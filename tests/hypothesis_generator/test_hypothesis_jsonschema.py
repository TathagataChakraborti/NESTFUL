from nestful.data_handlers import get_nestful_catalog
from nestful.hypothesis_generator import Hypothesis
from nestful import API


class TestHypothesisJSONSchema:
    def setup_method(self) -> None:
        self.catalog = get_nestful_catalog(executable=True)

    def test_basic(self) -> None:
        hypothesis = Hypothesis(
            name="SkyScrapperFlightSearch", catalog=self.catalog
        )

        hypothesis.generate_sample()
        first_value = hypothesis.random_value

        hypothesis.generate_sample()
        second_value = hypothesis.random_value

        assert first_value != second_value
        assert isinstance(hypothesis.api, API)
        assert set(hypothesis.api.get_outputs()) == set(first_value.keys())

    def test_nested_level_1(self) -> None:
        pass

    def test_array_length(self) -> None:
        pass
