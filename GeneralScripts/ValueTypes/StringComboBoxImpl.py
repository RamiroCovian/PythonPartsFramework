""" implementation of the StringComboBox value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties
from StringTableService import StringTableService

from Utilities.GeneralConstants import GeneralConstants

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from .BaseStrImpl import BaseStrImpl
from .ComboBoxImpl import ComboBoxImpl

if TYPE_CHECKING:
    from BuildingElementStringTable import BuildingElementStringTable
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class StringComboBoxImpl(BaseStrImpl, metaclass = ComboBoxImpl):
    """ implementation of the StringComboBox value type
    """

    @staticmethod
    def to_string(value: str) -> str:
        """ convert the string to a string

        Args:
            value: new value

        Returns:
            string as string
        """

        return value


    def to_string_extend(self,                          # pylint: disable=no-self-use
                         value              : str,
                         _attribute_id      : (int | list[int]),
                         build_ele_str_table: (BuildingElementStringTable | None)) -> str:
        """ convert the data to a string by an extended functionality

        Args:
            value:               new value
            _attribute_id:       attribute id
            build_ele_str_table: string table of the building element

        Returns:
            values as string
        """

        value_str = value

        if build_ele_str_table is None or \
           not build_ele_str_table.is_valid():
            return value_str

        if (text_id := build_ele_str_table.get_key(value_str)):
            value_str += f" {{{text_id}}}"

        return value_str


    def get_value_extend(self,                                          # pylint: disable=no-self-use
                         value_str          : str,
                         _attribute_id      : (int | list[int]),
                         build_ele_str_table: BuildingElementStringTable) -> (list[str] | str):
        """ get the string from a string

        Args:
            value_str:           value string
            _attribute_id:       attribute id
            build_ele_str_table: string table of the building element

        Returns:
            value from string
        """

        if build_ele_str_table is None:
            return BaseStringToValueConverter.to_str(value_str)

        if GeneralConstants.LIST_SEPARATOR_START not in value_str:
            return StringTableService.get_string_table_entry(build_ele_str_table, "", value_str)

        return [StringTableService.get_string_table_entry(build_ele_str_table, "", value)
                for value in BaseStringToValueConverter.to_str(value_str)]

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

        if prop.value_list_util and not ctrl_props.row_name:
            ctrl_props.row_name = ctrl_props.text

        prop_pal_ctrl_service.add_combo_box(wpf_palette, prop, ctrl_props, AllplanPalette.PaletteValueType.STRING)

        if prop.value_list_util:
            ComboBoxImpl.add_del_button(wpf_palette, prop, ctrl_props, prop_pal_ctrl_service)
