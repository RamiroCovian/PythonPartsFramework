# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Agua, GeneratedElement
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.geo_handler import GeometryHandler, PipelineProcessor
from .utils.segments import DynamicSegmentBuilder

from NemAll_Python_BaseElements import LayerService

# ---------------- CUSTOM NUM_TD PATH ----------------
project_name, host_name = (
    AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
)
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(
    project_name, host_name
)
if error != 0:
    error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(
        project_name, ""
    )

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Agua.profile()

# ---------------- DEFAULT CONFIG PARAMS ----------------
INST_NAME = "AGUA"
CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation=INST_NAME.upper(),
    parameters_show=profile.show,
    parameters_enabled=profile.enabled,
    num_td_path=base_path,
    limit_angles=True,
    allowed_angles=[0.0, 45.0, 90.0, 135.0, 180.0, -45.0, -90.0, -135.0],
)

# ------ MODULES LOADED FOR TEST ------
reload_module = [
    PBL,
    PBL_interactor,
    PBL_object,
]


def check_allplan_version(_build_ele, _version):
    for module in reload_module:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"Error al recargar el módulo {module.__name__}: {e}")
    return True


def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )
    # HOOK: Creación de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creación de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    return script_object


# ========================================
# HOOKS PERSONALIZADOS
# ========================================
def _create_elements_for_segment_group(
    segments, so: PBL.script_object.PolylineScriptObject
):
    """
    Genera la geometría 3D de los elementos sin crear PythonParts.
    Devuelve una lista de elementos generados para un grupo de segmentos.
    """
    print("################################## so.saved_segments: ", segments)

    #  print("################################## so.saved_segments: ", so)
    diameter = 0
    element_type_core = None
    elements_generated = []
    # new_elements_generated = []

    builder = DynamicSegmentBuilder()
    geo_handler = GeometryHandler()

    model_base = so.current_inst_config

    if model_base:
        element_type_core = model_base["key"]
        base_color = model_base["color"]

        if so.diameter_list and so.diameter_type:
            diameter = so.diameter_type
        else:
            diameter = model_base["diameter"]

    selected_inst = [
        item for item in so.pythonparts_modules if item.key == element_type_core
    ]
    # ------------------------------------------------------------------
    # CASO B: Conducto Recuperador (EXAMPLE)
    # ------------------------------------------------------------------
    if model_base and element_type_core in ["polietile", "multicapa"]:

        # water_type se guarda en SegmentInfo; si existe usamos el del primer segmento
        water_type = None
        try:
            if segments:
                first_seg = segments[0]
                info = getattr(first_seg, "info", None)
                if info is not None:
                    water_type = getattr(info, "water_type", None)
        except Exception:
            water_type = None

        # Obtenemos el modelo del conducto pasando los argumentos correctos a execute()
        # diameter      -> parámetro diameter del PythonPart
        # so.distribution_type -> parámetro dist_type del PythonPart
        # water_type    -> parámetro water_type del PythonPart (Fred, Calent, etc.)
        conduct_model = so._get_pythonpart_installed(
            element_key=selected_inst[0].key,
            exec_kwargs={
                "diameter": diameter,
                "dist_type": so.distribution_type,
                "water_type": water_type,
            },
        )

        codo_selected = [item for item in so.pythonparts_modules if item.key == "codo"]
        conexion_selected = [
            item for item in so.pythonparts_modules if item.key == "manguito"
        ]

        # Pasamos el tipo de distribución (IS / TD) al PythonPart de codo
        # para que CodoScript.execute pueda elegir entre ColzeModel y ColzeTDModel.
        codo_model = so._get_pythonpart_installed(
            element_key=codo_selected[0].key,
            exec_kwargs={"dist_type": so.distribution_type},
        )
        # La conexión (manguito) todavía no se utiliza en elem3D_list; no bloqueamos la creación
        # del tubo principal si este PythonPart no está disponible.
        # conexion_model = so._get_pythonpart_installed(
        #     element_key=conexion_selected[0].key
        # )

        if conduct_model and codo_model:
            elem3D_list = []

            # Siempre añadimos el primer elemento del modelo (outer / tubo simple)
            elem3D_list.append(
                {
                    "type": "tubo_agua",
                    "elem": conduct_model[0],
                    "rotate": True,
                    "color": 1,
                }
            )

            # Para los modelos TD de polietile, el PythonPart devuelve outer + inner.
            # Si existe un segundo elemento, lo añadimos también para que la polilínea
            # procese las dos partes del BRep.
            if len(conduct_model) > 1:
                elem3D_list.append(
                    {
                        "type": "tubo_agua_inner",
                        "elem": conduct_model[1],
                        "rotate": True,
                        "color": 1,
                    }
                )

            # Codo: en TD devuelve outer + inner, igual que el tubo de polietileno.
            # Registramos ambos en templates para que el PipelineProcessor pueda
            # instanciar tanto el codo exterior como el interior.
            elem3D_list.append(
                {"type": "codo_90", "elem": codo_model[0], "rotate": True}
            )
            if len(codo_model) > 1:
                elem3D_list.append(
                    {"type": "codo_90_inner", "elem": codo_model[1], "rotate": True}
                )

            processor = PipelineProcessor(
                elem3D_list=elem3D_list, element_type="tubo_agua"
            )
            elements_generated = processor.process(segments=segments)

    # self.element_list: List[List[GeneratedElement]] = []
    return elements_generated


