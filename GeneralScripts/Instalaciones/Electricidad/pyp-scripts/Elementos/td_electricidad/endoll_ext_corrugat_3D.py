# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList


class EndollExtCorrugat3D:
    """
    Endoll Exterior amb Corrugat – TD Electricitat.

    Convención de ejes:
      - Ancho : X (150mm, centrado en X=0)
      - Prof.  : Y (150mm, centrado en Y=0)
      - Altura : Z (80mm)

    Composición:
      - Cuerpo: 150mm(X) × 80mm(Y) × 150mm(Z)          color 100
      - Tapa:   200mm(Y) × 200mm(Z) × 15mm(X),          color 5
                pegada a la cara derecha (x=+75mm),
                centrada en Y y Z (sobresale 25mm cada lado)
    """

    WIDTH      = 80.0   # X
    DEPTH      = 150.0   # Y
    HEIGHT     = 150.0    # Z

    TAPA_SIZE  = 200.0   # Y y Z
    TAPA_DEPTH = 15.0    # X (protrusión a la derecha)

    def _create_cuerpo(self, color: int) -> list:
        half_w = self.WIDTH / 2.0   # 75mm
        half_d = self.DEPTH / 2.0   # 40mm

        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(-half_w, -half_d, 0)
        polygon += AllplanGeo.Point3D( half_w, -half_d, 0)
        polygon += AllplanGeo.Point3D( half_w, -half_d, self.HEIGHT)
        polygon += AllplanGeo.Point3D(-half_w, -half_d, self.HEIGHT)
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
        return [elem, elem]

    def _create_tapa(self, color: int) -> list:
        """
        Cubo 200mm(Y) × 200mm(Z) × 15mm(X) pegado a la cara derecha (x=+half_w).
        Centrado respecto al cuerpo en Y y en Z (z=0 a z=150 → centro z=75).
        """
        x_start  = self.WIDTH / 2.0                     # +75mm (cara derecha del cuerpo)
        half_t   = self.TAPA_SIZE / 2.0                  # 100mm
        half_d   = self.DEPTH / 2.0                      # 40mm
        z_center = self.HEIGHT / 2.0                     # 75mm

        # Sobresal 25mm en cada lado respecto al cuerpo (200 vs 150 en Z, 200 vs 80 en Y)
        y_min = -half_t                                  # -100mm
        y_max =  half_t                                  # +100mm
        z_min = z_center - half_t                        # -25mm
        z_max = z_center + half_t                        # +175mm

        # Polígono en el plano YZ (x=x_start), extruido en +X
        polygon = AllplanGeo.Polygon3D()
        polygon += AllplanGeo.Point3D(x_start, y_min, z_min)
        polygon += AllplanGeo.Point3D(x_start, y_max, z_min)
        polygon += AllplanGeo.Point3D(x_start, y_max, z_max)
        polygon += AllplanGeo.Point3D(x_start, y_min, z_max)
        polygon += polygon.Points[0]

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(self.TAPA_DEPTH, 0, 0))
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

    def create_geometry_3d(self, color: int = 1) -> ModelEleList:
        result = ModelEleList()
        for ele in self._create_cuerpo(color=100):
            result.append(ele)
        for ele in self._create_tapa(color=28):
            result.append(ele)
        return result
