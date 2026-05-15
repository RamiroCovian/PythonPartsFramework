import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonPart (simplificada)."""
    tram_recte = TramRecteModel(build_ele, script_object_data)
    model_ele_list = tram_recte.build()

    return model_ele_list, []

def create_script_object(build_ele, script_object_data):
    return TramRecteScript(build_ele, script_object_data)

PARAMS_BASE = [
    # 150x150
    {  # Outer
        "LEN_X": 200.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 200.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "150",
        "LONGITUD COND. CLIMA TRAM RECTE": "",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 200x150
    {  # Outer
        "LEN_X": 250.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 250.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "200",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 250x150
    {  # Outer
        "LEN_X": 300.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 300.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "250",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 300x150
    {  # Outer
        "LEN_X": 350.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 350.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "300",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 350x150
    {  # Outer
        "LEN_X": 400.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 400.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "350",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 400x150
    {  # Outer
        "LEN_X": 450.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 450.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "400",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 450x150
    {  # Outer
        "LEN_X": 500.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 500.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "450",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 500x150
    {  # Outer
        "LEN_X": 550.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 550.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "500",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 550x150
    {  # Outer
        "LEN_X": 600.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 600.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "550",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 600x150
    {  # Outer
        "LEN_X": 650.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 650.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "600",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 650x150
    {  # Outer
        "LEN_X": 700.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 700.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "650",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 700x150
    {  # Outer
        "LEN_X": 750.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 750.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "700",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
    # 750x150
    {  # Outer
        "LEN_X": 800.0,
        "LEN_Y": 1150.0,
        "HEIGHT": 200.0,
        "COLOR": 207,
        # Caps
        "CAP_ARM_X": 800.0,
        "CAP_ARM_Y": 25.0,
        "CAP_HEIGHT": 199.0,
        # Arrow
        "ARROW_COLOR": 0,
        # atributos
        "ALT": "150",
        "AMPLE": "750",
        "LONGITUD COND. CLIMA TRAM RECTE": "1199",
        "TIPUS DE PEÇA": "TRAM RECTE",
        "WARNING TRAM RECTE": "OK",
        "NUMERO PEÇA": "",  # Numero de pieza
    },
]

# Estructura de parámetros por tipo
# Todos los tipos comparten los mismos parámetros geométricos
PARAMS = {
    "Retorn": PARAMS_BASE,
    "Impulsió": PARAMS_BASE,
    "Retorn Amb Tapa": PARAMS_BASE,
    "Impulsió Amb Tapa": PARAMS_BASE,
}

# Mapeo del tamaño (string) a índice en la lista de parámetros
MAP_TRAM_RECTE_SIZE = {
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

COMBO_NAME_BY_TRAM = {
    "Retorn": "TypeTramRecteRetorn",
    "Impulsió": "TypeTramRecteImpulsió",
    "Retorn Amb Tapa": "TypeTramRecteRetornAmbTapa",
    "Impulsió Amb Tapa": "TypeTramRecteImpulsióAmbTapa",
}

# Normalización de nombres (maneja variantes sin acentos y typos comunes)
TRAM_TYPE_NORMALIZATION = {
    "retorn": "Retorn",
    "impulsio": "Impulsió",
    "implusio": "Impulsió",
    "retorn amb tapa": "Retorn Amb Tapa",
    "impulsio amb tapa": "Impulsió Amb Tapa",
    "implusio amb tapa": "Impulsió Amb Tapa",
}

# Colores de la flecha según el tipo
# Retorn y Retorn Amb Tapa → 65
# Impulsió e Impulsió Amb Tapa → 8
ARROW_COLOR_BY_TRAM_TYPE = {
    "Retorn": 65,
    "Retorn Amb Tapa": 65,
    "Impulsió": 8,
    "Impulsió Amb Tapa": 8,
}

# Diccionarios de atributos por tipo de tramo
ATTR_VALUES_BY_TRAM_TYPE = {
    "Retorn": {
        "TAPA": "-",
    },
    "Impulsió": {
        "TAPA": "-",
    },
    "Retorn Amb Tapa": {
        "TAPA": "TAPA RETORN",
    },
    "Impulsió Amb Tapa": {
        "TAPA": "TAPA IMPULSIÓ",
    },
}

# IDs fijos de atributos (usar si GetAttributeID no encuentra el atributo)
# Si conoces el ID del atributo en Allplan, puedes agregarlo aquí
# Ejemplo: ATTR_LONGITUD_FIXED_ID = 1234  # Reemplazar con el ID real
ATTR_LONGITUD_FIXED_ID = None  # Cambiar a un número si conoces el ID del atributo


def _normalize_tram_type(type_tram: str) -> str:
    if not type_tram:
        return ""
    text = str(type_tram).strip().lower()
    replacements = {
        "á": "a", "à": "a", "é": "e", "è": "e", "í": "i",
        "ï": "i", "ó": "o", "ò": "o", "ú": "u", "ü": "u"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return TRAM_TYPE_NORMALIZATION.get(text, type_tram)



# --- Mantenemos la lógica de negocio en la clase Model ---

class TramRecteModel:
    FLECHA_FACTOR_LARGO, FLECHA_OFFSET_Z, FLECHA_DIST_ANILLO = 0.7, 0.5, 30.0
    FLECHA_LARGO_FIJO = 140.0
    FLECHA_ANCHO_FIJO = 60.0
    CAP_DEPTH_MM = 25.0  # Hendidura/tapa fija en entrada y salida

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        self.build_ele = build_ele

        # 1) Leer tipo
        type_tram_raw = getattr(build_ele, "TypeTramRecte", None)
        type_tram_val = getattr(type_tram_raw, "value", type_tram_raw)
        type_tram = _normalize_tram_type(str(type_tram_val) if type_tram_val else None) # type: ignore

        # Fallback para uso desde polilíneas (no existe TypeTramRecte en el pyp base)
        # - InstallationType suele venir como "IMPULSION"/"RETORN"
        if not type_tram:
            inst_type_raw = getattr(build_ele, "InstallationType", None)
            inst_type_val = getattr(inst_type_raw, "value", inst_type_raw)
            inst_type = str(inst_type_val).strip().lower() if inst_type_val is not None else ""
            if inst_type in ["impulsion", "impulsio", "impulsió"]:
                type_tram = "Impulsió"
            elif inst_type == "retorn":
                type_tram = "Retorn"

        if type_tram not in PARAMS:
            type_tram = "Retorn"
        self.type_tram = type_tram

        # 2) Leer tamaño e índice
        idx = 0
        # Prioridad: si existe DiameterType (paleta de polilínea), usarlo SIEMPRE.
        diam_raw = getattr(build_ele, "DiameterType", None)
        diam_val = getattr(diam_raw, "value", diam_raw) if diam_raw is not None else None
        diam_key = str(diam_val).strip() if diam_val is not None else ""
        if diam_key:
            idx = MAP_TRAM_RECTE_SIZE.get(diam_key, 0)
        else:
            # Fallback: usar los combos propios del PythonPart Tram_recte si están disponibles
            combo_param_name = COMBO_NAME_BY_TRAM.get(self.type_tram)
            if combo_param_name:
                combo_raw = getattr(build_ele, combo_param_name, None)
                combo_val = getattr(combo_raw, "value", combo_raw) if combo_raw is not None else None
                combo_key = str(combo_val).strip() if combo_val is not None else ""
                if combo_key:
                    idx = MAP_TRAM_RECTE_SIZE.get(combo_key, 0)

        # Log para verificar uso desde paleta (InstallationType + DiameterType)
        _src = "paleta" if diam_key else "combo PythonPart"
        print(f"[Tram_recte] tipo={self.type_tram} diametro='{diam_key or 'N/A'}' idx={idx} (desde {_src})")

        # 3) Validar rango y obtener parámetros
        params_list = PARAMS.get(self.type_tram, PARAMS["Retorn"])
        idx = max(0, min(idx, len(params_list) - 1))

        self.param = dict(params_list[idx])
        self.size_idx = idx

        # 4) Colores y atributos base
        self.param["ARROW_COLOR"] = ARROW_COLOR_BY_TRAM_TYPE.get(self.type_tram, 0)
        attr_values = ATTR_VALUES_BY_TRAM_TYPE.get(self.type_tram, {})
        self.param.update(attr_values)

        # 5) Propiedades comunes
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param.get("COLOR", 1))
        self.common_props = common_properties

    def set_length(self, length_mm: float):
        """
        Permite que la polilínea ajuste el largo del tramo.
        Cambiamos solo LEN_X o ARM_LEN_X, que es la longitud del tramo.
        """
        try:
            length_mm = float(length_mm)
        except Exception:
            return

        if length_mm <= 0:
            return

        # Para este modelo, el ancho de sección está en LEN_X.
        # El "largo del tramo" lo representamos con custom_length (y LEN_Y como valor base).
        self.param["LEN_Y"] = length_mm
        self.custom_length = length_mm

    def _add_attributes(self, attr_list):
        """Agrega atributos según el tipo de tramo."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_ample_id = AttributeService.GetAttributeID(self.doc, "AMPLE")

            # Intentar diferentes variaciones del nombre del atributo LONGITUD
            attr_longitud_id = AttributeService.GetAttributeID(
                self.doc, "LONGITUD COND. CLIMA TRAM RECTE"
            )
            if attr_longitud_id <= 0:
                # Intentar sin puntos
                attr_longitud_id = AttributeService.GetAttributeID(
                    self.doc, "LONGITUD COND CLIMA TRAM RECTE"
                )
            if attr_longitud_id <= 0:
                # Intentar con guiones
                attr_longitud_id = AttributeService.GetAttributeID(
                    self.doc, "LONGITUD-COND-CLIMA-TRAM-RECTE"
                )
            # Si no se encuentra, usar ID fijo si está definido
            if attr_longitud_id <= 0 and ATTR_LONGITUD_FIXED_ID is not None:
                attr_longitud_id = ATTR_LONGITUD_FIXED_ID

            attr_numero_peca_id = AttributeService.GetAttributeID(
                self.doc, "NUMERO PEÇA"
            )
            attr_tapa_id = AttributeService.GetAttributeID(self.doc, "TAPA")
            attr_tipus_peca_id = AttributeService.GetAttributeID(
                self.doc, "TIPUS DE PEÇA"
            )
            attr_warning_id = AttributeService.GetAttributeID(
                self.doc, "WARNING TRAM RECTE"
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

            # LONGITUD COND. CLIMA TRAM RECTE: leer de self.param (está en PARAMS_BASE)
            # Prioridad: 1) custom_length, 2) valor de PARAMS_BASE, 3) calcular desde LEN_Y
            if attr_longitud_id and attr_longitud_id > 0:
                length = getattr(self, "custom_length", None)
                if length is not None:
                    # Si hay longitud personalizada, usar esa
                    longitud_value = str(int(length))
                else:
                    # Leer directamente de self.param (ya está en PARAMS_BASE)
                    longitud_value = self.param.get("LONGITUD COND. CLIMA TRAM RECTE")

                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_longitud_id, longitud_value # type: ignore
                    )
                )

            # NUMERO PEÇA: leer del diccionario o calcular dinámicamente
            if attr_numero_peca_id and attr_numero_peca_id > 0:
                numero_peca_value = self.param.get("NUMERO PEÇA")
                if numero_peca_value is None or numero_peca_value == "":
                    # Si no está en el diccionario o está vacío, calcular dinámicamente
                    size_keys = list(MAP_TRAM_RECTE_SIZE.keys())
                    size_str = (
                        size_keys[self.size_idx]
                        if self.size_idx < len(size_keys)
                        else ""
                    )
                    numero_peca_value = f"{self.type_tram}_{size_str}"
                else:
                    numero_peca_value = str(numero_peca_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_numero_peca_id, numero_peca_value
                    )
                )

            # TAPA: leer de self.param (ya aplicado en __init__ desde ATTR_VALUES_BY_TRAM_TYPE)
            if attr_tapa_id and attr_tapa_id > 0:
                tapa_value = self.param.get("TAPA", "-")
                if tapa_value is None:
                    tapa_value = "-"
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_tapa_id, str(tapa_value))
                )

            # TIPUS DE PEÇA: leer del diccionario de parámetros
            if attr_tipus_peca_id and attr_tipus_peca_id > 0:
                tipus_peca_value = self.param.get("TIPUS DE PEÇA")
                if tipus_peca_value is None:
                    # Si no está en el diccionario, usar el tipo de tramo
                    tipus_peca_value = self.type_tram
                else:
                    tipus_peca_value = str(tipus_peca_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(
                        attr_tipus_peca_id, tipus_peca_value
                    )
                )

            # WARNING TRAM RECTE: leer del diccionario de parámetros
            if attr_warning_id and attr_warning_id > 0:
                warning_value = self.param.get("WARNING TRAM RECTE", "")
                if warning_value is None:
                    warning_value = ""
                else:
                    warning_value = str(warning_value)
                attr_list.append(
                    AllplanBaseElements.AttributeString(attr_warning_id, warning_value)
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
            print(f"[Tram_recte] Advertencia al agregar atributos: {e}")
            import traceback

            traceback.print_exc()

    def _build_arrow(self) -> AllplanGeometry.Polygon3D:
        """Construye la flecha orientada en X y centrada en el tramo real."""
        referencia_x = getattr(self, "custom_length", float(self.param.get("LEN_Y", 200.0)))
        referencia_y = float(self.param.get("LEN_X", 200.0))
        altura_tubo = float(self.param.get("HEIGHT", 0.0))

        flecha_largo = self.FLECHA_LARGO_FIJO
        y_span = self.FLECHA_ANCHO_FIJO / 2.0
        z_flecha = altura_tubo + self.FLECHA_OFFSET_Z

        type_tram = getattr(self, "type_tram", "Retorn")
        if "Retorn" in type_tram:
            sentido = -1
        else:
            sentido = +1

        # Centrar la flecha en el largo REAL del tramo (custom_length),
        # ya que el conducto cambia de longitud según la polilínea.
        center_x = referencia_x * 0.5
        base_x = center_x - (sentido * flecha_largo * 0.5)
        y_centro = referencia_y * 0.5
        punta_x = base_x + sentido * flecha_largo

        # Puntos re-mapeados: X es largo, Y es ancho
        puntos = [
            AllplanGeometry.Point3D(base_x, y_centro - y_span, z_flecha),
            AllplanGeometry.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span, z_flecha),
            AllplanGeometry.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span * 2, z_flecha),
            AllplanGeometry.Point3D(punta_x, y_centro, z_flecha),
            AllplanGeometry.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span * 2, z_flecha),
            AllplanGeometry.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span, z_flecha),
            AllplanGeometry.Point3D(base_x, y_centro + y_span, z_flecha),
        ]
        # Cerrar polígono para asegurar contorno completo de la flecha.
        puntos.append(puntos[0])
        return AllplanGeometry.Polygon3D(puntos)

    def _create_brep(self, param: dict):
        """Tram recte orientado en X"""
        length = getattr(self, "custom_length", float(param.get("LEN_Y"))) # type: ignore
        width = float(param["LEN_X"]) # Este actúa ahora como ancho en Y
        height = float(param["HEIGHT"])

        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # INTERCAMBIO: Largo ahora es X, Ancho ahora es Y
        brep = AllplanGeometry.BRep3D.CreateCuboid(placement, length, width, height)

        cap_arm_x_val = self.CAP_DEPTH_MM # Grosor de la tapa fijo
        cap_arm_y_val = float(param.get("CAP_ARM_X", 0.0)) # Ancho de la tapa
        cap_height = float(param.get("CAP_HEIGHT", 0.0))

        if cap_arm_x_val > 0 and cap_arm_y_val > 0 and cap_height > 0:
            cap_y_offset = (width - cap_arm_y_val) / 2.0
            cap_z_offset = (height - cap_height) / 2.0

            # Cap 1: Extremo negativo de X
            cap1_origin = AllplanGeometry.Point3D(-cap_arm_x_val, cap_y_offset, cap_z_offset)
            cap1_brep = AllplanGeometry.BRep3D.CreateCuboid(AllplanGeometry.AxisPlacement3D(cap1_origin), cap_arm_x_val, cap_arm_y_val, cap_height)
            err, brep = AllplanGeometry.MakeUnion(brep, cap1_brep)

            # Cap 2: Extremo positivo de X
            cap2_origin = AllplanGeometry.Point3D(length, cap_y_offset, cap_z_offset)
            cap2_brep = AllplanGeometry.BRep3D.CreateCuboid(AllplanGeometry.AxisPlacement3D(cap2_origin), cap_arm_x_val, cap_arm_y_val, cap_height)
            err, brep = AllplanGeometry.MakeUnion(brep, cap2_brep)

        return brep

    def build(self):
        """Genera la lista de ModelElement3D centrada"""
        brep = self._create_brep(self.param)
        flecha_poly = self._build_arrow()

        length_x = getattr(self, "custom_length", float(self.param.get("LEN_Y", 200.0)))
        width_y = float(self.param.get("LEN_X", 200.0))
        height_z = float(self.param.get("HEIGHT", 0.0))

        # Centrado coherente con la nueva orientación
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-length_x / 2.0, -width_y / 2.0, -height_z / 2.0))

        brep_centered = AllplanGeometry.Transform(brep, mat_center)
        flecha_poly_centered = AllplanGeometry.Transform(flecha_poly, mat_center)

        model_ele = AllplanBasisElements.ModelElement3D(self.common_props, brep_centered)

        # Atributos (se mantiene igual)
        if self.doc:
            attr_list = []
            self._add_attributes(attr_list)
            if attr_list:
                model_ele.SetAttributes(AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet(attr_list)]))

        flecha_props = AllplanBaseElements.CommonProperties()
        flecha_props.GetGlobalProperties()
        flecha_props.Color = int(self.param.get("ARROW_COLOR", 0))
        flecha_props.ColorByLayer = False
        flecha_ele = AllplanBasisElements.ModelElement3D(flecha_props, flecha_poly_centered)

        return [model_ele, flecha_ele]

class TramRecteScript(BaseScriptObject):
    """Interfaz del Script para Allplan usando BaseScriptObject"""

    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        # Obtener el documento actual a través del input view
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        attr_list = []
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """Punto de entrada principal para la generación del elemento.

        kwargs:
            installation_type (str): "impulsion" | "retorn"
            diameter          (str): "150x150" | "200x150" | ... | "750x150"
            length            (float): longitud del segmento en mm
        """
        if "installation_type" in kwargs:
            param = getattr(self.build_ele, "InstallationType", None)
            if param is not None:
                param.value = kwargs["installation_type"]

        if "diameter" in kwargs:
            param = getattr(self.build_ele, "DiameterType", None)
            if param is not None:
                param.value = kwargs["diameter"]

        tram_model = TramRecteModel(self.build_ele, self.doc)

        length = kwargs.get("length")
        if length is None:
            build_ele_length = getattr(self.build_ele, "Length", None)
            length = getattr(build_ele_length, "value", None) if build_ele_length else None
        if length:
            tram_model.set_length(length)

        model_ele_list = tram_model.build()
        return CreateElementResult(model_ele_list)
