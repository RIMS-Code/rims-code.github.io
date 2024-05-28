# Create all pages for elements available in the database

from collections import OrderedDict
from pathlib import Path
import pytablewriter as ptw

from rimscode_website import DB_PATH, SCHEMES_PATH
from rimscode_website.db_reader import DataFileReader
from rimscode_website.element import Element
from rimscode_website.scheme_md import SchemeContentMD
from rimscode_website.utils import ip_reference_md, parse_db_filename


class ElementMD:
    """Class to handle the creation of the element markdown pages."""

    def __init__(self):
        """Initialize the class."""
        self.db_dict = None

        self._all_schemes = {}  # dictionary with all scheme: {ele: [ele-1, ele-2, ...]}
        self._ele_index_urls = {}  # dictionary with element name: url for adding to periodic table
        self._laser_type_dict = {}  # dictionary with element name: laser type

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
    def laser_type_dict(self) -> dict:
        """Return a dictionary with the laser type per element.

        Example dictionary that could be returned:
        {"Fe": "both", "Mo": "ti_sa", "U": "dye"}

        :return: Dictionary with element name as key and set of laser types as value.
        """
        ret_dict = {}
        for ele in self._laser_type_dict.keys():
            types = self._laser_type_dict[ele]
            if "Ti:Sa and Dye" in types or len(types) > 1:
                tp = "both"
            else:
                if "Ti:Sa" in types:
                    tp = "ti_sa"
                else:
                    tp = "dye"
            ret_dict[ele] = tp
        return ret_dict

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

        db_dict = OrderedDict()

        for f in db_files_in:
            # parse the file name
            db_file = DataFileReader(f)
            ele_pos = parse_db_filename(f)
            tmp_dict = {
                f: {
                    "position": ele_pos[1],
                    "lasers": db_file.lasers,
                    "references": db_file.main_reference_md_link,
                    "submitted_by": db_file.submitted_by,
                }
            }
            if ele_pos[0] not in db_dict.keys():
                db_dict[ele_pos[0]] = [tmp_dict]
            else:
                db_dict[ele_pos[0]].append(tmp_dict)

        self.db_dict = db_dict

    def _create_ele_folders(self):
        """Create empty folders for each element in the database.

        :param eles: List of elements in the database. Can contain duplicates.
        """
        eles = list(self.db_dict.keys())
        for ele in set(eles):
            folder = Path(self._scheme_docs_path.joinpath(ele))
            folder.mkdir(exist_ok=True, parents=True)

    def _create_ele_files(self) -> None:
        """Create all the markdown pages for the elements in the database."""
        db_dict = self.db_dict

        for ele, entry_ele_dict in db_dict.items():
            for entry_ele_dict_it in entry_ele_dict:
                for fl, entry_fl_dict in entry_ele_dict_it.items():
                    pos = entry_fl_dict["position"]
                    folder = Path(self._scheme_docs_path.joinpath(ele))

                    # scheme files
                    fname = folder.joinpath(
                        f"{ele}-{pos:0{self._file_name_zero_filling}d}.md"
                    )
                    if fname.exists() is False:  # scheme does not exist yet!
                        # scheme content creator
                        content_creator = SchemeContentMD(fl)
                        ele_file_content = content_creator.content_md

                        with open(fname, "w") as f:
                            f.write(ele_file_content)

                    # add element and scheme to the all_schemes dictionary
                    dict_entry = f"{ele}/{fname.stem}"
                    if ele not in self._all_schemes.keys():
                        self._all_schemes[ele] = [dict_entry]
                    else:
                        self._all_schemes[ele].append(dict_entry)

        # index file
        for ele in db_dict.keys():
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
        db_dict = self.db_dict[ele]

        element = Element(ele)

        ret = f"# Schemes for {element.name}\n\n"

        # add some element information:
        ret += "## Element information\n\n"
        ret += f"- **Symbol:** {element.symbol}\n"
        ret += f"- **Series:** {element.type}\n"
        ret += f"- **Atomic number:** {element.atomic_number}\n"
        ret += f"- **Atomic weight:** {element.atomic_weight: .3f~P}\n"
        ret += f"- **Ionization potential:** {element.ionization_potential.magnitude: .3f} cm⁻¹ {ip_reference_md(element.symbol)}\n"
        if element.melting_point is not None:
            ret += f"- **Melting point:** {element.melting_point: .1f~P}\n"
        if element.boiling_point is not None:
            ret += f"- **Boiling point:** {element.boiling_point: .1f~P}\n"
        ret += f"- [**Wikipedia**](https://en.wikipedia.org/wiki/{element.name})\n\n"

        # add the schemes

        # create a bullet point list of links to the schemes
        table_header = ["Scheme link", "Lasers", "Reference(s)", "Submitted by"]
        table = []
        for db_dict_it in db_dict:
            for fl, entry in db_dict_it.items():
                # URL for each scheme
                pos = entry["position"]
                url = f"../{ele}/{ele}-{pos:0{self._file_name_zero_filling}d}.md"

                table.append(
                    [
                        f"[{ele.capitalize()} {pos}]({url})",
                        entry["lasers"],
                        entry["references"],
                        entry["submitted_by"],
                    ]
                )

                # add laser type to the laser type dictionary
                if ele in self._laser_type_dict.keys():
                    self._laser_type_dict[ele].add(entry["lasers"])
                else:
                    self._laser_type_dict[ele] = {entry["lasers"]}

        table = sorted(table, key=lambda x: x[0].split("]")[1])

        md_table = ptw.MarkdownTableWriter(
            headers=table_header, value_matrix=table, margin=1
        )
        for col in range(len(table_header)):
            md_table.set_style(col, ptw.style.Style(align="left"))  # left aligned

        ret += "##Available Schemes\n\n"
        ret += str(md_table)

        return ret


if __name__ == "__main__":
    writer = ElementMD()
    writer.write_elements_md()
