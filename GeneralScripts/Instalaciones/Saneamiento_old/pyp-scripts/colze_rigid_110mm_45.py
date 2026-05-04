import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, _version) -> bool:
    """Check the current Allplan version (se soportan todas las versiones).

    Returns:
        bool: True if the version is supported.
    """
    return True
# 

# 
PARAMS = [
    # Codo 110mm 45° (igual a Colze_rigidSane_004.py, sin rotaciones extra)
    {
        "DIAMETRO": 110.0,
        "LARGO_VERTICAL": 10.0,
        "LARGO_INCLINADA": 80.0,
        "LARGO_HORIZONTAL": 70.0,
        "ANGULO_INCLINADA": 23.0,
        "ANGULO_HORIZONTAL": 45.0,
        "LARGO_ANILLO": 73.0,
        "SOBRESALE_ANILLO": 9.0,
        "COLOR": 7,
        "LAYER_SHORT": "IS_CON_SANE_FAB",
        "ATTR01": "COLZE M-F 110Ø 45°",
        "ATTR02": "Ø110",
        "ATTR07": "110",
        "object_name": "COLZE M-F 110Ø 45°",
        "6_CC_IS": "",
        "pmp_CARTICULO": "KN07_004_003",
        "pmp_diametre": "110",
        "pmp_nom": "COLZE M-F 110Ø 45°",
        "pmp_seccio": "Ø110/45°",
        "pmp_pes_unitari": 0.2110,
    },
]

ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07


