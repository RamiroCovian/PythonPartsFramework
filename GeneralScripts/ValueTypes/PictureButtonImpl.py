""" implementation of the PictureButton value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pathlib

import NemAll_Python_Palette as AllplanPalette

from StringEvaluate import StringEvaluate

from .BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class PictureButtonImpl(BaseStrImpl):
    """ implementation of the PictureButton value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add a picture button list to palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        picture_path = prop.value if pathlib.Path(prop.value).drive else f"{prop_pal_ctrl_service.picture_path}\\{prop.value}"

        event_id = StringEvaluate.eval_constants(ctrl_props.event_id, prop_pal_ctrl_service.param_dict)

        wpf_palette.AddPictureButton(ctrl_props.text, "", picture_path,
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
