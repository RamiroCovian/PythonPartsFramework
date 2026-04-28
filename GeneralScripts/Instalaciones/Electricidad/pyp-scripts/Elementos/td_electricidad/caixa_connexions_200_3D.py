# # -*- coding: utf-8 -*-
# import NemAll_Python_Geometry as AllplanGeo
# import NemAll_Python_AllplanSettings as AllplanSettings
# import NemAll_Python_BasisElements as AllplanBasisElements
# from TypeCollections.ModelEleList import ModelEleList

# from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


# def _create_cuerpo_general_extrusion(
#     length: float,
#     width: float,
#     height: float,
#     color: int = 1,
# ) -> ModelEleList:
#     """
#     Crea el cuerpo general simétrico (achique de ambos lados).
#     """
#     L = max(length, 200.0)  # Ancho total (ej. 200)
#     H = max(height, 350.0)  # Altura total (ej. 130)
#     W = max(width, 40.0)   # Profundidad de extrusión (ej. 45)

#     y_plane = -W / 2.0

#     # Medidas del achique (las dejamos fijas por ahora, como pediste)
#     base_width = 120.0
#     chamfer_h = 70.0 # Ajusté este valor a 50 para que en una altura de 130 se vea proporcionado

#     # Calculamos cuánto se mete hacia adentro de CADA lado para mantener la simetría
#     offset_x = (L - base_width) / 2.0

#     # Dibujamos el polígono simétrico de 6 lados
#     polygon = AllplanGeo.Polygon3D()
#     polygon += AllplanGeo.Point3D(offset_x, y_plane, 0)          # 1. Base inferior izquierda
#     polygon += AllplanGeo.Point3D(L - offset_x, y_plane, 0)      # 2. Base inferior derecha
#     polygon += AllplanGeo.Point3D(L, y_plane, chamfer_h)         # 3. Quiebre de la derecha
#     polygon += AllplanGeo.Point3D(L, y_plane, H)                 # 4. Esquina superior derecha
#     polygon += AllplanGeo.Point3D(0, y_plane, H)                 # 5. Esquina superior izquierda
#     polygon += AllplanGeo.Point3D(0, y_plane, chamfer_h)         # 6. Quiebre de la izquierda
#     polygon += polygon.Points[0]                                 # 7. Cierre automático

#     area = AllplanGeo.PolygonalArea3D()
#     area += polygon

#     # Extrusión
#     extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
#     extruded_solid.SetDirection(AllplanGeo.Vector3D(0, W, 0))
#     extruded_solid.SetRefPoint(polygon.Points[0])
#     extruded_solid.SetExtrudedArea(area)

#     err, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
#     if err != AllplanGeo.eGeometryErrorCode.eOK or polyhedron is None:
#         return ModelEleList()

#     err, brep = AllplanGeo.CreateBRep3D(polyhedron)
#     if err != AllplanGeo.eGeometryErrorCode.eOK or brep is None:
#         return ModelEleList()

#     prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
#     prop.Color = color
#     model_elem = AllplanBasisElements.ModelElement3D(prop, brep)
#     result = ModelEleList()
#     result.append(model_elem)
#     return result


# class CaixaConnexions200Object3D:
#     """
#     Caixa connexions 200 – Caja de conexiones eléctrica.

#     Convención de ejes:
#       - Largo : X
#       - Ancho : Y (centrado)
#       - Altura: Z
#     """

#     def __init__(self) -> None:
#         self.geo_tools = CreateSmartGeo()

#     def _cuerpo_1(self, length: float, width: float, height: float, color: int) -> dict:
#         """
#         Cuerpo 1: prisma rectangular base.
#         """
#         W = float(max(width, 10.0))
#         return {
#             "type": "cubo",
#             "length": float(max(length, 10.0)),
#             "width": W,
#             "height": float(max(height, 20.0)),
#             "base_point": (0, -W / 2.0, 0),
#             "color": color,
#             "operations": [],
#         }

