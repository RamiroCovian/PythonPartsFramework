""" implementation of the Circle2D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .CircleImpl import CircleImpl

class Circle3DImpl(CircleImpl):
    """ implementation of the Circle3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Arc3D] | AllplanGeo.Arc3D):
        """ get the 3D circle from a string

        Args:
            value_str: 3D circle string

        Returns:
            3D circle(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_circle3d, value_str)
