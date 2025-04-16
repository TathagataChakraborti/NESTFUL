from nestful.utils import parse_parameters


class TestParseParameters:
    def test_empty(self) -> None:
        assert parse_parameters(signature="a()") == ("a", [])
        assert parse_parameters(signature="a()") == ("a", [])

    def test_basic_parse(self) -> None:
        assert parse_parameters(signature="a(c)") == ("a", ["c"])

        assert parse_parameters(signature="a(b,c)") == ("a", ["b", "c"])
        assert parse_parameters(signature="a(b, c)") == ("a", ["b", "c"])
        assert parse_parameters(signature=" a(b,c) ") == ("a", ["b", "c"])

    def test_dash_and_bar(self) -> None:
        assert parse_parameters(signature="agent_a(b,c)") == (
            "agent_a",
            ["b", "c"],
        )
        assert parse_parameters(signature="3a-1(b-2,c3)") == (
            "3a-1",
            ["b-2", "c3"],
        )

    def test_comma(self) -> None:
        assert parse_parameters(signature='a("b,",c)') == ("a", ['"b, "', "c"])
        assert parse_parameters(signature='a("b,", "x", c)') == (
            "a",
            ['"b, "', '"x"', "c"],
        )

    def test_comma_with_assignment(self) -> None:
        assert parse_parameters(
            signature=(
                'LocalBusinessDataBusinessReviews(business_id="$var1.business_id$",'
                ' limit="20", offset="0", query="Bars in Manhattan, USA",'
                ' sortBy="most_relevant", region="us", language="en")'
            )
        ) == (
            "LocalBusinessDataBusinessReviews",
            [
                'business_id="$var1.business_id$"',
                'limit="20"',
                'offset="0"',
                'query="Bars in Manhattan, USA"',
                'sortBy="most_relevant"',
                'region="us"',
                'language="en"',
            ],
        )

    def test_comma_and_quote(self) -> None:
        assert parse_parameters(signature='a(a, "b,","x",c)') == (
            "a",
            ["a", '"b, "', '"x"', "c"],
        )

        assert parse_parameters(signature='a("b,x,c",c)') == (
            "a",
            ['"b, x, c"', "c"],
        )
        assert parse_parameters(signature='a(a, "b,x,c", "c,y",z)') == (
            "a",
            ["a", '"b, x, c"', '"c, y"', "z"],
        )

    def test_rogue_merge(self) -> None:
        assert parse_parameters(
            signature='a("Pets called "Mary" in "Sydney", Australia",c)'
        ) == (
            "a",
            ['"Pets called "Mary" in "Sydney", Australia"', "c"],
        )

    def test_rogue_merge_with_assignment(self) -> None:
        assert parse_parameters(
            signature='a("Pets called "Mary" in "Sydney", Australia",c)'
        ) == (
            "a",
            ['"Pets called "Mary" in "Sydney", Australia"', "c"],
        )
