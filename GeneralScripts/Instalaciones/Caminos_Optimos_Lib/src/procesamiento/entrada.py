"""
Parseo de datos de entrada JSON a objetos de dominio.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

from ..modelos.punto import Punto3D
from ..modelos.obstaculo import Obstaculo
from .geometria_techo import (
    calcular_normal_techo, calcular_z_eje,
    generar_is_cubriendo_techo, obtener_config_subtipo,
    ANCHO_MAX_IS, ALTO_MAX_IS,
)


@dataclass
class EntradaProcesada:
    """Datos parseados de la entrada JSON."""
    nombre: str
    vertices_techo: List[List[float]]
    normal_techo: Tuple[float, float, float]
    subdivisiones: List[Dict]
    subtipo: str
    config_subtipo: dict
    inicio: Punto3D
    inicio_real: Punto3D
    fin: Punto3D
    fin_real: Punto3D
    puntos_obligatorios: List[Punto3D]
    puntos_libres: List[Punto3D]
    obstaculos: List[Obstaculo]
    estrategia_colision: List[str] = field(default_factory=lambda: ['saltar'])
    techos: List[Dict] = field(default_factory=list)
    tubos_is: List[Dict] = field(default_factory=list)


def _extraer_coords(p: Dict) -> tuple:
    """Extrae (x, y, z) de un punto, soportando formato nuevo (coordenadas) y viejo (x,y,z directo)."""
    if 'coordenadas' in p:
        c = p['coordenadas']
        return c['x'], c['y'], c.get('z')
    return p['x'], p['y'], p.get('z')


def _normalizar_puntos(puntos_raw) -> Dict:
    """Normaliza puntos a dict con inicio/fin/obligatorios/libres.
    
    Soporta:
    - Lista plana (formato nuevo): [{tipo: "inicio", ...}, {tipo: "orden_obligatorio", ...}, ...]
    - Dict con claves separadas (formato viejo): {inicio: {...}, fin: {...}, obligatorios: [...], libres: [...]}
    """
    if isinstance(puntos_raw, dict) and 'inicio' in puntos_raw:
        # Formato viejo: ya tiene claves separadas
        return puntos_raw
    
    if isinstance(puntos_raw, list):
        # Formato nuevo: lista plana, clasificar por tipo
        inicio = None
        fin = None
        obligatorios = []
        libres = []
        
        for p in puntos_raw:
            tipo = p.get('tipo', '').lower()
            if tipo == 'inicio':
                inicio = p
            elif tipo == 'fin':
                fin = p
            elif tipo == 'orden_obligatorio':
                obligatorios.append(p)
            elif tipo == 'orden_libre':
                libres.append(p)
        
        return {
            'inicio': inicio or {},
            'fin': fin or {},
            'obligatorios': obligatorios,
            'libres': libres,
        }
    
    return {'inicio': {}, 'fin': {}, 'obligatorios': [], 'libres': []}


def _ordenar_obligatorios(p_inicio: Dict, p_fin: Dict, obligatorios: List[Dict]) -> List[Dict]:
    """Ordena obligatorios siguiendo la cadena anteriores/siguientes.
    
    Si los puntos tienen 'siguientes'/'anteriores' (formato nuevo), sigue la cadena
    desde inicio hasta fin. Si no, usa el campo 'orden' (formato viejo).
    """
    if not obligatorios:
        return []
    
    # Detectar formato nuevo: al menos un obligatorio tiene 'anteriores'
    tiene_cadena = any('anteriores' in o and o['anteriores'] for o in obligatorios)
    
    if not tiene_cadena:
        # Formato viejo: ordenar por campo 'orden'
        return sorted(obligatorios, key=lambda x: x.get('orden', 0))
    
    # Formato nuevo: seguir cadena desde inicio
    inicio_id = p_inicio.get('id', 'A')
    oblig_por_id = {o['id']: o for o in obligatorios}
    
    ordenados = []
    # Buscar el primer obligatorio: el que tiene inicio_id en sus anteriores
    current_id = inicio_id
    visitados = set()
    
    while len(ordenados) < len(obligatorios):
        encontrado = None
        for o in obligatorios:
            if o['id'] not in visitados and current_id in o.get('anteriores', []):
                encontrado = o
                break
        if encontrado is None:
            break
        ordenados.append(encontrado)
        visitados.add(encontrado['id'])
        current_id = encontrado['id']
    
    # Fallback: si la cadena no resolvio todos, agregar los restantes
    if len(ordenados) < len(obligatorios):
        for o in obligatorios:
            if o['id'] not in visitados:
                ordenados.append(o)
    
    return ordenados


def parsear_entrada(datos: Dict[str, Any], camino_override: Dict = None,
                    extra_obstaculos: List[Obstaculo] = None) -> EntradaProcesada:
    """
    Parsea el diccionario JSON en objetos de dominio.
    
    Args:
        datos: Diccionario completo del JSON
        camino_override: Si se provee, usa estos puntos en lugar de datos['puntos']
                        (usado para multi-camino)
        extra_obstaculos: Obstaculos adicionales (ej: tuberias de caminos anteriores)
    """
    nombre = datos.get('nombre', 'Ejemplo Sin Nombre')
    if camino_override:
        nombre_camino = camino_override.get('nombre', camino_override.get('id', ''))
        print(f"Procesando: {nombre} - {nombre_camino}")
    else:
        print(f"Procesando: {nombre}")
    
    # Extraer vertices del techo (soporta objeto unico o array de techos)
    techo_raw = datos['techo']
    if isinstance(techo_raw, list):
        techos = techo_raw
    else:
        techos = [techo_raw]
    
    # Usar primer techo para calculos de normal/Z
    vertices_techo = [
        [v['x'], v['y'], v['z']] 
        for v in techos[0]['vertices']
    ]
    
    # Leer tubos_is si existen
    tubos_is = datos.get('tubos_is', [])
    
    normal_techo = calcular_normal_techo(vertices_techo)
    
    # Leer subdivisiones IS desde el JSON; auto-generar solo como fallback
    if 'subdivisiones_is' in datos and datos['subdivisiones_is']:
        subdivisiones = []
        for is_data in datos['subdivisiones_is']:
            if 'vertices' in is_data:
                verts = [[v['x'], v['y'], v['z']] for v in is_data['vertices']]
                subdivisiones.append({
                    'id': is_data.get('id', f'IS{len(subdivisiones)+1}'),
                    'vertices': verts
                })
        if not subdivisiones:
            subdivisiones = generar_is_cubriendo_techo(vertices_techo)
    else:
        subdivisiones = generar_is_cubriendo_techo(vertices_techo)
    
    # Validar dimensiones de cada IS contra limites de config/dimensiones_is.json
    for is_sub in subdivisiones:
        verts_is = is_sub.get('vertices', [])
        if len(verts_is) >= 4:
            xs_is = [v[0] for v in verts_is]
            ys_is = [v[1] for v in verts_is]
            ancho_is = max(xs_is) - min(xs_is)
            alto_is = max(ys_is) - min(ys_is)
            if ancho_is > ANCHO_MAX_IS:
                print(f"  *** ADVERTENCIA: {is_sub['id']} ancho={ancho_is:.0f}mm excede max {ANCHO_MAX_IS}mm")
            if alto_is > ALTO_MAX_IS:
                print(f"  *** ADVERTENCIA: {is_sub['id']} alto={alto_is:.0f}mm excede max {ALTO_MAX_IS}mm")
    
    # Configuracion
    config = datos.get('configuracion', {})
    subtipo = config.get('subtipo_tuberia', 'extraccion_impulsion').lower()
    
    # Obtener configuracion del subtipo desde la UNICA fuente de verdad
    config_subtipo = obtener_config_subtipo(subtipo)
    subtipo_obj = config_subtipo['subtipo_obj']
    angulo_giro = config_subtipo['angulo_giro']
    radio_tubo = config_subtipo['radio']
    
    ESTRATEGIAS_VALIDAS = {'saltar', 'rodear', 'bajar'}
    estrategia_colision = config.get('estrategia_colision', ['saltar'])
    # Normalizar a minusculas y validar
    estrategia_colision = [e.lower() for e in estrategia_colision]
    for e in estrategia_colision:
        if e not in ESTRATEGIAS_VALIDAS:
            print(f"  *** ADVERTENCIA: estrategia de colision '{e}' no reconocida (validas: {ESTRATEGIAS_VALIDAS})")
    
    # Mostrar informacion de angulos
    if subtipo_obj:
        print(f"Subtipo: {subtipo}")
        print(f"  - Angulos de codo permitidos: {subtipo_obj.angulos_permitidos}")
        print(f"  - Angulo de movimiento (pathfinding): {angulo_giro} grados")
        print(f"  - Radio: {radio_tubo}mm")
        print(f"  - Estrategia de colision: {estrategia_colision}")
    else:
        print(f"Subtipo: {subtipo}, Angulo de giro: {angulo_giro} grados, Radio: {radio_tubo}mm")
        print(f"  - Estrategia de colision: {estrategia_colision}")
    
    # Nodos: usar camino_override si se provee, sino datos['nodos']
    if camino_override:
        puntos_raw = camino_override.get('nodos', camino_override)
    else:
        puntos_raw = datos.get('nodos', [])
    
    # Normalizar a dict con inicio/fin/obligatorios/libres
    puntos_data = _normalizar_puntos(puntos_raw)
    
    # Inicio - posicion real y proyectada a la cota
    p_inicio = puntos_data['inicio']
    cx, cy, cz = _extraer_coords(p_inicio)
    z_inicio_real = cz if cz is not None else calcular_z_eje(cx, cy, vertices_techo, subtipo)
    z_cota_inicio = calcular_z_eje(cx, cy, vertices_techo, subtipo)
    inicio_real = Punto3D(x=cx, y=cy, z=z_inicio_real, id=p_inicio.get('id', 'A'))
    inicio = Punto3D(x=cx, y=cy, z=z_cota_inicio, id=p_inicio.get('id', 'A'))
    
    # Fin - posicion real y proyectada a la cota
    p_fin = puntos_data['fin']
    cx, cy, cz = _extraer_coords(p_fin)
    z_fin_real = cz if cz is not None else calcular_z_eje(cx, cy, vertices_techo, subtipo)
    z_cota_fin = calcular_z_eje(cx, cy, vertices_techo, subtipo)
    fin_real = Punto3D(x=cx, y=cy, z=z_fin_real, id=p_fin.get('id', 'B'))
    fin = Punto3D(x=cx, y=cy, z=z_cota_fin, id=p_fin.get('id', 'B'))
    
    # Obligatorios - ordenar por cadena anteriores/siguientes si existe, sino por 'orden'
    obligatorios_raw = puntos_data.get('obligatorios', [])
    obligatorios_raw = _ordenar_obligatorios(p_inicio, p_fin, obligatorios_raw)
    
    puntos_obligatorios = []
    for p in obligatorios_raw:
        cx, cy, cz = _extraer_coords(p)
        z_final = cz if cz is not None else calcular_z_eje(cx, cy, vertices_techo, subtipo)
        puntos_obligatorios.append(Punto3D(x=cx, y=cy, z=z_final, id=p.get('id', '')))
    
    # Libres - usar Z del usuario si fue proporcionado
    puntos_libres = []
    for p in puntos_data.get('libres', []):
        cx, cy, cz = _extraer_coords(p)
        z_final = cz if cz is not None else calcular_z_eje(cx, cy, vertices_techo, subtipo)
        puntos_libres.append(Punto3D(x=cx, y=cy, z=z_final, id=p.get('id', '')))
    
    # Obstaculos - definidos por vertices (8 puntos 3D)
    # Cada obstáculo tiene su propio modo: 'saltar', 'rodear', 'bajar' o lista
    obstaculos = []
    for obs_data in datos.get('obstaculos', []):
        modo_obs = obs_data.get('modo', 'rodear')
        obs_id = obs_data.get('id', 'Obstaculo')
        
        if 'vertices' in obs_data:
            obs = Obstaculo.desde_vertices(
                vertices_data=obs_data['vertices'],
                id=obs_id,
                modo=modo_obs
            )
            obs.normal_techo = normal_techo
            obstaculos.append(obs)
        else:
            print(f"  Advertencia: obstáculo {obs_id} sin vertices, ignorado")
            continue
    
    # Agregar obstaculos extra (ej: tuberias de caminos anteriores)
    if extra_obstaculos:
        obstaculos.extend(extra_obstaculos)
    
    return EntradaProcesada(
        nombre=nombre,
        vertices_techo=vertices_techo,
        normal_techo=normal_techo,
        subdivisiones=subdivisiones,
        subtipo=subtipo,
        config_subtipo=config_subtipo,
        inicio=inicio,
        inicio_real=inicio_real,
        fin=fin,
        fin_real=fin_real,
        puntos_obligatorios=puntos_obligatorios,
        puntos_libres=puntos_libres,
        obstaculos=obstaculos,
        estrategia_colision=estrategia_colision,
        techos=techos,
        tubos_is=tubos_is,
    )
