"""
Estrategias de evasion de obstaculos: saltar, rodear, bajar.

Cada estrategia genera una ruta alternativa que evita un obstaculo
respetando las restricciones angulares del sistema.
"""

import math
from typing import List, Optional
from ...modelos import Punto3D
from .geometria import (
    LONGITUD_MINIMA, MARGEN_OBSTACULO,
    segmento_cruza_bbox, encontrar_obstaculos_en_segmento
)


def calcular_salto(
    inicio: Punto3D,
    fin: Punto3D,
    bbox: dict,
    radio_tubo: float,
    angulos_codo: List[int]
) -> Optional[List[Punto3D]]:
    """
    Calcula ruta que SALTA (pasa por encima) un obstaculo.
    
    La tuberia sube en Z, pasa sobre el obstaculo, y baja de nuevo.
    El perfil del salto depende de los angulos permitidos:
    - 90°: subida/bajada vertical
    - 45°: subida/bajada diagonal (delta_x = delta_z)
    - Otro: subida/bajada con pendiente segun angulo
    
    Args:
        inicio: Punto antes del obstaculo
        fin: Punto despues del obstaculo
        bbox: Bounding box del obstaculo
        radio_tubo: Radio de la tuberia
        angulos_codo: Angulos de codo permitidos
    
    Returns:
        Lista de puntos del salto, o None si no es posible
    """
    margen = radio_tubo + MARGEN_OBSTACULO
    z_real_max = bbox.get('z_real_max', bbox['z_max'] - margen)
    altura_salto = z_real_max + radio_tubo + 10  # clearance minimo
    delta_z = altura_salto - inicio.z
    
    if delta_z <= 0:
        delta_z = 100  # salto minimo
        altura_salto = inicio.z + delta_z
    
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    dist_xy = math.sqrt(dx**2 + dy**2)
    
    if dist_xy < 1:
        return None
    
    # Desplazamiento horizontal del salto segun angulos
    desp_horizontal = _calcular_desplazamiento_salto(delta_z, angulos_codo)
    
    # Usar enfoque DIRECCIONAL: el salto se alinea con la direccion del segmento
    puntos = _salto_direccional(inicio, fin, bbox, margen, delta_z, desp_horizontal, altura_salto,
                                  angulos_codo=angulos_codo)
    
    return _validar_y_limpiar_ruta(puntos, inicio, fin)


def calcular_bajada(
    inicio: Punto3D,
    fin: Punto3D,
    bbox: dict,
    radio_tubo: float,
    angulos_codo: List[int],
    techo_z: float = None
) -> Optional[List[Punto3D]]:
    """
    Calcula ruta que BAJA (pasa por debajo) de un obstaculo.
    
    La tuberia desciende en Z, pasa bajo el obstaculo, y sube de nuevo.
    Es el inverso geometrico del salto.
    
    Args:
        inicio: Punto antes del obstaculo
        fin: Punto despues del obstaculo
        bbox: Bounding box del obstaculo
        radio_tubo: Radio de la tuberia
        angulos_codo: Angulos de codo permitidos
        techo_z: Coordenada Z del techo (limite inferior, no se puede bajar mas)
    
    Returns:
        Lista de puntos de la bajada, o None si no es posible
    """
    margen = radio_tubo + MARGEN_OBSTACULO
    z_real_min = bbox.get('z_real_min', bbox['z_min'] + margen)
    altura_bajada = z_real_min - radio_tubo - 10  # clearance minimo por debajo
    
    # Verificar que la bajada no atraviese el techo
    if techo_z is not None:
        z_minimo_tubo = altura_bajada - radio_tubo  # borde inferior del tubo
        if z_minimo_tubo < techo_z:
            return None  # No hay espacio entre el obstaculo y el techo
    
    delta_z = inicio.z - altura_bajada
    
    if delta_z <= 0:
        return None  # No hay espacio para bajar
    
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    
    if abs(dx) < 1 and abs(dy) < 1:
        return None
    
    dist_xy = math.sqrt(dx**2 + dy**2)
    if dist_xy < 1:
        return None
    
    desp_horizontal = _calcular_desplazamiento_salto(delta_z, angulos_codo)
    
    puntos = _salto_direccional(inicio, fin, bbox, margen, delta_z, desp_horizontal, altura_bajada,
                                  bajar=True, angulos_codo=angulos_codo)
    
    return _validar_y_limpiar_ruta(puntos, inicio, fin)


