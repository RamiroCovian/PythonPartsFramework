# -*- coding: utf-8 -*-
"""
ElementosNoDefinidos: puntos indicativos de camino sin objetos 3D definidos.

Permite marcar inicio, final, bifurcaciones e intermedios en instalaciones
sin objetos 3D por punto. En modo edición, al finalizar (1020) los recorridos
por color/path_key pueden volcarse a ``saved_paths`` del script principal
para tuberías y elementos definidos.

- constants.py: tipos de punto, formas geométricas (círculo, cuadrado, etc.)
- palette.py: get_tipo_camino, get_tipo_punto_orden, get_color_puntos
- preview.py: draw_marker_for_tipo_punto, draw_all_puntos_no_definidos
- serialization.py: serialize/deserialize puntos_no_definidos
- handlers.py: on_anadir_punto_no_definido, on_finalizar_puntos_no_definidos

Uso desde fontaneria (u otro script):
  from ElementosNoDefinidos import (
      draw_all_puntos_no_definidos,
      on_anadir_punto_no_definido,
      on_finalizar_puntos_no_definidos,
  )
"""
from .constants import (
    CAMINO_LIBRE,
    CAMINO_ORDENADO,
    LABELS_TIPO_PUNTO,
    TIPO_BIFURCACION,
    TIPO_FINAL,
    TIPO_INICIO,
    TIPO_INTERMEDIO_LIBRE,
    TIPO_INTERMEDIO_ORDENADO,
    get_shape_for_tipo,
    label_to_tipo,
)
from .handlers import (
    build_nodos_export_data,
    handle_click_add_punto_no_definido,
    materialize_puntos_no_definidos_to_saved_paths,
    on_anadir_punto_no_definido,
    on_finalizar_puntos_no_definidos,
)
from .common_points import detect_common_point_groups
from .palette import (
    color_name_to_id,
    get_common_points_detection_enabled,
    get_common_points_halo_color_id,
    get_common_points_tolerance_mm,
    get_color_puntos,
    get_tipo_camino,
    get_tipo_camino_and_punto,
    get_tipo_punto_orden,
)
from .optimizer_graph import build_optimizer_graph_json
from .preview import (
    create_shape_geometry,
    draw_all_puntos_no_definidos,
    draw_marker_for_tipo_punto,
    draw_preview_at_cursor,
)
from .serialization import (
    deserialize_puntos_no_definidos,
    point_from_dict,
    point_to_dict,
    serialize_puntos_no_definidos,
)

__all__ = [
    "CAMINO_LIBRE",
    "CAMINO_ORDENADO",
    "LABELS_TIPO_PUNTO",
    "TIPO_BIFURCACION",
    "TIPO_FINAL",
    "TIPO_INICIO",
    "TIPO_INTERMEDIO_LIBRE",
    "TIPO_INTERMEDIO_ORDENADO",
    "get_shape_for_tipo",
    "label_to_tipo",
    "color_name_to_id",
    "get_tipo_camino",
    "get_tipo_punto_orden",
    "get_color_puntos",
    "get_common_points_detection_enabled",
    "get_common_points_tolerance_mm",
    "get_common_points_halo_color_id",
    "get_tipo_camino_and_punto",
    "build_optimizer_graph_json",
    "create_shape_geometry",
    "draw_marker_for_tipo_punto",
    "draw_preview_at_cursor",
    "draw_all_puntos_no_definidos",
    "point_to_dict",
    "point_from_dict",
    "serialize_puntos_no_definidos",
    "deserialize_puntos_no_definidos",
    "build_nodos_export_data",
    "on_anadir_punto_no_definido",
    "on_finalizar_puntos_no_definidos",
    "materialize_puntos_no_definidos_to_saved_paths",
    "handle_click_add_punto_no_definido",
    "detect_common_point_groups",
]
