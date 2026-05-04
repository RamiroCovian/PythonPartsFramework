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
        "module_path": f"pyp-scripts.{key}_script",  # Prefijo pyp-scripts por defecto
        "pythonpart": f"{class_name}Script",
    }
    return el


INSTALLATION_INFO = {
    "name": "SANEAMIENTO",
    "label": "Instalación Saneamiento",
    "angles": ANGLES_45,
    "angles_read": "45 - 90 grados",
    "default_layers": {
        "default": "IS_CON_SANE_FAB",
    },
    "layers": [
        {"key": "IS_CON_SANE_FAB", "label": "IS CON SANE FAB"},
        {"key": "IS_CON_SANE_OBR", "label": "IS CON SANE OBR"},
        {"key": "KN_X_AIGUA", "label": "KN X AIGUA"},
        {"key": "KN_Y_AIGUA", "label": "KN Y AIGUA"},
        {"key": "KN_AIGUA", "label": "KN AIGUA"},
    ],
    "installation_types": [
        {
            "key": "tub_pvc_tricapa_v",
            "label": "Pluvial",
            "is_individual": True,
            "min_segment_length": 350,
            "angles": ANGLES_45,
            "color": 19,
            "diameter": [110],
            "allowed_angles": "45 - 90 grados",
            "elems": ["codo_90", "conexion", "reduccion"],
            "connections": [
                ElementTypes.UNION,
                ElementTypes.CODO,
                ElementTypes.REDUCION,
                ElementTypes.BIFURCACION,
            ],
        },
        {
            "key": "tub_pvc_tricapa",
            "label": "Fecal",
            "is_individual": True,
            "min_segment_length": 350,
            "angles": ANGLES_45,
            "color": 19,
            "diameter": [25, 40, 110],
            "allowed_angles": "45 - 90 grados",
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
        # Solo Fecal Ø25 (no aparece en el combo; lo usa saneamiento_polyline con diámetro 25)
        create_element("tub_pvc_basic_f_25", "Tubo PVC fecal Ø25", dynamic=True),
        create_element("tub_pvc_tricapa_f_40", "Tubo PVC tricapa fecal Ø40", dynamic=True),
        create_element("tub_pvc_tricapa_p_110", "Tubo PVC tricapa Pluvial Ø110", dynamic=True),
        create_element("tub_pvc_tricapa_f_110", "Tubo PVC tricapa Fecal Ø110", dynamic=True),
        create_element("tub_pvc_tricapa_v", "Tubo PVC tricapa V (Pluvial Ø40)", dynamic=True),

        # AQUI TENES QUE AGREGAR LOS NOMBRES DE LOS SCRIPTS DE CODOS, REDUCTORES, BIFURCACION.. ETC

        # create_element("manguito", "Manguito"),
        # create_element("codo", "Codo"),
        # create_element("te", "Te"),
        # create_element("colze_base", "Colze Base"),
    ],
    "summary": {
        k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]
    },
}


def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)
