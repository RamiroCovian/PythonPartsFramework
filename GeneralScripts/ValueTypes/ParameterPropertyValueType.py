""" implementation of the value type constants
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import abc

import NemAll_Python_Palette as AllplanPalette

from .ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil
from .ValueTypeUtils.ValueType import ValueType

from .ParameterPropertyValueValidator import ParameterPropertyValueValidator

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from BuildingElementStringTable import BuildingElementStringTable
    from ControlProperties import ControlProperties
    from ParameterProperty import ParameterProperty

    from ValueTypes.ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ParameterPropertyValueType(ValueType, ParameterPropertyValueValidator):
    """ definition of the parameter property value type
    """

    _empty_row_counter = 0

    _build_ele_str_table: (BuildingElementStringTable | None) = None

    def __new__(cls,
                value_type: ValueType) -> ParameterPropertyValueType:
        """ initialize

        Args:
            value_type: value type

        Returns:
            created object
        """

        instance = cast(ValueType, super()).__new__(cls, value_type.value_type_impl, str(value_type), value_type.has_impl,
                                                    value_type.is_persistent)

        return cast(ParameterPropertyValueType, instance)

    def __init__(self,
                 value_type: ValueType):
        """ initialize

        Args:
            value_type: value type
        """

        super().__init__(value_type.value_type_impl, str(value_type), value_type.has_impl, value_type.is_persistent)

    @classmethod
    def set_property_value(cls,
                           prop : ParameterProperty,
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

        return ParameterPropertyListUtil.set_item_value(prop, name, value, cls.get_value)

    @staticmethod
    @abc.abstractmethod
    def to_string(value: Any) -> str:
        """ convert the data to a string

        Args:
            value: new value

        Returns:
            values as string
        """

    def to_string_extend(self,
                         value               : Any,
                         _attribute_id       : (int | list[int]),
                         _build_ele_str_table: (BuildingElementStringTable | None)) -> (str | None):
        """ convert the data to a string by an extended functionality

        Args:
            value:                new value
            _attribute_id:        attribute id
            _build_ele_str_table: string table of the building element

        Returns:
            values as string
        """

        return self.to_string(value)

    @staticmethod
    @abc.abstractmethod
    def get_value(value_str: str) -> Any:
        """ get the value from a string

        Args:
            value_str: value string

        Returns:
            value from the string
        """

    def get_value_extend(self,
                         value_str           : str,
                         _attribute_id       : (int | list[int]),
                         _build_ele_str_table: (BuildingElementStringTable | None)) -> Any:
        """ get the value from a string by an extended functionality

        Args:
            value_str:            value string
            _attribute_id:        attribute id
            _build_ele_str_table: string table of the building element

        Returns:
            value from the string
        """

        return self.get_value(value_str)

    @staticmethod
    @abc.abstractmethod
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

    def is_tuple_type(self,                                                     # pylint: disable=no-self-use
                      _is_named_tuple: bool = False) -> bool:
        """ test for tuple value type

        Args:
            _is_named_tuple: test from named tuple

        Returns:
            tuple type state
        """

        return False

    def is_combobox_type(self) -> bool:
        """ test for combobox value type

        Returns:
            union type state
        """

        return "combobox(" in self      # pylint: disable=magic-value-comparison

    @staticmethod
    def init_empty_row_name_counter():
        """ initialize the empty row counter
        """

        ParameterPropertyValueType._empty_row_counter = 0

    @staticmethod
    def get_empty_row_counter() -> int:
        """ increase and get the empty row counter

        Returns:
            empty row counter
        """

        ParameterPropertyValueType._empty_row_counter += 1

        return ParameterPropertyValueType._empty_row_counter

    @staticmethod
    def is_visible(name        : str,
                   visible_dict: dict[str, bool]) -> bool:
        """ check for a visible property

        Args:
            name:         name of the modified property
            visible_dict: visible dictionary

        Returns:
                property is visible state
        """

        if not visible_dict:
            return True

        return name not in visible_dict or visible_dict[name]


    @staticmethod
    def update_enable_by_constraint(build_ele : BuildingElement,
                                    prop      : ParameterProperty,
                                    ctrl_props: ControlProperties):
        """ update the enable state by a constraint: overload this function if necessary

        Args:
            build_ele:  building element with the parameter properties
            prop:       parameter property to update
            ctrl_props: control properties
        """


    @staticmethod
    def is_default_init_by_constraint(_build_ele : BuildingElement,
                                      _ctrl_props: ControlProperties) -> bool:
        """ check, whether the default value must be initialized by the constraint

        Args:
            _build_ele:  building element with the parameter properties
            _ctrl_props: control properties

        Returns:
            default init by the constraint state
        """

        return False


    @staticmethod
    def get_additonal_data(prop     : ParameterProperty,
                           value_str: str):
        """ get additional data from the value string

        Args:
            prop:      property
            value_str: value string
        """


    @staticmethod
    def value_to_unit_string(value: Any) -> str:
        """ convert the value to the current unit value

        Args:
            value: value

        Returns:
            unit value as string
        """

        return str(value)


    def string_to_unit_value(self,
                             value_str: str) -> Any:
        """ convert the string to the unit value

        Args:
            value_str: value string

        Returns:
            unit value as string
        """

        return self.get_value(value_str)


    @staticmethod
    def get_default_control_width() -> int:
        """ get the default control width

        Returns:
            default control width
        """

        return 30
