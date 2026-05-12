import math

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter

from CreateElementResult import CreateElementResult


def check_allplan_version(_build_ele, _version) -> bool:
    return True


# Valores por defecto en metros / grados cuando no existe parámetro en la paleta
TOP_LEN_M = 0.34853
LONG_DIAG_LEN_M = 0.66371
SHORT_DIAG_LEN_M = 0.09803
RIGHT_TOP_LEN_M = 0.18284
RIGHT_VERT_LEN_M = 0.2
RIGHT_BOTTOM_LEN_M = 0.1
RIGHT_BOTTOM_DIAG_LEN_M = 0.12021
BOTTOM_RIGHT_VERT_LEN_M = 0.1
BOTTOM_LEN_M = 0.70000
BOTTOM_LEFT_VERT_LEN_M = 0.1
BOTTOM_LEFT_DIAG_LEN_M = 0.12021
BOTTOM_LEFT_LEN_M = 0.1
LEFT_VERT_LEN_M = 0.60000
HEIGHT_M = 0.2

ARROW_LENGTH_M = 0.14
ARROW_HALF_WIDTH_M = 0.03
ARROW_THICK_M = 0.005
ARROW_Z_OFFSET_M = 0.005
ARROW_COLOR = 65
ARROW1_ANGLE_DEG = 45.0
ARROW2_ANGLE_DEG = -45.0
ARROW1_POS_X_FACTOR = 0.32
ARROW1_POS_Y_FACTOR = 0.62
ARROW2_POS_X_FACTOR = 0.83
ARROW2_POS_Y_FACTOR = 0.30

ANGLE_DOWN_RIGHT_DEG = -45.0
ANGLE_DOWN_LEFT_DEG = -135.0
ANGLE_UP_LEFT_DEG = 135.0

M_TO_MM = 1000.0


def _param_double(build_ele, name: str, default: float) -> float:
    if build_ele is not None and hasattr(build_ele, name):
        return float(getattr(build_ele, name).value)
    return float(default)


def _length_mm(build_ele, name: str, default_m: float) -> float:
    if build_ele is not None and hasattr(build_ele, name):
        return float(getattr(build_ele, name).value)
    return default_m * M_TO_MM


def _param_int(build_ele, name: str, default: int) -> int:
    if build_ele is not None and hasattr(build_ele, name):
        try:
            return int(getattr(build_ele, name).value)
        except (TypeError, ValueError):
            pass
    return int(default)


def _param_bool(build_ele, name: str, default: bool) -> bool:
    if build_ele is not None and hasattr(build_ele, name):
        val = getattr(build_ele, name).value
        if isinstance(val, bool):
            return val
        s = str(val).strip().lower()
        if s in ("true", "1", "yes"):
            return True
        if s in ("false", "0", "no"):
            return False
    return default


def _build_points_mm(build_ele):
    pairs = [
        ("TopLen", TOP_LEN_M, "AngleSegTopDeg", 0.0),
        ("LongDiagLen", LONG_DIAG_LEN_M, "AngleSegLongDiagDeg", ANGLE_DOWN_RIGHT_DEG),
        ("ShortDiagLen", SHORT_DIAG_LEN_M, "AngleSegShortDiagDeg", 45.0),
        ("RightTopLen", RIGHT_TOP_LEN_M, "AngleSegRightTopDeg", 0.0),
        ("RightVertLen", RIGHT_VERT_LEN_M, "AngleSegRightVertDeg", -90.0),
        ("RightBottomLen", RIGHT_BOTTOM_LEN_M, "AngleSegRightBottomDeg", 180.0),
        ("RightBottomDiagLen", RIGHT_BOTTOM_DIAG_LEN_M, "AngleSegRightBottomDiagDeg", ANGLE_DOWN_LEFT_DEG),
        ("BottomRightVertLen", BOTTOM_RIGHT_VERT_LEN_M, "AngleSegBottomRightVertDeg", -90.0),
        ("BottomLen", BOTTOM_LEN_M, "AngleSegBottomDeg", 180.0),
        ("BottomLeftVertLen", BOTTOM_LEFT_VERT_LEN_M, "AngleSegBottomLeftVertDeg", 90.0),
        ("BottomLeftDiagLen", BOTTOM_LEFT_DIAG_LEN_M, "AngleSegBottomLeftDiagDeg", ANGLE_UP_LEFT_DEG),
        ("BottomLeftLen", BOTTOM_LEFT_LEN_M, "AngleSegBottomLeftHorDeg", 180.0),
        ("LeftVertLen", LEFT_VERT_LEN_M, "AngleSegLeftVertDeg", 90.0),
    ]

    segments = [
        (_length_mm(build_ele, ln, dm), _param_double(build_ele, an, dd))
        for ln, dm, an, dd in pairs
    ]

    points = [AllplanGeometry.Point2D(0.0, 0.0)]
    x = 0.0
    y = 0.0

    for length, angle_deg in segments:
        angle_rad = math.radians(angle_deg)
        x += length * math.cos(angle_rad)
        y += length * math.sin(angle_rad)
        points.append(AllplanGeometry.Point2D(x, y))

    return points


