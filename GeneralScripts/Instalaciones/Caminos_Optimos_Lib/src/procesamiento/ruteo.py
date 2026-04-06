"""
Calculo de ruta e insercion de conectores diagonales.
"""

import math
from typing import List, Tuple

from ..modelos.punto import Punto3D
from ..modelos.obstaculo import Obstaculo
from ..algoritmos.general import calcular_ruta_general
from ..algoritmos.general.geometria import (
    crear_bbox, segmento_cruza_bbox, validar_autocruce,
    asignar_ids, eliminar_puntos_colineales,
)
from ..algoritmos.general.estrategias import _calcular_desplazamiento_salto
from ..algoritmos.general.angulos import calcular_direcciones_validas
from .entrada import EntradaProcesada
from .geometria_techo import calcular_z_eje


MAX_INTENTOS_RUTA = 5


def calcular_ruta(entrada: EntradaProcesada) -> List[Punto3D]:
    """Ejecuta el algoritmo de pathfinding con reintentos ante colisiones."""
    radio_tubo = entrada.config_subtipo['radio']
    subtipo_obj = entrada.config_subtipo['subtipo_obj']
    angulos_codo = subtipo_obj.angulos_permitidos if subtipo_obj else [45]
    
    # Calcular limites XY del techo para restringir el camino
    techo_xs = [v[0] for v in entrada.vertices_techo]
    techo_ys = [v[1] for v in entrada.vertices_techo]
    techo_bounds = (min(techo_xs), max(techo_xs), min(techo_ys), max(techo_ys))
    techo_z = min(v[2] for v in entrada.vertices_techo)
    
    mejor_camino = None
    
    for intento_ruta in range(MAX_INTENTOS_RUTA):
        camino = calcular_ruta_general(
            inicio=entrada.inicio,
            fin=entrada.fin,
            puntos_obligatorios=entrada.puntos_obligatorios,
            puntos_libres=entrada.puntos_libres,
            obstaculos=entrada.obstaculos,
            radio_tubo=radio_tubo,
            angulos_codo=angulos_codo,
            techo_bounds=techo_bounds,
            techo_z=techo_z
        )
        
        # Validacion rapida: colisiones + auto-cruce
        tiene_colision = _tiene_colision_rapida(camino, entrada.obstaculos, radio_tubo)
        
        margen = subtipo_obj.margen_seguridad_mm if subtipo_obj else 10.0
        clearance_rapido = radio_tubo + margen
        autocruces_rapido = validar_autocruce(camino, clearance_rapido)
        
        if not tiene_colision and not autocruces_rapido:
            return camino
        
        # Guardar el mejor intento por si todos fallan
        if mejor_camino is None:
            mejor_camino = camino
        
        if intento_ruta < MAX_INTENTOS_RUTA - 1:
            print(f"  Reintentando ruta completa ({intento_ruta + 2}/{MAX_INTENTOS_RUTA})...")
    
    return mejor_camino


def _tiene_colision_rapida(
    camino: List[Punto3D],
    obstaculos: List[Obstaculo],
    radio_tubo: float,
) -> bool:
    """Verifica si hay colision con algun obstaculo (chequeo rapido)."""
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i+1]
        for obs in obstaculos:
            bb = crear_bbox(obs, radio_tubo)
            modo = obs.modo if isinstance(obs.modo, list) else [obs.modo]
            if 'rodear' in modo:
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                    return True
            else:
                bb_real = {
                    'x_min': bb.get('x_real_min', bb['x_min']),
                    'x_max': bb.get('x_real_max', bb['x_max']),
                    'y_min': bb.get('y_real_min', bb['y_min']),
                    'y_max': bb.get('y_real_max', bb['y_max']),
                    'z_min': bb.get('z_real_min', bb['z_min']),
                    'z_max': bb.get('z_real_max', bb['z_max']),
                }
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb_real):
                    return True
    return False


