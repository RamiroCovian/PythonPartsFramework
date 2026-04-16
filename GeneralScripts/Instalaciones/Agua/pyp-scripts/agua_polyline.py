# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib
import json
import math
from pathlib import Path

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as PythonUtility

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Agua, GeneratedElement, SegmentItem
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.geo_handler import GeometryHandler, PipelineProcessor
from .utils.segments import DynamicSegmentBuilder
from .utils.vertex_utils import (
    compute_segment_cuts_for_path,
    compute_segment_cuts_for_all_paths,
    detect_bifurcations,
    detect_cross_path_elbows,
    detect_cross_path_manguitos,
)
from .utils.te_orientation import build_te_params
from .utils.attributes_utils import (
    _normalize_attribute_list,
    _get_attributes_from_model_elem,
    _merge_attributes,
    _apply_attributes_to_model_elem,
    _apply_absolute_numbering_attr01,
    _set_parent_attributes,
    _has_material_cavitat,
)
from .utils.layers_utils import _apply_layer_to_element
from .clau_de_pas_006 import ClauDePasModel
from .colze_base_002 import ColzeBaseModel
from .taps_010 import TapsModel
from .te_sortida_004 import TeSortidaModel
from Instalaciones.MacroCore import manager as _macrocore_manager_module
from .macros import macro_manager as _macro_manager_module
from .macros.macro_manager import AguaMacroManager
from Instalaciones.ElementosDefinidos import (
    CallbackDefinedElement,
    DefinedElementsFacadeConfig as ED_FacadeConfig,
    create_point_marker_geometry as ed_create_point_marker_geometry,
    draw_marker_for_element_type as ed_draw_marker_for_element_type,
    draw_defined_elements_preview as ed_draw_defined_elements_preview,
    get_defined_element_settings as ed_get_defined_element_settings,
    get_elementos_para_instalacion,
    get_rotation_value as ed_get_rotation_value,
    build_rotation_matrix as ed_build_rotation_matrix,
    ensure_defined_elements_interaction_state as ed_ensure_defined_elements_interaction_state,
    handle_defined_elements_mouse_message as ed_handle_defined_elements_mouse_message,
    handle_defined_elements_property_change as ed_handle_defined_elements_property_change,
    make_selection_common_properties as ed_make_selection_common_properties,
    prepare_defined_elements_event as ed_prepare_defined_elements_event,
    sync_last_element_marker_rotation as ed_sync_last_element_marker_rotation,
    materialize_element_markers as ed_materialize_element_markers,
    serialize_element_markers as ed_serialize_element_markers,
    deserialize_element_markers as ed_deserialize_element_markers,
    serialize_free_placed_points as ed_serialize_free_placed_points,
    deserialize_free_placed_points as ed_deserialize_free_placed_points,
    create_elements_from_free_placed_points as ed_create_elements_from_free_placed_points,
)
from Instalaciones.ElementosDefinidos.handlers import (
    start_element_point_capture as ed_start_element_point_capture,
    handle_element_point_capture_click as ed_handle_element_point_capture_click,
    add_defined_element_marker as ed_add_defined_element_marker,
    add_intermediate_element_at_point as ed_add_intermediate_element_at_point,
    on_anadir_punto_libre as ed_on_anadir_punto_libre,
    on_finalizar_puntos_libres as ed_on_finalizar_puntos_libres,
)
from Instalaciones.ElementosNoDefinidos import (
    build_nodos_export_data as end_build_nodos_export_data,
    deserialize_puntos_no_definidos as end_deserialize_puntos_no_definidos,
    draw_all_puntos_no_definidos as end_draw_all_puntos_no_definidos,
    draw_preview_at_cursor as end_draw_preview_at_cursor,
    handle_click_add_punto_no_definido as end_handle_click_add_punto_no_definido,
    on_anadir_punto_no_definido as end_on_anadir_punto_no_definido,
    on_finalizar_puntos_no_definidos as end_on_finalizar_puntos_no_definidos,
    serialize_puntos_no_definidos as end_serialize_puntos_no_definidos,
)

print(f"[AGUA] Loaded agua_polyline.py from: {__file__}")

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
    marker_manager_factory=lambda so, be: AguaMacroManager(so, be),
)

# ------ MODULES LOADED FOR TEST ------
reload_module = [
    PBL,
    PBL_interactor,
    PBL_object,
    _macrocore_manager_module,
    _macro_manager_module,
]

MAX_SEGMENT_LENGTH = 5000.0  # 5m (fallback)
MAX_SEGMENT_LENGTH_BY_TUBE_TYPE = {
    # TD
    ("TD", "Polietilè"): 5000.0,
    ("TD", "Multicapa"): 5000.0,
    ("TD", "Armaflex"): 5000.0,
    # IS
    ("IS", "Polietilè"): 5000.0,
    ("IS", "Multicapa"): 5000.0,
    ("IS", "Armaflex"): 5000.0,
}

_TUBE_LABEL_BY_KEY = {
    "polietile": "Polietilè",
    "multicapa": "Multicapa",
    "armaflex": "Armaflex",
}

AGUA_EVENT_ADD_PUNTO_NO_DEFINIDO = 1031
AGUA_EVENT_FINALIZAR_PUNTOS_NO_DEFINIDOS = 1032
AGUA_EVENT_ADD_PUNTO_LIBRE = 1017
AGUA_EVENT_FINALIZAR_PUNTOS_LIBRES = 1018


def _build_te_sortida_geometry(build_ele, doc):
    return TeSortidaModel(build_ele, doc).build()


def _build_colze_base_geometry(build_ele, doc):
    return ColzeBaseModel(build_ele, doc).build()


def _build_clau_de_pas_geometry(build_ele, doc):
    return ClauDePasModel(build_ele, doc).build()


def _build_taps_geometry(build_ele, doc):
    return TapsModel(build_ele, doc).build()


_DEFINED_ELEMENT_CALLBACKS = {
    "t_sortida": _build_te_sortida_geometry,
    "colze_base": _build_colze_base_geometry,
    "clau_de_pas": _build_clau_de_pas_geometry,
    "taps": _build_taps_geometry,
}

_agua_defined_elements = {}
for _info in get_elementos_para_instalacion("AGUA"):
    _callback = _DEFINED_ELEMENT_CALLBACKS.get(_info["key"])
    if _callback is not None:
        _agua_defined_elements[_info["key"]] = CallbackDefinedElement(
            nombre=_info["label"],
            callback_geometria=_callback,
            posibles_funciones=_info.get("posibles_funciones"),
            funcion_defecto=_info.get("funcion_defecto"),
        )


def _ensure_elementos_no_definidos_state(script_object) -> None:
    """Inicializa el estado usado por la paleta de puntos no definidos."""
    if not hasattr(script_object, "puntos_no_definidos") or not isinstance(
        getattr(script_object, "puntos_no_definidos", None), list
    ):
        script_object.puntos_no_definidos = []
    if not hasattr(script_object, "common_points_topology") or not isinstance(
        getattr(script_object, "common_points_topology", None), dict
    ):
        script_object.common_points_topology = {}
    if not hasattr(script_object, "common_junctions") or not isinstance(
        getattr(script_object, "common_junctions", None), list
    ):
        script_object.common_junctions = []


