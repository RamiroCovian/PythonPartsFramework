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

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.installation_registry import register_pythonpart
from Instalaciones.PolyLib.models import Clima, ElementTypes
from Instalaciones.PolyLib.parameters import EventIds, ParamNames

from .utils import geo_handler as _geo_handler_mod
from .utils import placement_logic as _placement_logic_mod
from .utils import codo_placement_offsets as _codo_placement_offsets_mod
from .quiebro2 import Quiebro2Script
from .reduccions import ReduccionsScript
from NemAll_Python_BaseElements import LayerService


# ---------------- CUSTOM NUM_TD PATH ----------------
project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(project_name, host_name)
if error != 0:
    error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(project_name, "")

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Clima.profile()
profile.show.add_polilyne = True # BORRAR ESTA LINEA DE CODIGO ANTES DE ENTREGAR MVP
profile.enabled.add_polilyne = True # BORRAR ESTA LINEA DE CODIGO ANTES DE ENTREGAR MVP

# ---------------- DEFAULT CONFIG PARAMS ----------------
INST_NAME = "CLIMA"
# Botón «Aplicar reductor» en clima_polyline.pyp (no está en PolyLib EventIds).
APLICAR_REDUCTOR_CLIMA_EVENT = 1039
# Combo polilínea → tramo recto inicial/final del reductor (Impulsió/Ret en execute).
CLIMA_REDUCTOR_STRAIGHT_PALETTE_PARAM = "ClimaReservedOpt100200300"
CLIMA_REDUCTOR_STRAIGHT_MM_DEFAULT = 300.0
_CLIMA_REDUCTOR_STRAIGHT_ALLOWED_MM = frozenset({100.0, 200.0, 300.0})
# Color Allplan del cuerpo del último tramo en Impulsió.
IMPULSIO_LAST_SEGMENT_CONDUCTO_COLOR = 13
# Color de fábrica del cuerpo en tram_recte (PARAMS ``COLOR``); necesario para resetear
# por tramo cuando la factoría va con caché y se aplica color solo al primero/último.
CLIMA_TRAM_RECTE_BODY_COLOR_DEFAULT = 207
# Color Allplan del cuerpo del primer tramo en Retorn (recuperador).
RETORN_FIRST_SEGMENT_CONDUCTO_COLOR = 44
# Atributo TAPA en ese mismo primer cuerpo (alineado con ATTR_VALUES „Retorn Amb Tapa”).
RETORN_FIRST_SEGMENT_TAPA_VALUE = "TAPA RETORN"
# Valor del atributo de usuario TAPA en ese mismo cuerpo (documento debe definir el atributo "TAPA").
IMPULSIO_LAST_SEGMENT_TAPA_VALUE = "TAPA IMPULSIÓ"
# Variantes de nombre en catálogo Allplan (orden: primero "TAPA" en geo_handler, luego estas).
IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ALIASES = ("Tapa", "tapa")
# Si ningún nombre resuelve ID, asignar aquí el ID entero del atributo en este proyecto
# (catálogo de atributos). Allplan devuelve -1 si el nombre no existe en ese documento.
IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK = None


def _read_clima_reductor_straight_mm(build_ele) -> float:
    """Lee el combo 100/200/300 de la paleta polilínea Clima (valor por defecto 300)."""
    raw = getattr(build_ele, CLIMA_REDUCTOR_STRAIGHT_PALETTE_PARAM, None)
    val = getattr(raw, "value", raw) if raw is not None else None
    if val is None:
        return float(CLIMA_REDUCTOR_STRAIGHT_MM_DEFAULT)
    try:
        f = float(str(val).strip())
        if f in _CLIMA_REDUCTOR_STRAIGHT_ALLOWED_MM:
            return f
    except (TypeError, ValueError):
        pass
    return float(CLIMA_REDUCTOR_STRAIGHT_MM_DEFAULT)


def _attr_lookup_documents(so: Any) -> list:
    """
    Documentos a probar con AttributeService.GetAttributeID (sin asumir cuál enlaza el catálogo).
    """
    acc: list = []
    seen: set[int] = set()

    def _add(d) -> None:
        if d is None:
            return
        k = id(d)
        if k in seen:
            return
        seen.add(k)
        acc.append(d)

    _add(getattr(so, "doc", None))
    ci = getattr(so, "coord_input", None)
    if ci is not None:
        try:
            _add(ci.GetInputViewDocument())
        except Exception:
            pass
    try:
        from DocumentManager import DocumentManager

        inst = DocumentManager.get_instance()
        if inst is not None:
            _add(getattr(inst, "document", None))
    except Exception:
        pass
    return acc


def _build_allowed_relative_turns():
    """
    Giros relativos permitidos respecto al segmento anterior:
    -45° .. +45° (incluye 0°), resolución de 1°.
    Se conservan además giros rectos ±90° para poder trazar codos de 90°.
    """
    out = {float(a) for a in range(-45, 46)}
    out.update({-90.0, 90.0})
    return sorted(out)


ALLOWED_RELATIVE_TURNS = _build_allowed_relative_turns()

# Toggle global Clima:
# - True: si el usuario dibuja un tramo < min_segment_length, se autocorrige
#   al mínimo (sin popup de confirmación).
# - False: se mantiene comportamiento con popup (PolyLib por defecto).
AUTO_CLAMP_MIN_SEGMENT_LENGTH = True

# Longitud máxima por tramo al dibujar en modo creación (mm). Si el clic deja
# el tramo más largo, se recorta automáticamente sobre la misma dirección (1,175 m).
# Implementado envolviendo process_mouse_msg del interactor; no modifica PolyLib.
CLIMA_MAX_SEGMENT_LENGTH_MM = 1175.0
AUTO_CLAMP_MAX_SEGMENT_LENGTH = True


