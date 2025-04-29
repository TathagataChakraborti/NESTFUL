from nestful.data_handlers import get_nestful_data_instance
from nestful.utils import extract_label
from nestful.errors import induce_error_in_sequence
from nestful.schemas.errors import ErrorType
from nestful.schemas.sequences import ErrorTag


class TestErrorGeneratorSequence:
    def setup_method(self) -> None:
        self.sequence, self.catalog = get_nestful_data_instance(
            index=0, executable=True
        )

    def test_missing_call(self) -> None:
        error_sequence = induce_error_in_sequence(
            self.sequence,
            catalog=self.catalog,
            memory={},
            error_type=ErrorType.MISSING_CALL,
            referred_only=True,
        )

        assert len(self.sequence.output) == len(error_sequence.output) + 1
        assert len(error_sequence.errors) > 0

        new_labels = [step.label for step in error_sequence.output]
        missing_step = next(
            step
            for step in self.sequence.output
            if step.label not in new_labels
        )

        assert (
            ErrorTag(error_type=ErrorType.MISSING_CALL, info=missing_step.name)
            in error_sequence.errors
        )

        who_used = self.sequence.who_used(missing_step.label or "")
        num_removals = 0

        for who in who_used:
            original_step = self.sequence.output[who]

            for step in error_sequence.output:
                if step.name == original_step.name:
                    remaining_args = set()
                    for arg, value in original_step.arguments.items():
                        l, m = extract_label(str(value))

                        if l == missing_step.label:
                            num_removals += 1
                        else:
                            remaining_args.add(arg)

                    assert remaining_args == set(step.arguments.keys())

                    for arg, value in step.arguments.items():
                        l, m = extract_label(str(value))
                        assert l != missing_step.label

        assert len(who_used) > 0
        assert num_removals > 0

    def test_repeat_call(self) -> None:
        error_sequence = induce_error_in_sequence(
            self.sequence,
            catalog=self.catalog,
            memory={},
            error_type=ErrorType.BAD_REPEAT,
        )

        assert len(self.sequence.output) == len(error_sequence.output) - 1
        assert len(error_sequence.errors) == 1

        repeat_step = None

        for step in error_sequence.output:
            if step.errors:
                assert repeat_step is None
                repeat_step = step

        assert repeat_step is not None
        assert (
            ErrorTag(error_type=ErrorType.BAD_REPEAT, info=repeat_step.name)
            in error_sequence.errors
        )
