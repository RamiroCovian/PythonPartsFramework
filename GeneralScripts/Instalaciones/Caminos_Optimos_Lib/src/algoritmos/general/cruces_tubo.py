"""
Modulo especializado para cruces tubo-tubo.

En vez de usar AABBs (bounding boxes) que aproximan mal tubos diagonales,
este modulo trabaja directamente con segmentos de tubo (p1, p2, radio) y
calcula el punto exacto de cruce entre la ruta y el tubo obstaculo.

El perfil de salto se genera alineado con la direccion del segmento de ruta,
garantizando angulos de 135 grados por construccion (para codos de 45 grados).
"""

import math
from typing import List, Optional, Tuple, NamedTuple

from ...modelos import Punto3D
from .geometria import LONGITUD_MINIMA


class SegmentoTubo(NamedTuple):
    """Representa un segmento de tubo fisico: linea (p1→p2) con radio."""
    p1: Punto3D
    p2: Punto3D
    radio: float
    camino_id: str = ""


# =====================================================================
#  Fase 2: Distancia minima entre dos segmentos 3D
# =====================================================================

def distancia_minima_segmentos(
    a0: Punto3D, a1: Punto3D,
    b0: Punto3D, b1: Punto3D,
) -> Tuple[float, float, float]:
    """
    Calcula la distancia minima entre dos segmentos 3D.
    
    Segmento A: a0 → a1  (parametro s ∈ [0, 1])
    Segmento B: b0 → b1  (parametro t ∈ [0, 1])
    
    Returns:
        (distancia, s, t) donde s y t son los parametros en [0,1]
        del punto mas cercano en cada segmento.
    
    Algoritmo basado en "Distance Between Lines, Rays, and Segments"
    de David Eberly (Geometric Tools).
    """
    dx = a1.x - a0.x
    dy = a1.y - a0.y
    dz = a1.z - a0.z
    
    ex = b1.x - b0.x
    ey = b1.y - b0.y
    ez = b1.z - b0.z
    
    wx = a0.x - b0.x
    wy = a0.y - b0.y
    wz = a0.z - b0.z
    
    a = dx * dx + dy * dy + dz * dz   # |d|^2
    b = dx * ex + dy * ey + dz * ez   # d · e
    c = ex * ex + ey * ey + ez * ez   # |e|^2
    d_val = dx * wx + dy * wy + dz * wz  # d · w
    e_val = ex * wx + ey * wy + ez * wz  # e · w
    
    denom = a * c - b * b
    
    # Parametros iniciales (lineas infinitas)
    if denom < 1e-10:
        # Segmentos paralelos
        s = 0.0
        t = e_val / c if c > 1e-10 else 0.0
    else:
        s = (b * e_val - c * d_val) / denom
        t = (a * e_val - b * d_val) / denom
    
    # Clampear s a [0, 1] y recalcular t
    s = max(0.0, min(1.0, s))
    # Recalcular t optimo para este s
    if c > 1e-10:
        t = (b * s + e_val) / c  # Nota: signo correcto -> (e · (a0 + s*d - b0)) / |e|^2
        # Correccion: t = (b*s + e_val) / c  ->  t = (dot(e, a0+s*d - b0)) / |e|^2
        #   = (e · (w + s*d)) / c = (e·w + s*(e·d)) / c = (e_val + s*b) / c
        t = (e_val + s * b) / c
    else:
        t = 0.0
    
    # Clampear t a [0, 1] y recalcular s
    t = max(0.0, min(1.0, t))
    if a > 1e-10:
        s = (-d_val + b * t) / a  # Nota: s = (d · (b0 + t*e - a0)) / |d|^2
        # Correccion: s = (dot(d, b0+t*e - a0)) / |d|^2 = (-d·w + t*(d·e)) / a = (-d_val + t*b) / a
        s = (-d_val + t * b) / a
    else:
        s = 0.0
    s = max(0.0, min(1.0, s))
    
    # Calcular puntos mas cercanos y distancia
    px = a0.x + s * (a1.x - a0.x) - (b0.x + t * (b1.x - b0.x))
    py = a0.y + s * (a1.y - a0.y) - (b0.y + t * (b1.y - b0.y))
    pz = a0.z + s * (a1.z - a0.z) - (b0.z + t * (b1.z - b0.z))
    
    dist = math.sqrt(px * px + py * py + pz * pz)
    return dist, s, t


# =====================================================================
#  Fase 3: Insercion de saltos para cruces tubo-tubo
# =====================================================================

