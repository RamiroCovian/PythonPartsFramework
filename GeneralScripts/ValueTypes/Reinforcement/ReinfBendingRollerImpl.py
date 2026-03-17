""" implementation of the ReinfBendingRoller value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Reinforcement as AllplanReinf

from ControlProperties import ControlProperties

import ParameterProperty

from Utilities.GeneralConstants import GeneralConstants

from ..BaseFloatImpl import BaseFloatImpl
from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinfBendingRollerImpl(BaseFloatImpl):
    """ implementation of the ReinfBendingRoller value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[float] | float):
        """ get the bending roller from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if value_str == GeneralConstants.USE_CURRENT_RESOURCE_VALUE:
            return AllplanReinf.ReinforcementSettings.GetBendingRoller()

        return BaseStringToValueConverter.to_float(value_str)

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty.ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the ReinfBendingRoller edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_control(wpf_palette.AddBendingRollerValue, prop, ctrl_props, float(prop.value))
