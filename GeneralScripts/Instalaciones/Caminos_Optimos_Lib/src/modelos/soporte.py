"""
Modelo de datos para soportes de ventilación y tubos de IS.

Tipos de soporte:
    OMEGA (estándar): Se ancla a dos tubos IS paralelos. B=680mm fijo.
    ZETA  (especial): Se ancla a un solo tubo IS. B=variable.

Orientación del soporte (para el JSON de salida):
    "horizontal" → el soporte va en eje X (porque el tubo IS es vertical)
    "vertical"   → el soporte va en eje Y (porque el tubo IS es horizontal)
"""

import math
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .punto import Punto3D


# ---------------------------------------------------------------------------
# Tubo de IS
# ---------------------------------------------------------------------------

@dataclass
class TuboIS:
    """
    Representa un tubo estructural del IS donde se anclan los soportes.

    Los tubos de IS se definen en el input.json con punto_inicio y punto_fin.
    El sistema los dibuja como líneas en la visualización 3D.

    Attributes:
        id: Identificador del tubo (ej: "T1")
        is_id: ID del IS al que pertenece (ej: "IS1")
        punto_inicio: Extremo inicial del tubo
        punto_fin: Extremo final del tubo
    """
    id: str
    is_id: str
    punto_inicio: Punto3D
    punto_fin: Punto3D

    @property
    def longitud(self) -> float:
        """Longitud del tubo en mm."""
        return self.punto_inicio.distancia_a(self.punto_fin)

    @property
    def direccion_xy(self):
        """Dirección unitaria del tubo en el plano XY."""
        dx = self.punto_fin.x - self.punto_inicio.x
        dy = self.punto_fin.y - self.punto_inicio.y
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1e-6:
            return (0.0, 0.0)
        return (dx / length, dy / length)

    @property
    def es_horizontal(self) -> bool:
        """True si el tubo corre principalmente en eje X."""
        dx = abs(self.punto_fin.x - self.punto_inicio.x)
        dy = abs(self.punto_fin.y - self.punto_inicio.y)
        return dx >= dy

    @property
    def es_vertical(self) -> bool:
        """True si el tubo corre principalmente en eje Y."""
        return not self.es_horizontal

    def punto_en_t(self, t: float) -> Punto3D:
        """Punto sobre el tubo en parámetro *t* (0=inicio, 1=fin)."""
        t = max(0.0, min(1.0, t))
        return Punto3D(
            x=self.punto_inicio.x + t * (self.punto_fin.x - self.punto_inicio.x),
            y=self.punto_inicio.y + t * (self.punto_fin.y - self.punto_inicio.y),
            z=self.punto_inicio.z + t * (self.punto_fin.z - self.punto_inicio.z),
        )

    def __repr__(self) -> str:
        orient = "H" if self.es_horizontal else "V"
        return f"TuboIS(id='{self.id}', is_id='{self.is_id}', {orient}, L={self.longitud:.0f}mm)"

    # --- Serialización / Deserialización ---

    @classmethod
    def desde_dict(cls, datos: dict) -> 'TuboIS':
        """Crea un TuboIS desde un dict del input JSON."""
        pi = datos['punto_inicio']
        pf = datos['punto_fin']
        return cls(
            id=datos.get('id', ''),
            is_id=datos.get('is_id', ''),
            punto_inicio=Punto3D(x=pi['x'], y=pi['y'], z=pi['z']),
            punto_fin=Punto3D(x=pf['x'], y=pf['y'], z=pf['z']),
        )

    def como_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'is_id': self.is_id,
            'punto_inicio': {'x': round(self.punto_inicio.x, 1),
                             'y': round(self.punto_inicio.y, 1),
                             'z': round(self.punto_inicio.z, 1)},
            'punto_fin': {'x': round(self.punto_fin.x, 1),
                          'y': round(self.punto_fin.y, 1),
                          'z': round(self.punto_fin.z, 1)},
        }


# ---------------------------------------------------------------------------
# Soporte de ventilación
# ---------------------------------------------------------------------------

@dataclass
class Soporte:
    """
    Representa un soporte de ventilación.

    Tipos constructivos:
        OMEGA – Soporte estándar que se ancla a dos tubos IS paralelos.
                Subtipo: "Ventilación".  B = 680 mm (fijo).
        ZETA  – Soporte especial que se ancla a un solo tubo IS.
                Subtipo: "VARIFIX".      B = variable.

    Orientación (para JSON de salida):
        "horizontal" → el soporte va en eje X (tubo IS es vertical)
        "vertical"   → el soporte va en eje Y (tubo IS es horizontal)

    Attributes:
        id: Identificador (ej: "SP1")
        tipo: "OMEGA" o "ZETA"
        subtipo: "Ventilación" o "VARIFIX"
        orientacion: "horizontal" o "vertical"
        posicion1: Punto de anclaje 1 (sobre tubo IS, z sobre plano IS)
        posicion2: Punto de anclaje 2
        cota_a: Alto del soporte (110 mm)
        cota_b: Largo del soporte (680 fijo para Omega, variable para Zeta)
        segmento_id: ID del segmento del camino al que pertenece
        is_id: ID del IS asociado (puede ser None si está en margen)
    """
    id: str
    tipo: str
    subtipo: str
    orientacion: str
    posicion1: Punto3D
    posicion2: Punto3D
    cota_a: float
    cota_b: float
    segmento_id: Optional[int] = None
    is_id: Optional[str] = None

    def __repr__(self) -> str:
        return (f"Soporte(id='{self.id}', tipo='{self.tipo}', "
                f"orient='{self.orientacion}', "
                f"B={self.cota_b:.1f}mm, seg={self.segmento_id})")

    def como_dict(self) -> Dict[str, Any]:
        """Serializa para el output JSON."""
        return {
            'tipo': self.orientacion,
            'subtipo': self.subtipo,
            'posicion1': [round(self.posicion1.x, 1),
                          round(self.posicion1.y, 1),
                          round(self.posicion1.z, 1)],
            'posicion2': [round(self.posicion2.x, 1),
                          round(self.posicion2.y, 1),
                          round(self.posicion2.z, 1)],
            'cota_a': self.cota_a,
            'cota_b': round(self.cota_b, 1),
        }
