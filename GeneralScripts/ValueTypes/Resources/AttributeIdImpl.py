""" implementation of the AttributeId value type
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties
from DocumentManager import DocumentManager

from Utilities.GeneralConstants import GeneralConstants

from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from ..ParameterPropertyValueType import ParameterPropertyValueType
from ..ValueTypeUtils.ValueToStringUtil import ValueToStringUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class AttributeIdImpl(ParameterPropertyValueType):
    """ implementation of the AttributeId value type
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           name : str,
                           value: Any) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            name:  name of the modified property
            value: new value

        Returns:
            update palette state
        """

        prop.is_modified = True

        if GeneralConstants.LIST_SEPARATOR_START in name:
            prop.value[int(name.split("[")[-1].split("]")[0])].value = value

        else:
            prop.value.value = value

        return False


    @staticmethod
    def to_string(value: int) -> str:
        """ convert the attribute ID to a string

        Args:
            value: new value

        Returns:
            attribute ID as string
        """

        return ValueToStringUtil.trim_value_string(str(value))


    @staticmethod
    def get_value(value_str: str) -> (int | list[int]):
        """ get the value from an attribute ID string

        Args:
            value_str: attribute ID string

        Returns:
            attribute ID(s) from the string
        """

        return BaseStringToValueConverter.to_int(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the control to the palette

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        old_value  = prop.value

        if not ctrl_props.row_name.strip():
            ctrl_props.row_name = ctrl_props.text

            if not ctrl_props.row_name:
                ctrl_props.row_name = " " * ParameterPropertyValueType.get_empty_row_counter()


        #----------------- create a text control

        if not prop.value:
            prop.value = prop_pal_ctrl_service.global_str_table.get_string("e_UNDEFINED", "undefined")
        else:
            doc = DocumentManager.get_instance().document

            prop.value = AllplanBaseEle.AttributeService.GetAttributeName(doc, prop.value)

        prop_pal_ctrl_service.add_text(wpf_palette, prop, ctrl_props)

        prop.value = old_value
