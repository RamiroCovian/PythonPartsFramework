""" implementation of the mock function for DrawElementPreview.
"""

# pylint: disable=invalid-name

from typing import List

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

def DrawElementPreviewMock(_doc                    : AllplanEleAdapter.DocumentAdapter,
                           _insertionMat           : AllplanGeo.Matrix3D,
                           _modelEleList           : List,
                           _bDirectDraw            : int,
                           _assoRefObj             : object,
                           _asStaticPreview        : bool = False,
                           _addToPreviewBoundingBox: bool = True):
    """ Draw the preview of the elements

    Args:
        _doc:                     document of the Allplan drawing files
        _insertionMat:            Matrix with the placement point and the rotation
        _modelEleList:            List with the model elements
        _bDirectDraw:             description
        _assoRefObj:              Associative view reference object
        _asStaticPreview:         Draw as static preview: true/false
        _addToPreviewBoundingBox: Add the elements to the bounding box of the preview
    """
