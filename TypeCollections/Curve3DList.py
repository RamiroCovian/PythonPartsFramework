""" implementation of the list for the 3D curve elements
"""

import NemAll_Python_Geometry as AllplanGeo

class Curve3DList(list[(AllplanGeo.Arc3D | AllplanGeo.BSpline3D | AllplanGeo.Line3D | \
                        AllplanGeo.Path3D | AllplanGeo.Polyline3D | AllplanGeo.Polygon3D | AllplanGeo.Spline3D)]):
    """ implementation of the list for the 3D curve elements
    """
