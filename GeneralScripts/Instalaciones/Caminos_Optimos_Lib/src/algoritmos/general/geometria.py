"""
Utilidades geometricas para el algoritmo general de pathfinding.

Incluye: BBox (bounding box), deteccion de colisiones, interseccion de segmentos.
"""

import math
from typing import List, Optional, Dict, Any
from ...modelos import Punto3D, Obstaculo
from ...etiquetas import label_sub


# Constantes
LONGITUD_MINIMA = 150  # mm - longitud minima de segmento
MARGEN_OBSTACULO = 10  # mm - margen de seguridad alrededor de obstaculos


def crear_bbox(obs: Obstaculo, radio_tubo: float) -> Dict[str, Any]:
    """
    Crea bounding box expandido para un obstaculo.
    
    El bbox incluye margenes para el radio del tubo y seguridad.
    Tambien almacena el modo del obstaculo y sus limites reales.
    
    Args:
        obs: Obstaculo
        radio_tubo: Radio de la tuberia en mm
    
    Returns:
        Dict con limites expandidos y metadata
    """
    margen = radio_tubo + MARGEN_OBSTACULO
    
    # Limites reales del obstaculo (sin margen)
    z_real_min = obs.centro.z - obs.alto_mm / 2
    z_real_max = obs.centro.z + obs.alto_mm / 2
    
    return {
        'x_min': obs.centro.x - obs.ancho_mm / 2 - margen,
        'x_max': obs.centro.x + obs.ancho_mm / 2 + margen,
        'y_min': obs.centro.y - obs.largo_mm / 2 - margen,
        'y_max': obs.centro.y + obs.largo_mm / 2 + margen,
        'z_min': obs.centro.z - obs.alto_mm / 2 - margen,
        'z_max': obs.centro.z + obs.alto_mm / 2 + margen,
        # Limites reales (para calcular saltos/bajadas precisos)
        'z_real_min': z_real_min,
        'z_real_max': z_real_max,
        'x_real_min': obs.centro.x - obs.ancho_mm / 2,
        'x_real_max': obs.centro.x + obs.ancho_mm / 2,
        'y_real_min': obs.centro.y - obs.largo_mm / 2,
        'y_real_max': obs.centro.y + obs.largo_mm / 2,
        # Metadata
        'modo': obs.modo,
        'id': obs.id,
        'centro_x': obs.centro.x,
        'centro_y': obs.centro.y,
        'centro_z': obs.centro.z,
    }


def segmento_cruza_bbox(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
    bbox: dict
) -> bool:
    """
    Verifica si un segmento de linea cruza un bounding box.
    
    Usa muestreo discreto proporcional a la longitud del segmento.
    
    Args:
        x1, y1, z1: Punto inicial
        x2, y2, z2: Punto final
        bbox: Bounding box (dict con x_min, x_max, y_min, y_max, z_min, z_max)
    
    Returns:
        True si el segmento cruza el bbox
    """
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    if dist < 1:
        return False
    
    pasos = max(10, int(dist / 50))
    for i in range(pasos + 1):
        t = i / pasos
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        pz = z1 + t * (z2 - z1)
        if (bbox['x_min'] < px < bbox['x_max'] and
            bbox['y_min'] < py < bbox['y_max'] and
            bbox['z_min'] < pz < bbox['z_max']):
            return True
    return False


def encontrar_obstaculos_en_segmento(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
    bboxes: List[dict]
) -> List[dict]:
    """
    Encuentra todos los obstaculos que un segmento cruza.
    
    Args:
        x1, y1, z1: Punto inicial
        x2, y2, z2: Punto final
        bboxes: Lista de bounding boxes
    
    Returns:
        Lista de bboxes que cruza el segmento
    """
    resultado = []
    for bbox in bboxes:
        if segmento_cruza_bbox(x1, y1, z1, x2, y2, z2, bbox):
            resultado.append(bbox)
    return resultado


def ruta_cruza_obstaculos(ruta: List[Punto3D], bboxes: List[dict]) -> bool:
    """Verifica si algún segmento de la ruta cruza algún obstáculo."""
    for i in range(len(ruta) - 1):
        p1, p2 = ruta[i], ruta[i + 1]
        if encontrar_obstaculos_en_segmento(
            p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bboxes
        ):
            return True
    return False


def longitud_ruta(ruta: List[Punto3D]) -> float:
    """Calcula la longitud total de una ruta."""
    total = 0.0
    for i in range(len(ruta) - 1):
        total += ruta[i].distancia_a(ruta[i + 1])
    return total


