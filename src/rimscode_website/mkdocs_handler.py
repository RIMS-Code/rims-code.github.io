"""This script handles all tasks related to the mkdocs.yaml file."""

import yaml

from rimscode_website import REPO_PATH


def navigation(all_schemes: dict) -> None:
    """Create the scheme navigation part of the mkdocs.yaml file.

    First, the existing scheme section is deleted, then a new one is created.

    Example dictionary for entry:
        {
            'he': ['schemes/he/he-1', 'schemes/he/he-2'],
            'as': ['schemes/as/as-1', 'schemes/as/as-2']
        }

    Note that the lists in the dictionary are not sorted here!

    :param all_schemes: Dictionary with available elements and all schemes.
        {"ele": ["ele/scheme-1", "ele/scheme-2", ...]}
    """
    # create the new scheme section
    scheme_dict = {"Schemes": [{"Periodic Table": "schemes.md"}, {"Elements": []}]}

    for ele, schemes in all_schemes.items():
        ele_dict = {}
        # add the element to the ele dictionary
        ele_dict[ele.capitalize()] = [{"Overview": f"schemes/{ele}/index.md"}]

        # add the schemes to the element
        for scheme in all_schemes[ele]:
            scheme_key = scheme.split("/")[1].capitalize()
            scheme_key = f"{scheme_key.split("-")[0]}-{int(scheme_key.split('-')[1])}"
            ele_dict[ele.capitalize()].append({scheme_key: f"schemes/{scheme}.md"})

        # add the element to the scheme dictionary
        scheme_dict["Schemes"][1]["Elements"].append(ele_dict)

    _write_mkdocs_conf(scheme_dict)


def _load_mkdocs_conf() -> dict:
    """Load the  mkdocs.yaml file.

    :return: Dictionary with the mkdocs.yml file.
    """
    with open(REPO_PATH.joinpath("mkdocs.yml"), "r") as f:
        mkd_conf = yaml.safe_load(f)
    return mkd_conf


def _write_mkdocs_conf(scheme_dict: dict) -> dict:
    """Write new scheme dictionary to mkdocs.yaml file.

    This updates the navigation of the website.

    :param scheme_dict: Dictionary with the scheme navigation.
    """
    mkd_conf = _load_mkdocs_conf()

    # find the index where the "Schemes" dictionary is in the navigation
    idx = None
    for it, entry in enumerate(mkd_conf["nav"]):
        if "Schemes" in entry.keys():
            idx = it
            break

    if idx is None:
        raise ValueError(
            "Could not find the 'Schemes' navigation entry in the mkdocs.yml file."
        )

    mkd_conf["nav"][idx] = scheme_dict

    with open(REPO_PATH.joinpath("mkdocs.yml"), "w") as f:
        yaml.dump(mkd_conf, f, default_flow_style=False, sort_keys=False, indent=2)
    return mkd_conf
