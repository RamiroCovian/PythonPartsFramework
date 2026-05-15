# -*- coding: utf-8 -*-
"""Reductor conjunto 110↔40 (geometría con tramo intermedio tipo 50+40; un solo artículo 110-40).

- PythonPart: ``create_element(build_ele, doc)`` (D1/D2 o 110 y 40 por defecto).
- Dinámico: ``ReductConjuntosModel`` + ``set_diameters`` + ``build`` (solo par 110↔40).
"""

import math
from typing import List, Any, Optional, Tuple

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult

# Solo transición 110 mm ↔ 40 mm (el cuerpo intermedio 50+40 es geometría interna).
SUPPORTED_REDUCTION_PAIRS = frozenset({(110, 40), (40, 110)})


def check_allplan_version(_build_ele, _version) -> bool:
    """Se soportan todas las versiones."""
    return True


def _pair_from_build_ele(build_ele) -> Tuple[int, int]:
    """Intenta leer D1/D2 o Diametro1/Diametro2 del PythonPart; si no, 110 y 40."""

    def _read(name: str) -> Optional[int]:
        val = getattr(build_ele, name, None)
        if val is None:
            return None
        if hasattr(val, "value"):
            try:
                return int(round(float(val.value)))
            except Exception:
                return None
        try:
            return int(round(float(val)))
        except Exception:
            return None

    for a_name, b_name in (
        ("D1", "D2"),
        ("Diametro1", "Diametro2"),
        ("DIAMETRO1", "DIAMETRO2"),
    ):
        a, b = _read(a_name), _read(b_name)
        if a is not None and b is not None:
            return a, b
    return 110, 40


