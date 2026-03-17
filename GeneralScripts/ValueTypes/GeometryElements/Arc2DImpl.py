""" implementation of the Arc2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ArcImpl import ArcImpl

class Arc2DImpl(ArcImpl):
    """ implementation of the Arc2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Arc2D] | AllplanGeo.Arc2D):
        """ get the 2D arc from a string

        Args:
            value_str: 2D arc string

        Returns:
            2D arc(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_arc2d, value_str)
