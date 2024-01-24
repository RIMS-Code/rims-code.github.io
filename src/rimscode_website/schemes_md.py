# This script creates the markdown files for the schemes overview page.

from typing import Dict, List, Set, Tuple, Union

import numpy as np

from rimscode_website import DOCS_PATH
from rimscode_website.utils import ELEMENTS_BY_NAME, SPECIAL_POSITIONS

# fixme: implement all these functions as a class and clean it up... too much passing around of variables


def write_scheme_md(urls: Dict[str, str]) -> None:
    """Write the elements overview site with links to a Markdown table.

    :param urls: Dictionary with the element name as key and the URL as value.
    """
    str_to_write = r"""# RIMS Schemes

Please click on an element in the periodic table below
to see the corresponding RIMS scheme.
If an element is not linked,
no scheme is currently available.

If you would like to contribute a scheme,
please see [here](../contribute).


"""

    # add table
    str_to_write += _table(urls)

    fname = DOCS_PATH.joinpath("schemes.md")
    with open(fname, "w") as f:
        # write the header of the site
        f.write(str_to_write)


def _all_colors() -> Set[str]:
    """Return a set of all colors used in the periodic table."""
    return {v[2] for v in ELEMENTS_BY_NAME.values()}


def _elements_by_position() -> Dict[Tuple[int, int], List[str]]:
    """Return a dictionary of elements by position.

    Transforms the dictionary ELEMENT_BY_NAME to a dictionary by position
    - {key: (x, y, color)} to {(x, y): [key, color]}.
    """
    return {(int(v[0]), int(v[1])): [k, v[2]] for k, v in ELEMENTS_BY_NAME.items()}


def _table(urls: Dict[str, str]) -> str:
    """Generate a HTML table with the elements and links.

    :param urls: Dictionary with the element name as key and the URL as value.

    :return: Fully formatted HTML table.
    """
    table = r""

    # add the style sheet
    table += _table_style()

    # write start of the body
    table += '\n\n<table class="tg">\n<tbody>'

    # number of rows and columns
    tmp = np.array(list(_elements_by_position().keys()))
    nrows = tmp[:, 0].max() + 1
    ncols = tmp[:, 1].max() + 1

    # loop over rows
    for row in range(nrows):
        # row start tag
        table += "\n  <tr>"

        # loop over columns
        for col in range(ncols):
            # get the element tag for this row and column
            table += _table_get_column(row, col, urls=urls)

        # row end tag
        table += "\n  </tr>"

    # write end of body
    table += "\n</tbody>\n</table>"

    return table


def _table_get_column(row: int, col: int, urls: Dict[str, str]) -> str:
    """Return the HTML code for a column for an element at this position.

    :param row: The row of the element.
    :param col: The column of the element.
    :param urls: Dictionary with the element name as key and the URL as value.

    :return: The HTML code for the column.
    """
    # get the element tag for this row and column
    element = _elements_by_position().get((row, col), None)

    special_tag = SPECIAL_POSITIONS.get((row, col), "")

    if element is None:
        align = ' align="center"' if special_tag != "" else ""
        return f"\n    <td{align}>{special_tag}</td>"

    # so we have an element:
    tag_name = _table_style_tag_name(element[1])
    link = _table_get_url(element[0], urls=urls)

    if link is not None:
        return f'\n    <td class="tg {tag_name}"><a href="{link}">{element[0]}</a></td>'
    else:
        return f'\n    <td class="tg {tag_name}">{element[0]}</td>'


def _table_get_url(element: str, urls: Dict[str, str]) -> Union[None, str]:
    """Return the URL for the element if schemes exist.

    :param element: The element name, e.g., "H" (not case-sensitive).
    :param urls: Dictionary with the element name as key and the URL as value.

    :return: The URL to the scheme if it exists, return None.
    """
    ret_url = urls.get(element.lower(), None)
    return "../" + ret_url if isinstance(ret_url, str) else None


def _table_style() -> str:
    """Generate a CSS style tag for the table.

    :return: The style sheet for the table.
    """
    style_out = r"""<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:transparent;border-style:solid;border-width:1px;overflow:hidden;padding:8px 8px;word-break:normal;}

"""

    for color in _all_colors():
        style_out += _table_style_tag(color)

    # end tag
    style_out += "\n</style>"

    return style_out


def _table_style_tag(
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
    tg_name = _table_style_tag_name(bgcolor)
    return f".tg .{tg_name}{{background-color: {bgcolor}; color: {color}; text-align: {ha}; vertical-align: {va};}}"


def _table_style_tag_name(color: str) -> str:
    """Take a color and turn it into a tag name for the HTML table.

    Leading hash of the color is stripped.

    :param color: The color of the element, e.g., "#ffffc7".
        If None, return "tg_none".

    :return: The tag name, e.g., "tg_ffffc7"
    """
    return "tg_" + color.lstrip("#")


if __name__ == "__main__":
    write_scheme_md()