def create_element(build_ele, _doc: AllplanElementAdapter.DocumentAdapter):
    common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    common_props.Color = _param_int(build_ele, "BodyColor", 207)
    common_props.ColorByLayer = False

    points_2d = _build_points_mm(build_ele)

    height_mm = _length_mm(build_ele, "Height", HEIGHT_M)

    poly_points = [AllplanGeometry.Point3D(p.X, p.Y, 0.0) for p in points_2d]
    if _param_bool(build_ele, "ClosePolygon", True):
        if poly_points[0] != poly_points[-1]:
            poly_points.append(poly_points[0])
    polygon = AllplanGeometry.Polygon3D(poly_points)

    path = AllplanGeometry.Polyline3D()
    path += AllplanGeometry.Point3D(0.0, 0.0, 0.0)
    path += AllplanGeometry.Point3D(0.0, 0.0, height_mm)

    err, body = AllplanGeometry.CreatePolyhedron(polygon, path)
    if err != 0 or body is None or not body.IsValid():
        return CreateElementResult([])

    arrow_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    arrow_props.Color = _param_int(build_ele, "ArrowColor", ARROW_COLOR)
    arrow_props.ColorByLayer = False

    min_x = min(p.X for p in points_2d)
    max_x = max(p.X for p in points_2d)
    min_y = min(p.Y for p in points_2d)
    max_y = max(p.Y for p in points_2d)

    length_mm_arrow = _param_double(build_ele, "ArrowLengthMm", ARROW_LENGTH_M * M_TO_MM)
    half_width_mm = _param_double(build_ele, "ArrowHalfWidthMm", ARROW_HALF_WIDTH_M * M_TO_MM)
    thick_mm = _param_double(build_ele, "ArrowThickMm", ARROW_THICK_M * M_TO_MM)
    z_off_mm = _param_double(build_ele, "ArrowZOffsetMm", ARROW_Z_OFFSET_M * M_TO_MM)

    a1_deg = _param_double(build_ele, "Arrow1AngleDeg", ARROW1_ANGLE_DEG)
    a2_deg = _param_double(build_ele, "Arrow2AngleDeg", ARROW2_ANGLE_DEG)

    fx1 = _param_double(build_ele, "Arrow1PosXFactor", ARROW1_POS_X_FACTOR)
    fy1 = _param_double(build_ele, "Arrow1PosYFactor", ARROW1_POS_Y_FACTOR)
    fx2 = _param_double(build_ele, "Arrow2PosXFactor", ARROW2_POS_X_FACTOR)
    fy2 = _param_double(build_ele, "Arrow2PosYFactor", ARROW2_POS_Y_FACTOR)

    def build_arrow(center_x: float, center_y: float, angle_deg: float, mat_center):
        z_base = height_mm + z_off_mm

        base_y = -length_mm_arrow * 0.5
        tip_y = base_y + length_mm_arrow

        pts = [
            (-half_width_mm, base_y),
            (-half_width_mm, tip_y - half_width_mm * 2),
            (-half_width_mm * 2, tip_y - half_width_mm * 2),
            (0.0, tip_y),
            (half_width_mm * 2, tip_y - half_width_mm * 2),
            (half_width_mm, tip_y - half_width_mm * 2),
            (half_width_mm, base_y),
        ]

        ang = math.radians(angle_deg)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        poly_pts = []
        for x, y in pts:
            rx = x * cos_a - y * sin_a + center_x
            ry = x * sin_a + y * cos_a + center_y
            poly_pts.append(AllplanGeometry.Point3D(rx, ry, z_base))
        poly_pts.append(poly_pts[0])

        arrow_poly = AllplanGeometry.Polygon3D(poly_pts)

        arrow_path = AllplanGeometry.Polyline3D()
        arrow_path += AllplanGeometry.Point3D(0.0, 0.0, z_base)
        arrow_path += AllplanGeometry.Point3D(0.0, 0.0, z_base + thick_mm)

        err_arrow, arrow_body = AllplanGeometry.CreatePolyhedron(arrow_poly, arrow_path)
        if err_arrow != 0 or arrow_body is None or not arrow_body.IsValid():
            return None
        if mat_center is not None:
            arrow_body = AllplanGeometry.Transform(arrow_body, mat_center)
        return AllplanBasisElements.ModelElement3D(arrow_props, arrow_body)

    span_x = max_x - min_x
    span_y = max_y - min_y
    arrow1_x = min_x + span_x * fx1
    arrow1_y = min_y + span_y * fy1
    arrow2_x = min_x + span_x * fx2
    arrow2_y = min_y + span_y * fy2

    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    center_z = height_mm * 0.5

    mat_center = AllplanGeometry.Matrix3D()
    mat_center.SetTranslation(
        AllplanGeometry.Vector3D(-center_x, -center_y, -center_z)
    )

    body_centered = AllplanGeometry.Transform(body, mat_center)
    elements = [AllplanBasisElements.ModelElement3D(common_props, body_centered)]
    arrow1 = build_arrow(arrow1_x, arrow1_y, a1_deg, mat_center)
    arrow2 = build_arrow(arrow2_x, arrow2_y, a2_deg, mat_center)
    if arrow1:
        elements.append(arrow1)
    if arrow2:
        elements.append(arrow2)

    return CreateElementResult(elements)
