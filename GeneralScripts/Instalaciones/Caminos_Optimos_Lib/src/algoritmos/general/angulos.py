"""
Calculo de direcciones validas y descomposicion de rutas para angulos arbitrarios.

Dado un conjunto de angulos de codo permitidos (ej: [45], [90], [45, 90], [60]),
calcula las direcciones de movimiento validas y descompone desplazamientos
en segmentos que respeten las restricciones angulares.
"""

import math
from typing import List, Tuple, Optional
from ...modelos import Punto3D


def calcular_direcciones_validas(angulos_codo: List[int]) -> List[float]:
    """
    Calcula el conjunto de direcciones de movimiento validas en el plano XY.
    
    Para un angulo de codo θ, las direcciones validas son multiplos de θ.
    180° (linea recta) siempre esta permitido.
    
    Args:
        angulos_codo: Lista de angulos de codo permitidos (ej: [45], [90], [60])
    
    Returns:
        Lista de direcciones en grados [0, 360), ordenadas
    """
    if not angulos_codo:
        return [0.0, 90.0, 180.0, 270.0]
    
    # El paso minimo es el GCD de todos los angulos
    paso = angulos_codo[0]
    for ang in angulos_codo[1:]:
        paso = math.gcd(paso, ang)
    
    # Generar todas las direcciones como multiplos del paso
    direcciones = []
    d = 0.0
    while d < 360:
        direcciones.append(d)
        d += paso
    
    return direcciones


def calcular_angulos_giro_validos(angulos_codo: List[int]) -> List[float]:
    """
    Calcula los angulos de giro validos entre segmentos consecutivos.
    
    El angulo de giro es el angulo entre vectores de direccion consecutivos.
    Para un codo de θ°, el angulo entre vectores = θ° (cambio de direccion).
    0° (sin cambio = linea recta) siempre esta permitido.
    
    Args:
        angulos_codo: Lista de angulos de codo permitidos
    
    Returns:
        Lista de angulos de giro validos (entre vectores)
    """
    validos = {0.0, 180.0}  # Linea recta siempre permitida (0° entre vectores = 180° interno)
    
    for ang in angulos_codo:
        # El angulo entre vectores consecutivos = angulo del codo
        validos.add(float(ang))
        # Tambien es valido 180° - ang (el complemento)
        complemento = 180.0 - ang
        if complemento > 0:
            validos.add(complemento)
    
    return sorted(validos)


def angulo_entre_vectores(dx1, dy1, dz1, dx2, dy2, dz2) -> float:
    """
    Calcula el angulo entre dos vectores 3D.
    
    Returns:
        Angulo en grados [0, 180]
    """
    len1 = math.sqrt(dx1**2 + dy1**2 + dz1**2)
    len2 = math.sqrt(dx2**2 + dy2**2 + dz2**2)
    
    if len1 < 0.001 or len2 < 0.001:
        return 0.0
    
    cos_ang = (dx1*dx2 + dy1*dy2 + dz1*dz2) / (len1 * len2)
    cos_ang = max(-1.0, min(1.0, cos_ang))
    return math.degrees(math.acos(cos_ang))


def angulo_xy(dx: float, dy: float) -> Optional[float]:
    """
    Calcula el angulo en el plano XY (0-360).
    Retorna None si el desplazamiento es nulo.
    """
    if abs(dx) < 0.001 and abs(dy) < 0.001:
        return None
    ang = math.degrees(math.atan2(dy, dx))
    if ang < 0:
        ang += 360
    return ang


def direccion_mas_cercana(angulo: float, direcciones: List[float]) -> float:
    """Encuentra la direccion valida mas cercana a un angulo dado."""
    mejor = direcciones[0]
    mejor_diff = 999
    for d in direcciones:
        diff = abs(angulo - d)
        if diff > 180:
            diff = 360 - diff
        if diff < mejor_diff:
            mejor_diff = diff
            mejor = d
    return mejor


