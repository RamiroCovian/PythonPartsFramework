"""
Pipeline principal: orquesta el procesamiento completo de datos de tuberia.

Soporta dos formatos de entrada:
- Single-camino: datos['puntos'] con un solo A/B
- Multi-camino: datos['caminos'] con una lista de caminos independientes
  Cada camino se procesa secuencialmente y las tuberias calculadas se
  convierten en obstaculos (rodear) para los caminos siguientes.
"""

import math
from typing import Dict, Any, Tuple, Optional, List

from ..modelos.punto import Punto3D
from ..modelos.obstaculo import Obstaculo
from ..modelos.soporte import TuboIS
from ..visualizacion.visualizador_3d import Visualizador3D
from ..reportes import Segmento, ResultadoCamino, imprimir_resultado
from .entrada import EntradaProcesada, parsear_entrada
from .ruteo import calcular_ruta, insertar_conectores
from .validacion import validar_ruta
from .resultado import post_procesar_is, construir_visualizacion
from ..algoritmos.general.cruces_tubo import SegmentoTubo, insertar_saltos_tubo
from ..algoritmos.general.resolver_tramos import insertar_saltos_en_ruta
from ..algoritmos.general.geometria import crear_bbox, segmento_cruza_bbox
from ..algoritmos.general.manejo_obstaculos import modo_es_saltar, modo_es_bajar
from .geometria_techo import calcular_z_eje


# ---------------------------------------------------------------------------
# Colores para cada camino en la visualizacion multi-camino
# ---------------------------------------------------------------------------
COLORES_CAMINOS = [
    'rgb(0, 150, 255)',    # azul (default)
    'rgb(255, 100, 0)',    # naranja
    'rgb(0, 200, 100)',    # verde
    'rgb(200, 0, 200)',    # magenta
    'rgb(255, 200, 0)',    # amarillo
    'rgb(0, 200, 200)',    # cyan
]


# ---------------------------------------------------------------------------
# Funciones auxiliares para optimizacion multi-camino
# ---------------------------------------------------------------------------

def _contar_puntos_prioridad(camino_data):
    """Cuenta puntos obligatorios y libres para determinar prioridad."""
    nodos = camino_data.get('nodos', [])
    if isinstance(nodos, list):
        n_oblig = sum(1 for n in nodos if n.get('tipo') == 'orden_obligatorio')
        n_libre = sum(1 for n in nodos if n.get('tipo') == 'orden_libre')
    else:
        n_oblig = len(nodos.get('obligatorios', []))
        n_libre = len(nodos.get('libres', []))
    return n_oblig, n_libre


def _ordenar_por_prioridad(caminos_data):
    """Retorna indices ordenados por prioridad (mas puntos obligatorios primero)."""
    prioridades = []
    for idx, cam in enumerate(caminos_data):
        n_oblig, n_libre = _contar_puntos_prioridad(cam)
        prioridades.append((n_oblig, n_libre, idx))
    prioridades.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return [idx for _, _, idx in prioridades]


def _extraer_coords_ab(camino_data):
    """Extrae coordenadas (x,y) de los puntos A y B de un camino."""
    nodos = camino_data.get('nodos', [])
    if isinstance(nodos, list):
        a = next((n for n in nodos if n.get('tipo') == 'inicio'), None)
        b = next((n for n in nodos if n.get('tipo') == 'fin'), None)
    else:
        a = nodos.get('inicio')
        b = nodos.get('fin')
    if not a or not b:
        return None
    def _coords(p):
        if 'coordenadas' in p:
            c = p['coordenadas']
            return c['x'], c['y']
        return p['x'], p['y']
    return _coords(a) + _coords(b)  # (ax, ay, bx, by)