def calcular_rodeo(
    inicio: Punto3D,
    fin: Punto3D,
    bbox: dict,
    bboxes: List[dict],
    angulos_codo: List[int]
) -> Optional[List[Punto3D]]:
    """
    Calcula ruta que RODEA un obstaculo horizontalmente.
    
    La tuberia se desvia en X o Y para evitar el obstaculo,
    respetando las restricciones angulares.
    
    Intenta rodear por ambos lados y elige la ruta mas corta
    que no cruce otros obstaculos.
    
    Args:
        inicio: Punto antes del obstaculo
        fin: Punto despues del obstaculo
        bbox: Bounding box del obstaculo a rodear
        bboxes: Todos los bounding boxes (para verificar colisiones)
        angulos_codo: Angulos de codo permitidos
    
    Returns:
        Lista de puntos del rodeo, o None si no es posible
    """
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    margen = 100
    
    rutas_candidatas = []
    
    for direccion in [1, -1]:
        ruta = _rodeo_lateral(inicio, fin, bbox, bboxes, angulos_codo, direccion, margen)
        if ruta:
            rutas_candidatas.append(ruta)
    
    if not rutas_candidatas:
        return None
    
    # Elegir la ruta mas corta
    def longitud(ruta):
        total = 0
        for i in range(len(ruta) - 1):
            total += ruta[i].distancia_a(ruta[i + 1])
        return total
    
    rutas_candidatas.sort(key=longitud)
    return rutas_candidatas[0]


# ===== Funciones auxiliares internas =====


def _calcular_desplazamiento_salto(delta_z: float, angulos_codo: List[int]) -> float:
    """
    Calcula el desplazamiento horizontal necesario para un cambio de Z.
    
    Para 90°: desplazamiento = 0 (subida vertical)
    Para 45°: desplazamiento = delta_z (subida a 45°)
    Para otro angulo θ: desplazamiento = delta_z * tan(90° - θ)
    """
    if not angulos_codo:
        return 0
    
    ang = max(angulos_codo)
    
    if ang >= 90:
        return 0
    
    rad = math.radians(90 - ang)
    return delta_z * math.tan(rad)


def _desp_h_con_pendiente(offset: float, angulos_codo: List[int],
                           z_slope: float, es_ascenso: bool = True) -> float:
    """
    Calcula desp_h exacto para transicion de salto con pendiente Z.
    
    Usa marco de referencia inclinado: si la seccion elevada sigue la misma
    pendiente que la linea base, todos los angulos son exactos.
    
    Para ascenso: ratio = (cos(θ)-sin(θ)*s) / (cos(θ)*s+sin(θ))
                  desp_h = ratio * offset / (1 - ratio*s)
    Para descenso: ratio = (cos(θ)+sin(θ)*s) / (sin(θ)-cos(θ)*s)
                   desp_h = ratio * offset / (1 + ratio*s)
    """
    desp_base = _calcular_desplazamiento_salto(abs(offset), angulos_codo)
    
    if abs(z_slope) < 0.0001:
        return desp_base
    
    ang = max(angulos_codo)
    ct = math.cos(math.radians(ang))
    st = math.sin(math.radians(ang))
    sl = z_slope
    
    if es_ascenso:
        denom1 = ct * sl + st
        if abs(denom1) < 1e-10:
            return desp_base
        ratio = (ct - st * sl) / denom1
        denom2 = 1.0 - ratio * sl
        if abs(denom2) < 1e-10:
            return desp_base
        result = ratio * abs(offset) / denom2
    else:
        denom1 = st - ct * sl
        if abs(denom1) < 1e-10:
            return desp_base
        ratio = (ct + st * sl) / denom1
        denom2 = 1.0 + ratio * sl
        if abs(denom2) < 1e-10:
            return desp_base
        result = ratio * abs(offset) / denom2
    
    # Para 90° el resultado puede ser negativo (leve retroceso XY)
    # Para otros angulos siempre positivo
    return result if result > -abs(offset) else desp_base


