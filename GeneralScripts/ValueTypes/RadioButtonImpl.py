""" implementation of the RadioButton value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from .ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class RadioButtonImpl(ParameterPropertyValueType):
    """ implementation of the RadioButton value type
    """

    @staticmethod
    def to_string(value: int) -> str:
        """ convert the radio button id to a string

        Args:
            value: new value

        Returns:
            radio button id as string
        """

        return str(value)


    @staticmethod
    def get_value(value_str: str) -> Any:
        """ get the radio button id from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        return BaseStringToValueConverter.to_auto(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the integer edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_radio_button_control(wpf_palette, prop.group_name, ctrl_props, prop.value, prop.selected_value)