def _clamp_polyline_point_to_max_seg(
    p0: AllplanGeo.Point3D, p1: AllplanGeo.Point3D, max_len_mm: float
) -> AllplanGeo.Point3D:
    if max_len_mm <= 0:
        return AllplanGeo.Point3D(p1.X, p1.Y, p1.Z)
    dist = float(AllplanGeo.CalcLength(AllplanGeo.Line3D(p0, p1)))
    if dist <= max_len_mm + 1e-6:
        return AllplanGeo.Point3D(p1.X, p1.Y, p1.Z)
    t = max_len_mm / dist if dist > 1e-12 else 0.0
    return AllplanGeo.Point3D(
        p0.X + t * (p1.X - p0.X),
        p0.Y + t * (p1.Y - p0.Y),
        p0.Z + t * (p1.Z - p0.Z),
    )


def _install_clima_max_segment_process_mouse_wrap(script_object) -> None:
    """Tras cada clic que añade vértice en modo creación, acorta el tramo si supera el máximo."""
    if not AUTO_CLAMP_MAX_SEGMENT_LENGTH or float(CLIMA_MAX_SEGMENT_LENGTH_MM) <= 0:
        return
    inter = getattr(script_object, "script_object_interactor", None)
    if inter is None or getattr(inter, "_clima_max_segment_mouse_wrapped", False):
        return
    max_mm = float(CLIMA_MAX_SEGMENT_LENGTH_MM)
    orig_pm = inter.process_mouse_msg

    def _wrapped_process_mouse_msg(mouse_msg, pnt, msg_info):
        n_before = len(inter.points)
        r = orig_pm(mouse_msg, pnt, msg_info)
        try:
            if (
                inter.create_mode
                and len(inter.points) > n_before
                and len(inter.points) >= 2
            ):
                a = inter.points[-2]
                b = inter.points[-1]
                b_new = _clamp_polyline_point_to_max_seg(a, b, max_mm)
                if (b_new.X - b.X) ** 2 + (b_new.Y - b.Y) ** 2 + (b_new.Z - b.Z) ** 2 > 1e-6:
                    inter.points[-1] = b_new
                    inter.current_point = b_new
                    inter.get_segments()
                    inter._update_segment_groups()
                    script_object._create_elements_preview()
                    inter._generate_elements_for_preview()
                    try:
                        ref = inter.current_point if inter.current_point is not None else b_new
                        cur = inter.coord_input.GetCurrentPoint(ref).GetPoint()
                    except Exception:
                        cur = b_new
                    inter._draw_preview(cur)
        except Exception as ex:
            print(f"[ClimaPolyline] max segment clamp: {ex}")
        return r

    inter.process_mouse_msg = _wrapped_process_mouse_msg
    inter._clima_max_segment_mouse_wrapped = True


CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation=INST_NAME.upper(),
    parameters_show=profile.show,
    parameters_enabled=profile.enabled,
    num_td_path=base_path,

    limit_angles=True,
    # Limitador: giro relativo respecto al tramo previo en [-45°, +45°].
    allowed_angles=ALLOWED_RELATIVE_TURNS,
)

reload_module = [
    PBL,
    PBL_interactor,
    PBL_object
]


def check_allplan_version(_build_ele, _version):
    # Recarga utils Clima sin reiniciar Allplan (placement_logic → offsets → geo_handler).
    try:
        importlib.reload(_placement_logic_mod)
    except Exception as e:
        print(f"[ClimaPolyline] reload placement_logic: {e}")
    try:
        importlib.reload(_codo_placement_offsets_mod)
    except Exception as e:
        print(f"[ClimaPolyline] reload codo_placement_offsets: {e}")
    try:
        importlib.reload(_geo_handler_mod)
    except Exception as e:
        print(f"[ClimaPolyline] reload geo_handler: {e}")

    for module in reload_module:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"Error al recargar el módulo {module.__name__}: {e}")
    # Garantizar registro en runtime aunque el registry quede cacheado
    try:
        register_pythonpart("quiebro", Quiebro2Script)
    except Exception as e:
        print(f"Error al registrar quiebro: {e}")
    try:
        register_pythonpart("reduccions", ReduccionsScript)
    except Exception as e:
        print(f"Error al registrar reduccions: {e}")
    return True

