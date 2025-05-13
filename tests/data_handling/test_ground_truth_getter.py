from nestful.data_handlers import get_nestful_data_instance
from nestful import SequencingData


class TestErrorTaggerSequence:
    def setup_method(self) -> None:
        self.gt_sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            # NOTE: Normal repeat but not in order
            'var2 = SkyScrapperSearchAirport(query="New York")',
            # NOTE: Disordered step
            'var3 = TripadvisorSearchLocation(query="London")',
            # NOTE: New call
            'var4 = NewsAPISearchByKeyWord(query="today")',
            (
                'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15")'
            ),
            # NOTE: Repeat call
            'var6 = TripadvisorSearchLocation(query="London")',
            # NOTE: Repeat call
            'var7 = SkyScrapperSearchAirport(query="London")',
            (
                'var8 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="$var4.date$",'
                ' returnDate="2024-08-18")'
            ),
        ]

        self.sequence_object = SequencingData.parse_pretty_print(tokens)

    def test_get_ground_truth_normal(self) -> None:
        _, step = self.sequence_object.get_ground_truth_step(
            index=7, ground_truth=self.gt_sequence
        )

        assert step is not None
        assert step.label == "var3"
        assert step.name == "SkyScrapperFlightSearch"

    def test_get_ground_truth_repeat(self) -> None:
        _, step = self.sequence_object.get_ground_truth_step(
            index=1, ground_truth=self.gt_sequence
        )

        assert step is not None
        assert step.label == "var2"
        assert step.name == "SkyScrapperSearchAirport"
        assert step.arguments["query"] == "London"

    def test_get_ground_truth_extra_call(self) -> None:
        indices, step = self.sequence_object.get_ground_truth_step(
            index=6, ground_truth=self.gt_sequence
        )

        assert step is None
        assert indices == [0, 1]

    def test_get_ground_truth_new_call(self) -> None:
        indices, step = self.sequence_object.get_ground_truth_step(
            index=3, ground_truth=self.gt_sequence
        )

        assert step is None
        assert indices == []
