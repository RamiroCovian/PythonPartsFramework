""" Script for BuildingElement
"""

from typing import Any

import re

from BuildingElementConverterUtil import BuildingElementConverterUtil
from BuildingElementTupleUtil import BuildingElementTupleUtil
from BuildingElementStringTable import BuildingElementStringTable
from ParameterProperty import NamedTupleDef
from StringToValueConverter import StringToValueConverter
from ValueToStringConverter import ValueToStringConverter

from Utilities.SplitUtil import SplitUtil

from ValueTypes.ParameterPropertyValueType import ParameterPropertyValueType
from ValueTypes.ParameterPropertyValueTypesImpl import ParameterPropertyValueTypesImpl

class BuildingElementListUtil():
    """ Definition of class BuildingElementListUtil
    """

    @staticmethod
    def get_list_params(list_ele    : list,
                        value_type  : ParameterPropertyValueType,
                        str_table   : BuildingElementStringTable,
                        attribute_id: (int | list[int]) = 0) -> str:
        """ Get the list parameter string from a list element

        Args:
            list_ele:     list element
            value_type:   value_type
            str_table:    string table
            attribute_id: attribute ID

        Returns:
            parameter string
        """

        list_str = ""

        if not isinstance(attribute_id, list):
            attribute_id = [attribute_id]

        attribute_id_count = len(attribute_id)

        for index, ele in enumerate(list_ele):
            if index:
                list_str += ";"

            object_type = str(type(ele))

            if value_type.is_tuple_type():
                list_str += BuildingElementTupleUtil.get_tuple_params(ele, str_table)

            elif object_type == "<class 'list'>":
                list_str += BuildingElementListUtil.get_list_params(ele, value_type, str_table)

            else:
                list_str += ValueToStringConverter.to_string_from_value(ele, ParameterPropertyValueTypesImpl.get_value_type_impl(value_type),
                                                                        str_table,
                                                                        attribute_id[index] if index < attribute_id_count else \
                                                                        attribute_id[0])

        return "[" + list_str + "]"


    @staticmethod
    def get_list_element(value_str      : str,
                         value_type     : ParameterPropertyValueType,
                         named_tuple_def: (NamedTupleDef | None),
                         attribute_id   : (int | list[int]) = 0) -> list[Any]:
        """ Convert the list string to a list element

        Args:
            value_str:       String with the values
            value_type:      Value type
            named_tuple_def: Definition of a named tuple
            attribute_id:    attribute ID

        Returns:
            element list
        """

        if not value_str or value_str =="[]":
            return []

        ele_list = []

        if value_str.startswith("["):
            value_str = value_str[1:]

        if value_str.endswith("]"):
            value_str = value_str[:-1]

        if value_str and value_str.startswith("[["):     # 3-dim list
            for ele_str in value_str.split("]];"):
                if not ele_str.endswith("]]"):
                    ele_str += "]]"

                ele_list.append(BuildingElementListUtil.get_list_element(ele_str, value_type, named_tuple_def))

            return ele_list

        if value_str and value_str.startswith("["):     # 2-dim list
            for ele_str in value_str.split("];"):
                ele_list.append(BuildingElementListUtil.get_list_element(ele_str, value_type, named_tuple_def))

            return ele_list

        if value_str.find(");(") != -1:           # list with tuples
            elements = SplitUtil.split_string_with_bracket_parts(value_str, ";")

        else:
            elements = value_str.split(";")

        if not isinstance(attribute_id, list):
            attribute_id = [attribute_id]


        #----------------- get the elements

        attribute_id_count = len(attribute_id)

        for index, ele_str in enumerate(elements):
            if ele_str.startswith("["):
                ele_list.append(BuildingElementListUtil.get_list_element(ele_str, value_type, named_tuple_def))

            elif value_type in {"string", "stringcombobox"}:
                if ele_str.endswith("}"):
                    value = re.sub(r"{\d+}", "", ele_str).strip()
                    ele_list.append(value)
                else:
                    ele_list.append(ele_str)

            elif value_type == "anyvaluebytype":
                ele_list.append(StringToValueConverter.get_value(ParameterPropertyValueTypesImpl.get_value_type_impl(value_type), ele_str))

            elif value_type.is_tuple_type():
                ele_list.append(BuildingElementTupleUtil.get_tuple_element(ele_str, value_type, named_tuple_def))

            elif ParameterPropertyValueTypesImpl.has_value_type_impl(value_type):
                ele_list.append(StringToValueConverter.get_value(value_type, ele_str,
                                                                 attribute_id = attribute_id[index] if index < attribute_id_count else \
                                                                                attribute_id[0]))

            else:
                name = ele_str.partition("(")[0]

                if (conv := BuildingElementConverterUtil.get_string_to_value_converter(name.lower())):
                    ele_list.append(conv(ele_str))
                else:
                    ele_list.append(eval(ele_str))

        return ele_list
