""" implementation of the geometry typing
"""

from typing import get_args

import NemAll_Python_Geometry as AllplanGeo

CURVES_2D = (AllplanGeo.Line2D | AllplanGeo.Arc2D | AllplanGeo.Polyline2D | AllplanGeo.Polygon2D |
             AllplanGeo.Spline2D | AllplanGeo.BSpline2D | AllplanGeo.Path2D)

CURVES_3D = (AllplanGeo.Line3D | AllplanGeo.Arc3D | AllplanGeo.Polyline3D | AllplanGeo.Polygon3D |
             AllplanGeo.Spline3D | AllplanGeo.BSpline3D | AllplanGeo.Path3D)

CURVES = (AllplanGeo.Line2D | AllplanGeo.Arc2D | AllplanGeo.Polyline2D | AllplanGeo.Polygon2D |
          AllplanGeo.Spline2D | AllplanGeo.BSpline2D | AllplanGeo.Path2D |
          AllplanGeo.Line3D | AllplanGeo.Arc3D | AllplanGeo.Polyline3D | AllplanGeo.Polygon3D |
          AllplanGeo.Spline3D | AllplanGeo.BSpline3D | AllplanGeo.Path3D | None)

LINEAR_CURVES_3D = AllplanGeo.Line3D | AllplanGeo.Polyline3D | AllplanGeo.Polygon3D


class GeometryTyping():
    """ implementation of the geometry element typing
    """

    @staticmethod
    def is_curve_2d(geo_ele: CURVES) -> bool:
        """ test for a 2D curve

        Args:
            geo_ele: geometry element

        Returns:
            curve 2D state
        """

        return isinstance(geo_ele, get_args(CURVES_2D))


    @staticmethod
    def is_curve_3d(geo_ele: CURVES) -> bool:
        """ test for a 3D curve

        Args:
            geo_ele: geometry element

        Returns:
            curve 3D state
        """

        return isinstance(geo_ele, get_args(CURVES_3D))