def _ensure_elementos_definidos_state(script_object) -> None:
    """Inicializa el estado usado por ElementosDefinidos en Agua."""
    if not hasattr(script_object, "element_markers") or not isinstance(
        getattr(script_object, "element_markers", None), list
    ):
        script_object.element_markers = []
    if not hasattr(script_object, "free_placed_points") or not isinstance(
        getattr(script_object, "free_placed_points", None), list
    ):
        script_object.free_placed_points = []
    script_object.defined_elements_optimizer_graph_output_dir = (
        Path(__file__).resolve().parents[1] / "debug_output"
    )
    script_object.defined_elements_optimizer_graph_file_name = (
        "agua_elementos_definidos_debug.json"
    )


def _set_palette_flag(build_ele, name: str, value) -> None:
    try:
        param = getattr(build_ele, name, None)
        if param is not None and hasattr(param, "value"):
            param.value = value
    except Exception:
        pass


def _get_rotation_value(build_ele, *names: str) -> float:
    return ed_get_rotation_value(build_ele, *names)


def _build_rotation_matrix_for_element(script_object, base_point: AllplanGeo.Point3D):
    """Replica la rotación de ElementosDefinidos usada en fontaneria."""
    build_ele = getattr(script_object, "build_ele", None)
    return _build_rotation_matrix_for_element_with_angles(build_ele, base_point)


def _build_rotation_matrix_for_element_with_angles(
    build_ele,
    base_point: AllplanGeo.Point3D,
    rot_x: float | None = None,
    rot_y: float | None = None,
    rot_z: float | None = None,
):
    """Construye una matriz de rotación/traslación con ángulos opcionales."""
    if rot_x is None:
        rot_x = _get_rotation_value(build_ele, "RotX", "ElementRotX")
    if rot_y is None:
        rot_y = _get_rotation_value(build_ele, "RotY", "ElementRotY")
    if rot_z is None:
        rot_z = _get_rotation_value(build_ele, "RotZ", "ElementRotZ")
    return ed_build_rotation_matrix(base_point, rot_x, rot_y, rot_z)


def _read_element_rotation_from_palette(build_ele) -> tuple[float, float, float]:
    return (
        _get_rotation_value(build_ele, "ElementRotX", "RotX"),
        _get_rotation_value(build_ele, "ElementRotY", "RotY"),
        _get_rotation_value(build_ele, "ElementRotZ", "RotZ"),
    )


def _sync_last_element_marker_rotation(script_object, intr=None) -> None:
    ed_sync_last_element_marker_rotation(script_object, intr)


def _build_defined_elements_facade_config(intr) -> ED_FacadeConfig:
    """Configura la fachada de ElementosDefinidos para la instalación Agua."""
    return ED_FacadeConfig(
        instalacion="AGUA",
        get_model_list=_get_element_model_list_agua,
        free_point_fallback_preview_factory=lambda point, intr_obj: ed_create_point_marker_geometry(
            point,
            getattr(intr_obj, "com_prop", None),
            45.0,
        ),
        marker_fallback_preview_factory=lambda pos, element_type, marker_prop: ed_draw_marker_for_element_type(
            pos,
            element_type,
            marker_prop,
            45.0,
        ),
        marker_selected_fallback_preview_factory=lambda pos, element_type, marker_prop: ed_draw_marker_for_element_type(
            pos,
            element_type,
            ed_make_selection_common_properties(marker_prop),
            45.0,
        ),
        marker_selected_marker_factory=lambda pos, marker_prop: ed_create_point_marker_geometry(
            pos,
            marker_prop,
            55.0,
        ),
        mouse_draw_preview_cb=(
            (lambda point: intr._draw_preview(point)) if intr else None
        ),
        free_point_debug_prefix="[INT]",
        marker_debug_prefix="[AGUA]",
    )


def _get_element_model_list_agua(script_object, build_ele, doc, element_type: str):
    element_type = (element_type or "").strip().lower()
    elem = _agua_defined_elements.get(element_type)
    if elem is None:
        return []
    try:
        result = elem.generate_preview(build_ele, doc) or []
        return result
    except Exception as ex:
        print(f"[AGUA] Error obteniendo preview de {element_type}: {ex}")
        return []


def _create_single_element_agua(
    script_object, build_ele, doc, element_type: str, p_mid
):
    return _create_single_element_agua_with_rotation(
        script_object, build_ele, doc, element_type, p_mid
    )


def _create_single_element_agua_with_rotation(
    script_object,
    build_ele,
    doc,
    element_type: str,
    p_mid,
    rot_x: float | None = None,
    rot_y: float | None = None,
    rot_z: float | None = None,
):
    element_type = (element_type or "").strip().lower()
    elem = _agua_defined_elements.get(element_type)
    if elem is None:
        return False
    try:
        model_list = elem.generate_final_3d(build_ele, doc)
        if not model_list:
            return False
        mat = _build_rotation_matrix_for_element_with_angles(
            build_ele, p_mid, rot_x, rot_y, rot_z
        )
        AllplanBaseElements.CreateElements(doc, mat, model_list, [], None)
        return True
    except Exception as ex:
        print(f"[AGUA] Error creando elemento {element_type} en punto libre: {ex}")
        return False


def _create_elements_from_free_placed_points(script_object, coord_input=None):
    return ed_create_elements_from_free_placed_points(
        script_object,
        coord_input or getattr(script_object, "coord_input", None),
        lambda build_ele, doc, element_type, pos: _create_single_element_agua(
            script_object, build_ele, doc, element_type, pos
        ),
    )


def _materialize_defined_element_markers(script_object) -> int:
    """Crea en documento los marcadores guardados al finalizar la polilínea."""
    return ed_materialize_element_markers(
        script_object,
        lambda so, build_ele, doc, element_type, pos, rot_x, rot_y, rot_z: _create_single_element_agua_with_rotation(
            so,
            build_ele,
            doc,
            element_type,
            pos,
            rot_x,
            rot_y,
            rot_z,
        ),
    )


def _write_provisional_puntos_json(script_object) -> str | None:
    """Escribe un JSON provisional para revisar qué datos genera Agua."""
    try:
        output_dir = Path(__file__).resolve().parents[1] / "debug_output"
        output_dir.mkdir(parents=True, exist_ok=True)

        puntos_serializados = end_serialize_puntos_no_definidos(
            getattr(script_object, "puntos_no_definidos", []) or []
        )
        nodos = getattr(script_object, "nodos_export_data", None)
        if nodos is None:
            nodos = end_build_nodos_export_data(
                getattr(script_object, "puntos_no_definidos", []) or []
            )

        payload = {
            "installation": "AGUA",
            "nodos": nodos,
            "common_points_topology": (
                getattr(script_object, "common_points_topology", {}) or {}
            ),
            "common_junctions": getattr(script_object, "common_junctions", []) or [],
        }

        file_name = "agua_puntos_no_definidos_debug.json"
        output_path = output_dir / file_name
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

        print(f"[AGUA] JSON provisional escrito en: {output_path}")
        return str(output_path)
    except Exception as ex:
        print(f"[AGUA] Error escribiendo JSON provisional: {ex}")
        return None


