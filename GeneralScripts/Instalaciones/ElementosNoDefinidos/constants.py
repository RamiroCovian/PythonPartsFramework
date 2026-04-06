# -*- coding: utf-8 -*-
"""
Constantes para puntos indicativos de camino sin objetos definidos.
Define tipos de punto, formas geométricas de previsualización y mapeos.
"""
from __future__ import annotations

from typing import Dict, List

# Tipos de punto (labels en UI)
TIPO_INICIO = "inicio"
TIPO_FINAL = "final"
TIPO_INTERMEDIO_LIBRE = "intermedio_libre"
TIPO_BIFURCACION = "bifurcación"
TIPO_INTERMEDIO_ORDENADO = "intermedio_ordenado"

# Formas geométricas para previsualización
SHAPE_CIRCLE = "circle"      # Inicio
SHAPE_SQUARE = "square"       # Final
SHAPE_TRIANGLE = "triangle"   # Bifurcación
SHAPE_RHOMBUS = "rhombus"    # Intermedio ordenado
SHAPE_PENTAGON = "pentagon"  # Intermedio libre

# Mapeo label UI -> key interna
LABEL_TO_TIPO: Dict[str, str] = {
    "Inicio": TIPO_INICIO,
    "Final": TIPO_FINAL,
    "Intermedio Libre": TIPO_INTERMEDIO_LIBRE,
    "Bifurcacion": TIPO_BIFURCACION,
    "Bifurcación": TIPO_BIFURCACION,
    "Intermedio Ordenado": TIPO_INTERMEDIO_ORDENADO,
}

# Mapeo tipo de punto -> forma geométrica (según especificación)
# Inicio: círculo, Final: cuadrado, Bifurcación: triángulo,
# Intermedio ordenado: rombo, Intermedio libre: pentágono
TIPO_PUNTO_TO_SHAPE: Dict[str, str] = {
    TIPO_INICIO: SHAPE_CIRCLE,
    TIPO_FINAL: SHAPE_SQUARE,
    TIPO_BIFURCACION: SHAPE_TRIANGLE,
    TIPO_INTERMEDIO_ORDENADO: SHAPE_RHOMBUS,
    TIPO_INTERMEDIO_LIBRE: SHAPE_PENTAGON,
}

# Labels para ComboBox
LABELS_TIPO_PUNTO: List[str] = [
    "Inicio",
    "Final",
    "Intermedio Libre",
    "Bifurcacion",
    "Intermedio Ordenado",
]

# Modos de camino
CAMINO_ORDENADO = 0
CAMINO_LIBRE = 1

# Detección visual de puntos comunes entre caminos
COMMON_POINT_TOLERANCE_MM = 5.0
COMMON_POINT_HALO_SCALE = 1.35
COMMON_POINT_COLOR_ID = 1


def label_to_tipo(label: str) -> str:
    """Convierte el valor del ComboBox (label) a key interna."""
    return LABEL_TO_TIPO.get(str(label or "").strip(), TIPO_INICIO)


def get_shape_for_tipo(tipo: str) -> str:
    """Devuelve la forma geométrica para un tipo de punto."""
    return TIPO_PUNTO_TO_SHAPE.get(tipo, SHAPE_CIRCLE)
