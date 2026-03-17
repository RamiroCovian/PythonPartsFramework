""" implementation of the include data
"""

from dataclasses import dataclass, field

@dataclass
class IncludeData:
    """ implementation of the include data
    """

    is_include  : bool           = False
    incl_visible: dict[str, str] = field(default_factory = dict)
    name_postfix: str            = ""
    text_postfix: str            = ""
