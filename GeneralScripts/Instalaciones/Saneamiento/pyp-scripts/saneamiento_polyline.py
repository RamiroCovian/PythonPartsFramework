# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib
import math
import os
import re
import sys
import traceback
import time

import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as PythonUtility
import NemAll_Python_AllplanSettings as AllplanSettings

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Saneamiento
from Instalaciones.PolyLib.parameters import EventIds, ParamNames
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.attributes_utils import (
    _apply_absolute_numbering_attr01,
    _apply_attributes_to_model_elem,
    _get_attributes_from_model_elem,
    _merge_attributes,
    _normalize_attribute_list,
)
from .utils.geo_handler import PipelineProcessor
from .utils.layers_utils import _apply_layer_to_element
from .utils.te_orientation import build_te_params
from .utils.vertex_utils import (
    compute_segment_cuts_for_all_paths,
    detect_bifurcations,
    detect_cross_path_elbows,
    detect_cross_path_manguitos,
)

# Claves de codos por diámetro/sistema:
# - Ø25 fecal mantiene codo_45/codo_90 dedicados.
# - Ø40 fecal usa codo_45_40 y codo_90_40.
# - Ø110 fecal usa codo_45_110 y codo_90_110.
# En ambos casos, 90° se resuelve como 2x45 salvo cambio de plano en el pipeline.
FECAL_ELBOW_KEYS_BY_DIAMETER = {
    25: ("codo_45", "codo_90"),
    40: ("codo_45_40", "codo_90_40"),
    110: ("codo_45_110", "codo_90_110"),
}
PLUVIAL_ELBOW_KEYS_BY_DIAMETER = {
    110: ("codo_45_110_p", "codo_90_110_p"),
}

# ---------------- CUSTOM ABSOLUTE ENUM PATH ----------------
project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(project_name, host_name)
if error != 0:
    base_path = AllplanSettings.AllplanPaths.GetCurPrjPath()

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Saneamiento.profile()
# Ocultar en paleta "Tipo de Distribucion" para Saneamiento.
profile.show.distribution_type = False
profile.enabled.distribution_type = False

# ---------------- DEFAULT CONFIG PARAMS ----------------
INST_NAME = "SANEAMIENTO"
CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation=INST_NAME.upper(),
    parameters_show=profile.show,
    parameters_enabled=profile.enabled,
    num_td_path=base_path,
    limit_angles=True,
    # Igual que Saneamiento_old: solo recto y giros de 45/90 (izq/der),
    # sin ángulos "cerrados" (135/180) en el limitador.
    allowed_angles=[0.0, 45.0, 90.0, -45.0, -90.0],
)

# ------ MODULES LOADED FOR TEST ------
reload_module = [
    PBL,
    PBL_interactor,
    PBL_object,
]

_HOT_RELOAD_ENABLED = str(os.getenv("SANEAMIENTO_HOT_RELOAD", "0")).strip().lower() in (
    "1",
    "true",
    "yes",
)
_SANEAMIENTO_DEBUG_HOOKS = str(
    os.getenv("SANEAMIENTO_DEBUG_HOOKS", "0")
).strip().lower() in ("1", "true", "yes")
_SANEAMIENTO_DEBUG_SEGMENTS_DUMP = str(
    os.getenv("SANEAMIENTO_DEBUG_SEGMENTS_DUMP", "0")
).strip().lower() in ("1", "true", "yes")
_SANEAMIENTO_PERF_DEBUG = str(
    os.getenv("SANEAMIENTO_PERF_DEBUG", "0")
).strip().lower() in ("1", "true", "yes")


def _reload_saneamiento_runtime_modules():
    """
    Hot-reload de scripts de saneamiento en tiempo de ejecución para evitar
    cerrar/abrir Allplan en cada ajuste fino de PythonParts.
    """
    # En Allplan, algunos nombres de módulo pueden incluir "pyp-scripts" (con guion),
    # lo que no siempre permite import_module directo. Reutilizamos módulos ya cargados.
    target_suffixes = (
        "polyline_reg_saneamiento",
        "tub_pvc_basic_f_25_script",
        "tub_pvc_tricapa_f_40_script",
        "tub_pvc_tricapa_v_script",
        "tub_pvc_tricapa_p_110_script",
        "tub_pvc_tricapa_f_110_script",
        "Colze_basic_25m_f_45_script",
        "Colze_basic_25m_f_90_script",
        "colze_rigid_40mm_f_45_script",
        "Colze_rigid_40m_f_90_script",
        "Colze_rigid_110m_f_45_script",
        "Colze_rigid_110m_f_90_script",
        "Colze_rigid_110m_p_45_script",
        "Colze_rigid_110m_p_90_script",
        "DerivacionY45_script",
        "Derivacion110m_f_script",
        "Derivacion110m_p_script",
        "utils.elbow_orientation",
        "utils.geo_handler",
        "utils.trim_config",
        "utils.vertex_utils",
    )
    loaded = list(sys.modules.items())
    for mod_name, mod in loaded:
        if not mod or not isinstance(mod_name, str):
            continue
        if "Instalaciones.Saneamiento" not in mod_name:
            continue
        if not mod_name.endswith(target_suffixes):
            continue
        try:
            importlib.reload(mod)
            if mod_name.endswith("utils.geo_handler") or mod_name.endswith(
                "DerivacionY45_script"
            ) or mod_name.endswith("Derivacion110m_f_script") or mod_name.endswith(
                "Derivacion110m_p_script"
            ):
                for _gh_mn, _gh_mod in list(sys.modules.items()):
                    if _gh_mn.endswith("utils.geo_handler") and _gh_mod is not None:
                        setattr(_gh_mod, "_DERIV_Y45_D40_CLASS", None)
                        setattr(_gh_mod, "_DERIV_Y45_D40_LOAD_FAILED", False)
                        setattr(_gh_mod, "_DERIV_Y110_FECAL_CLASS", None)
                        setattr(_gh_mod, "_DERIV_Y110_FECAL_LOAD_FAILED", False)
                        setattr(_gh_mod, "_DERIV_Y110_PLUVIAL_CLASS", None)
                        setattr(_gh_mod, "_DERIV_Y110_PLUVIAL_LOAD_FAILED", False)
                        break
        except Exception as ex:
            print(f"[SANEAMIENTO][HOT-RELOAD] {mod_name}: {ex}")

    # importlib.reload actualiza el módulo, pero `from .utils.geo_handler import
    # PipelineProcessor` dejó la referencia a la clase antigua: re-enlazar.
    try:
        _poly = sys.modules.get(__name__)
        if _poly is not None:
            for _mn, _mod in list(sys.modules.items()):
                if _mn.endswith("utils.geo_handler") and _mod is not None:
                    _pc = getattr(_mod, "PipelineProcessor", None)
                    if _pc is not None:
                        _poly.PipelineProcessor = _pc
                        break
    except Exception as _ex:
        print(f"[SANEAMIENTO][HOT-RELOAD] rebind PipelineProcessor: {_ex}")


