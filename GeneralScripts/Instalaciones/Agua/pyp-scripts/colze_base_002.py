import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    {  # Ø20x1/2"
        # Outer
        "LEN_X_SMALLEST": 38.75,
        "LEN_Y_SMALLEST": 40.0,
        "HEIGHT_SMALLEST": 40.00,
        "LEN_X_BIGGEST": 40.0,
        "LEN_Y_BIGGEST": 60.0,
        "HEIGHT_BIGGEST": 40.0,
        "COLOR": 5,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # ATTRS_SMALLEST
        "Material": "CAVITAT",
        # Inner
        "LEN_X_INNER_SMALLEST": 28.0,
        "LEN_Y_INNER_SMALLEST": 28.0,
        "HEIGHT_INNER_SMALLEST": 35.50,
        "LEN_X_INNER_BIGGEST": 52.0,
        "LEN_Y_INNER_BIGGEST": 53.0,
        "HEIGHT_INNER_BIGGEST": 34.50,
        "COLOR_INNER": 15,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # ATTRS_BIGGEST
        "ATTR01": "CODO BASE FIJACION Ø20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "object_name": "Colze Base Fijacion Ø20",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_002_001",
        "pmp_diametre": "Ø20",
        "pmp_nom": "CODO BASE FIJACION Ø20",
        "pmp_seccio": "Ø20",
        "pmp_pes_unitari": 0.1470,  # numérico
        # Cylinder
        "CIRCULAR_HOLE_RADIUS": 20.0,  # Radio exterior en mm
        "CIRCULAR_HOLE_HEIGHT": 16.0,  # Altura del cilindro en mm
        "CIRCULAR_HOLE_COLOR": 28,
        "CIRCULAR_HOLE_LAYER_SHORT": "KN_PLD_RECESS",
        "ATTR05": "HOLE",
        "pmp_tipus": "HOLE",
    },
    {  # Ø25x1/2"
        # Outer
        "LEN_X_BIGGEST": 75.0,
        "LEN_Y_BIGGEST": 75.0,
        "HEIGHT_BIGGEST": 80.25,
        "COLOR": 5,
        "LAYER_SHORT_OUTER": "KN_XPS_RECESS",
        # ATTRS_SMALLEST
        "Material": "CAVITAT",
        # Inner
        "LEN_X_INNER_SMALLEST": 35.0,
        "LEN_Y_INNER_SMALLEST": 35.0,
        "HEIGHT_INNER_SMALLEST": 43.00,
        "LEN_X_INNER_BIGGEST": 61.0,
        "LEN_Y_INNER_BIGGEST": 48.0,
        "HEIGHT_INNER_BIGGEST": 34.50,
        "COLOR_INNER": 15,
        "LAYER_SHORT_INNER": "KN_AIGUA",
        # ATTRS_BIGGEST
        "ATTR01": "CODO BASE FIJACION Ø25",
        "ATTR02": "Ø25",
        "ATTR07": "25",
        "object_name": "Colze Base Fijacion Ø25",
        "pmp_pare": "",
        "pmp_CARTICULO": "KN01_002_002",
        "pmp_diametre": "Ø25",
        "pmp_nom": "CODO BASE FIJACION Ø25",
        "pmp_seccio": "Ø25",
        "pmp_pes_unitari": 0.1470,  # numérico
        # Cylinder
        "CIRCULAR_HOLE_RADIUS": 20.0,  # Radio exterior en mm
        "CIRCULAR_HOLE_HEIGHT": 16.0,  # Altura del cilindro en mm
        "CIRCULAR_HOLE_COLOR": 28,
        "CIRCULAR_HOLE_LAYER_SHORT": "KN_PLD_RECESS",
        "ATTR05": "HOLE",
        "pmp_tipus": "HOLE",
    },
]

MAP_COLZE_BASE = {
    'Ø20x1/2"': 0,
    'Ø25x1/2"': 1,
}

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_05_ID = 10005  # Atributo personalizado 05
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07