def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )

    # Sin tocar librería: activar/desactivar auto-clamp de mínimo por script.
    script_object.auto_clamp_min_segment_length = bool(AUTO_CLAMP_MIN_SEGMENT_LENGTH)
    script_object.clima_reductor_straight_mm = _read_clima_reductor_straight_mm(build_ele)

    def _disable_vertex_reducer_path():
        """
        Desactiva el flujo de reductor por vértice en PolyLib para Clima.
        Nuestro flujo de `reductor` se resuelve por segmento en geo_handler.
        """
        conns = getattr(script_object, "allowed_connections", None)
        if isinstance(conns, list):
            script_object.allowed_connections = [
                c for c in conns
                if c != ElementTypes.REDUCION and str(getattr(c, "value", c)) != "reduccion"
            ]

    # Aplicar una vez y mantenerlo en cada resolución de instalación.
    _disable_vertex_reducer_path()
    _orig_resolve_installation_config = script_object.resolve_installation_config

    def _resolve_installation_config_no_vertex_reducer(*args, **kwargs):
        out = _orig_resolve_installation_config(*args, **kwargs)
        _disable_vertex_reducer_path()
        # Mantener el toggle global tras refrescos de config/instalación.
        script_object.auto_clamp_min_segment_length = bool(AUTO_CLAMP_MIN_SEGMENT_LENGTH)
        return out

    script_object.resolve_installation_config = _resolve_installation_config_no_vertex_reducer

    def _diameter_width_mm(diam_value):
        if diam_value is None:
            return None
        s = str(diam_value).strip().lower()
        if s == "reductor":
            return None
        try:
            return float(s.split("x", 1)[0].strip())
        except (TypeError, ValueError):
            return None

    def _compute_reductor_shift_for_segment(path_idx: int, seg_idx: int):
        paths = getattr(script_object, "saved_paths", None)
        if not paths or path_idx < 0 or path_idx >= len(paths):
            return (0.0, 0.0, 0.0)
        path = paths[path_idx]
        if seg_idx <= 0 or seg_idx + 1 >= len(path):
            return (0.0, 0.0, 0.0)

        meta = getattr(script_object, "persistent_metadata", {}) or {}
        info = meta.get(f"{path_idx}_{seg_idx}")
        diam = str(getattr(info, "diameter", "")).strip().lower() if info is not None else ""
        if diam != "reductor":
            return (0.0, 0.0, 0.0)

        prev_info = meta.get(f"{path_idx}_{seg_idx - 1}")
        next_info = meta.get(f"{path_idx}_{seg_idx + 1}")
        if prev_info is None or next_info is None:
            return (0.0, 0.0, 0.0)

        w_in = _diameter_width_mm(getattr(prev_info, "diameter", None))
        w_out = _diameter_width_mm(getattr(next_info, "diameter", None))
        if w_in is None or w_out is None:
            return (0.0, 0.0, 0.0)

        delta_mm = (w_in - w_out) * 0.5
        if abs(delta_mm) < 0.001:
            return (0.0, 0.0, 0.0)

        p0 = path[seg_idx]
        p1 = path[seg_idx + 1]
        dx = float(p1.X - p0.X)
        dy = float(p1.Y - p0.Y)
        length_xy = (dx * dx + dy * dy) ** 0.5
        if length_xy < 1e-6:
            return (0.0, 0.0, 0.0)

        nx = dy / length_xy
        ny = -dx / length_xy
        return (nx * delta_mm, ny * delta_mm, 0.0)

    def _clone_paths(paths_src):
        out = []
        for path in paths_src or []:
            if not path:
                out.append([])
                continue
            out.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in path])
        return out

    def _same_paths_shape(a_paths, b_paths):
        if a_paths is None or b_paths is None:
            return False
        if len(a_paths) != len(b_paths):
            return False
        for a_path, b_path in zip(a_paths, b_paths):
            if len(a_path or []) != len(b_path or []):
                return False
        return True

    def _refresh_reductor_base_paths():
        paths = getattr(script_object, "saved_paths", None)
        if not paths:
            script_object._reductor_shift_base_paths = None
            script_object._reductor_shift_state = {}
            return
        script_object._reductor_shift_base_paths = _clone_paths(paths)
        script_object._reductor_shift_state = {}

    def _apply_reductor_polyline_shifts():
        """
        Recalcula y aplica los desvíos de polilínea por segmentos 'reductor'
        de forma diferencial (new - old), para evitar acumulaciones y para que
        también reaccione cuando cambian los diámetros vecinos.
        """
        paths = getattr(script_object, "saved_paths", None)
        if not paths:
            return

        base_paths = getattr(script_object, "_reductor_shift_base_paths", None)
        if (base_paths is None) or (not _same_paths_shape(base_paths, paths)):
            base_paths = _clone_paths(paths)
            script_object._reductor_shift_base_paths = base_paths

        # Reponer SIEMPRE la base sin shift antes de recalcular.
        # Esto evita deriva por aplicar correcciones diferenciales sobre un path ya deformado.
        script_object.saved_paths = _clone_paths(base_paths)
        paths = getattr(script_object, "saved_paths", None) or []

        new_state = {}
        meta = getattr(script_object, "persistent_metadata", {}) or {}

        # Construir estado deseado actual.
        for path_idx, path in enumerate(paths):
            if not path or len(path) < 3:
                continue
            for seg_idx in range(1, len(path) - 1):
                info = meta.get(f"{path_idx}_{seg_idx}")
                diam = str(getattr(info, "diameter", "")).strip().lower() if info is not None else ""
                if diam != "reductor":
                    continue
                shift = _compute_reductor_shift_for_segment(path_idx, seg_idx)
                if abs(shift[0]) > 1e-6 or abs(shift[1]) > 1e-6 or abs(shift[2]) > 1e-6:
                    new_state[(path_idx, seg_idx)] = shift

        # Aplicar diferencias manteniendo fijos ambos extremos (inicio y final):
        # - No se toca la cola posterior al reductor.
        # - No se mueve el primer punto del path.
        # - La compensación se absorbe en un tramo interno previo al reductor.
        def _translate_range(path_pts, start_idx, end_idx, vx, vy, vz):
            if not path_pts:
                return
            start_idx = max(0, int(start_idx))
            end_idx = max(0, int(end_idx))
            if start_idx >= len(path_pts):
                return
            if end_idx >= len(path_pts):
                end_idx = len(path_pts) - 1
            if end_idx < start_idx:
                return
            for ii in range(start_idx, end_idx + 1):
                pp = path_pts[ii]
                path_pts[ii] = AllplanGeo.Point3D(pp.X + vx, pp.Y + vy, pp.Z + vz)

        def _is_parallel_to_shift(path_pts, vertex_idx, sx, sy, tol=1e-3):
            """
            Verifica si el segmento (vertex_idx-1 -> vertex_idx) es paralelo al shift (sx, sy).
            """
            if vertex_idx <= 0 or vertex_idx >= len(path_pts):
                return False
            p_prev = path_pts[vertex_idx - 1]
            p_cur = path_pts[vertex_idx]
            vx = float(p_cur.X - p_prev.X)
            vy = float(p_cur.Y - p_prev.Y)
            seg_norm = (vx * vx + vy * vy) ** 0.5
            sh_norm = (sx * sx + sy * sy) ** 0.5
            if seg_norm < 1e-9 or sh_norm < 1e-9:
                return False
            vx /= seg_norm
            vy /= seg_norm
            sxn = sx / sh_norm
            syn = sy / sh_norm
            cross = abs((vx * syn) - (vy * sxn))
            return cross <= tol

        all_keys = sorted(new_state.keys(), key=lambda k: (k[0], k[1]))
        for path_idx, seg_idx in all_keys:
            dx, dy, dz = new_state.get((path_idx, seg_idx), (0.0, 0.0, 0.0))
            if abs(dx) < 1e-6 and abs(dy) < 1e-6 and abs(dz) < 1e-6:
                continue

            if path_idx < 0 or path_idx >= len(paths):
                continue
            path = paths[path_idx]
            if not path or seg_idx + 1 >= len(path):
                continue
            # Reparto adaptativo de compensación:
            # - Prioriza el lado anterior al reductor (requerimiento funcional).
            # - Si el reductor está demasiado cerca del inicio, usa lado posterior.
            # - Nunca toca el primer ni el último punto.
            before_internal = max(0, seg_idx - 1)  # vértices internos en lado anterior
            after_internal = max(0, (len(path) - 2) - (seg_idx + 1) + 1)  # lado posterior
            min_internal_vertices = 2

            # Caso físicamente subdeterminado: no hay margen interno suficiente en
            # ninguno de los lados para compensar sin crear diagonales.
            # Priorizamos continuidad del eje y permitimos mover el punto final.
            if before_internal < min_internal_vertices and after_internal < min_internal_vertices:
                _translate_range(path, seg_idx + 1, len(path) - 1, dx, dy, dz)
                continue

            use_before = before_internal >= min_internal_vertices
            if not use_before and after_internal >= min_internal_vertices:
                use_before = False
            elif not use_before:
                # Caso degenerado: elegir el lado con más margen interno.
                use_before = before_internal >= after_internal

            if use_before:
                # 1) Desplazar toda la cabeza previa al reductor.
                _translate_range(path, 0, seg_idx, -dx, -dy, -dz)
                # 2) Anclar inicio devolviendo el tramo [0 .. pivot-1].
                before_segments = seg_idx
                if before_segments >= 2:
                    pivot_idx = None
                    for cand in range(seg_idx, 0, -1):
                        if _is_parallel_to_shift(path, cand, dx, dy):
                            pivot_idx = cand
                            break
                    if pivot_idx is None:
                        pivot_idx = 1
                    _translate_range(path, 0, pivot_idx - 1, dx, dy, dz)
            else:
                # 1) Desplazar toda la cola posterior al reductor.
                _translate_range(path, seg_idx + 1, len(path) - 1, dx, dy, dz)
                # 2) Anclar final devolviendo [pivot+1 .. end] para no anular
                #    completamente el shift en casos cortos/colineales.
                after_segments = (len(path) - 1) - (seg_idx + 1)
                if after_segments >= 2:
                    pivot_idx = None
                    for cand in range(seg_idx + 2, len(path) - 1):
                        if _is_parallel_to_shift(path, cand, dx, dy):
                            pivot_idx = cand
                            break
                    if pivot_idx is None:
                        pivot_idx = len(path) - 2
                    _translate_range(path, pivot_idx + 1, len(path) - 1, -dx, -dy, -dz)

        script_object._reductor_shift_state = new_state

    def _apply_quiebro_polyline_length_clamp(max_len_mm: float) -> bool:
        """
        Recorta en la polilínea real los segmentos elegibles como quiebro
        (patrón recto->inclinado->recto) cuando superan el largo máximo.
        """
        paths = getattr(script_object, "saved_paths", None)
        if not paths or max_len_mm <= 0.0:
            return False

        def _signed_delta_deg(a_deg: float, b_deg: float) -> float:
            return (float(a_deg) - float(b_deg) + 180.0) % 360.0 - 180.0

        def _angle_xy_deg(p0, p1) -> float:
            dx = float(p1.X - p0.X)
            dy = float(p1.Y - p0.Y)
            return math.degrees(math.atan2(dy, dx))

        changed = False
        eps = 1e-3
        for path_idx, path in enumerate(paths):
            if not path or len(path) < 4:
                continue

            i = 1  # segmento "actual" con vecinos previo y siguiente
            while i <= len(path) - 3:
                p_prev0 = path[i - 1]
                p_prev1 = path[i]
                p_cur0 = path[i]
                p_cur1 = path[i + 1]
                p_next0 = path[i + 1]
                p_next1 = path[i + 2]

                # Nunca clamplear como "quiebro" un tramo marcado como reductor.
                meta = getattr(script_object, "persistent_metadata", {}) or {}
                cur_info = meta.get(f"{path_idx}_{i}")
                cur_diam = str(getattr(cur_info, "diameter", "")).strip().lower() if cur_info is not None else ""
                if cur_diam == "reductor":
                    i += 1
                    continue

                vx = float(p_cur1.X - p_cur0.X)
                vy = float(p_cur1.Y - p_cur0.Y)
                vz = float(p_cur1.Z - p_cur0.Z)
                cur_len = (vx * vx + vy * vy + vz * vz) ** 0.5
                if cur_len <= max_len_mm + eps or cur_len < eps:
                    i += 1
                    continue

                prev_ang = _angle_xy_deg(p_prev0, p_prev1)
                cur_ang = _angle_xy_deg(p_cur0, p_cur1)
                next_ang = _angle_xy_deg(p_next0, p_next1)

                d_rel = abs(_signed_delta_deg(cur_ang, prev_ang))
                back_to_base = abs(_signed_delta_deg(next_ang, prev_ang)) <= 0.5
                is_quiebro_candidate = (d_rel > (0.5 - eps)) and (d_rel <= (45.0 + eps)) and back_to_base
                if not is_quiebro_candidate:
                    i += 1
                    continue

                scale = max_len_mm / cur_len
                new_end = AllplanGeo.Point3D(
                    p_cur0.X + vx * scale,
                    p_cur0.Y + vy * scale,
                    p_cur0.Z + vz * scale,
                )
                shift_x = float(new_end.X - p_cur1.X)
                shift_y = float(new_end.Y - p_cur1.Y)
                shift_z = float(new_end.Z - p_cur1.Z)
                if abs(shift_x) < eps and abs(shift_y) < eps and abs(shift_z) < eps:
                    i += 1
                    continue

                # Mover el vértice final del quiebro y toda la cola posterior.
                for j in range(i + 1, len(path)):
                    pj = path[j]
                    path[j] = AllplanGeo.Point3D(
                        pj.X + shift_x,
                        pj.Y + shift_y,
                        pj.Z + shift_z,
                    )

                changed = True
                print(
                    "[ClimaPolyline] Quiebro segment clamp",
                    f"path_idx={path_idx}",
                    f"segment_idx={i}",
                    f"requested_mm={round(cur_len, 3)}",
                    f"applied_mm={round(max_len_mm, 3)}",
                )
                i += 1

        return changed

    _orig_on_control_event = script_object.on_control_event

    def _clima_refresh_polyline_preview() -> None:
        inter = getattr(script_object, "script_object_interactor", None)
        if inter is None:
            return
        try:
            inter.get_segments()
            inter._update_segment_groups()
            script_object._create_elements_preview()
            inter._generate_elements_for_preview()
        except Exception:
            pass

    def _on_control_event_clima(event_id: int):
        restore_diameter = None
        eff_id = event_id
        if event_id == APLICAR_REDUCTOR_CLIMA_EVENT:
            restore_diameter = script_object.diameter_type
            script_object.clima_reductor_straight_mm = _read_clima_reductor_straight_mm(
                script_object.build_ele
            )
            script_object.diameter_type = "reductor"
            eff_id = EventIds.MODIFICAR_DIAMETRO

        result = _orig_on_control_event(eff_id)

        if eff_id == EventIds.MODIFICAR_DIAMETRO:
            quiebro_clamped = _apply_quiebro_polyline_length_clamp(
                float(getattr(script_object, "max_quiebro_segment_length", 1400.0))
            )
            _apply_reductor_polyline_shifts()
            # Regenerar después del ajuste geométrico de la polilínea.
            _clima_refresh_polyline_preview()
        else:
            # Cualquier operación no relacionada con cambio de diámetro invalida
            # la base anterior de shift (puntos añadidos/borrados, etc.).
            _refresh_reductor_base_paths()

        if restore_diameter is not None:
            script_object.diameter_type = restore_diameter

        return result

    script_object.on_control_event = _on_control_event_clima
    _refresh_reductor_base_paths()

    # Restricción para segmento de quiebro (polilínea):
    # si el usuario dibuja más largo, se ajusta automáticamente a este máximo.
    script_object.max_quiebro_segment_length = 1400.0  # mm
    script_object.quiebro_angle_deg = 14.42
    script_object.quiebro_angle_tolerance_deg = 0.8
    # HOOK: Creación de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creación de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    script_object.clima_max_segment_length_mm = float(CLIMA_MAX_SEGMENT_LENGTH_MM)

    _orig_start_input = script_object.start_input

    def _start_input_clima():
        out = _orig_start_input()
        _install_clima_max_segment_process_mouse_wrap(script_object)
        return out

    script_object.start_input = _start_input_clima
    _install_clima_max_segment_process_mouse_wrap(script_object)

    _orig_modify_element_property = script_object.modify_element_property

    def _align_clima_diameter_after_installation_change(prev_diam: str | None) -> None:
        """
        Tras cambiar Impulsió/Retorn, PolyLib fija diameter_type al primero de la lista.
        En Clima no hay REDUCION en connections: todos los tramos usan ese valor único.
        Si la paleta sigue en un diámetro válido (p. ej. 750x150), hay que resincronizar.
        """
        dlist = getattr(script_object, "diameter_list", None) or []
        dset = {str(d).strip() for d in dlist if d is not None}
        if not dset:
            return

        dparam = getattr(script_object.build_ele, ParamNames.Installation.DIAMETER_TYPE_STR, None)
        pal_diam = None
        if dparam is not None:
            raw = getattr(dparam, "value", None)
            if raw is not None:
                pal_diam = str(raw).strip()

        chosen = None
        if pal_diam and pal_diam in dset:
            chosen = pal_diam
        elif prev_diam and prev_diam in dset:
            chosen = prev_diam

        if chosen is None:
            return

        script_object.diameter_type = chosen
        if dparam is not None:
            try:
                dparam.value = chosen
            except Exception:
                pass
        _clima_refresh_polyline_preview()

    def _modify_element_property_clima(name: str, value) -> bool:
        prev_diam = None
        if name == ParamNames.Installation.INSTALLATION_TYPE:
            pd = getattr(script_object, "diameter_type", None)
            if pd is not None:
                prev_diam = str(pd).strip()

        upd = _orig_modify_element_property(name, value)

        if name == ParamNames.Installation.INSTALLATION_TYPE:
            _align_clima_diameter_after_installation_change(prev_diam)

        if name == CLIMA_REDUCTOR_STRAIGHT_PALETTE_PARAM:
            param = getattr(script_object.build_ele, name, None)
            if param is not None:
                try:
                    param.value = value
                except Exception:
                    pass
            script_object.clima_reductor_straight_mm = _read_clima_reductor_straight_mm(
                script_object.build_ele
            )
            _clima_refresh_polyline_preview()
            return True
        return upd

    script_object.modify_element_property = _modify_element_property_clima

    return script_object

