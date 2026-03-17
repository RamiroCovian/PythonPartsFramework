""" implementation of the property helper
"""

from typing import Any, Tuple

from BuildingElement import BuildingElement
from ControlProperties import ControlProperties
from ParameterProperty import ParameterProperty

def add_property(build_ele : BuildingElement,
                 name      : str,
                 value_type: str,
                 value     : Any,
                 persist   : ParameterProperty.Persistent) -> ParameterProperty:
    """ Add a property to the building element

    Args:
        build_ele:  building element with the parameter properties
        name:       name of the modified property
        value_type: value type of the property
        value:      value of the property
        persist:    persistent state of the property

    Returns:
        created property
    """

    prop            = ParameterProperty()
    prop.name       = name
    prop.value_type = value_type
    prop.persistent = persist
    prop.value      = value

    build_ele.add_property(name, prop)

    return prop


def create_property(name      : str,
                    value     : Any,
                    value_type: str) -> ParameterProperty:
    """ create a property

    Args:
        name:       name of the modified property
        value_type: value type of the property
        value:      value of the property

    Returns:
        created property
    """

    prop            = ParameterProperty()
    prop.name       = name
    prop.value_type = value_type
    prop.value      = value

    return prop


def create_ctrl_property(text: str,
                         name: str) -> ControlProperties:
    """ create a property

    Args:
        text: control text
        name: name of the property

    Returns:
        created property
    """

    return ControlProperties(text, name, "", "", 0, "", "", "", "", "", "")


def create_param_and_ctrl_prop(text      : str,
                               name      : str,
                               value     : Any,
                               value_type: str) -> Tuple[ParameterProperty, ControlProperties]:
    """ create a property and a control property

    Args:
        text:       description
        name:       name of the modified property
        value:      value of the property
        value_type: value type of the property

    Returns:
        created property
    """

    return create_property(name, value, value_type), create_ctrl_property(text, name)
