"""
Funciones de clasificacion, deteccion y expansion de obstaculos.
"""

import math
from typing import List

from ...modelos import Punto3D
from .geometria import LONGITUD_MINIMA, segmento_cruza_bbox


def tramo_cruza_obstaculos(origen: Punto3D, destino: Punto3D, bboxes: List[dict]) -> bool:
    """Verifica si un tramo directo cruza alguno de los bboxes dados."""
    for bb in bboxes:
        if segmento_cruza_bbox(
            origen.x, origen.y, origen.z,
            destino.x, destino.y, destino.z, bb
        ):
            return True
    return False


def expandir_secuencia_con_obstaculos(secuencia, bboxes_saltar, radio_tubo):
    """Inserta waypoints justo DESPUES de cada obstaculo saltar/bajar que la linea
    recta entre waypoints consecutivos cruza.  Esto obliga al RRT* a planificar
    una ruta que pase a traves de cada obstaculo."""
    if not bboxes_saltar:
        return secuencia
    
    nueva = [secuencia[0]]
    for i in range(len(secuencia) - 1):
        ori = secuencia[i]
        dst = secuencia[i + 1]
        
        dx = dst.x - ori.x
        dy = dst.y - ori.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 1:
            nueva.append(dst)
            continue
        ux = dx / dist
        uy = dy / dist
        
        # Encontrar obstaculos saltar/bajar que la linea recta cruza
        obs_en_linea = []
        for bb in bboxes_saltar:
            if segmento_cruza_bbox(ori.x, ori.y, ori.z, dst.x, dst.y, dst.z, bb):
                # Proyeccion del centro del obstaculo sobre eje de movimiento
                cx = bb['centro_x'] - ori.x
                cy = bb['centro_y'] - ori.y
                proj_centro = cx * ux + cy * uy
                # Extension del bbox sobre eje de movimiento
                hx = (bb['x_max'] - bb['x_min']) / 2
                hy = (bb['y_max'] - bb['y_min']) / 2
                ext = abs(ux) * hx + abs(uy) * hy
                # Waypoint justo despues de la salida del obstaculo
                t_salida = proj_centro + ext + LONGITUD_MINIMA
                if t_salida < dist - LONGITUD_MINIMA:
                    obs_en_linea.append((t_salida, bb))
        
        # Ordenar por distancia e insertar waypoints
        obs_en_linea.sort(key=lambda x: x[0])
        for t_wp, bb in obs_en_linea:
            wp_x = ori.x + ux * t_wp
            wp_y = ori.y + uy * t_wp
            wp_z = ori.z + (dst.z - ori.z) * (t_wp / dist)
            wp = Punto3D(x=wp_x, y=wp_y, z=wp_z, id=f"_wp_{bb['id']}")
            nueva.append(wp)
        
        nueva.append(dst)
    
    return nueva


def vb_solapa_con_saltar(vb: dict, bboxes_saltar: list) -> bool:
    """Verifica si un virtual bbox solapa en XY con algun obstaculo saltar/bajar.
    Si solapa, el virtual bbox NO debe bloquear esa zona (la ruta DEBE cruzar el obstaculo)."""
    for sb in bboxes_saltar:
        if not (vb['x_max'] < sb['x_min'] or vb['x_min'] > sb['x_max'] or
                vb['y_max'] < sb['y_min'] or vb['y_min'] > sb['y_max']):
            return True
    return False


def ruta_cruza_obstaculos_requeridos(ruta, obs_requeridos):
    """Verifica que la ruta cruza TODOS los obstaculos saltar/bajar requeridos."""
    for obs in obs_requeridos:
        cruzado = False
        for k in range(len(ruta) - 1):
            if segmento_cruza_bbox(ruta[k].x, ruta[k].y, ruta[k].z,
                                   ruta[k+1].x, ruta[k+1].y, ruta[k+1].z, obs):
                cruzado = True
                break
        if not cruzado:
            return False
    return True


def modo_requiere_rodeo(bbox: dict) -> bool:
    """Un obstaculo requiere rodeo si su modo incluye 'rodear' (barrera en XY)."""
    modo = bbox.get('modo', 'rodear')
    if isinstance(modo, list):
        return 'rodear' in modo
    return modo == 'rodear'


def modo_es_saltar(bbox: dict) -> bool:
    """Un obstaculo es de tipo saltar si su modo incluye 'saltar'."""
    modo = bbox.get('modo', 'rodear')
    if isinstance(modo, list):
        return 'saltar' in modo
    return modo == 'saltar'


def modo_es_bajar(bbox: dict) -> bool:
    """Un obstaculo es de tipo bajar si su modo incluye 'bajar'."""
    modo = bbox.get('modo', 'rodear')
    if isinstance(modo, list):
        return 'bajar' in modo
    return modo == 'bajar'


def obtener_modos(obs: dict) -> List[str]:
    """Obtiene la lista de modos de evasion de un obstaculo."""
    modo = obs.get('modo', 'rodear')
    
    if isinstance(modo, list):
        return modo
    
    if isinstance(modo, str):
        # Soportar formato "saltar,rodear" (comma-separated)
        if ',' in modo:
            return [m.strip() for m in modo.split(',')]
        return [modo]
    
    return ['rodear']