def _detectar_paralelos(caminos_data, orden):
    """Detecta caminos paralelos (A.x similar, B.x similar).

    Returns:
        paralelos: dict {idx_secundario: idx_base} para caminos que pueden usar offset.
        coords_ab: dict {idx: (ax, ay, bx, by)} coordenadas extraidas.
    """
    TOL = 100  # mm tolerancia para considerar misma X
    coords_ab = {}
    for idx in orden:
        ab = _extraer_coords_ab(caminos_data[idx])
        if ab:
            coords_ab[idx] = ab

    paralelos = {}
    for i, idx_i in enumerate(orden):
        if idx_i not in coords_ab or idx_i in paralelos:
            continue
        ax_i, _, bx_i, _ = coords_ab[idx_i]
        for j in range(i + 1, len(orden)):
            idx_j = orden[j]
            if idx_j not in coords_ab or idx_j in paralelos:
                continue
            ax_j, _, bx_j, _ = coords_ab[idx_j]
            if abs(ax_i - ax_j) < TOL and abs(bx_i - bx_j) < TOL:
                paralelos[idx_j] = idx_i

    return paralelos, coords_ab


def _aplanar_a_cota(camino, vertices_techo, subtipo):
    """Proyecta todos los puntos a la Z del techo, eliminando duplicados XY
    resultantes de perfiles de salto aplanados."""
    plano = []
    for p in camino:
        z_cota = calcular_z_eje(p.x, p.y, vertices_techo, subtipo)
        plano.append(Punto3D(x=p.x, y=p.y, z=z_cota, id=p.id))

    limpio = [plano[0]]
    for p in plano[1:]:
        dx = p.x - limpio[-1].x
        dy = p.y - limpio[-1].y
        if math.sqrt(dx*dx + dy*dy) > 20:
            limpio.append(p)
    if limpio[-1].distancia_a(plano[-1]) > 1:
        limpio.append(plano[-1])
    return limpio


def _aplicar_offset(camino_plano, offset_a, offset_b, vertices_techo, subtipo):
    """Desplaza un camino interpolando offset de A a B, recalculando Z en techo.

    Args:
        camino_plano: Camino base aplanado (Z en cota del techo)
        offset_a: (dx, dy) desplazamiento en el punto A
        offset_b: (dx, dy) desplazamiento en el punto B
        vertices_techo: Vertices del techo para recalcular Z
        subtipo: Subtipo de tuberia
    """
    if not camino_plano or len(camino_plano) < 2:
        return list(camino_plano)

    # Distancias acumuladas XY para interpolar el offset
    dists = [0.0]
    for i in range(1, len(camino_plano)):
        dx = camino_plano[i].x - camino_plano[i-1].x
        dy = camino_plano[i].y - camino_plano[i-1].y
        dists.append(dists[-1] + math.sqrt(dx*dx + dy*dy))
    total = dists[-1] if dists[-1] > 0 else 1.0

    resultado = []
    for i, p in enumerate(camino_plano):
        t = dists[i] / total  # 0 en A, 1 en B
        dx = (1 - t) * offset_a[0] + t * offset_b[0]
        dy = (1 - t) * offset_a[1] + t * offset_b[1]
        nx = p.x + dx
        ny = p.y + dy
        nz = calcular_z_eje(nx, ny, vertices_techo, subtipo)
        resultado.append(Punto3D(x=nx, y=ny, z=nz, id=p.id))
    return resultado


def _fuera_de_techo(camino, all_techo_verts, margen=50):
    """Verifica si algun punto del camino esta fuera del area UNION de todos los techos."""
    xs = [v[0] for v in all_techo_verts]
    ys = [v[1] for v in all_techo_verts]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    for p in camino:
        if (p.x < x_min - margen or p.x > x_max + margen or
            p.y < y_min - margen or p.y > y_max + margen):
            return True
    return False



def _angulos_offset_validos(camino, angulos_codo, tolerancia=1.0):
    """Verifica que todos los angulos del camino offset sean validos.
    
    acos(dot) entre vectores consecutivos da el angulo de deflexion (= angulo de codo).
    Para colinear (recto) = 0°, para giro de 45° codo = 45°.
    """
    if len(camino) < 3:
        return True
    for i in range(1, len(camino) - 1):
        p1, p2, p3 = camino[i-1], camino[i], camino[i+1]
        v1 = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
        v2 = (p3.x - p2.x, p3.y - p2.y, p3.z - p2.z)
        n1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        n2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        if n1 < 1.0 or n2 < 1.0:
            continue
        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        cos_a = max(-1.0, min(1.0, dot / (n1 * n2)))
        deflexion = math.degrees(math.acos(cos_a))
        # deflexion = angulo de codo (0° = recto, 45° = codo de 45°)
        valido = False
        for codo in angulos_codo:
            if abs(deflexion - codo) <= tolerancia or deflexion <= tolerancia:
                valido = True
                break
        if not valido:
            return False
    return True


