# -*- coding: utf-8 -*-
"""
Helpers genéricos de interacción/preview para ElementosDefinidos.

La idea es que las instalaciones (Agua, Electricidad, etc.) reutilicen
estas utilidades y solo aporten:
- cómo obtener el model_list 3D de cada elemento,
- qué parámetros de paleta usan,
- y cómo materializar el 3D final.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Optional

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
except Exception:
    AllplanGeo = None
    AllplanBaseElements = None
    AllplanBasisElements = None


def get_rotation_value(build_ele: Any, *names: str) -> float:
    """
    Lee el primer parámetro de rotación disponible en la paleta.

    Recorre los nombres recibidos en orden y devuelve su valor convertido a
    `float`. Si no encuentra ninguno válido, devuelve `0.0`.
    """
    for name in names:
        try:
            param = getattr(build_ele, name, None)
            if param is None:
                continue
            raw = getattr(param, "value", param)
            return float(raw or 0.0)
        except Exception:
            continue
    return 0.0


def build_rotation_matrix(
    base_point: Any,
    rot_x: float = 0.0,
    rot_y: float = 0.0,
    rot_z: float = 0.0,
):
    """
    Construye una `Matrix3D` con rotaciones X/Y/Z y traslación al punto base.

    Se usa para dibujar previews 3D o crear el elemento final ya orientado
    en la posición deseada.
    """
    if AllplanGeo is None or base_point is None or not hasattr(base_point, "X"):
        return None

    mat = AllplanGeo.Matrix3D()
    axis_x = AllplanGeo.Line3D(
        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
    )
    axis_y = AllplanGeo.Line3D(
        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
    )
    axis_z = AllplanGeo.Line3D(
        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
    )

    if abs(rot_x) > 1e-6:
        mat_x = AllplanGeo.Matrix3D()
        mat_x.SetRotation(axis_x, AllplanGeo.Angle(math.radians(rot_x)))
        mat = mat_x * mat
    if abs(rot_y) > 1e-6:
        mat_y = AllplanGeo.Matrix3D()
        mat_y.SetRotation(axis_y, AllplanGeo.Angle(math.radians(rot_y)))
        mat = mat_y * mat
    if abs(rot_z) > 1e-6:
        mat_z = AllplanGeo.Matrix3D()
        mat_z.SetRotation(axis_z, AllplanGeo.Angle(math.radians(rot_z)))
        mat = mat_z * mat

    mat.SetTranslation(
        AllplanGeo.Vector3D(base_point.X, base_point.Y, getattr(base_point, "Z", 0.0))
    )
    return mat


def build_rotation_matrix_from_palette(
    build_ele: Any,
    base_point: Any,
    rot_names: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
):
    """
    Variante de `build_rotation_matrix` que toma los ángulos desde la paleta.

    `rot_names` define, por eje, qué nombres de parámetros intentar leer.
    """
    rot_x = get_rotation_value(build_ele, *rot_names[0])
    rot_y = get_rotation_value(build_ele, *rot_names[1])
    rot_z = get_rotation_value(build_ele, *rot_names[2])
    return build_rotation_matrix(base_point, rot_x, rot_y, rot_z)


def sync_rotation_from_palette(
    build_ele: Any,
    target: dict,
    mapping: Iterable[tuple[str, str, Optional[str]]],
) -> None:
    """
    Copia valores de rotación desde la paleta hacia un diccionario destino.

    Se usa típicamente para persistir `rot_x/rot_y/rot_z` dentro de un marker
    o punto libre seleccionado.
    """
    if build_ele is None or not isinstance(target, dict):
        return
    for palette_name, target_key, fallback_name in mapping:
        try:
            names = [palette_name]
            if fallback_name:
                names.append(fallback_name)
            target[target_key] = get_rotation_value(build_ele, *names)
        except Exception:
            pass


def sync_rotation_to_palette(
    build_ele: Any,
    source: dict,
    mapping: Iterable[tuple[str, str]],
) -> None:
    """
    Copia valores de rotación desde un diccionario origen hacia la paleta.

    Sirve para que, al seleccionar un elemento ya colocado, la paleta refleje
    sus ángulos guardados.
    """
    if build_ele is None or not isinstance(source, dict):
        return
    for palette_name, source_key in mapping:
        try:
            param = getattr(build_ele, palette_name, None)
            if param is not None and hasattr(param, "value"):
                param.value = float(source.get(source_key, 0.0) or 0.0)
        except Exception:
            pass


def find_hover_entry(point: Any, entries: list[dict], tolerance_mm: float = 40.0) -> int:
    """
    Busca qué entrada de una lista está más cerca del punto dado.

    Devuelve el índice del elemento dentro de `tolerance_mm`, o `-1` si no hay
    ninguno. Se usa para hover/selección de markers o puntos libres.
    """
    if point is None or not hasattr(point, "X") or not entries:
        return -1
    tol_sq = float(tolerance_mm or 0.0) ** 2
    best_idx = -1
    best_dist = None
    for idx, entry in enumerate(entries):
        pos = entry.get("pos")
        if pos is None or not hasattr(pos, "X"):
            continue
        dx = float(pos.X) - float(point.X)
        dy = float(pos.Y) - float(point.Y)
        dz = float(getattr(pos, "Z", 0.0)) - float(getattr(point, "Z", 0.0))
        dist_sq = dx * dx + dy * dy + dz * dz
        if dist_sq <= tol_sq and (best_dist is None or dist_sq < best_dist):
            best_idx = idx
            best_dist = dist_sq
    return best_idx


def draw_preview_models(doc: Any, matrix: Any, model_list: list[Any]) -> bool:
    """
    Dibuja una lista de modelos 3D en preview usando una matriz dada.

    Es el helper base para mostrar el elemento real en pantalla durante la
    interacción, sin crear todavía elementos definitivos en el documento.
    """
    if (
        doc is None
        or matrix is None
        or not model_list
        or AllplanBaseElements is None
    ):
        return False
    try:
        AllplanBaseElements.DrawElementPreview(doc, matrix, model_list, False, None)
        return True
    except Exception:
        return False


def _make_highlight_properties(base_props: Any, color: int = 3, pen: int = 5):
    """
    Crea `CommonProperties` para resaltar una geometría ya existente.

    Parte de unas propiedades base y fuerza color/trazo visibles para feedback
    visual de selección o hover.
    """
    if AllplanBaseElements is None:
        return None
    hl = AllplanBaseElements.CommonProperties()
    try:
        hl.GetGlobalProperties()
    except Exception:
        pass
    if base_props is not None:
        for attr in ("Layer", "Pen", "Stroke", "Color"):
            try:
                setattr(hl, attr, getattr(base_props, attr))
            except Exception:
                pass
    hl.Color = color
    hl.Pen = pen
    hl.ColorByLayer = False
    hl.PenByLayer = False
    hl.Construction = True
    return hl


def make_selection_common_properties(
    base_props: Any = None,
    color: int = 6,
    pen: int = 5,
):
    """
    Genera propiedades visuales para representar un elemento en estado seleccionado.

    Se usa tanto para resaltado 3D como para previews geométricos 2D cuando la
    instalación no dispone de un `model_list` renderizable.
    """
    return _make_highlight_properties(base_props, color=color, pen=pen)


def draw_highlight_preview(
    doc: Any,
    matrix: Any,
    model_list: list[Any],
    base_props: Any = None,
    color: int = 3,
    pen: int = 5,
) -> bool:
    """
    Redibuja un `model_list` con propiedades de resaltado.

    Se usa para superponer una segunda pasada visual encima del preview normal,
    por ejemplo cuando un elemento está seleccionado.
    """
    if (
        doc is None
        or matrix is None
        or not model_list
        or AllplanBasisElements is None
        or AllplanBaseElements is None
    ):
        return False
    try:
        highlight_list = []
        for me in model_list:
            geo = getattr(me, "GeometryObject", None) or getattr(me, "Geometry", None)
            if geo is None:
                continue
            cp = getattr(me, "CommonProperties", None)
            props = _make_highlight_properties(cp or base_props, color=color, pen=pen)
            if props is None:
                continue
            highlight_list.append(AllplanBasisElements.ModelElement3D(props, geo))
        if not highlight_list:
            return False
        AllplanBaseElements.DrawElementPreview(
            doc, matrix, highlight_list, False, None
        )
        return True
    except Exception:
        return False


def draw_selected_defined_element_preview(
    doc: Any,
    matrix: Any,
    model_list: list[Any],
    base_props: Any = None,
    color: int = 6,
    pen: int = 5,
) -> bool:
    """
    Resaltado visual estándar para elementos definidos seleccionados.

    Por defecto usa cian/celeste como color de selección para diferenciar el
    elemento activo del preview base.
    """
    return draw_highlight_preview(
        doc,
        matrix,
        model_list,
        base_props=base_props,
        color=color,
        pen=pen,
    )


def draw_rotation_label(doc: Any, point: Any, rot_x: float, rot_y: float, rot_z: float) -> bool:
    """
    Dibuja una etiqueta 2D con los ángulos de rotación junto al elemento.

    Es una ayuda visual para edición: muestra `RotX`, `RotY` y `RotZ` cerca
    del punto seleccionado sin modificar la geometría del modelo.
    """
    if (
        doc is None
        or point is None
        or not hasattr(point, "X")
        or AllplanGeo is None
        or AllplanBasisElements is None
        or AllplanBaseElements is None
    ):
        return False
    try:
        label_text = f"RotX={rot_x:.1f}  RotY={rot_y:.1f}  RotZ={rot_z:.1f}"
        text_com_prop = AllplanBaseElements.CommonProperties()
        text_com_prop.Pen = 1
        text_com_prop.Color = 7
        text_com_prop.Construction = True
        text_prop = AllplanBasisElements.TextProperties()
        text_prop.Height = 0.10
        text_prop.Width = 0.10
        text_prop.IsScaleDependent = False
        loc = AllplanGeo.Point2D(point.X - 50.0, point.Y + 50.0)
        text_elem = AllplanBasisElements.TextElement(
            text_com_prop, text_prop, label_text, loc
        )
        AllplanBaseElements.DrawElementPreview(
            doc, AllplanGeo.Matrix3D(), [text_elem], False, None
        )
        return True
    except Exception:
        return False
