""" Script for BuildingElementXMLValue
"""
# pylint: disable=missing-docstring

from ValueTypes.ParameterPropertyValueType import ParameterPropertyValueType
from ValueTypes.ParameterPropertyValueTypesImpl import ParameterPropertyValueTypesImpl

class BuildingElementXMLValue():
    """ Definition of class BuildingElementXMLValue

    Convert a string value to the real value
    """


    @staticmethod
    def get_property_palette_value_type(value_type: ParameterPropertyValueType) -> ParameterPropertyValueType:
        """ Get the value type for the property palette

        Args:
            value_type: value type

        Returns:
            value type for the property palette
        """

        value_type_str = value_type.replace("inputlist", "list")


        #----------------- general list as list{} or single value like list{Double}

        if (ip_bracket := value_type_str.find("{")) == -1:
            return value_type

        if "{}" in value_type_str:
            return ParameterPropertyValueTypesImpl.get_value_type_impl(value_type_str.replace("{}", ""))

        if ";" in value_type_str:
            value_type_str = value_type_str[ip_bracket + 1:]

            return ParameterPropertyValueTypesImpl.get_value_type_impl(value_type_str[:value_type_str.find(";")])

        return ParameterPropertyValueTypesImpl.get_value_type_impl(value_type_str[ip_bracket + 1:].replace("}", ""))
