"""
Script for BuildingElementGeometryUtil
"""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil

from ValueTypes.ValueTypeUtils.StringToValueUtil import StringToValueUtil

def _get_coordinates_list(value_str):
    """
    Get the coordinates list from a string ("(100,200)(300,400)"

    Args:
        value_str:  Value string

    Return:     list with the coordinates
    """

    if not value_str:
        return []


    #----------------- create 100,200)(300,400

    value_str = value_str.lstrip(" (").rstrip(") ")

    if not value_str:
        return []

    pnt_str_list = value_str.split(")(")

    coords_list = []

    split_chr = "," if value_str.find(",") != -1 else " "


    #----------------- create a list for the coordinates

    for pnt_str in pnt_str_list:
        coords_str_list = pnt_str.split(split_chr)

        coords_list.append([float(coord.strip()) for coord in coords_str_list])

    return coords_list


def _get_double_list(value_str):
    """
    Get the double list from a string

    Args:
        value_str:  Value string

    Return: list with the double values
    """

    if not value_str:
        return AllplanUtil.VecDoubleList()

    value_str = value_str.lstrip("(").rstrip(")")

    str_list = value_str.split(",")

    double_list = AllplanUtil.VecDoubleList()

    for double_str in str_list:
        double_list.append(float(double_str))

    return double_list


def _make_coordinate(coords):
    """
    Make the 2D/3D coordinate from a list

    Args:
        coords:     Coordinates
    """

    return AllplanGeo.Point2D(coords[0],  coords[1]) if len(coords) == 2 else AllplanGeo.Point3D(coords[0],  coords[1], coords[2])


def _make_xyz_element(value_str, min_coord_count, element):
    """
    Make an xyz element from the coordinates

    Args:
        value_str:          Value string
        min_coord_count:    Minimal coordinate count
        element:            Element
    """

    if value_str == "[]":
        return []

    coords_list = _get_coordinates_list(value_str)

    if not coords_list  or  len(coords_list[0]) < min_coord_count:
        return element

    element.X = coords_list[0][0]
    element.Y = coords_list[0][1]

    if min_coord_count == 3:
        element.Z = coords_list[0][2]

    return element


def _add_coordinates(geo_ele, value_str):
    """
    Add the coordinates to a geometry element

    Args:
        geo_ele:            Geometry element
        value_str:          Value string
    """
    coords_list = _get_coordinates_list(value_str)

    for coords in coords_list:
        geo_ele += _make_coordinate(coords)

    return geo_ele


#------------------------------------------------------------------------------------------------------------


