# This script creates the markdown files for the schemes overview page.

from typing import Dict, List, Set, Tuple, Union

import numpy as np

from rimscode_website import SCHEMES_PATH
from rimscode_website.constants import (
    COLORS_BY_TYPE,
    INACCESSIBLE_ELEMENTS,
    ELEMENTS_BY_NAME,
    SPECIAL_POSITIONS,
)


class PeriodicTableMD:
    """Class to write the scheme overview page."""

    def __init__(self, urls: Dict[str, str], laser_types) -> None:
        """Initialize class.

        :param urls: Dictionary with the element name as key and the URL as value.
        :param laser_types: Dictionary with the element name as key and the laser type as value.
            Allowed laser types are: "dye", "ti_sa", "both"
        """
        self._urls = urls
        self._laser_types = laser_types

    def write_scheme_md(self) -> None:
        """Write the elements overview site with links to a Markdown table."""
        str_to_write = r"""# RIMS Schemes

Please click on an element in the periodic table below
to see the corresponding RIMS scheme.
For gray elements, no scheme is currently available in the database.
Therefore, the element is not clickable.
All other element are color-coded according to the type of laser scheme available
(see legend below).

If you would like to contribute a scheme,
please see [here](../schemes_static/submit_scheme.md).


"""

        # center both tables
        str_to_write += "\n\n<center>\n\n"
        # add table
        str_to_write += self._table()

        # add Legend
        str_to_write += "Color coding:\n\n"
        str_to_write += self._table_legend()
        str_to_write += "\n\n</center>\n"

        fname = SCHEMES_PATH.joinpath("schemes.md")
        with open(fname, "w") as f:
            # write the header of the site
            f.write(str_to_write)

    def _all_colors(self) -> Set[str]:
        """Return a set of all colors used in the periodic table."""
        return COLORS_BY_TYPE.values()

    def _elements_by_position(self) -> Dict[Tuple[int, int], List[str]]:
        """Return a dictionary of elements by position.

        Transforms the dictionary ELEMENT_BY_NAME to a dictionary by position
        - {key: (x, y, color)} to {(x, y): [key, color]}.
        """
        return_dict = {}
        for k, v in ELEMENTS_BY_NAME.items():
            # color = v[2]
            if (
                k.lower() in self._laser_types.keys()
            ):  # so we have some information about the laser type
                color = COLORS_BY_TYPE[self._laser_types[k.lower()]]
            elif k in INACCESSIBLE_ELEMENTS:
                color = COLORS_BY_TYPE["inaccessible"]
            else:
                color = COLORS_BY_TYPE["feasible"]

            # row and column
            row = int(v[0])
            col = int(v[1])

            # add spacing before lanthanides
            if row >= 7:
                row += 1

            return_dict[(row, col)] = [k, color]
        return return_dict

    def _table(self) -> str:
        """Generate an HTML table with the elements and links.

        :param urls: Dictionary with the element name as key and the URL as value.

        :return: Fully formatted HTML table.
        """
        table = r""

        # add the style sheet
        table += self._table_style()

        # write start of the body
        table += '\n\n<table class="tg">\n<tbody>'

        # number of rows and columns
        tmp = np.array(list(self._elements_by_position().keys()))
        nrows = tmp[:, 0].max() + 1
        ncols = tmp[:, 1].max() + 1

        # loop over rows
        for row in range(nrows):
            # row start tag
            table += "\n  <tr>"

            # loop over columns
            for col in range(ncols):
                # get the element tag for this row and column
                table += self._table_get_column(row, col, urls=self._urls)

            # row end tag
            table += "\n  </tr>"

        # write end of body
        table += "\n</tbody>\n</table>"

        return table

    def _table_legend(self) -> str:
        """Generate the legend for the table.

        :return: The legend for the table.
        """
        table = r""

        # add the style sheet
        table += self._table_style()

        # write start of the body
        table += '\n\n<table class="tg">\n<tbody>\n  <tr>'

        # write the legend
        for mode, color in COLORS_BY_TYPE.items():
            # color
            col_to_write = color[1:]
            # mode - translate to human readable
            if mode == "ti_sa":
                mode_to_write = "Ti:Sa schemes"
            elif mode == "dye":
                mode_to_write = "Dye schemes"
            elif mode == "both":
                mode_to_write = "Ti:Sa and Dye schemes"
            elif mode == "feasible":
                mode_to_write = "Feasible"
            else:
                mode_to_write = "Inaccessible"

            # write the legend
            table += f'    <td class="tg tg_{col_to_write}">{mode_to_write}</td>'

        # write end of body
        table += "  <tr>\n</tbody>\n</table>"

        return table

    def _table_get_column(self, row: int, col: int, urls: Dict[str, str]) -> str:
        """Return the HTML code for a column for an element at this position.

        :param row: The row of the element.
        :param col: The column of the element.
        :param urls: Dictionary with the element name as key and the URL as value.

        :return: The HTML code for the column.
        """
        # get the element tag for this row and column
        element = self._elements_by_position().get((row, col), None)

        special_tag = SPECIAL_POSITIONS.get((row, col), "")

        if element is None:
            align = ' align="center"' if special_tag != "" else ""
            return f"\n    <td{align}>{special_tag}</td>"

        # so we have an element:
        tag_name = self._table_style_tag_name(element[1])
        link = self._table_get_url(element[0])

        if link is not None:
            return f'\n    <td class="tg {tag_name}"><a href="{link}"><span style="color:#000">{element[0]}</span></a></td>'
        else:
            return f'\n    <td class="tg {tag_name}">{element[0]}</td>'

    def _table_get_url(self, element: str) -> Union[None, str]:
        """Return the URL for the element if schemes exist.

        :param element: The element name, e.g., "H" (not case-sensitive).
        :param urls: Dictionary with the element name as key and the URL as value.

        :return: The URL to the scheme if it exists, return None.
        """
        ret_url = self._urls.get(element.lower(), None)
        return "../../" + ret_url if isinstance(ret_url, str) else None

    def _table_style(self) -> str:
        """Generate a CSS style tag for the table.

        :return: The style sheet for the table.
        """
        style_out = r"""<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:transparent;border-style:solid;border-width:1px;overflow:hidden;padding:8px 8px;word-break:normal;}

"""

        for color in self._all_colors():
            style_out += self._table_style_tag(color)

        # end tag
        style_out += "\n</style>"

        return style_out

    def _table_style_tag(
        self,
        bgcolor: str,
        color: str = "#000000",
        ha: str = "center",
        va: str = "middle",
    ) -> str:
        """Generate a CSS style tag for the element color.

        :param bgcolor: The background color of the element, e.g., "#ffffc7".
            Also defines the name of the tag.
        :param color: The color of the text, e.g., "#000000".
        :param ha: Horizontal alignment of the text.
        :param va: Vertical alignment of the text.

        :return: The style tag, e.g.,
            ".tg .tg_ffffc7{background-color: #ffffc7; color: #000000; text-align: center; vertical-align: middle;}"
        """
        tg_name = self._table_style_tag_name(bgcolor)
        return f".tg .{tg_name}{{background-color: {bgcolor}; color: {color}; text-align: {ha}; vertical-align: {va};}}"

    def _table_style_tag_name(self, color: str) -> str:
        """Take a color and turn it into a tag name for the HTML table.

        Leading hash of the color is stripped.

        :param color: The color of the element, e.g., "#ffffc7".
            If None, return "tg_none".

        :return: The tag name, e.g., "tg_ffffc7"
        """
        return "tg_" + color.lstrip("#")
