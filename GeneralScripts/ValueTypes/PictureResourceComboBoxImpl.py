""" implementation of the PictureResourceComboBoxImpl value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from StringEvaluate import StringEvaluate

from .BaseEnumListImpl import BaseEnumListImpl

if TYPE_CHECKING:
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class PictureResourceComboBoxImpl(BaseEnumListImpl):
    """ implementation of the PictureResourceComboBoxImpl value types
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add a picture resource combo box to palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        value_list = ctrl_props.value_list if prop.enum_dict else \
                     StringEvaluate.eval_constants(ctrl_props.value_list, prop_pal_ctrl_service.param_dict, int)

        wpf_palette.AddPictureResourceComboBox(ctrl_props.text, prop.name, int(prop.value),
                                               ctrl_props.value_list_2, value_list, ctrl_props.value_text_list,
                                               prop_pal_ctrl_service.page_index,
                                               ctrl_props.expander_name + ctrl_props.expander_state_key,
                                               ctrl_props.row_name + ctrl_props.row_state_key,
                                               prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                               ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)
