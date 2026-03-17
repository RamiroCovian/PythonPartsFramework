import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplnaBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = {}

MAP_TUB_MULTICAPA = {
    "Ø20/2mm": 0,
    "Ø25/2,5mm": 1,
    "Ø32/3mm": 2,
}


class TubMulticapaModel:
    """Clase que representa Tub Multicapa"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoTubMulticapa", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_tub_multicapa = MAP_TUB_MULTICAPA.get(str(type_val), 0)
        self.param = PARAMS[self.type_tub_multicapa]

        common_properties = AllplnaBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_tub_multicapa_brep(self, param: dict):
        """Tub Multicapa externo"""

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        pass

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        pass


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    tub_multicapa = TubMulticapaModel(build_ele)
    model_list = tub_multicapa.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
