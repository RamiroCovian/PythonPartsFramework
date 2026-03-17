""" implementation of the palette control visibility checks
"""

from typing import Any

import inspect

from ControlProperties import ControlProperties
from StringEvaluate import StringEvaluate

from Utilities.GeneralConstants import GeneralConstants

from .PaletteData import PaletteData

class PaletteControlVisibility():
    """ implementation of the palette control visibility checks
    """

    @staticmethod
    def is_visible_expander_or_row(palette_data     : PaletteData,
                                   ctrl_prop        : ControlProperties,
                                   visible_condition: str) -> bool:
        """ check for visible expander / row

        Args:
            palette_data:      palette data
            ctrl_prop:         control property
            visible_condition: visible condition

        Returns:
            visible expander / row state
        """

        ctrl_prop.visible = True

        if ctrl_prop.control_type == ControlProperties.ControlType.EXPANDER:
            palette_data.expander_name    = ctrl_prop.expander_name
            palette_data.expander_visible = PaletteControlVisibility.is_visible_control(palette_data, ctrl_prop, visible_condition)

            return False

        if ctrl_prop.control_type == ControlProperties.ControlType.ROW:
            palette_data.row_name      = ctrl_prop.row_name
            palette_data.row_visible   = PaletteControlVisibility.is_visible_control(palette_data, ctrl_prop, visible_condition)
            palette_data.row_full_text = ctrl_prop.row_name if ctrl_prop.row_state_key else ""

            return False

        if palette_data.row_name != ctrl_prop.row_name:
            palette_data.row_full_text = ""

        if not palette_data.expander_visible and palette_data.expander_name == ctrl_prop.expander_name  or  \
           not palette_data.row_visible      and palette_data.row_name == ctrl_prop.row_name:
            ctrl_prop.visible          = False
            return False

        return True


    @staticmethod
    def is_visible_list_row(list_ctrl_props: ControlProperties,
                            row            : int,
                            param_dict     : dict[str, Any]) -> bool:
        """ check for visible list row

        Args:
            list_ctrl_props: control property
            row:             row index
            param_dict:      parameter dictionary

        Returns:
            visible expander state
        """

        visible_cond = list_ctrl_props.visible_condition.replace(GeneralConstants.LIST_ROW_KEYWORD, str(row))

        if visible_cond and not StringEvaluate.eval_condition(visible_cond, param_dict):
            return False

        if list_ctrl_props.visible_function:
            if not list_ctrl_props.visible_function(row):
                return False

        return True


    @staticmethod
    def is_visible_control(palette_data     : PaletteData,
                         ctrl_prop        : ControlProperties,
                         visible_condition: str) -> bool:
        """ check the visibility by the condition or function

        Args:
            palette_data:      palette data
            ctrl_prop:         control property
            visible_condition: visible condition

        Returns:
            control visibility state
        """

        if visible_condition and GeneralConstants.LIST_ROW_KEYWORD not in visible_condition and \
           not StringEvaluate.eval_condition(visible_condition, palette_data.param_dict):
            ctrl_prop.visible = False

            return False

        if ctrl_prop.visible_function:
            if not inspect.getfullargspec(ctrl_prop.visible_function).args and not ctrl_prop.visible_function():
                ctrl_prop.visible = False

                return False

        ctrl_prop.visible = True

        return True



    @staticmethod
    def set_tuple_visibilty(ctrl_prop        : ControlProperties,
                            visible_condition: str,
                            param_dict       : dict[str, Any]):
        """ set the tuple visibility

        Args:
            ctrl_prop:         control property
            visible_condition: visible condition
            param_dict:        parameter dictionary
        """

        ctrl_prop.visible = [bool(StringEvaluate.eval_condition(cond, param_dict)) \
                             if cond and GeneralConstants.LIST_ROW_KEYWORD not in cond else True for cond in visible_condition.split(",")]
