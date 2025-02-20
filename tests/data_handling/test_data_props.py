from nestful.data_handlers import get_nestful_catalog
from nestful import API, MinifiedAPI


class TestAPISchema:
    def test_parse_api_data(self) -> None:
        catalog = get_nestful_catalog(version="v1", executable=True)
        assert len(catalog.apis) == 39

        sky_scrapper_flight_search = catalog.get_api(
            name="SkyScrapperFlightSearch"
        )

        assert isinstance(sky_scrapper_flight_search, API)
        assert len(sky_scrapper_flight_search.query_parameters) == 16

        sky_scrapper_flight_search_minified = (
            sky_scrapper_flight_search.minified(required=True)
        )

        assert isinstance(sky_scrapper_flight_search_minified, MinifiedAPI)
        assert sky_scrapper_flight_search_minified.inputs == [
            "originSkyId",
            "destinationSkyId",
            "originEntityId",
            "destinationEntityId",
            "date",
        ]

    def test_parse_api_data_glaive(self) -> None:
        catalog = get_nestful_catalog(
            version="v1", executable=False, name="glaive"
        )
        assert len(catalog.apis) == 70

    def test_parse_api_data_sgd(self) -> None:
        catalog = get_nestful_catalog(
            version="v1", executable=False, name="sgd"
        )
        assert len(catalog.apis) == 30
