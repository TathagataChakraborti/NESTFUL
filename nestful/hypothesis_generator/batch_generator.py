from random import randint
from typing import Optional, List
from nestful.schemas.sequences import AtomicCall, Question
from nestful import SequencingDataset, Catalog

MAX_COLLISIONS = 100


def generate_atomic_calls(
    dataset: SequencingDataset,
    catalog: Catalog,
    num_samples: int,
    min_string_length: int = 3,
    min_array_length: int = 10,
    min_backing_length: Optional[int] = 1,
    forbidden_indices: Optional[List[int]] = None,
    max_collisions: int = MAX_COLLISIONS,
) -> List[AtomicCall]:
    current_samples: List[AtomicCall] = []
    stored_hashes = set()
    total_collisions = 0

    new_dataset = SequencingDataset(data=[])

    if forbidden_indices:
        for index, data in enumerate(dataset.data):
            if index not in forbidden_indices:
                new_dataset.data.append(data)
    else:
        new_dataset.data = dataset.data

    while len(current_samples) < num_samples:
        num_collisions = 0

        while num_collisions < max_collisions:
            random_index = randint(a=0, b=len(new_dataset.data) - 1)
            random_sequence = new_dataset.data[random_index]

            random_index = randint(a=1, b=len(random_sequence.output) - 1)
            step = random_sequence.output[random_index]

            # add to backing length
            # add to backing length

            memory, backing_steps = random_sequence.generate_dummy_output(
                catalog, index=random_index
            )

            call_str = step.pretty_print(collapse_maps=True)
            new_hash = hash(call_str)

            if new_hash in stored_hashes:
                num_collisions += 1
            else:
                stored_hashes.add(new_hash)

                current_samples.append(
                    AtomicCall(
                        call=step,
                        memory=memory,
                        question=Question(
                            user_said=random_sequence.input,
                            argument=,
                            assignment=,
                            resolved=,
                        )
                    )
                )

                break

            if num_collisions == max_collisions:
                total_collisions += 1

                if total_collisions == max_collisions:
                    return current_samples

    return current_samples
