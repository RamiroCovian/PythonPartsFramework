# -*- coding: utf-8 -*-
"""reductores rígidos"""

import math
from typing import Optional, Any

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult


# ===== Requisito estándar =====
def check_allplan_version(_build_ele, _version) -> bool:
    """Check Allplan version compatibility."""
    return True


# ===== Configuraciones =====
# Parámetros de rotación por tipo de tubo
ROTATIONS = {
    0: {"x": 0.0, "y": 0.0, "z": 0.0},  # R40-50mm
    2: {"x": 0.0, "y": 90.0, "z": 90.0}    # R50-110mm z90
}

# Parámetros de posición del anillo (solo para TipoTubo=2)
ANILLO_PARAMS = {
    "dx": 0.0,
    "dy": 0.0,
    "dz": -5.0
}

# Dimensiones y configuraciones para figuras
FIGURE_CONFIGS = {
    "cuboide_base": {"width": 110.0, "depth": 60.0, "height": 110.0},
    "trapecio": {
        "base_mayor": 110.0,
        "alto": 50.0,
        "angulo_caras_deg": 33.0,
        "salida_sur": 55.0,
        "rot_x": 0.0,
        "rot_y": 90.0,
        "rot_z": 0.0,
        "offset_x": -27.5,
        "offset_z": 0.0
    },
    "bloque_adicional": {"x": 50.0, "y": 30.0, "z": 45.0},
    "anillo": {"largo": 10.0, "sobresale": 5.0},
    "prisma_triangular": {
        "size": 55.5,
        "rot_x": 180.0,
        "rot_y": 0.0,
        "rot_z": 0.0,
        "offset_x": -27.5,
        "offset_y": 20.0,
        "offset_z": 0.0
    }
}


