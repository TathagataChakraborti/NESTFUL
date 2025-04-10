from __future__ import annotations
from typing import List, Dict, Optional, Any, Union, Tuple, Set
from pydantic import BaseModel, ConfigDict, model_validator
from nestful.utils import parse_parameters
from nestful.schemas.api import Catalog, API, MinifiedAPI


class SequenceStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = ""
    arguments: Dict[str, Any] = dict()
    label: Optional[str] = None

    def __str__(self) -> str:
        return str(self.dict())

    def get_tool_spec(self, catalog: Catalog) -> Optional[API]:
        tool_spec = catalog.get_api(name=self.name or "")

        assert not isinstance(tool_spec, MinifiedAPI)
        return tool_spec

    def get_required_args(self, catalog: Catalog) -> Set[str]:
        api_spec = (
            catalog.get_api(name=self.name, required=True)
            if self.name
            else None
        )

        required_arguments = set()

        if isinstance(api_spec, API):
            for item in self.arguments:
                if item in api_spec.get_arguments(required=True):
                    required_arguments.add(item)

        return required_arguments

    def is_same_as(
        self,
        ground_truth: SequenceStep | SequencingData,
        catalog: Catalog,
        required_schema_only: bool = False,
    ) -> bool:
        if required_schema_only:
            if isinstance(ground_truth, SequenceStep):
                gt_arguments = ground_truth.get_required_args(catalog)
                self_arguments = self.get_required_args(catalog)

                return (
                    self.name == ground_truth.name
                    and gt_arguments == self_arguments
                )

            else:
                return any(
                    [
                        self.is_same_as(
                            ground_truth_step, catalog, required_schema_only
                        )
                        for ground_truth_step in ground_truth.output
                    ]
                )
        else:
            return (
                self == ground_truth
                if isinstance(ground_truth, SequenceStep)
                else self in ground_truth.output
            )

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
    var_result: Dict[str, str] = {}

    @model_validator(mode="after")
    def remove_final_step(self) -> SequencingData:
        if self.output and self.output[-1].name == "var_result":
            self.var_result = self.output[-1].arguments
            self.output = self.output[:-1]

        return self

    def __str__(self) -> str:
        list_of_str = [str(item) for item in self.output]
        string_form = ",\n".join(list_of_str)
        return f"[\n{string_form}\n]"

    def get_tool_specs(self, catalog: Catalog) -> List[API]:
        list_of_apis: List[API] = []

        for step in self.output:
            tool_spec = step.get_tool_spec(catalog)

            if isinstance(tool_spec, API) and tool_spec not in list_of_apis:
                list_of_apis.append(tool_spec)

        return list_of_apis

    def is_same_as(
        self,
        ground_truth: SequencingData,
        catalog: Catalog,
        required_schema_only: bool = False,
    ) -> bool:
        return all(
            [
                step.is_same_as(ground_truth, catalog, required_schema_only)
                for step in self.output
            ]
        ) and len(self.output) == len(ground_truth.output)

    def who_produced(self, var: str) -> Tuple[Optional[str], int]:
        index_map: Dict[str, int] = {}

        for step in self.output:
            if step.name is not None:
                current_index = index_map.get(step.name, 0)
                index_map[step.name] = current_index + 1

                if step.label == var:
                    return step.name, index_map[step.name]

        return None, 0

    def get_label(self, name: str, index: int = 1) -> Optional[str]:
        index_map: Dict[str, int] = {}

        for step in self.output:
            if step.name is not None:
                current_index = index_map.get(step.name, 0)
                index_map[step.name] = current_index + 1

                if step.name == name and index_map[step.name] == index:
                    return step.label

        return None

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
