"""
Post-procesamiento IS y construccion de la visualizacion 3D.
"""

from typing import List, Dict, Tuple, Optional

from ..modelos.punto import Punto3D
from ..visualizacion.visualizador_3d import Visualizador3D
from ..reportes import Segmento, ResultadoCamino
from ..post_procesamiento import procesar_asignacion_is
from .entrada import EntradaProcesada
from .geometria_techo import calcular_z_eje


def post_procesar_is(
    camino: List[Punto3D],
    resultado: ResultadoCamino,
    entrada: EntradaProcesada,
    camino_idx: int = None,
) -> Tuple[Optional[Dict], List[Punto3D]]:
    """
    Post-procesamiento: asignacion IS y puntos U (solo si ruta valida).
    
    Returns:
        (grafo_is, puntos_u)
    """
    if not resultado.es_valido:
        return None, []
    
    subtipo_obj = entrada.config_subtipo['subtipo_obj']
    angulos_codo = subtipo_obj.angulos_permitidos if subtipo_obj else []
    es_subtipo_90 = angulos_codo == [90]
    dist_min_u = 0 if es_subtipo_90 else 1000.0  # 1m para subtipos != 90°
    
    z_eje_fn = lambda x, y: calcular_z_eje(x, y, entrada.vertices_techo, entrada.subtipo)
    resultado_is = procesar_asignacion_is(
        camino, entrada.subdivisiones, entrada.vertices_techo,
        z_eje_fn=z_eje_fn, distancia_minima_u=dist_min_u,
        camino_idx=camino_idx
    )
    grafo_is = resultado_is['grafo']
    puntos_u = resultado_is['puntos_u']
    
    # Actualizar resultado con camino que incluye puntos U
    if puntos_u:
        camino_con_u = resultado_is['camino_con_u']
        segmentos_u = []
        for i in range(len(camino_con_u) - 1):
            segmentos_u.append(Segmento.desde_puntos(camino_con_u[i], camino_con_u[i+1]))
        resultado.puntos = camino_con_u
        resultado.segmentos = segmentos_u
        resultado.longitud_total = sum(s.longitud for s in segmentos_u)
    
    if puntos_u:
        print(f"\nPuntos de union IS detectados: {len(puntos_u)}")
        for pu in puntos_u:
            print(f"  {pu.id}: ({pu.x:.0f}, {pu.y:.0f}, {pu.z:.0f})")
    
    return grafo_is, puntos_u


def construir_visualizacion(
    entrada: EntradaProcesada,
    camino: List[Punto3D],
    puntos_u: List[Punto3D],
    tubos_is: list = None,
    soportes: list = None,
) -> Visualizador3D:
    """Construye el Visualizador3D con todos los elementos."""
    subtipo_obj = entrada.config_subtipo['subtipo_obj']
    radio_tubo = entrada.config_subtipo['radio']
    
    vis = Visualizador3D(entrada.nombre)
    # Dibujar bordes de todos los techos
    for t in entrada.techos:
        verts_t = [[v['x'], v['y'], v['z']] for v in t['vertices']]
        vis.agregar_borde_techo(verts_t, nombre=f"Techo ({t.get('id', '')})")
    distancia_techo = subtipo_obj.distancia_techo_mm if subtipo_obj else 110.0
    vis.agregar_plano_tuberia(entrada.vertices_techo, distancia_techo)
    vis.agregar_subdivisiones_is(entrada.subdivisiones)
    vis.agregar_punto_inicio(entrada.inicio_real)
    vis.agregar_punto_fin(entrada.fin_real)
    vis.agregar_puntos_intermedios(
        puntos_obligatorios=entrada.puntos_obligatorios,
        puntos_libres=entrada.puntos_libres,
        puntos_conexion=[]
    )
    
    # Agregar puntos U (rosados)
    if puntos_u:
        vis.agregar_puntos_union(puntos_u)
    
    # Agregar obstaculos
    for obs in entrada.obstaculos:
        vis.agregar_obstaculo(obs, nombre=obs.id)
    
    # Agregar camino (excluir O, L y U para que no se etiqueten como C)
    puntos_excluir = entrada.puntos_obligatorios + entrada.puntos_libres + puntos_u
    vis.agregar_camino(camino, nombre="Camino (eje)", puntos_excluir=puntos_excluir)
    
    # Agregar tuberia 3D
    vis.agregar_tuberia_3d(camino, radio=radio_tubo, nombre="Tuberia 3D")
    
    # Agregar tubos IS y soportes si se proporcionaron
    if tubos_is:
        vis.agregar_tubos_is(tubos_is)
    if soportes:
        vis.agregar_soportes(soportes)
    
    return vis
