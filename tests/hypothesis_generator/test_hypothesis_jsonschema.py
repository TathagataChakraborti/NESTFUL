from nestful.data_handlers import get_nestful_catalog
from nestful.hypothesis_generator import Hypothesis
from nestful import API
from typing import List


class TestHypothesisJSONSchema:
    def setup_method(self) -> None:
        self.catalog = get_nestful_catalog(executable=True)

    def test_basic(self) -> None:
        hypothesis = Hypothesis(
            name="SkyScrapperFlightSearch", catalog=self.catalog
        )

        hypothesis.generate_sample()
        value = hypothesis.random_value

        assert isinstance(hypothesis.api, API)
        assert set(hypothesis.api.get_outputs()) == set(value.keys())

    def test_nested_level(self) -> None:
        hypothesis = Hypothesis(
            name="SkyScrapperSearchAirport", catalog=self.catalog
        )

        hypothesis.generate_sample()
        value = hypothesis.random_value

        assert isinstance(hypothesis.api, API)

        assert value["navigation"]["localizedName"]
        assert value["navigation"]["relevantFlightParams"]["skyId"]

    def test_array_length_1(self) -> None:
        hypothesis = Hypothesis(
            name="TripadvisorSearchHotels", catalog=self.catalog
        )

        hypothesis.generate_sample(min_array_length=5)
        value = hypothesis.random_value

        assert isinstance(hypothesis.api, API)
        assert isinstance(value["cardPhotos"], List)
        assert len(value["cardPhotos"]) >= 5

    def test_array_length_2(self) -> None:
        hypothesis = Hypothesis(
            name="Goodreads_Search_Quotes_By_Keyword", catalog=self.catalog
        )

        hypothesis.generate_sample()
        value = hypothesis.random_value

        assert isinstance(hypothesis.api, API)
        assert isinstance(value["urls"], List)
        assert len(value["urls"]) >= 3
        assert all([isinstance(item, str) for item in value["urls"]])
