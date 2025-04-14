from nestful.data_handlers import get_nestful_data_instance
from nestful.utils import extract_label
from nestful.errors.error_generator import transform_variable
from nestful.errors import induce_error_in_step
from nestful.schemas.errors import ErrorType
from nestful.schemas.sequences import ErrorTag


class TestErrorGeneratorStep:
    def setup_method(self) -> None:
        self.sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

    def test_missing_parameter(self) -> None:
        original_step = self.sequence.output[2]
        required_parameters = original_step.get_required_args(self.catalog)

        error_step, _ = induce_error_in_step(
            original_step,
            catalog=self.catalog,
            memory={},
            error_type=ErrorType.MISSING_PARAMETER,
        )

        assert error_step is not None
        remaining_parameters = error_step.get_required_args(self.catalog)

        assert len(remaining_parameters) == len(required_parameters) - 1

        error_step, _ = induce_error_in_step(
            original_step,
            catalog=self.catalog,
            memory={},
            num_errors=5,
            error_type=ErrorType.MISSING_PARAMETER,
        )

        assert error_step is not None
        remaining_parameters = error_step.get_required_args(self.catalog)

        assert len(remaining_parameters) == 0
        assert len(error_step.arguments.keys()) == 1

        error_count = 0

        for item in [
            "originSkyId",
            "destinationSkyId",
            "originEntityId",
            "destinationEntityId",
            "date",
        ]:
            error_count += 1
            assert (
                ErrorTag(error_type=ErrorType.MISSING_PARAMETER, info=item)
                in error_step.errors
            )

        assert error_count == 5
        assert error_count == len(error_step.errors)

        error_step, _ = induce_error_in_step(
            original_step,
            catalog=self.catalog,
            memory={},
            num_errors=6,
            error_type=ErrorType.MISSING_PARAMETER,
        )

        assert error_step is None

    def test_made_up_parameter(self) -> None:
        original_step = self.sequence.output[2]
        original_parameters = set(original_step.arguments.keys())

        error_step, _ = induce_error_in_step(
            original_step,
            catalog=self.catalog,
            memory={},
            error_type=ErrorType.MADE_UP_PARAMETER,
        )

        assert error_step is not None
        new_parameters = set(error_step.arguments.keys())

        assert len(new_parameters) == len(original_parameters)

        required_parameters = original_step.get_required_args(self.catalog)
        optional_parameters = original_parameters.difference(
            required_parameters
        )

        assert optional_parameters.issubset(new_parameters)

        compromised_parameters = new_parameters.difference(original_parameters)
        preserved_parameters = original_parameters.intersection(new_parameters)

        assert (
            preserved_parameters.union(
                {transform_variable(param) for param in compromised_parameters}
            )
            == original_parameters
        )

        made_up_parameter = compromised_parameters.pop()

        assert (
            ErrorTag(
                error_type=ErrorType.MADE_UP_PARAMETER, info=made_up_parameter
            )
            in error_step.errors
        )

    def test_missing_memory(self) -> None:
        memory = {
            "var1": {
                "skyId": "foo",
                "entityId": "bar",
            },
            "var2": {
                "skyId": "foo",
                "entityId": "bar",
            },
        }

        _, new_memory = induce_error_in_step(
            self.sequence.output[2],
            catalog=self.catalog,
            memory=memory,
            error_type=ErrorType.MISSING_MEMORY,
        )

        assert new_memory["var1"] == {} or new_memory["var2"] == {}

        _, new_memory = induce_error_in_step(
            self.sequence.output[1],
            catalog=self.catalog,
            memory=memory,
            error_type=ErrorType.MISSING_MEMORY,
        )

        assert new_memory == memory

        _, new_memory = induce_error_in_step(
            self.sequence.output[4],
            catalog=self.catalog,
            memory=memory,
            error_type=ErrorType.MISSING_MEMORY,
        )

        assert new_memory["var4"] == {}
        assert ErrorTag(
            error_type=ErrorType.MISSING_MEMORY, info="$var4.geoId$"
        )

    def test_made_up_assignment(self) -> None:
        original_step = self.sequence.output[2]
        num_errors = 2

        error_step, _ = induce_error_in_step(
            original_step,
            catalog=self.catalog,
            memory={},
            error_type=ErrorType.MADE_UP_ASSIGNMENT,
            num_errors=num_errors,
        )

        assert error_step is not None
        error_count = 0

        for arg, value in error_step.arguments.items():
            original_value = original_step.arguments[arg]
            if value != original_value:
                error_count += 1

                original_label, original_mapping = extract_label(original_value)
                new_label, new_mapping = extract_label(value)

                assert original_label == new_label
                assert original_mapping == transform_variable(new_mapping or "")

                assert ErrorTag(
                    error_type=ErrorType.MADE_UP_ASSIGNMENT, info=new_mapping
                )

        assert error_count == num_errors

    def test_made_up_assignment_nested(self) -> None:
        sequence, catalog = get_nestful_data_instance(index=35, executable=True)

        error_step, _ = induce_error_in_step(
            sequence.output[1],
            catalog=catalog,
            memory={},
            error_type=ErrorType.MADE_UP_ASSIGNMENT,
        )

        assert error_step is not None
        assert error_step.arguments["q"] == "$var1.location.eman$"

        assert ErrorTag(error_type=ErrorType.MADE_UP_ASSIGNMENT, info="enam")
        assert ErrorTag(
            error_type=ErrorType.MISSING_MEMORY, info="$var1.location.eman$"
        )
