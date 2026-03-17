""" implementation of the interactor for the single element selection
"""

from collections.abc import Callable
from dataclasses import dataclass

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW
from TypeCollections.GeometryTyping import CURVES

from .BaseScriptObjectInteractor import BaseScriptObjectInteractor


@dataclass
class ArchOffsetPointInteractorResult:
    """ Implementation of the result of a point input on an architectural element
    """

    sel_wall            : AllplanEleAdapter.BaseElementAdapter = AllplanEleAdapter.BaseElementAdapter()
    """Selected wall"""

    sel_geo_ele         : CURVES                               = None
    """Selected geometry element"""

    input_point         : AllplanGeo.Point3D                   = AllplanGeo.Point3D()
    """Selected point"""

    show_simple_preview : bool                                 = True
    """Whether a simplified preview should be shown"""


class ArchOffsetPointInteractor(BaseScriptObjectInteractor):
    """ Implementation of the interactor for point input on an architectural element with an additional
    offset input after picking the point.

    Only vertical architectural elements (i.e. walls, beams, columns, foundation) are valid
    for this interactor. The input result can be used e.g. for creation of openings in these elements.
    """

    def __init__(self,
                 interactor_result: ArchOffsetPointInteractorResult,
                 request_text     : str,
                 preview_function : (Callable[[], None] | None) = None):
        """ initialize

        Args:
            interactor_result: result of the interactor
            request_text:      request text
            preview_function:  preview function
        """

        self.interactor_result  = interactor_result
        self.__request_text     = request_text
        self.__preview_function = preview_function

        self.__coord_input = None


    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ start the input

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

        self.__coord_input = coord_input

        self.__coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(self.__request_text),
                                               AllplanIFW.CoordinateInputMode(AllplanIFW.eIdentificationMode.eIDENT_ARCHPOINT_OFFSET))


    def on_preview_draw(self):
        """ Handles the preview draw event
        """

        if self.__coord_input is None:
            return

        self.interactor_result.input_point = self.__coord_input.GetCurrentPoint().GetPoint()

        if self.__preview_function:
            self.__preview_function()


    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """

        self.on_preview_draw()


    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : AllplanIFW.AddMsgInfo) -> bool:
        """ Handles the process mouse message event

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates
            msg_info:  additional mouse message info

        Returns:
            True/False for success.
        """

        if not self.__coord_input:
            return True

        input_pnt = self.__coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()


        #----------------- set the selected element and point

        if self.__coord_input.IsIdentModePointWallPoint():
            self.interactor_result.show_simple_preview = True

            sel_ele = self.__coord_input.GetSelectedElement()

            self.interactor_result.input_point = input_pnt

            if sel_ele.IsNull():
                self.interactor_result.sel_geo_ele = None
                self.interactor_result.sel_wall    = AllplanEleAdapter.BaseElementAdapter()

                if self.__preview_function:
                    self.__preview_function()

                return True


            #------------- set the wall element and the geometry element

            self.interactor_result.sel_wall    = AllplanEleAdapter.BaseElementAdapterParentElementService.GetParentElement(sel_ele)
            self.interactor_result.sel_geo_ele = self.__coord_input.GetSelectedGeometryElement()

        else:
            self.interactor_result.show_simple_preview = False


        #----------------- draw the preview

        if self.__preview_function:
            self.__preview_function()

        return self.__coord_input.IsMouseMove(mouse_msg)
