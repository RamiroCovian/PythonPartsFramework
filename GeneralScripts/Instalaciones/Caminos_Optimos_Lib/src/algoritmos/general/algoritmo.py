"""
Algoritmo general de pathfinding para tuberias con RRT* y fallback deterministico.
"""

import math
from typing import List, Optional
from ...modelos import Punto3D, Obstaculo
from .geometria import (
    LONGITUD_MINIMA, MARGEN_OBSTACULO,
    crear_bbox, crear_bbox_segmento, punto_en_bbox,
    segmento_cruza_bbox,
    eliminar_puntos_colineales, eliminar_puntos_duplicados,
    asignar_ids, validar_autocruce,
)
from .angulos import calcular_direcciones_validas
from .rrt_star import planificar_tramo_rrt
from .validacion_ruta import validar_subruta_completa
from .manejo_obstaculos import (
    modo_requiere_rodeo, modo_es_saltar, modo_es_bajar,
    vb_solapa_con_saltar, ruta_cruza_obstaculos_requeridos,
)
from .resolver_tramos import (
    BajarImposibleError,
    resolver_tramo_fallback, insertar_saltos_en_ruta,
)


def calcular_ruta_general(
    inicio: Punto3D,
    fin: Punto3D,
    puntos_obligatorios: List[Punto3D],
    puntos_libres: List[Punto3D],
    obstaculos: List[Obstaculo],
    radio_tubo: float,
    angulos_codo: List[int],
    techo_bounds: tuple = None,
    techo_z: float = None
) -> List[Punto3D]:
    """Calcula la ruta optima pasando por puntos obligatorios, evitando obstaculos."""
    # Crear bounding boxes para todos los obstaculos
    bboxes = [crear_bbox(obs, radio_tubo) for obs in obstaculos]
    
    # Separar obstaculos por modo:
    # - rodear: barreras XY para RRT* (la ruta los evita en planta)
    # - saltar/bajar: la ruta los cruza en XY y pasa por encima/debajo con cambio en Z
    bboxes_rodear = [b for b in bboxes if modo_requiere_rodeo(b)]
    bboxes_saltar = [b for b in bboxes if modo_es_saltar(b) or modo_es_bajar(b)]
    
    # Calcular direcciones de movimiento validas
    direcciones = calcular_direcciones_validas(angulos_codo)
    
    # Calcular bounds del espacio de trabajo (restringido al techo si se proporciona)
    bounds = _calcular_bounds(inicio, fin, puntos_obligatorios or [], puntos_libres or [], bboxes, techo_bounds)
    
    print(f"Algoritmo general: angulos_codo={angulos_codo}, direcciones={len(direcciones)}")
    
    # --- NIVEL 1: Planificador de orden (TSP greedy) ---
    secuencia_fija = [inicio] + (puntos_obligatorios or []) + [fin]
    secuencia = _insertar_puntos_libres(secuencia_fija, puntos_libres or [])
    
    ruta_completa = []
    dir_salida_anterior = None
    virtual_bboxes = []  # obstaculos virtuales de tramos ya planificados
    margen_virtual = radio_tubo + MARGEN_OBSTACULO  # clearance entre tubo y si mismo
    
    # --- NIVEL 2: RRT* por cada tramo ---
    for i in range(len(secuencia) - 1):
        origen = secuencia[i]
        destino = secuencia[i + 1]
        
        print(f"  Tramo: {origen.id} -> {destino.id}")
        
        # Filtrar virtual bboxes: excluir los que contienen origen o destino,
        # y los que solapan en XY con obstaculos saltar/bajar (la ruta DEBE
        # poder cruzar esas zonas; la colision 3D se evita con el salto/bajada)
        vb_filtrados = [vb for vb in virtual_bboxes
                        if not punto_en_bbox(origen, vb, margen_virtual)
                        and not punto_en_bbox(destino, vb, margen_virtual)
                        and not vb_solapa_con_saltar(vb, bboxes_saltar)]
        
        # XY obstacles: rodear + virtual (saltar transparente en XY, se resuelve post-hoc)
        bboxes_xy = bboxes_rodear + vb_filtrados
        
        subruta = None
        MAX_REINTENTOS = 30
        import time as _time
        t0 = _time.time()
        TIEMPO_LIMITE = 25  # segundos max por tramo
        
        # Obstaculos saltar/bajar que la linea recta cruza: la ruta DEBERIA cruzarlos
        obs_requeridos = [bb for bb in bboxes_saltar
                          if segmento_cruza_bbox(origen.x, origen.y, origen.z,
                                                 destino.x, destino.y, destino.z, bb)]
        subruta_reserva = None  # valida pero sin cruzar todos los obstaculos
        
        # Paso 1+2: RRT* + insertar saltos, reintentar hasta resultado 100% valido
        for intento in range(MAX_REINTENTOS):
            if _time.time() - t0 > TIEMPO_LIMITE:
                break
            candidata = planificar_tramo_rrt(
                inicio=origen, fin=destino,
                bboxes_rodear=bboxes_xy, bboxes_saltar=obs_requeridos,
                direcciones=direcciones, angulos_codo=angulos_codo,
                radio_tubo=radio_tubo, longitud_minima=LONGITUD_MINIMA,
                bounds=bounds, max_iter=5000,
                dir_entrada=dir_salida_anterior
            )
            if candidata is None:
                continue
            
            # Verificar cruce de obstaculos ANTES de insertar saltos
            # (despues del salto, los segmentos estan a otro Z y no cruzan el bbox)
            cruza_obs = not obs_requeridos or ruta_cruza_obstaculos_requeridos(candidata, obs_requeridos)
            
            # Insertar saltos sobre segmentos que cruzan obstaculos saltar
            candidata = insertar_saltos_en_ruta(
                candidata, bboxes_saltar, radio_tubo, angulos_codo, techo_z=techo_z
            )
            if candidata is None or len(candidata) < 2:
                continue
            
            # Validar TODO: angulos, longitudes, colisiones, auto-cruce, techo
            if validar_subruta_completa(
                candidata, angulos_codo, dir_salida_anterior,
                bboxes_rodear=bboxes_rodear, bboxes_saltar=bboxes_saltar,
                radio_tubo=radio_tubo,
                techo_bounds=techo_bounds, ruta_previa=ruta_completa
            ):
                if cruza_obs:
                    subruta = candidata
                    break
                # Valida pero no cruza todos los obstaculos: guardar como reserva
                if subruta_reserva is None:
                    subruta_reserva = candidata
        
        # Usar subruta_reserva si no se encontro una que cruce todos los obstaculos
        if subruta is None and subruta_reserva is not None:
            subruta = subruta_reserva
        
        # Si RRT* no produjo resultado valido, usar fallback deterministico
        if subruta is None:
            fallback = resolver_tramo_fallback(
                origen, destino, bboxes_xy, radio_tubo,
                angulos_codo, direcciones
            )
            if fallback:
                fallback = insertar_saltos_en_ruta(
                    fallback, bboxes_saltar, radio_tubo, angulos_codo, techo_z=techo_z
                )
            if fallback and len(fallback) >= 2:
                if validar_subruta_completa(
                    fallback, angulos_codo, dir_salida_anterior,
                    bboxes_rodear=bboxes_rodear, bboxes_saltar=bboxes_saltar,
                    radio_tubo=radio_tubo,
                    techo_bounds=techo_bounds, ruta_previa=ruta_completa
                ):
                    subruta = fallback
                else:
                    # Fallback invalido: segunda ronda breve con mas iteraciones
                    t1 = _time.time()
                    TIEMPO_RONDA2 = 5
                    for intento in range(10):
                        if _time.time() - t1 > TIEMPO_RONDA2:
                            break
                        candidata = planificar_tramo_rrt(
                            inicio=origen, fin=destino,
                            bboxes_rodear=bboxes_xy, bboxes_saltar=obs_requeridos,
                            direcciones=direcciones, angulos_codo=angulos_codo,
                            radio_tubo=radio_tubo, longitud_minima=LONGITUD_MINIMA,
                            bounds=bounds, max_iter=10000,
                            dir_entrada=dir_salida_anterior
                        )
                        if candidata is None:
                            continue
                        candidata = insertar_saltos_en_ruta(
                            candidata, bboxes_saltar, radio_tubo, angulos_codo, techo_z=techo_z
                        )
                        if candidata and len(candidata) >= 2 and validar_subruta_completa(
                            candidata, angulos_codo, dir_salida_anterior,
                            bboxes_rodear=bboxes_rodear, bboxes_saltar=bboxes_saltar,
                            radio_tubo=radio_tubo,
                            techo_bounds=techo_bounds, ruta_previa=ruta_completa
                        ):
                            subruta = candidata
                            break
                    # Si segunda ronda tampoco encontro, usar fallback (mejor que nada)
                    if subruta is None:
                        subruta = fallback
        
        # Ultimo recurso: linea directa (solo si no hay fallback)
        if subruta is None:
            subruta = [origen, destino]
        
        # Registrar segmentos planificados como obstaculos virtuales
        if len(subruta) >= 2:
            for si in range(len(subruta) - 1):
                sp1, sp2 = subruta[si], subruta[si + 1]
                if sp1.distancia_a(sp2) > 50:
                    virtual_bboxes.append(
                        crear_bbox_segmento(sp1, sp2, margen_virtual)
                    )
        
        # Calcular direccion de salida de este tramo para el siguiente
        if len(subruta) >= 2:
            p_ante = subruta[-2]
            p_ult = subruta[-1]
            dx_sal = p_ult.x - p_ante.x
            dy_sal = p_ult.y - p_ante.y
            if abs(dx_sal) > 0.5 or abs(dy_sal) > 0.5:
                dir_salida_anterior = math.degrees(math.atan2(dy_sal, dx_sal)) % 360
            else:
                dir_salida_anterior = None
        
        # Agregar subruta evitando duplicados en la union
        for j, punto in enumerate(subruta):
            if j == 0 and ruta_completa:
                continue
            if not ruta_completa or (
                abs(punto.x - ruta_completa[-1].x) > 1 or
                abs(punto.y - ruta_completa[-1].y) > 1 or
                abs(punto.z - ruta_completa[-1].z) > 1
            ):
                ruta_completa.append(punto)
    
    # Post-procesamiento global
    ruta_completa = eliminar_puntos_duplicados(ruta_completa)
    # Eliminar colineales SOLO si no introduce auto-cruces
    puntos_protegidos = (puntos_obligatorios or []) + (puntos_libres or [])
    ruta_sin_colineales = eliminar_puntos_colineales(ruta_completa, 5.0, puntos_protegidos=puntos_protegidos)
    clearance_post = radio_tubo + MARGEN_OBSTACULO
    if not validar_autocruce(ruta_sin_colineales, clearance_post):
        ruta_completa = ruta_sin_colineales
    asignar_ids(ruta_completa, puntos_obligatorios, puntos_libres)
    
    # Validacion final: detectar colisiones con obstaculos
    # Rodear: bbox expandido (no debe cruzar nunca)
    # Saltar/bajar: bbox REAL sin expansion (el salto/bajada puede pasar cerca, pero
    #               nunca debe penetrar el cuerpo real del obstaculo)
    violaciones_obs = []
    for i in range(len(ruta_completa) - 1):
        p1, p2 = ruta_completa[i], ruta_completa[i+1]
        for bb in bboxes:
            if bb.get('id') == 'virtual':
                continue
            if modo_requiere_rodeo(bb):
                # Rodear: usar bbox expandido completo
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                    violaciones_obs.append(
                        f"  POST-CHECK: Seg {p1.id}-{p2.id} cruza {bb.get('id','?')}")
            else:
                # Saltar/bajar: usar bbox real (cuerpo fisico del obstaculo)
                bb_real = {
                    'x_min': bb.get('x_real_min', bb['x_min']),
                    'x_max': bb.get('x_real_max', bb['x_max']),
                    'y_min': bb.get('y_real_min', bb['y_min']),
                    'y_max': bb.get('y_real_max', bb['y_max']),
                    'z_min': bb.get('z_real_min', bb['z_min']),
                    'z_max': bb.get('z_real_max', bb['z_max']),
                }
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb_real):
                    violaciones_obs.append(
                        f"  POST-CHECK: Seg {p1.id}-{p2.id} cruza {bb.get('id','?')}")
    if violaciones_obs:
        print(f"  *** ADVERTENCIA: {len(violaciones_obs)} colision(es) con obstaculos:")
        for v in violaciones_obs:
            print(v)
    
    # Validacion final: auto-cruce (ruta no se cruza consigo misma)
    clearance = radio_tubo + MARGEN_OBSTACULO
    autocruce = validar_autocruce(ruta_completa, clearance)
    if autocruce:
        print(f"  *** ADVERTENCIA: {len(autocruce)} auto-cruce(s) (clearance {clearance:.0f}mm):")
        for v in autocruce:
            print(v)
    
    # Validacion final: puntos dentro del area del techo
    if techo_bounds:
        x_min_t, x_max_t, y_min_t, y_max_t = techo_bounds
        for p in ruta_completa:
            if p.x < x_min_t - 1 or p.x > x_max_t + 1 or p.y < y_min_t - 1 or p.y > y_max_t + 1:
                print(f"  *** ADVERTENCIA: Punto {p.id} ({p.x:.0f},{p.y:.0f}) fuera del techo")
    
    return ruta_completa


