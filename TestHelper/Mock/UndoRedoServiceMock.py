""" implementation of the mock for the UndoRedoService. """

# pylint: disable=invalid-name

import NemAll_Python_IFW_Input as AllplanIFW

from .CreateElementsMock import set_clear_model_elements

ORG_UNDO_REDO_SERVICE = AllplanIFW.UndoRedoService

class UndoRedoServiceMock(AllplanIFW.UndoRedoService):
    """ implementation of the mock for the UndoRedoService """

    def CreateUndoStep(self, _eventID: int = 0) -> None:
        """ Create an undo step

        Parameter: eventID  Event ID of the undo step
        """

        set_clear_model_elements()

        super().CreateUndoStep(0)
