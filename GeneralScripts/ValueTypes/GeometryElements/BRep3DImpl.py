""" implementation of the BRep3D value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette

from BuildingElementGeometryUtil import BuildingElementGeometryUtil
from ControlProperties import ControlProperties

import GeometryValidate

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.PropertyPaletteGeometryControlService import PropertyPaletteGeometryControlService
from ..ValueTypeUtils.PropertyPaletteControlTextUtil import PropertyPaletteControlTextData
from ..ValueTypeUtils.ValueToStringUtil import ValueToStringUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class BRep3DImpl(ParameterPropertyValueType):
    """ implementation of the BRep3D value type
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
    def to_string(value: AllplanGeo.BRep3D) -> str:
        """ convert the BRep3D to a string

        Args:
            value: arc value

        Returns:
            arc as string
        """

        if value is None:
            return ""

        _, res, trans_mat = value.WriteToStream()

        return f"BRep3D(Body({res}),{ValueToStringUtil.to_string_strip(trans_mat)})"


    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.BRep3D] | AllplanGeo.BRep3D):
        """ get the 3D Polyhedron from a string

        Args:
            value_str: 3D Polyhedron string

        Returns:
            3D Polyhedron(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_brep3d, value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the control to the palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        if prop.value == []:
            return

        value = cast(AllplanGeo.BRep3D, prop.value)

        error, vertices = value.GetVertices()

        if not GeometryValidate.element_method(error):
            return

        for i, pnt in enumerate(vertices):
            PropertyPaletteGeometryControlService.add_xyz_to_palette(wpf_palette, prop.name, ctrl_props,
                                                                     pnt, "",
                                                                     PropertyPaletteControlTextData(ctrl_props.text + str(i), ""),
                                                                     True, prop_pal_ctrl_service)
