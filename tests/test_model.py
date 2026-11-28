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
BUILD = ROOT / "scripts" / "build.py"

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


@pytest.fixture(scope="module")
def build_script():
    spec = importlib.util.spec_from_file_location("semantic_model_build", BUILD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("statuses", "opening"), [
    (["candidate", "candidate"], "Every name below is a candidate: none is accepted yet."),
    (["accepted", "candidate"], "A concept marked accepted carries the canonical name the author chose"),
    (["accepted", "accepted"], None),
])
def test_the_glossary_note_is_true_for_the_statuses_it_finds(build_script, statuses, opening) -> None:
    note = build_script.status_note([{"status": status} for status in statuses])
    if opening is None:
        assert note == []
    else:
        assert note[0].startswith(opening)
        assert note[-1] == ""


# The rungs of the literature ladder ---------------------------------------------------------

#: The rung cards in ladder order, as the author placed them on 2026-11-28, with each one's
#: display position and family (None: the reading of an arm registers no method of its own).
LADDER = (
    ("term_frequency", "0", "explainable-units"),
    ("own_annotations", "1", "explainable-units"),
    ("top_hit_identity", "2a", "explainable-units"),
    ("homology_vote", "2b", "explainable-units"),
    ("nearest_neighbour", "3", "embedding-reranker"),
    ("neighbourhood_vote", "4", "embedding-reranker"),
    ("reading_of_an_arm", "5", None),
    ("search_space_transform", "6", "embedding-reranker"),
    ("recipe_across_language_models", "6b", "embedding-reranker"),
    ("regime_calibration", "7", "embedding-reranker"),
    ("calibrated_maximum", "8", "embedding-reranker"),
    ("own_annotation_ranker", "9", "explainable-units"),
    ("supervised_head", "10", "embedding-reranker"),
    ("reranker_over_sources", "11a", "embedding-reranker"),
    ("count_map", "12a", "explainable-units"),
    ("segment_encoder", "12b", "world-model"),
)


def rungs(model: dict) -> list[dict]:
    """The rung cards, sorted by their ladder order."""
    return sorted((c for c in model["concepts"] if "ladder_order" in c), key=lambda c: c["ladder_order"])


def test_the_ladder_is_the_cards_with_an_order(model: dict) -> None:
    found = [(c["id"], c["ladder_position"], c.get("method_family")) for c in rungs(model)]
    assert found == list(LADDER)


def test_ladder_orders_are_unique_and_spaced_by_ten(model: dict) -> None:
    orders = [c["ladder_order"] for c in rungs(model)]
    assert len(orders) == len(set(orders))
    assert all(order % 10 == 0 for order in orders)


def test_a_display_position_comes_with_an_order(model: dict) -> None:
    for c in model["concepts"]:
        assert ("ladder_position" in c) == ("ladder_order" in c), c["id"]
        if "method_family" in c:
            assert "ladder_order" in c, c["id"]


def test_a_family_is_a_value_of_the_method_family_card(model: dict) -> None:
    families = next(c for c in model["concepts"] if c["id"] == "method_family")["values"]
    for c in rungs(model):
        if "method_family" in c:
            assert c["method_family"] in families, c["id"]


def test_every_rung_card_is_an_accepted_method(model: dict) -> None:
    for c in rungs(model):
        assert c["status"] == "accepted" and c["top_category"] == "method", c["id"]


def test_the_category_and_the_aspect_take_descriptive_values(model: dict) -> None:
    cards = {c["id"]: c for c in model["concepts"]}
    assert cards["knowledge_category"]["values"] == [
        "no_knowledge",
        "limited_knowledge",
        "partial_knowledge",
    ]
    assert cards["aspect"]["values"] == [
        "biological_process",
        "molecular_function",
        "cellular_component",
    ]


def test_schema_data_and_project_carry_one_version(model: dict) -> None:
    schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    project = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M)
    assert project is not None
    assert schema["version"] == model["version"] == project.group(1)
