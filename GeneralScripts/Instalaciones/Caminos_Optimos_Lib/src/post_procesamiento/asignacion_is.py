"""
Post-procesamiento: asigna cada nodo del camino a un IS y detecta puntos
de union (U) en los margenes entre IS adyacentes.

La asignacion se hace proyectando cada punto del camino sobre el plano del
techo (que puede ser inclinado) a lo largo de su vector normal.
"""

import math
import json
import numpy as np
from typing import List, Dict, Optional, Tuple, Any

from ..modelos.punto import Punto3D
from ..etiquetas import label_sub


# ---------------------------------------------------------------------------
# Proyeccion al plano del techo
# ---------------------------------------------------------------------------

def _calcular_normal_techo(vertices_techo: List[List[float]]) -> np.ndarray:
    """Devuelve el vector normal unitario del plano del techo (apuntando +Z)."""
    v0 = np.array(vertices_techo[0])
    v1 = np.array(vertices_techo[1])
    v2 = np.array(vertices_techo[2])
    n = np.cross(v1 - v0, v2 - v0)
    norma = np.linalg.norm(n)
    if norma > 1e-9:
        n = n / norma
    else:
        n = np.array([0.0, 0.0, 1.0])
    if n[2] < 0:
        n = -n
    return n


def proyectar_al_plano(px: float, py: float, pz: float,
                       normal: np.ndarray,
                       punto_plano: np.ndarray) -> Tuple[float, float, float]:
    """Proyecta un punto 3D sobre el plano del techo a lo largo de la normal.

    Retorna (x_proj, y_proj, z_proj) sobre el plano.
    """
    p = np.array([px, py, pz])
    denom = np.dot(normal, normal)
    if denom < 1e-12:
        return (px, py, pz)
    t = np.dot(punto_plano - p, normal) / denom
    proj = p + t * normal
    return (float(proj[0]), float(proj[1]), float(proj[2]))


# ---------------------------------------------------------------------------
# Asignacion de punto a IS
# ---------------------------------------------------------------------------

def _is_bounds(is_data: Dict) -> Tuple[float, float, float, float]:
    """Devuelve (x_min, x_max, y_min, y_max) de un IS."""
    verts = is_data.get('vertices', [])
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    return (min(xs), max(xs), min(ys), max(ys))


def punto_en_is(px_proj: float, py_proj: float, is_data: Dict) -> bool:
    """Verifica si un punto proyectado cae dentro del rectangulo de un IS."""
    xmin, xmax, ymin, ymax = _is_bounds(is_data)
    return xmin <= px_proj <= xmax and ymin <= py_proj <= ymax


def obtener_is_de_punto(px_proj: float, py_proj: float,
                        subdivisiones: List[Dict]) -> Optional[str]:
    """Dado un punto proyectado al plano del techo, devuelve el ID del IS
    que lo contiene, o None si esta en el margen."""
    for is_data in subdivisiones:
        if punto_en_is(px_proj, py_proj, is_data):
            return is_data.get('id')
    return None


# ---------------------------------------------------------------------------
# Deteccion de cruces de margen e insercion de puntos U
# ---------------------------------------------------------------------------

def _intersecciones_segmento_rect(x1, y1, x2, y2,
                                   xmin, ymin, xmax, ymax) -> List[float]:
    """Parametros t ∈ (0,1) donde el segmento (x1,y1)->(x2,y2) cruza
    los bordes del rectangulo [xmin,xmax] x [ymin,ymax]."""
    dx = x2 - x1
    dy = y2 - y1
    ts = []
    # Bordes verticales
    if abs(dx) > 1e-10:
        for xb in [xmin, xmax]:
            t = (xb - x1) / dx
            if 1e-9 < t < 1 - 1e-9:
                yy = y1 + t * dy
                if ymin - 1 <= yy <= ymax + 1:
                    ts.append(t)
    # Bordes horizontales
    if abs(dy) > 1e-10:
        for yb in [ymin, ymax]:
            t = (yb - y1) / dy
            if 1e-9 < t < 1 - 1e-9:
                xx = x1 + t * dx
                if xmin - 1 <= xx <= xmax + 1:
                    ts.append(t)
    return sorted(set(round(t, 10) for t in ts))


