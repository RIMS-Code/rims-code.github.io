"""Class to create the content of a individual scheme page from the data file."""

import json
from pathlib import Path

import pytablewriter as ptw
import rimsschemedrawer

from rimscode_website import SCHEMES_PATH
from rimscode_website.utils import parse_db_filename


class SchemeContentMD:
    """Create the content of a individual scheme page from the data file."""

    def __init__(self, db_file: Path) -> None:
        """Initialize the class.

        :param db_file: Path to the database file.
        """
        self.db_file = db_file

        # parse element and position
        ele, pos = parse_db_filename(db_file)
        self.ele = ele

        # figure path, filenames, and formats
        self.ele_path = SCHEMES_PATH.joinpath(self.ele)  # links relative to this!
        self.fig_path = self.ele_path.joinpath(self.db_file.stem)
        self.fig_path.mkdir(exist_ok=True, parents=True)
        self.fig_name_dark = self.fig_path.joinpath(f"{self.db_file.stem}-dark")
        self.fig_name_light = self.fig_path.joinpath(f"{self.db_file.stem}-light")
        self.fig_formats = ["pdf", "png", "svg"]

        # read the database file
        with open(db_file, "r") as fp:
            self.db_content = json.load(fp)
        self.rims_scheme_data = self.db_content["rims_scheme"]

        # get the rimsschemedrawer config parser ready
        self.scheme_config = rimsschemedrawer.ConfigParser(self.rims_scheme_data)

        # Set title of page
        self._content_md = f"# {ele.capitalize()} scheme {pos}"

        # Add the notes section
        self._notes()

        # Add the scheme section
        self._scheme()

        # Add the references section
        self._reference()

    @property
    def content_md(self) -> str:
        """Return the content string for the markdown file.

        :return: String with the content of the markdown file.
        """
        return self._content_md

    def _notes(self):
        """Add notes if available."""
        key = "notes"
        if key in self.db_content.keys():
            self._content_md += "\n\n## Notes\n\n"
            self._content_md += self.db_content[key] + "\n\n"

    def _reference(self):
        """Add reference if available.

        If multiple references are given, they are all added.
        """
        key = "references"
        if key in self.db_content.keys():
            self._content_md += "\n\n## Reference\n\n"

            dois = self.db_content[key]
            for doi in dois:
                self._content_md += f"[DOI: {doi}](https://doi.org/{doi})\n\n"

    def _scheme(self):
        """Add the scheme table to the content.

        This is a mandatory section, so no checks are done if section available.
        """
        self._content_md += "\n\n## Scheme\n\n"

        # label scheme IP:
        self._content_md += (
            f"**Ionization Potential**: {self.scheme_config.ip_level:.3f} cm⁻¹\n\n"
        )

        # create the scheme table
        header, table = self.scheme_config.scheme_table()
        md_table = ptw.MarkdownTableWriter(headers=header, value_matrix=table, margin=1)
        for col in range(len(header)):
            md_table.set_style(col, ptw.style.Style(align="left"))  # left aligned

        self._content_md += "### Scheme table\n\n"
        self._content_md += str(md_table)

        # figures
        fig_light = rimsschemedrawer.Plotter(self.rims_scheme_data)
        [
            fig_light.savefig(self.fig_name_light.with_suffix(f".{fmt}"))
            for fmt in self.fig_formats
        ]
        fig_dark = rimsschemedrawer.Plotter(self.rims_scheme_data, darkmode=True)
        [
            fig_dark.savefig(self.fig_name_dark.with_suffix(f".{fmt}"))
            for fmt in self.fig_formats
        ]

        # add the figures to the content for dark and light mode
        self._content_md += (
            f"\n\n"
            f"### Scheme drawing\n\n"
            f"![{self.ele} scheme, light mode]({self.fig_name_light.relative_to(self.ele_path).with_suffix('.png')}#only-light)\n"
            f"![{self.ele} scheme, dark mode]({self.fig_name_dark.relative_to(self.ele_path).with_suffix('.png')}#only-dark)"
            f"\n\n"
        )

        # download table for scheme drawing
        download_table_header = ["Color mode", "Link to download"]
        download_table = [
            [
                "Light",
                ", ".join(
                    [
                        f"[{fmt.upper()}]({self.fig_name_light.relative_to(self.ele_path).with_suffix(f'.{fmt}')})\n"
                        for fmt in self.fig_formats
                    ]
                ),
            ],
            [
                "Dark",
                ", ".join(
                    [
                        f"[{fmt.upper()}]({self.fig_name_dark.relative_to(self.ele_path).with_suffix(f'.{fmt}')})\n"
                        for fmt in self.fig_formats
                    ]
                ),
            ],
        ]
        self._content_md += "### Download scheme drawing\n\n"
        md_table = ptw.MarkdownTableWriter(
            headers=download_table_header, value_matrix=download_table, margin=1
        )
        for col in range(len(download_table_header)):
            md_table.set_style(col, ptw.style.Style(align="left"))
        self._content_md += str(md_table)