class BuildingElementGeometryUtil():
    """
    Definition of class BuildingElementGeometryUtil

    Create the geometry element from a value string
    """

    @staticmethod
    def get_value_point2d(value_str):
        """get a 2D point from a value string"""

        return _make_xyz_element(value_str.replace("Point2D", ""), 2, AllplanGeo.Point2D())

    @staticmethod
    def get_value_point3d(value_str):
        """get a 3D point from a value string"""

        return _make_xyz_element(value_str.replace("Point3D", ""), 3, AllplanGeo.Point3D())

    @staticmethod
    def get_value_vector2d(value_str):
        """get a 2D vector from a value string"""

        return _make_xyz_element(value_str.replace("Vector2D", ""), 2, AllplanGeo.Vector2D())

    @staticmethod
    def get_value_vector3d(value_str):
        """get a 3D vector from a value string"""

        return _make_xyz_element(value_str.replace("Vector3D", ""), 3, AllplanGeo.Vector3D())

    @staticmethod
    def get_value_line2d(value_str):
        """get a 2D line from a value string"""

        coords_list = _get_coordinates_list(value_str.replace("Line2D", ""))

        if not coords_list  or  len(coords_list[0]) < 4:
            return AllplanGeo.Line2D()

        return AllplanGeo.Line2D(coords_list[0][0], coords_list[0][1], coords_list[0][2], coords_list[0][3])

    @staticmethod
    def get_value_line3d(value_str):
        """get a 2D line from a value string"""

        coords_list = _get_coordinates_list(value_str.replace("Line3D", ""))

        if not coords_list  or  len(coords_list[0]) < 6:
            return AllplanGeo.Line3D()

        return AllplanGeo.Line3D(coords_list[0][0], coords_list[0][1], coords_list[0][2],
                                 coords_list[0][3], coords_list[0][4], coords_list[0][5])

    @staticmethod
    def get_value_arc2d(value_str):
        """get a 2D arc from a value string"""

        if not value_str  or  value_str == "()":
            return AllplanGeo.Arc2D()

        return AllplanGeo.Arc2D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "CenterPoint", "(0,0)"), 2, AllplanGeo.Point2D()),
                                StringToValueUtil.get_property_float(value_str, "MinorRadius", "0"),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                StringToValueUtil.get_property_angle(value_str, "AxisAngle", "0"),
                                StringToValueUtil.get_property_angle(value_str, "StartAngle", "0"),
                                StringToValueUtil.get_property_angle(value_str, "EndAngle", "0"),
                                StringToValueUtil.get_property_int(value_str, "IsCounterClockwise", "1"))

    @staticmethod
    def get_value_arc3d(value_str):
        """get a 3D arc from a value string"""

        if not value_str  or  value_str == "()":
            return AllplanGeo.Arc3D()

        return AllplanGeo.Arc3D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "CenterPoint", "(0,0,0)"),
                                                  3, AllplanGeo.Point3D()),
                                _make_xyz_element(StringToValueUtil.get_property_string(value_str, "XDirection", "1,0,0"),
                                                  3, AllplanGeo.Vector3D()),
                                _make_xyz_element(StringToValueUtil.get_property_string(value_str, "ZAxis", "0,0,1"),
                                                  3, AllplanGeo.Vector3D()),
                                StringToValueUtil.get_property_float(value_str, "MinorRadius", "0"),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                StringToValueUtil.get_property_angle(value_str, "StartAngle", "0"),
                                StringToValueUtil.get_property_angle(value_str, "EndAngle", "0"),
                                StringToValueUtil.get_property_int(value_str, "IsCounterClockwise", "1"))

    @staticmethod
    def get_value_circle2d(value_str):
        """get a 2D circle from a value string"""

        if not value_str  or  value_str == "()":
            return AllplanGeo.Arc2D()

        return AllplanGeo.Arc2D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "CenterPoint", "(0,0)"), 2, AllplanGeo.Point2D()),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                0, 0, math.pi * 2 , True)

    @staticmethod
    def get_value_circle3d(value_str):
        """get a 3D circle from a value string"""

        if not value_str  or  value_str == "()":
            return AllplanGeo.Arc3D()

        return AllplanGeo.Arc3D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "CenterPoint", "(0,0,0)"),
                                                  3, AllplanGeo.Point3D()),
                                AllplanGeo.Vector3D(1, 0, 0),
                                _make_xyz_element(StringToValueUtil.get_property_string(value_str, "ZAxis", "0,0,1"), 3, AllplanGeo.Vector3D()),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                StringToValueUtil.get_property_float(value_str, "MajorRadius", "0"),
                                0,
                                math.pi * 2)

    @staticmethod
    def get_value_polyline2d(value_str):
        """get a 2D polyline from a value string"""

        # workaround for Plate (from Connection Toolbox Python parts)
        if value_str.find("Point2D") == 0:    # Plate / created from Polyline
            property_string = StringToValueUtil.get_property_string(value_str, "Point2D", value_str.replace("Polyline2D", ""))
        elif value_str.find("Vector2D") == 0:    # Plate / Trapezoid
            property_string = StringToValueUtil.get_property_string(value_str, "Vector2D", value_str.replace("Polyline2D", ""))
        else:
            property_string = StringToValueUtil.get_property_string(value_str, "Points", value_str.replace("Polyline2D", ""))
        return _add_coordinates(AllplanGeo.Polyline2D(), property_string)

    @staticmethod
    def get_value_polyline3d(value_str):
        """get a 3D polyline from a value string"""

        # workaround for Plate (from Connection Toolbox Python parts)
        if value_str.find("Point3D") == 0:      # Plate / created from Polyline
            property_string = StringToValueUtil.get_property_string(value_str, "Point3D", value_str.replace("Polyline3D", ""))
        elif value_str.find("Vector3D") == 0:   # Plate / Trapezoid
            property_string = StringToValueUtil.get_property_string(value_str, "Vector3D", value_str.replace("Polyline3D", ""))
        else:
            property_string = StringToValueUtil.get_property_string(value_str, "Points", value_str.replace("Polyline3D", ""))
        return _add_coordinates(AllplanGeo.Polyline3D(), property_string)

    @staticmethod
    def get_value_polygon2d(value_str):
        """get a 2D polygon from a value string"""

        return _add_coordinates(AllplanGeo.Polygon2D(),
                                StringToValueUtil.get_property_string(value_str, "Points", value_str.replace("Polygon2D", "")))

    @staticmethod
    def get_value_polygon3d(value_str):
        """get a 3D polygon from a value string"""

        return _add_coordinates(AllplanGeo.Polygon3D(),
                                StringToValueUtil.get_property_string(value_str, "Points", value_str.replace("Polygon3D", "")))

    @staticmethod
    def get_value_spline2d(value_str):
        """get a 2D spline from a value string"""

        spline = AllplanGeo.Spline2D()

        if not value_str:
            return spline

        value_str = value_str.replace("Spline2D", "")

        spline.StartVector = _make_xyz_element(StringToValueUtil.get_property_string(value_str, "StartVector", "(0,0)"), 2, AllplanGeo.Vector2D())
        spline.EndVector   = _make_xyz_element(StringToValueUtil.get_property_string(value_str, "EndVector", "(0,0)"), 2, AllplanGeo.Vector2D())

        return _add_coordinates(spline, StringToValueUtil.get_property_string(value_str, "Points", value_str))

    @staticmethod
    def get_value_spline3d(value_str):
        """get a 3D spline from a value string"""

        spline = AllplanGeo.Spline3D()

        if not value_str:
            return spline

        value_str = value_str.replace("Spline3D", "")

        spline.StartVector = _make_xyz_element(StringToValueUtil.get_property_string(value_str, "StartVector", "(0,0,0)"), 3, AllplanGeo.Vector3D())
        spline.EndVector   = _make_xyz_element(StringToValueUtil.get_property_string(value_str, "EndVector", "(0,0,0)"), 3, AllplanGeo.Vector3D())

        return _add_coordinates(spline, StringToValueUtil.get_property_string(value_str, "Points", value_str))

    @staticmethod
    def get_value_bspline2d(value_str):
        """get a 2D bspline from a value string"""

        if not value_str:
            return AllplanGeo.BSpline2D()

        value_str = value_str.replace("BSpline2D", "")

        bspline = AllplanGeo.BSpline2D(AllplanGeo.Point2DList(),
                                       _get_double_list(StringToValueUtil.get_property_string(value_str, "Weights", "")),
                                       _get_double_list(StringToValueUtil.get_property_string(value_str, "Knots", "")),
                                       StringToValueUtil.get_property_int(value_str, "Degree", "0"),
                                       StringToValueUtil.get_property_string(value_str, "IsPeriodic" ,"0") == "1")

        return _add_coordinates(bspline, StringToValueUtil.get_property_string(value_str, "Points", value_str))

    @staticmethod
    def get_value_bspline3d(value_str):
        """get a 3D bspline from a value string"""

        if not value_str:
            return AllplanGeo.BSpline3D()

        value_str = value_str.replace("BSpline3D", "")

        bspline = AllplanGeo.BSpline3D(AllplanGeo.Point3DList(),
                                       _get_double_list(StringToValueUtil.get_property_string(value_str, "Weights", "")),
                                       _get_double_list(StringToValueUtil.get_property_string(value_str, "Knots", "")),
                                       StringToValueUtil.get_property_int(value_str, "Degree", "0"),
                                       StringToValueUtil.get_property_string(value_str, "IsPeriodic", "0") == "1")

        return _add_coordinates(bspline, StringToValueUtil.get_property_string(value_str, "Points", value_str))

    @staticmethod
    def get_value_polyhedron3d(value_str: str):
        """get a 3D polyhedron from a value string"""

        polyhed = AllplanGeo.Polyhedron3D()

        if not value_str:
            return polyhed

        if value_str.find("(") != -1:
            value_str = value_str.split("(")[1]

        value_str = value_str.rstrip(") \n")

        if not value_str:
            return polyhed

        polyhed.ReadFromStream(value_str)

        return polyhed

    @staticmethod
    def get_value_brep3d(value_str: str):
        """get a 3D brep from a value string"""

        brep = AllplanGeo.BRep3D()

        if not value_str:
            return brep

        value_str = value_str.split("(", 1)[1][:-1]

        if not value_str or value_str.find("RefPoint") != -1:
            return brep

        body_str, _, matrix_str = value_str.partition(",")

        trans_mat = BuildingElementGeometryUtil.get_value_matrix3d(matrix_str)

        brep.ReadFromStream(body_str.split("(")[1].rstrip(")"), trans_mat)

        return brep

    @staticmethod
    def get_value_path2d(_):
        """get a 2D path from a value string"""

        return AllplanGeo.Path2D()

    @staticmethod
    def get_value_path3d(_):
        """get a 3D path from a value string"""

        return AllplanGeo.Path3D()

    @staticmethod
    def get_value_matrix3d(value_str):
        """get a 3D matrix from a value string"""

        if not value_str:
            return AllplanGeo.Matrix3D()

        value_list = _get_coordinates_list(StringToValueUtil.get_property_string(value_str, "Matrix3D", value_str.replace("Matrix3D", "")))

        if not value_list:
            return AllplanGeo.Matrix3D()

        value_list = value_list[0]

        return AllplanGeo.Matrix3D(value_list[0], value_list[1], value_list[2], value_list[3],
                                   value_list[4], value_list[5], value_list[6], value_list[7],
                                   value_list[8], value_list[9], value_list[10], value_list[11],
                                   value_list[12], value_list[13], value_list[14], value_list[15])

    @staticmethod
    def get_value_plane3d(value_str):
        """get a 3D plane from a value string"""

        if not value_str:
            return AllplanGeo.Plane3D()

        value_str = value_str.replace("Plane3D", "").replace("Normal", "Vector")

        return AllplanGeo.Plane3D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "Point", "(0,0,0)"),
                                                    3, AllplanGeo.Point3D()),
                                  _make_xyz_element(StringToValueUtil.get_property_string(value_str, "Vector", "(0,0,0)"),
                                                    3, AllplanGeo.Vector3D()))

    @staticmethod
    def get_value_axisplacement3d(value_str):
        """get a 3D axis placement from a value string"""

        if not value_str:
            return AllplanGeo.AxisPlacement3D()

        value_str = value_str.replace("AxisPlacement3D", "").replace(" ", "")

        return AllplanGeo.AxisPlacement3D(_make_xyz_element(StringToValueUtil.get_property_string(value_str, "Origin", "(0,0,0)"),
                                                            3, AllplanGeo.Point3D()),
                                          _make_xyz_element(StringToValueUtil.get_property_string(value_str, "XDirection", "(1,0,0)"),
                                                            3, AllplanGeo.Vector3D()),
                                          _make_xyz_element(StringToValueUtil.get_property_string(value_str, "ZDirection", "(0,0,1)"),
                                                            3, AllplanGeo.Vector3D()))

    @staticmethod
    def get_value_geometryobject(value_str):
        """ get the value from a geometry object """

        value_type = value_str.split("(")[0]

        return getattr(BuildingElementGeometryUtil, "get_value" + value_type, None)

    @staticmethod
    def get_geometry_value_type(element):
        """get the geometry value type from a geometry element"""

        value_type = str(type(element))
        value_type = value_type.replace("<class 'NemAll_Python_Geometry.", "")

        return value_type.replace("'>", "").lower()
