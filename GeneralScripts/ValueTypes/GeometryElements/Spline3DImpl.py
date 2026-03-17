""" implementation of the Spline3D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .SplineImpl import SplineImpl

class Spline3DImpl(SplineImpl):
    """ implementation of the Spline3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Spline3D] | AllplanGeo.Spline3D):
        """ get the 3D spline from a string

        Args:
            value_str: 3D spline string

        Returns:
            3D spline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_spline3d, value_str)
