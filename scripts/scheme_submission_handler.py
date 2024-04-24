"""This python file handles the submission of new schemes to the database."""

from pathlib import Path
import sys

DB_PATH = Path(__file__).parents[1].joinpath("db")


def add_to_db(json_str: str) -> None:
    """Add a given json content to the database.

    :param json_str: JSON file content, as a string.
    """
    print(json_str)

    # todo:
    # 1: convert the json to an actual dictionary
    # 2: get the element
    # 3: determine the path and see what files are already present, then generate filename
    # 4: save json file under new filename


if __name__ == "__main__":
    try:
        arg_json = sys.argv[1]
    except IndexError as e:
        raise IndexError(
            'No arguments provided. Please provide the content of the json file in "".'
        ) from e

    add_to_db(arg_json)
