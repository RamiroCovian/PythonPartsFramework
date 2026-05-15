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
from PythonPartTransaction import ConnectToElements
from ScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor
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

MIN_WIDTH = 20.0
MIN_WIDTH_HALF = MIN_WIDTH / 2.0
MAX_HANDLE_DISTANCE = 100000.0

NEO_LAYER = "PMP_NEOPRENS"



def build_saved_state_dict(
    p0: AllplanGeo.Point3D,
    p1: AllplanGeo.Point3D,
    ancho: float,
    grosor: float,
    libre: bool,
    pmp_pare: str,
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
        pmp_pare: metadata del muro
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
        "pmp_pare": str(pmp_pare or ""),
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


def saved_state_to_point3d(state: Dict[str, Any], key: str) -> AllplanGeo.Point3D | None:
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
        z_unique_val = params.get('z_unique', params.get('ZUnique', 0))
        if z_unique_val and z_unique_val != 0:
            param_string += f"_z={z_unique_val}"

    hash_val = hashlib.sha224(param_string.encode('utf-8')).hexdigest()
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
        if '=' in param_str:
            parts = param_str.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().rstrip('\n').strip()
                try:
                    if '.' in value:
                        params[key] = float(value)
                    else:
                        params[key] = int(value)
                except ValueError:
                    if value.startswith('Point3D('):
                        try:
                            coords = value.replace('Point3D(', '').replace(')', '').split(',')
                            if len(coords) == 3:
                                params[key] = AllplanGeo.Point3D(
                                    float(coords[0].strip()),
                                    float(coords[1].strip()),
                                    float(coords[2].strip())
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


def cross_product(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(
        v1.Y * v2.Z - v1.Z * v2.Y,
        v1.Z * v2.X - v1.X * v2.Z,
        v1.X * v2.Y - v1.Y * v2.X
    )


def calc_distance_3d(point1: AllplanGeo.Point3D, point2: AllplanGeo.Point3D) -> float:
    return AllplanGeo.CalcLength(
        AllplanGeo.Vector3D(
            point2.X - point1.X,
            point2.Y - point1.Y,
            point2.Z - point1.Z
        )
    )


def vector_add(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(v1.X + v2.X, v1.Y + v2.Y, v1.Z + v2.Z)


def vector_scale(vector: AllplanGeo.Vector3D, factor: float) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(vector.X * factor, vector.Y * factor, vector.Z * factor)


def vector_dot(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> float:
    return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z


def rotate_vector_around_axis(vector: AllplanGeo.Vector3D,
                              axis: AllplanGeo.Vector3D,
                              angle_rad: float) -> AllplanGeo.Vector3D:
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


def get_view_plane_normal(coord_input: AllplanIFW.CoordinateInput = None) -> AllplanGeo.Vector3D:
    try:
        if coord_input:
            view_proj = coord_input.GetViewWorldProjection()
            if view_proj and isinstance(view_proj, AllplanGeo.Matrix3D):
                view_z = AllplanGeo.Vector3D(
                    view_proj.m20,
                    view_proj.m21,
                    view_proj.m22
                )
                view_z_normalized = normalize_vector(view_z)
                if view_z_normalized:
                    abs_x = abs(view_z_normalized.X)
                    abs_y = abs(view_z_normalized.Y)
                    abs_z = abs(view_z_normalized.Z)

                    if abs_x > abs_y and abs_x > abs_z:
                        return AllplanGeo.Vector3D(1, 0, 0) if view_z_normalized.X > 0 else AllplanGeo.Vector3D(-1, 0, 0)
                    if abs_y > abs_z:
                        return AllplanGeo.Vector3D(0, 1, 0) if view_z_normalized.Y > 0 else AllplanGeo.Vector3D(0, -1, 0)
                    return AllplanGeo.Vector3D(0, 0, 1) if view_z_normalized.Z > 0 else AllplanGeo.Vector3D(0, 0, -1)
    except Exception:
        pass
    return AllplanGeo.Vector3D(0, 0, 1)


def get_selected_thickness(build_ele: BuildingElement) -> float:
    if hasattr(build_ele, 'GrosorSeleccionado') and build_ele.GrosorSeleccionado.value is not None:
        return float(build_ele.GrosorSeleccionado.value)
    return 5.0


def get_neopreno_width(build_ele: BuildingElement, default: float = 50.0) -> float:
    min_width = 20.0

    if hasattr(build_ele, 'Ancho') and build_ele.Ancho.value is not None:
        try:
            width_value = float(build_ele.Ancho.value)
        except (TypeError, ValueError):
            width_value = default
    else:
        width_value = default

    width_value = max(min_width, width_value)

    if hasattr(build_ele, 'Ancho'):
        build_ele.Ancho.value = width_value

    return width_value


def get_color_for_thickness(thickness: float) -> int:
    color_map = {
        5.0: 15,
        10.0: 4,
        20.0: 5,
        30.0: 8,
        40.0: 3
    }
    return color_map.get(thickness, 15)


def update_color_for_thickness(build_ele: BuildingElement):
    if not build_ele or not hasattr(build_ele, 'GrosorSeleccionado'):
        return

    thickness = get_selected_thickness(build_ele)
    color_number = get_color_for_thickness(thickness)

    if hasattr(build_ele, 'Color'):
        build_ele.Color.value = color_number


def calculate_local_coordinate_system(face_polygon: AllplanGeo.Polygon3D,
                                     face_normal: AllplanGeo.Vector3D) -> dict:
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
            (min_point.Z + max_point.Z) / 2.0
        )

        p0 = face_polygon.GetPoint(0)
        p1 = face_polygon.GetPoint(1)
        edge_vector = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)

        dot = edge_vector.X * axis_w.X + edge_vector.Y * axis_w.Y + edge_vector.Z * axis_w.Z
        axis_u = AllplanGeo.Vector3D(
            edge_vector.X - dot * axis_w.X,
            edge_vector.Y - dot * axis_w.Y,
            edge_vector.Z - dot * axis_w.Z
        )

        axis_u = normalize_vector(axis_u)
        if not axis_u:
            axis_u = AllplanGeo.Vector3D(1, 0, 0) if abs(axis_w.X) < 0.9 else AllplanGeo.Vector3D(0, 1, 0)

        axis_v = cross_product(axis_w, axis_u)
        axis_v = normalize_vector(axis_v)

        u_coords = []
        v_coords = []

        for i in range(face_polygon.Count()):
            vertex = face_polygon.GetPoint(i)
            vec_from_origin = AllplanGeo.Vector3D(
                vertex.X - origin.X,
                vertex.Y - origin.Y,
                vertex.Z - origin.Z
            )
            u_coords.append(vec_from_origin.DotProduct(axis_u))
            v_coords.append(vec_from_origin.DotProduct(axis_v))

        width = max(u_coords) - min(u_coords)
        height = max(v_coords) - min(v_coords)

        return {
            'origin': origin,
            'axis_u': axis_u,
            'axis_v': axis_v,
            'axis_w': axis_w,
            'width': width,
            'height': height,
            'min_point': min_point,
            'max_point': max_point
        }

    except Exception:
        return None


def calculate_relative_position(point: AllplanGeo.Point3D,
                               local_system: dict) -> dict:
    try:
        if not local_system:
            return None

        origin = local_system['origin']
        axis_u = local_system['axis_u']
        axis_v = local_system['axis_v']
        width = local_system['width']
        height = local_system['height']

        to_point = AllplanGeo.Vector3D(
            point.X - origin.X,
            point.Y - origin.Y,
            point.Z - origin.Z
        )

        u_absolute = to_point.X * axis_u.X + to_point.Y * axis_u.Y + to_point.Z * axis_u.Z
        v_absolute = to_point.X * axis_v.X + to_point.Y * axis_v.Y + to_point.Z * axis_v.Z

        u_relative = (u_absolute / width + 0.5) if width > 0.001 else 0.5
        v_relative = (v_absolute / height + 0.5) if height > 0.001 else 0.5

        return {
            'u': u_relative,
            'v': v_relative,
            'u_absolute': u_absolute,
            'v_absolute': v_absolute,
            'distance_from_origin': AllplanGeo.CalcLength(to_point)
        }

    except Exception:
        return None


def calculate_position_from_uv(u_relative: float,
                               v_relative: float,
                               local_system: dict) -> AllplanGeo.Point3D:
    try:
        if not local_system:
            return None

        origin = local_system['origin']
        axis_u = local_system['axis_u']
        axis_v = local_system['axis_v']
        width = local_system['width']
        height = local_system['height']

        u_absolute = (u_relative - 0.5) * width
        v_absolute = (v_relative - 0.5) * height

        point = AllplanGeo.Point3D(
            origin.X + u_absolute * axis_u.X + v_absolute * axis_v.X,
            origin.Y + u_absolute * axis_u.Y + v_absolute * axis_v.Y,
            origin.Z + u_absolute * axis_u.Z + v_absolute * axis_v.Z
        )

        return point

    except Exception:
        return None


def project_line_on_face(line: AllplanGeo.Line3D,
                        face_point: AllplanGeo.Point3D,
                         face_normal: AllplanGeo.Vector3D) -> AllplanGeo.Line3D:
    try:
        normal = normalize_vector(face_normal)
        if not normal:
            return line

        nx, ny, nz = normal.X, normal.Y, normal.Z

        is_horizontal = abs(nz) > 0.9

        if is_horizontal:
            return AllplanGeo.Line3D(
                AllplanGeo.Point3D(line.StartPoint.X, line.StartPoint.Y, face_point.Z),
                AllplanGeo.Point3D(line.EndPoint.X, line.EndPoint.Y, face_point.Z)
            )
        else:
            center = AllplanGeo.Point3D(
                (line.StartPoint.X + line.EndPoint.X) / 2.0,
                (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
                (line.StartPoint.Z + line.EndPoint.Z) / 2.0
            )

            t = nx * (center.X - face_point.X) + \
                ny * (center.Y - face_point.Y) + \
                nz * (center.Z - face_point.Z)

            projected_center = AllplanGeo.Point3D(
                center.X - t * nx,
                center.Y - t * ny,
                center.Z - t * nz
            )

            offset = AllplanGeo.Vector3D(
                projected_center.X - center.X,
                projected_center.Y - center.Y,
                projected_center.Z - center.Z
            )

            return AllplanGeo.Line3D(
                AllplanGeo.Point3D(
                    line.StartPoint.X + offset.X,
                    line.StartPoint.Y + offset.Y,
                    line.StartPoint.Z + offset.Z
                ),
                AllplanGeo.Point3D(
                    line.EndPoint.X + offset.X,
                    line.EndPoint.Y + offset.Y,
                    line.EndPoint.Z + offset.Z
                )
            )

    except Exception:
        return line


def build_face_local_axes_for_handles(start_point: AllplanGeo.Point3D,
                                     end_point: AllplanGeo.Point3D,
                                     face_point: AllplanGeo.Point3D,
                                     face_normal: AllplanGeo.Vector3D) -> tuple[AllplanGeo.Vector3D | None, AllplanGeo.Vector3D | None, AllplanGeo.Vector3D | None]:
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
        end_proj.X - start_proj.X,
        end_proj.Y - start_proj.Y,
        end_proj.Z - start_proj.Z
    )
    x_dir = normalize_vector(proj_vec)

    if not x_dir:
        return None, None, None

    z_dir_normalized = normalize_vector(face_normal)
    if not z_dir_normalized:
        return None, None, None

    z_dir = AllplanGeo.Vector3D(-z_dir_normalized.X, -z_dir_normalized.Y, -z_dir_normalized.Z)

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


def project_point_to_face_plane(p: AllplanGeo.Point3D,
                                face_point: AllplanGeo.Point3D,
                                face_normal: AllplanGeo.Vector3D) -> AllplanGeo.Point3D:
    """Proyecta un punto al plano definido por face_point y face_normal."""
    n = normalize_vector(face_normal)
    if not n:
        return p

    v = AllplanGeo.Vector3D(
        p.X - face_point.X,
        p.Y - face_point.Y,
        p.Z - face_point.Z
    )

    d = vector_dot(v, n)

    return AllplanGeo.Point3D(
        p.X - n.X * d,
        p.Y - n.Y * d,
        p.Z - n.Z * d
    )


def get_view_ray_from_mouse(coord_input: AllplanIFW.CoordinateInput,
                            mouse_point_2d: AllplanGeo.Point2D) -> tuple[AllplanGeo.Point3D | None, AllplanGeo.Vector3D | None]:
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
            inv_view_proj.m30,
            inv_view_proj.m31,
            inv_view_proj.m32
        )

        ray_direction = AllplanGeo.Vector3D(
            mouse_world_approx.X - ray_origin.X,
            mouse_world_approx.Y - ray_origin.Y,
            mouse_world_approx.Z - ray_origin.Z
        )

        ray_direction = normalize_vector(ray_direction)
        if not ray_direction:
            return None, None

        return ray_origin, ray_direction

    except Exception:
        return None, None


def intersect_ray_with_face_plane(ray_origin: AllplanGeo.Point3D,
                                  ray_direction: AllplanGeo.Vector3D,
                                  face_point: AllplanGeo.Point3D,
                                  face_normal: AllplanGeo.Vector3D) -> AllplanGeo.Point3D | None:
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
        face_point.Z - ray_origin.Z
    )

    denom = vector_dot(ray_dir_norm, n)

    if abs(denom) < 1e-6:
        return None

    t = vector_dot(vec_to_face, n) / denom

    intersection_point = AllplanGeo.Point3D(
        ray_origin.X + ray_dir_norm.X * t,
        ray_origin.Y + ray_dir_norm.Y * t,
        ray_origin.Z + ray_dir_norm.Z * t
    )

    return intersection_point


def world_to_uv_face(p: AllplanGeo.Point3D,
                     origin: AllplanGeo.Point3D,
                     u_dir: AllplanGeo.Vector3D,
                     v_dir: AllplanGeo.Vector3D) -> tuple[float, float]:
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
    v = AllplanGeo.Vector3D(
        p.X - origin.X,
        p.Y - origin.Y,
        p.Z - origin.Z
    )
    u = vector_dot(v, u_dir)
    v_coord = vector_dot(v, v_dir)
    return u, v_coord


def uv_to_world_face(u: float,
                     v: float,
                     origin: AllplanGeo.Point3D,
                     u_dir: AllplanGeo.Vector3D,
                     v_dir: AllplanGeo.Vector3D) -> AllplanGeo.Point3D:
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
        origin.Z + u_dir.Z * u + v_dir.Z * v
    )