def _insertar_puntos_libres(secuencia_fija: List[Punto3D],
                            puntos_libres: List[Punto3D]) -> List[Punto3D]:
    """Inserta puntos libres en la posicion que minimiza distancia total (greedy)."""
    if not puntos_libres:
        return list(secuencia_fija)
    
    secuencia = list(secuencia_fija)
    pendientes = list(puntos_libres)
    
    while pendientes:
        mejor_punto = None
        mejor_pos = None
        mejor_costo = float('inf')
        
        for p_libre in pendientes:
            for i in range(len(secuencia) - 1):
                p_antes = secuencia[i]
                p_despues = secuencia[i + 1]
                
                # Costo de insertar p_libre entre p_antes y p_despues
                dist_actual = p_antes.distancia_a(p_despues)
                dist_nueva = p_antes.distancia_a(p_libre) + p_libre.distancia_a(p_despues)
                costo_extra = dist_nueva - dist_actual
                
                if costo_extra < mejor_costo:
                    mejor_costo = costo_extra
                    mejor_punto = p_libre
                    mejor_pos = i + 1
        
        if mejor_punto is not None:
            secuencia.insert(mejor_pos, mejor_punto)
            pendientes.remove(mejor_punto)
        else:
            break
    
    return secuencia


def _calcular_bounds(inicio, fin, obligatorios, libres, bboxes, techo_bounds=None):
    """Calcula los limites del espacio de trabajo, restringido al techo."""
    if techo_bounds:
        # Usar limites del techo como restriccion dura
        return techo_bounds
    
    todos_x = [inicio.x, fin.x] + [p.x for p in obligatorios] + [p.x for p in libres]
    todos_y = [inicio.y, fin.y] + [p.y for p in obligatorios] + [p.y for p in libres]
    
    for b in bboxes:
        todos_x.extend([b['x_min'], b['x_max']])
        todos_y.extend([b['y_min'], b['y_max']])
    
    return (min(todos_x), max(todos_x), min(todos_y), max(todos_y))

