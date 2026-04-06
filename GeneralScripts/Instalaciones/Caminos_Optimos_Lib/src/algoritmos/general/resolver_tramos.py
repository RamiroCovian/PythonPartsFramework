"""
Resolucion de tramos: fallback deterministico, insercion de saltos y aplicacion de estrategias.
"""

import math
from typing import List

from ...modelos import Punto3D
from .geometria import (
    LONGITUD_MINIMA, MARGEN_OBSTACULO,
    segmento_cruza_bbox, encontrar_obstaculos_en_segmento, longitud_ruta,
)
from .angulos import crear_ruta_directa
from .estrategias import calcular_salto, calcular_bajada, calcular_rodeo
from .manejo_obstaculos import obtener_modos


class BajarImposibleError(Exception):
    """Se lanza cuando no es posible bajar un obstaculo por restriccion de techo."""
    pass


def resolver_tramo_fallback(origen, destino, bboxes, radio_tubo,
                             angulos_codo, direcciones):
    """Fallback deterministico: descompone en segmentos alineados y aplica estrategias."""
    # Descomponer en segmentos alineados con direcciones validas
    ruta_base = crear_ruta_directa(origen, destino, direcciones)
    
    # Verificar si la ruta base tiene obstaculos
    tiene_obstaculos = False
    for seg_idx in range(len(ruta_base) - 1):
        p1, p2 = ruta_base[seg_idx], ruta_base[seg_idx + 1]
        if encontrar_obstaculos_en_segmento(
            p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bboxes
        ):
            tiene_obstaculos = True
            break
    
    if not tiene_obstaculos:
        return ruta_base
    
    # Resolver obstaculos POR SEGMENTO de la ruta descompuesta
    ruta_resultado = [ruta_base[0]]
    
    for seg_idx in range(len(ruta_base) - 1):
        seg_inicio = ruta_resultado[-1]
        seg_fin = ruta_base[seg_idx + 1]
        
        # Encontrar obstaculos en este segmento especifico
        obs_en_seg = encontrar_obstaculos_en_segmento(
            seg_inicio.x, seg_inicio.y, seg_inicio.z,
            seg_fin.x, seg_fin.y, seg_fin.z, bboxes
        )
        
        if not obs_en_seg:
            # Segmento limpio: agregar punto final directamente
            if seg_fin.distancia_a(ruta_resultado[-1]) > 1:
                ruta_resultado.append(seg_fin)
            continue
        
        # Ordenar obstaculos por distancia al inicio del segmento
        obs_en_seg.sort(key=lambda o: math.sqrt(
            (o['centro_x'] - seg_inicio.x)**2 + (o['centro_y'] - seg_inicio.y)**2
        ))
        
        # Resolver cada obstaculo en este segmento
        punto_actual = seg_inicio
        
        for obs in obs_en_seg:
            # Verificar si aun cruza desde punto_actual
            if not segmento_cruza_bbox(
                punto_actual.x, punto_actual.y, punto_actual.z,
                seg_fin.x, seg_fin.y, seg_fin.z, obs
            ):
                continue
            
            modos = obtener_modos(obs)
            
            mejor_ruta = None
            mejor_longitud = float('inf')
            
            for modo in modos:
                ruta_modo = aplicar_estrategia(
                    punto_actual, seg_fin, obs, bboxes,
                    radio_tubo, angulos_codo, modo
                )
                if ruta_modo and len(ruta_modo) >= 2:
                    lon = longitud_ruta(ruta_modo)
                    if lon < mejor_longitud:
                        mejor_longitud = lon
                        mejor_ruta = ruta_modo
            
            if mejor_ruta:
                # Agregar puntos intermedios (sin el ultimo = seg_fin)
                # para que punto_actual quede en el aterrizaje, no en el destino
                for p in mejor_ruta[1:-1]:
                    if (abs(p.x - ruta_resultado[-1].x) > 1 or
                        abs(p.y - ruta_resultado[-1].y) > 1 or
                        abs(p.z - ruta_resultado[-1].z) > 1):
                        ruta_resultado.append(p)
                punto_actual = ruta_resultado[-1]
        
        # Conectar al final del segmento si falta
        if seg_fin.distancia_a(ruta_resultado[-1]) > 10:
            ruta_resultado.append(seg_fin)
    
    return ruta_resultado


