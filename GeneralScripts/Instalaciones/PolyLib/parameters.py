"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONSTANTES DE PARÁMETROS - minimal_polyline.pyp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Archivo centralizado con todas las definiciones de parámetros para minimal_polyline.

Versión: 1.0.0
Basado en: minimal_polyline.pyp
Última actualización: 2025-01-30

ESTRUCTURA:
  1. Constantes individuales (PARAM_*)
  2. Clase ParamNames (agrupación jerárquica)
  3. Clase PointModeValues (valores de modos)
  4. Clase EventIds (IDs de eventos)
  5. Valores por defecto (DEFAULT_*)
  6. Diccionario de validación (ALL_PARAMETERS)

USO:
    # Opción 1: Constantes individuales
    from constants.parameters import PARAM_INSTALLATION_TYPE
    value = build_ele.get_value(PARAM_INSTALLATION_TYPE)

    # Opción 2: Clase agrupada (RECOMENDADO)
    from constants.parameters import ParamNames
    value = build_ele.get_value(ParamNames.Installation.TYPE)

    # Opción 3: Todo junto
    from constants.parameters import ParamNames, EventIds, PointModeValues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ══════════════════════════════════════════════════════════════════════════════════
# 1. CONSTANTES INDIVIDUALES - NOMBRES DE PARÁMETROS XML
# ══════════════════════════════════════════════════════════════════════════════════

# ─────────────────── Información de Instalación ───────────────────
PARAM_INSTALLATION_NAME = "InstallationName"           # Nombre de la instalación
PARAM_SUPPORTED_ANGLES = "SupportedAngles"             # Ángulos soportados (texto informativo)
PARAM_INSTALLATION_TYPE = "InstallationType"           # ComboBox tipo de instalación
PARAM_DIAMETER_TYPE = "DiameterType"
PARAM_DIAMETER_TYPE_STR = "DiameterTypeStr"
PARAM_DIAMETER_MODIFY = "DiameterModify"
PARAM_DISTRIBUTION_TYPE = "DistributionType"
PARAM_WATER_TYPE = "WaterType"
PARAM_FACE_EN ="FaceEN"

# ─────────────────── Modos de Dibujo
PARAM_INFO_BOX = "InfoPicture"
PARAM_POINT_MODE = "PointMode"                         # RadioButtonGroup (valor: 0, 1, 2)
PARAM_EXTEND_POLYLINE = "ExtendPolyline"               # RadioButton modo extender (0)
PARAM_EDIT_POLYLINE = "EditPolyline"                   # RadioButton modo edición (1)
PARAM_CREATE_POLYLINE = "CreatePolyline"               # RadioButton modo creación (2)
PARAM_CHECKBOX_INSERT_POINT = "CheckBoxInsertPoint"
PARAM_CHECKBOX_ADD_CUT = "CheckBoxAddCut"

# ─────────────────── Limitación de Ángulos ───────────────────
PARAM_ROW_LIMITAR_ANGULOS = "RowLimitarAngulos"        # Row contenedor
PARAM_CHECKBOX_LIMITAR_ANGULOS = "CheckBoxLimitarAngulos"  # CheckBox para limitar ángulos
PARAM_ROTATION_ANGLE = "RotationAngle"
PARAM_ROTATION_ANGLE_APPLY = "DefineOrientation"

# ─────────────────── Layers ───────────────────
PARAM_ELEMENT_DESCRIPTION = "ElementDescription"
PARAM_VIEW_INFO = "ViewInfo"
PARAM_LAYER_TYPES = "LayerTypes"                       # ComboBox con tipos de layer
PARAM_APLICAR_LAYERS = "aplicarLayers"                 # Button para aplicar layer

# ─────────────────── Atributos ───────────────────
PARAM_ATTRIBUTE_VALUE = "AttributeValue"               # String con valor del atributo
PARAM_ATTRIBUTE_APPLY = "AttributeApply"               # Button para aplicar atributo

# ─────────────────── Opciones Generales ───────────────────
PARAM_COMMON_PROP = "CommonProp"                      # Propiedades comunes (oculto)
PARAM_CREATE_PYTHON_PART = "CreatePythonPart"         # CheckBox crear PythonPartGroup
PARAM_ADD_POLILYNE = "AddPolilyne"                    # CheckBox agregar polilínea
PARAM_ADD_CUBE = "AddCube"                    # CheckBox agregar cubo en instalacion
PARAM_FUNCTIONAL_NAME = "FunctionalName"      # String con valor para definir nombre pythonpartgroup

