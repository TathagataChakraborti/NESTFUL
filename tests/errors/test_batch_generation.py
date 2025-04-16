from nestful.data_handlers import get_nestful_data
from nestful.errors import batch_generate_error_steps
from nestful.schemas.errors import ErrorType


class TestBatchGeneration:
    def setup_method(self) -> None:
        self.sequence_data, self.catalog = get_nestful_data(executable=True)

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
