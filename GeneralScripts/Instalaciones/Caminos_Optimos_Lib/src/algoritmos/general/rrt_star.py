"""
RRT* (Rapidly-exploring Random Tree Star) para planificacion de tuberias 3D.

Nivel 2 del planificador jerarquico:
- Encuentra el camino optimo entre dos puntos
- Respeta restricciones de angulo (codos discretos)
- Evita colisiones con obstaculos
- Minimiza longitud total del camino

Restricciones DURAS (rechazo si se violan):
- Angulo entre segmentos consecutivos debe ser valido
- Longitud minima de segmento
- Sin colision con obstaculos

Arquitectura:
  Fase 1: RRT* en plano XY evitando obstaculos 'rodear'
  Fase 2: Post-proceso para insertar saltos sobre obstaculos 'saltar'
"""

import math
import random
from typing import List, Optional, Tuple
from ...modelos import Punto3D
from .geometria import segmento_cruza_bbox, LONGITUD_MINIMA


# ---------------------------------------------------------------------------
# Nodo del arbol RRT*
# ---------------------------------------------------------------------------

class NodoRRT:
    """Nodo del arbol RRT*."""
    __slots__ = ['x', 'y', 'padre', 'costo', 'dir_entrada', 'hijos']

    def __init__(self, x: float, y: float, padre: 'NodoRRT' = None, costo: float = 0.0):
        self.x = x
        self.y = y
        self.padre = padre
        self.costo = costo
        self.dir_entrada: Optional[float] = None  # direccion de llegada (grados 0-360)
        self.hijos: List['NodoRRT'] = []


# ---------------------------------------------------------------------------
# Funciones de utilidad geometrica
# ---------------------------------------------------------------------------

def _angulo_xy(dx: float, dy: float) -> Optional[float]:
    """Angulo en grados [0, 360) de un vector XY. None si longitud ~0."""
    if abs(dx) < 0.5 and abs(dy) < 0.5:
        return None
    a = math.degrees(math.atan2(dy, dx))
    return a % 360


def _diff_angular(a: float, b: float) -> float:
    """Diferencia angular minima entre dos angulos (0-180)."""
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def _es_direccion_valida(ang: float, direcciones: List[float], tol: float = 1.0) -> bool:
    """Verifica si un angulo coincide con alguna direccion valida."""
    for d in direcciones:
        if _diff_angular(ang, d) <= tol:
            return True
    return False


def _snap_direccion(ang: float, direcciones: List[float]) -> float:
    """Ajusta un angulo a la direccion valida mas cercana."""
    return min(direcciones, key=lambda d: _diff_angular(d, ang))


def _direcciones_permitidas(
    direcciones: List[float],
    dir_entrada: Optional[float],
    angulos_codo: List[int]
) -> List[float]:
    """
    Filtra direcciones que forman un angulo valido con la direccion de entrada.

    Para el primer segmento (dir_entrada=None), todas las direcciones son validas.
    Para segmentos siguientes, el angulo entre vectores debe ser 0 o un codo permitido.
    """
    if dir_entrada is None:
        return list(direcciones)

    validas = []
    for d in direcciones:
        ang_entre = _diff_angular(d, dir_entrada)
        # 0° (recto) siempre valido
        if ang_entre < 1.0:
            validas.append(d)
            continue
        # Cada angulo de codo
        for codo in angulos_codo:
            if abs(ang_entre - codo) < 1.0:
                validas.append(d)
                break
    return validas


def _angulo_transicion_valido(
    dir_entrada: Optional[float],
    dir_salida: float,
    angulos_codo: List[int]
) -> bool:
    """Verifica si la transicion de dir_entrada a dir_salida es valida."""
    if dir_entrada is None:
        return True
    ang = _diff_angular(dir_entrada, dir_salida)
    if ang < 1.0:
        return True
    for codo in angulos_codo:
        if abs(ang - codo) < 1.0:
            return True
    return False


