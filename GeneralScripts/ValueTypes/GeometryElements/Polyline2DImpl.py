""" implementation of the Polyline2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .BasePolyPointsImpl import BasePolyPointsImpl

class Polyline2DImpl(BasePolyPointsImpl):
    """ implementation of the Polyline2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Polyline2D] | AllplanGeo.Polyline2D):
        """ get the 2D polyline from a string

        Args:
            value_str: 2D polyline string

        Returns:
            2D polyline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_polyline2d, value_str)
