""" implementation of the Line2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .LineImpl import LineImpl

class Line2DImpl(LineImpl):
    """ implementation of the Line2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Line2D] | AllplanGeo.Line2D):
        """ get the 2D line from a string

        Args:
            value_str: 2D line string

        Returns:
            2D line(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_line2d, value_str)