def _segmento_colisiona_2d(
    x1: float, y1: float, x2: float, y2: float,
    bboxes: List[dict], radio: float
) -> bool:
    """Verifica colision de un segmento 2D con bounding boxes (ignora Z)."""
    z_dummy = 0.0
    for bb in bboxes:
        # Crear bbox expandido que ignore Z
        bb_expandido = dict(bb)
        bb_expandido['z_min'] = -1e6
        bb_expandido['z_max'] = 1e6
        if segmento_cruza_bbox(x1, y1, z_dummy, x2, y2, z_dummy, bb_expandido):
            return True
    return False


# ---------------------------------------------------------------------------
# Consultas al arbol
# ---------------------------------------------------------------------------

def _nearest(nodos: List[NodoRRT], x: float, y: float) -> NodoRRT:
    """Encuentra el nodo mas cercano a (x, y)."""
    mejor = nodos[0]
    mejor_d2 = (mejor.x - x) ** 2 + (mejor.y - y) ** 2
    for n in nodos[1:]:
        d2 = (n.x - x) ** 2 + (n.y - y) ** 2
        if d2 < mejor_d2:
            mejor_d2 = d2
            mejor = n
    return mejor


def _near(nodos: List[NodoRRT], x: float, y: float, radio: float) -> List[NodoRRT]:
    """Encuentra todos los nodos dentro de un radio."""
    r2 = radio * radio
    return [n for n in nodos if (n.x - x) ** 2 + (n.y - y) ** 2 <= r2]


def _propagar_costo(nodo: NodoRRT) -> None:
    """Propaga actualizacion de costo a hijos recursivamente."""
    for hijo in nodo.hijos:
        d = math.sqrt((nodo.x - hijo.x) ** 2 + (nodo.y - hijo.y) ** 2)
        hijo.costo = nodo.costo + d
        _propagar_costo(hijo)


# ---------------------------------------------------------------------------
# Conexion al destino
# ---------------------------------------------------------------------------

