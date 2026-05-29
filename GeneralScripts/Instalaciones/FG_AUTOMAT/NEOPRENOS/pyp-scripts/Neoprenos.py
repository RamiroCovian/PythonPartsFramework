from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import random
from typing import Any, Dict, List, TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as AllplanUtil

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from CreateElementResult import CreateElementResult
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from HandlePropertiesService import HandlePropertiesService
from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from PythonPart import PythonPart, PythonPartGroup, View2D3D
from PythonPartUtil import PythonPartUtil
from PythonPartTransaction import ConnectToElements, PythonPartTransaction
from TypeCollections.ModificationElementList import ModificationElementList
from ScriptObjectInteractors.BaseScriptObjectInteractor import (
    BaseScriptObjectInteractor,
)
from ScriptObjectInteractors.LineInteractor import LineInteractor, LineInteractorResult
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from TypeCollections.ModelEleList import ModelEleList

if TYPE_CHECKING:
    from __BuildingElementStubFiles.NeoprenosBuildingElement import (
        NeoprenosBuildingElement as NeoprenosBuildingElement,  # type: ignore
    )

STOPPED = 0
SELECTING_SOLID = 1
SELECTING_WALL = 2
SELECTING_LINE = 3
SELECTING_EXISTING_NEOPRENO = 4

NEOPRENOS_SCRIPT_VERSION = "1.1.0-seleccionar-insert-matrix"
NEOPRENO_EVENT_SELECT_EXISTING = 1050
NEOPRENO_EVENT_DESELECT_EXISTING = 1051
NEOPRENO_EVENT_CHANGE_ACTIVE_WALL = 1052
NEOPRENO_OTHER_EXECUTION_MSG = (
    "No se puede seleccionar un neopreno colocado en otra ejecución.\n\n"
    "Solo puede editar neoprenos colocados en la ejecución actual.\n\n"
    "Para modificar uno anterior, cierre la ejecución actual y abra ese PythonPart."
)
NEOPRENO_PARENT_NOT_IDENTIFIABLE_MSG = (
    "Ha seleccionado un elemento padre no identificable.\n\n"
    "El atributo PMP_PARE quedará vacío."
)

NEOPRENO_CHECKBOX_PARAM_KEYS: tuple[str, ...] = (
    "neopreno_libre",
    "InvertirGrosor",
)

MIN_WIDTH = 20.0
MIN_WIDTH_HALF = MIN_WIDTH / 2.0
MAX_HANDLE_DISTANCE = 100000.0

NEO_LAYER = "PMP_NEOPRENS"

# Atributo estandar Allplan "IFC ID" (AttributeIdEnums.IFC_ID)
IFC_ID_ATTRIBUTE_ID = 683

# Marco auxiliar de seleccion (mismos valores que Angulares.py)
NEOPRENO_SELECTION_AUX_COLOR = 3
NEOPRENO_SELECTION_AUX_PEN = 15
NEOPRENO_SELECTION_AUX_OUTWARD_MM = 0.0
NEOPRENO_SELECTION_AUX_CROSS_HALF_MM = 120.0
NEOPRENO_SELECTION_AUX_PARALLEL_MM = 0.0
NEOPRENO_CREATION_INDICATOR_COLOR = 6
NEOPRENO_CREATION_INDICATOR_PEN = 4
NEOPRENO_CREATION_INDICATOR_HALF_MM = 90.0
NEOPRENO_CREATION_INDICATOR_TEXT_DX_MM = 120.0
NEOPRENO_CREATION_INDICATOR_TEXT_DY_MM = 80.0


def neo_log(message: str) -> None:
    """Log estable para depurar el flujo multi-colocacion en Allplan."""
    try:
        print(f"[NEOPRENOS_MULTI] {message}")
    except Exception:
        pass


def resolve_attribute_id(document, *candidate_names: str) -> int:
    """Devuelve el primer ID de atributo valido probando varios nombres (p. ej. pmp_pare / PMP_PARE)."""
    for name in candidate_names:
        if not name:
            continue
        try:
            attr_id = AllplanBaseElements.AttributeService.GetAttributeID(
                document, name
            )
            if attr_id and attr_id > 0:
                return attr_id
        except Exception:
            continue
    return 0


def _iter_attribute_id_value_pairs(attrs) -> list[tuple[int, Any]]:
    """Normaliza atributos devueltos por GetAttributes o ElementsAttributeService."""
    pairs: list[tuple[int, Any]] = []
    if not attrs:
        return pairs
    if isinstance(attrs, dict):
        for attr_id, attr_value in attrs.items():
            try:
                pairs.append((int(attr_id), attr_value))
            except (TypeError, ValueError):
                continue
        return pairs
    for attr in attrs:
        try:
            attr_id = getattr(attr, "Id", None)
            if attr_id is None and isinstance(attr, (tuple, list)) and len(attr) >= 2:
                attr_id, attr_value = attr[0], attr[1]
            else:
                attr_value = getattr(attr, "Value", None)
            if attr_id is not None:
                pairs.append((int(attr_id), attr_value))
        except Exception:
            continue
    return pairs


def _ifc_id_from_attribute_pairs(pairs: list[tuple[int, Any]]) -> str | None:
    for attr_id, attr_value in pairs:
        if attr_id == IFC_ID_ATTRIBUTE_ID and attr_value is not None:
            value = str(attr_value).strip()
            if value:
                return value
    return None


def build_host_element_selection_query() -> AllplanIFW.SelectionQuery:
    """Tipos seleccionables como soporte del neopreno (muros, losas, solidos 3D, etc.)."""
    type_uuids = (
        AllplanEleAdapter.Volume3D_TypeUUID,
        AllplanEleAdapter.Area3D_TypeUUID,
        AllplanEleAdapter.BRep3D_Volume_TypeUUID,
        AllplanEleAdapter.ArchitectureVolume3D_TypeUUID,
        AllplanEleAdapter.ArchitectureBRep3D_Volume_TypeUUID,
        AllplanEleAdapter.Wall_TypeUUID,
        AllplanEleAdapter.WallTier_TypeUUID,
        AllplanEleAdapter.Column_TypeUUID,
        AllplanEleAdapter.Beam_TypeUUID,
        AllplanEleAdapter.Slab_TypeUUID,
        AllplanEleAdapter.PythonPart_TypeUUID,
        AllplanEleAdapter.PythonPartGroup_TypeUUID,
    )
    return AllplanIFW.SelectionQuery(
        [AllplanIFW.QueryTypeID(uuid) for uuid in type_uuids]
    )


def get_element_ifc_id(element, try_parent: bool = True) -> str | None:
    """Lee el IFC ID (atributo 683) de cualquier elemento del modelo (muro, solido 3D, etc.)."""
    if not element:
        return None
    if hasattr(element, "IsNull") and element.IsNull():
        return None

    read_state = AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable

    try:
        service_attrs = AllplanBaseElements.ElementsAttributeService.GetAttributes(
            element, read_state
        )
        ifc_value = _ifc_id_from_attribute_pairs(
            _iter_attribute_id_value_pairs(service_attrs)
        )
        if ifc_value:
            return ifc_value
    except Exception:
        pass

    try:
        element_attrs = element.GetAttributes(read_state)
        ifc_value = _ifc_id_from_attribute_pairs(
            _iter_attribute_id_value_pairs(element_attrs)
        )
        if ifc_value:
            return ifc_value
    except Exception:
        pass

    if try_parent and hasattr(element, "GetParentElement"):
        try:
            parent = element.GetParentElement()
            if parent and hasattr(parent, "IsValid") and parent.IsValid():
                return get_element_ifc_id(parent, try_parent=False)
        except Exception:
            pass

    return None


def get_wall_ifc_id(wall_element) -> str | None:
    """Alias retrocompatible: obtiene IFC ID del elemento host."""
    return get_element_ifc_id(wall_element, try_parent=True)


def get_wall_material_name(wall_element) -> str | None:
    """Obtiene el nombre del muro desde el atributo Material (id 508) o buscando en todos los atributos."""

    if not wall_element:
        return ""

    try:
        from DocumentManager import DocumentManager

        doc = DocumentManager.get_instance().document

        attrs = wall_element.GetAttributes(
            AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
        )
        material_value_from_508 = None
        for attr in attrs:
            try:
                attr_id = getattr(attr, "Id", None)
                if (
                    attr_id is None
                    and isinstance(attr, (tuple, list))
                    and len(attr) >= 2
                ):
                    attr_id = attr[0]
                    attr_value = attr[1]
                else:
                    attr_value = getattr(attr, "Value", None)

                if attr_id == 508:
                    material_value_from_508 = (
                        str(attr_value).strip() if attr_value else ""
                    )

                    if (
                        material_value_from_508
                        and material_value_from_508 != "<undefiniert>"
                    ):
                        if "$" in material_value_from_508:
                            wall_name = material_value_from_508.split("$")[0].strip()
                            return wall_name if wall_name else None
                        else:
                            return material_value_from_508
            except Exception:
                continue

        for attr in attrs:
            try:
                attr_id = getattr(attr, "Id", None)
                if (
                    attr_id is None
                    and isinstance(attr, (tuple, list))
                    and len(attr) >= 2
                ):
                    attr_id = attr[0]
                    attr_value = attr[1]
                else:
                    attr_value = getattr(attr, "Value", None)

                if attr_value:
                    attr_value_str = str(attr_value).strip()
                    if "$" in attr_value_str and attr_value_str != "<undefiniert>":
                        try:
                            wall_name = attr_value_str.split("$")[0].strip()
                            if wall_name:
                                return wall_name
                        except Exception:
                            pass
            except Exception:
                continue

    except Exception:
        pass

    return None


neo_log(f"module loaded: {__file__}")


def build_saved_state_dict(
    p0: AllplanGeo.Point3D,
    p1: AllplanGeo.Point3D,
    ancho: float,
    grosor: float,
    libre: bool,
    pmp_pare: str,
    pmp_pare_name: str = "",
    rot: float = 0.0,
    invertido: bool = False,
    layer: int = -1,
) -> Dict[str, Any]:
    """
    Construye el diccionario de estado mínimo (MVP) para guardar en SavedState.

    Args:
        p0: PuntoInicial
        p1: PuntoFinal
        ancho: ancho del neopreno
        grosor: grosor seleccionado
        libre: modo libre (neopreno_libre)
        pmp_pare: identificador tecnico del muro/host
        pmp_pare_name: nombre/material legible del muro/host
        rot: rotación en grados (si libre)
        invertido: InvertirGrosor (si aplica)
        layer: layer ID

    Returns:
        Dict listo para serializar a JSON
    """
    return {
        "p0": [p0.X, p0.Y, p0.Z],
        "p1": [p1.X, p1.Y, p1.Z],
        "ancho": float(ancho),
        "grosor": float(grosor),
        "libre": bool(libre),
        "rot": float(rot),
        "invertido": bool(invertido),
        "pmp_pare": normalize_pmp_pare_value(pmp_pare),
        "pmp_pare_name": normalize_pmp_pare_value(pmp_pare_name),
        "layer": int(layer),
    }


def saved_state_to_string(state: Dict[str, Any]) -> str:
    """Serializa el estado a string (JSON) para guardar en build_ele.SavedState."""
    return json.dumps(state, separators=(",", ":"))


def parse_saved_state(s: str) -> Dict[str, Any]:
    """
    Parsea SavedState string (JSON) a diccionario.
    Si falla o está vacío, devuelve dict vacío (no generar defaults aquí).
    """
    if not s or not s.strip():
        return {}
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}


def saved_state_to_point3d(
    state: Dict[str, Any], key: str
) -> AllplanGeo.Point3D | None:
    """Obtiene un Point3D desde state[key] = [x, y, z]. Devuelve None si no existe o es inválido."""
    arr = state.get(key)
    if not arr or len(arr) != 3:
        return None
    try:
        return AllplanGeo.Point3D(float(arr[0]), float(arr[1]), float(arr[2]))
    except (TypeError, ValueError, IndexError):
        return None


def check_allplan_version(_build_ele: BuildingElement, _version: str) -> bool:
    return True


def create_element_hash(element_type: str, stable: bool = False, **params) -> str:
    """
    Crea un hash único y estable para un elemento basado en su tipo y parámetros.

    - En CREACIÓN: stable=False → genera random para unicidad
    - En EDICIÓN: stable=True → sin random, solo parámetros (hash estable)

    Args:
        element_type: Tipo de elemento
        stable: Si True, no agrega random (para edición estable)
        **params: Parámetros del elemento (debe incluir z_unique si está disponible)

    Returns:
        Hash SHA224 como string hexadecimal
    """
    param_items = sorted(params.items())
    param_string = element_type + "_" + "_".join(f"{k}={v}" for k, v in param_items)

    if not stable:
        random_suffix = "_r" + str(random.randint(10**15, 10**16 - 1))
        param_string += random_suffix
    else:
        z_unique_val = params.get("z_unique", params.get("ZUnique", 0))
        if z_unique_val and z_unique_val != 0:
            param_string += f"_z={z_unique_val}"

    hash_val = hashlib.sha224(param_string.encode("utf-8")).hexdigest()
    return hash_val


def create_params_list_from_dict(params: dict) -> List[str]:
    """
    Convierte un diccionario de parámetros en una lista de strings para PythonPart.

    Args:
        params: Diccionario con parámetros del elemento

    Returns:
        Lista de strings en formato "clave = valor\n"
    """
    param_list = []
    for key, value in sorted(params.items()):
        if isinstance(value, AllplanGeo.Point3D):
            param_list.append(f"{key} = Point3D({value.X}, {value.Y}, {value.Z})\n")
        elif isinstance(value, str):
            param_list.append(f"{key} = {repr(value)}\n")
        else:
            param_list.append(f"{key} = {value}\n")
    return param_list


