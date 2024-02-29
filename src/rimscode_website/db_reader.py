"""Database reader for the json database file."""

import json
from pathlib import Path


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
    def references(self) -> list[str]:
        """Return the references for the scheme."""
        return self._data["references"]

    @property
    def references_md_link_list(self) -> str:
        """Return a markdown formatted link list of the references."""
        ref_list = ", ".join(f"[{it}](https://doi.org/{it})" for it in self.references)
        return ref_list
