""" implementation of the base class for the coordinate value types
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

import ValueTypes.ValueTypeUtils.MinMaxValidator

from .CoordinateValueUtil import CoordinateValueUtil

from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.PropertyPaletteControlTextUtil import PropertyPaletteControlTextUtil
from ..ValueTypeUtils.PropertyPaletteGeometryControlService import PropertyPaletteGeometryControlService

if TYPE_CHECKING:
    from BuildingElementStringTable import BuildingElementStringTable
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class CoordinateImpl(ParameterPropertyValueType):
    """ implementation of the the base class for the coordinate value types
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           name : str,
                           value: Any) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            name:  name of the modified property
            value: new value

        Returns:
            update palette state
        """

        CoordinateValueUtil.set_coordinate(prop, name, value)

        return False


    @staticmethod
    def to_string(value: (AllplanGeo.Point2D | AllplanGeo.Point3D | AllplanGeo.Vector2D | AllplanGeo.Vector3D)) -> str:
        """ convert the coordinate to a string

        Args:
            value: coordinate value

        Returns:
            coordinate as string
        """

        return str(value).replace("\n", "").replace(" ", "")


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

        has_z_coord = isinstance(prop.value, (AllplanGeo.Point3D, AllplanGeo.Vector3D))

        text_util = PropertyPaletteControlTextUtil(prop_pal_ctrl_service.global_str_table)

        PropertyPaletteGeometryControlService.add_xyz_to_palette(wpf_palette, prop.name, ctrl_props,
                                                                 prop.value, "",
                                                                 text_util.get_row_name_text(ctrl_props, "", ""),
                                                                 has_z_coord, prop_pal_ctrl_service)


    @staticmethod
    def validate_for_min_value(prop            : ParameterProperty,
                               ctrl_prop       : ControlProperties,
                               min_value       : Any,
                               global_str_table: BuildingElementStringTable) -> bool:
        """ validate for the minimal value

        Args:
            prop:             property
            ctrl_prop:        control properties
            min_value:        min value
            global_str_table: global string table

        Returns:
            palette update state
        """

        has_z_coord = isinstance(prop.value, (AllplanGeo.Point3D, AllplanGeo.Vector3D))

        def test_min(value    : Any,
                     min_value: Any) -> tuple[bool, Any]:
            """ test for the min value

            Args:
                value:     value
                min_value: min value

            Returns:
                min value assigned state, min value
            """

            new_value = type(value)(value)

            new_value.X = max(value.X, min_value.X)
            new_value.Y = max(value.Y, min_value.Y)

            if has_z_coord and value.Z < min_value.Z:
                new_value.Z = min_value.Z

            return new_value != value, new_value

        return ValueTypes.ValueTypeUtils.MinMaxValidator.MinMaxValidator.validate_for_min_value(prop, ctrl_prop, min_value,
                                                                                                global_str_table, test_min)


    @staticmethod
    def validate_for_max_value(prop            : ParameterProperty,
                               ctrl_prop       : ControlProperties,
                               max_value       : Any,
                               global_str_table: BuildingElementStringTable) -> bool:
        """ validate for the maximal value

        Args:
            prop:             property
            ctrl_prop:        control properties
            max_value:        min value
            global_str_table: global string table

        Returns:
            palette update state
        """

        has_z_coord = isinstance(prop.value, (AllplanGeo.Point3D, AllplanGeo.Vector3D))

        def test_max(value    : Any,
                     max_value: Any) -> tuple[bool, Any]:
            """ test for the max value

            Args:
                value:     value
                max_value: max value

            Returns:
                max value assigned state, max value
            """

            new_value = type(value)(value)

            new_value.X = min(value.X, max_value.X)
            new_value.Y = min(value.Y, max_value.Y)

            if has_z_coord and value.Z > max_value.Z:
                new_value.Z = max_value.Z

            return new_value != value, new_value

        return ValueTypes.ValueTypeUtils.MinMaxValidator.MinMaxValidator.validate_for_max_value(prop, ctrl_prop, max_value,
                                                                                                global_str_table, test_max)


    @staticmethod
    def get_min_value() -> float:
        """ get the minimal value

        Returns:
            get the minimal value
        """

        return -1.7976931348623157e+300


    @staticmethod
    def get_max_value() -> float:
        """ get the maximal value

        Returns:
            get the maximal value
        """

        return 1.7976931348623157e+300