def _colisiona_con_rodear(camino, obstaculos, radio_tubo):
    """Verifica si el camino colisiona con algun obstaculo tipo 'rodear'."""
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i+1]
        for obs in obstaculos:
            modo = obs.modo if isinstance(obs.modo, list) else [obs.modo]
            if 'rodear' in modo:
                bb = crear_bbox(obs, radio_tubo)
                if segmento_cruza_bbox(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, bb):
                    return True
    return False


def _generar_soportes(entrada: 'EntradaProcesada', resultado: 'ResultadoCamino',
                      grafo_is: Optional[Dict]) -> Tuple[list, list]:
    """
    Genera soportes para un camino si la ruta es valida y hay tubos IS definidos.

    Returns:
        (tubos_is_obj, soportes) - listas vacias si no aplica.
    """
    if not resultado.es_valido or not entrada.tubos_is:
        return [], []

    from ..post_procesamiento.generador_soportes import generar_soportes

    tubos_is_obj = [TuboIS.desde_dict(t) for t in entrada.tubos_is]
    soportes = generar_soportes(
        camino_con_u=resultado.puntos,
        grafo=grafo_is or {'segmentos': []},
        tubos_is=tubos_is_obj,
        obstaculos=entrada.obstaculos,
        subtipo=entrada.subtipo,
        radio_tubo=entrada.config_subtipo['radio'],
        vertices_techo=entrada.vertices_techo,
        offset_eje=entrada.config_subtipo['offset_eje'],
    )
    return tubos_is_obj, soportes


def procesar_datos(datos: Dict[str, Any]) -> Tuple[Visualizador3D, ResultadoCamino, Optional[Dict]]:
    """
    Procesa un diccionario de entrada y ejecuta el pipeline completo.
    Detecta automaticamente si es single-camino o multi-camino.
    
    Args:
        datos: Diccionario con la configuracion (techo, puntos, obstaculos, etc.)
        
    Returns:
        (visualizador, resultado, grafo_is)
    """
    # Detectar formato multi-camino
    if 'caminos' in datos and datos['caminos']:
        return _procesar_multicamino(datos)
    
    return _procesar_single(datos)


def _procesar_single(datos: Dict[str, Any],
                     camino_override: Dict = None,
                     extra_obstaculos: List[Obstaculo] = None
                     ) -> Tuple[Visualizador3D, ResultadoCamino, Optional[Dict]]:
    """Procesa un unico camino (pipeline original)."""
    # 1. Parsear entrada
    entrada = parsear_entrada(datos, camino_override=camino_override,
                              extra_obstaculos=extra_obstaculos)
    
    # 2. Calcular ruta
    camino = calcular_ruta(entrada)
    
    # 3. Insertar conectores y limpiar
    camino, num_con_inicio, num_con_fin = insertar_conectores(camino, entrada)
    
    # 4. Crear segmentos
    segmentos = [Segmento.desde_puntos(camino[i], camino[i+1]) for i in range(len(camino) - 1)]
    longitud_total = sum(s.longitud for s in segmentos)
    
    # 5. Validar ruta
    ruta_valida = validar_ruta(camino, segmentos, entrada, num_con_inicio, num_con_fin)
    
    # 6. Verificar puntos libres visitados
    libres_visitados = []
    for p_libre in entrada.puntos_libres:
        for p_camino in camino:
            dist = math.sqrt((p_libre.x - p_camino.x)**2 + 
                           (p_libre.y - p_camino.y)**2 + 
                           (p_libre.z - p_camino.z)**2)
            if dist < 100:  # Tolerancia de 100mm
                libres_visitados.append(p_libre)
                break
    
    # 7. Construir resultado
    resultado = ResultadoCamino(
        puntos=camino,
        segmentos=segmentos,
        longitud_total=longitud_total,
        puntos_obligatorios_visitados=entrada.puntos_obligatorios,
        puntos_libres_visitados=libres_visitados,
        es_valido=ruta_valida,
        mensaje=f"Ruta {'VALIDA' if ruta_valida else 'INVALIDA'}: {len(segmentos)} segmentos, {longitud_total:.1f}mm",
        num_conectores_inicio=num_con_inicio,
        num_conectores_fin=num_con_fin,
    )
    
    # 8. Imprimir resultado
    print(imprimir_resultado(resultado))
    
    # 9. Post-procesamiento IS
    grafo_is, puntos_u = post_procesar_is(camino, resultado, entrada)
    
    # 9b. Generar soportes (solo si ruta valida y hay tubos IS definidos)
    tubos_is_obj, soportes = _generar_soportes(entrada, resultado, grafo_is)
    if soportes and grafo_is is not None:
        grafo_is['soportes'] = [sp.como_dict() for sp in soportes]
    
    # 10. Construir visualizacion
    vis = construir_visualizacion(entrada, resultado.puntos, puntos_u,
                                  tubos_is=tubos_is_obj, soportes=soportes)
    
    return vis, resultado, grafo_is


