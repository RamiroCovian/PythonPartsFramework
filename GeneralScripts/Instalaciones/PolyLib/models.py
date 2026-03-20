from __future__ import annotations

import json
import NemAll_Python_Geometry as AllplanGeo

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict, NamedTuple, Type
from .parameters import ParamNames


# ============= ENUMERACIONES BASE =============
class InstallationCategory(str, Enum):
    """Categorías principales de instalaciones"""
    VENTILATION = "Ventilacion"
    PLUMBING_WATER = "Agua"
    PLUMBING_DRAIN = "Saneamiento"
    ELECTRICAL = "Electrica"
    CLIMATE = "Clima"
    FIRE_PROTECTION = "Proteccion_contra_incendios"
    GAS = "Gas"


class ElementTypes(str, Enum):
    TUBO = "tubo"
    UNION = "union"
    CODO = "codo"
    BIFURCACION = "bifurcacion"
    REDUCION = "reduccion"


class DistributionTypes(str, Enum):
    IS = "IS"
    TD = "TD"
    EN = "EN"

    @classmethod
    def to_value_list(cls) -> str:
        """Formato listo para set_value_list."""
        return "|".join(e.value for e in cls)


class WaterTypes(str, Enum):
    FRED = "Fred"
    CALENT = "Calent"
    RETORN = "Retorn"
    MC_FRED = "MC fred"
    MC_CALENT = "MC calent"

    @classmethod
    def to_value_list(cls, distribution: DistributionTypes | str) -> str:
        """Retorna el ValueList filtrado según el tipo de distribución."""
        members = cls._by_distribution(distribution)
        return "|".join(e.value for e in members)

    @classmethod
    def _by_distribution(cls, distribution: DistributionTypes | str) -> list["WaterTypes"]:
        if distribution == DistributionTypes.TD:
            return [cls.FRED, cls.CALENT]
        return list(cls)


class FacesEN(str, Enum):
    X = "CARA X"
    Y = "CARA Y"

    @classmethod
    def to_value_list(cls) -> str:
        """Formato listo para set_value_list."""
        return "|".join(e.value for e in cls)

# ──────────────────────────────────────────────────────────────────────
#   PARAMETROS POR DEFECTO
# ──────────────────────────────────────────────────────────────────────
@dataclass
class AdditionalParametersBase:
    # ── Instalación ──
    installation_type: bool = True
    diameter_type: bool = False
    diameter_type_str: bool = False
    distribution_type: bool = False
    water_type: bool = False
    face_en: bool = False

    # ── Modo de dibujo ──
    draw_info_box: bool = True
    draw_mode: bool = True
    draw_insert_point: bool = True          # CheckBox "Insertar punto"
    draw_insert_cut: bool = False          # CheckBox "Insertar corte"

    # ── Ángulos ──
    limit_angles: bool = True              # CheckBox limitar ángulos
    rotation_angle: bool = True
    rotation_angle_apply: bool = True

    # ── Layers ──
    elem_desc: bool = False
    info_apply: bool = False
    layer_types: bool = True               # ComboBox tipos de layer
    layer_apply: bool = True               # Button aplicar layer

    # ── Atributos ──
    attribute_value: bool = True           # Input valor atributo
    attribute_apply: bool = True           # Button aplicar atributo

    # ── General ──
    create_python_part: bool = True        # CheckBox crear PythonPartGroup
    add_polilyne: bool = False             # CheckBox agregar polilínea
    add_cube: bool = False             # CheckBox agregar cubo
    functional_name: bool = True

    # ── Acciones ──
    borrar_seccion: bool = True            # Button borrar segmento
    finalizar_creacion: bool = True        # Button finalizar y crear

    # ──────────────────────────────────────────────────────────────
    # Mapeo: campo de este dataclass  →  nombre de parámetro XML
    # ──────────────────────────────────────────────────────────────
    def to_param_map(self) -> dict[str, bool]:
        """Retorna {nombre_XML: valor_habilitado} para cada campo."""
        return {
            ParamNames.Installation.INSTALLATION_TYPE:  self.installation_type,
            ParamNames.Installation.DIAMETER_TYPE:      self.diameter_type,
            ParamNames.Installation.DIAMETER_TYPE_STR:  self.diameter_type_str,
            ParamNames.Installation.DISTRIBUTION_TYPE:  self.distribution_type,
            ParamNames.Installation.WATER_TYPE:         self.water_type,
            ParamNames.Installation.FACE_EN:            self.face_en,
            ParamNames.DrawMode.INFO_BOX:               self.draw_info_box,
            ParamNames.DrawMode.MODE:                   self.draw_mode,
            ParamNames.DrawMode.INSERT:                 self.draw_insert_point,
            ParamNames.DrawMode.CUT:                    self.draw_insert_cut,
            ParamNames.Angles.CHECKBOX:                 self.limit_angles,
            ParamNames.Angles.ROTATION_ANGLE:           self.rotation_angle,
            ParamNames.Angles.ROTATION_ANGLE_APPLY:     self.rotation_angle_apply,
            ParamNames.Layers.DESCRIPTION:              self.elem_desc,
            ParamNames.Layers.VIEW_INFO:                self.info_apply,
            ParamNames.Layers.TYPES:                    self.layer_types,
            ParamNames.Layers.APPLY:                    self.layer_apply,
            ParamNames.Attributes.VALUE:                self.attribute_value,
            ParamNames.Attributes.APPLY:                self.attribute_apply,
            ParamNames.General.CREATE_PYTHON_PART:      self.create_python_part,
            ParamNames.General.ADD_POLILYNE:            self.add_polilyne,
            ParamNames.General.ADD_CUBE:                self.add_cube,
            ParamNames.General.FUNCTIONAL_NAME:         self.functional_name,
            ParamNames.Actions.BORRAR_SECCION:          self.borrar_seccion,
            ParamNames.Actions.FINALIZAR_CREACION:      self.finalizar_creacion,
        }

