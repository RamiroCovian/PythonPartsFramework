# -*- coding: utf-8 -*-
"""
Controlador reutilizable para `element_markers`.

Encapsula:
- selección y deselección,
- arrastre con umbral,
- sincronización de rotación con la paleta,
- preview del marker y del modelo 3D asociado,
- y creación final de elementos desde markers persistidos.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Optional

from .interaction import (
    find_hover_entry,
    sync_rotation_from_palette,
    sync_rotation_to_palette,
    build_rotation_matrix,
    draw_preview_models,
    draw_selected_defined_element_preview,
    make_selection_common_properties,
)
from .handlers import _try_refresh_palette

try:
    import NemAll_Python_Geometry as AllplanGeo
except Exception:
    AllplanGeo = None


ELEMENT_MARKER_INTERACTION_STATE_KEYS = (
    "element_marker_selected_index",
    "pending_element_marker_drag_index",
    "element_marker_dragging",
    "element_marker_drag_start_position",
)


def ensure_element_marker_interaction_state(intr: Any, script_object: Any = None) -> None:
    """
    Inicializa en el interactor el estado efímero de selección y arrastre de markers.

    Asegura que existan los índices y banderas necesarios para trabajar con el
    flujo de `1015/1016` sin depender del script concreto.
    """
    if intr is None:
        return
    if script_object is not None:
        intr.script_object = script_object
    intr.element_marker_selected_index = getattr(
        intr, "element_marker_selected_index", None
    )
    intr.pending_element_marker_drag_index = getattr(
        intr, "pending_element_marker_drag_index", None
    )
    intr.element_marker_dragging = bool(
        getattr(intr, "element_marker_dragging", False)
    )
    intr.element_marker_drag_start_position = getattr(
        intr, "element_marker_drag_start_position", None
    )


def capture_element_marker_interaction_state(intr: Any) -> dict:
    """
    Captura el estado efímero actual de interacción con markers.

    Devuelve un `dict` en memoria para poder restaurar selección y drag
    después de recreaciones del interactor o del script object.
    """
    ensure_element_marker_interaction_state(intr)
    state = {}
    for key in ELEMENT_MARKER_INTERACTION_STATE_KEYS:
        state[key] = getattr(intr, key, None)
    return state


def apply_element_marker_interaction_state(intr: Any, state: Optional[dict]) -> None:
    """
    Restaura en el interactor un estado efímero previamente capturado.

    No altera la lista de markers; solo recompone el contexto visual y de
    edición asociado a ellos.
    """
    ensure_element_marker_interaction_state(intr)
    if not state:
        return
    for key in ELEMENT_MARKER_INTERACTION_STATE_KEYS:
        if key in state:
            setattr(intr, key, state.get(key))


def save_element_marker_interaction_state(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_element_marker_interaction_state",
) -> dict:
    """
    Guarda en el script object el estado efímero actual de markers.

    Está pensado para sobrevivir a eventos que puedan reconstruir el script
    manteniendo la interacción del usuario.
    """
    state = capture_element_marker_interaction_state(intr)
    if script_object is not None:
        setattr(script_object, attr_name, state)
    return state


def restore_element_marker_interaction_state(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_element_marker_interaction_state",
) -> dict:
    """
    Restaura desde el script object el estado efímero de markers.

    Devuelve el estado recuperado para facilitar inspección o trazas.
    """
    state = getattr(script_object, attr_name, None) if script_object is not None else None
    apply_element_marker_interaction_state(intr, state)
    return state or {}


def prepare_element_marker_event(
    script_object: Any,
    intr: Any,
    attr_name: str = "_ed_element_marker_interaction_state",
) -> dict:
    """
    Normaliza el estado antes de eventos relacionados con markers.

    Se usa antes de `1015/1016` para que el contexto de selección/drag quede
    consistente aunque el script sea recreado.
    """
    restore_element_marker_interaction_state(script_object, intr, attr_name=attr_name)
    return save_element_marker_interaction_state(script_object, intr, attr_name=attr_name)


def apply_element_marker_rotation_to_palette(
    build_ele: Any,
    marker: dict,
    script_object: Any = None,
) -> None:
    """
    Carga en la paleta los ángulos guardados dentro de un marker seleccionado.

    Esto permite que el usuario vea y edite desde UI la rotación del elemento
    que ya está colocado.
    """
    sync_rotation_to_palette(
        build_ele,
        marker,
        (
            ("ElementRotX", "rot_x"),
            ("ElementRotY", "rot_y"),
            ("ElementRotZ", "rot_z"),
        ),
    )
    _try_refresh_palette(script_object)


def update_element_marker_rotation_from_palette(
    build_ele: Any,
    marker: dict,
) -> None:
    """
    Actualiza un marker leyendo los ángulos actuales desde la paleta.

    Busca primero `ElementRot*` y usa `Rot*` como fallback para mantener
    compatibilidad entre instalaciones.
    """
    sync_rotation_from_palette(
        build_ele,
        marker,
        (
            ("ElementRotX", "rot_x", "RotX"),
            ("ElementRotY", "rot_y", "RotY"),
            ("ElementRotZ", "rot_z", "RotZ"),
        ),
    )


def sync_last_element_marker_rotation(script_object: Any, intr: Any = None) -> None:
    """
    Aplica al último marker agregado la rotación actual de la paleta y lo selecciona.

    Es útil inmediatamente después de crear un marker, para que quede listo
    para edición visual sin pasos extra.
    """
    markers = getattr(script_object, "element_markers", None) or []
    if not markers:
        return
    marker = markers[-1]
    update_element_marker_rotation_from_palette(
        getattr(script_object, "build_ele", None), marker
    )
    if intr is not None:
        intr.element_marker_selected_index = len(markers) - 1
        save_element_marker_interaction_state(script_object, intr)


def handle_element_marker_property_change(
    script_object: Any,
    intr: Any,
    name: str,
    rotation_names: tuple[str, ...] = (
        "ElementRotX",
        "ElementRotY",
        "ElementRotZ",
        "RotX",
        "RotY",
        "RotZ",
    ),
) -> bool:
    """
    Reacciona a cambios de rotación hechos por el usuario en la paleta.

    Si existe un marker seleccionado, actualiza sus ángulos guardados y
    devuelve `True`.
    """
    if name not in rotation_names or script_object is None or intr is None:
        return False
    markers = getattr(script_object, "element_markers", None) or []
    idx = getattr(intr, "element_marker_selected_index", None)
    if idx is None or not (0 <= idx < len(markers)):
        return False
    update_element_marker_rotation_from_palette(
        getattr(script_object, "build_ele", None),
        markers[idx],
    )
    save_element_marker_interaction_state(script_object, intr)
    return True


def handle_element_marker_mouse_message(
    intr: Any,
    script_object: Any,
    mouse_msg: Any,
    pnt: Any,
    msg_info: Any,
    draw_preview_cb: Optional[Callable[[Any], None]] = None,
    tolerance_mm: float = 60.0,
    drag_threshold_mm: float = 50.0,
    debug_prefix: str = "[ED]",
) -> Optional[bool]:
    """
    Gestiona la interacción de mouse para `element_markers`.

    Incluye:
    - selección y deselección,
    - arrastre con umbral,
    - sincronización paleta <-> selección,
    - y refresco visual tras cada cambio.

    Devuelve:
    - `True` si el evento quedó resuelto por este controller,
    - `None` si el flujo debe continuar en el script llamador.
    """
    if intr is None or script_object is None:
        return None

    ensure_element_marker_interaction_state(intr, script_object)
    coord_input = getattr(intr, "coord_input", None)
    build_ele = getattr(script_object, "build_ele", None)
    markers = getattr(script_object, "element_markers", None) or []
    is_move = bool(coord_input and coord_input.IsMouseMove(mouse_msg))
    is_left_click = getattr(mouse_msg, "Button", 1) == 1

    if is_move:
        pending_idx = getattr(intr, "pending_element_marker_drag_index", None)
        start_pos = getattr(intr, "element_marker_drag_start_position", None)
        if (
            not getattr(intr, "element_marker_dragging", False)
            and pending_idx is not None
            and start_pos is not None
            and 0 <= pending_idx < len(markers)
            and coord_input
        ):
            try:
                raw_pnt = coord_input.GetInputPoint(
                    mouse_msg,
                    pnt,
                    msg_info,
                    getattr(intr, "current_point", None),
                    bool(getattr(intr, "points", [])),
                ).GetPoint()
                dx = raw_pnt.X - getattr(start_pos, "X", 0.0)
                dy = raw_pnt.Y - getattr(start_pos, "Y", 0.0)
                dz = raw_pnt.Z - getattr(start_pos, "Z", 0.0)
                if math.sqrt(dx * dx + dy * dy + dz * dz) > drag_threshold_mm:
                    intr.element_marker_dragging = True
                    save_element_marker_interaction_state(script_object, intr)
            except Exception:
                pass

        if getattr(intr, "element_marker_dragging", False) and coord_input:
            try:
                idx = getattr(intr, "pending_element_marker_drag_index", None)
                if idx is not None and 0 <= idx < len(markers):
                    raw_pnt = coord_input.GetInputPoint(
                        mouse_msg,
                        pnt,
                        msg_info,
                        getattr(intr, "current_point", None),
                        bool(getattr(intr, "points", [])),
                    ).GetPoint()
                    marker = markers[idx]
                    old_pos = marker.get("pos")
                    z_abs = float(getattr(old_pos, "Z", raw_pnt.Z) or raw_pnt.Z)
                    marker["pos"] = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, z_abs)
                    update_element_marker_rotation_from_palette(build_ele, marker)
                    save_element_marker_interaction_state(script_object, intr)
                    if callable(draw_preview_cb):
                        draw_preview_cb(raw_pnt)
                    return True
            except Exception as ex:
                print(f"{debug_prefix} Error arrastrando marker: {ex}")

    if is_left_click and getattr(intr, "element_marker_dragging", False):
        try:
            intr.element_marker_dragging = False
            intr.pending_element_marker_drag_index = None
            intr.element_marker_drag_start_position = None
            if hasattr(script_object, "_save_state_to_build_ele"):
                script_object._save_state_to_build_ele()
            save_element_marker_interaction_state(script_object, intr)
            if callable(draw_preview_cb) and coord_input:
                raw_pnt = coord_input.GetInputPoint(
                    mouse_msg,
                    pnt,
                    msg_info,
                    getattr(intr, "current_point", None),
                    bool(getattr(intr, "points", [])),
                ).GetPoint()
                draw_preview_cb(raw_pnt)
            return True
        except Exception:
            pass

    if is_left_click:
        try:
            if markers and coord_input:
                raw_pnt = coord_input.GetInputPoint(
                    mouse_msg,
                    pnt,
                    msg_info,
                    getattr(intr, "current_point", None),
                    bool(getattr(intr, "points", [])),
                ).GetPoint()
                idx_hit = find_hover_entry(raw_pnt, markers, tolerance_mm)
                if idx_hit != -1:
                    intr.element_marker_selected_index = idx_hit
                    intr.pending_element_marker_drag_index = idx_hit
                    intr.element_marker_drag_start_position = AllplanGeo.Point3D(
                        raw_pnt.X, raw_pnt.Y, raw_pnt.Z
                    )
                    apply_element_marker_rotation_to_palette(
                        build_ele,
                        markers[idx_hit],
                        script_object,
                    )
                    save_element_marker_interaction_state(script_object, intr)
                    if callable(draw_preview_cb):
                        draw_preview_cb(raw_pnt)
                    return True
                if getattr(intr, "element_marker_selected_index", None) is not None:
                    intr.element_marker_selected_index = None
                    intr.pending_element_marker_drag_index = None
                    intr.element_marker_drag_start_position = None
                    save_element_marker_interaction_state(script_object, intr)
                    if callable(draw_preview_cb):
                        draw_preview_cb(raw_pnt)
                    return True
        except Exception as ex:
            print(f"{debug_prefix} Error seleccionando marker: {ex}")

    return None


def draw_element_markers_preview(
    intr: Any,
    script_object: Any,
    get_model_list: Callable[[Any, Any, Any, str], list[Any]],
    fallback_preview_factory: Callable[[Any, str, Any], list[Any]],
    selected_marker_factory: Optional[Callable[[Any, Any], list[Any]]] = None,
    selected_fallback_preview_factory: Optional[Callable[[Any, str, Any], list[Any]]] = None,
) -> bool:
    """
    Dibuja el preview completo de `element_markers`.

    Centraliza:
    - preview 3D real cuando existe `model_list`,
    - fallback geométrico 2D cuando no existe,
    - resaltado del marker seleccionado,
    - y marcador auxiliar de selección si la instalación lo necesita.
    """
    if intr is None or script_object is None:
        return False
    ensure_element_marker_interaction_state(intr, script_object)
    doc = intr.coord_input.GetInputViewDocument() if getattr(intr, "coord_input", None) else None
    build_ele = getattr(script_object, "build_ele", None)
    overlay = []
    selected_idx = getattr(intr, "element_marker_selected_index", None)
    markers = getattr(script_object, "element_markers", None) or []

    if build_ele is not None and selected_idx is not None and 0 <= selected_idx < len(markers):
        try:
            update_element_marker_rotation_from_palette(build_ele, markers[selected_idx])
        except Exception:
            pass

    for idx, marker in enumerate(markers):
        pos = marker.get("pos")
        element_type = marker.get("element_type", "t_sortida")
        if pos is None or not hasattr(pos, "X"):
            continue
        marker_prop = getattr(intr, "com_prop", None)
        model_list = []
        if doc is not None:
            model_list = get_model_list(script_object, build_ele, doc, element_type)
        if model_list:
            try:
                mat = build_rotation_matrix(
                    pos,
                    float(marker.get("rot_x", 0.0) or 0.0),
                    float(marker.get("rot_y", 0.0) or 0.0),
                    float(marker.get("rot_z", 0.0) or 0.0),
                )
                draw_preview_models(doc, mat, model_list)
                if idx == selected_idx:
                    draw_selected_defined_element_preview(
                        doc,
                        mat,
                        model_list,
                        base_props=marker_prop,
                    )
            except Exception:
                if idx == selected_idx and callable(selected_fallback_preview_factory):
                    overlay.extend(
                        selected_fallback_preview_factory(pos, element_type, marker_prop)
                    )
                else:
                    overlay.extend(fallback_preview_factory(pos, element_type, marker_prop))
        else:
            if idx == selected_idx and callable(selected_fallback_preview_factory):
                overlay.extend(
                    selected_fallback_preview_factory(pos, element_type, marker_prop)
                )
            else:
                overlay.extend(fallback_preview_factory(pos, element_type, marker_prop))

        if idx == selected_idx and callable(selected_marker_factory):
            selection_props = make_selection_common_properties(marker_prop)
            overlay.extend(selected_marker_factory(pos, selection_props))

    if overlay and doc is not None and AllplanGeo is not None:
        import NemAll_Python_BaseElements as AllplanBaseElements

        AllplanBaseElements.DrawElementPreview(
            doc,
            AllplanGeo.Matrix3D(),
            overlay,
            False,
            None,
        )
    return True


def materialize_element_markers(
    script_object: Any,
    create_element_cb: Callable[[Any, Any, Any, str, Any, float, float, float], bool],
) -> int:
    """
    Crea en documento los elementos finales a partir de `element_markers`.

    Recorre todos los markers persistidos y delega la creación concreta al
    callback proporcionado por la instalación.
    """
    markers = getattr(script_object, "element_markers", None) or []
    if not markers:
        return 0
    try:
        doc = script_object.coord_input.GetInputViewDocument()
    except Exception:
        doc = None
    if doc is None:
        return 0

    created = 0
    build_ele = getattr(script_object, "build_ele", None)
    for marker in markers:
        pos = marker.get("pos")
        element_type = str(marker.get("element_type", "t_sortida") or "t_sortida")
        if pos is None or not hasattr(pos, "X"):
            continue
        p_mid = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)
        if create_element_cb(
            script_object,
            build_ele,
            doc,
            element_type,
            p_mid,
            float(marker.get("rot_x", 0.0) or 0.0),
            float(marker.get("rot_y", 0.0) or 0.0),
            float(marker.get("rot_z", 0.0) or 0.0),
        ):
            created += 1
    if created:
        script_object.element_markers = []
    return created
