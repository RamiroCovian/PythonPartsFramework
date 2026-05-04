from __future__ import annotations

import json
import NemAll_Python_Geometry as AllplanGeo

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Any, Dict, NamedTuple, Type, Tuple
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


class SoporteEditModeValues(int, Enum):
    """Valores del RadioButtonGroup SoporteEditMode."""
    DISABLED = 0   # Sin edición — clicks pasan al flujo normal de polilínea
    EDIT     = 1   # Edición — seleccionar, borrar, aplicar atributos
    MOVE     = 2   # Edición Mover — pick-and-place como insertar soporte


class TypeSupportTypes(str, Enum):
    """Tipos de soporte disponibles en el combo TypeSupport."""
    CINTA = "Cinta"
    OMEGA = "Omega"
    ZETA  = "Zeta"

    @classmethod
    def to_value_list(cls) -> str:
        """Formato listo para ctrl_prop_util.set_value_list."""
        return "|".join(e.value for e in cls)


# ─────────────────────────────────────────────────────────────────────────────
# Enum subtipo_tuberia → Caminos_Optimos_Lib
# ─────────────────────────────────────────────────────────────────────────────
class SubtipoConducto(str, Enum):
    """Mapea el nombre de instalación mostrado en la paleta al valor
    ``subtipo_tuberia`` que espera ``Caminos_Optimos_Lib``."""

    EXTRACCION_IMPULSION = "extraccion_impulsion"
    AISLADO              = "aislado"
    RECUPERADOR          = "recuperador"

    @classmethod
    def from_tipo_instalacion(cls, tipo: str) -> "SubtipoConducto":
        """Convierte ``selected_inst_type`` (nombre de paleta) al subtipo físico.

        Conducto Impulsion  → extraccion_impulsion
        Conducto Extraccion → extraccion_impulsion  (mismo subtipo físico)
        Conducto Aislado    → aislado
        Conducto Recuperador→ recuperador
        Cualquier otro valor → extraccion_impulsion (fallback)
        """
        _map: Dict[str, "SubtipoConducto"] = {
            "conducto impulsion":   cls.EXTRACCION_IMPULSION,
            "conducto extraccion":  cls.EXTRACCION_IMPULSION,
            "conducto aislado":     cls.AISLADO,
            "conducto recuperador": cls.RECUPERADOR,
            # variantes sin "conducto"
            "impulsion":            cls.EXTRACCION_IMPULSION,
            "extraccion":           cls.EXTRACCION_IMPULSION,
            "aislado":              cls.AISLADO,
            "recuperador":          cls.RECUPERADOR,
        }
        key = str(tipo or "").strip().lower()
        return _map.get(key, cls.EXTRACCION_IMPULSION)


# ─────────────────────────────────────────────────────────────────────────────
# Enum de roles → tipos del optimizador
# ─────────────────────────────────────────────────────────────────────────────
class OptimizerRole(str, Enum):
    """Roles de nodo en el pipeline del optimizador.

    El valor de cada miembro es el tipo que espera ``Caminos_Optimos_Lib``.
    Labels de paleta (StringComboBox ``TipoPuntoOrden``):
        ``Inicial|Paso(Libre)|Bifurcacion(Obligado)|Final``
    Al heredar de ``str`` puede usarse directamente donde se espera string.

    Conversión desde label de paleta::

        role = OptimizerRole.from_label("Inicio")   # → OptimizerRole.INICIO
        tipo = role.value                            # → "inicio"
    """
    INICIO              = "inicio"
    FINAL               = "fin"
    BIFURCACION         = "orden_obligatorio"
    PASO                = "orden_libre"


    @classmethod
    def from_label(cls, label: str) -> "OptimizerRole":
        """Convierte un label de paleta (StringComboBox ``TipoPuntoOrden``) al Enum correspondiente.

        Labels válidos: ``Inicial``, ``Paso(Libre)``, ``Bifurcacion(Obligado)``, ``Final``.
        Cualquier valor desconocido devuelve ``INICIO``.
        """
        # Normalizar: minúsculas, sin paréntesis ni espacios extra
        raw = str(label or "").strip()
        # key = raw.lower().replace("(", "").replace(")", "").replace(" ", "_")
        _map: Dict[str, "OptimizerRole"] = {
            # Normalizados (minúsculas, sin paréntesis)
            "Inicial":           cls.INICIO,
            "Final":             cls.FINAL,
            "Bifurcacion_Obligado": cls.BIFURCACION,
            "Paso_Libre":        cls.PASO,
            # Variantes sueltas
            "inicio":            cls.INICIO,
            "fin":               cls.FINAL,
            "orden_obligatorio": cls.BIFURCACION,
            "orden_libre":       cls.PASO,
        }
        role = _map.get(label, None)
        if role is None:
            print(f"[OptimizerRole] from_label: label desconocido '{raw}' → INICIO")
        return role or cls.INICIO


