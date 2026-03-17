"""
Implementation of the unit test interactor.

This interactor wraps the real interactor and allows to add
try and except for the member functions. The except will then
show the assert.
"""

# pylint: disable=bare-except
# pylint: disable=redundant-unittest-assert

from __future__ import annotations

from typing import Any

import unittest
import traceback

import NemAll_Python_Geometry as AllplanGeo


class UnitTestInteractorWrapper():
    """ implementation of the unit test interactor wrapper """

    interactor: Any

    @classmethod
    def process_mouse_msg(cls,
                          mouse_msg: int,
                          pnt      : AllplanGeo.Point2D,
                          msg_info : Any) -> bool:
        """
        Handles the process mouse message event

        Args:
            mouse_msg: the mouse message.
            pnt      : the input point.
            msg_info : additional message info.

        Returns:
            True/False for success.
        """

        try:
            return cls.interactor.process_mouse_msg(mouse_msg, pnt, msg_info)

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)

            return False


    @classmethod
    def modify_element_property(cls,
                                page : str,
                                name : str,
                                value: Any):
        """
        Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """

        try:
            cls.interactor.modify_element_property(page, name, value)

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)


    @classmethod
    def on_control_event(cls, event_id: int):
        """
        Handles the on control event

        Args:
            event_id: event id of button control.
        """

        try:
            cls.interactor.on_control_event(event_id)

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)


    @classmethod
    def on_cancel_function(cls) -> bool:
        """
        Handles the cancel function event (e.g. by ESC, ...)

        Returns:
            True/False for success.
        """

        try:
            return cls.interactor.on_cancel_function()

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)

            return False


    @classmethod
    def on_preview_draw(cls):
        """
        Handles the preview draw event
        """

        try:
            cls.interactor.on_preview_draw()

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)


    @classmethod
    def on_mouse_leave(cls):
        """
        Handles the mouse leave event
        """

        try:
            cls.interactor.on_mouse_leave()

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)


    @classmethod
    def on_value_input_control_enter(cls) -> bool:
        """
        Handles the enter inside the value input control event

        Returns:
            True/False for success.
        """

        try:
            return cls.interactor.on_value_input_control_enter()

        except:
            traceback.print_exc()

            unittest.TestCase().assertTrue(False)

            return False


class UnitTestInteractor(type):
    "Implementation of the unit test interactor."

    def __new__(cls, interactor) -> UnitTestInteractor:
        """ create the unit test interactor

        Args:
            interactor: original interactor

        Returns:
            unit test interactor
        """

        return super().__new__(cls, "UnitTestInteractor", (UnitTestInteractorWrapper, ), interactor.__dict__)


    def __init__(cls, interactor):
        """ initialize

        Args:
            interactor: interactor
        """

        cls.interactor = interactor

        super().__init__(interactor)
