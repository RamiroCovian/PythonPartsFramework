import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    # TAP 1/2"
    {
        "ARM_LEN_X": 30.0,
        "ARM_LEN_Y": 9.0,
        "HEIGHT": 30.0,
        "COLOR": 5,
        "SMALL_ARM_LEN_X": 20.0,
        "SMALL_ARM_LEN_Y": 11.0,
        "SMALL_HEIGHT": 20.0,
        "SPACE": 5.0,
        "LAYER_SHORT": "KN_AIGUA",
        # Attrs
        "ATTR01": "TAP 1/2'",
        "ATTR02": "1/2'",
        "ATTR07": "1/2'",
        "object_name": "TAP 1/2'",
        "pmp_CARTICULO": "KN01_010_001",
        "pmp_diametre": "1/2'",
        "pmp_nom": "TAP 1/2'",
        "pmp_seccio": "1/2'",
    },
]

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07

MAP_TAPS = {
    'TAP 1/2"': 0,
}


class TapsModel:
    """Clase que representa Taps"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        type_raw = getattr(build_ele, "TipoTaps", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_taps = MAP_TAPS.get(str(type_val), 0)
        self.param = PARAMS[self.type_taps]

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
        self.attr_pmp_diametre_id = AttributeService.GetAttributeID(
            self.doc, "pmp_diametre"
        )
        self.attr_pmp_nom_id = AttributeService.GetAttributeID(self.doc, "pmp_nom")
        self.attr_pmp_seccio_id = AttributeService.GetAttributeID(
            self.doc, "pmp_seccio"
        )
        self.attr_object_name_id = AttributeService.GetAttributeID(
            self.doc, "Nombre de objeto"
        )
        self.attr_material_id = AttributeService.GetAttributeID(self.doc, "Material")

    def _create_taps_brep(self, param: dict):
        """Taps externo"""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_taps == 0:
            brep_center = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )

            center_buttom_origin = AllplanGeometry.Point3D(
                param["SPACE"], -param["SMALL_ARM_LEN_Y"], param["SPACE"]
            )
            placement_buttom = AllplanGeometry.AxisPlacement3D(center_buttom_origin)
            brep_buttom = AllplanGeometry.BRep3D.CreateCuboid(
                placement_buttom,
                param["SMALL_ARM_LEN_X"],
                param["SMALL_ARM_LEN_Y"],
                param["SMALL_HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_center, brep_buttom)
            if err != 0:
                raise Exception(f"Error en MakeUnion del Taps: codigo {err}")

            return union_brep
        else:
            print("Aun no hemos realizado ese Brep")

    def _create_attributes(self):
        """Armo los atributos personalizados segun el tipo de Taps."""
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

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_core = None
        inner_core = None
        if self.type_taps == 0:
            outer_core = self._create_taps_brep(self.param)
        else:
            print("Aun no hemos creado outer, innner para ese Brep.")
        return outer_core, inner_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico del taps para centrarlo
        # El taps se extiende en Y desde -SMALL_ARM_LEN_Y hasta ARM_LEN_Y
        # El centro en Y es: (ARM_LEN_Y - SMALL_ARM_LEN_Y) / 2.0
        half_x = float(p.get("ARM_LEN_X", 0.0)) / 2.0
        arm_len_y = float(p.get("ARM_LEN_Y", 0.0))
        small_arm_len_y = float(p.get("SMALL_ARM_LEN_Y", 0.0))
        # Centro geométrico en Y: desde -SMALL_ARM_LEN_Y hasta ARM_LEN_Y
        half_y = (arm_len_y - small_arm_len_y) / 2.0
        half_z = float(p.get("HEIGHT", 0.0)) * 0.5

        # Transformación para centrar el taps en el origen (X, Y, Z)
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-half_x, -half_y, -half_z))

        # Aplicar la transformación al brep
        outer_brep_centered = None
        if outer_brep is not None:
            outer_brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)

        model_list = []

        # Outer
        if outer_brep_centered is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_props.ColorByLayer = False  # Desactivar color por layer

            # Asignar layer al outer_model
            outer_layer_short = p.get("LAYER_SHORT", None)
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

            # Atributos para outer_model (todos los atributos, incluyendo Material)
            # Como solo hay outer, combinamos todos los atributos
            all_attrs = []

            # Atributos normales
            normal_attrs = self._create_attributes()
            if normal_attrs:
                attr_sets = normal_attrs.GetAttributeSets()
                if attr_sets:
                    all_attrs.extend(attr_sets[0].GetAttributes())

            if all_attrs:
                combined_attr_set = AllplanBaseElements.AttributeSet(all_attrs)
                combined_attributes = AllplanBaseElements.Attributes(
                    [combined_attr_set]
                )
                outer_model.SetAttributes(combined_attributes)

            model_list.append(outer_model)

        # Inner (si existe en el futuro)
        if inner_brep is not None:
            pass

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    taps = TapsModel(build_ele, doc)
    model_list = taps.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