def _patch_interactor_for_elementos_auxiliares(script_object, intr) -> None:
    """Añade soporte de ElementosDefinidos y ElementosNoDefinidos al interactor."""
    if intr is None or getattr(intr, "_agua_elementos_extra_patched", False):
        return

    setattr(intr, "_agua_elementos_extra_patched", True)
    _ensure_elementos_definidos_state(script_object)
    intr.script_object = script_object
    intr.element_markers = script_object.element_markers
    intr._defined_elements_facade_config = _build_defined_elements_facade_config(intr)
    intr.next_click_adds_intermediate_element = bool(
        getattr(intr, "next_click_adds_intermediate_element", False)
    )
    intr.element_point_capture_mode = bool(
        getattr(intr, "element_point_capture_mode", False)
    )
    intr.element_selected_point = getattr(intr, "element_selected_point", None)
    ed_ensure_defined_elements_interaction_state(script_object, intr)
    intr.next_click_adds_punto_no_definido = bool(
        getattr(intr, "next_click_adds_punto_no_definido", False)
    )

    original_process_mouse_msg = intr.process_mouse_msg
    original_draw_preview = intr._draw_preview
    original_deserialize_state_from_json = intr._deserialize_state_from_json
    original_on_control_event = intr.on_control_event

    def _process_mouse_msg_with_elementos_auxiliares(mouse_msg, pnt, msg_info):
        is_move = bool(intr.coord_input and intr.coord_input.IsMouseMove(mouse_msg))
        is_left_click = getattr(mouse_msg, "Button", 1) == 1
        build_ele = getattr(script_object, "build_ele", None)
        element_markers = getattr(script_object, "element_markers", None) or []
        free_list = getattr(script_object, "free_placed_points", None) or []

        facade_handled = ed_handle_defined_elements_mouse_message(
            script_object,
            intr,
            mouse_msg,
            pnt,
            msg_info,
            getattr(
                intr,
                "_defined_elements_facade_config",
                _build_defined_elements_facade_config(intr),
            ),
        )
        if facade_handled is not None:
            return facade_handled

        if getattr(intr, "next_click_adds_punto_no_definido", False):
            try:
                if is_left_click and not is_move and intr.coord_input:
                    current_point = getattr(intr, "current_point", None)
                    if current_point is None:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            bool(getattr(intr, "points", [])),
                        )
                    else:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            current_point,
                            bool(getattr(intr, "points", [])),
                        )
                    raw_pnt = raw_input.GetPoint()
                    end_handle_click_add_punto_no_definido(intr, script_object, raw_pnt)
                    try:
                        intr._draw_preview(raw_pnt)
                    except Exception:
                        pass
                    return True
            except Exception as ex:
                print(f"[AGUA] Error añadiendo punto no definido: {ex}")

        if getattr(intr, "next_click_adds_intermediate_element", False):
            try:
                if is_left_click and not is_move and intr.coord_input:
                    current_point = getattr(intr, "current_point", None)
                    if current_point is None:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            bool(getattr(intr, "points", [])),
                        )
                    else:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            current_point,
                            bool(getattr(intr, "points", [])),
                        )
                    raw_pnt = raw_input.GetPoint()
                    intr.next_click_adds_intermediate_element = False
                    try:
                        seg = intr._find_hover_segment(raw_pnt, preferred_kind="saved")
                    except Exception:
                        seg = None
                    if seg is not None and hasattr(intr, "_get_segment_endpoints"):
                        a, b = intr._get_segment_endpoints(seg)
                        if a and b and hasattr(intr, "_segment_project_point"):
                            _t, q = intr._segment_project_point(a, b, raw_pnt)
                            ed_add_intermediate_element_at_point(intr, q, "AGUA")
                        else:
                            ed_add_intermediate_element_at_point(intr, raw_pnt, "AGUA")
                    else:
                        ed_add_intermediate_element_at_point(intr, raw_pnt, "AGUA")
                    script_object.element_markers = intr.element_markers
                    _sync_last_element_marker_rotation(script_object, intr)
                    try:
                        intr._draw_preview(raw_pnt)
                    except Exception:
                        pass
                    return True
            except Exception as ex:
                print(f"[AGUA] Error añadiendo marcador intermedio: {ex}")

        if getattr(intr, "element_point_capture_mode", False):
            try:
                if is_left_click and not is_move and intr.coord_input:
                    current_point = getattr(intr, "current_point", None)
                    if current_point is None:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            bool(getattr(intr, "points", [])),
                        )
                    else:
                        raw_input = intr.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            current_point,
                            bool(getattr(intr, "points", [])),
                        )
                    raw_pnt = raw_input.GetPoint()
                    handled = ed_handle_element_point_capture_click(intr, 1, raw_pnt)
                    _set_palette_flag(
                        getattr(script_object, "build_ele", None),
                        "IsElementCaptureMode",
                        False,
                    )
                    try:
                        intr._draw_preview(raw_pnt)
                    except Exception:
                        pass
                    if handled:
                        return True
            except Exception as ex:
                print(f"[AGUA] Error capturando punto de elemento: {ex}")

        return original_process_mouse_msg(mouse_msg, pnt, msg_info)

    def _draw_preview_with_elementos_auxiliares(current_pnt):
        result = original_draw_preview(current_pnt)
        try:
            overlay = []
            build_ele = getattr(script_object, "build_ele", None)
            doc = intr.coord_input.GetInputViewDocument() if intr.coord_input else None
            ed_draw_defined_elements_preview(
                script_object,
                intr,
                current_pnt,
                getattr(
                    intr,
                    "_defined_elements_facade_config",
                    _build_defined_elements_facade_config(intr),
                ),
            )

            if (
                getattr(intr, "element_point_capture_mode", False)
                and getattr(intr, "element_selected_point", None) is None
                and current_pnt is not None
            ):
                overlay.extend(
                    ed_create_point_marker_geometry(
                        current_pnt, getattr(intr, "com_prop", None), 40.0
                    )
                )

            selected_element_point = getattr(intr, "element_selected_point", None)
            if selected_element_point is not None and hasattr(
                selected_element_point, "X"
            ):
                overlay.extend(
                    ed_create_point_marker_geometry(
                        selected_element_point,
                        getattr(intr, "com_prop", None),
                        45.0,
                    )
                )

            puntos = getattr(script_object, "puntos_no_definidos", []) or []
            if puntos:
                overlay.extend(
                    end_draw_all_puntos_no_definidos(
                        puntos,
                        default_color_id=6,
                        base_props=getattr(intr, "com_prop", None),
                        size=45.0,
                        build_ele=build_ele,
                    )
                )

            if (
                getattr(intr, "next_click_adds_punto_no_definido", False)
                and current_pnt is not None
            ):
                overlay.extend(
                    end_draw_preview_at_cursor(
                        current_pnt,
                        build_ele,
                        getattr(intr, "com_prop", None),
                        45.0,
                    )
                )

            if overlay:
                AllplanBaseElements.DrawElementPreview(
                    intr.coord_input.GetInputViewDocument(),
                    AllplanGeo.Matrix3D(),
                    overlay,
                    False,
                    None,
                )
        except Exception as ex:
            print(f"[AGUA] Error dibujando preview de elementos auxiliares: {ex}")
        return result

    def _deserialize_state_with_elementos_auxiliares(json_str: str):
        result = original_deserialize_state_from_json(json_str)
        if not result:
            return result

        try:
            state = json.loads(json_str)
            script_object.element_markers = ed_deserialize_element_markers(
                state.get("element_markers") or []
            )
            intr.element_markers = script_object.element_markers
            script_object.free_placed_points = ed_deserialize_free_placed_points(
                state.get("free_placed_points") or []
            )
            script_object.puntos_no_definidos = end_deserialize_puntos_no_definidos(
                state.get("puntos_no_definidos") or []
            )
            script_object.common_points_topology = (
                state.get("common_points_topology") or {}
            )
            script_object.common_junctions = state.get("common_junctions") or []
        except Exception as ex:
            print(f"[AGUA] Error restaurando estado de elementos auxiliares: {ex}")
        return result

    def _on_control_event_with_defined_elements(event_id: int):
        if event_id == AGUA_EVENT_ADD_PUNTO_LIBRE:
            try:
                intr.save_current_polyline()
            except Exception:
                pass
            ed_prepare_defined_elements_event(
                script_object,
                intr,
                include_free_points=True,
                include_element_markers=False,
            )
            return bool(ed_on_anadir_punto_libre(script_object, intr, "AGUA"))

        if event_id == AGUA_EVENT_FINALIZAR_PUNTOS_LIBRES:
            ed_prepare_defined_elements_event(
                script_object,
                intr,
                include_free_points=True,
                include_element_markers=False,
            )
            return bool(
                ed_on_finalizar_puntos_libres(
                    script_object,
                    intr,
                    lambda coord_input=None: _create_elements_from_free_placed_points(
                        script_object, coord_input
                    ),
                )
            )

        if event_id == 1016:
            ed_prepare_defined_elements_event(
                script_object,
                intr,
                include_free_points=False,
                include_element_markers=True,
            )
            ok = bool(ed_add_defined_element_marker(intr, "AGUA"))
            if ok:
                _sync_last_element_marker_rotation(script_object, intr)
            return ok

        return original_on_control_event(event_id)

    intr.process_mouse_msg = _process_mouse_msg_with_elementos_auxiliares
    intr._draw_preview = _draw_preview_with_elementos_auxiliares
    intr._deserialize_state_from_json = _deserialize_state_with_elementos_auxiliares
    intr.on_control_event = _on_control_event_with_defined_elements


