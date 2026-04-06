"""
Validacion de rutas: angulos, longitudes minimas, colisiones y auto-cruce.
"""

import numpy as np
from typing import List

from ..modelos.punto import Punto3D
from ..modelos.obstaculo import Obstaculo
from ..reportes import Segmento
from ..algoritmos.general.geometria import (
    crear_bbox, segmento_cruza_bbox, validar_autocruce,
)
from ..algoritmos.general.angulos import validar_angulo
from .entrada import EntradaProcesada


def validar_ruta(
    camino: List[Punto3D],
    segmentos: List[Segmento],
    entrada: EntradaProcesada,
    num_conectores_inicio: int,
    num_conectores_fin: int,
) -> bool:
    """
    Valida la ruta: angulos, longitudes minimas, colisiones y auto-cruce.
    Imprime los errores encontrados.
    
    Returns:
        True si la ruta es valida.
    """
    subtipo_obj = entrada.config_subtipo['subtipo_obj']
    radio_tubo = entrada.config_subtipo['radio']
    angulos_codo = subtipo_obj.angulos_permitidos if subtipo_obj else [45]
    longitud_minima = subtipo_obj.longitud_minima_mm if subtipo_obj else 150.0
    tolerancia_angulo = 0.01  # grados de tolerancia estricta
    
    ruta_valida = True
    angulos_incorrectos = []
    segmentos_cortos = []
    
    # Validar longitud minima de cada segmento (saltar conectores)
    for i, seg in enumerate(segmentos):
        if i < num_conectores_inicio or i >= len(segmentos) - num_conectores_fin:
            continue
        # Usar tolerancia de 0.5mm para evitar problemas de precision numerica
        if seg.longitud < longitud_minima - 0.5:
            ruta_valida = False
            segmentos_cortos.append((i+1, seg.longitud))
    
    # Validar angulos entre segmentos consecutivos (en 3D, incluye conectores)
    for i in range(len(camino) - 2):
        p1, p2, p3 = camino[i], camino[i+1], camino[i+2]
        
        # Usar vectores 3D para validación correcta
        v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 < 1 or norm2 < 1:
            continue
        
        cos_ang = np.dot(v1, v2) / (norm1 * norm2)
        cos_ang = np.clip(cos_ang, -1, 1)
        angulo = np.degrees(np.arccos(cos_ang))
        
        # Validacion general: aceptar angulos de codo permitidos y 180° (recto)
        es_valido = validar_angulo(angulo, angulos_codo, tolerancia_angulo)
        if not es_valido:
            ruta_valida = False
            angulo_interno = 180 - angulo
            angulos_incorrectos.append((i+1, p2.id, angulo_interno))
    
    # Validar auto-cruce (la ruta no debe cruzarse consigo misma)
    margen = subtipo_obj.margen_seguridad_mm if subtipo_obj else 10.0
    clearance_cruce = radio_tubo + margen
    autocruces = validar_autocruce(camino, clearance_cruce)
    if autocruces:
        ruta_valida = False
    
    # Validar colisiones con obstaculos
    colisiones_obs = []
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i+1]
        for obs in entrada.obstaculos:
            bb = crear_bbox(obs, radio_tubo)
            modo = obs.modo if isinstance(obs.modo, list) else [obs.modo]
            if 'rodear' in modo:
                # Rodear: usar bbox expandido (nunca debe cruzar)
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                    colisiones_obs.append(f"Seg {p1.id}-{p2.id} cruza {obs.id}")
            else:
                # Saltar/bajar: usar bbox real (cuerpo fisico, sin expansion)
                bb_real = {
                    'x_min': bb.get('x_real_min', bb['x_min']),
                    'x_max': bb.get('x_real_max', bb['x_max']),
                    'y_min': bb.get('y_real_min', bb['y_min']),
                    'y_max': bb.get('y_real_max', bb['y_max']),
                    'z_min': bb.get('z_real_min', bb['z_min']),
                    'z_max': bb.get('z_real_max', bb['z_max']),
                }
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb_real):
                    colisiones_obs.append(f"Seg {p1.id}-{p2.id} cruza {obs.id}")
    if colisiones_obs:
        ruta_valida = False
    
    # Mostrar errores si los hay
    if colisiones_obs:
        print(f"\n*** ERROR: COLISION CON OBSTACULOS ***")
        for v in colisiones_obs:
            print(f"  - {v}")
    
    if autocruces:
        print(f"\n*** ERROR: AUTO-CRUCE DETECTADO (clearance {clearance_cruce:.0f}mm) ***")
        for v in autocruces:
            print(f"  - {v}")
    
    if segmentos_cortos:
        print(f"\n*** ERROR: SEGMENTOS MUY CORTOS (min {longitud_minima}mm) ***")
        for idx, lon in segmentos_cortos:
            print(f"  - Segmento {idx}: {lon:.1f}mm")
    
    if angulos_incorrectos:
        angulos_internos_validos = [180 - c for c in angulos_codo] + [180]
        print(f"\n*** ERROR: ANGULOS INCORRECTOS (internos válidos: {angulos_internos_validos}°) ***")
        for idx, pid, ang in angulos_incorrectos:
            print(f"  - Punto {pid} (seg {idx}): {ang:.1f}°")
    
    if not ruta_valida:
        print(f"\n*** RUTA INVALIDA - NO SE PUEDE USAR ***\n")
    
    return ruta_valida
