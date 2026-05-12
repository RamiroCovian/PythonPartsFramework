import math
import os
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService
import NemAll_Python_AllplanSettings as AllplanSettings


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS_BASE = [
    # 150x150
    {  # Outer
        "LEN_X": 457.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": 0.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 200.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 200.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "150",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200.0",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 200x150
    {  # Outer
        "LEN_X": 507.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -50.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 250.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 250.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "200",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 250x150
    {  # Outer
        "LEN_X": 557.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -100.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 300.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 300.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "250",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 300x150
    {  # Outer
        "LEN_X": 607.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -150.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 350.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 350.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "300",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 350x150
    {  # Outer
        "LEN_X": 657.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -200.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 400.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 400.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "350",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 400x150
    {  # Outer
        "LEN_X": 707.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -250.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 450.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 450.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "400",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 450x150
    {  # Outer
        "LEN_X": 757.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -300.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 500.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 500.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "450",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 500x150
    {  # Outer
        "LEN_X": 807.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -350.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 550.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 550.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "500",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 550x150
    {  # Outer
        "LEN_X": 857.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -400.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 600.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 600.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "550",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 600x150
    {  # Outer
        "LEN_X": 907.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -450.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 650.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 650.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "600",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 650x150
    {  # Outer
        "LEN_X": 957.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -500.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 700.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 700.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "650",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 700x150
    {  # Outer
        "LEN_X": 1007.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -550.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 750.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 750.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "700",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
    # 750x150
    {  # Outer
        "LEN_X": 1057.0,
        "LEN_Y": 1000.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        "DIFX": -600.0,
        # Caps
        "CAP_ARM_X_BIGGEST": 800.0,
        "CAP_ARM_Y_BIGGEST": 75.0,
        "CAP_HEIGHT_BIGGEST": 200.0,
        "CAP_ARM_X_SMALLEST": 800.0,
        "CAP_ARM_Y_SMALLEST": 25.0,
        "CAP_HEIGHT_SMALLEST": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "750",
        "DESVIACIÓ QUIEBRO": 256,
        "LONG. QUIEBRO": "1200",
        "NUMERO PEÇA": 2,  # Numero de pieza
        "TIPUS DE PEÇA": "QUIEBRO",
    },
]

# Estructura de parámetros por tipo
# Todos los tipos comparten los mismos parámetros geométricos
PARAMS = {
    "Retorn": PARAMS_BASE,
    "Impulsió": PARAMS_BASE,
}

# Mapeo del tamaño (string) a índice en la lista de parámetros
MAP_QUIEBRO_SIZE = {
    "150x150": 0,
    "200x150": 1,
    "250x150": 2,
    "300x150": 3,
    "350x150": 4,
    "400x150": 5,
    "450x150": 6,
    "500x150": 7,
    "550x150": 8,
    "600x150": 9,
    "650x150": 10,
    "700x150": 11,
    "750x150": 12,
}

COMBO_NAME_BY_QUIEBRO = {
    "Retorn": "TypeQuiebroRetorn",
    "Impulsió": "TypeQuiebroImpulsió",
}

# Colores de la flecha según el tipo
ARROW_COLOR_BY_QUIEBRO_TYPE = {
    "Retorn": 65,
    "Impulsió": 8,
}

# Longitud permitida del quiebro (mm): la polilínea ajusta con set_length()
MIN_LENGTH_MM = 200.0
MAX_LENGTH_MM = 1000.0
CUT_REFERENCE_LENGTH_MM = 1000.0

# IDs fijos de atributos (usar si GetAttributeID no encuentra el atributo)
# Si conoces el ID del atributo en Allplan, puedes agregarlo aquí
# Ejemplo: ATTR_LONGITUD_FIXED_ID = 1234  # Reemplazar con el ID real
ATTR_LONGITUD_FIXED_ID = None  # Cambiar a un número si conoces el ID del atributo

# --- Configuración del label (igual que Tram_recte: un label por atributo, uno debajo del otro) ---
LABEL_PREFIX = ""
LABEL_TEXT_HEIGHT_MM = 0.35
LABEL_TEXT_WIDTH_MM = 0.28
LABEL_TEXT_RATIO = None
LABEL_FONT_NAME = "Arial"
LABEL_FONT_ID = 9
LABEL_TEXT_COLOR = 1
LABEL_FONT_STYLES = 0
LABEL_TEXT_ALIGNMENT = AllplanBasisElements.TextAlignment.eLeftMiddle
LABEL_TEXT_ANGLE_RAD = 0.0
LABEL_IS_SCALE_DEPENDENT = False
LABEL_POSITION = "left"
LABEL_OFFSET_LEFT_MM = 190.0
LABEL_LINE_SPACING_MM = 60
LABEL_NUMERO_PECA_HAS_TEXT_FRAME = False
LABEL_NUMERO_PECA_FRAME_COLOR = 1
LABEL_NUMERO_PECA_FRAME_PEN = None
LABEL_NUMERO_PECA_FRAME_STROKE = None
LABEL_LONGITUD_PREFIX = "L(mm)="
QUIEBRO_DEBUG = str(os.getenv("QUIEBRO_DEBUG", "1")).strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def _read_build_ele_value(build_ele, name, default=None):
    raw = getattr(build_ele, name, None)
    if raw is None:
        return default
    value = getattr(raw, "value", raw)
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value


def _to_float(value, default):
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_int(value, default):
    try:
        return int(round(float(value)))
    except Exception:
        return int(default)


def _to_str(value, default):
    if value is None:
        return str(default)
    return str(value)


def _normalize_quiebro_data_in_place(param: dict) -> None:
    """
    Corrige datos incoherentes de paleta para evitar conflictos geométricos
    (sin compensaciones posteriores en el modelado).
    """
    width = _to_float(param.get("LEN_X", 457.0), 457.0)
    length_mm = _to_float(param.get("LONG. QUIEBRO", CUT_REFERENCE_LENGTH_MM), CUT_REFERENCE_LENGTH_MM)
    cut_length_y = _to_float(param.get("CUT_LENGTH_Y", length_mm), length_mm)
    final_length = max(1.0, min(length_mm, cut_length_y))
    scale_y = final_length / float(CUT_REFERENCE_LENGTH_MM)

    base_raw_input = max(1.0, _to_float(param.get("CUT_BASE_X", 257.0), 257.0))
    base_scaled_input = max(1.0, base_raw_input * scale_y)

    # Mantener el "ancho visual" original: NO tocar caps.
    # En su lugar, forzamos un CUT_BASE_X consistente con la cap de referencia.
    cap_x_big = max(0.0, _to_float(param.get("CAP_ARM_X_BIGGEST", 200.0), 200.0))
    cap_x_small = max(0.0, _to_float(param.get("CAP_ARM_X_SMALLEST", cap_x_big), cap_x_big))
    cap_x_ref = min(cap_x_big, cap_x_small) if cap_x_small > 0 else cap_x_big
    cap_x_ref = max(0.0, min(cap_x_ref, width - 1.0))

    target_base_scaled = max(1.0, width - cap_x_ref)
    safe_scale = max(scale_y, 1e-6)
    target_base_raw = max(1.0, target_base_scaled / safe_scale)

    # Offset consistente del segundo recorte para mantener paralelismo.
    expected_cut_offset_x = width - (2.0 * target_base_scaled)

    param["CUT_BASE_X"] = target_base_raw
    param["CUT_OFFSET_X"] = expected_cut_offset_x

    if QUIEBRO_DEBUG:
        print(
            "[QUIEBRO][NORMALIZE] "
            f"width={width:.3f} final_length={final_length:.3f} "
            f"base_raw_input={base_raw_input:.3f} base_scaled_input={base_scaled_input:.3f} "
            f"cap_x_ref={cap_x_ref:.3f} target_base_scaled={target_base_scaled:.3f} "
            f"target_base_raw={target_base_raw:.3f} cut_offset_x={expected_cut_offset_x:.3f}"
        )


def _numero_peca_label_content(numero_peca):
    """Contenido del label para el número de peça."""
    return f"%RA{numero_peca}%RE".strip()


def _ample_alt_label_content(ample_alt):
    """Contenido del label para ample x alt."""
    return (ample_alt or "").strip()


def _longitud_label_content(longitud):
    """Contenido del label para longitud (con prefijo L(mm)=)."""
    if not (longitud or "").strip():
        return ""
    return f"{LABEL_LONGITUD_PREFIX}{longitud}".strip()


def _desviacio_label_content(desviacio):
    """Contenido del label para el atributo DESVIACIÓ QUIEBRO (con prefijo)."""
    val = (str(desviacio) if desviacio is not None else "").strip()
    if not val:
        return "Des.= -"
    return f"Des.= {val}"


def _resolve_label_font_id():
    """Resuelve el ID de fuente del label por nombre o devuelve LABEL_FONT_ID."""
    if LABEL_FONT_NAME and str(LABEL_FONT_NAME).strip():
        name = str(LABEL_FONT_NAME).strip()
        try:
            if hasattr(AllplanSettings, "FontProvider"):
                provider = AllplanSettings.FontProvider.Instance()
                fid = provider.GetFontID(name, 1)
                if fid is not None and fid > 0:
                    return int(fid)
                ok_names, font_names = provider.GetPredefinedFonts()
                ok_ids, font_ids = provider.GetPredefinedFontIDs()
                if ok_names and ok_ids and name in font_names:
                    idx = font_names.index(name)
                    if idx < len(font_ids):
                        return int(font_ids[idx])
        except Exception as e:
            print(
                f"[Quiebro] Error al resolver el ID de fuente: {LABEL_FONT_NAME} - {e}"
            )
    return LABEL_FONT_ID


class QuiebroModel:
    """Clase que representa el quiebro"""

    # Constantes para la flecha
    FLECHA_FACTOR_LARGO, FLECHA_OFFSET_Z, FLECHA_DIST_ANILLO = 0.7, 0.5, 30.0
    # Tamaño fijo de la flecha (independiente del tamaño del tramo)
    FLECHA_LARGO_FIJO = 140.0  # Longitud fija de la flecha
    FLECHA_ANCHO_FIJO = 60.0  # Ancho fijo de la flecha (x_span * 2)
    FLECHA_ROTATION_ANGLE = 16.0  # Ángulo de rotación de la flecha

    def __init__(
        self,
        build_ele,
        doc: AllplanElementAdapter.DocumentAdapter,
        numero_peca_abs=None,
    ):
        self.doc = doc
        self.build_ele = build_ele

        # 1) Leer el tipo del combobox principal (TypeQuiebro)
        type_quiebro = None
        type_quiebro_raw = getattr(build_ele, "TypeQuiebro", None)
        if type_quiebro_raw is not None:
            type_quiebro_val = getattr(type_quiebro_raw, "value", type_quiebro_raw)
            if type_quiebro_val is not None:
                type_quiebro = str(type_quiebro_val)

        # ✅ NORMALIZAR (para que "Retorn Amb Tapa" cuente como Retorn, etc.)
        if type_quiebro and "Retorn" in type_quiebro:
            type_quiebro = "Retorn"
        elif type_quiebro and "Impulsió" in type_quiebro:
            type_quiebro = "Impulsió"
        else:
            type_quiebro = "Retorn"

        # Seguridad: si no está en PARAMS, usar "Retorn" por defecto
        if type_quiebro not in PARAMS:
            type_quiebro = "Retorn"

        self.type_quiebro = type_quiebro

        # 2) Leer el tamaño del combobox específico del tipo
        idx = 0  # índice por defecto

        # Obtener el nombre del parámetro del combobox según el tipo
        combo_param_name = COMBO_NAME_BY_QUIEBRO.get(self.type_quiebro)
        if combo_param_name:
            combo_raw = getattr(build_ele, combo_param_name, None)
            if combo_raw is not None:
                combo_val = getattr(combo_raw, "value", combo_raw)
                combo_str = str(combo_val) if combo_val is not None else ""

                # Mapear el tamaño (string) a índice usando MAP_QUIEBRO_SIZE
                idx = MAP_QUIEBRO_SIZE.get(combo_str, 0)

        # 3) Proteger por si el índice se va de rango
        params_list = PARAMS.get(self.type_quiebro, PARAMS["Retorn"])
        if idx >= len(params_list):
            idx = len(params_list) - 1
        if idx < 0:
            idx = 0

        # 4) Obtener los parámetros correspondientes
        self.param = dict(params_list[idx])  # Copia para no modificar el original
        self.size_idx = idx

        # 5) Asignar el color de la flecha según el tipo
        arrow_color = ARROW_COLOR_BY_QUIEBRO_TYPE.get(
            self.type_quiebro, 0
        )  # 0 por defecto
        self.param["ARROW_COLOR"] = arrow_color

        prefix = "Ret" if self.type_quiebro == "Retorn" else "Imp"

        # Overrides de paleta: geometría
        self.param["LEN_X"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_WidthX", self.param.get("LEN_X")),
            self.param.get("LEN_X", 457.0),
        )
        self.param["LEN_Y"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_LengthY", self.param.get("LEN_Y")),
            self.param.get("LEN_Y", 1000.0),
        )
        self.param["HEIGHT"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_Height", self.param.get("HEIGHT")),
            self.param.get("HEIGHT", 200.0),
        )
        self.param["DIFX"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_DifX", self.param.get("DIFX")),
            self.param.get("DIFX", 0.0),
        )
        self.param["CAP_ARM_X_BIGGEST"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CapArmXBig", self.param.get("CAP_ARM_X_BIGGEST")
            ),
            self.param.get("CAP_ARM_X_BIGGEST", 200.0),
        )
        self.param["CAP_ARM_Y_BIGGEST"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CapArmYBig", self.param.get("CAP_ARM_Y_BIGGEST")
            ),
            self.param.get("CAP_ARM_Y_BIGGEST", 75.0),
        )
        self.param["CAP_HEIGHT_BIGGEST"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CapHeightBig", self.param.get("CAP_HEIGHT_BIGGEST")
            ),
            self.param.get("CAP_HEIGHT_BIGGEST", 200.0),
        )
        self.param["CAP_ARM_X_SMALLEST"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CapArmXSmall", self.param.get("CAP_ARM_X_SMALLEST")
            ),
            self.param.get("CAP_ARM_X_SMALLEST", 200.0),
        )
        self.param["CAP_ARM_Y_SMALLEST"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CapArmYSmall", self.param.get("CAP_ARM_Y_SMALLEST")
            ),
            self.param.get("CAP_ARM_Y_SMALLEST", 25.0),
        )
        self.param["CAP_HEIGHT_SMALLEST"] = _to_float(
            _read_build_ele_value(
                build_ele,
                f"{prefix}_CapHeightSmall",
                self.param.get("CAP_HEIGHT_SMALLEST"),
            ),
            self.param.get("CAP_HEIGHT_SMALLEST", 199.0),
        )
        self.param["CUT_BASE_X"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_CutBaseX", 257.0),
            257.0,
        )
        self.param["CUT_LENGTH_Y"] = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_CutLengthY", self.param.get("LEN_Y", 1000.0)
            ),
            self.param.get("LEN_Y", 1000.0),
        )
        self.param["CUT_OFFSET_X"] = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_CutOffsetX", -57.0),
            -57.0,
        )

        # Overrides de paleta: flecha
        self.flecha_largo_fijo = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_ArrowLength", self.FLECHA_LARGO_FIJO),
            self.FLECHA_LARGO_FIJO,
        )
        self.flecha_ancho_fijo = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_ArrowWidth", self.FLECHA_ANCHO_FIJO),
            self.FLECHA_ANCHO_FIJO,
        )
        self.flecha_offset_z = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_ArrowZOffset", self.FLECHA_OFFSET_Z),
            self.FLECHA_OFFSET_Z,
        )
        self.flecha_dist_anillo = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_ArrowDistAnillo", self.FLECHA_DIST_ANILLO
            ),
            self.FLECHA_DIST_ANILLO,
        )
        self.flecha_rotation_angle = _to_float(
            _read_build_ele_value(
                build_ele, f"{prefix}_ArrowRotationDeg", self.FLECHA_ROTATION_ANGLE
            ),
            self.FLECHA_ROTATION_ANGLE,
        )
        self.param["ARROW_COLOR"] = _to_int(
            _read_build_ele_value(build_ele, f"{prefix}_ArrowColor", self.param["ARROW_COLOR"]),
            self.param["ARROW_COLOR"],
        )

        # Overrides de paleta: datos/atributos
        self.param["DESVIACIÓ QUIEBRO"] = _to_str(
            _read_build_ele_value(
                build_ele, f"{prefix}_Desviacio", self.param.get("DESVIACIÓ QUIEBRO", "")
            ),
            self.param.get("DESVIACIÓ QUIEBRO", ""),
        )
        self.param["NUMERO PEÇA"] = _to_str(
            _read_build_ele_value(
                build_ele, f"{prefix}_NumeroPeca", self.param.get("NUMERO PEÇA", "")
            ),
            self.param.get("NUMERO PEÇA", ""),
        )
        self.param["TIPUS DE PEÇA"] = _to_str(
            _read_build_ele_value(
                build_ele, f"{prefix}_TipusPeca", self.param.get("TIPUS DE PEÇA", "QUIEBRO")
            ),
            self.param.get("TIPUS DE PEÇA", "QUIEBRO"),
        )

        # Longitud editable en paleta para trabajo manual fuera de polilínea
        palette_length = _to_float(
            _read_build_ele_value(build_ele, f"{prefix}_LengthMm", self.param.get("LEN_Y", 1000)),
            self.param.get("LEN_Y", 1000.0),
        )
        palette_length = max(MIN_LENGTH_MM, min(MAX_LENGTH_MM, palette_length))
        self.custom_length = palette_length
        self.param["LONG. QUIEBRO"] = str(int(palette_length))
        _normalize_quiebro_data_in_place(self.param)
        if QUIEBRO_DEBUG:
            print(
                "[QUIEBRO][INIT] "
                f"type={self.type_quiebro} size_idx={self.size_idx} "
                f"len_mm={self.custom_length:.3f} "
                f"len_x={self.param.get('LEN_X')} len_y={self.param.get('LEN_Y')} "
                f"difx={self.param.get('DIFX')} "
                f"cut_base_x={self.param.get('CUT_BASE_X')} "
                f"cut_length_y={self.param.get('CUT_LENGTH_Y')} "
                f"cut_offset_x={self.param.get('CUT_OFFSET_X')}"
            )

        # 7) Configurar propiedades comunes
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

        # Si viene un número absoluto desde la polilínea, machacamos "NUMERO PEÇA"
        if numero_peca_abs is not None:
            self.param["NUMERO PEÇA"] = str(numero_peca_abs)

    def set_length(self, length_mm: float):
        """
        Permite que la polilínea ajuste el largo del quiebro.
        Cambiamos solo LEN_X o ARM_LEN_X, que es la longitud del quiebro.
        Se limita a [MIN_LENGTH_MM, MAX_LENGTH_MM] (200 mm - 1200 mm).
        """
        try:
            length_mm = float(length_mm)
        except Exception:
            return

        if length_mm <= 0:
            return

        length_mm = max(MIN_LENGTH_MM, min(MAX_LENGTH_MM, length_mm))

        # Actualizar el parámetro correspondiente (puede ser LEN_X o ARM_LEN_X)
        if "LEN_X" in self.param:
            self.param["LEN_X"] = length_mm
        elif "ARM_LEN_X" in self.param:
            self.param["ARM_LEN_X"] = length_mm

        self.custom_length = length_mm
        # Machacar el valor de longitud en param para que atributo y label muestren la longitud real de la polilínea
        self.param["LONG. QUIEBRO"] = str(int(length_mm))

    def _build_arrow(self) -> tuple[AllplanGeometry.Polygon3D, AllplanGeometry.Point3D]:
        """Construye la flecha direccional con tamaño fijo y devuelve el polígono y su centro."""
        # Usar LEN_X solo para centrar la flecha en X
        referencia = float(self.param.get("LEN_X", 200.0))
        altura_tubo = float(self.param.get("LEN_Y", 1150.0))
        altura_flecha = 0.1  # Factor similar a config["altura_flecha"] en el ejemplo

        # Usar tamaño fijo para la flecha (independiente del tamaño del quiebro)
        flecha_largo = float(getattr(self, "flecha_largo_fijo", self.FLECHA_LARGO_FIJO))
        x_span = float(getattr(self, "flecha_ancho_fijo", self.FLECHA_ANCHO_FIJO)) / 2.0

        # z_flecha: posicionar la flecha sobre el tubo (altura del tubo + offset)
        z_flecha = float(self.param.get("HEIGHT", 200.0)) + float(
            getattr(self, "flecha_offset_z", self.FLECHA_OFFSET_Z)
        )

        # Determinar dirección de la flecha según el tipo
        # Retorn → apunta a -Y
        # Impulsió → apunta a +Y
        # La posición es la misma para todos (parte inferior del quiebro)
        type_quiebro = getattr(self, "type_quiebro", "Retorn")
        if "Retorn" in type_quiebro:
            sentido = -1  # Apunta hacia atrás (-Y)
            # Retorn necesita subir 140mm en Y
            offset_y = 140.0
        else:  # Impulsió
            sentido = +1  # Apunta hacia adelante (+Y)
            offset_y = 0.0  # Sin offset para Impulsió

        # Posición fija: siempre en la parte inferior del quiebro
        base_y = float(getattr(self, "flecha_dist_anillo", self.FLECHA_DIST_ANILLO)) + offset_y

        # Centrar la flecha en X usando referencia, pero con tamaño fijo
        x_centro = (referencia * 0.5) + 103.0
        punta_y = base_y + sentido * flecha_largo

        # Calcular el centro de la flecha (aproximadamente en el medio)
        centro_x = x_centro
        centro_y = (base_y + punta_y) / 2.0  # Centro entre base y punta
        centro_z = z_flecha
        centro_flecha = AllplanGeometry.Point3D(centro_x, centro_y, centro_z)

        puntos = [
            AllplanGeometry.Point3D(x_centro - x_span, base_y, z_flecha),
            AllplanGeometry.Point3D(
                x_centro - x_span, punta_y - sentido * x_span * 2, z_flecha
            ),
            AllplanGeometry.Point3D(
                x_centro - x_span * 2, punta_y - sentido * x_span * 2, z_flecha
            ),
            AllplanGeometry.Point3D(x_centro, punta_y, z_flecha),
            AllplanGeometry.Point3D(
                x_centro + x_span * 2, punta_y - sentido * x_span * 2, z_flecha
            ),
            AllplanGeometry.Point3D(
                x_centro + x_span, punta_y - sentido * x_span * 2, z_flecha
            ),
            AllplanGeometry.Point3D(x_centro + x_span, base_y, z_flecha),
        ]
        puntos.append(puntos[0])  # Cerrar polígono
        return AllplanGeometry.Polygon3D(puntos), centro_flecha

    def _add_attributes(self, attr_list):
        """Agrega atributos según el tipo de quiebro."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_ample_id = AttributeService.GetAttributeID(self.doc, "AMPLE")

            # Intentar diferentes variaciones del nombre del atributo LONGITUD
            attr_longitud_id = AttributeService.GetAttributeID(
                self.doc, "LONG. QUIEBRO"
            )
            # Si no se encuentra, usar ID fijo si está definido
            if attr_longitud_id <= 0 and ATTR_LONGITUD_FIXED_ID is not None:
                attr_longitud_id = ATTR_LONGITUD_FIXED_ID

            attr_numero_peca_id = AttributeService.GetAttributeID(
                self.doc, "NUMERO PEÇA"
            )
            attr_tipus_peca_id = AttributeService.GetAttributeID(
                self.doc, "TIPUS DE PEÇA"
            )
            attr_desviacio_id = AttributeService.GetAttributeID(
                self.doc, "DESVIACIÓ QUIEBRO"
            )
            attr_alt_id = AttributeService.GetAttributeID(self.doc, "ALT")

            # AMPLE: leer del diccionario de parámetros o calcular desde LEN_X
            if attr_ample_id and attr_ample_id > 0:
                ample_value = self.param.get("AMPLE")
                if ample_value is None:
                    # Si no está en el diccionario, calcular desde LEN_X
                    ample_value = str(int(self.param.get("LEN_X", 0)))
                else:
                    ample_value = str(ample_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_ample_id, ample_value)
                )

            # LONG. QUIEBRO: leer de self.param (está en PARAMS_BASE)
            # Prioridad: 1) custom_length, 2) valor de PARAMS_BASE, 3) calcular desde LEN_Y
            if attr_longitud_id and attr_longitud_id > 0:
                length = getattr(self, "custom_length", None)
                if length is not None:
                    # Si hay longitud personalizada, usar esa
                    longitud_value = str(int(length))
                else:
                    # Leer directamente de self.param (ya está en PARAMS_BASE)
                    longitud_value = self.param.get("LONG. QUIEBRO")

                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_longitud_id, longitud_value
                    )
                )

            # NUMERO PEÇA: leer del diccionario o calcular dinámicamente
            if attr_numero_peca_id and attr_numero_peca_id > 0:
                numero_peca_value = self.param.get("NUMERO PEÇA")
                if numero_peca_value is None or numero_peca_value == "":
                    # Si no está en el diccionario o está vacío, calcular dinámicamente
                    size_keys = list(MAP_QUIEBRO_SIZE.keys())
                    size_str = (
                        size_keys[self.size_idx]
                        if self.size_idx < len(size_keys)
                        else ""
                    )
                    numero_peca_value = f"{self.type_quiebro}_{size_str}"
                else:
                    numero_peca_value = str(numero_peca_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_numero_peca_id, numero_peca_value
                    )
                )

            # TIPUS DE PEÇA: leer del diccionario de parámetros
            if attr_tipus_peca_id and attr_tipus_peca_id > 0:
                tipus_peca_value = self.param.get("TIPUS DE PEÇA")
                if tipus_peca_value is None:
                    # Si no está en el diccionario, usar el tipo de tramo
                    tipus_peca_value = self.type_quiebro
                else:
                    tipus_peca_value = str(tipus_peca_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_tipus_peca_id, tipus_peca_value
                    )
                )

            # DESVIACIÓ QUIEBRO: leer del diccionario de parámetros
            if attr_desviacio_id and attr_desviacio_id > 0:
                desviacio_value = self.param.get("DESVIACIÓ QUIEBRO", "")
                if desviacio_value is None:
                    desviacio_value = ""
                else:
                    desviacio_value = str(desviacio_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_desviacio_id, desviacio_value
                    )
                )

            # ALT: leer del diccionario de parámetros o calcular desde HEIGHT
            if attr_alt_id and attr_alt_id > 0:
                alt_value = self.param.get("ALT")
                if alt_value is None:
                    # Si no está en el diccionario, calcular desde HEIGHT
                    alt_value = str(int(self.param.get("HEIGHT", 0)))
                else:
                    alt_value = str(alt_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_alt_id, alt_value)
                )

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Quiebro] Advertencia al agregar atributos: {e}")
            import traceback

    def _create_label_for_element(self):
        """
        Crea un LabelElement por cada atributo (numero_peca, ample_alt, longitud, desviacio),
        posicionados uno debajo del otro, igual que en Tram_recte.
        """
        try:
            ample = self.param.get("AMPLE", "")
            alt = self.param.get("ALT", "")
            longitud = self.param.get("LONG. QUIEBRO", "")
            numero_peca = self.param.get("NUMERO PEÇA", "")
            desviacio = self.param.get("DESVIACIÓ QUIEBRO", "")
            ample_alt = f"{ample} x {alt}" if (ample or alt) else ""
            numero_peca_str = str(numero_peca) if numero_peca is not None else ""

            contents = [
                _numero_peca_label_content(numero_peca_str),
                _ample_alt_label_content(ample_alt),
                _longitud_label_content(longitud),
                _desviacio_label_content(desviacio),
            ]
            if not any(contents):
                return []

            if LABEL_POSITION == "left":
                half_x = (
                    getattr(self, "custom_length", None)
                    or float(self.param.get("LEN_X", 457.0))
                ) / 2.0
                x_label = -half_x + float(LABEL_OFFSET_LEFT_MM)
            else:
                x_label = 0.0

            height_mm = LABEL_TEXT_HEIGHT_MM
            if LABEL_TEXT_RATIO and LABEL_TEXT_RATIO > 0:
                width_mm = height_mm / LABEL_TEXT_RATIO
            else:
                width_mm = LABEL_TEXT_WIDTH_MM
            line_height = height_mm + float(LABEL_LINE_SPACING_MM)

            text_props = AllplanBasisElements.TextProperties()
            text_props.Height = height_mm
            text_props.Width = width_mm
            text_props.Font = _resolve_label_font_id()
            text_props.FontStyles = LABEL_FONT_STYLES
            if LABEL_TEXT_ALIGNMENT is not None:
                text_props.Alignment = LABEL_TEXT_ALIGNMENT
            text_props.IsScaleDependent = LABEL_IS_SCALE_DEPENDENT
            if LABEL_TEXT_ANGLE_RAD != 0.0:
                text_props.TextAngle = AllplanGeometry.Angle(LABEL_TEXT_ANGLE_RAD)

            label_common_props = AllplanBaseElements.CommonProperties()
            label_common_props.GetGlobalProperties()
            label_common_props.Color = int(LABEL_TEXT_COLOR)
            label_common_props.ColorByLayer = False

            label_elems = []
            for i, text_str in enumerate(contents):
                if not text_str:
                    continue
                tp = AllplanBasisElements.TextProperties(text_props)
                if i == 0 and LABEL_NUMERO_PECA_HAS_TEXT_FRAME:
                    tp.HasTextFrame = True
                    if LABEL_NUMERO_PECA_FRAME_COLOR is not None:
                        tp.TextFrameColor = int(LABEL_NUMERO_PECA_FRAME_COLOR)
                    if LABEL_NUMERO_PECA_FRAME_PEN is not None:
                        tp.TextFramePen = int(LABEL_NUMERO_PECA_FRAME_PEN)
                    if LABEL_NUMERO_PECA_FRAME_STROKE is not None:
                        tp.TextFrameStroke = int(LABEL_NUMERO_PECA_FRAME_STROKE)
                y_label = -i * line_height
                point_label = AllplanGeometry.Point2D(x_label, y_label)
                text_elem = AllplanBasisElements.TextElement(
                    label_common_props, tp, text_str, point_label
                )
                label_elem = AllplanBasisElements.LabelElement(
                    text_elem, AllplanBasisElements.LabelType.eLabelNormalText
                )
                label_elems.append(label_elem)

            return label_elems
        except Exception as e:
            print(f"[Quiebro] Advertencia al crear labels: {e}")
            return []

    def create_rhomboid_brep(self, param: dict):
        """
        Crea un BRep romboide.

        Paso1: Creo un rectangulo base con los parametros del param
        Paso2: Creo un Triangulo rectangulo para luego aplicar MakeSubtraction
        Paso3: Aplico MakeSubtraction para obtener el BRep romboide
        Paso4: Creo los rectangulos superiores e inferiores para luego aplicar MakeUnion
        Paso5: Creo las caps para luego aplicar MakeUnion
        Paso6: Devuelvo el BRep romboide
        """

        # Uso el largo real si está disponible en build_ele
        length = getattr(self, "custom_length", None)
        if length is None:
            # Algunos parámetros usan LEN_X, otros ARM_LEN_X
            length = float(param.get("LEN_Y"))

        # El recorte diagonal en Y debe achicar el quiebro completo sin deformar:
        # al reducirlo, mantenemos el ángulo de inclinación escalando la base en X.
        cut_length_y = max(1.0, float(param.get("CUT_LENGTH_Y", length)))
        length = min(float(length), cut_length_y)
        self.custom_length = length
        self.param["LONG. QUIEBRO"] = str(int(length))

        width = float(param["LEN_X"])
        height = float(param["HEIGHT"])

        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # Crear el brep principal
        brep = AllplanGeometry.BRep3D.CreateCuboid(placement, width, length, height)

        # Paso2: Creo un Triangulo rectangulo para luego aplicar MakeSubtraction
        base_raw = max(1.0, float(param.get("CUT_BASE_X", 257.0)))
        scale_y = float(length) / float(CUT_REFERENCE_LENGTH_MM)
        base_triangulo = max(1.0, base_raw * scale_y)
        altura_triangulo = max(1.0, float(length))
        altura_triangulo_z = float(height)
        if QUIEBRO_DEBUG:
            print(
                "[QUIEBRO][CUT] "
                f"length_input={param.get('LEN_Y')} custom_length={getattr(self, 'custom_length', None)} "
                f"cut_length_y={cut_length_y:.3f} final_length={length:.3f} "
                f"base_raw={base_raw:.3f} scale_y={scale_y:.6f} "
                f"base_scaled={base_triangulo:.3f} "
                f"height_z={altura_triangulo_z:.3f}"
            )

        # Defino los puntos de la base del triangulo en el plano XY
        p0 = AllplanGeometry.Point3D(0, 0, 0)
        p1 = AllplanGeometry.Point3D(base_triangulo, 0, 0)
        p2 = AllplanGeometry.Point3D(0, altura_triangulo, 0)

        profile = AllplanGeometry.Path3D()
        profile += AllplanGeometry.Line3D(p0, p1)
        profile += AllplanGeometry.Line3D(p1, p2)
        profile += AllplanGeometry.Line3D(p2, p0)

        profiles = [profile]

        path = AllplanGeometry.Line3D(
            AllplanGeometry.Point3D(0, 0, 0),
            AllplanGeometry.Point3D(0, 0, altura_triangulo_z),
        )

        axis = AllplanGeometry.Vector3D(0.0, 0.0, 1.0)
        err, triangulo1 = AllplanGeometry.CreateSweptBRep3D(
            profiles,
            path,
            True,
            True,
            axis,
            1,
        )
        if err != 0:
            raise Exception(f"Error en CreateSweptBRep3D(triangulo1): código {err}")

        # Paso3: Aplico MakeSubtraction para obtener el BRep romboide
        err, semifinal_brep = AllplanGeometry.MakeSubtraction(brep, triangulo1)
        if err != 0:
            raise Exception(f"Error en MakeSubtraction(brep, triangulo1): código {err}")

        err, triangulo2 = AllplanGeometry.CreateSweptBRep3D(
            profiles,
            path,
            True,
            True,
            axis,
            1,
        )
        if err != 0:
            raise Exception(f"Error en CreateSweptBRep3D(triangulo2): código {err}")

        # Rotar triangulo2 180 grados sobre el eje Z, usando p1 como punto de referencia
        import math

        # El punto de referencia es p1, pero en 3D (con Z en el centro de la extrusión)
        centro_x = p1.X  # base_triangulo
        centro_y = p1.Y  # 0
        centro_z = altura_triangulo_z / 2.0  # Centro de la extrusión en Z

        # Crear el eje de rotación (eje Z vertical) que pasa por p1
        rotation_axis = AllplanGeometry.Line3D(
            AllplanGeometry.Point3D(centro_x, centro_y, 0),
            AllplanGeometry.Point3D(centro_x, centro_y, 1),
        )

        # Crear la matriz de rotación
        rotation_matrix = AllplanGeometry.Matrix3D()
        rotation_matrix.SetRotation(
            rotation_axis, AllplanGeometry.Angle(math.pi)
        )  # 180 grados = π radianes

        # Aplicar la rotación al triangulo2
        triangulo2 = AllplanGeometry.Transform(triangulo2, rotation_matrix)

        # Posicionar triangulo2 en Y = +500mm
        translation_matrix = AllplanGeometry.Matrix3D()
        cut_offset_x_scaled = float(param.get("CUT_OFFSET_X", -57.0))
        translation_vec = AllplanGeometry.Vector3D(
            cut_offset_x_scaled - float(param["DIFX"]),
            altura_triangulo,
            0,
        )
        if QUIEBRO_DEBUG:
            print(
                "[QUIEBRO][CUT2] "
                f"cut_offset_scaled={cut_offset_x_scaled:.3f} "
                f"difx={float(param['DIFX']):.3f} "
                f"translation=({translation_vec.X:.3f},{translation_vec.Y:.3f},{translation_vec.Z:.3f}) "
                f"tri_base={base_triangulo:.3f} tri_len={altura_triangulo:.3f}"
            )
        translation_matrix.SetTranslation(
            translation_vec
        )
        triangulo2 = AllplanGeometry.Transform(triangulo2, translation_matrix)

        # Paso3: Aplico MakeSubtraction para obtener el BRep romboide
        err, final_brep_inner = AllplanGeometry.MakeSubtraction(
            semifinal_brep, triangulo2
        )
        if err != 0:
            raise Exception(f"Error en MakeSubtraction(brep, triangulo): código {err}")

        # Paso4: Creo los rectangulos superiores e inferiores para luego aplicar MakeUnion
        # Agregar las caps si están definidas y tienen valores válidos
        cap_arm_x_biggest = float(param.get("CAP_ARM_X_BIGGEST", 0.0))
        cap_arm_y_biggest = float(param.get("CAP_ARM_Y_BIGGEST", 0.0))
        cap_height_biggest = float(param.get("CAP_HEIGHT_BIGGEST", 0.0))

        if cap_arm_x_biggest > 0 and cap_arm_y_biggest > 0 and cap_height_biggest > 0:
            # Centrar las caps en X y Z
            # En X: centrar respecto al largo del tubo
            cap_x_offset = base_triangulo
            # En Z: centrar respecto a la altura del tubo
            cap_z_offset = (height - cap_height_biggest) / 2.0

            # Cap 1: en el extremo negativo de Y (inicio del tubo)
            cap1_origin = AllplanGeometry.Point3D(
                cap_x_offset, -cap_arm_y_biggest, cap_z_offset
            )
            cap1_placement = AllplanGeometry.AxisPlacement3D(cap1_origin)
            cap1_brep = AllplanGeometry.BRep3D.CreateCuboid(
                cap1_placement, cap_arm_x_biggest, cap_arm_y_biggest, cap_height_biggest
            )

            # Unir cap1 con el brep principal
            err, final_brep_inner1 = AllplanGeometry.MakeUnion(
                final_brep_inner, cap1_brep
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(final_brep_inner, cap1): código {err}"
                )
            # Cap 2: en el extremo positivo de Y (final del tubo)
            cap2_origin = AllplanGeometry.Point3D(0, length, cap_z_offset)
            cap2_placement = AllplanGeometry.AxisPlacement3D(cap2_origin)
            cap2_brep = AllplanGeometry.BRep3D.CreateCuboid(
                cap2_placement, cap_arm_x_biggest, cap_arm_y_biggest, cap_height_biggest
            )
            # Unir cap2 con el brep principal
            err, final_brep_inner2 = AllplanGeometry.MakeUnion(
                final_brep_inner1, cap2_brep
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(final_brep_inner1, cap2): código {err}"
                )

        # Paso5: Creo las caps para luego aplicar MakeUnion
        # Agregar las caps si están definidas y tienen valores válidos
        cap_arm_x_smallest = float(param.get("CAP_ARM_X_SMALLEST", 0.0))
        cap_arm_y_smallest = float(param.get("CAP_ARM_Y_SMALLEST", 0.0))
        cap_height_smallest = float(param.get("CAP_HEIGHT_SMALLEST", 0.0))
        if QUIEBRO_DEBUG:
            print(
                "[QUIEBRO][CAPS] "
                f"cap_x_big={cap_arm_x_biggest:.3f} "
                f"cap_x_small={cap_arm_x_smallest:.3f} "
                f"width={width:.3f} base_scaled={base_triangulo:.3f} "
                f"expected_cap_x={max(0.0, width - base_triangulo):.3f}"
            )

        if (
            cap_arm_x_smallest > 0
            and cap_arm_y_smallest > 0
            and cap_height_smallest > 0
        ):
            # Centrar las caps en X y Z
            # En X: centrar respecto al largo del tubo
            cap_x_offset_smallest = base_triangulo
            # En Z: centrar respecto a la altura del tubo
            cap_z_offset_smallest = (height - cap_height_smallest) / 2.0

            # Cap 1: en el extremo negativo de Y (inicio del tubo)
            cap1_origin_smallest = AllplanGeometry.Point3D(
                cap_x_offset_smallest,
                (-cap_arm_y_biggest - cap_arm_y_smallest),
                cap_z_offset_smallest,
            )
            cap1_placement_smallest = AllplanGeometry.AxisPlacement3D(
                cap1_origin_smallest
            )
            cap1_brep_smallest = AllplanGeometry.BRep3D.CreateCuboid(
                cap1_placement_smallest,
                cap_arm_x_smallest,
                cap_arm_y_smallest,
                cap_height_smallest,
            )

            # Unir cap1_smallest con el brep principal
            err, final_brep_semifinal = AllplanGeometry.MakeUnion(
                final_brep_inner2, cap1_brep_smallest
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(final_brep_inner2, cap1_smallest): código {err}"
                )
            # Cap 2: en el extremo positivo de Y (final del tubo)
            cap2_origin_smallest = AllplanGeometry.Point3D(
                0,
                (length + cap_arm_y_biggest),
                cap_z_offset_smallest,
            )
            cap2_placement_smallest = AllplanGeometry.AxisPlacement3D(
                cap2_origin_smallest
            )
            cap2_brep_smallest = AllplanGeometry.BRep3D.CreateCuboid(
                cap2_placement_smallest,
                cap_arm_x_smallest,
                cap_arm_y_smallest,
                cap_height_smallest,
            )
            # Unir cap2_smallest con el brep principal
            err, final_brep_final = AllplanGeometry.MakeUnion(
                final_brep_semifinal, cap2_brep_smallest
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(final_brep_semifinal, cap2_smallest): código {err}"
                )

        return final_brep_final

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        brep = self.create_rhomboid_brep(self.param)
        flecha_poly, centro_flecha = self._build_arrow()

        # Aplicar rotación FLECHA_ROTATION_ANGLE a la flecha

        # Crear el eje de rotación (eje Z vertical) que pasa por el centro de la flecha
        rotation_axis = AllplanGeometry.Line3D(
            centro_flecha,
            AllplanGeometry.Point3D(
                centro_flecha.X, centro_flecha.Y, centro_flecha.Z + 1.0
            ),
        )

        # Crear la matriz de rotación
        rotation_matrix = AllplanGeometry.Matrix3D()
        angle_rad = math.radians(
            float(getattr(self, "flecha_rotation_angle", self.FLECHA_ROTATION_ANGLE))
        )
        rotation_matrix.SetRotation(rotation_axis, AllplanGeometry.Angle(angle_rad))

        # Aplicar la rotación a la flecha
        flecha_poly = AllplanGeometry.Transform(flecha_poly, rotation_matrix)

        #  CENTRO EL TUBO SOBRE EL EJE DE LA POLILÍNEA
        # Usar el largo correcto (puede ser custom_length o el del parámetro)
        length = getattr(self, "custom_length", None)
        if length is None:
            length = float(self.param.get("LEN_X", self.param.get("ARM_LEN_X", 200.0)))

        half_x = length / 2.0
        half_y = float(self.param["LEN_Y"]) / 2.0
        half_z = float(self.param["HEIGHT"]) / 2.0

        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-half_x, -half_y, -half_z))

        brep_centered = AllplanGeometry.Transform(brep, mat_center)
        flecha_poly_centered = AllplanGeometry.Transform(flecha_poly, mat_center)

        # Crear ModelElement3D para el tubo
        model_ele = AllplanBasisElements.ModelElement3D(
            self.common_props, brep_centered
        )

        # Agregar atributos al elemento principal
        if self.doc:
            attr_list = []
            self._add_attributes(attr_list)
            if attr_list:
                attr_set_list = []
                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                attributes = AllplanBaseElements.Attributes(attr_set_list)
                model_ele.SetAttributes(attributes)

        # Labels por atributo (numero_peca, ample_alt, longitud, desviacio), uno debajo del otro
        label_elems = self._create_label_for_element()
        if label_elems:
            try:
                model_ele.SetLabelElements(label_elems)
            except AttributeError:
                try:
                    model_ele.LabelElements = label_elems
                except Exception:
                    pass

        # Configurar propiedades para la flecha con su color específico (igual que en el ejemplo)
        arrow_color = int(self.param.get("ARROW_COLOR", 0))
        flecha_props = AllplanBaseElements.CommonProperties()
        flecha_props.GetGlobalProperties()
        flecha_props.Color = arrow_color
        flecha_props.ColorByLayer = False

        flecha_ele = AllplanBasisElements.ModelElement3D(
            flecha_props, flecha_poly_centered
        )

        return [model_ele, flecha_ele]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Metodo que crea el elemento final."""
    quiebro = QuiebroModel(build_ele, doc)
    model_list = quiebro.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