def encontrar_puntos_union(camino: List[Punto3D],
                           subdivisiones: List[Dict],
                           normal: np.ndarray,
                           punto_plano: np.ndarray,
                           z_eje_fn=None,
                           camino_idx: int = None) -> List[Dict]:
    """Detecta donde el camino cruza margenes entre IS y genera puntos U.

    Args:
        z_eje_fn: opcional, callable(x, y) -> float que retorna la Z esperada
                  del eje en la cota. Si se provee, solo se generan puntos U
                  en segmentos cuyo tubo esta al ras de la cota.

    Retorna lista ordenada de dicts:
        {indice_segmento, t, is_origen, is_destino, punto: Punto3D}
    """
    if not subdivisiones or len(camino) < 2:
        return []

    puntos_u: List[Dict] = []
    contador_u = 1
    _TOLERANCIA_COTA = 5.0  # mm

    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i + 1]

        # Solo generar U en segmentos donde el tubo va al ras de la cota
        if z_eje_fn is not None:
            z_exp1 = z_eje_fn(p1.x, p1.y)
            z_exp2 = z_eje_fn(p2.x, p2.y)
            if abs(p1.z - z_exp1) > _TOLERANCIA_COTA or abs(p2.z - z_exp2) > _TOLERANCIA_COTA:
                continue

        # Proyectar endpoints al plano del techo
        proj1 = proyectar_al_plano(p1.x, p1.y, p1.z, normal, punto_plano)
        proj2 = proyectar_al_plano(p2.x, p2.y, p2.z, normal, punto_plano)

        is1 = obtener_is_de_punto(proj1[0], proj1[1], subdivisiones)
        is2 = obtener_is_de_punto(proj2[0], proj2[1], subdivisiones)

        if is1 == is2:
            continue  # mismo IS (o ambos en margen) — no hay cruce

        # Recoger TODOS los t de interseccion con bordes de todos los IS
        todos_t: List[float] = []
        for is_data in subdivisiones:
            xmin, xmax, ymin, ymax = _is_bounds(is_data)
            ts = _intersecciones_segmento_rect(
                proj1[0], proj1[1], proj2[0], proj2[1],
                xmin, ymin, xmax, ymax
            )
            todos_t.extend(ts)

        todos_t = sorted(set(todos_t))

        # Si no hay intersecciones pero IS cambia, poner U en el punto medio
        if not todos_t:
            t_u = 0.5
            ux = p1.x + t_u * (p2.x - p1.x)
            uy = p1.y + t_u * (p2.y - p1.y)
            uz = p1.z + t_u * (p2.z - p1.z)
            punto_u = Punto3D(x=ux, y=uy, z=uz, id=label_sub('U', camino_idx, contador_u))
            puntos_u.append({
                'indice_segmento': i, 't': t_u,
                'is_origen': is1, 'is_destino': is2, 'punto': punto_u,
            })
            contador_u += 1
            continue

        # Construir intervalos con su IS
        puntos_muestra = [0.0] + todos_t + [1.0]
        dx_proj = proj2[0] - proj1[0]
        dy_proj = proj2[1] - proj1[1]

        intervalos: List[Tuple[float, float, Optional[str]]] = []
        for k in range(len(puntos_muestra) - 1):
            t_mid = (puntos_muestra[k] + puntos_muestra[k + 1]) / 2.0
            x_mid = proj1[0] + t_mid * dx_proj
            y_mid = proj1[1] + t_mid * dy_proj
            is_mid = obtener_is_de_punto(x_mid, y_mid, subdivisiones)
            intervalos.append((puntos_muestra[k], puntos_muestra[k + 1], is_mid))

        # Crear U en cada intervalo de margen (is = None)
        for idx_iv, (t_start, t_end, is_iv) in enumerate(intervalos):
            if is_iv is not None:
                continue  # dentro de un IS, no necesita U

            # Buscar IS vecino antes y despues
            is_antes = None
            for j in range(idx_iv - 1, -1, -1):
                if intervalos[j][2] is not None:
                    is_antes = intervalos[j][2]
                    break
            if is_antes is None:
                is_antes = is1  # IS del endpoint de inicio

            is_despues = None
            for j in range(idx_iv + 1, len(intervalos)):
                if intervalos[j][2] is not None:
                    is_despues = intervalos[j][2]
                    break
            if is_despues is None:
                is_despues = is2  # IS del endpoint final

            t_u = (t_start + t_end) / 2.0
            ux = p1.x + t_u * (p2.x - p1.x)
            uy = p1.y + t_u * (p2.y - p1.y)
            uz = p1.z + t_u * (p2.z - p1.z)

            punto_u = Punto3D(x=ux, y=uy, z=uz, id=label_sub('U', camino_idx, contador_u))
            puntos_u.append({
                'indice_segmento': i, 't': t_u,
                'is_origen': is_antes, 'is_destino': is_despues,
                'punto': punto_u,
            })
            contador_u += 1

    return puntos_u


# ---------------------------------------------------------------------------
# Filtrar puntos U por distancia minima (greedy desde A)
# ---------------------------------------------------------------------------

def _distancia_en_camino(seg_lengths: List[float],
                         seg_a: int, t_a: float,
                         seg_b: int, t_b: float) -> float:
    """Calcula la distancia a lo largo del camino entre dos puntos parametricos."""
    if seg_a == seg_b:
        return abs(t_b - t_a) * seg_lengths[seg_a]
    dist = (1.0 - t_a) * seg_lengths[seg_a]
    for i in range(seg_a + 1, seg_b):
        dist += seg_lengths[i]
    dist += t_b * seg_lengths[seg_b]
    return dist


