from __future__ import annotations

import math, json, time

from collections import defaultdict
from typing import TYPE_CHECKING, Optional, List, Any, Tuple, Dict, Set

if TYPE_CHECKING:
    from .script_object import PolylineScriptObject

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BaseElements as AllplanBaseElements
    import NemAll_Python_BasisElements as AllplanBasisElements
    import NemAll_Python_IFW_Input as AllplanIFW
    import NemAll_Python_Utility as PythonUtility
    ALLPLAN_AVAILABLE = True
except Exception:
    ALLPLAN_AVAILABLE = False

from NemAll_Python_BaseElements import AttributeService
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

from .models import (
    PolylineBaseConfig, SegmentData, SegmentItem, InstallationElement, AppliedLayer, ElementTypes, SegmentInfo, WaterTypes
)
from .parameters import ParamNames, PointModeValues
from .utils import ElementSerializer

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

# User prompt message (can be modified by installation scripts)
DEFAULT_USER_PROMPT = "Click to add points, right-click to finish. ESC to cancel."
# ─────────────────── Parámetros de Interacción ───────────────────

SNAP_SIZE = 70.0 # mm - tamaño del snap
HANDLE_SIZE = 70.0  # mm - tamaño de los handles de vértices
HIT_TOL_VERTEX = 50.0  # mm - tolerancia de captura de puntos
HIT_TOL_SEGMENT = 50.0  # mm - tolerancia de captura de segmentos
HIT_TOL_MIDPOINT = 50.0  # mm - tolerancia de captura de puntos medios

# ─────────────────── Factores de Escala Visual ───────────────────

HOVER_SCALE = 1.25  # factor de escala para hover
DRAG_SCALE = 1.5  # factor de escala durante drag
MIDPOINT_SIZE_FACTOR = 0.90  # tamaño relativo al HANDLE_SIZE

# ─────────────────── Parámetros de Inserción ───────────────────

MIN_INSERT_OFFSET_MM = 2.0  # mm - distancia mínima a extremos para insertar
MIN_SEG_LEN_MM = 1.0  # mm - evitar segmentos casi nulos

# ─────────────────── Parámetros de Visualización ───────────────────

SEGMENT_OVERLAY_Z_BIAS = 1.0  # mm - offset Z para segmentos resaltados
MIDPOINT_Z_BIAS = 1.0  # mm - offset Z para puntos medios
SEGMENT_OVERLAY_PEN = 13  # grosor para segmentos resaltados
MIDPOINT_PEN = 13  # grosor para puntos medios
RECT_PEN = 12  # grosor del marco de selección

INSERT_PREVIEW_COLOR = 6  # cyan for ghost point
MIDPOINT_COLOR = 4  # neutral color for midpoint markers
# ─────────────────── Paleta de colores (por índice Allplan) ───────────────────
COLORS = {
    "handle": 2,  # amarillo - handles de vértices
    "preview_saved": 69,  # verde - polilíneas guardadas en preview
    "midpoint": 4,  # neutro - marcadores de punto medio
    "segment_selected": 5,  # azul - segmento seleccionado
    "vertex_selected": 5,  # azul - vértices seleccionados
    "insert_preview": 6,  # cian - punto fantasma de inserción
    "segment_hover": 1,  # rojo - segmento bajo mouse
    "branch_anchor": 7,  # magenta - preview de anclaje para bifurcar
    "rect_selection": 8,  # marco de selección rectangular
    "box_selected_seg": 9,  # marrón - segmentos seleccionados por marco
    "highlight_element": 7,  # amarillo - elemento seleccionado en modo preview
}