class ColzeBaseModel:
    """Clase que representa Colze Base"""

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        type_raw = getattr(build_ele, "TipoColzeBase", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_colze_base = MAP_COLZE_BASE.get(str(type_val), 0)
        self.param = PARAMS[self.type_colze_base]

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

    def _create_circular_hole_attributes(self):
        """Crea atributos personalizados para el circular hole de Te Sortidas.
        Usa 'Atributo personalizado 05' (attr05_id) para que se reflejen en Allplan;
        si no existe, intenta con 'ATTR05'."""
        p = self.param
        attrs = []

        # Preferir Atributo personalizado 05 (estándar en el proyecto)
        if self.attr05_id and self.attr05_id > 0 and "ATTR05" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr05_id, p["ATTR05"])
            )
        elif self.attr05_id and self.attr05_id > 0 and "ATTR05" in p:
            attrs.append(
                AllplanBaseElements.AttributeString(self.attr05_id, p["ATTR05"])
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

    def _create_colze_base_inner_brep(self):
        p = self.param
        if self.type_colze_base == 0:
            origin_brep_smallest = AllplanGeometry.Point3D(
                (-p["LEN_X_INNER_SMALLEST"] / 2) - 14,
                16,
                p["LEN_Y_INNER_SMALLEST"] + 9.33,
            )
            placement_brep_smallest = AllplanGeometry.AxisPlacement3D(
                origin_brep_smallest
            )
            brep_smallest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_smallest,
                p["LEN_X_INNER_SMALLEST"],
                p["LEN_Y_INNER_SMALLEST"],
                p["HEIGHT_INNER_SMALLEST"],
            )

            origin_brep_biggest = AllplanGeometry.Point3D(
                (-p["LEN_X_INNER_SMALLEST"] / 2) - 14,  # X
                (p["LEN_Y_INNER_SMALLEST"] / 2)
                - (p["LEN_Y_INNER_BIGGEST"] / 2)
                + 16,  # Y
                2.83,  # Z
            )
            placement_brep_biggest = AllplanGeometry.AxisPlacement3D(
                origin_brep_biggest
            )
            brep_biggest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_biggest,
                p["LEN_X_INNER_BIGGEST"],
                p["LEN_Y_INNER_BIGGEST"],
                p["HEIGHT_INNER_BIGGEST"],
            )
            err, brep_inner = AllplanGeometry.MakeUnion(brep_smallest, brep_biggest)
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_smallest, brep_biggest): código {err}"
                )

            return brep_inner

        elif self.type_colze_base == 1:
            origin_brep_smallest = AllplanGeometry.Point3D(
                (-p["LEN_X_INNER_SMALLEST"] / 2) + p["LEN_X_BIGGEST"] - 17.5,
                20,
                p["LEN_Y_INNER_SMALLEST"] + 2.25,
            )
            placement_brep_smallest = AllplanGeometry.AxisPlacement3D(
                origin_brep_smallest
            )
            brep_smallest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_smallest,
                p["LEN_X_INNER_SMALLEST"],
                p["LEN_Y_INNER_SMALLEST"],
                p["HEIGHT_INNER_SMALLEST"],
            )

            origin_brep_biggest = AllplanGeometry.Point3D(
                (-p["LEN_X_INNER_SMALLEST"] / 2) + p["LEN_X_BIGGEST"] - 21.5,  # X
                (p["LEN_Y_INNER_SMALLEST"] / 2)
                - (p["LEN_Y_INNER_BIGGEST"] / 2)
                + 20,  # Y
                2.83,  # Z
            )
            placement_brep_biggest = AllplanGeometry.AxisPlacement3D(
                origin_brep_biggest
            )
            brep_biggest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_biggest,
                p["LEN_X_INNER_BIGGEST"],
                p["LEN_Y_INNER_BIGGEST"],
                p["HEIGHT_INNER_BIGGEST"],
            )
            err, brep_inner = AllplanGeometry.MakeUnion(brep_smallest, brep_biggest)
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_smallest, brep_biggest): código {err}"
                )

            return brep_inner

    def _create_colze_base_outer_brep(self):
        p = self.param
        if self.type_colze_base == 0:
            origin_brep_biggest = AllplanGeometry.Point3D(0, 0, 0)
            placement_brep_biggest = AllplanGeometry.AxisPlacement3D(
                origin_brep_biggest
            )
            brep_biggest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_biggest,
                p["LEN_X_BIGGEST"],
                p["LEN_Y_BIGGEST"],
                p["HEIGHT_BIGGEST"],
            )

            origin_brep_smallest = AllplanGeometry.Point3D(
                p["LEN_X_BIGGEST"],
                (p["LEN_Y_BIGGEST"] / 2) - (p["LEN_Y_SMALLEST"] / 2),
                (p["HEIGHT_BIGGEST"] / 2) - (p["HEIGHT_SMALLEST"] / 2),
            )
            placement_brep_smallest = AllplanGeometry.AxisPlacement3D(
                origin_brep_smallest
            )
            brep_smallest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_smallest,
                p["LEN_X_SMALLEST"],
                p["LEN_Y_SMALLEST"],
                p["HEIGHT_SMALLEST"],
            )
            err, brep_outer = AllplanGeometry.MakeUnion(brep_biggest, brep_smallest)
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(brep_biggest, brep_smallest): código {err}"
                )

            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(-90)),
            )
            brep_outer = AllplanGeometry.Transform(brep_outer, mat_rot)
            return brep_outer

        elif self.type_colze_base == 1:
            origin_brep_biggest = AllplanGeometry.Point3D(0, 0, 0)
            placement_brep_biggest = AllplanGeometry.AxisPlacement3D(
                origin_brep_biggest
            )
            brep_biggest = AllplanGeometry.BRep3D.CreateCuboid(
                placement_brep_biggest,
                p["LEN_X_BIGGEST"],
                p["LEN_Y_BIGGEST"],
                p["HEIGHT_BIGGEST"],
            )

            return brep_biggest
        else:
            return None

    def _create_cylinder_brep(self):
        p = self.param
        if self.type_colze_base == 0:
            # Origen en (0, 0, 0) con eje Z hacia arriba
            origin_cylinder = AllplanGeometry.Point3D(
                p["CIRCULAR_HOLE_RADIUS"],  # Z
                p["CIRCULAR_HOLE_RADIUS"] + p["CIRCULAR_HOLE_RADIUS"] / 2,  # Y
                -p["CIRCULAR_HOLE_HEIGHT"],  # X
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
            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(-90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)

            return cylinder
        elif self.type_colze_base == 1:
            # Origen en (0, 0, 0) con eje Z hacia arriba
            origin_cylinder = AllplanGeometry.Point3D(
                p["CIRCULAR_HOLE_RADIUS"],  # Z
                p["CIRCULAR_HOLE_RADIUS"] + (p["CIRCULAR_HOLE_RADIUS"] / 2) + 7.5,  # Y
                -p["CIRCULAR_HOLE_HEIGHT"] - p["LEN_X_BIGGEST"],  # X
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
            # Rotacion de 90 grados en el eje Y
            mat_rot = AllplanGeometry.Matrix3D()
            mat_rot.SetRotation(
                AllplanGeometry.Line3D(0, 0, 0, 0, 1, 0),
                AllplanGeometry.Angle(math.radians(-90)),
            )
            cylinder = AllplanGeometry.Transform(cylinder, mat_rot)

            return cylinder
        else:
            return None

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_brep = None
        inner_brep = None
        cylinder_brep = None

        if self.type_colze_base == 0:
            outer_brep = self._create_colze_base_outer_brep()
            inner_brep = self._create_colze_base_inner_brep()
            cylinder_brep = self._create_cylinder_brep()
            return outer_brep, inner_brep, cylinder_brep

        elif self.type_colze_base == 1:
            outer_brep = self._create_colze_base_outer_brep()
            inner_brep = self._create_colze_base_inner_brep()
            cylinder_brep = self._create_cylinder_brep()
            return outer_brep, inner_brep, cylinder_brep
        else:
            return None

    def _get_brep_visible_minmax(self, brep):
        """Devuelve el MinMax3D visible (bounding box) de un BRep."""
        if brep is None:
            return None
        err, _s, _scale, _trans, _spacemm, visiblemm = (
            brep.WriteToStreamSplitTransform()
        )
        if err != 0:
            return None
        return visiblemm

    def _center_breps_outer_xy_cyl_z(self, outer_brep, inner_brep, cylinder_brep):
        """Centra el conjunto:
        - En X e Y usando el outer_brep.
        - En Z usando el cylinder_brep.
        Si alguno falta, se hace fallback al que exista.
        """
        mm_outer = self._get_brep_visible_minmax(outer_brep)
        mm_cyl = self._get_brep_visible_minmax(cylinder_brep)

        if (mm_outer is None or not mm_outer.IsValid()) and (
            mm_cyl is None or not mm_cyl.IsValid()
        ):
            # No tenemos info fiable para centrar, devolvemos sin cambios
            return outer_brep, inner_brep, cylinder_brep

        # Centro en X e Y a partir del outer_brep
        if mm_outer is not None and mm_outer.IsValid():
            omin, omax = mm_outer.GetMin(), mm_outer.GetMax()
            center_x = (omin.X + omax.X) * 0.5
            center_y = (omin.Y + omax.Y) * 0.5
        else:
            # Fallback: usar el cilindro si no hay outer válido
            cmin, cmax = mm_cyl.GetMin(), mm_cyl.GetMax()
            center_x = (cmin.X + cmax.X) * 0.5
            center_y = (cmin.Y + cmax.Y) * 0.5

        # Centro en Z a partir del cylinder_brep
        if mm_cyl is not None and mm_cyl.IsValid():
            cmin, cmax = mm_cyl.GetMin(), mm_cyl.GetMax()
            center_z = (cmin.Z + cmax.Z) * 0.5
        else:
            # Fallback: usar outer si no hay cilindro válido
            omin, omax = mm_outer.GetMin(), mm_outer.GetMax()
            center_z = (omin.Z + omax.Z) * 0.5

        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(
            AllplanGeometry.Vector3D(-center_x, -center_y, -center_z)
        )

        outer_brep_c = (
            AllplanGeometry.Transform(outer_brep, mat_center) if outer_brep else None
        )
        inner_brep_c = (
            AllplanGeometry.Transform(inner_brep, mat_center) if inner_brep else None
        )
        cylinder_brep_c = (
            AllplanGeometry.Transform(cylinder_brep, mat_center)
            if cylinder_brep
            else None
        )

        return outer_brep_c, inner_brep_c, cylinder_brep_c

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        p = self.param

        outer_brep, inner_brep, cylinder_brep = self._create_brep()

        if outer_brep is None and inner_brep is None and cylinder_brep is None:
            return []

        # Centramos el modelo: X/Y por el outer, Z por el cilindro
        outer_brep, inner_brep, cylinder_brep = self._center_breps_outer_xy_cyl_z(
            outer_brep, inner_brep, cylinder_brep
        )

        model_list = []

        if outer_brep is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
            model_list.append(outer_model)

        if inner_brep is not None:
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p["COLOR_INNER"]
            inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)
            model_list.append(inner_model)

        if cylinder_brep is not None:
            cylinder_props = AllplanBaseElements.CommonProperties()
            cylinder_props.GetGlobalProperties()
            cylinder_props.Color = p["CIRCULAR_HOLE_COLOR"]
            cylinder_model = AllplanBasisElements.ModelElement3D(
                cylinder_props, cylinder_brep
            )
            model_list.append(cylinder_model)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""

    colze_base = ColzeBaseModel(build_ele, doc)
    model_list = colze_base.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
