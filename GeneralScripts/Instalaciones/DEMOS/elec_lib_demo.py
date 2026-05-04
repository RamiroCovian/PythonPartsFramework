# -*- coding: utf-8 -*-
"""
Electricidad demo built on top of ``polyline_base_lib``.

Current architecture after refactor:
- Library owns generic polyline + PointInput runtime.
- Library now also owns reusable free-point tool state/click handling.
- This demo keeps only Electricidad-specific adapters:
  - palette values/defaults,
  - installation segment styling,
  - macro/defined-element factories,
  - event ID mapping to library free-point APIs.

Runtime call path:
- Allplan -> ``create_script_object()`` in this file
  -> ``PBL.initialize_script_object(..., CONFIG)``
  -> inject hooks:
     ``so.event_handler_hook = on_control_event``
     ``so.element_creation_hook = _create_electricidad_segment_elements``
- Free-point actions:
  -> UI event handled here
  -> delegated to library capture handler methods:
     ``start_free_point_tool / place_free_point_tool / stop_free_point_tool``
- Polyline create/edit/finalize:
  -> handled by library interactor/capture pipeline.
"""

from __future__ import annotations

import os
import sys
import math
from typing import Any, Dict, Optional

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil
try:
    from FileNameService import FileNameService
except Exception:
    FileNameService = None


def _add_libreria_to_sys_path() -> None:
    """
    Ensure ``Instalaciones/Libreria`` is importable.

    This keeps the demo independent from deployment nesting and guarantees
    ``polyline_base_lib`` import resolution.
    """
    if not __file__:
        return
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        parent = os.path.dirname(current)
        if os.path.basename(parent).lower() == "instalaciones":
            libreria = os.path.join(parent, "Libreria")
            if os.path.isdir(libreria) and libreria not in sys.path:
                sys.path.insert(0, libreria)
            break
        if parent == current:
            break
        current = parent


_add_libreria_to_sys_path()

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False

import polyline_base_lib as PBL
from polyline_base_lib import SegmentMetadata


INSTALLATION_NAME = "ELECTRICIDAD"
INSTALLATION_TYPES = [
    {"label": "Rejiband U 100mm", "color": 1, "diameter": 100.0, "layer_tipo": "Rejibands", "layer_subtipo": ""},
    {"label": "Rejiband U 200mm", "color": 1, "diameter": 200.0, "layer_tipo": "Rejibands", "layer_subtipo": ""},
    {"label": "Telecomunicaciones", "color": 5, "diameter": 20.0, "layer_tipo": "Telecos", "layer_subtipo": "SOBRE REJIBAND"},
    {"label": "Luz retorno / Paralelas", "color": 128, "diameter": 20.0, "layer_tipo": "Corrugats electricitat", "layer_subtipo": "SOBRE REJIBAND"},
    {"label": "Alimentacion horno", "color": 29, "diameter": 25.0, "layer_tipo": "Corrugats electricitat", "layer_subtipo": "SOBRE REJIBAND"},
    {"label": "Alimentacion luces / Cajetines", "color": 16, "diameter": 20.0, "layer_tipo": "Corrugats electricitat", "layer_subtipo": "SOBRE REJIBAND"},
    {"label": "Cajetin a enchufe", "color": 6, "diameter": 20.0, "layer_tipo": "Corrugats electricitat", "layer_subtipo": "SOBRE REJIBAND"},
    {"label": "Interruptores / Domotica", "color": 22, "diameter": 20.0, "layer_tipo": "Corrugats electricitat", "layer_subtipo": "SOBRE REJIBAND"},
]

EVENT_APPLY_LAYERS = 1009
EVENT_CAPTURE_MACRO_POINT = 1013
EVENT_ADD_MACRO_MARKER = 1014
EVENT_CAPTURE_ELEMENT_POINT = 1015
EVENT_ADD_DEFINED_ELEMENT = 1016
EVENT_EXPORT_JSON = 1030
EVENT_IMPORT_JSON = 1031
EVENT_GENERATE_OPTIMAL = 1032


