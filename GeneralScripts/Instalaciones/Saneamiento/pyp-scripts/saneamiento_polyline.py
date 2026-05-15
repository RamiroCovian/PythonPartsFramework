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
from Instalaciones.PolyLib.parameters import EventIds, ParamNames, PolyModeValues
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.attributes_utils import (
    _apply_absolute_numbering_attr01,
    _apply_attributes_to_model_elem,
    _get_attributes_from_model_elem,
    _merge_attributes,
    _normalize_attribute_list,
    attribute_debug_enabled,
    format_attributes_for_debug,
)
from .utils.geo_handler import PipelineProcessor
from .utils.layers_utils import _apply_layer_to_element, layer_debug_enabled
from .utils.te_orientation import (
    SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE,
    build_te_params,
)
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
# Volcado por tramo: ``.info`` / ``.data`` (hook de preview). Por defecto activo; ``=0`` para apagar.
_SANEAMIENTO_DEBUG_SEGMENT_INFO = str(
    os.getenv("SANEAMIENTO_DEBUG_SEGMENT_INFO", "1")
).strip().lower() in ("1", "true", "yes")
_SANEAMIENTO_DEBUG_SEGMENT_DATA = str(
    os.getenv("SANEAMIENTO_DEBUG_SEGMENT_DATA", "1")
).strip().lower() in ("1", "true", "yes")
_SANEAMIENTO_PERF_DEBUG = str(
    os.getenv("SANEAMIENTO_PERF_DEBUG", "0")
).strip().lower() in ("1", "true", "yes")


def _saneamiento_layer_trace() -> bool:
    """Rastro detallado de capas: ``SANEAMIENTO_LAYER_DEBUG`` o ``SANEAMIENTO_DEBUG_HOOKS``."""
    return layer_debug_enabled() or _SANEAMIENTO_DEBUG_HOOKS


def _saneamiento_attr_trace() -> bool:
    """Rastro de atributos palette→modelo: ``SANEAMIENTO_ATTR_DEBUG`` o ``SANEAMIENTO_DEBUG_HOOKS``."""
    return attribute_debug_enabled() or _SANEAMIENTO_DEBUG_HOOKS


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
        "utils.layers_utils",
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


def _apply_saneamiento_angle_steps_for_snap(so) -> None:
    """
    Tras `resolve_installation_config`, PolyLib asigna `angle_steps` desde el registry
    (`ANGLES_45`: 0…315 cada 45°). En `PolyLib.interactor.snap_point_with_angle` esos
    valores son **deltas relativos** al segmento anterior (`prev_ang + rel`), así que
    incluir 135° / 180° / 225° permite giros que generan vértices con ángulo interior
    agudo (~45° «cerrado») para los que el pipeline no está preparado.

    Se fuerza `angle_steps` desde `CONFIG.allowed_angles` (solo 0/±45/±90) cuando
    `limit_angles` está activo. No se modifica `allowed_angles`: la validación final
    sigue aceptando rumbos absolutos 0…315 en pasos de 45°.
    """
    cfg = getattr(so, "_config", None)
    if cfg is None or not getattr(cfg, "limit_angles", False):
        return
    steps = getattr(cfg, "allowed_angles", None)
    if not steps:
        return
    so.angle_steps = list(steps)


