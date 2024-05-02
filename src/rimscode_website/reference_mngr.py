"""This module manages references and returns printable strings for references."""

import json
import requests

from habanero import Crossref

from rimscode_website.data import REFERENCE_FILE


class ReferenceDOI:
    """Class to handle references with a DOI.

    This class will first check the `data/references.json` file if the DOI is already
    present and if so, populate itself from there. If not, it will use `crossref` to
    fetch the reference information and save it to file, then populate itself.
    """

    def __init__(self, doi: str):
        """Initialize the class.

        :param doi: The DOI of the reference.
        """
        self.doi = doi

        self._json_entry = None

        self._fetch_from_file()

        if self._json_entry is None:
            self._fetch_from_crossref()

    @property
    def doi_valid(self) -> bool:
        """Return whether the DOI is valid."""
        return self._doi_valid

    @property
    def ref_p(self) -> str:
        """Return the reference in the format "(Author, Year)"."""
        return f"({self._json_entry['author']}, {self._json_entry['year']})"

    @property
    def ref_t(self) -> str:
        """Return the reference in the format "Author (Year)"."""
        return f"{self._json_entry['author']} ({self._json_entry['year']})"

    @property
    def md_url_p(self) -> str:
        """Return a markdown URL with doi as URL in parentheses format."""
        return f'[{self.ref_p}](https://doi.org/{self.doi}){{target="_blank"}}'

    @property
    def md_url_t(self) -> str:
        """Return a markdown URL with doi as URL in in-text format."""
        return f'[{self.ref_t}](https://doi.org/{self.doi}){{target="_blank"}}'

    def _fetch_from_file(self):
        """Fetch the reference information from the file, if available."""
        with open(REFERENCE_FILE, "r") as file:
            references = json.load(file)
            self._json_entry = references.get(self.doi, None)

    def _fetch_from_crossref(self):
        """Fetch the reference information from crossref.

        If unsuccessful, the `_doi_valid` attribute is set to False. Otherwise,
        the reference information is saved to the file and the `_json_entry` attribute
        is updated.

        :raises IndexError: If the DOI is not found in crossref.
        :raises KeyError: If the DOI does not have author or year information.
        """
        cr = Crossref(mailto="reto@galactic-forensics.space")

        try:
            entry = cr.works(ids=self.doi)
        except requests.HTTPError as err:
            raise IndexError(
                f"DOI {self.doi} not found in cross-ref. "
                f"If the DOI is correct, "
                f"try adding it manually to `data/references.json`."
            ) from err

        try:
            author_list = entry["message"]["author"]
        except KeyError as err:
            raise KeyError(
                f"DOI {self.doi} does not have author information. "
            ) from err
        if len(author_list) > 2:
            author_str = f"{author_list[0]["family"]} et al."
        elif len(author_list) == 2:
            author_str = " and ".join([author["family"] for author in author_list])
        else:
            author_str = author_list[0]["family"]

        try:
            year = entry["message"]["published"]["date-parts"][0][0]
        except KeyError as err:
            raise KeyError(f"DOI {self.doi} does not have year information. ") from err

        self._json_entry = {
            "author": author_str,
            "year": year,
        }

        with open(REFERENCE_FILE, "r") as file:
            references = json.load(file)
            references[self.doi] = self._json_entry

        with open(REFERENCE_FILE, "w") as file:
            json.dump(references, file, indent=4)
