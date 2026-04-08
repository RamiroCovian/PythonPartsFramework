# -*- coding: utf-8 -*-
"""
Controlador reutilizable para puntos libres de ElementosDefinidos.

Encapsula:
- estado de selección/drag/doble clic,
- preview 3D/2D de puntos libres y cursor,
- bridge paleta <-> punto libre seleccionado,
- y utilidades de guardado/restauración de estado efímero.
"""
from __future__ import annotations

import time
import math
from typing import Any, Callable, Optional

from .editing import find_hover_free_point
from .handlers import (
    apply_free_point_rotation_to_palette,
    handle_click_add_free_point,
    update_free_point_rotation_from_palette,
)
from .interaction import (
    get_rotation_value,
    build_rotation_matrix,
    draw_preview_models,
    draw_highlight_preview,
    draw_rotation_label,
)

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
except Exception:
    AllplanGeo = None
    AllplanBaseElements = None


FREE_POINT_INTERACTION_STATE_KEYS = (
    "next_click_adds_free_point",
    "free_point_selected_index",
    "free_point_dragging",
    "free_point_drag_index",
    "pending_free_point_drag_index",
    "free_point_drag_start_position",
    "_last_free_point_click_time",
    "_last_free_point_click_index",
)


def ensure_free_point_interaction_state(intr: Any, script_object: Any = None) -> None:
    """
    Inicializa en el interactor el estado efímero usado por puntos libres.

    Asegura que existan las banderas e índices necesarios para selección,
    arrastre, doble clic y modo "siguiente clic añade punto".
    """
    if intr is None:
        return
    if script_object is not None:
        intr.script_object = script_object
    intr.next_click_adds_free_point = bool(
        getattr(intr, "next_click_adds_free_point", False)
    )
    intr.free_point_selected_index = getattr(intr, "free_point_selected_index", None)
    intr.free_point_dragging = bool(getattr(intr, "free_point_dragging", False))
    intr.free_point_drag_index = getattr(intr, "free_point_drag_index", None)
    intr.pending_free_point_drag_index = getattr(
        intr, "pending_free_point_drag_index", None
    )
    intr.free_point_drag_start_position = getattr(
        intr, "free_point_drag_start_position", None
    )
    intr._last_free_point_click_time = getattr(
        intr, "_last_free_point_click_time", None
    )
    intr._last_free_point_click_index = getattr(
        intr, "_last_free_point_click_index", None
    )


def capture_free_point_interaction_state(intr: Any) -> dict:
    """
    Captura el estado efímero actual de puntos libres del interactor.

    Devuelve un `dict` serializable en memoria con selección, arrastre y
    contexto de doble clic para poder restaurarlo después.
    """
    ensure_free_point_interaction_state(intr)
    state = {}
    for key in FREE_POINT_INTERACTION_STATE_KEYS:
        state[key] = getattr(intr, key, None)
    return state


def apply_free_point_interaction_state(intr: Any, state: Optional[dict]) -> None:
    """
    Restaura en el interactor un estado efímero previamente capturado.

    Se usa cuando el script necesita reaplicar el contexto de interacción
    después de reconstruir el interactor o el script object.
    """
    ensure_free_point_interaction_state(intr)
    if not state:
        return
    for key in FREE_POINT_INTERACTION_STATE_KEYS:
        if key in state:
            setattr(intr, key, state.get(key))


def save_free_point_interaction_state(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_free_point_interaction_state",
) -> dict:
    """
    Guarda en el script object el estado efímero actual de puntos libres.

    No persiste geometría ni datos de negocio; solo conserva el contexto de
    interacción necesario para continuar editando.
    """
    state = capture_free_point_interaction_state(intr)
    if script_object is not None:
        setattr(script_object, attr_name, state)
    return state


def restore_free_point_interaction_state(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_free_point_interaction_state",
) -> dict:
    """
    Restaura desde el script object el estado efímero de puntos libres.

    Devuelve el estado recuperado para facilitar trazas o inspección externa.
    """
    state = getattr(script_object, attr_name, None) if script_object is not None else None
    apply_free_point_interaction_state(intr, state)
    return state or {}


def prepare_free_point_event(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_free_point_interaction_state",
) -> dict:
    """
    Normaliza el estado antes de eventos relacionados con puntos libres.

    Primero restaura lo que hubiera guardado y luego vuelve a guardarlo,
    dejando el contexto consistente antes de disparar `1017/1018`.
    """
    restore_free_point_interaction_state(script_object, intr, attr_name=attr_name)
    return save_free_point_interaction_state(script_object, intr, attr_name=attr_name)