# ========================================
# HOOKS PERSONALIZADOS
# ========================================
def _create_elements_for_segment_group(segments, so: PBL.script_object.PolylineScriptObject):
    """
    Genera la geometría 3D de los elementos sin crear PythonParts.
    Devuelve una lista de elementos generados para un grupo de segmentos.
    """
    try:
        print(
            "[ClimaPolyline] _create_elements_for_segment_group",
            f"segments={segments}",
            f"so.current_inst_config={getattr(so, 'current_inst_config', None)}",
        )
    except Exception as e:
        print(f"[ClimaPolyline] Debug print failed: {e}")


    element_type_core = None
    elements_generated = []

    model_base = so.current_inst_config

    if model_base:
        element_type_core = model_base["key"]

    # ------------------------------------------------------------------
    # CASO B: Conducto
    # ------------------------------------------------------------------
    if model_base and element_type_core in ["tram_recte"]:

        inst_label = str(model_base.get("label", "retorn"))

        # Cache compartido para no regenerar el mismo modelo N veces por segmento
        _factory_cache: dict = {}

        def _resolve_seg_diameter(seg_item):
            """Resuelve el diámetro efectivo por segmento; fallback a paleta."""
            try:
                info = getattr(seg_item, "info", None)
                seg_diam = getattr(info, "diameter", None) if info is not None else None
                if seg_diam:
                    return str(seg_diam)
            except Exception:
                pass
            return str(so.diameter_type or "150x150")

        def _conducto_factory(_seg, target_length_mm=None):
            # Clima es multidiámetro por path: usar siempre el diámetro del segmento.
            diam = _resolve_seg_diameter(_seg)
            length_key = None
            if target_length_mm is not None:
                try:
                    length_key = int(round(float(target_length_mm)))
                except Exception:
                    length_key = None
            key = ("tram_recte", inst_label, diam, length_key)
            if key not in _factory_cache:
                exec_kwargs = {"installation_type": inst_label, "diameter": diam}
                if target_length_mm is not None:
                    exec_kwargs["length"] = float(target_length_mm)
                models = so._get_pythonpart_installed(
                    element_key="tram_recte",
                    exec_kwargs=exec_kwargs
                )
                # Conservar todos los sub-elementos (cuerpo + flecha de dirección).
                _factory_cache[key] = list(models) if models else None
            return _factory_cache[key]

        def _codo_factory(_seg, _next_seg):
            # Para codo, priorizar el diámetro del tramo de entrada.
            diam = _resolve_seg_diameter(_seg)
            key = ("colze", inst_label, diam)
            if key not in _factory_cache:
                models = so._get_pythonpart_installed(
                    element_key="colze",
                    exec_kwargs={"installation_type": inst_label, "diameter": diam}
                )
                # Conservar cuerpo + flecha del codo.
                _factory_cache[key] = list(models) if models else None
            return _factory_cache[key]

        def _quiebro_factory(prev_seg_item, quiebro_seg_item):
            # Quiebro2 hereda tipo/diámetro del tramo y adapta inclinación/longitud dinámicamente.
            prev_info = getattr(prev_seg_item, "info", None)
            diam = str(getattr(prev_info, "diameter", None) or so.diameter_type or "150x150")
            prev_ang = float(getattr(prev_seg_item.data, "angulo_xy", 0.0))
            cur_ang = float(getattr(quiebro_seg_item.data, "angulo_xy", 0.0))
            delta = (cur_ang - prev_ang + 180.0) % 360.0 - 180.0
            incl_h_deg = max(45.0, min(90.0, 90.0 - abs(delta)))
            signed_vertical_deg = -float(delta)
            requested_length_mm = float(quiebro_seg_item.data.longitud_3d)
            length_mm = min(requested_length_mm, 1400.0)
            # Exponer el largo efectivo para trazabilidad/uso en pipeline de colocación.
            try:
                setattr(quiebro_seg_item.data, "quiebro_effective_length_mm", float(length_mm))
            except Exception:
                pass
            if requested_length_mm > length_mm + 1e-6:
                print(
                    "[ClimaPolyline] Quiebro2 length clamp",
                    f"requested_mm={round(requested_length_mm, 3)}",
                    f"applied_mm={round(length_mm, 3)}",
                    "max_mm=1400.0",
                )
            key = (
                "quiebro",
                inst_label,
                diam,
                int(round(length_mm)),
                round(incl_h_deg, 3),
                round(signed_vertical_deg, 3),
            )
            if key not in _factory_cache:
                models = so._get_pythonpart_installed(
                    element_key="quiebro",
                    exec_kwargs={
                        "installation_type": inst_label,
                        "diameter": diam,
                        "length_mm": length_mm,
                        "inclination_from_horizontal_deg": incl_h_deg,
                        # Signo de giro para orientar el oblicuo en mano izquierda/derecha.
                        "angle_from_vertical_signed_deg": signed_vertical_deg,
                    },
                )
                # Conservar TODOS los subelementos de quiebro2 (cuerpo + hendiduras + flecha).
                _factory_cache[key] = list(models) if models else None
            return _factory_cache[key]

        def _reduccion_factory(seg_in_item, seg_out_item, target_length_mm=None):
            """
            Crea reductor entre secciones distintas (Impulsió → redimplusio, Retorn → redretorn).
            Puede recibir `target_length_mm` para usar el largo de un segmento "reductor".
            """
            if inst_label not in ("Impulsió", "Retorn"):
                return None
            d_in = _resolve_seg_diameter(seg_in_item)
            d_out = _resolve_seg_diameter(seg_out_item)
            if d_in == d_out:
                return None

            if target_length_mm is None:
                # Ajuste automático de largo al espacio disponible en el nudo:
                # L_disp = Lseg_izq/2 + Lseg_der/2 - holguras
                l_in = float(getattr(getattr(seg_in_item, "data", None), "longitud_3d", 0.0) or 0.0)
                l_out = float(getattr(getattr(seg_out_item, "data", None), "longitud_3d", 0.0) or 0.0)
                holgura_por_lado_mm = 20.0
                l_disponible = (l_in * 0.5) + (l_out * 0.5) - (2.0 * holgura_por_lado_mm)
                target_length_mm = max(120.0, l_disponible)
            else:
                target_length_mm = max(120.0, float(target_length_mm))

            be = getattr(so, "build_ele", None)
            straight_mm = None
            _cached_sl = getattr(so, "clima_reductor_straight_mm", None)
            try:
                if _cached_sl is not None and float(_cached_sl) in _CLIMA_REDUCTOR_STRAIGHT_ALLOWED_MM:
                    straight_mm = float(_cached_sl)
            except (TypeError, ValueError):
                straight_mm = None
            if straight_mm is None:
                straight_mm = (
                    _read_clima_reductor_straight_mm(be)
                    if be is not None
                    else float(CLIMA_REDUCTOR_STRAIGHT_MM_DEFAULT)
                )

            key = (
                "reduccions",
                inst_label,
                d_in,
                d_out,
                round(target_length_mm, 3),
                round(straight_mm, 3),
            )
            if key not in _factory_cache:
                models = so._get_pythonpart_installed(
                    element_key="reduccions",
                    exec_kwargs={
                        "installation_type": inst_label,
                        "diameter_in": d_in,
                        "diameter_out": d_out,
                        "target_length_mm": target_length_mm,
                        "straight_len_mm": straight_mm,
                    },
                )
                # Mantener TODOS los sub-elementos del reductor (cuerpo, flecha, línea guía).
                _factory_cache[key] = list(models) if models else None
            return _factory_cache[key]

        _attr_docs = _attr_lookup_documents(so)
        if inst_label == "Impulsió":
            print(
                "[ClimaPolyline] Impulsió TAPA: attr lookup docs count=",
                len(_attr_docs),
                "types=",
                [type(d).__name__ for d in _attr_docs],
            )
            if not _attr_docs:
                print(
                    "[ClimaPolyline] WARNING: no documents for TAPA lookup "
                    "(so.doc / coord_input / DocumentManager); set IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK"
                )
        elif inst_label == "Retorn":
            print(
                "[ClimaPolyline] Retorn TAPA (primer tramo): attr lookup docs count=",
                len(_attr_docs),
                "types=",
                [type(d).__name__ for d in _attr_docs],
            )
            if not _attr_docs:
                print(
                    "[ClimaPolyline] WARNING: no documents for TAPA lookup on Retorn first segment; "
                    "set IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK (shared with Impulsió)"
                )

        first_seg_color = RETORN_FIRST_SEGMENT_CONDUCTO_COLOR if inst_label == "Retorn" else None
        last_seg_color = IMPULSIO_LAST_SEGMENT_CONDUCTO_COLOR if inst_label == "Impulsió" else None
        first_seg_tapa = (
            RETORN_FIRST_SEGMENT_TAPA_VALUE if inst_label == "Retorn" else None
        )
        last_seg_tapa = (
            IMPULSIO_LAST_SEGMENT_TAPA_VALUE if inst_label == "Impulsió" else None
        )
        processor = _geo_handler_mod.PipelineProcessor(
            elem3D_list=[],
            element_type="tram_recte",
            conducto_factory=_conducto_factory,
            codo_factory=_codo_factory,
            quiebro_factory=_quiebro_factory,
            reduccion_factory=_reduccion_factory,
            first_segment_conducto_color=first_seg_color,
            last_segment_conducto_color=last_seg_color,
            conducto_default_body_color=CLIMA_TRAM_RECTE_BODY_COLOR_DEFAULT,
            first_segment_tapa_value=first_seg_tapa,
            last_segment_tapa_value=last_seg_tapa,
            last_segment_tapa_attr_aliases=IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ALIASES,
            last_segment_tapa_attr_id_fallback=IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK,
            attr_documents=_attr_docs,
        )
        elements_generated = processor.process(segments=segments)

    return elements_generated

