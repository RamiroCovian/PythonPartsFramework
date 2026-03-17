""" Implementation of the mock class for the InputFunctionStarterMock.
"""

# pylint: disable=invalid-name
# pylint: disable=global-statement
# pylint: disable=no-self-use

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

SELECTED_ELEMENTS = AllplanEleAdapter.BaseElementAdapterList()

class PostElementSelectionMock():
    """ implementation of the mock class for PostElementSelection
    """

    def __init__(self):
        """ initialize
        """
        global SELECTED_ELEMENTS

        SELECTED_ELEMENTS = AllplanEleAdapter.BaseElementAdapterList()


    def GetSelectedElements(self,
                            _doc: AllplanEleAdapter.DocumentAdapter) -> AllplanEleAdapter.BaseElementAdapterList:
        """ get the selected elements

        Args:
            _doc: document of the Allplan drawing files

        Returns:
            selected elements
        """

        return SELECTED_ELEMENTS

    @staticmethod
    def SetSelectedElements(sel_elements: AllplanEleAdapter.BaseElementAdapterList):
        """ function description

        Args:
            sel_elements: description
        """

        global SELECTED_ELEMENTS

        SELECTED_ELEMENTS = sel_elements


class InputFunctionStarterMock():
    """ Implementation of the mock class for the InputFunctionStarterMock
    """

    @staticmethod
    def StartElementSelect(text                : str,
                           selectSetting       : AllplanIFW.ElementSelectFilterSetting,
                           postSel             : AllplanIFW.PostElementSelection,
                           markSelectedElements: bool,
                           selectionMode       : AllplanIFW.SelectionMode = AllplanIFW.SelectionMode.eSelectGeometry):
        """ Start the element selection

        A standard element selection will be started as overloaded function. The function
        will be removed if the selection is finished and elements are selected.

        Args:
            text:                 Request string as resource ID, CAllstring, TCHAR or CString
            selectSetting:        Filter setting
            postSel:              Post element selection
            markSelectedElements: Mark the selected elements: True/False
            selectionMode:        Selection mode
        """


    @staticmethod
    def RemoveFunction():
        """ remove the input function
        """
