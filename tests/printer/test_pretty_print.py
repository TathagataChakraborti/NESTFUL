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
        ]

    def test_sequence_step_str(self) -> None:
        sequence, _ = get_nestful_data_instance(executable=True, index=0)

        assert (
            str(sequence.output[1])
            == "{'name': 'SkyScrapperSearchAirport', 'arguments': {'query':"
            " 'London'}}"
        )

        assert (
            str(sequence.output[4])
            == "{'name': 'TripadvisorSearchHotels', 'arguments': {'geoId':"
            " '$var4.geoId$', 'checkIn': '2024-08-15', 'checkOut':"
            " '2024-08-18'}}"
        )

    def test_sequence_str(self) -> None:
        sequence, _ = get_nestful_data_instance(executable=True, index=0)

        print(sequence)

        assert (
            str(sequence)
            == "[\n{'name': 'SkyScrapperSearchAirport', 'arguments': {'query':"
            " 'New York'}},\n{'name': 'SkyScrapperSearchAirport',"
            " 'arguments': {'query': 'London'}},\n{'name':"
            " 'SkyScrapperFlightSearch', 'arguments': {'originSkyId':"
            " '$var1.skyId$', 'destinationSkyId': '$var2.skyId$',"
            " 'originEntityId': '$var1.entityId$', 'destinationEntityId':"
            " '$var2.entityId$', 'date': '2024-08-15', 'returnDate':"
            " '2024-08-18'}},\n{'name': 'TripadvisorSearchLocation',"
            " 'arguments': {'query': 'London'}},\n{'name':"
            " 'TripadvisorSearchHotels', 'arguments': {'geoId':"
            " '$var4.geoId$', 'checkIn': '2024-08-15', 'checkOut':"
            " '2024-08-18'}}\n]"
        )