def _create_elements_with_layers_attrs(elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject) -> list:
    """
    Ajustes finales por path sin modificar PolyLib.

    En Impulsió + modo grupo, el PYP agrupado solo copia atributos del primer elemento;
    replicamos TAPA del último cuerpo de tubo al primero para que llegue al ``attribute_list``.
    """
    elements_generated_final = list(elements_generated) if elements_generated else []
    try:
        cfg = getattr(so, "current_inst_config", None) or {}
        if str(cfg.get("label", "")) != "Impulsió":
            return elements_generated_final
        if getattr(so, "is_individual_mode", True):
            return elements_generated_final

        core = str(getattr(so, "element_type_core", "tram_recte"))
        bodies: list = []
        i = 0
        n = len(elements_generated_final)
        while i < n:
            item = elements_generated_final[i]
            et = getattr(item, "element_type", None)
            if et != core:
                i += 1
                continue
            body_el = getattr(item, "element", None)
            if i + 1 < n and getattr(elements_generated_final[i + 1], "element_type", None) == core:
                if body_el is not None:
                    bodies.append(body_el)
                i += 2
            else:
                if body_el is not None:
                    bodies.append(body_el)
                i += 1

        if len(bodies) < 2:
            return elements_generated_final

        first_body, last_body = bodies[0], bodies[-1]
        if first_body is last_body:
            return elements_generated_final

        merged = _geo_handler_mod._merge_user_attribute_string(
            first_body,
            _attr_lookup_documents(so),
            "TAPA",
            IMPULSIO_LAST_SEGMENT_TAPA_VALUE,
            name_aliases=IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ALIASES,
            id_fallback=IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK,
        )
        print(
            "[ClimaPolyline] Modo grupo Impulsió: TAPA último tramo replicada en primer cuerpo",
            f"path_idx={path_idx} ok={merged}",
        )
    except Exception as ex:
        print(f"[ClimaPolyline] _create_elements_with_layers_attrs: {ex}")

    return elements_generated_final



# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================
# def _merge_attributes(base_attrs: list, override_attrs: list) -> list:
#     """
#     Fusiona dos listas de atributos de Allplan.
#     Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.

#     Args:
#         base_attrs: Lista base de atributos (AttributeString, AttributeDouble, etc.)
#         override_attrs: Lista de atributos que sobrescriben los base

#     Returns:
#         Lista fusionada de atributos sin duplicados por ID

#     Example:
#         base = [AttributeString(Id: 55015, Value: "IS08"),
#                 AttributeString(Id: 55010, Value: "")]
#         override = [AttributeString(Id: 55015, Value: "testtt00009")]

#         result = _merge_attributes(base, override)
#         # result tendrá Id 55015 con valor "testtt00009" y Id 55010 con valor ""
#     """
#     # Diccionario para rastrear atributos por ID
#     # Clave: ID del atributo, Valor: objeto de atributo completo
#     attr_dict = {}

#     # 1. Primero agregar todos los atributos base
#     for attr in base_attrs:
#         attr_dict[attr.Id] = attr

#     # 2. Sobrescribir/agregar con los atributos de override
#     for attr in override_attrs:
#         attr_dict[attr.Id] = attr

#     # 3. Convertir el diccionario de vuelta a lista
#     # Ordenar por ID para mantener consistencia (opcional)
#     merged_list = [attr_dict[key] for key in sorted(attr_dict.keys())]

