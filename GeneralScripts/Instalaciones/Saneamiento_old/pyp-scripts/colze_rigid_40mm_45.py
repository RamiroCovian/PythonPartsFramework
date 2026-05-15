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

# Indice 0 -> CØ20, Indice 1 -> CØ25
PARAMS = [
    # C 45°
    {
        "LEN_X": 40.0,
        "LEN_Y": 61.57,
        "HEIGHT": 40.0,
        "COLOR": 66,
        "LAYER_SHORT": "IS_CON_SANE_FAB",
        "CAP_LEN_X": 40.0,
        "CAP_LEN_Y": 21.57,
        "CAP_HEIGHT": 40.00,
        "RING_LEN": 40.0,
        "RING_OVERHANG": 5.0,
        "ATTR01": "CØ20",
        "ATTR02": "Ø20",
        "ATTR07": "20",
        "object_name": "Colze Ø20",
        "6_CC_IS": "",
        "pmp_CARTICULO": "KN01_001_001",
        "pmp_diametre": "20",
        "pmp_nom": "CØ20",
        "pmp_seccio": "20",
        "pmp_pes_unitari": 0.1470,  # numérico
    },
    # C 90°
    {
        "LEN_X": 52.0,
        "LEN_Y": 35.0,
        "HEIGHT": 35.0,
        "COLOR": 70,
        "LAYER_SHORT": "IS_CON_AIGUA_FAB",
        "CAP_LEN_X": 23.0,
        "CAP_LEN_Y": 35.0,
        "CAP_HEIGHT": 36.0,
        "ATTR01": "CØ25",
        "ATTR02": "Ø25",
        "ATTR07": "25",
        "object_name": "Colze Ø25",
        "6_CC_IS": "",
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


class CodoBasicoTEST:
    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        self.build_ele = build_ele

        # Seleccionar el tipo de codo (por defecto 0 = 45°, 1 = 90°)
        # La paleta usa el parámetro "TipoSaneamiento" con radios 45°/90°.
        self.type = self._int_value(getattr(build_ele, "TipoSaneamiento", None), 0)
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
        """Metodo para crear el cuerpo central."""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        # Cuerpo central del codo (primer cuboide)
        brep_x = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["LEN_X"],
            param["LEN_Y"],
            param["HEIGHT"],
        )

        # Segundo cuerpo
        brep_y = AllplanGeometry.BRep3D.CreateCuboid(
            placement,
            param["CAP_LEN_X"],
            param["CAP_LEN_Y"],
            param["CAP_HEIGHT"],
        )

        # Trasladar el segundo brep a la posición (0, param["LEN_Y"], 0)
        mat_translate = AllplanGeometry.Matrix3D()
        mat_translate.SetTranslation(AllplanGeometry.Vector3D(0, param["LEN_Y"], 0))
        brep_y_translated = AllplanGeometry.Transform(brep_y, mat_translate)

        # Anillo al final del ramal inclinado (solo si hay parámetros)
        ring_len = param.get("RING_LEN", None)
        ring_overhang = param.get("RING_OVERHANG", None)
        ring_brep = None
        if ring_len is not None and ring_overhang is not None:
            ring_x = float(param["LEN_X"]) + (2.0 * float(ring_overhang))
            ring_z = float(param["HEIGHT"])
            ring_origin = AllplanGeometry.Point3D(
                -float(ring_overhang),
                float(param["LEN_Y"]) + float(param["CAP_LEN_Y"]),
                0.0,
            )
            ring_axis = AllplanGeometry.AxisPlacement3D(ring_origin)
            ring_brep = AllplanGeometry.BRep3D.CreateCuboid(
                ring_axis,
                ring_x,
                float(ring_len),
                ring_z,
            )

        # Aplicar rotación de 45 grados alrededor del punto (0, param["LEN_Y"], 0)
        # Para rotar alrededor de un punto: trasladar al origen, rotar, trasladar de vuelta
        translate_y = param["LEN_Y"]

        # 1. Trasladar al origen
        mat_to_origin = AllplanGeometry.Matrix3D()
        mat_to_origin.SetTranslation(AllplanGeometry.Vector3D(0, -translate_y, 0))
        brep_y_at_origin = AllplanGeometry.Transform(brep_y_translated, mat_to_origin)

        # 2. Rotar 45 grados alrededor del eje Z
        mat_rot = AllplanGeometry.Matrix3D()
        mat_rot.SetRotation(
            AllplanGeometry.Line3D(0, 0, 0, 0, 0, 1),  # eje Z
            AllplanGeometry.Angle(math.radians(-45)),
        )
        brep_y_rotated = AllplanGeometry.Transform(brep_y_at_origin, mat_rot)

        # 3. Trasladar de vuelta a (0, translate_y, 0)
        mat_back = AllplanGeometry.Matrix3D()
        mat_back.SetTranslation(AllplanGeometry.Vector3D(0, translate_y, 0))
        brep_y_final = AllplanGeometry.Transform(brep_y_rotated, mat_back)

        ring_final = None
        if ring_brep is not None:
            ring_at_origin = AllplanGeometry.Transform(ring_brep, mat_to_origin)
            ring_rotated = AllplanGeometry.Transform(ring_at_origin, mat_rot)
            ring_final = AllplanGeometry.Transform(ring_rotated, mat_back)

        # Unir ambos cuerpos
        err, union_brep = AllplanGeometry.MakeUnion(brep_x, brep_y_final)
        if err != 0:
            raise Exception(f"Error en MakeUnion del codo: código {err}")

        if ring_final is not None:
            err, union_brep = AllplanGeometry.MakeUnion(union_brep, ring_final)
            if err != 0:
                raise Exception(f"Error en MakeUnion del anillo: código {err}")

        return union_brep

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
        half_x = float(self.param["LEN_X"]) / 2.0
        half_y = float(self.param["LEN_Y"]) / 2.0
        half_z = float(self.param["HEIGHT"]) / 2.0

        mat_center = AllplanGeometry.Matrix3D()
        mat_center.SetTranslation(AllplanGeometry.Vector3D(-20.00, -53.35, -20.00))

        brep_centered = AllplanGeometry.Transform(outer_brep, mat_center)

        outer_model = AllplanBasisElements.ModelElement3D(
            self.common_props, brep_centered
        )
        self._apply_45deg_custom_attributes(outer_model)

        return [outer_model]

    def _apply_45deg_custom_attributes(self, model_elem):
        """Aplicar atributos personalizados del codo 45° (exactos)."""
        if self.type != 0:
            return

        parent_value = self._get_parent_attribute_value()
        value_to_apply = parent_value or self.param.get("6_CC_IS", "")

        attr_list = [
            AllplanBaseElements.AttributeString(1083, "CS45ºØ25"),
            AllplanBaseElements.AttributeString(1084, "Ø25"),
            AllplanBaseElements.AttributeString(1085, ""),
            AllplanBaseElements.AttributeString(1086, ""),
            AllplanBaseElements.AttributeString(1087, ""),
            AllplanBaseElements.AttributeString(1895, ""),
            AllplanBaseElements.AttributeString(1896, "25"),
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
                            attr_pmp_carticulo_id, "KN07_001_001"
                        )
                    )
                if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_nom_id, "CS45ºØ25"
                        )
                    )
                if attr_pmp_pes_unitari_id and attr_pmp_pes_unitari_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeDouble(
                            attr_pmp_pes_unitari_id, 0.0133
                        )
                    )
                if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                    try:
                        attr_list.append(
                            AllplanBaseElements.AttributeInt(attr_pmp_seccio_id, 25)
                        )
                    except Exception:
                        attr_list.append(
                            AllplanBaseElements.AttributeString(
                                attr_pmp_seccio_id, "25"
                            )
                        )
                if attr_pmp_pare_id and attr_pmp_pare_id > 0:
                    attr_list.append(
                        AllplanBaseElements.AttributeString(
                            attr_pmp_pare_id, value_to_apply
                        )
                    )
            except Exception as e:
                print(f"[Colze_basic_001_TEST] Error atributos 45°: {e}")

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
