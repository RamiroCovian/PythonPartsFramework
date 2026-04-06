"""
Generador de soportes de ventilacion - v20

ALGORITMO:
  Los soportes se colocan UNICAMENTE a lo largo del camino (recorrido
  del ducto), NO en toda la grilla del IS.

  Para cada segmento del camino:
    1. Determinar IS al que pertenece (desde grafo o por posicion).
    2. Determinar direccion del ducto (vertical/horizontal/diagonal).
    3. Buscar el par de tubos IS mas cercano que flanquea el ducto:
       - Ducto en Y -> par de tubos VERTICALES -> soportes HORIZONTALES
       - Ducto en X -> par de tubos HORIZONTALES -> soportes VERTICALES
    4. Calcular zona valida (overlap entre ducto y tubos ancla).
    5. Distribuir soportes cada 700-1200mm en la zona.

REGLAS:
  - Soporte de tubo a tubo, menor distancia posible (mas corto).
  - 90 grados respecto al tubo de anclaje.
  - Si solo 1 tubo disponible -> ZETA (un extremo libre).
  - No puede cruzar limites de IS.
  - OMEGA: B=680mm (separacion estandar 700mm), A=110mm.
  - ZETA: B=variable, A=110mm.
"""

import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Optional, Tuple, Any

from ..modelos.punto import Punto3D
from ..modelos.soporte import TuboIS, Soporte
from ..modelos.obstaculo import Obstaculo


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
DIST_MIN    = 700.0
DIST_MAX    = 1200.0
COTA_A      = 110.0
B_OMEGA_STD = 680.0
TOL_POS     = 25.0


# ---------------------------------------------------------------------------
# Z sobre el plano del techo
# ---------------------------------------------------------------------------

def _calcular_z_techo(x, y, vertices_techo):
    v0 = np.array(vertices_techo[0], dtype=float)
    v1 = np.array(vertices_techo[1], dtype=float)
    v2 = np.array(vertices_techo[2], dtype=float)
    n = np.cross(v1 - v0, v2 - v0)
    norma = np.linalg.norm(n)
    if norma > 1e-9:
        n = n / norma
    if n[2] < 0:
        n = -n
    a, b, c = float(n[0]), float(n[1]), float(n[2])
    if abs(c) < 0.001:
        return float(v0[2])
    d = float(np.dot(n, v0))
    return (d - a * x - b * y) / c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _xc(t):
    return (t.punto_inicio.x + t.punto_fin.x) / 2.0

def _yc(t):
    return (t.punto_inicio.y + t.punto_fin.y) / 2.0

def _rango_y(t):
    return (min(t.punto_inicio.y, t.punto_fin.y),
            max(t.punto_inicio.y, t.punto_fin.y))

def _rango_x(t):
    return (min(t.punto_inicio.x, t.punto_fin.x),
            max(t.punto_inicio.x, t.punto_fin.x))


# ---------------------------------------------------------------------------
# Asignar IS a cada segmento del camino
# ---------------------------------------------------------------------------

