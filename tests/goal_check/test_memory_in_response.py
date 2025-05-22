from nestful.data_handlers import get_nestful_data_instance
from nestful import SequencingData
from tests.utils import load_data


class TestMemoryInResponse:
    def setup_method(self) -> None:
        data = load_data("test_step_by_step_with_memory.json")
        self.ground_truth_sequence, self.catalog = get_nestful_data_instance(
            executable=True, index=0
        )

        self.test_sequence = SequencingData.model_validate(data[0])

    def test_as_is(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog, ground_truth=self.ground_truth_sequence
            )
            is False
        )

    def test_memory_retrieval(self) -> None:
        memory = self.test_sequence.get_memory(self.catalog)

        assert memory["var3"] == {}
        assert memory["var5"] == {}
        assert memory["var4"]["geoId"] == 186338
        assert memory["var2"]["skyId"] == "LOND"

    def test_custom_var_result(self) -> None:
        assert (
            self.test_sequence.goal_check(
                catalog=self.catalog,
                ground_truth=self.ground_truth_sequence,
                var_result={
                    "item_1": "$var1.skyId$",
                    "item_2": "$var2.entityId$",
                    "item_3": "$var4.geoId$",
                },
            )
            is True
        )

    def test_num_successful_calls(self) -> None:
        assert self.test_sequence.num_successful_calls == 3
