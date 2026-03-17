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

# Indice 0 -> CØ20, Indice 1 -> CØ25
PARAMS = [
    # CØ20
    {  # Outer
        "ARM_LEN_X": 40.0,
        "ARM_LEN_Y": 75.0,
        "THICKNESS": 40.0,
        "HEIGHT": 40.0,
        "COLOR": 5,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 30.0,
        "INNER_ARM_Y": 42.0,
        "INNER_THICKNESS": 30.0,
        "INNER_HEIGHT": 30.0,
        "INNER_COLOR": 3,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Caps
        "CAP_ARM_X": 30.0,
        "CAP_ARM_Y": 23.0,
        "CAP_THICKNESS": 30.0,
        "CAP_HEIGHT": 31.0,
        # Dif Outer/Inner
        "SPACE": 5.0,
        "ATTR01": "CØ20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "pmp_pare": "",
        "object_name": "Colze Ø20",
        "pmp_CARTICULO": "KN01_001_001",
        "pmp_diametre": "Ø20",
        "pmp_nom": "CØ20",
        "pmp_seccio": "20",
        "pmp_pes_unitari": 0.1470,  # numérico
        "Material": "CAVITAT",  # Material para outer_model
    },
    # CØ25
    {  # Outer
        "ARM_LEN_X": 75.0,
        "ARM_LEN_Y": 115.0,
        "THICKNESS": 75.0,
        "HEIGHT": 75.0,
        "COLOR": 128,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 35.0,
        "INNER_ARM_Y": 52.0,
        "INNER_THICKNESS": 35.0,
        "INNER_HEIGHT": 35.0,
        "INNER_COLOR": 3,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Caps
        "CAP_ARM_X": 35.0,
        "CAP_ARM_Y": 23.0,
        "CAP_THICKNESS": 35.0,
        "CAP_HEIGHT": 36.0,
        # Dif Outer/Inner
        "SPACE": 20.0,
        "ATTR01": "CØ25",
        "ATTR02": "Ø25",
        "ATTR07": "25",
        "pmp_pare": "",
        "object_name": "Colze Ø25",
        "pmp_CARTICULO": "KN01_001_002",
        "pmp_diametre": "Ø25",
        "pmp_nom": "CØ25",
        "pmp_seccio": "25",
        "pmp_pes_unitari": 0.1470,  # numérico
        "Material": "CAVITAT",  # Material para outer_model
    },
]


