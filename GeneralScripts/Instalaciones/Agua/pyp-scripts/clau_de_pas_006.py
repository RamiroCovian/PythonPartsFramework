import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService
from NemAll_Python_BaseElements import LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    # CPØ20
    {  # Outer
        "LEN_X": 40.0,
        "LEN_Y": 50.0,
        "HEIGHT": 112.0,
        "COLOR": 5,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # Inner
        "INNER_ARM_X": 34.0,
        "INNER_ARM_Y": 34.0,
        "INNER_HEIGHT": 112.0,
        "OFFSET_INNER_RIGHT_X": 0.0,
        "SPACE_INNER_Y": 0.0,
        "INNER_COLOR": 67,
        "INNER_CROSS_ARM_X_VERTICAL": 2.0,
        "INNER_CROSS_ARM_Y_VERTICAL": 46.0,
        "INNER_CROSS_HEIGHT_VERTICAL": 0.50,
        "INNER_CROSS_ARM_X_HORIZONTAL": 36.0,
        "INNER_CROSS_ARM_Y_HORIZONTAL": 2.0,
        "INNER_CROSS_HEIGHT_HORIZONTAL": 0.50,
        "CYLINDER_INNER_ARM_X": 60.0,
        "CYLINDER_INNER_RADIUS": 10.0,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Cylinder
        "CIRCULAR_HOLE_RADIUS": 20.0,  # Radio exterior en mm
        "CIRCULAR_HOLE_HEIGHT": 16.0,  # Altura del cilindro en mm
        "CIRCULAR_HOLE_COLOR": 28,
        "CIRCULAR_HOLE_LAYER_SHORT": "KN_PLD_RECESS",
        # Attrs
        "ATTR01_INNER": "CPØ20",
        "ATTR02_INNER": "Ø20",
        "ATTR07_INNER": "20",
        "object_name": "Clau de Pas Ø20",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_006_001",
        "pmp_diametre": "Ø20",
        "pmp_nom": "CPØ20",
        "pmp_pes_unitari": 0.1470,  # numérico
        "pmp_seccio": "Ø20",
        "Material": "CAVITAT",  # Material para outer_model
        "ATTR05_CIRCULAR_HOLE": "HOLE",
        "pmp_tipus": "HOLE",
    },
    # CPØ25
    {  # Outer
        "LEN_X": 75.0,
        "LEN_Y": 75.0,
        "HEIGHT": 120.0,
        "COLOR": 128,
        "LAYER_SHORT_OUTER": "KN_XPS_CAVITAT",
        # Inner
        "INNER_ARM_X": 35.0,
        "INNER_ARM_Y": 35.0,
        "INNER_HEIGHT": 120.0,
        "OFFSET_INNER_RIGHT_X": 0.0,
        "SPACE_INNER_Y": 0.0,
        "INNER_COLOR": 67,
        "INNER_CROSS_ARM_X_VERTICAL": 2.0,
        "INNER_CROSS_ARM_Y_VERTICAL": 46.0,
        "INNER_CROSS_HEIGHT_VERTICAL": 0.50,
        "INNER_CROSS_ARM_X_HORIZONTAL": 36.0,
        "INNER_CROSS_ARM_Y_HORIZONTAL": 2.0,
        "INNER_CROSS_HEIGHT_HORIZONTAL": 0.50,
        "CYLINDER_INNER_ARM_X": 60.0,
        "CYLINDER_INNER_RADIUS": 10.0,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # Cylinder
        "CIRCULAR_HOLE_RADIUS": 20.0,  # Radio exterior en mm
        "CIRCULAR_HOLE_HEIGHT": 16.0,  # Altura del cilindro en mm
        "CIRCULAR_HOLE_COLOR": 28,
        "CIRCULAR_HOLE_LAYER_SHORT": "KN_PLD_RECESS",
        # Attrs
        "ATTR01_INNER": "CPØ25",
        "ATTR02_INNER": "Ø25",
        "ATTR07_INNER": "25",
        "object_name": "Clau de Pas Ø25",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_006_002",
        "pmp_diametre": "Ø25",
        "pmp_nom": "CPØ25",
        "pmp_pes_unitari": 0.1470,  # numérico
        "pmp_seccio": "Ø25",
        "Material": "CAVITAT",  # Material para outer_model
        "ATTR05_CIRCULAR_HOLE": "HOLE",
        "pmp_tipus": "HOLE",
    },
]

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_05_ID = 10005  # Atributo personalizado 05
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07

