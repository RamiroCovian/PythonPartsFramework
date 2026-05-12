import math

import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


# Medidas base en metros (150x150)
LEFT_BOTTOM_THICK_M = 0.0250
LEFT_VERTICAL_M = 0.157
LEFT_DIAG_45_M = 0.28589
TOP_HORIZONTAL_M = 0.157
TOP_RIGHT_EXT_M = 0.0250
RIGHT_VERTICAL_M = 0.20000
RIGHT_BOTTOM_EXT_M = 0.0250
RIGHT_MID_HORIZONTAL_M = 0.0750
RIGHT_DIAG_45_M = 0.120
RIGHT_MID_VERTICAL_M = 0.0750
RIGHT_BOTTOM_THICK_M = 0.0250
BOTTOM_HORIZONTAL_M = 0.20000
BOTTOM_LEFT_THICK_M = 0.0250

SIZE_PRESETS = {
    "150x150": {},
    "150x200": {
        "LEFT_VERTICAL_M": 0.17888,
        "TOP_HORIZONTAL_M": 0.17888,
        "LEFT_DIAG_45_M": 0.32708,
        "RIGHT_VERTICAL_M": 0.25000,
        "BOTTOM_HORIZONTAL_M": 0.25000,
    },
    "150x250": {
        "LEFT_VERTICAL_M": 0.19926,
        "TOP_HORIZONTAL_M": 0.19926,
        "LEFT_DIAG_45_M": 0.36873,
        "RIGHT_VERTICAL_M": 0.30000,
        "BOTTOM_HORIZONTAL_M": 0.30000,
    },
    "150x300": {
        "LEFT_VERTICAL_M": 0.21997,
        "TOP_HORIZONTAL_M": 0.21997,
        "LEFT_DIAG_45_M": 0.41016,
        "RIGHT_VERTICAL_M": 0.35000,
        "BOTTOM_HORIZONTAL_M": 0.35000,
    },
    "150x350": {
        "LEFT_VERTICAL_M": 0.24069,
        "TOP_HORIZONTAL_M": 0.24069,
        "LEFT_DIAG_45_M": 0.45158,
        "RIGHT_VERTICAL_M": 0.40000,
        "BOTTOM_HORIZONTAL_M": 0.40000,
    },
    "150x400": {
        "LEFT_VERTICAL_M": 0.26140,
        "TOP_HORIZONTAL_M": 0.26140,
        "LEFT_DIAG_45_M": 0.49300,
        "RIGHT_VERTICAL_M": 0.45000,
        "BOTTOM_HORIZONTAL_M": 0.45000,
    },
    "150x450": {
        "LEFT_VERTICAL_M": 0.26140,
        "TOP_HORIZONTAL_M": 0.26140,
        "LEFT_DIAG_45_M": 0.59300,
        "RIGHT_VERTICAL_M": 0.50000,
        "BOTTOM_HORIZONTAL_M": 0.50000,
    },
    "150x500": {
        "LEFT_VERTICAL_M": 0.23211,
        "TOP_HORIZONTAL_M": 0.23211,
        "LEFT_DIAG_45_M": 0.67584,
        "RIGHT_VERTICAL_M": 0.55000,
        "BOTTOM_HORIZONTAL_M": 0.55000,
    },
    "150x550": {
        "LEFT_VERTICAL_M": 0.32353,
        "TOP_HORIZONTAL_M": 0.32353,
        "LEFT_DIAG_45_M": 0.61726,
        "RIGHT_VERTICAL_M": 0.60000,
        "BOTTOM_HORIZONTAL_M": 0.60000,
    },
    "150x600": {
        "LEFT_VERTICAL_M": 0.34353,
        "TOP_HORIZONTAL_M": 0.34353,
        "LEFT_DIAG_45_M": 0.65969,
        "RIGHT_VERTICAL_M": 0.65000,
        "BOTTOM_HORIZONTAL_M": 0.65000,
    },
    "150x650": {
        "LEFT_VERTICAL_M": 0.36495,
        "TOP_HORIZONTAL_M": 0.36495,
        "LEFT_DIAG_45_M": 0.70011,
        "RIGHT_VERTICAL_M": 0.70000,
        "BOTTOM_HORIZONTAL_M": 0.70000,
    },
    "150x700": {
        "LEFT_VERTICAL_M": 0.38566,
        "TOP_HORIZONTAL_M": 0.38566,
        "LEFT_DIAG_45_M": 0.74153,
        "RIGHT_VERTICAL_M": 0.75000,
        "BOTTOM_HORIZONTAL_M": 0.75000,
    },
    "150x750": {
        "LEFT_VERTICAL_M": 0.40637,
        "LEFT_DIAG_45_M": 0.78295,
        "TOP_HORIZONTAL_M": 0.40637,
        "RIGHT_VERTICAL_M": 0.80000,
        "BOTTOM_HORIZONTAL_M": 0.80000,
    },
}

