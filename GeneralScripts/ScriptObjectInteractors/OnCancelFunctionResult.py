""" implementation of the OnCancelFunctionResult
"""

from typing import Any

import sys
import enum

from types import ModuleType

def __reload__(_mod: ModuleType) -> Any:
    """ don't reload this module to avoid problems with the enum check

    Args:
        _mod: module

    Returns:
        current module
    """

    return sys.modules[__name__]


class OnCancelFunctionResult(enum.IntEnum):
    """ enumeration for the on_cancel_function result
    """

    CANCEL_INPUT    = 1
    CONTINUE_INPUT  = 2
    CREATE_ELEMENTS = 3
    NOT_IMPLEMENTED = 4
    RESTART         = 5
