""" implementation of the Spline2D value type
"""

from typing import Any

import importlib

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

import ValueTypes.GeometryElements.SplineImpl as SplineImpl      # pylint: disable=consider-using-from-import

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

importlib.reload(SplineImpl)    # the module is not visible in the reload table!

class Spline2DImpl(SplineImpl.SplineImpl):
    """ implementation of the Spline2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Spline2D] | AllplanGeo.Spline2D):
        """ get the 2D spline from a string

        Args:
            value_str: 2D spline string

        Returns:
            2D spline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_spline2d, value_str)