# Alturas indicadas en la imagen (extrusión 3D)
MAIN_HEIGHT_M = 0.20000
LOWER_HEIGHT_M = 0.199
RIGHT_LOWER_HEIGHT_M = 0.199

# Flecha 3D (en metros)
ARROW_LENGTH_M = 0.14
ARROW_HALF_WIDTH_M = 0.03
ARROW_THICK_M = 0.005
ARROW_Z_OFFSET_M = 0.005
ARROW_COLOR = 65
ARROW_ANGLE_DEG = 135.0
ARROW_POS_X_FACTOR = 0.45
ARROW_POS_Y_FACTOR = 0.55

# Mantener polilínea abierta para el contorno 2D (solo informativo).
# Para el sólido 3D siempre se cierra la huella.
CLOSE_POLYLINE = False

M_TO_MM = 1000.0

COLZE_TYPE_DEFAULT = "Implusio"
COMBO_NAME_BY_COLZE = {
    "Implusio": "TypeColzeImplusio",
    "Retorn": "TypeColzeRetorn",
}
ARROW_COLOR_BY_COLZE = {
    "Implusio": 8,
    "Retorn": 65,
}
ARROW_ANGLE_BY_COLZE = {
    # Ajuste 2026-04-23: la flecha estaba invertida en codos tras aplicar
    # la transformación global del pipeline. Invertimos 180° los ángulos base.
    "Implusio": 45.0,
    "Retorn": -135.0,
}
ARROW_CENTER_DEBUG = True
# Ajuste fino visual solicitado: posicionar la flecha en el punto objetivo
# marcado por usuario (punto rojo de referencia).
ARROW_TARGET_OFFSET_X_MM = -55.0
ARROW_TARGET_OFFSET_Y_MM = 85.0

def check_allplan_version(_build_ele, _version) -> bool:
    return True


def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    colze = ColzeModel(build_ele, script_object_data)
    model_ele_list = colze.build()

    return model_ele_list, []

def create_script_object(build_ele, script_object_data):
    return ColzeScript(build_ele, script_object_data)