def insertar_saltos_tubo(
    ruta: List[Punto3D],
    tubos_obstaculo: List[SegmentoTubo],
    radio_tubo_nuevo: float,
    angulos_codo: List[int],
    segmentos_protegidos: Tuple[int, int] = (0, 0),
) -> List[Punto3D]:
    """
    Inserta saltos en Z donde la ruta cruza tubos obstaculo existentes.
    
    Algoritmo de 2 fases:
      Fase 1: Escanea TODOS los segmentos y detecta zonas de cruce.
      Fase 2: Agrupa segmentos consecutivos con cruce en ZONAS.
              Cada zona genera UN puente limpio (subir, elevado, bajar).
    
    Para 45 grados: perfil diagonal centrado en la zona de cruce.
    Para 90 grados: vertical UP, copia de ruta a Z elevada, vertical DOWN.
    
    Args:
        ruta: Lista de puntos de la ruta
        tubos_obstaculo: Segmentos de tubo existentes
        radio_tubo_nuevo: Radio del tubo que se esta calculando
        angulos_codo: Angulos de codo permitidos (ej. [45])
        segmentos_protegidos: (n_inicio, n_fin) segmentos a proteger en
            cada extremo. Los conectores diagonales en esos segmentos ya
            proveen clearance vertical, asi que no necesitan saltos.
    
    Returns:
        Ruta modificada con saltos insertados
    """
    if not tubos_obstaculo or not ruta or len(ruta) < 2:
        return ruta
    
    CLEARANCE = 10.0  # mm entre superficies
    MARGEN_DETECCION = 5.0  # mm extra para detectar tubos apilados
    clearance_det = CLEARANCE + MARGEN_DETECCION
    es_90 = (90 in angulos_codo)
    N = len(ruta) - 1  # numero de segmentos
    prot_ini, prot_fin = segmentos_protegidos
    
    # ================================================================
    #  FASE 1: Detectar cruces en cada segmento
    # ================================================================
    cruces = []
    for i in range(N):
        # Saltar segmentos protegidos (conectores) en los extremos
        if i < prot_ini or i >= N - prot_fin:
            cruces.append(None)
            continue
        cruce = _encontrar_cruce_mas_cercano(
            ruta[i], ruta[i + 1], tubos_obstaculo,
            radio_tubo_nuevo, clearance_det
        )
        cruces.append(cruce)  # None o (s_enter, s_exit, z_salto)
    
    # ================================================================
    #  FASE 2: Agrupar segmentos consecutivos con cruce en zonas
    # ================================================================
    zonas = []  # lista de (bridge_start, bridge_end, max_z_salto)
    i = 0
    while i < N:
        if cruces[i] is None:
            i += 1
            continue
        
        # Inicio de zona: agrupar TODOS los segmentos consecutivos con cruce
        zone_start = i
        zone_end = i
        max_z = cruces[i][2]
        
        while zone_end + 1 < N and cruces[zone_end + 1] is not None:
            zone_end += 1
            max_z = max(max_z, cruces[zone_end][2])
        
        # Recortar bordes marginales:
        # Si el primer segmento solo cruza al final (s_enter > 0.75),
        # excluirlo del puente -> sirve como approach natural.
        bridge_start = zone_start
        bridge_end = zone_end + 1  # apunta a ruta[bridge_end] = punto final
        
        if zone_end > zone_start:
            if cruces[zone_start][0] > 0.75:
                bridge_start = zone_start + 1
            if cruces[zone_end][1] < 0.25:
                bridge_end = zone_end
        
        # Si el recorte colapso la zona, revertir al rango completo
        if bridge_start >= bridge_end:
            bridge_start = zone_start
            bridge_end = zone_end + 1
        
        zonas.append((bridge_start, bridge_end, max_z))
        i = zone_end + 1
    
    if not zonas:
        return ruta
    
    # ================================================================
    #  FASE 3: Construir resultado con puentes limpios
    # ================================================================
    resultado = [ruta[0]]
    seg_idx = 0
    zone_ptr = 0
    
    while seg_idx < N:
        if zone_ptr < len(zonas) and seg_idx == zonas[zone_ptr][0]:
            zs, ze, max_z = zonas[zone_ptr]
            
            if ze - zs == 1 and not es_90:
                # Segmento unico con codos diagonales -> perfil de salto
                s_enter = cruces[zs][0] if cruces[zs] else 0.0
                s_exit = cruces[zs][1] if cruces[zs] else 1.0
                puntos = _generar_perfil_salto(
                    ruta[zs], ruta[ze], s_enter, s_exit, max_z,
                    angulos_codo, radio_tubo_nuevo
                )
                if puntos:
                    for sp in puntos:
                        if resultado[-1].distancia_a(sp) > 1.0:
                            resultado.append(sp)
                if ruta[ze].distancia_a(resultado[-1]) > 1.0:
                    resultado.append(ruta[ze])
            else:
                # Multi-segmento o 90 grados -> puente zona
                _insertar_salto_zona(
                    resultado, ruta, zs, ze, max_z,
                    angulos_codo, radio_tubo_nuevo
                )
            
            seg_idx = ze
            zone_ptr += 1
        else:
            if ruta[seg_idx + 1].distancia_a(resultado[-1]) > 1.0:
                resultado.append(ruta[seg_idx + 1])
            seg_idx += 1
    
    return resultado