def _procesar_multicamino(datos: Dict[str, Any]) -> Tuple[Visualizador3D, ResultadoCamino, Optional[Dict]]:
    """
    Procesa multiples caminos con optimizacion por prioridad y offset paralelo.

    1. Ordena caminos por prioridad (mas puntos obligatorios/libres primero).
    2. Detecta caminos paralelos (misma X en A y B).
    3. Calcula el camino base con RRT* y los paralelos por offset (mas rapido).
    4. Cada camino calculado se convierte en obstaculos para los siguientes.
    """
    caminos_data = datos['caminos']
    
    # 1. Ordenar por prioridad
    orden = _ordenar_por_prioridad(caminos_data)
    
    # 2. Detectar grupos paralelos
    paralelos, coords_ab = _detectar_paralelos(caminos_data, orden)
    bases = set(paralelos.values())  # indices que son base de un grupo
    
    print(f"\n=== MODO MULTI-CAMINO: {len(caminos_data)} caminos ===")
    if len(orden) > 1:
        ids_orden = [caminos_data[i].get('id', f'camino_{i+1}') for i in orden]
        print(f"  Orden de procesamiento (por prioridad): {ids_orden}")
    if paralelos:
        n_offset = len(paralelos)
        print(f"  Caminos paralelos detectados: {n_offset} usaran offset desde su base")
    print()
    
    # Extraer vertices de TODOS los techos para verificacion de bounds
    techo_raw = datos['techo']
    techos_list = techo_raw if isinstance(techo_raw, list) else [techo_raw]
    all_techo_verts = []
    for t in techos_list:
        for v in t['vertices']:
            all_techo_verts.append([v['x'], v['y'], v['z']])
    
    obstaculos_acumulados: List[Obstaculo] = []  # tuberias anteriores como obstaculos
    tubos_acumulados: List[SegmentoTubo] = []  # segmentos reales de tubo para cruces
    caminos_base_planos = {}  # base_idx -> camino aplanado (proyectado a cota techo)
    entradas_base = {}  # base_idx -> EntradaProcesada del base
    resultados_por_idx = {}  # idx_original -> (entrada, resultado, camino, puntos_u, grafo_is, soportes)
    
    for proc_num, idx in enumerate(orden):
        camino_data = caminos_data[idx]
        camino_id = camino_data.get('id', f'camino_{idx+1}')
        print(f"\n--- Camino {proc_num+1}/{len(caminos_data)}: {camino_id} ---")
        
        # Parsear entrada con obstaculos acumulados de caminos previos
        entrada = parsear_entrada(datos, camino_override=camino_data,
                                  extra_obstaculos=list(obstaculos_acumulados))
        
        radio_tubo = entrada.config_subtipo['radio']
        subtipo_obj = entrada.config_subtipo['subtipo_obj']
        angulos_codo = subtipo_obj.angulos_permitidos if subtipo_obj else [45]
        
        # === Intentar offset si es camino paralelo ===
        camino = None
        usar_offset = False
        if idx in paralelos:
            base_idx = paralelos[idx]
            if base_idx in caminos_base_planos:
                base_plano = caminos_base_planos[base_idx]
                entrada_base = entradas_base[base_idx]
                
                offset_a = (entrada.inicio.x - entrada_base.inicio.x,
                           entrada.inicio.y - entrada_base.inicio.y)
                offset_b = (entrada.fin.x - entrada_base.fin.x,
                           entrada.fin.y - entrada_base.fin.y)
                
                camino_offset = _aplicar_offset(
                    base_plano, offset_a, offset_b,
                    entrada.vertices_techo, entrada.subtipo)
                
                # Validar: no sale del techo, no colisiona con rodear, angulos correctos
                fuera = _fuera_de_techo(camino_offset, all_techo_verts)
                colisiona = _colisiona_con_rodear(camino_offset, entrada.obstaculos, radio_tubo)
                angulos_ok = _angulos_offset_validos(camino_offset, angulos_codo)
                
                if not fuera and not colisiona and angulos_ok:
                    camino = camino_offset
                    usar_offset = True
                    base_id = caminos_data[base_idx].get('id', '?')
                    print(f"  Ruta por offset desde {base_id}: "
                          f"dA=({offset_a[0]:.0f},{offset_a[1]:.0f}) "
                          f"dB=({offset_b[0]:.0f},{offset_b[1]:.0f})")
                    
                    # Insertar saltos para obstaculos saltar/bajar
                    bboxes_all = [crear_bbox(obs, radio_tubo) for obs in entrada.obstaculos]
                    bboxes_saltar = [
                        bb for bb in bboxes_all
                        if modo_es_saltar(bb) or modo_es_bajar(bb)
                    ]
                    if bboxes_saltar:
                        techo_z = min(v[2] for v in entrada.vertices_techo)
                        camino = insertar_saltos_en_ruta(
                            camino, bboxes_saltar, radio_tubo, angulos_codo, techo_z=techo_z)
                else:
                    razones = []
                    if fuera:
                        razones.append("fuera del techo")
                    if colisiona:
                        razones.append("colisiona con obstaculo rodear")
                    if not angulos_ok:
                        razones.append("angulos distorsionados")
                    print(f"  Offset no viable ({', '.join(razones)}), usando RRT*")
        
        # === Calcular con RRT* si offset no aplico ===
        if camino is None:
            camino = calcular_ruta(entrada)
        
        # Guardar version plana como base para futuros offsets paralelos
        if idx in bases:
            caminos_base_planos[idx] = _aplanar_a_cota(
                camino, entrada.vertices_techo, entrada.subtipo)
            entradas_base[idx] = entrada
        
        # Insertar conectores PRIMERO (antes de saltos)
        cam_num = idx + 1  # 1-based, indice ORIGINAL para etiquetas
        camino, num_con_inicio, num_con_fin = insertar_conectores(camino, entrada, camino_idx=cam_num)
        
        # Insertar saltos tubo-tubo DESPUES de conectores
        # Proteger segmentos de conector + buffer extra para 90° (descenso vertical
        # colisiona con conector diagonal si estan en el mismo punto XY)
        extra_prot = 1 if 90 in angulos_codo else 0
        prot_ini = num_con_inicio + extra_prot
        prot_fin = num_con_fin + extra_prot
        if tubos_acumulados and camino and len(camino) >= 2:
            camino = insertar_saltos_tubo(
                camino, tubos_acumulados, radio_tubo, angulos_codo,
                segmentos_protegidos=(prot_ini, prot_fin)
            )
        
        # Crear segmentos
        segmentos = [Segmento.desde_puntos(camino[i], camino[i+1]) for i in range(len(camino) - 1)]
        longitud_total = sum(s.longitud for s in segmentos)
        
        # Validar ruta
        ruta_valida = validar_ruta(camino, segmentos, entrada, num_con_inicio, num_con_fin)
        
        # Si usamos offset y el resultado final es invalido, reintentar con RRT*
        if usar_offset and not ruta_valida:
            print(f"  Offset invalido tras saltos/conectores, reintentando con RRT*")
            camino = calcular_ruta(entrada)
            usar_offset = False
            
            camino, num_con_inicio, num_con_fin = insertar_conectores(camino, entrada, camino_idx=cam_num)
            
            if tubos_acumulados and camino and len(camino) >= 2:
                camino = insertar_saltos_tubo(
                    camino, tubos_acumulados, radio_tubo, angulos_codo,
                    segmentos_protegidos=(prot_ini, prot_fin)
                )
            segmentos = [Segmento.desde_puntos(camino[i], camino[i+1]) for i in range(len(camino) - 1)]
            longitud_total = sum(s.longitud for s in segmentos)
            ruta_valida = validar_ruta(camino, segmentos, entrada, num_con_inicio, num_con_fin)
        
        # Extraer puntos O y L renombrados del camino (ya tienen IDs con subindice)
        obligatorios_en_ruta = [p for p in camino if p.id and p.id[0].upper() == 'O']
        
        # Verificar puntos libres visitados
        libres_visitados = []
        for p_libre in entrada.puntos_libres:
            for p_camino in camino:
                dist = math.sqrt((p_libre.x - p_camino.x)**2 + 
                               (p_libre.y - p_camino.y)**2 + 
                               (p_libre.z - p_camino.z)**2)
                if dist < 100:
                    libres_visitados.append(p_camino)  # usar el punto del camino (con ID renombrado)
                    break
        
        # Construir resultado
        resultado = ResultadoCamino(
            puntos=camino,
            segmentos=segmentos,
            longitud_total=longitud_total,
            puntos_obligatorios_visitados=obligatorios_en_ruta,
            puntos_libres_visitados=libres_visitados,
            es_valido=ruta_valida,
            mensaje=f"Ruta {'VALIDA' if ruta_valida else 'INVALIDA'}: {len(segmentos)} segmentos, {longitud_total:.1f}mm",
            num_conectores_inicio=num_con_inicio,
            num_conectores_fin=num_con_fin,
        )
        
        print(imprimir_resultado(resultado))
        
        # Post-procesamiento IS
        grafo_is, puntos_u = post_procesar_is(camino, resultado, entrada, camino_idx=cam_num)
        
        # Generar soportes para este camino (solo si valido y hay tubos IS)
        _, soportes_cam = _generar_soportes(entrada, resultado, grafo_is)
        if soportes_cam and grafo_is is not None:
            grafo_is['soportes'] = [sp.como_dict() for sp in soportes_cam]
        
        resultados_por_idx[idx] = (entrada, resultado, camino, puntos_u, grafo_is, soportes_cam)
        
        # Convertir la tuberia calculada en obstaculos para los siguientes caminos
        estrategia = entrada.estrategia_colision or ['saltar']
        
        # Almacenar segmentos reales del tubo para cruces tubo-tubo
        nuevos_tubos = _camino_a_segmentos_tubo(camino, radio_tubo, camino_id)
        tubos_acumulados.extend(nuevos_tubos)
        
        # Solo agregar AABBs al RRT si la estrategia NO es puramente 'saltar'.
        # Para 'saltar', el RRT pasa libre en XY y insertar_saltos_tubo maneja Z.
        estrategias_no_saltar = [e for e in estrategia if e != 'saltar']
        if estrategias_no_saltar:
            nuevos_obs = _camino_a_obstaculos(
                camino, radio_tubo, camino_id,
                estrategia_colision=estrategias_no_saltar
            )
            obstaculos_acumulados.extend(nuevos_obs)
            print(f"  -> Tuberia {camino_id} convertida en {len(nuevos_obs)} obstaculos ({estrategias_no_saltar}) + {len(nuevos_tubos)} segmentos tubo")
        else:
            print(f"  -> Tuberia {camino_id} convertida en {len(nuevos_tubos)} segmentos tubo (saltar via cruces_tubo)")
    
    # Reconstruir resultados en orden ORIGINAL para visualizacion
    resultados_caminos = [resultados_por_idx[i] for i in range(len(caminos_data))]
    
    # --- Construir visualizacion combinada ---
    primera_entrada = resultados_caminos[0][0]
    vis = Visualizador3D(datos.get('nombre', 'Multi-Camino'))
    # Dibujar bordes de todos los techos
    for t in primera_entrada.techos:
        verts_t = [[v['x'], v['y'], v['z']] for v in t['vertices']]
        vis.agregar_borde_techo(verts_t, nombre=f"Techo ({t.get('id', '')})")
    
    subtipo_obj = primera_entrada.config_subtipo['subtipo_obj']
    distancia_techo = subtipo_obj.distancia_techo_mm if subtipo_obj else 110.0
    # Plano de tuberia sobre el primer techo
    vis.agregar_plano_tuberia(primera_entrada.vertices_techo, distancia_techo)
    vis.agregar_subdivisiones_is(primera_entrada.subdivisiones)
    
    # Agregar obstaculos originales (no los generados por tuberias)
    for obs in primera_entrada.obstaculos:
        if not obs.id.startswith('tubo_'):
            vis.agregar_obstaculo(obs)
    
    # Agregar tubos IS (compartidos para todos los caminos)
    if primera_entrada.tubos_is:
        tubos_is_obj = [TuboIS.desde_dict(t) for t in primera_entrada.tubos_is]
        vis.agregar_tubos_is(tubos_is_obj)
    
    # Agregar cada camino con su color
    for idx, (entrada, resultado, camino, puntos_u, _, soportes_cam) in enumerate(resultados_caminos):
        color = COLORES_CAMINOS[idx % len(COLORES_CAMINOS)]
        camino_id = caminos_data[idx].get('id', f'camino_{idx+1}')
        
        cam_num = idx + 1  # 1-based para etiquetas
        vis.agregar_punto_inicio(entrada.inicio_real, nombre=f"A ({camino_id})", camino_idx=cam_num)
        vis.agregar_punto_fin(entrada.fin_real, nombre=f"B ({camino_id})", camino_idx=cam_num)
        vis.agregar_puntos_intermedios(
            puntos_obligatorios=entrada.puntos_obligatorios,
            puntos_libres=entrada.puntos_libres,
            puntos_conexion=[],
            camino_idx=cam_num
        )
        puntos_excluir = (entrada.puntos_obligatorios or []) + (entrada.puntos_libres or []) + (puntos_u or [])
        vis.agregar_camino(resultado.puntos, nombre=f"Tuberia {camino_id}", color=color, puntos_excluir=puntos_excluir, camino_idx=cam_num)
        radio_tubo = entrada.config_subtipo['radio']
        vis.agregar_tuberia_3d(resultado.puntos, radio=radio_tubo, nombre=f"Tubo 3D {camino_id}")
        
        if puntos_u:
            vis.agregar_puntos_union(puntos_u, camino_idx=cam_num)
        if soportes_cam:
            vis.agregar_soportes(soportes_cam)
    
    # Resultado combinado: usar el ultimo resultado para compatibilidad,
    # pero marcar como invalido si alguno fallo
    todos_validos = all(r[1].es_valido for r in resultados_caminos)
    longitud_combinada = sum(r[1].longitud_total for r in resultados_caminos)
    
    resultado_final = ResultadoCamino(
        puntos=resultados_caminos[-1][2],
        segmentos=resultados_caminos[-1][1].segmentos,
        longitud_total=longitud_combinada,
        puntos_obligatorios_visitados=[],
        puntos_libres_visitados=[],
        es_valido=todos_validos,
        mensaje=f"Multi-camino: {len(caminos_data)} caminos, total {longitud_combinada:.1f}mm, {'TODOS VALIDOS' if todos_validos else 'ALGUNOS INVALIDOS'}",
        num_conectores_inicio=0,
        num_conectores_fin=0,
    )
    
    # Construir grafo IS combinado en formato multi-camino
    grafo_is_final = _construir_grafo_multicamino(datos, caminos_data,
                                                  [(e, r, c, u, g) for e, r, c, u, g, _ in resultados_caminos])
    
    return vis, resultado_final, grafo_is_final


