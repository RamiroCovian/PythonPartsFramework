""" implementation of the Point3D value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from .CoordinateImpl import CoordinateImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class Point3DImpl(CoordinateImpl):
    """ implementation of the Point3D value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[AllplanGeo.Point3D] | AllplanGeo.Point3D):
        """ get the 3D point from a string

        Args:
            value_str: 3D point string

        Returns:
            3D point(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_point3d, value_str)
