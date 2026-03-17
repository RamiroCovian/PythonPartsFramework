import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplnaBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = {}

MAP_TE_SORTIDA = {
    'Ø20x1/2"': 0,
}


class TeSortidaModel:
    """Clase que representa Te Sortidas"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoTeSortida", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_te_sortidas = MAP_TE_SORTIDA.get(str(type_val), 0)
        self.param = PARAMS[self.type_te_sortidas]

        common_properties = AllplnaBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_te_sortidas_brep(self, param: dict):
        """Te Sortidas externo"""

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        pass

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        pass


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    te_sortidas = TeSortidaModel(build_ele)
    model_list = te_sortidas.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
