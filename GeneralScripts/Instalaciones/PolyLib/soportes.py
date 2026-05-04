import unicodedata
import importlib
import os
import sys
import NemAll_Python_Utility as PythonUtility
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService
from NemAll_Python_BaseElements import LayerService

# Utilidades de lectura de JSON externo para soportes
#
# NOTA IMPORTANTE:
# Dependiendo de cómo Allplan cargue el PythonPart, este fichero puede ser
# - un módulo suelto:          import SoportesFromJson
# - parte de un paquete:       from .SoportesFromJson import ...
# Probamos ambas variantes para que funcione en los dos casos.
try:
    # Caso 1: mismo directorio, sin paquete explícito
    from .utils import get_default_json_path, load_supports_from_json # type: ignore

    print("[Soportes] SoportesFromJson importado como módulo de paquete.")
except Exception as exc:
    # En caso de fallo de import (por ejemplo, en instalaciones antiguas)
    # dejamos las referencias como None y seguimos con el comportamiento clásico.
    print(f"[Soportes] Aviso: no se pudo importar SoportesFromJson: {exc}")
    SupportJson = None

    def load_supports_from_json(_path=None):
        return []

    def compute_segment_length(_support):
        return 0.0

    def get_default_json_path():
        return "N/A"


def check_allplan_version(_build_ele, version) -> bool:
    return True


# Parámetros geométricos por tipo de soporte + índice
PARAMS = {
    "Zeta": [
        # 0 -> 0mm
        {
            # Horizontal
            "LEN_X_HORIZONTAL": 729.30,
            "LEN_Y_HORIZONTAL": 50.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 100,
            "LAYER_SHORT": "IS_SUPORTS_LINEALS",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 70.0,  # Zeta 0mm: margen solo al inicio
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 0.0,
            "LEN_Y_VERTICAL": 0.0,
            "HEIGHT_VERTICAL": 0.0,
            # Pestañas
            "LEN_X_TABS": 0.0,
            "LEN_Y_TABS": 0.0,
            "HEIGHT_TABS": 0.0,
            "CYLINDER_RADIUS_TABS": 0.0,
            "CYLINDER_HEIGHT_TABS": 0.0,
            "CYLINDER_POS_X_TABS": 0.0,
            "CYLINDER_POS_Y_TABS": 0.0,
            "CYLINDER_POS_Y_TABS_OFFSET": 0.0,
            # Attributes
            "ATTR01": "W1",
            "ATTR05": "LINEAL;VARIFIX",
            "ATTR09": "",
            "6_CC_IS": "IS02",
            "pmp_CARTICULO": "KN16_005_001",
            "pmp_nom": "VARIFIX PLA",
            "pmp_densitat": 7874.0,
            "pmp_cargols": 2,
            "pmp_pare": "",
            "pmp_pes_unitari": 0.0,  # NUMERICO
        },
        # 1 -> 205x152.26mm
        {
            # Horizontal
            "LEN_X_HORIZONTAL": 152.26,
            "LEN_Y_HORIZONTAL": 50.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 100,
            "LAYER_SHORT": "IS_MULTISUPORT_ECV",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 50.0,
            "HEIGHT_VERTICAL": 205.0,
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 50.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            "CYLINDER_POS_Y_TABS_OFFSET": 25.0,
            # Attributes
            "ATTR01": "W1",
            "ATTR05": "ZETA;VARIFIX",
            "ATTR09": "",
            "6_CC_IS": "IS08",
            "pmp_CARTICULO": "KN16_005_004",
            "pmp_nom": "VARIFIX ELECTRICITAT",
            "pmp_pare": "",
            "pmp_pes_unitari": 0.8300,  # NUMERICO
        },
        # 2 -> 205x200mm
        {
            # Horizontal
            "LEN_X_HORIZONTAL": 200.0,
            "LEN_Y_HORIZONTAL": 50.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 100,
            "LAYER_SHORT": "IS_SUPORTS_ELECTRICITAT",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 50.0,
            "HEIGHT_VERTICAL": 205.0,
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 50.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            "CYLINDER_POS_Y_TABS_OFFSET": 25.0,
            # Attributes
            "ATTR01": "W1",
            "ATTR05": "ZETA;VARIFIX",
            "ATTR09": "",
            "6_CC_IS": "IS08",
            "pmp_CARTICULO": "KN16_005_004",
            "pmp_nom": "VARIFIX ELECTRICITAT",
            "pmp_pare": "",
            "pmp_pes_unitari": 0.8300,  # NUMERICO
        },
        # 3 -> 110x200mm
        {
            # Horizontal
            "LEN_X_HORIZONTAL": 200.0,
            "LEN_Y_HORIZONTAL": 50.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 100,
            "LAYER_SHORT": "IS_SUPORTS_VENT",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 50.0,
            "HEIGHT_VERTICAL": 110.0,
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 50.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            "CYLINDER_POS_Y_TABS_OFFSET": 25.0,
            # Attributes
            "ATTR01": "W6",
            "ATTR05": "OMEGA;VARIFIX",
            "ATTR09": "",
            "6_CC_IS": "IS08",
            "pmp_CARTICULO": "KN16_005_003",
            "pmp_nom": "VARIFIX VENTILACIO",
            "pmp_pare": "",
            "pmp_pes_unitari": 0.8300,  # NUMERICO
        },
    ],
    "Omega": [
        # 0 -> Vent. (SVP)
        {
            # Horizontal
            "LEN_X_HORIZONTAL": 675.0,  # TENER EN CUENTA QUE EL LARGO DEL SOPORTE TIENE QUE SUMAR LOS 3MM DE CADA LADO (3*2 = 6mm)
            "LEN_Y_HORIZONTAL": 25.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 5,
            "LAYER_SHORT": "IS_SUPORTS_VENT",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 25.0,
            "HEIGHT_VERTICAL": 110.0,  # TENER EN CUENTA QUE EL ALTO DEL SOPORTE ES EL QUE MANDA, A ESTE NO HAY QUE SUMARLE NADA
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 25.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            # Attributes
            "ATTR01": "V",
            "ATTR05": "OMEGA;ESTANDARD",
            "ATTR09": "",
            "6_CC_IS": "IS07",
            "pmp_cargols": 4,
            "pmp_CARTICULO": "KN8_005_002",
            "pmp_nom": "SUPORT VENTILACIO (SVP)",
            "pmp_pare": "",
            "pmp_densitat": 7874.0,  # NUMERICO
        },
        {  # 1 -> Electr./Clima (SEP)
            # Horizontal
            "LEN_X_HORIZONTAL": 675.0,
            "LEN_Y_HORIZONTAL": 25.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 66,
            "LAYER_SHORT": "IS_SUPORTS_ELECTRICITAT",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 25.0,
            "HEIGHT_VERTICAL": 205.0,
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 25.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            # Attributes
            "ATTR01": "EC",
            "ATTR05": "OMEGA;ESTANDARD",
            "ATTR09": "",
            "6_CC_IS": "IS07",
            "pmp_cargols": 4,
            "pmp_CARTICULO": "KN08_005_003",
            "pmp_nom": "SUPORT ELECTRICITAT (SEP)",
            "pmp_pare": "",
            "pmp_densitat": 7874.0,  # NUMERICO
        },
        {  # 2 -> Varifix
            # Horizontal
            "LEN_X_HORIZONTAL": 825.0,
            "LEN_Y_HORIZONTAL": 50.0,
            "HEIGHT_HORIZONTAL": 3.0,
            "COLOR": 100,
            "LAYER_SHORT": "IS_SUPORTS_VENT",
            "CAVITAT_LEN_X_HORIZONTAL": 20.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 8.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 3.0,
            "CAVITAT_INIT/END": 27.50,
            "CAVITAT_BETWEEN": 30.0,
            # Vertical
            "LEN_X_VERTICAL": 3.0,
            "LEN_Y_VERTICAL": 50.0,
            "HEIGHT_VERTICAL": 110.0,
            # Pestañas
            "LEN_X_TABS": 22.0,
            "LEN_Y_TABS": 50.0,
            "HEIGHT_TABS": 3.0,
            "CYLINDER_RADIUS_TABS": 2.5,
            "CYLINDER_HEIGHT_TABS": 3.0,
            "CYLINDER_POS_X_TABS": 5.0,
            "CYLINDER_POS_Y_TABS": 2.5,
            "CYLINDER_POS_Y_TABS_OFFSET": 25.0,
            # Attributes
            "ATTR01": "W6",
            "ATTR05": "OMEGA;VARIFIX",
            "ATTR09": "",
            "6_CC_IS": "IS08",
            "pmp_CARTICULO": "KN16_005_003",
            "pmp_nom": "VARIFIX VENTILACIO",
            "pmp_pare": "",
            "pmp_pes_unitari": 0.8300,  # NUMERICO
        },
    ],
    "Cinta": [
        {  # 0 -> Cinta
            # Horizontal
            "LEN_X_HORIZONTAL": 825.0,
            "LEN_Y_HORIZONTAL": 17.0,
            "HEIGHT_HORIZONTAL": 2.0,
            "COLOR": 91,
            "LAYER_SHORT": "IS_CINTA_PERFORADA",
            "CAVITAT_LEN_X_HORIZONTAL": 0.0,
            "CAVITAT_LEN_Y_HORIZONTAL": 0.0,
            "CAVITAT_HEIGHT_HORIZONTAL": 0.0,
            "CAVITAT_INIT/END": 0.0,
            "CAVITAT_BETWEEN": 0.0,
            # Vertical
            "LEN_X_VERTICAL": 2.0,
            "LEN_Y_VERTICAL": 17.0,
            "HEIGHT_VERTICAL": 88.0,
            # Pestañas
            "LEN_X_TABS": 20.0,
            "LEN_Y_TABS": 17.0,
            "HEIGHT_TABS": 2.0,
            "CYLINDER_RADIUS_TABS": 0.0,
            "CYLINDER_HEIGHT_TABS": 0.0,
            "CYLINDER_POS_X_TABS": 0.0,
            "CYLINDER_POS_Y_TABS": 0.0,
            "CYLINDER_POS_Y_TABS_OFFSET": 0.0,
            # Attributes
            "ATTR01": "CINTA PERFORADA",
            "ATTR13": "CARGOL M5X2.5;2",
            "ATTR09": "",
            "6_CC_IS": "IS05",
            "pmp_CARTICULO": "KN16_003_001",
            "pmp_densitat": 7874.0,
            "pmp_nom": "CINTA PERFORADA",
            "pmp_pare": "",
            "pmp_cargols": 2,  # NUMERICO
        },
    ],
}

