# -*- coding: utf-8 -*-
"""Constantes de colocación y recortes (trim in / trim out) para Clima.

Convención alineada con `Instalaciones/Saneamiento/pyp-scripts/utils/geo_handler.py`:
- **TRIM_IN**: recorta el tramo en el extremo de entrada (llegada / inicio del segmento según vector).
- **TRIM_OUT**: recorta el tramo en el extremo de salida (salida del tramo).

Valores por defecto para **todos** los diámetros de tramo recto (`DEFAULT_TRIM_*`).
Para afinar una sección concreta, edita `TRIM_BY_DIAMETER_MM`. Lo usa
`geo_handler.PipelineProcessor` al generar tubos.

**Codo 90° (todos los diámetros 150x150…750x150):** `CODO90_TRIM_BY_DIAMETER_MM` — hueco en
el vértice (mm), mismos criterios para **Impulsió** y **Retorn**.
"""

from typing import Dict, Optional, Tuple

# ---------------------------------------------------
# Valores por defecto (mm) — se aplican a cada entrada de `TRIM_BY_DIAMETER_MM`
# si no sobrescribes esa fila.
# ---------------------------------------------------
DEFAULT_TRIM_IN_MM = 0.0
DEFAULT_TRIM_OUT_MM = 25.0

# Diámetros nominales iguales que `MAP_TRAM_RECTE_SIZE` en `tram_recte_script.py`.
ALL_TRAM_RECTE_DIAMETERS = (
    "150x150",
    "200x150",
    "250x150",
    "300x150",
    "350x150",
    "400x150",
    "450x150",
    "500x150",
    "550x150",
    "600x150",
    "650x150",
    "700x150",
    "750x150",
)

# Mapa (mm): sobrescribe aquí por diámetro si hace falta; claves desconocidas → defaults.
TRIM_BY_DIAMETER_MM: Dict[str, Tuple[float, float]] = {
    d: (DEFAULT_TRIM_IN_MM, DEFAULT_TRIM_OUT_MM) for d in ALL_TRAM_RECTE_DIAMETERS
}


def get_trim_in_out_mm(diameter_key: Optional[str]) -> Tuple[float, float]:
    """Devuelve (trim_in, trim_out) para `SegmentInfo.diameter` (ej. ``150x150``)."""
    if not diameter_key:
        return (DEFAULT_TRIM_IN_MM, DEFAULT_TRIM_OUT_MM)
    key = str(diameter_key).strip()
    return TRIM_BY_DIAMETER_MM.get(key, (DEFAULT_TRIM_IN_MM, DEFAULT_TRIM_OUT_MM))


# ---------------------------------------------------
# Codo 90° — recortes en vértice por diámetro (Impulsió y Retorn: mismos mm)
# ---------------------------------------------------
# Convención (como en Saneamiento geo_handler para codos):
# - TRIM_IN: tramo **entrante** al codo (extremo final del segmento antes del vértice).
# - TRIM_OUT: tramo **saliente** del codo (extremo inicial del segmento después del vértice).
DEFAULT_CODO90_TRIM_IN_MM = 270.0
DEFAULT_CODO90_TRIM_OUT_MM = 270.0

# Recorte en vértice (mm) por sección: (TRIM_IN entrante, TRIM_OUT saliente). Edita fila a fila.
# Claves = mismas que `ALL_TRAM_RECTE_DIAMETERS` y la paleta (ej. "350x150").
# Diámetros no listados siguen resolviendo vía `get_codo90_trim_in_out_mm` → DEFAULT_*.
CODO90_TRIM_BY_DIAMETER_MM: Dict[str, Tuple[float, float]] = {
    "150x150": (260.0, 285.0),
    "200x150": (285.0, 310.0),
    "250x150": (310.0, 335.0),
    "300x150": (335.0, 360.0),
    "350x150": (355.5, 385.0),
    "400x150": (386.25, 410.0),
    "450x150": (410.5, 435.0),
    "500x150": (432.0, 460.0),
    "550x150": (460.0, 485.0),
    "600x150": (483.0, 510.0),
    "650x150": (504.80, 535.0),
    "700x150": (530.5, 560.0),
    "750x150": (561.2, 585.0),
}


def get_codo90_trim_in_out_mm(diameter_key: Optional[str]) -> Tuple[float, float]:
    """(trim_in, trim_out) en mm en vértice con codo 90° para el diámetro de paleta."""
    if not diameter_key:
        return (DEFAULT_CODO90_TRIM_IN_MM, DEFAULT_CODO90_TRIM_OUT_MM)
    key = str(diameter_key).strip()
    return CODO90_TRIM_BY_DIAMETER_MM.get(
        key, (DEFAULT_CODO90_TRIM_IN_MM, DEFAULT_CODO90_TRIM_OUT_MM)
    )


# ---------------------------------------------------
# Retrocompatibilidad / alias 150x150
# ---------------------------------------------------
SECTION_150x150 = "150x150"
_cin, _cout = get_codo90_trim_in_out_mm(SECTION_150x150)
CODO90_150x150_TRIM_IN_MM = _cin
CODO90_150x150_TRIM_OUT_MM = _cout
_tin, _tout = get_trim_in_out_mm(SECTION_150x150)
TUBO_150x150_TRIM_IN_MM = _tin
TUBO_150x150_TRIM_OUT_MM = _tout
TRAM_RECTE_150x150_TRIM_IN_MM = TUBO_150x150_TRIM_IN_MM
TRAM_RECTE_150x150_TRIM_OUT_MM = TUBO_150x150_TRIM_OUT_MM