def refresh_free_point_preview(intr: Any, point: Any = None) -> None:
    """
    Fuerza un refresco del preview asociado al interactor.

    Si recibe `point`, lo usa como posición de redraw. Si no, intenta usar el
    punto actual del cursor o, en último término, refresca sin punto explícito.
    """
    if intr is None or not getattr(intr, "_draw_preview", None):
        return
    try:
        if point is not None:
            intr._draw_preview(point)
            return
        cp = getattr(intr, "current_point", None)
        coord_input = getattr(intr, "coord_input", None)
        if (
            cp is not None
            and coord_input is not None
            and getattr(coord_input, "GetCurrentPoint", None)
        ):
            pt = coord_input.GetCurrentPoint(cp)
            if pt is not None and getattr(pt, "GetPoint", None):
                intr._draw_preview(pt.GetPoint())
                return
        intr._draw_preview(None)
    except Exception:
        pass


def sync_selected_free_point_rotation_from_palette(
    script_object: Any,
    intr: Any,
) -> bool:
    """
    Copia desde la paleta la rotación del punto libre actualmente seleccionado.

    Devuelve `True` si existía un punto seleccionado válido y se actualizó.
    """
    if script_object is None or intr is None:
        return False
    idx = getattr(intr, "free_point_selected_index", None)
    free_list = getattr(script_object, "free_placed_points", None) or []
    if idx is None or not (0 <= idx < len(free_list)):
        return False
    update_free_point_rotation_from_palette(script_object, idx)
    save_free_point_interaction_state(script_object, intr)
    return True


def handle_free_point_property_change(
    script_object: Any,
    intr: Any,
    name: str,
    rotation_names: tuple[str, ...] = ("RotX", "RotY", "RotZ", "ElementRotX", "ElementRotY", "ElementRotZ"),
) -> bool:
    """
    Reacciona a cambios de propiedades de rotación en la paleta.

    Si `name` corresponde a un ángulo de rotación, sincroniza el punto libre
    seleccionado y refresca el preview.
    """
    if name not in rotation_names:
        return False
    changed = sync_selected_free_point_rotation_from_palette(script_object, intr)
    refresh_free_point_preview(intr)
    return changed


def _get_input_point(intr: Any, mouse_msg: Any, pnt: Any, msg_info: Any):
    """Resuelve el punto de entrada actual a partir del `CoordinateInput`."""
    coord_input = getattr(intr, "coord_input", None)
    if coord_input is None:
        return None
    current_point = getattr(intr, "current_point", None)
    points = bool(getattr(intr, "points", []))
    if current_point is None:
        return coord_input.GetInputPoint(mouse_msg, pnt, msg_info, points).GetPoint()
    return coord_input.GetInputPoint(
        mouse_msg,
        pnt,
        msg_info,
        current_point,
        points,
    ).GetPoint()


def _is_left_click(intr: Any, mouse_msg: Any) -> bool:
    """
    Detecta un clic izquierdo real evitando confundir movimientos con clics.

    Allplan puede enviar `mouse_msg` como entero o como objeto con `Button`.
    """
    coord_input = getattr(intr, "coord_input", None)
    if coord_input is not None and coord_input.IsMouseMove(mouse_msg):
        return False
    if mouse_msg == 1:
        return True
    return getattr(mouse_msg, "Button", 1) == 1


