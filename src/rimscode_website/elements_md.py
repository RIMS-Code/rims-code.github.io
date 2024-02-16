# Create all pages for elements available in the database

from pathlib import Path

from rimscode_website import DB_PATH, SCHEMES_PATH
from rimscode_website.scheme_md import SchemeContentMD
from rimscode_website.utils import parse_db_filename


class ElementMD:
    """Class to handle the creation of the element markdown pages."""

    def __init__(self):
        """Initialize the class."""
        self.db_dict = None

        self._all_schemes = {}  # dictionary with all scheme: {ele: [ele-1, ele-2, ...]}
        self._ele_index_urls = {}  # dictionary with element name: url for adding to periodic table

        # create scheme docs path
        self._scheme_docs_path = SCHEMES_PATH

        # formatting decisions
        self._file_name_zero_filling = 3  # all files are named ele-00X.md

        self._create_db_dict()

    @property
    def all_schemes(self) -> dict:
        """Return a dictionary with the all schemes per element.

        Example dictionary that could be returned:
        {"he": ["he-1", "he-2"], "as": ["as-1", "as-2", "as-3"]}

        :return: Dictionary with element name as key and list of schemes as value.
        """
        return self._all_schemes

    @property
    def ele_index_urls(self) -> dict:
        """Return a dictionary with the element index urls.

        While the URL is not complicated compared to the element, the important
        function of this dictionary is to keep track of which elements exist.
        URLs are simply pointing at the folder. Example return dictionary:
        {"he": "he/", "as": "as/"}

        :return: Dictionary with element name as key and url as value. See example.
        """
        return self._ele_index_urls

    def write_elements_md(self):
        """Create all pages for elements in the database."""
        self._create_ele_folders()
        self._create_ele_files()

    def _create_db_dict(self):
        """Create a dictionary with the database information.

        Keys for the dictionary are:
            "files" -> Path to the json file.
            "elements" -> Element name.
            "positions" -> Position of the element in the list of elements.
        """
        db_files_in = DB_PATH.glob("*.json")

        db_dict = {"files": [], "elements": [], "positions": []}
        for f in db_files_in:
            # parse the file name
            ele_pos = parse_db_filename(f)
            if ele_pos is not None:
                db_dict["files"].append(f)
                db_dict["elements"].append(ele_pos[0])
                db_dict["positions"].append(ele_pos[1])

        self.db_dict = db_dict

    def _create_ele_folders(self):
        """Create empty folders for each element in the database.

        :param eles: List of elements in the database. Can contain duplicates.
        """
        eles = self.db_dict["elements"]
        for ele in set(eles):
            folder = Path(self._scheme_docs_path.joinpath(ele))
            folder.mkdir(exist_ok=True, parents=True)

    def _create_ele_files(self) -> None:
        """Create all the markdown pages for the elements in the database."""
        db_dict = self.db_dict

        for fl, ele, pos in zip(
            db_dict["files"], db_dict["elements"], db_dict["positions"]
        ):
            folder = Path(self._scheme_docs_path.joinpath(ele))

            # scheme content creator
            content_creator = SchemeContentMD(fl)
            ele_file_content = content_creator.content_md

            # scheme files
            fname = folder.joinpath(f"{ele}-{pos:0{self._file_name_zero_filling}d}.md")
            with open(fname, "w") as f:
                f.write(ele_file_content)

            # add element and scheme to the all_schemes dictionary
            dict_entry = f"{ele}/{fname.stem}"
            if ele not in self._all_schemes.keys():
                self._all_schemes[ele] = [dict_entry]
            else:
                self._all_schemes[ele].append(dict_entry)

        # index file
        for ele in set(db_dict["elements"]):
            folder = Path(self._scheme_docs_path.joinpath(ele))
            fname = folder.joinpath("index.md")
            with open(fname, "w") as f:
                f.write(self._create_ele_index_content(ele))

            # add url to self to the url dictionary
            self._ele_index_urls[ele] = f"{self._scheme_docs_path.stem}/{ele}/"

    def _create_ele_index_content(self, ele) -> str:
        """Create the index file for all the elements in the database.

        :param ele: Element name (all lowercase).

        :return: String with the content of the index markdown file.
        """
        # todo: table or something to give additional scheme information - later!
        db_dict = self.db_dict

        ret = f"# Schemes for {ele.capitalize()}\n\n"

        # get sorted positions list for this element from dictionary
        positions = sorted(
            [
                pos
                for pos, e in zip(db_dict["positions"], db_dict["elements"])
                if e == ele
            ]
        )

        # create a relative URL for each file
        urls = [
            f"../{ele}/{ele}-{pos:0{self._file_name_zero_filling}d}.md"
            for pos in positions
        ]

        # create a bullet point list of links to the schemes
        ret += "\n".join(
            [
                f"* [{ele.capitalize()} scheme {pos}]({url})"
                for pos, url in zip(positions, urls)
            ]
        )

        return ret


if __name__ == "__main__":
    writer = ElementMD()
    writer.write_elements_md()
