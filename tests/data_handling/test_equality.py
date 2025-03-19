from nestful import SequenceStep, SequencingData
from nestful.data_handlers import get_nestful_catalog


class TestEquality:
    def setup_method(self) -> None:
        self.catalog = get_nestful_catalog(executable=True)
        self.tokens = [
            'var1 = SkyScrapperSearchAirport(query="New York")',
            'var2 = SkyScrapperSearchAirport(query="London")',
            (
                'var3 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
            'var4 = TripadvisorSearchLocation(query="London")',
            (
                'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkIn="2024-08-15", checkOut="2024-08-18")'
            ),
        ]

        self.sequence_step = SequenceStep.parse_pretty_print(self.tokens[1])
        self.sequence_data = SequencingData.parse_pretty_print(self.tokens)

    def test_direct_same(self) -> None:
        test_step = SequenceStep.parse_pretty_print(self.tokens[1])
        assert test_step.is_same_as(self.sequence_step, catalog=self.catalog)

    def test_direct_not_same(self) -> None:
        test_step = SequenceStep.parse_pretty_print(self.tokens[0])
        assert not test_step.is_same_as(
            self.sequence_step, catalog=self.catalog
        )

    def test_membership(self) -> None:
        test_step = SequenceStep.parse_pretty_print(self.tokens[0])
        assert test_step.is_same_as(self.sequence_data, catalog=self.catalog)

    def test_not_membership(self) -> None:
        self.tokens[0] = 'var1 = SkyScrapperSearchAirport(query="Paris")'
        self.sequence_data = SequencingData.parse_pretty_print(self.tokens)

        test_step = SequenceStep.parse_pretty_print(
            'var1 = SkyScrapperSearchAirport(query="New York")'
        )

        assert not test_step.is_same_as(
            self.sequence_data, catalog=self.catalog
        )

    def test_required_only_direct(self) -> None:
        test_step = 'var1 = SkyScrapperSearchAirport(query="New York")'
        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert test_step_object.is_same_as(
            self.sequence_step, catalog=self.catalog, required_schema_only=True
        )

    def test_required_only_direct_not(self) -> None:
        test_step = (
            'var4 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
            ' destinationSkyId="$var2.skyId$",'
            ' originEntityId="$var1.entityId$", date="2024-08-15",'
            ' returnDate="2024-08-18")'
        )

        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert (
            test_step_object.is_same_as(
                ground_truth=self.sequence_data.output[3],
                catalog=self.catalog,
                required_schema_only=True,
            )
            is False
        )

    def test_required_only_direct_member(self) -> None:
        test_step = (
            'var4 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
            ' destinationSkyId="$var2.skyId$",'
            ' originEntityId="$var1.entityId$",'
            ' destinationEntityId="$var2.entityId$", date="2024-08-15")'
        )

        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert test_step_object.is_same_as(
            ground_truth=self.sequence_data,
            catalog=self.catalog,
            required_schema_only=True,
        )

    def test_required_only_direct_member_not(self) -> None:
        test_step = (
            'var4 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
            ' destinationSkyId="$var2.skyId$",'
            ' originEntityId="$var1.entityId$", date="2024-08-15",'
            ' returnDate="2024-08-18")'
        )

        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert (
            test_step_object.is_same_as(
                ground_truth=self.sequence_data,
                catalog=self.catalog,
                required_schema_only=True,
            )
            is False
        )

    def test_made_up_api(self) -> None:
        test_step = 'var1 = SkyCrapperSearchAirport(query="New York")'
        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert (
            test_step_object.is_same_as(
                self.sequence_step, catalog=self.catalog
            )
            is False
        )

    def test_made_up_api_required_only(self) -> None:
        test_step = 'var1 = SkyCrapperSearchAirport(query="New York")'
        test_step_object = SequenceStep.parse_pretty_print(test_step)

        assert (
            test_step_object.is_same_as(
                self.sequence_step,
                catalog=self.catalog,
                required_schema_only=True,
            )
            is False
        )