def _parse_diameter_palette_value(raw):
    """Normaliza el valor del combo DiameterType (int, float o '110 mm')."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return int(round(float(raw)))
    s = str(raw).strip().lower().replace("mm", "").strip()
    try:
        return int(round(float(s)))
    except (TypeError, ValueError):
        return None


def _diameter_list_as_ints(diameter_list):
    if not diameter_list:
        return []
    out = []
    for x in diameter_list:
        v = _parse_diameter_palette_value(x)
        if v is not None:
            out.append(v)
    return out


def _patch_resolve_installation_config_sync_diameter(so):
    """
    PolyLib actualiza `so.diameter_type` al cambiar InstallationType pero no siempre
    escribe el mismo valor en `build_ele.DiameterType`, de modo que la paleta puede
    seguir mostrando p. ej. 110 mm mientras la lógica usa el primer diámetro del
    nuevo tipo (25 mm en Fecal). Sin tocar PolyLib: envolvemos resolve_installation_config.
    """
    if getattr(so, "_saneamiento_resolve_diameter_patched", False):
        return
    so._saneamiento_resolve_diameter_patched = True
    orig = so.resolve_installation_config

    def wrapped():
        prev_ui = None
        try:
            param = getattr(so.build_ele, ParamNames.Installation.DIAMETER_TYPE, None)
            if param is not None and hasattr(param, "value"):
                prev_ui = _parse_diameter_palette_value(param.value)
        except Exception:
            pass

        result = orig()
        valid = _diameter_list_as_ints(so.diameter_list)
        if not valid:
            return result

        chosen = None
        if prev_ui is not None and prev_ui in valid:
            chosen = prev_ui
        else:
            chosen = _parse_diameter_palette_value(so.diameter_type)

        if chosen is None:
            chosen = valid[0]

        so.diameter_type = chosen
        try:
            param = getattr(so.build_ele, ParamNames.Installation.DIAMETER_TYPE, None)
            if param is not None:
                param.value = chosen
        except Exception:
            pass

        return result

    so.resolve_installation_config = wrapped


_SEG_KEY_RE = re.compile(r"^seg_(\d+)_elem_(\d+)$")
_META_KEY_RE = re.compile(r"^(\d+)_(\d+)$")


def _reverse_storage_map_by_path_segments(
    data_map: dict, seg_count_by_path: dict[int, int]
) -> dict:
    """
    Remapea claves tipo seg_{path}_elem_{idx} al invertir el sentido de cada path.
    """
    if not isinstance(data_map, dict) or not data_map:
        return data_map if isinstance(data_map, dict) else {}

    out = {}
    for key, value in data_map.items():
        m = _SEG_KEY_RE.match(str(key))
        if not m:
            out[key] = value
            continue
        path_idx = int(m.group(1))
        elem_idx = int(m.group(2))
        seg_count = int(seg_count_by_path.get(path_idx, 0))
        if seg_count <= 0:
            out[key] = value
            continue
        new_elem_idx = (seg_count - 1) - elem_idx
        if new_elem_idx < 0:
            new_elem_idx = 0
        out[f"seg_{path_idx}_elem_{new_elem_idx}"] = value
    return out


def _reverse_persistent_metadata_by_path_segments(
    metadata: dict, seg_count_by_path: dict[int, int]
) -> dict:
    """
    Remapea claves tipo {path}_{seg} al invertir el sentido de cada path.
    """
    if not isinstance(metadata, dict) or not metadata:
        return metadata if isinstance(metadata, dict) else {}

    out = {}
    for key, value in metadata.items():
        m = _META_KEY_RE.match(str(key))
        if not m:
            out[key] = value
            continue
        path_idx = int(m.group(1))
        seg_idx = int(m.group(2))
        seg_count = int(seg_count_by_path.get(path_idx, 0))
        if seg_count <= 0:
            out[key] = value
            continue
        new_seg_idx = (seg_count - 1) - seg_idx
        if new_seg_idx < 0:
            new_seg_idx = 0
        out[f"{path_idx}_{new_seg_idx}"] = value
    return out


def _invertir_caval_saneamiento(so) -> bool:
    """
    Invierte el sentido de la instalación (inicio<->final) por path.
    No rota geometría 180°; invierte la direccionalidad para que fittings
    (p.ej. codos 45°) se recalculen como su opuesto lógico en el pipeline.
    """
    intr = getattr(so, "script_object_interactor", None)

    # Si hay una polilínea activa en creación, guardarla para incluirla en la inversión.
    try:
        if intr and getattr(intr, "create_mode", False) and len(getattr(intr, "points", []) or []) >= 2:
            save_fn = getattr(intr, "_save_current_polyline", None)
            if callable(save_fn):
                save_fn()
    except Exception as ex:
        print(f"[SANEAMIENTO][INVERTIR] No se pudo guardar polilínea activa: {ex}")

    paths = list(getattr(so, "saved_paths", []) or [])
    if not paths:
        PythonUtility.ShowMessageBox(
            "No hay instalación guardada para invertir.",
            PythonUtility.MB_OK,
        )
        return True

    seg_count_by_path = {
        idx: max(len(path) - 1, 0) for idx, path in enumerate(paths)
    }

    # 1) Invertir direccionalidad de puntos por path.
    so.saved_paths = [list(reversed(path)) for path in paths]

    # 2) Remapear metadata y asignaciones por índice de segmento.
    so.persistent_metadata = _reverse_persistent_metadata_by_path_segments(
        getattr(so, "persistent_metadata", {}) or {},
        seg_count_by_path,
    )
    so.applied_layers = _reverse_storage_map_by_path_segments(
        getattr(so, "applied_layers", {}) or {},
        seg_count_by_path,
    )
    so.applied_attributes = _reverse_storage_map_by_path_segments(
        getattr(so, "applied_attributes", {}) or {},
        seg_count_by_path,
    )
    so.applied_default_attributes = _reverse_storage_map_by_path_segments(
        getattr(so, "applied_default_attributes", {}) or {},
        seg_count_by_path,
    )

    # 3) Recalcular segmentos + preview.
    if intr:
        try:
            intr.points.clear()
        except Exception:
            pass
        try:
            intr.selected_seg = None
            intr.selected_segments = []
            intr.selected_junction = None
        except Exception:
            pass

        get_segments_fn = getattr(intr, "get_segments", None)
        if callable(get_segments_fn):
            get_segments_fn()
        update_groups_fn = getattr(intr, "_update_segment_groups", None)
        if callable(update_groups_fn):
            update_groups_fn()
        create_preview_fn = getattr(so, "_create_elements_preview", None)
        if callable(create_preview_fn):
            create_preview_fn()
        draw_preview_fn = getattr(intr, "_generate_elements_for_preview", None)
        if callable(draw_preview_fn):
            draw_preview_fn()

    PythonUtility.ShowMessageBox(
        "Instalación invertida: ahora va de final a inicio.",
        PythonUtility.MB_OK,
    )
    return True


# ---------------------------------------------------------------------------
# Auto-inversión de segmentos rama de bifurcación
# ---------------------------------------------------------------------------

class _FlippedSegData:
    """
    Proxy de segment.data que intercambia start/end y niega el vector
    para que el pipeline renderice el segmento en sentido opuesto.
    """
    def __init__(self, data):
        self._d = data
        self.start = data.end
        self.end = data.start
        v = getattr(data, "vector_normalizado", None)
        # Debe ser un AllplanGeo.Vector3D real para que los bindings C++ funcionen.
        self.vector_normalizado = (
            AllplanGeo.Vector3D(-v.X, -v.Y, -v.Z) if v is not None else v
        )
        ang = float(getattr(data, "angulo_xy", 0.0))
        inverted = (ang + 180.0) % 360.0
        if inverted > 180.0:
            inverted -= 360.0
        self.angulo_xy = inverted
        self.angulo_z = -float(getattr(data, "angulo_z", 0.0))

    def __getattr__(self, name):
        return getattr(self._d, name)


class _FlippedSeg:
    """Proxy de segmento con dirección invertida (start↔end) para auto-inversión de rama."""
    def __init__(self, seg):
        self._seg = seg
        self.data = _FlippedSegData(seg.data)
        self.info = getattr(seg, "info", None)
        self.name = getattr(seg, "name", "")

    def __getattr__(self, name):
        return getattr(self._seg, name)


def _compute_branch_invert_paths(
    vertex_map: dict,
    te_vertices: set,
    segment_groups: list,
) -> set[int]:
    """
    Devuelve el conjunto de path_idx cuya rama sale del nodo TE hacia afuera
    (is_start=True en el vértice) y por tanto necesita inversión automática
    para que las flechas converjan en lugar de divergir.
    """
    branch_paths: set[int] = set()

    for vkey in te_vertices:
        conns = vertex_map.get(vkey, [])
        if len(conns) != 3:
            continue

        dirs: list[tuple[float, float, float]] = []
        for c in conns:
            p_idx = c["path_idx"]
            s_idx = c["seg_idx"]
            is_start = c.get("is_start", True)
            if p_idx >= len(segment_groups) or s_idx >= len(segment_groups[p_idx]):
                dirs.append((0.0, 0.0, 0.0))
                continue
            seg = segment_groups[p_idx][s_idx]
            data = getattr(seg, "data", None)
            if not data:
                dirs.append((0.0, 0.0, 0.0))
                continue
            pt_s = getattr(data, "start", None)
            pt_e = getattr(data, "end", None)
            if not pt_s or not pt_e:
                dirs.append((0.0, 0.0, 0.0))
                continue
            if is_start:
                vx, vy, vz = pt_e.X - pt_s.X, pt_e.Y - pt_s.Y, pt_e.Z - pt_s.Z
            else:
                vx, vy, vz = pt_s.X - pt_e.X, pt_s.Y - pt_e.Y, pt_s.Z - pt_e.Z
            ln = math.sqrt(vx * vx + vy * vy + vz * vz)
            dirs.append((vx / ln, vy / ln, vz / ln) if ln > 1e-9 else (0.0, 0.0, 0.0))

        def _dot(a, b):
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

        # El par con dot más negativo es el troncal (dos segmentos opuestos).
        # El índice sobrante (k) es la rama.
        candidates = [
            (_dot(dirs[0], dirs[1]), 0, 1, 2),
            (_dot(dirs[0], dirs[2]), 0, 2, 1),
            (_dot(dirs[1], dirs[2]), 1, 2, 0),
        ]
        dot_main, _, _, k = min(candidates, key=lambda x: x[0])
        if dot_main > -0.5:
            continue

        branch_conn = conns[k]
        # is_start=True → el nodo TE es el START del segmento rama → fluye hacia afuera → invertir
        if branch_conn.get("is_start", True):
            branch_paths.add(branch_conn["path_idx"])

    return branch_paths


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

    _patch_resolve_installation_config_sync_diameter(script_object)

    # Igual que en Agua: interceptamos evento en script_object para no cargar PolyLib
    # con lógica específica de Saneamiento.
    original_on_control_event = script_object.on_control_event

    def _on_control_event_saneamiento(event_id: int):
        if event_id == EventIds.INVERTIR_CAVAL:
            try:
                return _invertir_caval_saneamiento(script_object)
            except Exception as ex:
                print(f"[SANEAMIENTO][INVERTIR] Error: {ex}")
                print(traceback.format_exc())
                PythonUtility.ShowMessageBox(
                    f"No se pudo invertir la instalación:\n{ex}",
                    PythonUtility.MB_OK,
                )
                return True
        return original_on_control_event(event_id)

    script_object.on_control_event = _on_control_event_saneamiento

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
    t0_total = time.perf_counter()
    if _SANEAMIENTO_DEBUG_SEGMENTS_DUMP:
        print("################################## so.saved_segments: ", segments)
    try:
        installation_val = getattr(
            getattr(getattr(so, "build_ele", None), "InstallationType", None), "value", None
        )
        print(
            f"[SANEAMIENTO][DEBUG] segments_count={len(segments)} "
            f"diameter_type={getattr(so, 'diameter_type', None)} "
            f"installation={installation_val}"
        )
    except Exception:
        pass
    elements_generated = []
    # Hot reload es útil en desarrollo, pero penaliza mucho en modelos largos.
    if _HOT_RELOAD_ENABLED:
        _reload_saneamiento_runtime_modules()

    # Guardamos la orientación 3D de referencia
    so.reference_orientation_angle = getattr(so, "reference_orientation_angle", None)

    model_base = so.current_inst_config
    element_type_core = None
    base_color = None
    if model_base:
        element_type_core = model_base["key"]
        base_color = model_base["color"]

    # Diámetro activo (combo o primer valor del tipo de instalación)
    if so.diameter_list is not None and so.diameter_type is not None:
        diam = int(so.diameter_type)
    elif model_base:
        raw_d = model_base["diameter"]
        diam = int(raw_d[0] if isinstance(raw_d, (list, tuple)) else raw_d)
    else:
        diam = None

    # ------------------------------------------------------------------
    # CASO A: Saneamiento — Pluvial / Fecal (cada diámetro → su PythonPart)
    # ------------------------------------------------------------------
    if (
        model_base
        and element_type_core in ("tub_pvc_tricapa", "tub_pvc_tricapa_v")
        and diam is not None
    ):
        if element_type_core == "tub_pvc_tricapa":
            if diam == 25:
                element_key = "tub_pvc_basic_f_25"
                exec_kwargs = {"rot_x": 180.0, "rot_y": 0.0, "rot_z": 0.0}
            elif diam == 110:
                element_key = "tub_pvc_tricapa_f_110"
                exec_kwargs = {}
            else:
                element_key = "tub_pvc_tricapa_f_40"
                exec_kwargs = {"TipoTubo": 2}
        else:
            # Pluvial: Ø110 → script dedicado; otro diámetro (p. ej. 40) → tricapa_v
            if diam == 110:
                element_key = "tub_pvc_tricapa_p_110"
                exec_kwargs = {}
            else:
                element_key = "tub_pvc_tricapa_v"
                exec_kwargs = {"TipoTubo": 2}

        t_get_models = time.perf_counter()
        conduct_model = so._get_pythonpart_installed(
            element_key=element_key,
            exec_kwargs=exec_kwargs,
            attr_kwargs=exec_kwargs,
        )
        if _SANEAMIENTO_DEBUG_HOOKS:
            print(
                f"[SANEAMIENTO][DEBUG] conduct_key={element_key} "
                f"exec_kwargs={exec_kwargs} "
                f"loaded={bool(conduct_model)} "
                f"len={len(conduct_model) if conduct_model else 0}"
            )

        if conduct_model:
            codo_45_model = None
            codo_90_model = None
            # Codos dedicados por sistema/diámetro.
            # Fecal: Ø25/Ø40/Ø110. Pluvial: Ø110 (misma geometría que fecal con script propio).
            if element_type_core == "tub_pvc_tricapa":
                elbow_keys = FECAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam))
            else:
                elbow_keys = PLUVIAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam))

            if elbow_keys:
                codo_45_key, codo_90_key = elbow_keys
                codo_45_exec_kwargs = (
                    {}
                    if codo_45_key in ("codo_45_110", "codo_45_110_p")
                    else {"TipoSaneamiento": 0}
                )
                codo_45_model = so._get_pythonpart_installed(
                    element_key=codo_45_key,
                    exec_kwargs=codo_45_exec_kwargs,
                    attr_kwargs=codo_45_exec_kwargs,
                )
                # codo_90_40 se resuelve con script dedicado 87° para cambio de plano.
                # El resto mantiene TipoSaneamiento explícito para los scripts duales.
                codo_90_exec_kwargs = (
                    {}
                    if codo_90_key in ("codo_90_40", "codo_90_110", "codo_90_110_p")
                    else {"TipoSaneamiento": 1}
                )
                codo_90_model = so._get_pythonpart_installed(
                    element_key=codo_90_key,
                    exec_kwargs=codo_90_exec_kwargs,
                    attr_kwargs=codo_90_exec_kwargs,
                )
                if _SANEAMIENTO_DEBUG_HOOKS:
                    print(
                        f"[SANEAMIENTO][DEBUG] elbows diam={diam} "
                        f"c45_key={codo_45_key} c45_len={len(codo_45_model) if codo_45_model else 0} "
                        f"c90_key={codo_90_key} c90_len={len(codo_90_model) if codo_90_model else 0}"
                    )

            # AQUI CAPAZ YA PODRIAS OBTENER LOS MODEL 3D DE CODOS, REDUCTORES, UNIONES, ETC.
            # USAR SIEMPRE LA FUNCION "so._get_pythonpart_installed" PARA LLAMAR A LOS SCRIPTS

            # YA TENIENDO TODOS LOS SCRIPTS (MODEL 3D)
            # TE QUEDA IMPLEMENTAR LA LOGICA PARA  GENERAR EL 3D EN BASE A LO QUE LLEGA AQUI "segments"
            # CONSEJO: AGREGAR EN LA CARPETA UTILS LOS METODOS DE CLASE PARA GENERAR EL 3D.
            # TE DEJO DE EJEMPLO ACA ABAJO.. (BORRAR Y MODIFICAR COMO TE GUSTE)
            elem3D_list = [
                {
                    "type": "tubo_saneamiento",
                    "elem": conduct_model[0],
                    "rotate": True,
                    "color": base_color,
                }
            ]
            if codo_45_model:
                elem3D_list.append(
                    {"type": "codo_45", "elem": codo_45_model[0], "rotate": True}
                )
                if len(codo_45_model) > 1:
                    elem3D_list.append(
                        {"type": "codo_45_inner", "elem": codo_45_model[1], "rotate": True}
                    )
                if len(codo_45_model) > 2:
                    elem3D_list.append(
                        {"type": "codo_45_inner_2", "elem": codo_45_model[2], "rotate": True}
                    )
            if codo_90_model:
                elem3D_list.append(
                    {"type": "codo_90", "elem": codo_90_model[0], "rotate": True}
                )
                if len(codo_90_model) > 1:
                    elem3D_list.append(
                        {"type": "codo_90_inner", "elem": codo_90_model[1], "rotate": True}
                    )
                if len(codo_90_model) > 2:
                    elem3D_list.append(
                        {
                            "type": "codo_90_inner_2",
                            "elem": codo_90_model[2],
                            "rotate": True,
                        }
                    )
            if element_type_core == "tub_pvc_tricapa" and 40 in _diameter_list_as_ints(
                model_base.get("diameter", [])
            ):
                bif_te = so._get_pythonpart_installed(
                    element_key="bifurcacion_y40",
                    exec_kwargs={},
                    attr_kwargs={},
                )
                if bif_te:
                    elem3D_list.append(
                        {"type": "te", "elem": bif_te[0], "rotate": True}
                    )
            if element_type_core == "tub_pvc_tricapa_v" and 110 in _diameter_list_as_ints(
                model_base.get("diameter", [])
            ):
                bif_te110 = so._get_pythonpart_installed(
                    element_key="bifurcacion_y110_pluvial",
                    exec_kwargs={},
                    attr_kwargs={},
                )
                if bif_te110:
                    elem3D_list.append(
                        {"type": "te", "elem": bif_te110[0], "rotate": True}
                    )
            if element_type_core == "tub_pvc_tricapa" and 110 in _diameter_list_as_ints(
                model_base.get("diameter", [])
            ):
                bif_te110_f = so._get_pythonpart_installed(
                    element_key="bifurcacion_y110_fecal",
                    exec_kwargs={},
                    attr_kwargs={},
                )
                if bif_te110_f:
                    elem3D_list.append(
                        {"type": "te", "elem": bif_te110_f[0], "rotate": True}
                    )
            # Tricapa con anillo: regenerar por longitud de tramo (el anillo no se escala).
            # Ø25 básico sigue usando solo el template + escalado en el pipeline.
            _rebuild_ring_tube_keys = frozenset(
                {
                    "tub_pvc_basic_f_25",
                    "tub_pvc_tricapa_p_110",
                    "tub_pvc_tricapa_f_110",
                    "tub_pvc_tricapa_v",
                    "tub_pvc_tricapa_f_40",
                }
            )
            proc_kw = dict(
                elem3D_list=elem3D_list,
                element_type="tubo_saneamiento",
                build_ele=getattr(so, "build_ele", None),
                doc=so.coord_input.GetInputViewDocument() if so.coord_input else None,
            )
            if element_key in _rebuild_ring_tube_keys:
                rebuild_stats = {"calls": 0, "hits": 0, "misses": 0, "time_s": 0.0}

                def _rebuild_tubo_saneamiento(length_mm: float, seg_info=None):
                    t_rebuild = time.perf_counter()
                    rebuild_stats["calls"] += 1
                    # Resolver modelo por segmento para soportar rutas mixtas
                    # (p.ej. un tramo Pluvial 110 y otro Fecal 110 en la misma polilínea).
                    local_key = element_key
                    local_exec_kwargs = dict(exec_kwargs)
                    try:
                        seg_d = getattr(seg_info, "diameter", None)
                        if isinstance(seg_d, (list, tuple)) and seg_d:
                            seg_d = seg_d[0]
                        seg_d = int(seg_d) if seg_d is not None else None
                    except Exception:
                        seg_d = None
                    seg_system = str(getattr(seg_info, "system", "") or "").strip().lower()

                    if seg_d == 110:
                        local_key = (
                            "tub_pvc_tricapa_f_110"
                            if seg_system == "fecal"
                            else "tub_pvc_tricapa_p_110"
                        )
                        local_exec_kwargs = {}
                    elif seg_d == 40:
                        local_key = (
                            "tub_pvc_tricapa_f_40"
                            if seg_system == "fecal"
                            else "tub_pvc_tricapa_v"
                        )
                        local_exec_kwargs = {"TipoTubo": 2}
                    elif seg_d == 25:
                        local_key = "tub_pvc_basic_f_25"
                        local_exec_kwargs = {
                            "rot_x": 180.0,
                            "rot_y": 0.0,
                            "rot_z": 0.0,
                        }
                    # Cache entre refrescos para no re-ejecutar scripts en cada preview.
                    cache = getattr(so, "_saneamiento_rebuild_cache", None)
                    if cache is None:
                        cache = {}
                        so._saneamiento_rebuild_cache = cache
                    cache_key = (
                        str(local_key),
                        round(float(length_mm), 2),
                        tuple(sorted((local_exec_kwargs or {}).items())),
                    )
                    if cache_key in cache:
                        rebuild_stats["hits"] += 1
                        rebuild_stats["time_s"] += time.perf_counter() - t_rebuild
                        return cache[cache_key]
                    rebuild_stats["misses"] += 1

                    if _SANEAMIENTO_DEBUG_HOOKS:
                        print(
                            f"[SANEAMIENTO][REBUILD] seg_d={seg_d} seg_system={seg_system} "
                            f"-> key={local_key}"
                        )

                    elems = so._get_pythonpart_installed(
                        element_key=local_key,
                        exec_kwargs={
                            **local_exec_kwargs,
                            "LargoTramoMm": float(length_mm),
                        },
                        attr_kwargs=local_exec_kwargs,
                    )
                    if not elems:
                        if _SANEAMIENTO_DEBUG_HOOKS:
                            print(
                                f"[SANEAMIENTO][DEBUG][REBUILD] key={local_key} "
                                f"returned empty for length={length_mm}"
                            )
                        return None
                    if _SANEAMIENTO_DEBUG_HOOKS:
                        print(
                            f"[SANEAMIENTO][DEBUG][REBUILD] key={local_key} "
                            f"len={len(elems)} exec={local_exec_kwargs}"
                        )
                    # Los scripts con flecha propia BRep deben devolver lista completa.
                    if local_key in (
                        "tub_pvc_basic_f_25",
                        "tub_pvc_tricapa_f_40",
                        "tub_pvc_tricapa_p_110",
                        "tub_pvc_tricapa_f_110",
                    ):
                        cache[cache_key] = elems
                        rebuild_stats["time_s"] += time.perf_counter() - t_rebuild
                        return elems
                    cache[cache_key] = elems[0]
                    rebuild_stats["time_s"] += time.perf_counter() - t_rebuild
                    return elems[0]

                proc_kw["saneamiento_tube_rebuild"] = _rebuild_tubo_saneamiento

            processor = PipelineProcessor(**proc_kw)
            processor.saneamiento_fecal_tricapa_install = (
                element_type_core == "tub_pvc_tricapa"
            )
            processor.reference_orientation_angle = getattr(
                so, "reference_orientation_angle", None
            )
            path_idx = next(
                (i for i, sg in enumerate(so.segment_groups) if sg is segments),
                0,
            )
            split_segment_groups = list(so.segment_groups)

            vertex_map, te_vertices = detect_bifurcations(split_segment_groups)
            if te_vertices:
                print(
                    f"[SANEAMIENTO] Bifurcaciones detectadas (TE): {len(te_vertices)}"
                )

            cross_path_elbows_all = detect_cross_path_elbows(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )
            cross_path_manguitos_all = detect_cross_path_manguitos(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )

            processor.te_nodes = (
                build_te_params(
                    split_segment_groups,
                    vertex_map,
                    te_vertices,
                    saneamiento_enforce_y45_branch_geometry=True,
                )
                if te_vertices
                else {}
            )
            # TE 40-40-40; TE 110-110-110: script fecal vs pluvial según `y110_bif_script_variant`.
            if processor.te_nodes:
                for _te_params in processor.te_nodes.values():
                    try:
                        di_in = int(round(float(_te_params.get("d_main_in", 0) or 0)))
                        di_out = int(round(float(_te_params.get("d_main_out", 0) or 0)))
                        di_br = int(round(float(_te_params.get("d_branch", 0) or 0)))
                        # TE 40-40-40: misma orientación moderna (te_orientation + Parte 2)
                        # que Ø110; no usar try_apply_old_d40_bif_transform.
                        if di_in == 110 and di_out == 110 and di_br == 110:
                            _te_params[
                                "use_saneamiento_old_d110_pluvial_orientation"
                            ] = True
                        elif di_in == 110 and di_out == 110 and di_br == 40:
                            _te_params[
                                "use_saneamiento_old_d110_y40_orientation"
                            ] = True
                            if str(
                                os.getenv("SANEAMIENTO_DEBUG_TE_Y110_40", "0")
                            ).strip().lower() in ("1", "true", "yes", "on"):
                                _cp = _te_params.get("center_pt")
                                print(
                                    "[SANEAMIENTO][TE-Y110-40][DEBUG] te_nodes: "
                                    "use_saneamiento_old_d110_y40_orientation "
                                    f"d_main_in={di_in} d_main_out={di_out} d_branch={di_br} "
                                    f"center_pt={_cp} plane={_te_params.get('plane')!r}"
                                )
                    except Exception:
                        pass
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

            _te_skip_cuts: set | None = None
            if te_vertices:
                _te_skip_cuts = te_vertices - set((processor.te_nodes or {}).keys())

            all_cuts = compute_segment_cuts_for_all_paths(
                split_segment_groups,
                skip_te_vertices=_te_skip_cuts,
            )
            segment_cuts = {
                seg_idx: all_cuts.get((path_idx, seg_idx), {"start": 0.0, "end": 0.0})
                for seg_idx in range(len(segments))
            }

            # Auto-inversión de segmentos rama: cuando la rama sale desde el nodo TE
            # hacia afuera (diverge), invertimos localmente para que converja.
            if te_vertices:
                branch_invert_paths = _compute_branch_invert_paths(
                    vertex_map, te_vertices, split_segment_groups
                )
                if path_idx in branch_invert_paths:
                    n = len(segments)
                    segments = [_FlippedSeg(s) for s in reversed(segments)]
                    segment_cuts = {
                        (n - 1 - old_i): {
                            "start": c.get("end", 0.0),
                            "end": c.get("start", 0.0),
                        }
                        for old_i, c in segment_cuts.items()
                    }
                    # Remapear junctions cross-path: (seg_idx, is_start) → (n-1-seg_idx, not is_start)
                    processor.cross_path_elbows = {
                        (n - 1 - si, not ist): data
                        for (si, ist), data in processor.cross_path_elbows.items()
                    }
                    processor.cross_path_manguitos = {
                        (n - 1 - si, not ist): data
                        for (si, ist), data in processor.cross_path_manguitos.items()
                    }
                    print(
                        f"[SANEAMIENTO][BRANCH-INVERT] path={path_idx} "
                        f"n_segs={n} auto-invertido para convergencia"
                    )

            # Compartir el set de TE ya insertados entre todos los paths.
            # Esto evita que en bifurcaciones Case-1 (3 paths de 1 segmento)
            # el mismo nodo TE se inserte tres veces (una por path).
            if path_idx == 0:
                so._saneamiento_te_placed_verts = set()
            processor._global_te_inserted = getattr(
                so, "_saneamiento_te_placed_verts", None
            )

            t_pipeline = time.perf_counter()
            try:
                elements_generated = processor.process(
                    segments=segments, segment_cuts=segment_cuts
                )
                print(
                    f"[SANEAMIENTO][DEBUG] process_ok generated={len(elements_generated) if elements_generated else 0}"
                )
                if _SANEAMIENTO_PERF_DEBUG:
                    total_ms = (time.perf_counter() - t0_total) * 1000.0
                    prep_ms = (t_pipeline - t_get_models) * 1000.0
                    pipe_ms = (time.perf_counter() - t_pipeline) * 1000.0
                    r_calls = rebuild_stats["calls"] if "rebuild_stats" in locals() else 0
                    r_hits = rebuild_stats["hits"] if "rebuild_stats" in locals() else 0
                    r_miss = rebuild_stats["misses"] if "rebuild_stats" in locals() else 0
                    r_ms = (
                        rebuild_stats["time_s"] * 1000.0
                        if "rebuild_stats" in locals()
                        else 0.0
                    )
                    print(
                        "[SANEAMIENTO][PERF] "
                        f"segments={len(segments)} generated={len(elements_generated) if elements_generated else 0} "
                        f"total_ms={total_ms:.1f} prep_ms={prep_ms:.1f} pipeline_ms={pipe_ms:.1f} "
                        f"rebuild_calls={r_calls} cache_hits={r_hits} cache_miss={r_miss} rebuild_ms={r_ms:.1f}"
                    )
            except Exception as ex:
                print(
                    f"[SANEAMIENTO][DEBUG][ERROR] processor.process failed: {ex} "
                    f"(type={type(ex).__name__})"
                )
                print(traceback.format_exc())
                raise

    return elements_generated


def _saneamiento_resolve_layer_storage_key(
    so: PBL.script_object.PolylineScriptObject, candidates: list[str]
) -> str:
    """Devuelve la primera clave presente en applied_layers; si ninguna, la primera candidata."""
    applied = getattr(so, "applied_layers", {}) or {}
    for k in candidates:
        if k and k in applied:
            return k
    return candidates[0] if candidates else "seg_0_elem_0"


def _saneamiento_layer_key_candidates_for_index(path_idx: int, elem_idx: int) -> list[str]:
    """Vecinos por desfase entre índice secuencial del pipeline y layer_idx de la UI."""
    keys = [f"seg_{path_idx}_elem_{elem_idx}"]
    for delta in (-2, -1, 1, 2):
        j = elem_idx + delta
        if j >= 0:
            keys.append(f"seg_{path_idx}_elem_{j}")
    return keys


def _is_saneamiento_tube_attached(element_type: str | None) -> bool:
    if not element_type:
        return False
    if element_type == "tubo_saneamiento_inner":
        return True
    if element_type == "tubo_saneamiento_flecha":
        return True
    if element_type.startswith("tubo_saneamiento_copy_dyn_"):
        return True
    if element_type.startswith("tubo_saneamiento_copy_"):
        return True
    return False


def _is_saneamiento_elbow_element(element_type: str | None) -> bool:
    if not element_type:
        return False
    return element_type.startswith("codo_45") or element_type.startswith("codo_90")


def _resolve_assignment_key(
    so: PBL.script_object.PolylineScriptObject,
    default_key: str,
    candidate_keys: list[str] | None = None,
) -> str:
    """
    Igual que en Agua: cuando el índice final difiere del de selección UI,
    usar la primera clave existente en applied_layers/applied_attributes.
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


