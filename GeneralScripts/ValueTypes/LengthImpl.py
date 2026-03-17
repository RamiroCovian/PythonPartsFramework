""" implementation of the Length value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties
from StringEvaluate import StringEvaluate

import ParameterProperty

from .ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil

from .ParameterPropertyValueTypes import ParameterPropertyValueTypes

from .BaseFloatImpl import BaseFloatImpl

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class LengthImpl(BaseFloatImpl):
    """ implementation of the Length value type
    """

    @staticmethod
    def set_property_value(prop : ParameterProperty.ParameterProperty,
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

        if (ParameterPropertyListUtil.get_multiple_list_index(name)) is not None and isinstance(value, str):
            error, value = AllplanSettings.UnitService.ConvertToMM(value)

            if error:
                return True

        return BaseFloatImpl.set_property_value(prop, name, value)

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty.ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the length edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_edit_control(wpf_palette.AddLengthValue, prop, ctrl_props, prop.value)


    @staticmethod
    def update_by_constraint(build_ele : BuildingElement,
                             prop      : ParameterProperty.ParameterProperty,
                             ctrl_props: ControlProperties,
                             _name     : str):
        """ update by a constraint

        Args:
            build_ele:  building element with the parameter properties
            prop:       parameter property to update
            ctrl_props: control properties
            _name:      name of the modified value
        """

        prop.value = StringEvaluate.eval(ctrl_props.constraint[0],
                                         StringEvaluate.get_string_eval_param_dict(build_ele, build_ele.get_string_tables()[0]))


    @staticmethod
    def is_default_init_by_constraint(build_ele : BuildingElement,
                                      ctrl_props: ControlProperties) -> bool:
        """ check, whether the default value must be initialized by the constraint

        Args:
            build_ele:  building element with the parameter properties
            ctrl_props: control properties

        Returns:
            default init by the constraint state
        """

        prop = build_ele.get_existing_property(ctrl_props.value_name)

        if prop.persistent == ParameterProperty.ParameterProperty.Persistent.NO:
            return True

        constraint_name = ctrl_props.constraint[0].split(".")[0]

        if (prop := build_ele.get_property(constraint_name)) is None:
            return False

        return prop.value_type == ParameterPropertyValueTypes.PLANE_REFERENCES


    @staticmethod
    def value_to_unit_string(value: float) -> str:
        """ convert the value to the current unit value

        Args:
            value: value

        Returns:
            unit value as string
        """

        return AllplanSettings.UnitService.ToLengthUnitString(value)


    @classmethod
    def string_to_unit_value(cls,
                             value_str: str) -> float:
        """ convert the string to the unit value

        Args:
            value_str: value string

        Returns:
            unit value as string
        """

        error, value = AllplanSettings.UnitService.ConvertToMM(value_str)

        return 0 if error else value
