# -*- coding: utf-8 -*-
"""Electricidad polyline script — main entry point.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
- Página 2: Macros (SmartSymbol/Fixture) y Elementos Definidos
"""
from __future__ import annotations
from pathlib import Path

import importlib

import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Electricidad, SegmentItem, SegmentData
from Instalaciones.PolyLib.storage import PolylineStorage
from Instalaciones.PolyLib.installation_registry import get_pythonpart

from .utils.geo_handler import GeometryHandler
from .utils.segments import DynamicSegmentBuilder
from .rejiband_u_script import RejibandUScript
from .macros import macro_manager as _macro_manager_module
from .macros.macro_manager import ElectricidadMacroManager

from NemAll_Python_BaseElements import LayerService

# ---------------- CUSTOM ABSOLUTE ENUM PATH ----------------
project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(project_name, host_name)
if error != 0:
    base_path = AllplanSettings.AllplanPaths.GetCurPrjPath()

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Electricidad.profile()
profile.show.add_polilyne = False

INST_NAME = "ELECTRICIDAD"
# ---------------- DEFAULT CONFIG PARAMS ----------------
CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation=INST_NAME.upper(),
    parameters_show=profile.show,
    parameters_enabled=profile.enabled,
    num_td_path=base_path,

    limit_angles=False,
    allowed_angles=[],
    min_backtrack_deg=45,
    marker_manager_factory=lambda so, be: ElectricidadMacroManager(so, be),
)

# ------ MODULES LOADED FOR TEST ------
reload_module = [
    PBL,
    PBL_interactor,
    PBL_object,
    _macro_manager_module,
]


def check_allplan_version(_build_ele, _version):
    for module in reload_module:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"Error al recargar el módulo {module.__name__}: {e}")
    # Re-import ElectricidadMacroManager after reload so it picks up the latest code
    global ElectricidadMacroManager
    from .macros.macro_manager import ElectricidadMacroManager as _EMM
    ElectricidadMacroManager = _EMM
    return True

# ---- Mapa IS → TD: clave del script y color de sustitución ----
# Cuando distribution_type == "TD" o "EN", se usa el script TD equivalente.
# EN reutiliza los mismos scripts TD: la única diferencia es el layer asignado.
_TD_ELEMENT_MAP: dict[str, tuple[str, int]] = {
    "conducto_telecomunicaciones":             ("conducto_telecomunicaciones_td",             15),
    "conducto_luz_retorno_paralelas":          ("conducto_luz_retorno_paralelas_td",          13),
    "conducto_alimentacion_horno":             ("conducto_alimentacion_horno_td",             28),
    "conducto_alimentacion_luces_cajetines":   ("conducto_alimentacion_luces_cajetines_td",   16),
    "conducto_cajetin_a_enchufe":              ("conducto_cajetin_a_enchufe_td",              6),
    "conducto_interruptores_domotica":         ("conducto_interruptores_domotica_td",         27),
}
_EN_ELEMENT_MAP = _TD_ELEMENT_MAP   # misma geometría, distinto layer

_TD_COLOR_OUTER = 4     # recubrimiento exterior XPS
_TD_OUTER_OFFSET = 2.5  # mm: desplazamiento del recubrimiento hacia -Y (abajo en plano XY)

# IDs de atributos personalizados Allplan — fallback si GetAttributeID falla
_ATTR_PERSO_01_ID = 1083  # "Atributo personalizado 01" (numeración absoluta CC-{num})

# ---- Mapa de default_layers por tipo de distribución ----
_DEFAULT_LAYERS_BY_DISTRIBUTION: dict[str, dict] = {
    "IS": {
        "default": "IS_COR_ELECTRICITAT_FAB",
        "layer_polyline": "IS_COR_ELECTRICITAT_FAB",
    },
    "TD": {
        "default": "KN_ELECTRICITAT",
        "layer_polyline": "KN_ELECTRICITAT",
    },
    "EN_X": {
        "default": "KN_X_ELECTRICITAT",
        "layer_polyline": "KN_X_ELECTRICITAT",
    },
    "EN_Y": {
        "default": "KN_Y_ELECTRICITAT",
        "layer_polyline": "KN_Y_ELECTRICITAT",
    },
}


def _patch_create_group_pythonpart_for_td(script_object) -> None:
    """
    Monkey-patch de create_group_pythonpart para TD y EN.
    En IS, delega al original sin cambios.
    En TD/EN, separa elements_list por color antes de llamar al original dos veces:
    una para los tubos interiores y otra para el tubo exterior (color _TD_COLOR_OUTER=4),
    de forma que ambos queden como PythonParts independientes.
    """
    _original = script_object.create_group_pythonpart

    def _elem_color(e) -> int:
        try:
            return e.GetCommonProperties().Color
        except Exception:
            return -1

    def _td_aware_create_group(elements_list, build_ele):
        dist = getattr(script_object, "distribution_type", None)
        if dist not in ("TD", "EN"):
            return _original(elements_list, build_ele)

        inner_elems = [e for e in elements_list if _elem_color(e) != _TD_COLOR_OUTER]
        outer_elems = [e for e in elements_list if _elem_color(e) == _TD_COLOR_OUTER]

        result = []
        if inner_elems:
            result += _original(inner_elems, build_ele)
        if outer_elems:
            result += _original(outer_elems, build_ele)
        return result

    script_object.create_group_pythonpart = _td_aware_create_group


def _update_default_layers_for_distribution(
    so: PBL.script_object.PolylineScriptObject,
    distribution_type: str,
    face_en: str | None = None,
) -> None:
    """Actualiza default_layers según el tipo de distribución y, para EN, la cara seleccionada."""
    if distribution_type == "EN":
        key = "EN_Y" if face_en == "CARA Y" else "EN_X"
    else:
        key = distribution_type
    layers = _DEFAULT_LAYERS_BY_DISTRIBUTION.get(key)
    if layers:
        so.default_layers = layers
        if so.script_object_interactor:
            so.script_object_interactor.apply_layer_default()


