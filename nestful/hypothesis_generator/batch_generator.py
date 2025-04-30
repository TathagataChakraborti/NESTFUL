from random import randint, choice
from typing import Optional, List
from nestful.schemas.sequences import AtomicCall, Question
from nestful.errors.error_generator import get_args_with_labeled_assignments
from nestful.hypothesis_generator.random_hypothesis import (
    generate_dummy_output_sequence,
)
from nestful import SequencingDataset, Catalog

MAX_COLLISIONS = 100


def generate_atomic_calls(
    dataset: SequencingDataset,
    catalog: Catalog,
    num_samples: int,
    min_string_length: int = 3,
    min_array_length: int = 3,
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

            indices_of_interest: List[int] = []

            for index, step in enumerate(random_sequence.output):
                args_of_interest = get_args_with_labeled_assignments(
                    step.arguments
                )

                if args_of_interest:
                    indices_of_interest.append(index)

            random_index = choice(indices_of_interest)
            step = random_sequence.output[random_index]

            args_of_interest = get_args_with_labeled_assignments(step.arguments)
            arg_of_interest = choice(list(args_of_interest))

            memory = generate_dummy_output_sequence(
                random_sequence,
                catalog,
                index=random_index,
                min_string_length=min_string_length,
                min_array_length=min_array_length,
            )

            call_str = step.pretty_print(collapse_maps=True)
            new_hash = hash(f"{call_str} + {arg_of_interest}")

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
                            argument=arg_of_interest,
                            assignment=step.arguments[arg_of_interest],
                        ),
                        backing_steps=random_sequence.output[:random_index],
                    )
                )

                break

            if num_collisions == max_collisions:
                total_collisions += 1

                if total_collisions == max_collisions:
                    return current_samples

    return current_samples
