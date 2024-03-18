"""Convert CERN RILIS dbj format to json database entries."""

import json
from pathlib import Path
import shutil
import warnings


DBJ_FILE = Path("../temp/scheme_formatted.dbj")
OUT_PATH = Path("../temp/out")

ALL_WARNINGS = False

GERMAN_NUMBERS = {
    0: "null",
    1: "eins",
    2: "zwei",
    3: "drei",
    4: "vier",
    5: "fuenf",
    6: "sechs",
    7: "sieben",
}

# dictionary with RILIS keys - new keys in scheme
KEY_MAPPER_SCHEME = {
    "enull": "gs_level",
    "cnull": "gs_term",
    "eeins": "step_level0",
    "ezwei": "step_level1",
    "edrei": "step_level2",
    "evier": "step_level3",
    "efuenf": "step_level4",
    "esechs": "step_level5",
    "ceins": "step_term0",
    "czwei": "step_term1",
    "cdrei": "step_term2",
    "cvier": "step_term3",
    "cfuenf": "step_term4",
    "csechs": "step_term5",
    "tnull": "trans_strength0",
    "teins": "trans_strength1",
    "tzwei": "trans_strength2",
    "tdrei": "trans_strength3",
    "tvier": "trans_strength4",
    "tfuenf": "trans_strength5",
}

with open(DBJ_FILE, "r") as f:
    data = json.load(f)

# delete the example key
del data["Ex"]

# loop through all elements and create files

# delete all folders and files in out path
shutil.rmtree(OUT_PATH, ignore_errors=True)

# warning counters
cnt_warn_too_many_wl = 0
cnt_warn_too_many_ion_steps = 0
cnt_warn_no_ion_step = 0

for ele, entries in data.items():
    # create the output directory
    out_dir = OUT_PATH.joinpath(ele.lower())
    out_dir.mkdir(parents=True)

    for eit, entry in enumerate(entries):
        # problem at Ga, there's an additional level of nesting here!
        if ele == "Ga":
            entry = entries[entry]

        add_to_note = ""  # string to add to note at the very end

        entry_index = eit + 1
        out_file = out_dir.joinpath(f"{ele.capitalize()}-{entry_index}.json")

        content = {"rims_scheme": {"scheme": {}}}

        # create the rims scheme entry with the element
        scheme_out = {"element": ele.capitalize()}

        print(f"{ele=}, {eit=}")
        # lasers used
        lasers_used = entry.get("lasersused", None)
        if lasers_used:
            scheme_out["lasers"] = lasers_used

        # go through key mapper and fill with values (even if empty)
        for key, val in KEY_MAPPER_SCHEME.items():
            ent = entry.get(key, "")
            scheme_out[val] = ent

        # define which step is the ionization step
        it_step = 0
        for key in scheme_out.keys():
            if key.startswith("step_level"):
                it_current = int(key[-1])
                if it_current > it_step and scheme_out[key] != "":
                    it_step = it_current

        # check if ionization step in "w" values, in "ryd" or in "ai"
        ws_cern = []
        for it, german in GERMAN_NUMBERS.items():
            val = entry.get(f"w{german}", None)
            if val:
                ws_cern.append(val)

        w_cern = None

        if len(ws_cern) > 1 and ALL_WARNINGS:  # 2024-03-18: does not occur
            warnings.warn(
                f"Wavelengths defined > 1:\n" f"{ele=}\n{eit=}\n{entry=}\n{ws_cern=}"
            )
            cnt_warn_too_many_wl += 1
        elif len(ws_cern) == 1:
            if ele == "Tc" and eit == 4:  # special case Tc-4 - add a note!
                w_cern = None
                add_to_note = "Ionization step wavelength: >1129 nm\n"
            elif ele == "Pm" and eit == 0:  # For Pm-O, choose AI (better precision)
                add_to_note = (
                    f"Ionization step wavelength in original database: {w_cern} nm\n"
                )
                w_cern = None
            else:
                # transform wavelength to step level
                ws_temp = ws_cern[0]
                ws_temp = ws_temp.replace(",", ".")  # transform comma to period
                ws_temp = ws_temp.replace(" ", "")  # remove spaces
                if "&lt;" in ws_temp:
                    ws_temp = ws_temp.replace("&lt;", "")
                    add_to_note += "Ionization wavelength is a lower limit.\n"
                wl = float(ws_temp)

                step_before = it_step - 1
                if step_before == -1:
                    step_before_key = "gs_level"
                else:
                    step_before_key = f"step_level{step_before}"
                step_before = float(scheme_out[step_before_key])
                w_cern = step_before + (1 / wl * 1e7)

        ai_cern = entry.get("ai", None)
        ryd_cern = entry.get("ryd", None)

        if ALL_WARNINGS:
            if (
                bool(w_cern) + bool(ai_cern) + bool(ryd_cern) > 1
            ):  # more than one ion step
                warnings.warn(
                    f"More than one ionization step defined.\n{ele=}\n{eit=}\n{entry=}"
                )
                cnt_warn_too_many_ion_steps += 1

        # so only one ionization step is defined, add it to the scheme
        # We pick w_cern as the dominant one, exceptions are excluded in w_cern finder
        ionizaton_step = (
            w_cern if w_cern else ai_cern if ai_cern else ryd_cern if ryd_cern else None
        )
        if ionizaton_step:
            scheme_out[f"step_level{it_step}"] = ionizaton_step
        else:
            warnings.warn(f"No ionization step defined.\n{ele=}\n{eit=}\n{entry=}")
            cnt_warn_no_ion_step += 1

        # unit
        scheme_out["unit"] = "cm^-1"

# print status of warning counters
print(
    f"Warning counters:\n"
    f"{cnt_warn_too_many_wl=}\n"
    f"{cnt_warn_too_many_ion_steps=}\n"
    f"{cnt_warn_no_ion_step=}"
)
