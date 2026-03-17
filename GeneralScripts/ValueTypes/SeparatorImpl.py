""" implementation of the Separator value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from .BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class SeparatorImpl(BaseStrImpl):
    """ implementation of the Separator value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       _prop                : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the string edit control

        Args:
            wpf_palette:           WPf palette
            _prop:                 parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        wpf_palette.AddSeparator(prop_pal_ctrl_service.page_index, ctrl_props.expander_name + ctrl_props.expander_state_key)