#     return merged_list

# def _process_auto_numbering(
#     attribute_list: list,
#     inst_type: str,
#     so: PBL.script_object.PolylineScriptObject,
#     forced_number: int | None = None
# ) -> tuple[list, bool]:
#     # Si la numeración automática está desactivada globalmente,
#     # devolvemos la lista tal cual, sin tocar atributos.
#     if not AUTO_NUMBERING_ENABLED:
#         return attribute_list, False
#     if not attribute_list:
#         return attribute_list, False

#     new_attr_list = []
#     modified = False
#     target_id = 1083

#     for attr in attribute_list:
#         if hasattr(attr, "Id") and attr.Id == target_id:
#             # SIEMPRE generamos el valor si hay un forced_number,
#             # o si el valor es exactamente "TV" (semilla inicial)
#             if forced_number is not None:
#                 new_value = f"TV-{forced_number}"
#                 new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
#                 modified = True
#                 continue
#             elif attr.Value == "TV":
#                 # Caso de rescate: si no hay forced_number pero detectamos la semilla
#                 if so.init_storage:
#                     num = so.init_storage._get_next_number(inst_type)
#                     so.init_storage._save_numbering_file()
#                     new_value = f"TV-{num}"
#                     new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
#                     modified = True
#                     continue

#         new_attr_list.append(attr)