# Ver que opcion es mejor, una lista de 2 diccionarios?
# OJO: las claves deben coincidir EXACTAMENTE con los textos del .pyp
MAP_SUPPORT = {
    "Zeta": {
        "0mm": 0,
        "205x152.26mm": 1,
        "205x200mm": 2,
        "110x200mm": 3,
    },
    "Omega": {
        # Textos EXACTOS del ValueList en Varafix.pyp
        "Venti.(SVP)": 0,
        "Electr./Clima(SEP)": 1,
        "Varifix": 2,
    },
    "Cinta": {
        "Cinta": 0,
    },
}

COMBO_NAME_BY_SUPPORT = {
    "Zeta": "TypeSupportZeta",
    "Omega": "TypeSupportOmega",
    "Cinta": "TypeSupportCinta",
}

# Mapeo subtipo semántico -> layer (para Electr./Clima y Varifix)
MAP_LAYER_BY_INSTALLATION = {
    "Ventilación": "IS_SUPORTS_VENT",
    "Electricidad": "IS_SUPORTS_ELECTRICITAT",
    "Clima": "IS_SUPORTS_CLIMA",
    "Agua": "IS_SUPORTS_AIGUA",
    "Saneamiento": "IS_SUPORTS_SANE",
}

# Mapeo subtipo semántico -> pmp_nom (para Electr./Clima y Varifix)
MAP_PMP_NOM_BY_INSTALLATION = {
    "Ventilación": "SUPORT VENTILACIO (SVP)",
    "Electricidad": "SUPORT ELECTRICITAT (SEP)",
    "Clima": "SUPORT CLIMA (SCP)",
    "Agua": "SUPORT AIGUA",
    "Saneamiento": "SUPORT SANE",
}

