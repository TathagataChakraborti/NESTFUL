from nestful.schemas.tools import Tool


class TestSelectorInResponseSelector:
    def setup_method(self) -> None:
        self.tool = tool

    def test_basic(self) -> None:
        tool_spec = Tool.model_validate(self.tool)
        nestful_form = tool_spec.convert_to_catalog_spec()

        assert set(nestful_form.get_outputs()) == {
            "state_id",
            "address_line_1",
            "country_id",
            "address_line_2",
            "state_id.prop2",
            "postal_code",
            "state_id.prop1",
            "city",
            "address_id",
        }


tool = {
    "description": "Workday",
    "name": "get_info",
    "parameters": {
        "type": "object",
        "properties": {"person_id": {"type": "string", "title": "Person Id"}},
        "required": ["person_id"],
    },
    "output_parameters": {
        "description": "WorkdayHomeAddress",
        "anyOf": [
            {
                "type": "object",
                "title": "Address Part One",
                "properties": {
                    "city": {"type": "string", "title": "City"},
                    "state_id": {
                        "title": "State Id",
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"prop1": {"type": "string"}},
                                },
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"prop2": {"type": "string"}},
                                },
                            },
                        ],
                    },
                    "address_id": {"type": "string", "title": "Address Id"},
                    "country_id": {"type": "string", "title": "Country Id"},
                    "postal_code": {"type": "string", "title": "Postal Code"},
                },
                "required": [
                    "address_id",
                    "city",
                    "state_id",
                    "country_id",
                    "postal_code",
                ],
            },
            {
                "type": "object",
                "title": "Address Part Two",
                "properties": {
                    "address_line_1": {
                        "type": "string",
                        "title": "Address Line 1",
                    },
                    "address_line_2": {
                        "title": "Address Line 2",
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                    },
                },
                "required": [
                    "address_line_1",
                ],
            },
            {"type": "null"},
        ],
    },
}
