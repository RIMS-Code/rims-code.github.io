"""Database reader for the json database file."""

import json
from pathlib import Path
from typing import List

from rimscode_website.reference_mngr import ReferenceDOI


class DataFileReader:
    """Read the database file and server properties to return.

    :param db_file: Path to the database file.
    """

    def __init__(self, db_file: Path) -> None:
        """Initialize the DataFileReader class.

        :param db_file: Path to the database file.
        """
        with open(db_file, "r") as f:
            self._data = json.load(f)

    @property
    def lasers(self):
        """Return the types of lasers used in the experiment."""
        return self._data["rims_scheme"]["scheme"]["lasers"]

    @property
    def dois(self) -> List[str]:
        """Return the DOIs of all references."""
        try:
            return self._data["references"]
        except KeyError:
            return []

    @property
    def main_reference_md_link(self) -> str:
        """Return the markdown link to the main reference."""
        dois = self.dois
        if len(dois) == 0:
            return ""
        else:
            return ReferenceDOI(dois[0]).md_url_t
