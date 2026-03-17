""" implementation of the mock for PolylineInput
"""

# pylint: disable=invalid-name

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from .CoordinateInputMock import CoordinateInputMock

class PolylineInputMock(CoordinateInputMock):
    """Implementation of the polyline input mock
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

        self.polyline += self.coord_input.GetInputPoint(mouseMsg, pnt, pMsgInfo).GetPoint()

        return 1

    def GetPolyline(self) -> AllplanGeo.Polyline3D:
        """get the final polyline

        Returns:
            final polyline
        """

        return self.polyline


    def GetPreviewPolyline(self) -> AllplanGeo.Polyline3D:
        """get the preview polyline

        Returns:
            preview polyline
        """

        return self.polyline


    def StartNewInput(self):
        """Start new input
        """

        self.polyline = AllplanGeo.Polyline3D()


    def __init__(self,
                 coordInput: CoordinateInputMock,
                 _bZCoord  : bool):
        """ initialize

        Args:
            coordInput: Coordinate input object
            _bZCoord:   Z-coordinate input state
        """

        self.coord_input = coordInput

        self.polyline = AllplanGeo.Polyline3D()


    #--------------------- mocked functions

    def GetInputViewDocument(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the input view document

        Returns:
            input view document
        """

        return self.coord_input.GetInputViewDocument()