def _create_elements_with_layers_attrs(
    elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject
) -> list:
    """
    Versión corregida: Gestión de subdivisión con re-numeración y limpieza de caché. Aplicar atributos y layers a model3D elements
    """
    print(
        "###################################### elements_generated: ",
        elements_generated,
    )

    elements_generated_final = elements_generated

    return elements_generated_final


# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================
def _merge_attributes(base_attrs: list, override_attrs: list) -> list:
    """
    Fusiona dos listas de atributos de Allplan.
    Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.

    Args:
        base_attrs: Lista base de atributos (AttributeString, AttributeDouble, etc.)
        override_attrs: Lista de atributos que sobrescriben los base

    Returns:
        Lista fusionada de atributos sin duplicados por ID

    Example:
        base = [AttributeString(Id: 55015, Value: "IS08"),
                AttributeString(Id: 55010, Value: "")]
        override = [AttributeString(Id: 55015, Value: "testtt00009")]

        result = _merge_attributes(base, override)
        # result tendrá Id 55015 con valor "testtt00009" y Id 55010 con valor ""
    """
    # Diccionario para rastrear atributos por ID
    # Clave: ID del atributo, Valor: objeto de atributo completo
    attr_dict = {}

    # 1. Primero agregar todos los atributos base
    for attr in base_attrs:
        attr_dict[attr.Id] = attr

    # 2. Sobrescribir/agregar con los atributos de override
    for attr in override_attrs:
        attr_dict[attr.Id] = attr

    # 3. Convertir el diccionario de vuelta a lista
    # Ordenar por ID para mantener consistencia (opcional)
    merged_list = [attr_dict[key] for key in sorted(attr_dict.keys())]

    return merged_list


