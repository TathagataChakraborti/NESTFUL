from typing import List, Dict, Union, Any, Tuple
from enum import StrEnum, auto
from pydantic import BaseModel
from genson import SchemaBuilder
from nestful.schemas.openapi import Component
from nestful.schemas.api import API, Catalog, QueryParameter
from nestful.schemas.sequences import (
    SequenceStep,
    SequencingData,
    SequencingDataset,
)


class Role(StrEnum):
    USER = auto()
    ASSISTANT = auto()
    OBSERVATION = auto()


class FunctionCall(BaseModel):
    role: Role = Role.ASSISTANT
    function_call: List[SequenceStep]


class Content(BaseModel):
    role: Role
    content: str = ""


class Data(BaseModel):
    status: bool
    message: str
    data: Dict[str, Any] | List[Dict[str, Any]] | Any


class Observation(BaseModel):
    role: Role = Role.OBSERVATION
    content: List[Data | Dict[str, Any]]


class Function(BaseModel):
    name: str
    description: str
    parameters: Component

    def convert_to_nestful_api(
        self, cached_responses: List[Dict[str, Any] | List[Dict[str, Any]]]
    ) -> API:
        parameters: Dict[str, QueryParameter] = {}

        for item, value in self.parameters.properties.items():
            if isinstance(value, Component):
                parameters[item] = QueryParameter(
                    description=value.description,
                    allowed_values=value.enum,
                    required=item in self.parameters.required,
                )

            else:
                raise NotImplementedError(
                    "Complex schema nesting not identified in data."
                )

        schema_builder = SchemaBuilder()

        for response in cached_responses:
            schema_builder.add_object(response)

        schema = schema_builder.to_schema()

        if "type" in schema:
            if schema["type"] == "object":
                output_schema = schema.get("properties", {})
            elif schema["type"] == "array":
                output_schema = schema.get("items", {}).get("properties", {})
            else:
                raise NotImplementedError("ISS3/ISS4")

        else:
            output_schema = {}

        output_parameters = {
            k: Component.model_validate(v) for k, v in output_schema.items()
        }

        return API(
            name=self.name,
            description=self.description,
            parameters=parameters,
            output_parameters=output_parameters,
            sample_responses=cached_responses,
        )


class Conversation(BaseModel):
    id: str
    conversations: List[Union[FunctionCall, Content, Observation]]
    functions: List[Function]


class ComplexFuncBench(BaseModel):
    data: List[Conversation]

    def convert_to_nestful(self) -> Tuple[SequencingDataset, Catalog]:
        new_catalog = Catalog()
        sequences: List[SequencingData] = []
        response_map: Dict[str, List[Dict[str, Any] | List[Dict[str, Any]]]] = (
            dict()
        )

        for sample in self.data:
            for index, step in enumerate(sample.conversations):
                if isinstance(step, FunctionCall):
                    for pos, func_call in enumerate(step.function_call):
                        if func_call.name:
                            current_cache = response_map.get(func_call.name, [])

                            for lookahead_step in sample.conversations[
                                index + 1 :
                            ]:
                                if isinstance(lookahead_step, Observation):
                                    new_response = lookahead_step.content[pos]

                                    if isinstance(new_response, Data):
                                        current_cache.append(new_response.data)
                                    else:
                                        current_cache.append(new_response)

                                    break

                            response_map[func_call.name] = current_cache

        for sample in self.data:
            for func in sample.functions:
                existing_api = new_catalog.get_api(name=func.name or "")

                if existing_api is None:
                    cached_responses = response_map.get(func.name, [])

                    api = func.convert_to_nestful_api(
                        cached_responses=cached_responses
                    )

                    new_catalog.apis.append(api)

        return SequencingDataset(data=sequences), new_catalog