def _insertar_salto_zona(
    resultado: List[Punto3D],
    ruta: List[Punto3D],
    i_inicio: int,
    i_fin: int,
    z_salto: float,
    angulos_codo: List[int],
    radio_tubo: float,
):
    """
    Inserta un salto que abarca multiples segmentos consecutivos (zona de cruce).
    
    Para 90 grados: vertical UP en ruta[i_inicio], copia escalera a Z elevada,
    vertical DOWN en ruta[i_fin]. Angulos 90 por construccion.
    
    Para 45 grados: perfil diagonal desde ruta[i_inicio] a ruta[i_fin].
    """
    es_90 = (90 in angulos_codo)
    min_t = LONGITUD_MINIMA
    
    p_start = ruta[i_inicio]
    p_end = ruta[i_fin]
    
    # Calcular offset necesario
    z_baseline = p_start.z
    offset = z_salto - z_baseline
    
    # Forzar offset minimo para cumplir LONGITUD_MINIMA
    if es_90:
        if offset < min_t:
            offset = min_t
    else:
        offset_min_45 = min_t / math.sqrt(2)
        if offset < offset_min_45:
            offset = offset_min_45
    
    if es_90:
        # Vertical UP en p_start (misma XY, Z elevada)
        p_up = Punto3D(id="S", x=p_start.x, y=p_start.y, z=p_start.z + offset)
        if resultado[-1].distancia_a(p_up) > 1.0:
            resultado.append(p_up)
        
        # Copiar puntos intermedios de la escalera a Z elevada
        for k in range(i_inicio + 1, i_fin):
            p_elev = Punto3D(
                id="S", x=ruta[k].x, y=ruta[k].y,
                z=ruta[k].z + offset
            )
            if resultado[-1].distancia_a(p_elev) > 1.0:
                resultado.append(p_elev)
        
        # Punto elevado en p_end (antes del descenso)
        p_down_top = Punto3D(id="S", x=p_end.x, y=p_end.y, z=p_end.z + offset)
        if resultado[-1].distancia_a(p_down_top) > 1.0:
            resultado.append(p_down_top)
        
        # Descenso vertical a baseline en p_end
        if p_end.distancia_a(resultado[-1]) > 1.0:
            resultado.append(p_end)
    else:
        # 45 grados: perfil diagonal que abarca toda la zona
        dist_zona = math.sqrt(
            (p_end.x - p_start.x)**2 + (p_end.y - p_start.y)**2
        )
        if dist_zona > 1.0:
            puntos_salto = _generar_perfil_salto(
                p_start, p_end, 0.0, 1.0, z_salto,
                angulos_codo, radio_tubo
            )
            if puntos_salto:
                for sp in puntos_salto:
                    if resultado[-1].distancia_a(sp) > 1.0:
                        resultado.append(sp)
        if p_end.distancia_a(resultado[-1]) > 1.0:
            resultado.append(p_end)


