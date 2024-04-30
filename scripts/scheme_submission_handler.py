"""This python file handles the submission of new schemes to the database."""

import json
from pathlib import Path
import sys

DB_PATH = Path(__file__).parents[1].joinpath("db")


def add_to_db(json_str: str) -> str:
    """Add a given json content to the database.

    :param json_str: JSON file content, as a string.

    :return: Name of the created file.
    """
    json_str = json.loads(json_str)
    element = json_str["rims_scheme"]["scheme"]["element"].lower()

    # create the file name
    it = 1
    while True:
        fname = DB_PATH.joinpath(f"{element}-{str(it).zfill(3)}.json")
        if not fname.exists():
            break
        it += 1

    with open(fname, "w") as f:
        json.dump(json_str, f, indent=4)

    return str(fname.name)


# Main function called when the script is run with the json string as an argument

if __name__ == "__main__":
    try:
        arg_json = sys.argv[1]
    except IndexError as e:
        raise IndexError(
            'No arguments provided. Please provide the content of the json file in "".'
        ) from e

    retval = add_to_db(arg_json)
    print(retval)


# SOME MANUAL TESTS FOR THE FUNCTION ABOVE #


def test_manual():
    """Add a new element to the database."""
    json_str = '{"rims_scheme": {"scheme": {"element": "U", "ion": 1}}}'
    add_to_db(json_str)
