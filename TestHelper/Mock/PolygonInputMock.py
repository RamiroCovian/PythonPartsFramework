""" implementation of the mock for PolygonInput
"""

# pylint: disable=invalid-name

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from .CoordinateInputMock import CoordinateInputMock

class PolygonInputMock():
    """Implementation of the polygon input mock
    """

    def ExecuteInput(self,
                     mouseMsg: int,
                     pnt     : AllplanGeo.Point2D,
                     pMsgInfo: AllplanIFW.AddMsgInfo) -> int:
        """ Execute the input

        Args:
            mouseMsg: Mouse message
            pnt:      input point in Allplan view coordinates
            pMsgInfo: Additional message info

        Returns:
            execution state
        """

        self.polygon += self.coord_input.GetInputPoint(mouseMsg, pnt, pMsgInfo).GetPoint()

        return 1


    def GetPolygon(self) -> AllplanGeo.Polygon3D:
        """get the final polygon

        Returns:
            final polygon
        """

        return self.polygon


    def GetPreviewPolygon(self) -> AllplanGeo.Polygon3D:
        """get the preview polygon

        Returns:
            preview polygon
        """

        return self.polygon


    def StartNewInput(self):
        """Start new input
        """

        self.polygon = AllplanGeo.Polygon3D()


    def __init__(self,
                 coordInput   : CoordinateInputMock,
                 _bZCoord     : bool,
                 _multiPolygon: bool):
        """ initialize

        Args:
            coordInput:    Coordinate input object
            _bZCoord:      Z-coordinate input state
            _multiPolygon: Multi polygon with openings, ...
        """

        self.coord_input = coordInput

        self.polygon = AllplanGeo.Polygon3D()


    #--------------------- mocked functions

    def GetInputViewDocument(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the input view document

        Returns:
            input view document
        """

        return self.coord_input.GetInputViewDocument()


    def GetActiveViewDocument(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the active view document

        Returns:
            active view document
        """

        return self.coord_input.GetActiveViewDocument()
