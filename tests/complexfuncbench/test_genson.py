from genson import SchemaBuilder


class TestGenson:
    def setup_method(self) -> None:
        self.builder = SchemaBuilder()
        self.builder.add_schema({"type": "object", "properties": {}})

        self.sample_response = {
            "city": "San Diego",
            "coordinates": {"latitude": 32.873055, "longitude": -117.215935},
            "country": "United States",
            "name": "San Diego Marriott La Jolla",
        }

    def test_basic(self) -> None:
        self.builder.add_object(self.sample_response)
        schema = self.builder.to_schema()

        assert schema["properties"].keys() == {
            "city",
            "coordinates",
            "country",
            "name",
        }
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["coordinates"]["type"] == "object"
        assert (
            schema["properties"]["coordinates"]["properties"]["latitude"][
                "type"
            ]
            == "number"
        )

    def test_merge(self) -> None:
        new_response = {
            "city": "Washington",
            "coordinates": {
                "latitude": 38.8496017456055,
                "longitude": -77.0412979125977,
            },
            "country": "United States",
            "iata_code": "DCA",
            "name": "Ronald Reagan Washington National Airport",
            "type": "airport",
        }

        self.builder.add_object(self.sample_response)
        self.builder.add_object(new_response)

        schema = self.builder.to_schema()
        required_keys = {"city", "coordinates", "country", "name"}

        assert schema["properties"].keys() == {
            *required_keys,
            "type",
            "iata_code",
        }
        assert set(schema["required"]) == required_keys
