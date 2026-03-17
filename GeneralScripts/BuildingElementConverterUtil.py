"""
Script for BuildingElement
"""

from typing import Callable, Any

from BuildingElementGeometryUtil import BuildingElementGeometryUtil
from BuildingElementFixtureUtil import BuildingElementFixtureUtil
from BuildingElementArchitectureUtil import BuildingElementArchitectureUtil
from BuildingElementReinforcementUtil import BuildingElementReinforcementUtil

class BuildingElementConverterUtil():
    """
    Definition of class BuildingElementConverterUtil
    """

    @staticmethod
    def get_string_to_value_converter(value_type) -> Callable[[str], Any]:
        """
        Get the string to value converter for a value type

        Args:
            value_type:     Type of the value

        Return: value converter
        """

        function_get_value = "get_value_"+ value_type

        geo_conv   = getattr(BuildingElementGeometryUtil, function_get_value, None)

        if geo_conv:
            return geo_conv

        reinf_conv = getattr(BuildingElementReinforcementUtil, function_get_value, None)

        if reinf_conv:
            return reinf_conv

        arch_conv  = getattr(BuildingElementArchitectureUtil, function_get_value, None)

        if arch_conv:
            return arch_conv

        fixture_conv  = getattr(BuildingElementFixtureUtil, function_get_value, None)

        if fixture_conv:
            return fixture_conv

        return None
