""" Implementation of the mock class for the BuildingElementInputControls.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name

from __future__ import annotations

import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Geometry as AllplanGeo

class BuildingElementInputControlsMock():
    """ Implementation of the mock class for the BuildingElementInputControls
    """

    def CloseControls(self):
        """Close the input controls
        """

    def CreateControls(self,
                       _handlePropList : object,
                       _insertionMat   : AllplanGeo.Matrix3D,
                       _viewProj       : AllplanIFW.ViewWorldProjection,
                       _bUpdateControls: bool,
                       _assoRefObj     : object):
        """ Create the controls

        Args:
            _handlePropList:  List with the handle properties
            _insertionMat:    Transformation matrix
            _viewProj:        View world projection
            _bUpdateControls: Update the controls: true/false
            _assoRefObj:      Reference element for the drawing inside the associative views
        """

    def __init__(self):     # type: ignore
        """Initialize
        """
