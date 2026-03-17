""" implementation of the ReinforcementShapeProperties value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING


from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties

from ..BaseIntImpl import BaseIntImpl
from .ReinforcementShapeBarPropertiesImpl import ReinforcementShapeBarPropertiesImpl
from .ReinforcementShapeMeshPropertiesImpl import ReinforcementShapeMeshPropertiesImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinforcementShapePropertiesImpl(BaseIntImpl):
    """ implementation of the ReinforcementShapeProperties value type
    """

    EMPTY_DIAMETER = "Diameter(0.0)"

    @staticmethod
    def get_value(value_str: str) -> ReinforcementShapeProperties:
        """ get the shape properties from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if ReinforcementShapePropertiesImpl.EMPTY_DIAMETER not in value_str:
            return ReinforcementShapeBarPropertiesImpl.get_value(value_str)

        return ReinforcementShapeMeshPropertiesImpl.get_value(value_str)
