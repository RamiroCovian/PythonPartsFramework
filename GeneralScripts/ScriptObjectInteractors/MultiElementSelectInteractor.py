""" implementation of the interactor for the single element selection
"""

from dataclasses import dataclass

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from .BaseScriptObjectInteractor import BaseScriptObjectInteractor
from .BaseFilterObject import BaseFilterObject


@dataclass
class MultiElementSelectInteractorResult:
    """ Data class containing results of multiple element selection"""

    def __init__(self):
        """ initialize
        """

        self.sel_elements  : AllplanEleAdapter.BaseElementAdapterList = AllplanEleAdapter.BaseElementAdapterList()
        """List of selected elements"""


class MultiElementSelectInteractor(BaseScriptObjectInteractor):
    """ Implementation of the interactor for selecting multiple elements

    This interactor prompts the user to select one or more elements using
    Allplan native element selection functionality.
    """

    def __init__(self,
                 interactor_result: MultiElementSelectInteractorResult,
                 ele_filter       : (list[AllplanEleAdapter.GUID] | BaseFilterObject | AllplanIFW.SelectionQuery | None)  = None,
                 prompt_msg       : str     = "Select the elements",
                 active_elements  : bool    = True):
        """ Initialize the multiple element selection interactor

        Args:
            interactor_result:  object, where to save the selection results to
            ele_filter:         element filter as a list of accepted element type GUIDs or a callable or a selection query
                                returning True, when the element is valid for selection
            prompt_msg:         prompt message shown to the user in the dialog line
            active_elements:    When set to True, only elements on active layers and drawing files can be selected.
                                When set to False, elements on both active and passive layers and drawing files
                                can be selected.
        """

        self.interactor_result        = interactor_result
        self.__coord_input            = None
        self.__prompt_msg             = prompt_msg
        self.__post_element_selection = AllplanIFW.PostElementSelection()
        self.__selection_is_active    = False


        #----------------- set up selection filter

        if (sel_query := self.create_selection_query(ele_filter)) is not None:
            self.__selection_filter = AllplanIFW.ElementSelectFilterSetting(sel_query, not active_elements)
        else:
            self.__selection_filter = AllplanIFW.ElementSelectFilterSetting(not active_elements)


    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ Start the multiple element selection

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

        self.__coord_input = coord_input

        AllplanIFW.InputFunctionStarter.StartElementSelect(text                 = self.__prompt_msg,
                                                           selectSetting        = self.__selection_filter,
                                                           postSel              = self.__post_element_selection,
                                                           markSelectedElements = True)

        self.__selection_is_active = True


    def process_mouse_msg(self,
                          _mouse_msg: int,
                          _pnt      : AllplanGeo.Point2D,
                          _msg_info : AllplanIFW.AddMsgInfo) -> bool:
        """ Handles the process mouse message event

        Args:
            _mouse_msg: mouse message ID
            _pnt:       input point in Allplan view coordinates
            _msg_info:  additional mouse message info

        Returns:
            True/False for success.
        """

        if not self.__coord_input:
            return True

        self.__selection_is_active = False

        doc = self.__coord_input.GetInputViewDocument()

        selected_elements = self.__post_element_selection.GetSelectedElements(doc)

        if len(selected_elements) == 0:
            self.start_input(self.__coord_input)    # restart selection, if nothing selected
            return True

        self.interactor_result.sel_elements = selected_elements

        return False


    def close_selection(self):
        """ close the selection
        """

        if not self.__selection_is_active:
            return

        AllplanIFW.InputFunctionStarter.RemoveFunction()

        self.__selection_is_active = False


    def __del__(self):
        """Default destructor

        Remove the selection function from the stack, if it is running.
        """

        if self.__selection_is_active:
            AllplanIFW.InputFunctionStarter.RemoveFunction()
