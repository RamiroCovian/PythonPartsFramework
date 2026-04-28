# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList


class LlumExtXPS1203D:
    """
    Llum Exterior XPS 120 – TD Electricitat.

    Convención de ejes:
      - Ancho : X (centrado en X=0)
      - Prof.  : Y
      - Altura : Z (desde Z=0)

    Composición (WIP):
      - Base:   150(X) × 63(Y)  × 20(Z)  color 84   y: [-31.5, +31.5]
      - Cuerpo: 150(X) × 92(Y)  × 20(Z)  color 32   y: [-31.5, +60.5]  (desde neg. → +Y)
      - Top:    150(X) × 120(Y) × 40(Z)  color 30   y: [-31.5, +88.5]  (desde neg. → +Y)
      + Pieza unida (unión booleana)                  color 1
    """

    BASE_WIDTH  = 150.0
    BASE_DEPTH  =  63.0
    BASE_HEIGHT =  20.0

    BODY_DEPTH  =  92.0
    BODY_HEIGHT =  20.0

    TOP_DEPTH   = 120.0
    TOP_HEIGHT  =  40.0

    PILLAR_DEPTH  =  30.0
    PILLAR_HEIGHT = 760.0

    FRONT_DEPTH  =  20.0   # Y (hacia -Y desde el frente del assembly)
    FRONT_HEIGHT =  80.0   # Z

    # ---------------------------------------------------------------------------
    # BRep helpers
    # ---------------------------------------------------------------------------

    def _build_brep(self, half_w, y_plane, z_start, z_end, direction):
        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(-half_w, y_plane, z_start)
        polygon += AllplanGeo.Point3D( half_w, y_plane, z_start)
        polygon += AllplanGeo.Point3D( half_w, y_plane, z_end)
        polygon += AllplanGeo.Point3D(-half_w, y_plane, z_end)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded = AllplanGeo.ExtrudedAreaSolid3D()
        extruded.SetDirection(direction)
        extruded.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(extruded)
        if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
            return None

        err, brep = AllplanGeo.CreateBRep3D(polyhedron)
        if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
            return None

        return brep

    def _make_element(self, brep, color):
        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        return AllplanBasisElements.ModelElement3D(prop, brep)

    # ---------------------------------------------------------------------------
    # Piezas individuales
    # ---------------------------------------------------------------------------

    def _create_base(self, color: int) -> list:
        half_w = self.BASE_WIDTH / 2.0
        half_d = self.BASE_DEPTH / 2.0   # 31.5mm
        brep = self._build_brep(
            half_w, -half_d, 0, self.BASE_HEIGHT,
            AllplanGeo.Vector3D(0, self.BASE_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_body(self, color: int) -> list:
        """
        Parte del punto más negativo de la base (y=-31.5mm) hacia +Y.
        Z: de 20mm a 40mm.
        """
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0   # -31.5mm
        z_start = self.BASE_HEIGHT          # 20mm
        z_end   = z_start + self.BODY_HEIGHT  # 40mm
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, self.BODY_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_top(self, color: int) -> list:
        """
        Parte del punto más negativo de la base (y=-31.5mm) hacia +Y.
        Z: de 40mm a 80mm.
        """
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0   # -31.5mm
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT   # 40mm
        z_end   = z_start + self.TOP_HEIGHT              # 80mm
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, self.TOP_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_pillar(self, color: int) -> list:
        """
        Cubo 150(X) × 30(Y) × 760(Z), color 179.
        Parte del punto más positivo del top (y=+88.5mm) hacia -Y.
        Z: de 80mm a 840mm.
        """
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0 + self.TOP_DEPTH   # +88.5mm
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT + self.TOP_HEIGHT  # 80mm
        z_end   = z_start + self.PILLAR_HEIGHT               # 840mm
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, -self.PILLAR_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    # ---------------------------------------------------------------------------

    def _create_front(self, color: int) -> list:
        """
        Cubo 150(X) × 20(Y) × 80(Z) al frente del assembly.
        Parte del punto más negativo en Y (y=-31.5mm) hacia -Y.
        Z: de 0mm a 80mm (arranca con la base).
        """
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0   # -31.5mm
        brep = self._build_brep(
            half_w, y_start, 0, self.FRONT_HEIGHT,
            AllplanGeo.Vector3D(0, -self.FRONT_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_base(color=84):
            result.append(ele)
        for ele in self._create_body(color=32):
            result.append(ele)
        for ele in self._create_top(color=30):
            result.append(ele)
        for ele in self._create_pillar(color=179):
            result.append(ele)
        for ele in self._create_front(color=27):
            result.append(ele)
        return result