def _salto_direccional(inicio, fin, bbox, margen, delta_z, desp_h, altura_z,
                       bajar=False, angulos_codo=None):
    """
    Genera puntos de salto/bajada alineados con la direccion del segmento.
    
    Para mantener angulos exactos cuando inicio.z != fin.z:
    1. La seccion elevada sigue la MISMA pendiente Z que la linea base
    2. Los desplazamientos horizontales se compensan con la pendiente
    3. Esto garantiza angulos exactos en el marco de referencia inclinado
    """
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    dist_xy = math.sqrt(dx**2 + dy**2)
    
    if dist_xy < 1:
        return [inicio, fin]
    
    ux = dx / dist_xy
    uy = dy / dist_xy
    
    # Pendiente Z de la linea base
    z_slope = (fin.z - inicio.z) / dist_xy
    
    def z_base(t):
        return inicio.z + z_slope * t
    
    # Proyeccion del bbox sobre el eje de movimiento
    cx_bbox = (bbox['x_min'] + bbox['x_max']) / 2
    cy_bbox = (bbox['y_min'] + bbox['y_max']) / 2
    hx = (bbox['x_max'] - bbox['x_min']) / 2
    hy = (bbox['y_max'] - bbox['y_min']) / 2
    ext_dir = abs(ux) * hx + abs(uy) * hy
    
    vec_centro_x = cx_bbox - inicio.x
    vec_centro_y = cy_bbox - inicio.y
    proj_centro = vec_centro_x * ux + vec_centro_y * uy
    
    obs_inicio_t = proj_centro - ext_dir - margen
    obs_fin_t = proj_centro + ext_dir + margen
    
    min_t = LONGITUD_MINIMA
    ang_codo = angulos_codo if angulos_codo else [90]

    # offset = altura perpendicular sobre la linea base en la zona del obstaculo
    offset = max(
        altura_z - z_base(obs_inicio_t) if obs_inicio_t > 0 else delta_z,
        altura_z - z_base(obs_fin_t) if obs_fin_t > 0 else delta_z,
        abs(delta_z)
    )
    if offset < 1:
        offset = abs(delta_z)
    
    # Asegurar que offset es suficiente para que los segmentos de transicion
    # cumplan LONGITUD_MINIMA.  Para angulo θ: 3D_len = offset / sin(θ)
    # => offset_min = LONGITUD_MINIMA * sin(θ)
    ang_max = max(ang_codo) if ang_codo else 90
    if ang_max < 90:
        min_offset = LONGITUD_MINIMA * math.sin(math.radians(ang_max))
    else:
        min_offset = LONGITUD_MINIMA
    offset = max(offset, min_offset)

    # Si hay pendiente Z y 90° codo pero tambien 45°, preferir 45° para angulos exactos
    codo_efectivo = ang_codo
    if desp_h < 1 and abs(z_slope) > 0.001:
        # 90° transicion tendria error de ~arctan(slope) grados
        # Si 45° disponible, usarlo para compensacion exacta
        if 45 in ang_codo:
            codo_efectivo = [45]
            desp_h = _calcular_desplazamiento_salto(offset, codo_efectivo)

    # Calcular desp_h compensados por pendiente
    desp_h_asc = _desp_h_con_pendiente(offset, codo_efectivo, z_slope, es_ascenso=not bajar)
    desp_h_desc = _desp_h_con_pendiente(offset, codo_efectivo, z_slope, es_ascenso=bajar)

    # t1: inicio del ascenso
    t1 = max(min_t, obs_inicio_t - max(abs(desp_h_asc), abs(desp_h)))

    if desp_h < 1:
        # 90° codos: transicion vertical (sin pendiente significativa)
        t2 = t1
        t3 = max(t2 + min_t, obs_fin_t)
        t4 = t3
    else:
        # Diagonal: usar desp_h compensados
        t2 = t1 + abs(desp_h_asc)
        # Nota: NO empujar t1 a 0 si t2 > obs_inicio_t. El ascenso va hacia
        # ARRIBA y despeja el obstaculo verticalmente aunque este dentro de su
        # huella XY. Mantener t1 >= min_t preserva el segmento de aproximacion
        # que separa el giro horizontal del ascenso vertical.
        t3 = max(t2 + min_t, obs_fin_t)
        t4 = t3 + abs(desp_h_desc)

    # CRITICO: clampear t-values a [0, dist_xy] para evitar puntos fuera del
    # segmento (ocurre cuando el obstaculo es mas grande que el segmento)
    t1 = max(0, min(t1, dist_xy))
    t2 = max(t1, min(t2, dist_xy))
    t3 = max(t2, min(t3, dist_xy))
    t4 = max(t3, min(t4, dist_xy))
    
    # Si el descenso cae demasiado cerca de fin, extender hasta fin
    # para evitar segmentos residuales cortos (< LONGITUD_MINIMA)
    if dist_xy - t4 < min_t:
        t4 = dist_xy  # p4 coincide con fin -> se fusionan en _validar_y_limpiar
        # Recalcular t3 para mantener geometria de descenso correcta
        t3_ideal = t4 - abs(desp_h_desc) if abs(desp_h_desc) > 0.5 else t4
        t3 = max(t2, min(t3_ideal, dist_xy))

    # Compensacion XY para 90° con pendiente Z: la transicion debe ser
    # perpendicular a la direccion (ux, uy, z_slope), no puramente vertical.
    # dot((ux,uy,s), (-s*ux,-s*uy,1)) = -s + s = 0 => exactamente 90°
    xy_comp = z_slope * offset if (desp_h < 1 and abs(z_slope) > 0.0001) else 0

    # Puntos: baseline sigue z_base(t), seccion elevada sigue z_base(t) + offset
    p1 = Punto3D(id="S", x=inicio.x + ux * t1, y=inicio.y + uy * t1, z=z_base(t1))
    p2 = Punto3D(id="S", x=inicio.x + ux * t2 - ux * xy_comp,
                          y=inicio.y + uy * t2 - uy * xy_comp, z=z_base(t2) + offset)
    p3 = Punto3D(id="S", x=inicio.x + ux * t3 - ux * xy_comp,
                          y=inicio.y + uy * t3 - uy * xy_comp, z=z_base(t3) + offset)
    p4 = Punto3D(id="S", x=inicio.x + ux * t4, y=inicio.y + uy * t4, z=z_base(t4))

    if bajar:
        p2 = Punto3D(id="S", x=inicio.x + ux * t2 + ux * xy_comp,
                              y=inicio.y + uy * t2 + uy * xy_comp, z=z_base(t2) - offset)
        p3 = Punto3D(id="S", x=inicio.x + ux * t3 + ux * xy_comp,
                              y=inicio.y + uy * t3 + uy * xy_comp, z=z_base(t3) - offset)

    return [inicio, p1, p2, p3, p4, fin]