def get_face_uv_bounds(face_polygon: AllplanGeo.Polygon3D,
                      face_point: AllplanGeo.Point3D,
                      face_normal: AllplanGeo.Vector3D,
                      u_dir: AllplanGeo.Vector3D,
                      v_dir: AllplanGeo.Vector3D) -> tuple[float, float, float, float]:
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


def apply_line_projection_or_translation(line: AllplanGeo.Line3D,
                                         face_point: AllplanGeo.Point3D,
                                         face_normal: AllplanGeo.Vector3D,
                                         max_displacement: float = 50000) -> AllplanGeo.Line3D:
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
            face_point.Z - line.StartPoint.Z
        )

        return AllplanGeo.Line3D(
            AllplanGeo.Point3D(
                line.StartPoint.X + offset.X,
                line.StartPoint.Y + offset.Y,
                line.StartPoint.Z + offset.Z
            ),
            AllplanGeo.Point3D(
                line.EndPoint.X + offset.X,
                line.EndPoint.Y + offset.Y,
                line.EndPoint.Z + offset.Z
            )
        )


def create_neopreno_solid_on_face(line: AllplanGeo.Line3D,
                                 ancho: float,
                                 grosor: float,
                                 face_normal: AllplanGeo.Vector3D = None,
                                 face_point: AllplanGeo.Point3D = None,
                                 invertir_grosor: bool = False,
                                 coord_input: AllplanIFW.CoordinateInput = None,
                                 rotation_deg: float = 0.0,
                                 placement_matrix: AllplanGeo.Matrix3D = None,
                                 is_free_mode: bool = False) -> AllplanGeo.BRep3D:
    """Crea el solido del neopreno.

    Args:
        is_free_mode: Si True, usa posicionamiento libre.
    """
    try:
        raw_start = line.StartPoint
        raw_end = line.EndPoint

        if not is_free_mode and face_normal and face_point:
            punto_inicial = project_point_to_face_plane(raw_start, face_point, face_normal)
            punto_final = project_point_to_face_plane(raw_end, face_point, face_normal)
        else:
            punto_inicial = raw_start
            punto_final = raw_end

        vector_longitud = AllplanGeo.Vector3D(
            punto_final.X - punto_inicial.X,
            punto_final.Y - punto_inicial.Y,
            punto_final.Z - punto_inicial.Z
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
                        vector_ancho = cross_product(vector_longitud, AllplanGeo.Vector3D(0, 0, 1))
                    elif abs(vector_longitud.Y) < 0.9:
                        vector_ancho = cross_product(vector_longitud, AllplanGeo.Vector3D(0, 1, 0))
                    else:
                        vector_ancho = cross_product(vector_longitud, AllplanGeo.Vector3D(1, 0, 0))
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
                    -vector_ancho.X,
                    -vector_ancho.Y,
                    -vector_ancho.Z
                )
                vector_grosor = cross_product(vector_ancho, vector_longitud)
                vector_grosor = normalize_vector(vector_grosor)
                if not vector_grosor:
                    vector_grosor = get_view_plane_normal(coord_input)

            if abs(rotation_deg) > 1e-6:
                rotation_rad = math.radians(rotation_deg)
                vector_ancho = rotate_vector_around_axis(vector_ancho, vector_longitud, rotation_rad)
                vector_grosor = rotate_vector_around_axis(vector_grosor, vector_longitud, rotation_rad)
                vector_ancho = normalize_vector(vector_ancho) or vector_ancho
                vector_grosor = normalize_vector(cross_product(vector_ancho, vector_longitud)) or vector_grosor

            desplazamiento_centrado = ancho / 2.0
            longitud_vector_ancho = AllplanGeo.CalcLength(vector_ancho)

            if longitud_vector_ancho < 0.1:
                punto_inicio = punto_inicial
            else:
                punto_inicio = AllplanGeo.Point3D(
                    punto_inicial.X - vector_ancho.X * desplazamiento_centrado,
                    punto_inicial.Y - vector_ancho.Y * desplazamiento_centrado,
                    punto_inicial.Z - vector_ancho.Z * desplazamiento_centrado
                )

            vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                -vector_grosor.X,
                -vector_grosor.Y,
                -vector_grosor.Z
            )
        else:
            if face_normal and face_point:
                x_dir_solid, y_dir_solid, z_dir_solid = build_face_local_axes_for_handles(
                    punto_inicial,
                    punto_final,
                    face_point,
                    face_normal
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
                                -vector_grosor.X,
                                -vector_grosor.Y,
                                -vector_grosor.Z
                            )
                            vector_longitud = normalize_vector(cross_product(vector_ancho, vector_grosor))
                            if not vector_longitud:
                                vector_longitud = normalize_vector(AllplanGeo.Vector3D(
                                    punto_final.X - punto_inicial.X,
                                    punto_final.Y - punto_inicial.Y,
                                    punto_final.Z - punto_inicial.Z
                                ))
                                if not vector_longitud:
                                    vector_longitud = x_dir_solid

                    offset_centro = grosor * 0.5
                    punto_inicio = AllplanGeo.Point3D(
                        punto_inicial.X + vector_grosor.X * offset_centro,
                        punto_inicial.Y + vector_grosor.Y * offset_centro,
                        punto_inicial.Z + vector_grosor.Z * offset_centro
                    )

                    vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                        -vector_grosor.X,
                        -vector_grosor.Y,
                        -vector_grosor.Z
                    )
                else:
                    vector_grosor = normalize_vector(face_normal) if face_normal else AllplanGeo.Vector3D(0, 0, 1)
                    vector_ancho = cross_product(vector_longitud, vector_grosor)
                    vector_ancho = normalize_vector(vector_ancho) or AllplanGeo.Vector3D(0, 1, 0)
                    punto_inicio = punto_inicial
                    vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                        -vector_grosor.X,
                        -vector_grosor.Y,
                        -vector_grosor.Z
                    )
            else:
                vector_grosor = AllplanGeo.Vector3D(0, 0, 1)
                vector_ancho = cross_product(vector_longitud, vector_grosor)
                vector_ancho = normalize_vector(vector_ancho) or AllplanGeo.Vector3D(0, 1, 0)
                punto_inicio = punto_inicial
                vector_grosor_para_cuboid = AllplanGeo.Vector3D(
                    -vector_grosor.X,
                    -vector_grosor.Y,
                    -vector_grosor.Z
                )

        axis_placement = AllplanGeo.AxisPlacement3D(
            punto_inicio,
            vector_longitud,
            vector_grosor_para_cuboid
        )

        cuboid = AllplanGeo.BRep3D.CreateCuboid(
            axis_placement,
            longitud,
            ancho,
            grosor
        )

        return cuboid

    except Exception:
        return None