# ──────────────────────────────────────────────────────────────────────
# Habilitación de parámetros (True = interactúa, False = bloqueado)
# ──────────────────────────────────────────────────────────────────────
@dataclass
class AdditionalParametersEnabled(AdditionalParametersBase):
    """
    Controla qué parámetros son interactivos (editables por el usuario).

    True  → el usuario puede interactuar con el control.
    False → el control se muestra pero está bloqueado/deshabilitado.
    """
    pass

# ──────────────────────────────────────────────────────────────────────
# Visibilidad de parámetros (True = visible, False = oculto)
# ──────────────────────────────────────────────────────────────────────
@dataclass
class AdditionalParametersShow(AdditionalParametersBase):
    """
    Controla qué parámetros se muestran en el panel de propiedades.

    True  → el parámetro (y su row/expander padre) se muestra.
    False → el parámetro se oculta completamente.
    """
    pass


# ══════════════════════════════════════════════════════════════════════
#  PERFIL BASE — agrupa Show + Enabled de una instalación
# ══════════════════════════════════════════════════════════════════════
class InstallationProfile(NamedTuple):
    show:    AdditionalParametersShow
    enabled: AdditionalParametersEnabled


class BaseInstallation:
    """
    Clase base para perfiles de instalación.

    Subclaseá esta clase y sobreescribí Show / Enabled para
    cada tipo de instalación. Luego llamá a .profile() para
    obtener el par (show, enabled) listo para CONFIG.
    """
    class Show(AdditionalParametersShow):
        pass

    class Enabled(AdditionalParametersEnabled):
        pass

    @classmethod
    def profile(cls) -> InstallationProfile:
        return InstallationProfile(
            show=cls.Show(),
            enabled=cls.Enabled(),
        )