def _rodeo_lateral(
    inicio: Punto3D,
    fin: Punto3D,
    bbox: dict,
    bboxes: List[dict],
    angulos_codo: List[int],
    direccion: int,
    margen: float
) -> Optional[List[Punto3D]]:
    """
    Intenta rodear un obstaculo en una direccion lateral.
    
    Args:
        direccion: +1 para rodear por Y+ (o X+), -1 para Y- (o X-)
    """
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    
    es_horizontal = abs(dy) < abs(dx)
    
    if es_horizontal:
        # Movimiento principal en X -> rodear en Y
        if direccion > 0:
            desvio_y = bbox['y_max'] - inicio.y + margen
        else:
            desvio_y = inicio.y - bbox['y_min'] + margen
        desvio_y = max(desvio_y, LONGITUD_MINIMA)
        
        # Para 90°: rodeo ortogonal puro (L-shape)
        # Para 45°: rodeo diagonal
        if 90 in angulos_codo:
            # Rodeo ortogonal
            p1 = Punto3D(id="C", x=inicio.x, y=inicio.y + direccion * desvio_y, z=inicio.z)
            p2 = Punto3D(id="C", x=fin.x, y=inicio.y + direccion * desvio_y, z=fin.z)
            ruta = [inicio, p1, p2, fin]
        elif 45 in angulos_codo:
            # Rodeo diagonal: diagonal -> recto -> diagonal
            sign_x = 1 if dx > 0 else -1
            p1 = Punto3D(id="C", x=inicio.x + sign_x * desvio_y, y=inicio.y + direccion * desvio_y, z=inicio.z)
            desvio_fin = abs(fin.y - p1.y)
            p2 = Punto3D(id="C", x=fin.x - sign_x * desvio_fin, y=p1.y, z=fin.z)
            ruta = [inicio, p1, p2, fin]
        else:
            # Angulo generico: usar descomposicion de desplazamiento
            from .angulos import calcular_direcciones_validas, descomponer_desplazamiento
            dirs = calcular_direcciones_validas(angulos_codo)
            
            # Punto intermedio desviado
            mid_y = inicio.y + direccion * desvio_y
            
            # Ruta: inicio -> punto_desviado -> alinear_con_fin -> fin
            seg1 = descomponer_desplazamiento(0, direccion * desvio_y, dirs)
            if not seg1:
                return None
            
            # Construir punto desviado
            px, py = inicio.x, inicio.y
            for sdx, sdy, _ in seg1:
                px += sdx
                py += sdy
            p1 = Punto3D(id="C", x=px, y=py, z=inicio.z)
            
            # Desde p1 al fin
            p2 = Punto3D(id="C", x=fin.x, y=py, z=fin.z)
            ruta = [inicio, p1, p2, fin]
    else:
        # Movimiento principal en Y -> rodear en X
        if direccion > 0:
            desvio_x = bbox['x_max'] - inicio.x + margen
        else:
            desvio_x = inicio.x - bbox['x_min'] + margen
        desvio_x = max(desvio_x, LONGITUD_MINIMA)
        
        if 90 in angulos_codo:
            p1 = Punto3D(id="C", x=inicio.x + direccion * desvio_x, y=inicio.y, z=inicio.z)
            p2 = Punto3D(id="C", x=inicio.x + direccion * desvio_x, y=fin.y, z=fin.z)
            ruta = [inicio, p1, p2, fin]
        elif 45 in angulos_codo:
            sign_y = 1 if dy > 0 else -1
            p1 = Punto3D(id="C", x=inicio.x + direccion * desvio_x, y=inicio.y + sign_y * desvio_x, z=inicio.z)
            desvio_fin = abs(fin.x - p1.x)
            p2 = Punto3D(id="C", x=p1.x, y=fin.y - sign_y * desvio_fin, z=fin.z)
            ruta = [inicio, p1, p2, fin]
        else:
            from .angulos import calcular_direcciones_validas, descomponer_desplazamiento
            dirs = calcular_direcciones_validas(angulos_codo)
            px, py = inicio.x, inicio.y
            seg1 = descomponer_desplazamiento(direccion * desvio_x, 0, dirs)
            if not seg1:
                return None
            for sdx, sdy, _ in seg1:
                px += sdx
                py += sdy
            p1 = Punto3D(id="C", x=px, y=py, z=inicio.z)
            p2 = Punto3D(id="C", x=px, y=fin.y, z=fin.z)
            ruta = [inicio, p1, p2, fin]
    
    # Verificar que ningun segmento cruce obstaculos
    for i in range(len(ruta) - 1):
        p_a, p_b = ruta[i], ruta[i + 1]
        if any(segmento_cruza_bbox(p_a.x, p_a.y, p_a.z, p_b.x, p_b.y, p_b.z, b) for b in bboxes):
            return None
    
    # Verificar longitudes minimas
    for i in range(len(ruta) - 1):
        dist = ruta[i].distancia_a(ruta[i + 1])
        if dist < LONGITUD_MINIMA - 0.5 and dist > 1:
            return None
    
    # Verificar angulos validos
    from .angulos import angulo_entre_vectores, validar_angulo
    for i in range(1, len(ruta) - 1):
        da = (ruta[i].x - ruta[i-1].x, ruta[i].y - ruta[i-1].y, ruta[i].z - ruta[i-1].z)
        db = (ruta[i+1].x - ruta[i].x, ruta[i+1].y - ruta[i].y, ruta[i+1].z - ruta[i].z)
        ang = angulo_entre_vectores(*da, *db)
        if not validar_angulo(ang, angulos_codo, 1.0):
            return None
    
    return ruta


def _validar_y_limpiar_ruta(
    puntos: List[Punto3D],
    inicio: Punto3D,
    fin: Punto3D
) -> Optional[List[Punto3D]]:
    """
    Valida y limpia una ruta de salto/bajada.
    Elimina puntos duplicados y verifica longitudes minimas.
    """
    if not puntos:
        return None
    
    # Filtrar puntos muy cercanos
    resultado = [puntos[0]]
    for p in puntos[1:]:
        dist = resultado[-1].distancia_a(p)
        if dist >= 50:
            resultado.append(p)
    
    if len(resultado) < 3:
        return None
    
    # Verificar que inicio y fin esten presentes
    if resultado[0].distancia_a(inicio) > 1:
        resultado.insert(0, inicio)
    if resultado[-1].distancia_a(fin) > 1:
        resultado.append(fin)
    
    return resultado