def filtrar_puntos_u_por_distancia(camino: List[Punto3D],
                                   puntos_u_info: List[Dict],
                                   distancia_minima: float,
                                   camino_idx: int = None) -> List[Dict]:
    """Filtra puntos U cuya distancia al ancla anterior (A o ultimo U valido)
    sea menor a ``distancia_minima`` (en mm).

    Algoritmo greedy:
        1. Ancla = A (inicio del camino).
        2. Para cada U en orden: si dist(ancla, U) < min → eliminar U.
           Si >= min → conservar U y mover ancla a este U.
        3. Verificar tramo final: si dist(ultimo_U, B) < min → eliminar ultimo U.
        4. Renumerar los U restantes como U1, U2, ...
    """
    if not puntos_u_info or distancia_minima <= 0:
        return puntos_u_info

    # Precalcular longitudes de cada segmento del camino original
    seg_lengths: List[float] = []
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i + 1]
        d = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)
        seg_lengths.append(d)

    # Ancla inicial = punto A (seg 0, t 0)
    anchor_seg = 0
    anchor_t = 0.0

    filtrados: List[Dict] = []
    for u in puntos_u_info:
        u_seg = u['indice_segmento']
        u_t = u['t']
        dist = _distancia_en_camino(seg_lengths, anchor_seg, anchor_t, u_seg, u_t)
        if dist >= distancia_minima:
            filtrados.append(u)
            anchor_seg = u_seg
            anchor_t = u_t

    # Validar tramo final: dist(ultimo_U, B) >= distancia_minima
    # B esta en seg_final (ultimo segmento), t = 1.0
    while filtrados:
        ultimo = filtrados[-1]
        u_seg = ultimo['indice_segmento']
        u_t = ultimo['t']
        seg_final = len(seg_lengths) - 1
        dist_a_b = _distancia_en_camino(seg_lengths, u_seg, u_t, seg_final, 1.0)
        if dist_a_b >= distancia_minima:
            break
        # Tramo final muy corto, eliminar este U
        filtrados.pop()

    # Renumerar U1, U2, ... (con camino_idx si aplica)
    for i, u in enumerate(filtrados):
        u['punto'].id = label_sub('U', camino_idx, i + 1)

    return filtrados


# ---------------------------------------------------------------------------
# Insertar puntos U en el camino (sin alterar el camino original)
# ---------------------------------------------------------------------------

def insertar_puntos_u(camino: List[Punto3D],
                      puntos_u: List[Dict]) -> List[Punto3D]:
    """Devuelve una NUEVA lista de puntos con los U insertados en orden."""
    if not puntos_u:
        return list(camino)

    # Agrupar U por indice de segmento, ordenados por t
    u_por_seg: Dict[int, List[Dict]] = {}
    for u in puntos_u:
        idx = u['indice_segmento']
        u_por_seg.setdefault(idx, []).append(u)
    for idx in u_por_seg:
        u_por_seg[idx].sort(key=lambda d: d['t'])

    resultado: List[Punto3D] = []
    for i in range(len(camino)):
        resultado.append(camino[i])
        if i in u_por_seg:
            for u in u_por_seg[i]:
                resultado.append(u['punto'])

    return resultado


# ---------------------------------------------------------------------------
# Clasificacion de tipo de nodo
# ---------------------------------------------------------------------------

def _tipo_nodo(id_str: str) -> str:
    """Determina el tipo de nodo segun su ID.
    
    Soporta IDs con subindices Unicode: A₁, B₂, C₁₋₁, O₁₋₂, U₂₋₁, etc.
    """
    if not id_str:
        return 'codo'
    first = id_str[0].upper()
    if first == 'A':
        return 'inicio'
    if first == 'B':
        return 'final'
    if first == 'O':
        return 'obligatorio'
    if first == 'L':
        return 'libre'
    if first == 'S':
        return 'codo'
    if first == 'U':
        return 'union'
    if first == 'C':
        return 'codo'
    return 'codo'


# ---------------------------------------------------------------------------
# Generacion del grafo JSON
# ---------------------------------------------------------------------------

def _id_a_ascii(id_unicode: str) -> str:
    """Convierte ID con subindices Unicode a formato ASCII para JSON.
    
    Ejemplos:
        A₁ -> A1
        C₁₋₂ -> C1-2
        O₂₋₃ -> O2-3
        U₁₋₁ -> U1-1
    """
    if not id_unicode:
        return id_unicode
    
    # Mapeo de subindices Unicode a ASCII
    sub_map = str.maketrans('₀₁₂₃₄₅₆₇₈₉₋', '0123456789-')
    return id_unicode.translate(sub_map)


