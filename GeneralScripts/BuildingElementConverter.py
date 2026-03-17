""" Script for BuildingElement
"""

# pylint: disable=not-callable

from __future__ import annotations

from typing import TYPE_CHECKING

import traceback

import NemAll_Python_Utility as AllplanUtil

from BuildingElementConverterUtil import BuildingElementConverterUtil
from BuildingElementListUtil import BuildingElementListUtil
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementTupleUtil import BuildingElementTupleUtil
from ParameterProperty import ParameterProperty
from StringToValueConverter import StringToValueConverter
from ValueToStringConverter import ValueToStringConverter

if TYPE_CHECKING:
    from BuildingElement import BuildingElement

class BuildingElementConverter():
    """ Definition of class BuildingElementConverter
    """

    @staticmethod
    def get_params_list(build_ele              : BuildingElement,
                        persistence            : ParameterProperty.Persistent = ParameterProperty.Persistent.MODEL,
                        exclude_parameter_names: (list[str] | None) = None) -> list[str]:
        """ Reads params from dictionary, sets the param list

        Args:
            build_ele:               building element with the parameter properties
            persistence:             persistence type
            exclude_parameter_names: excluded parameter names

        Returns:
            list with the parameter string
        """

        param_list = ["__ElementID=" + build_ele.element_id + "\n"]

        for name, _ in build_ele.get_parameter_dict().items():
            if exclude_parameter_names and name in exclude_parameter_names:
                continue

            if not (prop := build_ele.get_property(name)):
                continue

            if persistence == ParameterProperty.Persistent.MODEL_AND_FAVORITE and build_ele.is_interactor and \
               prop.persistent not in (ParameterProperty.Persistent.FAVORITE, \
                                       ParameterProperty.Persistent.MODEL_AND_FAVORITE):
                continue

            BuildingElementConverter.add_parameter_property_to_params_list(prop, param_list,
                                                                           build_ele.get_string_tables()[0],
                                                                           persistence)

        return param_list


    @staticmethod
    def add_parameter_property_to_params_list(param_prop : ParameterProperty,
                                              param_list : list[str],
                                              str_table  : BuildingElementStringTable,
                                              persistence: ParameterProperty.Persistent = ParameterProperty.Persistent.MODEL):
        """ add a parameter property to the parameter list

        Args:
            param_prop:  parameter property
            param_list:  parameter list
            str_table:   string table
            persistence: persistence state
        """

        if (param_prop.persistent == ParameterProperty.Persistent.NO) or \
           (param_prop.persistent == ParameterProperty.Persistent.MODEL    and persistence == ParameterProperty.Persistent.FAVORITE) or \
           (param_prop.persistent == ParameterProperty.Persistent.FAVORITE and persistence == ParameterProperty.Persistent.MODEL):
            return

        value_type = param_prop.value_type

        if isinstance(param_prop.value, list):
            value_str = BuildingElementListUtil.get_list_params(param_prop.value, value_type, str_table, param_prop.attribute_id)

        elif value_type.find("tuple(") != -1:
            value_str = BuildingElementTupleUtil.get_tuple_params(param_prop.value, str_table)

        else:
            value_str = ValueToStringConverter.to_string(param_prop, str_table)

        name = param_prop.name if not param_prop.exclude_identical else "<" + param_prop.name + ">"

        param_list.append(name + "=" + value_str + "\n")


    @staticmethod
    def read_from_list(build_ele : BuildingElement,
                       input_list: list[str],
                       persistence = ParameterProperty.Persistent.MODEL):
        """ Read the properties from a list

        Args:
            input_list     list with properties
            persistence    persistence state for the reading of the data
        """

        build_ele_str_table = build_ele.get_string_tables()[0]

        name       = ""
        value_type = ""
        value_str  = ""

        try:
            for line in input_list:
                data = line.partition("=")

                name      = data[0].strip(" <>")
                value_str = data[2].strip()

                if not (prop := build_ele.get_property(name)):
                    continue

                if prop.persistent == ParameterProperty.Persistent.NO or \
                   prop.persistent == ParameterProperty.Persistent.MODEL and persistence == ParameterProperty.Persistent.MODEL_AND_FAVORITE:
                    continue

                value = prop.value

                object_type = str(type(value))
                value_type  = prop.value_type

                if object_type == "<class 'list'>"  or  value_str.find("[") == 0:
                    prop.value = BuildingElementListUtil.get_list_element(value_str, value_type, prop.named_tuple_def,
                                                                          prop.attribute_id)

                elif value_type.find("tuple(") != -1:
                    prop.value = BuildingElementTupleUtil.get_tuple_element(value_str.lstrip("(").rstrip(")"),
                                                                                  value_type, prop.named_tuple_def)

                else:
                    if (conv := BuildingElementConverterUtil.get_string_to_value_converter(value_type)):
                        prop.value = conv(value_str)

                    else:
                        prop.value = StringToValueConverter.get_value(prop.value_type, value_str, build_ele_str_table, prop.attribute_id)

        except (IndexError, ValueError):
            msg_text = "Exception during read of the favorite data: name = " + name + " / type = " + \
                        value_type + " / value = " + value_str + " !!!"

            print(msg_text)
            print()

            traceback.print_exc()

            AllplanUtil.ShowMessageBox(msg_text, AllplanUtil.MB_OK)

            return
