"""
Modelo de datos para obstaculos en el espacio.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple
import numpy as np

from .punto import Punto3D


@dataclass
class Obstaculo:
    """
    Representa un obstaculo con forma de prisma rectangular.
    
    Los obstaculos son PARALELOS al plano del techo.
    Se definen por sus 8 vertices o por posicion central + dimensiones.
    
    Attributes:
        centro: Punto central del obstaculo
        ancho_mm: Dimension en X
        largo_mm: Dimension en Y
        alto_mm: Dimension en Z
        id: Identificador del obstaculo
        normal_techo: Normal del plano del techo (default: horizontal)
        modo: Modo(s) de manejo del obstaculo ('saltar', 'rodear', 'bajar' o lista)
        _vertices_originales: Vertices originales si se creó desde vertices
    """
    centro: Punto3D
    ancho_mm: float
    largo_mm: float
    alto_mm: float
    id: Optional[str] = None
    normal_techo: Optional[Tuple[float, float, float]] = None
    rotacion_grados: float = 0.0
    margen_mm: float = 0.0
    modo: Any = "rodear"  # str o List[str]: 'saltar', 'rodear', 'bajar'
    _vertices_originales: Optional[List[Punto3D]] = field(default=None, repr=False)

    def _obtener_base_local(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula los vectores base para un obstaculo paralelo al techo.
        
        Returns:
            (u, v, n): vectores unitarios del sistema local
        """
        if self.normal_techo is None:
            # Techo horizontal por defecto
            n = np.array([0.0, 0.0, 1.0])
        else:
            n = np.array(self.normal_techo)
            norma = np.linalg.norm(n)
            if norma > 0.001:
                n = n / norma
            else:
                n = np.array([0.0, 0.0, 1.0])
        
        # Vector U: proyeccion de X en el plano del techo
        if abs(n[0]) < 0.9:
            u = np.cross(np.array([0, 0, 1]), n)
        else:
            u = np.cross(np.array([0, 1, 0]), n)
        
        u_norma = np.linalg.norm(u)
        if u_norma > 0.001:
            u = u / u_norma
        else:
            u = np.array([1.0, 0.0, 0.0])
        
        # Vector V: perpendicular a U y N
        v = np.cross(n, u)
        v = v / np.linalg.norm(v)
        
        return u, v, n
    
    @property
    def vertices(self) -> List[Punto3D]:
        """
        Calcula los 8 vertices del prisma PARALELO al techo.
        
        Returns:
            Lista de 8 puntos (4 base inferior, 4 base superior)
        """
        cx, cy, cz = self.centro.x, self.centro.y, self.centro.z
        centro = np.array([cx, cy, cz])
        
        du = self.ancho_mm / 2
        dv = self.largo_mm / 2
        dn = self.alto_mm / 2
        
        u, v, n = self._obtener_base_local()
        
        # Aplicar rotacion en el plano UV si es necesario
        if abs(self.rotacion_grados) > 0.001:
            rad = np.radians(self.rotacion_grados)
            cos_r = np.cos(rad)
            sin_r = np.sin(rad)
            u_rot = cos_r * u + sin_r * v
            v_rot = -sin_r * u + cos_r * v
            u, v = u_rot, v_rot
        
        # Vertices en coordenadas locales
        offsets = [
            # Base inferior (hacia abajo respecto al techo)
            (-du, -dv, -dn),
            (+du, -dv, -dn),
            (+du, +dv, -dn),
            (-du, +dv, -dn),
            # Base superior (hacia arriba respecto al techo)
            (-du, -dv, +dn),
            (+du, -dv, +dn),
            (+du, +dv, +dn),
            (-du, +dv, +dn),
        ]
        
        vertices = []
        for ou, ov, on in offsets:
            pos = centro + ou * u + ov * v + on * n
            vertices.append(Punto3D(x=pos[0], y=pos[1], z=pos[2]))
        
        return vertices
    
    @property
    def limites(self) -> Tuple[Punto3D, Punto3D]:
        """
        Obtiene el bounding box del obstaculo.
        
        Returns:
            Tupla (punto_minimo, punto_maximo)
        """
        verts = self.vertices
        xs = [v.x for v in verts]
        ys = [v.y for v in verts]
        zs = [v.z for v in verts]
        
        margen = self.margen_mm
        return (
            Punto3D(x=min(xs) - margen, y=min(ys) - margen, z=min(zs) - margen),
            Punto3D(x=max(xs) + margen, y=max(ys) + margen, z=max(zs) + margen)
        )
    
    def contiene_punto(self, punto: Punto3D) -> bool:
        """
        Verifica si un punto esta dentro del obstaculo.
        
        Args:
            punto: Punto a verificar
        
        Returns:
            True si el punto esta dentro
        """
        min_p, max_p = self.limites
        
        return (
            min_p.x <= punto.x <= max_p.x and
            min_p.y <= punto.y <= max_p.y and
            min_p.z <= punto.z <= max_p.z
        )
    
    def intersecta_segmento(
        self, 
        p1: Punto3D, 
        p2: Punto3D,
        pasos: int = 10
    ) -> bool:
        """
        Verifica si un segmento de linea intersecta el obstaculo.
        
        Usa muestreo discreto para simplificar el calculo.
        
        Args:
            p1: Punto inicial del segmento
            p2: Punto final del segmento
            pasos: Numero de puntos a verificar
        
        Returns:
            True si hay interseccion
        """
        for i in range(pasos + 1):
            t = i / pasos
            punto = Punto3D(
                x=p1.x + t * (p2.x - p1.x),
                y=p1.y + t * (p2.y - p1.y),
                z=p1.z + t * (p2.z - p1.z)
            )
            if self.contiene_punto(punto):
                return True
        return False
    
    def distancia_a_punto(self, punto: Punto3D) -> float:
        """
        Calcula la distancia minima del obstaculo a un punto.
        
        Args:
            punto: Punto de referencia
        
        Returns:
            Distancia en mm (0 si el punto esta dentro)
        """
        min_p, max_p = self.limites
        
        # Calcular punto mas cercano en el bounding box
        cx = max(min_p.x, min(punto.x, max_p.x))
        cy = max(min_p.y, min(punto.y, max_p.y))
        cz = max(min_p.z, min(punto.z, max_p.z))
        
        punto_cercano = Punto3D(x=cx, y=cy, z=cz)
        return punto.distancia_a(punto_cercano)
    
    def expandir(self, margen: float) -> 'Obstaculo':
        """
        Retorna una copia del obstaculo expandido por un margen.
        
        Util para calcular colisiones con tuberias.
        
        Args:
            margen: Margen a agregar en mm
        
        Returns:
            Nuevo obstaculo expandido
        """
        return Obstaculo(
            centro=self.centro.clonar(),
            ancho_mm=self.ancho_mm + 2 * margen,
            largo_mm=self.largo_mm + 2 * margen,
            alto_mm=self.alto_mm + 2 * margen,
            id=self.id,
            rotacion_grados=self.rotacion_grados,
            margen_mm=0.0,
            modo=self.modo
        )
    
    def __repr__(self) -> str:
        return (
            f"Obstaculo(id='{self.id}', "
            f"centro={self.centro}, "
            f"dims={self.ancho_mm:.0f}x{self.largo_mm:.0f}x{self.alto_mm:.0f}mm)"
        )
    
    @classmethod
    def desde_vertices(
        cls,
        vertices_data: List[dict],
        id: Optional[str] = None,
        modo: Any = "rodear"
    ) -> 'Obstaculo':
        """
        Crea un obstaculo desde una lista de vertices (8 o mas puntos con x, y, z).
        Calcula centro y dimensiones automaticamente desde el bounding box.
        
        Args:
            vertices_data: Lista de dicts con 'x', 'y', 'z'
            id: Identificador opcional
            modo: Modo(s) de manejo
        
        Returns:
            Obstaculo creado
        """
        xs = [v['x'] for v in vertices_data]
        ys = [v['y'] for v in vertices_data]
        zs = [v['z'] for v in vertices_data]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        z_min, z_max = min(zs), max(zs)
        
        centro = Punto3D(
            x=(x_min + x_max) / 2,
            y=(y_min + y_max) / 2,
            z=(z_min + z_max) / 2
        )
        
        vertices_pts = [
            Punto3D(x=v['x'], y=v['y'], z=v['z'])
            for v in vertices_data
        ]
        
        return cls(
            centro=centro,
            ancho_mm=x_max - x_min,
            largo_mm=y_max - y_min,
            alto_mm=z_max - z_min,
            id=id,
            modo=modo,
            _vertices_originales=vertices_pts
        )
    
    @classmethod
    def desde_esquinas(
        cls,
        esquina_min: Punto3D,
        esquina_max: Punto3D,
        id: Optional[str] = None
    ) -> 'Obstaculo':
        """
        Crea un obstaculo desde dos esquinas opuestas.
        
        Args:
            esquina_min: Esquina con coordenadas minimas
            esquina_max: Esquina con coordenadas maximas
            id: Identificador opcional
        
        Returns:
            Obstaculo creado
        """
        centro = Punto3D(
            x=(esquina_min.x + esquina_max.x) / 2,
            y=(esquina_min.y + esquina_max.y) / 2,
            z=(esquina_min.z + esquina_max.z) / 2
        )
        
        return cls(
            centro=centro,
            ancho_mm=abs(esquina_max.x - esquina_min.x),
            largo_mm=abs(esquina_max.y - esquina_min.y),
            alto_mm=abs(esquina_max.z - esquina_min.z),
            id=id
        )


