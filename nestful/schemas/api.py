from __future__ import annotations
from nestful.schemas.openapi import Component
from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Dict, Optional, Union


class QueryParameter(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = False
    enum: List[str] = []
    # TODO: https://github.com/TathagataChakraborti/NESTFUL/issues/2
    allowed_values: Union[str, List[str]] = []
    possible_values: Union[str, List[str]] = []
    default_value: Optional[str] = None
    ################################################################


class MinifiedAPI(BaseModel):
    name: str
    inputs: List[str]
    outputs: List[str]


class API(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str
    # TODO: https://github.com/TathagataChakraborti/NESTFUL/issues/2
    parameters: Dict[str, QueryParameter] = dict()
    query_parameters: Dict[str, QueryParameter] = dict()
    path_parameters: Dict[str, QueryParameter] = dict()
    arguments: Dict[str, QueryParameter] = dict()
    ################################################################
    output_parameters: Dict[str, Component] = dict()

    @model_validator(mode="after")
    def temporary_field_jarl(self) -> API:
        if self.path_parameters:
            self.query_parameters = self.path_parameters

        if self.parameters:
            self.query_parameters = self.parameters

        if self.arguments:
            self.query_parameters = self.arguments

        return self

    def get_arguments(self, required: Optional[bool] = True) -> List[str]:
        if required is None:
            return list(self.query_parameters.keys())
        else:
            return [
                key
                for key in self.query_parameters.keys()
                if self.query_parameters[key].required is required
            ]

    def get_outputs(self) -> List[str]:
        outputs = []

        for item in self.output_parameters:
            outputs.append(item)

            if self.output_parameters[item].properties:
                for inner_item in self.output_parameters[item].properties:
                    outputs.append(f"{item}.{inner_item}")

        return outputs

    def minified(self, required: Optional[bool] = True) -> MinifiedAPI:
        return MinifiedAPI(
            name=self.name,
            inputs=self.get_arguments(required),
            outputs=self.get_outputs(),
        )


class Catalog(BaseModel):
    apis: List[API] = []

    def get_api(
        self,
        name: str,
        minified: bool = False,
        required: Optional[bool] = False,
    ) -> Union[API, MinifiedAPI, None]:
        api_object = next(filter(lambda x: x.name == name, self.apis), None)

        if api_object:
            return api_object if not minified else api_object.minified(required)

        return None
