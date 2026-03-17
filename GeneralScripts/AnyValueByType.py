""" implementation of the data class for the AnyValueByType value type """

from __future__ import annotations

from typing import Any

import sys

from dataclasses import dataclass
from types import ModuleType

@dataclass
class AnyValueByType():
    """ implementation of the data class for the attribute id and value """

    value_type : str = ""
    text       : str = ""
    value      : Any = ""
    value_list : str = ""
    min_value  : str = ""
    max_value  : str = ""

    def deep_copy(self) -> AnyValueByType:
        """ execute a deep copy

        Returns:
            copied object
        """

        return AnyValueByType(self.value_type, self.text, self.value,
                              self.value_list, self.min_value, self.max_value)


    def __gt__(self,
               any_value: AnyValueByType) -> bool:
        """ > operator overloading

        Args:
            any_value: value to compare

        Returns:
            value is greater than value to compare with
        """

        return self.value > any_value.value


def __reload__(_mod: ModuleType) -> Any:
    """ don't reload this module to avoid problems with the enum check

    Args:
        _mod: module

    Returns:
        current module
    """

    return sys.modules[__name__]
