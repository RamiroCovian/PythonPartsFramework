""" implementation of the palette data
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from BuildingElement import BuildingElement
    from BuildingElementStringTable import BuildingElementStringTable

@dataclass
class PaletteData:
    """ implementation of the palette data
    """

    page_enable_cond : str
    param_dict       : dict[str, Any]
    page_index       : int
    picture_path     : str
    global_str_table : BuildingElementStringTable
    build_ele        : BuildingElement
    row              : int
    is_visual_script : bool

    expander_name      : str  = "???"
    expander_visible   : bool = True

    row_name      : str  = ""
    row_visible   : bool = True
    row_full_text : str  = ""
