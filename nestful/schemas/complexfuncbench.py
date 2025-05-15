from typing import List, Dict, Union, Any, Tuple
from enum import StrEnum, auto
from pydantic import BaseModel
from nestful.schemas.openapi import Component
from nestful.schemas.api import API, Catalog
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

    def convert_to_nestful_api(self) -> API:
        raise NotImplementedError()


class Conversation(BaseModel):
    id: str
    conversations: List[Union[FunctionCall, Content, Observation]]
    functions: List[Function]


class ComplexFuncBench(BaseModel):
    data: List[Conversation]

    def convert_to_nestful(self) -> Tuple[SequencingDataset, Catalog]:
        new_catalog = Catalog()
        sequences: List[SequencingData] = []

        for sample in self.data:
            new_catalog = Catalog(
                apis=[
                    func.convert_to_nestful_api() for func in sample.functions
                ]
            )

        return SequencingDataset(data=sequences), new_catalog
