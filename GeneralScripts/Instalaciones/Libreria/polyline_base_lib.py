# -*- coding: utf-8 -*-
"""Self-contained polyline base library for installation scripts.

This library provides a reusable polyline interaction component that installations
can import and use. It implements a ScriptObject and Interactor for creating and
editing polylines within Allplan.

The library is self-contained and does not import any external polyline base scripts.
Installations import this library and use it to handle polyline input.
"""

from __future__ import annotations

print("\n" + "="*80)
print(">>> POLYLINE_BASE_LIB.PY IS LOADING <<<")
print("="*80 + "\n")

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Any, Dict, Union
import math
import os
import json
import glob
import time
import importlib.util
import sys

try:
    from .installation_registry import (
        auto_load_installations as registry_auto_load_installations,
        ensure_installation_palette,
        get_installation as registry_get_installation,
        get_elements_for as registry_get_elements_for,
    )
except ImportError:
    import installation_registry
    registry_auto_load_installations = installation_registry.auto_load_installations
    ensure_installation_palette = installation_registry.ensure_installation_palette
    registry_get_installation = installation_registry.get_installation
    registry_get_elements_for = installation_registry.get_elements_for

# Allplan imports (will fail gracefully outside Allplan runtime)
try:
    import NemAll_Python_Geometry as AllplanGeo  # type: ignore
    import NemAll_Python_BaseElements as AllplanBaseElements  # type: ignore
    import NemAll_Python_BasisElements as AllplanBasisElements  # type: ignore
    import NemAll_Python_IFW_Input as AllplanIFW  # type: ignore
    from BaseScriptObject import BaseScriptObject  # type: ignore
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False
    # Placeholder classes for type checking outside Allplan
    class AllplanGeo:  # type: ignore
        class Point3D: pass
        class Polyline3D: pass
        class Line3D: pass
    class AllplanBaseElements:  # type: ignore
        class CommonProperties: pass
    class AllplanBasisElements:  # type: ignore
        class ModelElement3D: pass
    class AllplanIFW:  # type: ignore
        class MouseMessage:
            kMouseLeftButtonDown = 1
            kMouseRightButtonDown = 2
    class BaseScriptObject:  # type: ignore
        pass

# Ensure module spec is available for Allplan reloader
if __spec__ is None and "__file__" in globals():
    try:
        _spec = importlib.util.spec_from_file_location(__name__, __file__)
        if _spec is not None:
            __spec__ = _spec
            sys.modules[__name__].__spec__ = _spec
    except Exception:
        pass


Point3D = Tuple[float, float, float]


# ============================================================================
# PATH UTILITIES - Robust import path handling
# ============================================================================

def get_library_root() -> str:
    """Get the root directory of the models_lib package.
    
    Returns absolute path to models_lib/ regardless of how library was imported.
    Works for both:
    - Allplan PythonParts folder structure
    - Development/testing from arbitrary locations
    """
    if '__file__' in globals() and __file__:
        # Get directory containing this file (py/)
        py_dir = os.path.dirname(os.path.abspath(__file__))
        # Parent is models_lib/
        lib_root = os.path.dirname(py_dir)
        return lib_root
    else:
        # Fallback: search sys.path
        import sys
        for path in sys.path:
            if 'models_lib' in path and os.path.isdir(path):
                return path
        raise RuntimeError("Cannot determine models_lib root directory")

def get_model_builders_dir() -> str:
    """Get directory containing model builder files (Tub_PVC, Colze, etc.)."""
    lib_root = get_library_root()
    py_dir = os.path.join(lib_root, "py")
    return py_dir

def validate_model_builder_exists(module_name: str) -> Tuple[bool, Optional[str]]:
    """Check if a model builder module exists.
    
    Args:
        module_name: Name of module (e.g., 'Tub_PVC_TricapaV_005')
    
    Returns:
        (exists: bool, path: Optional[str])
    """
    try:
        models_dir = get_model_builders_dir()
        expected_path = os.path.join(models_dir, f"{module_name}.py")
        if os.path.exists(expected_path):
            return True, expected_path
        return False, None
    except Exception:
        return False, None

def ensure_models_in_path():
    """Ensure model builders directory is in sys.path for imports."""
    try:
        import sys
        models_dir = get_model_builders_dir()
        if models_dir not in sys.path:
            sys.path.insert(0, models_dir)
            print(f"[polyline_base_lib] Added to sys.path: {models_dir}")
        return True
    except Exception as e:
        print(f"[polyline_base_lib] Warning: Could not add models to path: {e}")
        return False


# ===== Configuration Constants =====
# These constants can be modified directly by installation scripts after importing this module.
# Installation scripts should set these values before creating the ScriptObject.
# Example: 
#   from Clima.models_lib.py import polyline_base_lib
#   polyline_base_lib.HANDLE_SIZE = 100.0
#   polyline_base_lib.HIT_TOL_VERTEX = 40.0
#   # Or import as:
#   from Clima.models_lib.py import polyline_base_lib as polyline_lib
#   polyline_lib.HANDLE_SIZE = 100.0

# ===== MODULE-LEVEL PERSISTENT STATE =====
# These persist across ScriptObject instances (Allplan creates new instances per session)
# CRITICAL: Use module-level variables for cross-session persistence
_persistent_finalized_endpoints: List[Any] = []  # Persistent across all ScriptObject instances

# File-based persistence for endpoints (survives module reloads)
# Store in user's temp directory for better compatibility
_ENDPOINTS_CACHE_FILE = os.path.join(
    os.path.expanduser("~"), 
    "AppData", "Local", "Temp", 
    "allplan_polyline_endpoints.json"
)
# Ensure temp directory exists
try:
    os.makedirs(os.path.dirname(_ENDPOINTS_CACHE_FILE), exist_ok=True)
except Exception:
    # Fallback to user home if temp dir fails
    _ENDPOINTS_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".allplan_polyline_endpoints.json")

def _load_endpoints_from_cache() -> List[Any]:
    """Load endpoints from file cache (survives module reloads)."""
    global _persistent_finalized_endpoints
    try:
        if os.path.exists(_ENDPOINTS_CACHE_FILE):
            with open(_ENDPOINTS_CACHE_FILE, 'r') as f:
                data = json.load(f)
                endpoints = []
                for ep_data in data:
                    if ALLPLAN_AVAILABLE:
                        endpoints.append(AllplanGeo.Point3D(ep_data['x'], ep_data['y'], ep_data['z']))
                    else:
                        endpoints.append(ep_data)
                _persistent_finalized_endpoints = endpoints
                return endpoints
    except Exception as ex:
        print(f"[LIBRARY] Could not load endpoints cache: {ex}")
    return []

def _save_endpoints_to_cache(endpoints: List[Any]) -> None:
    """Save endpoints to file cache (survives module reloads)."""
    try:
        data = []
        for ep in endpoints:
            if ALLPLAN_AVAILABLE and hasattr(ep, 'X'):
                data.append({'x': float(ep.X), 'y': float(ep.Y), 'z': float(ep.Z)})
            else:
                data.append(ep)
        with open(_ENDPOINTS_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as ex:
        print(f"[LIBRARY] Could not save endpoints cache: {ex}")

# Load endpoints on module import (if cache exists)
_load_endpoints_from_cache()

# Interaction and visualization constants
HANDLE_SIZE = 90.0  # mm - size of vertex handles
HIT_TOL_VERTEX = 30.0  # mm - point capture tolerance
HIT_TOL_SEGMENT = 80.0  # mm - segment capture tolerance
HOVER_SCALE = 1.25  # scale factor for hover
DRAG_SCALE = 1.5  # scale factor during drag
MAX_PERP_DIST_MM = 20.0  # mm - maximum perpendicular distance to allow click

# Segment overlay and visualization
SEGMENT_OVERLAY_Z_BIAS = 1.0  # mm - raises highlighted segment above base polyline
SEGMENT_OVERLAY_PEN = 13  # thicker pen for highlighted segments

# Insertion constants
INSERT_PREVIEW_COLOR = 6  # cyan for ghost point
MIN_INSERT_OFFSET_MM = 2.0  # mm - minimum distance to endpoints for insertion
MIN_SEG_LEN_MM = 1.0  # mm - avoid nearly null segments

# Color constants
HANDLE_COLOR_IDX = 2  # yellow (points)
PREVIEW_SAVED_COLOR = 3  # green (saved polylines)
SEGMENT_HOVER_COLOR = 1  # red (segment under mouse)
SEGMENT_SEL_COLOR = 5  # blue (selected segment)
BRANCH_ANCHOR_COLOR = 7  # magenta (branch anchor preview)
RECT_COLOR = 8  # color for selection rectangle
BOX_SELECTED_SEG_COLOR = 9  # brown (segments selected by rectangle)
SELECTED_VERTEX_COLOR = 5  # blue (selected vertices)

# Midpoint constants
MIDPOINT_COLOR = 4  # neutral color for midpoint markers
MIDPOINT_SIZE_FACTOR = 0.90  # size relative to HANDLE_SIZE
MIDPOINT_PEN = 13  # thick pen for visibility
MIDPOINT_Z_BIAS = 1.0  # mm - Z offset for visibility
MIDPOINT_HIT_TOL = 12.0  # mm - capture tolerance

# Box selection constants
RECT_PEN = 12  # rectangle line thickness

# Default segment properties (can be modified by installation scripts)
# These are used when creating default segments for new paths or when loading from JSON
DEFAULT_SEGMENT_DIAMETER = 110.0  # mm - default diameter for segments
DEFAULT_SEGMENT_SECTION_TYPE = "110mm"  # section type string
DEFAULT_SEGMENT_SYSTEM = "Pluvial"  # system type (e.g., "Pluvial", "Sanitario", etc.)
DEFAULT_SEGMENT_LABEL_PREFIX = "D110"  # label prefix for segments
DEFAULT_SYSTEM_INITIAL = "P"  # fallback initial letter for system label (used if DEFAULT_SEGMENT_SYSTEM is empty)

# User prompt message (can be modified by installation scripts)
DEFAULT_USER_PROMPT = "Click to add points, right-click to finish. ESC to cancel."

# Angle snap values for angle limiting (in degrees, can be modified by installation scripts)
# When limit_angles is enabled, angles snap to these values
ANGLE_SNAP_VALUES = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]  # degrees

# Palette property names (configurable by installation scripts)
# These define which palette properties the library will read/write
# Installation scripts can override these to match their palette structure
PALETTE_PROP_MODE = "PolylineMode"  # Radio group for create/edit/extend modes
PALETTE_PROP_CREATE_MODE = "CrearPolylinea"  # Checkbox for create mode (legacy)
PALETTE_PROP_INSERT_MODE = "CheckBoxInsertarPunto"  # Checkbox for insert point mode
PALETTE_PROP_LIMIT_ANGLES = "CheckBoxLimitarAngulos"  # Checkbox for angle limiting
PALETTE_PROP_FIRST_TEXT = "FirstText"  # Text field for user messages
PALETTE_PROP_SYSTEM = "Saneamiento"  # System selector (installation-specific)
PALETTE_PROP_DIAMETER = "Diametro"  # General diameter selector
PALETTE_PROP_DIAMETER_CUSTOM = "DiametroPersonalizado"  # Custom diameter input
PALETTE_PROP_INSTALLATION_HORIZONTAL = "TipoInstalacionHorizontal"  # Horizontal installation type
PALETTE_PROP_INSTALLATION_VERTICAL = "TipoInstalacionVertical"  # Vertical installation type
PALETTE_PROP_FACE_EN = "CaraEN"  # Face selector for EN installations

# Capture palette property names (optional)
PALETTE_PROP_PATH_ID = "PathId"
PALETTE_PROP_SEGMENT_ID = "SegmentId"
PALETTE_PROP_POINT_ROLE = "PointRole"
PALETTE_PROP_FINISH_NOW = "FinishNow"
PALETTE_PROP_ENABLE_ASSIST = "EnableAssistWndClick"
PALETTE_PROP_ENABLE_Z = "EnableZCoordinate"
PALETTE_PROP_ENABLE_UNDO = "EnableUndoStep"
PALETTE_PROP_SET_PROJ_BASE = "SetProjectionBase0"
PALETTE_PROP_CREATE_SYMBOL = "CreateSymbol"
PALETTE_PROP_INSTALLATION_NAME = "InstallationName"
PALETTE_PROP_ELEMENT_KEY = "ElementKey"
PALETTE_PROP_INSTALLATION_TYPE = "InstallationType"
PALETTE_PROP_SUPPORTED_ANGLES = "SupportedAngles"
PALETTE_PROP_POINT_MODE = "PointMode"

# Fusion/extension tolerance (configurable)
FUSION_TOLERANCE_MM = 30.0  # mm - distance threshold for automatic fusion
EXTENSION_TOLERANCE_MM = 30.0  # mm - distance threshold for extension detection

# Capture role identifiers
CAPTURE_ROLE_INICIAL = 0
CAPTURE_ROLE_PASO = 1
CAPTURE_ROLE_BIFURCACION = 2
CAPTURE_ROLE_FINAL = 3

CAPTURE_ROLE_LABELS = {
    CAPTURE_ROLE_INICIAL: "Inicial",
    CAPTURE_ROLE_PASO: "Paso",
    CAPTURE_ROLE_BIFURCACION: "Bifurcacion",
    CAPTURE_ROLE_FINAL: "Final",
}

CAPTURE_COLOR_MIN = 1
CAPTURE_COLOR_MAX = 255


# =============================================================================
# PointInputCaptureHandler - Extensible capture logic (subclass to customize)
# =============================================================================


class PointInputCaptureHandler:
    """PointInput-style capture handler. Encapsulates all capture logic.
    
    Subclass this class to customize behavior (e.g. different polyline creation,
    JSON export format, or palette property names). The interactor delegates
    to this handler when capture mode is enabled.
    
    Override methods to customize:
    - create_polylines_for_path(): Change how polylines are created
    - export_json(): Change JSON export path or format
    - get_path_id(), get_segment_id(), get_point_role(): Custom palette mapping
    """

    def __init__(self, interactor: "PolylineInteractor", config: "PolylineBaseConfig"):
        self.interactor = interactor
        self.config = config
        self.records: List[CapturePoint] = []
        self._order_counter = 0
        self._active_path_id: Optional[int] = None
        self._last_json_path: Optional[str] = None

    def enabled(self) -> bool:
        return True

    def get_path_id(self) -> int:
        value = self.interactor._safe_get_palette_property(PALETTE_PROP_PATH_ID, 1)
        try:
            return max(1, int(value))
        except Exception:
            return 1

    def get_segment_id(self) -> int:
        value = self.interactor._safe_get_palette_property(PALETTE_PROP_SEGMENT_ID, 1)
        try:
            return max(1, int(value))
        except Exception:
            return 1

    def get_point_role(self) -> int:
        value = self.interactor._safe_get_palette_property(PALETTE_PROP_POINT_ROLE, CAPTURE_ROLE_PASO)
        role = CAPTURE_ROLE_PASO
        if isinstance(value, (int, float)):
            role = int(value)
        elif isinstance(value, str):
            normalized = value.strip().lower()
            for key, label in CAPTURE_ROLE_LABELS.items():
                if label.lower() == normalized:
                    role = key
                    break
        role = max(CAPTURE_ROLE_INICIAL, min(CAPTURE_ROLE_FINAL, role))
        return role

    def color_from_path(self, path_id: int) -> int:
        return max(CAPTURE_COLOR_MIN, min(CAPTURE_COLOR_MAX, int(path_id)))

    def apply_color_to_commonprops(self, color_id: int) -> None:
        build_ele = getattr(self.interactor.script_object, "build_ele", None)
        if build_ele is None:
            return
        for attr in ("CommonProp", "SymbolCommonProps"):
            try:
                palette_prop = getattr(build_ele, attr, None)
                if palette_prop is None:
                    continue
                value = getattr(palette_prop, "value", None)
                if value is None:
                    continue
                if getattr(value, "Color", None) != color_id:
                    value.Color = color_id
                    palette_prop.value = value
            except Exception:
                continue

    def get_common_props_with_color(self, color_id: int) -> Any:
        if not ALLPLAN_AVAILABLE:
            return None
        try:
            build_ele = getattr(self.interactor.script_object, "build_ele", None)
            if build_ele is None:
                common_prop = AllplanBaseElements.CommonProperties()
                common_prop.GetGlobalProperties()
                try:
                    common_prop.Color = color_id
                except Exception:
                    pass
                return common_prop
            base = None
            try:
                base = getattr(getattr(build_ele, "CommonProp", None), "value", None)
            except Exception:
                pass
            if base is None:
                try:
                    base = getattr(getattr(build_ele, "SymbolCommonProps", None), "value", None)
                except Exception:
                    pass
            if base is None:
                common_prop = AllplanBaseElements.CommonProperties()
                common_prop.GetGlobalProperties()
                try:
                    common_prop.Color = color_id
                except Exception:
                    pass
                return common_prop
            try:
                common_prop = base.__class__()
                for attr in ("Pen", "Stroke", "LineStyle", "Layer", "Transparency", "DrawOrder", "Fill", "Color"):
                    try:
                        setattr(common_prop, attr, getattr(base, attr))
                    except Exception:
                        pass
            except Exception:
                common_prop = base
            try:
                common_prop.Color = color_id
            except Exception:
                pass
            return common_prop
        except Exception as e:
            print(f"[CAPTURE] Error getting CommonProps with color: {e}")
            try:
                common_prop = AllplanBaseElements.CommonProperties()
                common_prop.GetGlobalProperties()
                try:
                    common_prop.Color = color_id
                except Exception:
                    pass
                return common_prop
            except Exception:
                return None

    def apply_coord_flags(self) -> None:
        if not ALLPLAN_AVAILABLE or self.interactor.coord_input is None:
            return
        try:
            assist = bool(self.interactor._safe_get_palette_property(PALETTE_PROP_ENABLE_ASSIST, False))
            if hasattr(self.interactor.coord_input, "EnableAssistWndClick"):
                self.interactor.coord_input.EnableAssistWndClick(assist)
        except Exception:
            pass
        try:
            enable_z = self.interactor._safe_get_palette_property(
                PALETTE_PROP_ENABLE_Z, should_enable_z_coordinate(self.config)
            )
            if hasattr(self.interactor.coord_input, "SetEnableZCoordinate"):
                self.interactor.coord_input.SetEnableZCoordinate(bool(enable_z))
        except Exception:
            pass
        try:
            enable_undo = bool(self.interactor._safe_get_palette_property(PALETTE_PROP_ENABLE_UNDO, False))
            if hasattr(self.interactor.coord_input, "EnableUndoStep"):
                self.interactor.coord_input.EnableUndoStep(enable_undo)
        except Exception:
            pass
        try:
            projection = bool(self.interactor._safe_get_palette_property(PALETTE_PROP_SET_PROJ_BASE, True))
            if hasattr(self.interactor.coord_input, "SetProjectionBase0"):
                self.interactor.coord_input.SetProjectionBase0(projection)
        except Exception:
            pass

    def on_start(self) -> None:
        """Called when capture mode starts (start_input)."""
        self.apply_coord_flags()
        self.apply_color_to_commonprops(self.color_from_path(self.get_path_id()))

    def _get_free_point_tools(self) -> Dict[str, "FreePointToolConfig"]:
        tools = getattr(self.config, "free_point_tools", None)
        if isinstance(tools, dict):
            return {str(name): tool for name, tool in tools.items() if isinstance(tool, FreePointToolConfig)}
        return {}

    def _is_tool_active(self, tool: "FreePointToolConfig") -> bool:
        pending = bool(self.interactor._safe_get_palette_property(tool.pending_property, False))
        active = False
        if tool.active_property:
            active = bool(self.interactor._safe_get_palette_property(tool.active_property, False))
        return bool(pending or active)

    def _set_tool_state(self, tool: "FreePointToolConfig", enabled: bool) -> None:
        try:
            self.interactor._safe_set_palette_property(tool.pending_property, bool(enabled))
        except Exception:
            pass
        if tool.active_property:
            try:
                self.interactor._safe_set_palette_property(tool.active_property, bool(enabled))
            except Exception:
                pass

    def _set_status_message(self, message: str) -> None:
        if not message:
            return
        try:
            self.interactor._set_palette_message(message)
        except Exception:
            pass

    def _normalize_elements(self, created: Any) -> List[Any]:
        if created is None:
            return []
        if isinstance(created, (list, tuple)):
            return [ele for ele in created if ele is not None]
        return [created]

    def _resolve_tool_name(self, tool: "FreePointToolConfig") -> str:
        tools = self._get_free_point_tools()
        for name, cfg in tools.items():
            if cfg is tool:
                return str(name)
        return ""

    def _create_doc_elements(self, elements: List[Any]) -> bool:
        if not ALLPLAN_AVAILABLE or not elements:
            return False
        coord_input = getattr(self.interactor, "coord_input", None)
        if coord_input is None:
            return False
        try:
            doc = coord_input.GetInputViewDocument()
            AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(), elements, [], None)
            return True
        except Exception:
            return False

    def _run_tool_placement(self, tool: "FreePointToolConfig", point: Any) -> bool:
        so = self.interactor.script_object
        build_ele = getattr(so, "build_ele", None)
        normalized_point = self.interactor._clone_point3d(point)
        setattr(so, tool.point_store_attr, normalized_point)

        if callable(tool.create_elements):
            created = tool.create_elements(normalized_point, build_ele, so)
            elements = self._normalize_elements(created)
            if not elements:
                self._set_status_message(tool.invalid_selection_message)
                return False
            # Persist as editable entity in library state; actual element creation happens
            # via preview and execute pipeline, enabling move/delete parity with polylines.
            tool_name = self._resolve_tool_name(tool)
            state_payload = {}
            try:
                if hasattr(self.interactor, "_capture_free_entity_state"):
                    state_payload = self.interactor._capture_free_entity_state(tool_name)
            except Exception:
                state_payload = {}
            self.interactor._store_free_entity(tool_name, normalized_point, state_payload)
            self.interactor._draw_preview(normalized_point)
            self._set_status_message(tool.click_success_message)
            return True

        self._set_status_message(tool.invalid_selection_message)
        return False

    def _handle_free_point_tool_click(self, current_pnt: Any) -> bool:
        tools = self._get_free_point_tools()
        if not tools:
            return False
        for _, tool in tools.items():
            if not self._is_tool_active(tool):
                continue
            self._set_tool_state(tool, True)
            if tool.place_on_click:
                self._run_tool_placement(tool, current_pnt)
            self.interactor._draw_preview(current_pnt)
            self._reinit_coord_input_for_next_point(first_point=(len(self.interactor.points) == 0))
            return True
        return False

    def has_active_free_point_tool(self) -> bool:
        """True when any configured free-point tool is active."""
        tools = self._get_free_point_tools()
        if not tools:
            return False
        for _, tool in tools.items():
            if self._is_tool_active(tool):
                return True
        return False

    def start_free_point_tool(self, tool_name: str) -> bool:
        tools = self._get_free_point_tools()
        tool = tools.get(str(tool_name))
        if tool is None:
            return False

        if bool(tool.exclusive):
            for name, other in tools.items():
                if name == tool_name:
                    continue
                self._set_tool_state(other, False)
        self._set_tool_state(tool, True)
        self._set_status_message(tool.start_message)
        return True

    def stop_free_point_tool(self, tool_name: str) -> bool:
        tools = self._get_free_point_tools()
        tool = tools.get(str(tool_name))
        if tool is None:
            return False
        self._set_tool_state(tool, False)
        self._set_status_message(tool.finish_message)
        return True

    def place_free_point_tool(self, tool_name: str) -> bool:
        tools = self._get_free_point_tools()
        tool = tools.get(str(tool_name))
        if tool is None:
            return False
        so = self.interactor.script_object
        point = getattr(so, tool.point_store_attr, None)
        if point is None:
            self._set_status_message(tool.missing_point_message)
            return True
        return self._run_tool_placement(tool, point)

    def handle_point_click(self, current_pnt: Any) -> bool:
        """Handle point capture on left click. Returns True if handled."""
        if current_pnt is None:
            return False
        if self._handle_free_point_tool_click(current_pnt):
            return True
        self.interactor._save_state_snapshot()
        path_id = self.get_path_id()
        segment_id = self.get_segment_id()
        role = self.get_point_role()
        color_id = self.color_from_path(path_id)
        diameter = self.interactor._get_current_diameter()
        system = self.interactor._get_current_system()
        section_type = f"{diameter}mm"
        element_key = None
        if self.interactor.element_key_property:
            element_key = self.interactor._safe_get_palette_property(self.interactor.element_key_property)
            if element_key not in (None, ""):
                element_key = str(element_key)
        installation_ref = self.interactor.current_installation or self.interactor._read_installation_from_palette()
        if installation_ref in (None, ""):
            installation_ref = None

        if self._active_path_id is None or self._active_path_id != path_id or role == CAPTURE_ROLE_INICIAL:
            self.interactor.points.clear()
            self._active_path_id = path_id

        # PointInput_SO alignment: use raw world coordinates (no origin offset)
        new_point = self.interactor._clone_point3d(current_pnt) if current_pnt is not None else None
        if new_point is None:
            return False
        self.interactor.points.append(new_point)
        self.interactor.current_point = new_point

        capture_entry = CapturePoint(
            point=new_point,
            path_id=path_id,
            segment_id=segment_id,
            role=role,
            color_id=color_id,
            order_index=self._order_counter,
            diameter=diameter,
            system=system,
            section_type=section_type,
            element_key=element_key,
            installation=installation_ref,
        )
        self._order_counter += 1
        self.records.append(capture_entry)

        self.apply_color_to_commonprops(color_id)
        self._create_point_symbol(new_point)
        self.interactor._draw_preview(new_point)

        # Interactive branch workflow:
        # clicking Bifurcacion commits the current run immediately and starts a new run from the same point.
        if role == CAPTURE_ROLE_BIFURCACION and self.config.capture_auto_commit_on_final:
            if self._finalize_on_bifurcation(path_id, capture_entry):
                return True

        if role == CAPTURE_ROLE_FINAL and self.config.capture_auto_commit_on_final:
            self.finalize_path(path_id, reason="Final")
        else:
            # PointInput_SO alignment: re-init for next point after each capture
            self._reinit_coord_input_for_next_point()
        return True

    def _finalize_on_bifurcation(self, path_id: int, bif_record: "CapturePoint") -> bool:
        """Finalize current run at bifurcation and continue drawing from the branch node."""
        try:
            pending = [c for c in self.records if c.path_id == path_id and not c.exported]
            if len(pending) < 2:
                self.interactor._set_palette_message("Bifurcacion: necesitas al menos 2 puntos")
                return False

            # Commit all pending captures up to this click (stores paths, creates geometry/json as configured).
            if not self.finalize_path(path_id, reason="Bifurcacion"):
                self.interactor._set_palette_message("Bifurcacion: no se pudo finalizar tramo")
                return False

            # Seed next branch run from the same bifurcation node as a fresh "Inicial".
            branch_start = self.interactor._clone_point3d(bif_record.point)
            self.interactor.points = [branch_start]
            self.interactor.current_point = branch_start
            self._active_path_id = path_id
            self.records.append(
                CapturePoint(
                    point=branch_start,
                    path_id=path_id,
                    segment_id=bif_record.segment_id,
                    role=CAPTURE_ROLE_INICIAL,
                    color_id=bif_record.color_id,
                    order_index=self._order_counter,
                    diameter=bif_record.diameter,
                    system=bif_record.system,
                    section_type=bif_record.section_type,
                    element_key=bif_record.element_key,
                    installation=bif_record.installation,
                )
            )
            self._order_counter += 1
            self.interactor._set_palette_message(f"Bifurcacion creada en Path {path_id}. Continua rama.")
            self._reinit_coord_input_for_next_point(first_point=False)
            self.interactor._draw_preview(branch_start)
            return True
        except Exception:
            self.interactor._set_palette_message("Bifurcacion: error interno")
            return False

    def _reinit_coord_input_for_next_point(self, first_point: bool = False) -> None:
        """PointInput_SO alignment: re-init coord input after each capture."""
        if not ALLPLAN_AVAILABLE or self.interactor.coord_input is None:
            return
        try:
            role_label = CAPTURE_ROLE_LABELS.get(self.get_point_role(), "Paso")
            msg = f"Path {self.get_path_id()} · {role_label}"
            prompt = AllplanIFW.InputStringConvert(msg)
            if first_point or not self.interactor.points:
                self.interactor.coord_input.InitFirstPointInput(prompt)
            else:
                self.interactor.coord_input.InitNextPointInput(prompt)
        except Exception:
            pass

    def _create_point_symbol(self, point: Any) -> None:
        if not ALLPLAN_AVAILABLE or self.interactor.coord_input is None:
            return
        create_symbol = self.interactor._safe_get_palette_property(PALETTE_PROP_CREATE_SYMBOL, False)
        if not create_symbol:
            return
        try:
            symbol_props = AllplanBasisElements.Symbol3DProperties()
            symbol_props.IsScaleDependent = False  # type: ignore[attr-defined]
            symbol_props.SymbolID = 1  # type: ignore[attr-defined]
            build_ele = getattr(self.interactor.script_object, "build_ele", None)
            common_props = None
            if build_ele is not None:
                common_props = getattr(getattr(build_ele, "SymbolCommonProps", None), "value", None)
                if common_props is None:
                    common_props = getattr(getattr(build_ele, "CommonProp", None), "value", None)
            if common_props is None:
                return
            doc = None
            try:
                doc = self.interactor.coord_input.GetInputViewDocument()
            except Exception:
                doc = None
            if doc is None:
                return
            AllplanBaseElements.CreateElements(
                doc,
                AllplanGeo.Matrix3D(),
                [AllplanBasisElements.Symbol3DElement(common_props, symbol_props, point)],
                [],
                None,
            )
        except Exception:
            pass

    def finalize_path(self, path_id: int, reason: str = "manual") -> bool:
        pending = [c for c in self.records if c.path_id == path_id and not c.exported]
        if not pending:
            return False
        runs = self._split_runs(pending)
        if not runs:
            runs = [pending]
        for run in runs:
            self._store_run(path_id, run)
        if self.config.capture_auto_commit_on_final:
            self.create_polylines_for_path(path_id)
        if self.config.capture_auto_export_json:
            self._last_json_path = self.export_json(path_id)
        self.interactor.points.clear()
        self._active_path_id = None
        self.interactor._clear_editing_state()
        # PointInput_SO alignment: re-init for next path (first point of new path)
        self._reinit_coord_input_for_next_point(first_point=True)
        self.interactor._set_palette_message(f"Path {path_id} finalizado ({reason})")
        return True

    def _store_run(self, path_id: int, records: List[CapturePoint]) -> None:
        if len(records) < 2:
            return
        sanitized_points = [self.interactor._clone_point3d(rec.point) for rec in records]
        self.interactor.script_object.saved_paths.append(sanitized_points)
        path_idx = len(self.interactor.script_object.saved_paths) - 1
        for idx in range(len(records) - 1):
            start_rec = records[idx]
            end_rec = records[idx + 1]
            start_pt = self.interactor._clone_point3d(start_rec.point)
            end_pt = self.interactor._clone_point3d(end_rec.point)
            metadata = SegmentMetadata(
                points=[start_pt, end_pt],
                diameter=start_rec.diameter,
                section_type=start_rec.section_type,
                system=start_rec.system,
                label=f"{DEFAULT_SEGMENT_LABEL_PREFIX} {start_rec.system[:1] if start_rec.system else DEFAULT_SYSTEM_INITIAL}",
                path_id=path_id,
                segment_id=end_rec.segment_id,
                color_id=start_rec.color_id,
                point_roles=[start_rec.role, end_rec.role],
                custom={"path_idx": path_idx},
            )
            self.interactor.script_object.saved_segments.append(metadata)

    def _split_runs(self, records: List[CapturePoint]) -> List[List[CapturePoint]]:
        """Split captures into runs. Bifurcacion = branch point: ends current run, starts new run from same point."""
        ordered = sorted(records, key=lambda rec: rec.order_index)
        runs: List[List[CapturePoint]] = []
        current: List[CapturePoint] = []
        for record in ordered:
            if record.role == CAPTURE_ROLE_INICIAL:
                if current:
                    runs.append(self._dedupe_run(current))
                current = [record]
            elif record.role == CAPTURE_ROLE_PASO:
                if not current:
                    current = [record]
                else:
                    current.append(record)
            elif record.role == CAPTURE_ROLE_BIFURCACION:
                # Branch point: end current run, start new run from this point (shared vertex)
                if not current:
                    current = [record]
                else:
                    current.append(record)
                    runs.append(self._dedupe_run(current))
                    current = [record]  # New run starts at bifurcation point
            elif record.role == CAPTURE_ROLE_FINAL:
                if not current:
                    current = [record]
                else:
                    current.append(record)
                runs.append(self._dedupe_run(current))
                current = []
            else:
                current.append(record)
        if current:
            runs.append(self._dedupe_run(current))
        return [run for run in runs if len(run) >= 2]

    def _dedupe_run(self, run: List[CapturePoint]) -> List[CapturePoint]:
        deduped: List[CapturePoint] = []
        last_coords: Optional[Tuple[float, float, float]] = None
        for record in run:
            coords = _extract_point_components(record.point)
            if last_coords is None or coords != last_coords:
                deduped.append(record)
                last_coords = coords
        return deduped

    def create_polylines_for_path(self, path_id: int) -> None:
        """Create Polyline2D/3D for path. Override to customize."""
        if not self.interactor.coord_input:
            return
        try:
            create_pythonpart = False
            try:
                build_ele = getattr(self.interactor.script_object, "build_ele", None)
                if build_ele:
                    create_pythonpart_prop = getattr(build_ele, "CreatePythonPartGroup", None)
                    if create_pythonpart_prop:
                        create_pythonpart = bool(create_pythonpart_prop.value)
            except Exception:
                pass
            captures = [c for c in self.records if c.path_id == path_id]
            if not captures:
                return
            runs = self._split_runs(captures)
            if not runs:
                runs = [captures]
            if create_pythonpart:
                print(f"[CAPTURE] Path {path_id} stored for PythonPart creation (edit mode enabled)")
                return
            doc = None
            try:
                doc = self.interactor.coord_input.GetInputViewDocument()
            except Exception:
                return
            if not doc:
                return
            color_id = self.color_from_path(path_id)
            common_prop = self.get_common_props_with_color(color_id)
            if common_prop is None:
                return
            elements = []
            for run in runs:
                if len(run) < 2:
                    continue
                deduped = self._dedupe_run(run)
                if len(deduped) < 2:
                    continue
                points_2d = []
                points_3d = []
                for record in deduped:
                    pt = record.point
                    points_2d.append(AllplanGeo.Point2D(pt.X, pt.Y))
                    points_3d.append(AllplanGeo.Point3D(pt.X, pt.Y, pt.Z))
                if len(points_2d) >= 2:
                    pl2d = AllplanGeo.Polyline2D()
                    for p in points_2d:
                        pl2d += p
                    elements.append(AllplanBasisElements.ModelElement2D(common_prop, pl2d))
                if len(points_3d) >= 2:
                    pl3d = AllplanGeo.Polyline3D()
                    for p in points_3d:
                        pl3d += p
                    elements.append(AllplanBasisElements.ModelElement3D(common_prop, pl3d))
            if elements:
                AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(), elements, [], None)
                print(f"[CAPTURE] Created {len(elements)} polylines for path {path_id} (simple mode)")
        except Exception as e:
            print(f"[CAPTURE] Error creating polylines for path {path_id}: {e}")
            import traceback
            traceback.print_exc()

    def export_json(self, path_id: int) -> Optional[str]:
        """Export capture records to JSON. Override to customize path/format."""
        return export_capture_records_to_json(
            self.records, path_id, self.config.capture_json_path
        )

    def check_finish_now(self) -> None:
        finish_flag = self.interactor._safe_get_palette_property(PALETTE_PROP_FINISH_NOW, False)
        if finish_flag:
            path_id = self.get_path_id()
            if self.finalize_path(path_id, reason="FinishNow"):
                self.interactor._safe_set_palette_property(PALETTE_PROP_FINISH_NOW, False)

    def finalize_all_paths(self, reason: str = "shutdown") -> None:
        pending_paths = sorted({rec.path_id for rec in self.records if not rec.exported})
        for path_id in pending_paths:
            self.finalize_path(path_id, reason=reason)

    def on_shutdown(self, reason: str = "shutdown") -> None:
        """Called when capture session ends."""
        if self.config.capture_finish_on_cancel:
            self.finalize_all_paths(reason=reason)


def _extract_point_components(point: Any) -> Tuple[float, float, float]:
    """Return XYZ components regardless of point implementation."""
    try:
        return float(point.X), float(point.Y), float(point.Z)
    except Exception:
        pass

    if isinstance(point, (tuple, list)) and len(point) >= 3:
        return float(point[0]), float(point[1]), float(point[2])

    return 0.0, 0.0, 0.0


