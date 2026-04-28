# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class PorterAplics3D:
    """
    Porter i Aplics – TD Electricitat.

    Convención de ejes:
      - Ancho : X (40mm, centrado en X=0)
      - Prof.  : Y (40mm base → 20mm tope, centrado en Y=0)
      - Altura : Z (150mm)

    A diferencia del Caixeti 1, el chanfle reduce la PROFUNDIDAD (Y),
    no el ancho (X). El polígono va en el plano YZ extruido en X.

    Composición:
      - Cuerpo trapezoidal × 2            color 5
      - Cilindro base (r=20mm, L=40mm) × 2  color 5
        orientado en X, centrado en Y=0, Z=0
    """

    WIDTH     = 40.0   # X (constante en toda la altura)
    DEPTH     = 40.0   # Y base
    TOP_DEPTH = 20.0   # Y tope
    HEIGHT    = 150.0  # Z total
    CHAMFER_Z =  50.0  # Z donde arranca el chanfle

    CYL_RADIUS = 20.0  # radio real del cilindro base

    def __init__(self) -> None:
        self.geo_tools = CreateSmartGeo()

    def _create_cuerpo(self, color: int) -> list:
        """
        Polígono en el plano YZ (x=-half_w), extruido WIDTH mm en +X.
        El chanfle reduce Y simétricamente de DEPTH (40mm) a TOP_DEPTH (20mm).
        """
        half_w     = self.WIDTH / 2.0      # 20mm
        half_d     = self.DEPTH / 2.0      # 20mm
        top_half_d = self.TOP_DEPTH / 2.0  # 10mm
        x_plane    = -half_w               # -20mm

        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(x_plane, -half_d,     0)
        polygon += AllplanGeo.Point3D(x_plane,  half_d,     0)
        polygon += AllplanGeo.Point3D(x_plane,  half_d,     self.CHAMFER_Z)
        polygon += AllplanGeo.Point3D(x_plane,  top_half_d, self.HEIGHT)
        polygon += AllplanGeo.Point3D(x_plane, -top_half_d, self.HEIGHT)
        polygon += AllplanGeo.Point3D(x_plane, -half_d,     self.CHAMFER_Z)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(self.WIDTH, 0, 0))
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
        return [elem, elem]

    def _create_cilindro_base(self, color: int) -> ModelEleList:
        """
        Cilindro r=20mm, L=40mm orientado en X.
        Centro en Y=0, Z=0 (base del cuerpo).
        base_point = (-half_w, 0, 0), direction = (1, 0, 0).
        """
        half_w = self.WIDTH / 2.0   # 20mm
        x_dir  = AllplanGeo.Vector3D(1, 0, 0)
        x_axis = AllplanGeo.Vector3D(0, 1, 0)   # perpendicular a direction

        bases = [
            {
                "type": "cylinder",
                "radius": self.CYL_RADIUS * 2.0,
                "height": self.WIDTH,
                "base_point": (-half_w, 0.0, 0.0),
                "direction": x_dir,
                "x_axis": x_axis,
                "color": color,
                "operations": [],
            },
            {
                "type": "cylinder",
                "radius": self.CYL_RADIUS * 2.0,
                "height": self.WIDTH,
                "base_point": (-half_w, 0.0, 0.0),
                "direction": x_dir,
                "x_axis": x_axis,
                "color": color,
                "operations": [],
            },
            # Cilindro saliente color 28 — continúa desde x=+half_w hacia +X
            {
                "type": "cylinder",
                "radius": self.CYL_RADIUS * 2.0,
                "height": 16.0,
                "base_point": (half_w, 0.0, 0.0),
                "direction": x_dir,
                "x_axis": x_axis,
                "color": 28,
                "operations": [],
            },
        ]
        return self.geo_tools.build_from_description({"bases": bases})

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_cuerpo(color=5):
            result.append(ele)
        for ele in self._create_cilindro_base(color=5):
            result.append(ele)
        return result
