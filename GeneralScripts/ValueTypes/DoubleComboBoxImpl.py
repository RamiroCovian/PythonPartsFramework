""" implementation of the DoubleComboBox value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from .BaseFloatImpl import BaseFloatImpl
from .ComboBoxImpl import ComboBoxImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class DoubleComboBoxImpl(BaseFloatImpl, metaclass = ComboBoxImpl):
    """ implementation of the DoubleComboBox value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the double edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        if prop.value_list_util and not ctrl_props.row_name:
            ctrl_props.row_name = ctrl_props.text

        prop_pal_ctrl_service.add_combo_box(wpf_palette, prop, ctrl_props, AllplanPalette.PaletteValueType.DOUBLE)

        if prop.value_list_util:
            ComboBoxImpl.add_del_button(wpf_palette, prop, ctrl_props, prop_pal_ctrl_service)
