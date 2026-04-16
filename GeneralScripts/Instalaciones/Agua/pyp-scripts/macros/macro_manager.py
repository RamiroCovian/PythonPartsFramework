# -*- coding: utf-8 -*-
"""
AguaMacroManager — Agua-specific subclass of MarkerManager.

Overrides palette-reading methods, element geometry creation, cursor preview,
and room/local selection for the Agua installation.

All generic lifecycle logic (events, mouse, preview, serialization, PP injection)
is handled by the base MarkerManager in PolyLib.
"""
from __future__ import annotations

import importlib.util
import math
import pathlib
import sys
from typing import Any, Dict, List, Optional, Tuple

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as PythonUtility

from Instalaciones.PolyLib.marker_manager import MarkerManager
from FileNameService import FileNameService

from ScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _room_story_locales_filter(element) -> bool:
    """Filtro callable para SelectionQuery: acepta solo Room, Story, Locales."""
    try:
        dname = (getattr(element, "GetDisplayName", lambda: "")() or "").strip().lower()
        return dname in ("story", "room", "locales", "local")
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  AGUA MACRO MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class AguaMacroManager(MarkerManager):
    """Agua-specific overrides for macro/element marker management.

    Reads palette parameters specific to the Agua installation
    (MacroSmartSymbolPath, DefinedElementType, etc.) and creates element
    geometry via the installed PythonPart registry or file-based fallback.
    """

    # macro_manager.py lives at: pyp-scripts/macros/macro_manager.py
    # parent.parent resolves to the pyp-scripts/ folder
    _PYP_SCRIPTS_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    def __init__(self, script_object: Any, build_ele: Any) -> None:
        super().__init__(script_object, build_ele)
        # Room/local selection extra state
        self.post_element_selection_room: Any = None
        self.pending_room_selection_result: bool = False
        # Cache of raw (untransformed) model elements per element_type key
        # Avoids re-instantiating the PythonPart class on every mouse move
        self._element_template_cache: Dict[str, List[Any]] = {}

    # ═══════════════════════════════════════════════════════════════════════
    #  OVERRIDE: Palette parameter reading
    # ═══════════════════════════════════════════════════════════════════════

    def get_macro_settings_from_palette(self) -> Optional[dict]:
        """Read macro configuration from Agua palette parameters."""
        # Read marker point mode (start/end/free)
        mode = 0
        try:
            mode = int(
                getattr(getattr(self.build_ele, "MarkerPointMode", None), "value", 0) or 0
            )
        except Exception:
            mode = 0

        kind = "start" if mode == 0 else ("end" if mode == 1 else "free")

        # Read library type and paths
        lib_type = str(
            getattr(getattr(self.build_ele, "MacroLibraryElementType", None), "value", "") or "SmartSymbol"
        )
        smart_path = str(
            getattr(getattr(self.build_ele, "MacroSmartSymbolPath", None), "value", "") or ""
        ).strip()
        fixture_path = str(
            getattr(getattr(self.build_ele, "MacroFixturePath", None), "value", "") or ""
        ).strip()

        # Read local Z selection
        selected_z = -999999.0
        try:
            selected_z = float(
                getattr(getattr(self.build_ele, "MacroSelectedLocalZ", None), "value", -999999) or -999999
            )
        except Exception:
            selected_z = -999999.0

        if selected_z > -100000.0:
            # Local seleccionado: z_abs = z_base_local + altura sobre piso
            z_relative = 0.0
            try:
                z_relative = float(
                    getattr(getattr(self.build_ele, "MacroZRelative", None), "value", 0) or 0.0
                )
            except Exception:
                z_relative = 0.0
            z_abs = selected_z + z_relative
            self.current_floor_z = selected_z
            self.current_floor_index = 0
            auto_detect = True
        else:
            # Sin local: usar cota Z manual
            z_abs = 0.0
            try:
                z_abs = float(
                    getattr(getattr(self.build_ele, "MacroZAbs", None), "value", 0) or 0.0
                )
            except Exception:
                z_abs = 0.0
            z_relative = z_abs
            self.current_floor_z = z_abs
            self.current_floor_index = -1
            auto_detect = False

        return {
            "kind": kind,
            "lib_type": lib_type,
            "smart_path": smart_path,
            "fixture_path": fixture_path,
            "z_abs": z_abs,
            "z_relative": z_relative,
            "floor_index": self.current_floor_index,
            "floor_z": self.current_floor_z,
            "auto_detect": auto_detect,
        }

    def get_element_settings_from_palette(self) -> Tuple[str, float]:
        """Read element type key and radius from Agua palette."""
        element_label = str(
            getattr(getattr(self.build_ele, "DefinedElementType", None), "value", "") or "Circulo"
        ).strip()

        # Resolve element_type key from installed modules on the script_object
        element_type = "circle"
        try:
            pythonparts_modules = getattr(self.script_object, "pythonparts_modules", [])
            for item in pythonparts_modules or []:
                item_label = str(getattr(item, "label", "") or "").strip()
                if item_label == element_label:
                    element_type = str(getattr(item, "key", "") or "").strip() or "circle"
                    break
        except Exception as ex:
            print(f"[AGUA_MGR] Error resolving element type from modules: {ex}")
            element_type = "circle"

        if element_type == "circle":
            print(f"[AGUA_MGR] WARNING: Could not resolve element '{element_label}' from pythonparts_modules. "
                  f"Available labels: {[getattr(m, 'label', '?') for m in getattr(self.script_object, 'pythonparts_modules', [])]}")

        radius = 50.0
        try:
            radius = float(
                getattr(getattr(self.build_ele, "ElementRadius", None), "value", 50) or 50.0
            )
        except Exception:
            radius = 50.0
        if radius <= 0.0:
            radius = 50.0
        return element_type, radius

    def get_element_z_abs(self) -> float:
        """Read absolute Z coordinate for defined elements from Agua palette."""
        try:
            return float(
                getattr(getattr(self.build_ele, "ElementZAbs", None), "value", 0) or 0.0
            )
        except Exception:
            return 0.0

    def get_element_rotation(self) -> Tuple[float, float, float]:
        """Read rotation angles from Agua palette."""
        def _get_angle(name: str, fallback: str = "") -> float:
            try:
                param = getattr(self.build_ele, name, None)
                if param is None and fallback:
                    param = getattr(self.build_ele, fallback, None)
                if param is None:
                    return 0.0
                raw = getattr(param, "value", param)
                return float(raw or 0.0)
            except Exception:
                return 0.0

        return (
            _get_angle("ElementRotX", "RotX"),
            _get_angle("ElementRotY", "RotY"),
            _get_angle("ElementRotZ", "RotZ"),
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  OVERRIDE: Room/local selection
    # ═══════════════════════════════════════════════════════════════════════

    def _handle_room_selection(self) -> bool:
        """Start room/local selection for relative Z (EventId 1026)."""
        try:
            sel_query = BaseScriptObjectInteractor.create_selection_query(
                _room_story_locales_filter
            )
            if sel_query is not None:
                select_setting = AllplanIFW.ElementSelectFilterSetting(sel_query, True)
            else:
                select_setting = AllplanIFW.ElementSelectFilterSetting(True)
            self.post_element_selection_room = AllplanIFW.PostElementSelection()
            AllplanIFW.InputFunctionStarter.StartElementSelect(
                text="Seleccione un elemento Local, Story o Locales",
                post_element_selection=self.post_element_selection_room,
                element_select_filter_setting=select_setting,
                markSelectedElements=True,
            )
            self.pending_room_selection_result = True
            print("[ROOM] Seleccion de local iniciada (InputFunctionStarter)")
        except Exception as ex:
            print(f"[ROOM] Error iniciando seleccion: {ex}")
            self.pending_room_selection_result = False
            self.post_element_selection_room = None
        return True

    def _clear_room_selection(self) -> bool:
        """Clear room/local selection (EventId 1027)."""
        try:
            if hasattr(self.build_ele, "MacroSelectedLocalZ"):
                self.build_ele.MacroSelectedLocalZ.value = -999999.0
        except Exception:
            pass
        self._set_prompt("Click: agregar punto | ESC: terminar")
        print("[ROOM] Local quitado")
        self._try_save_state()
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  OVERRIDE: Element geometry creation
    # ═══════════════════════════════════════════════════════════════════════

    def create_element_geometry(self, marker: dict) -> List[Any]:
        """Create 3D geometry for a defined element marker.

        Uses script_object._get_pythonpart_installed() or file-based fallback
        to get element template, then applies centering, rotation, and translation.
        """
        pos = self._resolve_element_marker_pos(marker)
        if pos is None:
            print(f"[AGUA_MGR] create_element_geometry: pos is None for marker")
            return []

        element_type = str(marker.get("element_type", "circle") or "circle")
        print(f"[AGUA_MGR] create_element_geometry: type={element_type}, pos=({pos.X:.1f}, {pos.Y:.1f}, {pos.Z:.1f})")

        if element_type == "circle":
            # Simple circle fallback
            radius = float(marker.get("radius", 50.0) or 50.0)
            if radius <= 0.0:
                radius = 50.0
            try:
                prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                prop.Color = 6
                prop.ColorByLayer = False
                circle = self._make_circle_polyline(pos, radius, 48)
                return [AllplanBasisElements.ModelElement3D(prop, circle)]
            except Exception:
                return []

        result = self._get_and_transform_element_template(element_type, pos, marker, prop_override=None)
        print(f"[AGUA_MGR] create_element_geometry: got {len(result)} model elements")
        return result

    def get_cursor_preview_geo(self, cursor_pos: AllplanGeo.Point3D) -> List[Any]:
        """Return transformed 3D geometry at cursor pos for element preview."""
        try:
            element_type, _ = self.get_element_settings_from_palette()
            if not element_type or element_type == "circle":
                return []
            return self._get_and_transform_element_template(
                element_type, cursor_pos, {}, prop_override=None
            )
        except Exception:
            return []

    def get_macro_cursor_preview_geo(self, cursor_pos: AllplanGeo.Point3D) -> List[Any]:
        """Return the actual library macro as preview geometry at cursor position.

        Mirrors the approach from LibraryDialogs.py: build a LibraryElement
        directly with a placement matrix instead of drawing a generic marker.
        """
        try:
            settings = self.get_macro_settings_from_palette()
            if not settings:
                return []

            lib_type = str(settings.get("lib_type", "SmartSymbol") or "SmartSymbol")
            z_abs = float(settings.get("z_abs", cursor_pos.Z) or cursor_pos.Z)
            placement_point = AllplanGeo.Point3D(cursor_pos.X, cursor_pos.Y, z_abs)
            placement_mat = AllplanGeo.Matrix3D()
            placement_mat.SetTranslation(AllplanGeo.Vector3D(placement_point))

            if lib_type == "SmartSymbol":
                smart_path = str(settings.get("smart_path", "") or "").strip()
                if not smart_path:
                    return []
                smart_path = FileNameService.get_global_standard_path(smart_path) or smart_path
                lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
                    smart_path,
                    AllplanBasisElements.LibraryElementType.eSmartSymbol,
                    placement_mat,
                )
                return [AllplanBasisElements.LibraryElement(lib_ele_prop)]

            if lib_type == "Fixture":
                fixture_path = str(settings.get("fixture_path", "") or "").strip()
                if not fixture_path:
                    return []
                fixture_path = FileNameService.get_global_standard_path(fixture_path) or fixture_path
                lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
                    "", "", "",
                    fixture_path,
                    AllplanBasisElements.LibraryElementType.eFixtureSingleFile,
                    placement_mat,
                )
                try:
                    if fixture_path.lower().endswith(".lfx"):
                        pnt_list = [AllplanGeo.Point3D(), AllplanGeo.Point3D(1000, 0, 0)]
                        lib_ele_prop.SetPolyline(AllplanGeo.Polyline3D(pnt_list))
                except Exception:
                    pass
                return [AllplanBasisElements.LibraryElement(lib_ele_prop)]
        except Exception as ex:
            print(f"[AGUA_MGR] get_macro_cursor_preview_geo error: {ex}")

        return []

    # ═══════════════════════════════════════════════════════════════════════
    #  OVERRIDE: Element PythonPart injection (uses interactor.pythonpart)
    # ═══════════════════════════════════════════════════════════════════════

    def append_element_pythonparts(self, pythonpart_group_list: list, build_ele: Any) -> None:
        """Convert element markers to PythonParts using script_object.create_individual_pythonpart."""
        if not self.element_markers:
            print("[AGUA_MGR] append_element_pythonparts: no element_markers, skipping")
            return

        print(f"[AGUA_MGR] append_element_pythonparts: {len(self.element_markers)} markers")

        marker_groups = self._create_defined_element_model_elements_grouped()
        if not marker_groups:
            print("[AGUA_MGR] append_element_pythonparts: marker_groups is empty!")
            return

        print(f"[AGUA_MGR] marker_groups count={len(marker_groups)}, "
              f"non-empty={sum(1 for g in marker_groups if g)}")

        try:
            so = self.script_object
            for i, group in enumerate(marker_groups):
                if not group:
                    print(f"[AGUA_MGR]   group[{i}] is empty, skipping")
                    continue
                print(f"[AGUA_MGR]   group[{i}] has {len(group)} model elements")
                try:
                    pps = so.create_individual_pythonpart(
                        elements_list=group,
                        build_ele=build_ele,
                    )
                    pythonpart_group_list.extend(pps)
                    print(f"[AGUA_MGR]   group[{i}] -> {len(pps)} PythonParts created")
                except Exception as ex:
                    print(f"[AGUA_MGR]   group[{i}] create_individual_pythonpart error: {ex}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[AGUA_MGR] Error appending element PythonParts: {e}")
            import traceback
            traceback.print_exc()

    # ═══════════════════════════════════════════════════════════════════════
    #  TEMPLATE LOADING AND TRANSFORMATION
    # ═══════════════════════════════════════════════════════════════════════

    def _get_raw_element_template(self, element_type: str) -> List[Any]:
        """Get raw (untransformed) element geometry, using cache to avoid
        re-instantiating the PythonPart class on every call.
        """
        if element_type in self._element_template_cache:
            return self._element_template_cache[element_type]

        model_elems: List[Any] = []

        # --- Path 1: registry-based ---
        get_installed = getattr(self.script_object, "_get_pythonpart_installed", None)
        if get_installed is not None:
            try:
                model_elems = get_installed(element_key=element_type) or []
            except Exception:
                model_elems = []

        # --- Path 2: file-based fallback ---
        if not model_elems:
            model_elems = self._get_model_elems_from_module(element_type)

        # Cache the result (even empty list to avoid retrying)
        self._element_template_cache[element_type] = model_elems
        return model_elems

    def _get_and_transform_element_template(
        self,
        element_type: str,
        pos: AllplanGeo.Point3D,
        marker_data: dict,
        prop_override: Any = None,
    ) -> List[Any]:
        """Get installed element template, rotate and translate to position.

        Uses cached raw geometry to avoid re-instantiating the PythonPart
        class on every mouse move.
        """
        model_elems = self._get_raw_element_template(element_type)

        if not model_elems:
            return []

        # Compute bounding box center to re-center geometry on the click point
        center_offset = self._compute_center_offset(model_elems)

        # Get rotation
        try:
            rot_x = float(marker_data.get("rot_x", 0.0) or 0.0)
            rot_y = float(marker_data.get("rot_y", 0.0) or 0.0)
            rot_z = float(marker_data.get("rot_z", 0.0) or 0.0)
        except Exception:
            rot_x, rot_y, rot_z = (0.0, 0.0, 0.0)

        # Build transformation: center -> rotate -> translate to click pos
        mat = AllplanGeo.Matrix3D()
        mat.Translate(center_offset)
        if rot_x != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(1, 0, 0)),
                math.radians(rot_x),
            )
        if rot_y != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 1, 0)),
                math.radians(rot_y),
            )
        if rot_z != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 0, 1)),
                math.radians(rot_z),
            )
        mat.Translate(AllplanGeo.Vector3D(pos))

        out: List[Any] = []
        for elem in model_elems:
            try:
                geo = elem.GetGeometryObject()
                moved = AllplanGeo.Transform(geo, mat)
                prop = prop_override if prop_override is not None else elem.GetCommonProperties()
                out.append(AllplanBasisElements.ModelElement3D(prop, moved))
            except Exception:
                continue
        return out

    @staticmethod
    def _compute_center_offset(model_elems: List[Any]) -> AllplanGeo.Vector3D:
        """Compute bounding box center offset to re-center geometry at origin."""
        try:
            all_min_x, all_min_y, all_min_z = float('inf'), float('inf'), float('inf')
            all_max_x, all_max_y, all_max_z = float('-inf'), float('-inf'), float('-inf')
            bbox_ok = False
            for elem in model_elems:
                try:
                    geo = elem.GetGeometryObject()
                    result = AllplanGeo.CalcMinMax(geo)
                    if len(result) == 2:
                        err, bbox = result
                        if not err and hasattr(bbox, 'Min'):
                            all_min_x = min(all_min_x, bbox.Min.X)
                            all_min_y = min(all_min_y, bbox.Min.Y)
                            all_min_z = min(all_min_z, bbox.Min.Z)
                            all_max_x = max(all_max_x, bbox.Max.X)
                            all_max_y = max(all_max_y, bbox.Max.Y)
                            all_max_z = max(all_max_z, bbox.Max.Z)
                            bbox_ok = True
                    elif len(result) == 3:
                        ok, min_pt, max_pt = result
                        if ok:
                            all_min_x = min(all_min_x, min_pt.X)
                            all_min_y = min(all_min_y, min_pt.Y)
                            all_min_z = min(all_min_z, min_pt.Z)
                            all_max_x = max(all_max_x, max_pt.X)
                            all_max_y = max(all_max_y, max_pt.Y)
                            all_max_z = max(all_max_z, max_pt.Z)
                            bbox_ok = True
                except Exception:
                    pass

            if bbox_ok and math.isfinite(all_min_x) and math.isfinite(all_max_x):
                cx = (all_min_x + all_max_x) / 2.0
                cy = (all_min_y + all_max_y) / 2.0
                cz = all_min_z  # keep base at Z=0
                return AllplanGeo.Vector3D(-cx, -cy, -cz)
        except Exception:
            pass
        return AllplanGeo.Vector3D()

    # ═══════════════════════════════════════════════════════════════════════
    #  FILE-BASED MODULE LOADER
    # ═══════════════════════════════════════════════════════════════════════

    def _load_element_module_by_file(self, element_type: str) -> Any:
        """Import an element module using its absolute file path.

        Bypasses the Python naming restriction for paths with hyphens
        (e.g. 'pyp-scripts.clau_de_pas_script').
        """
        pythonparts_modules = getattr(self.script_object, "pythonparts_modules", [])
        elem_def = None
        for item in pythonparts_modules or []:
            if str(getattr(item, "key", "") or "").strip() == element_type:
                elem_def = item
                break

        if elem_def is None:
            return None

        module_path = str(getattr(elem_def, "module_path", "") or "").strip()
        if not module_path:
            return None

        parts = module_path.split(".")
        pyp_folder = self._PYP_SCRIPTS_DIR.name
        if parts and parts[0].replace("-", "_") == pyp_folder.replace("-", "_"):
            relative_parts = parts[1:]
        else:
            relative_parts = parts

        if not relative_parts:
            return None

        file_path = self._PYP_SCRIPTS_DIR.joinpath(*relative_parts).with_suffix(".py")
        if not file_path.exists():
            return None

        module_name = f"_agua_elem_{relative_parts[-1]}"
        if module_name in sys.modules:
            return sys.modules[module_name]

        try:
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            return module
        except Exception as ex:
            print(f"[AGUA_MGR] _load_element_module_by_file error: {ex}")
            sys.modules.pop(module_name, None)
            return None

    def _get_model_elems_from_module(self, element_type: str) -> List[Any]:
        """Load the element module by file path and call create_preview to get geometry."""
        module = self._load_element_module_by_file(element_type)
        if module is None:
            return []

        try:
            if hasattr(module, "create_preview"):
                result = module.create_preview(self.build_ele, None)
                if isinstance(result, (list, tuple)) and len(result) >= 1:
                    elems = result[0]
                else:
                    elems = result
                if hasattr(elems, "__iter__"):
                    return list(elems)
        except Exception as ex:
            print(f"[AGUA_MGR] _get_model_elems_from_module error for '{element_type}': {ex}")
        return []
