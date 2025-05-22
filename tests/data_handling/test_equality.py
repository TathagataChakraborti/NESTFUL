from nestful import SequenceStep, SequencingData
from nestful.data_handlers import get_nestful_data_instance

import pytest


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

    def test_step_equality_with_resolved_memory(self) -> None:
        memory = {"var4": {"geoId": 123}}

        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        assert step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert step_obj.is_same_as(
            self.sequence.output[4],
            catalog=self.catalog,
            memory=memory,
            check_values=True,
        )

        resolved_step_str = (
            'var5 = TripadvisorSearchHotels(geoId="123",'
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        step_obj = SequenceStep.parse_pretty_print(resolved_step_str)

        assert not step_obj.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert step_obj.is_same_as(
            self.sequence.output[4],
            catalog=self.catalog,
            memory=memory,
            check_values=True,
        )

    def test_sequence_equality_with_resolved_memory(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="New York")',
            'var2 = SkyScrapperSearchAirport(query="London")',
            (
                "var3 = SkyScrapperFlightSearch(originSkyId=1,"
                " destinationSkyId=3, originEntityId=2,"
                ' destinationEntityId=4, date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
            'var4 = TripadvisorSearchLocation(query="London")',
            (
                "var5 = TripadvisorSearchHotels(geoId=123,"
                ' checkIn="2024-08-15", checkOut="2024-08-18")'
            ),
        ]

        memory = {
            "var1": {"skyId": 1, "entityId": 2},
            "var2": {"skyId": 3, "entityId": 4},
            "var4": {"geoId": 123},
        }

        sequence_object = SequencingData.parse_pretty_print(tokens)

        assert not sequence_object.is_same_as(
            self.sequence, catalog=self.catalog, check_values=True
        )

        assert sequence_object.is_same_as(
            self.sequence,
            catalog=self.catalog,
            memory=memory,
            check_values=True,
        )

    def test_step_equality_with_resolved_memory_nested(self) -> None:
        memory = {"var4": {"geoId": {"value": 123}}}

        step_str = (
            "var5 = TripadvisorSearchHotels(geoId=123,"
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        step_object = SequenceStep.parse_pretty_print(step_str)

        reference_step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId.value$",'
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        reference_step_object = SequenceStep.parse_pretty_print(
            reference_step_str
        )

        assert not step_object.is_same_as(
            reference_step_object, catalog=self.catalog, check_values=True
        )

        assert step_object.is_same_as(
            reference_step_object,
            catalog=self.catalog,
            check_values=True,
            memory=memory,
        )

    @pytest.mark.skip(reason="ISS36")
    def test_step_equality_with_resolved_memory_non_string(self) -> None:
        memory = {"var4": {"geoId": {"value": 123}}}

        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="{"value": 123}",'
            ' checkOut="2024-08-18", checkIn="2024-08-15")'
        )

        step_object = SequenceStep.parse_pretty_print(step_str)

        assert not step_object.is_same_as(
            self.sequence.output[4], catalog=self.catalog, check_values=True
        )

        assert step_object.is_same_as(
            self.sequence.output[4],
            catalog=self.catalog,
            check_values=True,
            memory=memory,
        )
