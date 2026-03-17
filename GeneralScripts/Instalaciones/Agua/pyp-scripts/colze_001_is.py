import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


# Indice 0 -> CØ20, Indice 1 -> CØ25
PARAMS = [
    # CØ20
    {
        "LEN_X": 42.0,
        "LEN_Y": 30.0,
        "HEIGHT": 30.0,
        "COLOR": 16,
        "LAYER_SHORT": "IS_CON_AIGUA_FAB",
        "CAP_LEN_X": 23.0,
        "CAP_LEN_Y": 30.0,
        "CAP_HEIGHT": 31.0,
        "ATTR01": "CØ20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "object_name": "Colze Ø20",
        "6_CC_IS": "IS",
        "pmp_CARTICULO": "KN01_001_001",
        "pmp_diametre": "20",
        "pmp_nom": "CØ20",
        "pmp_seccio": "20",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # CØ25
    {
        "LEN_X": 52.0,
        "LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 16,
        "LAYER_SHORT": "IS_CON_AIGUA_FAB",
        "CAP_LEN_X": 23.0,
        "CAP_LEN_Y": 35.0,
        "CAP_HEIGHT": 36.0,
        "ATTR01": "CØ25",
        "ATTR02": "Ø25",
        "ATTR07": "25",
        "object_name": "Colze Ø25",
        "6_CC_IS": "IS",
        "pmp_CARTICULO": "KN01_001_002",
        "pmp_diametre": "25",
        "pmp_nom": "CØ25",
        "pmp_seccio": "25",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
]

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07


class ColzeModel:
    """Clase que representa Colze IS"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        # Leo el tipo desde el RadioButtonGroup
        self.type = self._int_value(getattr(build_ele, "TipoCodo", None), 0)

        # OVERRIDE desde la polilínea si existe DiametroAplicar
        diam_attr = getattr(build_ele, "DiametroAplicar", None)
        if diam_attr is not None:
            diam_val = getattr(diam_attr, "value", diam_attr)
            try:
                diam_int = int(diam_val)
            except Exception:
                diam_int = None

            if diam_int == 20:
                self.type = 0
            elif diam_int == 25:
                self.type = 1

        self.param = PARAMS[self.type]

        # Propiedades comunes
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = self.param["COLOR"]
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
        self.attr_pmp_pes_unitari_id = AttributeService.GetAttributeID(
            self.doc, "pmp_pes_unitari"
        )
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )

    @staticmethod
    def _int_value(attr, default=0) -> int:
        """Leo el value con seguridad."""
        if attr is None:
            return default
        v = getattr(attr, "value", attr)
        try:
            return int(v)
        except Exception:
            return default

    def _create_attributes(self):
        """Armo los atributos personalizados segun el tipo de colze."""
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

    def _create_colze_brep(self, param: dict):
        """Metodo para crear el cuerpo central."""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # Brazo en x
        brep_x = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["LEN_X"],
            param["LEN_Y"],
            param["HEIGHT"],
        )

        # Brazo en y
        brep_y = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["LEN_Y"],
            param["LEN_X"],
            param["HEIGHT"],
        )

        err, union_brep = AllplanGeometry.MakeUnion(brep_x, brep_y)
        if err != 0:
            raise Exception(f"Error en MakeUnion del codo: código {err}")

        # Rotacion final
        mat = AllplanGeometry.Matrix3D()
        mat.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),  # eje Z
            AllplanGeometry.Angle(math.radians(270)),
        )

        rotated = AllplanGeometry.Transform(union_brep, mat)
        return rotated

    def _create_inner_brep_with_caps(self):
        """Codo interior + Caps"""

        # Colze base
        inner_core = self._create_colze_brep(self.param)

        # Cap en el extremo del brazo X
        cap1_origin = AllplanGeometry.Point3D(
            self.param["LEN_X"], -(self.param["LEN_Y"]), 0.0
        )
        cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
        cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap1_place,
            self.param["CAP_LEN_X"],
            self.param["CAP_LEN_Y"],
            self.param["CAP_HEIGHT"],
        )

        # UNION: elbow interior + cap1
        err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1_local)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

        # CAP2 (brazo Y)

        # origen al final del brazo Y del elbow interior
        cap2_origin = AllplanGeometry.Point3D(
            0.0, -self.param["LEN_X"] - self.param["CAP_LEN_X"], 0.0
        )
        cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

        cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap2_place,
            self.param["CAP_LEN_Y"],
            self.param["CAP_LEN_X"],
            self.param["CAP_HEIGHT"],
        )

        # Rotacion
        mat2 = AllplanGeometry.Matrix3D()
        mat2.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeometry.Angle(math.radians(0)),
        )
        cap2 = AllplanGeometry.Transform(cap2_local, mat2)

        # UNION (inner + cap1) + cap2
        err, inner_with_caps = AllplanGeometry.MakeUnion(inner_with_cap1, cap2)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_with_cap1, cap2): código {err}")

        return inner_with_caps

    def _create_brep(self):
        """Metodo para crear los Colze"""

        outer_core = self._create_inner_brep_with_caps()

        return outer_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""

        outer_brep = self._create_brep()

        # Igual que el tubo centro el codo -> coloco el centro geométrico en la polilínea.
        half_y = float(self.param["LEN_Y"]) / 2.0

        half_z = float(self.param["HEIGHT"]) * 0.5

        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-half_y, half_y, -half_z))

        brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)

        outer_model = AllplanBasisElements.ModelElement3D(
            self.common_props, brep_centered
        )

        attributes = self._create_attributes()
        outer_model.SetAttributes(attributes)

        return [outer_model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    elbow = ColzeModel(build_ele, doc)
    model_list = elbow.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