def _compute_segment_geometry(
    p1_xyz: Tuple[float, float, float],
    p2_xyz: Tuple[float, float, float],
    index: int,
) -> Dict[str, Any]:
    """Compute full geometric properties for a segment defined by two points.

    Ported from PointInputElecNew/PolylineLib/creator.py (SegmentData computation).
    Pure math -- no Allplan dependencies.

    Args:
        p1_xyz: (x, y, z) of start point.
        p2_xyz: (x, y, z) of end point.
        index:  0-based segment index (used for the ``name`` field).

    Returns:
        Dict matching the ``data.json`` segment schema::

            {"name": "line_1", "data": { ... 35+ geometric fields ... }}
    """
    x1, y1, z1 = p1_xyz
    x2, y2, z2 = p2_xyz

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    longitud_3d = math.sqrt(dx * dx + dy * dy + dz * dz)
    longitud_xy = math.sqrt(dx * dx + dy * dy)
    longitud_xz = math.sqrt(dx * dx + dz * dz)
    longitud_yz = math.sqrt(dy * dy + dz * dz)
    longitud_x = abs(dx)
    longitud_y = abs(dy)
    longitud_z = abs(dz)

    if longitud_3d > 1e-6:
        vn_x, vn_y, vn_z = dx / longitud_3d, dy / longitud_3d, dz / longitud_3d
    else:
        vn_x = vn_y = vn_z = 0.0

    angulo_xy_desde_x = math.degrees(math.atan2(dy, dx))
    angulo_xy_desde_y = math.degrees(math.atan2(dx, dy))
    azimut = (90.0 - angulo_xy_desde_x) % 360.0

    angulo_xz_desde_x = math.degrees(math.atan2(dz, dx)) if dx != 0 else (90.0 if dz > 0 else -90.0)
    angulo_xz_desde_z = math.degrees(math.atan2(dx, dz)) if dz != 0 else (90.0 if dx > 0 else -90.0)
    inclinacion_en_x = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else 0.0

    angulo_yz_desde_y = math.degrees(math.atan2(dz, dy)) if dy != 0 else (90.0 if dz > 0 else -90.0)
    angulo_yz_desde_z = math.degrees(math.atan2(dy, dz)) if dz != 0 else (90.0 if dy > 0 else -90.0)
    inclinacion_en_y = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else 0.0

    elevacion = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else (90.0 if dz > 0 else -90.0)
    pendiente_porcentaje = (dz / longitud_xy * 100.0) if longitud_xy > 0 else 0.0

    if longitud_3d > 0:
        cos_x = dx / longitud_3d
        cos_y = dy / longitud_3d
        cos_z = dz / longitud_3d
        angulo_con_eje_x = math.degrees(math.acos(max(-1.0, min(1.0, cos_x))))
        angulo_con_eje_y = math.degrees(math.acos(max(-1.0, min(1.0, cos_y))))
        angulo_con_eje_z = math.degrees(math.acos(max(-1.0, min(1.0, cos_z))))
    else:
        cos_x = cos_y = cos_z = 0.0
        angulo_con_eje_x = angulo_con_eje_y = angulo_con_eje_z = 0.0

    angulo_xy_xz = math.degrees(math.atan2(longitud_z, longitud_xy)) if longitud_xy > 0 else 0.0
    angulo_xy_yz = math.degrees(math.atan2(longitud_z, longitud_xy)) if longitud_xy > 0 else 0.0
    angulo_xz_yz = math.degrees(math.atan2(longitud_y, longitud_x)) if longitud_x > 0 else 0.0

    if dx >= 0 and dy >= 0:
        cuadrante_xy = 1
    elif dx < 0 and dy >= 0:
        cuadrante_xy = 2
    elif dx < 0 and dy < 0:
        cuadrante_xy = 3
    else:
        cuadrante_xy = 4
    octante = cuadrante_xy if dz >= 0 else cuadrante_xy + 4

    sentido_x = "positivo" if dx > 0 else ("negativo" if dx < 0 else "neutro")
    sentido_y = "positivo" if dy > 0 else ("negativo" if dy < 0 else "neutro")
    sentido_z = "ascendente" if dz > 0 else ("descendente" if dz < 0 else "horizontal")

    if abs(elevacion) < 5.0:
        tipo_segmento = "horizontal"
    elif abs(elevacion) > 85.0:
        tipo_segmento = "vertical"
    else:
        tipo_segmento = "inclinado"

    return {
        "name": f"line_{index + 1}",
        "data": {
            "start": {"X": x1, "Y": y1, "Z": z1},
            "end": {"X": x2, "Y": y2, "Z": z2},
            "delta_x": dx,
            "delta_y": dy,
            "delta_z": dz,
            "longitud_3d": longitud_3d,
            "longitud_xy": longitud_xy,
            "longitud_xz": longitud_xz,
            "longitud_yz": longitud_yz,
            "longitud_x": longitud_x,
            "longitud_y": longitud_y,
            "longitud_z": longitud_z,
            "angulo_xy_desde_x": angulo_xy_desde_x,
            "angulo_xy_desde_y": angulo_xy_desde_y,
            "azimut": azimut,
            "angulo_xz_desde_x": angulo_xz_desde_x,
            "angulo_xz_desde_z": angulo_xz_desde_z,
            "inclinacion_en_x": inclinacion_en_x,
            "angulo_yz_desde_y": angulo_yz_desde_y,
            "angulo_yz_desde_z": angulo_yz_desde_z,
            "inclinacion_en_y": inclinacion_en_y,
            "elevacion": elevacion,
            "pendiente_porcentaje": pendiente_porcentaje,
            "angulo_con_eje_x": angulo_con_eje_x,
            "angulo_con_eje_y": angulo_con_eje_y,
            "angulo_con_eje_z": angulo_con_eje_z,
            "coseno_director_x": cos_x,
            "coseno_director_y": cos_y,
            "coseno_director_z": cos_z,
            "angulo_xy_xz": angulo_xy_xz,
            "angulo_xy_yz": angulo_xy_yz,
            "angulo_xz_yz": angulo_xz_yz,
            "cuadrante_xy": cuadrante_xy,
            "octante": octante,
            "tipo_segmento": tipo_segmento,
            "sentido_x": sentido_x,
            "sentido_y": sentido_y,
            "sentido_z": sentido_z,
            "vector": {"X": dx, "Y": dy, "Z": dz},
            "vector_normalizado": {"X": vn_x, "Y": vn_y, "Z": vn_z},
            "angulo_xy": angulo_xy_desde_x,
            "angulo_z": elevacion,
        },
    }


@dataclass
class SegmentMetadata:
    """Metadata for a single polyline segment.

    The library keeps this flexible so installation scripts can attach
    any additional information required to post-process saved paths.
    """

    points: List[Any]
    diameter: float = DEFAULT_SEGMENT_DIAMETER
    section_type: str = DEFAULT_SEGMENT_SECTION_TYPE
    system: str = DEFAULT_SEGMENT_SYSTEM
    label: str = field(default_factory=str)
    layer: Optional[str] = None
    path_id: Optional[int] = None
    segment_id: Optional[int] = None
    color_id: Optional[int] = None
    point_roles: List[int] = field(default_factory=list)
    custom: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_legacy(cls, data: Any) -> "SegmentMetadata":
        """Create metadata from legacy dict structures."""
        if isinstance(data, cls):
            return data

        if isinstance(data, dict):
            points = data.get("points", [])
            diameter = data.get("diameter", DEFAULT_SEGMENT_DIAMETER)
            section_type = data.get("section_type", DEFAULT_SEGMENT_SECTION_TYPE)
            system = data.get("system", DEFAULT_SEGMENT_SYSTEM)
            label = data.get("label", "")
            layer = data.get("layer")
            path_id = data.get("path_id")
            segment_id = data.get("segment_id")
            color_id = data.get("color_id")
            point_roles = data.get("point_roles", [])

            # Copy any additional fields that may exist
            custom_fields = {
                k: v
                for k, v in data.items()
                if k
                not in {
                    "points",
                    "diameter",
                    "section_type",
                    "system",
                    "label",
                    "layer",
                    "path_id",
                    "segment_id",
                    "color_id",
                    "point_roles",
                }
            }

            return cls(
                points=list(points),
                diameter=float(diameter) if isinstance(diameter, (int, float, str)) else DEFAULT_SEGMENT_DIAMETER,
                section_type=str(section_type),
                system=str(system),
                label=str(label),
                layer=str(layer) if layer is not None else None,
                path_id=int(path_id) if path_id is not None else None,
                segment_id=int(segment_id) if segment_id is not None else None,
                color_id=int(color_id) if color_id is not None else None,
                point_roles=list(point_roles) if isinstance(point_roles, (list, tuple)) else [],
                custom=custom_fields,
            )

        # Fallback: treat as empty metadata
        return cls(points=[])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata to a dict for backwards compatibility."""
        base = {
            "points": self.points,
            "diameter": self.diameter,
            "section_type": self.section_type,
            "system": self.system,
            "label": self.label,
        }
        if self.layer is not None:
            base["layer"] = self.layer
        if self.path_id is not None:
            base["path_id"] = self.path_id
        if self.segment_id is not None:
            base["segment_id"] = self.segment_id
        if self.color_id is not None:
            base["color_id"] = self.color_id
        if self.point_roles:
            base["point_roles"] = list(self.point_roles)
        base.update(self.custom)
        return base


@dataclass
class CapturePoint:
    """Stores a capture sample for JSON/export pipelines."""

    point: Any
    path_id: int
    segment_id: int
    role: int
    color_id: int
    order_index: int
    diameter: float = DEFAULT_SEGMENT_DIAMETER
    system: str = DEFAULT_SEGMENT_SYSTEM
    section_type: str = DEFAULT_SEGMENT_SECTION_TYPE
    exported: bool = False
    element_key: Optional[str] = None
    installation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json_dict(self) -> Dict[str, Any]:
        x, y, z = _extract_point_components(self.point)
        payload = {
            "x": float(round(x, 3)),
            "y": float(round(y, 3)),
            "z": float(round(z, 3)),
            "segmento": int(self.segment_id),
            "tipo": CAPTURE_ROLE_LABELS.get(self.role, "Paso"),
            "color": int(self.color_id),
        }
        if self.element_key:
            payload["elemento"] = self.element_key
        if self.installation:
            payload["instalacion"] = self.installation
        if self.metadata:
            payload.update(self.metadata)
        return payload


@dataclass
class FreePointToolConfig:
    """Reusable free-point tool config for capture workflows."""

    pending_property: str
    active_property: Optional[str] = None
    point_store_attr: str = "_free_point"
    place_on_click: bool = True
    create_elements: Optional[Callable[[Any, Any, Any], Any]] = None
    start_message: str = ""
    finish_message: str = ""
    click_success_message: str = "Element placed"
    click_fail_message: str = "Element placement failed"
    invalid_selection_message: str = "Selection is not valid"
    missing_point_message: str = "Select a free point first"
    exclusive: bool = True


# ===== JSON Export Models =====

# Type mapping: library capture roles --> optimizer nodo types
_ROLE_TO_OPTIMIZER_TYPE = {
    "Inicial": "inicio",
    "Paso": "intermedio_obligado",
    "Bifurcacion": "bifurcacion",
    "Final": "final",
}

# Reverse mapping: optimizer nodo types --> library capture roles
_OPTIMIZER_TYPE_TO_ROLE = {
    "inicio": "Inicial",
    "intermedio_obligado": "Paso",
    "intermedio_libre": "Paso",
    "convergencia": "Bifurcacion",
    "bifurcacion": "Bifurcacion",
    "final": "Final",
}


@dataclass
class PuntoModel:
    """Represents a single classified point (nodo) for the JSON export."""

    id: str
    x: float
    y: float
    z: float
    orden: int
    tipo: str
    path_id: int
    segment_id: int
    color_id: int
    diameter: float
    section_type: str
    system: str
    anteriores: List[str] = field(default_factory=list)
    siguientes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Emit optimizer nodo format."""
        return {
            "id": self.id,
            "tipo": _ROLE_TO_OPTIMIZER_TYPE.get(self.tipo, self.tipo),
            "coordenadas": [self.x, self.y, self.z],
            "anteriores": list(self.anteriores),
            "siguientes": list(self.siguientes),
            "metadata": {
                "orden": self.orden,
                "path_id": self.path_id,
                "segment_id": self.segment_id,
                "color_id": self.color_id,
                "diameter": self.diameter,
                "section_type": self.section_type,
                "system": self.system,
            },
        }


@dataclass
class CaminoModel:
    """Represents a complete polyline route for the JSON export.

    One CaminoModel = one full polyline network (all branches/runs)
    expressed as a graph of nodos with anteriores/siguientes connections.
    """

    id: str
    tipo_instalacion: str
    puntos: List[PuntoModel]
    entidades_libres: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "id": self.id,
            "tipo": self.tipo_instalacion,
            "nodos": [p.to_dict() for p in self.puntos],
        }
        if self.entidades_libres:
            result["entidades_libres"] = self.entidades_libres
        if self.metadata:
            result["metadata"] = self.metadata
        return result


def generate_json(
    caminos: List[CaminoModel],
    indent: int = 2,
    layer_default: Optional[Dict[str, Any]] = None,
    selected_inst_type: str = "",
    applied_layers: str = "{}",
    applied_default_attrs: str = "{}",
    applied_custom_attrs: str = "{}",
) -> str:
    """Serialize a list of CaminoModels to the optimizer input JSON.

    Top-level envelope always contains ``caminos`` plus shared metadata.
    """
    payload: Dict[str, Any] = {
        "caminos": [c.to_dict() for c in caminos],
        "layer_default": layer_default or {},
        "selected_inst_type": selected_inst_type,
        "applied_layers": applied_layers,
        "applied_default_attrs": applied_default_attrs,
        "applied_custom_attrs": applied_custom_attrs,
    }
    return json.dumps(payload, ensure_ascii=False, indent=indent)


# Drawing mode constants
DRAWING_MODE_2D = "2D"  # 2D only - Z coordinate forced to 0 (plan view)
DRAWING_MODE_3D_FREE = "3D_FREE"  # 3D free - Z coordinate fully enabled, no restrictions
DRAWING_MODE_3D_CONSTRAINED = "3D_CONSTRAINED"  # 3D with Z jump protection (prevents accidental large jumps)

# Interaction mode constants (create/edit/extend)
MODE_CREATE = 0
MODE_EDIT = 1
MODE_EXTEND = 2


@dataclass
class PolylineBaseConfig:
    """Runtime behavior configuration for polyline interaction.

    Controls interactive behavior flags. Geometry constants (HANDLE_SIZE, etc.)
    should be set directly on the module by installation scripts.
    
    Drawing Modes:
    - DRAWING_MODE_2D: 2D only mode - Z coordinate forced to 0. Use for plan view drawings.
    - DRAWING_MODE_3D_FREE: Full 3D mode - Z coordinate fully enabled, no restrictions. 
                            Use for vertical polylines (drainage stacks, risers) and diagonal segments.
    - DRAWING_MODE_3D_CONSTRAINED: 3D mode with Z jump protection - prevents accidental large Z jumps.
                                   Use for general 3D work where accidental vertical jumps should be prevented.
    
    Examples:
        # For 2D plan view:
        config = PolylineBaseConfig(drawing_mode=DRAWING_MODE_2D)
        
        # For vertical drainage stacks:
        config = PolylineBaseConfig(drawing_mode=DRAWING_MODE_3D_FREE)
        
        # For general 3D with protection:
        config = PolylineBaseConfig(drawing_mode=DRAWING_MODE_3D_CONSTRAINED, z_jump_threshold=200.0)
    """

    limit_angles: bool = False  # Enable angle limiting (snap to predefined increments)
    enable_z_coordinate: bool = True  # Enable Z coordinate input (DEPRECATED: use drawing_mode instead)
    drawing_mode: str = DRAWING_MODE_3D_CONSTRAINED  # Drawing mode: DRAWING_MODE_2D, DRAWING_MODE_3D_FREE, or DRAWING_MODE_3D_CONSTRAINED
    z_jump_threshold: float = 100.0  # Maximum Z change allowed in CONSTRAINED mode (mm)
    allow_insert_point_mode: bool = False  # Allow inserting points on segments
    enable_capture_mode: bool = False  # Enable PointInput-style capture workflow
    capture_auto_commit_on_final: bool = True  # Auto-finalize runs when role == Final
    capture_auto_export_json: bool = True  # Export JSON after commit
    capture_finish_on_cancel: bool = True  # Finish all pending paths on cancel
    capture_json_path: Optional[str] = None  # Optional override for route_groups JSON path
    capture_handler_class: Optional[type] = None  # Custom handler class (subclass PointInputCaptureHandler)
    free_point_tools: Optional[Dict[str, "FreePointToolConfig"]] = None  # Generic free-point tools handled by PointInputCaptureHandler
    registry_auto_load: bool = False  # Discover installations automatically
    registry_base_folder: str = "Instalaciones"
    registry_search_paths: Optional[List[str]] = None
    default_installation: Optional[str] = None
    installation_name_property: str = PALETTE_PROP_INSTALLATION_NAME
    element_key_property: str = PALETTE_PROP_ELEMENT_KEY
    installation_type_property: str = PALETTE_PROP_INSTALLATION_TYPE
    supported_angles_property: str = PALETTE_PROP_SUPPORTED_ANGLES
    point_mode_property: str = PALETTE_PROP_POINT_MODE
    sync_palette_with_registry: bool = False  # Ensure palette combos mirror registry
    
    # System-to-diameter property mapping (installation-agnostic)
    # Maps system identifier (int index or str name) to palette property name for diameter.
    # Example: {0: "DiametroPrincipal", 1: "DiametroSecundario"} or {"Principal": "DiametroPrincipal"}
    system_diameter_mapping: Optional[Dict[Union[int, str], str]] = None


@dataclass
class PolylineResult:
    """Result returned to the caller after user acceptance."""

    points: List[Point3D] = field(default_factory=list)
    is_closed: bool = False


# ===== Helper Functions =====
def get_effective_drawing_mode(config: PolylineBaseConfig) -> str:
    """Get effective drawing mode from config (handles backward compatibility).
    
    Args:
        config: PolylineBaseConfig instance
        
    Returns:
        Effective drawing mode string (DRAWING_MODE_2D, DRAWING_MODE_3D_FREE, or DRAWING_MODE_3D_CONSTRAINED)
    """
    # Backward compatibility: if enable_z_coordinate is explicitly False, use 2D mode
    if not config.enable_z_coordinate:
        return DRAWING_MODE_2D
    return config.drawing_mode


def should_enable_z_coordinate(config: PolylineBaseConfig) -> bool:
    """Determine if Z coordinate should be enabled based on drawing mode.
    
    Args:
        config: PolylineBaseConfig instance
        
    Returns:
        True if Z coordinate should be enabled, False for 2D mode
    """
    effective_mode = get_effective_drawing_mode(config)
    return (effective_mode != DRAWING_MODE_2D)


