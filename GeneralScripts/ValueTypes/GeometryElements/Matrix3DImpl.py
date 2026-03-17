""" implementation of the Matrix3D value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette

from BuildingElementGeometryUtil import BuildingElementGeometryUtil
from ControlProperties import ControlProperties

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.ValueToStringUtil import ValueToStringUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class Matrix3DImpl(ParameterPropertyValueType):
    """ implementation of the Matrix3D value type
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           _name: str,
                           value: Any) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            _name: name of the modified property
            value: new value

        Returns:
            update palette state
        """

        if value is None:
            return False

        prop.is_modified = True

        prop.value = value

        return True


    @staticmethod
    def to_string(value: AllplanGeo.Matrix3D) -> str:
        """ convert the matrix to a string

        Args:
            value: arc value

        Returns:
            arc as string
        """

        return ValueToStringUtil.to_string_strip(value)


    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Matrix3D] | AllplanGeo.Matrix3D):
        """ get the matrix from a string

        Args:
            value_str: matrix string

        Returns:
            matrix
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_matrix3d, value_str)


    @staticmethod
    def add_to_palette(_wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       _prop                 : ParameterProperty,
                       _ctrl_props           : ControlProperties,
                       _prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the control to the palette

        Args:
            _wpf_palette:           WPf palette
            _prop:                  parameter property
            _ctrl_props:            control properties
            _prop_pal_ctrl_service: property palette control service
        """
