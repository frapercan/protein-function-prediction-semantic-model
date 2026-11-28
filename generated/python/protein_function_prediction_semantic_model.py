from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.12.0"
version = "0.2.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'protein_function_prediction',
     'default_range': 'string',
     'description': 'The single versioned description of the concepts of protein '
                    'function prediction, of the components that implement or '
                    'document them, and of the relations between them. It is named '
                    'after the problem, not after any tool: PROTEA, the open '
                    'science platform, is one of its components. Its first ring is '
                    'concept, component and relation; the model itself is a SKOS '
                    'concept scheme. Two words are reserved: ontology names only '
                    'the Gene Ontology, and term names only a GO term.',
     'id': 'https://w3id.org/protein-function-prediction-semantic-model',
     'imports': ['linkml:types'],
     'name': 'protein_function_prediction_semantic_model',
     'prefixes': {'dcterms': {'prefix_prefix': 'dcterms',
                              'prefix_reference': 'http://purl.org/dc/terms/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'protein_function_prediction': {'prefix_prefix': 'protein_function_prediction',
                                                  'prefix_reference': 'https://w3id.org/protein-function-prediction-semantic-model/'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'}},
     'source_file': 'schema/protein_function_prediction_semantic_model.yaml',
     'title': 'Semantic model of protein function prediction'} )

class NameStatus(str, Enum):
    """
    Where a concept stands in the choice of its canonical name.
    """
    candidate = "candidate"
    """
    Imported or proposed; the canonical name is not chosen yet.
    """
    accepted = "accepted"
    """
    The author chose the canonical name.
    """


class TopCategory(str, Enum):
    """
    The top categories of version 0, as the closure map gave them.
    """
    data = "data"
    component = "component"
    method = "method"
    method_family = "method_family"
    activity = "activity"
    document = "document"


class RelationKind(str, Enum):
    """
    The relation kinds of the closure map.
    """
    produces_data_for = "produces_data_for"
    evaluates = "evaluates"
    explains = "explains"
    imports = "imports"
    calls = "calls"
    launches = "launches"
    configures = "configures"
    deploys = "deploys"
    documents = "documents"
    duplicates = "duplicates"
    replaces = "replaces"



