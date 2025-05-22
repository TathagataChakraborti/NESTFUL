from nestful.hypothesis_generator.faker_generator import FakerGenerator


class TestFaker:
    def setup_method(self) -> None:
        self.faker = FakerGenerator()

    def test_basic(self) -> None:
        for index, func in enumerate(self.faker.methods):
            tmp = f"{func.__name__}: {func()}"
            print(f"\n--------------------\n{tmp}\n----------------------")

    def test_match(self) -> None:
        func = self.faker.get_closest_method(name="surname")

        assert func is not None
        assert func.__name__ == "last_name"
        print(func())