def _create_elements_with_layers_attrs(
    elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject
) -> list:
    """
    Aplica capas + atributos de paleta y numeración absoluta ATTR01 en tubos (`tubo_saneamiento`).
    Capas: PolyLib `applied_layers`, claves `seg_{path}_elem_{layer_idx}`.

    El interactor guarda la capa del tubo por **índice de tramo** (coincide con el orden de
    `tubo_saneamiento`). Las piezas anexas (inner, flecha, copias del script) reutilizan la
    misma clave que el tubo exterior del tramo. Codos / TE / manguitos: resolución con vecinos
    por si el `index` del pipeline no coincide con el `layer_idx` de la selección.
    """
    if so._config and not getattr(so, "init_storage", None):
        inst_name = str(so._config.default_installation).lower()
        so.init_storage = PolylineStorage(name=inst_name)
        so.init_storage.base_path = so._config.num_td_path

    path_segments: list = []
    runtime_segments = getattr(so, "_runtime_segments_by_path", {})
    if isinstance(runtime_segments, dict) and path_idx in runtime_segments:
        path_segments = runtime_segments[path_idx]
    elif getattr(so, "segment_groups", None) and path_idx < len(so.segment_groups):
        path_segments = so.segment_groups[path_idx]

    if _SANEAMIENTO_DEBUG_HOOKS:
        try:
            print(
                f"[SANEAMIENTO][LAYERHOOK] path={path_idx} elems={len(elements_generated or [])} "
                f"applied_keys={list((getattr(so, 'applied_layers', {}) or {}).keys())}"
            )
        except Exception:
            pass
    elements_generated_final = []
    tube_segment_idx = -1
    last_tube_layer_key: str | None = None
    last_elbow_layer_key: str | None = None

    for seq_idx, item in enumerate(elements_generated or []):
        element_type = getattr(item, "element_type", None)
        model_elem = item.element
        idx = int(getattr(item, "index", 0))
        storage_key = f"seg_{path_idx}_elem_{idx}"

        if element_type == "tubo_saneamiento":
            tube_segment_idx += 1
            seg_key = f"seg_{path_idx}_elem_{tube_segment_idx}"
            layer_key = _resolve_assignment_key(so, storage_key, [seg_key])
            last_tube_layer_key = layer_key
            last_elbow_layer_key = None
        elif _is_saneamiento_tube_attached(element_type):
            base = last_tube_layer_key or f"seg_{path_idx}_elem_{max(tube_segment_idx, 0)}"
            layer_key = _resolve_assignment_key(
                so,
                storage_key,
                [base, f"seg_{path_idx}_elem_{max(tube_segment_idx, 0)}"],
            )
            last_elbow_layer_key = None
        elif _is_saneamiento_elbow_element(element_type):
            prev_is_elbow = False
            if seq_idx - 1 >= 0:
                prev_type = getattr(elements_generated[seq_idx - 1], "element_type", None)
                prev_is_elbow = _is_saneamiento_elbow_element(prev_type)
            if prev_is_elbow and last_elbow_layer_key:
                # Mismo paquete de codo (outer/inner/inner_2): conservar key del primero.
                layer_key = last_elbow_layer_key
            else:
                layer_key = _resolve_assignment_key(
                    so,
                    storage_key,
                    _saneamiento_layer_key_candidates_for_index(path_idx, idx),
                )
                last_elbow_layer_key = layer_key
        else:
            layer_key = _resolve_assignment_key(
                so,
                storage_key,
                _saneamiento_layer_key_candidates_for_index(path_idx, idx),
            )
            if element_type and element_type.endswith("_inner") and seq_idx - 1 >= 0:
                prev_item = elements_generated[seq_idx - 1]
                prev_idx = int(getattr(prev_item, "index", idx))
                layer_key = _resolve_assignment_key(
                    so,
                    layer_key,
                    [f"seg_{path_idx}_elem_{prev_idx}"],
                )
            last_elbow_layer_key = None

        try:
            model_elem = _apply_layer_to_element(model_elem, layer_key, so)
        except Exception as ex:
            print(f"[SANEAMIENTO][LAYER] No se pudo aplicar layer ({layer_key}): {ex}")
        else:
            if _SANEAMIENTO_DEBUG_HOOKS:
                try:
                    p = model_elem.GetCommonProperties()
                    print(
                        f"[SANEAMIENTO][LAYERHOOK] etype={element_type} idx={idx} "
                        f"layer_key={layer_key} final_layer={getattr(p, 'Layer', None)}"
                    )
                except Exception:
                    pass
        try:
            model_default_attrs = _get_attributes_from_model_elem(model_elem)
            custom_attrs = _normalize_attribute_list(
                (getattr(so, "applied_attributes", {}) or {}).get(layer_key, [])
            )
            if custom_attrs:
                merged_attrs = _merge_attributes(model_default_attrs, custom_attrs)
                model_elem = _apply_attributes_to_model_elem(model_elem, merged_attrs)
                if _SANEAMIENTO_DEBUG_HOOKS:
                    try:
                        print(
                            f"[SANEAMIENTO][ATTRHOOK] etype={element_type} idx={idx} "
                            f"key={layer_key} custom={len(custom_attrs)} merged={len(merged_attrs)}"
                        )
                    except Exception:
                        pass
        except Exception as ex:
            if _SANEAMIENTO_DEBUG_HOOKS:
                print(f"[SANEAMIENTO][ATTRHOOK] No se pudo aplicar atributos ({layer_key}): {ex}")

        if element_type == "tubo_saneamiento":
            seg_info = None
            if path_segments and 0 <= tube_segment_idx < len(path_segments):
                seg_info = getattr(path_segments[tube_segment_idx], "info", None)
            distribution_type = (
                getattr(seg_info, "distribution_type", None) if seg_info is not None else None
            )
            if not distribution_type:
                distribution_type = getattr(so, "distribution_type", None) or "IS"
            diameter_raw = getattr(seg_info, "diameter", None) if seg_info is not None else None
            if isinstance(diameter_raw, (list, tuple)) and diameter_raw:
                diameter_raw = diameter_raw[0]
            try:
                if diameter_raw is not None:
                    diameter_mm = int(round(float(diameter_raw)))
                else:
                    dt = getattr(so, "diameter_type", None)
                    diameter_mm = int(round(float(dt))) if dt is not None else 110
            except Exception:
                diameter_mm = 110
            _apply_absolute_numbering_attr01(
                model_elem,
                so,
                diameter_mm=diameter_mm,
                distribution_type=str(distribution_type),
            )

        item.element = model_elem
        elements_generated_final.append(item)

    if getattr(so, "init_storage", None):
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