def _get_installation_type(build_ele: Any) -> str:
    """Read selected installation type label from the palette object."""
    try:
        return str(getattr(getattr(build_ele, "InstallationType", None), "value", "") or "")
    except Exception:
        return ""


def _get_installation_cfg(build_ele: Any) -> Dict[str, Any]:
    """Map selected installation label to Electricidad config (color/diameter/layers)."""
    selected = _get_installation_type(build_ele)
    for item in INSTALLATION_TYPES:
        if item["label"] == selected:
            return item
    return INSTALLATION_TYPES[0]


def _set_status(build_ele: Any, message: str) -> None:
    """Write operator feedback into the palette status field."""
    try:
        if hasattr(build_ele, "FirstText"):
            build_ele.FirstText.value = message
    except Exception:
        pass


def initialize_control_properties(build_ele: BuildingElement, ctrl_prop_util: ControlPropertiesUtil, document: Any = None) -> None:
    """
    Initialize Electricidad-specific palette defaults.

    Library owns generic capture/edit startup behavior; this function only sets
    installation-specific UI defaults and value lists.
    """
    _ = document
    try:
        build_ele.InstallationName.value = INSTALLATION_NAME  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        build_ele.SupportedAngles.value = "Libre (angulo interior >= 45)"  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        value_list = "|".join([item["label"] for item in INSTALLATION_TYPES])
        ctrl_prop_util.set_value_list("InstallationType", value_list)
    except Exception:
        pass

    try:
        current = _get_installation_type(build_ele)
        if not current:
            build_ele.InstallationType.value = INSTALLATION_TYPES[0]["label"]  # type: ignore[attr-defined]
    except Exception:
        pass

    _apply_layer_defaults(build_ele)
    _set_status(build_ele, "Ready to draw")


class ElectricidadCaptureHandler(PBL.PointInputCaptureHandler):
    """Compatibility subclass kept for config stability.

    Free-point click routing is now implemented in ``PBL.PointInputCaptureHandler``.
    """


def _macro_free_point_elements(point: Any, build_ele: Any, _script_object: Any):
    """Factory callback used by library free-point tool ``macro``."""
    state = getattr(_script_object, "_free_entity_state", None)
    state_dict = state if isinstance(state, dict) else None
    return _create_library_macro_element(point, build_ele, state_dict)


def _defined_element_free_point_elements(point: Any, build_ele: Any, _script_object: Any):
    """Factory callback used by library free-point tool ``element``."""
    state = getattr(_script_object, "_free_entity_state", None)
    state_dict = state if isinstance(state, dict) else {}
    shape_name = str(
        state_dict.get(
            "DefinedElementType",
            getattr(getattr(build_ele, "DefinedElementType", None), "value", "Circulo"),
        )
        or "Circulo"
    )
    return _create_defined_shape(point, shape_name, color=4)


CONFIG = PBL.PolylineBaseConfig(
    # Migration seam:
    # generic runtime toggles live in library config, while demo injects only
    # Electricidad-specific callbacks and free-point tool definitions.
    limit_angles=False,
    drawing_mode=PBL.DRAWING_MODE_2D,
    enable_z_coordinate=False,
    allow_insert_point_mode=False,
    enable_capture_mode=True,
    capture_auto_commit_on_final=True,
    capture_auto_export_json=True,
    capture_finish_on_cancel=True,
    registry_auto_load=False,
    sync_palette_with_registry=False,
    capture_handler_class=ElectricidadCaptureHandler,
    free_point_tools={
        "macro": PBL.FreePointToolConfig(
            pending_property="PendingMacroCapture",
            active_property="IsMacroCaptureMode",
            point_store_attr="_macro_free_point",
            place_on_click=True,
            create_elements=_macro_free_point_elements,
            start_message="Macro: click a free point",
            finish_message="Macro capture finished",
            click_success_message="Macro placed (continuous mode, click more or Aceptar)",
            click_fail_message="Macro placement failed",
            invalid_selection_message="Macro: selecciona primero un SmartSymbol/Fixture valido",
            missing_point_message="Macro: first click 'Seleccionar punto' and pick free point",
            exclusive=True,
        ),
        "element": PBL.FreePointToolConfig(
            pending_property="PendingElementCapture",
            active_property="IsElementCaptureMode",
            point_store_attr="_element_free_point",
            place_on_click=True,
            create_elements=_defined_element_free_point_elements,
            start_message="Element: click a free point",
            finish_message="Element capture finished",
            click_success_message="Element placed (continuous mode, click more or Aceptar)",
            click_fail_message="Element placement failed",
            invalid_selection_message="Element placement failed",
            missing_point_message="Element: first click 'Seleccionar punto' and pick free point",
            exclusive=True,
        ),
    },
)