# ===== Interactor Implementation =====
class PolylineInteractor:
    """Interactor for polyline creation and editing.
    Handles mouse input, preview drawing, and state management.
    """
    def __init__(self, script_object: PolylineScriptObject, config: Optional[PolylineBaseConfig] = None):
        self.script_object = script_object
        self.config: PolylineBaseConfig = config or PolylineBaseConfig()
        self.ctrl_prop_util = getattr(script_object, "control_props_util", None)
        # Coordinate input
        self.coord_input: Optional[AllplanIFW.CoordinateInput | None] = None
        # self.init_storage = None
        self.doc: Any  = None

        self.current_installation: Optional[str] = self.config.default_installation
        self.visible_limit_angles = self.config.limit_angles
        self.angle_steps: Optional[List[float]] = self.config.allowed_angles
        self.min_backtrack_deg: Optional[int] = self.config.min_backtrack_deg
        self.segment_modes = []

        ## ---------- ADD NEW DATOS POLYLINE ----------
        self.points: list[AllplanGeo.Point3D] = []
        self.last_points: list[AllplanGeo.Point3D] = []
        self.polilyne: list[AllplanGeo.Point3D] = []
        self.data: List[SegmentItem] = []
        self.generated_elements: List[List[InstallationElement]] = []

        self.element_list_final = []
        self.pythonpart_group_list = []
        self.segment_groups = []
        self.saved_segments = []

        # ============================================================================
        # ORIENTACIÓN 3D (para tubos verticales): ángulo de referencia en plano XY
        # ============================================================================
        # Modo captura (botón 1012): el usuario define una línea en plano XY (Z=0)
        self.orientation_capture_mode: bool = False
        self.orientation_line_start: AllplanGeo.Point3D | None = None
        self.orientation_line_end: AllplanGeo.Point3D | None = None
        self.orientation_line_preview: AllplanGeo.Point3D | None = None

        self.create_mode: bool = False
        self.edit_mode: bool = False
        self.preview_mode: bool = False
        self.extend_mode: bool = True
        self.saved_elements: bool = False

        self.highlight_geometry = None
        self.selected_segments = set()

        # self.selected_inst_type: str | None = None
        self.applied_pythongroup = {}

        self.default_attributes: Dict = {}
        self.applied_default_attributes: Dict = {}
        self.custom_attributes: Dict = {}
        self.layer_default: str | None = None

        self.current_point: AllplanGeo.Point3D | None = None
        self.box_selecting = False
        self.box_start = None
        self.box_curr = None

        self.pmp_pare_default: Dict = {}
        self.layer_selected: str | None = None
        self.applied_layers: Dict = {}

        # Drag de vértices guardados (edición)
        self.saved_dragging = None  # (path_idx, pt_idx)
        self.saved_hover_point = None
        self.saved_dragging_original_point = (
            None  # Coordenadas originales antes del drag
        )

        self.extend_target = None
        self.elements_created = False  # Flag de control
        self.selected_element_id: Tuple | None = None  # ID del elemento actualmente seleccionado
        self.highlight_geometry = None  # Geometría de highlight temporal
        self.highlight_geometries = []
        self.hovered_element = None  # Elemento bajo el cursor
        self.hover_tooltip_text: str = ""  # Texto del tooltip
        self.allowed_connections = []
        self.allowed_angles = []

        # Editing state
        self.hover_index = -1
        self.drag_index = -1
        self.is_dragging = False

        # Cut and Insert mode
        self.cut_mode: bool = False
        self.insert_mode: bool = False
        self.insert_preview_p: Optional[Any] = None
        self.insert_target: Optional[Tuple] = None
        self.hover_cut_vertex : Optional[Any] = None
        self.selected_junction = None   # (path_idx, pt_idx, Point3D) - persistente tras click

        # Segment hover/selection
        self.hover_seg: Optional[Tuple] = None
        self.selected_seg: Optional[Tuple] = None
        self.hover_mid: Optional[Tuple] = None
        self.is_snapped: bool = False
        # Properties
        if ALLPLAN_AVAILABLE:
            self.com_prop = AllplanBaseElements.CommonProperties()
            self.com_prop.GetGlobalProperties()
        else:
            self.com_prop = None

        self._pending_description: str | None = None  # Flag de actualización pendiente
        self._pending_palette_refresh: bool = False

        self.script_object._load_default_inst_params(self.config.default_installation)

        self._on_installation_type_changed()

        self.is_modification_mode = self.script_object.modification_ele_list.is_modification_element()
        try:
            is_modification_mode = getattr(self, "is_modification_mode", False)
            is_only_update = getattr(self, "is_only_update", False)
            print(
                f"[SO] Inicialización - is_modification_mode={is_modification_mode}, is_only_update={is_only_update}"
            )
        except Exception as e:
            print(f"[SO] Error verificando modo en __init__: {e}")

    def start_input(self, coord_input):
        """Start input with the coordinate input handler."""
        print("\n" + "="*80)
        print("[INT] PolylineInteractor.start_input() CALLED")
        print(f"[INT] coord_input type: {type(coord_input)}")
        print("="*80)

        self.coord_input = coord_input
        self._print_prompt()
        self._change_draw_mode()
        self.doc = coord_input.GetInputViewDocument() # type: ignore
        print("[INT] Interactor ready for input\n")

    def _print_prompt(self):
        """Inicializa el prompt de coordenadas"""
        if self.coord_input:
            prompt = "Click: agregar punto | ESC: terminar"
            prompt_msg = AllplanIFW.InputStringConvert(prompt)

            input_mode = AllplanIFW.CoordinateInputMode(
                AllplanIFW.eIdentificationMode.eIDENT_POINT,
                AllplanIFW.eDrawElementIdentPointSymbols.eDRAW_IDENT_ELEMENT_POINT_SYMBOL_NO
            )
            self.coord_input.InitFirstPointInput(prompt_msg, input_mode)
            self._restore_saved_state()

    # ============================================================================
    # CHANGE DRAW MODE
    # ============================================================================
    def _current_mode(self) -> int:
        value = None
        try:
            value = getattr(self.script_object.build_ele, ParamNames.DrawMode.MODE).value
            mode = value
            return mode
        except Exception:
            return 0

    def _change_draw_mode(self):
        checkbox_value = self._current_mode()
        # --- RESET VISUAL INICIAL ---
        # Al cambiar de modo, eliminamos la referencia del último punto del cursor
        self.current_point = None

        if checkbox_value == PointModeValues.CREATE:
            self.current_point = None
            # Activar modo creación
            self.saved_elements = False
            self.elements_created = False
            self.create_mode = True
            self.edit_mode = False
            self.extend_mode = False
            self.preview_mode = False

            # Limpiar estado de selección y hover
            self.hover_index = -1
            self.hover_tooltip_text = ""
            self.hover_seg = None
            self.hover_mid = None
            self.selected_seg = None
            self.script_object.enable_parameter(ParamNames.DrawMode.INSERT, False)
            self.script_object.enable_parameter(ParamNames.DrawMode.CUT, False)
            self.script_object.show_parameter(ParamNames.Layers.DESCRIPTION, False)
            self.script_object.show_parameter(ParamNames.Layers.VIEW_INFO, False)
            print(f"[INT] CREATE MODE = ON - Nuevo camino iniciado")
        elif checkbox_value == PointModeValues.EDIT:
            self.highlight_geometries.clear()
            if not self.saved_elements:
                self.script_object.element_list = []
                self._save_current_polyline()
                # self._update_segment_groups()
                # self.saved_elements = True

            self.preview_mode = True
            self.edit_mode = True
            self.create_mode = False

            self.script_object._create_elements_preview()
            self._generate_elements_for_preview()
            self.script_object.enable_parameter(ParamNames.DrawMode.INSERT, False)
            self.script_object.enable_parameter(ParamNames.DrawMode.CUT, False)
            self.script_object.show_parameter(ParamNames.Layers.DESCRIPTION)
            self.script_object.enable_parameter(ParamNames.Layers.DESCRIPTION)
            self.script_object.show_parameter(ParamNames.Layers.VIEW_INFO)
            self.script_object.enable_parameter(ParamNames.Layers.VIEW_INFO)

            print(f"[INT] EDIT MODE = ON")
        else:
            if not self.saved_elements:
                self._save_current_polyline()
                self.saved_elements = True

            self.extend_mode = True
            self.preview_mode = False
            self.edit_mode = False
            self.create_mode = False
            self.hover_tooltip_text = ""

            self.script_object._create_elements_preview()
            self._generate_elements_for_preview()

            if self.config and self.config.parameters_show.draw_insert_point:
                self.script_object.enable_parameter(ParamNames.DrawMode.INSERT)
            if self.config and self.config.parameters_show.draw_insert_cut:
                self.script_object.enable_parameter(ParamNames.DrawMode.CUT)

            self.script_object.show_parameter(ParamNames.Layers.DESCRIPTION, False)
            self.script_object.show_parameter(ParamNames.Layers.VIEW_INFO, False)
            print(f"[INT] EXTEND MODE = ON")

        self._pending_palette_refresh = True
        return True

    # ============================================================================
    # LOAD DEFAULT INSTALLATION PARAMETERS
    # ============================================================================
    def _on_installation_type_changed(self):
        self.script_object.resolve_installation_config()

    # ============================================================================
    # RESTORE POLYLINE
    # ============================================================================
    def _restore_saved_state(self):
        """
        Restaura el estado guardado desde build_ele o desde el PythonPartGroup si existe.
        Se llama en __init__ cuando se edita una instancia existente.
        """
        try:
            # Intentar restaurar desde build_ele
            for param_name in ["SavedState", "PolylineState", "StateData"]:
                if not hasattr(self.script_object.build_ele, param_name): continue
                try:
                    param = getattr(self.script_object.build_ele, param_name)
                    if not hasattr(param, "value"): continue

                    state_json = param.value
                    if state_json and isinstance(state_json, str) and state_json.strip():
                        if self._deserialize_state_from_json(state_json):
                            print(f"[SO] Estado previo restaurado desde build_ele.{param_name}")
                            return True
                except Exception as e:
                    print(f"[SO] No se pudo leer parámetro {param_name} desde build_ele: {e}")

            # Intentar restaurar desde PythonPartGroup si está en modo modificación
            if getattr(self, "is_modification_mode", False):
                try:
                    doc = self.coord_input.GetInputViewDocument() # type: ignore
                    python_part_adapter = self.script_object.modification_ele_list.get_base_element_adapter(doc)
                    if not python_part_adapter.IsNull():
                        success, name, parameter = AllplanBaseElements.PythonPartService.GetParameter(python_part_adapter)

                        if success and parameter:
                            # Normalizar parámetro a lista
                            param_lines = parameter.split("\n") if isinstance(parameter, str) else list(parameter) if isinstance(parameter, (list, tuple)) else []
                            # Buscar 'SavedState' en los parámetros
                            for line in param_lines:
                                if isinstance(line, str):
                                    line = line.strip()
                                    if line.startswith("SavedState") and "=" in line:
                                        state_json = line.split("=", 1)[1].strip()
                                        if state_json:
                                            print(f"[SO] Encontrado SavedState en PythonPartGroup: {len(state_json)} caracteres")
                                            if self._deserialize_state_from_json(state_json):
                                                print("[SO] Estado previo restaurado desde PythonPartGroup.SavedState")
                                                return True
                                        break  # Ya encontramos la línea SavedState, salir del loop
                except Exception as e:
                    print(f"[SO] Error intentando leer estado desde PythonPartGroup: {e}")
                    import traceback
                    traceback.print_exc()

            # No se encontró estado guardado (normal en primera creación)
            print("[SO] No se encontró estado guardado (normal en primera creación)")
            return False

        except Exception as e:
            print(f"[SO] Error restaurando estado: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _deserialize_state_from_json(self, json_str: str) -> bool:
        """
        Deserializa saved_paths y saved_segments desde JSON.

        Args:
            json_str: String JSON con el estado serializado

        Returns:
            True si se restauró correctamente, False en caso contrario
        """
        # Limpiar todo primero
        self.data = []
        self.points = []
        self.last_points = []

        self.script_object.saved_paths = []
        self.script_object.saved_cut_points = []
        self.script_object.saved_vertex_cut_points = []
        self.script_object.applied_layers = {}
        self.script_object.applied_default_attributes = {}
        self.script_object.applied_attributes = {}
        self.script_object.global_group_numbers = {}
        self.script_object._fn_name = ""
        self.script_object.reference_orientation_angle = 0

        try:
            if not json_str or not json_str.strip():
                return False

            state = json.loads(json_str)

            try:
                self.script_object._delete_previous_copies()
            except Exception as e:
                print(f"[PMP_PARE] Error limpiando copias previas: {e}")

            # Restaurar paths
            if "saved_paths" in state:
                for path_data in state["saved_paths"]:
                    path = [
                        AllplanGeo.Point3D(pt["X"], pt["Y"], pt["Z"])
                        for pt in path_data
                    ]
                    self.script_object.saved_paths.append(path)

            # Restaurar cut points
            self.script_object.saved_cut_points = []
            if "saved_cut_points" in state:
                self.script_object.saved_cut_points = [
                    AllplanGeo.Point3D(pt["X"], pt["Y"], pt["Z"])
                    for pt in state["saved_cut_points"]
                ]

            self.script_object.saved_vertex_cut_points = []
            if "saved_vertex_cut_points" in state:
                self.script_object.saved_vertex_cut_points = [
                    AllplanGeo.Point3D(pt["X"], pt["Y"], pt["Z"])
                    for pt in state["saved_vertex_cut_points"]
                ]

            # Restaurar points
            for path_points in self.script_object.saved_paths:
                self.last_points.extend(path_points)

            # Restaurar data - SegmentItem
            if "data" in state:
                self.data = []
                for item in state["data"]:
                    segment_group = SegmentItem.dict_to_segment_item(item)
                    self.data.append(segment_group)

            # Restaurar metadata - SegmentInfo
            if "metadata" in state:
                self.script_object.persistent_metadata = ElementSerializer.deserialize_persistent_metadata(state["metadata"])

            if "layer_default" in state:
                self.script_object.default_layers = state["layer_default"]

            if "selected_inst_type" in state:
                param = getattr(self.script_object.build_ele, ParamNames.Installation.INSTALLATION_TYPE)
                param.value = state["selected_inst_type"]

                self.script_object.selected_inst_type = state["selected_inst_type"]

            if "functional_name" in state:
                param = getattr(self.script_object.build_ele, ParamNames.General.FUNCTIONAL_NAME)
                param.value = state["functional_name"]

                self.script_object._fn_name = state["functional_name"]

            if "distribution_type" in state:
                param = getattr(self.script_object.build_ele, ParamNames.Installation.DISTRIBUTION_TYPE)
                param.value = state["distribution_type"]

                self.script_object.distribution_type = state["distribution_type"]

            if "water_type" in state and self.config.parameters_enabled.water_type:
                if self.script_object.distribution_type:
                    water_types = WaterTypes.to_value_list(self.script_object.distribution_type)
                    self.script_object.ctrl_prop_util.set_value_list(ParamNames.Installation.WATER_TYPE, water_types)

                param = getattr(self.script_object.build_ele, ParamNames.Installation.WATER_TYPE)
                param.value = state["water_type"]

                self.script_object.water_type = state["water_type"]

            if "diameter_type" in state:
                _value = int(state["diameter_type"])

                param = getattr(self.script_object.build_ele, ParamNames.Installation.DIAMETER_TYPE)
                param.value = _value

                self.script_object.diameter_type = _value

            if "face_en" in state:
                param = getattr(self.script_object.build_ele, ParamNames.Installation.FACE_EN)
                param.value = state["face_en"]

                self.script_object.face_en = state["face_en"]

            if "reference_orientation_angle" in state and state["reference_orientation_angle"] != "":
                angle_value = float(state["reference_orientation_angle"])
                angle_deg = (math.degrees(angle_value) % 360.0 + 360.0) % 360.0
                info_text = f"{angle_deg:.1f} grados"

                param = getattr(self.script_object.build_ele, ParamNames.Angles.ROTATION_ANGLE)
                param.value = info_text

                self.script_object.reference_orientation_angle = angle_value

            if "applied_layers" in state:
                self.script_object.applied_layers = ElementSerializer.deserialize_layers(state["applied_layers"])

            if "applied_default_attrs" in state:
                self.script_object.applied_default_attributes = ElementSerializer.deserialize_attributes(state["applied_default_attrs"])

            if "applied_custom_attrs" in state:
                self.script_object.applied_attributes = ElementSerializer.deserialize_attributes(state["applied_custom_attrs"])

            if "global_group_numbers" in state:
                self.script_object.global_group_numbers = ElementSerializer.deserialize_global_numbers(state["global_group_numbers"])

            print(f"[SO] Modo edición activado")
            print(f"[SO] Polilínea con {len(self.points)} puntos lista para editar")
            print(f"[SO] Geometría 3D NO restaurada (se regenerará al finalizar)")

            if self.config:
                self.script_object.set_config(self.config)

            self._on_installation_type_changed()
            self.apply_layer_default()
            self._update_segment_groups()    # Re-mapea puntos con los nuevos SegmentItems

            # 3. RE-DIBUJO TOTAL
            self.script_object._create_elements_preview() # Limpia element_list y crea nuevos 3D
            self._generate_elements_for_preview()         # Envía al Viewport de Allplan

            mode_value = getattr(self.script_object.build_ele, ParamNames.DrawMode.MODE)
            mode_value.value = PointModeValues.EXTEND

            return True

        except Exception as e:
            print(f"[SO] Error deserializando estado: {e}")
            import traceback

            traceback.print_exc()
            return False

    # ============================================================================
    # SAVE POLYLINE
    # ============================================================================
    def _save_current_polyline(self):
        self.saved_elements = False
        polyline_info = ""

        # ── Guard ─────────────────────────────────────────────────────────────
        if len(self.points) < 2:
            print("[INT] _save_current_polyline: sin puntos suficientes, omitiendo.")
            self.extend_target = None
            self.points.clear()
            return

        # ── Detectar extend_target desde primer punto ─────────────────────────
        if self.extend_target is None:
            first_pnt = self.points[0]
            for pidx, path in enumerate(self.script_object.saved_paths):
                if not path:
                    continue
                if self._points_equal(first_pnt, path[-1]):
                    self.extend_target = (pidx, "end")
                    break
                if self._points_equal(first_pnt, path[0]):
                    self.extend_target = (pidx, "start")
                    break

        # ── Detectar end_target desde último punto ────────────────────────────
        end_target = None
        last_pnt = self.points[-1]
        for pidx, path in enumerate(self.script_object.saved_paths):
            if not path:
                continue
            if self.extend_target and self.extend_target[0] == pidx:
                continue
            if self._points_equal(last_pnt, path[0]):
                end_target = (pidx, "start")
                break
            if self._points_equal(last_pnt, path[-1]):
                end_target = (pidx, "end")
                break

        # ── Snapshot de metadata ANTES de modificar paths ─────────────────────
        # Guardamos referencia a los paths originales para remapear metadata
        old_paths = [list(p) for p in self.script_object.saved_paths]

        # ── CASO: Extensión simple (un extremo) ───────────────────────────────
        if self.extend_target is not None:
            pidx, side = self.extend_target
            if 0 <= pidx < len(self.script_object.saved_paths):
                base = self.script_object.saved_paths[pidx]
                old_len = len(base)  # Longitud ANTES de extender

                if side == "end":
                    new_points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]]
                    base.extend(new_points)
                    # Metadata: los segmentos anteriores mantienen índice
                    # Los nuevos segmentos no tienen metadata aún → se crearán al vuelo
                    print(f"[INT] Extensión fusionada en polilínea #{pidx} (end)")

                else:  # 'start'
                    new_points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]]
                    prepend_count = len(new_points)
                    self.script_object.saved_paths[pidx] = list(reversed(new_points)) + base
                    # Metadata: los segmentos originales se desplazan prepend_count posiciones
                    self._shift_metadata(pidx, offset=prepend_count)
                    print(f"[INT] Extensión fusionada en polilínea #{pidx} (start)")

                # ── CASO ESPECIAL: fusión de dos paths ────────────────────────
                if end_target is not None:
                    ep_idx, ep_side = end_target
                    if 0 <= ep_idx < len(self.script_object.saved_paths):
                        extended_path = self.script_object.saved_paths[pidx]
                        other_path    = self.script_object.saved_paths[ep_idx]
                        base_len      = len(extended_path)  # Segmentos antes de fusionar

                        if ep_side == "start":
                            merged = extended_path + other_path[1:]
                            # Metadata de other_path se remapea desde base_len
                            self._merge_metadata(
                                src_path_idx=ep_idx,
                                dst_path_idx=pidx,
                                dst_offset=base_len - 1,  # -1 porque el punto de unión es compartido
                                reverse=False
                            )
                        else:  # ep_side == "end"
                            merged = extended_path + list(reversed(other_path))[1:]
                            self._merge_metadata(
                                src_path_idx=ep_idx,
                                dst_path_idx=pidx,
                                dst_offset=base_len - 1,
                                reverse=True
                            )

                        self.script_object.saved_paths[pidx] = merged
                        # Eliminar ep_idx y reindexar metadata
                        self.script_object.saved_paths.pop(ep_idx)
                        self._reindex_metadata_after_pop(ep_idx)
                        print(f"[INT] Paths #{pidx} y #{ep_idx} fusionados en uno solo")

                polyline_info = f"Polilínea #{pidx + 1} extendida"
            self.extend_target = None

        # ── CASO: Camino nuevo o bifurcación ──────────────────────────────────
        else:
            first_pnt = self.points[0]
            match = self._find_path_to_extend(first_pnt)

            if match is not None:
                path_idx, vtx_idx, existing_vtx = match
                existing_path = self.script_object.saved_paths[path_idx]
                last_idx = len(existing_path) - 1
                new_pts = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]]

                if vtx_idx == last_idx:
                    self.script_object.saved_paths[path_idx].extend(new_pts)
                    print(f"[CONEXIÓN] Extendido final de camino {path_idx}")

                elif vtx_idx == 0:
                    prepend_count = len(new_pts)
                    self.script_object.saved_paths[path_idx] = list(reversed(new_pts)) + existing_path
                    self._shift_metadata(path_idx, offset=prepend_count)
                    print(f"[CONEXIÓN] Extendido inicio de camino {path_idx}")

                else:
                    branch_path = [existing_vtx] + new_pts
                    self.script_object.saved_paths.append(branch_path)
                    print(f"[BIFURCACIÓN] Nueva rama desde camino {path_idx} (Vértice {vtx_idx})")

                self.last_points.extend(self.points[1:])

            else:
                self.last_points.extend(self.points)
                new_path = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
                self.script_object.saved_paths.append(new_path)
                print(f"[NUEVO] Camino independiente creado")

        # ── Sincronización final ───────────────────────────────────────────────
        self.points.clear()
        self.get_segments()
        self._update_segment_groups()
        self.script_object._create_elements_preview()
        self.saved_elements = True

        if self.saved_elements:
            total_polylines = len(self.script_object.saved_paths)
            total_segments  = sum(
                len(pts) - 1 for pts in self.script_object.saved_paths if len(pts) >= 2
            )
            message = (
                f"✅ Polilínea guardada exitosamente!\n\n"
                f"{polyline_info}\n\n"
                f"Total de polilíneas: {total_polylines}\n"
                f"Total de segmentos: {total_segments}"
            )
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)

    # ============================================================================
    # HELPERS DE REINDEXACIÓN DE METADATA
    # ============================================================================
    def _shift_metadata(self, path_idx: int, offset: int):
        """
        Desplaza los índices de segmento de un path en +offset.
        Usado cuando se prependean puntos al inicio de un path.
        """
        meta = self.script_object.persistent_metadata
        keys_to_shift = [
            (k, v) for k, v in meta.items()
            if k.startswith(f"{path_idx}_")
        ]
        for old_key, value in keys_to_shift:
            seg_idx = int(old_key.split("_")[1])
            new_key = f"{path_idx}_{seg_idx + offset}"
            del meta[old_key]
            meta[new_key] = value

    def _merge_metadata(self, src_path_idx: int, dst_path_idx: int, dst_offset: int, reverse: bool):
        """
        Copia la metadata de src_path_idx a dst_path_idx con offset.
        Si reverse=True, invierte el orden de los segmentos (path invertido).
        """
        meta = self.script_object.persistent_metadata
        src_entries = {
            int(k.split("_")[1]): v
            for k, v in meta.items()
            if k.startswith(f"{src_path_idx}_")
        }
        if not src_entries:
            return

        max_seg = max(src_entries.keys())

        for seg_idx, value in src_entries.items():
            if reverse:
                new_seg_idx = dst_offset + (max_seg - seg_idx)
            else:
                new_seg_idx = dst_offset + seg_idx
            meta[f"{dst_path_idx}_{new_seg_idx}"] = value

    def _reindex_metadata_after_pop(self, removed_path_idx: int):
        """
        Reindexar todos los path_idx > removed_path_idx decrementando en 1.
        Llamar después de saved_paths.pop(removed_path_idx).
        """
        meta = self.script_object.persistent_metadata
        keys_to_update = [
            (k, v) for k, v in meta.items()
            if int(k.split("_")[0]) > removed_path_idx
        ]
        # Primero eliminar las claves antiguas
        for old_key, _ in keys_to_update:
            del meta[old_key]
        # Luego insertar con nuevo índice
        for old_key, value in keys_to_update:
            parts    = old_key.split("_")
            new_key  = f"{int(parts[0]) - 1}_{parts[1]}"
            meta[new_key] = value

    def _update_segment_groups(self):
        """
        Sincroniza los grupos de segmentos basándose en TODO lo que hay en data.
        """
        # 1. Preparar la lista de puntos completa (viejas + viva)
        all_path_points = [list(p) for p in self.script_object.saved_paths]

        if self.create_mode and len(self.points) >= 2:
            all_path_points.append(list(self.points))

        # 2. Ejecutar el filtro inteligente
        # Ahora self.data tiene segmentos de todas las rutas gracias al nuevo get_segments
        new_groups = self.filter_and_group_segments(
            segments=self.data,
            point_groups=all_path_points
        )

        # 3. Actualizar estado
        self.segment_groups = new_groups
        self.script_object.segment_groups = new_groups

    def _format_segment_label(self, diameter: float, system: str) -> str:
        """Formatea la etiqueta de segmento: D110 P (pluvial) o D25 F, D40 F, D110 F (fecal)."""
        try:
            d = int(round(float(diameter)))
        except Exception:
            d = int(diameter) if isinstance(diameter, (int, float)) else 0

        label = f"D{d} {system[0].strip().upper()}"
        return label

    def _get_segment_section_info(
        self, kind: str, path_idx: int, seg_idx: int
    ) -> Optional[dict]:
        """Obtiene información de sección para un segmento específico"""
        # if kind != "saved":
        #     return None

        # Buscar en saved_segments si ya tiene sección asignada
        for segment_info in self.script_object.saved_segments:
            points = segment_info["points"]
            if len(points) >= 2:
                # Verificar si coincide con el segmento buscado
                if (
                    0 <= path_idx < len(self.script_object.saved_paths)
                    and 0 <= seg_idx < len(self.script_object.saved_paths[path_idx]) - 1
                ):

                    expected_p1 = self.script_object.saved_paths[path_idx][seg_idx]
                    expected_p2 = self.script_object.saved_paths[path_idx][seg_idx + 1]

                    if self._points_equal(
                        points[0], expected_p1
                    ) and self._points_equal(points[1], expected_p2):
                        return segment_info
        return None

    def _points_equal(
        self, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D, tolerance: float = 1e-6
    ) -> bool:
        """Compara dos puntos con tolerancia"""
        return (
            abs(p1.X - p2.X) < tolerance
            and abs(p1.Y - p2.Y) < tolerance
            and abs(p1.Z - p2.Z) < tolerance
        )

    def filter_and_group_segments(self, segments, point_groups) -> list:
        all_groups = []

        # Función auxiliar para convertir Point3D en una tupla redondeada comparable
        def pt_to_tuple(pt):
            # Redondeamos a 4 decimales para evitar errores de precisión de Allplan
            return (round(pt.X, 4), round(pt.Y, 4), round(pt.Z, 4))

        # 1. Crear el mapa de segmentos con claves de tuplas redondeadas
        segment_map = {}
        for seg in segments:
            # Extraemos las coordenadas de los puntos de inicio y fin del segmento
            key = (pt_to_tuple(seg.data.start), pt_to_tuple(seg.data.end))
            segment_map[key] = seg

        # 2. Agrupar basándose en los grupos de puntos
        for points in point_groups:
            if len(points) < 2:
                continue

            group_segments = []
            for i in range(len(points) - 1):
                # Convertimos los puntos de la trayectoria a tuplas para buscar en el mapa
                pair = (pt_to_tuple(points[i]), pt_to_tuple(points[i + 1]))

                if pair in segment_map:
                    seg = segment_map[pair]
                    # Asignamos nombre correlativo dentro del grupo
                    seg.name = f"line_{len(group_segments) + 1}"
                    group_segments.append(seg)
                else:
                    # Opcional: Log de depuración si un segmento esperado no aparece
                    # print(f"[DEBUG] Segmento no encontrado para el par: {pair}")
                    pass

            if group_segments:
                all_groups.append(group_segments)

        return all_groups

    # ============================================================================
    # GENERATE ELEMENTS (TUBO - UNION - CODO - BIFURCACIONES - REDUCTORES)
    # ============================================================================
    def _generate_elements_for_preview(self):
        print("[SO] Generando elementos con detección de conexiones")
        self.generated_elements.clear()

        # --- HELPERS ---
        def p3d_to_key(p): return (round(p.X, 1), round(p.Y, 1), round(p.Z, 1))
        def p3d_to_list(p): return [p.X, p.Y, p.Z]
        def _norm_vec(p1, p2):
            vx, vy, vz = p2.X - p1.X, p2.Y - p1.Y, p2.Z - p1.Z
            length = (vx**2 + vy**2 + vz**2)**0.5
            return (0,0,0) if length < 1e-9 else (vx/length, vy/length, vz/length)
        def _norm(x, y, z):
            length = (x * x + y * y + z * z) ** 0.5
            if length < 1e-9:
                return (0.0, 0.0, 0.0)
            return (x / length, y / length, z / length)
        def _dot(x1, y1, z1, x2, y2, z2):
            return x1 * x2 + y1 * y2 + z1 * z2

        try:
            if not self.script_object.saved_paths: return

            # 1. MAPA DE CONECTIVIDAD: { (x,y,z): [ (path_idx, point_idx), ... ] }
            global_nodes = {}
            for p_idx, path in enumerate(self.script_object.saved_paths):
                for pt_idx, pt in enumerate(path):
                    key = p3d_to_key(pt)
                    if key not in global_nodes: global_nodes[key] = []
                    global_nodes[key].append((p_idx, pt_idx))

            # 1. Iniciamos el contador fuera de todos los bucles
            # Esto garantiza que la Ruta 2 empiece donde terminó la Ruta 1
            _current_global_idx = 0

            # 2. PROCESAR CADA RUTA
            for path_idx, path in enumerate(self.script_object.saved_paths):

                if path_idx > 0:
                    _current_global_idx += 1

                current_path_elements = []
                if len(path) < 2:
                    self.generated_elements.append([])
                    continue

                # Reutiliza allowed_connections que ya existe en el script_object
                allows_multi_diameter = ElementTypes.REDUCION.value in self.script_object.allowed_connections

                # --- 2.1 TUBOS (Segmentos) ---
                for e in range(len(path) - 1):
                    p1, p2 = path[e], path[e+1]
                    _type = ElementTypes.TUBO.value

                    # ── Resolver diámetro según si la instalación permite reductores ──
                    if allows_multi_diameter:
                        meta_key = f"{path_idx}_{e}"
                        meta = self.script_object.persistent_metadata.get(meta_key)
                        diameter = meta.diameter if meta and meta.diameter else self.script_object.diameter_type
                    else:
                        diameter = self.script_object.diameter_type

                    element = InstallationElement(
                        type=_type,
                        key=[_type, path_idx, e, 0, path_idx],
                        geometry=AllplanGeo.Line3D(p1, p2),
                        position=AllplanGeo.Point3D((p1.X+p2.X)/2, (p1.Y+p2.Y)/2, (p1.Z+p2.Z)/2),
                        layer=self.layer_default if self.layer_default else "",
                        path_idx=path_idx,
                        seg_idx=e,
                        params={'start': p3d_to_list(p1), 'end': p3d_to_list(p2)},
                        diameter_in=diameter
                    )
                    current_path_elements.append(element.to_dict())

                # --- 2.2 NODOS (Codos, Uniones, Bifurcaciones) ---
                for i in range(len(path)):
                    p_curr = path[i]
                    p_key = p3d_to_key(p_curr)
                    connections = global_nodes.get(p_key, [])

                    # 1. RECOLECTAR DIRECCIONES ÚNICAS
                    # Usamos un set para colapsar vectores que apuntan a la misma dirección
                    unique_directions = set()

                    for c_path_idx, c_pt_idx in connections:
                        c_path = self.script_object.saved_paths[c_path_idx]

                        # Dirección hacia el punto anterior (si existe)
                        if c_pt_idx > 0:
                            v_back = _norm_vec(p_curr, c_path[c_pt_idx - 1])
                            if v_back != (0,0,0):
                                # Redondeamos para evitar errores de precisión decimal
                                unique_directions.add(tuple(round(c, 4) for c in v_back))

                        # Dirección hacia el punto siguiente (si existe)
                        if c_pt_idx < len(c_path) - 1:
                            v_fwd = _norm_vec(p_curr, c_path[c_pt_idx + 1])
                            if v_fwd != (0,0,0):
                                unique_directions.add(tuple(round(c, 4) for c in v_fwd))

                    # 2. CLASIFICACIÓN GEOMÉTRICA
                    num_branches = len(unique_directions)

                    _type = ""
                    angle_deg = 0.0
                    marker_size = 90

                    # 3. CLASIFICACIÓN BASADA EN RAMAS REALES
                    if num_branches >= 3:
                        # TRES O MÁS SEGMENTOS CONECTADOS = BIFURCACIÓN (T o Y)
                        _type = ElementTypes.BIFURCACION.value
                        dirs = list(unique_directions)
                        # Encontramos el ángulo máximo entre cualquier par de vectores
                        # En una "T" perfecta, el ángulo máximo será 180° entre los extremos
                        max_angle = 0.0
                        best_pair = (0, 1)

                        for a in range(len(dirs)):
                            for b in range(a + 1, len(dirs)):
                                dot = sum(dirs[a][j] * dirs[b][j] for j in range(3))
                                angle = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
                                if angle > max_angle:
                                    max_angle = angle
                                    best_pair = (a, b)

                        # El ángulo de la bifurcación suele ser el ángulo del tercer vector
                        # respecto a uno de los vectores de la tubería principal.
                        main_indices = set(best_pair)
                        branch_indices = [idx for idx in range(len(dirs)) if idx not in main_indices]

                        if branch_indices:
                            # Calculamos el ángulo entre la rama y el primer vector principal
                            v_main = dirs[best_pair[0]]
                            v_branch = dirs[branch_indices[0]]
                            dot_branch = sum(v_main[j] * v_branch[j] for j in range(3))
                            angle_deg = math.degrees(math.acos(max(-1.0, min(1.0, dot_branch))))
                            # Si da 90 es una T, si da algo como 45 o 60 es una Y.
                    elif num_branches == 2:
                        # DOS SEGMENTOS = CODO O UNIÓN
                        vectors = list(unique_directions)
                        v1 = AllplanGeo.Vector3D(vectors[0][0], vectors[0][1], vectors[0][2])
                        v2 = AllplanGeo.Vector3D(vectors[1][0], vectors[1][1], vectors[1][2])

                        # Producto escalar para ver si están alineados (180 grados entre vectores opuestos)
                        # Nota: _norm_vec devuelve vectores que SALEN del nodo.
                        # Si están alineados (recta), el dot product será -1.0
                        dot = v1.X*v2.X + v1.Y*v2.Y + v1.Z*v2.Z

                        if dot <= -0.999: # Casi 180 grados (recta)
                            _type = ElementTypes.UNION.value
                        else:
                            _type = ElementTypes.CODO.value
                            angle_deg = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
                    elif num_branches == 1:
                        # UN SOLO SEGMENTO = TERMINAL / TAPÓN (Opcional)
                        _type = "" # O ElementTypes.TERMINAL si lo tienes

                    # 4. PROCESAMIENTO SI EL TIPO ES VÁLIDO
                    if _type in self.script_object.allowed_connections:
                        # Para bifurcaciones, podríamos querer un color o tamaño distinto
                        current_marker = marker_size if _type != ElementTypes.BIFURCACION.value else marker_size * 1.2
                        axis = AllplanGeo.AxisPlacement3D(
                            AllplanGeo.Point3D(p_curr.X - current_marker/2,
                                            p_curr.Y - current_marker/2,
                                            p_curr.Z - current_marker/2)
                        )
                        geom = AllplanGeo.Polyhedron3D.CreateCuboid(axis, current_marker, current_marker, current_marker)

                        element = InstallationElement(
                            type=_type,
                            key=[_type, path_idx, i, 0, path_idx],
                            geometry=geom,
                            position=p_curr,
                            layer=self.layer_default if self.layer_default else "",
                            path_idx=path_idx,
                            seg_idx=i,
                            params={'angle': angle_deg}
                        )
                        current_path_elements.append(element.to_dict())


                # --- 2.3 REDUCTORES (Cambios de diámetro en segmentos rectos) ---
                if len(path) >= 3:
                    for vertex_idx in range(1, len(path) - 1):
                        p_prev = path[vertex_idx - 1]
                        p_curr = path[vertex_idx]
                        p_next = path[vertex_idx + 1]

                        # 1. RECUPERAR METADATA USANDO EL NUEVO DICCIONARIO PERSISTENTE
                        # Acceso directo O(1) en lugar de bucles de comparación de puntos
                        key_in  = f"{path_idx}_{vertex_idx - 1}" # Segmento que entra al vértice
                        key_out = f"{path_idx}_{vertex_idx}"     # Segmento que sale del vértice

                        meta_in  = self.script_object.persistent_metadata.get(key_in)
                        meta_out = self.script_object.persistent_metadata.get(key_out)

                        if not meta_in or not meta_out:
                            continue

                        diameter_in  = meta_in.diameter
                        diameter_out = meta_out.diameter

                        # 2. LÓGICA DE FILTRADO
                        # Si los diámetros son iguales, no es una reducción
                        if diameter_in == diameter_out:
                            continue

                        # Solo en segmentos colineales (rectos)
                        v1 = _norm(p_curr.X - p_prev.X, p_curr.Y - p_prev.Y, p_curr.Z - p_prev.Z)
                        v2 = _norm(p_next.X - p_curr.X, p_next.Y - p_curr.Y, p_next.Z - p_curr.Z)
                        is_straight = abs(_dot(*v1, *v2)) >= 0.999

                        if not is_straight:
                            continue

                        # Validar si el tipo de conexión está habilitado
                        _reducer_type = ElementTypes.REDUCION.value
                        if _reducer_type not in self.script_object.allowed_connections:
                            continue

                        # 3. GENERACIÓN DE GEOMETRÍA Y ELEMENTO
                        reducer_label = f"D{int(diameter_in)}-D{int(diameter_out)}"
                        marker_size_r = 75.0

                        axis = AllplanGeo.AxisPlacement3D(
                            AllplanGeo.Point3D(
                                p_curr.X - marker_size_r / 2,
                                p_curr.Y - marker_size_r / 2,
                                p_curr.Z - marker_size_r / 2,
                            )
                        )

                        try:
                            reducer_geom = AllplanGeo.Polyhedron3D.CreateCuboid(
                                axis, marker_size_r, marker_size_r, marker_size_r
                            )
                        except:
                            reducer_geom = AllplanGeo.Line3D(p_curr, p_curr)

                        layer = self._calculate_layer_from_orientation(p_prev, p_curr)

                        element = InstallationElement(
                            type=_reducer_type,
                            key=[_reducer_type, path_idx, vertex_idx, 0, path_idx],
                            geometry=reducer_geom,
                            position=p_curr,
                            layer=layer,
                            path_idx=path_idx,
                            seg_idx=vertex_idx,
                            params={
                                "reducer_type": reducer_label,
                                "diameter_in": diameter_in,
                                "diameter_out": diameter_out,
                                "system": meta_in.system # Hereda el sistema del segmento
                            },
                            diameter_in=diameter_in,
                            diameter_out=diameter_out,
                            reducer_type=reducer_label,
                        )

                        current_path_elements.append(element.to_dict())
                        print(f"[SO] Reductor {reducer_label} generado en path{path_idx}_vtx{vertex_idx}")

                # --- 3. ORDENAR Y ASIGNAR SEQ_ID DENTRO DE ESTA RUTA ---
                # Ordenamos: 1ro conexiones (codos/uniones), 2do tubos, basándonos en seg_idx
                current_path_elements.sort(key=lambda x: (
                    x["key"][1],               # 1ro: path_idx
                    x["key"][2],               # 2do: sub_idx / vertex_idx
                    0 if x["type"] != "tubo" else 1  # 3ro: Conexión antes que tubo
                ))

                # Ajustamos los SEQ_ID finales y Layers para los elementos de esta ruta
                # new_generated_elements = []
                for final_idx, element in enumerate(current_path_elements):
                    # Actualizamos el 4to índice de la tupla key con el índice real

                    element["key"][1] = _current_global_idx
                    element["key"][3] = final_idx
                    element["key"] = tuple(element["key"]) # Volvemos a tupla para
                    # element["key"][1] = _next_path_group_idx # Usar el contador global
                    element["path_idx"] = _current_global_idx
                    element["seq_id"] = final_idx

                    # Aplicar Layer si existe en applied_layers usando la NUEVA estructura de storage_key
                    storage_key = f"seg_{_current_global_idx}_elem_{final_idx}"
                    if hasattr(self, 'applied_layers') and storage_key in self.applied_layers:
                        element["layer"] = self.applied_layers[storage_key]["layer"]

                    if element["type"] == ElementTypes.UNION.value:
                        _current_global_idx += 1  # Incrementamos para el SIGUIENTE segmento

                # Añadimos la lista de la ruta al array maestro
                current_path_elements.sort(key=lambda x: (
                    0 if x["type"] == "tubo" else 1, # Grupo 0: Tubos, Grupo 1: Codos/Uniones
                    x["seq_id"]                     # Orden interno por su ID ya asignado
                ))
                self.generated_elements.append(current_path_elements)

        except Exception as ex:
            print(f"Error en preview: {ex}")

    def _update_generate_elements(self, path_idx: int, layer_idx: int):
        generated_paths = getattr(self, "generated_elements", [])
        for path_group in generated_paths:  # Primer nivel: Las rutas
            for element in path_group:      # Segundo nivel: Los elementos
                key = element.get('key')
                if key and len(key) >= 4:
                    if key[1] == path_idx and key[3] == layer_idx:
                        element['layer'] = self.script_object.layer_selected
                        break

    def _calculate_layer_from_orientation(
        self, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D
    ) -> str:
        """
        Calcula el layer correcto basándose en la orientación del segmento y la configuración de la paleta.

        Args:
            p1: Punto inicial del segmento
            p2: Punto final del segmento

        Returns:
            Número de layer correcto
        """
        LAYER_NAME_IS_CON_SANE_FAB = "IS_CON_SANE_FAB"
        LAYER_NAME_IS_CON_SANE_OBR = "IS_CON_SANE_OBR"
        LAYER_NAME_KN_X_AIGUA = "KN_X_AIGUA"
        LAYER_NAME_KN_Y_AIGUA = "KN_Y_AIGUA"
        LAYER_NAME_KN_AIGUA = "KN_AIGUA"

        # Calcular orientación
        dx = p2.X - p1.X
        dy = p2.Y - p1.Y
        dz = p2.Z - p1.Z
        dz_abs = abs(dz)
        seg_len_xy = (dx * dx + dy * dy) ** 0.5

        is_horizontal = seg_len_xy > 1e-6 and dz_abs < 50.0
        is_vertical = dz_abs > 50.0 and seg_len_xy < 50.0

        # Obtener configuración de la paleta
        distribution_type = getattr(self.script_object.build_ele, ParamNames.Installation.DISTRIBUTION_TYPE).value
        # installation_vertical = self._get_installation_type_vertical()
        face = getattr(self.script_object.build_ele, ParamNames.Installation.FACE_EN).value or "X"

        # Calcular layer según orientación (por nombre)
        if is_horizontal:
            if distribution_type == "IS":
                return LAYER_NAME_IS_CON_SANE_FAB
            else:  # OBRA
                return LAYER_NAME_IS_CON_SANE_OBR
        elif is_vertical:
            if distribution_type == "EN":
                if face == "X":
                    return LAYER_NAME_KN_X_AIGUA
                else:  # Y
                    return LAYER_NAME_KN_Y_AIGUA
            else:  # TD o IS
                return LAYER_NAME_KN_AIGUA
        else:
            return LAYER_NAME_IS_CON_SANE_OBR

    # ============================================================================
    # PROCESSES MOUSE MOVEMENTS
    # ============================================================================
    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: AllplanIFW.AddMsgInfo
    ) -> bool:
        """
        Procesa mensajes del mouse unificando lógica de creación, edición y extensión.
        """
        # ----------------------------------------------------------------------
        # 0. DIAGNÓSTICO Y CHEQUEOS BÁSICOS
        # ----------------------------------------------------------------------
        # Imprimir log solo la primera vez para confirmar que recibe eventos
        if not hasattr(self, '_first_mouse_msg_logged'):
            print("\n" + "!"*80)
            print("[INT] process_mouse_msg() CALLED FOR FIRST TIME!")
            print(f"[INT] coord_input: {self.coord_input}")
            print("!"*80 + "\n")
            self._first_mouse_msg_logged = True

        result = False
        if not self.coord_input:
            print("[INT.process_mouse_msg] sin coord_input")
            return True

        # Si current_point es None, usamos un Point3D vacío para evitar el error de Boost.Python
        ref_point = self.current_point if self.current_point is not None else AllplanGeo.Point3D()
        raw_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, ref_point, bool(self.points)).GetPoint()

        # 1. Obtener punto con Snap y detectar el modo de vista
        smart_pnt, self.is_snapped = self.get_smart_snap_proyectado(raw_pnt)
        view_type = self.coord_input.GetViewWorldProjection().GetIsoProjection()
        mode = self._get_view_mode(view_type)

        # 2. Determinar el punto actual (Snap o Herencia de profundidad)
        if self.is_snapped:
            current_pnt = smart_pnt
        else:
            current_pnt = AllplanGeo.Point3D(raw_pnt)
            if self.points:
                last = self.points[-1]
                # Aplicamos la profundidad del último punto según el plano
                if mode == "XY":   current_pnt.Z = last.Z
                elif mode == "XZ": current_pnt.Y = last.Y
                elif mode == "YZ": current_pnt.X = last.X


        if self.orientation_capture_mode:
            return self._handle_orientation_capture(mouse_msg, current_pnt)

        button = getattr(mouse_msg, 'Button', 1)
        is_left_click = (button == 1)
        # ----------------------------------------------------------------------
        # 1. MODO CREACIÓN (Fuente A: Lógica de Snap and Smart Creation)
        # ----------------------------------------------------------------------
        if self.create_mode:
            self.box_selecting = False
            # CAPTURA DEL MODO: Guardamos el modo actual para este nuevo segmento
            if not hasattr(self, 'segment_modes'):
                self.segment_modes = []

            if len(self.points) >= 1:
                last_pt = self.points[-1]
                prev_pt = self.points[-2] if len(self.points) >= 2 else None

                limit_angles = getattr(self.script_object.build_ele, ParamNames.Angles.CHECKBOX).value
                if self.visible_limit_angles and limit_angles and self.angle_steps and prev_pt is not None:
                    current_pnt = self.snap_point_with_angle(
                        current_pnt,
                        last_pt,
                        prev_pt
                    )

                if self.min_backtrack_deg and prev_pt is not None:
                    current_pnt = self._constrain_no_backtrack(
                        raw_point=current_pnt,
                        last_point=last_pt,
                        prev_point=prev_pt,
                        min_backtrack_deg=self.min_backtrack_deg,
                    )

            if self.coord_input.IsMouseMove(mouse_msg):
                # 1. Prioridad: Vértices guardados (para Drag)
                self.saved_hover_point = self._find_hover_saved_point(current_pnt, mode)

                # 2. Si NO hay vértice, buscamos Midpoints
                self.hover_mid = (
                    None if self.saved_hover_point else self._find_hover_midpoint(current_pnt, mode)
                )

                # 3. Si NO hay vértice ni midpoint, buscamos Segmentos (para Inserción)
                self.hover_seg = (
                    None if (self.saved_hover_point or self.hover_mid)
                    else self._find_hover_segment(current_pnt, mode)
                )
                self._draw_preview(current_pnt)
                return True

            if is_left_click:
                snapped_point = None
                min_dist = float('inf')

                for path in self.script_object.saved_paths:
                    for saved_p in path:
                        # AQUÍ usamos la función de distancia en el plano
                        dist = self.get_dist_in_plane(current_pnt, saved_p, mode)
                        if dist < HIT_TOL_VERTEX and dist < min_dist:
                            snapped_point = saved_p
                            min_dist = dist

                # Si encontramos un punto guardado cerca, usamos su 3D REAL
                point_to_add = AllplanGeo.Point3D(snapped_point) if snapped_point else current_pnt

                # ── VALIDACIÓN DE LONGITUD MÍNIMA ──────────────────────────────────────
                if self.points:
                    last_point = self.points[-1]
                    vector = AllplanGeo.Line3D(last_point, point_to_add)
                    segment_length = AllplanGeo.CalcLength(vector)

                    inst_type = getattr(self.script_object, "selected_inst_type", None)
                    min_length = getattr(self.script_object, "min_segment_length", 0)

                    if min_length > 0 and segment_length < min_length:
                        message = (
                            f"Tipo de instalación: {inst_type}\n"
                            f"Longitud mínima requerida: {min_length / 1000:.4f} m\n\n"
                            f"El segmento trazado mide {segment_length / 1000:.4f} m,\n"
                            f"lo cual es menor que la longitud mínima permitida.\n\n"
                            f"¿Desea IGNORAR la restricción y agregar el punto?\n\n"
                            f"[SÍ] Agrega el punto de todos modos.\n"
                            f"[NO] Cancelar y reposicionar el punto."
                        )
                        result = PythonUtility.ShowMessageBox(message, PythonUtility.MB_YESNO)

                        if result == PythonUtility.IDNO:
                            # El usuario cancela → NO agregamos el punto, solo redibujamos
                            self._draw_preview(point_to_add)
                            return True
                        # Si IDYES → continúa normalmente y agrega el punto
                # ── FIN VALIDACIÓN ─────────────────────────────────────────────────────

                self.points.append(point_to_add)
                self.current_point = point_to_add
                self.segment_modes.append(mode) # Guardamos "XY", "XZ" o "YZ"
                self._draw_preview(current_pnt)
                self.get_segments()
                return True

            return True

        # ----------------------------------------------------------------------
        # 2. MODO CONFIGURACION (Fuente B: Selección, Hover, Box Select)
        # ----------------------------------------------------------------------
        elif self.edit_mode:
            # ref_point = self.current_point if self.current_point is not None else AllplanGeo.Point3D()
            current_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, AllplanGeo.Point3D(), True # Usamos punto vacío
            ).GetPoint()

            if self.coord_input.IsMouseMove(mouse_msg):

                # Rectángulo de selección
                if self.box_selecting and (self.box_start is not None):
                    self.box_curr = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                else:
                    hovered = self._find_element_at_point(current_pnt, mode, tolerance=HIT_TOL_SEGMENT)
                    if hovered != self.hovered_element:
                        self.hovered_element = hovered
                        if hovered:
                            self.hover_tooltip_text = self._generate_tooltip_text(hovered)
                            self.script_object.hover_tooltip_text = self.hover_tooltip_text
                        else:
                            self.hover_tooltip_text = ""

                self._draw_preview(current_pnt)
                return True

            if is_left_click:
                # ============================================================================
                # modo edicion de layers: Detectar clicks en elementos para cambiar layer
                # ============================================================================
                if self.preview_mode:
                    self._pending_description = ""
                    self.selected_segments.clear()
                    self.selected_seg = None

                    # # 1. Encontrar qué elemento individual se tocó
                    clicked_element = self._find_clicked_element(current_pnt, mode)
                    if clicked_element:
                        self.highlight_geometries.clear()
                        # 2. Extraer el path_idx del elemento clicado
                        # Estructura de key: (type, path_idx, elem_idx, layer_idx)
                        _type, path_idx, _, _, _= clicked_element.get("key")

                        self._pending_description = self.hover_tooltip_text

                        if _type == 'tubo' and not self.script_object.is_individual_mode:
                            # CASO: SELECCIÓN POR SEGMENTO (GRUPO)
                            # Buscamos todos los elementos que pertenecen al mismo path_idx
                            for path_group in getattr(self, "generated_elements", []):
                                for element in path_group:
                                    if element['type'] == 'tubo' and element['key'][1] == path_idx:
                                        self._on_element_clicked(element, is_multiple=True)
                        else:
                            # CASO: SELECCIÓN INDIVIDUAL (RECUPERADOR)
                            self._on_element_clicked(clicked_element, is_multiple=False)

                        self._draw_preview(current_pnt)
                        return True

                # C) Click sobre SEGMENTO GUARDADO: prioridad insertar si está activo
                self.hover_seg = self._find_hover_segment(current_pnt, mode)
                if self.hover_seg is not None:
                    if self.selected_segments:
                        seg_tuple = self.hover_seg
                        if seg_tuple in self.selected_segments:
                            self.selected_segments.remove(seg_tuple)
                            print(f"[INT] Segmento quitado: {seg_tuple}")
                        else:
                            self.selected_segments.add(seg_tuple)
                            print(f"[INT] Segmento agregado: {seg_tuple}")
                        print(
                            f"[INT] Total seleccionados: {len(self.selected_segments)}"
                        )

                    self._draw_preview(current_pnt)
                    return True

                # D) Selección por marco de segmentos - Solo si no hay conflictos de modo
                # Verificar que no estemos en modos que entren en conflicto
                if self.preview_mode:
                    if not self.box_selecting:
                        self.selected_element_id = None
                        self.box_selecting = True
                        self.box_start = AllplanGeo.Point3D(
                            current_pnt.X, current_pnt.Y, current_pnt.Z
                        )
                        self.box_curr = AllplanGeo.Point3D(
                            current_pnt.X, current_pnt.Y, current_pnt.Z
                        )
                        print("[INT] Iniciando selección por marco")
                    else:
                        # Finalizar selección por marco
                        # Validar coordenadas del rectángulo de selección
                        if (
                            self.box_start is not None
                            and self.box_curr is not None
                            and not (
                                self.box_start.X == self.box_curr.X
                                and self.box_start.Y == self.box_curr.Y
                            )
                        ):
                            self.selected_element_id = None
                            sel: Set[Tuple[str, int, int, int, str]] = set()

                            if self.preview_mode:
                                # Usar la nueva función para seleccionar múltiples elementos
                                sel = self._select_elements_in_box(self.box_start, self.box_curr)

                            self.selected_segments = sel
                            if sel:
                                print(f"[INT] Seleccionados {len(sel)} segmentos por marco")
                                # Resaltar todos los elementos seleccionados
                                self._highlight_selected_elements()
                            else:
                                print("[INT] Ningún segmento seleccionado en el rectángulo")
                                self.highlight_geometries = []  # Limpiar highlights

                        else:
                            # Rectángulo inválido: limpiar selección
                            self.selected_segments.clear()
                            print(
                                "[INT] Rectángulo de selección inválido - selección cancelada"
                            )

                        self.box_selecting = False
                        self.box_start = None
                        self.box_curr = None
                else:
                    # Si no se puede iniciar selección por marco, informar al usuario
                    if not self.box_selecting:
                        print(
                            "[INT] Selección por marco no disponible en el modo actual"
                        )

                self._draw_preview(current_pnt)
                return True

        # ----------------------------------------------------------------------
        # 3. MODO EDICION (Edición y Manipulación)
        # ----------------------------------------------------------------------
        elif self.extend_mode:
            self.box_selecting = False
            current_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, AllplanGeo.Point3D(), True
            ).GetPoint()

            # Preserve Z of the vertex being dragged (GetInputPoint projects to Z=0)
            if self.saved_dragging is not None and self.saved_dragging_original_point is not None:
                current_pnt = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, self.saved_dragging_original_point.Z)

            if self.coord_input.IsMouseMove(mouse_msg):
                # A) Si ya estamos arrastrando algo, actualizamos posición
                if self.saved_dragging is not None:
                    pidx, vidx = self.saved_dragging
                    self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(current_pnt)
                    self.saved_hover_point = None
                    self.hover_mid = None
                    self.hover_seg = None

                # B) Si no hay drag, buscamos qué hay bajo el mouse (PREVIEW)
                else:
                    if self.box_selecting and (self.box_start is not None):
                        self.box_curr = AllplanGeo.Point3D(current_pnt)
                    else:
                        # --- JERARQUÍA DE DETECCIÓN ---
                        self.saved_hover_point = self._find_hover_saved_point(current_pnt, mode)

                        # ── Detectar si el punto hovereado es un junction o vértice cortable ──
                        self.hover_cut_vertex = None
                        if self.saved_hover_point is not None:
                            path_idx, pt_idx = self.saved_hover_point[0], self.saved_hover_point[1]
                            junction = self._is_junction_point(path_idx, pt_idx)
                            if junction is not None:
                                self.hover_cut_vertex = junction  # (left_idx, right_idx)
                            elif self.cut_mode and self._is_cuttable_vertex(path_idx, pt_idx):
                                self.hover_cut_vertex = ("vertex", path_idx, pt_idx)

                        self.hover_mid = (
                            None if self.saved_hover_point
                            else self._find_hover_midpoint(current_pnt, mode)
                        )

                        self.hover_seg = (
                            None if (self.saved_hover_point or self.hover_mid)
                            else self._find_hover_segment(current_pnt, mode)
                        )

                        # --- LÓGICA DE PREVIEW DE INSERCIÓN ---
                        if self.insert_mode and not self.saved_hover_point:
                            if self.hover_mid:
                                # ── Snap exacto al MIDPOINT ──────────────────────────────
                                _, path_idx, seg_idx, mp = self.hover_mid
                                self.hover_seg        = ("tubo", path_idx, seg_idx)
                                self.insert_preview_p = mp
                                self.insert_target    = self.hover_seg

                            elif self.hover_seg:
                                # ── Posición libre sobre el SEGMENTO ────────────────────
                                a, b = self._get_segment_endpoints(self.hover_seg)
                                if a and b:
                                    t, q = self._segment_project_point(a, b, current_pnt, mode)
                                    if self._can_insert_here(a, b, t):
                                        self.insert_preview_p = q
                                        self.insert_target    = self.hover_seg
                                    else:
                                        self.insert_preview_p = self.insert_target = None

                            else:
                                # ── Sin hover → limpiar ──────────────────────────────────
                                self.insert_preview_p = self.insert_target = None

                        else:
                            self.insert_preview_p = self.insert_target = None

                self._draw_preview(current_pnt)
                return True

            if is_left_click:
                # ─────────────────────────────────────────────────────────────────
                # 1. FINALIZAR DRAG (máxima prioridad: siempre primero)
                # ─────────────────────────────────────────────────────────────────
                if self.saved_dragging is not None:
                    pidx, vidx = self.saved_dragging
                    if self.saved_dragging_original_point:
                        p_final = AllplanGeo.Point3D(current_pnt)
                        self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(p_final)
                        self._update_segments_after_vertex_drag(pidx, vidx, self.saved_dragging_original_point, mode)
                    self.saved_dragging = self.saved_dragging_original_point = None
                    self._draw_preview(current_pnt)
                    return True

                # ─────────────────────────────────────────────────────────────────
                # 2. MODO CORTE (excluyente: no puede combinarse con drag/select)
                # ─────────────────────────────────────────────────────────────────
                if self.cut_mode:
                    try:
                        # ── Corte en vértice existente ──────────────────────────────
                        hover_pt = self._find_hover_saved_point(current_pnt, mode)
                        if hover_pt is not None:
                            v_path, v_idx, _ = hover_pt
                            if self._is_cuttable_vertex(v_path, v_idx):
                                pts = self.script_object.saved_paths[v_path]
                                cut_pt = AllplanGeo.Point3D(pts[v_idx].X, pts[v_idx].Y, pts[v_idx].Z)
                                left  = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in pts[:v_idx + 1]]
                                right = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in pts[v_idx:]]
                                self.script_object.saved_paths.pop(v_path)
                                self.script_object.saved_paths.insert(v_path, right)
                                self.script_object.saved_paths.insert(v_path, left)
                                self.script_object.saved_cut_points.append(cut_pt)
                                self.script_object.saved_vertex_cut_points.append(cut_pt)
                                self.selected_segments.clear()
                                self.selected_seg      = None
                                self.selected_junction = None
                                self.hover_seg         = None
                                self._draw_preview(current_pnt)
                                return True

                        # ── Corte en punto proyectado sobre segmento ─────────────────
                        target = self._find_hover_segment(current_pnt, mode)
                        if target is None:
                            return True
                        kind, path_idx, seg_idx, _ = target

                        if kind == "tubo":
                            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                                return True
                            pts = self.script_object.saved_paths[path_idx]
                        else:
                            pts = self.points

                        if not pts or len(pts) < 2 or not (0 <= seg_idx < len(pts) - 1):
                            return True

                        a, b = pts[seg_idx], pts[seg_idx + 1]
                        t, q = self._segment_project_point(a, b, current_pnt, mode)

                        if t <= 1e-3 or t >= 1.0 - 1e-3:
                            return True
                        try:
                            if q.GetDistance(a) < 1.0 or q.GetDistance(b) < 1.0:
                                return True
                        except Exception:
                            pass

                        q3 = AllplanGeo.Point3D(q.X, q.Y, q.Z)

                        insert_at = seg_idx + 1
                        pts_new = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in pts]
                        pts_new.insert(insert_at, q3)

                        left  = pts_new[: insert_at + 1]
                        right = pts_new[insert_at:]
                        if len(left) < 2 or len(right) < 2:
                            return True

                        if kind == "tubo":
                            self.script_object.saved_paths.pop(path_idx)
                            self.script_object.saved_paths.insert(path_idx, right)
                            self.script_object.saved_paths.insert(path_idx, left)
                        else:
                            self.points = left
                            self.script_object.saved_paths.append(right)

                        self.script_object.saved_cut_points.append(
                            AllplanGeo.Point3D(q3.X, q3.Y, q3.Z)
                        )

                        self.selected_segments.clear()
                        self.selected_seg      = None
                        self.selected_junction = None
                        self.hover_seg         = None

                        self._draw_preview(current_pnt)
                        return True
                    except Exception as ex:
                        print(f"[CUT] Error añadiendo corte: {ex}")
                        self._draw_preview(current_pnt)
                        return True
                # ─────────────────────────────────────────────────────────────────
                # A partir de aquí: recalcular hover con la posición de click
                # ─────────────────────────────────────────────────────────────────
                self.saved_hover_point = self._find_hover_saved_point(current_pnt, mode)

                # ─────────────────────────────────────────────────────────────────
                # 3. SELECCIONAR / DESELECCIONAR PUNTO DE CORTE (junction)
                # ─────────────────────────────────────────────────────────────────
                if self.saved_hover_point and not self.insert_mode:
                    path_idx, pt_idx, pt_pos = self.saved_hover_point
                    if self._is_junction_point(path_idx, pt_idx) is not None:
                        # Toggle selección
                        if (self.selected_junction is not None
                                and self.selected_junction[0] == path_idx
                                and self.selected_junction[1] == pt_idx):
                            self.selected_junction = None
                            print("[INT] Junction deseleccionado")
                        else:
                            self.selected_junction = (path_idx, pt_idx, pt_pos)
                            self.selected_seg = None
                            self.selected_segments.clear()
                            print(f"[INT] Junction seleccionado: path={path_idx}, pt={pt_idx}")
                        self.hover_seg = None
                        self._draw_preview(current_pnt)
                        return True

                # ─────────────────────────────────────────────────────────────────
                # 4. INICIAR DRAG de vértice normal (no junction, no cut_mode)
                # ─────────────────────────────────────────────────────────────────
                if self.saved_hover_point and not self.insert_mode:
                    pidx, vidx, _ = self.saved_hover_point
                    original = self.script_object.saved_paths[pidx][vidx]
                    self.saved_dragging_original_point = AllplanGeo.Point3D(original)
                    self.saved_dragging = (pidx, vidx)
                    self._draw_preview(current_pnt)
                    return True

                # ─────────────────────────────────────────────────────────────────
                # 5. INSERTAR PUNTO en segmento
                # ─────────────────────────────────────────────────────────────────
                if self.insert_mode:
                    self.hover_seg = self._find_hover_segment(current_pnt, mode)
                    if self.hover_seg:
                        a, b = self._get_segment_endpoints(self.hover_seg)
                        if a and b:
                            t, q = self._segment_project_point(a, b, current_pnt, mode)
                            if self._can_insert_here(a, b, t):
                                self._insert_on_segment(self.hover_seg, q, keep_selection_left=True, mode=mode)
                                self.insert_preview_p = self.insert_target = self.hover_seg = None
                                self._draw_preview(current_pnt)
                                return True
                    self._draw_preview(current_pnt)
                    return True

                # ─────────────────────────────────────────────────────────────────
                # 6. SELECCIONAR SEGMENTO
                # ─────────────────────────────────────────────────────────────────
                self.hover_seg = self._find_hover_segment(current_pnt, mode)
                if self.hover_seg:
                    if self.selected_segments:
                        if self.hover_seg in self.selected_segments:
                            self.selected_segments.remove(self.hover_seg)
                        else:
                            self.selected_segments.add(self.hover_seg)
                    else:
                        self.selected_seg = (
                            None if self._seg_equal(self.selected_seg, self.hover_seg)
                            else self.hover_seg
                        )

                self._draw_preview(current_pnt)
                return True

        return result

    def _find_hover_cut_vertex(self, current_pnt, mode) -> tuple | None:
        """
        Detecta vértices intermedios (codos) candidatos para corte.
        Retorna (path_idx, vertex_idx, point) o None.
        Excluye el primer y último vértice de cada path.
        """
        view_mode = self._get_view_mode(mode)
        threshold = 50.0 if view_mode != "XYZ" else 100.0

        for pidx, path in enumerate(self.script_object.saved_paths):
            if len(path) < 3:
                continue

            for vidx in range(1, len(path) - 1):
                vertex = path[vidx]

                dx = current_pnt.X - vertex.X
                dy = current_pnt.Y - vertex.Y

                # ── En XZ ignoramos Y, en YZ ignoramos X ─────────────────
                if view_mode == "XYZ":
                    dz = current_pnt.Z - vertex.Z
                elif view_mode == "XZ":
                    dz = current_pnt.Z - vertex.Z
                    dy = 0.0
                elif view_mode == "YZ":
                    dz = current_pnt.Z - vertex.Z
                    dx = 0.0
                else:  # XY
                    dz = 0.0

                distance = (dx**2 + dy**2 + dz**2) ** 0.5

                if distance <= threshold:
                    return (pidx, vidx, vertex)

        return None

     # ---------- Detección y borrado de puntos de corte (junction) ----------

    def _is_cuttable_vertex(self, path_idx: int, pt_idx: int) -> bool:
        """Devuelve True si el vértice es interior (cortable): no es primero ni último
        del path y el path tiene ≥ 3 puntos (ambos fragmentos quedan con ≥ 2 puntos)."""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return False
        pts = self.script_object.saved_paths[path_idx]
        return len(pts) >= 3 and 1 <= pt_idx <= len(pts) - 2

    def _is_junction_point(self, path_idx: int, pt_idx: int) -> Optional[Tuple[int, int]]:
        """
        Detecta si un punto guardado es un punto de corte (junction entre dos paths adyacentes).
        Retorna (left_path_idx, right_path_idx) si es junction, None si no.
        """
        if not self.script_object.saved_paths or path_idx < 0 or path_idx >= len(self.script_object.saved_paths):
            return None
        pts = self.script_object.saved_paths[path_idx]
        if not pts or pt_idx < 0 or pt_idx >= len(pts):
            return None
        TOL_SQ = 1e-3 * 1e-3
        # Caso 1: último punto del path -> match con primer punto del siguiente
        if pt_idx == len(pts) - 1 and path_idx + 1 < len(self.script_object.saved_paths):
            next_pts = self.script_object.saved_paths[path_idx + 1]
            if next_pts and self._dist_sq(pts[-1], next_pts[0]) < TOL_SQ:
                return (path_idx, path_idx + 1)
        # Caso 2: primer punto del path -> match con último punto del anterior
        if pt_idx == 0 and path_idx > 0:
            prev_pts = self.script_object.saved_paths[path_idx - 1]
            if prev_pts and self._dist_sq(pts[0], prev_pts[-1]) < TOL_SQ:
                return (path_idx - 1, path_idx)
        return None

    def delete_cut_point(self) -> bool:
        """
        Elimina el punto de corte bajo hover y fusiona los dos paths adyacentes,
        restaurando la continuidad de la polilínea.
        """
        if self.saved_hover_point is None:
            return False
        path_idx, pt_idx, _ = self.saved_hover_point
        junction = self._is_junction_point(path_idx, pt_idx)
        if junction is None:
            return False
        left_idx, right_idx = junction
        left_pts = self.script_object.saved_paths[left_idx]
        right_pts = self.script_object.saved_paths[right_idx]

        # Determinar si el corte fue hecho en un vértice existente
        cut_pt = left_pts[-1]
        TOL_SQ = 1e-3 * 1e-3
        is_vertex_cut = any(
            self._dist_sq(cut_pt, p) < TOL_SQ
            for p in self.script_object.saved_vertex_cut_points
        )

        if is_vertex_cut:
            # Corte en vértice: conservar el vértice → left + right[1:]
            merged = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left_pts] + \
                     [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right_pts[1:]]
        else:
            # Corte en segmento: eliminar el punto proyectado → left[:-1] + right[1:]
            merged = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left_pts[:-1]] + \
                     [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right_pts[1:]]

        self.script_object.saved_paths.pop(right_idx)
        self.script_object.saved_paths[left_idx] = merged

        # Eliminar de saved_cut_points y saved_vertex_cut_points
        self.script_object.saved_cut_points = [
            p for p in self.script_object.saved_cut_points
            if self._dist_sq(p, cut_pt) >= TOL_SQ
        ]
        self.script_object.saved_vertex_cut_points = [
            p for p in self.script_object.saved_vertex_cut_points
            if self._dist_sq(p, cut_pt) >= TOL_SQ
        ]

        self.get_segments()
        self._update_segment_groups()    # Re-mapea puntos con los nuevos SegmentItems

        # 3. RE-DIBUJO TOTAL
        self.script_object._create_elements_preview() # Limpia element_list y crea nuevos 3D
        self._generate_elements_for_preview()         # Envía al Viewport de Allplan

        self.insert_preview_p = None
        self.insert_target = None
        self.hover_mid = None

        # Limpiar estado de selección
        self.saved_hover_point = None
        self.selected_seg = None
        self.selected_junction = None
        self.hover_seg = None
        print(f"[INT] Punto de corte eliminado: paths {left_idx}+{right_idx} fusionados ({len(merged)} puntos)")
        return True

    def get_dist_in_plane(self, p1, p2, mode, proj_data=None):
        """Calcula la distancia entre dos puntos ignorando el eje perpendicular a la vista."""
        if mode == "XY":
            return math.sqrt((p1.X - p2.X)**2 + (p1.Y - p2.Y)**2)
        elif mode == "XZ":
            return math.sqrt((p1.X - p2.X)**2 + (p1.Z - p2.Z)**2)
        elif mode == "YZ":
            return math.sqrt((p1.Y - p2.Y)**2 + (p1.Z - p2.Z)**2)
        else:
            # --- MEJORA PARA ISOMÉTRICAS (XYZ) ---
            # Proyectamos los puntos 3D a coordenadas de vista (2D en pantalla)
            if not proj_data:
                proj_data = self.coord_input.GetViewWorldProjection() # type: ignore
            # WorldToView proyecta el punto 3D al plano 2D de la ventana actual
            p1_2d = proj_data.WorldToView(p1)
            p2_2d = proj_data.WorldToView(p2)

            # #Calculamos la distancia en unidades de vista (píxeles/pantalla)
            return math.sqrt((p1_2d.X - p2_2d.X)**2 + (p1_2d.Y - p2_2d.Y)**2)
            # Isométrica: distancia 3D completa en mm
            # return math.sqrt((p1_2d.X - p2_2d.X)**2 + (p1_2d.Y - p2_2d.Y)**2 + (p1.Z - p2.Z)**2)

    def _get_view_mode(self, view_type):
        """Mapea el tipo de proyección de Allplan a un string de modo."""
        XY = [AllplanIFW.eProjectionType.GROUND_PLAN, AllplanIFW.eProjectionType.WORKING_PLANE_VIEW]
        XZ = [AllplanIFW.eProjectionType.SOUTH_VIEW, AllplanIFW.eProjectionType.NORTH_VIEW]
        YZ = [AllplanIFW.eProjectionType.EAST_VIEW, AllplanIFW.eProjectionType.WEST_VIEW]

        if view_type in XY: return "XY"
        if view_type in XZ: return "XZ"
        if view_type in YZ: return "YZ"
        return "XYZ"

    def _get_t_projected(self, p1, p2, rp, mode, proj_data=None):
        """Calcula el factor t de proyección escalar según el plano de la vista."""
        if mode == "XY":
            dx, dy = p2.X - p1.X, p2.Y - p1.Y
            return ((rp.X - p1.X) * dx + (rp.Y - p1.Y) * dy) / (dx*dx + dy*dy) if (dx*dx + dy*dy) != 0 else -1.0
        elif mode == "XZ":
            dx, dz = p2.X - p1.X, p2.Z - p1.Z
            return ((rp.X - p1.X) * dx + (rp.Z - p1.Z) * dz) / (dx*dx + dz*dz) if (dx*dx + dz*dz) != 0 else -1.0
        elif mode == "YZ":
            dy, dz = p2.Y - p1.Y, p2.Z - p1.Z
            return ((rp.Y - p1.Y) * dy + (rp.Z - p1.Z) * dz) / (dy*dy + dz*dz) if (dy*dy + dz*dz) != 0 else -1.0
        else:
            # --- SOLUCIÓN PARA ISOMÉTRICA ---
            if not proj_data:
                proj_data = self.coord_input.GetViewWorldProjection() # type: ignore

            # Convertimos todo al espacio de la pantalla (2D)
            p1_view = proj_data.WorldToView(p1)
            p2_view = proj_data.WorldToView(p2)
            rp_view = proj_data.WorldToView(rp) # El click ya suele estar en view, pero aseguramos

            dx = p2_view.X - p1_view.X
            dy = p2_view.Y - p1_view.Y

            mag_sq = dx*dx + dy*dy
            if mag_sq == 0: return 0.0

            # Proyección escalar en 2D (pantalla)
            dot = (rp_view.X - p1_view.X) * dx + (rp_view.Y - p1_view.Y) * dy
            return dot / mag_sq

    def get_smart_snap_proyectado(self, raw_pnt):
        """
        Versión optimizada: Detecta el plano de vista y realiza snap a
        geometría 3D real usando proyecciones 2D.
        """
        # 1. Obtener modo de vista (centralizado)
        proj_data = self.coord_input.GetViewWorldProjection() # type: ignore
        view_type = proj_data.GetIsoProjection()

        mode = self._get_view_mode(view_type) # Extraído a un helper para limpieza

        # Configuraciones de Snap
        SNAP_TOLERANCE = 1.0
        closest_pnt = AllplanGeo.Point3D(raw_pnt)
        is_snapped = False
        min_dist = float('inf')

        if not hasattr(self, 'last_points') or not self.last_points:
            return raw_pnt, False

        # --- A. SNAP A VÉRTICES (Prioridad 1) ---
        for p in self.last_points:
            dist = self.get_dist_in_plane(p, raw_pnt, mode)
            if dist < SNAP_TOLERANCE and dist < min_dist:
                min_dist = dist
                closest_pnt = AllplanGeo.Point3D(p)
                is_snapped = True

        if is_snapped:
            return closest_pnt, True

        # --- B. SNAP A ARISTAS (Prioridad 2) ---
        for i in range(len(self.last_points) - 1):
            p1, p2 = self.last_points[i], self.last_points[i + 1]

            # Obtener factor de proyección 't' en el plano actual
            t = self._get_t_projected(p1, p2, raw_pnt, mode, proj_data)

            if 0.0 <= t <= 1.0:
                # Interpolar punto 3D real
                proj_pnt_3d = AllplanGeo.Point3D(
                    p1.X + t * (p2.X - p1.X),
                    p1.Y + t * (p2.Y - p1.Y),
                    p1.Z + t * (p2.Z - p1.Z)
                )

                d_edge = self.get_dist_in_plane(proj_pnt_3d, raw_pnt, mode)

                if d_edge < SNAP_TOLERANCE and d_edge < min_dist:
                    min_dist = d_edge
                    closest_pnt = proj_pnt_3d
                    is_snapped = True

        return closest_pnt, is_snapped

    def _find_path_to_extend(self, point: AllplanGeo.Point3D, tolerance: float = 1.0):
        """
        Busca si 'point' coincide con CUALQUIER vértice de algún camino guardado.
        Retorna (path_index, vertex_index, point_object) o None.
        """
        for path_idx, path in enumerate(self.script_object.saved_paths):
            if not path:
                continue

            for vtx_idx, vtx in enumerate(path):
                # Cálculo de distancia euclidiana 3D
                dist = math.sqrt((vtx.X - point.X)**2 + (vtx.Y - point.Y)**2 + (vtx.Z - point.Z)**2)

                if dist <= tolerance:
                    # Retornamos la referencia al objeto original 'vtx'
                    return path_idx, vtx_idx, vtx

        return None

    def _find_hover_index(self, p: AllplanGeo.Point3D) -> int:
        if not self.points:
            return -1
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = -1
        best_d2 = max_d2 + 1.0
        for i, pt in enumerate(self.points):
            d2 = self._dist_sq(p, pt)
            if d2 <= max_d2 and d2 < best_d2:
                best_d2 = d2
                best = i
        return best

    # ============================================================================
    # METHODS FOR DRAWING THE POLYLINE IN THE ALLPLAN VIEWPORT
    # ============================================================================
    def _draw_preview(self, current_pnt: Any):
        """
        Función unificada de previsualización.
        Distingue entre:
        1. create_mode: Dibujo activo, rubber-band, guías de ángulos.
        2. preview_mode (Edit): Visualización de elementos 3D (tubos, codos) y layers.
        3. extended_mode: Lógica para edición avanzada.
        4. Fallback: Dibuja el esqueleto de la polilínea si no hay un modo dominante excluyente.
        """

        # Normalizar entrada (hover puede ser Point3D o None)
        hover = current_pnt if isinstance(current_pnt, AllplanGeo.Point3D) else None

        elems: List[AllplanBasisElements.ModelElement3D] = []

        # ============================================================================
        # 1. SETUP PROPERTIES (Común para todos los modos)
        # ============================================================================

        # Propiedades Base
        base_prop = self._clone_properties(self.com_prop)

        # Handles (Amarillos)
        handle_prop = self._clone_properties(self.com_prop)
        handle_prop.Color = 5 #COLORS.get("handle", 6)

        # Segmentos Guardados (Verde por defecto) (EXTENDED MODE)
        saved_prop = self._clone_properties(self.com_prop)
        saved_prop.Color = COLORS.get("preview_saved", 4)

        # Hover y Selección
        seg_hover_prop = self._clone_properties(self.com_prop)
        seg_hover_prop.Color = COLORS.get("segment_hover", 6)
        seg_hover_prop.ColorByLayer = False

        seg_sel_prop = self._clone_properties(self.com_prop)
        seg_sel_prop.Color = COLORS.get("segment_selected", 5)
        seg_sel_prop.ColorByLayer = False

        # Rectángulo de selección
        rect_prop = self._clone_properties(self.com_prop)
        rect_prop.Color = COLORS.get("rect_selection", 5)

         # Midpoints props (con pen propio y sin ByLayer)
        mid_prop = self._clone_properties(self.com_prop)
        mid_prop.Color = 1 #MIDPOINT_COLOR
        mid_prop.PenByLayer = False
        mid_prop.ColorByLayer = False
        mid_prop.StrokeByLayer = False
        try:
            mid_prop.Pen = max(MIDPOINT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass
        mid_size = HANDLE_SIZE * MIDPOINT_SIZE_FACTOR

        ins_prev_prop = self._clone_properties(self.com_prop)
        ins_prev_prop.Color = COLORS["insert_preview"]

        # 1. Obtener la proyección actual para decidir qué ejes dibujar
        proj_data = self.coord_input.GetViewWorldProjection() # type: ignore
        view_type = proj_data.GetIsoProjection()

        # # --- LÓGICA DE SNAP PARA DRAG ---
        # # Por defecto es la posición del ratón, pero si hay snap, se sobreescribe
        active_drag_pnt = current_pnt

        ISOM_VIEWS = {
            AllplanIFW.eProjectionType.SOUTH_WEST_VIEW,
            AllplanIFW.eProjectionType.SOUTH_EAST_VIEW,
            AllplanIFW.eProjectionType.NORTH_WEST_VIEW,
            AllplanIFW.eProjectionType.NORTH_EAST_VIEW,
            AllplanIFW.eProjectionType.FREE_VIEW,
        }
        XZ_VIEWS = {
            AllplanIFW.eProjectionType.SOUTH_VIEW,
            AllplanIFW.eProjectionType.NORTH_VIEW,
        }
        YZ_VIEWS = {
            AllplanIFW.eProjectionType.EAST_VIEW,
            AllplanIFW.eProjectionType.WEST_VIEW,
        }

        # ============================================================================
        # 2. DRAW SAVED POINTS (Con soporte para movimiento en tiempo real)
        # ============================================================================
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) >= 2:
                # 2.1 Generar lista de puntos para visualización (Network-Aware)
                display_pts = []
                for v_idx, vpt in enumerate(pts):
                    # Comprobamos si este vértice (de cualquier camino) coincide con la unión original
                    if (self.saved_dragging_original_point is not None and
                        self._points_equal(vpt, self.saved_dragging_original_point)):

                        # Usamos el punto ya procesado con el snap
                        display_pts.append(active_drag_pnt)
                    else:
                        display_pts.append(vpt)

                # 2.2 Dibujar Segmentos
                for seg_idx in range(len(display_pts) - 1):
                    a, b = display_pts[seg_idx], display_pts[seg_idx + 1]

                    # Determinar propiedades visuales (Selección / Hover)
                    is_selected = False
                    if self.selected_seg and self.selected_seg[0] == 'tubo' and \
                       self.selected_seg[1] == path_idx and self.selected_seg[2] == seg_idx:
                        is_selected = True

                    if ('tubo', path_idx, seg_idx) in getattr(self, 'selected_segments', set()):
                        is_selected = True

                    is_hovered = self.hover_seg and self.hover_seg[0] == 'tubo' and \
                                 self.hover_seg[1] == path_idx and self.hover_seg[2] == seg_idx

                    # Asignar Propiedad
                    if is_selected:
                        prop = seg_sel_prop
                    elif is_hovered and not self.is_dragging:
                        prop = seg_hover_prop
                    else:
                        prop = saved_prop

                    # Renderizar línea
                    elems.append(AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(a, b)))

                # Midpoints (guardadas)
                # 2.3 Dibujar Midpoints
                for si in range(len(display_pts) - 1):
                    # ── Usar display_pts (no pts) para sincronizar con el drag ──
                    a, b = display_pts[si], display_pts[si + 1]
                    mp = self._midpoint(a, b)

                    is_selected = (
                        self.selected_seg is not None
                        and self.selected_seg[0] == 'tubo'
                        and self.selected_seg[1] == path_idx
                        and self.selected_seg[2] == si
                    )

                    # ── Hover específico sobre el midpoint (usa hover_mid) ──────
                    is_hovered = (
                        self.hover_mid is not None
                        and self.hover_mid[0] == 'tubo'
                        and self.hover_mid[1] == path_idx
                        and self.hover_mid[2] == si
                    )
                    if is_selected:
                        prop = mid_prop
                    elif is_hovered and not self.is_dragging:
                        prop = mid_prop
                    else:
                        prop = mid_prop

                    elems.extend(self._create_cross_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

                # 2.4 Dibujar Vértices (Handlers)
                for vidx, vpt in enumerate(display_pts):
                    # ── Detectar junction por posición en saved_paths ────────────────
                    # Caso 1: último punto del path actual == primer punto del siguiente
                    # Caso 2: primer punto del path actual == último punto del anterior
                    junction_pair = None
                    if (vidx == len(display_pts) - 1
                            and path_idx + 1 < len(self.script_object.saved_paths)):
                        next_pts = self.script_object.saved_paths[path_idx + 1]
                        if next_pts and vpt.GetDistance(next_pts[0]) <= 1e-3:
                            junction_pair = (path_idx, path_idx + 1)

                    elif (vidx == 0
                            and path_idx > 0):
                        prev_pts = self.script_object.saved_paths[path_idx - 1]
                        if prev_pts and vpt.GetDistance(prev_pts[-1]) <= 1e-3:
                            junction_pair = (path_idx - 1, path_idx)

                    # ── JUNCTION: dibujar X + cuadrado de selección ──────────────────
                    if junction_pair is not None:
                        li, ri = junction_pair
                        cx, cy, cz = vpt.X, vpt.Y, vpt.Z

                        is_hovered = (
                            getattr(self, 'hover_cut_vertex', None) == junction_pair
                        )
                        is_selected = (
                            self.selected_junction is not None
                            and self.selected_junction[0] == li
                            and self.selected_junction[1] == len(self.script_object.saved_paths[li]) - 1
                        )

                        # Propiedades X
                        cut_prop = self._clone_properties(self.com_prop)
                        cut_prop.ColorByLayer  = False
                        cut_prop.PenByLayer    = False
                        cut_prop.StrokeByLayer = False
                        if is_selected:
                            cut_prop.Color = 5   # Amarillo
                        elif is_hovered:
                            cut_prop.Color = 7   # Blanco/hover
                        else:
                            cut_prop.Color = 6   # Rojo
                        try:
                            cut_prop.Pen = 3
                        except Exception:
                            pass

                        cut_size = 40 * (1.5 if (is_hovered or is_selected) else 1.0)
                        half = cut_size / 2.0

                        # Dibujar X según vista
                        if view_type in [AllplanIFW.eProjectionType.GROUND_PLAN,
                                         AllplanIFW.eProjectionType.WORKING_PLANE_VIEW]:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx + half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx - half, cy + half, cz))))

                        elif view_type in XZ_VIEWS:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy, cz - half),
                                                  AllplanGeo.Point3D(cx + half, cy, cz + half))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy, cz - half),
                                                  AllplanGeo.Point3D(cx - half, cy, cz + half))))

                        elif view_type in YZ_VIEWS:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy - half, cz - half),
                                                  AllplanGeo.Point3D(cx, cy + half, cz + half))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy + half, cz - half),
                                                  AllplanGeo.Point3D(cx, cy - half, cz + half))))

                        elif view_type in ISOM_VIEWS:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx + half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx - half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy, cz - half),
                                                  AllplanGeo.Point3D(cx, cy, cz + half))))

                        # Cuadrado de selección (hover o seleccionado)
                        if is_selected or is_hovered:
                            sq_prop = self._clone_properties(self.com_prop)
                            sq_prop.ColorByLayer  = False
                            sq_prop.PenByLayer    = False
                            sq_prop.StrokeByLayer = False
                            sq_prop.Color = 5 if is_selected else 7
                            try:
                                sq_prop.Pen = 1
                            except Exception:
                                pass

                            sq = cut_size * 0.9

                            if view_type in [AllplanIFW.eProjectionType.GROUND_PLAN,
                                             AllplanIFW.eProjectionType.WORKING_PLANE_VIEW]:
                                poly_sq = AllplanGeo.Polyline3D()
                                for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                                    poly_sq += AllplanGeo.Point3D(cx + dx*sq, cy + dy*sq, cz)
                                elems.append(AllplanBasisElements.ModelElement3D(sq_prop, poly_sq))

                            elif view_type in XZ_VIEWS:
                                poly_sq = AllplanGeo.Polyline3D()
                                for dx, dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                                    poly_sq += AllplanGeo.Point3D(cx + dx*sq, cy, cz + dz*sq)
                                elems.append(AllplanBasisElements.ModelElement3D(sq_prop, poly_sq))

                            elif view_type in YZ_VIEWS:
                                poly_sq = AllplanGeo.Polyline3D()
                                for dy, dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                                    poly_sq += AllplanGeo.Point3D(cx, cy + dy*sq, cz + dz*sq)
                                elems.append(AllplanBasisElements.ModelElement3D(sq_prop, poly_sq))

                            elif view_type in ISOM_VIEWS:
                                bot = [AllplanGeo.Point3D(cx + dx*sq, cy + dy*sq, cz - sq)
                                       for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                                top = [AllplanGeo.Point3D(cx + dx*sq, cy + dy*sq, cz + sq)
                                       for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                                for i in range(4):
                                    elems.append(AllplanBasisElements.ModelElement3D(sq_prop,
                                        AllplanGeo.Line3D(bot[i], bot[(i+1)%4])))
                                    elems.append(AllplanBasisElements.ModelElement3D(sq_prop,
                                        AllplanGeo.Line3D(top[i], top[(i+1)%4])))
                                    elems.append(AllplanBasisElements.ModelElement3D(sq_prop,
                                        AllplanGeo.Line3D(bot[i], top[i])))

                        # Junction dibujado, saltar handle normal
                        continue

                    # ── Vértice normal ───────────────────────────────────────────────
                    is_hovered_vtx = (
                        self.saved_hover_point is not None
                        and self.saved_hover_point[0] == path_idx
                        and self.saved_hover_point[1] == vidx
                    )

                    # En cut_mode: vértice cortable hovereado → X de corte en lugar de círculo
                    if self.cut_mode and is_hovered_vtx and self._is_cuttable_vertex(path_idx, vidx):
                        cx, cy, cz = vpt.X, vpt.Y, vpt.Z
                        cut_prop = self._clone_properties(self.com_prop)
                        cut_prop.ColorByLayer  = False
                        cut_prop.PenByLayer    = False
                        cut_prop.StrokeByLayer = False
                        cut_prop.Color = 7   # blanco/hover
                        try:
                            cut_prop.Pen = 3
                        except Exception:
                            pass
                        half = HANDLE_SIZE * 0.75

                        if view_type in [AllplanIFW.eProjectionType.GROUND_PLAN,
                                         AllplanIFW.eProjectionType.WORKING_PLANE_VIEW]:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx + half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx - half, cy + half, cz))))
                        elif view_type in XZ_VIEWS:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy, cz - half),
                                                  AllplanGeo.Point3D(cx + half, cy, cz + half))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy, cz - half),
                                                  AllplanGeo.Point3D(cx - half, cy, cz + half))))
                        elif view_type in YZ_VIEWS:
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy - half, cz - half),
                                                  AllplanGeo.Point3D(cx, cy + half, cz + half))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy + half, cz - half),
                                                  AllplanGeo.Point3D(cx, cy - half, cz + half))))
                        else:  # isométrica
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx - half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx + half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx + half, cy - half, cz),
                                                  AllplanGeo.Point3D(cx - half, cy + half, cz))))
                            elems.append(AllplanBasisElements.ModelElement3D(cut_prop,
                                AllplanGeo.Line3D(AllplanGeo.Point3D(cx, cy, cz - half),
                                                  AllplanGeo.Point3D(cx, cy, cz + half))))
                        continue

                    size = HANDLE_SIZE

                    if self.saved_dragging is not None and self.saved_dragging == (path_idx, vidx):
                        size = HANDLE_SIZE * DRAG_SCALE

                    if is_hovered_vtx:
                        size = HANDLE_SIZE * HOVER_SCALE

                    elems.extend(self._create_point_marker(vpt, handle_prop, size))

        # ----------------------------------------------------------------------------
        # A) CREATE MODE
        # ----------------------------------------------------------------------------
        # Activa + rubber-band (si hay activa)
        if self.points:
            poly = AllplanGeo.Polyline3D()
            for pt in self.points:
                poly += pt
            if hover is not None and not self.is_dragging and self.hover_seg is None and self.create_mode:
                poly += hover
            elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))

            # Handles (activa)
            for idx, pt in enumerate(self.points):
                size = HANDLE_SIZE * 0.65
                if idx == self.hover_index and not self.is_dragging:
                    size = HANDLE_SIZE * HOVER_SCALE
                if idx == self.drag_index and self.is_dragging:
                    size = HANDLE_SIZE * DRAG_SCALE
                elems.extend(self._create_point_marker(pt, handle_prop, size))

            # Selección/hover en activa (con overlay + z-bias)
            selected_i = self.selected_seg[2] if (self.selected_seg and self.selected_seg[0] == 'active') else -1
            hovered_i  = self.hover_seg[2]    if (self.hover_seg    and self.hover_seg[0]    == 'active') else -1

            if selected_i != -1 and 0 <= selected_i < len(self.points) - 1:
                a, b = self.points[selected_i], self.points[selected_i+1]
                elems.append(AllplanBasisElements.ModelElement3D(
                    seg_sel_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)
                ))

            if self.hover_seg and self.hover_seg[0] == 'active' and not self.is_dragging:
                si = self.hover_seg[2]
                if si != selected_i and 0 <= si < len(self.points) - 1:
                    a, b = self.points[si], self.points[si+1]
                    elems.append(AllplanBasisElements.ModelElement3D(
                        seg_hover_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)
                    ))

            # Midpoints (activa) como cruzetas
            if len(self.points) >= 2:
                for si in range(len(self.points) - 1):
                    a, b = self.points[si], self.points[si+1]
                    mp = self._midpoint(a, b)
                    if si == selected_i:
                        elems.extend(self._create_cross_marker(mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    elif si == hovered_i and not self.is_dragging:
                        elems.extend(self._create_cross_marker(mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    else:
                        elems.extend(self._create_cross_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

        # ----------------------------------------------------------------------------
        # B) EDIT MODE - LAYERS / ATRIBUTES
        # ----------------------------------------------------------------------------
        if self.edit_mode:
            # Highlights de geometrías múltiples
            for highlight_info in getattr(self, "highlight_geometries", []):
                highlight_geom = highlight_info.get('geometry')
                if highlight_geom:
                    com_prop = AllplanBaseElements.CommonProperties()
                    com_prop.Color = 250
                    com_prop.Pen = 5
                    try:
                        elems.append(AllplanBasisElements.ModelElement3D(com_prop, highlight_geom))
                    except: pass

            # DIBUJAR ELEMENTOS GENERADOS
            generated_paths = getattr(self, "generated_elements", [])
            for path_group in generated_paths:  # Primer nivel: Las rutas
                for element in path_group:      # Segundo nivel: Los elementos
                    elem_prop = self._clone_properties(self.com_prop)
                    elem_prop.Color = 4 if element.get('type') == 'tubo' else 1
                    elem_prop.ColorByLayer = False
                    elem_prop.PenByLayer = False

                    # Dibujar Geometría Principal
                    # geom = element.get('geometry')
                    # if geom:
                    #     try:
                    #         elems.append(AllplanBasisElements.ModelElement3D(elem_prop, geom))
                    #     except: pass

                    # Dibujar Marcadores de posición (+)
                    pos = element.get('position')
                    if pos:
                        marker_prop = self._clone_properties(self.com_prop)
                        marker_prop.Color = 6
                        marker_size = HANDLE_SIZE * 0.5
                        try:
                            # Cruz XY
                            p1 = AllplanGeo.Point3D(pos.X - marker_size, pos.Y, pos.Z)
                            p2 = AllplanGeo.Point3D(pos.X + marker_size, pos.Y, pos.Z)
                            elems.append(AllplanBasisElements.ModelElement3D(marker_prop, AllplanGeo.Line3D(p1, p2)))
                            p3 = AllplanGeo.Point3D(pos.X, pos.Y - marker_size, pos.Z)
                            p4 = AllplanGeo.Point3D(pos.X, pos.Y + marker_size, pos.Z)
                            elems.append(AllplanBasisElements.ModelElement3D(marker_prop, AllplanGeo.Line3D(p3, p4)))
                        except: pass

            # Render element 3D
            if self.script_object.element_list:
                new_list: List[Any]  = []
                for sub_list in self.script_object.element_list:
                    new_list = [e.element for e in sub_list]
                    elems.extend(new_list)

        # ============================================================================
        # MARCADOR DE HOVER/SNAP (Independiente de is_snapped, activo en todos los modos)
        # ============================================================================
        # Determinar si hay un punto de hover activo y cuál es
        marker_pnt = None

        # Prioridad 1: Snap activo sobre el cursor
        if hasattr(self, 'is_snapped') and self.is_snapped and isinstance(current_pnt, AllplanGeo.Point3D):
            marker_pnt = current_pnt

        # Prioridad 2: Hover sobre vértice guardado
        elif self.saved_hover_point is not None:
            pidx, vidx = self.saved_hover_point[0], self.saved_hover_point[1]
            try:
                marker_pnt = self.script_object.saved_paths[pidx][vidx]
            except (IndexError, TypeError):
                pass

        # Prioridad 3: Hover sobre punto medio de segmento guardado
        elif (self.hover_mid and self.hover_mid[0] == 'tubo' and not self.is_dragging):
            pidx, sidx = self.hover_mid[1], self.hover_mid[2]
            try:
                pts = self.script_object.saved_paths[pidx]
                marker_pnt = self._midpoint(pts[sidx], pts[sidx + 1])
            except (IndexError, TypeError):
                pass

        # Prioridad 4: Hover sobre punto medio de segmento activo
        elif (self.hover_seg and self.hover_seg[0] == 'tubo' and not self.is_dragging):
            sidx = self.hover_seg[3]
            try:
                marker_pnt = sidx
            except (IndexError, TypeError):
                pass

        # --- Dibujar el marcador si hay un punto ---
        if marker_pnt is not None:
            marker_props = self._clone_properties(self.com_prop)
            marker_props.Color = 6  # Magenta

            size = SNAP_SIZE
            half = size / 2.0
            cx, cy, cz = marker_pnt.X, marker_pnt.Y, marker_pnt.Z

            if view_type in [AllplanIFW.eProjectionType.GROUND_PLAN,
                            AllplanIFW.eProjectionType.WORKING_PLANE_VIEW]:
                sq = AllplanGeo.Polyline3D()
                for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                    sq += AllplanGeo.Point3D(cx + dx*half, cy + dy*half, cz)
                elems.append(AllplanBasisElements.ModelElement3D(marker_props, sq))

            elif view_type in XZ_VIEWS:
                sq = AllplanGeo.Polyline3D()
                for dx, dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                    sq += AllplanGeo.Point3D(cx + dx*half, cy, cz + dz*half)
                elems.append(AllplanBasisElements.ModelElement3D(marker_props, sq))

            elif view_type in YZ_VIEWS:
                sq = AllplanGeo.Polyline3D()
                for dy, dz in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]:
                    sq += AllplanGeo.Point3D(cx, cy + dy*half, cz + dz*half)
                elems.append(AllplanBasisElements.ModelElement3D(marker_props, sq))

            elif view_type in ISOM_VIEWS:
                # Cubo 3D completo
                bot = [AllplanGeo.Point3D(cx + dx*half, cy + dy*half, cz - half)
                    for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                top = [AllplanGeo.Point3D(cx + dx*half, cy + dy*half, cz + half)
                    for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                for i in range(4):
                    elems.append(AllplanBasisElements.ModelElement3D(
                        marker_props, AllplanGeo.Line3D(bot[i], bot[(i+1)%4])))
                    elems.append(AllplanBasisElements.ModelElement3D(
                        marker_props, AllplanGeo.Line3D(top[i], top[(i+1)%4])))
                    elems.append(AllplanBasisElements.ModelElement3D(
                        marker_props, AllplanGeo.Line3D(bot[i], top[i])))

        if self.orientation_capture_mode and self.orientation_line_start is not None:
            try:
                orient_prop = self._clone_properties(self.com_prop)
                orient_prop.Color = 7  # verde
                orient_prop.ColorByLayer = False
                orient_prop.PenByLayer = False
                orient_prop.StrokeByLayer = False
                try:
                    orient_prop.Pen = 15
                except Exception:
                    pass

                if self.orientation_line_end is not None:
                    end_point = self.orientation_line_end
                elif self.orientation_line_preview is not None:
                    end_point = self.orientation_line_preview
                else:
                    end_point = hover

                if end_point is not None:
                    p1_xy = AllplanGeo.Point3D(self.orientation_line_start.X, self.orientation_line_start.Y, 0.0)
                    p2_xy = AllplanGeo.Point3D(end_point.X, end_point.Y, 0.0)
                    elems.append(AllplanBasisElements.ModelElement3D(orient_prop, AllplanGeo.Line3D(p1_xy, p2_xy)))
            except Exception:
                pass

        # ============================================================================
        # 3. GLOBAL COMMON ELEMENTS (Se dibujan sobre cualquier modo)
        # ============================================================================
        # Punto fantasma de inserción (checkbox ON)
        if (self.insert_mode and self.insert_preview_p is not None):
            elems.extend(self._create_point_marker(self.insert_preview_p, ins_prev_prop, HANDLE_SIZE * 0.95))

        # 1. Draw Selection Rectangle (If applicable)
        if (self.box_selecting and self.box_start is not None and self.box_curr is not None):
            try:
                view_proj = self.coord_input.GetViewWorldProjection() # type: ignore
                a_view = view_proj.WorldToView(self.box_start)
                b_view = view_proj.WorldToView(self.box_curr)
                p1_view = AllplanGeo.Point2D(a_view.X, a_view.Y)
                p2_view = AllplanGeo.Point2D(b_view.X, a_view.Y)
                p3_view = AllplanGeo.Point2D(b_view.X, b_view.Y)
                p4_view = AllplanGeo.Point2D(a_view.X, b_view.Y)

                p1 = view_proj.ViewToWorld(p1_view)
                p2 = view_proj.ViewToWorld(p2_view)
                p3 = view_proj.ViewToWorld(p3_view)
                p4 = view_proj.ViewToWorld(p4_view)

                for s, e in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
                    elems.append(AllplanBasisElements.ModelElement3D(rect_prop, AllplanGeo.Line3D(s, e)))
            except Exception:
                a, b = self.box_start, self.box_curr
                p1 = AllplanGeo.Point3D(a.X, a.Y, a.Z)
                p2 = AllplanGeo.Point3D(b.X, a.Y, a.Z)
                p3 = AllplanGeo.Point3D(b.X, b.Y, a.Z)
                p4 = AllplanGeo.Point3D(a.X, b.Y, a.Z)
                for s, e in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
                    elems.append(AllplanBasisElements.ModelElement3D(rect_prop, AllplanGeo.Line3D(s, e)))

        # 2. Selected individual highlight
        if getattr(self, "highlight_geometry", None):
            h_prop = self._clone_properties(self.com_prop)
            h_prop.Color = COLORS.get('highlight_element', 6)
            try:
                elems.append(AllplanBasisElements.ModelElement3D(h_prop, self.highlight_geometry))
            except: pass

        # 3. Tooltip y Render end
        self._draw_tooltip(elems)

        # ============================================================================
        # 4. RENDER END
        # ============================================================================
        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(), # type: ignore
            AllplanGeo.Matrix3D(),
            elems,
            True, # Clean previous
            None,
        )

    def _draw_selection_box(self, elems, prop):
        """Dibuja el rectángulo de selección proyectado en vista o XY"""
        try:
            view_proj = self.coord_input.GetViewWorldProjection() # type: ignore
            a_view = view_proj.WorldToView(self.box_start) # type: ignore
            b_view = view_proj.WorldToView(self.box_curr) # type: ignore

            p1 = view_proj.ViewToWorld(AllplanGeo.Point2D(a_view.X, a_view.Y))
            p2 = view_proj.ViewToWorld(AllplanGeo.Point2D(b_view.X, a_view.Y))
            p3 = view_proj.ViewToWorld(AllplanGeo.Point2D(b_view.X, b_view.Y))
            p4 = view_proj.ViewToWorld(AllplanGeo.Point2D(a_view.X, b_view.Y))

            lines = [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]
            for s, e in lines:
                elems.append(AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(s, e)))
        except:
            # Fallback XY simple
            pass

    def _add_marker_at_pos(self, elems, pos, prop, size_factor=0.5):
        """Crea una cruz simple en una posición 3D"""
        size = HANDLE_SIZE * size_factor
        try:
            p1 = AllplanGeo.Point3D(pos.X - size, pos.Y, pos.Z)
            p2 = AllplanGeo.Point3D(pos.X + size, pos.Y, pos.Z)
            p3 = AllplanGeo.Point3D(pos.X, pos.Y - size, pos.Z)
            p4 = AllplanGeo.Point3D(pos.X, pos.Y + size, pos.Z)
            elems.append(AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(p1, p2)))
            elems.append(AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(p3, p4)))
        except: pass

    def applie_info_element_selected(self):

        # 1. Actualizar el modelo de datos (build_ele)
        param = getattr(self.script_object.build_ele, ParamNames.Layers.DESCRIPTION)
        param.value = self._pending_description

        return True

    def _draw_tooltip(self, elems):
        """
        Dibuja el tooltip con información del elemento hover.

        Args:
            elems: Lista de elementos a agregar el tooltip
        """
        if not self.hover_tooltip_text or not self.hovered_element:
            return

        pos = self.hovered_element.get('position')
        if not pos:
            return

        # Offset MUY PEQUEÑO para que esté cerca del cursor (en coordenadas escaladas)
        offset_x = 200.0  # mm
        offset_y = 200.0  # mm

        # IMPORTANTE: Aplicar el escalado DESPUÉS de sumar el offset
        loc = AllplanGeo.Point2D(pos.X -offset_y, pos.Y - offset_x)
        try:
            text_prop = AllplanBasisElements.TextProperties()
            text_prop.Height = 0.4  # Tamaño del texto en mm
            text_prop.Width = 0.4
            text_prop.Alignment = AllplanBasisElements.TextAlignment.eMiddleBottom

            com_prop = AllplanBaseElements.CommonProperties()
            com_prop.Color = 250  # Color amarillo/blanco para destacar
            com_prop.Layer = 0  # Layer temporal

            # Crear elemento de texto
            text_elem = AllplanBasisElements.TextElement(
                com_prop,
                text_prop,
                self.hover_tooltip_text,
                loc
            )
            elems.append(text_elem)

        except Exception as e:
            print(f"[SO] Error dibujando tooltip: {e}")

    def _add_text_label(self, elems_list, point_a: AllplanGeo.Point3D, point_b: AllplanGeo.Point3D, text: str):
        """Añade un TextElement 2D en el centro del segmento, rotado según la dirección del segmento."""
        try:
            # Calcular centro del segmento
            cx = (point_a.X + point_b.X) * 0.5
            cy = (point_a.Y + point_b.Y) * 0.5
            loc = AllplanGeo.Point2D(cx, cy)

            # Crear propiedades específicas para el texto
            text_com_prop = AllplanBaseElements.CommonProperties()
            # No llamar GetGlobalProperties() para evitar escala global

            text_prop = AllplanBasisElements.TextProperties()
            text_prop.Height = 0.30  # Valor fijo pequeño
            text_prop.Width  = 0.30
            text_prop.IsScaleDependent = False

            elems_list.append(AllplanBasisElements.TextElement(text_com_prop, text_prop, text, loc))
        except Exception as ex:
            print(f"[INT] No se pudo crear etiqueta de texto: {ex}")

    # ============================================================================
    # DRAWING MODE CREATE
    # ============================================================================
    def _constrain_no_backtrack(
        self,
        raw_point: AllplanGeo.Point3D,
        last_point: AllplanGeo.Point3D,
        prev_point: AllplanGeo.Point3D,
        min_backtrack_deg: float = 25.0,
    ) -> AllplanGeo.Point3D:
        """
        Restringe el nuevo vector para que NO apunte demasiado cerca de la dirección inversa del segmento anterior.
        - Segmento 1: libre (no se llama si no hay prev_point).
        - Segmentos 2..N: no permitir volver hacia atrás dentro de min_backtrack_deg.

        Geometría:
        - u_prev = (last - prev) normalizado
        - eje prohibido = -u_prev
        - si angle(u_new, -u_prev) < min_backtrack_deg => proyectar u_new al borde del cono.
        """
        dxp = float(last_point.X - prev_point.X)
        dyp = float(last_point.Y - prev_point.Y)
        dzp = float(last_point.Z - prev_point.Z)
        lp = math.sqrt(dxp * dxp + dyp * dyp + dzp * dzp)
        if lp < 1e-9:
            return raw_point

        # u_prev y eje prohibido a = -u_prev
        upx, upy, upz = dxp / lp, dyp / lp, dzp / lp
        ax, ay, az = -upx, -upy, -upz

        dxn = float(raw_point.X - last_point.X)
        dyn = float(raw_point.Y - last_point.Y)
        dzn = float(raw_point.Z - last_point.Z)
        ln = math.sqrt(dxn * dxn + dyn * dyn + dzn * dzn)
        if ln < 1e-9:
            return raw_point

        unx, uny, unz = dxn / ln, dyn / ln, dzn / ln

        # ¿Está dentro del cono prohibido alrededor de 'a'?
        cos_min = math.cos(math.radians(min_backtrack_deg))
        dot_a = unx * ax + uny * ay + unz * az

        # Si dot_a > cos(min) => ángulo < min => prohibido
        if dot_a <= cos_min:
            return raw_point

        # Vector perpendicular a 'a' en el plano {a, u_new}
        px = unx - ax * dot_a
        py = uny - ay * dot_a
        pz = unz - az * dot_a
        pl = math.sqrt(px * px + py * py + pz * pz)

        if pl < 1e-9:
            # u_new casi colineal con 'a' (exacto hacia atrás). Elegir un perpendicular estable.
            # Usamos cross(a, Z) o cross(a, Y) si es degenerado.
            cx = ay * 1.0 - az * 0.0
            cy = az * 0.0 - ax * 1.0
            cz = ax * 0.0 - ay * 0.0
            cl = math.sqrt(cx * cx + cy * cy + cz * cz)
            if cl < 1e-9:
                cx = ay * 0.0 - az * 1.0
                cy = az * 0.0 - ax * 0.0
                cz = ax * 1.0 - ay * 0.0
                cl = math.sqrt(cx * cx + cy * cy + cz * cz)
            if cl < 1e-9:
                return raw_point
            px, py, pz = cx / cl, cy / cl, cz / cl
        else:
            px, py, pz = px / pl, py / pl, pz / pl

        # Construir dirección en el borde del cono (lo más cercana posible a u_new)
        c = math.cos(math.radians(min_backtrack_deg))
        s = math.sin(math.radians(min_backtrack_deg))
        bx = ax * c + px * s
        by = ay * c + py * s
        bz = az * c + pz * s

        return AllplanGeo.Point3D(
            last_point.X + bx * ln,
            last_point.Y + by * ln,
            last_point.Z + bz * ln,
        )

    def snap_point_with_angle(self, raw_point: AllplanGeo.Point3D, last_point, prev_point=None):
        """
        Recibe un punto crudo y devuelve un punto snapeado con ángulos permitidos.
        """
        # ---------------------------------------------------
        #  Utilidades internas
        # ---------------------------------------------------
        def normalize_angle(angle_deg):
            angle_deg = angle_deg % 360.0
            return angle_deg + 360 if angle_deg < 0 else angle_deg

        def angular_distance(a, b):
            diff = abs(a - b)
            return min(diff, 360.0 - diff)

        def find_closest_valid_angle(angle_deg, valid_list):
            ang = normalize_angle(angle_deg)
            return min(valid_list, key=lambda va: angular_distance(ang, va))

        # ---------------------------------------------------
        #  Deltas y distancias
        # ---------------------------------------------------
        dx = raw_point.X - last_point.X
        dy = raw_point.Y - last_point.Y
        dz = raw_point.Z - last_point.Z

        dist_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist_3d <= 1e-6:
            return raw_point

        dist_xy = math.sqrt(dx*dx + dy*dy)
        dist_z = abs(dz)

        is_horizontal = dist_xy > dist_z
        is_vertical = dist_z > dist_xy

        # ---------------------------------------------------
        #  Ángulos relativos permitidos
        # ---------------------------------------------------
        relative_angles = self.angle_steps
        tolerance = 1.0

        # ---------------------------------------------------
        #  SNAP EN PLANO XY
        # ---------------------------------------------------
        if is_horizontal:
            angle_deg = math.degrees(math.atan2(dy, dx))

            # ----------------------------
            #  Si existe segmento previo
            # ----------------------------
            if prev_point is not None:
                pvx = last_point.X - prev_point.X
                pvy = last_point.Y - prev_point.Y
                prev_dist_xy = math.sqrt(pvx*pvx + pvy*pvy)
                prev_dist_z = abs(last_point.Z - prev_point.Z)

                # Solo si el previo fue horizontal real
                if prev_dist_xy > prev_dist_z and prev_dist_xy > 1e-6:
                    prev_ang = normalize_angle(math.degrees(math.atan2(pvy, pvx)))

                    # Generar ángulos absolutos relativos al anterior
                    valid_angles = [
                        normalize_angle(prev_ang + rel)
                        for rel in relative_angles # type: ignore
                    ]

                    # Filtrar retrocesos 180°
                    def good(a):
                        delta = angular_distance(a, prev_ang)
                        return abs(delta - 180) > tolerance

                    snap_angles = [a for a in valid_angles if good(a)]
                    if not snap_angles:
                        snap_angles = valid_angles

                else:
                    # Después de un vertical o primer segmento horizontal
                    snap_angles = [0, 45, 90, 135, 180, 225, 270, 315]

            else:
                # Primer segmento
                snap_angles = [0, 45, 90, 135, 180, 225, 270, 315]

            # SNAP final
            closest = find_closest_valid_angle(angle_deg, snap_angles)
            rad = math.radians(closest)

            snap_dx = dist_3d * math.cos(rad)
            snap_dy = dist_3d * math.sin(rad)

            return AllplanGeo.Point3D(
                last_point.X + snap_dx,
                last_point.Y + snap_dy,
                last_point.Z
            )

        # ---------------------------------------------------
        #  SNAP VERTICAL O DIAGONAL
        # ---------------------------------------------------
        if is_vertical:

            # Diagonal 3D
            if dist_xy > 1e-3:
                elevation_deg = math.degrees(math.atan2(dist_z, dist_xy))
                valid_elev = [0, 45, 90]
                closest_elev = min(valid_elev, key=lambda e: abs(elevation_deg - e))

                # Snap horizontal (XY)
                ang_xy_deg = math.degrees(math.atan2(dy, dx))
                abs_angles = [0, 45, 90, 135, 180, 225, 270, 315]
                closest_xy = find_closest_valid_angle(ang_xy_deg, abs_angles)

                if closest_elev == 90:
                    return AllplanGeo.Point3D(last_point.X, last_point.Y, raw_point.Z)

                rad_xy = math.radians(closest_xy)
                rad_el = math.radians(closest_elev)

                dist_xy_snap = dist_3d * math.cos(rad_el)
                dist_z_snap = dist_3d * math.sin(rad_el)

                return AllplanGeo.Point3D(
                    last_point.X + dist_xy_snap * math.cos(rad_xy),
                    last_point.Y + dist_xy_snap * math.sin(rad_xy),
                    last_point.Z + (dist_z_snap if dz >= 0 else -dist_z_snap)
                )

            # Puro vertical
            return AllplanGeo.Point3D(last_point.X, last_point.Y, raw_point.Z)

        # ---------------------------------------------------
        #  Si no es ni horizontal ni vertical → sin snap
        # ---------------------------------------------------
        return raw_point

    def _dist_sq(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx, dy, dz = a.X - b.X, a.Y - b.Y, a.Z - b.Z
        return dx*dx + dy*dy + dz*dz

    def _clone_properties(self, src_prop):
        dst = AllplanBaseElements.CommonProperties()
        dst.GetGlobalProperties()
        for name in ("Color", "Pen", "Stroke", "ColorByLayer", "PenByLayer", "StrokeByLayer", "Layer"):
            try:
                setattr(dst, name, getattr(src_prop, name))
            except Exception:
                pass
        return dst

    def _create_cross_marker(self, point, properties, size, z_bias: float = 0.0):
        """Dibuja una cruz (cruzeta) en torno al punto, en ejes X/Y y una pequeña marca Z."""
        half = max(size * 0.5, 0.1)
        px = getattr(point, "X", 0.0)
        py = getattr(point, "Y", 0.0)
        pz = getattr(point, "Z", 0.0) + (z_bias or 0.0)

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

    def _create_point_marker(self, point, properties, size, z_bias: float = 0.0):
        """
        Dibuja un marcador de vértice como esfera de alambre (wireframe).

        Se construye directamente con líneas sobre coordenadas esféricas, sin usar
        BRep3D.CreateSphere, porque en contexto de previsualización Allplan renderiza
        los sólidos BRep como un círculo plano con un arco interior — no como esfera.

        Vista planta   → círculo completo (paralelo ecuatorial)
        Vista alzado   → círculo completo (meridiano frontal)
        Vista isométrica → esfera de alambre tipo globo terráqueo
        """
        import math

        radius = max(size * 0.35, 0.01)
        cx = getattr(point, "X", 0.0)
        cy = getattr(point, "Y", 0.0)
        cz = getattr(point, "Z", 0.0) + (z_bias or 0.0)

        SEGMENTS    = 36   # suavidad de cada curva
        N_PARALLELS = 4    # anillos horizontales (sin polos)
        N_MERIDIANS = 6    # meridianos (cada uno = círculo completo polo a polo)

        elems = []

        def _pt(x, y, z):
            return AllplanGeo.Point3D(x, y, z)

        def _line(p1, p2):
            elems.append(
                AllplanBasisElements.ModelElement3D(
                    properties, AllplanGeo.Line3D(p1, p2)
                )
            )

        # ── Paralelos: anillos horizontales ──────────────────────────────────────
        # φ distribuido entre -π/2 y +π/2, incluyendo el ecuador
        for i in range(N_PARALLELS):
            phi    = math.pi * (-0.5 + (i + 1) / (N_PARALLELS + 1))
            r_ring = radius * math.cos(phi)
            z_ring = cz + radius * math.sin(phi)
            prev = None
            for j in range(SEGMENTS + 1):
                theta = 2.0 * math.pi * j / SEGMENTS
                pt = _pt(cx + r_ring * math.cos(theta),
                        cy + r_ring * math.sin(theta),
                        z_ring)
                if prev:
                    _line(prev, pt)
                prev = pt

        # ── Meridianos: círculos completos polo a polo ────────────────────────────
        # Cada θ genera una vuelta completa:
        #   primera mitad → θ        (de polo sur a polo norte)
        #   segunda mitad → θ + π    (de polo norte a polo sur, lado opuesto)
        for i in range(N_MERIDIANS):
            theta = math.pi * i / N_MERIDIANS
            prev  = None
            for j in range(SEGMENTS * 2 + 1):
                if j <= SEGMENTS:
                    phi = math.pi * (-0.5 + j / SEGMENTS)
                    t   = theta
                else:
                    phi = math.pi * (0.5 - (j - SEGMENTS) / SEGMENTS)
                    t   = theta + math.pi
                pt = _pt(
                    cx + radius * math.cos(phi) * math.cos(t),
                    cy + radius * math.cos(phi) * math.sin(t),
                    cz + radius * math.sin(phi),
                )
                if prev:
                    _line(prev, pt)
                prev = pt

        return elems

    def _line_with_zbias(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, z_bias: float):
        pa = AllplanGeo.Point3D(a.X, a.Y, a.Z + z_bias)
        pb = AllplanGeo.Point3D(b.X, b.Y, b.Z + z_bias)
        return AllplanGeo.Line3D(pa, pb)

    def _midpoint(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> AllplanGeo.Point3D:
        return AllplanGeo.Point3D((a.X + b.X) * 0.5, (a.Y + b.Y) * 0.5, (a.Z + b.Z) * 0.5)

    def get_segments(self):
        self.data = []
        all_static_points = []

        view_type = self.coord_input.GetViewWorldProjection().GetIsoProjection() # type: ignore
        current_mode = self._get_view_mode(view_type)

        # 1. PROCESAR RUTAS GUARDADAS
        for path_idx, path_points in enumerate(self.script_object.saved_paths):
            all_static_points.extend(path_points)
            pairs = self.build_point_pairs(path_points)
            for i, (p1, p2) in enumerate(pairs):
                meta_key = f"{path_idx}_{i}"
                meta = self.script_object.persistent_metadata.get(meta_key)
                saved_mode = getattr(meta, 'view_mode', None) if meta else None

                # Usar saved_mode solo si coincide con la vista actual
                # Si la vista cambió, recalcular con current_mode
                seg_mode = saved_mode if (saved_mode and saved_mode == current_mode) else current_mode

                segment = self._calculate_single_segment(p1, p2, i, seg_mode, path_idx)
                self.data.append(segment)

        # Actualizar referencia de Snap
        self.last_points = all_static_points + (self.points if self.create_mode else [])

        # 2. PROCESAR RUTA VIVA
        if self.create_mode and len(self.points) >= 2:
            live_pairs = self.build_point_pairs(self.points)
            for i, (p1, p2) in enumerate(live_pairs):
                # segment_modes aplica al trazado vivo, current_mode como fallback
                current_seg_mode = self.segment_modes[i + 1] if i + 1 < len(self.segment_modes) else current_mode
                segment = self._calculate_single_segment(p1, p2, i, current_seg_mode)
                self.data.append(segment)

        return self.data

    def _get_segment_info(self, path_idx: int, seg_idx: int, view_mode: str = "") -> SegmentInfo:
        """
        Busca si el segmento ya tiene info guardada.
        Si no, crea una nueva con los valores actuales del menú.
        """
        # 1. Intentar buscar en la memoria persistente
        # Usamos una clave única basada en el índice del camino y del segmento
        persistence_key = f"{path_idx}_{seg_idx}"

        if persistence_key in self.script_object.persistent_metadata:
            return self.script_object.persistent_metadata[persistence_key]

        # 2. Si no existe (es un tubo nuevo), creamos la info con el diámetro actual del menú

        default_diameter = self.script_object.diameter_type
        system = ""
        if self.script_object.selected_inst_type:
            system = self.script_object.selected_inst_type
        label = self._format_segment_label(default_diameter, system)

        # getattr(self.build_ele, ParamNames.General.FUNCTIONAL_NAME)
        new_info = SegmentInfo(
            diameter=default_diameter,
            section_type=f"{default_diameter} mm",
            system=system,
            label=label,
            distribution_type=self.script_object.distribution_type,
            water_type=self.script_object.water_type,
            face=self.script_object.face_en,
            view_mode=view_mode,
        )

        # Guardamos en la persistencia para que no se pierda al redibujar
        self.script_object.persistent_metadata[persistence_key] = new_info
        return new_info

    def _calculate_single_segment(self, p1, p2, index, view_mode, path_idx: int = -1):
            """
            Toma toda tu lógica actual de cálculo (puntos, ángulos, cuadrantes)
            y devuelve un objeto SegmentItem.
            """
            # ... (Aquí pegas todo tu código de cálculos: dx, dy, dz, ángulos, etc.) ...

            # ============================================================
            # 1. VECTOR Y COMPONENTES
            # ============================================================
            dx = p2.X - p1.X
            dy = p2.Y - p1.Y
            dz = p2.Z - p1.Z

            vec = AllplanGeo.Vector3D(dx, dy, dz)

            # ============================================================
            # 2. LONGITUDES EN TODOS LOS PLANOS Y EJES
            # ============================================================

            # Longitud 3D total (distancia euclidiana)
            longitud_3d = p1.GetDistance(p2)

            # Longitudes proyectadas en cada PLANO
            longitud_xy = math.sqrt(dx**2 + dy**2)  # Proyección en plano HORIZONTAL (suelo)
            longitud_xz = math.sqrt(dx**2 + dz**2)  # Proyección en plano VERTICAL X-Z (alzado lateral)
            longitud_yz = math.sqrt(dy**2 + dz**2)  # Proyección en plano VERTICAL Y-Z (alzado frontal)

            # Longitudes en cada EJE individual
            longitud_x = abs(dx)  # Distancia solo en X
            longitud_y = abs(dy)  # Distancia solo en Y
            longitud_z = abs(dz)  # Distancia solo en Z (altura/profundidad)

            # Vector normalizado (dirección unitaria)
            if longitud_3d > 1e-6:  # Evitar división por cero
                vec_normalizado = AllplanGeo.Vector3D(
                    dx / longitud_3d,
                    dy / longitud_3d,
                    dz / longitud_3d
                )
            else:
                vec_normalizado = AllplanGeo.Vector3D(0, 0, 0)

            # ============================================================
            # 3. ÁNGULOS HORIZONTALES (Plano X-Y - el cuadrado rojo)
            # ============================================================
            # Ángulo en plano XY desde eje X positivo (sentido antihorario)
            # 0° = +X (derecha), 90° = +Y (arriba), 180° = -X, 270° = -Y
            angulo_xy_desde_x = math.degrees(math.atan2(dy, dx))

            # Ángulo en plano XY desde eje Y positivo (sentido antihorario)
            # 0° = +Y (arriba), 90° = -X (izquierda), 180° = -Y, 270° = +X
            angulo_xy_desde_y = math.degrees(math.atan2(dx, dy))

            # Azimut (desde Norte = +Y, sentido horario) - común en topografía
            # 0° = Norte (+Y), 90° = Este (+X), 180° = Sur (-Y), 270° = Oeste (-X)
            azimut = (90.0 - angulo_xy_desde_x) % 360.0

            # ============================================================
            # 4. ÁNGULOS VERTICALES - PLANO X-Z (alzado lateral)
            # ============================================================

            # Ángulo en plano XZ desde eje X positivo
            angulo_xz_desde_x = math.degrees(math.atan2(dz, dx)) if dx != 0 else (90.0 if dz > 0 else -90.0)

            # Ángulo en plano XZ desde eje Z positivo
            angulo_xz_desde_z = math.degrees(math.atan2(dx, dz)) if dz != 0 else (90.0 if dx > 0 else -90.0)

            # Inclinación en X (pendiente lateral): ángulo respecto al plano horizontal XY
            inclinacion_en_x = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else 0.0

            # ============================================================
            # 5. ÁNGULOS VERTICALES - PLANO Y-Z (alzado frontal)
            # ============================================================

            # Ángulo en plano YZ desde eje Y positivo
            angulo_yz_desde_y = math.degrees(math.atan2(dz, dy)) if dy != 0 else (90.0 if dz > 0 else -90.0)

            # Ángulo en plano YZ desde eje Z positivo
            angulo_yz_desde_z = math.degrees(math.atan2(dy, dz)) if dz != 0 else (90.0 if dy > 0 else -90.0)

            # Inclinación en Y (pendiente frontal): ángulo respecto al plano horizontal XY
            inclinacion_en_y = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else 0.0

            # ============================================================
            # 6. INCLINACIÓN VERTICAL GENERAL (el más usado)
            # ============================================================

            # Elevación: ángulo vertical desde el plano horizontal XY
            elevacion = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else (90.0 if dz > 0 else -90.0)

            # Pendiente en porcentaje (rise/run * 100)
            pendiente_porcentaje = (dz / longitud_xy * 100.0) if longitud_xy > 0 else 0.0

            # ============================================================
            # 7. ÁNGULOS DIRECTORES (con cada eje coordenado)
            # ============================================================
            # Ángulo que forma el vector con cada eje (0° a 180°)

            if longitud_3d > 0:
                # Cosenos directores
                cos_x = dx / longitud_3d
                cos_y = dy / longitud_3d
                cos_z = dz / longitud_3d

                # Ángulos directores
                angulo_con_eje_x = math.degrees(math.acos(max(-1.0, min(1.0, cos_x))))
                angulo_con_eje_y = math.degrees(math.acos(max(-1.0, min(1.0, cos_y))))
                angulo_con_eje_z = math.degrees(math.acos(max(-1.0, min(1.0, cos_z))))
            else:
                cos_x = cos_y = cos_z = 0.0
                angulo_con_eje_x = angulo_con_eje_y = angulo_con_eje_z = 0.0

            # ============================================================
            # 8. ÁNGULOS ENTRE PROYECCIONES
            # ============================================================

            # Ángulo entre proyección XY y proyección XZ
            angulo_xy_xz = math.degrees(math.atan2(longitud_z, longitud_xy)) if longitud_xy > 0 else 0.0

            # Ángulo entre proyección XY y proyección YZ
            angulo_xy_yz = math.degrees(math.atan2(longitud_z, longitud_xy)) if longitud_xy > 0 else 0.0

            # Ángulo entre proyección XZ y proyección YZ
            angulo_xz_yz = math.degrees(math.atan2(longitud_y, longitud_x)) if longitud_x > 0 else 0.0

            # ============================================================
            # 9. CUADRANTE Y OCTANTE (clasificación espacial)
            # ============================================================

            # Cuadrante en plano XY (1-4)
            if dx >= 0 and dy >= 0:
                cuadrante_xy = 1  # Noreste
            elif dx < 0 and dy >= 0:
                cuadrante_xy = 2  # Noroeste
            elif dx < 0 and dy < 0:
                cuadrante_xy = 3  # Suroeste
            else:
                cuadrante_xy = 4  # Sureste

            # Octante en espacio 3D (1-8)
            if dz >= 0:
                octante = cuadrante_xy  # Octantes superiores (1-4)
            else:
                octante = cuadrante_xy + 4  # Octantes inferiores (5-8)

            # ============================================================
            # 10. INFORMACIÓN ADICIONAL
            # ============================================================

            # Sentido en cada eje
            sentido_x = "positivo" if dx > 0 else ("negativo" if dx < 0 else "neutro")
            sentido_y = "positivo" if dy > 0 else ("negativo" if dy < 0 else "neutro")
            sentido_z = "ascendente" if dz > 0 else ("descendente" if dz < 0 else "horizontal")

            # Es horizontal, vertical o inclinado
            umbral_horizontal = 5.0  # grados
            umbral_vertical = 85.0   # grados

            if abs(elevacion) < umbral_horizontal:
                tipo_segmento = "horizontal"
            elif abs(elevacion) > umbral_vertical:
                tipo_segmento = "vertical"
            else:
                tipo_segmento = "inclinado"

            # ============================================================
            # 11. CREAR SEGMENTO CON TODOS LOS DATOS
            # ============================================================
            if path_idx == -1:
                info = None
            else:
                info = self._get_segment_info(path_idx, index, view_mode)

            seg = SegmentItem(
                name=f"line_{index+1}",
                view_mode=view_mode,
                info=info,
                data=SegmentData(
                    # ===== PUNTOS =====
                    start=p1,
                    end=p2,

                    # ===== COMPONENTES DEL VECTOR =====
                    delta_x=dx,
                    delta_y=dy,
                    delta_z=dz,

                    # ===== LONGITUDES TOTALES =====
                    longitud_3d=longitud_3d,

                    # ===== LONGITUDES POR PLANO =====
                    longitud_xy=longitud_xy,  # Proyección horizontal (suelo)
                    longitud_xz=longitud_xz,  # Proyección alzado lateral
                    longitud_yz=longitud_yz,  # Proyección alzado frontal

                    # ===== LONGITUDES POR EJE =====
                    longitud_x=longitud_x,
                    longitud_y=longitud_y,
                    longitud_z=longitud_z,

                    # ===== ÁNGULOS HORIZONTALES (Plano XY) =====
                    angulo_xy_desde_x=angulo_xy_desde_x,
                    angulo_xy_desde_y=angulo_xy_desde_y,
                    azimut=azimut,

                    # ===== ÁNGULOS VERTICALES (Plano XZ) =====
                    angulo_xz_desde_x=angulo_xz_desde_x,
                    angulo_xz_desde_z=angulo_xz_desde_z,
                    inclinacion_en_x=inclinacion_en_x,

                    # ===== ÁNGULOS VERTICALES (Plano YZ) =====
                    angulo_yz_desde_y=angulo_yz_desde_y,
                    angulo_yz_desde_z=angulo_yz_desde_z,
                    inclinacion_en_y=inclinacion_en_y,

                    # ===== ELEVACIÓN Y PENDIENTE =====
                    elevacion=elevacion,
                    pendiente_porcentaje=pendiente_porcentaje,

                    # ===== ÁNGULOS DIRECTORES =====
                    angulo_con_eje_x=angulo_con_eje_x,
                    angulo_con_eje_y=angulo_con_eje_y,
                    angulo_con_eje_z=angulo_con_eje_z,
                    coseno_director_x=cos_x,
                    coseno_director_y=cos_y,
                    coseno_director_z=cos_z,

                    # ===== ÁNGULOS ENTRE PROYECCIONES =====
                    angulo_xy_xz=angulo_xy_xz,
                    angulo_xy_yz=angulo_xy_yz,
                    angulo_xz_yz=angulo_xz_yz,

                    # ===== CLASIFICACIÓN ESPACIAL =====
                    cuadrante_xy=cuadrante_xy,
                    octante=octante,
                    tipo_segmento=tipo_segmento,

                    # ===== SENTIDOS =====
                    sentido_x=sentido_x,
                    sentido_y=sentido_y,
                    sentido_z=sentido_z,

                    # ===== VECTORES =====
                    vector=vec,
                    vector_normalizado=vec_normalizado,

                    # ===== COMPATIBILIDAD =====
                    angulo_xy=angulo_xy_desde_x,  # Alias para compatibilidad
                    angulo_z=elevacion,            # Alias para compatibilidad
                )
            )
            return seg

    def build_point_pairs(self, points):
        list_point_group = []
        if len(points) >= 2:
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                list_point_group.append((p1, p2))

        return list_point_group

    # ============================================================================
    # DRAWING MODE CONFIGURATION
    # ============================================================================
    def _find_element_at_point(self, point, mode, tolerance=100.0):
        """
        Encuentra el elemento más cercano al punto dado.
        Prioriza elementos puntuales (codos, uniones) sobre tubos.
        """
        if not self.generated_elements:
            return None

        # Buscar primero elementos puntuales (codos, uniones) - más prioritarios
        point_elements = []
        tube_elements = []

        for path_group in getattr(self, "generated_elements", []):
            for element in path_group:
                element_type = element.get('type')
                pos = element.get('position')

                if not pos:
                    continue

                # Distancia 2D al punto de posición
                dist_to_pos = self.get_dist_in_plane(point, pos, mode)

                if element_type in ['codo', 'union', 'bifurcacion', 'reduccion']:
                    # Elementos puntuales - tolerancia más generosa
                    if dist_to_pos < tolerance:
                        point_elements.append((dist_to_pos, element))

                elif element_type in ['tubo']:
                    # Para tubos, calcular distancia a la línea
                    if dist_to_pos < tolerance:
                        tube_elements.append((dist_to_pos, element))

        # Priorizar elementos puntuales sobre tubos
        if point_elements:
            # Retornar el elemento puntual más cercano
            point_elements.sort(key=lambda x: x[0])
            return point_elements[0][1]

        if tube_elements:
            # Retornar el tubo más cercano
            tube_elements.sort(key=lambda x: x[0])
            return tube_elements[0][1]

        return None

    def _generate_tooltip_text(self, element):
        """
        Genera el texto descriptivo para el tooltip del elemento.
        Args:
            element: Diccionario con información del elemento
        Returns:
            str: Texto formateado para mostrar
        """
        if not element:
            return ""

        element_type = element.get('type', 'unknown')
        element_key = element.get('key', ())

        key_layer = f"seg_{element_key[4]}_elem_{element_key[3]}"
        # Nombres legibles para tipos de elementos
        type_names = {
            'tubo': 'Tubo',
            'codo': 'Codo',
            'union': 'Unión',
            'bifurcacion': 'Bifurcacion',
            'reduccion': 'Reduccion',
        }
        type_display = type_names.get(element_type, element_type.capitalize())

        # Información básica
        lines = [f"Inst: {self.script_object.selected_inst_type}", f"Tipo Elemento: {type_display}"]

        # Agregar información de la key
        if len(element_key) >= 3:
            path_idx = element_key[4]
            seg_or_vertex_idx = element_key[3] #element_key[3]

            if element_type == 'tubo':
                lines.append(f"Ruta: {path_idx}, Segmento: {seg_or_vertex_idx}")
                raw_diam = element.get('diameter_in', 0)
                try:
                    diameter_in = int(raw_diam)
                except (ValueError, TypeError):
                    diameter_in = raw_diam
                lines.append(f"Diametro: {diameter_in}")
            else:
                element_params = element.get('params', {})
                lines.append(f"Ruta: {path_idx}, Vértice: {seg_or_vertex_idx}")
                if element_type == 'bifurcacion':
                    lines.append(f"Angle: {int(element_params.get('angle', 0))}")
                elif element_type == 'reduccion':
                    lines.append(f"reducer_type: {element_params.get('reducer_type', "")}")

                    raw_in = element_params.get('diameter_in', 0)
                    raw_out = element_params.get('diameter_out', 0)
                    try:
                        diameter_in = int(raw_in)
                    except (ValueError, TypeError):
                        diameter_in = raw_in
                    try:
                        diameter_out = int(raw_out)
                    except (ValueError, TypeError):
                        diameter_out = raw_out
                    lines.append(f"Diametro IN: {diameter_in} - Diametro OUT: {diameter_out}")

        # Agregar información adicional según el tipo
        if element_type == 'tubo':
            geom = element.get('geometry')
            if isinstance(geom, AllplanGeo.Line3D):
                length = ((geom.EndPoint.X - geom.StartPoint.X) ** 2 +
                        (geom.EndPoint.Y - geom.StartPoint.Y) ** 2 +
                        (geom.EndPoint.Z - geom.StartPoint.Z) ** 2) ** 0.5
                lines.append(f"Longitud: {length:.2f} mm")

        # Información de layer si existe

        if 'layer' in element:
            layer_name = self.script_object.applied_layers[key_layer]["layer"] if key_layer in self.script_object.applied_layers else element['layer']
            lines.append(f"Layer: {layer_name}")

        if 'attribute' in element:
            attr_value = None
            # .get(key, []) intenta obtener la lista; si no existe la key, devuelve []
            attributes = self.script_object.applied_attributes.get(key_layer, [])
            if len(attributes) > 0: # Cambié a > 0 por si solo hay un atributo con ese ID
                for attr in attributes:
                    if attr.Id == 55010:
                        attr_value = attr.Value
                        break
            # Si attr_value sigue siendo None, usa el valor por defecto del elemento
            attribute = attr_value if attr_value is not None else element['attribute']
            lines.append(f"Attr-pmp_pare: {attribute}")

        return "\n".join(lines)

    def _highlight_selected_elements(self):
        """
        Resalta visualmente todos los elementos seleccionados.
        """
        self.highlight_geometries = []  # Lista para múltiples geometrías

        if not self.selected_segments:
            print("[SO] No hay elementos seleccionados para resaltar")
            return

        print(f"[SO] Resaltando {len(self.selected_segments)} elementos seleccionados")
        for element_key in self.selected_segments:
            # Buscar el elemento en generated_elements
            element = self._find_element_by_key(element_key)

            if element:
                pos = element.get("position")
                element_type = element.get("type")

                if pos:
                    try:
                        size = HANDLE_SIZE * HOVER_SCALE
                        half = size / 2

                        # Crear un cubo de highlight alrededor del punto
                        axis = AllplanGeo.AxisPlacement3D(
                            AllplanGeo.Point3D(pos.X - half, pos.Y - half, pos.Z - half)
                        )
                        highlight_geom = AllplanGeo.Polyhedron3D.CreateCuboid(
                            axis, size, size, size
                        )

                        self.highlight_geometries.append({
                            'geometry': highlight_geom,
                            'key': element_key,
                            'type': element_type
                        })

                        print(f"[SO] Elemento {element_key} resaltado en ({pos.X:.2f}, {pos.Y:.2f}, {pos.Z:.2f})")

                    except Exception as e:
                        print(f"[SO] Error creando geometría de highlight para {element_key}: {e}")
                        # Fallback: usar una línea vertical como marcador
                        try:
                            marker_height = HANDLE_SIZE * 2
                            p1 = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z - marker_height / 2)
                            p2 = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z + marker_height / 2)
                            highlight_geom = AllplanGeo.Line3D(p1, p2)

                            self.highlight_geometries.append({
                                'geometry': highlight_geom,
                                'key': element_key,
                                'type': element_type
                            })

                            print(f"[SO] Usando marcador de línea para {element_key}")
                        except Exception as e2:
                            print(f"[SO] Error creando marcador de línea para {element_key}: {e2}")

    def _find_element_by_key(self, element_key):
        """
        Busca un elemento en generated_elements por su key.

        Args:
            element_key: Tupla (type, path_idx, seg_idx/vertex_idx)

        Returns:
            dict: Elemento encontrado o None
        """
        for path_group in getattr(self, "generated_elements", []):
            for element in path_group:
                if element.get('key') == element_key:
                    return element
        return None

    def _select_elements_in_box(self, box_start, box_curr):
        """
        Selecciona múltiples elementos que estén dentro del rectángulo de selección.

        Args:
            box_start: Punto inicial del rectángulo de selección
            box_curr: Punto actual del rectángulo de selección

        Returns:
            set: Conjunto de keys de elementos seleccionados
        """
        selected = set()
        for path_group in getattr(self, "generated_elements", []):
            for element in path_group:
                element_type = element['type']
                element_key = element['key']

                if element_type == 'tubo':
                    # Para tubos, verificar que ambos extremos estén dentro del rectángulo
                    geometry = element['geometry']  # Line3D
                    p1 = geometry.StartPoint
                    p2 = geometry.EndPoint

                    if (self._point_in_rect_xy(p1, box_start, box_curr) and
                        self._point_in_rect_xy(p2, box_start, box_curr)):
                        selected.add(element_key)
                        print(f"[SO] Tubo seleccionado: {element_key}")

                elif element_type in ['codo', 'union']:
                    # Para codos y uniones, verificar que el punto central esté dentro
                    position = element['position']

                    if self._point_in_rect_xy(position, box_start, box_curr):
                        selected.add(element_key)
                        print(f"[SO] {element_type.capitalize()} seleccionado: {element_key}")

        return selected

    def _point_in_rect_xy(self, p: AllplanGeo.Point3D, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> bool:
        """
        Comprueba si el punto p está dentro del rectángulo formado por las esquinas a y b,
        proyectando todos los puntos al plano de la vista actual.
        Esto permite que la selección por marco funcione en cualquier vista (XY, vertical, diagonal, etc.).
        """
        try:
            # Obtener la proyección vista-mundo
            view_proj = self.coord_input.GetViewWorldProjection()  # type: ignore

            # Proyectar los tres puntos del espacio 3D al plano 2D de la vista
            # WorldToView convierte un punto 3D mundial a coordenadas 2D de la vista (pantalla)
            p_view = view_proj.WorldToView(p)
            a_view = view_proj.WorldToView(a)
            b_view = view_proj.WorldToView(b)

            # Ahora hacer la comparación 2D en el plano de vista
            # Usar las coordenadas X e Y del plano de vista (que son coordenadas de pantalla)
            xmin, xmax = (
                (a_view.X, b_view.X) if a_view.X <= b_view.X else (b_view.X, a_view.X)
            )
            ymin, ymax = (
                (a_view.Y, b_view.Y) if a_view.Y <= b_view.Y else (b_view.Y, a_view.Y)
            )

            return (xmin <= p_view.X <= xmax) and (ymin <= p_view.Y <= ymax)
        except Exception as ex:
            # Fallback: si falla la proyección, usar el método antiguo XY
            print(f"[INT] Error al proyectar punto a vista: {ex}, usando fallback XY")
            xmin, xmax = (a.X, b.X) if a.X <= b.X else (b.X, a.X)
            ymin, ymax = (a.Y, b.Y) if a.Y <= b.Y else (b.Y, a.Y)
            return (xmin <= p.X <= xmax) and (ymin <= p.Y <= ymax)

    def _on_element_clicked(self, element, is_multiple=False):
        """
        Maneja el click: resalta el elemento y lo añade a la selección.
        """
        element_key = element.get("key", None)

        # Si es el primero de un grupo o una selección individual, limpiamos highlights previos
        if not is_multiple:
            self.highlight_geometries.clear()
            self.selected_segments.clear()

        # Añadir a la lista de seleccionados (para aplicar atributos/layers luego)
        self.selected_segments.add(element_key)

        # Resaltar
        self._highlight_element(element)

    def _highlight_element(self, element):
        """
        Crea y acumula geometría de highlight para el elemento.
        """
        pos = element.get("position")
        if pos:
            try:
                size = HANDLE_SIZE * HOVER_SCALE
                half = size / 2
                axis = AllplanGeo.AxisPlacement3D(
                    AllplanGeo.Point3D(pos.X - half, pos.Y - half, pos.Z - half)
                )
                new_highlight = AllplanGeo.Polyhedron3D.CreateCuboid(axis, size, size, size)

                # Guardamos en la lista que lee _draw_preview
                self.highlight_geometries.append({'geometry': new_highlight})

            except Exception as e:
                print(f"[SO] Error resaltando: {e}")

    def _find_clicked_element(self, click_point: AllplanGeo.Point3D, mode: str):
        """
        Encuentra el elemento más cercano al punto de click usando distancias
        proyectadas según el plano de la vista actual.
        """
        # Usamos la tolerancia definida (ej. 150.0 mm)
        min_dist = HIT_TOL_VERTEX
        closest_element = None

        # Recorremos los elementos generados
        for path_group in getattr(self, "generated_elements", []):
            for element in path_group:
                pos = element.get("position")
                if pos:
                    # --- CAMBIO CLAVE: Usamos la distancia proyectada ---
                    # Esto permite que si clickeas en Planta (XY) detecte el objeto
                    # aunque esté a una Z (altura) muy diferente.
                    dist = self.get_dist_in_plane(click_point, pos, mode)
                    if dist < min_dist:
                        min_dist = dist
                        closest_element = element

        if closest_element:
            element_key = closest_element.get("key")
            print(f"[SO] Elemento clickeado: {element_key} a {min_dist:.1f}mm (Modo: {mode})")

        return closest_element

    def _find_hover_saved_point(self, current_pnt, mode):
        """Busca un vértice guardado usando distancia proyectada según la vista."""
        snap_dist = HIT_TOL_VERTEX # mm
        for pidx, path in enumerate(self.script_object.saved_paths):
            for vidx, saved_p in enumerate(path):
                # AQUÍ ESTÁ EL CAMBIO: No usar distancia 3D, usar dist_in_plane
                dist = self.get_dist_in_plane(current_pnt, saved_p, mode)
                if dist < snap_dist:
                    return (pidx, vidx, saved_p)
        return None

    def _find_hover_midpoint(self, p: AllplanGeo.Point3D, mode) -> Optional[Tuple[str, int, int, AllplanGeo.Point3D]]:
        """
        Busca el punto medio más cercano al cursor usando distancia proyectada.
        """
        # Tolerancia de captura (Snap distance)
        snap_dist_limit = HIT_TOL_MIDPOINT
        best = None
        min_dist = float('inf')

        # Pre-calculamos la proyección si es necesario para optimizar el bucle
        proj_data = None
        if mode not in ["XY", "XZ", "YZ"]:
            proj_data = self.coord_input.GetViewWorldProjection() # type: ignore

        # 1. BUSCAR EN RUTA ACTIVA (La que se está dibujando)
        if len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                a, b = self.points[i], self.points[i + 1]
                mp = self._midpoint(a, b)

                # Usamos distancia en plano de vista
                dist = self.get_dist_in_plane(p, mp, mode, proj_data)

                if dist < snap_dist_limit and dist < min_dist:
                    min_dist = dist
                    best = ("active", -1, i, mp)

        # 2. BUSCAR EN RUTAS GUARDADAS
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) < 2:
                continue

            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                mp = self._midpoint(a, b)

                # Usamos distancia en plano de vista
                dist = self.get_dist_in_plane(p, mp, mode, proj_data)
                if dist < snap_dist_limit and dist < min_dist:
                    min_dist = dist
                    best = ("tubo", path_idx, i, mp)

        return best

    def _find_hover_segment(self, click_point, mode):
        """
        Encuentra el segmento más cercano al cursor proyectando ambos al plano de la vista.
        """
        # 1. Definir una tolerancia realista.
        # Si click_point viene de la vista, asegúrate que HIT_TOL_SEGMENT esté en las mismas unidades.
        min_dist_found = HIT_TOL_SEGMENT
        best_seg = None

        proj_data = None
        if mode not in ["XY", "XZ", "YZ"]:
            proj_data = self.coord_input.GetViewWorldProjection() # type: ignore

        for p_idx, path in enumerate(self.script_object.saved_paths):
            if len(path) < 2:
                continue

            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i+1]

                # 2. Obtener el factor t proyectado en el plano actual
                # Esto es vital: la "perpendicular" debe calcularse en el plano donde ves el objeto
                t = self._get_t_projected(p1, p2, click_point, mode, proj_data)

                # Restringimos t al segmento [0, 1]
                t_clamped = max(0.0, min(1.0, t))

                # 3. Punto exacto sobre el eje del tubo en el espacio 3D real
                on_seg_3d = AllplanGeo.Point3D(
                    p1.X + t_clamped * (p2.X - p1.X),
                    p1.Y + t_clamped * (p2.Y - p1.Y),
                    p1.Z + t_clamped * (p2.Z - p1.Z)
                )

                # 4. Cálculo de distancia en el plano de la vista
                # IMPORTANTE: Esta función debe comparar la posición del mouse con la proyección de on_seg_3d
                dist = self.get_dist_in_plane(click_point, on_seg_3d, mode, proj_data)

                # Debug log para ver por qué no entra:
                # print(f"Seg {i}: Dist calc = {dist:.2f}, Tol = {min_dist_found}")

                if dist < min_dist_found:
                    min_dist_found = dist
                    # Retornamos el punto exacto 3D calculado (on_seg_3d)
                    best_seg = ("tubo", p_idx, i, on_seg_3d)

        return best_seg

    def _segment_project_point(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, p: AllplanGeo.Point3D, mode: str
    ) -> Tuple[float, AllplanGeo.Point3D]:
        """
        Calcula la proyección del punto 'p' sobre el segmento 'ab'
        según la vista actual (mode), devolviendo el factor t y el punto 3D real.
        """
        # 1. Definir vectores según el plano de la vista para calcular el t "visual"
        if mode == "XY":
            v = (b.X - a.X, b.Y - a.Y)
            w = (p.X - a.X, p.Y - a.Y)
        elif mode == "XZ":
            v = (b.X - a.X, b.Z - a.Z)
            w = (p.X - a.X, p.Z - a.Z)
        elif mode == "YZ":
            v = (b.Y - a.Y, b.Z - a.Z)
            w = (p.Y - a.Y, p.Z - a.Z)
        else:
            # Para Isométrica (XYZ), proyectamos a coordenadas de pantalla (píxeles)
            # Esto soluciona el problema de profundidad en la vista 3D
            proj_data = self.coord_input.GetViewWorldProjection() # type: ignore
            a_view = proj_data.WorldToView(a)
            b_view = proj_data.WorldToView(b)
            p_view = proj_data.WorldToView(p)

            v = (b_view.X - a_view.X, b_view.Y - a_view.Y)
            w = (p_view.X - a_view.X, p_view.Y - a_view.Y)

        # 2. Calcular el factor t (proyección escalar 2D)
        vv = v[0]**2 + v[1]**2
        if vv <= 1e-12:
            return 0.0, AllplanGeo.Point3D(a)

        t = (v[0] * w[0] + v[1] * w[1]) / vv

        # Restringir t al segmento [0, 1]
        t = max(0.0, min(1.0, t))

        # 3. Calcular el punto Q en el espacio 3D real interpolando con el t visual
        # Esto garantiza que el punto insertado esté EXACTAMENTE sobre la tubería original
        q = AllplanGeo.Point3D(
            a.X + t * (b.X - a.X),
            a.Y + t * (b.Y - a.Y),
            a.Z + t * (b.Z - a.Z)
        )

        return t, q

    # ============================================================================
    # DRAWING MODE EDIT - INSERTION
    # ============================================================================
    def _get_segment_endpoints(
        self, seg: Tuple[str, int, int, int]
    ) -> Tuple[Optional[AllplanGeo.Point3D], Optional[AllplanGeo.Point3D]]:
        kind, path_idx, seg_idx, _ = seg
        if kind == "active":
            if len(self.points) >= 2 and 0 <= seg_idx < len(self.points) - 1:
                return self.points[seg_idx], self.points[seg_idx + 1]
            return None, None
        if kind == "tubo":
            if 0 <= path_idx < len(self.script_object.saved_paths):
                pts = self.script_object.saved_paths[path_idx]
                if len(pts) >= 2 and 0 <= seg_idx < len(pts) - 1:
                    return pts[seg_idx], pts[seg_idx + 1]
        return None, None

    def _can_insert_here(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, t: float
    ) -> bool:
        seg_len = self._segment_len(a, b)
        if seg_len < MIN_SEG_LEN_MM:
            return False
        t_min = self.max_eps(MIN_INSERT_OFFSET_MM / max(seg_len, 1e-6))
        return (t > t_min) and (t < 1.0 - t_min)

    def _segment_len(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        return (self._dist_sq(a, b)) ** 0.5

    def max_eps(self, x: float) -> float:
        return max(min(x, 0.49), 0.0)

    def _insert_on_segment(
        self,
        seg: Tuple[str, int, int, int],
        q: AllplanGeo.Point3D,
        keep_selection_left: bool = True,
        mode: str = ""
    ):
        kind, path_idx, seg_idx, _ = seg
        if kind == "active":
            if not (0 <= seg_idx < len(self.points) - 1):
                return
            self.points.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))

            if self.selected_seg and self.selected_seg[0] == "active":
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = (
                        "active",
                        -1,
                        seg_idx if keep_selection_left else seg_idx + 1,
                    )
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ("active", -1, self.selected_seg[2] + 1)

        elif kind == "tubo":
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            # 1. Modificación de la 'Fuente de Verdad'
            current_path = self.script_object.saved_paths[path_idx]
            new_point = AllplanGeo.Point3D(q.X, q.Y, q.Z)
            current_path.insert(seg_idx + 1, new_point)

            # Actualizamos la lista maestra
            self.script_object.saved_paths[path_idx] = current_path

            # 2. RE-CÁLCULO TOTAL (La cadena de mando)
            self.get_segments()             # Recalcula toda la trigonometría de todas las rutas
            self._update_segment_groups()    # Re-mapea puntos con los nuevos SegmentItems

            # 3. RE-DIBUJO TOTAL
            self.script_object._create_elements_preview() # Limpia element_list y crea nuevos 3D
            self._generate_elements_for_preview()         # Envía al Viewport de Allplan

            # Limpieza de UI de inserción
            self.insert_preview_p = None
            self.insert_target = None

    def _seg_equal(
        self, a: Optional[Tuple[str, int, int]], b: Optional[Tuple[str, int, int]]
    ) -> bool:
        if a is None or b is None:
            return False
        return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

    def _update_segments_after_vertex_drag(self, path_idx: int, vertex_idx: int, original_point: AllplanGeo.Point3D, mode: str):
        """
        Sincroniza todos los caminos que coinciden en el 'original_point' para que se
        muevan juntos a la nueva ubicación. Mantiene la conectividad de la red.
        """
        try:
            # 1. Validaciones de seguridad
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            pts_referencia = self.script_object.saved_paths[path_idx]
            if not (0 <= vertex_idx < len(pts_referencia)):
                return

            # 2. Nueva posición (el destino del drag)
            new_point = pts_referencia[vertex_idx]
            new_coords = AllplanGeo.Point3D(new_point.X, new_point.Y, new_point.Z)

            vertices_moved = 0
            paths_affected = 0

            # 3. Escaneo Global de la Red
            for p_idx, path in enumerate(self.script_object.saved_paths):
                modified = False
                for v_idx, vtx in enumerate(path):
                    # USAR DISTANCIA CON TOLERANCIA
                    # A veces los puntos no son EXACTAMENTE iguales por micras.
                    # 0.1 mm es suficiente para considerar que están conectados.
                    dist = math.sqrt((vtx.X - original_point.X)**2 +
                                    (vtx.Y - original_point.Y)**2 +
                                    (vtx.Z - original_point.Z)**2)

                    if dist < 0.1:
                        self.script_object.saved_paths[p_idx][v_idx] = new_coords
                        vertices_moved += 1
                        modified = True

                if modified:
                    paths_affected += 1

            # 4. REGENERACIÓN TOTAL
            # Es crucial llamar a estos métodos para que Allplan reconstruya los 3D
            self.get_segments()             # Re-calcula la lista de segmentos
            self._update_segment_groups()    # Actualiza IDs y tipos
            self.script_object._create_elements_preview() # Regenera los tubos 3D

            print(f"[RED] Movimiento múltiple: {vertices_moved} tubos reconectados en {paths_affected} caminos.")

        except Exception as ex:
            print(f"[ERROR RED] Fallo en sincronización: {ex}")

    # ============================================================================
    # DELETE POLYLINE FOR SEGMENT OR SEGEMENT GROUP
    # ============================================================================
    def delete_selected_segments_by_box(self) -> bool:
        """
        Borra los segmentos seleccionados por marco. Si se seleccionan todos los segmentos de una polilínea,
        se borra toda la polilínea. Si se seleccionan solo algunos, se eliminan esos segmentos y se dividen
        las polilíneas en fragmentos válidos (≥2 puntos).
        """
        if not self.selected_segments:
            message = (
                f"No existen elementos seleccionados para borrar\n"
            )
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)
            return False

        to_delete = defaultdict(set)  # path_idx -> set(seg_idx)
        for kind, _, seg_idx, layer_idx, idx in self.selected_segments:
            if kind == "tubo":
                to_delete[idx].add(seg_idx)

        changed = False
        new_persistent_metadata = {}
        new_saved_paths = []

        message = (
            f"Tipo elemento seleccionado: {kind}\n"
            f"Ruta: {idx}\n"
            f"Cantidad Segmento a borrar: {len(self.selected_segments)}\n\n"
            f"Estas seguro que deseas eliminar los elementos seleccionados?\n"
        )
        result = PythonUtility.ShowMessageBox(message, PythonUtility.MB_YESNO)
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if result == 6:
                if path_idx not in to_delete:
                    # RUTA ENTERA SE MANTIENE: Re-mapeamos sus segmentos a la nueva posición
                    new_path_idx = len(new_saved_paths)
                    for s_idx in range(len(pts) - 1):
                        old_key = f"{path_idx}_{s_idx}"
                        new_key = f"{new_path_idx}_{s_idx}"
                        if old_key in self.script_object.persistent_metadata:
                            new_persistent_metadata[new_key] = self.script_object.persistent_metadata[old_key]

                    new_saved_paths.append(pts)
                    continue
                seg_indices = to_delete[path_idx]
                if len(seg_indices) == len(pts) - 1:
                    # Se seleccionaron todos los segmentos: borrar toda la polilínea
                    changed = True
                    continue
                # Si no, fragmentar en partes válidas (≥2 puntos)
                fragment = [pts[0]]
               # Guardamos los metadatos de los segmentos que sobreviven
                temp_fragments_metadata = []

                for i in range(len(pts) - 1):
                    if i in seg_indices:
                        if len(fragment) >= 2:
                            # Guardamos el fragmento y su metadata acumulada
                            self._add_fragment_with_meta(new_saved_paths, new_persistent_metadata, fragment, temp_fragments_metadata)
                            changed = True
                        fragment = [pts[i + 1]]
                        temp_fragments_metadata = []
                    else:
                        # Este segmento sobrevive: guardamos su info actual
                        old_key = f"{path_idx}_{i}"
                        meta = self.script_object.persistent_metadata.get(old_key)
                        temp_fragments_metadata.append(meta)
                        fragment.append(pts[i + 1])

                if len(fragment) >= 2:
                    self._add_fragment_with_meta(new_saved_paths, new_persistent_metadata, fragment, temp_fragments_metadata)
                    changed = True

        if changed:
            # 1. ACTUALIZACIÓN DE DATOS (El origen de la verdad)
            self.script_object.persistent_metadata = new_persistent_metadata
            self.script_object.saved_paths = new_saved_paths

            # 2. RE-CÁLCULO LÓGICO (Construye los nuevos SegmentItems con la nueva metadata)
            # Es vital que esto ocurra ANTES de crear la preview 3D
            self.get_segments()

            # 3. LIMPIEZA DE INTERFAZ Y ESTADOS
            self.highlight_geometry = None
            self.selected_segments.clear()
            self.selected_seg = None
            self.hover_seg = None
            self.insert_preview_p = None
            self.insert_target = None
            self.hover_mid = None
            self.highlight_geometries.clear()
            self.element_list_final = [] # Limpiamos los elementos lógicos finales

            # 4. REGENARACIÓN DE GRUPOS Y GEOMETRÍA 3D
            self._update_segment_groups()    # Mapea los nuevos SegmentItems a grupos

            # Crea los Polyhedron3D/PythonParts en la memoria del script_object
            self.script_object._create_elements_preview()

            # 5. RENDERIZADO (Viewport)
            self._generate_elements_for_preview() # Convierte la geometría en elementos de Allplan

            # Refresco final de la "línea elástica" si el ratón se está moviendo
            current_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint() # type: ignore
            self._draw_preview(current_pnt)
        return changed

    def _delete_selected_seg(self) -> bool:
        """
        Borra el segmento individual seleccionado en extend_mode (selected_seg).
        Si quedan fragmentos válidos (≥2 puntos) a ambos lados, los conserva como rutas separadas.
        """
        if self.selected_seg is None:
            return False
        try:
            kind = self.selected_seg[0]
            if kind != "tubo":
                return False
            path_idx = self.selected_seg[1]
            seg_idx  = self.selected_seg[2]
        except (IndexError, TypeError):
            return False

        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return False
        pts = self.script_object.saved_paths[path_idx]
        if not pts or seg_idx >= len(pts) - 1:
            return False

        message = (
            f"Tipo elemento seleccionado: {kind}\n"
            f"Ruta: {path_idx}\n"
            f"Segmento: {seg_idx}\n\n"
            f"Estas seguro que deseas eliminar el segmento seleccionado?\n"
        )
        result = PythonUtility.ShowMessageBox(message, PythonUtility.MB_YESNO)
        if result != 6:
            return False

        new_saved_paths: list = []
        new_persistent_metadata: dict = {}

        for idx, path_pts in enumerate(self.script_object.saved_paths):
            if idx != path_idx:
                new_path_idx = len(new_saved_paths)
                for s_idx in range(len(path_pts) - 1):
                    old_key = f"{idx}_{s_idx}"
                    new_key = f"{new_path_idx}_{s_idx}"
                    if old_key in self.script_object.persistent_metadata:
                        new_persistent_metadata[new_key] = self.script_object.persistent_metadata[old_key]
                new_saved_paths.append(path_pts)
            else:
                left  = path_pts[:seg_idx + 1]
                right = path_pts[seg_idx + 1:]

                if len(left) >= 2:
                    new_path_idx = len(new_saved_paths)
                    for s_idx in range(len(left) - 1):
                        old_key = f"{idx}_{s_idx}"
                        new_key = f"{new_path_idx}_{s_idx}"
                        if old_key in self.script_object.persistent_metadata:
                            new_persistent_metadata[new_key] = self.script_object.persistent_metadata[old_key]
                    new_saved_paths.append(left)

                if len(right) >= 2:
                    new_path_idx = len(new_saved_paths)
                    for s_idx in range(len(right) - 1):
                        old_key = f"{idx}_{seg_idx + 1 + s_idx}"
                        new_key = f"{new_path_idx}_{s_idx}"
                        if old_key in self.script_object.persistent_metadata:
                            new_persistent_metadata[new_key] = self.script_object.persistent_metadata[old_key]
                    new_saved_paths.append(right)

        self.script_object.persistent_metadata = new_persistent_metadata
        self.script_object.saved_paths = new_saved_paths

        self.get_segments()
        self.highlight_geometry = None
        self.selected_segments.clear()
        self.selected_seg = None
        self.hover_seg = None
        self.insert_preview_p = None
        self.insert_target = None
        self.hover_mid = None
        self.highlight_geometries.clear()
        self.element_list_final = []

        self._update_segment_groups()
        self.script_object._create_elements_preview()
        self._generate_elements_for_preview()

        current_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint() # type: ignore
        self._draw_preview(current_pnt)
        return True

    def delete_selected_cut_section(self) -> bool:
        if not self.selected_junction:
            message = (
                f"No existe corte seleccionado para borrar\n"
            )
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)
            return False

        # if self.selected_junction:
        path_idx, pt_idx = self.selected_junction[0], self.selected_junction[1]

        message = (
            f"Corte seleccionado:\n"
            f"Ruta: {path_idx}\n"
            f"Punto de corte: {pt_idx}\n\n"
            f"Estas seguro que deseas eliminar el corte seleccionado?\n"
        )
        # Verificar que el punto sigue existiendo y sigue siendo junction
        junction = None
        if (path_idx < len(self.script_object.saved_paths)
                        and pt_idx < len(self.script_object.saved_paths[path_idx])):
                    junction = self._is_junction_point(path_idx, pt_idx)

        if junction is not None:
            # Preparar saved_hover_point para que delete_cut_point lo encuentre
            result = PythonUtility.ShowMessageBox(message, PythonUtility.MB_YESNO)
            if result == 6:
                self.saved_hover_point = self.selected_junction
                deleted = self.delete_cut_point()
                if deleted:
                    print(f"[EVENT 1004] Punto de corte eliminado: junction {junction}")
        else:
            print(f"[EVENT 1004] Junction inválido, limpiando selección")

        # Limpiar siempre
        self.selected_junction = None
        self.hover_cut_vertex  = None
        self.saved_hover_point = None
        return True

    # Función auxiliar para no repetir lógica
    def _add_fragment_with_meta(self, paths_list, meta_dict, points, meta_list):
        new_p_idx = len(paths_list)
        paths_list.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in points])
        for s_idx, meta_obj in enumerate(meta_list):
            if meta_obj:
                meta_dict[f"{new_p_idx}_{s_idx}"] = meta_obj
    # ============================================================================
    # APPLY LAYERS AND ATTRIBUTES
    # ============================================================================
    def apply_layers_to_selected(self):
        """
        Aplica layers a los elementos seleccionados basándose en self.selected_segments
        Estructura de selected_segments: {('tubo', 0, 2), ('union', 0, 5), ...}
        """
        self.layer_selected = None

        # Obtener ID y Nombre del Layer seleccionado
        chosen_installation = [
            item
            for item in self.script_object.layer_types
            if item["label"] == getattr(self.script_object.build_ele, ParamNames.Layers.TYPES).value
        ]

        if not chosen_installation:
            print("Error: No se encontró el layer seleccionado")
            return

        self.layer_selected = chosen_installation[0]["key"]
        layer_name = chosen_installation[0]["label"]

        print(f"Applying Layer: {layer_name} (ID: {self.layer_selected})")
        applied_count = 0
        # Iterar sobre el set de elementos seleccionados
        # item es una tupla: ('tipo', path_idx, element_idx, layer_idx)
        if self.selected_segments:
            for item in self.selected_segments:
                if len(item) == 5:
                    elem_type, path_idx, elem_idx, layer_idx, idx = item
                    # Llamamos a apply_layer pasando los datos desagregados
                    self.apply_layer(
                        elem_type=elem_type,
                        path_idx=idx,
                        elem_idx=elem_idx,
                        layer_idx=layer_idx,
                    )
                    applied_count += 1

            # Mensaje de éxito
            message = (
                f"✅ Layer aplicado exitosamente!\n\n"
                f"Layer: {layer_name}\n"
                f"ID: {self.layer_selected}\n\n"
                f"Elementos actualizados: {applied_count}"
            )
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)

        elif self.selected_element_id:
            elem_type, path_idx, elem_idx, layer_idx, idx = self.selected_element_id
            self.apply_layer(
                elem_type=elem_type,
                path_idx=idx,
                elem_idx=elem_idx,
                layer_idx=layer_idx,
            )
            message = (
                f"✅ Layer aplicado exitosamente!\n\n"
                f"Layer: {layer_name}\n"
                f"ID: {self.layer_selected}\n\n"
                f"TYPE: {elem_type}"
            )
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)
        else:
            print("No hay segmentos seleccionados.")

    def apply_layer(self, elem_type, path_idx, elem_idx, layer_idx):
        """
        Aplica el layer y actualiza self.applied_layers usando la estructura de claves:
        "seg_{path_idx}_elem_{elem_idx}" para coincidir con custom_attributes.
        """
        # 1. Inicializar el diccionario maestro si no existe
        if not hasattr(self, 'applied_layers'):
            self.applied_layers = {}

        if not self.layer_selected:
            return

        # 2. Crear instancia
        applied = AppliedLayer(
            layer=self.layer_selected,
            type=elem_type,
            path_idx=path_idx,
            elem_idx=elem_idx,
            layer_idx=layer_idx
        )

        # 3. Guardar en el diccionario
        self.script_object.applied_layers[applied.storage_key] = applied.to_dict()

        # ---------------------------------------------------------
        # 4. Actualizar generated_elements (Vista previa/interactiva)
        # ---------------------------------------------------------
        # Mantenemos la actualización de la lista de elementos generados
        # para que el cambio sea visible inmediatamente sin recrear todo
        generated_paths = getattr(self, "generated_elements", [])
        for path_group in generated_paths:  # Primer nivel: Las rutas
            for element in path_group:      # Segundo nivel: Los elementos
                key = element.get('key')
                if key and len(key) >= 4:
                    if key[1] == path_idx and key[3] == layer_idx:
                        element['layer'] = self.layer_selected
                        break
        print(f"DEBUG - Layer guardado en clave: {applied.storage_key} -> ID: {self.layer_selected}")

    def apply_layer_default(self):
        if self.script_object.default_layers:
            self.layer_default = self.script_object.default_layers.get("default", "")

    def apply_attributes_input(self):
        """
        Aplica atributos personalizados a los elementos seleccionados.
        Guarda la configuración en self.custom_attributes para ser procesada por _create_elements.
        """
        # 1. Validar Input de Texto
        input_attribute_val = getattr(self.script_object.build_ele, ParamNames.Attributes.VALUE).value
        if not input_attribute_val:
            PythonUtility.ShowMessageBox("⚠️ Debes escribir un valor para el atributo.", PythonUtility.MB_OK)
            return

        # 2. Preparar los Objetos Atributo
        doc = self.coord_input.GetInputViewDocument() # type: ignore

        attr_6_cc_is = "6_CC_IS"
        attr_pmp_pare = "pmp_pare"

        attr_6_cc_is_id = AttributeService.GetAttributeID(doc, attr_6_cc_is)
        attr_pmp_pare_id = AttributeService.GetAttributeID(doc, attr_pmp_pare)

        # Lista de atributos a aplicar
        attributes_to_apply = [
            AllplanBaseElements.AttributeString(attr_6_cc_is_id, input_attribute_val),
            AllplanBaseElements.AttributeString(attr_pmp_pare_id, input_attribute_val)
        ]

        # 3. Determinar objetivos (Selección Múltiple o Simple)
        targets = []
        if self.selected_segments:
            targets = list(self.selected_segments)
        elif self.selected_element_id: # Fallback para selección simple (hover/click único)
            targets = [self.selected_element_id]

        if not targets:
            PythonUtility.ShowMessageBox("⚠️ Selecciona elementos para aplicar atributos.", PythonUtility.MB_OK)
            return

        # 4. Asegurar que existe el diccionario de almacenamiento
        if not hasattr(self, "custom_attributes"):
            self.custom_attributes = {}

        applied_count = 0
        affected_paths = set()

        # 5. Iterar y Guardar
        for item in targets:
            storage_key = ""

            # Desempaquetar la tupla (igual que en apply_layers_to_selected)
            elem_type, path_idx, elem_idx, layer_idx, idx = item

            # index = layer_idx if inst_type in self.simple_installation else elem_idx
            storage_key = f"seg_{idx}_elem_{layer_idx}"

            # Guardar en el diccionario persistente
            self.script_object.applied_attributes[storage_key] = attributes_to_apply

            applied_count += 1
            affected_paths.add(idx)

        # ---------------------------------------------------------
        # 4. Actualizar generated_elements (Vista previa/interactiva)
        # ---------------------------------------------------------
        # Mantenemos la actualización de la lista de elementos generados
        # para que el cambio sea visible inmediatamente sin recrear todo
        generated_paths = getattr(self, "generated_elements", [])
        for path_group in generated_paths:  # Primer nivel: Las rutas
            for element in path_group:      # Segundo nivel: Los elementos
                key = element.get('key')
                if key and len(key) >= 4:
                    if key[1] == path_idx and key[3] == layer_idx:
                        element['attribute'] = input_attribute_val
                        break

        # 6. Feedback al Usuario
        message = (
            f"✅ Atributos aplicados exitosamente!\n\n"
            f"Atributos actualizados: {attr_6_cc_is} - {attr_pmp_pare}\n"
            f"Valor: {input_attribute_val}\n"
            f"Elementos actualizados: {applied_count}\n"
        )
        PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)

    # ============================================================================
    # EVENTS
    # ============================================================================
    def on_preview_draw(self):
        current_pnt = self.coord_input.GetCurrentPoint(self.current_point).GetPoint() # type: ignore
        self._draw_preview(current_pnt)

    def on_mouse_leave(self):
        self.on_preview_draw()

    def on_cancel_function(self):
        """ESC: Validar, guardar si es correcto o permitir seguir editando."""
        try:
            print("[INT] ESC/Finalizar: Validando antes de crear...")
            if not self.saved_elements:
                self._save_current_polyline()
                self.script_object._create_elements_preview()
                # self._update_segment_groups()
                # self.saved_elements = True

            status = "OK" #self._is_geometry_valid()
            if status == "OK":
                print("[INT] ESC/Finalizar: guardando y creando inmediatamente...")
                # Si todo está bien, creamos y cerramos
                self.script_object.element_list_final = []
                self.script_object._generate_pythonparts()
                return OnCancelFunctionResult.CREATE_ELEMENTS

            elif status == "BORRAR":
                # El usuario confirmó que quiere descartar todo
                # Dependiendo de tu API, CANCEL_INPUT cierra la herramienta sin crear nada
                return OnCancelFunctionResult.CANCEL_INPUT

            elif status == "EDITAR":
                # El usuario quiere corregir los ángulos, NO cerramos la herramienta
                return  OnCancelFunctionResult.RESTART  # O el equivalente para mantener la herramienta abierta

        except Exception as ex:
            self.script_object.element_list_final = []
            self.script_object._generate_pythonparts()
            print(f"[INT] Error during cancel function: {ex}")
            return OnCancelFunctionResult.CANCEL_INPUT

    def on_control_event(self, event_id: int):
        """1001=toggle crear; 1002=guardar; 1003=finalizar(ESC); 1004=borrar; 1006=toggle bifurcar"""
        print(f"[SO] on_control_event: {event_id}")
        if event_id == 1004:
            # A) Borrar segmentos seleccionados por box
            if self.selected_segments and not self.selected_junction:
                self.delete_selected_segments_by_box()

            # B) Borrar punto de corte (junction) seleccionado
            elif self.selected_junction is not None:
                self.delete_selected_cut_section()

            # C) Borrar segmento seleccionado individualmente (extend_mode)
            elif self.selected_seg is not None:
                self._delete_selected_seg()

        elif event_id == 1003:  # Finalizar -> guardar y crear inmediatament
            print("[SO] Finalizar -> guardar y crear inmediatamente")
            name = "CancelInput"
            meth = getattr(self.coord_input, name, None)
            if callable(meth):
                try:
                    meth()
                        # break
                except Exception as ex:
                    print(f"[SO] coord_input.{name}() ex: {ex}")

        elif event_id == 1009:
            self.apply_layers_to_selected()

        elif event_id == 1010:
            self.applie_info_element_selected()
            return True

        elif event_id == 1011:
            self.apply_attributes_input()

        elif event_id == 1012:
            # Definir orientación 3D (captura de línea en XY)
            return bool(self.start_orientation_capture())

    # ========================================
    # HELPERS
    # ========================================
    def _is_geometry_valid(self):
        """Verifica si la geometría actual es válida para ser creada."""
        if not self.segment_groups:
            self._save_current_polyline()
            self.saved_elements = True

        verify_angles = self._detect_angles(segments=self.segment_groups[0], angles_to_find=self.script_object.allowed_angles)

        if verify_angles:
            message = (
                f"Tipo de instalacion: {self.script_object.selected_inst_type}\n"
                f"Angulos soportados: {self.script_object.support_angles}\n\n"
                f"La polilínea posee ángulos no permitidos.\n\n"
                f"¿Desea BORRAR TODO y salir?\n\n"
                f"[SI] Borra los datos.\n"
                f"[NO] Volver a la edición para corregir."
            )
            result = PythonUtility.ShowMessageBox(message, PythonUtility.MB_YESNO)

            if result == 6: # Eligió SÍ: Borrar
                self.saved_elements = False
                self.segment_groups.clear()
                return "BORRAR"
            else: # Eligió NO: Seguir editando
                return "EDITAR"

        return "OK" # Todo correcto

    def _detect_angles(self, segments, angles_to_find=None):
        """
        Detecta ángulos no permitidos normalizando a un rango de 0-360°
        y corrigiendo errores de precisión de punto flotante.

        Returns:
            bool: True si hay ángulos PROHIBIDOS, False si todo está OK.
        """
        if not angles_to_find:
            return False

        # Normalizamos la lista de permitidos a 0-360 y redondeamos
        allowed_normalized = [round(a % 360, 4) for a in angles_to_find]
        for segment in segments:
            # 1. Redondeamos el ángulo original para eliminar ruido (ej: 359.9999... -> 360.0)
            raw_angle = round(segment.data.angulo_xy_desde_x, 4)

            # 2. Normalizamos al rango 0-360 (ej: 360.0 -> 0.0)
            current_angle = raw_angle % 360
            # Caso especial: Si tras el módulo el resultado es 360 (por precisión), es 0
            if abs(current_angle - 360) < 0.001:
                current_angle = 0.0

            is_allowed = False
            for allowed in allowed_normalized:
                # Tolerancia de 0.5 grados para dibujo manual
                if abs(current_angle - allowed) < 0.5:
                    is_allowed = True
                    break

            if not is_allowed:
                print(f"[DEBUG] Ángulo prohibido detectado: {current_angle}° (Original: {segment.data.angulo_xy_desde_x}°)")
                return True

        return False

    # ============================================================================
    # ORIENTACIÓN 3D: helpers de paleta/prompt + captura (evento 1012)
    # ============================================================================
    def _set_prompt(self, msg: str) -> None:
        try:
            if self.coord_input:
                self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
        except Exception:
            pass

    def start_orientation_capture(self):
        """
        Toggle del modo de captura de línea de orientación en el plano XY.
        - Si el modo está activo y ya hay línea definida: guarda y desactiva
        - Si el modo está activo pero no hay línea: cancela
        - Si el modo no está activo: activa el modo
        """
        if self.orientation_capture_mode:
            if self.orientation_line_start is not None and self.orientation_line_end is not None:
                print("[INT] Guardando orientación 3D y desactivando modo...")
                self._save_orientation_from_line()
                self._cancel_orientation_capture()
                return True
            print("[INT] Cancelando captura de orientación 3D")
            self._cancel_orientation_capture()
            return True

        self.orientation_capture_mode = True
        self.orientation_line_start = None
        self.orientation_line_end = None
        self.orientation_line_preview = None
        print("[INT] Modo captura de orientación 3D activado")
        print("[INT] Click en el plano XY para definir el primer punto de la línea de orientación")
        self._set_prompt("Orientación 3D: Click para definir primer punto (plano XY)")
        return True

    def _handle_orientation_capture(self, mouse_msg, raw_pnt: AllplanGeo.Point3D) -> bool:
        """Maneja la captura de la línea de orientación (2 clicks en plano XY, Z=0)."""
        # Ya tenemos ambos puntos: sólo refrescar preview durante movimiento
        if self.orientation_line_start is not None and self.orientation_line_end is not None:
            if self.coord_input and self.coord_input.IsMouseMove(mouse_msg):
                self._draw_preview(raw_pnt)
            return True

        # Movimiento: actualizar preview temporal
        if self.coord_input and self.coord_input.IsMouseMove(mouse_msg):
            if self.orientation_line_start is not None:
                self.orientation_line_preview = raw_pnt
                self._draw_preview(raw_pnt)
            return True

        # Click izquierdo
        is_left = getattr(mouse_msg, "Button", 1) == 1
        if not is_left:
            return True

        if self.orientation_line_start is None:
            self.orientation_line_start = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
            self.orientation_line_end = None
            self.orientation_line_preview = None
            print(f"[INT] Primer punto orientación: ({self.orientation_line_start.X:.2f}, {self.orientation_line_start.Y:.2f}, 0.0)")
            self._set_prompt("Orientación 3D: Click para definir segundo punto (plano XY)")
            return True

        # Segundo punto
        p2 = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
        dx = p2.X - self.orientation_line_start.X
        dy = p2.Y - self.orientation_line_start.Y
        dist_xy = (dx * dx + dy * dy) ** 0.5
        if dist_xy < 1e-6:
            print("[INT] Error: La línea de orientación es demasiado corta. Intente con otro punto.")
            return True

        self.orientation_line_end = p2
        self.orientation_line_preview = None
        angle_rad = math.atan2(dy, dx)
        print(f"[INT] Segundo punto orientación: ({p2.X:.2f}, {p2.Y:.2f}, 0.0)")
        print(f"[INT] Ángulo calculado: {math.degrees(angle_rad):.2f}° (desde eje X)")
        print("[INT] ✓ Línea definida. Presione 'Definir orientación' para guardar.")
        self._set_prompt("Orientación 3D: ✓ Línea definida. Presione 'Definir orientación' para guardar.")
        return True

    def _save_orientation_from_line(self) -> bool:
        """Guarda reference_orientation_angle desde la línea definida (start/end) en radianes."""
        if self.orientation_line_start is None or self.orientation_line_end is None:
            print("[INT] Error: No hay línea completa para guardar")
            return False

        dx = self.orientation_line_end.X - self.orientation_line_start.X
        dy = self.orientation_line_end.Y - self.orientation_line_start.Y
        dist_xy = (dx * dx + dy * dy) ** 0.5
        if dist_xy < 1e-6:
            print("[INT] Error: La línea de orientación es demasiado corta. No se guarda.")
            return False

        angle_rad = math.atan2(dy, dx)
        self.script_object.reference_orientation_angle = angle_rad

        print(f"[INT] ✓ Orientación 3D guardada: {math.degrees(angle_rad):.1f}° (desde eje X)")
        self._update_orientation_info()
        return True

    def _cancel_orientation_capture(self) -> bool:
        if self.orientation_capture_mode:
            self.orientation_capture_mode = False
            self.orientation_line_start = None
            self.orientation_line_end = None
            self.orientation_line_preview = None
            self._set_prompt("Click: agregar punto | ESC: terminar")
            return True
        return False

    def _update_orientation_info(self) -> None:
        ref = self.script_object.reference_orientation_angle
        if ref is None:
            info_text = "No definida"
        else:
            angle_deg = (math.degrees(ref) % 360.0 + 360.0) % 360.0
            info_text = f"{angle_deg:.1f} grados"

        param = getattr(self.script_object.build_ele, ParamNames.Angles.ROTATION_ANGLE)
        param.value = info_text

    # ==========================================================================================================================================