def _encontrar_cruce_mas_cercano(
    seg_ini: Punto3D,
    seg_fin: Punto3D,
    tubos: List[SegmentoTubo],
    radio_nuevo: float,
    clearance: float,
) -> Optional[Tuple[float, float, float]]:
    """
    Encuentra la zona de cruce en el segmento de ruta.
    
    Muestrea el segmento para encontrar el span completo donde la ruta
    esta dentro de la distancia umbral de algun tubo obstaculo.
    
    Returns:
        (s_enter, s_exit, z_salto) o None si no hay cruce.
        s_enter: parametro [0,1] donde la ruta entra en la zona de peligro
        s_exit: parametro [0,1] donde la ruta sale de la zona de peligro
        z_salto: altura Z maxima que debe alcanzar el tubo para saltar
    """
    # Muestrear el segmento para encontrar toda la zona de peligro
    N_SAMPLES = 40
    CLEARANCE_FISICO = 10.0  # clearance real entre superficies de tubos
    global_s_enter = None
    global_s_exit = None
    max_z_salto = None
    
    for tubo in tubos:
        umbral = radio_nuevo + tubo.radio + clearance
        
        # Primero check rapido con distancia minima
        dist_min, _, _ = distancia_minima_segmentos(
            seg_ini, seg_fin, tubo.p1, tubo.p2
        )
        if dist_min >= umbral:
            continue
        
        # Hay cruce -> muestrear para encontrar span completo
        for k in range(N_SAMPLES + 1):
            s = k / N_SAMPLES
            # Punto en la ruta
            px = seg_ini.x + s * (seg_fin.x - seg_ini.x)
            py = seg_ini.y + s * (seg_fin.y - seg_ini.y)
            pz = seg_ini.z + s * (seg_fin.z - seg_ini.z)
            
            # Distancia de este punto al segmento del tubo
            p_sample = Punto3D(x=px, y=py, z=pz)
            dist_s, _, t_tube = distancia_minima_segmentos(
                p_sample, p_sample, tubo.p1, tubo.p2
            )
            
            if dist_s < umbral:
                if global_s_enter is None or s < global_s_enter:
                    global_s_enter = s
                if global_s_exit is None or s > global_s_exit:
                    global_s_exit = s
                
                # Z del tubo en este punto
                # Usar CLEARANCE_FISICO (no la clearance de deteccion) para
                # la altura del salto. Esto hace que el tubo saltado quede
                # DENTRO del umbral de deteccion del siguiente camino,
                # permitiendo apilamiento correcto de saltos.
                z_tubo = tubo.p1.z + t_tube * (tubo.p2.z - tubo.p1.z)
                z_obj = z_tubo + tubo.radio + radio_nuevo + CLEARANCE_FISICO
                if max_z_salto is None or z_obj > max_z_salto:
                    max_z_salto = z_obj
    
    if global_s_enter is None:
        return None
    
    # Agregar margen al span para seguridad (medio paso de muestreo)
    margen = 0.5 / N_SAMPLES
    global_s_enter = max(0.0, global_s_enter - margen)
    global_s_exit = min(1.0, global_s_exit + margen)
    
    return global_s_enter, global_s_exit, max_z_salto


