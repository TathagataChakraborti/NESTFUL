from faker import Faker


class TestFaker:
    def setup_method(self) -> None:
        self.faker = Faker()

    def test_basic(self) -> None:
        forbidden_methods = [
            "add_provider",
            "seed",
            "binary",
            "get_providers",
            "cache_pattern",
            "set_arguments",
            "del_arguments",
            "xml",
            "enum",
            "factories",
            "format",
            "generator_attrs",
            "get_arguments",
            "set_formatter",
            "get_formatter",
            "image",
            "parse",
            "provider",
            "seed_locale",
        ]

        faker_methods = [
            getattr(self.faker, item)
            for item in dir(self.faker)
            if not item.startswith("_") and item not in forbidden_methods
        ]
        callable_faker_methods = [
            item for item in faker_methods if callable(item)
        ]

        for index, func in enumerate(callable_faker_methods):
            tmp = f"{func.__name__}: {func()}"
            print(f"\n--------------------\n{tmp}\n----------------------")
