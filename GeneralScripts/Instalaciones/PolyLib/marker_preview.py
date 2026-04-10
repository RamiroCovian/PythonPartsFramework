# -*- coding: utf-8 -*-
"""Preview drawing helpers for macro and defined-element markers.

Used by ``MarkerManager.draw_marker_preview()`` to render marker overlays
on top of the polyline preview.  All functions are pure geometry generators
that append to an output list — they have no side-effects.
"""
from __future__ import annotations

import math
from typing import Any, List, Optional

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings

# ═══════════════════════════════════════════════════════════════════════════════
#  LEGACY-COMPATIBLE COLOR SCHEME (Allplan color indices)
# ═══════════════════════════════════════════════════════════════════════════════
COLOR_MACRO_BASE = 5        # azul  — marcadores de macro (base)
COLOR_ELEMENT_BASE = 3      # verde — marcadores de elemento (base)
COLOR_SELECTED = 2          # amarillo — marcador seleccionado
COLOR_HOVER = 1             # rojo  — marcador con hover
COLOR_CAPTURE_MACRO = 6     # cian  — cursor de captura macro
COLOR_CAPTURE_ELEMENT = 3   # verde — cursor de captura elemento

PEN_BASE = 12
PEN_HOVER = 14
PEN_SELECTED = 15


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_preview_properties(color: int = COLOR_MACRO_BASE, pen: int = PEN_BASE) -> Any:
    """Create common properties for preview markers."""
    try:
        prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        prop.Color = color
        prop.ColorByLayer = False
        prop.PenByLayer = False
        prop.StrokeByLayer = False
        try:
            prop.Pen = pen
        except Exception:
            pass
        return prop
    except Exception:
        return AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()


def _make_circle_lines(
    center: AllplanGeo.Point3D,
    radius: float,
    properties: Any,
    segments: int = 32,
) -> List[Any]:
    """Generate a circle as a list of Line3D ModelElement3D segments."""
    elems: List[Any] = []
    cx, cy, cz = center.X, center.Y, center.Z
    prev_pt = None
    for i in range(segments + 1):
        ang = (2.0 * math.pi) * (i / segments)
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        curr_pt = AllplanGeo.Point3D(x, y, cz)
        if prev_pt is not None:
            elems.append(
                AllplanBasisElements.ModelElement3D(
                    properties, AllplanGeo.Line3D(prev_pt, curr_pt)
                )
            )
        prev_pt = curr_pt
    return elems


