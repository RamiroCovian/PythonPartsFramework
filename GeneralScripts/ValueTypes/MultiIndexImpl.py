""" implementation of the MultiIndex value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import copy

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from Utilities.GeneralConstants import GeneralConstants

import ValueTypes.ValueTypeUtils.MinMaxValidator

from .BaseStrImpl import BaseStrImpl
from .MultiIndex import MultiIndex

if TYPE_CHECKING:
    from BuildingElementStringTable import BuildingElementStringTable
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class MultiIndexImpl(BaseStrImpl):
    """ implementation of the MultiIndex value type
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty,
                           _name: str,
                           value: str) -> bool:
        """ Set the value of the property

        Args:
            prop:  property
            _name: name of the modified property
            value: new value

        Returns:
            update palette state
        """

        prop.is_modified = True

        prop.value = MultiIndexImpl.get_value(value)

        return True


    @staticmethod
    def to_string(value: MultiIndex) -> str:
        """ convert the multi index to a string

        Args:
            value: new value

        Returns:
            multi index as string
        """

        return value.get_indexes(False)


    @staticmethod
    def get_value(value_str: str) -> MultiIndex:
        """ get the 2D arc from a string

        Args:
            value_str: 2D arc string

        Returns:
            2D arc(s)
        """

        return MultiIndex(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the string edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        of_str = prop_pal_ctrl_service.global_str_table.get_string('e_OF', 'of')


        #----------------- create the control text

        if isinstance(prop.value, MultiIndex):
            value_str = ""

            first_index_range = next(iter(prop.value))

            if len(prop.value) == 1 and first_index_range[0] == first_index_range[1]:
                value_str = f"{first_index_range[0]} {of_str} {ctrl_props.max_value}"


            else:
                for item in prop.value:
                    value_str += f"{item[0]}," if item[0] == item[1] else f"{item[0]}-{item[1]},"

                value_str = value_str[:-1]

            min_index = first_index_range[0]

            right_value = min(min_index + 1, ctrl_props.max_value)
            left_value  = max(1, min_index - 1)

        else:
            value_str = f"{prop.value} {of_str} {ctrl_props.max_value}"

            right_value = min(prop.value + 1, ctrl_props.max_value)
            left_value  = max(1, prop.value - 1)


        #----------------- create a row if not by default

        if not ctrl_props.row_name:
            ctrl_props          = ctrl_props.deep_copy()
            ctrl_props.row_name = ctrl_props.text


        #----------------- create the controls

        prop_pal_ctrl_service.add_string_edit_control(wpf_palette, prop, ctrl_props, value_str)

        wpf_palette.AddPictureResourceButton("", f"{prop.name}{GeneralConstants.DIALOG_BUTTON_KEY}_left",
                                             cast(int, AllplanSettings.PictResPalette.eRollLeft), cast(int,left_value),
                                             prop_pal_ctrl_service.page_index,
                                             ctrl_props.expander_name, ctrl_props.row_name + ctrl_props.row_state_key,
                                             prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                             ctrl_props.height, 8, ctrl_props.font_face_code)

        wpf_palette.AddPictureResourceButton("", f"{prop.name}{GeneralConstants.DIALOG_BUTTON_KEY}_right",
                                             cast(int, AllplanSettings.PictResPalette.eRollRight), cast(int, right_value),
                                             prop_pal_ctrl_service.page_index,
                                             ctrl_props.expander_name, ctrl_props.row_name + ctrl_props.row_state_key,
                                             prop_pal_ctrl_service.is_control_enabled(ctrl_props),
                                             ctrl_props.height, 8, ctrl_props.font_face_code)

    @staticmethod
    def test_and_update_for_min_value(value    : MultiIndex,
                                      min_value: int) -> tuple[bool, MultiIndex]:
        """ test and update for the minimal value

        Args:
            value:     value
            min_value: min value

        Returns:
            update state, new value
        """

        is_updated = False

        new_value = copy.deepcopy(value)

        for index, item in enumerate(new_value):
            if item[0] < min_value and item[1] < min_value:
                new_value[index] = (min_value, min_value)
                is_updated       = True

            elif item[0] < min_value:
                new_value[index] = (min_value, item[1])
                is_updated       = True

            elif item[1] < min_value:
                new_value[index] = (item[0], min_value)
                is_updated       = True

        return is_updated, new_value


    @staticmethod
    def validate_for_min_value(prop            : ParameterProperty,
                               ctrl_prop       : ControlProperties,
                               min_value       : Any,
                               global_str_table: BuildingElementStringTable) -> bool:
        """ validate for the minimal value

        Args:
            prop:             property
            ctrl_prop:        control properties
            min_value:        min value
            global_str_table: global string table

        Returns:
            palette update state
        """

        return ValueTypes.ValueTypeUtils.MinMaxValidator.MinMaxValidator.validate_for_min_value(
            prop, ctrl_prop, min_value, global_str_table,
            MultiIndexImpl.test_and_update_for_min_value)


    @staticmethod
    def test_and_update_for_max_value(value    : MultiIndex,
                                      max_value: int) -> tuple[bool, MultiIndex]:
        """ test and update for the maximal value

        Args:
            value:     value
            max_value: min value

        Returns:
            update state, new value
        """

        is_updated = False

        new_value = copy.deepcopy(value)

        for index, item in enumerate(new_value):
            if item[0] > max_value and item[1] > max_value:
                new_value[index] = (max_value, max_value)
                is_updated       = True

            elif item[0] > max_value:
                new_value[index] = (max_value, item[1])
                is_updated       = True

            elif item[1] > max_value:
                new_value[index] = (item[0], max_value)
                is_updated       = True

        return is_updated, new_value


    @staticmethod
    def validate_for_max_value(prop            : ParameterProperty,
                               ctrl_prop       : ControlProperties,
                               max_value       : Any,
                               global_str_table: BuildingElementStringTable) -> bool:
        """ validate for the maximal value

        Args:
            prop:             property
            ctrl_prop:        control properties
            max_value:        min value
            global_str_table: global string table

        Returns:
            palette update state
        """

        return ValueTypes.ValueTypeUtils.MinMaxValidator.MinMaxValidator.validate_for_max_value(
            prop, ctrl_prop, max_value, global_str_table,
            MultiIndexImpl.test_and_update_for_max_value)
