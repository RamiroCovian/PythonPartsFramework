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
        "module_path": f"pyp-scripts.{key}_script", # Prefijo pyp-scripts por defecto
        "pythonpart": f"{class_name}Script",
    }
    return el

INSTALLATION_INFO = {
    "name": "VENTILACION",
    "label": "Instalación de Ventilación",
    "angles": [0, 45, -45, 90, -90],
    "angles_read": "45 - 90 grados",
    "default_layers" : {
        "default": "IS_CON_VENT_FAB",
        "layer_polyline": "IS_CON_VENT_EIX",
        "layer_cuboid_label": "IS_NOM_CONDUCTE_VENTILACIO",
    },
    "layers": [
        {"key": "IS_CON_VENT_FAB", "label": "VENTILACIO FABRICA"},
        {"key": "IS_CON_VENT_FAB_SOB1", "label": "VENTILACIO FABRICA SOBRANT"},
        {"key": "IS_CON_VENT_OBRA", "label": "VENTILACIO OBRA"},
        {"key": "IS_CON_VENT_EIX", "label": "VENTILACIO EIX"},
    ],
    "installation_types": [
        {
            "key": "conducto_normal",
            "label": "Conducto Impulsion",
            "is_individual": False, "min_segment_length": 300,
            "angles": ANGLES_45, "color": 5, "diameter": 75, "allowed_angles": "45 - 90 grados",
            "elems": ["manguito", "difusor"], "connections": [ElementTypes.UNION]
        },
        {
            "key": "conducto_normal",
            "label": "Conducto Extraccion",
            "is_individual": False, "min_segment_length": 300,
            "angles": ANGLES_45, "color": 15, "diameter": 75, "allowed_angles": "45 - 90 grados",
            "elems": ["manguito", "difusor"], "connections": [ElementTypes.UNION]
        },
        {
            "key": "conducto_aislado",
            "label": f"Conducto Aislado", "min_segment_length": 300,
            "is_individual": False, "allowed_angles": "45 - 90 grados",
            "angles": ANGLES_45, "color": 19, "diameter": [150, 160],
            "elems": [], "connections": [ElementTypes.REDUCION]
        },
        {
            "key": "conducto_recuperador",
            "label": "Conducto Recuperador",
            "is_individual": True, "min_segment_length": 350,
            "angles": ANGLES_90, "color": 19, "diameter": 160, "allowed_angles": "Solo 90 grados",
            "elems": ["codo_90", "conexion"], "connections": [ElementTypes.UNION, ElementTypes.CODO]
        },
    ],
    "elements3D": [
        create_element("conducto_normal", "Conducto Impulsion", dynamic=True),
        create_element("conducto_normal", "Conducto Extraccion", dynamic=True),
        create_element("manguito", "Manguito"),
        create_element("difusor", "Difusor"),
        create_element("conducto_aislado", "Conducto Aislado", dynamic=True),
        # create_element("conducto_aislado", "Conducto Aislado 160 mm", dynamic=True, diameter=160),
        create_element("conducto_recuperador", "Conducto recuperador"),
        create_element("conexion", "Conexion"),
        create_element("codo_90", "Codo 90"),
    ],
    "summary": {k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]},
}

def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)