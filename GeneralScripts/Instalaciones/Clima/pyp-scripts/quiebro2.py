"""
Quiebro tipo S — figura 2D en XY (senda Y) extruida en Z (altura de sección).

Croquis Nemetschek — hendidura en los extremos (**altura** de sección reducida en Z):

- **Ancho** del casetón en planta XY: **0,200 m** en tramos rectos y oblicuo (mitad ±100 mm).
- **Largo** del tramo hendido a cada extremo: **0,025 m** en Y.
- En esos tramos la **altura** del perfil extruido (Z) es **0,199 m**; el tramo central
  usa **Q2_ExtrudeZ_mm** (p. ej. **0,200 m**). La diferencia forma el escalón visible
  en vista lateral (XZ), no un estrechamiento en X.

Depuración: variable de entorno Q2_LOG=1; mensajes [quiebro2] en stderr.
"""
from __future__ import annotations

import logging
import math
import os
import sys

import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

_LOG = logging.getLogger(__name__)
ARROW_COLOR_BY_TYPE = {
    "Retorn": 65,
    "Impulsió": 8,
}

_Q2_PARAM_NAMES = (
    "Q2_Type",
    "Q2_DiameterRetorn",
    "Q2_DiameterImpulsio",
    "Q2_GrooveLen_mm",
    "Q2_GrooveWidth_mm",
    "Q2_StraightLen_mm",
    "Q2_MainWidth_mm",
    "Q2_SlantEdgeLen_mm",
    "Q2_InclinationFromHorizontal_deg",
    "Q2_AngleFromVertical_deg",
    "Q2_ExtrudeZ_mm",
    "Q2_Color",
)


def _env_log_enabled() -> bool:
    return os.environ.get("Q2_LOG", "").strip() in ("1", "true", "True", "yes", "YES")


def _ensure_stderr_handler() -> None:
    if _LOG.handlers:
        return
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter("[quiebro2] %(levelname)s %(message)s"))
    _LOG.addHandler(h)
    _LOG.setLevel(logging.DEBUG)
    _LOG.propagate = False


def _console(msg: str) -> None:
    print(f"[quiebro2] {msg}", file=sys.stderr, flush=True)


def _log_palette_snapshot(build_ele) -> None:
    lines = []
    for name in _Q2_PARAM_NAMES:
        raw = getattr(build_ele, name, None)
        if raw is None:
            lines.append(f"  {name}: <no en paleta → default>")
        else:
            val = getattr(raw, "value", raw)
            lines.append(f"  {name}: {val!r}")
    text = "Paleta Q2_*:\n" + "\n".join(lines)
    _LOG.debug(text)
    if _env_log_enabled():
        _console(text)


def _log_polylines(tag: str, groups: list[tuple[str, list]]) -> None:
    _LOG.info("%s", tag)
    for label, pts in groups:
        _LOG.info("  %s: %d vértices", label, len(pts))
        for i, pt in enumerate(pts):
            _LOG.debug("    %s %02d: (%.6g, %.6g) mm", label, i, pt.X, pt.Y)


def check_allplan_version(_build_ele, _version) -> bool:
    return True


def _param_float(build_ele, name: str, default: float) -> float:
    raw = getattr(build_ele, name, None)
    if raw is None:
        return default
    val = getattr(raw, "value", raw)
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _param_int(build_ele, name: str, default: int) -> int:
    raw = getattr(build_ele, name, None)
    if raw is None:
        return default
    val = getattr(raw, "value", raw)
    try:
        return int(round(float(val)))
    except (TypeError, ValueError):
        return default


def _diameter_main_width_mm(diameter_key: str | None) -> float | None:
    """
    Extrae el ancho principal de una clave de sección tipo '350x150' -> 350.0.
    """
    if not diameter_key:
        return None
    try:
        return float(str(diameter_key).split("x", 1)[0].strip())
    except (TypeError, ValueError):
        return None


