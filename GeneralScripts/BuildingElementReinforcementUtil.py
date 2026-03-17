""" Script for BuildingElementReinforcementUtil
"""

from ValueTypes.Reinforcement.ReinforcementShapeBarPropertiesImpl import ReinforcementShapeBarPropertiesImpl
from ValueTypes.Reinforcement.ReinforcementShapeMeshPropertiesImpl import ReinforcementShapeMeshPropertiesImpl


class BuildingElementReinforcementUtil():
    """ Definition of class BuildingElementReinforcementUtil
    """

    @staticmethod
    def get_value_reinforcementshapeproperties(value_str):
        """ Get the reinforcement shape properties from a value string

        Args:   value_str   Value string

        Return: Reinforcement shape properties
        """

        if "Diameter(0.0)" not in value_str:
            return ReinforcementShapeBarPropertiesImpl.get_value(value_str)

        return ReinforcementShapeMeshPropertiesImpl.get_value(value_str)
