""" implementation of the property palette service for the geometry controls
"""

from __future__ import annotations

from typing import cast, TYPE_CHECKING, Any

from collections.abc import Callable

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from Utilities.ConditionUtil import ConditionUtil

from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService
from .PropertyPaletteControlTextUtil import PropertyPaletteControlTextUtil, PropertyPaletteControlTextData
from ..ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

class PropertyPaletteGeometryControlService():
    """ implementation of the property palette service for the geometry controls
    """

    @staticmethod
    def add_xyz_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                           value_name           : str,
                           ctrl_props           : ControlProperties,
                           xyz_value            : (AllplanGeo.Point2D | AllplanGeo.Point3D | AllplanGeo.Vector2D | AllplanGeo.Vector3D),
                           xyz_name             : str,
                           text_data            : PropertyPaletteControlTextData,
                           has_z_coord          : bool,
                           prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the xyz coordinates to the property palette

        Args:
            wpf_palette:           WPf palette
            value_name:            value name
            ctrl_props:            control properties
            xyz_value:             value of the coordinate
            xyz_name:              name of the coordinate, e. g. "StartPoint
            text_data:             text data
            has_z_coord:           has z coordinate state
            prop_pal_ctrl_service: property palette control service
        """

        PropertyPaletteGeometryControlService.__add_xyz_to_palette(wpf_palette, value_name, ctrl_props, xyz_value, xyz_name,
                                                                   text_data, has_z_coord, prop_pal_ctrl_service,
                                                                   prop_pal_ctrl_service.add_length_edit_control)

    @staticmethod
    def add_direction_vector_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                                        value_name           : str,
                                        ctrl_props           : ControlProperties,
                                        xyz_value            : (AllplanGeo.Vector2D | AllplanGeo.Vector3D),
                                        xyz_name             : str,
                                        text_data            : PropertyPaletteControlTextData,
                                        has_z_coord          : bool,
                                        prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add a direction vector to the property palette. Double value input is used for the coordinates.

        Args:
            wpf_palette:           WPf palette
            value_name:            value name
            ctrl_props:            control properties
            xyz_value:             value of the vector
            xyz_name:              name of the vector, e. g. "StartVector
            text_data:             text data
            has_z_coord:           has z vector state
            prop_pal_ctrl_service: property palette control service
        """

        PropertyPaletteGeometryControlService.__add_xyz_to_palette(wpf_palette, value_name, ctrl_props, xyz_value, xyz_name,
                                                                   text_data, has_z_coord, prop_pal_ctrl_service,
                                                                   prop_pal_ctrl_service.add_double_edit_control)


    @staticmethod
    def __add_xyz_to_palette(wpf_palette             : AllplanPalette.PythonWpfPaletteBuilder,
                             value_name              : str,
                             ctrl_props              : ControlProperties,
                             xyz_value               : (AllplanGeo.Point2D | AllplanGeo.Point3D | \
                                                        AllplanGeo.Vector2D | AllplanGeo.Vector3D),
                             xyz_name                : str,
                             text_data               : PropertyPaletteControlTextData,
                             has_z_coord             : bool,
                             prop_pal_ctrl_service   : PropertyPaletteControlService,
                             palette_control_function: Callable):
        """ Add the xyz coordinates to the property palette

        Args:
            wpf_palette:              WPf palette
            value_name:               value name
            ctrl_props:               control properties
            xyz_value:                value of the coordinate
            xyz_name:                 name of the coordinate, e. g. "StartPoint
            text_data:                text data
            has_z_coord:              has z coordinate state
            prop_pal_ctrl_service:    property palette control service
            palette_control_function: function for the control creation
        """

        add_sep = "." if xyz_name else ""

        x_name = f"{value_name}{add_sep}{xyz_name}.X"
        y_name = f"{value_name}{add_sep}{xyz_name}.Y"
        z_name = f"{value_name}{add_sep}{xyz_name}.Z"

        xyz_row_name = text_data.row_name
        xyz_text     = text_data.text

        prop_visible_dict = ConditionUtil.get_condition_dict(ctrl_props.visible_condition, value_name, prop_pal_ctrl_service.param_dict)

        if not ParameterPropertyValueType.is_visible(x_name, prop_visible_dict) or \
           not ParameterPropertyValueType.is_visible(y_name, prop_visible_dict) or \
           has_z_coord and not ParameterPropertyValueType.is_visible(z_name, prop_visible_dict):
            xyz_row_name = ""

        sub_name = f"{xyz_name}." if xyz_name else ""

        min_value = ctrl_props.min_value
        max_value = ctrl_props.max_value


        #----------------- x coord

        if prop_visible_dict.get(x_name, True) is True:
            sub_text = PropertyPaletteControlTextUtil.get_sub_text(ctrl_props.member_text, value_name, xyz_text, f"{sub_name}X")

            palette_control_function(wpf_palette, x_name, ctrl_props, xyz_value.X,
                                     PropertyPaletteGeometryControlService.__get_min_value(min_value, "X"),
                                     PropertyPaletteGeometryControlService.__get_max_value(max_value, "X"),
                                     PropertyPaletteControlTextData(xyz_row_name + ctrl_props.row_state_key, sub_text))

        #----------------- y coord

        if prop_visible_dict.get(y_name, True) is True:
            sub_text = PropertyPaletteControlTextUtil.get_sub_text(ctrl_props.member_text, value_name, xyz_text, f"{sub_name}Y")

            palette_control_function(wpf_palette, y_name, ctrl_props, xyz_value.Y,
                                     PropertyPaletteGeometryControlService.__get_min_value(min_value, "Y"),
                                     PropertyPaletteGeometryControlService.__get_max_value(max_value, "Y"),
                                     PropertyPaletteControlTextData(xyz_row_name + ctrl_props.row_state_key, sub_text))

        #----------------- z coord

        if has_z_coord and  prop_visible_dict.get(z_name, True) is True:
            sub_text = PropertyPaletteControlTextUtil.get_sub_text(ctrl_props.member_text, value_name, xyz_text, f"{sub_name}Z")

            palette_control_function(wpf_palette, z_name, ctrl_props,
                                     cast(AllplanGeo.Point3D, xyz_value).Z,
                                     PropertyPaletteGeometryControlService.__get_min_value(min_value, "Y"),
                                     PropertyPaletteGeometryControlService.__get_max_value(max_value, "Y"),
                                     PropertyPaletteControlTextData(xyz_row_name + ctrl_props.row_state_key, sub_text))

    @staticmethod
    def __get_min_value(min_value : Any,
                        coord_name: str) -> float:
        """ get the minimal value

        Args:
            min_value:  minimal value
            coord_name: coordinate name

        Returns:
            minimal value
        """

        return min_value if isinstance(min_value, (float, int)) else getattr(min_value, coord_name)


    @staticmethod
    def __get_max_value(max_value : Any,
                        coord_name: str) -> float:
        """ get the maximal value

        Args:
            max_value:  maximal value
            coord_name: coordinate name

        Returns:
            minimal value
        """

        return max_value if isinstance(max_value, (float, int)) else getattr(max_value, coord_name)