# ─────────────────── Acciones/Botones ───────────────────
PARAM_ROW_BORRAR = "RowBorrar"                        # Row de borrar
PARAM_BORRAR_SECCION = "borrarSeccion"                # Button borrar segmento
PARAM_ROW_FINALIZAR = "RowFinalizar"                  # Row de finalizar
PARAM_FINALIZAR_CREACION = "finalizarCreacion"        # Button finalizar y crear

# ─────────────────── Parámetros Ocultos/Internos ───────────────────
PARAM_Z_UNIQUE = "zUnique"                            # Double - Coordenada Z única (oculto)
PARAM_SAVED_STATE = "SavedState"                      # String - Estado serializado JSON (oculto)


# ══════════════════════════════════════════════════════════════════════════════════
# 2. CLASE PARAMNAMES - AGRUPACIÓN JERÁRQUICA (RECOMENDADO PARA USO)
# ══════════════════════════════════════════════════════════════════════════════════

class ParamNames:
    """
    Agrupación jerárquica de nombres de parámetros por categoría.

    Proporciona una forma organizada y autodocumentada de acceder a los nombres
    de parámetros del XML.

    Ventajas:
        - Autocompletado del IDE
        - Organización lógica por funcionalidad
        - Fácil descubrimiento de parámetros disponibles
        - Reduce errores de tipeo

    Ejemplo de uso:
        >>> # Acceder a tipo de instalación
        >>> inst_type = build_ele.get_value(ParamNames.Installation.TYPE)
        >>>
        >>> # Configurar visibilidad
        >>> param_helper.hide_parameter(ParamNames.Angles.CHECKBOX)
        >>>
        >>> # Verificar modo de punto
        >>> if mode == PointModeValues.CREATE:
        >>>     param_helper.show_parameter(ParamNames.DrawMode.CREATE)
    """

    class Installation:
        """
        Parámetros relacionados con la instalación.

        Atributos:
            NAME: Nombre de la instalación
            SUPPORTED_ANGLES: Ángulos soportados (informativo)
            TYPE_TITLE: Título del expander de tipos
            TYPE: Tipo de instalación seleccionado (ComboBox)
        """
        NAME = PARAM_INSTALLATION_NAME
        SUPPORTED_ANGLES = PARAM_SUPPORTED_ANGLES
        INSTALLATION_TYPE = PARAM_INSTALLATION_TYPE
        DIAMETER_TYPE = PARAM_DIAMETER_TYPE
        DIAMETER_TYPE_STR = PARAM_DIAMETER_TYPE_STR
        DIAMETER_MODIFY = PARAM_DIAMETER_MODIFY
        DISTRIBUTION_TYPE = PARAM_DISTRIBUTION_TYPE
        WATER_TYPE = PARAM_WATER_TYPE
        FACE_EN = PARAM_FACE_EN


    class DrawMode:
        """
        Parámetros de modos de dibujo/punto.

        Atributos:
            TITLE: Título del expander de modos
            MODE: Modo actual (RadioButtonGroup: 0=Extender, 1=Edición, 2=Creación)
            EXTEND: RadioButton modo extender
            EDIT: RadioButton modo edición
            CREATE: RadioButton modo creación
        """
        INFO_BOX = PARAM_INFO_BOX
        MODE = PARAM_POINT_MODE
        EXTEND = PARAM_EXTEND_POLYLINE
        EDIT = PARAM_EDIT_POLYLINE
        CREATE = PARAM_CREATE_POLYLINE
        INSERT = PARAM_CHECKBOX_INSERT_POINT
        CUT = PARAM_CHECKBOX_ADD_CUT

    class Angles:
        """
        Parámetros de limitación de ángulos.

        Atributos:
            ROW: Row contenedor
            CHECKBOX: CheckBox para activar/desactivar limitación
        """
        ROW = PARAM_ROW_LIMITAR_ANGULOS
        CHECKBOX = PARAM_CHECKBOX_LIMITAR_ANGULOS
        ROTATION_ANGLE = PARAM_ROTATION_ANGLE
        ROTATION_ANGLE_APPLY = PARAM_ROTATION_ANGLE_APPLY

    class Layers:
        """
        Parámetros de configuración de layers.

        Atributos:
            CUSTOM: Expander de layers
            TYPES: ComboBox con tipos de layer disponibles
            APPLY: Button para aplicar layer seleccionado
        """
        DESCRIPTION = PARAM_ELEMENT_DESCRIPTION
        VIEW_INFO = PARAM_VIEW_INFO
        TYPES = PARAM_LAYER_TYPES
        APPLY = PARAM_APLICAR_LAYERS

    class Attributes:
        """
        Parámetros de atributos personalizados.

        Atributos:
            ROW: Expander de atributos
            VALUE: String con el valor del atributo
            APPLY: Button para aplicar atributo
        """
        VALUE = PARAM_ATTRIBUTE_VALUE
        APPLY = PARAM_ATTRIBUTE_APPLY

    class General:
        """
        Parámetros de opciones generales.

        Atributos:
            EXPANDER: Expander de opciones generales
            COMMON_PROP: Propiedades comunes de Allplan (oculto)
            ROW_PYTHON_PART: Row contenedor de PythonPart
            CREATE_PYTHON_PART: CheckBox para crear como PythonPartGroup
            ROW_POLILYNE: Row contenedor de polilínea
            ADD_POLILYNE: CheckBox para agregar polilínea al grupo
            SEPARATOR: Separador visual
        """
        COMMON_PROP = PARAM_COMMON_PROP
        CREATE_PYTHON_PART = PARAM_CREATE_PYTHON_PART
        ADD_POLILYNE = PARAM_ADD_POLILYNE
        ADD_CUBE = PARAM_ADD_CUBE
        FUNCTIONAL_NAME = PARAM_FUNCTIONAL_NAME

    class Actions:
        """
        Parámetros de acciones/botones.

        Atributos:
            ROW_BORRAR: Row contenedor de borrar
            BORRAR_SECCION: Button para borrar segmento actual
            ROW_FINALIZAR: Row contenedor de finalizar
            FINALIZAR_CREACION: Button para finalizar y crear elementos
        """
        BORRAR_SECCION = PARAM_BORRAR_SECCION
        FINALIZAR_CREACION = PARAM_FINALIZAR_CREACION

    class Hidden:
        """
        Parámetros ocultos/internos del sistema.

        Atributos:
            Z_UNIQUE: Coordenada Z única (Double, oculto)
            SAVED_STATE: Estado serializado JSON para persistencia (String, oculto)
        """
        Z_UNIQUE = PARAM_Z_UNIQUE
        SAVED_STATE = PARAM_SAVED_STATE


