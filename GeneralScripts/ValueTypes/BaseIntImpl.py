""" implementation of the base class for the int based value types
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ValueTypeUtils.ValueListValidator import ValueListValidator

from .ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class BaseIntImpl(ParameterPropertyValueType):
    """ implementation of the base class for the int based value types
    """

    @staticmethod
    def to_string(value: int) -> str:
        """ convert the integer to a string

        Args:
            value: new value

        Returns:
            integer as string
        """

        return str(value)


    @staticmethod
    def get_value(value_str: str) -> (list[int] | int):
        """ get the integer from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        return BaseStringToValueConverter.to_int(value_str)


    @staticmethod
    def validate_for_list_value(value         : (list[int] | int),
                                value_type    : ParameterPropertyValueType,
                                value_list    : str,
                                parameter_dict: dict[str, Any]) -> tuple[bool, (list[int] | int)]:
        """ test for an existing integer value in the list

        Args:
            value:          value to test
            value_type:     value type
            value_list:     value list as pipe separated string or range command
            parameter_dict: parameter dictionary for the range command

        Returns:
            (value was updated, value if present in the list or nearest value from the list)
        """

        if isinstance(value, list):
            return ValueListValidator.validate_list(value, value_type, value_list, parameter_dict)

        return ValueListValidator.validate_numeric_value(value, value_type, value_list, int, parameter_dict)
