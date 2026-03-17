import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplnaBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


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
    },
]

MAP_TAPS = {
    'TAP 1/2"': 0,
}


class TapsModel:
    """Clase que representa Taps"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoTaps", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_taps = MAP_TAPS.get(str(type_val), 0)
        self.param = PARAMS[self.type_taps]

        common_properties = AllplnaBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

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

        model_list = []

        # Outer
        if outer_brep is not None:
            outer_props = AllplnaBaseElements.CommonProperties()
            outer_props.GetGlobalProperties()
            outer_props.Color = p["COLOR"]
            outer_model = AllplanBasisElements.ModelElement3D(outer_props, outer_brep)
            model_list.append(outer_model)
        if inner_brep is not None:
            pass

        return model_list


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    taps = TapsModel(build_ele)
    model_list = taps.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
