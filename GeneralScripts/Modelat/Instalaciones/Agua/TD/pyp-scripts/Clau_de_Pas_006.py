import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplnaBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = {}

MAP_CLAUDEPAS = {
    "CPØ20": 0,
    "CPØ25": 1,
    "CPØ32": 2,
}


class ClauDePasModel:
    """Clase que representa Clau de Pas"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoClaudePas", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_clau_de_pas = MAP_CLAUDEPAS.get(str(type_val), 0)
        self.param = PARAMS[self.type_clau_de_pas]

        common_properties = AllplnaBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_clau_de_pas_brep(self, param: dict):
        """Clau de Pas externo"""

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        pass

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        pass


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    clau_de_pas = ClauDePasModel(build_ele)
    model_list = clau_de_pas.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
