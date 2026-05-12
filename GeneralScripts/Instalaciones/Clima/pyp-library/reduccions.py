import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


def check_allplan_version(_build_ele, _version) -> bool:
    return True


# Valores por defecto (mm) — la paleta puede sobrescribirlos vía `Impl_*` / `Ret_*`.
REDIMPLUSIO_WIDTH_BOTTOM = 400.0
REDIMPLUSIO_WIDTH_TOP = 300.0
REDIMPLUSIO_LENGTH_TOTAL = 1200.0
REDIMPLUSIO_STRAIGHT_LEN = 300.0
REDIMPLUSIO_HEIGHT = 200.0

REDRETORN_WIDTH_BOTTOM = 400.0
REDRETORN_WIDTH_TOP = 300.0
REDRETORN_LENGTH_TOTAL = 1000.0
REDRETORN_STRAIGHT_LEN = 200.0
REDRETORN_HEIGHT = 200.0

# Flecha (orientación visual)
REDIMPLUSIO_ARROW_LENGTH = 140.0
REDIMPLUSIO_ARROW_HALF_WIDTH = 30.0
REDIMPLUSIO_ARROW_Z_OFFSET = 5.0

REDRETORN_ARROW_LENGTH = 140.0
REDRETORN_ARROW_HALF_WIDTH = 30.0
REDRETORN_ARROW_Z_OFFSET = 5.0


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


def _read_impl_from_palette(build_ele) -> dict:
    return {
        "width_bottom": _param_float(build_ele, "Impl_WidthBottom", REDIMPLUSIO_WIDTH_BOTTOM),
        "width_top": _param_float(build_ele, "Impl_WidthTop", REDIMPLUSIO_WIDTH_TOP),
        "length_total": _param_float(build_ele, "Impl_LengthTotal", REDIMPLUSIO_LENGTH_TOTAL),
        "straight_len": _param_float(build_ele, "Impl_StraightLen", REDIMPLUSIO_STRAIGHT_LEN),
        "height": _param_float(build_ele, "Impl_Height", REDIMPLUSIO_HEIGHT),
        "arrow_length": _param_float(build_ele, "Impl_ArrowLength", REDIMPLUSIO_ARROW_LENGTH),
        "arrow_half_width": _param_float(build_ele, "Impl_ArrowHalfWidth", REDIMPLUSIO_ARROW_HALF_WIDTH),
        "arrow_z_offset": _param_float(build_ele, "Impl_ArrowZOffset", REDIMPLUSIO_ARROW_Z_OFFSET),
        "arrow_color": _param_int(build_ele, "Impl_ArrowColor", 65),
    }


def _read_ret_from_palette(build_ele) -> dict:
    return {
        "width_bottom": _param_float(build_ele, "Ret_WidthBottom", REDRETORN_WIDTH_BOTTOM),
        "width_top": _param_float(build_ele, "Ret_WidthTop", REDRETORN_WIDTH_TOP),
        "length_total": _param_float(build_ele, "Ret_LengthTotal", REDRETORN_LENGTH_TOTAL),
        "straight_len": _param_float(build_ele, "Ret_StraightLen", REDRETORN_STRAIGHT_LEN),
        "height": _param_float(build_ele, "Ret_Height", REDRETORN_HEIGHT),
        "arrow_length": _param_float(build_ele, "Ret_ArrowLength", REDRETORN_ARROW_LENGTH),
        "arrow_half_width": _param_float(build_ele, "Ret_ArrowHalfWidth", REDRETORN_ARROW_HALF_WIDTH),
        "arrow_z_offset": _param_float(build_ele, "Ret_ArrowZOffset", REDRETORN_ARROW_Z_OFFSET),
        "arrow_color": _param_int(build_ele, "Ret_ArrowColor", 8),
    }