def _asignar_is_segmentos(camino_con_u, grafo, tubos_is):
    """
    Retorna lista de (p1, p2, is_id) para cada segmento del camino.

    Intenta usar grafo primero. Si falla, determina IS por posicion
    del punto medio respecto a los bounding boxes de los tubos por IS.
    """
    bbox_is = {}
    tubos_por_is = defaultdict(list)
    for t in tubos_is:
        tubos_por_is[t.is_id].append(t)

    for is_id, tubos in tubos_por_is.items():
        xs = [t.punto_inicio.x for t in tubos] + [t.punto_fin.x for t in tubos]
        ys = [t.punto_inicio.y for t in tubos] + [t.punto_fin.y for t in tubos]
        bbox_is[is_id] = {
            'x_min': min(xs), 'x_max': max(xs),
            'y_min': min(ys), 'y_max': max(ys),
        }

    def _is_de_punto(x, y):
        # Intento 1: dentro del bbox estricto (tolerancia pequeña)
        mejor, mejor_d = None, float('inf')
        for is_id, bb in bbox_is.items():
            cx = (bb['x_min'] + bb['x_max']) / 2
            cy = (bb['y_min'] + bb['y_max']) / 2
            if (bb['x_min'] - 50 <= x <= bb['x_max'] + 50 and
                bb['y_min'] - 50 <= y <= bb['y_max'] + 50):
                d = math.sqrt((x - cx)**2 + (y - cy)**2)
                if d < mejor_d:
                    mejor_d = d
                    mejor = is_id
        if mejor:
            return mejor
        # Intento 2: IS mas cercano por distancia (para puntos en margenes o gaps)
        for is_id, bb in bbox_is.items():
            cx = (bb['x_min'] + bb['x_max']) / 2
            cy = (bb['y_min'] + bb['y_max']) / 2
            # Distancia al borde del bbox (no al centro)
            dx_bb = max(bb['x_min'] - x, 0, x - bb['x_max'])
            dy_bb = max(bb['y_min'] - y, 0, y - bb['y_max'])
            d = math.sqrt(dx_bb**2 + dy_bb**2)
            if d < mejor_d:
                mejor_d = d
                mejor = is_id
        return mejor

    resultado_grafo = []
    if grafo and 'segmentos' in grafo:
        mapa = {p.id: p for p in camino_con_u if p.id}
        for seg in grafo['segmentos']:
            p1 = mapa.get(seg.get('n1_id'))
            p2 = mapa.get(seg.get('n2_id'))
            is_id = seg.get('IS')
            if p1 and p2 and is_id:
                resultado_grafo.append((p1, p2, is_id))

    if resultado_grafo:
        return resultado_grafo

    resultado = []
    for i in range(len(camino_con_u) - 1):
        p1, p2 = camino_con_u[i], camino_con_u[i + 1]
        mx = (p1.x + p2.x) / 2
        my = (p1.y + p2.y) / 2
        is_id = _is_de_punto(mx, my)
        if is_id:
            resultado.append((p1, p2, is_id))

    return resultado


# ---------------------------------------------------------------------------
# Buscar par de tubos ancla que flanquean el ducto
# ---------------------------------------------------------------------------

def _par_ancla_vertical(tubos_v, x_ducto):
    """Para ducto en Y: busca par de tubos V que flanquean x_ducto."""
    izq = sorted([t for t in tubos_v if _xc(t) <= x_ducto + TOL_POS],
                 key=lambda t: -_xc(t))
    der = sorted([t for t in tubos_v if _xc(t) >= x_ducto - TOL_POS],
                 key=lambda t: _xc(t))

    izq_real = [t for t in izq if _xc(t) < x_ducto - 1]
    der_real = [t for t in der if _xc(t) > x_ducto + 1]

    if izq_real and der_real:
        return (izq_real[0], der_real[0])
    if len(izq) >= 2:
        return (izq[0], izq[1])
    if len(der) >= 2:
        return (der[0], der[1])
    if izq:
        return (izq[0], None)
    if der:
        return (der[0], None)
    return None


def _par_ancla_horizontal(tubos_h, y_ducto):
    """Para ducto en X: busca par de tubos H que flanquean y_ducto."""
    arr = sorted([t for t in tubos_h if _yc(t) <= y_ducto + TOL_POS],
                 key=lambda t: -_yc(t))
    aba = sorted([t for t in tubos_h if _yc(t) >= y_ducto - TOL_POS],
                 key=lambda t: _yc(t))

    arr_real = [t for t in arr if _yc(t) < y_ducto - 1]
    aba_real = [t for t in aba if _yc(t) > y_ducto + 1]

    if arr_real and aba_real:
        return (arr_real[0], aba_real[0])
    if len(arr) >= 2:
        return (arr[0], arr[1])
    if len(aba) >= 2:
        return (aba[0], aba[1])
    if arr:
        return (arr[0], None)
    if aba:
        return (aba[0], None)
    return None


# ---------------------------------------------------------------------------
# Distribucion uniforme
# ---------------------------------------------------------------------------