#     return new_attr_list, modified

# def _extract_number_from_attrs(attribute_list: list) -> int | None:
#     """
#     Extrae el número entero del atributo 1083 (formato 'TV-X').
#     """
#     if not attribute_list:
#         return None

#     target_id = 1083
#     prefix = "TV-"

#     for attr in attribute_list:
#         try:
#             # Verificamos si es el atributo correcto
#             if hasattr(attr, "Id") and attr.Id == target_id:
#                 val_str = str(attr.Value)

#                 # Si el valor ya tiene el formato "TV-5", extraemos el 5
#                 if prefix in val_str:
#                     num_part = val_str.replace(prefix, "").strip()
#                     if num_part.isdigit():
#                         return int(num_part)

#                 # Si por alguna razón solo está el número como string
#                 elif val_str.isdigit():
#                     return int(val_str)

#         except Exception as e:
#             print(f"[EXTRACT] Error procesando atributo: {e}")
#             continue

#     return None

# def _apply_attributes_to_model_elem(model_elem, attr_list):
#         """
#         Empaqueta y aplica una lista de atributos a un elemento 3D de Allplan
#         usando la estructura AttributeSet -> Attributes.
#         """
#         if not attr_list:
#             return
#         try:
#             attr_set_list = []
#             # Creamos el set de atributos
#             attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
#             # Creamos el objeto Attributes contenedor
#             attributes = AllplanBaseElements.Attributes(attr_set_list)
#             # Aplicamos al elemento
#             model_elem.SetAttributes(attributes)
#             return model_elem
#         except Exception as e:
#             print(f"[Error] Al aplicar atributos: {e}")

# ========================================
# APLICACIÓN DE LAYERS
# ========================================
# def _apply_layer_to_element(model_elem: AllplanBasisElements.ModelElement3D,
#                             key_layer: str,
#                             so: PBL.script_object.PolylineScriptObject) -> AllplanBasisElements.ModelElement3D:
#         """
#         Responsabilidad única: Buscar el ID del layer y aplicarlo al elemento.
#         """
#         layer_id = _get_layer_id(key_layer, so)
#         if layer_id is not None:
#             try:
#                 props = model_elem.CommonProperties
#                 props.Layer = layer_id
#                 model_elem.CommonProperties = props
#             except Exception as e:
#                 print(f"[Error] Fallo al setear layer en {key_layer}: {e}")
#                 pass
#         else:
#             print(f"[Warn] No se pudo determinar un ID de Layer válido para {key_layer}")

#         return model_elem

# def _get_layer_id(key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject):
#         """
#         Obtiene el ID del layer apropiado para un elemento.
#         Prioriza layers específicos guardados sobre el layer por defecto.
#         """
#         doc = so.coord_input.GetInputViewDocument()
#         layer_id = 0
#         # Obtener ID del layer por defecto
#         if so.default_layers:
#             default_id = LayerService.GetIDByShortName(so.default_layers.get("default", ""), doc) # type: ignore
#             if default_id:
#                 layer_id = default_id

#         # Priorizar layer específico guardado
#         if hasattr(so, "applied_layers") and so.applied_layers:
#             layer_data = so.applied_layers.get(key_applied_layer_attr, None)
#             if layer_data and isinstance(layer_data, dict):
#                 layer_name_str = layer_data.get("layer")
#                 if layer_name_str:
#                     specific_id = LayerService.GetIDByShortName(layer_name_str, doc) # type: ignore
#                     if specific_id:
#                         layer_id = specific_id
#         return layer_id

