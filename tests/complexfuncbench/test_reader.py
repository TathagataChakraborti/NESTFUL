from nestful.schemas.complexfuncbench import ComplexFuncBench, Conversation
from nestful.data_handlers import DataType
from pathlib import Path

import json
import pytest


class TestReader:
    def setup_method(self) -> None:
        self.path_to_file = Path(__file__).parent.resolve()

        self.name = "complexfuncbench"
        self.relative_path_to_data = f"../../data_v1/{self.name}/"

        abs_path = Path.joinpath(
            self.path_to_file,
            f"{self.relative_path_to_data}/ComplexFuncBench.jsonl",
        ).resolve()

        with open(abs_path) as f:
            data = [json.loads(line) for line in f]

        self.dataset = ComplexFuncBench(
            data=[Conversation.model_validate(item) for item in data]
        )

    def test_read_samples(self) -> None:
        assert len(self.dataset.data) == 1000

    @pytest.mark.skip(reason="We only need to do this once.")
    def test_transform_catalog(self) -> None:
        sequence_data, catalog = self.dataset.convert_to_nestful()

        assert len(catalog.apis) == 40
        assert len(sequence_data.data) == 1000

        abs_path = Path.joinpath(
            self.path_to_file,
            f"{self.relative_path_to_data}/{self.name}-{DataType.SPEC}.json",
        ).resolve()

        with open(abs_path, "w") as f:
            json.dump([api.dict() for api in catalog.apis], f)

        abs_path = Path.joinpath(
            self.path_to_file,
            f"{self.relative_path_to_data}/{self.name}-{DataType.DATA}.json",
        ).resolve()

        with open(abs_path, "w") as f:
            json.dump([sample.dict() for sample in sequence_data.data], f)
