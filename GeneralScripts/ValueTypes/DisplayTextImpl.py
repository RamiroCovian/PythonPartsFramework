""" implementation of the DisplayText value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from .ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class DisplayTextImpl(BaseStrImpl):                 # pylint: disable=too-few-public-methods
    """ implementation of the DisplayText value type
    """
