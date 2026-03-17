""" Script for StringToValueUtil
"""

from typing import Any, Generic, TypeVar

import math

import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from Utilities.GeneralConstants import GeneralConstants

T = TypeVar("T")

class StringToValueUtil(Generic[T]):
    """ Definition of class StringToValueUtil
    """

    @staticmethod
    def get_bool_value_from_str(value_str: str) -> bool:
        """ Extract boolean value of string

        Args:
            value_str: String to parse for True or False.

        Returns:
            bool value from the string
        """
        return value_str.lower() == GeneralConstants.LOWER_TRUE


    @staticmethod
    def get_property_string(value_str:str,
                            prop     : str,
                            default  : Any) -> str:
        """ Get the property string for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property string
        """

        #----------------- get the value of the property

        parts = value_str.partition(prop)

        if not parts[1]:
            return default


        #----------------- get the value

        nclose = 0
        nopen  = 0

        value = parts[2].strip()

        for i, char in enumerate(value):
            if char == GeneralConstants.BRACKET_OPEN:
                nopen += 1

            elif char == GeneralConstants.BRACKET_CLOSE:
                nclose += 1

            if nopen == nclose:
                return value[1: i]

        return value[1:]


    @staticmethod
    def get_property_float(value_str: str,
                           prop     : str,
                           default  : str) -> float:
        """ Get the float property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property value
        """

        return float(StringToValueUtil.get_property_string(value_str, prop, default))


    @staticmethod
    def get_property_angle(value_str: str,
                           prop     : str,
                           default  : str) -> float:
        """ Get the angle property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property value
        """

        math_dict = {"pi": math.pi}

        return float(eval(StringToValueUtil.get_property_string(value_str, prop, default), math_dict))


    @staticmethod
    def get_property_int(value_str: str,
                         prop     : str,
                         default  : int) -> int:
        """ Get the int property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property value
        """

        return int(StringToValueUtil.get_property_string(value_str, prop, default))


    @staticmethod
    def get_property_bool(value_str: str,
                          prop     : str,
                          default  : bool) -> bool:
        """ Get the bool property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property value
        """

        return bool(int(StringToValueUtil.get_property_string(value_str, prop, default)))


    @staticmethod
    def get_property_guid(value_str: str,
                         prop      : str,
                         default   : str) -> AllplanEleAdapter.GUID:
        """ Get the int property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string

        Returns:
            property value
        """

        return AllplanUtil.GUID.FromString(StringToValueUtil.get_property_string(value_str, prop, default))


    @staticmethod
    def get_property_enum(value_str: str,
                          prop     : str,
                          default  : str,
                          enums    : list[T]) -> (T | None):
        """ Get the int property value for a property

        Args:
            value_str:      Value string like "Center(1000,2000,300)MinorRadius(500)"
            prop:           Property
            default:        Default value string
            enums:          enumerations

        Returns:
            property value
        """

        value = int(StringToValueUtil.get_property_string(value_str, prop, default))

        return next((enum_value for enum_value in enums if enum_value == value), None)
