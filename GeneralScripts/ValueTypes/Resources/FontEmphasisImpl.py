""" implementation of the FontEmphasis buttons value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Utility as AllplanUtil

from ControlProperties import ControlProperties

from Utilities.ConditionUtil import ConditionUtil

from ..ParameterPropertyValueTypes import ParameterPropertyValueTypes

from ..BaseIntImpl import BaseIntImpl
from ..ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class FontEmphasisImpl(BaseIntImpl):
    """ implementation of the Font combobox value type
    """

    INDEX_FROM_NAME = {"Bold"      : 0,
                       "Italic"    : 1,
                       "Underline" : 2,
                       "CrossedOut": 3}

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

        prop_value = ParameterPropertyListUtil.get_item_value(prop, name)

        values = [prop_value >> index & 1 for index in range(4)]

        index = int(FontEmphasisImpl.INDEX_FROM_NAME[name.rsplit(".", 1)[-1]])

        values[index] = value

        value = 0

        for index in range(4):
            value += values[index] * 2 ** index

        ParameterPropertyListUtil.set_item_value(prop, name, value)

        return False

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the string edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        values = [prop.value >> index & 1 for index in range(4)]

        if not (row_name := ctrl_props.row_name):
            row_name = ctrl_props.text

        prop_visible_dict = ConditionUtil.get_condition_dict(ctrl_props.visible_condition, prop.name, prop_pal_ctrl_service.param_dict)

        if prop_visible_dict.get(f"{prop.name}.Bold",  True) is True:
            wpf_palette.AddPictureResourceToggleButton(ctrl_props.text, f"{prop.name}.Bold",  values[0],
                                                       "15179|15179", "0|1", "|",
                                                       prop_pal_ctrl_service.page_index,
                                                       ctrl_props.expander_name + ctrl_props.expander_state_key,
                                                       row_name + ctrl_props.row_state_key,
                                                       prop_pal_ctrl_service.is_sub_control_enabled(ctrl_props, "Bold"),
                                                       ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if prop_visible_dict.get(f"{prop.name}.Italic",  True) is True:
            wpf_palette.AddPictureResourceToggleButton(ctrl_props.text, f"{prop.name}.Italic",  values[1],
                                                       "15197|15197", "0|1", "|",
                                                       prop_pal_ctrl_service.page_index,
                                                       ctrl_props.expander_name + ctrl_props.expander_state_key,
                                                       row_name + ctrl_props.row_state_key,
                                                       prop_pal_ctrl_service.is_sub_control_enabled(ctrl_props, "Italic"),
                                                       ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if prop_visible_dict.get(f"{prop.name}.Underline",  True) is True:
            wpf_palette.AddPictureResourceToggleButton(ctrl_props.text, f"{prop.name}.Underline",  values[2],
                                                       "15205|15205", "0|1", "|",
                                                       prop_pal_ctrl_service.page_index,
                                                       ctrl_props.expander_name + ctrl_props.expander_state_key,
                                                       row_name + ctrl_props.row_state_key,
                                                       prop_pal_ctrl_service.is_sub_control_enabled(ctrl_props, "Underline"),
                                                       ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if prop_visible_dict.get(f"{prop.name}.CrossedOut",  True) is True:
            wpf_palette.AddPictureResourceToggleButton(ctrl_props.text, f"{prop.name}.CrossedOut",  values[3],
                                                       "15189|15189", "0|1", "|",
                                                       prop_pal_ctrl_service.page_index,
                                                       ctrl_props.expander_name + ctrl_props.expander_state_key,
                                                       row_name + ctrl_props.row_state_key,
                                                       prop_pal_ctrl_service.is_sub_control_enabled(ctrl_props, "CrossedOut"),
                                                       ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)


    @staticmethod
    def update_by_constraint(build_ele : BuildingElement,
                             prop      : ParameterProperty,
                             ctrl_props: ControlProperties,
                             _name     : str):
        """ update by a constraint

        Args:
            build_ele:  building element with the parameter properties
            prop:       parameter property to update
            ctrl_props: control properties
            _name:      name of the modified value
        """

        constraints = ctrl_props.constraint

        font_id_prop = build_ele.get_property(constraints[0])

        if font_id_prop is None or \
           font_id_prop.value_type != ParameterPropertyValueTypes.FONT:
            return


        #----------------- check for single value

        max_nem_font_id = AllplanSettings.FontProvider.Instance().GetNemFontIDs()[1][-1]

        if not isinstance(prop.value, list):
            enable = str(font_id_prop.value > max_nem_font_id)

            ctrl_props.enable_condition = ConditionUtil.modify_condition(f"{prop.name}.Bold",  ctrl_props.enable_condition,  enable)
            ctrl_props.enable_condition = ConditionUtil.modify_condition(f"{prop.name}.CrossedOut",  ctrl_props.enable_condition,  enable)

            return


        #----------------- check for list

        enable = "["

        for font_id in font_id_prop.value:
            enable += f"{font_id > max_nem_font_id},"

        enable = f"{enable[:-1]}][$list_row]"

        ctrl_props.enable_condition = ConditionUtil.modify_condition(f"{prop.name}.Bold",  ctrl_props.enable_condition,  enable)
        ctrl_props.enable_condition = ConditionUtil.modify_condition(f"{prop.name}.CrossedOut",  ctrl_props.enable_condition,  enable)


    @staticmethod
    def update_enable_by_constraint(build_ele : BuildingElement,
                                    prop      : ParameterProperty,
                                    ctrl_props: ControlProperties):
        """ update the enable state by a constraint

        Args:
            build_ele:  building element with the parameter properties
            prop:       parameter property to update
            ctrl_props: control properties
        """

        FontEmphasisImpl.update_by_constraint(build_ele, prop, ctrl_props, "")


    @staticmethod
    def is_default_init_by_constraint(build_ele : BuildingElement,
                                      ctrl_props: ControlProperties) -> bool:
        """ check, whether the default value must be initialized by the constraint

        Args:
            build_ele:  building element with the parameter properties
            ctrl_props: control properties

        Returns:
            default init by the constraint state
        """

        constraints = ctrl_props.constraint

        font_id_prop = build_ele.get_property(constraints[0])

        if font_id_prop is None or \
           font_id_prop.value_type != ParameterPropertyValueTypes.FONT:
            AllplanUtil.ShowMessageBox("No constraint found for 'Font'", AllplanUtil.MB_OK)

            return False

        return True
