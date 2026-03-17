""" implementation of the palette update validation
"""

from typing import Any

from dataclasses import dataclass

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from StringEvaluate import StringEvaluate

from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes
from ValueTypes.ValueTypeUtils.ValueListValidator import ValueListValidator

@dataclass
class DynamicDates():
    """ data class with the dynamic control data
    """

    value_list   : tuple[str, str] = ("", "")
    expander_name: str              = ""
    row_name     : str             = ""
    text         : str             = ""
    value_text   : str             = ""


class PaletteUpdateValidation():
    """ implementation of the palette update validation
    """

    def __init__(self,
                 build_ele           : BuildingElement,
                 build_ele_ctrl_props: BuildingElementControlProperties,
                 parameter_dict      : dict[str, Any]):
        """ initialize

        Args:
            build_ele:            building element with the parameter properties
            build_ele_ctrl_props: list with the building element control properties
            parameter_dict:       parameter dict
        """

        self.build_ele            = build_ele
        self.build_ele_ctrl_props = build_ele_ctrl_props

        self.dynamic_dates = self.__get_dynamic_data_state(parameter_dict)


    def __get_dynamic_data_state(self,
                                 parameter_dict: dict[str, Any]) -> list[DynamicDates]:
        """ get the current state of the dynamic palette data

        Args:
            parameter_dict: parameter dictionary

        Returns:
            dynamic dates
        """

        dynamic_dates: list[DynamicDates] = []

        build_ele = self.build_ele

        for ctrl_prop in self.build_ele_ctrl_props:
            dyn_data = DynamicDates()

            if (prop := build_ele.get_property(ctrl_prop.value_name)) is not None and \
                not prop.value_type.is_tuple_type() and prop.value_type.is_combobox_type():
                dyn_data.value_list = ValueListValidator.eval_value_list_formula(ctrl_prop.value_list,
                                                                                 str(prop.value), parameter_dict)

            max_list_count = self.__get_max_list_count_from_group(ctrl_prop.list_group_name)

            dyn_data.text          = self.__eval_text(ctrl_prop.text, max_list_count, parameter_dict)
            dyn_data.expander_name = self.__eval_text(ctrl_prop.expander_name, max_list_count, parameter_dict)
            dyn_data.row_name      = self.__eval_text(ctrl_prop.row_name, max_list_count, parameter_dict)

            if prop is not None and prop.value_type == ParameterPropertyValueTypes.TEXT:
                dyn_data.value_text = self.__eval_text(prop.value, max_list_count, parameter_dict)

            dynamic_dates.append(dyn_data)

        return dynamic_dates


    def check_palette_update(self,
                             name          : str,
                             parameter_dict: dict[str, Any]) -> bool:
        """ check for a palette update

        Args:
            name:           name of the modified property
            parameter_dict: parameter dictionary

        Returns:
            palette update state
        """

        if any(name in ctrl_props.value_index_name for ctrl_props in self.build_ele_ctrl_props):
            return True

        if any(name in ctrl_props.value_list_2 for ctrl_props in self.build_ele_ctrl_props):
            return True

        return self.__check_dynamic_data_state(parameter_dict)



    def __check_dynamic_data_state(self,
                                   parameter_dict: dict[str, Any]) -> bool:
        """ get the current state of the dynamic palette data

        Args:
            parameter_dict: parameter dictionary

        Returns:
            palette update state
        """

        build_ele = self.build_ele

        for ctrl_prop, dyn_data in zip(self.build_ele_ctrl_props, self.dynamic_dates):
            if (prop := build_ele.get_property(ctrl_prop.value_name)) is not None and \
                not prop.value_type.is_tuple_type() and prop.value_type.is_combobox_type():
                if ValueListValidator.eval_value_list_formula(ctrl_prop.value_list,
                                                                            str(prop.value), parameter_dict) != dyn_data:
                    return True

            max_list_count = self.__get_max_list_count_from_group(ctrl_prop.list_group_name)

            if StringEvaluate.is_text_from_script(ctrl_prop.text) and \
                self.__eval_text(ctrl_prop.text, max_list_count, parameter_dict) != dyn_data.text:
                return True

            if StringEvaluate.is_text_from_script(ctrl_prop.expander_name) and \
                self.__eval_text(ctrl_prop.expander_name, max_list_count, parameter_dict) != dyn_data.expander_name:
                return True

            if StringEvaluate.is_text_from_script(ctrl_prop.row_name) and \
                self.__eval_text(ctrl_prop.row_name, max_list_count, parameter_dict) != dyn_data.row_name:
                return True

            if prop is not None and prop.value_type == ParameterPropertyValueTypes.TEXT and \
               StringEvaluate.is_text_from_script(prop.value) and \
               self.__eval_text(prop.value, max_list_count, parameter_dict) != dyn_data.value_text:
                return True

        return False


    def __get_max_list_count_from_group(self,
                                        list_group_name: str) -> int:
        """ get the max list count in a list group

        Args:
            list_group_name: list group name

        Returns:
            list group count
        """

        if not list_group_name:
            return 1

        build_ele = self.build_ele
        max_count = 1

        for ctrl_prop in self.build_ele_ctrl_props:
            if ctrl_prop.list_group_name == list_group_name:
                if (prop := build_ele.get_property(ctrl_prop.value_name)) is not None and isinstance(prop.value, list):
                    max_count = max(max_count, len(prop.value))

        return max_count


    @staticmethod
    def __eval_text(eval_text     : str,
                    max_list_count: int,
                    parameter_dict: dict[str, Any]) -> str:
        """ eval the dynamic text

        Args:
            eval_text:      text to evaluate
            max_list_count: max list count
            parameter_dict: parameter dictionary

        Returns:
            evaluated text
        """

        if not StringEvaluate.is_text_from_script(eval_text):
            return eval_text

        text = ""

        for index in range(max_list_count):
            text += StringEvaluate.eval_text(eval_text.replace("$list_row", str(index)).replace("$list_col", "0"), parameter_dict)

        return text
