"""
Modelo de datos para tuberias de ventilacion y sus subtipos.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import math

from .punto import Punto3D


@dataclass
class DimensionesPerfil:
    """
    Dimensiones del perfil de una tuberia.
    
    Attributes:
        ancho_mm: Ancho del perfil en milimetros
        alto_mm: Alto del perfil en milimetros
    """
    ancho_mm: float
    alto_mm: float
    
    @property
    def dimension_maxima_mm(self) -> float:
        """Retorna la dimension maxima (para calcular radio de colision)."""
        return max(self.ancho_mm, self.alto_mm)
    
    @property
    def radio_mm(self) -> float:
        """Radio aproximado para colisiones (asumiendo perfil circular)."""
        return self.dimension_maxima_mm / 2
    
    @property
    def area_mm2(self) -> float:
        """Area del perfil en mm cuadrados."""
        return self.ancho_mm * self.alto_mm
    
    def __str__(self) -> str:
        return f"{self.ancho_mm:.0f}x{self.alto_mm:.0f}mm"


class TipoSubtipo(Enum):
    """Enumeracion de subtipos de tuberia de ventilacion."""
    EXTRACCION_IMPULSION = "extraccion_impulsion"
    AISLADO = "aislado"
    RECUPERADOR = "recuperador"


@dataclass
class SubtipoTuberia:
    """
    Define las caracteristicas de un subtipo de tuberia.
    
    Attributes:
        nombre: Nombre descriptivo
        clave: Clave de identificacion
        dimensiones: Dimensiones del perfil
        angulos_permitidos: Lista de angulos permitidos en grados
        longitud_minima_mm: Longitud minima de cada segmento
        margen_seguridad_mm: Margen de seguridad alrededor de la tuberia
        descripcion: Descripcion del subtipo
    """
    nombre: str
    clave: str
    dimensiones: DimensionesPerfil
    angulos_permitidos: List[int]
    distancia_techo_mm: float = 110.0
    longitud_minima_mm: float = 150.0
    margen_seguridad_mm: float = 10.0
    descripcion: str = ""
    
    @property
    def radio_total_mm(self) -> float:
        """Radio total incluyendo margen de seguridad."""
        return self.dimensiones.radio_mm + self.margen_seguridad_mm
    
    @property
    def margen_colision_mm(self) -> float:
        """Margen para deteccion de colisiones."""
        return self.radio_total_mm
    
    def angulo_es_valido(self, angulo: float, tolerancia: float = 1.0) -> bool:
        """
        Verifica si un angulo esta permitido.
        
        Args:
            angulo: Angulo a verificar en grados
            tolerancia: Tolerancia en grados
        
        Returns:
            True si el angulo es valido
        """
        for ang_permitido in self.angulos_permitidos:
            if abs(angulo - ang_permitido) <= tolerancia:
                return True
            # Tambien verificar angulo complementario (180 - angulo)
            if abs(angulo - (180 - ang_permitido)) <= tolerancia:
                return True
        return False
    
    def __repr__(self) -> str:
        return f"SubtipoTuberia('{self.nombre}', {self.dimensiones})"
    
    @property
    def angulo_movimiento(self) -> int:
        """
        Convierte angulo de codo a angulo de movimiento para el pathfinding.
        
        - Codo de 45° → movimiento de 135° (giro de 45° respecto a linea recta)
        - Codo de 90° → movimiento de 90° (giro ortogonal)
        
        El angulo de movimiento es el angulo INTERNO entre segmentos consecutivos.
        """
        if not self.angulos_permitidos:
            return 90  # Default ortogonal
        
        # Usar el primer angulo configurado como referencia
        angulo_codo = self.angulos_permitidos[0]
        
        if angulo_codo == 45:
            return 135  # Codo de 45° significa giros de 45° (angulo interno 135°)
        elif angulo_codo == 90:
            return 90   # Codo de 90° significa giros ortogonales
        elif angulo_codo == 135:
            return 135  # Ya es angulo de movimiento
        else:
            # Para otros angulos, el angulo de movimiento es 180 - angulo_codo
            return 180 - angulo_codo
    
    def obtener_angulos_movimiento(self) -> List[int]:
        """
        Retorna lista de angulos de movimiento validos para el pathfinding.
        
        Convierte cada angulo de codo a su angulo de movimiento correspondiente.
        Siempre incluye 180° (linea recta).
        """
        angulos_mov = set([180])  # Linea recta siempre permitida
        
        for ang_codo in self.angulos_permitidos:
            if ang_codo == 45:
                angulos_mov.add(135)  # 45° de desvio
            elif ang_codo == 90:
                angulos_mov.add(90)   # 90° de desvio
            elif ang_codo == 135:
                angulos_mov.add(135)
            else:
                angulos_mov.add(180 - ang_codo)
        
        return sorted(list(angulos_mov))
    
    @classmethod
    def desde_dict(cls, clave: str, datos: Dict[str, Any]) -> 'SubtipoTuberia':
        """Crea un SubtipoTuberia desde un diccionario."""
        dimensiones = DimensionesPerfil(
            ancho_mm=datos['dimensiones']['ancho_mm'],
            alto_mm=datos['dimensiones']['alto_mm']
        )
        # Valores leidos del JSON de config; si no existen, usa valores por defecto
        return cls(
            nombre=datos.get('nombre', clave),
            clave=clave,
            dimensiones=dimensiones,
            angulos_permitidos=datos.get('angulos_permitidos', [45, 90, 135]),
            distancia_techo_mm=datos.get('distancia_techo_mm', 110.0),
            longitud_minima_mm=datos.get('longitud_minima_mm', 150.0),
            margen_seguridad_mm=datos.get('margen_seguridad_mm', 10.0),
            descripcion=datos.get('descripcion', '')
        )


@dataclass
class SegmentoTuberia:
    """
    Representa un segmento individual de tuberia entre dos puntos.
    """
    inicio: Punto3D
    fin: Punto3D
    subtipo: SubtipoTuberia
    id: Optional[str] = None
    
    @property
    def longitud_mm(self) -> float:
        """Longitud del segmento en mm."""
        return self.inicio.distancia_a(self.fin)
    
    @property
    def direccion(self) -> List[float]:
        """Vector direccion normalizado del segmento."""
        dx = self.fin.x - self.inicio.x
        dy = self.fin.y - self.inicio.y
        dz = self.fin.z - self.inicio.z
        
        longitud = self.longitud_mm
        if longitud < 0.001:
            return [0.0, 0.0, 0.0]
        
        return [dx/longitud, dy/longitud, dz/longitud]
    
    def es_valido(self) -> tuple[bool, str]:
        """
        Verifica si el segmento cumple con las restricciones.
        
        Returns:
            Tupla (es_valido, mensaje)
        """
        if self.longitud_mm < self.subtipo.longitud_minima_mm:
            return False, f"Longitud {self.longitud_mm:.1f}mm menor que minimo {self.subtipo.longitud_minima_mm}mm"
        return True, "OK"
    
    def punto_en_segmento(self, t: float) -> Punto3D:
        """
        Obtiene un punto a lo largo del segmento.
        
        Args:
            t: Parametro entre 0 (inicio) y 1 (fin)
        
        Returns:
            Punto en la posicion indicada
        """
        t = max(0.0, min(1.0, t))
        return Punto3D(
            x=self.inicio.x + t * (self.fin.x - self.inicio.x),
            y=self.inicio.y + t * (self.fin.y - self.inicio.y),
            z=self.inicio.z + t * (self.fin.z - self.inicio.z)
        )
    
    def centro(self) -> Punto3D:
        """Retorna el punto central del segmento."""
        return self.punto_en_segmento(0.5)


@dataclass
class Tuberia:
    """
    Representa una tuberia completa compuesta de multiples segmentos.
    
    Una tuberia conecta puntos siguiendo las restricciones del subtipo
    (angulos permitidos, longitud minima, etc.).
    """
    subtipo: SubtipoTuberia
    segmentos: List[SegmentoTuberia] = field(default_factory=list)
    id: Optional[str] = None
    
    @property
    def longitud_total_mm(self) -> float:
        """Longitud total de todos los segmentos."""
        return sum(seg.longitud_mm for seg in self.segmentos)
    
    @property
    def numero_segmentos(self) -> int:
        """Numero de segmentos en la tuberia."""
        return len(self.segmentos)
    
    @property
    def puntos(self) -> List[Punto3D]:
        """Lista de todos los puntos de la tuberia."""
        if not self.segmentos:
            return []
        
        puntos = [self.segmentos[0].inicio]
        for seg in self.segmentos:
            puntos.append(seg.fin)
        return puntos
    
    def agregar_segmento(self, inicio: Punto3D, fin: Punto3D) -> SegmentoTuberia:
        """
        Agrega un nuevo segmento a la tuberia.
        
        Args:
            inicio: Punto de inicio del segmento
            fin: Punto final del segmento
        
        Returns:
            El segmento creado
        """
        segmento = SegmentoTuberia(
            inicio=inicio,
            fin=fin,
            subtipo=self.subtipo,
            id=f"{self.id}_seg{len(self.segmentos)}" if self.id else None
        )
        self.segmentos.append(segmento)
        return segmento
    
    def validar(self) -> List[tuple[bool, str]]:
        """
        Valida todos los segmentos y angulos de la tuberia.
        
        Returns:
            Lista de resultados de validacion por segmento
        """
        resultados = []
        
        for i, seg in enumerate(self.segmentos):
            es_valido, msg = seg.es_valido()
            resultados.append((es_valido, f"Segmento {i}: {msg}"))
        
        # Validar angulos entre segmentos consecutivos
        for i in range(len(self.segmentos) - 1):
            seg_actual = self.segmentos[i]
            seg_siguiente = self.segmentos[i + 1]
            
            from .punto import calcular_angulo_entre_segmentos
            angulo = calcular_angulo_entre_segmentos(
                seg_actual.inicio,
                seg_actual.fin,
                seg_siguiente.fin
            )
            
            if not self.subtipo.angulo_es_valido(angulo):
                resultados.append((
                    False, 
                    f"Angulo {angulo:.1f} grados entre segmentos {i} y {i+1} no permitido"
                ))
        
        return resultados
    
    def es_valida(self) -> bool:
        """Verifica si toda la tuberia es valida."""
        resultados = self.validar()
        return all(es_valido for es_valido, _ in resultados)
    
    @classmethod
    def desde_puntos(
        cls, 
        puntos: List[Punto3D], 
        subtipo: SubtipoTuberia,
        id: Optional[str] = None
    ) -> 'Tuberia':
        """
        Crea una tuberia desde una lista de puntos.
        
        Args:
            puntos: Lista de puntos a conectar
            subtipo: Subtipo de tuberia
            id: Identificador opcional
        
        Returns:
            Tuberia con los segmentos creados
        """
        tuberia = cls(subtipo=subtipo, id=id)
        
        for i in range(len(puntos) - 1):
            tuberia.agregar_segmento(puntos[i], puntos[i + 1])
        
        return tuberia


# Subtipos predefinidos
SUBTIPOS_VENTILACION: Dict[str, SubtipoTuberia] = {
    "extraccion_impulsion": SubtipoTuberia(
        nombre="Extraccion e Impulsion",
        clave="extraccion_impulsion",
        dimensiones=DimensionesPerfil(ancho_mm=75.0, alto_mm=75.0),
        angulos_permitidos=[45, 135],
        longitud_minima_mm=150.0,
        margen_seguridad_mm=10.0,
        descripcion="Ductos de extraccion e impulsion de aire"
    ),
    "aislado": SubtipoTuberia(
        nombre="Aislado",
        clave="aislado",
        dimensiones=DimensionesPerfil(ancho_mm=160.0, alto_mm=160.0),
        angulos_permitidos=[45, 135],
        longitud_minima_mm=150.0,
        margen_seguridad_mm=10.0,
        descripcion="Ductos con aislamiento termico"
    ),
    "recuperador": SubtipoTuberia(
        nombre="Recuperador",
        clave="recuperador",
        dimensiones=DimensionesPerfil(ancho_mm=160.0, alto_mm=160.0),
        angulos_permitidos=[90],
        longitud_minima_mm=150.0,
        margen_seguridad_mm=10.0,
        descripcion="Ductos para recuperadores de calor (solo ortogonal)"
    )
}
