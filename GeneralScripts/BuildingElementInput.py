""" Script for BuildingElementInput
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=not-callable
# pylint: disable=bare-except

import os
import os.path
import sys
import traceback
import webbrowser

from typing import Any

import ErrorLogWindow

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as AllplanUtil

from BuildingElementListService import BuildingElementListService
from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementStringTableManager import BuildingElementStringTableManager
from BuildingElementSubElementUtil import BuildingElementSubElementUtil
from DeleteObsoleteFiles import delete_obsolete_files
from DocumentManager import DocumentManager
from FileNameService import FileNameService
from HandleModificationService import HandleModificationService
from ImportHook import ImportHookFinder
from InputMode import InputMode
from TraceService import TraceService

from BuildingElementInputServices.InteractorService import InteractorService
from BuildingElementInputServices.InputData import InputData
from BuildingElementInputServices.InputService import InputService
from BuildingElementInputServices.ScriptObjectService import ScriptObjectService
from BuildingElementInputServices.ScriptService import ScriptService
from PythonPartPreview import PythonPartPreview

from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

from TypeCollections.ModificationElementList import ModificationElementList



sys.meta_path.append(ImportHookFinder)

os.environ['TCL_LIBRARY'] = f"{AllplanSettings.AllplanPaths.GetPrgPath()}\\Python\\tcl\\tcl8.6"
os.environ['TK_LIBRARY']  = f"{AllplanSettings.AllplanPaths.GetPrgPath()}\\Python\\tcl\\tk8.6"

class BuildingElementInput(InputData):
    """ Definition of class BuildingElementInput
    """
    def __init__(self,
                 coord_input: AllplanIFW.CoordinateInput,
                 path       : str):
        """ Initialization of class BuildingElementInput

        Args:
            coord_input:    Coordinate input class
            path:           Python script path
        """

        self.part_name = ""

        super().__init__(coord_input, path)

        self.is_cancel_by_menu_function = False

        TraceService(True)

        if not AllplanUtil.IsExecutedByUnitTest():
            delete_obsolete_files()

        ErrorLogWindow.clear_error_log_window()

        if (str_table := BuildingElementStringTableManager.get_instance()):
            str_table.clear_global_string_table()

        FileNameService.set_node_script_default_path(os.path.dirname(os.path.abspath(path)))

        DocumentManager.get_instance().document = self.coord_input.GetInputViewDocument()

    def start_input(self,
                    file_name             : str,
                    parameter_data        : list[str],
                    msg_info              : (AllplanIFW.AddMsgInfo | None),
                    is_modification_mode  : bool,
                    modify_uuid_list      : ModificationElementList,
                    geo_matrix            : AllplanGeo.Matrix3D,
                    local_placement_matrix: AllplanGeo.Matrix3D,
                    asso_ref_ele          : AllplanElementAdapter.BaseElementAdapter,
                    is_only_update        : bool,
                    is_marked_for_delete  : bool = False) -> tuple[bool, Any]:
        """ Start the input function

        Args:
            file_name:              file name of the pyp file
            parameter_data:         parameter data of the selected PythonPart
            msg_info:               additional mouse message info
            is_modification_mode:   is started in modification mode
            modify_uuid_list:       list with the UUIDs of the modified elements
            geo_matrix:             placement matrix
            local_placement_matrix: local placement matrix
            asso_ref_ele:           reference element of the associative view
            is_only_update:         only update the PythonPart, no user interaction
            is_marked_for_delete:   is marked for delete state

        Returns:
            (successfully started, started script object)
        """

        self.set_is_only_update_locks(is_only_update)

        self.init_general_data(is_modification_mode, modify_uuid_list, asso_ref_ele, is_only_update)


        #----------------- start from Allplan command line

        params = file_name.split("|")

        file_name = params[-1]

        if file_name.startswith("@"):
            sys.argv  = ["Allplan_Command_Line"] + params[:-1]
            file_name = file_name[1:]


        #----------------- start the allep installer

        elif file_name.lower().endswith(".allep"):
            sys.argv  = file_name
            file_name = r"\Library\AllepPlugins\AllplanGmbH\AllepManagement\AllepInstaller.pyp"



        #----------------- get the sub file name from the input by ?

        sub_file_name     = BuildingElementSubElementUtil.get_file_name_from_parameter(parameter_data, "SubElementsName")
        add_sub_file_name = BuildingElementSubElementUtil.get_file_name_from_parameter(parameter_data, "__AddPypSubFile__")


        #------------------ Load the building element and prepare the script data

        result, self.build_ele_script, self.build_ele_list, self.build_ele_ctrl_props_list,    \
            self.build_ele_composite, self.part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(file_name, self.str_table_service.str_table, False, \
                                                      self.str_table_service.material_str_table, sub_file_name,
                                                      not is_modification_mode, add_sub_file_name)

        if not result or self.build_ele_script is None:
            return False, self.build_ele_script

        self.prepare_script_data(parameter_data, msg_info, is_modification_mode, geo_matrix, local_placement_matrix)


        #----------------- check for pre PythonPart delete

        if is_marked_for_delete:
            return self.execute_pre_element_delete(), None


        #----------------- Start the interactor

        if self.build_ele_list[0].is_interactor:
            return InteractorService.start_interactor(self, is_only_update)


        #----------------- Create the element

        if not ScriptService.initialize_control_properties(self):
            return False, self.build_ele_script

        if not ScriptObjectService.create_script_object(self) and not ScriptService.create_element(self, True):
            return False, self.build_ele_script

        self.palette_service = BuildingElementPaletteService(self.build_ele_list, self.build_ele_composite,
                                                             self.build_ele_script,
                                                             self.build_ele_ctrl_props_list, self.file_name,
                                                             self.script_object)

        return self.start_standard_pythonpart(False), self.build_ele_script


    def start_standard_pythonpart(self,
                                  update_palette: bool) -> bool:
        """ start the standard PythonPart input

        Args:
            update_palette: update palette state

        Returns:
            start state
        """

        #----------------- show the palette

        if self.is_only_update:
            return True

        self.set_is_only_update_locks(False)

        if self.palette_service:
            try:
                if update_palette:
                    self.palette_service.update_palette(-1, True)
                else:
                    self.palette_service.show_palette(self.part_name, True)

            except:
                traceback.print_exc()

                return False

        if self.script_object and self.script_object.script_object_interactor is not None or self.is_modify_elements:
            return True


        #----------------- create the handle modification service

        self.handle_modi_service = HandleModificationService(self.coord_input, self.build_ele_list,
                                                             self.build_ele_ctrl_props_list, self.asso_ref_ele,
                                                             not self.modification_ele_list.is_modification_element())


        #----------------- Start the placement point input

        if not self.b_insert_point and not self.create_ele_result.placement_point:
            str_tmp = self.str_table_service.get_string("e_SET_POINT_TO", "Set the to point / Angle")

            self.coord_input.InitFirstPointValueInput(AllplanIFW.InputStringConvert(str_tmp),   \
                                AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eANGLE_COMBOBOX,
                                                                 True, False))

        else:
            str_tmp = self.str_table_service.get_string("e_SELECT_HANDLE", "Select the handle")

            self.coord_input.InitFirstPointValueInput( \
                AllplanIFW.InputStringConvert(str_tmp),   \
                AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eANGLE_COMBOBOX,
                                                 True, False))

            InputService.recalculate_and_draw_preview(self, True, False, False)

            self.handle_modi_service.start(self.create_ele_result.handles,self.insert_matrix,
                                           self.coord_input.GetInputViewDocument(), self.coord_input.GetViewWorldProjection(),
                                           True)

            self.input_mode = InputMode.HandleSelect

        return True


    def execute_pre_element_delete(self) -> bool:
        """ execute the pre element delete

        Returns:
            pre element delete handled state
        """

        if (execute_pre_element_delete := getattr(self.build_ele_script, "execute_pre_element_delete", None)) is None:
            return False

        execute_pre_element_delete(self.coord_input.GetInputViewDocument(), self.build_ele_list, self.modification_ele_list)

        return True


    def on_control_event(self, event_id: int):
        """ On control event

        Args:
            event_id: event id of control.
        """

        #----------------- check for a web link

        str_event_id = str(event_id)

        for ctrl_props, build_ele in zip(self.build_ele_ctrl_props_list, self.build_ele_list):
            for ctrl_prop in ctrl_props:
                if ctrl_prop.event_id == str_event_id:
                    prop = build_ele.get_property(ctrl_prop.value_name)

                    if prop is None or prop.value_type != ParameterPropertyValueTypes.BUTTON or not str(prop.value).startswith("https:"):
                        break

                    webbrowser.open(prop.value)

                    return


        #----------------- execute the control event

        if self.input_mode == InputMode.Interactor and self.interactor is not None:
            InteractorService.on_control_event(self, event_id)

        elif self.script_object:
            if self.script_object.on_control_event(event_id) and self.palette_service:
                self.palette_service.update_palette(-1, False)

            InputService.recalculate_and_draw_preview(self, True, False, False)

        elif self.palette_service and self.palette_service.on_control_event(event_id):
            if ScriptService.modify_control_properties(self, "", event_id):
                self.palette_service.update_palette(-1, False)

            InputService.recalculate_and_draw_preview(self, True, False, False)

        elif ScriptService.modify_control_properties(self, "", event_id) and self.palette_service:
            self.palette_service.update_palette(-1, False)


    def on_value_input_control_enter(self) -> bool:
        """ Process the enter inside the value input control

        Returns:
            message was processed: True/False
        """

        if self.input_mode == InputMode.Interactor and self.interactor:
            return InteractorService.on_value_input_control_enter(self)

        if self.script_object and self.script_object.on_value_input_control_enter():
            ScriptObjectService.start_next_input(self)
            return True

        return False


    def on_shortcut_control_input(self,
                                  value: int) -> bool:
        """ Handles the input inside the shortcut control

        Args:
            value: shortcut value

        Returns:
            message was processed: True/False
        """

        if self.input_mode == InputMode.Interactor and self.interactor:
            return InteractorService.on_shortcut_control_input(self, value)

        return self.script_object is not None and self.script_object.on_shortcut_control_input(value)


    def on_input_undo(self) -> bool:
        """ Process the input undo event

        Returns:
            message was processed: True/False
        """

        if self.input_mode == InputMode.Interactor and self.interactor:
            return InteractorService.on_input_undo(self)

        return self.script_object is not None and self.script_object.on_input_undo()


    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any):
        """ Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """

        has_script_object_interactor = self.script_object and self.script_object.script_object_interactor

        InputService.modify_element_property(self, page, name, value)

        if has_script_object_interactor and not (self.script_object and self.script_object.script_object_interactor):
            self.start_standard_pythonpart(True)


    def close_palette(self):
        """ Close the palette
        """

        if self.palette_service is not None:
            self.palette_service.close_palette()

        PythonPartPreview.close()


    def on_cancel_function(self) -> bool:
        """ Cancel the input function

        Returns:
            True/False for success.
        """

        PythonPartPreview.close()


        #----------------- cancel the input inside the interactor

        if self.input_mode == InputMode.Interactor and self.interactor is not None:
            return InteractorService.on_cancel_function(self, self.is_cancel_by_menu_function)


        #----------------- process the result from a script object

        match ScriptObjectService.on_cancel_function(self):
            case OnCancelFunctionResult.CANCEL_INPUT:
                self.set_is_only_update_locks(False)

                return True

            case (OnCancelFunctionResult.CONTINUE_INPUT | OnCancelFunctionResult.RESTART):
                self.start_standard_pythonpart(True)

                return False

        if self.is_modify_elements:
            self.input_mode = InputMode.HandleSelect

        if self.input_mode in [InputMode.RefPoint, InputMode.GeoExpand]:
            return True


        #----------------- restore the original value in case of canceling the handle modification

        if self.input_mode == InputMode.HandleModify:
            self.handle_modi_service.reset_value()

            self.input_mode = InputMode.HandleSelect

            InputService.recalculate_and_draw_preview(self, True, True, False)

            return False


        #----------------- create the elements

        if self.input_mode == InputMode.HandleSelect:
            InputService.create_elements_in_db(self)

            if self.is_only_update:
                self.set_is_only_update_locks(False)

                DocumentManager.get_instance().clear_pythonpart_element()

            return not self.start_next_input()

        return False


    def on_preview_draw(self):
        """ Handles the preview draw event
        """

        if self.script_object and self.script_object.script_object_interactor is not None:
            self.script_object.script_object_interactor.on_preview_draw()

            return

        if self.input_mode == InputMode.Interactor and self.interactor is not None:
            InteractorService.on_preview_draw(self)

            return

        if self.input_mode == InputMode.WriteToDB:
            return

        if self.input_mode == InputMode.RefPoint:
            if self.create_ele_result.placement_point:
                pnt = AllplanGeo.Point3D(self.create_ele_result.placement_point)
            else:
                pnt = self.coord_input.GetCurrentPoint().GetPoint()

            self.set_insert_matrix_from_point(pnt)

            self.build_ele_list[0].set_insert_matrix(self.insert_matrix)

        elif self.input_mode == InputMode.HandleModify:
            if (handle_prop := self.handle_modi_service.handle_prop):
                pnt = self.coord_input.GetCurrentPoint(self.get_point_from_insert_matrix() + handle_prop.ref_point, True).GetPoint()

                if not ScriptObjectService.move_handle(self, pnt) and not ScriptService.move_handle(self, pnt):
                    return

        if self.input_mode not in (InputMode.HandleSelect, InputMode.HandleModify):
            InputService.recalculate_and_draw_preview(self, True, False, True)
        else:
            InputService.draw_preview(self, True, False, False, True)


    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """

        if self.script_object and self.script_object.script_object_interactor is not None:
            self.script_object.script_object_interactor.on_mouse_leave()

            return

        if self.input_mode == InputMode.Interactor and self.interactor is not None:
            InteractorService.on_mouse_leave(self)

            return

        if self.input_mode > InputMode.RefPoint or \
           self.input_mode <= InputMode.RefPoint and self.script_object:
            InputService.draw_preview(self, True, False, False, False)

        elif self.create_ele_result.placement_point:
            pnt = AllplanGeo.Point3D(self.create_ele_result.placement_point)

            self.set_insert_matrix_from_point(pnt)

            InputService.draw_preview(self, True, False, False, False)


    def save_load_favorite(self,
                           is_save  : bool,
                           file_name: str):
        """ Save or load a favorite

        Args:
            is_save:   True = save, False = load
            file_name: Name of the favorite file
        """

        if InteractorService.save_load_favorite(self, is_save, file_name):
            return

        if is_save:
            BuildingElementListService.write_to_file(file_name, self.build_ele_list)
        else:
            BuildingElementListService.read_from_file(file_name, self.build_ele_list)

            if self.palette_service:
                self.palette_service.update_palette(-1, True)

            InputService.recalculate_and_draw_preview(self, True, True, False)


    def reset_param_values(self):
        """ Reset to original parameter values from PYP file
        """

        if self.input_mode == InputMode.Interactor:
            InteractorService.reset_param_values(self)

            return

        BuildingElementListService.reset_param_values(self.build_ele_list)

        InputService.recalculate_and_draw_preview(self, True, True, False)

        if self.input_mode == InputMode.Interactor:
            if (update_fct := getattr(self.interactor, "update_after_favorite_read", None)):
                update_fct()

            return

        if self.palette_service:
            self.palette_service.update_palette(-1, True)


    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : AllplanIFW.AddMsgInfo) -> bool:
        """ Handles the process mouse message event

        Args:
            mouse_msg: the mouse message.
            pnt      : the input point.
            msg_info : additional message info.

        Returns:
            True/False for success.
        """

        #----------------- input interactor for standard PythonPart

        if self.script_object and self.script_object.script_object_interactor is not None:
            if not self.script_object.script_object_interactor.process_mouse_msg(mouse_msg, pnt, msg_info):
                ScriptObjectService.start_next_input(self)

                self.start_standard_pythonpart(True)

            return True


        #----------------- Interactor

        if self.input_mode == InputMode.Interactor and self.interactor is not None:
                return InteractorService.process_mouse_msg(self, mouse_msg, pnt, msg_info)


        #----------------- Expand the geometry

        expand         = False
        expand_handles = None

        if self.input_mode == InputMode.GeoExpand:
            world_pnt2d = AllplanGeo.Point2D(self.coord_input.GetViewWorldProjection().ViewToWorldBaseZ0(pnt))

            AllplanGeo.Point2D(self.coord_input.GetViewWorldProjection().ViewToWorldBaseZ0(pnt))

            self.last_input_doc = self.coord_input.GetInputViewDocument()
            self.last_view_proj = self.coord_input.GetViewWorldProjection()

            place_pnt = AllplanGeo.Point3D()

            try:
                if len(self.build_ele_list) == 1:
                    expand, expand_handles, place_pnt, self.asso_ref_ele, create_ele_result =   \
                        self.build_ele_script.expand_create_element(self.build_ele_list[0], self.expand_util,
                                                                    world_pnt2d,
                                                                    self.coord_input.GetViewWorldProjection(),
                                                                    self.last_input_doc, self.last_expanded)
                else:
                    expand, expand_handles, place_pnt, self.asso_ref_ele, create_ele_result =   \
                        self.build_ele_script.expand_create_element(self.build_ele_list, self.build_ele_composite,
                                                                    self.expand_util, world_pnt2d,
                                                                    self.coord_input.GetViewWorldProjection(),
                                                                    self.last_input_doc, self.last_expanded)

            except:
                traceback.print_exc()

                AllplanUtil.ShowMessageBox("Function 'expand_create_element' must be implemented in script " +
                                           self.build_ele_list[0].script_name,
                                           AllplanUtil.MB_OK)

                return False

            ScriptService.set_element_result_data(self, create_ele_result)

            if expand is False:
                place_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()

            self.set_insert_matrix_from_point(AllplanGeo.Point3D(place_pnt))

            self.last_expanded = expand


        #----------------- Get the input point

        elif self.input_mode == InputMode.RefPoint:
            if self.create_ele_result.placement_point:
                place_pnt = AllplanGeo.Point3D(self.create_ele_result.placement_point)
            else:
                place_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()

            self.set_insert_matrix_from_point(place_pnt)


        #----------------- Select a handle

        elif self.input_mode == InputMode.HandleSelect:
            if not self.handle_modi_service.process_mouse_msg(mouse_msg, pnt, msg_info):
                InputService.draw_preview(self, False, False, True, False)

                return True


        #----------------- Get the new handle point

        elif self.input_mode == InputMode.HandleModify:
            input_pnt = self.handle_modi_service.new_handle_point_input(mouse_msg, pnt, msg_info)

            if not ScriptObjectService.move_handle(self, input_pnt) and not ScriptService.move_handle(self, input_pnt):
                InputService.draw_preview(self, False, False, False, False)

                return True


        #----------------- Draw the preview

        InputService.draw_preview(self, False, False, False, False)


        #----------------- Continue the input in case of wrong elements or mouse move

        if self.create_ele_result.is_empty():
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        if self.input_mode == InputMode.GeoExpand  and  (expand is False or expand_handles):
            self.input_mode += 1

        self.input_mode += 1


        #----------------- Switch to handle selection

        if self.input_mode in [InputMode.HandleSelect, InputMode.HandleNext]:
            self.input_mode = InputMode.HandleSelect

            self.handle_modi_service.start(self.create_ele_result.handles,self.insert_matrix,
                                           self.last_input_doc, self.last_view_proj, True)

            if self.handle_modi_service.handle_prop and self.palette_service:
                self.palette_service.update_palette(-1, True)

            str_tmp = self.str_table_service.get_string("e_SELECT_HANDLE", "Select the handle")

            self.coord_input.InitFirstPointValueInput(AllplanIFW.InputStringConvert(str_tmp),   \
                                                      AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eANGLE_COMBOBOX,
                                                                                       True, False))

            return True


        #----------------- Switch to handle modification

        if self.input_mode == InputMode.HandleModify:
            handle_prop = self.handle_modi_service.handle_prop


            #---------------- click handle

            if handle_prop.click_state:
                if not ScriptObjectService.move_handle(self, AllplanGeo.Point3D()):
                    ScriptService.move_handle(self, AllplanGeo.Point3D())

                self.input_mode = InputMode.HandleSelect

                InputService.recalculate_and_draw_preview(self, False, True, False)

                return True


            #---------------- select a sub element

            if handle_prop.handle_id == "__SubElementSelect__" and self.palette_service:
                self.palette_service.show_page_for_element(self.active_page, handle_prop.build_ele_index_list)

                self.input_mode = InputMode.HandleSelect

                InputService.recalculate_and_draw_preview(self, True, True, False)

                return True


            #---------------- start the new handle point input

            self.handle_modi_service.start_new_handle_point_input(self.str_table_service,
                                                                  self.create_ele_result.handle_placement_geo)

            return True

        InputService.create_elements_in_db(self)

        return self.start_next_input()


    def start_next_input(self) -> bool:
        """ start the next input if multi placement is active

        Returns:
            next input is started: True/False
        """

        self.is_modified_parameter = False

        if self.is_only_update or \
           not self.create_ele_result.multi_placement or \
           not DocumentManager.get_instance().pythonpart_element.IsNull():
            return False

        self.input_mode = InputMode.RefPoint

        AllplanIFW.BuildingElementInputControls().CloseControls()

        if ScriptObjectService.start_input(self) and self.palette_service:
            self.palette_service.update_palette(-1, True)
            return True

        str_tmp = self.str_table_service.get_string("e_SET_POINT_TO", "Set the to point / Angle")

        self.coord_input.InitFirstPointValueInput(AllplanIFW.InputStringConvert(str_tmp),   \
                                                  AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eANGLE_COMBOBOX,
                                                  True, False))
        return True



    def get_point_from_insert_matrix(self) -> AllplanGeo.Point3D:
        """ Get input point from the insert matrix

        Returns:
            point from the insert matrix

        """
        trans_vec = self.insert_matrix.GetTranslationVector()

        return AllplanGeo.Point3D(trans_vec.X, trans_vec.Y, trans_vec.Z)


    def is_visualeditor_running(self,
                                _power_management      : bool,
                                cancel_by_menu_function: bool) -> bool:
        """ check for running visual editor

        Args:
            _power_management:       checking for power management
            cancel_by_menu_function: cancel is execute due to menu function start

        Returns:
            Visual Editor is running
        """

        if (fct := getattr(self.interactor, "is_visualeditor", None)) is None:
            self.is_cancel_by_menu_function = cancel_by_menu_function

            return False

        return fct()


    @staticmethod
    def set_is_only_update_locks(is_only_update: bool):
        """ set the is only update locks

        Args:
            is_only_update: only update the PythonPart, no user interaction
        """

        BuildingElementPaletteService.set_palette_lock(is_only_update)
        HandleModificationService.set_handle_draw_lock(is_only_update)
        PythonPartPreview.set_preview_draw_lock(is_only_update)