class ConjuntosReduccion:
    """Reductor 110↔40 (dos ModelElement3D, ambos etiquetados como conjunto 110-40)."""

    ROT_X_TIPO2: float = 180.0
    ROT_Y_TIPO2: float = 90.0
    ROT_Z_TIPO2: float = 90.0

    OFFSET_CUBOIDES_X: float = 20.0
    OFFSET_CUBOIDES_Y: float = 20.0
    OFFSET_CUBOIDES_Z: float = -23.0

    ROT_CUBOIDES_X: float = 90.0
    ROT_CUBOIDES_Y: float = 180.0
    ROT_CUBOIDES_Z: float = 0.0

    OFFSET_CUBOIDE_PEQUENO_X: float = 5.0
    OFFSET_CUBOIDE_PEQUENO_Y: float = 5.0
    OFFSET_CUBOIDE_PEQUENO_Z: float = 0.0

    # Matriz de traslación global (mm) tras todas las rotaciones: mueve ambos sólidos igual.
    TRANSLATION_X_MM: float = 48.66
    TRANSLATION_Y_MM: float = 68.1
    TRANSLATION_Z_MM: float = -80.0

    ADD_X: float = 50.0
    ADD_Y: float = 37.5
    ADD_Z: float = 60.0

    ANILLO_LARGO: float = 10.0
    SOBRESALE_ANILLO: float = 5.0
    LAYER = 40148

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc

    def create_result(self) -> CreateElementResult:
        return CreateElementResult(self._build_figura_reductora())

    def build_model_list(self) -> List[Any]:
        """Lista cruda de ModelElement3D (para cargador dinámico)."""
        return self._build_figura_reductora()

    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None):
        if layer is None:
            layer = self.LAYER
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = color
        p.ColorByLayer = False
        p.Pen = pen
        p.Stroke = stroke
        p.Layer = layer
        return p

    @staticmethod
    def _create_trapezoidal_prism(base1, base2, height, length):
        y0, y1 = 0.0, height
        x0 = (base2 - base1) / 2.0
        x1 = x0 + base1
        poly = AllplanGeo.Polygon3D([
            AllplanGeo.Point3D(x0, y0, 0.0),
            AllplanGeo.Point3D(x1, y0, 0.0),
            AllplanGeo.Point3D(base2, y1, 0.0),
            AllplanGeo.Point3D(0.0, y1, 0.0),
            AllplanGeo.Point3D(x0, y0, 0.0)
        ])
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, length)
        err, solid = AllplanGeo.CreatePolyhedron(poly, path)
        return solid if err == 0 and solid and solid.IsValid() else None

    @staticmethod
    def _make_union(*solids):
        if not solids:
            return None
        result = solids[0]
        for s in solids[1:]:
            err, result2 = AllplanGeo.MakeUnion(result, s)
            if err == 0 and result2 and result2.IsValid():
                result = result2
        return result

    @staticmethod
    def _translation_matrix(tx_mm: float, ty_mm: float, tz_mm: float) -> AllplanGeo.Matrix3D:
        """Solo traslación (mm), equivalente a T(tx,ty,tz)."""
        m = AllplanGeo.Matrix3D()
        m.SetTranslation(AllplanGeo.Vector3D(float(tx_mm), float(ty_mm), float(tz_mm)))
        return m

    @staticmethod
    def _apply_rotations(solid, cx, cy, cz, rx=0.0, ry=0.0, rz=0.0):
        for angle, axis in zip([rx, ry, rz], ['x', 'y', 'z']):
            if abs(angle) > 1e-6:
                mat = AllplanGeo.Matrix3D()
                if axis == 'x':
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                elif axis == 'y':
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                else:
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    def _add_user_attributes_reducer_rigid_110_40(self, attr_list):
        if not self.doc:
            return
        try:
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, "IS"))
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_007_002"))
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED. M-F 110-50Ø"))
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.1119))
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110-50"))
        except Exception as e:
            print(f"[Reduct_110_50_40_script] Advertencia atributos usuario reductor 110-40: {e}")

    def _attach_reductor_110_40_attributes(self, model_elem, include_user_attrs: bool = True):
        """Ficha 110-50; el segundo sólido solo custom (evita duplicar peso pmp en listados)."""
        red_attr_list = [
            AllplanBaseElements.AttributeString(1083, "RED. M-F 110-50Ø"),
            AllplanBaseElements.AttributeString(1084, "Ø110-50"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "110-50"),
            AllplanBaseElements.AttributeString(1897, ""),
            AllplanBaseElements.AttributeString(1898, ""),
            AllplanBaseElements.AttributeString(1899, ""),
            AllplanBaseElements.AttributeString(1900, ""),
            AllplanBaseElements.AttributeString(1901, ""),
            AllplanBaseElements.AttributeString(1902, ""),
            AllplanBaseElements.AttributeString(1903, ""),
            AllplanBaseElements.AttributeString(1904, ""),
        ]
        if include_user_attrs and self.doc:
            self._add_user_attributes_reducer_rigid_110_40(red_attr_list)
        red_attr_set = AllplanBaseElements.AttributeSet(red_attr_list)
        red_attributes = AllplanBaseElements.Attributes([red_attr_set])
        model_elem.SetAttributes(red_attributes)

    def _attach_adapter_50_40_attributes(self, model_elem):
        """Atributos propios del adaptador pequeño (50-40) según ficha."""
        attr_list = [
            AllplanBaseElements.AttributeString(1083, "RED. M-F 50-40Ø"),
            AllplanBaseElements.AttributeString(1084, "Ø40-50"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "40-50"),
            AllplanBaseElements.AttributeString(1897, ""),
            AllplanBaseElements.AttributeString(1898, ""),
            AllplanBaseElements.AttributeString(1899, ""),
            AllplanBaseElements.AttributeString(1900, ""),
            AllplanBaseElements.AttributeString(1901, ""),
            AllplanBaseElements.AttributeString(1902, ""),
            AllplanBaseElements.AttributeString(1903, ""),
            AllplanBaseElements.AttributeString(1904, ""),
        ]
        if self.doc:
            try:
                get_id = AllplanBaseElements.AttributeService.GetAttributeID
                id_6ccis = get_id(self.doc, "6_CC_IS")
                id_cart = get_id(self.doc, "pmp_CARTICULO")
                id_nom = get_id(self.doc, "pmp_nom")
                id_pes = get_id(self.doc, "pmp_pes_unitari")
                id_sec = get_id(self.doc, "pmp_seccio")
                if id_6ccis and id_6ccis > 0:
                    attr_list.append(AllplanBaseElements.AttributeString(id_6ccis, "IS"))
                if id_cart and id_cart > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(id_cart, "KN07_007_001")
                    )
                if id_nom and id_nom > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(id_nom, "RED. M-F 50-40Ø")
                    )
                if id_pes and id_pes > 0:
                    attr_list.append(AllplanBaseElements.AttributeDouble(id_pes, 0.0319))
                if id_sec and id_sec > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(id_sec, "Ø40-50mm")
                    )
            except Exception as ex:
                print(
                    "[Reduct_110_50_40_script] Advertencia atributos adaptador 50-40: "
                    f"{ex}"
                )
        attr_set = AllplanBaseElements.AttributeSet(attr_list)
        model_elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))

    def _build_figura_reductora(self) -> List[Any]:
        props = self._props(color=70)

        cara_inf = AllplanGeo.Polygon3D([
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(110.0, 0, 0),
            AllplanGeo.Point3D(110.0, 60.0, 0),
            AllplanGeo.Point3D(0, 60.0, 0),
            AllplanGeo.Point3D(0, 0, 0)
        ])
        path_cuboide = AllplanGeo.Polyline3D()
        path_cuboide += AllplanGeo.Point3D(0, 0, 0)
        path_cuboide += AllplanGeo.Point3D(0, 0, 110.0)
        err, cuboide = AllplanGeo.CreatePolyhedron(cara_inf, path_cuboide)
        if err != 0 or cuboide is None or not cuboide.IsValid():
            return []

        base_mayor, alto_trap, ANGULO_CARAS_DEG = 110.0, 50.0, 33.0
        base_menor = max(1.0, base_mayor - 2.0 * alto_trap * math.tan(math.radians(ANGULO_CARAS_DEG)))
        salida_sur, EPS_UNION = 60.0, 0.1
        ROT_X_DEG, ROT_Y_DEG, ROT_Z_DEG = 0.0, 90.0, 0.0
        OFFSET_X, OFFSET_Z = -25.0, 0.0

        trap = self._create_trapezoidal_prism(base1=base_menor, base2=base_mayor, height=alto_trap, length=salida_sur)
        if trap is None:
            return [AllplanBasisElements.ModelElement3D(props, cuboide)]

        dx = (110.0 - base_mayor) * 0.5
        dy = -alto_trap + EPS_UNION
        dz = (110.0 - salida_sur) * 0.5

        trap = AllplanGeo.Move(trap, AllplanGeo.Vector3D(dx + OFFSET_X, dy, dz + OFFSET_Z))
        cx = dx + OFFSET_X + base_mayor * 0.5
        cy = dy + alto_trap * 0.5
        cz = dz + OFFSET_Z + salida_sur * 0.5
        trap = self._apply_rotations(trap, cx, cy, cz, ROT_X_DEG, ROT_Y_DEG, ROT_Z_DEG)

        final_body = self._make_union(cuboide, trap)

        x_center = dx + OFFSET_X + base_mayor * 0.5
        z_center = dz + OFFSET_Z + salida_sur * 0.5
        y_top = dy

        add_min = AllplanGeo.Point3D(x_center - self.ADD_X * 0.5, y_top - self.ADD_Y, z_center - self.ADD_Z * 0.5)
        add_max = AllplanGeo.Point3D(x_center + self.ADD_X * 0.5, y_top,            z_center + self.ADD_Z * 0.5)
        cubo_trunc = AllplanGeo.Polyhedron3D.CreateCuboid(add_min, add_max)
        final_body = self._make_union(final_body, cubo_trunc)

        y_end_cubo = y_top - self.ADD_Y
        ring_min = AllplanGeo.Point3D(
            x_center - (self.ADD_X * 0.5 + self.SOBRESALE_ANILLO),
            y_end_cubo - self.ANILLO_LARGO,
            z_center - (self.ADD_Z * 0.5 + self.SOBRESALE_ANILLO)
        )
        ring_max = AllplanGeo.Point3D(
            x_center + (self.ADD_X * 0.5 + self.SOBRESALE_ANILLO),
            y_end_cubo,
            z_center + (self.ADD_Z * 0.5 + self.SOBRESALE_ANILLO)
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(ring_min, ring_max)
        final_body = self._make_union(final_body, anillo)

        cub1_largo, cub1_ancho, cub1_alto = 60.0, 50.0, 50.0
        cub2_largo, cub2_ancho, cub2_alto = 45.0, 40.0, 40.0

        y_base = y_end_cubo - self.ANILLO_LARGO - cub1_alto
        x_base = x_center - cub1_ancho * 0.5
        z_base = z_center - cub1_largo * 0.5

        x_base += self.OFFSET_CUBOIDES_X
        y_base += self.OFFSET_CUBOIDES_Y
        z_base += self.OFFSET_CUBOIDES_Z

        min1 = AllplanGeo.Point3D(x_base, y_base, z_base)
        max1 = AllplanGeo.Point3D(x_base + cub1_ancho, y_base + cub1_alto, z_base + cub1_largo)
        cuboide_50 = AllplanGeo.Polyhedron3D.CreateCuboid(min1, max1)

        min2_x = x_base + self.OFFSET_CUBOIDE_PEQUENO_X
        min2_y = y_base + self.OFFSET_CUBOIDE_PEQUENO_Y
        min2_z = z_base + cub1_largo + self.OFFSET_CUBOIDE_PEQUENO_Z
        min2 = AllplanGeo.Point3D(min2_x, min2_y, min2_z)
        max2 = AllplanGeo.Point3D(min2_x + cub2_ancho, min2_y + cub2_alto, min2_z + cub2_largo)
        cuboide_40 = AllplanGeo.Polyhedron3D.CreateCuboid(min2, max2)

        solido_cub = self._make_union(cuboide_50, cuboide_40)

        rot_x_deg, rot_y_deg, rot_z_deg = self.ROT_CUBOIDES_X, self.ROT_CUBOIDES_Y, self.ROT_CUBOIDES_Z
        cx2 = x_base + cub1_ancho * 0.5
        cy2 = y_base + cub1_alto * 0.5
        cz2 = z_base + (cub1_largo + cub2_largo) * 0.5
        solido_cub = self._apply_rotations(solido_cub, cx2, cy2, cz2, rot_x_deg, rot_y_deg, rot_z_deg)

        SIZE = 50.0
        ROT_X_TRI_DEG, ROT_Y_TRI_DEG, ROT_Z_TRI_DEG = 180.0, 0.0, 0.0
        OFFSET_TRI_X, OFFSET_TRI_Y, OFFSET_TRI_Z = -25.0, 17.0, 0.0

        p0t = AllplanGeo.Point3D(0.0, 0.0, 0.0)
        p1t = AllplanGeo.Point3D(SIZE, 0.0, 0.0)
        p2t = AllplanGeo.Point3D(0.0, SIZE, 0.0)
        base_face = AllplanGeo.Polygon3D([p0t, p1t, p2t, p0t])

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, SIZE)

        err_tri, prisma_tri = AllplanGeo.CreatePolyhedron(base_face, path)
        if err_tri == 0 and prisma_tri and prisma_tri.IsValid():
            cx3 = SIZE / 3.0
            cy3 = SIZE / 3.0
            cz3 = SIZE / 2.0
            prisma_tri = self._apply_rotations(prisma_tri, cx3, cy3, cz3, ROT_X_TRI_DEG, ROT_Y_TRI_DEG, ROT_Z_TRI_DEG)

            dx_tri = (110.0 - base_mayor) * 0.5
            x_right = dx_tri + OFFSET_X + base_mayor + OFFSET_TRI_X
            y_b = dy + OFFSET_TRI_Y
            z_b = z_center - SIZE * 0.5 + OFFSET_TRI_Z

            prisma_tri = AllplanGeo.Move(prisma_tri, AllplanGeo.Vector3D(x_right, y_b, z_b))
            final_body = self._make_union(final_body, prisma_tri)

        rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg = 180.0, 180.0, 0.0
        cx_obj = x_center
        cy_obj = y_top - self.ADD_Y * 0.5
        cz_obj = z_center

        obj = self._apply_rotations(final_body, cx_obj, cy_obj, cz_obj, rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg)

        obj = self._apply_rotations(
            obj,
            cx_obj, cy_obj, cz_obj,
            rx=self.ROT_X_TIPO2,
            ry=self.ROT_Y_TIPO2,
            rz=self.ROT_Z_TIPO2
        )

        obj_cuboides = self._apply_rotations(
            solido_cub,
            cx_obj, cy_obj, cz_obj,
            rot_obj_x_deg, rot_obj_y_deg, rot_obj_z_deg
        )
        obj_cuboides = self._apply_rotations(
            obj_cuboides,
            cx_obj, cy_obj, cz_obj,
            rx=self.ROT_X_TIPO2,
            ry=self.ROT_Y_TIPO2,
            rz=self.ROT_Z_TIPO2
        )

        mat_traslacion = self._translation_matrix(
            self.TRANSLATION_X_MM,
            self.TRANSLATION_Y_MM,
            self.TRANSLATION_Z_MM,
        )
        obj = AllplanGeo.Transform(obj, mat_traslacion)
        obj_cuboides = AllplanGeo.Transform(obj_cuboides, mat_traslacion)

        model_reductor = AllplanBasisElements.ModelElement3D(props, obj)
        model_cuboides = AllplanBasisElements.ModelElement3D(props, obj_cuboides)

        self._attach_reductor_110_40_attributes(model_reductor, include_user_attrs=True)
        self._attach_adapter_50_40_attributes(model_cuboides)

        return [model_reductor, model_cuboides]


