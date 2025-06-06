from nestful.data_handlers import get_nestful_catalog
from nestful import SequencingData, SequenceStep, API


class TestTrajectoryCheck:
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

        self.test_sequence_dict = [
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
                    "children": "$var3.status$",
                    "infants": "$var3.status$",
                    "sortBy": "best",
                },
                "label": "var4",
            },
            {
                "name": "TripadvisorSearchLocation",
                "arguments": {"query": "London"},
                "label": "var5",
            },
            {
                "name": "TripadvisorSearchHotels",
                "arguments": {
                    "geoId": "$var5.geoId$",
                    "checkIn": "2024-08-15",
                    "checkOut": "2024-08-18",
                    "pageNumber": 1,
                    "sort": "price",
                    "adults": 1,
                    "rooms": 1,
                    "currencyCode": "USD",
                },
                "label": "var6",
            },
            {
                "name": "TripadvisorSearchHotels",
                "arguments": {
                    "geoId": "$var5.geoId$",
                    "checkIn": "2025-08-15",
                    "checkOut": "2025-08-18",
                    "pageNumber": 1,
                    "sort": "price",
                    "adults": 1,
                    "rooms": 1,
                    "currencyCode": "USD",
                },
                "label": "var7",
            },
        ]

        self.test_sequence = SequencingData(
            output=[
                SequenceStep.model_validate(item)
                for item in self.test_sequence_dict
            ]
        )

    def test_who_done_it(self) -> None:
        assert self.ground_truth_sequence.who_produced("var6") == (None, 0)
        assert self.ground_truth_sequence.who_produced("var5") == (
            "TripadvisorSearchHotels",
            1,
        )

        assert self.ground_truth_sequence.who_produced("var1") == (
            "SkyScrapperSearchAirport",
            1,
        )

        assert self.ground_truth_sequence.who_produced("var2") == (
            "SkyScrapperSearchAirport",
            2,
        )

        assert self.test_sequence.who_produced("var6") == (
            "TripadvisorSearchHotels",
            1,
        )

        assert self.test_sequence.who_produced("var4") == (
            "SkyScrapperFlightSearch",
            2,
        )

    def test_what_did_they_do(self) -> None:
        assert (
            self.ground_truth_sequence.get_label("TripadvisorSearchHotels")
            == "var5"
        )

        assert (
            self.ground_truth_sequence.get_label("SkyScrapperSearchAirport")
            == "var1"
        )

        assert (
            self.ground_truth_sequence.get_label(
                name="SkyScrapperSearchAirport", index=2
            )
            == "var2"
        )

        name, index = self.ground_truth_sequence.who_produced("var2")
        assert (
            name is not None
            and self.ground_truth_sequence.get_label(name, index) == "var2"
        )

        assert (
            self.test_sequence.get_label(
                name="TripadvisorSearchHotels", index=2
            )
            == "var7"
        )

        name, index = self.ground_truth_sequence.who_produced("var5")
        assert (
            name is not None
            and self.test_sequence.get_label(name, index) == "var6"
        )

    def test_who_used(self) -> None:
        assert self.ground_truth_sequence.who_used("var4") == [4]
        assert self.ground_truth_sequence.who_used("var5") == []
        assert self.test_sequence.who_used("var5") == [5, 6]

    def test_remove_reference_sequence(self) -> None:
        sequence = self.test_sequence.remove_reference(label="var5")

        assert len(sequence.output) == len(self.test_sequence.output) - 1
        assert "TripadvisorSearchLocation" not in [
            item.name for item in sequence.output
        ]

        for i in range(1, 3):
            assert sequence.output[-i].name == "TripadvisorSearchHotels"
            assert "geoId" not in sequence.output[-i].arguments

    def test_missing_step(self) -> None:
        test_sequence = SequencingData(
            output=[
                SequenceStep.model_validate(item)
                for item in self.test_sequence_dict[:5]
            ]
        )

        name, index = self.ground_truth_sequence.who_produced("var5")
        assert (
            name == "TripadvisorSearchHotels"
            and test_sequence.get_label(name, index) is None
        )

    def test_get_spec_step(self) -> None:
        step = SequenceStep(name="TripadvisorSearchHotels")
        spec = step.get_tool_spec(catalog=self.catalog)

        assert isinstance(spec, API)
        assert spec.name == "TripadvisorSearchHotels"
        assert spec.get_arguments(required=True) == [
            "geoId",
            "checkIn",
            "checkOut",
        ]

        print(spec)

    def test_get_spec_made_up_step(self) -> None:
        step = SequenceStep(name="IamanLLMImadethisup!")
        spec = step.get_tool_spec(catalog=self.catalog)

        assert spec is None

    def test_get_spec_sequence(self) -> None:
        sequence = SequencingData(
            output=[
                SequenceStep(name="SkyScrapperSearchAirport"),
                SequenceStep(name="SkyScrapperSearchAirport"),
                SequenceStep(name="IamanLLMImadethisup"),
                SequenceStep(name="SkyScrapperFlightSearch"),
            ]
        )

        specs = sequence.get_tool_specs(catalog=self.catalog)

        assert [spec.name for spec in specs] == [
            "SkyScrapperSearchAirport",
            "SkyScrapperFlightSearch",
        ]
