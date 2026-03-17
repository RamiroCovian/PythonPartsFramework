""" Implementation of the mock class for the HandleService.
"""

# pylint: disable=invalid-name

from typing import Tuple, List, Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from HandleProperties import HandleProperties

class HandleServiceMock():
    """ Implementation of the mock class for the HandleService
    """

    def __init__(self):
        """ Initialize """

        self.handles = []

    def AddHandles(self,
                   _doc       : AllplanEleAdapter.DocumentAdapter,
                   handle_list: List[HandleProperties],
                   _insert_mat: type,
                   _asso      : type):
        """ add the handles

        Args:
            _doc:        document of the Allplan drawing files
            handle_list: description
            _insert_mat: description
            _asso:       description
        """

        self.handles = handle_list


    def DrawHandles(self):
        """ draw the handles
        """


    def DeleteToolTipText(self):
        """ Delete the tooltip text
        """


    def SelectHandle(self,
                     pnt       : AllplanGeo.Point2D,
                     _view_proj: AllplanIFW.ViewWorldProjection) -> Tuple[int, AllplanGeo.Matrix3D]:
        """ select the handle

        Args:
            pnt:        input point in Allplan view coordinates
            _view_proj: description

        Returns:
            handle index, handle matrix
        """

        index = 0

        for handle in self.handles:
            if AllplanGeo.Point3D(pnt) == handle.handle_point:
                return (index, AllplanGeo.Matrix3D())

            if handle.show_handles:
                index += 1

        return (-1, AllplanGeo.Matrix3D())


    def RemoveHandles(self):
        """ remove the handles
        """

        self.handles = []

    def ShowToolTipText(self,
                        _text: str):
        """ show the tooltip text

        Args:
            _text: text
        """
