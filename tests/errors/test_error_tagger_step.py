from nestful.data_handlers import get_nestful_data_instance
from nestful.errors import tag_sequence_step
from nestful.schemas.errors import ErrorType
from nestful.schemas.sequences import ErrorTag
from nestful import SequenceStep
from typing import Dict, Any


class TestErrorTaggerStep:
    def setup_method(self) -> None:
        self.sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

    def test_missing_parameter(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(checkIn="2024-08-15",'
            ' checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory={}
        )

        assert len(tagged_step.errors) == 1
        assert (
            ErrorTag(error_type=ErrorType.MISSING_PARAMETER, info="geoId")
            in tagged_step.errors
        )

    def test_missing_parameter_optional(self) -> None:
        memory = {
            "var1": {
                "skyId": "foo",
                "entityId": "bar",
            },
            "var2": {
                "skyId": "foo",
                "entityId": "bar",
            },
        }

        step_str = (
            'var5 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
            ' originEntityId="$var1.entityId$",'
            ' destinationSkyId="$var2.skyId$",'
            ' destinationEntityId="$var2.entityId$", date="2024-08-15")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[2], memory=memory
        )

        assert len(tagged_step.errors) == 1
        assert (
            ErrorTag(error_type=ErrorType.MISSING_PARAMETER, info="returnDate")
            in tagged_step.errors
        )

    def test_made_up_parameter(self) -> None:
        memory = {"var4": {"geoId": 123}}

        step_str = (
            'var5 = TripadvisorSearchHotels(locationId="$var4.geoId$",'
            ' checkIn="2024-08-15", checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory=memory
        )

        assert len(tagged_step.errors) == 2

        assert (
            ErrorTag(error_type=ErrorType.MADE_UP_PARAMETER, info="locationId")
            in tagged_step.errors
        )

        assert (
            ErrorTag(error_type=ErrorType.MISSING_PARAMETER, info="geoId")
            in tagged_step.errors
        )

    def test_wrong_assignment(self) -> None:
        memory = {"var4": {"geoId": 123}}

        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkIn="2024-08-15", checkOut="08-18-2024")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory=memory
        )

        assert len(tagged_step.errors) == 1
        assert (
            ErrorTag(
                error_type=ErrorType.WRONG_ASSIGNMENT,
                info={"checkOut": "08-18-2024"},
            )
            in tagged_step.errors
        )

    def test_made_up_assignment(self) -> None:
        memory = {"var4": {"geoId": 123}}

        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.locationId$",'
            ' checkIn="2024-08-15", checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory=memory
        )

        assert len(tagged_step.errors) == 3

        assert (
            ErrorTag(error_type=ErrorType.MADE_UP_ASSIGNMENT, info="locationId")
            in tagged_step.errors
        )

        assert (
            ErrorTag(
                error_type=ErrorType.WRONG_ASSIGNMENT,
                info={"geoId": "$var4.locationId$"},
            )
            in tagged_step.errors
        )

        assert (
            ErrorTag(
                error_type=ErrorType.MISSING_MEMORY, info="$var4.locationId$"
            )
            in tagged_step.errors
        )

    def test_missing_memory_nested_correct(self) -> None:
        sequence, _ = get_nestful_data_instance(index=35, executable=True)

        step_str = (
            "var2 ="
            ' WeatherAPI.com_Realtime_Weather_Api(q="$var1.location.name$")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        memory = {"var1": {"location": {"name": "Boston"}}}

        tagged_step = tag_sequence_step(
            step_obj, ground_truth=sequence.output[1], memory=memory
        )

        assert len(tagged_step.errors) == 0

    def test_missing_memory_nested_none_value(self) -> None:
        sequence, _ = get_nestful_data_instance(index=35, executable=True)

        step_str = (
            "var2 ="
            ' WeatherAPI.com_Realtime_Weather_Api(q="$var1.location.name$")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        memory = {"var1": {"location": {"name": None}}}

        tagged_step = tag_sequence_step(
            step_obj, ground_truth=sequence.output[1], memory=memory
        )

        assert len(tagged_step.errors) == 1

        assert (
            ErrorTag(
                error_type=ErrorType.MISSING_MEMORY, info="$var1.location.name$"
            )
            in tagged_step.errors
        )

    def test_missing_memory_nested_empty(self) -> None:
        sequence, _ = get_nestful_data_instance(index=35, executable=True)

        step_str = (
            "var2 ="
            ' WeatherAPI.com_Realtime_Weather_Api(q="$var1.location.name$")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)

        memory: Dict[str, Any] = {"var1": {}}

        tagged_step = tag_sequence_step(
            step_obj, ground_truth=sequence.output[1], memory=memory
        )

        assert len(tagged_step.errors) == 3

        assert (
            ErrorTag(
                error_type=ErrorType.MISSING_MEMORY, info="$var1.location.name$"
            )
            in tagged_step.errors
        )

        assert (
            ErrorTag(error_type=ErrorType.MADE_UP_ASSIGNMENT, info="location")
            in tagged_step.errors
        )

        assert (
            ErrorTag(error_type=ErrorType.MADE_UP_ASSIGNMENT, info="name")
            in tagged_step.errors
        )

    def test_missing_memory(self) -> None:
        step_str = (
            'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            ' checkIn="2024-08-15", checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory={}
        )

        assert len(tagged_step.errors) == 2

        assert (
            ErrorTag(error_type=ErrorType.MISSING_MEMORY, info="$var4.geoId$")
            in tagged_step.errors
        )

        assert (
            ErrorTag(error_type=ErrorType.MADE_UP_ASSIGNMENT, info="geoId")
            in tagged_step.errors
        )

    def test_made_up_api(self) -> None:
        step_str = (
            'var5 = Tripadvisor_Search_Hotels(checkIn="2024-08-15",'
            ' checkOut="2024-08-18")'
        )

        step_obj = SequenceStep.parse_pretty_print(step_str)
        tagged_step = tag_sequence_step(
            step_obj, ground_truth=self.sequence.output[4], memory={}
        )

        assert len(tagged_step.errors) == 1
        assert (
            ErrorTag(
                error_type=ErrorType.MADE_UP_API,
                info="Tripadvisor_Search_Hotels",
            )
            in tagged_step.errors
        )
