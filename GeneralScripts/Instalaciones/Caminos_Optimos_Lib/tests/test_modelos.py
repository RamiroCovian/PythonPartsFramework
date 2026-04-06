"""
Tests unitarios para los modelos de datos.
"""

import sys
from pathlib import Path
import unittest
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modelos.punto import Punto3D, calcular_angulo_entre_segmentos
from src.modelos.techo import Techo, VerticeIS
from src.modelos.tuberia import (
    DimensionesPerfil, 
    SubtipoTuberia, 
    SegmentoTuberia,
    Tuberia,
    SUBTIPOS_VENTILACION
)
from src.modelos.obstaculo import Obstaculo, GestorObstaculos


class TestPunto3D(unittest.TestCase):
    """Tests para la clase Punto3D."""
    
    def test_creacion_punto(self):
        """Test de creacion basica de punto."""
        p = Punto3D(x=100, y=200, z=300)
        self.assertEqual(p.x, 100)
        self.assertEqual(p.y, 200)
        self.assertEqual(p.z, 300)
    
    def test_distancia_a(self):
        """Test de calculo de distancia."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=100, y=0, z=0)
        self.assertAlmostEqual(p1.distancia_a(p2), 100, places=3)
        
        p3 = Punto3D(x=300, y=400, z=0)
        self.assertAlmostEqual(p1.distancia_a(p3), 500, places=3)
    
    def test_punto_medio(self):
        """Test de punto medio."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=100, y=100, z=100)
        medio = p1.punto_medio(p2)
        
        self.assertAlmostEqual(medio.x, 50, places=3)
        self.assertAlmostEqual(medio.y, 50, places=3)
        self.assertAlmostEqual(medio.z, 50, places=3)
    
    def test_desde_lista(self):
        """Test de creacion desde lista."""
        p = Punto3D.desde_lista([100, 200, 300], id="test")
        self.assertEqual(p.x, 100)
        self.assertEqual(p.id, "test")
    
    def test_mover(self):
        """Test de movimiento de punto."""
        p = Punto3D(x=100, y=100, z=100)
        p2 = p.mover(dx=50, dy=-50, dz=0)
        
        self.assertEqual(p2.x, 150)
        self.assertEqual(p2.y, 50)
        self.assertEqual(p2.z, 100)


