""" implementation of the interactor for the polygon input """

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW

from .BaseScriptObjectInteractor import BaseScriptObjectInteractor
from .OnCancelFunctionResult import OnCancelFunctionResult


@dataclass
class PolygonInteractorResult:
    """ implementation of the polygon input result
    """

    input_polygon : AllplanGeo.Polygon3D = AllplanGeo.Polygon3D()
    """Input polygon"""


class PolygonInteractor(BaseScriptObjectInteractor):
    """ implementation of the interactor for the polygon input
    """

    def __init__(self,
                 interactor_result  : PolygonInteractorResult,
                 common_prop        : AllplanBaseEle.CommonProperties = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties(),
                 z_coord_input      : bool = True,
                 multi_polygon_input: bool = True,
                 preview_function   : (Callable[[AllplanGeo.Polygon3D], list] | None)  = None):
        """ Create the interactor

        Args:
            interactor_result:   result of the interactor
            common_prop:         common properties for the polygon preview
            z_coord_input:       allow input of a 3d polygon
            multi_polygon_input: multi polygon input
            preview_function:    function for generating preview elements during the input
        """

        self.interactor_result   = interactor_result
        self.common_prop         = common_prop
        self.z_coord_input       = z_coord_input
        self.multi_polygon_input = multi_polygon_input
        self.preview_function    = preview_function
        self.polygon_input       = None


    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ start the input

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

        self.polygon_input = AllplanIFW.PolygonInput(coord_input, self.z_coord_input, self.multi_polygon_input)


    def on_cancel_function(self) -> OnCancelFunctionResult:
        """ Handles the cancel function event (triggered e.g. by hitting ESC, ...)

        Returns:
            True/False for success.
        """

        if self.polygon_input:
            result_polygon                       = self.polygon_input.GetPolygon()
            self.interactor_result.input_polygon = result_polygon if self.z_coord_input else self.flatten_polygon(result_polygon)
            self.polygon_input                   = None

        return OnCancelFunctionResult.CONTINUE_INPUT if self.interactor_result.input_polygon.IsValid() else OnCancelFunctionResult.CANCEL_INPUT


    def on_preview_draw(self):
        """ Handles the preview draw event
        """

        if self.polygon_input:
            preview_polygon = self.polygon_input.GetPreviewPolygon()

            self.draw_preview(preview_polygon if self.z_coord_input else self.flatten_polygon(preview_polygon))


    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """

        if self.polygon_input:
            self.draw_preview(self.polygon_input.GetPolygon())


    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : Any) -> bool:
        """ Process the mouse message event

        Args:
            mouse_msg: mouse message ID
            pnt:       input point in Allplan view coordinates
            msg_info:  additional mouse message info

        Returns:
            True/False for success.
        """

        if not self.polygon_input:
            return False

        self.polygon_input.ExecuteInput(mouse_msg, pnt, msg_info)

        self.draw_preview(self.polygon_input.GetPreviewPolygon())

        return True


    def draw_preview(self, polygon: AllplanGeo.Polygon3D):
        """ draw the preview

        Args:
            polygon: polygon
        """

        if not self.polygon_input:
            return

        if self.preview_function is None:
            preview_elements = [AllplanBasisEle.ModelElement3D(self.common_prop, polygon)]
        else:
            preview_elements = self.preview_function(polygon)

        AllplanBaseEle.DrawElementPreview(self.polygon_input.GetInputViewDocument(),
                                          AllplanGeo.Matrix3D(), preview_elements, True, None)


    @staticmethod
    def flatten_polygon(polygon: AllplanGeo.Polygon3D) -> AllplanGeo.Polygon3D:
        """Removes the Z coordinate from all vertices of the polygon

        Args:
            polygon: 3d polygon

        Returns:
            flattened polygon
        """

        xy_projection = AllplanGeo.Matrix3D(1,0,0,0,
                                            0,1,0,0,
                                            0,0,0,0,
                                            0,0,0,1)
        return polygon * xy_projection
