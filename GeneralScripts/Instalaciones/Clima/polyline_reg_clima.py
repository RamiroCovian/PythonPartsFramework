# -*- coding: utf-8 -*-
import importlib

from Instalaciones.PolyLib.installation_registry import register_installation, register_pythonpart
from Instalaciones.PolyLib.models import ElementTypes

ANGLES_45 = [0, 45, 90, 135, 180, 225, 270, 315]
ANGLES_90 = [0, 90, 180, 270]


def _build_allowed_relative_turns():
    """
    Giros relativos permitidos respecto al segmento anterior.
    Rango fino: -45° .. +45° (incluye 0°), resolución 1°.
    Se mantienen además giros rectos ±90° para compatibilidad con el flujo previo.
    """
    out = {float(a) for a in range(-45, 46)}
    out.update({-90.0, 90.0})
    return sorted(out)


ALLOWED_RELATIVE_TURNS = _build_allowed_relative_turns()
ALLOWED_RELATIVE_TURNS_READ = "|".join(
    str(int(a)) if float(a).is_integer() else str(a)
    for a in ALLOWED_RELATIVE_TURNS
)


def create_element(key, label, dynamic=False, diameter=None):
    """
    Genera automáticamente la estructura del elemento.
    Convierte 'conducto_normal' en 'ConductoNormalScript' de forma automática.
    """
    # Convierte snake_case a PascalCase para la clase de Python
    class_name = "".join(word.capitalize() for word in key.split("_"))
    el = {
        "key": key,
        "label": label,
        "roles": [0, 3], # Incluidos por defecto
        "module_path": f"pyp-scripts.{key}_script", # Prefijo pyp-scripts por defecto
        "pythonpart": f"{class_name}Script",
        "dinamic": dynamic,
        "attrs_default": [],
        "attrs_custom": [],
        "layers": {},
    }
    if diameter: el["diameter"] = diameter
    return el

INSTALLATION_INFO = {
    "name": "CLIMA",
    "label": "Instalación de Clima",
    # Giros relativos en planta respecto al tramo previo: -45°..+45°.
    "angles": ALLOWED_RELATIVE_TURNS,
    "angles_read": ALLOWED_RELATIVE_TURNS_READ,
    "default_layers" : {
        "default": " ",
        "layer_polyline": " ",
        "layer_cuboid_label": " ",
    },
    "layers": [
        {"key": "IS_CON_VENT_FAB", "label": "VENTILACIO FABRICA"},
        {"key": "IS_CON_VENT_FAB_SOB1", "label": "VENTILACIO FABRICA SOBRANT"},
        {"key": "IS_CON_VENT_OBRA", "label": "VENTILACIO OBRA"},
        {"key": "IS_CON_VENT_EIX", "label": "VENTILACIO EIX"},
    ],
    "installation_types": [
        {
            "key": "tram_recte",
            "label": "Impulsió",
            "is_individual": True,
            "angles": ALLOWED_RELATIVE_TURNS,
            "allowed_angles": ALLOWED_RELATIVE_TURNS_READ,
            # Longitud mínima del segmento (mm), igual que Saneamiento
            "min_segment_length": 600,
            "color": 19,
            "diameter": ["150x150", "200x150", "250x150", "300x150", "350x150", "400x150", "450x150", "500x150", "550x150", "600x150", "650x150", "700x150", "750x150"],
            # REDUCION nativa de PolyLib desactivada para Clima:
            # trabaja con diámetros numéricos y rompe preview/selección con claves "350x150".
            # El reductor no va en el combo: paleta «Aplicar reductor» (evento 1039) en clima_polyline.
            "elems": ["codo_90", "conexion"], "connections": [ElementTypes.CODO, ElementTypes.BIFURCACION],
        },
        {
            "key": "tram_recte",
            "label": "Retorn",
            "is_individual": True,
            "angles": ALLOWED_RELATIVE_TURNS,
            "allowed_angles": ALLOWED_RELATIVE_TURNS_READ,
            # Longitud mínima del segmento (mm), igual que Saneamiento
            "min_segment_length": 600,
            "color": 5,
            "diameter": ["150x150", "200x150", "250x150", "300x150", "350x150", "400x150", "450x150", "500x150", "550x150", "600x150", "650x150", "700x150", "750x150"],
            # REDUCION nativa de PolyLib desactivada para Clima (ver explicación arriba).
            "elems": ["codo_90", "conexion"], "connections": [ElementTypes.CODO, ElementTypes.BIFURCACION],
        },
    ],
    "elements3D": [
        create_element("tram_recte", "Tram recte", dynamic=True),
        create_element("colze", "Colze"),
        create_element("quiebro", "Quiebro"),
    ],
    "summary": {k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]},
}

def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)

    # Forzar registro de tram_recte: `register_installation` ignora errores de import
    # y, si falla, el elemento queda sin registrar (get_pythonpart -> None).
    try:
        mod = importlib.import_module(f"{import_base}.pyp-scripts.tram_recte_script")
        cls = getattr(mod, "TramRecteScript")
        register_pythonpart("tram_recte", cls)
    except Exception:
        pass
    try:
        mod = importlib.import_module(f"{import_base}.pyp-scripts.colze_script")
        cls = getattr(mod, "ColzeScript")
        register_pythonpart("colze", cls)
    except Exception:
        pass
    try:
        mod = importlib.import_module(f"{import_base}.pyp-scripts.quiebro2")
        cls = getattr(mod, "Quiebro2Script")
        register_pythonpart("quiebro", cls)
    except Exception:
        pass
    try:
        mod = importlib.import_module(f"{import_base}.pyp-scripts.reduccions")
        cls = getattr(mod, "ReduccionsScript")
        register_pythonpart("reduccions", cls)
    except Exception:
        pass