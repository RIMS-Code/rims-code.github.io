"""Get elemental information for a given element."""

from rimsschemedrawer import utils as ut

from rimscode_website import ureg
from rimscode_website.data import read_rilis_elements

RILIS_DATA = read_rilis_elements()


class Element:
    """Element class to get information about an element.

    Ionization potentials are retrieved in cm^-1 from the RIMSSchemeDrawer utilities.
    All other information is retrieved from the CERN RILIS element file, saved
    in `data/rilis_elements.json`.
    """

    def __init__(self, ele: str) -> None:
        """Initialize the Element class.

        :param ele: Element symbol, not case-sensitive.
        """
        self._ele = ele.capitalize()
        self._data = RILIS_DATA[self._ele]

    @property
    def atomic_number(self) -> int:
        """Get the atomic number of the element.

        :return: Atomic number.
        """
        return int(self._data["AtomicNumber"])

    @property
    def atomic_weight(self) -> ureg.Quantity:
        """Get the atomic weight of the element.

        :return: Atomic weight in amu.
        """
        return ureg.Quantity(float(self._data["AtomicWeight"]), ureg.amu)

    @property
    def boiling_point(self) -> ureg.Quantity:
        """Get the boiling point of the element.

        Returns None if no boiling point is available.

        :return: Boiling point in K.
        """
        try:
            ret_val = ureg.Quantity(float(self._data["BoilingPoint"]), ureg.degC)
            return ret_val.to("kelvin")
        except ValueError:
            return None

    @property
    def ionization_potential(self) -> ureg.Quantity:
        """Get the ionization potential of the element.

        :return: Ionization potential in cm^-1.
        """
        return ureg.Quantity(ut.get_ip(self._ele), ureg.Unit("cm^-1"))

    @property
    def melting_point(self) -> ureg.Quantity:
        """Get the melting point of the element.

        Returns None if no melting point is available.

        :return: Melting point in K.
        """
        try:
            ret_val = ureg.Quantity(float(self._data["MeltingPoint"]), ureg.degC)
            return ret_val.to("kelvin")
        except ValueError:
            return None

    @property
    def name(self) -> str:
        """Get the name of the element.

        :return: Name of the element.
        """
        return self._data["StandardName"]

    @property
    def symbol(self) -> str:
        """Get the symbol of the element.

        :return: Symbol of the element.
        """
        return self._ele

    @property
    def type(self) -> str:
        """Get the type of the element.

        :return: Type of the element.
        """
        return self._data["Series"]
