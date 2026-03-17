""" implementation of the curved geometry element filter
"""

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from ScriptObjectInteractors.BaseFilterObject import BaseFilterObject

from TypeCollections.GeometryTyping import GeometryTyping

class CurvedGeometryElementFilter(BaseFilterObject):
    """ implementation of the curved geometry element filter
    """

    def __init__(self,
                 filter_curve_2d: bool,
                 filter_curve_3d: bool):
        """ initialize

        Args:
            filter_curve_2d: filter 2D curves
            filter_curve_3d: filter 3D curves
        """

        self.filter_curve_2d = filter_curve_2d
        self.filter_curve_3d = filter_curve_3d


    def __call__(self,
                 element: AllplanEleAdapter.BaseElementAdapter) -> bool:
        """ execute the filtering

        Args:
            element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

        if (geo_ele := element.GetGeometry()) is None:
            return False

        if GeometryTyping.is_curve_2d(geo_ele):
            return self.filter_curve_2d

        return self.filter_curve_3d if GeometryTyping.is_curve_3d(geo_ele) else False