@dataclass 
class GestorObstaculos:
    """
    Gestiona una coleccion de obstaculos y proporciona metodos de consulta.
    """
    obstaculos: List[Obstaculo] = field(default_factory=list)
    
    def agregar(self, obstaculo: Obstaculo) -> None:
        """Agrega un obstaculo a la lista."""
        self.obstaculos.append(obstaculo)
    
    def remover(self, id: str) -> bool:
        """Remueve un obstaculo por su ID."""
        for i, obs in enumerate(self.obstaculos):
            if obs.id == id:
                self.obstaculos.pop(i)
                return True
        return False
    
    def hay_colision(self, punto: Punto3D) -> bool:
        """Verifica si un punto colisiona con algun obstaculo."""
        return any(obs.contiene_punto(punto) for obs in self.obstaculos)
    
    def segmento_colisiona(self, p1: Punto3D, p2: Punto3D) -> bool:
        """Verifica si un segmento colisiona con algun obstaculo."""
        return any(obs.intersecta_segmento(p1, p2) for obs in self.obstaculos)
    
    def obtener_obstaculos_cercanos(
        self, 
        punto: Punto3D, 
        radio: float
    ) -> List[Obstaculo]:
        """
        Obtiene obstaculos dentro de un radio.
        
        Args:
            punto: Centro de busqueda
            radio: Radio en mm
        
        Returns:
            Lista de obstaculos cercanos
        """
        return [
            obs for obs in self.obstaculos
            if obs.distancia_a_punto(punto) <= radio
        ]
    
    def expandir_todos(self, margen: float) -> 'GestorObstaculos':
        """
        Retorna un nuevo gestor con todos los obstaculos expandidos.
        
        Util para considerar el radio de las tuberias.
        """
        return GestorObstaculos(
            obstaculos=[obs.expandir(margen) for obs in self.obstaculos]
        )