def _generar_perfil_salto(
    seg_ini: Punto3D,
    seg_fin: Punto3D,
    s_enter: float,
    s_exit: float,
    z_salto: float,
    angulos_codo: List[int],
    radio_tubo: float,
) -> Optional[List[Punto3D]]:
    """
    Genera el perfil de salto que cubre toda la zona de cruce [s_enter, s_exit].
    
    El perfil sigue la MISMA direccion XY que el segmento original.
    Solo cambia Z. Esto garantiza angulos correctos por construccion.
    
    La seccion elevada (p2→p3) cubre TODA la zona de peligro, asegurando
    que ningun punto de la ruta quede dentro de la distancia de clearance
    del tubo obstaculo.
    
    Para 45 grados (diagonal):
        p1 → p2: ascenso diagonal (desp_h en XY + offset en Z)
        p2 → p3: seccion elevada horizontal (cubre [s_enter, s_exit])
        p3 → p4: descenso diagonal
    
    Para 90 grados (vertical):
        p1 → p2: ascenso vertical (0 en XY, offset en Z)
        p2 → p3: seccion elevada horizontal (cubre [s_enter, s_exit])
        p3 → p4: descenso vertical (0 en XY, offset en Z)
    
    Returns:
        Lista [p1, p2, p3, p4] o None si no hay espacio suficiente
    """
    # Calcular geometria del segmento
    dx = seg_fin.x - seg_ini.x
    dy = seg_fin.y - seg_ini.y
    dz = seg_fin.z - seg_ini.z
    dist_xy = math.sqrt(dx * dx + dy * dy)
    
    if dist_xy < 1.0:
        return None
    
    ux = dx / dist_xy
    uy = dy / dist_xy
    z_slope = dz / dist_xy  # pendiente Z por unidad XY
    
    # Z baseline en funcion del parametro t (distancia XY desde inicio)
    def z_base(t_xy):
        return seg_ini.z + z_slope * t_xy
    
    # Offset vertical necesario
    t_enter_xy = s_enter * dist_xy
    t_exit_xy = s_exit * dist_xy
    t_mid_xy = (t_enter_xy + t_exit_xy) / 2
    z_baseline_mid = z_base(t_mid_xy)
    offset = z_salto - z_baseline_mid
    
    if offset < 1.0:
        return None
    
    min_t = LONGITUD_MINIMA
    es_90 = (90 in angulos_codo)
    
    # ================================================================
    #  Calcular offset minimo para cumplir LONGITUD_MINIMA en ascenso
    # ================================================================
    if es_90:
        if offset < min_t:
            offset = min_t
    else:
        offset_min_45 = min_t / math.sqrt(2)
        if offset < offset_min_45:
            offset = offset_min_45
    
    # ================================================================
    #  Calcular desplazamiento horizontal para ascenso/descenso
    # ================================================================
    if es_90:
        desp_h_asc = 0.0
        desp_h_desc = 0.0
    elif 45 in angulos_codo:
        desp_h_asc = offset / max(0.1, 1.0 - abs(z_slope))
        desp_h_desc = offset / max(0.1, 1.0 + abs(z_slope))
        desp_h_asc = min(desp_h_asc, offset * 3)
        desp_h_desc = min(desp_h_desc, offset * 3)
    else:
        desp_h_asc = offset
        desp_h_desc = offset
    
    # ================================================================
    #  Calcular posiciones t (distancia XY desde inicio del segmento)
    #  La seccion elevada [t2, t3] DEBE cubrir toda la zona [t_enter, t_exit]
    # ================================================================
    if es_90 and dist_xy < 3 * min_t:
        # CASO ESPECIAL: segmento corto (escalera 90 grados).
        t1 = 0.0
        t2 = 0.0
        t3 = dist_xy
        t4 = dist_xy
    else:
        # La seccion elevada debe cubrir toda la zona de peligro
        t2 = t_enter_xy - desp_h_asc  # ascenso ANTES de entrar en la zona
        t3 = t_exit_xy + desp_h_desc   # descenso DESPUES de salir de la zona
        t1 = t2 - desp_h_asc
        t4 = t3 + desp_h_desc
        
        # Asegurar seccion elevada minima
        if t3 - t2 < min_t:
            expansion = (min_t - (t3 - t2)) / 2
            t2 -= expansion
            t3 += expansion
            t1 = t2 - desp_h_asc
            t4 = t3 + desp_h_desc
        
        # Asegurar espacio para approach
        if t1 < min_t:
            shift = min_t - t1
            t1 += shift
            t2 += shift
            t3 += shift
            t4 += shift
        
        # Limitar t4 para dejar gap minimo al final del segmento
        # (preserva el angulo valido existente en el vertice del endpoint)
        max_t4 = dist_xy - min_t
        if max_t4 < min_t * 3:
            max_t4 = dist_xy  # segmento demasiado corto, usar completo
        
        # Si no cabe departure, ajustar t3 para mantener angulo correcto
        if t4 > max_t4:
            t4 = max_t4
            # Retroceder t3 para que la distancia t4-t3 == desp_h_desc
            t3 = t4 - desp_h_desc
            # Si t3 colapsó sobre t2, no hay espacio suficiente
            if t3 < t2 + min_t * 0.5:
                return None
        
        # Si no cabe approach, ajustar t2 para mantener angulo correcto
        if t1 < 0:
            t1 = 0
            t2 = t1 + desp_h_asc
            if t2 > t3 - min_t * 0.5:
                return None
        
        # Clamp final
        t1 = max(0, min(t1, dist_xy))
        t2 = max(t1, min(t2, dist_xy))
        t3 = max(t2, min(t3, dist_xy))
        t4 = max(t3, min(t4, dist_xy))
    
    # ================================================================
    #  Generar puntos
    # ================================================================
    p1 = Punto3D(
        id="S", x=seg_ini.x + ux * t1, y=seg_ini.y + uy * t1,
        z=z_base(t1)
    )
    p2 = Punto3D(
        id="S", x=seg_ini.x + ux * t2, y=seg_ini.y + uy * t2,
        z=z_base(t2) + offset
    )
    p3 = Punto3D(
        id="S", x=seg_ini.x + ux * t3, y=seg_ini.y + uy * t3,
        z=z_base(t3) + offset
    )
    p4 = Punto3D(
        id="S", x=seg_ini.x + ux * t4, y=seg_ini.y + uy * t4,
        z=z_base(t4)
    )
    
    # Filtrar puntos degenerados (demasiado cercanos entre si)
    puntos = []
    for p in [p1, p2, p3, p4]:
        if not puntos or puntos[-1].distancia_a(p) > 10:
            puntos.append(p)
    
    if len(puntos) < 2:
        return None
    
    return puntos