def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )
    # HOOK: Creacion de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creacion de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    # PATCH: Wrap _generate_pythonparts to force segment rebuild before create
    _original_generate = script_object._generate_pythonparts

    def _synced_generate():
        print(f"[DBG-UNION] >>> _synced_generate START | inst_color={script_object.inst_color} | dist={script_object.distribution_type}")
        _sync_segments_before_create(script_object)
        print(f"[DBG-UNION] >>> after _sync_segments | inst_color={script_object.inst_color}")
        _original_generate()
        print(f"[DBG-UNION] >>> after _original_generate | inst_color={script_object.inst_color}")

    script_object._generate_pythonparts = _synced_generate

    # PATCH: Wrap modify_element_property to update default_layers when DistributionType changes
    _original_modify = script_object.modify_element_property

    def _patched_modify(name, value):
        result = _original_modify(name, value)
        if name == "DistributionType":
            _update_default_layers_for_distribution(
                script_object, value,
                face_en=getattr(script_object, "face_en", None),
            )
        elif name == "FaceEN":
            _update_default_layers_for_distribution(
                script_object, script_object.distribution_type, face_en=value, # type: ignore
            )
        return result

    script_object.modify_element_property = _patched_modify

    # PATCH: Para TD, create_group_pythonpart une cada color por separado
    _patch_create_group_pythonpart_for_td(script_object)

    # NOTE: Macro/element integration is now handled natively by PolyLib
    # via marker_manager_factory in CONFIG. No monkey-patches needed.

    return script_object


def _sync_segments_before_create(so: PBL.script_object.PolylineScriptObject):
    """Force-rebuild segment_groups and element_list from the current
    saved_paths state.  This ensures that manual cuts (which only update
    saved_paths without triggering a full rebuild) are reflected in the
    3D output."""
    interactor = getattr(so, "script_object_interactor", None)
    if not interactor:
        return
    try:
        interactor.get_segments()
        interactor._update_segment_groups()
        so._create_elements_preview()
    except Exception as ex:
        print(f"[SYNC] Error rebuilding segments before create: {ex}")
        import traceback
        traceback.print_exc()

