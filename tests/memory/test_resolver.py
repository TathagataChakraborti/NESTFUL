from nestful.memory import (
    resolve_in_memory,
    resolve_item_in_memory,
)


class TestResolver:
    def setup_method(self) -> None:
        self.memory = {
            "query": "London",
            "user": {
                "age": 32,
            },
            "var1": {
                "geoId": "foo",
            },
            "var2": {"location": {"name": "Whitechapel"}},
            "var3": {"location": {"address": {"zipcode": "02142"}}},
            "var4": {
                "items": [
                    {"foo": 1},
                    {
                        "bar": {
                            "baz": 3,
                        }
                    },
                ]
            },
        }

    def test_array(self) -> None:
        assert (
            resolve_item_in_memory(
                assignment="$var4.items[1].bar.baz$", memory=self.memory
            )
            == 3
        )

    def test_direct(self) -> None:
        assert (
            resolve_item_in_memory(assignment="$query$", memory=self.memory)
            == "London"
        )

    def test_nested_direct(self) -> None:
        assert (
            resolve_item_in_memory(assignment="$user.age$", memory=self.memory)
            == 32
        )

    def test_reference(self) -> None:
        assert (
            resolve_item_in_memory(
                assignment="$var1.geoId$", memory=self.memory
            )
            == "foo"
        )

    def test_nested_reference(self) -> None:
        assert (
            resolve_item_in_memory(
                assignment="$var2.location.name$", memory=self.memory
            )
            == "Whitechapel"
        )

    def test_nested_reference_2(self) -> None:
        assert (
            resolve_item_in_memory(
                assignment="$var3.location.address.zipcode$", memory=self.memory
            )
            == "02142"
        )

    def test_non_reference(self) -> None:
        assert (
            resolve_item_in_memory(assignment="2024-12-25", memory=self.memory)
            == "2024-12-25"
        )

    def test_does_not_exist(self) -> None:
        assert (
            resolve_item_in_memory(assignment="$var4.name$", memory=self.memory)
            is None
        )

    def test_argument_resolution(self) -> None:
        assert resolve_in_memory(
            arguments={
                "query": "$query$",
                "age": "$user.age$",
                "location": "$var2.location.name$",
                "date": "2024-2-20",
            },
            memory=self.memory,
        ) == {
            "query": "London",
            "age": 32,
            "location": "Whitechapel",
            "date": "2024-2-20",
        }
