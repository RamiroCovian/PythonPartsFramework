"""
Modelo de datos para techos inclinados y vertices IS.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

from .punto import Punto3D


@dataclass
class VerticeIS:
    """
    Representa un vertice de subdivision de techo (IS).
    
    Los IS son subdivisiones del techo padre y DEBEN tener la misma inclinacion.
    """
    id: str
    punto: Punto3D
    
    def __repr__(self) -> str:
        return f"VerticeIS(id='{self.id}', punto={self.punto})"


@dataclass
class Techo:
    """
    Representa un techo inclinado definido por vertices IS.
    
    El techo se define por 4 vertices (IS1, IS2, IS3, IS4) que forman
    un cuadrilatero en el espacio 3D. El plano del techo puede estar
    inclinado.
    
    Especificaciones (en mm):
    - Ancho: 1450mm - 5650mm
    - Alto: 1450mm - 2150mm
    - Margen entre IS: 50mm
    """
    vertices: List[VerticeIS] = field(default_factory=list)
    id: Optional[str] = None
    _normal: Optional[np.ndarray] = field(default=None, repr=False)
    
    # Constantes de dimensiones
    ANCHO_MIN_MM: float = 1450.0
    ANCHO_MAX_MM: float = 5650.0
    ALTO_MIN_MM: float = 1450.0
    ALTO_MAX_MM: float = 2150.0
    MARGEN_IS_MM: float = 50.0
    
    def __post_init__(self):
        """Calcula la normal del techo si hay suficientes vertices."""
        if len(self.vertices) >= 3:
            self._calcular_normal()
    
    def agregar_vertice(self, id: str, x: float, y: float, z: float) -> VerticeIS:
        """
        Agrega un nuevo vertice IS al techo.
        
        Args:
            id: Identificador del vertice (ej: "IS1", "IS2")
            x, y, z: Coordenadas en mm
        
        Returns:
            El vertice creado
        """
        punto = Punto3D(x=x, y=y, z=z, id=id)
        vertice = VerticeIS(id=id, punto=punto)
        self.vertices.append(vertice)
        
        if len(self.vertices) >= 3:
            self._calcular_normal()
        
        return vertice
    
    def _calcular_normal(self) -> None:
        """Calcula el vector normal del plano del techo."""
        if len(self.vertices) < 3:
            self._normal = np.array([0.0, 0.0, 1.0])
            return
        
        v0 = self.vertices[0].punto.como_array()
        v1 = self.vertices[1].punto.como_array()
        v2 = self.vertices[2].punto.como_array()
        
        vec1 = v1 - v0
        vec2 = v2 - v0
        
        normal = np.cross(vec1, vec2)
        norma = np.linalg.norm(normal)
        
        if norma > 0.001:
            normal = normal / norma
        else:
            normal = np.array([0.0, 0.0, 1.0])
        
        # Asegurar que apunte hacia arriba (Z positivo)
        if normal[2] < 0:
            normal = -normal
        
        self._normal = normal
    
    @property
    def normal(self) -> np.ndarray:
        """Vector normal del plano del techo."""
        if self._normal is None:
            self._calcular_normal()
        return self._normal
    
    def calcular_z_en_plano(self, x: float, y: float) -> float:
        """
        Calcula Z para un punto (X, Y) sobre el plano del techo.
        
        Ecuacion del plano: ax + by + cz = d
        Despejando: z = (d - a*x - b*y) / c
        
        Args:
            x: Coordenada X en mm
            y: Coordenada Y en mm
        
        Returns:
            Coordenada Z calculada
        """
        if len(self.vertices) < 1:
            return 0.0
        
        normal = self.normal
        punto_plano = self.vertices[0].punto.como_array()
        
        a, b, c = normal
        
        # Si el techo es horizontal (c aprox 1), Z es constante
        if abs(c) < 0.001:
            return punto_plano[2]
        
        # Calcular d (constante del plano)
        d = np.dot(normal, punto_plano)
        
        # Despejar Z
        z = (d - a * x - b * y) / c
        
        return float(z)
    
    def proyectar_punto(self, x: float, y: float) -> Punto3D:
        """
        Proyecta un punto (X, Y) sobre el plano del techo.
        
        Returns:
            Punto3D con las coordenadas proyectadas
        """
        z = self.calcular_z_en_plano(x, y)
        return Punto3D(x=x, y=y, z=z)
    
    def obtener_limites(self) -> Tuple[Punto3D, Punto3D]:
        """
        Obtiene los limites del techo (bounding box).
        
        Returns:
            Tupla (punto_minimo, punto_maximo)
        """
        if not self.vertices:
            return Punto3D.origen(), Punto3D.origen()
        
        xs = [v.punto.x for v in self.vertices]
        ys = [v.punto.y for v in self.vertices]
        zs = [v.punto.z for v in self.vertices]
        
        return (
            Punto3D(x=min(xs), y=min(ys), z=min(zs)),
            Punto3D(x=max(xs), y=max(ys), z=max(zs))
        )
    
    def punto_dentro(self, punto: Punto3D) -> bool:
        """
        Verifica si un punto esta dentro de los limites del techo (plano XY).
        
        Args:
            punto: Punto a verificar
        
        Returns:
            True si el punto esta dentro
        """
        if not self.vertices:
            return False
        
        min_p, max_p = self.obtener_limites()
        
        return (
            min_p.x <= punto.x <= max_p.x and
            min_p.y <= punto.y <= max_p.y
        )
    
    def obtener_dimensiones(self) -> Tuple[float, float]:
        """
        Obtiene las dimensiones del techo en mm.
        
        Returns:
            Tupla (ancho, alto)
        """
        if not self.vertices:
            return (0.0, 0.0)
        
        min_p, max_p = self.obtener_limites()
        
        ancho = max_p.x - min_p.x
        alto = max_p.y - min_p.y
        
        return (ancho, alto)
    
    def validar_dimensiones(self) -> Tuple[bool, str]:
        """
        Valida que las dimensiones esten dentro del rango permitido.
        
        Returns:
            Tupla (es_valido, mensaje)
        """
        ancho, alto = self.obtener_dimensiones()
        
        if not (self.ANCHO_MIN_MM <= ancho <= self.ANCHO_MAX_MM):
            return False, f"Ancho {ancho:.0f}mm fuera de rango [{self.ANCHO_MIN_MM}, {self.ANCHO_MAX_MM}]"
        
        if not (self.ALTO_MIN_MM <= alto <= self.ALTO_MAX_MM):
            return False, f"Alto {alto:.0f}mm fuera de rango [{self.ALTO_MIN_MM}, {self.ALTO_MAX_MM}]"
        
        return True, "OK"
    
    def obtener_inclinacion(self) -> float:
        """
        Obtiene el angulo de inclinacion del techo en grados.
        
        Returns:
            Angulo de inclinacion respecto al plano horizontal
        """
        normal = self.normal
        # Angulo entre la normal y el eje Z
        cos_angulo = abs(normal[2])
        cos_angulo = np.clip(cos_angulo, -1.0, 1.0)
        angulo_rad = np.arccos(cos_angulo)
        return float(np.degrees(angulo_rad))
    
    def como_lista_puntos(self) -> List[List[float]]:
        """Retorna los vertices como lista de listas [x, y, z]."""
        return [v.punto.como_lista() for v in self.vertices]
    
    @classmethod
    def desde_vertices(
        cls, 
        vertices: List[List[float]], 
        id: Optional[str] = None
    ) -> 'Techo':
        """
        Crea un techo desde una lista de vertices.
        
        Args:
            vertices: Lista de coordenadas [[x, y, z], ...]
            id: Identificador opcional del techo
        
        Returns:
            Instancia de Techo
        """
        techo = cls(id=id)
        for i, coords in enumerate(vertices):
            techo.agregar_vertice(
                id=f"IS{i+1}",
                x=coords[0],
                y=coords[1],
                z=coords[2]
            )
        return techo