# ══════════════════════════════════════════════════════════════════════════════════
# 3. CLASE POINTMODEVALUES - VALORES DE MODOS DE PUNTO
# ══════════════════════════════════════════════════════════════════════════════════

class PointModeValues:
    """
    Valores numéricos de los modos de punto (RadioButtonGroup).

    Estos valores corresponden a los RadioButtons definidos en el XML
    para el parámetro PointMode.

    Uso:
        >>> mode = build_ele.get_value(ParamNames.DrawMode.MODE)
        >>> if mode == PointModeValues.CREATE:
        >>>     print("Modo creación activado")
        >>> elif mode == PointModeValues.EDIT:
        >>>     print("Modo edición activado")
        >>> elif mode == PointModeValues.EXTEND:
        >>>     print("Modo extender activado")
    """
    EXTEND = 0  # Modo extender - ExtendPolyline
    EDIT = 1    # Modo edición - EditPolyline
    CREATE = 2  # Modo creación - CreatePolyline


# ══════════════════════════════════════════════════════════════════════════════════
# 4. CLASE EVENTIDS - IDs DE EVENTOS DE CONTROLES
# ══════════════════════════════════════════════════════════════════════════════════

class EventIds:
    """
    IDs de eventos de controles definidos en el XML.

    Estos IDs se disparan cuando el usuario interactúa con ciertos controles
    (botones, combobox con EventId, etc.)

    Uso:
        >>> def on_control_event(self, event_id):
        >>>     if event_id == EventIds.FINALIZAR_CREACION:
        >>>         self._create_elements()
        >>>         return True
        >>>     elif event_id == EventIds.INSTALLATION_TYPE_CHANGED:
        >>>         self._update_visibility()
        >>>         return True
        >>>     return False
    """
    INSTALLATION_TYPE_CHANGED = 1002  # Cambio en ComboBox de tipo de instalación
    FINALIZAR_CREACION = 1003         # Click en botón "Finalizar - Crear"
    BORRAR_SECCION = 1004             # Click en botón "Borrar Segmento"
    APLICAR_LAYERS = 1009             # Click en botón "Aplicar layer"
    ATTRIBUTE_APPLY = 1011            # Click en botón "Aplicar atributo"

    # --- Marker Manager events (Page 2: macros / defined elements) ---
    SELECT_MACRO_POINT = 1013         # Iniciar captura de punto para macro
    ADD_MACRO_LIBRARY = 1014          # Agregar macro de librería
    SELECT_ELEMENT_POINT = 1015       # Iniciar captura de punto para elemento
    ADD_ELEMENT_POINT = 1016          # Agregar punto de elemento
    ACCEPT_MACRO = 1020               # Aceptar macro (salir de captura)
    ACCEPT_ELEMENT = 1021             # Aceptar elemento (salir de captura)
    SELECT_LOCAL = 1026               # Seleccionar local/story
    CLEAR_LOCAL = 1027                # Limpiar selección de local


