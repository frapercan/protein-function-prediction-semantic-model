"""Checks of the semantic model: schema, concepts, reserved words and generated files."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "protein_function_prediction_semantic_model.yaml"
CONCEPTS = ROOT / "data" / "concepts.yaml"
PYDANTIC = ROOT / "generated" / "python" / "protein_function_prediction_semantic_model.py"

# Fields that define a concept; the names it has today and the notes about them are left out,
# because they quote the words as they are used now.
DEFINING_FIELDS = ("label_en", "label_es", "definition_en", "candidate_names", "canonical_name")

# Reserved words: "term" names only a GO term and "ontology" only the Gene Ontology, also in
# the Spanish label.
RESERVED = (
    (re.compile(r"\bterms?\b", re.IGNORECASE), re.compile(r"\bGO terms?\b")),
    (re.compile(r"\btérminos?\b", re.IGNORECASE), re.compile(r"\btérminos? GO\b", re.IGNORECASE)),
    (re.compile(r"\bontology\b", re.IGNORECASE),
     re.compile(r"\b(Gene Ontology|ontology snapshot|pivot ontology)\b", re.IGNORECASE)),
    (re.compile(r"\bontología\b", re.IGNORECASE),
     re.compile(r"\b(Gene Ontology|instantánea de ontología|ontología pivote)\b", re.IGNORECASE)),
)
# The concept that defines the word itself.
RESERVED_OWNER = "go_term"


@pytest.fixture(scope="module")
def model() -> dict:
    return yaml.safe_load(CONCEPTS.read_text(encoding="utf-8"))


def run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=ROOT)


def test_schema_lints_without_findings() -> None:
    done = run("linkml-lint", str(SCHEMA))
    assert done.returncode == 0, done.stdout + done.stderr


def test_concepts_validate_against_the_schema() -> None:
    done = run("linkml-validate", "-s", str(SCHEMA), "-C", "SemanticModel", str(CONCEPTS))
    assert done.returncode == 0, done.stdout + done.stderr


def test_generated_python_classes_load_the_concepts(model: dict) -> None:
    spec = importlib.util.spec_from_file_location("protein_function_prediction_semantic_model", PYDANTIC)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    loaded = module.SemanticModel(**model)
    assert len(loaded.concepts) == len(model["concepts"])


def test_identifiers_and_labels_are_unique(model: dict) -> None:
    concepts = model["concepts"]
    for field in ("id", "label_en", "label_es"):
        values = [c[field] for c in concepts]
        assert len(values) == len(set(values)), f"repeated {field}"


def test_an_accepted_concept_has_one_canonical_name(model: dict) -> None:
    for c in model["concepts"]:
        if c["status"] == "accepted":
            assert c.get("canonical_name"), c["id"]
            assert c["canonical_name"] in c["candidate_names"], c["id"]


def test_no_name_is_canonical_in_one_concept_and_deprecated_in_another(model: dict) -> None:
    canonical = {c["canonical_name"]: c["id"] for c in model["concepts"] if c.get("canonical_name")}
    for c in model["concepts"]:
        for name in c.get("deprecated_names", []):
            assert name not in canonical, f"{name!r} is deprecated in {c['id']} and canonical in {canonical[name]}"


def reserved_word_misuses(concepts: list[dict]) -> list[str]:
    """Every defining field that uses a reserved word in another sense."""
    misuses = []
    for c in concepts:
        if c["id"] == RESERVED_OWNER:
            continue
        for field in DEFINING_FIELDS:
            values = c.get(field) or []
            for text in [values] if isinstance(values, str) else values:
                for word, allowed in RESERVED:
                    if word.search(allowed.sub("", text)):
                        misuses.append(f"{c['id']}.{field}: {text}")
    return misuses


def test_reserved_words_keep_their_one_meaning(model: dict) -> None:
    misuses = reserved_word_misuses(model["concepts"])
    assert not misuses, "\n".join(misuses)


@pytest.mark.parametrize("text", [
    "A term of the panel.",
    "Un término del panel.",
    "The ontology of the laboratory.",
    "La ontología del laboratorio.",
])
def test_the_reserved_word_check_catches_another_sense(text: str) -> None:
    concept = {"id": "example", "definition_en": text}
    assert reserved_word_misuses([concept])


@pytest.mark.parametrize("text", [
    "The GO terms gained from t0 to t1.",
    "Los términos GO ganados.",
    "The pivot ontology of a window.",
    "Una instantánea de ontología.",
])
def test_the_reserved_word_check_lets_the_one_meaning_pass(text: str) -> None:
    concept = {"id": "example", "definition_en": text}
    assert not reserved_word_misuses([concept])


def test_generated_files_match_their_sources() -> None:
    done = run(sys.executable, "scripts/build.py", "--check")
    assert done.returncode == 0, done.stdout + done.stderr
