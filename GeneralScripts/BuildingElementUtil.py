""" Implementation of the building element utilities
"""

from typing import Any

import traceback
import os

from collections import defaultdict
from types import ModuleType

import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from TraceService import TraceService, TraceLevel

from Utilities.ModuleImportUtil import ModuleImportUtil

try:
    RELOADER = __import__("AllepPlugins.AllplanGmbH.PythonPartSDK.reloader", fromlist = "reloader")

except ModuleNotFoundError:
    RELOADER = None

class BuildingElementUtil():
    """ Definition of class BuildingElementUtil
    """

    @staticmethod
    def import_building_element_script(build_ele    : BuildingElement,
                                       reload_script: bool,
                                       _to_remove   : Any = None) -> (ModuleType | None): # pylint: enable= deprecated-argument
        """ Import the building element script

        Args:
            build_ele:     building element with the parameter properties
            reload_script: Reload the script
            _to_remove:    this parameter can be removed!

        Returns:
            loaded script
        """

        script_name = os.path.splitext(build_ele.script_name)[0]

        if not script_name  or  script_name[0] == "[":
            if build_ele.script_name.find(".pypsub") == -1:
                print("Script name is missing in the pyp file !!!")

            return None

        TraceService().trace(TraceLevel.SCRIPT_NAME, "Import script:", script_name)

        islash = script_name.rfind("\\")

        script = None

        try:

            #------------- import by an absolute path

            if script_name.startswith("."):
                script = ModuleImportUtil.import_from_abs_path(build_ele.pyp_file_path + script_name[1:])


            #------------- import by a local path

            elif islash != -1:
                script_name = script_name.replace("\\", ".")

                script = __import__(script_name, fromlist = script_name[islash + 1:])


            #------------- import by name

            else:
                script = __import__(script_name)


            #------------- reload all the sub modules imported by this module

            if RELOADER and reload_script:
                script = RELOADER.reload(script)

        except ModuleNotFoundError:
            traceback.print_exc()

            AllplanUtil.ShowMessageBox("Script " + script_name + " not found", AllplanUtil.MB_OK)

        return script


    @staticmethod
    def count_scripts(build_ele_list: list[BuildingElement]) -> dict[str, int]:
        """ Count the number of existing scripts

        Args:
            build_ele_list:     Building element list

        Return:
            dictionary with the script names and counts
        """

        script_dict = defaultdict(int)

        for build_ele in build_ele_list:
            script_dict[build_ele.script_name] += 1

        return script_dict


    @staticmethod
    def hide_element_index(build_ele_list    : list[BuildingElement],
                           control_props_list: list[BuildingElementControlProperties]):
        """ Check for only one element with __ElementIndex__ and hide it

        Args:
            build_ele_list:     Building element list
            control_props_list: Control properties list
        """

        script_dict = BuildingElementUtil.count_scripts(build_ele_list)

        for key, value in script_dict.items():
            if value != 1:
                continue

            index = next((i for i, build_ele in enumerate(build_ele_list) if key == build_ele.script_name), None)

            if index is not None and \
               (ctrl_prop := next((ctrl_prop for ctrl_prop in control_props_list[index]
                                             if ctrl_prop.value_name == "__ElementIndex__"), None)):
                ctrl_prop.visible_condition = "False"
