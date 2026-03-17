import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplnaBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, version) -> bool:
    return True


PARAMS = {}

# Ver que opcion es mejor, una lista de 2 diccionarios?
MAP_TUB_POLIETILE = {
    "Ø20-5ML - Fred": 0,
    "Ø20-5ML - Calent": 1,
    "Ø25-5ML - Fred": 2,
    "Ø25-5ML - Calent": 3,
    "Ø32-5ML - Fred": 4,
    "Ø32-5ML - Calent": 5,
}


class TubPolietileModel:
    """Clase que representa Tub Polietilè"""

    def __init__(self, build_ele):
        type_raw = getattr(build_ele, "TipoTubPolietile", None)
        type_val = getattr(type_raw, "value", type_raw)

        # Mapeo string a indice
        self.type_tub_polietile = MAP_TUB_POLIETILE.get(str(type_val), 0)
        self.param = PARAMS[self.type_tub_polietile]

        common_properties = AllplnaBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = int(self.param["COLOR"])
        self.common_props = common_properties

    def _create_tub_polietile_brep(self, param: dict):
        """Tub Polietilè externo"""

    def _create_brep(self):
        """Outer + Inner (si aplica)"""
        pass

    def build(self):
        """Devuelvo el ModelElement3D para Allplan."""
        pass


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    """Creo el elemento final."""
    tub_polietile = TubPolietileModel(build_ele)
    model_list = tub_polietile.build()

    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
