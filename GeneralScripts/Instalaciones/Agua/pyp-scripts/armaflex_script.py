from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
import NemAll_Python_Utility as PythonUtility

from .armaflex_009_td import ArmaflexModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


# --- Clase Principal del PythonPart ---
class ArmaflexScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un armaflex."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        """
        Devuelve atributos por defecto del modelo armaflex (TD).
        """
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")

        # No hay armaflex IS
        if dist_type == "IS":
            return []

        if diameter is not None:
            tipo_valor = None
            try:
                diam_int = int(diameter)
            except Exception:
                diam_int = None

            if diam_int is not None:
                if diam_int == 20:
                    tipo_valor = "Ø20/9mm"
                elif diam_int == 25:
                    tipo_valor = "Ø25"
                elif diam_int == 32:
                    tipo_valor = "Ø32"

            if tipo_valor:
                try:
                    tipo_attr = getattr(self.build_ele, "TipoArmaflex", None)
                    if tipo_attr is not None and hasattr(tipo_attr, "value"):
                        tipo_attr.value = tipo_valor
                    else:
                        setattr(self.build_ele, "TipoArmaflex", tipo_valor)
                except Exception:
                    pass

        try:
            tub = ArmaflexModel(self.build_ele, self.doc)
            create_attrs = getattr(tub, "_create_attributes", None)
            if callable(create_attrs):
                attrs = create_attrs()
                if attrs:
                    return [attrs]
        except Exception:
            pass

        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """
        Ejecuta la creación del armaflex.
        Acepta parámetros opcionales desde la polilínea:
        - diameter: diámetro elegido (20, 25, 32, ...)
        - dist_type: tipo de distribución ("IS" o "TD")
        - water_type: tipo de agua ("Fred", "Calent", etc.) – reservado para futura ampliación
        """
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")
        water_type = kwargs.get("water_type")

        # De momento solo existe versión TD de armaflex.
        if dist_type == "IS":
            PythonUtility.ShowMessageBox(
                "Este tipo de tubo no existe o no está disponible para la distribución IS.\n\n"
                "Para continuar:\n"
                "1) Vuelva a Modo creación.\n"
                "2) Cambie la distribución a TD.\n"
                "3) Regrese a Modo configuración.",
                PythonUtility.MB_OK,
            )
            return CreateElementResult([])

        # Si viene un diámetro desde la polilínea, lo mapeamos al tipo de armaflex
        # para que ArmaflexModel seleccione el índice correcto vía TipoArmaflex.
        if diameter is not None:
            tipo_valor = None
            try:
                diam_int = int(diameter)
            except Exception:
                diam_int = None

            if diam_int is not None:
                if diam_int == 20:
                    tipo_valor = "Ø20/9mm"
                elif diam_int == 25:
                    tipo_valor = "Ø25"
                elif diam_int == 32:
                    tipo_valor = "Ø32"

            if tipo_valor:
                try:
                    tipo_attr = getattr(self.build_ele, "TipoArmaflex", None)
                    if tipo_attr is not None and hasattr(tipo_attr, "value"):
                        tipo_attr.value = tipo_valor
                    else:
                        setattr(self.build_ele, "TipoArmaflex", tipo_valor)
                except Exception:
                    # Si algo falla, seguimos sin interrumpir la creación
                    pass

        tub = ArmaflexModel(self.build_ele, self.doc)
        model_ele_list = tub.build()

        return CreateElementResult(model_ele_list)
