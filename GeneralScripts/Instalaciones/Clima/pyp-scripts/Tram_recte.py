import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


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
    text = (
        text.replace("á", "a")
        .replace("à", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("í", "i")
        .replace("ï", "i")
        .replace("ó", "o")
        .replace("ò", "o")
        .replace("ú", "u")
        .replace("ü", "u")
    )
    return TRAM_TYPE_NORMALIZATION.get(text, type_tram)


class TramRecteModel:
    """Clase que representa el tram recte"""

    # Constantes para la flecha
    FLECHA_FACTOR_LARGO, FLECHA_OFFSET_Z, FLECHA_DIST_ANILLO = 0.7, 0.5, 30.0
    # Tamaño fijo de la flecha (independiente del tamaño del tramo)
    FLECHA_LARGO_FIJO = 140.0  # Longitud fija de la flecha
    FLECHA_ANCHO_FIJO = 60.0  # Ancho fijo de la flecha (x_span * 2)
    CAP_DEPTH_MM = 25.0  # Hendidura/tapa fija en entrada y salida

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc

        # 1) Leer el tipo del combobox principal (TypeTramRecte)
        type_tram = None
        type_tram_raw = getattr(build_ele, "TypeTramRecte", None)
        if type_tram_raw is not None:
            type_tram_val = getattr(type_tram_raw, "value", type_tram_raw)
            if type_tram_val is not None:
                type_tram = str(type_tram_val)

        # Normalizar y validar el tipo (maneja Impulsió/Impulsio/Implusio)
        type_tram = _normalize_tram_type(type_tram) # type: ignore
        if type_tram not in PARAMS:
            type_tram = "Retorn"

        self.type_tram = type_tram

        # 2) Leer el tamaño del combobox específico del tipo
        idx = 0  # índice por defecto

        # Obtener el nombre del parámetro del combobox según el tipo
        combo_param_name = COMBO_NAME_BY_TRAM.get(self.type_tram)
        if combo_param_name:
            combo_raw = getattr(build_ele, combo_param_name, None)
            if combo_raw is not None:
                combo_val = getattr(combo_raw, "value", combo_raw)
                combo_str = str(combo_val) if combo_val is not None else ""

                # Mapear el tamaño (string) a índice usando MAP_TRAM_RECTE_SIZE
                idx = MAP_TRAM_RECTE_SIZE.get(combo_str, 0)

        # 3) Proteger por si el índice se va de rango
        params_list = PARAMS.get(self.type_tram, PARAMS["Retorn"])
        if idx >= len(params_list):
            idx = len(params_list) - 1
        if idx < 0:
            idx = 0

        # 4) Obtener los parámetros correspondientes
        self.param = dict(params_list[idx])  # Copia para no modificar el original
        self.size_idx = idx

        # 5) Asignar el color de la flecha según el tipo
        arrow_color = ARROW_COLOR_BY_TRAM_TYPE.get(self.type_tram, 0)  # 0 por defecto
        self.param["ARROW_COLOR"] = arrow_color

        # 6) Aplicar valores de atributos según el tipo de tramo
        attr_values = ATTR_VALUES_BY_TRAM_TYPE.get(self.type_tram, {})
        # Actualizar self.param con los valores de atributos
        for attr_key, attr_value in attr_values.items():
            self.param[attr_key] = attr_value

        # 7) Configurar propiedades comunes
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def set_length(self, length_mm: float):
        """
        Permite que la polilínea ajuste el largo del tramo.
        Cambiamos solo LEN_Y, que representa la longitud del tramo.
        """
        try:
            length_mm = float(length_mm)
        except Exception:
            return

        if length_mm <= 0:
            return

        # LEN_X es el ancho de sección. LEN_Y es la longitud del tramo.
        self.param["LEN_Y"] = length_mm

        self.custom_length = length_mm

    def _build_arrow(self) -> AllplanGeometry.Polygon3D:
        """Construye la flecha direccional con tamaño fijo."""
        # Usar LEN_X solo para centrar la flecha en X
        referencia = float(self.param.get("LEN_X", 200.0))
        altura_tubo = float(self.param.get("LEN_Y", 1150.0))
        altura_flecha = 0.1  # Factor similar a config["altura_flecha"] en el ejemplo

        # Usar tamaño fijo para la flecha (independiente del tamaño del tramo)
        flecha_largo = self.FLECHA_LARGO_FIJO
        x_span = self.FLECHA_ANCHO_FIJO / 2.0  # Mitad del ancho fijo

        # z_flecha: posicionar la flecha sobre el tubo (altura del tubo + offset)
        z_flecha = altura_tubo + referencia * altura_flecha + self.FLECHA_OFFSET_Z

        # Determinar dirección de la flecha según el tipo
        # Retorn o Retorn Amb Tapa → apunta a -Y
        # Impulsió o Impulsió Amb Tapa → apunta a +Y
        # La posición es la misma para todos (parte inferior del tramo)
        type_tram = getattr(self, "type_tram", "Retorn")
        if "Retorn" in type_tram:
            sentido = -1  # Apunta hacia atrás (-Y)
            # Retorn necesita subir 140mm en Y
            offset_y = 140.0
        else:  # Impulsió o Impulsió Amb Tapa
            sentido = +1  # Apunta hacia adelante (+Y)
            offset_y = 0.0  # Sin offset para Impulsió

        # Posición fija: siempre en la parte inferior del tramo
        base_y = self.FLECHA_DIST_ANILLO + offset_y

        # Centrar la flecha en X usando referencia, pero con tamaño fijo
        x_centro = referencia * 0.5
        punta_y = base_y + sentido * flecha_largo

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
        return AllplanGeometry.Polygon3D(puntos)

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
                        attr_longitud_id, longitud_value
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

    def _create_brep(self, param: dict):
        """Tram recte"""
        # Uso el largo real si está disponible en build_ele
        length = getattr(self, "custom_length", None)
        if length is None:
            # Algunos parámetros usan LEN_X, otros ARM_LEN_X
            length = float(param.get("LEN_Y")) # type: ignore
        width = float(param["LEN_X"])
        height = float(param["HEIGHT"])

        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # Crear el brep principal
        brep = AllplanGeometry.BRep3D.CreateCuboid(placement, width, length, height)

        # Agregar las caps si están definidas y tienen valores válidos
        cap_arm_x = float(param.get("CAP_ARM_X", 0.0))
        # Profundidad de tapa/hendidura fija: no depende del largo del tramo.
        cap_arm_y = self.CAP_DEPTH_MM
        cap_height = float(param.get("CAP_HEIGHT", 0.0))

        if cap_arm_x > 0 and cap_arm_y > 0 and cap_height > 0:
            # Centrar las caps en X y Z
            # En X: centrar respecto al largo del tubo
            cap_x_offset = (width - cap_arm_x) / 2.0
            # En Z: centrar respecto a la altura del tubo
            cap_z_offset = (height - cap_height) / 2.0

            # Cap 1: en el extremo negativo de Y (inicio del tubo)
            cap1_origin = AllplanGeometry.Point3D(
                cap_x_offset, -cap_arm_y, cap_z_offset
            )
            cap1_placement = AllplanGeometry.AxisPlacement3D(cap1_origin)
            cap1_brep = AllplanGeometry.BRep3D.CreateCuboid(
                cap1_placement, cap_arm_x, cap_arm_y, cap_height
            )

            # Unir cap1 con el brep principal
            err, brep = AllplanGeometry.MakeUnion(brep, cap1_brep)
            if err != 0:
                raise Exception(f"Error en MakeUnion(brep, cap1): código {err}")

            # Cap 2: en el extremo positivo de Y (final del tubo)
            cap2_origin = AllplanGeometry.Point3D(cap_x_offset, length, cap_z_offset)
            cap2_placement = AllplanGeometry.AxisPlacement3D(cap2_origin)
            cap2_brep = AllplanGeometry.BRep3D.CreateCuboid(
                cap2_placement, cap_arm_x, cap_arm_y, cap_height
            )

            # Unir cap2 con el brep principal
            err, brep = AllplanGeometry.MakeUnion(brep, cap2_brep)
            if err != 0:
                raise Exception(f"Error en MakeUnion(brep, cap2): código {err}")

        return brep

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        brep = self._create_brep(self.param)
        flecha_poly = self._build_arrow()

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
    tram_recte_retorn_amb_tapa = TramRecteModel(build_ele, doc)
    model_list = tram_recte_retorn_amb_tapa.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