def _get_max_segment_length_for_group(
    so: PBL.script_object.PolylineScriptObject, segments: list, model_base: dict | None
) -> float:
    """
    Obtiene longitud máxima por tipo de tubo (TD/IS + tubo) con fallback global.
    """
    try:
        dist_raw = None
        if segments:
            first_info = getattr(segments[0], "info", None)
            dist_raw = getattr(first_info, "distribution_type", None)
        if not dist_raw:
            dist_raw = getattr(so, "distribution_type", None)
        distribution_type = "TD" if str(dist_raw).upper() == "TD" else "IS"

        tube_label = None
        if isinstance(model_base, dict):
            tube_label = model_base.get("label")
            if not tube_label:
                tube_key = str(model_base.get("key", "")).strip().lower()
                tube_label = _TUBE_LABEL_BY_KEY.get(tube_key)
        if not tube_label:
            tube_label = "Polietilè"

        key = (distribution_type, str(tube_label).strip())
        max_len = MAX_SEGMENT_LENGTH_BY_TUBE_TYPE.get(key)
        if max_len is not None:
            return float(max_len)

        print(
            f"[AGUA] No max length para {key}, usando fallback {MAX_SEGMENT_LENGTH}mm"
        )
        return float(MAX_SEGMENT_LENGTH)
    except Exception as ex:
        print(
            f"[AGUA] Error resolviendo max length por tipo de tubo: {ex}. "
            f"Usando fallback {MAX_SEGMENT_LENGTH}mm"
        )
        return float(MAX_SEGMENT_LENGTH)


def _split_segment_by_max_length(
    segment, max_length: float = MAX_SEGMENT_LENGTH
) -> list:
    """
    Divide un SegmentItem largo en subsegmentos de longitud máxima `max_length`.
    Conserva metadata (`info`) y orientación del segmento original.
    """
    data = getattr(segment, "data", None)
    if data is None:
        return [segment]

    start = getattr(data, "start", None)
    end = getattr(data, "end", None)
    length = float(getattr(data, "longitud_3d", 0.0) or 0.0)
    if not start or not end or length <= max_length + 1e-6:
        return [segment]
    if length <= 1e-6:
        return [segment]

    dx = end.X - start.X
    dy = end.Y - start.Y
    dz = end.Z - start.Z
    ux = dx / length
    uy = dy / length
    uz = dz / length

    result = []
    current_pos = 0.0
    sub_idx = 0

    while current_pos < length - 1e-3:
        sub_length = min(max_length, length - current_pos)

        p_start = AllplanGeo.Point3D(
            start.X + ux * current_pos,
            start.Y + uy * current_pos,
            start.Z + uz * current_pos,
        )
        p_end = AllplanGeo.Point3D(
            start.X + ux * (current_pos + sub_length),
            start.Y + uy * (current_pos + sub_length),
            start.Z + uz * (current_pos + sub_length),
        )

        seg_dict = SegmentItem.segment_item_to_dict(segment)
        sub_seg = SegmentItem.dict_to_segment_item(seg_dict)
        sub_seg.name = f"{segment.name}_sub_{sub_idx + 1}"

        sub_dx = p_end.X - p_start.X
        sub_dy = p_end.Y - p_start.Y
        sub_dz = p_end.Z - p_start.Z
        sub_len_xy = math.sqrt(sub_dx * sub_dx + sub_dy * sub_dy)
        sub_len = math.sqrt(sub_dx * sub_dx + sub_dy * sub_dy + sub_dz * sub_dz)

        sub_seg.data.start = p_start
        sub_seg.data.end = p_end
        sub_seg.data.delta_x = sub_dx
        sub_seg.data.delta_y = sub_dy
        sub_seg.data.delta_z = sub_dz
        sub_seg.data.longitud_3d = sub_len
        sub_seg.data.longitud_xy = sub_len_xy
        sub_seg.data.longitud_xz = math.sqrt(sub_dx * sub_dx + sub_dz * sub_dz)
        sub_seg.data.longitud_yz = math.sqrt(sub_dy * sub_dy + sub_dz * sub_dz)
        sub_seg.data.longitud_x = abs(sub_dx)
        sub_seg.data.longitud_y = abs(sub_dy)
        sub_seg.data.longitud_z = abs(sub_dz)
        sub_seg.data.vector = AllplanGeo.Vector3D(sub_dx, sub_dy, sub_dz)
        if sub_len > 1e-9:
            sub_seg.data.vector_normalizado = AllplanGeo.Vector3D(
                sub_dx / sub_len, sub_dy / sub_len, sub_dz / sub_len
            )
        else:
            sub_seg.data.vector_normalizado = AllplanGeo.Vector3D(0.0, 0.0, 0.0)

        result.append(sub_seg)
        current_pos += sub_length
        sub_idx += 1

    return result


