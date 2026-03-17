""" implementation of the Polygon2D value type
"""

from typing import Any

import importlib

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

import ValueTypes.GeometryElements.BasePolyPointsImpl as BasePolyPointsImpl      # pylint: disable=consider-using-from-import

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

importlib.reload(BasePolyPointsImpl)    # the module is not visible in the reload table!

class Polygon2DImpl(BasePolyPointsImpl.BasePolyPointsImpl):
    """ implementation of the Polygon2D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Polygon2D] | AllplanGeo.Polygon2D):
        """ get the 2D polygon from a string

        Args:
            value_str: 2D polygon string

        Returns:
            2D polygon(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_polygon2d, value_str)
