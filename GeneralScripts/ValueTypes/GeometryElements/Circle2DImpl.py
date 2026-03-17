""" implementation of the Circle2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .CircleImpl import CircleImpl

class Circle2DImpl(CircleImpl):
    """ implementation of the Circle2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Arc2D] | AllplanGeo.Arc2D):
        """ get the 2D circle from a string

        Args:
            value_str: 2D circle string

        Returns:
            2D circle(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_circle2d, value_str)