def _split_path_segments_by_max_length(
    segments: list, max_length: float = MAX_SEGMENT_LENGTH
) -> list:
    """
    Divide todos los segmentos de un path en subsegmentos de `max_length`.
    """
    out = []
    for seg in segments or []:
        out.extend(_split_segment_by_max_length(seg, max_length=max_length))
    return out


def _get_parent_value_from_palette(so: PBL.script_object.PolylineScriptObject) -> str:
    """Obtiene valor de padre desde la paleta (NomIS) si existe."""
    try:
        if hasattr(so, "build_ele") and hasattr(so.build_ele, "NomIS"):
            raw = getattr(so.build_ele.NomIS, "value", so.build_ele.NomIS)
            return str(raw or "").strip()
    except Exception:
        pass
    return ""


def _attr_has_non_empty_value(attr_list) -> bool:
    """True si la lista de atributos contiene algún valor no vacío."""
    for attr in _normalize_attribute_list(attr_list):
        val = getattr(attr, "Value", None)
        if val is None:
            val = getattr(attr, "value", None)
        if val is not None and str(val).strip():
            return True
    return False


def _collect_missing_layer_and_parent(
    so: PBL.script_object.PolylineScriptObject,
) -> tuple[list[str], list[str]]:
    """
    Recorre elementos en preview y detecta storage_keys sin layer o sin atributo padre.
    """
    intr = getattr(so, "script_object_interactor", None)
    generated_paths = getattr(intr, "generated_elements", []) if intr else []

    expected_elements: list[tuple[str, str, int, int]] = []
    for path_group in generated_paths:
        for element in path_group or []:
            if not isinstance(element, dict):
                continue
            key = element.get("key")
            if not key or len(key) < 5:
                continue
            # Estructura usada por PolyLib: seg_{key[4]}_elem_{key[3]}
            storage_key = f"seg_{key[4]}_elem_{key[3]}"
            elem_type = str(element.get("type", "") or "")
            expected_elements.append((storage_key, elem_type, int(key[4]), int(key[3])))

    if not expected_elements:
        return [], []

    applied_layers = getattr(so, "applied_layers", {}) or {}
    applied_attrs = getattr(so, "applied_attributes", {}) or {}

    def _resolve_assignment_key(
        key: str,
        source: dict,
        elem_type: str,
        path_idx: int,
        elem_idx: int,
    ) -> str | None:
        """Resuelve key de asignación para validación previa (evita falsos positivos)."""
        if key in source:
            return key

        # En tubos el desfase puede ser mayor por inserción de fittings (TE/manguito).
        if elem_type == "tubo":
            fallback_keys = [
                f"seg_{path_idx}_elem_{elem_idx - 1}",
                f"seg_{path_idx}_elem_{elem_idx + 1}",
                f"seg_{path_idx}_elem_{elem_idx - 2}",
                f"seg_{path_idx}_elem_{elem_idx + 2}",
            ]
        else:
            # En fittings puntuales suele bastar vecino inmediato.
            fallback_keys = [
                f"seg_{path_idx}_elem_{elem_idx - 1}",
                f"seg_{path_idx}_elem_{elem_idx + 1}",
            ]
        for fk in fallback_keys:
            if fk in source:
                return fk
        return None

    missing_layers = [
        key
        for key, elem_type, path_idx, elem_idx in expected_elements
        if not _resolve_assignment_key(
            key, applied_layers, elem_type, path_idx, elem_idx
        )
    ]

    def _is_missing_parent(
        key: str, elem_type: str, path_idx: int, elem_idx: int
    ) -> bool:
        resolved_key = _resolve_assignment_key(
            key, applied_attrs, elem_type, path_idx, elem_idx
        )
        if not resolved_key:
            return True
        return not _attr_has_non_empty_value(applied_attrs.get(resolved_key, []))

    # Si hay padre global en paleta, no exigimos atributo por elemento.
    parent_global = _get_parent_value_from_palette(so)
    if parent_global:
        missing_parent = []
    else:
        missing_parent = [
            k
            for k, elem_type, path_idx, elem_idx in expected_elements
            if _is_missing_parent(k, elem_type, path_idx, elem_idx)
        ]

    if missing_layers or missing_parent:
        # Debug mínimo para identificar el elemento exacto que dispara la advertencia.
        print(
            f"[AGUA][VALIDATION] missing_layers={missing_layers} missing_parent={missing_parent}"
        )

    return missing_layers, missing_parent


def _has_pending_geometry(so: PBL.script_object.PolylineScriptObject) -> bool:
    """Indica si hay geometría pendiente de validar/crear."""
    intr = getattr(so, "script_object_interactor", None)
    if intr and len(getattr(intr, "points", []) or []) >= 2:
        return True
    if len(getattr(so, "saved_paths", []) or []) > 0:
        return True
    if len(getattr(so, "segment_groups", []) or []) > 0:
        return True
    return False


def _ensure_validation_context_ready(
    so: PBL.script_object.PolylineScriptObject,
) -> None:
    """
    Garantiza que existan elementos de preview para validar layers/atributos
    incluso si se finaliza directamente desde modo creación.
    """
    intr = getattr(so, "script_object_interactor", None)
    if intr is None:
        return

    generated_paths = getattr(intr, "generated_elements", []) or []
    if generated_paths:
        return
    if not _has_pending_geometry(so):
        return

    try:
        # Si está dibujando en modo creación, guardar la polilínea activa primero.
        if (
            getattr(intr, "create_mode", False)
            and len(getattr(intr, "points", []) or []) >= 2
        ):
            save_fn = getattr(intr, "_save_current_polyline", None)
            if not callable(save_fn):
                save_fn = getattr(intr, "save_current_polyline", None)
            if callable(save_fn):
                save_fn()

        create_preview_fn = getattr(so, "_create_elements_preview", None)
        if callable(create_preview_fn):
            create_preview_fn()

        gen_preview_fn = getattr(intr, "_generate_elements_for_preview", None)
        if callable(gen_preview_fn):
            gen_preview_fn()
    except Exception as ex:
        print(f"[AGUA] No se pudo preparar contexto de validación: {ex}")


def check_allplan_version(_build_ele, _version):
    for module in reload_module:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"Error al recargar el módulo {module.__name__}: {e}")
    global AguaMacroManager
    from .macros.macro_manager import AguaMacroManager as _AMM
    AguaMacroManager = _AMM
    return True


