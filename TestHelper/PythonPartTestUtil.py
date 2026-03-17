""" Implementation of the test utilities for the nodes
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=not-callable

from typing import List, Any, Optional, Tuple

import os
import inspect

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementService import BuildingElementService
from BuildingElementListService import BuildingElementListService
from StringTableService import StringTableService

from TestHelper.Mock.CoordinateInputMock import CoordinateInputMock
from TestHelper.Mock.CreateElementsMock import clear_model_elements

class PythonPartTestUtil():
    """ Implementation of the test utilities for the nodes """

    @staticmethod
    def start_script(doc              : AllplanEleAdapter.DocumentAdapter,
                     example_name     : str,
                     print_script_name: bool                = True,
                     parameter_list   : Optional[List[Any]] = None,
                     modify_uuid_list : Optional[List[str]] = None) -> Tuple[Optional[Any], List[BuildingElement],
                                                                             CoordinateInputMock,
                                                                             AllplanPalette.PythonWpfPalette]:
        """ Start the example script

        Args:
            doc:               document of the Allplan drawing files
            example_name:      name of the example
            print_script_name: print the script name in the trace output state
            parameter_list:    list with the interactor parameters
            modify_uuid_list:  list with the UUIDs of the modified elements

        Returns:
            tuple(created interactor, list with the building elements, coordinate input, palette)
        """

        clear_model_elements()

        if print_script_name:
            print()
            print("---------------------------------------------------------")
            print(example_name)
            print()

        coord_input       = CoordinateInputMock(doc)
        str_table_service = StringTableService(AllplanSettings.AllplanPaths.GetEtcPath() + "PythonPartsFramework\\GeneralScripts")

        palette = AllplanPalette.PythonWpfPalette()

        build_ele_serv = BuildingElementService()

        example_path = AllplanSettings.AllplanPaths.GetEtcPath()

        _, build_ele_script, build_ele_list, control_props_list, build_ele_composite, _, file_name = \
            build_ele_serv.read_data_from_pyp(example_path + example_name + ".pyp",
                                              str_table_service.str_table, False,
                                              str_table_service.material_str_table, "", False)

        if build_ele_script is None:
            return None, build_ele_list, coord_input, palette

        if parameter_list:
            BuildingElementListService.read_fav_data(parameter_list, build_ele_list)

        pyp_path, _ = os.path.split(file_name)


        #----------------- create the interactor

        if (create_interactor := getattr(build_ele_script, "create_interactor", None)) is None:
            AllplanUtil.ShowMessageBox("Function 'create_interactor' not implemented in the py-file", AllplanUtil.MB_OK)
            return None, build_ele_list, coord_input, palette

        arg_spec = inspect.getfullargspec(create_interactor)

        func_param_count = len(arg_spec.args)

        if func_param_count == 3:
            interactor = create_interactor(coord_input, pyp_path, str_table_service)

        elif func_param_count == 7:
            interactor = create_interactor(coord_input, pyp_path, str_table_service,
                                           build_ele_list, build_ele_composite, control_props_list,
                                           modify_uuid_list if modify_uuid_list is not None else \
                                           ["00000000-0000-0000-0000-000000000000--0"])
        else:
            interactor = create_interactor(coord_input, pyp_path, False, str_table_service,
                                           build_ele_list, build_ele_composite, control_props_list,
                                           modify_uuid_list if modify_uuid_list is not None else \
                                           ["00000000-0000-0000-0000-000000000000--0"])

        return interactor, build_ele_list, coord_input, palette


    @staticmethod
    def create_interactor(doc              : AllplanEleAdapter.DocumentAdapter,
                          example_name     : str,
                          input_data       : Optional[List[Any]] = None,
                          print_script_name: bool                = True) -> Tuple[Optional[object],
                                                                                  AllplanPalette.PythonWpfPalette,
                                                                                  List[BuildingElement],
                                                                                  CoordinateInputMock]:
        """ Read the example

            input_data: AllplanGeo.Point3D(...)
                        "CancelInput"
                        "Cancel"

        Args:
            doc:               document of the Allplan drawing files
            example_name:      name of the example
            input_data:        input data
            print_script_name: print script name state

        Returns:
            tuple(created interactor, palette, list with the building elements, coordinate input)
        """
        import NemAll_Python_Geometry as AllplanGeo

        interactor, build_ele_list, coord_input, palette = PythonPartTestUtil.start_script(doc, example_name,
                                                                                           print_script_name = print_script_name)

        if interactor is None or not input_data:
            return interactor, palette, build_ele_list, coord_input

        for data in input_data:
            if isinstance(data, str):
                if data == "CancelInput":
                    interactor.on_cancel_function()

                    interactor.process_mouse_msg(512, AllplanGeo.Point2D(), None)

                    continue

                if data == "Cancel":
                    interactor.on_cancel_function()

            else:
                coord_input.SetInputPoint(data)

                interactor.process_mouse_msg(513, AllplanGeo.Point2D(), None)

        return interactor, palette, build_ele_list, coord_input
