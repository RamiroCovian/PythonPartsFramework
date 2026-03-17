""" implementation of the Vector2D value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .CoordinateImpl import CoordinateImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class Vector2DImpl(CoordinateImpl):
    """ implementation of the Vector2D value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[AllplanGeo.Vector2D] | AllplanGeo.Vector2D):
        """ get the 2D vector from a string

        Args:
            value_str: 2D vector string

        Returns:
            2D vector(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_vector2d, value_str)
