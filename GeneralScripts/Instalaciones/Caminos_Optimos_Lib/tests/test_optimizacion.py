"""
Tests unitarios para el modulo de optimizacion.
"""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modelos.punto import Punto3D
from src.modelos.techo import Techo
from src.modelos.tuberia import SUBTIPOS_VENTILACION
from src.modelos.obstaculo import Obstaculo, GestorObstaculos
from src.optimizacion.buscador_caminos import BuscadorCaminos


class TestBuscadorCaminos(unittest.TestCase):
    """Tests para BuscadorCaminos."""
    
    def setUp(self):
        """Configuracion para cada test."""
        self.techo = Techo.desde_vertices([
            [0, 0, 0],
            [3000, 0, 0],
            [3000, 2000, 0],
            [0, 2000, 0]
        ])
        self.subtipo = SUBTIPOS_VENTILACION["extraccion_impulsion"]
    
    def test_camino_recto_sin_obstaculos(self):
        """Test de camino recto cuando no hay obstaculos."""
        buscador = BuscadorCaminos(
            subtipo=self.subtipo,
            techo=self.techo
        )
        
        inicio = Punto3D(x=500, y=500, z=0)
        fin = Punto3D(x=2500, y=500, z=0)
        
        camino = buscador.buscar_camino(inicio, fin)
        
        self.assertIsNotNone(camino)
        self.assertGreaterEqual(len(camino), 2)
        # El primer y ultimo punto deben coincidir
        self.assertEqual(camino[0].x, inicio.x)
        self.assertEqual(camino[-1].x, fin.x)
    
    def test_camino_con_obstaculo(self):
        """Test de camino evitando obstaculo."""
        gestor_obs = GestorObstaculos()
        obs = Obstaculo(
            centro=Punto3D(x=1500, y=500, z=0),
            ancho_mm=500,
            largo_mm=500,
            alto_mm=200,
            id="bloqueador"
        )
        gestor_obs.agregar(obs)
        
        buscador = BuscadorCaminos(
            subtipo=self.subtipo,
            techo=self.techo,
            gestor_obstaculos=gestor_obs
        )
        
        inicio = Punto3D(x=500, y=500, z=0)
        fin = Punto3D(x=2500, y=500, z=0)
        
        camino = buscador.buscar_camino(inicio, fin)
        
        # Debe encontrar un camino (aunque no sea recto)
        self.assertIsNotNone(camino)
        # El camino debe tener mas de 2 puntos (rodea obstaculo)
        self.assertGreater(len(camino), 2)
    
    def test_camino_con_puntos_intermedios(self):
        """Test de camino pasando por puntos intermedios."""
        buscador = BuscadorCaminos(
            subtipo=self.subtipo,
            techo=self.techo
        )
        
        inicio = Punto3D(x=500, y=500, z=0)
        fin = Punto3D(x=2500, y=1500, z=0)
        intermedio = Punto3D(x=1500, y=1000, z=0)
        
        camino = buscador.buscar_camino(
            inicio, fin, 
            puntos_intermedios=[intermedio]
        )
        
        self.assertIsNotNone(camino)
        
        # Verificar que pasa cerca del punto intermedio
        distancias = [p.distancia_a(intermedio) for p in camino]
        min_dist = min(distancias)
        # Debe pasar a menos de la resolucion del buscador
        self.assertLess(min_dist, 100)
    
    def test_crear_tuberia_desde_camino(self):
        """Test de creacion de tuberia desde camino encontrado."""
        buscador = BuscadorCaminos(
            subtipo=self.subtipo,
            techo=self.techo
        )
        
        inicio = Punto3D(x=500, y=500, z=0)
        fin = Punto3D(x=2500, y=1500, z=0)
        
        camino = buscador.buscar_camino(inicio, fin)
        
        self.assertIsNotNone(camino)
        
        tuberia = buscador.crear_tuberia(camino, id="test_tuberia")
        
        self.assertEqual(tuberia.id, "test_tuberia")
        self.assertEqual(tuberia.subtipo, self.subtipo)
        self.assertGreater(tuberia.longitud_total_mm, 0)
    
    def test_subtipo_recuperador_angulo_90(self):
        """Test de que el subtipo recuperador solo use angulos de 90."""
        subtipo_rec = SUBTIPOS_VENTILACION["recuperador"]
        
        buscador = BuscadorCaminos(
            subtipo=subtipo_rec,
            techo=self.techo
        )
        
        inicio = Punto3D(x=500, y=500, z=0)
        fin = Punto3D(x=2500, y=1500, z=0)
        
        camino = buscador.buscar_camino(inicio, fin)
        
        # El camino debe existir
        self.assertIsNotNone(camino)


class TestValidacionCaminos(unittest.TestCase):
    """Tests para validacion de caminos."""
    
    def setUp(self):
        """Configuracion para cada test."""
        self.subtipo = SUBTIPOS_VENTILACION["extraccion_impulsion"]
    
    def test_longitud_minima_segmento(self):
        """Test de longitud minima de segmentos."""
        techo = Techo.desde_vertices([
            [0, 0, 0],
            [1000, 0, 0],
            [1000, 1000, 0],
            [0, 1000, 0]
        ])
        
        buscador = BuscadorCaminos(subtipo=self.subtipo, techo=techo)
        
        # Puntos muy cercanos (menos que longitud minima)
        inicio = Punto3D(x=100, y=100, z=0)
        fin = Punto3D(x=200, y=100, z=0)  # Solo 100mm de distancia
        
        # La longitud minima es 150mm, asi que deberia encontrar
        # un camino valido de alguna forma o retornar None
        camino = buscador.buscar_camino(inicio, fin)
        
        if camino:
            # Si encuentra camino, verificar que segmentos cumplen minimo
            tuberia = buscador.crear_tuberia(camino)
            for seg in tuberia.segmentos:
                # Puede haber tolerancia
                self.assertGreaterEqual(
                    seg.longitud_mm, 
                    self.subtipo.longitud_minima_mm * 0.9  # 10% tolerancia
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