class CodoBasicoTEST:
    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        self.build_ele = build_ele

        # Seleccionar el tipo de codo (por defecto 0 = 45°)
        # Se mantiene el esquema de colze_rigid_40mm_45.py aunque haya un solo tipo.
        self.type = self._int_value(getattr(build_ele, "TipoSaneamiento", None), 0)
        self.param = PARAMS[0]
        self.rot_x = self._float_value(getattr(build_ele, "RotX", None), 0.0)
        self.rot_y = self._float_value(getattr(build_ele, "RotY", None), 0.0)
        self.rot_z = self._float_value(getattr(build_ele, "RotZ", None), -135.0)

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

    @staticmethod
    def _float_value(attr, default=0.0) -> float:
        """Leo el value con seguridad."""
        if attr is None:
            return default
        v = getattr(attr, "value", attr)
        try:
            return float(v)
        except Exception:
            return default

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

    @staticmethod
    def _string_value(attr, default="") -> str:
        """Lee un valor string con seguridad."""
        if attr is None:
            return default
        v = getattr(attr, "value", attr)
        try:
            return str(v)
        except Exception:
            return default

    def _get_parent_attribute_value(self):
        """Obtiene el valor del atributo padre si existe en la paleta."""
        for name in ("ValorAtributos", "AtributoPadre", "AtributosPadre", "Atributo_Padre"):
            raw = self._string_value(getattr(self.build_ele, name, None), "")
            value = raw.strip()
            if value:
                return value
        return None

    def _create_colze_brep(self, param: dict):
        """Metodo para crear el codo 110mm 45° (sin rotaciones extra)."""
        cubo0 = AllplanGeometry.Polyhedron3D.CreateCuboid(
            AllplanGeometry.Point3D(0, 0, 0),
            AllplanGeometry.Point3D(
                param["DIAMETRO"], param["DIAMETRO"], param["LARGO_VERTICAL"]
            ),
        )

        rad_incl = math.radians(param["ANGULO_INCLINADA"])
        cubo1 = AllplanGeometry.Polyhedron3D.CreateCuboid(
            AllplanGeometry.Point3D(0, 0, 0),
            AllplanGeometry.Point3D(
                param["DIAMETRO"], param["DIAMETRO"], param["LARGO_INCLINADA"]
            ),
        )
        m1 = AllplanGeometry.Matrix3D()
        m1.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
            AllplanGeometry.Angle(-rad_incl),
        )
        cubo1 = AllplanGeometry.Transform(cubo1, m1)
        t1 = AllplanGeometry.Matrix3D()
        t1.SetTranslation(AllplanGeometry.Vector3D(0, 0, param["LARGO_VERTICAL"]))
        cubo1 = AllplanGeometry.Transform(cubo1, t1)

        dz = param["LARGO_INCLINADA"] * math.cos(rad_incl)
        dy = param["LARGO_INCLINADA"] * math.sin(rad_incl)

        rad_h = math.radians(param["ANGULO_HORIZONTAL"])
        cubo2 = AllplanGeometry.Polyhedron3D.CreateCuboid(
            AllplanGeometry.Point3D(0, 0, 0),
            AllplanGeometry.Point3D(
                param["DIAMETRO"], param["DIAMETRO"], param["LARGO_HORIZONTAL"]
            ),
        )
        m2 = AllplanGeometry.Matrix3D()
        m2.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 1, 0, 0),
            AllplanGeometry.Angle(-rad_h),
        )
        cubo2 = AllplanGeometry.Transform(cubo2, m2)
        t2 = AllplanGeometry.Matrix3D()
        t2.SetTranslation(
            AllplanGeometry.Vector3D(0, dy, param["LARGO_VERTICAL"] + dz)
        )
        cubo2 = AllplanGeometry.Transform(cubo2, t2)

        anillo = AllplanGeometry.Polyhedron3D.CreateCuboid(
            AllplanGeometry.Point3D(
                -param["SOBRESALE_ANILLO"],
                -param["SOBRESALE_ANILLO"],
                -param["LARGO_ANILLO"],
            ),
            AllplanGeometry.Point3D(
                param["DIAMETRO"] + param["SOBRESALE_ANILLO"],
                param["DIAMETRO"] + param["SOBRESALE_ANILLO"],
                0,
            ),
        )

        err, codo = AllplanGeometry.MakeUnion(cubo0, cubo1)
        if err == 0 and codo.IsValid():
            err, codo = AllplanGeometry.MakeUnion(codo, cubo2)
        if err == 0 and codo.IsValid():
            err, codo = AllplanGeometry.MakeUnion(codo, anillo)
        if err != 0 or not codo.IsValid():
            raise Exception(f"Error en MakeUnion del codo: código {err}")

        eje_y = AllplanGeometry.Axis3D(
            AllplanGeometry.Point3D(0, 0, 0), AllplanGeometry.Vector3D(0, 1, 0)
        )
        codo_rot = AllplanGeometry.Rotate(
            codo, eje_y, AllplanGeometry.Angle(math.radians(-270))
        )

        # Rotar sobre su propio eje (centroide aproximado)
        cx = param["DIAMETRO"] / 2.0
        cy = (
            param["DIAMETRO"] / 2.0
            + param["LARGO_INCLINADA"] * math.sin(math.radians(param["ANGULO_INCLINADA"])) / 2.0
        )
        cz = (
            param["LARGO_VERTICAL"]
            + param["LARGO_INCLINADA"] * math.cos(math.radians(param["ANGULO_INCLINADA"]))
            + param["LARGO_HORIZONTAL"]
        ) / 2.0

        if abs(self.rot_x) > 1e-6:
            eje_x = AllplanGeometry.Axis3D(
                AllplanGeometry.Point3D(cx, cy, cz), AllplanGeometry.Vector3D(1, 0, 0)
            )
            codo_rot = AllplanGeometry.Rotate(
                codo_rot, eje_x, AllplanGeometry.Angle(math.radians(self.rot_x))
            )
        if abs(self.rot_y) > 1e-6:
            eje_y_rot = AllplanGeometry.Axis3D(
                AllplanGeometry.Point3D(cx, cy, cz), AllplanGeometry.Vector3D(0, 1, 0)
            )
            codo_rot = AllplanGeometry.Rotate(
                codo_rot, eje_y_rot, AllplanGeometry.Angle(math.radians(self.rot_y))
            )
        if abs(self.rot_z) > 1e-6:
            eje_z = AllplanGeometry.Axis3D(
                AllplanGeometry.Point3D(cx, cy, cz), AllplanGeometry.Vector3D(0, 0, 1)
            )
            codo_rot = AllplanGeometry.Rotate(
                codo_rot, eje_z, AllplanGeometry.Angle(math.radians(self.rot_z))
            )

        return codo_rot

    def _create_brep(self):
        """Metodo para crear los Colze"""

        outer_core = self._create_colze_brep(self.param)

        return outer_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep = self._create_brep()

        # Centrar el cuboide en el origen (0,0,0)
        # El cuboide se crea desde el origen extendiéndose en direcciones positivas
        # Para centrarlo, lo movemos la mitad de sus dimensiones en dirección negativa
        half_x = float(self.param["DIAMETRO"]) / 2.0
        half_y = float(self.param["DIAMETRO"]) / 2.0
        half_z = float(self.param["LARGO_VERTICAL"]) / 2.0

        # Centrar el codo como en colze_rigid_40mm_45.py
        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-61.91, -100.00, 55.00))
        brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)

        outer_model = AllplanBasisElements.ModelElement3D(
            self.common_props, brep_centered
        )
        self._apply_45deg_custom_attributes(outer_model)

        return [outer_model]

    def _apply_45deg_custom_attributes(self, model_elem):
        """Aplicar atributos personalizados del codo 45° (110mm)."""
        if self.type != 0:
            return

        parent_value = self._get_parent_attribute_value()
        value_to_apply = parent_value or self.param.get("6_CC_IS", "")

        attr_list = [
            AllplanBaseElements.AttributeString(1083, "COLZE M-F 110Ø 45º"),
            AllplanBaseElements.AttributeString(1084, "Ø110"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "110"),
        ]

        if self.doc:
            try:
                attr_6_cc_is_id = AttributeService.GetAttributeID(self.doc, "6_CC_IS")
                attr_pmp_carticulo_id = AttributeService.GetAttributeID(
                    self.doc, "pmp_CARTICULO"
                )
                attr_pmp_nom_id = AttributeService.GetAttributeID(
                    self.doc, "pmp_nom"
                )
                attr_pmp_pes_unitari_id = AttributeService.GetAttributeID(
                    self.doc, "pmp_pes_unitari"
                )
                attr_pmp_seccio_id = AttributeService.GetAttributeID(
                    self.doc, "pmp_seccio"
                )
                attr_pmp_pare_id = AttributeService.GetAttributeID(
                    self.doc, "pmp_pare"
                )

                if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_6_cc_is_id, value_to_apply
                        )
                    )
                if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_carticulo_id, "KN07_004_003"
                        )
                    )
                if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_nom_id, "COLZE M-F 110Ø 45°"
                        )
                    )
                if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeDouble(
                            attr_pmp_pes_unitari_id, 0.2110
                        )
                    )
                if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_seccio_id, "Ø110/45°"
                        )
                    )
                if attr_pmp_pare_id and attr_pmp_pare_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_pare_id, value_to_apply
                        )
                    )
            except Exception as e:
                print(f"[colze_rigid_110mm_45] Error atributos 45°: {e}")

        if not attr_list:
            return

        attr_set_list = [AllplanBaseElements.AttributeSet(attr_list)]
        attributes = AllplanBaseElements.Attributes(attr_set_list)
        model_elem.SetAttributes(attributes)


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    elbow = CodoBasicoTEST(build_ele, doc)
    model_list = elbow.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
