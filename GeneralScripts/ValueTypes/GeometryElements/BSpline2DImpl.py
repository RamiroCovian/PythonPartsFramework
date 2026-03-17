""" implementation of the BSpline2D value type
"""

from typing import Any

import importlib

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

import ValueTypes.GeometryElements.BSplineImpl as BSplineImpl      # pylint: disable=consider-using-from-import

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

importlib.reload(BSplineImpl)    # the module is not visible in the reload table!

class BSpline2DImpl(BSplineImpl.BSplineImpl):
    """ implementation of the BSpline2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.BSpline2D] | AllplanGeo.BSpline2D):
        """ get the 2D b-spline from a string

        Args:
            value_str: 2D b-spline string

        Returns:
            2D b-spline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_bspline2d, value_str)
