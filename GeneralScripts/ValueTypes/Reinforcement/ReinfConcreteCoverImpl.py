""" implementation of the ReinfConcreteCover value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

import ParameterProperty

from ..BaseFloatImpl import BaseFloatImpl

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinfConcreteCoverImpl(BaseFloatImpl):
    """ implementation of the ReinfConcreteCover value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty.ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the ReinfConcreteCover edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_control(wpf_palette.AddConcreteCoverValue, prop, ctrl_props, float(prop.value))
