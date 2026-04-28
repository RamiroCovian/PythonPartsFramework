# -*- coding: utf-8 -*-
import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class CaixetiDobleVertical3D:
    """
    Caixeti Doble Vertical – TD Electricitat.

    Convención de ejes:
      - Ancho : X (90mm base, centrado en X=0)
      - Prof.  : Y (41.14mm, centrado en Y=0)
      - Altura : Z (220mm total)

    Polígono XZ (simétrico):
      - Base recta: 90mm × 120mm (z=0 a z=120)
      - Chamfer arranca en z=120mm
      - Tope: 60mm × 41.14mm (z=220)
    """

    WIDTH     = 90.0
    TOP_WIDTH = 60.0
    DEPTH     = 41.14
    HEIGHT    = 220.0
    CHAMFER_Z = 120.0

    # Elementos color 28 (cara trasera)
    CYL_BACK_RADIUS  = 34.0   # radio
    CYL_BACK_LENGTH  = 16.0   # profundidad (Y)
    CYL_BACK_Z_BOT   = 0.0    # z_center cilindro inferior (mitad bajo el eje z=0)
    CYL_BACK_Z_TOP   = 70.0   # z_center cilindro superior (mitad sobre el tope del rectángulo)

    BOX_WIDTH  = 68.0   # X
    BOX_HEIGHT = 70.0   # Z (z=0 a z=70, superpuesto con cilindro inferior)
    BOX_DEPTH  = 16.0   # Y (protrude)
    BOX_Z      = 0.0    # z inicio del rectángulo (arranca en el eje)

    # Cilindros pequeños color 28 — 4 individuales en esquinas del rectángulo trasero
    SMALL_CYL_DIAMETER = 10.0   # diámetro (CreateSmartGeo recibe diámetro)

    # Elemento color 1 — estadio vertical extruido 50mm
    INT_EXT_DEPTH    = 50.0
    INT_EXT_OVERHANG = 15.0
    ARC_SEGMENTS     = 16

    # Elemento color 5 — estadio vertical flush (profundidad total del cuerpo)
    INT_RADIUS = 35.0   # radio → ancho total = 2 × 35 = 70mm

    def __init__(self) -> None:
        self.geo_tools = CreateSmartGeo()

    def _create_cuerpo(self, color: int) -> list:
        half_w   = self.WIDTH / 2.0      # 45mm
        half_d   = self.DEPTH / 2.0      # 20.57mm
        top_half = self.TOP_WIDTH / 2.0  # 30mm
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

    def _create_elementos_traseros(self, color: int) -> ModelEleList:
        """
        Elementos color 28 en la cara delantera (y=-half_d), protruyen 16mm hacia afuera (Y negativo).

        Composición (de abajo a arriba en Z):
          - Cilindro inferior: r=34mm, z_center=0mm
          - Rectángulo: 68mm(X) × 70mm(Z) × 16mm(Y), z=0 a z=70
          - Cilindro superior: r=34mm, z_center=70mm
        """
        half_d  = self.DEPTH / 2.0   # 20.57mm
        y_start = -half_d            # cara delantera
        y_dir   = AllplanGeo.Vector3D(0, -1, 0)

        # --- Cilindros traseros (via geo_tools) ---
        bases = [
            {
                "type": "cylinder",
                "radius": self.CYL_BACK_RADIUS * 2.0,
                "height": self.CYL_BACK_LENGTH,
                "base_point": (0.0, y_start, self.CYL_BACK_Z_BOT),
                "direction": y_dir,
                "color": color,
                "operations": [],
            },
            {
                "type": "cylinder",
                "radius": self.CYL_BACK_RADIUS * 2.0,
                "height": self.CYL_BACK_LENGTH,
                "base_point": (0.0, y_start, self.CYL_BACK_Z_TOP),
                "direction": y_dir,
                "color": color,
                "operations": [],
            },
        ]
        result = self.geo_tools.build_from_description({"bases": bases})

        # --- Rectángulo trasero ---
        half_x  = self.BOX_WIDTH / 2.0   # 34mm
        z_bot   = self.BOX_Z             # 68mm
        z_top   = self.BOX_Z + self.BOX_HEIGHT  # 138mm

        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(-half_x, y_start, z_bot)
        polygon += AllplanGeo.Point3D( half_x, y_start, z_bot)
        polygon += AllplanGeo.Point3D( half_x, y_start, z_top)
        polygon += AllplanGeo.Point3D(-half_x, y_start, z_top)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, -self.BOX_DEPTH, 0))
        extruded_solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
        if err == AllplanGeo.eGeometryErrorCode.eOK and polyhedron is not None:
            err, brep = AllplanGeo.CreateBRep3D(polyhedron)
            if err == AllplanGeo.eGeometryErrorCode.eOK and brep is not None:
                prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                prop.Color = color
                result.append(AllplanBasisElements.ModelElement3D(prop, brep))

        return result

    def _create_small_cylinders(self, color: int) -> ModelEleList:
        """
        4 cilindros de 10mm radio, profundidad total del cuerpo (DEPTH).

        Posiciones (XZ):
          - Par exterior: x=±(half_w - 10) = ±35mm, z=CYL_BACK_Z_TOP (70mm)
          - Par interior: x=±(half_w - 10) = ±35mm, z=CYL_BACK_Z_BOT (0mm)

        Tangentes al lateral interno del cuerpo (half_w=45, radio=10 → centro x=±35).
        En Y: flush con el cuerpo, arrancan en y=-half_d, altura=DEPTH.
        """
        half_d  = self.DEPTH / 2.0
        y_dir   = AllplanGeo.Vector3D(0, 1, 0)
        cyl_r   = self.SMALL_CYL_DIAMETER   # 10mm → CreateSmartGeo lo usa como radio real
        cyl_x   = self.WIDTH / 2.0 - cyl_r  # 45 - 10 = 35mm

        positions = [
            ( cyl_x, -half_d, self.CYL_BACK_Z_TOP),
            (-cyl_x, -half_d, self.CYL_BACK_Z_TOP),
            ( cyl_x, -half_d, self.CYL_BACK_Z_BOT),
            (-cyl_x, -half_d, self.CYL_BACK_Z_BOT),
        ]

        bases = [
            {
                "type": "cylinder",
                "radius": cyl_r * 2.0,
                "height": self.DEPTH,
                "base_point": pos,
                "direction": y_dir,
                "color": color,
                "operations": [],
            }
            for pos in positions
        ]
        return self.geo_tools.build_from_description({"bases": bases})

    def _create_interior(self, color: int) -> list:
        """
        Estadio vertical flush (color 5) — ocupa la profundidad total del cuerpo (41.14mm).

        Forma en XZ idéntica al interior_ext pero con radio=35mm (ancho=70mm).
        Parte de la cara frontal (y=-half_d) y se extrude 41.14mm en Y.
        """
        r       = self.INT_RADIUS       # 35mm
        half_d  = self.DEPTH / 2.0      # 20.57mm
        y_plane = -half_d               # cara frontal
        z_bot   = self.CYL_BACK_Z_BOT  # 0.0
        z_top   = self.CYL_BACK_Z_TOP  # 70.0
        n       = self.ARC_SEGMENTS

        points = []

        # Semicírculo inferior: centro (0, z_bot), ángulo 0 → -π
        for i in range(n + 1):
            angle = -math.pi * i / n
            points.append((r * math.cos(angle), z_bot + r * math.sin(angle)))

        # Semicírculo superior: centro (0, z_top), ángulo π → 0
        for i in range(n + 1):
            angle = math.pi - math.pi * i / n
            points.append((r * math.cos(angle), z_top + r * math.sin(angle)))

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
        elem = AllplanBasisElements.ModelElement3D(prop, brep)
        return [elem, elem]  # duplicado × 2

    def _create_interior_ext(self, color: int) -> list:
        """
        Estadio vertical extruido 50mm (color 1).

        Forma en XZ:
          - Semicírculo inferior: centro (0, z_bot=0), radio=34mm → de ángulo 0 a -π
          - Recto izquierdo: (-34, 0) → (-34, 70)
          - Semicírculo superior: centro (0, z_top=70), radio=34mm → de ángulo π a 0
          - Recto derecho: (34, 70) → (34, 0) [cierre]

        Extruido 50mm en Y, sobresale 15mm de la cara delantera (y=-half_d).
        y_plane = -(half_d + overhang) = -(20.57 + 15) = -35.57mm
        """
        r        = self.CYL_BACK_RADIUS        # 34mm
        half_d   = self.DEPTH / 2.0            # 20.57mm
        y_plane  = -(half_d + self.INT_EXT_OVERHANG)  # -35.57mm
        z_bot    = self.CYL_BACK_Z_BOT         # 0.0
        z_top    = self.CYL_BACK_Z_TOP         # 70.0
        n        = self.ARC_SEGMENTS

        points = []

        # Semicírculo inferior: centro (0, z_bot), ángulo 0 → -π
        for i in range(n + 1):
            angle = -math.pi * i / n
            points.append((r * math.cos(angle), z_bot + r * math.sin(angle)))

        # Semicírculo superior: centro (0, z_top), ángulo π → 0
        for i in range(n + 1):
            angle = math.pi - math.pi * i / n
            points.append((r * math.cos(angle), z_top + r * math.sin(angle)))

        polygon = AllplanGeo.Polygon3D()
        for (x, z) in points:
            polygon += AllplanGeo.Point3D(x, y_plane, z)
        polygon += AllplanGeo.Point3D(points[0][0], y_plane, points[0][1])

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0, self.INT_EXT_DEPTH, 0))
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

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_cuerpo(color=5):
            result.append(ele)
        for ele in self._create_interior(color=5):
            result.append(ele)
        for ele in self._create_elementos_traseros(color=28):
            result.append(ele)
        for ele in self._create_small_cylinders(color=5):
            result.append(ele)
        for ele in self._create_interior_ext(color=1):
            result.append(ele)
        return result
