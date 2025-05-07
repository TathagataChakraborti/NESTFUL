from typing import Dict, Any
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
