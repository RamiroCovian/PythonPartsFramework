""" Implementation of the text reference points
"""

import enum

class TextReferencePointPosition(enum.IntEnum):
    """ Definition of the text reference points
    """

    BOTTOM_LEFT   = 1
    BOTTOM_CENTER = 2
    BOTTOM_RIGHT  = 3
    CENTER_LEFT   = 4
    CENTER_CENTER = 5
    CENTER_RIGHT  = 6
    TOP_LEFT      = 7
    TOP_CENTER    = 8
    TOP_RIGHT     = 9
