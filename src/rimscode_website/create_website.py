# Workflow for creating the RIMS scheme part of the website

import shutil

from rimscode_website import SCHEMES_PATH
from rimscode_website.elements_md import ElementMD
from rimscode_website.mkdocs_handler import navigation
from rimscode_website.periodic_table_md import PeriodicTableMD


def website():
    """Create the RIMS scheme part of the website."""
    shutil.rmtree(SCHEMES_PATH, ignore_errors=True)  # remove all existing schemes

    element_writer = ElementMD()
    element_writer.write_elements_md()

    scheme_writer = PeriodicTableMD(element_writer.ele_index_urls)
    scheme_writer.write_scheme_md()

    navigation(element_writer.all_schemes)

    print("RIMS scheme part of the website created. Enjoy!")


if __name__ == "__main__":
    website()
