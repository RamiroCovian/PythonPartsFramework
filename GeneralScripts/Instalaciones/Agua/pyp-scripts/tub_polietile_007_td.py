import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService
from NemAll_Python_BaseElements import LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


# Parámetros geométricos por tipo de agua + índice
PARAMS = {
    "Fred": [
        # 0 -> Ø20-5ML - Fred
        {
            # Outer
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 5,
            "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
            "Material": "CAVITAT",  # Material para outer_model
            # Inner
            "LEN_X_INNER": 200.0,
            "LEN_Y_INNER": 20.0,
            "HEIGHT_INNER": 20.0,
            "INNER_COLOR": 7,
            "SPACE": 10.0,
            "LAYER_SHORT_INNER": "KN_AIGUA",
            "ATTR01": "TAF-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "400",
            "ATTR14": "ARMAFLEX",
            "pmp_pare": "",
            "object_name": "Paralelepípedo",
            "pmp_area": "400",
            "pmp_CARTICULO": "KN01_007_001",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
            "pmp_diametre": "20",
            "pmp_nom": "TAF-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
        },
        # 1 -> Ø25-5ML - Fred
        {
            # Outer
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 128,
            "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
            "Material": "CAVITAT",  # Material para outer_model
            # Inner
            "LEN_X_INNER": 200.0,
            "LEN_Y_INNER": 25.0,
            "HEIGHT_INNER": 25.0,
            "INNER_COLOR": 7,
            "LAYER_SHORT_INNER": "KN_AIGUA",
            "SPACE": 25.0,
            "ATTR01": "TAF-25.",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "pmp_pare": "",
            "pmp_area": "625",
            "pmp_CARTICULO": "KN01_007_003",
            "pmp_diametre": "25",
            "pmp_nom": "TAF-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
    "Calent": [
        # 0 -> Ø20-5ML - Calent
        {
            # Outer
            "LEN_X": 200.0,
            "LEN_Y": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 5,
            "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
            "Material": "CAVITAT",  # Material para outer_model
            # Inner
            "LEN_X_INNER": 200.0,
            "LEN_Y_INNER": 20.0,
            "HEIGHT_INNER": 20.0,
            "INNER_COLOR": 6,
            "LAYER_SHORT_INNER": "KN_AIGUA",
            "SPACE": 10.0,
            "ATTR01": "TAC-20.",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "ATTR09": "400",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "pmp_pare": "",
            "pmp_area": "400",
            "pmp_CARTICULO": "KN01_007_002",
            "pmp_diametre": "20",
            "pmp_nom": "TAC-20. +ARMAFLEX",
            "pmp_seccio": "Ø20",
            "pmp_densitat_lineal": 0.1050,  # NUMERICO
        },
        {  # 1 -> Ø25-5ML - Calent
            # Outer
            "LEN_X": 200.0,
            "LEN_Y": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 128,
            "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
            "Material": "CAVITAT",  # Material para outer_model
            # Inner
            "LEN_X_INNER": 200.0,
            "LEN_Y_INNER": 25.0,
            "HEIGHT_INNER": 25.0,
            "INNER_COLOR": 6,
            "LAYER_SHORT_INNER": "KN_AIGUA",
            "SPACE": 25.0,
            "ATTR01": "TAC-25.",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "ATTR09": "625",
            "ATTR14": "ARMAFLEX",
            "object_name": "Paralelepípedo",
            "pmp_pare": "",
            "pmp_area": "625",
            "pmp_CARTICULO": "KN01_007_004",
            "pmp_diametre": "25",
            "pmp_nom": "TAC-25. +ARMAFLEX",
            "pmp_seccio": "Ø25",
            "pmp_densitat_lineal": 0.1600,  # NUMERICO
        },
    ],
}

# Ver que opcion es mejor, una lista de 2 diccionarios?
MAP_TUB_POLIETILE = {
    "Fred": {"Ø20-5ML - Fred": 0, "Ø25-5ML - Fred": 1, "Ø32-5ML - Fred": 2},
    "Calent": {"Ø20-5ML - Calent": 0, "Ø25-5ML - Calent": 1, "Ø32-5ML - Calent": 2},
}

COMBO_NAME_BY_WATER = {
    "Fred": "TipoTubPolietileFred",
    "Calent": "TipoTubPolietileCalent",
}

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07
ATTR_PERSO_09_ID = 10009  # Atributo personalizado 09
ATTR_PERSO_14_ID = 10014  # Atributo personalizado 14


class TubPolietileTDModel:
    """Clase que representa Tub Polietilè TD"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc

        # 1) Tipo de agua

        # 1.a) Intentar leer TipoDeAguaTD (nuevo nombre desde polilínea)
        type_water = None
        type_water_raw = getattr(build_ele, "TipoDeAguaTD", None)
        if type_water_raw is not None:
            type_water_val = getattr(type_water_raw, "value", type_water_raw)
            if type_water_val is not None:
                type_water = str(type_water_val).strip()

        # 1.a.1) Fallback: Intentar leer TipoDeAgua (compatibilidad con uso manual del PythonPart)
        if not type_water:
            type_water_raw = getattr(build_ele, "TipoDeAgua", None)
            if type_water_raw is not None:
                type_water_val = getattr(type_water_raw, "value", type_water_raw)
                if type_water_val is not None:
                    type_water = str(type_water_val).strip()

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

        # 1.c) Seguridad: si no está en PARAMS, caer a Fred
        if type_water not in PARAMS:
            print(
                f"[TubPolietileTD] Warning: Tipo de agua '{type_water}' no válido, usando 'Fred' por defecto"
            )
            type_water = "Fred"

        self.type_water = type_water
        print(f"[TubPolietileTD] Tipo de agua seleccionado: '{self.type_water}'")

        # Selección de diámetro: modo por defecto = COMBO (uso manual)
        idx = 0  # índice por defecto

        combo_param_name = COMBO_NAME_BY_WATER.get(self.type_water)
        if combo_param_name:
            combo_raw = getattr(build_ele, combo_param_name, None)
            combo_val = getattr(combo_raw, "value", combo_raw)
            combo_str = str(combo_val) if combo_val is not None else ""

            map_for_water = MAP_TUB_POLIETILE.get(self.type_water, {})
            idx = map_for_water.get(combo_str, 0)

        # Si existe DiametroAplicar (modo polilínea), OVERRIDE del índice
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

        # Proteger por si el idx se va de rango
        max_idx = len(PARAMS[self.type_water]) - 1
        if idx > max_idx:
            idx = max_idx
        if idx < 0:
            idx = 0

        # Parámetros elegidos (copia, no referencia)
        self.param = dict(PARAMS[self.type_water][idx])

        # Common properties
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        self.common_props = common_properties

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
        self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")
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
        self.attr_pmp_area_id = AttributeService.GetAttributeID(self.doc, "pmp_area")
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )
        self.attr_material_id = AttributeService.GetAttributeID(self.doc, "Material")

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
        """Armo los atributos personalizados segun el tipo de Tub."""
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

        if self.attr_pmp_area_id and self.attr_pmp_area_id > 0 and "pmp_area" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_area_id, p["pmp_area"]
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

        # nuevo numérico (icono 0,0 en la paleta)
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

    def _create_outer_attributes(self):
        """Crea atributos solo para el outer_model (solo Material)."""
        p = self.param
        attrs = []

        if self.attr_material_id and self.attr_material_id > 0 and "Material" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_material_id, p["Material"]
                )
            )

        if not attrs:
            return None

        attr_set = AllplanBaseElements.AttributeSet(attrs)
        return AllplanBaseElements.Attributes([attr_set])

    def _create_tub_polietile_brep(self, param: dict):
        """Tub Polietilè externo"""
        # Uso el largo real si está disponible en build_ele
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
        outer_core = None
        inner_core = None
        inner_param = {
            "LEN_X": self.param["LEN_X_INNER"],
            "LEN_Y": self.param["LEN_Y_INNER"],
            "HEIGHT": self.param["HEIGHT_INNER"],
            "COLOR": self.param["INNER_COLOR"],
        }
        outer_core = self._create_tub_polietile_brep(self.param)
        inner_core = self._create_tub_polietile_brep(inner_param)
        # CENTRO EL INNER DENTRO DEL OUTER
        # Distancia entre outer e inner
        dx = 0
        dy = self.param["SPACE"]
        dz = self.param["SPACE"]
        mat_t = AllplanGeometry.Matrix3D()
        mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
        inner_core = AllplanGeometry.Transform(inner_core, mat_t)
        # No hacemos MakeUnion, retornamos separados para aplicar layers diferentes
        return outer_core, inner_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico del tubo para centrarlo (X, Y, Z)
        # Para X usamos el largo total del tubo (que puede haber sido modificado con set_length)
        length_x = getattr(self, "custom_length", None)
        if length_x is None:
            length_x = float(p.get("LEN_X", 0.0))
        half_x = length_x / 2.0
        # Para Y y Z usamos las dimensiones del outer (el elemento más grande)
        half_y = float(p.get("LEN_Y", 0.0)) / 2.0
        half_z = float(p.get("HEIGHT", 0.0)) / 2.0

        # Transformación para centrar el tubo en el origen
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(0.0, -half_y, -half_z))

        # Aplicar la transformación a ambos breps
        outer_brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)
        inner_brep_centered = AllplanGeometry.Transform(inner_brep, mat_center)

        model_list = []

        # Outer
        if outer_brep_centered is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_props.ColorByLayer = False  # Desactivar color por layer

            # Asignar layer al outer_model
            outer_layer_short = p.get("LAYER_SHORT_OUTER", None)
            if outer_layer_short:
                outer_layer_id = LayerService.GetIDByShortName(
                    outer_layer_short, self.doc
                )
                if outer_layer_id > 0:
                    outer_props.Layer = outer_layer_id
                    # Reasignar color después de asignar layer para asegurar que se mantenga
                    outer_props.Color = p["COLOR"]
                    outer_props.ColorByLayer = False

            outer_model = AllplanBasisElements.ModelElement3D(
                outer_props, outer_brep_centered
            )

            # Atributos para outer_model (solo Material)
            outer_attributes = self._create_outer_attributes()
            if outer_attributes:
                outer_model.SetAttributes(outer_attributes)

            model_list.append(outer_model)

        # Inner
        if inner_brep_centered is not None:
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p["INNER_COLOR"]
            inner_props.ColorByLayer = False  # Desactivar color por layer

            # Asignar layer al inner_model
            inner_layer_short = p.get("LAYER_SHORT_INNER", None)
            if inner_layer_short:
                inner_layer_id = LayerService.GetIDByShortName(
                    inner_layer_short, self.doc
                )
                if inner_layer_id > 0:
                    inner_props.Layer = inner_layer_id
                    # Reasignar color después de asignar layer para asegurar que se mantenga
                    inner_props.Color = p["INNER_COLOR"]
                    inner_props.ColorByLayer = False

            inner_model = AllplanBasisElements.ModelElement3D(
                inner_props, inner_brep_centered
            )

            # Atributos para inner_model (todos los atributos excepto Material)
            inner_attributes = self._create_attributes()
            if inner_attributes:
                inner_model.SetAttributes(inner_attributes)

            model_list.append(inner_model)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    tub_polietile = TubPolietileTDModel(build_ele, doc)
    model_list = tub_polietile.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