def _construir_grafo_multicamino(
    datos: Dict[str, Any],
    caminos_data: List[Dict],
    resultados_caminos: list
) -> Dict[str, Any]:
    """
    Construye el grafo IS combinado en formato multi-camino.
    Sigue la estructura de ejemplo_output.json:
    {
        "id": "...",
        "nombre": "...",
        "caminos": [
            { "id", "nombre", "nodos": [...], "segmentos": [...] }
        ]
    }
    """
    caminos_output = []
    
    for idx, (entrada, resultado, camino, puntos_u, grafo_is) in enumerate(resultados_caminos):
        camino_data = caminos_data[idx]
        camino_id = camino_data.get('id', f'camino_{idx+1}')
        camino_nombre = camino_data.get('nombre', camino_id)
        
        if grafo_is is None:
            # Ruta invalida - crear grafo vacio
            caminos_output.append({
                'id': camino_id,
                'nombre': camino_nombre,
                'nodos': [],
                'segmentos': []
            })
            continue
        
        nodos_out = []
        for nodo in grafo_is.get('nodos', []):
            nodos_out.append({
                'id': nodo['id'],
                'tipo': nodo['tipo'],
                'coordenadas': nodo['coordenadas'],
                'IS': nodo['IS'],
                'anteriores': nodo.get('anteriores', []),
                'siguientes': nodo.get('siguientes', []),
            })
        
        entrada_camino = {
            'id': camino_id,
            'nombre': camino_nombre,
            'nodos': nodos_out,
            'segmentos': grafo_is.get('segmentos', [])
        }
        if 'soportes' in grafo_is:
            entrada_camino['soportes'] = grafo_is['soportes']
        caminos_output.append(entrada_camino)
    
    return {
        'id': datos.get('id', ''),
        'nombre': datos.get('nombre', ''),
        'caminos': caminos_output
    }


