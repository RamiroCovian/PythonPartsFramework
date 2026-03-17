""" implementation of the string evaluation """

#pylint: disable=exec-used
#pylint: disable=broad-except

from __future__ import annotations

from collections.abc import Callable

from typing import Any, TYPE_CHECKING

import ast

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil

from DocumentManager import DocumentManager

from Utils.StringUtil import StringUtil

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from BuildingElementStringTable import BuildingElementStringTable

class StringEvaluate():
    """ implementation of the string evaluation """

    TEXT_FROM_SCRIPT = "$Script:"
    BUILD_INS        = "__builtins__"

    @staticmethod
    def eval(string        : str,
             parameter_dict: dict[str, Any],
             log_error     : bool = True) -> Any:
        """ evaluate the string

        Args:
            string:         string to evaluate
            parameter_dict: parameter dictionary
            log_error:      log an error state

        Returns:
            result
        """

        string = string.strip(" \n")

        if StringEvaluate.is_python_script(string):
            string = StringEvaluate.exec_function_string(string, parameter_dict)

            if not isinstance(string, str):
                return string

        if not string:
            return string

        try:
            result = eval(string, parameter_dict)

        except Exception as err_msg:
            if log_error:
                StringEvaluate.show_error_message_box(err_msg, string)

                return ""

            return string

        return result


    @staticmethod
    def exec_function_string(function_string: str,
                             parameter_dict: dict[str, Any]) -> Any:
        """ execute a function string

        Args:
            function_string: string to execute
            parameter_dict:  parameter dictionary

        Returns:
            result
        """

        function_string = function_string.strip("\n")

        source = "import math\n\ndef eval_function_string():\n    " + function_string.replace("\n", "\n    ")

        try:
            exec(source, parameter_dict)

            if (result := parameter_dict["eval_function_string"]()) is None:
                result = ""

        except Exception as err_msg:
            StringEvaluate.show_error_message_box(err_msg, source)

            result = ""

        return result


    @staticmethod
    def eval_condition(condition: str,
                       parameter_dict: dict[str, Any]) -> bool:
        """ evaluate a condition

        Args:
            condition:       condition to evaluate
            parameter_dict:  parameter dictionary

        Returns:
            result
        """

        if not condition:
            return True

        if StringEvaluate.is_python_script(condition):
            return StringEvaluate.exec_function_string(condition, parameter_dict)

        return bool(eval(condition.strip().replace("\n", ""), parameter_dict))


    @staticmethod
    def eval_dimension(dimension: str,
                       parameter_dict: dict[str, Any]) -> int:
        """ evaluate a dimension

        Args:
            dimension:       dimension to evaluate
            parameter_dict:  parameter dictionary

        Returns:
            dimension
        """

        if not dimension:
            return 0

        if dimension.isdigit():
            return int(dimension)

        return int(eval(dimension, parameter_dict))


    @staticmethod
    def eval_color(color: str,
                   parameter_dict: dict[str, Any]) -> AllplanUtil.VecIntList:
        """ evaluate a color

        Args:
            color    :       color to evaluate
            parameter_dict:  parameter dictionary

        Returns:
            list with the red, green, blue color value
        """

        if not color:
            return AllplanUtil.VecIntList([-1, -1, -1])

        if StringEvaluate.is_python_script(color):
            return AllplanUtil.VecIntList(list(StringEvaluate.exec_function_string(color, parameter_dict)))

        return AllplanUtil.VecIntList(list(eval(color, parameter_dict)))


    @staticmethod
    def eval_constants(constants     : str,
                       parameter_dict: dict[str, Any],
                       converter     : (Callable[[str], (int | float)] | None) = None) -> str:
        """ evaluate constants

        Args:
            constants:      constants as xxx|xxx|zzz
            parameter_dict: parameter dictionary
            converter:      constant converter

        Returns:
            constants replaced with IDs
        """

        if not isinstance(constants, str):
            return constants

        if not constants:
            return ""

        constant_items = constants.split("|")

        if next((False for constant_item in constant_items if not constant_item.lstrip("+-").isdigit()), True):
            return constants

        if converter is None:
            return "|".join([str(StringEvaluate.eval(part, parameter_dict))
                            if not part.lstrip("-+").isdigit() else part for part in constant_items])

        return "|".join([str(converter(StringEvaluate.eval(part, parameter_dict)))
                         if not part.lstrip("-+").isdigit() else part for part in constant_items])


    @staticmethod
    def eval_constant(constant      : str,
                      parameter_dict: dict[str, Any]) -> str:
        """ evaluate a constant

        Args:
            constant:       constant
            parameter_dict: parameter dictionary

        Returns:
            constant
        """

        if not isinstance(constant, str):
            return constant

        if not constant:
            return ""

        return constant if (item := parameter_dict.get(constant)) is None else item


    @staticmethod
    def eval_list_row(text          : str,
                      row           : int,
                      parameter_dict: dict[str, Any]) -> str:
        """ evaluate a string with a list row and including a formula

        Args:
            text:           text to evaluate
            row:            row index
            parameter_dict: parameter dictionary

        Returns:
            adapted text
        """

        text = text.replace("$list_row", str(row))

        if StringEvaluate.is_text_from_script(text):
            return StringEvaluate.eval_text(text, parameter_dict)

        if "\"" in text:
            text = str(StringEvaluate.eval(text, parameter_dict))

        return text


    @staticmethod
    def eval_text(text: str,
                  parameter_dict: dict[str, Any]) -> str:
        """ evaluate a text

        Args:
            text:            text to evaluate
            parameter_dict:  parameter dictionary

        Returns:
            result from the dynamic text evaluation
        """

        if not text:
            return ""

        if not StringEvaluate.is_text_from_script(text):
            return text


        #----------------- evaluate the condition or formula

        text = text[8:]

        if StringEvaluate.is_python_script(text):
            result = StringEvaluate.exec_function_string(text, parameter_dict)

        else:
            try:
                result = eval(text, parameter_dict)

            except (NameError, ValueError, IndexError):
                return text

        return result


    @staticmethod
    def is_string_in_formula(string        : str,
                             formula_string: str) -> bool:
        """ test, whether a string is in a formula string

        Args:
            string:         string
            formula_string: formula string

        Returns:
            string is in formula string
        """

        if string == formula_string or formula_string.startswith(f"{string} ") or formula_string.endswith(f" {string}"):
            return True

        node = ast.parse(formula_string)

        def find_name_in_formula(node: ast.AST) -> bool:
            """ find the name inside the formula

            Args:
                node: description

            Returns:
                name was found state
            """

            if isinstance(node, ast.Name) and node.id == string:
                return True

            return any(find_name_in_formula(child) for child in ast.iter_child_nodes(node))

        return find_name_in_formula(node)


    @staticmethod
    def show_error_message_box(err_msg    : Exception,
                               eval_string: str):
        """ show the error message box

        Args:
            err_msg:     exception
            eval_string: string to evaluate
        """

        source = [f"{index + 1:4}: " + line for index, line in enumerate(eval_string.split("\n"))]

        AllplanUtil.ShowMessageBox(str(err_msg) + "\n\n" + "\n".join(source), AllplanUtil.MB_OK)


    @staticmethod
    def is_python_script(text: str) -> bool:
        """ test, whether the text is a Python script

        Args:
            text: text to analyze

        Returns:
            is python script state
        """

        return " return " in text or "\nreturn " in text or text.startswith("return ")    # pylint: disable=magic-value-comparison

    @staticmethod
    def is_text_from_script(text: str) -> bool:
        """ test, whether the text is generated by a script

        Args:
            text: text to analyze

        Returns:
            is text from script state
        """

        return StringEvaluate.TEXT_FROM_SCRIPT in text

    @staticmethod
    def get_string_eval_param_dict(build_ele: BuildingElement,
                                   str_table: BuildingElementStringTable) -> dict[str, Any]:
        """ get the parameter dict for the string evaluation

        Args:
            build_ele: building element with the parameter properties
            str_table: string table

        Returns:
            parameter dict
        """

        param_dict = build_ele.get_parameter_dict()

        param_dict["StringUtil"]     = StringUtil
        param_dict["__StringTable"]  = str_table
        param_dict["__document"]     = DocumentManager.get_instance().document

        param_dict.update(StringEvaluate.get_allplan_api_param_dict())
        param_dict.update(build_ele.get_constant_dict())

        return param_dict


    @staticmethod
    def get_allplan_api_param_dict() -> dict[str, Any]:
        """ get the parameter dict for the Allplan API

        Returns:
            parameter dict for the Allplan API access
        """

        return {"AllplanArchEle" : AllplanArchEle,
                "AllplanBaseEle" : AllplanBaseEle,
                "AllplanBasisEle": AllplanBasisEle,
                "AllplanGeo"     : AllplanGeo,
                "AllplanIFW"     : AllplanIFW,
                "AllplanPalette" : AllplanPalette,
                "AllplanReinf"   : AllplanReinf,
                "AllplanSettings": AllplanSettings,
                "AllplanUtil"    : AllplanUtil}


    @staticmethod
    def get_allplan_geometry_dict() -> dict[str, Any]:
        """ get the parameter dict for the standard geometry types

        Returns:
            parameter dict for the Allplan API access
        """

        return {"Vector2D": AllplanGeo.Vector2D,
                "Vector3D": AllplanGeo.Vector3D,
                "Point2D": AllplanGeo.Point2D,
                "Point3D": AllplanGeo.Point3D}
