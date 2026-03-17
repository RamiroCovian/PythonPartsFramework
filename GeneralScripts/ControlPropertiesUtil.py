""" Implementation of the control properties service
"""

from typing import Any

from collections.abc import Callable

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from ControlPropertiesValueListUtil import ControlPropertiesValueListUtil

from Utilities.GeneralConstants import GeneralConstants

class ControlPropertiesUtil():
    """ Implementation of the control properties utilities """

    def __init__(self,
                 control_props_list: list[BuildingElementControlProperties],
                 build_ele_list    : list[BuildingElement]):
        """ initialize

        Args:
            control_props_list: list with the control properties
            build_ele_list:     list with the building elements
        """

        self.control_props : dict[str, BuildingElementControlProperties] = {}

        for control_props, build_ele in zip(control_props_list, build_ele_list):
            element_id = build_ele.element_id

            for prop in control_props:
                name = element_id + ":" + prop.value_name

                if name in self.control_props:
                    self.control_props[name].append(prop)
                else:
                    self.control_props[name] = BuildingElementControlProperties([prop])

        self.build_ele_list = build_ele_list
        self.global_attr    = {}


    def set_global_attributes(self, global_attributes: dict[str, Any]):
        """ set the global attributes

        Args:
            global_attributes: global attributes
        """

        self.global_attr = global_attributes


    def set_text(self,
                 value_name: str,
                 text      : str,
                 element_id: str = ""):
        """ set the text control property

        Args:
            value_name: value name of the control
            text:       text control property
            element_id: element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            if ctrl_prop.value_list and GeneralConstants.TEXT_SEPARATOR in text:
                parts = text.split(GeneralConstants.TEXT_SEPARATOR)

                ctrl_prop.text            = parts[0]
                ctrl_prop.value_text_list = "|".join(parts[1:])
            else:
                ctrl_prop.text = text


    def set_value_list(self,
                       value_name: str,
                       value_list: str,
                       element_id: str = ""):
        """ set the value list control property

        Args:
            value_name: value name of the control
            value_list: value list control property
            element_id: element ID of the building element. Defaults to "".
        """

        build_ele = next((build_ele for build_ele in self.build_ele_list if build_ele.element_id == element_id), None)

        assert build_ele

        prop = build_ele.get_existing_property(value_name)

        value = prop.value

        is_in_globals = self.global_attr and value_name in self.global_attr


        #------------------- check for a new value list

        ctrl_prop_value_name = element_id + ":" + value_name

        if self.control_props[ctrl_prop_value_name][0].value_list == value_list:
            return

        for ctrl_prop in self.control_props[ctrl_prop_value_name]:
            ctrl_prop.value_list = value_list


        #----------------- check the current value against the value list

        param_dict = build_ele.get_parameter_dict()

        is_updated, upd_value = ControlPropertiesValueListUtil.validate_value(self.control_props[ctrl_prop_value_name][0],
                                                                              prop, value, param_dict)

        if not is_updated:
            return

        prop.value = upd_value

        if is_in_globals:
            self.global_attr[value_name] = prop.value


    def set_value_text_list(self,
                            value_name     : str,
                            value_text_list: str,
                            element_id     : str = ""):
        """ set the value list 2 control property

        Args:
            value_name:      value name of the control
            value_text_list: value text list
            element_id:      element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.value_text_list = value_text_list


    def set_value_list_2(self,
                         value_name  : str,
                         value_list_2: str,
                         element_id  : str = ""):
        """ set the value list 2 control property

        Args:
            value_name:   value name of the control
            value_list_2: value list 2 control property
            element_id:   element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.value_list_2 = value_list_2


    def set_enable_condition(self,
                             value_name      : str,
                             enable_condition: str,
                             element_id      : str = ""):
        """ set the enable condition control property

        Args:
            value_name      : value name of the control
            enable_condition: enable condition control property
            element_id      : element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.enable_condition = enable_condition


    def set_visible_condition(self,
                              value_name       : str,
                              visible_condition: str,
                              element_id       : str = ""):
        """ set the visible condition control property

        Args:
            value_name:        value name of the control
            visible_condition: visible condition control property
            element_id:        element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.visible_condition = visible_condition


    def set_enable_function(self,
                            value_name     : str,
                            enable_function: (Callable[..., bool] | None),
                            element_id     : str = "")            :
        """ set the enable function control property

        Args:
            value_name:      value name of the control
            enable_function: enable function control property
            element_id:      element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.enable_function = enable_function


    def set_visible_function(self,
                             value_name      : str,
                             visible_function: (Callable[..., bool] | None),
                             element_id      : str = "")            :
        """ set the visible function control property

        Args:
            value_name:       value name of the control
            visible_function: visible function control property
            element_id:       element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.visible_function = visible_function


    def set_min_value(self,
                      value_name      : str,
                      min_value       : str,
                      element_id      : str = ""):
        """ set the min value control property

        Args:
            value_name : value name of the control
            min_value  : minimal value
            element_id : element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.min_value_condition = min_value


    def set_max_value(self,
                      value_name      : str,
                      max_value       : str,
                      element_id      : str = ""):
        """ set the max value control property

        Args:
            value_name : value name of the control
            max_value  : maximal value
            element_id : element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.max_value_condition = max_value


    def set_background_color(self,
                             value_name      : str,
                             background_color: str,
                             element_id      : str = ""):
        """ set the background color control property

        Args:
            value_name:       value name of the control
            background_color: background color in the format "(red, green, blue)" with "(-1, -1, -1)" as default
            element_id:       element ID of the building element. Defaults to "".
        """

        for ctrl_prop in self.control_props[element_id + ":" + value_name]:
            ctrl_prop.background_color = background_color