@dataclass
class OptimizerNode:
    """Nodo en el input del optimizador (formato ``Caminos_Optimos_Lib``).

    Corresponde a un elemento de ``caminos[].nodos[]`` en el JSON de entrada.
    """
    id:          str
    tipo:        str                         # valor de OptimizerRole
    coordenadas: Dict[str, float]            # {"x": float, "y": float, "z": float}
    anteriores:  List[str] = field(default_factory=list)
    siguientes:  List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":          self.id,
            "tipo":        self.tipo,
            "coordenadas": self.coordenadas,
            "anteriores":  list(self.anteriores),
            "siguientes":  list(self.siguientes),
        }


@dataclass
class UndefinedPoint:
    """Punto colocado por el usuario en modo ``punto_input_mode``.

    Se almacena en ``script_object.undefined_points_list`` y luego se
    convierte a :class:`OptimizerNode` vía :meth:`to_optimizer_node`.
    """
    id:             str
    tipo:           OptimizerRole            # rol del nodo (Enum)
    coordenadas:    Dict[str, float]         # {"x": float, "y": float, "z": float}
    path_key:       str                      # clave de camino (por color_id)
    color_id:       int                      # ID de color Allplan (1-7)
    common_node_id: Optional[str] = None    # CP-N si es punto de cruce
    inst_type:      str = ""               # tipo de instalación del camino
    anteriores:     List[str] = field(default_factory=list)
    siguientes:     List[str] = field(default_factory=list)

    def to_optimizer_node(self) -> OptimizerNode:
        """Convierte al formato de nodo del optimizador."""
        return OptimizerNode(
            id          = self.id,
            tipo        = self.tipo.value,
            coordenadas = dict(self.coordenadas),
            anteriores  = list(self.anteriores),
            siguientes  = list(self.siguientes),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a dict plano para JSON."""
        return {
            "id":             self.id,
            "tipo":           self.tipo.value,
            "coordenadas":    dict(self.coordenadas),
            "path_key":       self.path_key,
            "color_id":       self.color_id,
            "common_node_id": self.common_node_id,
            "inst_type":      self.inst_type,
            "anteriores":     list(self.anteriores),
            "siguientes":     list(self.siguientes),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UndefinedPoint":
        """Reconstruye desde un dict generado por :meth:`to_dict`."""
        return cls(
            id             = d["id"],
            tipo           = OptimizerRole(d["tipo"]),
            coordenadas    = dict(d["coordenadas"]),
            path_key       = d.get("path_key", ""),
            color_id       = int(d.get("color_id", 1)),
            common_node_id = d.get("common_node_id"),
            inst_type      = d.get("inst_type", ""),
            anteriores     = list(d.get("anteriores", [])),
            siguientes     = list(d.get("siguientes", [])),
        )


@dataclass
class SoporteEntry:
    """
    Soporte acumulado, pendiente de inserción en el documento Allplan.
    Combina los campos tipados de SupportJson con datos de sesión
    (key único, Point3D canónicos, atributos Allplan).
    """
    # ── Identidad ────────────────────────────────────────────────────
    key: int                            # ID único secuencial (1, 2, 3…)

    # ── Campos del contrato JSON (de SupportJson) ─────────────────────
    tipo: str                           # "Omega" | "Zeta" | "Cinta"
    subtipo: str                        # "Ventilación", "Clima", "Varifix", …
    superficie: str                     # "Liso" | "Perforado"
    cota_a: float                       # cota A (altura vertical)
    cota_b: float                       # cota B (longitud cinta / variante)
    pos1: Any                           # Point3D — posicion1 canónica
    pos2: Any                           # Point3D — posicion2 canónica
    angulo_inclinacion: float = 0.0     # inclinación extra alrededor del eje

    # ── Campos extra (variante Omega / Zeta / SEP / Varifix) ─────────
    extra: dict = field(default_factory=dict)   # omega_variante, zeta_variante, tipo_instalacion, …

    # ── Atributos Allplan ─────────────────────────────────────────────
    attributes: dict = field(default_factory=dict)  # {"6_CC_IS": "val", …}

    # ─────────────────────────────────────────────────────────────────
    # Serialización
    # ─────────────────────────────────────────────────────────────────
    def as_dict(self) -> dict:
        """
        Serializa a dict plano compatible con el contrato JSON de SupportJson.
        pos1/pos2 se toman de los campos Point3D (fuente canónica) para
        garantizar consistencia tras operaciones de move.
        """
        d: dict = {
            "tipo":               self.tipo,
            "subtipo":            self.subtipo,
            "superficie":         self.superficie,
            "posicion1":          [self.pos1.X, self.pos1.Y, self.pos1.Z],
            "posicion2":          [self.pos2.X, self.pos2.Y, self.pos2.Z],
            "cota_a":             self.cota_a,
            "cota_b":             self.cota_b,
            "angulo_inclinacion": self.angulo_inclinacion,
            "attributes":         dict(self.attributes),
        }
        d.update(self.extra)    # omega_variante, zeta_variante, tipo_instalacion, …
        return d

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serializa a JSON string."""
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=indent)

    # ─────────────────────────────────────────────────────────────────
    # Construcción
    # ─────────────────────────────────────────────────────────────────
    _CORE_KEYS = frozenset({
        "tipo", "subtipo", "superficie",
        "posicion1", "posicion2",
        "cota_a", "cota_b", "angulo_inclinacion",
        "attributes",
    })

    @staticmethod
    def from_dict(d: dict, key: int) -> "SoporteEntry":
        """Reconstruye SoporteEntry desde un dict generado por as_dict() o from_palette."""
        p1r = d.get("posicion1", [0.0, 0.0, 0.0])
        p2r = d.get("posicion2", [1000.0, 0.0, 0.0])
        pos1 = AllplanGeo.Point3D(float(p1r[0]), float(p1r[1]), float(p1r[2]))
        pos2 = AllplanGeo.Point3D(float(p2r[0]), float(p2r[1]), float(p2r[2]))
        extra = {k: v for k, v in d.items() if k not in SoporteEntry._CORE_KEYS}
        return SoporteEntry(
            key=key,
            tipo=str(d.get("tipo", "")),
            subtipo=str(d.get("subtipo", "")),
            superficie=str(d.get("superficie", "")),
            cota_a=float(d.get("cota_a", 0.0) or 0.0),
            cota_b=float(d.get("cota_b", 0.0) or 0.0),
            pos1=pos1,
            pos2=pos2,
            angulo_inclinacion=float(d.get("angulo_inclinacion", 0.0) or 0.0),
            extra=extra,
            attributes=d.get("attributes", {}),
        )

    @staticmethod
    def from_support_json(sj: "SupportJson", key: int,
                          pos1: Any = None, pos2: Any = None) -> "SoporteEntry":
        """Construye un SoporteEntry desde un SupportJson (flujo lectura JSON externo)."""
        if pos1 is None:
            p1 = sj.posicion1
            pos1 = AllplanGeo.Point3D(float(p1[0]), float(p1[1]), float(p1[2]))
        if pos2 is None:
            p2 = sj.posicion2
            pos2 = AllplanGeo.Point3D(float(p2[0]), float(p2[1]), float(p2[2]))
        return SoporteEntry(
            key=key,
            tipo=sj.tipo,
            subtipo=sj.subtipo,
            superficie=sj.superficie,
            cota_a=sj.cota_a,
            cota_b=sj.cota_b,
            pos1=pos1,
            pos2=pos2,
            angulo_inclinacion=float(sj.angulo_inclinacion or 0.0),
        )


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
    diameter_modify: bool = False
    distribution_type: bool = False
    water_type: bool = False
    face_en: bool = False

    # ── Modo polilinea ──
    poly_mode: bool = True

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

    # ── Soportes (página separada) ──
    type_support: bool = True             # ComboBox Zeta/Omega
    type_support_zeta: bool = False        # ComboBox variante Zeta
    type_support_omega: bool = False       # ComboBox variante Omega
    type_installation_sep: bool = False    # ComboBox instalación Electr./Clima(SEP)
    type_installation_varifix: bool = False  # ComboBox instalación Varifix
    subtipo_soporte: bool = True          # ComboBox subtipo semántico
    superficie: bool = True              # ComboBox Liso/Perforado
    cota_a: bool = True                  # Double cota_a
    cota_b: bool = True                  # Double cota_b
    angulo_inclinacion: bool = True      # Angle angulo_inclinacion
    # Posición 1 (posicion1 del mock JSON)
    pos1_x: bool = True                  # Double X inicio
    pos1_y: bool = True                  # Double Y inicio
    pos1_z: bool = True                  # Double Z inicio
    # Posición 2 (posicion2 del mock JSON)
    pos2_x: bool = True                  # Double X fin
    pos2_y: bool = True                  # Double Y fin
    pos2_z: bool = True                  # Double Z fin
    # Botones de acción de soportes
    insertar_soporte: bool = True        # Button entra en modo inserción
    crear_soportes: bool = True          # Button acumula soporte en lista

    borrar_soportes: bool = True        # Button borra seleccionados
    # Modo de edición (RadioButtonGroup 0=Desactivado, 1=Edición, 2=Edición Mover)
    soporte_edit_mode: bool = True       # RadioButtonGroup SoporteEditMode
    soporte_attr_value: bool = True      # Input valor atributo soporte
    aplicar_attr_soporte: bool = True   # Button aplica atributo a seleccionados
    soporte_count: bool = True          # Text solo lectura — contador

    # ──────────────────────────────────────────────────────────────
    # Mapeo: campo de este dataclass  →  nombre de parámetro XML
    # ──────────────────────────────────────────────────────────────
    def to_param_map(self) -> dict[str, bool]:
        """Retorna {nombre_XML: valor_habilitado} para cada campo."""
        return {
            ParamNames.Installation.INSTALLATION_TYPE:  self.installation_type,
            ParamNames.Installation.DIAMETER_TYPE:      self.diameter_type,
            ParamNames.Installation.DIAMETER_TYPE_STR:  self.diameter_type_str,
            ParamNames.Installation.DIAMETER_MODIFY:    self.diameter_modify,
            ParamNames.Installation.DISTRIBUTION_TYPE:  self.distribution_type,
            ParamNames.Installation.WATER_TYPE:         self.water_type,
            ParamNames.Installation.FACE_EN:            self.face_en,
            ParamNames.PolyMode.MODE:                   self.poly_mode,
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
            # Soportes — tipo/variante
            ParamNames.Supports.TYPE_SUPPORT:               self.type_support,
            ParamNames.Supports.TYPE_SUPPORT_ZETA:          self.type_support_zeta,
            ParamNames.Supports.TYPE_SUPPORT_OMEGA:         self.type_support_omega,
            ParamNames.Supports.TYPE_INSTALLATION_SEP:      self.type_installation_sep,
            ParamNames.Supports.TYPE_INSTALLATION_VARIFIX:  self.type_installation_varifix,
            ParamNames.Supports.SUBTIPO_SOPORTE:            self.subtipo_soporte,
            ParamNames.Supports.SUPERFICIE:                 self.superficie,
            # Soportes — dimensiones
            ParamNames.Supports.COTA_A:                     self.cota_a,
            ParamNames.Supports.COTA_B:                     self.cota_b,
            ParamNames.Supports.ANGULO_INCLINACION:         self.angulo_inclinacion,
            # Soportes — botones de acción
            ParamNames.Supports.INSERTAR_SOPORTE:           self.insertar_soporte,
            ParamNames.Supports.CREAR_SOPORTES:             self.crear_soportes,
            ParamNames.Supports.BORRAR_SOPORTES:            self.borrar_soportes,
            # Soportes — modo edición (RadioButtonGroup) + atributos
            ParamNames.Supports.EDIT_MODE:                  self.soporte_edit_mode,
            ParamNames.Supports.ATTR_VALUE:                 self.soporte_attr_value,
            ParamNames.Supports.APLICAR_ATTR:               self.aplicar_attr_soporte,
            ParamNames.Supports.COUNT:                      self.soporte_count,
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


# ──────────────────────────────────────────────────────────────────────
# Support json file template
# ──────────────────────────────────────────────────────────────────────
@dataclass
class SupportJson:
    """
    Representa un soporte leído desde JSON externo.

    Contrato JSON oficial (consumido por optimización):
    - raíz: `soportes` (lista)
    - por soporte:
      - `tipo` (obligatorio): "Omega" | "Zeta"
      - `subtipo` (obligatorio): valores semánticos (ej.: "Ventilación", "Clima",
        "Electricidad", "Agua", "Saneamiento", "Varifix")
      - `superficie` (obligatorio): "Liso" | "Perforado"
      - `posicion1` (obligatorio): [x, y, z]
      - `posicion2` (obligatorio): [x, y, z]
      - `cota_a` (obligatorio): cota A
      - `cota_b` (obligatorio): cota B
      - `angulo_inclinacion` (opcional): inclinación extra alrededor del eje del soporte

    Nota de implementación:
    - Internamente se usan nombres canónicos en español para mantener consistencia
      de punta a punta (JSON -> dataclass -> Soportes.py).
    - Se mantiene compatibilidad temporal con claves antiguas (`supports`, `type`, `subtype`,
      `position1`, `position2`, `height_a`, `length_b`,
      `inclination_angle_deg`, `inclination_angel_deg`).
    """

    tipo: str
    subtipo: str
    superficie: str
    posicion1: Tuple[float, float, float]
    posicion2: Tuple[float, float, float]
    angulo_inclinacion: Optional[float] = None
    cota_a: float = 0.0
    cota_b: float = 0.0


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
        diameter_modify: bool = True
        water_type: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type: bool = True
        diameter_modify: bool = True
        water_type: bool = True


class Clima(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        draw_mode_insert: bool = True
        distribution_type: bool = True
        face_en: bool = False
        diameter_type_str: bool = True
        diameter_modify: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type_str: bool = True
        diameter_modify: bool = True


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
        # diameter_modify: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        add_polilyne: bool = True
        create_python_part: bool = False
        diameter_type: bool = True
        diameter_modify: bool = True


class Saneamiento(BaseInstallation):

    @dataclass
    class Show(AdditionalParametersShow):
        draw_mode_insert: bool = True
        distribution_type: bool = True
        face_en: bool = False
        diameter_type: bool = True
        diameter_modify: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        functional_name: bool = True
        distribution_type: bool = True
        face_en: bool = True
        create_python_part: bool = True
        diameter_type: bool = True
        diameter_modify: bool = True


class Soportes(BaseInstallation):
    """
    Perfil de instalación para soportes estructurales (Zeta / Omega).

    La geometría la maneja SupportModel (soportes.py) a partir de los
    parámetros de la página 'PageSoportes' del .pyp de instalación.
    Los campos de posicion1/posicion2 los aporta la polilínea; el resto
    (tipo, subtipo, superficie, cotas, ángulo) vienen de esta página.
    """

    @dataclass
    class Show(AdditionalParametersShow):
        # Soportes: TODOS siempre visibles — no hay visibilidad dinámica.
        type_support: bool = True
        type_support_zeta: bool = True
        type_support_omega: bool = True
        type_installation_sep: bool = True
        type_installation_varifix: bool = True
        subtipo_soporte: bool = True
        superficie: bool = True
        cota_a: bool = True
        cota_b: bool = True
        angulo_inclinacion: bool = True
        # Botones de acción
        insertar_soporte: bool = True
        crear_soportes: bool = True
        insertar_en_plano: bool = True
        borrar_soportes: bool = True
        # Modo edición + atributos
        soporte_edit_mode: bool = True
        soporte_attr_value: bool = True
        aplicar_attr_soporte: bool = True
        soporte_count: bool = True

    @dataclass
    class Enabled(AdditionalParametersEnabled):
        # Tipo / variante
        type_support: bool = True
        type_support_zeta: bool = True
        type_support_omega: bool = True
        type_installation_sep: bool = True
        type_installation_varifix: bool = True
        subtipo_soporte: bool = True
        superficie: bool = True
        # Dimensiones
        cota_a: bool = True
        cota_b: bool = True
        angulo_inclinacion: bool = True
        # Botones (borrar/insertar en plano deshabilitados cuando lista vacía)
        insertar_soporte: bool = True
        crear_soportes: bool = True

        borrar_soportes: bool = False     # se habilita cuando hay selección
        # Modo de edición (RadioButtonGroup) + atributos
        soporte_edit_mode: bool = True
        soporte_attr_value: bool = True
        aplicar_attr_soporte: bool = False  # se habilita cuando hay selección
        soporte_count: bool = False          # solo lectura — siempre deshabilitado


# ══════════════════════════════════════════════════════════════════════
#  REGISTRY  —  string → clase de instalación
# ══════════════════════════════════════════════════════════════════════
_REGISTRY: dict[str, Type[BaseInstallation]] = {
    "AGUA": Agua,
    "CLIMA": Clima,
    "VENTILACION": Ventilacion,
    "ELECTRICIDAD": Electricidad,
    "SANEAMIENTO": Saneamiento,
    "SOPORTES": Soportes,
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

    # Opt-in marker manager: factory(script_object, build_ele) -> MarkerManager
    marker_manager_factory: Optional[Callable] = None


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
            "water_type":        self.water_type if self.water_type is not None else "",
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
            water_type=        data.get("water_type", "") or None,
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


# ──────────────────────────────────────────────────────────────────────
# Modelo: cambio de tipo de instalación a nivel de camino (path)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class PathInstTypeChange:
    """Representa una operación de cambio de tipo de instalación sobre un camino completo.

    Se crea antes de aplicar el cambio para poder mostrar un diálogo de confirmación
    y para registrar el estado anterior si fuese necesario.

    Atributos:
        path_idx:       Índice del camino en ``active_paths`` / ``saved_paths``.
        old_type:       Etiqueta de tipo de instalación anterior (puede ser vacía si no estaba asignada).
        new_type:       Etiqueta de tipo de instalación nueva (valor de ``InstallationType`` en paleta).
        segments_count: Número de segmentos afectados en el camino.
    """
    path_idx:       int
    old_type:       str
    new_type:       str
    segments_count: int = 0

    def summary(self) -> str:
        """Texto legible para diálogos de confirmación."""
        old = self.old_type or "(sin tipo)"
        return (
            f"Camino {self.path_idx}  ({self.segments_count} segmento(s))\n"
            f"Tipo anterior : {old}\n"
            f"Nuevo tipo    : {self.new_type}"
        )
