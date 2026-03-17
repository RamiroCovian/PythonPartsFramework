""" implementation of the geometry element collection
"""

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil

class GeometryElementCollection():
    """ implementation of the geometry element collection
    """

    @staticmethod
    def create_line2d_plus_to_minus() -> AllplanGeo.Line2D:
        """ create a 2D line from plus to minus coordinates

        Returns:
            2D line
        """
        return AllplanGeo.Line2D(3000, 4000, -2000, -4000)


    @staticmethod
    def create_line3d_plus_to_minus() -> AllplanGeo.Line3D:
        """ create a 3D line from plus to minus coordinates

        Returns:
            3D line
        """
        return AllplanGeo.Line3D(3000, 4000, 5000, -2000, -4000, -1000)


    @staticmethod
    def create_polyline2d_as_u() -> AllplanGeo.Polyline2D:
        """create a 2D polyline as U

        Returns:
            2D polyline
        """

        return AllplanGeo.Polyline2D([AllplanGeo.Point2D(0, 1000), AllplanGeo.Point2D(0, 0),
                                      AllplanGeo.Point2D(2000, 0), AllplanGeo.Point2D(2000, 1000)])


    @staticmethod
    def create_polyline3d_as_u() -> AllplanGeo.Polyline3D:
        """create a 3D polyline as U

        Returns:
            3D polyline
        """

        return AllplanGeo.Polyline3D([AllplanGeo.Point3D(0, 0, 1000), AllplanGeo.Point3D(0, 0, 0),
                                      AllplanGeo.Point3D(2000, 0, 0), AllplanGeo.Point3D(2000, 0, 1000)])


    @staticmethod
    def create_polygon2d_as_box() -> AllplanGeo.Polygon2D:
        """create a 2D polygon as U

        Returns:
            2D polygon
        """

        return AllplanGeo.Polygon2D([AllplanGeo.Point2D(0, 1000), AllplanGeo.Point2D(0, 0),
                                     AllplanGeo.Point2D(2000, 0), AllplanGeo.Point2D(2000, 1000),
                                     AllplanGeo.Point2D(0, 1000)])


    @staticmethod
    def create_polygon3d_as_box() -> AllplanGeo.Polygon3D:
        """create a 3D polygon as U

        Returns:
            3D polygon
        """

        return AllplanGeo.Polygon3D([AllplanGeo.Point3D(0, 0, 1000), AllplanGeo.Point3D(0, 0, 0),
                                     AllplanGeo.Point3D(2000, 0, 0), AllplanGeo.Point3D(2000, 0, 1000),
                                     AllplanGeo.Point3D(0, 0, 1000)])

    @staticmethod
    def create_arc2d_0_270() -> AllplanGeo.Arc2D:
        """ create a 2D arc with 270 deg

        Returns:
            2D arc
        """
        return AllplanGeo.Arc2D(AllplanGeo.Point2D(), 5000, 5000, 0, 0, 1.5 * math.pi)

    @staticmethod
    def create_arc3d_0_270(z_coord: float = 0) -> AllplanGeo.Arc3D:
        """ create a 3D arc with 270 deg

        Args:
            z_coord: z coordinate of the arc

        Returns:
            3D arc
        """
        return AllplanGeo.Arc3D(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, z_coord),
                                                           AllplanGeo.Vector3D(1, 0, 0),
                                                           AllplanGeo.Vector3D(0, 0, 1)),
                                                           5000, 5000, 0, 1.5 * math.pi)

    def create_arc3d_ellipse_90_270():
        """ create a 3D elliptic arc with 180 deg

        Args:
            z_coord: z coordinate of the arc

        Returns:
            3D arc
        """
        return AllplanGeo.Arc3D(AllplanGeo.Point3D(50, 10, 75), AllplanGeo.Vector3D(1, 0, 0),
                                AllplanGeo.Vector3D(0, 0 , 1),
                                100, 200,
                                math.pi / 2, math.pi * 1.5)


    @staticmethod
    def create_spline2d() -> AllplanGeo.Spline2D:
        """ create a 2D spline

        Returns:
            2D spline
        """
        spline = AllplanGeo.Spline2D([AllplanGeo.Point2D(0, 0), AllplanGeo.Point2D(3000, 1000),
                                      AllplanGeo.Point2D(7000, -500),  AllplanGeo.Point2D(12000, -2500),
                                      AllplanGeo.Point2D(15000, -1000)])

        return spline


    @staticmethod
    def create_spline3d() -> AllplanGeo.Spline3D:
        """ create a 3D spline

        Returns:
            3D spline
        """
        return AllplanGeo.Spline3D([AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(3000, 0, 1000),
                                    AllplanGeo.Point3D(7000, 0, -500),  AllplanGeo.Point3D(13000, 0, -3500),
                                    AllplanGeo.Point3D(15000, 0, -1000)])

    @staticmethod
    def create_bspline2d() -> AllplanGeo.BSpline2D:
        """ create a 2D bspline

        Returns:
            3D bspline
        """
        points_list = AllplanGeo.Point2DList()
        weights     = AllplanUtil.VecDoubleList()
        knots       = AllplanUtil.VecDoubleList()

        points_list[:] = [AllplanGeo.Point2D(0, 0), AllplanGeo.Point2D(1000, 2000),
                          AllplanGeo.Point2D(3000, 1000), AllplanGeo.Point2D(5000, -2000)]

        weights[:] = [1, 1, 1, 1]
        knots[:]   = [-2, -1, 0, 1, 2, 3, 4, 5]

        return AllplanGeo.BSpline2D(points_list, weights, knots, 3, False)

    @staticmethod
    def create_bspline3d(z_coord: float = 0) -> AllplanGeo.BSpline3D:
        """ create a 3D bspline

        Args:
            z_coord: z coordinate

        Returns:
            3D bspline
        """

        points_list = AllplanGeo.Point3DList()
        points_list[:] = [AllplanGeo.Point3D(0, 0, z_coord), AllplanGeo.Point3D(1000, 2000, z_coord),
                          AllplanGeo.Point3D(3000, 1000, z_coord), AllplanGeo.Point3D(5000, -2000, z_coord)]

        return AllplanGeo.BSpline3D.CreateBSplineInterpolated(points_list, 3, False)

    @staticmethod
    def create_clothoid2d() -> AllplanGeo.Clothoid2D:
        """create a 2D clothoid

        Returns:
            2D clothoid
        """

        clothoid = AllplanGeo.Clothoid2D()

        clothoid.SetStartPoint(AllplanGeo.Point2D(1000, 2000))
        clothoid.SetEndPoint(AllplanGeo.Point2D(2000, 2000))
        clothoid.SetRefPoint(AllplanGeo.Point2D(1000, 1000))
        clothoid.SetStartVector(AllplanGeo.Vector2D(1000, 1000))
        clothoid.SetStartCurvature(3)
        clothoid.SetEndCurvature(4)
        clothoid.SetLength(2)
        clothoid.SetParallel(1)

        return clothoid

    @staticmethod
    def create_path2d() -> AllplanGeo.Path2D:
        """ create a 2D path

        Returns:
            2D path
        """

        arc = GeometryElementCollection.create_arc2d_0_270()

        line = AllplanGeo.Line2D(arc.EndPoint, AllplanGeo.Point2D(5000, -5000))

        path = AllplanGeo.Path2D()

        path += arc
        path += line

        return path

    @staticmethod
    def create_path3d(z_coord: float = 0) -> AllplanGeo.Path3D:
        """ create a 3D path

        Args:
            z_coord: z coordinate of the path

        Returns:
            3D path
        """

        arc = GeometryElementCollection.create_arc3d_0_270(z_coord)

        line = AllplanGeo.Line3D(arc.EndPoint, AllplanGeo.Point3D(5000, -5000, z_coord))

        path = AllplanGeo.Path3D()

        path += arc
        path += line

        return path

    @staticmethod
    def create_polyhedron3d_as_box() -> AllplanGeo.Polyhedron3D:
        """ create a box as 3D polyhedron

        Returns:
            3D polyhedron
        """
        return AllplanGeo.Polyhedron3D.CreateCuboid(AllplanGeo.Point3D(-1000, -2000, -3000), AllplanGeo.Point3D(1000, 2000, 3000))

    @staticmethod
    def create_brep3d_as_cylinder():
        """ create a cylinder as 3D bRep

        Returns:
            3D brep
        """
        return AllplanGeo.BRep3D.CreateCylinder(AllplanGeo.AxisPlacement3D(), 1000, 2000)
