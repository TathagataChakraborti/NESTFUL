from nestful import SequenceStep, SequencingData


class TestEquality:
    def setup_method(self) -> None:
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
        assert test_step.is_same_as(self.sequence_step)

    def test_direct_not_same(self) -> None:
        test_step = SequenceStep.parse_pretty_print(self.tokens[0])
        assert not test_step.is_same_as(self.sequence_step)

    def test_membership(self) -> None:
        test_step = SequenceStep.parse_pretty_print(self.tokens[0])
        assert test_step.is_same_as(self.sequence_data)

    def test_not_membership(self) -> None:
        self.tokens[0] = 'var1 = SkyScrapperSearchAirport(query="Paris")'
        self.sequence_data = SequencingData.parse_pretty_print(self.tokens)

        test_step = SequenceStep.parse_pretty_print(
            'var1 = SkyScrapperSearchAirport(query="New York")'
        )
        assert not test_step.is_same_as(self.sequence_data)
