# -*- coding: utf-8 -*-
import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class Caixeti2UTObject3D:
    """
    Caixeti 2 UT – EN Electricitat.

    Versión sin duplicados de Caixeti2Object3D (TD).
    Misma geometría y colores, cada elemento × 1.
    """

    WIDTH     = 140.0
    TOP_WIDTH = 50.0
    DEPTH     = 40.0
    HEIGHT    = 150.0
    CHAMFER_Z = 50.0

    INT_HEIGHT    = 70.0
    INT_RADIUS    = 35.0
    ARC_SEGMENTS  = 16

    INT_EXT_HEIGHT   = 68.0
    INT_EXT_WIDTH    = 138.03
    INT_EXT_DEPTH    = 50.0
    INT_EXT_OVERHANG = 15.0

    CYL_BACK_RADIUS  = 34.0
    CYL_BACK_LENGTH  = 16.0
    CYL_BACK_MARGIN  = 1.0

    def __init__(self) -> None:
        self.geo_tools = CreateSmartGeo()

    def _create_cuerpo(self, color: int) -> list:
        half_w   = self.WIDTH / 2.0
        half_d   = self.DEPTH / 2.0
        top_half = self.TOP_WIDTH / 2.0
        y_plane  = -half_d

        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(-half_w,   y_plane, 0)
        polygon += AllplanGeo.Point3D( half_w,   y_plane, 0)
        polygon += AllplanGeo.Point3D( half_w,   y_plane, self.CHAMFER_Z)
        polygon += AllplanGeo.Point3D( top_half, y_plane, self.HEIGHT)
        polygon += AllplanGeo.Point3D(-top_half, y_plane, self.HEIGHT)
        polygon += AllplanGeo.Point3D(-half_w,   y_plane, self.CHAMFER_Z)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, self.DEPTH, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return []

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return []

        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        return [AllplanBasisElements.ModelElement3D(prop, brep)]

    def _create_interior(self, color: int) -> list:
        r             = self.INT_RADIUS
        half_d        = self.DEPTH / 2.0
        y_plane       = -half_d
        half_straight = (self.WIDTH - 2.0 * r) / 2.0
        mid_z         = 0.0
        n             = self.ARC_SEGMENTS

        points = []
        for i in range(n + 1):
            angle = -math.pi / 2.0 + math.pi * i / n
            points.append((half_straight + r * math.cos(angle), mid_z + r * math.sin(angle)))
        for i in range(n + 1):
            angle = math.pi / 2.0 + math.pi * i / n
            points.append((-half_straight + r * math.cos(angle), mid_z + r * math.sin(angle)))

        polygon = AllplanGeo.Polygon3D()
        for (x, z) in points:
            polygon += AllplanGeo.Point3D(x, y_plane, z)
        polygon += AllplanGeo.Point3D(points[0][0], y_plane, points[0][1])

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, self.DEPTH, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return []

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return []

        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        return [AllplanBasisElements.ModelElement3D(prop, brep)]

    def _create_interior_ext(self, color: int) -> list:
        r             = self.INT_EXT_HEIGHT / 2.0
        half_d        = self.DEPTH / 2.0
        overhang      = self.INT_EXT_OVERHANG
        depth         = self.INT_EXT_DEPTH
        y_plane       = half_d + overhang - depth
        half_straight = (self.INT_EXT_WIDTH - 2.0 * r) / 2.0
        mid_z         = 0.0
        n             = self.ARC_SEGMENTS

        points = []
        for i in range(n + 1):
            angle = -math.pi / 2.0 + math.pi * i / n
            points.append((half_straight + r * math.cos(angle), mid_z + r * math.sin(angle)))
        for i in range(n + 1):
            angle = math.pi / 2.0 + math.pi * i / n
            points.append((-half_straight + r * math.cos(angle), mid_z + r * math.sin(angle)))

        polygon = AllplanGeo.Polygon3D()
        for (x, z) in points:
            polygon += AllplanGeo.Point3D(x, y_plane, z)
        polygon += AllplanGeo.Point3D(points[0][0], y_plane, points[0][1])

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, depth, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return []

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return []

        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        return [AllplanBasisElements.ModelElement3D(prop, brep)]

    def _create_cilindros_base(self, color: int) -> ModelEleList:
        half_d        = self.DEPTH / 2.0
        cyl_radius    = 10.0
        cyl_x         = self.INT_RADIUS
        cyl_z         = -self.INT_RADIUS
        y_dir         = AllplanGeo.Vector3D(0, 1, 0)

        bases = [
            {"type": "cylinder", "radius": cyl_radius * 2.0, "height": self.DEPTH,
             "base_point": (-cyl_x, -half_d, cyl_z), "direction": y_dir,
             "color": color, "operations": []},
            {"type": "cylinder", "radius": cyl_radius * 2.0, "height": self.DEPTH,
             "base_point": ( cyl_x, -half_d, cyl_z), "direction": y_dir,
             "color": color, "operations": []},
        ]
        return self.geo_tools.build_from_description({"bases": bases})

    def _create_caja_trasera(self, color: int) -> list:
        half_d  = self.DEPTH / 2.0
        half_x  = 70.0 / 2.0
        half_z  = 68.0 / 2.0
        depth   = 16.0
        y_plane = half_d

        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(-half_x, y_plane, -half_z)
        polygon += AllplanGeo.Point3D( half_x, y_plane, -half_z)
        polygon += AllplanGeo.Point3D( half_x, y_plane,  half_z)
        polygon += AllplanGeo.Point3D(-half_x, y_plane,  half_z)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, depth, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return []

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return []

        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        return [AllplanBasisElements.ModelElement3D(prop, brep)]

    def _create_cilindros_traseros(self, color: int) -> ModelEleList:
        half_w  = self.WIDTH / 2.0
        half_d  = self.DEPTH / 2.0
        cyl_x   = half_w - self.CYL_BACK_MARGIN - self.CYL_BACK_RADIUS
        y_dir   = AllplanGeo.Vector3D(0, 1, 0)

        bases = [
            {"type": "cylinder", "radius": self.CYL_BACK_RADIUS * 2.0, "height": self.CYL_BACK_LENGTH,
             "base_point": (-cyl_x, half_d, 0.0), "direction": y_dir,
             "color": color, "operations": []},
            {"type": "cylinder", "radius": self.CYL_BACK_RADIUS * 2.0, "height": self.CYL_BACK_LENGTH,
             "base_point": ( cyl_x, half_d, 0.0), "direction": y_dir,
             "color": color, "operations": []},
        ]
        return self.geo_tools.build_from_description({"bases": bases})

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_cuerpo(color=5):
            result.append(ele)
        for ele in self._create_interior(color=5):
            result.append(ele)
        for ele in self._create_interior_ext(color=1):
            result.append(ele)
        for ele in self._create_cilindros_base(color=5):
            result.append(ele)
        for ele in self._create_caja_trasera(color=28):
            result.append(ele)
        for ele in self._create_cilindros_traseros(color=28):
            result.append(ele)
        return result
