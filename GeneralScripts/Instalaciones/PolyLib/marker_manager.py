# -*- coding: utf-8 -*-
"""
MarkerManager — base class for macro/element marker management in PolyLib.

Provides an opt-in system for placing SmartSymbol/Fixture macros and defined
elements at free points (or polyline start/end).  Installations activate it
by setting ``marker_manager_factory`` in ``PolylineBaseConfig``.

Subclass to override palette-reading methods (get_macro_settings_from_palette,
get_element_settings_from_palette, etc.) for installation-specific parameters.

Lifecycle integration (handled automatically by script_object/interactor):
  - ``on_control_event(event_id)``        — from interactor.on_control_event
  - ``handle_mouse_msg(mouse_msg, pnt)``  — from interactor.process_mouse_msg
  - ``draw_marker_preview(elems, pnt)``   — from interactor._draw_preview
  - ``append_macro_pythonparts(ppg, doc)`` — from script_object._generate_pythonparts
  - ``append_element_pythonparts(ppg, be)``— from script_object._generate_pythonparts
  - ``serialize_markers() -> dict``        — from script_object._serialize_state_to_json
  - ``deserialize_markers(state)``         — from interactor._deserialize_state_from_json
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Utility as PythonUtility

from FileNameService import FileNameService
from PythonPartUtil import PythonPartUtil

from .marker_preview import (
    draw_macro_markers,
    draw_capture_preview,
    _make_circle_lines,
    _get_preview_properties,
    COLOR_ELEMENT_BASE,
)

# ═══════════════════════════════════════════════════════════════════════════════
#  EVENT IDS (from legacy polyline_test.pyp Page 2)
# ═══════════════════════════════════════════════════════════════════════════════
EVT_SELECT_MACRO_POINT = 1013
EVT_ADD_MACRO_LIBRARY = 1014
EVT_SELECT_ELEMENT_POINT = 1015
EVT_ADD_ELEMENT_POINT = 1016
EVT_ACCEPT_MACRO = 1020
EVT_ACCEPT_ELEMENT = 1021
EVT_SELECT_LOCAL = 1026
EVT_CLEAR_LOCAL = 1027
EVT_DELETE = 1004

MARKER_EVENT_IDS = {
    EVT_SELECT_MACRO_POINT, EVT_ADD_MACRO_LIBRARY,
    EVT_SELECT_ELEMENT_POINT, EVT_ADD_ELEMENT_POINT,
    EVT_ACCEPT_MACRO, EVT_ACCEPT_ELEMENT,
    EVT_SELECT_LOCAL, EVT_CLEAR_LOCAL,
    EVT_DELETE,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  MARKER MANAGER BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class MarkerManager:
    """Base class for macro/element marker management.

    Installations subclass to override palette-reading and geometry-creation
    methods.  Generic lifecycle (events, mouse, preview, serialization) is
    provided by this base class.
    """

    def __init__(self, script_object: Any, build_ele: Any) -> None:
        self.script_object = script_object
        self.build_ele = build_ele

        # --- Macro markers ---
        self.macro_markers: List[dict] = []
        self.macro_point_capture_mode: bool = False
        self.macro_point_capture_preview: Optional[AllplanGeo.Point3D] = None
        self.macro_selected_point: Optional[AllplanGeo.Point3D] = None
        self.macro_hover_index: int = -1
        self.macro_selected_index: Optional[int] = None

        # --- Element markers ---
        self.element_markers: List[dict] = []
        self.element_point_capture_mode: bool = False
        self.element_point_capture_preview: Optional[AllplanGeo.Point3D] = None
        self.element_selected_point: Optional[AllplanGeo.Point3D] = None
        self.element_hover_index: int = -1
        self.element_selected_index: Optional[int] = None

        # Cache of pre-transformed 3D geometry per element marker (for preview)
        self._element_preview_geo_cache: List[List[Any]] = []

        # --- Room/local selection ---
        self.current_floor_z: float = 0.0
        self.current_floor_index: int = -1

    # ═══════════════════════════════════════════════════════════════════════
    #  STATIC HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _ensure_point3d(pnt: Any) -> AllplanGeo.Point3D:
        """Convert Point2D or Point3D to Point3D (Allplan may pass either)."""
        if isinstance(pnt, AllplanGeo.Point3D):
            return pnt
        try:
            return AllplanGeo.Point3D(pnt.X, pnt.Y, 0.0)
        except Exception:
            return AllplanGeo.Point3D()

    # ═══════════════════════════════════════════════════════════════════════
    #  EVENT DISPATCH
    # ═══════════════════════════════════════════════════════════════════════

    def on_control_event(self, event_id: int) -> Optional[bool]:
        """Handle macro/element events. Returns None for unrecognized (pass-through).

        Deletion priority (1004): macro_selected > element_selected > None (PolyLib handles)
        """
        if event_id == EVT_DELETE:
            # Priority: selected macro > selected element > fallthrough
            if self.macro_selected_index is not None:
                return bool(self._delete_selected_macro())
            if self.element_selected_index is not None:
                return bool(self._delete_selected_element())
            return None  # let PolyLib handle junction/segment deletion

        if event_id not in MARKER_EVENT_IDS:
            return None

        if event_id == EVT_SELECT_MACRO_POINT:
            return bool(self.start_macro_point_capture())
        if event_id == EVT_ADD_MACRO_LIBRARY:
            return bool(self._add_macro_library_marker())
        if event_id == EVT_SELECT_ELEMENT_POINT:
            return bool(self.start_element_point_capture())
        if event_id == EVT_ADD_ELEMENT_POINT:
            return bool(self._add_defined_element_marker())
        if event_id == EVT_ACCEPT_MACRO:
            return bool(self._accept_macro())
        if event_id == EVT_ACCEPT_ELEMENT:
            return bool(self._accept_element())
        if event_id == EVT_SELECT_LOCAL:
            return bool(self._handle_room_selection())
        if event_id == EVT_CLEAR_LOCAL:
            return bool(self._clear_room_selection())

        return None

    # ═══════════════════════════════════════════════════════════════════════
    #  DELETION
    # ═══════════════════════════════════════════════════════════════════════

    def _delete_selected_macro(self) -> bool:
        """Delete the currently selected macro marker."""
        idx = self.macro_selected_index
        if idx is not None and 0 <= idx < len(self.macro_markers):
            self.macro_markers.pop(idx)
            print(f"[MARKER_MGR] Deleted macro marker at index {idx}")
        self.macro_selected_index = None
        self.macro_hover_index = -1
        self._try_save_state()
        return True

    def _delete_selected_element(self) -> bool:
        """Delete the currently selected element marker."""
        idx = self.element_selected_index
        if idx is not None and 0 <= idx < len(self.element_markers):
            self.element_markers.pop(idx)
            print(f"[MARKER_MGR] Deleted element marker at index {idx}")
        self.element_selected_index = None
        self.element_hover_index = -1
        self._rebuild_element_preview_cache()
        self._try_save_state()
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  MOUSE INTERCEPTION
    # ═══════════════════════════════════════════════════════════════════════

    def handle_mouse_msg(self, mouse_msg: int, raw_pnt: Any) -> Optional[bool]:
        """Handle mouse during capture mode or edit-mode hover/selection.

        Returns None when nothing to handle (pass-through to PolyLib).
        """
        pnt = self._ensure_point3d(raw_pnt)

        # --- Capture modes take priority ---
        if self.macro_point_capture_mode:
            return self._handle_macro_point_capture(mouse_msg, pnt)
        if self.element_point_capture_mode:
            return self._handle_element_point_capture(mouse_msg, pnt)

        # --- Edit mode: hover/selection of existing markers ---
        interactor = self.script_object.script_object_interactor
        coord_input = getattr(interactor, "coord_input", None) if interactor else None
        if not coord_input:
            return None

        is_move = coord_input.IsMouseMove(mouse_msg)
        if is_move:
            # Update hover indices
            old_macro_hover = self.macro_hover_index
            old_element_hover = self.element_hover_index
            self.macro_hover_index = self._find_hover_macro_marker(pnt)
            self.element_hover_index = self._find_hover_element_marker(pnt)
            # Only consume the event if we changed hover state
            if self.macro_hover_index != old_macro_hover or self.element_hover_index != old_element_hover:
                return None  # don't consume — let PolyLib also update its hover
            return None

        # Click: check for marker hit
        macro_hit = self._find_hover_macro_marker(pnt)
        element_hit = self._find_hover_element_marker(pnt)

        if macro_hit >= 0:
            # Toggle selection
            if self.macro_selected_index == macro_hit:
                self.macro_selected_index = None
            else:
                self.macro_selected_index = macro_hit
            self.element_selected_index = None  # clear other selection
            return True

        if element_hit >= 0:
            if self.element_selected_index == element_hit:
                self.element_selected_index = None
            else:
                self.element_selected_index = element_hit
            self.macro_selected_index = None
            return True

        # Click on empty space with a marker selected → move marker
        if self.macro_selected_index is not None:
            idx = self.macro_selected_index
            if 0 <= idx < len(self.macro_markers):
                old_z = float(self.macro_markers[idx].get("z_abs", 0.0) or 0.0)
                self.macro_markers[idx]["pos"] = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
                self.macro_markers[idx]["z_abs"] = old_z  # preserve Z
                self.macro_selected_index = None
                self._try_save_state()
                self._try_draw_preview(pnt)
                return True

        if self.element_selected_index is not None:
            idx = self.element_selected_index
            if 0 <= idx < len(self.element_markers):
                old_z = float(self.element_markers[idx].get("z_abs", 0.0) or 0.0)
                self.element_markers[idx]["pos"] = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
                self.element_markers[idx]["z_abs"] = old_z
                self.element_selected_index = None
                self._rebuild_element_preview_cache()
                self._try_save_state()
                self._try_draw_preview(pnt)
                return True

        return None  # nothing to handle — pass through to PolyLib

    # ═══════════════════════════════════════════════════════════════════════
    #  HOVER DETECTION
    # ═══════════════════════════════════════════════════════════════════════

    def _find_hover_macro_marker(self, p: AllplanGeo.Point3D) -> int:
        """Hit-test in XY plane. Tolerance: max(radius * 1.6, 120.0) mm."""
        best_idx = -1
        best_dist = float("inf")
        for idx, m in enumerate(self.macro_markers):
            pos = m.get("pos")
            if pos is None:
                continue
            r = float(m.get("radius", 50.0) or 50.0)
            tol = max(r * 1.6, 120.0)
            dx = p.X - pos.X
            dy = p.Y - pos.Y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= tol * tol and dist_sq < best_dist:
                best_dist = dist_sq
                best_idx = idx
        return best_idx

    def _find_hover_element_marker(self, p: AllplanGeo.Point3D) -> int:
        """Hit-test for element markers (XY plane)."""
        best_idx = -1
        best_dist = float("inf")
        for idx, m in enumerate(self.element_markers):
            pos = m.get("pos")
            if pos is None:
                continue
            r = float(m.get("radius", 50.0) or 50.0)
            tol = max(r * 1.6, 120.0)
            dx = p.X - pos.X
            dy = p.Y - pos.Y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= tol * tol and dist_sq < best_dist:
                best_dist = dist_sq
                best_idx = idx
        return best_idx

    # ═══════════════════════════════════════════════════════════════════════
    #  MACRO POINT CAPTURE
    # ═══════════════════════════════════════════════════════════════════════

    def start_macro_point_capture(self) -> bool:
        """Activate free-point capture mode for macro placement."""
        self.macro_point_capture_mode = True
        try:
            self.build_ele.IsMacroCaptureMode.value = True
        except Exception:
            pass
        self.macro_point_capture_preview = (
            AllplanGeo.Point3D(self.macro_selected_point.X, self.macro_selected_point.Y, self.macro_selected_point.Z)
            if self.macro_selected_point is not None else None
        )
        self._set_prompt("Macro (libre): Click para seleccionar punto | 'Aceptar' o ESC para terminar")
        return True

    def _handle_macro_point_capture(self, mouse_msg: int, pnt: AllplanGeo.Point3D) -> bool:
        """Handle mouse events during macro point capture."""
        interactor = self.script_object.script_object_interactor
        coord_input = getattr(interactor, "coord_input", None) if interactor else None

        if coord_input and coord_input.IsMouseMove(mouse_msg):
            self.macro_point_capture_preview = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
            self._try_draw_preview(pnt)
            return True

        # Click: set point and create marker immediately
        self.macro_selected_point = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
        try:
            self._add_macro_library_marker()
        except Exception:
            pass
        self._try_save_state()
        self._try_draw_preview(pnt)
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  ELEMENT POINT CAPTURE
    # ═══════════════════════════════════════════════════════════════════════

    def start_element_point_capture(self) -> bool:
        """Activate free-point capture mode for defined element placement."""
        self.element_point_capture_mode = True
        try:
            self.build_ele.IsElementCaptureMode.value = True
        except Exception:
            pass
        self.element_point_capture_preview = (
            AllplanGeo.Point3D(self.element_selected_point.X, self.element_selected_point.Y, self.element_selected_point.Z)
            if self.element_selected_point is not None else None
        )
        self._set_prompt("Elemento (libre): Click para colocar | 'Aceptar' o ESC para terminar")
        return True

    def _handle_element_point_capture(self, mouse_msg: int, pnt: AllplanGeo.Point3D) -> bool:
        """Handle mouse events during element point capture."""
        interactor = self.script_object.script_object_interactor
        coord_input = getattr(interactor, "coord_input", None) if interactor else None

        if coord_input and coord_input.IsMouseMove(mouse_msg):
            self.element_point_capture_preview = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
            self._try_draw_preview(pnt)
            return True

        # Click: set point and create marker
        self.element_selected_point = AllplanGeo.Point3D(pnt.X, pnt.Y, pnt.Z)
        try:
            self._add_defined_element_marker()
        except Exception as ex:
            print(f"[MARKER_MGR] Error in _add_defined_element_marker: {ex}")
        self._try_save_state()
        self._try_draw_preview(pnt)
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  ACCEPT / CANCEL
    # ═══════════════════════════════════════════════════════════════════════

    def _accept_macro(self) -> bool:
        """Accept macro selection and exit capture mode (EventId 1020)."""
        if self.macro_point_capture_mode:
            self.macro_point_capture_mode = False
            self.macro_point_capture_preview = None
            try:
                self.build_ele.IsMacroCaptureMode.value = False
            except Exception:
                pass
            self._set_prompt("Click: agregar punto | ESC: terminar")
        return True

    def _accept_element(self) -> bool:
        """Accept element selection and exit capture mode (EventId 1021)."""
        if self.element_point_capture_mode:
            self.element_point_capture_mode = False
            self.element_point_capture_preview = None
            try:
                self.build_ele.IsElementCaptureMode.value = False
            except Exception:
                pass
            self._set_prompt("Click: agregar punto | ESC: terminar")
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  ROOM / LOCAL SELECTION (overrideable)
    # ═══════════════════════════════════════════════════════════════════════

    def _handle_room_selection(self) -> bool:
        """Start room/local selection. Override in subclass for native Allplan selection."""
        print("[MARKER_MGR] _handle_room_selection: base implementation (no-op)")
        return True

    def _clear_room_selection(self) -> bool:
        """Clear room/local selection. Override in subclass."""
        try:
            if hasattr(self.build_ele, "MacroSelectedLocalZ"):
                self.build_ele.MacroSelectedLocalZ.value = -999999.0
        except Exception:
            pass
        self._set_prompt("Click: agregar punto | ESC: terminar")
        self._try_save_state()
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  MACRO MARKER CREATION
    # ═══════════════════════════════════════════════════════════════════════

    def _add_macro_library_marker(self) -> bool:
        """Create a macro marker from palette parameters and append to macro_markers.

        Reads settings via get_macro_settings_from_palette() (overrideable).
        """
        settings = self.get_macro_settings_from_palette()
        if settings is None:
            return False

        kind = settings.get("kind", "free")
        pts = self._get_active_path_points()

        if kind == "start":
            if not pts or len(pts) < 2:
                PythonUtility.ShowMessageBox(
                    "No hay una polilinea valida (necesitas al menos 2 puntos).",
                    PythonUtility.MB_OK,
                )
                return False
            pos = pts[0]
        elif kind == "end":
            if not pts or len(pts) < 2:
                PythonUtility.ShowMessageBox(
                    "No hay una polilinea valida (necesitas al menos 2 puntos).",
                    PythonUtility.MB_OK,
                )
                return False
            pos = pts[-1]
        else:  # free
            if self.macro_selected_point is None:
                PythonUtility.ShowMessageBox(
                    "Modo Libre: primero pulsa 'Seleccionar punto' y haz click.",
                    PythonUtility.MB_OK,
                )
                return False
            pos = AllplanGeo.Point3D(
                self.macro_selected_point.X, self.macro_selected_point.Y, self.macro_selected_point.Z
            )

        lib_type = settings.get("lib_type", "SmartSymbol")
        smart_path = settings.get("smart_path", "")
        fixture_path = settings.get("fixture_path", "")

        if lib_type == "SmartSymbol" and not smart_path:
            PythonUtility.ShowMessageBox("Selecciona primero una macro (SmartSymbol .nmk).", PythonUtility.MB_OK)
            return False
        if lib_type == "Fixture" and not fixture_path:
            PythonUtility.ShowMessageBox("Selecciona primero un fixture (.lfx/.pxf).", PythonUtility.MB_OK)
            return False

        marker = {
            "kind": kind,
            "pos": pos,
            "radius": 50.0,
            "style": "circle_cross",
            "lib_type": lib_type,
            "smart_path": smart_path,
            "fixture_path": fixture_path,
            "z_abs": settings.get("z_abs", 0.0),
            "z_relative": settings.get("z_relative", 0.0),
            "floor_index": settings.get("floor_index", self.current_floor_index),
            "floor_z": settings.get("floor_z", self.current_floor_z),
            "auto_detect": settings.get("auto_detect", False),
        }
        self.macro_markers.append(marker)
        self.macro_selected_point = None
        self._try_save_state()
        self._try_draw_preview(None)
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  DEFINED ELEMENT MARKER CREATION
    # ═══════════════════════════════════════════════════════════════════════

    def _add_defined_element_marker(self) -> bool:
        """Create a defined element marker and append to element_markers."""
        mode = self._get_element_point_mode()
        kind = "start" if mode == 0 else ("end" if mode == 1 else "free")
        pts = self._get_active_path_points()

        if kind == "start":
            if not pts or len(pts) < 2:
                PythonUtility.ShowMessageBox(
                    "No hay una polilinea valida (necesitas al menos 2 puntos).", PythonUtility.MB_OK
                )
                return False
            pos = pts[0]
        elif kind == "end":
            if not pts or len(pts) < 2:
                PythonUtility.ShowMessageBox(
                    "No hay una polilinea valida (necesitas al menos 2 puntos).", PythonUtility.MB_OK
                )
                return False
            pos = pts[-1]
        else:
            if self.element_selected_point is None:
                PythonUtility.ShowMessageBox(
                    "Modo Libre: primero pulsa 'Seleccionar punto' y haz click.", PythonUtility.MB_OK
                )
                return False
            pos = AllplanGeo.Point3D(
                self.element_selected_point.X, self.element_selected_point.Y, self.element_selected_point.Z
            )

        element_type, radius = self.get_element_settings_from_palette()
        z_abs = self.get_element_z_abs()
        rot_x, rot_y, rot_z = self.get_element_rotation()

        marker = {
            "kind": kind,
            "pos": pos,
            "radius": radius,
            "element_type": element_type,
            "rot_x": float(rot_x),
            "rot_y": float(rot_y),
            "rot_z": float(rot_z),
            "z_abs": z_abs,
            "path_idx": None,
            "pt_idx": None,
        }
        self.element_markers.append(marker)
        if kind == "free":
            self.element_selected_point = None

        self._rebuild_element_preview_cache()
        self._try_save_state()
        self._try_draw_preview(None)
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  LIBRARY ELEMENT CREATION (for PythonPartGroup)
    # ═══════════════════════════════════════════════════════════════════════

    def create_library_element_from_marker(self, marker: dict) -> Any:
        """Create an AllplanBasisElements.LibraryElement from a marker dict.

        Handles SmartSymbol (.nmk) and Fixture (.lfx/.pxf) with FileNameService
        path resolution.  Override for custom behavior.
        """
        lib_type = str(marker.get("lib_type") or "")
        placement_mat = AllplanGeo.Matrix3D()

        if lib_type == "SmartSymbol":
            smart_path = str(marker.get("smart_path") or "").strip()
            if not smart_path:
                return None
            smart_path = FileNameService.get_global_standard_path(smart_path) or smart_path
            lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
                smart_path,
                AllplanBasisElements.LibraryElementType.eSmartSymbol,
                placement_mat,
            )
            return AllplanBasisElements.LibraryElement(lib_ele_prop)

        if lib_type == "Fixture":
            fixture_path = str(marker.get("fixture_path") or "").strip()
            if not fixture_path:
                return None
            fixture_path = FileNameService.get_global_standard_path(fixture_path) or fixture_path
            lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
                "", "", "",
                fixture_path,
                AllplanBasisElements.LibraryElementType.eFixtureSingleFile,
                placement_mat,
            )
            # .lfx fixtures need a polyline set
            try:
                if fixture_path.lower().endswith(".lfx"):
                    pnt_list = [AllplanGeo.Point3D(), AllplanGeo.Point3D(1000, 0, 0)]
                    lib_ele_prop.SetPolyline(AllplanGeo.Polyline3D(pnt_list))
            except Exception:
                pass
            return AllplanBasisElements.LibraryElement(lib_ele_prop)

        return None

    # ═══════════════════════════════════════════════════════════════════════
    #  ELEMENT GEOMETRY CREATION (overrideable)
    # ═══════════════════════════════════════════════════════════════════════

    def create_element_geometry(self, marker: dict) -> List[Any]:
        """Create 3D geometry for a defined element marker.

        Override in subclass to use _get_pythonpart_installed or custom geometry.
        Base implementation: creates a cyan circle polyline.
        """
        pos = self._resolve_element_marker_pos(marker)
        if pos is None:
            return []
        radius = float(marker.get("radius", 50.0) or 50.0)
        if radius <= 0.0:
            radius = 50.0
        try:
            prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            prop.Color = 6  # cyan
            prop.ColorByLayer = False
            circle = self._make_circle_polyline(pos, radius, 48)
            return [AllplanBasisElements.ModelElement3D(prop, circle)]
        except Exception:
            return []

    def get_cursor_preview_geo(self, cursor_pos: AllplanGeo.Point3D) -> List[Any]:
        """Return preview geometry at cursor pos during element capture.

        Override in subclass to show actual element shape.
        Base: returns empty list (falls back to generic circle in draw_capture_preview).
        """
        return []

    def get_macro_cursor_preview_geo(self, cursor_pos: AllplanGeo.Point3D) -> List[Any]:
        """Return preview geometry at cursor pos during macro capture.

        Override in subclass to show actual macro symbol shape.
        Base: returns empty list (falls back to generic circle+cross in draw_capture_preview).
        """
        return []

    # ═══════════════════════════════════════════════════════════════════════
    #  PYTHONPART INJECTION
    # ═══════════════════════════════════════════════════════════════════════

    def append_macro_pythonparts(self, pythonpart_group_list: list, doc: Any) -> None:
        """Convert macro markers to PythonParts and append to PPG list.

        Each macro: LibraryElement + invisible 1mm cuboid (HelpConstruction) → PythonPart.
        """
        if not self.macro_markers:
            return

        for m in self.macro_markers:
            try:
                lib_type = str(m.get("lib_type") or "")
                if not lib_type:
                    continue
                pos = m.get("pos")
                if pos is None:
                    continue

                lib_ele = self.create_library_element_from_marker(m)
                if lib_ele is None:
                    continue

                pyp_util = PythonPartUtil()
                pyp_util.add_library_elements(lib_ele)

                # Invisible 1mm cuboid as HelpConstruction for hover/selection
                try:
                    com_prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                    com_prop.HelpConstruction = True
                    com_prop.ColorByLayer = True
                    com_prop.PenByLayer = True
                    com_prop.StrokeByLayer = True
                    mm = 1.0
                    polyhed = AllplanGeo.Polyhedron3D.CreateCuboid(
                        AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(-mm / 2, -mm / 2, -mm / 2)),
                        mm, mm, mm,
                    )
                    pyp_util.add_pythonpart_view_2d3d(
                        AllplanBasisElements.ModelElement3D(com_prop, polyhed)
                    )
                except Exception:
                    pass

                # Placement matrix with absolute Z
                placement_matrix = AllplanGeo.Matrix3D()
                try:
                    z_abs = float(m.get("z_abs", 0.0) or 0.0)
                except Exception:
                    z_abs = 0.0
                placement_point = AllplanGeo.Point3D(pos.X, pos.Y, z_abs)
                placement_matrix.SetTranslation(AllplanGeo.Vector3D(placement_point))

                pp = pyp_util.get_pythonpart(self.build_ele, placement_matrix=placement_matrix)
                pythonpart_group_list.append(pp)
            except Exception:
                continue

    def append_element_pythonparts(self, pythonpart_group_list: list, build_ele: Any) -> None:
        """Convert defined element markers to PythonParts and append to PPG."""
        if not self.element_markers:
            return

        marker_groups = self._create_defined_element_model_elements_grouped()
        if not marker_groups:
            return

        for group in marker_groups:
            if not group:
                continue
            try:
                pyp_util = PythonPartUtil()
                for elem in group:
                    pyp_util.add_pythonpart_view_2d3d(elem)
                pp = pyp_util.get_pythonpart(build_ele)
                pythonpart_group_list.append(pp)
            except Exception as ex:
                print(f"[MARKER_MGR] Element PythonPart wrapping error: {ex}")

    # ═══════════════════════════════════════════════════════════════════════
    #  PREVIEW DRAWING
    # ═══════════════════════════════════════════════════════════════════════

    def draw_marker_preview(self, model_ele_list: List[Any], current_pnt: Any) -> None:
        """Append marker preview geometry to model_ele_list.

        Called from interactor._draw_preview() as an overlay pass.
        """
        pnt3d = self._ensure_point3d(current_pnt) if current_pnt is not None else None

        # Determine if we need drag preview (a marker is selected and mouse is moving)
        has_selection = (self.macro_selected_index is not None
                         or self.element_selected_index is not None)
        drag_pos = pnt3d if has_selection else None

        # Draw all existing markers with hover/selection states
        draw_macro_markers(
            self.macro_markers,
            self.element_markers,
            model_ele_list,
            element_geo_cache=self._element_preview_geo_cache,
            macro_hover_idx=self.macro_hover_index,
            macro_selected_idx=self.macro_selected_index,
            element_hover_idx=self.element_hover_index,
            element_selected_idx=self.element_selected_index,
            drag_pos=drag_pos,
            create_element_geometry_fn=self.create_element_geometry if drag_pos else None,
        )

        # Ghost marker at cursor during capture mode
        if self.macro_point_capture_mode and pnt3d is not None:
            cursor_geo = self.get_macro_cursor_preview_geo(pnt3d)
            draw_capture_preview(pnt3d, model_ele_list, is_macro=True, cursor_geo=cursor_geo)
        elif self.element_point_capture_mode and pnt3d is not None:
            cursor_geo = self.get_cursor_preview_geo(pnt3d)
            draw_capture_preview(pnt3d, model_ele_list, is_macro=False, cursor_geo=cursor_geo)

    # ═══════════════════════════════════════════════════════════════════════
    #  SERIALIZATION
    # ═══════════════════════════════════════════════════════════════════════

    def serialize_markers(self) -> dict:
        """Export macro_markers and element_markers as serializable dicts.

        Point3D → {"X":, "Y":, "Z":}.  Does NOT apply repr() — that's done
        by script_object when saving to build_ele.
        """
        def point_to_dict(pt: Any) -> dict:
            return {"X": pt.X, "Y": pt.Y, "Z": pt.Z}

        macro_data = []
        for m in self.macro_markers or []:
            try:
                if not isinstance(m, dict) or m.get("pos") is None:
                    continue
                macro_data.append({
                    "kind": str(m.get("kind", "start")),
                    "radius": float(m.get("radius", 50.0) or 50.0),
                    "pos": point_to_dict(m["pos"]),
                    "style": str(m.get("style", "circle") or "circle"),
                    "lib_type": str(m.get("lib_type", "") or ""),
                    "smart_path": str(m.get("smart_path", "") or ""),
                    "fixture_path": str(m.get("fixture_path", "") or ""),
                    "z_abs": float(m.get("z_abs", 0.0) or 0.0),
                    "z_relative": float(m.get("z_relative", 0.0) or 0.0),
                    "floor_index": int(m.get("floor_index", -1) if m.get("floor_index") is not None else -1),
                    "floor_z": float(m.get("floor_z", 0.0) or 0.0),
                    "auto_detect": bool(m.get("auto_detect", False)),
                })
            except Exception:
                continue

        element_data = []
        for m in self.element_markers or []:
            try:
                if not isinstance(m, dict) or m.get("pos") is None:
                    continue
                element_data.append({
                    "kind": str(m.get("kind", "start")),
                    "radius": float(m.get("radius", 50.0) or 50.0),
                    "pos": point_to_dict(m["pos"]),
                    "element_type": str(m.get("element_type", "circle") or "circle"),
                    "rot_x": float(m.get("rot_x", 0.0) or 0.0),
                    "rot_y": float(m.get("rot_y", 0.0) or 0.0),
                    "rot_z": float(m.get("rot_z", 0.0) or 0.0),
                    "z_abs": float(m.get("z_abs", 0.0) or 0.0),
                    "path_idx": m.get("path_idx", None),
                    "pt_idx": m.get("pt_idx", None),
                })
            except Exception:
                continue

        return {"macro_markers": macro_data, "element_markers": element_data}

    def deserialize_markers(self, state: dict) -> None:
        """Restore macro_markers and element_markers from a state dict."""
        def _to_point3d(raw: Any) -> Optional[AllplanGeo.Point3D]:
            if isinstance(raw, dict):
                return AllplanGeo.Point3D(float(raw.get("X", 0)), float(raw.get("Y", 0)), float(raw.get("Z", 0)))
            if isinstance(raw, (list, tuple)) and len(raw) >= 3:
                return AllplanGeo.Point3D(float(raw[0]), float(raw[1]), float(raw[2]))
            return None

        # Macro markers
        try:
            self.macro_markers = []
            for m in state.get("macro_markers", []) or []:
                p = _to_point3d(m.get("pos"))
                if p is None:
                    continue
                self.macro_markers.append({
                    "kind": str(m.get("kind", "start")),
                    "pos": p,
                    "radius": float(m.get("radius", 50.0) or 50.0),
                    "style": "circle_cross",
                    "lib_type": str(m.get("lib_type", "") or ""),
                    "smart_path": str(m.get("smart_path", "") or ""),
                    "fixture_path": str(m.get("fixture_path", "") or ""),
                    "z_abs": float(m.get("z_abs", 0.0) or 0.0),
                    "z_relative": float(m.get("z_relative", 0.0) or 0.0),
                    "floor_index": int(m.get("floor_index", -1) if m.get("floor_index") is not None else -1),
                    "floor_z": float(m.get("floor_z", 0.0) or 0.0),
                    "auto_detect": bool(m.get("auto_detect", False)),
                })
        except Exception:
            self.macro_markers = []

        # Element markers
        try:
            self.element_markers = []
            for m in state.get("element_markers", []) or []:
                p = _to_point3d(m.get("pos"))
                if p is None:
                    continue
                self.element_markers.append({
                    "kind": str(m.get("kind", "start")),
                    "pos": p,
                    "radius": float(m.get("radius", 50.0) or 50.0),
                    "element_type": str(m.get("element_type", "circle") or "circle"),
                    "rot_x": float(m.get("rot_x", 0.0) or 0.0),
                    "rot_y": float(m.get("rot_y", 0.0) or 0.0),
                    "rot_z": float(m.get("rot_z", 0.0) or 0.0),
                    "z_abs": float(m.get("z_abs", 0.0) or 0.0),
                    "path_idx": m.get("path_idx", None),
                    "pt_idx": m.get("pt_idx", None),
                })
        except Exception:
            self.element_markers = []

        self.macro_selected_point = None
        self.element_selected_point = None

        if self.macro_markers:
            print(f"[MARKER_MGR] Restored {len(self.macro_markers)} macro markers")
        if self.element_markers:
            print(f"[MARKER_MGR] Restored {len(self.element_markers)} element markers")
            self._rebuild_element_preview_cache()

    # ═══════════════════════════════════════════════════════════════════════
    #  OVERRIDEABLE: Palette parameter reading
    # ═══════════════════════════════════════════════════════════════════════

    def get_macro_settings_from_palette(self) -> Optional[dict]:
        """Read macro configuration from palette parameters.

        Override in subclass to read installation-specific parameters.
        Returns dict with: kind, lib_type, smart_path, fixture_path, z_abs, z_relative,
        floor_index, floor_z, auto_detect.  Returns None on failure.
        """
        return {
            "kind": "free",
            "lib_type": "SmartSymbol",
            "smart_path": "",
            "fixture_path": "",
            "z_abs": 0.0,
            "z_relative": 0.0,
            "floor_index": -1,
            "floor_z": 0.0,
            "auto_detect": False,
        }

    def get_element_settings_from_palette(self) -> Tuple[str, float]:
        """Read element type key and radius from palette.

        Override in subclass. Base returns ('circle', 50.0).
        """
        return ("circle", 50.0)

    def get_element_z_abs(self) -> float:
        """Read absolute Z coordinate for defined elements. Override in subclass."""
        return 0.0

    def get_element_rotation(self) -> Tuple[float, float, float]:
        """Read rotation angles (degrees) for defined elements. Override in subclass."""
        return (0.0, 0.0, 0.0)

    def _get_element_point_mode(self) -> int:
        """Read element point mode (0=start, 1=end, 2=free). Override if needed."""
        try:
            return int(getattr(getattr(self.build_ele, "ElementPointMode", None), "value", 2) or 2)
        except Exception:
            return 2

    # ═══════════════════════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    def _create_defined_element_model_elements_grouped(self) -> List[List[Any]]:
        """Create geometry per element marker. Returns list-of-lists."""
        if not self.element_markers:
            return []
        groups: List[List[Any]] = []
        for m in self.element_markers:
            try:
                elems = self.create_element_geometry(m)
                groups.append(elems or [])
            except Exception:
                groups.append([])
        return groups

    def _rebuild_element_preview_cache(self) -> None:
        """Rebuild preview geometry cache for all element markers."""
        self._element_preview_geo_cache = []
        for m in self.element_markers:
            try:
                element_type = str(m.get("element_type", "circle") or "circle")
                if element_type == "circle":
                    self._element_preview_geo_cache.append([])
                    continue
                elems = self.create_element_geometry(m)
                self._element_preview_geo_cache.append(elems or [])
            except Exception:
                self._element_preview_geo_cache.append([])

    def _get_active_path_points(self) -> Optional[List[AllplanGeo.Point3D]]:
        """Get points from the active polyline path."""
        interactor = self.script_object.script_object_interactor
        if not interactor:
            return None
        # Creation mode active points
        try:
            if getattr(interactor, "create_mode", False):
                points = getattr(interactor, "points", [])
                if points and len(points) >= 2:
                    return [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in points]
        except Exception:
            pass
        # Saved paths fallback
        try:
            saved_paths = getattr(interactor, "saved_paths", [])
            if saved_paths:
                pts = saved_paths[-1]
                if pts and len(pts) >= 2:
                    return [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in pts]
        except Exception:
            pass
        return None

    def _resolve_element_marker_pos(self, m: dict) -> Optional[AllplanGeo.Point3D]:
        """Resolve position of an element marker (may be linked to a polyline node)."""
        try:
            pos = m.get("pos")
            if pos is None:
                return None
            path_idx = m.get("path_idx")
            pt_idx = m.get("pt_idx")
            if path_idx is not None and pt_idx is not None:
                try:
                    interactor = self.script_object.script_object_interactor
                    saved_paths = getattr(interactor, "saved_paths", []) if interactor else []
                    if 0 <= int(path_idx) < len(saved_paths):
                        pts = saved_paths[int(path_idx)]
                        if 0 <= int(pt_idx) < len(pts):
                            pos = pts[int(pt_idx)]
                except Exception:
                    pass
            z_abs = None
            try:
                z_abs = float(m.get("z_abs", None))
            except Exception:
                pass
            if z_abs is not None:
                return AllplanGeo.Point3D(pos.X, pos.Y, z_abs)
            return AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)
        except Exception:
            return None

    @staticmethod
    def _make_circle_polyline(center: AllplanGeo.Point3D, radius: float, segments: int = 48) -> AllplanGeo.Polyline3D:
        """Create a circle as a Polyline3D."""
        pnt_list = []
        for i in range(segments + 1):
            ang = (2.0 * math.pi) * (i / segments)
            x = center.X + radius * math.cos(ang)
            y = center.Y + radius * math.sin(ang)
            pnt_list.append(AllplanGeo.Point3D(x, y, center.Z))
        return AllplanGeo.Polyline3D(pnt_list)

    def _set_prompt(self, msg: str) -> None:
        """Set user prompt via PolyLib interactor."""
        try:
            interactor = self.script_object.script_object_interactor
            if interactor and hasattr(interactor, "coord_input"):
                interactor.coord_input.SetInputControlText(msg)
        except Exception:
            pass

    def _try_draw_preview(self, raw_pnt: Optional[AllplanGeo.Point3D]) -> None:
        """Trigger a preview redraw."""
        try:
            interactor = self.script_object.script_object_interactor
            if interactor and hasattr(interactor, "_draw_preview"):
                if raw_pnt is not None:
                    interactor._draw_preview(raw_pnt)
                else:
                    current_point = getattr(interactor, "current_point", None)
                    if current_point is not None:
                        interactor._draw_preview(current_point)
        except Exception:
            pass

    def _try_save_state(self) -> None:
        """Trigger state save via PolyLib interactor."""
        try:
            interactor = self.script_object.script_object_interactor
            if interactor and hasattr(interactor, "_save_state_to_build_ele"):
                interactor._save_state_to_build_ele()
        except Exception:
            pass
