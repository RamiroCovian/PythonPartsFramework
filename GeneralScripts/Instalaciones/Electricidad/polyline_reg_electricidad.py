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
        {"key": "KN_ELECTRICITAT", "label": "TD - Electricitat"},
        {"key": "KN_XPS_RECESS", "label": "TD - XPS Recess"},
        {"key": "KN_X_ELECTRICITAT", "label": "EN - Cara X"},
        {"key": "KN_Y_ELECTRICITAT", "label": "EN - Cara Y"},
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
        create_element("conducto_telecomunicaciones_td", "Telecomunicaciones TD", dynamic=True, diameter=20.0),
        create_element("conducto_luz_retorno_paralelas", "Luz retorno / Paralelas", dynamic=True, diameter=20.0),
        create_element("conducto_luz_retorno_paralelas_td", "Luz retorno / Paralelas TD", dynamic=True, diameter=20.0),
        create_element("conducto_alimentacion_horno", "Alimentación horno", dynamic=True, diameter=25.0),
        create_element("conducto_alimentacion_horno_td", "Alimentación horno TD", dynamic=True, diameter=25.0),
        create_element("conducto_alimentacion_luces_cajetines", "Alimentación luces / Cajetines", dynamic=True, diameter=20.0),
        create_element("conducto_alimentacion_luces_cajetines_td", "Alimentación luces / Cajetines TD", dynamic=True, diameter=20.0),
        create_element("conducto_cajetin_a_enchufe", "Conducto Aislado 150 mm", dynamic=True, diameter=20),
        create_element("conducto_cajetin_a_enchufe_td", "Cajetín a enchufe TD", dynamic=True, diameter=20.0),
        create_element("conducto_interruptores_domotica", "Conducto Aislado 160 mm", dynamic=True, diameter=20),
        create_element("conducto_interruptores_domotica_td", "Interruptores / Domótica TD", dynamic=True, diameter=20.0),
        # Elementos definidos (estáticos, colocados en puntos libres)
        {
            "key": "caixa_connexions_200",
            "label": "Caixa Connexions 200",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixa_connexions_200_script",
            "pythonpart": "CaixaConnexions200Script",
            "dinamic": False,
        },
        {
            "key": "caixa_connexions",
            "label": "Caixa Connexions",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.en_electricidad.caixa_connexions_script",
            "pythonpart": "CaixaConnexionsScript",
            "dinamic": False,
        },
        {
            "key": "caixeti_1",
            "label": "Caixetí 1",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixeti_1_script",
            "pythonpart": "Caixeti1Script",
            "dinamic": False,
        },
        {
            "key": "caixete_1_ut",
            "label": "Caixete 1 UT",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.en_electricidad.caixete_1_ut_script",
            "pythonpart": "Caixete1UTScript",
            "dinamic": False,
        },
        {
            "key": "caixeti_2",
            "label": "Caixetí 2",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixeti_2_script",
            "pythonpart": "Caixeti2Script",
            "dinamic": False,
        },
        {
            "key": "caixeti_2ut",
            "label": "Caixetí 2 UT",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.en_electricidad.caixeti_2ut_script",
            "pythonpart": "Caixeti2UTScript",
            "dinamic": False,
        },
        {
            "key": "caixeti_3",
            "label": "Caixetí 3",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixeti_3_script",
            "pythonpart": "Caixeti3Script",
            "dinamic": False,
        },
        {
            "key": "caixeti_4",
            "label": "Caixetí 4",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixeti_4_script",
            "pythonpart": "Caixeti4Script",
            "dinamic": False,
        },
        {
            "key": "caixeti_doble_vertical",
            "label": "Caixetí Doble Vertical",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.caixeti_doble_vertical_script",
            "pythonpart": "CaixetiDobleVerticalScript",
            "dinamic": False,
        },
        {
            "key": "porter_aplics",
            "label": "Porter i Aplics",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.porter_aplics_script",
            "pythonpart": "PorterAplicsScript",
            "dinamic": False,
        },
        {
            "key": "vehicle_electric",
            "label": "Vehicle Elèctric",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.vehicle_electric_script",
            "pythonpart": "VehicleElectricScript",
            "dinamic": False,
        },
        {
            "key": "llum_ext_xps80",
            "label": "Llum Ext. XPS 80",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.llum_ext_xps80_script",
            "pythonpart": "LlumExtXPS80Script",
            "dinamic": False,
        },
        {
            "key": "llum_ext_xps120",
            "label": "Llum Ext. XPS 120",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.llum_ext_xps120_script",
            "pythonpart": "LlumExtXPS120Script",
            "dinamic": False,
        },
        {
            "key": "llum_ext_xps70",
            "label": "Llum Ext. XPS 70",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.llum_ext_xps70_script",
            "pythonpart": "LlumExtXPS70Script",
            "dinamic": False,
        },
        {
            "key": "endoll_ext_corrugat",
            "label": "Endoll Ext amb Corrugat",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.td_electricidad.endoll_ext_corrugat_script",
            "pythonpart": "EndollExtCorrugat",
            "dinamic": False,
        },
        {
            "key": "caixeti_4ut",
            "label": "Caixetí 4 UT",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.en_electricidad.caixeti_4ut_script",
            "pythonpart": "Caixeti4UTScript",
            "dinamic": False,
        },
        {
            "key": "caixeti_3ut",
            "label": "Caixetí 3 UT",
            "roles": [0, 3],
            "module_path": "pyp-scripts.Elementos.en_electricidad.caixeti_3ut_script",
            "pythonpart": "Caixeti3UTScript",
            "dinamic": False,
        },
    ],
    "summary": {k: [] for k in ["conductos", "conexiones", "codo_90", "difusores", "manguitos"]},
}

def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)