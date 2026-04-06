"""
Helpers de geometria de techo y configuracion de subtipos.

Funciones para calcular normales, proyecciones Z, y generar subdivisiones IS.
"""

import numpy as np
from typing import List, Dict, Tuple

from ..core.gestor_configuracion import obtener_gestor_configuracion


# Dimensiones IS desde config/dimensiones_is.json
_gestor = obtener_gestor_configuracion()
_dim_is = _gestor.dimensiones_is
ANCHO_MIN_IS = _dim_is.get('ancho_min_mm', 1450)
ANCHO_MAX_IS = _dim_is.get('ancho_max_mm', 5650)
ALTO_MIN_IS = _dim_is.get('alto_min_mm', 1450)
ALTO_MAX_IS = _dim_is.get('alto_max_mm', 2150)
MARGEN_IS = _dim_is.get('margen_entre_is_mm', 50)


def calcular_normal_techo(vertices: List[List[float]]) -> Tuple[float, float, float]:
    """Calcula la normal del plano del techo."""
    v0 = np.array(vertices[0])
    v1 = np.array(vertices[1])
    v2 = np.array(vertices[2])
    vec1 = v1 - v0
    vec2 = v2 - v0
    normal = np.cross(vec1, vec2)
    norma = np.linalg.norm(normal)
    if norma > 0.001:
        normal = normal / norma
    if normal[2] < 0:
        normal = -normal
    return tuple(normal)


def calcular_z_en_plano(x: float, y: float, vertices: List[List[float]]) -> float:
    """Calcula Z para un punto (x,y) sobre el plano del techo."""
    normal = calcular_normal_techo(vertices)
    punto_plano = np.array(vertices[0])
    a, b, c = normal
    if abs(c) < 0.001:
        return punto_plano[2]
    d = np.dot(normal, punto_plano)
    z = (d - a * x - b * y) / c
    return z


def obtener_config_subtipo(subtipo: str) -> dict:
    """
    Obtiene la configuracion del subtipo desde el GestorConfiguracion.
    Esta es la UNICA fuente de verdad para los angulos permitidos.
    
    offset_eje = distancia_techo + radio del tubo
    """
    gestor = obtener_gestor_configuracion()
    subtipo_obj = gestor.obtener_subtipo(subtipo)
    
    if subtipo_obj:
        return {
            'radio': subtipo_obj.dimensiones.radio_mm,
            'offset_eje': subtipo_obj.distancia_techo_mm + subtipo_obj.dimensiones.radio_mm,
            'angulo_giro': subtipo_obj.angulo_movimiento,
            'subtipo_obj': subtipo_obj
        }
    
    # Fallback para subtipos no configurados
    radio_fallback = 37.5
    distancia_techo_fallback = 110.0
    print(f"  ADVERTENCIA: subtipo '{subtipo}' no encontrado, usando fallback (radio={radio_fallback}mm)")
    return {
        'radio': radio_fallback,
        'offset_eje': distancia_techo_fallback + radio_fallback,
        'angulo_giro': 90,
        'subtipo_obj': None
    }


def calcular_z_eje(x: float, y: float, vertices: List[List[float]], subtipo: str) -> float:
    """Calcula Z del eje del tubo (Z_techo + offset) - tubería va POR ENCIMA del techo."""
    z_techo = calcular_z_en_plano(x, y, vertices)
    config = obtener_config_subtipo(subtipo)
    offset = config['offset_eje']
    return z_techo + offset


def generar_is_cubriendo_techo(vertices_techo: List[List[float]]) -> List[Dict]:
    """Genera subdivisiones IS que cubran todo el techo."""
    xs = [v[0] for v in vertices_techo]
    ys = [v[1] for v in vertices_techo]
    
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    
    ancho_techo = x_max - x_min
    alto_techo = y_max - y_min
    
    # Calcular numero de divisiones
    n_cols = max(1, int(np.ceil(ancho_techo / ANCHO_MAX_IS)))
    n_rows = max(1, int(np.ceil(alto_techo / ALTO_MAX_IS)))
    
    ancho_is = ancho_techo / n_cols
    alto_is = alto_techo / n_rows
    
    subdivisiones = []
    contador = 1
    
    for row in range(n_rows):
        for col in range(n_cols):
            x0 = x_min + col * ancho_is + MARGEN_IS
            x1 = x_min + (col + 1) * ancho_is - MARGEN_IS
            y0 = y_min + row * alto_is + MARGEN_IS
            y1 = y_min + (row + 1) * alto_is - MARGEN_IS
            
            vertices_is = [
                [x0, y0, calcular_z_en_plano(x0, y0, vertices_techo)],
                [x1, y0, calcular_z_en_plano(x1, y0, vertices_techo)],
                [x1, y1, calcular_z_en_plano(x1, y1, vertices_techo)],
                [x0, y1, calcular_z_en_plano(x0, y1, vertices_techo)],
            ]
            
            subdivisiones.append({
                'id': f'IS{contador}',
                'vertices': vertices_is
            })
            contador += 1
    
    return subdivisiones
