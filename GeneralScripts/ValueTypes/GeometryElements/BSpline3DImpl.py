""" implementation of the BSpline3D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .BSplineImpl import BSplineImpl

class BSpline3DImpl(BSplineImpl):
    """ implementation of the BSpline3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.BSpline3D] | AllplanGeo.BSpline3D):
        """ get the 3D b-spline from a string

        Args:
            value_str: 3D b-spline string

        Returns:
            3D b-spline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_bspline3d, value_str)
