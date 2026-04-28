# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class Caixeti1Object3D:
    """
    Caixeti 1 – TD Electricitat.

    Convención de ejes:
      - Ancho : X (90mm base, centrado en X=0)
      - Prof.  : Y (40mm, centrado en Y=0)
      - Altura : Z (150mm)

    Composición:
      - Cuerpo trapezoidal × 2                     color 5
      - Cilindros pequeños 10mm × 2 (cada uno)     color 5
      - Cilindro mediano 35mm × 2                  color 5
      - Cilindro grande 34mm × 50mm × 1            color 1
      - Cilindro trasero 34mm × 16mm × 1           color 28
    """

    WIDTH     = 90.0
    TOP_WIDTH = 40.0
    DEPTH     = 40.0
    HEIGHT    = 150.0
    CHAMFER_Z = 50.0

    CYL_RADIUS = 10.0
    CYL_Z      = 0.0

    CYL_BIG_RADIUS   = 34.0
    CYL_BIG_LENGTH   = 50.0
    CYL_BIG_OVERHANG = 15.0

    CYL_MED_RADIUS = 35.0

    CYL_BACK_RADIUS = 34.0
    CYL_BACK_LENGTH = 16.0

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
        elem = AllplanBasisElements.ModelElement3D(prop, brep)
        return [elem, elem]  # duplicado × 2

    def _create_cilindros(self) -> ModelEleList:
        half_w = self.WIDTH / 2.0
        half_d = self.DEPTH / 2.0
        y_dir  = AllplanGeo.Vector3D(0, 1, 0)

        cyl_x       = half_w - self.CYL_RADIUS
        big_y_start = (half_d + self.CYL_BIG_OVERHANG) - self.CYL_BIG_LENGTH  # -15mm

        bases = []

        # Cilindros pequeños 10mm — color 5 — × 2 cada uno
        for _ in range(2):
            bases.append({
                "type": "cylinder",
                "radius": self.CYL_RADIUS * 2.0,
                "height": self.DEPTH,
                "base_point": (-cyl_x, -half_d, self.CYL_Z),
                "direction": y_dir,
                "color": 5,
                "operations": [],
            })
            bases.append({
                "type": "cylinder",
                "radius": self.CYL_RADIUS * 2.0,
                "height": self.DEPTH,
                "base_point": (cyl_x, -half_d, self.CYL_Z),
                "direction": y_dir,
                "color": 5,
                "operations": [],
            })

        # Cilindro mediano 35mm — color 5 — × 2
        for _ in range(2):
            bases.append({
                "type": "cylinder",
                "radius": self.CYL_MED_RADIUS * 2.0,
                "height": self.DEPTH,
                "base_point": (0.0, -half_d, self.CYL_Z),
                "direction": y_dir,
                "color": 5,
                "operations": [],
            })

        # Cilindro grande 34mm × 50mm — color 1 — × 1
        bases.append({
            "type": "cylinder",
            "radius": self.CYL_BIG_RADIUS * 2.0,
            "height": self.CYL_BIG_LENGTH,
            "base_point": (0.0, big_y_start, self.CYL_Z),
            "direction": y_dir,
            "color": 1,
            "operations": [],
        })

        # Cilindro trasero 34mm × 16mm — color 28 — × 1
        bases.append({
            "type": "cylinder",
            "radius": self.CYL_BACK_RADIUS * 2.0,
            "height": self.CYL_BACK_LENGTH,
            "base_point": (0.0, half_d, self.CYL_Z),
            "direction": y_dir,
            "color": 28,
            "operations": [],
        })

        return self.geo_tools.build_from_description({"bases": bases})

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()

        for ele in self._create_cuerpo(color=5):
            result.append(ele)

        for ele in self._create_cilindros():
            result.append(ele)

        return result
