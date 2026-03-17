""" implementation of the base class for the enum based value types
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ValueTypeUtils.BaseValueToStringConverter import BaseValueToStringConverter
from .ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil
from .ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class BaseEnumListImpl(ParameterPropertyValueType):
    """ implementation of the base class for the enum based value types
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           name : str,
                           value: Any) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            name:  name of the modified property
            value: new value

        Returns:
            update palette state
        """

        prop.is_modified = True

        if (enum_dict := prop.enum_dict):
            value = enum_dict[value]

        ParameterPropertyListUtil.set_item_value(prop, name, value)

        return True


    @staticmethod
    def to_string(value: Any) -> str:
        """ convert the value to a string

        Args:
            value: new value

        Returns:
            value as string
        """

        value_str = str(value)

        if value_str.lstrip("-").isnumeric():
            return value_str

        return BaseValueToStringConverter.enum_to_string(value)


    @staticmethod
    def get_value(value_str: str) -> (list[Any] | Any):
        """ get the value from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        return BaseStringToValueConverter.to_int(value_str)
