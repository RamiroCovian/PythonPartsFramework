from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


from .tub_polietile_007_is import TubPolietileModel
from .tub_polietile_007_td import TubPolietileTDModel


def check_allplan_version(_build_ele, version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return PolietileScript(build_ele, script_object_data)


# --- Clase Principal del PythonPart ---
class PolietileScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un tub polietile."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        """
        Devuelve la lista de atributos que usan los modelos de tubería de polietile
        (pmp_*, ATTR0X, 6_CC_IS, etc.), para que el PythonPart herede los mismos
        atributos que el 3D resultante.
        """
        dist_type = kwargs.get("dist_type")

        # Si no nos indican el tipo de distribución, asumimos IS por defecto
        if dist_type not in ("IS", "TD"):
            dist_type = "IS"

        try:
            if dist_type == "IS":
                tub = TubPolietileModel(self.build_ele, self.doc)
            else:
                tub = TubPolietileTDModel(self.build_ele, self.doc)

            # Reutilizamos la misma construcción de atributos que usan los modelos
            create_attrs = getattr(tub, "_create_attributes", None)
            if callable(create_attrs):
                attrs = create_attrs()
                if attrs:
                    return [attrs]
        except Exception:
            # Si algo falla, devolvemos lista vacía para no bloquear el PythonPart
            pass

        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        # diameter y water_type opcionales recibidos desde la polilínea
        diameter = args[0] if args else kwargs.get("diameter")
        dist_type = kwargs.get("dist_type")
        water_type = kwargs.get("water_type")

        # Usamos DiametroAplicar como punto de unión con los modelos TubPolietile*,
        # que ya leen este parámetro para decidir el índice de diámetro.
        if diameter is not None:
            diam_attr = getattr(self.build_ele, "DiametroAplicar", None)
            try:
                diam_int = int(diameter)
            except Exception:
                diam_int = None

            if diam_int is not None:
                try:
                    if diam_attr is not None and hasattr(diam_attr, "value"):
                        diam_attr.value = diam_int  # type: ignore[attr-defined]
                    else:
                        setattr(self.build_ele, "DiametroAplicar", diam_int)
                except Exception:
                    # En caso de fallo, seguimos sin romper la creación del elemento
                    pass

        # También trasladamos el tipo de agua para que los modelos TubPolietile*
        # no tengan que caer al valor por defecto.
        if water_type:
            target_names = []
            if dist_type == "IS":
                target_names = ["TipoDeAguaIS", "TipoDeAgua"]
            elif dist_type == "TD":
                target_names = ["TipoDeAguaTD", "TipoDeAgua"]
            else:
                target_names = ["TipoDeAgua"]

            for name in target_names:
                try:
                    attr = getattr(self.build_ele, name, None)
                    if attr is not None and hasattr(attr, "value"):
                        attr.value = str(water_type)
                    else:
                        setattr(self.build_ele, name, str(water_type))
                except Exception:
                    # Si falla uno, probamos el siguiente nombre sin romper la ejecución
                    continue

        model_ele_list = None
        if dist_type == "IS":
            tub = TubPolietileModel(self.build_ele, self.doc)
            model_ele_list = tub.build()
        else:
            tub = TubPolietileTDModel(self.build_ele, self.doc)
            model_ele_list = tub.build()

        return CreateElementResult(model_ele_list)
