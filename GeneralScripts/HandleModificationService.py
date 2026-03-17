""" Implementation of the handle modification service.

The service can be used inside an Interactor-PythonPart for executing the modification by handles
"""

from typing import Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from HandleProperties import HandleProperties
from HandleService import HandleService
from InputMode import InputMode
from StringTableService import StringTableService

from Utilities.SystemAngleUtil import SystemAngleUtil

class HandleModificationService():
    """ Implementation of the handle modification service
    """

    __handle_draw_lock = False

    def __init__(self,
                 coord_input       : AllplanIFW.CoordinateInput,
                 build_ele_list    : list[BuildingElement],
                 control_props_list: list[BuildingElementControlProperties],
                 asso_ref_ele      : (AllplanEleAdapter.BaseElementAdapter | None) = None,
                 use_system_angle  : bool                                          = True):
        """ initialize

        Args:
            coord_input:        API object for the coordinate input, element selection, ... in the Allplan view
            build_ele_list:     list with the building elements
            control_props_list: list with the control properties
            asso_ref_ele:       reference element of the associative view
            use_system_angle:   use system angle state
        """

        self.__coord_input        = coord_input
        self.__build_ele_list     = build_ele_list
        self.__control_props_list = control_props_list

        self.__handle_service     = AllplanIFW.HandleService()
        self.__handle_list        = []
        self.__handle_to_asso_mat = AllplanGeo.Matrix3D()
        self.__handle_prop        = None
        self.__placement_mat      = AllplanGeo.Matrix3D()
        self.__input_mode         = InputMode.HandleSelect
        self.__old_handle_values  = []
        self.__asso_ref_ele       = asso_ref_ele
        self.__input_doc          = self.__coord_input.GetInputViewDocument()
        self.__view_world_proj    = self.__coord_input.GetViewWorldProjection()
        self.__use_system_angle   = use_system_angle


    @staticmethod
    def set_handle_draw_lock(handle_draw_lock: bool):
        """ set the handle draw lock state

        Args:
            handle_draw_lock: handle draw lock state
        """

        HandleModificationService.__handle_draw_lock = handle_draw_lock


    @staticmethod
    def is_handle_draw_lock() -> bool:
        """ get the handle draw lock state

        Returns:
            handle draw lock state
        """

        return HandleModificationService.__handle_draw_lock


    def start(self,
              handle_list               : list[HandleProperties],
              placement_mat             : AllplanGeo.Matrix3D,
              input_doc                 : AllplanEleAdapter.DocumentAdapter,
              view_world_proj           : AllplanIFW.ViewWorldProjection,
              create_view_input_controls: bool):
        """ start the handle modification

        Args:
            handle_list:                list with the handles
            placement_mat:              placement matrix of the PythonPart
            input_doc:                  input document
            view_world_proj:            view world projection
            create_view_input_controls: create the input controls in the view
        """

        if self.__handle_draw_lock:
            return

        if (existing_view_controls := self.__handle_list != []):
            self.__handle_service.RemoveHandles()


        #----------------- final transformation in case of rotated crosshair

        if self.__use_system_angle:
            placement_mat = SystemAngleUtil.execute_rotation(placement_mat)


        #----------------- set the data

        self.__handle_list     = handle_list
        self.__placement_mat   = placement_mat
        self.__input_doc       = input_doc
        self.__view_world_proj = view_world_proj
        self.__input_mode      = InputMode.HandleSelect

        if not handle_list:
            return


        #----------------- set the min/max values

        for handle in handle_list:
            handle.set_min_max_values(self.__control_props_list, self.__build_ele_list)


        #----------------- add and draw the handles

        self.__handle_service.AddHandles(self.__input_doc , handle_list, self.__placement_mat, self.__asso_ref_ele)
        self.__handle_service.DrawHandles()

        if create_view_input_controls and handle_list:
            AllplanIFW.BuildingElementInputControls().CreateControls(handle_list, self.__placement_mat,
                                                                     self.__view_world_proj,
                                                                     existing_view_controls, self.__asso_ref_ele)


    def stop(self):
        """ stop the handle modification """

        if self.__handle_draw_lock:
            return

        self.__handle_service.RemoveHandles()

        AllplanIFW.BuildingElementInputControls().CloseControls()

        self.__handle_list = []


    def reset_value(self):
        """ reset the handle value """

        for value in self.__old_handle_values:
            if (prop := self.__build_ele_list[value[0]].get_property(value[1])) is not None:
                prop.value = value[2]

        self.__old_handle_values = []


    def start_new_handle_point_input(self,
                                     str_table_service   : StringTableService,
                                     handle_placement_geo: (list[Any] | None) = None):
        """ start the new handle point input

        Args:
            str_table_service:    string table service
            handle_placement_geo: additional geometry element for the point input (hidden elements, preview elements)
        """

        str_tmp = str_table_service.get_string("e_NEW_HANDLE_POSITION", "Set the new handle point")

        self.__coord_input.InitNextPointInput(AllplanIFW.InputStringConvert(str_tmp))

        if handle_placement_geo is not None:
            self.__coord_input.AddGeometryFromPreviewElements(handle_placement_geo)

        if self.__handle_prop is not None:
            HandleService.set_abscissa_line(self.__placement_mat , self.__handle_to_asso_mat,
                                            self.__handle_prop, self.__coord_input)


    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : Any) -> bool:
        """ Handles the process mouse message event

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates
            msg_info:  additional mouse message info

        Returns:
            True/False for success.
        """

        match self.__input_mode:
            case InputMode.HandleSelect:
                return self.__select_handle(mouse_msg, pnt)

            case InputMode.HandleModify:
                return self.__modify_handle(mouse_msg, pnt, msg_info)

        return True


    def __select_handle(self,
                        mouse_msg: int,
                        pnt      : AllplanGeo.Point2D) -> bool:
        """ select a handle

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates

        Returns:
            True/False for success.
        """

        handle, self.__handle_to_asso_mat = self.__handle_service.SelectHandle(pnt, self.__coord_input.GetViewWorldProjection())

        if handle == -1:
            self.__handle_service.DeleteToolTipText()
            return False


        #------------- get the real index depending on the hidden handles

        visible_count = 0
        index         = 0

        for index, handle_item in enumerate(self.__handle_list):
            if handle_item.show_handles:
                if visible_count == handle:
                    break

                visible_count += 1


        #------------- draw the symbol and the tooltip

        self.__handle_prop = self.__handle_list[index]

        if not self.__handle_prop.click_state:
            HandleService.draw_direction_symbol(self.__placement_mat, self.__handle_prop,
                                                self.__coord_input, self.__asso_ref_ele)

        if self.__handle_prop.info_text:
            self.__handle_service.ShowToolTipText(self.__handle_prop.info_text)

        if self.__coord_input.IsMouseMove(mouse_msg):
            return True


        #---------------- start the modification

        self.__input_mode = InputMode.HandleModify

        self.__old_handle_values = HandleService.get_property_values(self.__build_ele_list, self.__handle_prop)

        self.__handle_service.DeleteToolTipText()
        self.__handle_service.RemoveHandles()

        AllplanIFW.BuildingElementInputControls().CloseControls()

        return True


    def __modify_handle(self,
                        mouse_msg: int,
                        pnt      : AllplanGeo.Point2D,
                        msg_info : Any) -> bool:
        """ modify a handle

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates
            msg_info:  additional mouse message info

        Returns:
            coordinate input return state
        """

        if self.__handle_prop is None:
            return False

        if (local_pnt := self.get_local_handle_point(self.new_handle_point_input(mouse_msg, pnt, msg_info))) is None:
            return True

        for build_ele in self.__build_ele_list:
            for param in self.__handle_prop.parameter_data:
                if build_ele.get_property(param.param_prop_name) is not None:
                    build_ele.change_property(self.__handle_prop, local_pnt)

                    break

        return True


    def new_handle_point_input(self,
                               mouse_msg: int,
                               pnt      : AllplanGeo.Point2D,
                               msg_info : Any) -> AllplanGeo.Point3D:
        """ Input the new handle point

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates
            msg_info:  additional mouse message info

        Returns:
            new handle point
        """

        if self.__handle_prop is None:
            return AllplanGeo.Point3D()

        handle_ref_pnt   = AllplanGeo.Transform(self.__handle_prop.ref_point,
                                                self.__placement_mat * self.__handle_to_asso_mat)
        handle_point_pnt = AllplanGeo.Transform(self.__handle_prop.handle_point,
                                                self.__placement_mat * self.__handle_to_asso_mat)

        input_pnt = self.__coord_input.GetInputPoint(mouse_msg, pnt, msg_info, handle_ref_pnt, True).GetPoint()

        if self.__handle_to_asso_mat.IsIdentity():
            HandleService.set_input_point_for_isometric_projection(input_pnt, handle_point_pnt,
                                                                    self.__coord_input.GetViewWorldProjection().GetIsoProjection())

        return input_pnt


    def get_local_handle_point(self,
                               input_pnt: AllplanGeo.Point3D) -> (AllplanGeo.Point3D | None):
        """ get the local handle point

        Args:
            input_pnt: new handle point

        Returns:
            handle point in the local element coordinate system, None if not exist
        """

        if self.__handle_prop is None:
            return None

        inv_mat = AllplanGeo.Matrix3D(self.__placement_mat)

        inv_mat.Reverse()

        local_pnt = AllplanGeo.Transform(input_pnt, inv_mat)

        if HandleService.is_coordinate_input_possible(self.__handle_prop, self.__handle_prop.ref_point, local_pnt):
            return local_pnt

        self.reset_value()

        return None


    @property
    def handle_prop(self) -> HandleProperties | None:
        """ get the handle property

        Returns:
            handle properties
        """

        return self.__handle_prop