def _camino_a_obstaculos(
    camino: List[Punto3D],
    radio_tubo: float,
    camino_id: str,
    estrategia_colision: List[str] = None,
) -> List[Obstaculo]:
    """
    Convierte un camino calculado en una lista de obstaculos para caminos posteriores.
    
    Cada segmento genera un obstaculo ajustado al tubo fisico (centro ± radio_tubo).
    crear_bbox() anadira margenes adicionales para deteccion en el pathfinding.
    
    insertar_saltos_en_ruta() fusionara automaticamente los obstaculos cruzados
    por un mismo segmento en un unico salto.
    
    La altura de salto resultante sera:
        z_real_max + radio_tubo + 10 = tube_z + 2*radio + 10mm
    
    Args:
        camino: Lista de puntos del camino
        radio_tubo: Radio de la tuberia
        camino_id: ID del camino (para nombrar obstaculos)
        estrategia_colision: Estrategia(s) de colision (saltar/rodear/bajar)
    """
    if estrategia_colision is None:
        estrategia_colision = ['saltar']
    
    obstaculos = []
    padding_xy = radio_tubo
    padding_z = radio_tubo
    
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i + 1]
        
        x_min = min(p1.x, p2.x) - padding_xy
        x_max = max(p1.x, p2.x) + padding_xy
        y_min = min(p1.y, p2.y) - padding_xy
        y_max = max(p1.y, p2.y) + padding_xy
        z_min = min(p1.z, p2.z) - padding_z
        z_max = max(p1.z, p2.z) + padding_z
        
        # Evitar obstaculos degenerados (ancho o largo 0)
        if x_max - x_min < 1:
            x_min -= padding_xy
            x_max += padding_xy
        if y_max - y_min < 1:
            y_min -= padding_xy
            y_max += padding_xy
        
        obs = Obstaculo.desde_esquinas(
            esquina_min=Punto3D(x=x_min, y=y_min, z=z_min),
            esquina_max=Punto3D(x=x_max, y=y_max, z=z_max),
            id=f"tubo_{camino_id}_seg{i}"
        )
        obs.modo = list(estrategia_colision)
        obstaculos.append(obs)
    
    return obstaculos


def _camino_a_segmentos_tubo(
    camino: List[Punto3D],
    radio_tubo: float,
    camino_id: str,
) -> List[SegmentoTubo]:
    """
    Convierte un camino calculado en una lista de SegmentoTubo para deteccion
    precisa de cruces tubo-tubo (sin aproximacion AABB).
    """
    segmentos = []
    for i in range(len(camino) - 1):
        p1, p2 = camino[i], camino[i + 1]
        # Filtrar segmentos muy cortos (conectores)
        dist = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2 + (p2.z-p1.z)**2)
        if dist > 10:
            segmentos.append(SegmentoTubo(
                p1=p1, p2=p2, radio=radio_tubo, camino_id=camino_id
            ))
    return segmentos