def _process_auto_numbering(
    attribute_list: list,
    inst_type: str,
    so: PBL.script_object.PolylineScriptObject,
    forced_number: int | None = None,
) -> tuple[list, bool]:
    if not attribute_list:
        return attribute_list, False

    new_attr_list = []
    modified = False
    target_id = 1083

    for attr in attribute_list:
        if hasattr(attr, "Id") and attr.Id == target_id:
            # SIEMPRE generamos el valor si hay un forced_number,
            # o si el valor es exactamente "TV" (semilla inicial)
            if forced_number is not None:
                new_value = f"TV-{forced_number}"
                new_attr_list.append(
                    AllplanBaseElements.AttributeString(target_id, new_value)
                )
                modified = True
                continue
            elif attr.Value == "TV":
                # Caso de rescate: si no hay forced_number pero detectamos la semilla
                if so.init_storage:
                    num = so.init_storage._get_next_number(inst_type)
                    so.init_storage._save_numbering_file()
                    new_value = f"TV-{num}"
                    new_attr_list.append(
                        AllplanBaseElements.AttributeString(target_id, new_value)
                    )
                    modified = True
                    continue

        new_attr_list.append(attr)

    return new_attr_list, modified


def _extract_number_from_attrs(attribute_list: list) -> int | None:
    """
    Extrae el número entero del atributo 1083 (formato 'TV-X').
    """
    if not attribute_list:
        return None

    target_id = 1083
    prefix = "TV-"

    for attr in attribute_list:
        try:
            # Verificamos si es el atributo correcto
            if hasattr(attr, "Id") and attr.Id == target_id:
                val_str = str(attr.Value)

                # Si el valor ya tiene el formato "TV-5", extraemos el 5
                if prefix in val_str:
                    num_part = val_str.replace(prefix, "").strip()
                    if num_part.isdigit():
                        return int(num_part)

                # Si por alguna razón solo está el número como string
                elif val_str.isdigit():
                    return int(val_str)

        except Exception as e:
            print(f"[EXTRACT] Error procesando atributo: {e}")
            continue

    return None


def _apply_attributes_to_model_elem(model_elem, attr_list):
    """
    Empaqueta y aplica una lista de atributos a un elemento 3D de Allplan
    usando la estructura AttributeSet -> Attributes.
    """
    if not attr_list:
        return
    try:
        attr_set_list = []
        # Creamos el set de atributos
        attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
        # Creamos el objeto Attributes contenedor
        attributes = AllplanBaseElements.Attributes(attr_set_list)
        # Aplicamos al elemento
        model_elem.SetAttributes(attributes)
        return model_elem
    except Exception as e:
        print(f"[Error] Al aplicar atributos: {e}")


# ========================================
# APLICACIÓN DE LAYERS
# ========================================
def _apply_layer_to_element(
    model_elem: AllplanBasisElements.ModelElement3D,
    key_layer: str,
    so: PBL.script_object.PolylineScriptObject,
) -> AllplanBasisElements.ModelElement3D:
    """
    Responsabilidad única: Buscar el ID del layer y aplicarlo al elemento.
    """
    layer_id = _get_layer_id(key_layer, so)
    if layer_id is not None:
        try:
            props = model_elem.CommonProperties
            props.Layer = layer_id
            model_elem.CommonProperties = props
        except Exception as e:
            print(f"[Error] Fallo al setear layer en {key_layer}: {e}")
            pass
    else:
        print(f"[Warn] No se pudo determinar un ID de Layer válido para {key_layer}")

    return model_elem


def _get_layer_id(
    key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject
):
    """
    Obtiene el ID del layer apropiado para un elemento.
    Prioriza layers específicos guardados sobre el layer por defecto.
    """
    doc = so.coord_input.GetInputViewDocument()
    layer_id = 0
    # Obtener ID del layer por defecto
    if so.default_layers:
        default_id = LayerService.GetIDByShortName(so.default_layers.get("default", ""), doc)  # type: ignore
        if default_id:
            layer_id = default_id

    # Priorizar layer específico guardado
    if hasattr(so, "applied_layers") and so.applied_layers:
        layer_data = so.applied_layers.get(key_applied_layer_attr, None)
        if layer_data and isinstance(layer_data, dict):
            layer_name_str = layer_data.get("layer")
            if layer_name_str:
                specific_id = LayerService.GetIDByShortName(layer_name_str, doc)  # type: ignore
                if specific_id:
                    layer_id = specific_id
    return layer_id