# ══════════════════════════════════════════════════════════════════════════════════
# 5. VALORES POR DEFECTO
# ══════════════════════════════════════════════════════════════════════════════════

class DefaultValues:
    """
    Valores por defecto de los parámetros según definición XML.

    Estos valores se pueden usar para resetear parámetros o verificar
    el estado inicial esperado.
    """
    POINT_MODE = 0                    # Modo por defecto: Extender
    CREATE_PYTHON_PART = True         # Crear como PythonPart por defecto
    ADD_POLILYNE = True              # Agregar polilínea por defecto
    LIMITAR_ANGULOS = True           # Limitar ángulos activado por defecto
    Z_UNIQUE = 0.0                   # Coordenada Z inicial

# Constantes individuales para compatibilidad (opcional)
DEFAULT_POINT_MODE = DefaultValues.POINT_MODE
DEFAULT_CREATE_PYTHON_PART = DefaultValues.CREATE_PYTHON_PART
DEFAULT_ADD_POLILYNE = DefaultValues.ADD_POLILYNE
DEFAULT_LIMITAR_ANGULOS = DefaultValues.LIMITAR_ANGULOS
DEFAULT_Z_UNIQUE = DefaultValues.Z_UNIQUE


# ══════════════════════════════════════════════════════════════════════════════════
# 6. DICCIONARIO DE VALIDACIÓN - TODOS LOS PARÁMETROS
# ══════════════════════════════════════════════════════════════════════════════════

ALL_PARAMETERS = {
    # Instalación
    'PARAM_INSTALLATION_NAME': PARAM_INSTALLATION_NAME,
    'PARAM_SUPPORTED_ANGLES': PARAM_SUPPORTED_ANGLES,
    'PARAM_INSTALLATION_TYPE': PARAM_INSTALLATION_TYPE,

    # Modos de dibujo
    # 'PARAM_POINT_MODE_TITLE': PARAM_POINT_MODE_TITLE,
    'PARAM_POINT_MODE': PARAM_POINT_MODE,
    'PARAM_EXTEND_POLYLINE': PARAM_EXTEND_POLYLINE,
    'PARAM_EDIT_POLYLINE': PARAM_EDIT_POLYLINE,
    'PARAM_CREATE_POLYLINE': PARAM_CREATE_POLYLINE,
    'PARAM_CHECKBOX_INSERT_POINT': PARAM_CHECKBOX_INSERT_POINT,

    # Ángulos
    'PARAM_ROW_LIMITAR_ANGULOS': PARAM_ROW_LIMITAR_ANGULOS,
    'PARAM_CHECKBOX_LIMITAR_ANGULOS': PARAM_CHECKBOX_LIMITAR_ANGULOS,

    # Layers
    'PARAM_LAYER_TYPES': PARAM_LAYER_TYPES,
    'PARAM_APLICAR_LAYERS': PARAM_APLICAR_LAYERS,

    # Atributos
    'PARAM_ATTRIBUTE_VALUE': PARAM_ATTRIBUTE_VALUE,
    'PARAM_ATTRIBUTE_APPLY': PARAM_ATTRIBUTE_APPLY,

    # General
    'PARAM_COMMON_PROP': PARAM_COMMON_PROP,
    'PARAM_CREATE_PYTHON_PART': PARAM_CREATE_PYTHON_PART,
    'PARAM_ADD_POLILYNE': PARAM_ADD_POLILYNE,

    # Acciones
    'PARAM_ROW_BORRAR': PARAM_ROW_BORRAR,
    'PARAM_BORRAR_SECCION': PARAM_BORRAR_SECCION,
    'PARAM_ROW_FINALIZAR': PARAM_ROW_FINALIZAR,
    'PARAM_FINALIZAR_CREACION': PARAM_FINALIZAR_CREACION,

    # Ocultos
    'PARAM_Z_UNIQUE': PARAM_Z_UNIQUE,
    'PARAM_SAVED_STATE': PARAM_SAVED_STATE,
}

