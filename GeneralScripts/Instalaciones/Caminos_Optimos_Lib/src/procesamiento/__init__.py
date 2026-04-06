"""
Paquete de procesamiento de datos de tuberia.

Contiene el pipeline completo: parseo de entrada, calculo de ruta,
validacion, post-procesamiento IS y construccion de visualizacion.
"""

from .pipeline import procesar_datos
from .geometria_techo import obtener_config_subtipo

__all__ = [
    'procesar_datos',
    'obtener_config_subtipo',
]
