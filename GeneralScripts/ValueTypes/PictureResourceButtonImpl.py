""" implementation of the PictureResourceButton value type
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from StringEvaluate import StringEvaluate

from .BaseIntImpl import BaseIntImpl

if TYPE_CHECKING:
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class PictureResourceButtonImpl(BaseIntImpl):
    """ implementation of the PictureResourceButton value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[int] | int):
        """ get the picture id from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if "AllplanSettings" in value_str:   # pylint: disable=magic-value-comparison
            return int(eval(value_str, StringEvaluate.get_allplan_api_param_dict()))

        return BaseIntImpl.get_value(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add a picture resource button list to palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        event_id = StringEvaluate.eval_constants(ctrl_props.event_id, prop_pal_ctrl_service.param_dict)

        wpf_palette.AddPictureResourceButton(ctrl_props.text, prop.name, prop.value,
                                             int(event_id), prop_pal_ctrl_service.page_index,
                                             ctrl_props.expander_name + ctrl_props.expander_state_key,
                                             ctrl_props.row_name + ctrl_props.row_state_key,
                                             prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                             ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)


    @staticmethod
    def get_default_control_width() -> int:
        """ get the default control width

        Returns:
            default control width
        """

        return 22
