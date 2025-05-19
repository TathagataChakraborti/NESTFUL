from nestful.schemas.complexfuncbench import ComplexFuncBench, Conversation
from pathlib import Path

import json


class TestReader:
    def setup_method(self) -> None:
        path_to_file = Path(__file__).parent.resolve()

        relative_path_to_data = (
            "../../data_v1/complexfuncbench/ComplexFuncBench.jsonl"
        )

        abs_path = Path.joinpath(path_to_file, relative_path_to_data).resolve()

        with open(abs_path) as f:
            data = [json.loads(line) for line in f]

        self.dataset = ComplexFuncBench(
            data=[Conversation.model_validate(item) for item in data]
        )

    def test_read_samples(self) -> None:
        assert len(self.dataset.data) == 1000

    def test_transform_catalog(self) -> None:
        sequence_data, catalog = self.dataset.convert_to_nestful()

        assert len(catalog.apis) == 40
        # assert len(sequence_data.data) == 1000