def _intentar_conectar_meta(
    nodo: NodoRRT,
    fin_x: float, fin_y: float,
    direcciones: List[float],
    angulos_codo: List[int],
    bboxes: List[dict],
    radio: float,
    long_min: float
) -> Optional[Tuple[List[Tuple[float, float]], float]]:
    """
    Intenta conectar un nodo al destino final.

    Prueba:
    1. Conexion directa (1 segmento)
    2. Conexion en L (2 segmentos con codo valido)

    Returns:
        (lista de puntos (x,y), costo) o None
    """
    dx = fin_x - nodo.x
    dy = fin_y - nodo.y
    dist = math.sqrt(dx * dx + dy * dy)

    if dist < 1.0:
        return ([], 0.0)

    # --- 1. Conexion directa ---
    dir_meta = _angulo_xy(dx, dy)
    if dir_meta is not None and _es_direccion_valida(dir_meta, direcciones, 0.1):
        if _angulo_transicion_valido(nodo.dir_entrada, dir_meta, angulos_codo):
            if dist >= long_min - 1:
                if not _segmento_colisiona_2d(nodo.x, nodo.y, fin_x, fin_y, bboxes, radio):
                    return ([(fin_x, fin_y)], dist)

    # --- 2. Conexion en L (2 segmentos) ---
    dirs_validas = _direcciones_permitidas(direcciones, nodo.dir_entrada, angulos_codo)

    mejor = None
    mejor_costo = float('inf')

    for d1 in dirs_validas:
        r1 = math.radians(d1)
        ux1, uy1 = math.cos(r1), math.sin(r1)

        for d2 in direcciones:
            # Verificar que d2 forme angulo valido con d1
            if not _angulo_transicion_valido(d1, d2, angulos_codo):
                continue

            r2 = math.radians(d2)
            ux2, uy2 = math.cos(r2), math.sin(r2)

            # Resolver: t1*(ux1,uy1) + t2*(ux2,uy2) = (dx, dy)
            det = ux1 * uy2 - ux2 * uy1
            if abs(det) < 0.001:
                continue

            t1 = (dx * uy2 - dy * ux2) / det
            t2 = (ux1 * dy - uy1 * dx) / det

            if t1 < long_min - 1 or t2 < long_min - 1:
                continue

            costo = t1 + t2
            if costo >= mejor_costo:
                continue

            # Punto intermedio
            mx = nodo.x + ux1 * t1
            my = nodo.y + uy1 * t1

            # Verificar colisiones
            if _segmento_colisiona_2d(nodo.x, nodo.y, mx, my, bboxes, radio):
                continue
            if _segmento_colisiona_2d(mx, my, fin_x, fin_y, bboxes, radio):
                continue

            mejor = [(mx, my), (fin_x, fin_y)]
            mejor_costo = costo

    if mejor is not None:
        return (mejor, mejor_costo)

    # --- 3. Conexion en 3 segmentos (S-shape) ---
    for d1 in dirs_validas:
        r1 = math.radians(d1)
        ux1, uy1 = math.cos(r1), math.sin(r1)

        # Avanzar una distancia fija en d1
        for t1 in [long_min, long_min * 2, long_min * 3]:
            mx1 = nodo.x + ux1 * t1
            my1 = nodo.y + uy1 * t1

            if _segmento_colisiona_2d(nodo.x, nodo.y, mx1, my1, bboxes, radio):
                continue

            # Desde mx1, intentar 2 segmentos al destino
            sub_dx = fin_x - mx1
            sub_dy = fin_y - my1
            sub_dist = math.sqrt(sub_dx ** 2 + sub_dy ** 2)

            if sub_dist < long_min:
                continue

            dirs_desde_d1 = _direcciones_permitidas(direcciones, d1, angulos_codo)

            for d2 in dirs_desde_d1:
                r2 = math.radians(d2)
                ux2, uy2 = math.cos(r2), math.sin(r2)

                for d3 in direcciones:
                    if not _angulo_transicion_valido(d2, d3, angulos_codo):
                        continue

                    r3 = math.radians(d3)
                    ux3, uy3 = math.cos(r3), math.sin(r3)

                    det = ux2 * uy3 - ux3 * uy2
                    if abs(det) < 0.001:
                        continue

                    t2 = (sub_dx * uy3 - sub_dy * ux3) / det
                    t3 = (ux2 * sub_dy - uy2 * sub_dx) / det

                    if t2 < long_min - 1 or t3 < long_min - 1:
                        continue

                    costo_total = t1 + t2 + t3
                    if costo_total >= mejor_costo:
                        continue

                    mx2 = mx1 + ux2 * t2
                    my2 = my1 + uy2 * t2

                    if _segmento_colisiona_2d(mx1, my1, mx2, my2, bboxes, radio):
                        continue
                    if _segmento_colisiona_2d(mx2, my2, fin_x, fin_y, bboxes, radio):
                        continue

                    mejor = [(mx1, my1), (mx2, my2), (fin_x, fin_y)]
                    mejor_costo = costo_total

    if mejor is not None:
        return (mejor, mejor_costo)

    return None


# ---------------------------------------------------------------------------
# Extraccion de camino
# ---------------------------------------------------------------------------

def _extraer_camino(nodo: NodoRRT) -> List[Tuple[float, float]]:
    """Extrae el camino desde la raiz hasta el nodo dado."""
    camino = []
    actual = nodo
    while actual is not None:
        camino.append((actual.x, actual.y))
        actual = actual.padre
    camino.reverse()
    return camino


# ---------------------------------------------------------------------------
# Algoritmo principal RRT*
# ---------------------------------------------------------------------------