# ══════════════════════════════════════════════════════════════════════
#  INSTALACIONES CONCRETAS
# ══════════════════════════════════════════════════════════════════════
class Agua(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        draw_mode_insert: bool = True
        distribution_type: bool = True
        face_en: bool = False
        diameter_type: bool = True
        water_type: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type: bool = True
        water_type: bool = True


class Clima(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        draw_mode_insert: bool = True
        distribution_type: bool = True
        face_en: bool = False
        diameter_type_str: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type_str: bool = True


class Electricidad(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        distribution_type: bool = True
        face_en: bool = False
        draw_insert_point: bool = False
        draw_insert_cut: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = False


class Ventilacion(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        functional_name: bool = True
        draw_insert_point: bool = True
        add_polilyne: bool = True
        rotation_angle: bool = False
        rotation_angle_apply: bool = False

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        add_polilyne: bool = True
        create_python_part: bool = False
        diameter_type: bool = True


class Saneamiento(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        draw_mode_insert: bool = True
        distribution_type: bool = True
        face_en: bool = False
        diameter_type: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type: bool = True


# ══════════════════════════════════════════════════════════════════════
#  REGISTRY  —  string → clase de instalación
# ══════════════════════════════════════════════════════════════════════
_REGISTRY: dict[str, Type[BaseInstallation]] = {
    "AGUA": Agua,
    "CLIMA": Clima,
    "VENTILACION": Ventilacion,
    "ELECTRICIDAD": Electricidad,
    "SANEAMIENTO": Saneamiento,
}

def get_installation_profile(installation: str) -> InstallationProfile:
    key = installation.upper()
    if key not in _REGISTRY:
        raise ValueError(
            f"Instalación desconocida: '{installation}'. "
            f"Disponibles: {', '.join(_REGISTRY)}"
        )
    return _REGISTRY[key].profile()


def register_installation(name: str, cls: Type[BaseInstallation]) -> None:
    """Permite registrar nuevos tipos desde fuera de la librería."""
    _REGISTRY[name.upper()] = cls

# ══════════════════════════════════════════════════════════════════════
# CONFIG BASE
# ══════════════════════════════════════════════════════════════════════
@dataclass
class PolylineBaseConfig:
    """Runtime behavior configuration for polyline interaction.

    Controls interactive behavior flags. Geometry constants (HANDLE_SIZE, etc.)
    should be set directly on the module by installation scripts.
    """
    registry_base_folder: str = "Instalaciones"
    registry_auto_load: bool = True  # Discover installations automatically

    default_installation: Optional[str] = ""
    parameters_show: AdditionalParametersShow = field(default_factory=lambda: AdditionalParametersShow())
    parameters_enabled: AdditionalParametersEnabled = field(default_factory=lambda: AdditionalParametersEnabled())
    num_td_path: Optional[str | None] = None

    limit_angles: bool = False  # Enable angle limiting (snap to predefined increments)
    allowed_angles: Optional[List[float]] = field(default_factory=lambda: [0.0, 45.0, 90.0, -45.0, -90.0])
    min_backtrack_deg: int = 0 # Permite establecer rango de angulos


@dataclass
class PolylineResult:
    """Result returned to the caller after user acceptance."""
    points: List[AllplanGeo.Point3D] = field(default_factory=list)
    is_closed: bool = False


@dataclass
class SegmentData:
    """Datos geométricos completos de un segmento 3D."""

    # ===== PUNTOS =====
    start: AllplanGeo.Point3D
    end: AllplanGeo.Point3D

    # ===== COMPONENTES DEL VECTOR =====
    delta_x: float = 0.0
    delta_y: float = 0.0
    delta_z: float = 0.0

    # ===== LONGITUDES TOTALES =====
    longitud_3d: float = 0.0

    # ===== LONGITUDES POR PLANO =====
    longitud_xy: float = 0.0  # Horizontal (suelo)
    longitud_xz: float = 0.0  # Alzado lateral
    longitud_yz: float = 0.0  # Alzado frontal

    # ===== LONGITUDES POR EJE =====
    longitud_x: float = 0.0
    longitud_y: float = 0.0
    longitud_z: float = 0.0

    # ===== ÁNGULOS HORIZONTALES (Plano XY - cuadrado rojo) =====
    angulo_xy_desde_x: float = 0.0  # Desde +X [-180° a 180°]
    angulo_xy_desde_y: float = 0.0  # Desde +Y [-180° a 180°]
    azimut: float = 0.0              # Desde Norte (horario) [0° a 360°]

    # ===== ÁNGULOS VERTICALES (Plano XZ) =====
    angulo_xz_desde_x: float = 0.0
    angulo_xz_desde_z: float = 0.0
    inclinacion_en_x: float = 0.0

    # ===== ÁNGULOS VERTICALES (Plano YZ) =====
    angulo_yz_desde_y: float = 0.0
    angulo_yz_desde_z: float = 0.0
    inclinacion_en_y: float = 0.0

    # ===== ELEVACIÓN Y PENDIENTE =====
    elevacion: float = 0.0           # [-90° a 90°]
    pendiente_porcentaje: float = 0.0

    # ===== ÁNGULOS DIRECTORES =====
    angulo_con_eje_x: float = 0.0    # [0° a 180°]
    angulo_con_eje_y: float = 0.0
    angulo_con_eje_z: float = 0.0
    coseno_director_x: float = 0.0
    coseno_director_y: float = 0.0
    coseno_director_z: float = 0.0

    # ===== ÁNGULOS ENTRE PROYECCIONES =====
    angulo_xy_xz: float = 0.0
    angulo_xy_yz: float = 0.0
    angulo_xz_yz: float = 0.0

    # ===== CLASIFICACIÓN ESPACIAL =====
    cuadrante_xy: int = 1            # 1-4
    octante: int = 1                 # 1-8
    tipo_segmento: str = "horizontal"  # horizontal/vertical/inclinado

    # ===== SENTIDOS =====
    sentido_x: str = "neutro"
    sentido_y: str = "neutro"
    sentido_z: str = "horizontal"

    # ===== VECTORES =====
    vector: AllplanGeo.Vector3D | None = None
    vector_normalizado: AllplanGeo.Vector3D | None = None

    # ===== COMPATIBILIDAD CON CÓDIGO ANTERIOR =====
    angulo_xy: float = 0.0  # Alias de angulo_xy_desde_x
    angulo_z: float = 0.0   # Alias de elevacion


@dataclass
class SegmentItem:
    """
    Representa un segmento individual de una polilínea con todos sus datos geométricos.
    """
    name: str
    view_mode: str
    data: SegmentData
    info: Optional[SegmentInfo | None] = None

    def as_dict(self, simplified: bool = False) -> Dict[str, Any]:
        """
        Convierte el segmento a diccionario.

        Args:
            simplified: Si es True, solo incluye los datos más comunes.
                       Si es False, incluye todos los datos disponibles.

        Returns:
            Dict con los datos del segmento
        """
        if simplified:
            # Versión simplificada (compatibilidad con código anterior)
            return {
                self.name: {
                    "start": self._point_to_dict(self.data.start),
                    "end": self._point_to_dict(self.data.end),
                    "longitud": round(self.data.longitud_3d, 3),
                    "angulo_xy": round(self.data.angulo_xy_desde_x, 2),
                    "angulo_z": round(self.data.elevacion, 2),
                }
            }

        # Versión completa con todos los datos
        return {
            self.name: {
                # PUNTOS
                "puntos": {
                    "inicio": self._point_to_dict(self.data.start),
                    "fin": self._point_to_dict(self.data.end),
                    "delta": {
                        "x": round(self.data.delta_x, 3),
                        "y": round(self.data.delta_y, 3),
                        "z": round(self.data.delta_z, 3),
                    }
                },

                # LONGITUDES
                "longitudes": {
                    "total_3d": round(self.data.longitud_3d, 3),
                    "planos": {
                        "xy_horizontal": round(self.data.longitud_xy, 3),
                        "xz_alzado_lateral": round(self.data.longitud_xz, 3),
                        "yz_alzado_frontal": round(self.data.longitud_yz, 3),
                    },
                    "ejes": {
                        "x": round(self.data.longitud_x, 3),
                        "y": round(self.data.longitud_y, 3),
                        "z": round(self.data.longitud_z, 3),
                    }
                },

                # ÁNGULOS HORIZONTALES
                "angulos_horizontales": {
                    "desde_eje_x": round(self.data.angulo_xy_desde_x, 2),
                    "desde_eje_y": round(self.data.angulo_xy_desde_y, 2),
                    "azimut": round(self.data.azimut, 2),
                },

                # ÁNGULOS VERTICALES
                "angulos_verticales": {
                    "plano_xz": {
                        "desde_x": round(self.data.angulo_xz_desde_x, 2),
                        "desde_z": round(self.data.angulo_xz_desde_z, 2),
                        "inclinacion": round(self.data.inclinacion_en_x, 2),
                    },
                    "plano_yz": {
                        "desde_y": round(self.data.angulo_yz_desde_y, 2),
                        "desde_z": round(self.data.angulo_yz_desde_z, 2),
                        "inclinacion": round(self.data.inclinacion_en_y, 2),
                    },
                    "elevacion_general": round(self.data.elevacion, 2),
                    "pendiente_porcentaje": round(self.data.pendiente_porcentaje, 2),
                },

                # ÁNGULOS DIRECTORES
                "angulos_directores": {
                    "con_eje_x": round(self.data.angulo_con_eje_x, 2),
                    "con_eje_y": round(self.data.angulo_con_eje_y, 2),
                    "con_eje_z": round(self.data.angulo_con_eje_z, 2),
                    "cosenos": {
                        "x": round(self.data.coseno_director_x, 4),
                        "y": round(self.data.coseno_director_y, 4),
                        "z": round(self.data.coseno_director_z, 4),
                    }
                },

                # CLASIFICACIÓN
                "clasificacion": {
                    "cuadrante_xy": self.data.cuadrante_xy,
                    "octante": self.data.octante,
                    "tipo": self.data.tipo_segmento,
                    "sentidos": {
                        "x": self.data.sentido_x,
                        "y": self.data.sentido_y,
                        "z": self.data.sentido_z,
                    }
                },

                # VECTORES (solo magnitudes, no objetos)
                "vectores": {
                    "direccional": self._vector_to_dict(self.data.vector),
                    "normalizado": self._vector_to_dict(self.data.vector_normalizado),
                }
            }
        }

    def as_dict_legacy(self) -> Dict[str, Any]:
        """
        Versión legacy para compatibilidad con código anterior.
        Equivalente a as_dict(simplified=True).
        """
        return self.as_dict(simplified=True)

    def get_horizontal_angle(self, from_axis: str = "x") -> float:
        """
        Obtiene el ángulo horizontal desde un eje específico.

        Args:
            from_axis: 'x' o 'y'

        Returns:
            Ángulo en grados
        """
        if from_axis.lower() == "x":
            return self.data.angulo_xy_desde_x
        elif from_axis.lower() == "y":
            return self.data.angulo_xy_desde_y
        else:
            raise ValueError(f"Eje '{from_axis}' no válido. Use 'x' o 'y'.")

    def get_vertical_angle(self, plane: str = "general") -> float:
        """
        Obtiene el ángulo vertical desde un plano específico.

        Args:
            plane: 'general', 'xz', o 'yz'

        Returns:
            Ángulo en grados
        """
        plane = plane.lower()
        if plane == "general":
            return self.data.elevacion
        elif plane == "xz":
            return self.data.inclinacion_en_x
        elif plane == "yz":
            return self.data.inclinacion_en_y
        else:
            raise ValueError(f"Plano '{plane}' no válido. Use 'general', 'xz', o 'yz'.")

    def is_horizontal(self, tolerance: float = 5.0) -> bool:
        """Verifica si el segmento es horizontal (dentro de una tolerancia)."""
        return abs(self.data.elevacion) < tolerance

    def is_vertical(self, tolerance: float = 85.0) -> bool:
        """Verifica si el segmento es vertical (dentro de una tolerancia)."""
        return abs(self.data.elevacion) > tolerance

    def is_ascending(self) -> bool:
        """Verifica si el segmento asciende (Z aumenta)."""
        return self.data.delta_z > 0

    def is_descending(self) -> bool:
        """Verifica si el segmento desciende (Z disminuye)."""
        return self.data.delta_z < 0

    def get_quadrant(self) -> int:
        """Retorna el cuadrante en el plano XY (1-4)."""
        return self.data.cuadrante_xy

    def get_octant(self) -> int:
        """Retorna el octante en el espacio 3D (1-8)."""
        return self.data.octante

    def to_json(self, simplified: bool = False, indent: Optional[int] = 2) -> str:
        """
        Convierte el segmento a JSON.

        Args:
            simplified: Si es True, solo incluye los datos más comunes
            indent: Nivel de indentación (None para compacto)

        Returns:
            String JSON
        """
        return json.dumps(self.as_dict(simplified=simplified), indent=indent, ensure_ascii=False)

    def summary(self) -> str:
        """
        Genera un resumen legible del segmento.

        Returns:
            String con resumen del segmento
        """
        return (
            f"Segmento: {self.name}\n"
            f"  Longitud 3D: {self.data.longitud_3d:.3f}\n"
            f"  Azimut: {self.data.azimut:.2f}° (desde Norte)\n"
            f"  Elevación: {self.data.elevacion:.2f}° ({self.data.tipo_segmento})\n"
            f"  Pendiente: {self.data.pendiente_porcentaje:.2f}%\n"
            f"  Cuadrante: {self.data.cuadrante_xy} | Octante: {self.data.octante}\n"
            f"  Desde: ({self.data.start.X:.2f}, {self.data.start.Y:.2f}, {self.data.start.Z:.2f})\n"
            f"  Hasta: ({self.data.end.X:.2f}, {self.data.end.Y:.2f}, {self.data.end.Z:.2f})"
        )

    # def __str__(self) -> str:
    #     """Representación en string (resumen corto)."""
    #     return (
    #         f"{self.name}: L={self.data.longitud_3d:.2f}, "
    #         f"Az={self.data.azimut:.1f}°, Elev={self.data.elevacion:.1f}°"
    #     )

    # def __repr__(self) -> str:
    #     """Representación detallada."""
    #     return f"SegmentItem(name='{self.name}', length={self.data.longitud_3d:.3f})"

    # ===== MÉTODOS AUXILIARES PRIVADOS =====

    @staticmethod
    def _point_to_dict(point: Any) -> Dict[str, float]:
        """Convierte un Point3D a diccionario."""
        if point is None:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        return {
            "x": round(point.X, 3),
            "y": round(point.Y, 3),
            "z": round(point.Z, 3)
        }

    @staticmethod
    def _vector_to_dict(vector: Any) -> Dict[str, float]:
        """Convierte un Vector3D a diccionario."""
        if vector is None:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        return {
            "x": round(vector.X, 4),
            "y": round(vector.Y, 4),
            "z": round(vector.Z, 4)
        }

    # ===== PROPIEDADES DE ACCESO RÁPIDO =====

    @property
    def length(self) -> float:
        """Acceso rápido a la longitud 3D."""
        return self.data.longitud_3d

    @property
    def azimuth(self) -> float:
        """Acceso rápido al azimut."""
        return self.data.azimut

    @property
    def elevation(self) -> float:
        """Acceso rápido a la elevación."""
        return self.data.elevacion

    @property
    def slope_percent(self) -> float:
        """Acceso rápido a la pendiente en porcentaje."""
        return self.data.pendiente_porcentaje

    @staticmethod
    def point_to_dict(pt):
        """Convierte un Point3D a diccionario"""
        return {"X": pt.X, "Y": pt.Y, "Z": pt.Z}

    @staticmethod
    def vector_to_dict(vec):
        """Convierte un Vector3D a diccionario"""
        return {"X": vec.X, "Y": vec.Y, "Z": vec.Z}

    @staticmethod
    def segment_data_to_dict(data):
        """Convierte SegmentData completo a diccionario"""
        return {
            # Puntos principales
            "start": SegmentItem.point_to_dict(data.start),
            "end": SegmentItem.point_to_dict(data.end),

            # Deltas
            "delta_x": data.delta_x,
            "delta_y": data.delta_y,
            "delta_z": data.delta_z,

            # Longitudes
            "longitud_3d": data.longitud_3d,
            "longitud_xy": data.longitud_xy,
            "longitud_xz": data.longitud_xz,
            "longitud_yz": data.longitud_yz,
            "longitud_x": data.longitud_x,
            "longitud_y": data.longitud_y,
            "longitud_z": data.longitud_z,

            # Ángulos desde ejes
            "angulo_xy_desde_x": data.angulo_xy_desde_x,
            "angulo_xy_desde_y": data.angulo_xy_desde_y,
            "azimut": data.azimut,
            "angulo_xz_desde_x": data.angulo_xz_desde_x,
            "angulo_xz_desde_z": data.angulo_xz_desde_z,
            "inclinacion_en_x": data.inclinacion_en_x,
            "angulo_yz_desde_y": data.angulo_yz_desde_y,
            "angulo_yz_desde_z": data.angulo_yz_desde_z,
            "inclinacion_en_y": data.inclinacion_en_y,

            # Elevación y pendiente
            "elevacion": data.elevacion,
            "pendiente_porcentaje": data.pendiente_porcentaje,

            # Ángulos con ejes principales
            "angulo_con_eje_x": data.angulo_con_eje_x,
            "angulo_con_eje_y": data.angulo_con_eje_y,
            "angulo_con_eje_z": data.angulo_con_eje_z,

            # Cosenos directores
            "coseno_director_x": data.coseno_director_x,
            "coseno_director_y": data.coseno_director_y,
            "coseno_director_z": data.coseno_director_z,

            # Ángulos entre planos
            "angulo_xy_xz": data.angulo_xy_xz,
            "angulo_xy_yz": data.angulo_xy_yz,
            "angulo_xz_yz": data.angulo_xz_yz,

            # Clasificación espacial
            "cuadrante_xy": data.cuadrante_xy,
            "octante": data.octante,
            "tipo_segmento": data.tipo_segmento,

            # Sentidos
            "sentido_x": data.sentido_x,
            "sentido_y": data.sentido_y,
            "sentido_z": data.sentido_z,

            # Vectores
            "vector": SegmentItem.vector_to_dict(data.vector),
            "vector_normalizado": SegmentItem.vector_to_dict(data.vector_normalizado),

            # Ángulos principales (simplificados)
            "angulo_xy": data.angulo_xy,
            "angulo_z": data.angulo_z,
        }

    @staticmethod
    def segment_item_to_dict(item):
        """Convierte SegmentItem completo a diccionario"""
        return {
            "name": item.name,
            "view_mode": item.view_mode,
            "data": SegmentItem.segment_data_to_dict(item.data),
            "info": item.info.to_dict() if item.info else None,
        }

    @staticmethod
    def segments_list_to_dict(segments_list):
        """Convierte una lista de SegmentItem a lista de diccionarios"""
        return [SegmentItem.segment_item_to_dict(item) for item in segments_list]


    # ============================================================================
    # FUNCIONES DE DESERIALIZACIÓN (OPCIONAL - Para reconstruir desde JSON)
    # ============================================================================

    @staticmethod
    def dict_to_point(d):
        """Reconstruye Point3D desde diccionario"""
        return AllplanGeo.Point3D(d["X"], d["Y"], d["Z"])

    @staticmethod
    def dict_to_vector(d):
        """Reconstruye Vector3D desde diccionario"""
        return AllplanGeo.Vector3D(d["X"], d["Y"], d["Z"])

    @staticmethod
    def dict_to_segment_data(d):
        """Reconstruye SegmentData desde diccionario"""

        # Asumiendo que tienes una clase SegmentData definida
        return SegmentData(
            start=SegmentItem.dict_to_point(d["start"]),
            end=SegmentItem.dict_to_point(d["end"]),
            delta_x=d["delta_x"],
            delta_y=d["delta_y"],
            delta_z=d["delta_z"],
            longitud_3d=d["longitud_3d"],
            longitud_xy=d["longitud_xy"],
            longitud_xz=d["longitud_xz"],
            longitud_yz=d["longitud_yz"],
            longitud_x=d["longitud_x"],
            longitud_y=d["longitud_y"],
            longitud_z=d["longitud_z"],
            angulo_xy_desde_x=d["angulo_xy_desde_x"],
            angulo_xy_desde_y=d["angulo_xy_desde_y"],
            azimut=d["azimut"],
            angulo_xz_desde_x=d["angulo_xz_desde_x"],
            angulo_xz_desde_z=d["angulo_xz_desde_z"],
            inclinacion_en_x=d["inclinacion_en_x"],
            angulo_yz_desde_y=d["angulo_yz_desde_y"],
            angulo_yz_desde_z=d["angulo_yz_desde_z"],
            inclinacion_en_y=d["inclinacion_en_y"],
            elevacion=d["elevacion"],
            pendiente_porcentaje=d["pendiente_porcentaje"],
            angulo_con_eje_x=d["angulo_con_eje_x"],
            angulo_con_eje_y=d["angulo_con_eje_y"],
            angulo_con_eje_z=d["angulo_con_eje_z"],
            coseno_director_x=d["coseno_director_x"],
            coseno_director_y=d["coseno_director_y"],
            coseno_director_z=d["coseno_director_z"],
            angulo_xy_xz=d["angulo_xy_xz"],
            angulo_xy_yz=d["angulo_xy_yz"],
            angulo_xz_yz=d["angulo_xz_yz"],
            cuadrante_xy=d["cuadrante_xy"],
            octante=d["octante"],
            tipo_segmento=d["tipo_segmento"],
            sentido_x=d["sentido_x"],
            sentido_y=d["sentido_y"],
            sentido_z=d["sentido_z"],
            vector=SegmentItem.dict_to_vector(d["vector"]),
            vector_normalizado=SegmentItem.dict_to_vector(d["vector_normalizado"]),
            angulo_xy=d["angulo_xy"],
            angulo_z=d["angulo_z"]
        )

    @staticmethod
    def dict_to_segment_item(d):
        """Reconstruye SegmentItem desde diccionario"""
        return SegmentItem(
            name=d["name"],
            view_mode=d["view_mode"],
            data=SegmentItem.dict_to_segment_data(d["data"]),
            info=SegmentInfo.from_dict(d["info"]) if d.get("info") else None
        )


@dataclass
class SegmentInfo:
    """Representa un segmento de la instalación con su metadata técnica."""
    diameter: Any # int | float | list[int|float]
    section_type:  str = ""
    system: str = ""
    label: str = ""
    distribution_type: Optional[str] = None
    water_type: Optional[str] = None
    face: Optional[Any]  = None
    view_mode: Optional[str] = None

    @property
    def is_multi_diameter(self) -> bool:
        return isinstance(self.diameter, list)

    @property
    def diameter_in(self) -> float:
        return self.diameter[0] if self.is_multi_diameter else self.diameter

    @property
    def diameter_out(self) -> float:
        return self.diameter[-1] if self.is_multi_diameter else self.diameter

    def to_dict(self) -> dict:
        return {
            "diameter":          self.diameter,
            "section_type":      self.section_type,
            "system":            self.system,
            "label":             self.label,
            "distribution_type": self.distribution_type if self.distribution_type is not None else "",
            "face":              self.face if self.face is not None else "",
            "view_mode":          self.view_mode if self.view_mode is not None else "",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SegmentInfo":
        return cls(
            diameter=          data.get("diameter", 0),
            section_type=      data.get("section_type", ""),
            system=            data.get("system", ""),
            label=             data.get("label", ""),
            distribution_type= data.get("distribution_type", "") or None,
            face=              data.get("face", "") or None,
            view_mode=         data.get("view_mode", "")
        )

@dataclass
class InstallationElement:
    """
    Representa un componente real de la instalación con su data técnica,
    geometría y ubicación dentro de la red.
    """
    type: str                          # 'tubo', 'codo', 'union', 'bifurcacion', 'reducer'
    key: List                          # Identificador único para el interactor
    geometry: Any
    position: AllplanGeo.Point3D       # Punto de inserción o inicio
    layer: str                         # Layer Name
    path_idx: int                      # Índice de la trayectoria a la que pertenece
    seg_idx: int                       # Índice del segmento dentro de esa trayectoria
    params: Dict[str, Any] = field(default_factory=dict)  # Metadata adicional
    attribute: Optional[str] = None
    # --- Campos exclusivos de reductores (None para el resto de elementos) ---
    diameter_in: Optional[float] = None   # Diámetro del segmento entrante (mm)
    diameter_out: Optional[float] = None  # Diámetro del segmento saliente (mm)
    reducer_type: Optional[str] = None    # Ej: "D40-D110"

    def get_info(self) -> str:
        """Devuelve un resumen rápido del elemento."""
        if self.type == ElementTypes.REDUCION.value and self.reducer_type:
            return (f"Reductor {self.reducer_type} "
                    f"(Path: {self.path_idx}, Seg: {self.seg_idx})")
        return f"Elemento {self.type} (Path: {self.path_idx}, Seg: {self.seg_idx})"

    def to_dict(self) -> Dict[str, Any]:
        """Opcional: Para mantener compatibilidad con código antiguo"""
        return self.__dict__

@dataclass
class AppliedLayer:
    """Información de un layer aplicado a un elemento del path."""
    layer: str
    type: str
    path_idx: int
    elem_idx: int
    layer_idx: int

    @property
    def storage_key(self) -> str:
        """Genera la clave de almacenamiento para este layer."""
        return f"seg_{self.path_idx}_elem_{self.layer_idx}"

    def to_dict(self) -> dict:
        """Convierte la dataclass a diccionario."""
        return {
            "layer": self.layer,
            "type": self.type,
            "path_idx": self.path_idx,
            "elem_idx": self.elem_idx,
            "layer_idx": self.layer_idx
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppliedLayer':
        """Crea una instancia desde un diccionario."""
        return cls(
            layer=data["layer"],
            type=data["type"],
            path_idx=data["path_idx"],
            elem_idx=data["elem_idx"],
            layer_idx=data["layer_idx"]
        )


@dataclass
class GeneratedElement:
    """
    Representa un elemento generado y su metadata asociada.
    """
    element: Any  # Aquí podrías poner el tipo específico del objeto 3D si lo tienes
    index: int
    element_type: str

    # Opcional: __slots__ reduce el uso de memoria y acelera el acceso
    __slots__ = ['element', 'index', 'element_type']