class ColzeModel:
    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        self.build_ele = build_ele

    def _length_mm(self, name: str, default_m: float) -> float:
        if self.build_ele is not None and hasattr(self.build_ele, name):
            return float(getattr(self.build_ele, name).value)
        return default_m * M_TO_MM

    def _build_points_mm(self, params):
        segments = [
            (params["LEFT_BOTTOM_THICK_M"] * M_TO_MM, 90.0),
            (params["LEFT_VERTICAL_M"] * M_TO_MM, 90.0),
            (params["LEFT_DIAG_45_M"] * M_TO_MM, 45.0),
            (params["TOP_HORIZONTAL_M"] * M_TO_MM, 0.0),
            (params["TOP_RIGHT_EXT_M"] * M_TO_MM, 0.0),
            (params["RIGHT_VERTICAL_M"] * M_TO_MM, -90.0),
            (params["RIGHT_BOTTOM_EXT_M"] * M_TO_MM, 180.0),
            (params["RIGHT_MID_HORIZONTAL_M"] * M_TO_MM, 180.0),
            (params["RIGHT_DIAG_45_M"] * M_TO_MM, -135.0),
            (params["RIGHT_MID_VERTICAL_M"] * M_TO_MM, -90.0),
            (params["RIGHT_BOTTOM_THICK_M"] * M_TO_MM, -90.0),
            (params["BOTTOM_HORIZONTAL_M"] * M_TO_MM, 180.0),
            (params["BOTTOM_LEFT_THICK_M"] * M_TO_MM, 90.0),
        ]

        points = [AllplanGeometry.Point2D(0.0, 0.0)]
        x = 0.0
        y = 0.0

        for length, angle_deg in segments:
            angle_rad = math.radians(angle_deg)
            x += length * math.cos(angle_rad)
            y += length * math.sin(angle_rad)
            points.append(AllplanGeometry.Point2D(x, y))

        return points

    def _extrude_polygon(self, points_2d, height_mm):
        poly_points = [AllplanGeometry.Point3D(p.X, p.Y, 0.0) for p in points_2d]
        if poly_points[0] != poly_points[-1]:
            poly_points.append(poly_points[0])
        polygon = AllplanGeometry.Polygon3D(poly_points)

        path = AllplanGeometry.Polyline3D()
        path += AllplanGeometry.Point3D(0.0, 0.0, 0.0)
        path += AllplanGeometry.Point3D(0.0, 0.0, height_mm)

        err, body = AllplanGeometry.CreatePolyhedron(polygon, path)
        if err != 0 or body is None or not body.IsValid():
            return None
        return body

    def build(self):
        common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        common_props.Color = 207
        common_props.ColorByLayer = False

        colze_type_raw = getattr(self.build_ele, "TypeColze", None)
        colze_type_val = getattr(colze_type_raw, "value", colze_type_raw)
        colze_type = (
            str(colze_type_val) if colze_type_val is not None else COLZE_TYPE_DEFAULT
        )
        if colze_type not in COMBO_NAME_BY_COLZE:
            colze_type = COLZE_TYPE_DEFAULT

        # Tamaño: prioridad DiameterType (paleta polilínea); fallback combos del PythonPart
        size_key = "150x150"
        diam_raw = getattr(self.build_ele, "DiameterType", None)
        diam_val = getattr(diam_raw, "value", diam_raw) if diam_raw is not None else None
        if diam_val is not None and str(diam_val).strip():
            # Polilínea/tram_recte: "750x150" (ancho x 150). Colze: "150x750" (150 x ancho).
            diam_key = str(diam_val).strip()
            if diam_key in SIZE_PRESETS:
                size_key = diam_key
            else:
                parts = diam_key.split("x")
                if len(parts) == 2:
                    size_key = f"{parts[1].strip()}x{parts[0].strip()}"
                size_key = size_key if size_key in SIZE_PRESETS else "150x150"
        else:
            combo_param_name = COMBO_NAME_BY_COLZE.get(colze_type, "TypeColzeImplusio")
            size_raw = getattr(self.build_ele, combo_param_name, None)
            size_val = getattr(size_raw, "value", size_raw)
            size_key = str(size_val) if size_val is not None else "150x150"
            size_key = size_key if size_key in SIZE_PRESETS else "150x150"

        # Tipo desde polilínea: InstallationType IMPULSION -> Implusio, RETORN -> Retorn
        inst_raw = getattr(self.build_ele, "InstallationType", None)
        inst_val = getattr(inst_raw, "value", inst_raw) if inst_raw is not None else None
        if inst_val is not None and str(inst_val).strip().upper() == "IMPULSION":
            colze_type = "Implusio"
        elif inst_val is not None and str(inst_val).strip().upper() == "RETORN":
            colze_type = "Retorn"

        # Log para verificar uso desde paleta
        _diam_src = str(diam_val).strip() if diam_val is not None else ""
        print(f"[Colze] tipo={colze_type} size_key={size_key} (paleta: InstallationType={inst_val} DiameterType={_diam_src})")

        arrow_color = ARROW_COLOR_BY_COLZE.get(colze_type, ARROW_COLOR)
        arrow_angle = ARROW_ANGLE_BY_COLZE.get(colze_type, ARROW_ANGLE_DEG)

        params = {
            "LEFT_BOTTOM_THICK_M": LEFT_BOTTOM_THICK_M,
            "LEFT_VERTICAL_M": LEFT_VERTICAL_M,
            "LEFT_DIAG_45_M": LEFT_DIAG_45_M,
            "TOP_HORIZONTAL_M": TOP_HORIZONTAL_M,
            "TOP_RIGHT_EXT_M": TOP_RIGHT_EXT_M,
            "RIGHT_VERTICAL_M": RIGHT_VERTICAL_M,
            "RIGHT_BOTTOM_EXT_M": RIGHT_BOTTOM_EXT_M,
            "RIGHT_MID_HORIZONTAL_M": RIGHT_MID_HORIZONTAL_M,
            "RIGHT_DIAG_45_M": RIGHT_DIAG_45_M,
            "RIGHT_MID_VERTICAL_M": RIGHT_MID_VERTICAL_M,
            "RIGHT_BOTTOM_THICK_M": RIGHT_BOTTOM_THICK_M,
            "BOTTOM_HORIZONTAL_M": BOTTOM_HORIZONTAL_M,
            "BOTTOM_LEFT_THICK_M": BOTTOM_LEFT_THICK_M,
        }
        params.update(SIZE_PRESETS.get(size_key, {}))

        points_2d = self._build_points_mm(params)
        if len(points_2d) < 14:
            return []

        # Cuerpo principal a altura completa (un solo sólido)

        main_outline = points_2d
        main_height_mm = self._length_mm("MainHeight", MAIN_HEIGHT_M)
        main_body = self._extrude_polygon(main_outline, main_height_mm)

        # Zócalo inferior (desnivel a 0.199 m)
        lower_outline = [points_2d[10], points_2d[11], points_2d[12], points_2d[13]]
        lower_height_mm = self._length_mm("LowerHeight", LOWER_HEIGHT_M)

        # Salida derecha (desnivel a 0.199 m)
        right_lower_outline = [points_2d[4], points_2d[5], points_2d[6], points_2d[7]]
        right_lower_height_mm = self._length_mm("RightLowerHeight", RIGHT_LOWER_HEIGHT_M
        )

        elements: list = []
        if main_body is not None:
            # Recortar el zócalo inferior para crear el desnivel
            diff_height_mm = main_height_mm - lower_height_mm
            if diff_height_mm > 0.0:
                cut_body = self._extrude_polygon(lower_outline, diff_height_mm)
                if cut_body is not None:
                    mat_up = AllplanGeometry.Matrix3D()
                    mat_up.SetTranslation(
                        AllplanGeometry.Vector3D(0.0, 0.0, lower_height_mm)
                    )
                    cut_body = AllplanGeometry.Transform(cut_body, mat_up)
                    err_sub, main_body_cut = AllplanGeometry.MakeSubtraction(
                        main_body, cut_body
                    )
                    if err_sub == 0 and main_body_cut is not None and main_body_cut.IsValid():
                        main_body = main_body_cut

            # Recortar la salida derecha para crear el desnivel
            diff_height_mm = main_height_mm - right_lower_height_mm
            if diff_height_mm > 0.0:
                cut_body = self._extrude_polygon(right_lower_outline, diff_height_mm)
                if cut_body is not None:
                    mat_up = AllplanGeometry.Matrix3D()
                    mat_up.SetTranslation(
                        AllplanGeometry.Vector3D(0.0, 0.0, right_lower_height_mm)
                    )
                    cut_body = AllplanGeometry.Transform(cut_body, mat_up)
                    err_sub, main_body_cut = AllplanGeometry.MakeSubtraction(
                        main_body, cut_body
                    )
                    if err_sub == 0 and main_body_cut is not None and main_body_cut.IsValid():
                        main_body = main_body_cut

            min_x = min(p.X for p in points_2d)
            max_x = max(p.X for p in points_2d)
            min_y = min(p.Y for p in points_2d)
            max_y = max(p.Y for p in points_2d)
            # Centrar el codo en el eje de los tubos (centro de sección)
            size_parts = size_key.split("x")
            width_mm = None
            if len(size_parts) == 2:
                try:
                    width_mm = float(size_parts[1])
                except Exception:
                    width_mm = None
            thickness_mm = LEFT_BOTTOM_THICK_M * M_TO_MM
            if width_mm is not None:
                center_x = min_x + thickness_mm + (width_mm * 0.5)
                center_y = min_y + thickness_mm + (width_mm * 0.5) #+ 185.0
            else:
                center_x = (min_x + max_x) * 0.5
                center_y = (min_y + max_y) * 0.5
            center_z = main_height_mm * 0.5

            mat_center = AllplanGeometry.Matrix3D()
            mat_center.SetTranslation(
                AllplanGeometry.Vector3D(-center_x, -center_y, -center_z)
            )
            main_body = AllplanGeometry.Transform(main_body, mat_center)

            err_conv, codo_brep = AllplanGeometry.CreateBRep3D(main_body)

            matriz_roll = AllplanGeometry.Matrix3D()
            eje_x_local = AllplanGeometry.Line3D(AllplanGeometry.Point3D(0,0,0), AllplanGeometry.Point3D(0,1,0))
            matriz_roll.SetRotation(eje_x_local, AllplanGeometry.Angle.FromDeg(180))
            brep = AllplanGeometry.Transform(codo_brep, matriz_roll)

            elements.append(AllplanBasisElements.ModelElement3D(common_props, brep))

            arrow_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            arrow_props.Color = arrow_color
            arrow_props.ColorByLayer = False

            arrow_center_x = min_x + (max_x - min_x) * ARROW_POS_X_FACTOR - center_x
            arrow_center_y = min_y + (max_y - min_y) * ARROW_POS_Y_FACTOR - center_y
            arrow_length = ARROW_LENGTH_M * M_TO_MM
            arrow_half_width = ARROW_HALF_WIDTH_M * M_TO_MM
            arrow_thick = ARROW_THICK_M * M_TO_MM
            arrow_z_base = main_height_mm + ARROW_Z_OFFSET_M * M_TO_MM - center_z

            base_y = -arrow_length * 0.5
            tip_y = base_y + arrow_length
            arrow_pts = [
                (-arrow_half_width, base_y),
                (-arrow_half_width, tip_y - arrow_half_width * 2),
                (-arrow_half_width * 2, tip_y - arrow_half_width * 2),
                (0.0, tip_y),
                (arrow_half_width * 2, tip_y - arrow_half_width * 2),
                (arrow_half_width, tip_y - arrow_half_width * 2),
                (arrow_half_width, base_y),
            ]

            ang = math.radians(arrow_angle)
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)

            arrow_poly_pts = []
            for x, y in arrow_pts:
                rx = x * cos_a - y * sin_a + arrow_center_x
                ry = x * sin_a + y * cos_a + arrow_center_y
                arrow_poly_pts.append(AllplanGeometry.Point3D(rx, ry, arrow_z_base))
            arrow_poly_pts.append(arrow_poly_pts[0])

            arrow_poly = AllplanGeometry.Polygon3D(arrow_poly_pts)
            arrow_path = AllplanGeometry.Polyline3D()
            arrow_path += AllplanGeometry.Point3D(0.0, 0.0, arrow_z_base)
            arrow_path += AllplanGeometry.Point3D(0.0, 0.0, arrow_z_base + arrow_thick)

            err_arrow, arrow_body = AllplanGeometry.CreatePolyhedron(arrow_poly, arrow_path)
            if err_arrow == 0 and arrow_body is not None and arrow_body.IsValid():
                err_conv, arrow_brep = AllplanGeometry.CreateBRep3D(arrow_body)
                if err_conv == 0 and arrow_brep is not None and arrow_brep.IsValid():
                    # Centrar la flecha usando su "cubo" envolvente (bbox) en XY
                    # respecto al centro del codo (0,0 tras mat_center).
                    try:
                        verts_result = arrow_brep.GetVertices()
                        verts = None
                        if isinstance(verts_result, tuple):
                            if len(verts_result) >= 2 and isinstance(verts_result[1], list):
                                verts = verts_result[1]
                            elif len(verts_result) >= 1 and isinstance(verts_result[-1], list):
                                verts = verts_result[-1]
                        elif isinstance(verts_result, list):
                            verts = verts_result

                        if verts:
                            min_xv = min(v.X for v in verts)
                            max_xv = max(v.X for v in verts)
                            min_yv = min(v.Y for v in verts)
                            max_yv = max(v.Y for v in verts)
                            cx = (min_xv + max_xv) * 0.5
                            cy = (min_yv + max_yv) * 0.5
                            if ARROW_CENTER_DEBUG:
                                print(
                                    "[Colze][ArrowDebug] pre_center"
                                    f" type={colze_type} size={size_key}"
                                    f" codo_center_xy=(0.000,0.000)"
                                    f" arrow_bbox_center_xy=({cx:.3f},{cy:.3f})"
                                    f" delta_xy=({cx:.3f},{cy:.3f})"
                                    f" bbox_xy=[({min_xv:.3f},{min_yv:.3f})-({max_xv:.3f},{max_yv:.3f})]"
                                )

                            m_center_arrow = AllplanGeometry.Matrix3D()
                            m_center_arrow.SetTranslation(
                                AllplanGeometry.Vector3D(-cx, -cy, 0.0)
                            )
                            arrow_brep = AllplanGeometry.Transform(arrow_brep, m_center_arrow)
                            # Desplazamiento final al punto objetivo dentro del codo.
                            m_target_arrow = AllplanGeometry.Matrix3D()
                            m_target_arrow.SetTranslation(
                                AllplanGeometry.Vector3D(
                                    float(ARROW_TARGET_OFFSET_X_MM),
                                    float(ARROW_TARGET_OFFSET_Y_MM),
                                    0.0,
                                )
                            )
                            arrow_brep = AllplanGeometry.Transform(arrow_brep, m_target_arrow)
                            if ARROW_CENTER_DEBUG:
                                print(
                                    "[Colze][ArrowDebug] post_center"
                                    f" type={colze_type} size={size_key}"
                                    f" codo_center_xy=(0.000,0.000)"
                                    f" arrow_bbox_center_xy=({ARROW_TARGET_OFFSET_X_MM:.3f},{ARROW_TARGET_OFFSET_Y_MM:.3f})"
                                    f" delta_xy=({ARROW_TARGET_OFFSET_X_MM:.3f},{ARROW_TARGET_OFFSET_Y_MM:.3f})"
                                )
                    except Exception:
                        pass

                    elements.append(AllplanBasisElements.ModelElement3D(arrow_props, arrow_brep))

        return elements


