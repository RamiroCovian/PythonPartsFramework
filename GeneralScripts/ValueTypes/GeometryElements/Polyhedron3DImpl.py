""" implementation of the Point3D value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette

from BuildingElementGeometryUtil import BuildingElementGeometryUtil
from ControlProperties import ControlProperties

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.PropertyPaletteGeometryControlService import PropertyPaletteGeometryControlService
from ..ValueTypeUtils.PropertyPaletteControlTextUtil import PropertyPaletteControlTextData

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class Polyhedron3DImpl(ParameterPropertyValueType):
    """ implementation of the Polyhedron3D value type
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
    def to_string(value: AllplanGeo.Polyhedron3D) -> str:
        """ convert the polyhedron to a string

        Args:
            value: arc value

        Returns:
            arc as string
        """

        if value is None:
            return ""

        _, res = value.WriteToStream()

        return f"Polyhedron3D({res})"


    @staticmethod
    def get_value(value_str: Any) -> (list[AllplanGeo.Polyhedron3D] | AllplanGeo.Polyhedron3D):
        """ get the 3D Polyhedron from a string

        Args:
            value_str: 3D Polyhedron string

        Returns:
            3D Polyhedron(s)
        """

        return BaseStringToValueConverter.to_value_by_type_converter(BuildingElementGeometryUtil.get_value_polyhedron3d, value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the controls to the palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        if prop.value == []:
            return

        value = cast(AllplanGeo.Polyhedron3D, prop.value)

        for i, pnt in enumerate(value.GetVertices()):
            PropertyPaletteGeometryControlService.add_xyz_to_palette(wpf_palette, prop.name, ctrl_props,
                                                                     pnt, "",
                                                                     PropertyPaletteControlTextData(ctrl_props.text + str(i), ""),
                                                                     True, prop_pal_ctrl_service)
