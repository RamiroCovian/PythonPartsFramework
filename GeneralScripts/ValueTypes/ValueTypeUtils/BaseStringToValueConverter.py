""" implementation of the base functions for the string to value conversion
"""

from typing import Any

from datetime import date, datetime

import locale

from collections.abc import Callable

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Utility as AllplanUtil

from StringEvaluate import StringEvaluate
from ValueListUtil import ValueListUtil

class BaseStringToValueConverter():
    """ implementation of the base functions for the string to value conversion
    """

    empty_list_key     = "[_]"
    value_list_key     = "["
    imperial_inch_key  = "\""
    imperial_feed_key  = "'"
    imperial_pound_key = "lb"
    imperial_ton_key   = "uston"
    multi_line_key     = "\n"
    date_key           = "date"
    allplan_key        = "Allplan"

    @staticmethod
    def to_float(value_str: str) -> (float | list[float]):
        """ Convert a float value string to a float, list is possible

        Args:
            value_str: value string

        Returns:
            float value(s)
        """

        #----------------- create a list (empty values "" need to be "0.")

        if BaseStringToValueConverter.is_list_value_string(value_str):
            if value_str == BaseStringToValueConverter.empty_list_key:
                return []

            value_str = value_str.replace("\"\"", "0.").replace("''", "0.")

            return eval(value_str)


        #----------------- use default value

        if value_str == "":
            return 0.


        #----------------- imperial length unit conversion

        if BaseStringToValueConverter.imperial_inch_key in value_str or BaseStringToValueConverter.imperial_feed_key in value_str:
            error, value = AllplanSettings.ImperialUnitService.ConvertToMM(value_str)

            if error:
                return 0.

            return value


        #----------------- imperial weight unit conversion

        if BaseStringToValueConverter.imperial_pound_key in value_str or BaseStringToValueConverter.imperial_ton_key in value_str:
            error, value = AllplanSettings.ImperialUnitService.ConvertTokg(value_str)

            if error:
                return 0.

            return value


        #----------------- execute the float conversion

        try:
            return float(value_str)

        except ValueError:
            return BaseStringToValueConverter.__print_value_error_msg(value_str, 0.)


    @staticmethod
    def to_int(value_str: str) -> (int | list[int]):
        """ Convert an integer value string to an integer, list is possible

        Args:
            value_str: value string

        Returns:
            integer value(s)
        """

        #----------------- create a list (empty values "" need to be "0")

        if BaseStringToValueConverter.is_list_value_string(value_str):
            if value_str == BaseStringToValueConverter.empty_list_key:
                return []

            value_str = value_str.replace("\"\"", "0").replace("''", "0")

            return eval(value_str, StringEvaluate.get_allplan_api_param_dict())


        #----------------- default value

        if value_str == "":
            return 0


        #----------------- execute the integer conversion

        try:
            return int(value_str)

        except ValueError:
            if BaseStringToValueConverter.allplan_key not in value_str:
                return BaseStringToValueConverter.__print_value_error_msg(value_str, 0)


        #----------------- execute enum conversion

        try:
            return eval(value_str, StringEvaluate.get_allplan_api_param_dict())

        except ValueError:
            return BaseStringToValueConverter.__print_value_error_msg(value_str, 0)


    @staticmethod
    def to_str(value_str: str) -> (str | list[str]):
        """ Convert a string value string to a string, list is possible

        Args:
            value_str: value string

        Returns:
            string vale(s)
        """

        if BaseStringToValueConverter.is_list_value_string(value_str) and BaseStringToValueConverter.multi_line_key not in value_str:
            if value_str == BaseStringToValueConverter.empty_list_key:
                return []

            return eval(value_str)

        return value_str


    @staticmethod
    def to_date(value_str: str) -> (date | list[date] | None):
        """ Convert an date value string to an date object, list is possible

        Args:
            value_str: value string

        Returns:
            date object(s)
        """

        #----------------- create a list (empty values "" need to be "0")

        if BaseStringToValueConverter.is_list_value_string(value_str):
            if value_str == BaseStringToValueConverter.empty_list_key:
                return []

            return eval(value_str, {BaseStringToValueConverter.date_key: date})


        #----------------- None

        if value_str == "":
            return None

        if BaseStringToValueConverter.date_key not in value_str:
            return BaseStringToValueConverter.string_to_date(value_str, True)


        #----------------- execute the date conversion

        try:
            return eval(value_str, {BaseStringToValueConverter.date_key: date})

        except (ValueError, TypeError):
            return BaseStringToValueConverter.__print_value_error_msg(value_str, date.today())


    @staticmethod
    def string_to_date(date_str  : str,
                       show_error: bool) -> (date | None):
        """ convert a date string to a date

        Args:
            date_str:   date string
            show_error: show error state in case of not correct date string

        Returns:
            date
        """

        locale.setlocale(locale.LC_TIME, "")

        try:
            return datetime.strptime(date_str, "%x")

        except (ValueError, TypeError):
            if show_error:
                AllplanUtil.ShowMessageBox(f"Date is not correct: {date_str}",  AllplanUtil.MB_OK)

            return None


    @staticmethod
    def date_to_string(date_value: date) -> str:
        """ convert a date to a string

        Args:
            date_value: date

        Returns:
            date
        """

        if date_value is None:
            return ""

        if isinstance(date_value, str):
            return date_value

        locale.setlocale(locale.LC_TIME, "")

        return date_value.strftime("%x")


    @staticmethod
    def to_auto(value_str: str) -> Any:
        """ convert a string to the possible type integer, float or string

        Args:
            value_str: value string

        Returns:
            value
        """

        if not value_str.isdigit():
            if "Allplan" in value_str:  # pylint: disable=magic-value-comparison
                return StringEvaluate.eval(value_str, StringEvaluate.get_allplan_api_param_dict())

            try:
                return float(value_str)

            except ValueError:
                pass

        try:
            return int(value_str)

        except ValueError:
            return value_str


    @staticmethod
    def to_value_by_type_converter(type_converter: Callable[[str], Any],
                                   value_str     : str) -> Any:
        """ Convert the value string to a value by the type converter, a list is possible and
        can have the formate "[...] * xx"

        Args:
            type_converter: type converter function
            value_str:      value string

        Returns:
            returns
        """

        if value_str == BaseStringToValueConverter.empty_list_key:
            return []

        if not BaseStringToValueConverter.is_list_value_string(value_str):
            return type_converter(value_str)

        value_parts = value_str.partition("]")

        left_str  = value_parts[0].strip("[")
        right_str = value_parts[2]

        values = left_str.split(";")

        ele_list = [type_converter(value) for value in values]

        if not right_str:
            return ele_list


        #----------------- multiply

        count = eval(f"1{right_str}")

        ValueListUtil.resize_list(ele_list, count)

        return ele_list


    @staticmethod
    def is_list_value_string(value_str: str) -> bool:
        """ check for a list value string

        Args:
            value_str: value string

        Returns:
            list value string state
        """

        return BaseStringToValueConverter.value_list_key in value_str


    @staticmethod
    def __print_value_error_msg(value_str    : str,
                                default_value: Any) -> Any:
        """ show value error message

        Args:
            value_str:     value string
            default_value: default value

        Returns:
            default value
        """

        print("\n\n")
        print(f"not possible to convert to {type(default_value)}: ",  value_str)
        print("\n\n")

        return default_value
