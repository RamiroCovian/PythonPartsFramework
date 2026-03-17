""" Implementation of the build element list service
"""

from typing import Any

import codecs
import hashlib
import os
import importlib.util
import shutil

import NemAll_Python_AllplanSettings as AllplanSettings

from BuildingElement import BuildingElement
from BuildingElementConverter import BuildingElementConverter
from BuildingElementXML import BuildingElementXML
from TraceService import TraceService, TraceLevel
from ParameterProperty import ParameterProperty

class BuildingElementListService:
    """ Implementation of functions for managing the data in a list of BuildingElements
    """

    @staticmethod
    def write_to_default_favorite_file(build_ele_list: list[BuildingElement]):
        """ The parameter values are taken from build_ele_list and written to the default favorite file.
        The file is located in the Allplan ".../usr/local/tmp" directory and the extension of the file is "pyv"

        Args:
            build_ele_list: list with the building elements
        """

        if not (file_name := AllplanSettings.AllplanPaths.GetUsrPath()):
            return

        file_name += "tmp\\" + os.path.split(build_ele_list[0].pyp_file_name)[1]

        path_parts = os.path.splitext(file_name)

        file_name = path_parts[0] + ".pyv"

        BuildingElementListService.write_to_file(file_name, build_ele_list)


    @staticmethod
    def read_from_default_favorite_file(build_ele_list: list[BuildingElement]):
        """ The parameter values are read from the default favorite file and assigned to
        the parameters in build_ele_list. The file is located in the Allplan
        ".../usr/local/tmp" directory and the extension of the file is "pyv"

        Args:
            build_ele_list: list with the building elements
        """

        if not (file_name := AllplanSettings.AllplanPaths.GetUsrPath()):
            return

        file_name += "tmp\\" + os.path.split(build_ele_list[0].pyp_file_name)[1]

        path_parts = os.path.splitext(file_name)

        file_name = path_parts[0] + ".pyv"

        BuildingElementListService.read_from_file(file_name, build_ele_list)


    @staticmethod
    def read_fav_data(fav_param_list      : list[str],
                      build_ele_list      : list[BuildingElement],
                      persistence         : ParameterProperty.Persistent = ParameterProperty.Persistent.MODEL,
                      is_modification_mode: bool                         = True,
                      script              : Any                          = None):
        """ Read the data from a favorite parameter list

        Args:
            fav_param_list:       list with the favorite parameter
            build_ele_list:       list with the building elements
            persistence:          Parameter persistency, for which the data should be read
            is_modification_mode: Read the data for the PythonPart modification, True/False
            script:               script
        """

        BuildingElementListService.migrate_fav_data(fav_param_list, build_ele_list, script)

        remove_executed = build_ele_list[0].script_name == "NodeScript.py" and not is_modification_mode

        fav_param_iter = iter(fav_param_list)

        for build_ele in build_ele_list:
            param_list = []

            build_ele_by_id = build_ele

            while True:
                if not (param := next(fav_param_iter, None)):
                    break

                if remove_executed and param.startswith("Executed="):
                    continue

                if (param := param.strip("\n").strip("\r")) == ("-------------------"):
                    break

                if param.startswith("__ElementID="):
                    if not (element_id := param[12:].strip("\n")):
                        continue

                    if not (build_ele_by_id := next((ele for ele in build_ele_list if ele.element_id == element_id), None)):
                        build_ele_by_id = build_ele

                    continue

                param_list.append(param)

            BuildingElementConverter.read_from_list(build_ele_by_id, param_list, persistence)


    @staticmethod
    def get_hash(build_ele_list: list[BuildingElement]) -> str:
        """ Calculate a hash value for script name and parameter list

        Args:
            build_ele_list: list with the building elements

        Returns:
            Calculated hash string.
        """

        script_str = build_ele_list[0].script_name.encode('utf-8')

        for build_ele in build_ele_list:
            script_str += repr(build_ele.get_model_parameter_dict(True)).encode('utf-8')

        return hashlib.sha224(script_str).hexdigest()


    @staticmethod
    def get_params_list(build_ele_list         : list[BuildingElement],
                        persistence            : ParameterProperty.Persistent = ParameterProperty.Persistent.MODEL,
                        exclude_parameter_names: (list[str] | None)           = None) -> list[str]:
        """ Get the parameter list of the building elements

        Args:
            build_ele_list:          list with the building elements
            persistence:             persistence to check
            exclude_parameter_names: excluded parameter names from the list

        Returns:
            Parameter list
        """

        params_list : list[str] = []

        for build_ele in build_ele_list:
            params_list += BuildingElementConverter.get_params_list(build_ele, persistence, exclude_parameter_names)

            if len(build_ele_list) > 1:
                if params_list[-1].startswith("__ElementID="):
                    del params_list[-1]
                else:
                    params_list.append("-------------------\n")

        return params_list


    @staticmethod
    def write_to_file(file_name     : str,
                      build_ele_list: list[BuildingElement]):
        """ Write the properties to a file

        Args:
            file_name:      Name of the file
            build_ele_list: list with the building elements
        """

        path_name = os.path.dirname(file_name)

        if os.path.exists(path_name) is False:
            os.makedirs(path_name)

        params_list = BuildingElementListService.get_params_list(build_ele_list, ParameterProperty.Persistent.MODEL_AND_FAVORITE)

        with codecs.open(file_name, 'w', encoding = 'utf8') as file:
            for param in params_list:
                file.write(param)

            file.close()


    @staticmethod
    def read_from_file(file_name     : str,
                       build_ele_list: list[BuildingElement]):
        """ Read the properties from a file

        Args:
            file_name:      Name of the file
            build_ele_list: list with the building elements
        """

        TraceService().trace(TraceLevel.FAVORITE_FILE_NAME, "read from file ", file_name)

        try:
            with codecs.open(file_name,'r',encoding='utf8') as ins:
                param_list = [line.replace("\n","") for line in ins]

                BuildingElementListService.read_fav_data(param_list, build_ele_list, ParameterProperty.Persistent.MODEL_AND_FAVORITE)

        except FileNotFoundError:
            return


    @staticmethod
    def reset_param_values(build_ele_list: list[BuildingElement]):
        """ Reset to original parameter values from pyp file

        Args:
            build_ele_list: list with the building elements
        """

        for build_ele in build_ele_list:
            _, filename = os.path.split(build_ele.pyp_file_name)

            abs_filename = build_ele.pyp_file_path + '\\' + filename

            if os.path.exists(abs_filename) is False:
                print("Filename '{abs_filename}' doesn't exist")
                return


            #------------- read the pyp XML file

            xml_ele = BuildingElementXML()

            new_read_build_ele, _, _ = xml_ele.read_element_parameter(abs_filename,
                                                                      build_ele_list[0].get_string_tables()[1],
                                                                      build_ele_list[0].get_material_string_table())


            #------------- set the parameters to this element

            BuildingElementConverter.read_from_list(
                build_ele,
                BuildingElementConverter.get_params_list(new_read_build_ele,
                                                         ParameterProperty.Persistent.MODEL_AND_FAVORITE),
                ParameterProperty.Persistent.MODEL_AND_FAVORITE)

    @staticmethod
    def migrate_fav_data(fav_param_list: list[str],
                         build_ele_list: list[BuildingElement],
                         script        : Any):
        """ Migrate the favorite data

        Args:
            fav_param_list: list with the parameter data
            build_ele_list: list with the building elements
            script:         script
        """

        if script:
            if (migrate := getattr(script, "migrate_parameter", None)):
                migrate(fav_param_list, build_ele_list[0].get_float_version())

                return


        #----------------- check for VS migration file

        _, filename = os.path.split(build_ele_list[0].pyp_file_name)

        if not filename:
            return

        if filename.lower().endswith(".pal"):
            return

        migration_file = build_ele_list[0].pyp_file_path + "\\" + filename.replace(".pyp", "_Migration.py")

        if not os.path.exists(migration_file):
            return

        module_spec = importlib.util.spec_from_file_location("Migration", migration_file)

        if module_spec is None or module_spec.loader is None:
            return

        migration = importlib.util.module_from_spec(module_spec)

        module_spec.loader.exec_module(migration)

        migration.execute_migration(fav_param_list)

        shutil.rmtree(build_ele_list[0].pyp_file_path + "\\" + "__pycache__")
