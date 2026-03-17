from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_Utility as PythonUtility

from .tub_multicapa_008_td import TubMulticapaTDModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return MulticapaScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class MulticapaScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un tub multicapa."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, value: int = 0):

        attr_list = []
        return attr_list

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """
        Ejecuta la creación del tub multicapa.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.)
        """
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")
        water_type = kwargs.get("water_type")

        # De momento solo existe la versión TD de multicapa.
        if dist_type == "IS":
            PythonUtility.ShowMessageBox(
                "Este tipo de tub multicapa no existe o no está disponible para la distribución IS.",
                PythonUtility.MB_OK,
            )
            return CreateElementResult([])

        # Si viene un diámetro desde la polilínea, lo mapeamos al tipo de multicapa
        # para que TubMulticapaTDModel seleccione el índice correcto.
        if diameter is not None:
            tipo_valor = None
            try:
                diam_int = int(diameter)
            except Exception:
                diam_int = None

            if diam_int is not None:
                if diam_int == 20:
                    tipo_valor = "Ø20/2mm"
                elif diam_int == 25:
                    tipo_valor = "Ø25/2,5mm"
                elif diam_int == 32:
                    tipo_valor = "Ø32/3mm"

            if tipo_valor:
                try:
                    tipo_attr = getattr(self.build_ele, "TipoTubMulticapa", None)
                    if tipo_attr is not None and hasattr(tipo_attr, "value"):
                        tipo_attr.value = tipo_valor
                    else:
                        setattr(self.build_ele, "TipoTubMulticapa", tipo_valor)
                except Exception:
                    # Si algo falla, seguimos sin interrumpir la creación
                    pass

        # Trasladamos también el tipo de agua, para mantener coherencia con polietile
        if water_type:
            try:
                # De momento solo almacenamos en TipoDeAguaTD / TipoDeAgua
                for name in ("TipoDeAguaTD", "TipoDeAgua"):
                    attr = getattr(self.build_ele, name, None)
                    if attr is not None and hasattr(attr, "value"):
                        attr.value = str(water_type)
                    else:
                        setattr(self.build_ele, name, str(water_type))
            except Exception:
                pass

        tub = TubMulticapaTDModel(self.build_ele, self.doc)
        model_ele_list = tub.build()
        return CreateElementResult(model_ele_list)