class ColzeTDModel:
    """Clase que representa Colze TD"""

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

        # Propiedades comunes (ya no se usan, pero se mantienen por compatibilidad)
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = self.param["COLOR"]
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
        self.attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, "pmp_pare")
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )
        self.attr_material_id = AttributeService.GetAttributeID(self.doc, "Material")

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

    def _create_elbow_brep(self, param: dict):
        """Codo exterior."""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # Brazo en x
        brep_x = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["ARM_LEN_X"],
            param["ARM_LEN_Y"],
            param["HEIGHT"],
        )

        # Brazo en y
        brep_y = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["ARM_LEN_Y"],
            param["ARM_LEN_X"],
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

        # Parametros del inner
        inner_param = {
            "ARM_LEN_Y": self.param["INNER_ARM_Y"],
            "ARM_LEN_X": self.param["INNER_ARM_X"],
            "THICKNESS": self.param["INNER_THICKNESS"],
            "HEIGHT": self.param["INNER_HEIGHT"],
            "COLOR": self.param["INNER_COLOR"],
        }

        # Elbow interior base
        inner_core = self._create_elbow_brep(inner_param)

        # Cap en el extremo del brazo X
        cap1_origin = AllplanGeometry.Point3D(
            inner_param["ARM_LEN_Y"], -(inner_param["ARM_LEN_X"]), 0.0
        )
        cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
        cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap1_place,
            self.param["CAP_ARM_Y"],
            self.param["CAP_ARM_X"],
            self.param["CAP_HEIGHT"],
        )
        # Aplico la rotacion
        mat = AllplanGeometry.Matrix3D()
        mat.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeometry.Angle(math.radians(0)),
        )
        cap1 = AllplanGeometry.Transform(cap1_local, mat)

        # UNION: elbow interior + cap1
        err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

        # CAP2 (brazo Y)

        # origen al final del brazo Y del elbow interior
        cap2_origin = AllplanGeometry.Point3D(inner_param["ARM_LEN_Y"], 0.0, 0.0)
        cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

        cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
            cap2_place,
            self.param["CAP_ARM_Y"],
            self.param["CAP_ARM_X"],
            self.param["CAP_HEIGHT"],
        )

        # Rotacion
        mat2 = AllplanGeometry.Matrix3D()
        mat2.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeometry.Angle(math.radians(270)),
        )
        cap2 = AllplanGeometry.Transform(cap2_local, mat2)

        # UNION (inner + cap1) + cap2
        err, inner_with_caps = AllplanGeometry.MakeUnion(inner_with_cap1, cap2)
        if err != 0:
            raise Exception(f"Error en MakeUnion(inner_with_cap1, cap2): código {err}")

        return inner_with_caps

    def _create_brep(self):
        """Outer + Inner"""

        # Outer segun los parametros principales
        outer_param = {
            "ARM_LEN_Y": self.param["ARM_LEN_Y"],
            "ARM_LEN_X": self.param["ARM_LEN_X"],
            "THICKNESS": self.param["THICKNESS"],
            "HEIGHT": self.param["HEIGHT"],
            "COLOR": self.param["COLOR"],
        }

        outer_core = self._create_elbow_brep(outer_param)
        inner_with_caps = self._create_inner_brep_with_caps()

        # CENTRO EL INNER DENTRO DEL OUTER
        # Distancia entre outer e inner
        dx = self.param["SPACE"]
        dy = -self.param["SPACE"]
        dz = self.param["SPACE"]

        mat_t = AllplanGeometry.Matrix3D()
        mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
        inner_centered = AllplanGeometry.Transform(inner_with_caps, mat_t)

        return outer_core, inner_centered

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""

        outer_brep, inner_brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico del colze para centrarlo
        # El colze tiene dos brazos: uno en X (ARM_LEN_X) y uno en Y (ARM_LEN_Y)
        # Después de la rotación de 270 grados, el centro está en el punto de unión
        half_y = float(p["ARM_LEN_X"]) / 2.0
        half_z = float(p["INNER_HEIGHT"]) * 0.5

        # Transformación para centrar el colze en el origen
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-half_y, half_y, -half_z))

        # Aplicar la transformación a ambos breps
        outer_brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)
        inner_brep_centered = AllplanGeometry.Transform(inner_brep, mat_center)

        # Propiedades outer
        outer_props = AllplanBaseElements.CommonProperties()
        outer_props.GetGlobalProperties()
        outer_props.Color = p["COLOR"]
        outer_props.ColorByLayer = False  # Desactivar color por layer

        # Asignar layer al outer_model
        outer_layer_short = p.get("LAYER_SHORT_OUTER", None)
        if outer_layer_short:
            outer_layer_id = LayerService.GetIDByShortName(outer_layer_short, self.doc)
            if outer_layer_id > 0:
                outer_props.Layer = outer_layer_id
                # Reasignar color después de asignar layer para asegurar que se mantenga
                outer_props.Color = p["COLOR"]
                outer_props.ColorByLayer = False

        # Propiedades inner
        inner_props = AllplanBaseElements.CommonProperties()
        inner_props.GetGlobalProperties()
        inner_props.Color = p["INNER_COLOR"]
        inner_props.ColorByLayer = False  # Desactivar color por layer

        # Asignar layer al inner_model
        inner_layer_short = p.get("LAYER_SHORT_INNER", None)
        if inner_layer_short:
            inner_layer_id = LayerService.GetIDByShortName(inner_layer_short, self.doc)
            if inner_layer_id > 0:
                inner_props.Layer = inner_layer_id
                # Reasignar color después de asignar layer para asegurar que se mantenga
                inner_props.Color = p["INNER_COLOR"]
                inner_props.ColorByLayer = False

        outer_model = AllplanBasisElements.ModelElement3D(
            outer_props, outer_brep_centered
        )
        inner_model = AllplanBasisElements.ModelElement3D(
            inner_props, inner_brep_centered
        )

        # Atributos para inner_model (todos los atributos excepto Material)
        inner_attributes = self._create_attributes()
        if inner_attributes:
            inner_model.SetAttributes(inner_attributes)

        # Atributos para outer_model (solo Material)
        outer_attributes = self._create_outer_attributes()
        if outer_attributes:
            outer_model.SetAttributes(outer_attributes)

        return [outer_model, inner_model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    elbow = ColzeTDModel(build_ele, doc)
    model_list = elbow.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