def _angulo_3d(p_antes, cx, cy, cz, p_despues):
    """Calcula angulo entre vectores p_antes->conn y conn->p_despues."""
    v1 = [cx - p_antes.x, cy - p_antes.y, cz - p_antes.z]
    v2 = [p_despues.x - cx, p_despues.y - cy, p_despues.z - cz]
    n1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    n2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
    if n1 < 0.1 or n2 < 0.1:
        return None
    dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    cos_a = max(-1.0, min(1.0, dot / (n1 * n2)))
    return math.degrees(math.acos(cos_a))


def _corregir_angulo_conector(p_antes, p_conn, p_despues, angulo_codo,
                              vertices_techo, subtipo):
    """
    Ajusta p_conn en XY (con Z recalculado del techo) para que el angulo 3D
    entre p_antes->p_conn y p_conn->p_despues sea exactamente angulo_codo.
    Usa gradiente numerico (Newton) para convergencia rapida.
    """
    cx, cy = p_conn.x, p_conn.y

    # Direccion de ajuste en XY: usar el vector con mayor componente horizontal
    v1_xy = [cx - p_antes.x, cy - p_antes.y]
    v2_xy = [p_despues.x - cx, p_despues.y - cy]
    n1_xy = math.sqrt(v1_xy[0]**2 + v1_xy[1]**2)
    n2_xy = math.sqrt(v2_xy[0]**2 + v2_xy[1]**2)

    if n2_xy >= n1_xy and n2_xy > 0.1:
        dxy = [v2_xy[0]/n2_xy, v2_xy[1]/n2_xy]
    elif n1_xy > 0.1:
        dxy = [v1_xy[0]/n1_xy, v1_xy[1]/n1_xy]
    else:
        return p_conn

    for _ in range(20):
        cz = calcular_z_eje(cx, cy, vertices_techo, subtipo)
        ang = _angulo_3d(p_antes, cx, cy, cz, p_despues)
        if ang is None:
            break

        error = ang - angulo_codo
        if abs(error) <= 0.001:
            break

        # Gradiente numerico: medir cambio de angulo por mm de desplazamiento XY
        eps = 0.1
        cz_e = calcular_z_eje(cx + eps*dxy[0], cy + eps*dxy[1], vertices_techo, subtipo)
        ang_e = _angulo_3d(p_antes, cx + eps*dxy[0], cy + eps*dxy[1], cz_e, p_despues)
        if ang_e is None:
            break

        grad = (ang_e - ang) / eps
        if abs(grad) < 1e-6:
            break

        delta = -error / grad
        cx += delta * dxy[0]
        cy += delta * dxy[1]

    cz = calcular_z_eje(cx, cy, vertices_techo, subtipo)
    return Punto3D(x=cx, y=cy, z=cz, id=p_conn.id)


