# -*- coding: utf-8 -*-
"""
Traslación adicional del codo (mm) según diámetro de paleta.

Hay dos formas de interpretar la tupla (a, b, c), controladas por
`COD0_TRANSLATION_SPACE`:

- "vertex" (recomendado): coherente en **todos** los giros 90° en planta.
  - a = mm a lo largo del **tramo de entrada** (vector del segmento que llega al vértice)
  - b = mm a lo largo del **tramo de salida** (vector del segmento que sale del vértice)
  - c = mm en **Z global** (Allplan)

- "world": (a, b, c) son desplazamiento fijo en **X, Y, Z mundo**.
  El mismo número se ve distinto según orientación del tramo (por eso un caso
  “parece” que aplica y otro no).

El diámetro debe coincidir con SegmentInfo.diameter ("150x150" … "750x150").
"""
from __future__ import annotations

# "vertex" | "world"
COD0_TRANSLATION_SPACE: str = "vertex"

# ── Yaw extra del codo (°) según sentido del giro en planta (vista desde +Z) ──
# cross_z = v_entrada.X * v_salida.Y - v_entrada.Y * v_salida.X
#   > 0  → giro antihorario / a la izquierda
#   < 0  → giro horario / a la derecha (en geo_handler además se hace flip 180° en eje X local)
# Se suma a: obtener_rotacion_codo(v_entrada)
COLZE_YAW_EXTRA_GIRO_IZQUIERDA_DEG: float = 270.0
COLZE_YAW_EXTRA_GIRO_DERECHA_DEG: float =90.0


def get_colze_yaw_extra_deg(cross_z: float) -> float:
    """Corrección de yaw (grados) según el signo de cross_z (giro izq./der.)."""
    if cross_z < 0:
        return float(COLZE_YAW_EXTRA_GIRO_DERECHA_DEG)
    return float(COLZE_YAW_EXTRA_GIRO_IZQUIERDA_DEG)


# Claves = mismas cadenas que en polyline_reg_clima (DiameterTypeStr / diámetro de segmento).
COD0_TRANSLATION_MM_BY_DIAMETER: dict[str, tuple[float, float, float]] = {
    "150x150": (-185.0, 100.0, 100.0),
    "200x150": (-210.0, 125.0, -100.0),
    "250x150": (-235.0, 150.0, -100.0),
    "300x150": (-115.0, -175.0, 100.0),
    "350x150": (-115.0, -200.0, 100.0),
    "400x150": (-125.0, -225.0, 100.0),
    "450x150": (-170.0, -250.0, 100.0),
    "500x150": (-200.0, -275.0, 100.0),
    "550x150": (-140.0, -300.0, 100.0),
    "600x150": (-140.0, -325.0, 100.0),
    "650x150": (-140.0, -350.0, 100.0),
    "700x150": (-145.0, -375.0, 100.0),
    "750x150": (-155.0, -400.0, 100.0),
}


def get_codo_translation_mm(diameter_key: str | None) -> tuple[float, float, float]:
    """Devuelve la tupla (a, b, c) en mm según `COD0_TRANSLATION_SPACE`; si no hay clave, (0,0,0)."""
    if not diameter_key:
        return (0.0, 0.0, 0.0)
    key = str(diameter_key).strip()
    return COD0_TRANSLATION_MM_BY_DIAMETER.get(key, (0.0, 0.0, 0.0))


def resolve_codo_translation_world_mm(
    diameter_key: str | None,
    v_in,
    v_out,
) -> tuple[float, float, float]:
    """
    Convierte (a,b,c) a desplazamiento mundo (mm) para colocar el codo.

    v_in, v_out: Vector3D normalizados (tramo que termina en el vértice y el siguiente).
    """
    a, b, c = get_codo_translation_mm(diameter_key)
    if COD0_TRANSLATION_SPACE == "world":
        return (a, b, c)
    # vertex: combinación lineal en el plano del giro + Z global
    wx = a * v_in.X + b * v_out.X
    wy = a * v_in.Y + b * v_out.Y
    wz = a * v_in.Z + b * v_out.Z + c
    return (wx, wy, wz)
