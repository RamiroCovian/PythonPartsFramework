""" implementation of the Polyline3D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .BasePolyPointsImpl import BasePolyPointsImpl

class Polyline3DImpl(BasePolyPointsImpl):
    """ implementation of the Polyline3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Polyline3D] | AllplanGeo.Polyline3D):
        """ get the 3D polyline from a string

        Args:
            value_str: 3D polyline string

        Returns:
            3D polyline(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_polyline3d, value_str)