def planificar_tramo_rrt(
    inicio: Punto3D,
    fin: Punto3D,
    bboxes_rodear: List[dict],
    bboxes_saltar: List[dict],
    direcciones: List[float],
    angulos_codo: List[int],
    radio_tubo: float,
    longitud_minima: float,
    bounds: Tuple[float, float, float, float],
    max_iter: int = 5000,
    dir_entrada: Optional[float] = None
) -> Optional[List[Punto3D]]:
    """
    Planifica un tramo usando RRT* con restricciones de tuberia.

    Fase 1: RRT* en plano XY evitando obstaculos 'rodear'
    Fase 2: Post-proceso para insertar saltos sobre obstaculos 'saltar'

    Args:
        inicio: Punto de partida
        fin: Punto de destino
        bboxes_rodear: Bounding boxes de obstaculos a rodear (barreras)
        bboxes_saltar: Bounding boxes de obstaculos a saltar (se ignoran en XY)
        direcciones: Direcciones de movimiento validas (grados)
        angulos_codo: Angulos de codo permitidos
        radio_tubo: Radio de la tuberia
        longitud_minima: Longitud minima de segmento
        bounds: (x_min, x_max, y_min, y_max) del espacio de trabajo
        max_iter: Maximo de iteraciones

    Returns:
        Lista de Punto3D o None si no encontro camino
    """
    # --- Intento rapido: conexion directa ---
    # Solo si no hay obstaculos saltar/bajar que deban cruzarse
    # (el atajo rapido los esquiva; se necesita el RRT* completo con bias)
    if not bboxes_saltar:
        rapido = _intentar_conexion_directa(
            inicio, fin, direcciones, angulos_codo,
            bboxes_rodear, radio_tubo, longitud_minima,
            dir_entrada=dir_entrada
        )
        if rapido is not None:
            return rapido

    # --- Parametros RRT* ---
    dist_total = math.sqrt((fin.x - inicio.x) ** 2 + (fin.y - inicio.y) ** 2)
    step_min = longitud_minima
    step_max = max(2000.0, dist_total * 0.4)
    radio_rewire = step_max * 1.5
    goal_tolerance = step_max * 1.5
    goal_bias = 0.15

    x_min, x_max, y_min, y_max = bounds
    # Contraer bounds hacia adentro por radio_tubo para que el cuerpo
    # del tubo no sobresalga del techo.  Esto fuerza al RRT* a buscar
    # rutas interiores (p.ej. rodear por abajo y saltar otros tubos)
    # en lugar de salirse del techo.
    margen_borde = radio_tubo
    x_min_exp = x_min + margen_borde
    x_max_exp = x_max - margen_borde
    y_min_exp = y_min + margen_borde
    y_max_exp = y_max - margen_borde

    # --- Bias hacia obstaculos saltar/bajar (forzar que el arbol crezca por ahi) ---
    centros_obs = [(bb['centro_x'], bb['centro_y']) for bb in bboxes_saltar]
    obs_bias = 0.15 if centros_obs else 0.0
    obs_jitter = max(500.0, dist_total * 0.1)  # jitter alrededor del centro
    
    # --- Inicializar arbol ---
    raiz = NodoRRT(inicio.x, inicio.y, costo=0.0)
    raiz.dir_entrada = dir_entrada  # respetar direccion de entrada del tramo anterior
    nodos = [raiz]

    mejor_meta = None
    mejor_costo_meta = float('inf')

    for it in range(max_iter):
        # --- Muestreo ---
        r = random.random()
        if r < goal_bias:
            rx, ry = fin.x, fin.y
        elif r < goal_bias + obs_bias and centros_obs:
            cx, cy = random.choice(centros_obs)
            rx = cx + random.uniform(-obs_jitter, obs_jitter)
            ry = cy + random.uniform(-obs_jitter, obs_jitter)
        else:
            rx = random.uniform(x_min_exp, x_max_exp)
            ry = random.uniform(y_min_exp, y_max_exp)

        # --- Nearest ---
        nodo_cercano = _nearest(nodos, rx, ry)

        # --- Steer ---
        dir_deseada = _angulo_xy(rx - nodo_cercano.x, ry - nodo_cercano.y)
        if dir_deseada is None:
            continue

        dirs_validas = _direcciones_permitidas(
            direcciones, nodo_cercano.dir_entrada, angulos_codo
        )
        if not dirs_validas:
            continue

        mejor_dir = min(dirs_validas, key=lambda d: _diff_angular(d, dir_deseada))

        # --- Extend ---
        dist_muestra = math.sqrt((rx - nodo_cercano.x) ** 2 + (ry - nodo_cercano.y) ** 2)
        step = max(step_min, min(step_max, dist_muestra))

        rad = math.radians(mejor_dir)
        nx = nodo_cercano.x + step * math.cos(rad)
        ny = nodo_cercano.y + step * math.sin(rad)

        # Bounds check
        if not (x_min_exp <= nx <= x_max_exp and y_min_exp <= ny <= y_max_exp):
            continue

        # Collision check
        if _segmento_colisiona_2d(nodo_cercano.x, nodo_cercano.y, nx, ny, bboxes_rodear, radio_tubo):
            continue

        # --- Best parent (RRT*) ---
        nuevo_costo = nodo_cercano.costo + step
        vecinos = _near(nodos, nx, ny, radio_rewire)

        mejor_padre = nodo_cercano
        mejor_costo = nuevo_costo
        mejor_dir_final = mejor_dir

        for vec in vecinos:
            d_vec = math.sqrt((vec.x - nx) ** 2 + (vec.y - ny) ** 2)
            if d_vec < step_min - 1:
                continue

            costo_via = vec.costo + d_vec
            if costo_via >= mejor_costo:
                continue

            dir_vec = _angulo_xy(nx - vec.x, ny - vec.y)
            if dir_vec is None:
                continue
            if not _es_direccion_valida(dir_vec, direcciones, 0.1):
                continue
            if not _angulo_transicion_valido(vec.dir_entrada, dir_vec, angulos_codo):
                continue
            if _segmento_colisiona_2d(vec.x, vec.y, nx, ny, bboxes_rodear, radio_tubo):
                continue

            mejor_padre = vec
            mejor_costo = costo_via
            mejor_dir_final = _snap_direccion(dir_vec, direcciones)

        # --- Add node ---
        nodo_nuevo = NodoRRT(nx, ny, mejor_padre, mejor_costo)
        nodo_nuevo.dir_entrada = mejor_dir_final
        nodos.append(nodo_nuevo)
        mejor_padre.hijos.append(nodo_nuevo)

        # --- Rewire ---
        for vec in vecinos:
            if vec is mejor_padre or vec is raiz:
                continue

            d_nv = math.sqrt((nodo_nuevo.x - vec.x) ** 2 + (nodo_nuevo.y - vec.y) ** 2)
            if d_nv < step_min - 1:
                continue

            costo_via_nuevo = nodo_nuevo.costo + d_nv
            if costo_via_nuevo >= vec.costo:
                continue

            dir_nv = _angulo_xy(vec.x - nodo_nuevo.x, vec.y - nodo_nuevo.y)
            if dir_nv is None:
                continue
            if not _es_direccion_valida(dir_nv, direcciones, 0.1):
                continue
            if not _angulo_transicion_valido(nodo_nuevo.dir_entrada, dir_nv, angulos_codo):
                continue
            if _segmento_colisiona_2d(nodo_nuevo.x, nodo_nuevo.y, vec.x, vec.y, bboxes_rodear, radio_tubo):
                continue

            # Rewire
            if vec.padre:
                vec.padre.hijos.remove(vec)
            vec.padre = nodo_nuevo
            vec.costo = costo_via_nuevo
            vec.dir_entrada = _snap_direccion(dir_nv, direcciones)
            nodo_nuevo.hijos.append(vec)
            _propagar_costo(vec)

        # --- Goal check ---
        dist_meta = math.sqrt((nodo_nuevo.x - fin.x) ** 2 + (nodo_nuevo.y - fin.y) ** 2)

        if dist_meta <= goal_tolerance:
            resultado = _intentar_conectar_meta(
                nodo_nuevo, fin.x, fin.y,
                direcciones, angulos_codo,
                bboxes_rodear, radio_tubo, longitud_minima
            )
            if resultado is not None:
                pts_conexion, costo_conexion = resultado
                costo_total = nodo_nuevo.costo + costo_conexion
                if costo_total < mejor_costo_meta:
                    mejor_costo_meta = costo_total
                    mejor_meta = (nodo_nuevo, pts_conexion)

    # --- Extraer resultado ---
    if mejor_meta is None:
        return None

    nodo_final, puntos_conexion = mejor_meta
    camino_xy = _extraer_camino(nodo_final) + puntos_conexion

    # Convertir a Punto3D (Z interpolado por distancia acumulada a lo largo del camino)
    # Usar distancia acumulada (no recta) para Z uniforme y angulos correctos
    dist_acum = [0.0]
    for i in range(1, len(camino_xy)):
        dx_seg = camino_xy[i][0] - camino_xy[i-1][0]
        dy_seg = camino_xy[i][1] - camino_xy[i-1][1]
        dist_acum.append(dist_acum[-1] + math.sqrt(dx_seg**2 + dy_seg**2))
    dist_path = dist_acum[-1] if dist_acum else 1.0

    resultado = []
    for i, (x, y) in enumerate(camino_xy):
        if i == 0:
            z = inicio.z
        elif i == len(camino_xy) - 1:
            z = fin.z
        else:
            if dist_path > 1:
                t = min(1.0, dist_acum[i] / dist_path)
                z = inicio.z + t * (fin.z - inicio.z)
            else:
                z = inicio.z
        resultado.append(Punto3D(id="", x=x, y=y, z=z))

    return resultado


