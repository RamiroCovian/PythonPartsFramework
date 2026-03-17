import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService
from NemAll_Python_BaseElements import LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


# Lo que sale del ComboBox → índice
MAP_TUB_POLIETILE = {
    "Fred": {"Ø20-5ML - Fred": 0, "Ø25-5ML - Fred": 1},
    "Calent": {"Ø20-5ML - Calent": 0, "Ø25-5ML - Calent": 1},
    "Retorn": {"Ø20-5ML - Retorn": 0, "Ø25-5ML - Retorn": 1},
    "MC fred": {"Ø20-5ML - MC fred": 0, "Ø25-5ML - MC fred": 1},
    "MC calent": {"Ø20-5ML - MC calent": 0, "Ø25-5ML - MC calent": 1},
}

COMBO_NAME_BY_WATER = {
    "Fred": "TipoTubPolietileFred",
    "Calent": "TipoTubPolietileCalent",
    "Retorn": "TipoTubPolietileRetorn",
    "MC fred": "TipoTubPolietileMCfred",
    "MC calent": "TipoTubPolietileMCcalent",
}

# Parámetros geométricos por tipo de agua + índice
PARAMS = {
    "Fred": [
        # 0 -> Ø20-5ML - Fred
        {
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 7,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAF-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_diametre": "20",
            "pmp_nom": "TAF-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        # 1 -> Ø25-5ML - Fred
        {
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 7,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAF-25.",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "5625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_003",
            "pmp_diametre": "25",
            "pmp_area": "5625",
            "pmp_nom": "TAF-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
    "Calent": [
        # 0 -> Ø20-5ML - Calent
        {
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 6,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAC-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_002",
            "pmp_diametre": "20",
            "pmp_nom": "TAC-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        {  # 1 -> Ø25-5ML - Calent
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 6,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAC-25.",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "5625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_004",
            "pmp_diametre": "25",
            "pmp_area": "5625",
            "pmp_nom": "TAC-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
    "Retorn": [
        {  # 0 -> Ø20-5ML - Retorn
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 8,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TR-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_diametre": "20",
            "pmp_nom": "TR-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        {  # 1 -> Ø25-5ML - Retorn
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 8,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TR-25.",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_diametre": "25",
            "pmp_area": "1600",
            "pmp_nom": "TR-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
    ],
    "MC fred": [
        {  # 0 -> Ø20-5ML - MC fred
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 60,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAFM-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_diametre": "20",
            "pmp_nom": "TAFM-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        {  # 1 -> Ø25-5ML - MC fred
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 60,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TAFM-25",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "5625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_003",
            "pmp_diametre": "25",
            "pmp_area": "5625",
            "pmp_nom": "TAFM-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
    "MC calent": [
        {  # 0 -> Ø20-5ML - MC calent
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 110,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TACM-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "1600",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_diametre": "20",
            "pmp_nom": "TACM-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        {  # 1 -> Ø25-5ML - MC calent
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 110,
            "LAYER_SHORT": "IS_CON_AIGUA_FAB",
            "ATTR01": "TACM-25",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "5625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_007_003",
            "pmp_diametre": "25",
            "pmp_area": "5625",
            "pmp_nom": "TACM-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
}


ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07
ATTR_PERSO_09_ID = 10009  # Atributo personalizado 09
ATTR_PERSO_14_ID = 10014  # Atributo personalizado 14


# class TubPolietileModel:
#     """Clase que representa Tub Polietilè IS"""

#     def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
#         self.doc = doc
#         # Tipo de agua
#         type_water_raw = getattr(build_ele, "TipoDeAgua", None)
#         type_water_val = getattr(type_water_raw, "value", type_water_raw)
#         type_water = str(type_water_val) if type_water_val is not None else "Fred"

#         if type_water not in PARAMS:
#             type_water = "Fred"

#         self.type_water = type_water

#         # Nombre del combo según el tipo de agua
#         combo_param_name = COMBO_NAME_BY_WATER.get(self.type_water)
#         combo_raw = getattr(build_ele, combo_param_name, None)

#         combo_val = getattr(combo_raw, "value", combo_raw)
#         combo_str = str(combo_val) if combo_val is not None else ""

#         # Mapa texto del combo → índice
#         map_for_water = MAP_TUB_POLIETILE.get(self.type_water, {})
#         idx = map_for_water.get(combo_str, 0)

#         # Parámetros elegidos
#         self.param = dict(PARAMS[self.type_water][idx])


class TubPolietileModel:
    """Clase que representa Tub Polietilè IS"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc

        # --- 1) Tipo de agua ---

        # 1.a) Intentar leer TipoDeAgua (uso manual del PythonPart)
        type_water = None
        type_water_raw = getattr(build_ele, "TipoDeAgua", None)
        if type_water_raw is not None:
            type_water_val = getattr(type_water_raw, "value", type_water_raw)
            if type_water_val is not None:
                type_water = str(type_water_val)

        # 1.b) Si no hay TipoDeAgua, intentar con el RadioButtonGroup "Fontaneria" (polilínea)
        if not type_water:
            font_raw = getattr(build_ele, "Fontaneria", None)
            font_val = getattr(font_raw, "value", font_raw)
            try:
                font_int = int(font_val)
            except Exception:
                font_int = None

            if font_int == 0:
                type_water = "Fred"  # Agua fría
            elif font_int == 1:
                type_water = "Calent"  # Agua caliente
            elif font_int == 2:
                type_water = "Retorn"  # Agua de retorno
            elif font_int == 3:
                type_water = "MC fred"  # Agua de MC fred
            elif font_int == 4:
                type_water = "MC calent"  # Agua de MC calent
            else:
                type_water = "Fred"

        # 1.c) Seguridad: si no está en PARAMS, caer a Fred
        if type_water not in PARAMS:
            type_water = "Fred"

        self.type_water = type_water

        # --- 2) Selección de diámetro: modo por defecto = COMBO (uso manual) ---
        idx = 0  # índice por defecto

        combo_param_name = COMBO_NAME_BY_WATER.get(self.type_water)
        if combo_param_name:
            combo_raw = getattr(build_ele, combo_param_name, None)
            combo_val = getattr(combo_raw, "value", combo_raw)
            combo_str = str(combo_val) if combo_val is not None else ""

            map_for_water = MAP_TUB_POLIETILE.get(self.type_water, {})
            idx = map_for_water.get(combo_str, 0)

        # --- 3) Si existe DiametroAplicar (modo polilínea), OVERRIDE del índice ---
        diametro_attr = getattr(build_ele, "DiametroAplicar", None)
        if diametro_attr is not None:
            diam_val = getattr(diametro_attr, "value", diametro_attr)
            try:
                diam_int = int(diam_val)
            except Exception:
                diam_int = None

            if diam_int is not None:
                if diam_int == 20:
                    idx = 0
                elif diam_int == 25:
                    idx = 1
                elif diam_int == 32:
                    idx = min(2, len(PARAMS[self.type_water]) - 1)

        # --- 4) Proteger por si el idx se va de rango ---
        max_idx = len(PARAMS[self.type_water]) - 1
        if idx > max_idx:
            idx = max_idx
        if idx < 0:
            idx = 0

        # --- 5) Parámetros elegidos (copia, no referencia) ---
        self.param = dict(PARAMS[self.type_water][idx])

        # Common properties
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        self.common_props = common_properties

        # Asigno el Layer desde el short name
        short_name = self.param.get("LAYER_SHORT", None)
        if short_name:
            layer_id = LayerService.GetIDByShortName(short_name, self.doc)
            if layer_id > 0:
                self.common_props.Layer = layer_id

        # Desactivo el color de layer
        common_properties.ColorByLayer = False

        common_properties.Color = int(self.param["COLOR"])

        # IDs de atributos por nombre tal cual en Allplan
        self.attr01_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 01"
        )
        self.attr02_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 02"
        )
        self.attr07_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 07"
        )
        self.attr09_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 09"
        )
        self.attr14_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 14"
        )
        self.attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
        self.attr_pmp_CARTICULO_id = AttributeService.GetAttributeID(
            self.doc, "pmp_CARTICULO"
        )
        self.attr_pmp_diametre_id = AttributeService.GetAttributeID(
            self.doc, "pmp_diametre"
        )
        self.attr_pmp_nom_id = AttributeService.GetAttributeID(self.doc, "pmp_nom")
        self.attr_pmp_seccio_id = AttributeService.GetAttributeID(
            self.doc, "pmp_seccio"
        )
        self.attr_pmp_densitat_lineal_id = AttributeService.GetAttributeID(
            self.doc, "pmp_densitat_lineal"
        )
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )

    def set_length(self, length_mm: float):
        """
        Permite que la polilínea ajuste el largo del tubo.
        Cambiamos solo LEN_X, que es la longitud del cubo.
        """
        try:
            length_mm = float(length_mm)
        except Exception:
            return

        if length_mm <= 0:
            return

        self.param["LEN_X"] = length_mm
        self.custom_length = length_mm

    def _create_attributes(self):
        """Armo los atributos personalizados segun el tipo de Te."""
        p = self.param
        attrs = []

        if self.attr01_id and self.attr01_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr01_id, p["ATTR01"])
            )
        if self.attr02_id and self.attr02_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr02_id, p["ATTR02"])
            )
        if self.attr07_id and self.attr07_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr07_id, p["ATTR07"])
            )
        if self.attr09_id and self.attr09_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr09_id, p["ATTR09"])
            )
        if self.attr14_id and self.attr14_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr14_id, p["ATTR14"])
            )
        if self.attr_6_cc_is_id and self.attr_6_cc_is_id > 0 and "6_CC_IS" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr_6_cc_is_id, p["6_CC_IS"])
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

        if (
            self.attr_pmp_diametre_id
            and self.attr_pmp_diametre_id > 0
            and "pmp_diametre" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_diametre_id, p["pmp_diametre"]
                )
            )

        if self.attr_pmp_nom_id and self.attr_pmp_nom_id > 0 and "pmp_nom" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr_pmp_nom_id, p["pmp_nom"])
            )

        if (
            self.attr_pmp_seccio_id
            and self.attr_pmp_seccio_id > 0
            and "pmp_seccio" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_seccio_id, p["pmp_seccio"]
                )
            )

        # ---- nuevo numérico (icono 0,0 en la paleta) ----
        if (
            self.attr_pmp_densitat_lineal_id
            and self.attr_pmp_densitat_lineal_id > 0
            and "pmp_densitat_lineal" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeDouble(
                    self.attr_pmp_densitat_lineal_id, float(p["pmp_densitat_lineal"])
                )
            )

        if (
            self.attr_object_name_id
            and self.attr_object_name_id > 0
            and "object_name" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_object_name_id, p["object_name"]
                )
            )

        if not attrs:
            return None

        attr_set = AllplanBaseElements.AttributeSet(attrs)
        return AllplanBaseElements.Attributes([attr_set])

    def _create_tub_polietile_brep(self, param: dict):
        """Tub Polietilè externo (simple: un paralelepípedo)"""
        # Usar el largo real si está disponible en build_ele
        length = getattr(self, "custom_length", None)
        if length is None:
            length = float(param["LEN_X"])
        width = float(param["LEN_Y"])
        height = float(param["HEIGHT"])

        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        brep = AllplanGeometry.BRep3D.CreateCuboid(placement, length, width, height)
        return brep

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_brep = self._create_tub_polietile_brep(self.param)

        return outer_brep

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        # Si el objeto build_ele tiene Largo, úsalo para el largo del tubo
        custom_length = getattr(self, "custom_length", None)
        if custom_length is None and hasattr(self, "build_ele"):
            custom_length = getattr(self.build_ele, "Largo", None)
        self.custom_length = (
            custom_length if custom_length is not None else float(self.param["LEN_X"])
        )

        brep = self._create_brep()
        model_ele = AllplanBasisElements.ModelElement3D(self.common_props, brep)
        attributes = self._create_attributes()
        model_ele.SetAttributes(attributes)
        return [model_ele]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    tub_polietile = TubPolietileModel(build_ele, doc)
    model_list = tub_polietile.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
