"""
Ejemplo basico de uso del sistema de optimizacion de tuberias.

Este ejemplo muestra como:
1. Crear un techo inclinado con vertices IS
2. Definir puntos de conexion (obligatorios y libres)
3. Agregar obstaculos
4. Buscar un camino optimo
5. Visualizar el resultado en 3D
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modelos.punto import Punto3D
from src.modelos.techo import Techo
from src.modelos.tuberia import SUBTIPOS_VENTILACION
from src.modelos.obstaculo import Obstaculo, GestorObstaculos
from src.optimizacion.buscador_caminos import BuscadorCaminos
from src.visualizacion.visualizador_3d import Visualizador3D


def ejemplo_techo_simple():
    """
    Ejemplo con un techo simple inclinado y puntos de conexion.
    """
    print("=" * 60)
    print("EJEMPLO: Techo Simple con Tuberias de Ventilacion")
    print("=" * 60)
    
    # 1. Crear techo inclinado (3m x 2m con pendiente)
    # Los vertices IS definen las esquinas del techo
    techo = Techo.desde_vertices([
        [0, 0, 0],           # IS1 - esquina inferior izquierda
        [3000, 0, 300],      # IS2 - esquina inferior derecha (mas alta)
        [3000, 2000, 300],   # IS3 - esquina superior derecha
        [0, 2000, 0]         # IS4 - esquina superior izquierda
    ], id="Techo_Principal")
    
    print(f"\nTecho creado:")
    print(f"  - Dimensiones: {techo.obtener_dimensiones()[0]:.0f} x {techo.obtener_dimensiones()[1]:.0f} mm")
    print(f"  - Inclinacion: {techo.obtener_inclinacion():.1f} grados")
    
    # 2. Definir puntos de conexion
    # Punto de inicio (entrada de aire)
    inicio = Punto3D(
        x=200, 
        y=200, 
        z=techo.calcular_z_en_plano(200, 200),
        id="Entrada",
        es_obligatorio=True,
        orden=1
    )
    
    # Punto final (salida de aire)
    fin = Punto3D(
        x=2800, 
        y=1800, 
        z=techo.calcular_z_en_plano(2800, 1800),
        id="Salida",
        es_obligatorio=True,
        orden=3
    )
    
    # Punto intermedio opcional
    intermedio = Punto3D(
        x=1500, 
        y=1000, 
        z=techo.calcular_z_en_plano(1500, 1000),
        id="Conexion_1",
        es_obligatorio=False
    )
    
    puntos = [inicio, intermedio, fin]
    
    print(f"\nPuntos de conexion:")
    for p in puntos:
        tipo = "OBLIGATORIO" if p.es_obligatorio else "libre"
        print(f"  - {p.id}: ({p.x:.0f}, {p.y:.0f}, {p.z:.0f}) [{tipo}]")
    
    # 3. Crear obstaculo (viga estructural)
    obstaculo = Obstaculo(
        centro=Punto3D(x=1500, y=600, z=150),
        ancho_mm=300,
        largo_mm=2000,
        alto_mm=200,
        id="Viga_Central"
    )
    
    gestor_obs = GestorObstaculos()
    gestor_obs.agregar(obstaculo)
    
    print(f"\nObstaculos:")
    print(f"  - {obstaculo.id}: {obstaculo.ancho_mm:.0f}x{obstaculo.largo_mm:.0f}x{obstaculo.alto_mm:.0f} mm")
    
    # 4. Seleccionar subtipo de tuberia
    subtipo = SUBTIPOS_VENTILACION["extraccion_impulsion"]
    
    print(f"\nSubtipo de tuberia: {subtipo.nombre}")
    print(f"  - Dimensiones perfil: {subtipo.dimensiones}")
    print(f"  - Angulos permitidos: {subtipo.angulos_permitidos} grados")
    print(f"  - Longitud minima: {subtipo.longitud_minima_mm} mm")
    print(f"  - Margen seguridad: {subtipo.margen_seguridad_mm} mm")
    
    # 5. Buscar camino optimo
    buscador = BuscadorCaminos(
        subtipo=subtipo,
        techo=techo,
        gestor_obstaculos=gestor_obs
    )
    
    print("\nBuscando camino optimo...")
    camino = buscador.buscar_camino(inicio, fin, puntos_intermedios=[intermedio])
    
    if camino:
        print(f"  Camino encontrado con {len(camino)} puntos")
        
        # Crear tuberia
        tuberia = buscador.crear_tuberia(camino, id="Tuberia_Principal")
        print(f"  Longitud total: {tuberia.longitud_total_mm:.0f} mm")
        
        # Validar
        if tuberia.es_valida():
            print("  Estado: VALIDA")
        else:
            print("  Estado: Con errores")
            for valido, msg in tuberia.validar():
                if not valido:
                    print(f"    - {msg}")
    else:
        print("  No se encontro camino!")
        tuberia = None
    
    # 6. Visualizar
    print("\nGenerando visualizacion 3D...")
    
    vis = Visualizador3D("Ejemplo: Techo Simple con Ventilacion")
    
    # Agregar techo
    vis.agregar_techo(techo, "Techo Inclinado")
    
    # Agregar puntos
    vis.agregar_puntos(puntos, "Puntos de Conexion")
    
    # Agregar obstaculo
    vis.agregar_obstaculo(obstaculo)
    
    # Agregar tuberia si se encontro
    if tuberia:
        vis.agregar_tuberia(tuberia)
    
    # Guardar y mostrar
    ruta_salida = Path(__file__).parent.parent / "outputs" / "ejemplo_basico.html"
    vis.guardar_html(str(ruta_salida))
    print(f"  Guardado en: {ruta_salida}")
    
    # Mostrar en navegador
    vis.mostrar()
    
    return vis


def ejemplo_multiples_subtipos():
    """
    Ejemplo comparando diferentes subtipos de tuberia.
    """
    print("\n" + "=" * 60)
    print("EJEMPLO: Comparacion de Subtipos de Tuberia")
    print("=" * 60)
    
    # Crear techo
    techo = Techo.desde_vertices([
        [0, 0, 0],
        [4000, 0, 0],
        [4000, 3000, 400],
        [0, 3000, 400]
    ], id="Techo_Comparacion")
    
    # Puntos de prueba
    inicio = Punto3D(x=500, y=500, z=techo.calcular_z_en_plano(500, 500), id="A")
    fin = Punto3D(x=3500, y=2500, z=techo.calcular_z_en_plano(3500, 2500), id="B")
    
    vis = Visualizador3D("Comparacion de Subtipos")
    vis.agregar_techo(techo, "Techo")
    vis.agregar_puntos([inicio, fin], "Puntos")
    
    colores = ['rgb(0, 100, 200)', 'rgb(200, 100, 0)', 'rgb(100, 200, 0)']
    
    for i, (clave, subtipo) in enumerate(SUBTIPOS_VENTILACION.items()):
        print(f"\nSubtipo: {subtipo.nombre}")
        print(f"  Perfil: {subtipo.dimensiones}")
        print(f"  Angulos: {subtipo.angulos_permitidos}")
        
        buscador = BuscadorCaminos(subtipo=subtipo, techo=techo)
        camino = buscador.buscar_camino(inicio, fin)
        
        if camino:
            # Desplazar ligeramente para visualizacion
            offset = (i - 1) * 100
            camino_desplazado = [
                Punto3D(x=p.x, y=p.y + offset, z=p.z + offset/2)
                for p in camino
            ]
            
            vis.agregar_linea(
                camino_desplazado, 
                f"{subtipo.nombre}", 
                colores[i], 
                ancho=3
            )
            print(f"  Camino: {len(camino)} puntos")
        else:
            print(f"  No se encontro camino")
    
    ruta_salida = Path(__file__).parent.parent / "outputs" / "comparacion_subtipos.html"
    vis.guardar_html(str(ruta_salida))
    print(f"\nGuardado en: {ruta_salida}")
    
    return vis


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# EJEMPLOS DE USO - CAMINOS OPTIMOS")
    print("#" * 60)
    
    # Ejecutar ejemplo basico
    ejemplo_techo_simple()
    
    # Ejecutar comparacion de subtipos
    # ejemplo_multiples_subtipos()
    
    print("\n" + "#" * 60)
    print("# EJEMPLOS COMPLETADOS")
    print("#" * 60)
