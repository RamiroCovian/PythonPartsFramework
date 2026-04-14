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
    "name": "ELECTRICIDAD",
    "label": "Instalación de Electricidad",
    "angles": [],
    "angles_read": "Libre (ángulo interior >= 45°)",
    "default_layers" : {
        "default": "IS_COR_ELECTRICITAT_FAB",
        "layer_polyline": "IS_COR_ELECTRICITAT_FAB",
    },
    "layers": [
        {"key": "IS_REJIBANDS", "label": "Rejibands"},
        {"key": "IS_COR_TELECOS_FAB", "label": "Telecos Sobre Rejiband"},
        {"key": "IS_COR_TELECOS_IN", "label": "Telecos D'Entrada"},
        {"key": "IS_COR_TELECOS_OUT", "label": "Telecos De Sortida"},
        {"key": "IS_COR_ELECTRICITAT_FAB", "label": "Corrugats Sobre Rejiband"},
        {"key": "IS_COR_ELECTRICITAT_FAB_IN", "label": "Corrugats D'Entrada"},
        {"key": "IS_COR_ELECTRICITAT_FAB_OUT", "label": "Corrugats De Sortida"},
    ],
    "installation_types": [
        {
            "key": "rejiband_u",
            "label": "Rejiband U 100mm",
            "color": 1,
            "elems": [], "diameter": 100,
            "overlap_mm": 50, "allowed_angles": "Libre (ángulo interior >= 45°)",
             "is_individual": False, "min_segment_length": 300,
            "angles": [], "connections": [],
        },
        {
            "key": "rejiband_u",
            "label": "Rejiband U 200mm",
            "color": 1,
            "elems": [], "diameter": 200,
            "overlap_mm": 50, "allowed_angles": "Libre (ángulo interior >= 45°)",
            "is_individual": False, "min_segment_length": 300,
            "angles": [], "connections": [],
        },
        # Modo grupo: unión booleana → tramo continuo (crítico en electricidad).
        # is_individual=True rompe la continuidad (un PP por tramo, sin MakeUnion).
        {"key": "conducto_telecomunicaciones", "label": "Telecomunicaciones", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 15, "elems": [], "diameter": 20.0, "overlap_mm": 10},
        {"key": "conducto_luz_retorno_paralelas", "label": "Luz retorno / Paralelas", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 13, "elems": [], "diameter": 20.0, "overlap_mm": 10},
        {"key": "conducto_alimentacion_horno", "label": "Alimentación horno", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 28, "elems": [], "diameter": 25.0, "overlap_mm": 12.5},
        {"key": "conducto_alimentacion_luces_cajetines", "label": "Alimentación luces / Cajetines", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 16, "elems": [], "diameter": 20.0, "overlap_mm": 10},
        {"key": "conducto_cajetin_a_enchufe", "label": "Cajetín a enchufe", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 6, "elems": [], "diameter": 20.0, "overlap_mm": 10},
        {"key": "conducto_interruptores_domotica", "label": "Interruptores / Domótica", "is_individual": False,
            "min_segment_length": 300, "angles": [], "connections": [],
            "allowed_angles": "Libre (ángulo interior >= 45°)",
            "color": 27, "elems": [], "diameter": 20.0, "overlap_mm": 10},
    ],
    "elements3D": [
        create_element("rejiband_u", "Rejiband U 100mm", dynamic=True, diameter=100),
        create_element("rejiband_u", "Rejiband U 200mm", dynamic=True, diameter=200),
        create_element("conducto_telecomunicaciones", "Telecomunicaciones", dynamic=True, diameter=20.0),
        create_element("conducto_luz_retorno_paralelas", "Luz retorno / Paralelas", dynamic=True, diameter=20.0),
        create_element("conducto_alimentacion_horno", "Alimentación horno", dynamic=True, diameter=25.0),
        create_element("conducto_alimentacion_luces_cajetines", "Alimentación luces / Cajetines", dynamic=True, diameter=20.0),
        create_element("conducto_cajetin_a_enchufe", "Conducto Aislado 150 mm", dynamic=True, diameter=20),
        create_element("conducto_interruptores_domotica", "Conducto Aislado 160 mm", dynamic=True, diameter=20),
        # Elementos definidos (estáticos, colocados en puntos libres)
        {
            "key": "caixa_connexions_200",
            "label": "Caixa Connexions 200",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.caixa_connexions_200_script",
            "pythonpart": "CaixaConnexions200Script",
            "dinamic": False,
        },
    ],
    "summary": {k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]},
}

def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)