def create_handles(build_ele: BuildingElement,
                   line: AllplanGeo.Line3D,
                   face_normal: AllplanGeo.Vector3D | None = None,
                   coord_input: AllplanIFW.CoordinateInput = None,
                   rotation_deg: float = 0.0,
                   is_free_mode: bool = False,
                   x_dir: AllplanGeo.Vector3D | None = None,
                   y_dir: AllplanGeo.Vector3D | None = None,
                   z_dir: AllplanGeo.Vector3D | None = None) -> list[HandleProperties]:
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
        punto_final.Z - punto_inicial.Z
    )
    line_direction = normalize_vector(line_direction_vec) or AllplanGeo.Vector3D(1.0, 0.0, 0.0)

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
                info_text="Punto inicial de la linea"
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
                info_text="Punto final de la linea"
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
                info_text="Punto inicial de la linea"
            )
        )

        handle_list.append(
            HandleProperties(
                "PuntoFinalHandle",
                punto_final,
                punto_inicial,
                [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                HandleDirection.XYZ_DIR,
                info_text="Punto final de la linea"
            )
        )

    width_value = get_neopreno_width(build_ele)
    midpoint = AllplanGeo.Point3D(
        (punto_inicial.X + punto_final.X) / 2.0,
        (punto_inicial.Y + punto_final.Y) / 2.0,
        (punto_inicial.Z + punto_final.Z) / 2.0
    )

    if is_free_mode:
        if face_normal:
            vector_grosor = normalize_vector(face_normal)
            if not vector_grosor:
                vector_grosor = get_view_plane_normal(coord_input)
        else:
            vector_grosor = get_view_plane_normal(coord_input)

        width_direction = cross_product(line_direction, vector_grosor)
        width_direction = normalize_vector(width_direction) or AllplanGeo.Vector3D(0.0, 1.0, 0.0)

        if abs(rotation_deg) > 1e-6:
            rotation_rad = math.radians(rotation_deg)
            width_direction = rotate_vector_around_axis(width_direction, line_direction, rotation_rad)
            width_direction = normalize_vector(width_direction) or width_direction

        width_handle_point = AllplanGeo.Point3D(
            midpoint.X + width_direction.X * (width_value / 2.0),
            midpoint.Y + width_direction.Y * (width_value / 2.0),
            midpoint.Z + width_direction.Z * (width_value / 2.0)
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
                        dir_vector=width_direction
                    )
                ],
                HandleDirection.VECTOR_DIR,
                dir_vector=width_direction
            )
        )
    else:
        if handle_plane and y_dir:
            width_direction = normalize_vector(y_dir) or AllplanGeo.Vector3D(0.0, 1.0, 0.0)
            width_handle_point = AllplanGeo.Point3D(
                midpoint.X + width_direction.X * (width_value / 2.0),
                midpoint.Y + width_direction.Y * (width_value / 2.0),
                midpoint.Z + width_direction.Z * (width_value / 2.0)
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
                            dir_vector=width_direction
                        )
                    ],
                    HandleDirection.PLANE_DIR,
                    plane=handle_plane,
                    dir_vector=width_direction
                )
            )
        else:
            normal_vector = normalize_vector(face_normal) if face_normal else None
            if not normal_vector and hasattr(build_ele, 'CaraNormalX'):
                normal_vector = normalize_vector(
                    AllplanGeo.Vector3D(
                        getattr(build_ele.CaraNormalX, "value", 0.0),
                        getattr(build_ele.CaraNormalY, "value", 0.0),
                        getattr(build_ele.CaraNormalZ, "value", 1.0)
                    )
                )
            normal_vector = normal_vector or AllplanGeo.Vector3D(0.0, 0.0, 1.0)
            width_direction = normalize_vector(cross_product(line_direction, normal_vector)) or AllplanGeo.Vector3D(0.0, 1.0, 0.0)

            width_handle_point = AllplanGeo.Point3D(
                midpoint.X + width_direction.X * (width_value / 2.0),
                midpoint.Y + width_direction.Y * (width_value / 2.0),
                midpoint.Z + width_direction.Z * (width_value / 2.0)
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
                            dir_vector=width_direction
                        )
                    ],
                    HandleDirection.VECTOR_DIR,
                    dir_vector=width_direction
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
                    HandleParameterData("PuntoFinal", HandleParameterType.POINT)
                ],
                HandleDirection.XYZ_DIR,
                dir_vector=None
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
        'GetPlacementMatrix',
        'GetTransformationMatrix',
        'GetModelMatrix',
        'GetWorldMatrix',
        'GetMatrix'
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
            success, matrix = AllplanBaseElements.PythonPartService.GetPlacementMatrix(wall_element)
            if success and isinstance(matrix, AllplanGeo.Matrix3D):
                placement_matrix = matrix
        except Exception:
            pass

    return placement_matrix


def get_wall_ifc_id(wall_element) -> str | None:
    """Obtiene el nombre del muro desde el atributo Material (id 508) o buscando en todos los atributos.

    El nombre esta separado por $, por ejemplo "AP$PV_!0" → nombre = "AP"
    (la parte antes del primer $).

    Args:
        wall_element: Elemento del muro

    Returns:
        Nombre del muro (parte antes del $) o None si no se encuentra
    """

    if not wall_element:
        return None

    try:
        from DocumentManager import DocumentManager
        doc = DocumentManager.get_instance().document

        attrs = wall_element.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable)
        material_value_from_508 = None
        for attr in attrs:
            try:
                attr_id = getattr(attr, "Id", None)
                if attr_id is None and isinstance(attr, (tuple, list)) and len(attr) >= 2:
                    attr_id = attr[0]
                    attr_value = attr[1]
                else:
                    attr_value = getattr(attr, "Value", None)

                if attr_id == 683:
                    material_value_from_508 = str(attr_value).strip() if attr_value else ""
                    return material_value_from_508
            except Exception:
                continue

    except Exception:
        pass

    return None


class WallSelectResult:
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.is_selected = False


class WallSelectInteractor(BaseScriptObjectInteractor):

    def __init__(self, result: WallSelectResult, prompt_msg: str = "Seleccione el muro", script_object=None):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg
        self.script_object = script_object

        self.sel_query = AllplanIFW.SelectionQuery([
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Volume3D_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Area3D_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Wall_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.WallTier_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Column_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Beam_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Slab_TypeUUID),
        ])

        self.element_filter = AllplanIFW.ElementSelectFilterSetting(self.sel_query, True)

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        if self.script_object:
            self.script_object._saved_coord_input = coord_input
        if coord_input:
            coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert(self.prompt_msg)
            )

    def process_mouse_msg(self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: Any) -> bool:
        if not self.coord_input:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
            return True

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())
        self.result.is_selected = True

        return False

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

    def __init__(self, result: SolidFaceSelectResult, prompt_msg: str = "Seleccione la cara del solido"):
        self.result = result
        self.coord_input = None
        self.prompt_msg = prompt_msg

        self.sel_query = AllplanIFW.SelectionQuery([
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Volume3D_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Area3D_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Wall_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.WallTier_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Column_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Beam_TypeUUID),
            AllplanIFW.QueryTypeID(AllplanEleAdapter.Slab_TypeUUID),
        ])

        self.element_filter = AllplanIFW.ElementSelectFilterSetting(self.sel_query, True)

    def start_input(self, coord_input: AllplanIFW.CoordinateInput):
        self.coord_input = coord_input
        coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(self.prompt_msg)
        )

    def process_mouse_msg(self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: Any) -> bool:
        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        is_selected, face_polygon, intersect_result = self._select_face(selected_element, pnt)

        if not is_selected:
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            if intersect_result and hasattr(intersect_result, 'IntersectionPoint'):
                self._draw_face_normal_preview(intersect_result)
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())

        if intersect_result and hasattr(intersect_result, 'IntersectionPoint'):
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
                    ray_origin,
                    ray_direction,
                    face_point_approx,
                    face_normal
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
            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    element, pnt, True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(), True
                )
            if is_selected:
                return is_selected, face_polygon, intersect_result
        except Exception:
            pass

        try:
            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    element, pnt, True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(), True
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
            common_props,
            AllplanGeo.Line3D(point_at_face, point_at_face + normal * 500)
        )

        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            [ray],
            True,
            None
        )

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass


def create_script_object(
    build_ele: BuildingElement,
    script_object_data: BaseScriptObjectData
) -> BaseScriptObject:
    return NeoprenosScriptObject(build_ele, script_object_data)


