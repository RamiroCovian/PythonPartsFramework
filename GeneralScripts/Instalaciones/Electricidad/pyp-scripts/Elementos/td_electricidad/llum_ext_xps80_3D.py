# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList


class LlumExtXPS803D:
    """
    Llum Exterior XPS 80 – TD Electricitat.

    Convención de ejes:
      - Ancho : X (centrado en X=0)
      - Prof.  : Y
      - Altura : Z (desde Z=0)

    Composición:
      - Base:   150(X) × 23(Y)  × 20(Z)  color 125  y: [-11.5, +11.5]
      - Cuerpo: 150(X) × 52(Y)  × 20(Z)  color 61   y: [-11.5, +40.5]
      - Top:    150(X) × 80(Y)  × 40(Z)  color 30   y: [-11.5, +68.5]
      - Pilar:  150(X) × 30(Y)  × 760(Z) color 33   y: [+68.5, +38.5]
    """

    BASE_WIDTH  = 150.0
    BASE_DEPTH  =  23.0
    BASE_HEIGHT =  20.0

    BODY_DEPTH  =  52.0
    BODY_HEIGHT =  20.0

    TOP_DEPTH   =  80.0
    TOP_HEIGHT  =  40.0

    PILLAR_DEPTH  =  30.0
    PILLAR_HEIGHT = 760.0

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
    # Piezas
    # ---------------------------------------------------------------------------

    def _create_base(self, color: int) -> list:
        half_w = self.BASE_WIDTH / 2.0
        half_d = self.BASE_DEPTH / 2.0   # 11.5mm
        brep = self._build_brep(
            half_w, -half_d, 0, self.BASE_HEIGHT,
            AllplanGeo.Vector3D(0, self.BASE_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_body(self, color: int) -> list:
        """Desde y=-11.5mm hacia +Y 52mm. Z: 20 a 40mm."""
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0   # -11.5mm
        z_start = self.BASE_HEIGHT
        z_end   = z_start + self.BODY_HEIGHT
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, self.BODY_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_top(self, color: int) -> list:
        """Desde y=-11.5mm hacia +Y 80mm. Z: 40 a 80mm."""
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0   # -11.5mm
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT
        z_end   = z_start + self.TOP_HEIGHT
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, self.TOP_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    def _create_pillar(self, color: int) -> list:
        """Desde y más positivo del top (y=+68.5mm) hacia -Y 30mm. Z: 80 a 840mm."""
        half_w  = self.BASE_WIDTH / 2.0
        y_start = -self.BASE_DEPTH / 2.0 + self.TOP_DEPTH   # +68.5mm
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT + self.TOP_HEIGHT
        z_end   = z_start + self.PILLAR_HEIGHT
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, -self.PILLAR_DEPTH, 0)
        )
        if brep is None:
            return []
        return [self._make_element(brep, color)]

    # ---------------------------------------------------------------------------

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_base(color=125):
            result.append(ele)
        for ele in self._create_body(color=61):
            result.append(ele)
        for ele in self._create_top(color=30):
            result.append(ele)
        for ele in self._create_pillar(color=33):
            result.append(ele)
        return result
