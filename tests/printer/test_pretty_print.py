from nestful.data_handlers import get_nestful_data_instance, get_nestful_data


class TestPrettyPrint:
    def test_parse_sequence_data(self) -> None:
        sequence_data, _ = get_nestful_data(executable=True)
        assert len(sequence_data.data) == 85

    def test_print_as_plan(self) -> None:
        sequence, catalog = get_nestful_data_instance(executable=True, index=0)
        pretty_print = sequence.pretty_print()

        assert pretty_print.split("\n") == [
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
            'var_result(flights="$var3$", hotels="$var5$")',
        ]
