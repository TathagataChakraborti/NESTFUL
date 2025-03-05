from __future__ import annotations
from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Dict, Optional, Any, Union
from nestful.utils import parse_parameters


class SequenceStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = ""
    arguments: Dict[str, Any] = dict()
    label: Optional[str] = None

    @model_validator(mode="after")
    def non_string_assignments(self) -> SequenceStep:
        self.arguments = {
            key: str(item) for key, item in self.arguments.items()
        }
        return self

    @staticmethod
    def parse_pretty_print(pretty_print: str) -> SequenceStep:
        split = pretty_print.split(" = ")

        label = split[0] if " = " in pretty_print else ""
        signature = split[0] if len(split) == 1 else split[1]

        action_name, parameters = parse_parameters(signature)

        arguments = {}
        for item in parameters:
            item_split = item.split("=")
            arguments[item_split[0]] = item_split[1].replace('"', "")

        return SequenceStep(name=action_name, arguments=arguments, label=label)

    def pretty_print(
        self,
        mapper_tag: Optional[str] = None,
        collapse_maps: bool = True,
    ) -> str:
        label = f"{self.label} = " if self.label else ""

        required_arguments = list(self.arguments.keys())
        pretty_strings = []

        if collapse_maps:
            required_arguments = [
                f'{item}="{self.arguments.get(item)}"'
                for item in required_arguments
            ]
        else:
            assert (
                mapper_tag
            ), "You must provide a mapper tag if you are not collapsing maps."

            for item in required_arguments:
                value = self.arguments.get(item)

                if item != value:
                    mapping_string = f'{mapper_tag}("{value}", {item})'
                    pretty_strings.append(mapping_string)

        action_string = f"{label}{self.name}({', '.join(required_arguments)})"
        pretty_strings.append(action_string)

        return "\n".join(pretty_strings)


class SequencingData(BaseModel):
    input: str = ""
    output: List[SequenceStep] = []

    @model_validator(mode="after")
    def remove_final_step(self) -> SequencingData:
        if self.output[-1].name == "var_result":
            self.output = self.output[:-1]

        return self

    @staticmethod
    def parse_pretty_print(
        pretty_print: Union[str, List[str]]
    ) -> SequencingData:
        if isinstance(pretty_print, str):
            pretty_print = pretty_print.split("\n")

        return SequencingData(
            input="",
            output=[SequenceStep.parse_pretty_print(p) for p in pretty_print],
        )

    def pretty_print(
        self,
        mapper_tag: Optional[str] = None,
        collapse_maps: bool = True,
    ) -> str:
        tokens = [
            op.pretty_print(mapper_tag, collapse_maps) for op in self.output
        ]
        return "\n".join(tokens)


class SequencingDataset(BaseModel):
    data: List[SequencingData]
