import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


class ManguitoModel:
    """Guardamos los parametros geometricos de los manguitos"""

    PARAMS = [
        # MØ20
        {
            # Outer
            "ARM_LEN_X": 85.0,
            "ARM_LEN_Y": 40.0,
            "THICKNESS": 40.0,
            "HEIGHT": 35.0,
            "COLOR": 5,
            # Inner
            "INNER_ARM_X": 29.0,
            "INNER_ARM_Y": 30.0,
            "INNER_THICKNESS": 30.0,
            "INNER_HEIGHT": 30.0,
            "INNER_COLOR": 16,
            # Caps
            "CAP_ARM_X": 23.0,
            "CAP_ARM_Y": 30.0,
            "CAP_THICKNESS": 30.0,
            "CAP_HEIGHT": 31.0,
            # Dif Outer/Inner
            "SPACE": 5.0,
        },
        # MØ25
        {
            # Outer
            "ARM_LEN_X": 120.0,
            "ARM_LEN_Y": 75.0,
            "THICKNESS": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 128,
            # Inner
            "INNER_ARM_X": 34.0,
            "INNER_ARM_Y": 35.0,
            "INNER_THICKNESS": 35.0,
            "INNER_HEIGHT": 35.0,
            "INNER_COLOR": 16,
            # Caps
            "CAP_ARM_X": 23.0,
            "CAP_ARM_Y": 35.0,
            "CAP_THICKNESS": 35.0,
            "CAP_HEIGHT": 36.0,
            # Dif Outer/Inner
            "SPACE": 20.0,
        },
        # MØ32
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
        # MØ25-20
        {
            # Middle-left
            "MDL_ARM_LEN_X": 12.0,
            "MDL_ARM_LEN_Y": 30.0,
            "MDL_THICKNESS": 30.0,
            "MDL_HEIGHT": 30.0,
            "COLOR": 16,
            # Middle-Right
            "MDR_ARM_LEN_X": 17.0,
            "MDR_ARM_LEN_Y": 35.0,
            "MDR_THICKNESS": 35.0,
            "MDR_HEIGHT": 30.0,
            # Left Cap
            "LEFT_CAP_ARM_X": 23.0,
            "LEFT_CAP_ARM_Y": 30.0,
            "LEFT_CAP_THICKNESS": 30.0,
            "LEFT_CAP_HEIGHT": 31.0,
            # Right Cap
            "RIGHT_CAP_ARM_X": 23.0,
            "RIGHT_CAP_ARM_Y": 35.0,
            "RIGHT_CAP_THICKNESS": 35.0,
            "RIGHT_CAP_HEIGHT": 31.0,
            # Dif Outer/Inner
            "SPACE": 0.0,
        },
        # MØ32x25
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
    ]

    def __init__(self, build_ele):
        self.type_manguito = self._int_value(
            getattr(build_ele, "TipoManguito", None), 0
        )
        self.param = ManguitoModel.PARAMS[self.type_manguito]

        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = self.param["COLOR"]
        self.common_props = common_properties

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
            # Parametros del inner
            inner_param = {
                "ARM_LEN_Y": self.param["INNER_ARM_Y"],
                "ARM_LEN_X": self.param["INNER_ARM_X"],
                "THICKNESS": self.param["INNER_THICKNESS"],
                "HEIGHT": self.param["INNER_HEIGHT"],
                "COLOR": self.param["INNER_COLOR"],
            }

            # Elbow interior base
            inner_core = self._create_manguito_brep(inner_param)

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
            cap2_origin = AllplanGeometry.Point3D(inner_param["ARM_LEN_X"], 0.0, 0.0)
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
                "MDL_THICKNESS": self.param["MDL_THICKNESS"],
                "MDL_HEIGHT": self.param["MDL_HEIGHT"],
                "COLOR": self.param["COLOR"],
                "MDR_ARM_LEN_X": self.param["MDR_ARM_LEN_X"],
                "MDR_ARM_LEN_Y": self.param["MDR_ARM_LEN_Y"],
                "MDR_THICKNESS": self.param["MDR_THICKNESS"],
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
            # Outer segun los parametros principales
            outer_param = {
                "ARM_LEN_Y": self.param["ARM_LEN_Y"],
                "ARM_LEN_X": self.param["ARM_LEN_X"],
                "THICKNESS": self.param["THICKNESS"],
                "HEIGHT": self.param["HEIGHT"],
                "COLOR": self.param["COLOR"],
            }

            outer_core = self._create_manguito_brep(outer_param)
            inner_with_caps = self._create_inner_brep_with_caps()

            # CENTRO EL INNER DENTRO DEL OUTER
            # Distancia entre outer e inner
            dx = self.param["SPACE"] + self.param["CAP_ARM_X"]
            dy = self.param["SPACE"]
            dz = self.param["SPACE"]

            mat_t = AllplanGeometry.Matrix3D()
            mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
            inner_centered = AllplanGeometry.Transform(inner_with_caps, mat_t)

            return outer_core, inner_centered
        else:
            """Caso especial con MØ25-20"""
            special_manguito = self._create_inner_brep_with_caps()
            return special_manguito

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        p = self.param
        if self.type_manguito != 3:
            outer_brep, inner_brep = self._create_brep()

            # Propiedades outer
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]

            # # Propiedades inner
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p["INNER_COLOR"]

            outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
            inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)
            return [outer_model, inner_model]
        else:
            special_brep = self._create_brep()
            special_props = AllplanBaseElements.CommonProperties()
            special_props.GetGlobalProperties()
            special_props.Color = p["COLOR"]

            special_model = AllplanBasisElements.ModelElement3D(
                special_props, special_brep
            )
            return [special_model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    mangui = ManguitoModel(build_ele)
    model_list = mangui.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
