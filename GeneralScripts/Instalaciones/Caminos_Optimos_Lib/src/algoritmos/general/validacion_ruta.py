"""
Validacion de subrutas: angulos, longitudes, colisiones, auto-cruce y bounds.
"""

import math
import numpy as np
from typing import List

from ...modelos import Punto3D
from .geometria import (
    LONGITUD_MINIMA, MARGEN_OBSTACULO,
    segmento_cruza_bbox, validar_autocruce,
)
from .angulos import validar_angulo


def validar_subruta_completa(ruta, angulos_codo, dir_entrada=None, tolerancia=0.01,
                              bboxes_rodear=None, bboxes_saltar=None, radio_tubo=0,
                              techo_bounds=None, ruta_previa=None):
    """Valida subruta completa: angulos, longitudes, colisiones, auto-cruce, bounds."""
    if len(ruta) < 2:
        return True
    
    # 1. Validar longitudes minimas
    for i in range(len(ruta) - 1):
        d = ruta[i].distancia_a(ruta[i+1])
        if d < LONGITUD_MINIMA - 0.5 and d > 1:
            return False
    
    # 2. Validar angulos
    if not validar_angulos_subruta(ruta, angulos_codo, dir_entrada, tolerancia):
        return False
    
    # 3. Validar que no cruza obstaculos "rodear" (solo segmentos XY, saltar es permitido)
    if bboxes_rodear:
        for i in range(len(ruta) - 1):
            p1, p2 = ruta[i], ruta[i+1]
            for bb in bboxes_rodear:
                if bb.get('id') == 'virtual':
                    continue
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                    return False
    
    # 3b. Validar que segmentos HORIZONTALES no penetran cuerpo real de
    #     obstaculos saltar/bajar.  Segmentos con cambio Z grande son transiciones
    #     de salto/bajada y pueden pasar cerca del obstaculo legitimamente.
    if bboxes_saltar:
        for i in range(len(ruta) - 1):
            p1, p2 = ruta[i], ruta[i+1]
            if abs(p1.z - p2.z) > 50:
                continue  # transicion vertical de salto/bajada — exento
            for bb in bboxes_saltar:
                if bb.get('id') == 'virtual':
                    continue
                bb_real = {
                    'x_min': bb.get('x_real_min', bb['x_min']),
                    'x_max': bb.get('x_real_max', bb['x_max']),
                    'y_min': bb.get('y_real_min', bb['y_min']),
                    'y_max': bb.get('y_real_max', bb['y_max']),
                    'z_min': bb.get('z_real_min', bb['z_min']),
                    'z_max': bb.get('z_real_max', bb['z_max']),
                }
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb_real):
                    return False
    
    # 4. Validar auto-cruce (segmentos no adyacentes a distancia >= radio+10mm)
    clearance = radio_tubo + MARGEN_OBSTACULO
    if clearance > 0 and len(ruta) >= 4:
        violaciones = validar_autocruce(ruta, clearance)
        if violaciones:
            return False
    
    # 5. Validar que no cruza tramos previos de la ruta ya planificada
    if ruta_previa and len(ruta_previa) >= 2 and clearance > 0:
        from .geometria import distancia_minima_segmentos_3d
        for i in range(len(ruta) - 1):
            p1, p2 = ruta[i], ruta[i+1]
            for j in range(len(ruta_previa) - 1):
                q1, q2 = ruta_previa[j], ruta_previa[j+1]
                # Ignorar segmentos que comparten endpoint (union entre tramos)
                if (abs(p1.x - q2.x) < 1 and abs(p1.y - q2.y) < 1):
                    continue
                # Pre-filtro rapido por bbox
                if (max(p1.x, p2.x) + clearance < min(q1.x, q2.x) - clearance or
                    min(p1.x, p2.x) - clearance > max(q1.x, q2.x) + clearance or
                    max(p1.y, p2.y) + clearance < min(q1.y, q2.y) - clearance or
                    min(p1.y, p2.y) - clearance > max(q1.y, q2.y) + clearance or
                    max(p1.z, p2.z) + clearance < min(q1.z, q2.z) - clearance or
                    min(p1.z, p2.z) - clearance > max(q1.z, q2.z) + clearance):
                    continue
                d = distancia_minima_segmentos_3d(p1, p2, q1, q2)
                if d < clearance:
                    return False
    
    # 6. Validar dentro del techo
    if techo_bounds:
        x_min_t, x_max_t, y_min_t, y_max_t = techo_bounds
        for p in ruta:
            if p.x < x_min_t - 1 or p.x > x_max_t + 1 or p.y < y_min_t - 1 or p.y > y_max_t + 1:
                return False
    
    return True


def validar_angulos_subruta(ruta, angulos_codo, dir_entrada=None, tolerancia=0.01):
    """Valida angulos entre segmentos consecutivos."""
    if len(ruta) < 2:
        return True
    
    # Validar transicion con dir_entrada
    if dir_entrada is not None and len(ruta) >= 2:
        dx = ruta[1].x - ruta[0].x
        dy = ruta[1].y - ruta[0].y
        if abs(dx) > 0.5 or abs(dy) > 0.5:
            dir_primer = math.degrees(math.atan2(dy, dx)) % 360
            diff = abs(dir_entrada - dir_primer) % 360
            if diff > 180:
                diff = 360 - diff
            # diff es el angulo entre vectores
            if diff > tolerancia:
                es_valido = False
                for codo in angulos_codo:
                    if abs(diff - codo) <= tolerancia:
                        es_valido = True
                        break
                if not es_valido:
                    return False
    
    # Validar angulos internos
    for i in range(1, len(ruta) - 1):
        p1, p2, p3 = ruta[i-1], ruta[i], ruta[i+1]
        v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 < 1 or n2 < 1:
            continue
        
        cos_ang = np.clip(np.dot(v1, v2) / (n1 * n2), -1, 1)
        angulo = float(np.degrees(np.arccos(cos_ang)))
        
        if not validar_angulo(angulo, angulos_codo, tolerancia):
            return False
    
    return True
