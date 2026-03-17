""" implementation of the Picture value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import os
import pathlib

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties
from StringEvaluate import StringEvaluate

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from .BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class PictureImpl(BaseStrImpl):
    """ implementation of the Picture value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[str] | str):
        """ get the picture from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        res = BaseStringToValueConverter.to_str(value_str)

        if isinstance(res, list):
            return res

        return res.lstrip()


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the string edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        if prop.value.isnumeric():
            picture_path = ""
            file_name    = prop.value

        elif "AllplanSettings" in prop.value:       # pylint: disable=magic-value-comparison
            picture_path = ""
            file_name    = str(int(eval(prop.value, StringEvaluate.get_allplan_api_param_dict())))

        elif not pathlib.Path(prop.value).drive:
            picture_path = prop_pal_ctrl_service.picture_path
            file_name    = prop.value

        else:
            picture_path = os.path.dirname(prop.value)
            file_name    = os.path.basename(prop.value)

        wpf_palette.AddPicture(ctrl_props.text.replace("\\n", "\n"), prop.name, file_name, picture_path,
                               prop.selected_value, prop_pal_ctrl_service.page_index,
                               ctrl_props.expander_name + ctrl_props.expander_state_key,
                               ctrl_props.row_name + ctrl_props.row_state_key)