def _rebuild_rejiband_segment(name: str, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> SegmentItem:
    """Crea un SegmentItem con datos geométricos recalculados desde dos puntos."""
    dx = float(b.X - a.X)
    dy = float(b.Y - a.Y)
    dz = float(b.Z - a.Z)
    len3 = math.sqrt(dx * dx + dy * dy + dz * dz)
    len_xy = math.sqrt(dx * dx + dy * dy)

    vec_n = AllplanGeo.Vector3D(dx, dy, dz)
    if len3 > 1e-9:
        vec_n.Normalize()

    # Ángulos necesarios para detección de esquinas y posicionamiento
    ang_xy = math.degrees(math.atan2(dy, dx)) if len_xy > 1e-9 else 0.0
    ang_z = math.degrees(math.atan2(dz, len_xy)) if len3 > 1e-9 else 0.0

    data = SegmentData(
        start=a,
        end=b,
        delta_x=dx,
        delta_y=dy,
        delta_z=dz,
        longitud_3d=len3,
        longitud_xy=len_xy,
        angulo_xy=ang_xy,
        angulo_z=ang_z,
        vector_normalizado=vec_n
    )
    return SegmentItem(name=name, view_mode="3D", data=data)

def _split_segments_by_max_len(segments: list[SegmentItem], max_len: float) -> list[SegmentItem]:
    """Divide segmentos largos en piezas de longitud comercial máxima."""
    if max_len <= 0.0:
        return list(segments)

    out: list[SegmentItem] = []
    for seg in segments:
        length = seg.data.longitud_3d
        if length <= max_len + 1e-6:
            out.append(seg)
            continue

        # Dirección del segmento
        v = seg.data.vector_normalizado
        if not v:
            out.append(seg)
            continue

        remaining = length
        p0 = seg.data.start
        piece_idx = 0
        while remaining > max_len + 1e-6:
            p1 = AllplanGeo.Point3D(
                p0.X + v.X * max_len,
                p0.Y + v.Y * max_len,
                p0.Z + v.Z * max_len
            )
            out.append(_rebuild_rejiband_segment(f"{seg.name}_p{piece_idx}", p0, p1))
            remaining -= max_len
            p0 = p1
            piece_idx += 1

        # Última pieza
        if remaining > 1e-6:
            out.append(_rebuild_rejiband_segment(f"{seg.name}_p{piece_idx}", p0, seg.data.end))

    return out

def _apply_corner_overlap_only(segs: list[SegmentItem], width: float) -> list[SegmentItem]:
    """Aplica solape dinámico en esquinas basado en el ancho de la bandeja."""
    if width <= 0.0 or len(segs) < 2:
        return list(segs)

    def extend_end(s: SegmentItem, d: float) -> SegmentItem:
        v = s.data.vector_normalizado
        if not v: return s
        b = s.data.end
        nb = AllplanGeo.Point3D(b.X + v.X * d, b.Y + v.Y * d, b.Z + v.Z * d)
        return _rebuild_rejiband_segment(s.name, s.data.start, nb)

    def extend_start(s: SegmentItem, d: float) -> SegmentItem:
        v = s.data.vector_normalizado
        if not v: return s
        a = s.data.start
        na = AllplanGeo.Point3D(a.X - v.X * d, a.Y - v.Y * d, a.Z - v.Z * d)
        return _rebuild_rejiband_segment(s.name, na, s.data.end)

    out = list(segs)
    for i in range(len(out) - 1):
        a1_xy = out[i].data.angulo_xy
        a2_xy = out[i + 1].data.angulo_xy
        a1_z = getattr(out[i].data, 'angulo_z', 0.0)
        a2_z = getattr(out[i + 1].data, 'angulo_z', 0.0)
        diff_xy = abs(a1_xy - a2_xy)
        diff_z = abs(a1_z - a2_z)
        diff = max(diff_xy, diff_z)

        if diff > 1e-3:
            rad_half = math.radians(diff) / 2.0
            ov = (width / 2.0) * math.tan(rad_half)

            out[i] = extend_end(out[i], ov)
            out[i + 1] = extend_start(out[i + 1], ov)
    return out

# ========================================
# UTILIDADES DE CORTE
# ========================================

_CUT_TOLERANCE_SQ = 1e-3 * 1e-3  # 0.001 mm squared

def _points_coincide(a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> bool:
    dx = a.X - b.X
    dy = a.Y - b.Y
    dz = a.Z - b.Z
    return (dx * dx + dy * dy + dz * dz) < _CUT_TOLERANCE_SQ


def _apply_vertex_cut_overlap(segs: list[SegmentItem], width: float,
                               so: 'PBL.script_object.PolylineScriptObject') -> list[SegmentItem]:
    """Aplica solape en extremos de grupo que coinciden con un corte en vértice.

    Cuando se corta en una esquina, los dos tramos quedan en grupos separados
    y ``_apply_corner_overlap_only`` no puede ver el segmento adyacente del
    otro grupo.  Esta función busca en ``saved_paths`` el path vecino que
    comparte el punto de corte y calcula el overlap necesario.
    """
    if width <= 0.0 or not segs:
        return list(segs)

    vertex_cuts = getattr(so, "saved_vertex_cut_points", [])
    if not vertex_cuts:
        return list(segs)

    saved_paths = getattr(so, "saved_paths", [])
    if not saved_paths:
        return list(segs)

    out = list(segs)

    def _calc_angle_xy(a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx = float(b.X - a.X)
        dy = float(b.Y - a.Y)
        length = math.sqrt(dx * dx + dy * dy)
        return math.degrees(math.atan2(dy, dx)) if length > 1e-9 else 0.0

    def _calc_angle_z(a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx = float(b.X - a.X)
        dy = float(b.Y - a.Y)
        dz = float(b.Z - a.Z)
        len_xy = math.sqrt(dx * dx + dy * dy)
        len3 = math.sqrt(dx * dx + dy * dy + dz * dz)
        return math.degrees(math.atan2(dz, len_xy)) if len3 > 1e-9 else 0.0

    def _extend_end(s: SegmentItem, d: float) -> SegmentItem:
        v = s.data.vector_normalizado
        if not v:
            return s
        b = s.data.end
        nb = AllplanGeo.Point3D(b.X + v.X * d, b.Y + v.Y * d, b.Z + v.Z * d)
        return _rebuild_rejiband_segment(s.name, s.data.start, nb)

    def _extend_start(s: SegmentItem, d: float) -> SegmentItem:
        v = s.data.vector_normalizado
        if not v:
            return s
        a = s.data.start
        na = AllplanGeo.Point3D(a.X - v.X * d, a.Y - v.Y * d, a.Z - v.Z * d)
        return _rebuild_rejiband_segment(s.name, na, s.data.end)

    # --- Comprobar extremo final del último segmento ---
    last_end = out[-1].data.end
    for vcp in vertex_cuts:
        if not _points_coincide(last_end, vcp):
            continue
        # Buscar el path que EMPIEZA en este punto de corte
        for path in saved_paths:
            if len(path) < 2:
                continue
            if not _points_coincide(path[0], vcp):
                continue
            # path[0]→path[1] es el primer segmento del grupo vecino
            adj_ang_xy = _calc_angle_xy(path[0], path[1])
            adj_ang_z = _calc_angle_z(path[0], path[1])
            my_ang_xy = out[-1].data.angulo_xy
            my_ang_z = getattr(out[-1].data, 'angulo_z', 0.0)
            diff = max(abs(my_ang_xy - adj_ang_xy), abs(my_ang_z - adj_ang_z))
            if diff > 1e-3:
                rad_half = math.radians(diff) / 2.0
                ov = (width / 2.0) * math.tan(rad_half)
                out[-1] = _extend_end(out[-1], ov)
            break

    # No extender el extremo inicial: solo el path que TERMINA en el
    # corte cubre la esquina, evitando solape y doble conteo de metros.

    return out


def _get_vertex_cut_adjacent_vectors(
    segments: list[SegmentItem],
    so: 'PBL.script_object.PolylineScriptObject'
) -> tuple[AllplanGeo.Vector3D | None, AllplanGeo.Vector3D | None]:
    """Devuelve (vec_start, vec_end): vectores de los segmentos adyacentes de
    otros paths cuando los extremos del grupo coinciden con un corte en vértice.

    - vec_start: vector del último segmento del path que TERMINA en el punto
      de inicio del grupo actual (para calcular extensión del primer elemento).
    - vec_end: vector del primer segmento del path que EMPIEZA en el punto
      final del grupo actual (para calcular extensión del último elemento).
    """
    vertex_cuts = getattr(so, "saved_vertex_cut_points", [])
    saved_paths = getattr(so, "saved_paths", [])
    if not vertex_cuts or not saved_paths or not segments:
        return None, None

    vec_start = None
    vec_end = None

    # --- Extremo inicial: buscar path que termina aquí ---
    first_start = segments[0].data.start
    for vcp in vertex_cuts:
        if not _points_coincide(first_start, vcp):
            continue
        for path in saved_paths:
            if len(path) < 2 or not _points_coincide(path[-1], vcp):
                continue
            dx = float(path[-1].X - path[-2].X)
            dy = float(path[-1].Y - path[-2].Y)
            dz = float(path[-1].Z - path[-2].Z)
            v = AllplanGeo.Vector3D(dx, dy, dz)
            v.Normalize()
            vec_start = v
            break
        break

    # --- Extremo final: buscar path que empieza aquí ---
    last_end = segments[-1].data.end
    for vcp in vertex_cuts:
        if not _points_coincide(last_end, vcp):
            continue
        for path in saved_paths:
            if len(path) < 2 or not _points_coincide(path[0], vcp):
                continue
            dx = float(path[1].X - path[0].X)
            dy = float(path[1].Y - path[0].Y)
            dz = float(path[1].Z - path[0].Z)
            v = AllplanGeo.Vector3D(dx, dy, dz)
            v.Normalize()
            vec_end = v
            break
        break

    return vec_start, vec_end


# ========================================
# HOOKS PERSONALIZADOS
# ========================================
def _create_elements_for_segment_group(segments, so: PBL.script_object.PolylineScriptObject):
    """
    Genera la geometría 3D de los elementos sin crear PythonParts.
    Devuelve una lista de elementos generados para un grupo de segmentos.
    """
    base_color = 0
    diameter = 0
    _model_conduct = None
    element_type_core = None
    elements_generated = []

    builder = DynamicSegmentBuilder()
    geo_handler = GeometryHandler()

    model_base = so.current_inst_config

    if model_base:
        element_type_core = model_base["key"]
        base_color = model_base["color"]
        diameter = model_base["diameter"]

    is_rejiband = "rejiband" in str(element_type_core).lower()

    # ------------------------------------------------------------------
    # TD / EN: redirigir al script TD equivalente si existe en el mapa.
    # EN reutiliza los mismos scripts TD; solo difiere el layer asignado.
    # ------------------------------------------------------------------
    _dist = getattr(so, "distribution_type", None)
    if not is_rejiband and _dist in ("TD", "EN"):
        _elem_map = _TD_ELEMENT_MAP if _dist == "TD" else _EN_ELEMENT_MAP
        td_key, td_inst_color = _elem_map.get(element_type_core, (None, None)) # type: ignore
        if td_key:
            element_type_core = td_key
            base_color = None                   # preserva colores por elemento (inner/outer)
            so.inst_color = td_inst_color       # alinea base_c para MakeUnion en create_group_pythonpart
            so.element_type_core = td_key       # alinea el filtro de _create_grouped_pythonparts
            print(f"[DBG-UNION] {_dist} remap → key={element_type_core} | base_color={base_color} | so.inst_color={so.inst_color} | so.element_type_core={so.element_type_core}")

    selected_inst = [
        item for item in so.pythonparts_modules
        if item.key == element_type_core
    ]

    # ------------------------------------------------------------------
    # Detectar extremos que coinciden con puntos de corte manual
    # ------------------------------------------------------------------
    cut_pts = getattr(so, "saved_cut_points", [])
    has_cut_start = bool(
        segments and cut_pts
        and any(_points_coincide(segments[0].data.start, cp) for cp in cut_pts)
    )
    has_cut_end = bool(
        segments and cut_pts
        and any(_points_coincide(segments[-1].data.end, cp) for cp in cut_pts)
    )

    # ------------------------------------------------------------------
    # CASO A: Rejiband U (Geometría exacta por segmento)
    # ------------------------------------------------------------------
    if model_base and is_rejiband:
        max_len = 3000.0

        # Particionado comercial y solape dinámico en esquinas
        segs_rej = _split_segments_by_max_len(segments, max_len)
        segs_rej = _apply_corner_overlap_only(segs_rej, width=diameter)
        # Solo extiende el extremo final (no el inicio) para evitar solape
        segs_rej = _apply_vertex_cut_overlap(segs_rej, width=diameter, so=so)

        segment_group_parse = []
        n = len(segs_rej)
        for j, seg in enumerate(segs_rej):
            inst = RejibandUScript(so.build_ele, so)
            result = inst.execute(diameter=diameter, length=seg.data.longitud_3d)
            segment_group_parse.append({
                "type": element_type_core,
                "element3d": result.elements,
                "segment": seg,
                "metadata": {
                    "is_main": True,
                    "path_segment_index": j,
                    "is_cut_start": has_cut_start and j == 0,
                    "is_cut_end": has_cut_end and j == n - 1,
                }
            })

        elements_generated = geo_handler.center_and_connect_models(
            data_list=segment_group_parse,
            conducto_width=diameter,
            color=base_color,
            reference_orientation_angle=getattr(so, 'reference_orientation_angle', None),
            debug=True
        )

    # ------------------------------------------------------------------
    # CASO B: Conductos Normales / Aislados (Template + DynamicBuilder)
    # ------------------------------------------------------------------
    elif model_base:
        _model_conduct = so._get_pythonpart_installed(
            element_key=selected_inst[0].key,
            exec_args=(diameter,),
            attr_kwargs={"value": diameter}
        )

        segment_group_parse = builder.create_segment_group(
            segments,
            _model_conduct,
            element_type_core,
        )

        # adj_vec_end: el tubo que TERMINA en el corte se extiende +W/2
        # adj_vec_start: el tubo que COMIENZA en el corte se retrae -W/2 (sin solape)
        adj_vec_start, adj_vec_end = _get_vertex_cut_adjacent_vectors(segments, so)

        elements_generated = geo_handler.center_and_connect_models(
            data_list=segment_group_parse,
            conducto_width=diameter,
            color=base_color,
            reference_orientation_angle=getattr(so, 'reference_orientation_angle', None),
            adj_vec_start=adj_vec_start,
            adj_vec_end=adj_vec_end,
            debug=True
        )

    # TD: desplazar tubo exterior en la dirección del "height axis" del cubo tras rotación.
    # geo_handler centra cada elemento por su propio centroide: el exterior (25mm) queda
    # ±12.5mm y el interior (20mm) queda ±10mm → 2.5mm en cada lado.
    # Movemos el exterior _TD_OUTER_OFFSET mm en la dirección H para que el solape
    # quede todo en un lado (abajo en plano XY según orientación del segmento).
    if not is_rejiband and getattr(so, "distribution_type", None) in ("TD", "EN") and elements_generated:
        _hx, _hy, _hz = 0.0, -1.0, 0.0  # fallback: vertical rot_xy=90°
        try:
            if segments:
                _sdata = segments[0].data
                _ang_rad = math.radians(float(getattr(_sdata, 'angulo_xy', 90.0)))
                _len_xy  = float(getattr(_sdata, 'longitud_xy', 0.0))
                _dz      = float(getattr(_sdata, 'delta_z', 1.0))
                _pitch   = math.atan2(_dz, _len_xy if abs(_len_xy) > 1e-6 else 1e-6)
                _hx = -math.cos(_ang_rad) * math.sin(_pitch)
                _hy = -math.sin(_ang_rad) * math.sin(_pitch)
                _hz =  math.cos(_pitch)
        except Exception as _ex:
            print(f"[DBG-TD] Error calculando H direction: {_ex}")

        _offset_vec = AllplanGeo.Vector3D(
            _hx * _TD_OUTER_OFFSET,
            _hy * _TD_OUTER_OFFSET,
            _hz * _TD_OUTER_OFFSET,
        )
        print(f"[DBG-TD] offset_vec=({_hx*_TD_OUTER_OFFSET:.2f}, {_hy*_TD_OUTER_OFFSET:.2f}, {_hz*_TD_OUTER_OFFSET:.2f})")
        adjusted = []
        for item in elements_generated:
            elem = item.get("element")
            try:
                if elem is not None and elem.GetCommonProperties().Color == _TD_COLOR_OUTER:
                    new_brep = AllplanGeo.Move(elem.GetGeometryObject(), _offset_vec)
                    item = {**item, "element": AllplanBasisElements.ModelElement3D(
                        elem.GetCommonProperties(), new_brep
                    )}
            except Exception as _ex:
                print(f"[DBG-TD] Error aplicando offset: {_ex}")
            adjusted.append(item)
        elements_generated = adjusted

    return elements_generated

# Coincide con TIPOS_ACCESORIOS en geo_handler.center_and_connect_models
_GEO_TIPOS_ACCESORIOS = frozenset({"manguito", "codo_45", "codo_90", "conexion", "difusor"})


def _is_geo_accessory_element_type(element_type: str | None) -> bool:
    """True si la pieza es manguito/codo/conexión (no un tramo de conducto principal)."""
    et = element_type or ""
    return et in _GEO_TIPOS_ACCESORIOS


def _layer_and_attr_storage_keys(
    path_idx: int, element_type: str | None, ui_segment_index: int
) -> tuple[str, str | None]:
    """
    Igual que Ventilación: clave seg_{path}_elem_{N} con N = path_segment_index
    (metadata en segments + índice en geo). Accesorio: capa según tramo i del vértice;
    atributos de paleta solo en conductos (attr None).
    """
    sk = f"seg_{path_idx}_elem_{ui_segment_index}"
    if _is_geo_accessory_element_type(element_type):
        return sk, None
    return sk, sk


def _find_cut_sibling_number(path_idx: int, so: 'PBL.script_object.PolylineScriptObject') -> int | None:
    """
    Devuelve el CC number de un path hermano si path_idx es un corte del mismo tubo.
    Un path es corte si comparte un punto de corte explícito (saved_cut_points /
    saved_vertex_cut_points) con otro path que ya tiene CC asignado.
    Devuelve None para paths independientes → deben recibir número nuevo.
    """
    cut_pts = (
        list(getattr(so, 'saved_cut_points', []))
        + list(getattr(so, 'saved_vertex_cut_points', []))
    )
    if not cut_pts:
        return None

    saved_paths = getattr(so, 'saved_paths', [])
    if path_idx >= len(saved_paths):
        return None

    current_path = saved_paths[path_idx]
    if not current_path:
        return None

    current_start = current_path[0]
    current_end   = current_path[-1]

    for cp in cut_pts:
        if not (_points_coincide(current_start, cp) or _points_coincide(current_end, cp)):
            continue
        for sibling_idx, sibling_num in so.cc_path_numbers.items():
            if sibling_idx == path_idx or sibling_idx >= len(saved_paths):
                continue
            sibling_path = saved_paths[sibling_idx]
            if sibling_path and (
                _points_coincide(sibling_path[0], cp)
                or _points_coincide(sibling_path[-1], cp)
            ):
                return sibling_num

    return None


def _create_elements_with_layers_attrs(elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject) -> list:
    """
    Hook final: aplica layers y atributos técnicos + nombre de usuario a cada elemento generado.
    """
    if so._config and not so.init_storage:
        inst_name = str(so._config.default_installation).lower()
        from Instalaciones.PolyLib.storage import PolylineStorage
        so.init_storage = PolylineStorage(name=inst_name)
        so.init_storage.base_path = so._config.num_td_path

    # Datos del tipo de instalación activo (comunes a todos los elementos del path)
    cfg = so.current_inst_config or {}
    element_key  = cfg.get("key", "")
    diameter     = float(cfg.get("diameter", 0))
    color        = int(cfg.get("color", 0))
    overlap_mm   = float(cfg.get("overlap_mm", 0.0))

    # Prefijo y clave de contador: REJ para rejiband, CC para el resto.
    _num_key = "REJ" if "rejiband" in str(element_key).lower() else "CC"

    # Numeración absoluta: UN número por path, contador global compartido entre tipos.
    # Todos los paths de un mismo tubo (incluyendo cortes) comparten el mismo número.
    # Si el path ya tiene un número asignado (modo edición o propagación del split), se reutiliza.
    path_num = 0
    if so.init_storage:
        if not hasattr(so, "cc_path_numbers"):
            so.cc_path_numbers = {}
        cc_before = dict(so.cc_path_numbers)
        if path_idx in so.cc_path_numbers:
            path_num = so.cc_path_numbers[path_idx]
            print(f"[CC-DBG] ASIGNACION | path_idx={path_idx} | REUSAR cc_path_numbers existente → path_num={path_num} | cc={cc_before}")
        else:
            # Solo hereda si este path es un CORTE de otro (comparten punto de corte explícito).
            # Paths independientes dibujados en la misma sesión NO deben heredar.
            cut_sibling_num = _find_cut_sibling_number(path_idx, so)
            if cut_sibling_num is not None:
                path_num = cut_sibling_num
                print(f"[CC-DBG] ASIGNACION | path_idx={path_idx} | HEREDAR de corte hermano → path_num={path_num} | cc={cc_before}")
            else:
                path_num = so.init_storage._get_next_number(_num_key)
                print(f"[CC-DBG] ASIGNACION | path_idx={path_idx} | NUEVO numero de archivo ({_num_key}) → path_num={path_num} | cc={cc_before}")
            so.cc_path_numbers[path_idx] = path_num
    else:
        print(f"[CC-DBG] ASIGNACION | path_idx={path_idx} | init_storage=None → path_num=0 (no se escribe attr01)")

    doc = so.coord_input.GetInputViewDocument()

    print(f"[DBG-UNION] _create_elements_with_layers_attrs START | path_idx={path_idx} | so.inst_color={so.inst_color} | dist={so.distribution_type}")

    elements_generated_final = []

    for i, element in enumerate(elements_generated):
        element_model = element.element
        etype = getattr(element, "element_type", None)
        try:
            _dbg_color = element_model.GetCommonProperties().Color
        except Exception:
            _dbg_color = "?"
        print(f"[DBG-UNION]   elem[{i}] type={etype} | color_on_model={_dbg_color}")
        ui_seg = int(getattr(element, "index", i))
        layer_storage_key, attr_storage_key = _layer_and_attr_storage_keys(
            path_idx, etype, ui_seg
        )

        # 1. Layer (clave alineada con tubos de la vista previa)
        # Para TD/EN: tubo externo (color _TD_COLOR_OUTER) → siempre KN_XPS_RECESS
        #             tubo interno → layer normal (KN_ELECTRICITAT / KN_X/Y_ELECTRICITAT)
        _dist = getattr(so, "distribution_type", "IS")
        try:
            _elem_color = element_model.GetCommonProperties().Color
        except Exception:
            _elem_color = None
        if _dist in ("TD", "EN") and _elem_color == _TD_COLOR_OUTER:
            _xps_id = LayerService.GetIDByShortName("KN_XPS_RECESS", doc)
            if _xps_id:
                try:
                    _props = element_model.CommonProperties
                    _props.Layer = _xps_id
                    element_model.CommonProperties = _props
                except Exception as _e:
                    print(f"[Error] Fallo al setear KN_XPS_RECESS: {_e}")
        elif "rejiband" in str(etype or "").lower():
            _rej_id = LayerService.GetIDByShortName("IS_REJIBANDS", doc)
            if _rej_id:
                try:
                    _props = element_model.CommonProperties
                    _props.Layer = _rej_id
                    element_model.CommonProperties = _props
                except Exception as _e:
                    print(f"[Error] Fallo al setear IS_REJIBANDS: {_e}")
        else:
            element_model = _apply_layer_to_element(element_model, layer_storage_key, so)

        # 2. Tipo derivado del layer (para attr04)
        layer_key = _get_element_layer_key(layer_storage_key, so)
        # tipo del layer (para uso futuro; ya no se pasa a get_attributes)
        _get_tipo_from_layer(layer_key)

        # 1. Obtener la clase desde el registry e instanciarla (sin generar el 3D)
        element_key = getattr(element, 'element_type', None) or so.current_inst_config.get("key", "")
        diameter = so.current_inst_config.get("diameter", 0)
        color = so.current_inst_config.get("color", 0)

        script_class = get_pythonpart(element_key)

        raw_attrs = []
        if script_class:
            script_inst = script_class(so.build_ele, so)
            # tipo=None: attr04 no se genera desde el layer; overlap_mm=0.0: attr10 no se genera en scripts
            raw_attrs = script_inst.get_attributes(value=diameter, tipo=None, color=color, overlap_mm=0.0)

        # 2. Post-proceso de raw_attrs para cumplir valores esperados por la biblioteca:
        #    - attr01 = "{prefix}-{num}" (CC- para conductos, REJ- para rejiband)
        #    - attr04 = pmp_tipus_cablejat (tipo de cable/tubo, no descripción del layer)
        #    - attr07, attr09 = enteros sin decimales
        #    - attr10 = siempre 0 (valor calculado pendiente)
        elem_num = path_num if not _is_geo_accessory_element_type(etype) else 0
        codificacion = so.applied_codificacion.get(attr_storage_key, "") if attr_storage_key else ""
        raw_attrs = _fix_numeric_and_attr04(doc, raw_attrs, num=elem_num, codificacion=codificacion, prefix=_num_key)

        # 3. Atributos de UI solo en tramos principales (misma clave que al aplicar desde marco)
        elem_attrs = so.applied_attributes.get(attr_storage_key, []) if attr_storage_key else []

        # 4. Fusión en orden de prioridad: Base <- Usuario (UI)
        final_attrs = _merge_attributes(raw_attrs, elem_attrs)

        # 7. Aplicar al modelo
        if final_attrs:
            element_model = _apply_attributes_to_model_elem(element_model, final_attrs) or element_model

        element.element = element_model
        elements_generated_final.append(element)

        # --- Polilínea continua: popular _polyline_attrs ---
        is_core = not _is_geo_accessory_element_type(etype)

        if is_core:
            pt_idx = sum(
                1 for j in range(i)
                if not _is_geo_accessory_element_type(
                    getattr(elements_generated[j], "element_type", None)
                )
            )

            is_first_in_path = (i == 0)
            is_first_after_accessory = (
                i > 0 and _is_geo_accessory_element_type(
                    getattr(elements_generated[i - 1], "element_type", None)
                )
            )

            if is_first_in_path or is_first_after_accessory:
                if so._polyline_attrs is None:
                    so._polyline_attrs = {}
                if path_idx not in so._polyline_attrs:
                    so._polyline_attrs[path_idx] = {}
                if pt_idx not in so._polyline_attrs[path_idx]:
                    so._polyline_attrs[path_idx][pt_idx] = final_attrs

    if so.init_storage:
        so.init_storage._save_numbering_file()

    return elements_generated_final


# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================

# ---- Mapa layer → valor de "Atributo personalizado 04" ----
_LAYER_TIPO_MAP: dict[str, str] = {
    "IS_COR_TELECOS_FAB":          "TELECOS SOBRE REJIBAND",
    "IS_COR_TELECOS_IN":           "TELECOS D'ENTRADA",
    "IS_COR_TELECOS_OUT":          "TELECOS DE SORTIDA",
    "IS_COR_ELECTRICITAT_FAB":     "CORRUGATS SOBRE REJIBAND",
    "IS_COR_ELECTRICITAT_FAB_IN":  "CORRUGATS D'ENTRADA",
    "IS_COR_ELECTRICITAT_FAB_OUT": "CORRUGATS DE SORTIDA",
}


def _get_tipo_from_layer(layer_key: str) -> str | None:
    """Traduce el short name de un layer al valor del Atributo personalizado 04 (Tipo)."""
    return _LAYER_TIPO_MAP.get(layer_key)


def _get_element_layer_key(storage_key: str, so: PBL.script_object.PolylineScriptObject) -> str:
    """Devuelve el short name del layer asignado a un storage_key.
    Prioridad: applied_layers (usuario) > default (global en default_layers)."""
    if hasattr(so, "applied_layers") and so.applied_layers:
        layer_data = so.applied_layers.get(storage_key)
        if layer_data and isinstance(layer_data, dict):
            layer_name = layer_data.get("layer", "")
            if layer_name:
                return layer_name
    if so.default_layers:
        d = so.default_layers.get("default", "")
        if d:
            return str(d)
    return ""


def _build_attr01(doc, user_value: str, element_key: str) -> list:
    """
    Construye el Atributo personalizado 01 (Nombre) con las reglas de negocio:
      - Telecos / Corrugados: el valor siempre termina en ;0
      - Rejiband: sin restricción de sufijo
    Devuelve lista vacía si no hay nombre de usuario.
    """
    if not user_value:
        return []
    try:
        attr_id = 1083
        if not attr_id or attr_id <= 0:
            return []
        if element_key != "rejiband_u":
            if not user_value.endswith(";0"):
                user_value = user_value.rstrip(";") + ";0"
        return [AllplanBaseElements.AttributeString(attr_id, user_value)]
    except Exception as e:
        print(f"[ATTR01] Error construyendo attr01: {e}")
        return []


def _merge_attributes(base_attrs: list, override_attrs: list) -> list:
    """
    Fusiona dos listas de atributos de Allplan.
    Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.

    Args:
        base_attrs: Lista base de atributos (AttributeString, AttributeDouble, etc.)
        override_attrs: Lista de atributos que sobrescriben los base

    Returns:
        Lista fusionada de atributos sin duplicados por ID

    Example:
        base = [AttributeString(Id: 55015, Value: "IS08"),
                AttributeString(Id: 55010, Value: "")]
        override = [AttributeString(Id: 55015, Value: "testtt00009")]

        result = _merge_attributes(base, override)
        # result tendrá Id 55015 con valor "testtt00009" y Id 55010 con valor ""
    """
    # Diccionario para rastrear atributos por ID
    # Clave: ID del atributo, Valor: objeto de atributo completo
    attr_dict = {}

    # 1. Primero agregar todos los atributos base
    for attr in base_attrs:
        attr_dict[attr.Id] = attr

    # 2. Sobrescribir/agregar con los atributos de override
    for attr in override_attrs:
        attr_dict[attr.Id] = attr

    # 3. Convertir el diccionario de vuelta a lista
    # Ordenar por ID para mantener consistencia (opcional)
    merged_list = [attr_dict[key] for key in sorted(attr_dict.keys())]

    return merged_list

def _process_auto_numbering(
    attribute_list: list,
    inst_type: str,
    so: PBL.script_object.PolylineScriptObject,
    forced_number: int | None = None
) -> tuple[list, bool]:
    if not attribute_list:
        return attribute_list, False

    new_attr_list = []
    modified = False
    target_id = 1083

    for attr in attribute_list:
        if hasattr(attr, "Id") and attr.Id == target_id:
            # SIEMPRE generamos el valor si hay un forced_number,
            # o si el valor es exactamente "TV" (semilla inicial)
            if forced_number is not None:
                new_value = f"TV-{forced_number}"
                new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
                modified = True
                continue
            elif attr.Value == "TV":
                # Caso de rescate: si no hay forced_number pero detectamos la semilla
                if so.init_storage:
                    num = so.init_storage._get_next_number(inst_type)
                    so.init_storage._save_numbering_file()
                    new_value = f"TV-{num}"
                    new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
                    modified = True
                    continue

        new_attr_list.append(attr)

    return new_attr_list, modified

def _extract_number_from_attrs(attribute_list: list) -> int | None:
    """
    Extrae el número entero del atributo 1083 (formato 'TV-X').
    """
    if not attribute_list:
        return None

    target_id = 1083
    prefix = "TV-"

    for attr in attribute_list:
        try:
            # Verificamos si es el atributo correcto
            if hasattr(attr, "Id") and attr.Id == target_id:
                val_str = str(attr.Value)

                # Si el valor ya tiene el formato "TV-5", extraemos el 5
                if prefix in val_str:
                    num_part = val_str.replace(prefix, "").strip()
                    if num_part.isdigit():
                        return int(num_part)

                # Si por alguna razón solo está el número como string
                elif val_str.isdigit():
                    return int(val_str)

        except Exception as e:
            print(f"[EXTRACT] Error procesando atributo: {e}")
            continue

    return None

def _fix_numeric_and_attr04(doc, raw_attrs: list, num: int = 0, codificacion: str = "", prefix: str = "CC") -> list:
    """
    Post-procesa raw_attrs:
      - Escribe attr01 = "{prefix}-{num}" (CC- para conductos, REJ- para rejiband).
        Si num == 0, no escribe attr01.
      - Extrae pmp_tipus_cablejat y lo escribe como Atributo personalizado 04.
      - Convierte pmp_diametre y pmp_area a AttributeString (sin decimales).
    Los attrs 07, 09, 10 ya se generan como AttributeInteger directamente en cada script.
    IDs hardcodeados (no GetAttributeID por nombre): attr01=1083, attr04=1086.
    """
    id_attr01 = 1083  # Custom attribute 01
    id_attr04 = 1086  # Custom attribute 04
    try:
        id_tc   = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_tipus_cablejat")
        id_diam = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_diametre")
        id_area = AllplanBaseElements.AttributeService.GetAttributeID(doc, "pmp_area")
    except Exception:
        id_tc   = None
        id_diam = None
        id_area = None

    tipo_cablejat = ""
    result = []
    for attr in raw_attrs:
        attr_id = getattr(attr, "Id", None)
        if id_tc and attr_id == id_tc:
            tipo_cablejat = str(attr.Value)
            result.append(attr)
        elif id_diam and attr_id == id_diam:
            result.append(AllplanBaseElements.AttributeString(id_diam, str(int(float(attr.Value)))))
        elif id_area and attr_id == id_area:
            result.append(AllplanBaseElements.AttributeString(id_area, str(int(float(attr.Value)))))
        else:
            result.append(attr)

    print(f"[DBG-CC] _fix_numeric_and_attr04 | num={num} | prefix={prefix} | tipo_cablejat={tipo_cablejat!r}")
    if num > 0:
        attr01_val = f"{prefix}-{num}:{codificacion}" if codificacion else f"{prefix}-{num}"
        print(f"[DBG-CC] escribiendo attr01={attr01_val!r}")
        result.append(AllplanBaseElements.AttributeString(id_attr01, attr01_val))

    if tipo_cablejat:
        result.append(AllplanBaseElements.AttributeString(id_attr04, tipo_cablejat))

    return result


def _apply_attributes_to_model_elem(model_elem, attr_list):
        """
        Empaqueta y aplica una lista de atributos a un elemento 3D de Allplan
        usando la estructura AttributeSet -> Attributes.
        """
        if not attr_list:
            return
        try:
            attr_set_list = []
            # Creamos el set de atributos
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            # Creamos el objeto Attributes contenedor
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            # Aplicamos al elemento
            model_elem.SetAttributes(attributes)
            return model_elem
        except Exception as e:
            print(f"[Error] Al aplicar atributos: {e}")

# ========================================
# APLICACIÓN DE LAYERS
# ========================================
def _apply_layer_to_element(model_elem: AllplanBasisElements.ModelElement3D,
                            key_layer: str,
                            so: PBL.script_object.PolylineScriptObject) -> AllplanBasisElements.ModelElement3D:
        """
        Responsabilidad única: Buscar el ID del layer y aplicarlo al elemento.
        """
        layer_id = _get_layer_id(key_layer, so)
        if layer_id:
            try:
                props = model_elem.CommonProperties
                props.Layer = layer_id
                model_elem.CommonProperties = props
            except Exception as e:
                print(f"[Error] Fallo al setear layer en {key_layer}: {e}")
                pass
        else:
            print(f"[Warn] No se pudo determinar un ID de Layer válido para {key_layer}")

        return model_elem

def _get_layer_id(key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject):
        """
        Obtiene el ID del layer apropiado para un elemento.
        Para EN, resuelve automáticamente KN_X_ELECTRICITAT o KN_Y_ELECTRICITAT según face_en.
        Prioriza layers específicos guardados sobre el layer por defecto.
        """
        doc = so.coord_input.GetInputViewDocument()
        layer_id = 0

        # Para EN, el default_layers ya fue actualizado según face_en en _update_default_layers_for_distribution.
        # Si por algún motivo no está sincronizado, lo resolvemos aquí directamente.
        if getattr(so, "distribution_type", None) == "EN":
            face = getattr(so, "face_en", None)
            en_layer = "KN_Y_ELECTRICITAT" if face == "CARA Y" else "KN_X_ELECTRICITAT"
            en_id = LayerService.GetIDByShortName(en_layer, doc)  # type: ignore
            if en_id:
                layer_id = en_id
        elif so.default_layers:
            default_id = LayerService.GetIDByShortName(so.default_layers.get("default", ""), doc)  # type: ignore
            if default_id:
                layer_id = default_id

        if hasattr(so, "applied_layers") and so.applied_layers:
            layer_data = so.applied_layers.get(key_applied_layer_attr, None)
            if layer_data and isinstance(layer_data, dict):
                layer_name_str = layer_data.get("layer")
                if layer_name_str:
                    specific_id = LayerService.GetIDByShortName(layer_name_str, doc)  # type: ignore
                    if specific_id:
                        layer_id = specific_id
        return layer_id

