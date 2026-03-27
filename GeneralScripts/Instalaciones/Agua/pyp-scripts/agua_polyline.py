# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib
import math

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

    expected_storage_keys: set[str] = set()
    for path_group in generated_paths:
        for element in path_group or []:
            key = element.get("key") if isinstance(element, dict) else None
            if not key or len(key) < 5:
                continue
            # Estructura usada por PolyLib: seg_{key[4]}_elem_{key[3]}
            expected_storage_keys.add(f"seg_{key[4]}_elem_{key[3]}")

    if not expected_storage_keys:
        return [], []

    applied_layers = getattr(so, "applied_layers", {}) or {}
    applied_attrs = getattr(so, "applied_attributes", {}) or {}

    missing_layers = [k for k in expected_storage_keys if k not in applied_layers]

    # Si hay padre global en paleta, no exigimos atributo por elemento.
    parent_global = _get_parent_value_from_palette(so)
    if parent_global:
        missing_parent = []
    else:
        missing_parent = [
            k
            for k in expected_storage_keys
            if not _attr_has_non_empty_value(applied_attrs.get(k, []))
        ]

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


def _ensure_validation_context_ready(so: PBL.script_object.PolylineScriptObject) -> None:
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
        if getattr(intr, "create_mode", False) and len(getattr(intr, "points", []) or []) >= 2:
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
    return True


def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )
    # HOOK: Creación de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creación de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    # Validación UX previa a finalizar: layer + atributo padre.
    original_on_control_event = script_object.on_control_event

    def _on_control_event_with_reminder(event_id: int):
        try:
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

        return original_on_control_event(event_id)

    script_object.on_control_event = _on_control_event_with_reminder

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
