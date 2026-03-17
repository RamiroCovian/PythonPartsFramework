""" implementation of the CommonProperties value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties
from CommonPropertiesUtil import CommonPropertiesUtil

from Utilities.ConditionUtil import ConditionUtil
from Utilities.GeneralConstants import GeneralConstants

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.StringToValueUtil import StringToValueUtil
from ..ValueTypeUtils.ValueToStringUtil import ValueToStringUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class CommonPropertiesImpl(ParameterPropertyValueType):
    """ implementation of the CommonProperties value type
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

        prop.is_modified = True

        if GeneralConstants.SUB_NAME_SEPARATOR not in name:
            return ParameterPropertyListUtil.set_item_value(prop, name, value)

        com_prop = cast(AllplanBaseEle.CommonProperties, ParameterPropertyListUtil.get_item_value(prop, name))

        sub_name = name.split(".")[1]

        color_by_layer  = com_prop.ColorByLayer
        pen_by_layer    = com_prop.PenByLayer
        stroke_by_layer = com_prop.StrokeByLayer
        help_constr     = com_prop.HelpConstruction
        layer           = com_prop.Layer

        setattr(com_prop, sub_name, value)

        if not (update_palette := CommonPropertiesUtil.update_by_layer(com_prop)):
            update_palette = color_by_layer  != com_prop.ColorByLayer  or \
                             pen_by_layer    != com_prop.PenByLayer    or \
                             stroke_by_layer != com_prop.StrokeByLayer or \
                             layer           != com_prop.Layer and layer == 0 or com_prop.Layer == 0


        #----------------- check for constraint property update

        if help_constr != com_prop.HelpConstruction:
            if com_prop.HelpConstruction:
                com_prop.Color = 11

            elif not com_prop.ColorByLayer:
                com_prop.Color = AllplanSettings.AllplanGlobalSettings.GetCurrentColorId()

            update_palette = True

        if com_prop.HelpConstruction:
            com_prop.Color = 11

            return update_palette

        if color_by_layer and not com_prop.ColorByLayer:
            com_prop.Color = AllplanSettings.AllplanGlobalSettings.GetCurrentColorId()

            return True

        if pen_by_layer and not com_prop.PenByLayer:
            com_prop.Pen = AllplanSettings.AllplanGlobalSettings.GetCurrentPenId()

            return True

        if stroke_by_layer and not com_prop.StrokeByLayer:
            com_prop.Stroke = AllplanSettings.AllplanGlobalSettings.GetCurrentStrokeId()

            return True

        return update_palette


    @staticmethod
    def to_string(value: AllplanBaseEle.CommonProperties) -> str:
        """ convert the common properties to a string

        Args:
            value: common properties

        Returns:
            common properties as string
        """

        return ValueToStringUtil.trim_value_string(str(value))


    @staticmethod
    def get_value(value_str: str) -> AllplanBaseEle.CommonProperties:
        """ get the common properties from a string

        Args:
            value_str: common properties string

        Returns:
            common properties from the string
        """

        def get_common_properties(value_str: str) -> AllplanBaseEle.CommonProperties:
            """ get the common properties from the value string

            Args:
                value_str: value string

            Returns:
                common properties
            """

            com_prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()

            if not value_str:
                return com_prop

            com_prop.Pen    = StringToValueUtil.get_property_int(value_str, "Pen", 1)
            com_prop.Stroke = StringToValueUtil.get_property_int(value_str, "Stroke", 1)
            com_prop.Color  = StringToValueUtil.get_property_int(value_str, "Color", 1)
            com_prop.Layer  = StringToValueUtil.get_property_int(value_str, "Layer", 0)

            com_prop.PenByLayer       = StringToValueUtil.get_property_bool(value_str, "PenByLayer", False)
            com_prop.StrokeByLayer    = StringToValueUtil.get_property_bool(value_str, "StrokeByLayer", False)
            com_prop.ColorByLayer     = StringToValueUtil.get_property_bool(value_str, "ColorByLayer", False)
            com_prop.HelpConstruction = StringToValueUtil.get_property_bool(value_str, "HelpConstruction", False)
            com_prop.DrawOrder        = StringToValueUtil.get_property_int(value_str, "DrawOrder", 0)

            return com_prop

        return BaseStringToValueConverter.to_value_by_type_converter(get_common_properties, value_str)


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

        text = f"{ctrl_props.text} " if ctrl_props.text else ""

        index_name = f" {ctrl_props.row_name}" if ctrl_props.row_name and not text else ""

        pen_str         , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_PEN")
        stroke_str      , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_LINETYPE")
        color_str       , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_COLOR")
        layer_str       , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_LAYER")
        help_constr_str , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_HELPCONSTRUCTION")
        draw_order_str  , _ = prop_pal_ctrl_service.global_str_table.get_entry("e_DRAW_ORDER")

        enabled = prop_pal_ctrl_service.is_control_enabled(ctrl_props)

        com_prop = cast(AllplanBaseEle.CommonProperties, prop.value)

        layer = com_prop.Layer

        prop_visible_dict = ConditionUtil.get_condition_dict(ctrl_props.visible_condition, prop.name, prop_pal_ctrl_service.param_dict)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.PenByLayer",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddCheckboxValue, prop, ctrl_props, "PenByLayer",
                                                  text + pen_str + index_name,
                                                  enabled and not com_prop.HelpConstruction and layer != 0)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.Pen",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddPenValue, prop, ctrl_props, "Pen",
                                                  text + pen_str + index_name,
                                                  enabled and not com_prop.PenByLayer and not com_prop.HelpConstruction)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.StrokeByLayer",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddCheckboxValue, prop, ctrl_props, "StrokeByLayer",
                                                  text + stroke_str + index_name,
                                                  enabled and not com_prop.HelpConstruction and layer != 0)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.Stroke",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddStroke, prop, ctrl_props, "Stroke",
                                                  text + stroke_str + index_name,
                                                  enabled and not com_prop.StrokeByLayer and not com_prop.HelpConstruction)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.ColorByLayer",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddCheckboxValue, prop, ctrl_props, "ColorByLayer",
                                                  text + color_str + index_name,
                                                  enabled and not com_prop.HelpConstruction and layer != 0)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.Color",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddColorValue, prop, ctrl_props, "Color",
                                                  text + color_str + index_name,
                                                  enabled and not com_prop.ColorByLayer and not com_prop.HelpConstruction)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.Layer",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddLayer, prop, ctrl_props, "Layer",
                                                  text + layer_str + index_name, True)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.HelpConstruction",  prop_visible_dict):
            prop_pal_ctrl_service.add_sub_control(wpf_palette.AddCheckboxValue, prop, ctrl_props, "HelpConstruction",
                                                  text + help_constr_str + index_name, True)

        if ParameterPropertyValueType.is_visible(f"{prop.name}.DrawOrder",  prop_visible_dict):
            draw_order_ctrl_props = ctrl_props.deep_copy()
            draw_order_ctrl_props.as_slider = True

            prop_pal_ctrl_service.add_int_edit_control(wpf_palette, f"{prop.name}.DrawOrder",  draw_order_ctrl_props,
                                                       prop.value.DrawOrder, -15, 15, "", text + draw_order_str + index_name)
