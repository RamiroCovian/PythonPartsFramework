"""
Ejemplo de visualizacion de techos inclinados con vertices IS.

Demuestra:
- Creacion de techos con diferentes inclinaciones
- Proyeccion de puntos sobre el plano del techo
- Visualizacion de vertices IS
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modelos.punto import Punto3D
from src.modelos.techo import Techo
from src.visualizacion.visualizador_3d import Visualizador3D


def ejemplo_techos_inclinados():
    """
    Crea y visualiza varios tipos de techos inclinados.
    """
    print("Creando visualizacion de techos inclinados...")
    
    vis = Visualizador3D("Techos Inclinados - Vertices IS")
    
    # Techo 1: Inclinacion simple (una agua)
    techo1 = Techo.desde_vertices([
        [0, 0, 0],         # IS1
        [2000, 0, 0],      # IS2
        [2000, 1500, 500], # IS3 (elevado)
        [0, 1500, 500]     # IS4 (elevado)
    ], id="Techo_Una_Agua")
    
    vis.agregar_techo(techo1, "Techo Una Agua")
    
    # Agregar puntos de ejemplo proyectados sobre el techo
    puntos_techo1 = []
    for x in [500, 1000, 1500]:
        for y in [500, 1000]:
            z = techo1.calcular_z_en_plano(x, y)
            puntos_techo1.append(Punto3D(x=x, y=y, z=z, id=f"P_{x}_{y}"))
    
    vis.agregar_puntos(puntos_techo1, "Puntos Techo 1", color='rgb(255, 100, 100)')
    
    # Techo 2: Inclinacion diagonal (desplazado)
    offset_x = 2500
    techo2 = Techo.desde_vertices([
        [offset_x + 0, 0, 0],
        [offset_x + 2000, 0, 300],
        [offset_x + 2000, 1500, 600],
        [offset_x + 0, 1500, 300]
    ], id="Techo_Diagonal")
    
    vis.agregar_techo(techo2, "Techo Diagonal", color_superficie='rgba(100, 200, 100, 0.3)')
    
    # Puntos proyectados
    puntos_techo2 = []
    for x in [500, 1000, 1500]:
        for y in [500, 1000]:
            real_x = offset_x + x
            z = techo2.calcular_z_en_plano(real_x, y)
            puntos_techo2.append(Punto3D(x=real_x, y=y, z=z, id=f"Q_{x}_{y}"))
    
    vis.agregar_puntos(puntos_techo2, "Puntos Techo 2", color='rgb(100, 255, 100)')
    
    # Techo 3: Horizontal (referencia)
    offset_x2 = 5000
    techo3 = Techo.desde_vertices([
        [offset_x2 + 0, 0, 300],
        [offset_x2 + 2000, 0, 300],
        [offset_x2 + 2000, 1500, 300],
        [offset_x2 + 0, 1500, 300]
    ], id="Techo_Horizontal")
    
    vis.agregar_techo(techo3, "Techo Horizontal", color_superficie='rgba(100, 100, 200, 0.3)')
    
    # Informacion de techos
    print("\nInformacion de techos:")
    for techo in [techo1, techo2, techo3]:
        ancho, alto = techo.obtener_dimensiones()
        inclinacion = techo.obtener_inclinacion()
        print(f"  {techo.id}:")
        print(f"    Dimensiones: {ancho:.0f} x {alto:.0f} mm")
        print(f"    Inclinacion: {inclinacion:.1f} grados")
        print(f"    Normal: {techo.normal}")
    
    # Guardar y mostrar
    ruta_salida = Path(__file__).parent.parent / "outputs" / "techos_inclinados.html"
    vis.guardar_html(str(ruta_salida))
    print(f"\nVisualizacion guardada en: {ruta_salida}")
    
    vis.mostrar()
    
    return vis


if __name__ == "__main__":
    ejemplo_techos_inclinados()
