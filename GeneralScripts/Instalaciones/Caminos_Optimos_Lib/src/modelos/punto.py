"""
Modelo de datos para puntos en espacio 3D.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import math


@dataclass
class Punto3D:
    """
    Representa un punto en el espacio tridimensional.
    
    Attributes:
        x: Coordenada X en milimetros
        y: Coordenada Y en milimetros
        z: Coordenada Z en milimetros
        id: Identificador opcional del punto
        es_obligatorio: Si el punto debe ser visitado en orden especifico
        orden: Orden de visita (None si es libre)
    """
    x: float
    y: float
    z: float
    id: Optional[str] = None
    es_obligatorio: bool = False
    orden: Optional[int] = None
    
    def __post_init__(self):
        """Validacion post-inicializacion."""
        self.x = float(self.x)
        self.y = float(self.y)
        self.z = float(self.z)
    
    def como_array(self) -> np.ndarray:
        """Retorna el punto como array numpy."""
        return np.array([self.x, self.y, self.z])
    
    def como_lista(self) -> List[float]:
        """Retorna el punto como lista."""
        return [self.x, self.y, self.z]
    
    def como_tupla(self) -> Tuple[float, float, float]:
        """Retorna el punto como tupla."""
        return (self.x, self.y, self.z)
    
    def distancia_a(self, otro: 'Punto3D') -> float:
        """Calcula la distancia euclidiana a otro punto."""
        dx = self.x - otro.x
        dy = self.y - otro.y
        dz = self.z - otro.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def distancia_xy(self, otro: 'Punto3D') -> float:
        """Calcula la distancia en el plano XY (ignorando Z)."""
        dx = self.x - otro.x
        dy = self.y - otro.y
        return math.sqrt(dx*dx + dy*dy)
    
    def punto_medio(self, otro: 'Punto3D') -> 'Punto3D':
        """Retorna el punto medio entre este punto y otro."""
        return Punto3D(
            x=(self.x + otro.x) / 2,
            y=(self.y + otro.y) / 2,
            z=(self.z + otro.z) / 2
        )
    
    def mover(self, dx: float = 0, dy: float = 0, dz: float = 0) -> 'Punto3D':
        """Retorna un nuevo punto desplazado."""
        return Punto3D(
            x=self.x + dx,
            y=self.y + dy,
            z=self.z + dz,
            id=self.id,
            es_obligatorio=self.es_obligatorio,
            orden=self.orden
        )
    
    def clonar(self) -> 'Punto3D':
        """Retorna una copia del punto."""
        return Punto3D(
            x=self.x,
            y=self.y,
            z=self.z,
            id=self.id,
            es_obligatorio=self.es_obligatorio,
            orden=self.orden
        )
    
    def __eq__(self, otro: object) -> bool:
        """Compara igualdad con tolerancia."""
        if not isinstance(otro, Punto3D):
            return False
        tolerancia = 0.001
        return (
            abs(self.x - otro.x) < tolerancia and
            abs(self.y - otro.y) < tolerancia and
            abs(self.z - otro.z) < tolerancia
        )
    
    def __hash__(self) -> int:
        """Hash basado en coordenadas redondeadas."""
        return hash((round(self.x, 3), round(self.y, 3), round(self.z, 3)))
    
    def __repr__(self) -> str:
        id_str = f", id='{self.id}'" if self.id else ""
        return f"Punto3D(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f}{id_str})"
    
    @classmethod
    def desde_lista(cls, coords: List[float], id: Optional[str] = None) -> 'Punto3D':
        """Crea un punto desde una lista de coordenadas [x, y, z]."""
        if len(coords) < 3:
            raise ValueError("La lista debe tener al menos 3 elementos [x, y, z]")
        return cls(x=coords[0], y=coords[1], z=coords[2], id=id)
    
    @classmethod
    def origen(cls) -> 'Punto3D':
        """Retorna el punto origen (0, 0, 0)."""
        return cls(x=0.0, y=0.0, z=0.0)


def calcular_angulo_entre_segmentos(
    p1: Punto3D, 
    p2: Punto3D, 
    p3: Punto3D
) -> float:
    """
    Calcula el angulo formado en p2 por los segmentos p1-p2 y p2-p3.
    
    Args:
        p1: Punto inicial del primer segmento
        p2: Punto central (vertice del angulo)
        p3: Punto final del segundo segmento
    
    Returns:
        Angulo en grados (0-180)
    """
    v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
    
    norma_v1 = np.linalg.norm(v1)
    norma_v2 = np.linalg.norm(v2)
    
    if norma_v1 < 0.001 or norma_v2 < 0.001:
        return 0.0
    
    cos_angulo = np.dot(v1, v2) / (norma_v1 * norma_v2)
    cos_angulo = np.clip(cos_angulo, -1.0, 1.0)
    
    angulo_rad = math.acos(cos_angulo)
    return math.degrees(angulo_rad)
