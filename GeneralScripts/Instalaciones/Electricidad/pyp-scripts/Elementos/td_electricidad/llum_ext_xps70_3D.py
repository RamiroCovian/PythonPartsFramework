# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList


class LlumExtXPS703D:
    """
    Llum Exterior XPS 70 – TD Electricitat.

    Convención de ejes:
      - Ancho : X (centrado en X=0)
      - Prof.  : Y
      - Altura : Z (desde Z=0)

    Composición:
      - Base:   150(X) × 13(Y)  × 20(Z)  color 107  y: [-6.5, +6.5]
      - Cuerpo: 150(X) × 42(Y)  × 20(Z)  color 21   y: [+6.5, -35.5]
      - Top:    150(X) × 70(Y)  × 40(Z)  color 30   y: [+6.5, -63.5]
      - Pilar:  150(X) × 30(Y)  × 760(Z) color 33   y: [-63.5, -33.5]
      + Pieza unida (unión booleana de las 4)         color 1
    """

    BASE_WIDTH  = 150.0
    BASE_DEPTH  =  13.0
    BASE_HEIGHT =  20.0

    BODY_DEPTH  =  42.0
    BODY_HEIGHT =  20.0

    TOP_DEPTH   =  70.0
    TOP_HEIGHT  =  40.0

    PILLAR_DEPTH  =  30.0
    PILLAR_HEIGHT = 760.0

    # ---------------------------------------------------------------------------
    # BRep helpers
    # ---------------------------------------------------------------------------

    def _build_brep(self, half_w, y_plane, z_start, z_end, direction):
        """Construye un BRep3D de caja rectangular. Devuelve el BRep o None."""
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
        half_d = self.BASE_DEPTH / 2.0
        brep = self._build_brep(
            half_w, -half_d, 0, self.BASE_HEIGHT,
            AllplanGeo.Vector3D(0, self.BASE_DEPTH, 0)
        )
        if brep is None:
            return []
        elem = self._make_element(brep, color)
        return [elem]

    def _create_body(self, color: int) -> list:
        half_w = self.BASE_WIDTH / 2.0
        y_back = self.BASE_DEPTH / 2.0
        z_start = self.BASE_HEIGHT
        z_end   = z_start + self.BODY_HEIGHT
        brep = self._build_brep(
            half_w, y_back, z_start, z_end,
            AllplanGeo.Vector3D(0, -self.BODY_DEPTH, 0)
        )
        if brep is None:
            return []
        elem = self._make_element(brep, color)
        return [elem]

    def _create_top(self, color: int) -> list:
        half_w  = self.BASE_WIDTH / 2.0
        y_back  = self.BASE_DEPTH / 2.0
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT
        z_end   = z_start + self.TOP_HEIGHT
        brep = self._build_brep(
            half_w, y_back, z_start, z_end,
            AllplanGeo.Vector3D(0, -self.TOP_DEPTH, 0)
        )
        if brep is None:
            return []
        elem = self._make_element(brep, color)
        return [elem]

    def _create_pillar(self, color: int) -> list:
        half_w  = self.BASE_WIDTH / 2.0
        y_start = self.BASE_DEPTH / 2.0 - self.TOP_DEPTH
        z_start = self.BASE_HEIGHT + self.BODY_HEIGHT + self.TOP_HEIGHT
        z_end   = z_start + self.PILLAR_HEIGHT
        brep = self._build_brep(
            half_w, y_start, z_start, z_end,
            AllplanGeo.Vector3D(0, self.PILLAR_DEPTH, 0)
        )
        if brep is None:
            return []
        elem = self._make_element(brep, color)
        return [elem]

    # ---------------------------------------------------------------------------
    # Pieza unida (unión booleana de todas las piezas)
    # ---------------------------------------------------------------------------

    def _create_unified(self, color: int) -> list:
        half_w  = self.BASE_WIDTH / 2.0
        half_d  = self.BASE_DEPTH / 2.0
        y_back  = half_d
        z1 = self.BASE_HEIGHT
        z2 = z1 + self.BODY_HEIGHT
        z3 = z2 + self.TOP_HEIGHT
        z4 = z3 + self.PILLAR_HEIGHT

        breps = [
            self._build_brep(half_w, -half_d,            0,  z1, AllplanGeo.Vector3D(0,  self.BASE_DEPTH,   0)),
            self._build_brep(half_w,  y_back,            z1, z2, AllplanGeo.Vector3D(0, -self.BODY_DEPTH,   0)),
            self._build_brep(half_w,  y_back,            z2, z3, AllplanGeo.Vector3D(0, -self.TOP_DEPTH,    0)),
            self._build_brep(half_w,  y_back - self.TOP_DEPTH, z3, z4, AllplanGeo.Vector3D(0,  self.PILLAR_DEPTH, 0)),
        ]
        breps = [b for b in breps if b is not None]
        if not breps:
            return []

        union_brep = breps[0]
        for brep in breps[1:]:
            err, union_brep = AllplanGeo.MakeUnion(union_brep, brep)
            if err != AllplanGeo.eGeometryErrorCode.eOK or union_brep is None:
                return []

        elem = self._make_element(union_brep, color)
        return [elem]

    # ---------------------------------------------------------------------------

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_base(color=107):
            result.append(ele)
        for ele in self._create_body(color=21):
            result.append(ele)
        for ele in self._create_top(color=30):
            result.append(ele)
        for ele in self._create_pillar(color=33):
            result.append(ele)
        for ele in self._create_unified(color=1):
            result.append(ele)
        return result