def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )

    # Reattach palette utilities exposed by Allplan so auxiliary modules can
    # refresh the visible palette after synchronizing build_ele values.
    def _find_palette_service_candidate(*objects):
        for obj in objects:
            if obj is None:
                continue
            try:
                if callable(getattr(obj, "update_palette", None)):
                    return obj
            except Exception:
                pass
            try:
                for attr_name in dir(obj):
                    try:
                        candidate = getattr(obj, attr_name, None)
                    except Exception:
                        continue
                    if callable(getattr(candidate, "update_palette", None)):
                        print(
                            f"[AGUA] palette_service detectado en atributo '{attr_name}'"
                        )
                        return candidate
                    if callable(getattr(candidate, "refresh_palette", None)):
                        print(
                            f"[AGUA] palette_service detectado en atributo '{attr_name}'"
                        )
                        return candidate
            except Exception:
                pass
        return None

    try:
        if not getattr(script_object, "palette_service", None):
            script_object.palette_service = _find_palette_service_candidate(
                getattr(script_object_data, "palette_service", None),
                script_object_data,
                script_object,
            )
        if not getattr(script_object, "palette_service", None):
            try:
                candidate_attrs = []
                for attr_name in dir(script_object_data):
                    if attr_name.startswith("_"):
                        continue
                    try:
                        value = getattr(script_object_data, attr_name, None)
                    except Exception:
                        continue
                    if callable(value):
                        continue
                    candidate_attrs.append(attr_name)
                print(
                    "[AGUA] No se encontró palette_service. "
                    "Atributos públicos de script_object_data: "
                    + ", ".join(candidate_attrs[:80])
                )
            except Exception:
                pass
    except Exception:
        pass
    try:
        if not getattr(script_object, "control_props_util", None):
            script_object.control_props_util = getattr(
                script_object_data, "control_props_util", None
            )
    except Exception:
        pass
    _ensure_elementos_definidos_state(script_object)
    _ensure_elementos_no_definidos_state(script_object)

    original_start_input = script_object.start_input

    def _start_input_with_elementos_no_definidos():
        intr = original_start_input()
        _patch_interactor_for_elementos_auxiliares(script_object, intr)
        return intr

    script_object.start_input = _start_input_with_elementos_no_definidos

    original_serialize_state_to_json = script_object._serialize_state_to_json

    def _serialize_state_to_json_with_elementos_no_definidos():
        raw = original_serialize_state_to_json()
        if not raw:
            return raw
        try:
            state = json.loads(raw)
            state["element_markers"] = ed_serialize_element_markers(
                getattr(script_object, "element_markers", []) or []
            )
            state["free_placed_points"] = ed_serialize_free_placed_points(
                getattr(script_object, "free_placed_points", []) or []
            )
            state["puntos_no_definidos"] = end_serialize_puntos_no_definidos(
                getattr(script_object, "puntos_no_definidos", []) or []
            )
            state["common_points_topology"] = (
                getattr(script_object, "common_points_topology", {}) or {}
            )
            state["common_junctions"] = (
                getattr(script_object, "common_junctions", []) or []
            )
            return json.dumps(state)
        except Exception as ex:
            print(f"[AGUA] Error serializando puntos no definidos: {ex}")
            return raw

    script_object._serialize_state_to_json = (
        _serialize_state_to_json_with_elementos_no_definidos
    )

    # HOOK: Creación de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creación de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    # Validación UX previa a finalizar: layer + atributo padre.
    original_on_control_event = script_object.on_control_event
    original_modify_element_property = script_object.modify_element_property

    def _on_control_event_with_reminder(event_id: int):
        try:
            if event_id in (
                1015,
                1016,
                1021,
                AGUA_EVENT_ADD_PUNTO_LIBRE,
                AGUA_EVENT_FINALIZAR_PUNTOS_LIBRES,
                AGUA_EVENT_ADD_PUNTO_NO_DEFINIDO,
                AGUA_EVENT_FINALIZAR_PUNTOS_NO_DEFINIDOS,
            ):
                intr = getattr(script_object, "script_object_interactor", None)
                if intr is None:
                    intr = script_object.start_input()
                _patch_interactor_for_elementos_auxiliares(script_object, intr)
                if event_id in (
                    AGUA_EVENT_ADD_PUNTO_LIBRE,
                    AGUA_EVENT_FINALIZAR_PUNTOS_LIBRES,
                ):
                    ed_prepare_defined_elements_event(
                        script_object,
                        intr,
                        include_free_points=True,
                        include_element_markers=False,
                    )
                if event_id in (1015, 1016):
                    ed_prepare_defined_elements_event(
                        script_object,
                        intr,
                        include_free_points=False,
                        include_element_markers=True,
                    )

            if event_id == 1015:
                ed_prepare_defined_elements_event(
                    script_object,
                    intr,
                    include_free_points=False,
                    include_element_markers=True,
                )
                ok = bool(ed_start_element_point_capture(intr, "AGUA"))
                _set_palette_flag(build_ele, "IsElementCaptureMode", ok)
                return ok

            if event_id == 1021:
                intr.element_point_capture_mode = False
                intr.element_selected_point = None
                _set_palette_flag(build_ele, "IsElementCaptureMode", False)
                return True

            if event_id == 1016:
                ed_prepare_defined_elements_event(
                    script_object,
                    intr,
                    include_free_points=False,
                    include_element_markers=True,
                )
                ok = bool(ed_add_defined_element_marker(intr, "AGUA"))
                if ok:
                    _sync_last_element_marker_rotation(script_object, intr)
                return ok

            if event_id == AGUA_EVENT_ADD_PUNTO_LIBRE:
                return bool(ed_on_anadir_punto_libre(script_object, intr, "AGUA"))

            if event_id == AGUA_EVENT_FINALIZAR_PUNTOS_LIBRES:
                return bool(
                    ed_on_finalizar_puntos_libres(
                        script_object,
                        intr,
                        lambda coord_input=None: _create_elements_from_free_placed_points(
                            script_object, coord_input
                        ),
                    )
                )

            if event_id in (
                AGUA_EVENT_ADD_PUNTO_NO_DEFINIDO,
                AGUA_EVENT_FINALIZAR_PUNTOS_NO_DEFINIDOS,
            ):
                intr = getattr(script_object, "script_object_interactor", None)
                if intr is None:
                    intr = script_object.start_input()
                _patch_interactor_for_elementos_auxiliares(script_object, intr)

                if event_id == AGUA_EVENT_ADD_PUNTO_NO_DEFINIDO:
                    return bool(end_on_anadir_punto_no_definido(script_object, intr))

                ok = bool(end_on_finalizar_puntos_no_definidos(script_object, intr))
                _write_provisional_puntos_json(script_object)
                return ok

            if event_id == 1003:
                _ensure_validation_context_ready(script_object)
                missing_layers, missing_parent = _collect_missing_layer_and_parent(
                    script_object
                )
                if missing_layers or missing_parent:
                    lines = [
                        "Hay elementos sin configuración completa antes de finalizar.",
                        "",
                    ]
                    if missing_layers:
                        lines.append(
                            f"• Sin layer asignado: {len(missing_layers)} elemento(s)."
                        )
                    if missing_parent:
                        lines.append(
                            f"• Sin atributo padre (pmp_pare / 6_CC_IS): {len(missing_parent)} elemento(s)."
                        )
                    lines.extend(
                        [
                            "",
                            "¿Desea continuar sin asignar (Aceptar) o volver a configuración para asignar estos datos (Cancelar)?",
                        ]
                    )
                    warning_message = "\n".join(lines)

                    try:
                        if hasattr(PythonUtility, "MB_OKCANCEL"):
                            response = PythonUtility.ShowMessageBox(
                                warning_message, PythonUtility.MB_OKCANCEL
                            )
                        else:
                            response = PythonUtility.ShowMessageBox(
                                warning_message, PythonUtility.MB_OK
                            )
                    except Exception as ex:
                        print(
                            f"[AGUA] Error mostrando advertencia de layer/atributos: {ex}"
                        )
                        response = getattr(PythonUtility, "IDOK", None)

                    if (
                        getattr(PythonUtility, "IDCANCEL", None) is not None
                        and response == PythonUtility.IDCANCEL
                    ):
                        print(
                            "[AGUA] Finalización cancelada por usuario para completar layer/atributos."
                        )
                        intr = getattr(script_object, "script_object_interactor", None)
                        try:
                            if intr:
                                intr.preview_mode = True
                                intr.edit_mode = True
                                intr.create_mode = False
                                intr._generate_elements_for_preview()
                        except Exception as ex:
                            print(
                                f"[AGUA] No se pudo reactivar modo configuración: {ex}"
                            )
                        return True
        except Exception as ex:
            print(f"[AGUA] Error en recordatorio previo a finalizar: {ex}")

        result = original_on_control_event(event_id)
        if event_id == 1003:
            try:
                created_markers = _materialize_defined_element_markers(script_object)
                if created_markers:
                    print(
                        f"[AGUA] Elementos definidos creados desde marcadores: {created_markers}"
                    )
            except Exception as ex:
                print(f"[AGUA] Error materializando marcadores definidos: {ex}")
        return result

    script_object.on_control_event = _on_control_event_with_reminder

    def _modify_element_property_with_preview(name: str, value):
        result = original_modify_element_property(name, value)
        try:
            intr = getattr(script_object, "script_object_interactor", None)
            if intr is not None:
                ed_handle_defined_elements_property_change(script_object, intr, name)
        except Exception as ex:
            print(
                f"[AGUA] Error refrescando preview tras modify_element_property: {ex}"
            )
        return result

    script_object.modify_element_property = _modify_element_property_with_preview

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
            attr_kwargs={
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
            attr_kwargs={"dist_type": so.distribution_type},
        )
        # Manguito (conexión) para tramos colineales (0°/180°)
        manguito_model = None
        try:
            if conexion_selected:
                manguito_model = so._get_pythonpart_installed(
                    element_key=conexion_selected[0].key,
                    exec_kwargs={"dist_type": so.distribution_type},
                    attr_kwargs={"dist_type": so.distribution_type},
                )
        except Exception:
            manguito_model = None

        te_model = None
        try:
            if te_selected:
                te_model = so._get_pythonpart_installed(
                    element_key=te_selected[0].key,
                    exec_kwargs={"dist_type": so.distribution_type},
                    attr_kwargs={"dist_type": so.distribution_type},
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
            max_segment_length = _get_max_segment_length_for_group(
                so, segments, model_base
            )
            segments_to_process = _split_path_segments_by_max_length(
                segments, max_segment_length
            )
            split_segment_groups = list(so.segment_groups)
            if 0 <= path_idx < len(split_segment_groups):
                split_segment_groups[path_idx] = segments_to_process
            if not hasattr(so, "_runtime_segments_by_path"):
                so._runtime_segments_by_path = {}
            so._runtime_segments_by_path[path_idx] = segments_to_process

            # Detección de bifurcaciones: puntos con 3 segmentos conectados (TE)
            vertex_map, te_vertices = detect_bifurcations(split_segment_groups)
            if te_vertices:
                print(f"[AGUA] Bifurcaciones detectadas (TE): {len(te_vertices)}")

            # Detección de codos entre paths distintos (nodo compartido con 2 conexiones).
            # Cubre casos de edición/borrado donde un codo queda partido en dos caminos.
            cross_path_elbows_all = detect_cross_path_elbows(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )
            cross_path_manguitos_all = detect_cross_path_manguitos(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )

            # Preparar TE nodes (yaw por troncal) para el processor
            processor.te_nodes = (
                build_te_params(split_segment_groups, vertex_map, te_vertices)
                if te_vertices
                else {}
            )
            processor.cross_path_elbows = {
                (seg_idx, is_start): data
                for (p_idx, seg_idx, is_start), data in cross_path_elbows_all.items()
                if p_idx == path_idx
            }
            processor.cross_path_manguitos = {
                (seg_idx, is_start): {
                    **data,
                    "other_diameter": (
                        getattr(
                            getattr(
                                split_segment_groups[data["other_path_idx"]][
                                    data["other_seg_idx"]
                                ],
                                "info",
                                None,
                            ),
                            "diameter",
                            None,
                        )
                        if isinstance(data.get("other_path_idx"), int)
                        and isinstance(data.get("other_seg_idx"), int)
                        and 0 <= data["other_path_idx"] < len(split_segment_groups)
                        and 0
                        <= data["other_seg_idx"]
                        < len(split_segment_groups[data["other_path_idx"]])
                        else None
                    ),
                }
                for (p_idx, seg_idx, is_start), data in cross_path_manguitos_all.items()
                if p_idx == path_idx
            }

            all_cuts = compute_segment_cuts_for_all_paths(split_segment_groups)
            segment_cuts = {
                seg_idx: all_cuts.get((path_idx, seg_idx), {"start": 0.0, "end": 0.0})
                for seg_idx in range(len(segments_to_process))
            }
            elements_generated = processor.process(
                segments=segments_to_process, segment_cuts=segment_cuts
            )

    # self.element_list: List[List[GeneratedElement]] = []
    return elements_generated


def _create_elements_with_layers_attrs(
    elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject
) -> list:
    """
    Integra atributos + atributos padre + layers + numeración absoluta.
    Reutiliza metadata persistida en PolyLib (applied_attributes/applied_layers).
    """
    if so._config and not so.init_storage:
        inst_name = str(so._config.default_installation).lower()
        so.init_storage = PolylineStorage(name=inst_name)
        so.init_storage.base_path = so._config.num_td_path

    try:
        doc = so.coord_input.GetInputViewDocument() if so.coord_input else None
    except Exception:
        doc = None

    path_segments = []
    runtime_segments = getattr(so, "_runtime_segments_by_path", {})
    if isinstance(runtime_segments, dict) and path_idx in runtime_segments:
        path_segments = runtime_segments[path_idx]
    elif getattr(so, "segment_groups", None) and path_idx < len(so.segment_groups):
        path_segments = so.segment_groups[path_idx]

    def _default_attr_key_for(element_type: str) -> str:
        # Mapeo de tipos "render" -> tipo lógico de PythonPart
        if element_type in ("tubo_agua", "tubo_agua_inner"):
            if getattr(so, "current_inst_config", None):
                return str(so.current_inst_config.get("key", ""))
            return ""
        if element_type.startswith("codo"):
            return "codo"
        if element_type.startswith("manguito"):
            return "manguito"
        if element_type.startswith("te"):
            return "te"
        return element_type

    def _extract_attr_value_from_list(attr_list):
        for attr in _normalize_attribute_list(attr_list):
            val = getattr(attr, "Value", None)
            if val is not None and str(val).strip():
                return str(val).strip()
        return ""

    def _resolve_assignment_key(default_key, candidate_keys):
        """
        Resuelve la key de paleta (attrs/layers) cuando el índice final de
        elementos difiere del índice usado al seleccionar.
        """
        applied_attrs = getattr(so, "applied_attributes", {}) or {}
        applied_layers = getattr(so, "applied_layers", {}) or {}

        keys_to_try = [default_key] + [k for k in (candidate_keys or []) if k]
        seen = set()
        for key in keys_to_try:
            if key in seen:
                continue
            seen.add(key)
            if key in applied_attrs or key in applied_layers:
                return key
        return default_key

    elements_generated_final = []
    current_tube_idx = -1
    last_segment_idx = 0
    current_tube_assignment_key = None

    outer_inner_type_map = {
        "tubo_agua": "tubo_agua_inner",
        "codo_90": "codo_90_inner",
        "manguito": "manguito_inner",
        "te": "te_inner",
    }
    inner_outer_type_map = {v: k for k, v in outer_inner_type_map.items()}

    for seq_idx, item in enumerate(elements_generated):
        element_type = item.element_type
        model_elem = item.element
        element_idx = item.index

        if element_type == "tubo_agua":
            current_tube_idx += 1
            last_segment_idx = max(current_tube_idx, 0)
            current_tube_assignment_key = f"seg_{path_idx}_elem_{current_tube_idx}"

        seg_info = None
        if path_segments and 0 <= last_segment_idx < len(path_segments):
            seg_info = getattr(path_segments[last_segment_idx], "info", None)

        distribution_type = (
            getattr(seg_info, "distribution_type", None)
            if seg_info is not None
            else None
        )
        if not distribution_type:
            distribution_type = getattr(so, "distribution_type", None) or "IS"

        storage_key = f"seg_{path_idx}_elem_{element_idx}"
        assignment_key = storage_key
        base_key = _default_attr_key_for(element_type)

        # Para tubos, la paleta puede guardar índices "desplazados" cuando hay
        # fittings (p. ej. TE/manguito) antes del tramo en preview. En creación
        # final el índice puede variar, por lo que buscamos key exacta y, si no
        # existe, probamos vecinos inmediatos.
        if element_type == "tubo_agua" and current_tube_assignment_key:
            tube_fallback_keys = [current_tube_assignment_key]
            try:
                idx = int(element_idx)
                tube_fallback_keys.extend(
                    [
                        f"seg_{path_idx}_elem_{idx - 1}",
                        f"seg_{path_idx}_elem_{idx + 1}",
                        f"seg_{path_idx}_elem_{idx - 2}",
                        f"seg_{path_idx}_elem_{idx + 2}",
                    ]
                )
            except Exception:
                pass
            assignment_key = _resolve_assignment_key(assignment_key, tube_fallback_keys)

        expected_outer_type = inner_outer_type_map.get(element_type)
        is_paired_inner = False
        if expected_outer_type and seq_idx - 1 >= 0:
            prev_item = elements_generated[seq_idx - 1]
            is_paired_inner = prev_item.element_type == expected_outer_type
            if is_paired_inner:
                assignment_key = f"seg_{path_idx}_elem_{prev_item.index}"

        # Fallback robusto para inner (incluye manguito reductor TD inner-only):
        # si la key exacta no existe en paleta, buscar en vecinos inmediatos.
        if element_type.endswith("_inner"):
            fallback_keys = []
            try:
                idx = int(element_idx)
                # Priorizar vecino previo (caso real: unión guardada en elem anterior)
                fallback_keys.append(f"seg_{path_idx}_elem_{idx - 1}")
                fallback_keys.append(f"seg_{path_idx}_elem_{idx + 1}")
                # Un fallback extra por si hubo inserción de outer/inner adicional
                fallback_keys.append(f"seg_{path_idx}_elem_{idx - 2}")
                fallback_keys.append(f"seg_{path_idx}_elem_{idx + 2}")
            except Exception:
                pass
            if element_type == "tubo_agua_inner" and current_tube_assignment_key:
                fallback_keys.insert(0, current_tube_assignment_key)
            assignment_key = _resolve_assignment_key(assignment_key, fallback_keys)

        # 1) Defaults que ya trae el modelo generado por el PythonPart
        model_default_attrs = _get_attributes_from_model_elem(model_elem)
        # 2) Defaults cacheados por key (compatibilidad con el flujo actual)
        key_default_attrs = _normalize_attribute_list(
            so.default_attributes.get(base_key, []) if base_key else []
        )
        # 3) Atributos custom aplicados desde paleta
        custom_attrs = _normalize_attribute_list(
            so.applied_attributes.get(assignment_key, [])
        )

        expected_inner_type = outer_inner_type_map.get(element_type)
        has_outer_inner_pair = False
        if expected_inner_type and seq_idx + 1 < len(elements_generated):
            next_item = elements_generated[seq_idx + 1]
            has_outer_inner_pair = next_item.element_type == expected_inner_type

        is_td = str(distribution_type).upper() == "TD"
        is_outer_cavitat = bool(
            doc
            and is_td
            and has_outer_inner_pair
            and _has_material_cavitat(model_elem, doc)
        )

        if is_outer_cavitat:
            # En TD, el outer (Material=CAVITAT) debe conservar:
            # - su atributo Material propio del modelo
            # - su layer por defecto del modelo (no layer de paleta)
            so.applied_default_attributes[storage_key] = list(model_default_attrs)
        else:
            merged_defaults = (
                _merge_attributes(key_default_attrs, model_default_attrs)
                if key_default_attrs
                else list(model_default_attrs)
            )
            merged_attrs = (
                _merge_attributes(merged_defaults, custom_attrs)
                if custom_attrs
                else list(merged_defaults)
            )

            if merged_attrs:
                model_elem = _apply_attributes_to_model_elem(model_elem, merged_attrs)
            so.applied_default_attributes[storage_key] = merged_attrs

        diameter_raw = (
            getattr(seg_info, "diameter", None) if seg_info is not None else None
        )
        if isinstance(diameter_raw, (list, tuple)) and diameter_raw:
            diameter_raw = diameter_raw[0]
        try:
            diameter_mm = int(round(float(diameter_raw))) if diameter_raw else 20
        except Exception:
            diameter_mm = 20

        custom_parent_value = _extract_attr_value_from_list(custom_attrs)
        if not custom_parent_value:
            try:
                if hasattr(so, "build_ele") and hasattr(so.build_ele, "NomIS"):
                    nomis_attr = getattr(so.build_ele, "NomIS", None)
                    custom_parent_value = str(
                        getattr(nomis_attr, "value", nomis_attr) or ""
                    ).strip()
            except Exception:
                custom_parent_value = ""

        if custom_parent_value and doc:
            _set_parent_attributes(
                model_elem,
                {"NomIS": custom_parent_value},
                doc,
                distribution_type=str(distribution_type),
            )

        if element_type == "tubo_agua":
            _apply_absolute_numbering_attr01(
                model_elem,
                so,
                diameter_mm=diameter_mm,
                distribution_type=str(distribution_type),
            )

        if not is_outer_cavitat:
            model_elem = _apply_layer_to_element(model_elem, assignment_key, so)
        item.element = model_elem
        elements_generated_final.append(item)

    if so.init_storage:
        so.init_storage._save_numbering_file()

    return elements_generated_final


# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================
#
# Las funciones auxiliares de atributos y layers se han movido a:
#   - utils/attributes_utils.py
#   - utils/layers_utils.py
# y se importan al inicio de este módulo.
