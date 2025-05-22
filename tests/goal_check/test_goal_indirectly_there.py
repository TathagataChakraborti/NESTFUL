from nestful.data_handlers import get_nestful_data_instance
from nestful import SequencingData
from tests.utils import load_data

import pytest


class TestGoalIndirectlyThere:
    def setup_method(self) -> None:
        data = load_data("test_step_by_step_no_memory.json")

        self.test_sequence = SequencingData.model_validate(data[0])
        self.ground_truth_sequence, self.catalog = get_nestful_data_instance(
            executable=True, index=0
        )

    def test_with_no_memory(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog, ground_truth=self.ground_truth_sequence
            )
            is False
        )

    def test_with_fake_memory(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                fill_in_memory=True,
            )
            is True
        )

    def test_with_actual_memory(self) -> None:
        memory = {
            "var3": {"foo": "bar"},
            "var6": "bar",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is True
        )

    def test_with_actual_memory_empty(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory={},
            )
            is False
        )

    def test_with_actual_memory_empty_key_1(self) -> None:
        memory = {
            "var3": {},
            "var6": "bar",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is False
        )

    def test_with_actual_memory_empty_key_2(self) -> None:
        memory = {
            "var3": None,
            "var6": "bar",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is False
        )

    def test_with_actual_memory_wrong_key(self) -> None:
        memory = {
            "var3": {"foo": "bar"},
            "var5": "bar",
        }

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
            )
            is False
        )

    def test_retrieved_memory_fill_it_in(self) -> None:
        memory = self.test_sequence.get_memory(
            self.catalog, fill_in_memory=True
        )

        assert set(memory.keys()) == {
            f"var{i}" for i in range(1, len(self.test_sequence.output))
        }

        assert memory["var1"]["entityId"]
        assert memory["var6"]["provider"]
        assert memory["var7"]["commerceInfo"]["externalUrl"]

    def test_memory_fill_in_block(self) -> None:
        memory = {
            "var3": {"foo": "bar"},
            "var5": "bar",
        }

        with pytest.raises(AssertionError):
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                memory=memory,
                fill_in_memory=True,
            )

    def test_incomplete_sequence(self) -> None:
        self.test_sequence.output = self.test_sequence.output[:4]

        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                fill_in_memory=True,
            )
            is False
        )
