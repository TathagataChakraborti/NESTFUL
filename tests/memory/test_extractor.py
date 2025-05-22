from nestful.memory import (
    extract_references_from_memory,
    extract_reference_from_memory,
)


class TestExtractor:
    def setup_method(self) -> None:
        self.memory = {
            "date": "2024-09-13",
            "payload": {"foo": {"bar": {"baz": 1}}},
            "var4": {
                "skyId": "123",
                "location": {
                    "zipcode": 700031,
                },
            },
        }

    def test_no_match(self) -> None:
        assert (
            extract_reference_from_memory(value=12345, memory=self.memory)
            is None
        )

    def test_direct(self) -> None:
        assert (
            extract_reference_from_memory(
                value="2024-09-13", memory=self.memory
            )
            == "$date$"
        )

    def test_nested(self) -> None:
        assert (
            extract_reference_from_memory(value=700031, memory=self.memory)
            == "$var4.location.zipcode$"
        )

    def test_nested_2(self) -> None:
        assert (
            extract_reference_from_memory(value=1, memory=self.memory)
            == "$payload.foo.bar.baz$"
        )

    def test_object_match(self) -> None:
        assert (
            extract_reference_from_memory(
                value={"bar": {"baz": 1}}, memory=self.memory
            )
            == "$payload.foo$"
        )

    def test_stringify(self) -> None:
        assert (
            extract_reference_from_memory(value=123, memory=self.memory) is None
        )

        assert (
            extract_reference_from_memory(
                value="123", memory=self.memory, stringify=True
            )
            == "$var4.skyId$"
        )

    def test_extract_args(self) -> None:
        args = {
            "datetime": "2024-09-13",
            "howmany": 1,
            "herring": "red",
            "location": {
                "zipcode": 700031,
            },
        }

        assert extract_references_from_memory(args, memory=self.memory) == {
            "datetime": "$date$",
            "howmany": "$payload.foo.bar.baz$",
            "herring": "red",
            "location": "$var4.location$",
        }