def _intentar_conexion_directa(
    inicio: Punto3D, fin: Punto3D,
    direcciones: List[float], angulos_codo: List[int],
    bboxes: List[dict], radio: float, long_min: float,
    dir_entrada: Optional[float] = None
) -> Optional[List[Punto3D]]:
    """Intenta conexion directa sin RRT* (rapido para casos simples)."""
    dx = fin.x - inicio.x
    dy = fin.y - inicio.y
    dist = math.sqrt(dx * dx + dy * dy)

    if dist < 1:
        return [inicio, fin]

    # Intento 1: linea recta
    dir_meta = _angulo_xy(dx, dy)
    if dir_meta is not None and _es_direccion_valida(dir_meta, direcciones, 0.1):
        if _angulo_transicion_valido(dir_entrada, dir_meta, angulos_codo):
            if dist >= long_min - 1:
                if not _segmento_colisiona_2d(inicio.x, inicio.y, fin.x, fin.y, bboxes, radio):
                    return [inicio, fin]

    # Intento 2: dos segmentos (L-shape)
    mejor = None
    mejor_costo = float('inf')

    # Filtrar d1 segun dir_entrada
    dirs_d1 = _direcciones_permitidas(direcciones, dir_entrada, angulos_codo) if dir_entrada is not None else direcciones

    for d1 in dirs_d1:
        r1 = math.radians(d1)
        ux1, uy1 = math.cos(r1), math.sin(r1)

        for d2 in direcciones:
            if not _angulo_transicion_valido(d1, d2, angulos_codo):
                continue

            r2 = math.radians(d2)
            ux2, uy2 = math.cos(r2), math.sin(r2)

            det = ux1 * uy2 - ux2 * uy1
            if abs(det) < 0.001:
                continue

            t1 = (dx * uy2 - dy * ux2) / det
            t2 = (ux1 * dy - uy1 * dx) / det

            if t1 < long_min - 1 or t2 < long_min - 1:
                continue

            costo = t1 + t2
            if costo >= mejor_costo:
                continue

            mx = inicio.x + ux1 * t1
            my = inicio.y + uy1 * t1

            if _segmento_colisiona_2d(inicio.x, inicio.y, mx, my, bboxes, radio):
                continue
            if _segmento_colisiona_2d(mx, my, fin.x, fin.y, bboxes, radio):
                continue

            z_mid = (inicio.z + fin.z) / 2
            mejor = [inicio, Punto3D(id="C", x=mx, y=my, z=z_mid), fin]
            mejor_costo = costo

    return mejor