class TestCalculoAngulos(unittest.TestCase):
    """Tests para calculo de angulos."""
    
    def test_angulo_recto(self):
        """Test de angulo de 90 grados."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=100, y=0, z=0)
        p3 = Punto3D(x=100, y=100, z=0)
        
        angulo = calcular_angulo_entre_segmentos(p1, p2, p3)
        self.assertAlmostEqual(angulo, 90, places=1)
    
    def test_angulo_45(self):
        """Test de angulo de 45 grados."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=100, y=0, z=0)
        p3 = Punto3D(x=200, y=100, z=0)
        
        angulo = calcular_angulo_entre_segmentos(p1, p2, p3)
        self.assertAlmostEqual(angulo, 135, places=1)  # Angulo interior
    
    def test_angulo_linea_recta(self):
        """Test de angulo de 180 grados (linea recta)."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=100, y=0, z=0)
        p3 = Punto3D(x=200, y=0, z=0)
        
        angulo = calcular_angulo_entre_segmentos(p1, p2, p3)
        self.assertAlmostEqual(angulo, 180, places=1)


class TestTecho(unittest.TestCase):
    """Tests para la clase Techo."""
    
    def test_crear_techo_horizontal(self):
        """Test de techo horizontal."""
        techo = Techo.desde_vertices([
            [0, 0, 100],
            [1000, 0, 100],
            [1000, 1000, 100],
            [0, 1000, 100]
        ])
        
        # La inclinacion debe ser 0
        self.assertAlmostEqual(techo.obtener_inclinacion(), 0, places=1)
        
        # Z debe ser constante
        self.assertAlmostEqual(techo.calcular_z_en_plano(500, 500), 100, places=1)
    
    def test_crear_techo_inclinado(self):
        """Test de techo inclinado."""
        techo = Techo.desde_vertices([
            [0, 0, 0],
            [1000, 0, 0],
            [1000, 1000, 500],
            [0, 1000, 500]
        ])
        
        # La inclinacion debe ser mayor a 0
        self.assertGreater(techo.obtener_inclinacion(), 0)
        
        # Z debe variar con Y
        z_bajo = techo.calcular_z_en_plano(500, 0)
        z_alto = techo.calcular_z_en_plano(500, 1000)
        self.assertLess(z_bajo, z_alto)
    
    def test_dimensiones_techo(self):
        """Test de calculo de dimensiones."""
        techo = Techo.desde_vertices([
            [0, 0, 0],
            [3000, 0, 0],
            [3000, 2000, 0],
            [0, 2000, 0]
        ])
        
        ancho, alto = techo.obtener_dimensiones()
        self.assertEqual(ancho, 3000)
        self.assertEqual(alto, 2000)
    
    def test_punto_dentro(self):
        """Test de verificacion de punto dentro del techo."""
        techo = Techo.desde_vertices([
            [0, 0, 0],
            [1000, 0, 0],
            [1000, 1000, 0],
            [0, 1000, 0]
        ])
        
        p_dentro = Punto3D(x=500, y=500, z=0)
        p_fuera = Punto3D(x=1500, y=500, z=0)
        
        self.assertTrue(techo.punto_dentro(p_dentro))
        self.assertFalse(techo.punto_dentro(p_fuera))


class TestTuberia(unittest.TestCase):
    """Tests para las clases de tuberia."""
    
    def test_dimensiones_perfil(self):
        """Test de DimensionesPerfil."""
        dim = DimensionesPerfil(ancho_mm=75, alto_mm=75)
        
        self.assertEqual(dim.dimension_maxima_mm, 75)
        self.assertEqual(dim.radio_mm, 37.5)
        self.assertEqual(dim.area_mm2, 5625)
    
    def test_subtipo_angulo_valido(self):
        """Test de validacion de angulos en subtipo."""
        subtipo = SUBTIPOS_VENTILACION["extraccion_impulsion"]
        
        self.assertTrue(subtipo.angulo_es_valido(45))
        self.assertTrue(subtipo.angulo_es_valido(135))
        self.assertFalse(subtipo.angulo_es_valido(60))
    
    def test_subtipo_recuperador_solo_90(self):
        """Test de que recuperador solo permite 90 grados."""
        subtipo = SUBTIPOS_VENTILACION["recuperador"]
        
        self.assertTrue(subtipo.angulo_es_valido(90))
        self.assertFalse(subtipo.angulo_es_valido(45))
    
    def test_crear_tuberia_desde_puntos(self):
        """Test de creacion de tuberia desde puntos."""
        puntos = [
            Punto3D(x=0, y=0, z=0),
            Punto3D(x=500, y=0, z=0),
            Punto3D(x=500, y=500, z=0)
        ]
        
        subtipo = SUBTIPOS_VENTILACION["extraccion_impulsion"]
        tuberia = Tuberia.desde_puntos(puntos, subtipo, id="test")
        
        self.assertEqual(tuberia.numero_segmentos, 2)
        self.assertAlmostEqual(tuberia.longitud_total_mm, 1000, places=1)
    
    def test_segmento_longitud(self):
        """Test de longitud de segmento."""
        p1 = Punto3D(x=0, y=0, z=0)
        p2 = Punto3D(x=300, y=400, z=0)
        
        subtipo = SUBTIPOS_VENTILACION["aislado"]
        seg = SegmentoTuberia(inicio=p1, fin=p2, subtipo=subtipo)
        
        self.assertAlmostEqual(seg.longitud_mm, 500, places=1)


class TestObstaculo(unittest.TestCase):
    """Tests para la clase Obstaculo."""
    
    def test_crear_obstaculo(self):
        """Test de creacion de obstaculo."""
        centro = Punto3D(x=500, y=500, z=100)
        obs = Obstaculo(
            centro=centro,
            ancho_mm=200,
            largo_mm=200,
            alto_mm=100,
            id="test"
        )
        
        self.assertEqual(len(obs.vertices), 8)
    
    def test_contiene_punto(self):
        """Test de verificacion de punto dentro de obstaculo."""
        centro = Punto3D(x=500, y=500, z=100)
        obs = Obstaculo(
            centro=centro,
            ancho_mm=200,
            largo_mm=200,
            alto_mm=100
        )
        
        p_dentro = Punto3D(x=500, y=500, z=100)
        p_fuera = Punto3D(x=800, y=800, z=100)
        
        self.assertTrue(obs.contiene_punto(p_dentro))
        self.assertFalse(obs.contiene_punto(p_fuera))
    
    def test_expandir(self):
        """Test de expansion de obstaculo."""
        centro = Punto3D(x=500, y=500, z=100)
        obs = Obstaculo(
            centro=centro,
            ancho_mm=200,
            largo_mm=200,
            alto_mm=100
        )
        
        obs_expandido = obs.expandir(50)
        
        self.assertEqual(obs_expandido.ancho_mm, 300)
        self.assertEqual(obs_expandido.largo_mm, 300)
        self.assertEqual(obs_expandido.alto_mm, 200)
    
    def test_gestor_obstaculos(self):
        """Test del gestor de obstaculos."""
        gestor = GestorObstaculos()
        
        obs1 = Obstaculo(
            centro=Punto3D(x=500, y=500, z=100),
            ancho_mm=200,
            largo_mm=200,
            alto_mm=100,
            id="obs1"
        )
        
        gestor.agregar(obs1)
        
        self.assertEqual(len(gestor.obstaculos), 1)
        self.assertTrue(gestor.hay_colision(Punto3D(x=500, y=500, z=100)))
        self.assertFalse(gestor.hay_colision(Punto3D(x=1000, y=1000, z=100)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