class Reductores:
    """Implementación OO de reductores.

    - TipoTubo = 0 → Dos cuboides unidos (50×50×65) + (40×40×45).
    - TipoTubo = 2 → Figura reductora (cuboide base + prisma trapezoidal + añadidos).
    - Otros → no crea elementos.
    """

    DEFAULT_PARAMS: dict[str, float] = {
        "COLOR": 70
    }
    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(self, build_ele, doc=None, params: Optional[dict[str, float]] = None):
        """Initialize the Reductores class.

        Args:
            build_ele: The build element from Allplan.
            doc: Document adapter for attribute access.
            params: Optional parameters dictionary.
        """
        self.build_ele = build_ele
        self.doc = doc
        self.params = dict(self.DEFAULT_PARAMS)
        if params:
            self.params.update(params)

    # ---------- API ----------
    def create_result(self) -> CreateElementResult:
        """Create the result based on TipoTubo value."""
        tipo_val = self._get_build_ele_value("TipoTubo")

        if tipo_val == 0:
            rot = ROTATIONS.get(0, {"x": 0.0, "y": 0.0, "z": 0.0})
            elems = self._build_cuboides(self.params, rot["x"], rot["y"], rot["z"])
        elif tipo_val == 2:
            rot = ROTATIONS.get(2, {"x": 0.0, "y": 0.0, "z": 0.0})
            elems = self._build_figura_reductora(self.params, rot["x"], rot["y"], rot["z"])
        else:
            elems = []

        # Add attributes to first element if exists
        if elems:
            model_elem = elems[0]
            attr_list = []

            if tipo_val == 0:
                # R40-50
                attr_list.append(AllplanBaseElements.AttributeString(1083, "RED. M-F 50-40Ø"))  # Custom attribute 01
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40-50"))           # Custom attribute 02
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                 # Custom attribute 03
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                 # Custom attribute 04
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                 # Custom attribute 05
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))                 # Custom attribute 06
                attr_list.append(AllplanBaseElements.AttributeString(1896, "40-50"))            # Custom attribute 07
                attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                 # Custom attribute 08
                attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                 # Custom attribute 09
                attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                 # Custom attribute 10
                attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                 # Custom attribute 11
                attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                 # Custom attribute 12
                attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                 # Custom attribute 13
                attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                 # Custom attribute 14
                attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                 # Custom attribute 15
                
                # Agregar atributos de usuario adicionales si hay documento disponible
                if self.doc:
                    self._add_user_attributes_50_40(attr_list)
            elif tipo_val == 2:
                # R50-110
                attr_list.append(AllplanBaseElements.AttributeString(1083, "RED. M-F 110-50Ø"))  # Custom attribute 01
                attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110-50"))           # Custom attribute 02
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))                  # Custom attribute 03
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))                  # Custom attribute 04
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))                  # Custom attribute 05
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))                  # Custom attribute 06
                attr_list.append(AllplanBaseElements.AttributeString(1896, "110-50"))            # Custom attribute 07
                attr_list.append(AllplanBaseElements.AttributeString(1897, ""))                  # Custom attribute 08
                attr_list.append(AllplanBaseElements.AttributeString(1898, ""))                  # Custom attribute 09
                attr_list.append(AllplanBaseElements.AttributeString(1899, ""))                  # Custom attribute 10
                attr_list.append(AllplanBaseElements.AttributeString(1900, ""))                  # Custom attribute 11
                attr_list.append(AllplanBaseElements.AttributeString(1901, ""))                  # Custom attribute 12
                attr_list.append(AllplanBaseElements.AttributeString(1902, ""))                  # Custom attribute 13
                attr_list.append(AllplanBaseElements.AttributeString(1903, ""))                  # Custom attribute 14
                attr_list.append(AllplanBaseElements.AttributeString(1904, ""))                  # Custom attribute 15
                
                # Agregar atributos de usuario adicionales si hay documento disponible
                if self.doc:
                    self._add_user_attributes_110_50(attr_list)
            else:
                attr_list.append(AllplanBaseElements.AttributeString(1083, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1084, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1085, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1086, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1087, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1895, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1896, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1897, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1898, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1899, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1900, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1901, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1902, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1903, ""))
                attr_list.append(AllplanBaseElements.AttributeString(1904, ""))

            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            attributes = AllplanBaseElements.Attributes([attr_set])
            model_elem.SetAttributes(attributes)

        return CreateElementResult(elems)

    # ---------- Utilidades ----------
    def _get_build_ele_value(self, attr: str) -> Optional[Any]:
        """Get value from build element attribute."""
        val = getattr(self.build_ele, attr, None)
        if hasattr(val, "value"):
            try:
                return int(val.value)
            except ValueError:
                return None
        return None

    def _props(self, color: int, pen: int = 1, stroke: int = 1, layer: int = None) -> Any:
        """Create properties for the model element."""
        if layer is None:
            layer = self.LAYER
        p = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        p.Color = color
        p.ColorByLayer = False  # No afectar el color
        p.Pen = pen
        p.Stroke = stroke
        p.Layer = layer
        return p

    @staticmethod
    def _create_trapezoidal_prism(base1, base2, height, length) -> Optional[Any]:
        """Create a trapezoidal prism solid."""
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
    def _make_union(*solids) -> Any:
        """Make union of multiple solids."""
        result = solids[0]
        for s in solids[1:]:
            err, result2 = AllplanGeo.MakeUnion(result, s)
            if err == 0 and result2 and result2.IsValid():
                result = result2
        return result

    @staticmethod
    def _apply_rotations(solid, cx, cy, cz, rx=0.0, ry=0.0, rz=0.0) -> Any:
        """Apply rotations to a solid around a center point."""
        for angle, axis in zip([rx, ry, rz], ["x", "y", "z"]):
            if abs(angle) > 1e-6:
                mat = AllplanGeo.Matrix3D()
                if axis == "x":
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx + 1.0, cy, cz)
                elif axis == "y":
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy + 1.0, cz)
                else:
                    axis_line = AllplanGeo.Line3D(cx, cy, cz, cx, cy, cz + 1.0)
                mat.SetRotation(axis_line, AllplanGeo.Angle(math.radians(angle)))
                solid = AllplanGeo.Transform(solid, mat)
        return solid

    def _add_user_attributes_50_40(self, attr_list):
        """Agrega atributos de usuario para reducción 50-40mm."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_007_001"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_007_001"))

            # pmp_nom: "RED. M-F 50-40Ø"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED. M-F 50-40Ø"))

            # pmp_pes_unitari: 0.0319 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.0319))

            # pmp_seccio: "Ø40-50mm" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "Ø40-50mm"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Reductiorigid_007] Advertencia al agregar atributos de usuario 50-40mm: {e}")

    def _add_user_attributes_110_50(self, attr_list):
        """Agrega atributos de usuario para reducción 110-50mm."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_pes_unitari_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_pes_unitari")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: "KN07_007_002"
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, "KN07_007_002"))

            # pmp_nom: "RED. M-F 110-50Ø"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "RED. M-F 110-50Ø"))

            # pmp_pes_unitari: 0.1119 (AttributeDouble)
            if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_pes_unitari_id, 0.1119))

            # pmp_seccio: "110-50" (AttributeString)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110-50"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Reductiorigid_007] Advertencia al agregar atributos de usuario 110-50mm: {e}")

    # ---------- Tipo 0: dos cuboides unidos ----------
    def _build_cuboides(self, params: dict[str, float], rot_x=0.0, rot_y=0.0, rot_z=0.0) -> list[Any]:
        """Build cuboides for TipoTubo=0."""
        p = params
        props = self._props(color=p["COLOR"])

        # Orientaciones tal como en el script original
        x_dir = AllplanGeo.Vector3D(0, 0, 1)
        z_dir = AllplanGeo.Vector3D(1, 0, 0)

        axis1 = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), x_dir, z_dir)
        cuboide_50 = AllplanGeo.BRep3D.CreateCuboid(axis1, 50, 50, 65)

        axis2 = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(65, 0, 0), x_dir, z_dir)
        cuboide_40 = AllplanGeo.BRep3D.CreateCuboid(axis2, 40, 40, 45)

        solido = self._make_union(cuboide_50, cuboide_40)
        # Rotación sobre su propio eje
        cx, cy, cz = 50.0, 25.0, 32.5  # centro aproximado del sólido
        solido = self._apply_rotations(solido, cx, cy, cz, rot_x, rot_y, rot_z)
        return [AllplanBasisElements.ModelElement3D(props, solido)]

    # ---------- Tipo 2: figura reductora ----------
    def _build_figura_reductora(self, _params: dict[str, float], rot_x=0.0, rot_y=0.0, rot_z=0.0) -> list[Any]:
        """Build figura reductora for TipoTubo=2."""
        props = self._props(color=70)

        # Cuboide base
        config_base = FIGURE_CONFIGS["cuboide_base"]
        cara_inf = AllplanGeo.Polygon3D([
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(config_base["width"], 0, 0),
            AllplanGeo.Point3D(config_base["width"], config_base["depth"], 0),
            AllplanGeo.Point3D(0, config_base["depth"], 0),
            AllplanGeo.Point3D(0, 0, 0)
        ])
        path_cuboide = AllplanGeo.Polyline3D()
        path_cuboide += AllplanGeo.Point3D(0, 0, 0)
        path_cuboide += AllplanGeo.Point3D(0, 0, config_base["height"])
        err, cuboide = AllplanGeo.CreatePolyhedron(cara_inf, path_cuboide)
        if err != 0 or cuboide is None or not cuboide.IsValid():
            return []

        # Trapecio
        config_trap = FIGURE_CONFIGS["trapecio"]
        base_menor = max(1.0, config_trap["base_mayor"] - 2.0 * config_trap["alto"] * math.tan(math.radians(config_trap["angulo_caras_deg"])))
        trap = self._create_trapezoidal_prism(base1=base_menor, base2=config_trap["base_mayor"], height=config_trap["alto"], length=config_trap["salida_sur"])
        if trap is None:
            return [AllplanBasisElements.ModelElement3D(props, cuboide)]

        dx = (config_base["width"] - config_trap["base_mayor"]) * 0.5
        dy = -config_trap["alto"] + 0.1  # EPS_UNION
        dz = (config_base["height"] - config_trap["salida_sur"]) * 0.5

        trap = AllplanGeo.Move(trap, AllplanGeo.Vector3D(dx + config_trap["offset_x"], dy, dz + config_trap["offset_z"]))
        cx = dx + config_trap["offset_x"] + config_trap["base_mayor"] * 0.5
        cy = dy + config_trap["alto"] * 0.5
        cz = dz + config_trap["offset_z"] + config_trap["salida_sur"] * 0.5
        trap = self._apply_rotations(trap, cx, cy, cz, config_trap["rot_x"], config_trap["rot_y"], config_trap["rot_z"])

        final_body = self._make_union(cuboide, trap)

        # Bloque adicional
        config_add = FIGURE_CONFIGS["bloque_adicional"]
        x_center = dx + config_trap["offset_x"] + config_trap["base_mayor"] * 0.5 - 2.5
        z_center = dz + config_trap["offset_z"] + config_trap["salida_sur"] * 0.5
        y_top = dy

        add_min = AllplanGeo.Point3D(x_center - config_add["x"] * 0.5, y_top - config_add["y"], z_center - config_add["z"] * 0.5)
        add_max = AllplanGeo.Point3D(x_center + config_add["x"] * 0.5, y_top, z_center + config_add["z"] * 0.5)
        cubo_trunc = AllplanGeo.Polyhedron3D.CreateCuboid(add_min, add_max)
        final_body = self._make_union(final_body, cubo_trunc)

        # Anillo
        config_anillo = FIGURE_CONFIGS["anillo"]
        y_end_cubo = y_top - config_add["y"]
        ring_min = AllplanGeo.Point3D(
            x_center - (config_add["x"] * 0.5 + config_anillo["sobresale"]) + ANILLO_PARAMS["dx"],
            y_end_cubo - config_anillo["largo"] + ANILLO_PARAMS["dy"],
            z_center - (config_add["z"] * 0.5 + config_anillo["sobresale"]) + ANILLO_PARAMS["dz"]
        )
        ring_max = AllplanGeo.Point3D(
            x_center + (config_add["x"] * 0.5 + config_anillo["sobresale"]) + ANILLO_PARAMS["dx"],
            y_end_cubo + ANILLO_PARAMS["dy"],
            z_center + (config_add["z"] * 0.5 + config_anillo["sobresale"]) + ANILLO_PARAMS["dz"]
        )
        anillo = AllplanGeo.Polyhedron3D.CreateCuboid(ring_min, ring_max)
        final_body = self._make_union(final_body, anillo)

        # Prisma triangular
        config_tri = FIGURE_CONFIGS["prisma_triangular"]
        p0t = AllplanGeo.Point3D(0.0, 0.0, 0.0)
        p1t = AllplanGeo.Point3D(config_tri["size"], 0.0, 0.0)
        p2t = AllplanGeo.Point3D(0.0, config_tri["size"], 0.0)
        base_face = AllplanGeo.Polygon3D([p0t, p1t, p2t, p0t])

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeo.Point3D(0.0, 0.0, config_tri["size"])

        err_tri, prisma_tri = AllplanGeo.CreatePolyhedron(base_face, path)
        if err_tri == 0 and prisma_tri and prisma_tri.IsValid():
            cx3 = config_tri["size"] / 3.0
            cy3 = config_tri["size"] / 3.0
            cz3 = config_tri["size"] / 2.0
            prisma_tri = self._apply_rotations(prisma_tri, cx3, cy3, cz3, config_tri["rot_x"], config_tri["rot_y"], config_tri["rot_z"])

            x_right = dx + config_trap["offset_x"] + config_trap["base_mayor"] + config_tri["offset_x"]
            y_b = dy + config_tri["offset_y"]
            z_b = z_center - config_tri["size"] * 0.5 + config_tri["offset_z"]

            prisma_tri = AllplanGeo.Move(prisma_tri, AllplanGeo.Vector3D(x_right, y_b, z_b))
            final_body = self._make_union(final_body, prisma_tri)

        # Rotación final
        cx, cy, cz = 55.0, 30.0, 55.0  # centro aproximado del sólido
        final_body = self._apply_rotations(final_body, cx, cy, cz, rot_x, rot_y, rot_z)

        model = AllplanBasisElements.ModelElement3D(props, final_body)
        return [model]


# ===== Punto de entrada PythonPart =====
def create_element(build_ele, _doc) -> CreateElementResult:
    """Create element for PythonPart."""
    return Reductores(build_ele, _doc).create_result()
