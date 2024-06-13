"""This module manages references and returns printable strings for references."""

import json
import requests

from habanero import Crossref

from rimscode_website.data import REFERENCE_FILE


class ReferenceDOI:
    """Class to handle references.

    If the ID is a doi, the class will first check the `data/references.json`
    file if the DOI is already present and if so, populate itself from there.
    If not, it will use `crossref` to fetch the reference information and
    save it to file, then populate itself.

    For non-DOI references, the link will be stiched together directly from the
    user entry.
    """

    def __init__(self, ref_id: dict):
        """Initialize the class.

        :param ref_id: The DOI of the reference.
        """
        self.ref_id = ref_id
        self._is_doi = False

        if ref_id.get("author", "") == "" and ref_id.get("year", 0) == 0:  # it's a DOI
            self._json_entry = None
            self._is_doi = True
            self._fetch_from_file()

            if self._json_entry is None:
                self._fetch_from_crossref()
        else:
            self._json_entry = ref_id

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
        return f'[{self.ref_p}]({self.url}){{target="_blank"}}'

    @property
    def md_url_t(self) -> str:
        """Return a markdown URL with doi as URL in in-text format."""
        return f'[{self.ref_t}]({self.url}){{target="_blank"}}'

    @property
    def url(self) -> str:
        """Return the URL of the reference."""
        if self._is_doi:
            url = f"https://doi.org/{self.ref_id['id']}"
        else:
            url = self.ref_id["id"]
        return url

    def _fetch_from_file(self):
        """Fetch the reference information from the file, if available."""
        with open(REFERENCE_FILE, "r") as file:
            references = json.load(file)
            self._json_entry = references.get(self.ref_id["id"], None)

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
            entry = cr.works(ids=self.ref_id["id"])
        except requests.HTTPError as err:
            raise IndexError(
                f"DOI {self.ref_id["id"]} not found in cross-ref. "
                f"If the DOI is correct, "
                f"try adding it manually to `data/references.json`."
            ) from err

        try:
            author_list = entry["message"]["author"]
        except KeyError as err:
            raise KeyError(
                f"DOI {self.ref_id["id"]} does not have author information. "
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
            raise KeyError(
                f"DOI {self.ref_id["id"]} does not have year information. "
            ) from err

        self._json_entry = {
            "author": author_str,
            "year": year,
        }

        with open(REFERENCE_FILE, "r") as file:
            references = json.load(file)
            references[self.ref_id["id"]] = self._json_entry

        with open(REFERENCE_FILE, "w") as file:
            json.dump(references, file, indent=4)
