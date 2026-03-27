"""
TØ20|TØ25|TØ32|TØ25-20-25|TØ25-20-20|TØ25-25-20
"""

import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07

PARAMS = [
    # TØ20
    {
        # Outer
        "ARM_LEN_X": 110.0,
        "ARM_LEN_Y": 40.0,
        "HEIGHT": 40.0,
        "COLOR": 5,
        "SMALL_ARM_X": 40.0,
        "SMALL_ARM_Y": 35.0,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 54.0,
        "INNER_ARM_Y": 30.0,
        "INNER_HEIGHT": 30.0,
        "INNER_COLOR": 122,
        "SMALL_INNER_ARM_X": 30.0,
        "SMALL_INNER_ARM_Y": 12.0,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Caps
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 30.0,
        "TOP_CAP_HEIGHT": 31.0,
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 30.0,
        "LEFT_CAP_HEIGHT": 31.0,
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 31.0,
        # Dif Outer/Inner
        "SPACE": 5.0,
        # Attrs
        "ATTR01": "TØ20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "object_name": "T20",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_001",
        "pmp_diametre": "Ø20",
        "pmp_nom": "TØ20",
        "pmp_seccio": "Ø20",
        "pmp_pes_unitari": 0.1470,  # numérico
        "Material": "CAVITAT",  # Material para outer_model
    },
    # TØ25
    {
        # Outer
        "ARM_LEN_X": 155.0,
        "ARM_LEN_Y": 75.0,
        "HEIGHT": 75.0,
        "COLOR": 128,
        "SMALL_ARM_X": 75.0,
        "SMALL_ARM_Y": 40.0,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 69.0,
        "INNER_ARM_Y": 35.0,
        "INNER_HEIGHT": 35.0,
        "INNER_COLOR": 122,
        "SMALL_INNER_ARM_X": 35.0,
        "SMALL_INNER_ARM_Y": 17.0,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Caps
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 35.0,
        "TOP_CAP_HEIGHT": 36.0,
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 35.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Dif Outer/Inner
        "SPACE": 20.0,
        # Attrs
        "ATTR01": "TØ25",
        "ATTR02": "Ø25",
        "ATTR07": "20",
        "object_name": "T25",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_002",
        "pmp_diametre": "Ø25",
        "pmp_nom": "TØ25",
        "pmp_seccio": "Ø25",
        "pmp_pes_unitari": 0.1470,  # numérico
        "Material": "CAVITAT",  # Material para outer_model
    },
    # TØ32
    {
        # Outer
        "ARM_LEN_X": 0.0,
        "ARM_LEN_Y": 0.0,
        "HEIGHT": 0.0,
        "COLOR": 5,
        "SMALL_ARM_X": 0.0,
        "SMALL_ARM_Y": 0.0,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 0.0,
        "INNER_ARM_Y": 0.0,
        "INNER_HEIGHT": 0.0,
        "INNER_COLOR": 0,
        "SMALL_INNER_ARM_X": 0.0,
        "SMALL_INNER_ARM_Y": 0.0,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Caps
        "TOP_CAP_ARM_X": 0.0,
        "TOP_CAP_ARM_Y": 0.0,
        "TOP_CAP_HEIGHT": 0.0,
        "LEFT_CAP_ARM_X": 0.0,
        "LEFT_CAP_ARM_Y": 0.0,
        "LEFT_CAP_HEIGHT": 0.0,
        "RIGHT_CAP_ARM_X": 0.0,
        "RIGHT_CAP_ARM_Y": 0.0,
        "RIGHT_CAP_HEIGHT": 0.0,
        # Dif Outer/Inner
        "SPACE": 0.0,
        # Attrs
        "ATTR01": "TØ32",
        "ATTR02": "Ø32",
        "ATTR07": "32",
        "object_name": "T32",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_003",
        "pmp_diametre": "Ø32",
        "pmp_nom": "TØ32",
        "pmp_seccio": "Ø32",
        "pmp_pes_unitari": 0.1470,  # numérico
        "Material": "CAVITAT",  # Material para outer_model
    },
    # TØ25-20-25
    {
        # Middle
        "ARM_LEN_X": 64.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 12.0,
        "LAYER_SHORT": "KN_AIGUA",
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 35.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Up Cap
        "TOP_CAP_ARM_X": 23.0,
        "TOP_CAP_ARM_Y": 30.0,
        "TOP_CAP_HEIGHT": 36.0,
        # Attrs
        "ATTR01": "TØ25-20-25",
        "ATTR02": "Ø25-Ø20-Ø25",
        "ATTR07": "25-20-25",
        "object_name": "T25-20-25",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_004",
        "pmp_diametre": "Ø25-Ø20-Ø25",
        "pmp_nom": "TØ25-20-25",
        "pmp_seccio": "Ø25-Ø20-Ø25",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # TØ25-20-20
    {
        # Middle
        "ARM_LEN_X": 59.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 17.0,
        "LAYER_SHORT": "KN_AIGUA",
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Buttom Cap
        "TOP_CAP_ARM_X": 30.0,
        "TOP_CAP_ARM_Y": 23.0,
        "TOP_CAP_HEIGHT": 36.0,
        # Attrs
        "ATTR01": "TØ25-20-20",
        "ATTR02": "Ø25-Ø20-Ø20",
        "ATTR07": "25-20-20",
        "object_name": "T25-20-20",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_005",
        "pmp_diametre": "Ø25-Ø20-Ø20",
        "pmp_nom": "TØ25-20-20",
        "pmp_seccio": "Ø25-Ø20-Ø20",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # TØ25-25-20
    {
        # Middle
        "ARM_LEN_X": 66.5,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 122,
        "SMALL_ARM_X": 35.0,
        "SMALL_ARM_Y": 17.0,
        "LAYER_SHORT": "KN_AIGUA",
        # Left Cap
        "LEFT_CAP_ARM_X": 23.0,
        "LEFT_CAP_ARM_Y": 35.0,
        "LEFT_CAP_HEIGHT": 36.0,
        # Right Cap
        "RIGHT_CAP_ARM_X": 23.0,
        "RIGHT_CAP_ARM_Y": 30.0,
        "RIGHT_CAP_HEIGHT": 36.0,
        # Buttom Cap
        "TOP_CAP_ARM_X": 35.0,
        "TOP_CAP_ARM_Y": 23.0,
        "TOP_CAP_HEIGHT": 36.0,
        # Attrs
        "ATTR01": "TØ25-25-20",
        "ATTR02": "Ø25-Ø25-Ø20",
        "ATTR07": "25-25-20",
        "object_name": "T25-25-20",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_003_006",
        "pmp_diametre": "Ø25-Ø25-Ø20",
        "pmp_nom": "TØ25-25-20",
        "pmp_seccio": "Ø25-Ø25-Ø20",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
]

MAP_TES = {
    "TØ20": 0,
    "TØ25": 1,
    "TØ32": 2,
    "TØ25-20-25": 3,
    "TØ25-20-20": 4,
    "TØ25-25-20": 5,
}


class TeTDModel:
    """Clase que representa los modelos de las diferentes Te TD"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc

        tipo_raw = getattr(build_ele, "TipoTe", None)
        tipo_val = getattr(tipo_raw, "value", tipo_raw)

        # Mapear string a índice
        self.type_te = MAP_TES.get(str(tipo_val), 0)
        self.param = PARAMS[self.type_te]

        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

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
        self.attr_pmp_CARTICULO_id = AttributeService.GetAttributeID(
            self.doc, "pmp_CARTICULO"
        )
        self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")

        self.attr_pmp_diametre_id = AttributeService.GetAttributeID(
            self.doc, "pmp_diametre"
        )
        self.attr_pmp_nom_id = AttributeService.GetAttributeID(self.doc, "pmp_nom")
        self.attr_pmp_seccio_id = AttributeService.GetAttributeID(
            self.doc, "pmp_seccio"
        )
        self.attr_pmp_pes_unitari_id = AttributeService.GetAttributeID(
            self.doc, "pmp_pes_unitari"
        )
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )
        self.attr_material_id = AttributeService.GetAttributeID(self.doc, "Material")

    def set_diameters(self, d_main_in, d_branch, d_main_out):
        """
        Ajusta el tipo de Te según los diámetros:
        - d_main_in  : tramo antes del nodo (eje principal)
        - d_branch   : rama perpendicular
        - d_main_out : tramo después del nodo (eje principal)
        """
        try:
            a = int(d_main_in)
            b = int(d_branch)
            c = int(d_main_out)
        except Exception:
            # si algo raro viene, no tocamos nada
            return

        idx = self.type_te  # valor por defecto: lo que venga de TipoTe

        # --- Casos básicos totalmente simétricos ---
        if a == 20 and b == 20 and c == 20:
            # TØ20
            idx = 0
        elif a == 25 and b == 25 and c == 25:
            # TØ25
            idx = 1

        # --- Combinaciones mixtas 20 / 25 ---
        else:
            main_pair = tuple(sorted((a, c)))
            triple_sorted = tuple(sorted((a, b, c)))

            # 25-25-20  (main 25/25, rama 20) -> type_te=3 (regla usuario)
            if main_pair == (25, 25) and b == 20:
                idx = 3

            # 25-20-25  (uno de los main es 20, rama 25) -> type_te=5 (regla usuario)
            elif b == 25 and triple_sorted == (20, 25, 25):
                idx = 5

            # 25-20-20  (uno de los main es 25, rama 20)
            elif b == 20 and triple_sorted == (20, 20, 25):
                idx = 4  # TØ25-20-20

            # Si en el futuro agregas TØ32 u otros, se suman acá.

        # Actualizar internamente el tipo
        if 0 <= idx < len(PARAMS):
            self.type_te = idx
            self.param = PARAMS[idx]
            try:
                self.common_props.Color = int(self.param["COLOR"])
            except Exception:
                pass

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
            self.attr_pmp_pes_unitari_id
            and self.attr_pmp_pes_unitari_id > 0
            and "pmp_pes_unitari" in p
        ):
            attrs.append(
                AllplanBaseElements.AttributeDouble(
                    self.attr_pmp_pes_unitari_id, float(p["pmp_pes_unitari"])
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

    def _create_te_brep(self, param: dict):
        """Te externo"""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_te < 3:
            brep_center = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )

            center_x = (param["ARM_LEN_X"] / 2) - (param["SMALL_ARM_X"] / 2)
            origin_top = AllplanGeometry.Point3D(center_x, param["ARM_LEN_Y"], 0)
            placement_top = AllplanGeometry.AxisPlacement3D(origin_top)

            brep_top = AllplanGeometry.BRep3D.CreateCuboid(
                placement_top,
                param["SMALL_ARM_X"],
                param["SMALL_ARM_Y"],
                param["HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_center, brep_top)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            return union_brep
        if self.type_te >= 3:
            brep_left = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["LEFT_CAP_ARM_X"],
                param["LEFT_CAP_ARM_Y"],
                param["LEFT_CAP_HEIGHT"],
            )
            origin_middle = AllplanGeometry.Point3D(
                param["LEFT_CAP_ARM_X"],
                0,
                0,
            )
            placement_middle = AllplanGeometry.AxisPlacement3D(origin_middle)
            brep_middle = AllplanGeometry.BRep3D.CreateCuboid(
                placement_middle,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_left, brep_middle)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            if self.type_te == 4:
                # Medidas del brep a restar
                len_x_sub = 12
                len_y_sub = 5
            elif self.type_te == 5:
                # Medidas del brep a restar
                len_x_sub = 14.5
                len_y_sub = 5

            # Brep para hacer subtraction
            origin_sub = AllplanGeometry.Point3D(
                ((param["LEFT_CAP_ARM_X"] + param["ARM_LEN_X"]) - len_x_sub),
                0,
                0,
            )
            placement_sub = AllplanGeometry.AxisPlacement3D(origin_sub)
            brep_sub = AllplanGeometry.BRep3D.CreateCuboid(
                placement_sub,
                len_x_sub,
                len_y_sub,
                param["LEFT_CAP_HEIGHT"],
            )

            err, sub_brep = AllplanGeometry.MakeSubtraction(union_brep, brep_sub)
            if err != 0:
                raise Exception(f"Error en MakeSubtraction: {err}")

            # Right Cap
            origin_right = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + param["ARM_LEN_X"]),
                len_y_sub,
                0,
            )
            placement_right = AllplanGeometry.AxisPlacement3D(origin_right)
            brep_right = AllplanGeometry.BRep3D.CreateCuboid(
                placement_right,
                param["RIGHT_CAP_ARM_X"],
                param["RIGHT_CAP_ARM_Y"],
                param["RIGHT_CAP_HEIGHT"],
            )

            err, second_union_brep = AllplanGeometry.MakeUnion(sub_brep, brep_right)
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            # Medidas del brep a restar
            x_len = 17
            y_len = 6

            # Buttom union
            origin_buttom_brep_union = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + x_len),
                -(param["LEFT_CAP_ARM_Y"] - param["SMALL_ARM_Y"] - y_len),
                0,
            )
            placement_buttom_brep_union = AllplanGeometry.AxisPlacement3D(
                origin_buttom_brep_union
            )
            brep_buttom_brep_union = AllplanGeometry.BRep3D.CreateCuboid(
                placement_buttom_brep_union,
                param["SMALL_ARM_X"],
                param["SMALL_ARM_Y"],
                param["HEIGHT"],
            )

            err, second_union_brep2 = AllplanGeometry.MakeUnion(
                second_union_brep, brep_buttom_brep_union
            )
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            # Buttom Cap
            origin_buttom_brep = AllplanGeometry.Point3D(
                (param["LEFT_CAP_ARM_X"] + 17),
                -(
                    param["LEFT_CAP_ARM_Y"]
                    - param["SMALL_ARM_Y"]
                    - y_len
                    + param["TOP_CAP_ARM_Y"]
                ),
                0,
            )
            placement_buttom_brep = AllplanGeometry.AxisPlacement3D(origin_buttom_brep)
            brep_buttom_brep = AllplanGeometry.BRep3D.CreateCuboid(
                placement_buttom_brep,
                param["TOP_CAP_ARM_X"],
                param["TOP_CAP_ARM_Y"],
                param["TOP_CAP_HEIGHT"],
            )

            err, final_brep = AllplanGeometry.MakeUnion(
                second_union_brep2, brep_buttom_brep
            )
            if err != 0:
                raise Exception(f"Error en MakeUnion del te: codigo {err}")

            return final_brep
        else:
            print("No hemos creado ese Brep todavia!.")

    def _create_te_brep_with_caps(self):
        """Te Interior + Caps"""

        if self.type_te == 3:
            # TØ25-20-25: tiene tapa arriba, no abajo
            inner_param = self.param

            origin = AllplanGeometry.Point3D(0, 0, 0)
            placement = AllplanGeometry.AxisPlacement3D(origin)

            # Cuerpo horizontal
            inner_core = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                inner_param["ARM_LEN_X"],
                inner_param["ARM_LEN_Y"],
                inner_param["HEIGHT"],
            )

            # Brazo vertical (arriba)
            center_x = (inner_param["ARM_LEN_X"] / 2.0) - (
                inner_param["SMALL_ARM_X"] / 2.0
            )
            origin_top = AllplanGeometry.Point3D(
                center_x,
                inner_param["ARM_LEN_Y"],
                0.0,
            )
            placement_top = AllplanGeometry.AxisPlacement3D(origin_top)

            brep_top = AllplanGeometry.BRep3D.CreateCuboid(
                placement_top,
                inner_param["SMALL_ARM_X"],
                inner_param["SMALL_ARM_Y"],
                inner_param["HEIGHT"],
            )

            err, inner_core = AllplanGeometry.MakeUnion(inner_core, brep_top)
            if err != 0:
                raise Exception(f"Error en MakeUnion(inner_core, top): código {err}")

        elif self.type_te >= 4:
            # Estos sí tienen BUTTOM_CAP_* → puedo reutilizar _create_te_brep
            inner_param = self.param
            inner_core = self._create_te_brep(inner_param)

        elif self.type_te < 2:
            inner_param = {
                "ARM_LEN_X": self.param["INNER_ARM_X"],
                "ARM_LEN_Y": self.param["INNER_ARM_Y"],
                "HEIGHT": self.param["INNER_HEIGHT"],
                "COLOR": self.param["INNER_COLOR"],
                "SMALL_ARM_X": self.param["SMALL_INNER_ARM_X"],
                "SMALL_ARM_Y": self.param["SMALL_INNER_ARM_Y"],
                "LEFT_CAP_ARM_X": self.param["LEFT_CAP_ARM_X"],
                "LEFT_CAP_ARM_Y": self.param["LEFT_CAP_ARM_Y"],
                "LEFT_CAP_HEIGHT": self.param["LEFT_CAP_HEIGHT"],
                "RIGHT_CAP_ARM_X": self.param["RIGHT_CAP_ARM_X"],
                "RIGHT_CAP_ARM_Y": self.param["RIGHT_CAP_ARM_Y"],
                "RIGHT_CAP_HEIGHT": self.param["RIGHT_CAP_HEIGHT"],
                "TOP_CAP_ARM_X": self.param["TOP_CAP_ARM_X"],
                "TOP_CAP_ARM_Y": self.param["TOP_CAP_ARM_Y"],
                "TOP_CAP_HEIGHT": self.param["TOP_CAP_HEIGHT"],
            }

            inner_core = self._create_te_brep(inner_param)
        else:
            print("No hemos creado ese Brep todavia!. (_create_te_brep_with_caps)")
        # --- A partir de acá, dejo tu lógica de caps casi igual ---

        # Left Cap
        cap1_origin = AllplanGeometry.Point3D(
            -(inner_param["LEFT_CAP_ARM_X"]), 0.0, 0.0
        )
        cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
        cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap1_place,
            inner_param["LEFT_CAP_ARM_X"],
            inner_param["LEFT_CAP_ARM_Y"],
            inner_param["LEFT_CAP_HEIGHT"],
        )

        err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

        # Right Cap
        cap2_origin = AllplanGeometry.Point3D(inner_param["ARM_LEN_X"], 0.0, 0.0)
        cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

        cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap2_place,
            inner_param["RIGHT_CAP_ARM_X"],
            inner_param["RIGHT_CAP_ARM_Y"],
            inner_param["RIGHT_CAP_HEIGHT"],
        )

        err, inner_with_caps2 = AllplanGeometry.MakeUnion(inner_with_cap1, cap2_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_with_cap1, cap2): código {err}")

        # Top Cap
        center_x = (inner_param["ARM_LEN_X"] / 2) - (inner_param["SMALL_ARM_X"] / 2)
        center_y = inner_param["ARM_LEN_Y"] + inner_param["SMALL_ARM_Y"]
        cap3_origin = AllplanGeometry.Point3D(center_x, center_y, 0.0)
        cap3_place = AllplanGeometry.AxisPlacement3D(cap3_origin)

        cap3_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap3_place,
            inner_param["TOP_CAP_ARM_Y"],
            inner_param["TOP_CAP_ARM_X"],
            inner_param["TOP_CAP_HEIGHT"],
        )

        # Si no hay rotación real, no hace falta transform:
        err, inner_with_caps = AllplanGeometry.MakeUnion(inner_with_caps2, cap3_local)
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(inner_with_caps2, cap3_local): código {err}"
            )

        return inner_with_caps

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_core = None
        inner_centered = None
        if self.type_te < 2:

            outer_core = self._create_te_brep(self.param)
            inner_core = self._create_te_brep_with_caps()

            # CENTRO EL INNER DENTRO DEL OUTER
            # Distancia entre outer e inner
            dx = self.param["SPACE"] + self.param["TOP_CAP_ARM_X"]
            dy = self.param["SPACE"]
            dz = self.param["SPACE"]

            mat_t = AllplanGeometry.Matrix3D()
            mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
            inner_centered = AllplanGeometry.Transform(inner_core, mat_t)

        elif self.type_te == 3:
            outer_core = self._create_te_brep_with_caps()
        elif self.type_te >= 4:
            # outer_core = self._create_te_brep_with_caps()
            outer_core = self._create_te_brep(self.param)

        else:
            print("No hemos creado este Brep todavia!. (_create_brep)")
        return outer_core, inner_centered

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico de la Te para centrarla (mismo método que Te IS)
        cap_x = float(p.get("ARM_LEN_X", 0.0))
        cap_y = float(p.get("ARM_LEN_Y", 0.0))
        cap_z = float(p.get("HEIGHT", 0.0))

        offset = (
            float(p.get("LEFT_CAP_ARM_Y", 0.0)) - float(p.get("RIGHT_CAP_ARM_Y", 0.0))
        ) / 2  # 2.5mm

        # Centrado especial para TØ25-20-20 y TØ25-25-20
        tipo_te = p.get("ATTR01", "")
        if tipo_te in ("TØ25-20-20", "TØ25-25-20"):
            # Cálculo alternativo para el centrado en X
            centro_x = float(
                p.get("RIGHT_CAP_ARM_X", 0.0)
                + float(p.get("SMALL_ARM_Y", 0.0))
                + (float(p.get("TOP_CAP_ARM_X", 0.0))) / 2
            )
            tx = -centro_x
        else:
            tx = -cap_x * 0.5
        ty = (-cap_y * 0.5) - offset
        tz = -cap_z * 0.5

        # Transformación para centrar la Te en el origen
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(tx, ty, tz))

        # Aplicar la transformación a los breps
        outer_brep_centered = None
        inner_brep_centered = None

        if outer_brep is not None:
            outer_brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)

        if inner_brep is not None:
            inner_brep_centered = AllplanGeometry.Transform(inner_brep, mat_center)

        model_list = []

        # Outer
        if outer_brep_centered is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_props.ColorByLayer = False  # Desactivar color por layer

            # Asignar layer al outer_model
            outer_layer_short = (
                p.get("LAYER_SHORT_OUTER", None)
                or p.get("LAYER_SHORT_INNER", None)
                or p.get("LAYER_SHORT", None)
            )
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

            # TE TD mixta (type_te >= 3) se comporta como "inner-only":
            # no lleva Material=CAVITAT y debe traer attrs propios del tipo dinámico.
            # En TE TD normal (<3), outer lleva solo Material.
            if self.type_te >= 3:
                outer_attributes = self._create_attributes()
            else:
                outer_attributes = self._create_outer_attributes()
            if outer_attributes:
                outer_model.SetAttributes(outer_attributes)

            model_list.append(outer_model)

        # Inner (solo para type_te < 3)
        if inner_brep_centered is not None and self.type_te < 3:
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p.get("INNER_COLOR", p["COLOR"])
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
                    inner_props.Color = p.get("INNER_COLOR", p["COLOR"])
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
    """
    Creo el elemento final.
    """

    te = TeTDModel(build_ele, doc)
    model_list = te.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
