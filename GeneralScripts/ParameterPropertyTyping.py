""" implementation of the helper class for the ParameterProperty typing
"""

from typing import Generic, TypeVar

from ParameterProperty import ParameterProperty

T = TypeVar("T")

class ParameterPropertyTyping(Generic[T], ParameterProperty):
    """ generic ParameterProperty for the typing

    Args:
        Generic:           generic type
        ParameterProperty: base class
    """

    value : T