def _distribuir(zona_ini, zona_fin):
    largo = zona_fin - zona_ini
    if largo < DIST_MIN * 0.3:
        return []
    media = (DIST_MIN + DIST_MAX) / 2.0
    n = max(1, round(largo / media))
    esp = largo / (n + 1)
    if esp > DIST_MAX:
        n = max(1, math.ceil(largo / DIST_MAX) - 1)
        esp = largo / (n + 1)
    elif esp < DIST_MIN and n > 1:
        n = max(1, math.floor(largo / DIST_MIN) - 1)
        esp = largo / (n + 1)
    return [zona_ini + i * esp for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# Punto sobre la linea del ducto en posicion t
# ---------------------------------------------------------------------------

def _punto_en_ducto(p1, p2, coord, ducto_en_y):
    """Dado un coord en el eje de avance, retorna (x, y) sobre el ducto."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    L = math.sqrt(dx*dx + dy*dy)
    if L < 1:
        return (p1.x, p1.y)

    if ducto_en_y:
        if abs(dy) < 1:
            return (p1.x, coord)
        t = (coord - p1.y) / dy
        t = max(0, min(1, t))
        return (p1.x + t * dx, coord)
    else:
        if abs(dx) < 1:
            return (coord, p1.y)
        t = (coord - p1.x) / dx
        t = max(0, min(1, t))
        return (coord, p1.y + t * dy)


# ---------------------------------------------------------------------------
# FUNCION PRINCIPAL
# ---------------------------------------------------------------------------

def generar_soportes(
    camino_con_u,
    grafo,
    tubos_is,
    obstaculos,
    subtipo,
    radio_tubo,
    vertices_techo,
    offset_eje,
):
    """
    Genera soportes a lo largo del camino del ducto.

    Para cada segmento del camino:
      1. Identifica IS.
      2. Busca par de tubos mas cercano flanqueando el ducto.
      3. Distribuye soportes cada 700-1200mm.
      4. Cada soporte es perpendicular a los tubos de anclaje.

    Args:
        camino_con_u: Lista de Punto3D del camino (con puntos U incluidos).
        grafo: Diccionario del grafo IS (con 'segmentos').
        tubos_is: Lista de TuboIS.
        obstaculos: Lista de Obstaculo.
        subtipo: Nombre del subtipo de tuberia.
        radio_tubo: Radio del tubo en mm.
        vertices_techo: Lista de vertices del techo [[x,y,z], ...].
        offset_eje: Distancia del eje del tubo al plano del techo.

    Returns:
        Lista de Soporte generados.
    """
    print("")
    print("  ################################################################")
    print("  #  GENERADOR SOPORTES v20 - SOLO A LO LARGO DEL CAMINO        #")
    print("  ################################################################")
    print("")

    if subtipo not in ('extraccion_impulsion',):
        print(f"  Subtipo '{subtipo}': sin soportes.")
        return []

    if not tubos_is:
        print("  *** Sin tubos IS.")
        return []

    if not camino_con_u or len(camino_con_u) < 2:
        print("  *** Camino vacio o insuficiente.")
        return []

    tubos_por_is = defaultdict(list)
    for t in tubos_is:
        tubos_por_is[t.is_id].append(t)

    segmentos = _asignar_is_segmentos(camino_con_u, grafo, tubos_is)

    print(f"  Camino: {len(camino_con_u)} puntos, {len(segmentos)} segmentos")
    for i, (p1, p2, is_id) in enumerate(segmentos):
        L = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2)
        print(f"    Seg {i+1}: {p1.id}({p1.x:.0f},{p1.y:.0f})"
              f" -> {p2.id}({p2.x:.0f},{p2.y:.0f})"
              f"  IS={is_id}  L={L:.0f}mm")

    soportes = []
    contador = 1

    for (p1, p2, is_id) in segmentos:
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        L_seg = math.sqrt(dx*dx + dy*dy)

        if L_seg < 50:
            continue

        tl = tubos_por_is.get(is_id, [])
        if not tl:
            print(f"    *** Sin tubos para IS '{is_id}'")
            continue

        tv = [t for t in tl if t.es_vertical]
        th = [t for t in tl if t.es_horizontal]

        ducto_en_y = abs(dy) >= abs(dx)

        if ducto_en_y:
            x_ducto = (p1.x + p2.x) / 2.0
            par = _par_ancla_vertical(tv, x_ducto)

            if par is None:
                print(f"    *** Sin tubos verticales en IS '{is_id}'")
                continue

            ta, tb = par
            orientacion = "horizontal"

            ducto_y = (min(p1.y, p2.y), max(p1.y, p2.y))
            tubo_y = _rango_y(ta)
            if tb:
                rb = _rango_y(tb)
                tubo_y = (max(tubo_y[0], rb[0]), min(tubo_y[1], rb[1]))

            zona_ini = max(ducto_y[0], tubo_y[0])
            zona_fin = min(ducto_y[1], tubo_y[1])

            if zona_fin - zona_ini < 100:
                continue

            xa = _xc(ta)
            xb = _xc(tb) if tb else xa
            sep = abs(xb - xa) if tb else 0

        else:
            y_ducto = (p1.y + p2.y) / 2.0
            par = _par_ancla_horizontal(th, y_ducto)

            if par is None:
                print(f"    *** Sin tubos horizontales en IS '{is_id}'")
                continue

            ta, tb = par
            orientacion = "vertical"

            ducto_x = (min(p1.x, p2.x), max(p1.x, p2.x))
            tubo_x = _rango_x(ta)
            if tb:
                rb = _rango_x(tb)
                tubo_x = (max(tubo_x[0], rb[0]), min(tubo_x[1], rb[1]))

            zona_ini = max(ducto_x[0], tubo_x[0])
            zona_fin = min(ducto_x[1], tubo_x[1])

            if zona_fin - zona_ini < 100:
                continue

            ya = _yc(ta)
            yb = _yc(tb) if tb else ya
            sep = abs(yb - ya) if tb else 0

        if tb:
            tipo_sp = "OMEGA"
            subtipo_sp = "Ventilación"
            cota_b = B_OMEGA_STD if abs(sep - 700) < 30 else round(sep, 1)
            print(f"\n    [{is_id}] Par: {ta.id} <-> {tb.id}"
                  f"  sep={sep:.0f}mm  B={cota_b:.0f}mm")
        else:
            tipo_sp = "ZETA"
            subtipo_sp = "VARIFIX"
            if ducto_en_y:
                dist_al_ducto = abs(_xc(ta) - x_ducto)
            else:
                dist_al_ducto = abs(_yc(ta) - y_ducto)
            cota_b = round(dist_al_ducto + radio_tubo + 10, 1)
            print(f"\n    [{is_id}] ZETA: {ta.id}  B={cota_b:.0f}mm")

        print(f"    Zona: [{zona_ini:.0f}, {zona_fin:.0f}]"
              f" = {zona_fin - zona_ini:.0f}mm")

        coords = _distribuir(zona_ini, zona_fin)
        if not coords:
            continue

        esp = (zona_fin - zona_ini) / (len(coords) + 1)
        print(f"    -> {len(coords)} soportes @{esp:.0f}mm")

        for coord in coords:
            if ducto_en_y:
                ducto_x_at_coord, _ = _punto_en_ducto(p1, p2, coord, True)
                z = _calcular_z_techo(xa, coord, vertices_techo)
                pos1 = Punto3D(x=xa, y=coord, z=z)
                pos2 = Punto3D(x=xb, y=coord, z=z) if tb else Punto3D(x=xa, y=coord, z=z)
            else:
                _, ducto_y_at_coord = _punto_en_ducto(p1, p2, coord, False)
                z = _calcular_z_techo(coord, ya, vertices_techo)
                pos1 = Punto3D(x=coord, y=ya, z=z)
                pos2 = Punto3D(x=coord, y=yb, z=z) if tb else Punto3D(x=coord, y=ya, z=z)

            sp = Soporte(
                id=f"SP{contador}",
                tipo=tipo_sp,
                subtipo=subtipo_sp,
                orientacion=orientacion,
                posicion1=pos1,
                posicion2=pos2,
                cota_a=COTA_A,
                cota_b=cota_b,
                segmento_id=0,
                is_id=is_id,
            )
            soportes.append(sp)

            print(f"       SP{contador:03d} {tipo_sp} {orientacion}"
                  f" ({pos1.x:.0f},{pos1.y:.0f})"
                  f"->({pos2.x:.0f},{pos2.y:.0f})"
                  f" B={cota_b:.0f}")
            contador += 1

    n_h = sum(1 for s in soportes if s.orientacion == 'horizontal')
    n_v = sum(1 for s in soportes if s.orientacion == 'vertical')
    n_om = sum(1 for s in soportes if s.tipo == 'OMEGA')
    n_ze = sum(1 for s in soportes if s.tipo == 'ZETA')
    print(f"\n  ================================================================")
    print(f"  TOTAL: {len(soportes)} soportes (H={n_h}, V={n_v})")
    print(f"         OMEGA={n_om}  ZETA={n_ze}")
    print(f"  Dist: [{DIST_MIN:.0f}, {DIST_MAX:.0f}]mm  A={COTA_A:.0f}mm")
    print(f"  ================================================================")
    return soportes