_global_script_object = None


def check_allplan_version(_build_ele, _version):
    return True


def create_script_object(build_ele, script_object_data):
    """
    Build library script object and attach Electricidad extension hooks.

    - ``event_handler_hook``: Electricidad event ID mapping.
    - ``element_creation_hook``: per-segment visual style for this installation.
    - transactional finalize lifecycle remains in library.
    """
    global _global_script_object
    so = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    so.event_handler_hook = on_control_event
    so.element_creation_hook = _create_electricidad_segment_elements
    PBL.enable_transactional_finalize(so)
    _global_script_object = so
    return so


def _clone_common(common_prop):
    """Defensive CommonProperties clone so per-segment edits do not mutate shared state."""
    if common_prop is None:
        return None
    try:
        clone = common_prop.__class__()
        for attr in ("Pen", "Stroke", "LineStyle", "Layer", "Transparency", "DrawOrder", "Fill", "Color"):
            try:
                setattr(clone, attr, getattr(common_prop, attr))
            except Exception:
                pass
        return clone
    except Exception:
        return common_prop


def _create_electricidad_segment_elements(seg_meta: SegmentMetadata, common_prop) -> list:
    """
    Segment element hook called by library during element materialization.

    This file only decides Electricidad-specific appearance (color by installation type).
    """
    if not ALLPLAN_AVAILABLE or len(seg_meta.points) < 2:
        return []
    so = _global_script_object
    build_ele = getattr(so, "build_ele", None) if so else None
    cfg = _get_installation_cfg(build_ele) if build_ele is not None else INSTALLATION_TYPES[0]
    cp = _clone_common(common_prop)
    try:
        cp.Color = int(cfg["color"])
    except Exception:
        pass
    p0, p1 = seg_meta.points[0], seg_meta.points[1]
    return [AllplanBasisElements.ModelElement3D(cp, AllplanGeo.Line3D(p0, p1))]


def _apply_layer_defaults(build_ele: Any) -> bool:
    """Apply layer defaults derived from selected Electricidad type."""
    cfg = _get_installation_cfg(build_ele)
    try:
        if hasattr(build_ele, "LayerTipo"):
            build_ele.LayerTipo.value = cfg["layer_tipo"]
        if hasattr(build_ele, "LayerSubtipo"):
            build_ele.LayerSubtipo.value = cfg["layer_subtipo"]
        return True
    except Exception:
        return False


def _create_cross_marker(point, color: int = 6, size: float = 120.0):
    """Fallback marker when selected macro resource cannot be loaded."""
    if point is None:
        return []
    cp = AllplanBaseElements.CommonProperties()
    cp.GetGlobalProperties()
    cp.Color = color
    p1 = AllplanGeo.Point3D(point.X - size, point.Y, point.Z)
    p2 = AllplanGeo.Point3D(point.X + size, point.Y, point.Z)
    p3 = AllplanGeo.Point3D(point.X, point.Y - size, point.Z)
    p4 = AllplanGeo.Point3D(point.X, point.Y + size, point.Z)
    return [
        AllplanBasisElements.ModelElement3D(cp, AllplanGeo.Line3D(p1, p2)),
        AllplanBasisElements.ModelElement3D(cp, AllplanGeo.Line3D(p3, p4)),
    ]


