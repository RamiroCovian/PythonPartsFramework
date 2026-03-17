""" implementation of the CreateSectionsAndViews mock. """

# pylint: disable=invalid-name

from typing import List

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

def CreateSectionsAndViewsMock(_doc              : AllplanEleAdapter.DocumentAdapter,
                               _insertion_mat    : AllplanGeo.Matrix3D,
                               _elements         : AllplanEleAdapter.BaseElementAdapterList,
                               _section_view_list: List,
                               _view_proj        : AllplanIFW.ViewWorldProjection,
                               _undo_redo_service: object = None) -> AllplanGeo.MinMax2DList:
    """ implementation of the CreateSectionAndViews mock

    Args:
        _doc:               document of the Allplan drawing files
        _insertion_mat:     placement matrix
        _elements:          element
        _section_view_list: list with the section and views
        _view_proj:         view world projection
        _undo_redo_service: undo/redo service

    Returns:
        min/max list
    """

    return AllplanGeo.MinMax2DList()
