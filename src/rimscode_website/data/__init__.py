"""Initialize the CERN RILIS element file and other data.

Note: Updated the element file with all element names up to Oganesson (2024-02-29)
"""

import json
from pathlib import Path

REFERENCE_FILE = Path(__file__).parent.joinpath("references.json")


def read_rilis_elements() -> dict:
    """Read the CERN RILIS element file.

    :return: Dictionary with element data. Keys are element symbols now!
    """
    fname = Path(__file__).parent.joinpath("rilis_elements.json")
    with open(fname, "r") as f:
        data = json.load(f)

    element_dict = {}
    for key, val in data.items():
        if int(key) >= 1:
            element_dict[val["Abbreviation"]] = val

    return element_dict
