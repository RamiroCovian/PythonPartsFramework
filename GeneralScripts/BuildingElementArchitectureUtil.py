"""
Script for BuildingElementArchitectureUtil
"""

from ValueTypes.Resources.PlaneReferencesImpl import PlaneReferencesImpl

class BuildingElementArchitectureUtil():
    """
    Definition of class BuildingElementArchitectureUtil
    """

    @staticmethod
    def get_value_planereferences(value_str):
        """
        Get the plane reference properties

        Args:   value_str   Value string

        Return: Plane reference properties

        """

        return PlaneReferencesImpl.get_value(value_str)
