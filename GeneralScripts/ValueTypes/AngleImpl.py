""" implementation of the Angle value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Utility as AllplanUtil

from ControlProperties import ControlProperties

from .ParameterPropertyValueTypes import ParameterPropertyValueTypes

from .BaseFloatImpl import BaseFloatImpl

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class AngleImpl(BaseFloatImpl):
    """ implementation of the Angle value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the angle edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_edit_control(wpf_palette.AddAngleValue, prop, ctrl_props, prop.value)


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

        font_id_prop       = build_ele.get_property(constraints[0])
        font_emphasis_prop = build_ele.get_property(constraints[1]) if len(constraints) > 1 else None

        if font_id_prop and font_id_prop.value_type != ParameterPropertyValueTypes.FONT:
            font_id_prop, font_emphasis_prop = font_emphasis_prop, font_id_prop

        if font_id_prop is None or font_emphasis_prop is None:
            return


        #----------------- check for single value

        max_nem_font_id = AllplanSettings.FontProvider.Instance().GetNemFontIDs()[1][-1]

        if not isinstance(prop.value, list):
            if not font_emphasis_prop.value >> 1 & 1:
                prop.value                  = 90
                ctrl_props.enable_condition = "False"

                return

            if font_id_prop.value > max_nem_font_id:
                prop.value                  = 71
                ctrl_props.enable_condition = "False"

                return

            ctrl_props.enable_condition = "True"

            return


        #----------------- check for list

        enable_cond = "["

        for index, (font_id, font_emphasis) in enumerate(zip(font_id_prop.value, font_emphasis_prop.value)):
            if not font_emphasis >> 1 & 1:
                prop.value[index]  = 90
                enable_cond       += "False,"

                continue

            if font_id > max_nem_font_id:
                prop.value[index]  = 71
                enable_cond       += "False,"

                continue

            enable_cond += "True,"

        ctrl_props.enable_condition = f"{enable_cond[:-1]}][$list_row]"


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

        AngleImpl.update_by_constraint(build_ele, prop, ctrl_props, "")


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

        font_id_prop       = build_ele.get_property(constraints[0])
        font_emphasis_prop = build_ele.get_property(constraints[1]) if len(constraints) > 1 else None

        if font_id_prop and font_id_prop.value_type != ParameterPropertyValueTypes.FONT:
            font_id_prop, font_emphasis_prop = font_emphasis_prop, font_id_prop

        if font_id_prop is None:
            AllplanUtil.ShowMessageBox("No constraint found for 'Font'", AllplanUtil.MB_OK)

            return False

        if font_emphasis_prop is None or \
           font_emphasis_prop.value_type != ParameterPropertyValueTypes.FONTEMPHASIS:
            AllplanUtil.ShowMessageBox("No constraint found for 'FontEmphasis'", AllplanUtil.MB_OK)

            return False

        return True


    @staticmethod
    def get_min_value() -> float:
        """ get the minimal value

        Returns:
            get the minimal value
        """

        return -360.


    @staticmethod
    def get_max_value() -> float:
        """ get the maximal value

        Returns:
            get the maximal value
        """

        return 360.
