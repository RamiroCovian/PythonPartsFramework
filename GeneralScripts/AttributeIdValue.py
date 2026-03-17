""" implementation of the data class for the attribute id and value """

from typing import Any

from dataclasses import dataclass
from types import ModuleType

import sys

@dataclass
class AttributeIdValue():
    """ implementation of the data class for the attribute id and value """

    attribute_id : int = 0
    value        : Any = ""


def __reload__(_mod: ModuleType) -> Any:
    """ don't reload this module to avoid problems with the enum check

    Args:
        _mod: module

    Returns:
        current module
    """

    return sys.modules[__name__]
