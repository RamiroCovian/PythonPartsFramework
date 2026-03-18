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
from .utils.vertex_utils import (
    compute_segment_cuts_for_path,
    compute_segment_cuts_for_all_paths,
    detect_bifurcations,
)
from .utils.te_orientation import build_te_params
from .utils.attributes_utils import (
    _merge_attributes,
    _process_auto_numbering,
    _extract_number_from_attrs,
    _apply_attributes_to_model_elem,
)
from .utils.layers_utils import _apply_layer_to_element, _get_layer_id

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

    # Guardamos la orientación 3D de referencia
    so.reference_orientation_angle = getattr(so, "reference_orientation_angle", None)
    print(
        "################################## so.reference_orientation_angle: ",
        so.reference_orientation_angle,
    )

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
    if model_base and element_type_core in ["polietile", "multicapa", "armaflex"]:

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
        te_selected = [item for item in so.pythonparts_modules if item.key == "te"]

        # Pasamos el tipo de distribución (IS / TD) al PythonPart de codo
        # para que CodoScript.execute pueda elegir entre ColzeModel y ColzeTDModel.
        codo_model = so._get_pythonpart_installed(
            element_key=codo_selected[0].key,
            exec_kwargs={"dist_type": so.distribution_type},
        )
        # Manguito (conexión) para tramos colineales (0°/180°)
        manguito_model = None
        try:
            if conexion_selected:
                manguito_model = so._get_pythonpart_installed(
                    element_key=conexion_selected[0].key,
                    exec_kwargs={"dist_type": so.distribution_type},
                )
        except Exception:
            manguito_model = None

        te_model = None
        try:
            if te_selected:
                te_model = so._get_pythonpart_installed(
                    element_key=te_selected[0].key,
                    exec_kwargs={"dist_type": so.distribution_type},
                )
        except Exception:
            te_model = None

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

            # Manguito: se insertará automáticamente en vertices colineales.
            if manguito_model:
                elem3D_list.append(
                    {"type": "manguito", "elem": manguito_model[0], "rotate": True}
                )
                if len(manguito_model) > 1:
                    elem3D_list.append(
                        {
                            "type": "manguito_inner",
                            "elem": manguito_model[1],
                            "rotate": True,
                        }
                    )

            # TE: igual que el codo, puede devolver outer + inner en TD.
            if te_model:
                elem3D_list.append({"type": "te", "elem": te_model[0], "rotate": True})
                if len(te_model) > 1:
                    elem3D_list.append(
                        {"type": "te_inner", "elem": te_model[1], "rotate": True}
                    )

            processor = PipelineProcessor(
                elem3D_list=elem3D_list,
                element_type="tubo_agua",
                build_ele=getattr(so, "build_ele", None),
                doc=so.coord_input.GetInputViewDocument() if so.coord_input else None,
            )
            # Portar orientación capturada en start_orientation_capture a fittings/tramos.
            processor.reference_orientation_angle = getattr(
                so, "reference_orientation_angle", None
            )
            # Recortes por codo, manguito y bifurcaciones (TE) en todos los paths
            path_idx = next(
                (i for i, sg in enumerate(so.segment_groups) if sg is segments),
                0,
            )
            # Detección de bifurcaciones: puntos con 3 segmentos conectados (TE)
            vertex_map, te_vertices = detect_bifurcations(so.segment_groups)
            if te_vertices:
                print(f"[AGUA] Bifurcaciones detectadas (TE): {len(te_vertices)}")

            # Preparar TE nodes (yaw por troncal) para el processor
            processor.te_nodes = (
                build_te_params(so.segment_groups, vertex_map, te_vertices)
                if te_vertices
                else {}
            )

            all_cuts = compute_segment_cuts_for_all_paths(so.segment_groups)
            segment_cuts = {
                seg_idx: all_cuts.get((path_idx, seg_idx), {"start": 0.0, "end": 0.0})
                for seg_idx in range(len(segments))
            }
            elements_generated = processor.process(
                segments=segments, segment_cuts=segment_cuts
            )

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
#
# Las funciones auxiliares de atributos y layers se han movido a:
#   - utils/attributes_utils.py
#   - utils/layers_utils.py
# y se importan al inicio de este módulo.
