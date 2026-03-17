""" General script for parameter properties
"""

# pylint: disable="too-many-instance-attributes"

from __future__ import annotations

from enum import IntEnum

from typing import Any

import enum

from collections import namedtuple

from ValueTypes.ParameterPropertyValueType import ParameterPropertyValueType
from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes
from ValueTypes.ParameterPropertyValueTypesImpl import ParameterPropertyValueTypesImpl
from ValueTypes.ValueTypeUtils.ComboBoxValueListUtil import ComboBoxValueListUtil
from ValueTypes.ValueTypeUtils.ValueType import ValueType

NamedTupleDef = namedtuple("NamedTupleDef", ["typename" ,"field_names"])

class ParameterProperty:
    """ Definition of class ParameterProperty
    """

    class Persistent(enum.IntEnum):
        """ Definition of class PersistentType
        """

        NO                 = 0
        MODEL_AND_FAVORITE = 1
        MODEL              = 2
        FAVORITE           = 3


    class InputType(enum.IntEnum):
        """ Class used to define the type of inputs
        """

        MANDATORY = 0
        OPTIONAL  = 1


    def __init__(self):
        """ initialize """

        self.__name              : str                            = ''
        self.__group_name        : str                            = ""
        self.__value_type        : ParameterPropertyValueType     = ParameterPropertyValueType(ValueType("", "", False, False))
        self.__value             : Any                            = 0.
        self.__selected_value    : Any                            = 0
        self.__attribute_id_str  : str                            = "0"
        self.__persistent        : ParameterProperty.Persistent   = ParameterProperty.Persistent.NO
        self.__input_type        : ParameterProperty.InputType    = ParameterProperty.InputType.OPTIONAL
        self.__dimensions        : str                            = ""
        self.__list_state        : int                            = 0
        self.__list_reverse      : bool                           = False
        self.__list_squeeze      : bool                           = True
        self.__is_modified       : bool                           = False
        self.__exclude_identical : bool                           = False
        self.__named_tuple_def   : (NamedTupleDef | None)         = None
        self.__enum_dict         : dict[int, IntEnum]             = {}
        self.__value_list_util   : (ComboBoxValueListUtil | None) = None

    def __repr__(self) -> str:
        """ Print class information

        Returns:
            parameter property as string
        """
        return f"<{self.__class__.__name__}>\n" \
               f"name:              {self.__name}\n" \
               f"group_name:        {self.__group_name}\n" \
               f"value_type:        {self.__value_type}\n" \
               f"value:             {self.__value}\n" \
               f"selected_value:    {self.__selected_value}\n" \
               f"attribute_id_str:  {self.__attribute_id_str}\n" \
               f"persistent:        Persistent.{str(self.__persistent.name)}\n" \
               f"input_type:        InputType.{str(self.__input_type.name)}\n" \
               f"dimension:         {self.__dimensions}\n" \
               f"list state:        {self.__list_state}\n" \
               f"list reverse:      {self.__list_reverse}\n" \
               f"list squeeze:      {self.__list_squeeze}\n" \
               f"is_modified:       {self.__is_modified}\n" \
               f"exclude_identical: {self.__exclude_identical}\n" \
               f"named_tuple_def:   {self.__named_tuple_def}\n" \
               f"enum_dict:         {self.__enum_dict}\n" \
               f"value_list_util:   {str(self.__value_list_util)}\n"

    @property
    def name(self) -> str:
        """ Get the name of the property

        Returns:
            name of the property.
        """
        return self.__name

    @name.setter
    def name(self,
             name: str):
        """ Set the name of the property

        Args:
            name: name of the modified property
        """
        self.__name = name

    @property
    def group_name(self) -> str:
        """ Get the group name of the property

        Returns:
            name of the property.
        """
        return self.__group_name

    @group_name.setter
    def group_name(self,
                   name: str):
        """ Set the group name of the property

        Args:
            name: name of the modified property
        """
        self.__group_name = name

    @property
    def value(self) -> Any:
        """ Get the value of the property

        Returns:
            value of the property.
        """
        return self.__value

    @value.setter
    def value(self,
              value: Any):
        """ Set the value of the property

        Args:
            value: new value
        """
        self.__value       = value
        self.__is_modified = True

    @property
    def selected_value(self) -> Any:
        """ Get the selected value of the property

        Returns:
            value of the property.
        """
        return self.__selected_value

    @selected_value.setter
    def selected_value(self,
                       value: Any):
        """ Set the selected value of the property

        Args:
            value: new value
        """
        self.__selected_value = value

    @property
    def attribute_id(self) -> (int | list[int]):
        """ Get the attribute id of the property

        Returns:
            attribute id of the property.
        """
        return eval(self.__attribute_id_str)

    @attribute_id.setter
    def attribute_id(self,
                     attribute_id: int):
        """ Set the attribute id of the property

        Args:
            attribute_id: attribute ID
        """

        self.__attribute_id_str = str(attribute_id)


    @property
    def attribute_id_str(self) -> str:
        """ Get the attribute id string of the property

        Returns:
            attribute id of the property.
        """
        return self.__attribute_id_str

    @attribute_id_str.setter
    def attribute_id_str(self,
                         attribute_id_str: str):
        """ Set the attribute id string of the property

        Args:
            attribute_id_str: new attribute id
        """
        self.__attribute_id_str = attribute_id_str

    @property
    def value_type(self) -> ParameterPropertyValueType:
        """ Get the value type of the property

        Returns:
            value type.
        """
        return self.__value_type

    @value_type.setter
    def value_type(self,
                   value_type: str):
        """ Set the value type of the property

        Args:
            value_type: new value type.
        """
        self.__value_type = ParameterPropertyValueTypesImpl.get_value_type_impl(value_type)

    @property
    def persistent(self) -> Persistent:
        """ Get the persistent state of the property

        Returns:
            persistent state (save in the PythonPart data).
        """
        return self.__persistent

    @persistent.setter
    def persistent(self,
                   persistent: Persistent):
        """ Set the persistent state of the property

        Args:
            persistent: property is persistent (save in the PythonPart data).
        """
        self.__persistent = persistent

    @property
    def input_type(self) -> InputType:
        """  Getter for input type parameter

        Returns:
            Input type of parameter property.
        """
        return self.__input_type

    @input_type.setter
    def input_type(self,
                   input_type: InputType):
        """Setter to input type property

        Args:
            input_type (InputType): Type of input
        """
        self.__input_type = input_type

    @property
    def dimensions(self) -> str:
        """ Get the dimensions of the property in case of a list

        Returns:
            dimensions.
        """
        return self.__dimensions

    @dimensions.setter
    def dimensions(self,
                   dimensions: str):
        """ Set the dimensions of the property in case of a list

        Args:
            dimensions: list dimensions.
        """
        self.__dimensions = dimensions

    @property
    def list_state(self) -> int:
        """ Get the list as block state

        Returns:
            returns
        """

        return self.__list_state

    @list_state.setter
    def list_state(self,
                   list_state: int):
        """ Set the list as block state

        Args:
            list_state: description
        """

        self.__list_state = list_state

    @property
    def list_reverse(self) -> bool:
        """ Get the list reverse state

        Returns:
            returns
        """

        return self.__list_reverse

    @list_reverse.setter
    def list_reverse(self,
                     is_list_reverse: bool):
        """ Set the list reverse state

        Args:
            is_list_reverse: description
        """

        self.__list_reverse = is_list_reverse

    @property
    def list_squeeze(self) -> bool:
        """ Get the list squeeze state

        Returns:
            returns
        """

        return self.__list_squeeze

    @list_squeeze.setter
    def list_squeeze(self,
                     is_list_squeeze: bool):
        """ Set the list squeeze state

        Args:
            is_list_squeeze: description
        """

        self.__list_squeeze = is_list_squeeze

    @property
    def is_modified(self) -> bool:
        """ Get the modified state

        Returns:
            returns
        """

        return self.__is_modified

    @is_modified.setter
    def is_modified(self,
                    is_modified: bool):
        """ Set the modified state

        Args:
            is_modified: description
        """

        self.__is_modified = is_modified

    def reset_modified(self):
        """ Reset the is_modified state
        """

        self.__is_modified = False

    @property
    def exclude_identical(self) -> bool:
        """ Get the exclude identical state

        If True, the parameter is not used for checking identical PythonParts

        Returns:
            returns
        """

        return self.__exclude_identical

    @exclude_identical.setter
    def exclude_identical(self,
                          exclude_identical: bool):
        """ Set the exclude identical state

        If True, the parameter is not used for checking identical PythonParts

        Args:
            exclude_identical: description
        """

        self.__exclude_identical = exclude_identical

    @property
    def named_tuple_def(self) -> (NamedTupleDef | None):
        """ Get the named tuple definition

        Returns:
            named tuple definition
        """

        return self.__named_tuple_def

    def set_named_tuple_def(self,
                            typename   : str,
                            field_names: list[str]):
        """ Set the named tuple definition

        Args:
            typename:    description
            field_names: description
        """

        self.__named_tuple_def = NamedTupleDef(typename, field_names)

    @property
    def enum_dict(self) -> dict[int, IntEnum]:
        """ Get the enumeration list for the input values

        Returns:
            enumeration list
        """

        return self.__enum_dict

    @enum_dict.setter
    def enum_dict(self,
                  enum_dict: dict[int, IntEnum]):
        """ Set the enumeration list for the input values

        Args:
            enum_dict: enumeration list for the input values
        """

        self.__enum_dict = enum_dict

    @property
    def value_list_util(self) -> (ComboBoxValueListUtil | None):
        """ Get the combo box value list utility

        Returns:
            combo box value list utility
        """

        return self.__value_list_util

    @value_list_util.setter
    def value_list_util(self,
                        value_list_util: (ComboBoxValueListUtil | None)):
        """ Set the combo box value list utility

        Args:
            value_list_util: combo box value list utility
        """

        self.__value_list_util = value_list_util

    def deep_copy(self) -> ParameterProperty:
        """ deep copy of the parameter values

        Returns:
            copied parameter property
        """

        prop = ParameterProperty()

        prop.name              = self.name
        prop.group_name        = self.group_name
        prop.value_type        = self.value_type
        prop.selected_value    = self.selected_value
        prop.persistent        = self.persistent
        prop.dimensions        = self.dimensions
        prop.list_state        = self.list_state
        prop.list_reverse      = self.list_reverse
        prop.list_squeeze      = self.list_squeeze
        prop.is_modified       = self.is_modified
        prop.exclude_identical = self.exclude_identical
        prop.enum_dict         = dict(self.enum_dict)
        prop.value_list_util   = self.value_list_util

        if self.named_tuple_def is not None:
            prop.set_named_tuple_def(*self.named_tuple_def)

        def copy_value(value: Any) -> Any:
            """ copy the value

            Args:
                value: new value

            Returns:
                copied value
            """

            if not value:
                return value

            if isinstance(value, list):
                return [copy_value(item) for item in value]

            if ParameterPropertyValueTypes.NAMED_TUPLE in self.value_type:
                if self.__named_tuple_def is not None:
                    return namedtuple(self.__named_tuple_def.typename, self.__named_tuple_def.field_names)(*value)

                return None

            if self.value_type in {ParameterPropertyValueTypes.REINFORCEMENT_SHAPE_BAR_PROPERTIES,
                                   ParameterPropertyValueTypes.REINFORCEMENT_SHAPE_MESH_PROPERTIES,
                                   ParameterPropertyValueTypes.ANY_VALUE_BY_TYPE}:
                return value.deep_copy()

            return type(value)(value)

        prop.value = copy_value(self.value)

        return prop
