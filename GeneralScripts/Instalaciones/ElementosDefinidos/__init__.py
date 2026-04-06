# -*- coding: utf-8 -*-
"""
ElementosDefinidos: módulo base para elementos definidos de la instalación.

- base.py: BaseDefinedElement, BaseMacroElement, CallbackDefinedElement.
- catalogo.py: catálogo por instalación, validación, ValueList para UI.
- handlers.py: eventos 1015–1018 (start_element_point_capture, add_defined_element_marker, on_anadir_punto_libre, on_finalizar_puntos_libres, etc.).
- capture.py: ElementPointCaptureMixin para usar con PolylineInteractor.
- editing.py: find_hover_free_point, get_index_to_select_after_add.
- palette.py: get_defined_element_settings, get_tipo_punto_libre_flag, get_free_point_selection_tolerance.
- preview.py: create_point_marker_geometry, draw_marker_for_element_type, make_circle_polyline_for_marker.
- serialization.py: serialize_element_markers, deserialize_element_markers, serialize_free_placed_points, deserialize_free_placed_points.
- creation.py: create_elements_from_free_placed_points, iterate_element_markers.

Uso desde fontaneria (u otro script):
  from ElementosDefinidos import (
      get_defined_element_settings,
      start_element_point_capture,
      add_defined_element_marker,
      create_point_marker_geometry,
      draw_marker_for_element_type,
  )
  from ElementosDefinidos.handlers import start_element_point_capture, add_defined_element_marker, ...
  from ElementosDefinidos.palette import get_defined_element_settings, get_tipo_punto_libre_flag, ...
"""
from .base import (
    POSIBLES_FUNCIONES,
    FUNCION_TO_ROLE,
    BaseDefinedElement,
    BaseMacroElement,
    CallbackDefinedElement,
)
from .catalogo import (
    get_funciones_por_elemento,
    get_elementos_para_instalacion,
    get_value_list_elementos,
    get_value_list_tipo_punto,
    validar_ubicacion_elemento,
    label_a_key_agua,
    label_tipo_punto_to_funcion,
    LABELS_AGUA,
    LABELS_FUNCION,
    T_SORTIDA,
    COLZE_BASE,
    CLAU_DE_PAS,
    TAPON,
)
from .capture import ElementPointCaptureMixin
from .editing import find_hover_free_point, get_index_to_select_after_add
from .palette import (
    get_defined_element_settings,
    get_free_point_type_flag,
    get_free_point_selection_tolerance,
    get_element_z_abs,
    get_element_point_mode,
)
from .preview import (
    create_point_marker_geometry,
    draw_marker_for_element_type,
    make_circle_polyline_for_marker,
)
from .serialization import (
    point_to_dict,
    point_from_dict,
    serialize_element_markers,
    deserialize_element_markers,
    serialize_free_placed_points,
    deserialize_free_placed_points,
)
from .handlers import (
    start_element_point_capture,
    handle_element_point_capture_click,
    add_defined_element_marker,
    add_intermediate_element_at_point,
    on_anadir_punto_libre,
    on_finalizar_puntos_libres,
    handle_click_add_free_point,
    start_macro_point_capture,
    add_macro_library_marker,
    detect_common_user_points_between_paths,
)
from .creation import (
    create_elements_from_free_placed_points,
    iterate_element_markers,
)

__all__ = [
    "find_hover_free_point",
    "get_index_to_select_after_add",
    "ElementPointCaptureMixin",
    "POSIBLES_FUNCIONES",
    "FUNCION_TO_ROLE",
    "BaseDefinedElement",
    "BaseMacroElement",
    "CallbackDefinedElement",
    "get_funciones_por_elemento",
    "get_elementos_para_instalacion",
    "get_value_list_elementos",
    "get_value_list_tipo_punto",
    "validar_ubicacion_elemento",
    "label_a_key_agua",
    "label_tipo_punto_to_funcion",
    "LABELS_AGUA",
    "LABELS_FUNCION",
    "T_SORTIDA",
    "COLZE_BASE",
    "CLAU_DE_PAS",
    "TAPON",
    "get_defined_element_settings",
    "get_free_point_type_flag",
    "get_free_point_selection_tolerance",
    "get_element_z_abs",
    "get_element_point_mode",
    "create_point_marker_geometry",
    "draw_marker_for_element_type",
    "make_circle_polyline_for_marker",
    "point_to_dict",
    "point_from_dict",
    "serialize_element_markers",
    "deserialize_element_markers",
    "serialize_free_placed_points",
    "deserialize_free_placed_points",
    "start_element_point_capture",
    "handle_element_point_capture_click",
    "add_defined_element_marker",
    "add_intermediate_element_at_point",
    "on_anadir_punto_libre",
    "on_finalizar_puntos_libres",
    "handle_click_add_free_point",
    "start_macro_point_capture",
    "add_macro_library_marker",
    "create_elements_from_free_placed_points",
    "iterate_element_markers",
    "detect_common_user_points_between_paths",
]
