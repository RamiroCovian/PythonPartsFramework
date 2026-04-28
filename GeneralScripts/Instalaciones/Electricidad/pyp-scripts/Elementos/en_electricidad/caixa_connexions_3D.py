# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class CaixaConnexionsObject3D:
    """
    Caixa connexions – Caja de conexiones eléctrica (EN Electricitat).
    """

    def __init__(self) -> None:
        self.geo_tools = CreateSmartGeo()

    def _cuerpo_1(self, length: float, width: float, height: float, z_offset: float, color: int) -> dict:
        W = float(max(width, 10.0))
        L = float(max(length, 10.0))
        return {
            "type": "cubo",
            "length": L,
            "width": W,
            "height": float(max(height, 20.0)),
            "base_point": (-L / 2.0, -10.0, z_offset),
            "color": color,
            "operations": [],
        }

    def _create_cuerpo_general_extrusion(self, length: float, color: int) -> list:
        L = float(max(length, 10.0))
        half_L = L / 2.0
        W_outer = 40.0
        H_total = 346.5

        y_plane = -20.0
        base_width = 120.0
        chamfer_h = 70.0

        base_w = min(base_width, L * 0.8) if L < base_width else base_width
        offset_x = (L - base_w) / 2.0

        x0 = -half_L
        x1 = half_L
        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(x0 + offset_x, y_plane, 0)
        polygon += AllplanGeo.Point3D(x1 - offset_x, y_plane, 0)
        polygon += AllplanGeo.Point3D(x1, y_plane, chamfer_h)
        polygon += AllplanGeo.Point3D(x1, y_plane, H_total)
        polygon += AllplanGeo.Point3D(x0, y_plane, H_total)
        polygon += AllplanGeo.Point3D(x0, y_plane, chamfer_h)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, W_outer, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return []

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return []

        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        model_elem = AllplanBasisElements.ModelElement3D(prop, brep)
        return [model_elem]

    def create_geometry_3d(
        self,
        length: float = 200.0,
        width: float = 45.0,
        height: float = 130.0,
        hole_diameter: float = 20.0,
        color: int = 1,
    ) -> ModelEleList:

        final_model_list = ModelEleList()
        bases = []

        L = float(max(length, 10.0))
        half_L = L / 2.0

        offset_z = 101.5

        # 1. CUERPO 1 — centrado en X=0
        bases.append(self._cuerpo_1(L, width, height, offset_z, color))

        # 2. CUERPO 2 — centrado en X=0
        bases.append({
            "type": "cubo",
            "length": L,
            "width": 16.0,
            "height": float(max(height, 10.0)),
            "base_point": (-half_L, 19.5, offset_z),
            "color": 28,
            "operations": [],
        })

        # 3. CILINDROS — un cilindro por esquina, sin duplicados
        r_base = float(max(hole_diameter / 2.0, 1.0))
        radio_real = r_base * 2.0
        L_cilindro = 40.0
        y_dir = AllplanGeo.Vector3D(0, 1, 0)

        esquinas_molinete = [
            (-half_L,              height - radio_real),
            (half_L - radio_real,  height),
            (half_L,               radio_real),
            (-half_L + radio_real, 0),
        ]

        for x, z in esquinas_molinete:
            bases.append({
                "type": "cylinder",
                "radius": radio_real * 2.0,
                "height": L_cilindro,
                "base_point": (float(x), -20.0, float(z) + offset_z),
                "direction": y_dir,
                "color": 5,
                "operations": [],
            })

        # --- ENSAMBLAJE FINAL ---
        desc = {"bases": bases}
        inner_elements = self.geo_tools.build_from_description(desc)
        for ele in inner_elements:
            final_model_list.append(ele)

        outer_elements = self._create_cuerpo_general_extrusion(length, color=5)
        for ele in outer_elements:
            final_model_list.append(ele)

        return final_model_list
