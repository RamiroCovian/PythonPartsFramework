""" implementation of the ReinforcementShapeBarProperties value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Reinforcement as AllplanReinf

from ControlProperties import ControlProperties

from Utilities.ConditionUtil import ConditionUtil

from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties

from ..BaseIntImpl import BaseIntImpl
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.StringToValueUtil import StringToValueUtil
from ..ValueTypeUtils.ValueToStringUtil import ValueToStringUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinforcementShapeBarPropertiesImpl(BaseIntImpl):
    """ implementation of the ReinforcementShapeBarProperties value type
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

        match name.split(".", 1)[-1]:
            case "ConcreteGrade":
                prop.value.concrete_grade = value

            case "BarDiameter":
                prop.value.diameter = float(value)

            case "SteelGrade":
                prop.value.steel_grade = value

            case "BendingRoller":
                prop.value.bending_roller = float(value)

        return False

    @staticmethod
    def to_string(value: ReinforcementShapeProperties) -> str:
        """ convert the shape bar properties to a string

        Args:
            value: new value

        Returns:
            shape bar properties as string
        """

        return ValueToStringUtil.trim_value_string(value.to_reinforcementshapebarproperties_string())


    @staticmethod
    def get_value(value_str: str) -> ReinforcementShapeProperties:
        """ get the shape bar properties from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        diameter       = StringToValueUtil.get_property_float(value_str, "Diameter", "10.0")
        bending_roller = StringToValueUtil.get_property_float(value_str, "BendingRoller", "4.0")
        steel_grade    = StringToValueUtil.get_property_int(value_str, "SteelGrade", 4)
        concrete_grade = StringToValueUtil.get_property_int(value_str, "ConcreteGrade", 4)

        return ReinforcementShapeProperties.rebar(diameter, bending_roller, steel_grade, concrete_grade,
                                                  AllplanReinf.BendingShapeType.Stirrup)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the ReinforcementShapeBarProperties edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_visible_dict = ConditionUtil.get_condition_dict(ctrl_props.visible_condition, prop.name, prop_pal_ctrl_service.param_dict)

        value      = prop.value
        value_name = ctrl_props.value_name
        str_table  = prop_pal_ctrl_service.global_str_table
        page_index = prop_pal_ctrl_service.page_index

        if ParameterPropertyValueType.is_visible(f"{value_name}.ConcreteGrade",  prop_visible_dict):
            wpf_palette.AddConcreteGrade(str_table.get_entry("e_CONCRETE_GRADE")[0],
                                         f"{value_name}.ConcreteGrade", value.concrete_grade,
                                         page_index, ctrl_props.expander_name, "",
                                         prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                         ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if ParameterPropertyValueType.is_visible(f"{value_name}.SteelGrade",  prop_visible_dict):
            wpf_palette.AddSteelGrade(str_table.get_entry("e_STEEL_GRADE")[0],
                                      f"{value_name}.SteelGrade", value.steel_grade,
                                      page_index, ctrl_props.expander_name, "",
                                      prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                      ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if ParameterPropertyValueType.is_visible(f"{value_name}.BarDiameter",  prop_visible_dict):
            wpf_palette.AddBarDiameter(str_table.get_entry("e_BAR_DIAMETER")[0],
                                       f"{value_name}.BarDiameter", value.diameter,
                                       page_index, ctrl_props.expander_name, "",
                                       prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                       ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)

        if ParameterPropertyValueType.is_visible(f"{value_name}.BendingRoller",  prop_visible_dict):
            wpf_palette.AddBendingRollerValue(str_table.get_entry("e_BENDING_ROLLER")[0],
                                              f"{value_name}.BendingRoller", value.bending_roller,
                                              page_index, ctrl_props.expander_name, "",
                                              prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                              ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)