def handle_free_point_mouse_message(
    intr: Any,
    script_object: Any,
    mouse_msg: Any,
    pnt: Any,
    msg_info: Any,
    instalacion: str,
    draw_preview_cb: Optional[Callable[[Any], None]] = None,
    debug_prefix: str = "[ED]",
) -> Optional[bool]:
    """
    Gestiona toda la interacción de mouse asociada a puntos libres.

    Incluye:
    - selección y deselección,
    - doble clic para recolocar,
    - arrastre con umbral,
    - modo "siguiente clic añade punto",
    - y refresco visual después de cada cambio.

    Devuelve:
    - `True` si el evento quedó manejado por este controller,
    - `None` si no aplicaba y el script llamador debe seguir con su flujo.
    """
    if intr is None or script_object is None:
        return None

    ensure_free_point_interaction_state(intr, script_object)
    free_list = getattr(script_object, "free_placed_points", None) or []
    coord_input = getattr(intr, "coord_input", None)
    is_move = bool(coord_input and coord_input.IsMouseMove(mouse_msg))
    is_left_click = _is_left_click(intr, mouse_msg)

    if is_move:
        pending_idx = getattr(intr, "pending_free_point_drag_index", None)
        start_pos = getattr(intr, "free_point_drag_start_position", None)
        if (
            not getattr(intr, "free_point_dragging", False)
            and pending_idx is not None
            and start_pos is not None
            and coord_input
        ):
            try:
                raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
                dx = raw_pnt.X - getattr(start_pos, "X", 0.0)
                dy = raw_pnt.Y - getattr(start_pos, "Y", 0.0)
                dz = raw_pnt.Z - getattr(start_pos, "Z", 0.0)
                if math.sqrt(dx * dx + dy * dy + dz * dz) > 50.0:
                    intr.free_point_dragging = True
                    intr.free_point_drag_index = pending_idx
                    save_free_point_interaction_state(script_object, intr)
            except Exception:
                pass

        if getattr(intr, "free_point_dragging", False) and coord_input:
            try:
                idx = getattr(intr, "free_point_drag_index", None)
                if idx is not None and 0 <= idx < len(free_list):
                    raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
                    fp = free_list[idx]
                    old_pos = fp.get("pos")
                    z_abs = float(getattr(old_pos, "Z", raw_pnt.Z) or raw_pnt.Z)
                    fp["pos"] = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, z_abs)
                    free_list[idx] = fp
                    save_free_point_interaction_state(script_object, intr)
                    (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                    return True
            except Exception:
                pass

    if is_left_click and getattr(intr, "free_point_dragging", False):
        intr.free_point_dragging = False
        intr.free_point_drag_index = None
        intr.pending_free_point_drag_index = None
        intr.free_point_drag_start_position = None
        try:
            if hasattr(script_object, "_save_state_to_build_ele"):
                script_object._save_state_to_build_ele()
        except Exception:
            pass
        save_free_point_interaction_state(script_object, intr)
        try:
            raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
        except Exception:
            raw_pnt = None
        (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
        return True

    if (
        is_move
        and not getattr(intr, "next_click_adds_free_point", False)
        and not getattr(intr, "free_point_dragging", False)
        and free_list
        and coord_input
    ):
        try:
            cursor_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
            (draw_preview_cb or refresh_free_point_preview)(cursor_pnt)
            return True
        except Exception:
            pass

    if (
        is_left_click
        and not getattr(intr, "next_click_adds_free_point", False)
        and free_list
        and coord_input
    ):
        try:
            raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
            idx_hit = find_hover_free_point(raw_pnt, free_list, 40.0)
            if idx_hit == -1:
                intr.free_point_selected_index = None
                intr.pending_free_point_drag_index = None
                intr.free_point_drag_start_position = None
                intr._last_free_point_click_time = None
                intr._last_free_point_click_index = None
                save_free_point_interaction_state(script_object, intr)
                (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                return True

            now = time.time()
            last_time = getattr(intr, "_last_free_point_click_time", None)
            last_idx = getattr(intr, "_last_free_point_click_index", None)

            if last_time is not None and last_idx == idx_hit and (now - last_time) < 0.4:
                intr._last_free_point_click_time = None
                intr._last_free_point_click_index = None
                fp = free_list[idx_hit]
                old_pos = fp.get("pos")
                z_abs = float(getattr(old_pos, "Z", raw_pnt.Z) or raw_pnt.Z)
                fp["pos"] = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, z_abs)
                free_list[idx_hit] = fp
                intr.free_point_selected_index = idx_hit
                intr.pending_free_point_drag_index = None
                intr.free_point_drag_start_position = None
                try:
                    if hasattr(script_object, "_save_state_to_build_ele"):
                        script_object._save_state_to_build_ele()
                except Exception:
                    pass
                save_free_point_interaction_state(script_object, intr)
                (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                return True

            if getattr(intr, "free_point_selected_index", None) == idx_hit:
                intr.free_point_selected_index = None
                intr.pending_free_point_drag_index = None
                intr.free_point_drag_start_position = None
                intr._last_free_point_click_time = None
                intr._last_free_point_click_index = None
                save_free_point_interaction_state(script_object, intr)
                (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                return True

            intr._last_free_point_click_time = now
            intr._last_free_point_click_index = idx_hit
            intr.free_point_selected_index = idx_hit
            apply_free_point_rotation_to_palette(script_object, idx_hit)
            intr.free_point_dragging = False
            intr.free_point_drag_index = None
            intr.pending_free_point_drag_index = idx_hit
            intr.free_point_drag_start_position = AllplanGeo.Point3D(
                raw_pnt.X, raw_pnt.Y, raw_pnt.Z
            )
            save_free_point_interaction_state(script_object, intr)
            (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
            return True
        except Exception as ex:
            print(f"{debug_prefix} Error seleccionando punto libre: {ex}")

    if getattr(intr, "next_click_adds_free_point", False):
        try:
            if is_move and coord_input:
                raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
                (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                return True
            if is_left_click and not is_move and coord_input:
                raw_pnt = _get_input_point(intr, mouse_msg, pnt, msg_info)
                intr.next_click_adds_free_point = False
                print(f"{debug_prefix} Alta punto libre consumida por módulo")
                handle_click_add_free_point(intr, script_object, raw_pnt, instalacion)
                save_free_point_interaction_state(script_object, intr)
                (draw_preview_cb or refresh_free_point_preview)(raw_pnt)
                return True
        except Exception as ex:
            print(f"{debug_prefix} Error añadiendo punto libre: {ex}")

    return None


def draw_free_point_preview(
    intr: Any,
    script_object: Any,
    current_pnt: Any,
    instalacion: str,
    get_model_list: Callable[[Any, Any, Any, str], list[Any]],
    fallback_preview_factory: Optional[Callable[[Any, Any], list[Any]]] = None,
    debug_prefix: str = "[ED]",
) -> bool:
    """
    Dibuja el preview completo de puntos libres y del cursor en modo alta.

    Este método centraliza:
    - preview 3D real de puntos ya colocados,
    - resaltado del punto seleccionado,
    - etiqueta de rotación,
    - y preview del elemento bajo el cursor cuando `1017` está activo.
    """
    if intr is None or script_object is None:
        return False
    ensure_free_point_interaction_state(intr, script_object)

    build_ele = getattr(script_object, "build_ele", None)
    coord_input = getattr(intr, "coord_input", None)
    doc = coord_input.GetInputViewDocument() if coord_input else None
    overlay = []
    free_list = getattr(script_object, "free_placed_points", None) or []
    fp_sel_idx = getattr(intr, "free_point_selected_index", None)

    if (
        build_ele is not None
        and fp_sel_idx is not None
        and 0 <= fp_sel_idx < len(free_list)
    ):
        try:
            update_free_point_rotation_from_palette(script_object, fp_sel_idx)
        except Exception:
            pass

    for idx, fp in enumerate(free_list):
        pos = fp.get("pos")
        if pos is None or not hasattr(pos, "X"):
            continue

        model_list = []
        if doc is not None:
            model_list = get_model_list(
                script_object,
                build_ele,
                doc,
                fp.get("element_type", "t_sortida"),
            )
        if model_list:
            mat = build_rotation_matrix(
                pos,
                float(fp.get("rot_x", 0.0) or 0.0),
                float(fp.get("rot_y", 0.0) or 0.0),
                float(fp.get("rot_z", 0.0) or 0.0),
            )
            draw_preview_models(doc, mat, model_list)
            if idx == fp_sel_idx:
                draw_highlight_preview(
                    doc,
                    mat,
                    model_list,
                    base_props=getattr(intr, "com_prop", None),
                )
        elif callable(fallback_preview_factory):
            overlay.extend(fallback_preview_factory(pos, intr))

    if doc is not None and fp_sel_idx is not None and 0 <= fp_sel_idx < len(free_list):
        try:
            fp_sel = free_list[fp_sel_idx]
            pos = fp_sel.get("pos")
            if pos is not None and hasattr(pos, "X"):
                draw_rotation_label(
                    doc,
                    pos,
                    float(fp_sel.get("rot_x", 0.0) or 0.0),
                    float(fp_sel.get("rot_y", 0.0) or 0.0),
                    float(fp_sel.get("rot_z", 0.0) or 0.0),
                )
        except Exception as ex:
            print(f"{debug_prefix} No se pudo crear etiqueta de rotación: {ex}")

    if getattr(intr, "next_click_adds_free_point", False) and current_pnt is not None:
        cursor_preview_added = False
        if doc is not None:
            try:
                element_type = "t_sortida"
                if build_ele is not None:
                    try:
                        from .palette import get_defined_element_settings

                        element_type = get_defined_element_settings(build_ele, instalacion)[0]
                    except Exception:
                        pass
                model_list = get_model_list(
                    script_object,
                    build_ele,
                    doc,
                    element_type,
                )
                if model_list:
                    mat = build_rotation_matrix(
                        current_pnt,
                        get_rotation_value(build_ele, "RotX", "ElementRotX"),
                        get_rotation_value(build_ele, "RotY", "ElementRotY"),
                        get_rotation_value(build_ele, "RotZ", "ElementRotZ"),
                    )
                    draw_preview_models(doc, mat, model_list)
                    cursor_preview_added = True
            except Exception as ex:
                print(f"{debug_prefix} Error dibujando preview cursor: {ex}")
        if not cursor_preview_added and callable(fallback_preview_factory):
            overlay.extend(fallback_preview_factory(current_pnt, intr))

    if overlay and doc is not None and AllplanGeo is not None and AllplanBaseElements is not None:
        AllplanBaseElements.DrawElementPreview(
            doc,
            AllplanGeo.Matrix3D(),
            overlay,
            False,
            None,
        )
    return True
