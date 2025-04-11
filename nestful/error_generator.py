from nestful import SequenceStep, SequencingData, Catalog
from nestful.utils import extract_label
from nestful.schemas.errors import ErrorType
from random import sample, randint
from typing import Optional, Dict, Any, Tuple
from copy import deepcopy


def induce_error_in_step(
    step: SequenceStep,
    catalog: Catalog,
    memory: Dict[str, Any],
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_errors: int = 1,
) -> Tuple[Optional[SequenceStep], Dict[str, Any]]:
    if error_type == ErrorType.UNKNOWN:
        error_type = ErrorType.get_random_error()

    if error_type == ErrorType.MISSING_PARAMETER:
        error_step = remove_required_argument(step, catalog, num_errors)
        return error_step, memory
    elif error_type == ErrorType.MADE_UP_PARAMETER:
        error_step = rename_required_argument(step, catalog, num_errors)
        return error_step, memory
    elif error_type == ErrorType.MISSING_MEMORY:
        new_memory = remove_memory_item(step, memory, num_errors)
        return step if new_memory != memory else None, memory
    elif error_type == ErrorType.MADE_UP_ASSIGNMENT:
        error_step = rename_assignment(step, num_errors)
        return error_step, memory
    else:
        raise NotImplementedError(f"Error type {error_type} not supported yet.")


def induce_error_in_sequence(
    sequence: SequencingData,
    catalog: Catalog,
    memory: Dict[str, Any],
    error_type: ErrorType = ErrorType.UNKNOWN,
    num_errors: int = 1,
) -> SequencingData:
    error_count = 0

    while error_count < num_errors:
        index = randint(a=0, b=len(sequence.output) - 1)
        step = sequence.output[index]

        error_step, new_memory = induce_error_in_step(
            step, catalog, memory, error_type
        )

        if error_step is not None:
            sequence.output[index] = error_step
            memory = new_memory

            error_count += 1

    return sequence


def remove_required_argument(
    step: SequenceStep, catalog: Catalog, num: int = 1
) -> Optional[SequenceStep]:
    error_step = deepcopy(step)
    required_params = error_step.get_required_args(catalog)

    if num > len(required_params):
        return None

    else:
        params_to_remove = sample(list(required_params), num)

        for item in params_to_remove:
            del error_step.arguments[item]

        return error_step


def rename_required_argument(
    step: SequenceStep, catalog: Catalog, num: int = 1
) -> Optional[SequenceStep]:
    error_step = deepcopy(step)
    required_params = error_step.get_required_args(catalog)

    if num > len(required_params):
        return None

    else:
        params_to_rename = sample(list(required_params), num)

        for item in params_to_rename:
            new_argument = transform_variable(item)
            error_step.arguments[new_argument] = step.arguments[item]

            del error_step.arguments[item]

        return error_step


def remove_memory_item(
    step: SequenceStep, memory: Dict[str, Any], num: int = 1
) -> Dict[str, Any]:
    keys_of_interest = set()

    for arg, value in step.arguments.items():
        label, mapping = extract_label(str(value))

        if label.startswith("var"):
            keys_of_interest.add(label)

    if num > len(keys_of_interest):
        return memory

    else:
        key_to_remove = sample(list(keys_of_interest), num)

        for item in key_to_remove:
            memory[item] = {}

        return memory


def rename_assignment(
    step: SequenceStep, num: int = 1
) -> Optional[SequenceStep]:
    args_of_interest = set()
    error_step = deepcopy(step)

    for arg, value in step.arguments.items():
        label, mapping = extract_label(str(value))

        if label.startswith("var") and mapping is not None:
            args_of_interest.add(arg)

    if num > len(args_of_interest):
        return None

    else:
        assignments_to_reassign = sample(list(args_of_interest), num)

        for item in assignments_to_reassign:
            label, mapping = extract_label(str(step.arguments[item]))

            if mapping:
                mapping_components = mapping.split(".")
                mapping_components[-1] = transform_variable(
                    mapping_components[-1]
                )

                new_mapping = ".".join(mapping_components)
                error_step.arguments[item] = f"${label}.{new_mapping}$"

        return error_step


def transform_variable(name: str) -> str:
    # TODO: ISS24 Need to replace with better generator
    return name[::-1]