MAP_CLAUDEPAS = {
    "CPØ20": 0,
    "CPØ25": 1,
}


class ClauDePasModel:
    """Clase que representa Clau de Pas"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        type_raw = getattr(build_ele, "TipoClaudePas", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_clau_de_pas = MAP_CLAUDEPAS.get(str(type_val), 0)

        # Validar que el ID existe en PARAMS
        if self.type_clau_de_pas < len(PARAMS):
            self.param = dict(PARAMS[self.type_clau_de_pas])
            self.is_implemented = True
        else:
            # ID no implementado (ej: ID 2 o superior)
            self.param = {}
            self.is_implemented = False
            print(
                f"[Clau de Pas] ERROR: El tipo con ID {self.type_clau_de_pas} no está implementado todavía."
            )

        # Common properties (solo si está implementado)
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
        self.attr05_id = AttributeService.GetAttributeID(
            self.doc, "Atributo personalizado 05"
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
        self.attr_pmp_tipus_id = AttributeService.GetAttributeID(self.doc, "pmp_tipus")

    def _create_attributes(self):
        """Armo los atributos personalizados según el tipo de Clau de Pas."""
        p = self.param
        attrs = []

        if self.attr01_id and self.attr01_id > 0 and "ATTR01" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr01_id, p["ATTR01"])
            )
        if self.attr02_id and self.attr02_id > 0 and "ATTR02" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr02_id, p["ATTR02"])
            )
        if self.attr07_id and self.attr07_id > 0 and "ATTR07" in p:
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

    def _create_inner_attributes(self):
        """Crea atributos personalizados para el inner_model."""
        p = self.param
        attrs = []

        if self.attr01_id and self.attr01_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr01_id, p["ATTR01_INNER"])
            )
        if self.attr02_id and self.attr02_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr02_id, p["ATTR02_INNER"])
            )
        if self.attr07_id and self.attr07_id > 0:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr07_id, p["ATTR07_INNER"])
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

    def _create_circular_hole_attributes(self):
        """Crea atributos personalizados para el cilindro de Clau de Pas."""
        p = self.param
        attrs = []

        if self.attr05_id and self.attr05_id > 0 and "ATTR05_CIRCULAR_HOLE" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr05_id, p["ATTR05_CIRCULAR_HOLE"]
                )
            )
        if self.attr_pmp_tipus_id and self.attr_pmp_tipus_id > 0 and "pmp_tipus" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(
                    self.attr_pmp_tipus_id, p["pmp_tipus"]
                )
            )

        if not attrs:
            return None

        attr_set = AllplanBaseElements.AttributeSet(attrs)
        return AllplanBaseElements.Attributes([attr_set])

    def _create_cylinder_brep(self):
        """Crea un cilindro con el radio y altura especificados."""
        p = self.param
        # Origen en (0, 0, 0) con eje Z hacia arriba
        origin_cylinder = AllplanGeometry.Point3D(
            0, 0, -p["LEN_X"] / 2 - p["CIRCULAR_HOLE_HEIGHT"]
        )
        placement = AllplanGeometry.AxisPlacement3D(origin_cylinder)

        # Crear el cilindro usando CreateCylinder (mismo método que en TechtivaPiece.py)
        # Parámetros: placement, radius, height, top_cap (True), bottom_cap (True)
        cylinder = AllplanGeometry.BRep3D.CreateCylinder(
            placement,
            p["CIRCULAR_HOLE_RADIUS"],
            p["CIRCULAR_HOLE_HEIGHT"],
            True,  # Tapa superior
            True,  # Tapa inferior
        )
        # Rotacion de 90 grados en el eje X
        mat_rot = AllplanGeometry.Matrix3D()
        mat_rot.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
            AllplanGeometry.Angle(math.radians(90)),
        )
        cylinder = AllplanGeometry.Transform(cylinder, mat_rot)

        # Rotacion de 90 grados en el eje Z
        mat_rot = AllplanGeometry.Matrix3D()
        mat_rot.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),
            AllplanGeometry.Angle(math.radians(90)),
        )
        cylinder = AllplanGeometry.Transform(cylinder, mat_rot)
        return cylinder

    def _create_clau_de_pas_outer_brep(self):
        """Clau de Pas externo"""
        p = self.param
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_clau_de_pas == 0:
            brep_outer = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                p["LEN_X"],
                p["LEN_Y"],
                p["HEIGHT"],
            )
            return brep_outer
        elif self.type_clau_de_pas == 1:
            brep_outer = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                p["LEN_X"],
                p["LEN_Y"],
                p["HEIGHT"],
            )
            return brep_outer
        else:
            print(
                f"[Clau de Pas] ERROR: No se puede crear el elemento. El tipo con ID {self.type_clau_de_pas} no está implementado."
            )
            return None

    def _create_clau_de_pas_inner_brep(self):
        """Clau de Pas interno"""
        p = self.param

        if self.type_clau_de_pas == 0:
            OFFSET_CENTERED_INNER_Y = 18
            OFFSET_CENTERED_INNER_X = 19

            # Inner center
            origin_inner_center = AllplanGeometry.Point3D(
                -p["INNER_ARM_X"] + OFFSET_CENTERED_INNER_X,  # X
                p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2
                - p["INNER_ARM_Y"] / 2
                - OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_HEIGHT"] / 2,  # Z
            )

            placement_inner_center = AllplanGeometry.AxisPlacement3D(
                origin_inner_center
            )
            brep_inner = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_center,
                p["INNER_ARM_X"],
                p["INNER_ARM_Y"],
                p["INNER_HEIGHT"],
            )

            # Inner cross horizontal
            origin_inner_cross_horizontal = AllplanGeometry.Point3D(
                -OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                OFFSET_CENTERED_INNER_X,  # X
            )
            placement_inner_cross_horizontal = AllplanGeometry.AxisPlacement3D(
                origin_inner_cross_horizontal
            )
            brep_inner_cross_horizontal = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_cross_horizontal,
                p["INNER_CROSS_ARM_X_HORIZONTAL"],
                p["INNER_CROSS_ARM_Y_HORIZONTAL"],
                p["INNER_CROSS_HEIGHT_HORIZONTAL"],
            )

            # Inner cross vertical
            origin_inner_cross_vertical = AllplanGeometry.Point3D(
                -p["INNER_CROSS_ARM_X_VERTICAL"] / 2
                + p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2
                - OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_CROSS_ARM_Y_VERTICAL"] / 2
                + p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2
                - p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                OFFSET_CENTERED_INNER_X,  # X
            )
            placement_inner_cross_vertical = AllplanGeometry.AxisPlacement3D(
                origin_inner_cross_vertical
            )
            brep_inner_cross_vertical = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_cross_vertical,
                p["INNER_CROSS_ARM_X_VERTICAL"],
                p["INNER_CROSS_ARM_Y_VERTICAL"],
                p["INNER_CROSS_HEIGHT_VERTICAL"],
            )
            err, brep_inner_cross_union = AllplanGeometry.MakeUnion(
                brep_inner_cross_vertical, brep_inner_cross_horizontal
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_vertical, brep_inner_cross_horizontal): código {err}"
                )
            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            brep_inner_cross_union = AllplanGeometry.Transform(
                brep_inner_cross_union, mat_rot
            )
            # Rotacion de 90 grados en el eje X
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            brep_inner_cross_union = AllplanGeometry.Transform(
                brep_inner_cross_union, mat_rot
            )

            err, brep_inner_cross_union = AllplanGeometry.MakeUnion(
                brep_inner_cross_union, brep_inner
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_union, brep_inner): código {err}"
                )

            # Cylinder
            origin_cylinder = AllplanGeometry.Point3D(
                p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2 - OFFSET_CENTERED_INNER_Y,  # Y
                p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2
                - p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                -p["CYLINDER_INNER_ARM_X"]
                - p["INNER_ARM_X"]
                + OFFSET_CENTERED_INNER_X,  # X
            )

            placement_cylinder = AllplanGeometry.AxisPlacement3D(origin_cylinder)
            cylinder = AllplanGeometry.BRep3D.CreateCylinder(
                placement_cylinder,
                p["CYLINDER_INNER_RADIUS"],
                p["CYLINDER_INNER_ARM_X"],
                True,
                True,
            )

            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)

            # Rotacion de 90 grados en el eje X
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)
            err, brep_inner_final = AllplanGeometry.MakeUnion(
                brep_inner_cross_union, cylinder
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_union, cylinder): código {err}"
                )

            return brep_inner_final

        elif self.type_clau_de_pas == 1:
            OFFSET_CENTERED_INNER_Y = 18
            OFFSET_CENTERED_INNER_X = 2.5

            # Inner center
            origin_inner_center = AllplanGeometry.Point3D(
                -p["INNER_ARM_X"] + OFFSET_CENTERED_INNER_X,  # X
                p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2
                - p["INNER_ARM_Y"] / 2
                - OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_HEIGHT"] / 2,  # Z
            )

            placement_inner_center = AllplanGeometry.AxisPlacement3D(
                origin_inner_center
            )
            brep_inner = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_center,
                p["INNER_ARM_X"],
                p["INNER_ARM_Y"],
                p["INNER_HEIGHT"],
            )

            # Inner cross horizontal
            origin_inner_cross_horizontal = AllplanGeometry.Point3D(
                -OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                OFFSET_CENTERED_INNER_X,  # X
            )
            placement_inner_cross_horizontal = AllplanGeometry.AxisPlacement3D(
                origin_inner_cross_horizontal
            )
            brep_inner_cross_horizontal = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_cross_horizontal,
                p["INNER_CROSS_ARM_X_HORIZONTAL"],
                p["INNER_CROSS_ARM_Y_HORIZONTAL"],
                p["INNER_CROSS_HEIGHT_HORIZONTAL"],
            )

            # Inner cross vertical
            origin_inner_cross_vertical = AllplanGeometry.Point3D(
                -p["INNER_CROSS_ARM_X_VERTICAL"] / 2
                + p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2
                - OFFSET_CENTERED_INNER_Y,  # Y
                -p["INNER_CROSS_ARM_Y_VERTICAL"] / 2
                + p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2
                - p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                OFFSET_CENTERED_INNER_X,  # X
            )
            placement_inner_cross_vertical = AllplanGeometry.AxisPlacement3D(
                origin_inner_cross_vertical
            )
            brep_inner_cross_vertical = AllplanGeometry.BRep3D.CreateCuboid(
                placement_inner_cross_vertical,
                p["INNER_CROSS_ARM_X_VERTICAL"],
                p["INNER_CROSS_ARM_Y_VERTICAL"],
                p["INNER_CROSS_HEIGHT_VERTICAL"],
            )
            err, brep_inner_cross_union = AllplanGeometry.MakeUnion(
                brep_inner_cross_vertical, brep_inner_cross_horizontal
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_vertical, brep_inner_cross_horizontal): código {err}"
                )
            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            brep_inner_cross_union = AllplanGeometry.Transform(
                brep_inner_cross_union, mat_rot
            )
            # Rotacion de 90 grados en el eje X
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            brep_inner_cross_union = AllplanGeometry.Transform(
                brep_inner_cross_union, mat_rot
            )

            err, brep_inner_cross_union = AllplanGeometry.MakeUnion(
                brep_inner_cross_union, brep_inner
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_union, brep_inner): código {err}"
                )

            # Cylinder
            origin_cylinder = AllplanGeometry.Point3D(
                p["INNER_CROSS_ARM_X_HORIZONTAL"] / 2 - OFFSET_CENTERED_INNER_Y,  # Y
                p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2
                - p["INNER_CROSS_ARM_Y_HORIZONTAL"] / 2,  # Z
                -p["CYLINDER_INNER_ARM_X"]
                - p["INNER_ARM_X"]
                + OFFSET_CENTERED_INNER_X,  # X
            )

            placement_cylinder = AllplanGeometry.AxisPlacement3D(origin_cylinder)
            cylinder = AllplanGeometry.BRep3D.CreateCylinder(
                placement_cylinder,
                p["CYLINDER_INNER_RADIUS"],
                p["CYLINDER_INNER_ARM_X"],
                True,
                True,
            )

            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)

            # Rotacion de 90 grados en el eje X
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
                AllplanGeometry.Angle(math.radians(90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)
            err, brep_inner_final = AllplanGeometry.MakeUnion(
                brep_inner_cross_union, cylinder
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_inner_cross_union, cylinder): código {err}"
                )

            return brep_inner_final

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_brep = None
        inner_brep = None
        cylinder_brep = None
        if self.type_clau_de_pas in [0, 1]:
            outer_brep = self._create_clau_de_pas_outer_brep()
            cylinder_brep = self._create_cylinder_brep()
            inner_brep = self._create_clau_de_pas_inner_brep()
            return outer_brep, inner_brep, cylinder_brep
        else:
            print(
                f"[Clau de Pas] ERROR: No se puede crear el elemento. El tipo con ID {self.type_clau_de_pas} no está implementado."
            )
            return None, None, None

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep, cylinder_brep = self._create_brep()
        p = self.param

        # Calcular el centro geométrico del Clau de Pas para centrarlo
        # El Clau de Pas se extiende en Y desde -SMALL_ARM_LEN_Y hasta ARM_LEN_Y
        # El centro en Y es: (ARM_LEN_Y - SMALL_ARM_LEN_Y) / 2.0
        half_x = float(p.get("LEN_X", 0.0)) / 2.0
        half_y = float(p.get("LEN_Y", 0.0)) / 2.0
        half_z = float(p.get("HEIGHT", 0.0)) * 0.5

        # Transformación para centrar el Clau de Pas en el origen (X, Y, Z)
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

            # Atributos para outer_model (todos los atributos, incluyendo Material)
            # Como solo hay outer, combinamos todos los atributos
            all_attrs = []

            # Atributos normales
            normal_attrs = self._create_outer_attributes()
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
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p["INNER_COLOR"]
            inner_props.ColorByLayer = False
            inner_layer_short = p.get("LAYER_SHORT_INNER", None)
            if inner_layer_short:
                inner_layer_id = LayerService.GetIDByShortName(
                    inner_layer_short, self.doc
                )
                if inner_layer_id > 0:
                    inner_props.Layer = inner_layer_id
                    inner_props.Color = p["INNER_COLOR"]
                    inner_props.ColorByLayer = False
            inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)

            model_list.append(inner_model)
            inner_attributes = self._create_inner_attributes()
            if inner_attributes:
                inner_model.SetAttributes(inner_attributes)

        # Cylinder
        if cylinder_brep is not None:
            cylinder_props = AllplanBaseElements.CommonProperties()
            cylinder_props.GetGlobalProperties()
            cylinder_props.Color = p["CIRCULAR_HOLE_COLOR"]
            cylinder_props.ColorByLayer = False
            cylinder_layer_short = p.get("CIRCULAR_HOLE_LAYER_SHORT", None)
            if cylinder_layer_short:
                cylinder_layer_id = LayerService.GetIDByShortName(
                    cylinder_layer_short, self.doc
                )
                if cylinder_layer_id > 0:
                    cylinder_props.Layer = cylinder_layer_id
                    cylinder_props.Color = p["CIRCULAR_HOLE_COLOR"]
                    cylinder_props.ColorByLayer = False
            cylinder_model = AllplanBasisElements.ModelElement3D(
                cylinder_props, cylinder_brep
            )
            model_list.append(cylinder_model)
            cylinder_attributes = self._create_circular_hole_attributes()
            if cylinder_attributes:
                cylinder_model.SetAttributes(cylinder_attributes)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    clau_de_pas = ClauDePasModel(build_ele, doc)
    model_list = clau_de_pas.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
