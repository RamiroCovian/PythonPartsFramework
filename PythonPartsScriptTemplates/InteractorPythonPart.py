""" A template script for creating an interactor PythonPart
"""
from typing import Any

import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_Input as AllplanIFWInput
from BaseInteractor import BaseInteractor
from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from CreateElementResult import CreateElementResult
from StringTableService import StringTableService


def check_allplan_version(build_ele: BuildingElement,
                          version: float) -> bool:
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
                      version: float) -> None:
    """Migrate the parameter

    This function is called only during the modification of a PythonPart

    Args:
        parameter_list: parameter list
        version:        current PythonPart version
    """


def create_preview(build_ele: BuildingElement,
                   doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """ Create the library preview

    Args:
        build_ele: building element with the parameter properties
        doc:       document of the Allplan drawing files

    Returns:
        created element result
    """
    return CreateElementResult(elements=[...])


def create_interactor(coord_input: AllplanIFWInput.CoordinateInput,
                      pyp_path: str,
                      global_str_table_service: StringTableService,
                      build_ele_list: list[BuildingElement],
                      build_ele_composite: BuildingElementComposite,
                      control_props_list: list[BuildingElementControlProperties],
                      modify_uuid_list: list[str]) -> "Interactor":
    """Function for the interactor creation, called when PythonPart is initialized.
    When called, the PythonPart framework performs the following steps:

    - reads the parameters and their values from the xxx.pyp file and stores them in the buld_ele_list
    - if tag `ReadLastInput` is set to True: read the parameter values from the last input,
        (stored in ...\\Usr\\_user_name_\\tmp\\_python_part_name.pyv) and assign them to the parameters
        in build_ele_list
    - if starting an input by Match from the context menu or double right click: read the parameter
        values from the attribute @611@ of the matched PythonPart and assign them to the parameters
        in build_ele_list
    - if in modification mode: read the parameter values from the attribute @611@ of the selected
        PythonPart and assign them to the parameters in build_ele_list

    Args:
        coord_input:               coordinate input
        pyp_path:                  path of the pyp file
        global_str_table_service:  global string table service for default strings
        build_ele_list:            list with the building elements containing parameter properties
        build_ele_composite:       building element composite
        control_props_list:        control properties list
        modify_uuid_list:          UUIDs of the existing elements in the modification mode

    Returns:
        Created interactor object
    """

    return Interactor(coord_input, pyp_path, global_str_table_service, build_ele_list,
                      build_ele_composite, control_props_list, modify_uuid_list)


class Interactor(BaseInteractor):
    """ Template of an Interactor class """

    # #############
    #
    # implement the methods of your interactor here, as shown in the BaseInteractor class
    #
    # #############
