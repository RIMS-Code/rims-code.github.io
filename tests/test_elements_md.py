# Tests for elements_md.py file


from pathlib import Path
import pytest

import rimscode_website.utils


@pytest.mark.parametrize(
    "fname",
    [
        [Path("HE-1.json"), ("he", 1)],
        [Path("amd-3.json"), None],
        [Path("as-444.json"), ("as", 444)],
        [Path("as-333-amf.json"), None],
        [Path("as-as.json"), None],
        [Path("readme.json"), None],
    ],
)
def test_parse_fname(fname):
    """Parse the file name and return ele, pos or None."""
    assert rimscode_website.utils.parse_db_filename(fname[0]) == fname[1]
