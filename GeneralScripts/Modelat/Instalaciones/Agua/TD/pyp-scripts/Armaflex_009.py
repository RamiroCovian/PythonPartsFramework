import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = [
    # Ø20/9mm
    {  # Outer
        "ARM_LEN_X": 140.0,
        "ARM_LEN_Y": 40.0,
        "HEIGHT": 40.0,
        "COLOR": 5,
        # Inner
        "INNER_ARM_X": 140.0,
        "INNER_ARM_Y": 38.0,
        "INNER_HEIGHT": 38.0,
        "INNER_COLOR": 1,
        "SPACE": 1.0,
    },
    # Ø25
    {  # Outer
        "ARM_LEN_X": 154.64,
        "ARM_LEN_Y": 75.0,
        "HEIGHT": 75.0,
        "COLOR": 128,
        "SMALL_ARM_X": 40.0,
        "SMALL_ARM_Y": 35.0,
        # Inner
        "INNER_ARM_X": 154.64,
        "INNER_ARM_Y": 71.0,
        "INNER_HEIGHT": 75.0,
        "INNER_COLOR": 1,
        "SPACE": 2.0,
    },
    # Ø32
    {  # Outer
        "ARM_LEN_X": 0.0,
        "ARM_LEN_Y": 0.0,
        "HEIGHT": 0.0,
        "COLOR": 0,
        "SMALL_ARM_X": 0.0,
        "SMALL_ARM_Y": 0.0,
        # Inner
        "INNER_ARM_X": 0.0,
        "INNER_ARM_Y": 0.0,
        "INNER_HEIGHT": 0.0,
        "INNER_COLOR": 0,
        "SPACE": 0.0,
    },
]

MAP_ARMAFLEX = {
    "Ø20/9mm": 0,
    "Ø25": 1,
    "Ø32": 2,
}


class ArmaflexModel:
    """Clase que representa Armaflex"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoArmaflex", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_armaflex = MAP_ARMAFLEX.get(str(type_val), 0)
        self.param = PARAMS[self.type_armaflex]

        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_armaflex_brep(self, param: dict):
        """Armaflex externo"""
        origin = AllplanGeometry.Point3D(0, 0, 0)
        placement = AllplanGeometry.AxisPlacement3D(origin)

        if self.type_armaflex < 2:
            armaflex_brep = AllplanGeometry.BRep3D.CreateCuboid(
                placement,
                param["ARM_LEN_X"],
                param["ARM_LEN_Y"],
                param["HEIGHT"],
            )
        else:
            print("No hemos creado este Brep todavia!. (_create_armaflex_brep)")

        return armaflex_brep

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        outer_core = None
        inner_core = None

        inner_param = {
            "ARM_LEN_X": self.param["INNER_ARM_X"],
            "ARM_LEN_Y": self.param["INNER_ARM_Y"],
            "HEIGHT": self.param["INNER_HEIGHT"],
            "COLOR": self.param["INNER_COLOR"],
        }

        if self.type_armaflex < 2:
            outer_core = self._create_armaflex_brep(self.param)
            inner_core = self._create_armaflex_brep(inner_param)

            # CENTRO EL INNER DENTRO DEL OUTER
            # Distancia entre outer e inner
            dx = 0
            dy = self.param["SPACE"]
            dz = self.param["SPACE"]

            mat_t = AllplanGeometry.Matrix3D()
            mat_t.SetTranslation(AllplanGeometry.Vector3D(dx, dy, dz))
            inner_core = AllplanGeometry.Transform(inner_core, mat_t)
        else:
            print("No hemos creado este Brep todavia!. (_create_brep)")

        return outer_core, inner_core

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        outer_brep, inner_brep = self._create_brep()
        p = self.param

        model_list = []

        # Outer
        if outer_brep is not None:
            outer_props = AllplanBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
            model_list.append(outer_model)

        # Inner (solo para type_te < 3)
        if inner_brep is not None and self.type_armaflex < 2:
            inner_props = AllplanBaseElements.CommonProperties()
            inner_props.GetGlobalProperties()
            inner_props.Color = p["INNER_COLOR"]
            inner_model = AllplanBasisElements.ModelElement3D(inner_props, inner_brep)
            model_list.append(inner_model)

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    armaflex = ArmaflexModel(build_ele)
    model_list = armaflex.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
