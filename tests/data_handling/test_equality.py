from nestful import SequenceStep, SequencingData
from nestful.data_handlers import get_nestful_data_instance


class TestEquality:
    def setup_method(self) -> None:
        self.sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

        # [
        #     'var1 = SkyScrapperSearchAirport(query="New York")',
        #     'var2 = SkyScrapperSearchAirport(query="London")',
        #     (
        #         'var3 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
        #         ' destinationSkyId="$var2.skyId$",'
        #         ' originEntityId="$var1.entityId$",'
        #         ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
        #         ' returnDate="2024-08-18")'
        #     ),
        #     'var4 = TripadvisorSearchLocation(query="London")',
        #     (
        #         'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
        #         ' checkIn="2024-08-15", checkOut="2024-08-18")'
        #     ),
        # ]

    def test_exact_same_step(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkIn="2024-08-15", checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert self.sequence.contains(
            step_obj, catalog=self.catalog, check_values=True
        )

    def test_wrong_name(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotelsAPI(geoId="$var4.geoId$",'
            ' checkIn="2024-08-15", checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert not step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert not self.sequence.contains(step_obj, catalog=self.catalog)

    def test_exact_same_step_disorder(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert self.sequence.contains(
            step_obj, catalog=self.catalog, check_values=True
        )

    def test_same_step_wrong_assignment(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-15-08")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog
        )

        assert not step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert self.sequence.contains(step_obj, catalog=self.catalog)

        assert not self.sequence.contains(
            step_obj, catalog=self.catalog, check_values=True
        )

    def test_same_step_wrong_assignment_optional(self) -> None:
        step_str_1 = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15", pageNumber="3")'
        )

        step_str_2 = (
            'var3 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15", pageNumber="2")'
        )

        step_obj_1 = SequenceStep.parse_pretty_print(step_str_1)
        step_obj_2 = SequenceStep.parse_pretty_print(step_str_2)

        assert not step_obj_1.is_same_as(
            step_obj_2, catalog=self.catalog, check_values=True
        )

        assert step_obj_1.is_same_as(
            self.sequence.output[4],
            catalog=self.catalog,
            required_schema_only=True,
            check_values=True,
        )

        assert not self.sequence.contains(
            step_obj_1, catalog=self.catalog, check_values=True
        )

        assert not self.sequence.contains(step_obj_1, catalog=self.catalog)

        assert self.sequence.contains(
            step_obj_1,
            catalog=self.catalog,
            required_schema_only=True,
        )

        assert self.sequence.contains(
            step_obj_1,
            catalog=self.catalog,
            required_schema_only=True,
            check_values=True,
        )

    def test_same_step_wrong_assignment_optional_made_up(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15", madeup="3")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert not step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert step_obj.is_same_as(
            self.sequence.output[4],
            catalog=self.catalog,
            required_schema_only=True,
            check_values=True,
        )

        assert not self.sequence.contains(
            step_obj, catalog=self.catalog, check_values=True
        )

        assert not self.sequence.contains(step_obj, catalog=self.catalog)

        assert self.sequence.contains(
            step_obj,
            catalog=self.catalog,
            required_schema_only=True,
        )

        assert self.sequence.contains(
            step_obj,
            catalog=self.catalog,
            required_schema_only=True,
            check_values=True,
        )

    def test_sequence_disorder(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            'var2 = SkyScrapperSearchAirport(query="New York")',
            'var3 = TripadvisorSearchLocation(query="London")',
            (
                'var4 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15")'
            ),
            (
                'var5 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)

        assert sequence_object.is_same_as(
            ground_truth=self.sequence, catalog=self.catalog, check_values=True
        )

    def test_sequence_disorder_extra_steps(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="New York")',
            'var2 = SkyScrapperSearchAirport(query="London")',
            (
                'var3 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
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

        sequence_object = SequencingData.parse_pretty_print(tokens)

        assert sequence_object.is_same_as(
            ground_truth=self.sequence, catalog=self.catalog, check_values=True
        )

        sequence_object = SequencingData.parse_pretty_print(tokens[:-2])

        assert not sequence_object.is_same_as(
            ground_truth=self.sequence, catalog=self.catalog, check_values=True
        )

    def test_sequence_optionals(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="New York")',
            'var2 = SkyScrapperSearchAirport(query="London")',
            'var3 = TripadvisorSearchLocation(query="London")',
            (
                'var5 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-18-08")'
            ),
            (
                'var4 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15", pageNumber="3")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)

        assert not sequence_object.is_same_as(
            ground_truth=self.sequence, catalog=self.catalog, check_values=True
        )

        assert not sequence_object.is_same_as(
            ground_truth=self.sequence, catalog=self.catalog
        )

        assert sequence_object.is_same_as(
            ground_truth=self.sequence,
            catalog=self.catalog,
            required_schema_only=True,
            check_values=False,
        )

        assert sequence_object.is_same_as(
            ground_truth=self.sequence,
            catalog=self.catalog,
            required_schema_only=True,
        )
