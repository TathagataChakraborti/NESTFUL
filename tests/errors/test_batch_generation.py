from nestful.data_handlers import get_nestful_data
from nestful.errors import (
    batch_generate_error_steps,
    batch_generate_error_sequences,
)
from nestful.schemas.errors import ErrorType
from nestful import AtomicCall
from random import randint
from typing import List


class TestBatchGeneration:
    def setup_method(self) -> None:
        self.sequence_data, self.catalog = get_nestful_data(executable=True)

    def test_batch_gen_sample_test(self) -> None:
        previous_data: List[AtomicCall] = []

        for i in range(10):
            request_size = randint(1, i + 5)
            dataset = batch_generate_error_steps(
                dataset=self.sequence_data,
                catalog=self.catalog,
                num_samples=request_size,
                num_error_per_sample=1,
                random_seed=16,
            )

            assert len(dataset) <= request_size

            if previous_data:
                same_length = min(len(previous_data), len(dataset))
                assert (
                    previous_data is None
                    or previous_data[:same_length] == dataset[:same_length]
                )

            previous_data = dataset

    def test_batch_gen_step(self) -> None:
        dataset = batch_generate_error_steps(
            dataset=self.sequence_data,
            catalog=self.catalog,
            num_samples=100,
            error_type=ErrorType.MISSING_PARAMETER,
            num_error_per_sample=1,
        )

        assert len(dataset) <= 100

        for data in dataset:
            assert len(data.call.errors) == 1
            assert data.call.errors[0].error_type == ErrorType.MISSING_PARAMETER

    def test_batch_gen_sequence(self) -> None:
        dataset = batch_generate_error_sequences(
            dataset=self.sequence_data,
            catalog=self.catalog,
            num_samples=100,
            num_error_per_sample=2,
        )

        assert len(dataset) <= 100

        for data in dataset:
            assert data.sequence.num_errors >= 2