class _BaseReduccionModel:
    def __init__(
        self,
        _doc: AllplanElementAdapter.DocumentAdapter,
        width_bottom: float,
        width_top: float,
        length_total: float,
        straight_len: float,
        height: float,
        arrow_length: float,
        arrow_half_width: float,
        arrow_z_offset: float,
        arrow_direction: int,
        arrow_color: int,
    ):
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Color = 207
        common_properties.ColorByLayer = False
        self.common_props = common_properties

        arrow_props = AllplanBaseElements.CommonProperties()
        arrow_props.GetGlobalProperties()
        arrow_props.Color = int(arrow_color)
        arrow_props.ColorByLayer = False
        self.arrow_props = arrow_props

        self.width_bottom = width_bottom
        self.width_top = width_top
        self.length_total = length_total
        self.straight_len = straight_len
        self.height = height
        self.arrow_length = arrow_length
        self.arrow_half_width = arrow_half_width
        self.arrow_z_offset = arrow_z_offset
        self.arrow_direction = arrow_direction

        # Rodillas del cono: referencia fija por tipo. straight_len (paleta/combo) solo
        # extiende tramos rectos en y_lo / y_hi (no sustituye a s_ref).
        if arrow_direction >= 0:
            s_ref = float(REDIMPLUSIO_STRAIGHT_LEN)
        else:
            s_ref = float(REDRETORN_STRAIGHT_LEN)
        # Largo físico = 2 * straight_len + slope_proj (tramos rectos a ambos lados del cono).
        # Usar `straight_len` aquí (no `s_ref` catálogo): si straight > s_ref —típ. Retorn 300 vs 200—
        # el término antiguo length_total - 2*s_ref alargaba la pieza en 2*(straight_len - s_ref).
        slope_proj = max(0.0, length_total - 2.0 * float(straight_len))
        self._y_knee_l = s_ref
        self._y_knee_r = s_ref + slope_proj
        self._y_lo = self._y_knee_l - straight_len
        self._y_hi = self._y_knee_r + straight_len
        self.length_effective = self._y_hi - self._y_lo

    def _build_body(self) -> AllplanGeometry.BRep3D:
        delta_width = self.width_bottom - self.width_top
        y_lo = self._y_lo
        y_knee_l = self._y_knee_l
        y_knee_r = self._y_knee_r
        y_hi = self._y_hi

        poly = AllplanGeometry.Polygon3D(
            [
                AllplanGeometry.Point3D(0.0, y_lo, 0.0),
                AllplanGeometry.Point3D(0.0, y_knee_l, 0.0),
                AllplanGeometry.Point3D(delta_width, y_knee_r, 0.0),
                AllplanGeometry.Point3D(delta_width, y_hi, 0.0),
                AllplanGeometry.Point3D(self.width_bottom, y_hi, 0.0),
                AllplanGeometry.Point3D(self.width_bottom, y_lo, 0.0),
                AllplanGeometry.Point3D(0.0, y_lo, 0.0),
            ]
        )

        path = AllplanGeometry.Polyline3D()
        path += AllplanGeometry.Point3D(0.0, y_lo, 0.0)
        path += AllplanGeometry.Point3D(0.0, y_lo, self.height)

        err, body = AllplanGeometry.CreatePolyhedron(poly, path)
        if err != 0 or body is None or not body.IsValid():
            raise Exception(f"Error al crear la reducción: código {err}")

        return body

    def _center_x_on_axis_at_y(self, y: float) -> float:
        """
        Centro transversal del eje en planta a la cota Y (misma lógica que la línea guía).
        Sin esto, la flecha queda fija en width_bottom/2 y se descentra con transiciones
        extremas (p. ej. 150x150 ↔ 750x150).
        """
        wb = self.width_bottom
        wt = self.width_top
        dw = wb - wt
        x_wide_c = wb * 0.5
        x_narrow_c = dw + wt * 0.5
        ykl = self._y_knee_l
        ykr = self._y_knee_r
        if y <= ykl:
            return float(x_wide_c)
        if y >= ykr:
            return float(x_narrow_c)
        span = float(ykr - ykl)
        if span < 1e-9:
            return float(x_wide_c)
        frac = (float(y) - ykl) / span
        return float(x_wide_c + frac * (x_narrow_c - x_wide_c))

    def _build_arrow(self) -> AllplanGeometry.Polygon3D:
        z_flecha = self.height + self.arrow_z_offset
        y_mid = 0.5 * (self._y_lo + self._y_hi)
        x_center = self._center_x_on_axis_at_y(y_mid)
        base_y = y_mid - self.arrow_length * 0.5
        sentido = 1 if self.arrow_direction >= 0 else -1
        punta_y = base_y + sentido * self.arrow_length

        points = [
            AllplanGeometry.Point3D(
                x_center - self.arrow_half_width, base_y, z_flecha
            ),
            AllplanGeometry.Point3D(
                x_center - self.arrow_half_width,
                punta_y - sentido * self.arrow_half_width * 2,
                z_flecha,
            ),
            AllplanGeometry.Point3D(
                x_center - self.arrow_half_width * 2,
                punta_y - sentido * self.arrow_half_width * 2,
                z_flecha,
            ),
            AllplanGeometry.Point3D(x_center, punta_y, z_flecha),
            AllplanGeometry.Point3D(
                x_center + self.arrow_half_width * 2,
                punta_y - sentido * self.arrow_half_width * 2,
                z_flecha,
            ),
            AllplanGeometry.Point3D(
                x_center + self.arrow_half_width,
                punta_y - sentido * self.arrow_half_width * 2,
                z_flecha,
            ),
            AllplanGeometry.Point3D(
                x_center + self.arrow_half_width, base_y, z_flecha
            ),
        ]
        points.append(points[0])
        return AllplanGeometry.Polygon3D(points)

    def build(self):
        body = self._build_body()
        arrow = self._build_arrow()

        mat_center = AllplanGeometry.Matrix3D()
        y_ctr = 0.5 * (self._y_lo + self._y_hi)
        mat_center.SetTranslation(
            AllplanGeometry.Vector3D(
                -self.width_bottom * 0.5,
                -y_ctr,
                -self.height * 0.5,
            )
        )

        body_centered = AllplanGeometry.Transform(body, mat_center)
        arrow_centered = AllplanGeometry.Transform(arrow, mat_center)

        model_ele = AllplanBasisElements.ModelElement3D(
            self.common_props, body_centered
        )
        arrow_ele = AllplanBasisElements.ModelElement3D(
            self.arrow_props, arrow_centered
        )

        return [model_ele, arrow_ele]


def _from_params(doc, p: dict, direction: int) -> _BaseReduccionModel:
    return _BaseReduccionModel(
        doc,
        p["width_bottom"],
        p["width_top"],
        p["length_total"],
        p["straight_len"],
        p["height"],
        p["arrow_length"],
        p["arrow_half_width"],
        p["arrow_z_offset"],
        arrow_direction=direction,
        arrow_color=p.get("arrow_color", 65),
    )


def create_element(build_ele, doc: AllplanElementAdapter.DocumentAdapter):
    type_raw = getattr(build_ele, "TypeReduccionUp", None)
    type_val = getattr(type_raw, "value", type_raw)
    reduccion_type = str(type_val) if type_val else "redimplusio"

    if reduccion_type == "redretorn":
        p = _read_ret_from_palette(build_ele)
        model = _from_params(doc, p, -1)
    else:
        p = _read_impl_from_palette(build_ele)
        model = _from_params(doc, p, 1)

    model_list = model.build()
    return (model_list, [], [])


def create_preview(build_ele, doc):
    model_list, _, _ = create_element(build_ele, doc)
    return model_list
