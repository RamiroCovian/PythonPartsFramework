""" implementation of the script object base class
"""

# pylint: disable=no-self-use

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dataclasses import dataclass

import abc

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

from TypeCollections.ModificationElementList import ModificationElementList

if TYPE_CHECKING:
    import NemAll_Python_Geometry as AllplanGeo
    from ControlPropertiesUtil import ControlPropertiesUtil
    from CreateElementResult import CreateElementResult
    from HandleProperties import HandleProperties
    from ScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor


@dataclass
class BaseScriptObjectData:
    """ implementation of the data class for the script object interactor
    """

    coord_input          : AllplanIFW.CoordinateInput
    modification_ele_list: ModificationElementList
    is_only_update       : bool
    control_props_util   : ControlPropertiesUtil


class BaseScriptObject(abc.ABC, BaseScriptObjectData):
    """ implementation of the script object base class
    """

    def __init__(self,
                 script_object_data: BaseScriptObjectData):
        """ Initialization of class TextExample

        Args:
            script_object_data: script object data
        """

        super().__init__(script_object_data.coord_input,
                         script_object_data.modification_ele_list,
                         script_object_data.is_only_update,
                         script_object_data.control_props_util)

        self.__script_object_interactor : (BaseScriptObjectInteractor | None) = None

        self.is_modification_mode = self.modification_ele_list.is_modification_element()


    @property
    def document(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the document

        Returns:
            document
        """

        return self.coord_input.GetInputViewDocument()


    @property
    def script_object_interactor(self) -> (BaseScriptObjectInteractor | None):
        """ get the script object interactor

        Returns:
            script object interactor
        """

        return self.__script_object_interactor


    @script_object_interactor.setter
    def script_object_interactor(self,
                                 interactor: (BaseScriptObjectInteractor | None)):
        """ set the script object interactor

        Args:
            interactor: script object interactor
        """

        self.__script_object_interactor = interactor


    @abc.abstractmethod
    def execute(self) -> CreateElementResult:
        """  execute the script

        Returns:
            created result
        """


    def start_input(self):
        """ start the input

        Overload this member function in the case where a script object interactor
        (e. g. for an element selection) needs to be started before the script execution
        """


    def start_next_input(self):
        """ start the next input

        Overload this member function to execute the needed steps after the execution
        of a script object interactor (e. g. after an element selection)
        """


    def modify_element_property(self,
                                _name : str,
                                _value: Any) -> bool:
        """ Modify property of element

        Args:
            _name:  the name of the property.
            _value: new value for property.

        Returns:
            palette update state
        """

        return False


    def on_cancel_function(self) -> OnCancelFunctionResult:
        """ Handles the cancel function event (e.g. by ESC, ...)

        Returns:
            True : cancel the input
            False: continue the input
            None : in case of not implemented
        """

        return OnCancelFunctionResult.NOT_IMPLEMENTED


    def on_control_event(self,
                         event_id: int):
        """ Handles the on control event

        Args:
            event_id: event id of the clicked button control
        """


    def on_value_input_control_enter(self) -> bool:
        """ Process the enter inside the value input control

        Returns:
            message was processed: True/False
        """

        return False


    def on_shortcut_control_input(self,                     # pylint: disable=no-self-use
                                  _value: int) -> bool:
        """ Handles the input inside the shortcut control

        Args:
            _value: shortcut value

        Returns:
            True/False for success.
        """

        print()
        print("Missing implementation of on_shortcut_control_input ---> see BaseScriptObject!!!")
        print()

        return False


    def on_input_undo(self) -> bool:                                 # pylint: disable=no-self-use
        """ Process the input undo event

        Returns:
            message was processed: True/False
        """

        print()
        print("Missing implementation of on_input_undo ---> see BaseScriptObject!!!")
        print()

        return False


    def set_text_for_palette_modification(self,
                                          text: str):
        """ set an input text for a modification by palette

        Args:
            text: input text
        """

        self.coord_input.InitFirstElementInput(AllplanIFW.InputStringConvert(text))
