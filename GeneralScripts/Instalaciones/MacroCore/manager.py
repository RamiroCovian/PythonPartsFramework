# -*- coding: utf-8 -*-
"""Reusable macro manager core for installation-specific managers."""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Utility as PythonUtility

from FileNameService import FileNameService
from PythonPartUtil import PythonPartUtil

from Instalaciones.PolyLib.marker_manager import MarkerManager


class MacroCoreManager(MarkerManager):
    """Reusable macro functionality shared across installations."""

    MACRO_POINT_MODE_PARAM = "MarkerPointMode"
    MACRO_LIBRARY_TYPE_PARAM = "MacroLibraryElementType"
    MACRO_SMART_PATH_PARAM = "MacroSmartSymbolPath"
    MACRO_FIXTURE_PATH_PARAM = "MacroFixturePath"
    MACRO_SELECTED_LOCAL_Z_PARAM = "MacroSelectedLocalZ"
    MACRO_Z_RELATIVE_PARAM = "MacroZRelative"
    MACRO_Z_ABS_PARAM = "MacroZAbs"
    MACRO_ROT_X_PARAM = "MacroRotX"
    MACRO_ROT_Y_PARAM = "MacroRotY"
    MACRO_ROT_Z_PARAM = "MacroRotZ"

    def get_macro_settings_from_palette(self) -> Optional[dict]:
        """Read macro configuration from palette parameters."""
        mode = 0
        try:
            mode = int(
                getattr(getattr(self.build_ele, self.MACRO_POINT_MODE_PARAM, None), "value", 0) or 0
            )
        except Exception:
            mode = 0

        kind = "start" if mode == 0 else ("end" if mode == 1 else "free")
        lib_type = str(
            getattr(getattr(self.build_ele, self.MACRO_LIBRARY_TYPE_PARAM, None), "value", "") or "SmartSymbol"
        )
        smart_path = str(
            getattr(getattr(self.build_ele, self.MACRO_SMART_PATH_PARAM, None), "value", "") or ""
        ).strip()
        fixture_path = str(
            getattr(getattr(self.build_ele, self.MACRO_FIXTURE_PATH_PARAM, None), "value", "") or ""
        ).strip()

        selected_z = -999999.0
        try:
            selected_z = float(
                getattr(
                    getattr(self.build_ele, self.MACRO_SELECTED_LOCAL_Z_PARAM, None),
                    "value",
                    -999999,
                )
                or -999999
            )
        except Exception:
            selected_z = -999999.0

        if selected_z > -100000.0:
            z_relative = 0.0
            try:
                z_relative = float(
                    getattr(getattr(self.build_ele, self.MACRO_Z_RELATIVE_PARAM, None), "value", 0) or 0.0
                )
            except Exception:
                z_relative = 0.0
            z_abs = selected_z + z_relative
            self.current_floor_z = selected_z
            self.current_floor_index = 0
            auto_detect = True
        else:
            z_abs = 0.0
            try:
                z_abs = float(
                    getattr(getattr(self.build_ele, self.MACRO_Z_ABS_PARAM, None), "value", 0) or 0.0
                )
            except Exception:
                z_abs = 0.0
            z_relative = z_abs
            self.current_floor_z = z_abs
            self.current_floor_index = -1
            auto_detect = False

        rot_x, rot_y, rot_z = self.get_macro_rotation()

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
            "rot_x": rot_x,
            "rot_y": rot_y,
            "rot_z": rot_z,
        }

    def get_macro_rotation(self) -> Tuple[float, float, float]:
        def _get_angle(name: str) -> float:
            try:
                param = getattr(self.build_ele, name, None)
                if param is None:
                    return 0.0
                raw = getattr(param, "value", param)
                return float(raw or 0.0)
            except Exception:
                return 0.0

        return (
            _get_angle(self.MACRO_ROT_X_PARAM),
            _get_angle(self.MACRO_ROT_Y_PARAM),
            _get_angle(self.MACRO_ROT_Z_PARAM),
        )

    def _add_macro_library_marker(self) -> bool:
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
        else:
            if self.macro_selected_point is None:
                PythonUtility.ShowMessageBox(
                    "Modo Libre: primero pulsa 'Seleccionar punto' y haz click.",
                    PythonUtility.MB_OK,
                )
                return False
            pos = AllplanGeo.Point3D(
                self.macro_selected_point.X,
                self.macro_selected_point.Y,
                self.macro_selected_point.Z,
            )

        lib_type = settings.get("lib_type", "SmartSymbol")
        smart_path = settings.get("smart_path", "")
        fixture_path = settings.get("fixture_path", "")
        if lib_type == "SmartSymbol" and not smart_path:
            PythonUtility.ShowMessageBox(
                "Selecciona primero una macro (SmartSymbol .nmk).",
                PythonUtility.MB_OK,
            )
            return False
        if lib_type == "Fixture" and not fixture_path:
            PythonUtility.ShowMessageBox(
                "Selecciona primero un fixture (.lfx/.pxf).",
                PythonUtility.MB_OK,
            )
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
            "rot_x": settings.get("rot_x", 0.0),
            "rot_y": settings.get("rot_y", 0.0),
            "rot_z": settings.get("rot_z", 0.0),
            "floor_index": settings.get("floor_index", self.current_floor_index),
            "floor_z": settings.get("floor_z", self.current_floor_z),
            "auto_detect": settings.get("auto_detect", False),
        }
        self.macro_markers.append(marker)
        self.macro_selected_point = None
        self._try_save_state()
        self._try_draw_preview(None)
        return True

    def get_macro_cursor_preview_geo(self, cursor_pos: AllplanGeo.Point3D) -> List[Any]:
        try:
            settings = self.get_macro_settings_from_palette()
            if not settings:
                return []
            return self._create_library_preview_elements(settings, cursor_pos)
        except Exception as ex:
            print(f"[MACRO_CORE] get_macro_cursor_preview_geo error: {ex}")
        return []

    def draw_marker_preview(self, model_ele_list: List[Any], current_pnt: Any) -> None:
        super().draw_marker_preview(model_ele_list, current_pnt)
        try:
            pnt3d = self._ensure_point3d(current_pnt) if current_pnt is not None else None
        except Exception:
            pnt3d = None

        selected_idx = self.macro_selected_index
        for idx, marker in enumerate(self.macro_markers or []):
            try:
                pos = marker.get("pos")
                if pos is None:
                    continue
                preview_pos = (
                    pnt3d if selected_idx is not None and idx == selected_idx and pnt3d is not None else pos
                )
                preview_geo = self._create_library_preview_elements(marker, preview_pos)
                if preview_geo:
                    model_ele_list.extend(preview_geo)
            except Exception as ex:
                print(f"[MACRO_CORE] draw_marker_preview overlay error: {ex}")

    def _create_library_preview_elements(
        self,
        settings_or_marker: dict,
        placement_xy: AllplanGeo.Point3D,
    ) -> List[Any]:
        lib_ele = self.create_library_element_from_marker(settings_or_marker, placement_xy)
        return [lib_ele] if lib_ele is not None else []

    def create_library_element_from_marker(
        self,
        marker: dict,
        placement_xy: Optional[AllplanGeo.Point3D] = None,
    ) -> Any:
        lib_type = str(marker.get("lib_type", "SmartSymbol") or "SmartSymbol")
        placement_mat = self._build_macro_placement_matrix(marker, placement_xy)

        if lib_type == "SmartSymbol":
            smart_path = str(marker.get("smart_path", "") or "").strip()
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
            fixture_path = str(marker.get("fixture_path", "") or "").strip()
            if not fixture_path:
                return None
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
            return AllplanBasisElements.LibraryElement(lib_ele_prop)

        return None

    def append_macro_pythonparts(self, pythonpart_group_list: list, doc: Any) -> None:
        if not self.macro_markers:
            return
        for m in self.macro_markers:
            try:
                pos = m.get("pos")
                if pos is None:
                    continue
                lib_ele = self.create_library_element_from_marker(m)
                if lib_ele is None:
                    continue
                pyp_util = PythonPartUtil()
                pyp_util.add_library_elements(lib_ele)
                try:
                    com_prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
                    com_prop.HelpConstruction = True
                    com_prop.ColorByLayer = True
                    com_prop.PenByLayer = True
                    com_prop.StrokeByLayer = True
                    mm = 1.0
                    z_abs = float(m.get("z_abs", 0.0) or 0.0)
                    polyhed = AllplanGeo.Polyhedron3D.CreateCuboid(
                        AllplanGeo.AxisPlacement3D(
                            AllplanGeo.Point3D(pos.X - mm / 2, pos.Y - mm / 2, z_abs - mm / 2)
                        ),
                        mm, mm, mm,
                    )
                    pyp_util.add_pythonpart_view_2d3d(
                        AllplanBasisElements.ModelElement3D(com_prop, polyhed)
                    )
                except Exception:
                    pass
                pp = pyp_util.get_pythonpart(self.build_ele)
                pythonpart_group_list.append(pp)
            except Exception as ex:
                print(f"[MACRO_CORE] append_macro_pythonparts error: {ex}")

    def serialize_markers(self) -> dict:
        state = super().serialize_markers()
        macro_data = state.get("macro_markers", []) or []
        for idx, marker in enumerate(self.macro_markers or []):
            if idx >= len(macro_data):
                break
            macro_data[idx]["rot_x"] = float(marker.get("rot_x", 0.0) or 0.0)
            macro_data[idx]["rot_y"] = float(marker.get("rot_y", 0.0) or 0.0)
            macro_data[idx]["rot_z"] = float(marker.get("rot_z", 0.0) or 0.0)
        state["macro_markers"] = macro_data
        return state

    def deserialize_markers(self, state: dict) -> None:
        super().deserialize_markers(state)
        raw_macros = state.get("macro_markers", []) or []
        for idx, marker in enumerate(self.macro_markers or []):
            if idx >= len(raw_macros):
                break
            raw = raw_macros[idx] or {}
            marker["rot_x"] = float(raw.get("rot_x", 0.0) or 0.0)
            marker["rot_y"] = float(raw.get("rot_y", 0.0) or 0.0)
            marker["rot_z"] = float(raw.get("rot_z", 0.0) or 0.0)

    def _build_macro_placement_matrix(
        self,
        marker: dict,
        placement_xy: Optional[AllplanGeo.Point3D] = None,
    ) -> AllplanGeo.Matrix3D:
        if placement_xy is None:
            placement_xy = marker.get("pos")
        if placement_xy is None:
            placement_xy = AllplanGeo.Point3D()
        try:
            z_abs = float(marker.get("z_abs", placement_xy.Z) or placement_xy.Z)
        except Exception:
            z_abs = placement_xy.Z
        try:
            rot_x = float(marker.get("rot_x", 0.0) or 0.0)
            rot_y = float(marker.get("rot_y", 0.0) or 0.0)
            rot_z = float(marker.get("rot_z", 0.0) or 0.0)
        except Exception:
            rot_x, rot_y, rot_z = (0.0, 0.0, 0.0)

        placement_point = AllplanGeo.Point3D(placement_xy.X, placement_xy.Y, z_abs)
        mat = AllplanGeo.Matrix3D()
        if rot_x != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(1, 0, 0)),
                AllplanGeo.Angle.FromDeg(rot_x),
            )
        if rot_y != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 1, 0)),
                AllplanGeo.Angle.FromDeg(rot_y),
            )
        if rot_z != 0.0:
            mat.Rotation(
                AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 0, 1)),
                AllplanGeo.Angle.FromDeg(rot_z),
            )
        mat.Translate(AllplanGeo.Vector3D(placement_point))
        return mat