def _pair_supported(d1: int, d2: int) -> bool:
    return tuple(sorted((d1, d2))) == (40, 110)


class ReductConjuntosModel:
    """API tipo manguito: ``set_diameters`` + ``build`` para geo_handler / PolyLib."""

    def __init__(self, build_ele, doc=None):
        self.build_ele = build_ele
        self.doc = doc
        self.d1 = 110
        self.d2 = 40
        self.type_manguito = "RED_110_40"

    def set_diameters(self, d1, d2):
        try:
            self.d1 = int(round(float(d1)))
            self.d2 = int(round(float(d2)))
        except Exception:
            self.d1, self.d2 = 110, 40
        self.type_manguito = (
            "RED_110_40" if _pair_supported(self.d1, self.d2) else "RED_INVALID"
        )

    def build(self):
        if not _pair_supported(self.d1, self.d2):
            return []
        return ConjuntosReduccion(self.build_ele, self.doc).build_model_list()


def create_element(build_ele, _doc) -> CreateElementResult:
    d1, d2 = _pair_from_build_ele(build_ele)
    if not _pair_supported(d1, d2):
        return CreateElementResult([])
    return ConjuntosReduccion(build_ele, _doc).create_result()


ManguitoModel = ReductConjuntosModel

__all__ = [
    "ConjuntosReduccion",
    "ReductConjuntosModel",
    "ManguitoModel",
    "SUPPORTED_REDUCTION_PAIRS",
    "create_element",
    "check_allplan_version",
]
