""" implementation of the CheckBox value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from .ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter
from .ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class CheckBoxImpl(ParameterPropertyValueType):
    """ implementation of the CheckBox value type
    """

    @staticmethod
    def to_string(value: Any) -> str:
        """ convert the attribute to a string

        Args:
            value: new value

        Returns:
            value as string
        """

        return "True" if value else "False"


    @staticmethod
    def get_value(value_str: Any) -> (list[int] | int):
        """ get the attribute from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        value_str = value_str.lower().replace("true", "1").replace("false", "0")

        return BaseStringToValueConverter.to_int(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the CheckBox control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_control(wpf_palette.AddCheckboxValue, prop, ctrl_props, int(prop.value))


    @staticmethod
    def update_by_constraint(build_ele : BuildingElement,
                             prop      : ParameterProperty,
                             ctrl_props: ControlProperties,
                             _name     : str):
        """ update by a constraint

        Args:
            build_ele:  building element with the parameter properties
            prop:       parameter property to update
            ctrl_props: control properties
            _name:      name of the modified value
        """

        constraints = ctrl_props.constraint

        constraint_prop = build_ele.get_property(constraints[0])

        if constraint_prop and constraint_prop.value:
            prop.value = False