class SemanticModel(ConfiguredBaseModel):
    """
    The model itself: one versioned description from which the glossary, the component map, interface texts and contract schemas are generated.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'skos:ConceptScheme',
         'from_schema': 'https://w3id.org/protein-function-prediction-semantic-model',
         'tree_root': True})

    id: str = Field(default=..., description="""Stable identifier in snake_case English. In version 0 it is provisional and follows the first candidate name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel', 'Concept', 'Component']} })
    title: Optional[str] = Field(default=None, description="""The title of the model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel'], 'slot_uri': 'dcterms:title'} })
    version: Optional[str] = Field(default=None, description="""The semantic version of the model; 0.x while names are candidates.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel'], 'slot_uri': 'dcterms:hasVersion'} })
    description: Optional[str] = Field(default=None, description="""What the element is, in English prose.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel', 'Component'], 'slot_uri': 'dcterms:description'} })
    concepts: Optional[list[Concept]] = Field(default=None, description="""The concepts of the model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel'], 'slot_uri': 'skos:hasTopConcept'} })
    components: Optional[list[Component]] = Field(default=None, description="""The components of the project that implement or document concepts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel']} })
    relations: Optional[list[Relation]] = Field(default=None, description="""The named, directed links between components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('version')
    def pattern_version(cls, v):
        pattern=re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid version format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid version format: {v}"
            raise ValueError(err_msg)
        return v


class Concept(ConfiguredBaseModel):
    """
    A unit of meaning of protein function prediction. Every concept carries the same card: canonical name, English label and definition, a Spanish label for the Spanish user interface, its top category, the names it has today and where, and its external equivalent.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'skos:Concept',
         'from_schema': 'https://w3id.org/protein-function-prediction-semantic-model',
         'rules': [{'description': 'An accepted concept has its one canonical name.',
                    'postconditions': {'slot_conditions': {'canonical_name': {'name': 'canonical_name',
                                                                              'required': True}}},
                    'preconditions': {'slot_conditions': {'status': {'equals_string': 'accepted',
                                                                     'name': 'status'}}}}]})

    id: str = Field(default=..., description="""Stable identifier in snake_case English. In version 0 it is provisional and follows the first candidate name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel', 'Concept', 'Component']} })
    status: NameStatus = Field(default=..., description="""Whether the canonical name of the concept is chosen.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    label_en: str = Field(default=..., description="""Label in English.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept', 'Component'], 'exact_mappings': ['skos:prefLabel']} })
    label_es: str = Field(default=..., description="""Label in Spanish, for the Spanish user interface; the only field of a concept that is not in English.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept', 'Component'], 'exact_mappings': ['skos:prefLabel']} })
    candidate_names: list[str] = Field(default=..., description="""The English names proposed for the concept. More than one means the row of the closure map groups several concepts that still have to be split.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    canonical_name: Optional[str] = Field(default=None, description="""The one name chosen by the author. Required once the concept is accepted.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    top_category: TopCategory = Field(default=..., description="""The broadest kind the concept belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    definition_en: str = Field(default=..., description="""Definition in English.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'exact_mappings': ['skos:definition']} })
    values: Optional[list[str]] = Field(default=None, description="""The closed set of values the concept takes, when it has one.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    examples: Optional[list[str]] = Field(default=None, description="""Instances that show the concept, verbatim.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'slot_uri': 'skos:example'} })
    external_match: Optional[str] = Field(default=None, description="""The equivalent outside the project (a standard, a vocabulary or a paper), as text.""", json_schema_extra = { "linkml_meta": {'close_mappings': ['skos:closeMatch'], 'domain_of': ['Concept']} })
    current_names: Optional[list[NameUse]] = Field(default=None, description="""The names the concept has today, place by place.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    deprecated_names: Optional[list[str]] = Field(default=None, description="""Names retired once the canonical name is accepted; a check refuses them.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'exact_mappings': ['skos:hiddenLabel']} })
    naming_conflict: Optional[str] = Field(default=None, description="""Why the current names conflict, as the closure map found it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'slot_uri': 'skos:editorialNote'} })
    review_note: Optional[str] = Field(default=None, description="""A fact found after the import that the review has to settle.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'slot_uri': 'skos:editorialNote'} })
    ladder_order: Optional[int] = Field(default=None, description="""Where a rung of the literature ladder sits in it: an integer, spaced by ten so that a later rung is inserted without renumbering the others. Only a rung card carries it, and the ladder is the cards that do, sorted by it.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    ladder_position: Optional[str] = Field(default=None, description="""The label a rung is shown with in the ladder, such as 2b; carried only with a ladder order.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })
    method_family: Optional[str] = Field(default=None, description="""The family of a rung's method, one of the values of the method family concept. The family is part of a method's identity, so a rung whose writers register no method of their own (the reading of an arm) carries none.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('ladder_position')
    def pattern_ladder_position(cls, v):
        pattern=re.compile(r"^[0-9]+[a-z]?$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid ladder_position format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid ladder_position format: {v}"
            raise ValueError(err_msg)
        return v


class NameUse(ConfiguredBaseModel):
    """
    The names one place of the project gives to a concept today.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/protein-function-prediction-semantic-model'})

    where: str = Field(default=..., description="""The place, such as the ORM, the user interface, the panel or the laboratory code.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NameUse']} })
    names: list[str] = Field(default=..., description="""The names used there, verbatim.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NameUse']} })


class Component(ConfiguredBaseModel):
    """
    A piece of the project (code, data store, document, panel) that implements or documents concepts. Not filled in version 0.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'prov:Entity',
         'from_schema': 'https://w3id.org/protein-function-prediction-semantic-model'})

    id: str = Field(default=..., description="""Stable identifier in snake_case English. In version 0 it is provisional and follows the first candidate name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel', 'Concept', 'Component']} })
    label_en: str = Field(default=..., description="""Label in English.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept', 'Component'], 'exact_mappings': ['skos:prefLabel']} })
    label_es: str = Field(default=..., description="""Label in Spanish, for the Spanish user interface; the only field of a concept that is not in English.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept', 'Component'], 'exact_mappings': ['skos:prefLabel']} })
    description: Optional[str] = Field(default=None, description="""What the element is, in English prose.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SemanticModel', 'Component'], 'slot_uri': 'dcterms:description'} })
    paths: Optional[list[str]] = Field(default=None, description="""Where the component lives, as repository paths.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Component']} })
    implements: Optional[list[str]] = Field(default=None, description="""The concepts the component implements.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Component']} })
    documents_concepts: Optional[list[str]] = Field(default=None, description="""The concepts the component documents.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Component']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class Relation(ConfiguredBaseModel):
    """
    A named, directed link from one component to another. Not filled in version 0.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/protein-function-prediction-semantic-model'})

    subject: str = Field(default=..., description="""The component the relation starts from.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })
    predicate: RelationKind = Field(default=..., description="""The kind of the relation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })
    object: str = Field(default=..., description="""The component the relation points to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
SemanticModel.model_rebuild()
Concept.model_rebuild()
NameUse.model_rebuild()
Component.model_rebuild()
Relation.model_rebuild()