def insertar_conectores(
    camino: List[Punto3D],
    entrada: EntradaProcesada,
    camino_idx: int = None,
) -> Tuple[List[Punto3D], int, int]:
    """
    Inserta conectores diagonales si A o B no estan en la cota del techo.
    
    Returns:
        (camino_modificado, num_conectores_inicio, num_conectores_fin)
    """
    subtipo_obj = entrada.config_subtipo['subtipo_obj']
    angulos_codo = subtipo_obj.angulos_permitidos if subtipo_obj else [45]
    direcciones_validas = calcular_direcciones_validas(angulos_codo)
    ang_conector = max(angulos_codo)
    
    z_cota_inicio = entrada.inicio.z
    z_cota_fin = entrada.fin.z
    delta_z_a = abs(z_cota_inicio - entrada.inicio_real.z)
    delta_z_b = abs(entrada.fin_real.z - z_cota_fin)
    num_conectores_inicio = 0
    num_conectores_fin = 0
    
    def _snap_direccion(ang_deg, dirs):
        ang_deg = ang_deg % 360
        return min(dirs, key=lambda d: min(abs(d - ang_deg), 360 - abs(d - ang_deg)))
    
    if delta_z_a > 1 and len(camino) >= 2:
        h_a = _calcular_desplazamiento_salto(delta_z_a, angulos_codo)
        # Usar direccion del primer segmento del camino
        dx1 = camino[1].x - camino[0].x if len(camino) >= 2 else entrada.fin.x - entrada.inicio.x
        dy1 = camino[1].y - camino[0].y if len(camino) >= 2 else entrada.fin.y - entrada.inicio.y
        if abs(dx1) < 0.5 and abs(dy1) < 0.5:
            dx1 = entrada.fin.x - entrada.inicio.x
            dy1 = entrada.fin.y - entrada.inicio.y
        dir_a_deg = math.degrees(math.atan2(dy1, dx1))
        dir_a_snap = _snap_direccion(dir_a_deg, direcciones_validas)
        dir_a_rad = math.radians(dir_a_snap)
        
        landing_x = entrada.inicio_real.x + h_a * math.cos(dir_a_rad)
        landing_y = entrada.inicio_real.y + h_a * math.sin(dir_a_rad)
        z_landing = calcular_z_eje(landing_x, landing_y, entrada.vertices_techo, entrada.subtipo)
        
        landing_a = Punto3D(x=landing_x, y=landing_y, z=z_landing, id='C0')
        camino[0] = landing_a
        camino.insert(0, Punto3D(x=entrada.inicio_real.x, y=entrada.inicio_real.y, z=entrada.inicio_real.z))
        # Corregir angulo 3D en C0 (entre A->C0 y C0->C1)
        camino[1] = _corregir_angulo_conector(
            camino[0], camino[1], camino[2], ang_conector,
            entrada.vertices_techo, entrada.subtipo)
        num_conectores_inicio = 1
    
    if delta_z_b > 1 and len(camino) >= 2:
        h_b = _calcular_desplazamiento_salto(delta_z_b, angulos_codo)
        # Usar direccion del ultimo segmento del camino
        dx_last = camino[-1].x - camino[-2].x
        dy_last = camino[-1].y - camino[-2].y
        if abs(dx_last) < 0.5 and abs(dy_last) < 0.5:
            dx_last = entrada.fin.x - entrada.inicio.x
            dy_last = entrada.fin.y - entrada.inicio.y
        dir_b_deg = math.degrees(math.atan2(dy_last, dx_last))
        dir_b_snap = _snap_direccion(dir_b_deg, direcciones_validas)
        dir_b_rad = math.radians(dir_b_snap)
        
        takeoff_x = entrada.fin_real.x - h_b * math.cos(dir_b_rad)
        takeoff_y = entrada.fin_real.y - h_b * math.sin(dir_b_rad)
        z_takeoff = calcular_z_eje(takeoff_x, takeoff_y, entrada.vertices_techo, entrada.subtipo)
        
        takeoff_b = Punto3D(x=takeoff_x, y=takeoff_y, z=z_takeoff, id='C')
        camino[-1] = takeoff_b
        camino.append(Punto3D(x=entrada.fin_real.x, y=entrada.fin_real.y, z=entrada.fin_real.z))
        # Corregir angulo 3D en C_takeoff (entre C_prev->C_takeoff y C_takeoff->B)
        camino[-2] = _corregir_angulo_conector(
            camino[-3], camino[-2], camino[-1], ang_conector,
            entrada.vertices_techo, entrada.subtipo)
        num_conectores_fin = 1
    
    # Limpieza final de puntos colineales (near-180°) que sobrevivieron
    # al pathfinding o fueron introducidos por conectores/snap.
    # Usar misma tolerancia que validacion (0.01°) para consistencia
    protegidos = (entrada.puntos_obligatorios or []) + (entrada.puntos_libres or [])
    camino = eliminar_puntos_colineales(camino, tolerancia=5.0, puntos_protegidos=protegidos)
    
    # Re-asignar IDs tras insertar conectores
    asignar_ids(camino, entrada.puntos_obligatorios, entrada.puntos_libres, camino_idx=camino_idx)
    
    return camino, num_conectores_inicio, num_conectores_fin
