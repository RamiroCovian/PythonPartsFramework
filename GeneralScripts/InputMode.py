"""
Implementation of the input mode enumeration
"""

import enum

class InputMode(enum.IntEnum):
    """
    Definition of class InputMode
    """
    GeoExpand    = 1
    RefPoint     = 2
    HandleSelect = 3
    HandleModify = 4
    HandleNext   = 5
    Interactor   = 6
    WriteToDB    = 7


