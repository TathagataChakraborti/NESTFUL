from nestful.data_handlers import (
    get_nestful_data_instance,
    get_nestful_data,
    get_nestful_catalog,
)


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
            " 'London'}, 'label': 'var2'}"
        )

        assert (
            str(sequence.output[4])
            == "{'name': 'TripadvisorSearchHotels', 'arguments': {'geoId':"
            " '$var4.geoId$', 'checkIn': '2024-08-15', 'checkOut':"
            " '2024-08-18'}, 'label': 'var5'}"
        )

    def test_sequence_str(self) -> None:
        sequence, _ = get_nestful_data_instance(executable=True, index=0)

        print(sequence)

        assert (
            str(sequence)
            == "[\n{'name': 'SkyScrapperSearchAirport', 'arguments': {'query':"
            " 'New York'}, 'label': 'var1'},\n{'name':"
            " 'SkyScrapperSearchAirport', 'arguments': {'query': 'London'},"
            " 'label': 'var2'},\n{'name': 'SkyScrapperFlightSearch',"
            " 'arguments': {'originSkyId': '$var1.skyId$',"
            " 'destinationSkyId': '$var2.skyId$', 'originEntityId':"
            " '$var1.entityId$', 'destinationEntityId': '$var2.entityId$',"
            " 'date': '2024-08-15', 'returnDate': '2024-08-18'}, 'label':"
            " 'var3'},\n{'name': 'TripadvisorSearchLocation', 'arguments':"
            " {'query': 'London'}, 'label': 'var4'},\n{'name':"
            " 'TripadvisorSearchHotels', 'arguments': {'geoId':"
            " '$var4.geoId$', 'checkIn': '2024-08-15', 'checkOut':"
            " '2024-08-18'}, 'label': 'var5'}\n]"
        )

    def test_api_str(self) -> None:
        catalog = get_nestful_catalog(executable=True)
        api_spec = catalog.get_api(name="Spotify_Scraper_List_Related_Artists")

        print(api_spec)

        assert (
            str(api_spec)
            == "{'name': 'Spotify_Scraper_List_Related_Artists', 'description':"
            " 'Retrieve a list of related artists based on the provided"
            " Artist ID.', 'parameters': {'artistId': {'type': 'String',"
            " 'description': 'Unique identifier of the artist.', 'required':"
            " True, 'enum': [], 'allowed_values': [], 'default_value':"
            " None}}, 'output_schema': {'type': {'title': '', 'type':"
            " 'string', 'description': \"Type of the artist (e.g.,"
            " 'artist').\", 'enum': [], 'required': [], 'properties': {},"
            " 'items': None}, 'id': {'title': '', 'type': 'string',"
            " 'description': 'Unique identifier of the artist.', 'enum': [],"
            " 'required': [], 'properties': {}, 'items': None}, 'name':"
            " {'title': '', 'type': 'string', 'description': 'Name of the"
            " artist.', 'enum': [], 'required': [], 'properties': {},"
            " 'items': None}, 'shareUrl': {'title': '', 'type': 'string',"
            " 'description': 'URL to open the artist in Spotify.', 'enum':"
            " [], 'required': [], 'properties': {}, 'items': None}}}"
        )
