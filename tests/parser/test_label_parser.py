from nestful.utils import get_token, extract_label


class TestLabelParsing:
    def test_direct_assignment(self) -> None:
        string = "02-25-2024"
        label, mapping = extract_label(string)

        assert label == ""
        assert mapping is None

    def test_direct_map(self) -> None:
        string = "$data$"
        label, mapping = extract_label(string)

        assert label == get_token(index=0)
        assert mapping == "data"

    def test_keyed_map(self) -> None:
        string = "$var1.data$"
        label, mapping = extract_label(string)

        assert label == "var1"
        assert mapping == "data"

    def test_keyed_map_nested(self) -> None:
        string = "$var2.location.geoId$"
        label, mapping = extract_label(string)

        assert label == "var2"
        assert mapping == "location.geoId"

    def test_var_result_reference(self) -> None:
        string = "$var5$"
        label, mapping = extract_label(string)

        assert label == get_token(index=0)
        assert mapping == "var5"

    def test_indexed_reference(self) -> None:
        string = "$var5.authors[0]$"
        label, mapping = extract_label(string)

        assert label == "var5"
        assert mapping == "authors"
