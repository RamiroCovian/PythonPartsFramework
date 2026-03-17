""" implementation of the base script object interactor
"""

# pylint: disable=no-self-use

from __future__ import annotations

import abc

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

from .BaseFilterObject import BaseFilterObject

class BaseScriptObjectInteractor(abc.ABC):
    """ implementation of the base script object interactor
    """

    @abc.abstractmethod
    def start_input(self,
                    coord_input: AllplanIFW.CoordinateInput):
        """ start the input

        Args:
            coord_input: API object for the coordinate input, element selection, ... in the Allplan view
        """

    @abc.abstractmethod
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

    def on_preview_draw(self):
        """ Handles the preview draw event
        """

    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """

    def on_cancel_function(self) -> OnCancelFunctionResult:
        """ Handles the cancel function event (e.g. by ESC, ...)

        Returns:
            True : cancel the input
            False: continue the input
            None : in case of not implemented
        """

        return OnCancelFunctionResult.NOT_IMPLEMENTED


    @staticmethod
    def create_selection_query(ele_filter: (list[AllplanEleAdapter.GUID] | \
                               BaseFilterObject | AllplanIFW.SelectionQuery | None)) -> AllplanIFW.SelectionQuery:
        """ create the selection query

        Args:
            ele_filter: element filter as a list of accepted element type GUIDs or a callable or a selection query

        Returns:
            selection query or None
        """

        if isinstance(ele_filter, list):
            type_queries = [AllplanIFW.QueryTypeID(ele_guid) for ele_guid in ele_filter]

            return AllplanIFW.SelectionQuery(type_queries)

        if callable(ele_filter):
            return AllplanIFW.SelectionQuery(ele_filter)

        return ele_filter
