# -*- coding: utf-8 -*-
from Instalaciones.PolyLib.installation_registry import register_installation
from Instalaciones.PolyLib.models import ElementTypes

ANGLES_45 = [0, 45, 90, 135, 180, 225, 270, 315]
ANGLES_90 = [0, 90, 180, 270]


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
        "roles": [0, 3],
        "module_path": f"pyp-scripts.{key}_script",  # Prefijo pyp-scripts por defecto
        "pythonpart": f"{class_name}Script",
        "dinamic": dynamic,
        "attrs_default": [],
        "attrs_custom": [],
        "layers": {},
    }
    if diameter:
        el["diameter"] = diameter
    return el


INSTALLATION_INFO = {
    "name": "AGUA",
    "label": "Instalación de Agua",
    "angles": [],
    "angles_read": "Libre (ángulo interior >= 45°)",
    "default_layers": {
        "default": "KN_AIGUA_FAB",
        "layer_polyline": "IS_CON_VENT_EIX",
    },
    "layers": [
        {"key": "KN_XPS_RECESS", "label": "XPS RECESS"},
        {"key": "KN_AIGUA", "label": "AIGUA"},
        {"key": "KN_XPS_CAVITAT", "label": "XPS CAVITAT"},
        {"key": "KN_PLD_RECESS", "label": "KN PLD RECESS"},
        {"key": "IS_CON_AIGUA_FAB", "label": "IS CON AIGUA FAB"},
    ],
    "installation_types": [
        {
            "key": "polietile",
            "label": "Polietilè",
            "is_individual": True,
            "min_segment_length": 350,
            "angles": ANGLES_90,
            "color": 19,
            "diameter": [20, 25],
            "allowed_angles": "Solo 90 grados",
            "elems": ["codo_90", "conexion", "reduccion"],
            "connections": [
                ElementTypes.UNION,
                ElementTypes.CODO,
                ElementTypes.REDUCION,
                ElementTypes.BIFURCACION,
            ],
        },
        {
            "key": "multicapa",
            "label": "Multicapa",
            "is_individual": True,
            "min_segment_length": 350,
            "angles": ANGLES_90,
            "color": 19,
            "diameter": [20, 25],
            "allowed_angles": "Solo 90 grados",
            "elems": ["codo_90", "conexion", "reduccion"],
            "connections": [
                ElementTypes.UNION,
                ElementTypes.CODO,
                ElementTypes.REDUCION,
                ElementTypes.BIFURCACION,
            ],
        },
        {
            "key": "armaflex",
            "label": "Armaflex",
            "is_individual": True,
            "min_segment_length": 350,
            "angles": ANGLES_90,
            "color": 19,
            "diameter": [20, 25],
            "allowed_angles": "Solo 90 grados",
            "elems": ["codo_90", "conexion", "reduccion"],
            "connections": [
                ElementTypes.UNION,
                ElementTypes.CODO,
                ElementTypes.REDUCION,
                ElementTypes.BIFURCACION,
            ],
        },
    ],
    "elements3D": [
        create_element("polietile", "Polietilè", dynamic=True),
        create_element("multicapa", "Multicapa", dynamic=True),
        create_element("armaflex", "Armaflex", dynamic=True),
        create_element("manguito", "Manguito"),
        create_element("codo", "Codo"),
        create_element("te", "Te"),
        create_element("colze_base", "Colze Base"),
        create_element("clau_de_pas", "Clau de Pas"),
        create_element("taps", "Taps"),
        create_element("te_sortida", "Te Sortida"),
    ],
    "summary": {
        k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]
    },
}


def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)
