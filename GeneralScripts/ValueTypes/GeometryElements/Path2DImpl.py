""" implementation of the Path2D value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class Path2DImpl(ParameterPropertyValueType):
    """ implementation of the Path2D value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[AllplanGeo.Path2D] | AllplanGeo.Path2D):
        """ get the 2D path from a string

        Args:
            value_str: 2D path string

        Returns:
            2D path(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_path2d, value_str)


    @staticmethod
    def to_string(value: AllplanGeo.Path2D) -> str:
        """ convert the path to a string

        Args:
            value: path value

        Returns:
            path as string
        """

        return str(value).replace("\n", "").replace(" ", "")