def descomponer_desplazamiento(
    dx: float, dy: float,
    direcciones: List[float]
) -> List[Tuple[float, float, float]]:
    """
    Descompone un desplazamiento (dx, dy) en segmentos usando solo direcciones validas.
    
    Busca la combinacion de 1 o 2 direcciones que alcance el destino.
    Si no es posible con 2, usa 3 segmentos.
    
    Args:
        dx, dy: Desplazamiento objetivo
        direcciones: Direcciones validas en grados
    
    Returns:
        Lista de (dx_seg, dy_seg, longitud) para cada segmento
    """
    dist = math.sqrt(dx**2 + dy**2)
    if dist < 1:
        return []
    
    # Caso 1: Desplazamiento alineado con una direccion valida
    ang_objetivo = math.degrees(math.atan2(dy, dx))
    if ang_objetivo < 0:
        ang_objetivo += 360
    
    for d in direcciones:
        diff = abs(ang_objetivo - d)
        if diff > 180:
            diff = 360 - diff
        if diff < 0.5:  # Alineado
            return [(dx, dy, dist)]
    
    # Caso 2: Descomponer en 2 segmentos usando 2 direcciones
    mejor_combo = None
    mejor_longitud = float('inf')
    
    for i, d1 in enumerate(direcciones):
        r1 = math.radians(d1)
        ux1, uy1 = math.cos(r1), math.sin(r1)
        
        for d2 in direcciones:
            if d1 == d2:
                continue
            r2 = math.radians(d2)
            ux2, uy2 = math.cos(r2), math.sin(r2)
            
            # Resolver: t1 * (ux1, uy1) + t2 * (ux2, uy2) = (dx, dy)
            det = ux1 * uy2 - ux2 * uy1
            if abs(det) < 0.001:
                continue  # Direcciones paralelas
            
            t1 = (dx * uy2 - dy * ux2) / det
            t2 = (ux1 * dy - uy1 * dx) / det
            
            if t1 < 0 or t2 < 0:
                continue  # Solo segmentos en direccion positiva
            
            longitud_total = t1 + t2
            if longitud_total < mejor_longitud:
                # Verificar que ambos segmentos tengan longitud minima
                if t1 >= 1 and t2 >= 1:
                    mejor_longitud = longitud_total
                    mejor_combo = [
                        (ux1 * t1, uy1 * t1, t1),
                        (ux2 * t2, uy2 * t2, t2)
                    ]
    
    if mejor_combo:
        return mejor_combo
    
    # Caso 3: Fallback - usar la direccion mas cercana + correccion ortogonal
    d_cercana = direccion_mas_cercana(ang_objetivo, direcciones)
    r = math.radians(d_cercana)
    ux, uy = math.cos(r), math.sin(r)
    
    # Proyectar sobre la direccion elegida
    proj = dx * ux + dy * uy
    if proj < 0:
        # Direccion opuesta
        d_cercana = (d_cercana + 180) % 360
        r = math.radians(d_cercana)
        ux, uy = math.cos(r), math.sin(r)
        proj = dx * ux + dy * uy
    
    seg1_dx = ux * proj
    seg1_dy = uy * proj
    
    # Residuo
    res_dx = dx - seg1_dx
    res_dy = dy - seg1_dy
    res_dist = math.sqrt(res_dx**2 + res_dy**2)
    
    resultado = []
    if proj > 1:
        resultado.append((seg1_dx, seg1_dy, proj))
    if res_dist > 1:
        resultado.append((res_dx, res_dy, res_dist))
    
    return resultado if resultado else [(dx, dy, dist)]


def crear_ruta_directa(
    inicio: Punto3D,
    fin: Punto3D,
    direcciones: List[float]
) -> List[Punto3D]:
    """
    Crea una ruta directa entre dos puntos usando solo direcciones validas.
    
    Si los puntos no estan alineados con una direccion valida,
    descompone en segmentos intermedios.
    
    Args:
        inicio: Punto de partida
        fin: Punto de destino
        direcciones: Direcciones validas
    
    Returns:
        Lista de puntos que forman la ruta
    """
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    
    segmentos = descomponer_desplazamiento(dx, dy, direcciones)
    
    if not segmentos:
        return [inicio, fin]
    
    if len(segmentos) == 1:
        return [inicio, fin]
    
    # Construir puntos intermedios
    ruta = [inicio]
    x_actual, y_actual = inicio.x, inicio.y
    
    for i, (sdx, sdy, slen) in enumerate(segmentos[:-1]):
        x_actual += sdx
        y_actual += sdy
        ruta.append(Punto3D(
            id="C",
            x=x_actual,
            y=y_actual,
            z=inicio.z  # Mantener Z del inicio (ajuste Z se hace en estrategias)
        ))
    
    ruta.append(fin)
    return ruta


def validar_angulo(angulo: float, angulos_codo: List[int], tolerancia: float = 0.01) -> bool:
    """
    Verifica si un angulo entre vectores es valido segun los codos permitidos.
    
    El angulo entre vectores (arccos del dot product) es:
    - 0° = linea recta (180° interno, sin cambio de direccion)
    - θ° = codo de θ° (180°-θ° interno)
    
    Angulos validos entre vectores:
    - ~0° (colineal/recto)
    - Cada angulo de codo directamente
    
    Ejemplos (angulos internos que se muestran al usuario):
    - [45] -> internos validos: 135°, 180° -> entre vectores: 45°, 0°
    - [90] -> internos validos: 90°, 180° -> entre vectores: 90°, 0°
    - [45,90] -> internos validos: 90°, 135°, 180° -> entre vectores: 90°, 45°, 0°
    
    Args:
        angulo: Angulo medido entre vectores (grados, 0=recto, 90=perpendicular)
        angulos_codo: Lista de angulos de codo permitidos
        tolerancia: Tolerancia en grados
    
    Returns:
        True si es valido
    """
    # Linea recta (0° entre vectores = 180° interno)
    if angulo <= tolerancia:
        return True
    
    # Verificar cada angulo de codo directamente
    for codo in angulos_codo:
        if abs(angulo - codo) <= tolerancia:
            return True
    
    return False
