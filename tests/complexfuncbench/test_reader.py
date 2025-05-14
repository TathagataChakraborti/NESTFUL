from nestful.schemas.complexfuncbench import ComplexFuncBench, Conversation

import json
import pytest


@pytest.mark.skip(reason="This is temporary")
class TestReader:
    def setup_method(self) -> None:
        file_name = "../../data_v1/complexfuncbench/ComplexFuncBench.jsonl"

        with open(file_name) as f:
            data = [json.loads(line) for line in f]

        self.dataset = ComplexFuncBench(
            data=[Conversation.model_validate(item) for item in data]
        )

    def test_read_samples(self) -> None:
        assert len(self.dataset.data) == 1000