"""
Diccionario para validación completa.
Uso con validate_parameters() para verificar que todos los parámetros
existen en el build_ele antes de usarlos.
"""


# ══════════════════════════════════════════════════════════════════════════════════
# 7. CONJUNTOS DE PARÁMETROS POR CATEGORÍA (ÚTIL PARA OPERACIONES BATCH)
# ══════════════════════════════════════════════════════════════════════════════════

class ParameterGroups:
    """
    Agrupaciones de parámetros para operaciones batch.

    Útil para ocultar/mostrar/habilitar grupos completos de parámetros.
    """

    # Parámetros que siempre deben estar visibles
    ALWAYS_VISIBLE = [
        PARAM_INSTALLATION_TYPE,
        PARAM_POINT_MODE,
        PARAM_CREATE_PYTHON_PART,
    ]

    # Parámetros que siempre deben estar ocultos
    ALWAYS_HIDDEN = [
        PARAM_Z_UNIQUE,
        PARAM_SAVED_STATE,
        PARAM_COMMON_PROP,
    ]

    # Parámetros específicos para conducto normal/aislado
    CONDUCTO_NORMAL_PARAMS = [
        PARAM_CHECKBOX_LIMITAR_ANGULOS,
    ]

    # Parámetros específicos para conducto recuperador
    CONDUCTO_RECUPERADOR_PARAMS = [
        # Aquí irían parámetros específicos de recuperador si los hay
    ]

    # Parámetros de configuración avanzada
    ADVANCED_PARAMS = [
        PARAM_LAYER_TYPES,
        PARAM_ATTRIBUTE_VALUE,
    ]

    # Todos los botones/acciones
    ACTION_BUTTONS = [
        PARAM_BORRAR_SECCION,
        PARAM_FINALIZAR_CREACION,
        PARAM_APLICAR_LAYERS,
        PARAM_ATTRIBUTE_APPLY,
    ]


# ══════════════════════════════════════════════════════════════════════════════════
# 8. METADATA DEL ARCHIVO
# ══════════════════════════════════════════════════════════════════════════════════
__version__ = "1.0.0"
__date__ = "2025-01-30"
__description__ = "Constantes de parámetros para minimal_polyline.pyp"

# Lista de exportación para imports con *
__all__ = [
    # Clases principales (RECOMENDADO)
    'ParamNames',
    'EventIds',
    'PointModeValues',
    'DefaultValues',
    'ParameterGroups',

    # Constantes individuales (para compatibilidad)
    'PARAM_INSTALLATION_NAME',
    'PARAM_INSTALLATION_TYPE',
    'PARAM_POINT_MODE',
    'PARAM_CREATE_PYTHON_PART',
    'PARAM_CHECKBOX_LIMITAR_ANGULOS',
    'PARAM_ADD_POLILYNE',
    'PARAM_LAYER_TYPES',
    'PARAM_ATTRIBUTE_VALUE',
    'PARAM_SAVED_STATE',
    'PARAM_Z_UNIQUE',

    # Diccionario de validación
    'ALL_PARAMETERS',
]

# ══════════════════════════════════════════════════════════════════════════════════
# FIN DEL ARCHIVO
# ══════════════════════════════════════════════════════════════════════════════════
