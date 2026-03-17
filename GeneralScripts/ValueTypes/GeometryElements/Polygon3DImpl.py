""" implementation of the Polygon3D value type
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .BasePolyPointsImpl import BasePolyPointsImpl

class Polygon3DImpl(BasePolyPointsImpl):
    """ implementation of the Polygon3D value type
    """

    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Polygon3D] | AllplanGeo.Polygon3D):
        """ get the 3D polygon from a string

        Args:
            value_str: 3D polygon string

        Returns:
            3D polygon(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_polygon3d, value_str)