def _create_defined_shape(point, shape_name: str, color: int = 4, size: float = 150.0):
    """
    Build Electricidad-defined shape geometry for free-point placement.

    This is installation-specific content generation; library controls interaction flow.
    """
    if point is None:
        return []
    cp = AllplanBaseElements.CommonProperties()
    cp.GetGlobalProperties()
    cp.Color = color

    if shape_name == "Circulo":
        poly = AllplanGeo.Polyline3D()
        steps = 24
        for i in range(steps + 1):
            ang = (2.0 * math.pi * i) / steps
            px = point.X + size * math.cos(ang)
            py = point.Y + size * math.sin(ang)
            poly += AllplanGeo.Point3D(px, py, point.Z)
        return [AllplanBasisElements.ModelElement3D(cp, poly)]

    if shape_name == "Cuadrado":
        p1 = AllplanGeo.Point3D(point.X - size, point.Y - size, point.Z)
        p2 = AllplanGeo.Point3D(point.X + size, point.Y - size, point.Z)
        p3 = AllplanGeo.Point3D(point.X + size, point.Y + size, point.Z)
        p4 = AllplanGeo.Point3D(point.X - size, point.Y + size, point.Z)
        poly = AllplanGeo.Polyline3D()
        for p in (p1, p2, p3, p4, p1):
            poly += p
        return [AllplanBasisElements.ModelElement3D(cp, poly)]

    if shape_name == "Triangulo":
        p1 = AllplanGeo.Point3D(point.X, point.Y + size, point.Z)
        p2 = AllplanGeo.Point3D(point.X - size, point.Y - size, point.Z)
        p3 = AllplanGeo.Point3D(point.X + size, point.Y - size, point.Z)
        poly = AllplanGeo.Polyline3D()
        for p in (p1, p2, p3, p1):
            poly += p
        return [AllplanBasisElements.ModelElement3D(cp, poly)]

    try:
        circle = AllplanGeo.Polyhedron3D.CreateSphere(AllplanGeo.Point3D(point.X, point.Y, point.Z), size * 0.4)
        return [AllplanBasisElements.ModelElement3D(cp, circle)]
    except Exception:
        return _create_cross_marker(point, color=color, size=size)


def _create_doc_elements(elements: list) -> bool:
    """
    Legacy immediate placement helper.

    Free-point placement flow is now handled in library; kept here for compatibility
    with any direct script-side calls.
    """
    if not ALLPLAN_AVAILABLE or not elements:
        return False
    so = _global_script_object
    intr = getattr(so, "script_object_interactor", None) if so else None
    coord_input = getattr(intr, "coord_input", None) if intr else None
    if coord_input is None:
        return False
    try:
        doc = coord_input.GetInputViewDocument()
        AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(), elements, [], None)
        return True
    except Exception as ex:
        print(f"[elec_demo] CreateElements error: {ex}")
        return False


def _create_library_macro_element(point: Any, build_ele: Any, state_override: Optional[Dict[str, Any]] = None):
    """
    Build selected SmartSymbol/Fixture instance from palette values.

    Used by library-managed free-point tool callbacks defined in this demo config.
    """
    if point is None or not ALLPLAN_AVAILABLE:
        return None

    state = state_override if isinstance(state_override, dict) else {}
    lib_type = str(state.get("MacroLibraryElementType", getattr(getattr(build_ele, "MacroLibraryElementType", None), "value", "") or "SmartSymbol") or "SmartSymbol")
    smart_path = str(state.get("MacroSmartSymbolPath", getattr(getattr(build_ele, "MacroSmartSymbolPath", None), "value", "") or "") or "").strip()
    fixture_path = str(state.get("MacroFixturePath", getattr(getattr(build_ele, "MacroFixturePath", None), "value", "") or "") or "").strip()
    try:
        z_abs = float(state.get("MacroZAbs", getattr(getattr(build_ele, "MacroZAbs", None), "value", 0) or 0.0) or 0.0)
    except Exception:
        z_abs = 0.0

    placement = AllplanGeo.Matrix3D()
    placement.Translate(AllplanGeo.Vector3D(float(point.X), float(point.Y), float(z_abs)))

    try:
        if lib_type == "SmartSymbol":
            if not smart_path:
                return None
            if FileNameService is not None:
                smart_path = FileNameService.get_global_standard_path(smart_path) or smart_path
            lib_prop = AllplanBasisElements.LibraryElementProperties(
                smart_path,
                AllplanBasisElements.LibraryElementType.eSmartSymbol,
                placement,
            )
            return AllplanBasisElements.LibraryElement(lib_prop)

        if lib_type == "Fixture":
            if not fixture_path:
                return None
            if FileNameService is not None:
                fixture_path = FileNameService.get_global_standard_path(fixture_path) or fixture_path
            lib_prop = AllplanBasisElements.LibraryElementProperties(
                "", "", "", fixture_path,
                AllplanBasisElements.LibraryElementType.eFixtureSingleFile,
                placement,
            )
            return AllplanBasisElements.LibraryElement(lib_prop)
    except Exception:
        return None
    return None


