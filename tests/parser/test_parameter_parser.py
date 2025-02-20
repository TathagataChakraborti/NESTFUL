from nestful.utils import parse_parameters


def test_parse_parameters() -> None:
    assert parse_parameters(signature="a(b,c)") == ("a", ["b", "c"])
    assert parse_parameters(signature="a(b, c)") == ("a", ["b", "c"])
    assert parse_parameters(signature=" a(b,c) ") == ("a", ["b", "c"])

    assert parse_parameters(signature="a(c)") == ("a", ["c"])
    assert parse_parameters(signature="a()") == ("a", [])

    assert parse_parameters(signature="agent_a(b,c)") == ("agent_a", ["b", "c"])
    assert parse_parameters(signature="3a-1(b-2,c3)") == ("3a-1", ["b-2", "c3"])

    assert parse_parameters(signature='a("b,",c)') == ("a", ['"b, "', "c"])
    assert parse_parameters(signature='a("b,", "x", c)') == (
        "a",
        ['"b, "', '"x"', "c"],
    )
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

    assert parse_parameters(
        signature='a("Pets called "Mary" in "Sydney", Australia",c)'
    ) == (
        "a",
        ['"Pets called "Mary" in "Sydney", Australia"', "c"],
    )