def _normalize_q2_type(raw_value: str | None) -> str:
    text = str(raw_value or "").strip().lower()
    text = (
        text.replace("á", "a")
        .replace("à", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("í", "i")
        .replace("ï", "i")
        .replace("ó", "o")
        .replace("ò", "o")
        .replace("ú", "u")
        .replace("ü", "u")
    )
    if "impuls" in text:
        return "Impulsió"
    return "Retorn"


def _read_angle_from_vertical_deg(build_ele) -> tuple[float, float]:
    """
    Devuelve (ángulo respecto a la vertical en grados, inclinación respecto a la horizontal).

    Prioridad: ``Q2_InclinationFromHorizontal_deg`` en [45, 90] (90 = vertical;
    45 = pendiente máxima del rango). Si no existe, se usa ``Q2_AngleFromVertical_deg``
    en [0, 45] (paletas antiguas).
    """
    raw_inc = getattr(build_ele, "Q2_InclinationFromHorizontal_deg", None)
    if raw_inc is not None:
        beta = float(getattr(raw_inc, "value", raw_inc))
        beta = max(45.0, min(90.0, beta))
        alpha = 90.0 - beta
        return alpha, beta
    av = _param_float(build_ele, "Q2_AngleFromVertical_deg", 15.0)
    av = max(0.0, min(45.0, av))
    return av, 90.0 - av


def _slant_dims_mm(
    groove_len_mm: float,
    straight_len_mm: float,
    main_width_mm: float,
    slant_edge_len_mm: float,
    angle_from_vertical_deg: float,
) -> dict:
    gl = groove_len_mm
    sl = straight_len_mm
    mh = main_width_mm
    L = slant_edge_len_mm
    theta = math.radians(angle_from_vertical_deg)
    dx = L * math.sin(theta)
    dy = L * math.cos(theta)
    half_m = mh * 0.5
    y0 = gl + sl
    y_slant_top = y0 + dy
    y_after_upper_straight = y_slant_top + sl
    y_max = y_after_upper_straight + gl
    return {
        "dx": dx,
        "dy": dy,
        "half_m": half_m,
        "gl": gl,
        "y0": y0,
        "y_slant_top": y_slant_top,
        "y_after_upper_straight": y_after_upper_straight,
        "y_max": y_max,
    }


def build_middle_outline_mm(
    groove_len_mm: float,
    straight_len_mm: float,
    main_width_mm: float,
    slant_edge_len_mm: float,
    angle_from_vertical_deg: float,
) -> list[AllplanGeometry.Point2D]:
    """
    Perfil del tramo central (sin los 25 mm extremos): ancho constante mh en planta.
    CCW en XY.
    """
    d = _slant_dims_mm(
        groove_len_mm,
        straight_len_mm,
        main_width_mm,
        slant_edge_len_mm,
        angle_from_vertical_deg,
    )
    hm = d["half_m"]
    gl = d["gl"]
    y0 = d["y0"]
    dx = d["dx"]
    yst = d["y_slant_top"]
    yaf = d["y_after_upper_straight"]

    pts: list[tuple[float, float]] = [
        (hm, gl),
        (hm, y0),
        (hm + dx, yst),
        (hm + dx, yaf),
        (-hm + dx, yaf),
        (-hm + dx, yst),
        (-hm, y0),
        (-hm, gl),
    ]
    return [AllplanGeometry.Point2D(x, y) for x, y in pts]


def build_groove_bottom_rect_mm(
    groove_len_mm: float,
    main_width_mm: float,
) -> list[AllplanGeometry.Point2D]:
    """Rectángulo Y∈[0, gl], X ancho completo mh (hendidura ancho 0,200 m)."""
    hm = main_width_mm * 0.5
    gl = groove_len_mm
    pts = [
        (-hm, 0.0),
        (hm, 0.0),
        (hm, gl),
        (-hm, gl),
    ]
    return [AllplanGeometry.Point2D(x, y) for x, y in pts]


def build_groove_top_rect_mm(
    groove_len_mm: float,
    straight_len_mm: float,
    main_width_mm: float,
    slant_edge_len_mm: float,
    angle_from_vertical_deg: float,
) -> list[AllplanGeometry.Point2D]:
    """Rectángulo últimos 25 mm en Y; X desplazado +dx como la cara superior del tramo."""
    d = _slant_dims_mm(
        groove_len_mm,
        straight_len_mm,
        main_width_mm,
        slant_edge_len_mm,
        angle_from_vertical_deg,
    )
    hm = d["half_m"]
    dx = d["dx"]
    yaf = d["y_after_upper_straight"]
    ymax = d["y_max"]
    pts = [
        (-hm + dx, yaf),
        (hm + dx, yaf),
        (hm + dx, ymax),
        (-hm + dx, ymax),
    ]
    return [AllplanGeometry.Point2D(x, y) for x, y in pts]


def _extrude_polygon_z(
    points_2d: list[AllplanGeometry.Point2D],
    depth_mm: float,
    *,
    label: str = "",
) -> AllplanGeometry.BRep3D | None:
    poly_points = [AllplanGeometry.Point3D(p.X, p.Y, 0.0) for p in points_2d]
    if poly_points[0] != poly_points[-1]:
        poly_points.append(poly_points[0])

    polygon = AllplanGeometry.Polygon3D(poly_points)
    path = AllplanGeometry.Polyline3D()
    path += AllplanGeometry.Point3D(0.0, 0.0, 0.0)
    path += AllplanGeometry.Point3D(0.0, 0.0, depth_mm)

    err, body = AllplanGeometry.CreatePolyhedron(polygon, path)
    valid = body is not None and body.IsValid()
    _ensure_stderr_handler()
    _LOG.info(
        "CreatePolyhedron%s: err=%s valid=%s n_pts=%d depth_mm=%.6g",
        f" [{label}]" if label else "",
        err,
        valid,
        len(points_2d),
        depth_mm,
    )
    if err != 0 or not valid:
        _console(
            f"ERROR CreatePolyhedron{label} err={err} body_is_none={body is None} "
            f"valid={valid}"
        )
        _LOG.warning("Polígono inválido o orden incorrecto.")
    if err != 0 or body is None or not body.IsValid():
        return None
    return body


def _build_flow_arrow_polygon(
    *,
    main_width_mm: float,
    groove_len_mm: float,
    straight_len_mm: float,
    slant_edge_len_mm: float,
    angle_from_vertical_deg: float,
    extrude_z_mm: float,
    flow_forward: bool,
) -> AllplanGeometry.Polygon3D:
    """
    Flecha centrada sobre el eje del quiebro.
    - flow_forward=True: inicio -> final (Impulsió)
    - flow_forward=False: final -> inicio (Retorn)
    """
    d = _slant_dims_mm(
        groove_len_mm,
        straight_len_mm,
        main_width_mm,
        slant_edge_len_mm,
        angle_from_vertical_deg,
    )
    dx = d["dx"]
    y_max = d["y_max"]

    # Dirección y centrado sobre el eje completo entrada->salida del quiebro.
    # Esto evita descentres laterales en planta respecto al tubo total.
    start_x, start_y = 0.0, 0.0
    end_x, end_y = dx, y_max
    if not flow_forward:
        start_x, end_x = end_x, start_x
        start_y, end_y = end_y, start_y

    vx = end_x - start_x
    vy = end_y - start_y
    vlen = math.hypot(vx, vy)
    if vlen < 1e-6:
        vx, vy, vlen = 0.0, 1.0, 1.0
    ux = vx / vlen
    uy = vy / vlen
    nx = -uy
    ny = ux

    arrow_len = 140.0
    x_span = 30.0
    center_x = (start_x + end_x) * 0.5
    center_y = (start_y + end_y) * 0.5
    base_x = center_x - ux * (arrow_len * 0.5)
    base_y = center_y - uy * (arrow_len * 0.5)
    tip_x = center_x + ux * (arrow_len * 0.5)
    tip_y = center_y + uy * (arrow_len * 0.5)
    neck_x = tip_x - ux * (x_span * 2.0)
    neck_y = tip_y - uy * (x_span * 2.0)
    z = extrude_z_mm + 0.5

    pts = [
        AllplanGeometry.Point3D(base_x - nx * x_span, base_y - ny * x_span, z),
        AllplanGeometry.Point3D(neck_x - nx * x_span, neck_y - ny * x_span, z),
        AllplanGeometry.Point3D(neck_x - nx * x_span * 2.0, neck_y - ny * x_span * 2.0, z),
        AllplanGeometry.Point3D(tip_x, tip_y, z),
        AllplanGeometry.Point3D(neck_x + nx * x_span * 2.0, neck_y + ny * x_span * 2.0, z),
        AllplanGeometry.Point3D(neck_x + nx * x_span, neck_y + ny * x_span, z),
        AllplanGeometry.Point3D(base_x + nx * x_span, base_y + ny * x_span, z),
    ]
    pts.append(pts[0])
    return AllplanGeometry.Polygon3D(pts)


def _build_flow_arrow_polygon_aligned(
    *,
    center_x: float,
    center_y: float,
    extrude_z_mm: float,
    flow_forward: bool,
) -> AllplanGeometry.Polygon3D:
    """
    Flecha construida directamente en el sistema local ALINEADO del quiebro:
    - eje longitudinal = +Y
    - evita desfaces por mezclar ejes geométricos distintos.
    """
    arrow_len = 140.0
    x_span = 30.0
    ux, uy = (0.0, 1.0) if flow_forward else (0.0, -1.0)
    nx, ny = -uy, ux

    base_x = center_x - ux * (arrow_len * 0.5)
    base_y = center_y - uy * (arrow_len * 0.5)
    tip_x = center_x + ux * (arrow_len * 0.5)
    tip_y = center_y + uy * (arrow_len * 0.5)
    neck_x = tip_x - ux * (x_span * 2.0)
    neck_y = tip_y - uy * (x_span * 2.0)
    z = extrude_z_mm + 0.5

    pts = [
        AllplanGeometry.Point3D(base_x - nx * x_span, base_y - ny * x_span, z),
        AllplanGeometry.Point3D(neck_x - nx * x_span, neck_y - ny * x_span, z),
        AllplanGeometry.Point3D(neck_x - nx * x_span * 2.0, neck_y - ny * x_span * 2.0, z),
        AllplanGeometry.Point3D(tip_x, tip_y, z),
        AllplanGeometry.Point3D(neck_x + nx * x_span * 2.0, neck_y + ny * x_span * 2.0, z),
        AllplanGeometry.Point3D(neck_x + nx * x_span, neck_y + ny * x_span, z),
        AllplanGeometry.Point3D(base_x + nx * x_span, base_y + ny * x_span, z),
    ]
    pts.append(pts[0])
    return AllplanGeometry.Polygon3D(pts)


def _build_axis_alignment_matrix(
    *,
    groove_len_mm: float,
    straight_len_mm: float,
    main_width_mm: float,
    slant_edge_len_mm: float,
    angle_from_vertical_deg: float,
) -> tuple[AllplanGeometry.Matrix3D, float, float]:
    """
    Alinea el eje local del quiebro al +Y usando el eje del tramo oblicuo real:
    - eje intrínseco: vector (dx, dy) del tramo inclinado
    - se rota en Z para que ese vector quede vertical local.
    Devuelve (matriz, angulo_intrinseco_deg, rot_aplicada_deg).
    """
    d = _slant_dims_mm(
        groove_len_mm,
        straight_len_mm,
        main_width_mm,
        slant_edge_len_mm,
        angle_from_vertical_deg,
    )
    dx = float(d["dx"])
    dy = float(d["dy"])
    intrinsic_deg = math.degrees(math.atan2(dy, dx if abs(dx) > 1e-9 else 1e-9))
    rot_deg = 90.0 - intrinsic_deg
    m = AllplanGeometry.Matrix3D()
    z_axis = AllplanGeometry.Line3D(
        AllplanGeometry.Point3D(0.0, 0.0, 0.0),
        AllplanGeometry.Point3D(0.0, 0.0, 1.0),
    )
    m.Rotation(z_axis, AllplanGeometry.Angle.FromDeg(rot_deg))
    return m, intrinsic_deg, rot_deg


def _read_params(build_ele, runtime_overrides: dict | None = None) -> dict:
    av, beta = _read_angle_from_vertical_deg(build_ele)
    q2_type_raw = str(getattr(getattr(build_ele, "Q2_Type", "Retorn"), "value", getattr(build_ele, "Q2_Type", "Retorn")))
    q2_type = _normalize_q2_type(q2_type_raw)
    q2_diam_ret = str(getattr(getattr(build_ele, "Q2_DiameterRetorn", "150x150"), "value", getattr(build_ele, "Q2_DiameterRetorn", "150x150")))
    q2_diam_imp = str(getattr(getattr(build_ele, "Q2_DiameterImpulsio", "150x150"), "value", getattr(build_ele, "Q2_DiameterImpulsio", "150x150")))
    active_diameter = q2_diam_ret if q2_type == "Retorn" else q2_diam_imp

    main_width_manual = _param_float(build_ele, "Q2_MainWidth_mm", 200.0)
    d_main = _diameter_main_width_mm(active_diameter)
    # Regla Clima solicitada: base 150x150 => ancho recto 200 mm,
    # y cada salto de sección +50 incrementa +50 el ancho recto:
    # main_width = diámetro_principal + 50.
    main_width_from_diameter = (d_main + 50.0) if d_main is not None else None
    main_width_effective = (
        main_width_from_diameter
        if main_width_from_diameter is not None
        else main_width_manual
    )

    out = {
        "type": q2_type,
        "type_raw": q2_type_raw,
        "diameter_retorn": q2_diam_ret,
        "diameter_impulsio": q2_diam_imp,
        "groove_len": _param_float(build_ele, "Q2_GrooveLen_mm", 25.0),
        "groove_width": _param_float(build_ele, "Q2_GrooveWidth_mm", 199.0),
        "straight_len": _param_float(build_ele, "Q2_StraightLen_mm", 75.0),
        "main_width": main_width_effective,
        "main_width_manual": main_width_manual,
        "main_width_from_diameter": main_width_from_diameter,
        "active_diameter": active_diameter,
        "slant_edge": _param_float(build_ele, "Q2_SlantEdgeLen_mm", 1032.35),
        "angle_deg": av,
        "inclination_from_horizontal_deg": beta,
        "extrude_z": _param_float(build_ele, "Q2_ExtrudeZ_mm", 200.0),
        "color": _param_int(build_ele, "Q2_Color", 207),
    }
    if runtime_overrides:
        out.update(runtime_overrides)
    return out


def _bbox_xy_mm(point_groups: list[list[AllplanGeometry.Point2D]]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for grp in point_groups:
        for pt in grp:
            xs.append(pt.X)
            ys.append(pt.Y)
    return min(xs), max(xs), min(ys), max(ys)


def create_element(
    build_ele,
    doc: AllplanElementAdapter.DocumentAdapter,
    runtime_overrides: dict | None = None,
):
    del doc
    _ensure_stderr_handler()
    _log_palette_snapshot(build_ele)
    p = _read_params(build_ele, runtime_overrides=runtime_overrides)
    _LOG.info("Parámetros resueltos: %s", p)
    _console(f"params: {p}")
    _LOG.info(
        "Paleta tipo/diámetro: tipo=%s, diámetro_activo=%s",
        p["type"],
        p["active_diameter"],
    )
    _LOG.info(
        "Ancho tramo recto (Q2_MainWidth_mm): efectivo=%.6g mm | manual=%.6g mm | por_diametro=%s",
        p["main_width"],
        p["main_width_manual"],
        (
            f"{p['main_width_from_diameter']:.6g}"
            if p["main_width_from_diameter"] is not None
            else "N/A"
        ),
    )

    mh = p["main_width"]
    gh = p["groove_width"]
    ez = max(1.0, p["extrude_z"])
    # Altura Z en hendidura (199 mm si gh/mh = 199/200)
    z_groove = ez * gh / mh if mh > 1e-9 else ez
    z_groove = min(z_groove, ez)

    gl = p["groove_len"]
    sl = p["straight_len"]
    L = p["slant_edge"]
    ang = p["angle_deg"]

    middle_pts = build_middle_outline_mm(gl, sl, mh, L, ang)
    g_bot = build_groove_bottom_rect_mm(gl, mh)
    g_top = build_groove_top_rect_mm(gl, sl, mh, L, ang)

    _log_polylines(
        "Perfiles (mm): tramo central Z=extrusión; rectángulos extremos Z=hendidura",
        [
            ("middle_Z_full", middle_pts),
            ("groove_bottom_Z_low", g_bot),
            ("groove_top_Z_low", g_top),
        ],
    )
    _LOG.info(
        "Hendidura extrema: largo Y=%.6g mm, ancho X=%.6g mm, altura Z=%.6g mm "
        "(principal Z=%.6g mm)",
        gl,
        mh,
        z_groove,
        ez,
    )
    _LOG.info(
        "Oblicuo: inclinación horizontal=%.4g° (45–90), ángulo con vertical=%.4g°",
        p["inclination_from_horizontal_deg"],
        p["angle_deg"],
    )

    bodies: list[AllplanGeometry.BRep3D] = []
    pieces = [
        (middle_pts, ez, "middle"),
        (g_bot, z_groove, "groove_bottom"),
        (g_top, z_groove, "groove_top"),
    ]
    for pts, zdep, lab in pieces:
        b = _extrude_polygon_z(pts, zdep, label=lab)
        if b is None:
            _console(f"Salida: fallo en sólido [{lab}].")
            return ([], [], [])
        bodies.append(b)

    common_properties = AllplanBaseElements.CommonProperties()
    common_properties.GetGlobalProperties()
    common_properties.Color = int(p["color"])
    common_properties.ColorByLayer = False

    model_eles = []
    axis_align_mat, intrinsic_deg, rot_applied_deg = _build_axis_alignment_matrix(
        groove_len_mm=gl,
        straight_len_mm=sl,
        main_width_mm=mh,
        slant_edge_len_mm=L,
        angle_from_vertical_deg=ang,
    )
    # Centro de anclaje del quiebro = punto medio del eje entrada->salida.
    # El pipeline inserta el elemento en el centro del segmento; esta referencia
    # debe coincidir con ese centro para que empalmen entrada/salida.
    d_axis = _slant_dims_mm(gl, sl, mh, L, ang)
    axis_mid = AllplanGeometry.Point3D(d_axis["dx"] * 0.5, d_axis["y_max"] * 0.5, 0.0)
    axis_mid_aligned = AllplanGeometry.Transform(axis_mid, axis_align_mat)
    cx = axis_mid_aligned.X
    cy = axis_mid_aligned.Y
    cz = ez * 0.5

    mat = AllplanGeometry.Matrix3D()
    mat.SetTranslation(AllplanGeometry.Vector3D(-cx, -cy, -cz))

    for b in bodies:
        b_local = AllplanGeometry.Transform(b, axis_align_mat)
        bc = AllplanGeometry.Transform(b_local, mat)
        model_eles.append(AllplanBasisElements.ModelElement3D(common_properties, bc))

    flow_forward = p["type"] == "Impulsió"
    arrow_poly_local = _build_flow_arrow_polygon_aligned(
        center_x=cx,
        center_y=cy,
        extrude_z_mm=ez,
        flow_forward=flow_forward,
    )
    arrow_poly_centered = AllplanGeometry.Transform(arrow_poly_local, mat)
    arrow_props = AllplanBaseElements.CommonProperties()
    arrow_props.GetGlobalProperties()
    arrow_props.Color = int(ARROW_COLOR_BY_TYPE.get(p["type"], 8))
    arrow_props.ColorByLayer = False
    model_eles.append(AllplanBasisElements.ModelElement3D(arrow_props, arrow_poly_centered))

    _LOG.info(
        "Centrado: cx=%.6g cy=%.6g cz=%.6g (XY total + mitad Z principal)",
        cx,
        cy,
        cz,
    )
    _LOG.info(
        "Flecha centrada: tipo=%s(raw=%s), sentido=%s, color=%s",
        p["type"],
        p["type_raw"],
        "inicio->final" if flow_forward else "final->inicio",
        ARROW_COLOR_BY_TYPE.get(p["type"], 8),
    )
    _LOG.info(
        "Alineación eje local quiebro: intrínseco=%.6g° desde +X, rot_local=%.6g° para llevar a +Y",
        intrinsic_deg,
        rot_applied_deg,
    )
    _console(f"centrado mm: cx={cx:.4f} cy={cy:.4f} cz={cz:.4f}")
    _console(f"Salida: {len(model_eles)} ModelElement3D (1 central + 2 hendiduras + flecha).")
    return (model_eles, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list


class Quiebro2Script(BaseScriptObject):
    """PolyLib / mismo flujo que otros PythonParts de la instalación."""

    def __init__(
        self,
        build_ele: BuildingElement,
        script_object_data: BaseScriptObjectData,
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        runtime_overrides: dict = {}
        installation_type = kwargs.get("installation_type", None)
        diameter = kwargs.get("diameter", None)
        length_mm = kwargs.get("length_mm", None)
        incl_h_deg = kwargs.get("inclination_from_horizontal_deg", None)
        angle_signed_v_deg = kwargs.get("angle_from_vertical_signed_deg", None)
        if installation_type is not None:
            runtime_overrides["type_raw"] = str(installation_type)
            runtime_overrides["type"] = _normalize_q2_type(str(installation_type))
        if diameter is not None:
            runtime_overrides["active_diameter"] = str(diameter)
            d_main = _diameter_main_width_mm(str(diameter))
            if d_main is not None:
                runtime_overrides["main_width"] = d_main + 50.0
                runtime_overrides["main_width_from_diameter"] = d_main + 50.0
        if length_mm is not None:
            try:
                runtime_overrides["slant_edge"] = max(1.0, float(length_mm))
            except Exception:
                pass
        if incl_h_deg is not None:
            try:
                beta = max(45.0, min(90.0, float(incl_h_deg)))
                runtime_overrides["inclination_from_horizontal_deg"] = beta
                runtime_overrides["angle_deg"] = 90.0 - beta
            except Exception:
                pass
        if angle_signed_v_deg is not None:
            try:
                a_signed = max(-45.0, min(45.0, float(angle_signed_v_deg)))
                runtime_overrides["angle_deg"] = a_signed
                runtime_overrides["inclination_from_horizontal_deg"] = 90.0 - abs(a_signed)
            except Exception:
                pass
        model_list, _, _ = create_element(
            self.build_ele,
            self.doc,
            runtime_overrides=runtime_overrides or None,
        )
        return CreateElementResult(model_list)
