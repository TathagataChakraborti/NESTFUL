from nestful.data_handlers import get_nestful_data_instance
from nestful.errors import tag_sequence
from nestful.schemas.errors import ErrorType
from nestful.schemas.sequences import ErrorTag
from nestful import SequencingData


class TestErrorTaggerSequence:
    def setup_method(self) -> None:
        self.sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

    def test_missing_call(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            'var2 = SkyScrapperSearchAirport(query="New York")',
            'var3 = TripadvisorSearchLocation(query="London")',
            # (
            #     'var4 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
            #     ' checkOut="2024-08-18", checkIn="2024-08-15")'
            # ),
            (
                'var5 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)
        tagged_sequence = tag_sequence(
            sequence_object,
            ground_truth=self.sequence,
            memory={},
            catalog=self.catalog,
        )

        assert len(tagged_sequence.errors) == 1
        assert (
            ErrorTag(
                error_type=ErrorType.MISSING_CALL,
                info="TripadvisorSearchHotels",
            )
            in tagged_sequence.errors
        )

    def test_missing_call_repeat(self) -> None:
        tokens = [
            # 'var1 = SkyScrapperSearchAirport(query="London")',
            # 'var2 = SkyScrapperSearchAirport(query="New York")',
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
        tagged_sequence = tag_sequence(
            sequence_object,
            ground_truth=self.sequence,
            memory={},
            catalog=self.catalog,
        )

        assert len(tagged_sequence.errors) == 2

        for err in tagged_sequence.errors:
            assert err == ErrorTag(
                error_type=ErrorType.MISSING_CALL,
                info="SkyScrapperSearchAirport",
            )

    def test_repeat_call(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            'var2 = SkyScrapperSearchAirport(query="New York")',
            'var3 = TripadvisorSearchLocation(query="London")',
            (
                'var4 = TripadvisorSearchHotels(checkOut="2024-08-18",'
                ' checkIn="2024-08-15")'
            ),
            (
                'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15")'
            ),
            (
                'var6 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)
        tagged_sequence = tag_sequence(
            sequence_object,
            ground_truth=self.sequence,
            memory={},
            catalog=self.catalog,
        )

        assert len(tagged_sequence.errors) == 1

        assert (
            ErrorTag(
                error_type=ErrorType.BAD_REPEAT, info="TripadvisorSearchHotels"
            )
            in tagged_sequence.errors
        )
        assert (
            ErrorTag(error_type=ErrorType.MISSING_PARAMETER, info="geoId")
            in tagged_sequence.output[3].errors
        )

    def test_new_call(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            'var2 = SkyScrapperSearchAirport(query="New York")',
            'var3 = TripadvisorSearchLocation(query="London")',
            (
                'var4 = Tripadvisor_Search_Hotels(checkOut="2024-08-18",'
                ' checkIn="2024-08-15")'
            ),
            (
                'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15")'
            ),
            (
                'var6 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="2024-08-15",'
                ' returnDate="2024-08-18")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)
        tagged_sequence = tag_sequence(
            sequence_object,
            ground_truth=self.sequence,
            memory={},
            catalog=self.catalog,
        )

        assert len(tagged_sequence.errors) == 2

        assert (
            ErrorTag(
                error_type=ErrorType.NEW_CALL, info="Tripadvisor_Search_Hotels"
            )
            in tagged_sequence.errors
        )
        assert (
            ErrorTag(
                error_type=ErrorType.MADE_UP_API,
                info="Tripadvisor_Search_Hotels",
            )
            in tagged_sequence.errors
        )

    def test_new_call_made_up(self) -> None:
        tokens = [
            'var1 = SkyScrapperSearchAirport(query="London")',
            'var2 = SkyScrapperSearchAirport(query="New York")',
            'var3 = TripadvisorSearchLocation(query="London")',
            'var4 = NewsAPISearchByKeyWord(query="today")',
            (
                'var5 = TripadvisorSearchHotels(geoId="$var4.geoId$",'
                ' checkOut="2024-08-18", checkIn="2024-08-15")'
            ),
            (
                'var6 = SkyScrapperFlightSearch(originSkyId="$var1.skyId$",'
                ' originEntityId="$var1.entityId$",'
                ' destinationSkyId="$var2.skyId$",'
                ' destinationEntityId="$var2.entityId$", date="$var4.date$",'
                ' returnDate="2024-08-18")'
            ),
        ]

        sequence_object = SequencingData.parse_pretty_print(tokens)
        tagged_sequence = tag_sequence(
            sequence_object,
            ground_truth=self.sequence,
            memory={},
            catalog=self.catalog,
        )

        assert len(tagged_sequence.errors) == 1

        assert (
            ErrorTag(
                error_type=ErrorType.NEW_CALL, info="NewsAPISearchByKeyWord"
            )
            in tagged_sequence.errors
        )