def on_control_event(build_ele, event_id: int):
    """
    Electricidad event boundary.

    - Return True: event handled here (installation-specific behavior).
    - Return False: library continues with generic event handling.
    - Free-point workflow is delegated to library capture handler APIs.
    """
    global _global_script_object
    so = _global_script_object
    if so is None:
        return False
    intr = getattr(so, "script_object_interactor", None)
    capture_handler = getattr(intr, "capture_handler", None) if intr is not None else None

    if event_id == EVENT_APPLY_LAYERS:
        ok = _apply_layer_defaults(build_ele)
        _set_status(build_ele, "Layers applied" if ok else "Could not apply layers")
        return True

    if event_id == EVENT_CAPTURE_MACRO_POINT:
        if capture_handler is None or not hasattr(capture_handler, "start_free_point_tool"):
            return False
        return bool(capture_handler.start_free_point_tool("macro"))

    if event_id == EVENT_ADD_MACRO_MARKER:
        if capture_handler is None or not hasattr(capture_handler, "place_free_point_tool"):
            return False
        return bool(capture_handler.place_free_point_tool("macro"))

    if event_id == EVENT_CAPTURE_ELEMENT_POINT:
        if capture_handler is None or not hasattr(capture_handler, "start_free_point_tool"):
            return False
        return bool(capture_handler.start_free_point_tool("element"))

    if event_id == EVENT_ADD_DEFINED_ELEMENT:
        if capture_handler is None or not hasattr(capture_handler, "place_free_point_tool"):
            return False
        return bool(capture_handler.place_free_point_tool("element"))

    if event_id == 1020:
        if capture_handler is None or not hasattr(capture_handler, "stop_free_point_tool"):
            return False
        return bool(capture_handler.stop_free_point_tool("macro"))

    if event_id == 1021:
        if capture_handler is None or not hasattr(capture_handler, "stop_free_point_tool"):
            return False
        return bool(capture_handler.stop_free_point_tool("element"))

    if event_id == EVENT_EXPORT_JSON:
        if intr is None or not hasattr(intr, "export_json"):
            _set_status(build_ele, "Export not available")
            return True
        tipo = _get_installation_type(build_ele)
        out_dir = os.path.dirname(os.path.abspath(__file__))
        intr.export_json(
            tipo_instalacion=tipo,
            output_dir=out_dir,
        )
        return True

    if event_id == EVENT_IMPORT_JSON:
        if intr is None or not hasattr(intr, "import_json"):
            _set_status(build_ele, "Import not available")
            return True
        intr.import_json()
        return True

    if event_id == EVENT_GENERATE_OPTIMAL:
        if intr is None or not hasattr(intr, "generar_camino_optimo"):
            _set_status(build_ele, "Optimizer not available")
            return True
        tipo = _get_installation_type(build_ele)
        intr.generar_camino_optimo(tipo_instalacion=tipo)
        return True

    return False
