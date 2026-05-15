# -*- coding: utf-8 -*-
"""
PointInput — Modo de entrada de puntos del optimizador.

Gestiona el modo de dibujo "Puntos No Definidos": el usuario activa el modo
vía CheckBox ``UndefinedPointsMode``, hace clic en el viewport para colocar
puntos con tipo y color desde la paleta, y finalmente pulsa "Generar Camino Óptimo".

Lee los parámetros de paleta directamente desde ``build_ele`` usando los
nombres definidos en ``parameters.ParamNames.PointInput``
(``TipoPuntoOrden``, ``ColorPuntosNoDefinidos``, tolerancia, etc.).

Guarda cada punto como :class:`~optimizer.UndefinedPoint` en
``script_object.undefined_points_list`` y genera la lista de
:class:`~optimizer.OptimizerNode` en ``script_object.nodo_list`` que
``PolylineOptimizer._build_camino_dict`` consume directamente.

Flujo::

    # 1. CheckBox UndefinedPointsMode → interactor.punto_input_mode = True
    # 2. Cada clic en viewport → PointInput.handle_click(current_pnt)
    #       guarda UndefinedPoint en undefined_points_list
    #       actualiza nodo_list y overlay
    # 3. "Generar Camino Óptimo" (EventId 1041) → optimizer.run()
    #       lee nodo_list via _build_camino_dict
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .interactor import PolylineInteractor

from .models import  OptimizerRole, UndefinedPoint
from .parameters import ParamNames

try:
    import NemAll_Python_Geometry as AllplanGeo
    import NemAll_Python_BasisElements as AllplanBasisElements
    import NemAll_Python_BaseElements as AllplanBaseElements
    _ALLPLAN_AVAILABLE = True
except Exception:
    AllplanGeo = None
    AllplanBasisElements = None
    AllplanBaseElements = None
    _ALLPLAN_AVAILABLE = False


TIPO_PUNTO_TO_SHAPE: Dict[str, str] = {
    OptimizerRole.INICIO.value:     "circle",
    OptimizerRole.BIFURCACION.value: "pentagon",
    OptimizerRole.PASO.value:       "triangle",
    OptimizerRole.FINAL.value:      "square",
}

INST_TYPE_TO_LABEL: Dict[str, str] = {
    "conducto impulsion":  "impulsion",
    "conducto extraccion": "extraccion",
    "conducto aislado":    "aislado",
    "conducto recuperador":"recuperador",
}

COLOR_NAME_TO_ID: dict[str, int] = {
    "Negro": 1,
    "Rojo": 6,
    "Amarillo": 2,
    "Verde": 4,
    "Cyan": 3,
    "Azul": 7,
    "Magenta": 5,
}


def color_name_to_id(color_name: str, default: int = 1) -> int:
    """Mapea un nombre de color de paleta a color ID de Allplan."""
    if color_name is None:
        return default
    return COLOR_NAME_TO_ID.get(str(color_name).strip(), default)

def _shape_for_role(role_value: str) -> str:
    return TIPO_PUNTO_TO_SHAPE.get(role_value, "circle")


class UndefinedPointInput:
    """Gestiona el modo de entrada de puntos para el optimizador.

    Lee los parámetros de paleta directamente desde ``build_ele``.
    Guarda puntos como :class:`UndefinedPoint` en
    ``script_object.undefined_points_list`` y construye
    ``script_object.nodo_list`` (lista de :class:`OptimizerNode`)
    que ``PolylineOptimizer._build_camino_dict`` consume.

    Args:
        interactor: Instancia activa del interactor de polilínea.
    """

    def __init__(self, interactor: "PolylineInteractor") -> None:
        self._interactor = interactor

    @property
    def _so(self) -> Any:
        return self._interactor.script_object

    @property
    def _build_ele(self) -> Any:
        return getattr(self._so, "build_ele", None)

    # ─────────────────────────────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────────────────────────────

    def _snap_guide_elems(self, current_pnt: Any, path_key: str) -> List[Any]:
        """Línea de tracking pespunteada desde el último punto del camino al cursor.

        Usa ``Stroke`` discontinuo (Strichart) para imitar la línea de seguimiento
        nativa de Allplan.
        """
        if AllplanGeo is None or AllplanBasisElements is None or AllplanBaseElements is None:
            return []
        undef_list = getattr(self._so, "undefined_points_list", None) or []
        same_path = [up for up in reversed(undef_list) if up.path_key == path_key]
        if not same_path:
            return []
        p0 = _coords_to_point3d(same_path[0].coordenadas)
        if p0 is None:
            return []
        try:
            guide_prop = AllplanBaseElements.CommonProperties()  # type: ignore[union-attr]
            guide_prop.GetGlobalProperties()
            guide_prop.Color        = 8      # gris — igual que la línea de tracking de Allplan
            guide_prop.ColorByLayer = False
            guide_prop.Pen          = 1      # línea fina
            guide_prop.PenByLayer   = False
            guide_prop.Stroke       = 3      # Strichart discontinuo (dash-dot)
            guide_prop.StrokeByLayer = False
        except Exception:
            return []
        return [AllplanBasisElements.ModelElement3D(  # type: ignore[union-attr]
            guide_prop, AllplanGeo.Line3D(p0, current_pnt)
        )]

    # ─────────────────────────────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────────────────────────────

    def handle_click(self, current_pnt: Any) -> None:
        """Añade un punto al modelo con el tipo y color actuales de la paleta.

        Lee ``TipoPuntoOrden`` y ``ColorPuntosNoDefinidos`` directamente desde
        ``build_ele``. El color determina el ``path_key``
        (un color = un camino). Los puntos de distinto color que caigan dentro
        de la tolerancia de detección se anclan como punto común (``CP-N``).

        Guarda un :class:`UndefinedPoint` en ``undefined_points_list`` y
        actualiza ``nodo_list`` con el :class:`OptimizerNode` correspondiente.

        Args:
            current_pnt: Punto 3D ya snapeado/proyectado de ``process_mouse_msg``.
        """
        if not _ALLPLAN_AVAILABLE or current_pnt is None:
            return

        be = self._build_ele
        tipo_label  = getattr(getattr(be, ParamNames.PointInput.TIPO_PUNTO, None), "value", "Inicial")
        color_value = getattr(getattr(be, ParamNames.PointInput.COLOR, None), "value", "Negro")
        color_id    = color_name_to_id(color_value)
        role      = OptimizerRole.from_label(tipo_label)
        inst_type = getattr(self._so, "selected_inst_type", "") or ""
        path_key  = f"{inst_type}:{color_id}"
        print(f"[PointInput] handle_click → tipo_label='{tipo_label}' role={role.value} inst_type='{inst_type}'")

        if not getattr(self._so, "undefined_points_list", None):
            self._so.undefined_points_list = []
        undef_list: List[UndefinedPoint] = self._so.undefined_points_list

        #assert AllplanGeo is not None
        pos = AllplanGeo.Point3D(  # type: ignore[union-attr]
            float(current_pnt.X), float(current_pnt.Y), float(current_pnt.Z)
        )
        common_node_id: Optional[str] = None

        common_enabled = getattr(getattr(be, "DeteccionPuntosComunesActiva", None), "value", True)
        if common_enabled:
            tol_mm = getattr(getattr(be, "ToleranciaPuntosComunesMm", None), "value", 5.0)
            anchor = self._find_common_anchor(undef_list, pos, path_key, tol_mm)
            if anchor is not None:
                ap = anchor.coordenadas
                pos = AllplanGeo.Point3D(ap["x"], ap["y"], ap["z"])  # type: ignore[union-attr]
                common_node_id = self._ensure_common_node_id(anchor)
                print(
                    f"[PointInput] Snap → camino {anchor.path_key}, "
                    f"node_id={common_node_id}"
                )

        # ── Construir UndefinedPoint ──────────────────────────────────────
        idx    = len(undef_list)
        nid    = f"U{color_id}-{idx}"
        coords = {"x": float(pos.X), "y": float(pos.Y), "z": float(pos.Z)}

        up = UndefinedPoint(
            id             = nid,
            tipo           = role,
            coordenadas    = coords,
            path_key       = path_key,
            color_id       = color_id,
            common_node_id = common_node_id,
            inst_type      = inst_type,
        )
        undef_list.append(up)

        print(
            f"[PointInput] #{idx}: tipo={role.value}, path={path_key}, "
            f"pos=({pos.X:.0f}, {pos.Y:.0f}, {pos.Z:.0f})"
        )

        # ── Reconstruir nodo_list y overlay ──────────────────────────────
        self._rebuild_nodo_list(undef_list)
        self._update_overlay(undef_list)

    def delete_at(self, index: int) -> None:
        """Borra el :class:`UndefinedPoint` en ``index`` y reconstruye nodo_list y overlay."""
        undef_list: List[UndefinedPoint] = getattr(self._so, "undefined_points_list", None) or []
        if not (0 <= index < len(undef_list)):
            return
        removed = undef_list.pop(index)
        print(f"[PointInput] Borrado nodo #{index} id={removed.id} tipo={removed.tipo.value}")
        self._rebuild_nodo_list(undef_list)
        self._update_overlay(undef_list)

    def clear(self) -> None:
        """Borra todos los puntos colocados y limpia overlay y nodo_list."""
        self._so.undefined_points_list = []
        self._so.nodo_list = []
        self._interactor._optimizer_preview_elems = []
        self._interactor._free_points = []
        print("[PointInput] Puntos borrados.")

    def draw_cursor_preview(self, current_pnt: Any) -> List[Any]:
        """Forma de preview en la posición del cursor (se llama en cada MouseMove).

        Args:
            current_pnt: Posición actual del cursor.

        Returns:
            Lista de ``ModelElement3D`` con la forma correspondiente al tipo seleccionado.
        """
        if not _ALLPLAN_AVAILABLE or current_pnt is None:
            return []
        be          = self._build_ele
        tipo_lbl    = getattr(getattr(be, "TipoPuntoOrden", None), "value", "Inicial")
        color_value = getattr(getattr(be, "ColorPuntosNoDefinidos", None), "value", "Negro")
        color_id = color_name_to_id(color_value)
        role     = OptimizerRole.from_label(tipo_lbl)
        prop = _make_properties(color_id)
        if prop is None:
            return []
        return _make_shape_elems_3d(current_pnt, role.value, prop, size=150.0)

    # ─────────────────────────────────────────────────────────────────────
    # Construcción de nodo_list
    # ─────────────────────────────────────────────────────────────────────

    def _rebuild_nodo_list(self, undef_list: List[UndefinedPoint]) -> None:
        """Convierte ``undefined_points_list`` → ``nodo_list`` y ``camino_inst_types``.

        ``nodo_list`` es ``List[List[OptimizerNode]]``: cada sublista agrupa
        los nodos de la misma clave ``(inst_type, color_id)`` — un camino
        independiente por combinación de tipo de instalación y color.
        El orden de inserción dentro de cada grupo se preserva.

        ``camino_inst_types`` es ``List[str]``: un valor por camino (mismo orden
        que ``nodo_list``), tomado del ``inst_type`` de la clave del grupo.

        Esto permite tener dos caminos del mismo color (p.ej. Negro) pero de
        distinto tipo de instalación (p.ej. Impulsión y Recuperador).
        """
        groups: Dict[tuple, List] = {}
        for up in undef_list:
            key = (up.inst_type or "", up.color_id)
            groups.setdefault(key, []).append(up.to_optimizer_node())

        ordered_keys = list(groups.keys())
        self._so.nodo_list          = list(groups.values())
        self._so.camino_inst_types  = [inst for inst, _ in ordered_keys]
        # Mapeo color_id → índice de saved_optimized_paths (mismo orden que nodo_list)
        self._so.auto_path_color_ids = [color_id for _, color_id in ordered_keys]

    # ─────────────────────────────────────────────────────────────────────
    # Overlay (preview de puntos colocados)
    # ─────────────────────────────────────────────────────────────────────

    def _update_overlay(self, undef_list: List[UndefinedPoint]) -> None:
        """Reconstruye el overlay con las formas de todos los puntos colocados."""
        if not _ALLPLAN_AVAILABLE:
            self._interactor._optimizer_preview_elems = []
            return
        try:
            be           = self._build_ele
            halo_color_name = getattr(getattr(be, "ColorResaltadoPuntosComunes", None), "value", "Rojo")
            halo_color   = color_name_to_id(halo_color_name, default=6)
            halo_prop    = _make_properties(halo_color)
            elems: List[Any] = []

            for up in undef_list:
                prop = _make_properties(up.color_id)
                if prop is None:
                    continue
                pos_pt = _coords_to_point3d(up.coordenadas)
                if pos_pt is None:
                    continue
                elems.extend(_make_shape_elems_3d(pos_pt, up.tipo.value, prop, size=150.0))
                if up.common_node_id and halo_prop is not None:
                    elems.extend(_make_circle_elems(pos_pt, halo_prop, size=150.0 * 1.35))
                label = _inst_type_to_label(up.inst_type)
                if label:
                    elems.extend(_make_text_elem(pos_pt, label, up.color_id))

            self._interactor._optimizer_preview_elems = elems
            self._interactor._free_points = [
                _coords_to_point3d(up.coordenadas)
                for up in undef_list
                if _coords_to_point3d(up.coordenadas) is not None
            ]
        except Exception as ex:
            print(f"[PointInput] Error generando overlay: {ex}")
            self._interactor._optimizer_preview_elems = []

    # ─────────────────────────────────────────────────────────────────────
    # Detección de puntos comunes
    # ─────────────────────────────────────────────────────────────────────

    def _find_common_anchor(
        self,
        undef_list: List[UndefinedPoint],
        pos: Any,
        current_path_key: str,
        tolerance_mm: float,
    ) -> Optional[UndefinedPoint]:
        """Busca un punto de OTRO camino dentro de tolerancia XY."""
        tol_sq = max(float(tolerance_mm), 0.0) ** 2
        best:    Optional[UndefinedPoint] = None
        best_d2: float = tol_sq + 1.0
        for up in undef_list:
            if up.path_key == current_path_key:
                continue
            dx = up.coordenadas["x"] - float(pos.X)
            dy = up.coordenadas["y"] - float(pos.Y)
            d2 = dx * dx + dy * dy
            if d2 <= tol_sq and d2 < best_d2:
                best_d2 = d2
                best = up
        return best

    def _ensure_common_node_id(self, anchor: UndefinedPoint) -> str:
        """Garantiza que el ancla tenga ``common_node_id`` y lo retorna."""
        if anchor.common_node_id:
            return anchor.common_node_id
        seq = int(getattr(self._so, "_common_point_seq", 0)) + 1
        self._so._common_point_seq = seq
        node_id = f"CP-{seq}"
        anchor.common_node_id = node_id
        return node_id


# ─────────────────────────────────────────────────────────────────────────────
# Helpers geométricos (formas de preview)
# ─────────────────────────────────────────────────────────────────────────────
def _make_properties(color_id: int) -> Any:
    if AllplanBaseElements is None:
        return None
    try:
        prop = AllplanBaseElements.CommonProperties()
        prop.GetGlobalProperties()
        prop.Color        = int(color_id)
        prop.ColorByLayer = False
        prop.PenByLayer   = False
        return prop
    except Exception:
        return None

def _coords_to_point3d(coords: Dict[str, float]) -> Any:
    if AllplanGeo is None:
        return None
    try:
        return AllplanGeo.Point3D(  # type: ignore[union-attr]
            float(coords.get("x", 0.0)),
            float(coords.get("y", 0.0)),
            float(coords.get("z", 0.0)),
        )
    except Exception:
        return None

def _make_circle_elems(pos: Any, prop: Any, size: float, segments: int = 24) -> List[Any]:
    if AllplanGeo is None or AllplanBasisElements is None or prop is None:
        return []
    cx = float(getattr(pos, "X", 0.0))
    cy = float(getattr(pos, "Y", 0.0))
    cz = float(getattr(pos, "Z", 0.0))
    pairs = _circle_pairs(cx, cy, cz, size, segments)
    return [
        AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(p1, p2))  # type: ignore[union-attr]
        for p1, p2 in pairs
    ]

def _pt(x: float, y: float, z: float) -> Any:
    return AllplanGeo.Point3D(x, y, z)  # type: ignore[union-attr]

def _circle_pairs(
    cx: float, cy: float, cz: float, size: float, segments: int = 32
) -> List[Tuple[Any, Any]]:
    r = max(size * 0.5, 0.1)
    pts = [
        _pt(cx + r * math.cos(2 * math.pi * i / segments),
            cy + r * math.sin(2 * math.pi * i / segments), cz)
        for i in range(segments + 1)
    ]
    return [(pts[i], pts[i+1]) for i in range(len(pts) - 1)]


# ─────────────────────────────────────────────────────────────────────────────
# Formas 3D (wireframe volumétrico)
# ─────────────────────────────────────────────────────────────────────────────

def _shape_pairs_3d(
    cx: float, cy: float, cz: float, shape: str, size: float
) -> List[Tuple[Any, Any]]:
    """Versión 3D de ``_shape_pairs``. Despacha al constructor específico."""
    if shape == "square":
        return _square_pairs_3d(cx, cy, cz, 100)
    if shape == "triangle":
        return _triangle_pairs_3d(cx, cy, cz, size)
    if shape == "pentagon":
        return _pentagon_pairs_3d(cx, cy, cz, 100)
    return _circle_pairs_3d(cx, cy, cz, size)   # circle / rhombus / default

def _square_pairs_3d(
    cx: float, cy: float, cz: float, size: float
) -> List[Tuple[Any, Any]]:
    """Cubo wireframe centrado en (cx, cy, cz)."""
    h = size * 0.5
    # 8 vértices
    blf = _pt(cx-h, cy-h, cz-h); brf = _pt(cx+h, cy-h, cz-h)
    brf2= _pt(cx+h, cy+h, cz-h); blf2= _pt(cx-h, cy+h, cz-h)
    tlf = _pt(cx-h, cy-h, cz+h); trf = _pt(cx+h, cy-h, cz+h)
    trf2= _pt(cx+h, cy+h, cz+h); tlf2= _pt(cx-h, cy+h, cz+h)
    return [
        # cara inferior
        (blf, brf), (brf, brf2), (brf2, blf2), (blf2, blf),
        # cara superior
        (tlf, trf), (trf, trf2), (trf2, tlf2), (tlf2, tlf),
        # pilares verticales
        (blf, tlf), (brf, trf), (brf2, trf2), (blf2, tlf2),
    ]

def _triangle_pairs_3d(
    cx: float, cy: float, cz: float, size: float
) -> List[Tuple[Any, Any]]:
    """Tetraedro wireframe centrado en (cx, cy, cz)."""
    h = size * 0.5
    # base: triángulo equilátero en plano Z-h
    r_base = h
    base = [
        _pt(cx + r_base * math.cos(2 * math.pi * i / 3 - math.pi / 2),
            cy + r_base * math.sin(2 * math.pi * i / 3 - math.pi / 2),
            cz - h)
        for i in range(3)
    ]
    apex = _pt(cx, cy, cz + h)
    return [
        # base
        (base[0], base[1]), (base[1], base[2]), (base[2], base[0]),
        # aristas al ápice
        (base[0], apex), (base[1], apex), (base[2], apex),
    ]

def _pentagon_pairs_3d(
    cx: float, cy: float, cz: float, size: float
) -> List[Tuple[Any, Any]]:
    """Prisma pentagonal wireframe centrado en (cx, cy, cz)."""
    r = max(size * 0.5, 0.1)
    h = size * 0.5
    bottom = [
        _pt(cx + r * math.cos(2 * math.pi * i / 5 - math.pi / 2),
            cy + r * math.sin(2 * math.pi * i / 5 - math.pi / 2),
            cz - h)
        for i in range(5)
    ]
    top = [
        _pt(cx + r * math.cos(2 * math.pi * i / 5 - math.pi / 2),
            cy + r * math.sin(2 * math.pi * i / 5 - math.pi / 2),
            cz + h)
        for i in range(5)
    ]
    pairs: List[Tuple[Any, Any]] = []
    for i in range(5):
        pairs.append((bottom[i], bottom[(i + 1) % 5]))   # cara inferior
        pairs.append((top[i],    top[(i + 1) % 5]))      # cara superior
        pairs.append((bottom[i], top[i]))                 # pilares
    return pairs

def _circle_pairs_3d(
    cx: float, cy: float, cz: float, size: float, segments: int = 24
) -> List[Tuple[Any, Any]]:
    """Esfera wireframe (3 círculos ortogonales) centrada en (cx, cy, cz)."""
    r = max(size * 0.5, 0.1)
    pairs: List[Tuple[Any, Any]] = []

    def ring(axis: str) -> List[Tuple[Any, Any]]:
        pts = []
        for i in range(segments + 1):
            a = 2 * math.pi * i / segments
            cos_a, sin_a = math.cos(a), math.sin(a)
            if axis == "Z":
                pts.append(_pt(cx + r * cos_a, cy + r * sin_a, cz))
            elif axis == "X":
                pts.append(_pt(cx, cy + r * cos_a, cz + r * sin_a))
            else:  # Y
                pts.append(_pt(cx + r * cos_a, cy, cz + r * sin_a))
        return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

    pairs += ring("Z")
    pairs += ring("X")
    pairs += ring("Y")
    return pairs


def _inst_type_to_label(inst_type: str) -> str:
    """Convierte el nombre completo de instalación al label corto para la leyenda."""
    return INST_TYPE_TO_LABEL.get(str(inst_type or "").strip().lower(), "")


def _make_text_elem(pos: Any, label: str, color_id: int, offset: float = 80.0) -> List[Any]:
    """Crea un TextElement junto al punto con el label de instalación."""
    if AllplanGeo is None or AllplanBasisElements is None or AllplanBaseElements is None:
        return []
    try:
        cx = float(getattr(pos, "X", 0.0))
        cy = float(getattr(pos, "Y", 0.0))

        text_prop = AllplanBasisElements.TextProperties()
        text_prop.Height = 1.0
        text_prop.Width  = 1.0

        common = AllplanBaseElements.CommonProperties()
        common.GetGlobalProperties()
        common.Color        = int(color_id)
        common.ColorByLayer = False

        insertion_pt = AllplanGeo.Point2D(cx + offset, cy + offset)
        return [AllplanBasisElements.TextElement(common, text_prop, label, insertion_pt)]
    except Exception as ex:
        print(f"[PointInput] Error creando leyenda texto: {ex}")
        return []


def _make_shape_elems_3d(pos: Any, tipo: str, prop: Any, size: float) -> List[Any]:
    """Como ``_make_shape_elems`` pero genera geometría 3D volumétrica."""
    if AllplanGeo is None or AllplanBasisElements is None:
        return []
    shape = _shape_for_role(tipo)
    cx = float(getattr(pos, "X", 0.0))
    cy = float(getattr(pos, "Y", 0.0))
    cz = float(getattr(pos, "Z", 0.0))
    pairs = _shape_pairs_3d(cx, cy, cz, shape, size)
    return [
        AllplanBasisElements.ModelElement3D(prop, AllplanGeo.Line3D(p1, p2))  # type: ignore[union-attr]
        for p1, p2 in pairs
    ]
