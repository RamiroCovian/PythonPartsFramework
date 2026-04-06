"""
Gestor de configuracion del sistema.

Carga y gestiona las configuraciones desde archivos JSON.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..modelos.tuberia import SubtipoTuberia, DimensionesPerfil


class GestorConfiguracion:
    """
    Gestor central de configuraciones del sistema.
    
    Carga configuraciones desde archivos JSON y proporciona
    acceso unificado a todos los parametros del sistema.
    """
    
    def __init__(self, ruta_config: Optional[str] = None):
        """
        Inicializa el gestor de configuracion.
        
        Args:
            ruta_config: Ruta al directorio de configuracion.
                        Si es None, usa el directorio 'config' del proyecto.
        """
        if ruta_config is None:
            # Buscar directorio config relativo al paquete
            ruta_base = Path(__file__).parent.parent.parent
            self.ruta_config = ruta_base / "config"
        else:
            self.ruta_config = Path(ruta_config)
        
        self._subtipos: Dict[str, SubtipoTuberia] = {}
        self._dimensiones_is: Dict[str, Any] = {}
        self._config_global: Dict[str, Any] = {}
        
        self._cargar_configuraciones()
    
    def _cargar_configuraciones(self) -> None:
        """Carga todas las configuraciones desde archivos JSON."""
        self._cargar_subtipos_ventilacion()
        self._cargar_dimensiones_is()
    
    def _cargar_subtipos_ventilacion(self) -> None:
        """Carga los subtipos de ventilacion desde JSON."""
        ruta = self.ruta_config / "subtipos_ventilacion.json"
        
        if not ruta.exists():
            self._cargar_subtipos_default()
            return
        
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            for clave, info in datos.get('subtipos', {}).items():
                self._subtipos[clave] = SubtipoTuberia.desde_dict(clave, info)
            
            self._config_global.update(datos.get('configuracion_global', {}))
            
        except Exception as e:
            print(f"Error cargando subtipos: {e}")
            self._cargar_subtipos_default()
    
    def _cargar_subtipos_default(self) -> None:
        """Carga subtipos por defecto si no existe archivo."""
        self._subtipos = {
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
                descripcion="Ductos para recuperadores de calor"
            )
        }
    
    def _cargar_dimensiones_is(self) -> None:
        """Carga las dimensiones de IS desde JSON."""
        ruta = self.ruta_config / "dimensiones_is.json"
        
        if not ruta.exists():
            self._dimensiones_is = {
                "ancho_min_mm": 1450,
                "ancho_max_mm": 5650,
                "alto_min_mm": 1450,
                "alto_max_mm": 2150,
                "margen_entre_is_mm": 50
            }
            return
        
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            self._dimensiones_is = datos.get('is_dimensiones', {})
        except Exception as e:
            print(f"Error cargando dimensiones IS: {e}")
    
    def obtener_subtipo(self, clave: str) -> Optional[SubtipoTuberia]:
        """
        Obtiene un subtipo de tuberia por su clave.
        
        Args:
            clave: Clave del subtipo (ej: 'extraccion_impulsion')
        
        Returns:
            SubtipoTuberia o None si no existe
        """
        return self._subtipos.get(clave)
    
    def listar_subtipos(self) -> List[str]:
        """Retorna lista de claves de subtipos disponibles."""
        return list(self._subtipos.keys())
    
    def obtener_todos_subtipos(self) -> Dict[str, SubtipoTuberia]:
        """Retorna diccionario con todos los subtipos."""
        return self._subtipos.copy()
    
    @property
    def dimensiones_is(self) -> Dict[str, Any]:
        """Retorna las dimensiones de IS."""
        return self._dimensiones_is.copy()
    
    @property
    def margen_is_mm(self) -> float:
        """Retorna el margen entre IS en mm."""
        return self._config_global.get('margen_is_mm', 50)
    
    @property
    def tolerancia_geometrica_mm(self) -> float:
        """Retorna la tolerancia geometrica en mm."""
        return self._config_global.get('tolerancia_geometrica_mm', 0.001)
    
    def guardar_subtipos(self, ruta: Optional[str] = None) -> bool:
        """
        Guarda los subtipos actuales a archivo JSON.
        
        Args:
            ruta: Ruta del archivo. Si es None, usa la ruta por defecto.
        
        Returns:
            True si se guardo correctamente
        """
        if ruta is None:
            ruta = self.ruta_config / "subtipos_ventilacion.json"
        
        datos = {
            "subtipos": {
                clave: {
                    "nombre": st.nombre,
                    "dimensiones": {
                        "ancho_mm": st.dimensiones.ancho_mm,
                        "alto_mm": st.dimensiones.alto_mm
                    },
                    "angulos_permitidos": st.angulos_permitidos,
                    "longitud_minima_mm": st.longitud_minima_mm,
                    "margen_seguridad_mm": st.margen_seguridad_mm,
                    "descripcion": st.descripcion
                }
                for clave, st in self._subtipos.items()
            },
            "configuracion_global": self._config_global
        }
        
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando subtipos: {e}")
            return False


# Instancia global (singleton)
_gestor_global: Optional[GestorConfiguracion] = None


def obtener_gestor_configuracion() -> GestorConfiguracion:
    """
    Obtiene la instancia global del gestor de configuracion.
    
    Returns:
        GestorConfiguracion singleton
    """
    global _gestor_global
    if _gestor_global is None:
        _gestor_global = GestorConfiguracion()
    return _gestor_global
