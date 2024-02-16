# Utility functions, used across the site
import warnings
from pathlib import Path
from typing import Union, Tuple

from rimscode_website.constants import ELEMENTS_BY_NAME


def parse_db_filename(fname: Path) -> Union[Tuple[str, int], None]:
    """Parse the filename and return the element name and the position.

    :param fname: Path to the file to parse.

    :return: Tuple with element name (all lowercase) and position or
        None if the file name is invalid.
    """
    try:
        ele, pos = fname.stem.split("-")
        pos = int(pos)
    except ValueError:  # file name cannot be unpacked
        warnings.warn(
            f"Invalid database file name {fname.stem}.", UserWarning, stacklevel=2
        )
        return None

    # check if element name is valid
    valid_elements = set(k.casefold() for k in ELEMENTS_BY_NAME.keys())
    if ele.casefold() not in valid_elements:
        warnings.warn(
            f"Invalid element name in database file {fname.stem}.",
            UserWarning,
            stacklevel=2,
        )
        return None

    return ele.lower(), pos