def insertar_saltos_en_ruta(ruta, bboxes_saltar, radio_tubo, angulos_codo, techo_z=None):
    """Post-proceso: inserta saltos en Z en segmentos que cruzan obstaculos saltar.
    Se aplica DESPUES del routing XY, de modo que cada segmento es recto y
    la transicion vertical mantiene angulos validos.
    
    Usa look-ahead: cuando un segmento cruza obstaculos, busca todos los
    segmentos contiguos que tambien cruzan y calcula UN salto para toda la zona,
    dando suficiente espacio para una geometria de salto correcta."""
    if not bboxes_saltar or not ruta or len(ruta) < 2:
        return ruta

    resultado = [ruta[0]]
    i = 0

    while i < len(ruta) - 1:
        p1 = resultado[-1]
        p2 = ruta[i + 1]

        obs_saltar = [bb for bb in bboxes_saltar
                      if segmento_cruza_bbox(p1.x, p1.y, p1.z,
                                             p2.x, p2.y, p2.z, bb)]

        if not obs_saltar:
            if p2.distancia_a(resultado[-1]) > 1:
                resultado.append(p2)
            i += 1
            continue

        # Look-ahead: buscar todos los segmentos contiguos que cruzan obstaculos
        todos_obs = list(obs_saltar)
        j = i + 1
        while j < len(ruta) - 1:
            seg_start = ruta[j]
            seg_end = ruta[j + 1]
            obs_next = [bb for bb in bboxes_saltar
                        if segmento_cruza_bbox(seg_start.x, seg_start.y, seg_start.z,
                                               seg_end.x, seg_end.y, seg_end.z, bb)]
            if not obs_next:
                break
            for ob in obs_next:
                if ob not in todos_obs:
                    todos_obs.append(ob)
            j += 1

        # Destino del salto: primer punto DESPUES de la zona de obstaculos
        destino_salto = ruta[j]

        # Fusionar todos los obstaculos cruzados en un unico bbox
        obs_fusionado = _fusionar_bboxes_saltar(todos_obs)

        modos = obtener_modos(obs_fusionado)
        mejor_ruta = None
        mejor_lon = float('inf')

        for modo in modos:
            ruta_modo = aplicar_estrategia(
                p1, destino_salto, obs_fusionado, bboxes_saltar,
                radio_tubo, angulos_codo, modo, techo_z=techo_z
            )
            if ruta_modo and len(ruta_modo) >= 2:
                lon = longitud_ruta(ruta_modo)
                if lon < mejor_lon:
                    mejor_lon = lon
                    mejor_ruta = ruta_modo

        if mejor_ruta:
            for sp in mejor_ruta[1:-1]:
                if sp.distancia_a(resultado[-1]) > 1:
                    resultado.append(sp)

        if destino_salto.distancia_a(resultado[-1]) > 10:
            resultado.append(destino_salto)

        i = j  # Saltar todos los segmentos de la zona de obstaculos

    return resultado


def _fusionar_bboxes_saltar(bboxes_list):
    """Fusiona multiples bboxes saltar en un unico bbox combinado."""
    if len(bboxes_list) == 1:
        return bboxes_list[0]
    
    fusionado = {
        'x_min': min(b['x_min'] for b in bboxes_list),
        'x_max': max(b['x_max'] for b in bboxes_list),
        'y_min': min(b['y_min'] for b in bboxes_list),
        'y_max': max(b['y_max'] for b in bboxes_list),
        'z_min': min(b['z_min'] for b in bboxes_list),
        'z_max': max(b['z_max'] for b in bboxes_list),
        'z_real_min': min(b.get('z_real_min', b['z_min']) for b in bboxes_list),
        'z_real_max': max(b.get('z_real_max', b['z_max']) for b in bboxes_list),
        'x_real_min': min(b.get('x_real_min', b['x_min']) for b in bboxes_list),
        'x_real_max': max(b.get('x_real_max', b['x_max']) for b in bboxes_list),
        'y_real_min': min(b.get('y_real_min', b['y_min']) for b in bboxes_list),
        'y_real_max': max(b.get('y_real_max', b['y_max']) for b in bboxes_list),
        'modo': bboxes_list[0].get('modo', ['saltar']),
        'id': 'merged_saltar',
        'centro_x': sum(b.get('centro_x', 0) for b in bboxes_list) / len(bboxes_list),
        'centro_y': sum(b.get('centro_y', 0) for b in bboxes_list) / len(bboxes_list),
        'centro_z': sum(b.get('centro_z', 0) for b in bboxes_list) / len(bboxes_list),
    }
    return fusionado


def aplicar_estrategia(origen, destino, obs, bboxes, radio_tubo,
                        angulos_codo, modo, techo_z=None):
    """Aplica estrategia de evasion: saltar, rodear, o bajar."""
    if modo == 'saltar':
        return calcular_salto(origen, destino, obs, radio_tubo, angulos_codo)
    elif modo == 'bajar':
        resultado = calcular_bajada(origen, destino, obs, radio_tubo, angulos_codo, techo_z=techo_z)
        if resultado is None and techo_z is not None:
            # Solo lanzar BajarImposibleError si es ESPECIFICAMENTE el techo
            # quien bloquea.  Otros None son fallos geometricos normales.
            margen = radio_tubo + MARGEN_OBSTACULO
            z_real_min = obs.get('z_real_min', obs.get('z_min', 0) + margen)
            altura_bajada = z_real_min - radio_tubo - 10
            z_minimo_tubo = altura_bajada - radio_tubo
            if z_minimo_tubo < techo_z:
                obs_id = obs.get('id', obs.get('obs_id', '?'))
                raise BajarImposibleError(
                    f"No es posible BAJAR el obstáculo '{obs_id}': el techo (z={techo_z}) bloquea el paso por debajo."
                )
        return resultado
    elif modo == 'rodear':
        return calcular_rodeo(origen, destino, obs, bboxes, angulos_codo)
    else:
        print(f"  Modo desconocido: {modo}, usando rodear")
        return calcular_rodeo(origen, destino, obs, bboxes, angulos_codo)