# ===== ScriptObject Implementation =====
class PolylineScriptObject(BaseScriptObject if ALLPLAN_AVAILABLE else object):  # type: ignore
    """ScriptObject for polyline creation and editing.

    Maintains state between interactions and handles element creation.
    """

    def __init__(self, build_ele, script_object_data):
        if ALLPLAN_AVAILABLE:
            super().__init__(script_object_data)
        self.build_ele = build_ele
        self.script_object_interactor: Optional[PolylineInteractor] = None

        # Store polyline paths and segments
        self.saved_segments: List[SegmentMetadata] = []
        self.saved_paths: List[List[Any]] = []
        # Store free-point entities (macros/defined elements) managed by library tools
        self.saved_free_entities: List[Dict[str, Any]] = []
        
        # Flag to control whether 3D models should be created on exit
        # False = Save mode (just save polyline, no 3D models)
        # True = Finalize mode (save + create 3D models)
        self._should_create_3d_models: bool = True  # Default: create 3D models (for ESC key)
        
        # BIFURCATION: Endpoints are stored in module-level _persistent_finalized_endpoints
        # This persists across ScriptObject instances (Allplan creates new instances per session)
        # Access via: _persistent_finalized_endpoints (module-level)

        # Store configuration
        self._config: Optional[PolylineBaseConfig] = None

        # Element assembly hooks (callbacks for installations to customize element creation)
        self.element_creation_hook: Optional[callable] = None  # Called for each segment: hook(segment_meta, common_prop) -> List[ModelElement3D]
        self.post_process_hook: Optional[callable] = None  # Called after all elements created: hook(elements, script_object) -> List[ModelElement3D]
        
        # Event handler hook (for installations to handle custom button events)
        # Signature: hook(build_ele, event_id: int) -> bool
        # Return True if event was handled, False or None to allow library default handling
        self.event_handler_hook: Optional[callable] = None
        
        # Instrumentation/debugging
        self._debug = False  # Enable debug logging
        self._diagnostics: List[str] = []  # Store diagnostic messages
        self._skip_execute_geometry = False
        self._preserve_saved_state = False
        self._suppress_execute = False

    def set_config(self, config: PolylineBaseConfig) -> None:
        """Set the configuration for this script object."""
        self._config = config
        if config.registry_auto_load:
            try:
                registry_auto_load_installations(
                    config.registry_base_folder, config.registry_search_paths
                )
            except Exception:
                pass

        if config.sync_palette_with_registry:
            try:
                ensure_installation_palette(
                    self.build_ele,
                    installation_name=config.default_installation,
                    installation_property=config.installation_name_property,
                    element_key_property=config.element_key_property,
                    installation_type_property=config.installation_type_property,
                    supported_angles_property=config.supported_angles_property,
                )
            except Exception:
                pass

    def start_input(self):
        """Initialize the interactor and start input.
        
        Returns the interactor so Allplan can call its methods (on_cancel_function, etc.)
        """
        print("\n" + "="*80)
        print("[SO] PolylineScriptObject.start_input() CALLED")
        print(f"[SO] coord_input exists: {hasattr(self, 'coord_input')}")
        print(f"[SO] coord_input value: {getattr(self, 'coord_input', None)}")
        print("="*80)
        
        # CRITICAL: Reuse existing interactor if it exists (preserves state when toggling modes)
        # This prevents losing the interactor when Allplan calls start_input() multiple times
        if self.script_object_interactor is None:
            print("[SO] Creating PolylineInteractor...")
            self.script_object_interactor = PolylineInteractor(self, self._config)
            print(f"[SO] Interactor created: {type(self.script_object_interactor)}")
        else:
            print("[SO] Reusing existing interactor (preserving state)")

        # Reset execute skip flag for new session
        self._skip_execute_geometry = False
        
        # If we have saved paths, enter edit mode
        if self.saved_paths and len(self.saved_paths) > 0:
            # Don't force create_mode - let it sync from palette
            # self.script_object_interactor.create_mode = True
            # Load the first path into the active points for editing (only if no active points)
            if len(self.saved_paths[0]) > 0 and len(self.script_object_interactor.points) == 0:
                self.script_object_interactor.points = list(self.saved_paths[0])
        
        if hasattr(self, 'coord_input') and self.coord_input is not None:
            print("[SO] Calling interactor.start_input() with coord_input...")
            self.script_object_interactor.start_input(self.coord_input)
            print("[SO] Interactor started successfully")
        else:
            print("[SO] WARNING: coord_input not available, interactor not fully initialized")
        
        print(f"[SO] Returning interactor to Allplan: {self.script_object_interactor}")
        print("[SO] start_input() complete\n")
        
        # CRITICAL: Return the interactor so Allplan can call its methods (on_cancel_function, etc.)
        return self.script_object_interactor

    def start_next_input(self):
        """Cleanup resources when transitioning to next input or shutting down."""
        try:
            if self.script_object_interactor is not None:
                intr = self.script_object_interactor
                if intr and getattr(intr, 'capture_handler', None) is not None:
                    intr.capture_handler.on_shutdown(reason="start_next_input")
                if hasattr(self.script_object_interactor, '_cleanup_resources'):
                    self.script_object_interactor._cleanup_resources()

            if not self._preserve_saved_state:
                self.saved_segments.clear()
                self.saved_paths.clear()
                self.saved_free_entities.clear()
            self.script_object_interactor = None
            self._preserve_saved_state = False
        except Exception as ex:
            print(f"[SO] Error during cleanup in start_next_input: {ex}")
            self.script_object_interactor = None

    def _build_elements_for_creation(self) -> List[Any]:
        """Build element list from saved paths/segments for creation."""
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        elements: List[Any] = []

        print(f"[LIBRARY] Creating simple line blueprint for {len(self.saved_segments)} segments...")
        interactor = getattr(self, "script_object_interactor", None)
        element_creation_hook = getattr(self, "element_creation_hook", None)
        skip_geometry = bool(getattr(self, "_skip_execute_geometry", False))
        for seg_idx, segment_info in enumerate(self.saved_segments):
            print(f"[LIBRARY] Segment {seg_idx + 1}/{len(self.saved_segments)}")
            seg_meta = SegmentMetadata.from_legacy(segment_info)
            pts = seg_meta.points
            if len(pts) >= 2:
                segment_prop = AllplanBaseElements.CommonProperties()
                segment_prop.GetGlobalProperties()

                print(f"[LIBRARY]   Creating simple line for PythonPart blueprint")
                line = AllplanGeo.Line3D(pts[0], pts[1])
                elements.append(AllplanBasisElements.ModelElement3D(segment_prop, line))

                if element_creation_hook is not None and not skip_geometry:
                    try:
                        if interactor is not None and hasattr(interactor, "_segment_to_world_coordinates"):
                            world_seg_meta = interactor._segment_to_world_coordinates(seg_meta)
                        else:
                            world_seg_meta = seg_meta
                        hook_elements = element_creation_hook(world_seg_meta, segment_prop)
                        if hook_elements:
                            elements.extend(hook_elements)
                    except Exception as ex:
                        if self._debug:
                            self._add_diagnostic(f"Error in element_creation_hook: {ex}")

        for pts in self.saved_paths:
            if len(pts) >= 2:
                poly = AllplanGeo.Polyline3D()
                for pt in pts:
                    poly += pt
                elements.append(AllplanBasisElements.ModelElement3D(com_prop, poly))

        # Build persisted free-point entities (macro / defined element) through configured tool callbacks.
        free_entities = getattr(self, "saved_free_entities", []) or []
        if free_entities and interactor is not None and hasattr(interactor, "_build_free_entity_elements"):
            for entity in free_entities:
                try:
                    built = interactor._build_free_entity_elements(entity)
                    if built:
                        elements.extend(built)
                except Exception as ex:
                    if self._debug:
                        self._add_diagnostic(f"Error rebuilding free entity: {ex}")

        if self.post_process_hook is not None:
            try:
                elements = self.post_process_hook(elements, self)
            except Exception as ex:
                if self._debug:
                    self._add_diagnostic(f"Error in post_process_hook: {ex}")

        return elements

    def _wrap_elements_in_pythonpartgroup(self, elements: List[Any]) -> List[Any]:
        """Wrap elements into a PythonPartGroup for editability."""
        from PythonPart import PythonPartGroup, PythonPart, View2D3D  # type: ignore
        import NemAll_Python_AllplanSettings as AllplanSettings  # type: ignore
        import hashlib
        import random

        pythonparts_list = []
        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, "pyp_file_name") else ""

        def _hash():
            return hashlib.sha224(str(random.randint(10**15, 10**16 - 1)).encode("utf-8")).hexdigest()

        for idx, element in enumerate(elements):
            try:
                common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                try:
                    common_props = element.GetCommonProperties()
                except Exception:
                    pass

                attribute_list = []
                try:
                    if hasattr(element, "GetAttributes"):
                        attrs = element.GetAttributes()
                        if attrs:
                            for attr_set in attrs.GetAttributeSets():
                                attribute_list.extend(list(attr_set.GetAttributes()))
                                break
                except Exception:
                    pass

                views = [View2D3D([element])]
                params = {"ElementIndex": idx}
                param_list = [f"{k} = {v}\n" for k, v in sorted(params.items())]

                pythonpart = PythonPart(
                    f"PolylineElement_{idx}",
                    parameter_list=param_list,
                    hash_value=_hash(),
                    python_file=python_file_name,
                    views=views,
                    common_props=common_props,
                    attribute_list=attribute_list,
                )
                pythonparts_list.append(pythonpart)
            except Exception as ex:
                if self._debug:
                    self._add_diagnostic(f"Error creating PythonPart element: {ex}")

        intr = getattr(self, "script_object_interactor", None)
        state_json = ""
        if intr is not None and hasattr(intr, "_serialize_state_to_json"):
            state_json = intr._serialize_state_to_json()

        group_params = {
            "TotalElements": len(pythonparts_list),
        }
        if state_json:
            group_params["SavedState"] = state_json

        group_param_list = [f"{k} = {v}\n" for k, v in sorted(group_params.items())]
        group = PythonPartGroup(
            "PolylineGroup",
            group_param_list,
            _hash(),
            python_file_name,
            pythonparts_list,
        )
        return group.create()

    def execute(self):
        """Create elements from saved paths/segments.

        Returns CreateElementResult with model elements.
        Supports element creation hooks for installations to customize element creation.
        """
        print("\n" + "="*80)
        print("[LIBRARY] execute() CALLED!")
        print(f"[LIBRARY] saved_segments count: {len(self.saved_segments)}")
        print(f"[LIBRARY] saved_paths count: {len(self.saved_paths)}")
        print("="*80)

        if self._suppress_execute:
            self._suppress_execute = False
            try:
                from CreateElementResult import CreateElementResult  # type: ignore
                return CreateElementResult([])
            except Exception:
                return []

        if not ALLPLAN_AVAILABLE:
            print("[LIBRARY] execute: Allplan not available")
            return []

        try:
            from CreateElementResult import CreateElementResult  # type: ignore
        except Exception:
            print("[LIBRARY] execute: Could not import CreateElementResult")
            return []

        free_entities = getattr(self, "saved_free_entities", []) or []
        if not self.saved_paths and not self.saved_segments and not free_entities:
            # Try restoring from persisted SavedState (save-driven flow)
            try:
                interactor = getattr(self, "script_object_interactor", None)
                if interactor is None:
                    interactor = PolylineInteractor(self, self._config)
                if interactor is not None and hasattr(interactor, "_restore_saved_state"):
                    restored = interactor._restore_saved_state()
                    if restored:
                        print("[LIBRARY] execute: Restored saved state from build_ele")
            except Exception as ex:
                print(f"[LIBRARY] execute: Could not restore saved state: {ex}")

        free_entities = getattr(self, "saved_free_entities", []) or []
        if not self.saved_paths and not self.saved_segments and not free_entities:
            print("[LIBRARY] execute: No paths or segments to create")
            return CreateElementResult([])

        elements = self._build_elements_for_creation()

        try:
            create_group_prop = getattr(self.build_ele, "CreatePythonPartGroup", None)
            create_group = bool(getattr(create_group_prop, "value", create_group_prop)) if create_group_prop else False
        except Exception:
            create_group = False

        if create_group:
            try:
                group_elements = self._wrap_elements_in_pythonpartgroup(elements)
                print(f"\n[LIBRARY] execute() returning PythonPartGroup with {len(group_elements)} elements")
                print("="*80 + "\n")
                return CreateElementResult(group_elements)
            except Exception as ex:
                if self._debug:
                    self._add_diagnostic(f"Error creating PythonPartGroup: {ex}")

        print(f"\n[LIBRARY] execute() returning {len(elements)} elements")
        print("="*80 + "\n")
        return CreateElementResult(elements)
    
    def on_cancel_function(self):
        """ESC pressed - delegate to interactor if it exists."""
        print("[SO] on_cancel_function() called")
        
        if self.script_object_interactor is not None:
            print("[SO] Delegating to interactor")
            return self.script_object_interactor.on_cancel_function()
        else:
            print("[SO] No interactor - returning CREATE_ELEMENTS")
            if ALLPLAN_AVAILABLE:
                try:
                    from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
                    return OnCancelFunctionResult.CREATE_ELEMENTS
                except Exception as ex:
                    print(f"[SO] ERROR importing OnCancelFunctionResult: {ex}")
        return None

    def on_control_event(self, event_id: int):
        """Handle palette button events.
        
        EventIds:
        - 1002: Save Polyline (save current polyline to saved_paths)
        - 1003: Finalize & Create (save + create 3D models + exit)
        - 1004: Delete segment
        """
        print(f"[SO] Event received: {event_id}")
        
        # Ensure interactor exists
        if self.script_object_interactor is None:
            print(f"[SO] Creating interactor...")
            try:
                self.start_input()
            except Exception as ex:
                print(f"[SO] Error creating interactor: {ex}")
                return False
        
        intr = self.script_object_interactor
        
        def _finalize_now():
            """Save, create 3D models, and exit the interaction."""
            try:
                if intr:
                    print("[SO] Saving current polyline...")
                    intr.save_current_polyline()
                    try:
                        intr._persist_state_to_build_ele()
                    except Exception:
                        pass
                    self._preserve_saved_state = True

                    # Create 3D geometry immediately only when not creating a PythonPartGroup
                    try:
                        create_group = False
                        build_ele = getattr(self, "build_ele", None)
                        create_group_prop = getattr(build_ele, "CreatePythonPartGroup", None) if build_ele else None
                        if create_group_prop is not None:
                            create_group = bool(getattr(create_group_prop, "value", create_group_prop))
                        if create_group:
                            try:
                                elements = self._build_elements_for_creation()
                                group_elements = self._wrap_elements_in_pythonpartgroup(elements)
                                if group_elements and ALLPLAN_AVAILABLE and self.coord_input is not None:
                                    doc = self.coord_input.GetInputViewDocument()
                                    AllplanBaseElements.CreateElements(
                                        doc,
                                        AllplanGeo.Matrix3D(),
                                        group_elements,
                                        [],
                                        None,
                                    )
                                    self._suppress_execute = True
                            except Exception as ex:
                                if self._debug:
                                    self._add_diagnostic(f"Error creating PythonPartGroup immediately: {ex}")
                        else:
                            intr._create_elements_immediately()
                            self._skip_execute_geometry = True
                            self._suppress_execute = True  # execute() must return [] to avoid duplicate creation
                    except Exception:
                        pass
                
                # Show success message dialog BEFORE clearing data (like Saneamiento!)
                try:
                    self._show_finalize_success_dialog(intr)
                except Exception as dlg_ex:
                    print(f"[SO] Could not show success dialog: {dlg_ex}")
                
                print("[SO] Creating 3D models...")
                self._finalize_and_create_now()
                
                if intr:
                    # BIFURCATION: Store endpoints BEFORE clearing saved_paths!
                    print("[SO] Storing endpoints for bifurcation...")
                    try:
                        intr._store_polyline_endpoints()
                    except Exception as store_ex:
                        print(f"[SO] Warning: Could not store endpoints: {store_ex}")
                    
                    # NOTE: Do NOT clear saved_paths here - they are needed for execute() to create models!
                    # saved_paths will be cleared after execute() completes
                    print("[SO] Keeping saved_paths for execute() (will clear after model creation)...")
                    
                    # Clear all preview elements before creating final geometry
                    print("[SO] Clearing preview elements...")
                    try:
                        intr._clear_preview()
                    except Exception as clear_ex:
                        print(f"[SO] Warning: Could not clear preview: {clear_ex}")
                
                # Call coord_input cancel to exit the interaction
                print("[SO] Exiting interaction...")
                # Guard: finalize button path already created/rebuilt geometry.
                # The upcoming CancelInput() callback must not run another recreate pass.
                self._skip_on_cancel_recreate_once = True
                for name in ("CancelFunction", "OnCancelFunction", "CancelInput", "Cancel"):
                    meth = getattr(self.coord_input, name, None)
                    if callable(meth):
                        try:
                            meth()
                            print(f"[SO] Called coord_input.{name}() successfully")
                            break
                        except Exception as ex:
                            print(f"[SO] coord_input.{name}() ex: {ex}")
                return True
            except Exception as ex:
                print(f"[SO] Error in finalize: {ex}")
                import traceback
                traceback.print_exc()
                return False
        
        # Event handlers for library-defined events
        def _save_now():
            try:
                if intr:
                    intr.save_current_polyline()
                    try:
                        intr._persist_state_to_build_ele()
                    except Exception:
                        pass
                    self._preserve_saved_state = True
                print(f"[SO] Saved: {len(self.saved_paths)} polylines, {len(self.saved_segments)} segments")
                return True
            except Exception as ex:
                print(f"[SO] Error during save: {ex}")
                return False

        def _delete_now():
            try:
                if not intr:
                    return False
                deleted = intr.delete_selected_or_hovered_segment()
                if deleted:
                    intr._draw_preview(getattr(intr, "current_point", None))
                else:
                    intr._update_status("Delete: sin segmento activo")
                return bool(deleted)
            except Exception as ex:
                print(f"[SO] Error during delete: {ex}")
                try:
                    intr._update_status("Delete: error interno")
                except Exception:
                    pass
                return False

        handlers = {
            1002: _save_now,
            1003: _finalize_now,
            1004: _delete_now,
            1010: lambda: self._set_origin_to_current() if intr else False,
        }
        
        try:
            # First, check if installation has registered a custom event handler
            if self.event_handler_hook and callable(self.event_handler_hook):
                try:
                    result = self.event_handler_hook(self.build_ele, event_id)
                    # If handler returns True (or any truthy value), event was handled - don't process further
                    if result:
                        print(f"[SO] Event {event_id} handled by installation's event_handler_hook (returned: {result})")
                        return True
                    # If handler returns False/None, continue to library handlers
                    print(f"[SO] Event {event_id} hook returned False/None, checking library handlers")
                except Exception as hook_ex:
                    print(f"[SO] Error in installation event handler: {hook_ex}")
                    import traceback
                    traceback.print_exc()
                    # Continue to library handlers on error
            
            # Check library's built-in handlers
            handler = handlers.get(event_id)
            if handler:
                return bool(handler())
            
            # Event not handled - return True to allow propagation
            print(f"[SO] Event {event_id} not handled by library, allowing propagation")
            return True
        except Exception as ex:
            print(f"[SO] Error processing event {event_id}: {ex}")
            import traceback
            traceback.print_exc()
            return False

    def _add_diagnostic(self, message: str) -> None:
        """Add a diagnostic message for debugging."""
        if self._debug:
            self._diagnostics.append(message)
            print(f"[SO] {message}")

    def get_diagnostics(self) -> List[str]:
        """Get accumulated diagnostic messages."""
        return list(self._diagnostics)

    def clear_diagnostics(self) -> None:
        """Clear diagnostic messages."""
        self._diagnostics.clear()

    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug logging."""
        self._debug = enabled
        if self.script_object_interactor is not None:
            self.script_object_interactor._debug = enabled

    def _finalize_and_create_now(self):
        """Materialize saved paths immediately in the document.
        
        Note: In pure interactor mode, this is overridden to not create elements.
        """
        # Default implementation: execute() is called separately by Allplan
        # This method can be overridden for immediate creation if needed

    def _show_finalize_success_dialog(self, interactor):
        """Show success message dialog after polyline is finalized (like Saneamiento!).
        
        Args:
            interactor: The PolylineInteractor instance with polyline data
        """
        if not ALLPLAN_AVAILABLE:
            return
        
        try:
            # Collect statistics
            num_segments = len(self.saved_segments)
            num_paths = len(self.saved_paths) if hasattr(self, 'saved_paths') else 0
            
            # Count total points across all paths
            total_points = 0
            for path in self.saved_paths:
                total_points += len(path)
            
            # Check if creating as PythonPart group
            is_group = False
            create_group_prop = getattr(self.build_ele, "CreatePythonPartGroup", None)
            if create_group_prop:
                is_group = create_group_prop.value
            
            # Build message text (matching Saneamiento style)
            message_lines = [
                "✓ Polyline saved successfully!",
                "",
                f"New polyline #{num_paths}",
                f"Points: {total_points}",
                f"Segments: {num_segments}",
            ]
            
            if is_group:
                message_lines.append("Type: PythonPart Group")
            else:
                message_lines.append("Type: Standard Elements")
            
            message_lines.append("")
            message_lines.append(f"Total polylines: {num_paths}")
            
            message = "\n".join(message_lines)
            
            # Show dialog using Windows MessageBox (most reliable in Allplan)
            try:
                import ctypes
                MB_OK = 0x0
                MB_ICONINFORMATION = 0x40
                MB_TOPMOST = 0x40000
                
                # Show modal dialog on top of Allplan
                ctypes.windll.user32.MessageBoxW(
                    0, 
                    message, 
                    "Polyline Library", 
                    MB_OK | MB_ICONINFORMATION | MB_TOPMOST
                )
                print(f"[SO] ✓ Success dialog shown")
            except Exception as dlg_ex:
                print(f"[SO] Could not show dialog: {dlg_ex}")
                # Fallback: print to console
                print("\n" + "="*60)
                print(message)
                print("="*60 + "\n")
        
        except Exception as ex:
            print(f"[SO] Error creating success dialog: {ex}")
            import traceback
            traceback.print_exc()

    def _set_origin_to_current(self):
        """Set the origin to the current cursor position or last point."""
        try:
            if self.script_object_interactor is None:
                print("[SO] No interactor - cannot get current position")
                return False
            
            # Try current_point first (mouse position)
            current_pnt = getattr(self.script_object_interactor, 'current_point', None)
            
            # If no current_point, use last clicked point
            if current_pnt is None:
                points = getattr(self.script_object_interactor, 'points', [])
                if points and len(points) > 0:
                    current_pnt = points[-1]  # Use last clicked point
                    print(f"[SO] Using last clicked point as origin")
                else:
                    print("[SO] No current point or clicked points available")
                    return False
            
            if not ALLPLAN_AVAILABLE:
                print("[SO] Allplan not available")
                return False
            
            # Update origin values in palette
            start_x = getattr(self.build_ele, "StartX", None)
            start_y = getattr(self.build_ele, "StartY", None)
            start_z = getattr(self.build_ele, "StartZ", None)
            
            if start_x:
                start_x.value = float(current_pnt.X)
            if start_y:
                start_y.value = float(current_pnt.Y)
            if start_z:
                start_z.value = float(current_pnt.Z)
            
            print(f"[SO] ✓ Origin set to: X={current_pnt.X:.2f}, Y={current_pnt.Y:.2f}, Z={current_pnt.Z:.2f}")
            print(f"[SO] Coordinates will now display relative to this point!")
            return True
        except Exception as ex:
            print(f"[SO] Error setting origin: {ex}")
            import traceback
            traceback.print_exc()
            return False

    def modify_element_property(self, *args):
        """Handle palette property changes.
        
        Supports FinishNow parameter for capture mode to manually finalize current path.
        
        Args:
            *args: Either (name, value) or (page, name, value)
            
        Returns:
            True if property was handled, False otherwise
        """
        try:
            # Parse arguments
            if len(args) == 2:
                name, value = args
            elif len(args) == 3:
                _page, name, value = args
            else:
                return False
            
            # Handle FinishNow parameter for capture mode
            if name == PALETTE_PROP_FINISH_NOW and bool(value):
                intr = self.script_object_interactor
                if intr and getattr(intr, 'capture_handler', None) is not None:
                    intr.capture_handler.check_finish_now()
                    return True
            
            # Delegate other property changes to interactor if it has a handler
            if self.script_object_interactor:
                # Check if interactor has a modify_element_property method
                if hasattr(self.script_object_interactor, 'modify_element_property'):
                    try:
                        return self.script_object_interactor.modify_element_property(*args)
                    except Exception:
                        pass
            
            return False
        except Exception as ex:
            print(f"[SO] Error in modify_element_property: {ex}")
            import traceback
            traceback.print_exc()
            return False


# ===== Interactor Implementation =====
class PolylineInteractor:
    """Interactor for polyline creation and editing.

    Handles mouse input, preview drawing, and state management.
    """

    def __init__(self, script_object: PolylineScriptObject, config: Optional[PolylineBaseConfig] = None):
        self.script_object = script_object
        self.config: PolylineBaseConfig = config or PolylineBaseConfig()

        if getattr(self.config, "registry_auto_load", False):
            try:
                registry_auto_load_installations(
                    self.config.registry_base_folder, self.config.registry_search_paths
                )
            except Exception:
                pass

        self.installation_name_property = self.config.installation_name_property
        self.element_key_property = self.config.element_key_property
        self.installation_type_property = self.config.installation_type_property
        self.supported_angles_property = self.config.supported_angles_property
        self.point_mode_property = self.config.point_mode_property
        self.current_installation: Optional[str] = self.config.default_installation

        # Active polyline (being created/edited)
        self.mode = MODE_EDIT
        self.create_mode = False
        self.points: List[Any] = []
        self.current_point: Any = None
        self._last_preview_point: Any = None
        self._force_edit_mode: bool = False
        self._mode_set_by_palette: bool = False
        self._extend_anchor: Optional[Any] = None
        self.is_modification_mode = False

        # Editing state
        self.hover_index = -1
        self.drag_index = -1
        self.is_dragging = False
        
        # Auto-origin flag
        self._origin_auto_set = False
        
        # Debug flags (log only once)
        self._debug_logged_mouse_attrs = False
        self._debug_logged_clear_methods = False
        # Handle draw logging (removed - was causing spam)

        # Insert mode
        self.insert_mode = bool(self.config.allow_insert_point_mode)
        self.insert_preview_p: Optional[Any] = None
        self.insert_target: Optional[Tuple] = None

        # Segment hover/selection
        self.hover_seg: Optional[Tuple] = None
        self.selected_seg: Optional[Tuple] = None
        self.hover_mid: Optional[Tuple] = None
        self.hover_vertex: Optional[Tuple] = None  # (path_idx, vertex_idx) for vertex hover feedback
        self.hover_free_entity: Optional[int] = None
        self.selected_free_entity: Optional[int] = None
        
        # Edit mode dragging
        self.drag_path_idx: Optional[int] = None
        self.drag_vertex_idx: Optional[int] = None
        self.drag_free_entity_idx: Optional[int] = None
        self._drag_start_point: Optional[Any] = None
        self._drag_start_path: Optional[List[Any]] = None  # Store original path positions for entire path dragging
        self._last_button_state: Optional[int] = None  # Track button state to detect release

        # Capture workflow state
        self.capture_mode = bool(self.config.enable_capture_mode)
        handler_cls = self.config.capture_handler_class or PointInputCaptureHandler
        self.capture_handler: Optional[PointInputCaptureHandler] = (
            handler_cls(self, self.config) if self.capture_mode else None
        )

        # Undo/Cancel state
        self._undo_stack: List[Dict[str, Any]] = []  # Stack of state snapshots for undo
        self._max_undo_depth = 50  # Maximum undo operations to store
        self._initial_state: Optional[Dict[str, Any]] = None  # Snapshot of initial state for cancel

        # Branching & Fittings hooks (callbacks for installations to plug in custom logic)
        self.branching_hook: Optional[Callable[[Any, SegmentMetadata], List[Any]]] = None
        self.fitting_hook: Optional[Callable[[str, SegmentMetadata, SegmentMetadata], List[Any]]] = None
        self.elbow_hook: Optional[Callable[[SegmentMetadata, SegmentMetadata, float], List[Any]]] = None
        self.reducer_hook: Optional[Callable[[SegmentMetadata, SegmentMetadata, float, float], List[Any]]] = None
        self.bifurcation_hook: Optional[Callable[[SegmentMetadata, SegmentMetadata, SegmentMetadata], List[Any]]] = None

        # Bifurcation support: Store finalized polyline endpoints for continuation
        # BIFURCATION: Use ScriptObject's persistent endpoints (not local to interactor!)
        # This ensures endpoints persist across sessions
        # Access via: self.script_object.finalized_endpoints
        self.bifurcation_snap_distance = 80.0  # mm - distance to snap to existing endpoint
        
        # Coordinate input
        self.coord_input: Optional[Any] = None

        # Debug flag
        self._debug = False

        # Angle limiting (from installation registry or module defaults)
        self.angle_steps: Optional[List[float]] = None

        # Properties
        if ALLPLAN_AVAILABLE:
            self.com_prop = AllplanBaseElements.CommonProperties()
            self.com_prop.GetGlobalProperties()
        else:
            self.com_prop = None

        self._apply_installation_angles()

        # Note: Module constants (HANDLE_SIZE, HIT_TOL_VERTEX, etc.) are read directly.
        # Installation scripts should modify these module constants before creating the ScriptObject.

    @property
    def capture_records(self) -> List[CapturePoint]:
        """Capture records (delegates to handler when capture mode enabled)."""
        if self.capture_handler is not None:
            return self.capture_handler.records
        return []

    def start_input(self, coord_input):
        """Start input with the coordinate input handler."""
        print("\n" + "="*80)
        print("[INT] PolylineInteractor.start_input() CALLED")
        print(f"[INT] coord_input type: {type(coord_input)}")
        print("="*80)
        
        self.coord_input = coord_input
        
        # CRITICAL: Clear any preview from previous session
        try:
            self._clear_preview()
            print("[INT] Cleared preview from previous session")
        except:
            pass
        
        # Bifurcation endpoints: load from cache for drawing mode (NOT for capture mode - PointInput_SO has no bifurcation)
        global _persistent_finalized_endpoints
        if not self.capture_mode:
            _persistent_finalized_endpoints = _load_endpoints_from_cache()
            endpoint_count = len(_persistent_finalized_endpoints)
            print(f"[INT] ✓ Loaded {endpoint_count} bifurcation endpoints from cache (file-based persistence)")
            if endpoint_count > 0:
                for i, ep in enumerate(_persistent_finalized_endpoints[:3]):  # Show first 3
                    if hasattr(ep, 'X'):
                        print(f"[INT]   Endpoint {i+1}: ({ep.X:.1f}, {ep.Y:.1f}, {ep.Z:.1f})")
                if endpoint_count > 3:
                    print(f"[INT]   ... and {endpoint_count - 3} more")
        else:
            _persistent_finalized_endpoints = []  # Capture mode: start fresh, no cached endpoints
        
        self._mode_set_by_palette = False
        self.insert_mode = bool(self.config.allow_insert_point_mode)
        print(f"[INT] insert_mode (from config): {self.insert_mode}")
        print(f"[INT] mode (before sync): {self.mode}")
        
        # Set initial status
        self._update_status("Ready to draw")
        
        self.sync_installation_from_palette()
        
        # CRITICAL: Sync mode from palette at startup
        self._sync_create_mode_from_palette()
        self._sync_insert_mode_from_palette()
        print(f"[INT] mode (after sync): {self.mode}")

        # Restore saved state when available (double-click on PythonPart or manual re-entry).
        # IMPORTANT: modification mode must restore state even if capture_mode is enabled.
        self._detect_modification_mode()
        restored = False
        if self.is_modification_mode:
            restored = self._restore_saved_state()
        elif not self.capture_mode:
            restored = self._restore_saved_state()
        elif hasattr(self.script_object, 'saved_paths'):
            # Fresh capture session (non-modification): start clean like PointInput_SO.
            self.script_object.saved_paths.clear()
            if hasattr(self.script_object, 'saved_segments'):
                self.script_object.saved_segments.clear()
        if restored or self.is_modification_mode:
            self._apply_mode(MODE_EDIT, source="modification")
            self._safe_set_palette_property(PALETTE_PROP_MODE, MODE_EDIT)
            self._safe_set_palette_property(self.point_mode_property, MODE_EDIT)
            self._safe_set_palette_property(PALETTE_PROP_CREATE_MODE, False)
            self._force_edit_mode = True
            if self._last_preview_point is None and self.script_object.saved_paths:
                try:
                    self._last_preview_point = self.script_object.saved_paths[0][0]
                except Exception:
                    pass

        # Enable Z coordinate based on drawing mode
        try:
            if hasattr(self.coord_input, "SetEnableZCoordinate"):
                effective_mode = get_effective_drawing_mode(self.config)
                z_enabled = should_enable_z_coordinate(self.config)
                self.coord_input.SetEnableZCoordinate(z_enabled)
                print(f"[INT] Drawing mode: {effective_mode}, Z coordinate enabled: {z_enabled}")
        except Exception as e:
            print(f"[INT] Could not set Z coordinate: {e}")

        if self.capture_mode and not self.is_modification_mode and not restored:
            if not self._mode_set_by_palette:
                self.mode = MODE_CREATE
                self.create_mode = True
            if self._is_create_like_mode() and self.capture_handler:
                self.capture_handler.on_start()

        # If we already have points loaded (from JSON) but are in edit mode, clear active points
        if self.points and not self._is_create_like_mode():
            self.points = []

        # Save initial state for cancel
        self._save_state_snapshot()

        # Set initial prompt
        self._print_prompt()
        print(f"[INT] FINAL mode: {self.mode}")
        try:
            self._draw_preview(self.current_point or self._last_preview_point)
        except Exception:
            pass
        print("[INT] Interactor ready for input\n")

    def _print_prompt(self):
        """Print initial prompt to user."""
        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            return
        try:
            # Use configurable prompt message
            msg = DEFAULT_USER_PROMPT
            if self.capture_mode and self.capture_handler and self._is_create_like_mode():
                role_label = CAPTURE_ROLE_LABELS.get(self.capture_handler.get_point_role(), "Paso")
                msg = f"Path {self.capture_handler.get_path_id()} · {role_label}"
            if self.current_installation:
                msg = f"{msg} · {self.current_installation}"
            self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
        except Exception:
            pass

    # ===== Palette Synchronization =====
    def _safe_get_palette_property(self, property_name: str, default_value: Any = None) -> Any:
        """Safely get a property from the palette.
        
        Args:
            property_name: Name of the palette property to read
            default_value: Value to return if property doesn't exist or can't be read
            
        Returns:
            Property value or default_value
        """
        try:
            if not hasattr(self.script_object, 'build_ele') or self.script_object.build_ele is None:
                return default_value

            if not hasattr(self.script_object.build_ele, property_name):
                return default_value

            prop = getattr(self.script_object.build_ele, property_name)
            if hasattr(prop, "value"):
                return prop.value
            else:
                return prop
        except Exception as ex:
            # Use module-level debug flag if available
            if hasattr(self, '_debug') and self._debug:
                print(f"[INT] Error getting palette property {property_name}: {ex}")
            return default_value

    def _safe_set_palette_property(self, property_name: str, value: Any) -> bool:
        """Safely set a property on the palette.
        
        Args:
            property_name: Name of the palette property to set
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not hasattr(self.script_object, 'build_ele') or self.script_object.build_ele is None:
                return False

            if not hasattr(self.script_object.build_ele, property_name):
                return False

            prop = getattr(self.script_object.build_ele, property_name)
            if hasattr(prop, "value"):
                prop.value = value
            else:
                setattr(self.script_object.build_ele, property_name, value)
            return True
        except Exception as ex:
            if hasattr(self, '_debug') and self._debug:
                print(f"[INT] Error setting palette property {property_name}: {ex}")
            return False

    def _read_installation_from_palette(self) -> Optional[str]:
        if not self.installation_name_property:
            return None
        value = self._safe_get_palette_property(self.installation_name_property)
        if value in (None, ""):
            return None
        return str(value)

    def _apply_installation_angles(self) -> None:
        inst_name = self.current_installation or self.config.default_installation
        if not inst_name:
            return
        inst = registry_get_installation(inst_name)
        if inst is None:
            return
        if inst.angles:
            self.angle_steps = inst.angles
        if inst.angles_read:
            self._safe_set_palette_property(self.supported_angles_property, inst.angles_read)

    def sync_installation_from_palette(self) -> None:
        palette_value = self._read_installation_from_palette()
        if palette_value:
            self.current_installation = palette_value
        elif self.current_installation is None:
            self.current_installation = self.config.default_installation
        self._apply_installation_angles()

    def _normalize_palette_value(self, value: Any) -> Any:
        if hasattr(value, "value"):
            return value.value
        return value

    def _parse_mode_from_palette(self) -> Optional[int]:
        raw_value = self._safe_get_palette_property(PALETTE_PROP_MODE)
        if raw_value is None:
            raw_value = self._safe_get_palette_property(self.point_mode_property)
        if raw_value is None:
            return None
        value = self._normalize_palette_value(raw_value)
        if isinstance(value, str):
            token = value.strip().lower()
            if token in ("create", "crear", "creation", "creacion", "0"):
                return MODE_CREATE
            if token in ("edit", "editar", "edicion", "1"):
                return MODE_EDIT
            if token in ("extend", "extension", "extender", "2"):
                return MODE_CREATE
            return None
        if isinstance(value, (int, float)):
            mode_value = int(value)
            if mode_value == MODE_EXTEND:
                mode_value = MODE_CREATE
            if mode_value in (MODE_CREATE, MODE_EDIT):
                return mode_value
        return None

    def _apply_mode(self, new_mode: int, source: str = "palette") -> None:
        if new_mode not in (MODE_CREATE, MODE_EDIT, MODE_EXTEND):
            return
        if new_mode == self.mode:
            return

        old_mode = self.mode
        self.mode = new_mode
        self.create_mode = (new_mode in (MODE_CREATE, MODE_EXTEND))
        self._extend_anchor = None

        if new_mode == MODE_EDIT:
            if old_mode in (MODE_CREATE, MODE_EXTEND):
                if len(self.points) >= 2:
                    print("[INT] Auto-saving polyline before switching to edit mode")
                    self.save_current_polyline()
            self.points = []
            self.current_point = None
            self.is_dragging = False
            self.drag_index = -1
            try:
                if self.coord_input:
                    edit_msg = AllplanIFW.InputStringConvert("Edit mode: Click segments to select, drag to move")
                    self.coord_input.InitFirstPointInput(edit_msg)
            except Exception:
                pass
            print(f"[INT] Mode switched to EDIT ({source})")
            return

        # Create or extend mode: clear edit selection, keep interactor state
        self.selected_seg = None
        self.hover_seg = None
        self.hover_mid = None
        self.selected_free_entity = None
        self.hover_free_entity = None
        self.is_dragging = False
        self.drag_path_idx = None
        self.drag_vertex_idx = None
        self.drag_free_entity_idx = None
        self._print_prompt()
        if new_mode == MODE_EXTEND:
            self._update_status("Extend mode: click an endpoint to start")
        print(f"[INT] Mode switched to {('CREATE' if new_mode == MODE_CREATE else 'EXTEND')} ({source})")

    def _is_create_mode(self) -> bool:
        return self.mode == MODE_CREATE

    def _is_edit_mode(self) -> bool:
        return self.mode == MODE_EDIT

    def _is_extend_mode(self) -> bool:
        return self.mode == MODE_EXTEND

    def _is_create_like_mode(self) -> bool:
        return self.mode in (MODE_CREATE, MODE_EXTEND)

    def _get_saved_free_entities(self) -> List[Dict[str, Any]]:
        entities = getattr(self.script_object, "saved_free_entities", None)
        if isinstance(entities, list):
            return entities
        self.script_object.saved_free_entities = []
        return self.script_object.saved_free_entities

    def _store_free_entity(self, tool_name: str, point: Any, state: Optional[Dict[str, Any]] = None) -> int:
        entities = self._get_saved_free_entities()
        entities.append({
            "tool": str(tool_name or ""),
            "point": self._clone_point3d(point),
            "state": dict(state) if isinstance(state, dict) else {},
        })
        return len(entities) - 1

    def _build_free_entity_elements(self, entity: Dict[str, Any]) -> List[Any]:
        if not isinstance(entity, dict):
            return []
        tool_name = str(entity.get("tool", "") or "")
        point = entity.get("point", None)
        if point is None:
            return []
        tools = getattr(self.config, "free_point_tools", None)
        if not isinstance(tools, dict):
            return []
        tool_cfg = tools.get(tool_name)
        if tool_cfg is None or not callable(getattr(tool_cfg, "create_elements", None)):
            return []
        build_ele = getattr(self.script_object, "build_ele", None)
        state_payload = entity.get("state", {}) if isinstance(entity, dict) else {}
        setattr(self.script_object, "_free_entity_state", state_payload if isinstance(state_payload, dict) else {})
        try:
            created = tool_cfg.create_elements(point, build_ele, self.script_object)
        finally:
            setattr(self.script_object, "_free_entity_state", None)
        if created is None:
            return []
        if isinstance(created, (list, tuple)):
            return [ele for ele in created if ele is not None]
        return [created]

    def _capture_free_entity_state(self, tool_name: str) -> Dict[str, Any]:
        """Capture tool-relevant palette state for per-entity persistence."""
        state: Dict[str, Any] = {}
        build_ele = getattr(self.script_object, "build_ele", None)
        if build_ele is None:
            return state
        try:
            if tool_name == "element":
                state["DefinedElementType"] = self._safe_get_palette_property("DefinedElementType")
                try:
                    state["ElementColor"] = self._safe_get_palette_property("ElementColor")
                except Exception:
                    pass
            elif tool_name == "macro":
                for key in ("MacroLibraryElementType", "MacroSmartSymbolPath", "MacroFixturePath", "MacroZAbs"):
                    state[key] = self._safe_get_palette_property(key)
        except Exception:
            pass
        return state

    def _sync_create_mode_from_palette(self) -> None:
        """Synchronize mode from palette controls (mode group or legacy checkbox)."""
        try:
            palette_mode = self._parse_mode_from_palette()
        except Exception:
            palette_mode = None
        if self._force_edit_mode or self.is_modification_mode:
            if palette_mode == MODE_CREATE:
                self._force_edit_mode = False
                self._apply_mode(MODE_CREATE, source="palette")
                self._mode_set_by_palette = True
            else:
                return
        try:
            new_mode = palette_mode if palette_mode is not None else self._parse_mode_from_palette()
            if new_mode is None:
                checkbox_value = self._safe_get_palette_property(PALETTE_PROP_CREATE_MODE)
                if checkbox_value is not None:
                    create_enabled = bool(self._normalize_palette_value(checkbox_value))
                    new_mode = MODE_CREATE if create_enabled else MODE_EDIT

            if new_mode is not None:
                self._mode_set_by_palette = True
                if new_mode != self.mode:
                    self._apply_mode(new_mode, source="palette")
        except Exception as e:
            if not hasattr(self, '_sync_error_logged'):
                print(f"[INT] ERROR syncing create_mode: {e}")
                self._sync_error_logged = True

    def _sync_insert_mode_from_palette(self) -> None:
        """Synchronize insert_mode from palette checkbox."""
        if self.capture_mode:
            self.insert_mode = False
            return
        try:
            checkbox_value = self._safe_get_palette_property(PALETTE_PROP_INSERT_MODE)
            if checkbox_value is None:
                # Legacy PointInputElec palettes use AddCut for cut/insert behavior.
                checkbox_value = self._safe_get_palette_property("AddCut")
            if checkbox_value is not None:
                if hasattr(checkbox_value, "value"):
                    self.insert_mode = bool(checkbox_value.value)
                else:
                    self.insert_mode = bool(checkbox_value)
        except Exception:
            pass

    def _get_palette_limit_angles(self) -> bool:
        """Get limit angles setting from palette or config."""
        try:
            checkbox_value = self._safe_get_palette_property(PALETTE_PROP_LIMIT_ANGLES)
            if checkbox_value is not None:
                if hasattr(checkbox_value, "value"):
                    return bool(checkbox_value.value)
                else:
                    return bool(checkbox_value)
        except Exception:
            pass
        return bool(self.config.limit_angles)

    def _get_current_system(self) -> str:
        """Get current system from palette.
        
        Returns:
            System name string, or DEFAULT_SEGMENT_SYSTEM if not available
        """
        try:
            system_value = self._safe_get_palette_property(PALETTE_PROP_SYSTEM)
            if system_value is not None:
                # If it's a string, return it directly
                if isinstance(system_value, str):
                    return system_value
                # If it's numeric, convert to string (installations can override this behavior)
                elif isinstance(system_value, (int, float)):
                    return str(int(system_value))
        except Exception:
            pass
        return DEFAULT_SEGMENT_SYSTEM

    def _get_current_diameter(self) -> float:
        """Get current diameter from palette.
        
        Uses configurable system_diameter_mapping from config if available.
        
        Returns:
            Diameter in mm, or DEFAULT_SEGMENT_DIAMETER if not available
        """
        try:
            # Try custom diameter first
            custom_diameter = self._safe_get_palette_property(PALETTE_PROP_DIAMETER_CUSTOM)
            if custom_diameter is not None and custom_diameter > 0:
                return float(custom_diameter)

            # Try system-specific diameter using configurable mapping
            system_value = self._safe_get_palette_property(PALETTE_PROP_SYSTEM)
            if system_value is not None:
                config = getattr(self, 'config', None)
                if config and hasattr(config, 'system_diameter_mapping') and config.system_diameter_mapping:
                    # Try both numeric index and string name lookup
                    diameter_prop_name = config.system_diameter_mapping.get(system_value)
                    if diameter_prop_name is None and isinstance(system_value, (int, float)):
                        # Also try getting system name and looking it up by name
                        system_name = self._get_current_system()
                        if system_name:
                            diameter_prop_name = config.system_diameter_mapping.get(system_name)
                    
                    if diameter_prop_name:
                        system_diameter = self._safe_get_palette_property(diameter_prop_name)
                        if system_diameter is not None and system_diameter > 0:
                            return float(system_diameter)

            # Try general diameter
            diameter = self._safe_get_palette_property(PALETTE_PROP_DIAMETER)
            if diameter is not None and diameter > 0:
                return float(diameter)
        except Exception:
            pass
        return DEFAULT_SEGMENT_DIAMETER

    def _set_palette_message(self, message: str) -> None:
        """Set a message in the palette's text field."""
        self._safe_set_palette_property(PALETTE_PROP_FIRST_TEXT, message)

    # ===== Capture Workflow (delegates to PointInputCaptureHandler) =====
    def _capture_enabled(self) -> bool:
        """True if capture mode is enabled and handler exists."""
        return bool(self.capture_mode and self.capture_handler is not None)

    def _capture_handle_left_click(self, current_pnt: Any) -> bool:
        """Delegate to capture handler."""
        if self.capture_handler:
            return self.capture_handler.handle_point_click(current_pnt)
        return False

    def _capture_check_finish_now(self) -> None:
        """Delegate to capture handler."""
        if self.capture_handler:
            self.capture_handler.check_finish_now()

    def finalize_capture_on_shutdown(self, reason: str = "shutdown") -> None:
        """Called when capture session ends. Delegates to handler."""
        if self.capture_handler:
            self.capture_handler.on_shutdown(reason=reason)

    def _clone_point3d(self, point: Any) -> Any:
        if ALLPLAN_AVAILABLE and hasattr(point, "X"):
            return AllplanGeo.Point3D(point.X, point.Y, point.Z)
        if isinstance(point, (tuple, list)) and len(point) >= 3:
            return (float(point[0]), float(point[1]), float(point[2]))
        try:
            return (float(point.X), float(point.Y), float(point.Z))
        except Exception:
            return point

    def save_current_polyline(self):
        """Save the current active polyline to saved_paths, with automatic fusion if near extremes."""
        print(f"\n[LIBRARY] save_current_polyline() called with {len(self.points)} points")
        if len(self.points) < 2:
            print(f"[LIBRARY] Not enough points to save (need at least 2)")
            return

        # Save state before saving polyline
        self._save_state_snapshot()

        if ALLPLAN_AVAILABLE:
            new_path = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
        else:
            new_path = list(self.points)

        # Normalize angles on save when limiter is enabled
        if self._get_palette_limit_angles() and len(new_path) >= 2:
            new_path = self._snap_path_to_angles(new_path)

        # Check for automatic fusion with existing paths
        if len(new_path) >= 2:
            # Check if last point is near an extreme
            nearby_extreme = self._find_nearby_extreme(new_path[-1])
            if nearby_extreme:
                target_path_idx, target_end = nearby_extreme
                # Add new path temporarily
                temp_path_idx = len(self.script_object.saved_paths)
                self.script_object.saved_paths.append(new_path)
                # Merge
                self._merge_polylines(target_path_idx, target_end, temp_path_idx, 'end')
                # Store endpoints so handles are visible immediately
                self._store_endpoints_for_path(new_path)
                # Reset active polyline
                self.points.clear()
                self._clear_editing_state()
                return

            # Check if first point is near an extreme
            nearby_extreme = self._find_nearby_extreme(new_path[0])
            if nearby_extreme:
                target_path_idx, target_end = nearby_extreme
                # Add new path temporarily
                temp_path_idx = len(self.script_object.saved_paths)
                self.script_object.saved_paths.append(new_path)
                # Merge
                self._merge_polylines(target_path_idx, target_end, temp_path_idx, 'start')
                # Store endpoints so handles are visible immediately
                self._store_endpoints_for_path(new_path)
                # Reset active polyline
                self.points.clear()
                self._clear_editing_state()
                return

        # Normal save (no fusion)
        self.script_object.saved_paths.append(new_path)
        # Create default segments
        path_idx = len(self.script_object.saved_paths) - 1
        print(f"[LIBRARY] Saved as path #{path_idx}, creating segments...")
        self._create_default_segments_for_new_path(path_idx)
        # Store endpoints so handles appear immediately (before finalize)
        self._store_endpoints_for_path(new_path)
        
        # Clear active polyline after save to start fresh
        self.points.clear()
        self._clear_editing_state()
        print(f"[LIBRARY] Active polyline cleared, ready for next")
        print(f"[LIBRARY] Total saved_segments: {len(self.script_object.saved_segments)}")
        
        # Update status and section info
        seg_count = len(self.script_object.saved_segments)
        self._update_status(f"✓ Polyline saved ({seg_count} segments)")
        self._update_section_info()

        # Reset active polyline
        self.points.clear()
        self._clear_editing_state()
        print(f"[LIBRARY] save_current_polyline() complete\n")

    def _create_default_segments_for_new_path(self, path_idx: int):
        """Create default segments for a new path."""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        system = self._get_current_system()
        diameter = self._get_current_diameter()
        system_initial = system[0] if system else DEFAULT_SYSTEM_INITIAL
        
        for seg_idx in range(len(pts) - 1):
            metadata = SegmentMetadata(
                points=[pts[seg_idx], pts[seg_idx + 1]],
                diameter=diameter,
                section_type=f"{diameter}mm",
                system=system,
                label=f"{DEFAULT_SEGMENT_LABEL_PREFIX} {system_initial}",
                custom={"path_idx": path_idx, "seg_idx": seg_idx},  # Track which path/segment this belongs to
            )
            self.script_object.saved_segments.append(metadata)

    # ===== Segment Extension & Fusion =====
    def _dist_sq(self, a: Any, b: Any) -> float:
        """Calculate squared distance between two points."""
        if not ALLPLAN_AVAILABLE:
            return 0.0
        try:
            dx = a.X - b.X
            dy = a.Y - b.Y
            dz = a.Z - b.Z
            return dx*dx + dy*dy + dz*dz
        except Exception:
            return 0.0

    def _find_nearby_extreme(self, point: Any) -> Optional[Tuple[int, str]]:
        """Find a nearby extreme point (start or end) of a saved path.
        
        Args:
            point: Point to check
            
        Returns:
            Tuple of (path_idx, 'start'|'end') if found, None otherwise
        """
        if not ALLPLAN_AVAILABLE or not self.script_object.saved_paths:
            return None

        tolerance_sq = FUSION_TOLERANCE_MM * FUSION_TOLERANCE_MM
        min_dist_sq = tolerance_sq
        result = None

        for path_idx, path in enumerate(self.script_object.saved_paths):
            if len(path) < 2:
                continue

            # Check start point
            dist_start_sq = self._dist_sq(point, path[0])
            if dist_start_sq < min_dist_sq:
                min_dist_sq = dist_start_sq
                result = (path_idx, 'start')

            # Check end point
            dist_end_sq = self._dist_sq(point, path[-1])
            if dist_end_sq < min_dist_sq:
                min_dist_sq = dist_end_sq
                result = (path_idx, 'end')

        return result

    def _find_nearby_vertex(self, point: Any) -> Optional[Tuple[int, int]]:
        """Find a nearby vertex in saved paths.
        
        Args:
            point: Point to check
            
        Returns:
            Tuple of (path_idx, vertex_idx) if found, None otherwise
        """
        if not ALLPLAN_AVAILABLE or not self.script_object.saved_paths:
            return None

        tolerance_sq = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        min_dist_sq = tolerance_sq
        result = None

        for path_idx, path in enumerate(self.script_object.saved_paths):
            for vertex_idx, vertex in enumerate(path):
                dist_sq = self._dist_sq(point, vertex)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    result = (path_idx, vertex_idx)

        return result

    def _merge_polylines(self, target_path_idx: int, target_end: str, source_path_idx: int, source_end: str) -> None:
        """Merge two polylines by connecting them at their extremes.
        
        Args:
            target_path_idx: Index of target path to merge into
            source_path_idx: Index of source path to merge from
            target_end: 'start' or 'end' of target path
            source_end: 'start' or 'end' of source path
        """
        if not (0 <= target_path_idx < len(self.script_object.saved_paths)):
            return
        if not (0 <= source_path_idx < len(self.script_object.saved_paths)):
            return
        if target_path_idx == source_path_idx:
            return

        target_path = self.script_object.saved_paths[target_path_idx]
        source_path = self.script_object.saved_paths[source_path_idx]

        if len(target_path) < 2 or len(source_path) < 2:
            return

        # Determine merge direction
        if target_end == 'end' and source_end == 'start':
            # Append source to target end
            merged = list(target_path) + list(source_path[1:])  # Skip first point of source
        elif target_end == 'end' and source_end == 'end':
            # Append reversed source to target end
            merged = list(target_path) + list(reversed(source_path[:-1]))  # Skip last point of source
        elif target_end == 'start' and source_end == 'start':
            # Prepend reversed source to target start
            merged = list(reversed(source_path[1:])) + list(target_path)  # Skip first point of source
        elif target_end == 'start' and source_end == 'end':
            # Prepend source to target start
            merged = list(source_path[:-1]) + list(target_path)  # Skip last point of source
        else:
            return

        # Update target path
        self.script_object.saved_paths[target_path_idx] = merged

        # Remove source path
        self.script_object.saved_paths.pop(source_path_idx)

        # Rebuild segments for merged path
        self._rebuild_segments_for_path(target_path_idx)

        # Adjust segment indices for paths after removed source
        if source_path_idx < target_path_idx:
            # Source was before target, so target index shifted
            pass  # No adjustment needed since we're working with target_path_idx
        else:
            # Source was after target, segments for paths after source need adjustment
            # This is handled by rebuilding segments
            pass

    def _rebuild_segments_for_path(self, path_idx: int) -> None:
        """Rebuild segments for a path after geometry changes.
        
        CRITICAL: This removes ALL segments for the path and recreates them from current path positions.
        Uses path_idx tracking in segment metadata to identify which segments belong to which path.
        PRESERVES metadata (diameter, etc.) when geometry still matches.
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        # Save metadata for segments that will be removed (to preserve custom properties like diameter)
        path = self.script_object.saved_paths[path_idx]
        # Use TWO preservation strategies:
        # 1. By segment index (for dragging - preserves metadata when segment count is same)
        # 2. By geometry (for cases where segment count changes)
        metadata_by_index = {}  # Map from seg_idx to SegmentMetadata
        metadata_by_geometry = {}  # Map from (p0, p1) tuple to SegmentMetadata
        
        # Remove existing segments for this path, but save their metadata first
        segments_to_remove = []
        
        for seg_idx, seg_meta in enumerate(self.script_object.saved_segments):
            seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
            # SIMPLIFIED: Only match by path_idx (don't use geometry matching to prevent duplication)
            # After a path split, segments from the original path still have the old path_idx,
            # so we only remove segments that explicitly belong to this path_idx
            seg_path_idx = seg_meta_obj.custom.get("path_idx", None)
            seg_seg_idx = seg_meta_obj.custom.get("seg_idx", None)  # Segment index within path
            should_remove = False
            
            # Only remove segments that explicitly belong to this path_idx
            # Don't use geometry matching - it causes duplication after splits
            if seg_path_idx == path_idx:
                should_remove = True
            
            if should_remove:
                # Save metadata by segment index (for position-based matching)
                if seg_seg_idx is not None:
                    metadata_by_index[seg_seg_idx] = seg_meta_obj
                
                # Also save by geometry (for fallback matching)
                if len(seg_meta_obj.points) >= 2:
                    p0, p1 = seg_meta_obj.points[0], seg_meta_obj.points[1]
                    # Create a key from point coordinates (rounded to avoid floating point issues)
                    key = (
                        round(p0.X, 3), round(p0.Y, 3), round(p0.Z, 3),
                        round(p1.X, 3), round(p1.Y, 3), round(p1.Z, 3)
                    )
                    metadata_by_geometry[key] = seg_meta_obj
                segments_to_remove.append(seg_idx)

        # Remove segments in reverse order to maintain indices
        for seg_idx in reversed(segments_to_remove):
            self.script_object.saved_segments.pop(seg_idx)
            print(f"[INT] Removed segment {seg_idx} from path {path_idx}")

        # Create new segments from current path positions, preserving metadata where possible
        pts = self.script_object.saved_paths[path_idx]
        system = self._get_current_system()
        default_diameter = self._get_current_diameter()
        system_initial = system[0] if system else DEFAULT_SYSTEM_INITIAL
        
        for seg_idx in range(len(pts) - 1):
            p0, p1 = pts[seg_idx], pts[seg_idx + 1]
            
            # Try to preserve metadata: first by segment index (most reliable for dragging)
            preserved_meta = None
            if seg_idx in metadata_by_index:
                preserved_meta = metadata_by_index[seg_idx]
                print(f"[INT] Preserving metadata for segment {seg_idx} by index (diameter={preserved_meta.diameter}mm)")
            else:
                # Fallback: try geometry matching (for cases where segment count changed)
                key = (
                    round(p0.X, 3), round(p0.Y, 3), round(p0.Z, 3),
                    round(p1.X, 3), round(p1.Y, 3), round(p1.Z, 3)
                )
                if key in metadata_by_geometry:
                    preserved_meta = metadata_by_geometry[key]
                    print(f"[INT] Preserving metadata for segment {seg_idx} by geometry (diameter={preserved_meta.diameter}mm)")
            
            if preserved_meta:
                # Preserve existing metadata, just update points and path/segment indices
                metadata = SegmentMetadata(
                    points=[p0, p1],
                    diameter=preserved_meta.diameter,  # PRESERVE custom diameter
                    section_type=preserved_meta.section_type,  # PRESERVE section type
                    system=preserved_meta.system,  # PRESERVE system
                    label=preserved_meta.label,  # PRESERVE label
                    custom={"path_idx": path_idx, "seg_idx": seg_idx},  # Update indices
                )
            else:
                # New segment - use defaults
                metadata = SegmentMetadata(
                    points=[p0, p1],
                    diameter=default_diameter,
                    section_type=f"{default_diameter}mm",
                    system=system,
                    label=f"{DEFAULT_SEGMENT_LABEL_PREFIX} {system_initial}",
                    custom={"path_idx": path_idx, "seg_idx": seg_idx},
                )
            
            self.script_object.saved_segments.append(metadata)
        
        print(f"[INT] Rebuilt {len(pts) - 1} segments for path {path_idx}")

    def _point_in_path(self, point: Any, path_idx: int) -> bool:
        """Check if a point is in a path (within tolerance)."""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return False
        
        path = self.script_object.saved_paths[path_idx]
        tolerance_sq = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        
        for path_point in path:
            if self._dist_sq(point, path_point) < tolerance_sq:
                return True
        return False

    def _extend_path(self, path_idx: int, side: str, new_points: List[Any]) -> None:
        """Extend a path at start or end with new points.
        
        Args:
            path_idx: Index of path to extend
            side: 'start' or 'end'
            new_points: List of points to add
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        path = self.script_object.saved_paths[path_idx]
        if side == 'end':
            path.extend(new_points)
            # Create segments for new points
            # Last segment connects last two points, so max segment index = len(path) - 2
            start_seg = len(path) - len(new_points) - 1
            end_seg = len(path) - 2
            self._create_segments_for_range(path_idx, start_seg, end_seg)
        else:  # 'start'
            new_path = list(new_points) + list(path)
            self.script_object.saved_paths[path_idx] = new_path
            # Create segments for new points (segments connect new points and first old point)
            # If we prepend N points, we create segments [0..N-1], plus segment N-1 already connects to old path
            self._create_segments_for_range(path_idx, 0, len(new_points) - 1)

    def _create_segments_for_range(self, path_idx: int, start_seg: int, end_seg: int) -> None:
        """Create segments for a range of a path.
        
        Args:
            path_idx: Index of the path
            start_seg: First segment index (inclusive)
            end_seg: Last segment index (inclusive, unlike Python's range)
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        system = self._get_current_system()
        diameter = self._get_current_diameter()
        system_initial = system[0] if system else DEFAULT_SYSTEM_INITIAL

        # Make end_seg inclusive by adding 1, and cap at max valid segment index
        for seg_idx in range(start_seg, min(end_seg + 1, len(pts) - 1)):
            # Check if segment already exists
            existing = self._get_segment_metadata(path_idx, seg_idx)
            if existing is None:
                metadata = SegmentMetadata(
                    points=[pts[seg_idx], pts[seg_idx + 1]],
                    diameter=diameter,
                    section_type=f"{diameter}mm",
                    system=system,
                    label=f"{DEFAULT_SEGMENT_LABEL_PREFIX} {system_initial}",
                )
                self.script_object.saved_segments.append(metadata)

    def _get_segment_metadata(self, path_idx: int, seg_idx: int) -> Optional[SegmentMetadata]:
        """Get metadata for a specific segment."""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return None

        pts = self.script_object.saved_paths[path_idx]
        if seg_idx < 0 or seg_idx >= len(pts) - 1:
            return None

        p0, p1 = pts[seg_idx], pts[seg_idx + 1]

        for seg_meta in self.script_object.saved_segments:
            seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
            if len(seg_meta_obj.points) >= 2:
                seg_p0, seg_p1 = seg_meta_obj.points[0], seg_meta_obj.points[1]
                if self._dist_sq(seg_p0, p0) < 1e-6 and self._dist_sq(seg_p1, p1) < 1e-6:
                    return seg_meta_obj

        return None

    # ===== Public Segment Query API =====
    def get_segments(self) -> List[SegmentMetadata]:
        """Get all segments.
        
        Returns:
            List of all segment metadata objects
        """
        return [SegmentMetadata.from_legacy(seg) for seg in self.script_object.saved_segments]

    def get_segment_by_index(self, seg_idx: int) -> Optional[SegmentMetadata]:
        """Get segment by index in saved_segments list.
        
        Args:
            seg_idx: Index in saved_segments list
            
        Returns:
            SegmentMetadata object or None if index out of bounds
        """
        if 0 <= seg_idx < len(self.script_object.saved_segments):
            return SegmentMetadata.from_legacy(self.script_object.saved_segments[seg_idx])
        return None

    def get_segments_for_path(self, path_idx: int) -> List[SegmentMetadata]:
        """Get all segments belonging to a specific path.
        
        Args:
            path_idx: Index of path in saved_paths
            
        Returns:
            List of segment metadata objects for the specified path
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return []
        
        path_segments = []
        path = self.script_object.saved_paths[path_idx]
        
        # Find segments that match this path's geometry
        for seg_meta in self.script_object.saved_segments:
            seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
            if len(seg_meta_obj.points) >= 2:
                seg_p0 = seg_meta_obj.points[0]
                # Check if first point of segment matches any point in this path
                for i in range(len(path) - 1):
                    if self._dist_sq(seg_p0, path[i]) < 1e-6:
                        # Verify second point also matches
                        seg_p1 = seg_meta_obj.points[1]
                        if self._dist_sq(seg_p1, path[i + 1]) < 1e-6:
                            path_segments.append(seg_meta_obj)
                            break
        
        return path_segments

    def find_segment_at_point(self, point: Point3D, tolerance: float = HIT_TOL_SEGMENT) -> Optional[Tuple[int, SegmentMetadata]]:
        """Find segment near a point.
        
        Args:
            point: Point to search near (x, y, z) tuple or AllplanGeo.Point3D
            tolerance: Distance tolerance in mm
            
        Returns:
            Tuple of (segment_index, segment_metadata) or None if not found
        """
        # Convert point to tuple if needed
        if ALLPLAN_AVAILABLE and hasattr(point, 'X'):
            query_point = (point.X, point.Y, point.Z)
        else:
            query_point = point
        
        tol_sq = tolerance * tolerance
        
        for seg_idx, seg_meta in enumerate(self.script_object.saved_segments):
            seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
            if len(seg_meta_obj.points) >= 2:
                p0 = seg_meta_obj.points[0]
                p1 = seg_meta_obj.points[1]
                
                # Convert segment points to tuples if needed
                if ALLPLAN_AVAILABLE and hasattr(p0, 'X'):
                    p0 = (p0.X, p0.Y, p0.Z)
                if ALLPLAN_AVAILABLE and hasattr(p1, 'X'):
                    p1 = (p1.X, p1.Y, p1.Z)
                
                # Calculate distance from point to segment
                dist_sq = self._point_to_segment_dist_sq(query_point, p0, p1)
                
                if dist_sq <= tol_sq:
                    return (seg_idx, seg_meta_obj)
        
        return None

    def _point_to_segment_dist_sq(self, point: Tuple[float, float, float], 
                                   seg_p0: Tuple[float, float, float], 
                                   seg_p1: Tuple[float, float, float]) -> float:
        """Calculate squared distance from point to segment.
        
        Args:
            point: Query point (x, y, z)
            seg_p0: Segment start point (x, y, z)
            seg_p1: Segment end point (x, y, z)
            
        Returns:
            Squared distance in mm²
        """
        # Vector from seg_p0 to seg_p1
        dx = seg_p1[0] - seg_p0[0]
        dy = seg_p1[1] - seg_p0[1]
        dz = seg_p1[2] - seg_p0[2]
        
        # Segment length squared
        seg_len_sq = dx * dx + dy * dy + dz * dz
        
        if seg_len_sq < 1e-9:
            # Degenerate segment, return distance to point
            return self._dist_sq(point, seg_p0)
        
        # Vector from seg_p0 to point
        px = point[0] - seg_p0[0]
        py = point[1] - seg_p0[1]
        pz = point[2] - seg_p0[2]
        
        # Project point onto segment (parameter t in [0, 1])
        t = max(0.0, min(1.0, (px * dx + py * dy + pz * dz) / seg_len_sq))
        
        # Closest point on segment
        closest_x = seg_p0[0] + t * dx
        closest_y = seg_p0[1] + t * dy
        closest_z = seg_p0[2] + t * dz
        
        # Distance squared from point to closest point
        dist_x = point[0] - closest_x
        dist_y = point[1] - closest_y
        dist_z = point[2] - closest_z
        
        return dist_x * dist_x + dist_y * dist_y + dist_z * dist_z

    # ===== Segment Property Editing API =====
    def update_segment_properties(self, seg_idx: int, 
                                  diameter: Optional[float] = None,
                                  section_type: Optional[str] = None,
                                  system: Optional[str] = None,
                                  label: Optional[str] = None,
                                  layer: Optional[str] = None,
                                  color_id: Optional[int] = None,
                                  **custom_props) -> bool:
        """Update segment properties.
        
        Follows Allplan CommonProperties pattern for attribute updates.
        Automatically saves state snapshot for undo support.
        
        Args:
            seg_idx: Index in saved_segments list
            diameter: New diameter in mm (optional)
            section_type: New section type string (optional)
            system: New system type (optional)
            label: New label (optional)
            layer: New layer name (optional)
            color_id: New color ID (optional)
            **custom_props: Additional custom properties to update
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= seg_idx < len(self.script_object.saved_segments)):
            if self._debug:
                print(f"[INT] update_segment_properties: Invalid segment index {seg_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Get current segment
            seg_meta = SegmentMetadata.from_legacy(self.script_object.saved_segments[seg_idx])
            
            # Update properties (only if provided)
            if diameter is not None:
                seg_meta.diameter = float(diameter)
            if section_type is not None:
                seg_meta.section_type = str(section_type)
            if system is not None:
                seg_meta.system = str(system)
            if label is not None:
                seg_meta.label = str(label)
            if layer is not None:
                seg_meta.layer = str(layer)
            if color_id is not None:
                seg_meta.color_id = int(color_id)
            
            # Update custom properties
            if custom_props:
                seg_meta.custom.update(custom_props)
            
            # Save back to list
            self.script_object.saved_segments[seg_idx] = seg_meta
            
            if self._debug:
                print(f"[INT] Updated segment {seg_idx} properties")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error updating segment properties: {ex}")
            return False

    def update_segment_by_metadata(self, seg_idx: int, new_metadata: SegmentMetadata) -> bool:
        """Replace entire segment metadata.
        
        Args:
            seg_idx: Index in saved_segments list
            new_metadata: New SegmentMetadata object
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= seg_idx < len(self.script_object.saved_segments)):
            if self._debug:
                print(f"[INT] update_segment_by_metadata: Invalid segment index {seg_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Replace segment
            self.script_object.saved_segments[seg_idx] = new_metadata
            
            if self._debug:
                print(f"[INT] Replaced segment {seg_idx} metadata")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error replacing segment metadata: {ex}")
            return False

    # ===== Breakpoint/Role Management API =====
    def set_point_role(self, path_idx: int, point_idx: int, role: int) -> bool:
        """Set role for a specific point (INICIAL=1, PASO=2, BIFURCACION=3, FINAL=4).
        
        Updates segment metadata point_roles list. The role determines how the point
        is treated during capture and export operations.
        
        Args:
            path_idx: Index of path in saved_paths
            point_idx: Index of point in the path
            role: Role constant (CAPTURE_ROLE_INICIAL, CAPTURE_ROLE_PASO, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] set_point_role: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        if not (0 <= point_idx < len(path)):
            if self._debug:
                print(f"[INT] set_point_role: Invalid point index {point_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Find segments that contain this point
            updated = False
            for seg_meta in self.script_object.saved_segments:
                seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
                if len(seg_meta_obj.points) >= 2:
                    # Check if this segment's start point matches
                    if self._dist_sq(seg_meta_obj.points[0], path[point_idx]) < 1e-6:
                        # Update role at position 0
                        while len(seg_meta_obj.point_roles) < len(seg_meta_obj.points):
                            seg_meta_obj.point_roles.append(CAPTURE_ROLE_PASO)
                        seg_meta_obj.point_roles[0] = role
                        # Save back
                        seg_idx = self.script_object.saved_segments.index(seg_meta)
                        self.script_object.saved_segments[seg_idx] = seg_meta_obj
                        updated = True
                    # Check if this segment's end point matches
                    elif self._dist_sq(seg_meta_obj.points[-1], path[point_idx]) < 1e-6:
                        # Update role at last position
                        while len(seg_meta_obj.point_roles) < len(seg_meta_obj.points):
                            seg_meta_obj.point_roles.append(CAPTURE_ROLE_PASO)
                        seg_meta_obj.point_roles[-1] = role
                        # Save back
                        seg_idx = self.script_object.saved_segments.index(seg_meta)
                        self.script_object.saved_segments[seg_idx] = seg_meta_obj
                        updated = True
            
            if self._debug:
                if updated:
                    print(f"[INT] Set role {role} for point {point_idx} in path {path_idx}")
                else:
                    print(f"[INT] No segments found for point {point_idx} in path {path_idx}")
            
            return updated
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error setting point role: {ex}")
            return False

    def get_point_role(self, path_idx: int, point_idx: int) -> Optional[int]:
        """Get role for a specific point.
        
        Args:
            path_idx: Index of path in saved_paths
            point_idx: Index of point in the path
            
        Returns:
            Role constant (int) or None if not found
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return None
        
        path = self.script_object.saved_paths[path_idx]
        if not (0 <= point_idx < len(path)):
            return None
        
        # Find segments that contain this point
        for seg_meta in self.script_object.saved_segments:
            seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
            if len(seg_meta_obj.points) >= 2 and seg_meta_obj.point_roles:
                # Check if this segment's start point matches
                if self._dist_sq(seg_meta_obj.points[0], path[point_idx]) < 1e-6:
                    if len(seg_meta_obj.point_roles) > 0:
                        return seg_meta_obj.point_roles[0]
                # Check if this segment's end point matches
                elif self._dist_sq(seg_meta_obj.points[-1], path[point_idx]) < 1e-6:
                    if len(seg_meta_obj.point_roles) > len(seg_meta_obj.points) - 1:
                        return seg_meta_obj.point_roles[-1]
        
        return None

    def mark_as_breakpoint(self, path_idx: int, point_idx: int, role: int = CAPTURE_ROLE_PASO) -> bool:
        """Mark a point as a breakpoint with specific role.
        
        This is a convenience method that sets the point role to indicate it's a breakpoint
        in the installation routing.
        
        Args:
            path_idx: Index of path in saved_paths
            point_idx: Index of point in the path
            role: Role to assign (default: CAPTURE_ROLE_PASO for intermediate breakpoint)
            
        Returns:
            True if successful, False otherwise
        """
        return self.set_point_role(path_idx, point_idx, role)

    # ===== Geometry Editing API =====
    def move_point(self, path_idx: int, point_idx: int, new_point: Point3D) -> bool:
        """Move a point in a path. Updates affected segments automatically.
        
        Uses Allplan Point3D for geometry. Rebuilds affected segments using 
        existing _rebuild_segments_for_path().
        
        Args:
            path_idx: Index of path in saved_paths
            point_idx: Index of point to move
            new_point: New position (x, y, z) tuple or AllplanGeo.Point3D
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] move_point: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        if not (0 <= point_idx < len(path)):
            if self._debug:
                print(f"[INT] move_point: Invalid point index {point_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Convert new_point to appropriate format
            if ALLPLAN_AVAILABLE:
                if hasattr(new_point, 'X'):
                    new_pt = AllplanGeo.Point3D(new_point.X, new_point.Y, new_point.Z)
                elif isinstance(new_point, (tuple, list)) and len(new_point) >= 3:
                    new_pt = AllplanGeo.Point3D(float(new_point[0]), float(new_point[1]), float(new_point[2]))
                else:
                    if self._debug:
                        print(f"[INT] move_point: Invalid point format")
                    return False
            else:
                if isinstance(new_point, (tuple, list)) and len(new_point) >= 3:
                    new_pt = (float(new_point[0]), float(new_point[1]), float(new_point[2]))
                else:
                    new_pt = new_point
            
            # Update point in path
            self.script_object.saved_paths[path_idx][point_idx] = new_pt
            
            # Rebuild segments for this path
            self._rebuild_segments_for_path(path_idx)
            
            if self._debug:
                print(f"[INT] Moved point {point_idx} in path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error moving point: {ex}")
            return False

    def insert_point_at_position(self, path_idx: int, insert_after_idx: int, new_point: Point3D) -> bool:
        """Insert point in path. Creates/updates segments.
        
        Follows existing insert point logic patterns from the library.
        
        Args:
            path_idx: Index of path in saved_paths
            insert_after_idx: Insert after this index (-1 to insert at start)
            new_point: Point to insert (x, y, z) tuple or AllplanGeo.Point3D
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] insert_point_at_position: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        if not (-1 <= insert_after_idx < len(path)):
            if self._debug:
                print(f"[INT] insert_point_at_position: Invalid insert position {insert_after_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Convert new_point to appropriate format
            if ALLPLAN_AVAILABLE:
                if hasattr(new_point, 'X'):
                    new_pt = AllplanGeo.Point3D(new_point.X, new_point.Y, new_point.Z)
                elif isinstance(new_point, (tuple, list)) and len(new_point) >= 3:
                    new_pt = AllplanGeo.Point3D(float(new_point[0]), float(new_point[1]), float(new_point[2]))
                else:
                    if self._debug:
                        print(f"[INT] insert_point_at_position: Invalid point format")
                    return False
            else:
                if isinstance(new_point, (tuple, list)) and len(new_point) >= 3:
                    new_pt = (float(new_point[0]), float(new_point[1]), float(new_point[2]))
                else:
                    new_pt = new_point
            
            # Insert point into path
            insert_idx = insert_after_idx + 1
            self.script_object.saved_paths[path_idx].insert(insert_idx, new_pt)
            
            # Rebuild segments for this path
            self._rebuild_segments_for_path(path_idx)
            
            if self._debug:
                print(f"[INT] Inserted point at position {insert_idx} in path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error inserting point: {ex}")
            return False

    def remove_point(self, path_idx: int, point_idx: int, min_points: int = 2) -> bool:
        """Remove point from path. Merges adjacent segments if needed.
        
        Args:
            path_idx: Index of path in saved_paths
            point_idx: Index of point to remove
            min_points: Minimum points to keep in path (default: 2)
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] remove_point: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        if not (0 <= point_idx < len(path)):
            if self._debug:
                print(f"[INT] remove_point: Invalid point index {point_idx}")
            return False
        
        if len(path) <= min_points:
            if self._debug:
                print(f"[INT] remove_point: Cannot remove point, path has minimum points")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Remove point from path
            self.script_object.saved_paths[path_idx].pop(point_idx)
            
            # Rebuild segments for this path
            self._rebuild_segments_for_path(path_idx)
            
            if self._debug:
                print(f"[INT] Removed point {point_idx} from path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error removing point: {ex}")
            return False

    def split_segment(self, path_idx: int, seg_idx: int, split_point: Point3D) -> bool:
        """Split segment at point. Creates two segments with same properties.
        
        Inserts point into saved_paths, creates new segment metadata.
        
        Args:
            path_idx: Index of path in saved_paths
            seg_idx: Index of segment in the path (0 to len(path)-2)
            split_point: Point to split at (x, y, z) tuple or AllplanGeo.Point3D
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] split_segment: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        if not (0 <= seg_idx < len(path) - 1):
            if self._debug:
                print(f"[INT] split_segment: Invalid segment index {seg_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Convert split_point to appropriate format
            if ALLPLAN_AVAILABLE:
                if hasattr(split_point, 'X'):
                    split_pt = AllplanGeo.Point3D(split_point.X, split_point.Y, split_point.Z)
                elif isinstance(split_point, (tuple, list)) and len(split_point) >= 3:
                    split_pt = AllplanGeo.Point3D(float(split_point[0]), float(split_point[1]), float(split_point[2]))
                else:
                    if self._debug:
                        print(f"[INT] split_segment: Invalid point format")
                    return False
            else:
                if isinstance(split_point, (tuple, list)) and len(split_point) >= 3:
                    split_pt = (float(split_point[0]), float(split_point[1]), float(split_point[2]))
                else:
                    split_pt = split_point
            
            # Validate split point is on the segment (within tolerance)
            p0 = path[seg_idx]
            p1 = path[seg_idx + 1]
            
            if ALLPLAN_AVAILABLE and hasattr(p0, 'X'):
                p0_tuple = (p0.X, p0.Y, p0.Z)
                p1_tuple = (p1.X, p1.Y, p1.Z)
            else:
                p0_tuple = p0
                p1_tuple = p1
            
            if ALLPLAN_AVAILABLE and hasattr(split_pt, 'X'):
                split_tuple = (split_pt.X, split_pt.Y, split_pt.Z)
            else:
                split_tuple = split_pt
            
            # Check if split point is reasonably close to the segment
            dist_sq = self._point_to_segment_dist_sq(split_tuple, p0_tuple, p1_tuple)
            if dist_sq > (MIN_SEG_LEN_MM * MIN_SEG_LEN_MM):
                if self._debug:
                    print(f"[INT] split_segment: Split point too far from segment")
                return False
            
            # Check split point is not too close to endpoints
            if self._dist_sq(split_tuple, p0_tuple) < (MIN_SEG_LEN_MM * MIN_SEG_LEN_MM):
                if self._debug:
                    print(f"[INT] split_segment: Split point too close to segment start")
                return False
            if self._dist_sq(split_tuple, p1_tuple) < (MIN_SEG_LEN_MM * MIN_SEG_LEN_MM):
                if self._debug:
                    print(f"[INT] split_segment: Split point too close to segment end")
                return False
            
            # Insert split point into path
            self.script_object.saved_paths[path_idx].insert(seg_idx + 1, split_pt)
            
            # Rebuild segments for this path (will create two segments from the original)
            self._rebuild_segments_for_path(path_idx)
            
            if self._debug:
                print(f"[INT] Split segment {seg_idx} in path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error splitting segment: {ex}")
            return False

    def merge_segments(self, path_idx: int, seg1_idx: int, seg2_idx: int) -> bool:
        """Merge two adjacent segments. Keeps properties from first segment.
        
        The segments must be adjacent (seg2_idx = seg1_idx + 1). The shared point
        between them is removed, creating one continuous segment.
        
        Args:
            path_idx: Index of path in saved_paths
            seg1_idx: Index of first segment
            seg2_idx: Index of second segment (must be seg1_idx + 1)
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] merge_segments: Invalid path index {path_idx}")
            return False
        
        path = self.script_object.saved_paths[path_idx]
        
        # Validate segment indices
        if not (0 <= seg1_idx < len(path) - 1):
            if self._debug:
                print(f"[INT] merge_segments: Invalid first segment index {seg1_idx}")
            return False
        
        if not (0 <= seg2_idx < len(path) - 1):
            if self._debug:
                print(f"[INT] merge_segments: Invalid second segment index {seg2_idx}")
            return False
        
        # Check segments are adjacent
        if seg2_idx != seg1_idx + 1:
            if self._debug:
                print(f"[INT] merge_segments: Segments must be adjacent (seg2 = seg1 + 1)")
            return False
        
        # Need at least 3 points to merge (can't reduce below 2 points)
        if len(path) <= 2:
            if self._debug:
                print(f"[INT] merge_segments: Path too short to merge segments")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Remove the shared point (which is at seg2_idx = seg1_idx + 1)
            shared_point_idx = seg1_idx + 1
            self.script_object.saved_paths[path_idx].pop(shared_point_idx)
            
            # Rebuild segments for this path
            self._rebuild_segments_for_path(path_idx)
            
            if self._debug:
                print(f"[INT] Merged segments {seg1_idx} and {seg2_idx} in path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error merging segments: {ex}")
            return False

    def _project_point_on_segment(self, path_idx: int, seg_idx: int, point: Any) -> Optional[Any]:
        """Project a point onto a path segment in relative coordinates."""
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return None
            path = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(path) - 1):
                return None
            p0 = path[seg_idx]
            p1 = path[seg_idx + 1]

            vx = p1.X - p0.X
            vy = p1.Y - p0.Y
            vz = p1.Z - p0.Z
            seg_len_sq = vx * vx + vy * vy + vz * vz
            if seg_len_sq < 1e-9:
                return None

            wx = point.X - p0.X
            wy = point.Y - p0.Y
            wz = point.Z - p0.Z
            t = (wx * vx + wy * vy + wz * vz) / seg_len_sq
            t = max(0.0, min(1.0, t))
            return AllplanGeo.Point3D(p0.X + t * vx, p0.Y + t * vy, p0.Z + t * vz) if ALLPLAN_AVAILABLE else None
        except Exception:
            return None

    def _find_saved_segment_index(self, path_idx: int, seg_idx: int) -> Optional[int]:
        """Resolve (path_idx, seg_idx) to index in saved_segments."""
        try:
            for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(saved_seg)
                if seg_meta.custom.get("path_idx") == path_idx and seg_meta.custom.get("seg_idx") == seg_idx:
                    return saved_idx
        except Exception:
            pass
        return None

    def split_hovered_or_selected_segment(self, click_point: Any) -> bool:
        """Insert a cut point in selected/hovered segment (AddCut / insert mode)."""
        target = self.selected_seg or self.hover_seg
        if target is None:
            self._update_status("AddCut: selecciona o apunta un segmento")
            return False
        path_idx, seg_idx = target
        split_pt = self._project_point_on_segment(path_idx, seg_idx, click_point)
        if split_pt is None:
            self._update_status("AddCut: no se pudo calcular punto de corte")
            return False
        if not self.split_segment(path_idx, seg_idx, split_pt):
            self._update_status("AddCut: corte invalido (muy cerca de extremos)")
            return False
        self.selected_seg = (path_idx, seg_idx + 1)
        self.hover_seg = self.selected_seg
        self.hover_mid = None
        self._update_status(f"Corte agregado: Path {path_idx}, Segment {seg_idx}")
        return True

    def delete_selected_or_hovered_segment(self) -> bool:
        """Delete selected segment; fallback to hovered/current capture segment."""
        # Priority: delete selected/hovered free-point entity first.
        free_entities = self._get_saved_free_entities()
        target_entity = self.selected_free_entity if self.selected_free_entity is not None else self.hover_free_entity
        if target_entity is not None and 0 <= target_entity < len(free_entities):
            try:
                self._save_state_snapshot()
                free_entities.pop(target_entity)
                self.selected_free_entity = None
                self.hover_free_entity = None
                self.drag_free_entity_idx = None
                self._update_status("Free-point entity deleted")
                self._draw_preview(self.current_point)
                return True
            except Exception:
                self._update_status("Delete: could not delete free-point entity")
                return False

        # Capture mode fallback: remove the last unfinished segment interactively.
        if self.capture_mode and self.capture_handler and len(self.points) >= 2:
            try:
                self._save_state_snapshot()
                self.points.pop()
                active_pid = self.capture_handler._active_path_id
                for idx in range(len(self.capture_handler.records) - 1, -1, -1):
                    rec = self.capture_handler.records[idx]
                    if rec.exported:
                        continue
                    if active_pid is not None and rec.path_id != active_pid:
                        continue
                    self.capture_handler.records.pop(idx)
                    break
                self._update_status("Ultimo segmento eliminado")
                self._draw_preview(self.current_point)
                return True
            except Exception:
                self._update_status("Delete: error al eliminar ultimo segmento")
                return False

        target = self.selected_seg or self.hover_seg
        if target is None:
            self._update_status("Delete: selecciona o apunta un segmento")
            return False
        path_idx, seg_idx = target
        saved_idx = self._find_saved_segment_index(path_idx, seg_idx)
        if saved_idx is None:
            self._update_status("Delete: segmento no encontrado")
            return False
        ok = self.delete_segment(saved_idx, delete_geometry=True)
        if ok:
            self._update_status(f"Segmento eliminado: Path {path_idx}, Segment {seg_idx}")
        else:
            self._update_status("Delete: no se pudo eliminar el segmento")
        return ok

    # ===== Segment Deletion and Batch Operations API =====
    def delete_segment(self, seg_idx: int, delete_geometry: bool = True) -> bool:
        """Delete segment and its geometry from the path.
        
        If the segment is in the middle of a path, the path will be split into two separate paths.
        If it's at the start or end, that point is removed.
        
        Args:
            seg_idx: Index in saved_segments list
            delete_geometry: If True, remove geometry from saved_paths (default True)
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= seg_idx < len(self.script_object.saved_segments)):
            print(f"[INT] delete_segment: Invalid segment index {seg_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            # Get segment metadata to find its path and local segment index
            seg_meta = SegmentMetadata.from_legacy(self.script_object.saved_segments[seg_idx])
            path_idx = seg_meta.custom.get("path_idx", None)
            seg_idx_in_path = seg_meta.custom.get("seg_idx", None)
            
            if path_idx is None or not (0 <= path_idx < len(self.script_object.saved_paths)):
                print(f"[INT] delete_segment: Could not find path for segment {seg_idx} (path_idx={path_idx})")
                return False
            
            path = self.script_object.saved_paths[path_idx]
            
            if seg_idx_in_path is None:
                # Fallback: Try to find segment by matching points (for backward compatibility)
                if len(seg_meta.points) < 2:
                    print(f"[INT] delete_segment: Segment {seg_idx} has invalid points and no seg_idx")
                    return False
                
                seg_p0 = seg_meta.points[0]
                seg_p1 = seg_meta.points[1]
                tolerance_sq = 1.0  # 1mm tolerance
                seg_idx_in_path = None
                for i in range(len(path) - 1):
                    if self._dist_sq(seg_p0, path[i]) < tolerance_sq and self._dist_sq(seg_p1, path[i + 1]) < tolerance_sq:
                        seg_idx_in_path = i
                        break
                
                if seg_idx_in_path is None:
                    print(f"[INT] delete_segment: Could not find segment {seg_idx} in path {path_idx} by point matching")
                    return False
            else:
                # Use the seg_idx from metadata (more reliable)
                if not (0 <= seg_idx_in_path < len(path) - 1):
                    print(f"[INT] delete_segment: Invalid seg_idx_in_path {seg_idx_in_path} for path with {len(path)} points")
                    return False
            
            print(f"[INT] Deleting segment {seg_idx} (path {path_idx}, segment {seg_idx_in_path} in path)")
            
            if delete_geometry:
                # Step 1: Split path geometry
                if len(path) < 2 or not (0 <= seg_idx_in_path < len(path) - 1):
                    print(f"[INT] delete_segment: Invalid path or segment index")
                    return False
                
                # Split path: left = points up to and including start of segment, right = points from end of segment onwards
                # Include the end point of deleted segment in right path so remaining segments can be rendered
                left = path[:seg_idx_in_path + 1]  # Up to and including start point of deleted segment
                right = path[seg_idx_in_path + 1:]  # From start point onwards (includes end point of deleted segment)
                
                new_paths: List[List[Any]] = []
                if len(left) >= 2:
                    new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left])
                if len(right) >= 2:
                    new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])
                
                # Step 2: Remove only the deleted segment
                self.script_object.saved_segments.pop(seg_idx)
                print(f"[INT] Removed segment {seg_idx} from saved_segments")
                
                # Step 3: Update segments that moved to the new path (for correct path_idx/seg_idx)
                # This is needed for selection lookup and absolute numbering
                # But we only update the custom dict, not any palette properties
                segments_to_update = []
                for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                    saved_meta = SegmentMetadata.from_legacy(saved_seg)
                    saved_path_idx = saved_meta.custom.get("path_idx", None)
                    saved_seg_idx_in_path = saved_meta.custom.get("seg_idx", None)
                    
                    if saved_path_idx == path_idx and saved_seg_idx_in_path is not None:
                        if saved_seg_idx_in_path > seg_idx_in_path and len(new_paths) > 1:
                            # Segment moved to right path - update path_idx and seg_idx
                            new_path_idx = path_idx + 1
                            new_seg_idx = saved_seg_idx_in_path - seg_idx_in_path - 1
                            if 0 <= new_seg_idx < len(new_paths[1]) - 1:
                                saved_meta.custom["path_idx"] = new_path_idx
                                saved_meta.custom["seg_idx"] = new_seg_idx
                                segments_to_update.append((saved_idx, saved_meta))
                
                # Apply updates (only custom dict, no palette interaction)
                for saved_idx, updated_meta in segments_to_update:
                    self.script_object.saved_segments[saved_idx] = updated_meta
                
                # Step 4: Update path_idx for segments from OTHER paths (after the split)
                if len(new_paths) == 2:
                    for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                        saved_meta = SegmentMetadata.from_legacy(saved_seg)
                        saved_path_idx = saved_meta.custom.get("path_idx", None)
                        # Update segments from paths originally after the deleted path
                        if saved_path_idx is not None and saved_path_idx > path_idx + 1:
                            saved_meta.custom["path_idx"] = saved_path_idx + 1
                            self.script_object.saved_segments[saved_idx] = saved_meta
                
                # Step 5: Replace original path with new paths
                self.script_object.saved_paths.pop(path_idx)
                for offset, new_path in enumerate(new_paths):
                    new_path_idx = path_idx + offset
                    self.script_object.saved_paths.insert(new_path_idx, new_path)
                
                if len(new_paths) == 2:
                    print(f"[INT] Deleted segment {seg_idx} from middle of path {path_idx}, split into 2 paths")
                elif len(new_paths) == 1:
                    print(f"[INT] Deleted segment {seg_idx} from path {path_idx} (end segment)")
                else:
                    print(f"[INT] Deleted segment {seg_idx} - path {path_idx} removed (was too short)")
            else:
                # Just removed segment metadata (already done above)
                print(f"[INT] Deleted segment {seg_idx} metadata only")
            
            # Clear selection after deletion
            self.selected_seg = None
            self.hover_seg = None
            self.hover_mid = None
            
            return True
            
        except Exception as ex:
            print(f"[INT] Error deleting segment: {ex}")
            import traceback
            traceback.print_exc()
            return False

    def delete_segments_for_path(self, path_idx: int) -> bool:
        """Delete all segments for a path.
        
        Args:
            path_idx: Index of path in saved_paths
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            if self._debug:
                print(f"[INT] delete_segments_for_path: Invalid path index {path_idx}")
            return False
        
        try:
            # Save state for undo
            self._save_state_snapshot()
            
            path = self.script_object.saved_paths[path_idx]
            
            # Find and remove all segments that belong to this path
            segments_to_remove = []
            for seg_idx, seg_meta in enumerate(self.script_object.saved_segments):
                seg_meta_obj = SegmentMetadata.from_legacy(seg_meta)
                if len(seg_meta_obj.points) >= 2:
                    seg_p0 = seg_meta_obj.points[0]
                    # Check if first point of segment matches any point in this path
                    for i in range(len(path) - 1):
                        if self._dist_sq(seg_p0, path[i]) < 1e-6:
                            # Verify second point also matches
                            seg_p1 = seg_meta_obj.points[1]
                            if self._dist_sq(seg_p1, path[i + 1]) < 1e-6:
                                segments_to_remove.append(seg_idx)
                                break
            
            # Remove segments in reverse order to maintain indices
            for seg_idx in reversed(segments_to_remove):
                self.script_object.saved_segments.pop(seg_idx)
            
            if self._debug:
                print(f"[INT] Deleted {len(segments_to_remove)} segments for path {path_idx}")
            
            return True
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error deleting segments for path: {ex}")
            return False

    def batch_update_segments(self, updates: List[Tuple[int, Dict[str, Any]]]) -> int:
        """Update multiple segments in one operation.
        
        Args:
            updates: List of (seg_idx, properties_dict) tuples
                    properties_dict can contain: diameter, section_type, system, label, etc.
        
        Returns:
            Number of segments successfully updated
        """
        if not updates:
            return 0
        
        try:
            # Save state for undo (once for entire batch)
            self._save_state_snapshot()
            
            updated_count = 0
            for seg_idx, props in updates:
                if 0 <= seg_idx < len(self.script_object.saved_segments):
                    try:
                        # Get current segment
                        seg_meta = SegmentMetadata.from_legacy(self.script_object.saved_segments[seg_idx])
                        
                        # Update properties
                        if 'diameter' in props:
                            seg_meta.diameter = float(props['diameter'])
                        if 'section_type' in props:
                            seg_meta.section_type = str(props['section_type'])
                        if 'system' in props:
                            seg_meta.system = str(props['system'])
                        if 'label' in props:
                            seg_meta.label = str(props['label'])
                        if 'layer' in props:
                            seg_meta.layer = str(props['layer'])
                        if 'color_id' in props:
                            seg_meta.color_id = int(props['color_id'])
                        
                        # Update any additional custom properties
                        custom_keys = set(props.keys()) - {'diameter', 'section_type', 'system', 'label', 'layer', 'color_id'}
                        for key in custom_keys:
                            seg_meta.custom[key] = props[key]
                        
                        # Save back to list
                        self.script_object.saved_segments[seg_idx] = seg_meta
                        updated_count += 1
                        
                    except Exception as ex:
                        if self._debug:
                            print(f"[INT] Error updating segment {seg_idx} in batch: {ex}")
                        continue
            
            if self._debug:
                print(f"[INT] Batch updated {updated_count} of {len(updates)} segments")
            
            return updated_count
            
        except Exception as ex:
            if self._debug:
                print(f"[INT] Error in batch update: {ex}")
            return 0

    def _clear_editing_state(self):
        """Clear all editing state."""
        self.is_dragging = False
        self.drag_index = -1
        self.hover_index = -1
        self.hover_seg = None
        self.selected_seg = None
        self.hover_free_entity = None
        self.selected_free_entity = None
        self.insert_preview_p = None
        self.insert_target = None
        self.hover_mid = None
        self.drag_free_entity_idx = None

    def _clear_preview(self):
        """Clear all preview elements completely using Allplan's DrawElementPreview."""
        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            return
        
        try:
            # Create empty elements list to clear the preview
            empty_elems: List[Any] = []

            # Use DrawElementPreview with empty list to clear previous previews
            # CRITICAL: Use True to actually clear previous elements (from Saneamiento)
            AllplanBaseElements.DrawElementPreview(
                self.coord_input.GetInputViewDocument(),
                AllplanGeo.Matrix3D(),
                empty_elems,
                True,  # Clear previous elements - THIS MUST BE TRUE!
                None
            )
        except Exception as e:
            if not self._debug_logged_clear_methods:
                print(f"[INT] Error in _clear_preview: {e}")
                self._debug_logged_clear_methods = True

    def _cleanup_resources(self):
        """Clean up all resources."""
        self._clear_preview()
        self.points.clear()
        self._clear_editing_state()

    # ===== State Persistence (Edit/Re-entry) =====
    def _detect_modification_mode(self) -> None:
        self.is_modification_mode = False
        try:
            mod_list = getattr(self.script_object, "modification_ele_list", None)
            if mod_list is not None and hasattr(mod_list, "is_modification_element"):
                self.is_modification_mode = bool(mod_list.is_modification_element())
        except Exception:
            self.is_modification_mode = False

    def _serialize_state_to_json(self) -> str:
        try:
            origin_x, origin_y, origin_z = self._get_origin_offset()
            paths_payload = []
            for path in self.script_object.saved_paths:
                paths_payload.append([_extract_point_components(p) for p in path])

            segments_payload = []
            for seg in self.script_object.saved_segments:
                seg_meta = SegmentMetadata.from_legacy(seg)
                seg_dict = seg_meta.to_dict()
                seg_dict["points"] = [_extract_point_components(p) for p in seg_meta.points]
                segments_payload.append(seg_dict)

            free_entities_payload = []
            for entity in self._get_saved_free_entities():
                if not isinstance(entity, dict):
                    continue
                pt = entity.get("point", None)
                if pt is None:
                    continue
                x, y, z = _extract_point_components(pt)
                free_entities_payload.append({
                    "tool": str(entity.get("tool", "") or ""),
                    "point": [x, y, z],
                        "state": entity.get("state", {}) if isinstance(entity.get("state", {}), dict) else {},
                })

            payload = {
                "version": 1,
                "origin": {"x": origin_x, "y": origin_y, "z": origin_z},
                "paths": paths_payload,
                "segments": segments_payload,
                "free_entities": free_entities_payload,
            }
            return json.dumps(payload, ensure_ascii=True)
        except Exception as ex:
            print(f"[INT] Error serializing state: {ex}")
            return ""

    # ===== JSON Export =====

    def build_camino_model(
        self,
        camino_id: Optional[str] = None,
        tipo_instalacion: str = "",
    ) -> CaminoModel:
        """Build a :class:`CaminoModel` from the current library state.

        Args:
            camino_id: Unique identifier.  Auto-generated when *None*.
            tipo_instalacion: Installation type string (e.g. "Electricidad").

        Returns:
            A fully populated :class:`CaminoModel` ready for
            :func:`generate_json`.
        """

        if camino_id is None:
            import uuid as _uuid
            camino_id = f"camino-{_uuid.uuid4().hex[:8]}"

        # -- 1. Build PuntoModel list with role classification --------------
        puntos: List[PuntoModel] = []
        global_order = 0

        seg_by_path: Dict[int, List[SegmentMetadata]] = {}
        for seg in self.script_object.saved_segments:
            seg_meta = SegmentMetadata.from_legacy(seg) if not isinstance(seg, SegmentMetadata) else seg
            pidx = seg_meta.custom.get("path_idx") if seg_meta.custom else None
            if pidx is None:
                pidx = seg_meta.path_id
            if pidx is not None:
                seg_by_path.setdefault(pidx, []).append(seg_meta)

        endpoint_counts: Dict[Tuple[float, float, float], int] = {}
        for path in self.script_object.saved_paths:
            if len(path) >= 2:
                for pt in (path[0], path[-1]):
                    key = tuple(round(c, 1) for c in _extract_point_components(pt))
                    endpoint_counts[key] = endpoint_counts.get(key, 0) + 1

        for path_idx, path in enumerate(self.script_object.saved_paths):
            segs = seg_by_path.get(path_idx, [])

            for pt_idx, pt in enumerate(path):
                x, y, z = _extract_point_components(pt)

                role_str = "Paso"
                role_found = False

                if segs:
                    if pt_idx == 0 and len(segs) > 0 and len(segs[0].point_roles) >= 1:
                        role_str = CAPTURE_ROLE_LABELS.get(segs[0].point_roles[0], "Paso")
                        role_found = True
                    elif pt_idx > 0:
                        seg_i = min(pt_idx - 1, len(segs) - 1)
                        if seg_i >= 0 and len(segs[seg_i].point_roles) >= 2:
                            role_str = CAPTURE_ROLE_LABELS.get(segs[seg_i].point_roles[1], "Paso")
                            role_found = True

                if not role_found:
                    pt_key = tuple(round(c, 1) for c in (x, y, z))
                    is_shared = endpoint_counts.get(pt_key, 0) > 1
                    if is_shared:
                        role_str = "Bifurcacion"
                    elif pt_idx == 0 and path_idx == 0:
                        role_str = "Inicial"
                    elif pt_idx == len(path) - 1:
                        role_str = "Final"

                seg_ref = segs[min(pt_idx, len(segs) - 1)] if segs else None
                diameter = seg_ref.diameter if seg_ref else DEFAULT_SEGMENT_DIAMETER
                section_type = seg_ref.section_type if seg_ref else DEFAULT_SEGMENT_SECTION_TYPE
                system = seg_ref.system if seg_ref else DEFAULT_SEGMENT_SYSTEM
                color_id = seg_ref.color_id if seg_ref and seg_ref.color_id is not None else 1
                segment_id = seg_ref.segment_id if seg_ref and seg_ref.segment_id is not None else 0

                puntos.append(PuntoModel(
                    id=f"P-{global_order}",
                    x=x, y=y, z=z,
                    orden=global_order,
                    tipo=role_str,
                    path_id=path_idx,
                    segment_id=segment_id,
                    color_id=color_id,
                    diameter=diameter,
                    section_type=section_type,
                    system=system,
                ))
                global_order += 1

        # -- 2. Compute anteriores/siguientes graph links -------------------
        for path_idx, path in enumerate(self.script_object.saved_paths):
            path_puntos = [p for p in puntos if p.path_id == path_idx]
            path_puntos.sort(key=lambda p: p.orden)
            for i, punto in enumerate(path_puntos):
                if i > 0:
                    prev_id = path_puntos[i - 1].id
                    if prev_id not in punto.anteriores:
                        punto.anteriores.append(prev_id)
                if i < len(path_puntos) - 1:
                    next_id = path_puntos[i + 1].id
                    if next_id not in punto.siguientes:
                        punto.siguientes.append(next_id)

        # -- 3. Free entities -----------------------------------------------
        free_entities_payload: List[Dict[str, Any]] = []
        for entity in self._get_saved_free_entities():
            if not isinstance(entity, dict):
                continue
            pt = entity.get("point")
            if pt is None:
                continue
            ex, ey, ez = _extract_point_components(pt)
            free_entities_payload.append({
                "tool": str(entity.get("tool", "") or ""),
                "x": ex, "y": ey, "z": ez,
                "state": entity.get("state", {}) if isinstance(entity.get("state", {}), dict) else {},
            })

        return CaminoModel(
            id=camino_id,
            tipo_instalacion=tipo_instalacion,
            puntos=puntos,
            entidades_libres=free_entities_payload,
        )

    def export_json(
        self,
        camino_id: Optional[str] = None,
        tipo_instalacion: str = "",
        layer_default: Optional[Dict[str, Any]] = None,
        applied_layers: str = "{}",
        applied_default_attrs: str = "{}",
        applied_custom_attrs: str = "{}",
        indent: int = 2,
        output_dir: Optional[str] = None,
    ) -> str:
        """Build a CaminoModel from current state and return the JSON.

        Convenience wrapper around :meth:`build_camino_model` +
        :func:`generate_json`.

        Args:
            output_dir: When provided, writes the JSON to a timestamped file
                inside this directory and shows a success/error dialog.
        """
        camino = self.build_camino_model(
            camino_id=camino_id,
            tipo_instalacion=tipo_instalacion,
        )
        json_str = generate_json(
            [camino],
            indent=indent,
            layer_default=layer_default,
            selected_inst_type=tipo_instalacion,
            applied_layers=applied_layers,
            applied_default_attrs=applied_default_attrs,
            applied_custom_attrs=applied_custom_attrs,
        )

        if output_dir:
            try:
                from datetime import datetime as _dt
                filename = f"export_{_dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                output_path = os.path.join(output_dir, filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                print(f"[LIBRARY] JSON exported to: {output_path}")
                self._show_export_dialog(output_path)
            except Exception as ex:
                print(f"[LIBRARY] Export write error: {ex}")
                self._show_export_dialog(None, error=str(ex))

        return json_str

    def import_json(self, file_path: Optional[str] = None) -> bool:
        """Import a previously exported JSON file and restore state.

        Args:
            file_path: Path to the JSON file. When ``None``, opens a file
                selection dialog so the user can pick a file.

        Returns:
            ``True`` if the import succeeded and state was restored.
        """
        if file_path is None:
            file_path = self._pick_json_file()
        if not file_path:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            print(f"[LIBRARY] Import read error: {ex}")
            self._show_import_dialog(file_path, error=str(ex))
            return False

        try:
            self._restore_from_export_data(data)
            print(f"[LIBRARY] JSON imported from: {file_path}")
            self._show_import_dialog(file_path)
            return True
        except Exception as ex:
            print(f"[LIBRARY] Import restore error: {ex}")
            self._show_import_dialog(file_path, error=str(ex))
            return False

    def generar_camino_optimo(
        self,
        tipo_instalacion: str = "",
        mock_config: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
    ) -> bool:
        """Run the full optimisation pipeline and preview the result.

        1. Build a CaminoModel from the current state
        2. Translate to the optimizer input format
        3. Write a temp JSON file
        4. Run Caminos_Optimos_Lib as a subprocess (venv Python)
        5. Parse the grafo output
        6. Restore the optimised polyline into the interactor state
        7. Show a result dialog

        Args:
            tipo_instalacion: Installation type string for the camino.
            mock_config: Extra optimizer input fields (``techo``,
                ``obstaculos``, ``configuracion``, etc.).  When *None*,
                a flat techo is auto-computed from the polyline bounding box.
            timeout: Max seconds to wait for the optimizer subprocess.

        Returns:
            ``True`` if the optimised polyline was loaded successfully.
        """
        try:
            from datetime import datetime as _dt
            import optimizer_adapter
            import optimizer_runner
        except ImportError:
            try:
                lib_dir = os.path.dirname(os.path.abspath(__file__))
                if lib_dir not in sys.path:
                    sys.path.insert(0, lib_dir)
                import optimizer_adapter
                import optimizer_runner
            except ImportError as ie:
                print(f"[LIBRARY] Cannot import optimizer modules: {ie}")
                self._show_optimizer_dialog(error=f"Módulos no encontrados: {ie}")
                return False

        camino = self.build_camino_model(tipo_instalacion=tipo_instalacion)
        camino_dict = camino.to_dict()

        if not camino_dict.get("nodos"):
            msg = "No hay nodos para optimizar. Dibuje puntos primero."
            print(f"[LIBRARY] {msg}")
            self._show_optimizer_dialog(error=msg)
            return False

        optimizer_input = optimizer_adapter.build_optimizer_input(
            camino_dict, mock_config=mock_config
        )

        lib_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(lib_dir, "optimizer_temp")
        os.makedirs(temp_dir, exist_ok=True)

        from datetime import datetime as _dt
        stamp = _dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        input_dir = os.path.join(temp_dir, stamp)
        os.makedirs(input_dir, exist_ok=True)
        input_path = os.path.join(input_dir, f"input_{stamp}.json")

        try:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(optimizer_input, f, ensure_ascii=False, indent=2)
            print(f"[LIBRARY] Optimizer input written to: {input_path}")
        except Exception as ex:
            self._show_optimizer_dialog(error=f"Error escribiendo input: {ex}")
            return False

        try:
            grafo = optimizer_runner.run_optimizer(
                input_json_path=input_path,
                timeout=timeout,
            )
        except (TimeoutError, RuntimeError, FileNotFoundError) as ex:
            print(f"[LIBRARY] Optimizer failed: {ex}")
            self._show_optimizer_dialog(error=str(ex))
            return False

        paths = optimizer_adapter.parse_optimizer_output(grafo)
        if not paths:
            msg = "El optimizador no devolvió caminos válidos."
            print(f"[LIBRARY] {msg}")
            self._show_optimizer_dialog(error=msg)
            return False

        import_data = {"caminos": []}
        for idx, pts in enumerate(paths):
            import_data["caminos"].append({
                "polilinea": pts,
                "tipo": f"{tipo_instalacion}_{idx+1}" if len(paths) > 1 else tipo_instalacion,
                "nodos": [],
            })

        try:
            self._restore_from_export_data(import_data)
            num_paths = len(paths)
            total_pts = sum(len(p) for p in paths)
            print(f"[LIBRARY] Optimised polyline loaded: {num_paths} path(s), {total_pts} points")
            self._show_optimizer_dialog(
                num_paths=num_paths,
                total_points=total_pts,
            )
            return True
        except Exception as ex:
            print(f"[LIBRARY] Error restoring optimised data: {ex}")
            self._show_optimizer_dialog(error=str(ex))
            return False

    def _show_optimizer_dialog(
        self,
        num_paths: int = 0,
        total_points: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Show a dialog after the optimiser run."""
        try:
            import ctypes
            MB_OK = 0x0
            MB_TOPMOST = 0x40000
            if error:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Error en optimización:\n\n{error}",
                    "Generar Camino Óptimo",
                    MB_OK | 0x10 | MB_TOPMOST,
                )
            else:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Camino óptimo generado correctamente.\n\n"
                    f"Caminos: {num_paths}\n"
                    f"Puntos totales: {total_points}",
                    "Generar Camino Óptimo",
                    MB_OK | 0x40 | MB_TOPMOST,
                )
        except Exception:
            pass

    def _pick_json_file(self) -> Optional[str]:
        """Open a native file dialog to select a JSON file."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askopenfilename(
                title="Importar JSON",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            root.destroy()
            return path if path else None
        except Exception as ex:
            print(f"[LIBRARY] File dialog error: {ex}")
            return None

    def _restore_from_export_data(self, data: Dict[str, Any]) -> None:
        """Populate interactor state from an imported JSON dict.

        Auto-detects two formats:

        **Optimizer output** (``output.json``)::

            { "caminos": [{"polilinea": [[x,y,z], ...], "nodos": ["id",...]}],
              "nodos": [{"id","tipo","coord","ant","sig"}] }

        **Our export** (``export_*.json``)::

            { "caminos": [{"nodos": [{"id","tipo","coordenadas":[x,y,z],
              "anteriores","siguientes","metadata":{...}}]}] }
        """

        role_label_to_int = {v: k for k, v in CAPTURE_ROLE_LABELS.items()}

        # Top-level nodo map (optimizer output keeps nodos at root level)
        top_nodos = data.get("nodos", [])
        top_nodo_map: Dict[str, Dict[str, Any]] = {}
        for nodo in top_nodos:
            if isinstance(nodo, dict) and "id" in nodo:
                top_nodo_map[nodo["id"]] = nodo

        caminos = data.get("caminos", [])
        saved_paths: List[list] = []
        segments: List[SegmentMetadata] = []

        for camino in caminos:
            if not isinstance(camino, dict):
                continue

            # --- Detect format ---
            polilinea = camino.get("polilinea")
            nodos_list = camino.get("nodos", [])
            is_optimizer_output = isinstance(polilinea, list) and len(polilinea) > 0
            is_our_export = (
                not is_optimizer_output
                and isinstance(nodos_list, list)
                and len(nodos_list) > 0
                and isinstance(nodos_list[0], dict)
                and "coordenadas" in nodos_list[0]
            )

            if is_optimizer_output:
                path_points, path_segments = self._parse_optimizer_camino(
                    polilinea, nodos_list, top_nodo_map, role_label_to_int
                )
            elif is_our_export:
                path_points, path_segments = self._parse_own_export_camino(
                    nodos_list, role_label_to_int
                )
            else:
                print(f"[LIBRARY] Skipping unrecognised camino format: {list(camino.keys())}")
                continue

            if len(path_points) >= 2:
                saved_paths.append(path_points)
                segments.extend(path_segments)

        if not saved_paths:
            print("[LIBRARY] WARNING: imported JSON contained 0 usable paths")

        self.script_object.saved_paths = saved_paths

        if hasattr(self.script_object, "saved_segments"):
            self.script_object.saved_segments = segments

        if hasattr(self.script_object, "saved_free_entities"):
            self.script_object.saved_free_entities = []

        self.points = []
        self.current_point = None
        try:
            self._draw_preview(self._last_preview_point)
        except Exception:
            pass

    def _parse_coord(self, pt: Any) -> Optional[tuple]:
        """Parse a point from various representations to (x, y, z)."""
        if isinstance(pt, (list, tuple)) and len(pt) >= 3:
            return (float(pt[0]), float(pt[1]), float(pt[2]))
        if isinstance(pt, dict):
            x = float(pt.get("x", pt.get("X", 0.0)))
            y = float(pt.get("y", pt.get("Y", 0.0)))
            z = float(pt.get("z", pt.get("Z", 0.0)))
            return (x, y, z)
        return None

    def _make_point(self, x: float, y: float, z: float):
        if ALLPLAN_AVAILABLE:
            return AllplanGeo.Point3D(x, y, z)
        return (x, y, z)

    def _parse_optimizer_camino(
        self, polilinea, nodo_ids, top_nodo_map, role_label_to_int
    ):
        """Parse a camino from optimizer output format (polilinea + nodo ID list)."""
        path_points = []
        for pt in polilinea:
            coords = self._parse_coord(pt)
            if coords:
                path_points.append(self._make_point(*coords))

        segments: List[SegmentMetadata] = []
        for i in range(len(path_points) - 1):
            nodo_info = top_nodo_map.get(nodo_ids[min(i, len(nodo_ids) - 1)], {}) if nodo_ids else {}
            optimizer_tipo = nodo_info.get("tipo", "")
            role = _OPTIMIZER_TYPE_TO_ROLE.get(optimizer_tipo, "Paso")
            role_int = role_label_to_int.get(role, CAPTURE_ROLE_PASO)

            segments.append(SegmentMetadata(
                points=[path_points[i], path_points[i + 1]],
                diameter=DEFAULT_SEGMENT_DIAMETER,
                color_id=1,
                section_type=DEFAULT_SEGMENT_SECTION_TYPE,
                system=DEFAULT_SEGMENT_SYSTEM,
                point_roles=[role_int, CAPTURE_ROLE_PASO],
            ))
        return path_points, segments

    def _parse_own_export_camino(self, nodos_list, role_label_to_int):
        """Parse a camino from our export format (nodos with coordenadas + metadata)."""
        path_points = []
        segments: List[SegmentMetadata] = []

        for nodo in nodos_list:
            if not isinstance(nodo, dict):
                continue
            coords = self._parse_coord(nodo.get("coordenadas"))
            if not coords:
                continue
            path_points.append(self._make_point(*coords))

        for i in range(len(path_points) - 1):
            nodo = nodos_list[i] if i < len(nodos_list) else {}
            optimizer_tipo = nodo.get("tipo", "")
            role = _OPTIMIZER_TYPE_TO_ROLE.get(optimizer_tipo, "Paso")
            role_int = role_label_to_int.get(role, CAPTURE_ROLE_PASO)

            meta = nodo.get("metadata", {})
            diameter = float(meta.get("diameter", DEFAULT_SEGMENT_DIAMETER))
            color_id = int(meta.get("color_id", 1))
            section_type = str(meta.get("section_type", DEFAULT_SEGMENT_SECTION_TYPE))
            system = str(meta.get("system", DEFAULT_SEGMENT_SYSTEM))

            segments.append(SegmentMetadata(
                points=[path_points[i], path_points[i + 1]],
                diameter=diameter,
                color_id=color_id,
                section_type=section_type,
                system=system,
                point_roles=[role_int, CAPTURE_ROLE_PASO],
            ))
        return path_points, segments

    def _show_export_dialog(
        self, path: Optional[str], error: Optional[str] = None
    ) -> None:
        """Show a dialog after JSON export."""
        try:
            import ctypes
            MB_OK = 0x0
            MB_TOPMOST = 0x40000
            if error:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Error al exportar JSON:\n\n{error}",
                    "Exportar JSON",
                    MB_OK | 0x10 | MB_TOPMOST,
                )
            else:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"JSON exportado correctamente.\n\n{path}",
                    "Exportar JSON",
                    MB_OK | 0x40 | MB_TOPMOST,
                )
        except Exception:
            pass

    def _show_import_dialog(
        self, path: Optional[str], error: Optional[str] = None
    ) -> None:
        """Show a dialog after JSON import."""
        try:
            import ctypes
            MB_OK = 0x0
            MB_TOPMOST = 0x40000
            if error:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Error al importar JSON:\n\n{error}",
                    "Importar JSON",
                    MB_OK | 0x10 | MB_TOPMOST,
                )
            else:
                num_paths = len(self.script_object.saved_paths) if hasattr(self.script_object, "saved_paths") else 0
                num_segs = len(self.script_object.saved_segments) if hasattr(self.script_object, "saved_segments") else 0
                if num_paths == 0:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        f"JSON importado pero no se encontraron caminos válidos.\n\n"
                        f"Archivo: {path}\n\n"
                        f"El archivo puede tener un formato no reconocido.",
                        "Importar JSON",
                        MB_OK | 0x30 | MB_TOPMOST,
                    )
                else:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        f"JSON importado correctamente.\n\nArchivo: {path}\nCaminos: {num_paths}\nSegmentos: {num_segs}",
                        "Importar JSON",
                        MB_OK | 0x40 | MB_TOPMOST,
                    )
        except Exception:
            pass

    def _deserialize_state_from_json(self, json_str: str) -> bool:
        try:
            if not json_str or not isinstance(json_str, str) or not json_str.strip():
                return False

            data = json.loads(json_str)
            origin_payload = data.get("origin", {}) if isinstance(data, dict) else {}
            paths_payload = data.get("paths", [])
            segments_payload = data.get("segments", [])
            free_entities_payload = data.get("free_entities", [])

            def _to_point(coords: Any):
                if isinstance(coords, (list, tuple)) and len(coords) >= 3:
                    x, y, z = coords[0], coords[1], coords[2]
                elif isinstance(coords, dict):
                    x, y, z = coords.get("x", 0.0), coords.get("y", 0.0), coords.get("z", 0.0)
                else:
                    x, y, z = 0.0, 0.0, 0.0
                if ALLPLAN_AVAILABLE:
                    return AllplanGeo.Point3D(float(x), float(y), float(z))
                return (float(x), float(y), float(z))

            self.script_object.saved_paths = [
                [_to_point(pt) for pt in path] for path in paths_payload if isinstance(path, list)
            ]

            self.script_object.saved_segments = []
            for seg_dict in segments_payload:
                if not isinstance(seg_dict, dict):
                    continue
                pts = seg_dict.get("points", [])
                seg_dict["points"] = [_to_point(p) for p in pts]
                self.script_object.saved_segments.append(SegmentMetadata.from_legacy(seg_dict))

            self.script_object.saved_free_entities = []
            for entity in free_entities_payload:
                if not isinstance(entity, dict):
                    continue
                pt = entity.get("point", None)
                self.script_object.saved_free_entities.append({
                    "tool": str(entity.get("tool", "") or ""),
                    "point": _to_point(pt),
                    "state": entity.get("state", {}) if isinstance(entity.get("state", {}), dict) else {},
                })

            if not self.script_object.saved_segments and self.script_object.saved_paths:
                for path_idx in range(len(self.script_object.saved_paths)):
                    self._create_default_segments_for_new_path(path_idx)

            self.points = []
            self._clear_editing_state()
            try:
                build_ele = getattr(self.script_object, "build_ele", None)
                if build_ele is not None and isinstance(origin_payload, dict):
                    start_x = getattr(build_ele, "StartX", None)
                    start_y = getattr(build_ele, "StartY", None)
                    start_z = getattr(build_ele, "StartZ", None)
                    if start_x is not None and "x" in origin_payload:
                        start_x.value = float(origin_payload.get("x", 0.0))
                    if start_y is not None and "y" in origin_payload:
                        start_y.value = float(origin_payload.get("y", 0.0))
                    if start_z is not None and "z" in origin_payload:
                        start_z.value = float(origin_payload.get("z", 0.0))
                    self._origin_auto_set = True
            except Exception:
                pass
            return True
        except Exception as ex:
            print(f"[INT] Error deserializing state: {ex}")
            return False

    def _restore_saved_state(self) -> bool:
        try:
            for param_name in ("SavedState", "PolylineState", "StateData"):
                try:
                    value = self._safe_get_palette_property(param_name)
                    value = self._normalize_palette_value(value)
                    if isinstance(value, str) and value.strip():
                        if self._deserialize_state_from_json(value):
                            print(f"[INT] Restored state from build_ele.{param_name}")
                            return True
                except Exception:
                    continue

            if self.is_modification_mode and ALLPLAN_AVAILABLE and self.coord_input is not None:
                try:
                    mod_list = getattr(self.script_object, "modification_ele_list", None)
                    if mod_list is not None and hasattr(mod_list, "get_base_element_adapter"):
                        doc = self.coord_input.GetInputViewDocument()
                        adapter = mod_list.get_base_element_adapter(doc)
                        if adapter and hasattr(adapter, "IsNull") and not adapter.IsNull():
                            success, _name, parameter = AllplanBaseElements.PythonPartService.GetParameter(adapter)
                            if success and parameter:
                                lines = parameter.split("\n") if isinstance(parameter, str) else list(parameter)
                                for line in lines:
                                    if not isinstance(line, str):
                                        continue
                                    line = line.strip()
                                    if line.startswith("SavedState") and "=" in line:
                                        state_json = line.split("=", 1)[1].strip()
                                        if state_json and self._deserialize_state_from_json(state_json):
                                            print("[INT] Restored state from PythonPartGroup.SavedState")
                                            return True
                                        break
                except Exception as ex:
                    print(f"[INT] Error restoring state from PythonPartGroup: {ex}")
            return False
        except Exception as ex:
            print(f"[INT] Error restoring state: {ex}")
            return False

    def _persist_state_to_build_ele(self) -> bool:
        build_ele = getattr(self.script_object, "build_ele", None)
        if build_ele is None:
            return False
        state_json = self._serialize_state_to_json()
        if not state_json:
            return False
        for param_name in ("SavedState", "PolylineState", "StateData"):
            if hasattr(build_ele, param_name):
                try:
                    self._safe_set_palette_property(param_name, state_json)
                    return True
                except Exception:
                    continue
        return False

    # ===== Undo/Cancel Flow =====
    def _save_state_snapshot(self) -> None:
        """Save current state to undo stack."""
        snapshot = {
            'points': [p for p in self.points] if self.points else [],
            'saved_paths': [[p for p in path] for path in self.script_object.saved_paths] if self.script_object.saved_paths else [],
            'saved_segments': [seg.to_dict() if isinstance(seg, SegmentMetadata) else seg for seg in self.script_object.saved_segments],
            'saved_free_entities': [
                {
                    "tool": str(e.get("tool", "") or ""),
                    "point": e.get("point", None),
                    "state": e.get("state", {}) if isinstance(e.get("state", {}), dict) else {},
                }
                for e in self._get_saved_free_entities()
                if isinstance(e, dict)
            ],
            'mode': self.mode,
            'create_mode': self.create_mode,
            'insert_mode': self.insert_mode,
        }
        
        # Save as initial state if this is the first snapshot
        if self._initial_state is None:
            self._initial_state = snapshot.copy()
        
        # Add to undo stack (limit depth)
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._max_undo_depth:
            self._undo_stack.pop(0)  # Remove oldest

    def _restore_state_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from a snapshot."""
        try:
            # Restore points
            if ALLPLAN_AVAILABLE:
                self.points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) if hasattr(p, 'X') else p for p in snapshot.get('points', [])]
            else:
                self.points = list(snapshot.get('points', []))
            
            # Restore saved paths
            if ALLPLAN_AVAILABLE:
                self.script_object.saved_paths = [
                    [AllplanGeo.Point3D(p.X, p.Y, p.Z) if hasattr(p, 'X') else p for p in path]
                    for path in snapshot.get('saved_paths', [])
                ]
            else:
                self.script_object.saved_paths = [list(path) for path in snapshot.get('saved_paths', [])]
            
            # Restore saved segments
            self.script_object.saved_segments = [
                SegmentMetadata.from_legacy(seg) for seg in snapshot.get('saved_segments', [])
            ]
            # Restore free entities
            self.script_object.saved_free_entities = []
            for entity in snapshot.get('saved_free_entities', []):
                if not isinstance(entity, dict):
                    continue
                pt = entity.get("point", None)
                if ALLPLAN_AVAILABLE and hasattr(pt, "X"):
                    cloned_pt = AllplanGeo.Point3D(pt.X, pt.Y, pt.Z)
                else:
                    cloned_pt = pt
                self.script_object.saved_free_entities.append({
                    "tool": str(entity.get("tool", "") or ""),
                    "point": cloned_pt,
                    "state": entity.get("state", {}) if isinstance(entity.get("state", {}), dict) else {},
                })
            
            # Restore modes
            self.mode = snapshot.get('mode', MODE_CREATE if snapshot.get('create_mode', False) else MODE_EDIT)
            self.create_mode = snapshot.get('create_mode', self.mode in (MODE_CREATE, MODE_EXTEND))
            self.insert_mode = snapshot.get('insert_mode', False)
            
            # Clear editing state
            self._clear_editing_state()
        except Exception as ex:
            if hasattr(self, '_debug') and self._debug:
                print(f"[INT] Error restoring state: {ex}")

    def undo(self) -> bool:
        """Undo last operation.
        
        Returns:
            True if undo was successful, False if nothing to undo
        """
        if not self._undo_stack:
            return False
        
        # Remove current state (last in stack)
        if len(self._undo_stack) > 1:
            self._undo_stack.pop()  # Remove current state
            previous_state = self._undo_stack[-1]  # Get previous state
            self._restore_state_snapshot(previous_state)
            return True
        elif len(self._undo_stack) == 1:
            # Only initial state remains, restore it
            initial = self._undo_stack[0]
            self._restore_state_snapshot(initial)
            return True
        
        return False

    def _handle_cancel(self) -> bool:
        """Handle cancel (ESC key) - In transactional mode, finalize and create.
        
        Returns:
            True if cancel was handled
        """
        print("\n" + "="*80)
        print("[INT] ESC KEY PRESSED - FINALIZING POLYLINE")
        print(f"[INT] Points in current polyline: {len(self.points)}")
        print(f"[INT] Saved paths: {len(self.script_object.saved_paths)}")
        print("="*80)
        
        # Save current polyline if we have points
        if len(self.points) >= 2:
            print("[INT] Saving current polyline before finalize...")
            self.save_current_polyline()

        # Persist state for re-entry
        try:
            self._persist_state_to_build_ele()
        except Exception:
            pass
        
        # Trigger finalize to create all geometry
        print("[INT] Calling _finalize_and_create_now() to create geometry...")
        if hasattr(self.script_object, '_finalize_and_create_now'):
            finalize = getattr(self.script_object, '_finalize_and_create_now')
            if callable(finalize):
                finalize()
                print("[INT] Finalize called - geometry should be created now")
        
        print("="*80 + "\n")
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 1

    # ===== Branching & Fittings API =====
    def create_branch(self, branch_point: Any, parent_segment: SegmentMetadata) -> List[Any]:
        """Create a branch at the specified point on a parent segment.
        
        Args:
            branch_point: Point where branch should be created
            parent_segment: Parent segment metadata
            
        Returns:
            List of model elements created for the branch
        """
        if self.branching_hook is not None:
            try:
                return self.branching_hook(branch_point, parent_segment)
            except Exception as ex:
                if hasattr(self, '_debug') and self._debug:
                    print(f"[INT] Error in branching_hook: {ex}")
        
        # Default: return empty list (installations must implement hook)
        return []

    def create_fitting(self, fitting_type: str, segment1: SegmentMetadata, segment2: SegmentMetadata) -> List[Any]:
        """Create a fitting between two segments.
        
        Args:
            fitting_type: Type of fitting (e.g., 'elbow', 'reducer', 'tee', etc.)
            segment1: First segment metadata
            segment2: Second segment metadata
            
        Returns:
            List of model elements created for the fitting
        """
        if self.fitting_hook is not None:
            try:
                return self.fitting_hook(fitting_type, segment1, segment2)
            except Exception as ex:
                if hasattr(self, '_debug') and self._debug:
                    print(f"[INT] Error in fitting_hook: {ex}")
        
        # Try specific hooks based on fitting type
        elbow_hook = self.elbow_hook
        if fitting_type.lower() == 'elbow' and elbow_hook is not None:
            try:
                # Calculate angle between segments
                angle = self._calculate_segment_angle(segment1, segment2)
                return elbow_hook(segment1, segment2, angle)
            except Exception as ex:
                if hasattr(self, '_debug') and self._debug:
                    print(f"[INT] Error in elbow_hook: {ex}")
        
        reducer_hook = self.reducer_hook
        if fitting_type.lower() == 'reducer' and reducer_hook is not None:
            try:
                return reducer_hook(segment1, segment2, segment1.diameter, segment2.diameter)
            except Exception as ex:
                if hasattr(self, '_debug') and self._debug:
                    print(f"[INT] Error in reducer_hook: {ex}")
        
        # Default: return empty list (installations must implement hook)
        return []

    def create_bifurcation(self, parent_segment: SegmentMetadata, branch1: SegmentMetadata, branch2: SegmentMetadata) -> List[Any]:
        """Create a bifurcation (split) from one parent segment into two branches.
        
        Args:
            parent_segment: Parent segment metadata
            branch1: First branch segment metadata
            branch2: Second branch segment metadata
            
        Returns:
            List of model elements created for the bifurcation
        """
        if self.bifurcation_hook is not None:
            try:
                return self.bifurcation_hook(parent_segment, branch1, branch2)
            except Exception as ex:
                if hasattr(self, '_debug') and self._debug:
                    print(f"[INT] Error in bifurcation_hook: {ex}")
        
        # Default: return empty list (installations must implement hook)
        return []

    def _calculate_segment_angle(self, seg1: SegmentMetadata, seg2: SegmentMetadata) -> float:
        """Calculate angle between two segments in degrees."""
        if not ALLPLAN_AVAILABLE or len(seg1.points) < 2 or len(seg2.points) < 2:
            return 0.0
        
        try:
            # Get direction vectors
            dir1 = AllplanGeo.Vector3D(
                seg1.points[1].X - seg1.points[0].X,
                seg1.points[1].Y - seg1.points[0].Y,
                seg1.points[1].Z - seg1.points[0].Z
            )
            dir2 = AllplanGeo.Vector3D(
                seg2.points[1].X - seg2.points[0].X,
                seg2.points[1].Y - seg2.points[0].Y,
                seg2.points[1].Z - seg2.points[0].Z
            )
            
            # Normalize
            len1 = (dir1.X*dir1.X + dir1.Y*dir1.Y + dir1.Z*dir1.Z) ** 0.5
            len2 = (dir2.X*dir2.X + dir2.Y*dir2.Y + dir2.Z*dir2.Z) ** 0.5
            
            if len1 < 1e-6 or len2 < 1e-6:
                return 0.0
            
            # Dot product
            dot = (dir1.X*dir2.X + dir1.Y*dir2.Y + dir1.Z*dir2.Z) / (len1 * len2)
            dot = max(-1.0, min(1.0, dot))  # Clamp to valid range
            
            # Angle in degrees
            angle_rad = math.acos(dot)
            return math.degrees(angle_rad)
        except Exception:
            return 0.0

    def process_mouse_msg(self, mouse_msg, pnt, _msg_info) -> bool:
        """Process mouse messages.

        Returns True if the message was handled.
        """
        # FIRST print to confirm this is being called AT ALL
        if not hasattr(self, '_first_mouse_msg_logged'):
            print("\n" + "!"*80)
            print("[INT] process_mouse_msg() CALLED FOR FIRST TIME!")
            print(f"[INT] ALLPLAN_AVAILABLE: {ALLPLAN_AVAILABLE}")
            print(f"[INT] coord_input: {self.coord_input}")
            print("!"*80 + "\n")
            self._first_mouse_msg_logged = True
        
        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            print(f"[INT] Returning False - ALLPLAN_AVAILABLE={ALLPLAN_AVAILABLE}, coord_input={self.coord_input}")
            return False

        try:
            # Check for ESC key (cancel)
            # Debug: Check what attributes mouse_msg actually has (log only once)
            # Check for ESC key
            if hasattr(mouse_msg, 'Key') and hasattr(mouse_msg, 'IsKeyDown'):
                try:
                    if mouse_msg.IsKeyDown(27):  # ESC key
                        return self._handle_cancel()
                except Exception as e:
                    print(f"[INT] Error checking ESC key: {e}")

            # Sync palette state (only check for changes, don't spam console)
            self._sync_create_mode_from_palette()
            self._sync_insert_mode_from_palette()
            if self.capture_mode and self.capture_handler:
                self.capture_handler.check_finish_now()

            # EDIT MODE: Handle differently - use GetInputPoint but without drawing mode parameters
            # In edit mode, we want to click segments, not draw new points
            if self._is_edit_mode():
                # In edit mode, get point but don't enable drawing mode (pass empty/None for last point)
                # This prevents the crosshair from appearing
                try:
                    raw_pnt = self.coord_input.GetInputPoint(
                        mouse_msg, pnt, _msg_info, AllplanGeo.Point3D(), False  # No last point, no angle tracking
                    ).GetPoint()
                except:
                    # Fallback: convert 2D point to 3D directly
                    raw_pnt = AllplanGeo.Point3D(pnt.X, pnt.Y, 0.0)
                
                # Convert to relative coordinates
                if raw_pnt is None:
                    try:
                        raw_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    except Exception:
                        raw_pnt = None
                relative_pnt = self._apply_origin_offset(raw_pnt) if raw_pnt is not None else None
                current_pnt = relative_pnt  # No angle limiting in edit mode
                
                if current_pnt is None and self._last_preview_point is not None:
                    self._draw_preview(self._last_preview_point)
                    return True
                
                # Handle mouse movement
                if self.coord_input.IsMouseMove(mouse_msg):
                    self._handle_mouse_move(current_pnt)
                    return True
                
                # When dragging, only handle button release (not clicks)
                if self.is_dragging:
                    # Check for button release
                    button_val = getattr(mouse_msg, 'Button', None)
                    # Detect release: button_val == 0, or transition from 1 to None/0
                    is_release = (button_val == 0) or (self._last_button_state == 1 and button_val is None)
                    # Fallback for environments where Button is always None:
                    # a non-move message while dragging is treated as "place/release".
                    if (not is_release) and (button_val is None):
                        try:
                            if not self.coord_input.IsMouseMove(mouse_msg):
                                is_release = True
                        except Exception:
                            pass
                    
                    if is_release:
                        # Button released - stop dragging
                        print(f"[INT] ✓ Button released - stopping drag (button_val={button_val}, last={self._last_button_state})")
                        
                        # CRITICAL: Rebuild segments for dragged path to sync with new positions
                        if self.drag_path_idx is not None:
                            self._rebuild_segments_for_path(self.drag_path_idx)
                            print(f"[INT] ✓ Rebuilt segments for path {self.drag_path_idx} after drag")
                        elif self.drag_free_entity_idx is not None:
                            print(f"[INT] ✓ Finished dragging free entity {self.drag_free_entity_idx}")
                        
                        self.is_dragging = False
                        self.drag_path_idx = None
                        self.drag_vertex_idx = None
                        self.drag_free_entity_idx = None
                        self._drag_start_point = None
                        self._drag_start_path = None
                        self.hover_vertex = None  # Clear hover when drag ends
                        self._last_button_state = None
                        self._update_status("Drag complete")
                        self._draw_preview(current_pnt)
                        return True
                    
                    # Update button state tracking
                    if button_val is not None:
                        self._last_button_state = button_val
                    
                    # Still dragging - ignore this message (handled by _handle_mouse_move)
                    return True

                # If a free-point tool is active, delegate click handling to capture handler
                # even while mode is EDIT. This preserves edit mode cursor/selection behavior
                # while allowing macro/element free-point placement workflows.
                if self.capture_mode and self.capture_handler:
                    try:
                        if self.capture_handler.has_active_free_point_tool():
                            return bool(self.capture_handler.handle_point_click(raw_pnt))
                    except Exception:
                        pass
                
                # Handle clicks in edit mode (only when NOT dragging)
                # CRITICAL: Update hover state before processing click (hover might not be set yet)
                self._update_edit_mode_hover(current_pnt)
                return self._handle_edit_mode_click(current_pnt, raw_pnt, mouse_msg)
            
            # CAPTURE MODE (PointInput_SO alignment): Use raw coordinates - no origin offset, no angle limiting
            # Matches PointInput_SO: GetInputPoint returns world coords, use directly
            if self.capture_mode and self.capture_handler:
                try:
                    raw_pnt = self.coord_input.GetInputPoint(
                        mouse_msg, pnt, _msg_info, AllplanGeo.Point3D(), False
                    ).GetPoint()
                except Exception:
                    raw_pnt = AllplanGeo.Point3D(pnt.X, pnt.Y, 0.0) if ALLPLAN_AVAILABLE else None
                if raw_pnt is None:
                    try:
                        raw_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    except Exception:
                        raw_pnt = None
                if raw_pnt is None and self._last_preview_point is not None:
                    self._draw_preview(self._last_preview_point)
                    return True
                is_mouse_move = self.coord_input.IsMouseMove(mouse_msg)
                if is_mouse_move:
                    self.current_point = raw_pnt
                    self._draw_preview(raw_pnt)
                    return True
                return self._handle_left_click(raw_pnt, raw_pnt)
            
            # CREATE/EXTEND MODE: Use normal GetInputPoint (shows crosshair for drawing)
            # Get current point
            # NOTE: the third argument must be the provided _msg_info; using an
            # undefined variable here breaks the interaction loop.
            # CRITICAL: When angle limiter is OFF, pass None/empty to disable Allplan's native
            # angle tracking ("Track line 90.0"). When ON, pass last point in WORLD coordinates.
            limit_angles = self._get_palette_limit_angles()
            last_world_pt = None
            if limit_angles and self.points and len(self.points) > 0:
                # Angle limiter ON: Pass last point so Allplan can track angles
                last_world_pt = self._to_world_coordinates(self.points[-1])
            elif limit_angles and self.current_point:
                last_world_pt = self._to_world_coordinates(self.current_point)
            # else: angle limiter OFF, pass None/empty to disable Allplan's native tracking
            
            raw_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, _msg_info, last_world_pt or AllplanGeo.Point3D(), bool(self.points) and limit_angles
            ).GetPoint()
            if raw_pnt is None:
                try:
                    raw_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                except Exception:
                    raw_pnt = None
            if raw_pnt is None and self._last_preview_point is not None:
                self._draw_preview(self._last_preview_point)
                return True

            # CRITICAL: Convert to relative coordinates FIRST, then apply angle limiting
            # Angle limiting must work on relative coordinates to avoid infinity issues
            is_mouse_move = self.coord_input.IsMouseMove(mouse_msg)
            if (
                not is_mouse_move
                and not self._origin_auto_set
                and self._is_create_like_mode()
                and len(self.points) == 0
                and not self.is_modification_mode
                and not self.capture_mode
                and not (hasattr(self.script_object, "saved_paths") and self.script_object.saved_paths)
            ):
                self._auto_set_origin(raw_pnt, round_to_meter=False)

            relative_pnt = self._apply_origin_offset(raw_pnt)
            current_pnt = self._apply_angle_limiting(relative_pnt)

            # Handle mouse movement
            if is_mouse_move:
                # current_pnt is already in relative coordinates after origin offset + angle limiting
                self._handle_mouse_move(current_pnt)
                return True

            # CREATE MODE: Handle normal polyline creation
            # For non-move messages, check button state properly
            # mouse_msg might have a Button attribute or might be an enum
            button_val = getattr(mouse_msg, 'Button', None)
            
            if button_val is not None:
                # Button attribute exists - check its value
                if button_val == 1:
                    return self._handle_left_click(current_pnt, raw_pnt)
                elif button_val == 2:
                    return self._handle_right_click()
            else:
                # No Button attribute - assume left click for unknown non-move messages
                return self._handle_left_click(current_pnt, raw_pnt)

        except Exception as ex:
            print(f"[INT] Error processing mouse message: {ex}")
        return False

    def _apply_angle_limiting(self, relative_pnt: Any) -> Any:
        """Apply angle limiting if enabled.
        
        CRITICAL: This function expects RELATIVE coordinates (after origin offset).
        Working on relative coordinates prevents infinity coordinate issues.
        """
        if not self._get_palette_limit_angles() or not self._is_create_like_mode() or len(self.points) < 1:
            return relative_pnt

        if not ALLPLAN_AVAILABLE:
            return relative_pnt

        try:
            last_point = self.points[-1]  # Already in relative coordinates
            dx = relative_pnt.X - last_point.X
            dy = relative_pnt.Y - last_point.Y
            dz = relative_pnt.Z - last_point.Z
            dist = (dx*dx + dy*dy + dz*dz) ** 0.5

            if dist > 1e-6:
                angle = math.atan2(dy, dx)
                angle_deg = (math.degrees(angle) % 360.0)
                # Use installation angles if available, otherwise module defaults
                valid_angles = self.angle_steps if self.angle_steps else ANGLE_SNAP_VALUES
                closest = min(valid_angles, key=lambda va: abs(angle_deg - va))
                snap_dx, snap_dy = self._snap_dx_dy(dist, closest)
                # Return in relative coordinates (matching last_point coordinate system)
                return AllplanGeo.Point3D(last_point.X + snap_dx, last_point.Y + snap_dy, relative_pnt.Z)
        except Exception as ex:
            print(f"[INT] Error in angle limiting: {ex}")

        return relative_pnt

    def _snap_dx_dy(self, dist: float, angle_deg: float) -> Tuple[float, float]:
        """Return dx/dy aligned to an angle with exact orthogonal/45 snapping."""
        angle_deg = angle_deg % 360.0
        snap_angle_rad = math.radians(angle_deg)
        cos_a = math.cos(snap_angle_rad)
        sin_a = math.sin(snap_angle_rad)

        # Exact orthogonal snapping
        if angle_deg % 90.0 == 0.0:
            if angle_deg in (0.0, 180.0):
                return (dist if cos_a >= 0 else -dist, 0.0)
            return (0.0, dist if sin_a >= 0 else -dist)

        # Exact 45-degree snapping
        if angle_deg % 45.0 == 0.0:
            comp = dist / math.sqrt(2.0)
            return (comp if cos_a >= 0 else -comp, comp if sin_a >= 0 else -comp)

        return (dist * cos_a, dist * sin_a)

    def _snap_path_to_angles(self, path: List[Any]) -> List[Any]:
        """Force each segment to align to snap angles (used at save time)."""
        if len(path) < 2:
            return path

        snapped: List[Any] = []
        try:
            last = path[0]
            snapped.append(last)
            valid_angles = self.angle_steps if self.angle_steps else ANGLE_SNAP_VALUES
            for idx in range(1, len(path)):
                current = path[idx]
                dx = current.X - last.X
                dy = current.Y - last.Y
                dz = current.Z - last.Z
                dist = (dx * dx + dy * dy + dz * dz) ** 0.5
                if dist <= 1e-6:
                    snapped.append(current)
                    last = current
                    continue
                angle = math.atan2(dy, dx)
                angle_deg = (math.degrees(angle) % 360.0)
                closest = min(valid_angles, key=lambda va: abs(angle_deg - va))
                snap_dx, snap_dy = self._snap_dx_dy(dist, closest)
                if ALLPLAN_AVAILABLE:
                    new_pt = AllplanGeo.Point3D(last.X + snap_dx, last.Y + snap_dy, current.Z)
                else:
                    new_pt = (last.X + snap_dx, last.Y + snap_dy, current.Z)
                snapped.append(new_pt)
                last = new_pt
        except Exception:
            return path
        return snapped

    def _handle_mouse_move(self, current_pnt: Any):
        """Handle mouse movement.
        
        CRITICAL: current_pnt is already in relative coordinates (from process_mouse_msg).
        """
        # Update coordinate display in palette (needs world coordinates for display)
        world_pnt = self._to_world_coordinates(current_pnt)
        self._update_coordinate_display(world_pnt)
        
        # EDIT MODE: Handle segment hover and dragging
        if self._is_edit_mode():
            self._update_edit_mode_hover(current_pnt)
            if self.is_dragging:
                # Dragging entire polyline or vertex
                if hasattr(self, 'drag_path_idx') and self.drag_path_idx is not None:
                    # Dragging a saved path
                    path_idx = self.drag_path_idx
                    if 0 <= path_idx < len(self.script_object.saved_paths):
                        path = self.script_object.saved_paths[path_idx]
                        if hasattr(self, 'drag_vertex_idx') and self.drag_vertex_idx is not None and 0 <= self.drag_vertex_idx < len(path):
                            # Dragging a single vertex - just move it to new position (rubberband effect)
                            # The rest of the polyline stays in place, only this vertex moves
                            path[self.drag_vertex_idx] = current_pnt
                            # NOTE: Don't rebuild segments during drag - only when drag stops (for performance)
                        elif hasattr(self, '_drag_start_path') and self._drag_start_path and hasattr(self, '_drag_start_point') and self._drag_start_point:
                            # Dragging entire path - calculate offset from drag start
                            offset_x = current_pnt.X - self._drag_start_point.X
                            offset_y = current_pnt.Y - self._drag_start_point.Y
                            offset_z = current_pnt.Z - self._drag_start_point.Z
                            
                            # Apply offset to all vertices (using original positions from drag start)
                            for i, orig_pt in enumerate(self._drag_start_path):
                                if i < len(path):
                                    path[i] = AllplanGeo.Point3D(orig_pt.X + offset_x, orig_pt.Y + offset_y, orig_pt.Z + offset_z)
                            # NOTE: Don't rebuild segments during drag - only when drag stops (for performance)
                elif self.drag_free_entity_idx is not None:
                    entities = self._get_saved_free_entities()
                    if 0 <= self.drag_free_entity_idx < len(entities):
                        entities[self.drag_free_entity_idx]["point"] = self._clone_point3d(current_pnt)
            self.current_point = current_pnt
            self._draw_preview(current_pnt)
            return
        
        # CREATE MODE: Handle normal polyline creation
        # current_pnt is already in relative coordinates - no need to apply origin offset again!
        if self.is_dragging and 0 <= self.drag_index < len(self.points):
            self.points[self.drag_index] = current_pnt
            self.current_point = current_pnt
            self.hover_index = -1
        else:
            self.current_point = current_pnt
            self.hover_index = self._find_hover_index(current_pnt) if self._is_create_like_mode() else -1

        self._draw_preview(current_pnt)

    def _update_edit_mode_hover(self, current_pnt: Any):
        """Update hover state in edit mode (segment selection, midpoint detection, vertex hover)."""
        # Free-point entities hover (works with or without saved polylines)
        self.hover_free_entity = None
        free_entities = self._get_saved_free_entities()
        if free_entities:
            min_entity_dist = 120.0
            closest_idx = None
            closest_dist = min_entity_dist
            for idx, entity in enumerate(free_entities):
                if not isinstance(entity, dict):
                    continue
                pt = entity.get("point", None)
                if pt is None:
                    continue
                dx = current_pnt.X - pt.X
                dy = current_pnt.Y - pt.Y
                dz = current_pnt.Z - pt.Z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_idx = idx
            self.hover_free_entity = closest_idx

        if not hasattr(self.script_object, 'saved_paths') or not self.script_object.saved_paths:
            self.hover_seg = None
            self.hover_mid = None
            self.hover_vertex = None
            return
        
        # Check for segment hover (clickable segments)
        min_dist = 50.0  # 50mm tolerance for segment selection
        closest_seg = None
        closest_dist = min_dist
        
        for path_idx, path in enumerate(self.script_object.saved_paths):
            if len(path) < 2:
                continue
            
            # Check each segment in this path
            for seg_idx in range(len(path) - 1):
                p1, p2 = path[seg_idx], path[seg_idx + 1]
                
                # Calculate distance from point to segment
                seg_vec = AllplanGeo.Vector3D(p2.X - p1.X, p2.Y - p1.Y, p2.Z - p1.Z)
                pt_vec = AllplanGeo.Vector3D(current_pnt.X - p1.X, current_pnt.Y - p1.Y, current_pnt.Z - p1.Z)
                
                seg_len_sq = seg_vec.X*seg_vec.X + seg_vec.Y*seg_vec.Y + seg_vec.Z*seg_vec.Z
                if seg_len_sq < 1e-6:
                    continue
                
                # Project point onto segment
                t = (pt_vec.X*seg_vec.X + pt_vec.Y*seg_vec.Y + pt_vec.Z*seg_vec.Z) / seg_len_sq
                t = max(0.0, min(1.0, t))  # Clamp to segment
                
                # Closest point on segment
                closest_pt = AllplanGeo.Point3D(
                    p1.X + t * seg_vec.X,
                    p1.Y + t * seg_vec.Y,
                    p1.Z + t * seg_vec.Z
                )
                
                # Distance to segment
                dx = current_pnt.X - closest_pt.X
                dy = current_pnt.Y - closest_pt.Y
                dz = current_pnt.Z - closest_pt.Z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < closest_dist:
                    closest_dist = dist
                    closest_seg = (path_idx, seg_idx)
                    
                    # Check if near midpoint (for midpoint handle)
                    if abs(t - 0.5) < 0.1:  # Within 10% of midpoint
                        mid_pt = AllplanGeo.Point3D(
                            (p1.X + p2.X) / 2,
                            (p1.Y + p2.Y) / 2,
                            (p1.Z + p2.Z) / 2
                        )
                        mid_dx = current_pnt.X - mid_pt.X
                        mid_dy = current_pnt.Y - mid_pt.Y
                        mid_dz = current_pnt.Z - mid_pt.Z
                        mid_dist = math.sqrt(mid_dx*mid_dx + mid_dy*mid_dy + mid_dz*mid_dz)
                        if mid_dist < 50.0:  # 50mm tolerance for midpoint (increased for easier selection)
                            self.hover_mid = (path_idx, seg_idx, mid_pt)
                        else:
                            self.hover_mid = None
                    else:
                        self.hover_mid = None
        
        self.hover_seg = closest_seg if closest_dist < min_dist else None
        
        # Check for vertex hover (for dragging feedback) - PRIORITY: Check vertices BEFORE segments
        # This ensures vertex detection works even when near segments
        self.hover_vertex = None
        if not self.is_dragging:  # Only check hover when not dragging
            min_vertex_dist = 30.0  # 30mm tolerance for vertex hover (increased for better detection)
            closest_vertex = None
            closest_vertex_dist = min_vertex_dist
            
            for path_idx, path in enumerate(self.script_object.saved_paths):
                for vertex_idx, vertex_pt in enumerate(path):
                    # Both current_pnt and vertex_pt are in relative coordinates
                    dx = current_pnt.X - vertex_pt.X
                    dy = current_pnt.Y - vertex_pt.Y
                    dz = current_pnt.Z - vertex_pt.Z
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < closest_vertex_dist:
                        closest_vertex_dist = dist
                        closest_vertex = (path_idx, vertex_idx)
            
            if closest_vertex:
                self.hover_vertex = closest_vertex

    def _handle_edit_mode_click(self, current_pnt: Any, raw_pnt: Any, mouse_msg: Any) -> bool:
        """Handle clicks in edit mode (segment selection, dragging, etc.).
        
        NOTE: Dragging is now handled in process_mouse_msg before this is called.
        This function only handles clicks when NOT dragging.
        """
        button_val = getattr(mouse_msg, 'Button', None)
        
        # Debug: Log click detection
        print(f"[INT] Edit mode click: button_val={button_val}, hover_seg={self.hover_seg}, hover_mid={self.hover_mid}, hover_vertex={self.hover_vertex}")
        
        # Only process left mouse button clicks (button_val == 1)
        # Also handle cases where button_val might be None but it's a click (not a move)
        if button_val is not None and button_val != 1:
            # Right click or other button - ignore
            return True
        
        # If button_val is None, check if it's a mouse move (if so, ignore)
        if button_val is None:
            if self.coord_input.IsMouseMove(mouse_msg):
                return True  # It's a move, not a click
            # If it's not a move and button_val is None, treat it as a left click
            # (Allplan sometimes doesn't set Button attribute for clicks)
            print(f"[INT] Treating None button_val as left click (not a move)")

        # PRIORITY -1: Free-point entity selection/dragging in edit mode.
        if self.hover_free_entity is not None:
            entity_idx = self.hover_free_entity
            entities = self._get_saved_free_entities()
            if 0 <= entity_idx < len(entities):
                self.selected_free_entity = entity_idx
                self.selected_seg = None
                self.is_dragging = True
                self.drag_free_entity_idx = entity_idx
                self.drag_path_idx = None
                self.drag_vertex_idx = None
                self._update_status(f"Selected free entity #{entity_idx}")
                self._draw_preview(current_pnt)
                return True

        # PRIORITY 0: Real cut/add-cut behavior in edit mode.
        if self.insert_mode and (self.hover_seg or self.selected_seg):
            if self.split_hovered_or_selected_segment(current_pnt):
                self._draw_preview(current_pnt)
                return True
        
        # PRIORITY 1: Check if clicking on a segment midpoint (for segment selection) - HIGHEST PRIORITY
        # This must come FIRST so clicking midpoints selects segments instead of dragging
        if self.hover_mid:
            path_idx, seg_idx, mid_pt = self.hover_mid
            # Find the actual segment index in saved_segments by matching path_idx and seg_idx
            # Use geometry matching as fallback to ensure we get the correct segment
            actual_seg_idx = None
            matching_segments = []
            
            # First, try to find by path_idx and seg_idx
            for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(saved_seg)
                if seg_meta.custom.get("path_idx") == path_idx and seg_meta.custom.get("seg_idx") == seg_idx:
                    matching_segments.append((saved_idx, seg_meta))
            
            # If multiple matches (duplicate indices), use geometry to find the correct one
            if len(matching_segments) > 1:
                print(f"[INT] Warning: Multiple segments with path_idx={path_idx}, seg_idx={seg_idx}, using geometry match")
                # Find the segment whose midpoint is closest to the clicked point
                best_match = None
                best_dist = float('inf')
                for saved_idx, seg_meta in matching_segments:
                    if len(seg_meta.points) >= 2:
                        p0, p1 = seg_meta.points[0], seg_meta.points[1]
                        seg_mid = AllplanGeo.Point3D((p0.X + p1.X) / 2, (p0.Y + p1.Y) / 2, (p0.Z + p1.Z) / 2)
                        dx = mid_pt.X - seg_mid.X
                        dy = mid_pt.Y - seg_mid.Y
                        dz = mid_pt.Z - seg_mid.Z
                        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                        if dist < best_dist:
                            best_dist = dist
                            best_match = saved_idx
                actual_seg_idx = best_match
            elif len(matching_segments) == 1:
                actual_seg_idx = matching_segments[0][0]
            else:
                # No match by indices - try geometry matching
                print(f"[INT] No segment found with path_idx={path_idx}, seg_idx={seg_idx}, trying geometry match")
                if path_idx < len(self.script_object.saved_paths):
                    path = self.script_object.saved_paths[path_idx]
                    if seg_idx < len(path) - 1:
                        p0, p1 = path[seg_idx], path[seg_idx + 1]
                        # Find segment in saved_segments that matches these points
                        for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                            seg_meta = SegmentMetadata.from_legacy(saved_seg)
                            if len(seg_meta.points) >= 2:
                                s0, s1 = seg_meta.points[0], seg_meta.points[1]
                                if (self._dist_sq(p0, s0) < 1.0 and self._dist_sq(p1, s1) < 1.0) or \
                                   (self._dist_sq(p0, s1) < 1.0 and self._dist_sq(p1, s0) < 1.0):
                                    actual_seg_idx = saved_idx
                                    break
            
            # Select this segment
            self.selected_seg = (path_idx, seg_idx)
            print(f"[INT] Selected segment: path {path_idx}, segment {seg_idx} (saved_segments index: {actual_seg_idx})")
            self._update_status(f"Selected: Path {path_idx}, Segment {seg_idx}")
            
            # Update palette with segment info if available
            # CRITICAL: Update diameter FIRST, then SegmentIndex to ensure both are set correctly
            if actual_seg_idx is not None and 0 <= actual_seg_idx < len(self.script_object.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(self.script_object.saved_segments[actual_seg_idx])
                # Update palette fields (diameter, segment index, etc.)
                try:
                    # Update diameter FIRST - this is the most important for user feedback
                    diameter_field = getattr(self.script_object.build_ele, "NewDiameter", None)
                    if diameter_field:
                        # Ensure diameter is a valid integer/float
                        diameter_value = float(seg_meta.diameter) if seg_meta.diameter else 110.0
                        diameter_field.value = diameter_value
                        print(f"[INT] Updated palette diameter to {diameter_value}mm")
                    
                    # NOTE: We do NOT set SegmentIndex.value directly - that's data-driven via SegmentIndicesList
                    # The combobox reads from ValueList which references SegmentIndicesList
                    # Only log the selection - don't touch the combobox value directly
                    print(f"[INT] Selected segment index: {actual_seg_idx}, Diameter={seg_meta.diameter}")
                except Exception as e:
                    print(f"[INT] Error updating palette: {e}")
                    import traceback
                    traceback.print_exc()
            
            self._draw_preview(current_pnt)
            return True
        
        # PRIORITY 2: Check for vertex dragging (before path dragging, but after midpoint)
        if hasattr(self.script_object, 'saved_paths') and self.script_object.saved_paths:
            # Check if clicking on a vertex (for dragging) - second priority
            min_dist = 40.0  # 40mm tolerance for vertex selection
            closest_vertex = None
            closest_vertex_dist = min_dist
            
            for path_idx, path in enumerate(self.script_object.saved_paths):
                for vertex_idx, vertex_pt in enumerate(path):
                    dx = current_pnt.X - vertex_pt.X
                    dy = current_pnt.Y - vertex_pt.Y
                    dz = current_pnt.Z - vertex_pt.Z
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < closest_vertex_dist:
                        closest_vertex_dist = dist
                        closest_vertex = (path_idx, vertex_idx, dist)
            
            if closest_vertex:
                path_idx, vertex_idx, dist = closest_vertex
                # Start dragging this vertex (rubberband effect)
                self.is_dragging = True
                self.drag_path_idx = path_idx
                self.drag_vertex_idx = vertex_idx
                self._drag_start_point = current_pnt
                button_val = getattr(mouse_msg, 'Button', None)
                self._last_button_state = button_val if button_val is not None else 1
                print(f"[INT] ✓ Started dragging vertex {vertex_idx} of path {path_idx} (dist={dist:.1f}mm)")
                self._update_status(f"Dragging: Path {path_idx}, Vertex {vertex_idx} - Release to finish")
                self._draw_preview(current_pnt)
                return True
        
        # PRIORITY 3: Check if clicking on a path segment (for dragging entire polyline)
        # Only if NOT clicking on midpoint or vertex
        if hasattr(self.script_object, 'saved_paths') and self.script_object.saved_paths:
            for path_idx, path in enumerate(self.script_object.saved_paths):
                if len(path) < 2:
                    continue
                for seg_idx in range(len(path) - 1):
                    p1, p2 = path[seg_idx], path[seg_idx + 1]
                    seg_vec = AllplanGeo.Vector3D(p2.X - p1.X, p2.Y - p1.Y, p2.Z - p1.Z)
                    pt_vec = AllplanGeo.Vector3D(current_pnt.X - p1.X, current_pnt.Y - p1.Y, current_pnt.Z - p1.Z)
                    seg_len_sq = seg_vec.X*seg_vec.X + seg_vec.Y*seg_vec.Y + seg_vec.Z*seg_vec.Z
                    if seg_len_sq < 1e-6:
                        continue
                    t = (pt_vec.X*seg_vec.X + pt_vec.Y*seg_vec.Y + pt_vec.Z*seg_vec.Z) / seg_len_sq
                    if 0 <= t <= 1:
                        closest_pt = AllplanGeo.Point3D(
                            p1.X + t * seg_vec.X,
                            p1.Y + t * seg_vec.Y,
                            p1.Z + t * seg_vec.Z
                        )
                        dx = current_pnt.X - closest_pt.X
                        dy = current_pnt.Y - closest_pt.Y
                        dz = current_pnt.Z - closest_pt.Z
                        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                        # Only drag if NOT near midpoint (midpoint has 30mm tolerance, use 25mm here to avoid conflicts)
                        if dist < 25.0 and not self.hover_mid:
                            # Start dragging entire path
                            self.is_dragging = True
                            self.drag_path_idx = path_idx
                            self.drag_vertex_idx = None
                            self._drag_start_point = current_pnt
                            self._drag_start_path = [AllplanGeo.Point3D(pt.X, pt.Y, pt.Z) for pt in path]
                            button_val = getattr(mouse_msg, 'Button', None)
                            self._last_button_state = button_val if button_val is not None else 1
                            print(f"[INT] ✓ Started dragging path {path_idx} (button={button_val})")
                            self._update_status(f"Dragging: Path {path_idx} - Release to finish")
                            self._draw_preview(current_pnt)
                            return True
        
        # PRIORITY 4: Check if clicking on a segment (not midpoint) - fallback selection
        if self.hover_seg:
            path_idx, seg_idx = self.hover_seg
            # Find the actual segment index in saved_segments by matching path_idx and seg_idx
            actual_seg_idx = None
            for saved_idx, saved_seg in enumerate(self.script_object.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(saved_seg)
                if seg_meta.custom.get("path_idx") == path_idx and seg_meta.custom.get("seg_idx") == seg_idx:
                    actual_seg_idx = saved_idx
                    break
            
            # Select this segment
            self.selected_seg = (path_idx, seg_idx)
            print(f"[INT] ✓ Selected segment: path {path_idx}, segment {seg_idx} (saved_segments index: {actual_seg_idx})")
            self._update_status(f"Selected: Path {path_idx}, Segment {seg_idx}")
            
            # Update palette with segment info (CRITICAL: Update diameter FIRST for user feedback)
            if actual_seg_idx is not None and 0 <= actual_seg_idx < len(self.script_object.saved_segments):
                seg_meta = SegmentMetadata.from_legacy(self.script_object.saved_segments[actual_seg_idx])
                try:
                    # Update diameter FIRST - this is what the user needs to see
                    # The diameter should be displayed in the "New Diameter (mm)" field (NewDiameter)
                    diameter_field = getattr(self.script_object.build_ele, "NewDiameter", None)
                    if diameter_field:
                        # Ensure diameter is a valid integer (IntegerComboBox requires int)
                        # Get the actual diameter from segment metadata
                        raw_diameter = seg_meta.diameter if seg_meta.diameter and seg_meta.diameter > 0 else 110.0
                        diameter_value = int(round(float(raw_diameter)))  # Convert to int for IntegerComboBox
                        
                        # CRITICAL: IntegerComboBox can only display values in its ValueList
                        # Check if value is in ValueList (40|110|160), if not, use closest valid value
                        # This ensures the dropdown shows the correct value
                        try:
                            # Try to set the value directly
                            diameter_field.value = diameter_value
                            # Force update by accessing the value (triggers UI refresh)
                            _ = diameter_field.value
                            print(f"[INT] Updated palette NewDiameter field to {diameter_value}mm for segment {actual_seg_idx} (from metadata: {raw_diameter}mm)")
                        except (ValueError, TypeError, RuntimeError) as e:
                            # If value is not in ValueList, use default
                            print(f"[INT] Warning: Diameter {diameter_value}mm not in ValueList, using 110mm instead: {e}")
                            diameter_field.value = 110
                    
                    # NOTE: We do NOT set SegmentIndex.value directly - that's data-driven via SegmentIndicesList
                    # The combobox reads from ValueList which references SegmentIndicesList
                    # Only log the selection - don't touch the combobox value directly
                    print(f"[INT] Selected segment index: {actual_seg_idx}, Diameter={seg_meta.diameter}mm")
                except Exception as e:
                    print(f"[INT] Error updating palette: {e}")
                    import traceback
                    traceback.print_exc()
            
            self._draw_preview(current_pnt)
            return True
        
        # No selection - clear selection
        self.selected_seg = None
        self.selected_free_entity = None
        self._draw_preview(current_pnt)
        return True

    def _update_status(self, message: str):
        """Update the Status field in palette."""
        try:
            status_field = getattr(self.script_object.build_ele, "FirstText", None)
            if status_field:
                status_field.value = message
        except Exception:
            pass

    def _update_section_info(self):
        """Update the Section Info field showing segment count and total length."""
        try:
            section_info = getattr(self.script_object.build_ele, "SectionInfo", None)
            if section_info:
                seg_count = len(self.script_object.saved_segments)
                
                # Calculate total length
                total_length = 0.0
                for seg_meta in self.script_object.saved_segments:
                    if seg_meta.points and len(seg_meta.points) >= 2:
                        p1, p2 = seg_meta.points[0], seg_meta.points[1]
                        dx = p2.X - p1.X
                        dy = p2.Y - p1.Y
                        dz = p2.Z - p1.Z
                        length = math.sqrt(dx*dx + dy*dy + dz*dz)
                        total_length += length
                
                section_info.value = f"Segments: {seg_count} | Total: {total_length:.0f}mm"
        except Exception:
            pass

    def _get_origin_offset(self) -> tuple:
        """Get the origin offset from palette (StartX, StartY, StartZ).
        
        Returns:
            Tuple of (origin_x, origin_y, origin_z) in millimeters
        """
        start_x = getattr(self.script_object.build_ele, "StartX", None)
        start_y = getattr(self.script_object.build_ele, "StartY", None)
        start_z = getattr(self.script_object.build_ele, "StartZ", None)
        
        origin_x = float(start_x.value) if start_x else 0.0
        origin_y = float(start_y.value) if start_y else 0.0
        origin_z = float(start_z.value) if start_z else 0.0
        
        return (origin_x, origin_y, origin_z)
    
    def _apply_origin_offset(self, pnt: Any) -> Any:
        """Apply origin offset to a point (subtract origin from point coordinates).
        
        Args:
            pnt: Raw point from Allplan (with world coordinates)
            
        Returns:
            New point with origin offset applied (relative coordinates)
        """
        origin_x, origin_y, origin_z = self._get_origin_offset()
        
        if ALLPLAN_AVAILABLE:
            return AllplanGeo.Point3D(
                pnt.X - origin_x,
                pnt.Y - origin_y,
                pnt.Z - origin_z
            )
        else:
            # Fallback for non-Allplan environments
            return pnt
    
    def _to_world_coordinates(self, pnt: Any) -> Any:
        """Convert relative coordinates back to world coordinates (add origin).
        
        Args:
            pnt: Point with relative coordinates (origin-subtracted)
            
        Returns:
            New point with world coordinates (origin added back)
        """
        origin_x, origin_y, origin_z = self._get_origin_offset()
        
        if ALLPLAN_AVAILABLE:
            return AllplanGeo.Point3D(
                pnt.X + origin_x,
                pnt.Y + origin_y,
                pnt.Z + origin_z
            )
        else:
            # Fallback for non-Allplan environments
            return pnt
    
    def _segment_to_world_coordinates(self, segment: SegmentMetadata) -> SegmentMetadata:
        """Convert a segment with relative coordinates to world coordinates.
        
        Args:
            segment: SegmentMetadata with relative coordinates
            
        Returns:
            New SegmentMetadata with world coordinates (for placing 3D models)
        """
        world_points = [self._to_world_coordinates(pt) for pt in segment.points]
        
        # Create new segment with world coordinates
        # Use getattr with defaults for optional attributes
        world_segment = SegmentMetadata(
            points=world_points,
            diameter=getattr(segment, 'diameter', 110.0),
            section_type=getattr(segment, 'section_type', '110mm'),
            system=getattr(segment, 'system', 'Pluvial'),
            label=getattr(segment, 'label', 'Segment'),
            layer=getattr(segment, 'layer', None),
            path_id=getattr(segment, 'path_id', None),
            segment_id=getattr(segment, 'segment_id', None),
            color_id=getattr(segment, 'color_id', None),
            point_roles=getattr(segment, 'point_roles', []).copy() if hasattr(segment, 'point_roles') else [],
            custom=segment.custom.copy() if hasattr(segment, 'custom') and segment.custom else {}
        )
        
        return world_segment
    
    def _auto_set_origin(self, pnt: Any, round_to_meter: bool = True):
        """Automatically set origin on first click or mouse move."""
        if self._origin_auto_set or pnt is None:
            return
        
        if not ALLPLAN_AVAILABLE:
            return
        
        if round_to_meter:
            origin_x = round(pnt.X / 1000.0) * 1000.0
            origin_y = round(pnt.Y / 1000.0) * 1000.0
            origin_z = round(pnt.Z / 1000.0) * 1000.0
        else:
            origin_x = pnt.X
            origin_y = pnt.Y
            origin_z = pnt.Z
        
        # Set origin to rounded position
        start_x = getattr(self.script_object.build_ele, "StartX", None)
        start_y = getattr(self.script_object.build_ele, "StartY", None) 
        start_z = getattr(self.script_object.build_ele, "StartZ", None)
        
        if start_x:
            start_x.value = origin_x
        if start_y:
            start_y.value = origin_y
        if start_z:
            start_z.value = origin_z
        
        self._origin_auto_set = True
        print(f"[INT] ✓ Origin auto-set to X={origin_x:.0f}, Y={origin_y:.0f}, Z={origin_z:.0f}")
        self._update_status("✓ Origin set automatically")

    def _update_coordinate_display(self, pnt: Any):
        """Update the coordinate display in the palette."""
        if not ALLPLAN_AVAILABLE or pnt is None:
            return
        
        try:
            # Get origin offset if set
            origin_x = getattr(self.script_object.build_ele, "StartX", None)
            origin_y = getattr(self.script_object.build_ele, "StartY", None)
            origin_z = getattr(self.script_object.build_ele, "StartZ", None)
            
            offset_x = float(origin_x.value) if origin_x else 0.0
            offset_y = float(origin_y.value) if origin_y else 0.0
            offset_z = float(origin_z.value) if origin_z else 0.0
            
            # Calculate relative coordinates
            rel_x = pnt.X - offset_x
            rel_y = pnt.Y - offset_y
            rel_z = pnt.Z - offset_z
            
            # Calculate distance and angle from last point (using relative coordinates)
            delta_info = ""
            if len(self.points) > 0:
                last = self.points[-1]  # Already in relative coords
                dx = rel_x - last.X
                dy = rel_y - last.Y
                dz = rel_z - last.Z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                angle = math.degrees(math.atan2(dy, dx))
                delta_info = f" | Δ: {dist:.0f}mm @ {angle:.0f}°"
            
            # Update palette text field (if it exists)
            coord_info = getattr(self.script_object.build_ele, "CoordInfo", None)
            if coord_info:
                coord_info.value = f"X: {rel_x:.0f}, Y: {rel_y:.0f}, Z: {rel_z:.0f}{delta_info}"
        except Exception as ex:
            # Log errors during coordinate update (at least the first one)
            if not hasattr(self, '_coord_error_logged'):
                print(f"[INT] Error updating coordinates: {ex}")
                self._coord_error_logged = True

    def _handle_left_click(self, current_pnt: Any, _raw_pnt: Any = None) -> bool:
        """Handle left click."""
        if self.capture_mode and self.capture_handler:
            return self.capture_handler.handle_point_click(current_pnt)

        if self.is_dragging:
            self.is_dragging = False
            self.drag_index = -1
            # Save state after drag completes
            self._save_state_snapshot()
            self._draw_preview(current_pnt)
            return True

        if self._is_create_like_mode():
            # Check if clicking on existing point to drag
            hover_idx = self._find_hover_index(current_pnt)
            if hover_idx != -1:
                # Save state before drag starts
                self._save_state_snapshot()
                self.is_dragging = True
                self.drag_index = hover_idx
                return True

            # Add new point - save state before adding
            self._save_state_snapshot()
            
            # CRITICAL: current_pnt is already in relative coordinates (from process_mouse_msg)
            # It has been: raw_pnt -> origin_offset -> angle_limiting
            new_point = current_pnt
            
            # CRITICAL: Handle Z coordinate based on drawing mode
            effective_mode = get_effective_drawing_mode(self.config)
            
            if effective_mode == DRAWING_MODE_2D:
                # 2D mode - force Z to 0 for all points (plan view)
                if ALLPLAN_AVAILABLE:
                    new_point = AllplanGeo.Point3D(new_point.X, new_point.Y, 0.0)
                else:
                    new_point.Z = 0.0
            elif effective_mode == DRAWING_MODE_3D_FREE:
                # 3D free mode - allow any Z value (for vertical polylines, diagonal segments)
                # No restrictions - user can draw vertical stacks, risers, etc.
                pass  # Use Z coordinate as-is
            elif effective_mode == DRAWING_MODE_3D_CONSTRAINED:
                # 3D constrained mode - allow Z but limit large jumps (prevent accidental jumps)
                if len(self.points) > 0:
                    last_z = self.points[-1].Z
                    z_change = abs(new_point.Z - last_z)
                    threshold = self.config.z_jump_threshold
                    # If Z change exceeds threshold, it's probably accidental - preserve previous Z
                    if z_change > threshold:
                        print(f"[INT] ⚠ Large Z jump detected ({z_change:.1f}mm > {threshold:.1f}mm), preserving previous Z: {last_z:.1f}")
                        if ALLPLAN_AVAILABLE:
                            new_point = AllplanGeo.Point3D(new_point.X, new_point.Y, last_z)
                        else:
                            new_point.Z = last_z
            
            # BIFURCATION SUPPORT: Check for nearby endpoints on EVERY click (not just first!)
            # This allows bifurcation at any point during drawing, not just at the start
            nearby_endpoint = self._find_nearby_endpoint(new_point, point_is_world=False)
            if nearby_endpoint is not None:
                # CRITICAL: Use EXACT endpoint coordinate (no rounding) to ensure perfect connection!
                # This ensures models created from this point will align perfectly with existing models
                if ALLPLAN_AVAILABLE:
                    rel_pt = self._apply_origin_offset(nearby_endpoint)
                    new_point = AllplanGeo.Point3D(
                        float(rel_pt.X),
                        float(rel_pt.Y),
                        float(rel_pt.Z)
                    )
                else:
                    new_point = nearby_endpoint
                if len(self.points) == 0:
                    print(f"[INT] ✓ BIFURCATION! Starting from existing endpoint: ({new_point.X:.3f}, {new_point.Y:.3f}, {new_point.Z:.3f})")
                    self._update_status("✓ Starting from existing endpoint (bifurcation)")
                else:
                    print(f"[INT] ✓ BIFURCATION! Snapped to endpoint during drawing: ({new_point.X:.3f}, {new_point.Y:.3f}, {new_point.Z:.3f})")
                    # Snap status update removed - too verbose
            
            # CRITICAL: Prevent duplicate points (causes loops/zero-length segments!)
            # Check if new point is too close to last point
            if len(self.points) > 0:
                last_pt = self.points[-1]
                dx = new_point.X - last_pt.X
                dy = new_point.Y - last_pt.Y
                dz = new_point.Z - last_pt.Z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist < 1.0:  # Less than 1mm = duplicate
                    print(f"[INT] ⚠ Duplicate point detected (distance: {dist:.2f}mm), ignoring")
                    self._update_status("⚠ Point too close to previous - ignored")
                    return True  # Ignore the click but don't add point
            
            self.points.append(new_point)
            print(f"[INT] Point added! Total points: {len(self.points)} - ({new_point.X:.1f}, {new_point.Y:.1f}, {new_point.Z:.1f})")
            
            # Update status
            if len(self.points) == 1:
                self._update_status("Place next point...")
            else:
                self._update_status(f"Drawing... {len(self.points)} points placed")
            
            # Update section info
            self._update_section_info()
            
            self._draw_preview(new_point)
            return True

        return False

    def _handle_right_click(self) -> bool:
        """Handle right click - save current polyline."""
        print(f"[INT] _handle_right_click: mode={self.mode}, points={len(self.points)}")
        if self._is_create_like_mode() and len(self.points) >= 2:
            print(f"[INT] Conditions met, calling save_current_polyline()")
            self.save_current_polyline()
            self._draw_preview(self.current_point or (AllplanGeo.Point3D() if ALLPLAN_AVAILABLE else None))
            return True
        else:
            print(f"[INT] Conditions NOT met - need create/extend mode and >=2 points")
        return False

    def _find_hover_index(self, pnt: Any) -> int:
        """Find index of point under cursor, or -1."""
        if not ALLPLAN_AVAILABLE or not self.points:
            return -1

        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        min_dist = max_d2
        result = -1

        for i, pt in enumerate(self.points):
            dx = pnt.X - pt.X
            dy = pnt.Y - pt.Y
            dz = pnt.Z - pt.Z
            d2 = dx*dx + dy*dy + dz*dz
            if d2 < min_dist:
                min_dist = d2
                result = i

        return result

    def _draw_preview(self, current_pnt: Any):
        """Draw preview - active polyline + saved paths + handles (matches Saneamiento exactly).
        
        Note: Preview rendering in multiple viewports is handled by Allplan's DrawElementPreview API.
        If preview artifacts appear in alternate viewports, this may be an Allplan viewport rendering
        limitation. The preview is drawn to the input view document and Allplan manages multi-viewport
        display automatically.
        """
        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            return

        try:
            if current_pnt is not None:
                self._last_preview_point = current_pnt
            # Build ONE list with ALL preview elements (Saneamiento pattern)
            elems: List[Any] = []
            
            # Properties for different visual elements
            base_prop = self.com_prop
            handle_prop = AllplanBaseElements.CommonProperties()
            handle_prop.Color = 2  # Yellow for handles
            
            saved_prop = AllplanBaseElements.CommonProperties()
            saved_prop.Color = 3  # Green for saved paths
            
            # BIFURCATION MARKERS: White circles at endpoints
            endpoint_prop = AllplanBaseElements.CommonProperties()
            endpoint_prop.Color = 7  # White for connection points
            
            # Draw saved paths (convert to world coordinates for preview)
            # CRITICAL: Filter out invalid paths (duplicates, loops, zero-length segments)
            for pts in self.script_object.saved_paths:
                if len(pts) >= 2:
                    # Remove duplicate consecutive points (prevents loops)
                    filtered_pts = []
                    for i, pt in enumerate(pts):
                        if i == 0:
                            filtered_pts.append(pt)
                        else:
                            prev_pt = filtered_pts[-1]
                            dx = pt.X - prev_pt.X
                            dy = pt.Y - prev_pt.Y
                            dz = pt.Z - prev_pt.Z
                            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                            if dist >= 1.0:  # Only add if distance >= 1mm
                                filtered_pts.append(pt)
                    
                    # Only draw if we have at least 2 distinct points
                    if len(filtered_pts) >= 2:
                        poly = AllplanGeo.Polyline3D()
                        for pt in filtered_pts:
                            world_pt = self._to_world_coordinates(pt)
                            poly += world_pt
                        elems.append(AllplanBasisElements.ModelElement3D(saved_prop, poly))

            # Draw persisted free-point entities (macros / defined elements).
            free_entities = self._get_saved_free_entities()
            for idx, entity in enumerate(free_entities):
                try:
                    built = self._build_free_entity_elements(entity)
                    if built:
                        elems.extend(built)
                except Exception:
                    pass

                # Selection/hover marker for free entities in edit mode
                if self._is_edit_mode() and isinstance(entity, dict):
                    pt = entity.get("point", None)
                    if pt is not None:
                        tool_name = str(entity.get("tool", "") or "").lower()
                        marker_prop = AllplanBaseElements.CommonProperties()
                        marker_prop.Color = 6 if idx == self.selected_free_entity else 2 if idx == self.hover_free_entity else 7
                        marker_prop.Pen = 2
                        marker_prop.Stroke = 2
                        try:
                            world_pt = self._to_world_coordinates(pt)
                            sphere = AllplanGeo.Polyhedron3D.CreateSphere(
                                AllplanGeo.Point3D(world_pt.X, world_pt.Y, world_pt.Z),
                                90.0 if idx == self.selected_free_entity else 70.0,
                            )
                            elems.append(AllplanBasisElements.ModelElement3D(marker_prop, sphere))
                        except Exception:
                            pass
                        # Extra visual cue for macro entities: draw a wireframe box
                        # so macros are easier to identify than circle/square/triangle markers.
                        if tool_name == "macro":
                            try:
                                box_size = 260.0 if idx == self.selected_free_entity else 220.0
                                half = box_size / 2.0
                                z0 = world_pt.Z - half
                                z1 = world_pt.Z + half
                                p000 = AllplanGeo.Point3D(world_pt.X - half, world_pt.Y - half, z0)
                                p100 = AllplanGeo.Point3D(world_pt.X + half, world_pt.Y - half, z0)
                                p110 = AllplanGeo.Point3D(world_pt.X + half, world_pt.Y + half, z0)
                                p010 = AllplanGeo.Point3D(world_pt.X - half, world_pt.Y + half, z0)
                                p001 = AllplanGeo.Point3D(world_pt.X - half, world_pt.Y - half, z1)
                                p101 = AllplanGeo.Point3D(world_pt.X + half, world_pt.Y - half, z1)
                                p111 = AllplanGeo.Point3D(world_pt.X + half, world_pt.Y + half, z1)
                                p011 = AllplanGeo.Point3D(world_pt.X - half, world_pt.Y + half, z1)

                                bottom = AllplanGeo.Polyline3D()
                                for p in (p000, p100, p110, p010, p000):
                                    bottom += p
                                elems.append(AllplanBasisElements.ModelElement3D(marker_prop, bottom))

                                top = AllplanGeo.Polyline3D()
                                for p in (p001, p101, p111, p011, p001):
                                    top += p
                                elems.append(AllplanBasisElements.ModelElement3D(marker_prop, top))

                                for a, b in ((p000, p001), (p100, p101), (p110, p111), (p010, p011)):
                                    edge = AllplanGeo.Polyline3D()
                                    edge += a
                                    edge += b
                                    elems.append(AllplanBasisElements.ModelElement3D(marker_prop, edge))
                            except Exception:
                                pass
            
            # Draw active polyline being created (with rubber-band to cursor)
            if self._is_create_like_mode() and len(self.points) >= 1:
                if current_pnt:
                    poly = AllplanGeo.Polyline3D()
                    for pt in self.points:
                        world_pt = self._to_world_coordinates(pt)
                        poly += world_pt
                    world_current = self._to_world_coordinates(current_pnt)
                    poly += world_current  # Rubber-band line
                    elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))
            
            # HANDLES AT ACTIVE POLYLINE VERTICES: Show handles at ALL points of polyline being drawn
            # These appear at every click/segment endpoint during drawing
            if self._is_create_like_mode() and len(self.points) > 0:
                vertex_handle_prop = AllplanBaseElements.CommonProperties()
                vertex_handle_prop.Color = 2  # Yellow for active polyline vertices
                vertex_handle_prop.Pen = 2
                vertex_handle_prop.Stroke = 2
                vertex_handle_size = self.bifurcation_snap_distance  # Match snap distance
                
                for pt in self.points:
                    try:
                        world_pt = self._to_world_coordinates(pt)
                        center = AllplanGeo.Point3D(world_pt.X, world_pt.Y, world_pt.Z)
                        try:
                            sphere = AllplanGeo.Polyhedron3D.CreateSphere(center, vertex_handle_size)
                            vertex_elem = AllplanBasisElements.ModelElement3D(vertex_handle_prop, sphere)
                            elems.append(vertex_elem)
                        except:
                            # Fallback to circle
                            circle_points = []
                            for i in range(33):
                                angle = i * 2 * math.pi / 32
                                x = world_pt.X + vertex_handle_size * math.cos(angle)
                                y = world_pt.Y + vertex_handle_size * math.sin(angle)
                                circle_points.append(AllplanGeo.Point3D(x, y, world_pt.Z))
                            if circle_points:
                                circle_poly = AllplanGeo.Polyline3D(circle_points)
                                vertex_elem = AllplanBasisElements.ModelElement3D(vertex_handle_prop, circle_poly)
                                elems.append(vertex_elem)
                    except:
                        pass
            
            # HANDLES AT SAVED POLYLINE VERTICES: Show handles at ALL vertices of saved polylines
            # These persist after saving and appear at every segment endpoint
            # CRITICAL: Show handles in BOTH create mode AND edit mode (when create_mode is False)
            # CRITICAL: Only show handles from currently existing saved_paths, not stale cache
            # This prevents handles persisting after Ctrl+Z undo
            # Show handles in both create and edit modes
            if True:  # Always show handles for saved polylines (both create and edit mode)
                handle_size = self.bifurcation_snap_distance  # Match snap distance
                
                # Create properties for saved polyline vertex handles
                saved_handle_prop = AllplanBaseElements.CommonProperties()
                saved_handle_prop.Color = 7  # White (bright, visible)
                saved_handle_prop.Pen = 2  # Medium thickness
                saved_handle_prop.Stroke = 2  # Medium stroke
                
                # Get ALL vertices from CURRENTLY EXISTING saved_paths (not stale cache)
                # This ensures handles disappear when paths are deleted via Ctrl+Z
                if hasattr(self.script_object, 'saved_paths') and self.script_object.saved_paths:
                    for path_idx, path in enumerate(self.script_object.saved_paths):
                        if path and len(path) >= 2:
                            # Draw handles at ALL vertices of this saved path
                            for vertex_idx, vertex_pt in enumerate(path):
                                try:
                                    world_vertex = self._to_world_coordinates(vertex_pt)
                                    center = AllplanGeo.Point3D(world_vertex.X, world_vertex.Y, world_vertex.Z)
                                    
                                    # Use different color for starting point (first vertex of each path)
                                    if vertex_idx == 0:
                                        # Starting point - use green color to distinguish from other vertices
                                        start_handle_prop = AllplanBaseElements.CommonProperties()
                                        start_handle_prop.Color = 3  # Green for starting point
                                        start_handle_prop.Pen = 2
                                        start_handle_prop.Stroke = 2
                                        handle_prop_to_use = start_handle_prop
                                    else:
                                        # Regular vertex - use white
                                        handle_prop_to_use = saved_handle_prop
                                    
                                    # Create handle sphere or circle
                                    try:
                                        sphere = AllplanGeo.Polyhedron3D.CreateSphere(center, handle_size)
                                        handle_elem = AllplanBasisElements.ModelElement3D(handle_prop_to_use, sphere)
                                        elems.append(handle_elem)
                                    except:
                                        # Fallback to 2D circle
                                        try:
                                            circle_points = []
                                            num_segments = 32
                                            for i in range(num_segments + 1):
                                                angle = i * 2 * math.pi / num_segments
                                                x = world_vertex.X + handle_size * math.cos(angle)
                                                y = world_vertex.Y + handle_size * math.sin(angle)
                                                circle_points.append(AllplanGeo.Point3D(x, y, world_vertex.Z))
                                            
                                            if circle_points:
                                                circle_polyline = AllplanGeo.Polyline3D(circle_points)
                                                handle_elem = AllplanBasisElements.ModelElement3D(handle_prop_to_use, circle_polyline)
                                                elems.append(handle_elem)
                                        except:
                                            pass
                                except:
                                    pass
            
            # HIGHLIGHT: Larger marker when hovering near snap zone (works during drawing too!)
            if self._is_create_like_mode() and current_pnt:
                # current_pnt is already in relative coords from _handle_mouse_move
                nearest = self._find_nearby_endpoint(current_pnt, point_is_world=False)
                if nearest is not None:
                    # Draw LARGER, RED sphere to show "SNAP HERE!" (convert to world for display)
                    highlight_prop = AllplanBaseElements.CommonProperties()
                    highlight_prop.Color = 5  # Red/magenta
                    highlight_prop.Pen = 2
                    highlight_prop.Stroke = 2
                    
                    try:
                        highlight_radius = self.bifurcation_snap_distance
                        center = AllplanGeo.Point3D(nearest.X, nearest.Y, nearest.Z)
                        
                        sphere = AllplanGeo.Polyhedron3D.CreateSphere(
                            center,
                            highlight_radius
                        )
                        
                        highlight_elem = AllplanBasisElements.ModelElement3D(highlight_prop, sphere)
                        elems.append(highlight_elem)
                    except:
                        pass  # Skip highlight if creation fails
            
            # EDIT MODE: Midpoint handles and segment highlighting (when create_mode is False)
            if self._is_edit_mode() and hasattr(self.script_object, 'saved_paths') and self.script_object.saved_paths:
                # Properties for edit mode visualization
                midpoint_prop = AllplanBaseElements.CommonProperties()
                midpoint_prop.Color = 5  # Red for midpoint handles
                midpoint_prop.Pen = 3
                midpoint_prop.Stroke = 3
                
                selected_midpoint_prop = AllplanBaseElements.CommonProperties()
                selected_midpoint_prop.Color = 1  # Blue for selected midpoint
                selected_midpoint_prop.Pen = 4
                selected_midpoint_prop.Stroke = 4
                
                selected_seg_prop = AllplanBaseElements.CommonProperties()
                selected_seg_prop.Color = 1  # Blue for selected segment
                selected_seg_prop.Pen = 4
                selected_seg_prop.Stroke = 4
                
                hover_seg_prop = AllplanBaseElements.CommonProperties()
                hover_seg_prop.Color = 4  # Cyan for hovered segment
                hover_seg_prop.Pen = 2
                hover_seg_prop.Stroke = 2
                
                # Draw midpoint handles (red boxes) at all segment midpoints
                for path_idx, path in enumerate(self.script_object.saved_paths):
                    if len(path) < 2:
                        continue
                    
                    for seg_idx in range(len(path) - 1):
                        p1, p2 = path[seg_idx], path[seg_idx + 1]
                        
                        # Calculate midpoint
                        mid_x = (p1.X + p2.X) / 2
                        mid_y = (p1.Y + p2.Y) / 2
                        mid_z = (p1.Z + p2.Z) / 2
                        mid_pt = AllplanGeo.Point3D(mid_x, mid_y, mid_z)
                        
                        # Convert to world coordinates
                        world_mid = self._to_world_coordinates(mid_pt)
                        center = AllplanGeo.Point3D(world_mid.X, world_mid.Y, world_mid.Z)
                        
                        # Check if this is the selected segment's midpoint
                        is_selected = (self.selected_seg and 
                                     self.selected_seg[0] == path_idx and 
                                     self.selected_seg[1] == seg_idx)
                        
                        # Use larger, blue box for selected segment, red box for others
                        box_size = 100.0 if is_selected else 80.0  # Larger for selected
                        current_midpoint_prop = selected_midpoint_prop if is_selected else midpoint_prop
                        
                        try:
                            # Create box using 4 points forming a rectangle
                            box_points = [
                                AllplanGeo.Point3D(world_mid.X - box_size, world_mid.Y - box_size, world_mid.Z),
                                AllplanGeo.Point3D(world_mid.X + box_size, world_mid.Y - box_size, world_mid.Z),
                                AllplanGeo.Point3D(world_mid.X + box_size, world_mid.Y + box_size, world_mid.Z),
                                AllplanGeo.Point3D(world_mid.X - box_size, world_mid.Y + box_size, world_mid.Z),
                                AllplanGeo.Point3D(world_mid.X - box_size, world_mid.Y - box_size, world_mid.Z)  # Close the box
                            ]
                            
                            box_poly = AllplanGeo.Polyline3D(box_points)
                            box_elem = AllplanBasisElements.ModelElement3D(current_midpoint_prop, box_poly)
                            elems.append(box_elem)
                        except:
                            # Fallback to circle if box fails
                            try:
                                circle_points = []
                                for i in range(33):
                                    angle = i * 2 * math.pi / 32
                                    x = world_mid.X + box_size * math.cos(angle)
                                    y = world_mid.Y + box_size * math.sin(angle)
                                    circle_points.append(AllplanGeo.Point3D(x, y, world_mid.Z))
                                if circle_points:
                                    circle_poly = AllplanGeo.Polyline3D(circle_points)
                                    box_elem = AllplanBasisElements.ModelElement3D(midpoint_prop, circle_poly)
                                    elems.append(box_elem)
                            except:
                                pass
                
                # Highlight selected segment
                if self.selected_seg:
                    path_idx, seg_idx = self.selected_seg
                    if 0 <= path_idx < len(self.script_object.saved_paths):
                        path = self.script_object.saved_paths[path_idx]
                        if 0 <= seg_idx < len(path) - 1:
                            p1, p2 = path[seg_idx], path[seg_idx + 1]
                            world_p1 = self._to_world_coordinates(p1)
                            world_p2 = self._to_world_coordinates(p2)
                            selected_seg_line = AllplanGeo.Polyline3D([world_p1, world_p2])
                            selected_elem = AllplanBasisElements.ModelElement3D(selected_seg_prop, selected_seg_line)
                            elems.append(selected_elem)
                
                # Highlight hovered segment
                if self.hover_seg and self.hover_seg != self.selected_seg:
                    path_idx, seg_idx = self.hover_seg
                    if 0 <= path_idx < len(self.script_object.saved_paths):
                        path = self.script_object.saved_paths[path_idx]
                        if 0 <= seg_idx < len(path) - 1:
                            p1, p2 = path[seg_idx], path[seg_idx + 1]
                            world_p1 = self._to_world_coordinates(p1)
                            world_p2 = self._to_world_coordinates(p2)
                            hover_seg_line = AllplanGeo.Polyline3D([world_p1, world_p2])
                            hover_elem = AllplanBasisElements.ModelElement3D(hover_seg_prop, hover_seg_line)
                            elems.append(hover_elem)
                
                # Highlight hovered vertex (for dragging feedback)
                hover_vertex_prop = AllplanBaseElements.CommonProperties()
                hover_vertex_prop.Color = 2  # Yellow for hovered vertex
                hover_vertex_prop.Pen = 3
                hover_vertex_prop.Stroke = 3
                
                if self.hover_vertex and not self.is_dragging:
                    path_idx, vertex_idx = self.hover_vertex
                    if 0 <= path_idx < len(self.script_object.saved_paths):
                        path = self.script_object.saved_paths[path_idx]
                        if 0 <= vertex_idx < len(path):
                            vertex_pt = path[vertex_idx]
                            world_vertex = self._to_world_coordinates(vertex_pt)
                            try:
                                # Draw larger yellow sphere for hovered vertex
                                hover_size = 150.0  # Larger than normal handles
                                center = AllplanGeo.Point3D(world_vertex.X, world_vertex.Y, world_vertex.Z)
                                sphere = AllplanGeo.Polyhedron3D.CreateSphere(center, hover_size)
                                hover_vertex_elem = AllplanBasisElements.ModelElement3D(hover_vertex_prop, sphere)
                                elems.append(hover_vertex_elem)
                            except:
                                pass
                
                # Highlight dragged vertex/path
                if self.is_dragging and self.drag_path_idx is not None:
                    drag_highlight_prop = AllplanBaseElements.CommonProperties()
                    drag_highlight_prop.Color = 2  # Yellow for dragged element
                    drag_highlight_prop.Pen = 5
                    drag_highlight_prop.Stroke = 5
                    
                    path_idx = self.drag_path_idx
                    if 0 <= path_idx < len(self.script_object.saved_paths):
                        path = self.script_object.saved_paths[path_idx]
                        if self.drag_vertex_idx is not None and 0 <= self.drag_vertex_idx < len(path):
                            # Highlight dragged vertex
                            vertex_pt = path[self.drag_vertex_idx]
                            world_vertex = self._to_world_coordinates(vertex_pt)
                            try:
                                drag_size = 200.0  # Even larger for active drag
                                center = AllplanGeo.Point3D(world_vertex.X, world_vertex.Y, world_vertex.Z)
                                sphere = AllplanGeo.Polyhedron3D.CreateSphere(center, drag_size)
                                drag_elem = AllplanBasisElements.ModelElement3D(drag_highlight_prop, sphere)
                                elems.append(drag_elem)
                            except:
                                pass
                        else:
                            # Highlight entire dragged path
                            if len(path) >= 2:
                                drag_path_pts = [self._to_world_coordinates(pt) for pt in path]
                                drag_path_poly = AllplanGeo.Polyline3D(drag_path_pts)
                                drag_path_elem = AllplanBasisElements.ModelElement3D(drag_highlight_prop, drag_path_poly)
                                elems.append(drag_path_elem)
            
            # Draw ALL elements at once with proper clearing (Saneamiento method)
            AllplanBaseElements.DrawElementPreview(
                self.coord_input.GetInputViewDocument(),
                AllplanGeo.Matrix3D(),
                elems,
                True,  # CRITICAL: Clear previous elements to prevent ghosting
                None
            )

        except Exception as ex:
            print(f"[INT] Error in _draw_preview: {ex}")

    def on_preview_draw(self):
        """Called when preview should be drawn."""
        if self.current_point:
            self._draw_preview(self.current_point)

    def on_mouse_leave(self) -> None:
        """Allplan callback when the cursor leaves the drawing viewport."""
        self.hover_index = -1
        self.drag_index = -1
        self.is_dragging = False
        self.insert_preview_p = None
        self.insert_target = None
        self.current_point = None
        
        # Clear edit mode dragging
        self.drag_path_idx = None
        self.drag_vertex_idx = None
        self._drag_start_point = None
        self._drag_start_path = None
        self.hover_seg = None
        self.hover_mid = None

        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            return
        try:
            if self._last_preview_point is not None:
                self._draw_preview(self._last_preview_point)
        except Exception:
            pass

    def on_cancel_function(self):
        """ESC key pressed - Create 3D models immediately, then let execute() create PythonPart blueprint."""
        print("\n" + "="*80)
        print("[INT] ESC KEY PRESSED - on_cancel_function() called!")
        print(f"[INT] Points in current polyline: {len(self.points)}")
        print(f"[INT] Saved paths: {len(self.script_object.saved_paths)}")
        print("="*80)

        # One-shot skip when cancel was triggered programmatically by finalize button (Event 1003).
        # In that flow, geometry has already been created/rebuilt and running cancel recreate again
        # causes visible ghost duplicates.
        if bool(getattr(self.script_object, "_skip_on_cancel_recreate_once", False)):
            self.script_object._skip_on_cancel_recreate_once = False
            print("[INT] Skip on_cancel recreate: finalize flow already handled geometry")
            if ALLPLAN_AVAILABLE:
                try:
                    from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult  # type: ignore
                    return OnCancelFunctionResult.CREATE_ELEMENTS
                except Exception:
                    pass
            return None
        
        try:
            if self.is_modification_mode or self._force_edit_mode:
                print("[INT] ESC during modification - restore saved state and recreate")
                try:
                    preserve_state = bool(getattr(self.script_object, "_preserve_saved_state", False))
                    if not preserve_state:
                        self._restore_saved_state()
                    else:
                        print("[INT] Modification finalize: keeping current persisted state")
                except Exception:
                    pass
                try:
                    create_group = False
                    build_ele = getattr(self.script_object, "build_ele", None)
                    create_group_prop = getattr(build_ele, "CreatePythonPartGroup", None) if build_ele else None
                    if create_group_prop is not None:
                        create_group = bool(getattr(create_group_prop, "value", create_group_prop))
                    if create_group:
                        elements = self.script_object._build_elements_for_creation()
                        group_elements = self.script_object._wrap_elements_in_pythonpartgroup(elements)
                        if group_elements and self.coord_input is not None:
                            doc = self.coord_input.GetInputViewDocument()
                            AllplanBaseElements.CreateElements(
                                doc,
                                AllplanGeo.Matrix3D(),
                                group_elements,
                                [],
                                None,
                            )
                            self.script_object._suppress_execute = True
                    else:
                        self._create_elements_immediately()
                except Exception:
                    pass
                if ALLPLAN_AVAILABLE:
                    try:
                        from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult  # type: ignore
                        return OnCancelFunctionResult.CREATE_ELEMENTS
                    except Exception:
                        pass
                return None

            # PointInput_SO alignment: capture mode - finalize all paths (export JSON + create polylines)
            if self.capture_mode and self.capture_handler:
                print("[INT] Capture mode: finalizing all paths (like PointInput_SO on ESC)")
                self.capture_handler.finalize_all_paths(reason="ESC")
                self.script_object._suppress_execute = True
                self._clear_preview()
                if ALLPLAN_AVAILABLE:
                    try:
                        from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult  # type: ignore
                        return OnCancelFunctionResult.CREATE_ELEMENTS
                    except Exception:
                        pass
                return None
            # Save current polyline if we have points
            if len(self.points) >= 2:
                print("[INT] Saving current polyline...")
                self.save_current_polyline()
                print(f"[INT] After save - Saved segments: {len(self.script_object.saved_segments)}")
                print(f"[INT] After save - Saved paths: {len(self.script_object.saved_paths)}")
            else:
                print("[INT] Not enough points to save (need >= 2)")

            # Persist state for re-entry (PythonPart modification)
            self._persist_state_to_build_ele()
            
            # Create 3D models immediately (separate from PythonPart) only if not using PythonPart groups
            create_group = False
            try:
                build_ele = getattr(self.script_object, "build_ele", None)
                create_group_prop = getattr(build_ele, "CreatePythonPartGroup", None) if build_ele else None
                if create_group_prop is not None:
                    create_group = bool(getattr(create_group_prop, "value", create_group_prop))
            except Exception:
                create_group = False

            if not create_group:
                print("[INT] Creating 3D models as separate geometry...")
                self._create_elements_immediately()
            
            # BIFURCATION SUPPORT: Endpoints are stored in _finalize_now() handler
            # (before saved_paths is cleared)
            
            # Update status and section info
            seg_count = len(self.script_object.saved_segments)
            self._update_status(f"✓ Created {seg_count} segments with 3D models")
            self._update_section_info()
            
            # Clear preview only (DON'T clear points/state - execute() needs the data!)
            print("[INT] Clearing preview...")
            self._clear_preview()
            # Note: Saved data is NOT cleared - execute() will use it to create the PythonPart blueprint
            
        except Exception as ex:
            print(f"[INT] ERROR in on_cancel_function: {ex}")
            import traceback
            traceback.print_exc()
        
        print("[INT] Returning CREATE_ELEMENTS - Allplan will call execute() next...")
        print("="*80 + "\n")
        
        # Return CREATE_ELEMENTS - Allplan will call execute() to create the editable PythonPart
        if ALLPLAN_AVAILABLE:
            try:
                from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult  # type: ignore
                print("[INT] Returning OnCancelFunctionResult.CREATE_ELEMENTS")
                return OnCancelFunctionResult.CREATE_ELEMENTS
            except Exception as ex:
                print(f"[INT] ERROR importing OnCancelFunctionResult: {ex}")
                import traceback
                traceback.print_exc()
        return None
    
    def _store_polyline_endpoints(self):
        """Store endpoints of finalized polylines for bifurcation support.
        
        CRITICAL: Stores in module-level _persistent_finalized_endpoints to survive ScriptObject recreation!
        Allplan creates a NEW ScriptObject instance for each session, so instance variables are lost.
        """
        try:
            global _persistent_finalized_endpoints
            
            for path in self.script_object.saved_paths:
                if len(path) >= 2:
                    # Store both start and end points
                    start_pt = self._to_world_coordinates(path[0])
                    end_pt = self._to_world_coordinates(path[-1])
                    
                    # Check if already stored (avoid duplicates)
                    def is_duplicate(pt, stored_pts, tolerance=1.0):
                        for stored_pt in stored_pts:
                            # Calculate distance manually (CalcLength doesn't work with two points)
                            dx = pt.X - stored_pt.X
                            dy = pt.Y - stored_pt.Y
                            dz = pt.Z - stored_pt.Z
                            dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                            if dist < tolerance:
                                return True
                        return False
                    
                    if not is_duplicate(start_pt, _persistent_finalized_endpoints):
                        _persistent_finalized_endpoints.append(start_pt)
                        print(f"[INT] Stored endpoint: ({start_pt.X:.1f}, {start_pt.Y:.1f}, {start_pt.Z:.1f})")
                    
                    if not is_duplicate(end_pt, _persistent_finalized_endpoints):
                        _persistent_finalized_endpoints.append(end_pt)
                        print(f"[INT] Stored endpoint: ({end_pt.X:.1f}, {end_pt.Y:.1f}, {end_pt.Z:.1f})")
            
            # CRITICAL: Save to file cache so endpoints survive module reloads!
            _save_endpoints_to_cache(_persistent_finalized_endpoints)
            
            print(f"[INT] Total stored endpoints for bifurcation: {len(_persistent_finalized_endpoints)}")
        except Exception as ex:
            print(f"[INT] Error storing endpoints: {ex}")

    def _store_endpoints_for_path(self, path: List[Any]) -> None:
        """Store endpoints for a single path (used immediately after save to show handles)."""
        if not path or len(path) < 2:
            return
        try:
            global _persistent_finalized_endpoints

            def is_duplicate(pt, stored_pts, tolerance=1.0):
                for stored_pt in stored_pts:
                    dx = pt.X - stored_pt.X
                    dy = pt.Y - stored_pt.Y
                    dz = pt.Z - stored_pt.Z
                    dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                    if dist < tolerance:
                        return True
                return False

            start_pt = self._to_world_coordinates(path[0])
            end_pt = self._to_world_coordinates(path[-1])

            added = 0
            if not is_duplicate(start_pt, _persistent_finalized_endpoints):
                _persistent_finalized_endpoints.append(start_pt)
                added += 1
            if not is_duplicate(end_pt, _persistent_finalized_endpoints):
                _persistent_finalized_endpoints.append(end_pt)
                added += 1

            if added > 0:
                _save_endpoints_to_cache(_persistent_finalized_endpoints)
                print(f"[INT] ✓ Stored {added} endpoint(s) immediately after save (total {len(_persistent_finalized_endpoints)})")
        except Exception as ex:
            print(f"[INT] Error storing endpoints for path: {ex}")
    
    def _find_nearby_endpoint(self, point, point_is_world: bool = False):
        """Check if point is near an existing endpoint for bifurcation.
        
        Args:
            point: Point3D to check
            
        Returns:
            Nearest endpoint if within snap distance, else None
        """
        # Use module-level persistent endpoints (survives ScriptObject recreation)
        if not _persistent_finalized_endpoints:
            return None
        
        try:
            if not point_is_world:
                point = self._to_world_coordinates(point)
            nearest_pt = None
            min_dist = self.bifurcation_snap_distance
            
            # Prefer endpoints from current saved paths (avoid snapping to unrelated cached endpoints)
            if hasattr(self.script_object, "saved_paths") and self.script_object.saved_paths:
                for path in self.script_object.saved_paths:
                    if not path or len(path) < 2:
                        continue
                    for endpoint in (path[0], path[-1]):
                        try:
                            world_ep = self._to_world_coordinates(endpoint)
                        except Exception:
                            world_ep = endpoint
                        dx = point.X - world_ep.X
                        dy = point.Y - world_ep.Y
                        dz = point.Z - world_ep.Z
                        dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            nearest_pt = world_ep
                if nearest_pt is not None:
                    return nearest_pt

            for endpoint in _persistent_finalized_endpoints:
                # Calculate distance manually
                dx = point.X - endpoint.X
                dy = point.Y - endpoint.Y
                dz = point.Z - endpoint.Z
                dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                
                if dist < min_dist:
                    min_dist = dist
                    nearest_pt = endpoint
            
            if nearest_pt:
                # Snap logging removed - too verbose
                return nearest_pt
        except Exception as ex:
            print(f"[INT] Error finding nearby endpoint: {ex}")
        
        return None
    
    def _create_elements_immediately(self):
        """Create elements immediately using AllplanBaseElements.CreateElements()."""
        if not ALLPLAN_AVAILABLE or self.coord_input is None:
            print("[INT] Cannot create elements - Allplan not available or no coord_input")
            return
        
        try:
            saved_segments = self.script_object.saved_segments
            saved_paths = self.script_object.saved_paths
            
            if not saved_segments and not saved_paths:
                print("[INT] No segments or paths to create")
                return
            
            elements = []
            com_prop = AllplanBaseElements.CommonProperties()
            com_prop.GetGlobalProperties()
            
            # Create from segments (with hook support)
            element_creation_hook = getattr(self.script_object, "element_creation_hook", None)
            print(f"[INT] Processing {len(saved_segments)} segments...")
            
            for seg_idx, seg_info in enumerate(saved_segments):
                # Handle both dict-style and SegmentMetadata objects
                if isinstance(seg_info, dict):
                    points = seg_info.get('points', [])
                    seg_meta = SegmentMetadata.from_legacy(seg_info)
                else:
                    # Already a SegmentMetadata object
                    points = seg_info.points if hasattr(seg_info, 'points') else []
                    seg_meta = seg_info

                if len(points) >= 2:
                    segment_prop = AllplanBaseElements.CommonProperties()
                    segment_prop.GetGlobalProperties()
                    
                    # Try hook first - Convert segment to world coordinates!
                    if element_creation_hook is not None:
                        try:
                            # Convert from relative to world coordinates for 3D model placement
                            world_seg_meta = self._segment_to_world_coordinates(seg_meta)
                            hook_elements = element_creation_hook(world_seg_meta, segment_prop)
                            if hook_elements:
                                print(f"[INT]   Segment {seg_idx}: Hook returned {len(hook_elements)} elements")
                                elements.extend(hook_elements)
                                continue
                        except Exception as ex:
                            print(f"[INT]   Segment {seg_idx}: Hook failed: {ex}")
                            import traceback
                            traceback.print_exc()
                    
                    # Default: create line (also convert to world!)
                    print(f"[INT]   Segment {seg_idx}: Creating default line")
                    world_seg = self._segment_to_world_coordinates(seg_meta)
                    pts = world_seg.points
                    line = AllplanGeo.Line3D(pts[0], pts[1])
                    elements.append(AllplanBasisElements.ModelElement3D(segment_prop, line))
            
            # Create from paths (fallback) - Convert to world coordinates!
            for path_idx, pts in enumerate(saved_paths):
                if len(pts) >= 2:
                    poly = AllplanGeo.Polyline3D()
                    for pt in pts:
                        world_pt = self._to_world_coordinates(pt)
                        poly += world_pt
                    elements.append(AllplanBasisElements.ModelElement3D(com_prop, poly))
            
            print(f"[INT] Total elements to create: {len(elements)}")
            
            # CREATE IMMEDIATELY (Saneamiento method)
            AllplanBaseElements.CreateElements(
                self.coord_input.GetInputViewDocument(),
                AllplanGeo.Matrix3D(),
                elements,
                [],
                None
            )
            print(f"[INT] ✓ Created {len(elements)} elements in document!")
            
            # DON'T clear data - execute() needs it for PythonPart blueprint creation
            # self.script_object.saved_segments.clear()
            # self.script_object.saved_paths.clear()
            print("[INT] Data preserved for execute()")
            
        except Exception as ex:
            print(f"[INT] ERROR creating elements: {ex}")
            import traceback
            traceback.print_exc()


# ===== Public API Functions =====

def create_script_object(build_ele, script_object_data):
    """Create a PolylineScriptObject instance.

    This is the entry point that Allplan calls.
    """
    return PolylineScriptObject(build_ele, script_object_data)


def create_polyline_script_object(build_ele, script_object_data):
    """Factory that returns an instance of PolylineScriptObject.

    Use this when an installation wants to drive the ScriptObject
    but coordinate result retrieval via this library.
    """
    return PolylineScriptObject(build_ele, script_object_data)


def extract_result_from_script_object(script_object) -> PolylineResult:
    """Extract a PolylineResult from a script object instance.

    Reads stored paths from the object in a non-invasive way.
    Returns empty result if no data present.
    """
    points: List[Point3D] = []
    try:
        saved_paths = getattr(script_object, "saved_paths", [])
        if saved_paths:
            # Flatten first path into points list for a simple result
            for p in saved_paths[0]:
                if ALLPLAN_AVAILABLE:
                    x = float(getattr(p, "X", getattr(p, "x", 0.0)))
                    y = float(getattr(p, "Y", getattr(p, "y", 0.0)))
                    z = float(getattr(p, "Z", getattr(p, "z", 0.0)))
                else:
                    x, y, z = p if isinstance(p, (tuple, list)) and len(p) >= 3 else (0.0, 0.0, 0.0)
                points.append((x, y, z))
    except Exception:
        points = []

    return PolylineResult(points=points, is_closed=False)


def apply_config_to_script_object(script_object, config: PolylineBaseConfig) -> None:
    """Apply runtime behavior configuration to the script object and its interactor.

    Note: Geometry constants (HANDLE_SIZE, HIT_TOL_VERTEX, etc.) should be set
    directly on the module by installation scripts before creating the ScriptObject.
    This function only applies runtime behavior flags.

    Safe to call before or after `start_input`.
    """
    # Store config in script object
    if hasattr(script_object, 'set_config'):
        script_object.set_config(config)

    # Apply to interactor if it exists
    interactor = getattr(script_object, "script_object_interactor", None)
    if interactor is not None:
        interactor.config = config
        interactor.insert_mode = bool(config.allow_insert_point_mode)

        # Enable Z coordinate if supported
        try:
            if hasattr(interactor, "coord_input") and hasattr(interactor.coord_input, "SetEnableZCoordinate"):
                z_enabled = should_enable_z_coordinate(config)
                interactor.coord_input.SetEnableZCoordinate(z_enabled)
        except Exception:
            pass


def initialize_script_object(build_ele, script_object_data, config: Optional[PolylineBaseConfig] = None):
    """Create the script object and apply configuration.

    Returns the initialized script object. Allplan will set coord_input and call start_input().
    This function does not run the interaction loopÔÇöAllplan drives that.
    """
    print("[LIBRARY] initialize_script_object() called")
    so = create_polyline_script_object(build_ele, script_object_data)
    print(f"[LIBRARY] Script object created: {type(so)}")

    if config is not None:
        apply_config_to_script_object(so, config)
        print("[LIBRARY] Configuration applied")

    # DON'T call start_input() here - Allplan will call it after setting coord_input
    print("[LIBRARY] Returning script object (Allplan will call start_input later)")
    return so


def save_and_get_result(script_object, clear_state: bool = False) -> PolylineResult:
    """Ask the interactor to save the current polyline and return the result.

    Does not create elements in the document. Optionally clears the stored
    paths/segments afterwards.
    """
    try:
        interactor = getattr(script_object, "script_object_interactor", None)
        if interactor is not None and hasattr(interactor, "save_current_polyline"):
            interactor.save_current_polyline()
    except Exception:
        pass

    result = extract_result_from_script_object(script_object)

    if clear_state:
        try:
            if hasattr(script_object, "saved_paths"):
                script_object.saved_paths.clear()
            if hasattr(script_object, "saved_segments"):
                script_object.saved_segments.clear()
        except Exception:
            pass

    return result


# ===== Pure interactor mode =====
class PureInteractorSession:
    """Holds the result of a pure interactor session.

    The `result` is set when the user accepts (Finalize button/event).
    """

    def __init__(self) -> None:
        self.result: Optional[PolylineResult] = None

    def _on_accept(self, so) -> None:
        self.result = extract_result_from_script_object(so)


def enable_pure_interactor_mode(script_object, session: Optional[PureInteractorSession] = None) -> PureInteractorSession:
    """Modify the ScriptObject to not create elements and to report result.

    - Overrides `_finalize_and_create_now` to capture the polyline and cancel
      the input without creating model elements.
    - Makes `execute` return an empty result to avoid creation via execute.
    Returns the `PureInteractorSession` that will hold the result when accepted.
    """

    CreateElementResult = None
    try:
        if ALLPLAN_AVAILABLE:
            CreateElementResult = getattr(__import__("CreateElementResult"), "CreateElementResult")  # type: ignore
    except Exception:
        pass

    if session is None:
        session = PureInteractorSession()

    # Patch methods on the instance only
    orig_finalize = getattr(script_object, "_finalize_and_create_now", None)
    orig_execute = getattr(script_object, "execute", None)

    def _finalize_and_capture() -> None:
        try:
            intr = getattr(script_object, "script_object_interactor", None)
            if intr is not None and hasattr(intr, "save_current_polyline"):
                intr.save_current_polyline()
        except Exception:
            pass
        # Capture and store in session
        session._on_accept(script_object)
        # Clear state to end session
        try:
            if hasattr(script_object, "saved_paths"):
                script_object.saved_paths.clear()
            if hasattr(script_object, "saved_segments"):
                script_object.saved_segments.clear()
        except Exception:
            pass

    def _execute_noop():
        if CreateElementResult is not None:
            try:
                return CreateElementResult([])
            except Exception:
                return []
        return []

    # Bind the instance-level overrides
    setattr(script_object, "_finalize_and_create_now", _finalize_and_capture)
    setattr(script_object, "execute", _execute_noop)

    # Keep originals for potential restoration
    setattr(script_object, "_orig_finalize_and_create_now", orig_finalize)
    setattr(script_object, "_orig_execute", orig_execute)

    return session


# ===== Transactional finalize mode =====
def enable_transactional_finalize(script_object) -> None:
    """Enable transactional finalize - elements created via execute() for editability.
    
    This is the CORRECT pattern for editable PythonParts:
    1. on_cancel_function() returns OnCancelFunctionResult.CREATE_ELEMENTS
    2. Allplan calls execute()
    3. execute() returns CreateElementResult([elements])
    4. Allplan creates an editable PythonPart that can be double-clicked and modified
    """
    print("[LIBRARY] Transactional mode enabled - execute() will create editable PythonParts")
    # This function is now just for API compatibility - the flow is built into on_cancel_function + execute


def restore_original_finalize(script_object) -> None:
    """Restore the original finalize method if it was patched."""
    orig = getattr(script_object, "_orig_finalize_and_create_now_tx", None)
    if orig is not None:
        setattr(script_object, "_finalize_and_create_now", orig)


# ===== Utility Helper Functions =====
def get_segment_length(segment: SegmentMetadata) -> float:
    """Calculate segment length using Allplan geometry.
    
    Args:
        segment: SegmentMetadata object
        
    Returns:
        Length in mm, or 0.0 if segment is invalid
    """
    if len(segment.points) < 2:
        return 0.0
    
    try:
        p0 = segment.points[0]
        p1 = segment.points[1]
        
        # Convert to tuples if needed
        if ALLPLAN_AVAILABLE and hasattr(p0, 'X'):
            p0 = (p0.X, p0.Y, p0.Z)
        if ALLPLAN_AVAILABLE and hasattr(p1, 'X'):
            p1 = (p1.X, p1.Y, p1.Z)
        
        # Calculate Euclidean distance
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dz = p1[2] - p0[2]
        
        return math.sqrt(dx * dx + dy * dy + dz * dz)
        
    except Exception:
        return 0.0


def get_segment_direction_vector(segment: SegmentMetadata) -> Tuple[float, float, float]:
    """Get normalized direction vector for a segment.
    
    Args:
        segment: SegmentMetadata object
        
    Returns:
        Normalized direction vector (dx, dy, dz), or (0, 0, 0) if invalid
    """
    if len(segment.points) < 2:
        return (0.0, 0.0, 0.0)
    
    try:
        p0 = segment.points[0]
        p1 = segment.points[1]
        
        # Convert to tuples if needed
        if ALLPLAN_AVAILABLE and hasattr(p0, 'X'):
            p0 = (p0.X, p0.Y, p0.Z)
        if ALLPLAN_AVAILABLE and hasattr(p1, 'X'):
            p1 = (p1.X, p1.Y, p1.Z)
        
        # Calculate direction vector
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dz = p1[2] - p0[2]
        
        # Normalize
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-9:
            return (0.0, 0.0, 0.0)
        
        return (dx / length, dy / length, dz / length)
        
    except Exception:
        return (0.0, 0.0, 0.0)


def find_closest_point_on_segment(segment: SegmentMetadata, query_point: Point3D) -> Point3D:
    """Find closest point on segment to query point.
    
    Follows Allplan CalcOrthogonalProjection pattern for projecting points onto lines.
    
    Args:
        segment: SegmentMetadata object
        query_point: Query point (x, y, z) tuple or AllplanGeo.Point3D
        
    Returns:
        Closest point on segment (x, y, z) tuple
    """
    if len(segment.points) < 2:
        return (0.0, 0.0, 0.0)
    
    try:
        p0 = segment.points[0]
        p1 = segment.points[1]
        
        # Convert to tuples if needed
        if ALLPLAN_AVAILABLE and hasattr(p0, 'X'):
            p0 = (p0.X, p0.Y, p0.Z)
        if ALLPLAN_AVAILABLE and hasattr(p1, 'X'):
            p1 = (p1.X, p1.Y, p1.Z)
        if ALLPLAN_AVAILABLE and hasattr(query_point, 'X'):
            query_point = (query_point.X, query_point.Y, query_point.Z)
        
        # Vector from p0 to p1
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dz = p1[2] - p0[2]
        
        # Segment length squared
        seg_len_sq = dx * dx + dy * dy + dz * dz
        
        if seg_len_sq < 1e-9:
            # Degenerate segment, return p0
            return p0
        
        # Vector from p0 to query_point
        px = query_point[0] - p0[0]
        py = query_point[1] - p0[1]
        pz = query_point[2] - p0[2]
        
        # Project query_point onto segment (parameter t in [0, 1])
        t = max(0.0, min(1.0, (px * dx + py * dy + pz * dz) / seg_len_sq))
        
        # Closest point on segment
        closest_x = p0[0] + t * dx
        closest_y = p0[1] + t * dy
        closest_z = p0[2] + t * dz
        
        return (closest_x, closest_y, closest_z)
        
    except Exception:
        return (0.0, 0.0, 0.0)


# ===== Convenience API =====
class PolylineBaseInteractor:
    """Convenience wrapper for simpler API usage."""

    def __init__(self, config: Optional[PolylineBaseConfig] = None) -> None:
        self.config: PolylineBaseConfig = config or PolylineBaseConfig()

    def run(self) -> PolylineResult:
        """Run polyline interaction and return result.

        Note: In Allplan, this sets up the object but user must complete interaction.
        Returns empty result if called outside Allplan or before completion.
        """
        try:
            so = initialize_script_object(None, None, self.config)
        except Exception:
            return PolylineResult(points=[], is_closed=False)

        try:
            session = enable_pure_interactor_mode(so)
        except Exception:
            session = None

        if session is not None and session.result is not None:
            return session.result

        try:
            return extract_result_from_script_object(so)
        except Exception:
            return PolylineResult(points=[], is_closed=False)


def run_polyline_interaction(config: Optional[PolylineBaseConfig] = None) -> PolylineResult:
    """Convenience function for callers that prefer a function API."""
    interactor = PolylineBaseInteractor(config)
    return interactor.run()


# ===== Custom Interactor (for simple use cases) =====
try:
    from BaseScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor  # type: ignore
except Exception:
    class BaseScriptObjectInteractor:  # type: ignore
        def start_input(self, coord_input):
            raise NotImplementedError
        def process_mouse_msg(self, mouse_msg, pnt, msg_info):
            raise NotImplementedError
        def on_preview_draw(self):
            pass


class CustomPolylineInteractor(BaseScriptObjectInteractor):
    """Minimal custom interactor for simple polyline collection."""

    def __init__(self, config: Optional[PolylineBaseConfig] = None, on_accept: Optional[callable] = None) -> None:
        self.config: PolylineBaseConfig = config or PolylineBaseConfig()
        self.coord_input = None
        self.points_3d: List[Point3D] = []
        self._on_accept = on_accept

    def start_input(self, coord_input):
        self.coord_input = coord_input
        try:
            if hasattr(self.coord_input, "SetEnableZCoordinate"):
                z_enabled = should_enable_z_coordinate(self.config)
                self.coord_input.SetEnableZCoordinate(z_enabled)
        except Exception:
            pass

    def process_mouse_msg(self, mouse_msg, pnt, msg_info) -> bool:
        if not ALLPLAN_AVAILABLE:
            return False

        try:
            if mouse_msg == AllplanIFW.MouseMessage.kMouseLeftButtonDown:
                z_val = 0.0
                try:
                    if self.coord_input is not None:
                        cur = self.coord_input.GetCurrentPoint(pnt)
                        if cur is not None:
                            pt3 = cur.GetPoint()
                            z_val = float(getattr(pt3, "Z", 0.0))
                except Exception:
                    z_val = 0.0

                self.points_3d.append((float(pnt.X), float(pnt.Y), float(z_val)))
                return True

            if mouse_msg == AllplanIFW.MouseMessage.kMouseRightButtonDown:
                if callable(self._on_accept):
                    self._on_accept(self.points_3d)
                return True
        except Exception:
            return False
        return False

    def on_preview_draw(self):
        if not ALLPLAN_AVAILABLE or self.coord_input is None or len(self.points_3d) < 2:
            return

        try:
            poly = AllplanGeo.Polyline3D()
            for x, y, z in self.points_3d:
                poly += AllplanGeo.Point3D(x, y, z)

            com_prop = AllplanBaseElements.CommonProperties()
            com_prop.GetGlobalProperties()

            elem = AllplanBasisElements.ModelElement3D(com_prop, poly)
            add_prev = getattr(self.coord_input, "AddPreviewElement", None)
            add_prev_callable: Optional[Callable[[Any], None]] = add_prev if callable(add_prev) else None
            if add_prev_callable is not None:
                add_prev_callable(elem)
        except Exception:
            pass

    def on_mouse_leave(self) -> None:
        """Allplan callback when cursor leaves the viewport."""
        # This interactor only tracks discrete clicks, so we simply ignore the event.
        return None


def attach_custom_interactor_to_script_object(script_object, config: Optional[PolylineBaseConfig] = None,
                                              session: Optional[PureInteractorSession] = None) -> PureInteractorSession:
    """Attach the custom interactor to a given ScriptObject and start input.

    Returns the session container that will receive the result upon acceptance.
    """

    if session is None:
        session = PureInteractorSession()

    def _on_accept(points: List[Point3D]) -> None:
        if hasattr(script_object, "saved_paths"):
            try:
                if ALLPLAN_AVAILABLE:
                    so_pts = [AllplanGeo.Point3D(x, y, z) for x, y, z in points]
                else:
                    so_pts = points
                script_object.saved_paths = [so_pts]
            except Exception:
                pass

        session.result = PolylineResult(points=list(points), is_closed=False)

        try:
            for meth_name in ("CancelFunction", "OnCancelFunction", "CancelInput", "Cancel"):
                meth = getattr(getattr(script_object, "coord_input", None), meth_name, None)
                if callable(meth):
                    meth()
                    break
        except Exception:
            pass

    interactor = CustomPolylineInteractor(config=config, on_accept=_on_accept)
    script_object.script_object_interactor = interactor

    try:
        if getattr(script_object, "coord_input", None) is not None:
            interactor.start_input(script_object.coord_input)
    except Exception:
        pass

    return session


# ===== JSON Loading from PointInput_SO =====

def _get_desktop_dir() -> str:
    """Get the desktop directory path."""
    try:
        up = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        d = os.path.join(up, "Desktop")
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        return os.path.expanduser("~")


def find_latest_route_groups_json() -> Optional[str]:
    """Find the most recently modified route_groups JSON file on the desktop.
    
    Returns the path to the most recent file, or None if no files found.
    """
    try:
        desktop = _get_desktop_dir()
        pattern = os.path.join(desktop, "route_groups_*.json")
        files = glob.glob(pattern)
        if not files:
            return None
        
        # Sort by modification time, most recent first
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]
    except Exception:
        return None


def find_route_groups_json_by_path_id(path_id: int) -> Optional[str]:
    """Find a route_groups JSON file containing a specific path_id.
    
    Args:
        path_id: The path_id to search for
        
    Returns:
        Path to the JSON file containing the path_id, or None if not found.
    """
    try:
        desktop = _get_desktop_dir()
        pattern = os.path.join(desktop, "route_groups_*.json")
        files = glob.glob(pattern)
        
        for file_path in sorted(files, key=os.path.getmtime, reverse=True):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and entry.get("path_id") == path_id:
                            return file_path
            except Exception:
                continue
        return None
    except Exception:
        return None


def load_points_from_json(json_path: Optional[str] = None, path_id: Optional[int] = None) -> List[Point3D]:
    """Load points from a PointInput_SO JSON file.
    
    Args:
        json_path: Path to the JSON file. If None, searches for the latest route_groups JSON.
        path_id: If specified, only loads points from this path_id. If None, loads from the first path.
        
    Returns:
        List of (x, y, z) tuples representing the points in order:
        iniciales -> intermedios -> finales
        
    Example JSON structure:
        [
            {
                "path_id": 1,
                "iniciales": [{"x": 100.0, "y": 200.0, "z": 0.0, ...}, ...],
                "intermedios": [{"x": 150.0, "y": 250.0, "z": 0.0, ...}, ...],
                "finales": [{"x": 200.0, "y": 300.0, "z": 0.0, ...}, ...]
            }
        ]
    """
    points: List[Point3D] = []
    
    try:
        # Determine JSON file path
        if json_path is None:
            if path_id is not None:
                json_path = find_route_groups_json_by_path_id(path_id)
            else:
                json_path = find_latest_route_groups_json()
        
        if json_path is None or not os.path.exists(json_path):
            return points
        
        # Load JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list) or len(data) == 0:
            return points
        
        # Find the appropriate path entry
        target_entry = None
        if path_id is not None:
            for entry in data:
                if isinstance(entry, dict) and entry.get("path_id") == path_id:
                    target_entry = entry
                    break
        else:
            # Use first entry if no path_id specified
            target_entry = data[0] if isinstance(data[0], dict) else None
        
        if target_entry is None:
            return points
        
        # Extract points in order: initial -> intermediate -> final
        for category in ["iniciales", "intermedios", "finales"]:
            category_points = target_entry.get(category, [])
            if isinstance(category_points, list):
                for pt in category_points:
                    if isinstance(pt, dict):
                        x = float(pt.get("x", 0.0))
                        y = float(pt.get("y", 0.0))
                        z = float(pt.get("z", 0.0))
                        points.append((x, y, z))
        
    except Exception as e:
        print(f"[polyline_base_lib] Error loading JSON: {e}")
    
    return points


def load_points_from_json_by_segments(json_path: Optional[str] = None, path_id: Optional[int] = None) -> Dict[int, List[Point3D]]:
    """Load points from JSON organized by segment_id.
    
    Args:
        json_path: Path to the JSON file. If None, searches for the latest route_groups JSON.
        path_id: If specified, only loads points from this path_id. If None, loads from the first path.
        
    Returns:
        Dictionary mapping segment_id to list of (x, y, z) points for that segment.
    """
    segments: Dict[int, List[Point3D]] = {}
    
    try:
        # Determine JSON file path
        if json_path is None:
            if path_id is not None:
                json_path = find_route_groups_json_by_path_id(path_id)
            else:
                json_path = find_latest_route_groups_json()
        
        if json_path is None or not os.path.exists(json_path):
            return segments
        
        # Load JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list) or len(data) == 0:
            return segments
        
        # Find the appropriate path entry
        target_entry = None
        if path_id is not None:
            for entry in data:
                if isinstance(entry, dict) and entry.get("path_id") == path_id:
                    target_entry = entry
                    break
        else:
            target_entry = data[0] if isinstance(data[0], dict) else None
        
        if target_entry is None:
            return segments
        
        # Extract points organized by segment
        for category in ["iniciales", "intermedios", "finales"]:
            category_points = target_entry.get(category, [])
            if isinstance(category_points, list):
                for pt in category_points:
                    if isinstance(pt, dict):
                        seg_id = int(pt.get("segmento", 1))
                        x = float(pt.get("x", 0.0))
                        y = float(pt.get("y", 0.0))
                        z = float(pt.get("z", 0.0))
                        
                        if seg_id not in segments:
                            segments[seg_id] = []
                        segments[seg_id].append((x, y, z))
        
        # Sort points within each segment by category order
        # (initial points first, then intermediate, then final)
        for seg_id in segments:
            # Reorder points to maintain initial -> intermediate -> final order
            ordered_points: List[Point3D] = []
            
            for category in ["iniciales", "intermedios", "finales"]:
                category_points = target_entry.get(category, [])
                if isinstance(category_points, list):
                    for pt in category_points:
                        if isinstance(pt, dict) and int(pt.get("segmento", 1)) == seg_id:
                            x = float(pt.get("x", 0.0))
                            y = float(pt.get("y", 0.0))
                            z = float(pt.get("z", 0.0))
                            ordered_points.append((x, y, z))
            
            if ordered_points:
                segments[seg_id] = ordered_points
        
    except Exception as e:
        print(f"[polyline_base_lib] Error loading JSON by segments: {e}")
    
    return segments


def initialize_script_object_from_json(
    build_ele,
    script_object_data,
    json_path: Optional[str] = None,
    path_id: Optional[int] = None,
    config: Optional[PolylineBaseConfig] = None
) -> PolylineScriptObject:
    """Create and initialize a ScriptObject with points loaded from a PointInput_SO JSON file.
    
    Args:
        build_ele: Building element from Allplan
        script_object_data: Script object data from Allplan
        json_path: Path to JSON file. If None, searches for latest route_groups JSON.
        path_id: If specified, only loads points from this path_id.
        config: Optional configuration for the script object.
        
    Returns:
        Initialized ScriptObject with points pre-loaded into saved_paths.
        
    Example:
        from Clima.models_lib.py import polyline_base_lib
        
        so = polyline_base_lib.initialize_script_object_from_json(
            build_ele,
            script_object_data,
            path_id=1,  # Load points from path_id 1
            config=PolylineBaseConfig(enable_z_coordinate=True)
        )
    """
    so = create_polyline_script_object(build_ele, script_object_data)
    
    # Load points from JSON
    points = load_points_from_json(json_path=json_path, path_id=path_id)
    
    if points:
        # Convert to Allplan Point3D objects
        if ALLPLAN_AVAILABLE:
            so.saved_paths = [[AllplanGeo.Point3D(x, y, z) for x, y, z in points]]
        else:
            so.saved_paths = [points]
        
        # Create default segments for the loaded path
        # Generate segments based on loaded points
        if len(points) >= 2:
            # Use module-level constants (configurable by installation scripts)
            system_initial = DEFAULT_SEGMENT_SYSTEM[0] if DEFAULT_SEGMENT_SYSTEM else DEFAULT_SYSTEM_INITIAL
            for seg_idx in range(len(points) - 1):
                metadata = SegmentMetadata(
                    points=[
                        so.saved_paths[0][seg_idx],
                        so.saved_paths[0][seg_idx + 1],
                    ],
                    diameter=DEFAULT_SEGMENT_DIAMETER,
                    section_type=DEFAULT_SEGMENT_SECTION_TYPE,
                    system=DEFAULT_SEGMENT_SYSTEM,
                    label=f"{DEFAULT_SEGMENT_LABEL_PREFIX} {system_initial}",
                )
                so.saved_segments.append(metadata)
    
    # Apply configuration
    if config is not None:
        apply_config_to_script_object(so, config)
    
    return so


def load_json_path_ids(json_path: Optional[str] = None) -> List[int]:
    """Get list of path_ids available in a JSON file.
    
    Args:
        json_path: Path to JSON file. If None, searches for latest route_groups JSON.
        
    Returns:
        List of path_id values found in the JSON file.
    """
    path_ids: List[int] = []
    
    try:
        if json_path is None:
            json_path = find_latest_route_groups_json()
        
        if json_path is None or not os.path.exists(json_path):
            return path_ids
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    pid = entry.get("path_id")
                    if pid is not None:
                        try:
                            path_ids.append(int(pid))
                        except Exception:
                            pass
        
        path_ids.sort()
    except Exception as e:
        print(f"[polyline_base_lib] Error loading path_ids: {e}")
    
    return path_ids


def ensure_route_groups_json_path(json_path: Optional[str] = None) -> Optional[str]:
    """Ensure a writable route_groups JSON path exists.
    
    Args:
        json_path: Custom path or None to use Desktop
    
    Returns:
        Valid writable path or None if cannot create
    """
    try:
        if json_path:
            # Validate custom path
            directory = os.path.dirname(json_path)
            if directory and not os.path.exists(directory):
                print(f"[polyline_base_lib] Warning: Directory does not exist: {directory}")
                # Try to create it
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    print(f"[polyline_base_lib] Error creating directory: {e}")
                    return None
            if directory and not os.access(directory, os.W_OK):
                print(f"[polyline_base_lib] Warning: No write permission: {directory}")
                return None
            return json_path
        else:
            # Use Desktop (existing logic)
            existing = find_latest_route_groups_json()
            if existing:
                return existing
            
            desktop = _get_desktop_dir()
            if not os.access(desktop, os.W_OK):
                print(f"[polyline_base_lib] Warning: Desktop not writable: {desktop}")
                return None
            
            filename = f"route_groups_{int(time.time())}.json"
            return os.path.join(desktop, filename)
    except Exception as e:
        print(f"[polyline_base_lib] Error in ensure_route_groups_json_path: {e}")
        return None


def export_capture_records_to_json(
    captures: List[CapturePoint],
    path_id: int,
    json_path: Optional[str] = None,
) -> Optional[str]:
    """Persist capture records to the PointInput_SO JSON format.

    Args:
        captures: List of CapturePoint instances (can include exported ones).
        path_id: Path identifier to export.
        json_path: Optional explicit path. If None, uses most recent or creates a new desktop file.

    Returns:
        The JSON path written, or None if nothing was exported.
    """
    pending = [c for c in captures if c.path_id == path_id and not c.exported]
    if not pending:
        return None

    events = {"iniciales": [], "intermedios": [], "finales": []}
    for record in pending:
        payload = record.to_json_dict()
        if record.role == CAPTURE_ROLE_INICIAL:
            events["iniciales"].append(payload)
        elif record.role == CAPTURE_ROLE_FINAL:
            events["finales"].append(payload)
        else:
            events["intermedios"].append(payload)

    json_target = ensure_route_groups_json_path(json_path)
    if not json_target:
        return None

    data: List[Dict[str, Any]]
    try:
        if os.path.exists(json_target):
            with open(json_target, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        else:
            data = []
    except Exception:
        data = []

    index: Dict[int, Dict[str, Any]] = {}
    for entry in data:
        try:
            pid = int(entry.get("path_id"))
        except Exception:
            continue
        index[pid] = entry

    target_entry = index.get(path_id, {"path_id": path_id, "iniciales": [], "intermedios": [], "finales": []})
    for key in ("iniciales", "intermedios", "finales"):
        existing_points = target_entry.get(key) or []
        target_entry[key] = list(existing_points) + events[key]

    index[path_id] = target_entry

    out_list = [index[k] for k in sorted(index.keys())]
    try:
        with open(json_target, "w", encoding="utf-8") as f:
            json.dump(out_list, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"[polyline_base_lib] Error writing capture JSON: {exc}")
        return None

    # Mark exported captures
    for record in pending:
        record.exported = True

    return json_target


# ===== Module exports =====
# Export constants so installation scripts can modify them
__all__ = [
    # Constants (can be modified by installation scripts)
    "HANDLE_SIZE",
    "HIT_TOL_VERTEX",
    "HIT_TOL_SEGMENT",
    "HOVER_SCALE",
    "DRAG_SCALE",
    "MAX_PERP_DIST_MM",
    "SEGMENT_OVERLAY_Z_BIAS",
    "SEGMENT_OVERLAY_PEN",
    "INSERT_PREVIEW_COLOR",
    "MIN_INSERT_OFFSET_MM",
    "MIN_SEG_LEN_MM",
    "HANDLE_COLOR_IDX",
    "PREVIEW_SAVED_COLOR",
    "SEGMENT_HOVER_COLOR",
    "SEGMENT_SEL_COLOR",
    "BRANCH_ANCHOR_COLOR",
    "RECT_COLOR",
    "BOX_SELECTED_SEG_COLOR",
    "SELECTED_VERTEX_COLOR",
    "MIDPOINT_COLOR",
    "MIDPOINT_SIZE_FACTOR",
    "MIDPOINT_PEN",
    "MIDPOINT_Z_BIAS",
    "MIDPOINT_HIT_TOL",
    "RECT_PEN",
    # Default segment properties (can be modified by installation scripts)
    "DEFAULT_SEGMENT_DIAMETER",
    "DEFAULT_SEGMENT_SECTION_TYPE",
    "DEFAULT_SEGMENT_SYSTEM",
    "DEFAULT_SEGMENT_LABEL_PREFIX",
    "DEFAULT_SYSTEM_INITIAL",
    # User interface constants
    "DEFAULT_USER_PROMPT",
    "ANGLE_SNAP_VALUES",
    # Palette property names (configurable)
    "PALETTE_PROP_MODE",
    "PALETTE_PROP_CREATE_MODE",
    "PALETTE_PROP_INSERT_MODE",
    "PALETTE_PROP_LIMIT_ANGLES",
    "PALETTE_PROP_FIRST_TEXT",
    "PALETTE_PROP_SYSTEM",
    "PALETTE_PROP_DIAMETER",
    "PALETTE_PROP_DIAMETER_CUSTOM",
    "PALETTE_PROP_INSTALLATION_HORIZONTAL",
    "PALETTE_PROP_INSTALLATION_VERTICAL",
    "PALETTE_PROP_FACE_EN",
    "PALETTE_PROP_PATH_ID",
    "PALETTE_PROP_SEGMENT_ID",
    "PALETTE_PROP_POINT_ROLE",
    "PALETTE_PROP_FINISH_NOW",
    "PALETTE_PROP_ENABLE_ASSIST",
    "PALETTE_PROP_ENABLE_Z",
    "PALETTE_PROP_ENABLE_UNDO",
    "PALETTE_PROP_SET_PROJ_BASE",
    "PALETTE_PROP_CREATE_SYMBOL",
    # Fusion/extension constants
    "FUSION_TOLERANCE_MM",
    "EXTENSION_TOLERANCE_MM",
    # Capture role identifiers
    "CAPTURE_ROLE_INICIAL",
    "CAPTURE_ROLE_PASO",
    "CAPTURE_ROLE_BIFURCACION",
    "CAPTURE_ROLE_FINAL",
    "CAPTURE_ROLE_LABELS",
    # Interaction modes
    "MODE_CREATE",
    "MODE_EDIT",
    "MODE_EXTEND",
    # Classes and types
    "SegmentMetadata",
    "CapturePoint",
    "FreePointToolConfig",
    "PointInputCaptureHandler",
    "PolylineBaseConfig",
    "PolylineResult",
    "PolylineBaseInteractor",
    "PolylineScriptObject",
    "PolylineInteractor",
    "PureInteractorSession",
    "CustomPolylineInteractor",
    # Functions
    "run_polyline_interaction",
    "create_script_object",
    "create_polyline_script_object",
    "extract_result_from_script_object",
    "apply_config_to_script_object",
    "initialize_script_object",
    "save_and_get_result",
    "enable_pure_interactor_mode",
    "attach_custom_interactor_to_script_object",
    "enable_transactional_finalize",
    "restore_original_finalize",
    # JSON loading functions
    "find_latest_route_groups_json",
    "find_route_groups_json_by_path_id",
    "load_points_from_json",
    "load_points_from_json_by_segments",
    "initialize_script_object_from_json",
    "load_json_path_ids",
    "ensure_route_groups_json_path",
    "export_capture_records_to_json",
    # Utility helper functions
    "get_segment_length",
    "get_segment_direction_vector",
    "find_closest_point_on_segment",
    # Path utilities
    "get_library_root",
    "get_model_builders_dir",
    "validate_model_builder_exists",
    "ensure_models_in_path",
]

__version__ = "0.3.0"