def _normalize_token(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.strip().lower()


def _infer_installation_type_from_subtype(subtype_norm: str):
    """
    Traduce subtipo semántico normalizado a tipo de instalación canónico.
    """
    if subtype_norm in ("ventilacion", "svp", "venti.(svp)", "venti svp"):
        return "Ventilación"
    if subtype_norm == "clima":
        return "Clima"
    if subtype_norm == "electricidad":
        return "Electricidad"
    if subtype_norm == "agua":
        return "Agua"
    if subtype_norm == "saneamiento":
        return "Saneamiento"
    return None


def _json_get_value(support_data, *keys, default=None):
    """
    Obtiene un valor desde soporte JSON aceptando:
    - objeto con atributos (SupportJson)
    - diccionario (dict)
    y múltiples aliases de clave.
    """
    if support_data is None:
        return default

    if isinstance(support_data, dict):
        for key in keys:
            if key in support_data:
                value = support_data.get(key)
                if value is not None:
                    return value
        return default

    for key in keys:
        value = getattr(support_data, key, None)
        if value is not None:
            return value
    return default


def _refresh_soportes_from_json_helpers():
    """
    Fuerza recarga de SoportesFromJson para evitar caché de módulos
    en sesiones largas de Allplan.
    """
    module_names = ("Soportes.SoportesFromJson", "SoportesFromJson")
    last_error = None

    for module_name in module_names:
        try:
            module = sys.modules.get(module_name)
            if module is None:
                module = importlib.import_module(module_name)
            else:
                module = importlib.reload(module)

            globals()["SupportJson"] = getattr(module, "SupportJson", None)
            globals()["load_supports_from_json"] = getattr(
                module, "load_supports_from_json", lambda _path=None: []
            )
            globals()["compute_segment_length"] = getattr(
                module, "compute_segment_length", lambda _support: 0.0
            )
            globals()["get_default_json_path"] = getattr(
                module, "get_default_json_path", lambda: "N/A"
            )

            print(f"[Soportes] SoportesFromJson recargado: {module.__file__}")
            return
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        print(f"[Soportes] Aviso: no se pudo recargar SoportesFromJson: {last_error}")

# Mapeo ID -> nombre de atributo personalizado (según IDs de Allplan)
# Usar IDs directamente evita problemas con idioma (Atributo personalizado vs Custom attribute)
CUSTOM_ATTR_IDS = {
    1: 1083,  # Custom attribute 01
    2: 1084,  # Custom attribute 02
    3: 1085,  # Custom attribute 03
    4: 1086,  # Custom attribute 04
    5: 1087,  # Custom attribute 05
    6: 1895,  # Custom attribute 06
    7: 1896,  # Custom attribute 07
    8: 1897,  # Custom attribute 08
    9: 1898,  # Custom attribute 09
    10: 1899,  # Custom attribute 10
    11: 1900,  # Custom attribute 11
    12: 1901,  # Custom attribute 12
    13: 1902,  # Custom attribute 13
    14: 1903,  # Custom attribute 14
    15: 1904,  # Custom attribute 15
    16: 1947,  # Custom attribute
}

# Alias para compatibilidad
ATTR_PERSO_01_ID = CUSTOM_ATTR_IDS[1]
ATTR_PERSO_05_ID = CUSTOM_ATTR_IDS[5]
ATTR_PERSO_09_ID = CUSTOM_ATTR_IDS[9]


class SupportModel:
    """Clase que representa el soporte"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        # 1) Tipo de soporte
        # 1.a) Intentar leer TypeSupport (nuevo nombre desde polilínea)
        type_support = None
        type_support_raw = getattr(build_ele, "TypeSupport", None)
        if type_support_raw is not None:
            type_support_val = getattr(type_support_raw, "value", type_support_raw)
            if type_support_val is not None:
                type_support = str(type_support_val).strip()

        # 1.a.1) Fallback: Intentar leer TypeSupport (compatibilidad con uso manual del PythonPart)
        if not type_support:
            type_support_raw = getattr(build_ele, "TypeSupport", None)
            if type_support_raw is not None:
                type_support_val = getattr(type_support_raw, "value", type_support_raw)
                if type_support_val is not None:
                    type_support = str(type_support_val).strip()

        # 1.b) Si no hay TipoDeAgua, intentar con el RadioButtonGroup "Fontaneria" (polilínea)
        if not type_support:
            font_raw = getattr(build_ele, "Fontaneria", None)
            font_val = getattr(font_raw, "value", font_raw)
            try:
                font_int = int(font_val) # type: ignore
            except Exception:
                font_int = None

            if font_int == 0:
                type_water = "Fred"  # Agua fría
            elif font_int == 1:
                type_water = (
                    "Calent"  # Agua caliente #TODO: Revisar como lo implementamos
                )

        # 1.c) Seguridad: si no está en PARAMS, caer a Fred
        if type_support not in PARAMS:
            print(
                f"[SupportModel] Warning: Tipo de soporte '{type_support}' no válido, usando 'Zeta' por defecto"
            )
            type_support = "Zeta"

        self.type_support = type_support

        # Selección de soporte: modo por defecto = COMBO (uso manual)
        idx = 0  # índice por defecto

        combo_param_name = COMBO_NAME_BY_SUPPORT.get(self.type_support)
        if combo_param_name:
            combo_raw = getattr(build_ele, combo_param_name, None)
            combo_val = getattr(combo_raw, "value", combo_raw)
            combo_str = str(combo_val) if combo_val is not None else ""
            combo_str = combo_str.strip()

            map_for_support = MAP_SUPPORT.get(self.type_support, {})
            idx = map_for_support.get(combo_str, 0)
            self.support_key = (
                combo_str  # 'Venti.(SVP)', 'Electr./Clima(SEP)', 'Varifix', etc.
            )
            self.support_idx = idx  # 0, 1, 2 según MAP_SUPPORT

        # Proteger por si el idx se va de rango
        max_idx = len(PARAMS[self.type_support]) - 1
        if idx > max_idx:
            idx = max_idx
        if idx < 0:
            idx = 0

        # Parámetros elegidos (copia, no referencia)
        self.param = dict(PARAMS[self.type_support][idx])

        # Sobrescribir LAYER_SHORT y pmp_nom según tipo de instalación (solo Omega Electr./Clima o Varifix)
        if self.type_support == "Omega":
            support_key = getattr(self, "support_key", "")
            if support_key == "Electr./Clima(SEP)":
                type_inst_raw = getattr(build_ele, "TypeInstallationSEP", None)
                type_inst_val = getattr(type_inst_raw, "value", type_inst_raw)
                type_inst = (
                    str(type_inst_val).strip() if type_inst_val else "Electricidad"
                )
                layer = MAP_LAYER_BY_INSTALLATION.get(type_inst)
                pmp_nom = MAP_PMP_NOM_BY_INSTALLATION.get(type_inst)
                if layer:
                    self.param["LAYER_SHORT"] = layer
                if pmp_nom:
                    self.param["pmp_nom"] = pmp_nom
            elif support_key == "Varifix":
                type_inst_raw = getattr(build_ele, "TypeInstallationVarifix", None)
                type_inst_val = getattr(type_inst_raw, "value", type_inst_raw)
                type_inst = str(type_inst_val).strip() if type_inst_val else "Agua"
                layer = MAP_LAYER_BY_INSTALLATION.get(type_inst)
                pmp_nom = MAP_PMP_NOM_BY_INSTALLATION.get(type_inst)
                if layer:
                    self.param["LAYER_SHORT"] = layer
                if pmp_nom:
                    self.param["pmp_nom"] = pmp_nom

        # Common properties
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        self.common_props = common_properties

        common_properties.Color = int(self.param["COLOR"])

        # IDs de atributos personalizados: usar IDs directamente (independiente del idioma)
        self.attr01_id = CUSTOM_ATTR_IDS.get(1)   # Custom attribute 01
        self.attr05_id = CUSTOM_ATTR_IDS.get(5)   # Custom attribute 05
        self.attr09_id = CUSTOM_ATTR_IDS.get(9)   # Custom attribute 09
        self.attr13_id = CUSTOM_ATTR_IDS.get(13)  # Custom attribute 13
        self.attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
        self.attr_pmp_cargols_id = AttributeService.GetAttributeID(
            self.doc, "pmp_cargols"
        )
        self.attr_pmp_CARTICULO_id = AttributeService.GetAttributeID(
            self.doc, "pmp_CARTICULO"
        )
        self.attr_pmp_nom_id = AttributeService.GetAttributeID(self.doc, "pmp_nom")
        self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")

        self.attr_densitat_id = AttributeService.GetAttributeID(
            self.doc, "pmp_densitat"
        )

        # Superficie: se controla exclusivamente desde JSON ("Liso"/"Perforado")
        # Valor por defecto conservador para fallback sin JSON.
        self.is_perforated = True

    # ------------------------------------------------------------
    # Configuración opcional a partir de JSON externo
    # ------------------------------------------------------------

    def apply_json_definition(self, support_json, caller_installation: str | None = None):
        """
        Ajusta el tipo de soporte y el índice a partir de un objeto SupportJson.

        Reglas de mapeo:
        - `tipo`: selecciona familia ('Omega' / 'Zeta' / 'Cinta').
        - `subtipo` semántico:
          - Omega + "Ventilación" -> "Venti.(SVP)"
          - Omega + "Electricidad" -> "Electr./Clima(SEP)"
          - Omega + "Clima" o "Varifix" o "Agua" o "Saneamiento" -> "Varifix"
          - Cinta -> idx=0 siempre (layer y atributos ya definidos en PARAMS)
        - Si no se puede mapear un valor, se mantiene la configuración previa.
        """
        if support_json is None:
            return

        tipo_raw = (
            _json_get_value(support_json, "tipo", "type", default="") or ""
        ).strip()
        if not tipo_raw:
            return

        # Normalizamos: OMEGA -> Omega, ZETA -> Zeta, etc.
        tipo_norm = tipo_raw.capitalize()
        if tipo_norm not in PARAMS:
            # Tipo desconocido: no tocamos la configuración actual
            print(
                f"[SupportModel] Tipo desde JSON '{tipo_raw}' no reconocido, se mantiene '{self.type_support}'"
            )
            return

        self.type_support = tipo_norm

        # Determinar índice a partir del subtipo semántico (Ventilación, Clima, etc.)
        subtipo_raw = (
            _json_get_value(support_json, "subtipo", "subtype", default="") or ""
        ).strip()
        subtype_norm = _normalize_token(subtipo_raw)
        idx = 0

        if self.type_support == "Omega":
            if subtype_norm in ("varifix", "clima", "agua", "saneamiento"):
                idx = MAP_SUPPORT["Omega"].get("Varifix", 0)
            elif subtype_norm in ("electricidad",):
                idx = MAP_SUPPORT["Omega"].get("Electr./Clima(SEP)", 0)
            elif subtype_norm in ("ventilacion", "svp", "venti.(svp)", "venti svp"):
                idx = MAP_SUPPORT["Omega"].get("Venti.(SVP)", 0)
        elif self.type_support == "Cinta":
            idx = 0
        elif self.type_support == "Zeta":
            # Para Zeta no se define el soporte por medidas en `subtipo`.
            # Regla:
            # - cota_a == 0  -> variante 0mm (PARAMS["Zeta"][0])
            # - cota_a  > 0  -> variante base con ala vertical (205x200mm)
            cota_a_json = float(
                _json_get_value(support_json, "cota_a", "height_a", default=0.0) or 0.0
            )
            if abs(cota_a_json) <= 1e-9:
                idx = 0
            else:
                idx = MAP_SUPPORT["Zeta"].get("205x200mm", 0)

        # Proteger por rango y actualizar parámetros
        max_idx = len(PARAMS[self.type_support]) - 1
        if idx < 0:
            idx = 0
        if idx > max_idx:
            idx = max_idx

        self.support_idx = idx
        map_omega = MAP_SUPPORT.get(self.type_support, {})
        self.support_key = next((k for k, v in map_omega.items() if v == idx), "")
        self.param = dict(PARAMS[self.type_support][idx])

        inferred_installation_type = _infer_installation_type_from_subtype(subtype_norm)

        # Si el subtipo no resolvió, usar la instalación del caller como fallback.
        if not inferred_installation_type and caller_installation:
            inferred_installation_type = caller_installation.strip()

        # En Electr./Clima(SEP) el tipo de instalación se deduce del subtipo semántico.
        if self.type_support == "Omega" and self.support_key == "Electr./Clima(SEP)":
            if inferred_installation_type in ("Clima", "Electricidad"):
                layer = MAP_LAYER_BY_INSTALLATION.get(inferred_installation_type)
                pmp_nom = MAP_PMP_NOM_BY_INSTALLATION.get(inferred_installation_type)
                if layer:
                    self.param["LAYER_SHORT"] = layer
                if pmp_nom:
                    self.param["pmp_nom"] = pmp_nom

        # En Varifix, Agua/Saneamiento también se deduce desde subtipo semántico.
        if self.type_support == "Omega" and self.support_key == "Varifix":
            if inferred_installation_type in ("Agua", "Saneamiento"):
                layer = MAP_LAYER_BY_INSTALLATION.get(inferred_installation_type)
                pmp_nom = MAP_PMP_NOM_BY_INSTALLATION.get(inferred_installation_type)
                if layer:
                    self.param["LAYER_SHORT"] = layer
                if pmp_nom:
                    self.param["pmp_nom"] = pmp_nom

        # En Zeta, el subtipo semántico solo aplica layer/pmp_nom cuando cota_a > 0.
        # Cuando cota_a == 0 (variante 0mm), se conserva IS_SUPORTS_LINEALS de PARAMS.
        if self.type_support == "Zeta" and inferred_installation_type:
            is_0mm = self.support_idx == MAP_SUPPORT["Zeta"].get("0mm", 0)

            if not is_0mm:
                layer = MAP_LAYER_BY_INSTALLATION.get(inferred_installation_type)
                pmp_nom = MAP_PMP_NOM_BY_INSTALLATION.get(inferred_installation_type)
                if layer:
                    self.param["LAYER_SHORT"] = layer
                if pmp_nom:
                    self.param["pmp_nom"] = pmp_nom
                self.param["ATTR05"] = "ZETA;VARIFIX"
            else:
                layer = self.param.get("LAYER_SHORT")
                pmp_nom = self.param.get("pmp_nom")

            # Atributos semánticos: ventilación vs resto de instalaciones.
            if inferred_installation_type == "Ventilación":
                self.param["ATTR01"] = "W6"
            else:
                self.param["ATTR01"] = "W1"

        # Superficie obligatoria desde JSON ("Liso"/"Perforado")
        surface_raw = (
            _json_get_value(support_json, "superficie", "surface", default="") or ""
        ).strip()
        if self.type_support == "Cinta":
            self.is_perforated = False
        elif _normalize_token(surface_raw) == "liso":
            self.is_perforated = False
        elif _normalize_token(surface_raw) == "perforado":
            self.is_perforated = True
        else:
            # Si algo llega mal (no debería, el parser ya valida), dejamos perforado.
            print(
                f"[SupportModel] JSON: superficie inválida '{surface_raw}', se usa 'Perforado'"
            )
            self.is_perforated = True


    def set_length(self, length_mm: float):
        """
        Permite que la polilínea ajuste el largo del soporte.
        Cambiamos solo LEN_X, que es la longitud del soporte.
        """
        try:
            length_mm = float(length_mm)
        except Exception:
            return

        if length_mm <= 0:
            return

        self.param["LEN_X_HORIZONTAL"] = length_mm
        self.custom_length = length_mm

    def _create_support_attributes(self):
        """Armo los atributos personalizados segun el tipo de soporte."""
        p = self.param
        attrs = []

        if self.attr01_id and self.attr01_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr01_id, p["ATTR01"])
            )
        if self.attr05_id and self.attr05_id > 0 and "ATTR05" in p:
            attr05_val = p["ATTR05"]
            if not self.is_perforated:
                # Liso: mantener parte antes del ";" y añadir "; LLIS"
                if ";" in attr05_val:
                    attr05_val = attr05_val.split(";", 1)[0].strip() + "; LLIS"
                else:
                    attr05_val = attr05_val.strip() + "; LLIS"
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr05_id, attr05_val)
            )
        if self.attr09_id and self.attr09_id > 0 and "ATTR09" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr09_id, p["ATTR09"])
            )
        if self.attr13_id and self.attr13_id > 0 and "ATTR13" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr13_id, p["ATTR13"])
            )
        if self.attr_6_cc_is_id and self.attr_6_cc_is_id > 0 and "6_CC_IS" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr_6_cc_is_id, p["6_CC_IS"])
            )
        if (
            self.attr_pmp_cargols_id
            and self.attr_pmp_cargols_id > 0
            and "pmp_cargols" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_cargols_id, str(p["pmp_cargols"])
                )
            )
        if self.attr_pmp_pare_id and self.attr_pmp_pare_id > 0 and "pmp_pare" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_pare_id, p["pmp_pare"]
                )
            )

        if (
            self.attr_pmp_CARTICULO_id
            and self.attr_pmp_CARTICULO_id > 0
            and "pmp_CARTICULO" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_CARTICULO_id, p["pmp_CARTICULO"]
                )
            )
        if self.attr_pmp_nom_id and self.attr_pmp_nom_id > 0 and "pmp_nom" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr_pmp_nom_id, p["pmp_nom"])
            )
        if self.attr_densitat_id and self.attr_densitat_id > 0 and "pmp_densitat" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_densitat_id, str(p["pmp_densitat"])
                )
            )

        if not attrs:
            return None

        attr_set = AllplanBaseElements.AttributeSet(attrs)
        return AllplanBaseElements.Attributes([attr_set])

    def _create_cylinder_brep(self, px, py, pz):
        """Crea un cilindro con el radio y altura especificados."""
        p = self.param
        # Origen en (0, 0, 0) con eje Z hacia arriba
        origin_cylinder = AllplanGeometry.Point3D(px, py, pz)
        placement = AllplanGeometry.AxisPlacement3D(origin_cylinder)

        # Crear el cilindro usando CreateCylinder (mismo método que en TechtivaPiece.py)
        # Parámetros: placement, radius, height, top_cap (True), bottom_cap (True)
        cylinder = AllplanGeometry.BRep3D.CreateCylinder(
            placement,
            p["CYLINDER_RADIUS_TABS"],
            p["CYLINDER_HEIGHT_TABS"],
            True,  # Tapa superior
            True,  # Tapa inferior
        )
        return cylinder

    def _create_single_capsule_at_x(self, param: dict, x_start: float):
        """
        Crea una sola cápsula de longitud CAVITAT_LEN_X_HORIZONTAL con su borde
        izquierdo en x_start. Centrada en Y respecto a LEN_Y_HORIZONTAL.
        """
        capsule_length = float(param["CAVITAT_LEN_X_HORIZONTAL"])
        len_y_support = float(param["LEN_Y_HORIZONTAL"])
        capsule_width = float(param["CAVITAT_LEN_Y_HORIZONTAL"])
        height = float(param["CAVITAT_HEIGHT_HORIZONTAL"])

        R = capsule_width / 2.0
        rect_length = max(capsule_length - 2.0 * R, 0.0)
        origin_y = (len_y_support - capsule_width) / 2.0

        origin_rect = AllplanGeometry.Point3D(x_start + R, origin_y, 0.0)
        placement_rect = AllplanGeometry.AxisPlacement3D(origin_rect)
        rect_brep = AllplanGeometry.BRep3D.CreateCuboid(
            placement_rect, rect_length, capsule_width, height
        )

        left_center = AllplanGeometry.Point3D(
            x_start + R, origin_y + capsule_width / 2.0, 0.0
        )
        left_cyl = AllplanGeometry.BRep3D.CreateCylinder(
            AllplanGeometry.AxisPlacement3D(left_center), R, height, True, True
        )

        right_center = AllplanGeometry.Point3D(
            x_start + capsule_length - R, origin_y + capsule_width / 2.0, 0.0
        )
        right_cyl = AllplanGeometry.BRep3D.CreateCylinder(
            AllplanGeometry.AxisPlacement3D(right_center), R, height, True, True
        )

        err, capsule = AllplanGeometry.MakeUnion(rect_brep, left_cyl)
        if err != 0 or capsule is None or not capsule.IsValid():
            return rect_brep
        err, capsule = AllplanGeometry.MakeUnion(capsule, right_cyl)
        if err != 0 or capsule is None or not capsule.IsValid():
            return rect_brep
        return capsule

    def _create_capsule_brep(self, param: dict):
        """
        Crea tantas cápsulas como quepan en la longitud del soporte, con
        separación CAVITAT_BETWEEN entre ellas. Margen CAVITAT_INIT/END:
        - Omega: al inicio y al final.
        - Zeta: solo al inicio; el final no importa.
        Centradas en el eje Y de LEN_Y_HORIZONTAL.
        """
        total_length = getattr(self, "custom_length", None)
        if total_length is None:
            total_length = float(param["LEN_X_HORIZONTAL"])
        capsule_length = float(param["CAVITAT_LEN_X_HORIZONTAL"])
        gap_between = float(param["CAVITAT_BETWEEN"])
        init_end = float(param["CAVITAT_INIT/END"])

        if self.type_support == "Zeta":
            # Zeta: margen solo al inicio
            available = total_length - init_end
        else:
            # Omega: margen al inicio y al final
            available = total_length - 2.0 * init_end

        if available <= 0:
            return None
        # n * capsule_length + (n-1) * gap_between <= available  =>  n <= (available + gap_between) / (capsule_length + gap_between)
        n = int((available + gap_between) / (capsule_length + gap_between))
        n = max(0, n)
        add_extra_at_end = (
            self.type_support == "Zeta" and getattr(self, "support_idx", 0) == 0
        )
        if n == 0 and not add_extra_at_end:
            return None

        result_brep = None
        for i in range(n):
            x_start = init_end + i * (capsule_length + gap_between)
            single = self._create_single_capsule_at_x(param, x_start)
            if single is None or not single.IsValid():
                continue
            if result_brep is None:
                result_brep = single
                continue
            err, result_brep = AllplanGeometry.MakeUnion(result_brep, single)
            if err != 0 or result_brep is None or not result_brep.IsValid():
                break

        # Zeta 0mm: si al final no cabía una cavidad completa, se crea igual una más; o si n==0, una al inicio
        if add_extra_at_end:
            x_start_extra = init_end + n * (capsule_length + gap_between)
            # Añadir una más si queda hueco al final sin caber una entera, o si no había ninguna (n==0)
            if (n == 0) or (
                x_start_extra < total_length
                and x_start_extra + capsule_length > total_length
            ):
                single_extra = self._create_single_capsule_at_x(param, x_start_extra)
                if single_extra is not None and single_extra.IsValid():
                    if result_brep is None:
                        result_brep = single_extra
                    else:
                        err, result_brep = AllplanGeometry.MakeUnion(
                            result_brep, single_extra
                        )

        return result_brep

    def _create_support_brep(self, param: dict):
        """Crea el brep del soporte."""

        # Uso el largo real si está disponible en build_ele
        length = getattr(self, "custom_length", None)
        if length is None:
            length = float(param["LEN_X_HORIZONTAL"])
        width = float(param["LEN_Y_HORIZONTAL"])
        height = float(param["HEIGHT_HORIZONTAL"])

        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        brep_centered = AllplanGeometry.BRep3D.CreateCuboid(
            placement, length, width, height
        )

        #########################################################
        ###############  lateral_left_brep  #####################
        #########################################################
        origin_lateral_left_brep = AllplanGeometry.Point3D(
            -param["LEN_X_VERTICAL"],
            0,
            -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
        )
        placement_lateral_left_brep = AllplanGeometry.AxisPlacement3D(
            origin_lateral_left_brep
        )
        brep_lateral_left = AllplanGeometry.BRep3D.CreateCuboid(
            placement_lateral_left_brep,
            param["LEN_X_VERTICAL"],
            param["LEN_Y_VERTICAL"],
            param["HEIGHT_VERTICAL"],
        )

        err, brep_with_left_lateral = AllplanGeometry.MakeUnion(
            brep_centered, brep_lateral_left
        )
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(brep_centered, brep_lateral): código {err}"
            )

        #########################################################
        ###############  lateral_right_brep  ####################
        #########################################################
        if self.type_support in ("Omega", "Cinta"):
            origin_lateral_right_brep = AllplanGeometry.Point3D(
                param["LEN_X_HORIZONTAL"],
                0,
                -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
            )
            placement_lateral_right_brep = AllplanGeometry.AxisPlacement3D(
                origin_lateral_right_brep
            )
            brep_lateral_right = AllplanGeometry.BRep3D.CreateCuboid(
                placement_lateral_right_brep,
                param["LEN_X_VERTICAL"],
                param["LEN_Y_VERTICAL"],
                param["HEIGHT_VERTICAL"],
            )
            err, brep_with_right_lateral = AllplanGeometry.MakeUnion(
                brep_with_left_lateral, brep_lateral_right
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_with_left_lateral, brep_lateral_right): código {err}"
                )
        else:
            # Zeta: no lateral derecho
            brep_with_right_lateral = brep_with_left_lateral

        #########################################################
        ############  lateral_left_bottom_brep  #################
        #########################################################
        origin_lateral_left_bottom_brep = AllplanGeometry.Point3D(
            -param["LEN_X_TABS"] - param["HEIGHT_HORIZONTAL"],
            0,
            -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
        )
        placement_lateral_left_bottom_brep = AllplanGeometry.AxisPlacement3D(
            origin_lateral_left_bottom_brep
        )
        brep_lateral_left_bottom = AllplanGeometry.BRep3D.CreateCuboid(
            placement_lateral_left_bottom_brep,
            param["LEN_X_TABS"],
            param["LEN_Y_TABS"],
            param["HEIGHT_TABS"],
        )
        err, brep_with_left_lateral_bottom = AllplanGeometry.MakeUnion(
            brep_with_right_lateral, brep_lateral_left_bottom
        )
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(brep_with_right_lateral, brep_lateral_left_bottom): código {err}"
            )

        #########################################################
        ############  lateral_right_bottom_brep  #################
        #########################################################
        if self.type_support in ("Omega", "Cinta"):
            origin_lateral_right_bottom_brep = AllplanGeometry.Point3D(
                param["LEN_X_HORIZONTAL"] + param["HEIGHT_HORIZONTAL"],
                0,
                -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
            )
            placement_lateral_right_bottom_brep = AllplanGeometry.AxisPlacement3D(
                origin_lateral_right_bottom_brep
            )
            brep_lateral_right_bottom = AllplanGeometry.BRep3D.CreateCuboid(
                placement_lateral_right_bottom_brep,
                param["LEN_X_TABS"],
                param["LEN_Y_TABS"],
                param["HEIGHT_TABS"],
            )
            err, brep_with_right_lateral_bottom = AllplanGeometry.MakeUnion(
                brep_with_left_lateral_bottom, brep_lateral_right_bottom
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_with_left_lateral_bottom, brep_lateral_right_bottom): código {err}"
                )
        else:
            brep_with_right_lateral_bottom = brep_with_left_lateral_bottom

        #########################################################
        ##############  cylinder_taps_brep  #####################
        #########################################################
        cylinder_taps_left_bottom = self._create_cylinder_brep(
            -param["CYLINDER_POS_X_TABS"] - (param["CYLINDER_RADIUS_TABS"] * 5),
            param["CYLINDER_POS_Y_TABS"] * 2,
            -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
        )

        err, brep_with_both_taps = AllplanGeometry.MakeSubtraction(
            brep_with_right_lateral_bottom, cylinder_taps_left_bottom
        )
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(brep_with_right_lateral_bottom, cylinder_taps_left_bottom): código {err}"
            )

        #########################################################
        ##############  cylinder_taps_brep  #####################
        #########################################################
        cylinder_taps_left_top = self._create_cylinder_brep(
            -param["CYLINDER_POS_X_TABS"] - (param["CYLINDER_RADIUS_TABS"] * 5),
            (param["CYLINDER_POS_Y_TABS"] * 8)
            + float(param.get("CYLINDER_POS_Y_TABS_OFFSET", 0.0)),
            -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
        )
        err, brep_with_left_taps = AllplanGeometry.MakeSubtraction(
            brep_with_both_taps, cylinder_taps_left_top
        )
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(brep_with_both_taps, cylinder_taps_left_top): código {err}"
            )

        #########################################################
        ##############  cylinder_taps_right_bottom_brep  #####################
        #########################################################
        if self.type_support in ("Omega", "Cinta"):
            cylinder_taps_right_bottom = self._create_cylinder_brep(
                +param["LEN_X_HORIZONTAL"]
                + param["HEIGHT_HORIZONTAL"]
                + param["CYLINDER_POS_X_TABS"]
                + (param["CYLINDER_RADIUS_TABS"] * 4)
                - 0.5,
                param["CYLINDER_POS_Y_TABS"] * 2,
                -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
            )
            err, brep_with_right_bottom_taps = AllplanGeometry.MakeSubtraction(
                brep_with_left_taps, cylinder_taps_right_bottom
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_with_left_taps, cylinder_taps_right_bottom): código {err}"
                )
            #########################################################
            #########  cylinder_taps_right_top_brep  ################
            #########################################################
            cylinder_taps_right_top = self._create_cylinder_brep(
                +param["LEN_X_HORIZONTAL"]
                + param["HEIGHT_HORIZONTAL"]
                + param["CYLINDER_POS_X_TABS"]
                + (param["CYLINDER_RADIUS_TABS"] * 4)
                - 0.5,
                (param["CYLINDER_POS_Y_TABS"] * 8)
                + float(param.get("CYLINDER_POS_Y_TABS_OFFSET", 0.0)),
                -param["HEIGHT_VERTICAL"] + param["HEIGHT_HORIZONTAL"],
            )
            err, brep_with_right_top_taps = AllplanGeometry.MakeSubtraction(
                brep_with_right_bottom_taps, cylinder_taps_right_top
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_with_right_bottom_taps, cylinder_taps_right_top): código {err}"
                )

            # Cápsulas (perforaciones): solo si el usuario eligió "Perforado"
            if self.is_perforated:
                capsule_brep = self._create_capsule_brep(self.param)
                if capsule_brep is not None:
                    err, brep_with_capsule = AllplanGeometry.MakeSubtraction(
                        brep_with_right_top_taps, capsule_brep
                    )
                    if err != 0:
                        raise Exception(
                            f"Error en MakeSubtraction(brep_with_right_top_taps, capsule_brep): código {err}"
                        )
                else:
                    brep_with_capsule = brep_with_right_top_taps
            else:
                brep_with_capsule = brep_with_right_top_taps
        else:
            # Zeta: no lateral derecho, no pestaña derecha ni cilindros derechos; sí cápsulas
            if self.is_perforated:
                capsule_brep = self._create_capsule_brep(self.param)
                if capsule_brep is not None:
                    err, brep_with_capsule = AllplanGeometry.MakeSubtraction(
                        brep_with_left_taps, capsule_brep
                    )
                    if err != 0:
                        raise Exception(
                            f"Error en MakeSubtraction(brep_with_left_taps, capsule_brep): código {err}"
                        )
                else:
                    brep_with_capsule = brep_with_left_taps
            else:
                brep_with_capsule = brep_with_left_taps

        return brep_with_capsule

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        return self._create_support_brep(self.param)

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico del tubo para centrarlo (X, Y, Z)
        # Para X usamos el largo total del tubo (que puede haber sido modificado con set_length)
        length_x = getattr(self, "custom_length", None)
        if length_x is None:
            length_x = float(p.get("LEN_X_HORIZONTAL", 0.0))
        half_x = length_x / 2.0
        # Para Y y Z usamos las dimensiones del outer (el elemento más grande)
        half_y = float(p.get("LEN_Y_HORIZONTAL", 0.0)) / 2.0
        half_z = float(p.get("HEIGHT_HORIZONTAL", 0.0)) / 2.0

        # Transformación para centrar el tubo en el origen
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(0.0, -half_y, -half_z))

        # Aplicar la transformación a ambos breps
        brep_centered = AllplanGeometry.Transform(brep, mat_center)

        model_list = []

        # Outer
        if brep_centered is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_props.ColorByLayer = False  # Desactivar color por layer

            # Asignar layer al support_model
            outer_layer_short = p.get("LAYER_SHORT", None)
            if outer_layer_short:
                outer_layer_id = LayerService.GetIDByShortName(
                    outer_layer_short, self.doc
                )
                # Fallback: si AIGUA no existe, probar AGUA (nomenclatura española)
                if outer_layer_id <= 0 and outer_layer_short == "IS_SUPORTS_AIGUA":
                    alt_layer = "IS_SUPORTS_AGUA"
                    outer_layer_id = LayerService.GetIDByShortName(alt_layer, self.doc)
                    if outer_layer_id > 0:
                        outer_layer_short = alt_layer
                if outer_layer_id > 0:
                    outer_props.Layer = outer_layer_id
                    # Reasignar color después de asignar layer para asegurar que se mantenga
                    outer_props.Color = p["COLOR"]
                    outer_props.ColorByLayer = False

            support_model = AllplanBasisElements.ModelElement3D(
                outer_props, brep_centered
            )

            # Atributos para support_model
            support_attributes = self._create_support_attributes()
            if support_attributes:
                support_model.SetAttributes(support_attributes)

            model_list.append(support_model)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter, caller_installation: str | None = None):
    """
    Crea el/los elementos finales.

    Integración con JSON externo:
    - Si hay soportes válidos en JSON, se crea un soporte por cada item.
    - Del JSON se aplican:
      - tipo/subtipo -> selección de familia y variante de soporte
      - superficie -> "Liso" (sin perforaciones) / "Perforado"
      - cota_b -> longitud horizontal (con descuento interno de 6 mm)
      - cota_a -> altura vertical
      - posicion1/posicion2 -> orientación y emplazamiento 3D
      - angulo_inclinacion -> giro adicional sobre el eje del soporte
    - En Omega, `subtipo` decide también capa y `pmp_nom` para:
      - `Electr./Clima(SEP)`: `Clima`/`Electricidad`
      - `Varifix`: `Agua`/`Saneamiento`
    - Si el JSON no existe, está vacío o no es válido, se mantiene el
      comportamiento clásico del PythonPart (un único soporte por parámetros UI).
    """
    model_list = []

    # Forzar refresco de helpers JSON para evitar desalineación por cachérevisar la seleccion de soportes
    # entre ejecución standalone y runtime de Allplan.
    _refresh_soportes_from_json_helpers()

    # 1) Intentar leer soportes desde JSON externo
    json_supports = []
    try:
        json_path = get_default_json_path()
        print(f"[Soportes] JSON path por defecto: {json_path}")
        json_path_str = str(json_path) if json_path else ""
        if json_path_str and json_path_str != "N/A" and not os.path.exists(json_path_str):
            PythonUtility.ShowMessageBox(
                f"No se encontró el archivo JSON de soportes:\n{json_path_str}",
                PythonUtility.MB_OK,
            )
        else:
            json_supports = load_supports_from_json()
    except Exception as exc:
        print(f"[Soportes] Aviso: error leyendo JSON externo de soportes: {exc}")

    if json_supports:
        print(f"[Soportes] Creando soportes desde JSON (n={len(json_supports)})")
        for js in json_supports:
            try:
                print(f"[Soportes] Tipo runtime del soporte JSON: {type(js)}")
                print(
                    "[Soportes] JSON en create_element: tipo='{}', subtipo='{}', "
                    "superficie='{}', angulo_inclinacion={}, "
                    "posicion1={}, posicion2={}, cota_a={}, cota_b={}".format(
                        _json_get_value(js, "tipo", "type"),
                        _json_get_value(js, "subtipo", "subtype"),
                        _json_get_value(js, "superficie", "surface"),
                        _json_get_value(
                            js,
                            "angulo_inclinacion",
                            "inclination_angle_deg",
                            "inclination_angel_deg",
                        ),
                        _json_get_value(js, "posicion1", "position1"),
                        _json_get_value(js, "posicion2", "position2"),
                        _json_get_value(js, "cota_a", "height_a"),
                        _json_get_value(js, "cota_b", "height_b", "length_b"),
                    )
                )
            except Exception as exc:
                print(f"[Soportes] Aviso: no se pudo loguear soporte JSON: {exc}")

            support = SupportModel(build_ele, doc)

            # Configurar tipo/subtipo según JSON (si es posible)
            try:
                support.apply_json_definition(js, caller_installation=caller_installation)
            except Exception as exc:
                print(
                    f"[Soportes] Aviso: error aplicando configuración JSON al soporte: {exc}"
                )

            # Ajustar geometría a partir de los valores del JSON:
            # - LEN_X_HORIZONTAL se toma de cota_b (menos 6 mm).
            # - HEIGHT_VERTICAL se toma de cota_a.
            try:
                cota_b = _json_get_value(js, "cota_b", "height_b", "length_b", default=0.0)
                if cota_b and cota_b > 0.0:
                    length_mm = float(cota_b) - 6.0  # descuento de 6 mm
                    if length_mm > 0.0:
                        support.set_length(length_mm)

                cota_a = _json_get_value(js, "cota_a", "height_a", default=0.0)
                if cota_a and cota_a > 0.0 and support.type_support != "Cinta":
                    support.param["HEIGHT_VERTICAL"] = float(cota_a)
            except Exception as exc:
                print(
                    f"[Soportes] Aviso: error aplicando longitud/altura desde JSON, se mantienen valores por defecto: {exc}"
                )

            # Construir geometría local del soporte
            local_models = support.build()

            # Orientar y posicionar el soporte según posicion1 (inicio) y posicion2 (fin)
            try:
                p1 = _json_get_value(js, "posicion1", "position1")
                p2 = _json_get_value(js, "posicion2", "position2")

                if p1 is not None and p2 is not None:
                    x1, y1, z1 = float(p1[0]), float(p1[1]), float(p1[2])
                    x2, y2, z2 = float(p2[0]), float(p2[1]), float(p2[2])

                    # Vector 3D entre posicion1 y posicion2
                    dx = x2 - x1
                    dy = y2 - y1
                    dz = z2 - z1

                    # Elevar Z por cota_a (alto del soporte).
                    # Si cota_a es 0 o no está definido, usar 110 mm como valor por defecto.
                    _DEFAULT_COTA_A = 110.0
                    cota_a_val = round(float(_json_get_value(js, "cota_a", "height_a", default=0.0) or 0.0), 2)
                    if cota_a_val < 0.01:
                        cota_a_val = _DEFAULT_COTA_A
                    # Restar 1.5 mm (0.00150 m) para compensar el offset de centrado interno del brep.
                    z1 += cota_a_val - 1.5

                    # Si el vector es muy pequeño, usamos eje X por defecto
                    is_zero_vec = abs(dx) < 1e-6 and abs(dy) < 1e-6 and abs(dz) < 1e-6
                    if is_zero_vec:
                        dx, dy, dz = 1.0, 0.0, 0.0
                    direction_vec = AllplanGeometry.Vector3D(dx, dy, dz)

                    # Patrón oficial Allplan: SetRotation luego Translate (post-multiplica).
                    # Garantiza "primero rotar, luego trasladar" con el convenio de Allplan.
                    placement_mat = AllplanGeometry.Matrix3D()
                    placement_mat.SetRotation(
                        AllplanGeometry.Vector3D(1.0, 0.0, 0.0), direction_vec
                    )

                    # Rotación adicional por ángulo de inclinación (roll sobre el eje de dirección).
                    inclination_deg = _json_get_value(
                        js,
                        "angulo_inclinacion",
                        "inclination_angle_deg",
                        "inclination_angel_deg",
                    )
                    if (
                        inclination_deg is not None
                        and abs(float(inclination_deg)) > 1e-6
                    ):
                        axis_line = AllplanGeometry.Line3D(
                            AllplanGeometry.Point3D(0.0, 0.0, 0.0),
                            AllplanGeometry.Point3D(dx, dy, dz),
                        )
                        mat_roll = AllplanGeometry.Matrix3D()
                        mat_roll.SetRotation(
                            axis_line,
                            AllplanGeometry.Angle.FromDeg(float(inclination_deg)),
                        )
                        # Post-multiplicar: aplica roll después de la rotación de dirección
                        placement_mat = placement_mat * mat_roll

                    # Trasladar al punto inicial (Translate post-multiplica)
                    placement_mat.Translate(AllplanGeometry.Vector3D(x1, y1, z1))

                    # Aplicar la transformación a cada ModelElement3D devuelto por SupportModel
                    for elem in local_models:
                        geom = elem.GeometryObject
                        elem.GeometryObject = AllplanGeometry.Transform(
                            geom, placement_mat
                        )

            except Exception as exc:
                print(
                    f"[Soportes] Aviso: error orientando soporte según posicion1/posicion2: {exc}"
                )

            model_list.extend(local_models)

        return (model_list, [], [])

    # 2) Fallback: comportamiento clásico si no hay JSON
    support = SupportModel(build_ele, doc)
    model_list = support.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