def distancia_3d(x1, y1, z1, x2, y2, z2) -> float:
    """Distancia euclidiana 3D."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)


def eliminar_puntos_colineales(ruta: List[Punto3D], tolerancia: float = 2.0,
                               puntos_protegidos: List[Punto3D] = None) -> List[Punto3D]:
    """
    Elimina puntos redundantes que estan en linea recta (angulo ~180°).
    
    Args:
        ruta: Lista de puntos
        tolerancia: Tolerancia angular en grados
        puntos_protegidos: Puntos que nunca deben eliminarse (obligatorios, libres)
    
    Returns:
        Ruta sin puntos colineales
    """
    if len(ruta) < 3:
        return ruta
    
    # Construir set de posiciones protegidas para busqueda rapida
    protegidos = set()
    if puntos_protegidos:
        for p in puntos_protegidos:
            protegidos.add((round(p.x, 1), round(p.y, 1), round(p.z, 1)))
    
    def _es_protegido(punto: Punto3D) -> bool:
        return (round(punto.x, 1), round(punto.y, 1), round(punto.z, 1)) in protegidos
    
    resultado = [ruta[0]]
    
    for i in range(1, len(ruta) - 1):
        p_prev = resultado[-1]
        p_curr = ruta[i]
        p_next = ruta[i + 1]
        
        # Nunca eliminar puntos protegidos (obligatorios, libres, saltos)
        if _es_protegido(p_curr) or p_curr.id == "S":
            resultado.append(p_curr)
            continue
        
        dx1 = p_curr.x - p_prev.x
        dy1 = p_curr.y - p_prev.y
        dz1 = p_curr.z - p_prev.z
        
        dx2 = p_next.x - p_curr.x
        dy2 = p_next.y - p_curr.y
        dz2 = p_next.z - p_curr.z
        
        len1 = math.sqrt(dx1**2 + dy1**2 + dz1**2)
        len2 = math.sqrt(dx2**2 + dy2**2 + dz2**2)
        
        if len1 < 1 or len2 < 1:
            continue
        
        cos_ang = (dx1*dx2 + dy1*dy2 + dz1*dz2) / (len1 * len2)
        cos_ang = max(-1, min(1, cos_ang))
        angulo = math.degrees(math.acos(cos_ang))
        
        # Si angulo ~180° o ~0°, es colineal -> eliminar punto intermedio
        if angulo > 180 - tolerancia or angulo < tolerancia:
            continue
        
        resultado.append(p_curr)
    
    resultado.append(ruta[-1])
    return resultado


def eliminar_puntos_duplicados(ruta: List[Punto3D], tolerancia: float = 1.0) -> List[Punto3D]:
    """Elimina puntos duplicados consecutivos."""
    if not ruta:
        return ruta
    
    resultado = [ruta[0]]
    for p in ruta[1:]:
        ultimo = resultado[-1]
        if (abs(p.x - ultimo.x) > tolerancia or
            abs(p.y - ultimo.y) > tolerancia or
            abs(p.z - ultimo.z) > tolerancia):
            resultado.append(p)
    
    return resultado


def crear_bbox_segmento(p1: Punto3D, p2: Punto3D, margen: float) -> Dict[str, Any]:
    """Crea un AABB virtual alrededor de un segmento de tubo ya planificado.
    Se usa para evitar que tramos posteriores se solapen con este segmento."""
    xmin, xmax = min(p1.x, p2.x) - margen, max(p1.x, p2.x) + margen
    ymin, ymax = min(p1.y, p2.y) - margen, max(p1.y, p2.y) + margen
    zmin, zmax = min(p1.z, p2.z) - margen, max(p1.z, p2.z) + margen
    return {
        'x_min': xmin, 'x_max': xmax,
        'y_min': ymin, 'y_max': ymax,
        'z_min': zmin, 'z_max': zmax,
        'x_real_min': xmin, 'x_real_max': xmax,
        'y_real_min': ymin, 'y_real_max': ymax,
        'z_real_min': zmin, 'z_real_max': zmax,
        'modo': ['rodear'],
        'id': 'virtual',
        'centro_x': (p1.x + p2.x) / 2,
        'centro_y': (p1.y + p2.y) / 2,
        'centro_z': (p1.z + p2.z) / 2,
    }


def punto_en_bbox(p: Punto3D, bbox: Dict[str, Any], margen: float = 5.0) -> bool:
    """Verifica si un punto esta dentro de un bbox (con tolerancia)."""
    return (bbox['x_min'] - margen <= p.x <= bbox['x_max'] + margen and
            bbox['y_min'] - margen <= p.y <= bbox['y_max'] + margen and
            bbox['z_min'] - margen <= p.z <= bbox['z_max'] + margen)


def distancia_minima_segmentos_3d(p1, p2, p3, p4):
    """Distancia minima 3D entre dos segmentos usando muestreo proporcional."""
    min_d = float('inf')
    # Muestreo proporcional a la longitud del segmento (cada ~50mm)
    d1 = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2 + (p2.z-p1.z)**2)
    d2 = math.sqrt((p4.x-p3.x)**2 + (p4.y-p3.y)**2 + (p4.z-p3.z)**2)
    pasos_a = max(10, int(d1 / 100))
    pasos_b = max(10, int(d2 / 100))
    for i in range(pasos_a + 1):
        ta = i / pasos_a
        ax = p1.x + ta * (p2.x - p1.x)
        ay = p1.y + ta * (p2.y - p1.y)
        az = p1.z + ta * (p2.z - p1.z)
        for j in range(pasos_b + 1):
            tb = j / pasos_b
            bx = p3.x + tb * (p4.x - p3.x)
            by = p3.y + tb * (p4.y - p3.y)
            bz = p3.z + tb * (p4.z - p3.z)
            d = math.sqrt((ax - bx)**2 + (ay - by)**2 + (az - bz)**2)
            if d < min_d:
                min_d = d
    return min_d


def validar_autocruce(ruta: List[Punto3D], clearance: float) -> List[str]:
    """Detecta si la ruta se cruza consigo misma en 3D.
    Segmentos no adyacentes deben mantener distancia 3D >= clearance.
    Retorna lista de violaciones."""
    violaciones = []
    n = len(ruta)
    for i in range(n - 1):
        p1, p2 = ruta[i], ruta[i + 1]
        for j in range(i + 2, n - 1):
            p3, p4 = ruta[j], ruta[j + 1]
            # Pre-filtro rapido: si bboxes 3D no se solapan, skip
            margin = clearance
            if (max(p1.x, p2.x) + margin < min(p3.x, p4.x) - margin or
                min(p1.x, p2.x) - margin > max(p3.x, p4.x) + margin or
                max(p1.y, p2.y) + margin < min(p3.y, p4.y) - margin or
                min(p1.y, p2.y) - margin > max(p3.y, p4.y) + margin or
                max(p1.z, p2.z) + margin < min(p3.z, p4.z) - margin or
                min(p1.z, p2.z) - margin > max(p3.z, p4.z) + margin):
                continue
            d = distancia_minima_segmentos_3d(p1, p2, p3, p4)
            if d < clearance:
                violaciones.append(
                    f"  AutoCruce: seg {p1.id}-{p2.id} vs {p3.id}-{p4.id} dist={d:.1f}mm < {clearance:.1f}mm"
                )
    return violaciones


def validar_ruta_contra_obstaculos(ruta: List[Punto3D], bboxes: List[Dict],
                                    etiqueta: str = "") -> List[str]:
    """Valida que ningun segmento de la ruta cruce obstaculos. Retorna lista de violaciones."""
    violaciones = []
    for i in range(len(ruta) - 1):
        p1, p2 = ruta[i], ruta[i + 1]
        for bb in bboxes:
            if bb.get('id') == 'virtual':
                continue
            if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                violaciones.append(
                    f"  {etiqueta}Seg {p1.id}-{p2.id} cruza {bb.get('id','?')}"
                )
    return violaciones


def snap_ruta_a_grilla(ruta: List[Punto3D], direcciones: List[float],
                       angulos_codo: List[int] = None) -> List[Punto3D]:
    """
    Ajusta posiciones XY de puntos intermedios para que cada segmento
    siga una direccion exacta de la grilla. Preserva Z.
    El primer y ultimo punto no se mueven.
    Solo ajusta puntos donde el error es pequeño (<5°) para no romper la geometria.
    """
    if len(ruta) < 3 or not direcciones:
        return ruta

    def _diff_ang(a, b):
        d = (a - b) % 360
        return d if d <= 180 else 360 - d

    def _snap_dir(ang):
        return min(direcciones, key=lambda d: _diff_ang(ang, d))

    def _dir_xy(p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        d = math.sqrt(dx * dx + dy * dy)
        if d < 1:
            return None
        return math.degrees(math.atan2(dy, dx)) % 360

    # Build set of valid internal angles (from codo angles)
    valid_angles = {180.0}
    if angulos_codo:
        for c in angulos_codo:
            valid_angles.add(180.0 - c)

    def _angle_valid(d_in, d_out):
        """Check if the turn from d_in to d_out produces a valid internal angle."""
        if d_in is None or d_out is None:
            return True
        between = _diff_ang(d_in, d_out)
        internal = 180.0 - between
        for va in valid_angles:
            if abs(internal - va) < 1.5:
                return True
        return internal > 178.5  # near-straight is always ok

    resultado = list(ruta)

    # Forward pass: snap each intermediate point, validate angle before accepting
    for i in range(1, len(resultado) - 1):
        prev = resultado[i - 1]
        curr = resultado[i]
        dx = curr.x - prev.x
        dy = curr.y - prev.y
        dist_xy = math.sqrt(dx * dx + dy * dy)

        if dist_xy < 1:
            continue

        ang = math.degrees(math.atan2(dy, dx)) % 360
        snapped = _snap_dir(ang)
        error = _diff_ang(ang, snapped)
        if error < 0.01 or error > 5:
            continue

        # Compute candidate new position
        rad = math.radians(snapped)
        new_x = prev.x + dist_xy * math.cos(rad)
        new_y = prev.y + dist_xy * math.sin(rad)
        candidate = Punto3D(id=curr.id, x=new_x, y=new_y, z=curr.z)

        # Check that angle at this point remains valid
        nxt = resultado[i + 1] if i + 1 < len(resultado) else None
        d_out = _dir_xy(candidate, nxt) if nxt else None
        if not _angle_valid(snapped, d_out):
            continue  # Skip this snap — would create bad angle

        # Check angle at previous point
        if i >= 2:
            d_prev_in = _dir_xy(resultado[i - 2], prev)
            d_prev_out = _dir_xy(prev, candidate)
            if not _angle_valid(d_prev_in, d_prev_out):
                continue

        resultado[i] = candidate

    return resultado


def fusionar_segmentos_cortos(ruta: List[Punto3D], longitud_min: float) -> List[Punto3D]:
    """Fusiona puntos que crean segmentos mas cortos que longitud_min."""
    if len(ruta) < 3:
        return ruta
    cambios = True
    while cambios:
        cambios = False
        resultado = [ruta[0]]
        i = 1
        while i < len(ruta) - 1:
            dist_prev = resultado[-1].distancia_a(ruta[i])
            dist_next = ruta[i].distancia_a(ruta[i + 1])
            if dist_prev < longitud_min - 1:
                cambios = True
                i += 1
                continue
            if dist_next < longitud_min - 1 and i + 1 < len(ruta) - 1:
                resultado.append(ruta[i])
                cambios = True
                i += 2
                continue
            resultado.append(ruta[i])
            i += 1
        while i < len(ruta):
            resultado.append(ruta[i])
            i += 1
        ruta = resultado
    return ruta


def asignar_ids(ruta: List[Punto3D], puntos_obligatorios: List[Punto3D],
                puntos_libres: List[Punto3D] = None,
                camino_idx: int = None) -> None:
    """Asigna IDs descriptivos: A, B, O#, L#, C#.
    
    Si camino_idx se proporciona, usa formato con subindice de camino:
      A₁, B₁, C₁₋₁, C₁₋₂, O₁₋₁, etc.
    """
    if not ruta:
        return
    if not ruta[0].id:
        ruta[0].id = label_sub('A', camino_idx)
    if not ruta[-1].id:
        ruta[-1].id = label_sub('B', camino_idx)
    puntos_conocidos = (puntos_obligatorios or []) + (puntos_libres or [])
    contador_c = 1
    contador_o = 1
    contador_l = 1
    for punto in ruta[1:-1]:
        es_conocido = False
        for p_ref in puntos_conocidos:
            if punto.distancia_a(p_ref) < 500:
                # Reasignar ID con formato de camino si aplica
                if camino_idx is not None:
                    prefix = p_ref.id[0] if p_ref.id else 'C'
                    if prefix.upper() == 'O':
                        punto.id = label_sub('O', camino_idx, contador_o)
                        contador_o += 1
                    elif prefix.upper() == 'L':
                        punto.id = label_sub('L', camino_idx, contador_l)
                        contador_l += 1
                    else:
                        punto.id = p_ref.id
                else:
                    punto.id = p_ref.id
                es_conocido = True
                break
        if not es_conocido:
            punto.id = label_sub('C', camino_idx, contador_c) if camino_idx else f"C{contador_c}"
            contador_c += 1
