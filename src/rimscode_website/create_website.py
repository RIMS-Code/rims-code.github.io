# Workflow for creating the RIMS scheme part of the website

import shutil

from rimscode_website import SCHEMES_PATH
from rimscode_website.elements_md import ElementMD
from rimscode_website.mkdocs_handler import navigation
from rimscode_website.periodic_table_md import PeriodicTableMD


def website_recreate():
    """Create the RIMS scheme part of the website."""
    print("Full website rebuild started... please hold on!")
    shutil.rmtree(SCHEMES_PATH, ignore_errors=True)  # remove all existing schemes
    website_add_new()


def website_add_new():
    """Add new RIMS schemes to the website."""
    print("Adding new RIMS schemes to the website...")
    element_writer = ElementMD()
    element_writer.write_elements_md()

    scheme_writer = PeriodicTableMD(
        element_writer.ele_index_urls, element_writer.laser_type_dict
    )
    scheme_writer.write_scheme_md()

    navigation(element_writer.all_schemes)

    print("New RIMS schemes added to the website. Enjoy!")


if __name__ == "__main__":
    website_add_new()
