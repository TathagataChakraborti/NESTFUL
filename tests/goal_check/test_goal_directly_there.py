from nestful.data_handlers import get_nestful_catalog
from nestful import SequencingData, SequenceStep


class TestGoalDirectlyThere:
    def setup_method(self) -> None:
        self.catalog = get_nestful_catalog(executable=True)

        ground_truth_sequence_dict = [
            {
                "name": "SkyScrapperSearchAirport",
                "arguments": {"query": "New York"},
                "label": "var1",
            },
            {
                "name": "SkyScrapperSearchAirport",
                "arguments": {"query": "London"},
                "label": "var2",
            },
            {
                "name": "SkyScrapperFlightSearch",
                "arguments": {
                    "originSkyId": "$var1.skyId$",
                    "destinationSkyId": "$var2.skyId$",
                    "originEntityId": "$var1.entityId$",
                    "destinationEntityId": "$var2.entityId$",
                    "date": "2024-08-15",
                    "returnDate": "2024-08-18",
                },
                "label": "var3",
            },
            {
                "name": "TripadvisorSearchLocation",
                "arguments": {"query": "London"},
                "label": "var4",
            },
            {
                "name": "TripadvisorSearchHotels",
                "arguments": {
                    "geoId": "$var4.geoId$",
                    "checkIn": "2024-08-15",
                    "checkOut": "2024-08-18",
                },
                "label": "var5",
            },
            {
                "name": "var_result",
                "arguments": {"flights": "$var3$", "hotels": "$var5$"},
            },
        ]

        self.ground_truth_sequence = SequencingData(
            output=[
                SequenceStep.model_validate(item)
                for item in ground_truth_sequence_dict
            ]
        )

        test_sequence_dict = [
            {
                "name": "SkyScrapperSearchAirport",
                "arguments": {"query": "New York"},
                "label": "var1",
            },
            {
                "name": "SkyScrapperSearchAirport",
                "arguments": {"query": "London"},
                "label": "var2",
            },
            {
                "name": "SkyScrapperFlightSearch",
                "arguments": {
                    "originSkyId": "$var1.skyId$",
                    "destinationSkyId": "$var2.skyId$",
                    "originEntityId": "$var1.entityId$",
                    "destinationEntityId": "$var2.entityId$",
                    "date": "2024-08-15",
                    "returnDate": "2024-08-18",
                    "cabinClass": "economy",
                    "adults": 1,
                    "children": 0,
                    "infants": 0,
                    "sortBy": "best",
                },
                "label": "var3",
            },
            {
                "name": "TripadvisorSearchLocation",
                "arguments": {"query": "London"},
                "label": "var4",
            },
            {
                "name": "TripadvisorSearchHotels",
                "arguments": {
                    "geoId": "$var4.geoId$",
                    "checkIn": "2024-08-15",
                    "checkOut": "2024-08-18",
                    "pageNumber": 1,
                    "sort": "price",
                    "adults": 1,
                    "rooms": 1,
                    "currencyCode": "USD",
                },
                "label": "var5",
            },
        ]

        self.test_sequence = SequencingData(
            output=[
                SequenceStep.model_validate(item) for item in test_sequence_dict
            ]
        )

    def test_no_memory(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog, ground_truth=self.ground_truth_sequence
            )
            is False
        )

    def test_with_fake_memory(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                fill_in_memory=True,
            )
            is True
        )

    def test_result_actual_memory_simple(self) -> None:
        memory = {
            "var1": "foo",
            "var2": "bar",
            "var3": "baz",
            "var4": "qux",
            "var5": "quxx",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is True
        )

    def test_result_actual_memory_missing(self) -> None:
        memory = {
            "var1": "foo",
            "var2": "bar",
            "var3": "baz",
            "var4": {"qux": "quxx"},
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is False
        )

    def test_retrieved_memory_with_fill(self) -> None:
        memory = self.test_sequence.get_memory(
            self.catalog, fill_in_memory=True
        )
        assert set(memory.keys()) == {
            f"var{i}" for i in range(1, len(self.test_sequence.output) + 1)
        }

    def test_retrieved_memory_with_fill_with_index(self) -> None:
        test_index = 3

        memory = self.test_sequence.get_memory(
            self.catalog, index=test_index, fill_in_memory=True
        )
        assert set(memory.keys()) == {
            f"var{i}" for i in range(1, test_index + 1)
        }

    def test_custom_var_result(self) -> None:
        var_result = {
            "foo": "$var3$",
            "bar": "$var5.provider$",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                var_result=var_result,
                fill_in_memory=True,
            )
            is True
        )
