# Semantic model of protein function prediction

The single versioned description of the concepts of protein function prediction, of the
components that implement or document them, and of the relations between them.

It is named after the problem, not after a tool. PROTEA, the open science platform where the
work runs, is one of its components; so are the laboratory code, the evaluator and the
documentation. The glossary, the component map, the labels of user interfaces and the schemas
of data contracts are meant to be generated from it, so that one concept has one name
everywhere.

## Status

Version 0.2, under review.

- Version 0 imported the 35 concept candidates found while mapping the project for its closure
  (2026-11-20), as they were found and written in English. Their canonical names are not chosen
  yet: the author chooses them. A concept with several candidate names groups concepts that
  still have to be split.
- Version 0.1 adds the 34 concepts of the literature ladder, the protocol that reproduces the
  published ways of transferring GO terms inside PROTEA as ordered rungs. The author accepted
  their names on 2026-11-28, so each of these cards is accepted, with its one canonical name.
  The same acceptance amends three cards of version 0 (evidence channel, donor set, target
  population) and settles where a method that combines families belongs (method family).
- Version 0.2 places the rungs of the ladder. A rung is a concept card that carries a ladder
  order (an integer spaced by ten), a display position (such as 2b) and, when its writers
  register a method of their own, that method's family (the reading of an arm, rung 5,
  carries none); the ladder is the cards that carry an order, sorted by it. It adds the nine rung
  cards that had none (GO term frequency, own annotations, top-hit identity, homology vote,
  nearest neighbour, neighbourhood vote, recipe across language models, own-annotation ranker,
  segment encoder), accepts the count map's name, and gives the knowledge category and the
  aspect their descriptive values, the codes PROTEA uses today kept as current names. The
  author accepted these names and the families on 2026-11-28.
  The same evening he accepted in bulk the code names of the ladder's third implementation
  batch, recorded as current names on the cards they belong to: `search_space` (search-space
  transform), `delivered_reading` (coverage guarantee), `homology_self_scores` with its columns
  `scores_uri`, `scores_sha256` and `queries_without_self_score` (homology vote), `channel_mask`
  (evidence channel), and the count map's method code suffixes `-accession` and `-grid`.
- Components and relations are defined in the schema and not filled yet.

## What is here

| Path | What it is |
|---|---|
| `schema/protein_function_prediction_semantic_model.yaml` | The LinkML schema, the only source of the structure. |
| `data/concepts.yaml` | The concepts, the only source of the content. |
| `generated/` | JSON Schema, OWL in Turtle, Pydantic classes and the SKOS concept scheme, built from the two sources. |
| `docs/glossary.md` | The glossary, built from the concepts. |
| `scripts/build.py` | Builds everything under `generated/` and the glossary. |
| `tests/` | The checks run locally and in CI. |

Nothing under `generated/` or `docs/glossary.md` is edited by hand: change the schema or the
concepts and rebuild.

## The model in brief

- **First ring.** Concept (`skos:Concept`), component and relation. The model itself is a
  `skos:ConceptScheme`.
- **Reserved words.** *Ontology* names only the Gene Ontology and *term* names only a GO term.
  A test refuses any other use in labels, names and definitions.
- **One card per concept.** Identifier, status, English label, candidate names and, once
  accepted, the canonical name; top category; definition; values and examples when it has
  them; the names it has today and where; its equivalent outside the project; and the names
  it retires.
- **English only.** Everything is in English except one field, the Spanish label, kept for the
  Spanish user interface. The names a concept has today are quoted verbatim, whatever their
  language, because they are the record of what has to be renamed.

## Build and check

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync --frozen                  # the pinned tools: LinkML 1.12.1 and pytest
uv run python scripts/build.py    # rebuild generated/ and docs/glossary.md
uv run pytest                     # lint, validation, reserved words, generated files up to date
```

CI runs the same checks on every pull request and on `main`, and refuses commit messages or
pull request bodies that carry AI attribution lines.

## Identifiers

Concept URIs live under `https://w3id.org/protein-function-prediction-semantic-model/`. The
redirect is not registered yet, so they identify concepts but do not resolve.

## License

Released into the public domain under the [Unlicense](LICENSE), like the rest of the stack.
