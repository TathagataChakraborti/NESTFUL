from nestful.data_handlers import get_nestful_data
from nestful.hypothesis_generator import generate_atomic_calls


class TestHypothesisGeneratorBatch:
    def setup_method(self) -> None:
        self.sequence_data, self.catalog = get_nestful_data(executable=True)

    def test_basic(self) -> None:
        dataset = generate_atomic_calls(
            dataset=self.sequence_data,
            catalog=self.catalog,
            num_samples=3,
        )

        assert len(dataset) <= 3
