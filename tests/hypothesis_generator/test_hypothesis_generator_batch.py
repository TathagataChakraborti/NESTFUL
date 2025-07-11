from nestful.data_handlers import get_nestful_data
from nestful.hypothesis_generator import generate_atomic_calls


class TestHypothesisGeneratorBatch:
    def setup_method(self) -> None:
        self.sequence_data, self.catalog = get_nestful_data(executable=True)

    def test_basic(self) -> None:
        dataset = generate_atomic_calls(
            dataset=self.sequence_data,
            catalog=self.catalog,
            num_samples=2,
        )

        assert len(dataset) == 2

    def test_extended_backing_step(self) -> None:
        dataset = generate_atomic_calls(
            dataset=self.sequence_data,
            catalog=self.catalog,
            num_samples=1,
            min_backing_steps=10,
            split_merge=True,
        )

        assert len(dataset[0].backing_steps) >= 10

    def test_complexfuncbench(self) -> None:
        sequence_data, catalog = get_nestful_data(name="complexfuncbench")

        dataset = generate_atomic_calls(
            dataset=sequence_data,
            catalog=catalog,
            num_samples=1,
        )

        for sample in dataset:
            assert sample.question and sample.question.resolved

        assert len(dataset) == 1

    def test_complexfuncbench_from_memory(self) -> None:
        sequence_data, catalog = get_nestful_data(name="complexfuncbench")

        dataset = generate_atomic_calls(
            dataset=sequence_data,
            catalog=catalog,
            num_samples=5,
            use_memory=True,
        )

        for sample in dataset:
            assert sample.question and sample.question.resolved

        assert len(dataset) == 5