#     def _cuerpo_2(
#         self,
#         length: float = 200.0,
#         width: float = 16.0,
#         height: float = 130.0,
#         color: int = 1,
#     ) -> ModelEleList:
#         """
#         Cuerpo 2: prisma rectangular 200 x 40 x 130 mm.
#         length (X) x width (Y) x height (Z). Centrado en Y.
#         """
#         W = float(max(width, 10.0))
#         desc = {
#             "bases": [
#                 {
#                     "type": "cubo",
#                     "length": float(max(length, 16.0)),
#                     "width": W,
#                     "height": float(max(height, 20.0)),
#                     "base_point": (0, -W / 2.0, 0),
#                     "color": color,
#                     "operations": [],
#                 },
#             ],
#         }
#         return self.geo_tools.build_from_description(desc)

#     def _cilindro_1(
#         self,
#         radius: float = 20.0,
#         axial_length: float = 40.0,
#         color: int = 1,
#     ) -> ModelEleList:
#         """
#         Cilindro 1: radio 20 mm, longitud axial 40 mm.
#         Orientado en eje Y (horizontal), centrado en Y.
#         CreateSmartGeo divide radius por 2 internamente, por eso pasamos diámetro.
#         """
#         r = float(max(radius, 1.0))
#         L = float(max(axial_length, 1.0))
#         y_dir = AllplanGeo.Vector3D(0, 1, 0)
#         desc = {
#             "bases": [
#                 {
#                     "type": "cylinder",
#                     "radius": r * 2.0,
#                     "height": L,
#                     "base_point": (0, -L / 2.0, 0),
#                     "direction": y_dir,
#                     "color": color,
#                     "operations": [],
#                 },
#             ],
#         }
#         return self.geo_tools.build_from_description(desc)

#     def create_geometry_3d(
#         self,
#         length: float = 200.0,
#         width: float = 45.0,
#         height: float = 130.0,
#         hole_diameter: float = 20.0,
#         color: int = 1,
#     ) -> ModelEleList:
#         # Por ahora solo Cuerpo 2 (para verificar antes de unir)
#         return self._cuerpo_2(length, width, height, color)



#

# -*- coding: utf-8 -*-
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class CaixaConnexions200Object3D:
    """
    Caixa connexions 200 – Caja de conexiones eléctrica completa.
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
        # Usamos la misma longitud paramétrica para que alinee perfecto con el interior
        L = float(max(length, 10.0))
        half_L = L / 2.0
        W_outer = 40.0
        H_total = 346.5

        y_plane = -20.0
        base_width = 120.0
        chamfer_h = 70.0

        # Lógica para evitar errores si la caja se hace muy angosta
        base_w = min(base_width, L * 0.8) if L < base_width else base_width
        offset_x = (L - base_w) / 2.0

        # Polígono centrado en X=0 (de -half_L a +half_L)
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
        # ¡ELIMINADA LA LÍNEA SetRefPoint AQUÍ!
        # Ahora Allplan respetará el X=0 y X=L del polígono sin desplazarlo.
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

        # Altura correcta y confirmada
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

        # 3. CILINDROS — posiciones relativas al centro (X=0)
        r_base = float(max(hole_diameter / 2.0, 1.0))
        radio_real = r_base * 2.0
        L_cilindro = 40.0
        y_dir = AllplanGeo.Vector3D(0, 1, 0)

        # Esquinas del molinete expresadas relativas a X=0
        esquinas_molinete = [
            (-half_L,            height - radio_real),
            (half_L - radio_real, height),
            (half_L,             radio_real),
            (-half_L + radio_real, 0),
        ]

        for x, z in esquinas_molinete:
            for _ in range(2):
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

        # Le pongo color 6 (magenta) temporalmente para que lo diferencies en Allplan
        outer_elements = self._create_cuerpo_general_extrusion(length, color=5)
        for ele in outer_elements:
            final_model_list.append(ele)

        return final_model_list