class NeoprenosScriptObject(BaseScriptObject):

    def __init__(
        self,
        build_ele: BuildingElement,
        script_object_data: BaseScriptObjectData
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
        self.parent_element = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None

        self.ref_face_element = None
        self.ref_face_polygon = None


        self._saved_coord_input = self.coord_input if self.coord_input else None

        self.is_editing_existing = bool(
            hasattr(self.build_ele, "SavedState") and
            isinstance(self.build_ele.SavedState.value, str) and
            self.build_ele.SavedState.value.strip()
        )
        self._restored_from_saved_state = False
        self.is_free_mode = self._get_free_mode()
        self.needs_auto_update = False

        if hasattr(self.build_ele, "SavedState"):
            ss = getattr(self.build_ele.SavedState, "value", None)
            if isinstance(ss, str) and ss.strip():
                self._restored_from_saved_state = self._deserialize_state_from_json(ss)
        if not self._restored_from_saved_state and hasattr(self, "script_object_data") and self.script_object_data:
            param_list_src = getattr(self.script_object_data, "param_list", None)
            if param_list_src:
                for p in param_list_src:
                    s = p.strip()
                    if s.startswith("SavedState = ") or s.startswith("SavedState="):
                        _, _, rest = p.partition("=")
                        val = rest.strip().rstrip("\n").strip()
                        if val:
                            try:
                                if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                                    val = ast.literal_eval(val)
                            except Exception:
                                pass
                            if isinstance(val, str) and val:
                                self._restored_from_saved_state = self._deserialize_state_from_json(val)
                            break

        if self.is_editing_existing:
            self._load_saved_connection_info()
        if self._restored_from_saved_state:
            self.is_free_mode = self._get_free_mode()

        self._update_parameter_visibility()


    def _get_free_mode(self) -> bool:
        if hasattr(self.build_ele, 'neopreno_libre'):
            val = self.build_ele.neopreno_libre.value
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ('true', '1', 'yes')
            return bool(val)
        return False

    def _update_parameter_visibility(self):
        pass

    def _serialize_state_to_json(self) -> str:
        """
        Serializa el estado actual de build_ele a JSON para guardar en SavedState.
        Incluye "v": 1 para poder migrar formato más adelante.
        """
        try:
            p0 = self.build_ele.PuntoInicial.value if hasattr(self.build_ele, "PuntoInicial") else None
            p1 = self.build_ele.PuntoFinal.value if hasattr(self.build_ele, "PuntoFinal") else None
            if p0 is None or p1 is None:
                return ""

            grosor = None
            if hasattr(self.build_ele, "GrosorSeleccionado") and self.build_ele.GrosorSeleccionado.value is not None:
                grosor = float(self.build_ele.GrosorSeleccionado.value)
            ancho = None
            if hasattr(self.build_ele, "Ancho") and self.build_ele.Ancho.value is not None:
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
                rot = rv.GetDeg() if hasattr(rv, "GetDeg") else float(rv) if rv is not None else 0.0

            invertido = False
            if hasattr(self.build_ele, "InvertirGrosor") and self.build_ele.InvertirGrosor.value is not None:
                val = self.build_ele.InvertirGrosor.value
                invertido = bool(val) if isinstance(val, bool) else str(val).lower() in ("true", "1", "yes")

            pmp_pare = ""
            if hasattr(self.build_ele, "pmp_pare") and self.build_ele.pmp_pare.value is not None:
                pmp_pare = str(self.build_ele.pmp_pare.value).strip()

            layer = -1
            if hasattr(self.build_ele, "Layer") and self.build_ele.Layer.value is not None:
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
                "rot": rot,
                "invertido": invertido,
                "pmp_pare": pmp_pare,
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
                self.build_ele.PuntoInicial.value = AllplanGeo.Point3D(float(p0[0]), float(p0[1]), float(p0[2]))
            if hasattr(self.build_ele, "PuntoFinal"):
                self.build_ele.PuntoFinal.value = AllplanGeo.Point3D(float(p1[0]), float(p1[1]), float(p1[2]))

            if "ancho" in state and state["ancho"] is not None and hasattr(self.build_ele, "Ancho"):
                self.build_ele.Ancho.value = float(state["ancho"])

            if "grosor" in state and state["grosor"] is not None and hasattr(self.build_ele, "GrosorSeleccionado"):
                self.build_ele.GrosorSeleccionado.value = float(state["grosor"])

            if "libre" in state and hasattr(self.build_ele, "neopreno_libre"):
                self.build_ele.neopreno_libre.value = bool(state["libre"])

            if "rot" in state and state["rot"] is not None and hasattr(self.build_ele, "RotacionManual"):
                try:
                    self.build_ele.RotacionManual.value = float(state["rot"])
                except (TypeError, ValueError):
                    pass

            if "invertido" in state and hasattr(self.build_ele, "InvertirGrosor"):
                self.build_ele.InvertirGrosor.value = bool(state["invertido"])

            if "pmp_pare" in state and hasattr(self.build_ele, "pmp_pare"):
                self.build_ele.pmp_pare.value = str(state["pmp_pare"] or "")

            if "layer" in state and state["layer"] is not None and hasattr(self.build_ele, "Layer"):
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
            if hasattr(self.build_ele, "SavedState") and hasattr(self.build_ele.SavedState, "value"):
                ss = self.build_ele.SavedState.value
                if isinstance(ss, str) and ss.strip():
                    return self._deserialize_state_from_json(ss)
        except Exception as e:
            return False

    def _save_state_to_build_ele(self):
        """
        Guarda el estado actual serializado en build_ele.SavedState.
        Se llama justo antes de crear el grupo / antes del return final en CREATE y EDIT.
        """
        try:
            if hasattr(self.build_ele, "SavedState") and hasattr(self.build_ele.SavedState, "value"):
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
        if not hasattr(self, 'script_object_data') or not self.script_object_data:
            return {}

        param_list = getattr(self.script_object_data, 'param_list', None)
        if not param_list:
            return {}

        params = {}
        for p in param_list:
            try:
                if '=' in p:
                    key, val = p.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    params[key] = eval(val)
            except Exception as e:
                pass

        return params

    def _check_if_editing_existing(self) -> bool:
        if (hasattr(self.build_ele, 'z_unique') and
            self.build_ele.z_unique.value > 0 and
            hasattr(self.build_ele, 'PuntoInicial') and
            hasattr(self.build_ele, 'PuntoFinal') and
            self.build_ele.PuntoInicial.value is not None and
            self.build_ele.PuntoFinal.value is not None):

            existing_line = AllplanGeo.Line3D(
                self.build_ele.PuntoInicial.value,
                self.build_ele.PuntoFinal.value
            )
            if AllplanGeo.CalcLength(existing_line) > 0.1:
                self.line_result.input_line = existing_line
                return True

        return False


    def _load_saved_connection_info(self):
        """Carga la informacion de conexion guardada cuando se esta editando."""
        if self.is_free_mode:
            if hasattr(self.build_ele, 'MuroConnection') and \
               self.build_ele.MuroConnection.value and \
               hasattr(self.build_ele.MuroConnection.value, 'element') and \
               self.build_ele.MuroConnection.value.element.IsValid():
                self.detected_wall = self.build_ele.MuroConnection.value.element
                self.detected_wall_guid = str(self.detected_wall.GetModelElementUUID())
            elif hasattr(self.build_ele, 'MuroGUID') and self.build_ele.MuroGUID.value:
                self.detected_wall_guid = self.build_ele.MuroGUID.value
                try:
                    wall_guid = AllplanEleAdapter.GUID.FromString(self.detected_wall_guid)
                    self.detected_wall = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                        wall_guid,
                        self.document
                    )
                    if self.detected_wall and not self.detected_wall.IsNull():
                        if hasattr(self.build_ele, 'MuroConnection'):
                            self.build_ele.MuroConnection.value.element = self.detected_wall
                except Exception:
                    pass
            elif hasattr(self.build_ele, 'MuroConnection') and \
                 self.build_ele.MuroConnection.value.uuid:
                self.detected_wall_guid = str(self.build_ele.MuroConnection.value.uuid)
        else:
            if hasattr(self.build_ele, 'SolidoGUID') and self.build_ele.SolidoGUID.value:
                self.solid_info = {
                    'guid': self.build_ele.SolidoGUID.value
                }
            elif hasattr(self.build_ele, 'SolidoConnection') and \
                 self.build_ele.SolidoConnection.value.uuid:
                self.solid_info = {
                    'guid': str(self.build_ele.SolidoConnection.value.uuid)
                }

    def _get_face_local_system(self) -> dict[str, Any] | None:
        if not self.face_polygon or not self.face_normal:
            return None
        return calculate_local_coordinate_system(self.face_polygon, self.face_normal)

    def _clamp_point_to_face(self,
                             point: AllplanGeo.Point3D,
                             local_system: dict[str, Any] | None = None) -> AllplanGeo.Point3D:
        if local_system is None:
            local_system = self._get_face_local_system()

        if not local_system:
            return point

        relative = calculate_relative_position(point, local_system)
        if not relative:
            return point

        u_clamped = min(max(relative['u'], 0.0), 1.0)
        v_clamped = min(max(relative['v'], 0.0), 1.0)

        clamped_point = calculate_position_from_uv(u_clamped, v_clamped, local_system)
        return clamped_point if clamped_point else point

    def _clamp_line_to_face(self,
                            line: AllplanGeo.Line3D,
                            local_system: dict[str, Any] | None = None) -> tuple[AllplanGeo.Line3D, dict[str, Any] | None]:
        if local_system is None:
            local_system = self._get_face_local_system()

        if not local_system:
            return line, None

        start = self._clamp_point_to_face(line.StartPoint, local_system)
        end = self._clamp_point_to_face(line.EndPoint, local_system)

        return AllplanGeo.Line3D(start, end), local_system

    def _max_distance_to_face(self,
                              origin: AllplanGeo.Point3D,
                              direction: AllplanGeo.Vector3D,
                              local_system: dict[str, Any]) -> float:
        direction_norm = normalize_vector(direction)
        if not direction_norm:
            return 0.0

        far_point = AllplanGeo.Point3D(
            origin.X + direction_norm.X * MAX_HANDLE_DISTANCE,
            origin.Y + direction_norm.Y * MAX_HANDLE_DISTANCE,
            origin.Z + direction_norm.Z * MAX_HANDLE_DISTANCE
        )

        clamped_point = self._clamp_point_to_face(far_point, local_system)
        return calc_distance_3d(origin, clamped_point)

    def _adjust_width_to_face(self,
                              line: AllplanGeo.Line3D,
                              local_system: dict[str, Any]) -> float:
        current_width = get_neopreno_width(self.build_ele)

        midpoint = AllplanGeo.Point3D(
            (line.StartPoint.X + line.EndPoint.X) / 2.0,
            (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
            (line.StartPoint.Z + line.EndPoint.Z) / 2.0
        )

        line_vector = AllplanGeo.Vector3D(
            line.EndPoint.X - line.StartPoint.X,
            line.EndPoint.Y - line.StartPoint.Y,
            line.EndPoint.Z - line.StartPoint.Z
        )
        line_direction = normalize_vector(line_vector) or AllplanGeo.Vector3D(1.0, 0.0, 0.0)

        face_normal = normalize_vector(self.face_normal) if self.face_normal else None
        if not face_normal and local_system.get('axis_w'):
            face_normal = normalize_vector(local_system['axis_w'])
        if not face_normal:
            face_normal = AllplanGeo.Vector3D(0.0, 0.0, 1.0)

        width_direction = normalize_vector(cross_product(line_direction, face_normal))
        if not width_direction:
            axis_v = local_system.get('axis_v')
            width_direction = normalize_vector(axis_v) if axis_v else None
        if not width_direction:
            width_direction = AllplanGeo.Vector3D(0.0, 1.0, 0.0)

        max_plus = self._max_distance_to_face(midpoint, width_direction, local_system)
        max_minus = self._max_distance_to_face(
            midpoint,
            AllplanGeo.Vector3D(-width_direction.X, -width_direction.Y, -width_direction.Z),
            local_system
        )

        max_half_width = min(max_plus, max_minus)
        if max_half_width <= 0.0:
            return current_width

        desired_half_width = current_width / 2.0
        new_half_width = min(desired_half_width, max_half_width)

        min_half_width = min(MIN_WIDTH_HALF, max_half_width)
        new_half_width = max(new_half_width, min_half_width)

        new_width = new_half_width * 2.0

        if hasattr(self.build_ele, 'Ancho'):
            self.build_ele.Ancho.value = new_width

        return new_width

    def _prepare_line(self,
                      line: AllplanGeo.Line3D,
                      adjust_width: bool = True,
                      is_already_in_local_coords: bool = False) -> tuple[AllplanGeo.Line3D, dict[str, Any] | None]:
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
            line = apply_line_projection_or_translation(
                line, self.face_point, self.face_normal
            )
            line, local_system = self._clamp_line_to_face(line)

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

        if hasattr(self.build_ele, 'SolidoConnection'):
            conn = self.build_ele.SolidoConnection.value
            if hasattr(conn, 'element') and conn.element.IsValid():
                solid_element = conn.element

        if not solid_element or solid_element.IsNull():
            if hasattr(self.build_ele, 'SolidoGUID') and self.build_ele.SolidoGUID.value:
                solid_guid = AllplanEleAdapter.GUID.FromString(self.build_ele.SolidoGUID.value)
                solid_element = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                    solid_guid,
                    self.document
                )

        return solid_element

    def _get_stored_normal(self):
        return AllplanGeo.Vector3D(
            self.build_ele.CaraNormalX.value if hasattr(self.build_ele, 'CaraNormalX') else 0,
            self.build_ele.CaraNormalY.value if hasattr(self.build_ele, 'CaraNormalY') else 0,
            self.build_ele.CaraNormalZ.value if hasattr(self.build_ele, 'CaraNormalZ') else 1
        )

    def _get_stored_point(self):
        return AllplanGeo.Point3D(
            self.build_ele.PuntoClicX.value if hasattr(self.build_ele, 'PuntoClicX') else 0,
            self.build_ele.PuntoClicY.value if hasattr(self.build_ele, 'PuntoClicY') else 0,
            self.build_ele.PuntoClicZ.value if hasattr(self.build_ele, 'PuntoClicZ') else 0
        )

    def _find_face_index(self, solid_element, selected_face_polygon, selected_face_normal=None):
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
                (minmax.Min.Z + minmax.Max.Z) / 2.0
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
                success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(solid_geo, face)

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
                    (minmax.Min.Z + minmax.Max.Z) / 2.0
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
                    candidates.append({
                        'index': i,
                        'distance': distance,
                        'dot': dot,
                        'center': face_center
                    })

            if selected_normal:
                candidates.sort(key=lambda x: (-x['dot'], x['distance']))
                for c in candidates:
                    if c['dot'] > 0.7:
                        return c['index']
            else:
                candidates.sort(key=lambda x: x['distance'])
                if candidates and candidates[0]['distance'] < 100.0:
                    return candidates[0]['index']

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
            success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(solid_geo, face)

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
                success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(solid_geo, face)

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
                            (minmax.Min.Z + minmax.Max.Z) / 2.0
                        )

                        distance_to_stored = calc_distance_3d(face_center, stored_point)

                        MAX_DISTANCE = 1000.0  # mm

                        if distance_to_stored <= MAX_DISTANCE:
                            candidate_faces.append({
                                'index': i,
                                'polygon': face_polygon,
                                'normal': face_normal,
                                'center': face_center,
                                'dot': dot,
                                'distance': distance_to_stored
                            })
                        pass

            if not candidate_faces:
                return False, None, None

            candidate_faces.sort(key=lambda x: x['distance'])

            best_candidate = candidate_faces[0]
            face_polygon = best_candidate['polygon']
            face_normal = best_candidate['normal']
            face_center = best_candidate['center']
            best_dot = best_candidate['dot']

            if best_dot < 0:
                face_normal = AllplanGeo.Vector3D(
                    -face_normal.X,
                    -face_normal.Y,
                    -face_normal.Z
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
                (min_max.Min.Z + min_max.Max.Z) / 2.0
            )
            center_2d = AllplanGeo.Point2D(center.X, center.Y)

            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    solid_element, center_2d, True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(), True
                )

            if is_selected:
                return is_selected, face_polygon, intersect_result

            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    solid_element, center_2d, True,
                    self.coord_input.GetViewWorldProjection(),
                    self.coord_input.GetInputViewDocument(), True
                )

            return is_selected, face_polygon, intersect_result

        except Exception:
            return False, None, None

    def start_input(self):
        """Inicia el input del script."""

        if self.is_editing_existing:
            self.is_free_mode = self._get_free_mode()
            self._update_parameter_visibility()


            if self.line_result and self.line_result.input_line:
                self._process_line_input()

            self.interactor_state = STOPPED
            self.script_object_interactor = None
            return

        if hasattr(self.build_ele, 'neopreno_libre'):
            val = self.build_ele.neopreno_libre.value
            if isinstance(val, bool):
                self.is_free_mode = val
            elif isinstance(val, str):
                self.is_free_mode = val.lower() in ('true', '1', 'yes')
            else:
                self.is_free_mode = bool(val)
        else:
            self.is_free_mode = False

        self._update_parameter_visibility()

        if hasattr(self.build_ele, 'neopreno_libre'):
            self.build_ele.neopreno_libre.value = bool(self.is_free_mode)

        if self.is_free_mode:
            self.wall_select_result = WallSelectResult()
            self.interactor_state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el muro",
                script_object=self
            )
            coord_input_to_use = self._saved_coord_input if self._saved_coord_input else self.coord_input
            if coord_input_to_use:
                self.script_object_interactor.start_input(coord_input_to_use)
        else:
            self.interactor_state = SELECTING_SOLID
            self.script_object_interactor = SolidFaceSelectInteractor(
                self.face_select_result,
            )
            coord_input_to_use = self._saved_coord_input if self._saved_coord_input else self.coord_input
            if coord_input_to_use:
                self.script_object_interactor.start_input(coord_input_to_use)

    def start_next_input(self):
        """Gestiona la transicion entre interactors."""
        if self.interactor_state == SELECTING_WALL:
            if self.wall_select_result.is_selected:
                self._process_wall_selection()
                self.interactor_state = SELECTING_LINE
                self._start_line_input()
            else:
                self.interactor_state = STOPPED
                self.script_object_interactor = None

        elif self.interactor_state == SELECTING_SOLID:
            if self.face_select_result.is_selected:
                self._process_solid_selection()
                self.interactor_state = SELECTING_LINE
                self._start_line_input()
            else:
                self.interactor_state = STOPPED
                self.script_object_interactor = None

        elif self.interactor_state == SELECTING_LINE:
            if self.line_result.input_line:
                if self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
                    self._saved_coord_input = self.script_object_interactor.coord_input
                self._process_line_input()

            self.interactor_state = STOPPED
            self.script_object_interactor = None

    def _process_wall_selection(self):
        element_guid_str = self.wall_select_result.element_guid
        selected_element = self.wall_select_result.element

        self.detected_wall = selected_element
        real_wall_guid = str(selected_element.GetModelElementUUID())
        self.detected_wall_guid = real_wall_guid

        self.wall_ifc_id = get_wall_ifc_id(selected_element)

        if hasattr(self.build_ele, 'MuroConnection'):
            self.build_ele.MuroConnection.value.element = selected_element
            if str(self.build_ele.MuroConnection.value.uuid) == "00000000-0000-0000-0000-000000000000":
                try:
                    element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(real_wall_guid)
                    element_from_guid = AllplanBaseElements.ElementsService.GetElement(element_guid)
                    if element_from_guid and element_from_guid.IsValid():
                        self.build_ele.MuroConnection.value.element = element_from_guid
                except Exception:
                    pass
        if hasattr(self.build_ele, 'MuroGUID'):
            self.build_ele.MuroGUID.value = real_wall_guid

    def _process_solid_selection(self):
        self.face_point = self.face_select_result.face_point
        self.face_normal = self.face_select_result.face_normal
        self.face_polygon = self.face_select_result.face_polygon

        element_guid_str = self.face_select_result.element_guid
        selected_element = self.face_select_result.element

        self.ref_face_element = selected_element
        self.ref_face_polygon = self.face_polygon

        face_index = self._find_face_index(selected_element, self.face_polygon, self.face_normal)
        if face_index is not None and hasattr(self.build_ele, 'CaraIndice'):
            self.build_ele.CaraIndice.value = face_index

        self.solid_info = {
            'guid': element_guid_str,
            'element': selected_element,
            'face_normal': self.face_normal,
            'face_center': self.face_point,
            'click_point': self.face_point,
            'face_index': face_index
        }

        parent_element = None
        try:
            element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(element_guid_str)
            parent_element = AllplanBaseElements.ElementsService.GetElement(element_guid)

            if parent_element and parent_element.IsValid():
                self.parent_element = parent_element
            else:
                if hasattr(selected_element, 'GetParentElement'):
                    try:
                        parent_element = selected_element.GetParentElement()
                        if parent_element and parent_element.IsValid():
                            self.parent_element = parent_element
                    except Exception:
                        pass
        except Exception:
            pass

        wall_element_to_check = self.parent_element if self.parent_element else selected_element
        self.wall_ifc_id = get_wall_ifc_id(wall_element_to_check)

        if not self.is_free_mode and wall_element_to_check:
            try:
                element_type = wall_element_to_check.GetElementType()
                is_wall = (hasattr(element_type, 'TypeUUID') and
                          (element_type.TypeUUID == AllplanEleAdapter.Wall_TypeUUID or
                           element_type.TypeUUID == AllplanEleAdapter.WallTier_TypeUUID))
                if is_wall:
                    self.detected_wall = wall_element_to_check
                    self.detected_wall_guid = str(wall_element_to_check.GetModelElementUUID())
            except Exception:
                pass

        if hasattr(self.build_ele, 'SolidoConnection'):
            self.build_ele.SolidoConnection.value.element = selected_element
            if str(self.build_ele.SolidoConnection.value.uuid) == "00000000-0000-0000-0000-000000000000":
                try:
                    element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(element_guid_str)
                    element_from_guid = AllplanBaseElements.ElementsService.GetElement(element_guid)
                    if element_from_guid and element_from_guid.IsValid():
                        self.build_ele.SolidoConnection.value.element = element_from_guid
                except Exception:
                    pass

        if hasattr(self.build_ele, 'SolidoGUID'):
            self.build_ele.SolidoGUID.value = element_guid_str

        if hasattr(self.build_ele, 'CaraNormalX'):
            self.build_ele.CaraNormalX.value = self.face_normal.X
            self.build_ele.CaraNormalY.value = self.face_normal.Y
            self.build_ele.CaraNormalZ.value = self.face_normal.Z

        if hasattr(self.build_ele, 'PuntoClicX'):
            self.build_ele.PuntoClicX.value = self.face_point.X
            self.build_ele.PuntoClicY.value = self.face_point.Y
            self.build_ele.PuntoClicZ.value = self.face_point.Z

    def _start_line_input(self):
        prompt_msg = "Defina la linea para el neopreno - Posicionamiento libre" if self.is_free_mode else "Defina la linea para el neopreno (punto inicial)"

        coord_input_to_use = self._saved_coord_input if self._saved_coord_input else self.coord_input

        self.script_object_interactor = LineInteractor(
            self.line_result,
            True,
            prompt_msg,
            allow_pick_up=True,
            preview_function=self.draw_neopreno_preview
        )

        if coord_input_to_use:
            try:
                self.script_object_interactor.start_input(coord_input_to_use)

                if not self.is_free_mode and self.ref_face_element and self.ref_face_polygon:
                    try:
                        if hasattr(self.script_object_interactor, 'SetReferenceElement'):
                            self.script_object_interactor.SetReferenceElement(self.ref_face_element)
                        elif hasattr(self.script_object_interactor, 'AddReferenceGeometry'):
                            self.script_object_interactor.AddReferenceGeometry(self.ref_face_polygon)
                    except Exception:
                        pass
            except Exception:
                pass

    def _process_line_input(self):
        if not (line := self.line_result.input_line):
            return

        if getattr(self, "_restored_from_saved_state", False):
            if hasattr(self.build_ele, "PuntoInicial") and hasattr(self.build_ele, "PuntoFinal"):
                p0 = getattr(self.build_ele.PuntoInicial, "value", None)
                p1 = getattr(self.build_ele.PuntoFinal, "value", None)
                if p0 and p1:
                    self.line_result.input_line = AllplanGeo.Line3D(p0, p1)
                    line = self.line_result.input_line

        if self.is_free_mode:
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
        if hasattr(self.build_ele, 'Longitud'):
            self.build_ele.Longitud.value = longitud

        if local_system and not self._restored_from_saved_state:
            line_center = AllplanGeo.Point3D(
                (line.StartPoint.X + line.EndPoint.X) / 2.0,
                (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
                (line.StartPoint.Z + line.EndPoint.Z) / 2.0
            )

            rel_pos = calculate_relative_position(line_center, local_system)

            if rel_pos:
                if hasattr(self.build_ele, 'PosicionRelativaU'):
                    self.build_ele.PosicionRelativaU.value = rel_pos['u']
                if hasattr(self.build_ele, 'PosicionRelativaV'):
                    self.build_ele.PosicionRelativaV.value = rel_pos['v']
                if hasattr(self.build_ele, 'DistanciaDesdeOrigen'):
                    self.build_ele.DistanciaDesdeOrigen.value = rel_pos['distance_from_origin']

            rel_pos_start = calculate_relative_position(line_to_process.StartPoint, local_system)
            if rel_pos_start:
                if hasattr(self.build_ele, 'PosicionRelativaU_Inicio'):
                    self.build_ele.PosicionRelativaU_Inicio.value = rel_pos_start['u']
                if hasattr(self.build_ele, 'PosicionRelativaV_Inicio'):
                    self.build_ele.PosicionRelativaV_Inicio.value = rel_pos_start['v']

            rel_pos_end = calculate_relative_position(line_to_process.EndPoint, local_system)
            if rel_pos_end:
                if hasattr(self.build_ele, 'PosicionRelativaU_Fin'):
                    self.build_ele.PosicionRelativaU_Fin.value = rel_pos_end['u']
                if hasattr(self.build_ele, 'PosicionRelativaV_Fin'):
                    self.build_ele.PosicionRelativaV_Fin.value = rel_pos_end['v']

            line_vector = AllplanGeo.Vector3D(
                line_to_process.EndPoint.X - line_to_process.StartPoint.X,
                line_to_process.EndPoint.Y - line_to_process.StartPoint.Y,
                line_to_process.EndPoint.Z - line_to_process.StartPoint.Z
            )
            line_vector.Normalize()

            axis_u = local_system['axis_u']
            axis_v = local_system['axis_v']

            line_u = line_vector.DotProduct(axis_u)
            line_v = line_vector.DotProduct(axis_v)

            if hasattr(self.build_ele, 'LineaOrientacionU'):
                self.build_ele.LineaOrientacionU.value = line_u
            if hasattr(self.build_ele, 'LineaOrientacionV'):
                self.build_ele.LineaOrientacionV.value = line_v

            if hasattr(self.build_ele, 'AxisU_X'):
                self.build_ele.AxisU_X.value = axis_u.X
                self.build_ele.AxisU_Y.value = axis_u.Y
                self.build_ele.AxisU_Z.value = axis_u.Z
            if hasattr(self.build_ele, 'AxisV_X'):
                self.build_ele.AxisV_X.value = axis_v.X
                self.build_ele.AxisV_Y.value = axis_v.Y
                self.build_ele.AxisV_Z.value = axis_v.Z

        self.line_result.input_line = line_to_process

        coord_input = None
        if self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, 'RotacionManual'):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, 'GetDeg'):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            x_dir_handle, y_dir_handle, z_dir_handle = build_face_local_axes_for_handles(
                line_to_process.StartPoint,
                line_to_process.EndPoint,
                self.face_point,
                self.face_normal
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
            z_dir_handle
        )

    def draw_neopreno_preview(self, line: AllplanGeo.Line3D) -> ModelEleList:
        """Dibuja el preview del neopreno durante la creacion."""
        if not line or AllplanGeo.CalcLength(line) < 0.1:
            return []

        if self.is_free_mode:
            line_to_use = line
        else:
            line_to_use, _ = self._prepare_line(line)


        longitud = AllplanGeo.CalcLength(line_to_use)
        if hasattr(self.build_ele, 'Longitud'):
            self.build_ele.Longitud.value = longitud

        grosor = get_selected_thickness(self.build_ele)
        color = get_color_for_thickness(grosor)
        ancho = get_neopreno_width(self.build_ele)

        invertir_grosor = False
        if self.is_free_mode and hasattr(self.build_ele, 'InvertirGrosor'):
            val = self.build_ele.InvertirGrosor.value
            if isinstance(val, bool):
                invertir_grosor = not val
            elif isinstance(val, str):
                invertir_grosor = val.lower() not in ('true', '1', 'yes')
            else:
                invertir_grosor = not bool(val)

        coord_input = None
        if self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, 'RotacionManual'):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, 'GetDeg'):
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
            self.is_free_mode
        )

        if not solid:
            return []

        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.Color = color

        model_ele_list = ModelEleList()
        model_ele_list.append_geometry_3d(solid, props)

        return model_ele_list

    def on_mouse_leave(self):
        if self.script_object_interactor:
            self.script_object_interactor.on_mouse_leave()

    def modify_element_property(self, name: str, _value: Any) -> bool:
        """Maneja cambios en propiedades del elemento."""
        if name == 'GrosorSeleccionado':
            update_color_for_thickness(self.build_ele)

        if name == 'neopreno_libre':
            if self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
                self._saved_coord_input = self.script_object_interactor.coord_input
            self.is_free_mode = self._get_free_mode()
            self._update_parameter_visibility()
            if not self.is_editing_existing:
                if self.interactor_state == SELECTING_WALL or self.interactor_state == SELECTING_SOLID:
                    self.start_input()

        if name in ('InvertirGrosor', 'RotacionManual'):
            if self.line_result and self.line_result.input_line:
                if self.is_editing_existing:
                    return False
                elif self.interactor_state == SELECTING_LINE:
                    if self.script_object_interactor and hasattr(self.script_object_interactor, 'preview_function'):
                        self.draw_neopreno_preview(self.line_result.input_line)

        if self.is_editing_existing:
            return False

        if self.interactor_state == SELECTING_WALL:
            return False

        if self.interactor_state == SELECTING_LINE:
            self._start_line_input()
            if self.script_object_interactor:
                coord_input_to_use = self._saved_coord_input if self._saved_coord_input else self.coord_input
                if coord_input_to_use:
                    self.script_object_interactor.start_input(coord_input_to_use)

        return False

    def execute(self) -> CreateElementResult:
        """Dispatcher principal: separa CREATE y EDIT en funciones independientes."""

        if hasattr(self.build_ele, 'IsModify'):
            is_modify = self.build_ele.IsModify()
        else:
            is_modify = self.is_editing_existing


        self.is_editing_existing = is_modify

        if is_modify:
            return self._execute_modify()
        else:
            return self._execute_create()

    def _execute_create(self) -> CreateElementResult:
        """Lógica completa de CREACIÓN: detecta muro, calcula PMP_PARE, genera z_unique, crea geometrías."""

        if not self.line_result or not self.line_result.input_line:
            punto_inicial = getattr(self.build_ele, 'PuntoInicial', None)
            punto_final = getattr(self.build_ele, 'PuntoFinal', None)
            if punto_inicial and punto_final and hasattr(punto_inicial, 'value') and hasattr(punto_final, 'value'):
                if punto_inicial.value and punto_final.value:
                    if not self.line_result:
                        from ScriptObjectInteractors.LineInteractor import LineInteractorResult
                        self.line_result = LineInteractorResult()
                    self.line_result.input_line = AllplanGeo.Line3D(punto_inicial.value, punto_final.value)
                else:
                    return CreateElementResult([])
            else:
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
                                    self.face_normal.Z
                                )
                                transformed_origin = inv_wall_matrix * origin_point
                                transformed_normal = inv_wall_matrix * normal_point
                                self.face_normal = AllplanGeo.Vector3D(
                                    transformed_normal.X - transformed_origin.X,
                                    transformed_normal.Y - transformed_origin.Y,
                                    transformed_normal.Z - transformed_origin.Z
                                )
                                self.face_normal = normalize_vector(self.face_normal) or self.face_normal
                            except Exception:
                                pass
            except Exception:
                pass
        else:
            local_line = line

        if self.is_free_mode:
            line_to_use = local_line
        else:
            line_to_use, _ = self._prepare_line(local_line, is_already_in_local_coords=True)

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
        if hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value"):
            if not self.build_ele.z_unique.value or self.build_ele.z_unique.value == 0:
                z_unique = random.random() * 3600
                self.build_ele.z_unique.value = z_unique
            else:
                z_unique = float(self.build_ele.z_unique.value)
        else:
            z_unique = random.random() * 3600

        wall_pare = None
        wall = self.detected_wall if hasattr(self, 'detected_wall') else None
        if wall:
            try:
                wall_pare = get_wall_ifc_id(wall)
            except Exception as e:
                pass

        if not wall_pare:
            if hasattr(self, 'wall_ifc_id') and self.wall_ifc_id:
                wall_pare = self.wall_ifc_id
            else:
                wall_pare = "MURO_NO_DEFINIDO"

        if not self.is_editing_existing:
            if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, 'value'):
                try:
                    self.build_ele.pmp_pare.value = wall_pare
                except Exception as e:
                    pass
        else:
            if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, 'value'):
                wall_pare = str(self.build_ele.pmp_pare.value).strip() if self.build_ele.pmp_pare.value else ""


        self.line_result.input_line = line_to_use

        self.attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_PARE")
        self.attr_pmp_wall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_WALL_ID")

        self.elements = self._create_neopreno_elements(pmp_pare=wall_pare)

        if not self.elements:
            return CreateElementResult([])

        individual_pythonparts = self.create_individual_pythonparts_from_elements(
            self.elements,
            pmp_pare=wall_pare,
            is_modify=False  # Hash random en creación
        )

        if not individual_pythonparts:
            return CreateElementResult([])


        punto_inicial = start_point
        punto_final = end_point
        ancho = get_neopreno_width(self.build_ele) if hasattr(self.build_ele, 'Ancho') else 50.0
        grosor = get_selected_thickness(self.build_ele) if hasattr(self.build_ele, 'GrosorSeleccionado') else 5.0
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
                invertido = bool(val) if isinstance(val, bool) else str(val).lower() in ("true", "1", "yes")

        saved_state_str = self._serialize_state_to_json()
        if saved_state_str and hasattr(self.build_ele, "SavedState"):
            try:
                self.build_ele.SavedState.value = saved_state_str
            except Exception:
                pass

        global_params = {
            "z_unique": z_unique,
            "pmp_pare": wall_pare,
            "TotalElements": len(individual_pythonparts),
            "PuntoInicial": punto_inicial,
            "PuntoFinal": punto_final,
            "Ancho": ancho,
            "Grosor": grosor,
            "Libre": libre,
            "RotacionManual": rot,
            "InvertirGrosor": invertido,
            "SavedState": saved_state_str if saved_state_str else ""
        }

        group_hash = create_element_hash(
            "neopreno_group",
            stable=False  # CREATE = random
        )

        param_list = create_params_list_from_dict(global_params)

        pmp_pare_in_param_list = any('pmp_pare' in p for p in param_list)

        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        pythonpart_group = PythonPartGroup(
            "Neoprenos",
            param_list,
            group_hash,
            python_file_name,
            individual_pythonparts
        )

        model_elem_list = pythonpart_group.create()

        if not model_elem_list or len(model_elem_list) == 0:
            return CreateElementResult([])


        handles: list[HandleProperties] = []

        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if not coord_input and self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, 'RotacionManual'):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, 'GetDeg'):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            line_for_handles = self.line_result.input_line if self.line_result and self.line_result.input_line else None
            if line_for_handles:
                x_dir_handle, y_dir_handle, z_dir_handle = build_face_local_axes_for_handles(
                    line_for_handles.StartPoint,
                    line_for_handles.EndPoint,
                    self.face_point,
                    self.face_normal
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
                z_dir_handle
            )
        else:
            punto_inicial = getattr(self.build_ele, 'PuntoInicial', None)
            punto_final = getattr(self.build_ele, 'PuntoFinal', None)
            if punto_inicial and punto_final and punto_inicial.value and punto_final.value:
                fallback_line = AllplanGeo.Line3D(punto_inicial.value, punto_final.value)
                handles = create_handles(
                    self.build_ele,
                    fallback_line,
                    self.face_normal,
                    coord_input,
                    rotation_deg,
                    self.is_free_mode,
                    x_dir_handle,
                    y_dir_handle,
                    z_dir_handle
                )

        self.handles = handles

        connect_to_ele = ConnectToElements()

        if not self.is_free_mode:
            if hasattr(self.build_ele, 'SolidoConnection') and \
               self.build_ele.SolidoConnection.value.uuid:
                uuid_str = str(self.build_ele.SolidoConnection.value.uuid)
                if uuid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(uuid_str)
            if len(connect_to_ele.connection_elements) == 0 and self.solid_info:
                if self.solid_info.get('guid'):
                    connect_to_ele.connection_elements.append(self.solid_info['guid'])
                elif self.solid_info.get('element'):
                    try:
                        element_guid = str(self.solid_info['element'].GetModelElementUUID())
                        if element_guid != "00000000-0000-0000-0000-000000000000":
                            connect_to_ele.connection_elements.append(element_guid)
                    except Exception:
                        pass
            if len(connect_to_ele.connection_elements) == 0 and \
               hasattr(self.build_ele, 'SolidoGUID') and self.build_ele.SolidoGUID.value:
                guid_str = str(self.build_ele.SolidoGUID.value)
                if guid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(guid_str)
        else:
            if hasattr(self.build_ele, 'MuroConnection') and \
               self.build_ele.MuroConnection.value.uuid:
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
            if len(connect_to_ele.connection_elements) == 0 and \
               hasattr(self.build_ele, 'MuroGUID') and self.build_ele.MuroGUID.value:
                guid_str = str(self.build_ele.MuroGUID.value)
                if guid_str != "00000000-0000-0000-0000-000000000000":
                    connect_to_ele.connection_elements.append(guid_str)

        if len(connect_to_ele.connection_elements) == 0:
            AllplanUtil.ShowMessageBox(
                "Error: No se pudo establecer conexion con el elemento.\n\n"
                "El neopreno necesita estar conectado a un muro o solido para guardarse correctamente.",
                AllplanUtil.MB_OK
            )
            return CreateElementResult([])

        self._save_state_to_build_ele()

        return CreateElementResult(
            elements=model_elem_list,
            handles=handles,
            placement_point=AllplanGeo.Point3D(0.0, 0.0, 0.0),
            connect_to_ele=connect_to_ele,
            uuid_parameter_name="PythonPartUUID"
        )

    def _execute_modify(self) -> CreateElementResult:
        """Lógica completa de EDICIÓN: lee TODO desde build_ele, NUNCA escribe parámetros persistentes."""

        start_point = None
        end_point = None
        wall_pare = ""
        ancho = 50.0
        grosor = 5.0
        libre = True

        saved_state_str = ""
        if hasattr(self.build_ele, "SavedState") and hasattr(self.build_ele.SavedState, "value"):
            saved_state_str = (self.build_ele.SavedState.value or "").strip()
        state = parse_saved_state(saved_state_str) if saved_state_str else {}
        p0_restored = saved_state_to_point3d(state, "p0")
        p1_restored = saved_state_to_point3d(state, "p1")

        if p0_restored is not None and p1_restored is not None:
            start_point = p0_restored
            end_point = p1_restored
            wall_pare = (state.get("pmp_pare") or "").strip() or "SIN_PARE"
            ancho = state.get("ancho")
            if ancho is None:
                ancho = get_neopreno_width(self.build_ele) if hasattr(self.build_ele, "Ancho") else 50.0
            else:
                try:
                    ancho = float(ancho)
                except (TypeError, ValueError):
                    ancho = 50.0
            grosor = state.get("grosor")
            if grosor is None:
                grosor = get_selected_thickness(self.build_ele) if hasattr(self.build_ele, "GrosorSeleccionado") else 5.0
            else:
                try:
                    grosor = float(grosor)
                except (TypeError, ValueError):
                    grosor = 5.0
            libre = state.get("libre", True)
            if not isinstance(libre, bool):
                libre = bool(libre) if libre is not None else True
        else:
            if hasattr(self.build_ele, 'PuntoInicial') and hasattr(self.build_ele, 'PuntoFinal'):
                start_point = self.build_ele.PuntoInicial.value
                end_point = self.build_ele.PuntoFinal.value
            else:
                return CreateElementResult(self.elements if hasattr(self, 'elements') and self.elements else [],
                                         self.handles if hasattr(self, 'handles') else [])

            if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, 'value'):
                wall_pare = str(self.build_ele.pmp_pare.value).strip() if self.build_ele.pmp_pare.value else ""
            if not wall_pare:
                wall_pare = "SIN_PARE"
            if hasattr(self.build_ele, 'Ancho'):
                ancho = get_neopreno_width(self.build_ele)
            if hasattr(self.build_ele, 'GrosorSeleccionado'):
                grosor = get_selected_thickness(self.build_ele)
            libre = getattr(self, "is_free_mode", True)


        existing_group_hash = None
        if hasattr(self.build_ele, 'get_hash'):
            try:
                existing_group_hash = self.build_ele.get_hash()
                if existing_group_hash:
                    pass
            except Exception as e:
                pass

        self.is_free_mode = libre

        line = AllplanGeo.Line3D(start_point, end_point)
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
            line_to_use, _ = self._prepare_line(local_line, is_already_in_local_coords=True)

        self.line_result.input_line = line_to_use

        self.attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "pmp_pare")
        self.attr_pmp_wall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_WALL_ID")

        self.elements = self._create_neopreno_elements(pmp_pare=wall_pare)

        if not self.elements:
            return CreateElementResult(self.elements if hasattr(self, 'elements') and self.elements else [],
                                     self.handles if hasattr(self, 'handles') else [])

        individual_pp = self.create_individual_pythonparts_from_elements(
            self.elements,
            pmp_pare=wall_pare,
            is_modify=True  # Hash estable en edición
        )

        if not individual_pp:
            return CreateElementResult(self.elements if hasattr(self, 'elements') and self.elements else [],
                                     self.handles if hasattr(self, 'handles') else [])

        if existing_group_hash:
            group_hash = existing_group_hash
        else:
            group_hash = create_element_hash(
                "neopreno_group",
                stable=True  # EDIT = estable
            )

        z_unique = 0.0
        if hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value"):
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
                invertido = bool(val) if isinstance(val, bool) else str(val).lower() in ("true", "1", "yes")
        saved_state_str = self._serialize_state_to_json() if self._restored_from_saved_state else (getattr(self.build_ele.SavedState, "value", None) or "") if hasattr(self.build_ele, "SavedState") else ""

        global_params = {
            "z_unique": z_unique,
            "pmp_pare": wall_pare,
            "TotalElements": len(individual_pp),
            "PuntoInicial": start_point,
            "PuntoFinal": end_point,
            "Ancho": ancho,
            "Grosor": grosor,
            "Libre": libre,
            "RotacionManual": rot,
            "InvertirGrosor": invertido,
            "SavedState": saved_state_str if isinstance(saved_state_str, str) else ""
        }

        param_list = create_params_list_from_dict(global_params)
        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        pythonpart_group = PythonPartGroup(
            "Neoprenos",
            param_list,
            group_hash,
            python_file_name,
            individual_pp
        )

        model_elem_list = pythonpart_group.create()

        if not model_elem_list or len(model_elem_list) == 0:
            return CreateElementResult(self.elements if hasattr(self, 'elements') and self.elements else [],
                                     self.handles if hasattr(self, 'handles') else [])

        handles: list[HandleProperties] = []
        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if not coord_input and self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, 'RotacionManual'):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, 'GetDeg'):
                rotation_deg = rot_val.GetDeg()
            elif isinstance(rot_val, (int, float)):
                rotation_deg = float(rot_val)

        x_dir_handle = None
        y_dir_handle = None
        z_dir_handle = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            line_for_handles = self.line_result.input_line if self.line_result and self.line_result.input_line else None
            if line_for_handles:
                x_dir_handle, y_dir_handle, z_dir_handle = build_face_local_axes_for_handles(
                    line_for_handles.StartPoint,
                    line_for_handles.EndPoint,
                    self.face_point,
                    self.face_normal
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
                z_dir_handle
            )
        else:
            punto_inicial = getattr(self.build_ele, 'PuntoInicial', None)
            punto_final = getattr(self.build_ele, 'PuntoFinal', None)
            if punto_inicial and punto_final and punto_inicial.value and punto_final.value:
                fallback_line = AllplanGeo.Line3D(punto_inicial.value, punto_final.value)
                handles = create_handles(
                    self.build_ele,
                    fallback_line,
                    self.face_normal,
                    coord_input,
                    rotation_deg,
                    self.is_free_mode,
                    x_dir_handle,
                    y_dir_handle,
                    z_dir_handle
                )

        self.handles = handles

        if self._restored_from_saved_state:
            self._save_state_to_build_ele()

        return CreateElementResult(
            elements=model_elem_list,
            handles=handles,
            placement_point=AllplanGeo.Point3D(0, 0, 0),
            uuid_parameter_name="PythonPartUUID"
        )

    def move_handle(self,
                    handle_prop: HandleProperties,
                    input_pnt: AllplanGeo.Point3D) -> CreateElementResult:
        """
        Maneja el movimiento de handles.
        """
        handle_name = handle_prop.name if hasattr(handle_prop, 'name') else 'unknown'
        input_pnt_final = input_pnt
        if not self.is_free_mode and self.face_normal and self.face_point and self.face_polygon:
            current_point = None
            if handle_name == "PuntoInicialHandle":
                start_prop = getattr(self.build_ele, 'PuntoInicial', None)
                if start_prop and hasattr(start_prop, 'value') and start_prop.value:
                    current_point = start_prop.value
            elif handle_name == "PuntoFinalHandle":
                end_prop = getattr(self.build_ele, 'PuntoFinal', None)
                if end_prop and hasattr(end_prop, 'value') and end_prop.value:
                    current_point = end_prop.value
            elif handle_name == "AnchoHandle":
                start_prop = getattr(self.build_ele, 'PuntoInicial', None)
                end_prop = getattr(self.build_ele, 'PuntoFinal', None)
                if start_prop and end_prop and start_prop.value and end_prop.value:
                    current_point = AllplanGeo.Point3D(
                        (start_prop.value.X + end_prop.value.X) / 2.0,
                        (start_prop.value.Y + end_prop.value.Y) / 2.0,
                        (start_prop.value.Z + end_prop.value.Z) / 2.0
                    )

            if current_point:
                if self.line_result and self.line_result.input_line:
                    line_for_axes = self.line_result.input_line
                else:
                    start_prop = getattr(self.build_ele, 'PuntoInicial', None)
                    end_prop = getattr(self.build_ele, 'PuntoFinal', None)
                    if start_prop and end_prop and start_prop.value and end_prop.value:
                        line_for_axes = AllplanGeo.Line3D(start_prop.value, end_prop.value)
                    else:
                        line_for_axes = None

                if line_for_axes:
                    x_dir_handle, y_dir_handle, z_dir_handle = build_face_local_axes_for_handles(
                        line_for_axes.StartPoint,
                        line_for_axes.EndPoint,
                        self.face_point,
                        self.face_normal
                    )

                    if x_dir_handle and y_dir_handle and z_dir_handle:
                        current_proj = project_point_to_face_plane(current_point, self.face_point, self.face_normal)
                        input_proj = project_point_to_face_plane(input_pnt, self.face_point, self.face_normal)

                        u_current, v_current = world_to_uv_face(current_proj, self.face_point, x_dir_handle, y_dir_handle)
                        u_input, v_input = world_to_uv_face(input_proj, self.face_point, x_dir_handle, y_dir_handle)

                        du = u_input - u_current
                        dv = v_input - v_current

                        u_min, u_max, v_min, v_max = get_face_uv_bounds(
                            self.face_polygon,
                            self.face_point,
                            self.face_normal,
                            x_dir_handle,
                            y_dir_handle
                        )

                        u_new = max(u_min, min(u_max, u_current + du))
                        v_new = max(v_min, min(v_max, v_current + dv))

                        new_point_uv = uv_to_world_face(u_new, v_new, self.face_point, x_dir_handle, y_dir_handle)
                        new_point_proj = project_point_to_face_plane(new_point_uv, self.face_point, self.face_normal)

                        dist_to_plane = abs(vector_dot(
                            AllplanGeo.Vector3D(
                                new_point_proj.X - self.face_point.X,
                                new_point_proj.Y - self.face_point.Y,
                                new_point_proj.Z - self.face_point.Z
                            ),
                            normalize_vector(self.face_normal) or AllplanGeo.Vector3D(0, 0, 1)
                        ))

                        input_pnt_final = new_point_proj

        HandlePropertiesService.update_property_value(self.build_ele, handle_prop, input_pnt_final)

        start_prop = getattr(self.build_ele, 'PuntoInicial', None)
        end_prop = getattr(self.build_ele, 'PuntoFinal', None)
        start_point = start_prop.value if start_prop and hasattr(start_prop, 'value') else None
        end_point = end_prop.value if end_prop and hasattr(end_prop, 'value') else None

        if start_point and end_point:
            self.line_result.input_line = AllplanGeo.Line3D(start_point, end_point)
            self._process_line_input()
        else:
            self.line_result.input_line = None

        get_neopreno_width(self.build_ele)

        return self.execute()

    def get_or_create_layer_in_group(self, group_name: str, short_name: str, long_name: str) -> int:
        """Busca la layer por short_name o la crea en el grupo usando CreateLayer.
        LayerManager no existe en NemAll_Python_BaseElements; se usa CreateLayer.
        """
        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(short_name, self.document)
        if layer_id > 0:
            return layer_id

        return AllplanBaseElements.CreateLayer(
            self.document,
            group_name,
            "",
            long_name,
            short_name,
            1, 1, 1, True, True,
        )

    def _create_neopreno_elements(self, pmp_pare: str = None) -> List[AllplanBasisElements.ModelElement3D]:
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
        if hasattr(self.build_ele, 'Longitud'):
            self.build_ele.Longitud.value = longitud

        grosor = get_selected_thickness(self.build_ele)
        update_color_for_thickness(self.build_ele)
        ancho = get_neopreno_width(self.build_ele)

        invertir_grosor = False
        if self.is_free_mode and hasattr(self.build_ele, 'InvertirGrosor'):
            val = self.build_ele.InvertirGrosor.value
            if isinstance(val, bool):
                invertir_grosor = not val
            elif isinstance(val, str):
                invertir_grosor = val.lower() not in ('true', '1', 'yes')
            else:
                invertir_grosor = not bool(val)

        coord_input = self.coord_input if self.coord_input else None
        if not coord_input:
            coord_input = self._saved_coord_input if self._saved_coord_input else None
        if not coord_input and self.script_object_interactor and hasattr(self.script_object_interactor, 'coord_input'):
            coord_input = self.script_object_interactor.coord_input

        rotation_deg = 0.0
        if self.is_free_mode and hasattr(self.build_ele, 'RotacionManual'):
            rot_val = self.build_ele.RotacionManual.value
            if hasattr(rot_val, 'GetDeg'):
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
            self.is_free_mode
        )

        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(NEO_LAYER, self.document)

        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()
        common_props.Color = self.build_ele.Color.value if hasattr(self.build_ele, 'Color') else 15
        common_props.Pen = self.build_ele.Pen.value if hasattr(self.build_ele, 'Pen') else 1
        common_props.Stroke = self.build_ele.Stroke.value if hasattr(self.build_ele, 'Stroke') else 1
        common_props.Layer = layer_id

        attr_list = BuildingElementAttributeList()
        if pmp_pare is None:
            pmp_pare = ""

        attr_id = self.attr_pmp_pare_id
        attr_wall_id = self.attr_pmp_wall_id
        if attr_id > 0 and pmp_pare:
            attr_list.add_attribute(attr_id, pmp_pare)
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

    def create_individual_pythonparts_from_elements(self, elements_list: List[AllplanBasisElements.ModelElement3D], pmp_pare: str = None, is_modify: bool = False) -> List[PythonPart]:
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

        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        for idx, element in enumerate(elements_list):
            try:
                common_props = element.GetCommonProperties() if hasattr(element, 'GetCommonProperties') else AllplanBaseElements.CommonProperties()
                if not hasattr(common_props, 'Layer') or common_props.Layer <= 0:
                    layer_id = AllplanBaseElements.LayerService.GetIDByShortName(NEO_LAYER, self.document)
                    common_props.Layer = layer_id

                attr_list = BuildingElementAttributeList()
                attr_pmp_id = getattr(self, "attr_pmp_pare_id", 0)
                attr_wall_name_id =getattr(self, "attr_pmp_wall_id", 0)

                wall_pare = pmp_pare if pmp_pare else ""
                if wall_pare and attr_pmp_id > 0:
                    attr_list.add_attribute(attr_pmp_id, wall_pare)
                    attr_list.add_attribute(attr_wall_name_id, wall_pare)

                attribute_list = attr_list.get_attribute_list()

                views = [View2D3D([element])]

                params = {
                    'ElementIndex': idx,
                    'ElementType': type(element).__name__,
                    'Layer': common_props.Layer,
                    'Color': common_props.Color,
                    'Pen': common_props.Pen,
                    'Stroke': common_props.Stroke
                }

                hash_value = create_element_hash(
                    "neopreno_element",
                    stable=is_modify,
                    Index=idx
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
                    attribute_list=attribute_list if attribute_list else None
                )

                pythonparts_list.append(pythonpart)

            except Exception as e:
                import traceback
                continue

        return pythonparts_list

    def on_cancel_function(self) -> OnCancelFunctionResult:
        if not self.line_result or not self.line_result.input_line:
            return OnCancelFunctionResult.CANCEL_INPUT

        try:

            wall_pare = None
            if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, "value") and self.build_ele.pmp_pare.value:
                wall_pare = self.build_ele.pmp_pare.value
            else:
                if self.detected_wall:
                    try:
                        wall_pare = get_wall_ifc_id(self.detected_wall)
                    except Exception:
                        pass
                if not wall_pare and getattr(self, "wall_ifc_id", None):
                    wall_pare = self.wall_ifc_id
                if not wall_pare:
                    wall_pare = "MURO_NO_DEFINIDO"
                if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, "value"):
                    try:
                        self.build_ele.pmp_pare.value = wall_pare
                    except Exception:
                        pass

            self.attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "pmp_pare")
            self.attr_pmp_wall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_WALL_ID")

            elements = self._create_neopreno_elements(pmp_pare=wall_pare)

            if not elements:
                return OnCancelFunctionResult.CANCEL_INPUT

            individual_pythonparts = self.create_individual_pythonparts_from_elements(elements, pmp_pare=wall_pare)

            if not individual_pythonparts:
                return OnCancelFunctionResult.CANCEL_INPUT

            start_point = self.line_result.input_line.StartPoint
            end_point = self.line_result.input_line.EndPoint
            ancho = get_neopreno_width(self.build_ele) if hasattr(self.build_ele, "Ancho") else 50.0
            grosor = get_selected_thickness(self.build_ele) if hasattr(self.build_ele, "GrosorSeleccionado") else 5.0
            libre = getattr(self, "is_free_mode", True)
            rot = 0.0
            if hasattr(self.build_ele, "RotacionManual"):
                rv = getattr(self.build_ele.RotacionManual, "value", None)
                if rv is not None:
                    rot = rv.GetDeg() if hasattr(rv, "GetDeg") else float(rv)
            invertido = False
            if hasattr(self.build_ele, "InvertirGrosor"):
                val = getattr(self.build_ele.InvertirGrosor, "value", None)
                if val is not None:
                    invertido = bool(val) if isinstance(val, bool) else str(val).lower() in ("true", "1", "yes")
            saved_state_str = self._serialize_state_to_json() if hasattr(self, "_serialize_state_to_json") else ""
            z_unique = 0.0
            if hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value"):
                try:
                    z_unique = float(self.build_ele.z_unique.value)
                except (ValueError, TypeError):
                    z_unique = 0.0

            global_params = {
                "z_unique": z_unique,
                "pmp_pare": wall_pare,
                "TotalElements": len(elements),
                "PuntoInicial": start_point,
                "PuntoFinal": end_point,
                "Ancho": ancho,
                "Grosor": grosor,
                "Libre": libre,
                "RotacionManual": rot,
                "InvertirGrosor": invertido,
                "SavedState": saved_state_str if saved_state_str else ""
            }

            group_hash = create_element_hash('neopreno_group', stable=False)

            param_list = create_params_list_from_dict(global_params)

            python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

            pythonpart_group = PythonPartGroup(
                "Neoprenos",
                param_list,
                group_hash,
                python_file_name,
                individual_pythonparts
            )

            model_elem_list = pythonpart_group.create()

            if model_elem_list and len(model_elem_list) > 0:
                AllplanBaseElements.CreateElements(
                    self.document,
                    AllplanGeo.Matrix3D(),
                    model_elem_list,
                    [],
                    None
                )

        except Exception as e:
            import traceback
            return OnCancelFunctionResult.CANCEL_INPUT

        return OnCancelFunctionResult.CANCEL_INPUT