def generar_grafo_json(camino_con_u: List[Punto3D],
                       subdivisiones: List[Dict],
                       normal: np.ndarray,
                       punto_plano: np.ndarray) -> Dict[str, Any]:
    """Genera el grafo de nodos y segmentos con asignacion de IS.

    Retorna dict listo para serializar a JSON:
        { nodos: [...], segmentos: [...] }
    """
    nodos: List[Dict] = []
    segmentos: List[Dict] = []

    ultimo_is = None
    for idx, p in enumerate(camino_con_u):
        proj = proyectar_al_plano(p.x, p.y, p.z, normal, punto_plano)
        is_id = obtener_is_de_punto(proj[0], proj[1], subdivisiones)

        # Puntos U caen en el borde entre IS; heredar IS del punto anterior
        if is_id is None and ultimo_is is not None:
            is_id = ultimo_is
        if is_id is not None:
            ultimo_is = is_id

        ant = [_id_a_ascii(camino_con_u[idx - 1].id)] if idx > 0 else []
        sig = [_id_a_ascii(camino_con_u[idx + 1].id)] if idx < len(camino_con_u) - 1 else []

        nodos.append({
            'id': _id_a_ascii(p.id) or f'P{idx}',
            'tipo': _tipo_nodo(p.id),
            'coordenadas': {'x': round(p.x, 1), 'y': round(p.y, 1), 'z': round(p.z, 1)},
            'IS': is_id,
            'anteriores': ant,
            'siguientes': sig,
        })

    for idx in range(len(camino_con_u) - 1):
        n1 = camino_con_u[idx]
        n2 = camino_con_u[idx + 1]

        # IS del segmento = IS del primer punto que tenga IS, luego del segundo
        proj1 = proyectar_al_plano(n1.x, n1.y, n1.z, normal, punto_plano)
        proj2 = proyectar_al_plano(n2.x, n2.y, n2.z, normal, punto_plano)
        is_seg = obtener_is_de_punto(proj1[0], proj1[1], subdivisiones)
        if is_seg is None:
            is_seg = obtener_is_de_punto(proj2[0], proj2[1], subdivisiones)

        segmentos.append({
            'id': idx + 1,
            'n1_id': _id_a_ascii(n1.id) or f'P{idx}',
            'n2_id': _id_a_ascii(n2.id) or f'P{idx + 1}',
            'IS': is_seg,
        })

    return {'nodos': nodos, 'segmentos': segmentos}


# ---------------------------------------------------------------------------
# Funcion principal
# ---------------------------------------------------------------------------

def procesar_asignacion_is(camino: List[Punto3D],
                           subdivisiones: List[Dict],
                           vertices_techo: List[List[float]],
                           z_eje_fn=None,
                           distancia_minima_u: float = 0,
                           camino_idx: int = None
                           ) -> Dict[str, Any]:
    """Punto de entrada: asigna IS, inserta U, genera grafo.

    Args:
        camino: lista de Punto3D (ruta validada)
        subdivisiones: lista de dicts con 'id' y 'vertices'
        vertices_techo: vertices del techo para calcular plano
        z_eje_fn: opcional, callable(x, y) -> float con la Z esperada en la cota.
                  Si se provee, los puntos U solo se generan en segmentos al ras.
        distancia_minima_u: distancia minima (mm) entre A y primer U, y entre
                            U consecutivos. Los U que no cumplan se eliminan.
                            0 = sin filtro (ej. subtipo 90°).

    Returns:
        dict con:
            'grafo': {nodos, segmentos}
            'puntos_u': lista de Punto3D (para visualizacion)
            'camino_con_u': camino extendido con puntos U insertados
    """
    normal = _calcular_normal_techo(vertices_techo)
    punto_plano = np.array(vertices_techo[0])

    # 1. Encontrar puntos U (filtrados por cota si z_eje_fn se provee)
    puntos_u_info = encontrar_puntos_union(camino, subdivisiones, normal, punto_plano, z_eje_fn=z_eje_fn, camino_idx=camino_idx)

    # 2. Filtrar por distancia minima (greedy desde A)
    if distancia_minima_u > 0:
        puntos_u_info = filtrar_puntos_u_por_distancia(camino, puntos_u_info, distancia_minima_u, camino_idx=camino_idx)

    # 3. Insertar U en el camino
    camino_con_u = insertar_puntos_u(camino, puntos_u_info)

    # 3. Generar grafo
    grafo = generar_grafo_json(camino_con_u, subdivisiones, normal, punto_plano)

    # Extraer solo los Punto3D de U para visualizacion
    puntos_u_vis = [u['punto'] for u in puntos_u_info]

    return {
        'grafo': grafo,
        'puntos_u': puntos_u_vis,
        'camino_con_u': camino_con_u,
    }
