"""Class to create the content of a individual scheme page from the data file."""

import json
from pathlib import Path

import numpy as np
import pytablewriter as ptw
import rimsschemedrawer
import rttools.rims.saturation_curve as sc

from rimscode_website import SCHEMES_PATH
from rimscode_website.utils import parse_db_filename


class SchemeContentMD:
    """Create the content of an individual scheme page from the data file."""

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
        self.fig_name_dark_web = self.fig_path.joinpath(f"{self.db_file.stem}-dark-web")
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

        # Add the saturation curves section
        self._saturation_curves()

        # Add the references section
        self._reference()

        # Add submitted by
        self._submitted_by()

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

    def _saturation_curves(self):
        """Add the saturation curves to the content if available."""
        key = "saturation_curves"
        if key not in self.db_content.keys():
            return

        self._content_md += "\n\n## Saturation curves\n\n"

        # loop through available saturation curves
        for sit, sat_key in enumerate(self.db_content[key].keys()):
            self._content_md += f"### {sat_key}\n\n"

            fname = f"sat-{sit}"

            xdat = self.db_content[key][sat_key]["data"]["x"]
            xdat_err = self.db_content[key][sat_key]["data"].get("x_err", None)
            ydat = self.db_content[key][sat_key]["data"]["y"]
            ydat_err = self.db_content[key][sat_key]["data"].get("y_err", None)
            unit = self.db_content[key][sat_key].get("unit", None)

            # create figures
            if xdat_err:
                xdata = np.stack([np.array(xdat), np.array(xdat_err)])
            else:
                xdata = np.array(xdat)
            if ydat_err:
                ydata = np.stack([np.array(ydat), np.array(ydat_err)])
            else:
                ydata = np.array(ydat)
            fig_light = sc.saturation_curve(
                xdata, ydata, xunit=unit, darkmode=False, title=sat_key
            )
            [
                fig_light.savefig(self.fig_path.joinpath(f"{fname}-light.{fmt}"))
                for fmt in self.fig_formats
            ]
            fig_dark = sc.saturation_curve(
                xdata, ydata, xunit=unit, darkmode=True, title=sat_key
            )
            [
                fig_dark.savefig(self.fig_path.joinpath(f"{fname}-dark.{fmt}"))
                for fmt in self.fig_formats
            ]

            # create dark figure w/ transparent background for website
            fig_dark.axes[0].patch.set_alpha(0)
            fig_dark.figure.patch.set_alpha(0)
            fig_dark.savefig(self.fig_path.joinpath(f"{fname}-dark-web.png"))

            # create and save data table as csv file
            data_table_fname = self.fig_path.joinpath(f"{fname}-data-table.csv")
            data_table_hdr = [fig_dark.axes[0].get_xlabel()]
            if xdat_err is not None:
                data_table_hdr.append("+-")
            data_table_hdr.append(fig_dark.axes[0].get_ylabel())
            if ydat_err is not None:
                data_table_hdr.append("+-")
            data_table_arr = np.vstack([xdata, ydata]).T
            np.savetxt(
                data_table_fname,
                data_table_arr,
                delimiter=",",
                header=",".join(data_table_hdr),
            )

            # add the figures to the content for dark and light mode
            self._content_md += (
                f"![{sat_key}, light mode]({self.fig_path.relative_to(self.ele_path).joinpath(f'{fname}-light.png')}#only-light)\n"
                f"![{sat_key}, dark mode]({self.fig_path.relative_to(self.ele_path).joinpath(f'{fname}-dark-web.png')}#only-dark)\n"
            )

            # download table for saturation curve: data file and figures
            download_table_header = ["Data table", "Light color", "Dark color"]
            download_table = [
                [
                    f"[CSV]({data_table_fname.relative_to(self.ele_path)})",
                    ", ".join(
                        [
                            f"[{fmt.upper()}]({self.fig_path.relative_to(self.ele_path).joinpath(f'{fname}-light.{fmt}')})"
                            for fmt in self.fig_formats
                        ]
                    ),
                    ", ".join(
                        [
                            f"[{fmt.upper()}]({self.fig_path.relative_to(self.ele_path).joinpath(f'{fname}-dark.{fmt}')})"
                            for fmt in self.fig_formats
                        ]
                    ),
                ],
            ]
            md_table = ptw.MarkdownTableWriter(
                headers=download_table_header, value_matrix=download_table, margin=1
            )
            for col in range(len(download_table_header)):
                md_table.set_style(col, ptw.style.Style(align="left"))

            self._content_md += "\n\n#### Download saturation curve\n\n"
            self._content_md += str(md_table)
            self._content_md += "\n\n"

    def _scheme(self):
        """Add the scheme table to the content.

        This is a mandatory section, so no checks are done if section available.
        """
        self._content_md += "\n\n## Scheme\n\n"

        # label scheme IP:
        self._content_md += f"**Ionization Potential**: {rimsschemedrawer.utils.get_ip(self.ele):.3f} cm⁻¹  \n"

        try:
            lasers = self.db_content["rims_scheme"]["scheme"]["lasers"]
            self._content_md += f"**Lasers used**: {lasers}\n\n"
        except KeyError:
            self._content_md += "\n"

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
        # for web display, set backgrounds to transparent!
        fig_dark.axes.patch.set_alpha(0)
        fig_dark.figure.patch.set_alpha(0)
        fig_dark.savefig(self.fig_name_dark_web.with_suffix(".png"))

        # add the figures to the content for dark and light mode
        self._content_md += (
            f"\n\n"
            f"### Scheme drawing\n\n"
            f"![{self.ele} scheme, light mode]({self.fig_name_light.relative_to(self.ele_path).with_suffix('.png')}#only-light)\n"
            f"![{self.ele} scheme, dark mode]({self.fig_name_dark_web.relative_to(self.ele_path).with_suffix('.png')}#only-dark)"
            f"\n\n"
        )

        # download table for scheme drawing
        download_table_header = ["Light color", "Dark color"]
        download_table = [
            [
                ", ".join(
                    [
                        f"[{fmt.upper()}]({self.fig_name_light.relative_to(self.ele_path).with_suffix(f'.{fmt}')})\n"
                        for fmt in self.fig_formats
                    ]
                ),
                ", ".join(
                    [
                        f"[{fmt.upper()}]({self.fig_name_dark.relative_to(self.ele_path).with_suffix(f'.{fmt}')})\n"
                        for fmt in self.fig_formats
                    ]
                ),
            ],
        ]
        self._content_md += "#### Download scheme drawing\n\n"
        md_table = ptw.MarkdownTableWriter(
            headers=download_table_header, value_matrix=download_table, margin=1
        )
        for col in range(len(download_table_header)):
            md_table.set_style(col, ptw.style.Style(align="left"))
        self._content_md += str(md_table)

    def _submitted_by(self):
        """Add submitted by if available."""
        key = "submitted_by"
        if key in self.db_content.keys():
            self._content_md += "\n\n## Submitted by\n\n"
            self._content_md += self.db_content[key] + "\n\n"
