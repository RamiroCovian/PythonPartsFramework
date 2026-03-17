import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    # TØ20
    {
        # Outer
        "ARM_LEN_X": 54.0,
        "ARM_LEN_Y": 30.0,
        "HEIGHT": 30.0,
        "COLOR": 16,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 12.0,
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
        # Attrs
        "ATTR01": "TØ20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "object_name": "T20",
        "6_CC_IS": "IS",
        "pmp_CARTICULO": "KN01_003_001",
        "pmp_diametre": "20",
        "pmp_nom": "TØ20",
        "pmp_seccio": "Ø20",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # TØ25
    {
        # Outer
        "ARM_LEN_X": 69.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 16,
        "SMALL_ARM_X": 35.0,
        "SMALL_ARM_Y": 17.0,
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
        # Attrs
        "ATTR01": "TØ25",
        "ATTR02": "Ø25",
        "ATTR07": "25",
        "object_name": "T25",
        "6_CC_IS": "IS",
        "pmp_CARTICULO": "KN01_003_002",
        "pmp_diametre": "25",
        "pmp_nom": "TØ25",
        "pmp_seccio": "Ø25",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # TØ32
    {
        # Outer
        "ARM_LEN_X": 0.0,
        "ARM_LEN_Y": 0.0,
        "THICKNESS": 0.0,
        "HEIGHT": 0.0,
        "COLOR": 0.0,
        # Inner
        "INNER_ARM_X": 0.0,
        "INNER_ARM_Y": 0.0,
        "INNER_THICKNESS": 0.0,
        "INNER_HEIGHT": 0.0,
        "INNER_COLOR": 0.0,
        # Caps
        "CAP_ARM_X": 0.0,
        "CAP_ARM_Y": 0.0,
        "CAP_THICKNESS": 0.0,
        "CAP_HEIGHT": 0.0,
        # Dif Outer/Inner
        "SPACE": 0.0,
    },
    # TØ25-20-25
    {
        # Middle
        "ARM_LEN_X": 64.0,
        "ARM_LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 16,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 12.0,
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
        "6_CC_IS": "IS",
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
        "COLOR": 16,
        "SMALL_ARM_X": 30.0,
        "SMALL_ARM_Y": 17.0,
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
        "6_CC_IS": "IS",
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
        "COLOR": 16,
        "SMALL_ARM_X": 35.0,
        "SMALL_ARM_Y": 17.0,
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
        "6_CC_IS": "IS",
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

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07


class TeModel:
    """Clase que representa los modelos de las diferentes Te IS"""

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

    def _create_te_brep(self, param: dict):
        """Te externo"""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_te > 3:
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
                (param["LEFT_CAP_ARM_X"] + x_len),
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
        elif self.type_te < 2:
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
        else:
            print("No hemos creado ese Brep todavia!. (_create_te_brep_with_caps)")

    def _create_te_brep_with_caps(self):
        """Te + Caps"""

        if self.type_te == 3:
            origin = AllplanGeometry.Point3D(0, 0, 0)
            placement = AllplanGeometry.AxisPlacement3D(origin)

            # Cuerpo horizontal
            inner_core = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                self.param["ARM_LEN_X"],
                self.param["ARM_LEN_Y"],
                self.param["HEIGHT"],
            )

            # Brazo vertical (arriba)
            center_x = (self.param["ARM_LEN_X"] / 2.0) - (
                self.param["SMALL_ARM_X"] / 2.0
            )
            origin_top = AllplanGeometry.Point3D(
                center_x,
                self.param["ARM_LEN_Y"],
                0.0,
            )
            placement_top = AllplanGeometry.AxisPlacement3D(origin_top)

            brep_top = AllplanGeometry.BRep3D.CreateCuboid(
                placement_top,
                self.param["SMALL_ARM_X"],
                self.param["SMALL_ARM_Y"],
                self.param["HEIGHT"],
            )

            err, inner_core = AllplanGeometry.MakeUnion(inner_core, brep_top)
            if err != 0:
                raise Exception(f"Error en MakeUnion(inner_core, top): código {err}")

        elif self.type_te >= 4:
            inner_core = self._create_te_brep(self.param)
        elif self.type_te < 3:
            inner_core = self._create_te_brep(self.param)

        # Left Cap
        cap1_origin = AllplanGeometry.Point3D(-(self.param["LEFT_CAP_ARM_X"]), 0.0, 0.0)
        cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
        cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap1_place,
            self.param["LEFT_CAP_ARM_X"],
            self.param["LEFT_CAP_ARM_Y"],
            self.param["LEFT_CAP_HEIGHT"],
        )

        err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

        # Right Cap
        cap2_origin = AllplanGeometry.Point3D(self.param["ARM_LEN_X"], 0.0, 0.0)
        cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

        cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap2_place,
            self.param["RIGHT_CAP_ARM_X"],
            self.param["RIGHT_CAP_ARM_Y"],
            self.param["RIGHT_CAP_HEIGHT"],
        )

        err, inner_with_caps2 = AllplanGeometry.MakeUnion(inner_with_cap1, cap2_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_with_cap1, cap2): código {err}")

        # Top Cap
        center_x = (self.param["ARM_LEN_X"] / 2) - (self.param["SMALL_ARM_X"] / 2)
        center_y = self.param["ARM_LEN_Y"] + self.param["SMALL_ARM_Y"]
        cap3_origin = AllplanGeometry.Point3D(center_x, center_y, 0.0)
        cap3_place = AllplanGeometry.AxisPlacement3D(cap3_origin)

        cap3_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap3_place,
            self.param["TOP_CAP_ARM_Y"],
            self.param["TOP_CAP_ARM_X"],
            self.param["TOP_CAP_HEIGHT"],
        )

        err, inner_with_caps = AllplanGeometry.MakeUnion(inner_with_caps2, cap3_local)
        if err != 0:
            raise Exception(
                f"Error en MakeUnion(inner_with_caps2, cap3_local): código {err}"
            )

        return inner_with_caps

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_core = None
        if self.type_te < 2:
            outer_core = self._create_te_brep_with_caps()
        elif self.type_te == 3:
            outer_core = self._create_te_brep_with_caps()
        elif self.type_te >= 4:
            outer_core = self._create_te_brep(self.param)
        else:
            print("No hemos creado este Brep todavia!. (_create_brep)")
        return outer_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep = self._create_brep()
        outer_model = AllplanBasisElements.ModelElement3D(self.common_props, outer_brep)

        attributes = self._create_attributes()
        outer_model.SetAttributes(attributes)

        return [outer_model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    te = TeModel(build_ele, doc)
    model_list = te.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
