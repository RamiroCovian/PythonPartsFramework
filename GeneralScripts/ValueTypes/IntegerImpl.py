""" implementation of the Integer value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from .BaseIntImpl import BaseIntImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class IntegerImpl(BaseIntImpl):
    """ implementation of the Integer value type
    """

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

        prop_pal_ctrl_service.add_edit_control(wpf_palette.AddIntValue, prop, ctrl_props, int(prop.value))
