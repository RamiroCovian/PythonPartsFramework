import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from NemAll_Python_BaseElements import AttributeService, LayerService


def check_allplan_version(_build_ele, version) -> bool:
    return True


class ManguitoModel:
    """Clase que representa Manguitos IS"""

    PARAMS = [
        # MØ20
        {
            # Outer
            "ARM_LEN_X": 29.0,
            "ARM_LEN_Y": 30.0,
            "HEIGHT": 35.0,
            "COLOR": 16,
            # Caps
            "CAP_ARM_X": 23.0,
            "CAP_ARM_Y": 30.0,
            "CAP_HEIGHT": 31.0,
            # Attrs
            "ATTR01": "MØ20",
            "ATTR02": "Ø20",
            "ATTR07": "20",
            "object_name": "Manguito 20",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_005_001",
            "pmp_diametre": "20",
            "pmp_nom": "MØ20",
            "pmp_seccio": "Ø20",
            "pmp_pes_unitari": 0.1470,  # numérico
        },
        # MØ25
        {
            # Outer
            "ARM_LEN_X": 34.0,
            "ARM_LEN_Y": 35.0,
            "HEIGHT": 35.0,
            "COLOR": 16,
            # Caps
            "CAP_ARM_X": 23.0,
            "CAP_ARM_Y": 35.0,
            "CAP_HEIGHT": 36.0,
            # Attrs
            "ATTR01": "MØ25",
            "ATTR02": "Ø25",
            "ATTR07": "25",
            "object_name": "Manguito 25",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_005_002",
            "pmp_diametre": "25",
            "pmp_nom": "MØ25",
            "pmp_seccio": "Ø25",
            "pmp_pes_unitari": 0.1470,  # numérico
        },
        # MØ32
        {
            # Outer
            "ARM_LEN_X": 0.0,
            "ARM_LEN_Y": 0.0,
            "THICKNESS": 0.0,
            "HEIGHT": 0.0,
            "COLOR": 0.0,
            # Caps
            "CAP_ARM_X": 0.0,
            "CAP_ARM_Y": 0.0,
            "CAP_THICKNESS": 0.0,
            "CAP_HEIGHT": 0.0,
        },
        # MØ25-20
        {
            # Middle-left
            "MDL_ARM_LEN_X": 12.0,
            "MDL_ARM_LEN_Y": 30.0,
            "MDL_HEIGHT": 30.0,
            "COLOR": 16,
            # Middle-Right
            "MDR_ARM_LEN_X": 17.0,
            "MDR_ARM_LEN_Y": 35.0,
            "MDR_HEIGHT": 30.0,
            # Left Cap
            "LEFT_CAP_ARM_X": 23.0,
            "LEFT_CAP_ARM_Y": 30.0,
            "LEFT_CAP_HEIGHT": 31.0,
            # Right Cap
            "RIGHT_CAP_ARM_X": 23.0,
            "RIGHT_CAP_ARM_Y": 35.0,
            "RIGHT_CAP_HEIGHT": 31.0,
            # Attrs
            "ATTR01": "RØ25-20",
            "ATTR02": "Ø25-20",
            "ATTR07": "25-20",
            "object_name": "Red 25-20",
            "6_CC_IS": "IS",
            "pmp_CARTICULO": "KN01_005_001",
            "pmp_diametre": "25-20",
            "pmp_nom": "RØ25-20",
            "pmp_seccio": "Ø25-20",
            "pmp_pes_unitari": 0.1470,  # numérico
        },
        # MØ32x25
        {
            # Outer
            "ARM_LEN_X": 0.0,
            "ARM_LEN_Y": 0.0,
            "THICKNESS": 0.0,
            "HEIGHT": 0.0,
            "COLOR": 0.0,
            # Caps
            "CAP_ARM_X": 0.0,
            "CAP_ARM_Y": 0.0,
            "CAP_THICKNESS": 0.0,
            "CAP_HEIGHT": 0.0,
        },
    ]

    ATTR_PERSO_01_ID = 10001  # Atributo personalizado 01
    ATTR_PERSO_02_ID = 10002  # Atributo personalizado 02
    ATTR_PERSO_07_ID = 10007  # Atributo personalizado 07

    def __init__(self, build_ele, doc: AllplanElementAdapter.DocumentAdapter):
        self.doc = doc
        self.type_manguito = self._int_value(
            getattr(build_ele, "TipoManguito", None), 0
        )
        self.param = ManguitoModel.PARAMS[self.type_manguito]

        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        self.common_props = common_properties

        # === LAYER igual que tubos y codos ===
        short_name = self.param.get("LAYER_SHORT", None)
        if short_name:
            layer_id = LayerService.GetIDByShortName(short_name, self.doc)
            if layer_id > 0:
                self.common_props.Layer = layer_id

        # Color fijo por pieza, no por layer
        self.common_props.ColorByLayer = False
        self.common_props.Color = int(self.param["COLOR"])
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

    def set_diameters(self, d1, d2):
        """
        Ajusta automáticamente el tipo de manguito según los diámetros
        de los tramos anterior y siguiente.
        d1 = diámetro tramo anterior
        d2 = diámetro tramo siguiente
        """
        try:
            a = int(d1)
            b = int(d2)
        except:
            a = b = None

        # Ordeno para detectar reducción 20-25 o 25-20
        pair = tuple(sorted((a, b)))

        # Map según tus PARAMS
        if pair == (20, 20):
            idx = 0  # MØ20
        elif pair == (25, 25):
            idx = 1  # MØ25
        elif pair == (20, 25):
            idx = 3  # Reductor 25-20
        else:
            # Default a lo que diga TipoManguito
            idx = self.type_manguito

        # Actualizar internamente el tipo
        self.type_manguito = idx
        self.param = ManguitoModel.PARAMS[idx]

        # Actualizar color y propiedades
        try:
            self.common_props.Color = int(self.param["COLOR"])
        except:
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

    def _create_manguito_brep(self, param: dict):
        "Manguito externo"
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_manguito != 3:
            brep_x = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )
            return brep_x
        else:
            brep_left = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["MDL_ARM_LEN_X"],
                param["MDL_ARM_LEN_Y"],
                param["MDL_HEIGHT"],
            )
            # Centro el Brep derecho al Brep izquierdo
            center_brep_right_y = (param["MDR_ARM_LEN_Y"] - param["MDL_ARM_LEN_Y"]) / 2

            origin_right = AllplanGeometry.Point3D(
                param["MDL_ARM_LEN_X"], -(center_brep_right_y), 0
            )
            placement_right = AllplanGeometry.AxisPlacement3D(origin_right)

            brep_right = AllplanGeometry.BRep3D.CreateCuboid(
                placement_right,
                param["MDR_ARM_LEN_X"],
                param["MDR_ARM_LEN_Y"],
                param["MDR_HEIGHT"],
            )

            err, union_brep = AllplanGeometry.MakeUnion(brep_left, brep_right)
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion del manguito MØ25-20: codigo {err}"
                )
            return union_brep

    def _create_inner_brep_with_caps(self):
        """Codo interior + Caps"""

        if self.type_manguito != 3:

            # Elbow interior base
            inner_core = self._create_manguito_brep(self.param)

            # Left Cap
            cap1_origin = AllplanGeometry.Point3D(-(self.param["CAP_ARM_X"]), 0.0, 0.0)
            cap1_place = AllplanGeometry.AxisPlacement3D(cap1_origin)
            cap1_local = AllplanGeometry.BRep3D.CreateCuboid(
                cap1_place,
                self.param["CAP_ARM_X"],
                self.param["CAP_ARM_Y"],
                self.param["CAP_HEIGHT"],
            )

            # UNION: elbow interior + cap1
            err, inner_with_cap1 = AllplanGeometry.MakeUnion(inner_core, cap1_local)
            if err != 0:
                raise Exception(f"Error en MakeUnion(inner_core, cap1): código {err}")

            # Right Cap
            cap2_origin = AllplanGeometry.Point3D(self.param["ARM_LEN_X"], 0.0, 0.0)
            cap2_place = AllplanGeometry.AxisPlacement3D(cap2_origin)

            cap2_local = AllplanGeometry.BRep3D.CreateCuboid(
                cap2_place,
                self.param["CAP_ARM_X"],
                self.param["CAP_ARM_Y"],
                self.param["CAP_HEIGHT"],
            )

            # UNION (inner + Cap Left) + Cap Right
            err, inner_with_caps = AllplanGeometry.MakeUnion(
                inner_with_cap1, cap2_local
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(inner_with_cap1, cap2): código {err}"
                )

            return inner_with_caps
        else:
            """Caso especial con MØ25-20"""
            special_param = {
                "MDL_ARM_LEN_X": self.param["MDL_ARM_LEN_X"],
                "MDL_ARM_LEN_Y": self.param["MDL_ARM_LEN_Y"],
                "MDL_HEIGHT": self.param["MDL_HEIGHT"],
                "COLOR": self.param["COLOR"],
                "MDR_ARM_LEN_X": self.param["MDR_ARM_LEN_X"],
                "MDR_ARM_LEN_Y": self.param["MDR_ARM_LEN_Y"],
                "MDR_HEIGHT": self.param["MDR_HEIGHT"],
            }
            special_manguito = self._create_manguito_brep(special_param)

            # Left Cap
            left_cap_origin = AllplanGeometry.Point3D(
                -(self.param["LEFT_CAP_ARM_X"]), 0, 0
            )
            left_cap_place = AllplanGeometry.AxisPlacement3D(left_cap_origin)

            left_cap = AllplanGeometry.BRep3D.CreateCuboid(
                left_cap_place,
                self.param["LEFT_CAP_ARM_X"],
                self.param["LEFT_CAP_ARM_Y"],
                self.param["LEFT_CAP_HEIGHT"],
            )

            err, special_with_left_cap = AllplanGeometry.MakeUnion(
                special_manguito, left_cap
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(special_manguito, left_cap): código {err}"
                )

            right_cap_x_position = (
                special_param["MDL_ARM_LEN_X"] + special_param["MDR_ARM_LEN_X"]
            )
            right_cap_y_position = (
                self.param["MDR_ARM_LEN_Y"] - self.param["MDL_ARM_LEN_Y"]
            ) / 2

            # Right Cap
            right_cap_origin = AllplanGeometry.Point3D(
                right_cap_x_position, -(right_cap_y_position), 0
            )
            right_cap_place = AllplanGeometry.AxisPlacement3D(right_cap_origin)
            right_cap = AllplanGeometry.BRep3D.CreateCuboid(
                right_cap_place,
                self.param["RIGHT_CAP_ARM_X"],
                self.param["RIGHT_CAP_ARM_Y"],
                self.param["RIGHT_CAP_HEIGHT"],
            )

            err, special_with_both_caps = AllplanGeometry.MakeUnion(
                special_with_left_cap, right_cap
            )
            if err != 0:
                raise Exception(
                    f"Error en MakeUnion(special_with_left_cap, right_cap): código {err}"
                )

            return special_with_both_caps

    def _create_brep(self):
        """Outer + Inner"""
        if self.type_manguito != 3:
            outer_core = self._create_inner_brep_with_caps()

            return outer_core
        else:
            """Caso especial con MØ25-20"""
            special_manguito = self._create_inner_brep_with_caps()
            return special_manguito

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        p = self.param

        # Creo los atributos una sola vez
        attributes = self._create_attributes()

        # ================== CENTRADO EN X/Y/Z ==================
        if self.type_manguito != 3:
            # Caso normal MØ20 / MØ25
            brep = self._create_brep()

            # Usamos el cap del lado de 20mm cuando exista,
            # si no, caemos al propio ARM_LEN_Y / HEIGHT
            cap_y = float(p.get("CAP_ARM_Y", p.get("ARM_LEN_Y", 0.0)))
            cap_z = float(p.get("CAP_HEIGHT", p.get("HEIGHT", 0.0)))

            # Centrado en X: el brep va de -CAP_ARM_X a ARM_LEN_X + CAP_ARM_X
            # El centro está en ARM_LEN_X / 2
            arm_len_x = float(p.get("ARM_LEN_X", 0.0))
            half_x = arm_len_x * 0.5

            half_y = cap_y * 0.5
            half_z = cap_z * 0.5

            mat_center = AllplanGeometry.Matrix3D()
            # Centramos en X, Y y Z
            mat_center.SetTranslation(
                AllplanGeometry.Vector3D(-half_x, -half_y, -half_z)
            )

            brep_centered = AllplanGeometry.Transform(brep, mat_center)

            props = AllplanBaseElements.CommonProperties()
            props.GetGlobalProperties()
            props.Color = p["COLOR"]

            model = AllplanBasisElements.ModelElement3D(props, brep_centered)

            if attributes is not None:
                model.SetAttributes(attributes)

            return [model]

        else:
            # Caso especial reductor MØ25-20
            brep = self._create_brep()

            # Tomamos como referencia el CAP de 20mm (lado LEFT)
            cap_y = float(p.get("LEFT_CAP_ARM_Y", 0.0))
            cap_z = float(p.get("LEFT_CAP_HEIGHT", 0.0))

            # Centrado en X: el brep va de -LEFT_CAP_ARM_X a MDL_ARM_LEN_X + MDR_ARM_LEN_X + RIGHT_CAP_ARM_X
            # El centro está en: (MDL_ARM_LEN_X + MDR_ARM_LEN_X + RIGHT_CAP_ARM_X - LEFT_CAP_ARM_X) / 2
            left_cap_x = float(p.get("LEFT_CAP_ARM_X", 0.0))
            mdl_arm_x = float(p.get("MDL_ARM_LEN_X", 0.0))
            mdr_arm_x = float(p.get("MDR_ARM_LEN_X", 0.0))
            right_cap_x = float(p.get("RIGHT_CAP_ARM_X", 0.0))

            # Longitud total en X
            total_x = left_cap_x + mdl_arm_x + mdr_arm_x + right_cap_x
            # El punto inicial es -left_cap_x, así que el centro es:
            half_x = (total_x * 0.5) - left_cap_x

            half_y = cap_y * 0.5
            half_z = cap_z * 0.5

            mat_center = AllplanGeometry.Matrix3D()
            # Centramos en X, Y y Z
            mat_center.SetTranslation(
                AllplanGeometry.Vector3D(-half_x, -half_y, -half_z)
            )

            brep_centered = AllplanGeometry.Transform(brep, mat_center)

            props = AllplanBaseElements.CommonProperties()
            props.GetGlobalProperties()
            props.Color = p["COLOR"]

            model = AllplanBasisElements.ModelElement3D(props, brep_centered)

            if attributes is not None:
                model.SetAttributes(attributes)

            return [model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    mangui = ManguitoModel(build_ele, doc)
    model_list = mangui.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