def _patch_resolve_installation_config_sync_diameter(so):
    """
    PolyLib actualiza `so.diameter_type` al cambiar InstallationType pero no siempre
    escribe el mismo valor en `build_ele.DiameterType`, de modo que la paleta puede
    seguir mostrando p. ej. 110 mm mientras la lógica usa el primer diámetro del
    nuevo tipo (25 mm en Fecal). Sin tocar PolyLib: envolvemos resolve_installation_config.
    También se re-aplican los pasos de snap de ángulo (ver `_apply_saneamiento_angle_steps_for_snap`).
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
        _apply_saneamiento_angle_steps_for_snap(so)
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

    _poly_dbg = ""
    try:
        if intr is not None and callable(getattr(intr, "_current_poly_mode", None)):
            pm = intr._current_poly_mode()
            _poly_dbg = str(pm)
            _uses_auto = pm == PolyModeValues.Automatico
        else:
            _uses_auto = False
    except Exception as ex_poly:
        _poly_dbg = f"error:{type(ex_poly).__name__}:{ex_poly}"
        _uses_auto = False

    paths_manual = list(getattr(so, "saved_paths", []) or [])
    paths_auto = list(getattr(so, "saved_optimized_paths", []) or [])

    print(
        "[SANEAMIENTO][INVERTIR][DBG] clic recibido | "
        f"poly_mode={_poly_dbg!r} usa_active_saved_optimized_paths={_uses_auto} "
        f"n_manual_paths={len(paths_manual)} n_saved_optimized_paths={len(paths_auto)}"
    )

    # Si hay una polilínea activa en creación, guardarla para incluirla en la inversión.
    try:
        if intr and getattr(intr, "create_mode", False) and len(getattr(intr, "points", []) or []) >= 2:
            save_fn = getattr(intr, "_save_current_polyline", None)
            if callable(save_fn):
                save_fn()
            paths_manual = list(getattr(so, "saved_paths", []) or [])
            paths_auto = list(getattr(so, "saved_optimized_paths", []) or [])
            print(
                "[SANEAMIENTO][INVERTIR][DBG] después de guardar polilínea activa | "
                f"n_manual_paths={len(paths_manual)} n_auto_paths={len(paths_auto)}"
            )
    except Exception as ex:
        print(f"[SANEAMIENTO][INVERTIR] No se pudo guardar polilínea activa: {ex}")

    if not paths_manual and not paths_auto:
        print("[SANEAMIENTO][INVERTIR][DBG] aborto: manual y saved_optimized_paths vacíos")
        PythonUtility.ShowMessageBox(
            "No hay instalación guardada para invertir.",
            PythonUtility.MB_OK,
        )
        return True

    seg_count_by_path: dict[int, int] = {}
    for idx, path in enumerate(paths_manual):
        seg_count_by_path[idx] = max(len(path) - 1, 0)
    offset = len(paths_manual)
    for j, path in enumerate(paths_auto):
        seg_count_by_path[offset + j] = max(len(path) - 1, 0)

    # 1) Invertir direccionalidad de puntos (manual + óptimos, mismos índices que persistent_metadata).
    so.saved_paths = [list(reversed(p)) for p in paths_manual]
    so.saved_optimized_paths = [list(reversed(p)) for p in paths_auto]
    print(
        "[SANEAMIENTO][INVERTIR][DBG] rutas invertidas | "
        f"seg_counts_por_path_idx={seg_count_by_path!r}"
    )

    if SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE:
        try:
            so._saneamiento_te_flip_suppress_signature = _paths_signature_te_flip(so)
        except Exception:
            so._saneamiento_te_flip_suppress_signature = None

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
            intr.selected_segments = set()
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
# Auto-inversión en TE (rama obligatoria si is_start; troncal si branch_along_main<0)
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
    """Proxy de segmento con dirección invertida (start↔end) para auto-inversión de sentido."""
    def __init__(self, seg):
        self._seg = seg
        self.data = _FlippedSegData(seg.data)
        self.info = getattr(seg, "info", None)
        self.name = getattr(seg, "name", "")

    def __getattr__(self, name):
        return getattr(self._seg, name)


def _conn_nominal_diameter(segment_groups: list, conn: dict) -> float:
    try:
        seg = segment_groups[conn["path_idx"]][conn["seg_idx"]]
        d = getattr(getattr(seg, "info", None), "diameter", None)
        if d is None:
            return 0.0
        return float(d)
    except Exception:
        return 0.0


def _paths_signature_te_flip(so) -> tuple:
    """Firma de vértices guardados (por path) para detectar edición geométrica real."""

    def _pack(paths):
        rows: list[tuple[tuple[float, float, float], ...]] = []
        for path in paths or []:
            pts = []
            for p in path:
                try:
                    pts.append((float(p.X), float(p.Y), float(p.Z)))
                except Exception:
                    pts.append((0.0, 0.0, 0.0))
            rows.append(tuple(pts))
        return tuple(rows)

    manual = getattr(so, "saved_paths", []) or []
    auto = getattr(so, "saved_optimized_paths", []) or []
    return (_pack(manual), _pack(auto))


def _sig_paths_is_nested_per_path(paths_pack) -> bool:
    """True = firma nueva (tupla de paths); False = antigua plana de triples concatenados."""
    if not paths_pack:
        return True
    first = paths_pack[0]
    if not isinstance(first, tuple) or len(first) == 0:
        return True
    el0 = first[0]
    return isinstance(el0, tuple)


def _paths_te_flip_signatures_equivalent(
    cur: tuple,
    tgt: tuple,
    atol_mm: float = 2.0,
) -> bool:
    """Igualdad salvo tolerancia numérica entre firmas ``_paths_signature_te_flip``."""

    def _paths_close(pa: tuple, pb: tuple) -> bool:
        if len(pa) != len(pb):
            return False
        for path_a, path_b in zip(pa, pb):
            if len(path_a) != len(path_b):
                return False
            for xyz_a, xyz_b in zip(path_a, path_b):
                if (
                    abs(xyz_a[0] - xyz_b[0]) > atol_mm
                    or abs(xyz_a[1] - xyz_b[1]) > atol_mm
                    or abs(xyz_a[2] - xyz_b[2]) > atol_mm
                ):
                    return False
        return True

    if cur is None or tgt is None or len(cur) != 2 or len(tgt) != 2:
        return False

    cm, ca = cur
    tm, ta = tgt

    # Firmas legacy (lista plana de puntos): comparación exacta por compatibilidad.
    if not _sig_paths_is_nested_per_path(tm):
        return cur == tgt

    return _paths_close(cm, tm) and _paths_close(ca, ta)


def _te_flip_suppress_after_invert_active(so) -> bool:
    """
    True si debe omitirse la auto-inversión TE simétrica con ``along > 0`` porque el usuario acaba de
    usar «Invertir cabal» y la geometría (puntos guardados) no ha cambiado desde entonces.
    """
    if so is None:
        return False
    if not SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE:
        try:
            so._saneamiento_te_flip_suppress_signature = None
        except Exception:
            pass
        return False
    tgt = getattr(so, "_saneamiento_te_flip_suppress_signature", None)
    if tgt is None:
        return False
    cur = _paths_signature_te_flip(so)
    if not _paths_te_flip_signatures_equivalent(cur, tgt):
        try:
            so._saneamiento_te_flip_suppress_signature = None
        except Exception:
            pass
        return False
    return True


def _compute_branch_invert_paths(
    vertex_map: dict,
    te_vertices: set,
    segment_groups: list,
    script_object=None,
) -> set[int]:
    """
    Determina paths a invertir (proxy ``_FlippedSeg``) en un TE para alinear caudales.

    Rama en divergencia clásica: ``is_start`` en la conexión → invertir ese path.

    El troncal (par colineal) sólo cuando el acoplamiento axial es “contrario”:
    ``is_start`` y ``branch_along_main < 0`` (misma ``base_main`` que vertex_utils / TE).

    Caso simétrico tras «invertir cabal»:
    - ``is_start=False`` y ``branch_along_main > 0`` → igual que start+along<0 (rama+troncal si aplica).
    - ``is_start=False`` y ``branch_along_main < 0`` → igual que start+along>0 (sólo path de la rama).

    |along|≈0 en rama desde start: sólo invertir la rama, no el troncal.

    Si ``SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE`` es True y la TE tiene troncal simétrico:

    - ``branch_along_main < 0`` («caval sin sentido» geométrico): no se invierten paths; mirrors TE en
      ``build_te_params`` alinean la pieza.
    - ``branch_along_main > 0``: sí se aplica la auto-inversión salvo que siga activa la supresión
      tras «Invertir cabal» (firma de puntos igual a la guardada en el clic — ver
      ``_paths_signature_te_flip``).

    ``script_object`` debe ser el PolylineScriptObject del saneamiento cuando exista.
    """
    paths_to_flip: set[int] = set()
    suppress_flip_after_invert = _te_flip_suppress_after_invert_active(script_object)

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
        dot_main, i_ma, i_mb, k_br = min(candidates, key=lambda x: x[0])
        if dot_main > -0.5:
            continue

        branch_conn = conns[k_br]
        main_pa = conns[i_ma]["path_idx"]
        main_pb = conns[i_mb]["path_idx"]
        v_main_a = dirs[i_ma]
        v_main_b = dirs[i_mb]
        v_branch = dirs[k_br]

        base_main = v_main_a
        # Igual que register_te_cuts_into (vertex_utils) / TE orientación.
        if _dot(v_main_a, v_main_b) > 0.0:
            base_main = (-base_main[0], -base_main[1], -base_main[2])
        branch_along_main = _dot(v_branch, base_main)

        _along_eps = 1e-6
        if SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE:
            d_ma = _conn_nominal_diameter(segment_groups, conns[i_ma])
            d_mb = _conn_nominal_diameter(segment_groups, conns[i_mb])
            v_ma = dirs[i_ma]
            v_mb = dirs[i_mb]
            dot_ma = _dot(v_ma, base_main)
            dot_mb = _dot(v_mb, base_main)
            if dot_ma > dot_mb:
                di_in_r = int(round(d_ma))
                di_out_r = int(round(d_mb))
            else:
                di_in_r = int(round(d_mb))
                di_out_r = int(round(d_ma))
            if di_in_r > 0 and di_in_r == di_out_r:
                if branch_along_main < -_along_eps:
                    continue
                if branch_along_main > _along_eps and suppress_flip_after_invert:
                    continue

        is_branch_start = branch_conn.get("is_start", True)

        def _add_mains_flip():
            if main_pa == main_pb:
                paths_to_flip.add(main_pa)
            else:
                paths_to_flip.add(main_pa)
                paths_to_flip.add(main_pb)

        if is_branch_start:
            paths_to_flip.add(branch_conn["path_idx"])
            if branch_along_main < -_along_eps:
                _add_mains_flip()
        elif branch_along_main > _along_eps:
            paths_to_flip.add(branch_conn["path_idx"])
            _add_mains_flip()
        elif branch_along_main < -_along_eps:
            # Post «invertir cabal»: rama en end con along<0 (espejo de start+along>0).
            paths_to_flip.add(branch_conn["path_idx"])

    return paths_to_flip


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
            print(
                "[SANEAMIENTO][INVERTIR][DBG] EventIds.INVERTIR_CAVAL → "
                f"_invertir_caval_saneamiento (id={event_id})"
            )
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
        if event_id == EventIds.ATTRIBUTE_APPLY and _saneamiento_attr_trace():
            out = original_on_control_event(event_id)
            try:
                _saneamiento_trace_attribute_apply_after_button(script_object)
            except Exception as ex:
                print(f"[SANEAMIENTO][ATTRDBG] post-apply trace: {ex}")
            return out
        return original_on_control_event(event_id)

    script_object.on_control_event = _on_control_event_saneamiento

    # Diagnóstico: algunos clicks pueden llegar sólo por modify_element_property.
    _orig_modify_element_property = getattr(
        script_object, "modify_element_property", None
    )
    if callable(_orig_modify_element_property):

        def _wrapped_modify_element_property(name, value):
            nm = str(name)
            if nm in (
                ParamNames.Actions.INVERTIR_CAVAL,
                "invertirCaval",
            ):
                print(
                    "[SANEAMIENTO][INVERTIR][DBG] modify_element_property "
                    f"name={nm!r} value={value!r}"
                )
            return _orig_modify_element_property(name, value)

        script_object.modify_element_property = _wrapped_modify_element_property

    return script_object


def _saneamiento_debug_segment_info_line(seg, idx: int) -> str:
    inf = getattr(seg, "info", None)
    nm = getattr(seg, "name", "")
    if inf is None:
        return f"[SANEAMIENTO][SEGINFO][{idx}] name={nm!r} info=None"
    chunks: list[str] = [f"name={nm!r}"]
    for attr in (
        "diameter",
        "diameter_in",
        "diameter_out",
        "distribution_type",
        "installation",
        "system",
    ):
        if hasattr(inf, attr):
            try:
                chunks.append(f"{attr}={getattr(inf, attr)!r}")
            except Exception:
                chunks.append(f"{attr}=<?>")
    return f"[SANEAMIENTO][SEGINFO][{idx}] " + " ".join(chunks)


def _saneamiento_debug_segment_data_line(seg, idx: int) -> str:
    d = getattr(seg, "data", None)
    nm = getattr(seg, "name", "")
    if d is None:
        return f"[SANEAMIENTO][SEGDATA][{idx}] name={nm!r} data=None"

    def _p(pt, label: str) -> str:
        if pt is None:
            return f"{label}=None"
        try:
            return f"{label}=({float(pt.X):.3f},{float(pt.Y):.3f},{float(pt.Z):.3f})"
        except Exception:
            return f"{label}=<?>"

    parts = [
        _p(getattr(d, "start", None), "start"),
        _p(getattr(d, "end", None), "end"),
    ]
    for attr in (
        "angulo_xy",
        "angulo_z",
        "angulo_rotacion",
        "longitud_3d",
        "longitud_xy",
        "view_mode",
    ):
        if hasattr(d, attr):
            try:
                parts.append(f"{attr}={getattr(d, attr)!r}")
            except Exception:
                parts.append(f"{attr}=<?>")
    v = getattr(d, "vector_normalizado", None)
    if v is not None:
        try:
            parts.append(f"v=({float(v.X):.4f},{float(v.Y):.4f},{float(v.Z):.4f})")
        except Exception:
            parts.append("v=<?>")
    return f"[SANEAMIENTO][SEGDATA][{idx}] name={nm!r} " + " ".join(parts)


def _saneamiento_debug_dump_segments_info_data(segments) -> None:
    if not (_SANEAMIENTO_DEBUG_SEGMENT_INFO or _SANEAMIENTO_DEBUG_SEGMENT_DATA):
        return
    if not segments:
        print("[SANEAMIENTO][SEG] (grupo de segmentos vacío)")
        return
    try:
        print(f"[SANEAMIENTO][SEG] --- {len(segments)} segmento(s) ---")
        for i, seg in enumerate(segments):
            if _SANEAMIENTO_DEBUG_SEGMENT_INFO:
                print(_saneamiento_debug_segment_info_line(seg, i))
            if _SANEAMIENTO_DEBUG_SEGMENT_DATA:
                print(_saneamiento_debug_segment_data_line(seg, i))
    except Exception as ex:
        print(f"[SANEAMIENTO][SEG] error volcando segmentos: {ex}")


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
    _saneamiento_debug_dump_segments_info_data(segments)
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
            processor.requested_diameter = diam
            processor.reference_orientation_angle = getattr(
                so, "reference_orientation_angle", None
            )
            # Reconstruir split_segment_groups desde los paths guardados.
            # La nueva PolyLib usa _build_segment_groups_for_paths en _create_elements_preview
            # (objetos nuevos), mientras so.segment_groups usa filter_and_group_segments
            # (objetos distintos). La comparación 'sg is segments' siempre falla → path_idx=0.
            # Fix: comparar por coordenadas de todos los segmentos del camino.
            _intr = getattr(so, "script_object_interactor", None)
            _rebuild_fn = getattr(_intr, "build_segments_for_paths", None) if _intr else None
            if callable(_rebuild_fn):
                _manual = list(getattr(so, "saved_paths", []) or [])
                _auto = list(getattr(so, "saved_optimized_paths", []) or [])
                split_segment_groups = _rebuild_fn(_manual)
                if _auto:
                    split_segment_groups = split_segment_groups + _rebuild_fn(_auto)
            else:
                split_segment_groups = list(so.segment_groups)

            path_idx = next(
                (i for i, sg in enumerate(split_segment_groups) if sg is segments),
                None,
            )
            if path_idx is None:
                def _path_coords_match(sg, segs):
                    if len(sg) != len(segs):
                        return False
                    try:
                        for _a, _b in zip(sg, segs):
                            _da, _db = _a.data, _b.data
                            if (abs(_da.start.X - _db.start.X) > 0.1 or
                                    abs(_da.start.Y - _db.start.Y) > 0.1 or
                                    abs(_da.start.Z - _db.start.Z) > 0.1 or
                                    abs(_da.end.X - _db.end.X) > 0.1 or
                                    abs(_da.end.Y - _db.end.Y) > 0.1 or
                                    abs(_da.end.Z - _db.end.Z) > 0.1):
                                return False
                    except Exception:
                        return False
                    return True
                path_idx = next(
                    (i for i, sg in enumerate(split_segment_groups)
                     if _path_coords_match(sg, segments)),
                    0,
                )

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

            if not processor.resolve_elbow_diameter_conflicts(segments):
                print(
                    "[SANEAMIENTO][ELBOW][DIAM] Preview/creacion omitida: "
                    "el usuario cancelo la correccion de diametro en codo."
                )
                return []

            def _diam_from_segment_item(seg_item, default=25):
                try:
                    info = getattr(seg_item, "info", None)
                    diam = getattr(info, "diameter", None) if info is not None else None
                    if isinstance(diam, (list, tuple)) and diam:
                        diam = diam[0]
                    if diam is None:
                        return int(default)
                    return int(round(float(diam)))
                except Exception:
                    return int(default)

            def _first_elbow_diameter_after_resolution():
                try:
                    for elbow_idx in range(1, len(segments)):
                        seg_prev_item = segments[elbow_idx - 1]
                        seg_next_item = segments[elbow_idx]
                        p_prev = getattr(getattr(seg_prev_item, "data", None), "start", None)
                        p_curr = getattr(getattr(seg_prev_item, "data", None), "end", None)
                        p_next = getattr(getattr(seg_next_item, "data", None), "end", None)
                        if processor._is_elbow_turn_for_diameter_conflict(
                            p_prev, p_curr, p_next
                        ):
                            return _diam_from_segment_item(seg_prev_item, diam or 25)
                except Exception as ex:
                    print(
                        "[SANEAMIENTO][ELBOW][DIAM] No se pudo inferir "
                        f"diametro de codo: {ex}"
                    )
                return None

            def _set_build_ele_diameter(diam_mm):
                build_ele = getattr(so, "build_ele", None)
                if build_ele is None or diam_mm is None:
                    return
                for attr_name in ("DiameterType", "DiametroAplicar"):
                    try:
                        attr = getattr(build_ele, attr_name, None)
                        if attr is not None and hasattr(attr, "value"):
                            attr.value = int(diam_mm)
                        else:
                            setattr(build_ele, attr_name, int(diam_mm))
                    except Exception:
                        continue

            def _refresh_elbow_templates(diam_mm):
                if diam_mm is None:
                    return
                if element_type_core == "tub_pvc_tricapa":
                    keys = FECAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam_mm))
                else:
                    keys = PLUVIAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam_mm))
                if not keys:
                    print(
                        f"[SANEAMIENTO][ELBOW][DIAM] Sin codos registrados "
                        f"para diametro {diam_mm}mm"
                    )
                    return

                _set_build_ele_diameter(diam_mm)
                c45_key, c90_key = keys
                c45_kwargs = (
                    {}
                    if c45_key in ("codo_45_110", "codo_45_110_p")
                    else {"TipoSaneamiento": 0}
                )
                c90_kwargs = (
                    {}
                    if c90_key in ("codo_90_40", "codo_90_110", "codo_90_110_p")
                    else {"TipoSaneamiento": 1}
                )
                refreshed_c45 = so._get_pythonpart_installed(
                    element_key=c45_key,
                    exec_kwargs=c45_kwargs,
                    attr_kwargs=c45_kwargs,
                )
                refreshed_c90 = so._get_pythonpart_installed(
                    element_key=c90_key,
                    exec_kwargs=c90_kwargs,
                    attr_kwargs=c90_kwargs,
                )

                def _replace_templates(prefix, models):
                    keys_to_clear = [prefix, f"{prefix}_inner", f"{prefix}_inner_2"]
                    for key in keys_to_clear:
                        if key in processor.templates:
                            del processor.templates[key]
                    if not models:
                        return
                    processor.templates[prefix] = models[0]
                    if len(models) > 1:
                        processor.templates[f"{prefix}_inner"] = models[1]
                    if len(models) > 2:
                        processor.templates[f"{prefix}_inner_2"] = models[2]

                _replace_templates("codo_45", refreshed_c45)
                _replace_templates("codo_90", refreshed_c90)
                print(
                    f"[SANEAMIENTO][ELBOW][DIAM] templates de codo refrescados "
                    f"con diametro {diam_mm}mm"
                )

            elbow_diam = _first_elbow_diameter_after_resolution()
            _refresh_elbow_templates(elbow_diam)

            all_cuts = compute_segment_cuts_for_all_paths(
                split_segment_groups,
                skip_te_vertices=_te_skip_cuts,
            )
            segment_cuts = {
                seg_idx: all_cuts.get((path_idx, seg_idx), {"start": 0.0, "end": 0.0})
                for seg_idx in range(len(segments))
            }

            # is_start en la rama: invertir rama siempre; invertir además el troncal
            # sólo cuando branch_along_main < 0 (misma lógica que orientación/recortes TE).
            if te_vertices:
                paths_te_flow_fix = _compute_branch_invert_paths(
                    vertex_map, te_vertices, split_segment_groups, so
                )
                if path_idx in paths_te_flow_fix:
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
                        f"[SANEAMIENTO][TE-ALINEACION-CAUDAL] path={path_idx} "
                        f"n_segs={n} auto-invertido (TE divergencia; troncal solo si along<0)"
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


def _saneamiento_find_applied_layer_key_for_tube(
    so: PBL.script_object.PolylineScriptObject, path_idx: int, tube_segment_idx: int
) -> str | None:
    """
    PolyLib guarda ``AppliedLayer`` con ``storage_key = seg_{path}_elem_{layer_idx}``, donde
    ``layer_idx`` suele ser el índice del pipeline en el click, no el ordinal del tubo.
    El dict persistido incluye ``elem_idx`` (tramo de tubo 0..n-1) y ``type``='tubo'.
    Resolver por esos campos evita colisiones (p. ej. 3.er tubo vs clave del 2.º) y que
    los codos usen la entrada de capa de un tubo por igualdad de string de clave.
    """
    al = getattr(so, "applied_layers", {}) or {}
    for key, data in al.items():
        if not isinstance(data, dict):
            continue
        if str(data.get("type", "")).lower() != "tubo":
            continue
        try:
            if int(data.get("path_idx", -1)) != int(path_idx):
                continue
        except (TypeError, ValueError):
            continue
        try:
            if int(data.get("elem_idx", -999)) == int(tube_segment_idx):
                return str(key)
        except (TypeError, ValueError):
            continue
    return None


def _saneamiento_find_applied_layer_key_for_codo(
    so: PBL.script_object.PolylineScriptObject, path_idx: int, polylib_codo_vertex_idx: int
) -> str | None:
    """
    Igual que los tubos: PolyLib guarda el layer del codo en ``seg_{path}_elem_{layer_idx}``,
    pero el dict lleva ``elem_idx`` = índice lógico del vértice/codo en el path (p. ej. 1..4
    al marcar 4 codos) y ``type``='codo'. Los dos modelos ``codo_45`` del mismo vértice tienen
    ``pipe_idx`` distintos (10 y 11) y ninguno coincide con la clave guardada (p. ej. 5).
    """
    al = getattr(so, "applied_layers", {}) or {}
    for key, data in al.items():
        if not isinstance(data, dict):
            continue
        if str(data.get("type", "")).lower() != "codo":
            continue
        try:
            if int(data.get("path_idx", -1)) != int(path_idx):
                continue
        except (TypeError, ValueError):
            continue
        try:
            if int(data.get("elem_idx", -999)) == int(polylib_codo_vertex_idx):
                return str(key)
        except (TypeError, ValueError):
            continue
    return None


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


def _is_saneamiento_palette_secondary_geometry(element_type: str | None) -> bool:
    """
    Geometría gemela del mismo PythonPart (copias BRep ``*_copy_*``, tubo ``*_inner``,
    inner de codos/manguitos/TE, etc.). La capa asignada en paleta debe afectar sólo al
    cuerpo principal del modelo; las copias conservan capa/color definidos por el script.
    """
    if not element_type:
        return False
    low = str(element_type).lower()
    if low.endswith("_inner"):
        return True
    if "_copy_" in low:
        return True
    return False


def _saneamiento_skip_palette_secondary_geometry_key(
    storage_key: str, element_type: str | None
) -> str:
    """Clave fuera de ``applied_layers`` para no sustituir capa en copias/inner."""
    et = re.sub(r"[^a-zA-Z0-9_]+", "_", str(element_type or "geom"))[:80]
    return f"{storage_key}__saneamiento_palette_original_only__{et}__"


def _saneamiento_skip_tubo_palette_storage_key(pipeline_storage_key: str) -> str:
    """
    Clave que no existe en ``applied_layers``. Así ``_apply_layer_to_element`` no fuerza
    la capa de un tubo sobre codos/accesorios cuando ``seg_*_elem_*`` es el mismo string
    pero la fila de paleta es sólo válida para tubo.
    """
    return f"{pipeline_storage_key}__saneamiento_skip_tubo_palette__"


def _saneamiento_tubo_elem_mismatch_palette_key(
    pipeline_storage_key: str, tube_segment_idx: int
) -> str:
    """
    Misma cadena ``seg_*_elem_*`` puede ser el ``storage_key`` de un tubo en pipeline y
    también la clave PolyLib de **otro** tubo (``layer_idx`` del click = índice pipeline
    del punto clickado). Si ``applied_layers[pipeline_storage_key]`` es ``type=tubo`` con
    ``elem_idx`` distinto de ``tube_segment_idx``, no aplicar esa capa aquí.
    """
    return f"{pipeline_storage_key}__saneamiento_tubo_elem_mismatch_{tube_segment_idx}__"


def _saneamiento_skip_codo_elem_mismatch_storage_key(
    pipeline_storage_key: str, codo_path_vertex_idx: int
) -> str:
    """Clave inexistente en ``applied_layers`` cuando un vecino sería capa de **otro** vértice (`elem_idx`)."""
    return f"{pipeline_storage_key}__saneamiento_skip_codo_elem_{codo_path_vertex_idx}__"


def _resolve_assignment_key(
    so: PBL.script_object.PolylineScriptObject,
    default_key: str,
    candidate_keys: list[str] | None = None,
    *,
    reject_applied_layer_types: frozenset[str] | None = None,
    require_applied_codo_elem_idx: int | None = None,
) -> str:
    """
    Igual que en Agua: cuando el índice final difiere del de selección UI,
    usar la primera clave existente en ``applied_layers`` para **capas**.

    (No se considera ``applied_attributes`` aquí: una misma clave puede tener sólo
    atributos de paleta y entrar en colisión numérica con el ``pipe_idx`` de un codo;
    mezclar ambos mapas devolvía la clave del tubo y forzaba capa ``type=tubo`` en codos.)

    ``reject_applied_layer_types``: no considerar entradas de ``applied_layers`` cuyo
    ``type`` coincida (p. ej. excluir entradas de tubo al resolver codos con la misma
    clave numérica ``seg_*_elem_*``).

    ``require_applied_codo_elem_idx``: si se informa, ignorar filas ``type=codo`` cuyo
    ``elem_idx`` no coincida (evita que vecinos ±k apliquen la capa de otro vértice).
    """
    reject_lc = None
    if reject_applied_layer_types:
        reject_lc = frozenset(x.lower() for x in reject_applied_layer_types)

    applied_layers = getattr(so, "applied_layers", {}) or {}
    keys_to_try = [default_key] + [k for k in (candidate_keys or []) if k]
    seen = set()
    for key in keys_to_try:
        if key in seen:
            continue
        seen.add(key)
        if key in applied_layers:
            ent = applied_layers[key]
            if reject_lc and isinstance(ent, dict):
                t = str(ent.get("type", "")).lower()
                if t in reject_lc:
                    continue
            if require_applied_codo_elem_idx is not None and isinstance(ent, dict):
                if str(ent.get("type", "")).lower() == "codo":
                    try:
                        if int(ent.get("elem_idx", -999)) != int(require_applied_codo_elem_idx):
                            continue
                    except (TypeError, ValueError):
                        continue
            return key
    if (
        reject_lc
        and default_key in applied_layers
    ):
        ent = applied_layers[default_key]
        if isinstance(ent, dict) and str(ent.get("type", "")).lower() in reject_lc:
            return _saneamiento_skip_tubo_palette_storage_key(default_key)
    if require_applied_codo_elem_idx is not None and default_key in applied_layers:
        ent = applied_layers[default_key]
        if isinstance(ent, dict) and str(ent.get("type", "")).lower() == "codo":
            try:
                if int(ent.get("elem_idx", -999)) != int(require_applied_codo_elem_idx):
                    return _saneamiento_skip_codo_elem_mismatch_storage_key(
                        default_key, require_applied_codo_elem_idx
                    )
            except (TypeError, ValueError):
                pass
    return default_key


# Codos/accesorios no deben reutilizar filas de paleta guardadas como tubo (misma clave).
_REJECT_TUBE_LAYER_ENTRY_FOR_NON_TUBE: frozenset[str] = frozenset({"tubo"})


def _saneamiento_polylib_preview_storage_key(
    so: PBL.script_object.PolylineScriptObject,
    path_idx: int,
    *,
    element_type: str | None,
    tube_segment_idx: int,
    codo_path_vertex_idx: int,
) -> str | None:
    """
    Clave ``seg_{path}_elem_{final_idx}`` que usa PolyLib al guardar paleta, distinta del
    ``pipe_idx`` del pipeline Saneamiento. Se obtiene de ``generated_elements`` (``key[3]``).
    """
    inter = getattr(so, "script_object_interactor", None)
    if inter is None:
        return None
    groups = getattr(inter, "generated_elements", None) or []
    if not (0 <= path_idx < len(groups)):
        return None
    group = groups[path_idx]
    if not group:
        return None
    et = str(element_type or "")

    if et in ("tubo_saneamiento", "tubo_saneamiento_flecha"):
        want_seg = int(tube_segment_idx)
        for el in group:
            if str(el.get("type", "")) != "tubo":
                continue
            try:
                if int(el.get("seg_idx", -999)) != want_seg:
                    continue
            except (TypeError, ValueError):
                continue
            key = el.get("key")
            if isinstance(key, (list, tuple)) and len(key) > 3:
                try:
                    return f"seg_{path_idx}_elem_{int(key[3])}"
                except (TypeError, ValueError):
                    return None
        return None

    if _is_saneamiento_elbow_element(element_type):
        want_v = int(codo_path_vertex_idx)
        for el in group:
            t = str(el.get("type", "")).lower()
            if t not in ("codo", "union"):
                continue
            try:
                if int(el.get("seg_idx", -999)) != want_v:
                    continue
            except (TypeError, ValueError):
                continue
            key = el.get("key")
            if isinstance(key, (list, tuple)) and len(key) > 3:
                try:
                    return f"seg_{path_idx}_elem_{int(key[3])}"
                except (TypeError, ValueError):
                    return None
        return None

    if _is_saneamiento_tube_attached(element_type):
        return _saneamiento_polylib_preview_storage_key(
            so,
            path_idx,
            element_type="tubo_saneamiento",
            tube_segment_idx=tube_segment_idx,
            codo_path_vertex_idx=codo_path_vertex_idx,
        )

    return None


def _saneamiento_resolve_applied_attributes_list(
    so: PBL.script_object.PolylineScriptObject,
    applied_attrs_map: dict,
    path_idx: int,
    layer_key: str,
    element_type: str | None,
    tube_segment_idx: int,
    codo_path_vertex_idx: int,
) -> tuple[list, str | None, str | None]:
    """
    Devuelve (lista normalizada, clave usada en ``applied_attributes``, clave preview PolyLib).

    PolyLib guarda atributos en ``seg_{path}_elem_{key[3]}`` (preview); el pipeline usa
    ``seg_{path}_elem_{pipe_idx}``. Se prueba primero la clave preview si existe.

    En **codos**, ``layer_key`` puede coincidir con el otro vértice 2×45° (resolución pensada
    para capas); los atributos no deben tomarse de ahí. Tampoco ``pipeline_storage_key``:
    el 2.º sólido del primer 2×45 puede ser ``seg_0_elem_3``, igual que la clave PolyLib de
    otro vértice. Solo se usa ``poly_key`` (preview por ``seg_idx`` = vértice del path).
    """
    if _is_saneamiento_palette_secondary_geometry(element_type):
        return [], None, None

    pk = _saneamiento_polylib_preview_storage_key(
        so,
        path_idx,
        element_type=element_type,
        tube_segment_idx=tube_segment_idx,
        codo_path_vertex_idx=codo_path_vertex_idx,
    )
    if _is_saneamiento_elbow_element(element_type):
        if pk:
            raw = applied_attrs_map.get(pk)
            if raw:
                return _normalize_attribute_list(raw), pk, pk
        return [], None, pk

    for k in (pk, layer_key):
        if not k:
            continue
        raw = applied_attrs_map.get(k)
        if raw:
            return _normalize_attribute_list(raw), k, pk
    return [], None, pk


def _saneamiento_trace_attribute_apply_after_button(
    so: PBL.script_object.PolylineScriptObject,
) -> None:
    """
    Tras ``EventIds.ATTRIBUTE_APPLY`` (PolyLib ``apply_attributes_input``): estado
    de ``applied_attributes`` y selección. No modifica PolyLib.
    """
    if not _saneamiento_attr_trace():
        return
    val_s: object | None = None
    try:
        be = getattr(so, "build_ele", None)
        if be is not None:
            p = getattr(be, ParamNames.Attributes.VALUE, None)
            if p is not None:
                val_s = getattr(p, "value", None)
    except Exception:
        val_s = None

    inter = getattr(so, "script_object_interactor", None)
    sel_n = 0
    sel_one: object | None = None
    try:
        segs = getattr(inter, "selected_segments", None) or ()
        sel_n = len(segs)
        sel_one = getattr(inter, "selected_element_id", None)
    except Exception:
        pass

    aa = getattr(so, "applied_attributes", {}) or {}
    keys = sorted(aa.keys())
    print(
        f"[SANEAMIENTO][ATTRDBG] ATTRIBUTE_APPLY post handler "
        f"palette_value={val_s!r} selected_segments_n={sel_n} "
        f"selected_element_id={sel_one!r} applied_attributes_keys={len(keys)}"
    )
    tail = keys[-25:] if len(keys) > 25 else keys
    if len(keys) > 25:
        print(
            f"[SANEAMIENTO][ATTRDBG] …mostrando últimas {len(tail)} de {len(keys)} claves"
        )
    for k in tail:
        try:
            print(
                f"[SANEAMIENTO][ATTRDBG]   {k!r} -> "
                f"{format_attributes_for_debug(aa.get(k), max_attrs=10)}"
            )
        except Exception:
            print(f"[SANEAMIENTO][ATTRDBG]   {k!r} -> <?>")


def _create_elements_with_layers_attrs(
    elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject
) -> list:
    """
    Aplica capas + atributos de paleta y numeración absoluta ATTR01 en tubos (`tubo_saneamiento`).
    Capas: PolyLib `applied_layers`, claves `seg_{path}_elem_{layer_idx}`.

    El interactor PolyLib guarda ``seg_{path}_elem_{layer_idx}`` (índice de click); la capa
    de tubo se asocia por ``elem_idx`` en el payload vía
    ``_saneamiento_find_applied_layer_key_for_tube``. Sin vecinos en el fallback de tubo
    (evita tomar ``seg_*_elem_{i±k}`` que es capa de otro tramo). Si ``storage_key``
    coincide con una entrada de paleta de **otro** tubo (mismo string, otro ``elem_idx``),
    usar clave sintética ``__saneamiento_tubo_elem_mismatch_*__``. Codos: ignoran entradas
    ``type=tubo`` y, si la clave por defecto sólo tenía tubo, usan sufijo
    ``__saneamiento_skip_tubo_palette__`` para no aplicar esa capa al codo.
    Vértice 2×45°: el primer ``codo_45`` usa ``_saneamiento_find_applied_layer_key_for_codo``
    con contador 1-based alineado con ``elem_idx`` en PolyLib; el segundo reutiliza la misma
    ``layer_key`` que el primero. El fallback con vecinos exige ``elem_idx`` coincidente
    (`require_applied_codo_elem_idx`) para no aplicar la capa de otro vértice.
    **Copias BRep / inner** (`*_copy_*`, tipos que terminan en ``_inner``): no reciben capa
    de paleta; conservan la del script.
    **Atributos:** PolyLib guarda ``applied_attributes`` con la misma convención que el
    preview (``seg_{path}_elem_{final_idx}`` de ``generated_elements``); el hook resuelve
    también esa clave vía ``_saneamiento_resolve_applied_attributes_list`` para coincidir
    con el ``pipe_idx`` del modelo. En codos no se usa ``layer_key`` para atributos (evita
    mezclar 2×45° de otro vértice ni el ``pipe_idx`` del 2.º codo del mismo vértice.
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

    applied_attrs_map = getattr(so, "applied_attributes", {}) or {}

    if _saneamiento_layer_trace():
        try:
            al = getattr(so, "applied_layers", {}) or {}
            print(
                f"[SANEAMIENTO][LAYERDBG] hook start path={path_idx} "
                f"elems={len(elements_generated or [])} applied_layer_keys={list(al.keys())} "
                f"default_layers={getattr(so, 'default_layers', None)}"
            )
        except Exception:
            pass
    if _saneamiento_attr_trace():
        try:
            print(
                f"[SANEAMIENTO][ATTRDBG] hook start path={path_idx} "
                f"elems={len(elements_generated or [])} "
                f"applied_attr_keys={sorted(applied_attrs_map.keys())!r}"
            )
        except Exception:
            pass
    elements_generated_final = []
    tube_segment_idx = -1
    codo_path_vertex_idx = 0
    last_tube_layer_key: str | None = None
    last_elbow_layer_key: str | None = None

    for seq_idx, item in enumerate(elements_generated or []):
        element_type = getattr(item, "element_type", None)
        model_elem = item.element
        idx = int(getattr(item, "index", 0))
        storage_key = f"seg_{path_idx}_elem_{idx}"

        if element_type == "tubo_saneamiento":
            tube_segment_idx += 1
            meta_key = _saneamiento_find_applied_layer_key_for_tube(
                so, path_idx, tube_segment_idx
            )
            if meta_key:
                layer_key = meta_key
            else:
                # Misma clave string: p. ej. 3.er tubo guarda seg_0_elem_4 (layer_idx) y el
                # 2.º tubo tiene pipe_idx=4 → sin comprobar elem_idx aplicaríamos la capa ajena.
                al = getattr(so, "applied_layers", {}) or {}
                ent = al.get(storage_key)
                if isinstance(ent, dict) and str(ent.get("type", "")).lower() == "tubo":
                    try:
                        pal_e = int(ent.get("elem_idx", -999))
                    except (TypeError, ValueError):
                        pal_e = -999
                    if pal_e != int(tube_segment_idx):
                        layer_key = _saneamiento_tubo_elem_mismatch_palette_key(
                            storage_key, tube_segment_idx
                        )
                    else:
                        layer_key = storage_key
                else:
                    layer_key = _resolve_assignment_key(so, storage_key, [])
            last_tube_layer_key = layer_key
            last_elbow_layer_key = None
        elif _is_saneamiento_tube_attached(element_type):
            base = last_tube_layer_key
            layer_key = _resolve_assignment_key(
                so,
                storage_key,
                [k for k in [base] if k],
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
                codo_path_vertex_idx += 1
                meta_codo = _saneamiento_find_applied_layer_key_for_codo(
                    so, path_idx, codo_path_vertex_idx
                )
                if meta_codo:
                    layer_key = meta_codo
                else:
                    layer_key = _resolve_assignment_key(
                        so,
                        storage_key,
                        _saneamiento_layer_key_candidates_for_index(path_idx, idx),
                        reject_applied_layer_types=_REJECT_TUBE_LAYER_ENTRY_FOR_NON_TUBE,
                        require_applied_codo_elem_idx=codo_path_vertex_idx,
                    )
                last_elbow_layer_key = layer_key
        else:
            layer_key = _resolve_assignment_key(
                so,
                storage_key,
                _saneamiento_layer_key_candidates_for_index(path_idx, idx),
                reject_applied_layer_types=_REJECT_TUBE_LAYER_ENTRY_FOR_NON_TUBE,
            )
            if element_type and element_type.endswith("_inner") and seq_idx - 1 >= 0:
                prev_item = elements_generated[seq_idx - 1]
                prev_idx = int(getattr(prev_item, "index", idx))
                layer_key = _resolve_assignment_key(
                    so,
                    layer_key,
                    [f"seg_{path_idx}_elem_{prev_idx}"],
                    reject_applied_layer_types=_REJECT_TUBE_LAYER_ENTRY_FOR_NON_TUBE,
                )
            last_elbow_layer_key = None

        if _is_saneamiento_palette_secondary_geometry(element_type):
            layer_key = _saneamiento_skip_palette_secondary_geometry_key(
                storage_key, element_type
            )

        if _saneamiento_layer_trace():
            try:
                pre_l = None
                try:
                    pre_l = getattr(model_elem.GetCommonProperties(), "Layer", None)
                except Exception:
                    pass
                al_map = getattr(so, "applied_layers", {}) or {}
                raw_ent = al_map.get(layer_key)
                print(
                    f"[SANEAMIENTO][LAYERDBG] path={path_idx} seq={seq_idx} "
                    f"etype={element_type!r} pipe_idx={idx} tube_seg_idx={tube_segment_idx} "
                    f"storage={storage_key!r} layer_key={layer_key!r} "
                    f"in_applied_layers={layer_key in al_map} palette_entry={raw_ent!r} "
                    f"pre_apply_Layer={pre_l}"
                )
            except Exception:
                pass

        try:
            model_elem = _apply_layer_to_element(model_elem, layer_key, so)
        except Exception as ex:
            print(f"[SANEAMIENTO][LAYER] No se pudo aplicar layer ({layer_key}): {ex}")
        else:
            if _saneamiento_layer_trace():
                try:
                    p = model_elem.GetCommonProperties()
                    print(
                        f"[SANEAMIENTO][LAYERDBG] path={path_idx} seq={seq_idx} etype={element_type!r} "
                        f"layer_key={layer_key!r} post_apply_Layer={getattr(p, 'Layer', None)} "
                        f"ColorByLayer={getattr(p, 'ColorByLayer', None)}"
                    )
                except Exception:
                    pass
        try:
            model_default_attrs = _get_attributes_from_model_elem(model_elem)
            custom_attrs, attr_palette_key, poly_attr_key = (
                _saneamiento_resolve_applied_attributes_list(
                    so,
                    applied_attrs_map,
                    path_idx,
                    layer_key,
                    element_type,
                    tube_segment_idx,
                    codo_path_vertex_idx,
                )
            )
            if _saneamiento_attr_trace():
                try:
                    md_n = len(_normalize_attribute_list(model_default_attrs))
                except Exception:
                    md_n = -1
                try:
                    print(
                        f"[SANEAMIENTO][ATTRDBG] path={path_idx} seq={seq_idx} "
                        f"etype={element_type!r} storage={storage_key!r} layer_key={layer_key!r} "
                        f"polylib_attr_key={poly_attr_key!r} attr_resolved_from={attr_palette_key!r} "
                        f"model_defaults_n={md_n} palette_n={len(custom_attrs)} "
                        f"palette={format_attributes_for_debug(custom_attrs, max_attrs=8)}"
                    )
                except Exception:
                    pass
            if custom_attrs:
                merged_attrs = _merge_attributes(model_default_attrs, custom_attrs)
                model_elem = _apply_attributes_to_model_elem(model_elem, merged_attrs)
                if _saneamiento_attr_trace():
                    try:
                        print(
                            f"[SANEAMIENTO][ATTRDBG] path={path_idx} seq={seq_idx} "
                            f"merged_n={len(merged_attrs)} "
                            f"merged_preview={format_attributes_for_debug(merged_attrs, max_attrs=8)}"
                        )
                    except Exception:
                        pass
        except Exception as ex:
            if _saneamiento_attr_trace() or _SANEAMIENTO_DEBUG_HOOKS:
                print(f"[SANEAMIENTO][ATTRDBG] No se pudo aplicar atributos ({layer_key}): {ex}")

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
