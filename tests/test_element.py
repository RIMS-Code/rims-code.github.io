"""Test the element class."""

from rimsschemedrawer import utils as ut

from rimscode_website import ureg
from rimscode_website.element import Element


def test_element_entries():
    """Assure that entries that are expected to be present are present."""
    ele = Element("n")

    assert ele.atomic_number == 7
    assert ele.atomic_weight == ureg.Quantity(14.0067, ureg.amu)
    assert ele.name == "Nitrogen"
    assert ele.symbol == "N"
    assert ele.boiling_point == ureg.Quantity(-195.79, ureg.degC).to("kelvin")
    assert ele.melting_point == ureg.Quantity(-210.1, ureg.degC).to("kelvin")
    assert ele.type == "Nonmetal"


def test_entries_all_elements():
    """Run through elements and assure they are there."""
    for this_ele in ut.get_elements():
        ele = Element(this_ele)

        # check all names
        assert ele.symbol == this_ele

        # ensure all entries return useful values
        assert ele.atomic_number > 0
        assert ele.atomic_weight.magnitude > 0
        assert ele.name != ""
        assert ele.type != ""

        # melting point and boiling point, can be numbers or None if N/A
        if ele.melting_point is not None:
            assert ele.melting_point.magnitude > 0
            assert ele.melting_point.units == ureg.kelvin
        if ele.boiling_point is not None:
            assert ele.boiling_point.magnitude > 0
            assert ele.boiling_point.units == ureg.kelvin

        # ionization potential
        assert ele.ionization_potential.magnitude > 0
        assert ele.ionization_potential.units == ureg.Unit("cm^-1")
