from __future__ import annotations

import json, random, hashlib, ast

from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Dict, Any

if TYPE_CHECKING:
    from .interactor import PolylineInteractor

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    import NemAll_Python_AllplanSettings as AllplanSettings
    import NemAll_Python_IFW_Input as AllplanIFW
    import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False

from NemAll_Python_BaseElements import LayerService
from NemAll_Python_BaseElements import AttributeService
from BaseScriptObject import BaseScriptObject
from PythonPart import PythonPartGroup
from PythonPart import View2D3D, PythonPart
from PythonPartTransaction import PythonPartTransaction
from DocumentManager import DocumentManager
from TypeCollections.ModificationElementList import ModificationElementList

from .models import PolylineBaseConfig, InstallationElement, DistributionTypes, FacesEN, GeneratedElement, SegmentInfo, WaterTypes
from .parameters import ParamNames
from .utils import ElementSerializer
from .installation_registry import (
    auto_load_installations,
    get_installation as registry_get_installation,
    get_pythonpart
)


# ===== ScriptObject Implementation =====
class PolylineScriptObject(BaseScriptObject if ALLPLAN_AVAILABLE else object):  # type: ignore
    """ScriptObject for polyline creation and editing. (It functions as database)
    Maintains state between interactions and handles element creation.
    """
    def __init__(self, build_ele, script_object_data):
        # if ALLPLAN_AVAILABLE:
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc: Any  = None
        self.script_object_interactor: Optional[PolylineInteractor] = None
        self.ctrl_prop_util = getattr(script_object_data, "control_props_util")
        self.init_storage: Any = None

        # Store polyline paths and segments
        self.saved_paths: List[List[AllplanGeo.Point3D]] = []
        self.polilyne: List[AllplanGeo.Point3D] = []
        self.generated_elements: List[List[InstallationElement]] = []
        self.installation_types: list = []

        self.element_list: List[List[GeneratedElement]] = []
        self.element_list_final = []
        self.pythonpart_group_list = []
        self.copy_element_list = []

        self.selected_inst_type: str | None = None
        self.min_segment_length: float | int = 0
        self.diameter_list: List[int] | None = None
        self.diameter_type: int = 0

        self.crear_pythonpart: bool = True
        self._fn_name: str | None = None
        self.distribution_type: str | None = None
        self.water_type: str | None = None
        self.face_en: str | None = None
        self.support_angles: str | None = None
        self.reference_orientation_angle: float | None = None

        self.data_restore = []
        self.segment_groups = []
        self.saved_segments = []
        self.bifurcation_nodes: Dict = {}
        self.persistent_metadata: dict[str, SegmentInfo] = {}

        # Store configuration self._config = config
        self._config: Optional[PolylineBaseConfig | None] = None

        # Element assembly hooks (callbacks for installations to customize element creation)
        self.element_creation_preview_hook: Optional[Callable] = None  # Called for each segment: hook(segment_data, properties)
        self.element_creation_layer_attrs_hook: Optional[Callable] = None  # Called for each segment: hook(segment_data, idx, properties)

        self.global_group_numbers: Dict = {} # Aquí se guardará la consistencia entre paths

        # ----------------------- NEW VARIABLES -----------------------
        self.allowed_connections = []
        self.allowed_angles = []
        self.is_individual_mode: bool = True
        self.current_inst_config: Dict = {}
        self.pythonparts_modules: list = []
        self.element_type_core = ""
        self.inst_color = 1

        self.selected_element_id: Tuple | None = None  # ID del elemento actualmente seleccionado
        self.selected_segments = set()

        self.layer_types: list = []

        self.default_layers: Dict = {}
        self.default_attributes: Dict = {}
        self.pmp_pare_default: Dict = {}

        self.applied_layers: Dict = {}
        self.applied_attributes: Dict = {}

        self.applied_default_attributes: Dict = {}
        self.hover_tooltip_text: str = ""

        # Instrumentation/debugging
        self._debug = False  # Enable debug logging
        self._diagnostics: List[str] = []  # Store diagnostic messages

    def set_config(self, config: PolylineBaseConfig) -> None:
        """Set the configuration for this script object."""
        self._config = config
        if config.registry_auto_load:
            try:
                # self.build_ele.parameter_data["CheckBoxLimitarAngulos"] = config.limit_angles
                if config.default_installation:
                    auto_load_installations(
                        config.registry_base_folder, config.default_installation.lower()
                    )
            except Exception:
                pass

    def start_input(self):
        from .interactor import PolylineInteractor
        """Initialize the interactor and start input.

        Returns the interactor so Allplan can call its methods (on_cancel_function, etc.)
        """
        self.doc = self.coord_input.GetInputViewDocument()
        if self.script_object_interactor is None:
            if self._config:
                self.set_config(config=self._config)
                self.script_object_interactor = PolylineInteractor(self, self._config)

        if self.script_object_interactor and self._config:
            self._initialize_parameter_states()
            # if self._config.default_layers:
            #     self.script_object_interactor.apply_layer_default(layer=self._config.default_layer)

        print(f"[SO] Returning interactor to Allplan: {self.script_object_interactor}")
        print("[SO] start_input() complete\n")
        return self.script_object_interactor

    def _initialize_parameter_states(self):
        if self._config:
            if self._config.parameters_show:
                for parameter_name, visible in self._config.parameters_show.to_param_map().items():
                    self.show_parameter(parameter_name, visible)

            if self._config.parameters_enabled:
                for parameter_name, enabled in self._config.parameters_enabled.to_param_map().items():
                    self.enable_parameter(parameter_name, enabled)

    def _load_default_inst_params(self, installation_name=None):

        inst_name = installation_name or self._config and self._config.default_installation
        if not inst_name:
            return

        inst = registry_get_installation(inst_name)
        if inst is None:
            return

        if hasattr(inst, "label"):
            param = getattr(self.build_ele, ParamNames.Installation.NAME)
            param.value = inst.label

        if hasattr(inst, "angles"):
            self.angle_steps = inst.angles

        if hasattr(inst, "installation_types"):
            self.installation_types = inst.installation_types
            self.ctrl_prop_util.set_value_list(
                ParamNames.Installation.INSTALLATION_TYPE,
                "|".join(el['label'] for el in self.installation_types)
            )

            if self._config and self._config.parameters_enabled.functional_name:
                _value = self.installation_types[0]["label"]
                param = getattr(self.build_ele, ParamNames.General.FUNCTIONAL_NAME)
                param.value =_value

                self.selected_inst_type = _value

            if self._config and self._config.parameters_enabled.limit_angles:
                _value = self.installation_types[0]["allowed_angles"]
                param = getattr(self.build_ele, ParamNames.Installation.SUPPORTED_ANGLES)
                param.value = _value

                self.support_angles = _value

        if hasattr(inst, "layers"):
            self.layer_types = inst.layers
            self.ctrl_prop_util.set_value_list(
                "LayerTypes",
                "|".join(el['label'] for el in self.layer_types)
            )

        if hasattr(inst, "elements3D"):
            self.pythonparts_modules = inst.elements3D

        if hasattr(inst, "default_layers"):
            self.default_layers =  inst.default_layers
            if  self.script_object_interactor:
                self.script_object_interactor.apply_layer_default()

        if self._config and self._config.parameters_enabled.distribution_type:
            self.ctrl_prop_util.set_value_list(
                ParamNames.Installation.DISTRIBUTION_TYPE,
                DistributionTypes.to_value_list()
            )
            self.distribution_type = DistributionTypes.IS.value

            if self._config.parameters_enabled.water_type:
                param_name = ParamNames.Installation.WATER_TYPE
                self.show_parameter(param_name)

                if self.distribution_type:
                    water_types = WaterTypes.to_value_list(self.distribution_type)
                    self.ctrl_prop_util.set_value_list(param_name, water_types)
                else:
                    water_types = WaterTypes.to_value_list(DistributionTypes.IS)
                    self.ctrl_prop_util.set_value_list(param_name, water_types)

                self.water_type = WaterTypes.FRED.value

    def show_parameter(self, parameter_name: str, visible: bool = True):
        """
        Cambia la visibilidad solo si el parámetro existe en el build_element.
        """
        # Verificamos si el parámetro existe en el objeto build_ele
        if hasattr(self.build_ele, parameter_name) and self.ctrl_prop_util:
            condition: str = "True" if visible else "False"
            self.ctrl_prop_util.set_visible_condition(parameter_name, condition)

    def enable_parameter(self, parameter_name: str, enabled: bool = True):
        """
        Habilita/Deshabilita solo si el parámetro existe en el build_element.
        """
        if hasattr(self.build_ele, parameter_name) and self.ctrl_prop_util:
            condition: str = "True" if enabled else "False"
            self.ctrl_prop_util.set_enable_condition(parameter_name, condition)

    def resolve_installation_config(self):
        selected_type = getattr(self.build_ele, ParamNames.Installation.INSTALLATION_TYPE).value
        model_base = next(
            (item for item in self.installation_types if item["label"] == selected_type),
            None
        )
        if not model_base:
            return None

        self.current_inst_config = model_base
        self.element_type_core = model_base["key"]
        self.allowed_connections = model_base["connections"]
        self.allowed_angles = model_base["angles"]
        self.is_individual_mode =  model_base["is_individual"]
        self.inst_color = model_base["color"]
        self.support_angles = model_base["allowed_angles"]
        self.min_segment_length = model_base["min_segment_length"]

        raw_diameter = model_base["diameter"]
        is_list = isinstance(raw_diameter, list)

        self.diameter_list = raw_diameter if is_list else None
        self.show_parameter(ParamNames.Installation.DIAMETER_TYPE, is_list)

        if is_list:
            if self.diameter_list:
                self.ctrl_prop_util.set_value_list(ParamNames.Installation.DIAMETER_TYPE,
                    "|".join(str(el) for el in self.diameter_list)
                )
            self.diameter_type = raw_diameter[0]
        else:
            self.diameter_type = raw_diameter

        param = getattr(self.build_ele, ParamNames.Installation.SUPPORTED_ANGLES)
        param.value =  self.support_angles

        return model_base

    def _create_elements(self):
        """
        Crea los elementos finales de Allplan a partir de los segmentos almacenados.

        - Recorre cada grupo de segmentos (paths)
        - Aplica el hook de creación de elementos y capas si está definido
        - Almacena los elementos resultantes en `element_list_final`
        """
        # Si no existen grupos de segmentos, no hay nada para crear
        if not self.segment_groups:
            print("[SO] No hay segmentos guardados para crear")
            return

        # Reinicia el mapeo de números de grupo globales
        # (usado para mantener coherencia entre paths / elementos)
        # self.global_group_numbers = {}

        # Limpia la lista final de elementos antes de generar nuevos
        self.element_list_final = []

        # Recorre cada path (trayectoria) junto con su índice
        for path_idx, segments in enumerate(self.element_list):
            # segments = List[GeneratedElement]
            # Si existe un hook para crear elementos con atributos y capas, se delega la creación a esa función
            if self.element_creation_layer_attrs_hook:
                elements = self.element_creation_layer_attrs_hook(
                    segments,   # segmentos del path actual
                    path_idx,   # índice del path
                    self        # referencia al script object
                )
                # Se almacenan los elementos generados para su posterior uso
                self.element_list_final.append(elements)

    def _create_elements_preview(self):
        """
        Genera la representación visual (Preview) basada en los grupos de segmentos actuales.
        """
        # [PASO 1] LIMPIEZA VISUAL
        # Borramos la lista de objetos 3D anteriores antes de crear los nuevos.
        self.element_list = []

        # [PASO 2] VALIDACIÓN DE DATOS
        # Si no hay grupos de segmentos, no hacemos nada (evita errores)
        if not self.segment_groups:
            return

        # [PASO CRITICO 3] ITERACIÓN ESTRUCTURADA
        for i, segments in enumerate(self.segment_groups):
            if self.element_creation_preview_hook:
                raw_elements = self.element_creation_preview_hook(segments, self)
                if raw_elements:
                    typed_elements = [GeneratedElement(**data) for data in raw_elements]
                    self.element_list.append(typed_elements)

    def _get_pythonpart_installed(
        self,
        element_key: str,
        exec_args: tuple = (),
        exec_kwargs: dict | None = None,
        attr_args: tuple = (),
        attr_kwargs: dict | None = None
    ):
        """
        Instancia un PythonPart, ejecuta su lógica y registra atributos por defecto.
        """
        model_elems = None
        exec_kwargs = exec_kwargs or {}
        attr_kwargs = attr_kwargs or {}

        # 1. Obtención de la clase
        cls = get_pythonpart(element_key)
        if not cls:
            print(f"[PolylineInteractor] No hay PythonPart registrado para '{element_key}'")
            return None

        try:
            # 2. Instanciación
            inst = cls(self.build_ele, self)
            print(f"[PolylineInteractor] CREATED INSTANCE: {type(inst)}")

            # 3. Ejecución (Llamada única con argumentos variables)
            # Esto reemplaza el doble execute() anterior, siendo más eficiente en Allplan
            result = inst.execute(*exec_args, **exec_kwargs)
            print(f"[PolylineInteractor] Execute result: {type(result)}")

            # 4. Captura de Default Attributes (Solo si no existen para esta key)
            if element_key not in self.default_attributes and hasattr(inst, "get_attributes"):
                try:
                    attrs_list = inst.get_attributes(*attr_args, **attr_kwargs)
                    self.default_attributes[element_key] = attrs_list
                    print(f"[SO] Defaults registrados para {element_key}")
                except Exception as e:
                    print(f"Error getting attributes for {element_key}: {e}")

            # 5. Retorno de elementos de modelo
            if hasattr(result, "elements"):
                model_elems = result.elements
            else:
                print(f"[PolylineInteractor] Warning: El resultado de execute no contiene '.elements'")

        except Exception as ex:
            print(f"[PolylineInteractor] Error creating PythonPart '{element_key}': {ex}")

        return model_elems

    def start_next_input(self):
        """Cleanup resources when transitioning to next input or shutting down."""
        pass

    def execute(self):
        """Create elements from saved paths/segments.
        Returns CreateElementResult with model elements.
        Supports element creation hooks for installations to customize element creation.
        """
        pass

    def on_cancel_function(self):
        """ESC pressed - delegate to interactor if it exists."""
        print("[SO] on_cancel_function() called")
        if self.script_object_interactor:
            return self.script_object_interactor.on_cancel_function()

    def on_control_event(self, event_id: int):
        if self.script_object_interactor:
            return self.script_object_interactor.on_control_event(event_id)
        return True

    def modify_element_property(self, name: str, value: Any) -> bool:
        update_necessary = False
        print(f"[MODIFY_PROPERTY] Name: {name}, Value: {value}")

        if name == ParamNames.Installation.NAME:
            param = getattr(self.build_ele, name)
            param.value = value
            update_necessary = True

        elif name == ParamNames.Installation.INSTALLATION_TYPE:
            param = getattr(self.build_ele, name)
            param.value = value

            self.selected_inst_type = value

            param = getattr(self.build_ele, ParamNames.General.FUNCTIONAL_NAME)
            param.value = value

            self._fn_name = value

            if self.script_object_interactor:
                self.script_object_interactor._on_installation_type_changed()
            update_necessary = True

        elif name == ParamNames.Installation.DIAMETER_TYPE:
            param = getattr(self.build_ele, name)
            param.value = value

            self.diameter_type = value
            update_necessary = True

        elif name == ParamNames.General.FUNCTIONAL_NAME:
            param = getattr(self.build_ele, name)
            param.value = value

            self._fn_name = value
            update_necessary = True

        elif name == ParamNames.Installation.DISTRIBUTION_TYPE:
            param = getattr(self.build_ele, name)
            param.value = value

            self.distribution_type = value

            if value == DistributionTypes.EN.value and self._config:
                param_name = ParamNames.Installation.FACE_EN
                self.show_parameter(param_name)
                self.ctrl_prop_util.set_value_list(param_name, FacesEN.to_value_list())
            else:
                self.show_parameter(ParamNames.Installation.FACE_EN, False)

            if self._config and self._config.parameters_enabled.water_type:
                param_name = ParamNames.Installation.WATER_TYPE
                self.show_parameter(param_name)

                if value in [DistributionTypes.IS.value, DistributionTypes.TD.value]:
                    water_types = WaterTypes.to_value_list(value)
                    self.ctrl_prop_util.set_value_list(param_name, water_types)
                else:
                    self.show_parameter(ParamNames.Installation.WATER_TYPE, False)

            update_necessary = True

        elif name == ParamNames.Installation.WATER_TYPE:
            param = getattr(self.build_ele, name)
            param.value = value

            self.water_type = value
            update_necessary = True

        elif name == ParamNames.Installation.FACE_EN:
            param = getattr(self.build_ele, name)
            param.value = value

            self.face_en = value
            update_necessary = True

        elif name == ParamNames.DrawMode.MODE:
            if self.script_object_interactor:
                self.script_object_interactor._change_draw_mode()
            update_necessary = True

        elif name == ParamNames.DrawMode.INSERT:
            if self.script_object_interactor:
                self.script_object_interactor.insert_mode = value
                self.script_object_interactor.cut_mode = False

                param = getattr(self.build_ele, ParamNames.DrawMode.CUT)
                param.value = False

            update_necessary = True

        elif name == ParamNames.DrawMode.CUT:
            if self.script_object_interactor:
                self.script_object_interactor.cut_mode = value
                self.script_object_interactor.insert_mode = False

                param = getattr(self.build_ele, ParamNames.DrawMode.INSERT)
                param.value = False

            update_necessary = True

        elif name == ParamNames.Attributes.VALUE:
            if self.script_object_interactor:
                self.script_object_interactor.apply_attributes_input()
            update_necessary = True

        elif name == ParamNames.Layers.DESCRIPTION:
            param = getattr(self.build_ele, name)
            param.value = value
            update_necessary = True

        return update_necessary

    # ========================================
    # CREACION PYTHONPARTS Y PTYHONGROUP
    # ========================================
    def _generate_pythonparts(self):
        """
        Genera PythonParts a partir de self.element_list_final.
        Maneja la creación de grupos, elementos individuales y el container final.
        """
        self.element_list_final = []
        self.pythonpart_group_list = [] # Limpiar grupos previos
        self._delete_previous_copies()

        self._create_elements()
        if not self.element_list_final:
            print("[PolylineInteractor] No se generaron elementos.")
            return

        self.crear_pythonpart =  getattr(self.build_ele, ParamNames.General.CREATE_PYTHON_PART).value
        self._fn_name = getattr(self.build_ele, ParamNames.General.FUNCTIONAL_NAME).value

        # Crear polilínea si está habilitado
        if self._config and self._config.parameters_show.add_polilyne:
            if getattr(self.build_ele, ParamNames.General.ADD_POLILYNE).value:
                polyline_list = self._create_polyline()
                pp_poly = self.create_individual_pythonpart(elements_list=polyline_list, build_ele=self.build_ele)
                self.pythonpart_group_list.extend(pp_poly)

        # --- Inserción de Elementos y Creación de PythonParts ---
        if self.crear_pythonpart:
            pythonpart_type_selected= "Individual" if self.is_individual_mode else "Group"
            print(f"[SO] ========== MODO PYTHONPARTGROUP ACTIVADO ==========")
            print(f"[SO] Iniciando creación de PythonPartGroup - '{pythonpart_type_selected} type' - {len(self.element_list_final)} elementos.")

            try:
                if not self.is_individual_mode:
                    self._create_grouped_pythonparts()
                else:
                    self._create_individual_pythonparts()

                if not self.pythonpart_group_list:
                    raise Exception("No se pudieron crear lista de PythonParts")

                # Una vez procesadas todas las rutas, copiar a los archivos de dibujo
                self._copy_elements_grouped_by_attribute(self.pythonpart_group_list)

            except Exception as e:
                print(f"[SO] Error creando PythonPartGroup: {e}")
                print(f"[SO] Fallback: Creando elementos individuales sin PythonPart.")
                self._insert_elements_without_pythonpart()
                return

            # Crear el container final (PythonPartGroup)
            self._create_pythonpart_container()
        else:
            # Creación simple sin PythonPart
            self._insert_elements_without_pythonpart()

    def _copy_elements_grouped_by_attribute(self, elements: list) -> None:
        """
        Agrupa los elementos por el valor del atributo 'pmp_pare'
        y copia cada grupo a su archivo de dibujo correspondiente.
        """
        attr_pmp_pare = "pmp_pare"
        attr_pmp_pare_id = AttributeService.GetAttributeID(self.doc, attr_pmp_pare)

        element_dict: dict[str, list] = {}

        for element_model in elements:
            result_list =  element_model.create()
            model = element_model.views[0].elements[0]

            for element in result_list:
                if isinstance(element, AllplanBasisElements.MacroPlacementElement):
                    # Intenta obtener el set de atributos directamente del Placement
                    attrs = element.GetAttributes()
                    for attr_set in attrs.GetAttributeSets(): # type: ignore
                        for attr in attr_set.GetAttributes():
                            if attr.Id == attr_pmp_pare_id and attr.Value:
                                group_key = str(attr.Value).strip()
                                if group_key not in element_dict:
                                    element_dict[group_key] = []
                                element_dict[group_key].append(model)
                                self.copy_element_list.append(model)
        if element_dict:
            for group_key, group_elements in element_dict.items():
                if not group_key:
                    continue
                self._copy_elements_to_drawing_files(group_elements, group_key)

    def _create_grouped_pythonparts(self):
        """
        Crea PythonParts agrupados (modo 'group').
        Los resultados se agregan a self.pythonpart_group_list.
        """
        # all_elements: list = []  # acumula todos los element_models de todas las rutas
        for path_index, element_list_data in enumerate(self.element_list_final):
            current_segment_group = []
            connections_to_create = []

            # Acumular elementos para el agrupado por atributo
            # all_elements.extend(element_list_data)

            def flush_segment_group(group):
                """Genera el PythonPart para el grupo de tuberías/cables acumulado."""
                if not group:
                    return

                pp_segments = self.create_group_pythonpart(
                    elements_list=group,
                    build_ele=self.build_ele,
                    base_c=self.inst_color
                )
                self.pythonpart_group_list.extend(pp_segments)

            for index, item in enumerate(element_list_data):
                element_type = item.element_type
                element_model = item.element

                if element_type == self.element_type_core:
                    # Es tubería/cable: se acumula para crear un solo PythonPart grupal
                    current_segment_group.append(element_model)

                elif element_type == "CUBOID_LABEL":
                    # Es el cuboide: lo creamos como PythonPart individual inmediatamente
                    # para que no se mezcle con la geometría de las tuberías
                    pp_cuboid = self.create_individual_pythonpart(
                        elements_list=[element_model],
                        build_ele=self.build_ele
                    )
                    self.pythonpart_group_list.extend(pp_cuboid)

                else:
                    # Es un manguito/conexión: cerramos el grupo actual y guardamos la conexión
                    flush_segment_group(current_segment_group)
                    current_segment_group = []
                    connections_to_create.append(element_model)

            # Al finalizar el camino, procesamos el último grupo pendiente
            flush_segment_group(current_segment_group)

            # Creamos las conexiones (manguitos) de este camino
            if connections_to_create:
                pp_connections = self.create_individual_pythonpart(
                    elements_list=connections_to_create,
                    build_ele=self.build_ele
                )
                self.pythonpart_group_list.extend(pp_connections)

    def _create_individual_pythonparts(self):
        """
        Crea PythonParts individuales (modo 'individual').
        Los resultados se agregan a self.pythonpart_group_list
        """
        for element_list_data in self.element_list_final:
            new_list: List[Any] = [
                e.element if hasattr(e, 'element') else e.get('element')
                for e in element_list_data
            ]

            # 2. Quitar duplicados manteniendo el orden (si los elementos son hashables)
            # Si son objetos 3D complejos, dict.fromkeys es una forma rápida de limpiar
            new_list = list(dict.fromkeys(new_list))

            pythonparts_list = self.create_individual_pythonpart(
                elements_list=new_list,
                build_ele=self.build_ele,
            )
            self.pythonpart_group_list.extend(pythonparts_list)

    def _insert_elements_without_pythonpart(self):
        """
        Inserta elementos directamente sin crear PythonParts.
        Usa self.element_list_final y self.doc
        """
        try:
            for element_list_data in self.element_list_final:
                # Extraer elementos del dict si es necesario
                new_list: List[Any] = [
                    e.element if hasattr(e, 'element') else e.get('element')
                    for e in element_list_data
                ]

                # 2. Quitar duplicados manteniendo el orden (si los elementos son hashables)
                # Si son objetos 3D complejos, dict.fromkeys es una forma rápida de limpiar
                elements_to_insert = list(dict.fromkeys(new_list))

                # elements_to_insert = []
                # for item in element_list_data:
                #     if isinstance(item, dict):
                #         elements_to_insert.append(item.get("element", item))
                #     else:
                #         elements_to_insert.append(item)

                AllplanBaseElements.CreateElements(
                    doc=self.doc,
                    insertionMat=AllplanGeo.Matrix3D(),
                    modelEleList=elements_to_insert,
                    modelUuidList=[],
                    assoRefObj=None,
                )
            print(f"[PolylineInteractor] {len(self.element_list_final)} elementos insertados exitosamente.")
        except Exception as e:
            print(f"[PolylineInteractor] Error CreateElements: {e}")

    def _create_pythonpart_container(self):
        """
        Crea el container final (PythonPartGroup) que agrupa todos los PythonParts.
        Usa self.pythonpart_group_list y self.doc
        """
        # Limpiar copias 3D previas en otros archivos (feature pmp_pare)

        global_params: Dict = {
            "TotalElements": len(self.pythonpart_group_list),
            "PolylineID": id(self.pythonpart_group_list),
            "CopiedElementsUUIDs": repr(str(getattr(getattr(self.build_ele, "CopiedElementsUUIDs", None), "value", "") or "")),
            "CopiedElementsFiles": repr(str(getattr(getattr(self.build_ele, "CopiedElementsFiles", None), "value", "") or "")),
        }

        # Serialización del Estado
        state_json = self._serialize_state_to_json()
        if state_json:
            global_params["SavedState"] = state_json
            print(f"[SO] Estado guardado ({len(state_json)} chars)")

        try:
            installation_hash = self.create_element_hash("polyline_installation", **global_params)
            param_list = self.create_params_list_from_dict(global_params)

            python_file_name = ""
            if hasattr(self, 'build_ele') and hasattr(self.build_ele, "pyp_file_name"):
                python_file_name = self.build_ele.pyp_file_name

                inst_name = ""
                if self._config:
                    inst_name = self._config.default_installation

                ppg_name = f"{self._fn_name}_{id(self.pythonpart_group_list)}" if self._fn_name else f"Polyline_Installation_{inst_name}"
                pythonpart_group = PythonPartGroup(
                    name=ppg_name,
                    parameter_list=param_list,
                    hash_value=installation_hash,
                    python_file=python_file_name,
                    pythonparts=self.pythonpart_group_list,
                )
                model_elem_list = pythonpart_group.create()

                AllplanBaseElements.CreateElements(
                    doc=self.doc,
                    insertionMat=AllplanGeo.Matrix3D(),
                    modelEleList=model_elem_list,
                    modelUuidList=[],
                    assoRefObj=None,
                )
                print(f"[SO] PythonPartGroup creado exitosamente.")

                # _sv = str(getattr(getattr(self.build_ele, "AttributeValue", None), "value", "") or "").strip()
                # print("################## _SV: ", _sv)
                # if _sv:
                #     self._copy_elements_to_drawing_files(model_elem_list, _sv)

        except Exception as e:
            print(f"[SO] ERROR al crear PythonPartGroup. {str(e)}")

    def _create_polyline(self) -> List:
        """Materializa inmediatamente lo que haya en saved_paths en el documento."""
        _points = self.saved_paths.copy()
        if not _points:
            return []

        # doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        if self.default_layers:
            default_id = LayerService.GetIDByShortName(self.default_layers["default"], self.doc) # type: ignore

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Layer = default_id

        elems: List[AllplanBasisElements.ModelElement3D] = []

        for pts in _points:
            if len(pts) < 2:
                continue
            poly = AllplanGeo.Polyline3D()
            for p in pts:
                poly += p
            elems.append(AllplanBasisElements.ModelElement3D(com_prop, poly))

        return elems

    # ═══════════════════════════════════════════════════════════════════════
    #  COPIA 3D A ARCHIVOS DE DIBUJO POR ATRIBUTO pmp_pare
    # ═══════════════════════════════════════════════════════════════════════
    def _find_drawing_file_by_name(self, pmp_value: str) -> int | None:
        """Busca un archivo de dibujo cargado cuyo nombre contenga pmp_value.

        Args:
            pmp_value: valor del atributo pmp_pare (ej: "TD04", "EN10")

        Returns:
            fileIndex del primer archivo que coincide, o None.
        """
        if not pmp_value:
            return None
        try:
            loaded_docs = AllplanEleAdapter.DocumentNameService.GetLoadedDocumentsNameData()
            print(f"[PMP_PARE] Archivos cargados ({len(loaded_docs)}): {loaded_docs}")
            pmp_upper = pmp_value.strip().upper()
            for doc_name, file_number in loaded_docs:
                if pmp_upper in str(doc_name).upper():
                    print(f"[PMP_PARE] Archivo encontrado: '{doc_name}' (file={file_number}) para pmp_pare='{pmp_value}'")
                    return file_number
            print(f"[PMP_PARE] No se encontró archivo cargado que contenga '{pmp_value}'")
        except Exception as e:
            print(f"[PMP_PARE] Error buscando archivo de dibujo: {e}")
        return None

    def _copy_elements_to_drawing_files(self, model_elem_list: list, section_value: str | None):
        """Copia los elementos 3D generados a un archivo de dibujo cuyo nombre
        contenga el valor de pmp_pare (section_value).

        Flujo:
        1. Guardar archivo activo actual
        2. Buscar archivo destino por nombre
        3. Activar archivo destino con LoadFile
        4. Crear copia con PythonPartTransaction.execute()
        5. Guardar UUIDs de los elementos creados
        6. Reactivar archivo original

        Args:
            model_elem_list: lista de ModelElement3D / PythonPart a copiar
            section_value:   valor de pmp_pare (ej: "TD04")
        """
        if not section_value or not model_elem_list:
            return

        try:
            drawing_service = AllplanBaseElements.DrawingFileService()
            original_file = AllplanBaseElements.DrawingFileService.GetActiveFileNumber()
            doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
            if doc is None:
                print("[PMP_PARE] No se pudo obtener documento activo para copia")
                return

            target_file_index = self._find_drawing_file_by_name(section_value)
            if target_file_index is None:
                print(f"[PMP_PARE] Archivo destino para '{section_value}' no encontrado. "
                      "Asegúrese de que el archivo esté cargado/activo.")
                return

            if target_file_index == original_file:
                print(f"[PMP_PARE] Archivo destino es el mismo que el activo, no se requiere copia separada")
                return

            print(f"[PMP_PARE] Activando archivo destino {target_file_index} para copiar elementos...")
            drawing_service.LoadFile(doc, target_file_index,
                                     AllplanBaseElements.DrawingFileLoadState.ActiveForeground)
            target_doc = DocumentManager.get_instance().document

            pyp_transaction = PythonPartTransaction(target_doc)
            created_elements = pyp_transaction.execute(
                placement_matrix=AllplanGeo.Matrix3D(),
                view_world_projection=AllplanIFW.ViewWorldProjection(),
                model_ele_list=model_elem_list,
                modification_ele_list=ModificationElementList(),
                uuid_parameter_name="PythonPart",
            )

            copied_uuids = []
            for elem in created_elements:
                try:
                    copied_uuids.append(str(elem.GetElementUUID()))
                except Exception:
                    pass

            print(f"[PMP_PARE] {len(copied_uuids)} elementos copiados al archivo {target_file_index}")

            print(f"[PMP_PARE] Reactivando archivo original {original_file}...")
            drawing_service.LoadFile(doc, original_file,
                                     AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

            self._persist_copied_elements_data(copied_uuids, target_file_index)

        except Exception as e:
            print(f"[PMP_PARE] Error en _copy_elements_to_drawing_files: {e}")
            import traceback
            traceback.print_exc()
            try:
                drawing_service = AllplanBaseElements.DrawingFileService()
                doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
                if doc and original_file:
                    drawing_service.LoadFile(doc, original_file,
                                             AllplanBaseElements.DrawingFileLoadState.ActiveForeground)
            except Exception:
                pass

    def _persist_copied_elements_data(self, uuids: list[str], file_index: int):
        """Almacena los UUIDs y el fileIndex de las copias en build_ele para
        poder eliminarlas al re-entrar a la PythonPart.
        """
        try:
            prev_uuids_raw = str(getattr(getattr(self.build_ele, "CopiedElementsUUIDs", None), "value", "") or "")
            prev_files_raw = str(getattr(getattr(self.build_ele, "CopiedElementsFiles", None), "value", "") or "")

            prev_uuids = self._safe_parse_list(prev_uuids_raw)
            prev_files = self._safe_parse_list(prev_files_raw)
            try:
                prev_files = [int(f) for f in prev_files]
            except (ValueError, TypeError):
                prev_files = []

            prev_uuids.extend(uuids)
            prev_files.append(file_index)

            self.build_ele.CopiedElementsUUIDs.value = repr(prev_uuids)
            self.build_ele.CopiedElementsFiles.value = repr(prev_files)
            print(f"[PMP_PARE] Datos de copias persistidos: {len(prev_uuids)} UUIDs, {len(prev_files)} archivos")
        except Exception as e:
            print(f"[PMP_PARE] Error persistiendo datos de copias: {e}")

    def _safe_parse_list(self, raw: str) -> list:
        """Parsea un string repr de lista de forma robusta.

        Maneja casos como: "[9, 8]", "'[9, 8]'", "9, 8", "(9, 8)", etc.
        Siempre devuelve una list (posiblemente vacía).
        """
        s = raw.strip()
        if not s:
            return []
        for _ in range(2):
            if len(s) >= 2 and s[0] in ("'", '"') and s[-1] == s[0]:
                try:
                    v = ast.literal_eval(s)
                    if isinstance(v, str):
                        s = v.strip()
                        continue
                except Exception:
                    break
            break
        try:
            result = ast.literal_eval(s)
        except Exception:
            if "," in s:
                return [x.strip() for x in s.split(",") if x.strip()]
            return [s] if s else []
        if isinstance(result, list):
            return result
        if isinstance(result, tuple):
            return list(result)
        if isinstance(result, str):
            try:
                inner = ast.literal_eval(result)
                if isinstance(inner, (list, tuple)):
                    return list(inner)
            except Exception:
                pass
            return [result] if result else []
        return [result]

    def _delete_previous_copies(self):
        """Elimina las copias 3D creadas previamente en otros archivos de dibujo.

        Lee los UUIDs almacenados en build_ele.CopiedElementsUUIDs y recorre
        los archivos indicados en build_ele.CopiedElementsFiles para buscar y
        eliminar los elementos por UUID.
        Los archivos deben estar activos/cargados por el usuario.
        """
        try:
            uuids_raw = str(getattr(getattr(self.build_ele, "CopiedElementsUUIDs", None), "value", "") or "")
            files_raw = str(getattr(getattr(self.build_ele, "CopiedElementsFiles", None), "value", "") or "")

            if not uuids_raw or not files_raw:
                return

            try:
                target_uuids = ast.literal_eval(uuids_raw)
            except Exception:
                return
            try:
                target_files = ast.literal_eval(files_raw)
            except Exception:
                return

            if not target_uuids or not isinstance(target_uuids, list):
                return
            if not target_files or not isinstance(target_files, list):
                return

            print(f"[PMP_PARE] Eliminando {len(target_uuids)} copias previas en {len(target_files)} archivos...")

            drawing_service = AllplanBaseElements.DrawingFileService()
            original_file = AllplanBaseElements.DrawingFileService.GetActiveFileNumber()
            doc_adapter = self.coord_input.GetInputViewDocument() if self.coord_input else None
            if doc_adapter is None:
                print("[PMP_PARE] No se pudo obtener documento para limpieza de copias")
                return

            uuid_set = set(target_uuids)
            total_deleted = 0

            for file_index in target_files:
                try:
                    drawing_service.LoadFile(doc_adapter, file_index,
                                             AllplanBaseElements.DrawingFileLoadState.ActiveForeground)
                    active_doc = DocumentManager.get_instance().document

                    elems_to_delete = AllplanEleAdapter.BaseElementAdapterList()
                    for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(active_doc):
                        try:
                            elem_uuid = str(element.GetElementUUID())
                            if elem_uuid in uuid_set:
                                elems_to_delete.append(element)
                        except Exception:
                            continue

                    if len(elems_to_delete) > 0:
                        AllplanBaseElements.DeleteElements(doc=active_doc, elements=elems_to_delete)
                        total_deleted += len(elems_to_delete)
                        print(f"[PMP_PARE] Eliminados {len(elems_to_delete)} elementos del archivo {file_index}")
                    else:
                        print(f"[PMP_PARE] No se encontraron elementos para eliminar en archivo {file_index}")

                except Exception as e:
                    print(f"[PMP_PARE] Error eliminando en archivo {file_index}: {e}")

            drawing_service.LoadFile(doc_adapter, original_file,
                                     AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

            self.build_ele.CopiedElementsUUIDs.value = ""
            self.build_ele.CopiedElementsFiles.value = ""
            print(f"[PMP_PARE] Limpieza completada: {total_deleted} elementos eliminados en total")

        except Exception as e:
            print(f"[PMP_PARE] Error en _delete_previous_copies: {e}")
            import traceback
            traceback.print_exc()

    # ========================================
    # HELPERS
    # ========================================
    def _serialize_state_to_json(self) -> str:
        """
        Serializa saved_paths y saved_segments a JSON para persistencia.

        Returns:
            String JSON con el estado serializado
        """
        try:
            # Convertir Point3D a listas [x, y, z]
            def point_to_dict(pt):
                return {"X": pt.X, "Y": pt.Y, "Z": pt.Z}

            # Serializar paths
            paths_data = []
            for path in self.saved_paths:
                paths_data.append([point_to_dict(pt) for pt in path])

            data = []
            if self.script_object_interactor:
                for item in self.script_object_interactor.data:
                    seg = item.segment_item_to_dict(item)
                    data.append(seg)

            ref_angle =  f"{self.reference_orientation_angle:.15f}" if self.reference_orientation_angle else ""

            _water_type = ""
            if self._config and self._config.parameters_enabled.water_type:
                _water_type = getattr(self.build_ele, ParamNames.Installation.WATER_TYPE).value
                self.water_type = _water_type

            state = {
                "saved_paths": paths_data,
                "data": data,
                "metadata": ElementSerializer.serialize_persistent_metadata(self.persistent_metadata),
                "layer_default": self.default_layers,
                "selected_inst_type": self.selected_inst_type if  self.selected_inst_type else "",
                "functional_name": getattr(self.build_ele, ParamNames.General.FUNCTIONAL_NAME).value,
                "distribution_type": getattr(self.build_ele, ParamNames.Installation.DISTRIBUTION_TYPE).value,
                "water_type": _water_type,
                "diameter_type": f"{getattr(self.build_ele, ParamNames.Installation.DIAMETER_TYPE).value}",
                "face_en": getattr(self.build_ele, ParamNames.Installation.FACE_EN).value,
                "reference_orientation_angle": ref_angle,
                "applied_layers": ElementSerializer.serialize_layers(self.applied_layers),
                "applied_default_attrs": ElementSerializer.serialize_attributes(self.applied_default_attributes),
                "applied_custom_attrs": ElementSerializer.serialize_attributes(self.applied_attributes),
                "global_group_numbers": ElementSerializer.serialize_global_numbers(self.global_group_numbers),
            }
            return json.dumps(state)
        except Exception as e:
            print(f"[SO] Error serializando estado: {e}")
            import traceback

            traceback.print_exc()
            return ""

    def create_element_hash(self, element_type: str, **params) -> str:
        """
        Crea un hash único para un elemento basado en su tipo y parámetros.
        Args:
            element_type: Tipo de elemento ('tubo', 'codo', 'reductor', 'bifurcacion')
            **params: Parámetros del elemento (posición, diámetro, longitud, etc.)
        Returns:
            Hash SHA224 como string hexadecimal
        """
        # Generar un número random largo para asegurar unicidad
        # Usar un rango muy grande (10^15 a 10^16-1) para minimizar colisiones
        random_number = random.randint(10**15, 10**16 - 1)
        # Generar hash
        hash_val = hashlib.sha224(str(random_number).encode('utf-8')).hexdigest()
        return hash_val

    def create_params_list_from_dict(self, params: dict) -> List[str]:
        """
        Convierte un diccionario de parámetros en una lista de strings para PythonPart.
        Args:
            params: Diccionario con parámetros del elemento
        Returns:
            Lista de strings en formato "clave = valor\n"
        """
        return [f"{key} = {value}\n" for key, value in sorted(params.items())]

    def create_individual_pythonpart(self, elements_list: List, build_ele) -> List[PythonPart]:
        """
        Convierte una lista de ModelElement3D en PythonParts individuales.
        Cada elemento 3D se envuelve en su propia PythonPart para que GSI pueda leerlos individualmente.
        Args:
            elements_list: Lista de ModelElement3D creados
            build_ele: BuildingElement con parámetros

        Returns:
            Lista de PythonParts individuales
        """
        pythonparts_list = []

        # Obtener el nombre del archivo .pyp desde build_ele
        python_file_name = build_ele.pyp_file_name if hasattr(build_ele, 'pyp_file_name') else ""
        common_props = None

        for idx, element in enumerate(elements_list):
            try:
                # 1. EXTRAER CommonProperties del elemento
                common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                try:
                    common_props = element.GetCommonProperties()
                except:
                    pass

                # 2. EXTRAER atributos del elemento (ya fueron asignados previamente)
                #    Leemos TODOS los AttributeSet para no perder atributos default.
                attribute_list = []
                try:
                    if hasattr(element, 'GetAttributes'):
                        attrs = element.GetAttributes()
                        if attrs:
                            attrs_by_id = {}
                            for attr_set in attrs.GetAttributeSets() or []:
                                for attr in attr_set.GetAttributes() or []:
                                    attr_id = getattr(attr, "Id", None)
                                    if attr_id is None:
                                        continue
                                    attrs_by_id[attr_id] = attr
                            attribute_list = list(attrs_by_id.values())
                except Exception as e:
                    print(f"[SO] Advertencia: No se pudieron extraer atributos del elemento {idx}: {e}")

                # 3. CREAR VIEWS con el ModelElement3D
                views = [View2D3D([element])]

                # 4. CREAR parámetros únicos para este elemento
                params = {
                    'ElementIndex': idx,
                    'ElementType': type(element).__name__,
                    'Layer': common_props.Layer,
                    'Color': common_props.Color,
                    'Pen': common_props.Pen,
                    'Stroke': common_props.Stroke
                }

                # 5. GENERAR hash único (SHA224)
                hash_value = self.create_element_hash('element', **params)

                # 6. CREAR lista de parámetros (formato: "key = value\n")
                param_list = self.create_params_list_from_dict(params)

                # 7. OBTENER nombre descriptivo basado en atributos (ID 1083 = Atributo Personalizado 01)
                element_name = f"PolylineElement_{idx}"
                pp_name = f"{self._fn_name}_{idx}" if self._fn_name else element_name

                # 8. CREAR PythonPart individual con la firma completa
                # Patrón del ejemplo: PythonPart(name, parameter_list, hash_value, python_file, views, matrix, common_props, attribute_list)
                pythonpart = PythonPart(
                    pp_name,                            # name
                    parameter_list=param_list,               # parameter_list
                    hash_value=hash_value,                   # hash_value
                    python_file=python_file_name,            # python_file (nombre del .pyp)
                    views=views,                             # views (View2D3D con ModelElement3D) # type: ignore
                    common_props=common_props,               # common_props
                    attribute_list=attribute_list  # attribute_list
                )
                pythonparts_list.append(pythonpart)

            except Exception as e:
                print(f"[SO] Error creando PythonPart individual para elemento {idx}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"[SO] Creadas {len(pythonparts_list)} PythonParts individuales de {len(elements_list)} elementos")
        return pythonparts_list

    def create_group_pythonpart(self,
                                elements_list: List,
                                build_ele,
                                base_c: int=0) -> List[PythonPart]:
        """
        Unifica SOLO los elementos del mismo color del PRIMER elemento.
        El resto se dejan como elementos individuales sin aplicar MakeUnion.
        """
        try:
            print(f"[SO] Element LIST: {len(elements_list)}")
            pythonparts_list = []
            element_data_list = []
            all_attributes = []
            first_common_props = None
            base_color = 0

            # ------------------------------------------------------------
            # 1. EXTRAER GEOMETRÍA + PROPIEDADES + ATRIBUTOS
            # ------------------------------------------------------------
            geo = None
            for idx, element in enumerate(elements_list):
                print(f"[SO] Procesando elemento {idx}/{len(elements_list)-1}")
                try:
                    geo = element.GetGeometryObject()
                    props = element.GetCommonProperties()
                except:
                    props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()

                if base_c == props.Color:
                    first_common_props = props
                    base_color = props.Color    # <-- COLOR BASE
                    print(f"[SO] Color base = {base_color}")

                # Atributos
                elem_attrs = []
                try:
                    if idx == 0:
                        if hasattr(element, 'GetAttributes'):
                            attrs = element.GetAttributes()
                            if attrs:
                                attrs_by_id = {}
                                for attr_set in attrs.GetAttributeSets() or []:
                                    for attr in attr_set.GetAttributes() or []:
                                        attr_id = getattr(attr, "Id", None)
                                        if attr_id is None:
                                            continue
                                        attrs_by_id[attr_id] = attr
                                elem_attrs = list(attrs_by_id.values())
                                all_attributes.extend(elem_attrs)
                except:
                    pass

                element_data_list.append({
                    "geometry": geo,
                    "common_props": props,
                    "attributes": elem_attrs,
                })

            if not element_data_list:
                return []

            # ------------------------------------------------------------
            # 2. UNION SOLO DE ELEMENTOS DEL MISMO COLOR
            # ------------------------------------------------------------
            print("[SO] Iniciando unión solo entre elementos del color base...")

            list_new = []
            unified_geometry = None
            first_geometry_taken = False
            list_manguito = []

            for i, elem in enumerate(element_data_list):
                elem_color = elem["common_props"].Color
                # elem_layer = elem["common_props"].Layer # Extraído previamente con tu lógica de layers_list

                if elem_color == base_color: # type: ignore
                    # SOLO se unen si coinciden en COLOR y LAYER
                    if not first_geometry_taken:
                        unified_geometry = elem["geometry"]
                        first_geometry_taken = True
                    else:
                        err, unified_geometry = AllplanGeo.MakeUnion(unified_geometry, elem["geometry"]) # type: ignore
                        if err != 0:
                            print(f"[SO] ERROR en MakeUnion {i}: {err}")
                            return []
                else:
                    # === NO SE UNE ===
                    props = elem["common_props"]
                    # props.Layer = layer_default
                    new_elem = AllplanBasisElements.ModelElement3D(props, elem["geometry"])

                    if elem["attributes"]:
                        attr_set_list = [AllplanBaseElements.AttributeSet(elem["attributes"])]
                        attributes = AllplanBaseElements.Attributes(attr_set_list)
                        new_elem.SetAttributes(attributes)

                    print(f"[SO] Elemento {i} color={elem_color} diferente → NO se une - Layer: {props.Layer} - {i}")
                    list_manguito.append(new_elem)

            # ------------------------------------------------------------
            # 3. AGREGAR EL SÓLIDO UNIFICADO FINAL
            # ------------------------------------------------------------
            if unified_geometry:
                print("[SO] Unión de color base completada. Agregando sólido unificado final...")
                solid_elem = AllplanBasisElements.ModelElement3D(first_common_props, unified_geometry) # type: ignore
                list_new.append(solid_elem)

            # ------------------------------------------------------------
            # 4. CREAR VIEW
            # ------------------------------------------------------------
            views = [View2D3D(list_new)]

            # ------------------------------------------------------------
            # 5. PARÁMETROS DEL PYTHONPART
            # ------------------------------------------------------------
            params = {
                # 'ElementIndex': num_td,
                'ElementType': type(element).__name__,
                'ElementCount': len(elements_list),
                'BaseColor': base_color,
                'AttributeCount': len(all_attributes)
            }

            hash_value = self.create_element_hash('solid_by_color_group', **params)
            param_list = self.create_params_list_from_dict(params)

            pp_name = self._fn_name if self._fn_name else "SolidByColorGroup"
            pythonpart = PythonPart(
                pp_name,
                parameter_list=param_list,
                hash_value=hash_value,
                python_file=getattr(build_ele, 'pyp_file_name', ""),
                views=views, # type: ignore
                common_props=first_common_props,
                attribute_list=all_attributes
            )
            pythonparts_list.append(pythonpart)

            print("[SO] PythonPart creado correctamente")

        except Exception as e:
            print(f"[SO] Error creando PythonPart Group para elemento {idx}: {e}")
            import traceback
            traceback.print_exc()

        return pythonparts_list


# ==================================================================================================================================
def apply_config_to_script_object(script_object, config: PolylineBaseConfig) -> None:
    """
    Aplica la configuración de comportamiento en tiempo de ejecución
    tanto al script object como a su interactor (si existe).

    Es seguro llamar a esta función antes o después de `start_input()`.
    """
    # Guarda la configuración dentro del script object
    # (solo si el script object implementa el método set_config)
    if hasattr(script_object, 'set_config'):
        script_object.set_config(config)

    # Intenta obtener el interactor asociado al script object
    interactor = getattr(script_object, "script_object_interactor", None)

    # Si el interactor ya existe, se le asigna la misma configuración
    # para que ambos (script + interactor) compartan el mismo estado
    if interactor is not None:
        interactor.config = config

def initialize_script_object(build_ele, script_object_data, config: Optional[PolylineBaseConfig] = None):
    """
    Crea e inicializa el ScriptObject y le aplica la configuración opcional.

    - Allplan se encarga de asignar `coord_input`
    - Allplan también llamará automáticamente a `start_input()`
    - Esta función NO inicia el loop de interacción
    """
    print("[LIBRARY] Initialize_script_object")

    # Se crea la instancia del ScriptObject principal
    so = PolylineScriptObject(build_ele, script_object_data)

    if so:
        print(f"[LIBRARY] Script object created: OK")

    # Si se recibe una configuración, se aplica al script object
    # y también a su interactor (si ya fue creado)
    if config is not None:
        apply_config_to_script_object(so, config)
        print("[LIBRARY] Configuration applied")

    # IMPORTANTE:
    # No se debe llamar a start_input() aquí.
    # Allplan primero asigna coord_input y luego invoca start_input()
    print("[LIBRARY] Returning script object (Allplan will call start_input later)")

    # Se retorna el script object ya inicializado
    return so
