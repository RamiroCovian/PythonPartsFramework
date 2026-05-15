# -*- coding: utf-8 -*-
"""
CommonPoint – Captura por roles + Editor de polilíneas con persistencia (Allplan PythonParts)
============================================================================================

Este script unifica dos modos:
- CAPTURA: clicás puntos con rol (Inicial/Paso/Bifurcación/Final). Al marcar "Final" se cierra la corrida,
  se crea geometría en el documento y se persiste en JSON (merge por PathId).
- EDITOR: vista previa rica para editar polilíneas guardadas: mover vértices, insertar en midpoints/segmentos,
  borrar secciones, extender por doble‑clic en extremos, bifurcar desde extremos o puntos insertados.

Ajustes pedidos por el usuario:
- Tolerancia de *snap* por defecto: 5 mm (HIT_TOL_*).
- El elemento "punto" que se crea en captura es un **cuadrado** (no símbolo), con tamaño configurable.
- Persistencia en JSON en escritorio.
- Soporta "ambas" funciones (captura y editor).

IMPORTANTE
----------
Este archivo asume que el .pyp usa los mismos nombres de parámetros que el de ejemplo (PathId, SegmentId,
PointRole, CheckBoxValue, CommonProp, SymbolCommonProps, CreateSymbol, y los botones 2100..2103 y 1001..1006).
Si tu .pyp cambia, actualizá los getters en este .py.

Pendiente de validar y ajustar en obra: ver README_CommonPoint.md
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
import os, json, random, sys

# ===== Allplan imports =====
import NemAll_Python_Geometry      as AllplanGeo
import NemAll_Python_BaseElements  as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_Input     as AllplanIFW

from BuildingElement     import BuildingElement
from BaseScriptObject    import BaseScriptObject, BaseScriptObjectData
from CreateElementResult import CreateElementResult
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

if TYPE_CHECKING:
    from __BuildingElementStubFiles.PointInputBuildingElement import PointInputBuildingElement
else:
    PointInputBuildingElement = BuildingElement

# -------------------- Helpers --------------------
def _flush():
    try: sys.stdout.flush()
    except Exception: pass

def _desktop_dir() -> str:
    up = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    d  = os.path.join(up, "Desktop")
    os.makedirs(d, exist_ok=True)
    print("[DESKTOP] usando:", d); _flush()
    return d

# Persistencia JSON (un archivo aleatorio por sesión para evitar lockeos)
JSON_PATH = os.path.join(_desktop_dir(), f"common_points_{random.randint(0,999_999_999)}.json")
print("[BOOT] JSON_PATH =", JSON_PATH); _flush()

# -------------------- Datos captura --------------------
@dataclass
class Capture:
    p: AllplanGeo.Point3D
    color_id: int
    path_id: int
    seg_id: int
    role: int   # 0 Inicial, 1 Paso, 2 Bifurcación, 3 Final

# -------------------- Hook versión --------------------
def check_allplan_version(_build_ele: BuildingElement, _version: float) -> bool:
    print(f"[CHECK VERSION] version={_version}"); _flush()
    return True

def create_script_object(build_ele: BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    return UnifiedScriptObject(build_ele, script_object_data)

# -------------------- Constantes UI / Tolerancias --------------------
# Requerimiento: tolerancia default 5mm
HANDLE_SIZE            = 90.0
HIT_TOL_VERTEX         = 5.0     # mm
HIT_TOL_SEGMENT        = 5.0     # mm
HOVER_SCALE            = 1.25
DRAG_SCALE             = 1.5
SEGMENT_OVERLAY_Z_BIAS = 1.0
SEGMENT_OVERLAY_PEN    = 13
INSERT_PREVIEW_COLOR   = 6
MIN_INSERT_OFFSET_MM   = 2.0
MIN_SEG_LEN_MM         = 1.0
HANDLE_COLOR_IDX       = 2
SAVED_POLY_COLOR       = 3
SEGMENT_HOVER_COLOR    = 1
SEGMENT_SEL_COLOR      = 5
BRANCH_ANCHOR_COLOR    = 7
MIDPOINT_COLOR         = 4
MIDPOINT_SIZE_FACTOR   = 0.90
MIDPOINT_PEN           = 13
MIDPOINT_Z_BIAS        = 1.0
RECT_COLOR             = 8
RECT_PEN               = 12
BOX_SELECTED_SEG_COLOR = 9

# Tamaño del cuadrado (elemento puntual) que se crea en modo captura.
DEFAULT_SQUARE_SIZE_MM = 50.0

def MAX_EPS(x: float) -> float:
    return max(min(x, 0.49), 0.0)

# -------------------- ScriptObject unificado --------------------
class UnifiedScriptObject(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele  # type: ignore

        # Interactores
        self._cap: Optional[CaptureInteractor]   = None
        self._edit: Optional[PolylineInteractor] = None

        # Historial común para el editor
        self.saved_paths: List[List[AllplanGeo.Point3D]] = []
        self._created_hashes: Set[Tuple[Tuple[float,float,float], ...]] = set()

    # ---------- ciclo de vida ----------
    def start_input(self):
        print("[SO] start_input -> CAPTURA por defecto, editor disponible por botones 100x")
        self._ensure_capture()

    def start_next_input(self):
        # fallback: si algo quedó pendiente
        try:
            if self._cap:
                print("[SO] start_next_input fallback -> export JSON + crear pendientes")
                self._cap._export_json_all_paths()
                self._cap._close_runs_to_saved_paths(create_now=True)
        except Exception as e:
            print("[SO] start_next_input fallback EXC:", e)
        self.script_object_interactor = None

    def execute(self) -> CreateElementResult:
        return CreateElementResult([])

    # ---------- switching helpers ----------
    def _ensure_capture(self):
        if self._cap is None:
            self._cap = CaptureInteractor(self, self.build_ele)
        self.script_object_interactor = self._cap
        if getattr(self._cap, "coord_input", None) is None and self.coord_input is not None:
            self._cap.start_input(self.coord_input)

    def _ensure_editor(self):
        if self._edit is None:
            self._edit = PolylineInteractor(self)
        self.script_object_interactor = self._edit
        if getattr(self._edit, "coord_input", None) is None and self.coord_input is not None:
            self._edit.start_input(self.coord_input)

    # ---------- eventos de paleta ----------
    def on_control_event(self, event_id: int):
        print(f"[SO] on_control_event: {event_id}")

        # --- BOTONES DE ROL (captura) ---
        if event_id in (2100, 2101, 2102, 2103):
            self._ensure_capture()
            mapping = {2100: 0, 2101: 1, 2102: 2, 2103: 3}
            return self._set_point_role(mapping[event_id])

        # --- BOTONES DE EDICIÓN ---
        self._ensure_editor()

        if event_id == 1001:  # Crear polilínea (toggle)
            self._edit.toggle_create_mode();  return True
        if event_id == 1002:  # Guardar polilínea
            self._edit.save_current_polyline(); print(f"[SO] Guardadas: {len(self.saved_paths)}"); return True
        if event_id == 1003:  # Finalizar y crear
            print("[SO] Finalizar -> guardar y crear inmediatamente")
            self._edit.save_current_polyline()
            self._finalize_and_create_now()
            # cerrar interacción
            for meth_name in ("CancelFunction", "OnCancelFunction", "CancelInput", "Cancel"):
                meth = getattr(self.coord_input, meth_name, None)
                if callable(meth):
                    try:
                        meth()
                        break
                    except Exception as ex:
                        print(f"[SO] coord_input.{meth_name}() ex: {ex}")
            return True
        if event_id == 1004:  # Borrar sección
            if getattr(self._edit, "selected_segments", None):
                changed = self._edit.delete_selected_segments_by_box()
            else:
                changed = self._edit.delete_selected_or_hovered_segment()
            print(f"[SO] Borrar -> {'OK' if changed else 'sin objetivo'}")
            return True
        if event_id == 1006:  # Bifurcar (auto ON crear si hace falta)
            self._edit.toggle_branch_mode(); return True

        return False

    def _set_point_role(self, r: int) -> bool:
        try:
            r = max(0, min(int(r), 3))
            getattr(self.build_ele, "PointRole").value = r
            print(f"[SO] PointRole -> {r}")
            if self._cap:
                self._cap._init_coord_prompt()
            return True
        except Exception as e:
            print("[SO] set PointRole EXC:", e); _flush()
            return False

    # ---------- util historial editor ----------
    def _hash_pts(self, pts: List[AllplanGeo.Point3D]) -> Tuple[Tuple[float,float,float], ...]:
        return tuple((round(p.X,3), round(p.Y,3), round(p.Z,3)) for p in pts)

    def add_saved_path(self, pts3: List[AllplanGeo.Point3D], mark_created: bool = True):
        if len(pts3) >= 2:
            pts_copy = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in pts3]
            self.saved_paths.append(pts_copy)
            if mark_created:
                self._created_hashes.add(self._hash_pts(pts_copy))
            print(f"[SO] add_saved_path -> total={len(self.saved_paths)}")

    def _finalize_and_create_now(self):
        """Crea en el documento cualquier corrida guardada que no esté creada aún."""
        if not self.saved_paths:
            print("[SO] finalize_now: no hay corridas guardadas"); return
        com_prop = AllplanBaseElements.CommonProperties(); com_prop.GetGlobalProperties()
        doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        pending = 0
        for pts in self.saved_paths:
            if len(pts) < 2: continue
            h = self._hash_pts(pts)
            if h in self._created_hashes:
                continue
            pl = AllplanGeo.Polyline3D()
            for p in pts: pl += p
            AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(),
                                               [AllplanBasisElements.ModelElement3D(com_prop, pl)], [], None)
            self._created_hashes.add(h)
            pending += 1
        print(f"[SO] finalize_now: creadas {pending} corridas pendientes")

# -------------------- Interactor de CAPTURA (sin preview) --------------------
class CaptureInteractor:
    def __init__(self, so: UnifiedScriptObject, build_ele: PointInputBuildingElement):
        self.so = so
        self.build_ele = build_ele
        self.coord_input: Optional[AllplanIFW.CoordinateInput] = None
        self.input_pnt: Optional[AllplanGeo.Point3D] = None
        self.captures: List[Capture] = []

    # ---- entrada estándar ----
    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input or AllplanIFW.CoordinateInput()
        print("[CAP] start_input"); _flush()

        def _v(name, default):
            try: return getattr(self.build_ele, name).value
            except Exception: return default

        self.coord_input.EnableAssistWndClick(_v("EnableAssistWndClick", False))
        self.coord_input.EnableZCoord(_v("EnableZCoordinate", True))
        self.coord_input.EnableUndoStep(_v("EnableUndoStep", False))
        self.coord_input.SetProjectionBase0(_v("SetProjectionBase0", True))

        # sincroniza color en CommonProp / SymbolCommonProps con Path
        path = self._current_path()
        col  = self._color_from_path(path)
        self._apply_color_to_commonprops(col)

        self._init_coord_prompt()

    def _init_coord_prompt(self):
        if not self.coord_input: return
        try:
            r = self._current_role()
            msg_role = {0:"Inicial",1:"Paso",2:"Bifurcación",3:"Final"}.get(r, "Paso")
        except Exception:
            msg_role = "Paso"
        prompt = AllplanIFW.InputStringConvert(f"Click ({msg_role}). Al marcar 'Final' -> crear corrida + export JSON.")
        mode = AllplanIFW.CoordinateInputMode(
            identMode       = AllplanIFW.eIdentificationMode.names["eIDENT_POINT"],
            drawPointSymbol = AllplanIFW.eDrawElementIdentPointSymbols.names["eDRAW_IDENT_ELEMENT_POINT_SYMBOL_YES"]
        )
        if self.input_pnt is None:
            self.coord_input.InitFirstPointInput(prompt, mode)
        else:
            self.coord_input.InitNextPointInput(prompt, mode)

    def on_preview_draw(self):
        if self.coord_input:
            self.coord_input.GetCurrentPoint()  # sin preview

    def on_mouse_leave(self):
        if self.coord_input:
            self.coord_input.GetCurrentPoint()

    def on_input_undo(self) -> bool:
        return True

    def on_cancel_function(self) -> bool:
        """ESC: cerrar corridas abiertas + export JSON (fallback principal)."""
        print("[CAP] ESC -> cerrar corridas abiertas + export all"); _flush()
        try:
            self._export_json_all_paths()
            self._close_runs_to_saved_paths(create_now=True)
        except Exception as e:
            print("[CAP] ESC EXC:", e)
        return True

    def on_value_input_control_enter(self) -> bool:
        return True

    def process_mouse_msg(self, mouse_msg: int,
                          pnt: AllplanGeo.Point2D,
                          msg_info: AllplanIFW.AddMsgInfo) -> bool:
        if not self.coord_input:
            return True

        res = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info)
        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        self.input_pnt = res.GetPoint()
        if self.input_pnt is not None:
            role = self._current_role()
            path = self._current_path()
            seg  = self._current_segment()
            col  = self._color_from_path(path)

            self.captures.append(
                Capture(
                    p        = AllplanGeo.Point3D(self.input_pnt.X, self.input_pnt.Y, self.input_pnt.Z),
                    color_id = col, path_id = path, seg_id = seg, role = role
                )
            )
            print(f"[CAP] #{len(self.captures)} role={role} path={path} seg={seg} z={self.input_pnt.Z}"); _flush()

            # Crear "punto" como un cuadrado
            self._create_square_element(self.input_pnt, size_mm=DEFAULT_SQUARE_SIZE_MM, color_id=col)

            # Al marcar Final → exportar JSON y crear la corrida
            if role == 3:
                print(f"[CAP] Final -> export JSON y cerrar corrida (path {path})"); _flush()
                self._export_json_for_path(path)
                self._close_runs_to_saved_paths(pid=path, create_now=True)

        self._init_coord_prompt()
        return True

    # ---- cuadrado en captura ----
    def _create_square_element(self, center: AllplanGeo.Point3D, size_mm: float, color_id: int):
        """Crea un cuadrado plano (en XY) centrado en 'center'."""
        if not self.coord_input or center is None:
            return
        half = size_mm * 0.5
        p1 = AllplanGeo.Point3D(center.X - half, center.Y - half, center.Z)
        p2 = AllplanGeo.Point3D(center.X + half, center.Y - half, center.Z)
        p3 = AllplanGeo.Point3D(center.X + half, center.Y + half, center.Z)
        p4 = AllplanGeo.Point3D(center.X - half, center.Y + half, center.Z)

        com_prop = AllplanBaseElements.CommonProperties(); com_prop.GetGlobalProperties()
        try:
            base_cp = getattr(self.build_ele, "CommonProp").value
            for name in ("Pen", "Stroke", "Layer", "ColorByLayer", "PenByLayer", "StrokeByLayer"):
                try: setattr(com_prop, name, getattr(base_cp, name))
                except Exception: pass
        except Exception:
            pass
        com_prop.Color = color_id

        lines = [
            AllplanGeo.Line3D(p1, p2), AllplanGeo.Line3D(p2, p3),
            AllplanGeo.Line3D(p3, p4), AllplanGeo.Line3D(p4, p1)
        ]
        elems = [AllplanBasisElements.ModelElement3D(com_prop, ln) for ln in lines]
        AllplanBaseElements.CreateElements(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            elems, [], None
        )

    # ---- cierre / creación de corridas ----
    def _close_runs_to_saved_paths(self, pid: Optional[int] = None, create_now: bool = False):
        """
        Parte en corridas por roles (Inicial...Final) en ORDEN DE CAPTURA.
        Si create_now=True, crea inmediatamente en el documento cada corrida (>=2 puntos).
        Si pid es None, procesa todos los paths; si no, solo ese.
        """
        if not self.captures:
            return

        doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        paths = [pid] if pid is not None else sorted({c.path_id for c in self.captures})

        for cur in paths:
            caps = [c for c in self.captures if c.path_id == cur]
            if not caps:
                continue

            run3: List[AllplanGeo.Point3D] = []

            def flush_run():
                nonlocal run3
                if len(run3) >= 2:
                    # 1) historial compartido (para editor)
                    self.so.add_saved_path(run3, mark_created=create_now)
                    # 2) crear YA si corresponde
                    if create_now and doc is not None:
                        try:
                            com_prop = AllplanBaseElements.CommonProperties(); com_prop.GetGlobalProperties()
                            try:
                                base_cp = getattr(self.build_ele, "CommonProp").value
                                for name in ("Pen", "Stroke", "Layer", "ColorByLayer", "PenByLayer", "StrokeByLayer"):
                                    try: setattr(com_prop, name, getattr(base_cp, name))
                                    except Exception: pass
                            except Exception:
                                pass
                            com_prop.Color = self._color_from_path(cur)

                            pl = AllplanGeo.Polyline3D()
                            for p in run3: pl += p

                            AllplanBaseElements.CreateElements(
                                doc, AllplanGeo.Matrix3D(),
                                [AllplanBasisElements.ModelElement3D(com_prop, pl)],
                                [], None
                            )
                            print(f"[CREATE] Polyline3D creada (path={cur}, npts={len(run3)}, color={com_prop.Color})")
                        except Exception as e:
                            print("[CREATE] EXC creando polilínea:", e)
                run3 = []

            for c in caps:
                if c.role == 0:  # Inicial
                    if run3: flush_run()
                    run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                elif c.role in (1, 2):  # Paso / Bif
                    if not run3:
                        run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                    else:
                        run3.append(AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z))
                elif c.role == 3:  # Final
                    if not run3:
                        run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                    else:
                        run3.append(AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z))
                    flush_run()

            if run3 and create_now:
                flush_run()

    # ---- JSON helpers ----
    def _export_json_all_paths(self):
        for pid in sorted({c.path_id for c in self.captures}):
            self._export_json_for_path(pid)

    def _export_json_for_path(self, pid: int):
        print(f"[JSON] export path_id={pid} → {JSON_PATH}"); _flush()
        evento = {"iniciales": [], "intermedios": [], "finales": []}
        for c in self.captures:
            if c.path_id != pid: continue
            pt = {
                "x": float(round(c.p.X, 3)), "y": float(round(c.p.Y, 3)), "z": float(round(c.p.Z, 3)),
                "segmento": int(c.seg_id), "tipo": {0:"Inicial",1:"Paso",2:"Bifurcacion",3:"Final"}.get(c.role, "Paso"),
                "color": int(c.color_id)
            }
            if c.role == 0:   evento["iniciales"].append(pt)
            elif c.role == 3: evento["finales"].append(pt)
            else:             evento["intermedios"].append(pt)

        # merge
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list): data = []
        except FileNotFoundError:
            data = []
        except Exception:
            data = []

        index: Dict[int, Dict[str, Any]] = {}
        for entry in data:
            try: index[int(entry.get("path_id"))] = entry
            except Exception: pass

        if pid in index:
            dst = index[pid]
            for k in ("iniciales","intermedios","finales"):
                dst[k] = (dst.get(k) or []) + evento[k]
        else:
            index[pid] = {"path_id": pid, **evento}

        out_list = [index[k] for k in sorted(index.keys())]
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(out_list, f, ensure_ascii=False, indent=2)
            print(f"[JSON] OK path_id={pid} (len={len(out_list)})"); _flush()
        except Exception as e:
            print("[JSON] ERROR escritura:", e); _flush()

    # ---- utilidades varias ----
    def _apply_color_to_commonprops(self, color_id: int):
        try:
            cp = getattr(self.build_ele, "CommonProp").value
            if getattr(cp, "Color", None) != color_id:
                cp.Color = color_id
                getattr(self.build_ele, "CommonProp").value = cp
        except Exception:
            pass
        try:
            scp = getattr(self.build_ele, "SymbolCommonProps").value
            if getattr(scp, "Color", None) != color_id:
                scp.Color = color_id
                getattr(self.build_ele, "SymbolCommonProps").value = scp
        except Exception:
            pass
        _flush()

    def _color_from_path(self, path: int) -> int:
        try: path = int(path)
        except Exception: path = 1
        return max(1, min(path, 255))

    def _current_role(self) -> int:
        try:
            val = getattr(self.build_ele, "PointRole").value
            if isinstance(val, (int, float)): return max(0, min(int(val), 3))
            return 1
        except Exception:
            return 1

    def _current_path(self) -> int:
        try: return max(1, int(getattr(self.build_ele, "PathId").value))
        except Exception: return 1

    def _current_segment(self) -> int:
        try: return max(1, int(getattr(self.build_ele, "SegmentId").value))
        except Exception: return 1

# -------------------- EDITOR (con preview) --------------------
class PolylineInteractor:
    # ---------- Borrar por marco ----------
    def delete_selected_segments_by_box(self) -> bool:
        if not self.selected_segments:
            return False
        from collections import defaultdict
        to_delete = defaultdict(set)  # path_idx -> set(seg_idx)
        for kind, path_idx, seg_idx in self.selected_segments:
            if kind == 'saved':
                to_delete[path_idx].add(seg_idx)

        changed = False
        new_saved_paths = []
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx not in to_delete:
                new_saved_paths.append(pts); continue
            seg_indices = to_delete[path_idx]
            if len(seg_indices) == len(pts) - 1:
                changed = True; continue
            fragment = [pts[0]]
            for i in range(len(pts) - 1):
                if i in seg_indices:
                    if len(fragment) >= 2:
                        new_saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment]); changed = True
                    fragment = [pts[i+1]]
                else:
                    fragment.append(pts[i+1])
            if len(fragment) >= 2:
                new_saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment]); changed = True

        if changed:
            self.script_object.saved_paths = new_saved_paths
            self.selected_segments.clear()
            self.selected_seg = None; self.hover_seg = None
            self.insert_preview_p = None; self.insert_target = None; self.hover_mid = None
            self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())
        return changed

    def __init__(self, script_object: UnifiedScriptObject):
        self.script_object = script_object
        # Modo creación
        self.create_mode = False
        # Polilínea activa
        self.points: List[AllplanGeo.Point3D] = []
        self.current_point = AllplanGeo.Point3D()
        # Estados
        self.hover_index = -1; self.drag_index = -1; self.is_dragging = False
        self.saved_dragging = None  # (path_idx, pt_idx)
        self.extend_target = None   # (path_idx, 'start'|'end')
        self.hover_seg = None; self.selected_seg = None
        self.insert_mode = False; self.insert_preview_p = None; self.insert_target = None
        self.hover_mid = None
        self.branch_mode = False; self.saved_hover_point = None
        self.box_selecting = False; self.box_start = None; self.box_curr = None
        self.selected_segments = set()  # (kind, path_idx, seg_idx)
        self.com_prop = AllplanBaseElements.CommonProperties(); self.com_prop.GetGlobalProperties()

    def start_input(self, coord_input):
        self.coord_input = coord_input
        self._sync_insert_mode_from_palette()
        self._print_prompt()

    def _print_prompt(self):
        msg = (
            f"[Crear: {'ON' if self.create_mode else 'OFF'}] "
            "Edición: drag vértices guardados, selección por marco; midpoints insertables; "
            "doble clic extremo = extender; 1006=bifurcar; 1004=borrar; 1002=guardar; ESC/1003=finalizar"
        )
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))

    def toggle_create_mode(self):
        self.create_mode = not self.create_mode
        print(f"[INT] Crear: {'ON' if self.create_mode else 'OFF'}")
        if not self.create_mode:
            self.save_current_polyline(); self.branch_mode = False
        self.is_dragging = False; self.drag_index = -1; self.saved_dragging = None
        self.hover_mid = None; self.hover_seg = None; self.selected_seg = None
        self.box_selecting = False; self.box_start = None; self.box_curr = None
        self._print_prompt()
        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

    # ---- Paleta -> modo insertar ----
    def _get_palette_insert_mode(self) -> Optional[bool]:
        try:
            val = getattr(self.script_object.build_ele, "CheckBoxValue", None)
            if hasattr(val, "value"): return bool(val.value)
            if isinstance(val, bool): return val
        except Exception:
            pass
        return None

    def _sync_insert_mode_from_palette(self):
        new_mode = self._get_palette_insert_mode()
        if new_mode is None: return
        if new_mode != self.insert_mode:
            self.insert_mode = new_mode
            print(f"[INT] Insert mode: {'ON' if self.insert_mode else 'OFF'}")
            self.insert_preview_p = None; self.insert_target = None

    # ---- Bifurcación ----
    def toggle_branch_mode(self):
        # Encender crear si hace falta
        if not self.create_mode:
            print("[INT] Crear estaba OFF, se enciende para bifurcar.")
            self.create_mode = True

        self.branch_mode = not self.branch_mode
        print(f"[INT] Branch: {'ON' if self.branch_mode else 'OFF'}")

        # Intento de anclaje automático si acaba de encenderse
        if self.branch_mode:
            curr = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()

            # 1) ¿estás cerca de un EXTREMO? => extensión directa
            hv = self._find_hover_saved_point(curr, only_extremes=True) or self._nearest_saved_vertex(curr, tol_mult=1.1)
            if hv is not None:
                pidx, vidx, anchor = hv
                if 0 <= pidx < len(self.script_object.saved_paths):
                    pts = self.script_object.saved_paths[pidx]
                    if vidx == 0 or vidx == len(pts) - 1:
                        side = 'start' if vidx == 0 else 'end'
                        print(f"[INT] Branch auto: extremo elegible de poly #{pidx} -> EXTENDER ({side}).")
                        self._start_extension_from_endpoint(pidx, side, anchor)
                        self.branch_mode = False
                        self._draw_preview(curr)
                        return

            # 2) ¿estás sobre un segmento y el modo insertar está ON? => insertar y ramificar
            if self.insert_mode:
                seg, q = self._nearest_saved_segment(curr, tol_mult=1.25)
                if seg and q:
                    a, b = self._get_segment_endpoints(seg)
                    if a and b:
                        t, _ = self._segment_project_point(a, b, q)
                        if self._can_insert_here(a, b, t):
                            self._insert_on_segment(seg, q, keep_selection_left=True)
                            print(f"[INT] Branch auto: anclaje en segmento {seg}, punto insertado.")
                            self._begin_new_branch_from(q)
                            self.branch_mode = False
                            self._draw_preview(curr)
                            return

            print("[INT] Branch: mové el mouse sobre un extremo o sobre un segmento (con 'Mode Insertar punto' ON) y clic para anclar.")
        else:
            self.saved_hover_point = None

        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

    # ---- Utilidades (tolerancia 5mm) ----
    def _dist_sq(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx, dy, dz = a.X - b.X, a.Y - b.Y, a.Z - b.Z
        return dx*dx + dy*dy + dz*dz

    def _segment_len(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        return (self._dist_sq(a, b)) ** 0.5

    def _segment_project_point(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, p: AllplanGeo.Point3D):
        vx, vy, vz = b.X - a.X, b.Y - a.Y, b.Z - a.Z
        wx, wy, wz = p.X - a.X, p.Y - a.Y, p.Z - a.Z
        vv = vx*vx + vy*vy + vz*vz
        if vv <= 1e-12:
            return 0.0, AllplanGeo.Point3D(a.X, a.Y, a.Z)
        t = (vx*wx + vy*wy + vz*wz) / vv
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        q = AllplanGeo.Point3D(a.X + t*vx, a.Y + t*vy, a.Z + t*vz)
        return t, q

    def _midpoint(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> AllplanGeo.Point3D:
        return AllplanGeo.Point3D((a.X + b.X) * 0.5, (a.Y + b.Y) * 0.5, (a.Z + b.Z) * 0.5)

    def _find_hover_index(self, p: AllplanGeo.Point3D) -> int:
        if not self.points: return -1
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = -1; best_d2 = max_d2 + 1.0
        for i, pt in enumerate(self.points):
            d2 = self._dist_sq(p, pt)
            if d2 <= max_d2 and d2 < best_d2:
                best_d2 = d2; best = i
        return best

    def _find_hover_saved_point(self, p: AllplanGeo.Point3D, only_extremes: bool = False):
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None; best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            indices = [0, len(pts)-1] if (only_extremes and len(pts) >= 1) else range(len(pts))
            for i in indices:
                q = pts[i]; d2 = self._dist_sq(p, q)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2; best = (path_idx, i, q)
        return best

    def _find_hover_segment(self, p: AllplanGeo.Point3D, preferred_kind: Optional[str] = None):
        max_d2 = HIT_TOL_SEGMENT * HIT_TOL_SEGMENT
        best = None; best_d2 = max_d2 + 1.0

        # activa
        if preferred_kind in (None, 'active') and len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                a, b = self.points[i], self.points[i+1]
                _, q = self._segment_project_point(a, b, p)
                dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                d2 = dx*dx + dy*dy + dz*dz
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2; best = ('active', -1, i)

        # guardadas
        if preferred_kind in (None, 'saved'):
            for path_idx, pts in enumerate(self.script_object.saved_paths):
                if len(pts) < 2: continue
                for i in range(len(pts) - 1):
                    a, b = pts[i], pts[i+1]
                    _, q = self._segment_project_point(a, b, p)
                    dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                    d2 = dx*dx + dy*dy + dz*dz
                    if d2 <= max_d2 and d2 < best_d2:
                        best_d2 = d2; best = ('saved', path_idx, i)
        return best

    def _find_hover_midpoint(self, p: AllplanGeo.Point3D):
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None; best_d2 = max_d2 + 1.0
        if len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                mp = self._midpoint(self.points[i], self.points[i+1])
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2; best = ('active', -1, i, mp)
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) < 2: continue
            for i in range(len(pts) - 1):
                mp = self._midpoint(pts[i], pts[i+1])
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2; best = ('saved', path_idx, i, mp)
        return best

    # --- helpers "nearest" ---
    def _nearest_saved_vertex(self, p: AllplanGeo.Point3D, tol_mult: float = 1.25):
        max_d2 = (HIT_TOL_VERTEX * tol_mult) ** 2
        best = None
        best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            for i, q in enumerate(pts):
                dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                d2 = dx*dx + dy*dy + dz*dz
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = (path_idx, i, q)
        return best

    def _nearest_saved_segment(self, p: AllplanGeo.Point3D, tol_mult: float = 1.5):
        max_d2 = (HIT_TOL_SEGMENT * tol_mult) ** 2
        best = None
        best_q = None
        best_d2 = max_d2 + 1.0

        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) < 2:
                continue
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i+1]
                _, q = self._segment_project_point(a, b, p)
                dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                d2 = dx*dx + dy*dy + dz*dz
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = ('saved', path_idx, i)
                    best_q = q

        return (best, best_q)

    def _seg_equal(self, a, b) -> bool:
        if a is None or b is None: return False
        return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

    def _clear_selection_if_invalid(self):
        sel = self.selected_seg
        if sel is None: return
        kind, path_idx, seg_idx = sel
        if kind == 'active':
            if seg_idx < 0 or seg_idx >= max(0, len(self.points) - 1): self.selected_seg = None
        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)): self.selected_seg = None
            else:
                pts = self.script_object.saved_paths[path_idx]
                if seg_idx < 0 or seg_idx >= max(0, len(pts) - 1): self.selected_seg = None

    def _point_in_rect_xy(self, p: AllplanGeo.Point3D, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> bool:
        xmin, xmax = (a.X, b.X) if a.X <= b.X else (b.X, a.X)
        ymin, ymax = (a.Y, b.Y) if a.Y <= b.Y else (b.Y, a.Y)
        return (xmin <= p.X <= xmax) and (ymin <= p.Y <= ymax)

    # ---------- Doble clic (extensión) ----------
    def _handle_double_click(self, p: AllplanGeo.Point3D):
        hp = self._find_hover_saved_point(p, only_extremes=True)
        if hp is None: return False
        pidx, vidx, anchor = hp
        if not (0 <= pidx < len(self.script_object.saved_paths)): return False
        pts = self.script_object.saved_paths[pidx]
        if not pts: return False
        if vidx == 0 or vidx == len(pts) - 1:
            side = 'start' if vidx == 0 else 'end'
            print(f"[INT] Doble clic extremo poly #{pidx} -> EXTENDER ({side}).")
            self._start_extension_from_endpoint(pidx, side, anchor)
            return True
        return False

    def _start_extension_from_endpoint(self, pidx: int, side: str, anchor: AllplanGeo.Point3D):
        if not self.create_mode:
            self.create_mode = True; print("[INT] Crear: ON (por extensión).")
        self.branch_mode = False
        self.extend_target = (pidx, side)
        self.points = [AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z)]
        self.current_point = AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z)
        self.hover_index = -1; self.drag_index = -1; self.is_dragging = False
        self.selected_seg = None; self.hover_seg = None
        self.insert_preview_p = None; self.insert_target = None; self.saved_hover_point = None
        self.hover_mid = None
        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

    # ---------- Entrada de mouse ----------
    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        self._sync_insert_mode_from_palette()
        current_pnt = self.coord_input.GetInputPoint(
            mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
        ).GetPoint()

        is_left = (getattr(mouse_msg, 'Button', 1) == 1)
        is_dbl  = bool(getattr(mouse_msg, 'DoubleClick', False))
        if is_left and is_dbl:
            if self._handle_double_click(current_pnt):
                self._draw_preview(current_pnt); return True

        if self.coord_input.IsMouseMove(mouse_msg):
            if self.is_dragging and 0 <= self.drag_index < len(self.points):
                self.points[self.drag_index] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.current_point = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.hover_index = -1; self.hover_seg = None; self.hover_mid = None
                self.insert_preview_p = None; self.insert_target = None; self.saved_hover_point = None
                self._clear_selection_if_invalid()
            elif (not self.create_mode) and self.saved_dragging is not None:
                pidx, vidx = self.saved_dragging
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.saved_hover_point = None; self.hover_mid = None; self.hover_seg = None
            else:
                # feedback extensión elegible
                self.extensible_extreme = None
                if self.create_mode and not self.points:
                    hp = self._find_hover_saved_point(current_pnt, only_extremes=True)
                    if hp is not None:
                        pidx, vidx, anchor = hp
                        pts = self.script_object.saved_paths[pidx]
                        if vidx == 0 or vidx == len(pts) - 1:
                            self.extensible_extreme = (pidx, vidx, anchor)

                self.hover_index = self._find_hover_index(current_pnt) if self.create_mode else -1
                self.hover_mid = None if self.hover_index != -1 else self._find_hover_midpoint(current_pnt)
                if self.create_mode:
                    self.hover_seg = None if (self.hover_index != -1 or self.hover_mid is not None) else self._find_hover_segment(current_pnt, preferred_kind='active')
                else:
                    self.hover_seg = None if (self.hover_mid is not None) else self._find_hover_segment(current_pnt, preferred_kind='saved')

                self.saved_hover_point = None
                if not self.create_mode and self.hover_mid is None and self.hover_seg is None:
                    self.saved_hover_point = self._find_hover_saved_point(current_pnt)

                if self.insert_mode and (self.hover_seg is not None) and (self.hover_mid is None):
                    a, b = self._get_segment_endpoints(self.hover_seg)
                    if a and b:
                        t, q = self._segment_project_point(a, b, current_pnt)
                        if self._can_insert_here(a, b, t):
                            self.insert_preview_p = q; self.insert_target = self.hover_seg
                        else:
                            self.insert_preview_p = None; self.insert_target = None
                else:
                    self.insert_preview_p = None; self.insert_target = None

            self._draw_preview(current_pnt); return True

        # Click simple
        if is_left and not is_dbl:
            if self.is_dragging:
                self.is_dragging = False; self.drag_index = -1
                self._clear_selection_if_invalid(); self._draw_preview(current_pnt); return True
            if self.saved_dragging is not None:
                self.saved_dragging = None; self._draw_preview(current_pnt); return True

            # Bifurcar (anclar)
            if self.branch_mode:
                self.hover_index = self._find_hover_index(current_pnt)
                self.hover_mid   = None if self.hover_index != -1 else self._find_hover_midpoint(current_pnt)
                self.hover_seg   = None if (self.hover_index != -1 or self.hover_mid is not None) else self._find_hover_segment(current_pnt, None)
                self.saved_hover_point = None if self.hover_index != -1 else self._find_hover_saved_point(current_pnt)

                anchor_pt = None
                if self.hover_index != -1:
                    anchor_pt = self.points[self.hover_index]
                elif self.saved_hover_point is not None:
                    anchor_pt = self.saved_hover_point[2]
                elif (self.hover_seg is not None or self.hover_mid is not None) and self.insert_mode:
                    if self.hover_mid is not None:
                        seg = (self.hover_mid[0], self.hover_mid[1], self.hover_mid[2]); q = self.hover_mid[3]
                        a, b = self._get_segment_endpoints(seg)
                        if a and b and self._can_insert_here(a, b, 0.5):
                            self._insert_on_segment(seg, q, keep_selection_left=True); anchor_pt = q
                    else:
                        a, b = self._get_segment_endpoints(self.hover_seg)
                        if a and b:
                            t, q = self._segment_project_point(a, b, current_pnt)
                            if self._can_insert_here(a, b, t):
                                self._insert_on_segment(self.hover_seg, q, keep_selection_left=True); anchor_pt = q

                if anchor_pt is not None:
                    print("[INT] Bifurcar: anclaje OK")
                    self._begin_new_branch_from(anchor_pt)
                    self.branch_mode = False
                    self.saved_hover_point = None; self.insert_preview_p = None; self.insert_target = None; self.hover_mid = None
                    self._draw_preview(current_pnt); return True

                self._draw_preview(current_pnt); return True

            # Crear=ON: preferencia extensión de extremo
            if self.create_mode:
                if hasattr(self, 'extensible_extreme') and self.extensible_extreme is not None and not self.points:
                    pidx, vidx, anchor = self.extensible_extreme
                    pts = self.script_object.saved_paths[pidx]
                    if vidx == 0 or vidx == len(pts) - 1:
                        side = 'start' if vidx == 0 else 'end'
                        print(f"[INT] Click extremo elegible poly #{pidx} -> EXTENSIÓN ({side})")
                        self._start_extension_from_endpoint(pidx, side, anchor)
                        self._draw_preview(current_pnt); return True

                self.hover_index = self._find_hover_index(current_pnt)
                if self.hover_index != -1:
                    self.is_dragging = True; self.drag_index = self.hover_index
                    self.points[self.drag_index] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                    self._clear_selection_if_invalid(); self._draw_preview(current_pnt); return True

                self.hover_mid = self._find_hover_midpoint(current_pnt)
                if self.hover_mid is not None:
                    kind, path_idx, seg_idx, mp = self.hover_mid
                    seg = (kind, path_idx, seg_idx)
                    a, b = self._get_segment_endpoints(seg)
                    if a and b and self._can_insert_here(a, b, 0.5):
                        self._insert_on_segment(seg, mp, keep_selection_left=True)
                        self.insert_preview_p = None; self.insert_target = None; self.hover_seg = None; self.hover_mid = None
                        self._draw_preview(current_pnt); return True

                self.hover_seg = self._find_hover_segment(current_pnt, preferred_kind='active')
                if self.hover_seg is not None:
                    a, b = self._get_segment_endpoints(self.hover_seg)
                    if self.insert_mode and a and b:
                        t, q = self._segment_project_point(a, b, current_pnt)
                        if self._can_insert_here(a, b, t):
                            self._insert_on_segment(self.hover_seg, q, keep_selection_left=True)
                            self.insert_preview_p = None; self.insert_target = None; self.hover_seg = None; self.hover_mid = None
                            self._draw_preview(current_pnt); return True
                    if not self.insert_mode:
                        if self._seg_equal(self.selected_seg, self.hover_seg): self.selected_seg = None
                        else: self.selected_seg = self.hover_seg
                        self._draw_preview(current_pnt); return True

                # click vacío -> agregar vértice a activa
                self.points.append(AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z))
                self.current_point = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self._clear_selection_if_invalid(); self._draw_preview(current_pnt); return True

            # Crear=OFF: edición guardadas
            self.saved_hover_point = self._find_hover_saved_point(current_pnt)
            if self.saved_hover_point is not None:
                pidx, vidx, _ = self.saved_hover_point
                self.saved_dragging = (pidx, vidx)
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self._draw_preview(current_pnt); return True

            self.hover_mid = self._find_hover_midpoint(current_pnt)
            if self.hover_mid is not None:
                kind, path_idx, seg_idx, mp = self.hover_mid
                seg = (kind, path_idx, seg_idx)
                a, b = self._get_segment_endpoints(seg)
                if a and b and self._can_insert_here(a, b, 0.5):
                    self._insert_on_segment(seg, mp, keep_selection_left=True)
                    self.insert_preview_p = None; self.insert_target = None; self.hover_seg = None; self.hover_mid = None
                    self._draw_preview(current_pnt); return True

            self.hover_seg = self._find_hover_segment(current_pnt, preferred_kind='saved')
            if self.hover_seg is not None:
                a, b = self._get_segment_endpoints(self.hover_seg)
                if self.insert_mode and a and b:
                    t, q = self._segment_project_point(a, b, current_pnt)
                    if self._can_insert_here(a, b, t):
                        self._insert_on_segment(self.hover_seg, q, keep_selection_left=True)
                        self.insert_preview_p = None; self.insert_target = None; self.hover_seg = None; self.hover_mid = None
                        self._draw_preview(current_pnt); return True
                if not self.insert_mode:
                    if self._seg_equal(self.selected_seg, self.hover_seg): self.selected_seg = None
                    else: self.selected_seg = self.hover_seg
                    print(f"[INT] Toggle selección seg guardado: {self.selected_seg}")
                    self._draw_preview(current_pnt); return True

            # marco de selección
            if not self.box_selecting:
                self.box_selecting = True
                self.box_start = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.box_curr = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
            else:
                if self.box_start is not None and self.box_curr is not None:
                    sel: Set[Tuple[str, int, int]] = set()
                    for pidx, pts in enumerate(self.script_object.saved_paths):
                        for seg_idx in range(len(pts) - 1):
                            a, b = pts[seg_idx], pts[seg_idx + 1]
                            if self._point_in_rect_xy(a, self.box_start, self.box_curr) and self._point_in_rect_xy(b, self.box_start, self.box_curr):
                                sel.add(('saved', pidx, seg_idx))
                    self.selected_segments = sel
                self.box_selecting = False; self.box_start = None; self.box_curr = None

            self._draw_preview(current_pnt); return True

        return True

    # ---------- Lógica de bifurcación ----------
    def _begin_new_branch_from(self, anchor: AllplanGeo.Point3D):
        if len(self.points) >= 2:
            self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points])
        self.points = [AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z)]
        self.current_point = AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z)
        self.hover_index = -1; self.drag_index = -1; self.is_dragging = False
        self.selected_seg = None; self.hover_seg = None
        self.insert_preview_p = None; self.insert_target = None; self.saved_hover_point = None; self.hover_mid = None
        self._clear_preview()

    # ---------- Inserción ----------
    def _get_segment_endpoints(self, seg: Tuple[str, int, int]):
        kind, path_idx, seg_idx = seg
        if kind == 'active':
            if len(self.points) >= 2 and 0 <= seg_idx < len(self.points) - 1:
                return self.points[seg_idx], self.points[seg_idx+1]
            return None, None
        if kind == 'saved':
            if 0 <= path_idx < len(self.script_object.saved_paths):
                pts = self.script_object.saved_paths[path_idx]
                if len(pts) >= 2 and 0 <= seg_idx < len(pts) - 1:
                    return pts[seg_idx], pts[seg_idx+1]
        return None, None

    def _can_insert_here(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, t: float) -> bool:
        seg_len = ((a.X-b.X)**2 + (a.Y-b.Y)**2 + (a.Z-b.Z)**2) ** 0.5
        if seg_len < MIN_SEG_LEN_MM: return False
        t_min = MAX_EPS(MIN_INSERT_OFFSET_MM / max(seg_len, 1e-6))
        return (t > t_min) and (t < 1.0 - t_min)

    def _insert_on_segment(self, seg: Tuple[str, int, int], q: AllplanGeo.Point3D, keep_selection_left: bool = True):
        kind, path_idx, seg_idx = seg
        if kind == 'active':
            if not (0 <= seg_idx < len(self.points) - 1): return
            self.points.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))
            if self.selected_seg and self.selected_seg[0] == 'active':
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = ('active', -1, seg_idx if keep_selection_left else seg_idx + 1)
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ('active', -1, self.selected_seg[2] + 1)
        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)): return
            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1): return
            pts.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))
            if self.selected_seg and self.selected_seg[0] == 'saved' and self.selected_seg[1] == path_idx:
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = ('saved', path_idx, seg_idx if keep_selection_left else seg_idx + 1)
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ('saved', path_idx, self.selected_seg[2] + 1)
        self.insert_preview_p = None; self.insert_target = None

    # ---------- Borrar secciones ----------
    def delete_selected_or_hovered_segment(self) -> bool:
        target = self.selected_seg if self.selected_seg is not None else self.hover_seg
        curr = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()

        if target is None:
            seg, _ = self._nearest_saved_segment(curr, tol_mult=1.75)
            if seg:
                target = seg

        if target is None:
            if len(self.script_object.saved_paths) == 1:
                pts = self.script_object.saved_paths[0]
                if len(pts) >= 2:
                    target = ('saved', 0, len(pts) - 2)

        if not target:
            print("[INT] Borrar: sin objetivo (no hay selección, ni hover, ni segmento cercano).")
            return False

        kind, path_idx, seg_idx = target
        print(f"[INT] Borrar -> objetivo: {target}")

        if kind == 'active':
            if len(self.points) < 2 or not (0 <= seg_idx < len(self.points) - 1):
                return False
            left  = self.points[:seg_idx+1]
            right = self.points[seg_idx+1:]
            if len(right) >= 2:
                self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])
            self.points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left]

        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False
            pts = self.script_object.saved_paths[path_idx]
            if len(pts) < 2 or not (0 <= seg_idx < len(pts) - 1):
                return False

            left  = pts[:seg_idx+1]
            right = pts[seg_idx+1:]
            new_paths: List[List[AllplanGeo.Point3D]] = []
            if len(left)  >= 2: new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left])
            if len(right) >= 2: new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])

            self.script_object.saved_paths.pop(path_idx)
            for offset, path in enumerate(new_paths):
                self.script_object.saved_paths.insert(path_idx + offset, path)
        else:
            return False

        self.selected_seg = None
        self.hover_seg = None
        self.insert_preview_p = None
        self.insert_target = None
        self.hover_mid = None

        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())
        return True

    # ---------- Guardar / Finalizar ----------
    def on_cancel_function(self):
        print("[INT] ESC/Finalizar: guardando y creando inmediatamente...")
        self.save_current_polyline()
        self.script_object._finalize_and_create_now()
        return OnCancelFunctionResult.CREATE_ELEMENTS

    def save_current_polyline(self):
        if self.extend_target is not None and len(self.points) >= 2:
            pidx, side = self.extend_target
            if 0 <= pidx < len(self.script_object.saved_paths):
                base = self.script_object.saved_paths[pidx]
                if side == 'end':
                    base.extend([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]])
                else:
                    prepend = list(reversed(self.points[1:]))
                    self.script_object.saved_paths[pidx] = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in prepend] + base
                print(f"[INT] Extensión fusionada en poly #{pidx} ({side}).")
            self.extend_target = None
        else:
            if len(self.points) >= 2:
                self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points])

        self.points.clear()
        self.hover_index = -1; self.drag_index  = -1; self.is_dragging = False
        self.hover_seg   = None; self.selected_seg= None
        self.insert_preview_p = None; self.insert_target = None
        self.saved_hover_point = None; self.hover_mid = None
        self._clear_preview()

    # ---------- Preview ----------
    def _clear_preview(self):
        elems: List[AllplanBasisElements.ModelElement3D] = []
        if self.script_object.saved_paths:
            saved_prop = self._clone_properties(self.com_prop); saved_prop.Color = SAVED_POLY_COLOR
            for pts in self.script_object.saved_paths:
                if len(pts) >= 2:
                    poly = AllplanGeo.Polyline3D()
                    for pt in pts: poly += pt
                    elems.append(AllplanBasisElements.ModelElement3D(saved_prop, poly))
        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            elems, False, None
        )

    def on_preview_draw(self):
        self._sync_insert_mode_from_palette()
        hover = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        self._draw_preview(hover)

    def on_mouse_leave(self):
        self.on_preview_draw()

    def _line_with_zbias(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, z_bias: float):
        pa = AllplanGeo.Point3D(a.X, a.Y, a.Z + z_bias)
        pb = AllplanGeo.Point3D(b.X, b.Y, b.Z + z_bias)
        return AllplanGeo.Line3D(pa, pb)

    def _draw_preview(self, hover: Optional[AllplanGeo.Point3D]):
        elems: List[AllplanBasisElements.ModelElement3D] = []

        base_prop   = self._clone_properties(self.com_prop)
        handle_prop = self._clone_properties(self.com_prop); handle_prop.Color = HANDLE_COLOR_IDX
        saved_prop  = self._clone_properties(self.com_prop); saved_prop.Color  = SAVED_POLY_COLOR

        seg_hover_prop = self._clone_properties(self.com_prop); seg_hover_prop.Color = SEGMENT_HOVER_COLOR
        seg_hover_prop.ColorByLayer = False; seg_hover_prop.PenByLayer = False; seg_hover_prop.StrokeByLayer = False
        try: seg_hover_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception: pass

        seg_sel_prop = self._clone_properties(self.com_prop); seg_sel_prop.Color = SEGMENT_SEL_COLOR
        seg_sel_prop.ColorByLayer = False; seg_sel_prop.PenByLayer = False; seg_sel_prop.StrokeByLayer = False
        try: seg_sel_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception: pass

        ins_prev_prop = self._clone_properties(self.com_prop); ins_prev_prop.Color = INSERT_PREVIEW_COLOR
        branch_anchor_prop = self._clone_properties(self.com_prop); branch_anchor_prop.Color = BRANCH_ANCHOR_COLOR

        mid_prop = self._clone_properties(self.com_prop); mid_prop.Color = MIDPOINT_COLOR
        mid_prop.PenByLayer = False; mid_prop.ColorByLayer = False; mid_prop.StrokeByLayer = False
        try: mid_prop.Pen = max(MIDPOINT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception: pass
        mid_size = HANDLE_SIZE * MIDPOINT_SIZE_FACTOR

        rect_prop = self._clone_properties(self.com_prop); rect_prop.Color = RECT_COLOR
        rect_prop.PenByLayer = False; rect_prop.ColorByLayer = False; rect_prop.StrokeByLayer = False
        try: rect_prop.Pen = max(RECT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception: pass

        ext_marker_size = HANDLE_SIZE * 1.25
        ext_marker_prop = self._clone_properties(self.com_prop); ext_marker_prop.Color = BRANCH_ANCHOR_COLOR
        ext_marker_prop.PenByLayer = False; ext_marker_prop.ColorByLayer = False; ext_marker_prop.StrokeByLayer = False
        try: ext_marker_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception: pass

        # guardadas
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) >= 2:
                poly = AllplanGeo.Polyline3D()
                for pt in pts: poly += pt
                elems.append(AllplanBasisElements.ModelElement3D(saved_prop, poly))

                selected_i = self.selected_seg[2] if (self.selected_seg and self.selected_seg[0] == 'saved' and self.selected_seg[1] == path_idx) else -1
                hovered_i  = self.hover_seg[2]    if (self.hover_seg    and self.hover_seg[0]    == 'saved' and self.hover_seg[1]    == path_idx) else -1

                if selected_i != -1 and 0 <= selected_i < len(pts) - 1:
                    a, b = pts[selected_i], pts[selected_i + 1]
                    elems.append(AllplanBasisElements.ModelElement3D(seg_sel_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)))

                if hovered_i != -1 and hovered_i != selected_i and 0 <= hovered_i < len(pts) - 1 and not self.is_dragging:
                    a, b = pts[hovered_i], pts[hovered_i + 1]
                    elems.append(AllplanBasisElements.ModelElement3D(seg_hover_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)))

                box_sel_prop = self._clone_properties(self.com_prop); box_sel_prop.Color = BOX_SELECTED_SEG_COLOR
                box_sel_prop.ColorByLayer = False; box_sel_prop.PenByLayer = False; box_sel_prop.StrokeByLayer = False
                try: box_sel_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
                except Exception: pass
                if hasattr(self, 'selected_segments') and self.selected_segments:
                    for si in range(len(pts) - 1):
                        if ('saved', path_idx, si) in self.selected_segments:
                            a, b = pts[si], pts[si + 1]
                            elems.append(AllplanBasisElements.ModelElement3D(box_sel_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)))

                # midpoints guardadas
                for si in range(len(pts) - 1):
                    a, b = pts[si], pts[si+1]
                    mp = self._midpoint(a, b)
                    if si == selected_i:
                        elems.extend(self._create_point_marker(mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    elif si == hovered_i and not self.is_dragging:
                        elems.extend(self._create_point_marker(mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    else:
                        elems.extend(self._create_point_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

                if hasattr(self, 'extensible_extreme') and self.extensible_extreme is not None:
                    pidx_e, vidx_e, anchor_e = self.extensible_extreme
                    if pidx_e == path_idx and (vidx_e == 0 or vidx_e == len(pts)-1):
                        elems.extend(self._create_point_marker(anchor_e, ext_marker_prop, ext_marker_size, z_bias=2.0))

        # activa
        if self.points:
            poly = AllplanGeo.Polyline3D()
            for pt in self.points: poly += pt
            if hover is not None and not self.is_dragging and self.hover_seg is None and self.create_mode:
                poly += hover
            elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))

            for idx, pt in enumerate(self.points):
                size = HANDLE_SIZE * 0.65
                if idx == self.hover_index and not self.is_dragging: size = HANDLE_SIZE * HOVER_SCALE
                if idx == self.drag_index and self.is_dragging:      size = HANDLE_SIZE * DRAG_SCALE
                elems.extend(self._create_point_marker(pt, handle_prop, size))

            selected_i = self.selected_seg[2] if (self.selected_seg and self.selected_seg[0] == 'active') else -1
            hovered_i  = self.hover_seg[2]    if (self.hover_seg    and self.hover_seg[0]    == 'active') else -1

            if selected_i != -1 and 0 <= selected_i < len(self.points) - 1:
                a, b = self.points[selected_i], self.points[selected_i+1]
                elems.append(AllplanBasisElements.ModelElement3D(seg_sel_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)))

            if self.hover_seg and self.hover_seg[0] == 'active' and not self.is_dragging:
                si = self.hover_seg[2]
                if si != selected_i and 0 <= si < len(self.points) - 1:
                    a, b = self.points[si], self.points[si+1]
                    elems.append(AllplanBasisElements.ModelElement3D(seg_hover_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)))

            if len(self.points) >= 2:
                for si in range(len(self.points) - 1):
                    a, b = self.points[si], self.points[si+1]
                    mp = self._midpoint(a, b)
                    if si == selected_i:
                        elems.extend(self._create_point_marker(mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    elif si == hovered_i and not self.is_dragging:
                        elems.extend(self._create_point_marker(mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    else:
                        elems.extend(self._create_point_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

        if self.insert_mode and self.insert_preview_p is not None and self.insert_target is not None:
            elems.extend(self._create_point_marker(self.insert_preview_p, ins_prev_prop, HANDLE_SIZE * 0.95))

        if self.branch_mode:
            if self.hover_index != -1 and self.create_mode:
                elems.extend(self._create_point_marker(self.points[self.hover_index], branch_anchor_prop, HANDLE_SIZE * 1.05))
            elif self.saved_hover_point is not None:
                elems.extend(self._create_point_marker(self.saved_hover_point[2], branch_anchor_prop, HANDLE_SIZE * 1.05))

        if self.box_selecting and self.box_start is not None and self.box_curr is not None:
            a = self.box_start; b = self.box_curr
            p1 = AllplanGeo.Point3D(a.X, a.Y, a.Z); p2 = AllplanGeo.Point3D(b.X, a.Y, a.Z)
            p3 = AllplanGeo.Point3D(b.X, b.Y, a.Z); p4 = AllplanGeo.Point3D(a.X, b.Y, a.Z)
            for (s, e) in [(p1,p2),(p2,p3),(p3,p4),(p4,p1)]:
                elems.append(AllplanBasisElements.ModelElement3D(rect_prop, AllplanGeo.Line3D(s, e)))

        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            elems, False, None
        )

    # ---------- Helpers ----------
    def _clone_properties(self, src_prop):
        dst = AllplanBaseElements.CommonProperties(); dst.GetGlobalProperties()
        for name in ("Color", "Pen", "Stroke", "ColorByLayer", "PenByLayer", "StrokeByLayer", "Layer"):
            try: setattr(dst, name, getattr(src_prop, name))
            except Exception: pass
        return dst

    def _create_point_marker(self, point, properties, size, z_bias: float = 0.0):
        half = size * 0.5
        px, py, pz = point.X, point.Y, point.Z + z_bias
        p1 = AllplanGeo.Point3D(px - half, py,        pz)
        p2 = AllplanGeo.Point3D(px + half, py,        pz)
        p3 = AllplanGeo.Point3D(px,        py - half, pz)
        p4 = AllplanGeo.Point3D(px,        py + half, pz)
        p5 = AllplanGeo.Point3D(px,        py,        pz - half)
        p6 = AllplanGeo.Point3D(px,        py,        pz + half)
        return [
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p1, p2)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p3, p4)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p5, p6)),
        ]
