""" implementation of the Arc2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ArcImpl import ArcImpl

class Arc3DImpl(ArcImpl):
    """ implementation of the Arc3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Arc3D] | AllplanGeo.Arc3D):
        """ get the 3D arc from a string

        Args:
            value_str: 3D arc string

        Returns:
            3D arc(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_arc3d, value_str)
