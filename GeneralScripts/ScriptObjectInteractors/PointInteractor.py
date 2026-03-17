""" implementation of the interactor for the point input
"""

from collections.abc import Callable
from dataclasses import dataclass

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
from TypeCollections.GeometryTyping import CURVES

from .BaseScriptObjectInteractor import BaseScriptObjectInteractor


@dataclass
class PointInteractorResult:
    """ Implementation of the point input result
    """

    input_point : AllplanGeo.Point3D = AllplanGeo.Point3D()
    """Input point"""

    input_value: float               = 0
    """Value input in the input control in the dialog line"""


class PointInteractor(BaseScriptObjectInteractor):
    """ implementation of the interactor for the point input
    """

    def __init__(self,
                 interactor_result  : PointInteractorResult,
                 is_first_input     : bool,
                 request_text       : str,
                 preview_function   : (Callable[[], None] | None) = None,
                 default_input_value: (float | None)              = None,
                 abscissa_element   : CURVES                      = None):
        """ initialize

        Args:
            interactor_result:   result of the interactor
            is_first_input:      first input in a input sequence state
            request_text:        request text
            preview_function:    preview function
            default_input_value: default input value if value input is activated
            abscissa_element:    abscissa element for the point projection
        """

        self.interactor_result   = interactor_result
        self.is_first_input      = is_first_input
        self.request_text        = request_text
        self.preview_function    = preview_function
        self.default_input_value = default_input_value
        self.abscisssa_element   = abscissa_element

        self.coord_input = None

        if default_input_value is not None:
            self.interactor_result.input_value = default_input_value


    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ start the input

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

        self.coord_input = coord_input

        if self.default_input_value is None:
            if self.is_first_input:
                self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(self.request_text))
            else:
                self.coord_input.InitNextPointInput(AllplanIFW.InputStringConvert(self.request_text))

        elif self.is_first_input:
            self.coord_input.InitFirstPointValueInput(AllplanIFW.InputStringConvert(self.request_text),
                                                        AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eCOORDINATE_EDIT,
                                                                                         self.default_input_value,
                                                                                         True, False))
        else:
            self.coord_input.InitNextPointValueInput(AllplanIFW.InputStringConvert(self.request_text),
                                                       AllplanIFW.ValueInputControlData(AllplanIFW.eValueInputControlType.eCOORDINATE_EDIT,
                                                                                        self.default_input_value,
                                                                                        True, False))

        if self.abscisssa_element is not None:
            self.coord_input.SetAbscissaElement(self.abscisssa_element, AllplanGeo.Matrix3D())


    def on_preview_draw(self):
        """ Handles the preview draw event
        """

        if self.coord_input is None:
            return

        self.interactor_result.input_point = self.coord_input.GetCurrentPoint().GetPoint()

        if self.default_input_value is not None:
            self.interactor_result.input_value = self.coord_input.GetInputControlValue()

        if self.preview_function:
            self.preview_function()


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

        if not self.coord_input:
            return True

        self.interactor_result.input_point = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()

        if self.default_input_value is not None:
            self.interactor_result.input_value = self.coord_input.GetInputControlValue()

        if self.preview_function:
            self.preview_function()

        return self.coord_input.IsMouseMove(mouse_msg)
