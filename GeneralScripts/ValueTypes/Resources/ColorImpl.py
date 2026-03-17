""" implementation of the Color value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from Utilities.GeneralConstants import GeneralConstants

from ..BaseIntImpl import BaseIntImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ColorImpl(BaseIntImpl):
    """ implementation of the Color value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[int] | int):
        """ get the color from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if value_str == GeneralConstants.USE_CURRENT_RESOURCE_VALUE:
            return AllplanSettings.AllplanGlobalSettings.GetCurrentColorId()

        return BaseIntImpl.get_value(value_str)


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

        prop_pal_ctrl_service.add_control(wpf_palette.AddColorValue, prop, ctrl_props, int(prop.value))
