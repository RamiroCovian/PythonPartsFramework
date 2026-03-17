""" implementation of the interactor for the single element selection
"""

from dataclasses import dataclass
from typing import Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from .BaseFilterObject import BaseFilterObject
from .BaseScriptObjectInteractor import BaseScriptObjectInteractor


@dataclass
class SingleElementSelectResult:
    """ implementation of the single element selection result
    """

    sel_element : AllplanEleAdapter.BaseElementAdapter = AllplanEleAdapter.BaseElementAdapter()
    """Selected element"""

    sel_geo_ele : Any                                  = None
    """Geometry of the selected element"""

    input_point : AllplanGeo.Point3D                   = AllplanGeo.Point3D()
    """Input point"""


class SingleElementSelectInteractor(BaseScriptObjectInteractor):
    """ implementation of the interactor for the single element selection
    """

    def __init__(self,
                 interactor_result: SingleElementSelectResult,
                 ele_filter       : (list[AllplanEleAdapter.GUID] | BaseFilterObject | AllplanIFW.SelectionQuery | None)  = None,
                 prompt_msg       : str = "Select the element"):
        """ initialize

        Args:
            interactor_result: result of the interactor
            ele_filter:        element filter as a list of accepted element type GUIDs or a callable or a selection query
                               returning True, when the element is valid for selection
            prompt_msg:        prompt message shown to the user in the dialog line
        """

        self.interactor_result = interactor_result
        self.__coord_input     = None
        self.__prompt_msg      = prompt_msg


        #----------------- set up selection filter

        if (sel_query := self.create_selection_query(ele_filter)) is not None:
            self.__selection_filter = AllplanIFW.ElementSelectFilterSetting(sel_query)
        else:
            self.__selection_filter = None


    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ start the input

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

        self.__coord_input = coord_input

        self.__coord_input.InitFirstElementInput(AllplanIFW.InputStringConvert(self.__prompt_msg))


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

        if self.__selection_filter is None:
            self.__coord_input.SelectElement(mouse_msg, pnt, msg_info, True, False, False)
        else:
            self.__coord_input.SelectElement(mouse_msg, pnt, msg_info, True, False, False, self.__selection_filter)

        sel_ele = self.__coord_input.GetSelectedElement()

        if sel_ele.IsNull() or self.__coord_input.IsMouseMove(mouse_msg):
            return True

        self.interactor_result.sel_element = sel_ele

        return False
