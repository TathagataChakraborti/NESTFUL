from typing import Any, Optional
from pathlib import Path
from os import listdir
from os.path import isfile, join

import json


def load_data(file_name: str) -> Any:
    path_to_file = Path(__file__).parent.resolve()
    relative_path_to_data = "./cached_data"

    abs_path_to_data = Path.joinpath(
        path_to_file, relative_path_to_data
    ).resolve()

    data_file: Optional[str] = next(
        (
            item
            for item in listdir(abs_path_to_data)
            if isfile(join(abs_path_to_data, item)) and file_name in item
        ),
        None,
    )

    assert data_file, f"File {file_name} not found!"

    if data_file.endswith(".json"):
        with open(join(abs_path_to_data, data_file), "r") as file:
            try:
                json_object = json.loads(file.read())
                return json_object

            except json.JSONDecodeError as e:
                print(e)
                return []

    elif data_file.endswith(".jsonl"):
        list_of_jsons = []
        with open(join(abs_path_to_data, data_file), "r") as file:
            for line in file:
                try:
                    json_object = json.loads(line)
                    list_of_jsons.append(json_object)

                except json.JSONDecodeError as e:
                    print(e)
                    return []

        return list_of_jsons
    else:
        raise ValueError(f"Unknown file extension for {data_file}!")
