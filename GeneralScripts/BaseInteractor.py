""" Implementation of the interactor base class
"""

# pylint: disable=no-self-use
# pylint: disable=unused-private-member

from typing import Any

import abc
import enum
import sys

from types import ModuleType

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFWInput
import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from StringTableService import StringTableService

from ScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor

def __reload__(_mod: ModuleType) -> Any:
    """ don't reload this module to avoid problems with the enum check

    Args:
        _mod: module

    Returns:
        current module
    """

    return sys.modules[__name__]


class BaseInteractor(abc.ABC):
    """ base class for a PythonPart interactor
    """

    class InteractorInputMode(enum.IntEnum):
        """ definition of the interactor modes
        """

        COORDINATE_INPUT  = 0
        ELEMENT_SELECTION = 1

    @abc.abstractmethod
    def __init__(self,
                coord_input:                AllplanIFWInput.CoordinateInput,
                pyp_path:                   str,
                global_str_table_service:   StringTableService,
                build_ele_list:             list[BuildingElement],
                build_ele_composite:        BuildingElementComposite,
                control_props_list:         list[BuildingElementControlProperties],
                modify_uuid_list:           list[str]):
        """ Constructor

        Args:
            coord_input:               coordinate input
            pyp_path:                  path of the pyp file
            global_str_table_service:  global string table service for default strings
            build_ele_list:            list with the building elements containing parameter properties
            build_ele_composite:       building element composite
            control_props_list:        control properties list
            modify_uuid_list:          UUIDs of the existing elements in the modification mode
        """

        self.__script_object_interactor : (BaseScriptObjectInteractor | None) = None

    @abc.abstractmethod
    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : Any) -> bool:
        """ Handles the process mouse message event.

        This event is triggered with each message sent by the mouse, which can be a mouse move,
        mouse click, zoom out, etc. The message is sent only during mouse actions inside a viewport.

        Args:
            mouse_msg:  The mouse message.
            pnt:        The input point in view coordinates. The origin is the mid point of the viewport
            msg_info:   additional message info.

        Returns:
            True/False for success.
        """

    @abc.abstractmethod
    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any):
        """ Handles the modify element property event.

        This event is triggered with each modification of the element property done in the property
        palette or by using a handle.

        Args:
            page:   Page of the modified property
            name:   Name of the modified property.
            value:  New value of the modified property.
        """

    @abc.abstractmethod
    def on_control_event(self,
                         event_id: int) -> bool:
        """ Handles the on control event.

        Called when an event is triggered by a palette control (ex. button).

        Args:
            event_id: event id of the clicked button control

        Returns:
            palette update state
        """


    @abc.abstractmethod
    def on_cancel_function(self) -> bool:
        """ Handles the cancel function event

        This event is triggered when the ESC button is hit during the runtime of the PythonPart.

        Returns:
            True when the PythonPart framework should terminate the PythonPart, False otherwise.
        """

    def on_cancel_by_menu_function(self) -> None:
        """ Handles the event of terminating the PythonPart by calling another function
        in Allplan UI.

        Implement this method, when some actions must be introduced, before the PythonPart
        is eventually terminated.
        """

    @abc.abstractmethod
    def on_preview_draw(self):
        """ Handles the preview draw event.

        This event is triggered, when an input in the dialog line is done (e.g. input of a coordinate).
        """


    @abc.abstractmethod
    def on_mouse_leave(self):
        """ Handles the mouse leave event.

        This event is triggered, when the mouse leaves the viewport.
        """


    @abc.abstractmethod
    def on_value_input_control_enter(self) -> bool:
        """ Handles the value input control enter event.

        This event is triggered, when enter key is hit during the input inside the input control
        located in the dialog line.

        Returns:
            True/False for success.
        """


    def on_shortcut_control_input(self,                     # pylint: disable=no-self-use
                                  _value: int) -> bool:
        """ Handles the input inside the shortcut control.

        This event is triggered, when a shortcut is hit inside a shortcut input control in the
        dialog line. A shortcut input control is a control in the dialog line, where the user can hit
        only certain keys, like e.g. ROTATION_ANGLE_STEP where only + and - keys can be hit.

        Implementing this method makes sense only, when this kind of input control is used!

        Args:
            _value: value associated with the hit shortcut key

        Returns:
            True/False for success.
        """

        print()
        print("Missing implementation of on_shortcut_control_input ---> see BaseInteractor!!!")
        print()

        return False


    def on_input_undo(self) -> bool:                                 # pylint: disable=no-self-use
        """ Process the input undo event

        This event is triggered, when during coordinate input the user hits the undo button
        in the dialog line.

        Implementing this method is necessary only, when the undo button is shown to the
        user, i.e. the CoordinateInput.EnableUndoStep method was used.

        Returns:
            message was processed: True/False
        """

        print()
        print("Missing implementation of on_input_undo ---> see BaseInteractor!!!")
        print()

        return False


    def execute_save_favorite(self,
                              _file_name: str) -> None:
        """ Handles the execute save favorite event.

        This event is triggered after pressing "Save as a favorite" button in the property palette and
        selecting the location of the favorite file in the file dialog.

        Implementing this method is necessary only, when the load/save/restore favorite buttons are shown
        in the property palette, i.e. when the tag ShowFavoriteButtons in the .pyp file is set to True

        Args:
            _file_name:  full path and name of the selected favorite file
        """

        print()
        print("Missing implementation of execute_save_favorite ---> see BaseInteractor!!!")
        print()



    def execute_load_favorite(self,
                              _file_name: str) -> None:
        """ Handles the execute load favorite event.

        This event is triggered after pressing "Load favorite" button in the property palette and
        selecting the favorite file in the file dialog

        Implementing this method is necessary only, when the load/save/restore favorite buttons are shown
        in the property palette, i.e. when the tag ShowFavoriteButtons in the .pyp file is set to True

        Args:
            _file_name:  full path and name of the selected favorite file
        """

        print()
        print("Missing implementation of execute_load_favorite ---> see BaseInteractor!!!")
        print()


    def reset_param_values(self,
                           _build_ele_list: list[BuildingElement]) -> None:
        """ Handles the reset parameter values event.

        This event is triggered after pressing "Restore basic setting" button in the property palette.

        Implementing this method is necessary only, when the load/save/restore favorite buttons are shown
        in the property palette, i.e. when the tag ShowFavoriteButtons in the .pyp file is set to True

        Args:
            _build_ele_list:  list with building elements
        """

        print()
        print("Missing implementation of reset_param_values ---> see BaseInteractor!!!")
        print()


    def update_after_favorite_read(self) -> None:
        """ Called after reading the favorite data

        Implementing this method is necessary only, when the execute_load_favorite method
        was implemented and additional actions must be performed after the favorite file
        has been loaded.
        """


    def set_active_palette_page_index(self,
                                      _active_page_index: int) -> None:
        """ Handles the event of changing pages inside the property palette

        Args:
            _active_page_index: index of the active page, starting from 0
        """


    def start_next_input(self):
        """ start the next input

        Overload this member function to execute the needed steps after the execution
        of a script object interactor (e. g. after an element selection)
        """

        AllplanUtil.ShowMessageBox("Overload 'start_next_input' to execute the needed steps after the execution\n" \
                                   "of a script object interactor (e. g. after an element selection", AllplanUtil.MB_OK)


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
