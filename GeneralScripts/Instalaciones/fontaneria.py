# -*- coding: utf-8 -*-
"""Script de creacion de Polilineas"""

from __future__ import annotations
from typing import List, Optional, Tuple, Set
import traceback
import math
import time
import inspect
import os
import importlib.util
import hashlib
import random
import builtins
import json


from PythonPart import View2D3D, PythonPart, PythonPartGroup
from PythonPartUtil import PythonPartUtil

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as PythonUtility
from NemAll_Python_BaseElements import LayerService
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter


from BaseScriptObject import BaseScriptObject
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult

# Módulo ElementosDefinidos: eventos 1015–1018, paleta, preview, serialización y creación

from ElementosDefinidos import (
    CallbackDefinedElement,
    get_defined_element_settings as ed_get_defined_element_settings,
    get_free_point_type_flag as ed_get_tipo_punto_libre_flag,
    get_free_point_selection_tolerance as ed_get_free_point_selection_tolerance,
    get_elementos_para_instalacion,
    find_hover_free_point,
    detect_common_user_points_between_paths as ed_detect_common_points_between_paths,
    create_point_marker_geometry,
    draw_marker_for_element_type,
    make_circle_polyline_for_marker,
    serialize_element_markers as ed_serialize_element_markers,
    deserialize_element_markers as ed_deserialize_element_markers,
    serialize_free_placed_points as ed_serialize_free_placed_points,
    deserialize_free_placed_points as ed_deserialize_free_placed_points,
    create_elements_from_free_placed_points as ed_create_elements_from_free_placed_points,
)
from ElementosDefinidos.handlers import (
    start_element_point_capture as ed_start_element_point_capture,
    handle_element_point_capture_click as ed_handle_element_point_capture_click,
    add_defined_element_marker as ed_add_defined_element_marker,
    add_intermediate_element_at_point as ed_add_intermediate_element_at_point,
    on_anadir_punto_libre as ed_on_anadir_punto_libre,
    on_finalizar_puntos_libres as ed_on_finalizar_puntos_libres,
    handle_click_add_free_point as ed_handle_click_add_free_point,
    apply_free_point_rotation_to_palette as ed_apply_free_point_rotation_to_palette,
    update_free_point_rotation_from_palette as ed_update_free_point_rotation_from_palette,
)

# ═══════════════════════════════════════════════════════════════════════════════
#                              CONTROL DE DEBUG
# ═══════════════════════════════════════════════════════════════════════════════

DEBUG = True  # Cambia a False si no quieres ver mensajes de debug en consola
_real_print = builtins.print


def debug(*args, **kwargs):
    """Función de debug condicional"""
    if DEBUG:
        _real_print(*args, **kwargs)


# Caché de estado de polilínea por build_ele (cuando Allplan recrea el script object tras 1015/1016)
_polyline_state_cache = {}


# ═══════════════════════════════════════════════════════════════════════════════
#                    FUNCIONES AUXILIARES - ATRIBUTOS
# ═══════════════════════════════════════════════════════════════════════════════


class _SimpleValueWrapper:
    """
    Wrapper genérico para valores simples con atributo .value
    Reemplaza múltiples clases específicas (TipoTuboAttr, TipoColzeAttr, etc.)
    """

    def __init__(self, value):
        self.value = value


def _save_attr_state(obj, attr_name):
    """Guarda el estado actual de un atributo de objeto"""
    exists = hasattr(obj, attr_name)
    if not exists:
        return {"exists": False}
    attr = getattr(obj, attr_name)
    has_value = hasattr(attr, "value")
    orig_val = getattr(attr, "value", attr)
    return {"exists": True, "has_value": has_value, "value": orig_val}


def _set_attr_value(obj, attr_name, new_value):
    """Establece el valor de un atributo, creando el wrapper si es necesario"""
    if hasattr(obj, attr_name):
        attr = getattr(obj, attr_name)
        if hasattr(attr, "value"):
            attr.value = new_value
        else:
            setattr(obj, attr_name, new_value)
    else:
        setattr(obj, attr_name, _SimpleValueWrapper(new_value))


def _restore_attr_state(obj, attr_name, state):
    """Restaura el estado guardado de un atributo"""
    if not state or not state.get("exists"):
        return
    if hasattr(obj, attr_name):
        attr = getattr(obj, attr_name)
        if state.get("has_value") and hasattr(attr, "value"):
            attr.value = state["value"]
        else:
            setattr(obj, attr_name, state["value"])


def call_with_build_ele_attrs(build_ele, set_attrs: dict, create_func, *args, **kwargs):
    """
    Setea atributos temporalmente en build_ele, llama a una función y restaura.

    Args:
        build_ele: Objeto de parámetros
        set_attrs: Diccionario {nombre_atributo: valor_temporal}
        create_func: Función a llamar (ej: create_elbow_element)
        *args, **kwargs: Argumentos para create_func (sin build_ele)

    Returns:
        Resultado de create_func(build_ele, *args, **kwargs)
    """
    states = {name: _save_attr_state(build_ele, name) for name in set_attrs.keys()}
    try:
        for name, value in set_attrs.items():
            _set_attr_value(build_ele, name, value)
        return create_func(build_ele, *args, **kwargs)
    finally:
        for name, state in states.items():
            _restore_attr_state(build_ele, name, state)


def _detect_distribution_from_element(elem) -> str:
    """
    Intenta detectar el tipo de distribución (IS o TD) desde un elemento.
    Por defecto retorna "IS" si no se puede determinar.

    Args:
        elem: Elemento de Allplan

    Returns:
        "IS" o "TD"
    """
    try:
        # Intentar detectar desde el nombre del modelo o propiedades
        # Los modelos TD suelen tener "TD" en su nombre o usar modelos específicos
        # Por ahora, usamos "IS" por defecto ya que es el más común
        # TODO: Implementar detección más precisa si es necesario
        return "IS"
    except Exception:
        return "IS"


def _has_material_cavitat(elem, doc) -> bool:
    """
    Verifica si un elemento tiene el atributo "Material" con valor "CAVITAT".
    Estos elementos (típicamente elementos "outer" en TD) no deben recibir
    numeración absoluta ni atributos padre.

    Args:
        elem: Elemento de Allplan
        doc: Documento de Allplan

    Returns:
        True si el elemento tiene "Material" = "CAVITAT", False en caso contrario
    """
    if not elem or not doc:
        return False

    try:
        # Obtener ID del atributo "Material"
        material_attr_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "Material"
        )
        if not material_attr_id or material_attr_id <= 0:
            return False

        # Leer atributos del elemento
        attrs = elem.GetAttributes()
        if not attrs:
            return False

        attr_sets = list(attrs.GetAttributeSets() or [])
        for attr_set in attr_sets:
            attr_list = list(attr_set.GetAttributes() or [])
            for a in attr_list:
                if a.Id == material_attr_id:
                    # Verificar si el valor es "CAVITAT"
                    if (
                        hasattr(a, "Value")
                        and str(a.Value).strip().upper() == "CAVITAT"
                    ):
                        return True
        return False
    except Exception as e:
        debug(f"[ATTR] Error verificando atributo Material: {e}")
        return False


def _set_pmp_pare(elem, custom_attrs: dict, doc) -> None:
    """
    Modifica SOLO el atributo pmp_pare de un elemento.
    Mantiene todos los demás atributos tal cual estaban.

    Args:
        elem: Elemento al que aplicar el atributo
        custom_attrs: Diccionario con el valor del atributo
        doc: Documento de Allplan
    """
    if not custom_attrs or not doc or elem is None:
        return

    # No aplicar atributos a elementos con Material = "CAVITAT"
    if _has_material_cavitat(elem, doc):
        debug(
            "[ATTR] Elemento con Material=CAVITAT detectado, omitiendo aplicación de pmp_pare"
        )
        return

    # Tomar el primer valor no vacío del diccionario
    try:
        attr_value = next(
            v for v in custom_attrs.values() if isinstance(v, str) and v.strip()
        )
    except StopIteration:
        return

    # Obtener ID del atributo pmp_pare
    try:
        attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "pmp_pare"
        )
    except Exception as e:
        debug(f"[ATTR] Error obteniendo ID 'pmp_pare': {e}")
        attr_pmp_pare_id = None

    if not attr_pmp_pare_id:
        debug("[ATTR] No se pudo obtener ID para pmp_pare")
        return

    # Leer atributos existentes del elemento
    attrs = elem.GetAttributes()
    if not attrs:
        # Si no tiene atributos, creamos un set nuevo SOLO con pmp_pare
        attr_list = []
        if attr_pmp_pare_id and attr_pmp_pare_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )

        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
        return

    # Tiene atributos: trabajamos sobre los sets existentes
    attr_sets = list(attrs.GetAttributeSets() or [])
    found_pare = False

    for attr_set in attr_sets:
        attr_list = list(attr_set.GetAttributes() or [])
        for a in attr_list:
            if attr_pmp_pare_id and a.Id == attr_pmp_pare_id:
                a.Value = attr_value
                found_pare = True
        attr_set.SetAttributes(attr_list)

    # Si no existía, lo agregamos al primer set
    if attr_sets:
        first_set = attr_sets[0]
        attr_list = list(first_set.GetAttributes() or [])

        if attr_pmp_pare_id and attr_pmp_pare_id > 0 and not found_pare:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )

        first_set.SetAttributes(attr_list)
    else:
        # Por si viniera un container raro sin sets
        attr_list = []
        if attr_pmp_pare_id and attr_pmp_pare_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )
        if attr_list:
            attr_sets = [AllplanBaseElements.AttributeSet(attr_list)]

    attrs.SetAttributeSets(attr_sets)
    elem.SetAttributes(attrs)


def _set_6_cc_is_y_pmp_pare_en_elemento(
    elem, custom_attrs: dict, doc, distribution_type: str = None
) -> None:
    """
    Modifica los atributos 6_CC_IS y pmp_pare de un elemento.
    Aplica AMBOS atributos (solo para elementos IS).

    Mantiene todos los demás atributos tal cual estaban.

    Args:
        elem: Elemento al que aplicar los atributos
        custom_attrs: Diccionario con los valores de atributos
        doc: Documento de Allplan
        distribution_type: Tipo de distribución ("IS" o "TD"). Si es None, intenta detectarlo desde el elemento.
    """
    if not custom_attrs or not doc or elem is None:
        return

    # No aplicar atributos a elementos con Material = "CAVITAT"
    if _has_material_cavitat(elem, doc):
        debug(
            "[ATTR] Elemento con Material=CAVITAT detectado, omitiendo aplicación de 6_CC_IS y pmp_pare"
        )
        return

    # Si no se proporciona distribution_type, intentar detectarlo
    if distribution_type is None:
        distribution_type = _detect_distribution_from_element(elem)

    # Tomar el primer valor no vacío del diccionario
    try:
        attr_value = next(
            v for v in custom_attrs.values() if isinstance(v, str) and v.strip()
        )
    except StopIteration:
        return

    # Este método siempre aplica ambos atributos (solo se usa para IS)
    # Obtener IDs de ambos atributos
    attr_6_cc_is_id = None
    try:
        attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "6_CC_IS"
        )
    except Exception as e:
        debug(f"[ATTR] Error obteniendo ID '6_CC_IS': {e}")
        attr_6_cc_is_id = None

    attr_pmp_pare_id = None
    try:
        attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "pmp_pare"
        )
    except Exception as e:
        debug(f"[ATTR] Error obteniendo ID 'pmp_pare': {e}")
        attr_pmp_pare_id = None

    if not attr_6_cc_is_id and not attr_pmp_pare_id:
        debug("[ATTR] Ningún ID válido para 6_CC_IS / pmp_pare")
        return

    # Leer atributos existentes del elemento
    attrs = elem.GetAttributes()
    if not attrs:
        # Si no tiene atributos, creamos un set nuevo SOLO con estos dos
        attr_list = []
        if attr_6_cc_is_id and attr_6_cc_is_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_6_cc_is_id, attr_value)
            )
        if attr_pmp_pare_id and attr_pmp_pare_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )

        if attr_list:
            attr_set = AllplanBaseElements.AttributeSet(attr_list)
            elem.SetAttributes(AllplanBaseElements.Attributes([attr_set]))
        return

    # Tiene atributos: trabajamos sobre los sets existentes
    attr_sets = list(attrs.GetAttributeSets() or [])
    found_6 = False
    found_pare = False

    for attr_set in attr_sets:
        attr_list = list(attr_set.GetAttributes() or [])
        for a in attr_list:
            if attr_6_cc_is_id and a.Id == attr_6_cc_is_id:
                # Solo cambiamos el valor
                a.Value = attr_value
                found_6 = True
            elif attr_pmp_pare_id and a.Id == attr_pmp_pare_id:
                a.Value = attr_value
                found_pare = True
        attr_set.SetAttributes(attr_list)

    # Si no existían, los agregamos al primer set
    if attr_sets:
        first_set = attr_sets[0]
        attr_list = list(first_set.GetAttributes() or [])

        if attr_6_cc_is_id and attr_6_cc_is_id > 0 and not found_6:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_6_cc_is_id, attr_value)
            )
        if attr_pmp_pare_id and attr_pmp_pare_id > 0 and not found_pare:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )

        first_set.SetAttributes(attr_list)
    else:
        # Por si viniera un container raro sin sets
        attr_list = []
        if attr_6_cc_is_id and attr_6_cc_is_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_6_cc_is_id, attr_value)
            )
        if attr_pmp_pare_id and attr_pmp_pare_id > 0:
            attr_list.append(
                AllplanBaseElements.AttributeString(attr_pmp_pare_id, attr_value)
            )
        if attr_list:
            attr_sets = [AllplanBaseElements.AttributeSet(attr_list)]

    attrs.SetAttributeSets(attr_sets)
    elem.SetAttributes(attrs)


def _get_pmp_pare_value_from_elem(elem, doc) -> Optional[str]:
    """
    Devuelve el valor del atributo pmp_pare de un elemento o None si no existe.
    """
    if elem is None or doc is None:
        return None

    try:
        attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "pmp_pare"
        )
    except Exception as e:
        debug(f"[ATTR] Error obteniendo ID 'pmp_pare' al leer valor: {e}")
        return None

    if not attr_pmp_pare_id:
        return None

    if not hasattr(elem, "GetAttributes"):
        return None

    try:
        attrs = elem.GetAttributes()
        if not attrs or not hasattr(attrs, "GetAttributeSets"):
            return None

        attr_sets = attrs.GetAttributeSets() or []
        for attr_set in attr_sets:
            if not hasattr(attr_set, "GetAttributes"):
                continue
            for a in attr_set.GetAttributes() or []:
                attr_id = getattr(a, "Id", None)
                if attr_id != attr_pmp_pare_id:
                    continue

                val = getattr(a, "Value", None)
                if val is None and hasattr(a, "value"):
                    val = getattr(a, "value")

                if val is None:
                    continue

                s = str(val).strip()
                if s:
                    return s
    except Exception as ex:
        debug(f"[ATTR] Error leyendo valor de 'pmp_pare': {ex}")

    return None


def _set_attr_padre(
    elem, custom_attrs: dict, doc, distribution_type: str = None
) -> None:
    """
    Método handle que aplica los atributos padre según el tipo de distribución.
    - Si distribución es TD: aplica solo pmp_pare usando _set_pmp_pare
    - Si distribución es IS: aplica ambos (6_CC_IS y pmp_pare) usando _set_6_cc_is_y_pmp_pare_en_elemento

    Args:
        elem: Elemento al que aplicar los atributos
        custom_attrs: Diccionario con los valores de atributos
        doc: Documento de Allplan
        distribution_type: Tipo de distribución ("IS" o "TD"). Si es None, intenta detectarlo desde el elemento.
    """
    if not custom_attrs or not doc or elem is None:
        return

    # Si no se proporciona distribution_type, intentar detectarlo
    if distribution_type is None:
        distribution_type = _detect_distribution_from_element(elem)

    # Decidir qué método usar según la distribución
    if distribution_type == "TD":
        # TD: solo pmp_pare
        _set_pmp_pare(elem, custom_attrs, doc)
    else:
        # IS (o cualquier otro): ambos atributos
        _set_6_cc_is_y_pmp_pare_en_elemento(elem, custom_attrs, doc, distribution_type)


def _dir_from_delta(dx, dy, eps=1e-6):
    """
    Devuelve 'E', 'N', 'W', 'S' según el signo de dx,dy.
    Suponemos tramos ortogonales (solo X o solo Y).
    """
    if abs(dx) > abs(dy):
        # horizontal
        return "E" if dx > 0 else "W"
    else:
        # vertical
        return "N" if dy > 0 else "S"


# ===== Config =====

# Sizes and Tolerances
DRAG_SCALE = 1.5
HANDLE_SIZE = 90.0  # mm
HIT_TOL_SEGMENT = 80.0  # mm (captura de segmentos en 3D)
HIT_TOL_VIEW = 20.0  # unidades de vista (pantalla) para hit-test 2D; permite clic en verticales en cualquier vista
HIT_TOL_VERTEX = 30.0  # mm (captura de puntos)
HOVER_SCALE = 1.25
MAX_PERP_DIST_MM = 20.0  # Ajusta este valor según preferencia
MIN_INSERT_OFFSET_MM = 2.0  # distancia mínima a extremos para insertar
MIN_SEG_LEN_MM = 1.0  # evitar segmentos casi nulos

# Colors
# ID estándar Allplan para atributo personalizado 01 (Custom attribute 01)
ATTR_PERSO_01_ID = 1083

BRANCH_ANCHOR_COLOR = 7  # 7 = magenta (preview de anclaje para bifurcar)
BOX_SELECTED_SEG_COLOR = 9  # 9 = marrón
HANDLE_COLOR_IDX = 2  # 2 = amarillo (puntos)
INSERT_PREVIEW_COLOR = 6  # cian para el punto fantasma
MIDPOINT_COLOR = 4  # color neutro para marcadores de punto medio
PREVIEW_SAVED_COLOR = 3  # 3 = verde (polilíneas guardadas en preview únicamente)
RECT_COLOR = 8
SEGMENT_HOVER_COLOR = 1  # 1 = rojo (segmento bajo mouse)
SEGMENT_SEL_COLOR = 5  # 5 = azul (segmento seleccionado)
SELECTED_VERTEX_COLOR = 5

# Midpoints (visual)
MIDPOINT_HIT_TOL = 12.0  # mm
MIDPOINT_PEN = 13  # trazo gordo para que se vean
MIDPOINT_SIZE_FACTOR = 0.90  # tamaño relativo al HANDLE_SIZE
MIDPOINT_Z_BIAS = 1.0  # mm

# Overlay para segmentos resaltados (evitar z-fighting y mejorar visibilidad)
SEGMENT_OVERLAY_PEN = 13  # trazo más gordo para que se note
SEGMENT_OVERLAY_Z_BIAS = 1.0  # mm: levanta el tramo resaltado sobre la poly base

# Selection by Box
RECT_PEN = 12

# ═══════════════════════════════════════════════════════════════════════════════
#                     Configuración de Numeración
# ═══════════════════════════════════════════════════════════════════════════════

# IMPORTANTE: Solo se numeran TUBOS (elementos de longitud variable)
# Codos, reductores y bifurcaciones NO se numeran
# La numeración es persistente por proyecto en carpetas separadas
# Formato: NumTD\{ProjectName}\NumTD_Tubo_{diameter}mm.txt

# Rutas de numeración: se determina automáticamente la ruta base desde la ubicación del script
# Solo necesitas configurar el subdirectorio relativo al script
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_NUMBERING_BASE_PATH = os.path.dirname(
    _SCRIPT_DIR
)  # Directorio padre del script (PythonPartsScripts)

NUMTD_SUBPATH = r"Agua\NumTD"
NUMIS_SUBPATH = r"Agua\NumIS"

# Diccionario para almacenar los números durante la sesión
# { "Tubo_20mm": {"used": set(), "next": 1}, ... }
numbering_by_type = {}

# ═══════════════════════════════════════════════════════════════════════════════
#       Config recortes de tubos según elemento de unión (manguito, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

# Manguito entre Ø20 y Ø25 → recortar 14.5 mm en cada tubo
MANGUITO_TRIM_BY_DIAM = {
    (20, 20): 14.5,
    (25, 25): 17.0,
    (20, 25): 14.5,
    (25, 20): 14.5,
}

ELBOW_TRIM_BY_DIAM = {
    20: 27.0,
    25: 34.5,
    # 32: ... (cuando exista)
}

# Longitud máxima permitida para un segmento de tubo (en mm)
# Si un segmento excede esta longitud, se divide automáticamente en múltiples segmentos
# intercalando manguitos entre ellos
MAX_SEGMENT_LENGTH = 5000.0  # 5 metros = 5000mm (valor por defecto/legacy)

# Longitudes máximas por tipo de tubo (en mm)
# Cada tipo de tubo tiene su propia longitud máxima permitida
MAX_SEGMENT_LENGTH_BY_TUBE_TYPE = {
    # TD (Terreno/Vertical)
    ("TD", "Polietilè"): 5000.0,  # 5 metros
    ("TD", "Multicapa"): 5000.0,  # 5 metros (ajustar si es diferente)
    ("TD", "Armaflex"): 5000.0,  # 3 metros (ajustar según especificaciones)
    # IS (Interior/Superficie)
    ("IS", "Polietilè"): 5000.0,  # 5 metros
    # Agregar más tipos IS cuando se implementen
}

# trims por TE en mm (main_in, main_out, branch)
# IMPORTANTE: el orden del main es "los dos tramos colineales" y branch es la rama
TE_TRIMS = {
    (20, 20, 20): (27.0, 27.0, 27.0),
    (25, 25, 25): (34.5, 34.5, 34.5),
    # mixtas
    (25, 20, 20): (32.0, 32.0, 27.0),  # main_in=25, branch=20, main_out=20
    (25, 25, 20): (34.5, 32.0, 32.0),  # main_in=25, branch=25, main_out=20
    (25, 20, 25): (
        32.0,
        30.0,
        32.0,
    ),  # main_in=25, branch=20, main_out=25 (TØ25-20-25, type_te=3)
}

# ═══════════════════════════════════════════════════════════════════════════════
#                     Helpers para crear PythonPartsGroups
# ═══════════════════════════════════════════════════════════════════════════════


def create_element_hash(element_type: str, **params) -> str:
    """Hash único (SHA224) para evitar caché de Allplan."""
    random_number = random.randint(10**15, 10**16 - 1)
    param_items = sorted(params.items())
    param_string = f"{element_type}_random{random_number}_" + "_".join(
        f"{k}={v}" for k, v in param_items
    )
    hash_val = hashlib.sha224(param_string.encode("utf-8")).hexdigest()
    return hash_val


def create_params_list_from_dict(params: dict):
    """
    Convierte dict a lista de strings, que es lo que pide PythonPartGroup.
    Formato: "key = value\n" para compatibilidad con PythonPartService.GetParameter()
    """
    return [f"{key} = {value}\n" for key, value in sorted(params.items())]


def create_individual_pythonparts_from_elements(elems, build_ele):
    """
    Crea un PythonPart por cada ModelElement3D (misma idea que Saneamiento).
    Extrae los atributos de cada elemento y los pasa a la PythonPart.
    """
    pythonparts_list = []

    # Obtener el nombre del archivo .pyp desde build_ele
    python_file_name = (
        build_ele.pyp_file_name if hasattr(build_ele, "pyp_file_name") else ""
    )

    for idx, elem in enumerate(elems):
        try:
            # 1. EXTRAER CommonProperties del elemento
            common_props = (
                AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            )
            try:
                # El ModelElement3D ya tiene CommonProperties asignados
                if hasattr(elem, "GetCommonProperties"):
                    elem_props = elem.GetCommonProperties()
                    if elem_props is not None:
                        common_props = elem_props
            except Exception:
                pass

            # 2. EXTRAER atributos del elemento (ya fueron asignados previamente)
            attribute_list = []
            try:
                if hasattr(elem, "GetAttributes"):
                    attrs = elem.GetAttributes()
                    if attrs and hasattr(attrs, "GetAttributeSets"):
                        attr_sets = attrs.GetAttributeSets()
                        if attr_sets and len(attr_sets) > 0:
                            # Extraer AttributeString individuales del primer set
                            for attr_set in attr_sets:
                                if hasattr(attr_set, "GetAttributes"):
                                    attribute_list = list(attr_set.GetAttributes())
                                    break
            except Exception as e:
                debug(
                    f"[SO] Advertencia: No se pudieron extraer atributos del elemento {idx}: {e}"
                )

            # 3. CREAR VIEWS con el ModelElement3D
            views = [View2D3D([elem])]
            matrix = AllplanGeo.Matrix3D()

            # 4. CREAR parámetros únicos para este elemento
            params = {
                "Index": idx,
                "NomIS": (
                    getattr(build_ele, "NomIS", None).value
                    if hasattr(build_ele, "NomIS")
                    else ""
                ),
            }

            # 5. GENERAR hash único
            hash_val = create_element_hash("PP_IS_Element", **params)

            # 6. CREAR lista de parámetros
            param_list = create_params_list_from_dict(params)

            # 7. OBTENER nombre descriptivo basado en atributos (ID 1083 = Atributo Personalizado 01)
            element_name = f"PP_IS_Element_{idx}"
            try:
                for attr in attribute_list:
                    # Intentar diferentes formas de obtener el ID del atributo
                    attr_id = None
                    if hasattr(attr, "Id"):
                        attr_id = attr.Id
                    elif hasattr(attr, "GetAttributeID"):
                        attr_id = attr.GetAttributeID()
                    elif hasattr(attr, "attribute_id"):
                        attr_id = attr.attribute_id

                    # ID 1083 = "Atributo personalizado 01"
                    if attr_id == 1083:
                        if hasattr(attr, "Value") and attr.Value:
                            element_name = str(attr.Value).replace(" ", "_")[:50]
                            break
                        elif hasattr(attr, "value") and attr.value:
                            element_name = str(attr.value).replace(" ", "_")[:50]
                            break
            except Exception:
                pass

            # 8. CREAR PythonPart individual con la firma completa
            # Incluir attribute_list para que los atributos se preserven en la PythonPart
            pythonpart = PythonPart(
                element_name,  # name
                parameter_list=param_list,  # parameter_list
                hash_value=hash_val,  # hash_value
                python_file=python_file_name,  # python_file (nombre del .pyp)
                views=views,  # views (View2D3D con ModelElement3D)
                matrix=matrix,  # matrix
                common_props=common_props,  # common_props
                attribute_list=(
                    attribute_list if attribute_list else None
                ),  # attribute_list
            )

            pythonparts_list.append(pythonpart)

        except Exception as e:
            debug(f"[SO] Error creando PythonPart para elemento {idx}: {e}")
            import traceback

            traceback.print_exc()
            continue

    return pythonparts_list


# Helper para importación local con fallback al sistema
def _import_local_module(module_name: str, *class_names):
    """
    Importa módulo desde directorio local con fallback al sistema.
    Args:
        module_name: Nombre del archivo sin extensión (ej: 'Tub_PVC_TricapaV_005')
        *class_names: Nombres de clases/funciones a extraer del módulo
    Returns:
        tuple: Valores importados en el mismo orden que class_names (None si falla)
    """
    current_dir = os.path.dirname(__file__)
    td_path = os.path.join(current_dir, "TD", "pyp-scripts", f"{module_name}.py")
    is_path = os.path.join(current_dir, "IS", "pyp-scripts", f"{module_name}.py")

    try:
        if os.path.exists(td_path):
            spec = importlib.util.spec_from_file_location(
                f"{module_name}_td_local", td_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"[SO] Importado {module_name} desde subcarpeta TD: {td_path}")
        elif os.path.exists(is_path):
            spec = importlib.util.spec_from_file_location(
                f"{module_name}_is_local", is_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"[SO] Importado {module_name} desde subcarpeta IS: {is_path}")
        else:
            module = __import__(module_name, fromlist=class_names)
            print(f"[SO] Usando {module_name} del sistema")
        return tuple(getattr(module, name, None) for name in class_names)
    except Exception as e:
        print(f"[SO] Error importando {module_name}: {e} : PATH {is_path}")
        return tuple(None for _ in class_names)


# Importar módulos de AGUA IS (horizontales)
(TubPolietileModel,) = _import_local_module("Tub_Polietile_007_IS", "TubPolietileModel")
(ColzeModel,) = _import_local_module("Colze_001_IS", "ColzeModel")
(ManguitoModel,) = _import_local_module("Manguito_005_IS", "ManguitoModel")
(TeModel,) = _import_local_module("Te_003_IS", "TeModel")

# Importar módulos de TD (terreno/verticales)
(ColzeTDModel,) = _import_local_module("Colze_001", "ColzeTDModel")
(TeTDModel,) = _import_local_module("Te_003", "TeTDModel")
(ManguitoTDModel,) = _import_local_module("Manguito_005", "ManguitoTDModel")
(TubPolietileTDModel,) = _import_local_module(
    "Tub_Polietile_007", "TubPolietileTDModel"
)
(TubMulticapaTDModel,) = _import_local_module(
    "Tub_Multicapa_008", "TubMulticapaTDModel"
)
(ArmaflexModel,) = _import_local_module("Armaflex_009", "ArmaflexModel")

# Elementos definidos en polilínea (TD Agua)
(ColzeBaseCreateElement,) = _import_local_module("Colze_Base_002", "create_element")
(TeSortidaCreateElement,) = _import_local_module("Te_Sortida_004", "create_element")
(ClauDePasCreateElement,) = _import_local_module("Clau_de_Pas_006", "create_element")
(TapsCreateElement,) = _import_local_module("Taps_010", "create_element")

# Registro de elementos definidos Agua (BaseDefinedElement): preview y 3D vía generate_preview / generate_final_3d
_CREATE_ELEMENT_BY_KEY = {
    "colze_base": ColzeBaseCreateElement,
    "t_sortida": TeSortidaCreateElement,
    "clau_de_pas": ClauDePasCreateElement,
    "taps": TapsCreateElement,
}
_agua_defined_elements = {}
for _info in get_elementos_para_instalacion("AGUA"):
    _key = _info["key"]
    _create_fn = _CREATE_ELEMENT_BY_KEY.get(_key)
    if _create_fn is not None:
        _agua_defined_elements[_key] = CallbackDefinedElement(
            nombre=_info["label"],
            callback_geometria=_create_fn,
            posibles_funciones=_info.get("posibles_funciones"),
            funcion_defecto=_info.get("funcion_defecto"),
        )


# ===== Obligatorios =====
def check_allplan_version(_build_ele, _version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return PolylineScriptObject(build_ele, script_object_data)


# ===== Script Object =====
class PolylineScriptObject(BaseScriptObject):
    # ═══════════════════════════════════════════════════════════════════════════════
    #                     Helpers para Numeracion Absoluta
    # ═══════════════════════════════════════════════════════════════════════════════

    def _get_project_name(self):
        try:
            doc = self.coord_input.GetInputViewDocument()
            project = doc.GetProject()
            return project.name if hasattr(project, "name") else "ProyectoDesconocido"
        except Exception:
            return "ProyectoDesconocido"

    def _get_numbering_file_path(self, element_type, distribution_type="IS"):
        """
        Devuelve la ruta completa del archivo de numeración para un tipo de elemento.
        Estructura:
        - TD: {BASE_PATH} / NUMTD_SUBPATH / {ProjectName} / NumTD_{element_type}.txt
        - IS: {BASE_PATH} / NUMIS_SUBPATH / {ProjectName} / NumIS_{element_type}.txt
        La ruta base se determina automáticamente desde la ubicación del script.
        """
        try:
            project_name = self._get_project_name()

            if distribution_type == "TD":
                sub_path = NUMTD_SUBPATH
                prefix = "NumTD"
            else:  # IS (por defecto)
                sub_path = NUMIS_SUBPATH
                prefix = "NumIS"

            # Usar la ruta base determinada automáticamente
            folder = os.path.join(_NUMBERING_BASE_PATH, sub_path, project_name)
            os.makedirs(folder, exist_ok=True)

            filename = f"{prefix}_{element_type}.txt"
            return os.path.join(folder, filename)

        except Exception as e:
            debug(f"[NUM] Error generando ruta del archivo: {e}")
            return None

    def _load_numbering_file(self, element_type, distribution_type="IS"):
        # Crear clave única que incluye el tipo de distribución
        key = f"{element_type}_{distribution_type}"

        if key not in numbering_by_type:
            numbering_by_type[key] = {"used": set(), "next": 1}

        path = self._get_numbering_file_path(element_type, distribution_type)
        if not path:
            return

        try:
            if os.path.exists(path):
                used = set()
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.isdigit():
                            used.add(int(line))

                numbering_by_type[key]["used"] = used
                numbering_by_type[key]["next"] = max(used) + 1 if used else 1

                debug(
                    f"[NUM] {key}: cargados {len(used)} números. Próximo = {numbering_by_type[key]['next']}"
                )
            else:
                debug(f"[NUM] {key}: archivo inexistente, se creará nuevo")

        except Exception as e:
            debug(f"[NUM] Error leyendo archivo: {e}")

    def _get_next_number(self, element_type, distribution_type="IS"):
        # Crear clave única que incluye el tipo de distribución
        key = f"{element_type}_{distribution_type}"

        if key not in numbering_by_type:
            self._load_numbering_file(element_type, distribution_type)

        num = numbering_by_type[key]["next"]
        numbering_by_type[key]["used"].add(num)
        numbering_by_type[key]["next"] = num + 1

        path = self._get_numbering_file_path(element_type, distribution_type)
        try:
            with open(path, "a") as f:
                f.write(f"{num}\n")
            debug(f"[NUM] Guardado número {num} → {key}")
        except Exception as e:
            debug(f"[NUM] Error guardando número: {e}")

        return num

    # ════════════════════════════════════════════════════════════════════════════
    #            Helpers para copias 3D en otros archivos (atributo pmp_pare)
    # ════════════════════════════════════════════════════════════════════════════

    def _get_pmp_pare_copy_uuids(self) -> List[str]:
        """
        Lee del build_ele la lista de UUID de copias 3D creadas en otros archivos.
        """
        try:
            if not hasattr(self.build_ele, "PmpPareCopyUUIDs"):
                return []
            raw = getattr(self.build_ele.PmpPareCopyUUIDs, "value", "") or ""
            if not raw:
                return []
            return [s for s in str(raw).split(";") if s.strip()]
        except Exception as ex:
            debug(f"[PMP_PARE] Error leyendo UUIDs guardados en build_ele: {ex}")
            return []

    def _set_pmp_pare_copy_uuids(self, uuids: List[str]) -> None:
        """
        Guarda en el build_ele la lista de UUID de copias 3D creadas en otros archivos.
        """
        try:
            if not hasattr(self.build_ele, "PmpPareCopyUUIDs"):
                return
            value = ";".join(str(u) for u in uuids if u)
            self.build_ele.PmpPareCopyUUIDs.value = value
        except Exception as ex:
            debug(f"[PMP_PARE] Error escribiendo UUIDs en build_ele: {ex}")

    def _delete_old_pmp_pare_copies_if_any(self) -> None:
        """
        Elimina, en todos los archivos de dibujo cargados, las copias 3D creadas
        en ejecuciones anteriores según la lista de UUID almacenada.
        """
        uuids = self._get_pmp_pare_copy_uuids()
        if not uuids:
            return

        uuid_set: Set[str] = set(uuids)

        try:
            list_documents = (
                AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
            )
        except Exception as ex_docs:
            debug(
                f"[PMP_PARE] Error obteniendo documentos cargados para borrar copias: {ex_docs}"
            )
            return

        if not list_documents:
            return

        drawing_service = AllplanBaseElements.DrawingFileService()
        doc_adapter = AllplanElementAdapter.DocumentAdapter()

        for name, df_id in list_documents:
            try:
                drawing_service.LoadFile(
                    doc_adapter,
                    df_id,
                    AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
                )
                target_doc = self.coord_input.GetActiveViewDocument()
            except Exception as ex_load:
                debug(
                    f"[PMP_PARE] Error activando archivo de dibujo '{name}' (ID={df_id}) para borrar copias: {ex_load}"
                )
                continue

            try:
                elems_to_delete = AllplanElementAdapter.BaseElementAdapterList()
                for (
                    element
                ) in AllplanBaseElements.ElementsSelectService.SelectAllElements(
                    target_doc
                ):
                    try:
                        if str(element.GetElementUUID()) in uuid_set:
                            elems_to_delete.append(element)
                    except Exception:
                        continue

                if len(elems_to_delete) > 0:
                    AllplanBaseElements.DeleteElements(
                        doc=target_doc, elements=elems_to_delete
                    )
                    debug(
                        f"[PMP_PARE] Eliminados {len(elems_to_delete)} elementos en '{name}' según lista guardada."
                    )
            except Exception as ex_del:
                debug(
                    f"[PMP_PARE] Error borrando elementos en archivo '{name}': {ex_del}"
                )

        # Limpiar lista tras el borrado
        self._set_pmp_pare_copy_uuids([])

    def _get_all_element_uuids_in_doc(self, doc) -> Set[str]:
        """Devuelve el conjunto de UUID de todos los elementos en el documento."""
        out: Set[str] = set()
        try:
            for el in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
                try:
                    out.add(str(el.GetElementUUID()))
                except Exception:
                    continue
        except Exception:
            pass
        return out

    def _delete_elements_by_uuids(self, doc, uuid_set: Set[str]) -> int:
        """Borra del documento los elementos cuyo UUID está en uuid_set. Devuelve cuántos se borraron."""
        try:
            elems_to_delete = AllplanElementAdapter.BaseElementAdapterList()
            for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(
                doc
            ):
                try:
                    if str(element.GetElementUUID()) in uuid_set:
                        elems_to_delete.append(element)
                except Exception:
                    continue
            if len(elems_to_delete) > 0:
                AllplanBaseElements.DeleteElements(doc=doc, elements=elems_to_delete)
                return len(elems_to_delete)
        except Exception as ex:
            debug(f"[PMP_PARE] Error borrando elementos por UUID: {ex}")
        return 0

    def _check_all_elements_have_pmp_pare(self, elems, base_doc) -> bool:
        """
        Comprueba que todos los elementos 3D (excepto los que tienen Material=CAVITAT)
        tengan el atributo pmp_pare. Si falta en alguno, devuelve False.
        """
        for elem in elems:
            try:
                if _has_material_cavitat(elem, base_doc):
                    continue
                parent_id = _get_pmp_pare_value_from_elem(elem, base_doc)
                if not parent_id or not str(parent_id).strip():
                    return False
            except Exception:
                return False
        return True

    def _copy_elements_by_pmp_pare(self, elems) -> bool:
        """
        Copia los sólidos 3D de 'elems' a otros archivos de dibujo,
        agrupando por el valor del atributo pmp_pare.
        Si algún elemento (no CAVITAT) no tiene pmp_pare, se avisa al usuario.
        Devuelve True para continuar (con o sin copia), False si el usuario canceló para asignar el atributo.
        """
        if not elems:
            return True

        try:
            if not hasattr(self, "coord_input") or self.coord_input is None:
                return True
            base_doc = self.coord_input.GetInputViewDocument()
        except Exception as ex_doc:
            debug(
                f"[PMP_PARE] No se pudo obtener documento base para lectura de atributos: {ex_doc}"
            )
            return True

        if not self._check_all_elements_have_pmp_pare(elems, base_doc):
            msg = (
                "Un elemento del modelo no tiene atributo de padre. "
                "No se podrá hacer la copia en su respectivo archivo.\n\n"
                "¿Desea continuar sin copiar (Aceptar) o cancelar para asignar el atributo (Cancelar)?"
            )
            try:
                if hasattr(PythonUtility, "MB_OKCANCEL"):
                    resp = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
                else:
                    resp = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
            except Exception:
                resp = PythonUtility.MB_OK
            if (
                getattr(PythonUtility, "IDCANCEL", None) is not None
                and resp == PythonUtility.IDCANCEL
            ):
                debug("[PMP_PARE] Usuario canceló para asignar el atributo de padre.")
                return False
            debug("[PMP_PARE] Usuario eligió continuar sin copiar.")
            return True

        # Agrupar elementos por valor de pmp_pare
        parent_map: dict[str, List[object]] = {}
        try:
            for elem in elems:
                try:
                    parent_id = _get_pmp_pare_value_from_elem(elem, base_doc)
                except Exception as ex_attr:
                    debug(
                        f"[PMP_PARE] Error leyendo pmp_pare de un elemento: {ex_attr}"
                    )
                    continue

                if not parent_id:
                    continue

                parent_id = str(parent_id).strip()
                if not parent_id:
                    continue

                parent_map.setdefault(parent_id, []).append(elem)
        except Exception as ex_group:
            debug(f"[PMP_PARE] Error agrupando elementos por pmp_pare: {ex_group}")
            return True

        if not parent_map:
            debug("[PMP_PARE] No hay elementos con atributo pmp_pare para copiar.")
            self._set_pmp_pare_copy_uuids([])
            return True

        try:
            list_documents = (
                AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
            )
        except Exception as ex_docs:
            debug(
                f"[PMP_PARE] Error obteniendo documentos cargados para copiar geometrías: {ex_docs}"
            )
            return True

        if not list_documents:
            debug("[PMP_PARE] No hay documentos cargados para copiar las geometrías.")
            return True

        # Debug: mostrar qué nombres/IDs devuelve la API para poder encontrar IS01/TD01
        print(
            f"[PMP_PARE] Documentos cargados ({len(list_documents)}): "
            + ", ".join(
                f"id={df_id} name={repr(name)}" for name, df_id in list_documents
            )
        )

        drawing_service = AllplanBaseElements.DrawingFileService()
        # Recordar el número de archivo activo para restaurarlo después
        try:
            original_file = AllplanBaseElements.DrawingFileService.GetActiveFileNumber()
        except Exception:
            original_file = None

        new_uuids: List[str] = []

        for parent_id, elems_list in parent_map.items():
            # Buscar archivo de dibujo cuyo nombre contenga el ID de padre
            target = None
            for name, df_id in list_documents:
                try:
                    if parent_id in str(name):
                        target = (name, df_id)
                        break
                except Exception:
                    continue

            if not target:
                debug(
                    f"[PMP_PARE] No se encontró archivo cuyo nombre contenga '{parent_id}'."
                )
                continue

            name, df_id = target  # df_id es el número de archivo de dibujo

            try:
                drawing_service.LoadFile(
                    base_doc,
                    df_id,
                    AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
                )
                target_doc = self.coord_input.GetActiveViewDocument()
            except Exception as ex_load:
                debug(
                    f"[PMP_PARE] Error activando archivo de dibujo '{name}' (ID={df_id}): {ex_load}"
                )
                continue

            try:
                # UUIDs existentes antes de crear copias
                before_uuids: Set[str] = set()
                for el in AllplanBaseElements.ElementsSelectService.SelectAllElements(
                    target_doc
                ):
                    try:
                        before_uuids.add(str(el.GetElementUUID()))
                    except Exception:
                        continue

                # Crear las copias de los elementos 3D en el archivo de dibujo activo
                AllplanBaseElements.CreateElements(
                    target_doc, AllplanGeo.Matrix3D(), elems_list, [], None
                )

                # UUIDs después de crear copias
                after_uuids: Set[str] = set()
                for el in AllplanBaseElements.ElementsSelectService.SelectAllElements(
                    target_doc
                ):
                    try:
                        after_uuids.add(str(el.GetElementUUID()))
                    except Exception:
                        continue

                created_uuids = after_uuids.difference(before_uuids)
                if created_uuids:
                    debug(
                        f"[PMP_PARE] Copiados {len(created_uuids)} elementos a '{name}' para padre '{parent_id}'."
                    )
                    new_uuids.extend(sorted(created_uuids))
            except Exception as ex_copy:
                debug(
                    f"[PMP_PARE] Error copiando elementos a archivo '{name}' para padre '{parent_id}': {ex_copy}"
                )

        # Volver a activar el archivo donde el usuario estaba dibujando (PPG)
        if original_file is not None:
            try:
                drawing_service.LoadFile(
                    base_doc,
                    original_file,
                    AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
                )
            except Exception as ex_restore:
                debug(
                    f"[PMP_PARE] No se pudo restaurar archivo de dibujo original: {ex_restore}"
                )

        self._set_pmp_pare_copy_uuids(new_uuids)
        return True

    def _get_te_model(self, d_main_in: float, d_main_out: float, d_branch: float):
        """
        Devuelve (TeModelAuto, mirror_x) según exista el modelo específico en /IS.
        Usa el patrón de importación que vos pasaste.
        """
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return None, False, None

        te_name = f"Te_{int(d_main_in)}_{int(d_branch)}_{int(d_main_out)}_IS"
        te_path = os.path.join(os.path.dirname(__file__), "IS", f"{te_name}.py")

        inv_name = f"Te_{int(d_main_out)}_{int(d_branch)}_{int(d_main_in)}_IS"
        inv_path = os.path.join(os.path.dirname(__file__), "IS", f"{inv_name}.py")

        TeModelAuto = None
        mirror_x = False

        if os.path.exists(te_path):
            spec = importlib.util.spec_from_file_location(te_name, te_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            TeModelAuto = getattr(module, "TeModel", None)
            print(f"[SO] Importado {te_name}")

        elif os.path.exists(inv_path):
            spec = importlib.util.spec_from_file_location(inv_name, inv_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            TeModelAuto = getattr(module, "TeModel", None)
            mirror_x = True
            print(f"[SO] Importado {inv_name} (invertida)")

        else:
            print("[SO] Modelo específico no existe → uso genérico")
            # OJO: acá asumimos que existe un TeModel genérico importado en tu script
            TeModelAuto = TeModel
            if d_main_in < d_main_out:
                mirror_x = True

        if TeModelAuto is None:
            return None, mirror_x, doc

        return TeModelAuto, mirror_x, doc

    def _register_manguito_cuts(
        self,
        path_idx: int,
        seg_left_idx: int,
        seg_right_idx: int,
        d1: float,
        d2: float,
    ):
        """
        Registra cuánto recortar en los extremos de los tramos que se unen
        mediante un manguito (cambio de diámetro recto).

        - seg_left_idx: tramo antes del vértice (usa diámetro d1)
        - seg_right_idx: tramo después del vértice (usa diámetro d2)
        """
        try:
            d1_key = int(round(d1))
            d2_key = int(round(d2))
            key = (d1_key, d2_key)

            if key not in MANGUITO_TRIM_BY_DIAM:
                print(f"[DBG] Manguito sin recorte definido para {key}")
                return

            cut_left, cut_right = MANGUITO_TRIM_BY_DIAM[key]

            if not hasattr(self, "segment_cuts") or self.segment_cuts is None:
                self.segment_cuts = {}

            # Tramo izquierdo: recorte en el extremo final (end)
            cuts_left = self.segment_cuts.setdefault(
                (path_idx, seg_left_idx), {"start": 0.0, "end": 0.0}
            )
            cuts_left["end"] += cut_left

            # Tramo derecho: recorte en el extremo inicial (start)
            cuts_right = self.segment_cuts.setdefault(
                (path_idx, seg_right_idx), {"start": 0.0, "end": 0.0}
            )
            cuts_right["start"] += cut_right

            print(
                f"[DBG] Manguito cuts path={path_idx}: "
                f"seg_left={seg_left_idx} end-={cut_left}mm, "
                f"seg_right={seg_right_idx} start-={cut_right}mm"
            )
        except Exception as ex:
            print(f"[DBG] Error en _register_manguito_cuts: {ex}")

    def _register_te_cuts(self, path_idx: int, vkey, vertex_map):
        """
        Registra recortes de tubos alrededor de una TE en el vértice vkey.

        Convención TE:
        key TE_TRIMS = (main_in, branch, main_out)
        trims        = (trim_main_in, trim_branch, trim_main_out)

        Requiere:
        vertex_map[vkey] -> lista de 3 conexiones (2 colineales = main, 1 perpendicular = branch)
        cada conexión: {"path_idx": int, "seg_idx": int, "side": "start"|"end"}
        """
        conns = vertex_map.get(vkey, [])
        if len(conns) < 3:
            print(
                f"[DBG] TE cuts: vertex {vkey} no tiene 3 conexiones (tiene {len(conns)})"
            )
            return

        import math

        # --- helper: dirección unitaria de un segmento (seg_idx) ---
        def _seg_dir(conn):
            pts = self.saved_paths[conn["path_idx"]]
            s = conn["seg_idx"]
            a = pts[s]
            b = pts[s + 1]
            vx = b.X - a.X
            vy = b.Y - a.Y
            vz = b.Z - a.Z
            ln = math.sqrt(vx * vx + vy * vy + vz * vz)
            if ln < 1e-9:
                return (0.0, 0.0, 0.0)
            return (vx / ln, vy / ln, vz / ln)

        # --- identificar cuáles 2 conexiones son colineales (main) por máximo dot ---
        dirs = [(_seg_dir(c), idx) for idx, c in enumerate(conns)]
        best_pair = None
        best_dot = -1.0

        for i in range(len(dirs)):
            for j in range(i + 1, len(dirs)):
                (d1, idx1) = dirs[i]
                (d2, idx2) = dirs[j]
                dot = abs(d1[0] * d2[0] + d1[1] * d2[1] + d1[2] * d2[2])
                if dot > best_dot:
                    best_dot = dot
                    best_pair = (idx1, idx2)

        if not best_pair:
            print("[DBG] TE cuts: no pude detectar los 2 main colineales")
            return

        main_i, main_j = best_pair
        branch_k = [k for k in range(len(conns)) if k not in (main_i, main_j)][0]

        main_a = conns[main_i]
        main_b = conns[main_j]
        branch = conns[branch_k]

        # --- diámetros de cada tramo ---
        d_main_a = int(
            round(
                self._get_segment_diameter(
                    main_a["path_idx"], main_a["seg_idx"], default=20.0
                )
            )
        )
        d_main_b = int(
            round(
                self._get_segment_diameter(
                    main_b["path_idx"], main_b["seg_idx"], default=20.0
                )
            )
        )
        d_branch = int(
            round(
                self._get_segment_diameter(
                    branch["path_idx"], branch["seg_idx"], default=20.0
                )
            )
        )

        # Definimos main_in y main_out como (mayor, menor) entre los 2 main
        main_in = max(d_main_a, d_main_b)
        main_out = min(d_main_a, d_main_b)

        # ✅ TU ORDEN: (main_in, branch, main_out)
        key = (main_in, d_branch, main_out)
        trims = TE_TRIMS.get(key)

        print(
            f"[DBG] TE cuts: main_a={d_main_a} main_b={d_main_b} branch={d_branch} "
            f"-> key={key} trims={trims}"
        )

        if not trims:
            print(f"[DBG] TE cuts: no hay regla TE_TRIMS para {key}")
            return

        trim_main_in, trim_branch, trim_main_out = trims

        # decidir cuál conexión es main_in y cuál main_out
        if d_main_a >= d_main_b:
            conn_in = main_a
            conn_out = main_b
        else:
            conn_in = main_b
            conn_out = main_a

        # --- helper para sumar recorte al lado correcto (start/end) ---
        def _add_cut(conn, trim_mm):
            seg_key = (conn["path_idx"], conn["seg_idx"])
            cuts = self.segment_cuts.setdefault(seg_key, {"start": 0.0, "end": 0.0})

            side = "start" if conn.get("is_start") else "end"

            if side == "start":
                cuts["start"] += float(trim_mm)
            else:
                cuts["end"] += float(trim_mm)

        # Aplicar trims a las 3 conexiones en el extremo que toca la TE
        _add_cut(conn_in, trim_main_in)
        _add_cut(branch, trim_branch)
        _add_cut(conn_out, trim_main_out)

        print(
            f"[DBG] TE cuts applied: main_in({main_in})={trim_main_in}mm, "
            f"branch({d_branch})={trim_branch}mm, "
            f"main_out({main_out})={trim_main_out}mm"
        )

    def __init__(self, build_ele, script_object_data):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.script_object_interactor: Optional[PolylineInteractor] = None

        # Cambio: en lugar de solo puntos, guardamos segmentos con información de sección
        self.saved_segments = []
        self.saved_paths = []

        # Puntos de elementos definidos (T sortida, Colze base, Clau de Pas) en la polilínea
        self.element_markers = (
            []
        )  # [{"kind": "start"|"end"|"free", "pos": Point3D, "element_type": str, ...}]
        # Puntos libres (modo "Modo puntos libres"): lista de {pos, flag, element_type, order}
        self.free_placed_points = []

        # Nuevo: recortes por tramo (start/end) en mm
        # clave: (path_idx, seg_idx) -> {"start": mm, "end": mm}
        self.segment_cuts = {}

        # Layer overrides desde modo edición de layers
        self.layer_overrides = {}  # {element_key: layer_id}
        # Distribution y attribute overrides desde modo edición de layers
        self.distribution_overrides = {}  # {element_key: distribution_type}
        self.attribute_overrides = {}  # {element_key: attribute_value}

        # Orientación 3D de referencia (ángulo en radianes desde eje X)
        self.reference_orientation_angle = None

        # Restaurar estado guardado si existe (al editar una instancia existente)
        self._restore_saved_state()

        # Al iniciar la PythonPart, eliminar las copias 3D creadas en ejecuciones anteriores
        # según los UUID almacenados en el build_ele (si existen).
        try:
            self._delete_old_pmp_pare_copies_if_any()
        except Exception as ex_del:
            debug(f"[PMP_PARE] Error borrando copias antiguas por pmp_pare: {ex_del}")

        print(f"[SO] *** SCRIPT OBJECT INICIALIZADO ***")

    def _make_circle_polyline_for_marker(
        self, center: AllplanGeo.Point3D, radius: float, segments: int = 24
    ):
        """Crea una Polyline3D circular en el plano XY para marcadores de elementos definidos (módulo ElementosDefinidos)."""
        return make_circle_polyline_for_marker(center, radius, segments)

    def _create_tube_segment(
        self,
        p0,
        p1,
        path_idx=None,
        seg_idx=None,
        sub_seg_idx=None,
        distribution_type=None,
        p_prev=None,
    ):
        """
        Crea un tramo de tubo de polietileno entre p0 y p1.
        Usa TubPolietileModel (IS).
        Usa el largo real del segmento y el diámetro del segmento (saved_segments).
        Respeta recortes en inicio/fin según elementos adyacentes (segment_cuts).

        Args:
            p0, p1: Puntos de inicio y fin del tubo
            path_idx: Índice del path
            seg_idx: Índice del segmento original
            sub_seg_idx: Índice del sub-segmento (opcional, para segmentos divididos)
            distribution_type: Tipo de distribución (TD o IS)
            p_prev: Punto del segmento previo (opcional, para calcular rotación adicional)
        """
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return []

        # ==========================================================
        # Diámetro por tramo (si tenemos índices)
        # ==========================================================
        d_seg = 20.0
        if path_idx is not None and seg_idx is not None:
            try:
                d_seg = self._get_segment_diameter(path_idx, seg_idx, default=20.0)
            except Exception:
                d_seg = 20.0

            diam_attr = getattr(self.build_ele, "DiametroAplicar", None)
            if diam_attr is not None:
                try:
                    diam_attr.value = int(round(d_seg))
                except Exception:
                    diam_attr.value = d_seg

            if sub_seg_idx is not None:
                print(
                    f"[DBG] tubo tramo path={path_idx} seg={seg_idx} sub={sub_seg_idx} usa diam={d_seg}"
                )
            else:
                print(
                    f"[DBG] tubo tramo path={path_idx} seg={seg_idx} usa diam={d_seg}"
                )
        else:
            print("[DBG] tubo sin path/seg -> usa DiametroAplicar tal cual")

        # ==========================================================
        # Recortes (start/end) para este tramo
        # ==========================================================
        cut_start = 0.0
        cut_end = 0.0
        if path_idx is not None and seg_idx is not None:
            try:
                # Si hay sub_seg_idx, usar clave compuesta; si no, usar clave simple
                if sub_seg_idx is not None:
                    seg_key = (path_idx, seg_idx, sub_seg_idx)
                else:
                    seg_key = (path_idx, seg_idx)

                cuts = getattr(self, "segment_cuts", {}).get(seg_key, None)
                if cuts:
                    cut_start = float(cuts.get("start", 0.0) or 0.0)
                    cut_end = float(cuts.get("end", 0.0) or 0.0)
                    if sub_seg_idx is not None:
                        print(
                            f"[DBG] segment_cuts lookup path={path_idx} seg={seg_idx} sub={sub_seg_idx} -> {cuts}"
                        )
                    else:
                        print(
                            f"[DBG] segment_cuts lookup path={path_idx} seg={seg_idx} -> {cuts}"
                        )
            except Exception as ex:
                print(f"[DBG] Error leyendo segment_cuts: {ex}")

        # ==========================================================
        # Vector del tramo original
        # ==========================================================
        vx = p1.X - p0.X
        vy = p1.Y - p0.Y
        vz = p1.Z - p0.Z

        length = math.sqrt(vx * vx + vy * vy + vz * vz)
        if length < 1e-3:
            return []

        # ==========================================================
        # Longitud efectiva después de recortes
        # ==========================================================
        total_cut = cut_start + cut_end
        length_trim = length - total_cut
        if length_trim <= 1e-3:
            if sub_seg_idx is not None:
                print(
                    f"[DBG] tramo path={path_idx} seg={seg_idx} sub={sub_seg_idx} demasiado corto "
                    f"después de recorte (length={length}, total_cut={total_cut})"
                )
            else:
                print(
                    f"[DBG] tramo path={path_idx} seg={seg_idx} demasiado corto "
                    f"después de recorte (length={length}, total_cut={total_cut})"
                )
            return []

        # Vector unitario del tramo ORIGINAL
        ux = vx / length
        uy = vy / length
        uz = vz / length

        # Puntos recortados
        p_start = AllplanGeo.Point3D(
            p0.X + ux * cut_start,
            p0.Y + uy * cut_start,
            p0.Z + uz * cut_start,
        )
        p_end = AllplanGeo.Point3D(
            p1.X - ux * cut_end,
            p1.Y - uy * cut_end,
            p1.Z - uz * cut_end,
        )

        # Vector del tramo RECORTADO (esto es lo que se usa para orientar)
        dx = p_end.X - p_start.X
        dy = p_end.Y - p_start.Y
        dz = p_end.Z - p_start.Z

        # Debug: Verificar si el tubo es vertical y si necesita rotación
        if path_idx is not None:
            # Calcular la magnitud horizontal del vector
            horizontal_mag = math.sqrt(dx * dx + dy * dy)
            is_vertical = (
                horizontal_mag < 1e-3 and abs(dz) > 1e-6
            )  # Tolerancia más amplia para detectar vertical
            branch_rotation_needed = getattr(self, "branch_tube_rotation_needed", {})

            # Debug para todos los tubos del path que necesita rotación
            if path_idx in branch_rotation_needed:
                print(
                    f"[DBG] Tubo path={path_idx} seg={seg_idx}: dx={dx:.6f}, dy={dy:.6f}, dz={dz:.6f}, "
                    f"horizontal_mag={horizontal_mag:.6f}, is_vertical={is_vertical}, "
                    f"branch_rotation_needed={branch_rotation_needed}"
                )

            if is_vertical:
                print(
                    f"[DBG] ✅ Tubo path={path_idx} seg={seg_idx} es VERTICAL (dx={dx:.6f}, dy={dy:.6f}, dz={dz:.6f}), "
                    f"branch_rotation_needed={branch_rotation_needed}, path en dict={path_idx in branch_rotation_needed}"
                )
                if path_idx in branch_rotation_needed:
                    stored_angle = branch_rotation_needed[path_idx]
                    print(
                        f"[DBG] Ángulo almacenado para path={path_idx}: {math.degrees(stored_angle):.1f}° "
                        f"({stored_angle:.4f} rad)"
                    )

        if abs(cut_start) > 1e-6 or abs(cut_end) > 1e-6:
            if sub_seg_idx is not None:
                print(
                    f"[DBG] trim seg path={path_idx} seg={seg_idx} sub={sub_seg_idx}: "
                    f"start={cut_start}mm end={cut_end}mm len={length:.3f} -> {length_trim:.3f}"
                )
            else:
                print(
                    f"[DBG] trim seg path={path_idx} seg={seg_idx}: "
                    f"start={cut_start}mm end={cut_end}mm len={length:.3f} -> {length_trim:.3f}"
                )

        # ==========================================================
        # Crear modelo de tubo (TD o IS según distribución del segmento)
        # ==========================================================
        # Obtener tipo de distribución del segmento
        # Si no se proporciona distribution_type como parámetro, obtenerlo del segmento
        if distribution_type is None:
            distribution_type = "IS"  # Por defecto IS
            if path_idx is not None and seg_idx is not None:
                try:
                    distribution_type = self._get_segment_distribution_type(
                        path_idx, seg_idx, "IS"
                    )
                except Exception as ex:
                    print(f"[DBG] Error obteniendo distribución del segmento: {ex}")

        if path_idx is not None and seg_idx is not None:
            print(
                f"[DBG] tubo tramo path={path_idx} seg={seg_idx} usa distribución={distribution_type}"
            )

        # ==========================================================
        # Instanciar modelo de tubo según distribución + tipo de tubo
        # ==========================================================
        tubo = None

        try:
            # Leer tipo de tubo desde la paleta según la distribución
            if distribution_type == "TD":
                # Para TD usamos el combo TipoDeTuboTD (Polietilè | Multicapa | Armaflex)
                tube_prop = getattr(self.build_ele, "TipoDeTuboTD", None)
                tube_type = None
                if tube_prop is not None:
                    tube_type = getattr(tube_prop, "value", tube_prop)
                tube_type = tube_type or "Polietilè"

                if isinstance(tube_type, str):
                    tube_type_norm = tube_type.strip()
                else:
                    tube_type_norm = "Polietilè"

                # Seleccionar modelo TD según tipo de tubo
                if tube_type_norm == "Polietilè":
                    tubo = (
                        TubPolietileTDModel(self.build_ele, doc)
                        if TubPolietileTDModel is not None
                        else None
                    )
                elif tube_type_norm == "Multicapa":
                    tubo = (
                        TubMulticapaTDModel(self.build_ele, doc)
                        if TubMulticapaTDModel is not None
                        else None
                    )
                elif tube_type_norm == "Armaflex":
                    tubo = (
                        ArmaflexModel(self.build_ele, doc)
                        if ArmaflexModel is not None
                        else None
                    )
                else:
                    # Fallback seguro: Polietileno TD
                    print(
                        f"[DBG] TipoDeTuboTD desconocido '{tube_type_norm}', usando Polietilè TD por defecto"
                    )
                    tubo = (
                        TubPolietileTDModel(self.build_ele, doc)
                        if TubPolietileTDModel is not None
                        else None
                    )

                print(
                    f"[DBG] distribución TD, TipoDeTuboTD='{tube_type_norm}', modelo={tubo.__class__.__name__ if tubo else 'None'}"
                )

            else:
                # IS (por defecto) → hoy solo Polietilè, pero leemos el combo por si se amplía en el futuro
                tube_prop = getattr(self.build_ele, "TipoDeTuboIS", None)
                tube_type = None
                if tube_prop is not None:
                    tube_type = getattr(tube_prop, "value", tube_prop)
                tube_type = tube_type or "Polietilè"

                if isinstance(tube_type, str):
                    tube_type_norm = tube_type.strip()
                else:
                    tube_type_norm = "Polietilè"

                # De momento solo Polietilè-IS
                tubo = (
                    TubPolietileModel(self.build_ele, doc)
                    if TubPolietileModel is not None
                    else None
                )

                print(
                    f"[DBG] distribución IS, TipoDeTuboIS='{tube_type_norm}', modelo={tubo.__class__.__name__ if tubo else 'None'}"
                )

        except Exception as ex:
            print(f"[SO] ERROR instanciando modelo de tubo según TipoDeTubo: {ex}")
            # Fallback final: usar polietileno según distribución
            if distribution_type == "TD":
                tubo = (
                    TubPolietileTDModel(self.build_ele, doc)
                    if TubPolietileTDModel is not None
                    else None
                )
            else:
                tubo = (
                    TubPolietileModel(self.build_ele, doc)
                    if TubPolietileModel is not None
                    else None
                )

        if tubo is None:
            print("[SO] ERROR: No hay modelo de tubo disponible")
            return []

        # ==========================================================
        # 2) Pasar la longitud recortada
        # ==========================================================
        if hasattr(tubo, "set_length"):
            tubo.set_length(length_trim)

        # ==========================================================
        # 3) Crear ModelElement3D
        # ==========================================================
        model_list = tubo.build()
        if not model_list:
            return []

        # ==========================================================
        # 4) Orientación + Transform
        # ==========================================================
        mat = AllplanGeo.Matrix3D()

        # Debug: Verificar todos los tubos, especialmente los que necesitan rotación
        if path_idx is not None:
            branch_rotation_needed = getattr(self, "branch_tube_rotation_needed", {})
            if path_idx in branch_rotation_needed:
                print(
                    f"[DBG] 🔍 Tubo path={path_idx} seg={seg_idx}: dx={dx:.6f}, dy={dy:.6f}, dz={dz:.6f}, "
                    f"length={length_trim:.2f}mm, branch_rotation_needed contiene path={path_idx}"
                )

        # Caso 1: tramo prácticamente vertical (solo Z)
        # Usar tolerancia más amplia para detectar tubos verticales (pueden tener pequeñas componentes X/Y por recortes)
        horizontal_mag = math.sqrt(dx * dx + dy * dy)
        is_vertical_tube = horizontal_mag < 1e-3 and abs(dz) > 1e-6

        # Debug adicional para verificar detección de tubo vertical
        if path_idx is not None:
            branch_rotation_needed = getattr(self, "branch_tube_rotation_needed", {})
            if path_idx in branch_rotation_needed:
                print(
                    f"[DBG] 🔍 Verificando si tubo path={path_idx} seg={seg_idx} es vertical: "
                    f"horizontal_mag={horizontal_mag:.6f}, dz={dz:.6f}, is_vertical_tube={is_vertical_tube}"
                )

        if is_vertical_tube:
            # 🚨 ROTACIÓN ADICIONAL: Usar reference_orientation_angle si está definido,
            # o el ángulo del segmento previo si existe, o aplicar rotación de -45° si viene de Te diagonal
            rotation_angle_z = 0.0

            # Prioridad 1: CONDICIONAL - Si el tubo viene de una Te con tramo principal en diagonal
            # y rama perpendicular elevada en Z, aplicar rotación usando el ángulo del tramo principal
            if path_idx is not None:
                branch_rotation_needed = getattr(
                    self, "branch_tube_rotation_needed", {}
                )
                print(
                    f"[DBG] Verificando rotación para tubo VERTICAL path={path_idx}, "
                    f"branch_rotation_needed={branch_rotation_needed}, "
                    f"path en dict={path_idx in branch_rotation_needed}"
                )
                if path_idx in branch_rotation_needed:
                    # Usar el ángulo del tramo principal almacenado (ya está en radianes)
                    rotation_angle_z = branch_rotation_needed[path_idx]
                    print(
                        f"[DBG] ✅ CONDICIONAL: Aplicando rotación de {math.degrees(rotation_angle_z):.1f}° "
                        f"al tubo perpendicular (path={path_idx}) "
                        f"usando el ángulo del tramo principal como referencia"
                    )
                else:
                    print(
                        f"[DBG] ⚠️ Tubo path={path_idx} NO está en branch_rotation_needed, "
                        f"no se aplicará rotación del tramo principal"
                    )

            # Prioridad 2: Usar reference_orientation_angle si está definido (solo si no hay rotación de Te)
            if abs(rotation_angle_z) < 1e-6:
                ref_orientation = getattr(self, "reference_orientation_angle", None)
                if ref_orientation is not None:
                    rotation_angle_z = ref_orientation
                    print(
                        f"[DBG] Usando orientación 3D de referencia: {math.degrees(rotation_angle_z):.2f}° en XY"
                    )

            # Prioridad 3: Calcular ángulo del segmento previo si existe (solo si no hay rotación de Te ni referencia)
            if abs(rotation_angle_z) < 1e-6 and p_prev is not None:
                # Prioridad 2: Calcular ángulo del segmento previo si existe
                prev_dx = p0.X - p_prev.X
                prev_dy = p0.Y - p_prev.Y
                prev_dz = p0.Z - p_prev.Z
                prev_length = math.sqrt(
                    prev_dx * prev_dx + prev_dy * prev_dy + prev_dz * prev_dz
                )

                # Verificar si el segmento previo era horizontal (prácticamente sin componente Z)
                if prev_length > 1e-6 and abs(prev_dz) < 1e-6:
                    # Calcular el ángulo del segmento previo en el plano XY
                    rotation_angle_z = math.atan2(prev_dy, prev_dx)
                    print(
                        f"[DBG] Segmento previo horizontal detectado con ángulo {math.degrees(rotation_angle_z):.2f}° en XY"
                    )

            # Aplicar primero la rotación sobre el eje Z (si hay ángulo definido)
            if abs(rotation_angle_z) > 1e-6:
                axis_z = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0),
                    AllplanGeo.Point3D(0, 0, 1),
                )
                mat_z_rot = AllplanGeo.Matrix3D()
                mat_z_rot.SetRotation(axis_z, AllplanGeo.Angle(rotation_angle_z))
                mat = mat_z_rot

            # Luego aplicar la rotación sobre el eje Y para orientar verticalmente
            axis_y = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(0, 1, 0),
            )

            if dz > 0:
                angle_y = -math.pi / 2.0  # +X → +Z
            else:
                angle_y = math.pi / 2.0  # +X → -Z

            mat_y_rot = AllplanGeo.Matrix3D()
            mat_y_rot.SetRotation(axis_y, AllplanGeo.Angle(angle_y))

            # Combinar las rotaciones: primero Z (si existe), luego Y
            if abs(rotation_angle_z) > 1e-6:
                mat = (
                    mat_y_rot * mat
                )  # Aplicar primero mat (rotación Z), luego mat_y_rot (rotación Y)
            else:
                mat = mat_y_rot

            # 🚨 CLAVE: colocar en p_start, no en p0
            mat.SetTranslation(AllplanGeo.Vector3D(p_start.X, p_start.Y, p_start.Z))

        # Caso 2: horizontal/XY
        else:
            angle_rad = math.atan2(dy, dx)
            axis_z = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(0, 0, 1),
            )
            mat.SetRotation(axis_z, AllplanGeo.Angle(angle_rad))

            # 🚨 CLAVE: colocar en p_start, no en p0
            mat.SetTranslation(AllplanGeo.Vector3D(p_start.X, p_start.Y, p_start.Z))

        elems = []
        for m in model_list:
            try:
                tlist = m.GetTransformationList()
            except Exception:
                tlist = []
            tlist.append(mat)
            m.SetTransformationList(tlist)

            # Aplicar layer si está definido para este segmento
            if path_idx is not None and seg_idx is not None:
                try:
                    # Primero verificar si hay layer override (modo edición de layers)
                    element_key = ("tube", path_idx, seg_idx)
                    layer_id = None
                    if hasattr(self, "layer_overrides") and self.layer_overrides:
                        layer_id = self.layer_overrides.get(element_key)

                    # Si no hay override, usar el layer del segmento
                    if layer_id is None:
                        layer_id = self._get_segment_layer_id(
                            path_idx, seg_idx, default=None
                        )

                    if layer_id is not None and layer_id > 0:
                        # Obtener las propiedades comunes del elemento
                        com_prop = m.GetCommonProperties()
                        if com_prop is None:
                            com_prop = AllplanBaseElements.CommonProperties()
                            com_prop.GetGlobalProperties()
                        com_prop.Layer = layer_id
                        m.SetCommonProperties(com_prop)
                        print(
                            f"[DBG] Layer ID {layer_id} aplicado a tubo path={path_idx} seg={seg_idx}"
                        )
                except Exception as ex:
                    print(f"[DBG] Error aplicando layer al elemento: {ex}")

            elems.append(m)

        # ==========================================================
        # NUMERACIÓN ABSOLUTA DE TUBOS (solo primer elemento)
        # Modifica el atributo "Atributo personalizado 01"
        # IMPORTANTE: No aplicar a elementos con Material = "CAVITAT"
        # ==========================================================
        try:
            if elems:
                diam_mm = int(round(d_seg)) if "d_seg" in locals() else 20
                element_type = f"Tubo_{diam_mm}mm"

                # siguiente número absoluto (discrimina entre TD e IS)
                next_num = self._get_next_number(element_type, distribution_type)

                # Buscar el primer elemento que NO tenga Material = "CAVITAT"
                first_elem = None
                for elem in elems:
                    if not _has_material_cavitat(elem, doc):
                        first_elem = elem
                        break

                # Si todos los elementos tienen CAVITAT, no aplicar numeración
                if first_elem is None:
                    debug(
                        "[NUM] Todos los elementos tienen Material=CAVITAT, omitiendo numeración"
                    )
                    return elems

                # Usar ID estándar Allplan (Custom attribute 01)
                attr01_id = ATTR_PERSO_01_ID
                debug(f"[NUM] ID 'Atributo personalizado 01' = {attr01_id}")

                if attr01_id and attr01_id > 0:
                    attrs = first_elem.GetAttributes()
                    attr_sets = list(attrs.GetAttributeSets() or [])

                    found_attr = False

                    for attr_set in attr_sets:
                        attr_list = list(attr_set.GetAttributes() or [])
                        for a in attr_list:
                            if a.Id == attr01_id:
                                base_value = (a.Value or "").strip()
                                if not base_value:
                                    base_value = f"TAF-{diam_mm}."
                                # Ej: "TAF-20." -> "TAF-20. 3"
                                a.Value = f"{base_value} {next_num}"
                                found_attr = True
                                debug(
                                    f"[NUM] ATTR01 original = '{base_value}' → nuevo = '{a.Value}'"
                                )
                        attr_set.SetAttributes(attr_list)

                    # Si por lo que sea no existía, lo creamos
                    if not found_attr:
                        new_val = f"TAF-{diam_mm}. {next_num}"
                        new_attr = AllplanBaseElements.AttributeString(
                            attr01_id, new_val
                        )

                        if attr_sets:
                            first_set = attr_sets[0]
                            attr_list = list(first_set.GetAttributes() or [])
                            attr_list.append(new_attr)
                            first_set.SetAttributes(attr_list)
                        else:
                            attr_sets = [AllplanBaseElements.AttributeSet([new_attr])]

                    attrs.SetAttributeSets(attr_sets)
                    first_elem.SetAttributes(attrs)

                    debug(f"[NUM] Tubo enumerado: ATTR01 actualizado con {next_num}")
                else:
                    debug("[NUM] No se pudo obtener ID de 'Atributo personalizado 01'")

        except Exception as e:
            debug(f"[NUM] ERROR asignando numeración al ATTR01 del tubo: {e}")

        return elems

    def _normalize_ref_angle_for_comparison(self, angle_rad):
        """
        Normaliza el ángulo de referencia para que ángulos equivalentes (135° y 315°/-45°)
        se traten igual. Mapea 315°/-45° a 135° para usar la misma lógica.
        Devuelve el ángulo en grados normalizado.
        """
        angle_deg = math.degrees(angle_rad)
        # Normalizar a [-180, 180]
        if angle_deg > 180.0:
            angle_deg -= 360.0
        elif angle_deg < -180.0:
            angle_deg += 360.0

        # Si está cerca de -45° (entre -55° y -35°), mapearlo a 135°
        # 315° cuando se normaliza a [-180, 180] se convierte en -45°
        if angle_deg >= -55.0 and angle_deg <= -35.0:
            angle_deg = 135.0  # -45° o 315° -> 135°

        return angle_deg

    def _create_elbow(
        self,
        p_prev,
        p_mid,
        p_next,
        path_idx=None,
        seg_idx=None,
        distribution_type=None,
        p_prev_prev=None,
    ):
        """Crea un codo (ColzeModel o ColzeTDModel) en p_mid, orientado hacia los tramos de la polilínea.

        Args:
            p_prev: Punto anterior al vértice (p_mid)
            p_mid: Punto del vértice donde se coloca el codo
            p_next: Punto siguiente al vértice
            path_idx: Índice del path
            seg_idx: Índice del segmento
            distribution_type: Tipo de distribución (TD o IS)
            p_prev_prev: Punto anterior a p_prev (opcional, para detectar segmentos horizontales previos)
        """
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return []

        # Obtener tipo de distribución del segmento solo si no se proporcionó explícitamente
        if distribution_type is None and path_idx is not None and seg_idx is not None:
            try:
                distribution_type = self._get_segment_distribution_type(
                    path_idx, seg_idx, "IS"
                )
            except Exception:
                distribution_type = "IS"  # Fallback a IS

        # Si aún no tenemos tipo, usar IS por defecto
        if distribution_type is None:
            distribution_type = "IS"

        # Crear modelo de codo según distribución
        if distribution_type == "TD":
            codo = (
                ColzeTDModel(self.build_ele, doc) if ColzeTDModel is not None else None
            )
        else:  # IS
            codo = ColzeModel(self.build_ele, doc) if ColzeModel is not None else None

        if codo is None:
            print("[SO] ERROR: No hay modelo de codo disponible")
            return []
        codo_elems = codo.build()
        if not codo_elems:
            return []

        import math

        dx = p_next.X - p_mid.X
        dy = p_next.Y - p_mid.Y
        dz = p_next.Z - p_mid.Z

        eps = 1e-6
        mat = AllplanGeo.Matrix3D()

        print(f"[ELBOW] dx={dx}, dy={dy}, dz={dz}")

        # ============================================================
        # CASO 1 — Giro vertical (un tramo horizontal + uno vertical)
        #   Soportando:
        #   - seg1 vertical, seg2 horizontal
        #   - seg1 horizontal, seg2 vertical
        # ============================================================

        # Vector del primer tramo (seg1 = p_prev -> p_mid)
        px = p_mid.X - p_prev.X
        py = p_mid.Y - p_prev.Y
        pz = p_mid.Z - p_prev.Z

        # Detectamos quién es vertical
        seg1_vert = abs(px) < eps and abs(py) < eps and abs(pz) > eps
        seg2_vert = abs(dx) < eps and abs(dy) < eps and abs(dz) > eps

        if seg1_vert or seg2_vert:
            print(f"[ELBOW] Vertical turn seg1_vert={seg1_vert}, seg2_vert={seg2_vert}")

            # Normalizamos el caso para tener SIEMPRE:
            #   v_dz = componente vertical del tramo vertical
            #   (hx, hy) = vector horizontal del tramo horizontal en planta
            if seg2_vert:
                # Caso que ya te funcionaba:
                #   seg2 = VERT, seg1 = HORIZ
                v_dz = dz
                hx = px
                hy = py
                print("[ELBOW] vertical: seg2=VERT, seg1=HORIZ")
            else:
                # Nuevo caso:
                #   seg1 = VERT, seg2 = HORIZ
                v_dz = pz
                hx = dx
                hy = dy
                print("[ELBOW] vertical: seg1=VERT, seg2=HORIZ (normalizado)")

            # Vector horizontal en planta
            h_len = math.hypot(hx, hy)
            if h_len < eps:
                print("[ELBOW] vertical: h_vec casi nulo, NO creo codo")
                return []

            # Normalizamos
            hx /= h_len
            hy /= h_len

            # Dirección horizontal y vertical (solo debug)
            h_dir = _dir_from_delta(hx, hy, eps)
            v_dir = "U" if v_dz > 0 else "D"
            print(f"[ELBOW] vertical h_dir={h_dir}, v_dir={v_dir}")

            # -------- MAPA EXPLÍCITO PARA E / W / N / S --------
            # (axis, ang_h, ang_v)
            # axis = 'X' -> rotamos verticalmente alrededor del eje X
            # axis = 'Y' -> rotamos verticalmente alrededor del eje Y
            vertical_map = {
                # Horizontal ESTE (+X)  -> eje X (como ya tenías)
                ("E", "U"): ("X", -math.pi / 2.0, math.pi / 2.0),
                ("E", "D"): ("X", -math.pi / 2.0, -math.pi / 2.0),
                # Horizontal OESTE (W, -X) -> eje X
                ("W", "U"): ("X", math.pi / 2.0, -math.pi / 2.0),
                ("W", "D"): ("X", math.pi / 2.0, math.pi / 2.0),
                # Horizontal NORTE (N, +Y) -> eje Y
                ("N", "U"): ("Y", 0.0, -math.pi / 2.0),
                ("N", "D"): ("Y", 0.0, math.pi / 2.0),
                # Horizontal SUR (S, -Y) -> eje Y
                ("S", "U"): ("Y", math.pi, math.pi / 2.0),
                ("S", "D"): ("Y", math.pi, -math.pi / 2.0),
            }

            if (h_dir, v_dir) in vertical_map:
                axis_code, ang_h, ang_v = vertical_map[(h_dir, v_dir)]
                print(
                    f"[ELBOW] Vertical MAP -> axis={axis_code}, "
                    f"ang_h={math.degrees(ang_h):.1f}°, "
                    f"ang_v={math.degrees(ang_v):.1f}°"
                )
            else:
                # Fallback genérico
                axis_code = "X"
                BASE_PLAN_OFFSET = -math.pi / 2.0  # esquina ("E","S")
                ang_h = math.atan2(hy, hx) + BASE_PLAN_OFFSET
                ang_v = math.pi / 2.0 if v_dz > 0 else -math.pi / 2.0
                print(
                    f"[ELBOW] Vertical GEN -> ang_h={math.degrees(ang_h):.1f}°, "
                    f"ang_v={math.degrees(ang_v):.1f}°"
                )

            # Guardar axis_code y h_dir para uso en la rotación Z adicional
            # (se usan más abajo en la sección de rotación Z adicional)

            # 🔴 Ajuste extra: cuando el tramo vertical es el PRIMERO
            # (seg1 = VERT, seg2 = HORIZ) el codo queda girado 180° en planta
            # respecto al caso base → le sumamos π.
            if seg1_vert and not seg2_vert:
                ang_h += math.pi
                print(
                    f"[ELBOW] seg1_vert=True → añado 180° en planta, "
                    f"ang_h={math.degrees(ang_h):.1f}°"
                )

            # 🚨 ROTACIÓN ADICIONAL: Usar reference_orientation_angle si está definido,
            # o el ángulo del segmento horizontal previo si existe
            # NOTA: Para direcciones N/S (axis=Y), puede necesitar un ajuste diferente que para E/W (axis=X)
            prev_angle_xy = 0.0

            # Prioridad 1: Usar reference_orientation_angle si está definido
            # NOTA: _create_elbow() es método de PolylineScriptObject, así que self ya es el script_object
            ref_orientation = getattr(self, "reference_orientation_angle", None)
            if ref_orientation is not None:
                prev_angle_xy = ref_orientation

                # 🚨 AJUSTE ESPECIAL: Cuando seg1_vert=True (primer tramo vertical) y el segundo tramo horizontal
                # está en dirección Oeste (W) o Sur (S), necesitamos ajustar prev_angle_xy
                # Esto corrige la orientación del codo en estos casos específicos
                if seg1_vert and not seg2_vert:
                    # Calcular el ángulo real del segundo tramo horizontal
                    h_angle = math.atan2(hy, hx)
                    h_angle_deg = math.degrees(h_angle)

                    # Detectar si el segundo tramo va hacia Oeste, Sur o Norte
                    # Oeste: ángulos entre 135° y 180° o entre -180° y -135° -> necesita 180°
                    # Sur con ángulo ~-45°: necesita +90°
                    # Sur con otros ángulos: necesita 180°
                    # Norte con ángulo ~135°: necesita -90°
                    adjustment_angle = 0.0

                    if h_dir == "W":
                        # Normalizar reference_orientation_angle para detectar caso especial del codo 3
                        ref_angle_deg_check = math.degrees(ref_orientation)
                        # Normalizar a [-180, 180]
                        if ref_angle_deg_check > 180.0:
                            ref_angle_deg_check -= 360.0
                        elif ref_angle_deg_check < -180.0:
                            ref_angle_deg_check += 360.0

                        # Guardar el valor original para el ajuste adicional después
                        ref_angle_deg_original_w = ref_angle_deg_check

                        # Mapear 225°/-135° a 45° para usar la misma lógica
                        # 225° y 45° tienen la misma lógica base (225° = 45° + 180°)
                        ref_angle_deg_for_comp = ref_angle_deg_check
                        if (
                            abs(ref_angle_deg_check - 225.0) < 10.0
                            or abs(ref_angle_deg_check + 135.0) < 10.0
                        ):
                            # 225° o -135° -> mapear a 45° para la comparación
                            ref_angle_deg_for_comp = 45.0

                        # Normalizar h_angle también
                        h_angle_normalized_check = h_angle_deg
                        if h_angle_normalized_check > 180.0:
                            h_angle_normalized_check -= 360.0
                        elif h_angle_normalized_check < -180.0:
                            h_angle_normalized_check += 360.0

                        # CASO ESPECIAL: Si ref_orientation está cerca de 45° (o 225° normalizado a 45°) y h_angle cerca de -135° (225°)
                        # (caso del codo 3 para 45°/225°: no aplicar rotación adicional en la lógica base)
                        if (
                            abs(ref_angle_deg_for_comp - 45.0) < 10.0
                            and abs(h_angle_normalized_check + 135.0) < 10.0
                        ):
                            # Codo 3 para 45°/225°: no aplicar rotación adicional (0°) en la lógica base
                            # (la rotación adicional de 180° para 225° se aplicará después)
                            adjustment_angle = 0.0
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° (normalizado={h_angle_normalized_check:.2f}°), "
                                f"ref_angle={ref_angle_deg_check:.2f}° (comparación={ref_angle_deg_for_comp:.2f}°) -> "
                                f"No aplicando ajuste adicional en lógica base (caso codo 3 para 45°/225°)"
                            )
                        elif abs(h_angle_deg) > 135.0 and abs(h_angle_deg) <= 180.0:
                            # Segundo tramo va hacia Oeste (caso normal) -> aplicar 180°
                            adjustment_angle = math.pi
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° -> "
                                f"Aplicando ajuste de 180° a reference_orientation_angle"
                            )
                    elif h_dir == "N":
                        # Segundo tramo va hacia Norte
                        # Normalizar el reference_orientation_angle para comparación (315°/-45° -> 135°)
                        ref_angle_deg = math.degrees(ref_orientation)
                        ref_angle_normalized = self._normalize_ref_angle_for_comparison(
                            ref_orientation
                        )

                        # Normalizar h_angle también
                        h_angle_normalized = h_angle_deg
                        if h_angle_normalized > 180.0:
                            h_angle_normalized -= 360.0
                        elif h_angle_normalized < -180.0:
                            h_angle_normalized += 360.0

                        # Normalizar h_angle también para comparación (315°/-45° -> 135°)
                        h_angle_normalized = self._normalize_ref_angle_for_comparison(
                            h_angle
                        )

                        if (
                            abs(ref_angle_normalized - 135.0) < 10.0
                            or abs(h_angle_normalized - 135.0) < 10.0
                        ):
                            # Ángulo cerca de 135° -> aplicar -90°
                            adjustment_angle = -math.pi / 2.0
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}°, ref_angle={ref_angle_deg:.2f}° -> "
                                f"Aplicando ajuste de -90° a reference_orientation_angle"
                            )
                        else:
                            # Otros ángulos hacia Norte -> aplicar 180°
                            adjustment_angle = math.pi
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}°, ref_angle={ref_angle_deg:.2f}° -> "
                                f"Aplicando ajuste de 180° a reference_orientation_angle"
                            )
                    elif h_dir == "S":
                        # Segundo tramo va hacia Sur
                        # Normalizar reference_orientation_angle para comparación (315°/-45° -> 135°)
                        ref_angle_deg = math.degrees(ref_orientation)
                        ref_angle_normalized = self._normalize_ref_angle_for_comparison(
                            ref_orientation
                        )

                        # Normalizar h_angle para comparación (315°/-45° -> 135°)
                        angle_normalized_for_comp = (
                            self._normalize_ref_angle_for_comparison(h_angle)
                        )

                        # También mantener el ángulo normalizado original para verificaciones adicionales
                        angle_normalized = h_angle_deg
                        if angle_normalized > 180.0:
                            angle_normalized -= 360.0
                        elif angle_normalized < -180.0:
                            angle_normalized += 360.0

                        # CASO ESPECIAL: Si reference_orientation_angle está cerca de 135° (o 315°/-45° normalizado a 135°)
                        # y h_angle cerca de -45° (o 315° normalizado a 135°)
                        # (caso del codo 3: viene después de varios codos) -> aplicar -90°
                        # Ahora funciona igual para ref=135° y ref=315°/-45° porque ambos se normalizan a 135°
                        if (
                            abs(ref_angle_normalized - 135.0) < 10.0
                            and abs(angle_normalized_for_comp - 135.0) < 10.0
                        ):
                            # Codo 3: aplicar -90° (-180° + 90°)
                            adjustment_angle = -math.pi / 2.0
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° (normalizado={angle_normalized:.2f}°), "
                                f"ref_angle={ref_angle_deg:.2f}° (normalizado={ref_angle_normalized:.2f}°) -> "
                                f"Aplicando ajuste de -90° a reference_orientation_angle (caso codo 3)"
                            )
                        # Verificar si h_angle normalizado está cerca de 135° (incluye -45°/315° normalizados)
                        elif abs(angle_normalized_for_comp - 135.0) < 10.0:
                            # Ángulo cerca de -45° o 135° (normalizados a 135°): aplicar +90°
                            adjustment_angle = math.pi / 2.0
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° (normalizado={angle_normalized_for_comp:.2f}°) -> "
                                f"Aplicando ajuste de +90° a reference_orientation_angle"
                            )
                        else:
                            # Otros ángulos hacia Sur -> aplicar 180°
                            adjustment_angle = math.pi
                            print(
                                f"[ELBOW] seg1_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° (normalizado={angle_normalized:.2f}°) -> "
                                f"Aplicando ajuste de 180° a reference_orientation_angle"
                            )

                    # Aplicar adjustment_angle si no es cero
                    if abs(adjustment_angle) > 1e-6:
                        prev_angle_xy += adjustment_angle
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi

                    # 🚨 AJUSTE ADICIONAL: Si ref_orientation es 315°/-45° o 225°, añadir 180° adicional
                    # Este ajuste se aplica siempre, incluso cuando adjustment_angle = 0.0 (caso del codo 3 para 45°/225°)
                    ref_angle_deg_original = math.degrees(ref_orientation)
                    # Normalizar a [-180, 180]
                    if ref_angle_deg_original > 180.0:
                        ref_angle_deg_original -= 360.0
                    elif ref_angle_deg_original < -180.0:
                        ref_angle_deg_original += 360.0

                    # Si está cerca de -45° o 315°, añadir 180° adicional
                    # 315°/-45° usa la misma lógica que 135° pero con +180° adicional
                    if abs(ref_angle_deg_original + 45.0) < 10.0:
                        prev_angle_xy += math.pi  # +180° adicional para 315°/-45°
                        # Normalizar nuevamente
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] ref_orientation={ref_angle_deg_original:.2f}° (-45°/315°) -> Añadiendo 180° adicional -> "
                            f"prev_angle_xy={math.degrees(prev_angle_xy):.2f}°"
                        )
                    # Si está cerca de 225° o -135° (equivalente a 225° cuando se normaliza), añadir 180° adicional
                    # 225°/-135° usa la misma lógica base que 45°, pero con +180° adicional
                    # Nota: 225° normalizado a [-180, 180] = -135°
                    elif (
                        abs(ref_angle_deg_original - 225.0) < 10.0
                        or abs(ref_angle_deg_original + 135.0) < 10.0
                        or (
                            ref_angle_deg_original > 220.0
                            and ref_angle_deg_original < 230.0
                        )
                        or (
                            ref_angle_deg_original > -145.0
                            and ref_angle_deg_original < -125.0
                        )
                    ):
                        prev_angle_xy += math.pi  # +180° adicional para 225°/-135°
                        # Normalizar nuevamente
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] ref_orientation={ref_angle_deg_original:.2f}° (225°/-135°) -> Añadiendo 180° adicional -> "
                            f"prev_angle_xy={math.degrees(prev_angle_xy):.2f}°"
                        )
                elif seg2_vert and not seg1_vert:
                    # 🚨 AJUSTE ESPECIAL: Cuando seg2_vert=True (segundo tramo vertical) y el primer tramo horizontal
                    # está en dirección Norte (N), necesitamos añadir -90° a prev_angle_xy
                    # Esto corrige la orientación del codo en estos casos específicos
                    print(
                        f"[ELBOW] DEBUG: seg2_vert=True, seg1_vert=False, h_dir={h_dir}, entrando en bloque de ajuste para seg2_vert"
                    )
                    # Calcular el ángulo real del primer tramo horizontal
                    h_angle = math.atan2(hy, hx)
                    h_angle_deg = math.degrees(h_angle)

                    # Verificar si el primer tramo horizontal va hacia Norte
                    if h_dir == "N":
                        # Normalizar reference_orientation_angle para comparación (315°/-45° -> 135°)
                        ref_angle_deg = math.degrees(ref_orientation)
                        angle_normalized = self._normalize_ref_angle_for_comparison(
                            ref_orientation
                        )

                        # Normalizar h_angle también para comparación (315°/-45° -> 135°)
                        h_angle_normalized = self._normalize_ref_angle_for_comparison(
                            h_angle
                        )

                        # Si está cerca de 135° (incluye 315°/-45° normalizados), aplicar -90°
                        if (
                            abs(angle_normalized - 135.0) < 10.0
                            or abs(h_angle_normalized - 135.0) < 10.0
                        ):
                            prev_angle_xy -= math.pi / 2.0  # -90°
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] seg2_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}°, ref_angle={ref_angle_deg:.2f}° -> "
                                f"Aplicando ajuste de -90° a reference_orientation_angle"
                            )
                    elif h_dir == "S":
                        # Cuando seg2_vert=True y h_dir=S, aplicar -90°
                        prev_angle_xy -= math.pi / 2.0  # -90°
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] seg2_vert=True, h_dir={h_dir}, h_angle={h_angle_deg:.2f}° -> "
                            f"Aplicando ajuste de -90° a reference_orientation_angle"
                        )

                    # 🚨 AJUSTE ADICIONAL: Si ref_orientation es 315°/-45° o 225°, añadir 180° adicional (igual que en seg1_vert)
                    ref_angle_deg_original = math.degrees(ref_orientation)
                    # Normalizar a [-180, 180]
                    if ref_angle_deg_original > 180.0:
                        ref_angle_deg_original -= 360.0
                    elif ref_angle_deg_original < -180.0:
                        ref_angle_deg_original += 360.0

                    # Si está cerca de -45° o 315°, añadir 180° adicional
                    # 315°/-45° usa la misma lógica que 135° pero con +180° adicional
                    if abs(ref_angle_deg_original + 45.0) < 10.0:
                        prev_angle_xy += math.pi  # +180° adicional para 315°/-45°
                        # Normalizar nuevamente
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] seg2_vert=True, ref_orientation={ref_angle_deg_original:.2f}° (-45°/315°) -> "
                            f"Añadiendo 180° adicional -> prev_angle_xy={math.degrees(prev_angle_xy):.2f}°"
                        )
                    # Si está cerca de 225° o -135° (equivalente a 225° cuando se normaliza), añadir 180° adicional
                    # 225°/-135° usa la misma lógica base que 45°, pero con +180° adicional
                    # Nota: 225° normalizado a [-180, 180] = -135°
                    elif (
                        abs(ref_angle_deg_original - 225.0) < 10.0
                        or abs(ref_angle_deg_original + 135.0) < 10.0
                        or (
                            ref_angle_deg_original > 220.0
                            and ref_angle_deg_original < 230.0
                        )
                        or (
                            ref_angle_deg_original > -145.0
                            and ref_angle_deg_original < -125.0
                        )
                    ):
                        prev_angle_xy += math.pi  # +180° adicional para 225°/-135°
                        # Normalizar nuevamente
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] seg2_vert=True, ref_orientation={ref_angle_deg_original:.2f}° (225°/-135°) -> "
                            f"Añadiendo 180° adicional -> prev_angle_xy={math.degrees(prev_angle_xy):.2f}°"
                        )

                print(
                    f"[ELBOW] Usando orientación 3D de referencia: {math.degrees(ref_orientation):.2f}° -> "
                    f"prev_angle_xy={math.degrees(prev_angle_xy):.2f}° en XY"
                )
            elif seg2_vert:
                # Prioridad 2: seg1 es horizontal (p_prev -> p_mid), usar su ángulo directamente
                # El vector horizontal ya está normalizado en (hx, hy)
                prev_angle_xy = math.atan2(hy, hx)

                # Normalizar el ángulo a [-π, π] primero para comparaciones consistentes
                while prev_angle_xy > math.pi:
                    prev_angle_xy -= 2 * math.pi
                while prev_angle_xy < -math.pi:
                    prev_angle_xy += 2 * math.pi

                # Guardar el ángulo original normalizado para comparación
                original_angle_normalized = prev_angle_xy

                # Determinar si necesitamos invertir el signo según el contexto
                # Si NO hay p_prev_prev (es el primer vértice) o viene directamente de otro segmento horizontal,
                # NO invertir. Si viene después de un segmento vertical, SÍ invertir.
                # EXCEPCIÓN: Si el ángulo normalizado es el mismo que el del primer vértice (44.98°),
                # no invertir aunque venga después de vertical (caso del codo 5 que es igual al codo 1)
                should_invert = False  # Por defecto NO invertir
                if p_prev_prev is not None:
                    # Verificar si p_prev_prev -> p_prev era vertical (no horizontal)
                    prev_prev_dx = p_prev.X - p_prev_prev.X
                    prev_prev_dy = p_prev.Y - p_prev_prev.Y
                    prev_prev_dz = p_prev.Z - p_prev_prev.Z
                    prev_prev_length = math.sqrt(
                        prev_prev_dx * prev_prev_dx
                        + prev_prev_dy * prev_prev_dy
                        + prev_prev_dz * prev_prev_dz
                    )
                    if prev_prev_length > 1e-6:
                        # Si el segmento previo previo es vertical, entonces SÍ invertir
                        if (
                            abs(prev_prev_dx) < eps
                            and abs(prev_prev_dy) < eps
                            and abs(prev_prev_dz) > eps
                        ):
                            # EXCEPCIÓN: Si el ángulo normalizado es aproximadamente 44.98° (E/W) o 134.98° (N/S),
                            # es el mismo caso que el primer vértice, NO invertir
                            # NOTA: -45.02° NO es el primer vértice, así que debe invertir normalmente
                            angle_deg = math.degrees(original_angle_normalized)
                            if (
                                abs(
                                    original_angle_normalized
                                    - (44.98 * math.pi / 180.0)
                                )
                                < 0.1
                            ) or (axis_code == "Y" and abs(angle_deg - 134.98) < 5.0):
                                should_invert = False
                                print(
                                    f"[ELBOW] Segmento horizontal viene después de segmento vertical, "
                                    f"pero ángulo es igual al primer vértice ({angle_deg:.2f}°), NO invirtiendo signo"
                                )
                            else:
                                should_invert = True
                                print(
                                    f"[ELBOW] Segmento horizontal viene después de segmento vertical, "
                                    f"invirtiendo signo"
                                )
                        else:
                            print(
                                f"[ELBOW] Segmento horizontal viene directamente de otro horizontal, "
                                f"NO invirtiendo signo"
                            )
                else:
                    # CASO ESPECIAL: Para direcciones N/S con ángulo 134.98°, NO invertir
                    # (similar a cómo E/W con 44.98° no invierte en el primer vértice)
                    angle_deg = math.degrees(original_angle_normalized)
                    # Para N/S, el ángulo 134.98° es equivalente al 44.98° de E/W
                    # Ambos deben tratarse igual: NO invertir en el primer vértice
                    if abs(angle_deg - 134.98) < 5.0 or abs(angle_deg - (-45.02)) < 5.0:
                        # Para estos ángulos en N/S, NO invertir (igual que E/W con 44.98°)
                        should_invert = False
                        print(
                            f"[ELBOW] Primer vértice con dirección N/S y ángulo {angle_deg:.2f}°, "
                            f"NO invirtiendo signo (equivalente a E/W con 44.98°)"
                        )
                    else:
                        print(
                            f"[ELBOW] Primer vértice (no hay p_prev_prev), NO invirtiendo signo"
                        )

                if should_invert:
                    # Verificar primero si es una dirección cardinal (múltiplo de 90°)
                    angle_deg = math.degrees(original_angle_normalized)
                    is_cardinal = (
                        abs(abs(angle_deg) - 90.0) < 5.0  # ±90°
                        or abs(abs(angle_deg) - 180.0) < 5.0  # ±180°
                        or abs(abs(angle_deg)) < 5.0  # 0°
                    )

                    if is_cardinal:
                        # Para direcciones cardinales, NO aplicar rotación Z adicional
                        # Establecer prev_angle_xy = 0 para que no se cree mat_z_rot
                        prev_angle_xy = 0.0
                        print(
                            f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                            f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección cardinal), "
                            f"NO aplicando rotación Z adicional"
                        )
                    else:
                        # Cuando viene después de segmento vertical, añadir 180° en lugar de invertir
                        prev_angle_xy += math.pi
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi

                        # CASO ESPECIAL: Para direcciones N/S (axis=Y), aplicar ajuste de -90° después de invertir
                        # (similar al primer vértice)
                        if axis_code == "Y":
                            # Para N/S, restar 90° al ángulo después de invertir
                            prev_angle_xy -= math.pi / 2.0
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección N/S), aplicando rotación Z adicional "
                                f"con +180° y luego -90°: {math.degrees(prev_angle_xy):.2f}°"
                            )
                        else:
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY, aplicando rotación Z adicional "
                                f"con +180°: {math.degrees(prev_angle_xy):.2f}°"
                            )
                else:
                    # Verificar si es una dirección cardinal (múltiplo de 90°: 0°, 90°, -90°, 180°, -180°)
                    angle_deg = math.degrees(original_angle_normalized)
                    is_cardinal = (
                        abs(abs(angle_deg) - 90.0) < 5.0  # ±90°
                        or abs(abs(angle_deg) - 180.0) < 5.0  # ±180°
                        or abs(abs(angle_deg)) < 5.0  # 0°
                    )

                    if is_cardinal:
                        # Para direcciones cardinales, NO aplicar rotación Z adicional
                        # Establecer prev_angle_xy = 0 para que no se cree mat_z_rot
                        prev_angle_xy = 0.0
                        print(
                            f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                            f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección cardinal), "
                            f"NO aplicando rotación Z adicional"
                        )
                    elif axis_code == "Y":
                        # CASO ESPECIAL: Solo para direcciones N/S NO cardinales, aplicar ajuste según el ángulo
                        # - Si el ángulo es 134.98°: restar 90° → 44.98°
                        # - Si el ángulo es -45.02°: añadir 90° → 44.98° (sentido contrario)
                        if abs(angle_deg - 134.98) < 5.0:
                            # Para 134.98°, restar 90°
                            prev_angle_xy -= math.pi / 2.0
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección N/S a 45°), "
                                f"aplicando rotación Z adicional con -90°: {math.degrees(prev_angle_xy):.2f}°"
                            )
                        elif abs(angle_deg - (-45.02)) < 5.0:
                            # Para -45.02°, añadir 90° (sentido contrario)
                            prev_angle_xy += math.pi / 2.0
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección N/S a 45°), "
                                f"aplicando rotación Z adicional con +90°: {math.degrees(prev_angle_xy):.2f}°"
                            )
                        else:
                            # Por defecto para N/S no cardinales, restar 90°
                            prev_angle_xy -= math.pi / 2.0
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección N/S no cardinal), "
                                f"aplicando rotación Z adicional con -90°: {math.degrees(prev_angle_xy):.2f}°"
                            )
                    else:
                        # Para E/W no cardinales, aplicar ajuste según el ángulo
                        # Si el ángulo es -135.02° (opuesto a 44.98°), añadir 180° para que apunte en dirección opuesta
                        # Si el ángulo es 44.98°, no aplicar ajuste adicional (ya funciona bien)
                        if abs(angle_deg - (-135.02)) < 5.0:
                            # Para -135.02°, añadir 180° para apuntar en dirección opuesta (44.98°)
                            prev_angle_xy += math.pi
                            # Normalizar el ángulo a [-π, π]
                            while prev_angle_xy > math.pi:
                                prev_angle_xy -= 2 * math.pi
                            while prev_angle_xy < -math.pi:
                                prev_angle_xy += 2 * math.pi
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(original_angle_normalized):.2f}° en XY (dirección E/W), aplicando rotación Z adicional "
                                f"con +180° para apuntar en dirección opuesta: {math.degrees(prev_angle_xy):.2f}°"
                            )
                        else:
                            # Para otros ángulos E/W no cardinales (como 44.98°), no aplicar ajuste adicional
                            print(
                                f"[ELBOW] Segmento horizontal que llega al codo tiene ángulo "
                                f"{math.degrees(prev_angle_xy):.2f}° en XY (dirección E/W), aplicando rotación Z adicional"
                            )
            elif seg1_vert:
                # seg2 es horizontal (p_mid -> p_next), usar su ángulo
                # El vector horizontal ya está normalizado en (hx, hy) después de la normalización
                prev_angle_xy = math.atan2(hy, hx)

                # Normalizar el ángulo inicial a [-π, π]
                while prev_angle_xy > math.pi:
                    prev_angle_xy -= 2 * math.pi
                while prev_angle_xy < -math.pi:
                    prev_angle_xy += 2 * math.pi

                # Guardar el ángulo original para usar en la lógica de ajuste
                original_angle = prev_angle_xy
                angle_deg = math.degrees(original_angle)

                # ============================================================
                # CONDICIONAL: Detectar si el tubo vertical viene de una Te diagonal
                # Si el path_idx está en branch_tube_rotation_needed, el tubo vertical
                # ya tiene una rotación aplicada (45°), y el codo debe orientarse
                # según el ángulo del segmento horizontal directamente
                # ============================================================
                branch_rotation_needed = getattr(
                    self, "branch_tube_rotation_needed", {}
                )
                comes_from_diagonal_te = (
                    path_idx is not None and path_idx in branch_rotation_needed
                )

                # Debug: imprimir información sobre branch_tube_rotation_needed
                if branch_rotation_needed:
                    print(
                        f"[ELBOW] 🔍 DEBUG: branch_tube_rotation_needed contiene: {branch_rotation_needed}, "
                        f"path_idx={path_idx}, comes_from_diagonal_te={comes_from_diagonal_te}"
                    )
                else:
                    # También imprimir cuando NO hay branch_rotation_needed para ayudar a depurar
                    print(
                        f"[ELBOW] 🔍 DEBUG: branch_tube_rotation_needed está vacío o no existe, "
                        f"path_idx={path_idx}, comes_from_diagonal_te={comes_from_diagonal_te}"
                    )

                if comes_from_diagonal_te:
                    # El tubo vertical viene de una Te diagonal
                    # Usar la misma lógica que para casos normales (vertical a horizontal)
                    # Se comporta exactamente igual que un codo normal: solo usar el ángulo del segmento horizontal
                    stored_angle = branch_rotation_needed[path_idx]
                    branch_direction_dict = getattr(self, "branch_tube_direction", {})
                    branch_direction = branch_direction_dict.get(path_idx, "+Z")

                    # Normalizar ángulos para comparación
                    stored_angle_deg = math.degrees(stored_angle)
                    horizontal_angle_deg = math.degrees(prev_angle_xy)

                    # Normalizar stored_angle a rango -180 a 180
                    stored_angle_deg_normalized = stored_angle_deg
                    while stored_angle_deg_normalized > 180:
                        stored_angle_deg_normalized -= 360
                    while stored_angle_deg_normalized < -180:
                        stored_angle_deg_normalized += 360

                    # Normalizar horizontal_angle a rango -180 a 180
                    horizontal_angle_deg_normalized = horizontal_angle_deg
                    while horizontal_angle_deg_normalized > 180:
                        horizontal_angle_deg_normalized -= 360
                    while horizontal_angle_deg_normalized < -180:
                        horizontal_angle_deg_normalized += 360

                    # CASO ESPECIAL 1: Cuando stored_angle está cerca de 45° y horizontal_angle está cerca de -135° (opuestos, diferencia de ~180°)
                    # y axis_code es X (E/W), el codo apunta en sentido contrario, necesitamos aplicar +180°
                    if (
                        abs(stored_angle_deg_normalized - 45.0) < 10.0
                        and abs(horizontal_angle_deg_normalized - (-135.0)) < 10.0
                        and axis_code == "X"
                    ):
                        # Aplicar ajuste de +180° para corregir la orientación
                        prev_angle_xy += math.pi
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] ✅ CASO ESPECIAL 1: Te diagonal con stored_angle={stored_angle_deg_normalized:.1f}° y "
                            f"horizontal_angle={horizontal_angle_deg_normalized:.1f}° (opuestos, diferencia ~180°, axis=X). "
                            f"Aplicando ajuste de +180°: {math.degrees(prev_angle_xy):.2f}°"
                        )
                        # Actualizar original_angle después del ajuste
                        original_angle = prev_angle_xy
                        angle_deg = math.degrees(original_angle)
                    # CASO ESPECIAL 2: Cuando stored_angle está cerca de -135° y horizontal_angle está cerca de -135° (similares)
                    # y axis_code es X (E/W), el codo apunta en sentido contrario, necesitamos aplicar +180°
                    elif (
                        abs(stored_angle_deg_normalized - (-135.0)) < 10.0
                        and abs(horizontal_angle_deg_normalized - (-135.0)) < 10.0
                        and axis_code == "X"
                    ):
                        # Aplicar ajuste de +180° para corregir la orientación
                        prev_angle_xy += math.pi
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] ✅ CASO ESPECIAL 2: Te diagonal con stored_angle={stored_angle_deg_normalized:.1f}° y "
                            f"horizontal_angle={horizontal_angle_deg_normalized:.1f}° (similares, ambos ~-135°, axis=X). "
                            f"Aplicando ajuste de +180°: {math.degrees(prev_angle_xy):.2f}°"
                        )
                        # Actualizar original_angle después del ajuste
                        original_angle = prev_angle_xy
                        angle_deg = math.degrees(original_angle)

                    # prev_angle_xy ya está normalizado arriba y original_angle ya está calculado
                    # No aplicar ajustes especiales - usar lógica normal de orientación
                    should_add_180 = False
                    print(
                        f"[ELBOW] ✅ Tubo vertical (path={path_idx}) viene de Te diagonal "
                        f"(ángulo almacenado: {math.degrees(stored_angle):.1f}°, dirección: {branch_direction}). "
                        f"Usando lógica normal de orientación vertical a horizontal igual que casos normales, "
                        f"con ángulo del segmento horizontal: {math.degrees(prev_angle_xy):.2f}°"
                    )
                    # La lógica de ajuste según axis_code se aplicará más abajo (igual que casos normales)
                else:
                    # Determinar si necesitamos un ajuste diferente según el contexto
                    # El segmento que llega al codo es vertical (p_prev -> p_mid)
                    # Caso especial: Codo 2 - viene directamente después de un segmento vertical (del codo 1)
                    # En este caso, SÍ añadir 180°
                    # Caso general: Si p_prev_prev existe y el segmento p_prev_prev -> p_prev es horizontal,
                    # entonces el vertical viene después de un horizontal (que viene después de otro segmento),
                    # NO añadir 180°
                    should_add_180 = True  # Por defecto añadir 180°
                    if p_prev_prev is not None:
                        # Verificar si p_prev_prev -> p_prev era horizontal
                        prev_prev_dx = p_prev.X - p_prev_prev.X
                        prev_prev_dy = p_prev.Y - p_prev_prev.Y
                        prev_prev_dz = p_prev.Z - p_prev_prev.Z
                        prev_prev_length = math.sqrt(
                            prev_prev_dx * prev_prev_dx
                            + prev_prev_dy * prev_prev_dy
                            + prev_prev_dz * prev_prev_dz
                        )
                        if prev_prev_length > 1e-6:
                            # Si el segmento previo previo es horizontal, entonces el vertical viene después
                            # de un horizontal que a su vez viene después de otro segmento
                            if abs(prev_prev_dz) < 1e-6:
                                # CASO ESPECIAL: Codo 2 - verificar si el segmento previo previo viene directamente
                                # de un segmento horizontal inicial (no hay p_prev_prev_prev o es el primer segmento)
                                # En este caso, el codo 2 viene directamente después de un vertical (del codo 1),
                                # así que SÍ añadir 180°
                                # Para el codo 4, el segmento previo previo viene después de otro segmento,
                                # así que NO añadir 180°
                                # La diferencia es que el codo 2 es el segundo codo (i=2), mientras que el codo 4 es el cuarto (i=4)
                                # Podemos detectar esto verificando si hay más contexto o simplemente
                                # asumir que si viene después de horizontal, NO añadir 180° (excepto para codo 2)
                                # Pero el codo 2 también tiene p_prev_prev horizontal...
                                # Necesitamos una forma de distinguir: el codo 2 viene después de un codo seg2_vert,
                                # mientras que el codo 4 viene después de un codo seg2_vert que a su vez viene después de otro codo
                                # La clave es: si el segmento previo previo es horizontal Y viene directamente del inicio
                                # (no hay más contexto), entonces es el codo 2 y SÍ añadir 180°
                                # Si el segmento previo previo es horizontal pero hay más contexto, entonces es el codo 4 y NO añadir 180°
                                # Por ahora, para no romper el codo 4, asumimos que si viene después de horizontal, NO añadir 180°
                                # Pero necesitamos una excepción para el codo 2
                                # Solución: verificar si el segmento previo previo viene directamente de un segmento horizontal inicial
                                # Si es así, es el codo 2 y SÍ añadir 180°
                                # Si no, es el codo 4 y NO añadir 180°
                                # Pero no tenemos acceso a p_prev_prev_prev...
                                # Alternativa: el codo 2 siempre necesita añadir 180°, así que forzamos eso
                                # cuando el segmento previo previo es horizontal Y el ángulo del segmento horizontal
                                # que sale es -135.02° (que es característico del codo 2)
                                # Mejor: simplemente forzar que el codo 2 siempre añada 180°
                                # El codo 2 tiene ángulo -135.02° antes de añadir 180°, y 44.98° después
                                # El codo 4 tiene ángulo 44.98° antes de añadir 180°, y -135.02° después
                                # Podemos usar el ángulo para distinguir, pero es frágil
                                # Mejor solución: el codo 2 viene directamente después del primer codo (seg2_vert),
                                # mientras que el codo 4 viene después del tercer codo (seg2_vert) que a su vez viene después del segundo codo (seg1_vert)
                                # La diferencia clave: el codo 2 es el segundo vértice, el codo 4 es el cuarto vértice
                                # Pero no tenemos acceso al índice del vértice directamente...
                                # Solución más simple: si el ángulo original es -135.02° (aproximadamente), es el codo 2 y SÍ añadir 180°
                                # Si el ángulo original es 44.98° (aproximadamente), es el codo 4 y NO añadir 180°
                                # CASO ESPECIAL: Codo 2 - tiene ángulo -135.02° (aproximadamente -2.36 rad)
                                # El codo 4 tiene ángulo 44.98° (aproximadamente 0.78 rad)
                                # Usamos el ángulo para distinguir entre codo 2 y codo 4
                                angle_deg = math.degrees(prev_angle_xy)
                                if (
                                    abs(angle_deg - (-135.0)) < 5.0
                                ):  # Aproximadamente -135°
                                    # Es el codo 2, SÍ añadir 180°
                                    should_add_180 = True
                                    print(
                                        f"[ELBOW] Codo 2 detectado (ángulo {angle_deg:.2f}°), añadiendo 180°"
                                    )
                                else:
                                    # Es el codo 4, NO añadir 180°
                                    should_add_180 = False
                                    print(
                                        f"[ELBOW] Codo 4 detectado (ángulo {angle_deg:.2f}°), NO añadiendo 180°"
                                    )

                # Aplicar lógica de orientación según axis_code (N/S vs E/W)
                # Esta lógica se aplica tanto para casos normales como para Tees diagonales

                # Verificar si es una dirección cardinal (múltiplo de 90°)
                is_cardinal = (
                    abs(abs(angle_deg) - 90.0) < 5.0  # ±90°
                    or abs(abs(angle_deg) - 180.0) < 5.0  # ±180°
                    or abs(abs(angle_deg)) < 5.0  # 0°
                )

                # Verificar si es realmente el codo 4: debe tener ángulo 44.98° o ~90° (cardinal)
                # y haber sido detectado como codo 4 (not should_add_180) pero con ángulo específico
                is_really_elbow_4 = (
                    axis_code == "Y"
                    and not should_add_180
                    and (
                        abs(angle_deg - 44.98) < 5.0  # Codo 4 a 45°
                        or abs(abs(angle_deg) - 90.0) < 5.0  # Codo 4 cardinal
                    )
                )

                # Solo aplicar ajustes de should_add_180 cuando NO viene de Te diagonal
                if not comes_from_diagonal_te:
                    if is_cardinal and not is_really_elbow_4:
                        # Para direcciones cardinales (excepto codo 4 real), NO aplicar rotación Z adicional
                        # Establecer prev_angle_xy = 0 para que no se cree mat_z_rot
                        prev_angle_xy = 0.0
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección cardinal), "
                            f"NO aplicando rotación Z adicional"
                        )
                    elif should_add_180:
                        # Añadir 180° solo si corresponde (porque el codo ya tiene ajuste de 180° en ang_h)
                        # SOLO si NO es cardinal (para no sobrescribir el prev_angle_xy = 0.0 de arriba)
                        prev_angle_xy += math.pi
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (no cardinal), aplicando rotación Z adicional "
                            f"con +180°: {math.degrees(prev_angle_xy):.2f}°"
                        )

                # CASO ESPECIAL: Para direcciones N/S (axis=Y) en seg1_vert, aplicar ajuste
                # Esta lógica se aplica tanto para casos normales como para Tees diagonales
                # Para seg1_vert con N/S:
                # - Si el ángulo es -45.02° (Codo 2 equivalente), añadir 90° → 44.98°
                # - Si el ángulo es 134.98° (Codo 4 equivalente), restar 90° → 44.98°
                # - Si el ángulo es 44.98° (Codo 4 a 45°), no aplicar ajuste adicional
                # - Si el ángulo es ~90° (Codo 4 cardinal), NO aplicar rotación (prev_angle_xy = 0)
                if axis_code == "Y" and not should_add_180:
                    # Si el ángulo es aproximadamente 134.98° (Codo 4), restar 90°
                    # Si el ángulo es aproximadamente -45.02° (Codo 2), añadir 90°
                    # Si el ángulo es aproximadamente 44.98° (Codo 4 a 45°), no aplicar ajuste
                    # Si el ángulo es aproximadamente 90° (Codo 4 cardinal), NO aplicar rotación
                    if abs(angle_deg - 134.98) < 5.0:
                        # Codo 4 equivalente: restar 90°
                        prev_angle_xy -= math.pi / 2.0
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección N/S a 45°, Codo 4), aplicando rotación Z adicional "
                            f"con -90°: {math.degrees(prev_angle_xy):.2f}°"
                        )
                    elif abs(angle_deg - (-45.02)) < 5.0:
                        # Codo 2 equivalente: añadir 90°
                        prev_angle_xy += math.pi / 2.0
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección N/S a 45°, Codo 2), aplicando rotación Z adicional "
                            f"con +90°: {math.degrees(prev_angle_xy):.2f}°"
                        )
                    elif abs(angle_deg - 44.98) < 5.0:
                        # Codo 4 a 45°: no aplicar ajuste adicional (ya está correcto)
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección N/S a 45°, Codo 4), "
                            f"NO aplicando rotación Z adicional (ya correcto)"
                        )
                    elif abs(abs(angle_deg) - 90.0) < 5.0:
                        # Codo 4 cardinal (~90°): NO aplicar rotación (igual que otros cardinales)
                        prev_angle_xy = 0.0
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección N/S cardinal, Codo 4), "
                            f"NO aplicando rotación Z adicional"
                        )
                    else:
                        # Por defecto para N/S no cardinales, añadir 90°
                        prev_angle_xy += math.pi / 2.0
                        # Normalizar el ángulo a [-π, π]
                        while prev_angle_xy > math.pi:
                            prev_angle_xy -= 2 * math.pi
                        while prev_angle_xy < -math.pi:
                            prev_angle_xy += 2 * math.pi
                        print(
                            f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                            f"{math.degrees(original_angle):.2f}° en XY (dirección N/S no cardinal), aplicando rotación Z adicional "
                            f"con +90°: {math.degrees(prev_angle_xy):.2f}°"
                        )
                else:
                    # Para E/W (axis_code != "Y")
                    # Esta lógica se aplica tanto para casos normales como para Tees diagonales
                    # NOTA: Los ajustes de should_add_180 ya se aplicaron arriba cuando not comes_from_diagonal_te
                    # Aquí solo mostramos el estado final
                    print(
                        f"[ELBOW] Segmento horizontal que sale del codo tiene ángulo "
                        f"{math.degrees(original_angle):.2f}° en XY (dirección E/W), rotación Z adicional final: "
                        f"{math.degrees(prev_angle_xy):.2f}°"
                    )

            # Aplicar primero la rotación sobre el eje Z (si hay segmento horizontal)
            mat_z_rot = None
            if abs(prev_angle_xy) > 1e-6:
                axis_z_prev = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0),
                    AllplanGeo.Point3D(0, 0, 1),
                )
                mat_z_rot = AllplanGeo.Matrix3D()
                mat_z_rot.SetRotation(axis_z_prev, AllplanGeo.Angle(prev_angle_xy))

            # Rotación vertical alrededor de X o Y según el caso
            if axis_code == "Y":
                axis_vert = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
                )
            else:
                # default / eje X (como tenías antes)
                axis_vert = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(-1, 0, 0)
                )

            mat_v = AllplanGeo.Matrix3D()
            mat_v.SetRotation(axis_vert, AllplanGeo.Angle(ang_v))

            # Rotación en planta Rz(ang_h) alrededor de eje Z global
            axis_z = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
            )
            mat_h = AllplanGeo.Matrix3D()
            mat_h.SetRotation(axis_z, AllplanGeo.Angle(ang_h))

            # Composición: aplicar rotaciones en el orden correcto
            # Si hay rotación Z adicional, aplicarla primero (como en el tubo), luego vertical, luego horizontal
            if mat_z_rot is not None:
                # Orden: primero rotación Z adicional, luego vertical, luego horizontal
                # mat_h * mat_v * mat_z_rot aplica primero mat_z_rot, luego mat_v, luego mat_h
                mat = mat_h * mat_v * mat_z_rot
                print(
                    f"[ELBOW] Aplicando rotación Z adicional de {math.degrees(prev_angle_xy):.2f}° "
                    f"antes de rotaciones vertical y horizontal (igual que en tubo)"
                )
            else:
                # Composición normal: primero levantamos el codo, luego lo orientamos en planta
                mat = mat_h * mat_v

            # Traslación al vértice
            mat.SetTranslation(AllplanGeo.Vector3D(p_mid.X, p_mid.Y, p_mid.Z))

        # ============================================================
        # CASO 2 — Giro horizontal (XY, XZ o YZ, independiente del sentido)
        # ============================================================
        else:
            # Detectar en qué plano está la polilínea
            # Calculamos las componentes de cambio en cada eje
            d_prev_x = p_mid.X - p_prev.X
            d_prev_y = p_mid.Y - p_prev.Y
            d_prev_z = p_mid.Z - p_prev.Z
            d_next_x = p_next.X - p_mid.X
            d_next_y = p_next.Y - p_mid.Y
            d_next_z = p_next.Z - p_mid.Z

            # Detectar el plano: XY, XZ o YZ
            prev_y_magnitude = abs(d_prev_y)
            next_y_magnitude = abs(d_next_y)
            prev_x_magnitude = abs(d_prev_x)
            next_x_magnitude = abs(d_next_x)
            prev_z_magnitude = abs(d_prev_z)
            next_z_magnitude = abs(d_next_z)

            # Detectar si está en el plano XZ (Y constante o casi constante)
            in_xz_plane = (prev_y_magnitude < eps and next_y_magnitude < eps) or (
                prev_y_magnitude < 0.1 * max(abs(d_prev_x), abs(d_prev_z), eps)
                and next_y_magnitude < 0.1 * max(abs(d_next_x), abs(d_next_z), eps)
            )

            # Detectar si está en el plano YZ (X constante o casi constante)
            in_yz_plane = (prev_x_magnitude < eps and next_x_magnitude < eps) or (
                prev_x_magnitude < 0.1 * max(abs(d_prev_y), abs(d_prev_z), eps)
                and next_x_magnitude < 0.1 * max(abs(d_next_y), abs(d_next_z), eps)
            )

            if in_xz_plane:
                # ============================================================
                # CASO 2A — Giro en el plano XZ
                # ============================================================
                print("[ELBOW] Detectado giro en plano XZ")

                # Direcciones en el plano XZ
                # Calcular los ángulos reales de ambos vectores respecto al eje X
                angle_prev = math.atan2(
                    d_prev_z, d_prev_x
                )  # Ángulo del tramo previo en XZ
                angle_next = math.atan2(
                    d_next_z, d_next_x
                )  # Ángulo del tramo siguiente en XZ

                # Producto cruzado en XZ: signo indica si el giro es horario o antihorario
                cross = d_prev_x * d_next_z - d_prev_z * d_next_x

                # Misma lógica que en XY
                if abs(cross) < 1e-6:
                    angle = angle_next
                    needs_mirror = False
                elif cross < 0:
                    angle = angle_next
                    needs_mirror = False
                else:
                    angle = angle_prev
                    needs_mirror = True

                # Normalizar el ángulo
                while angle < 0:
                    angle += 2 * math.pi
                while angle >= 2 * math.pi:
                    angle -= 2 * math.pi

                print(
                    f"[ELBOW] XZ: d_prev=({d_prev_x:.2f}, {d_prev_z:.2f}), "
                    f"d_next=({d_next_x:.2f}, {d_next_z:.2f})"
                )
                print(
                    f"[ELBOW] XZ: angle_prev={math.degrees(angle_prev):.1f}°, "
                    f"angle_next={math.degrees(angle_next):.1f}°, "
                    f"cross={cross:.4f}, final={math.degrees(angle):.1f}°, mirror={needs_mirror}"
                )

                # Para el plano XZ, rotamos alrededor del eje Y
                # Primero rotamos el modelo del plano XY al plano XZ (rotación preparatoria alrededor de X)
                axis_x = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                )
                mat_prep = AllplanGeo.Matrix3D()
                mat_prep.SetRotation(axis_x, AllplanGeo.Angle(-math.pi / 2.0))

                # Rotación de orientación alrededor del eje Y
                axis_y = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
                )
                mat_rot = AllplanGeo.Matrix3D()
                mat_rot.SetRotation(axis_y, AllplanGeo.Angle(angle))

                # Combinar: primero preparación (XY->XZ), luego orientación
                mat = mat_rot * mat_prep

                # Si necesita reflejo, aplicar rotación adicional de 180° alrededor del eje Y
                if needs_mirror:
                    mirror_mat = AllplanGeo.Matrix3D()
                    mirror_mat.SetRotation(axis_y, AllplanGeo.Angle(math.pi))
                    mat = mat * mirror_mat

            elif in_yz_plane:
                # ============================================================
                # CASO 2B — Giro en el plano YZ
                # ============================================================
                print("[ELBOW] Detectado giro en plano YZ")

                # Direcciones en el plano YZ
                # Calcular los ángulos reales de ambos vectores respecto al eje Y
                angle_prev = math.atan2(
                    d_prev_z, d_prev_y
                )  # Ángulo del tramo previo en YZ
                angle_next = math.atan2(
                    d_next_z, d_next_y
                )  # Ángulo del tramo siguiente en YZ

                # Producto cruzado en YZ: signo indica si el giro es horario o antihorario
                cross = d_prev_y * d_next_z - d_prev_z * d_next_y

                # Misma lógica que en XY
                if abs(cross) < 1e-6:
                    angle = angle_next
                    needs_mirror = False
                elif cross < 0:
                    angle = angle_next
                    needs_mirror = False
                else:
                    angle = angle_prev
                    needs_mirror = True

                # Normalizar el ángulo
                while angle < 0:
                    angle += 2 * math.pi
                while angle >= 2 * math.pi:
                    angle -= 2 * math.pi

                print(
                    f"[ELBOW] YZ: d_prev=({d_prev_y:.2f}, {d_prev_z:.2f}), "
                    f"d_next=({d_next_y:.2f}, {d_next_z:.2f})"
                )
                print(
                    f"[ELBOW] YZ: angle_prev={math.degrees(angle_prev):.1f}°, "
                    f"angle_next={math.degrees(angle_next):.1f}°, "
                    f"cross={cross:.4f}, final={math.degrees(angle):.1f}°, mirror={needs_mirror}"
                )

                # Para el plano YZ, rotamos alrededor del eje X
                # Primero rotamos el modelo del plano XY al plano YZ (rotación preparatoria alrededor de Z)
                axis_z = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                )
                mat_prep = AllplanGeo.Matrix3D()
                mat_prep.SetRotation(axis_z, AllplanGeo.Angle(math.pi / 2.0))

                # Rotación de orientación alrededor del eje X
                axis_x = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                )
                mat_rot = AllplanGeo.Matrix3D()
                mat_rot.SetRotation(axis_x, AllplanGeo.Angle(angle))

                # Combinar: primero preparación (XY->YZ), luego orientación
                mat = mat_rot * mat_prep

                # Si necesita reflejo, aplicar rotación adicional de 180° alrededor del eje X
                if needs_mirror:
                    mirror_mat = AllplanGeo.Matrix3D()
                    mirror_mat.SetRotation(axis_x, AllplanGeo.Angle(math.pi))
                    mat = mat * mirror_mat

            else:
                # ============================================================
                # CASO 2C — Giro en el plano XY (caso original)
                # ============================================================
                print("[ELBOW] Detectado giro en plano XY")

                # Direcciones absolutas de cada tramo (en planta XY)
                # Calcular los ángulos reales de ambos vectores respecto al eje X
                angle_prev = math.atan2(d_prev_y, d_prev_x)  # Ángulo del tramo previo
                angle_next = math.atan2(
                    d_next_y, d_next_x
                )  # Ángulo del tramo siguiente

                # Producto cruzado en XY: signo indica si el giro es horario o antihorario
                cross = d_prev_x * d_next_y - d_prev_y * d_next_x

                # El modelo del codo está orientado de manera que para giros horarios (cross < 0)
                # funciona correctamente usando el ángulo del vector siguiente.
                # Para giros antihorarios (cross > 0), necesitamos usar el ángulo del vector previo
                # y aplicar un reflejo para orientar correctamente el codo.
                if abs(cross) < 1e-6:
                    angle = angle_next
                    needs_mirror = False
                elif cross < 0:
                    angle = angle_next
                    needs_mirror = False
                else:
                    angle = angle_prev
                    needs_mirror = True

                # Normalizar el ángulo al rango [0, 2π)
                while angle < 0:
                    angle += 2 * math.pi
                while angle >= 2 * math.pi:
                    angle -= 2 * math.pi

                print(
                    f"[ELBOW] XY: d_prev=({d_prev_x:.2f}, {d_prev_y:.2f}), "
                    f"d_next=({d_next_x:.2f}, {d_next_y:.2f})"
                )
                print(
                    f"[ELBOW] XY: angle_prev={math.degrees(angle_prev):.1f}°, "
                    f"angle_next={math.degrees(angle_next):.1f}°, "
                    f"cross={cross:.4f}, final={math.degrees(angle):.1f}°, mirror={needs_mirror}"
                )

                axis_z = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                )

                # Aplicar rotación base
                mat.SetRotation(axis_z, AllplanGeo.Angle(angle))

                # Si necesita reflejo (cross > 0), aplicar rotación adicional de 180° alrededor del eje Z
                # Esto efectivamente refleja el codo en el plano XY
                if needs_mirror:
                    mirror_mat = AllplanGeo.Matrix3D()
                    mirror_mat.SetRotation(axis_z, AllplanGeo.Angle(math.pi))
                    # Combinar las transformaciones: primero rotación base, luego reflejo
                    mat = mat * mirror_mat

            mat.SetTranslation(AllplanGeo.Vector3D(p_mid.X, p_mid.Y, p_mid.Z))

        # ============================================================
        # Aplicar la rotación y el LAYER a los elementos del codo
        # ============================================================
        final_list = []
        for elem in codo_elems:
            try:
                tlist = elem.GetTransformationList()
            except Exception:
                tlist = []
            tlist.append(mat)
            elem.SetTransformationList(tlist)

            # Aplicar layer si está definido para este segmento
            if path_idx is not None and seg_idx is not None:
                try:
                    # Primero verificar si hay layer override (modo edición de layers)
                    # El codo está en el vértice, así que usamos vertex_idx = seg_idx + 1
                    vertex_idx = seg_idx + 1
                    element_key = ("elbow", path_idx, vertex_idx)
                    layer_id = None
                    if hasattr(self, "layer_overrides") and self.layer_overrides:
                        layer_id = self.layer_overrides.get(element_key)

                    # Si no hay override, usar el layer del segmento anterior (el codo está en el vértice entre seg_idx y seg_idx+1)
                    if layer_id is None:
                        layer_id = self._get_segment_layer_id(
                            path_idx, seg_idx, default=None
                        )

                    if layer_id is not None and layer_id > 0:
                        com_prop = elem.GetCommonProperties()
                        if com_prop is None:
                            com_prop = AllplanBaseElements.CommonProperties()
                            com_prop.GetGlobalProperties()
                        com_prop.Layer = layer_id
                        elem.SetCommonProperties(com_prop)
                        print(
                            f"[DBG] Layer ID {layer_id} aplicado a CODO path={path_idx} seg={seg_idx}"
                        )
                except Exception as ex:
                    print(f"[DBG] Error aplicando layer al codo: {ex}")

            final_list.append(elem)

        return final_list

    def _create_manguito(
        self,
        p_prev,
        p_mid,
        p_next,
        d1: float,
        d2: float,
        path_idx=None,
        seg_idx=None,
        distribution_type="IS",
    ):
        """Crea un manguito/reductor en p_mid, alineado al tramo y centrado en la polilínea."""
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return []

        # Obtener tipo de distribución del segmento si no se proporciona
        if distribution_type == "IS" and path_idx is not None and seg_idx is not None:
            try:
                distribution_type = self._get_segment_distribution_type(
                    path_idx, seg_idx, "IS"
                )
            except Exception:
                pass

        # Crear modelo de manguito según distribución
        if distribution_type == "TD":
            ModelClass = ManguitoTDModel
        else:  # IS
            ModelClass = ManguitoModel

        if ModelClass is None:
            print("[SO] ManguitoModel no disponible")
            return []

        # Instancio modelo
        try:
            sig = inspect.signature(ModelClass.__init__)
            param_count = len(sig.parameters)
        except Exception:
            param_count = 3  # asumimos (self, build_ele, doc)

        try:
            if param_count >= 3:
                manguito = ModelClass(self.build_ele, doc)
            else:
                manguito = ModelClass(self.build_ele)
        except TypeError:
            # fallback defensivo
            try:
                manguito = ModelClass(self.build_ele)
            except Exception as ex2:
                print(f"[SO] No se pudo crear ManguitoModel: {ex2}")
                return []

        # ==========================================================
        # FIX: normalizar diámetros (int) antes de set_diameters
        # para que 25-25 no se interprete como reductor por error.
        # ==========================================================
        di1 = int(round(float(d1)))
        di2 = int(round(float(d2)))

        print(
            f"[MANGUITO] Iniciando creación: di1={di1}, di2={di2}, distribution_type={distribution_type}"
        )

        if hasattr(manguito, "set_diameters"):
            try:
                manguito.set_diameters(di1, di2)
                print(f"[MANGUITO] set_diameters({di1}, {di2}) llamado")
            except Exception as ex:
                print(f"[MANGUITO] Error en set_diameters({di1}, {di2}): {ex}")

        type_manguito = getattr(manguito, "type_manguito", None)
        print(f"[MANGUITO] type_manguito después de set_diameters: {type_manguito}")

        # Creo geometría base
        try:
            model_list = manguito.build()
            print(f"[MANGUITO] build() retornó {len(model_list)} elementos")
        except Exception as ex:
            print(f"[MANGUITO] Error en manguito.build(): {ex}")
            import traceback

            traceback.print_exc()
            return []

        if not model_list:
            print("[MANGUITO] model_list está vacío, retornando vacío")
            return []

        # ==========================================================
        # ORIENTACIÓN: Seguir la trayectoria de la polilínea (como los tubos)
        # ==========================================================
        # Calcular vector del tramo completo (p_prev -> p_next pasando por p_mid)
        if p_prev is not None:
            # Usar dirección desde p_prev hasta p_next
            dx = p_next.X - p_prev.X
            dy = p_next.Y - p_prev.Y
            dz = p_next.Z - p_prev.Z
        else:
            # Si no hay p_prev, usar dirección desde p_mid hasta p_next
            dx = p_next.X - p_mid.X
            dy = p_next.Y - p_mid.Y
            dz = p_next.Z - p_mid.Z

        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-6:
            print("[MANGUITO] Vector de dirección muy pequeño, retornando vacío")
            return []

        # Punto de colocación: p_mid directamente
        # Los modelos ya se centran internamente en X, Y, Z
        placement_x = p_mid.X
        placement_y = p_mid.Y
        placement_z = p_mid.Z

        # ==========================================================
        # MATRIZ DE TRANSFORMACIÓN (igual que los tubos)
        # ==========================================================
        # Aplicar mirror primero si es necesario (en espacio local, antes de rotación)
        need_mirror = False
        try:
            type_manguito = getattr(manguito, "type_manguito", None)
            if type_manguito == 3:  # Reductor 25-20
                # El modelo está diseñado para 20->25
                # Si tenemos 25->20, necesitamos hacer mirror en X local para invertir la dirección
                if di1 < di2:  # 20->25 (expansor, usamos modelo reductor)
                    print(
                        f"[MANGUITO] Expansor 20->25 detectado (usando modelo reductor), sin transformación adicional"
                    )
                elif di1 > di2:  # 25->20 (reductor, necesita mirror)
                    need_mirror = True
                    print(
                        f"[MANGUITO] Reductor 25->20 detectado, aplicando mirror en X local"
                    )
        except Exception as ex:
            print(f"[MANGUITO] Error determinando necesidad de mirror: {ex}")

        mat = AllplanGeo.Matrix3D()

        # Caso 1: tramo prácticamente vertical (solo Z)
        if abs(dx) < 1e-6 and abs(dy) < 1e-6 and abs(dz) > 1e-6:
            # 🚨 ROTACIÓN ADICIONAL: Usar reference_orientation_angle si está definido,
            # o el ángulo del segmento previo si existe
            rotation_angle_z = 0.0

            # Prioridad 1: Usar reference_orientation_angle si está definido
            ref_orientation = getattr(self, "reference_orientation_angle", None)
            if ref_orientation is not None:
                rotation_angle_z = ref_orientation
                print(
                    f"[MANGUITO] Usando orientación 3D de referencia: {math.degrees(rotation_angle_z):.2f}° en XY"
                )
            elif p_prev is not None:
                # Prioridad 2: Calcular ángulo del segmento previo si existe
                prev_dx = p_mid.X - p_prev.X
                prev_dy = p_mid.Y - p_prev.Y
                prev_dz = p_mid.Z - p_prev.Z
                prev_length = math.sqrt(
                    prev_dx * prev_dx + prev_dy * prev_dy + prev_dz * prev_dz
                )

                # Verificar si el segmento previo era horizontal (prácticamente sin componente Z)
                if prev_length > 1e-6 and abs(prev_dz) < 1e-6:
                    # Calcular el ángulo del segmento previo en el plano XY
                    rotation_angle_z = math.atan2(prev_dy, prev_dx)
                    print(
                        f"[MANGUITO] Segmento previo horizontal detectado con ángulo {math.degrees(rotation_angle_z):.2f}° en XY"
                    )

            # Aplicar primero la rotación sobre el eje Z (si hay ángulo definido)
            if abs(rotation_angle_z) > 1e-6:
                axis_z = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0),
                    AllplanGeo.Point3D(0, 0, 1),
                )
                mat_z_rot = AllplanGeo.Matrix3D()
                mat_z_rot.SetRotation(axis_z, AllplanGeo.Angle(rotation_angle_z))
                mat = mat_z_rot

            # Luego aplicar la rotación sobre el eje Y para orientar verticalmente
            axis_y = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(0, 1, 0),
            )

            if dz > 0:
                angle_y = -math.pi / 2.0  # +X → +Z
            else:
                angle_y = math.pi / 2.0  # +X → -Z

            mat_y_rot = AllplanGeo.Matrix3D()
            mat_y_rot.SetRotation(axis_y, AllplanGeo.Angle(angle_y))

            # Combinar las rotaciones: primero Z (si existe), luego Y
            if abs(rotation_angle_z) > 1e-6:
                mat = (
                    mat_y_rot * mat
                )  # Aplicar primero mat (rotación Z), luego mat_y_rot (rotación Y)
            else:
                mat = mat_y_rot

            # Aplicar mirror en espacio local (después de las rotaciones, antes de traslación)
            if need_mirror:
                mirror_mat = AllplanGeo.Matrix3D()
                mirror_mat.SetScaling(-1, 1, 1)  # Mirror en X local
                mat = mat * mirror_mat

            mat.SetTranslation(
                AllplanGeo.Vector3D(placement_x, placement_y, placement_z)
            )

        # Caso 2: horizontal/XY o inclinado
        else:
            angle_rad = math.atan2(dy, dx)
            axis_z = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(0, 0, 1),
            )
            rot_mat = AllplanGeo.Matrix3D()
            rot_mat.SetRotation(axis_z, AllplanGeo.Angle(angle_rad))
            mat = mat * rot_mat
            mat.SetTranslation(
                AllplanGeo.Vector3D(placement_x, placement_y, placement_z)
            )

        final_elems = []
        for elem in model_list:
            try:
                tlist = elem.GetTransformationList()
            except Exception:
                tlist = []
            tlist.append(mat)
            elem.SetTransformationList(tlist)

            # Aplicar layer si está definido para este segmento
            if path_idx is not None and seg_idx is not None:
                try:
                    layer_id = self._get_segment_layer_id(
                        path_idx, seg_idx, default=None
                    )
                    if layer_id is not None and layer_id > 0:
                        com_prop = elem.GetCommonProperties()
                        if com_prop is None:
                            com_prop = AllplanBaseElements.CommonProperties()
                            com_prop.GetGlobalProperties()
                        com_prop.Layer = layer_id
                        elem.SetCommonProperties(com_prop)
                        print(
                            f"[DBG] Layer ID {layer_id} aplicado a MANGUITO path={path_idx} seg={seg_idx}"
                        )
                except Exception as ex:
                    print(f"[DBG] Error aplicando layer al manguito: {ex}")

            final_elems.append(elem)

        return final_elems

    def _create_te(
        self,
        center_pt,
        main_dir_vec,
        d_main_in: float,
        d_main_out: float,
        d_branch: float,
        v_branch: tuple = None,
        dir_main_raw: str = None,  # "E", "W", "N", "S" según el primer tramo
        path_idx=None,
        seg_idx=None,
        distribution_type="IS",
        branch_path_idx=None,  # 🆕 path_idx del tubo perpendicular
    ):
        """
        Crea una Te (Te_003) centrada en center_pt con orientación básica.
        Similar a _create_elbow() y _create_manguito(), solo crea el modelo base
        y aplica rotación básica al eje principal + traslación al nodo.

        - center_pt: punto del nodo donde se cruzan los tramos
        - main_dir_vec: vector (dx, dy) del eje principal según cálculo previo
        - d_main_in: diámetro tramo antes del nodo
        - d_main_out: diámetro tramo después del nodo
        - d_branch: diámetro de la rama perpendicular
        - v_branch: vector rama perpendicular (en coords globales) - actualmente no usado
        - dir_main_raw: dirección cruda del troncal - actualmente no usado

        Nota: Si necesitas lógica compleja de orientación (mirrors, etc.),
        deberías hacerla en _finalize_and_create_now() después de obtener los elementos.
        """

        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception:
            return []

        # Obtener tipo de distribución del segmento si no se proporciona
        if distribution_type == "IS" and path_idx is not None and seg_idx is not None:
            try:
                distribution_type = self._get_segment_distribution_type(
                    path_idx, seg_idx, "IS"
                )
            except Exception:
                pass

        # ============================================================
        # Usar modelos TD o IS según distribución (buscar específico o genérico)
        # ============================================================
        folder = "TD" if distribution_type == "TD" else "IS"
        suffix = "TD" if distribution_type == "TD" else "IS"

        te_name = f"Te_{int(d_main_in)}_{int(d_branch)}_{int(d_main_out)}_{suffix}"
        te_path = os.path.join(os.path.dirname(__file__), folder, f"{te_name}.py")

        inv_name = f"Te_{int(d_main_out)}_{int(d_branch)}_{int(d_main_in)}_{suffix}"
        inv_path = os.path.join(os.path.dirname(__file__), folder, f"{inv_name}.py")

        TeModelAuto = None
        mirror_x = False

        if os.path.exists(te_path):
            try:
                spec = importlib.util.spec_from_file_location(te_name, te_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                TeModelAuto = getattr(module, "TeModel", None)
                print(f"[SO] Importado {te_name}")
            except Exception as e:
                print(f"[SO] Error importando {te_name}: {e}")

        elif os.path.exists(inv_path):
            try:
                spec = importlib.util.spec_from_file_location(inv_name, inv_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                TeModelAuto = getattr(module, "TeModel", None)
                mirror_x = True
                print(f"[SO] Importado {inv_name} (invertida)")
            except Exception as e:
                print(f"[SO] Error importando {inv_name}: {e}")

        else:
            # Usar modelo genérico según distribución
            if distribution_type == "TD":
                print("[SO] No existe el modelo específico, usando Te_003 TD genérica")
                TeModelAuto = TeTDModel
            else:
                print("[SO] No existe el modelo específico, usando Te_003_IS genérica")
                TeModelAuto = TeModel
            if d_main_in < d_main_out:
                mirror_x = True

        if TeModelAuto is None:
            print("[SO] ERROR: TeModelAuto es None")
            return []

        # ============================================================
        # INSTANCIAR MODELO
        # ============================================================

        try:
            sig = inspect.signature(TeModelAuto.__init__)
            if len(sig.parameters) >= 3:
                te = TeModelAuto(self.build_ele, doc)
            else:
                te = TeModelAuto(self.build_ele)
        except Exception:
            try:
                te = TeModelAuto(self.build_ele)
            except Exception as ex:
                print(f"[SO] No se pudo instanciar modelo Te: {ex}")
                return []

        # ============================================================
        # SET DE DIÁMETROS
        # ============================================================
        type_te = 0  # Valor por defecto
        if hasattr(te, "set_diameters"):
            try:
                if mirror_x:
                    te.set_diameters(d_main_out, d_branch, d_main_in)
                else:
                    te.set_diameters(d_main_in, d_branch, d_main_out)
                # Obtener el type_te después de set_diameters
                if hasattr(te, "type_te"):
                    type_te = te.type_te
                    print(f"[DBG] T: type_te={type_te}")
            except Exception as ex:
                print(
                    f"[SO] Error en set_diameters({d_main_in}, {d_branch}, {d_main_out}): {ex}"
                )
        elif hasattr(te, "type_te"):
            # Si no tiene set_diameters, obtener type_te directamente
            type_te = te.type_te
            print(f"[DBG] T: type_te={type_te} (sin set_diameters)")

        # ============================================================
        # CREAR GEOMETRÍA BASE
        # ============================================================

        try:
            model_list = te.build()
        except Exception as ex:
            print(f"[SO] Error en TeModel.build(): {ex}")
            return []

        if not model_list:
            return []

        # ============================================================
        # VECTOR PRINCIPAL (TRAMO TRONCAL) Y RAMA
        # ============================================================

        # Normalizamos main_dir_vec solo para orientación y debug
        mx, my = main_dir_vec
        n_main = math.hypot(mx, my)
        if n_main > 1e-6:
            mx /= n_main
            my /= n_main
        else:
            print("[SO] _create_te: main_dir_vec sin dirección válida")
            return []

        print(f"[DBG] Troncal = ({mx:.3f}, {my:.3f})")

        # Rama - detectar si está en el plano XY o elevada en Z
        if v_branch is None:
            # fallback: rama en el plano XY
            v_branch = (0.0, 1.0, 0.0)

        # Manejar tanto vectores 2D como 3D
        if len(v_branch) == 2:
            bx, by = v_branch
            bz = 0.0
        else:
            bx, by, bz = v_branch

        # Normalizar el vector de la rama
        n_branch = math.sqrt(bx * bx + by * by + bz * bz)
        if n_branch > 1e-6:
            bx /= n_branch
            by /= n_branch
            bz /= n_branch
        else:
            # Si el vector es cero, usar +Y por defecto (plano XY)
            bx, by, bz = 0.0, 1.0, 0.0

        print(f"[DBG] Rama = ({bx:.3f}, {by:.3f}, {bz:.3f})")

        # Detectar si la rama está en el plano XY (bz ≈ 0) o elevada en Z (bz ≠ 0)
        branch_in_xy_plane = (
            abs(bz) < 0.1
        )  # Tolerancia para considerar que está en el plano XY
        branch_elevated = not branch_in_xy_plane

        # Detectar dirección de la rama cuando está elevada: +Z (hacia arriba) o -Z (hacia abajo)
        branch_points_up = bz > 0.1  # Rama apunta hacia +Z
        branch_points_down = bz < -0.1  # Rama apunta hacia -Z

        print(
            f"[DBG] Rama en plano XY: {branch_in_xy_plane}, Rama elevada en Z: {branch_elevated}, "
            f"Rama hacia +Z: {branch_points_up}, Rama hacia -Z: {branch_points_down}"
        )

        branch_up = by > 0 if branch_in_xy_plane else bz > 0
        branch_down = by < 0 if branch_in_xy_plane else bz < 0

        # ============================================================
        # ORIENTACIÓN: Verificar rama y determinar si necesitamos mirror por diámetro
        # ============================================================

        # Calcular ángulo base para alinear el eje principal
        ang = math.atan2(my, mx)

        # Calcular la dirección de la rama después de la rotación inicial
        # En el modelo local: eje principal = +X, rama = +Y
        if branch_in_xy_plane:
            # Rama en el plano XY: usar lógica original
            # Después de rotar el eje principal por 'ang', la rama es (sin(ang), cos(ang))
            branch_dir_initial_x = math.sin(ang)
            branch_dir_initial_y = math.cos(ang)
            branch_dir_initial_z = 0.0

            # Verificar si la rama inicial apunta hacia v_branch (en el plano XY)
            dot_branch_initial = branch_dir_initial_x * bx + branch_dir_initial_y * by
        else:
            # Rama elevada en Z: la rama apuntará hacia +Z después de la rotación adicional
            branch_dir_initial_x = 0.0
            branch_dir_initial_y = 0.0
            branch_dir_initial_z = 1.0

            # Verificar si la rama inicial apunta hacia v_branch (componente Z)
            dot_branch_initial = bz

        print(
            f"[DBG] T: Rama - ang={math.degrees(ang):.1f}°, "
            f"branch_dir_initial=({branch_dir_initial_x:.3f}, {branch_dir_initial_y:.3f}, {branch_dir_initial_z:.3f}), "
            f"v_branch=({bx:.3f}, {by:.3f}, {bz:.3f}), dot={dot_branch_initial:.3f}"
        )

        # Ajustar orientación según si la rama está en el plano XY o elevada
        if branch_in_xy_plane:
            # Rama en el plano XY: rotar 180° si es necesario (lógica original)
            if dot_branch_initial < 0:
                ang += math.pi
                print(
                    f"[DBG] T: Rama inicial apuntaba en dirección opuesta, rotando 180° para orientar rama"
                )
                # Recalcular la dirección de la rama después de la rotación
                branch_dir_after_rotation_x = math.sin(ang)
                branch_dir_after_rotation_y = math.cos(ang)
                dot_branch_after = (
                    branch_dir_after_rotation_x * bx + branch_dir_after_rotation_y * by
                )
                print(
                    f"[DBG] T: Rama después de rotación - branch_dir=({branch_dir_after_rotation_x:.3f}, {branch_dir_after_rotation_y:.3f}), "
                    f"dot={dot_branch_after:.3f}"
                )
        else:
            # Rama elevada en Z: no necesitamos rotar 180° alrededor de Z
            # La rotación adicional hacia +Z se aplicará más adelante
            if dot_branch_initial < 0:
                print(
                    f"[DBG] T: Advertencia - v_branch apunta hacia -Z, pero la rama se orientará hacia +Z automáticamente"
                )

        # ============================================================
        # ORIENTACIÓN POR DIÁMETRO (igual que manguitos)
        # Solo para T con type_te >= 3 (TØ25-20-25, TØ25-20-20, TØ25-25-20)
        # O cuando la rama está elevada en Z (independientemente del type_te)
        # Para type_te < 3 (TØ20, TØ25, TØ32) y rama en plano XY, la orientación en X es distinta
        # ============================================================

        di_main_in = int(round(float(d_main_in)))
        di_main_out = int(round(float(d_main_out)))

        need_mirror_x_local = False
        need_mirror_y_local = False
        need_mirror_z_local = (
            False  # Para invertir la dirección Z cuando la rama está elevada
        )

        # Aplicar lógica de orientación por diámetro si:
        # 1. type_te > 3 (TØ25-20-25, TØ25-20-20, TØ25-25-20)
        # 2. O si la rama está elevada en Z (independientemente del type_te)
        if type_te > 3 or (type_te > 3 and branch_elevated):
            # Lógica exactamente igual que manguitos:
            # Si d_main_in > d_main_out (lado grande en entrada) y mirror_x=False,
            # aplicar mirror en X local (equivalente a rotar 180° en manguitos)
            # pero sin afectar la rama perpendicular

            # Determinar el motivo por el cual se aplica la lógica
            motivo = ""
            if type_te > 3 and branch_elevated:
                motivo = f"type_te={type_te} > 3 Y rama elevada en Z"
            elif type_te > 3:
                motivo = f"type_te={type_te} > 3"
            elif branch_elevated:
                motivo = f"rama elevada en Z (type_te={type_te})"

            print(f"[DBG] T: {motivo}, aplicando lógica de orientación por diámetro")
            print(
                f"[DBG] T: di_main_in={di_main_in}, di_main_out={di_main_out}, mirror_x={mirror_x}, "
                f"branch_elevated={branch_elevated}, ang={math.degrees(ang):.1f}°"
            )
            print(
                f"[DBG] T: condición 1 (>): {di_main_in} != {di_main_out} and {di_main_in} > {di_main_out} = "
                f"{di_main_in != di_main_out and di_main_in > di_main_out}"
            )
            print(
                f"[DBG] T: condición 2 (<): {di_main_in} != {di_main_out} and {di_main_in} < {di_main_out} = "
                f"{di_main_in != di_main_out and di_main_in < di_main_out}"
            )

            if di_main_in != di_main_out and di_main_in > di_main_out:
                print("------------------> PASO POR ACA PRIMERO!!! <-----------------")
                # Lado más grande en main_in (entrada) - igual que manguitos cuando di1 > di2
                if not mirror_x:
                    # Verificar si el troncal es vertical (90° o -90°)
                    ang_degrees = math.degrees(ang)
                    # Normalizar a rango -180 a 180
                    while ang_degrees > 180:
                        ang_degrees -= 360
                    while ang_degrees < -180:
                        ang_degrees += 360

                    if abs(ang_degrees - 90) < 1:
                        # Troncal vertical hacia arriba (90°)
                        need_mirror_y_local = True
                        need_mirror_x_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                            f"troncal vertical 90°, branch_elevated={branch_elevated}, aplicando mirror"
                        )
                        print("ACA 90°")
                        if branch_elevated:
                            if branch_points_up:
                                # Rama apunta hacia +Z, aplicar mirror según la lógica
                                need_mirror_z_local = False
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal vertical 90°, branch_elevated={branch_elevated}, "
                                    f"rama hacia +Z, aplicando mirror en Z local"
                                )
                            elif branch_points_down:
                                # Rama apunta hacia -Z, aplicar mirror para orientarla
                                need_mirror_z_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal vertical 90°, branch_elevated={branch_elevated}, "
                                    f"rama hacia -Z, aplicando mirror en Z local"
                                )
                    elif abs(ang_degrees - (-90)) < 1 or abs(ang_degrees - 270) < 1:
                        # Troncal vertical hacia abajo (-90° o 270°)
                        need_mirror_x_local = True
                        need_mirror_y_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                            f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, aplicando mirror"
                        )
                        if branch_elevated:
                            if branch_points_up:
                                # Rama apunta hacia +Z, aplicar mirror según la lógica
                                need_mirror_z_local = False
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, "
                                    f"rama hacia +Z, aplicando mirror en Z local,"
                                    f"N->S UP/ I<F"
                                )
                            elif branch_points_down:
                                # Rama apunta hacia -Z, aplicar mirror para orientarla
                                need_mirror_z_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, "
                                    f"rama hacia -Z, aplicando mirror en Z local."
                                    f"N->S DOWN/ I<F"
                                )
                    elif abs(ang_degrees - 180) < 1 or abs(ang_degrees - (-180)) < 1:
                        # Troncal horizontal invertido (180° o -180°)
                        need_mirror_y_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                            f"troncal horizontal invertido 180°/-180°, branch_elevated={branch_elevated}, aplicando mirror"
                        )
                        if branch_elevated:
                            if branch_points_up:
                                # Rama apunta hacia +Z, verificar si necesita mirror
                                need_mirror_z_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal horizontal invertido 180°/-180°, branch_elevated={branch_elevated}, "
                                    f"rama hacia +Z, aplicando mirror en Z local"
                                )
                    elif abs(ang_degrees - 0) < 1 or abs(ang_degrees - 360) < 1:
                        # Troncal horizontal (0° o 360°)
                        need_mirror_y_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                            f"troncal horizontal 0°/360°, branch_elevated={branch_elevated}, aplicando mirror"
                        )
                        if branch_elevated:
                            if branch_points_up:
                                # Rama apunta hacia +Z, aplicar mirror según la lógica
                                need_mirror_z_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal horizontal 0°/360°, branch_elevated={branch_elevated}, "
                                    f"rama hacia +Z, aplicando mirror en Z local"
                                )
                    else:
                        # Troncal horizontal u otra orientación: verificar si es ángulo de 45° en plano XY
                        if branch_in_xy_plane:
                            # Casos de 45° y 225°
                            if (
                                abs(ang_degrees - 45.0) < 10.0
                                or abs(ang_degrees - 225.0) < 10.0
                                or abs(ang_degrees - (-135.0)) < 10.0
                            ):
                                need_mirror_x_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal ángulo {ang_degrees:.1f}° (45°/225°), rama en plano XY, "
                                    f"aplicando mirror en X local para corregir orientación"
                                )
                            # Casos de 135° y 315°
                            elif (
                                abs(ang_degrees - 135.0) < 10.0
                                or abs(ang_degrees - 315.0) < 10.0
                                or abs(ang_degrees - (-45.0)) < 10.0
                            ):
                                need_mirror_y_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal ángulo {ang_degrees:.1f}° (135°/315°), rama en plano XY, "
                                    f"aplicando mirror en Y local para corregir orientación"
                                )
                            else:
                                # Troncal horizontal u otra orientación: aplicar mirror normal
                                need_mirror_y_local = True
                                print(
                                    f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                    f"troncal ángulo {ang_degrees:.1f}°, branch_elevated={branch_elevated}, aplicando mirror en Y local"
                                )
                        else:
                            # Troncal horizontal u otra orientación: aplicar mirror normal
                            need_mirror_y_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=False, "
                                f"troncal ángulo {ang_degrees:.1f}°, branch_elevated={branch_elevated}, aplicando mirror en Y local"
                            )
                else:
                    # mirror_x=True: verificar si es ángulo de 45° en plano XY
                    if branch_in_xy_plane:
                        # Casos de 45° y 225°
                        if (
                            abs(ang_degrees - 45.0) < 10.0
                            or abs(ang_degrees - 225.0) < 10.0
                            or abs(ang_degrees - (-135.0)) < 10.0
                        ):
                            need_mirror_x_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal ángulo {ang_degrees:.1f}° (45°/225°), rama en plano XY, "
                                f"aplicando mirror adicional en X local para corregir orientación"
                            )
                        # Casos de 135° y 315°
                        elif (
                            abs(ang_degrees - 135.0) < 10.0
                            or abs(ang_degrees - 315.0) < 10.0
                            or abs(ang_degrees - (-45.0)) < 10.0
                        ):
                            need_mirror_y_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) > d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal ángulo {ang_degrees:.1f}° (135°/315°), rama en plano XY, "
                                f"aplicando mirror en Y local para corregir orientación"
                            )
                    # Si mirror_x=True y no es ángulo de 45°, el modelo ya está invertido y configurado correctamente
            elif di_main_in != di_main_out and di_main_in < di_main_out:
                print(
                    f"[DBG] T: ✅ Entró en condición 2 (di_main_in < di_main_out), branch_elevated={branch_elevated}"
                )
                # Verificar si el troncal es vertical (90° o -90°)
                ang_degrees = math.degrees(ang)
                # Normalizar a rango -180 a 180
                while ang_degrees > 180:
                    ang_degrees -= 360
                while ang_degrees < -180:
                    ang_degrees += 360
                print(
                    f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x={mirror_x}, "
                    f"ang={ang_degrees:.1f}°, branch_elevated={branch_elevated}"
                )
                if not mirror_x:
                    need_mirror_x_local = True
                    print(
                        f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=False, "
                        f"ang={ang_degrees:.1f}°, branch_elevated={branch_elevated}, aplicando mirror en X local"
                    )
                elif abs(ang_degrees - 90) < 1:
                    need_mirror_y_local = False
                    print(
                        f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                        f"troncal vertical 90°, branch_elevated={branch_elevated}, NO aplicando mirror"
                    )
                    print("ACA 90°")
                    if branch_elevated:
                        if branch_points_up:
                            # Rama apunta hacia +Z, aplicarcursor  mirror según la lógica
                            need_mirror_z_local = False
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal vertical 90°, branch_elevated={branch_elevated}, "
                                f"rama hacia +Z, aplicando mirror en Z local,"
                                f"S->N UP/ I>F"
                            )
                        elif branch_points_down:
                            # Rama apunta hacia -Z, aplicar mirror para orientarla
                            need_mirror_z_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal vertical 90°, branch_elevated={branch_elevated}, "
                                f"rama hacia -Z, aplicando mirror en Z local,"
                                f"S->N DOWN/ I>F"
                            )
                elif abs(ang_degrees - (-90)) < 1 or abs(ang_degrees - 270) < 1:
                    need_mirror_y_local = False
                    print(
                        f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                        f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, NO aplicando mirror"
                    )
                    print("ACA -90")
                    if branch_elevated:
                        if branch_points_up:
                            # Rama apunta hacia +Z, aplicar mirror según la lógica
                            need_mirror_z_local = False
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, "
                                f"rama hacia +Z, aplicando mirror en Z local"
                            )
                        elif branch_points_down:
                            # Rama apunta hacia -Z, aplicar mirror para orientarla
                            need_mirror_z_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                                f"troncal vertical -90°/270°, branch_elevated={branch_elevated}, "
                                f"rama hacia -Z, aplicando mirror en Z local"
                            )
                elif abs(ang_degrees - 180) < 1 or abs(ang_degrees - (-180)) < 1:
                    need_mirror_x_local = True
                    print(
                        f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                        f"troncal horizontal invertido 180°/-180°, branch_elevated={branch_elevated}, aplicando mirror en X local"
                    )
                    if branch_elevated:
                        if branch_points_up:
                            # Rama apunta hacia +Z, aplicar mirror según la lógica
                            need_mirror_z_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), "
                                f"troncal horizontal 180°/-180°, branch_elevated={branch_elevated}, "
                                f"rama hacia +Z, aplicando mirror en Z local"
                            )
                elif abs(ang_degrees - 0) < 1 or abs(ang_degrees - 360) < 1:
                    need_mirror_x_local = True  # Para el caso de horizontal , rama arriba I>F y rama abajo F<I
                    print(
                        f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x=True, "
                        f"troncal horizontal 0°/360°, branch_elevated={branch_elevated}, aplicando mirror en X local"
                    )
                    if branch_elevated:
                        # Cuando la rama está elevada y el ángulo es 0°/360°,
                        # necesitamos aplicar mirror en Z según la dirección de la rama
                        if branch_points_up:
                            # Rama apunta hacia +Z, aplicar mirror según la lógica
                            need_mirror_z_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), "
                                f"troncal horizontal 0°/360°, branch_elevated={branch_elevated}, "
                                f"rama hacia +Z, aplicando mirror en Z local"
                            )
                elif branch_in_xy_plane:
                    # Casos de 45° y 225°
                    if (
                        abs(ang_degrees - 45.0) < 10.0
                        or abs(ang_degrees - 225.0) < 10.0
                        or abs(ang_degrees - (-135.0)) < 10.0
                    ):
                        need_mirror_x_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x={mirror_x}, "
                            f"troncal ángulo {ang_degrees:.1f}° (45°/225°), rama en plano XY, "
                            f"aplicando mirror en X local para corregir orientación"
                        )
                    # Casos de 135° y 315°
                    elif (
                        abs(ang_degrees - 135.0) < 10.0
                        or abs(ang_degrees - 315.0) < 10.0
                        or abs(ang_degrees - (-45.0)) < 10.0
                    ):
                        need_mirror_y_local = True
                        print(
                            f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x={mirror_x}, "
                            f"troncal ángulo {ang_degrees:.1f}° (135°/315°), rama en plano XY, "
                            f"aplicando mirror en Y local para corregir orientación"
                        )
                else:
                    # Verificar si es ángulo de 45° en plano XY
                    if branch_in_xy_plane:
                        # Casos de 45° y 225°
                        if (
                            abs(ang_degrees - 45.0) < 10.0
                            or abs(ang_degrees - 225.0) < 10.0
                            or abs(ang_degrees - (-135.0)) < 10.0
                        ):
                            need_mirror_x_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x={mirror_x}, "
                                f"troncal ángulo {ang_degrees:.1f}° (45°/225°), rama en plano XY, "
                                f"aplicando mirror en X local para corregir orientación"
                            )
                        # Casos de 135° y 315°
                        elif (
                            abs(ang_degrees - 135.0) < 10.0
                            or abs(ang_degrees - 315.0) < 10.0
                            or abs(ang_degrees - (-45.0)) < 10.0
                        ):
                            need_mirror_y_local = True
                            print(
                                f"[DBG] T: d_main_in({di_main_in}) < d_main_out({di_main_out}), mirror_x={mirror_x}, "
                                f"troncal ángulo {ang_degrees:.1f}° (135°/315°), rama en plano XY, "
                                f"aplicando mirror en Y local para corregir orientación"
                            )
                    else:
                        print(
                            f"[DBG] T: ⚠️ No entró en ninguna condición específica de ángulo (di_main_in={di_main_in}, di_main_out={di_main_out}, "
                            f"ang={ang_degrees:.1f}°, branch_elevated={branch_elevated})"
                        )
        elif type_te <= 3 or (type_te <= 3 and branch_elevated):
            # Para type_te < 3 (TØ20, TØ25, TØ32), la orientación en X es distinta
            # Si el ángulo es 90° o -90°, aplicar mirror
            print(
                f"[DBG] T: type_te={type_te} < 3, usando orientación básica (sin mirrors por diámetro)"
            )
            print("ENTRO ACA")

            # Verificar si el ángulo es 90° o -90° (o 270°)
            ang_degrees = math.degrees(ang)
            # Normalizar a rango -180 a 180
            while ang_degrees > 180:
                ang_degrees -= 360
            while ang_degrees < -180:
                ang_degrees += 360

            # ============================================================
            # CASOS ESPECIALES: Ángulos de 45°, 135°, 225° y 315° en plano XY
            # Aplicar mirror sobre el eje principal para corregir orientación de la rama
            # Separar casos: 45°/225° vs 135°/315° requieren tratamientos diferentes
            # ============================================================
            if branch_in_xy_plane:
                # Verificar si el ángulo está cerca de 45° o 225° (o -135°)
                if (
                    abs(ang_degrees - 45.0) < 10.0
                    or abs(ang_degrees - 225.0) < 10.0
                    or abs(ang_degrees - (-135.0)) < 10.0
                ):
                    # Para 45° y 225°: aplicar mirror en X local
                    need_mirror_x_local = True
                    print(
                        f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (45°/225°), "
                        f"rama en plano XY, aplicando mirror en X local para corregir orientación"
                    )
                # Verificar si el ángulo está cerca de 135° o 315° (o -45°)
                elif (
                    abs(ang_degrees - 135.0) < 10.0
                    or abs(ang_degrees - 315.0) < 10.0
                    or abs(ang_degrees - (-45.0)) < 10.0
                ):
                    # Para 135° y 315°: aplicar mirror en Y local
                    need_mirror_y_local = True
                    print(
                        f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (135°/315°), "
                        f"rama en plano XY, aplicando mirror en Y local para corregir orientación"
                    )
                elif (
                    abs(ang_degrees - 90) < 1
                    or abs(ang_degrees - (-90)) < 1
                    or abs(ang_degrees - 270) < 1
                ):
                    need_mirror_y_local = True
                    print(
                        f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (90° o -90°), aplicando mirror en X local"
                    )
            elif (
                abs(ang_degrees - 90) < 1
                or abs(ang_degrees - (-90)) < 1
                or abs(ang_degrees - 270) < 1
            ):
                need_mirror_y_local = True
                print(
                    f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (90° o -90°), aplicando mirror en X local"
                )
                if branch_elevated:
                    if branch_points_up:
                        # Rama apunta hacia +Z, aplicar mirror según la lógica
                        need_mirror_z_local = False
                        print(
                            f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (90° o -90°), branch_elevated={branch_elevated}, "
                            f"rama hacia +Z, aplicando mirror en Z local"
                        )
                    elif branch_points_down:
                        # Rama apunta hacia -Z, aplicar mirror para orientarla
                        need_mirror_z_local = True
                        print(
                            f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (90° o -90°), branch_elevated={branch_elevated}, "
                            f"rama hacia -Z, aplicando mirror en Z local"
                        )
            else:
                if branch_elevated:
                    if branch_points_up:
                        # Rama apunta hacia +Z, aplicar mirror según la lógica
                        need_mirror_z_local = True
                        print(
                            f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (0° o 360°), branch_elevated={branch_elevated}, "
                            f"rama hacia +Z, aplicando mirror en Z local"
                        )
                    elif branch_points_down:
                        # Rama apunta hacia -Z, aplicar mirror para orientarla
                        need_mirror_z_local = False
                        print(
                            f"[DBG] T: type_te={type_te} < 3, ang={ang_degrees:.1f}° (0° o 360°), branch_elevated={branch_elevated}, "
                            f"rama hacia -Z, aplicando mirror en Z local"
                        )
        else:
            pass
        # ============================================================
        # MATRIZ BASE: APLICAR TRANSFORMACIONES EN ORDEN CORRECTO
        # 1. Mirror en X local (si es necesario) - ANTES de la rotación
        # 2. Rotar al eje de la tubería
        # 3. Trasladar al nodo
        # ============================================================

        axis_z = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
        )

        mat = AllplanGeo.Matrix3D()

        # 1. Aplicar mirror en X local ANTES de la rotación (si es necesario)
        if need_mirror_x_local:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetScaling(1, -1, 1)  # Mirror en X local
            mat = mat * mirror_mat

        if need_mirror_y_local:
            mirror_mat = AllplanGeo.Matrix3D()
            mirror_mat.SetScaling(-1, -1, 1)  # Mirror en y local
            mat = mat * mirror_mat

        # 2. Aplicar rotación alrededor del eje Z para alinear el eje principal
        rot_mat = AllplanGeo.Matrix3D()
        rot_mat.SetRotation(axis_z, AllplanGeo.Angle(ang))
        mat = mat * rot_mat

        # 2.5. Rotar la rama hacia +Z SOLO si está elevada (no en el plano XY)
        if branch_elevated:
            # Rotar la rama hacia +Z (rotación de -90° alrededor del eje X local)
            # En el modelo base, la rama apunta en +Y local
            # Después de rotar alrededor de Z, el eje X local está en la dirección del troncal
            # Rotamos -90° alrededor del eje X local para que +Y local se convierta en +Z
            # Aplicar la rotación Z al eje X local primero
            axis_x_rotated = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0),
                AllplanGeo.Point3D(math.cos(ang), math.sin(ang), 0),
            )
            rot_branch_mat = AllplanGeo.Matrix3D()
            rot_branch_mat.SetRotation(axis_x_rotated, AllplanGeo.Angle(-math.pi / 2))
            mat = mat * rot_branch_mat

            # Determinar la dirección objetivo según la dirección original de la rama
            if branch_points_down:
                # Rama original apunta hacia -Z, después de rotar apuntará hacia +Z
                # Si necesitamos que apunte hacia -Z, aplicamos mirror
                target_direction = "-Z"
                print(
                    f"[DBG] T: Aplicando rotación adicional para elevar rama (original hacia -Z, objetivo: {target_direction})"
                )
            else:
                # Rama original apunta hacia +Z
                target_direction = "+Z"
                print(
                    f"[DBG] T: Aplicando rotación adicional para elevar rama hacia {target_direction}"
                )

            # 2.6. Aplicar mirror en Z si es necesario
            if need_mirror_z_local:
                mirror_z_mat = AllplanGeo.Matrix3D()
                mirror_z_mat.SetScaling(1, 1, -1)  # Mirror en Z local (invierte solo Z)
                mat = mat * mirror_z_mat
                print(
                    f"[DBG] T: Aplicando mirror en Z local para corregir orientación de la rama "
                    f"(rama original hacia {'-Z' if branch_points_up else '+Z'}, objetivo: {target_direction})"
                )
            elif branch_points_down:
                # Si la rama apunta hacia -Z y no hay need_mirror_z_local,
                # aplicar mirror para orientarla hacia -Z (invertir de +Z a -Z)
                mirror_z_mat = AllplanGeo.Matrix3D()
                mirror_z_mat.SetScaling(1, 1, 1)
                mat = mat * mirror_z_mat
                print(
                    f"[DBG] T: Rama original hacia -Z, aplicando mirror en Z local para orientarla hacia -Z"
                )

        # 3. Aplicar traslación
        mat.SetTranslation(AllplanGeo.Vector3D(center_pt.X, center_pt.Y, center_pt.Z))

        # ============================================================
        # CONDICIONAL: Detectar si el tramo principal está en diagonal
        # y la rama perpendicular está elevada en Z
        # Si ambas condiciones se cumplen, marcar el tubo perpendicular
        # para aplicar rotación de -45 grados
        # ============================================================
        if branch_elevated and branch_path_idx is not None:
            # 1. Calcular el ángulo del tramo principal en grados
            ang_degrees = math.degrees(ang)

            # Normalizar ángulo a rango -180 a 180
            while ang_degrees > 180:
                ang_degrees -= 360
            while ang_degrees < -180:
                ang_degrees += 360

            # Verificar si el tramo principal está en diagonal (45°, 135°, 225°, 315°)
            is_main_diagonal = (
                abs(ang_degrees - 45.0) < 10.0
                or abs(ang_degrees - 135.0) < 10.0
                or abs(ang_degrees - 225.0) < 10.0
                or abs(ang_degrees - 315.0) < 10.0
                or abs(ang_degrees - (-45.0)) < 10.0
                or abs(ang_degrees - (-135.0)) < 10.0
            )

            # 2. Verificar si la rama perpendicular está elevada en Z (ya detectado arriba)
            # branch_elevated ya está definido arriba

            # 3. Si ambas condiciones se cumplen, marcar el tubo perpendicular para rotación
            # usando el ángulo del tramo principal como referencia
            if is_main_diagonal:
                # Los diccionarios ya están inicializados y limpios al inicio de _finalize_and_create_now
                # Almacenar el ángulo del tramo principal (en radianes) para aplicar al tubo perpendicular
                # Usar branch_path_idx como clave para identificar el tubo
                self.branch_tube_rotation_needed[branch_path_idx] = (
                    ang  # Almacenar ángulo en radianes
                )

                # Almacenar la dirección de la rama: "+Z" o "-Z"
                branch_direction = "+Z" if branch_points_up else "-Z"
                self.branch_tube_direction[branch_path_idx] = branch_direction

                print(
                    f"[DBG] ✅ CONDICIONAL: Tramo principal en diagonal ({ang_degrees:.1f}°) "
                    f"y rama perpendicular elevada en Z (z={bz:.3f}, dirección={branch_direction}) detectados. "
                    f"Marcando tubo perpendicular (path={branch_path_idx}) para rotación de {ang_degrees:.1f}° "
                    f"(usando ángulo del tramo principal como referencia). "
                    f"Ángulo almacenado: {ang:.4f} rad"
                )
                print(
                    f"[DBG] Diccionario branch_tube_rotation_needed después de almacenar: {self.branch_tube_rotation_needed}"
                )
                print(
                    f"[DBG] Diccionario branch_tube_direction después de almacenar: {self.branch_tube_direction}"
                )
            else:
                print(
                    f"[DBG] ⚠️ Condicional NO se cumple: is_main_diagonal={is_main_diagonal}, "
                    f"ang_degrees={ang_degrees:.1f}°, branch_elevated={branch_elevated}"
                )

        # Verificación final de la rama
        if branch_in_xy_plane:
            # Rama en el plano XY: verificar dirección en XY
            # Orden de transformaciones:
            # 1. Mirror en X local: SetScaling(1, -1, 1) -> invierte Y local
            # 2. Mirror en Y local: SetScaling(-1, -1, 1) -> invierte X e Y local (equivale a rotación 180°)
            # 3. Rotación por 'ang' alrededor de Z
            #
            # En el modelo base: rama = +Y local
            # Después de rotar por 'ang': rama apunta en (sin(ang), cos(ang)) en coordenadas globales
            #
            # Efecto de mirrors ANTES de la rotación:
            # - Mirror en X: invierte Y local -> rama = -Y local -> después de rotar: (-sin(ang), -cos(ang))
            # - Mirror en Y: invierte X e Y local -> rama = -Y local -> después de rotar: (-sin(ang), -cos(ang))
            # - Ambos mirrors: neto sin cambios -> después de rotar: (sin(ang), cos(ang))

            # Calcular dirección esperada según los mirrors aplicados
            branch_dir_final_x = math.sin(ang)
            branch_dir_final_y = math.cos(ang)

            # Aplicar efecto de mirrors (solo si NO es un caso especial de 45° con mirror en X)
            # Para casos normales (90°, 0°, 180°, etc.), los mirrors se aplican normalmente
            # Para casos de 45° con mirror en X, el mirror ya corrige la orientación correctamente

            # Verificar si se aplicó mirror específicamente para ángulos de 45° en plano XY
            is_45_deg_case = False
            is_135_deg_case = False

            ang_degrees_check = math.degrees(ang)
            while ang_degrees_check > 180:
                ang_degrees_check -= 360
            while ang_degrees_check < -180:
                ang_degrees_check += 360

            # Casos de 45° y 225° con mirror en X
            if need_mirror_x_local and (
                abs(ang_degrees_check - 45.0) < 10.0
                or abs(ang_degrees_check - 225.0) < 10.0
                or abs(ang_degrees_check - (-135.0)) < 10.0
            ):
                is_45_deg_case = True

            # Casos de 135° y 315° con mirror en Y
            if need_mirror_y_local and (
                abs(ang_degrees_check - 135.0) < 10.0
                or abs(ang_degrees_check - 315.0) < 10.0
                or abs(ang_degrees_check - (-45.0)) < 10.0
            ):
                is_135_deg_case = True

            # Aplicar efecto de mirrors según el caso
            if is_45_deg_case:
                # Caso especial: ángulos de 45°/225° con mirror en X
                # El mirror en X invierte Y local, entonces después de rotar por 'ang':
                # la rama apunta en (-sin(ang), -cos(ang))
                branch_dir_final_x = -math.sin(ang)
                branch_dir_final_y = -math.cos(ang)
                print(
                    f"[DBG] T: Verificación final - caso 45°/225° con mirror en X, "
                    f"rama esperada: ({branch_dir_final_x:.3f}, {branch_dir_final_y:.3f})"
                )
            elif is_135_deg_case:
                # Caso especial: ángulos de 135°/315° con mirror en Y
                # El mirror en Y invierte ambos X e Y local:
                # - Eje principal: +X local -> -X local
                # - Rama: +Y local -> -Y local
                # Después de rotar por 'ang', la rama (que era -Y local) apunta en:
                # (sin(ang), -cos(ang))
                branch_dir_final_x = math.sin(ang)
                branch_dir_final_y = -math.cos(ang)
                print(
                    f"[DBG] T: Verificación final - caso 135°/315° con mirror en Y, "
                    f"rama esperada: ({branch_dir_final_x:.3f}, {branch_dir_final_y:.3f})"
                )
            else:
                # Para casos normales (90°, 0°, 180°, etc.): usar lógica original
                # Los mirrors ya están correctamente aplicados en la matriz de transformación,
                # así que la dirección esperada es simplemente (sin(ang), cos(ang))
                # No necesitamos ajustar por los mirrors aquí porque la verificación original funcionaba
                pass  # branch_dir_final ya está calculado como (sin(ang), cos(ang))

            branch_dir_final_z = 0.0

            dot_branch_final = branch_dir_final_x * bx + branch_dir_final_y * by
            print(
                f"[DBG] T: Verificación final - branch_dir_final=({branch_dir_final_x:.3f}, {branch_dir_final_y:.3f}), "
                f"v_branch=({bx:.3f}, {by:.3f}), dot={dot_branch_final:.3f}"
            )
        else:
            # Rama elevada: verificar dirección en Z
            branch_dir_final_x = 0.0
            branch_dir_final_y = 0.0
            # La dirección final depende de si la rama original apunta hacia +Z o -Z
            if branch_points_down:
                # Rama original hacia -Z, después de transformaciones debería apuntar hacia -Z
                branch_dir_final_z = -1.0
                dot_branch_final = (
                    -bz
                )  # Debería ser positivo si bz es negativo (rama hacia -Z)
            else:
                # Rama original hacia +Z, después de transformaciones debería apuntar hacia +Z
                branch_dir_final_z = 1.0
                dot_branch_final = bz  # Debería ser positivo si apunta hacia +Z

        if dot_branch_final < 0.5:  # Si no apunta en la dirección correcta
            # Esto no debería pasar, pero por seguridad ajustamos
            # Recrear la matriz con rotación adicional
            mat = AllplanGeo.Matrix3D()
            if need_mirror_x_local:
                mirror_mat = AllplanGeo.Matrix3D()
                mirror_mat.SetScaling(1, -1, 1)
                mat = mat * mirror_mat
            if need_mirror_y_local:
                mirror_mat = AllplanGeo.Matrix3D()
                mirror_mat.SetScaling(-1, -1, 1)
                mat = mat * mirror_mat
            ang += math.pi
            rot_mat = AllplanGeo.Matrix3D()
            rot_mat.SetRotation(axis_z, AllplanGeo.Angle(ang))
            mat = mat * rot_mat
            # Aplicar rotación de la rama hacia +Z o -Z solo si está elevada
            if branch_elevated:
                axis_x_rotated = AllplanGeo.Line3D(
                    AllplanGeo.Point3D(0, 0, 0),
                    AllplanGeo.Point3D(math.cos(ang), math.sin(ang), 0),
                )
                rot_branch_mat = AllplanGeo.Matrix3D()
                rot_branch_mat.SetRotation(
                    axis_x_rotated, AllplanGeo.Angle(-math.pi / 2)
                )
                mat = mat * rot_branch_mat
                # Aplicar mirror en Z si es necesario
                if need_mirror_z_local:
                    mirror_z_mat = AllplanGeo.Matrix3D()
                    mirror_z_mat.SetScaling(1, 1, -1)
                    mat = mat * mirror_z_mat
                elif branch_points_down:
                    # Si la rama apunta hacia -Z y no hay need_mirror_z_local,
                    # aplicar mirror para orientarla hacia -Z
                    mirror_z_mat = AllplanGeo.Matrix3D()
                    mirror_z_mat.SetScaling(1, 1, -1)
                    mat = mat * mirror_z_mat
            mat.SetTranslation(
                AllplanGeo.Vector3D(center_pt.X, center_pt.Y, center_pt.Z)
            )
            print(
                f"[DBG] T: WARNING - Rama final apuntaba en dirección opuesta, corrigiendo con rotación adicional"
            )

        # ============================================================
        # APLICAR TRANSFORMACIÓN BÁSICA
        # ============================================================

        final_elems = []
        for elem in model_list:
            try:
                tlist = elem.GetTransformationList()
            except Exception:
                tlist = []
            tlist.append(mat)
            elem.SetTransformationList(tlist)

            # Aplicar layer si está definido para este segmento
            if path_idx is not None and seg_idx is not None:
                try:
                    layer_id = self._get_segment_layer_id(
                        path_idx, seg_idx, default=None
                    )
                    if layer_id is not None and layer_id > 0:
                        com_prop = elem.GetCommonProperties()
                        if com_prop is None:
                            com_prop = AllplanBaseElements.CommonProperties()
                            com_prop.GetGlobalProperties()
                        com_prop.Layer = layer_id
                        elem.SetCommonProperties(com_prop)
                        print(
                            f"[DBG] Layer ID {layer_id} aplicado a TE path={path_idx} seg={seg_idx}"
                        )
                except Exception as ex:
                    print(f"[DBG] Error aplicando layer a la Te: {ex}")

            final_elems.append(elem)

        return final_elems

    def _is_90_deg_turn(self, p_prev, p_curr, p_next) -> bool:
        """Devuelve True si el giro entre (p_prev → p_curr → p_next) es 90°
        considerando tramos ortogonales en X, Y o Z.
        """
        if not (p_prev and p_curr and p_next):
            return False

        # Vectores 3D
        v1 = (
            p_curr.X - p_prev.X,
            p_curr.Y - p_prev.Y,
            p_curr.Z - p_prev.Z,
        )
        v2 = (
            p_next.X - p_curr.X,
            p_next.Y - p_curr.Y,
            p_next.Z - p_curr.Z,
        )

        eps = 1e-6

        # Si alguno es casi nulo, no hay giro definido
        if (abs(v1[0]) < eps and abs(v1[1]) < eps and abs(v1[2]) < eps) or (
            abs(v2[0]) < eps and abs(v2[1]) < eps and abs(v2[2]) < eps
        ):
            return False

        def dom_axis(v):
            """Devuelve 0=X, 1=Y, 2=Z según el componente dominante."""
            ax = [abs(v[0]), abs(v[1]), abs(v[2])]
            m = max(ax)
            if m < eps:
                return None
            return ax.index(m)

        a1 = dom_axis(v1)
        a2 = dom_axis(v2)

        if a1 is None or a2 is None:
            return False

        # Si cambias de eje (X→Y, X→Z, Y→Z, etc.) lo consideramos giro de 90°
        return a1 != a2

    def _get_segment_diameter(self, path_idx: int, seg_idx: int, default=20.0):
        print(f"[DBG] _get_segment_diameter: busco path={path_idx}, seg={seg_idx}")
        print(f"[DBG] saved_segments tiene {len(self.saved_segments)} items")

        for idx, seg in enumerate(self.saved_segments):
            print(
                f"   [DBG] seg[{idx}] path={seg.get('path_idx')} "
                f"seg_idx={seg.get('seg_idx')} diam={seg.get('diameter')}"
            )
            if seg.get("path_idx") == path_idx and seg.get("seg_idx") == seg_idx:
                d = float(seg.get("diameter", default))
                print(f"   [DBG]  👉 MATCH, devuelvo diameter={d}")
                return d

        print(f"   [DBG]  ❌ no encontré segmento, devuelvo default={default}")
        return default

    def _update_segment_diameter(
        self, path_idx: int, seg_idx: int, new_diameter: float
    ):
        """
        Actualiza el diámetro de un segmento en saved_segments.
        Usado para forzar el mismo diámetro en codos cuando hay diferencia.
        """
        try:
            for seg in self.saved_segments:
                if seg.get("path_idx") == path_idx and seg.get("seg_idx") == seg_idx:
                    old_diam = seg.get("diameter", 20.0)
                    seg["diameter"] = float(new_diameter)
                    seg["section_type"] = f"{int(round(new_diameter))}mm"
                    print(
                        f"[DBG] _update_segment_diameter: path={path_idx}, seg={seg_idx}: "
                        f"{old_diam}mm -> {new_diameter}mm"
                    )
                    return True
            print(
                f"[DBG] _update_segment_diameter: No se encontró segmento path={path_idx}, seg={seg_idx}"
            )
            return False
        except Exception as ex:
            print(f"[DBG] Error actualizando diámetro del segmento: {ex}")
            return False

    def _get_max_segment_length(self, distribution_type: str) -> float:
        """
        Obtiene la longitud máxima permitida para un segmento según el tipo de distribución
        y el tipo de tubo seleccionado en la paleta.

        Args:
            distribution_type: Tipo de distribución ("TD" o "IS")

        Returns:
            Longitud máxima en mm
        """
        try:
            # Leer tipo de tubo desde la paleta según la distribución
            if distribution_type == "TD":
                tube_prop = getattr(self.build_ele, "TipoDeTuboTD", None)
                tube_type = None
                if tube_prop is not None:
                    tube_type = getattr(tube_prop, "value", tube_prop)
                tube_type = tube_type or "Polietilè"

                if isinstance(tube_type, str):
                    tube_type_norm = tube_type.strip()
                else:
                    tube_type_norm = "Polietilè"
            else:
                # IS (por defecto)
                tube_prop = getattr(self.build_ele, "TipoDeTuboIS", None)
                tube_type = None
                if tube_prop is not None:
                    tube_type = getattr(tube_prop, "value", tube_prop)
                tube_type = tube_type or "Polietilè"

                if isinstance(tube_type, str):
                    tube_type_norm = tube_type.strip()
                else:
                    tube_type_norm = "Polietilè"

            # Buscar en el diccionario
            key = (distribution_type, tube_type_norm)
            max_length = MAX_SEGMENT_LENGTH_BY_TUBE_TYPE.get(key, None)

            if max_length is not None:
                print(
                    f"[DBG] _get_max_segment_length: dist={distribution_type}, tubo='{tube_type_norm}' -> {max_length}mm"
                )
                return float(max_length)
            else:
                # Fallback al valor por defecto
                print(
                    f"[DBG] _get_max_segment_length: No se encontró longitud máxima para dist={distribution_type}, tubo='{tube_type_norm}', usando MAX_SEGMENT_LENGTH={MAX_SEGMENT_LENGTH}mm"
                )
                return MAX_SEGMENT_LENGTH

        except Exception as ex:
            print(
                f"[DBG] ERROR en _get_max_segment_length: {ex}, usando MAX_SEGMENT_LENGTH={MAX_SEGMENT_LENGTH}mm"
            )
            return MAX_SEGMENT_LENGTH

    def _get_segment_distribution_type(self, path_idx: int, seg_idx: int, default="IS"):
        """Obtiene el tipo de distribución (TD o IS) de un segmento específico"""
        try:
            for seg in self.saved_segments:
                if seg.get("path_idx") == path_idx and seg.get("seg_idx") == seg_idx:
                    dist_type = seg.get("distribution_type")
                    if dist_type in ["TD", "IS"]:
                        return dist_type
            return default
        except Exception as ex:
            print(f"[DBG] Error obteniendo distribution_type del segmento: {ex}")
            return default

    def _get_segment_nomis(self, path_idx: int, seg_idx: int, default=""):
        """
        Obtiene el valor de atributo (NomIS) para 6_CC_IS/pmp_pare de un segmento.
        Busca en saved_segments custom_attributes; si no hay, usa el valor de la paleta (build_ele.NomIS).
        Así se preservan los atributos al entrar en modo edición de layers (preview_mode).
        """
        try:
            for seg in self.saved_segments:
                if seg.get("path_idx") == path_idx and seg.get("seg_idx") == seg_idx:
                    custom = seg.get("custom_attributes") or {}
                    if custom:
                        vals = list(custom.values())
                        if vals:
                            v = vals[-1] if isinstance(vals[-1], str) else str(vals[-1])
                            if v.strip():
                                return v.strip()
                    break
            nom_is_val = default
            if hasattr(self, "build_ele") and hasattr(self.build_ele, "NomIS"):
                nom_attr = getattr(self.build_ele, "NomIS", None)
                if nom_attr is not None:
                    nom_is_val = getattr(nom_attr, "value", "") or ""
            return (
                (nom_is_val or "").strip()
                if isinstance(nom_is_val, str)
                else str(nom_is_val).strip()
            )
        except Exception as ex:
            print(f"[DBG] Error obteniendo NomIS del segmento: {ex}")
            return default

    def _get_segment_layer_id(self, path_idx: int, seg_idx: int, default=None):
        """Obtiene el ID del layer asignado a un segmento específico"""
        try:
            for seg in self.saved_segments:
                if seg.get("path_idx") == path_idx and seg.get("seg_idx") == seg_idx:
                    # Primero intentar obtener layer_id (nuevo formato)
                    layer_id = seg.get("layer_id")
                    if layer_id is not None:
                        return int(layer_id)
                    # Fallback al formato antiguo (solo número)
                    layer = seg.get("layer")
                    if layer is not None:
                        return int(layer)
            return default
        except Exception as ex:
            print(f"[DBG] Error obteniendo layer_id del segmento: {ex}")
            return default

    def _is_straight_turn(self, p_prev, p_curr, p_next, tol_deg=1.0) -> bool:
        v1 = (p_curr.X - p_prev.X, p_curr.Y - p_prev.Y)
        v2 = (p_next.X - p_curr.X, p_next.Y - p_curr.Y)

        ang1 = math.degrees(math.atan2(v1[1], v1[0]))
        ang2 = math.degrees(math.atan2(v2[1], v2[0]))

        diff = abs((ang2 - ang1) % 360)
        if diff > 180:
            diff = 360 - diff

        return diff < tol_deg or abs(diff - 180) < tol_deg

    def _serialize_state_to_json(self) -> str:
        """
        Serializa saved_paths y saved_segments a JSON para persistencia.

        Returns:
            String JSON con el estado serializado
        """
        try:
            # Convertir Point3D a listas [x, y, z]
            def point_to_dict(pt):
                return {"X": pt.X, "Y": pt.Y, "Z": pt.Z}

            # Serializar paths
            paths_data = []
            for path in self.saved_paths:
                paths_data.append([point_to_dict(pt) for pt in path])

            # Serializar segments (ya tienen estructura de diccionario)
            segments_data = []
            for seg in self.saved_segments:
                seg_copy = seg.copy()
                if "points" in seg_copy:
                    seg_copy["points"] = [
                        point_to_dict(pt) for pt in seg_copy["points"]
                    ]
                segments_data.append(seg_copy)

            # Serializar overrides (convertir tuplas a listas para JSON)
            layer_overrides_serializable = {}
            for key, value in getattr(self, "layer_overrides", {}).items():
                # Convertir tupla a lista para serialización JSON
                if isinstance(key, tuple):
                    layer_overrides_serializable[str(key)] = value
                else:
                    layer_overrides_serializable[str(key)] = value

            distribution_overrides_serializable = {}
            for key, value in getattr(self, "distribution_overrides", {}).items():
                if isinstance(key, tuple):
                    distribution_overrides_serializable[str(key)] = value
                else:
                    distribution_overrides_serializable[str(key)] = value

            attribute_overrides_serializable = {}
            for key, value in getattr(self, "attribute_overrides", {}).items():
                if isinstance(key, tuple):
                    attribute_overrides_serializable[str(key)] = value
                else:
                    attribute_overrides_serializable[str(key)] = value

            # Serializar element_markers y free_placed_points (módulo ElementosDefinidos)
            element_markers_data = ed_serialize_element_markers(
                getattr(self, "element_markers", []) or []
            )
            free_placed_data = ed_serialize_free_placed_points(
                getattr(self, "free_placed_points", []) or []
            )

            # Serializar también el estado relevante de la paleta (tipo de distribución,
            # tipo de tubo, tipo de agua, diámetros, etc.) para poder restaurarlo al
            # re‑entrar en edición del PythonPartGroup sin que se pierdan estos valores.
            palette_state = {}
            try:
                build_ele = getattr(self, "build_ele", None)

                def _get_be_value(name, default=None):
                    if build_ele is None or not hasattr(build_ele, name):
                        return default
                    prop = getattr(build_ele, name)
                    return (
                        getattr(prop, "value", prop) if hasattr(prop, "value") else prop
                    )

                # Tipo de distribución (TD / IS)
                palette_state["TipoDeDistribucion"] = _get_be_value(
                    "TipoDeDistribucion", None
                )

                # Tipos de tubo (TD / IS)
                palette_state["TipoDeTuboTD"] = _get_be_value("TipoDeTuboTD", None)
                palette_state["TipoDeTuboIS"] = _get_be_value("TipoDeTuboIS", None)

                # Tipos de agua (TD / IS)
                palette_state["TipoDeAguaTD"] = _get_be_value("TipoDeAguaTD", None)
                palette_state["TipoDeAguaIS"] = _get_be_value("TipoDeAguaIS", None)

                # Diámetro base usado por la polilínea (si existe en la paleta)
                palette_state["DiametroAplicar"] = _get_be_value(
                    "DiametroAplicar", None
                )
            except Exception:
                # No romper la serialización si algo falla con la lectura de la paleta
                palette_state = {}

            state = {
                "paths": paths_data,
                "segments": segments_data,
                "layer_overrides": layer_overrides_serializable,
                "distribution_overrides": distribution_overrides_serializable,
                "attribute_overrides": attribute_overrides_serializable,
                "element_markers": element_markers_data,
                "free_placed_points": free_placed_data,
                "palette_state": palette_state,
            }

            return json.dumps(state)
        except Exception as e:
            print(f"[SO] Error serializando estado: {e}")
            import traceback

            traceback.print_exc()
            return ""

    def _deserialize_state_from_json(self, json_str: str) -> bool:
        """
        Deserializa saved_paths y saved_segments desde JSON.

        Args:
            json_str: String JSON con el estado serializado

        Returns:
            True si se restauró correctamente, False en caso contrario
        """
        try:
            if not json_str or not json_str.strip():
                return False

            state = json.loads(json_str)

            # Restaurar paths
            if "paths" in state:
                self.saved_paths = []
                for path_data in state["paths"]:
                    path = [
                        AllplanGeo.Point3D(pt["X"], pt["Y"], pt["Z"])
                        for pt in path_data
                    ]
                    self.saved_paths.append(path)

            # Restaurar segments
            if "segments" in state:
                self.saved_segments = []

                # Determinar tipo de distribución por defecto preferentemente
                # desde el estado guardado de la paleta (palette_state), que
                # refleja cómo se creó originalmente la PPG (TD o IS).
                default_dist = "IS"
                try:
                    palette_state_for_dist = state.get("palette_state", {}) or {}
                    pal_val = palette_state_for_dist.get("TipoDeDistribucion")
                    if isinstance(pal_val, str) and pal_val.strip() in ["TD", "IS"]:
                        default_dist = pal_val.strip()
                    else:
                        be = getattr(self, "build_ele", None)
                        if be is not None and hasattr(be, "TipoDeDistribucion"):
                            prop = getattr(be, "TipoDeDistribucion")
                            val = getattr(prop, "value", prop)
                            if isinstance(val, str) and val.strip() in ["TD", "IS"]:
                                default_dist = val.strip()
                except Exception:
                    default_dist = "IS"

                for seg_data in state["segments"]:
                    seg_copy = seg_data.copy()
                    if "points" in seg_copy:
                        seg_copy["points"] = [
                            AllplanGeo.Point3D(pt["X"], pt["Y"], pt["Z"])
                            for pt in seg_copy["points"]
                        ]

                    # Si el segmento no tiene distribution_type (PPG antiguas),
                    # inicializarlo con el tipo de distribución por defecto
                    # determinado arriba (TD/IS).
                    dist_val = seg_copy.get("distribution_type")
                    if dist_val not in ["TD", "IS"]:
                        seg_copy["distribution_type"] = default_dist

                    self.saved_segments.append(seg_copy)

            # Restaurar overrides (convertir strings de vuelta a tuplas)
            def str_to_tuple(key_str):
                """Convierte string de tupla de vuelta a tupla"""
                try:
                    # Formato: "('tube', 0, 0)" o "('elbow', 0, 1)"
                    if key_str.startswith("(") and key_str.endswith(")"):
                        # Evaluar de forma segura
                        import ast

                        return ast.literal_eval(key_str)
                    return key_str
                except Exception:
                    return key_str

            if "layer_overrides" in state:
                self.layer_overrides = {}
                for key_str, value in state["layer_overrides"].items():
                    key = str_to_tuple(key_str)
                    self.layer_overrides[key] = value

            if "distribution_overrides" in state:
                self.distribution_overrides = {}
                for key_str, value in state["distribution_overrides"].items():
                    key = str_to_tuple(key_str)
                    self.distribution_overrides[key] = value

            if "attribute_overrides" in state:
                self.attribute_overrides = {}
                for key_str, value in state["attribute_overrides"].items():
                    key = str_to_tuple(key_str)
                    self.attribute_overrides[key] = value

            # Restaurar estado de la paleta (tipo de distribución / agua / tubo / diámetro)
            try:
                palette_state = state.get("palette_state", {}) or {}
                build_ele = getattr(self, "build_ele", None)

                def _set_be_value(name, value):
                    if build_ele is None or value is None:
                        return
                    if not hasattr(build_ele, name):
                        return
                    prop = getattr(build_ele, name)
                    if hasattr(prop, "value"):
                        prop.value = value
                    else:
                        setattr(build_ele, name, value)

                # Restaurar solo si existen en el estado serializado
                for key in [
                    "TipoDeDistribucion",
                    "TipoDeTuboTD",
                    "TipoDeTuboIS",
                    "TipoDeAguaTD",
                    "TipoDeAguaIS",
                    "DiametroAplicar",
                ]:
                    if key in palette_state:
                        _set_be_value(key, palette_state.get(key))
            except Exception:
                # No abortar la restauración completa si la parte de paleta falla
                pass

            # Restaurar element_markers y free_placed_points (módulo ElementosDefinidos)
            if "element_markers" in state:
                self.element_markers = ed_deserialize_element_markers(
                    state["element_markers"] or []
                )
            else:
                self.element_markers = getattr(self, "element_markers", []) or []

            if "free_placed_points" in state:
                self.free_placed_points = ed_deserialize_free_placed_points(
                    state["free_placed_points"] or []
                )
            else:
                self.free_placed_points = getattr(self, "free_placed_points", []) or []

            print(
                f"[SO] Estado restaurado: {len(self.saved_paths)} paths, {len(self.saved_segments)} segments"
            )
            if hasattr(self, "layer_overrides") and self.layer_overrides:
                print(f"[SO]   Layer overrides: {len(self.layer_overrides)} elementos")
            if hasattr(self, "distribution_overrides") and self.distribution_overrides:
                print(
                    f"[SO]   Distribution overrides: {len(self.distribution_overrides)} elementos"
                )
            if hasattr(self, "attribute_overrides") and self.attribute_overrides:
                print(
                    f"[SO]   Attribute overrides: {len(self.attribute_overrides)} elementos"
                )
            return True

        except Exception as e:
            print(f"[SO] Error deserializando estado: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _restore_saved_state(self):
        """
        Restaura el estado guardado desde caché de sesión, build_ele o PythonPartGroup.
        Se llama en __init__ cuando se edita una instancia existente o tras 1015/1016.
        """
        try:
            # Primero: si Allplan acaba de recrear el script object (p. ej. tras "Seleccionar punto"),
            # restaurar desde la caché de sesión (mismo build_ele)
            cache_key = id(self.build_ele)
            if cache_key in _polyline_state_cache:
                state_json = _polyline_state_cache.pop(cache_key)
                if state_json and self._deserialize_state_from_json(state_json):
                    print(
                        f"[SO] ✓ Estado restaurado desde caché de sesión (polilínea mantenida tras 1015/1016)"
                    )
                    return True

            # Intentar desde build_ele (parámetros normales)
            param_names = ["SavedState", "PolylineState", "StateData"]

            for param_name in param_names:
                try:
                    if hasattr(self.build_ele, param_name):
                        param = getattr(self.build_ele, param_name)
                        if hasattr(param, "value"):
                            state_json = param.value
                            if (
                                state_json
                                and isinstance(state_json, str)
                                and state_json.strip()
                            ):
                                if self._deserialize_state_from_json(state_json):
                                    print(
                                        f"[SO] ✓ Estado previo restaurado desde build_ele.{param_name}"
                                    )
                                    # Activar automáticamente el checkbox CrearPythonPart para mantener la propiedad
                                    self._activate_crear_pythonpart_checkbox()
                                    return True
                except Exception as e:
                    debug(
                        f"[SO] No se pudo leer parámetro {param_name} desde build_ele: {e}"
                    )
                    continue

            # Si no se encontró en build_ele y estamos en modo modificación,
            # intentar leer desde el PythonPartGroup usando PythonPartService
            try:
                is_modification_mode = getattr(self, "is_modification_mode", False)
                if is_modification_mode and hasattr(self, "modification_ele_list"):
                    python_part_adapter = (
                        self.modification_ele_list.get_base_element_adapter(
                            self.document
                        )
                    )
                    if not python_part_adapter.IsNull():
                        success, name, parameter = (
                            AllplanBaseElements.PythonPartService.GetParameter(
                                python_part_adapter
                            )
                        )
                        if success and parameter:
                            # El parámetro puede venir como string o como lista de strings
                            # Normalizar a lista
                            if isinstance(parameter, str):
                                param_lines = parameter.split("\n")
                            elif isinstance(parameter, (list, tuple)):
                                param_lines = parameter
                            else:
                                param_lines = []

                            # Buscar 'SavedState' y 'PmpPareCopyUUIDs' en los parámetros del PPG
                            # Formato: "key = value\nkey2 = value2\n..."
                            state_json = None
                            pmp_pare_uuids_str = None
                            for line in param_lines:
                                if isinstance(line, str):
                                    line = line.strip()
                                    if "=" in line:
                                        key, val = line.split("=", 1)
                                        key, val = key.strip(), val.strip()
                                        if key == "SavedState" and val:
                                            state_json = val
                                        elif key == "PmpPareCopyUUIDs" and val:
                                            pmp_pare_uuids_str = val
                            # Restaurar UUIDs de copias para poder borrarlas al reentrar
                            if pmp_pare_uuids_str and hasattr(
                                self.build_ele, "PmpPareCopyUUIDs"
                            ):
                                try:
                                    self.build_ele.PmpPareCopyUUIDs.value = (
                                        pmp_pare_uuids_str
                                    )
                                    debug(
                                        f"[PMP_PARE] Restaurados {len(pmp_pare_uuids_str.split(';'))} UUIDs de copias desde PPG"
                                    )
                                except Exception as e:
                                    debug(
                                        f"[PMP_PARE] No se pudo restaurar PmpPareCopyUUIDs: {e}"
                                    )
                            if state_json:
                                print(
                                    f"[SO] Encontrado SavedState en PythonPartGroup: {len(state_json)} caracteres"
                                )
                                if self._deserialize_state_from_json(state_json):
                                    print(
                                        f"[SO] ✓ Estado previo restaurado desde PythonPartGroup.SavedState"
                                    )
                                    self._activate_crear_pythonpart_checkbox()
                                    return True
            except Exception as e:
                print(f"[SO] Error intentando leer estado desde PythonPartGroup: {e}")
                import traceback

                traceback.print_exc()

            # Si no se encontró en ningún lugar, es normal en primera creación
            debug(f"[SO] No se encontró estado guardado (normal en primera creación)")
        except Exception as e:
            debug(f"[SO] Error restaurando estado: {e}")
            import traceback

            traceback.print_exc()

        return False

    def _save_state_to_build_ele(self):
        """
        Guarda el estado actual (saved_paths y saved_segments) en build_ele.
        Se llama antes de crear el elemento para persistir el estado.
        Nota: El parámetro SavedState debe existir en el archivo .pyp para que se guarde correctamente.
        """
        try:
            state_json = self._serialize_state_to_json()
            if state_json:
                # Intentar guardar en diferentes parámetros posibles (priorizar PolylineState como en Electricidad)
                param_names = ["PolylineState", "SavedState", "StateData"]
                saved = False

                for param_name in param_names:
                    try:
                        if hasattr(self.build_ele, param_name):
                            param = getattr(self.build_ele, param_name)
                            if hasattr(param, "value"):
                                param.value = state_json
                                print(
                                    f"[SO] ✓ Estado guardado en build_ele.{param_name} ({len(state_json)} caracteres)"
                                )
                                saved = True
                                break
                    except Exception as e:
                        debug(f"[SO] No se pudo guardar en {param_name}: {e}")
                        continue

                if not saved:
                    debug(
                        f"[SO] Advertencia: No se encontró parámetro para guardar estado (SavedState/PolylineState/StateData)"
                    )
                    debug(
                        f"[SO] Para habilitar persistencia, agregue un parámetro String 'SavedState' en el archivo .pyp"
                    )
        except Exception as e:
            print(f"[SO] Error guardando estado en build_ele: {e}")
            import traceback

            traceback.print_exc()

    def _activate_crear_pythonpart_checkbox(self):
        """
        Activa automáticamente el checkbox CrearPythonPart cuando se está editando
        un PythonPartGroup existente, para mantener la propiedad de PythonPartGroup.
        También muestra un mensaje informativo al usuario.
        """
        try:
            # Activar el checkbox en build_ele
            if hasattr(self.build_ele, "CrearPythonPart"):
                try:
                    self.build_ele.CrearPythonPart.value = True
                    print(
                        "[SO] ✓ Checkbox 'CrearPythonPart' activado automáticamente (modo edición)"
                    )
                except Exception as e:
                    print(f"[SO] No se pudo activar CrearPythonPart en build_ele: {e}")

            # Mostrar mensaje informativo al usuario
            try:
                mensaje = (
                    "Se está editando un PythonPartGroup existente.\n\n"
                    "Para mantener la propiedad de PythonPartGroup, el checkbox "
                    "'Crear PythonPart' ha sido activado automáticamente.\n\n"
                    "Si desactiva este checkbox antes de finalizar, los elementos "
                    "se crearán como elementos individuales en lugar de un PythonPartGroup."
                )
                PythonUtility.ShowMessageBox(
                    mensaje, "Edición de PythonPartGroup", PythonUtility.MB_OK
                )
                print("[SO] Mensaje informativo mostrado al usuario")
            except Exception as e:
                print(f"[SO] No se pudo mostrar mensaje informativo: {e}")
                # Fallback: mostrar en consola
                print(
                    "[SO] ⚠ IMPORTANTE: Para mantener PythonPartGroup, asegúrese de que el checkbox 'Crear PythonPart' esté activado antes de finalizar"
                )

        except Exception as e:
            print(f"[SO] Error en _activate_crear_pythonpart_checkbox: {e}")
            import traceback

            traceback.print_exc()

    def start_input(self):
        self.script_object_interactor = PolylineInteractor(self)
        self.script_object_interactor.start_input(self.coord_input)

        # Si hay datos guardados, activar automáticamente el modo de creación
        if self.saved_paths or self.saved_segments:
            if self.script_object_interactor:
                self.script_object_interactor.create_mode = True
                print(
                    f"[SO] ✓ Modo creación activado automáticamente (datos restaurados)"
                )
                self.script_object_interactor._update_create_mode_display()
                self.script_object_interactor._print_prompt()

        # Copiar overrides del script_object al interactor si existen (al editar)
        if self.script_object_interactor:
            if hasattr(self, "layer_overrides") and self.layer_overrides:
                self.script_object_interactor.layer_overrides = (
                    self.layer_overrides.copy()
                )
                print(
                    f"[SO] ✓ {len(self.layer_overrides)} layer overrides restaurados al interactor"
                )
            if hasattr(self, "distribution_overrides") and self.distribution_overrides:
                self.script_object_interactor.distribution_overrides = (
                    self.distribution_overrides.copy()
                )
                print(
                    f"[SO] ✓ {len(self.distribution_overrides)} distribution overrides restaurados al interactor"
                )
            if hasattr(self, "attribute_overrides") and self.attribute_overrides:
                self.script_object_interactor.attribute_overrides = (
                    self.attribute_overrides.copy()
                )
                print(
                    f"[SO] ✓ {len(self.attribute_overrides)} attribute overrides restaurados al interactor"
                )

    def start_next_input(self):
        """Limpia solo el interactor (preview, etc.). No borra saved_paths ni saved_segments
        para que la polilínea guardada se mantenga al pulsar 'Seleccionar punto' (1015) o 'Agregar elemento' (1016).
        """
        try:
            # En algunos flujos (por ejemplo, cuando la creación se cancela por falta de atributo
            # de padre pmp_pare) queremos mantener el modo de edición de layers activo incluso
            # después de que Allplan invoque start_next_input tras ESC.
            if getattr(self, "_suppress_start_next_cleanup", False):
                print(
                    "[SO] start_next_input: limpieza suprimida (cancelación de creación; "
                    "se mantiene edición de layers activa)."
                )
                # Resetear la bandera para futuras llamadas
                self._suppress_start_next_cleanup = False
                return

            if self.script_object_interactor is not None:
                self.script_object_interactor._cleanup_resources()
            self.script_object_interactor = None
            print("[SO] Resources cleaned up in start_next_input")

        except Exception as ex:
            print(f"[SO] Error during cleanup in start_next_input: {ex}")
            # Ensure interactor is still set to None even if cleanup fails
            self.script_object_interactor = None

    def execute(self):
        from CreateElementResult import CreateElementResult

        if not self.saved_paths and not self.saved_segments:
            return CreateElementResult([])

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        elements = []

        # Creo elementos desde saved_segments (con información de sección)
        for segment_info in self.saved_segments:
            if len(segment_info["points"]) >= 2:
                line = AllplanGeo.Line3D(
                    segment_info["points"][0], segment_info["points"][1]
                )
                segment_prop = AllplanBaseElements.CommonProperties()
                segment_prop.GetGlobalProperties()
                segment_prop = self._get_properties_for_diameter(
                    segment_prop, segment_info.get("diameter", 110.0)
                )
                elements.append(AllplanBasisElements.ModelElement3D(segment_prop, line))

        # Mantener compatibilidad con saved_paths
        for pts in self.saved_paths:
            if len(pts) >= 2:
                poly = AllplanGeo.Polyline3D()
                for pt in pts:
                    poly += pt
                elements.append(AllplanBasisElements.ModelElement3D(com_prop, poly))

        return CreateElementResult(elements)

    def _get_properties_for_diameter(self, base_prop, diameter: float):
        prop = AllplanBaseElements.CommonProperties()
        prop.GetGlobalProperties()
        return prop

    def _build_rotation_matrix_for_element(self, base_point: AllplanGeo.Point3D):
        """
        Construye una Matrix3D con las rotaciones definidas en la paleta (RotX, RotY, RotZ)
        y traslación al punto base indicado.
        """
        mat = AllplanGeo.Matrix3D()

        def _get_angle(name: str) -> float:
            try:
                param = getattr(self.build_ele, name, None)
                if param is None:
                    return 0.0
                # En la paleta es ValueType Double, el valor real está en .value
                raw = getattr(param, "value", param)
                return float(raw or 0.0)
            except Exception:
                return 0.0

        rot_x = _get_angle("RotX")
        rot_y = _get_angle("RotY")
        rot_z = _get_angle("RotZ")

        # Ejes de rotación
        axis_x = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
        )
        axis_y = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
        )
        axis_z = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
        )

        # Rotaciones en grados → usar el helper de Allplan para ángulos
        if abs(rot_x) > 1e-6:
            mat_x = AllplanGeo.Matrix3D()
            mat_x.SetRotation(axis_x, AllplanGeo.Angle(math.radians(rot_x)))
            mat = mat_x * mat
        if abs(rot_y) > 1e-6:
            mat_y = AllplanGeo.Matrix3D()
            mat_y.SetRotation(axis_y, AllplanGeo.Angle(math.radians(rot_y)))
            mat = mat_y * mat
        if abs(rot_z) > 1e-6:
            mat_z = AllplanGeo.Matrix3D()
            mat_z.SetRotation(axis_z, AllplanGeo.Angle(math.radians(rot_z)))
            mat = mat_z * mat

        # Traslación final al punto base
        mat.SetTranslation(
            AllplanGeo.Vector3D(base_point.X, base_point.Y, base_point.Z)
        )
        return mat

    def _get_element_model_list_agua(self, build_ele, doc, element_type: str):
        """Obtiene el model_list 3D de un elemento definido de Agua (vía BaseDefinedElement.generate_preview)."""
        element_type = (element_type or "").strip().lower()
        elem = _agua_defined_elements.get(element_type)
        if elem is None:
            return []
        try:
            return elem.generate_preview(build_ele, doc) or []
        except Exception as ex:
            print(
                f"[SO] Error obteniendo model_list para preview de {element_type}: {ex}"
            )
        return []

    def _create_single_element_agua(self, build_ele, doc, element_type: str, p_mid):
        """Crea un solo elemento 3D Agua (Colze, T sortida, Clau de Pas, Taps) vía BaseDefinedElement.generate_final_3d."""
        element_type = (element_type or "").strip().lower()
        elem = _agua_defined_elements.get(element_type)
        if elem is None:
            return False
        try:
            model_list = elem.generate_final_3d(build_ele, doc)
            if not model_list:
                return False
            mat = self._build_rotation_matrix_for_element(p_mid)
            AllplanBaseElements.CreateElements(doc, mat, model_list, [], None)
            return True
        except Exception as ex:
            print(f"[SO] Error creando elemento {element_type} en punto libre: {ex}")
        return False

    def _create_elements_from_free_placed_points(self, coord_input=None):
        """
        Crea los elementos 3D desde free_placed_points y vacía la lista (módulo ElementosDefinidos).
        coord_input: opcional (ej. intr.coord_input).
        """
        created = ed_create_elements_from_free_placed_points(
            self,
            coord_input or getattr(self, "coord_input", None),
            self._create_single_element_agua,
        )
        print(f"[SO] Finalizar puntos libres: creados {created} elemento(s) 3D.")

    def _finalize_and_create_now(self):
        """
        Al finalizar (ESC / botón 1003):
        - usamos las polilíneas guardadas (saved_paths)
        - por cada tramo creamos un TUBO de polietileno IS
        - en giros 90° creamos CODO
        - en cambios de diámetro sobre tramo recto creamos MANGUITO
        - en nodos con 3 tramos (2 colineales + 1 rama) creamos una TE

        Returns:
            True si la creación se completó (elementos creados y datos limpiados).
            False si el usuario canceló (p. ej. pmp_pare) o no se creó nada; en ese caso
            los datos se mantienen y el caller no debe cerrar el input.
        """
        # Variable para controlar si se canceló la creación (para mantener los datos)
        creation_cancelled = False

        try:
            if not self.saved_paths:
                print("[SO] No hay paths guardados para crear")
                return False

            doc = self.coord_input.GetInputViewDocument()
            elems = []
            # Diccionario para almacenar la distribución de cada elemento por índice
            # {elemento_index: distribution_type}
            elem_distribution_map = {}

            def _key_from_point(pt):
                return (round(pt.X, 3), round(pt.Y, 3), round(pt.Z, 3))

            # Construir vertex_map y te_vertices antes de crear manguitos
            vertex_map = {}
            for path_idx, pts in enumerate(self.saved_paths):
                for seg_idx in range(len(pts) - 1):
                    p_start = pts[seg_idx]
                    p_end = pts[seg_idx + 1]
                    for is_start, pt, other in (
                        (True, p_start, p_end),
                        (False, p_end, p_start),
                    ):
                        key = _key_from_point(pt)
                        vertex_map.setdefault(key, []).append(
                            {
                                "path_idx": path_idx,
                                "seg_idx": seg_idx,
                                "is_start": is_start,
                                "pt": pt,
                                "other": other,
                            }
                        )
            te_vertices = set()
            for key, seg_list in vertex_map.items():
                if len(seg_list) == 3:
                    te_vertices.add(key)

            # -----------------------------
            # PASADA PREVIA: ANALIZAR TES PARA ROTACIÓN DE TUBOS PERPENDICULARES
            # Analizar las tes ANTES de crear los fittings para almacenar información de rotación
            # Esto permite que los codos que conectan tubos verticales con horizontales
            # puedan usar esta información para orientarse correctamente
            # -----------------------------
            # Limpiar e inicializar diccionarios para almacenar rotaciones necesarias
            # IMPORTANTE: Limpiar siempre al inicio para evitar que datos de ejecuciones anteriores
            # interfieran cuando hay múltiples elementos
            self.branch_tube_rotation_needed = {}
            self.branch_tube_direction = {}

            # Analizar todas las tes para detectar casos donde el tubo perpendicular necesita rotación
            for key, seg_list in vertex_map.items():
                # Necesitamos exactamente 3 segmentos para una Te
                if len(seg_list) != 3:
                    continue

                cx, cy, cz = key
                center_pt = AllplanGeo.Point3D(cx, cy, cz)

                # Vectores normalizados desde el nodo
                def _norm_vec(info):
                    op = info["other"]
                    vx = op.X - center_pt.X
                    vy = op.Y - center_pt.Y
                    n = math.hypot(vx, vy)
                    if n < 1e-6:
                        return (0.0, 0.0)
                    return (vx / n, vy / n)

                def _norm_vec_3d(info):
                    """Vector normalizado 3D desde el nodo, incluyendo componente Z"""
                    op = info["other"]
                    vx = op.X - center_pt.X
                    vy = op.Y - center_pt.Y
                    vz = op.Z - center_pt.Z
                    n = math.sqrt(vx * vx + vy * vy + vz * vz)
                    if n < 1e-6:
                        return (0.0, 0.0, 0.0)
                    return (vx / n, vy / n, vz / n)

                # Decidir main (2 colineales) y rama por geometría (igual que en creación de T)
                dirs_2d = [_norm_vec(info) for info in seg_list]
                dot_01 = dirs_2d[0][0] * dirs_2d[1][0] + dirs_2d[0][1] * dirs_2d[1][1]
                dot_02 = dirs_2d[0][0] * dirs_2d[2][0] + dirs_2d[0][1] * dirs_2d[2][1]
                dot_12 = dirs_2d[1][0] * dirs_2d[2][0] + dirs_2d[1][1] * dirs_2d[2][1]
                best_pair = min(
                    [(dot_01, 0, 1, 2), (dot_02, 0, 2, 1), (dot_12, 1, 2, 0)],
                    key=lambda x: x[0],
                )
                dot_main, i, j, k = best_pair
                if dot_main > -0.5:
                    continue
                main_infos = [seg_list[i], seg_list[j]]
                branch_info = seg_list[k]
                branch_path_idx = branch_info["path_idx"]

                v_main1 = dirs_2d[i]
                v_main2 = dirs_2d[j]
                v_branch = _norm_vec_3d(branch_info)

                # Tomar uno como dirección base
                main_vec = v_main1

                # Elegir sentido del eje para que la rama coincida
                def _branch_from_main(mvec):
                    mx, my = mvec
                    return (my, mx)

                cand1_main = main_vec
                cand2_main = (-main_vec[0], -main_vec[1])

                def _dot(a, b):
                    return a[0] * b[0] + a[1] * b[1]

                score1 = _dot(_branch_from_main(cand1_main), v_branch)
                score2 = _dot(_branch_from_main(cand2_main), v_branch)

                if score2 > score1:
                    main_dir_vec = cand2_main
                else:
                    main_dir_vec = cand1_main

                # Calcular ángulo del tramo principal
                ang = math.atan2(main_dir_vec[1], main_dir_vec[0])
                ang_degrees = math.degrees(ang)

                # Normalizar ángulo a rango -180 a 180
                while ang_degrees > 180:
                    ang_degrees -= 360
                while ang_degrees < -180:
                    ang_degrees += 360

                # Verificar si el tramo principal está en diagonal (45°, 135°, 225°, 315°)
                is_main_diagonal = (
                    abs(ang_degrees - 45.0) < 10.0
                    or abs(ang_degrees - 135.0) < 10.0
                    or abs(ang_degrees - 225.0) < 10.0
                    or abs(ang_degrees - 315.0) < 10.0
                    or abs(ang_degrees - (-45.0)) < 10.0
                    or abs(ang_degrees - (-135.0)) < 10.0
                )

                # Verificar si la rama perpendicular está elevada en Z
                bz = v_branch[2]
                branch_elevated = abs(bz) > 0.5  # Rama principalmente en Z
                branch_points_up = bz > 0.1  # Rama apunta hacia +Z
                branch_points_down = bz < -0.1  # Rama apunta hacia -Z

                # Si ambas condiciones se cumplen, almacenar el ángulo para el tubo perpendicular
                if is_main_diagonal and branch_elevated:
                    # Los diccionarios ya están inicializados y limpios al inicio de la función
                    self.branch_tube_rotation_needed[branch_path_idx] = ang

                    # Almacenar la dirección de la rama: "+Z" o "-Z"
                    branch_direction = "+Z" if branch_points_up else "-Z"
                    self.branch_tube_direction[branch_path_idx] = branch_direction

                    print(
                        f"[DBG] ✅ PASADA PREVIA: Te detectada con tramo principal en diagonal ({ang_degrees:.1f}°) "
                        f"y rama perpendicular elevada en Z (z={bz:.3f}, dirección={branch_direction}). "
                        f"Marcando tubo perpendicular (path={branch_path_idx}) para rotación de {ang_degrees:.1f}°. "
                        f"Ángulo almacenado: {ang:.4f} rad"
                    )

            # =======================================================
            # 1) FITTINGS (CODOS / MANGUITOS) + REGISTRO DE RECORTES
            # 2) TUBOS (SIEMPRE todos los tramos)
            # =======================================================

            # Reset recortes para esta ejecución
            self.segment_cuts = {}

            for path_idx, pts in enumerate(self.saved_paths):
                if len(pts) < 2:
                    continue

                n = len(pts)

                # -----------------------------
                # PASADA 1: VÉRTICES (fittings)
                # i es el índice del VÉRTICE (p_curr = pts[i])
                # afecta a seg_left=i-1 y seg_right=i
                # -----------------------------
                for i in range(1, n - 1):
                    p_prev = pts[i - 1]
                    p_curr = pts[i]
                    p_next = pts[i + 1]

                    d1 = self._get_segment_diameter(
                        path_idx, i - 1, default=20.0
                    )  # seg_left
                    d2 = self._get_segment_diameter(
                        path_idx, i, default=20.0
                    )  # seg_right

                    is_90 = self._is_90_deg_turn(p_prev, p_curr, p_next)
                    print(
                        f"[DBG] vértice path={path_idx} i={i} d1={d1} d2={d2} is_90={is_90}"
                    )

                    if is_90:
                        # Si en este vértice hay una T (3 segmentos), no crear codo pero sí registrar recortes T
                        key_curr = _key_from_point(p_curr)
                        if key_curr in te_vertices:
                            print(
                                f"[DBG] Saltando codo en vértice {i} (hay T en este punto)"
                            )
                            self._register_te_cuts(path_idx, key_curr, vertex_map)
                            continue
                        # ============================
                        # RECORTE DE TUBOS POR CODO
                        # ============================
                        # REGLA: En codos NO se permite cambio de diámetro.
                        # Si los diámetros difieren, usar el mismo diámetro para ambos segmentos.
                        di1_int = int(round(float(d1)))
                        di2_int = int(round(float(d2)))

                        if di1_int != di2_int:
                            # Determinar diámetros mayor y menor
                            diam_mayor = max(di1_int, di2_int)
                            diam_menor = min(di1_int, di2_int)

                            # Mostrar advertencia y preguntar al usuario qué diámetro desea usar
                            warning_message = (
                                f"⚠️ ADVERTENCIA: Cambio de diámetro detectado en codo\n\n"
                                f"Diámetro segmento anterior: {d1}mm\n"
                                f"Diámetro segmento siguiente: {d2}mm\n\n"
                                f"Los codos NO permiten cambio de diámetro.\n"
                                f"¿Qué diámetro desea usar para ambos segmentos?\n\n"
                                f"• Sí: Usar diámetro MAYOR ({diam_mayor}mm)\n"
                                f"• No: Usar diámetro MENOR ({diam_menor}mm)\n"
                                f"• Cancelar: No crear el codo y modificar manualmente"
                            )

                            user_response = None
                            try:
                                # Intentar usar MB_YESNOCANCEL si está disponible
                                # Si no está disponible, usar MB_YESNO y luego preguntar por el menor
                                if hasattr(PythonUtility, "MB_YESNOCANCEL"):
                                    user_response = PythonUtility.ShowMessageBox(
                                        warning_message, PythonUtility.MB_YESNOCANCEL
                                    )
                                else:
                                    # Fallback: usar MB_YESNO primero
                                    user_response = PythonUtility.ShowMessageBox(
                                        warning_message, PythonUtility.MB_YESNO
                                    )
                            except Exception as ex:
                                print(
                                    f"[DBG] Error mostrando mensaje de advertencia: {ex}"
                                )
                                # Si hay error, asumir que el usuario cancela por seguridad
                                user_response = PythonUtility.IDNO

                            # Determinar qué diámetro usar según la respuesta
                            selected_diam = None

                            if (
                                hasattr(PythonUtility, "IDCANCEL")
                                and user_response == PythonUtility.IDCANCEL
                            ):
                                # Usuario canceló: mostrar mensaje y cancelar toda la creación
                                print(
                                    f"[DBG] ⚠️ Usuario canceló la creación. "
                                    f"Conflicto en codo: seg={i-1} ({d1}mm) -> seg={i} ({d2}mm)."
                                )
                                # Mostrar mensaje informativo
                                try:
                                    PythonUtility.ShowMessageBox(
                                        f"Creación cancelada.\n\n"
                                        f"Se ha cancelado toda la creación debido al conflicto de diámetros en el codo.",
                                        PythonUtility.MB_OK,
                                    )
                                except Exception as ex:
                                    print(
                                        f"[DBG] Error mostrando mensaje informativo: {ex}"
                                    )

                                # Retornar sin crear elementos
                                return
                            elif user_response == PythonUtility.IDYES:
                                # Usuario eligió usar el diámetro mayor
                                selected_diam = diam_mayor
                                print(
                                    f"[DBG] Usuario eligió usar diámetro MAYOR: {selected_diam}mm"
                                )
                            elif user_response == PythonUtility.IDNO:
                                # Si tenemos MB_YESNOCANCEL, IDNO significa usar el menor
                                # Si no, necesitamos preguntar de nuevo
                                if hasattr(PythonUtility, "MB_YESNOCANCEL"):
                                    selected_diam = diam_menor
                                    print(
                                        f"[DBG] Usuario eligió usar diámetro MENOR: {selected_diam}mm"
                                    )
                                else:
                                    # Fallback: preguntar si quiere usar el menor
                                    menor_message = (
                                        f"¿Desea usar el diámetro MENOR ({diam_menor}mm) para ambos segmentos?\n\n"
                                        f"Si cancela, se cancelará toda la creación."
                                    )
                                    menor_response = None
                                    try:
                                        menor_response = PythonUtility.ShowMessageBox(
                                            menor_message, PythonUtility.MB_YESNO
                                        )
                                    except Exception as ex:
                                        print(
                                            f"[DBG] Error mostrando diálogo de diámetro menor: {ex}"
                                        )
                                        menor_response = PythonUtility.IDNO

                                    if menor_response == PythonUtility.IDYES:
                                        selected_diam = diam_menor
                                        print(
                                            f"[DBG] Usuario eligió usar diámetro MENOR: {selected_diam}mm"
                                        )
                                    else:
                                        # Usuario canceló: mostrar mensaje y cancelar toda la creación
                                        print(
                                            f"[DBG] ⚠️ Usuario canceló la creación. "
                                            f"Conflicto en codo: seg={i-1} ({d1}mm) -> seg={i} ({d2}mm)."
                                        )
                                        # Mostrar mensaje informativo
                                        try:
                                            PythonUtility.ShowMessageBox(
                                                f"Creación cancelada.\n\n"
                                                f"Se ha cancelado toda la creación debido al conflicto de diámetros en el codo.",
                                                PythonUtility.MB_OK,
                                            )
                                        except Exception as ex:
                                            print(
                                                f"[DBG] Error mostrando mensaje informativo: {ex}"
                                            )

                                        # Retornar sin crear elementos
                                        return

                            # Aplicar el diámetro seleccionado
                            if selected_diam is not None:
                                elbow_diam = selected_diam

                                # Actualizar el diámetro del segmento que no coincide
                                if di1_int != selected_diam:
                                    # Actualizar segmento izquierdo (i-1)
                                    self._update_segment_diameter(
                                        path_idx, i - 1, float(selected_diam)
                                    )
                                    print(
                                        f"[DBG]   Segmento izquierdo (seg={i-1}) actualizado de {di1_int}mm a {selected_diam}mm"
                                    )

                                if di2_int != selected_diam:
                                    # Actualizar segmento derecho (i)
                                    self._update_segment_diameter(
                                        path_idx, i, float(selected_diam)
                                    )
                                    print(
                                        f"[DBG]   Segmento derecho (seg={i}) actualizado de {di2_int}mm a {selected_diam}mm"
                                    )

                                # Actualizar d1 y d2 para usar el diámetro unificado
                                d1 = float(selected_diam)
                                d2 = float(selected_diam)
                            else:
                                # No se seleccionó diámetro, no crear el codo
                                print(
                                    f"[DBG] No se seleccionó diámetro. Codo NO creado."
                                )
                                continue
                        else:
                            elbow_diam = di1_int

                        trim = ELBOW_TRIM_BY_DIAM.get(elbow_diam, 0.0)

                        if trim > 0.0:
                            # tramo antes del vértice: seg_left = i-1 → recorta en END
                            cuts_left = self.segment_cuts.setdefault(
                                (path_idx, i - 1), {"start": 0.0, "end": 0.0}
                            )
                            cuts_left["end"] += float(trim)

                            # tramo después del vértice: seg_right = i → recorta en START
                            cuts_right = self.segment_cuts.setdefault(
                                (path_idx, i), {"start": 0.0, "end": 0.0}
                            )
                            cuts_right["start"] += float(trim)

                            print(
                                f"[DBG] Elbow cuts path={path_idx}: "
                                f"seg_left={i-1} end-={trim}mm, "
                                f"seg_right={i} start-={trim}mm (diam={elbow_diam})"
                            )
                        else:
                            print(f"[DBG] No elbow trim rule for diam={elbow_diam}")

                        # ============================
                        # CREAR CODO (sin tocar tu método)
                        # ============================
                        # Usar el diámetro unificado (ya se normalizó arriba si había diferencia)
                        # d1 y d2 ya son iguales si había diferencia, así que usar cualquiera
                        elbow_diam = int(round(float(d1)))

                        # Obtener tipo de distribución de ambos segmentos
                        dist_type_prev = self._get_segment_distribution_type(
                            path_idx, i - 1, "IS"
                        )
                        dist_type_next = self._get_segment_distribution_type(
                            path_idx, i, "IS"
                        )

                        # Si hay cambio de distribución, siempre usar IS para el codo
                        # Ejemplos:
                        # - TD -> IS: codo IS
                        # - IS -> TD: codo IS
                        if dist_type_prev != dist_type_next:
                            dist_type = "IS"
                            print(
                                f"[DBG] Cambio de distribución en codo: "
                                f"seg_left={i-1} ({dist_type_prev}) -> seg_right={i} ({dist_type_next}), "
                                f"usando codo IS (siempre IS cuando hay cambio)"
                            )
                        else:
                            dist_type = dist_type_prev  # Usar la del segmento (ambos son iguales)
                            print(f"[DBG] Codo con distribución uniforme: {dist_type}")

                        # Verificar si hay override de distribución desde preview mode
                        if (
                            hasattr(self, "distribution_overrides")
                            and self.distribution_overrides
                        ):
                            elbow_key = ("elbow", path_idx, i)
                            if elbow_key in self.distribution_overrides:
                                override_dist = self.distribution_overrides[elbow_key]
                                print(
                                    f"[SO] *** APLICANDO DISTRIBUCIÓN OVERRIDE a Codo {elbow_key}: → '{override_dist}'"
                                )
                                dist_type = override_dist

                        # Determinar punto previo previo si está disponible (para detectar segmentos horizontales previos)
                        p_prev_prev = None
                        if i >= 2:
                            p_prev_prev = pts[i - 2]

                        def _create_elbow_wrapped(_be, a, b, c):
                            return self._create_elbow(
                                a, b, c, path_idx, i - 1, dist_type, p_prev_prev
                            )

                        elbow_elems = call_with_build_ele_attrs(
                            self.build_ele,
                            {"DiametroAplicar": elbow_diam},
                            _create_elbow_wrapped,
                            p_prev,
                            p_curr,
                            p_next,
                        )

                        # Aplicar atributos desde attribute_overrides si existe
                        if (
                            hasattr(self, "attribute_overrides")
                            and self.attribute_overrides
                        ):
                            elbow_key = ("elbow", path_idx, i)
                            if elbow_key in self.attribute_overrides:
                                attr_value = self.attribute_overrides[elbow_key]
                                print(
                                    f"[SO] *** APLICANDO ATRIBUTOS a Codo {elbow_key}: → '{attr_value}'"
                                )
                                custom_attrs = {"NomIS": attr_value}
                                # dist_type ya está calculado arriba (línea ~3185)
                                for elem in elbow_elems:
                                    try:
                                        _set_attr_padre(
                                            elem, custom_attrs, doc, dist_type
                                        )
                                        attrs_applied = (
                                            "6_CC_IS y pmp_pare"
                                            if dist_type == "IS"
                                            else "pmp_pare"
                                        )
                                        print(
                                            f"[SO]   Codo elemento ({dist_type}): Atributos {attrs_applied} = '{attr_value}'"
                                        )
                                    except Exception as ex:
                                        print(
                                            f"[SO] Error aplicando atributos a elemento Codo: {ex}"
                                        )

                        # Almacenar distribución para cada elemento del codo
                        start_idx = len(elems)
                        elems.extend(elbow_elems)
                        for i, elem in enumerate(elbow_elems):
                            elem_distribution_map[start_idx + i] = dist_type
                        continue

                    straight = self._is_straight_turn(p_prev, p_curr, p_next)
                    print(f"[DBG]   straight={straight}")

                    # --- MANGUITO: cambio de diámetro colineal ---
                    # ==========================================
                    # RECORTES PARA LOS TUBOS ADYACENTES (MANGUITO)
                    # ==========================================
                    if straight:
                        key_curr = _key_from_point(p_curr)

                        # Si hay TE en ese vértice, no creo manguito aquí; solo registro recortes TE
                        if key_curr in te_vertices:
                            print("[DBG]   👉 Hay TE, registro recortes TE")
                            self._register_te_cuts(path_idx, key_curr, vertex_map)
                            continue

                        di1 = int(round(float(d1)))
                        di2 = int(round(float(d2)))

                        # key exacta y key ordenada (por si tu map está en un sentido u otro)
                        k_exact = (di1, di2)
                        k_sorted = tuple(sorted((di1, di2)))

                        trim = MANGUITO_TRIM_BY_DIAM.get(k_exact)
                        if trim is None:
                            trim = MANGUITO_TRIM_BY_DIAM.get(k_sorted)

                        print(
                            f"[DBG] Manguito diam: d1={d1} d2={d2} -> di1={di1} di2={di2} k_exact={k_exact} k_sorted={k_sorted} trim={trim}"
                        )

                        if trim is None:
                            print(
                                f"[DBG] No trim rule for {k_exact} / {k_sorted} -> igual creo manguito sin recortes"
                            )
                            trim = 0.0

                        # ✅ Registrar recortes SIEMPRE que haya regla (incluye 20-20 y 25-25)
                        if trim > 0.0:
                            cuts_left = self.segment_cuts.setdefault(
                                (path_idx, i - 1), {"start": 0.0, "end": 0.0}
                            )
                            cuts_right = self.segment_cuts.setdefault(
                                (path_idx, i), {"start": 0.0, "end": 0.0}
                            )

                            before_left = dict(cuts_left)
                            before_right = dict(cuts_right)

                            cuts_left["end"] += float(trim)
                            cuts_right["start"] += float(trim)

                            print(
                                f"[DBG] Manguito CUTS APPLY path={path_idx} i={i} "
                                f"seg_left={i-1} {before_left} -> {cuts_left} | "
                                f"seg_right={i} {before_right} -> {cuts_right}"
                            )

                        # ✅ Crear SIEMPRE el manguito (aunque sea 20-20 / 25-25)
                        # Obtener tipo de distribución del segmento
                        dist_type = self._get_segment_distribution_type(
                            path_idx, i - 1, "IS"
                        )

                        # Verificar si hay override de distribución desde preview mode
                        if (
                            hasattr(self, "distribution_overrides")
                            and self.distribution_overrides
                        ):
                            manguito_key = ("manguito", path_idx, i)
                            if manguito_key in self.distribution_overrides:
                                override_dist = self.distribution_overrides[
                                    manguito_key
                                ]
                                print(
                                    f"[SO] *** APLICANDO DISTRIBUCIÓN OVERRIDE a Manguito {manguito_key}: → '{override_dist}'"
                                )
                                dist_type = override_dist

                        print("[DBG]   👉 Creando MANGUITO")
                        mang_elems = self._create_manguito(
                            p_prev, p_curr, p_next, di1, di2, path_idx, i - 1, dist_type
                        )  # 👈 PASO INTS

                        # Clave igual que en _generate_elements_for_preview: ('manguito', path_idx, vertex_idx)
                        manguito_key = ("manguito", path_idx, i)

                        # Aplicar layer override si existe (misma lógica que en preview)
                        if hasattr(self, "layer_overrides") and self.layer_overrides:
                            if manguito_key in self.layer_overrides:
                                override_layer = self.layer_overrides[manguito_key]
                                print(
                                    f"[SO] *** APLICANDO LAYER OVERRIDE a Manguito {manguito_key}: → {override_layer}"
                                )
                                # Aplicar el layer override a todos los elementos del manguito
                                for elem in mang_elems:
                                    try:
                                        com_prop = elem.GetCommonProperties()
                                        if com_prop is None:
                                            com_prop = (
                                                AllplanBaseElements.CommonProperties()
                                            )
                                            com_prop.GetGlobalProperties()
                                        old_layer = com_prop.Layer
                                        com_prop.Layer = override_layer
                                        elem.SetCommonProperties(com_prop)
                                        print(
                                            f"[SO]   Manguito elemento: Layer {old_layer} → {override_layer}"
                                        )
                                    except Exception as ex:
                                        print(
                                            f"[SO] Error aplicando layer override a elemento Manguito: {ex}"
                                        )
                            else:
                                print(
                                    f"[SO] DEBUG: No hay override para Manguito {manguito_key} (keys disponibles: {list(self.layer_overrides.keys())})"
                                )

                        # Aplicar atributos desde attribute_overrides si existe (independiente del layer)
                        if (
                            hasattr(self, "attribute_overrides")
                            and self.attribute_overrides
                            and manguito_key in self.attribute_overrides
                        ):
                            attr_value = self.attribute_overrides[manguito_key]
                            print(
                                f"[SO] *** APLICANDO ATRIBUTOS a Manguito {manguito_key}: → '{attr_value}'"
                            )
                            custom_attrs = {"NomIS": attr_value}
                            for elem in mang_elems:
                                try:
                                    _set_attr_padre(elem, custom_attrs, doc, dist_type)
                                    attrs_applied = (
                                        "6_CC_IS y pmp_pare"
                                        if dist_type == "IS"
                                        else "pmp_pare"
                                    )
                                    print(
                                        f"[SO]   Manguito elemento ({dist_type}): Atributos {attrs_applied} = '{attr_value}'"
                                    )
                                except Exception as ex:
                                    print(
                                        f"[SO] Error aplicando atributos a elemento Manguito: {ex}"
                                    )

                        # Almacenar distribución para cada elemento del manguito
                        start_idx = len(elems)
                        elems.extend(mang_elems)
                        for i, elem in enumerate(mang_elems):
                            elem_distribution_map[start_idx + i] = dist_type

            # -----------------------------
            # PASADA 2: SEGMENTOS (TUBOS)
            # Se crean SIEMPRE todos los tramos
            # Si un segmento excede MAX_SEGMENT_LENGTH, se divide automáticamente
            # -----------------------------
            for path_idx, pts in enumerate(self.saved_paths):
                if len(pts) < 2:
                    continue

                for seg_idx in range(len(pts) - 1):
                    p0 = pts[seg_idx]
                    p1 = pts[seg_idx + 1]

                    # Calcular longitud del segmento
                    vx = p1.X - p0.X
                    vy = p1.Y - p0.Y
                    vz = p1.Z - p0.Z
                    length = math.sqrt(vx * vx + vy * vy + vz * vz)

                    # Obtener diámetro y tipo de distribución del segmento
                    d_seg = self._get_segment_diameter(path_idx, seg_idx, default=20.0)
                    di_seg = int(round(float(d_seg)))
                    dist_type = self._get_segment_distribution_type(
                        path_idx, seg_idx, "IS"
                    )

                    # Verificar si hay override de distribución desde preview mode
                    if (
                        hasattr(self, "distribution_overrides")
                        and self.distribution_overrides
                    ):
                        tube_key = ("tube", path_idx, seg_idx)
                        if tube_key in self.distribution_overrides:
                            override_dist = self.distribution_overrides[tube_key]
                            print(
                                f"[SO] *** APLICANDO DISTRIBUCIÓN OVERRIDE a Tubo {tube_key}: → '{override_dist}'"
                            )
                            dist_type = override_dist

                    print(
                        f"[DBG] >>> creando tubo path={path_idx} seg={seg_idx} length={length:.2f}mm diam={di_seg} dist={dist_type}"
                    )

                    # dist_type ya tiene el override aplicado arriba si existe
                    # Usar el mismo valor para todos los sub-segmentos si se divide
                    segment_dist_override = dist_type

                    # Obtener longitud máxima según el tipo de tubo seleccionado
                    max_segment_length = self._get_max_segment_length(dist_type)

                    # Si el segmento excede la longitud máxima, dividirlo
                    # IMPORTANTE: La longitud máxima se considera DESPUÉS de los recortes
                    # Si max_segment_length = 5000mm y trim = 14.5mm, creamos tubos de 5014.5mm
                    # y luego recortamos 14.5mm, resultando en 5000mm
                    if length > max_segment_length:
                        print(
                            f"[DBG] Segmento excede longitud máxima ({max_segment_length}mm), dividiendo..."
                        )

                        # Obtener recortes del segmento original (si existen)
                        # Estos recortes pueden venir de manguitos, codos o T en los vértices
                        seg_key_original = (path_idx, seg_idx)
                        original_cuts = getattr(self, "segment_cuts", {}).get(
                            seg_key_original, {"start": 0.0, "end": 0.0}
                        )
                        original_start_trim = float(
                            original_cuts.get("start", 0.0) or 0.0
                        )
                        original_end_trim = float(original_cuts.get("end", 0.0) or 0.0)
                        print(
                            f"[DBG] Recortes originales del segmento: start={original_start_trim}mm, end={original_end_trim}mm"
                        )

                        # Vector unitario
                        ux = vx / length
                        uy = vy / length
                        uz = vz / length

                        # Obtener trim para manguitos del mismo diámetro
                        k_same_diam = (di_seg, di_seg)
                        trim_manguito = MANGUITO_TRIM_BY_DIAM.get(k_same_diam, 0.0)
                        print(
                            f"[DBG] Trim para manguitos intermedios (diámetro {di_seg}mm): {trim_manguito}mm"
                        )

                        # IMPORTANTE: Cada sub-segmento tiene su propio trim:
                        # - Primer sub-segmento: trim_start (del segmento original) + trim_manguito (si hay manguito después)
                        # - Sub-segmentos intermedios: trim_manguito (inicio) + trim_manguito (fin)
                        # - Último sub-segmento: trim_manguito (inicio) + trim_end (del segmento original)
                        #
                        # Para calcular cuántos sub-segmentos necesitamos, usamos una estimación conservadora:
                        # Asumimos que cada sub-segmento tendrá al menos trim_manguito en ambos extremos
                        # excepto el primero (que puede tener original_start_trim) y el último (que puede tener original_end_trim)

                        # Calcular longitud máxima base para sub-segmentos intermedios
                        # (los más comunes, con manguito en ambos extremos)
                        max_length_intermediate = max_segment_length + (
                            trim_manguito * 2
                        )

                        # Calcular longitud máxima para el primer sub-segmento
                        trim_first_start = original_start_trim
                        trim_first_end = trim_manguito  # Si hay más sub-segmentos, habrá manguito después
                        max_length_first = (
                            max_segment_length + trim_first_start + trim_first_end
                        )

                        # Calcular longitud máxima para el último sub-segmento
                        trim_last_start = trim_manguito  # Si hay manguito antes
                        trim_last_end = original_end_trim
                        max_length_last = (
                            max_segment_length + trim_last_start + trim_last_end
                        )

                        # Usar el mínimo para estimar (más conservador)
                        # Esto asegura que todos los sub-segmentos quepan
                        estimated_max_length = min(
                            max_length_intermediate, max_length_first, max_length_last
                        )

                        print(
                            f"[DBG] Longitudes máximas calculadas: "
                            f"intermedio={max_length_intermediate}mm, "
                            f"primero={max_length_first}mm, "
                            f"último={max_length_last}mm"
                        )
                        print(
                            f"[DBG] Usando longitud estimada: {estimated_max_length}mm para calcular número de sub-segmentos"
                        )

                        # Calcular cuántos sub-segmentos necesitamos (estimación)
                        num_sub_segments = int(math.ceil(length / estimated_max_length))
                        print(
                            f"[DBG] Dividiendo en aproximadamente {num_sub_segments} sub-segmentos"
                        )

                        # Dividir en segmentos de longitud máxima
                        # IMPORTANTE: Los puntos se calculan considerando que los recortes se aplicarán después
                        # El manguito se coloca en el punto de unión, pero los tubos deben terminar antes
                        current_pos = 0.0
                        sub_seg_idx = 0
                        prev_p_end = None

                        while current_pos < length - 1e-3:
                            # Calcular longitud del sub-segmento actual
                            # IMPORTANTE: Cada sub-segmento tiene su propio trim, calcular su longitud máxima específica
                            remaining = length - current_pos

                            # Determinar qué tipo de sub-segmento es este
                            is_first = sub_seg_idx == 0

                            # Calcular trim específico para este sub-segmento
                            if is_first:
                                # Primer sub-segmento: trim_start (original) + trim_manguito (si hay más sub-segmentos)
                                trim_this_start = original_start_trim
                                # Verificar si habrá más sub-segmentos después
                                # Usar una estimación conservadora: si remaining > max_segment_length, habrá más
                                will_have_manguito_after = (
                                    remaining > max_segment_length + 1e-3
                                )
                                trim_this_end = (
                                    trim_manguito if will_have_manguito_after else 0.0
                                )
                                max_length_this = (
                                    max_segment_length + trim_this_start + trim_this_end
                                )
                                print(
                                    f"[DBG]   Sub-segmento {sub_seg_idx} (PRIMERO): trim_start={trim_this_start}mm, trim_end={trim_this_end}mm, max_length={max_length_this}mm"
                                )
                            else:
                                # No es el primero, verificar si es el último
                                # Calcular cuánto queda después de un sub-segmento intermedio típico
                                remaining_after_intermediate = remaining - (
                                    max_segment_length + trim_manguito * 2
                                )
                                is_last = remaining_after_intermediate < 1e-3

                                if is_last:
                                    # Último sub-segmento: trim_manguito (si hay manguito antes) + trim_end (original)
                                    trim_this_start = trim_manguito  # Siempre hay manguito antes si no es el primero
                                    trim_this_end = original_end_trim
                                    max_length_this = (
                                        max_segment_length
                                        + trim_this_start
                                        + trim_this_end
                                    )
                                    print(
                                        f"[DBG]   Sub-segmento {sub_seg_idx} (ÚLTIMO): trim_start={trim_this_start}mm, trim_end={trim_this_end}mm, max_length={max_length_this}mm"
                                    )
                                else:
                                    # Sub-segmento intermedio: trim_manguito en ambos extremos
                                    trim_this_start = trim_manguito
                                    trim_this_end = trim_manguito
                                    max_length_this = (
                                        max_segment_length
                                        + trim_this_start
                                        + trim_this_end
                                    )
                                    print(
                                        f"[DBG]   Sub-segmento {sub_seg_idx} (INTERMEDIO): trim_start={trim_this_start}mm, trim_end={trim_this_end}mm, max_length={max_length_this}mm"
                                    )

                            sub_length = min(max_length_this, remaining)

                            # Punto inicial del sub-segmento (sin recortes aún)
                            # Estos puntos son los extremos teóricos del sub-segmento
                            # Los recortes se aplicarán en _create_tube_segment
                            p_start = AllplanGeo.Point3D(
                                p0.X + ux * current_pos,
                                p0.Y + uy * current_pos,
                                p0.Z + uz * current_pos,
                            )

                            # Punto final del sub-segmento (sin recortes aún)
                            p_end = AllplanGeo.Point3D(
                                p0.X + ux * (current_pos + sub_length),
                                p0.Y + uy * (current_pos + sub_length),
                                p0.Z + uz * (current_pos + sub_length),
                            )

                            # Inicializar recortes para este sub-segmento ANTES de crear el manguito
                            sub_seg_key = (path_idx, seg_idx, sub_seg_idx)
                            if not hasattr(self, "segment_cuts"):
                                self.segment_cuts = {}
                            sub_cuts = self.segment_cuts.setdefault(
                                sub_seg_key, {"start": 0.0, "end": 0.0}
                            )

                            # Aplicar recortes del segmento original:
                            # - El primer sub-segmento hereda el recorte de inicio del segmento original
                            # - El último sub-segmento hereda el recorte de fin del segmento original
                            # Usar += para acumular (igual que en segmentos normales)
                            if sub_seg_idx == 0:
                                # Primer sub-segmento: hereda el recorte de inicio
                                sub_cuts["start"] += original_start_trim
                                print(
                                    f"[DBG]   Sub-segmento {sub_seg_idx}: hereda recorte inicio={original_start_trim}mm del segmento original (total start={sub_cuts['start']}mm)"
                                )

                            # Verificar si es el último sub-segmento (usar la longitud calculada específica)
                            remaining_after = length - (current_pos + sub_length)
                            is_last_sub_segment = remaining_after < 1e-3
                            if is_last_sub_segment:
                                # Último sub-segmento: hereda el recorte de fin
                                sub_cuts["end"] += original_end_trim
                                print(
                                    f"[DBG]   Sub-segmento {sub_seg_idx}: hereda recorte fin={original_end_trim}mm del segmento original (total end={sub_cuts['end']}mm)"
                                )

                            # Si hay un sub-segmento anterior, crear manguito entre ellos
                            # IMPORTANTE: Registrar los recortes del manguito ANTES de crear los sub-segmentos
                            if prev_p_end is not None:
                                # Crear manguito en el punto de unión (p_start)
                                # El manguito se coloca en p_start, que es donde se unen los dos sub-segmentos
                                print(
                                    f"[DBG]   Creando manguito intermedio en posición {current_pos:.2f}mm"
                                )

                                # Para el manguito, necesitamos p_prev (final del sub-segmento anterior)
                                # y p_next (inicio del siguiente sub-segmento, que es p_end)
                                # p_mid es p_start (punto de unión)
                                mang_elems = self._create_manguito(
                                    prev_p_end,  # p_prev: final del sub-segmento anterior
                                    p_start,  # p_mid: punto de unión (donde se coloca el manguito)
                                    p_end,  # p_next: inicio del siguiente sub-segmento
                                    di_seg,
                                    di_seg,
                                    path_idx,
                                    seg_idx,
                                    dist_type,
                                )
                                # Almacenar distribución para cada elemento del manguito
                                start_idx = len(elems)
                                elems.extend(mang_elems)
                                for i, elem in enumerate(mang_elems):
                                    elem_distribution_map[start_idx + i] = dist_type

                                # Registrar recortes para los tubos adyacentes al manguito
                                # NOTA: El recorte del sub-segmento anterior ya se registró en la iteración anterior
                                # Solo necesitamos registrar el recorte del sub-segmento actual
                                # Usar += para acumular (igual que en segmentos normales)
                                if trim_manguito > 0.0:
                                    # Recorte para el sub-segmento actual (inicio)
                                    # El recorte del sub-segmento anterior (fin) ya se registró antes de crearlo
                                    sub_cuts["start"] += float(trim_manguito)
                                    print(
                                        f"[DBG]   Recorte inicio sub-segmento {sub_seg_idx} (manguito intermedio): +{trim_manguito}mm (total start={sub_cuts['start']}mm)"
                                    )
                                    print(
                                        f"[DBG]   → El sub-segmento {sub_seg_idx} empezará {trim_manguito}mm después del centro del manguito"
                                    )

                            # Antes de crear el sub-segmento, verificar si habrá un manguito después
                            # Si hay más sub-segmentos, registrar el recorte del manguito que vendrá
                            remaining_after_current = length - (
                                current_pos + sub_length
                            )
                            will_have_next_manguito = remaining_after_current > 1e-3

                            if will_have_next_manguito and trim_manguito > 0.0:
                                # Habrá un manguito después, registrar el recorte al final de este sub-segmento
                                sub_cuts["end"] += float(trim_manguito)
                                print(
                                    f"[DBG]   Pre-registro: Sub-segmento {sub_seg_idx} tendrá manguito después, recorte fin={trim_manguito}mm (total end={sub_cuts['end']}mm)"
                                )

                            # Crear el sub-segmento con una clave única que incluye el índice del sub-segmento
                            print(
                                f"[DBG]   Sub-segmento {sub_seg_idx}: {current_pos:.2f} -> {current_pos + sub_length:.2f}mm (length={sub_length:.2f}mm)"
                            )
                            # Usar una clave única para cada sub-segmento: (path_idx, seg_idx, sub_seg_idx)
                            # Usar segment_dist_override si existe (aplica a todos los sub-segmentos)
                            # Determinar punto previo: si es el primer sub-segmento, usar p0; si no, usar prev_p_end
                            p_prev_sub = p0 if sub_seg_idx == 0 else prev_p_end
                            tramo_elems = self._create_tube_segment(
                                p_start,
                                p_end,
                                path_idx,
                                seg_idx,
                                sub_seg_idx,
                                segment_dist_override,
                                p_prev_sub,
                            )

                            # Obtener dist_type para este sub-segmento
                            if segment_dist_override is not None:
                                dist_type = segment_dist_override
                            else:
                                dist_type = self._get_segment_distribution_type(
                                    path_idx, seg_idx, "IS"
                                )

                            # Aplicar atributos desde attribute_overrides si existe
                            if (
                                hasattr(self, "attribute_overrides")
                                and self.attribute_overrides
                            ):
                                tube_key = ("tube", path_idx, seg_idx, sub_seg_idx)
                                # En preview los tubos usan clave sin sub_seg_idx; fallback para no perder atributos
                                attr_value = self.attribute_overrides.get(
                                    tube_key
                                ) or self.attribute_overrides.get(
                                    ("tube", path_idx, seg_idx)
                                )
                                if attr_value is not None:
                                    print(
                                        f"[SO] *** APLICANDO ATRIBUTOS a Tubo {tube_key}: → '{attr_value}'"
                                    )
                                    custom_attrs = {"NomIS": attr_value}
                                    for elem in tramo_elems:
                                        try:
                                            _set_attr_padre(
                                                elem, custom_attrs, doc, dist_type
                                            )
                                            attrs_applied = (
                                                "6_CC_IS y pmp_pare"
                                                if dist_type == "IS"
                                                else "pmp_pare"
                                            )
                                            print(
                                                f"[SO]   Tubo elemento ({dist_type}): Atributos {attrs_applied} = '{attr_value}'"
                                            )
                                        except Exception as ex:
                                            print(
                                                f"[SO] Error aplicando atributos a elemento Tubo: {ex}"
                                            )

                            # Almacenar distribución para cada elemento del tubo
                            # IMPORTANTE: Siempre agregar elementos a elems, incluso si no hay atributos
                            start_idx = len(elems)
                            elems.extend(tramo_elems)
                            for i, elem in enumerate(tramo_elems):
                                elem_distribution_map[start_idx + i] = dist_type

                            # Guardar el punto final para el siguiente manguito
                            prev_p_end = p_end

                            # Avanzar posición
                            current_pos += sub_length
                            sub_seg_idx += 1
                    else:
                        # Segmento normal, crear directamente
                        # Usar dist_type que ya tiene el override aplicado si existe
                        # Determinar punto previo: si seg_idx > 0, usar el punto anterior del path
                        p_prev_normal = None
                        if seg_idx > 0:
                            p_prev_normal = pts[seg_idx - 1]
                        tramo_elems = self._create_tube_segment(
                            p0, p1, path_idx, seg_idx, None, dist_type, p_prev_normal
                        )

                        # Aplicar atributos desde attribute_overrides si existe
                        if (
                            hasattr(self, "attribute_overrides")
                            and self.attribute_overrides
                        ):
                            tube_key = ("tube", path_idx, seg_idx)
                            if tube_key in self.attribute_overrides:
                                attr_value = self.attribute_overrides[tube_key]
                                print(
                                    f"[SO] *** APLICANDO ATRIBUTOS a Tubo {tube_key}: → '{attr_value}'"
                                )
                                custom_attrs = {"NomIS": attr_value}
                                # dist_type ya tiene el override aplicado arriba si existe
                                for elem in tramo_elems:
                                    try:
                                        _set_attr_padre(
                                            elem, custom_attrs, doc, dist_type
                                        )
                                        attrs_applied = (
                                            "6_CC_IS y pmp_pare"
                                            if dist_type == "IS"
                                            else "pmp_pare"
                                        )
                                        print(
                                            f"[SO]   Tubo elemento ({dist_type}): Atributos {attrs_applied} = '{attr_value}'"
                                        )
                                    except Exception as ex:
                                        print(
                                            f"[SO] Error aplicando atributos a elemento Tubo: {ex}"
                                        )

                        # Almacenar distribución para cada elemento del tubo
                        # IMPORTANTE: Siempre agregar elementos a elems, incluso si no hay atributos
                        start_idx = len(elems)
                        elems.extend(tramo_elems)
                        for i, elem in enumerate(tramo_elems):
                            elem_distribution_map[start_idx + i] = dist_type

            # =======================================================
            # 2) DETECCIÓN DE NODOS EN T Y CREACIÓN DE TES
            # =======================================================

            # Mapa: vértice -> lista de segmentos que llegan a ese vértice
            vertex_map = {}

            for path_idx, pts in enumerate(self.saved_paths):
                for seg_idx in range(len(pts) - 1):
                    p_start = pts[seg_idx]
                    p_end = pts[seg_idx + 1]
                    for is_start, pt, other in (
                        (True, p_start, p_end),
                        (False, p_end, p_start),
                    ):
                        key = _key_from_point(pt)
                        vertex_map.setdefault(key, []).append(
                            {
                                "path_idx": path_idx,
                                "seg_idx": seg_idx,
                                "is_start": is_start,
                                "pt": pt,
                                "other": other,
                            }
                        )

            # Definir te_vertices para usarlo en la creación de manguitos
            te_vertices = set()
            for key, seg_list in vertex_map.items():
                if len(seg_list) == 3:
                    te_vertices.add(key)

            used_te_vertices = set()

            for key, seg_list in vertex_map.items():
                # Necesitamos exactamente 3 segmentos para una Te
                if len(seg_list) != 3:
                    continue

                if key in used_te_vertices:
                    continue

                cx, cy, cz = key
                center_pt = AllplanGeo.Point3D(cx, cy, cz)

                # --- 2.1) Vectores normalizados desde el nodo ---
                def _norm_vec(info):
                    op = info["other"]
                    vx = op.X - center_pt.X
                    vy = op.Y - center_pt.Y
                    n = math.hypot(vx, vy)
                    if n < 1e-6:
                        return (0.0, 0.0)
                    return (vx / n, vy / n)

                def _norm_vec_3d(info):
                    """Vector normalizado 3D desde el nodo, incluyendo componente Z"""
                    op = info["other"]
                    vx = op.X - center_pt.X
                    vy = op.Y - center_pt.Y
                    vz = op.Z - center_pt.Z
                    n = math.sqrt(vx * vx + vy * vy + vz * vz)
                    if n < 1e-6:
                        return (0.0, 0.0, 0.0)
                    return (vx / n, vy / n, vz / n)

                # --- 2.2) Decidir main (2 colineales) y rama por geometría ---
                # Si un path tiene codo en este punto (90°) y otro path llega aquí en línea
                # con uno de los lados del codo, los 2 colineales pueden ser de paths distintos.
                dirs_2d = [_norm_vec(info) for info in seg_list]
                dot_01 = dirs_2d[0][0] * dirs_2d[1][0] + dirs_2d[0][1] * dirs_2d[1][1]
                dot_02 = dirs_2d[0][0] * dirs_2d[2][0] + dirs_2d[0][1] * dirs_2d[2][1]
                dot_12 = dirs_2d[1][0] * dirs_2d[2][0] + dirs_2d[1][1] * dirs_2d[2][1]
                # El par más colineal (dot más negativo, idealmente -1) es el troncal
                best_pair = min(
                    [(dot_01, 0, 1, 2), (dot_02, 0, 2, 1), (dot_12, 1, 2, 0)],
                    key=lambda x: x[0],
                )
                dot_main, i, j, k = best_pair
                if dot_main > -0.5:
                    # No hay dos segmentos suficientemente colineales → no es T
                    continue
                main_infos = [seg_list[i], seg_list[j]]
                branch_info = seg_list[k]
                main_path_idx = main_infos[0]["path_idx"]
                branch_path_idx = branch_info["path_idx"]

                v_main1 = dirs_2d[i]
                v_main2 = dirs_2d[j]
                v_branch = _norm_vec_3d(branch_info)

                # Tomamos uno como dirección base (asociado a d_main_in)
                main_vec = v_main1

                # Dirección "cruda" del troncal según el primer tramo (E/W/N/S)
                orig_dir_main = _dir_from_delta(main_vec[0], main_vec[1], 1e-6)
                print(f"[DBG] orig_dir_main={orig_dir_main}")

                # --- 2.3) Elegir sentido del eje para que la rama coincida ---
                # En el modelo local: eje principal = +X, rama = +Y
                def _branch_from_main(mvec):
                    mx, my = mvec
                    # rotación +90° ideal sería (-my, mx), pero seguimos tu convención
                    return (my, mx)

                cand1_main = main_vec
                cand1_branch = _branch_from_main(cand1_main)

                cand2_main = (-main_vec[0], -main_vec[1])
                cand2_branch = _branch_from_main(cand2_main)

                def _dot(a, b):
                    return a[0] * b[0] + a[1] * b[1]

                score1 = _dot(cand1_branch, v_branch)
                score2 = _dot(cand2_branch, v_branch)

                if score2 > score1:
                    main_dir_vec = cand2_main
                else:
                    main_dir_vec = cand1_main

                # --- 2.4) Diámetros de los 3 tramos ---
                info1 = main_infos[0]
                info2 = main_infos[1]
                info_br = branch_info

                # Obtener diámetros de los segmentos
                d1 = self._get_segment_diameter(info1["path_idx"], info1["seg_idx"])
                d2 = self._get_segment_diameter(info2["path_idx"], info2["seg_idx"])
                d_branch = self._get_segment_diameter(
                    info_br["path_idx"], info_br["seg_idx"]
                )

                # Determinar cuál es main_in y cuál main_out según la dirección real de la polilínea
                # main_dir_vec apunta desde el nodo hacia fuera (dirección del troncal)
                # El segmento en la dirección de main_dir_vec es main_out, el opuesto es main_in
                v1 = _norm_vec(info1)
                v2 = _norm_vec(info2)

                dot1 = v1[0] * main_dir_vec[0] + v1[1] * main_dir_vec[1]
                dot2 = v2[0] * main_dir_vec[0] + v2[1] * main_dir_vec[1]

                # main_dir_vec apunta hacia el segmento con el producto punto más positivo
                if dot1 > dot2:
                    # main_dir_vec apunta hacia info2, entonces info2 es main_out, info1 es main_in
                    d_main_in = d1
                    d_main_out = d2
                else:
                    # main_dir_vec apunta hacia info1, entonces info1 es main_out, info2 es main_in
                    d_main_in = d2
                    d_main_out = d1

                print(
                    f"[DBG] Nodo Te en {key} -> "
                    f"main_path={main_path_idx}, branch_path={branch_path_idx}, "
                    f"main_dir_vec={main_dir_vec}, "
                    f"d_main_in={d_main_in}, d_main_out={d_main_out}, "
                    f"d_branch={d_branch}"
                )

                # Construir point_key y te_type ANTES de crear la Te para poder verificar overrides
                point_key = (
                    round(center_pt.X, 0),
                    round(center_pt.Y, 0),
                    round(center_pt.Z, 0),
                )

                # Determinar tipo de Te según diámetros (misma lógica que en preview)
                has_20mm = False
                has_25mm = False

                # Helper para comparar puntos
                def _points_equal_local(p1, p2, tolerance=1e-3):
                    return (
                        abs(p1.X - p2.X) < tolerance
                        and abs(p1.Y - p2.Y) < tolerance
                        and abs(p1.Z - p2.Z) < tolerance
                    )

                for info in seg_list:
                    path_idx_conn = info["path_idx"]
                    seg_idx_conn = info["seg_idx"]
                    pts_conn = self.saved_paths[path_idx_conn]
                    if seg_idx_conn < len(pts_conn) - 1:
                        p1_conn = pts_conn[seg_idx_conn]
                        p2_conn = pts_conn[seg_idx_conn + 1]
                        # Buscar diámetro del segmento
                        for seg in self.saved_segments:
                            seg_pts = seg.get("points", [])
                            if len(seg_pts) >= 2:
                                if (
                                    _points_equal_local(seg_pts[0], p1_conn)
                                    and _points_equal_local(seg_pts[1], p2_conn)
                                ) or (
                                    _points_equal_local(seg_pts[0], p2_conn)
                                    and _points_equal_local(seg_pts[1], p1_conn)
                                ):
                                    d = float(seg.get("diameter", 20.0) or 20.0)
                                    if abs(d - 20.0) < 1e-3:
                                        has_20mm = True
                                    elif abs(d - 25.0) < 1e-3:
                                        has_25mm = True
                                    break

                # Determinar tipo
                if has_20mm and has_25mm:
                    te_type = "D20-D25"
                elif has_20mm:
                    te_type = "D20-D20"
                elif has_25mm:
                    te_type = "D25-D25"
                else:
                    te_type = "D20-D20"  # Default si no se encuentra

                # Obtener tipo de distribución del segmento principal
                dist_type = self._get_segment_distribution_type(
                    info1["path_idx"], info1["seg_idx"], "IS"
                )

                # Verificar si hay override de distribución desde preview mode
                if (
                    hasattr(self, "distribution_overrides")
                    and self.distribution_overrides
                ):
                    te_key = ("te", te_type, point_key)
                    if te_key in self.distribution_overrides:
                        override_dist = self.distribution_overrides[te_key]
                        print(
                            f"[SO] *** APLICANDO DISTRIBUCIÓN OVERRIDE a Te {te_key}: → '{override_dist}'"
                        )
                        dist_type = override_dist

                te_elems = self._create_te(
                    center_pt,
                    main_dir_vec,
                    d_main_in,
                    d_main_out,
                    d_branch,
                    v_branch,
                    orig_dir_main,  # 🆕 dirección cruda del troncal
                    info1["path_idx"],
                    info1["seg_idx"],
                    dist_type,
                    branch_path_idx,  # 🆕 path_idx del tubo perpendicular
                )

                # Aplicar layer override si existe (misma lógica que en preview)
                # point_key y te_type ya están definidos arriba
                if hasattr(self, "layer_overrides") and self.layer_overrides:
                    te_key = ("te", te_type, point_key)

                    if te_key in self.layer_overrides:
                        override_layer = self.layer_overrides[te_key]
                        print(
                            f"[SO] *** APLICANDO LAYER OVERRIDE a Te {te_key}: → {override_layer}"
                        )
                        # Aplicar el layer override a todos los elementos de la Te
                        for elem in te_elems:
                            try:
                                com_prop = elem.GetCommonProperties()
                                if com_prop is None:
                                    com_prop = AllplanBaseElements.CommonProperties()
                                    com_prop.GetGlobalProperties()
                                old_layer = com_prop.Layer
                                com_prop.Layer = override_layer
                                elem.SetCommonProperties(com_prop)
                                print(
                                    f"[SO]   Te elemento: Layer {old_layer} → {override_layer}"
                                )
                            except Exception as ex:
                                print(
                                    f"[SO] Error aplicando layer override a elemento Te: {ex}"
                                )
                    else:
                        print(
                            f"[SO] DEBUG: No hay override para Te {te_key} (keys disponibles: {list(self.layer_overrides.keys())})"
                        )

                    # Aplicar atributos desde attribute_overrides si existe
                    if (
                        hasattr(self, "attribute_overrides")
                        and self.attribute_overrides
                    ):
                        if te_key in self.attribute_overrides:
                            attr_value = self.attribute_overrides[te_key]
                            print(
                                f"[SO] *** APLICANDO ATRIBUTOS a Te {te_key}: → '{attr_value}'"
                            )
                            custom_attrs = {"NomIS": attr_value}
                            # dist_type ya está calculado arriba (línea ~3900)
                            for elem in te_elems:
                                try:
                                    _set_attr_padre(elem, custom_attrs, doc, dist_type)
                                    attrs_applied = (
                                        "6_CC_IS y pmp_pare"
                                        if dist_type == "IS"
                                        else "pmp_pare"
                                    )
                                    print(
                                        f"[SO]   Te elemento ({dist_type}): Atributos {attrs_applied} = '{attr_value}'"
                                    )
                                except Exception as ex:
                                    print(
                                        f"[SO] Error aplicando atributos a elemento Te: {ex}"
                                    )

                # Almacenar distribución para cada elemento de la Te
                start_idx = len(elems)
                elems.extend(te_elems)
                for i, elem in enumerate(te_elems):
                    elem_distribution_map[start_idx + i] = dist_type
                used_te_vertices.add(key)

            # =======================================================
            # 2b) ELEMENTOS DEFINIDOS (T sortida, Colze base, Clau de Pas) desde marcadores
            # =======================================================
            _markers = getattr(self, "element_markers", []) or []
            if _markers:
                print(
                    f"[SO] Creando {len(_markers)} elemento(s) definido(s) desde marcadores (T/Colze/Clau)..."
                )
            for m in _markers:
                kind = m.get("kind", "free")
                pos = m.get("pos")
                element_type = (
                    str(m.get("element_type", "t_sortida") or "t_sortida")
                    .strip()
                    .lower()
                )
                if pos is None:
                    continue
                if not hasattr(pos, "X"):
                    continue
                p_mid = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)

                # Determinar path y puntos solo cuando sea necesario
                path_idx = m.get("path_idx", None)
                pts = (
                    self.saved_paths[path_idx]
                    if (path_idx is not None and 0 <= path_idx < len(self.saved_paths))
                    else (self.saved_paths[0] if self.saved_paths else None)
                )

                try:
                    # Elementos definidos Agua: crear 3D vía BaseDefinedElement.generate_final_3d
                    elem = _agua_defined_elements.get(element_type)
                    if elem is None:
                        continue
                    doc = self.coord_input.GetInputViewDocument()
                    if doc is None:
                        continue
                    try:
                        model_list = elem.generate_final_3d(self.build_ele, doc)
                    except Exception as ex_el:
                        print(f"[SO] Error en {element_type}: {ex_el}")
                        continue
                    if not model_list:
                        continue
                    mat = AllplanGeo.Matrix3D()
                    mat.SetTranslation(AllplanGeo.Vector3D(p_mid.X, p_mid.Y, p_mid.Z))
                    AllplanBaseElements.CreateElements(doc, mat, model_list, [], None)
                    print(
                        f"[SO] {elem.nombre} creado en marcador ({kind}) en ({p_mid.X:.1f}, {p_mid.Y:.1f}, {p_mid.Z:.1f})"
                    )

                except Exception as ex:
                    print(
                        f"[SO] Error creando elemento definido {element_type} en {kind}: {ex}"
                    )

            # =======================================================
            # 3) CREAR ELEMENTOS EN EL DOCUMENTO / PYTHONPARTGROUP
            # =======================================================
            if not elems:
                print("[SO] Aviso: no hay elementos para crear.")
                return

            # Leer flag de la paleta (checkbox tipo bool en el .pyp)
            crear_pythonpart = False
            try:
                crear_pythonpart = self.build_ele.CrearPythonPart.value
            except Exception as e:
                print(f"[SO] No se pudo leer CrearPythonPart, uso False. Detalle: {e}")
                crear_pythonpart = False

            if crear_pythonpart:
                print("[SO] ========== MODO PYTHONPARTGROUP ACTIVADO ==========")
                try:
                    # 1) Un PythonPart por cada elemento 3D
                    individual_pythonparts = (
                        create_individual_pythonparts_from_elements(
                            elems, self.build_ele
                        )
                    )

                    if not individual_pythonparts:
                        raise Exception(
                            "No se pudieron crear PythonParts individuales."
                        )

                    # 2) Copias pmp_pare ANTES de crear el PPG (para guardar UUIDs en la PPG)
                    copy_ok = True
                    try:
                        copy_ok = self._copy_elements_by_pmp_pare(elems)
                        if not copy_ok:
                            creation_cancelled = True
                            print(
                                "[PMP_PARE] Usuario canceló para asignar el atributo de padre. "
                                "No se crea el grupo. Complete los atributos y vuelva a finalizar."
                            )
                    except Exception as ex_copy:
                        print(
                            f"[PMP_PARE] Error copiando elementos por pmp_pare: {ex_copy}"
                        )

                    # 3) Parámetros globales y creación del PPG solo si el usuario no canceló
                    if copy_ok:
                        global_params = {
                            "TotalElements": len(elems),
                            "PolylineID": id(self.saved_paths),
                        }
                        copy_uuids_str = ";".join(self._get_pmp_pare_copy_uuids())
                        if copy_uuids_str:
                            global_params["PmpPareCopyUUIDs"] = copy_uuids_str

                        # Agregar estado serializado para poder restaurarlo al editar
                        state_json = self._serialize_state_to_json()
                        if state_json:
                            global_params["SavedState"] = state_json
                            print(
                                f"[SO] Estado guardado en PythonPartGroup ({len(state_json)} caracteres)"
                            )

                        installation_hash = create_element_hash(
                            "agua_is_polyline", **global_params
                        )
                        param_list = create_params_list_from_dict(global_params)
                        python_file_name = (
                            self.build_ele.pyp_file_name
                            if hasattr(self.build_ele, "pyp_file_name")
                            else ""
                        )

                        # Crear el grupo
                        pythonpart_group = PythonPartGroup(
                            "PP_IS_Polyline",
                            param_list,
                            installation_hash,
                            python_file_name,
                            individual_pythonparts,
                        )

                        model_elem_list = pythonpart_group.create()

                        if not hasattr(self, "coord_input") or self.coord_input is None:
                            print(
                                "[SO] Error: coord_input no disponible para crear elementos"
                            )
                            return False

                        doc = self.coord_input.GetInputViewDocument()

                        # ==========================================================
                        # NOTA: Los atributos ya fueron aplicados a los elementos
                        # antes de convertirlos en PythonParts (en _set_attr_padre).
                        # La función create_individual_pythonparts_from_elements
                        # extrae esos atributos y los pasa a cada PythonPart.
                        # ==========================================================

                        AllplanBaseElements.CreateElements(
                            doc, AllplanGeo.Matrix3D(), model_elem_list, [], None
                        )
                        print(
                            f"[SO] ✓ PythonPartGroup creado con {len(individual_pythonparts)} elementos."
                        )
                except Exception as e:
                    print(f"[SO] ✗ Error creando PythonPartGroup: {e}")
                    import traceback

                    traceback.print_exc()

                    # fallback: crear elementos individuales como siempre,
                    # manteniendo los atributos que ya se hayan aplicado por elemento.
                    if hasattr(self, "coord_input") and self.coord_input is not None:
                        doc = self.coord_input.GetInputViewDocument()
                        AllplanBaseElements.CreateElements(
                            doc, AllplanGeo.Matrix3D(), elems, [], None
                        )
                        print(
                            f"[SO] Fallback: creados {len(elems)} elementos individuales."
                        )
            else:
                # Modo tradicional: elementos sueltos.
                # Los atributos 6_CC_IS / pmp_pare ya se han aplicado por elemento
                # antes de este punto (usando attribute_overrides y _set_attr_padre),
                # igual que en el modo PythonPartGroup.
                if not hasattr(self, "coord_input") or self.coord_input is None:
                    print("[SO] Error: coord_input no disponible para crear elementos")
                    return False
                doc = self.coord_input.GetInputViewDocument()

                uuids_before = self._get_all_element_uuids_in_doc(doc)
                AllplanBaseElements.CreateElements(
                    doc, AllplanGeo.Matrix3D(), elems, [], None
                )
                print(
                    f"[SO] Creados {len(elems)} elementos "
                    "(tubos + codos + manguitos + Tes) en el documento"
                )
                uuids_after = self._get_all_element_uuids_in_doc(doc)
                new_uuids = uuids_after - uuids_before

                # Copiar sólidos pmp_pare en modo tradicional (en PPG ya se hizo antes de crear el grupo)
                try:
                    if not self._copy_elements_by_pmp_pare(elems):
                        creation_cancelled = True
                        deleted = self._delete_elements_by_uuids(doc, new_uuids)
                        print(
                            f"[PMP_PARE] Usuario canceló para asignar el atributo de padre. "
                            f"Se eliminaron {deleted} elementos del documento. Asigne el atributo y vuelva a finalizar."
                        )
                        # No return: seguir hasta el final para no limpiar datos
                except Exception as ex_copy:
                    print(
                        f"[PMP_PARE] Error copiando elementos por pmp_pare: {ex_copy}"
                    )

            # Limpiar memoria SOLO si la creación se completó exitosamente
            # Si se canceló (creation_cancelled = True), mantener los datos para edición
            if not creation_cancelled:
                self.saved_paths.clear()
                self.saved_segments.clear()
                self.element_markers.clear()
                print("[SO] Datos limpiados después de creación exitosa")
                return True
            else:
                print("[SO] Creación cancelada: datos mantenidos para edición")
                return False

        except Exception as ex:
            print(f"[SO] Error en _finalize_and_create_now: {ex}")
            # Si hubo un error, solo limpiar si no se canceló intencionalmente
            if not creation_cancelled:
                try:
                    self.saved_paths.clear()
                    self.saved_segments.clear()
                except Exception:
                    pass
            return False

    def _on_anadir_punto_libre(self, intr) -> bool:
        """Activa modo 'siguiente clic = añadir punto libre' (evento 1017, módulo ElementosDefinidos)."""
        return ed_on_anadir_punto_libre(self, intr, "AGUA")

    def _on_finalizar_puntos_libres(self, intr) -> bool:
        """Crea los elementos 3D desde puntos libres y vacía la lista (evento 1018, módulo ElementosDefinidos)."""
        return ed_on_finalizar_puntos_libres(
            self, intr, self._create_elements_from_free_placed_points
        )

    def on_control_event(self, event_id: int):
        """1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=eliminar nodo; 1017=añadir punto libre; 1018=finalizar puntos libres"""
        print(f"[SO] *** EVENTO RECIBIDO: {event_id} ***")

        if self.script_object_interactor is None:
            print(f"[SO] Creando interactor...")
            try:
                self.start_input()
            except Exception as ex:
                print(f"[SO] Error creando interactor: {ex}")
                return False

        intr = self.script_object_interactor

        # Antes de 1015/1016/1017: guardar estado para que, si Allplan recrea el script object, se restaure la polilínea / puntos libres.
        if event_id in (1015, 1016, 1017, 1018):
            try:
                if intr:
                    intr.save_current_polyline()
                self.element_markers = (
                    getattr(intr, "element_markers", self.element_markers) or []
                )
                self._save_state_to_build_ele()
                # Caché de sesión: cuando Allplan cree una nueva instancia del script, __init__ restaurará desde aquí
                state_json = self._serialize_state_to_json()
                if state_json:
                    _polyline_state_cache[id(self.build_ele)] = state_json
                    debug(
                        f"[SO] Estado guardado en caché de sesión para restauración tras evento {event_id}"
                    )
            except Exception as ex:
                print(f"[SO] Error guardando estado antes de evento {event_id}: {ex}")

        def _finalize_now():
            try:
                # Resetear marcador de resultado de creación antes de cada llamada
                try:
                    self._last_finalize_creation_done = None
                except Exception:
                    pass
                # Si estamos en modo captura de orientación, cancelar solo eso
                if intr.orientation_capture_mode:
                    print("[SO] Cancelando captura de orientación 3D (evento 1003)")
                    intr._cancel_orientation_capture()
                    return True  # No finalizar, solo cancelar orientación

                # ============================================================================
                # LÓGICA DE DOS PASOS: PREVIEW → EDICIÓN DE LAYERS → FINALIZAR
                # ============================================================================
                if not intr.preview_mode:
                    # PRIMER PASO: Generar elementos en modo edición de layers
                    print("[SO] ========== EDICIÓN DE LAYERS ACTIVADO ==========")

                    # IMPORTANTE: Guardar la polilínea activa antes de generar elementos
                    # Esto asegura que cualquier polilínea en edición se guarde primero
                    if intr:
                        intr.save_current_polyline()
                        print(
                            f"[SO] Polilínea guardada. Total de polilíneas guardadas: {len(self.saved_paths)}"
                        )

                    # Verificar que haya polilíneas guardadas
                    if not self.saved_paths:
                        print(
                            "[SO] ⚠ No hay polilíneas guardadas. Guarde al menos una polilínea antes de pasar a edición de layers."
                        )
                        PythonUtility.ShowMessageBox(
                            "No hay polilíneas guardadas.\n\nPor favor, guarde al menos una polilínea antes de pasar a edición de layers.",
                            PythonUtility.MB_OK,
                        )
                        return False

                    print("[SO] Generando elementos para edición de layers...")
                    intr.preview_mode = True
                    intr._generate_elements_for_preview()
                    # Cambiar texto del botón a "Finalizar y crear"
                    intr._update_finalize_button_text("Finalizar y crear")
                    print(
                        "[SO] Click en elementos para cambiar layer. Presione 'Finalizar y crear' para confirmar."
                    )
                    return True
                else:
                    # SEGUNDO PASO: Aplicar cambios y finalizar realmente
                    print("[SO] ========== FINALIZANDO Y CREANDO ELEMENTOS ==========")
                    print(
                        f"[SO] Aplicando {len(intr.layer_overrides)} cambios de layer..."
                    )
                    intr.preview_mode = False
                    intr.generated_elements.clear()
                    intr.selected_element_id = None

                    # Copiar layer_overrides, distribution_overrides y attribute_overrides del interactor al script_object
                    self.layer_overrides = intr.layer_overrides.copy()
                    if hasattr(intr, "distribution_overrides"):
                        self.distribution_overrides = intr.distribution_overrides.copy()
                    if hasattr(intr, "attribute_overrides"):
                        self.attribute_overrides = intr.attribute_overrides.copy()

                    # Crear elementos definitivos (los overrides se usan dentro de _finalize_and_create_now)
                    if intr:
                        intr.save_current_polyline()
                    # Asegurar que los marcadores de elementos definidos (T/Colze/Clau) estén en el script object
                    # (por si el script object fue recreado y tiene element_markers vacío)
                    if getattr(intr, "element_markers", None):
                        self.element_markers = list(intr.element_markers)
                    creation_done = self._finalize_and_create_now()

                    # Guardar el resultado de la creación para que pueda ser consultado (p. ej. por ESC)
                    try:
                        self._last_finalize_creation_done = bool(creation_done)
                    except Exception:
                        pass

                    if creation_done:
                        # Limpiar layer_overrides y attribute_overrides DESPUÉS de crear los elementos
                        intr.layer_overrides.clear()
                        if hasattr(intr, "attribute_overrides"):
                            intr.attribute_overrides.clear()
                        if hasattr(intr, "distribution_overrides"):
                            intr.distribution_overrides.clear()

                        # Cancelar el input y cerrar
                        for name in (
                            "CancelFunction",
                            "OnCancelFunction",
                            "CancelInput",
                            "Cancel",
                        ):
                            meth = getattr(self.coord_input, name, None)
                            if callable(meth):
                                try:
                                    meth()
                                    break
                                except Exception as ex:
                                    print(f"[SO] coord_input.{name}() ex: {ex}")
                    else:
                        # Usuario canceló (p. ej. pmp_pare): mantener datos y volver a modo edición de layers
                        intr.preview_mode = True
                        intr._generate_elements_for_preview()
                        intr._update_finalize_button_text("Finalizar y crear")
                        print(
                            "[SO] Siga editando atributos y pulse de nuevo 'Finalizar y crear' cuando termine."
                        )
                    return True
            except Exception as ex:
                print(f"[SO] Error en finalizar: {ex}")
                import traceback

                traceback.print_exc()
                return False

        handlers = {
            1001: lambda: (
                setattr(intr, "create_mode", not intr.create_mode),
                intr._update_create_mode_display(),
                intr._apply_create_mode_changes(),
                True,
            )[-1],
            1002: lambda: (
                intr.save_current_polyline(),
                print(f"[SO] Guardadas: {len(self.saved_paths)} polilíneas"),
                True,
            )[-1],
            1003: _finalize_now,
            1004: lambda: intr.delete_vertex_at_hover_or_fallback_to_segment(),
            1007: intr.apply_section_to_selected,
            1008: intr.show_sections_info,
            1009: intr.apply_layers_to_selected,
            1010: intr.apply_distribution_to_selected,
            1011: intr.apply_attributes_to_selected,
            1012: intr.start_orientation_capture,  # Definir orientación 3D
            # 1015 Seleccionar punto: activar captura de punto libre (element_point_capture_mode).
            # Si el elemento no permite intermedio (colze_base, taps), mostrar mensaje; si no, activar modo.
            1015: lambda: (
                (
                    bool(
                        PythonUtility.ShowMessageBox(
                            "Colze base y Taps solo pueden situarse en Inicio o Final de la polilínea, no en puntos intermedios.",
                            PythonUtility.MB_OK,
                        )
                    )
                    if intr._get_defined_element_settings()[0] in ("colze_base", "taps")
                    else bool(intr.start_element_point_capture())
                ),
            ),
            1016: lambda: intr._add_defined_element_marker(),  # Agregar elemento definido (T/Colze/Clau)
            1017: lambda: self._on_anadir_punto_libre(
                intr
            ),  # Modo puntos libres: siguiente clic añade punto libre
            1018: lambda: self._on_finalizar_puntos_libres(
                intr
            ),  # Modo puntos libres: crear 3D y vaciar lista
        }

        try:
            return bool(
                handlers.get(
                    event_id,
                    lambda: (
                        print(f"[SO] *** EVENTO NO RECONOCIDO: {event_id} ***"),
                        False,
                    )[-1],
                )()
            )
        except Exception as ex:
            print(f"[SO] *** ERROR PROCESANDO EVENTO {event_id}: {ex} ***")
            try:
                if self.script_object_interactor is not None:
                    self.script_object_interactor._cleanup_resources()
            except Exception as cleanup_ex:
                print(f"[SO] Error durante limpieza tras excepción: {cleanup_ex}")
            return False

    def on_cancel_function(self):
        """
        Maneja ESC a nivel de ScriptObject.

        Debe ejecutar en orden:
        1) Guardar la polilínea activa.
        2) Pasar (si hace falta) a modo edición de layers (preview).
        3) Finalizar y crear los elementos (misma lógica que botón 1003).
        """
        print("[SO] on_cancel_function: ESC recibido.")

        intr = getattr(self, "script_object_interactor", None)

        # Asegurar que existe interactor
        if intr is None:
            try:
                print(
                    "[SO] on_cancel_function: no hay interactor, llamando start_input()..."
                )
                self.start_input()
                intr = self.script_object_interactor
            except Exception as ex:
                print(f"[SO] on_cancel_function: error creando interactor: {ex}")
                return OnCancelFunctionResult.CANCEL_INPUT

        if intr is None:
            print("[SO] on_cancel_function: interactor sigue siendo None; cancelando.")
            return OnCancelFunctionResult.CANCEL_INPUT

        # 0) Caso especial: si estamos en captura de orientación, solo cancelar esa captura
        if getattr(intr, "orientation_capture_mode", False):
            print(
                "[SO] ESC: Cancelando captura de orientación 3D (desde ScriptObject)."
            )
            try:
                intr._cancel_orientation_capture()
            except Exception as ex:
                print(f"[SO] Error cancelando captura de orientación: {ex}")
            return OnCancelFunctionResult.CONTINUE_INPUT

        # 1) Guardar la polilínea activa
        try:
            print("[SO] ESC: guardando polilínea activa antes de finalizar.")
            intr.save_current_polyline()
            print(f"[SO] ESC: guardadas {len(self.saved_paths)} polilíneas.")
        except Exception as ex:
            print(f"[SO] ESC: error guardando polilínea activa: {ex}")

        # Si no hay polilíneas guardadas, no tiene sentido pasar a edición de layers ni crear.
        # Este caso puede darse, por ejemplo, si se pulsa el botón Cerrar de la paleta sin haber
        # dibujado ninguna polilínea. En lugar de mostrar un mensaje de error, simplemente
        # cancelamos la entrada sin crear elementos.
        if not self.saved_paths:
            print(
                "[SO] ESC/Cerrar: no hay polilíneas guardadas; se cancela sin crear elementos."
            )
            return OnCancelFunctionResult.CANCEL_INPUT

        was_preview = getattr(intr, "preview_mode", False)

        # 2) Pasar a modo edición de layers (si aún no estamos en preview)
        if not was_preview:
            print(
                "[SO] ESC: pasando a modo edición de layers (equivalente a primer clic en 1003)."
            )
            try:
                ok_preview = self.on_control_event(1003)
            except Exception as ex_evt:
                print(
                    f"[SO] ESC: error al entrar en modo edición de layers (1003): {ex_evt}"
                )
                return OnCancelFunctionResult.CANCEL_INPUT

            if not ok_preview:
                print(
                    "[SO] ESC: on_control_event(1003) devolvió False al entrar en preview; se mantiene la sesión."
                )
                return OnCancelFunctionResult.CONTINUE_INPUT

        # 3) Finalizar y crear (equivalente a segundo clic en 1003)
        print("[SO] ESC: finalizando y creando (segundo paso de 1003).")
        try:
            # Resetear flag de resultado antes de la llamada
            try:
                self._last_finalize_creation_done = None
            except Exception:
                pass

            ok_final = self.on_control_event(1003)
        except Exception as ex_evt:
            print(f"[SO] ESC: error al finalizar con on_control_event(1003): {ex_evt}")
            return OnCancelFunctionResult.CANCEL_INPUT

        if not ok_final:
            print(
                "[SO] ESC: on_control_event(1003) devolvió False al finalizar; se mantiene la sesión."
            )
            return OnCancelFunctionResult.CONTINUE_INPUT

        created = getattr(self, "_last_finalize_creation_done", None)

        if created:
            print("[SO] ESC: elementos creados correctamente; se cierra la sesión.")
            # Asegurarnos de que futuras llamadas no reutilicen este valor
            try:
                self._last_finalize_creation_done = None
            except Exception:
                pass
            return OnCancelFunctionResult.CREATE_ELEMENTS

        # Caso especial: la lógica interna (_finalize_and_create_now) ha cancelado la creación
        # (por ejemplo, porque el usuario ha pulsado "Cancelar" en el diálogo de pmp_pare).
        # En este caso, queremos mantener el modo de edición de layers activo y NO permitir
        # que start_next_input limpie el interactor ni los elementos de preview.
        print(
            "[SO] ESC: la creación fue cancelada dentro de la lógica de finalización; "
            "se mantiene la sesión y la edición de layers."
        )
        try:
            self._suppress_start_next_cleanup = True
        except Exception:
            pass
        return OnCancelFunctionResult.CONTINUE_INPUT


# ===== Interactor =====
class PolylineInteractor:
    def _clear_editing_state(self):
        """
        Centraliza la limpieza de todos los estados temporales de edición, selección, inserción, drag, hover, bifurcación, etc.
        Llamar siempre que se requiera un reset completo de la UI/estado de edición.
        """
        self.is_dragging = False
        self.drag_index = -1
        self.saved_dragging = None
        self.saved_dragging_original_point = None
        self.hover_index = -1
        self.hover_seg = None
        self.selected_seg = None
        self.insert_preview_p = None
        self.insert_target = None
        self.saved_hover_point = None
        self.hover_mid = None
        self.extend_target = None
        self.free_point_hover_index = -1
        self.free_point_selected_index = None
        self.last_free_point_selected_index = None
        # No limpia self.points ni self.current_point (eso depende del contexto)
        # Limpia selección por marcos
        self._clear_box_selection_state()

    # ---------- Borrar segmentos seleccionados por marco ----------
    def delete_selected_segments_by_box(self) -> bool:
        """
        Borra los segmentos seleccionados por marco. Si se seleccionan todos los segmentos de una polilínea,
        se borra toda la polilínea. Si se seleccionan solo algunos, se eliminan esos segmentos y se dividen
        las polilíneas en fragmentos válidos (≥2 puntos).
        """
        if not self.selected_segments:
            return False

        from collections import defaultdict

        to_delete = defaultdict(set)  # path_idx -> set(seg_idx)
        for kind, path_idx, seg_idx in self.selected_segments:
            if kind == "saved":
                to_delete[path_idx].add(seg_idx)

        changed = False
        new_saved_paths = []
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx not in to_delete:
                new_saved_paths.append(pts)
                continue
            seg_indices = to_delete[path_idx]
            if len(seg_indices) == len(pts) - 1:
                # Se seleccionaron todos los segmentos: borrar toda la polilínea
                changed = True
                continue
            # Si no, fragmentar en partes válidas (≥2 puntos)
            fragment = [pts[0]]
            for i in range(len(pts) - 1):
                if i in seg_indices:
                    if len(fragment) >= 2:
                        new_saved_paths.append(
                            [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment]
                        )
                        changed = True
                    fragment = [pts[i + 1]]
                else:
                    fragment.append(pts[i + 1])
            if len(fragment) >= 2:
                new_saved_paths.append(
                    [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment]
                )
                changed = True

        if changed:
            self.script_object.saved_paths = new_saved_paths
            self.selected_seg = None
            self.hover_seg = None
            self.insert_preview_p = None
            self.insert_target = None
            self.hover_mid = None
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )
        return changed

    def __init__(self, script_object: PolylineScriptObject):
        self.script_object = script_object

        # Modo creación (toggle con 1001) - OFF por defecto
        self.create_mode = False

        # Polilínea activa (en edición/creación)
        self.points = []
        self.current_point = AllplanGeo.Point3D()

        # Estado de edición (activa)
        self.hover_index = -1
        self.drag_index = -1
        self.is_dragging = False

        # Drag de vértices guardados (edición)
        self.saved_dragging = None  # (path_idx, pt_idx)
        self.saved_dragging_original_point = (
            None  # Coordenadas originales antes del drag
        )

        # : extensión de polilínea guardada ---
        # Si no es None, al guardar se fusiona la activa a esa polilínea (start/end)
        self.extend_target = None  # (path_idx, 'start'|'end')

        # Segmentos: hover + seleccionado persistente
        # Formato: ('active'|'saved', path_idx, seg_idx); active => path_idx = -1
        self.hover_seg = None
        self.selected_seg = None

        # Inserción (controlado por CheckBox en paleta)
        self.insert_mode = False
        self.insert_preview_p = None
        self.insert_target = None

        # Midpoint hover
        self.hover_mid = None

        # Selección por marco
        self.box_selecting = False
        self.box_start = None
        self.box_curr = None
        self.selected_segments = set()  # (kind, path_idx, seg_idx)

        # ============================================================================
        # MODO EDICIÓN DE LAYERS (PREVIEW MODE)
        # ============================================================================
        self.preview_mode = False  # True cuando está en modo edición de layers
        self.generated_elements = []  # Lista de elementos generados con fitting
        self.layer_overrides = (
            {}
        )  # {element_key: layer_id} - cambios de layer por elemento
        self.attribute_overrides = (
            {}
        )  # {element_key: attribute_value} - cambios de atributos por elemento
        self.distribution_overrides = (
            {}
        )  # {element_key: distribution_type} - cambios de distribución por elemento
        self.selected_element_id = None  # ID del elemento actualmente seleccionado
        self.highlight_geometry = None  # Geometría de highlight temporal

        # ============================================================================
        # ORIENTACIÓN 3D: Captura de línea de referencia en plano XY
        # ============================================================================
        self.orientation_capture_mode = (
            False  # True cuando estamos capturando línea de orientación
        )
        self.orientation_line_start = (
            None  # Primer punto de la línea de orientación (Point3D)
        )
        self.orientation_line_end = None  # Segundo punto de la línea de orientación (Point3D) - guardado al completar
        self.orientation_line_preview = (
            None  # Segundo punto temporal durante captura (Point3D)
        )

        # ============================================================================
        # ELEMENTOS DEFINIDOS: T sortida, Colze base, Clau de Pas (entrada de puntos)
        # ============================================================================
        self.element_point_capture_mode = False
        self.element_selected_point = (
            None  # Point3D cuando modo Intermedio (flujo antiguo)
        )
        self.element_markers = []  # Se sincroniza con script_object.element_markers
        # Intermedio simplificado: al pulsar "Agregar elemento" el siguiente clic en el dibujo añade el elemento (sin diálogos)
        self.next_click_adds_intermediate_element = False
        # Modo puntos libres (pestaña "Modo puntos libres", evento 1017): siguiente clic añade punto libre
        self.next_click_adds_free_point = False
        # Selección de punto libre: índice bajo el cursor (hover) e índice seleccionado (clic)
        self.free_point_hover_index = -1
        self.free_point_selected_index = None
        self.last_free_point_selected_index = None
        # Arrastre de punto libre: el punto sigue al cursor hasta soltar
        self.free_point_dragging = False
        self.free_point_drag_index = None
        # Índice pendiente de posible arrastre (click sobre punto sin empezar aún a moverlo)
        self.pending_free_point_drag_index = None
        # Posición del clic para umbral de arrastre (solo arrastrar si el cursor se mueve > este umbral)
        self.free_point_drag_start_position = None
        # Doble clic en punto libre: (timestamp del último clic, índice del punto)
        self._last_free_point_click_time = None
        self._last_free_point_click_index = None

        # Propiedades
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()

    def __del__(self):
        """Destructor to ensure cleanup when object is garbage collected"""
        try:
            self._cleanup_resources()
        except Exception:
            # Ignore errors during destruction to prevent issues with garbage collection
            pass

    def _cleanup_resources(self):
        """Comprehensive cleanup of all resources to prevent memory leaks"""
        try:
            print("[INT] Starting resource cleanup...")

            # Clear all preview elements
            self._clear_preview()

            # Clear all temporary data structures
            self.points.clear()
            self.selected_segments.clear()

            # Reset all indices and flags
            self.hover_index = -1
            self.drag_index = -1
            self.is_dragging = False
            self.saved_dragging = None
            self.saved_dragging_original_point = None
            self.extend_target = None
            self.hover_seg = None
            self.selected_seg = None
            self.insert_mode = False
            self.insert_preview_p = None
            self.insert_target = None
            self.hover_mid = None
            self.saved_hover_point = None
            self.saved_dragging_original_point = None
            self.box_selecting = False
            self.box_start = None
            self.box_curr = None
            self.next_click_adds_intermediate_element = False
            self.next_click_adds_free_point = False
            self.free_point_hover_index = -1
            self.free_point_selected_index = None
            self.last_free_point_selected_index = None
            self.free_point_dragging = False
            self.free_point_drag_index = None
            self.pending_free_point_drag_index = None
            self.free_point_drag_start_position = None
            self._last_free_point_click_time = None
            self._last_free_point_click_index = None
            self.element_point_capture_mode = False
            self.element_selected_point = None

            # Clean up orphaned segments (segments that reference non-existent paths)
            self._cleanup_orphaned_segments()

            # Force garbage collection hint
            self.current_point = AllplanGeo.Point3D()

            print("[INT] Resource cleanup completed successfully")

        except Exception as ex:
            print(f"[INT] Error during resource cleanup: {ex}")
            # Continue cleanup even if some parts fail
            try:
                self.points.clear()
                self.selected_segments.clear()
            except:
                pass

    def _cleanup_orphaned_segments(self):
        """Remove segments that reference non-existent polyline paths to prevent accumulation"""
        try:
            if (
                not hasattr(self.script_object, "saved_segments")
                or not self.script_object.saved_segments
            ):
                return

            valid_segments = []
            total_segments = len(self.script_object.saved_segments)

            for segment_info in self.script_object.saved_segments:
                try:
                    points = segment_info.get("points", [])
                    if len(points) >= 2:
                        # Check if this segment still corresponds to an existing path
                        segment_still_valid = False
                        for pts in self.script_object.saved_paths:
                            if len(pts) >= 2:
                                for i in range(len(pts) - 1):
                                    if self._points_equal(
                                        pts[i], points[0]
                                    ) and self._points_equal(pts[i + 1], points[1]):
                                        segment_still_valid = True
                                        break
                            if segment_still_valid:
                                break

                        if segment_still_valid:
                            valid_segments.append(segment_info)

                except Exception:
                    # Skip malformed segments
                    continue

            # Update saved_segments with only valid ones
            removed_count = total_segments - len(valid_segments)
            if removed_count > 0:
                self.script_object.saved_segments = valid_segments
                print(
                    f"[INT] Removed {removed_count} orphaned segments from saved_segments"
                )

        except Exception as ex:
            print(f"[INT] Error cleaning orphaned segments: {ex}")

    def _update_segments_after_vertex_drag(
        self, path_idx: int, vertex_idx: int, original_point: AllplanGeo.Point3D
    ):
        """
        Actualiza las coordenadas de los segmentos afectados después de mover un vértice.
        Se llama cuando se termina el drag de un vértice guardado para sincronizar saved_segments.
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= vertex_idx < len(pts)):
                return

            # Actualizar segmentos afectados por el vértice movido
            segments_updated = 0

            for segment_info in self.script_object.saved_segments:
                if not isinstance(segment_info, dict):
                    continue

                seg_path = segment_info.get("path_idx", -1)
                seg_idx = segment_info.get("seg_idx", -1)

                if seg_path == path_idx and seg_idx >= 0:
                    points = segment_info.get("points", [])
                    if len(points) >= 2:
                        # Actualizar puntos del segmento
                        if seg_idx == vertex_idx:
                            # El vértice movido es el inicio del segmento
                            segment_info["points"][0] = AllplanGeo.Point3D(
                                pts[vertex_idx].X, pts[vertex_idx].Y, pts[vertex_idx].Z
                            )
                            segments_updated += 1
                        elif seg_idx + 1 == vertex_idx:
                            # El vértice movido es el final del segmento
                            segment_info["points"][1] = AllplanGeo.Point3D(
                                pts[vertex_idx].X, pts[vertex_idx].Y, pts[vertex_idx].Z
                            )
                            segments_updated += 1

            if segments_updated > 0:
                print(
                    f"[INT] Actualizados {segments_updated} segmentos después de mover vértice {vertex_idx} en polilínea {path_idx}"
                )
            else:
                print(
                    f"[INT] No se encontraron segmentos para actualizar después de mover vértice {vertex_idx} en polilínea {path_idx}"
                )

        except Exception as ex:
            print(f"[INT] Error actualizando segmentos después de drag: {ex}")

    def _propagate_section_info_after_split(
        self,
        path_idx: int,
        original_seg_idx: int,
        original_section_info: dict,
        original_end_point: AllplanGeo.Point3D,
    ):
        """
        Propaga la información de sección del segmento original a los dos nuevos segmentos
        después de insertar un punto intermedio.
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            pts = self.script_object.saved_paths[path_idx]

            # Después de la inserción, tenemos:
            # - Segmento 1: pts[original_seg_idx] -> pts[original_seg_idx + 1] (hasta punto insertado)
            # - Segmento 2: pts[original_seg_idx + 1] -> pts[original_seg_idx + 2] (desde punto insertado hasta final)

            if original_seg_idx + 2 >= len(pts):
                print(f"[INT] Error: índices fuera de rango después de inserción")
                return

            # Remover el segmento original de saved_segments usando el punto final original guardado
            original_segments = []
            filtered_segments = []

            for seg in self.script_object.saved_segments:
                if self._is_original_segment(
                    seg, pts[original_seg_idx], original_end_point
                ):
                    original_segments.append(seg)
                else:
                    filtered_segments.append(seg)

            self.script_object.saved_segments = filtered_segments

            if original_segments:
                print(
                    f"[INT] Removido {len(original_segments)} segmento(s) original(es)"
                )

            # Crear dos nuevos segmentos con la misma información de sección
            dist_type = original_section_info.get("distribution_type")
            if dist_type not in ["TD", "IS"]:
                dist_type = self._get_distribution_type_to_apply() or "IS"
            # Primer segmento: del punto original al punto insertado
            first_segment_info = {
                "points": [
                    AllplanGeo.Point3D(
                        pts[original_seg_idx].X,
                        pts[original_seg_idx].Y,
                        pts[original_seg_idx].Z,
                    ),
                    AllplanGeo.Point3D(
                        pts[original_seg_idx + 1].X,
                        pts[original_seg_idx + 1].Y,
                        pts[original_seg_idx + 1].Z,
                    ),
                ],
                "diameter": original_section_info.get("diameter", 110.0),
                "section_type": original_section_info.get("section_type", "110mm"),
                "system": original_section_info.get("system", "Pluvial"),
                "label": original_section_info.get("label", "D110 P"),
                "path_idx": path_idx,
                "seg_idx": original_seg_idx,
                "distribution_type": dist_type,
            }

            # Segundo segmento: del punto insertado al punto final original (ahora en posición +2)
            second_segment_info = {
                "points": [
                    AllplanGeo.Point3D(
                        pts[original_seg_idx + 1].X,
                        pts[original_seg_idx + 1].Y,
                        pts[original_seg_idx + 1].Z,
                    ),
                    AllplanGeo.Point3D(
                        pts[original_seg_idx + 2].X,
                        pts[original_seg_idx + 2].Y,
                        pts[original_seg_idx + 2].Z,
                    ),
                ],
                "diameter": original_section_info.get("diameter", 110.0),
                "section_type": original_section_info.get("section_type", "110mm"),
                "system": original_section_info.get("system", "Pluvial"),
                "label": original_section_info.get("label", "D110 P"),
                "path_idx": path_idx,
                "seg_idx": original_seg_idx + 1,
                "distribution_type": dist_type,
            }

            # Añadir ambos segmentos a saved_segments
            self.script_object.saved_segments.append(first_segment_info)
            self.script_object.saved_segments.append(second_segment_info)

            print(
                f"[INT] Propagada información de sección a 2 nuevos segmentos: {original_section_info.get('label', 'Sin etiqueta')}"
            )

        except Exception as ex:
            print(
                f"[INT] Error propagando información de sección después de split: {ex}"
            )

    def _is_original_segment(
        self,
        segment_info: dict,
        original_start: AllplanGeo.Point3D,
        original_end: AllplanGeo.Point3D,
    ) -> bool:
        """
        Verifica si un segmento es el segmento original que se va a dividir.
        """
        try:
            if not isinstance(segment_info, dict) or "points" not in segment_info:
                return False

            points = segment_info["points"]
            if len(points) < 2:
                return False

            # Verificar si los puntos coinciden con el segmento original
            start_match = self._points_equal(points[0], original_start)
            end_match = self._points_equal(points[1], original_end)

            if start_match and end_match:
                print(
                    f"[INT] Encontrado segmento original para remover: {segment_info.get('label', 'Sin etiqueta')}"
                )
                return True

            return False

        except Exception as ex:
            print(f"[INT] Error verificando segmento original: {ex}")
            return False

    def _propagate_section_info_after_vertex_removal(
        self, path_idx: int, vertex_idx: int, section_info: dict
    ):
        """
        Actualiza saved_segments después de eliminar un vértice: fusiona los dos
        segmentos adyacentes en un único segmento (dos puntos). No se insertan
        puntos intermedios aquí: si la longitud supera MAX_SEGMENT_LENGTH, el
        código de creación (_finalize_and_create_now) ya divide el tramo igual
        que un segmento largo dibujado de una vez (5000 + manguito + 5000 +
        manguito + resto), con los mismos recortes y manguitos.
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return
            pts = self.script_object.saved_paths[path_idx]
            if vertex_idx <= 0 or vertex_idx >= len(pts):
                return
            # Punto fusionado: pts[vertex_idx-1] -> pts[vertex_idx] (el antiguo vertex_idx+1)
            p_start = pts[vertex_idx - 1]
            p_end = pts[vertex_idx]

            merged_segment = {
                "points": [
                    AllplanGeo.Point3D(p_start.X, p_start.Y, p_start.Z),
                    AllplanGeo.Point3D(p_end.X, p_end.Y, p_end.Z),
                ],
                "diameter": section_info.get("diameter", 110.0),
                "section_type": section_info.get("section_type", "110mm"),
                "system": section_info.get("system", "Pluvial"),
                "label": section_info.get("label", "D110 P"),
                "path_idx": path_idx,
                "seg_idx": vertex_idx - 1,
            }
            if "distribution_type" in section_info:
                merged_segment["distribution_type"] = section_info["distribution_type"]
            new_segments = []
            for seg in self.script_object.saved_segments:
                if seg.get("path_idx") != path_idx:
                    new_segments.append(seg)
                    continue
                s_idx = seg.get("seg_idx", -1)
                if s_idx == vertex_idx - 1 or s_idx == vertex_idx:
                    continue
                if s_idx > vertex_idx:
                    seg = dict(seg)
                    seg["seg_idx"] = s_idx - 1
                new_segments.append(seg)
            new_segments.append(merged_segment)
            self.script_object.saved_segments = sorted(
                new_segments,
                key=lambda s: (s.get("path_idx", 0), s.get("seg_idx", 0)),
            )
            print(
                f"[INT] Segmentos fusionados tras eliminar vértice {vertex_idx} en polilínea {path_idx} "
                "(la creación aplicará longitud máx. y recortes como en un segmento largo)"
            )
        except Exception as ex:
            print(f"[INT] Error propagando sección tras eliminar vértice: {ex}")

    def _remove_vertex_saved(self, path_idx: int, vertex_idx: int) -> bool:
        """
        Elimina un vértice intermedio de una polilínea guardada, fusionando los dos
        segmentos adyacentes. Permite deshacer bifurcaciones o corregir nodos añadidos.
        Solo permite eliminar vértices intermedios (no extremos).
        """
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return False
        pts = self.script_object.saved_paths[path_idx]
        if len(pts) <= 2:
            return False
        if vertex_idx <= 0 or vertex_idx >= len(pts) - 1:
            return False
        section_info = self._get_segment_section_info("saved", path_idx, vertex_idx - 1)
        if not section_info:
            section_info = {
                "diameter": 110.0,
                "section_type": "110mm",
                "system": "Pluvial",
                "label": "D110 P",
            }
        pts.pop(vertex_idx)
        self._propagate_section_info_after_vertex_removal(
            path_idx, vertex_idx, section_info
        )
        return True

    def _remove_vertex_active(self, vertex_idx: int) -> bool:
        """
        Elimina un vértice intermedio de la polilínea activa (en creación).
        Solo permite vértices intermedios (no extremos).
        """
        if len(self.points) <= 2:
            return False
        if vertex_idx <= 0 or vertex_idx >= len(self.points) - 1:
            return False
        self.points.pop(vertex_idx)
        return True

    def delete_vertex_at_hover_or_fallback_to_segment(self) -> bool:
        """
        Elimina un nodo (vértice intermedio) si el hover/contexto está sobre uno;
        en caso contrario borra segmento (comportamiento anterior).
        Permite deshacer bifurcaciones y corregir la topología de la red.
        """
        # 1) Prioridad: selección por marco
        if self.selected_segments:
            return self.delete_selected_segments_by_box()

        # 2) Vértice guardado bajo cursor (modo edición): eliminar nodo
        if self.saved_hover_point is not None and not self.create_mode:
            pidx, vidx, _ = self.saved_hover_point
            pts = self.script_object.saved_paths[pidx]
            if len(pts) > 2 and 0 < vidx < len(pts) - 1:
                if self._remove_vertex_saved(pidx, vidx):
                    self.saved_hover_point = None
                    self._clear_editing_state()
                    self._draw_preview(
                        self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    )
                    print(f"[INT] Nodo eliminado en polilínea {pidx}, vértice {vidx}")
                    return True

        # 3) Vértice activo bajo cursor (modo creación): eliminar nodo
        if self.create_mode and self.hover_index >= 0 and len(self.points) > 2:
            if 0 < self.hover_index < len(self.points) - 1:
                vidx_removed = self.hover_index
                if self._remove_vertex_active(vidx_removed):
                    self.hover_index = -1
                    self._draw_preview(
                        self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    )
                    print(
                        f"[INT] Nodo eliminado en polilínea activa, vértice {vidx_removed}"
                    )
                    return True

        # 4) Fallback: borrar segmento (comportamiento original)
        return self.delete_selected_or_hovered_segment()

    # ---------- Inicio ----------
    def start_input(self, coord_input):
        self.coord_input = coord_input
        self._sync_insert_mode_from_palette()

        # Sincronización inicial: leer el estado del checkbox y aplicarlo
        try:
            checkbox_value = self._safe_get_palette_property("CrearPolylinea")
            if hasattr(checkbox_value, "value"):
                self.create_mode = bool(checkbox_value.value)
                print(
                    f"[INT] Estado inicial del checkbox: {checkbox_value.value} -> create_mode = {self.create_mode}"
                )
            else:
                # Valor por defecto
                self.create_mode = False
                print(
                    f"[INT] Checkbox no encontrado, usando valor por defecto: create_mode = {self.create_mode}"
                )
        except Exception as ex:
            self.create_mode = False
            print(f"[INT] Error leyendo estado inicial: {ex}")

        # Sincronizar element_markers con el script object (misma lista)
        self.element_markers = (
            getattr(self.script_object, "element_markers", None) or []
        )
        if not isinstance(self.script_object.element_markers, list):
            self.script_object.element_markers = []
        self.element_markers = self.script_object.element_markers
        # Puntos libres (modo puntos libres): asegurar que exista la lista en script_object
        if not hasattr(self.script_object, "free_placed_points") or not isinstance(
            getattr(self.script_object, "free_placed_points", None), list
        ):
            self.script_object.free_placed_points = []

        # Actualizar display inicial
        self._update_create_mode_display()
        self._print_prompt()

    def _print_prompt(self):
        if getattr(self, "next_click_adds_free_point", False):
            msg = "Modo puntos libres: haga clic en el plano para añadir un punto."
        elif getattr(self, "next_click_adds_intermediate_element", False):
            msg = "Haga clic en la polilínea donde desea colocar el elemento (posición intermedia)."
        else:
            msg = (
                "Edición: drag vértices guardados; selección por marco (clic vacío→mover→clic); "
                "midpoints clicables; clic en segmento para seleccionar; "
                "1004=eliminar nodo (con cursor sobre vértice) o borrar segmento; 1002=guardar; ESC/1003=finalizar"
            )
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))

    def toggle_create_mode(self):
        self.create_mode = not self.create_mode
        self._update_create_mode_display()
        self._apply_create_mode_changes()

    def sync_create_mode_from_checkbox(self):
        """Sincroniza el modo de creación con el valor del checkbox en la paleta"""
        try:
            # Leer el valor actual del checkbox de manera segura
            checkbox_value = self._safe_get_palette_property("CrearPolylinea", None)

            if checkbox_value is None:
                # No hacemos nada si no podemos leer el valor
                return

            # Convertir a booleano de manera segura
            try:
                if isinstance(checkbox_value, bool):
                    new_mode = checkbox_value
                elif hasattr(checkbox_value, "__bool__"):
                    new_mode = bool(checkbox_value)
                else:
                    new_mode = bool(checkbox_value)
            except Exception as conv_ex:
                print(f"[INT] Error convirtiendo valor del checkbox: {conv_ex}")
                return

            # Comparar con el estado actual - solo cambiar si realmente es diferente
            if new_mode != self.create_mode:
                self.create_mode = new_mode
                self._update_create_mode_display()
                self._apply_create_mode_changes()

        except Exception as ex:
            print(f"[INT] Error sincronizando checkbox: {ex}")
            traceback.print_exc()

    def _update_create_mode_display(self):
        """Actualiza el texto de feedback en la paleta y el estado visual del botón"""
        print(f"[INT] Crear polilínea: OFF")
        try:
            # Actualizar texto de feedback de manera segura
            self._safe_set_palette_property("FirstText", "")

            # Intentar actualizar la paleta si es posible
            try:
                if (
                    hasattr(self.script_object, "palette_service")
                    and self.script_object.palette_service
                ):
                    self.script_object.palette_service.update_palette(
                        self.script_object.build_ele, show_palette=True
                    )
            except Exception as palette_ex:
                print(f"[INT] No se pudo actualizar paleta: {palette_ex}")

        except Exception as ex:
            print(f"[INT] Error actualizando displays: {ex}")
            traceback.print_exc()

    def _apply_create_mode_changes(self):
        """Aplica los cambios correspondientes al cambiar de modo"""
        if not self.create_mode:
            self.save_current_polyline()  # guarda lo que estuvieras creando/extendiéndo
        self._clear_editing_state()
        # Si activamos crear, desactivar modo insertar para evitar confusiones
        if self.create_mode and self.insert_mode:
            self.insert_mode = False

    # ============================================================================
    # ORIENTACIÓN 3D: Métodos de captura y gestión
    # ============================================================================

    def start_orientation_capture(self):
        """
        Toggle del modo de captura de línea de orientación en el plano XY.
        - Si el modo está activo y ya hay línea definida: guarda y desactiva
        - Si el modo está activo pero no hay línea: cancela
        - Si el modo no está activo: activa el modo
        """
        if self.orientation_capture_mode:
            # Modo ya está activo
            if (
                self.orientation_line_start is not None
                and self.orientation_line_end is not None
            ):
                # Ya hay línea definida: guardar y desactivar
                print("[INT] Guardando orientación 3D y desactivando modo...")
                self._save_orientation_from_line()
                self._cancel_orientation_capture()
                return True
            else:
                # No hay línea completa: cancelar modo
                print("[INT] Cancelando captura de orientación 3D")
                self._cancel_orientation_capture()
                return True
        else:
            # Modo no está activo: activar modo
            self.orientation_capture_mode = True
            self.orientation_line_start = None
            self.orientation_line_end = None
            self.orientation_line_preview = None
            print("[INT] Modo captura de orientación 3D activado")
            print(
                "[INT] Click en el plano XY para definir el primer punto de la línea de orientación"
            )
            # Actualizar el prompt
            msg = "Orientación 3D: Click para definir primer punto de la línea de orientación (plano XY)"
            self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
            return True

    def _handle_orientation_capture(self, mouse_msg, raw_pnt):
        """Maneja la captura de la línea de orientación"""
        # Si ya tenemos ambos puntos, solo mostrar preview
        if (
            self.orientation_line_start is not None
            and self.orientation_line_end is not None
        ):
            # Durante el movimiento, actualizar el preview con la línea ya definida
            if self.coord_input.IsMouseMove(mouse_msg):
                self._draw_preview(raw_pnt)
            return True

        # Detectar movimiento del mouse
        if self.coord_input.IsMouseMove(mouse_msg):
            # Durante el movimiento, actualizar el preview
            if self.orientation_line_start is not None:
                self.orientation_line_preview = raw_pnt
                self._draw_preview(raw_pnt)
            return True

        # Click izquierdo: capturar punto
        is_left = getattr(mouse_msg, "Button", 1) == 1
        if not is_left:
            return True
        if self.orientation_line_start is None:
            # Primer punto: forzar Z=0 para estar en el plano XY
            self.orientation_line_start = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
            self.orientation_line_end = None  # Asegurar que está limpio
            print(
                f"[INT] Primer punto de orientación capturado: ({self.orientation_line_start.X:.2f}, {self.orientation_line_start.Y:.2f}, 0.0)"
            )
            msg = "Orientación 3D: Click para definir segundo punto de la línea de orientación"
            self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
            self.orientation_line_preview = None
            return True
        else:
            # Segundo punto: forzar Z=0 para estar en el plano XY
            p2 = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)

            # Calcular el ángulo de la línea respecto al eje X
            dx = p2.X - self.orientation_line_start.X
            dy = p2.Y - self.orientation_line_start.Y
            dist_xy = (dx * dx + dy * dy) ** 0.5

            if dist_xy < 1e-6:
                print(
                    "[INT] Error: La línea de orientación es demasiado corta. Intente con otro punto."
                )
                # No cancelar, solo mostrar error y esperar otro clic
                return True

            # Guardar el segundo punto (pero NO guardar la orientación aún)
            self.orientation_line_end = p2
            self.orientation_line_preview = (
                None  # Limpiar preview ya que tenemos el punto final
            )

            # Calcular ángulo para mostrar feedback
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            print(
                f"[INT] Segundo punto de orientación capturado: ({p2.X:.2f}, {p2.Y:.2f}, 0.0)"
            )
            print(f"[INT] Ángulo calculado: {angle_deg:.2f}° (desde eje X)")
            print(
                f"[INT] ✓ Línea de orientación definida. Presione el botón 'Definir orientación' para guardar."
            )

            # Actualizar el prompt para indicar que debe presionar el botón
            msg = "Orientación 3D: ✓ Línea definida. Presione 'Definir orientación' para guardar."
            self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))

            return True

    def _save_orientation_from_line(self):
        """Guarda la orientación desde la línea definida (orientation_line_start y orientation_line_end)"""
        if self.orientation_line_start is None or self.orientation_line_end is None:
            print("[INT] Error: No hay línea de orientación completa para guardar")
            return False

        # Calcular el ángulo de la línea respecto al eje X
        dx = self.orientation_line_end.X - self.orientation_line_start.X
        dy = self.orientation_line_end.Y - self.orientation_line_start.Y
        dist_xy = (dx * dx + dy * dy) ** 0.5

        if dist_xy < 1e-6:
            print(
                "[INT] Error: La línea de orientación es demasiado corta. No se guarda."
            )
            return False

        # Calcular ángulo en radianes (atan2 devuelve ángulo desde +X hacia +Y)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Guardar en el script object
        self.script_object.reference_orientation_angle = angle_rad

        print(f"[INT] ✓ Orientación 3D guardada: {angle_deg:.2f}° (desde eje X)")
        print(
            f"[INT]   Todos los tubos y codos se rotarán para seguir esta orientación"
        )

        # Actualizar información en la paleta
        self._update_orientation_info()

        return True

    def _cancel_orientation_capture(self):
        """Cancela el modo de captura de orientación y restaura el estado normal"""
        if self.orientation_capture_mode:
            print("[INT] Cancelando captura de orientación 3D")
            self.orientation_capture_mode = False
            self.orientation_line_start = None
            self.orientation_line_end = None
            self.orientation_line_preview = None
            self._print_prompt()
            return True
        return False

    def _update_orientation_info(self):
        """Actualiza la información de orientación 3D en la paleta"""
        try:
            ref_angle = getattr(self.script_object, "reference_orientation_angle", None)

            if ref_angle is None:
                info_text = "No definida"
            else:
                angle_deg = math.degrees(ref_angle)
                # Normalizar ángulo a [0, 360)
                angle_deg = angle_deg % 360.0
                if angle_deg < 0:
                    angle_deg += 360.0

                # Determinar dirección cardinal/principal
                direction = self._get_direction_from_angle(angle_deg)

                # Determinar eje/cota principal
                axis_info = self._get_axis_info_from_angle(angle_deg)

                # Formatear texto
                info_text = f"{angle_deg:.1f}° - {direction} ({axis_info})"

            # Actualizar en la paleta
            self._safe_set_palette_property("Orientacion3DInfo", info_text)

            # Forzar actualización de la paleta
            try:
                if (
                    hasattr(self.script_object, "palette_service")
                    and self.script_object.palette_service
                ):
                    self.script_object.palette_service.update_palette(
                        self.script_object.build_ele, show_palette=True
                    )
            except Exception as palette_ex:
                print(f"[INT] No se pudo actualizar paleta: {palette_ex}")

        except Exception as ex:
            print(f"[INT] Error actualizando información de orientación: {ex}")

    def _get_direction_from_angle(self, angle_deg: float) -> str:
        """Determina la dirección cardinal/principal desde el ángulo"""
        # Normalizar a [0, 360)
        angle_deg = angle_deg % 360.0

        # Direcciones principales con tolerancia de ±22.5°
        if 337.5 <= angle_deg or angle_deg < 22.5:
            return "Este (E)"
        elif 22.5 <= angle_deg < 67.5:
            return "Noreste (NE)"
        elif 67.5 <= angle_deg < 112.5:
            return "Norte (N)"
        elif 112.5 <= angle_deg < 157.5:
            return "Noroeste (NO)"
        elif 157.5 <= angle_deg < 202.5:
            return "Oeste (O)"
        elif 202.5 <= angle_deg < 247.5:
            return "Suroeste (SO)"
        elif 247.5 <= angle_deg < 292.5:
            return "Sur (S)"
        else:  # 292.5 <= angle_deg < 337.5
            return "Sureste (SE)"

    def _get_axis_info_from_angle(self, angle_deg: float) -> str:
        """Determina el eje/cota principal desde el ángulo"""
        # Normalizar a [0, 360)
        angle_deg = angle_deg % 360.0

        # Calcular componentes X e Y normalizadas
        angle_rad = math.radians(angle_deg)
        comp_x = math.cos(angle_rad)
        comp_y = math.sin(angle_rad)

        # Determinar componente dominante
        abs_x = abs(comp_x)
        abs_y = abs(comp_y)

        if abs_x > abs_y * 1.5:  # Dominante en X
            if comp_x > 0:
                return "Eje X+"
            else:
                return "Eje X-"
        elif abs_y > abs_x * 1.5:  # Dominante en Y
            if comp_y > 0:
                return "Eje Y+"
            else:
                return "Eje Y-"
        else:  # Diagonal (ambos componentes similares)
            if comp_x > 0 and comp_y > 0:
                return "Diagonal X+/Y+"
            elif comp_x < 0 and comp_y > 0:
                return "Diagonal X-/Y+"
            elif comp_x < 0 and comp_y < 0:
                return "Diagonal X-/Y-"
            else:  # comp_x > 0 and comp_y < 0
                return "Diagonal X+/Y-"
            print("[INT] Insert mode: OFF (por activar Crear)")
        self._print_prompt()
        self._draw_preview(
            self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        )

    # ---------- Paleta -> modo insertar ----------
    def _get_palette_insert_mode(self) -> Optional[bool]:
        """Obtiene el modo de inserción desde la paleta de manera segura"""
        # Renombrado en paleta: antes "CheckBoxValue" (duplicado). Ahora único: "CheckBoxInsertarPunto"
        return self._safe_get_palette_property("CheckBoxInsertarPunto", None)

    def _get_palette_limit_angles(self) -> Optional[bool]:
        """Lee el checkbox 'Limitar ángulos' de la paleta.
        Nota: actualmente no se utiliza en la lógica; se deja listo para futuras mejoras.
        """
        return self._safe_get_palette_property("CheckBoxLimitarAngulos", None)

    def _sync_insert_mode_from_palette(self):
        new_mode = self._get_palette_insert_mode()
        if new_mode is None:
            return
        if new_mode != self.insert_mode:
            self.insert_mode = new_mode
            print(
                f"[INT] Insert mode (checkbox): {'ON' if self.insert_mode else 'OFF'}"
            )
            self.insert_preview_p = None
            self.insert_target = None

    # ---------- Utilidades ----------
    def _dist_sq(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx, dy, dz = a.X - b.X, a.Y - b.Y, a.Z - b.Z
        return dx * dx + dy * dy + dz * dz

    def _segment_len(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        return (self._dist_sq(a, b)) ** 0.5

    def _segment_project_point(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, p: AllplanGeo.Point3D
    ) -> Tuple[float, AllplanGeo.Point3D]:
        vx, vy, vz = b.X - a.X, b.Y - a.Y, b.Z - a.Z
        wx, wy, wz = p.X - a.X, p.Y - a.Y, p.Z - a.Z
        vv = vx * vx + vy * vy + vz * vz
        if vv <= 1e-12:
            return 0.0, AllplanGeo.Point3D(a.X, a.Y, a.Z)
        t = (vx * wx + vy * wy + vz * wz) / vv
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        q = AllplanGeo.Point3D(a.X + t * vx, a.Y + t * vy, a.Z + t * vz)
        return t, q

    def _midpoint(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D
    ) -> AllplanGeo.Point3D:
        return AllplanGeo.Point3D(
            (a.X + b.X) * 0.5, (a.Y + b.Y) * 0.5, (a.Z + b.Z) * 0.5
        )

    def _is_valid_angle(self, new_point: AllplanGeo.Point3D) -> bool:
        """
        Valida el nuevo segmento según el modo "Limitar ángulos".
        Copiado de Saneamiento, adaptado para fontaneria: solo [0, 90, 180, 270], tolerancia 0.
        """
        if len(self.points) < 1:
            return True

        limit_angles = self._get_palette_limit_angles()
        if not limit_angles:
            return True

        last_point = self.points[-1]
        dx = new_point.X - last_point.X
        dy = new_point.Y - last_point.Y
        dz = new_point.Z - last_point.Z

        dist_3d = (dx * dx + dy * dy + dz * dz) ** 0.5
        if dist_3d < 1e-6:
            return True

        dist_xy = (dx * dx + dy * dy) ** 0.5
        dist_z = abs(dz)

        is_horizontal = dist_xy > dist_z
        is_vertical = dist_z > dist_xy

        valid_angles = [0.0, 90.0, 180.0, 270.0]
        tolerance = 0.0

        def normalize_angle(angle_deg):
            angle_deg = angle_deg % 360.0
            if angle_deg < 0:
                angle_deg += 360.0
            return angle_deg

        def is_angle_valid(angle_deg):
            norm_angle = normalize_angle(angle_deg)
            return any(
                abs(norm_angle - va) <= tolerance
                or abs(norm_angle - (va + 360.0)) <= tolerance
                for va in valid_angles
            )

        if is_horizontal:
            angle_deg = math.degrees(math.atan2(dy, dx))
            curr_ang = normalize_angle(angle_deg)

            if len(self.points) >= 2:
                prev_point = self.points[-2]
                pvx = last_point.X - prev_point.X
                pvy = last_point.Y - prev_point.Y
                prev_dist_xy = (pvx * pvx + pvy * pvy) ** 0.5
                prev_dist_z = abs(last_point.Z - prev_point.Z)
                if prev_dist_xy > prev_dist_z and prev_dist_xy > 1e-6:
                    # Excepción: segmento previo en ángulo distinto a [0,90,180,270].
                    # Tomar el ángulo del segmento anterior como referencia 0°.
                    # El siguiente segmento puede ser [0, 90, 180, 270] relativo al anterior.
                    prev_ang = normalize_angle(math.degrees(math.atan2(pvy, pvx)))
                    delta = normalize_angle(curr_ang - prev_ang)
                    valid_relative = [0.0, 90.0, 180.0, 270.0]
                    if not any(abs(delta - vr) <= tolerance for vr in valid_relative):
                        return False
                else:
                    if not is_angle_valid(angle_deg):
                        return False
            else:
                if not is_angle_valid(angle_deg):
                    return False

        elif is_vertical:
            if dist_xy > 1e-3:
                elevation_deg = math.degrees(math.atan2(dist_z, dist_xy))
                valid_elevations = [0.0, 90.0]
                if not any(
                    abs(elevation_deg - ve) <= tolerance for ve in valid_elevations
                ):
                    return False
                angle_xy_deg = math.degrees(math.atan2(dy, dx))
                if not is_angle_valid(angle_xy_deg):
                    return False

        return True

    def _find_hover_index(self, p: AllplanGeo.Point3D) -> int:
        if not self.points:
            return -1
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = -1
        best_d2 = max_d2 + 1.0
        for i, pt in enumerate(self.points):
            d2 = self._dist_sq(p, pt)
            if d2 <= max_d2 and d2 < best_d2:
                best_d2 = d2
                best = i
        return best

    def _find_hover_saved_point(
        self, p: AllplanGeo.Point3D, only_extremes: bool = False
    ) -> Optional[Tuple[int, int, AllplanGeo.Point3D]]:
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None
        best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            indices = range(len(pts))
            for i in indices:
                q = pts[i]
                d2 = self._dist_sq(p, q)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = (path_idx, i, q)
        return best

    def _find_junction_vertex_in_other_path(
        self,
        exclude_path_idx: int,
        point: AllplanGeo.Point3D,
        tolerance_mm: float = 2.0,
    ) -> Optional[Tuple[int, int]]:
        """
        Busca un vértice intermedio (no extremo) en otra polilínea que coincida con
        el punto (p. ej. el extremo de una rama). Así detectamos el nodo de una Te
        para colapsarlo al borrar la rama.
        Devuelve (path_idx, vertex_idx) o None. tolerance_mm en mm.
        """
        max_d2 = tolerance_mm * tolerance_mm
        for pidx, pts in enumerate(self.script_object.saved_paths):
            if pidx == exclude_path_idx or len(pts) < 3:
                continue
            for j in range(1, len(pts) - 1):
                if self._dist_sq(point, pts[j]) <= max_d2:
                    return (pidx, j)
        return None

    @staticmethod
    def _angle_deg_at_junction(
        p_before: AllplanGeo.Point3D,
        p_junction: AllplanGeo.Point3D,
        p_after: AllplanGeo.Point3D,
    ) -> float:
        """
        Ángulo en grados en el vértice p_junction entre el segmento (p_before -> p_junction)
        y el segmento (p_junction -> p_after). 0° = colineal, 90° = giro recto (codo).
        """
        v1x = p_junction.X - p_before.X
        v1y = p_junction.Y - p_before.Y
        v1z = p_junction.Z - p_before.Z
        v2x = p_after.X - p_junction.X
        v2y = p_after.Y - p_junction.Y
        v2z = p_after.Z - p_junction.Z
        len1 = (v1x * v1x + v1y * v1y + v1z * v1z) ** 0.5
        len2 = (v2x * v2x + v2y * v2y + v2z * v2z) ** 0.5
        if len1 < 1e-6 or len2 < 1e-6:
            return 0.0
        v1x, v1y, v1z = v1x / len1, v1y / len1, v1z / len1
        v2x, v2y, v2z = v2x / len2, v2y / len2, v2z / len2
        dot = max(-1.0, min(1.0, v1x * v2x + v1y * v2y + v1z * v2z))
        return math.degrees(math.acos(dot))

    def _merge_paths_at_90_degree_junctions(self, tolerance_deg: float = 10.0) -> bool:
        """
        Si dos polilíneas guardadas comparten exactamente un extremo y el ángulo en ese
        punto es ~90°, las fusiona en una sola polilínea para que en creación se dibuje
        un codo en ese vértice (y no quede como dos paths separados sin codo).
        Devuelve True si se hizo al menos una fusión.
        """
        paths = self.script_object.saved_paths
        if len(paths) < 2:
            return False
        tol_sq = (2.0) ** 2  # 2 mm para considerar mismo punto
        merged_any = False
        while True:
            # Mapa: clave (x,y,z) redondeada -> [(path_idx, "start"|"end"), ...]
            endpoint_map = {}
            for pidx, pts in enumerate(paths):
                if len(pts) < 2:
                    continue
                for key, which in [
                    (
                        (round(pts[0].X, 0), round(pts[0].Y, 0), round(pts[0].Z, 0)),
                        "start",
                    ),
                    (
                        (round(pts[-1].X, 0), round(pts[-1].Y, 0), round(pts[-1].Z, 0)),
                        "end",
                    ),
                ]:
                    endpoint_map.setdefault(key, []).append((pidx, which))
            # Buscar puntos donde exactamente 2 paths comparten extremo (uno start, otro end)
            merge_done = False
            for point_key, endpoints in endpoint_map.items():
                if len(endpoints) != 2:
                    continue
                (i, wi), (j, wj) = endpoints
                if i == j:
                    continue
                # Que uno sea start y otro end (confluencia)
                if not (
                    (wi == "start" and wj == "end") or (wi == "end" and wj == "start")
                ):
                    continue
                if wi == "end" and wj == "start":
                    path_a, path_b = paths[i], paths[j]
                else:
                    path_a, path_b = paths[j], paths[i]
                end_a, start_b = path_a[-1], path_b[0]
                if self._dist_sq(end_a, start_b) > tol_sq:
                    continue
                # Obtener puntos antes y después del vértice de unión
                p_junction = path_a[-1]
                if len(path_a) < 2 or len(path_b) < 2:
                    continue
                p_before = path_a[-2]
                p_after = path_b[1]
                angle_deg = self._angle_deg_at_junction(p_before, p_junction, p_after)
                if abs(angle_deg - 90.0) > tolerance_deg:
                    continue
                # Fusionar: path_a + path_b[1:]
                merged = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in path_a] + [
                    AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in path_b[1:]
                ]
                lo, hi = min(i, j), max(i, j)
                num_seg_a = len(path_a) - 1  # segmentos del path que queda como inicio

                # Mantener coherencia con saved_segments: reasignar (hi, seg) -> (lo, seg + num_seg_a)
                # y actualizar path_idx de los demás paths tras eliminar dos
                if (
                    hasattr(self.script_object, "saved_segments")
                    and self.script_object.saved_segments
                ):
                    for seg in self.script_object.saved_segments:
                        pid = seg.get("path_idx")
                        sid = seg.get("seg_idx", 0)
                        if pid == hi:
                            seg["path_idx"] = lo
                            seg["seg_idx"] = sid + num_seg_a
                        elif pid > hi:
                            seg["path_idx"] = pid - 2
                        elif pid > lo:
                            seg["path_idx"] = pid - 1

                paths.pop(hi)
                paths.pop(lo)
                paths.insert(lo, merged)
                merge_done = True
                merged_any = True
                print(
                    f"[INT] Giro 90° en unión: polilíneas fusionadas para dibujar codo."
                )
                break
            if not merge_done:
                break
        return merged_any

    def _find_nearby_extreme(
        self, p: AllplanGeo.Point3D, exclude_path: int = -1
    ) -> Optional[Tuple[int, str]]:
        """Busca extremos de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path"""
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx == exclude_path:
                continue
            if len(pts) >= 2:
                # Check start
                if self._dist_sq(p, pts[0]) <= max_d2:
                    return (path_idx, "start")
                # Check end
                if self._dist_sq(p, pts[-1]) <= max_d2:
                    return (path_idx, "end")
        return None

    def _find_nearby_vertex(
        self, p: AllplanGeo.Point3D, exclude_path: int = -1
    ) -> Optional[Tuple[int, int]]:
        """Busca cualquier vértice de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path"""
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None
        best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx == exclude_path:
                continue
            for i, q in enumerate(pts):
                d2 = self._dist_sq(p, q)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = (path_idx, i)
        return best

    def _segment_hit_distance_sq(
        self,
        a: AllplanGeo.Point3D,
        b: AllplanGeo.Point3D,
        p: AllplanGeo.Point3D,
    ) -> float:
        """
        Distancia al cuadrado desde p al segmento (a,b) para hit-test en 3D.
        """
        _, q = self._segment_project_point(a, b, p)
        dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
        return dx * dx + dy * dy + dz * dz

    @staticmethod
    def _distance_point_to_segment_2d_sq(
        px: float, py: float, ax: float, ay: float, bx: float, by: float
    ) -> float:
        """Distancia al cuadrado del punto (px,py) al segmento (ax,ay)-(bx,by) en 2D."""
        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay
        vv = vx * vx + vy * vy
        if vv <= 1e-12:
            return wx * wx + wy * wy
        t = (vx * wx + vy * wy) / vv
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        qx = ax + t * vx
        qy = ay + t * vy
        return (px - qx) * (px - qx) + (py - qy) * (py - qy)

    # preferred_kind: 'active', 'saved' o None (ambos)
    # pnt_2d: Point2D (cursor en vista); si se pasa con view_proj se usa hit-test 2D (permite seleccionar verticales en cualquier vista)
    def _find_hover_segment(
        self,
        p: AllplanGeo.Point3D,
        preferred_kind: Optional[str] = None,
        pnt_2d=None,
        view_proj=None,
    ) -> Optional[Tuple[str, int, int]]:
        use_2d = (
            pnt_2d is not None
            and view_proj is not None
            and hasattr(pnt_2d, "X")
            and hasattr(pnt_2d, "Y")
        )
        if use_2d:
            try:
                max_d2_view = HIT_TOL_VIEW * HIT_TOL_VIEW
                best = None
                best_d2 = max_d2_view + 1.0
                cx, cy = float(pnt_2d.X), float(pnt_2d.Y)

                if preferred_kind in (None, "active") and len(self.points) >= 2:
                    for i in range(len(self.points) - 1):
                        a, b = self.points[i], self.points[i + 1]
                        a_v = view_proj.WorldToView(a)
                        b_v = view_proj.WorldToView(b)
                        d2 = self._distance_point_to_segment_2d_sq(
                            cx, cy, a_v.X, a_v.Y, b_v.X, b_v.Y
                        )
                        if d2 <= max_d2_view and d2 < best_d2:
                            best_d2 = d2
                            best = ("active", -1, i)

                if preferred_kind in (None, "saved"):
                    for path_idx, pts in enumerate(self.script_object.saved_paths):
                        if len(pts) < 2:
                            continue
                        for i in range(len(pts) - 1):
                            a, b = pts[i], pts[i + 1]
                            a_v = view_proj.WorldToView(a)
                            b_v = view_proj.WorldToView(b)
                            d2 = self._distance_point_to_segment_2d_sq(
                                cx, cy, a_v.X, a_v.Y, b_v.X, b_v.Y
                            )
                            if d2 <= max_d2_view and d2 < best_d2:
                                best_d2 = d2
                                best = ("saved", path_idx, i)

                return best
            except Exception:
                use_2d = False

        if not use_2d:
            max_d2 = HIT_TOL_SEGMENT * HIT_TOL_SEGMENT
            best = None
            best_d2 = max_d2 + 1.0
            if preferred_kind in (None, "active") and len(self.points) >= 2:
                for i in range(len(self.points) - 1):
                    a, b = self.points[i], self.points[i + 1]
                    d2 = self._segment_hit_distance_sq(a, b, p)
                    if d2 <= max_d2 and d2 < best_d2:
                        best_d2 = d2
                        best = ("active", -1, i)
            if preferred_kind in (None, "saved"):
                for path_idx, pts in enumerate(self.script_object.saved_paths):
                    if len(pts) < 2:
                        continue
                    for i in range(len(pts) - 1):
                        a, b = pts[i], pts[i + 1]
                        d2 = self._segment_hit_distance_sq(a, b, p)
                        if d2 <= max_d2 and d2 < best_d2:
                            best_d2 = d2
                            best = ("saved", path_idx, i)
            return best
        return None

    def _find_hover_midpoint(
        self, p: AllplanGeo.Point3D
    ) -> Optional[Tuple[str, int, int, AllplanGeo.Point3D]]:
        max_d2 = MIDPOINT_HIT_TOL * MIDPOINT_HIT_TOL
        best = None
        best_d2 = max_d2 + 1.0

        # Activa
        if len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                a, b = self.points[i], self.points[i + 1]
                mp = self._midpoint(a, b)
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = ("active", -1, i, mp)

        # Guardadas
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) < 2:
                continue
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                mp = self._midpoint(a, b)
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = ("saved", path_idx, i, mp)

        return best

    def _seg_equal(
        self, a: Optional[Tuple[str, int, int]], b: Optional[Tuple[str, int, int]]
    ) -> bool:
        if a is None or b is None:
            return False
        return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

    def _clear_selection_if_invalid(self):
        sel = self.selected_seg
        if sel is None:
            return
        kind, path_idx, seg_idx = sel
        if kind == "active":
            if seg_idx < 0 or seg_idx >= max(0, len(self.points) - 1):
                self.selected_seg = None
        elif kind == "saved":
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                self.selected_seg = None
            else:
                pts = self.script_object.saved_paths[path_idx]
                if seg_idx < 0 or seg_idx >= max(0, len(pts) - 1):
                    self.selected_seg = None

    def _can_start_box_selection(self) -> bool:
        """
        Verifica si se puede iniciar la selección por marcos según el estado actual.
        Evita conflictos con otros modos activos.
        """
        # No permitir selección por marcos si estamos en modo creación
        if self.create_mode:
            return False

        # No permitir si estamos arrastrando elementos
        if self.is_dragging or self.saved_dragging is not None:
            return False

        # No permitir si estamos extendiendo una polilínea
        if self.extend_target is not None:
            return False

        # No permitir si hay una polilínea activa en creación
        if self.points:
            return False

        # Solo permitir en modo edición (create_mode=False) y sin estados activos
        return True

    def _clear_box_selection_state(self):
        """
        Limpia completamente el estado de selección por marcos.
        Útil para evitar estados inconsistentes al cambiar de modo.
        """
        if self.box_selecting:
            print(
                "[INT] Cancelando selección por marcos en curso debido a cambio de modo"
            )

        self.box_selecting = False
        self.box_start = None
        self.box_curr = None
        self.selected_segments.clear()

    # ---------- Elementos definidos (T sortida, Colze base, Clau de Pas) — delegado a ElementosDefinidos ----------
    def _get_defined_element_settings(self) -> Tuple[str, float]:
        """Obtiene tipo de elemento y radio desde la paleta (módulo ElementosDefinidos)."""
        return ed_get_defined_element_settings(
            getattr(self.script_object, "build_ele", None), "AGUA"
        )

    def _get_tipo_punto_libre_flag(self) -> str:
        """Obtiene la función (inicio/final/intermedio_*) desde TipoPuntoLibre (módulo ElementosDefinidos)."""
        return ed_get_tipo_punto_libre_flag(
            getattr(self.script_object, "build_ele", None), "AGUA"
        )

    def _get_free_point_selection_tolerance(self) -> float:
        """Tolerancia en mm para seleccionar un punto libre (módulo ElementosDefinidos)."""
        return ed_get_free_point_selection_tolerance(
            getattr(self.script_object, "build_ele", None), 40.0
        )

    def start_element_point_capture(self) -> bool:
        """Activa/desactiva modo selección de punto para elemento intermedio (evento 1015, módulo ElementosDefinidos)."""
        return ed_start_element_point_capture(self, "AGUA")

    def _handle_element_point_capture(
        self, mouse_msg: int, raw_pnt: AllplanGeo.Point3D
    ) -> bool:
        """Maneja el clic en modo captura de punto intermedio (módulo ElementosDefinidos)."""
        return ed_handle_element_point_capture_click(self, mouse_msg, raw_pnt)

    def _add_intermediate_element_at_point(self, raw_pnt: AllplanGeo.Point3D) -> None:
        """Añade elemento definido en posición intermedio en el punto indicado (módulo ElementosDefinidos)."""
        ed_add_intermediate_element_at_point(self, raw_pnt, "AGUA")

    def _add_defined_element_marker(self) -> bool:
        """Añade marcador de elemento definido según posición en paleta (evento 1016, módulo ElementosDefinidos)."""
        return ed_add_defined_element_marker(self, "AGUA")

    def _get_active_path_points(self) -> List[AllplanGeo.Point3D]:
        """Devuelve los puntos de la polilínea activa (en creación) o del primer path guardado."""
        if self.points and len(self.points) >= 2:
            return self.points
        if (
            getattr(self.script_object, "saved_paths", None)
            and self.script_object.saved_paths
        ):
            return self.script_object.saved_paths[0]
        return []

    def _point_in_rect_xy(
        self, p: AllplanGeo.Point3D, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D
    ) -> bool:
        xmin, xmax = (a.X, b.X) if a.X <= b.X else (b.X, a.X)
        ymin, ymax = (a.Y, b.Y) if a.Y <= b.Y else (b.Y, a.Y)
        return (xmin <= p.X <= xmax) and (ymin <= p.Y <= ymax)

    # ---------- Entrada de mouse ----------
    def _is_left_click(self, mouse_msg) -> bool:
        """Detecta clic izquierdo (Allplan puede enviar mouse_msg como entero 1 o como objeto con .Button)."""
        if self.coord_input.IsMouseMove(mouse_msg):
            return False
        if mouse_msg == 1:
            return True
        return getattr(mouse_msg, "Button", 1) == 1

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        # Si estamos en modo captura de orientación, manejar eso primero
        if self.orientation_capture_mode:
            raw_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
            ).GetPoint()
            return self._handle_orientation_capture(mouse_msg, raw_pnt)

        # Modo puntos libres: al mover el ratón, previsualizar el elemento en el cursor
        if getattr(
            self, "next_click_adds_free_point", False
        ) and self.coord_input.IsMouseMove(mouse_msg):
            try:
                # Usar GetInputPoint con el mensaje de ratón para obtener la posición actual del cursor
                raw_pnt = self.coord_input.GetInputPoint(
                    mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
                ).GetPoint()
                self._draw_preview(raw_pnt)
            except Exception:
                pass
            return True

        # Arrastre de punto libre: solo se mueve el punto si el usuario arrastra (mueve > umbral desde el clic).
        # Umbral alto para que un simple clic (o pequeño temblor) no mueva el elemento.
        DRAG_THRESHOLD_MM = 50.0
        if self.coord_input.IsMouseMove(mouse_msg):
            pending_idx = getattr(self, "pending_free_point_drag_index", None)
            start_pos = getattr(self, "free_point_drag_start_position", None)

            # Iniciar arrastre solo si hay punto pendiente y el cursor se movió más del umbral desde el clic
            if (
                not getattr(self, "free_point_dragging", False)
                and pending_idx is not None
                and start_pos is not None
            ):
                try:
                    raw_pnt = self.coord_input.GetInputPoint(
                        mouse_msg,
                        pnt,
                        msg_info,
                        self.current_point,
                        bool(self.points),
                    ).GetPoint()
                    dx = raw_pnt.X - getattr(start_pos, "X", 0.0)
                    dy = raw_pnt.Y - getattr(start_pos, "Y", 0.0)
                    dz = raw_pnt.Z - getattr(start_pos, "Z", 0.0)
                    dist_mm = math.sqrt(dx * dx + dy * dy + dz * dz)
                    if dist_mm > DRAG_THRESHOLD_MM:
                        self.free_point_dragging = True
                        self.free_point_drag_index = pending_idx
                except Exception:
                    pass

            if getattr(self, "free_point_dragging", False):
                try:
                    free_list = (
                        getattr(self.script_object, "free_placed_points", None) or []
                    )
                    idx = getattr(self, "free_point_drag_index", None)
                    if idx is not None and 0 <= idx < len(free_list):
                        raw_pnt = self.coord_input.GetInputPoint(
                            mouse_msg,
                            pnt,
                            msg_info,
                            self.current_point,
                            bool(self.points),
                        ).GetPoint()
                        fp = free_list[idx]
                        old_pos = fp.get("pos")
                        z_abs = float(getattr(old_pos, "Z", raw_pnt.Z) or raw_pnt.Z)
                        fp["pos"] = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, z_abs)
                        free_list[idx] = fp
                        self._draw_preview(raw_pnt)
                except Exception:
                    pass
                return True

        # Puntos libres: en cada movimiento actualizar hover con la posición del cursor y redibujar
        # para que el punto cambie de color (rojo) cuando el cursor está dentro de la tolerancia
        if (
            self.coord_input.IsMouseMove(mouse_msg)
            and not getattr(self, "next_click_adds_free_point", False)
            and not getattr(self, "free_point_dragging", False)
        ):
            free_list = getattr(self.script_object, "free_placed_points", None) or []
            if free_list:
                try:
                    cursor_pnt = self.coord_input.GetInputPoint(
                        mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
                    ).GetPoint()
                    self._draw_preview(cursor_pnt)
                except Exception:
                    pass
                return True

        is_click = self._is_left_click(mouse_msg)

        # Arrastre de punto libre: soltar el botón termina el arrastre
        if is_click and getattr(self, "free_point_dragging", False):
            try:
                self.free_point_dragging = False
                self.free_point_drag_index = None
                self.pending_free_point_drag_index = None
                self.free_point_drag_start_position = None
                try:
                    self.script_object._save_state_to_build_ele()
                except Exception:
                    pass
                try:
                    raw_pnt = self.coord_input.GetInputPoint(
                        mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
                    ).GetPoint()
                    self._draw_preview(raw_pnt)
                except Exception:
                    pass
                return True
            except Exception:
                pass

        # Selección / arrastre de puntos libres (ElementosDefinidos): prioridad sobre el resto
        if is_click and not getattr(self, "next_click_adds_free_point", False):
            try:
                free_list = (
                    getattr(self.script_object, "free_placed_points", None) or []
                )
                tol = self._get_free_point_selection_tolerance()
                print(
                    f"[ELEMENTO] Tolerancia selección punto libre (clic): {tol:.1f} mm"
                )
                if free_list:
                    raw_pnt = self.coord_input.GetInputPoint(
                        mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
                    ).GetPoint()
                    idx_hit = find_hover_free_point(raw_pnt, free_list, tol)
                    # Clic fuera de cualquier punto: deseleccionar (quitar resaltado y label)
                    if idx_hit == -1:
                        self.free_point_selected_index = None
                        self.pending_free_point_drag_index = None
                        self.free_point_drag_start_position = None
                        self._last_free_point_click_time = None
                        self._last_free_point_click_index = None
                        try:
                            self._draw_preview(raw_pnt)
                        except Exception:
                            pass
                        return True
                    # Clic sobre punto libre
                    if idx_hit != -1:
                        now = time.time()
                        last_time = getattr(self, "_last_free_point_click_time", None)
                        last_idx = getattr(self, "_last_free_point_click_index", None)
                        # Doble clic: mismo punto y segundo clic dentro de ~400 ms → actualizar posición al cursor
                        if (
                            last_time is not None
                            and last_idx == idx_hit
                            and (now - last_time) < 0.4
                        ):
                            self._last_free_point_click_time = None
                            self._last_free_point_click_index = None
                            fp = free_list[idx_hit]
                            old_pos = fp.get("pos")
                            z_abs = float(getattr(old_pos, "Z", raw_pnt.Z) or raw_pnt.Z)
                            fp["pos"] = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, z_abs)
                            free_list[idx_hit] = fp
                            self.free_point_selected_index = idx_hit
                            self.pending_free_point_drag_index = None
                            self.free_point_drag_start_position = None
                            try:
                                self.script_object._save_state_to_build_ele()
                            except Exception:
                                pass
                            try:
                                self._draw_preview(raw_pnt)
                            except Exception:
                                pass
                            return True

                        # Clic sobre el punto que ya está seleccionado → deseleccionar (quitar resaltado y label)
                        if getattr(self, "free_point_selected_index", None) == idx_hit:
                            self.free_point_selected_index = None
                            self.pending_free_point_drag_index = None
                            self.free_point_drag_start_position = None
                            self._last_free_point_click_time = None
                            self._last_free_point_click_index = None
                            try:
                                self._draw_preview(raw_pnt)
                            except Exception:
                                pass
                            return True

                        # Simple clic en otro punto: seleccionar (resaltar + label). Arrastre solo si se mueve > umbral.
                        self._last_free_point_click_time = now
                        self._last_free_point_click_index = idx_hit
                        self.free_point_selected_index = idx_hit
                        try:
                            ed_apply_free_point_rotation_to_palette(
                                self.script_object, idx_hit
                            )
                        except Exception:
                            pass

                        self.free_point_dragging = False
                        self.free_point_drag_index = None
                        self.pending_free_point_drag_index = idx_hit
                        self.free_point_drag_start_position = AllplanGeo.Point3D(
                            raw_pnt.X, raw_pnt.Y, raw_pnt.Z
                        )
                        try:
                            self._draw_preview(raw_pnt)
                        except Exception:
                            pass
                        return True
            except Exception:
                pass

        # Intermedio sin botón: con "Posición = Intermedio", un clic sobre un segmento guardado añade el elemento ahí
        if is_click:
            build_ele = getattr(self.script_object, "build_ele", None)
            try:
                mode = int(
                    getattr(getattr(build_ele, "ElementPointMode", None), "value", 0)
                    or 0
                )
            except Exception:
                mode = 0
            saved = getattr(self.script_object, "saved_paths", None)
            if (
                mode == 2
                and saved
                and len(saved) > 0
                and getattr(self.script_object, "element_markers", None) is not None
            ):
                raw_pnt = self.coord_input.GetInputPoint(
                    mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
                ).GetPoint()
                seg = self._find_hover_segment(raw_pnt, preferred_kind="saved")
                if seg is not None:
                    a, b = self._get_segment_endpoints(seg)
                    if a and b:
                        _t, q = self._segment_project_point(a, b, raw_pnt)
                        self._add_intermediate_element_at_point(q)
                        try:
                            self._draw_preview(
                                self.coord_input.GetCurrentPoint(
                                    self.current_point
                                ).GetPoint()
                            )
                        except Exception:
                            pass
                        return True

        # Modo puntos libres (1017): siguiente clic añade punto libre (módulo ElementosDefinidos)
        if getattr(self, "next_click_adds_free_point", False) and is_click:
            raw_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
            ).GetPoint()
            self.next_click_adds_free_point = False
            try:
                ed_handle_click_add_free_point(
                    self, self.script_object, raw_pnt, "AGUA"
                )
            except Exception as ex:
                print(f"[ELEMENTO] Error añadiendo punto libre: {ex}")
            self._print_prompt()
            try:
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
            except Exception:
                pass
            return True

        # Intermedio con botón "Seleccionar punto" (1015): el siguiente clic añade el elemento (sobre segmento si aplica)
        if self.next_click_adds_intermediate_element and is_click:
            raw_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
            ).GetPoint()
            self.next_click_adds_intermediate_element = False
            # Si el clic cae sobre un segmento guardado, proyectar el punto para que el elemento quede sobre la polilínea
            seg = self._find_hover_segment(raw_pnt, preferred_kind="saved")
            if seg is not None:
                a, b = self._get_segment_endpoints(seg)
                if a and b:
                    _t, q = self._segment_project_point(a, b, raw_pnt)
                    self._add_intermediate_element_at_point(q)
                else:
                    self._add_intermediate_element_at_point(raw_pnt)
            else:
                self._add_intermediate_element_at_point(raw_pnt)
            self._print_prompt()  # Restaurar prompt de edición
            try:
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
            except Exception:
                pass
            return True

        # Si estamos en modo captura de punto para elemento definido (Intermedio, flujo antiguo)
        if self.element_point_capture_mode:
            raw_pnt = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
            ).GetPoint()
            return self._handle_element_point_capture(mouse_msg, raw_pnt)

        # Sincronizar siempre el modo crear desde la paleta (checkbox)
        self.sync_create_mode_from_checkbox()
        # Sincronizar modo insertar desde la paleta
        self._sync_insert_mode_from_palette()

        # --- SNAP A ÁNGULOS VÁLIDOS ---
        raw_pnt = self.coord_input.GetInputPoint(
            mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
        ).GetPoint()

        # Determinar si "Limitar ángulos" está activo
        limit_angles_active = self._get_palette_limit_angles()

        # Snap copiado de Saneamiento, adaptado para fontaneria: solo [0, 90, 180, 270], tolerancia 0
        if self.create_mode and limit_angles_active:
            if len(self.points) >= 1:
                last_point = self.points[-1]
                dx = raw_pnt.X - last_point.X
                dy = raw_pnt.Y - last_point.Y
                dz = raw_pnt.Z - last_point.Z
                dist_3d = (dx * dx + dy * dy + dz * dz) ** 0.5

                if dist_3d > 1e-6:
                    dist_xy = (dx * dx + dy * dy) ** 0.5
                    dist_z = abs(dz)

                    is_horizontal = dist_xy > dist_z
                    is_vertical = dist_z > dist_xy

                    tolerance = 0.0

                    def normalize_angle(angle_deg):
                        angle_deg = angle_deg % 360.0
                        if angle_deg < 0:
                            angle_deg += 360.0
                        return angle_deg

                    def find_closest_valid_angle(angle_deg, valid_list):
                        norm_angle = normalize_angle(angle_deg)

                        def angular_distance(a, b):
                            diff = abs(a - b)
                            return min(diff, 360.0 - diff)

                        return min(
                            valid_list, key=lambda va: angular_distance(norm_angle, va)
                        )

                    if is_horizontal:
                        angle = math.atan2(dy, dx)
                        angle_deg = math.degrees(angle)

                        if len(self.points) >= 2:
                            prev_point = self.points[-2]
                            pvx = last_point.X - prev_point.X
                            pvy = last_point.Y - prev_point.Y
                            prev_dist_xy = (pvx * pvx + pvy * pvy) ** 0.5
                            prev_dist_z = abs(last_point.Z - prev_point.Z)

                            if prev_dist_xy > prev_dist_z and prev_dist_xy > 1e-6:
                                # Excepción: segmento previo como referencia 0°.
                                # Snap a [0, 90, 180, 270] relativos al segmento anterior.
                                prev_ang = normalize_angle(
                                    math.degrees(math.atan2(pvy, pvx))
                                )
                                relative_angles_full = [0.0, 90.0, 180.0, 270.0]
                                valid_angles = [
                                    normalize_angle(prev_ang + rel)
                                    for rel in relative_angles_full
                                ]
                                snap_angles = valid_angles
                            else:
                                snap_angles = [0.0, 90.0, 180.0, 270.0]
                        else:
                            snap_angles = [0.0, 90.0, 180.0, 270.0]

                        closest = find_closest_valid_angle(angle_deg, snap_angles)
                        snap_angle_rad = math.radians(closest)
                        snap_dx = dist_3d * math.cos(snap_angle_rad)
                        snap_dy = dist_3d * math.sin(snap_angle_rad)
                        current_pnt = AllplanGeo.Point3D(
                            last_point.X + snap_dx, last_point.Y + snap_dy, last_point.Z
                        )

                    elif is_vertical:
                        if dist_xy > 1e-3:
                            elevation_deg = math.degrees(math.atan2(dist_z, dist_xy))
                            valid_elevations = [0.0, 90.0]
                            closest_elev = min(
                                valid_elevations, key=lambda ve: abs(elevation_deg - ve)
                            )

                            angle_xy = math.atan2(dy, dx)
                            angle_xy_deg = math.degrees(angle_xy)
                            absolute_angles = [0.0, 90.0, 180.0, 270.0]
                            closest_xy = find_closest_valid_angle(
                                angle_xy_deg, absolute_angles
                            )

                            snap_angle_xy_rad = math.radians(closest_xy)
                            snap_elev_rad = math.radians(closest_elev)

                            if closest_elev == 90.0:
                                current_pnt = AllplanGeo.Point3D(
                                    last_point.X, last_point.Y, raw_pnt.Z
                                )
                            else:
                                dist_xy_snap = dist_3d * math.cos(snap_elev_rad)
                                dist_z_snap = dist_3d * math.sin(snap_elev_rad)
                                snap_dx = dist_xy_snap * math.cos(snap_angle_xy_rad)
                                snap_dy = dist_xy_snap * math.sin(snap_angle_xy_rad)
                                snap_dz = dist_z_snap if dz > 0 else -dist_z_snap
                                current_pnt = AllplanGeo.Point3D(
                                    last_point.X + snap_dx,
                                    last_point.Y + snap_dy,
                                    last_point.Z + snap_dz,
                                )
                        else:
                            current_pnt = AllplanGeo.Point3D(
                                last_point.X, last_point.Y, raw_pnt.Z
                            )
                    else:
                        current_pnt = raw_pnt
                else:
                    current_pnt = raw_pnt
            else:
                current_pnt = raw_pnt
        else:
            current_pnt = raw_pnt

        if self.coord_input.IsMouseMove(mouse_msg):
            # Drag de activo
            if self.is_dragging and 0 <= self.drag_index < len(self.points):
                self.points[self.drag_index] = AllplanGeo.Point3D(
                    current_pnt.X, current_pnt.Y, current_pnt.Z
                )
                self.current_point = AllplanGeo.Point3D(
                    current_pnt.X, current_pnt.Y, current_pnt.Z
                )
                self.hover_index = -1
                self.hover_seg = None
                self.hover_mid = None
                self.insert_preview_p = None
                self.insert_target = None
                self.saved_hover_point = None
                self._clear_selection_if_invalid()

            # Drag de guardado (solo Crear=OFF)
            elif (not self.create_mode) and self.saved_dragging is not None:
                pidx, vidx = self.saved_dragging
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(
                    current_pnt.X, current_pnt.Y, current_pnt.Z
                )
                self.saved_hover_point = None
                self.hover_mid = None
                self.hover_seg = None

            else:
                # ¿Rectángulo de selección activo?
                if self.box_selecting and (self.box_start is not None):
                    self.box_curr = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                else:
                    # Prioridad: puntos activos -> midpoints -> segmentos -> vértices guardados
                    self.hover_index = (
                        self._find_hover_index(current_pnt) if self.create_mode else -1
                    )
                    self.hover_mid = (
                        None
                        if self.hover_index != -1
                        else self._find_hover_midpoint(current_pnt)
                    )
                    # Hit-test 2D en vista (permite seleccionar segmentos verticales en cualquier vista)
                    view_proj = None
                    try:
                        view_proj = self.coord_input.GetViewWorldProjection()
                    except Exception:
                        pass
                    if self.create_mode:
                        self.hover_seg = (
                            None
                            if (self.hover_index != -1 or self.hover_mid is not None)
                            else self._find_hover_segment(
                                current_pnt,
                                preferred_kind="active",
                                pnt_2d=pnt,
                                view_proj=view_proj,
                            )
                        )
                    else:
                        self.hover_seg = (
                            None
                            if (self.hover_mid is not None)
                            else self._find_hover_segment(
                                current_pnt,
                                preferred_kind="saved",
                                pnt_2d=pnt,
                                view_proj=view_proj,
                            )
                        )

                    # Para edición (Crear=OFF): también trackeamos vértices guardados
                    self.saved_hover_point = None
                    if (
                        not self.create_mode
                        and self.hover_mid is None
                        and self.hover_seg is None
                    ):
                        self.saved_hover_point = self._find_hover_saved_point(
                            current_pnt
                        )

                    # Inserción preview (solo cuando NO hay midpoint bajo mouse)
                    if (
                        self.insert_mode
                        and (self.hover_seg is not None)
                        and (self.hover_mid is None)
                    ):
                        a, b = self._get_segment_endpoints(self.hover_seg)
                        if a and b:
                            t, q = self._segment_project_point(a, b, current_pnt)
                            if self._can_insert_here(a, b, t):
                                self.insert_preview_p = q
                                self.insert_target = self.hover_seg
                            else:
                                self.insert_preview_p = None
                                self.insert_target = None
                        else:
                            self.insert_preview_p = None
                            self.insert_target = None
                    else:
                        self.insert_preview_p = None
                        self.insert_target = None

            self._draw_preview(current_pnt)
            return True

        # Click izquierdo
        is_left = getattr(mouse_msg, "Button", 1) == 1

        if is_left:
            # ============================================================================
            # MODO EDICIÓN DE LAYERS: Detectar clicks en elementos generados
            # ============================================================================
            if self.preview_mode:
                _vp = None
                try:
                    _vp = self.coord_input.GetViewWorldProjection()
                except Exception:
                    pass
                clicked_element = self._find_clicked_element(
                    current_pnt, pnt_2d=pnt, view_proj=_vp
                )
                if clicked_element:
                    self._on_element_clicked(clicked_element)
                    self._draw_preview(current_pnt)
                    return True
                else:
                    # En modo preview, si no se clickeó ningún elemento, deseleccionar el elemento actual
                    if self.selected_element_id:
                        print(
                            f"[INT] Modo preview: clic en lugar vacío, deseleccionando elemento {self.selected_element_id}"
                        )
                        self.selected_element_id = None
                        self.highlight_geometry = None
                        self._draw_preview(current_pnt)
                    return True
            # Soltar drags en curso
            if self.is_dragging:
                self.is_dragging = False
                self.drag_index = -1
                self._clear_selection_if_invalid()
                self._draw_preview(current_pnt)
                return True
            if self.saved_dragging is not None:
                pidx, vidx = self.saved_dragging
                pts = self.script_object.saved_paths[pidx]
                if vidx == 0 or vidx == len(pts) - 1:  # es extremo
                    merge_target = self._find_nearby_extreme(
                        current_pnt, exclude_path=pidx
                    )
                    if merge_target:
                        target_pidx, target_end = merge_target
                        self._merge_polylines(
                            pidx,
                            "start" if vidx == 0 else "end",
                            target_pidx,
                            target_end,
                        )
                    else:
                        # mover normalmente
                        pts[vidx] = AllplanGeo.Point3D(
                            current_pnt.X, current_pnt.Y, current_pnt.Z
                        )
                        if self.saved_dragging_original_point is not None:
                            self._update_segments_after_vertex_drag(
                                pidx, vidx, self.saved_dragging_original_point
                            )
                else:
                    # mover normalmente
                    pts[vidx] = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                    if self.saved_dragging_original_point is not None:
                        self._update_segments_after_vertex_drag(
                            pidx, vidx, self.saved_dragging_original_point
                        )
                self.saved_dragging = None
                self.saved_dragging_original_point = None
                self._draw_preview(current_pnt)
                return True

            # --- MODO CREAR=ON: agregar puntos a polilínea activa ---
            if self.create_mode:
                # 1) Click sobre PUNTO ACTIVO -> iniciar drag
                self.hover_index = self._find_hover_index(current_pnt)
                if self.hover_index != -1:
                    self.is_dragging = True
                    self.drag_index = self.hover_index
                    self.points[self.drag_index] = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                    self._clear_selection_if_invalid()
                    self._draw_preview(current_pnt)
                    return True

                # 2) Click sobre MIDPOINT -> insertar punto directo
                self.hover_mid = self._find_hover_midpoint(current_pnt)
                if self.hover_mid is not None:
                    kind, path_idx, seg_idx, mp = self.hover_mid
                    seg = (kind, path_idx, seg_idx)
                    a, b = self._get_segment_endpoints(seg)
                    if a and b and self._can_insert_here(a, b, 0.5):
                        self._insert_on_segment(seg, mp, keep_selection_left=True)
                        self.insert_preview_p = None
                        self.insert_target = None
                        self.hover_seg = None
                        self.hover_mid = None
                        self._draw_preview(current_pnt)
                        return True

                # 3) Click sobre SEGMENTO: prioridad insertar si está activo
                _vp = None
                try:
                    _vp = self.coord_input.GetViewWorldProjection()
                except Exception:
                    pass
                self.hover_seg = self._find_hover_segment(
                    current_pnt,
                    preferred_kind="active",
                    pnt_2d=pnt,
                    view_proj=_vp,
                )
                if self.hover_seg is not None:
                    a, b = self._get_segment_endpoints(self.hover_seg)
                    if self.insert_mode and a and b:
                        t, q = self._segment_project_point(a, b, current_pnt)
                        if self._can_insert_here(a, b, t):
                            self._insert_on_segment(
                                self.hover_seg, q, keep_selection_left=True
                            )
                            self.insert_preview_p = None
                            self.insert_target = None
                            self.hover_seg = None
                            self.hover_mid = None
                            self._draw_preview(current_pnt)
                            return True
                    # Solo si NO está en modo insertar, permitir selección de segmento
                    if not self.insert_mode:
                        if self._seg_equal(self.selected_seg, self.hover_seg):
                            self.selected_seg = None
                        else:
                            self.selected_seg = self.hover_seg
                        self._draw_preview(current_pnt)
                        return True

                # 4) Click en vacío -> agregar vértice al final de la ACTIVA

                # Verificar ángulos válidos si está activada la limitación
                limit_angles = self._get_palette_limit_angles()
                if limit_angles:
                    # --- NUEVO: Solo permitir click si el mouse está cerca de la línea propuesta ---
                    # Usar la dirección del snap (current_pnt) y la línea desde last_point
                    last_point = self.points[-1] if self.points else None
                    if last_point is not None:
                        # Calcular proyección perpendicular del mouse a la línea propuesta
                        # (línea: last_point -> current_pnt)
                        # Distancia perpendicular del mouse real (raw_pnt) a la línea propuesta
                        # Usar la proyección del raw_pnt sobre la línea last_point-current_pnt
                        # Si la distancia es mayor a un umbral, ignorar el click
                        # Solo si el segmento propuesto no es demasiado corto
                        seg_len = self._segment_len(last_point, current_pnt)
                        if seg_len > 1e-6:
                            # Vector de la línea propuesta
                            vx = current_pnt.X - last_point.X
                            vy = current_pnt.Y - last_point.Y
                            vz = current_pnt.Z - last_point.Z
                            # Vector del mouse real
                            wx = raw_pnt.X - last_point.X
                            wy = raw_pnt.Y - last_point.Y
                            wz = raw_pnt.Z - last_point.Z

                            # Determinar el plano de la línea propuesta
                            eps = 1e-6
                            dist_xy = (vx * vx + vy * vy) ** 0.5
                            dist_xz = (vx * vx + vz * vz) ** 0.5
                            dist_yz = (vy * vy + vz * vz) ** 0.5

                            in_xz_plane = abs(vy) < eps or abs(vy) < 0.1 * max(
                                abs(vx), abs(vz), eps
                            )
                            in_yz_plane = abs(vx) < eps or abs(vx) < 0.1 * max(
                                abs(vy), abs(vz), eps
                            )

                            # Calcular proyección según el plano
                            if in_xz_plane and dist_xz > eps:
                                # Plano XZ: proyección en XZ
                                t = (vx * wx + vz * wz) / max(vx * vx + vz * vz, 1e-12)
                                proj_x = last_point.X + t * vx
                                proj_z = last_point.Z + t * vz
                                perp_dist = (
                                    (raw_pnt.X - proj_x) ** 2
                                    + (raw_pnt.Z - proj_z) ** 2
                                ) ** 0.5
                            elif in_yz_plane and dist_yz > eps:
                                # Plano YZ: proyección en YZ
                                t = (vy * wy + vz * wz) / max(vy * vy + vz * vz, 1e-12)
                                proj_y = last_point.Y + t * vy
                                proj_z = last_point.Z + t * vz
                                perp_dist = (
                                    (raw_pnt.Y - proj_y) ** 2
                                    + (raw_pnt.Z - proj_z) ** 2
                                ) ** 0.5
                            else:
                                # Plano XY: proyección en XY (caso original)
                                t = (vx * wx + vy * wy) / max(vx * vx + vy * vy, 1e-12)
                                proj_x = last_point.X + t * vx
                                proj_y = last_point.Y + t * vy
                                perp_dist = (
                                    (raw_pnt.X - proj_x) ** 2
                                    + (raw_pnt.Y - proj_y) ** 2
                                ) ** 0.5

                            if perp_dist > MAX_PERP_DIST_MM:
                                # Feedback visual
                                self._safe_set_palette_property(
                                    "FirstText",
                                    f"El mouse está demasiado lejos del ángulo propuesto (>{int(MAX_PERP_DIST_MM)} mm)",
                                )
                                return True  # Ignorar el click
                            else:
                                self._safe_set_palette_property("FirstText", "")

                    if not self._is_valid_angle(current_pnt):
                        PythonUtility.ShowMessageBox(
                            "Ángulo inválido", PythonUtility.MB_OK
                        )
                        return True  # No agregar el punto

                self.points.append(
                    AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                )
                self.current_point = AllplanGeo.Point3D(
                    current_pnt.X, current_pnt.Y, current_pnt.Z
                )
                self._clear_selection_if_invalid()
                self._draw_preview(current_pnt)

                # Verificación automática de fusión durante creación
                if len(self.points) >= 2:
                    nearby = self._find_nearby_extreme(self.points[-1])
                    if nearby:
                        # Requerir tipo de distribución antes de fusionar (crea segmentos)
                        if self._require_distribution_for_new_segments() is None:
                            return True  # Mantener el punto, no fusionar
                        target_path, target_end = nearby
                        # Agregar la polilínea activa a saved_paths temporalmente
                        new_path_idx = len(self.script_object.saved_paths)
                        self.script_object.saved_paths.append(
                            [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
                        )
                        self._merge_polylines(
                            target_path, target_end, new_path_idx, "end"
                        )  # El último punto es el que está cerca
                        # Limpiar
                        self.points.clear()
                        self._clear_editing_state()
                        self._draw_preview(current_pnt)
                        return True

                    # Verificación de vértices intermedios: mover si cerca
                    nearby_vertex = self._find_nearby_vertex(self.points[-1])
                    if nearby_vertex:
                        target_path, target_vertex_idx = nearby_vertex
                        target_point = self.script_object.saved_paths[target_path][
                            target_vertex_idx
                        ]
                        current_point = self.points[-1]
                        delta_x = target_point.X - current_point.X
                        delta_y = target_point.Y - current_point.Y
                        delta_z = target_point.Z - current_point.Z
                        # Trasladar toda la polilínea activa
                        for p in self.points:
                            p.X += delta_x
                            p.Y += delta_y
                            p.Z += delta_z
                        print(
                            f"[INT] Polilínea movida al vértice intermedio {target_vertex_idx} de polilínea {target_path} durante creación"
                        )
                        # Actualizar current_point
                        self.current_point = AllplanGeo.Point3D(
                            target_point.X, target_point.Y, target_point.Z
                        )
                        self._draw_preview(current_pnt)
                        return True

                return True

            # --- MODO CREAR=OFF: edición (guardadas) ---
            # A) Click en vértice GUARDADO -> iniciar drag de guardado
            self.saved_hover_point = self._find_hover_saved_point(current_pnt)
            if self.saved_hover_point is not None:
                pidx, vidx, _ = self.saved_hover_point
                # Capturar coordenadas originales antes del drag
                original_point = self.script_object.saved_paths[pidx][vidx]
                self.saved_dragging_original_point = AllplanGeo.Point3D(
                    original_point.X, original_point.Y, original_point.Z
                )
                self.saved_dragging = (pidx, vidx)
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(
                    current_pnt.X, current_pnt.Y, current_pnt.Z
                )
                self._draw_preview(current_pnt)
                return True

            # B) Click en MIDPOINT -> insertar punto directo (edición)
            self.hover_mid = self._find_hover_midpoint(current_pnt)
            if self.hover_mid is not None:
                kind, path_idx, seg_idx, mp = self.hover_mid
                seg = (kind, path_idx, seg_idx)
                a, b = self._get_segment_endpoints(seg)
                if a and b and self._can_insert_here(a, b, 0.5):
                    self._insert_on_segment(seg, mp, keep_selection_left=True)
                    self.insert_preview_p = None
                    self.insert_target = None
                    self.hover_seg = None
                    self.hover_mid = None
                    self._draw_preview(current_pnt)
                    return True

            # C) Click sobre SEGMENTO GUARDADO: prioridad insertar si está activo
            _vp = None
            try:
                _vp = self.coord_input.GetViewWorldProjection()
            except Exception:
                pass
            self.hover_seg = self._find_hover_segment(
                current_pnt,
                preferred_kind="saved",
                pnt_2d=pnt,
                view_proj=_vp,
            )
            if self.hover_seg is not None:
                a, b = self._get_segment_endpoints(self.hover_seg)
                if self.insert_mode and a and b:
                    t, q = self._segment_project_point(a, b, current_pnt)
                    if self._can_insert_here(a, b, t):
                        self._insert_on_segment(
                            self.hover_seg, q, keep_selection_left=True
                        )
                        self.insert_preview_p = None
                        self.insert_target = None
                        self.hover_seg = None
                        self.hover_mid = None
                        self._draw_preview(current_pnt)
                        return True
                # Solo si NO está en modo insertar, permitir selección de segmento guardado
                # IMPORTANTE: En modo preview (edición de layers), NO permitir selección de segmentos guardados
                if not self.insert_mode and not self.preview_mode:
                    if self._seg_equal(self.selected_seg, self.hover_seg):
                        self.selected_seg = None
                    else:
                        self.selected_seg = self.hover_seg
                    print(f"[INT] Toggle selección seg guardado: {self.selected_seg}")
                    self._draw_preview(current_pnt)
                    return True
                elif self.preview_mode:
                    # En modo preview, solo permitir selección de elementos generados (tubos, codos, Te's, manguitos)
                    # No permitir selección de segmentos guardados
                    print(
                        f"[INT] Modo preview activo: selección de segmentos guardados deshabilitada"
                    )
                    return False

            # D) Selección por marco de segmentos - Solo si no hay conflictos de modo
            # IMPORTANTE: En modo preview (edición de layers), NO permitir selección por marco de segmentos guardados
            if not self.preview_mode and self._can_start_box_selection():
                if not self.box_selecting:
                    self.box_selecting = True
                    self.box_start = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                    self.box_curr = AllplanGeo.Point3D(
                        current_pnt.X, current_pnt.Y, current_pnt.Z
                    )
                    print("[INT] Iniciando selección por marco")
                else:
                    # Finalizar selección por marco
                    # Validar coordenadas del rectángulo de selección
                    if (
                        self.box_start is not None
                        and self.box_curr is not None
                        and not (
                            self.box_start.X == self.box_curr.X
                            and self.box_start.Y == self.box_curr.Y
                        )
                    ):

                        sel: Set[Tuple[str, int, int]] = set()
                        for pidx, pts in enumerate(self.script_object.saved_paths):
                            if (
                                len(pts) < 2
                            ):  # Validar que la polilínea tenga al menos 2 puntos
                                continue
                            for seg_idx in range(len(pts) - 1):
                                a, b = pts[seg_idx], pts[seg_idx + 1]
                                if self._point_in_rect_xy(
                                    a, self.box_start, self.box_curr
                                ) and self._point_in_rect_xy(
                                    b, self.box_start, self.box_curr
                                ):
                                    sel.add(("saved", pidx, seg_idx))
                        self.selected_segments = sel
                        if sel:
                            print(f"[INT] Seleccionados {len(sel)} segmentos por marco")
                        else:
                            print("[INT] Ningún segmento seleccionado en el rectángulo")
                    else:
                        # Rectángulo inválido: limpiar selección
                        self.selected_segments.clear()
                        print(
                            "[INT] Rectángulo de selección inválido - selección cancelada"
                        )

                    self.box_selecting = False
                    self.box_start = None
                    self.box_curr = None
            else:
                # Si no se puede iniciar selección por marco, informar al usuario
                if not self.box_selecting:
                    print("[INT] Selección por marco no disponible en el modo actual")

            self._draw_preview(current_pnt)
            return True

        return True

    # ---------- Inserción ----------
    def _get_segment_endpoints(
        self, seg: Tuple[str, int, int]
    ) -> Tuple[Optional[AllplanGeo.Point3D], Optional[AllplanGeo.Point3D]]:
        kind, path_idx, seg_idx = seg
        if kind == "active":
            if len(self.points) >= 2 and 0 <= seg_idx < len(self.points) - 1:
                return self.points[seg_idx], self.points[seg_idx + 1]
            return None, None
        if kind == "saved":
            if 0 <= path_idx < len(self.script_object.saved_paths):
                pts = self.script_object.saved_paths[path_idx]
                if len(pts) >= 2 and 0 <= seg_idx < len(pts) - 1:
                    return pts[seg_idx], pts[seg_idx + 1]
        return None, None

    def _can_insert_here(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, t: float
    ) -> bool:
        seg_len = self._segment_len(a, b)
        if seg_len < MIN_SEG_LEN_MM:
            return False
        t_min = MAX_EPS(MIN_INSERT_OFFSET_MM / max(seg_len, 1e-6))
        return (t > t_min) and (t < 1.0 - t_min)

    def _insert_on_segment(
        self,
        seg: Tuple[str, int, int],
        q: AllplanGeo.Point3D,
        keep_selection_left: bool = True,
    ):
        kind, path_idx, seg_idx = seg

        if kind == "active":
            if not (0 <= seg_idx < len(self.points) - 1):
                return
            self.points.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))

            if self.selected_seg and self.selected_seg[0] == "active":
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = (
                        "active",
                        -1,
                        seg_idx if keep_selection_left else seg_idx + 1,
                    )
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ("active", -1, self.selected_seg[2] + 1)

        elif kind == "saved":
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return
            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return

            # Antes de insertar, guardar la información de sección del segmento original
            original_section_info = self._get_segment_section_info(
                "saved", path_idx, seg_idx
            )
            original_end_point = None
            if original_section_info:
                # Guardar el punto final original antes de la inserción
                original_end_point = AllplanGeo.Point3D(
                    pts[seg_idx + 1].X, pts[seg_idx + 1].Y, pts[seg_idx + 1].Z
                )

            # Insertar el nuevo punto
            pts.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))

            # Después de la inserción, propagar la información de sección a ambos segmentos nuevos
            if original_section_info and original_end_point:
                self._propagate_section_info_after_split(
                    path_idx, seg_idx, original_section_info, original_end_point
                )

            if (
                self.selected_seg
                and self.selected_seg[0] == "saved"
                and self.selected_seg[1] == path_idx
            ):
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = (
                        "saved",
                        path_idx,
                        seg_idx if keep_selection_left else seg_idx + 1,
                    )
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ("saved", path_idx, self.selected_seg[2] + 1)

        self.insert_preview_p = None
        self.insert_target = None

    # ---------- Borrar sección ----------
    def delete_selected_or_hovered_segment(self) -> bool:
        # Si no hay selección, reintenta con el hover actual; si tampoco hay, recalcula según modo
        target = self.selected_seg if self.selected_seg is not None else self.hover_seg

        if target is None:
            curr = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            if self.create_mode:
                target = self._find_hover_segment(curr, preferred_kind="active")
            else:
                target = self._find_hover_segment(curr, preferred_kind="saved")

        if not target:
            print("[INT] Borrar sección: sin objetivo (ni seleccionado ni hover).")
            return False

        kind, path_idx, seg_idx = target
        print(f"[INT] Borrar sección -> objetivo: {target}")

        if kind == "active":
            if len(self.points) < 2 or not (0 <= seg_idx < len(self.points) - 1):
                return False
            left = self.points[: seg_idx + 1]
            right = self.points[seg_idx + 1 :]

            if len(right) >= 2:
                self.script_object.saved_paths.append(
                    [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right]
                )

            self.points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left]

        elif kind == "saved":
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False
            pts = self.script_object.saved_paths[path_idx]
            if len(pts) < 2 or not (0 <= seg_idx < len(pts) - 1):
                return False

            # Si estamos borrando la única segmento de una rama (path con 2 puntos),
            # detectar si su extremo toca un vértice intermedio de otra polilínea (nodo Te)
            # para colapsar ese nodo y unificar los dos tramos (y aplicar longitud máx.).
            junction_to_collapse: Optional[Tuple[int, int]] = None
            if len(pts) == 2:
                for endpoint in (pts[0], pts[1]):
                    junction_to_collapse = self._find_junction_vertex_in_other_path(
                        path_idx, endpoint
                    )
                    if junction_to_collapse is not None:
                        break

            left = pts[: seg_idx + 1]
            right = pts[seg_idx + 1 :]

            new_paths: List[List[AllplanGeo.Point3D]] = []
            if len(left) >= 2:
                new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left])
            if len(right) >= 2:
                new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])

            self.script_object.saved_paths.pop(path_idx)
            for offset, path in enumerate(new_paths):
                self.script_object.saved_paths.insert(path_idx + offset, path)

            # Tras borrar la rama: colapsar el nodo en la otra polilínea (unificar tramos,
            # y si superan longitud máx. se dividen en 5000 + manguito + resto).
            if junction_to_collapse is not None:
                other_path_idx, vertex_idx = junction_to_collapse
                # Tras el pop, índices > path_idx bajaron; si other_path_idx > path_idx, ahora es other_path_idx - 1
                if other_path_idx > path_idx:
                    other_path_idx -= 1
                if self._remove_vertex_saved(other_path_idx, vertex_idx):
                    print(
                        f"[INT] Rama eliminada: nodo colapsado en polilínea {other_path_idx}, "
                        "tramos unificados (con longitud máx. aplicada si aplica)."
                    )
            else:
                # Si al borrar un segmento quedan dos polilíneas que se unen en 90°,
                # fusionarlas para que en creación se dibuje un codo en ese vértice.
                self._merge_paths_at_90_degree_junctions()
        else:
            return False

        self._clear_editing_state()
        self._draw_preview(
            self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        )
        return True

    # ---------- Guardar / Finalizar ----------
    def on_cancel_function(self):
        """
        Delegar el manejo de ESC en el ScriptObject para que se apliquen
        los mismos pasos que el botón 1003 (guardar → preview → finalizar).
        """
        print(
            "[INT] on_cancel_function: delegando ESC en ScriptObject.on_cancel_function()."
        )
        if not self.script_object:
            print("[INT] on_cancel_function: script_object no disponible.")
            return OnCancelFunctionResult.CANCEL_INPUT
        try:
            return self.script_object.on_cancel_function()
        except Exception as ex:
            print(f"[INT] Error delegando ESC en ScriptObject: {ex}")
            return OnCancelFunctionResult.CANCEL_INPUT

    def save_current_polyline(self):
        saved_successfully = False
        polyline_info = ""

        # Requerir tipo de distribución (TD o IS) antes de crear/guardar segmentos
        if len(self.points) >= 2:
            if self._require_distribution_for_new_segments() is None:
                return

        # Verificación automática de fusión: si los extremos están cerca de otros extremos, fusionar automáticamente
        if len(self.points) >= 2:
            start_extreme = self._find_nearby_extreme(self.points[0])
            end_extreme = self._find_nearby_extreme(self.points[-1])

            if start_extreme is not None or end_extreme is not None:
                # Priorizar el extremo más cercano (si ambos están cerca, elegir el que esté más cerca)
                candidates = []
                if start_extreme:
                    dist_start = self._dist_sq(
                        self.points[0],
                        self.script_object.saved_paths[start_extreme[0]][
                            0 if start_extreme[1] == "start" else -1
                        ],
                    )
                    candidates.append((dist_start, 0, start_extreme))  # 0 para start
                if end_extreme:
                    dist_end = self._dist_sq(
                        self.points[-1],
                        self.script_object.saved_paths[end_extreme[0]][
                            0 if end_extreme[1] == "start" else -1
                        ],
                    )
                    candidates.append((dist_end, -1, end_extreme))  # -1 para end

                if candidates:
                    # Elegir el candidato más cercano
                    candidates.sort(key=lambda x: x[0])
                    _, point_idx, (target_path, target_end) = candidates[0]

                    # Agregar la nueva polilínea temporalmente
                    new_path_idx = len(self.script_object.saved_paths)
                    self.script_object.saved_paths.append(
                        [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
                    )

                    # Fusionar
                    self._merge_polylines(
                        target_path,
                        target_end,
                        new_path_idx,
                        "start" if point_idx == 0 else "end",
                    )

                    saved_successfully = True
                    polyline_info = (
                        f"Fusionada automáticamente con polilínea {target_path}"
                    )
                    print(
                        f"[INT] Polilínea fusionada automáticamente con {target_path} en extremo {target_end}"
                    )

                    # Limpiar y salir
                    self.points.clear()
                    self._clear_editing_state()
                    self._clear_preview()
                    self._cleanup_orphaned_segments()
                    return

        # Verificación de vértices intermedios: si cerca, mover pero no fusionar
        if len(self.points) >= 2:
            start_vertex = self._find_nearby_vertex(self.points[0])
            end_vertex = self._find_nearby_vertex(self.points[-1])

            if start_vertex is not None or end_vertex is not None:
                candidates = []
                if start_vertex:
                    dist_start = self._dist_sq(
                        self.points[0],
                        self.script_object.saved_paths[start_vertex[0]][
                            start_vertex[1]
                        ],
                    )
                    candidates.append((dist_start, 0, start_vertex))  # 0 para start
                if end_vertex:
                    dist_end = self._dist_sq(
                        self.points[-1],
                        self.script_object.saved_paths[end_vertex[0]][end_vertex[1]],
                    )
                    candidates.append((dist_end, -1, end_vertex))  # -1 para end

                if candidates:
                    # Elegir el candidato más cercano
                    candidates.sort(key=lambda x: x[0])
                    _, point_idx, (target_path, target_vertex_idx) = candidates[0]

                    # Solo mover, no fusionar
                    target_point = self.script_object.saved_paths[target_path][
                        target_vertex_idx
                    ]
                    current_point = self.points[point_idx]
                    delta_x = target_point.X - current_point.X
                    delta_y = target_point.Y - current_point.Y
                    delta_z = target_point.Z - current_point.Z

                    # Trasladar toda la polilínea activa
                    for p in self.points:
                        p.X += delta_x
                        p.Y += delta_y
                        p.Z += delta_z

                    print(
                        f"[INT] Polilínea movida al vértice intermedio {target_vertex_idx} de polilínea {target_path}"
                    )

        # Si estamos EXTENDIENDO una guardada, fusiona en su lugar
        if self.extend_target is not None and len(self.points) >= 2:
            pidx, side = self.extend_target
            if 0 <= pidx < len(self.script_object.saved_paths):
                base = self.script_object.saved_paths[pidx]
                if side == "end":
                    # points = [anchor, p1, p2, ...] -> añadir p1.. al final
                    new_points = [
                        AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]
                    ]
                    base.extend(new_points)

                    # Crear segmentos con sección por defecto para los nuevos segmentos
                    self._create_default_segments_for_extension(
                        pidx, len(base) - len(new_points), len(base)
                    )

                else:  # 'start'
                    # Prepend en orden correcto: ... p2, p1, anchor, base...
                    prepend = list(reversed(self.points[1:]))
                    new_path = [
                        AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in prepend
                    ] + base
                    self.script_object.saved_paths[pidx] = new_path

                    # Crear segmentos con sección por defecto para los nuevos segmentos
                    self._create_default_segments_for_extension(pidx, 0, len(prepend))

                print(
                    f"[INT] Extensión fusionada en polilínea guardada #{pidx} ({side})."
                )
                saved_successfully = True
                polyline_info = f"Polilínea #{pidx + 1} extendida ({side})\nNuevos puntos: {len(self.points) - 1}"
            self.extend_target = None

        else:
            # Comportamiento normal: guardar como nueva si hay ≥2 puntos
            if len(self.points) >= 2:
                new_path = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
                self.script_object.saved_paths.append(new_path)

                # Crear segmentos con sección por defecto
                self._create_default_segments_for_new_path(
                    len(self.script_object.saved_paths) - 1
                )

                saved_successfully = True
                polyline_info = f"Nueva polilínea guardada #{len(self.script_object.saved_paths)}\nPuntos: {len(self.points)}"

        # Mostrar popup de confirmación si se guardó exitosamente
        if saved_successfully:
            total_polylines = len(self.script_object.saved_paths)
            message = f"✅ Polilínea guardada exitosamente!\n\n{polyline_info}\n\nTotal de polilíneas: {total_polylines}"
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)

        # Reset temporal de la activa
        self.points.clear()
        self._clear_editing_state()
        self._clear_preview()

        # Periodic cleanup of orphaned segments to prevent accumulation
        self._cleanup_orphaned_segments()

    def _create_default_segments_for_new_path(self, path_idx: int):
        """Crea segmentos con sección por defecto para una nueva polilínea"""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        default_diameter = self._get_default_diameter()
        system = self._get_current_system()

        for seg_idx in range(len(pts) - 1):
            label = self._format_segment_label(default_diameter, system)
            segment_info = {
                "points": [pts[seg_idx], pts[seg_idx + 1]],
                "diameter": default_diameter,
                "section_type": f"{int(default_diameter)}mm",
                "system": system,
                "label": label,
                "path_idx": path_idx,
                "seg_idx": seg_idx,
                "distribution_type": self._get_distribution_type_to_apply(),
            }
            self.script_object.saved_segments.append(segment_info)

    def _create_default_segments_for_extension(
        self, path_idx: int, start_seg: int, end_seg: int
    ):
        """Crea segmentos con sección por defecto para una extensión"""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        default_diameter = self._get_default_diameter()
        default_system = self._get_current_system()

        for seg_idx in range(start_seg, min(end_seg, len(pts) - 1)):
            # Solo crear si no existe ya un segmento para esta posición
            existing = self._get_segment_section_info("saved", path_idx, seg_idx)
            if not existing:
                # Intentar heredar la sección del segmento anterior (mismo path)
                source_info = None
                if seg_idx > 0:
                    source_info = self._get_segment_section_info(
                        "saved", path_idx, seg_idx - 1
                    )
                # Como fallback, intentar con el siguiente segmento si existe
                if source_info is None and seg_idx + 1 < len(pts) - 1:
                    source_info = self._get_segment_section_info(
                        "saved", path_idx, seg_idx + 1
                    )

                if source_info:
                    # Heredar diámetro, sistema, etiqueta y distribución del segmento vecino
                    diameter = float(source_info.get("diameter", default_diameter))
                    system = source_info.get("system", default_system)
                    section_type = source_info.get(
                        "section_type", f"{int(round(diameter))}mm"
                    )
                    label = source_info.get(
                        "label", self._format_segment_label(diameter, system)
                    )
                    segment_info = {
                        "points": [pts[seg_idx], pts[seg_idx + 1]],
                        "diameter": diameter,
                        "section_type": section_type,
                        "system": system,
                        "label": label,
                        "path_idx": path_idx,
                        "seg_idx": seg_idx,
                    }
                    # Tipo de distribución: heredar del vecino o usar el de la paleta (restaurado al editar)
                    if "distribution_type" in source_info and source_info[
                        "distribution_type"
                    ] in ["TD", "IS"]:
                        segment_info["distribution_type"] = source_info[
                            "distribution_type"
                        ]
                    else:
                        segment_info["distribution_type"] = (
                            self._get_distribution_type_to_apply()
                        )
                    # Si tenía atributos personalizados, clonarlos
                    if "custom_attributes" in source_info:
                        try:
                            segment_info["custom_attributes"] = dict(
                                source_info["custom_attributes"]
                            )
                        except Exception:
                            segment_info["custom_attributes"] = source_info[
                                "custom_attributes"
                            ]
                else:
                    # Fallback: usar el diámetro y sistema por defecto actuales
                    diameter = default_diameter
                    system = default_system
                    label = self._format_segment_label(diameter, system)
                    segment_info = {
                        "points": [pts[seg_idx], pts[seg_idx + 1]],
                        "diameter": diameter,
                        "section_type": f"{int(round(diameter))}mm",
                        "system": system,
                        "label": label,
                        "path_idx": path_idx,
                        "seg_idx": seg_idx,
                        "distribution_type": self._get_distribution_type_to_apply(),
                    }

                self.script_object.saved_segments.append(segment_info)

    def _merge_polylines(self, path1: int, end1: str, path2: int, end2: str):
        """Fusiona dos polilíneas conectándolas por sus extremos, trasladando la segunda (nueva) para que coincida con la primera (existente)"""
        if path1 == path2:
            return

        pts1 = self.script_object.saved_paths[path1]
        pts2 = self.script_object.saved_paths[path2]

        # Determinar puntos extremos
        end1_point = pts1[0] if end1 == "start" else pts1[-1]
        end2_point = pts2[0] if end2 == "start" else pts2[-1]

        # Calcular traslación para que end2_point coincida con end1_point (trasladar path2 hacia path1)
        delta_x = end1_point.X - end2_point.X
        delta_y = end1_point.Y - end2_point.Y
        delta_z = end1_point.Z - end2_point.Z

        # Trasladar pts2
        translated_pts2 = [
            AllplanGeo.Point3D(p.X + delta_x, p.Y + delta_y, p.Z + delta_z)
            for p in pts2
        ]

        # Determinar el orden de concatenación y evitar puntos duplicados
        if end1 == "end" and end2 == "start":
            new_pts = (
                pts1 + translated_pts2[1:]
            )  # pts1 termina en end1_point, translated_pts2 empieza en end1_point
        elif end1 == "start" and end2 == "end":
            new_pts = (
                list(reversed(translated_pts2[:-1])) + pts1
            )  # translated_pts2 termina en end1_point, pts1 empieza en end1_point
        elif end1 == "end" and end2 == "end":
            new_pts = pts1 + list(
                reversed(translated_pts2[:-1])
            )  # Ambos terminan en end1_point
        elif end1 == "start" and end2 == "start":
            new_pts = (
                list(reversed(translated_pts2)) + pts1[1:]
            )  # Ambos empiezan en end1_point
        else:
            return  # Caso no válido

        # Remove consecutive duplicate points
        i = 0
        while i < len(new_pts) - 1:
            if self._points_equal(new_pts[i], new_pts[i + 1]):
                del new_pts[i + 1]
            else:
                i += 1

        # Asegurar que path1 < path2 para remover el mayor primero
        if path1 > path2:
            path1, path2 = path2, path1

        # Crear nuevos segmentos preservando información de sección
        new_segments = []
        for i in range(len(new_pts) - 1):
            # Intentar encontrar información de sección del segmento correspondiente
            existing = None
            if end1 == "end" and end2 == "start":
                if i < len(pts1) - 1:
                    existing = self._get_segment_section_info("saved", path1, i)
                else:
                    seg_idx_in_path2 = i - (len(pts1) - 1)
                    existing = self._get_segment_section_info(
                        "saved", path2, seg_idx_in_path2
                    )
            # Para otros casos, simplificar: usar valores por defecto por ahora
            # TODO: implementar mapeo completo para todos los casos

            if existing:
                segment_info = {
                    "points": [new_pts[i], new_pts[i + 1]],
                    "diameter": existing["diameter"],
                    "section_type": existing["section_type"],
                    "system": existing["system"],
                    "label": existing["label"],
                    "path_idx": path1,
                    "seg_idx": i,
                }
                if "distribution_type" in existing and existing[
                    "distribution_type"
                ] in ["TD", "IS"]:
                    segment_info["distribution_type"] = existing["distribution_type"]
            else:
                # Valores por defecto (requiere TipoDeDistribucion en paleta)
                dist_type = self._get_distribution_type_to_apply()
                if dist_type not in ["TD", "IS"]:
                    dist_type = "IS"  # Fallback solo si la validación previa falló
                default_diameter = self._get_default_diameter()
                system = self._get_current_system()
                label = self._format_segment_label(default_diameter, system)
                segment_info = {
                    "points": [new_pts[i], new_pts[i + 1]],
                    "diameter": default_diameter,
                    "section_type": f"{default_diameter}mm",
                    "system": system,
                    "label": label,
                    "path_idx": path1,
                    "seg_idx": i,
                    "distribution_type": dist_type,
                }
            new_segments.append(segment_info)

        # Remover segmentos de path1 y path2
        self.script_object.saved_segments = [
            s
            for s in self.script_object.saved_segments
            if s.get("path_idx") not in (path1, path2)
        ]

        # Agregar nuevos segmentos
        self.script_object.saved_segments.extend(new_segments)

        # Actualizar path_idx de segmentos > path2
        for s in self.script_object.saved_segments:
            if s.get("path_idx", -1) > path2:
                s["path_idx"] -= 1

        # Reemplazar path1 con la nueva polilínea
        self.script_object.saved_paths[path1] = new_pts

        # Remover path2
        self.script_object.saved_paths.pop(path2)

        print(
            f"[INT] Polilíneas fusionadas con traslación: {path1} y {path2} -> nueva en {path1}"
        )

        print(
            f"[INT] Polilíneas fusionadas con traslación: {path1} y {path2} -> nueva en {path1}"
        )

    def _get_default_diameter(self) -> float:
        """Obtiene el diámetro por defecto usando la opción actualmente seleccionada en la paleta de gestión de secciones"""
        try:
            # Usar el diámetro actualmente seleccionado en la paleta de gestión de secciones
            return self._get_diameter_to_apply()
        except Exception as ex:
            print(f"[INT] Error obteniendo diámetro por defecto desde paleta: {ex}")
            return 110.0  # Fallback seguro

    # ---------- Preview ----------
    def _clear_preview(self):
        """Clear all preview elements completely. No-op if coord_input or document is invalid (e.g. during shutdown)."""
        try:
            if not getattr(self, "coord_input", None):
                return
            doc = self.coord_input.GetInputViewDocument()
            if doc is None:
                return
            # Create empty elements list to clear the preview
            empty_elems: List[AllplanBasisElements.ModelElement3D] = []

            # Use DrawElementPreview with empty list to clear previous previews
            AllplanBaseElements.DrawElementPreview(
                doc,
                AllplanGeo.Matrix3D(),
                empty_elems,
                True,  # Clear previous elements
                None,
            )

            print("[INT] Preview elements cleared")

        except Exception as ex:
            # Avoid Access violation / RTTI errors when view is already closed during cleanup
            print(f"[INT] Error clearing preview: {ex}")

    def on_preview_draw(self):
        self._sync_insert_mode_from_palette()
        hover = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        self._draw_preview(hover)

    def on_mouse_leave(self):
        self.on_preview_draw()

    def _line_with_zbias(
        self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, z_bias: float
    ):
        pa = AllplanGeo.Point3D(a.X, a.Y, a.Z + z_bias)
        pb = AllplanGeo.Point3D(b.X, b.Y, b.Z + z_bias)
        return AllplanGeo.Line3D(pa, pb)

    def _draw_preview(self, hover: Optional[AllplanGeo.Point3D]):
        elems: List[AllplanBasisElements.ModelElement3D] = []

        base_prop = self._clone_properties(self.com_prop)
        handle_prop = self._clone_properties(self.com_prop)
        handle_prop.Color = HANDLE_COLOR_IDX  # amarillo

        saved_prop = self._clone_properties(self.com_prop)
        saved_prop.Color = (
            PREVIEW_SAVED_COLOR  # Color verde solo para preview de polilíneas guardadas
        )

        seg_hover_prop = self._clone_properties(self.com_prop)
        seg_hover_prop.Color = SEGMENT_HOVER_COLOR
        seg_hover_prop.ColorByLayer = False
        seg_hover_prop.PenByLayer = False
        seg_hover_prop.StrokeByLayer = False
        try:
            seg_hover_prop.Pen = max(
                SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1)
            )
        except Exception:
            pass

        seg_sel_prop = self._clone_properties(self.com_prop)
        seg_sel_prop.Color = SEGMENT_SEL_COLOR
        seg_sel_prop.ColorByLayer = False
        seg_sel_prop.PenByLayer = False
        seg_sel_prop.StrokeByLayer = False
        try:
            seg_sel_prop.Pen = max(
                SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1)
            )
        except Exception:
            pass

        ins_prev_prop = self._clone_properties(self.com_prop)
        ins_prev_prop.Color = INSERT_PREVIEW_COLOR

        branch_anchor_prop = self._clone_properties(self.com_prop)
        branch_anchor_prop.Color = BRANCH_ANCHOR_COLOR

        # Midpoints props (con pen propio y sin ByLayer)
        mid_prop = self._clone_properties(self.com_prop)
        mid_prop.Color = MIDPOINT_COLOR
        mid_prop.PenByLayer = False
        mid_prop.ColorByLayer = False
        mid_prop.StrokeByLayer = False
        try:
            mid_prop.Pen = max(MIDPOINT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass
        mid_size = HANDLE_SIZE * MIDPOINT_SIZE_FACTOR

        # Rectángulo de selección
        rect_prop = self._clone_properties(self.com_prop)
        rect_prop.Color = RECT_COLOR
        rect_prop.PenByLayer = False
        rect_prop.ColorByLayer = False
        rect_prop.StrokeByLayer = False
        try:
            rect_prop.Pen = max(RECT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass

        # Guardadas
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) >= 2:
                # Dibujar segmentos individuales con color de selección si están seleccionados (por click o por marco)
                for seg_idx in range(len(pts) - 1):
                    a, b = pts[seg_idx], pts[seg_idx + 1]
                    # ¿Está seleccionado por click o por marco?
                    is_selected = False
                    if (
                        self.selected_seg
                        and self.selected_seg[0] == "saved"
                        and self.selected_seg[1] == path_idx
                        and self.selected_seg[2] == seg_idx
                    ):
                        is_selected = True
                    if ("saved", path_idx, seg_idx) in getattr(
                        self, "selected_segments", set()
                    ):
                        is_selected = True
                    # ¿Está hover?
                    is_hovered = (
                        self.hover_seg
                        and self.hover_seg[0] == "saved"
                        and self.hover_seg[1] == path_idx
                        and self.hover_seg[2] == seg_idx
                    )
                    # Propiedades
                    if is_selected:
                        prop = seg_sel_prop
                    elif is_hovered and not self.is_dragging:
                        prop = seg_hover_prop
                    else:
                        # Verificar si este segmento tiene sección configurada
                        section_info = self._get_segment_section_info(
                            "saved", path_idx, seg_idx
                        )
                        if section_info:
                            prop = self._clone_properties(self.com_prop)
                            # Aplicar color específico según diámetro y sistema
                            diameter = section_info.get("diameter", 110.0)
                            system = section_info.get("system", "Pluvial")
                            prop.Color = self._get_section_color_for_preview(
                                diameter, system
                            )
                            prop.ColorByLayer = False
                        else:
                            prop = saved_prop
                    # Crear línea del segmento
                    line = AllplanGeo.Line3D(a, b)
                    elems.append(AllplanBasisElements.ModelElement3D(prop, line))
                    # Etiqueta de texto en el punto medio si hay info de sección con label
                    if (
                        is_selected
                        and self._get_segment_section_info("saved", path_idx, seg_idx)
                        and self._get_segment_section_info(
                            "saved", path_idx, seg_idx
                        ).get("label")
                    ):
                        self._add_text_label(
                            elems,
                            a,
                            b,
                            str(
                                self._get_segment_section_info(
                                    "saved", path_idx, seg_idx
                                )["label"]
                            ),
                        )

                # Midpoints (guardadas)
                for si in range(len(pts) - 1):
                    a, b = pts[si], pts[si + 1]
                    mp = self._midpoint(a, b)
                    is_selected = False
                    if (
                        self.selected_seg
                        and self.selected_seg[0] == "saved"
                        and self.selected_seg[1] == path_idx
                        and self.selected_seg[2] == si
                    ):
                        is_selected = True
                    if ("saved", path_idx, si) in getattr(
                        self, "selected_segments", set()
                    ):
                        is_selected = True
                    is_hovered = (
                        self.hover_seg
                        and self.hover_seg[0] == "saved"
                        and self.hover_seg[1] == path_idx
                        and self.hover_seg[2] == si
                    )
                    if is_selected:
                        elems.extend(
                            self._create_cross_marker(
                                mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )
                    elif is_hovered and not self.is_dragging:
                        elems.extend(
                            self._create_cross_marker(
                                mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )
                    else:
                        elems.extend(
                            self._create_cross_marker(
                                mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )

                # Vértices de polilíneas guardadas: handlers circulares (igual estilo que activa)
                for vidx, vpt in enumerate(pts):
                    size = HANDLE_SIZE * 0.60
                    # si el vértice está siendo arrastrado (guardado), agrandar
                    if self.saved_dragging is not None and self.saved_dragging == (
                        path_idx,
                        vidx,
                    ):
                        size = HANDLE_SIZE * DRAG_SCALE
                    # si hay hover del punto guardado
                    if (
                        self.saved_hover_point is not None
                        and self.saved_hover_point[0] == path_idx
                        and self.saved_hover_point[1] == vidx
                        and not self.is_dragging
                    ):
                        size = HANDLE_SIZE * HOVER_SCALE
                    elems.extend(self._create_point_marker(vpt, handle_prop, size))

        # Activa + rubber-band (si hay activa)
        if self.points:
            poly = AllplanGeo.Polyline3D()
            for pt in self.points:
                poly += pt
            if (
                hover is not None
                and not self.is_dragging
                and self.hover_seg is None
                and self.create_mode
            ):
                poly += hover
            elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))

            # Handles (activa)
            for idx, pt in enumerate(self.points):
                size = HANDLE_SIZE * 0.65
                if idx == self.hover_index and not self.is_dragging:
                    size = HANDLE_SIZE * HOVER_SCALE
                if idx == self.drag_index and self.is_dragging:
                    size = HANDLE_SIZE * DRAG_SCALE
                elems.extend(self._create_point_marker(pt, handle_prop, size))

            # Selección/hover en activa (con overlay + z-bias)
            selected_i = (
                self.selected_seg[2]
                if (self.selected_seg and self.selected_seg[0] == "active")
                else -1
            )
            hovered_i = (
                self.hover_seg[2]
                if (self.hover_seg and self.hover_seg[0] == "active")
                else -1
            )

            if selected_i != -1 and 0 <= selected_i < len(self.points) - 1:
                a, b = self.points[selected_i], self.points[selected_i + 1]
                elems.append(
                    AllplanBasisElements.ModelElement3D(
                        seg_sel_prop,
                        self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS),
                    )
                )

            if (
                self.hover_seg
                and self.hover_seg[0] == "active"
                and not self.is_dragging
            ):
                si = self.hover_seg[2]
                if si != selected_i and 0 <= si < len(self.points) - 1:
                    a, b = self.points[si], self.points[si + 1]
                    elems.append(
                        AllplanBasisElements.ModelElement3D(
                            seg_hover_prop,
                            self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS),
                        )
                    )

            # Midpoints (activa) como cruzetas
            if len(self.points) >= 2:
                for si in range(len(self.points) - 1):
                    a, b = self.points[si], self.points[si + 1]
                    mp = self._midpoint(a, b)
                    if si == selected_i:
                        elems.extend(
                            self._create_cross_marker(
                                mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )
                    elif si == hovered_i and not self.is_dragging:
                        elems.extend(
                            self._create_cross_marker(
                                mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )
                    else:
                        elems.extend(
                            self._create_cross_marker(
                                mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS
                            )
                        )

        # Punto fantasma de inserción (checkbox ON)
        if (
            self.insert_mode
            and self.insert_preview_p is not None
            and self.insert_target is not None
        ):
            elems.extend(
                self._create_point_marker(
                    self.insert_preview_p, ins_prev_prop, HANDLE_SIZE * 0.95
                )
            )

        # Rectángulo de selección (si está activo)
        if (
            self.box_selecting
            and self.box_start is not None
            and self.box_curr is not None
        ):
            a = self.box_start
            b = self.box_curr
            p1 = AllplanGeo.Point3D(a.X, a.Y, a.Z)
            p2 = AllplanGeo.Point3D(b.X, a.Y, a.Z)
            p3 = AllplanGeo.Point3D(b.X, b.Y, a.Z)
            p4 = AllplanGeo.Point3D(a.X, b.Y, a.Z)
            for s, e in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
                elems.append(
                    AllplanBasisElements.ModelElement3D(
                        rect_prop, AllplanGeo.Line3D(s, e)
                    )
                )

        # Feedback visual para fusión de polilíneas (línea cyan)
        if self.saved_dragging is not None and hover is not None:
            pidx, vidx = self.saved_dragging
            pts = self.script_object.saved_paths[pidx]
            if vidx == 0 or vidx == len(pts) - 1:
                merge_target = self._find_nearby_extreme(hover, exclude_path=pidx)
                if merge_target:
                    target_pidx, target_end = merge_target
                    target_pts = self.script_object.saved_paths[target_pidx]
                    target_point = (
                        target_pts[0] if target_end == "start" else target_pts[-1]
                    )
                    # Dibujar línea cyan entre hover y target_point
                    cyan_prop = self._clone_properties(self.com_prop)
                    cyan_prop.Color = 6  # cyan
                    elems.append(
                        AllplanBasisElements.ModelElement3D(
                            cyan_prop, AllplanGeo.Line3D(hover, target_point)
                        )
                    )

        # --- FEEDBACK VISUAL: cruceta grande y roja sobre el mouse si el ángulo es válido ---
        # Solo en modo creación, con Limitar ángulos activo, y si hover existe
        if self.create_mode and hover is not None:
            limit_angles = self._get_palette_limit_angles()
            # Solo mostrar si el ángulo sería válido
            if limit_angles:
                if len(self.points) < 1:
                    show_cross = True
                else:
                    last_point = self.points[-1]
                    dx = hover.X - last_point.X
                    dy = hover.Y - last_point.Y
                    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
                        show_cross = False
                    else:
                        angle_deg = math.degrees(math.atan2(dy, dx)) % 360.0
                        valid_angles = [0.0, 90.0, 180.0, 270.0]
                        # Tolerancia visual: mostrar cruceta cuando estamos "cerca" del ángulo válido
                        # (la validación real sigue siendo estricta; esto solo mejora el feedback)
                        cross_tolerance = 8.0

                        def _ang_dist(a, b):
                            d = abs(a - b)
                            return min(d, 360.0 - d)

                        if len(self.points) >= 2:
                            prev = self.points[-2]
                            v1x = last_point.X - prev.X
                            v1y = last_point.Y - prev.Y
                            prev_dist_xy = (v1x * v1x + v1y * v1y) ** 0.5
                            prev_dist_z = abs(last_point.Z - prev.Z)
                            if prev_dist_xy > prev_dist_z and prev_dist_xy > 1e-6:
                                # Excepción: ángulos relativos al segmento anterior.
                                ang1 = math.degrees(math.atan2(v1y, v1x)) % 360.0
                                delta = (angle_deg - ang1) % 360.0
                                show_cross = any(
                                    _ang_dist(delta, va) <= cross_tolerance
                                    for va in valid_angles
                                )
                            else:
                                show_cross = any(
                                    _ang_dist(angle_deg, va) <= cross_tolerance
                                    for va in valid_angles
                                )
                        else:
                            show_cross = any(
                                _ang_dist(angle_deg, va) <= cross_tolerance
                                for va in valid_angles
                            )
                if show_cross:
                    # Handler grande y rojo
                    cross_size = HANDLE_SIZE * 1.2
                    cross_prop = self._clone_properties(self.com_prop)
                    cross_prop.Color = 5  # azul
                    cross_prop.PenByLayer = False
                    cross_prop.ColorByLayer = False
                    cross_prop.StrokeByLayer = False
                    cross_elems = self._create_cross_marker(
                        hover, cross_prop, cross_size, z_bias=4.0
                    )
                    elems.extend(cross_elems)

        # ============================================================================
        # MODO EDICIÓN DE LAYERS: Dibujar elementos generados con fitting
        # ============================================================================
        if self.preview_mode and self.generated_elements:
            # Propiedades para elementos generados
            gen_elem_prop = self._clone_properties(self.com_prop)
            gen_elem_prop.Color = 67  # Color por defecto
            gen_elem_prop.ColorByLayer = False

            # Propiedad para elemento seleccionado
            selected_elem_prop = self._clone_properties(self.com_prop)
            selected_elem_prop.Color = 5  # Azul para seleccionado
            selected_elem_prop.ColorByLayer = False
            selected_elem_prop.Pen = 3  # Pen más grueso

            for element in self.generated_elements:
                element_key = element.get("key")
                element_type = element.get("type")
                geometry = element.get("geometry")
                layer = self.layer_overrides.get(element_key, element.get("layer", 0))

                # Usar propiedades según si está seleccionado
                if element_key == self.selected_element_id:
                    elem_prop = selected_elem_prop
                else:
                    elem_prop = gen_elem_prop
                    elem_prop.Layer = layer

                if geometry:
                    try:
                        # Crear ModelElement3D con la geometría
                        if isinstance(geometry, AllplanGeo.Line3D):
                            # Para tubos: dibujar línea
                            elem = AllplanBasisElements.ModelElement3D(
                                elem_prop, geometry
                            )
                            elems.append(elem)
                        elif isinstance(geometry, AllplanGeo.Polyhedron3D):
                            # Para codos: dibujar poliedro
                            elem = AllplanBasisElements.ModelElement3D(
                                elem_prop, geometry
                            )
                            elems.append(elem)
                    except Exception as ex:
                        print(f"[INT] Error dibujando elemento {element_type}: {ex}")

            # Dibujar highlight del elemento seleccionado
            if self.highlight_geometry:
                highlight_prop = self._clone_properties(self.com_prop)
                highlight_prop.Color = 1  # Rojo para highlight
                highlight_prop.ColorByLayer = False
                try:
                    highlight_elem = AllplanBasisElements.ModelElement3D(
                        highlight_prop, self.highlight_geometry
                    )
                    elems.append(highlight_elem)
                except Exception as ex:
                    print(f"[INT] Error dibujando highlight: {ex}")

        # ============================================================================
        # MARCADORES DE ELEMENTOS DEFINIDOS (T sortida, Colze base, Clau de Pas)
        # ============================================================================
        elem_def_prop = self._clone_properties(self.com_prop)
        elem_def_prop.Color = 6  # cian
        elem_def_prop.ColorByLayer = False
        elem_def_prop.PenByLayer = False
        for m in getattr(self, "element_markers", []) or []:
            pos = m.get("pos")
            if pos is None:
                continue
            if hasattr(pos, "X"):
                pt = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)
            else:
                continue
            radius = float(m.get("radius", 50.0) or 50.0)
            if radius <= 0:
                radius = 50.0
            elems.extend(self._create_point_marker(pt, elem_def_prop, radius * 2.0))
        # Preview del punto seleccionado (modo Intermedio) antes de agregar
        if (
            self.element_point_capture_mode
            and self.element_selected_point is None
            and hover is not None
        ):
            elems.extend(self._create_point_marker(hover, elem_def_prop, 40.0))

        # ============================================================================
        # PUNTOS LIBRES (modo "Modo puntos libres"): solo cálculo de hover/selección
        # (la representación visual se hace con el 3D real más abajo)
        # ============================================================================
        free_placed = getattr(self.script_object, "free_placed_points", None) or []
        try:
            tol = self._get_free_point_selection_tolerance()
            if hover is not None:
                self.free_point_hover_index = find_hover_free_point(
                    hover, free_placed, tol
                )
            else:
                self.free_point_hover_index = -1
        except Exception:
            self.free_point_hover_index = -1
        fp_hover_idx = getattr(self, "free_point_hover_index", -1)
        fp_sel_idx = getattr(self, "free_point_selected_index", None)

        # ============================================================================
        # PREVIEW DE LÍNEA DE ORIENTACIÓN 3D
        # ============================================================================
        if self.orientation_capture_mode and self.orientation_line_start is not None:
            # Crear propiedades para la línea de orientación
            orient_prop = self._clone_properties(self.com_prop)
            orient_prop.Color = 3  # Verde
            orient_prop.ColorByLayer = False
            orient_prop.PenByLayer = False
            orient_prop.StrokeByLayer = False
            orient_prop.Pen = 15  # Línea más gruesa

            # Determinar el punto final: usar el punto guardado si existe, sino el preview, sino hover
            if self.orientation_line_end is not None:
                # Ya tenemos el segundo punto guardado
                end_point = self.orientation_line_end
            elif self.orientation_line_preview is not None:
                # Usar el preview del mouse
                end_point = self.orientation_line_preview
            else:
                # Usar el hover actual
                end_point = hover

            if end_point is not None:
                # Forzar Z=0 para ambos puntos (plano XY)
                p1_xy = AllplanGeo.Point3D(
                    self.orientation_line_start.X, self.orientation_line_start.Y, 0.0
                )
                p2_xy = AllplanGeo.Point3D(end_point.X, end_point.Y, 0.0)
                orient_line = AllplanGeo.Line3D(p1_xy, p2_xy)
                elems.append(
                    AllplanBasisElements.ModelElement3D(orient_prop, orient_line)
                )

        doc = self.coord_input.GetInputViewDocument()
        AllplanBaseElements.DrawElementPreview(
            doc,
            AllplanGeo.Matrix3D(),
            elems,
            True,  # Clear previous elements to prevent memory accumulation
            None,
        )

        # Tras dibujar la polilínea y manejadores, dibujar el elemento 3D real
        # de los puntos libres (modo "Modo puntos libres") y el que sigue al cursor.
        try:
            # Puntos libres ya colocados (preview 3D real)
            free_placed = getattr(self.script_object, "free_placed_points", None) or []
            build_ele = getattr(self.script_object, "build_ele", None)

            # Si hay un punto libre seleccionado, actualizar su rotación almacenada
            # leyendo los valores actuales de la paleta (paleta -> punto).
            if (
                build_ele is not None
                and fp_sel_idx is not None
                and 0 <= fp_sel_idx < len(free_placed)
            ):
                try:
                    ed_update_free_point_rotation_from_palette(
                        self.script_object, fp_sel_idx
                    )
                except Exception:
                    pass

            # Etiquetas de rotación para el punto seleccionado (texto 2D en el modelo)
            rot_labels = []

            for i, fp in enumerate(free_placed):
                pos = fp.get("pos")
                if pos is None or not hasattr(pos, "X"):
                    continue
                pt = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)
                # Etiqueta de rotación para el punto seleccionado: crear siempre que haya posición válida,
                # independientemente de si hay model_list (así se muestra al seleccionar aunque falle el 3D)
                if i == fp_sel_idx:
                    try:
                        rx = float(fp.get("rot_x", 0.0) or 0.0)
                        ry = float(fp.get("rot_y", 0.0) or 0.0)
                        rz = float(fp.get("rot_z", 0.0) or 0.0)
                        label_text = f"RotX={rx:.1f}  RotY={ry:.1f}  RotZ={rz:.1f}"

                        text_com_prop = AllplanBaseElements.CommonProperties()
                        text_com_prop.Pen = 1
                        text_com_prop.Color = 7  # gris claro
                        text_com_prop.Construction = True

                        text_prop = AllplanBasisElements.TextProperties()
                        text_prop.Height = 0.10
                        text_prop.Width = 0.10
                        text_prop.IsScaleDependent = False

                        loc = AllplanGeo.Point2D(pt.X - 50.0, pt.Y + 50.0)
                        rot_labels.append(
                            AllplanBasisElements.TextElement(
                                text_com_prop, text_prop, label_text, loc
                            )
                        )
                    except Exception as ex:
                        print(f"[INT] No se pudo crear etiqueta de rotación: {ex}")

                etype = fp.get("element_type", "clau_de_pas")
                model_list = self.script_object._get_element_model_list_agua(
                    build_ele, doc, etype
                )
                print(
                    f"[INT] Preview 3D punto libre {i}: type={etype}, models={len(model_list)}"
                )
                if not model_list:
                    continue

                # Aplicar rotación específica del punto libre si está disponible
                prev_values = {}
                if build_ele is not None:
                    try:
                        for attr_name, fp_key in (
                            ("RotX", "rot_x"),
                            ("RotY", "rot_y"),
                            ("RotZ", "rot_z"),
                        ):
                            param = getattr(build_ele, attr_name, None)
                            if param is None or not hasattr(param, "value"):
                                continue
                            prev_values[attr_name] = param.value
                            fp_val = fp.get(fp_key, None)
                            if fp_val is None:
                                # Si no hay valor guardado, dejar el global
                                continue
                            try:
                                param.value = float(fp_val)
                            except Exception:
                                pass
                    except Exception:
                        prev_values = {}

                try:
                    mat = self.script_object._build_rotation_matrix_for_element(pt)
                finally:
                    # Restaurar RotX/RotY/RotZ globales
                    if build_ele is not None and prev_values:
                        try:
                            for attr_name, old_val in prev_values.items():
                                param = getattr(build_ele, attr_name, None)
                                if param is None or not hasattr(param, "value"):
                                    continue
                                param.value = old_val
                        except Exception:
                            pass

                # Dibujar el elemento 3D (apariencia normal)
                AllplanBaseElements.DrawElementPreview(
                    doc,
                    mat,
                    model_list,
                    False,
                    None,
                )

                # Si es el punto seleccionado, resaltar el mismo elemento (contorno con color/trazo de resaltado)
                if i == fp_sel_idx:
                    try:
                        highlight_list = []
                        for me in model_list:
                            geo = getattr(me, "GeometryObject", None) or getattr(
                                me, "Geometry", None
                            )
                            if geo is None:
                                continue
                            cp = getattr(me, "CommonProperties", None)
                            if cp is None and hasattr(me, "GetCommonProperties"):
                                cp = me.GetCommonProperties()
                            cp_hl = (
                                self._clone_properties(cp)
                                if cp is not None
                                else self._clone_properties(self.com_prop)
                            )
                            cp_hl.Color = 3  # verde resaltado
                            cp_hl.Pen = 5
                            cp_hl.ColorByLayer = False
                            cp_hl.PenByLayer = False
                            cp_hl.Construction = True
                            highlight_list.append(
                                AllplanBasisElements.ModelElement3D(cp_hl, geo)
                            )
                        if highlight_list:
                            AllplanBaseElements.DrawElementPreview(
                                doc,
                                mat,
                                highlight_list,
                                False,
                                None,
                            )
                    except Exception as ex:
                        print(f"[INT] No se pudo crear resaltado del elemento: {ex}")

            # Dibujar etiquetas de rotación (si las hay) sin limpiar el preview previo
            if rot_labels:
                try:
                    AllplanBaseElements.DrawElementPreview(
                        doc,
                        AllplanGeo.Matrix3D(),
                        rot_labels,
                        False,
                        None,
                    )
                except Exception as ex:
                    print(f"[INT] Error dibujando etiquetas de rotación: {ex}")

            # Preview del elemento en el cursor al esperar clic (modo puntos libres, 3D)
            if getattr(self, "next_click_adds_free_point", False) and hover is not None:
                element_type, _ = self._get_defined_element_settings()
                build_ele = getattr(self.script_object, "build_ele", None)
                model_list = self.script_object._get_element_model_list_agua(
                    build_ele, doc, element_type
                )
                if model_list:
                    print(
                        f"[INT] Preview 3D cursor: type={element_type}, models={len(model_list)}"
                    )
                    mat = self.script_object._build_rotation_matrix_for_element(hover)
                    AllplanBaseElements.DrawElementPreview(
                        doc,
                        mat,
                        model_list,
                        False,
                        None,
                    )
        except Exception as ex:
            print(f"[INT] Error dibujando preview 3D de puntos libres: {ex}")

    # ---------- Gestión de Secciones ----------
    def apply_section_to_selected(self):
        """Aplica la sección seleccionada en la paleta a los segmentos seleccionados"""
        try:
            # ============================================================================
            # MODO EDICIÓN DE LAYERS (PREVIEW MODE)
            # ============================================================================
            if self.preview_mode:
                # En modo preview, verificar si hay un elemento generado seleccionado
                if self.selected_element_id:
                    # Buscar el elemento seleccionado
                    selected_element = None
                    for element in self.generated_elements:
                        if element.get("key") == self.selected_element_id:
                            selected_element = element
                            break

                    if selected_element:
                        element_type = selected_element.get("type", "")

                        # Solo permitir aplicar diámetro a tubos
                        if element_type != "tube":
                            # Determinar el nombre del elemento para el mensaje
                            tipo_nombre = {
                                "elbow": "Codo",
                                "manguito": "Manguito",
                                "te": "Te",
                            }.get(element_type, "Elemento")

                            mensaje = (
                                f"Operación no permitida\n\n"
                                f"El cambio de diámetro solo puede aplicarse a TUBOS.\n\n"
                                f"El elemento seleccionado es un {tipo_nombre}, que es un elemento de unión "
                                f"con diámetros fijos según su tipo.\n\n"
                                f"Para cambiar el diámetro:\n"
                                f"• Seleccione un TUBO\n"
                                f"• O modifique los diámetros de los segmentos antes de crear los elementos"
                            )

                            try:
                                # Mostrar mensaje modal en Allplan
                                PythonUtility.ShowMessageBox(
                                    mensaje,
                                    PythonUtility.MB_OK,
                                )
                                print(
                                    f"[INT] ⚠ Mostrado mensaje: No se puede aplicar diámetro a {tipo_nombre.lower()} en modo preview"
                                )
                            except Exception as ex:
                                print(f"[INT] Error mostrando mensaje modal: {ex}")
                                # Fallback: mostrar solo en consola si falla el modal
                                print(
                                    f"[INT] ⚠ No se puede aplicar diámetro a {tipo_nombre.lower()} en modo preview"
                                )

                            print(
                                f"[INT] ⚠ No se puede aplicar diámetro a {tipo_nombre.lower()} en modo preview"
                            )
                            return False

                        # Si es un tubo, aplicar el diámetro al segmento correspondiente
                        path_idx = selected_element.get("path_idx")
                        seg_idx = selected_element.get("seg_idx")

                        if path_idx is not None and seg_idx is not None:
                            diameter = self._get_diameter_to_apply()
                            if diameter <= 0:
                                print("[INT] Error: diámetro inválido")
                                return False

                            if self._apply_diameter_to_segment(
                                path_idx, seg_idx, diameter
                            ):
                                print(
                                    f"[INT] Aplicado diámetro {diameter}mm al tubo seleccionado"
                                )
                                self._draw_preview(
                                    self.coord_input.GetCurrentPoint(
                                        self.current_point
                                    ).GetPoint()
                                )
                                return True

                    print("[INT] ⚠ No se encontró el elemento seleccionado")
                    return False
                else:
                    print(
                        "[INT] ⚠ No hay ningún elemento seleccionado en EDICIÓN DE LAYERS"
                    )
                    print("[INT] AYUDA: Haz clic en un tubo para seleccionarlo")
                    return False

            # ============================================================================
            # MODO NORMAL: Aplicar diámetro a segmentos guardados
            # ============================================================================
            # Obtener el diámetro a aplicar
            diameter = self._get_diameter_to_apply()
            if diameter <= 0:
                print("[INT] Error: diámetro inválido")
                return False

            applied_count = 0

            # Aplicar a segmentos seleccionados por marco
            if self.selected_segments:
                for kind, path_idx, seg_idx in self.selected_segments:
                    if kind == "saved":
                        if self._apply_diameter_to_segment(path_idx, seg_idx, diameter):
                            applied_count += 1

            # Si no hay selección por marco, aplicar al segmento hover/seleccionado
            elif self.selected_seg or self.hover_seg:
                target = self.selected_seg or self.hover_seg
                kind, path_idx, seg_idx = target
                if kind == "saved":
                    if self._apply_diameter_to_segment(path_idx, seg_idx, diameter):
                        applied_count += 1

            if applied_count > 0:
                print(
                    f"[INT] Aplicado diámetro {diameter}mm a {applied_count} segmento(s)"
                )
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
                return True
            else:
                print("[INT] No hay segmentos seleccionados para aplicar sección")
                print("[INT] AYUDA: Para seleccionar segmentos:")
                print("[INT] - Haz clic en un segmento de polilínea guardada")
                print("[INT] - O arrastra para crear un marco de selección")
                return False

        except Exception as ex:
            print(f"[INT] Error aplicando sección: {ex}")
            return False

    def _get_diameter_to_apply(self) -> float:
        """Obtiene el diámetro a aplicar desde la paleta"""
        try:
            # Primero verificar si hay diámetro personalizado
            custom_diameter = self._safe_get_palette_property("DiametroPersonalizado")

            if custom_diameter is not None and custom_diameter > 0:
                return float(custom_diameter)

            # Determinar el tipo de saneamiento para usar el control correcto
            saneamiento_type = self._safe_get_palette_property("Saneamiento")

            selected_diameter = None

            if saneamiento_type is not None:
                if saneamiento_type == 0:  # Pluvial
                    selected_diameter = self._safe_get_palette_property(
                        "DiametroAplicarPluvial"
                    )
                    if selected_diameter is None:
                        # Usar diámetro por defecto para pluvial
                        return 110.0
                else:  # Fecal (saneamiento_type == 1)
                    # Para fecal, intentar primero el control específico
                    selected_diameter = self._safe_get_palette_property(
                        "DiametroAplicarFecal"
                    )

                    # Si no existe, intentar el control general de diámetro
                    if selected_diameter is None:
                        selected_diameter = self._safe_get_palette_property("Diametro")

                    # Si tampoco existe, usar diámetro por defecto para fecal
                    if selected_diameter is None:
                        return 40.0

            # Si tenemos un valor específico válido, usarlo
            if selected_diameter is not None and selected_diameter > 0:
                return float(selected_diameter)

            # Fallback al control original por compatibilidad (solo si los otros no funcionaron)
            fallback_diameter = self._safe_get_palette_property("DiametroAplicar")

            if fallback_diameter is not None and fallback_diameter > 0:
                return float(fallback_diameter)

            # Como último recurso, usar el diámetro por defecto del tipo de saneamiento
            default_diameter = self._get_default_diameter()
            return default_diameter

        except Exception as ex:
            print(f"[INT] Error obteniendo diámetro: {ex}")
            return 110.0  # Valor seguro por defecto

    def _apply_diameter_to_segment(
        self, path_idx: int, seg_idx: int, diameter: float
    ) -> bool:
        """Aplica un diámetro específico a un segmento guardado"""
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return False

            # Obtener los puntos del segmento actual
            point1 = pts[seg_idx]
            point2 = pts[seg_idx + 1]

            # Obtener sistema actual y generar etiqueta
            system = self._get_current_system()
            label = self._format_segment_label(diameter, system)

            # Buscar si ya existe una configuración para este segmento
            segment_found = False
            for i, existing_segment in enumerate(self.script_object.saved_segments):
                existing_points = existing_segment["points"]
                if (
                    len(existing_points) >= 2
                    and self._points_equal(existing_points[0], point1)
                    and self._points_equal(existing_points[1], point2)
                ):
                    # Actualizar el segmento existente
                    existing_segment = self.script_object.saved_segments[i]

                    existing_segment["points"] = [point1, point2]
                    existing_segment["diameter"] = diameter
                    existing_segment["section_type"] = f"{diameter}mm"
                    existing_segment["system"] = system
                    existing_segment["label"] = label

                    # Aseguramos que sigan teniendo path_idx / seg_idx
                    existing_segment["path_idx"] = path_idx
                    existing_segment["seg_idx"] = seg_idx
                    segment_found = True
                    print(
                        f"[INT] Segmento {path_idx}-{seg_idx} actualizado con diámetro {diameter}mm, sistema {system}"
                    )
                    break

            # Si no se encontró, agregar como nuevo
            if not segment_found:
                dist_type = self._get_distribution_type_to_apply() or "IS"
                segment_info = {
                    "points": [point1, point2],
                    "diameter": diameter,
                    "section_type": f"{diameter}mm",
                    "system": system,
                    "label": label,
                    "path_idx": path_idx,
                    "seg_idx": seg_idx,
                    "distribution_type": dist_type,
                }
                self.script_object.saved_segments.append(segment_info)
                print(
                    f"[INT] Segmento {path_idx}-{seg_idx} configurado con diámetro {diameter}mm, sistema {system}"
                )

            # Forzar redibujado para actualizar las etiquetas
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )

            return True

        except Exception as ex:
            print(f"[INT] Error aplicando diámetro a segmento: {ex}")
            return False

    # ---------- Gestión de Layers ----------
    def _get_layer_mapping(self) -> dict:
        """
        Retorna el mapa de short_names de layers según el tipo de instalación.
        Basado en la orientación (horizontal/vertical) y tipo de instalación.
        Según documentación oficial de Allplan:
        - Horizontales (techo): FABRICA=IS_CON_AIGUA_FAB, OBRA=IS_AIG_CON_CLIMA_OBR
        - Verticales (pared): TD=KN_AIGUA, EN_X=KN_X_AIGUA, EN_Y=KN_Y_AIGUA
        """
        # Mapa de layers según tipo de instalación
        # Según documentación oficial de Allplan:
        # - Horizontales (techo): FABRICA=40139, OBRA=40140
        # - Verticales (pared): TD=40061, EN_X=40106, EN_Y=40108
        layer_map = {
            # Instalaciones horizontales (techo)
            "FABRICA": "IS_CON_AIGUA_FAB",  # 40139
            "OBRA": "IS_AIG_CON_CLIMA_OBR",  # 40140
            # Instalaciones verticales (pared)
            "TD": "KN_AIGUA",  # 40061
            "EN_X": "KN_X_AIGUA",  # 40106 (Cara X)
            "EN_Y": "KN_Y_AIGUA",  # 40108 (Cara Y)
        }
        return layer_map

    def _get_layer_short_name_to_apply(self) -> str:
        """Obtiene el short_name del layer a aplicar según la configuración de la paleta"""
        try:
            # Obtener orientación (0=Horizontal, 1=Vertical)
            orientacion = self._safe_get_palette_property("TipoOrientacion", 0)

            layer_map = self._get_layer_mapping()

            if orientacion == 0:  # Horizontal (Techo)
                tipo_instalacion = self._safe_get_palette_property(
                    "TipoInstalacionHorizontal", "FABRICA"
                )
                short_name = layer_map.get(tipo_instalacion, layer_map["FABRICA"])
            else:  # Vertical (Pared)
                tipo_instalacion = self._safe_get_palette_property(
                    "TipoInstalacionVertical", "TD"
                )

                # Para EN, necesitamos considerar la cara (X o Y)
                if tipo_instalacion == "EN":
                    cara = self._safe_get_palette_property("CaraEN", "X")
                    if cara == "X":
                        short_name = layer_map["EN_X"]
                    else:  # cara == "Y"
                        short_name = layer_map["EN_Y"]
                else:  # TD
                    short_name = layer_map.get(tipo_instalacion, layer_map["TD"])

            return short_name
        except Exception as ex:
            print(f"[INT] Error obteniendo layer short_name: {ex}")
            # Retornar layer por defecto
            layer_map = self._get_layer_mapping()
            return layer_map.get("FABRICA", "IS_CON_AIGUA_FAB")

    def _get_layer_id_from_short_name(self, short_name: str, doc) -> int:
        """Obtiene el ID del layer desde su short_name usando LayerService"""
        try:
            if not short_name or not doc:
                return 0
            layer_id = LayerService.GetIDByShortName(short_name, doc)
            if layer_id > 0:
                return layer_id
            else:
                print(
                    f"[INT] Warning: No se encontró layer con short_name '{short_name}'"
                )
                return 0
        except Exception as ex:
            print(
                f"[INT] Error obteniendo layer ID desde short_name '{short_name}': {ex}"
            )
            return 0

    def _update_finalize_button_text(self, new_text: str) -> bool:
        """
        Actualiza el texto del botón cambiando el parámetro PreviewModeButtonText.
        0 = "Pasar a Edición de Layers", 1 = "Finalizar y crear"
        """
        try:
            if (
                not hasattr(self.script_object, "build_ele")
                or self.script_object.build_ele is None
            ):
                return False

            # Usar el parámetro oculto PreviewModeButtonText para controlar el texto mediante TextDyn
            button_state = 1 if new_text == "Finalizar y crear" else 0

            if hasattr(self.script_object.build_ele, "PreviewModeButtonText"):
                if hasattr(self.script_object.build_ele.PreviewModeButtonText, "value"):
                    self.script_object.build_ele.PreviewModeButtonText.value = (
                        button_state
                    )
                else:
                    self.script_object.build_ele.PreviewModeButtonText = button_state
                print(
                    f"[INT] Estado del botón actualizado a: {button_state} (texto: '{new_text}')"
                )
                return True
            else:
                print(
                    f"[INT] Parámetro PreviewModeButtonText no encontrado en build_ele"
                )
                return False
        except Exception as ex:
            print(f"[INT] Error actualizando texto del botón: {ex}")
            import traceback

            traceback.print_exc()
            return False

    def _calculate_layer_from_orientation(
        self, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D
    ) -> int:
        """
        Calcula el layer según la orientación del segmento (horizontal/vertical) y configuración de la paleta.
        Por ahora retorna un layer por defecto. Se puede mejorar después según tus layers específicos.
        """
        dx = p2.X - p1.X
        dy = p2.Y - p1.Y
        dz = p2.Z - p1.Z
        dz_abs = abs(dz)
        seg_len_xy = (dx * dx + dy * dy) ** 0.5

        is_horizontal = seg_len_xy > 1e-6 and dz_abs < 50.0
        is_vertical = dz_abs > 50.0 and seg_len_xy < 50.0

        # Por ahora usar layer por defecto - se puede mejorar después
        # TODO: Obtener configuración de la paleta y calcular layer según orientación
        if is_vertical:
            return 40061  # Layer vertical por defecto (ajustar según tus layers)
        else:
            return 40149  # Layer horizontal por defecto (ajustar según tus layers)

    def _generate_elements_for_preview(self):
        """
        Genera todos los elementos (tubos, codos) con fitting y los guarda
        en self.generated_elements para permitir la edición de layers antes de finalizar.
        """
        print("[SO] Generando elementos en EDICIÓN DE LAYERS...")
        self.generated_elements.clear()

        # Helper functions
        def _norm_preview(x, y, z):
            """Normaliza un vector 3D"""
            length = (x * x + y * y + z * z) ** 0.5
            if length < 1e-9:
                return (0.0, 0.0, 0.0)
            return (x / length, y / length, z / length)

        def _dot_preview(x1, y1, z1, x2, y2, z2):
            """Producto punto de dos vectores"""
            return x1 * x2 + y1 * y2 + z1 * z2

        try:
            if self.script_object.saved_paths:
                # Construir bifurcation_points al inicio para saber dónde hay T (2+ paths)
                # y no dibujar codo en esos vértices (se dibujará T).
                bifurcation_points = {}
                for path_idx, pts in enumerate(self.script_object.saved_paths):
                    if len(pts) < 2:
                        continue
                    for seg_idx in range(len(pts) - 1):
                        p1, p2 = pts[seg_idx], pts[seg_idx + 1]
                        p1_key = (round(p1.X, 0), round(p1.Y, 0), round(p1.Z, 0))
                        p2_key = (round(p2.X, 0), round(p2.Y, 0), round(p2.Z, 0))
                        if seg_idx > 0:
                            p_prev = pts[seg_idx - 1]
                            if p1_key not in bifurcation_points:
                                bifurcation_points[p1_key] = []
                            bifurcation_points[p1_key].append((path_idx, seg_idx, True))
                        else:
                            if p1_key not in bifurcation_points:
                                bifurcation_points[p1_key] = []
                            bifurcation_points[p1_key].append((path_idx, seg_idx, True))
                        if seg_idx < len(pts) - 2:
                            if p2_key not in bifurcation_points:
                                bifurcation_points[p2_key] = []
                            bifurcation_points[p2_key].append(
                                (path_idx, seg_idx, False)
                            )
                        else:
                            if p2_key not in bifurcation_points:
                                bifurcation_points[p2_key] = []
                            bifurcation_points[p2_key].append(
                                (path_idx, seg_idx, False)
                            )

                te_point_keys_preview = {
                    pk
                    for pk, conns in bifurcation_points.items()
                    if len(set(c[0] for c in conns)) >= 2
                }

                for path_idx, path in enumerate(self.script_object.saved_paths):
                    if len(path) >= 2:
                        # Generar tubos con fitting
                        for i in range(len(path) - 1):
                            p1, p2 = path[i], path[i + 1]

                            # Usar coordenadas como ID
                            element_key = ("tube", path_idx, i)

                            mid_point = AllplanGeo.Point3D(
                                (p1.X + p2.X) / 2, (p1.Y + p2.Y) / 2, (p1.Z + p2.Z) / 2
                            )

                            # Crear geometría de tubo (línea simple para preview)
                            tube_geom = AllplanGeo.Line3D(p1, p2)

                            # Determinar layer usando configuración de la paleta
                            layer = self._calculate_layer_from_orientation(p1, p2)

                            # Obtener diámetro del segmento
                            diameter = self.script_object._get_segment_diameter(
                                path_idx, i, default=20.0
                            )

                            self.generated_elements.append(
                                {
                                    "type": "tube",
                                    "key": element_key,
                                    "geometry": tube_geom,
                                    "position": mid_point,
                                    "layer": layer,
                                    "path_idx": path_idx,
                                    "seg_idx": i,
                                    "diameter": diameter,
                                    "p1": p1,
                                    "p2": p2,
                                }
                            )

                            print(
                                f"[SO] Tubo generado: path{path_idx}_seg{i} layer {layer} diam {diameter}mm"
                            )

                    # Generar codos en vértices intermedios
                    if len(path) >= 3:
                        for i in range(1, len(path) - 1):
                            p_prev, p_curr, p_next = path[i - 1], path[i], path[i + 1]

                            # Verificar si hay cambio de diámetro
                            d1 = self.script_object._get_segment_diameter(
                                path_idx, i - 1, default=20.0
                            )
                            d2 = self.script_object._get_segment_diameter(
                                path_idx, i, default=20.0
                            )

                            if abs(d1 - d2) > 1e-3:
                                print(
                                    f"[SO] Saltando codo en vértice {i} (hay cambio de diámetro D{d1:.0f}-D{d2:.0f})"
                                )
                                continue

                            # Verificar si los segmentos son colineales (rectos)
                            v1_vec = (
                                p_curr.X - p_prev.X,
                                p_curr.Y - p_prev.Y,
                                p_curr.Z - p_prev.Z,
                            )
                            v2_vec = (
                                p_next.X - p_curr.X,
                                p_next.Y - p_curr.Y,
                                p_next.Z - p_curr.Z,
                            )

                            v1_norm = _norm_preview(*v1_vec)
                            v2_norm = _norm_preview(*v2_vec)
                            dot_product = _dot_preview(*v1_norm, *v2_norm)

                            # Si son casi colineales, no hay codo
                            if abs(dot_product) >= 0.999:
                                print(
                                    f"[SO] Saltando codo en vértice {i} (segmentos colineales/rectos)"
                                )
                                continue

                            # Verificar si es giro de 90°
                            is_90 = self.script_object._is_90_deg_turn(
                                p_prev, p_curr, p_next
                            )
                            if not is_90:
                                print(
                                    f"[SO] Saltando codo en vértice {i} (no es giro de 90°)"
                                )
                                continue

                            # Si en este punto confluyen 2+ paths, es una T → no dibujar codo
                            pk_curr = (
                                round(p_curr.X, 0),
                                round(p_curr.Y, 0),
                                round(p_curr.Z, 0),
                            )
                            if pk_curr in te_point_keys_preview:
                                print(
                                    f"[SO] Saltando codo en vértice {i} (bifurcación T en este punto)"
                                )
                                continue

                            element_key = ("elbow", path_idx, i)

                            # Usar el segmento de entrada para determinar layer
                            layer = self._calculate_layer_from_orientation(
                                p_prev, p_curr
                            )

                            # Crear geometría de codo (cubo pequeño para preview)
                            try:
                                marker_size = 50.0  # mm
                                axis = AllplanGeo.AxisPlacement3D(
                                    AllplanGeo.Point3D(
                                        p_curr.X - marker_size / 2,
                                        p_curr.Y - marker_size / 2,
                                        p_curr.Z - marker_size / 2,
                                    )
                                )
                                elbow_geom = AllplanGeo.Polyhedron3D.CreateCuboid(
                                    axis, marker_size, marker_size, marker_size
                                )
                            except:
                                elbow_geom = AllplanGeo.Line3D(
                                    p_curr, p_curr
                                )  # Fallback

                            self.generated_elements.append(
                                {
                                    "type": "elbow",
                                    "key": element_key,
                                    "geometry": elbow_geom,
                                    "position": p_curr,
                                    "layer": layer,
                                    "path_idx": path_idx,
                                    "vertex_idx": i,
                                    "diameter": d1,
                                }
                            )

                            print(
                                f"[SO] Codo generado: path{path_idx}_vertex{i} layer {layer} diam {d1:.0f}mm"
                            )

                # ============================================================================
                # Generar Te's (bifurcaciones) — bifurcation_points ya construido al inicio
                # ============================================================================
                # Buscar puntos que conectan 2 o más polilíneas diferentes
                for point_key, connections in bifurcation_points.items():
                    unique_paths = set(conn[0] for conn in connections)
                    if len(unique_paths) >= 2:  # Bifurcación real (Te)
                        # Determinar tipo de Te según diámetros
                        has_20mm = False
                        has_25mm = False

                        # Helper: encontrar diámetro configurado para un segmento
                        def _find_diameter_for_segment_preview(
                            p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D
                        ) -> float:
                            """Encuentra el diámetro de un segmento"""
                            for seg in self.script_object.saved_segments:
                                pts = seg.get("points", [])
                                if len(pts) >= 2:
                                    # Comparar en ambas direcciones (p1->p2 y p2->p1)
                                    if (
                                        self._points_equal(pts[0], p1)
                                        and self._points_equal(pts[1], p2)
                                    ) or (
                                        self._points_equal(pts[0], p2)
                                        and self._points_equal(pts[1], p1)
                                    ):
                                        d = float(seg.get("diameter", 20.0) or 20.0)
                                        # Normalizar valores de diámetro
                                        if abs(d - 20.0) < 1e-3:
                                            return 20.0
                                        if abs(d - 25.0) < 1e-3:
                                            return 25.0
                                        return 20.0
                            return 20.0

                        for path_idx, seg_idx, is_start in connections:
                            pts = self.script_object.saved_paths[path_idx]
                            if seg_idx < len(pts) - 1:
                                p1, p2 = pts[seg_idx], pts[seg_idx + 1]
                                # Usar la misma función helper para detectar diámetros
                                diameter = _find_diameter_for_segment_preview(p1, p2)

                                if abs(diameter - 20.0) < 1e-3:
                                    has_20mm = True
                                elif abs(diameter - 25.0) < 1e-3:
                                    has_25mm = True

                        # Determinar tipo
                        if has_20mm and has_25mm:
                            te_type = "D20-D25"
                        elif has_20mm:
                            te_type = "D20-D20"
                        elif has_25mm:
                            te_type = "D25-D25"
                        else:
                            continue

                        # Crear elemento de Te
                        te_pos = AllplanGeo.Point3D(
                            point_key[0], point_key[1], point_key[2]
                        )
                        element_key = ("te", te_type, point_key)

                        # Crear geometría placeholder (cubo más grande)
                        try:
                            marker_size = 100.0  # mm - más grande que codos
                            axis = AllplanGeo.AxisPlacement3D(
                                AllplanGeo.Point3D(
                                    te_pos.X - marker_size / 2,
                                    te_pos.Y - marker_size / 2,
                                    te_pos.Z - marker_size / 2,
                                )
                            )
                            te_geom = AllplanGeo.Polyhedron3D.CreateCuboid(
                                axis, marker_size, marker_size, marker_size
                            )
                        except:
                            te_geom = AllplanGeo.Line3D(te_pos, te_pos)

                        # Determinar layer basándose en orientación del segmento principal
                        # Buscar el primer segmento conectado para determinar orientación
                        layer = 40149  # Default: IS_CON_SANE_OBR (horizontal obra)
                        for path_idx, seg_idx, is_start in connections:
                            pts = self.script_object.saved_paths[path_idx]
                            if seg_idx < len(pts) - 1:
                                p1, p2 = pts[seg_idx], pts[seg_idx + 1]
                                # Calcular orientación
                                dx = p2.X - p1.X
                                dy = p2.Y - p1.Y
                                dz = p2.Z - p1.Z
                                dz_abs = abs(dz)
                                seg_len_xy = (dx * dx + dy * dy) ** 0.5

                                is_vertical_seg = dz_abs > 50.0 and seg_len_xy < 50.0

                                if is_vertical_seg:
                                    # Segmento vertical - usar layer TD por defecto
                                    layer = 40061  # KN_AIGUA
                                else:
                                    # Segmento horizontal - usar layer OBRA por defecto
                                    layer = 40149  # IS_CON_SANE_OBR
                                break  # Usar el primer segmento para determinar orientación

                        self.generated_elements.append(
                            {
                                "type": "te",
                                "key": element_key,
                                "geometry": te_geom,
                                "position": te_pos,
                                "layer": layer,
                                "te_type": te_type,
                                "point_key": point_key,
                            }
                        )

                        print(
                            f"[SO] Te {te_type} generada en {point_key} layer {layer}"
                        )

                # ============================================================================
                # Generar Manguitos (en vértices rectos, igual que _finalize_and_create_now)
                # IMPORTANTE: Usar la misma lógica que _finalize_and_create_now
                # - NO debe ser giro de 90° (is_90 = False)
                # - Debe ser recto (straight = True)
                # - NO debe haber Te en ese vértice
                # - Se crea SIEMPRE si cumple las condiciones, incluso sin cambio de diámetro (20-20, 25-25)
                # ============================================================================

                # Construir mapa de vértices de Te (igual que en _finalize_and_create_now)
                def _key_from_point_preview(pt):
                    return (round(pt.X, 3), round(pt.Y, 3), round(pt.Z, 3))

                # Construir vertex_map para detectar Te's
                vertex_map_preview = {}
                for path_idx_preview, pts_preview in enumerate(
                    self.script_object.saved_paths
                ):
                    for seg_idx_preview in range(len(pts_preview) - 1):
                        p_start = pts_preview[seg_idx_preview]
                        p_end = pts_preview[seg_idx_preview + 1]
                        for is_start, pt, other in (
                            (True, p_start, p_end),
                            (False, p_end, p_start),
                        ):
                            key = _key_from_point_preview(pt)
                            vertex_map_preview.setdefault(key, []).append(
                                {
                                    "path_idx": path_idx_preview,
                                    "seg_idx": seg_idx_preview,
                                    "is_start": is_start,
                                    "pt": pt,
                                    "other": other,
                                }
                            )
                te_vertices_preview = set()
                for key, seg_list in vertex_map_preview.items():
                    if len(seg_list) == 3:
                        te_vertices_preview.add(key)

                # Helper: normalizar vector
                def _norm(x, y, z):
                    """Normaliza un vector 3D"""
                    length = (x * x + y * y + z * z) ** 0.5
                    if length < 1e-9:
                        return (0.0, 0.0, 0.0)
                    return (x / length, y / length, z / length)

                # Helper: producto punto
                def _dot(x1, y1, z1, x2, y2, z2):
                    """Producto punto de dos vectores"""
                    return x1 * x2 + y1 * y2 + z1 * z2

                for path_idx, path in enumerate(self.script_object.saved_paths):
                    if len(path) >= 3:
                        for vertex_idx in range(1, len(path) - 1):
                            p_prev, p_curr, p_next = (
                                path[vertex_idx - 1],
                                path[vertex_idx],
                                path[vertex_idx + 1],
                            )

                            # IMPORTANTE: Verificar que NO sea un giro de 90° (igual que _finalize_and_create_now)
                            is_90 = self.script_object._is_90_deg_turn(
                                p_prev, p_curr, p_next
                            )
                            if is_90:
                                # Es un codo, no un manguito
                                continue

                            # IMPORTANTE: Verificar que sea recto (straight)
                            # Usar la misma función que _finalize_and_create_now
                            straight = self.script_object._is_straight_turn(
                                p_prev, p_curr, p_next
                            )
                            if not straight:
                                continue

                            # IMPORTANTE: Verificar que NO haya Te en ese vértice (igual que _finalize_and_create_now)
                            key_curr = _key_from_point_preview(p_curr)
                            if key_curr in te_vertices_preview:
                                # Hay Te en ese vértice, no crear manguito
                                continue

                            # Obtener diámetros de los segmentos (usar _get_segment_diameter como en _finalize_and_create_now)
                            d1 = self.script_object._get_segment_diameter(
                                path_idx, vertex_idx - 1, default=20.0
                            )
                            d2 = self.script_object._get_segment_diameter(
                                path_idx, vertex_idx, default=20.0
                            )

                            # Normalizar diámetros a enteros (igual que _finalize_and_create_now)
                            di1 = int(round(float(d1)))
                            di2 = int(round(float(d2)))

                            # Crear SIEMPRE el manguito si es recto (igual que _finalize_and_create_now)
                            # Incluye 20-20, 25-25, 20-25, 25-20
                            element_key = ("manguito", path_idx, vertex_idx)

                            # Determinar tipo de manguito
                            manguito_type = f"D{di1}-D{di2}"

                            # Crear geometría placeholder (cubo distintivo)
                            try:
                                marker_size = (
                                    75.0  # mm - tamaño medio entre codos y Te's
                                )
                                axis = AllplanGeo.AxisPlacement3D(
                                    AllplanGeo.Point3D(
                                        p_curr.X - marker_size / 2,
                                        p_curr.Y - marker_size / 2,
                                        p_curr.Z - marker_size / 2,
                                    )
                                )
                                manguito_geom = AllplanGeo.Polyhedron3D.CreateCuboid(
                                    axis, marker_size, marker_size, marker_size
                                )
                            except:
                                manguito_geom = AllplanGeo.Line3D(p_curr, p_curr)

                            # Determinar layer usando configuración de la paleta
                            # Usar el segmento de entrada
                            layer = self._calculate_layer_from_orientation(
                                p_prev, p_curr
                            )

                            self.generated_elements.append(
                                {
                                    "type": "manguito",
                                    "key": element_key,
                                    "geometry": manguito_geom,
                                    "position": p_curr,
                                    "layer": layer,
                                    "path_idx": path_idx,
                                    "vertex_idx": vertex_idx,
                                    "manguito_type": manguito_type,
                                    "diameter_in": float(d1),
                                    "diameter_out": float(d2),
                                }
                            )

                            print(
                                f"[SO] Manguito {manguito_type} generado: path{path_idx}_vertex{vertex_idx} layer {layer}"
                            )

        except Exception as ex:
            print(f"[SO] Error generando elementos preview: {ex}")
            import traceback

            traceback.print_exc()

        # Inicializar attribute_overrides SOLO desde atributos por-segmento ya existentes,
        # sin propagar automáticamente el valor global de NomIS a todos los elementos.
        # Así, cada elemento puede conservar/definir su propio valor.
        so = self.script_object
        for element in self.generated_elements:
            key = element.get("key")
            if key is None or key in self.attribute_overrides:
                continue

            path_idx = element.get("path_idx")
            seg_idx = None

            if element.get("type") == "tube":
                seg_idx = element.get("seg_idx")
            elif element.get("type") in ("elbow", "manguito"):
                vertex_idx = element.get("vertex_idx")
                if vertex_idx is not None and vertex_idx > 0:
                    seg_idx = vertex_idx - 1

            nomis = ""
            if (
                path_idx is not None
                and seg_idx is not None
                and hasattr(so, "_get_segment_nomis")
            ):
                # Usar solo el valor almacenado por segmento (custom_attributes).
                # Si no hay nada definido para ese segmento, no se asigna nada por defecto aquí.
                nomis = so._get_segment_nomis(path_idx, seg_idx, default="")

            if nomis:
                self.attribute_overrides[key] = nomis

        print(f"[SO] Total de elementos generados: {len(self.generated_elements)}")

        # Forzar redibujado
        if hasattr(self, "coord_input") and self.coord_input:
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )

    def _find_clicked_element(
        self,
        click_point: AllplanGeo.Point3D,
        pnt_2d=None,
        view_proj=None,
    ):
        """
        Encuentra el elemento generado más cercano al punto de click.
        Si se pasan pnt_2d y view_proj, usa distancia en espacio 2D de vista
        (permite seleccionar en vistas isométricas/ortogonales).
        Retorna el diccionario del elemento o None.
        """
        use_2d = (
            pnt_2d is not None
            and view_proj is not None
            and hasattr(pnt_2d, "X")
            and hasattr(pnt_2d, "Y")
        )
        if use_2d:
            try:
                max_d2_view = HIT_TOL_VIEW * HIT_TOL_VIEW
                closest_element = None
                best_d2 = max_d2_view + 1.0
                cx, cy = float(pnt_2d.X), float(pnt_2d.Y)
                for element in self.generated_elements:
                    pos = element.get("position")
                    if pos:
                        p_v = view_proj.WorldToView(pos)
                        dx = cx - p_v.X
                        dy = cy - p_v.Y
                        d2 = dx * dx + dy * dy
                        if d2 <= max_d2_view and d2 < best_d2:
                            best_d2 = d2
                            closest_element = element
                if closest_element:
                    element_key = closest_element["key"]
                    print(
                        f"[SO] Elemento clickeado (2D vista): {closest_element['type']} (key: {element_key})"
                    )
                return closest_element
            except Exception:
                use_2d = False

        if not use_2d:
            min_dist = HIT_TOL_VERTEX
            closest_element = None
            for element in self.generated_elements:
                pos = element.get("position")
                if pos:
                    dist = (
                        (click_point.X - pos.X) ** 2
                        + (click_point.Y - pos.Y) ** 2
                        + (click_point.Z - pos.Z) ** 2
                    ) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_element = element
            if closest_element:
                element_key = closest_element["key"]
                print(
                    f"[SO] Elemento clickeado: {closest_element['type']} (key: {element_key}) a {min_dist:.1f}mm"
                )
            return closest_element
        return None

    def _on_element_clicked(self, element):
        """
        Maneja el click en un elemento: resalta el elemento y permite cambiar layer.
        """
        element_key = element["key"]
        element_type = element["type"]
        current_layer = self.layer_overrides.get(element_key, element["layer"])

        print(
            f"[SO] Elemento seleccionado: {element_type} - Layer actual: {current_layer}"
        )

        # Resaltar el elemento seleccionado
        self.selected_element_id = element_key
        self._highlight_element(element)

        # Solicitar nuevo layer al usuario mediante la paleta
        self._request_layer_change(element)

    def _highlight_element(self, element):
        """
        Resalta visualmente el elemento seleccionado.
        """
        pos = element.get("position")
        if pos:
            try:
                size = HANDLE_SIZE * HOVER_SCALE
                half = size / 2

                # Crear un cubo simple alrededor del punto
                axis = AllplanGeo.AxisPlacement3D(
                    AllplanGeo.Point3D(pos.X - half, pos.Y - half, pos.Z - half)
                )
                self.highlight_geometry = AllplanGeo.Polyhedron3D.CreateCuboid(
                    axis, size, size, size
                )
                print(
                    f"[SO] Elemento resaltado en ({pos.X:.1f}, {pos.Y:.1f}, {pos.Z:.1f})"
                )
            except Exception as e:
                print(f"[SO] Error creando geometría de highlight: {e}")
                # Fallback: usar una línea vertical como marcador
                try:
                    marker_height = HANDLE_SIZE * 2
                    p1 = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z - marker_height / 2)
                    p2 = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z + marker_height / 2)
                    self.highlight_geometry = AllplanGeo.Line3D(p1, p2)
                    print(f"[SO] Usando marcador de línea para highlight")
                except Exception as e2:
                    print(f"[SO] Error creando marcador de línea: {e2}")
                    self.highlight_geometry = None

        # Forzar redibujado
        if hasattr(self, "coord_input") and self.coord_input:
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )

    def _request_layer_change(self, element):
        """
        Solicita al usuario un nuevo número de layer para el elemento.
        Por ahora usa un prompt simple en la paleta.
        """
        element_key = element["key"]
        element_type = element["type"]
        current_layer = self.layer_overrides.get(element_key, element["layer"])

        # Mostrar mensaje en la paleta
        tipo_texto = {
            "tube": "TUBO",
            "elbow": "CODO",
            "manguito": "MANGUITO",
            "te": "TE",
        }.get(element_type, element_type.upper())

        mensaje = f"Seleccionado: {tipo_texto} (Layer: {current_layer})"
        self._safe_set_palette_property("FirstText", mensaje)

        # TODO: Implementar input de layer mediante diálogo o campo de paleta
        # Por ahora, solo muestra el mensaje
        print(f"[SO] Use la paleta para cambiar el layer del {tipo_texto}")

    def apply_layers_to_selected(self):
        """
        Aplica el layer seleccionado en la paleta a los segmentos seleccionados.
        En modo PREVIEW (edición de layers), aplica layers a elementos generados.
        En modo NORMAL, aplica layers a segmentos guardados.
        """
        try:
            # ============================================================================
            # MODO EDICIÓN DE LAYERS (PREVIEW MODE)
            # ============================================================================
            if self.preview_mode:
                print(
                    "[INT] EDICIÓN DE LAYERS activo: aplicando layers a elementos generados"
                )

                if not self.selected_element_id:
                    print(
                        "[INT] ⚠ No hay ningún elemento seleccionado en EDICIÓN DE LAYERS"
                    )
                    print("[INT] AYUDA: Haz clic en un tubo o codo para seleccionarlo")
                    return False

                # Obtener el documento
                try:
                    doc = self.coord_input.GetInputViewDocument()
                except Exception:
                    print("[INT] Error: No se pudo obtener el documento")
                    return False

                # Obtener el short_name del layer a aplicar
                short_name = self._get_layer_short_name_to_apply()
                if not short_name:
                    print("[INT] Error: short_name de layer inválido")
                    return False

                # Obtener el ID del layer desde el short_name
                layer_id = self._get_layer_id_from_short_name(short_name, doc)
                if layer_id <= 0:
                    print(
                        f"[INT] Error: No se pudo obtener el ID del layer '{short_name}'"
                    )
                    return False

                # Buscar el elemento seleccionado
                selected_element = None
                for element in self.generated_elements:
                    if element.get("key") == self.selected_element_id:
                        selected_element = element
                        break

                if not selected_element:
                    print(
                        f"[INT] ⚠ No se encontró el elemento {self.selected_element_id} en generated_elements"
                    )
                    return False

                # Aplicar el layer override
                old_layer = selected_element.get("layer", "N/A")
                self.layer_overrides[self.selected_element_id] = layer_id

                tipo_texto = {
                    "tube": "TUBO",
                    "elbow": "CODO",
                    "manguito": "MANGUITO",
                    "te": "TE",
                }.get(selected_element["type"], selected_element["type"].upper())

                print(f"[INT] ✓ {tipo_texto} actualizado:")
                print(f"[INT]   Layer: {old_layer} → {layer_id} ({short_name})")

                # Actualizar visualización
                if hasattr(self, "coord_input") and self.coord_input:
                    self._draw_preview(
                        self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    )

                return True

            # ============================================================================
            # MODO NORMAL: Aplicar layers a segmentos guardados
            # ============================================================================
            print("[INT] Modo NORMAL: aplicando layers a segmentos guardados")

            # Obtener el documento
            try:
                doc = self.coord_input.GetInputViewDocument()
            except Exception:
                print("[INT] Error: No se pudo obtener el documento")
                return False

            # Obtener el short_name del layer a aplicar
            short_name = self._get_layer_short_name_to_apply()
            if not short_name:
                print("[INT] Error: short_name de layer inválido")
                return False

            # Obtener el ID del layer desde el short_name
            layer_id = self._get_layer_id_from_short_name(short_name, doc)
            if layer_id <= 0:
                print(f"[INT] Error: No se pudo obtener el ID del layer '{short_name}'")
                return False

            applied_count = 0

            # Aplicar a segmentos seleccionados por marco
            if self.selected_segments:
                for kind, path_idx, seg_idx in self.selected_segments:
                    if kind == "saved":
                        if self._apply_layer_to_segment(
                            path_idx, seg_idx, short_name, layer_id
                        ):
                            applied_count += 1

            # Si no hay selección por marco, aplicar al segmento hover/seleccionado
            elif self.selected_seg or self.hover_seg:
                target = self.selected_seg or self.hover_seg
                kind, path_idx, seg_idx = target
                if kind == "saved":
                    if self._apply_layer_to_segment(
                        path_idx, seg_idx, short_name, layer_id
                    ):
                        applied_count += 1

            if applied_count > 0:
                print(
                    f"[INT] Aplicado layer '{short_name}' (ID: {layer_id}) a {applied_count} segmento(s)"
                )
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
                return True
            else:
                print("[INT] No hay segmentos seleccionados para aplicar layer")
                print("[INT] AYUDA: Para seleccionar segmentos:")
                print("[INT] - Haz clic en un segmento de polilínea guardada")
                print("[INT] - O arrastra para crear un marco de selección")
                return False

        except Exception as ex:
            print(f"[INT] Error aplicando layer: {ex}")
            return False

    def _apply_layer_to_segment(
        self, path_idx: int, seg_idx: int, layer_short_name: str, layer_id: int
    ) -> bool:
        """Aplica un layer específico a un segmento guardado usando short_name e ID"""
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return False

            # Obtener los puntos del segmento actual
            point1 = pts[seg_idx]
            point2 = pts[seg_idx + 1]

            # Buscar si ya existe una configuración para este segmento
            segment_found = False
            for i, existing_segment in enumerate(self.script_object.saved_segments):
                existing_points = existing_segment["points"]
                if (
                    len(existing_points) >= 2
                    and self._points_equal(existing_points[0], point1)
                    and self._points_equal(existing_points[1], point2)
                ):
                    # Actualizar el segmento existente con el layer (guardamos short_name e ID)
                    existing_segment = self.script_object.saved_segments[i]
                    existing_segment["layer_short_name"] = layer_short_name
                    existing_segment["layer_id"] = layer_id
                    segment_found = True
                    print(
                        f"[INT] Segmento {path_idx}-{seg_idx} actualizado con layer '{layer_short_name}' (ID: {layer_id})"
                    )
                    break

            # Si no se encontró, agregar como nuevo (con valores por defecto)
            if not segment_found:
                # Obtener diámetro por defecto si no existe
                diameter = self._get_diameter_to_apply()
                system = self._get_current_system()
                label = self._format_segment_label(diameter, system)
                dist_type = self._get_distribution_type_to_apply() or "IS"

                segment_info = {
                    "points": [point1, point2],
                    "diameter": diameter,
                    "section_type": f"{diameter}mm",
                    "system": system,
                    "label": label,
                    "path_idx": path_idx,
                    "seg_idx": seg_idx,
                    "layer_short_name": layer_short_name,
                    "layer_id": layer_id,
                    "distribution_type": dist_type,
                }
                self.script_object.saved_segments.append(segment_info)
                print(
                    f"[INT] Segmento {path_idx}-{seg_idx} configurado con layer '{layer_short_name}' (ID: {layer_id})"
                )

            # Forzar redibujado para actualizar
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )

            return True

        except Exception as ex:
            print(f"[INT] Error aplicando layer a segmento: {ex}")
            return False

    def apply_distribution_to_selected(self):
        """
        Aplica el tipo de distribución seleccionado en la paleta a los elementos seleccionados.
        En modo PREVIEW (edición de layers), aplica distribución a elementos generados.
        En modo NORMAL, aplica distribución a segmentos guardados.
        """
        try:
            # Obtener el tipo de distribución a aplicar
            distribution_type = self._get_distribution_type_to_apply()
            if not distribution_type:
                print(
                    "[INT] Error: Debe seleccionar un tipo de distribución (TD o IS) en la paleta"
                )
                self._safe_set_palette_property(
                    "FirstText",
                    "⚠ Debe seleccionar un tipo de distribución (TD o IS) en la paleta",
                )
                return False

            # Obtener tipo de tubo y tipo de agua para logs de debug
            tube_type = self._get_tube_type_to_apply(distribution_type)
            water_type = self._get_water_type_to_apply(distribution_type)

            print(f"[INT] ===== APLICANDO CONFIGURACIÓN =====")
            print(f"[INT] Distribución: '{distribution_type}'")
            print(f"[INT] Tipo de Tubo: '{tube_type}'")
            print(f"[INT] Tipo de Agua: '{water_type}'")
            print(f"[INT] =====================================")

            applied_count = 0

            # ============================================================================
            # MODO EDICIÓN DE LAYERS (PREVIEW MODE)
            # ============================================================================
            if self.preview_mode:
                print(
                    "[INT] EDICIÓN DE LAYERS activo: aplicando distribución a elementos generados"
                )

                if not self.selected_element_id:
                    print(
                        "[INT] ⚠ No hay ningún elemento seleccionado en EDICIÓN DE LAYERS"
                    )
                    print(
                        "[INT] AYUDA: Haz clic en un tubo, codo, manguito o Te para seleccionarlo"
                    )
                    self._safe_set_palette_property(
                        "FirstText", "⚠ Seleccione un elemento primero"
                    )
                    return False

                # Buscar el elemento seleccionado en generated_elements
                selected_element = None
                for element in self.generated_elements:
                    if element.get("key") == self.selected_element_id:
                        selected_element = element
                        break

                if not selected_element:
                    print(
                        f"[INT] ⚠ Elemento con key {self.selected_element_id} no encontrado"
                    )
                    return False

                element_key = selected_element.get("key")
                element_type = element_key[0] if element_key else "unknown"

                # Almacenar la distribución en distribution_overrides
                self.distribution_overrides[element_key] = distribution_type
                applied_count = 1

                tipo_texto = {
                    "tube": "TUBO",
                    "elbow": "CODO",
                    "manguito": "MANGUITO",
                    "te": "TE",
                }.get(element_type, element_type.upper())

                print(
                    f"[INT] ✓ Distribución '{distribution_type}' aplicada a {tipo_texto}"
                )
                print(f"[INT]   Tipo de Tubo: '{tube_type}'")
                print(f"[INT]   Tipo de Agua: '{water_type}'")
                print(
                    f"[INT] La distribución se aplicará al crear los elementos finales"
                )

                # Si la distribución es TD, aplicar automáticamente el atributo pmp_pare
                # (no se aplica 6_CC_IS porque TD no usa ese atributo)
                if distribution_type == "TD":
                    # Obtener el valor del campo NomIS de la paleta
                    valor_atributos = self._safe_get_palette_property("NomIS", "")
                    if valor_atributos and valor_atributos.strip():
                        # Almacenar el atributo en attribute_overrides
                        # La función _set_6_cc_is_y_pmp_pare_en_elemento ya maneja
                        # que para TD solo se aplique pmp_pare
                        self.attribute_overrides[element_key] = valor_atributos.strip()
                        print(
                            f"[INT] ✓ Atributo pmp_pare aplicado automáticamente a {tipo_texto} (distribución TD)"
                        )
                        self._safe_set_palette_property(
                            "FirstText",
                            f"✓ Distribución {distribution_type} y atributo pmp_pare aplicados a {tipo_texto}",
                        )
                    else:
                        self._safe_set_palette_property(
                            "FirstText",
                            f"✓ Distribución {distribution_type} aplicada a {tipo_texto}",
                        )
                else:
                    self._safe_set_palette_property(
                        "FirstText",
                        f"✓ Distribución {distribution_type} aplicada a {tipo_texto}",
                    )

                # Redibujar para actualizar
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
                return True

            # ============================================================================
            # MODO NORMAL (segmentos guardados)
            # ============================================================================
            else:
                print("[INT] MODO NORMAL: aplicando distribución a segmentos guardados")

                # Aplicar a segmentos seleccionados por marco
                if self.selected_segments:
                    for kind, path_idx, seg_idx in self.selected_segments:
                        if kind == "saved":
                            if self._apply_distribution_to_segment(
                                path_idx, seg_idx, distribution_type
                            ):
                                applied_count += 1

                # Si no hay selección por marco, aplicar al segmento hover/seleccionado
                elif self.selected_seg or self.hover_seg:
                    target = self.selected_seg or self.hover_seg
                    kind, path_idx, seg_idx = target
                    if kind == "saved":
                        if self._apply_distribution_to_segment(
                            path_idx, seg_idx, distribution_type
                        ):
                            applied_count += 1

                if applied_count > 0:
                    print(f"[INT] ✓ Aplicado a {applied_count} segmento(s):")
                    print(f"[INT]   Distribución: '{distribution_type}'")
                    print(f"[INT]   Tipo de Tubo: '{tube_type}'")
                    print(f"[INT]   Tipo de Agua: '{water_type}'")
                    self._draw_preview(
                        self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    )
                    return True
                else:
                    print(
                        "[INT] No hay segmentos seleccionados para aplicar distribución"
                    )
                    print("[INT] AYUDA: Para seleccionar segmentos:")
                    print("[INT] - Haz clic en un segmento de polilínea guardada")
                    print("[INT] - O arrastra para crear un marco de selección")
                    return False

        except Exception as ex:
            print(f"[INT] Error aplicando distribución: {ex}")
            return False

    def _get_distribution_type_to_apply(self):
        """
        Obtiene el tipo de distribución a aplicar según la configuración de la paleta.
        Devuelve 'TD' o 'IS' solo si está explícitamente configurado.
        Devuelve None si no se ha asignado tipo de distribución (obligatorio elegir TD o IS).
        """
        try:
            distribution_type = self._safe_get_palette_property(
                "TipoDeDistribucion", None
            )
            if distribution_type in ["TD", "IS"]:
                return distribution_type.strip()
            return None
        except Exception as ex:
            print(f"[INT] Error obteniendo tipo de distribución: {ex}")
            return None

    def _require_distribution_for_new_segments(self):
        """
        Comprueba que haya un tipo de distribución (TD o IS) configurado antes de crear
        segmentos. Si no hay, muestra mensaje al usuario y devuelve None.
        Devuelve el tipo de distribución si es válido.
        """
        dist = self._get_distribution_type_to_apply()
        if dist in ["TD", "IS"]:
            return dist
        msg = (
            "Debe seleccionar un tipo de distribución (TD o IS) en la paleta antes de "
            "crear o guardar una polilínea."
        )
        print(f"[INT] {msg}")
        self._safe_set_palette_property("FirstText", f"⚠ {msg}")
        try:
            PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
        except Exception:
            pass
        return None

    def _get_tube_type_to_apply(self, distribution_type: str) -> str:
        """Obtiene el tipo de tubo a aplicar según la distribución"""
        try:
            if distribution_type == "TD":
                tube_type = self._safe_get_palette_property("TipoDeTuboTD", "Polietilè")
            else:  # IS
                tube_type = self._safe_get_palette_property("TipoDeTuboIS", "Polietilè")

            if isinstance(tube_type, str):
                return tube_type.strip()
            return str(tube_type) if tube_type else "Polietilè"
        except Exception as ex:
            print(f"[INT] Error obteniendo tipo de tubo: {ex}")
            return "Polietilè"

    def _get_water_type_to_apply(self, distribution_type: str = None) -> str:
        """
        Obtiene el tipo de agua a aplicar según la configuración de la paleta.
        Lee desde TipoDeAguaTD o TipoDeAguaIS según la distribución.
        """
        try:
            # Si no se proporciona distribution_type, intentar obtenerlo
            if distribution_type is None:
                distribution_type = self._get_distribution_type_to_apply()

            # Leer el control correcto según la distribución
            if distribution_type == "TD":
                water_type = self._safe_get_palette_property("TipoDeAguaTD", "Fred")
            else:  # IS
                water_type = self._safe_get_palette_property("TipoDeAguaIS", "Fred")

            # Normalizar el valor
            if isinstance(water_type, str):
                water_type = water_type.strip()
            else:
                water_type = str(water_type) if water_type else "Fred"

            print(
                f"[DBG] _get_water_type_to_apply: dist={distribution_type}, leído='{water_type}'"
            )

            # Validar que el valor sea válido según la distribución
            if distribution_type == "TD":
                # TD solo permite Fred o Calent
                if water_type not in ["Fred", "Calent"]:
                    print(
                        f"[INT] Warning: Tipo de agua '{water_type}' no válido para TD, usando 'Fred' por defecto"
                    )
                    water_type = "Fred"
            else:  # IS
                # IS permite: Fred, Calent, Retorn, MC fred, MC calent
                valid_is_types = ["Fred", "Calent", "Retorn", "MC fred", "MC calent"]
                if water_type not in valid_is_types:
                    print(
                        f"[INT] Warning: Tipo de agua '{water_type}' no válido para IS, usando 'Fred' por defecto"
                    )
                    water_type = "Fred"

            return water_type
        except Exception as ex:
            print(f"[INT] Error obteniendo tipo de agua: {ex}")
            return "Fred"

    def _apply_distribution_to_segment(
        self, path_idx: int, seg_idx: int, distribution_type: str
    ) -> bool:
        """Aplica un tipo de distribución específico a un segmento guardado"""
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return False

            # Obtener los puntos del segmento actual
            point1 = pts[seg_idx]
            point2 = pts[seg_idx + 1]

            # Buscar si ya existe una configuración para este segmento
            segment_found = False
            for i, existing_segment in enumerate(self.script_object.saved_segments):
                existing_points = existing_segment["points"]
                if (
                    len(existing_points) >= 2
                    and self._points_equal(existing_points[0], point1)
                    and self._points_equal(existing_points[1], point2)
                ):
                    # Actualizar el segmento existente con el tipo de distribución
                    existing_segment = self.script_object.saved_segments[i]
                    existing_segment["distribution_type"] = distribution_type
                    segment_found = True

                    # Obtener tipo de tubo y agua para el log
                    tube_type = self._get_tube_type_to_apply(distribution_type)
                    water_type = self._get_water_type_to_apply(distribution_type)

                    print(f"[INT] Segmento {path_idx}-{seg_idx} actualizado:")
                    print(f"[INT]   Distribución: '{distribution_type}'")
                    print(f"[INT]   Tipo de Tubo: '{tube_type}'")
                    print(f"[INT]   Tipo de Agua: '{water_type}'")
                    break

            # Si no se encontró, agregar como nuevo (con valores por defecto)
            if not segment_found:
                # Obtener diámetro por defecto si no existe
                diameter = self._get_diameter_to_apply()
                system = self._get_current_system()
                label = self._format_segment_label(diameter, system)

                segment_info = {
                    "points": [point1, point2],
                    "diameter": diameter,
                    "section_type": f"{diameter}mm",
                    "system": system,
                    "label": label,
                    "path_idx": path_idx,
                    "seg_idx": seg_idx,
                    "distribution_type": distribution_type,
                }
                self.script_object.saved_segments.append(segment_info)

                # Obtener tipo de tubo y agua para el log
                tube_type = self._get_tube_type_to_apply(distribution_type)
                water_type = self._get_water_type_to_apply(distribution_type)

                print(f"[INT] Segmento {path_idx}-{seg_idx} configurado (nuevo):")
                print(f"[INT]   Distribución: '{distribution_type}'")
                print(f"[INT]   Tipo de Tubo: '{tube_type}'")
                print(f"[INT]   Tipo de Agua: '{water_type}'")

            # Forzar redibujado para actualizar
            self._draw_preview(
                self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            )

            return True

        except Exception as ex:
            print(f"[INT] Error aplicando distribución a segmento: {ex}")
            return False

    def apply_attributes_to_selected(self):
        """
        Aplica Atributos Padre (6_CC_IS / pmp_pare) a los elementos seleccionados
        con el valor ingresado en el campo NomIS de la paleta.

        En modo PREVIEW (edición de layers), aplica atributos a elementos generados.
        En modo NORMAL, aplica atributos a segmentos guardados.
        """
        try:
            # Obtener el valor del campo NomIS de la paleta
            valor_atributos = self._safe_get_palette_property("NomIS", "")

            if not valor_atributos or valor_atributos.strip() == "":
                print(
                    "[INT] Error: Debe ingresar un valor para los atributos en el campo 'Nombre instalación'"
                )
                self._safe_set_palette_property(
                    "FirstText", "⚠ Ingrese un valor para el atributo"
                )
                return False

            valor_atributos = valor_atributos.strip()
            applied_count = 0

            # ============================================================================
            # MODO EDICIÓN DE LAYERS (PREVIEW MODE)
            # ============================================================================
            if self.preview_mode:
                print(
                    "[INT] EDICIÓN DE LAYERS activo: aplicando atributos a elementos generados"
                )

                if not self.selected_element_id:
                    print(
                        "[INT] ⚠ No hay ningún elemento seleccionado en EDICIÓN DE LAYERS"
                    )
                    print(
                        "[INT] AYUDA: Haz clic en un tubo, codo, manguito o Te para seleccionarlo"
                    )
                    self._safe_set_palette_property(
                        "FirstText", "⚠ Seleccione un elemento primero"
                    )
                    return False

                # Buscar el elemento seleccionado en generated_elements
                selected_element = None
                for element in self.generated_elements:
                    if element.get("key") == self.selected_element_id:
                        selected_element = element
                        break

                if not selected_element:
                    print(
                        f"[INT] ⚠ Elemento con key {self.selected_element_id} no encontrado"
                    )
                    return False

                element_key = selected_element.get("key")
                element_type = element_key[0] if element_key else "unknown"

                # Almacenar el atributo en attribute_overrides
                self.attribute_overrides[element_key] = valor_atributos
                applied_count = 1

                tipo_texto = {
                    "tube": "TUBO",
                    "elbow": "CODO",
                    "manguito": "MANGUITO",
                    "te": "TE",
                }.get(element_type, element_type.upper())

                print(f"[INT] ✓ Atributo '{valor_atributos}' aplicado a {tipo_texto}")
                print(
                    f"[INT] Los atributos se asignarán a '6_CC_IS' y 'pmp_pare' al crear los elementos"
                )
                self._safe_set_palette_property(
                    "FirstText", f"✓ Atributo aplicado a {tipo_texto}"
                )

                # Redibujar para actualizar
                self._draw_preview(
                    self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                )
                return True

            # ============================================================================
            # MODO NORMAL (segmentos guardados)
            # ============================================================================
            else:
                print("[INT] MODO NORMAL: aplicando atributos a segmentos guardados")

                # Aplicar a segmentos seleccionados por marco
                if self.selected_segments:
                    for kind, path_idx, seg_idx in self.selected_segments:
                        if kind == "saved":
                            if self._apply_attributes_to_segment(
                                path_idx, seg_idx, valor_atributos
                            ):
                                applied_count += 1

                # Si no hay selección por marco, aplicar al segmento hover/seleccionado
                elif self.selected_seg or self.hover_seg:
                    target = self.selected_seg or self.hover_seg
                    kind, path_idx, seg_idx = target
                    if kind == "saved":
                        if self._apply_attributes_to_segment(
                            path_idx, seg_idx, valor_atributos
                        ):
                            applied_count += 1

                if applied_count > 0:
                    print(
                        f"[INT] ✓ Atributo '{valor_atributos}' aplicado a {applied_count} segmento(s)"
                    )
                    print(
                        f"[INT] Los atributos se asignarán a '6_CC_IS' y 'pmp_pare' al crear los elementos"
                    )
                    self._safe_set_palette_property(
                        "FirstText",
                        f"✓ Atributo aplicado a {applied_count} segmento(s)",
                    )
                    self._draw_preview(
                        self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
                    )
                    return True
                else:
                    print("[INT] No hay segmentos seleccionados para aplicar atributos")
                    print("[INT] AYUDA: Para seleccionar segmentos:")
                    print("[INT] - Haz clic en un segmento de polilínea guardada")
                    print("[INT] - O arrastra para crear un marco de selección")
                    self._safe_set_palette_property(
                        "FirstText", "⚠ No hay segmentos seleccionados"
                    )
                    return False

        except Exception as ex:
            print(f"[INT] Error aplicando atributos: {ex}")
            import traceback

            traceback.print_exc()
            return False

    def _apply_attributes_to_segment(
        self, path_idx: int, seg_idx: int, valor_atributos: str
    ) -> bool:
        """
        Aplica los Atributos Padre a un segmento específico.

        Args:
            path_idx: índice de la polilínea
            seg_idx: índice del segmento
            valor_atributos: valor a asignar al atributo
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return False

            # Obtener los puntos del segmento actual
            point1 = pts[seg_idx]
            point2 = pts[seg_idx + 1]

            # Buscar si ya existe una configuración para este segmento
            segment_found = False
            for i, existing_segment in enumerate(self.script_object.saved_segments):
                existing_points = existing_segment.get("points", [])
                if (
                    len(existing_points) >= 2
                    and self._points_equal(existing_points[0], point1)
                    and self._points_equal(existing_points[1], point2)
                ):
                    # Actualizar el segmento existente con el nuevo valor de atributo
                    if "custom_attributes" not in self.script_object.saved_segments[i]:
                        self.script_object.saved_segments[i]["custom_attributes"] = {}

                    # Agregar el nuevo atributo con timestamp para mantener el orden
                    import time

                    attr_key = f"attr_{int(time.time() * 1000000)}"  # Clave única con timestamp
                    self.script_object.saved_segments[i]["custom_attributes"][
                        attr_key
                    ] = valor_atributos

                    segment_found = True
                    print(
                        f"[INT] Segmento {path_idx}-{seg_idx} actualizado con atributo: '{valor_atributos}'"
                    )
                    break

            # Si no se encontró, crear una entrada nueva con los atributos
            if not segment_found:
                # Obtener valores por defecto para otros campos
                diameter = self._safe_get_palette_property("DiametroAplicarFecal", 20)
                system = self._get_current_system()
                label = self._format_segment_label(diameter, system)
                dist_type = self._get_distribution_type_to_apply() or "IS"

                import time

                attr_key = f"attr_{int(time.time() * 1000000)}"
                # Obtener valores de instalación (usar valores por defecto si no existen los métodos)
                try:
                    installation_type_horizontal = (
                        self._get_installation_type_horizontal()
                    )
                except AttributeError:
                    installation_type_horizontal = "OBRA"  # Valor por defecto

                try:
                    installation_type_vertical = self._get_installation_type_vertical()
                except AttributeError:
                    installation_type_vertical = "IS"  # Valor por defecto

                try:
                    face = self._get_face_en()
                except AttributeError:
                    face = "Y"  # Valor por defecto

                segment_info = {
                    "points": [point1, point2],
                    "diameter": diameter,
                    "section_type": f"{diameter}mm",
                    "system": system,
                    "label": label,
                    "path_idx": path_idx,
                    "seg_idx": seg_idx,
                    "installation_type_horizontal": installation_type_horizontal,
                    "installation_type_vertical": installation_type_vertical,
                    "face": face,
                    "custom_attributes": {attr_key: valor_atributos},
                    "distribution_type": dist_type,
                }
                self.script_object.saved_segments.append(segment_info)
                print(
                    f"[INT] Segmento {path_idx}-{seg_idx} creado con atributo: '{valor_atributos}'"
                )

            return True

        except Exception as ex:
            print(f"[INT] Error aplicando atributos a segmento: {ex}")
            import traceback

            traceback.print_exc()
            return False

    def show_sections_info(self):
        """Muestra información de las secciones configuradas"""
        try:
            print("[INT] === INFORMACIÓN DE SECCIONES ===")

            # Información general
            total_paths = len(self.script_object.saved_paths)
            total_segments_with_section = len(self.script_object.saved_segments)

            print(f"[INT] Polilíneas guardadas: {total_paths}")
            print(
                f"[INT] Segmentos con sección configurada: {total_segments_with_section}"
            )

            # Para debugging: mostrar todos los segmentos
            for i, segment_info in enumerate(self.script_object.saved_segments):
                diameter = segment_info.get("diameter", 0)
                points = segment_info.get("points", [])
                if len(points) >= 2:
                    p1 = points[0]
                    p2 = points[1]
                    print(
                        f"[INT] Segment {i}: {diameter}mm from ({p1.X:.1f},{p1.Y:.1f}) to ({p2.X:.1f},{p2.Y:.1f})"
                    )

            if not self.script_object.saved_segments:
                print("[INT] No hay segmentos con sección configurada")
                # Mostrar información de polilíneas sin sección
                total_segments_available = sum(
                    len(pts) - 1
                    for pts in self.script_object.saved_paths
                    if len(pts) >= 2
                )
                print(
                    f"[INT] Segmentos disponibles para configurar: {total_segments_available}"
                )
                return

            # Agrupar por diámetro
            from collections import defaultdict

            sections_by_diameter = defaultdict(int)

            for segment_info in self.script_object.saved_segments:
                diameter = segment_info["diameter"]
                sections_by_diameter[diameter] += 1

            print(
                f"[INT] Total de segmentos con sección: {len(self.script_object.saved_segments)}"
            )
            for diameter, count in sorted(sections_by_diameter.items()):
                print(f"[INT] - Diámetro {diameter}mm: {count} segmento(s)")

            # Información de estado actual
            print(f"[INT] Estado actual:")
            print(
                f"[INT] - Selección por marco: {len(self.selected_segments) if hasattr(self, 'selected_segments') else 0} segmentos"
            )
            print(
                f"[INT] - Segmento seleccionado: {'Sí' if self.selected_seg else 'No'}"
            )
            print(f"[INT] - Segmento hover: {'Sí' if self.hover_seg else 'No'}")

            # Actualizar texto en la paleta si es posible
            try:
                info_text = f"Segmentos: {len(self.script_object.saved_segments)}\n"
                for diameter, count in sorted(sections_by_diameter.items()):
                    info_text += f"⌀{diameter}mm: {count}\n"

                # Intentar actualizar algún campo de texto en la paleta
                if hasattr(self.script_object.build_ele, "FirstText"):
                    self.script_object.build_ele.FirstText.value = info_text.strip()

            except Exception as ex:
                print(f"[INT] No se pudo actualizar texto en paleta: {ex}")

            return True

        except Exception as ex:
            print(f"[INT] Error mostrando información de secciones: {ex}")
            return False

    def _get_segment_section_info(
        self, kind: str, path_idx: int, seg_idx: int
    ) -> Optional[dict]:
        """Obtiene información de sección para un segmento específico"""
        if kind != "saved":
            return None

        # Buscar en saved_segments usando path_idx y seg_idx si están presentes
        for segment_info in self.script_object.saved_segments:
            if (
                segment_info.get("path_idx") == path_idx
                and segment_info.get("seg_idx") == seg_idx
            ):
                return segment_info

        # Fallback: buscar por puntos (para compatibilidad)
        if 0 <= path_idx < len(self.script_object.saved_paths):
            pts = self.script_object.saved_paths[path_idx]
            if 0 <= seg_idx < len(pts) - 1:
                expected_p1 = pts[seg_idx]
                expected_p2 = pts[seg_idx + 1]

                for segment_info in self.script_object.saved_segments:
                    points = segment_info.get("points", [])
                    if (
                        len(points) >= 2
                        and self._points_equal(points[0], expected_p1)
                        and self._points_equal(points[1], expected_p2)
                    ):
                        return segment_info

        return None

    def _points_equal(
        self, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D, tolerance: float = 1e-6
    ) -> bool:
        """Compara dos puntos con tolerancia"""
        return (
            abs(p1.X - p2.X) < tolerance
            and abs(p1.Y - p2.Y) < tolerance
            and abs(p1.Z - p2.Z) < tolerance
        )

    def _get_section_properties(self, diameter: float):
        """Obtiene las propiedades visuales según el diámetro del segmento"""
        prop = self._clone_properties(self.com_prop)
        # Usar propiedades por defecto del sistema (sin asignar colores específicos)
        return prop

    def _get_section_color_for_preview(self, diameter: float, system: str) -> int:
        """
        Obtiene el color específico para preview según diámetro y sistema.
        - Pluvial 110mm: color 7
        - Fecal 110mm: color 4
        - Fecal 40mm: color 66
        - Fecal 25mm: color 70
        """
        try:
            diameter_int = int(round(diameter))
            system_lower = system.lower().strip()

            if system_lower.startswith("pluvial") and diameter_int == 110:
                return 7
            elif system_lower.startswith("fecal"):
                if diameter_int == 110:
                    return 4
                elif diameter_int == 40:
                    return 66
                elif diameter_int == 25:
                    return 70

            # Color por defecto si no coincide con ninguna especificación
            return PREVIEW_SAVED_COLOR

        except Exception:
            return PREVIEW_SAVED_COLOR

    # ---------- Utilidades de Paleta (Sincronización Segura) ----------
    def _safe_get_palette_property(self, property_name: str, default_value=None):
        """Obtiene una propiedad de la paleta de manera segura"""
        try:
            if (
                not hasattr(self.script_object, "build_ele")
                or self.script_object.build_ele is None
            ):
                return default_value

            if not hasattr(self.script_object.build_ele, property_name):
                return default_value

            prop = getattr(self.script_object.build_ele, property_name)

            if hasattr(prop, "value"):
                return prop.value
            else:
                return prop
        except Exception as ex:
            print(f"[INT] Error obteniendo propiedad {property_name}: {ex}")
            return default_value

    def _safe_set_palette_property(self, property_name: str, value) -> bool:
        """Establece una propiedad de la paleta de manera segura"""
        try:
            if (
                not hasattr(self.script_object, "build_ele")
                or self.script_object.build_ele is None
            ):
                return False

            if not hasattr(self.script_object.build_ele, property_name):
                return False

            prop = getattr(self.script_object.build_ele, property_name)
            if hasattr(prop, "value"):
                prop.value = value
            else:
                setattr(self.script_object.build_ele, property_name, value)
            return True
        except Exception as ex:
            print(f"[INT] Error estableciendo propiedad {property_name}: {ex}")
            return False

    # ---------- Helpers ----------
    def _clone_properties(self, src_prop):
        dst = AllplanBaseElements.CommonProperties()
        dst.GetGlobalProperties()
        for name in (
            "Color",
            "Pen",
            "Stroke",
            "ColorByLayer",
            "PenByLayer",
            "StrokeByLayer",
            "Layer",
        ):
            try:
                setattr(dst, name, getattr(src_prop, name))
            except Exception:
                pass
        return dst

    def _get_current_system(self) -> str:
        """Devuelve el sistema actual en texto ('Pluvial'|'Fecal') según la paleta."""
        try:
            saneamiento_type = self._safe_get_palette_property("Saneamiento")

            if saneamiento_type is not None:
                system = "Pluvial" if saneamiento_type == 0 else "Fecal"
                return system
        except Exception as ex:
            print(f"[INT] Error en _get_current_system: {ex}")

        return "Pluvial"

    def _format_segment_label(self, diameter: float, system: str) -> str:
        """Formatea la etiqueta de segmento: D110 P (pluvial) o D25 F, D40 F, D110 F (fecal)."""
        try:
            d = int(round(float(diameter)))
        except Exception:
            d = int(diameter) if isinstance(diameter, (int, float)) else 0

        # Determinar la letra del sistema
        if system.strip().lower().startswith("fecal"):
            label = f"D{d} F"
        else:
            label = f"D{d} P"

        return label

    def _create_cross_marker(self, point, properties, size, z_bias: float = 0.0):
        """Dibuja una cruz (cruzeta) en torno al punto, en ejes X/Y y una pequeña marca Z."""
        half = max(size * 0.5, 0.1)
        px = getattr(point, "X", 0.0)
        py = getattr(point, "Y", 0.0)
        pz = getattr(point, "Z", 0.0) + (z_bias or 0.0)

        p1 = AllplanGeo.Point3D(px - half, py, pz)
        p2 = AllplanGeo.Point3D(px + half, py, pz)
        p3 = AllplanGeo.Point3D(px, py - half, pz)
        p4 = AllplanGeo.Point3D(px, py + half, pz)
        p5 = AllplanGeo.Point3D(px, py, pz - half)
        p6 = AllplanGeo.Point3D(px, py, pz + half)

        return [
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p1, p2)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p3, p4)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p5, p6)),
        ]

    def _create_point_marker(self, point, properties, size, z_bias: float = 0.0):
        """Marcador circular en plano XY (módulo ElementosDefinidos)."""
        return create_point_marker_geometry(point, properties, size, z_bias)

    def _draw_marker_for_element_type(
        self, pos, element_type: str, properties, size: float = 45.0
    ):
        """Forma por tipo de elemento en modo puntos libres (módulo ElementosDefinidos)."""
        return draw_marker_for_element_type(pos, element_type, properties, size)

    def _add_text_label(
        self,
        elems_list,
        point_a: AllplanGeo.Point3D,
        point_b: AllplanGeo.Point3D,
        text: str,
    ):
        """Añade un TextElement 2D en el centro del segmento, rotado según la dirección del segmento."""
        try:
            # Calcular centro del segmento
            cx = (point_a.X + point_b.X) * 0.5
            cy = (point_a.Y + point_b.Y) * 0.5
            loc = AllplanGeo.Point2D(cx, cy)

            # Crear propiedades específicas para el texto
            text_com_prop = AllplanBaseElements.CommonProperties()
            # No llamar GetGlobalProperties() para evitar escala global

            text_prop = AllplanBasisElements.TextProperties()
            text_prop.Height = 0.30  # Valor fijo pequeño
            text_prop.Width = 0.30
            text_prop.IsScaleDependent = False

            elems_list.append(
                AllplanBasisElements.TextElement(text_com_prop, text_prop, text, loc)
            )
        except Exception as ex:
            print(f"[INT] No se pudo crear etiqueta de texto: {ex}")


# --- utilidad para acotar t mínimo razonable en segmentos cortos ---
def MAX_EPS(x: float) -> float:
    return max(min(x, 0.49), 0.0)


""""
FLUJO:

- Botón 1001 = "Crear polilínea" -> TOGGLE ON/OFF (OFF por defecto)
    * OFF: edición (drag vértices de guardadas, selección por marco, inserción por midpoint/segmento)
    * ON : creación normal (agregar puntos, drag de activos, borrar secciones, insertar)
- Midpoints visibles con z-bias y pen propio, clicables para insertar
- CheckBox 'Mode Insertar punto' controla inserción por clic sobre segmento
- 1004: eliminar nodo (cursor sobre vértice intermedio) o borrar segmento seleccionado/hover
- 1002: guardar activa · 1003/ESC: finalizar (guarda activa y CREA INMEDIATAMENTE)
"""