class ColzeScript(BaseScriptObject):
    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        attr_list = []
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """Punto de entrada principal para la generación del elemento.

        kwargs:
            installation_type (str): "impulsion" | "retorn"
            diameter          (str): "150x150" | "200x150" | ... | "750x150"
        """
        if "installation_type" in kwargs:
            param = getattr(self.build_ele, "InstallationType", None)
            if param is not None:
                param.value = kwargs["installation_type"]

        if "diameter" in kwargs:
            param = getattr(self.build_ele, "DiameterType", None)
            if param is not None:
                param.value = kwargs["diameter"]

        # Forzar alturas de referencia cuando se soliciten desde la factoría
        # para evitar desajustes de Z en la primera creación (defaults aún no cacheados).
        if "main_height_mm" in kwargs:
            param = getattr(self.build_ele, "MainHeight", None)
            if param is not None:
                param.value = float(kwargs["main_height_mm"])
        if "lower_height_mm" in kwargs:
            param = getattr(self.build_ele, "LowerHeight", None)
            if param is not None:
                param.value = float(kwargs["lower_height_mm"])
        if "right_lower_height_mm" in kwargs:
            param = getattr(self.build_ele, "RightLowerHeight", None)
            if param is not None:
                param.value = float(kwargs["right_lower_height_mm"])

        colze_model = ColzeModel(self.build_ele, self.doc)
        model_ele_list = colze_model.build()
        return CreateElementResult(model_ele_list)