def parse_bool_param_value(value: Any) -> bool | None:
    """Convierte True/False, 0/1 o strings del param_list a bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if value is None:
        return None
    text = str(value).strip().strip("'").strip('"').lower()
    if text in ("true", "1", "yes", "on"):
        return True
    if text in ("false", "0", "no", "off"):
        return False
    return None


def normalize_pmp_pare_value(value: Any) -> str:
    """Valor limpio para PMP_PARE/PMP_WALL_ID: sin comillas de serializacion."""
    if value is None:
        return ""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, str):
                text = parsed.strip()
        except (ValueError, SyntaxError):
            pass
        return text.strip().strip("'").strip('"')
    return str(value).strip().strip("'").strip('"')


def coerce_build_ele_param_value(key: str, value: Any) -> Any:
    """Tipo correcto al cargar param_list del PPG en build_ele (evita CheckBox con str)."""
    if key in ("pmp_pare", "pmp_pare_name"):
        return normalize_pmp_pare_value(value)
    if key in NEOPRENO_CHECKBOX_PARAM_KEYS:
        parsed = parse_bool_param_value(value)
        if parsed is not None:
            return parsed
    if key in ("RotacionManual",):
        try:
            return float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            return 0.0
    if key in ("PuntoInicial", "PuntoFinal") and isinstance(value, AllplanGeo.Point3D):
        return value
    if key in ("Ancho", "GrosorSeleccionado", "Longitud", "z_unique"):
        try:
            return float(value) if value is not None else value
        except (TypeError, ValueError):
            return value
    return value


def parse_params_list_to_dict(param_list: List[str]) -> dict:
    """
    Parsea una lista de strings de parámetros en un diccionario.

    Args:
        param_list: Lista de strings en formato "clave = valor\n"

    Returns:
        Diccionario con los parámetros parseados
    """
    params = {}
    for param_str in param_list:
        if "=" in param_str:
            parts = param_str.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().rstrip("\n").strip()
                bool_val = parse_bool_param_value(value)
                if bool_val is not None and str(value).strip().lower() in (
                    "true",
                    "false",
                    "0",
                    "1",
                ):
                    params[key] = bool_val
                    continue
                try:
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, bool):
                        params[key] = parsed
                        continue
                    if isinstance(parsed, str):
                        params[key] = parsed
                        continue
                except (ValueError, SyntaxError):
                    pass
                try:
                    if "." in value:
                        params[key] = float(value)
                    else:
                        params[key] = int(value)
                except ValueError:
                    if value.startswith("Point3D("):
                        try:
                            coords = (
                                value.replace("Point3D(", "")
                                .replace(")", "")
                                .split(",")
                            )
                            if len(coords) == 3:
                                params[key] = AllplanGeo.Point3D(
                                    float(coords[0].strip()),
                                    float(coords[1].strip()),
                                    float(coords[2].strip()),
                                )
                        except:
                            params[key] = value
                    else:
                        params[key] = value
    return params


def normalize_vector(vec: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D | None:
    length = AllplanGeo.CalcLength(vec)
    if length < 0.001:
        return None
    return AllplanGeo.Vector3D(vec.X / length, vec.Y / length, vec.Z / length)


def cross_product(
    v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D
) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(
        v1.Y * v2.Z - v1.Z * v2.Y, v1.Z * v2.X - v1.X * v2.Z, v1.X * v2.Y - v1.Y * v2.X
    )


def calc_distance_3d(point1: AllplanGeo.Point3D, point2: AllplanGeo.Point3D) -> float:
    return AllplanGeo.CalcLength(
        AllplanGeo.Vector3D(
            point2.X - point1.X, point2.Y - point1.Y, point2.Z - point1.Z
        )
    )


def vector_add(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(v1.X + v2.X, v1.Y + v2.Y, v1.Z + v2.Z)


def vector_scale(vector: AllplanGeo.Vector3D, factor: float) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(vector.X * factor, vector.Y * factor, vector.Z * factor)


def vector_dot(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> float:
    return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z


def _normalize_vector_selection(vector: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    """Normaliza como Angulares.normalize_vector (marco auxiliar de seleccion)."""
    length = vector.GetLength()
    if length < 1e-6:
        return AllplanGeo.Vector3D(0.0, 0.0, 0.0)
    inv = 1.0 / length
    return AllplanGeo.Vector3D(vector.X * inv, vector.Y * inv, vector.Z * inv)


def _is_valid_line(line: AllplanGeo.Line3D | None, min_length_mm: float = 0.1) -> bool:
    if line is None:
        return False
    try:
        return AllplanGeo.CalcLength(line) > float(min_length_mm)
    except Exception:
        return False


def _make_neopreno_selection_aux_properties(
    color: int = NEOPRENO_SELECTION_AUX_COLOR,
    pen: int = NEOPRENO_SELECTION_AUX_PEN,
):
    """Propiedades visibles para las lineas auxiliares de seleccion."""
    props = AllplanBaseElements.CommonProperties()
    try:
        props.GetGlobalProperties()
    except Exception:
        pass
    props.Color = color
    props.Pen = pen
    props.ColorByLayer = False
    props.PenByLayer = False
    props.StrokeByLayer = False
    props.Construction = True
    return props


def _offset_point3d_selection(
    point: AllplanGeo.Point3D, direction: AllplanGeo.Vector3D, distance_mm: float
) -> AllplanGeo.Point3D:
    return AllplanGeo.Point3D(
        point.X + direction.X * distance_mm,
        point.Y + direction.Y * distance_mm,
        point.Z + direction.Z * distance_mm,
    )


def _append_neopreno_aux_line(
    elements: list[Any],
    props: Any,
    p0: AllplanGeo.Point3D,
    p1: AllplanGeo.Point3D,
) -> None:
    try:
        if AllplanGeo.CalcLength(AllplanGeo.Line3D(p0, p1)) < 0.5:
            return
    except Exception:
        return
    elements.append(
        AllplanBasisElements.ModelElement3D(props, AllplanGeo.Line3D(p0, p1))
    )


def _build_neopreno_selection_auxiliary_elements(
    line: AllplanGeo.Line3D | None,
    outward: AllplanGeo.Vector3D | None = None,
    color: int = NEOPRENO_SELECTION_AUX_COLOR,
    pen: int = NEOPRENO_SELECTION_AUX_PEN,
) -> list[Any]:
    """
    Marco auxiliar de seleccion: eje, paralelas y cruz central (sin escuadras).
    """
    if line is None:
        return []

    props = _make_neopreno_selection_aux_properties(color=color, pen=pen)
    start = AllplanGeo.Point3D(line.StartPoint.X, line.StartPoint.Y, line.StartPoint.Z)
    end = AllplanGeo.Point3D(line.EndPoint.X, line.EndPoint.Y, line.EndPoint.Z)

    outward_norm = _normalize_vector_selection(outward) if outward is not None else None
    if outward_norm is not None and outward_norm.GetLength() > 1e-6:
        outward_mm = float(NEOPRENO_SELECTION_AUX_OUTWARD_MM)
        if abs(outward_mm) > 0.01:
            start = _offset_point3d_selection(start, outward_norm, outward_mm)
            end = _offset_point3d_selection(end, outward_norm, outward_mm)

    axis_vec = _normalize_vector_selection(
        AllplanGeo.Vector3D(end.X - start.X, end.Y - start.Y, end.Z - start.Z)
    )
    if axis_vec.GetLength() < 1e-6:
        return []

    if outward_norm is not None and outward_norm.GetLength() > 1e-6:
        lateral = _normalize_vector_selection(cross_product(axis_vec, outward_norm))
    else:
        lateral = _normalize_vector_selection(
            cross_product(axis_vec, AllplanGeo.Vector3D(0.0, 0.0, 1.0))
        )
    if lateral.GetLength() < 1e-6:
        lateral = _normalize_vector_selection(
            cross_product(axis_vec, AllplanGeo.Vector3D(0.0, 1.0, 0.0))
        )
    vertical = _normalize_vector_selection(cross_product(axis_vec, lateral))

    guides: list[Any] = []
    _append_neopreno_aux_line(guides, props, start, end)

    parallel_offset = NEOPRENO_SELECTION_AUX_PARALLEL_MM
    for sign in (-1.0, 1.0):
        off = sign * parallel_offset
        p0 = _offset_point3d_selection(start, lateral, off)
        p1 = _offset_point3d_selection(end, lateral, off)
        _append_neopreno_aux_line(guides, props, p0, p1)

    mid = AllplanGeo.Point3D(
        (start.X + end.X) / 2.0,
        (start.Y + end.Y) / 2.0,
        (start.Z + end.Z) / 2.0,
    )
    cross_half = float(NEOPRENO_SELECTION_AUX_CROSS_HALF_MM)
    _append_neopreno_aux_line(
        guides,
        props,
        _offset_point3d_selection(mid, lateral, -cross_half),
        _offset_point3d_selection(mid, lateral, cross_half),
    )
    _append_neopreno_aux_line(
        guides,
        props,
        _offset_point3d_selection(mid, vertical, -cross_half),
        _offset_point3d_selection(mid, vertical, cross_half),
    )
    return guides


def _make_neopreno_creation_indicator_properties():
    props = AllplanBaseElements.CommonProperties()
    try:
        props.GetGlobalProperties()
    except Exception:
        pass
    props.Color = NEOPRENO_CREATION_INDICATOR_COLOR
    props.Pen = NEOPRENO_CREATION_INDICATOR_PEN
    props.ColorByLayer = False
    props.PenByLayer = False
    props.StrokeByLayer = False
    props.Construction = True
    return props


def _build_neopreno_creation_indicator_elements(
    anchor: AllplanGeo.Point3D | None,
    has_previous_neoprenos: bool,
) -> list[Any]:
    if anchor is None:
        return []

    props = _make_neopreno_creation_indicator_properties()
    half = float(NEOPRENO_CREATION_INDICATOR_HALF_MM)
    elements: list[Any] = []

    px = AllplanGeo.Point3D(anchor.X + half, anchor.Y, anchor.Z)
    nx = AllplanGeo.Point3D(anchor.X - half, anchor.Y, anchor.Z)
    py = AllplanGeo.Point3D(anchor.X, anchor.Y + half, anchor.Z)
    ny = AllplanGeo.Point3D(anchor.X, anchor.Y - half, anchor.Z)
    pz = AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z + half)
    nz = AllplanGeo.Point3D(anchor.X, anchor.Y, anchor.Z - half)

    elements.append(
        AllplanBasisElements.ModelElement3D(props, AllplanGeo.Line3D(nx, px))
    )
    elements.append(
        AllplanBasisElements.ModelElement3D(props, AllplanGeo.Line3D(ny, py))
    )
    elements.append(
        AllplanBasisElements.ModelElement3D(props, AllplanGeo.Line3D(nz, pz))
    )

    try:
        text_props = AllplanBasisElements.TextProperties()
        text_props.Height = 0.12
        text_props.Width = 0.12
        text_props.IsScaleDependent = False
        label = (
            "Nuevo neopreno: primer punto"
            if has_previous_neoprenos
            else "Neopreno: primer punto"
        )
        loc = AllplanGeo.Point2D(
            anchor.X + NEOPRENO_CREATION_INDICATOR_TEXT_DX_MM,
            anchor.Y + NEOPRENO_CREATION_INDICATOR_TEXT_DY_MM,
        )
        elements.append(AllplanBasisElements.TextElement(props, text_props, label, loc))
    except Exception:
        pass

    return elements


def rotate_vector_around_axis(
    vector: AllplanGeo.Vector3D, axis: AllplanGeo.Vector3D, angle_rad: float
) -> AllplanGeo.Vector3D:
    axis_norm = normalize_vector(axis)
    if not axis_norm:
        return vector

    cos_ang = math.cos(angle_rad)
    sin_ang = math.sin(angle_rad)

    term1 = vector_scale(vector, cos_ang)
    term2 = vector_scale(cross_product(axis_norm, vector), sin_ang)
    term3 = vector_scale(axis_norm, vector_dot(axis_norm, vector) * (1.0 - cos_ang))

    rotated = vector_add(vector_add(term1, term2), term3)
    return normalize_vector(rotated) or vector


def get_view_plane_normal(
    coord_input: AllplanIFW.CoordinateInput = None,
) -> AllplanGeo.Vector3D:
    try:
        if coord_input:
            view_proj = coord_input.GetViewWorldProjection()
            if view_proj and isinstance(view_proj, AllplanGeo.Matrix3D):
                view_z = AllplanGeo.Vector3D(
                    view_proj.m20, view_proj.m21, view_proj.m22
                )
                view_z_normalized = normalize_vector(view_z)
                if view_z_normalized:
                    abs_x = abs(view_z_normalized.X)
                    abs_y = abs(view_z_normalized.Y)
                    abs_z = abs(view_z_normalized.Z)

                    if abs_x > abs_y and abs_x > abs_z:
                        return (
                            AllplanGeo.Vector3D(1, 0, 0)
                            if view_z_normalized.X > 0
                            else AllplanGeo.Vector3D(-1, 0, 0)
                        )
                    if abs_y > abs_z:
                        return (
                            AllplanGeo.Vector3D(0, 1, 0)
                            if view_z_normalized.Y > 0
                            else AllplanGeo.Vector3D(0, -1, 0)
                        )
                    return (
                        AllplanGeo.Vector3D(0, 0, 1)
                        if view_z_normalized.Z > 0
                        else AllplanGeo.Vector3D(0, 0, -1)
                    )
    except Exception:
        pass
    return AllplanGeo.Vector3D(0, 0, 1)


def get_selected_thickness(build_ele: BuildingElement) -> float:
    if (
        hasattr(build_ele, "GrosorSeleccionado")
        and build_ele.GrosorSeleccionado.value is not None
    ):
        return float(build_ele.GrosorSeleccionado.value)
    return 5.0


def get_neopreno_width(build_ele: BuildingElement, default: float = 50.0) -> float:
    min_width = 20.0

    if hasattr(build_ele, "Ancho") and build_ele.Ancho.value is not None:
        try:
            width_value = float(build_ele.Ancho.value)
        except (TypeError, ValueError):
            width_value = default
    else:
        width_value = default

    width_value = max(min_width, width_value)

    if hasattr(build_ele, "Ancho"):
        build_ele.Ancho.value = width_value

    return width_value


def get_color_for_thickness(thickness: float) -> int:
    color_map = {5.0: 15, 10.0: 4, 20.0: 5, 30.0: 8, 40.0: 3}
    return color_map.get(thickness, 15)


def update_color_for_thickness(build_ele: BuildingElement):
    if not build_ele or not hasattr(build_ele, "GrosorSeleccionado"):
        return

    thickness = get_selected_thickness(build_ele)
    color_number = get_color_for_thickness(thickness)

    if hasattr(build_ele, "Color"):
        build_ele.Color.value = color_number


def calculate_local_coordinate_system(
    face_polygon: AllplanGeo.Polygon3D, face_normal: AllplanGeo.Vector3D
) -> dict:
    try:
        if not face_polygon or face_polygon.Count() < 3:
            return None

        axis_w = normalize_vector(face_normal)
        if not axis_w:
            return None

        result = AllplanGeo.CalcMinMax(face_polygon)
        if isinstance(result, tuple):
            minmax_obj, _ = result
            min_point = minmax_obj.Min
            max_point = minmax_obj.Max
        else:
            min_point = result.Min
            max_point = result.Max

        origin = AllplanGeo.Point3D(
            (min_point.X + max_point.X) / 2.0,
            (min_point.Y + max_point.Y) / 2.0,
            (min_point.Z + max_point.Z) / 2.0,
        )

        p0 = face_polygon.GetPoint(0)
        p1 = face_polygon.GetPoint(1)
        edge_vector = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)

        dot = (
            edge_vector.X * axis_w.X
            + edge_vector.Y * axis_w.Y
            + edge_vector.Z * axis_w.Z
        )
        axis_u = AllplanGeo.Vector3D(
            edge_vector.X - dot * axis_w.X,
            edge_vector.Y - dot * axis_w.Y,
            edge_vector.Z - dot * axis_w.Z,
        )

        axis_u = normalize_vector(axis_u)
        if not axis_u:
            axis_u = (
                AllplanGeo.Vector3D(1, 0, 0)
                if abs(axis_w.X) < 0.9
                else AllplanGeo.Vector3D(0, 1, 0)
            )

        axis_v = cross_product(axis_w, axis_u)
        axis_v = normalize_vector(axis_v)

        u_coords = []
        v_coords = []

        for i in range(face_polygon.Count()):
            vertex = face_polygon.GetPoint(i)
            vec_from_origin = AllplanGeo.Vector3D(
                vertex.X - origin.X, vertex.Y - origin.Y, vertex.Z - origin.Z
            )
            u_coords.append(vec_from_origin.DotProduct(axis_u))
            v_coords.append(vec_from_origin.DotProduct(axis_v))

        width = max(u_coords) - min(u_coords)
        height = max(v_coords) - min(v_coords)

        return {
            "origin": origin,
            "axis_u": axis_u,
            "axis_v": axis_v,
            "axis_w": axis_w,
            "width": width,
            "height": height,
            "min_point": min_point,
            "max_point": max_point,
        }

    except Exception:
        return None


def calculate_relative_position(point: AllplanGeo.Point3D, local_system: dict) -> dict:
    try:
        if not local_system:
            return None

        origin = local_system["origin"]
        axis_u = local_system["axis_u"]
        axis_v = local_system["axis_v"]
        width = local_system["width"]
        height = local_system["height"]

        to_point = AllplanGeo.Vector3D(
            point.X - origin.X, point.Y - origin.Y, point.Z - origin.Z
        )

        u_absolute = (
            to_point.X * axis_u.X + to_point.Y * axis_u.Y + to_point.Z * axis_u.Z
        )
        v_absolute = (
            to_point.X * axis_v.X + to_point.Y * axis_v.Y + to_point.Z * axis_v.Z
        )

        u_relative = (u_absolute / width + 0.5) if width > 0.001 else 0.5
        v_relative = (v_absolute / height + 0.5) if height > 0.001 else 0.5

        return {
            "u": u_relative,
            "v": v_relative,
            "u_absolute": u_absolute,
            "v_absolute": v_absolute,
            "distance_from_origin": AllplanGeo.CalcLength(to_point),
        }

    except Exception:
        return None


def calculate_position_from_uv(
    u_relative: float, v_relative: float, local_system: dict
) -> AllplanGeo.Point3D:
    try:
        if not local_system:
            return None

        origin = local_system["origin"]
        axis_u = local_system["axis_u"]
        axis_v = local_system["axis_v"]
        width = local_system["width"]
        height = local_system["height"]

        u_absolute = (u_relative - 0.5) * width
        v_absolute = (v_relative - 0.5) * height

        point = AllplanGeo.Point3D(
            origin.X + u_absolute * axis_u.X + v_absolute * axis_v.X,
            origin.Y + u_absolute * axis_u.Y + v_absolute * axis_v.Y,
            origin.Z + u_absolute * axis_u.Z + v_absolute * axis_v.Z,
        )

        return point

    except Exception:
        return None


def project_line_on_face(
    line: AllplanGeo.Line3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
) -> AllplanGeo.Line3D:
    try:
        normal = normalize_vector(face_normal)
        if not normal:
            return line

        nx, ny, nz = normal.X, normal.Y, normal.Z

        is_horizontal = abs(nz) > 0.9

        if is_horizontal:
            return AllplanGeo.Line3D(
                AllplanGeo.Point3D(line.StartPoint.X, line.StartPoint.Y, face_point.Z),
                AllplanGeo.Point3D(line.EndPoint.X, line.EndPoint.Y, face_point.Z),
            )
        else:
            return AllplanGeo.Line3D(
                project_point_to_face_plane(line.StartPoint, face_point, face_normal),
                project_point_to_face_plane(line.EndPoint, face_point, face_normal),
            )

    except Exception:
        return line


def build_face_local_axes_for_handles(
    start_point: AllplanGeo.Point3D,
    end_point: AllplanGeo.Point3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
) -> tuple[
    AllplanGeo.Vector3D | None, AllplanGeo.Vector3D | None, AllplanGeo.Vector3D | None
]:
    """
    Construye los ejes locales de la cara para los handles.

    Returns:
        tuple: (x_dir, y_dir, z_dir) donde:
        - x_dir: direccion de la linea en el plano de la cara
        - y_dir: direccion del ancho en el plano de la cara
        - z_dir: normal hacia afuera del muro
    """
    start_proj = project_point_to_face_plane(start_point, face_point, face_normal)
    end_proj = project_point_to_face_plane(end_point, face_point, face_normal)

    proj_vec = AllplanGeo.Vector3D(
        end_proj.X - start_proj.X, end_proj.Y - start_proj.Y, end_proj.Z - start_proj.Z
    )
    x_dir = normalize_vector(proj_vec)

    if not x_dir:
        return None, None, None

    z_dir_normalized = normalize_vector(face_normal)
    if not z_dir_normalized:
        return None, None, None

    z_dir = AllplanGeo.Vector3D(
        -z_dir_normalized.X, -z_dir_normalized.Y, -z_dir_normalized.Z
    )

    y_dir = cross_product(z_dir, x_dir)
    y_dir = normalize_vector(y_dir)

    if not y_dir:
        return None, None, None

    dot_z_face_check = vector_dot(z_dir, z_dir_normalized)
    if dot_z_face_check > 0:
        z_dir = AllplanGeo.Vector3D(-z_dir.X, -z_dir.Y, -z_dir.Z)
        y_dir = cross_product(z_dir, x_dir)
        y_dir = normalize_vector(y_dir)
        if not y_dir:
            return None, None, None

    if y_dir.Z < 0:
        dot_z_face_before_flip = vector_dot(z_dir, z_dir_normalized)
        if dot_z_face_before_flip < 0:  # z_dir ya apunta hacia afuera
            y_dir = AllplanGeo.Vector3D(-y_dir.X, -y_dir.Y, -y_dir.Z)
            z_dir = AllplanGeo.Vector3D(-z_dir.X, -z_dir.Y, -z_dir.Z)
        else:
            y_dir = AllplanGeo.Vector3D(-y_dir.X, -y_dir.Y, -y_dir.Z)
            dot_z_face_after = vector_dot(z_dir, z_dir_normalized)
            if dot_z_face_after > 0:
                z_dir = AllplanGeo.Vector3D(-z_dir.X, -z_dir.Y, -z_dir.Z)

    return x_dir, y_dir, z_dir


def project_point_to_face_plane(
    p: AllplanGeo.Point3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
) -> AllplanGeo.Point3D:
    """Proyecta un punto al plano definido por face_point y face_normal."""
    n = normalize_vector(face_normal)
    if not n:
        return p

    v = AllplanGeo.Vector3D(p.X - face_point.X, p.Y - face_point.Y, p.Z - face_point.Z)

    d = vector_dot(v, n)

    return AllplanGeo.Point3D(p.X - n.X * d, p.Y - n.Y * d, p.Z - n.Z * d)


def get_view_ray_from_mouse(
    coord_input: AllplanIFW.CoordinateInput, mouse_point_2d: AllplanGeo.Point2D
) -> tuple[AllplanGeo.Point3D | None, AllplanGeo.Vector3D | None]:
    """
    Obtiene el rayo de vista desde la posicion del mouse.

    Args:
        coord_input: CoordinateInput del interactor
        mouse_point_2d: Posicion del mouse en coordenadas 2D de la vista
    """
    if not coord_input:
        return None, None

    try:
        view_proj = coord_input.GetViewWorldProjection()
        if not view_proj or not isinstance(view_proj, AllplanGeo.Matrix3D):
            return None, None

        mouse_world_approx = coord_input.GetWorldPoint(mouse_point_2d)
        if not mouse_world_approx:
            return None, None

        inv_view_proj = view_proj.GetInverse()
        if not inv_view_proj:
            return None, None

        ray_origin = AllplanGeo.Point3D(
            inv_view_proj.m30, inv_view_proj.m31, inv_view_proj.m32
        )

        ray_direction = AllplanGeo.Vector3D(
            mouse_world_approx.X - ray_origin.X,
            mouse_world_approx.Y - ray_origin.Y,
            mouse_world_approx.Z - ray_origin.Z,
        )

        ray_direction = normalize_vector(ray_direction)
        if not ray_direction:
            return None, None

        return ray_origin, ray_direction

    except Exception:
        return None, None


def intersect_ray_with_face_plane(
    ray_origin: AllplanGeo.Point3D,
    ray_direction: AllplanGeo.Vector3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
) -> AllplanGeo.Point3D | None:
    """
    Calcula la interseccion de un rayo con el plano de la cara.

    Args:
        ray_origin: Origen del rayo (posicion de la camara)
        ray_direction: Direccion normalizada del rayo
        face_point: Punto en el plano de la cara
        face_normal: Normal del plano de la cara

    Returns:
        Punto de interseccion o None si el rayo es paralelo al plano
    """
    n = normalize_vector(face_normal)
    if not n:
        return None

    ray_dir_norm = normalize_vector(ray_direction)
    if not ray_dir_norm:
        return None

    vec_to_face = AllplanGeo.Vector3D(
        face_point.X - ray_origin.X,
        face_point.Y - ray_origin.Y,
        face_point.Z - ray_origin.Z,
    )

    denom = vector_dot(ray_dir_norm, n)

    if abs(denom) < 1e-6:
        return None

    t = vector_dot(vec_to_face, n) / denom

    intersection_point = AllplanGeo.Point3D(
        ray_origin.X + ray_dir_norm.X * t,
        ray_origin.Y + ray_dir_norm.Y * t,
        ray_origin.Z + ray_dir_norm.Z * t,
    )

    return intersection_point


def world_to_uv_face(
    p: AllplanGeo.Point3D,
    origin: AllplanGeo.Point3D,
    u_dir: AllplanGeo.Vector3D,
    v_dir: AllplanGeo.Vector3D,
) -> tuple[float, float]:
    """
    Convierte un punto global a coordenadas UV del plano de la cara.

    Args:
        p: Punto en coordenadas globales
        origin: Origen del sistema UV (tipicamente face_point o punto inicial)
        u_dir: Direccion U (x_dir, normalizada)
        v_dir: Direccion V (y_dir, normalizada)

    Returns:
        tuple: (u, v) coordenadas en el plano UV
    """
    v = AllplanGeo.Vector3D(p.X - origin.X, p.Y - origin.Y, p.Z - origin.Z)
    u = vector_dot(v, u_dir)
    v_coord = vector_dot(v, v_dir)
    return u, v_coord


def uv_to_world_face(
    u: float,
    v: float,
    origin: AllplanGeo.Point3D,
    u_dir: AllplanGeo.Vector3D,
    v_dir: AllplanGeo.Vector3D,
) -> AllplanGeo.Point3D:
    """
    Convierte coordenadas UV del plano de la cara a coordenadas world.

    Args:
        u: Coordenada U en el plano de la cara
        v: Coordenada V en el plano de la cara
        origin: Origen del sistema UV
        u_dir: Direccion U (x_dir, normalizada)
        v_dir: Direccion V (y_dir, normalizada)

    Returns:
        Punto en coordenadas world
    """
    return AllplanGeo.Point3D(
        origin.X + u_dir.X * u + v_dir.X * v,
        origin.Y + u_dir.Y * u + v_dir.Y * v,
        origin.Z + u_dir.Z * u + v_dir.Z * v,
    )


def get_face_uv_bounds(
    face_polygon: AllplanGeo.Polygon3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
    u_dir: AllplanGeo.Vector3D,
    v_dir: AllplanGeo.Vector3D,
) -> tuple[float, float, float, float]:
    """
    Calcula los limites UV del poligono de la cara.

    Returns:
        tuple: (u_min, u_max, v_min, v_max)
    """
    if not face_polygon or face_polygon.Count() < 3:
        return -1e6, 1e6, -1e6, 1e6

    u_coords = []
    v_coords = []

    for i in range(face_polygon.Count()):
        vertex = face_polygon.GetPoint(i)
        vertex_proj = project_point_to_face_plane(vertex, face_point, face_normal)
        u, v = world_to_uv_face(vertex_proj, face_point, u_dir, v_dir)
        u_coords.append(u)
        v_coords.append(v)

    return min(u_coords), max(u_coords), min(v_coords), max(v_coords)


def apply_line_projection_or_translation(
    line: AllplanGeo.Line3D,
    face_point: AllplanGeo.Point3D,
    face_normal: AllplanGeo.Vector3D,
    max_displacement: float = 50000,
) -> AllplanGeo.Line3D:
    if not face_normal or not face_point:
        return line

    projected_line = project_line_on_face(line, face_point, face_normal)

    displacement = calc_distance_3d(projected_line.StartPoint, line.StartPoint)

    if displacement < max_displacement:
        return projected_line
    else:
        offset = AllplanGeo.Vector3D(
            face_point.X - line.StartPoint.X,
            face_point.Y - line.StartPoint.Y,
            face_point.Z - line.StartPoint.Z,
        )

        return AllplanGeo.Line3D(
            AllplanGeo.Point3D(
                line.StartPoint.X + offset.X,
                line.StartPoint.Y + offset.Y,
                line.StartPoint.Z + offset.Z,
            ),
            AllplanGeo.Point3D(
                line.EndPoint.X + offset.X,
                line.EndPoint.Y + offset.Y,
                line.EndPoint.Z + offset.Z,
            ),
        )


def create_neopreno_solid_on_face(
    line: AllplanGeo.Line3D,
    ancho: float,
    grosor: float,
    face_normal: AllplanGeo.Vector3D = None,
    face_point: AllplanGeo.Point3D = None,
    invertir_grosor: bool = False,
    coord_input: AllplanIFW.CoordinateInput = None,
    rotation_deg: float = 0.0,
    placement_matrix: AllplanGeo.Matrix3D = None,
    is_free_mode: bool = False,
) -> AllplanGeo.BRep3D:
    """Crea el solido del neopreno.

    Args:
        is_free_mode: Si True, usa posicionamiento libre.
    """
    try:
        raw_start = line.StartPoint
        raw_end = line.EndPoint

        if not is_free_mode and face_normal and face_point:
            # punto_inicial = project_point_to_face_plane(
            #     raw_start, face_point, face_normal
            # )
            # punto_final = project_point_to_face_plane(raw_end, face_point, face_normal)
            punto_inicial = raw_start
            punto_final = raw_end
        else:
            punto_inicial = raw_start
            punto_final = raw_end

        vector_longitud = AllplanGeo.Vector3D(
            punto_final.X - punto_inicial.X,
            punto_final.Y - punto_inicial.Y,
            punto_final.Z - punto_inicial.Z,
        )

        longitud = AllplanGeo.CalcLength(vector_longitud)
        if longitud < 0.1:
            return None

        vector_longitud = normalize_vector(vector_longitud)

        if is_free_mode:
            if face_normal:
                vector_grosor = normalize_vector(face_normal)
                if not vector_grosor:
                    vector_grosor = get_view_plane_normal(coord_input)
            else:
                view_plane_normal = get_view_plane_normal(coord_input)
                vector_grosor = view_plane_normal

            vector_ancho = cross_product(vector_longitud, vector_grosor)
            vector_ancho = normalize_vector(vector_ancho)

            if not vector_ancho or AllplanGeo.CalcLength(vector_ancho) < 0.001:
                if abs(vector_longitud.DotProduct(vector_grosor)) > 0.9:
                    view_plane_normal = get_view_plane_normal(coord_input)
                    if abs(vector_longitud.Z) < 0.9:
                        vector_ancho = cross_product(
                            vector_longitud, AllplanGeo.Vector3D(0, 0, 1)
                        )
                    elif abs(vector_longitud.Y) < 0.9:
                        vector_ancho = cross_product(
                            vector_longitud, AllplanGeo.Vector3D(0, 1, 0)
                        )
                    else:
                        vector_ancho = cross_product(
                            vector_longitud, AllplanGeo.Vector3D(1, 0, 0)
                        )
                    vector_ancho = normalize_vector(vector_ancho)
                    if not vector_ancho:
                        if abs(vector_longitud.X) < 0.5:
                            vector_ancho = AllplanGeo.Vector3D(1, 0, 0)
                        elif abs(vector_longitud.Y) < 0.5:
                            vector_ancho = AllplanGeo.Vector3D(0, 1, 0)
                        else:
                            vector_ancho = AllplanGeo.Vector3D(0, 0, 1)

            if invertir_grosor:
                vector_ancho = AllplanGeo.Vector3D(
                    -vector_ancho.X, -vector_ancho.Y, -vector_ancho.Z
                )
                vector_grosor = cross_product(vector_ancho, vector_longitud)
                vector_grosor = normalize_vector(vector_grosor)
                if not vector_grosor:
                    vector_grosor = get_view_plane_normal(coord_input)

            if abs(rotation_deg) > 1e-6:
                rotation_rad = math.radians(rotation_deg)
                vector_ancho = rotate_vector_around_axis(
                    vector_ancho, vector_longitud, rotation_rad
                )
                vector_grosor = rotate_vector_around_axis(
                    vector_grosor, vector_longitud, rotation_rad
                )
                vector_ancho = normalize_vector(vector_ancho) or vector_ancho
                vector_grosor = (
                    normalize_vector(cross_product(vector_ancho, vector_longitud))
                    or vector_grosor
                )

            desplazamiento_centrado = ancho / 2.0
            longitud_vector_ancho = AllplanGeo.CalcLength(vector_ancho)

            if longitud_vector_ancho < 0.1:
                punto_inicio = punto_inicial
            else:
                punto_inicio = AllplanGeo.Point3D(
                    punto_inicial.X - vector_ancho.X * desplazamiento_centrado,
                    punto_inicial.Y - vector_ancho.Y * desplazamiento_centrado,
                    punto_inicial.Z - vector_ancho.Z * desplazamiento_centrado,
                )

            vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                -vector_grosor.X, -vector_grosor.Y, -vector_grosor.Z
            )
        else:
            if face_normal and face_point:
                x_dir_solid, y_dir_solid, z_dir_solid = (
                    build_face_local_axes_for_handles(
                        punto_inicial, punto_final, face_point, face_normal
                    )
                )

                if x_dir_solid and y_dir_solid and z_dir_solid:
                    vector_longitud = x_dir_solid
                    vector_ancho = y_dir_solid
                    vector_grosor = z_dir_solid

                    n_check = normalize_vector(face_normal)
                    if n_check:
                        dot_z_face_before = vector_dot(vector_grosor, n_check)
                        if dot_z_face_before > 0:
                            vector_grosor = AllplanGeo.Vector3D(
                                -vector_grosor.X, -vector_grosor.Y, -vector_grosor.Z
                            )
                            vector_longitud = normalize_vector(
                                cross_product(vector_ancho, vector_grosor)
                            )
                            if not vector_longitud:
                                vector_longitud = normalize_vector(
                                    AllplanGeo.Vector3D(
                                        punto_final.X - punto_inicial.X,
                                        punto_final.Y - punto_inicial.Y,
                                        punto_final.Z - punto_inicial.Z,
                                    )
                                )
                                if not vector_longitud:
                                    vector_longitud = x_dir_solid

                    offset_centro = grosor * 0.5
                    punto_inicio = AllplanGeo.Point3D(
                        punto_inicial.X + vector_grosor.X * offset_centro,
                        punto_inicial.Y + vector_grosor.Y * offset_centro,
                        punto_inicial.Z + vector_grosor.Z * offset_centro,
                    )

                    vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                        -vector_grosor.X, -vector_grosor.Y, -vector_grosor.Z
                    )
                else:
                    vector_grosor = (
                        normalize_vector(face_normal)
                        if face_normal
                        else AllplanGeo.Vector3D(0, 0, 1)
                    )
                    vector_ancho = cross_product(vector_longitud, vector_grosor)
                    vector_ancho = normalize_vector(
                        vector_ancho
                    ) or AllplanGeo.Vector3D(0, 1, 0)
                    punto_inicio = punto_inicial
                    vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                        -vector_grosor.X, -vector_grosor.Y, -vector_grosor.Z
                    )
            else:
                vector_grosor = AllplanGeo.Vector3D(0, 0, 1)
                vector_ancho = cross_product(vector_longitud, vector_grosor)
                vector_ancho = normalize_vector(vector_ancho) or AllplanGeo.Vector3D(
                    0, 1, 0
                )
                punto_inicio = punto_inicial
                vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                    -vector_grosor.X, -vector_grosor.Y, -vector_grosor.Z
                )

        axis_placement = AllplanGeo.AxisPlacement3D(
            punto_inicio, vector_longitud, vector_grosor_para_cuboid
        )

        cuboid = AllplanGeo.BRep3D.CreateCuboid(axis_placement, longitud, ancho, grosor)

        return cuboid

    except Exception:
        return None


def create_handles(
    build_ele: BuildingElement,
    line: AllplanGeo.Line3D,
    face_normal: AllplanGeo.Vector3D | None = None,
    coord_input: AllplanIFW.CoordinateInput = None,
    rotation_deg: float = 0.0,
    is_free_mode: bool = False,
    x_dir: AllplanGeo.Vector3D | None = None,
    y_dir: AllplanGeo.Vector3D | None = None,
    z_dir: AllplanGeo.Vector3D | None = None,
) -> list[HandleProperties]:
    """
    Crea los handles para el neopreno.

    Args:
        x_dir: Direccion longitudinal del neopreno sobre la cara
        y_dir: Direccion del ancho del neopreno sobre la cara
        z_dir: Normal de la cara, hacia afuera del muro
    """
    handle_list = []

    punto_inicial = line.StartPoint
    punto_final = line.EndPoint

    line_direction_vec = AllplanGeo.Vector3D(
        punto_final.X - punto_inicial.X,
        punto_final.Y - punto_inicial.Y,
        punto_final.Z - punto_inicial.Z,
    )
    line_direction = normalize_vector(line_direction_vec) or AllplanGeo.Vector3D(
        1.0, 0.0, 0.0
    )

    handle_plane = None
    if not is_free_mode and x_dir and y_dir and z_dir:
        x_dir_handle = normalize_vector(x_dir)
        y_dir_handle = normalize_vector(y_dir)
        z_dir_handle = normalize_vector(z_dir)

        if x_dir_handle and y_dir_handle and z_dir_handle:
            handle_plane = AllplanGeo.Plane3D(punto_inicial, z_dir_handle)

            if face_normal:
                handle_plane_normal = cross_product(x_dir_handle, y_dir_handle)
                handle_plane_normal = normalize_vector(handle_plane_normal)
                face_normal_norm = normalize_vector(face_normal)

                if handle_plane_normal and face_normal_norm:
                    dot_plane = vector_dot(handle_plane_normal, face_normal_norm)
                    dot_n_face = vector_dot(z_dir_handle, face_normal_norm)

    if handle_plane:

        handle_list.append(
            HandleProperties(
                "PuntoInicialHandle",
                punto_inicial,
                punto_inicial,
                [HandleParameterData("PuntoInicial", HandleParameterType.POINT)],
                HandleDirection.PLANE_DIR,
                plane=handle_plane,
                info_text="Punto inicial de la linea",
            )
        )

        handle_list.append(
            HandleProperties(
                "PuntoFinalHandle",
                punto_final,
                punto_inicial,
                [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                HandleDirection.PLANE_DIR,
                plane=handle_plane,
                info_text="Punto final de la linea",
            )
        )
    else:
        handle_list.append(
            HandleProperties(
                "PuntoInicialHandle",
                punto_inicial,
                punto_inicial,
                [HandleParameterData("PuntoInicial", HandleParameterType.POINT)],
                HandleDirection.XYZ_DIR,
                info_text="Punto inicial de la linea",
            )
        )

        handle_list.append(
            HandleProperties(
                "PuntoFinalHandle",
                punto_final,
                punto_inicial,
                [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                HandleDirection.XYZ_DIR,
                info_text="Punto final de la linea",
            )
        )

    width_value = get_neopreno_width(build_ele)
    midpoint = AllplanGeo.Point3D(
        (punto_inicial.X + punto_final.X) / 2.0,
        (punto_inicial.Y + punto_final.Y) / 2.0,
        (punto_inicial.Z + punto_final.Z) / 2.0,
    )

    if is_free_mode:
        if face_normal:
            vector_grosor = normalize_vector(face_normal)
            if not vector_grosor:
                vector_grosor = get_view_plane_normal(coord_input)
        else:
            vector_grosor = get_view_plane_normal(coord_input)

        width_direction = cross_product(line_direction, vector_grosor)
        width_direction = normalize_vector(width_direction) or AllplanGeo.Vector3D(
            0.0, 1.0, 0.0
        )

        if abs(rotation_deg) > 1e-6:
            rotation_rad = math.radians(rotation_deg)
            width_direction = rotate_vector_around_axis(
                width_direction, line_direction, rotation_rad
            )
            width_direction = normalize_vector(width_direction) or width_direction

        width_handle_point = AllplanGeo.Point3D(
            midpoint.X + width_direction.X * (width_value / 2.0),
            midpoint.Y + width_direction.Y * (width_value / 2.0),
            midpoint.Z + width_direction.Z * (width_value / 2.0),
        )

        handle_list.append(
            HandleProperties(
                "AnchoHandle",
                width_handle_point,
                midpoint,
                [
                    HandleParameterData(
                        "Ancho",
                        HandleParameterType.VECTOR_DISTANCE,
                        distance_factor=2.0,
                        dir_vector=width_direction,
                    )
                ],
                HandleDirection.VECTOR_DIR,
                dir_vector=width_direction,
            )
        )
    else:
        if handle_plane and y_dir:
            width_direction = normalize_vector(y_dir) or AllplanGeo.Vector3D(
                0.0, 1.0, 0.0
            )
            width_handle_point = AllplanGeo.Point3D(
                midpoint.X + width_direction.X * (width_value / 2.0),
                midpoint.Y + width_direction.Y * (width_value / 2.0),
                midpoint.Z + width_direction.Z * (width_value / 2.0),
            )

            handle_list.append(
                HandleProperties(
                    "AnchoHandle",
                    width_handle_point,
                    midpoint,
                    [
                        HandleParameterData(
                            "Ancho",
                            HandleParameterType.VECTOR_DISTANCE,
                            distance_factor=2.0,
                            dir_vector=width_direction,
                        )
                    ],
                    HandleDirection.PLANE_DIR,
                    plane=handle_plane,
                    dir_vector=width_direction,
                )
            )
        else:
            normal_vector = normalize_vector(face_normal) if face_normal else None
            if not normal_vector and hasattr(build_ele, "CaraNormalX"):
                normal_vector = normalize_vector(
                    AllplanGeo.Vector3D(
                        getattr(build_ele.CaraNormalX, "value", 0.0),
                        getattr(build_ele.CaraNormalY, "value", 0.0),
                        getattr(build_ele.CaraNormalZ, "value", 1.0),
                    )
                )
            normal_vector = normal_vector or AllplanGeo.Vector3D(0.0, 0.0, 1.0)
            width_direction = normalize_vector(
                cross_product(line_direction, normal_vector)
            ) or AllplanGeo.Vector3D(0.0, 1.0, 0.0)

            width_handle_point = AllplanGeo.Point3D(
                midpoint.X + width_direction.X * (width_value / 2.0),
                midpoint.Y + width_direction.Y * (width_value / 2.0),
                midpoint.Z + width_direction.Z * (width_value / 2.0),
            )

            handle_list.append(
                HandleProperties(
                    "AnchoHandle",
                    width_handle_point,
                    midpoint,
                    [
                        HandleParameterData(
                            "Ancho",
                            HandleParameterType.VECTOR_DISTANCE,
                            distance_factor=2.0,
                            dir_vector=width_direction,
                        )
                    ],
                    HandleDirection.VECTOR_DIR,
                    dir_vector=width_direction,
                )
            )

    if is_free_mode:
        handle_list.append(
            HandleProperties(
                "DesplazamientoHandle",
                midpoint,
                midpoint,
                [
                    HandleParameterData("PuntoInicial", HandleParameterType.POINT),
                    HandleParameterData("PuntoFinal", HandleParameterType.POINT),
                ],
                HandleDirection.XYZ_DIR,
                dir_vector=None,
            )
        )

    return handle_list


def get_wall_placement_matrix(wall_element) -> AllplanGeo.Matrix3D | None:
    """Obtiene la matriz de transformacion del muro.

    Args:
        wall_element: Elemento del muro

    Returns:
        Matriz de transformacion o None si no se puede obtener
    """
    if not wall_element or wall_element.IsNull():
        return None

    placement_matrix = None
    methods_to_try = [
        "GetPlacementMatrix",
        "GetTransformationMatrix",
        "GetModelMatrix",
        "GetWorldMatrix",
        "GetMatrix",
    ]

    for method_name in methods_to_try:
        if hasattr(wall_element, method_name):
            try:
                method = getattr(wall_element, method_name)
                if callable(method):
                    result = method()
                    if isinstance(result, AllplanGeo.Matrix3D):
                        placement_matrix = result
                        break
            except Exception:
                continue

    if placement_matrix is None:
        try:
            success, matrix = AllplanBaseElements.PythonPartService.GetPlacementMatrix(
                wall_element
            )
            if success and isinstance(matrix, AllplanGeo.Matrix3D):
                placement_matrix = matrix
        except Exception:
            pass

    return placement_matrix


class WallSelectResult:
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None
        self.is_selected = False


class WallSelectInteractor(BaseScriptObjectInteractor):

    def __init__(
        self,
        result: WallSelectResult,
        prompt_msg: str = "Seleccione el elemento (cara)",
        script_object=None,
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg
        self.script_object = script_object

        self.sel_query = build_host_element_selection_query()
        self.element_filter = AllplanIFW.ElementSelectFilterSetting(
            self.sel_query, True
        )

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        if self.script_object:
            self.script_object._saved_coord_input = coord_input
        if coord_input:
            coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert(self.prompt_msg)
            )

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: Any
    ) -> bool:
        if not self.coord_input:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            self.coord_input.SelectElement(
                mouse_msg, pnt, msg_info, True, True, True, self.element_filter
            )
            return True

        self.coord_input.SelectElement(
            mouse_msg, pnt, msg_info, True, True, True, self.element_filter
        )
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        is_selected, face_polygon, intersect_result = self._select_face(
            selected_element, pnt
        )

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())
        if is_selected:
            self._store_face_result(face_polygon, intersect_result, pnt)
        self.result.is_selected = True

        return False

    def _select_face(self, element, pnt):
        try:
            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    element,
                    pnt,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )
            if is_selected:
                return is_selected, face_polygon, intersect_result
        except Exception:
            pass

        try:
            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    element,
                    pnt,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )
            return is_selected, face_polygon, intersect_result
        except Exception:
            pass

        return False, None, None

    def _store_face_result(self, face_polygon, intersect_result, pnt):
        if intersect_result and hasattr(intersect_result, "IntersectionPoint"):
            face_normal = intersect_result.FaceNv
            face_point_approx = intersect_result.IntersectionPoint
            ray_origin, ray_direction = get_view_ray_from_mouse(self.coord_input, pnt)
            if ray_origin and ray_direction and face_normal:
                real_intersection = intersect_ray_with_face_plane(
                    ray_origin, ray_direction, face_point_approx, face_normal
                )
                self.result.face_point = (
                    real_intersection if real_intersection else face_point_approx
                )
            else:
                self.result.face_point = face_point_approx
            self.result.face_normal = face_normal
        self.result.face_polygon = face_polygon

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


class SolidFaceSelectResult:
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None
        self.is_selected = False


class SolidFaceSelectInteractor(BaseScriptObjectInteractor):

    def __init__(
        self,
        result: SolidFaceSelectResult,
        prompt_msg: str = "Seleccione la cara del elemento",
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg

        self.sel_query = build_host_element_selection_query()
        self.element_filter = AllplanIFW.ElementSelectFilterSetting(
            self.sel_query, True
        )

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: Any
    ) -> bool:
        self.coord_input.SelectElement(
            mouse_msg, pnt, msg_info, True, True, True, self.element_filter
        )
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        is_selected, face_polygon, intersect_result = self._select_face(
            selected_element, pnt
        )

        if not is_selected:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            if intersect_result and hasattr(intersect_result, "IntersectionPoint"):
                self._draw_face_normal_preview(intersect_result)
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())

        if intersect_result and hasattr(intersect_result, "IntersectionPoint"):
            face_normal = intersect_result.FaceNv
            face_point_approx = intersect_result.IntersectionPoint

            mouse_world_approx = None
            if self.coord_input:
                try:
                    mouse_world_approx = self.coord_input.GetWorldPoint(pnt)
                except Exception:
                    pass

            ray_origin, ray_direction = get_view_ray_from_mouse(self.coord_input, pnt)
            if ray_origin and ray_direction and face_normal:
                real_intersection = intersect_ray_with_face_plane(
                    ray_origin, ray_direction, face_point_approx, face_normal
                )
                if real_intersection:
                    self.result.face_point = real_intersection
                else:
                    self.result.face_point = face_point_approx
            else:
                self.result.face_point = face_point_approx

            self.result.face_normal = face_normal
        else:
            self.result.face_point = AllplanGeo.Point3D()
            self.result.face_normal = AllplanGeo.Vector3D(0, 0, 1)

        self.result.face_polygon = face_polygon
        self.result.is_selected = True

        return False

    def _select_face(self, element, pnt):
        try:
            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    element,
                    pnt,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )
            if is_selected:
                return is_selected, face_polygon, intersect_result
        except Exception:
            pass

        try:
            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    element,
                    pnt,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )
            return is_selected, face_polygon, intersect_result
        except Exception:
            pass

        return False, None, None

    def _draw_face_normal_preview(self, intersect_result):
        """Dibuja un preview de la normal de la cara."""
        point_at_face = intersect_result.IntersectionPoint
        normal = intersect_result.FaceNv

        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()

        ray = AllplanBasisElements.ModelElement3D(
            common_props, AllplanGeo.Line3D(point_at_face, point_at_face + normal * 500)
        )

        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            [ray],
            True,
            None,
        )

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


class NeoprenoSelectResult:
    """Resultado de seleccion de un PPG Neoprenos existente."""

    def __init__(self):
        self.element = None
        self.param_list: list = []
        self.input_point = None
        self.record_index = None
        self.is_selected = False


class ExistingNeoprenoSelectInteractor(BaseScriptObjectInteractor):
    """Selecciona un PPG Neoprenos del dibujo (clic en geometria o grupo)."""

    def __init__(
        self,
        result: NeoprenoSelectResult,
        prompt_msg: str = "Seleccione el neopreno (PPG) en el dibujo",
        owner=None,
    ):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg
        self.owner = owner

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: Any
    ) -> bool:
        if not self.coord_input or self.owner is None:
            return True

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, False, False)

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        try:
            input_point = self.coord_input.GetInputPoint(
                mouse_msg, pnt, msg_info
            ).GetPoint()
        except Exception:
            input_point = None

        selected_element = self.coord_input.GetSelectedElement()
        if selected_element is None or selected_element.IsNull():
            if input_point is not None:
                pyp_element, param_list = self.owner._resolve_neopreno_ppg_from_adapter(
                    None, input_point
                )
                if pyp_element is not None:
                    record_index = (
                        self.owner._find_created_neopreno_record_index_for_element(
                            pyp_element
                        )
                    )
                    if record_index is None:
                        self.owner._warn_neopreno_from_other_execution()
                        return True
                    record_index, _ = (
                        self.owner._register_or_refresh_neopreno_record_from_ppg(
                            pyp_element, param_list, input_point=input_point
                        )
                    )
                    self._finish_selection(
                        pyp_element, param_list, record_index, input_point
                    )
                    return False
            print(
                "[SELECT][NEOPRENO] Clic sin elemento: seleccione la geometria del neopreno"
            )
            return True

        pyp_element, param_list = self.owner._resolve_neopreno_ppg_from_adapter(
            selected_element, input_point
        )
        if pyp_element is None:
            print("[SELECT][NEOPRENO] No se identifico el PPG Neoprenos en el dibujo")
            return True

        fresh_params = self.owner._read_neopreno_param_list_from_element(pyp_element)
        if fresh_params:
            param_list = fresh_params

        record_index = self.owner._find_created_neopreno_record_index_for_element(
            pyp_element
        )
        if record_index is None:
            self.owner._warn_neopreno_from_other_execution()
            return True

        record_index, _ = self.owner._register_or_refresh_neopreno_record_from_ppg(
            pyp_element, param_list, input_point=input_point
        )
        self._finish_selection(pyp_element, param_list, record_index, input_point)
        return False

    def _finish_selection(
        self, pyp_element, param_list, record_index, input_point
    ) -> None:
        self.result.element = pyp_element
        self.result.param_list = list(param_list) if param_list else []
        self.result.input_point = input_point
        self.result.record_index = record_index
        self.result.is_selected = True
        print(
            f"[SELECT][NEOPRENO] PPG seleccionado registro={record_index} "
            f"params={len(self.result.param_list)}"
        )

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


def create_script_object(
    build_ele: BuildingElement, script_object_data: BaseScriptObjectData
) -> BaseScriptObject:
    return NeoprenosScriptObject(build_ele, script_object_data)


class NeoprenosScriptObject(BaseScriptObject):

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)

        self.build_ele = build_ele
        self.interactor_state = STOPPED

        self.face_select_result = SolidFaceSelectResult()
        self.wall_select_result = WallSelectResult()
        self.line_result = LineInteractorResult()
        self.handles: list[HandleProperties] = []

        self.solid_info = None
        self.detected_wall = None
        self.detected_wall_guid = None
        self.wall_ifc_id = None
        self._unidentifiable_parent_warned = False
        self.parent_element = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None

        self.ref_face_element = None
        self.ref_face_polygon = None

        self._saved_coord_input = self.coord_input if self.coord_input else None

        self.is_editing_existing = bool(
            hasattr(self.build_ele, "SavedState")
            and isinstance(self.build_ele.SavedState.value, str)
            and self.build_ele.SavedState.value.strip()
        )
        self._restored_from_saved_state = False
        self.is_free_mode = self._get_free_mode()
        self.needs_auto_update = False
        self._pending_create_edit = False

        self.is_modification_mode = self.modification_ele_list.is_modification_element()
        self.neopreno_select_result = NeoprenoSelectResult()
        self._inline_selected_neopreno_active = False
        self._inline_modification_ele_list = None
        self._inline_original_modification_mode = getattr(
            self, "is_modification_mode", False
        )
        self._inline_original_modification_ele_list = getattr(
            self, "modification_ele_list", None
        )
        self._created_neopreno_records: list[dict] = []
        self._neopreno_record_selected_index = None
        self._inline_last_execute_result = None

        self._set_allow_wall_change_palette_flag()

        if hasattr(self.build_ele, "SavedState"):
            ss = getattr(self.build_ele.SavedState, "value", None)
            if isinstance(ss, str) and ss.strip():
                self._restored_from_saved_state = self._deserialize_state_from_json(ss)
        if (
            not self._restored_from_saved_state
            and hasattr(self, "script_object_data")
            and self.script_object_data
        ):
            param_list_src = getattr(self.script_object_data, "param_list", None)
            if param_list_src:
                for p in param_list_src:
                    s = p.strip()
                    if s.startswith("SavedState = ") or s.startswith("SavedState="):
                        _, _, rest = p.partition("=")
                        val = rest.strip().rstrip("\n").strip()
                        if val:
                            try:
                                if (val.startswith("'") and val.endswith("'")) or (
                                    val.startswith('"') and val.endswith('"')
                                ):
                                    val = ast.literal_eval(val)
                            except Exception:
                                pass
                            if isinstance(val, str) and val:
                                self._restored_from_saved_state = (
                                    self._deserialize_state_from_json(val)
                                )
                            break
        if (
            not self._restored_from_saved_state
            and self.is_modification_mode
            and self._restore_state_from_modification_element()
        ):
            self._restored_from_saved_state = True

        if self.is_modification_mode:
            self.is_editing_existing = True
            self._ensure_line_result_from_build_ele_for_modify()
            self._apply_face_context_from_build_ele_only()
        elif self.is_editing_existing:
            self._load_saved_connection_info()
        if self._restored_from_saved_state:
            self.is_free_mode = self._get_free_mode()

        neo_log(
            f"init version={NEOPRENOS_SCRIPT_VERSION} modify={self.is_modification_mode}"
        )
        self._update_parameter_visibility()

    def _set_allow_wall_change_palette_flag(self) -> None:
        """Muestra el boton solo durante una ejecucion nueva, no al reentrar en EDIT."""
        if not hasattr(self.build_ele, "PermitirCambiarMuro"):
            return
        allow = not bool(getattr(self, "is_modification_mode", False))
        if getattr(self, "_restored_from_saved_state", False):
            allow = False
        try:
            self.build_ele.PermitirCambiarMuro.value = allow
        except Exception:
            pass

    def _get_free_mode(self) -> bool:
        if hasattr(self.build_ele, "neopreno_libre"):
            val = self.build_ele.neopreno_libre.value
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ("true", "1", "yes")
            return bool(val)
        return False

    def _get_allow_line_pickup(self) -> bool:
        """Siempre activo: tomar linea completa del muro (sin control en paleta)."""
        return True

    def _resolve_host_pmp_pare(self) -> str:
        """Obtiene pmp_pare desde IFC ID (683) del elemento host seleccionado."""
        if getattr(self, "wall_ifc_id", None):
            cached = normalize_pmp_pare_value(self.wall_ifc_id)
            if cached:
                return cached

        host_candidates: list = []
        if getattr(self, "ref_face_element", None):
            host_candidates.append(self.ref_face_element)
        if getattr(self, "detected_wall", None):
            host_candidates.append(self.detected_wall)
        solid_info = getattr(self, "solid_info", None)
        if isinstance(solid_info, dict) and solid_info.get("element"):
            host_candidates.append(solid_info["element"])
        if (
            getattr(self, "wall_select_result", None)
            and self.wall_select_result.element
        ):
            host_candidates.append(self.wall_select_result.element)
        if (
            getattr(self, "face_select_result", None)
            and self.face_select_result.element
        ):
            host_candidates.append(self.face_select_result.element)

        seen_guids: set[str] = set()
        had_host = False
        for element in host_candidates:
            if not element or (hasattr(element, "IsNull") and element.IsNull()):
                continue
            had_host = True
            try:
                element_guid = str(element.GetModelElementUUID())
                if element_guid in seen_guids:
                    continue
                seen_guids.add(element_guid)
            except Exception:
                pass
            ifc_id = get_element_ifc_id(element, try_parent=True)
            if ifc_id:
                self.wall_ifc_id = normalize_pmp_pare_value(ifc_id)
                return self.wall_ifc_id

        if had_host:
            self._warn_unidentifiable_parent_element()
        return ""

    def _resolve_host_pmp_pare_name(self) -> str:
        """Obtiene un nombre/material legible del elemento host seleccionado."""
        if getattr(self, "wall_material_name", None):
            cached = normalize_pmp_pare_value(self.wall_material_name)
            if cached:
                return cached

        host_candidates: list = []
        if getattr(self, "ref_face_element", None):
            host_candidates.append(self.ref_face_element)
        if getattr(self, "detected_wall", None):
            host_candidates.append(self.detected_wall)
        solid_info = getattr(self, "solid_info", None)
        if isinstance(solid_info, dict) and solid_info.get("element"):
            host_candidates.append(solid_info["element"])
        if (
            getattr(self, "wall_select_result", None)
            and self.wall_select_result.element
        ):
            host_candidates.append(self.wall_select_result.element)
        if (
            getattr(self, "face_select_result", None)
            and self.face_select_result.element
        ):
            host_candidates.append(self.face_select_result.element)

        seen_guids: set[str] = set()
        for element in host_candidates:
            if not element or (hasattr(element, "IsNull") and element.IsNull()):
                continue
            try:
                element_guid = str(element.GetModelElementUUID())
                if element_guid in seen_guids:
                    continue
                seen_guids.add(element_guid)
            except Exception:
                pass

            wall_name = get_wall_material_name(element)
            if wall_name:
                self.wall_material_name = normalize_pmp_pare_value(wall_name)
                return self.wall_material_name

        return ""

    def _warn_unidentifiable_parent_element(self) -> None:
        """Aviso al usuario: el elemento padre no tiene IFC ID identificable."""
        if getattr(self, "_unidentifiable_parent_warned", False):
            return
        self._unidentifiable_parent_warned = True
        neo_log(
            "_warn_unidentifiable_parent_element: host sin IFC ID (683) -> PMP_PARE vacío"
        )
        try:
            AllplanUtil.ShowMessageBox(
                NEOPRENO_PARENT_NOT_IDENTIFIABLE_MSG, AllplanUtil.MB_OK
            )
        except Exception as exc:
            print(f"[NEOPRENOS] No se pudo mostrar el cuadro de aviso: {exc}")
            print(NEOPRENO_PARENT_NOT_IDENTIFIABLE_MSG)

    def _init_pmp_attribute_ids(self) -> None:
        """Resuelve IDs de PMP_PARE y PMP_WALL_ID."""
        doc = getattr(self, "document", None)
        if not doc:
            self.attr_pmp_pare_id = 0
            self.attr_pmp_wall_id = 0
            return
        self.attr_pmp_pare_id = resolve_attribute_id(doc, "pmp_pare", "PMP_PARE")
        self.attr_pmp_wall_id = resolve_attribute_id(
            doc,
            "PMP_WALL_ID",
        )
        if self.attr_pmp_pare_id <= 0 or self.attr_pmp_wall_id <= 0:
            neo_log(
                "_init_pmp_attribute_ids: "
                f"PMP_PARE={self.attr_pmp_pare_id} PMP_WALL_ID={self.attr_pmp_wall_id}"
            )
        else:
            neo_log(
                "_init_pmp_attribute_ids: "
                f"PMP_PARE={self.attr_pmp_pare_id} PMP_WALL_ID={self.attr_pmp_wall_id}"
            )

    def _update_parameter_visibility(self):
        self._set_allow_wall_change_palette_flag()

    def _serialize_state_to_json(self) -> str:
        """
        Serializa el estado actual de build_ele a JSON para guardar en SavedState.
        Incluye "v": 1 para poder migrar formato más adelante.
        """
        try:
            p0 = (
                self.build_ele.PuntoInicial.value
                if hasattr(self.build_ele, "PuntoInicial")
                else None
            )
            p1 = (
                self.build_ele.PuntoFinal.value
                if hasattr(self.build_ele, "PuntoFinal")
                else None
            )
            if p0 is None or p1 is None:
                return ""

            grosor = None
            if (
                hasattr(self.build_ele, "GrosorSeleccionado")
                and self.build_ele.GrosorSeleccionado.value is not None
            ):
                grosor = float(self.build_ele.GrosorSeleccionado.value)
            ancho = None
            if (
                hasattr(self.build_ele, "Ancho")
                and self.build_ele.Ancho.value is not None
            ):
                try:
                    ancho = float(self.build_ele.Ancho.value)
                except (TypeError, ValueError):
                    ancho = get_neopreno_width(self.build_ele)
            else:
                ancho = get_neopreno_width(self.build_ele)

            libre = bool(getattr(self, "is_free_mode", False))
            if hasattr(self.build_ele, "neopreno_libre"):
                val = self.build_ele.neopreno_libre.value
                if isinstance(val, bool):
                    libre = val
                elif isinstance(val, str):
                    libre = val.lower() in ("true", "1", "yes")
                else:
                    libre = bool(val)

            rot = 0.0
            if hasattr(self.build_ele, "RotacionManual"):
                rv = self.build_ele.RotacionManual.value
                rot = (
                    rv.GetDeg()
                    if hasattr(rv, "GetDeg")
                    else float(rv) if rv is not None else 0.0
                )

            invertido = False
            if (
                hasattr(self.build_ele, "InvertirGrosor")
                and self.build_ele.InvertirGrosor.value is not None
            ):
                val = self.build_ele.InvertirGrosor.value
                invertido = (
                    bool(val)
                    if isinstance(val, bool)
                    else str(val).lower() in ("true", "1", "yes")
                )

            pmp_pare = ""
            if (
                hasattr(self.build_ele, "pmp_pare")
                and self.build_ele.pmp_pare.value is not None
            ):
                pmp_pare = normalize_pmp_pare_value(self.build_ele.pmp_pare.value)

            pmp_pare_name = ""
            if (
                hasattr(self.build_ele, "pmp_pare_name")
                and self.build_ele.pmp_pare_name.value is not None
            ):
                pmp_pare_name = normalize_pmp_pare_value(
                    self.build_ele.pmp_pare_name.value
                )

            layer = -1
            if (
                hasattr(self.build_ele, "Layer")
                and self.build_ele.Layer.value is not None
            ):
                try:
                    layer = int(self.build_ele.Layer.value)
                except (TypeError, ValueError):
                    layer = -1

            state = {
                "v": 1,
                "p0": [p0.X, p0.Y, p0.Z],
                "p1": [p1.X, p1.Y, p1.Z],
                "ancho": ancho,
                "grosor": grosor,
                "libre": libre,
                "pickup_linea": self._get_allow_line_pickup(),
                "rot": rot,
                "invertido": invertido,
                "pmp_pare": normalize_pmp_pare_value(pmp_pare),
                "pmp_pare_name": normalize_pmp_pare_value(pmp_pare_name),
                "layer": layer,
            }
            return json.dumps(state, separators=(",", ":"))
        except Exception as e:
            import traceback

            return ""

    def _deserialize_state_from_json(self, json_str: str) -> bool:
        """
        Deserializa SavedState desde JSON y aplica los valores a build_ele (precarga real).
        Devuelve True si se restauró correctamente, False en caso contrario.
        """
        try:
            if not json_str or not str(json_str).strip():
                return False

            state = json.loads(json_str)

            p0 = state.get("p0")
            p1 = state.get("p1")
            if not p0 or not p1 or len(p0) != 3 or len(p1) != 3:
                return False

            self._restored_state = state

            if hasattr(self.build_ele, "PuntoInicial"):
                self.build_ele.PuntoInicial.value = AllplanGeo.Point3D(
                    float(p0[0]), float(p0[1]), float(p0[2])
                )
            if hasattr(self.build_ele, "PuntoFinal"):
                self.build_ele.PuntoFinal.value = AllplanGeo.Point3D(
                    float(p1[0]), float(p1[1]), float(p1[2])
                )

            if (
                "ancho" in state
                and state["ancho"] is not None
                and hasattr(self.build_ele, "Ancho")
            ):
                self.build_ele.Ancho.value = float(state["ancho"])

            if (
                "grosor" in state
                and state["grosor"] is not None
                and hasattr(self.build_ele, "GrosorSeleccionado")
            ):
                self.build_ele.GrosorSeleccionado.value = float(state["grosor"])

            if "libre" in state and hasattr(self.build_ele, "neopreno_libre"):
                self.build_ele.neopreno_libre.value = bool(state["libre"])

            if "pickup_linea" in state and hasattr(
                self.build_ele, "PermitirPickUpLinea"
            ):
                self.build_ele.PermitirPickUpLinea.value = bool(state["pickup_linea"])

            if (
                "rot" in state
                and state["rot"] is not None
                and hasattr(self.build_ele, "RotacionManual")
            ):
                try:
                    self.build_ele.RotacionManual.value = float(state["rot"])
                except (TypeError, ValueError):
                    pass

            if "invertido" in state and hasattr(self.build_ele, "InvertirGrosor"):
                self.build_ele.InvertirGrosor.value = bool(state["invertido"])

            if "pmp_pare" in state and hasattr(self.build_ele, "pmp_pare"):
                self.build_ele.pmp_pare.value = normalize_pmp_pare_value(
                    state["pmp_pare"]
                )
            if "pmp_pare_name" in state and hasattr(self.build_ele, "pmp_pare_name"):
                self.build_ele.pmp_pare_name.value = normalize_pmp_pare_value(
                    state["pmp_pare_name"]
                )

            if (
                "layer" in state
                and state["layer"] is not None
                and hasattr(self.build_ele, "Layer")
            ):
                try:
                    self.build_ele.Layer.value = int(state["layer"])
                except (TypeError, ValueError):
                    pass

            return True

        except Exception as e:
            return False

    def _restore_saved_state(self) -> bool:
        """
        Restaura el estado desde build_ele.SavedState (se llama al entrar en EDIT).
        Primero intenta desde build_ele.SavedState; si hay JSON válido, aplica a build_ele.
        Devuelve True si se restauró correctamente.
        """
        try:
            if hasattr(self.build_ele, "SavedState") and hasattr(
                self.build_ele.SavedState, "value"
            ):
                ss = self.build_ele.SavedState.value
                if isinstance(ss, str) and ss.strip():
                    return self._deserialize_state_from_json(ss)
        except Exception as e:
            return False

    def _restore_state_from_modification_element(self) -> bool:
        """Fallback EDIT: lee parametros del PythonPart real si build_ele llega incompleto."""
        try:
            modification_list = getattr(self, "modification_ele_list", None)
            if modification_list is None:
                return False
            adapter = modification_list.get_base_element_adapter(self.document)
            if adapter is None or adapter.IsNull():
                return False

            param_list = self._read_neopreno_param_list_from_element(adapter)
            if not param_list:
                return False

            params = parse_params_list_to_dict(param_list)
            saved_state = str(params.get("SavedState", "") or "").strip()
            if saved_state and self._deserialize_state_from_json(saved_state):
                if hasattr(self.build_ele, "SavedState"):
                    self.build_ele.SavedState.value = saved_state
                neo_log(
                    "_restore_state_from_modification_element: SavedState restaurado desde PPG"
                )
                return True

            self._apply_param_list_to_build_ele(param_list)
            p0 = (
                getattr(self.build_ele.PuntoInicial, "value", None)
                if hasattr(self.build_ele, "PuntoInicial")
                else None
            )
            p1 = (
                getattr(self.build_ele.PuntoFinal, "value", None)
                if hasattr(self.build_ele, "PuntoFinal")
                else None
            )
            if p0 is not None and p1 is not None:
                line = AllplanGeo.Line3D(p0, p1)
                if _is_valid_line(line):
                    self.line_result.input_line = line
                    self._save_state_to_build_ele()
                    neo_log(
                        "_restore_state_from_modification_element: puntos restaurados desde PPG"
                    )
                    return True
        except Exception as exc:
            neo_log(f"_restore_state_from_modification_element: fallo {exc}")
        return False

    def _save_state_to_build_ele(self):
        """
        Guarda el estado actual serializado en build_ele.SavedState.
        Se llama justo antes de crear el grupo / antes del return final en CREATE y EDIT.
        """
        try:
            if hasattr(self.build_ele, "SavedState") and hasattr(
                self.build_ele.SavedState, "value"
            ):
                ss = self._serialize_state_to_json()
                if ss:
                    self.build_ele.SavedState.value = ss
        except Exception as e:
            pass

    def _read_group_params(self) -> dict:
        """
        Lee los parámetros del PythonPartGroup desde script_object_data.param_list.

        Returns:
            Diccionario con los parámetros parseados del grupo
        """
        if not hasattr(self, "script_object_data") or not self.script_object_data:
            return {}

        param_list = getattr(self.script_object_data, "param_list", None)
        if not param_list:
            return {}

        params = {}
        for p in param_list:
            try:
                if "=" in p:
                    key, val = p.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    params[key] = eval(val)
            except Exception as e:
                pass

        return params

    def _check_if_editing_existing(self) -> bool:
        if (
            hasattr(self.build_ele, "z_unique")
            and self.build_ele.z_unique.value > 0
            and hasattr(self.build_ele, "PuntoInicial")
            and hasattr(self.build_ele, "PuntoFinal")
            and self.build_ele.PuntoInicial.value is not None
            and self.build_ele.PuntoFinal.value is not None
        ):

            existing_line = AllplanGeo.Line3D(
                self.build_ele.PuntoInicial.value, self.build_ele.PuntoFinal.value
            )
            if AllplanGeo.CalcLength(existing_line) > 0.1:
                self.line_result.input_line = existing_line
                return True

        return False

    def _load_saved_connection_info(self):
        """Carga la informacion de conexion guardada cuando se esta editando."""
        if self.is_free_mode:
            if (
                hasattr(self.build_ele, "MuroConnection")
                and self.build_ele.MuroConnection.value
                and hasattr(self.build_ele.MuroConnection.value, "element")
                and self.build_ele.MuroConnection.value.element.IsValid()
            ):
                self.detected_wall = self.build_ele.MuroConnection.value.element
                self.detected_wall_guid = str(self.detected_wall.GetModelElementUUID())
            elif hasattr(self.build_ele, "MuroGUID") and self.build_ele.MuroGUID.value:
                self.detected_wall_guid = self.build_ele.MuroGUID.value
                try:
                    wall_guid = AllplanEleAdapter.GUID.FromString(
                        self.detected_wall_guid
                    )
                    self.detected_wall = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                        wall_guid, self.document
                    )
                    if self.detected_wall and not self.detected_wall.IsNull():
                        if hasattr(self.build_ele, "MuroConnection"):
                            self.build_ele.MuroConnection.value.element = (
                                self.detected_wall
                            )
                except Exception:
                    pass
            elif (
                hasattr(self.build_ele, "MuroConnection")
                and self.build_ele.MuroConnection.value.uuid
            ):
                self.detected_wall_guid = str(self.build_ele.MuroConnection.value.uuid)
        else:
            if (
                hasattr(self.build_ele, "SolidoGUID")
                and self.build_ele.SolidoGUID.value
            ):
                self.solid_info = {"guid": self.build_ele.SolidoGUID.value}
            elif (
                hasattr(self.build_ele, "SolidoConnection")
                and self.build_ele.SolidoConnection.value.uuid
            ):
                self.solid_info = {
                    "guid": str(self.build_ele.SolidoConnection.value.uuid)
                }

    def _get_face_local_system(self) -> dict[str, Any] | None:
        if not self.face_polygon or not self.face_normal:
            return None
        return calculate_local_coordinate_system(self.face_polygon, self.face_normal)

    def _clamp_point_to_face(
        self, point: AllplanGeo.Point3D, local_system: dict[str, Any] | None = None
    ) -> AllplanGeo.Point3D:
        if local_system is None:
            local_system = self._get_face_local_system()

        if not local_system:
            return point

        if self.face_point and self.face_normal:
            point = project_point_to_face_plane(
                point, self.face_point, self.face_normal
            )

        relative = calculate_relative_position(point, local_system)
        if not relative:
            return point

        u_clamped = min(max(relative["u"], 0.0), 1.0)
        v_clamped = min(max(relative["v"], 0.0), 1.0)

        clamped_point = calculate_position_from_uv(u_clamped, v_clamped, local_system)
        return clamped_point if clamped_point else point

    def _clamp_line_to_face(
        self, line: AllplanGeo.Line3D, local_system: dict[str, Any] | None = None
    ) -> tuple[AllplanGeo.Line3D, dict[str, Any] | None]:
        if local_system is None:
            local_system = self._get_face_local_system()

        if not local_system:
            return line, None

        start = self._clamp_point_to_face(line.StartPoint, local_system)
        end = self._clamp_point_to_face(line.EndPoint, local_system)

        return AllplanGeo.Line3D(start, end), local_system

    def _max_distance_to_face(
        self,
        origin: AllplanGeo.Point3D,
        direction: AllplanGeo.Vector3D,
        local_system: dict[str, Any],
    ) -> float:
        direction_norm = normalize_vector(direction)
        if not direction_norm:
            return 0.0

        far_point = AllplanGeo.Point3D(
            origin.X + direction_norm.X * MAX_HANDLE_DISTANCE,
            origin.Y + direction_norm.Y * MAX_HANDLE_DISTANCE,
            origin.Z + direction_norm.Z * MAX_HANDLE_DISTANCE,
        )

        clamped_point = self._clamp_point_to_face(far_point, local_system)
        return calc_distance_3d(origin, clamped_point)

    def _adjust_width_to_face(
        self, line: AllplanGeo.Line3D, local_system: dict[str, Any]
    ) -> float:
        current_width = get_neopreno_width(self.build_ele)

        midpoint = AllplanGeo.Point3D(
            (line.StartPoint.X + line.EndPoint.X) / 2.0,
            (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
            (line.StartPoint.Z + line.EndPoint.Z) / 2.0,
        )

        line_vector = AllplanGeo.Vector3D(
            line.EndPoint.X - line.StartPoint.X,
            line.EndPoint.Y - line.StartPoint.Y,
            line.EndPoint.Z - line.StartPoint.Z,
        )
        line_direction = normalize_vector(line_vector) or AllplanGeo.Vector3D(
            1.0, 0.0, 0.0
        )

        face_normal = normalize_vector(self.face_normal) if self.face_normal else None
        if not face_normal and local_system.get("axis_w"):
            face_normal = normalize_vector(local_system["axis_w"])
        if not face_normal:
            face_normal = AllplanGeo.Vector3D(0.0, 0.0, 1.0)

        width_direction = normalize_vector(cross_product(line_direction, face_normal))
        if not width_direction:
            axis_v = local_system.get("axis_v")
            width_direction = normalize_vector(axis_v) if axis_v else None
        if not width_direction:
            width_direction = AllplanGeo.Vector3D(0.0, 1.0, 0.0)

        max_plus = self._max_distance_to_face(midpoint, width_direction, local_system)
        max_minus = self._max_distance_to_face(
            midpoint,
            AllplanGeo.Vector3D(
                -width_direction.X, -width_direction.Y, -width_direction.Z
            ),
            local_system,
        )

        max_half_width = min(max_plus, max_minus)
        if max_half_width <= 0.0:
            return current_width

        desired_half_width = current_width / 2.0
        new_half_width = min(desired_half_width, max_half_width)

        min_half_width = min(MIN_WIDTH_HALF, max_half_width)
        new_half_width = max(new_half_width, min_half_width)

        new_width = new_half_width * 2.0

        if hasattr(self.build_ele, "Ancho"):
            self.build_ele.Ancho.value = new_width

        return new_width

    def _prepare_line(
        self,
        line: AllplanGeo.Line3D,
        adjust_width: bool = True,
        is_already_in_local_coords: bool = False,
    ) -> tuple[AllplanGeo.Line3D, dict[str, Any] | None]:
        """
        Prepara la linea para crear el neopreno.

        Args:
            line: Linea a preparar
            adjust_width: Si ajustar el ancho a la cara
            is_already_in_local_coords: Si True, la linea ya esta en sistema local del muro
                                       y NO debe reproyectarse
        """
        local_system = None

        if is_already_in_local_coords:
            if self.face_polygon and self.face_normal:
                local_system = self._get_face_local_system()

            if adjust_width and local_system:
                self._adjust_width_to_face(line, local_system)
            elif adjust_width:
                get_neopreno_width(self.build_ele)

            return line, local_system

        if self.face_normal and self.face_point:
            # line = apply_line_projection_or_translation(
            #     line, self.face_point, self.face_normal
            # )
            # line, local_system = self._clamp_line_to_face(line)
            line = line

        if not local_system and self.face_polygon and self.face_normal:
            local_system = self._get_face_local_system()

        if adjust_width:
            if local_system:
                self._adjust_width_to_face(line, local_system)
            else:
                get_neopreno_width(self.build_ele)

        return line, local_system

    def _get_solid_element(self):
        solid_element = None

        if hasattr(self.build_ele, "SolidoConnection"):
            conn = self.build_ele.SolidoConnection.value
            if hasattr(conn, "element") and conn.element.IsValid():
                solid_element = conn.element

        if not solid_element or solid_element.IsNull():
            if (
                hasattr(self.build_ele, "SolidoGUID")
                and self.build_ele.SolidoGUID.value
            ):
                solid_guid = AllplanEleAdapter.GUID.FromString(
                    self.build_ele.SolidoGUID.value
                )
                solid_element = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                    solid_guid, self.document
                )

        return solid_element

    def _get_stored_normal(self):
        return AllplanGeo.Vector3D(
            (
                self.build_ele.CaraNormalX.value
                if hasattr(self.build_ele, "CaraNormalX")
                else 0
            ),
            (
                self.build_ele.CaraNormalY.value
                if hasattr(self.build_ele, "CaraNormalY")
                else 0
            ),
            (
                self.build_ele.CaraNormalZ.value
                if hasattr(self.build_ele, "CaraNormalZ")
                else 1
            ),
        )

    def _get_stored_point(self):
        return AllplanGeo.Point3D(
            (
                self.build_ele.PuntoClicX.value
                if hasattr(self.build_ele, "PuntoClicX")
                else 0
            ),
            (
                self.build_ele.PuntoClicY.value
                if hasattr(self.build_ele, "PuntoClicY")
                else 0
            ),
            (
                self.build_ele.PuntoClicZ.value
                if hasattr(self.build_ele, "PuntoClicZ")
                else 0
            ),
        )

    def _find_face_index(
        self, solid_element, selected_face_polygon, selected_face_normal=None
    ):
        """Encuentra el indice de una cara seleccionada comparandola con todas las caras del solido.

        Args:
            solid_element: Elemento solido
            selected_face_polygon: Poligono de la cara seleccionada
            selected_face_normal: Normal de la cara seleccionada (CRITICO para distinguir caras opuestas)

        Returns:
            face_index (int) o None si no se encuentra
        """
        try:
            solid_geo = solid_element.GetModelGeometry()
            if not solid_geo:
                solid_geo = solid_element.GetGeometry()

            if isinstance(solid_geo, AllplanGeo.BRep3D):
                error, solid_geo = AllplanGeo.CreatePolyhedron(solid_geo)
                if error != AllplanGeo.eGeometryErrorCode.eOK:
                    return None

            if not solid_geo or not isinstance(solid_geo, AllplanGeo.Polyhedron3D):
                return None

            result = AllplanGeo.CalcMinMax(selected_face_polygon)
            if isinstance(result, tuple):
                minmax, _ = result
            else:
                minmax = result

            selected_center = AllplanGeo.Point3D(
                (minmax.Min.X + minmax.Max.X) / 2.0,
                (minmax.Min.Y + minmax.Max.Y) / 2.0,
                (minmax.Min.Z + minmax.Max.Z) / 2.0,
            )

            selected_normal = None
            if selected_face_polygon.Count() >= 3:
                p0 = selected_face_polygon.GetPoint(0)
                p1 = selected_face_polygon.GetPoint(1)
                p2 = selected_face_polygon.GetPoint(2)

                v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
                v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

                selected_normal = AllplanGeo.Vector3D(v1)
                selected_normal.CrossProduct(v2)
                selected_normal = normalize_vector(selected_normal)

            faces_count = solid_geo.GetFacesCount()
            candidates = []

            for i in range(faces_count):
                face = solid_geo.GetFace(i)
                success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(
                    solid_geo, face
                )

                if not success or len(face_points) < 3:
                    continue

                points_list = [face_points[j] for j in range(len(face_points))]
                face_polygon = AllplanGeo.Polygon3D(points_list)

                if face_polygon.Count() < 3:
                    continue

                result = AllplanGeo.CalcMinMax(face_polygon)
                if isinstance(result, tuple):
                    minmax, _ = result
                else:
                    minmax = result

                face_center = AllplanGeo.Point3D(
                    (minmax.Min.X + minmax.Max.X) / 2.0,
                    (minmax.Min.Y + minmax.Max.Y) / 2.0,
                    (minmax.Min.Z + minmax.Max.Z) / 2.0,
                )

                distance = calc_distance_3d(selected_center, face_center)

                p0 = face_polygon.GetPoint(0)
                p1 = face_polygon.GetPoint(1)
                p2 = face_polygon.GetPoint(2)

                v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
                v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

                face_normal = AllplanGeo.Vector3D(v1)
                face_normal.CrossProduct(v2)
                face_normal_normalized = normalize_vector(face_normal)

                dot = 0.0
                if selected_normal:
                    dot = abs(face_normal_normalized.DotProduct(selected_normal))

                if distance < 500.0:
                    candidates.append(
                        {
                            "index": i,
                            "distance": distance,
                            "dot": dot,
                            "center": face_center,
                        }
                    )

            if selected_normal:
                candidates.sort(key=lambda x: (-x["dot"], x["distance"]))
                for c in candidates:
                    if c["dot"] > 0.7:
                        return c["index"]
            else:
                candidates.sort(key=lambda x: x["distance"])
                if candidates and candidates[0]["distance"] < 100.0:
                    return candidates[0]["index"]

            return None

        except Exception:
            return None

    def _get_face_by_index(self, solid_element, face_index):
        """Obtiene una cara especifica del solido por su indice.

        Returns:
            (success, face_polygon, face_normal) tuple
        """
        try:
            solid_geo = solid_element.GetModelGeometry()
            if not solid_geo:
                solid_geo = solid_element.GetGeometry()

            if isinstance(solid_geo, AllplanGeo.BRep3D):
                error, solid_geo = AllplanGeo.CreatePolyhedron(solid_geo)
                if error != AllplanGeo.eGeometryErrorCode.eOK:
                    return False, None, None

            if not solid_geo or not isinstance(solid_geo, AllplanGeo.Polyhedron3D):
                return False, None, None

            faces_count = solid_geo.GetFacesCount()
            if face_index < 0 or face_index >= faces_count:
                return False, None, None

            face = solid_geo.GetFace(face_index)
            success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(
                solid_geo, face
            )

            if not success or len(face_points) < 3:
                return False, None, None

            points_list = [face_points[j] for j in range(len(face_points))]
            face_polygon = AllplanGeo.Polygon3D(points_list)

            if face_polygon.Count() < 3:
                return False, None, None

            p0 = face_polygon.GetPoint(0)
            p1 = face_polygon.GetPoint(1)
            p2 = face_polygon.GetPoint(2)

            v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
            v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

            face_normal = AllplanGeo.Vector3D(v1)
            face_normal.CrossProduct(v2)
            face_normal.Normalize()

            return True, face_polygon, face_normal

        except Exception:
            return False, None, None

    def _find_face_on_solid(self, solid_element, stored_normal, stored_point):
        """Encuentra la cara del solido que coincide con la normal guardada.

        DEPRECADO: Esta funcion es un fallback. Se debe usar _get_face_by_index() cuando sea posible.
        """
        try:
            solid_geo = solid_element.GetModelGeometry()
            if not solid_geo:
                solid_geo = solid_element.GetGeometry()

            if isinstance(solid_geo, AllplanGeo.BRep3D):
                error, solid_geo = AllplanGeo.CreatePolyhedron(solid_geo)
                if error != AllplanGeo.eGeometryErrorCode.eOK:
                    solid_geo = None

            if not solid_geo or not isinstance(solid_geo, AllplanGeo.Polyhedron3D):
                return self._fallback_face_selection(solid_element)

            stored_normal_normalized = AllplanGeo.Vector3D(stored_normal)
            stored_normal_normalized.Normalize()

            candidate_faces = []

            faces_count = solid_geo.GetFacesCount()

            for i in range(faces_count):
                face = solid_geo.GetFace(i)
                success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(
                    solid_geo, face
                )

                if not success or len(face_points) < 3:
                    continue

                points_list = [face_points[j] for j in range(len(face_points))]
                face_polygon = AllplanGeo.Polygon3D(points_list)

                if face_polygon.Count() >= 3:
                    p0 = face_polygon.GetPoint(0)
                    p1 = face_polygon.GetPoint(1)
                    p2 = face_polygon.GetPoint(2)

                    v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
                    v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

                    face_normal = AllplanGeo.Vector3D(v1)
                    face_normal.CrossProduct(v2)
                    face_normal.Normalize()

                    dot = face_normal.DotProduct(stored_normal_normalized)

                    if abs(dot) > 0.9:
                        result = AllplanGeo.CalcMinMax(face_polygon)
                        if isinstance(result, tuple):
                            minmax, _ = result
                        else:
                            minmax = result

                        face_center = AllplanGeo.Point3D(
                            (minmax.Min.X + minmax.Max.X) / 2.0,
                            (minmax.Min.Y + minmax.Max.Y) / 2.0,
                            (minmax.Min.Z + minmax.Max.Z) / 2.0,
                        )

                        distance_to_stored = calc_distance_3d(face_center, stored_point)

                        MAX_DISTANCE = 1000.0  # mm

                        if distance_to_stored <= MAX_DISTANCE:
                            candidate_faces.append(
                                {
                                    "index": i,
                                    "polygon": face_polygon,
                                    "normal": face_normal,
                                    "center": face_center,
                                    "dot": dot,
                                    "distance": distance_to_stored,
                                }
                            )
                        pass

            if not candidate_faces:
                return False, None, None

            candidate_faces.sort(key=lambda x: x["distance"])

            best_candidate = candidate_faces[0]
            face_polygon = best_candidate["polygon"]
            face_normal = best_candidate["normal"]
            face_center = best_candidate["center"]
            best_dot = best_candidate["dot"]

            if best_dot < 0:
                face_normal = AllplanGeo.Vector3D(
                    -face_normal.X, -face_normal.Y, -face_normal.Z
                )

            class FakeIntersectResult:
                def __init__(self, point, normal):
                    self.IntersectionPoint = point
                    self.FaceNv = normal

            intersect_result = FakeIntersectResult(face_center, face_normal)

            return True, face_polygon, intersect_result

        except Exception:
            return False, None, None

    def _fallback_face_selection(self, solid_element):
        try:
            min_max = AllplanGeo.MinMax3D()
            geo = solid_element.GetGeometry()

            if isinstance(geo, AllplanGeo.BRep3D):
                min_max = geo.GetMinMax()

            center = AllplanGeo.Point3D(
                (min_max.Min.X + min_max.Max.X) / 2.0,
                (min_max.Min.Y + min_max.Max.Y) / 2.0,
                (min_max.Min.Z + min_max.Max.Z) / 2.0,
            )
            center_2d = AllplanGeo.Point2D(center.X, center.Y)

            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    solid_element,
                    center_2d,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )

            if is_selected:
                return is_selected, face_polygon, intersect_result

            is_selected, face_polygon, intersect_result = (
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    solid_element,
                    center_2d,
                    True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(),
                    True,
                )
            )

            return is_selected, face_polygon, intersect_result

        except Exception:
            return False, None, None

    def start_input(self):
        """Inicia el input del script."""
        neo_log(
            "start_input: "
            f"editing={self.is_editing_existing} "
            f"saved_state={bool(getattr(getattr(self.build_ele, 'SavedState', None), 'value', ''))}"
        )

        if self.is_editing_existing:
            self.is_free_mode = self._get_free_mode()
            self._update_parameter_visibility()

            if self.line_result and self.line_result.input_line:
                self._process_line_input()

            self.interactor_state = STOPPED
            self.script_object_interactor = None
            return

        self.line_result = LineInteractorResult()
        self.wall_select_result = WallSelectResult()
        self.face_select_result = SolidFaceSelectResult()
        self.solid_info = None
        self.detected_wall = None
        self.detected_wall_guid = None
        self.wall_ifc_id = None
        self._unidentifiable_parent_warned = False
        self.parent_element = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None
        self.ref_face_element = None
        self.ref_face_polygon = None

        if hasattr(self.build_ele, "neopreno_libre"):
            val = self.build_ele.neopreno_libre.value
            if isinstance(val, bool):
                self.is_free_mode = val
            elif isinstance(val, str):
                self.is_free_mode = val.lower() in ("true", "1", "yes")
            else:
                self.is_free_mode = bool(val)
        else:
            self.is_free_mode = False

        self._update_parameter_visibility()

        if hasattr(self.build_ele, "neopreno_libre"):
            self.build_ele.neopreno_libre.value = bool(self.is_free_mode)

        neo_log(
            f"start_input: modo={'libre/muro' if self.is_free_mode else 'solido/cara'}"
        )

        if self.is_free_mode:
            self.wall_select_result = WallSelectResult()
            self.interactor_state = SELECTING_WALL
            neo_log("start_input: esperando seleccion de muro")
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el elemento (cara)",
                script_object=self,
            )
            coord_input_to_use = (
                self._saved_coord_input if self._saved_coord_input else self.coord_input
            )
            if coord_input_to_use:
                self.script_object_interactor.start_input(coord_input_to_use)
        else:
            self.interactor_state = SELECTING_SOLID
            neo_log("start_input: esperando seleccion de solido/cara")
            self.script_object_interactor = SolidFaceSelectInteractor(
                self.face_select_result,
            )
            coord_input_to_use = (
                self._saved_coord_input if self._saved_coord_input else self.coord_input
            )
            if coord_input_to_use:
                self.script_object_interactor.start_input(coord_input_to_use)

    def start_next_input(self):
        """Gestiona la transicion entre interactors."""
        neo_log(f"start_next_input: estado={self.interactor_state}")
        if self.interactor_state == SELECTING_WALL:
            if self.wall_select_result.is_selected:
                neo_log("start_next_input: muro seleccionado")
                self._process_wall_selection()
                self.interactor_state = SELECTING_LINE
                self._start_line_input()
            else:
                neo_log("start_next_input: muro no seleccionado, STOPPED")
                self.interactor_state = STOPPED
                self.script_object_interactor = None

        elif self.interactor_state == SELECTING_SOLID:
            if self.face_select_result.is_selected:
                neo_log("start_next_input: solido/cara seleccionado")
                self._process_solid_selection()
                self.interactor_state = SELECTING_LINE
                self._start_line_input()
            else:
                neo_log("start_next_input: solido/cara no seleccionado, STOPPED")
                self.interactor_state = STOPPED
                self.script_object_interactor = None

        elif self.interactor_state == SELECTING_LINE:
            if self.line_result.input_line:
                line = self.line_result.input_line
                neo_log(
                    "start_next_input: linea recibida "
                    f"p0=({line.StartPoint.X:.2f},{line.StartPoint.Y:.2f},{line.StartPoint.Z:.2f}) "
                    f"p1=({line.EndPoint.X:.2f},{line.EndPoint.Y:.2f},{line.EndPoint.Z:.2f})"
                )
                if self.script_object_interactor and hasattr(
                    self.script_object_interactor, "coord_input"
                ):
                    self._saved_coord_input = self.script_object_interactor.coord_input
                self._process_line_input()
                if not self.is_editing_existing:
                    if getattr(self, "_inline_selected_neopreno_active", False):
                        self._finish_inline_neopreno_edit()
                    coord_input = (
                        self.script_object_interactor.coord_input
                        if self.script_object_interactor
                        and hasattr(self.script_object_interactor, "coord_input")
                        else self._saved_coord_input
                    )
                    if self._materialize_current_neopreno(coord_input):
                        self.line_result = LineInteractorResult()
                        self._pending_create_edit = False
                        self.interactor_state = SELECTING_LINE
                        self._start_line_input()
                        if coord_input and self.script_object_interactor:
                            self.script_object_interactor.start_input(coord_input)
                        neo_log(
                            "start_next_input: neopreno materializado; siguiente linea"
                        )
                        return
                    self._pending_create_edit = True
                    self.interactor_state = STOPPED
                    self.script_object_interactor = None
                    neo_log(
                        "start_next_input: neopreno pendiente para ajuste de propiedades"
                    )
                    return
            else:
                neo_log("start_next_input: SELECTING_LINE sin input_line")

            # Fallback: si la creacion directa falla, dejamos que el framework
            # ejecute el PythonPart con el flujo estandar.
            self.script_object_interactor = None
            neo_log("start_next_input: linea procesada, fallback execute/framework")

        elif self.interactor_state == SELECTING_EXISTING_NEOPRENO:
            self.script_object_interactor = None
            if self.neopreno_select_result.is_selected:
                if self._enter_inline_neopreno_edit_mode(self.neopreno_select_result):
                    self.interactor_state = STOPPED
                else:
                    self._resume_neopreno_line_input(self._get_active_coord_input())
            else:
                self._resume_neopreno_line_input(self._get_active_coord_input())

    def _process_wall_selection(self):
        element_guid_str = self.wall_select_result.element_guid
        selected_element = self.wall_select_result.element
        neo_log(f"_process_wall_selection: guid={element_guid_str}")

        self.detected_wall = selected_element
        real_wall_guid = str(selected_element.GetModelElementUUID())
        self.detected_wall_guid = real_wall_guid
        self.face_point = self.wall_select_result.face_point
        self.face_normal = self.wall_select_result.face_normal
        self.face_polygon = self.wall_select_result.face_polygon
        self.ref_face_element = selected_element
        self.ref_face_polygon = self.face_polygon

        self.wall_ifc_id = get_element_ifc_id(selected_element, try_parent=True)
        neo_log(f"_process_wall_selection: ifc_id={self.wall_ifc_id or '(vacío)'}")
        if not self.wall_ifc_id:
            self._warn_unidentifiable_parent_element()

        if hasattr(self.build_ele, "MuroConnection"):
            self.build_ele.MuroConnection.value.element = selected_element
            if (
                str(self.build_ele.MuroConnection.value.uuid)
                == "00000000-0000-0000-0000-000000000000"
            ):
                try:
                    element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(
                        real_wall_guid
                    )
                    element_from_guid = AllplanBaseElements.ElementsService.GetElement(
                        element_guid
                    )
                    if element_from_guid and element_from_guid.IsValid():
                        self.build_ele.MuroConnection.value.element = element_from_guid
                except Exception:
                    pass
        if hasattr(self.build_ele, "MuroGUID"):
            self.build_ele.MuroGUID.value = real_wall_guid

        if self.face_normal and hasattr(self.build_ele, "CaraNormalX"):
            self.build_ele.CaraNormalX.value = self.face_normal.X
            self.build_ele.CaraNormalY.value = self.face_normal.Y
            self.build_ele.CaraNormalZ.value = self.face_normal.Z

        if self.face_point and hasattr(self.build_ele, "PuntoClicX"):
            self.build_ele.PuntoClicX.value = self.face_point.X
            self.build_ele.PuntoClicY.value = self.face_point.Y
            self.build_ele.PuntoClicZ.value = self.face_point.Z

    def _process_solid_selection(self):
        self.face_point = self.face_select_result.face_point
        self.face_normal = self.face_select_result.face_normal
        self.face_polygon = self.face_select_result.face_polygon

        element_guid_str = self.face_select_result.element_guid
        selected_element = self.face_select_result.element
        neo_log(f"_process_solid_selection: guid={element_guid_str}")

        self.ref_face_element = selected_element
        self.ref_face_polygon = self.face_polygon

        face_index = self._find_face_index(
            selected_element, self.face_polygon, self.face_normal
        )
        if face_index is not None and hasattr(self.build_ele, "CaraIndice"):
            self.build_ele.CaraIndice.value = face_index

        self.solid_info = {
            "guid": element_guid_str,
            "element": selected_element,
            "face_normal": self.face_normal,
            "face_center": self.face_point,
            "click_point": self.face_point,
            "face_index": face_index,
        }

        parent_element = None
        try:
            element_guid = (
                AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(
                    element_guid_str
                )
            )
            parent_element = AllplanBaseElements.ElementsService.GetElement(
                element_guid
            )

            if parent_element and parent_element.IsValid():
                self.parent_element = parent_element
            else:
                if hasattr(selected_element, "GetParentElement"):
                    try:
                        parent_element = selected_element.GetParentElement()
                        if parent_element and parent_element.IsValid():
                            self.parent_element = parent_element
                    except Exception:
                        pass
        except Exception:
            pass

        host_element = selected_element
        if self.parent_element and not self.parent_element.IsNull():
            host_element = self.parent_element

        self.wall_ifc_id = get_element_ifc_id(selected_element, try_parent=True)
        if not self.wall_ifc_id and self.parent_element:
            self.wall_ifc_id = get_element_ifc_id(self.parent_element, try_parent=False)

        if host_element and not host_element.IsNull():
            self.detected_wall = host_element
            self.detected_wall_guid = str(host_element.GetModelElementUUID())

        neo_log(
            f"_process_solid_selection: ifc_id={self.wall_ifc_id or '(vacío)'} "
            f"host_guid={self.detected_wall_guid or '(sin host)'}"
        )
        if not self.wall_ifc_id:
            self._warn_unidentifiable_parent_element()

        if hasattr(self.build_ele, "SolidoConnection"):
            self.build_ele.SolidoConnection.value.element = selected_element
            if (
                str(self.build_ele.SolidoConnection.value.uuid)
                == "00000000-0000-0000-0000-000000000000"
            ):
                try:
                    element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(
                        element_guid_str
                    )
                    element_from_guid = AllplanBaseElements.ElementsService.GetElement(
                        element_guid
                    )
                    if element_from_guid and element_from_guid.IsValid():
                        self.build_ele.SolidoConnection.value.element = (
                            element_from_guid
                        )
                except Exception:
                    pass

        if hasattr(self.build_ele, "SolidoGUID"):
            self.build_ele.SolidoGUID.value = element_guid_str

        if hasattr(self.build_ele, "CaraNormalX"):
            self.build_ele.CaraNormalX.value = self.face_normal.X
            self.build_ele.CaraNormalY.value = self.face_normal.Y
            self.build_ele.CaraNormalZ.value = self.face_normal.Z

        if hasattr(self.build_ele, "PuntoClicX"):
            self.build_ele.PuntoClicX.value = self.face_point.X
            self.build_ele.PuntoClicY.value = self.face_point.Y
            self.build_ele.PuntoClicZ.value = self.face_point.Z

    def _start_line_input(self):
        prompt_msg = (
            "Defina la linea para el neopreno - Posicionamiento libre"
            if self.is_free_mode
            else "Defina la linea para el neopreno (punto inicial)"
        )
        neo_log(f"_start_line_input: {prompt_msg}")

        coord_input_to_use = (
            self._saved_coord_input if self._saved_coord_input else self.coord_input
        )

        self.script_object_interactor = LineInteractor(
            self.line_result,
            True,
            prompt_msg,
            allow_pick_up=self._get_allow_line_pickup(),
            preview_function=self.draw_neopreno_preview,
        )

        if coord_input_to_use:
            try:
                self.script_object_interactor.start_input(coord_input_to_use)
            except Exception:
                pass
        self._draw_creation_indicator_preview(clear_before=True)

    def _process_line_input(self):
        if not (line := self.line_result.input_line):
            neo_log("_process_line_input: sin linea")
            return
        neo_log(
            "_process_line_input: inicio "
            f"len={AllplanGeo.CalcLength(line):.2f} "
            f"free={self.is_free_mode}"
        )

        if getattr(self, "_restored_from_saved_state", False):
            if hasattr(self.build_ele, "PuntoInicial") and hasattr(
                self.build_ele, "PuntoFinal"
            ):
                p0 = getattr(self.build_ele.PuntoInicial, "value", None)
                p1 = getattr(self.build_ele.PuntoFinal, "value", None)
                if p0 and p1:
                    self.line_result.input_line = AllplanGeo.Line3D(p0, p1)
                    line = self.line_result.input_line

        if self.is_free_mode and self.face_normal and self.face_point:
            line_to_process, local_system = self._prepare_line(line, adjust_width=False)
            if not local_system and self.face_polygon and self.face_normal:
                local_system = self._get_face_local_system()
        elif self.is_free_mode:
            line_to_process = line
            local_system = None
        else:
            line_to_process, local_system = self._prepare_line(line)
            if not local_system and self.face_polygon and self.face_normal:
                local_system = self._get_face_local_system()

        if not self._restored_from_saved_state:
            self.build_ele.PuntoInicial.value = line_to_process.StartPoint
            self.build_ele.PuntoFinal.value = line_to_process.EndPoint

        longitud = AllplanGeo.CalcLength(line_to_process)
        if hasattr(self.build_ele, "Longitud"):
            self.build_ele.Longitud.value = longitud

        if local_system and not self._restored_from_saved_state:
            line_center = AllplanGeo.Point3D(
                (line.StartPoint.X + line.EndPoint.X) / 2.0,
                (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
                (line.StartPoint.Z + line.EndPoint.Z) / 2.0,
            )

            rel_pos = calculate_relative_position(line_center, local_system)

            if rel_pos:
                if hasattr(self.build_ele, "PosicionRelativaU"):
                    self.build_ele.PosicionRelativaU.value = rel_pos["u"]
                if hasattr(self.build_ele, "PosicionRelativaV"):
                    self.build_ele.PosicionRelativaV.value = rel_pos["v"]
                if hasattr(self.build_ele, "DistanciaDesdeOrigen"):
                    self.build_ele.DistanciaDesdeOrigen.value = rel_pos[
                        "distance_from_origin"
                    ]

            rel_pos_start = calculate_relative_position(
                line_to_process.StartPoint, local_system
            )
            if rel_pos_start:
                if hasattr(self.build_ele, "PosicionRelativaU_Inicio"):
                    self.build_ele.PosicionRelativaU_Inicio.value = rel_pos_start["u"]
                if hasattr(self.build_ele, "PosicionRelativaV_Inicio"):
                    self.build_ele.PosicionRelativaV_Inicio.value = rel_pos_start["v"]

            rel_pos_end = calculate_relative_position(
                line_to_process.EndPoint, local_system
            )
            if rel_pos_end:
                if hasattr(self.build_ele, "PosicionRelativaU_Fin"):
                    self.build_ele.PosicionRelativaU_Fin.value = rel_pos_end["u"]
                if hasattr(self.build_ele, "PosicionRelativaV_Fin"):
                    self.build_ele.PosicionRelativaV_Fin.value = rel_pos_end["v"]

            line_vector = AllplanGeo.Vector3D(
                line_to_process.EndPoint.X - line_to_process.StartPoint.X,
                line_to_process.EndPoint.Y - line_to_process.StartPoint.Y,
                line_to_process.EndPoint.Z - line_to_process.StartPoint.Z,
            )
            line_vector.Normalize()

            axis_u = local_system["axis_u"]
            axis_v = local_system["axis_v"]

            line_u = line_vector.DotProduct(axis_u)
            line_v = line_vector.DotProduct(axis_v)

            if hasattr(self.build_ele, "LineaOrientacionU"):
                self.build_ele.LineaOrientacionU.value = line_u
            if hasattr(self.build_ele, "LineaOrientacionV"):
                self.build_ele.LineaOrientacionV.value = line_v

            if hasattr(self.build_ele, "AxisU_X"):
                self.build_ele.AxisU_X.value = axis_u.X
                self.build_ele.AxisU_Y.value = axis_u.Y
                self.build_ele.AxisU_Z.value = axis_u.Z
            if hasattr(self.build_ele, "AxisV_X"):
                self.build_ele.AxisV_X.value = axis_v.X
                self.build_ele.AxisV_Y.value = axis_v.Y
                self.build_ele.AxisV_Z.value = axis_v.Z

        self.line_result.input_line = line_to_process
        neo_log(
            "_process_line_input: linea procesada "
            f"len={AllplanGeo.CalcLength(line_to_process):.2f}"
        )

        coord_input = None
        if self.script_object_interactor and hasattr(
            self.script_object_interactor, "coord_input"
        ):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, "RotacionManual"):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, "GetDeg"):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            x_dir_handle, y_dir_handle, z_dir_handle = (
                build_face_local_axes_for_handles(
                    line_to_process.StartPoint,
                    line_to_process.EndPoint,
                    self.face_point,
                    self.face_normal,
                )
            )

        self.handles = create_handles(
            self.build_ele,
            line_to_process,
            self.face_normal,
            coord_input,
            rotation_deg,
            self.is_free_mode,
            x_dir_handle,
            y_dir_handle,
            z_dir_handle,
        )

    def draw_neopreno_preview(self, line: AllplanGeo.Line3D) -> ModelEleList:
        """Dibuja el preview del neopreno durante la creacion."""
        if not line or AllplanGeo.CalcLength(line) < 0.1:
            return []

        if self.is_free_mode and self.face_normal and self.face_point:
            line_to_use, _ = self._prepare_line(line, adjust_width=False)
        elif self.is_free_mode:
            line_to_use = line
        else:
            line_to_use, _ = self._prepare_line(line)

        longitud = AllplanGeo.CalcLength(line_to_use)
        if hasattr(self.build_ele, "Longitud"):
            self.build_ele.Longitud.value = longitud

        grosor = get_selected_thickness(self.build_ele)
        color = get_color_for_thickness(grosor)
        ancho = get_neopreno_width(self.build_ele)

        invertir_grosor = False
        if self.is_free_mode and hasattr(self.build_ele, "InvertirGrosor"):
            val = self.build_ele.InvertirGrosor.value
            if isinstance(val, bool):
                invertir_grosor = not val
            elif isinstance(val, str):
                invertir_grosor = val.lower() not in ("true", "1", "yes")
            else:
                invertir_grosor = not bool(val)

        coord_input = None
        if self.script_object_interactor and hasattr(
            self.script_object_interactor, "coord_input"
        ):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, "RotacionManual"):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, "GetDeg"):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        solid = create_neopreno_solid_on_face(
            line_to_use,
            ancho,
            grosor,
            self.face_normal if not self.is_free_mode else None,
            self.face_point if not self.is_free_mode else None,
            invertir_grosor,
            coord_input,
            rotation_deg,
            AllplanGeo.Matrix3D(),
            self.is_free_mode,
        )

        if not solid:
            return []

        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.Color = color

        model_ele_list = ModelEleList()
        model_ele_list.append_geometry_3d(solid, props)

        return model_ele_list

    def _get_creation_indicator_anchor(self) -> AllplanGeo.Point3D | None:
        """Punto donde mostrar que la sesion sigue lista para crear otro neopreno."""
        records = getattr(self, "_created_neopreno_records", []) or []
        if records:
            last_record = records[-1]
            pos = last_record.get("pos")
            if pos is not None and hasattr(pos, "X"):
                return AllplanGeo.Point3D(pos.X, pos.Y, getattr(pos, "Z", 0.0))

            start = last_record.get("start")
            end = last_record.get("end")
            if start is not None and end is not None:
                return AllplanGeo.Point3D(
                    (start.X + end.X) / 2.0,
                    (start.Y + end.Y) / 2.0,
                    (start.Z + end.Z) / 2.0,
                )

        if self.face_point is not None and hasattr(self.face_point, "X"):
            return AllplanGeo.Point3D(
                self.face_point.X, self.face_point.Y, self.face_point.Z
            )
        return None

    def _draw_creation_indicator_preview(self, clear_before: bool = True) -> bool:
        """Preview auxiliar mientras se espera el primer punto de la siguiente linea."""
        if self.is_editing_existing or getattr(self, "is_modification_mode", False):
            return False
        if self.interactor_state != SELECTING_LINE:
            return False
        if self.line_result and self.line_result.input_line:
            return False

        anchor = self._get_creation_indicator_anchor()
        indicator = _build_neopreno_creation_indicator_elements(
            anchor,
            bool(getattr(self, "_created_neopreno_records", []) or []),
        )
        if not indicator:
            return False

        doc = self._get_inline_preview_document()
        try:
            AllplanBaseElements.DrawElementPreview(
                doc, AllplanGeo.Matrix3D(), indicator, clear_before, None
            )
            return True
        except Exception as exc:
            print(f"[NEOPRENO] Error dibujando indicador de creacion: {exc}")
            return False

    def on_mouse_leave(self):
        if self.script_object_interactor:
            self.script_object_interactor.on_mouse_leave()

    def on_preview_draw(self):
        if getattr(self, "_inline_selected_neopreno_active", False):
            self._draw_inline_selected_neopreno_preview(clear_before=False)
            return

        if (
            self.line_result
            and self.line_result.input_line
            and self.interactor_state == SELECTING_LINE
        ):
            preview_elements = self.draw_neopreno_preview(self.line_result.input_line)
            if preview_elements:
                AllplanBaseElements.DrawElementPreview(
                    self.document,
                    AllplanGeo.Matrix3D(),
                    preview_elements,
                    True,
                    None,
                )
        elif self.interactor_state == SELECTING_LINE:
            self._draw_creation_indicator_preview(clear_before=True)

    def modify_element_property(self, name: str, _value: Any) -> bool:
        """Maneja cambios en propiedades del elemento."""
        editable_config_changed = name in (
            "Ancho",
            "GrosorSeleccionado",
            "InvertirGrosor",
            "RotacionManual",
        )

        if name == "GrosorSeleccionado":
            update_color_for_thickness(self.build_ele)

        if name == "Ancho":
            get_neopreno_width(self.build_ele)

        if name == "neopreno_libre":
            if self.script_object_interactor and hasattr(
                self.script_object_interactor, "coord_input"
            ):
                self._saved_coord_input = self.script_object_interactor.coord_input
            self.is_free_mode = self._get_free_mode()
            self._update_parameter_visibility()
            if not self.is_editing_existing:
                if (
                    self.interactor_state == SELECTING_WALL
                    or self.interactor_state == SELECTING_SOLID
                ):
                    self.start_input()

        if name in ("InvertirGrosor", "RotacionManual"):
            if self.line_result and self.line_result.input_line:
                if self._pending_create_edit:
                    return False
                elif self.is_editing_existing:
                    return False
                elif self.interactor_state == SELECTING_LINE:
                    if self.script_object_interactor and hasattr(
                        self.script_object_interactor, "preview_function"
                    ):
                        self.draw_neopreno_preview(self.line_result.input_line)

        if getattr(self, "_inline_selected_neopreno_active", False) and (
            editable_config_changed or name == "neopreno_libre"
        ):
            self._commit_inline_palette_change(name)
            return True

        if self._pending_create_edit and editable_config_changed:
            self.is_free_mode = self._get_free_mode()
            self._save_state_to_build_ele()
            return False

        if self.is_editing_existing and editable_config_changed:
            self.is_free_mode = self._get_free_mode()
            if self.line_result and self.line_result.input_line:
                self._save_state_to_build_ele()
            return False

        if self.is_editing_existing:
            return False

        if self.interactor_state == SELECTING_WALL:
            return False

        if self.interactor_state == SELECTING_LINE:
            self._start_line_input()
            if self.script_object_interactor:
                coord_input_to_use = (
                    self._saved_coord_input
                    if self._saved_coord_input
                    else self.coord_input
                )
                if coord_input_to_use:
                    self.script_object_interactor.start_input(coord_input_to_use)

        return False

    def execute(self) -> CreateElementResult:
        """Dispatcher principal: separa CREATE y EDIT en funciones independientes."""

        if hasattr(self.build_ele, "IsModify"):
            is_modify = self.build_ele.IsModify()
        else:
            is_modify = self.is_editing_existing or getattr(
                self, "is_modification_mode", False
            )

        if getattr(self, "_inline_selected_neopreno_active", False) and not is_modify:
            result = self._execute_inline_selection_preview()
            neo_log(
                "execute: edicion inline "
                f"elements={len(result.elements)} "
                f"preview_aux={len(result.preview_elements)}"
            )
            return result

        self.is_editing_existing = is_modify
        neo_log(
            "execute: "
            f"mode={'MODIFY' if is_modify else 'CREATE'} "
            f"state={self.interactor_state} "
            f"has_line={bool(self.line_result and self.line_result.input_line)}"
        )

        if is_modify:
            return self._execute_modify()
        return self._execute_create()

    def _execute_create(self) -> CreateElementResult:
        neo_log("_execute_create: inicio")
        """Lógica completa de CREACIÓN: detecta muro, calcula PMP_PARE, genera z_unique, crea geometrías."""

        if not self.line_result or not self.line_result.input_line:
            punto_inicial = getattr(self.build_ele, "PuntoInicial", None)
            punto_final = getattr(self.build_ele, "PuntoFinal", None)
            if (
                punto_inicial
                and punto_final
                and hasattr(punto_inicial, "value")
                and hasattr(punto_final, "value")
            ):
                if punto_inicial.value and punto_final.value:
                    if not self.line_result:
                        from ScriptObjectInteractors.LineInteractor import (
                            LineInteractorResult,
                        )

                        self.line_result = LineInteractorResult()
                    self.line_result.input_line = AllplanGeo.Line3D(
                        punto_inicial.value, punto_final.value
                    )
                    neo_log("_execute_create: linea recuperada desde build_ele")
                else:
                    neo_log(
                        "_execute_create: sin linea y puntos vacios -> CreateElementResult([])"
                    )
                    return CreateElementResult([])
            else:
                neo_log(
                    "_execute_create: sin linea ni parametros PuntoInicial/PuntoFinal -> CreateElementResult([])"
                )
                return CreateElementResult([])

        line = self.line_result.input_line

        local_line = line

        if not self.is_free_mode and self.detected_wall:
            try:
                wall_matrix = get_wall_placement_matrix(self.detected_wall)
                if wall_matrix:
                    inv_wall_matrix = wall_matrix.GetInverse()
                    if inv_wall_matrix:
                        local_start = inv_wall_matrix * line.StartPoint
                        local_end = inv_wall_matrix * line.EndPoint
                        local_line = AllplanGeo.Line3D(local_start, local_end)

                        if self.face_normal:
                            try:
                                origin_point = AllplanGeo.Point3D(0, 0, 0)
                                normal_point = AllplanGeo.Point3D(
                                    self.face_normal.X,
                                    self.face_normal.Y,
                                    self.face_normal.Z,
                                )
                                transformed_origin = inv_wall_matrix * origin_point
                                transformed_normal = inv_wall_matrix * normal_point
                                self.face_normal = AllplanGeo.Vector3D(
                                    transformed_normal.X - transformed_origin.X,
                                    transformed_normal.Y - transformed_origin.Y,
                                    transformed_normal.Z - transformed_origin.Z,
                                )
                                self.face_normal = (
                                    normalize_vector(self.face_normal)
                                    or self.face_normal
                                )
                            except Exception:
                                pass
            except Exception:
                pass
        else:
            local_line = line

        if self.is_free_mode:
            line_to_use = local_line
        else:
            line_to_use, _ = self._prepare_line(
                local_line, is_already_in_local_coords=True
            )

        start_point = line_to_use.StartPoint
        end_point = line_to_use.EndPoint

        if not self.is_editing_existing:
            self.build_ele.PuntoInicial.value = start_point
            self.build_ele.PuntoFinal.value = end_point
        else:
            pass

        if not hasattr(self, "_z_unique_initialized"):
            self._z_unique_initialized = False

        z_unique = 0.0
        if hasattr(self.build_ele, "z_unique") and hasattr(
            self.build_ele.z_unique, "value"
        ):
            if not self.build_ele.z_unique.value or self.build_ele.z_unique.value == 0:
                z_unique = random.random() * 3600
                self.build_ele.z_unique.value = z_unique
            else:
                z_unique = float(self.build_ele.z_unique.value)
        else:
            z_unique = random.random() * 3600

        wall_pare = normalize_pmp_pare_value(self._resolve_host_pmp_pare())
        wall_name = normalize_pmp_pare_value(self._resolve_host_pmp_pare_name())

        if not self.is_editing_existing:
            if hasattr(self.build_ele, "pmp_pare") and hasattr(
                self.build_ele.pmp_pare, "value"
            ):
                try:
                    self.build_ele.pmp_pare.value = wall_pare
                    neo_log(f"_execute_create: build_ele.pmp_pare(IFC)='{wall_pare}'")
                except Exception as e:
                    pass
            if hasattr(self.build_ele, "pmp_pare_name") and hasattr(
                self.build_ele.pmp_pare_name, "value"
            ):
                try:
                    self.build_ele.pmp_pare_name.value = wall_name
                    neo_log(
                        f"_execute_create: build_ele.pmp_pare_name(material)='{wall_name}'"
                    )
                except Exception:
                    pass
        else:
            if hasattr(self.build_ele, "pmp_pare") and hasattr(
                self.build_ele.pmp_pare, "value"
            ):
                wall_pare = (
                    normalize_pmp_pare_value(self.build_ele.pmp_pare.value)
                    if self.build_ele.pmp_pare.value
                    else ""
                )
            if hasattr(self.build_ele, "pmp_pare_name") and hasattr(
                self.build_ele.pmp_pare_name, "value"
            ):
                wall_name = (
                    normalize_pmp_pare_value(self.build_ele.pmp_pare_name.value)
                    if self.build_ele.pmp_pare_name.value
                    else ""
                )

        if not wall_pare:
            wall_pare = "SIN_IFC"
        if not wall_name:
            wall_name = "SIN_PARE"

        self.line_result.input_line = line_to_use

        self._init_pmp_attribute_ids()
        neo_log(
            "_execute_create: atributos destino "
            f"PMP_PARE={getattr(self, 'attr_pmp_pare_id', 0)} "
            f"PMP_WALL_ID={getattr(self, 'attr_pmp_wall_id', 0)} "
            f"valor_ifc='{wall_pare}' valor_material='{wall_name}'"
        )

        self.elements = self._create_neopreno_elements(
            pmp_pare=wall_pare,
            pmp_pare_name=wall_name,
        )
        neo_log(
            f"_execute_create: elementos geometria={len(self.elements) if self.elements else 0} wall_pare={wall_pare}"
        )

        if not self.elements:
            neo_log(
                "_execute_create: no se crearon elementos geometria -> CreateElementResult([])"
            )
            return CreateElementResult([])

        individual_pythonparts = self.create_individual_pythonparts_from_elements(
            self.elements,
            pmp_pare=wall_pare,
            pmp_pare_name=wall_name,
            is_modify=False,  # Hash random en creación
        )

        if not individual_pythonparts:
            neo_log(
                "_execute_create: no se crearon PythonParts individuales -> CreateElementResult([])"
            )
            return CreateElementResult([])

        punto_inicial = start_point
        punto_final = end_point
        ancho = (
            get_neopreno_width(self.build_ele)
            if hasattr(self.build_ele, "Ancho")
            else 50.0
        )
        grosor = (
            get_selected_thickness(self.build_ele)
            if hasattr(self.build_ele, "GrosorSeleccionado")
            else 5.0
        )
        libre = self.is_free_mode
        rot = 0.0
        if hasattr(self.build_ele, "RotacionManual"):
            rv = getattr(self.build_ele.RotacionManual, "value", None)
            if rv is not None:
                rot = rv.GetDeg() if hasattr(rv, "GetDeg") else float(rv)
        invertido = False
        if hasattr(self.build_ele, "InvertirGrosor"):
            val = getattr(self.build_ele.InvertirGrosor, "value", None)
            if val is not None:
                invertido = (
                    bool(val)
                    if isinstance(val, bool)
                    else str(val).lower() in ("true", "1", "yes")
                )

        saved_state_str = self._serialize_state_to_json()
        if saved_state_str and hasattr(self.build_ele, "SavedState"):
            try:
                self.build_ele.SavedState.value = saved_state_str
            except Exception:
                pass

        global_params = {
            "z_unique": z_unique,
            "pmp_pare": wall_pare,
            "pmp_pare_name": wall_name,
            "TotalElements": len(individual_pythonparts),
            "PuntoInicial": punto_inicial,
            "PuntoFinal": punto_final,
            "Ancho": ancho,
            "Grosor": grosor,
            "Libre": libre,
            "PermitirPickUpLinea": self._get_allow_line_pickup(),
            "RotacionManual": rot,
            "InvertirGrosor": invertido,
            "SavedState": saved_state_str if saved_state_str else "",
        }

        group_hash = create_element_hash(
            "neopreno_group", stable=False  # CREATE = random
        )

        param_list = create_params_list_from_dict(global_params)

        pmp_pare_in_param_list = any("pmp_pare" in p for p in param_list)

        python_file_name = (
            self.build_ele.pyp_file_name
            if hasattr(self.build_ele, "pyp_file_name")
            else ""
        )

        pythonpart_group = PythonPartGroup(
            "Neoprenos",
            param_list,
            group_hash,
            python_file_name,
            individual_pythonparts,
        )

        model_elem_list = pythonpart_group.create()
        neo_log(
            f"_execute_create: PythonPartGroup elementos={len(model_elem_list) if model_elem_list else 0}"
        )

        if not model_elem_list or len(model_elem_list) == 0:
            neo_log("_execute_create: PythonPartGroup vacio -> CreateElementResult([])")
            return CreateElementResult([])

        handles: list[HandleProperties] = []

        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if (
            not coord_input
            and self.script_object_interactor
            and hasattr(self.script_object_interactor, "coord_input")
        ):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, "RotacionManual"):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, "GetDeg"):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            line_for_handles = (
                self.line_result.input_line
                if self.line_result and self.line_result.input_line
                else None
            )
            if line_for_handles:
                x_dir_handle, y_dir_handle, z_dir_handle = (
                    build_face_local_axes_for_handles(
                        line_for_handles.StartPoint,
                        line_for_handles.EndPoint,
                        self.face_point,
                        self.face_normal,
                    )
                )

        if self.line_result and self.line_result.input_line:
            current_line = self.line_result.input_line
            handles = create_handles(
                self.build_ele,
                current_line,
                self.face_normal,
                coord_input,
                rotation_deg,
                self.is_free_mode,
                x_dir_handle,
                y_dir_handle,
                z_dir_handle,
            )
        else:
            punto_inicial = getattr(self.build_ele, "PuntoInicial", None)
            punto_final = getattr(self.build_ele, "PuntoFinal", None)
            if (
                punto_inicial
                and punto_final
                and punto_inicial.value
                and punto_final.value
            ):
                fallback_line = AllplanGeo.Line3D(
                    punto_inicial.value, punto_final.value
                )
                handles = create_handles(
                    self.build_ele,
                    fallback_line,
                    self.face_normal,
                    coord_input,
                    rotation_deg,
                    self.is_free_mode,
                    x_dir_handle,
                    y_dir_handle,
                    z_dir_handle,
                )

        self.handles = handles

        connect_to_ele = ConnectToElements()

        if not self.is_free_mode:
            if (
                hasattr(self.build_ele, "SolidoConnection")
                and self.build_ele.SolidoConnection.value.uuid
            ):
                uuid_str = str(self.build_ele.SolidoConnection.value.uuid)
                if uuid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(uuid_str)
            if len(connect_to_ele.connection_elements) == 0 and self.solid_info:
                if self.solid_info.get("guid"):
                    connect_to_ele.connection_elements.append(self.solid_info["guid"])
                elif self.solid_info.get("element"):
                    try:
                        element_guid = str(
                            self.solid_info["element"].GetModelElementUUID()
                        )
                        if element_guid != "00000000-0000-0000-0000-000000000000":
                            connect_to_ele.connection_elements.append(element_guid)
                    except Exception:
                        pass
            if (
                len(connect_to_ele.connection_elements) == 0
                and hasattr(self.build_ele, "SolidoGUID")
                and self.build_ele.SolidoGUID.value
            ):
                guid_str = str(self.build_ele.SolidoGUID.value)
                if guid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(guid_str)
        else:
            if (
                hasattr(self.build_ele, "MuroConnection")
                and self.build_ele.MuroConnection.value.uuid
            ):
                uuid_str = str(self.build_ele.MuroConnection.value.uuid)
                if uuid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(uuid_str)
            if len(connect_to_ele.connection_elements) == 0 and self.detected_wall_guid:
                if self.detected_wall_guid != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(self.detected_wall_guid)
            if len(connect_to_ele.connection_elements) == 0 and self.detected_wall:
                try:
                    wall_guid = str(self.detected_wall.GetModelElementUUID())
                    if wall_guid != "00000000-0000-0000-0000-000000000000":
                        connect_to_ele.connection_elements.append(wall_guid)
                except Exception:
                    pass
            if (
                len(connect_to_ele.connection_elements) == 0
                and hasattr(self.build_ele, "MuroGUID")
                and self.build_ele.MuroGUID.value
            ):
                guid_str = str(self.build_ele.MuroGUID.value)
                if guid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(guid_str)

        if len(connect_to_ele.connection_elements) == 0:
            neo_log(
                "_execute_create: sin conexion a muro/solido -> mensaje y CreateElementResult([])"
            )
            AllplanUtil.ShowMessageBox(
                "Error: No se pudo establecer conexion con el elemento.\n\n"
                "El neopreno necesita estar conectado a un muro o solido para guardarse correctamente.",
                AllplanUtil.MB_OK,
            )
            return CreateElementResult([])

        self._save_state_to_build_ele()

        return_handles = handles if self._pending_create_edit else []
        return_multi_placement = True
        neo_log(
            "_execute_create: return "
            f"model_elems={len(model_elem_list)} "
            f"connect={len(connect_to_ele.connection_elements)} "
            f"handles={len(return_handles)} "
            f"multi_placement={return_multi_placement}"
        )

        return CreateElementResult(
            elements=model_elem_list,
            handles=return_handles,
            placement_point=AllplanGeo.Point3D(0.0, 0.0, 0.0),
            connect_to_ele=connect_to_ele,
            uuid_parameter_name="PythonPartUUID",
            multi_placement=return_multi_placement,
        )

    # --- Sincronizacion posicion tras arrastre (MODIFY) y edicion inline (Seleccionar) ---

    def _ensure_line_result_from_build_ele_for_modify(self) -> None:
        if _is_valid_line(self.line_result.input_line):
            return
        p0 = (
            getattr(self.build_ele.PuntoInicial, "value", None)
            if hasattr(self.build_ele, "PuntoInicial")
            else None
        )
        p1 = (
            getattr(self.build_ele.PuntoFinal, "value", None)
            if hasattr(self.build_ele, "PuntoFinal")
            else None
        )
        if p0 is not None and p1 is not None:
            line = AllplanGeo.Line3D(p0, p1)
            if _is_valid_line(line):
                self.line_result.input_line = line
                return
        ss = (
            (self.build_ele.SavedState.value or "").strip()
            if hasattr(self.build_ele, "SavedState")
            and hasattr(self.build_ele.SavedState, "value")
            else ""
        )
        st = parse_saved_state(ss) if ss else {}
        q0 = saved_state_to_point3d(st, "p0")
        q1 = saved_state_to_point3d(st, "p1")
        if q0 is not None and q1 is not None:
            line = AllplanGeo.Line3D(q0, q1)
            if _is_valid_line(line):
                self.line_result.input_line = line
                return
        if self._restore_state_from_modification_element():
            return

    def _apply_face_context_from_build_ele_only(self) -> None:
        try:
            if (
                hasattr(self.build_ele, "CaraNormalX")
                and hasattr(self.build_ele, "CaraNormalY")
                and hasattr(self.build_ele, "CaraNormalZ")
            ):
                normal = AllplanGeo.Vector3D(
                    self.build_ele.CaraNormalX.value,
                    self.build_ele.CaraNormalY.value,
                    self.build_ele.CaraNormalZ.value,
                )
                self.face_normal = normalize_vector(normal) or normal
            if (
                hasattr(self.build_ele, "PuntoClicX")
                and hasattr(self.build_ele, "PuntoClicY")
                and hasattr(self.build_ele, "PuntoClicZ")
            ):
                self.face_point = AllplanGeo.Point3D(
                    self.build_ele.PuntoClicX.value,
                    self.build_ele.PuntoClicY.value,
                    self.build_ele.PuntoClicZ.value,
                )
            self.face_polygon = None
        except Exception:
            pass

    def _normalize_checkbox_build_ele_values(self) -> None:
        """Asegura bool nativo en CheckBox tras cargar param_list (paleta Allplan)."""
        for key in NEOPRENO_CHECKBOX_PARAM_KEYS:
            if not hasattr(self.build_ele, key):
                continue
            attr = getattr(self.build_ele, key)
            if not hasattr(attr, "value"):
                continue
            parsed = parse_bool_param_value(attr.value)
            if parsed is not None:
                attr.value = parsed

    def _apply_param_list_to_build_ele(self, param_list_src: list) -> None:
        if not param_list_src:
            return
        try:
            params = parse_params_list_to_dict(param_list_src)
            for key, value in params.items():
                if key == "SavedState":
                    continue
                if not hasattr(self.build_ele, key):
                    continue
                attr = getattr(self.build_ele, key)
                if not hasattr(attr, "value"):
                    continue
                try:
                    attr.value = coerce_build_ele_param_value(key, value)
                except Exception as exc:
                    print(f"[SELECT][NEOPRENO] No se aplico {key}: {exc}")
            self._normalize_checkbox_build_ele_values()
            if (
                hasattr(self.build_ele, "Longitud")
                and hasattr(self.build_ele, "PuntoInicial")
                and hasattr(self.build_ele, "PuntoFinal")
            ):
                p0 = getattr(self.build_ele.PuntoInicial, "value", None)
                p1 = getattr(self.build_ele.PuntoFinal, "value", None)
                if p0 is not None and p1 is not None:
                    self.build_ele.Longitud.value = AllplanGeo.CalcLength(
                        AllplanGeo.Line3D(p0, p1)
                    )
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error aplicando param_list: {exc}")

    def _apply_line_points_to_build_ele(
        self, start: AllplanGeo.Point3D, end: AllplanGeo.Point3D
    ) -> None:
        if hasattr(self.build_ele, "PuntoInicial"):
            self.build_ele.PuntoInicial.value = AllplanGeo.Point3D(
                start.X, start.Y, start.Z
            )
        if hasattr(self.build_ele, "PuntoFinal"):
            self.build_ele.PuntoFinal.value = AllplanGeo.Point3D(end.X, end.Y, end.Z)
        self.line_result.input_line = AllplanGeo.Line3D(
            AllplanGeo.Point3D(start.X, start.Y, start.Z),
            AllplanGeo.Point3D(end.X, end.Y, end.Z),
        )
        self._save_state_to_build_ele()

    def _get_build_ele_insert_matrix(self) -> AllplanGeo.Matrix3D | None:
        if not hasattr(self.build_ele, "get_insert_matrix"):
            return None
        try:
            return self.build_ele.get_insert_matrix()
        except Exception:
            return None

    def _matrix_translation_length(self, matrix: AllplanGeo.Matrix3D) -> float:
        try:
            translation = matrix.GetTranslationVector()
            return float(translation.GetLength()) if translation else 0.0
        except Exception:
            return 0.0

    def _sync_line_from_build_ele_insert_matrix(
        self, min_displacement_mm: float = 1.0
    ) -> bool:
        matrix = self._get_build_ele_insert_matrix()
        if matrix is None:
            return False
        trans_len = self._matrix_translation_length(matrix)
        if trans_len < min_displacement_mm:
            return False
        old_start = (
            getattr(self.build_ele.PuntoInicial, "value", None)
            if hasattr(self.build_ele, "PuntoInicial")
            else None
        )
        old_end = (
            getattr(self.build_ele.PuntoFinal, "value", None)
            if hasattr(self.build_ele, "PuntoFinal")
            else None
        )
        if old_start is None or old_end is None:
            return False
        try:
            new_start = AllplanGeo.Transform(old_start, matrix)
            new_end = AllplanGeo.Transform(old_end, matrix)
        except Exception:
            return False
        displacement = min(
            old_start.GetDistance(new_start), old_end.GetDistance(new_end)
        )
        if displacement < min_displacement_mm:
            return False
        self._apply_line_points_to_build_ele(new_start, new_end)
        try:
            self.build_ele.set_insert_matrix(AllplanGeo.Matrix3D())
        except Exception:
            pass
        print(
            f"[EDIT][SYNC] Linea actualizada desde insert_matrix "
            f"traslacion={trans_len:.1f} mm"
        )
        return True

    def _is_inline_neopreno_edit_session(self) -> bool:
        return bool(getattr(self, "_inline_selected_neopreno_active", False))

    def _try_sync_drag_offset_for_modify(self) -> bool:
        if self._is_inline_neopreno_edit_session():
            return False
        return self._sync_line_from_build_ele_insert_matrix()

    def _sync_line_from_build_ele_points(self) -> bool:
        if not hasattr(self.build_ele, "PuntoInicial") or not hasattr(
            self.build_ele, "PuntoFinal"
        ):
            return False
        p0 = getattr(self.build_ele.PuntoInicial, "value", None)
        p1 = getattr(self.build_ele.PuntoFinal, "value", None)
        if p0 is None or p1 is None:
            return False
        self.line_result.input_line = AllplanGeo.Line3D(
            AllplanGeo.Point3D(p0.X, p0.Y, p0.Z),
            AllplanGeo.Point3D(p1.X, p1.Y, p1.Z),
        )
        return True

    def _element_adapter_key(self, element) -> str:
        if element is None:
            return ""
        try:
            if element.IsNull():
                return ""
        except Exception:
            pass
        try:
            return str(element.GetModelElementUUID())
        except Exception:
            pass
        try:
            return str(element.GetNOIGUID())
        except Exception:
            return ""

    def _normalize_pyp_display_name(self, name: Any) -> str:
        return str(name or "").strip().strip("'\"")

    def _parameter_to_param_list(self, parameter: Any) -> list:
        if isinstance(parameter, str):
            return parameter.splitlines()
        if isinstance(parameter, (list, tuple)):
            return list(parameter)
        return []

    def _is_neopreno_pyp_params(self, name: Any, parameter: Any) -> bool:
        if self._normalize_pyp_display_name(name) == "Neoprenos":
            return True
        param_list = self._parameter_to_param_list(parameter)
        if not param_list:
            return False
        params = parse_params_list_to_dict(param_list)
        if params.get("SavedState") and (
            params.get("GrosorSeleccionado") is not None
            or params.get("Ancho") is not None
        ):
            return True
        if "neopreno_libre" in params:
            return True
        return False

    def _read_neopreno_param_list_from_element(self, pyp_element) -> list:
        if pyp_element is None:
            return []
        try:
            if pyp_element.IsNull():
                return []
        except Exception:
            pass
        try:
            success, name, parameter = (
                AllplanBaseElements.PythonPartService.GetParameter(pyp_element)
            )
            if success and self._is_neopreno_pyp_params(name, parameter):
                return self._parameter_to_param_list(parameter)
        except Exception:
            pass
        return []

    def _coerce_to_base_element_adapter(self, element):
        if element is None:
            return None
        if isinstance(element, str):
            try:
                adapter = AllplanEleAdapter.BaseElementAdapter.FromNOIGUID(
                    element, self.document
                )
                if adapter is not None and not adapter.IsNull():
                    return adapter
            except Exception:
                return None
            return None
        try:
            if element.IsNull():
                return None
        except Exception:
            pass
        return element

    def _adapter_is_under_element(self, selected_element, ancestor_element) -> bool:
        if selected_element is None or ancestor_element is None:
            return False
        ancestor_key = self._element_adapter_key(ancestor_element)
        if not ancestor_key:
            return False
        if self._element_adapter_key(selected_element) == ancestor_key:
            return True
        current = selected_element
        visited: set[str] = set()
        for _ in range(14):
            try:
                if current is None or current.IsNull():
                    break
            except Exception:
                break
            if self._element_adapter_key(current) == ancestor_key:
                return True
            try:
                noiguid = str(current.GetNOIGUID())
            except Exception:
                noiguid = ""
            if noiguid and noiguid in visited:
                break
            if noiguid:
                visited.add(noiguid)
            try:
                parent = AllplanEleAdapter.BaseElementAdapterParentElementService.GetParentElement(
                    current
                )
            except Exception:
                parent = None
            if parent is None or parent.IsNull():
                break
            current = parent
        return False

    def _distance_point_to_segment(self, point, start, end) -> float:
        if point is None or start is None or end is None:
            return float("inf")
        vx = end.X - start.X
        vy = end.Y - start.Y
        vz = end.Z - start.Z
        wx = point.X - start.X
        wy = point.Y - start.Y
        wz = point.Z - start.Z
        length_sq = vx * vx + vy * vy + vz * vz
        if length_sq <= 1e-9:
            return point.GetDistance(start)
        t = max(0.0, min(1.0, (wx * vx + wy * vy + wz * vz) / length_sq))
        proj = AllplanGeo.Point3D(start.X + t * vx, start.Y + t * vy, start.Z + t * vz)
        return point.GetDistance(proj)

    def _find_created_neopreno_record_at_point(self, point):
        if point is None:
            return None, None
        records = getattr(self, "_created_neopreno_records", []) or []
        best_record = None
        best_idx = None
        best_dist = float("inf")
        for idx, record in enumerate(records):
            pos = record.get("pos")
            if pos is not None:
                dist_center = point.GetDistance(pos)
                if dist_center <= 300.0:
                    return idx, record
            dist = self._distance_point_to_segment(
                point, record.get("start"), record.get("end")
            )
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
                best_record = record
        if best_record is not None and best_dist <= 350.0:
            return best_idx, best_record
        return None, None

    def _build_neopreno_record_from_ppg(
        self,
        pyp_element,
        param_list: list,
        model_ele_list=None,
        line: AllplanGeo.Line3D | None = None,
    ) -> dict:
        params = parse_params_list_to_dict(param_list) if param_list else {}
        start = params.get("PuntoInicial")
        end = params.get("PuntoFinal")
        if line is not None:
            start = AllplanGeo.Point3D(
                line.StartPoint.X, line.StartPoint.Y, line.StartPoint.Z
            )
            end = AllplanGeo.Point3D(line.EndPoint.X, line.EndPoint.Y, line.EndPoint.Z)
        elif not isinstance(start, AllplanGeo.Point3D) or not isinstance(
            end, AllplanGeo.Point3D
        ):
            start = None
            end = None
        pos = None
        if isinstance(start, AllplanGeo.Point3D) and isinstance(
            end, AllplanGeo.Point3D
        ):
            pos = AllplanGeo.Point3D(
                (start.X + end.X) / 2.0,
                (start.Y + end.Y) / 2.0,
                (start.Z + end.Z) / 2.0,
            )
        return {
            "element": pyp_element,
            "model_list": model_ele_list,
            "param_list": list(param_list) if param_list else [],
            "pos": pos,
            "start": start,
            "end": end,
        }

    def _find_created_neopreno_record_index_for_element(self, element) -> int | None:
        key = self._element_adapter_key(element)
        if not key:
            return None
        for idx, record in enumerate(self._created_neopreno_records):
            record_element = record.get("element")
            if record_element and self._element_adapter_key(record_element) == key:
                return idx
        return None

    def _register_or_refresh_neopreno_record_from_ppg(
        self,
        pyp_element,
        param_list: list,
        input_point=None,
        model_ele_list=None,
        line: AllplanGeo.Line3D | None = None,
    ) -> tuple[int | None, dict | None]:
        if pyp_element is None:
            return None, None
        full_param_list = param_list or self._read_neopreno_param_list_from_element(
            pyp_element
        )
        record = self._build_neopreno_record_from_ppg(
            pyp_element, full_param_list, model_ele_list=model_ele_list, line=line
        )
        if (
            record.get("pos") is None
            and input_point is not None
            and hasattr(input_point, "X")
        ):
            record["pos"] = AllplanGeo.Point3D(
                input_point.X, input_point.Y, input_point.Z
            )
        existing_idx = self._find_created_neopreno_record_index_for_element(pyp_element)
        if existing_idx is not None:
            self._created_neopreno_records[existing_idx].update(record)
            return existing_idx, self._created_neopreno_records[existing_idx]

        if getattr(self, "interactor_state", None) == SELECTING_EXISTING_NEOPRENO:
            print("[SELECT][NEOPRENO] PPG ignorado: no pertenece a la ejecucion actual")
            return None, None

        self._created_neopreno_records.append(record)
        new_idx = len(self._created_neopreno_records) - 1
        return new_idx, record

    def _warn_neopreno_from_other_execution(self) -> None:
        """Aviso al usuario: Seleccionar solo neoprenos de la ejecucion en curso."""
        print(
            "[SELECT][NEOPRENO] Rechazado: neopreno de otra ejecucion "
            "(solo neoprenos colocados en esta sesion)"
        )
        try:
            AllplanUtil.ShowMessageBox(NEOPRENO_OTHER_EXECUTION_MSG, AllplanUtil.MB_OK)
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] No se pudo mostrar el cuadro de aviso: {exc}")
            print(NEOPRENO_OTHER_EXECUTION_MSG)

    def _build_current_inline_param_list(self) -> list:
        params: dict[str, Any] = {}
        if hasattr(self.build_ele, "SavedState"):
            ss = str(getattr(self.build_ele.SavedState, "value", "") or "")
            if ss:
                params["SavedState"] = ss
        for key in (
            "PuntoInicial",
            "PuntoFinal",
            "Ancho",
            "GrosorSeleccionado",
            "neopreno_libre",
            "RotacionManual",
            "InvertirGrosor",
            "pmp_pare",
            "pmp_pare_name",
            "z_unique",
            "MuroGUID",
            "SolidoGUID",
        ):
            if not hasattr(self.build_ele, key):
                continue
            attr = getattr(self.build_ele, key)
            if hasattr(attr, "value"):
                params[key] = attr.value
        return create_params_list_from_dict(params)

    def _remember_created_neopreno(self, created_elements, model_ele_list=None) -> None:
        line = getattr(self.line_result, "input_line", None)
        if not line:
            return
        pyp_adapter = next(
            (
                element
                for element in created_elements
                if AllplanBaseElements.PythonPartService.IsPythonPartGroupElement(
                    element
                )
            ),
            None,
        )
        if pyp_adapter is None:
            pyp_adapter = next(
                (
                    element
                    for element in created_elements
                    if AllplanBaseElements.PythonPartService.IsPythonPartElement(
                        element
                    )
                ),
                None,
            )
        if pyp_adapter is None:
            return
        param_list = self._read_neopreno_param_list_from_element(pyp_adapter)
        if not param_list:
            param_list = self._build_current_inline_param_list()
        self._register_or_refresh_neopreno_record_from_ppg(
            pyp_adapter, param_list, model_ele_list=model_ele_list, line=line
        )

    def _resolve_neopreno_ppg_from_adapter(
        self, selected_element, input_point=None
    ) -> tuple[Any, list]:
        current = selected_element
        visited: set[str] = set()
        rejected: list[str] = []
        if current is not None:
            try:
                if not current.IsNull():
                    for _depth in range(14):
                        try:
                            noiguid = str(current.GetNOIGUID())
                        except Exception:
                            noiguid = ""
                        if noiguid and noiguid in visited:
                            break
                        if noiguid:
                            visited.add(noiguid)
                        is_group = False
                        is_part = False
                        try:
                            is_group = AllplanBaseElements.PythonPartService.IsPythonPartGroupElement(
                                current
                            )
                            is_part = (
                                not is_group
                                and AllplanBaseElements.PythonPartService.IsPythonPartElement(
                                    current
                                )
                            )
                        except Exception:
                            pass
                        if is_group or is_part:
                            try:
                                success, name, parameter = (
                                    AllplanBaseElements.PythonPartService.GetParameter(
                                        current
                                    )
                                )
                                if success and self._is_neopreno_pyp_params(
                                    name, parameter
                                ):
                                    return current, self._parameter_to_param_list(
                                        parameter
                                    )
                                if success and is_group:
                                    rejected.append(
                                        self._normalize_pyp_display_name(name)
                                    )
                            except Exception:
                                pass
                        try:
                            parent = AllplanEleAdapter.BaseElementAdapterParentElementService.GetParentElement(
                                current
                            )
                        except Exception:
                            parent = None
                        if parent is None or parent.IsNull():
                            break
                        current = parent
            except Exception:
                pass
        records = getattr(self, "_created_neopreno_records", []) or []
        if selected_element is not None:
            try:
                if not selected_element.IsNull():
                    for idx, record in enumerate(records):
                        rec_element = record.get("element")
                        if rec_element and self._adapter_is_under_element(
                            selected_element, rec_element
                        ):
                            param_list = self._read_neopreno_param_list_from_element(
                                rec_element
                            )
                            if not param_list:
                                param_list = list(record.get("param_list") or [])
                            return rec_element, param_list
            except Exception:
                pass
        if input_point is not None:
            record_index, record = self._find_created_neopreno_record_at_point(
                input_point
            )
            if record is not None:
                rec_element = record.get("element")
                param_list = self._read_neopreno_param_list_from_element(rec_element)
                if not param_list:
                    param_list = list(record.get("param_list") or [])
                return rec_element, param_list
        if rejected:
            print(f"[SELECT][NEOPRENO] Otros PPG encontrados: {rejected}")
        return None, []

    def _materialize_current_neopreno(self, coord_input=None) -> bool:
        if getattr(self, "is_modification_mode", False):
            return False
        if not self.line_result.input_line:
            return False
        try:
            result = self._execute_create()
            if not result or not result.elements:
                return False
            if coord_input:
                view_world_projection = coord_input.GetViewWorldProjection()
            else:
                view_world_projection = AllplanIFW.ViewWorldProjection()
            transaction = PythonPartTransaction(
                self.document,
                connect_to_ele=result.connect_to_ele,
            )
            created_elements = transaction.execute(
                placement_matrix=AllplanGeo.Matrix3D(),
                view_world_projection=view_world_projection,
                model_ele_list=result.elements,
                modification_ele_list=getattr(self, "modification_ele_list", []),
                rearrange_reinf_pos_nr=result.reinf_rearrange,
                append_reinf_pos_nr=True,
                asso_ref_object=None,
                uuid_parameter_name=result.uuid_parameter_name,
                elements_to_delete=result.elements_to_delete,
            )
            self._remember_created_neopreno(
                created_elements, model_ele_list=result.elements
            )
            neo_log(f"neopreno materializado: {len(created_elements)} elementos")
            return True
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error materializando: {exc}")
            return False

    def _get_active_coord_input(self):
        coord_input = getattr(self, "coord_input", None)
        if coord_input:
            return coord_input
        interactor = getattr(self, "script_object_interactor", None)
        return getattr(interactor, "coord_input", None)

    def _resume_neopreno_line_input(self, coord_input=None) -> bool:
        self.interactor_state = SELECTING_LINE
        self.line_result = LineInteractorResult()
        self._pending_create_edit = False
        self._start_line_input()
        if coord_input is None:
            coord_input = self._get_active_coord_input()
        if coord_input and self.script_object_interactor:
            self.script_object_interactor.start_input(coord_input)
            return True
        return False

    def _start_inline_neopreno_selection(self) -> bool:
        if getattr(self, "is_modification_mode", False):
            print("[SELECT][NEOPRENO] No disponible en MODIFY externo")
            return False
        if getattr(self, "_inline_selected_neopreno_active", False):
            self._leave_inline_neopreno_edit_mode()
        self.neopreno_select_result = NeoprenoSelectResult()
        self.interactor_state = SELECTING_EXISTING_NEOPRENO
        self.script_object_interactor = ExistingNeoprenoSelectInteractor(
            self.neopreno_select_result,
            "Seleccione el neopreno (PPG) en el dibujo",
            owner=self,
        )
        coord_input = self._get_active_coord_input()
        if coord_input:
            self.script_object_interactor.start_input(coord_input)
        return True

    def _deselect_inline_neopreno(self) -> bool:
        if getattr(self, "_inline_selected_neopreno_active", False):
            self._clear_inline_selection_visual()
            self._leave_inline_neopreno_edit_mode()
        self.neopreno_select_result = NeoprenoSelectResult()
        return self._resume_neopreno_line_input(self._get_active_coord_input())

    def _start_active_wall_selection(self) -> bool:
        """Boton Cambiar muro: selecciona el host para los siguientes neoprenos."""
        if getattr(self, "is_modification_mode", False) or getattr(
            self, "_restored_from_saved_state", False
        ):
            print("[INPUT][NEOPRENO] Cambio de muro no disponible en EDIT")
            return False

        if getattr(self, "_inline_selected_neopreno_active", False):
            self._clear_inline_selection_visual()
            self._leave_inline_neopreno_edit_mode()

        self.wall_select_result = WallSelectResult()
        self.line_result = LineInteractorResult()
        if hasattr(self.build_ele, "PuntoInicial"):
            self.build_ele.PuntoInicial.value = None
        if hasattr(self.build_ele, "PuntoFinal"):
            self.build_ele.PuntoFinal.value = None
        self._pending_create_edit = False
        self.interactor_state = SELECTING_WALL
        self.script_object_interactor = WallSelectInteractor(
            self.wall_select_result,
            "Seleccione el nuevo muro para los siguientes neoprenos",
            script_object=self,
        )
        coord_input = self._get_active_coord_input()
        if coord_input:
            self.script_object_interactor.start_input(coord_input)
        neo_log("_start_active_wall_selection: esperando nuevo muro activo")
        return True

    def _enter_inline_neopreno_edit_mode(self, result: NeoprenoSelectResult) -> bool:
        if not result or not result.is_selected or result.element is None:
            return False
        try:
            self._inline_original_modification_mode = getattr(
                self, "is_modification_mode", False
            )
            self._inline_original_modification_ele_list = getattr(
                self, "modification_ele_list", None
            )
            param_list = self._read_neopreno_param_list_from_element(result.element)
            if not param_list:
                param_list = list(result.param_list or [])
            self._apply_param_list_to_build_ele(param_list)
            params = parse_params_list_to_dict(param_list)
            saved_state = str(params.get("SavedState", "") or "").strip()
            if saved_state:
                self._deserialize_state_from_json(saved_state)
            self._normalize_checkbox_build_ele_values()
            self._inline_modification_ele_list = ModificationElementList(
                [result.element]
            )
            self.modification_ele_list = self._inline_original_modification_ele_list
            self.is_modification_mode = False
            self.is_editing_existing = False
            self._inline_selected_neopreno_active = True
            self._neopreno_record_selected_index = result.record_index
            self.is_free_mode = self._get_free_mode()
            try:
                self.build_ele.set_insert_matrix(AllplanGeo.Matrix3D())
            except Exception:
                pass
            self._apply_face_context_from_build_ele_only()
            self._ensure_line_result_from_build_ele_for_modify()
            self._sync_line_from_build_ele_points()
            if result.record_index is not None:
                self._sync_neopreno_record_geometry_from_line(result.record_index)
            self._refresh_inline_execute_cache()
            self._draw_inline_selected_neopreno_preview()
            print("[SELECT][NEOPRENO] Edicion inline activa")
            return True
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error entrando en edicion: {exc}")
            return False

    def _leave_inline_neopreno_edit_mode(self) -> None:
        self._inline_selected_neopreno_active = False
        self._inline_modification_ele_list = None
        self._neopreno_record_selected_index = None
        self._inline_last_execute_result = None
        self.elements = []
        self.is_modification_mode = getattr(
            self, "_inline_original_modification_mode", False
        )
        self.is_editing_existing = self.is_modification_mode
        self.modification_ele_list = getattr(
            self, "_inline_original_modification_ele_list", None
        )

    def _finish_inline_neopreno_edit(self) -> None:
        self._leave_inline_neopreno_edit_mode()

    def _build_inline_edit_handles_result(self) -> CreateElementResult:
        start_prop = getattr(self.build_ele, "PuntoInicial", None)
        end_prop = getattr(self.build_ele, "PuntoFinal", None)
        start_point = (
            start_prop.value if start_prop and hasattr(start_prop, "value") else None
        )
        end_point = end_prop.value if end_prop and hasattr(end_prop, "value") else None
        if not start_point or not end_point:
            line = getattr(self.line_result, "input_line", None)
            if line:
                start_point = line.StartPoint
                end_point = line.EndPoint
        if not start_point or not end_point:
            return CreateElementResult(elements=[], handles=[])
        line = AllplanGeo.Line3D(start_point, end_point)
        handles = create_handles(
            self.build_ele,
            line,
            None if self.is_free_mode else self.face_normal,
            None if self.is_free_mode else self.face_point,
        )
        return CreateElementResult(elements=[], handles=handles)

    def _sync_neopreno_record_geometry_from_line(self, record_index: int) -> None:
        """Actualiza start/end/pos del registro desde line_result tras cargar el PPG."""
        records = getattr(self, "_created_neopreno_records", []) or []
        if record_index is None or record_index < 0 or record_index >= len(records):
            return
        line = getattr(self.line_result, "input_line", None)
        if not line:
            return
        records[record_index]["start"] = AllplanGeo.Point3D(
            line.StartPoint.X, line.StartPoint.Y, line.StartPoint.Z
        )
        records[record_index]["end"] = AllplanGeo.Point3D(
            line.EndPoint.X, line.EndPoint.Y, line.EndPoint.Z
        )
        records[record_index]["pos"] = AllplanGeo.Point3D(
            (line.StartPoint.X + line.EndPoint.X) / 2.0,
            (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
            (line.StartPoint.Z + line.EndPoint.Z) / 2.0,
        )

    def _get_inline_preview_document(self):
        """Documento de vista activo para previews interactivos."""
        coord_input = self._get_active_coord_input()
        if coord_input:
            try:
                return coord_input.GetInputViewDocument()
            except Exception:
                pass
        return self.document

    def _get_inline_selection_axis_line(self) -> AllplanGeo.Line3D | None:
        """Segmento del neopreno seleccionado para las lineas auxiliares."""
        line = getattr(self.line_result, "input_line", None)
        if line:
            return line

        idx = getattr(self, "_neopreno_record_selected_index", None)
        records = getattr(self, "_created_neopreno_records", []) or []
        if idx is not None and 0 <= idx < len(records):
            record = records[idx]
            start = record.get("start")
            end = record.get("end")
            if start is not None and end is not None:
                return AllplanGeo.Line3D(start, end)

        if hasattr(self.build_ele, "PuntoInicial") and hasattr(
            self.build_ele, "PuntoFinal"
        ):
            p0 = getattr(self.build_ele.PuntoInicial, "value", None)
            p1 = getattr(self.build_ele.PuntoFinal, "value", None)
            if p0 is not None and p1 is not None:
                try:
                    axis = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(p0.X, p0.Y, p0.Z),
                        AllplanGeo.Point3D(p1.X, p1.Y, p1.Z),
                    )
                    if AllplanGeo.CalcLength(axis) > 0.1:
                        return axis
                except Exception:
                    pass
        return None

    def _get_inline_selection_outward_vector(self) -> AllplanGeo.Vector3D | None:
        """Direccion para sacar las guias del muro y que se vean en planta/3D."""
        face_normal = getattr(self, "face_normal", None)
        if face_normal is not None:
            normal = _normalize_vector_selection(face_normal)
            if normal.GetLength() > 1e-6:
                return normal

        nx = ny = nz = None
        if hasattr(self.build_ele, "CaraNormalX"):
            nx = getattr(self.build_ele.CaraNormalX, "value", None)
        if hasattr(self.build_ele, "CaraNormalY"):
            ny = getattr(self.build_ele.CaraNormalY, "value", None)
        if hasattr(self.build_ele, "CaraNormalZ"):
            nz = getattr(self.build_ele.CaraNormalZ, "value", None)
        if nx is not None and ny is not None and nz is not None:
            normal = _normalize_vector_selection(
                AllplanGeo.Vector3D(float(nx), float(ny), float(nz))
            )
            if normal.GetLength() > 1e-6:
                return normal
        return None

    def _get_inline_selection_preview_overlay(self) -> list[Any]:
        """Solo lineas auxiliares (acuse visual de seleccion)."""
        return _build_neopreno_selection_auxiliary_elements(
            self._get_inline_selection_axis_line(),
            self._get_inline_selection_outward_vector(),
        )

    def _build_inline_selection_create_result(
        self,
        model_list: list[Any] | None = None,
    ) -> CreateElementResult:
        """
        Resultado de execute() en edicion inline: PPG en elements (si existe)
        y marco auxiliar siempre en preview_elements (o en elements si no hay PPG).
        """
        overlay = self._get_inline_selection_preview_overlay()
        handles = self._build_inline_edit_handles_result().handles
        connect_to_ele = ConnectToElements()
        if hasattr(self.build_ele, "MuroGUID") and getattr(
            self.build_ele.MuroGUID, "value", None
        ):
            mg = str(self.build_ele.MuroGUID.value or "").strip().strip("'").strip('"')
            if mg:
                connect_to_ele.connection_elements.append(mg)

        base_elements = list(model_list or [])
        preview_overlay = list(overlay)
        if not base_elements and preview_overlay:
            base_elements = list(preview_overlay)
            preview_overlay = []

        return CreateElementResult(
            elements=base_elements,
            handles=handles,
            preview_elements=preview_overlay,
            placement_point=AllplanGeo.Point3D(0.0, 0.0, 0.0),
            connect_to_ele=connect_to_ele,
            uuid_parameter_name="PythonPartUUID",
            multi_placement=True,
        )

    def _rebuild_session_preview_model_elements(self) -> list[Any]:
        """ModelElement3D de preview del neopreno en edicion inline."""
        if not self._sync_line_from_build_ele_points():
            return []
        line = getattr(self.line_result, "input_line", None)
        if not line:
            return []
        preview = self.draw_neopreno_preview(line)
        if not preview:
            return []
        try:
            return list(preview)
        except TypeError:
            return preview if isinstance(preview, list) else []

    def _refresh_inline_execute_cache(self) -> None:
        """Cache para execute(): nunca vacio mientras hay seleccion activa."""
        self.elements = self._rebuild_session_preview_model_elements()
        model_list = None
        idx = getattr(self, "_neopreno_record_selected_index", None)
        records = getattr(self, "_created_neopreno_records", []) or []
        if idx is not None and 0 <= idx < len(records):
            model_list = records[idx].get("model_list")

        self._inline_last_execute_result = self._build_inline_selection_create_result(
            model_list
        )
        cached = self._inline_last_execute_result
        neo_log(
            "_refresh_inline_execute_cache: "
            f"elements={len(cached.elements)} "
            f"preview_aux={len(cached.preview_elements)}"
        )

    def _execute_inline_selection_preview(self) -> CreateElementResult:
        """Regenera el marco auxiliar en cada execute() (posicion/parametros actuales)."""
        model_list = None
        cached = getattr(self, "_inline_last_execute_result", None)
        if cached is not None and cached.elements:
            model_list = list(cached.elements)

        idx = getattr(self, "_neopreno_record_selected_index", None)
        records = getattr(self, "_created_neopreno_records", []) or []
        if idx is not None and 0 <= idx < len(records):
            record_model_list = records[idx].get("model_list")
            if record_model_list:
                model_list = list(record_model_list)

        result = self._build_inline_selection_create_result(model_list)
        self._inline_last_execute_result = result
        return result

    def _draw_inline_selected_neopreno_preview(
        self, clear_before: bool = False
    ) -> bool:
        """Refuerzo visual del marco auxiliar (encima del preview del framework)."""
        if not getattr(self, "_inline_selected_neopreno_active", False):
            return False

        overlay = self._get_inline_selection_preview_overlay()
        if not overlay:
            print(
                "[SELECT][NEOPRENO] Sin linea auxiliar: no hay eje PuntoInicial/PuntoFinal"
            )
            return False

        doc = self._get_inline_preview_document()
        try:
            AllplanBaseElements.DrawElementPreview(
                doc, AllplanGeo.Matrix3D(), overlay, clear_before, None
            )
            return True
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error dibujando lineas auxiliares: {exc}")
            return False

    def _clear_framework_handles_and_controls(self) -> None:
        """Quita handles nativos y cotas dinamicas del input."""
        try:
            AllplanIFW.HandleService().RemoveHandles()
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] RemoveHandles: {exc}")
        try:
            AllplanIFW.BuildingElementInputControls().CloseControls()
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] CloseControls: {exc}")

    def _clear_inline_selection_visual(self) -> None:
        """Borra marco auxiliar y preview 3D del neopreno en edicion inline."""
        self._clear_framework_handles_and_controls()
        doc = self._get_inline_preview_document()
        if doc is None:
            return

        to_clear: list[Any] = []
        cached = getattr(self, "_inline_last_execute_result", None)
        if cached is not None:
            to_clear.extend(list(cached.elements or []))
            to_clear.extend(list(cached.preview_elements or []))
        session_elements = getattr(self, "elements", None) or []
        if session_elements:
            to_clear.extend(list(session_elements))

        aux_overlay = self._get_inline_selection_preview_overlay()
        if aux_overlay:
            to_clear.extend(aux_overlay)

        if not to_clear:
            return

        try:
            AllplanBaseElements.DrawElementPreview(
                doc, AllplanGeo.Matrix3D(), to_clear, True, None
            )
            print(
                f"[SELECT][NEOPRENO] Preview inline limpiado ({len(to_clear)} elementos)"
            )
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error limpiando preview inline: {exc}")

    def _apply_inline_edit_to_model(self, coord_input=None) -> bool:
        if not getattr(self, "_inline_selected_neopreno_active", False):
            return False
        if not self._inline_modification_ele_list:
            return False
        original_modification_list = self.modification_ele_list
        original_modification_mode = self.is_modification_mode
        try:
            if not self._sync_line_from_build_ele_points():
                return False
            self.modification_ele_list = self._inline_modification_ele_list
            self.is_modification_mode = True
            try:
                self.build_ele.set_insert_matrix(AllplanGeo.Matrix3D())
            except Exception:
                pass
            result = self._execute_modify()
            if not result or not result.elements:
                return False
            if coord_input:
                view_world_projection = coord_input.GetViewWorldProjection()
            else:
                view_world_projection = AllplanIFW.ViewWorldProjection()
            transaction = PythonPartTransaction(
                self.document,
                connect_to_ele=result.connect_to_ele,
            )
            created_elements = transaction.execute(
                placement_matrix=AllplanGeo.Matrix3D(),
                view_world_projection=view_world_projection,
                model_ele_list=result.elements,
                modification_ele_list=self._inline_modification_ele_list,
                rearrange_reinf_pos_nr=result.reinf_rearrange,
                append_reinf_pos_nr=True,
                asso_ref_object=None,
                uuid_parameter_name=result.uuid_parameter_name,
                elements_to_delete=result.elements_to_delete,
                use_system_angle=False,
            )
            new_pyp = None
            for element in created_elements:
                if AllplanBaseElements.PythonPartService.IsPythonPartGroupElement(
                    element
                ):
                    new_pyp = element
                    break
            if new_pyp is None:
                for element in created_elements:
                    if AllplanBaseElements.PythonPartService.IsPythonPartElement(
                        element
                    ):
                        new_pyp = element
                        break
            if new_pyp is not None:
                self._inline_modification_ele_list = ModificationElementList([new_pyp])
                idx = getattr(self, "_neopreno_record_selected_index", None)
                records = getattr(self, "_created_neopreno_records", []) or []
                fresh_params = self._read_neopreno_param_list_from_element(new_pyp)
                if idx is not None and 0 <= idx < len(records):
                    line = self.line_result.input_line
                    records[idx]["element"] = new_pyp
                    records[idx]["model_list"] = result.elements
                    records[idx]["param_list"] = fresh_params or records[idx].get(
                        "param_list", []
                    )
            self._inline_last_execute_result = result
            self._refresh_inline_execute_cache()
            return True
        except Exception as exc:
            print(f"[SELECT][NEOPRENO] Error aplicando edicion: {exc}")
            return False
        finally:
            self.modification_ele_list = original_modification_list
            self.is_modification_mode = original_modification_mode

    def _commit_inline_palette_change(self, property_name: str) -> bool:
        if not getattr(self, "_inline_selected_neopreno_active", False):
            return False
        if self.line_result.input_line:
            line = self.line_result.input_line
            if hasattr(self.build_ele, "PuntoInicial") and hasattr(
                self.build_ele, "PuntoFinal"
            ):
                self.build_ele.PuntoInicial.value = AllplanGeo.Point3D(
                    line.StartPoint.X, line.StartPoint.Y, line.StartPoint.Z
                )
                self.build_ele.PuntoFinal.value = AllplanGeo.Point3D(
                    line.EndPoint.X, line.EndPoint.Y, line.EndPoint.Z
                )
        self._apply_inline_edit_to_model()
        idx = getattr(self, "_neopreno_record_selected_index", None)
        if idx is not None:
            self._sync_neopreno_record_geometry_from_line(idx)
        self._refresh_inline_execute_cache()
        self._draw_inline_selected_neopreno_preview()
        return True

    def on_control_event(self, event_id: int):
        if event_id == NEOPRENO_EVENT_SELECT_EXISTING:
            return self._start_inline_neopreno_selection()
        if event_id == NEOPRENO_EVENT_DESELECT_EXISTING:
            return self._deselect_inline_neopreno()
        if event_id == NEOPRENO_EVENT_CHANGE_ACTIVE_WALL:
            return self._start_active_wall_selection()
        return True

    def _execute_modify(self) -> CreateElementResult:
        """Lógica completa de EDICIÓN: lee TODO desde build_ele, NUNCA escribe parámetros persistentes."""
        if not self._is_inline_neopreno_edit_session():
            self._apply_face_context_from_build_ele_only()
            self._ensure_line_result_from_build_ele_for_modify()
            self._try_sync_drag_offset_for_modify()

        start_point = None
        end_point = None
        wall_pare = ""
        wall_name = ""
        ancho = 50.0
        grosor = 5.0
        libre = True

        saved_state_str = ""
        if hasattr(self.build_ele, "SavedState") and hasattr(
            self.build_ele.SavedState, "value"
        ):
            saved_state_str = (self.build_ele.SavedState.value or "").strip()
        state = parse_saved_state(saved_state_str) if saved_state_str else {}
        p0_restored = saved_state_to_point3d(state, "p0")
        p1_restored = saved_state_to_point3d(state, "p1")
        current_start = None
        current_end = None
        if hasattr(self.build_ele, "PuntoInicial") and hasattr(
            self.build_ele, "PuntoFinal"
        ):
            current_start = self.build_ele.PuntoInicial.value
            current_end = self.build_ele.PuntoFinal.value

        if p0_restored is not None and p1_restored is not None:
            current_line = (
                AllplanGeo.Line3D(current_start, current_end)
                if current_start is not None and current_end is not None
                else None
            )
            if _is_valid_line(current_line):
                start_point = current_start
                end_point = current_end
            else:
                start_point = p0_restored
                end_point = p1_restored
            wall_pare = normalize_pmp_pare_value((state.get("pmp_pare") or "").strip())
            wall_name = normalize_pmp_pare_value(
                (state.get("pmp_pare_name") or "").strip()
            )
            if wall_pare == "SIN_IFC":
                wall_pare = ""
            if wall_name == "SIN_PARE":
                wall_name = ""
            ancho = (
                get_neopreno_width(self.build_ele)
                if hasattr(self.build_ele, "Ancho")
                else 50.0
            )
            grosor = (
                get_selected_thickness(self.build_ele)
                if hasattr(self.build_ele, "GrosorSeleccionado")
                else 5.0
            )
            libre = self._get_free_mode()
        else:
            current_line = (
                AllplanGeo.Line3D(current_start, current_end)
                if current_start is not None and current_end is not None
                else None
            )
            if _is_valid_line(current_line):
                start_point = current_start
                end_point = current_end
            else:
                neo_log(
                    "_execute_modify: estado geometrico invalido; no se regenera para evitar borrado"
                )
                return CreateElementResult(
                    elements=[],
                    handles=self.handles if hasattr(self, "handles") else [],
                    elements_to_delete=None,
                )

            if hasattr(self.build_ele, "pmp_pare") and hasattr(
                self.build_ele.pmp_pare, "value"
            ):
                wall_pare = (
                    normalize_pmp_pare_value(self.build_ele.pmp_pare.value)
                    if self.build_ele.pmp_pare.value
                    else ""
                )
            if wall_pare == "SIN_IFC":
                wall_pare = ""
            if not wall_pare:
                wall_pare = normalize_pmp_pare_value(self._resolve_host_pmp_pare())
            if hasattr(self.build_ele, "pmp_pare_name") and hasattr(
                self.build_ele.pmp_pare_name, "value"
            ):
                wall_name = (
                    normalize_pmp_pare_value(self.build_ele.pmp_pare_name.value)
                    if self.build_ele.pmp_pare_name.value
                    else ""
                )
            if wall_name == "SIN_PARE":
                wall_name = ""
            if not wall_name:
                wall_name = normalize_pmp_pare_value(self._resolve_host_pmp_pare_name())
            if hasattr(self.build_ele, "Ancho"):
                ancho = get_neopreno_width(self.build_ele)
            if hasattr(self.build_ele, "GrosorSeleccionado"):
                grosor = get_selected_thickness(self.build_ele)
            libre = self._get_free_mode()

        if not wall_pare:
            wall_pare = "SIN_IFC"
        if not wall_name:
            wall_name = "SIN_PARE"

        existing_group_hash = None
        if hasattr(self.build_ele, "get_hash"):
            try:
                existing_group_hash = self.build_ele.get_hash()
                if existing_group_hash:
                    pass
            except Exception as e:
                pass

        self.is_free_mode = libre

        line = AllplanGeo.Line3D(start_point, end_point)
        if not _is_valid_line(line):
            neo_log(
                "_execute_modify: linea de longitud cero; se cancela regeneracion para conservar PPG"
            )
            return CreateElementResult(
                elements=[],
                handles=self.handles if hasattr(self, "handles") else [],
                elements_to_delete=None,
            )
        if not self.line_result:
            from ScriptObjectInteractors.LineInteractor import LineInteractorResult

            self.line_result = LineInteractorResult()
        self.line_result.input_line = line

        local_line = line
        if not self.is_free_mode and self.detected_wall:
            try:
                wall_matrix = get_wall_placement_matrix(self.detected_wall)
                if wall_matrix:
                    inv_wall_matrix = wall_matrix.GetInverse()
                    if inv_wall_matrix:
                        local_start = inv_wall_matrix * line.StartPoint
                        local_end = inv_wall_matrix * line.EndPoint
                        local_line = AllplanGeo.Line3D(local_start, local_end)
            except Exception:
                pass

        if self.is_free_mode:
            line_to_use = local_line
        else:
            line_to_use, _ = self._prepare_line(
                local_line, is_already_in_local_coords=True
            )

        self.line_result.input_line = line_to_use

        self._init_pmp_attribute_ids()
        neo_log(
            "_execute_modify: atributos destino "
            f"PMP_PARE={getattr(self, 'attr_pmp_pare_id', 0)} "
            f"PMP_WALL_ID={getattr(self, 'attr_pmp_wall_id', 0)} "
            f"valor_ifc='{wall_pare}' valor_material='{wall_name}'"
        )

        self.elements = self._create_neopreno_elements(
            pmp_pare=wall_pare,
            pmp_pare_name=wall_name,
        )

        if not self.elements:
            return CreateElementResult(
                self.elements if hasattr(self, "elements") and self.elements else [],
                self.handles if hasattr(self, "handles") else [],
            )

        individual_pp = self.create_individual_pythonparts_from_elements(
            self.elements,
            pmp_pare=wall_pare,
            pmp_pare_name=wall_name,
            is_modify=True,  # Hash estable en edición
        )

        if not individual_pp:
            return CreateElementResult(
                self.elements if hasattr(self, "elements") and self.elements else [],
                self.handles if hasattr(self, "handles") else [],
            )

        if existing_group_hash:
            group_hash = existing_group_hash
        else:
            group_hash = create_element_hash(
                "neopreno_group", stable=True  # EDIT = estable
            )

        z_unique = 0.0
        if hasattr(self.build_ele, "z_unique") and hasattr(
            self.build_ele.z_unique, "value"
        ):
            try:
                z_unique = float(self.build_ele.z_unique.value)
            except (ValueError, TypeError):
                z_unique = 0.0
        rot = 0.0
        if hasattr(self.build_ele, "RotacionManual"):
            rv = getattr(self.build_ele.RotacionManual, "value", None)
            if rv is not None:
                rot = rv.GetDeg() if hasattr(rv, "GetDeg") else float(rv)
        invertido = False
        if hasattr(self.build_ele, "InvertirGrosor"):
            val = getattr(self.build_ele.InvertirGrosor, "value", None)
            if val is not None:
                invertido = (
                    bool(val)
                    if isinstance(val, bool)
                    else str(val).lower() in ("true", "1", "yes")
                )
        saved_state_str = self._serialize_state_to_json()
        if (
            saved_state_str
            and hasattr(self.build_ele, "SavedState")
            and hasattr(self.build_ele.SavedState, "value")
        ):
            self.build_ele.SavedState.value = saved_state_str

        global_params = {
            "z_unique": z_unique,
            "pmp_pare": wall_pare,
            "pmp_pare_name": wall_name,
            "TotalElements": len(individual_pp),
            "PuntoInicial": start_point,
            "PuntoFinal": end_point,
            "Ancho": ancho,
            "Grosor": grosor,
            "Libre": libre,
            "PermitirPickUpLinea": self._get_allow_line_pickup(),
            "RotacionManual": rot,
            "InvertirGrosor": invertido,
            "SavedState": saved_state_str if isinstance(saved_state_str, str) else "",
        }

        param_list = create_params_list_from_dict(global_params)
        python_file_name = (
            self.build_ele.pyp_file_name
            if hasattr(self.build_ele, "pyp_file_name")
            else ""
        )

        pythonpart_group = PythonPartGroup(
            "Neoprenos", param_list, group_hash, python_file_name, individual_pp
        )

        model_elem_list = pythonpart_group.create()

        if not model_elem_list or len(model_elem_list) == 0:
            return CreateElementResult(
                self.elements if hasattr(self, "elements") and self.elements else [],
                self.handles if hasattr(self, "handles") else [],
            )

        handles: list[HandleProperties] = []
        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if (
            not coord_input
            and self.script_object_interactor
            and hasattr(self.script_object_interactor, "coord_input")
        ):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, "RotacionManual"):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, "GetDeg"):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            line_for_handles = (
                self.line_result.input_line
                if self.line_result and self.line_result.input_line
                else None
            )
            if line_for_handles:
                x_dir_handle, y_dir_handle, z_dir_handle = (
                    build_face_local_axes_for_handles(
                        line_for_handles.StartPoint,
                        line_for_handles.EndPoint,
                        self.face_point,
                        self.face_normal,
                    )
                )

        if self.line_result and self.line_result.input_line:
            current_line = self.line_result.input_line
            handles = create_handles(
                self.build_ele,
                current_line,
                self.face_normal,
                coord_input,
                rotation_deg,
                self.is_free_mode,
                x_dir_handle,
                y_dir_handle,
                z_dir_handle,
            )
        else:
            punto_inicial = getattr(self.build_ele, "PuntoInicial", None)
            punto_final = getattr(self.build_ele, "PuntoFinal", None)
            if (
                punto_inicial
                and punto_final
                and punto_inicial.value
                and punto_final.value
            ):
                fallback_line = AllplanGeo.Line3D(
                    punto_inicial.value, punto_final.value
                )
                handles = create_handles(
                    self.build_ele,
                    fallback_line,
                    self.face_normal,
                    coord_input,
                    rotation_deg,
                    self.is_free_mode,
                    x_dir_handle,
                    y_dir_handle,
                    z_dir_handle,
                )

        self.handles = handles

        if self._restored_from_saved_state:
            self._save_state_to_build_ele()

        return CreateElementResult(
            elements=model_elem_list,
            handles=handles,
            placement_point=AllplanGeo.Point3D(0, 0, 0),
            uuid_parameter_name="PythonPartUUID",
            multi_placement=False,
        )

    def move_handle(
        self, handle_prop: HandleProperties, input_pnt: AllplanGeo.Point3D
    ) -> CreateElementResult:
        """
        Maneja el movimiento de handles.
        """
        handle_name = handle_prop.name if hasattr(handle_prop, "name") else "unknown"
        input_pnt_final = input_pnt
        if (
            not self.is_free_mode
            and self.face_normal
            and self.face_point
            and self.face_polygon
        ):
            current_point = None
            if handle_name == "PuntoInicialHandle":
                start_prop = getattr(self.build_ele, "PuntoInicial", None)
                if start_prop and hasattr(start_prop, "value") and start_prop.value:
                    current_point = start_prop.value
            elif handle_name == "PuntoFinalHandle":
                end_prop = getattr(self.build_ele, "PuntoFinal", None)
                if end_prop and hasattr(end_prop, "value") and end_prop.value:
                    current_point = end_prop.value
            elif handle_name == "AnchoHandle":
                start_prop = getattr(self.build_ele, "PuntoInicial", None)
                end_prop = getattr(self.build_ele, "PuntoFinal", None)
                if start_prop and end_prop and start_prop.value and end_prop.value:
                    current_point = AllplanGeo.Point3D(
                        (start_prop.value.X + end_prop.value.X) / 2.0,
                        (start_prop.value.Y + end_prop.value.Y) / 2.0,
                        (start_prop.value.Z + end_prop.value.Z) / 2.0,
                    )

            if current_point:
                if self.line_result and self.line_result.input_line:
                    line_for_axes = self.line_result.input_line
                else:
                    start_prop = getattr(self.build_ele, "PuntoInicial", None)
                    end_prop = getattr(self.build_ele, "PuntoFinal", None)
                    if start_prop and end_prop and start_prop.value and end_prop.value:
                        line_for_axes = AllplanGeo.Line3D(
                            start_prop.value, end_prop.value
                        )
                    else:
                        line_for_axes = None

                if line_for_axes:
                    x_dir_handle, y_dir_handle, z_dir_handle = (
                        build_face_local_axes_for_handles(
                            line_for_axes.StartPoint,
                            line_for_axes.EndPoint,
                            self.face_point,
                            self.face_normal,
                        )
                    )

                    if x_dir_handle and y_dir_handle and z_dir_handle:
                        current_proj = project_point_to_face_plane(
                            current_point, self.face_point, self.face_normal
                        )
                        input_proj = project_point_to_face_plane(
                            input_pnt, self.face_point, self.face_normal
                        )

                        u_current, v_current = world_to_uv_face(
                            current_proj, self.face_point, x_dir_handle, y_dir_handle
                        )
                        u_input, v_input = world_to_uv_face(
                            input_proj, self.face_point, x_dir_handle, y_dir_handle
                        )

                        du = u_input - u_current
                        dv = v_input - v_current

                        u_min, u_max, v_min, v_max = get_face_uv_bounds(
                            self.face_polygon,
                            self.face_point,
                            self.face_normal,
                            x_dir_handle,
                            y_dir_handle,
                        )

                        u_new = max(u_min, min(u_max, u_current + du))
                        v_new = max(v_min, min(v_max, v_current + dv))

                        new_point_uv = uv_to_world_face(
                            u_new, v_new, self.face_point, x_dir_handle, y_dir_handle
                        )
                        new_point_proj = project_point_to_face_plane(
                            new_point_uv, self.face_point, self.face_normal
                        )

                        dist_to_plane = abs(
                            vector_dot(
                                AllplanGeo.Vector3D(
                                    new_point_proj.X - self.face_point.X,
                                    new_point_proj.Y - self.face_point.Y,
                                    new_point_proj.Z - self.face_point.Z,
                                ),
                                normalize_vector(self.face_normal)
                                or AllplanGeo.Vector3D(0, 0, 1),
                            )
                        )

                        input_pnt_final = new_point_proj

        HandlePropertiesService.update_property_value(
            self.build_ele, handle_prop, input_pnt_final
        )

        start_prop = getattr(self.build_ele, "PuntoInicial", None)
        end_prop = getattr(self.build_ele, "PuntoFinal", None)
        start_point = (
            start_prop.value if start_prop and hasattr(start_prop, "value") else None
        )
        end_point = end_prop.value if end_prop and hasattr(end_prop, "value") else None

        if start_point and end_point:
            self.line_result.input_line = AllplanGeo.Line3D(start_point, end_point)
            self._process_line_input()
        else:
            self.line_result.input_line = None

        get_neopreno_width(self.build_ele)

        if getattr(self, "_inline_selected_neopreno_active", False):
            self._apply_inline_edit_to_model(self._get_active_coord_input())
            idx = getattr(self, "_neopreno_record_selected_index", None)
            if idx is not None:
                self._sync_neopreno_record_geometry_from_line(idx)
            self._refresh_inline_execute_cache()
            cached = getattr(self, "_inline_last_execute_result", None)
            handles = self._build_inline_edit_handles_result().handles
            if cached is not None and cached.elements:
                return CreateElementResult(
                    elements=cached.elements,
                    handles=handles,
                    placement_point=getattr(
                        cached, "placement_point", AllplanGeo.Point3D(0.0, 0.0, 0.0)
                    ),
                    connect_to_ele=getattr(cached, "connect_to_ele", None),
                    uuid_parameter_name=getattr(
                        cached, "uuid_parameter_name", "PythonPartUUID"
                    ),
                    multi_placement=True,
                )
            return self._build_inline_edit_handles_result()

        return self.execute()

    def get_or_create_layer_in_group(
        self, group_name: str, short_name: str, long_name: str
    ) -> int:
        """Busca la layer por short_name o la crea en el grupo usando CreateLayer.
        LayerManager no existe en NemAll_Python_BaseElements; se usa CreateLayer.
        """
        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(
            short_name, self.document
        )
        if layer_id > 0:
            return layer_id

        return AllplanBaseElements.CreateLayer(
            self.document,
            group_name,
            "",
            long_name,
            short_name,
            1,
            1,
            1,
            True,
            True,
        )

    def _create_neopreno_elements(
        self, pmp_pare: str = None, pmp_pare_name: str = None
    ) -> List[AllplanBasisElements.ModelElement3D]:
        """Crea los elementos del neopreno como ModelElement3D individuales.

        Args:
            pmp_pare: Valor de PMP_PARE a aplicar
        """
        if not self.line_result or not self.line_result.input_line:
            return []

        line = self.line_result.input_line

        if AllplanGeo.CalcLength(line) < 0.1:
            return []

        if self.is_free_mode:
            line_to_use = line
        else:
            line_to_use, _ = self._prepare_line(line)

        longitud = AllplanGeo.CalcLength(line_to_use)
        if hasattr(self.build_ele, "Longitud"):
            self.build_ele.Longitud.value = longitud

        grosor = get_selected_thickness(self.build_ele)
        update_color_for_thickness(self.build_ele)
        ancho = get_neopreno_width(self.build_ele)

        invertir_grosor = False
        if self.is_free_mode and hasattr(self.build_ele, "InvertirGrosor"):
            val = self.build_ele.InvertirGrosor.value
            if isinstance(val, bool):
                invertir_grosor = not val
            elif isinstance(val, str):
                invertir_grosor = val.lower() not in ("true", "1", "yes")
            else:
                invertir_grosor = not bool(val)

        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if (
            not coord_input
            and self.script_object_interactor
            and hasattr(self.script_object_interactor, "coord_input")
        ):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, "RotacionManual"):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, "GetDeg"):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        solid = create_neopreno_solid_on_face(
            line_to_use,
            ancho,
            grosor,
            self.face_normal if not self.is_free_mode else None,
            self.face_point if not self.is_free_mode else None,
            invertir_grosor,
            coord_input,
            rotation_deg,
            AllplanGeo.Matrix3D(),
            self.is_free_mode,
        )

        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(
            NEO_LAYER, self.document
        )

        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()
        common_props.Color = (
            self.build_ele.Color.value if hasattr(self.build_ele, "Color") else 15
        )
        common_props.Pen = (
            self.build_ele.Pen.value if hasattr(self.build_ele, "Pen") else 1
        )
        common_props.Stroke = (
            self.build_ele.Stroke.value if hasattr(self.build_ele, "Stroke") else 1
        )
        common_props.Layer = layer_id

        attr_list = BuildingElementAttributeList()
        pmp_pare = normalize_pmp_pare_value(pmp_pare)
        pmp_pare_name = normalize_pmp_pare_value(pmp_pare_name)

        if (
            getattr(self, "attr_pmp_pare_id", 0) <= 0
            or getattr(self, "attr_pmp_wall_id", 0) <= 0
        ):
            self._init_pmp_attribute_ids()

        attr_id = getattr(self, "attr_pmp_pare_id", 0)
        attr_wall_id = getattr(self, "attr_pmp_wall_id", 0)
        neo_log(
            "_create_neopreno_elements: "
            f"attr_pmp_pare_id={attr_id} value='{pmp_pare_name}' "
            f"attr_pmp_wall_id={attr_wall_id} value='{pmp_pare}'"
        )
        if attr_id > 0 and pmp_pare_name:
            attr_list.add_attribute(attr_id, pmp_pare_name)
        if attr_wall_id > 0 and pmp_pare:
            attr_list.add_attribute(attr_wall_id, pmp_pare)

        elements = []
        if solid:
            elem = AllplanBasisElements.ModelElement3D(common_props, solid)
            if attr_list.get_attribute_list():
                elem.SetAttributes(attr_list.get_attribute_list())
            elements.append(elem)
        else:
            elem = AllplanBasisElements.ModelElement3D(common_props, line)
            if attr_list.get_attribute_list():
                elem.SetAttributes(attr_list.get_attribute_list())
            elements.append(elem)

        return elements

    def create_individual_pythonparts_from_elements(
        self,
        elements_list: List[AllplanBasisElements.ModelElement3D],
        pmp_pare: str = None,
        pmp_pare_name: str = None,
        is_modify: bool = False,
    ) -> List[PythonPart]:
        """
        Convierte una lista de ModelElement3D en PythonParts individuales.
        Cada elemento 3D se envuelve en su propia PythonPart para que GSI pueda leerlos individualmente.

        Args:
            elements_list: Lista de ModelElement3D creados
            pmp_pare: Valor de PMP_PARE a aplicar
            is_modify: Si True, usa hash estable (para edición)

        Returns:
            Lista de PythonParts individuales
        """

        pythonparts_list = []

        python_file_name = (
            self.build_ele.pyp_file_name
            if hasattr(self.build_ele, "pyp_file_name")
            else ""
        )

        for idx, element in enumerate(elements_list):
            try:
                common_props = (
                    element.GetCommonProperties()
                    if hasattr(element, "GetCommonProperties")
                    else AllplanBaseElements.CommonProperties()
                )
                if not hasattr(common_props, "Layer") or common_props.Layer <= 0:
                    layer_id = AllplanBaseElements.LayerService.GetIDByShortName(
                        NEO_LAYER, self.document
                    )
                    common_props.Layer = layer_id

                if (
                    getattr(self, "attr_pmp_pare_id", 0) <= 0
                    or getattr(self, "attr_pmp_wall_id", 0) <= 0
                ):
                    self._init_pmp_attribute_ids()

                attr_list = BuildingElementAttributeList()
                attr_pmp_id = getattr(self, "attr_pmp_pare_id", 0)
                attr_wall_name_id = getattr(self, "attr_pmp_wall_id", 0)

                wall_pare = normalize_pmp_pare_value(pmp_pare)
                wall_name = normalize_pmp_pare_value(pmp_pare_name)
                neo_log(
                    "create_individual_pythonparts_from_elements: "
                    f"attr_pmp_pare_id={attr_pmp_id} value='{wall_name}' "
                    f"attr_pmp_wall_id={attr_wall_name_id} value='{wall_pare}'"
                )
                if wall_name and attr_pmp_id > 0:
                    attr_list.add_attribute(attr_pmp_id, wall_name)
                if wall_pare and attr_wall_name_id > 0:
                    attr_list.add_attribute(attr_wall_name_id, wall_pare)

                attribute_list = attr_list.get_attribute_list()

                views = [View2D3D([element])]

                params = {
                    "ElementIndex": idx,
                    "ElementType": type(element).__name__,
                    "Layer": common_props.Layer,
                    "Color": common_props.Color,
                    "Pen": common_props.Pen,
                    "Stroke": common_props.Stroke,
                }

                line = (
                    self.line_result.input_line
                    if self.line_result and self.line_result.input_line
                    else None
                )
                if line:
                    params.update(
                        {
                            "StartX": line.StartPoint.X,
                            "StartY": line.StartPoint.Y,
                            "StartZ": line.StartPoint.Z,
                            "EndX": line.EndPoint.X,
                            "EndY": line.EndPoint.Y,
                            "EndZ": line.EndPoint.Z,
                        }
                    )

                params["Ancho"] = (
                    get_neopreno_width(self.build_ele)
                    if hasattr(self.build_ele, "Ancho")
                    else 50.0
                )
                params["Grosor"] = (
                    get_selected_thickness(self.build_ele)
                    if hasattr(self.build_ele, "GrosorSeleccionado")
                    else 5.0
                )
                params["FreeMode"] = bool(getattr(self, "is_free_mode", False))

                rot = 0.0
                if hasattr(self.build_ele, "RotacionManual"):
                    rot_val = getattr(self.build_ele.RotacionManual, "value", None)
                    if rot_val is not None:
                        rot = (
                            rot_val.GetDeg()
                            if hasattr(rot_val, "GetDeg")
                            else float(rot_val)
                        )
                params["RotacionManual"] = rot

                invertido = False
                if hasattr(self.build_ele, "InvertirGrosor"):
                    val = getattr(self.build_ele.InvertirGrosor, "value", None)
                    if val is not None:
                        invertido = (
                            bool(val)
                            if isinstance(val, bool)
                            else str(val).lower() in ("true", "1", "yes")
                        )
                params["InvertirGrosor"] = invertido

                hash_params = {
                    key: (
                        round(float(value), 6)
                        if isinstance(value, (int, float))
                        and not isinstance(value, bool)
                        else value
                    )
                    for key, value in params.items()
                }

                hash_value = create_element_hash(
                    "neopreno_element", stable=is_modify, **hash_params
                )

                param_list = create_params_list_from_dict(params)

                element_name = f"NeoprenoElement_{idx}"

                pythonpart = PythonPart(
                    element_name,
                    parameter_list=param_list,
                    hash_value=hash_value,
                    python_file=python_file_name,
                    views=views,
                    common_props=common_props,
                    attribute_list=attribute_list if attribute_list else None,
                )

                pythonparts_list.append(pythonpart)

            except Exception as e:
                import traceback

                continue

        return pythonparts_list

    def on_cancel_function(self) -> OnCancelFunctionResult:
        if hasattr(self.build_ele, "IsModify"):
            is_modify = self.build_ele.IsModify()
        else:
            is_modify = getattr(self, "is_modification_mode", False)

        if is_modify:
            self.interactor_state = STOPPED
            self.script_object_interactor = None
            has_points = False
            if hasattr(self.build_ele, "PuntoInicial") and hasattr(
                self.build_ele, "PuntoFinal"
            ):
                p0 = self.build_ele.PuntoInicial.value
                p1 = self.build_ele.PuntoFinal.value
                has_points = (
                    p0 is not None
                    and p1 is not None
                    and _is_valid_line(AllplanGeo.Line3D(p0, p1))
                )
            has_saved_state = False
            if hasattr(self.build_ele, "SavedState") and hasattr(
                self.build_ele.SavedState, "value"
            ):
                state = parse_saved_state(
                    (self.build_ele.SavedState.value or "").strip()
                )
                has_saved_state = (
                    saved_state_to_point3d(state, "p0") is not None
                    and saved_state_to_point3d(state, "p1") is not None
                )
            if not (has_points or has_saved_state):
                neo_log(
                    "on_cancel_function: MODIFY sin puntos/SavedState -> CANCEL_INPUT para conservar PPG"
                )
                return OnCancelFunctionResult.CANCEL_INPUT
            return OnCancelFunctionResult.CREATE_ELEMENTS

        if self.line_result and self.line_result.input_line:
            self._pending_create_edit = False
            self.interactor_state = STOPPED
            self.script_object_interactor = None
            return OnCancelFunctionResult.CREATE_ELEMENTS

        if self._pending_create_edit:
            self._pending_create_edit = False
            return OnCancelFunctionResult.CREATE_ELEMENTS

        return OnCancelFunctionResult.CANCEL_INPUT
