# -*- coding: utf-8 -*-
"""
Fachada pública para integrar ElementosDefinidos en una instalación.

La idea es que los scripts de instalación no tengan que conocer cada helper
individual del módulo. Esta capa agrupa las operaciones más comunes:
- preparar estado,
- manejar mouse,
- reaccionar a cambios de propiedades,
- dibujar preview,
- y preparar eventos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .free_points_controller import (
    ensure_free_point_interaction_state,
    restore_free_point_interaction_state,
    prepare_free_point_event,
    handle_free_point_property_change,
    handle_free_point_mouse_message,
    draw_free_point_preview,
)
from .element_markers_controller import (
    ensure_element_marker_interaction_state,
    restore_element_marker_interaction_state,
    prepare_element_marker_event,
    handle_element_marker_property_change,
    handle_element_marker_mouse_message,
    draw_element_markers_preview,
)


@dataclass
class DefinedElementsFacadeConfig:
    """
    Configuración mínima para conectar ElementosDefinidos a una instalación.

    El script de instalación aporta sus callbacks concretos de preview y
    fallback, mientras el módulo resuelve la lógica de interacción.
    """

    instalacion: str
    get_model_list: Callable[[Any, Any, Any, str], list[Any]]
    free_point_fallback_preview_factory: Optional[Callable[[Any, Any], list[Any]]] = None
    marker_fallback_preview_factory: Optional[
        Callable[[Any, str, Any], list[Any]]
    ] = None
    marker_selected_fallback_preview_factory: Optional[
        Callable[[Any, str, Any], list[Any]]
    ] = None
    marker_selected_marker_factory: Optional[Callable[[Any, Any], list[Any]]] = None
    mouse_draw_preview_cb: Optional[Callable[[Any], None]] = None
    free_point_debug_prefix: str = "[ED]"
    marker_debug_prefix: str = "[ED]"


def ensure_defined_elements_interaction_state(
    script_object: Any,
    intr: Any,
) -> None:
    """Inicializa y restaura el estado efímero de puntos libres y markers."""
    ensure_free_point_interaction_state(intr, script_object)
    restore_free_point_interaction_state(script_object, intr)
    ensure_element_marker_interaction_state(intr, script_object)
    restore_element_marker_interaction_state(script_object, intr)


def prepare_defined_elements_event(
    script_object: Any,
    intr: Any,
    include_free_points: bool = True,
    include_element_markers: bool = True,
) -> None:
    """Prepara el estado del módulo antes de eventos de paleta o interacción."""
    if include_free_points:
        prepare_free_point_event(script_object, intr)
    if include_element_markers:
        prepare_element_marker_event(script_object, intr)


def handle_defined_elements_property_change(
    script_object: Any,
    intr: Any,
    name: str,
) -> bool:
    """
    Propaga un cambio de propiedad a los controladores activos del módulo.

    Devuelve `True` si al menos uno de los controladores reaccionó al cambio.
    """
    changed_free = handle_free_point_property_change(script_object, intr, name)
    changed_marker = handle_element_marker_property_change(script_object, intr, name)
    return bool(changed_free or changed_marker)


def handle_defined_elements_mouse_message(
    script_object: Any,
    intr: Any,
    mouse_msg: Any,
    pnt: Any,
    msg_info: Any,
    config: DefinedElementsFacadeConfig,
) -> Optional[bool]:
    """
    Orquesta la gestión de mouse del módulo para markers y puntos libres.

    El orden actual da prioridad a `element_markers` y luego a `free_placed_points`.
    """
    marker_handled = handle_element_marker_mouse_message(
        intr,
        script_object,
        mouse_msg,
        pnt,
        msg_info,
        draw_preview_cb=config.mouse_draw_preview_cb,
        debug_prefix=config.marker_debug_prefix,
    )
    if marker_handled is not None:
        return marker_handled

    return handle_free_point_mouse_message(
        intr,
        script_object,
        mouse_msg,
        pnt,
        msg_info,
        config.instalacion,
        draw_preview_cb=config.mouse_draw_preview_cb,
        debug_prefix=config.free_point_debug_prefix,
    )


def draw_defined_elements_preview(
    script_object: Any,
    intr: Any,
    current_pnt: Any,
    config: DefinedElementsFacadeConfig,
) -> bool:
    """Dibuja, en una única llamada, markers y puntos libres del módulo."""
    draw_element_markers_preview(
        intr,
        script_object,
        get_model_list=config.get_model_list,
        fallback_preview_factory=config.marker_fallback_preview_factory,
        selected_fallback_preview_factory=config.marker_selected_fallback_preview_factory,
        selected_marker_factory=config.marker_selected_marker_factory,
    )
    draw_free_point_preview(
        intr,
        script_object,
        current_pnt,
        config.instalacion,
        get_model_list=config.get_model_list,
        fallback_preview_factory=config.free_point_fallback_preview_factory,
        debug_prefix=config.free_point_debug_prefix,
    )
    return True
