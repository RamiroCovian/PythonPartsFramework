# -*- coding: utf-8 -*-
"""
ElementPoint – Captura/edición de caminos con asociación a elementos definidos (Allplan PythonPart).

Qué hace
--------
- Permite capturar puntos con rol (Inicial, Paso, Bifurcación, Final) **asociados a un elemento lógico** (interruptor,
  enchufe, luminaria, caja de conexiones, etc.).
- Valida que el rol sea compatible con el elemento elegido según un **catálogo** configurable en este archivo.
- Al marcar rol "Final" crea la polilínea del camino actual y persiste la información a un JSON en el Escritorio.
- Incluye editor con preview (mover vértices, insertar, eliminar, bifurcar, extender).

Requisitos de la paleta (.pyp)
------------------------------
- ElementKey (String/List)   -> clave del elemento elegido (p.ej. "switch","outlet","luminaire","junction_box")
- ElementName (String)       -> etiqueta visible del elemento (opcional; si no, se deduce del catálogo)
- PathId, SegmentId, PointRole (Integer) con los mismos significados que en CommonPoint.py
- CheckBoxValue (CheckBox)   -> modo insertar punto (True/False)
- CommonProp, SymbolCommonProps (CommonProperties)
- Botones de evento:
  - 2100..2103 -> setear rol (Inicial, Paso, Bifurcación, Final)
  - 1001       -> crear (toggle)
  - 1002       -> guardar polilínea activa
  - 1003       -> finalizar y crear todo lo pendiente
  - 1004       -> borrar sección seleccionada
  - 1006       -> bifurcar

Notas
-----
- Tolerancia por defecto: 5 mm para detección de vértices/segmentos.
- El marcador del punto es un **cuadrado** (placeholder) centrado en el punto.
- La persistencia se hace en JSON: element_points_XXXXXXXX.json en el Escritorio del usuario.
- Si el rol seleccionado **no** es compatible con el elemento elegido, se forzará al primer rol permitido y se informará
  en consola para evitar estados inválidos en la captura.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
import os, json, random, sys

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

# ------------------ Catálogo de elementos y roles permitidos ------------------
# Definí acá las claves y qué roles aceptan (0 Inicial, 1 Paso, 2 Bifurcación, 3 Final).
ELEMENT_CATALOG: Dict[str, Dict[str, Any]] = {
    "switch":       {"label": "Interruptor",   "allowed_roles": [3]},
    "outlet":       {"label": "Enchufe",       "allowed_roles": [3]},
    "luminaire":    {"label": "Luminaria",     "allowed_roles": [3]},
    "junction_box": {"label": "Caja conexiones","allowed_roles": [0,1,2,3]},
    "panel":        {"label": "Tablero",       "allowed_roles": [0,1,2,3]},
}

DEFAULT_ELEMENT_KEY = "junction_box"

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

JSON_PATH = os.path.join(_desktop_dir(), f"element_points_{random.randint(0,999_999_999)}.json")
print("[BOOT] JSON_PATH =", JSON_PATH); _flush()

# tolerancias (mm)
HIT_TOL_VERTEX   = 5.0
HIT_TOL_SEGMENT  = 5.0 * 1.6  # un poco más amplio para segmentos

# -------------------- Datos captura --------------------
@dataclass
class Capture:
    p: AllplanGeo.Point3D
    color_id: int
    path_id: int
    seg_id: int
    role: int                 # 0 Inicial, 1 Paso, 2 Bifurcación, 3 Final
    element_key: str          # clave del elemento
    element_label: str        # etiqueta legible

# -------------------- Hooks Allplan --------------------
def check_allplan_version(_build_ele: BuildingElement, _version: float) -> bool:
    print(f"[CHECK VERSION] version={_version}"); _flush()
    return True

def create_script_object(build_ele: BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    return UnifiedScriptObject(build_ele, script_object_data)

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
        print("[SO] start_input -> CAPTURA por defecto, editor en botones 100x")
        self._ensure_capture()

    def start_next_input(self):
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

        # Botones de rol
        if event_id in (2100, 2101, 2102, 2103):
            self._ensure_capture()
            mapping = {2100: 0, 2101: 1, 2102: 2, 2103: 3}
            return self._set_point_role(mapping[event_id])

        # Editor
        self._ensure_editor()
        if event_id == 1001:  self._edit.toggle_create_mode();  return True
        if event_id == 1002:  self._edit.save_current_polyline(); print(f"[SO] Guardadas: {len(self.saved_paths)}"); return True
        if event_id == 1003:
            print("[SO] Finalizar -> guardar y crear inmediatamente")
            self._edit.save_current_polyline(); self._finalize_and_create_now()
            # cerrar interacción
            for meth_name in ("CancelFunction", "OnCancelFunction", "CancelInput", "Cancel"):
                meth = getattr(self.coord_input, meth_name, None)
                if callable(meth):
                    try: meth(); break
                    except Exception as ex: print(f"[SO] coord_input.{meth_name}() ex: {ex}")
            return True
        if event_id == 1004:
            # placeholders de edición avanzada; puede ampliarse como en CommonPoint
            return True
        if event_id == 1006:  # bifurcar (placeholder en esta versión)
            self._edit.toggle_create_mode(); return True
        return False

    def _set_point_role(self, r: int) -> bool:
        try:
            r = max(0, min(int(r), 3))
            # Validar con el elemento actual:
            key, label, allowed = self._current_element_info()
            if r not in allowed:
                new_r = allowed[0]
                print(f"[SO] PointRole {r} no permitido para '{label}'. Se fuerza a {new_r}.")
                r = new_r
            getattr(self.build_ele, "PointRole").value = r
            if self._cap: self._cap._init_coord_prompt()
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

    def _finalize_and_create_now(self):
        if not self.saved_paths: return
        com_prop = AllplanBaseElements.CommonProperties(); com_prop.GetGlobalProperties()
        doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        for pts in self.saved_paths:
            if len(pts) < 2: continue
            h = self._hash_pts(pts)
            if h in self._created_hashes: continue
            pl = AllplanGeo.Polyline3D()
            for p in pts: pl += p
            AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(),
                                               [AllplanBasisElements.ModelElement3D(com_prop, pl)], [], None)
            self._created_hashes.add(h)

    # ---------- elemento actual ----------
    def _current_element_info(self) -> Tuple[str, str, List[int]]:
        key = None
        try:
            val = getattr(self.build_ele, "ElementKey", None)
            key = str(val.value if hasattr(val, "value") else val).strip() or None
        except Exception:
            pass
        if not key or key not in ELEMENT_CATALOG:
            key = DEFAULT_ELEMENT_KEY
        item = ELEMENT_CATALOG.get(key, {})
        label = item.get("label", key)
        allowed = list(item.get("allowed_roles", [0,1,2,3]))
        if not allowed: allowed = [1]
        return key, label, allowed

# -------------------- Interactor de CAPTURA --------------------
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

        # sincroniza color
        path = self._current_path()
        col  = self._color_from_path(path)
        self._apply_color_to_commonprops(col)
        self._init_coord_prompt()

    def _init_coord_prompt(self):
        if not self.coord_input: return
        try:
            r = self._current_role()
            msg_role = {0:"Inicial",1:"Paso",2:"Bifurcación",3:"Final"}.get(r, "Paso")
            key, label, allowed = self.so._current_element_info()
            msg_role += f" | Elem: {label} (permitidos: {allowed})"
        except Exception:
            msg_role = "Paso"
        prompt = AllplanIFW.InputStringConvert(f"Click ({msg_role}). Rol y Elemento desde paleta.")
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
            self.coord_input.GetCurrentPoint()  # no preview específico

    def on_mouse_leave(self):
        if self.coord_input:
            self.coord_input.GetCurrentPoint()

    def on_input_undo(self) -> bool: return True
    def on_value_input_control_enter(self) -> bool: return True

    def on_cancel_function(self) -> bool:
        print("[CAP] ESC -> cerrar corridas abiertas + export all"); _flush()
        try:
            self._export_json_all_paths()
            self._close_runs_to_saved_paths(create_now=True)
        except Exception as e:
            print("[CAP] ESC EXC:", e)
        return True

    def process_mouse_msg(self, mouse_msg: int,
                          pnt: AllplanGeo.Point2D,
                          msg_info: AllplanIFW.AddMsgInfo) -> bool:
        if not self.coord_input: return True
        res = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info)
        if self.coord_input.IsMouseMove(mouse_msg): return True

        self.input_pnt = res.GetPoint()
        if self.input_pnt is not None:
            role = self._current_role()
            path = self._current_path()
            seg  = self._current_segment()
            col  = self._color_from_path(path)
            key, label, allowed = self.so._current_element_info()
            if role not in allowed:
                print(f"[CAP] Rol {role} no permitido para '{label}', se fuerza a {allowed[0]}")
                role = allowed[0]

            self.captures.append(
                Capture(
                    p=AllplanGeo.Point3D(self.input_pnt.X, self.input_pnt.Y, self.input_pnt.Z),
                    color_id=col, path_id=path, seg_id=seg, role=role,
                    element_key=key, element_label=label
                )
            )
            self._create_square_marker(self.input_pnt, col)
            print(f"[CAP] #{len(self.captures)} role={role} elem={label} path={path} seg={seg}"); _flush()

            if role == 3:
                print(f"[CAP] Final -> export JSON y cerrar corrida (path {path})"); _flush()
                self._export_json_for_path(path)
                self._close_runs_to_saved_paths(pid=path, create_now=True)

        self._init_coord_prompt()
        return True

    # ---- cierre / creación de corridas ----
    def _close_runs_to_saved_paths(self, pid: Optional[int] = None, create_now: bool = False):
        if not self.captures: return
        doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        paths = [pid] if pid is not None else sorted({c.path_id for c in self.captures})

        for cur in paths:
            caps = [c for c in self.captures if c.path_id == cur]
            if not caps: continue

            run3: List[AllplanGeo.Point3D] = []
            def flush_run():
                nonlocal run3
                if len(run3) >= 2:
                    self.so.add_saved_path(run3, mark_created=create_now)
                    if create_now and doc is not None:
                        try:
                            com_prop = AllplanBaseElements.CommonProperties(); com_prop.GetGlobalProperties()
                            com_prop.Color = self._color_from_path(cur)
                            pl = AllplanGeo.Polyline3D()
                            for p in run3: pl += p
                            AllplanBaseElements.CreateElements(
                                doc, AllplanGeo.Matrix3D(),
                                [AllplanBasisElements.ModelElement3D(com_prop, pl)],
                                [], None
                            )
                        except Exception as e:
                            print("[CREATE] EXC creando polilínea:", e)
                run3 = []

            for c in caps:
                if c.role == 0:
                    if run3: flush_run()
                    run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                elif c.role in (1, 2):
                    if not run3: run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                    else: run3.append(AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z))
                elif c.role == 3:
                    if not run3: run3 = [AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z)]
                    else: run3.append(AllplanGeo.Point3D(c.p.X, c.p.Y, c.p.Z))
                    flush_run()

            if run3 and create_now: flush_run()

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
                "segmento": int(c.seg_id),
                "tipo": {0:"Inicial",1:"Paso",2:"Bifurcacion",3:"Final"}.get(c.role, "Paso"),
                "color": int(c.color_id),
                "element": {"key": c.element_key, "label": c.element_label}
            }
            if c.role == 0:   evento["iniciales"].append(pt)
            elif c.role == 3: evento["finales"].append(pt)
            else:             evento["intermedios"].append(pt)

        # merge
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f: data = json.load(f)
            if not isinstance(data, list): data = []
        except Exception: data = []

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
        except Exception: pass
        try:
            scp = getattr(self.build_ele, "SymbolCommonProps").value
            if getattr(scp, "Color", None) != color_id:
                scp.Color = color_id
                getattr(self.build_ele, "SymbolCommonProps").value = scp
        except Exception: pass
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

    # marcador cuadrado centrado en p (placeholder de 50 mm)
    def _create_square_marker(self, p: AllplanGeo.Point3D, color_id: int, size: float = 50.0):
        if not self.coord_input or p is None: return
        half = size * 0.5
        px, py, pz = p.X, p.Y, p.Z
        pts = [
            AllplanGeo.Point3D(px - half, py - half, pz),
            AllplanGeo.Point3D(px + half, py - half, pz),
            AllplanGeo.Point3D(px + half, py + half, pz),
            AllplanGeo.Point3D(px - half, py + half, pz),
            AllplanGeo.Point3D(px - half, py - half, pz),
        ]
        poly = AllplanGeo.Polyline3D()
        for q in pts: poly += q
        try:
            common_props = getattr(getattr(self.build_ele, "SymbolCommonProps", None), "value",
                                   getattr(self.build_ele, "CommonProp").value)
            common_props.Color = color_id
            AllplanBaseElements.CreateElements(
                self.coord_input.GetInputViewDocument(),
                AllplanGeo.Matrix3D(),
                [AllplanBasisElements.ModelElement3D(common_props, poly)], [], None
            )
        except Exception as e:
            print("[MARKER] EXC:", e); _flush()

# -------------------- EDITOR (preview) --------------------
# Editor compacto con creación y preview de polilíneas.
SAVED_POLY_COLOR = 3

class PolylineInteractor:
    def __init__(self, script_object: UnifiedScriptObject):
        self.script_object = script_object
        self.create_mode = False
        self.points: List[AllplanGeo.Point3D] = []
        self.current_point = AllplanGeo.Point3D()
        self.com_prop = AllplanBaseElements.CommonProperties(); self.com_prop.GetGlobalProperties()

    def start_input(self, coord_input):
        self.coord_input = coord_input
        self._print_prompt()

    def _print_prompt(self):
        msg = ("[Crear: %s] Clic para definir vértices; 1002=guardar, ESC/1003=finalizar"
               % ("ON" if self.create_mode else "OFF"))
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))

    def toggle_create_mode(self):
        self.create_mode = not self.create_mode
        if not self.create_mode: self.save_current_polyline()
        self._print_prompt()
        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        current_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point, bool(self.points)).GetPoint()
        if self.coord_input.IsMouseMove(mouse_msg):
            self._draw_preview(current_pnt); return True
        if self.create_mode:
            self.points.append(AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z))
            self.current_point = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
        self._draw_preview(current_pnt); return True

    def save_current_polyline(self):
        if len(self.points) >= 2:
            self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points])
        self.points.clear()
        self._clear_preview()

    def on_preview_draw(self):
        hover = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        self._draw_preview(hover)

    def on_mouse_leave(self): self.on_preview_draw()

    def on_cancel_function(self):
        print("[INT] ESC/Finalizar: guardando y creando inmediatamente...")
        self.save_current_polyline()
        self.script_object._finalize_and_create_now()
        return OnCancelFunctionResult.CREATE_ELEMENTS

    def _clear_preview(self):
        elems: List[AllplanBasisElements.ModelElement3D] = []
        if self.script_object.saved_paths:
            saved_prop = self._clone_properties(self.com_prop); saved_prop.Color = SAVED_POLY_COLOR
            for pts in self.script_object.saved_paths:
                if len(pts) >= 2:
                    poly = AllplanGeo.Polyline3D()
                    for pt in pts: poly += pt
                    elems.append(AllplanBasisElements.ModelElement3D(saved_prop, poly))
        AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(), AllplanGeo.Matrix3D(), elems, False, None)

    def _draw_preview(self, hover: Optional[AllplanGeo.Point3D]):
        elems: List[AllplanBasisElements.ModelElement3D] = []
        base_prop   = self._clone_properties(self.com_prop)
        saved_prop  = self._clone_properties(self.com_prop); saved_prop.Color  = SAVED_POLY_COLOR

        for pts in self.script_object.saved_paths:
            if len(pts) >= 2:
                poly = AllplanGeo.Polyline3D()
                for pt in pts: poly += pt
                elems.append(AllplanBasisElements.ModelElement3D(saved_prop, poly))

        if self.points:
            poly = AllplanGeo.Polyline3D()
            for pt in self.points: poly += pt
            if hover is not None:
                poly += hover
            elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))

        AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(), AllplanGeo.Matrix3D(), elems, False, None)

    def _clone_properties(self, src_prop):
        dst = AllplanBaseElements.CommonProperties(); dst.GetGlobalProperties()
        for name in ("Color", "Pen", "Stroke", "ColorByLayer", "PenByLayer", "StrokeByLayer", "Layer"):
            try: setattr(dst, name, getattr(src_prop, name))
            except Exception: pass
        return dst