def _make_cross_lines(
    center: AllplanGeo.Point3D,
    size: float,
    properties: Any,
) -> List[Any]:
    """Generate a 3-axis cross marker at the given point."""
    half = max(size * 0.5, 0.1)
    px, py, pz = center.X, center.Y, center.Z
    p1 = AllplanGeo.Point3D(px - half, py, pz)
    p2 = AllplanGeo.Point3D(px + half, py, pz)
    p3 = AllplanGeo.Point3D(px, py - half, pz)
    p4 = AllplanGeo.Point3D(px, py + half, pz)
    p5 = AllplanGeo.Point3D(px, py, pz - half)
    p6 = AllplanGeo.Point3D(px, py, pz + half)
    return [
        AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p1, p2)),
        AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p3, p4)),
        AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p5, p6)),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def draw_macro_markers(
    macro_markers: List[dict],
    element_markers: List[dict],
    model_ele_list: List[Any],
    element_geo_cache: Optional[List[List[Any]]] = None,
    macro_hover_idx: int = -1,
    macro_selected_idx: Optional[int] = None,
    element_hover_idx: int = -1,
    element_selected_idx: Optional[int] = None,
    drag_pos: Optional[AllplanGeo.Point3D] = None,
    create_element_geometry_fn: Any = None,
) -> None:
    """Append preview geometry for all macro and element markers.

    Args:
        macro_markers:      List of macro marker dicts.
        element_markers:    List of element marker dicts.
        model_ele_list:     Output list to append preview elements to.
        element_geo_cache:  Optional per-marker pre-computed geometry lists.
        macro_hover_idx:    Index of hovered macro marker (-1 = none).
        macro_selected_idx: Index of selected macro marker (None = none).
        element_hover_idx:  Index of hovered element marker.
        element_selected_idx: Index of selected element marker.
        drag_pos:           Current cursor position for drag preview.
                            When a marker is selected, it is drawn at drag_pos
                            instead of its stored position (visual drag feedback).
        create_element_geometry_fn: Optional callable(marker_dict) -> List[ModelElement3D]
                            used to regenerate element geometry at drag_pos.
    """
    # --- Macro markers (circle + cross) ---
    if macro_markers:
        base_prop = _get_preview_properties(color=COLOR_MACRO_BASE, pen=PEN_BASE)
        sel_prop = _get_preview_properties(color=COLOR_SELECTED, pen=PEN_SELECTED)
        hover_prop = _get_preview_properties(color=COLOR_HOVER, pen=PEN_HOVER)

        for idx, m in enumerate(macro_markers):
            try:
                pos = m.get("pos")
                if pos is None:
                    continue
                radius = float(m.get("radius", 50.0) or 50.0)
                z_abs = float(m.get("z_abs", 0.0) or 0.0)

                # Drag preview: draw selected marker at cursor position
                if (macro_selected_idx is not None
                        and idx == macro_selected_idx
                        and drag_pos is not None):
                    draw_pos = AllplanGeo.Point3D(drag_pos.X, drag_pos.Y, z_abs)
                else:
                    draw_pos = AllplanGeo.Point3D(pos.X, pos.Y, z_abs)

                # Choose properties based on state
                if macro_selected_idx is not None and idx == macro_selected_idx:
                    prop = sel_prop
                elif idx == macro_hover_idx:
                    prop = hover_prop
                else:
                    prop = base_prop

                model_ele_list.extend(_make_circle_lines(draw_pos, radius, prop))
                cross_size = max(radius * 0.8, 10.0)
                model_ele_list.extend(_make_cross_lines(draw_pos, cross_size, prop))
            except Exception:
                continue

    # --- Element markers (actual geometry or circle fallback) ---
    if element_markers:
        base_prop = _get_preview_properties(color=COLOR_ELEMENT_BASE, pen=PEN_BASE)
        sel_prop = _get_preview_properties(color=COLOR_SELECTED, pen=PEN_SELECTED)
        hover_prop = _get_preview_properties(color=COLOR_HOVER, pen=PEN_HOVER)

        for idx, m in enumerate(element_markers):
            try:
                pos = m.get("pos")
                if pos is None:
                    continue

                # Choose properties based on state
                is_selected = element_selected_idx is not None and idx == element_selected_idx
                if is_selected:
                    prop = sel_prop
                elif idx == element_hover_idx:
                    prop = hover_prop
                else:
                    prop = base_prop

                # Drag preview: regenerate geometry at cursor position
                if is_selected and drag_pos is not None and create_element_geometry_fn is not None:
                    try:
                        drag_marker = dict(m)
                        drag_marker["pos"] = AllplanGeo.Point3D(drag_pos.X, drag_pos.Y, pos.Z)
                        drag_geo = create_element_geometry_fn(drag_marker)
                        if drag_geo:
                            model_ele_list.extend(drag_geo)
                            continue
                    except Exception:
                        pass

                # Use cached 3D geometry when available
                geo_elems: Optional[List[Any]] = None
                if element_geo_cache is not None and idx < len(element_geo_cache):
                    geo_elems = element_geo_cache[idx]

                if geo_elems:
                    model_ele_list.extend(geo_elems)
                else:
                    # Fallback: circle marker at placement point
                    radius = float(m.get("radius", 50.0) or 50.0)
                    z_abs = float(m.get("z_abs", 0.0) or 0.0)
                    draw_pos = AllplanGeo.Point3D(pos.X, pos.Y, z_abs)
                    model_ele_list.extend(_make_circle_lines(draw_pos, radius, prop))
            except Exception:
                continue


def draw_capture_preview(
    point: Optional[AllplanGeo.Point3D],
    model_ele_list: List[Any],
    is_macro: bool = True,
    cursor_geo: Optional[List[Any]] = None,
) -> None:
    """Draw a ghost marker at the cursor position during capture mode.

    Args:
        point:       Current cursor position.
        model_ele_list: Output list to append preview elements to.
        is_macro:    True for macro capture, False for element capture.
        cursor_geo:  Optional pre-computed cursor geometry (e.g. actual element shape).
    """
    if point is None:
        return

    # If custom cursor geometry is provided, use it directly
    if cursor_geo:
        model_ele_list.extend(cursor_geo)
        return

    color = COLOR_CAPTURE_MACRO if is_macro else COLOR_CAPTURE_ELEMENT
    prop = _get_preview_properties(color=color)
    radius = 50.0
    model_ele_list.extend(_make_circle_lines(point, radius, prop, segments=24))
    if is_macro:
        model_ele_list.extend(_make_cross_lines(point, radius * 1.2, prop))
