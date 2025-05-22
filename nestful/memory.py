from typing import Dict, Any, List, Optional
from copy import deepcopy
from nestful.utils import extract_label, get_token


def resolve_in_memory(arguments: Dict[str, Any], memory: Dict[str, Any]) -> Any:
    return {k: resolve_item_in_memory(v, memory) for k, v in arguments.items()}


def resolve_item_in_memory(assignment: str, memory: Dict[str, Any]) -> Any:
    label, mapping = extract_label(assignment)

    if label == "" and mapping is None:
        return assignment

    if label == get_token(index=0) and mapping is not None:
        key_chain = mapping.split(".")
        memory_item = memory

        for key in key_chain:
            memory_item = memory_item.get(key, {})

        return memory_item
    else:
        memory_item = memory.get(label, None)

    if memory_item is None:
        return None

    else:
        if mapping is None:
            return memory_item
        else:
            key_chain = mapping.split(".")

            for key in key_chain:
                memory_item = memory_item.get(key, {})

            return memory_item


def extract_references_from_memory(
    args: Dict[str, Any], memory: Dict[str, Any], stringify: bool = False
) -> Dict[str, Any]:
    for k, v in args.items():
        new_value = extract_reference_from_memory(
            v, memory, stringify=stringify
        )

        if new_value is not None:
            args[k] = new_value

        elif isinstance(v, Dict):
            args[k] = extract_references_from_memory(
                v, memory, stringify=stringify
            )

    return args


def extract_reference_from_memory(
    value: Any,
    memory: Dict[str, Any],
    prefix: Optional[List[str]] = None,
    stringify: bool = False,
) -> Optional[str]:
    prefix = prefix or []
    value = str(value) if stringify else value

    for k, v in memory.items():
        v = str(v) if stringify is True and not isinstance(v, Dict) else v

        if v == value:
            prefix.append(k)
            return f"${'.'.join(prefix)}$"

        if isinstance(v, Dict):
            new_prefix = deepcopy(prefix)
            new_prefix.append(k)

            reference = extract_reference_from_memory(value, v, new_prefix)

            if reference is not None:
                return reference

    return None
