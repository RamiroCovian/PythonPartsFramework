""" A template script for creating a Script Object PythonPart
"""

import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_Input as AllplanIFW
from BaseScriptObject import BaseScriptObject
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


def check_allplan_version(build_ele: BuildingElement,
                          version:   float) -> bool:
    """Called when the PythonPart is started to check, if the current
    Allplan version is supported.

    Args:
        build_ele: building element with the parameter properties
        version:   current Allplan version

    Returns:
        True if current Allplan version is supported and PythonPart script can be run, False otherwise
    """

    return True


def migrate_parameter(parameter_list: list,
                      version:        float) -> None:
    """Migrate the parameter

    This function is called only during the modification of a PythonPart

    Args:
        parameter_list: parameter list
        version:        current PythonPart version
    """


def create_preview(build_ele: BuildingElement,
                   doc:       AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Function for the creation of the library preview elements.

    Args:
        build_ele: the building element.
        doc:       input document

    Returns:
        Preview elements. Only elements included in the property "elements" will be shown in the library preview
    """

    return CreateElementResult(elements=[...])


def create_script_object(build_ele  : BuildingElement,
                         coord_input: AllplanIFW.CoordinateInput) -> BaseScriptObject:
    """ Creation of the script object

    Args:
        build_ele:   building element with the parameter properties
        coord_input: API object for the coordinate input, element selection, ... in the Allplan view

    Returns:
        created script object
    """

    return ScriptObject(build_ele, coord_input)


class ScriptObject(BaseScriptObject):
    """ Implementation of the script object class """

    # #############
    #
    # implement the methods of your script object here, as shown in the BaseScriptObject class
    #
    # #############
