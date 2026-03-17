""" implementation of the Date value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from datetime import date

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil

from .BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class DateImpl(BaseStrImpl):
    """ implementation of the Date value type
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           name : str,
                           value: str) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            name:  name of the modified property
            value: new value

        Returns:
            update palette state
        """

        prop.is_modified = True

        if (date_value := BaseStringToValueConverter.string_to_date(value, True)) is None:
            return True

        ParameterPropertyListUtil.set_item_value(prop, name, date_value)

        return False

    @staticmethod
    def to_string(value: date) -> str:
        """ convert the date to a string

        Args:
            value: new value

        Returns:
            date as string
        """

        if value is None:
            return ""

        return f"date({value.year},{value.month},{value.day})"


    @staticmethod
    def get_value(value_str: str) -> (list[date] | date | None):
        """ get the date from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        return BaseStringToValueConverter.to_date(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the date edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        date_ctrl_props = ctrl_props.deep_copy()

        date_ctrl_props.row_name = ctrl_props.row_name if ctrl_props.row_name or not ctrl_props.value_dialog else ctrl_props.text

        prop_pal_ctrl_service.add_string_edit_control(wpf_palette, prop, date_ctrl_props,
                                                      BaseStringToValueConverter.date_to_string(cast(date, prop.value)))
