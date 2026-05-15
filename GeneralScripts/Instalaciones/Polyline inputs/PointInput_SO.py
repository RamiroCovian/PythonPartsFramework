# -*- coding: utf-8 -*-
"""ScriptObject: captura puntos y traza polilíneas por Path.

- Auto-commit: en el click con PointRole == Final (3) crea:
    * UNA Polyline2D unificada por PathId (orden por seg_id y orden de captura)
    * UNA Polyline3D unificada por PathId (usa Z real)
    * Exporta JSON solo de ese PathId (merge por path_id)

- Fallback: on_cancel_function recorre todos los PathIds capturados y crea/expone lo mismo.
- Opcional: si existe el parámetro de paleta 'FinishNow' y se pone True, dispara el cierre del Path actual.

- Usa CoordinateInput (sin PolylineInput).
- JSON único en Escritorio: route_groups_XXXXXXXX.json (merge por path_id).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Tuple, Dict
from dataclasses import dataclass
from collections import defaultdict
import os, json, random, sys

import NemAll_Python_BaseElements  as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry      as AllplanGeometry
import NemAll_Python_IFW_Input     as AllplanIFW

from CreateElementResult import CreateElementResult
from BuildingElement     import BuildingElement
from BaseScriptObject    import BaseScriptObject, BaseScriptObjectData

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

JSON_PATH = os.path.join(_desktop_dir(), f"route_groups_{random.randint(0,999_999_999)}.json")
print("[BOOT] JSON_PATH =", JSON_PATH); _flush()


# -------------------- Datos --------------------
@dataclass
class Capture:
    p: AllplanGeometry.Point2D
    z: float
    color_id: int
    path_id: int
    seg_id: int
    role: int   # 0 Inicial, 1 Paso, 2 Bifurcación, 3 Final

ROLE_LABEL = {0: "Inicial", 1: "Paso", 2: "Bifurcacion", 3: "Final"}


# -------------------- Hooks Allplan --------------------
def check_allplan_version(_build_ele: BuildingElement, _version: float) -> bool:
    print(f"[CHECK VERSION] version={_version}"); _flush()
    return True

def create_script_object(build_ele: BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    print("[CREATE SO] build_ele:", type(build_ele).__name__); _flush()
    return PointInputSO(build_ele, script_object_data)


# -------------------- ScriptObject --------------------
class PointInputSO(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele  # type: ignore
        self._interactor: PointInputSOInteractor | None = None
        print("[SO.__init__] OK"); _flush()

    def start_input(self):
        print("[SO start_input] pyp:", getattr(self.build_ele, "pyp_file_name", "?"),
              "| py:", getattr(self.build_ele, "script_name", "?")); _flush()
        self._interactor = PointInputSOInteractor(self, self.build_ele)  # type: ignore
        self.script_object_interactor = self._interactor
        print("[SO start_input] interactor listo"); _flush()

    def start_next_input(self):
        print("[SO start_next_input] fin de interacción"); _flush()
        try:
            if self._interactor is not None:
                self._interactor._finish_all_paths(reason="start_next_input")
        except Exception as e:
            print("[SO start_next_input] finalize EXC:", e); _flush()
        self.script_object_interactor = None

    def execute(self) -> CreateElementResult:
        print("[SO execute] sin geometría final"); _flush()
        return CreateElementResult([])

    def modify_element_property(self, *args):
        print("[SO modify_element_property] args:", args); _flush()
        if len(args) == 2:
            name, value = args
        elif len(args) == 3:
            _page, name, value = args
        else:
            return False
        if self._interactor is not None:
            res = self._interactor.modify_element_property(name, value)
            print("[SO modify_element_property] →", res); _flush()
            return res
        return False


# -------------------- Interactor --------------------
class PointInputSOInteractor:
    def __init__(self, so: PointInputSO, build_ele: PointInputBuildingElement):
        self.so = so
        self.build_ele = build_ele
        self.coord_input: AllplanIFW.CoordinateInput | None = None
        self.input_pnt: AllplanGeometry.Point3D | None = None
        self.captures: List[Capture] = []
        print("[INT.__init__] listo:", type(build_ele).__name__); _flush()

    # Allplan te pasa el CoordinateInput
    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input or AllplanIFW.CoordinateInput()
        print("[INT.start_input] coord_input:", type(self.coord_input).__name__); _flush()

        def _v(name, default):
            try: return getattr(self.build_ele, name).value
            except Exception: return default

        ea = _v("EnableAssistWndClick", False)
        ez = _v("EnableZCoordinate", True)
        eu = _v("EnableUndoStep", False)
        sp = _v("SetProjectionBase0", True)

        print(f"[INT.start_input] flags AssistWnd={ea} Z={ez} Undo={eu} Proj0={sp}"); _flush()
        self.coord_input.EnableAssistWndClick(ea)
        self.coord_input.EnableZCoord(ez)
        self.coord_input.EnableUndoStep(eu)
        self.coord_input.SetProjectionBase0(sp)

        # sincroniza color en la paleta con el Path actual
        path = self._current_path(); print("[UTIL path] →", path); _flush()
        color = self._color_from_path(path); print("[UTIL color-from-path] path=", path, "→ color=", color); _flush()
        self._apply_color_to_commonprops(color)

        self.initialize_coord_input()

    # ---- eventos estándar ----
    def on_preview_draw(self):
        if self.coord_input: self.coord_input.GetCurrentPoint()

    def on_value_input_control_enter(self) -> bool:
        return True

    def process_mouse_msg(self, mouse_msg: int,
                          pnt: AllplanGeometry.Point2D,
                          msg_info: AllplanIFW.AddMsgInfo) -> bool:
        if not self.coord_input:
            print("[INT.process_mouse_msg] sin coord_input"); _flush()
            return True

        res = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info)
        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        self.input_pnt = res.GetPoint()
        if self.input_pnt is not None:
            role = self._current_role()
            path = self._current_path()
            seg  = self._current_segment()
            col  = self._color_from_path(path)  # color = PathId

            self.captures.append(
                Capture(
                    p        = AllplanGeometry.Point2D(self.input_pnt.X, self.input_pnt.Y),
                    z        = float(self.input_pnt.Z),
                    color_id = col,
                    path_id  = path,
                    seg_id   = seg,
                    role     = role,
                )
            )
            print(f"[CAP] #{len(self.captures)} role={role} path={path} seg={seg} z={self.input_pnt.Z}"); _flush()

            # --- AUTOCOMMIT AL MARCAR FINAL ---
            if role == 3:  # Final
                print(f"[AUTOCOMMIT] role=Final -> path {path}"); _flush()
                self._export_json_for_path(path)
                self._create_unified_polylines_for_path(path)

        # símbolo opcional
        if getattr(self.build_ele, "CreateSymbol", type("x", (), {"value": False})).value:
            self.create_point_symbol()

        self.initialize_coord_input()
        return True

    def on_mouse_leave(self):
        if self.coord_input: self.coord_input.GetCurrentPoint()

    def on_input_undo(self) -> bool:
        return True

    def on_cancel_function(self) -> bool:
        """ESC: recorre todos los paths y finaliza."""
        self._finish_all_paths(reason="ESC")
        self.so.start_next_input()
        return True

    # -------------------- Finalizaciones --------------------
    def _finish_all_paths(self, reason: str = "manual"):
        if not self.captures:
            print(f"[FINISH] {reason}: sin capturas"); _flush(); return
        pids = sorted({c.path_id for c in self.captures})
        print(f"[FINISH] {reason}: paths={pids}"); _flush()
        for pid in pids:
            self._export_json_for_path(pid)
            self._create_unified_polylines_for_path(pid)

    # -------------------- JSON: solo un path (merge) --------------------
    def _export_json_for_path(self, pid: int):
        print(f"[JSON] export path_id={pid} → {JSON_PATH}"); _flush()

        event = {"iniciales": [], "intermedios": [], "finales": []}
        for c in self.captures:
            if c.path_id != pid:
                continue
            pt = {
                "x": float(round(c.p.X, 3)),
                "y": float(round(c.p.Y, 3)),
                "z": float(round(c.z, 3)),
                "segmento": int(c.seg_id),
                "tipo": ROLE_LABEL.get(c.role, "Paso"),
                "color": int(c.color_id)
            }
            if c.role == 0:   event["iniciales"].append(pt)
            elif c.role == 3: event["finales"].append(pt)
            else:             event["intermedios"].append(pt)

        # leer/merge existente
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = []
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
                dst[k] = (dst.get(k) or []) + event[k]
        else:
            index[pid] = {"path_id": pid, **event}

        out_list = [index[k] for k in sorted(index.keys())]
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(out_list, f, ensure_ascii=False, indent=2)
            print(f"[JSON] OK path_id={pid} (len={len(out_list)})"); _flush()
        except Exception as e:
            print("[JSON] ERROR escritura:", e); _flush()

    # -------------------- Crear polilíneas unificadas (2D + 3D) --------------------
    def _create_unified_polylines_for_path(self, pid: int):
        """Crea N polilíneas (2D y 3D) para un mismo PathId, una por cada
        secuencia delimitada por roles: Inicial ... Final. Usa el orden REAL
        de captura (no por seg_id)."""
        try:
            # Filtrar manteniendo el orden de captura
            caps = [(i, c) for i, c in enumerate(self.captures) if c.path_id == pid]
            if not caps:
                print(f"[RUN] path {pid} sin capturas -> skip"); _flush(); return

            elems: list[Any] = []
            cp = self._clone_common_with_color(self._color_from_path(pid))

            run2: list[AllplanGeometry.Point2D] = []
            run3: list[AllplanGeometry.Point3D] = []
            run_idx = 0

            def dedupe2(pts: list[AllplanGeometry.Point2D]) -> list[AllplanGeometry.Point2D]:
                out: list[AllplanGeometry.Point2D] = []
                for q in pts:
                    if not out or out[-1].X != q.X or out[-1].Y != q.Y:
                        out.append(q)
                return out

            def dedupe3(pts: list[AllplanGeometry.Point3D]) -> list[AllplanGeometry.Point3D]:
                out: list[AllplanGeometry.Point3D] = []
                for q in pts:
                    if not out or out[-1].X != q.X or out[-1].Y != q.Y or out[-1].Z != q.Z:
                        out.append(q)
                return out

            def flush_run():
                nonlocal run2, run3, run_idx, elems
                run2 = dedupe2(run2)
                run3 = dedupe3(run3)
                if len(run2) >= 2:
                    pl2d = AllplanGeometry.Polyline2D()
                    for q in run2: pl2d += q
                    elems.append(AllplanBasisElements.ModelElement2D(cp, pl2d))
                    print(f"[RUN {run_idx}] Polyline2D path={pid} npts={len(run2)}")
                if len(run3) >= 2:
                    pl3d = AllplanGeometry.Polyline3D()
                    for q in run3: pl3d += q
                    elems.append(AllplanBasisElements.ModelElement3D(cp, pl3d))
                    print(f"[RUN {run_idx}] Polyline3D path={pid} npts={len(run3)}")
                run2, run3 = [], []
                run_idx += 1

            # Recorremos por orden de captura y cortamos por roles
            for _, c in caps:
                if c.role == 0:  # Inicial → empezar nueva corrida
                    if run2 or run3:
                        flush_run()
                    run2 = [c.p]
                    run3 = [AllplanGeometry.Point3D(c.p.X, c.p.Y, c.z)]
                elif c.role in (1, 2):  # Paso / Bifurcación
                    if not run2:  # si llega un Paso antes de un Inicial, abrimos con él
                        run2 = [c.p]
                        run3 = [AllplanGeometry.Point3D(c.p.X, c.p.Y, c.z)]
                    else:
                        run2.append(c.p)
                        run3.append(AllplanGeometry.Point3D(c.p.X, c.p.Y, c.z))
                elif c.role == 3:  # Final → cerrar corrida
                    if not run2:  # Final sin inicio previo: creamos corrida mínima
                        run2 = [c.p]
                        run3 = [AllplanGeometry.Point3D(c.p.X, c.p.Y, c.z)]
                    else:
                        run2.append(c.p)
                        run3.append(AllplanGeometry.Point3D(c.p.X, c.p.Y, c.z))
                    flush_run()

            # Si quedó una corrida abierta sin Final, la cerramos igual
            if run2 or run3:
                flush_run()

            self._commit_elements(elems, tag=f"[RUNS path={pid}]")
        except Exception as e:
            print(f"[RUN] EXC path={pid}:", e); _flush()

    # -------------------- Utils de geometría/commit --------------------
    def _clone_common_with_color(self, color_id: int):
        """
        Clona CommonProperties a partir de la paleta (CommonProp.value). Evita depender de
        AllplanBasisElements.CommonProperties() si no está exportado en este entorno.
        """
        base = None
        try:
            base = getattr(getattr(self.build_ele, "CommonProp", None), "value", None)
            if base is None:
                base = getattr(getattr(self.build_ele, "SymbolCommonProps", None), "value", None)
        except Exception:
            base = None

        if base is None:
            print("[CP] WARNING: no base CommonProp; devolveré None"); _flush()
            return None  # CreateElements aceptará None → usa defaults del doc

        # intentar clonar usando la propia clase del objeto base
        try:
            cp_new = base.__class__()  # robusto ante cambios de módulo/clase
        except Exception:
            cp_new = None

        target = cp_new if cp_new is not None else base  # fallback: usar la misma instancia

        # copiar atributos "típicos" si existen
        for attr in ("Pen", "Stroke", "LineStyle", "Layer", "Transparency", "DrawOrder", "Fill", "Color"):
            try:
                setattr(target, attr, getattr(base, attr))
            except Exception:
                pass

        # aplicar color deseado
        try:
            target.Color = color_id
        except Exception:
            pass

        if cp_new is None:
            print("[CP] Fallback: usando CommonProp original (no clonado)"); _flush()
        return target

    def _commit_elements(self, elems: List[Any], tag: str = "[GEOM]"):
        if not elems:
            print(f"{tag} nada para crear"); _flush(); return
        doc = None
        try:
            doc = self.coord_input.GetInputViewDocument() if self.coord_input else None
        except Exception as e:
            print(f"{tag} GetInputViewDocument EXC:", e); _flush()
        if not doc:
            print(f"{tag} sin DocumentAdapter -> no puedo crear elementos"); _flush(); return
        try:
            AllplanBaseElements.CreateElements(
                doc,
                AllplanGeometry.Matrix3D(),
                elems, [], None
            )
            print(f"{tag} creados: {len(elems)}"); _flush()
        except Exception as e:
            print(f"{tag} CreateElements EXC:", e); _flush()

    # -------------------- Modificación de propiedades --------------------
    def modify_element_property(self, *args):
        print("[INT.modify_element_property] args:", args); _flush()
        if len(args) == 2:
            name, value = args
        elif len(args) == 3:
            _page, name, value = args
        else:
            return False

        if not self.coord_input:
            print("[INT.modify_element_property] sin coord_input"); _flush()
            return False

        if name == "EnableAssistWndClick":
            self.coord_input.EnableAssistWndClick(value)
        elif name == "EnableZCoordinate":
            self.coord_input.EnableZCoord(value)
        elif name == "EnableUndoStep":
            self.coord_input.EnableUndoStep(value)
        elif name == "SetProjectionBase0":
            self.coord_input.SetProjectionBase0(value)
        elif name == "PathId":
            try: path = max(1, int(value))
            except Exception: path = self._current_path()
            new_col = self._color_from_path(path)
            self._apply_color_to_commonprops(new_col)
            self.initialize_coord_input()
            return True
        elif name == "FinishNow" and bool(value):
            pid = self._current_path()
            print(f"[FinishNow] pid={pid}"); _flush()
            self._export_json_for_path(pid)
            self._create_unified_polylines_for_path(pid)
            return True
        else:
            # Nota: PointRole/SegmentId no necesitan tratamiento aquí; se leen al vuelo.
            print(f"[INT.modify_element_property] no tratado: {name} = {value}")
        self.initialize_coord_input()
        return True

    # -------------------- Setup input --------------------
    def initialize_coord_input(self):
        if not self.coord_input:
            print("[INT.initialize_coord_input] sin coord_input"); _flush(); return
        prompt_msg = AllplanIFW.InputStringConvert(
            "Input first point" if self.input_pnt is None else "Input next point"
        )
        input_mode = AllplanIFW.CoordinateInputMode(
            identMode       = AllplanIFW.eIdentificationMode.names["eIDENT_POINT"],
            drawPointSymbol = AllplanIFW.eDrawElementIdentPointSymbols.names["eDRAW_IDENT_ELEMENT_POINT_SYMBOL_YES"]
        )
        if self.input_pnt is None:
            self.coord_input.InitFirstPointInput(prompt_msg, input_mode)
        else:
            self.coord_input.InitNextPointInput(prompt_msg, input_mode)

    # -------------------- Utilidades varias --------------------
    def _apply_color_to_commonprops(self, color_id: int):
        try:
            cp = getattr(self.build_ele, "CommonProp").value
            if getattr(cp, "Color", None) != color_id:
                cp.Color = color_id
                getattr(self.build_ele, "CommonProp").value = cp
                print("[SYNC] CommonProp.Color ->", color_id)
        except Exception:
            pass

        try:
            scp = getattr(self.build_ele, "SymbolCommonProps").value
            if getattr(scp, "Color", None) != color_id:
                scp.Color = color_id
                getattr(self.build_ele, "SymbolCommonProps").value = scp
                print("[SYNC] SymbolCommonProps.Color ->", color_id)
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
            if isinstance(val, (int, float)):
                return max(0, min(int(val), 3))
            mapping = {"Inicial": 0, "Paso": 1, "Bifurcacion": 2, "Final": 3}
            return mapping.get(str(val), 0)
        except Exception:
            return 0

    def _current_path(self) -> int:
        try: return max(1, int(getattr(self.build_ele, "PathId").value))
        except Exception: return 1

    def _current_segment(self) -> int:
        try: return max(1, int(getattr(self.build_ele, "SegmentId").value))
        except Exception: return 1

    def create_point_symbol(self):
        if self.input_pnt is None or not self.coord_input: return
        symbol_props = AllplanBasisElements.Symbol3DProperties()
        symbol_props.IsScaleDependent = False  # type: ignore
        symbol_props.SymbolID         = 1      # type: ignore
        common_props = getattr(getattr(self.build_ele, "SymbolCommonProps", None), "value",
                               getattr(self.build_ele, "CommonProp").value)
        AllplanBaseElements.CreateElements(
            self.coord_input.GetInputViewDocument(),
            AllplanGeometry.Matrix3D(),
            [AllplanBasisElements.Symbol3DElement(common_props, symbol_props, self.input_pnt)], [], None
        )
