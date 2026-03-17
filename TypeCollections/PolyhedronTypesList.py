""" implementation of the list for the polyhedron types
"""

import NemAll_Python_Geometry as AllplanGeo

class PolyhedronTypesList(list[(AllplanGeo.Polyhedron3D | AllplanGeo.Cylinder3D | AllplanGeo.ExtrudedAreaSolid3D |
                                AllplanGeo.Polygon3D | AllplanGeo.Line3D | AllplanGeo.Polyline3D | AllplanGeo.ClippedSweptSolid3D)]):
    """implementation of the list for the polyhedron types
    """
