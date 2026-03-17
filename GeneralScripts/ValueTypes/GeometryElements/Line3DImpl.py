""" implementation of the Line3D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from .LineImpl import LineImpl

class Line3DImpl(LineImpl):
    """ implementation of the Line3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Line3D]| AllplanGeo.Line3D):
        """ get the 3d line from a string

        Args:
            value_str: 3D line string

        Returns:
            3D line(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_line3d, value_str)
