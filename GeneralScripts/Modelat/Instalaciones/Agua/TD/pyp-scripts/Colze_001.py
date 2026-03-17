import math
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


class ElbowModel:
    """Guardo todos los parametros geometricos del codo."""

    # Indice 0 -> CØ20, Indice 1 -> CØ25
    PARAMS = [
        # CØ20
        {  # Outer
            "ARM_LEN_X": 40.0,
            "ARM_LEN_Y": 75.0,
            "THICKNESS": 40.0,
            "HEIGHT": 40.0,
            "COLOR": 5,
            # Inner
            "INNER_ARM_X": 30.0,
            "INNER_ARM_Y": 42.0,
            "INNER_THICKNESS": 30.0,
            "INNER_HEIGHT": 30.0,
            "INNER_COLOR": 3,
            # Caps
            "CAP_ARM_X": 30.0,
            "CAP_ARM_Y": 23.0,
            "CAP_THICKNESS": 30.0,
            "CAP_HEIGHT": 31.0,
            # Dif Outer/Inner
            "SPACE": 5.0,
        },
        # CØ25
        {  # Outer
            "ARM_LEN_X": 75.0,
            "ARM_LEN_Y": 115.0,
            "THICKNESS": 75.0,
            "HEIGHT": 75.0,
            "COLOR": 128,
            # Inner
            "INNER_ARM_X": 35.0,
            "INNER_ARM_Y": 52.0,
            "INNER_THICKNESS": 35.0,
            "INNER_HEIGHT": 35.0,
            "INNER_COLOR": 3,
            # Caps
            "CAP_ARM_X": 35.0,
            "CAP_ARM_Y": 23.0,
            "CAP_THICKNESS": 35.0,
            "CAP_HEIGHT": 36.0,
            # Dif Outer/Inner
            "SPACE": 20.0,
        },
    ]

    def __init__(self, build_ele):
        # Leo el tipo desde el RadioButtonGroup
        self.tipo = self._int_value(getattr(build_ele, "TipoCodo", None), 0)
        self.param = ElbowModel.PARAMS[self.tipo]

        # Propiedades comunes
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

        # MakeSubtraction: outer - inner
        # err, final_brep = AllplanGeometry.MakeSubtraction(outer_core, inner_centered)
        # if err != 0:
        #     raise Exception(
        #         f"Error en MakeSubtraction(outer_core, inner_centered): código {err}"
        #     )

        return outer_core, inner_centered

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""

        outer_brep, inner_brep = self._create_brep()
        p = self.param

        # Propiedades outer
        outer_props = AllplanBaseElements.CommonProperties()
        outer_props.GetGlobalProperties()
        outer_props.Color = p["COLOR"]

        # Propiedades inner
        inner_props = AllplanBaseElements.CommonProperties()
        inner_props.GetGlobalProperties()
        inner_props.Color = p["INNER_COLOR"]

        outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
        inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)
        return [outer_model, inner_model]


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """
    Creo el elemento final.
    """

    elbow = ElbowModel(build_ele)
    model_list = elbow.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
