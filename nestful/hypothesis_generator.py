from nestful import Catalog, API
from nestful.schemas.openapi import Component
from typing import Dict, Any, Optional
from hypothesis_jsonschema import from_schema
from hypothesis.strategies import SearchStrategy
from hypothesis import given


def get_output_in_json_form(
    output_parameters: Dict[str, Component],
    min_string_length: int = 3,
    min_array_length: int = 3,
    pattern: str = "^[a-zA-Z0-9_.-]*$",
) -> Dict[str, Any]:
    json_form: Dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "required": list(output_parameters.keys()),
        "properties": dict(),
    }

    for item, value in output_parameters.items():
        if value.required:
            json_form["required"].append(item)

        json_form["properties"][item] = {"type": value.type}

        if value.type == "object":
            json_form["properties"][item]["additionalProperties"] = (
                value.properties != {}
            )
            json_form["properties"][item]["properties"] = dict()

            if value.properties:
                if not all(
                    [
                        isinstance(value, Component)
                        for value in value.properties.values()
                    ]
                ):
                    raise NotImplementedError()

                json_form["properties"][item]["properties"] = (
                    get_output_in_json_form(
                        value.properties,  # type: ignore
                        min_string_length,
                        min_array_length,
                        pattern,
                    )
                )

        elif value.type == "array":
            json_form["properties"][item]["minItems"] = min_array_length

        else:
            json_form["properties"][item] = {
                "type": (
                    "number"
                    if value.type in ["float", "double"]
                    else value.type
                )
            }

            if value.type == "string":
                json_form["properties"][item]["minLength"] = min_string_length
                json_form["properties"][item]["pattern"] = pattern

    return json_form


class Hypothesis:
    def __init__(self, name: str, catalog: Catalog) -> None:
        self.api = catalog.get_api(name)
        self.strategy: Optional[SearchStrategy] = None
        self.random_value: Dict[str, Any] = {}

    def generate_sample(
        self,
        min_string_length: int = 3,
        min_array_length: int = 10,
        pattern: str = "^[a-zA-Z0-9_.-]*$",
    ) -> None:
        assert isinstance(self.api, API)

        json_form = get_output_in_json_form(
            self.api.output_parameters,
            min_string_length,
            min_array_length,
            pattern,
        )
        self.strategy = from_schema(json_form)
        self.store_value()  # type: ignore

    @(
        lambda method: lambda self, *args, **kwargs: given(self.strategy)(
            method
        )(self, *args, **kwargs)
    )
    def store_value(self, value: Any) -> None:
        self.random_value = value
