""" implementation of the script object service
"""

from typing import cast, Any

import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from ControlPropertiesUtil import ControlPropertiesUtil
from HandlePropertiesService import HandlePropertiesService

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

from .InputData import InputData
from .ScriptService import ScriptService

class ScriptObjectService():
    """ implementation of the script object service
    """

    @staticmethod
    def create_script_object(input_data: InputData) -> bool:
        """ create the element

        Args:
            input_data: input data

        Returns:
            script object is created: True/False
        """

        if (create_script_object := getattr(input_data.build_ele_script, "create_script_object", None)) is None:
            return False

        script_object_data = BaseScriptObjectData(input_data.coord_input,
                                                  input_data.modification_ele_list,
                                                  input_data.is_only_update,
                                                  ControlPropertiesUtil(input_data.build_ele_ctrl_props_list,
                                                                        input_data.build_ele_list))

        input_data.script_object = cast(BaseScriptObject, create_script_object(input_data.build_ele_list[0],
                                                                               script_object_data))

        input_data.script_object.start_input()

        if input_data.script_object.script_object_interactor is not None:
            input_data.script_object.script_object_interactor.start_input(input_data.coord_input)

            return True

        ScriptObjectService.execute_script_object(input_data)

        return True


    @staticmethod
    def execute_script_object(input_data: InputData) -> bool:
        """ execute the script object

        Args:
            input_data: input data

        Returns:
            script object is executed: True/False
        """

        if not input_data.script_object:
            return False

        input_data.create_ele_result = input_data.script_object.execute()

        if input_data.create_ele_result.placement_point:
            pnt = AllplanGeo.Point3D(input_data.create_ele_result.placement_point)

            input_data.set_insert_matrix_from_point(pnt)


        #----------------- test for modify elements

        input_data.is_modify_elements = False

        for ele in input_data.create_ele_result.elements:
            if isinstance(ele, AllplanBasisEle.AllplanElement):
                if not ele.GetBaseElementAdapter().IsNull():
                    input_data.is_modify_elements                = True
                    input_data.create_ele_result.placement_point = AllplanGeo.Point3D()

                    input_data.set_insert_matrix_from_point(AllplanGeo.Point3D())

                    break

        return True


    @staticmethod
    def modify_element_property(script_object: BaseScriptObject,
                                name         : str,
                                value        : Any) -> bool:
        """ modify the element property

        Args:
            script_object: script object
            name:          name
            value:         value

        Returns:
            update palette state
        """

        if (modify_prop := getattr(script_object, "modify_element_property", None)) is None:
            return False

        return False if (result := modify_prop(name.split("___", 1)[0], value)) is None else result


    @staticmethod
    def move_handle(input_data: InputData,
                    input_pnt : AllplanGeo.Point3D) -> bool:
        """ Move a handle

        Args:
            input_data: input data
            input_pnt:  input point

        Returns:
            Handle is moved: True/False
        """

        if not input_data.script_object:
            return False

        if (handle_prop := input_data.handle_modi_service.handle_prop) is None:
            return False

        if (local_pnt := input_data.handle_modi_service.get_local_handle_point(input_pnt)) is None:
            return False


        #----------------- in case of missing implementation execute default

        if (move_handle := getattr(input_data.script_object, "move_handle", None)) is None:
            HandlePropertiesService.update_property_value(input_data.build_ele_list[0], handle_prop, local_pnt)

            if (created := ScriptObjectService.execute_script_object(input_data)):
                ScriptService.update_palette(input_data, handle_prop)

            return created


        #----------------- execute the function from the script object

        input_data.create_ele_result = move_handle(handle_prop, local_pnt)

        if input_data.create_ele_result.placement_point:
            pnt = AllplanGeo.Point3D(input_data.create_ele_result.placement_point)

            input_data.set_insert_matrix_from_point(pnt)

        ScriptService.update_palette(input_data, handle_prop)

        return True


    @staticmethod
    def start_input(input_data: InputData) -> bool:
        """ execute the script object

        Args:
            input_data: input data

        Returns:
            next input is started: True/False
        """

        if not input_data.script_object:
            return False

        input_data.is_modify_elements         = False
        input_data.create_ele_result.elements = []

        input_data.script_object.start_input()

        if input_data.script_object.script_object_interactor is not None:
            input_data.script_object.script_object_interactor.start_input(input_data.coord_input)

        return True


    @staticmethod
    def start_next_input(input_data: InputData) -> bool:
        """ start the next input

        Args:
            input_data: input data

        Returns:
            next input is started: True/False
        """

        if not input_data.script_object:
            return False

        input_data.script_object.start_next_input()

        if input_data.script_object.script_object_interactor is None:
            ScriptObjectService.execute_script_object(input_data)

        else:
            input_data.script_object.script_object_interactor.start_input(input_data.coord_input)

        return True


    @staticmethod
    def on_cancel_function(input_data: InputData) -> OnCancelFunctionResult:
        """ Cancel the input function

        Args:
            input_data: input data

        Returns:
            on cancel function result
        """

        if not input_data.script_object:
            return OnCancelFunctionResult.NOT_IMPLEMENTED

        match (result := input_data.script_object.on_cancel_function()):
            case OnCancelFunctionResult.RESTART:
                ScriptObjectService.start_input(input_data)

            case OnCancelFunctionResult.CONTINUE_INPUT:
                ScriptObjectService.start_next_input(input_data)

        return result
