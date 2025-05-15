from __future__ import annotations
from typing import List, Dict, Optional, Any, Union, Tuple, Set
from pydantic import BaseModel, ConfigDict, model_validator, computed_field
from nestful.utils import parse_parameters, extract_label, get_token
from nestful.schemas.api import Catalog, API, MinifiedAPI
from nestful.schemas.errors import ErrorType
from copy import deepcopy

DUMMY_VALUE = "INIT"


class Question(BaseModel):
    user_said: str
    argument: str
    assignment: str
    resolved: Any

    def __str__(self) -> str:
        return f"What value should be assigned to {self.argument}?"

    def __repr__(self) -> str:
        return f"What is the value of {self.assignment}?"


class AtomicSequence(BaseModel):
    sequence: SequencingData
    ground_truth: SequencingData


class AtomicCall(BaseModel):
    input: str = ""
    call: SequenceStep
    memory: Dict[str, Any]
    question: Optional[Question] = None
    backing_steps: List[SequenceStep] = []
    ground_truth: Optional[AtomicCall] = None

    @property
    def sequence_form(self) -> SequencingData:
        return SequencingData(input=self.input, output=[self.call])


class SequenceStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = ""
    arguments: Dict[str, Any] = dict()
    label: Optional[str] = None
    errors: List[ErrorTag] = []
    response: Optional[Any] = dict()

    def __str__(self) -> str:
        return str(self.model_dump(exclude={"errors", "response"}))

    def generate_dummy_output(
        self, catalog: Catalog, fill_in_memory: bool = True
    ) -> Dict[str, Any]:
        new_memory: Dict[str, Any] = dict()
        api_spec = next(
            filter(lambda api: api.name == self.name, catalog.apis), None
        )

        if api_spec is None or self.label is None:
            return new_memory

        else:
            if fill_in_memory:
                for k, item in api_spec.output_parameters.items():
                    new_memory[k] = (
                        {key: DUMMY_VALUE for key in item.properties}
                        if item.properties
                        else DUMMY_VALUE
                    )

                memory = {self.label: new_memory}
                return memory

            else:
                if self.response:
                    return {self.label: self.response}

                return new_memory

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
        ground_truth: SequenceStep,
        catalog: Catalog,
        required_schema_only: bool = False,
        check_values: bool = False,
    ) -> bool:
        gt_arguments = (
            ground_truth.get_required_args(catalog)
            if required_schema_only
            else set(ground_truth.arguments.keys())
        )

        self_arguments = (
            self.get_required_args(catalog)
            if required_schema_only
            else set(self.arguments.keys())
        )

        if check_values:
            tmp_1 = {
                k: v
                for k, v in ground_truth.arguments.items()
                if k in gt_arguments
            }
            tmp_2 = {
                k: v for k, v in self.arguments.items() if k in self_arguments
            }

            return self.name == ground_truth.name and tmp_1 == tmp_2

        else:
            return (
                self.name == ground_truth.name
                and gt_arguments == self_arguments
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

    def remove_reference(self, label: str) -> SequenceStep:
        new_step = deepcopy(self)
        new_step.arguments = dict()

        for arg, value in self.arguments.items():
            l, m = extract_label(str(value))

            if l == label:
                continue

            new_step.arguments[arg] = value

        return new_step


class SequencingData(BaseModel):
    input: str = ""
    output: List[SequenceStep] = []
    var_result: Dict[str, str] = {}
    errors: List[ErrorTag] = []

    @model_validator(mode="after")
    def remove_final_step(self) -> SequencingData:
        if self.output and self.output[-1].name == "var_result":
            self.var_result = self.output[-1].arguments
            self.output = self.output[:-1]

        return self

    @computed_field  # type: ignore
    @property
    def num_successful_calls(self) -> int:
        return len([step for step in self.output if step.response is not None])

    @property
    def num_errors(self) -> int:
        all_errors = self.errors

        for step in self.output:
            all_errors.extend(step.errors)

        return len(all_errors)

    def __str__(self) -> str:
        list_of_str = [str(item) for item in self.output]
        string_form = ",\n".join(list_of_str)
        return f"[\n{string_form}\n]"

    def generate_dummy_output(
        self,
        catalog: Catalog,
        index: Optional[int] = None,
        fill_in_memory: bool = True,
    ) -> Dict[str, Any]:
        assert index is None or index < len(self.output)
        index = len(self.output) if index is None else index

        memory: Dict[str, Any] = {}

        for i in range(index):
            step_memory = self.output[i].generate_dummy_output(
                catalog, fill_in_memory
            )
            memory = {**memory, **step_memory}

        return memory

    def get_tool_specs(self, catalog: Catalog) -> List[API]:
        list_of_apis: List[API] = []

        for step in self.output:
            tool_spec = step.get_tool_spec(catalog)

            if isinstance(tool_spec, API) and tool_spec not in list_of_apis:
                list_of_apis.append(tool_spec)

        return list_of_apis

    def contains(
        self,
        step: SequenceStep,
        catalog: Catalog,
        required_schema_only: bool = False,
        check_values: bool = False,
    ) -> bool:
        return any(
            [
                item.is_same_as(
                    step, catalog, required_schema_only, check_values
                )
                for item in self.output
            ]
        )

    def is_same_as(
        self,
        ground_truth: SequencingData,
        catalog: Catalog,
        required_schema_only: bool = False,
        check_values: bool = False,
    ) -> bool:
        return all(
            [
                ground_truth.contains(
                    step, catalog, required_schema_only, check_values
                )
                for step in self.output
            ]
        ) and all(
            [
                self.contains(step, catalog, required_schema_only, check_values)
                for step in ground_truth.output
            ]
        )

    def remove_reference(self, label: str) -> SequencingData:
        new_sequence = deepcopy(self)
        cached_index = 0

        for index, step in enumerate(new_sequence.output):
            new_sequence.output[index] = step.remove_reference(label)

            if step.label == label:
                cached_index = index

        new_sequence.output = (
            new_sequence.output[:cached_index]
            + new_sequence.output[cached_index + 1 :]
        )

        return new_sequence

    def who_used(self, label: str) -> List[int]:
        indices = []

        for index, step in enumerate(self.output):
            for arg, value in step.arguments.items():
                l, m = extract_label(str(value))

                if l == label:
                    indices.append(index)
                    break

        return indices

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

    def prepare_sequence(
        self,
        catalog: Catalog,
        index: int = 0,
        fill_in_memory: bool = True,
    ) -> Tuple[SequencingData, Dict[str, Any]]:
        memory = self.generate_dummy_output(catalog, index, fill_in_memory)
        sequence = SequencingData(output=[self.output[index]])

        return sequence, memory

    def goal_check(
        self,
        catalog: Catalog,
        ground_truth: SequencingData,
        memory: Optional[Dict[str, Any]] = None,
        fill_in_memory: bool = True,
    ) -> bool:
        if memory is None:
            memory = self.generate_dummy_output(
                catalog=catalog, fill_in_memory=fill_in_memory
            )

        else:
            assert (
                fill_in_memory is False
            ), "Cannot provide memory as well as fill it in!"

        vars_to_check = list(ground_truth.var_result.values())
        vars_to_check = (
            vars_to_check
            if vars_to_check
            else [f"${step.label}$" for step in ground_truth.output]
        )

        check_results: List[bool] = []

        for item in vars_to_check:
            gt_label, var_id = extract_label(item)

            if gt_label == get_token(index=0):
                gt_label = var_id or ""
                var_id = None

            name, index = ground_truth.who_produced(gt_label)
            target_label = "" if name is None else self.get_label(name, index)

            memory_item = memory.get(target_label or "", {})

            if memory_item:
                if var_id is None or not isinstance(memory_item, Dict):
                    check_results.append(memory_item != {})
                else:
                    check_results.append(
                        memory_item.get(var_id, None) is not None
                    )
            else:
                return False

        return all(check_results)

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


class ErrorTag(BaseModel):
    error_type: ErrorType = ErrorType.UNKNOWN
    info: str | Dict[str, Any] | None
