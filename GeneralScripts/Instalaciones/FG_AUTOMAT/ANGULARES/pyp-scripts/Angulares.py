from __future__ import annotations

import ast
import hashlib
import json
import math
import random
from typing import Any, Dict, List

try:
    import numpy as np
except ImportError:
    np = None

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from ScriptObjectInteractors.LineInteractor import LineInteractor, LineInteractorResult
from ScriptObjectInteractors.PointInteractor import PointInteractor, PointInteractorResult
from ScriptObjectInteractors.BaseScriptObjectInteractor import BaseScriptObjectInteractor
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from TypeCollections.ModelEleList import ModelEleList
from PythonPart import PythonPart, PythonPartGroup, View2D3D
from PythonPartTransaction import ConnectToElements
from HandleProperties import HandleProperties
from HandlePropertiesService import HandlePropertiesService
from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from HandleDirection import HandleDirection
from BuildingElementAttributeList import BuildingElementAttributeList

HOLE_DIAMETER = 14.0
HOLE_RADIUS = HOLE_DIAMETER / 2.0

ANG_LAYER = "PMP_ANGULARS"

DISTRIBUTION_GROUP = "grupal"
DISTRIBUTION_INDIVIDUAL = "individual"
ANGULARES_SCRIPT_VERSION = "1.2-distribucion-individual-multiple-ppg"


def normalize_distribution_type(value: Any) -> str:
    """Normaliza el valor del combobox de distribución."""
    normalized = str(value or "").strip().lower().replace("'", "")
    if normalized == DISTRIBUTION_INDIVIDUAL:
        return DISTRIBUTION_INDIVIDUAL
    return DISTRIBUTION_GROUP


def create_element_hash(element_type: str, stable: bool = False, **params) -> str:
    """
    Crea un hash único y estable para un elemento basado en su tipo y parámetros.

    IMPORTANTE:
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
        # En modo estable, incluir z_unique en el hash para que sea determinístico
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
    Soporta Point3D, int, float, bool (True/False), strings con repr.

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
                if value.startswith('Point3D('):
                    try:
                        coords = value.replace('Point3D(', '').replace(')', '').split(',')
                        if len(coords) == 3:
                            params[key] = AllplanGeo.Point3D(
                                float(coords[0].strip()),
                                float(coords[1].strip()),
                                float(coords[2].strip())
                            )
                        else:
                            params[key] = value
                    except Exception:
                        params[key] = value
                else:
                    try:
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        try:
                            params[key] = ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            params[key] = value
    return params


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


def _rows(top_y, bottom_y, top_positions, bottom_positions):
    """Helper para construir la lista de filas de taladros.

    Cada fila tiene:
    - y: altura vertical del taladro (medida desde el origen del angular)
    - x_positions: lista de posiciones horizontales a lo largo del angular

    Ejemplo: _rows(160.0, 60.0, [50.0, 230.0, 410.0], [50.0, 410.0])
    crea 3 taladros en la fila superior (y=160) en x=50, 230, 410
    y 2 taladros en la fila inferior (y=60) en x=50, 410
    """
    rows = [{"y": top_y, "x_positions": top_positions}]
    if bottom_positions:
        rows.append({"y": bottom_y, "x_positions": bottom_positions})
    return rows

def get_hole_coordinates(angular_key: str) -> dict:
    """Obtiene las coordenadas de todos los taladros para un tipo de angular.

    Args:
        angular_key: Clave del angular (ej: "ANG200_L460")

    Returns:
        Diccionario con información detallada de los taladros:
        {
            "angular_info": {...},
            "holes": [
                {"index": 1, "local_coords": (x, y, z), "row": "top/bottom", "description": "..."},
                ...
            ]
        }

    """
    if angular_key not in ANGULAR_CATALOG:
        return None

    definition = ANGULAR_CATALOG[angular_key]
    holes = []
    hole_index = 1

    for row_idx, row in enumerate(definition["hole_rows"]):
        hole_y = row["y"]
        row_name = "superior" if row_idx == 0 else "inferior"

        for hole_x in row["x_positions"]:
            holes.append({
                "index": hole_index,
                "local_coords": (hole_x, hole_y, 0.0),
                "row": row_name,
                "x": hole_x,
                "y": hole_y,
                "z": 0.0,
                "description": f"Taladro {hole_index} ({row_name}): posición X={hole_x}mm, Y={hole_y}mm"
            })
            hole_index += 1

    return {
        "angular_info": {
            "key": angular_key,
            "label": definition["label"],
            "length": definition["length"],
            "vertical": definition["vertical"],
            "horizontal": definition["horizontal"],
            "thickness": definition["thickness"],
            "total_holes": len(holes)
        },
        "holes": holes
    }

ANGULAR_CATALOG = {
    "ANG200_L460": {
        "label": "200×200×20 - L460 - 5 taladros",
        "length": 460.0,
        "vertical": 200.0,
        "horizontal": 200.0,
        "thickness": 20.0,
        "hole_rows": _rows(
            top_y=200.0 - 40.0,
            bottom_y=60.0,
            top_positions=[50.0, 230.0, 410.0],
            bottom_positions=[50.0, 410.0],
        ),
        "color": 119,
    },
    "ANG200_L310": {
        "label": "200×200×20 - L310 - 4 taladros",
        "length": 310.0,
        "vertical": 200.0,
        "horizontal": 200.0,
        "thickness": 20.0,
        "hole_rows": _rows(
            top_y=200.0 - 40.0,
            bottom_y=60.0,
            top_positions=[50.0, 260.0],
            bottom_positions=[50.0, 260.0],
        ),
        "color": 68,
    },
    "ANG200_L150": {
        "label": "200×200×20 - L150 - 2 taladros",
        "length": 150.0,
        "vertical": 200.0,
        "horizontal": 200.0,
        "thickness": 20.0,
        "hole_rows": _rows(
            top_y=200.0 - 40.0,
            bottom_y=60.0,
            top_positions=[75.0],
            bottom_positions=[75.0],
        ),
        "color": 11,
    },
    "ANG250_L460": {
        "label": "250×250×25 - L460 - 5 taladros",
        "length": 460.0,
        "vertical": 250.0,
        "horizontal": 250.0,
        "thickness": 25.0,
        "hole_rows": _rows(
            top_y=250.0 - 40.0,
            bottom_y=110.0,
            top_positions=[50.0, 230.0, 410.0],
            bottom_positions=[50.0, 410.0],
        ),
        "color": 5,
    },
    "ANG250_L310": {
        "label": "250×250×25 - L310 - 4 taladros",
        "length": 310.0,
        "vertical": 250.0,
        "horizontal": 250.0,
        "thickness": 25.0,
        "hole_rows": _rows(
            top_y=250.0 - 40.0,
            bottom_y=110.0,
            top_positions=[50.0, 260.0],
            bottom_positions=[50.0, 260.0],
        ),
        "color": 52,
    },
    "ANG250_L150": {
        "label": "250×250×25 - L150 - 2 taladros",
        "length": 150.0,
        "vertical": 250.0,
        "horizontal": 250.0,
        "thickness": 25.0,
        "hole_rows": _rows(
            top_y=250.0 - 40.0,
            bottom_y=110.0,
            top_positions=[75.0],
            bottom_positions=[75.0],
        ),
        "color": 8,
    },
    "TENSOR": {
        "label": "Tensor",
        "length": 200.0,
        "piece_length": 200.0,
        "vertical": 300.0,
        "horizontal": 200.0,
        "thickness": 10.0,
        "hole_rows": [],
        "color": 8,
        "is_tensor": True
    },
}

def get_num_forats_from_definition(definition: dict) -> int:
    """Determina el número de taladros (forats) según la definición del angular.

    Args:
        definition: Diccionario con la definición del angular

    Returns:
        str: "2", "4" o "5" según el número de taladros
    """
    if definition.get("is_tensor", False):
        return 4

    length = definition.get("length", 0.0)

    if abs(length - 460.0) < 1e-6:
        return 5
    elif abs(length - 310.0) < 1e-6:
        return 4
    elif abs(length - 150.0) < 1e-6:
        return 2
    else:
        hole_rows = definition.get("hole_rows", [])
        if hole_rows:
            total_holes = 0
            for row in hole_rows:
                positions = row.get("positions", [])
                total_holes += len(positions)
            if total_holes == 5:
                return 5
            elif total_holes == 4:
                return 4
            elif total_holes == 2:
                return 2

        return 4

def get_nom_from_angular_key(angular_key: str) -> str:
    """Obtiene el nombre (NOM) del angular según su clave.

    Args:
        angular_key: Clave del angular (ej: "ANG200_L460", "TENSOR")

    Returns:
        str: Nombre completo del angular según el catálogo
    """
    nom_mapping = {
        "ANG200_L460": "ANGULARS SUPORT 200x200x20 (460)",
        "ANG200_L310": "ANGULARS SUPORT 200x200x20 (310)",
        "ANG200_L150": "ANGULARS SUPORT 200x200x20 (150)",
        "ANG250_L460": "ANGULARS SUPORT 250 x 5 FORATS (460)",
        "ANG250_L310": "ANGULARS SUPORT 250 x 4 FORATS (310)",
        "ANG250_L150": "ANGULARS SUPORT 250x250x25 (150)",
        "TENSOR": "TENSORS 4 FORATS"
    }

    return nom_mapping.get(angular_key, "")

def vector_from_points(start_point: AllplanGeo.Point3D, end_point: AllplanGeo.Point3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(start_point, end_point)

def vector_add(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(v1.X + v2.X, v1.Y + v2.Y, v1.Z + v2.Z)

def vector_scale(vector: AllplanGeo.Vector3D, factor: float) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(vector.X * factor, vector.Y * factor, vector.Z * factor)

def vector_cross(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    return AllplanGeo.Vector3D(
        v1.Y * v2.Z - v1.Z * v2.Y,
        v1.Z * v2.X - v1.X * v2.Z,
        v1.X * v2.Y - v1.Y * v2.X,
    )

def vector_dot(v1: AllplanGeo.Vector3D, v2: AllplanGeo.Vector3D) -> float:
    return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

def normalize_vector(vector: AllplanGeo.Vector3D) -> AllplanGeo.Vector3D:
    length = vector.GetLength()
    if length < 1e-6:
        return AllplanGeo.Vector3D(0.0, 0.0, 0.0)
    inv = 1.0 / length
    return AllplanGeo.Vector3D(vector.X * inv, vector.Y * inv, vector.Z * inv)

def rotate_vector_around_axis(vector: AllplanGeo.Vector3D,
                              axis: AllplanGeo.Vector3D,
                              angle_rad: float) -> AllplanGeo.Vector3D:
    """Rotates vector around axis using la fórmula de Rodrigues"""
    axis_norm = normalize_vector(axis)
    cos_ang = math.cos(angle_rad)
    sin_ang = math.sin(angle_rad)

    term1 = vector_scale(vector, cos_ang)
    term2 = vector_scale(vector_cross(axis_norm, vector), sin_ang)
    term3 = vector_scale(axis_norm, vector_dot(axis_norm, vector) * (1.0 - cos_ang))

    rotated = vector_add(vector_add(term1, term2), term3)
    return normalize_vector(rotated)

def apply_local_y_rotation(x_dir: AllplanGeo.Vector3D,
                           y_dir: AllplanGeo.Vector3D,
                           z_dir: AllplanGeo.Vector3D,
                           rotation_y_deg: float) -> tuple[AllplanGeo.Vector3D, AllplanGeo.Vector3D, AllplanGeo.Vector3D]:
    """Aplica un giro adicional alrededor del eje local Y."""
    if abs(rotation_y_deg) <= 1e-6:
        return x_dir, y_dir, z_dir

    rotation_rad = math.radians(rotation_y_deg)
    x_dir = normalize_vector(rotate_vector_around_axis(x_dir, y_dir, rotation_rad))
    z_dir = normalize_vector(rotate_vector_around_axis(z_dir, y_dir, rotation_rad))
    return x_dir, y_dir, z_dir

def move_point(point: AllplanGeo.Point3D, direction: AllplanGeo.Vector3D, distance: float) -> AllplanGeo.Point3D:
    return AllplanGeo.Point3D(
        point.X + direction.X * distance,
        point.Y + direction.Y * distance,
        point.Z + direction.Z * distance,
    )

def local_to_world(origin: AllplanGeo.Point3D,
                   x_dir: AllplanGeo.Vector3D,
                   y_dir: AllplanGeo.Vector3D,
                   z_dir: AllplanGeo.Vector3D,
                   loc_x: float,
                   loc_y: float,
                   loc_z: float) -> AllplanGeo.Point3D:
    return AllplanGeo.Point3D(
        origin.X + x_dir.X * loc_x + y_dir.X * loc_y + z_dir.X * loc_z,
        origin.Y + x_dir.Y * loc_x + y_dir.Y * loc_y + z_dir.Y * loc_z,
        origin.Z + x_dir.Z * loc_x + y_dir.Z * loc_y + z_dir.Z * loc_z,
    )

def axis_with_offset(origin: AllplanGeo.Point3D,
                     x_dir: AllplanGeo.Vector3D,
                     y_dir: AllplanGeo.Vector3D,
                     z_dir: AllplanGeo.Vector3D,
                     offset_x: float,
                     offset_y: float,
                     offset_z: float) -> AllplanGeo.AxisPlacement3D:
    axis_origin = local_to_world(origin, x_dir, y_dir, z_dir, offset_x, offset_y, offset_z)
    return AllplanGeo.AxisPlacement3D(axis_origin, x_dir, z_dir)

class SolidFaceSelectResult:
    """Resultado de la selección de una cara de un sólido"""
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None
        self.is_selected = False

class SolidFaceSelectInteractor(BaseScriptObjectInteractor):
    """Interactor para seleccionar la cara de un sólido"""

    def __init__(self, result: SolidFaceSelectResult, prompt_msg: str = "Seleccione la cara del muro"):
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
            self.result.face_point = intersect_result.IntersectionPoint
            self.result.face_normal = intersect_result.FaceNv
        else:
            self.result.face_point = AllplanGeo.Point3D()
            self.result.face_normal = AllplanGeo.Vector3D(0, 0, 1)

        self.result.face_polygon = face_polygon
        self.result.is_selected = True

        return False

    def _select_face(self, element, pnt):
        """Intenta seleccionar una cara del elemento"""
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
        """Dibuja un preview de la normal de la cara"""
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

def calculate_local_coordinate_system(face_polygon: AllplanGeo.Polygon3D,
                                     face_normal: AllplanGeo.Vector3D) -> dict:
    """Calcula el sistema de coordenadas local de una cara"""
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

        axis_v = vector_cross(axis_w, axis_u)
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
            u_coords.append(vector_dot(vec_from_origin, axis_u))
            v_coords.append(vector_dot(vec_from_origin, axis_v))

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
    """Calcula la posición relativa de un punto en el sistema de coordenadas local"""
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

        u_absolute = vector_dot(to_point, axis_u)
        v_absolute = vector_dot(to_point, axis_v)

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
    """Calcula la posición absoluta desde coordenadas relativas U, V"""
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

def get_wall_ifc_id(wall_element) -> str | None:
    """Obtiene el nombre del muro desde el atributo Material (id 508) o buscando en todos los atributos.

    El nombre está separado por $, por ejemplo "AP$PV_!0" → nombre = "AP"
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

def get_all_walls_from_document(document) -> list:
    """Obtiene todos los muros del documento.

    Nota: Esta función intenta obtener muros del documento. Si GetAllElements
    no está disponible, se intentará usar un método alternativo.
    """
    walls = []
    try:
        if hasattr(AllplanBaseElements.ElementsService, 'GetAllElements'):
            all_elements = AllplanBaseElements.ElementsService.GetAllElements(document)
            if all_elements:
                for element in all_elements:
                    try:
                        element_type = element.GetElementType()
                        if element_type in (AllplanEleAdapter.Wall_TypeUUID, AllplanEleAdapter.WallTier_TypeUUID):
                            walls.append(element)
                    except Exception:
                        continue
    except Exception:
        pass
    return walls

def is_lateral_face(face_normal: AllplanGeo.Vector3D, tolerance: float = 0.1) -> bool:
    """Verifica si una cara es lateral (no superior ni inferior).

    Las caras laterales tienen normal principalmente horizontal (componente Z pequeña).
    Las caras superior/inferior tienen normal principalmente vertical (componente Z grande).
    """
    normal_norm = normalize_vector(face_normal)
    if not normal_norm:
        return False

    abs_z = abs(normal_norm.Z)
    return abs_z < (1.0 - tolerance)

def get_wall_lateral_faces(wall_element) -> list:
    """Obtiene todas las caras laterales de un muro"""
    lateral_faces = []
    try:
        wall_geo = wall_element.GetModelGeometry()
        if not wall_geo:
            wall_geo = wall_element.GetGeometry()

        if isinstance(wall_geo, AllplanGeo.BRep3D):
            error, polyhedron = AllplanGeo.CreatePolyhedron(wall_geo)
            if error != AllplanGeo.eGeometryErrorCode.eOK:
                return lateral_faces
            wall_geo = polyhedron

        if not wall_geo or not isinstance(wall_geo, AllplanGeo.Polyhedron3D):
            return lateral_faces

        faces_count = wall_geo.GetFacesCount()
        for i in range(faces_count):
            face = wall_geo.GetFace(i)
            success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(wall_geo, face)

            if not success or len(face_points) < 3:
                continue

            p0 = face_points[0]
            p1 = face_points[1]
            p2 = face_points[2]

            v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
            v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

            face_normal = vector_cross(v1, v2)
            face_normal = normalize_vector(face_normal)

            if is_lateral_face(face_normal):
                points_list = [face_points[j] for j in range(len(face_points))]
                face_polygon = AllplanGeo.Polygon3D(points_list)

                if face_polygon.Count() >= 3:
                    lateral_faces.append({
                        'index': i,
                        'polygon': face_polygon,
                        'normal': face_normal,
                        'points': face_points
                    })
    except Exception:
        pass

    return lateral_faces

def points_on_plane(points: list[AllplanGeo.Point3D],
                   plane_point: AllplanGeo.Point3D,
                   plane_normal: AllplanGeo.Vector3D,
                   tolerance: float = 1.0) -> bool:
    """Verifica si todos los puntos están en el plano definido por un punto y una normal.

    Usa numpy si está disponible, sino usa cálculo vectorial básico.
    """
    if not points:
        return False

    plane_normal_norm = normalize_vector(plane_normal)
    if not plane_normal_norm:
        return False

    if np is not None:
        try:
            plane_point_np = np.array([plane_point.X, plane_point.Y, plane_point.Z])
            plane_normal_np = np.array([plane_normal_norm.X, plane_normal_norm.Y, plane_normal_norm.Z])

            for point in points:
                point_np = np.array([point.X, point.Y, point.Z])
                vec_to_point = point_np - plane_point_np
                distance = abs(np.dot(vec_to_point, plane_normal_np))

                if distance > tolerance:
                    return False

            return True
        except Exception:
            pass

    for point in points:
        vec_to_point = AllplanGeo.Vector3D(
            point.X - plane_point.X,
            point.Y - plane_point.Y,
            point.Z - plane_point.Z
        )
        distance = abs(vector_dot(vec_to_point, plane_normal_norm))

        if distance > tolerance:
            return False

    return True

def find_wall_containing_line(line: AllplanGeo.Line3D,
                              coord_input,
                              document) -> tuple:
    """Encuentra el muro que contiene la línea usando FaceSelectService

    Obtiene muros del documento y usa SelectWallFace
    para detectar la cara lateral que contiene los puntos de la línea.

    Args:
        line: Línea 3D
        coord_input: CoordinateInput del LineInteractor (opcional)
        document: Documento de Allplan

    Returns:
        (wall_element, face_info) o (None, None) si no se encuentra
    """
    try:
        start_point = line.StartPoint
        end_point = line.EndPoint
        points = [start_point, end_point]

        view_projection = None
        input_document = document
        if coord_input:
            try:
                view_projection = coord_input.GetViewWorldProjection()
                input_document = coord_input.GetInputViewDocument()
            except Exception:
                pass

        walls = get_all_walls_from_document(input_document)
        if not walls:
            return None, None

        start_2d = AllplanGeo.Point2D(start_point.X, start_point.Y)
        end_2d = AllplanGeo.Point2D(end_point.X, end_point.Y)
        midpoint = AllplanGeo.Point3D(
            (start_point.X + end_point.X) / 2.0,
            (start_point.Y + end_point.Y) / 2.0,
            (start_point.Z + end_point.Z) / 2.0
        )
        mid_2d = AllplanGeo.Point2D(midpoint.X, midpoint.Y)

        test_points_2d = [mid_2d, start_2d, end_2d]

        for test_point_2d in test_points_2d:
            for wall in walls:
                try:
                    is_selected, face_polygon, intersect_result = \
                        AllplanBaseElements.FaceSelectService.SelectWallFace(
                            wall, test_point_2d, True,
                            view_projection,
                            input_document, True
                        )

                    if is_selected and face_polygon and intersect_result:
                        face_normal = intersect_result.FaceNv
                        if face_normal and is_lateral_face(face_normal):
                            result = AllplanGeo.CalcMinMax(face_polygon)
                            if isinstance(result, tuple):
                                minmax = result[0]
                            else:
                                minmax = result

                            plane_point = AllplanGeo.Point3D(
                                (minmax.Min.X + minmax.Max.X) / 2.0,
                                (minmax.Min.Y + minmax.Max.Y) / 2.0,
                                (minmax.Min.Z + minmax.Max.Z) / 2.0
                            )

                            if points_on_plane(points, plane_point, face_normal, tolerance=10.0):
                                return wall, {
                                    'polygon': face_polygon,
                                    'normal': face_normal,
                                    'intersect_result': intersect_result
                                }
                except Exception:
                    pass

                try:
                    is_selected, face_polygon, intersect_result = \
                        AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                            wall, test_point_2d, True,
                            view_projection,
                            input_document, True
                        )

                    if is_selected and face_polygon and intersect_result:
                        face_normal = intersect_result.FaceNv
                        if face_normal and is_lateral_face(face_normal):
                            result = AllplanGeo.CalcMinMax(face_polygon)
                            if isinstance(result, tuple):
                                minmax = result[0]
                            else:
                                minmax = result

                            plane_point = AllplanGeo.Point3D(
                                (minmax.Min.X + minmax.Max.X) / 2.0,
                                (minmax.Min.Y + minmax.Max.Y) / 2.0,
                                (minmax.Min.Z + minmax.Max.Z) / 2.0
                            )

                            if points_on_plane(points, plane_point, face_normal, tolerance=10.0):
                                return wall, {
                                    'polygon': face_polygon,
                                    'normal': face_normal,
                                    'intersect_result': intersect_result
                                }
                except Exception:
                    continue

    except Exception:
        pass

    return None, None

def project_point_to_plane(point: AllplanGeo.Point3D,
                           plane_point: AllplanGeo.Point3D,
                           plane_normal: AllplanGeo.Vector3D) -> AllplanGeo.Point3D:
    """Proyecta un punto sobre un plano"""
    normal = normalize_vector(plane_normal)
    if not normal:
        return point

    vec_to_point = AllplanGeo.Vector3D(
        point.X - plane_point.X,
        point.Y - plane_point.Y,
        point.Z - plane_point.Z
    )

    distance = vector_dot(vec_to_point, normal)

    return AllplanGeo.Point3D(
        point.X - distance * normal.X,
        point.Y - distance * normal.Y,
        point.Z - distance * normal.Z
    )

def clamp_point_to_face_bounds(point: AllplanGeo.Point3D,
                               face_polygon: AllplanGeo.Polygon3D,
                               face_normal: AllplanGeo.Vector3D = None,
                               tolerance: float = 1.0) -> AllplanGeo.Point3D:
    """Limita un punto a los límites del polígono de la cara.

    Primero proyecta el punto al plano de la cara, luego lo limita al bounding box
    del polígono. Si el punto está fuera del polígono, lo mueve al punto más cercano
    dentro del bounding box.
    """
    try:
        if not face_polygon or face_polygon.Count() < 3:
            return point

        if face_normal:
            result = AllplanGeo.CalcMinMax(face_polygon)
            if isinstance(result, tuple):
                minmax = result[0]
            else:
                minmax = result

            plane_point = AllplanGeo.Point3D(
                (minmax.Min.X + minmax.Max.X) / 2.0,
                (minmax.Min.Y + minmax.Max.Y) / 2.0,
                (minmax.Min.Z + minmax.Max.Z) / 2.0
            )

            point = project_point_to_plane(point, plane_point, face_normal)

        result = AllplanGeo.CalcMinMax(face_polygon)
        if isinstance(result, tuple):
            minmax = result[0]
        else:
            minmax = result

        clamped_point = AllplanGeo.Point3D(
            max(minmax.Min.X - tolerance, min(minmax.Max.X + tolerance, point.X)),
            max(minmax.Min.Y - tolerance, min(minmax.Max.Y + tolerance, point.Y)),
            max(minmax.Min.Z - tolerance, min(minmax.Max.Z + tolerance, point.Z))
        )

        return clamped_point
    except Exception:
        return point

def project_line_on_face(line: AllplanGeo.Line3D,
                        face_point: AllplanGeo.Point3D,
                        face_normal: AllplanGeo.Vector3D) -> AllplanGeo.Line3D:
    """Proyecta una línea sobre el plano de una cara"""
    try:
        normal = normalize_vector(face_normal)
        if not normal:
            return line

        projected_start = project_point_to_plane(line.StartPoint, face_point, normal)
        projected_end = project_point_to_plane(line.EndPoint, face_point, normal)

        return AllplanGeo.Line3D(projected_start, projected_end)
    except Exception:
        return line

def clamp_line_to_face_bounds(line: AllplanGeo.Line3D,
                              face_polygon: AllplanGeo.Polygon3D,
                              face_normal: AllplanGeo.Vector3D = None) -> AllplanGeo.Line3D:
    """Recorta la línea a los límites de la cara del muro.

    Primero proyecta la línea sobre el plano de la cara, luego la recorta
    a los límites del polígono usando intersección con los bordes.
    """
    try:
        if not face_polygon or face_polygon.Count() < 3:
            return line

        if face_normal:
            result = AllplanGeo.CalcMinMax(face_polygon)
            if isinstance(result, tuple):
                minmax = result[0]
            else:
                minmax = result

            plane_point = AllplanGeo.Point3D(
                (minmax.Min.X + minmax.Max.X) / 2.0,
                (minmax.Min.Y + minmax.Max.Y) / 2.0,
                (minmax.Min.Z + minmax.Max.Z) / 2.0
            )

            line = project_line_on_face(line, plane_point, face_normal)

        result = AllplanGeo.CalcMinMax(face_polygon)
        if isinstance(result, tuple):
            minmax = result[0]
        else:
            minmax = result

        start = line.StartPoint
        end = line.EndPoint

        line_dir = AllplanGeo.Vector3D(end.X - start.X, end.Y - start.Y, end.Z - start.Z)
        line_length = line_dir.GetLength()
        if line_length < 1e-6:
            return line

        line_dir = normalize_vector(line_dir)

        def clamp_point_to_box(point: AllplanGeo.Point3D, minmax) -> AllplanGeo.Point3D:
            return AllplanGeo.Point3D(
                max(minmax.Min.X, min(minmax.Max.X, point.X)),
                max(minmax.Min.Y, min(minmax.Max.Y, point.Y)),
                max(minmax.Min.Z, min(minmax.Max.Z, point.Z))
            )

        clamped_start = clamp_point_to_box(start, minmax)
        clamped_end = clamp_point_to_box(end, minmax)

        return AllplanGeo.Line3D(clamped_start, clamped_end)
    except Exception:
        return line

def adjust_line_length_incremental(line: AllplanGeo.Line3D,
                                    increment: float) -> AllplanGeo.Line3D:
    """Ajusta la longitud de la línea en incrementos especificados.

    La línea crece en incrementos del valor especificado.
    Por ejemplo, si el incremento es 150mm:
    - Longitudes posibles: 150mm, 300mm (150*2), 450mm (150*3), etc.
    Si el incremento es 370mm:
    - Longitudes posibles: 370mm, 740mm (370*2), 1110mm (370*3), etc.
    """
    try:
        if increment < 1e-6:
            return line

        start = line.StartPoint
        end = line.EndPoint

        line_vector = vector_from_points(start, end)
        current_length = line_vector.GetLength()

        if current_length < 1e-6:
            return line

        line_dir = normalize_vector(line_vector)

        num_increments = int(math.floor(current_length / increment))
        adjusted_length = (num_increments + 1) * increment

        adjusted_end = move_point(start, line_dir, adjusted_length)

        return AllplanGeo.Line3D(start, adjusted_end)
    except Exception:
        return line

def set_line_length(line: AllplanGeo.Line3D, length: float) -> AllplanGeo.Line3D:
    """Mantiene el punto inicial y ajusta el final al largo indicado."""
    try:
        if length < 1e-6:
            return line

        start = line.StartPoint
        end = line.EndPoint
        line_vector = vector_from_points(start, end)
        line_dir = normalize_vector(line_vector)
        if not line_dir:
            return line

        adjusted_end = move_point(start, line_dir, length)
        return AllplanGeo.Line3D(start, adjusted_end)
    except Exception:
        return line

def create_single_angular(definition: dict,
                          origin: AllplanGeo.Point3D,
                          x_dir: AllplanGeo.Vector3D,
                          y_dir: AllplanGeo.Vector3D,
                          z_dir: AllplanGeo.Vector3D,
                          invert_profile: bool = False) -> AllplanGeo.BRep3D:
    """Crea un angular orientado según los ejes indicados.

    Args:
        invert_profile: Parámetro heredado (no se usa aquí).
                       El reflejo lateral se hace invirtiendo el sistema local (y_dir) en create_angulars_on_line
                       antes de llamar a esta función, para cambiar de lado respecto a la línea sin cambiar la forma.
    """
    length = definition["length"]
    vertical = definition["vertical"]
    horizontal = definition["horizontal"]
    thickness = definition["thickness"]

    angular_origin = move_point(origin, x_dir, -length / 2.0)

    horizontal_axis = axis_with_offset(angular_origin, x_dir, y_dir, z_dir, 0.0, 0.0, 0.0)
    horizontal_leg = AllplanGeo.BRep3D.CreateCuboid(horizontal_axis, length, horizontal, thickness)

    vertical_axis = axis_with_offset(angular_origin, x_dir, y_dir, z_dir, 0.0, 0.0, 0.0)
    vertical_leg = AllplanGeo.BRep3D.CreateCuboid(vertical_axis, length, thickness, vertical)

    err, geometry = AllplanGeo.MakeUnion(horizontal_leg, vertical_leg)
    if err != AllplanGeo.eGeometryErrorCode.eOK:
        geometry = vertical_leg

    fillet_radius = 8.0
    edge_count = geometry.GetEdgeCount()

    all_edges_info = []
    for edge_idx in range(edge_count):
        err, p_start, p_end = geometry.GetEdgeVertices(edge_idx)
        if err == AllplanGeo.eGeometryErrorCode.eOK:
            edge_vec = AllplanGeo.Vector3D(p_end.X - p_start.X, p_end.Y - p_start.Y, p_end.Z - p_start.Z)
            edge_length = edge_vec.GetLength()
            edge_vec_normalized = normalize_vector(edge_vec) if edge_length > 1e-6 else AllplanGeo.Vector3D(0, 0, 0)

            is_horizontal = abs(p_start.Z - p_end.Z) < 1e-3
            is_vertical = abs(p_start.X - p_end.X) < 1e-3 and abs(p_start.Y - p_end.Y) < 1e-3

            edge_info = {
                'idx': edge_idx,
                'start': p_start,
                'end': p_end,
                'z_start': p_start.Z,
                'z_end': p_end.Z,
                'is_horizontal': is_horizontal,
                'is_vertical': is_vertical,
                'direction': edge_vec_normalized,
                'length': edge_length
            }
            all_edges_info.append(edge_info)

    def points_equal(p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D, tolerance: float = 1e-3) -> bool:
        """Verifica si dos puntos son iguales dentro de una tolerancia"""
        return (abs(p1.X - p2.X) < tolerance and
                abs(p1.Y - p2.Y) < tolerance and
                abs(p1.Z - p2.Z) < tolerance)

    connections = {}

    for i, edge_i in enumerate(all_edges_info):
        connections[edge_i['idx']] = []
        for j, edge_j in enumerate(all_edges_info):
            if i == j:
                continue
            shares_vertex = (
                points_equal(edge_i['start'], edge_j['start']) or
                points_equal(edge_i['start'], edge_j['end']) or
                points_equal(edge_i['end'], edge_j['start']) or
                points_equal(edge_i['end'], edge_j['end'])
            )
            if shares_vertex:
                connections[edge_i['idx']].append(edge_j['idx'])

    consecutive_segments = []
    processed_pairs = set()

    for i, edge_i in enumerate(all_edges_info):
        for j, edge_j in enumerate(all_edges_info):
            if i >= j:
                continue
            pair_key = (min(edge_i['idx'], edge_j['idx']), max(edge_i['idx'], edge_j['idx']))
            if pair_key in processed_pairs:
                continue

            shares_vertex = (
                points_equal(edge_i['start'], edge_j['start']) or
                points_equal(edge_i['start'], edge_j['end']) or
                points_equal(edge_i['end'], edge_j['start']) or
                points_equal(edge_i['end'], edge_j['end'])
            )

            if shares_vertex:
                dot_product = (edge_i['direction'].X * edge_j['direction'].X +
                              edge_i['direction'].Y * edge_j['direction'].Y +
                              edge_i['direction'].Z * edge_j['direction'].Z)
                is_parallel = abs(abs(dot_product) - 1.0) < 0.1

                same_plane = abs(edge_i['z_start'] - edge_j['z_start']) < 1e-3

                segment_info = {
                    'edges': [edge_i['idx'], edge_j['idx']],
                    'lengths': [edge_i['length'], edge_j['length']],
                    'is_parallel': is_parallel,
                    'same_plane': same_plane,
                    'dot_product': dot_product
                }
                consecutive_segments.append(segment_info)
                processed_pairs.add(pair_key)

    all_target_edges: list[int] = []

    edge_0_info = None
    edge_0_info = None
    edge_14_info = None

    for edge_info in all_edges_info:
        if edge_info['idx'] == 0:
            edge_0_info = edge_info
        elif edge_info['idx'] == 14:
            edge_14_info = edge_info

    if edge_0_info is None or edge_14_info is None:
        candidate_indices = [0, 14]
    else:
        target_edges_set = set()

        dot_0_with_z = (edge_0_info['direction'].X * z_dir.X +
                       edge_0_info['direction'].Y * z_dir.Y +
                       edge_0_info['direction'].Z * z_dir.Z)
        is_0_horizontal = abs(dot_0_with_z) < 0.1
        if is_0_horizontal:
            target_edges_set.add(0)

        dot_14_with_z = (edge_14_info['direction'].X * z_dir.X +
                        edge_14_info['direction'].Y * z_dir.Y +
                        edge_14_info['direction'].Z * z_dir.Z)
        is_14_horizontal = abs(dot_14_with_z) < 0.1
        if is_14_horizontal:
            target_edges_set.add(14)

        edge_2_info = None
        for edge_info in all_edges_info:
            if edge_info['idx'] == 2:
                edge_2_info = edge_info
                break

        if edge_2_info is not None:
            dot_with_z = (edge_2_info['direction'].X * z_dir.X +
                         edge_2_info['direction'].Y * z_dir.Y +
                         edge_2_info['direction'].Z * z_dir.Z)
            is_horizontal = abs(dot_with_z) < 0.1

            z_2 = edge_2_info['z_start']
            z_0 = edge_0_info['z_start']
            is_same_height_as_0 = abs(z_2 - z_0) < 1e-3

            dot_with_0 = (edge_2_info['direction'].X * edge_0_info['direction'].X +
                         edge_2_info['direction'].Y * edge_0_info['direction'].Y +
                         edge_2_info['direction'].Z * edge_0_info['direction'].Z)
            is_parallel_to_0 = abs(abs(dot_with_0) - 1.0) < 0.1

            shares_with_connected_to_0 = False
            edges_connected_to_0 = connections.get(0, [])
            for connected_edge_idx in connections.get(2, []):
                if connected_edge_idx in edges_connected_to_0:
                    shares_with_connected_to_0 = True
                    break

            if is_horizontal and is_same_height_as_0 and is_parallel_to_0 and shares_with_connected_to_0:
                target_edges_set.add(2)

        if 12 in target_edges_set:
            target_edges_set.remove(12)

        all_target_edges = sorted(list(target_edges_set))

        if len(all_target_edges) < 2:
            candidate_indices = [0, 14]
            all_target_edges = []
        else:
            candidate_indices = []

    if len(all_target_edges) == 0:
        for edge_idx in candidate_indices:
            if edge_idx >= edge_count:
                continue

            err, p_start, p_end = geometry.GetEdgeVertices(edge_idx)
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                continue

            vec_to_start = AllplanGeo.Vector3D(p_start.X - angular_origin.X,
                                              p_start.Y - angular_origin.Y,
                                              p_start.Z - angular_origin.Z)
            vec_to_end = AllplanGeo.Vector3D(p_end.X - angular_origin.X,
                                            p_end.Y - angular_origin.Y,
                                            p_end.Z - angular_origin.Z)

            z_start_local = (vec_to_start.X * z_dir.X +
                            vec_to_start.Y * z_dir.Y +
                            vec_to_start.Z * z_dir.Z)
            z_end_local = (vec_to_end.X * z_dir.X +
                           vec_to_end.Y * z_dir.Y +
                           vec_to_end.Z * z_dir.Z)

            z_avg = (z_start_local + z_end_local) / 2.0
            is_at_thickness = abs(z_avg - thickness) < 1e-3
            is_at_vertical = abs(z_avg - vertical) < 1e-3

            edge_vec = AllplanGeo.Vector3D(p_end.X - p_start.X,
                                          p_end.Y - p_start.Y,
                                          p_end.Z - p_start.Z)
            edge_length = edge_vec.GetLength()
            if edge_length < 1e-3:
                continue

            edge_dir = normalize_vector(edge_vec)
            dot_with_z = (edge_dir.X * z_dir.X +
                         edge_dir.Y * z_dir.Y +
                         edge_dir.Z * z_dir.Z)
            is_horizontal = abs(dot_with_z) < 0.1

            y_start_local = (vec_to_start.X * y_dir.X +
                            vec_to_start.Y * y_dir.Y +
                            vec_to_start.Z * y_dir.Z)
            y_end_local = (vec_to_end.X * y_dir.X +
                          vec_to_end.Y * y_dir.Y +
                          vec_to_end.Z * y_dir.Z)
            y_avg = (y_start_local + y_end_local) / 2.0

            is_interior = abs(y_avg) < horizontal * 0.6

            if edge_idx == 12:
                continue

            if (is_at_thickness or is_at_vertical) and is_horizontal and is_interior:
                all_target_edges.append(edge_idx)

    if len(all_target_edges) < 2:
        for edge_info in all_edges_info:
            if edge_info['idx'] in all_target_edges:
                continue

            vec_to_start = AllplanGeo.Vector3D(edge_info['start'].X - angular_origin.X,
                                              edge_info['start'].Y - angular_origin.Y,
                                              edge_info['start'].Z - angular_origin.Z)
            z_start_local = (vec_to_start.X * z_dir.X +
                            vec_to_start.Y * z_dir.Y +
                            vec_to_start.Z * z_dir.Z)

            is_at_thickness = abs(z_start_local - thickness) < 1e-3
            is_at_vertical = abs(z_start_local - vertical) < 1e-3

            dot_with_z = (edge_info['direction'].X * z_dir.X +
                         edge_info['direction'].Y * z_dir.Y +
                         edge_info['direction'].Z * z_dir.Z)
            is_horizontal = abs(dot_with_z) < 0.1

            y_start_local = (vec_to_start.X * y_dir.X +
                            vec_to_start.Y * y_dir.Y +
                            vec_to_start.Z * y_dir.Z)
            is_interior = abs(y_start_local) < horizontal * 0.6

            if edge_info['idx'] == 12:
                continue

            if (is_at_thickness or is_at_vertical) and is_horizontal and is_interior and edge_info['length'] > 1e-3:
                all_target_edges.append(edge_info['idx'])
                if len(all_target_edges) >= 3:
                    break

    if 12 in all_target_edges:
        all_target_edges.remove(12)

    if all_target_edges:
        vec_edges = AllplanUtil.VecSizeTList(all_target_edges)
        fillet_err, filleted_geometry = AllplanGeo.FilletCalculus3D.Calculate(geometry, vec_edges, fillet_radius, False)
        if fillet_err == AllplanGeo.eFilletErrorCode.eNO_ERROR:
            geometry = filleted_geometry

    for row in definition["hole_rows"]:
        hole_y = row["y"]
        for hole_x in row["x_positions"]:
            hole_origin = local_to_world(angular_origin, x_dir, y_dir, z_dir, hole_x, hole_y, 0.0)
            hole_axis = AllplanGeo.AxisPlacement3D(hole_origin, x_dir, z_dir)
            hole_cylinder = AllplanGeo.BRep3D.CreateCylinder(hole_axis, HOLE_RADIUS, thickness)
            err, geometry = AllplanGeo.MakeSubtraction(geometry, hole_cylinder)
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                continue

    return geometry

def create_tensor_solid(origin: AllplanGeo.Point3D,
                        x_dir: AllplanGeo.Vector3D,
                        y_dir: AllplanGeo.Vector3D,
                        z_dir: AllplanGeo.Vector3D,
                        invert_profile: bool = False,
                        rotation_deg: float = 0.0) -> AllplanGeo.BRep3D:
    """Crea un Tensor orientado según los ejes indicados.

    Args:
        origin: Punto de origen del tensor
        x_dir: Dirección del eje X (longitudinal)
        y_dir: Dirección del eje Y (transversal)
        z_dir: Dirección del eje Z (vertical)
        invert_profile: Si True, refleja el tensor
        rotation_deg: Rotación en grados alrededor del eje x_dir

    Returns:
        BRep3D del tensor completo
    """
    y_dir_rotated = y_dir
    z_dir_rotated = z_dir
    if abs(rotation_deg) > 1e-6:
        rotation_rad = math.radians(rotation_deg)
        y_dir_rotated = rotate_vector_around_axis(y_dir, x_dir, rotation_rad)
        z_dir_rotated = rotate_vector_around_axis(z_dir, x_dir, rotation_rad)
        y_dir_rotated = normalize_vector(y_dir_rotated)
        z_dir_rotated = normalize_vector(z_dir_rotated)

    largo_placa_x = 10.0
    ancho_placa_y = 200.0
    alto_placa_z = 300.0
    diametro_taladros = HOLE_DIAMETER
    largo_placa_d_y = 132.5
    ancho_placa_d_x = 14.0
    alto_placa_d_z = 130.0
    diametro_taladro_d = 85.0
    distancia_taladro_d_y = 65.0
    distancia_taladro_d_z = 65.0
    diametro_semi_d = 130.0
    radio_semi_d = diametro_semi_d / 2.0
    distancia_semi_d_y = 65.0
    distancia_semi_d_z = 65.0

    axis_principal = AllplanGeo.AxisPlacement3D(origin, x_dir, z_dir_rotated)
    placa_principal = AllplanGeo.BRep3D.CreateCuboid(
        axis_principal,
        ancho_placa_y,
        largo_placa_x,
        alto_placa_z
    )

    hole_rows = [
        {"z": alto_placa_z - 25.0, "x_positions": [25.0, 175.0]},
        {"z": 25.0, "x_positions": [25.0, 175.0]}
    ]

    for row in hole_rows:
        hole_z = row["z"]
        for hole_x in row["x_positions"]:
            hole_origin = local_to_world(origin, x_dir, y_dir_rotated, z_dir_rotated, hole_x, 0.0, hole_z)
            hole_axis = AllplanGeo.AxisPlacement3D(hole_origin, x_dir, y_dir_rotated)
            altura_cilindro = ancho_placa_y * 2.0
            hole_cylinder = AllplanGeo.BRep3D.CreateCylinder(hole_axis, HOLE_RADIUS, altura_cilindro)
            err, placa_principal = AllplanGeo.MakeSubtraction(placa_principal, hole_cylinder)
            if err != AllplanGeo.eGeometryErrorCode.eOK:
                continue

    axis_d = AllplanGeo.AxisPlacement3D(origin, y_dir_rotated, z_dir_rotated)
    placa_d = AllplanGeo.BRep3D.CreateCuboid(
        axis_d,
        largo_placa_d_y,
        ancho_placa_d_x,
        alto_placa_d_z
    )

    center_y = distancia_taladro_d_y
    center_z = distancia_taladro_d_z

    hole_origin_d = local_to_world(
        origin, x_dir, y_dir_rotated, z_dir_rotated,
        -ancho_placa_d_x,
        center_y,
        center_z
    )

    hole_axis_d = AllplanGeo.AxisPlacement3D(
        hole_origin_d,
        y_dir_rotated,
        x_dir
    )

    hole_cylinder_d = AllplanGeo.BRep3D.CreateCylinder(
        hole_axis_d,
        diametro_taladro_d / 2.0,
        ancho_placa_d_x * 2.0
    )

    err, placa_d = AllplanGeo.MakeSubtraction(placa_d, hole_cylinder_d)
    if err != AllplanGeo.eGeometryErrorCode.eOK:
        pass

    eps = 0.5

    big_origin = local_to_world(
        origin, x_dir, y_dir_rotated, z_dir_rotated,
        -ancho_placa_d_x - eps,
        center_y,
        center_z
    )

    big_axis = AllplanGeo.AxisPlacement3D(big_origin, y_dir_rotated, x_dir)

    big_cylinder = AllplanGeo.BRep3D.CreateCylinder(
        big_axis,
        radio_semi_d + eps,
        (ancho_placa_d_x + eps) * 2.0
    )

    left_axis = AllplanGeo.AxisPlacement3D(origin, y_dir_rotated, z_dir_rotated)

    left_box = AllplanGeo.BRep3D.CreateCuboid(
        left_axis,
        center_y + eps,
        ancho_placa_d_x + eps,
        alto_placa_d_z + eps
    )

    err, tips = AllplanGeo.MakeSubtraction(left_box, big_cylinder)
    if err != AllplanGeo.eGeometryErrorCode.eOK:
        pass
    else:
        err, placa_d = AllplanGeo.MakeSubtraction(placa_d, tips)
        if err != AllplanGeo.eGeometryErrorCode.eOK:
            pass

    offset_x = 107.0
    offset_y = -132.5
    offset_z = 85.0

    mat = AllplanGeo.Matrix3D()
    offset_vec = AllplanGeo.Vector3D(
        x_dir.X * offset_x + y_dir_rotated.X * offset_y + z_dir_rotated.X * offset_z,
        x_dir.Y * offset_x + y_dir_rotated.Y * offset_y + z_dir_rotated.Y * offset_z,
        x_dir.Z * offset_x + y_dir_rotated.Z * offset_y + z_dir_rotated.Z * offset_z
    )
    mat.SetTranslation(offset_vec)

    placa_d_pos = AllplanGeo.Transform(placa_d, mat)

    err, geometry = AllplanGeo.MakeUnion(placa_principal, placa_d_pos)
    if err != AllplanGeo.eGeometryErrorCode.eOK:
        geometry = placa_principal

    shift_y = -largo_placa_x

    mat_origin = AllplanGeo.Matrix3D()
    shift_vec = AllplanGeo.Vector3D(
        y_dir_rotated.X * shift_y,
        y_dir_rotated.Y * shift_y,
        y_dir_rotated.Z * shift_y
    )
    mat_origin.SetTranslation(shift_vec)
    geometry = AllplanGeo.Transform(geometry, mat_origin)

    return geometry

def get_bounding_box_from_geometry(geometry: AllplanGeo.BRep3D) -> dict:
    """Obtiene el bounding box de una geometría BRep3D.

    Returns:
        dict con keys: 'min', 'max', 'center', 'width', 'height', 'depth'
    """
    try:
        err, bbox = geometry.GetBoundingBox()
        if err == AllplanGeo.eGeometryErrorCode.eOK and bbox:
            min_pt = bbox.MinPoint
            max_pt = bbox.MaxPoint
            center = AllplanGeo.Point3D(
                (min_pt.X + max_pt.X) / 2.0,
                (min_pt.Y + max_pt.Y) / 2.0,
                (min_pt.Z + max_pt.Z) / 2.0
            )
            return {
                'min': min_pt,
                'max': max_pt,
                'center': center,
                'width': abs(max_pt.X - min_pt.X),
                'height': abs(max_pt.Y - min_pt.Y),
                'depth': abs(max_pt.Z - min_pt.Z)
            }
    except Exception as e:
        return None

def get_bounding_box_from_wall_element(wall_element) -> dict:
    """Obtiene el bounding box de un elemento de muro.

    Returns:
        dict con keys: 'min', 'max', 'center', 'width', 'height', 'depth'
    """
    try:
        if not wall_element:
            return None

        wall_geo = None
        if hasattr(wall_element, 'GetModelGeometry'):
            wall_geo = wall_element.GetModelGeometry()
        elif hasattr(wall_element, 'GetGeometry'):
            wall_geo = wall_element.GetGeometry()

        if not wall_geo:
            return None

        if isinstance(wall_geo, AllplanGeo.BRep3D):
            return get_bounding_box_from_geometry(wall_geo)
        elif hasattr(wall_geo, 'GetBoundingBox'):
            err, bbox = wall_geo.GetBoundingBox()
            if err == AllplanGeo.eGeometryErrorCode.eOK and bbox:
                min_pt = bbox.MinPoint
                max_pt = bbox.MaxPoint
                center = AllplanGeo.Point3D(
                    (min_pt.X + max_pt.X) / 2.0,
                    (min_pt.Y + max_pt.Y) / 2.0,
                    (min_pt.Z + max_pt.Z) / 2.0
                )
                return {
                    'min': min_pt,
                    'max': max_pt,
                    'center': center,
                    'width': abs(max_pt.X - min_pt.X),
                    'height': abs(max_pt.Y - min_pt.Y),
                    'depth': abs(max_pt.Z - min_pt.Z)
                }
    except Exception as e:
        return None

def find_opposite_face_info(wall_element, current_face_normal: AllplanGeo.Vector3D, tolerance: float = 0.1) -> tuple:
    """Encuentra la cara opuesta del muro basándose en la normal de la cara actual.

    Args:
        wall_element: Elemento del muro
        current_face_normal: Normal de la cara frontal (normalizada)
        tolerance: Tolerancia para comparar normales opuestas

    Returns:
        tuple: (opposite_face_polygon, opposite_face_normal, opposite_face_point) o (None, None, None)
    """
    try:
        lateral_faces = get_wall_lateral_faces(wall_element)
        if not lateral_faces:
            return (None, None, None)

        opposite_face = None
        best_dot_product = -2.0

        for face_info in lateral_faces:
            face_normal = face_info['normal']
            if not face_normal:
                continue

            dot_product = vector_dot(current_face_normal, face_normal)

            if dot_product < best_dot_product:
                best_dot_product = dot_product
                opposite_face = face_info

        if opposite_face and best_dot_product < -tolerance:
            opposite_polygon = opposite_face['polygon']
            opposite_normal = opposite_face['normal']

            if opposite_polygon and opposite_polygon.Count() > 0:
                opposite_points = opposite_face['points']
                if opposite_points and len(opposite_points) > 0:
                    sum_x = sum(p.X for p in opposite_points)
                    sum_y = sum(p.Y for p in opposite_points)
                    sum_z = sum(p.Z for p in opposite_points)
                    count = len(opposite_points)
                    opposite_face_point = AllplanGeo.Point3D(
                        sum_x / count,
                        sum_y / count,
                        sum_z / count
                    )
                    return (opposite_polygon, opposite_normal, opposite_face_point)

        return (None, None, None)
    except Exception as e:
        return (None, None, None)

def normalize_line_direction(start: AllplanGeo.Point3D,
                              end: AllplanGeo.Point3D) -> tuple[AllplanGeo.Point3D, AllplanGeo.Point3D, bool]:
    """Normaliza la dirección de la línea para que siempre avance en dirección positiva del eje dominante.

    Si la línea está "invertida" (derecha → izquierda), intercambia start y end.

    Args:
        start: Punto inicial de la línea
        end: Punto final de la línea

    Returns:
        tuple: (start_normalized, end_normalized, was_reversed)
    """
    vec = vector_from_points(start, end)
    dir_vec = normalize_vector(vec)

    if not dir_vec:
        return start, end, False

    if abs(dir_vec.X) >= abs(dir_vec.Y) and abs(dir_vec.X) >= abs(dir_vec.Z):
        if dir_vec.X < 0:
            return end, start, True
    elif abs(dir_vec.Y) >= abs(dir_vec.Z):
        if dir_vec.Y < 0:
            return end, start, True
    else:
        if dir_vec.Z < 0:
            return end, start, True

    return start, end, False

def create_single_angular_on_line(definition: dict,
                                  start_point: AllplanGeo.Point3D,
                                  end_point: AllplanGeo.Point3D,
                                  invert_side: bool,
                                  rotation_deg: float,
                                  rotation_y_deg: float = 0.0,
                                  face_normal: AllplanGeo.Vector3D = None,
                                  face_point: AllplanGeo.Point3D = None,
                                  is_opposite_face: bool = False,
                                  is_free_mode: bool = False) -> tuple[list[AllplanGeo.BRep3D], list[AllplanGeo.Line3D]]:
    """Genera una sola pieza posicionada desde el punto inicial de la línea."""
    is_tensor = bool(definition.get("is_tensor", False))
    if not is_tensor:
        rotation_deg = rotation_deg + 90.0
    if is_tensor and not is_free_mode:
        return [], []

    base_vector = get_base_vector(start_point, end_point, face_normal, is_opposite_face)
    if base_vector.GetLength() < 1e-6:
        return [], []

    x_dir, y_dir, z_dir = decompose_vector(base_vector, rotation_deg, face_normal, is_opposite_face)
    x_dir, y_dir, z_dir = apply_local_y_rotation(x_dir, y_dir, z_dir, rotation_y_deg)
    piece_length = definition.get("piece_length", definition.get("length", 0.0))
    if piece_length <= 0:
        return [], []

    if face_normal and face_point:
        origin = project_point_to_plane(start_point, face_point, face_normal)
    else:
        origin = start_point

    if is_tensor:
        geometry = create_tensor_solid(
            origin=origin,
            x_dir=x_dir,
            y_dir=y_dir,
            z_dir=z_dir,
            invert_profile=False,
            rotation_deg=rotation_deg
        )
        edge = create_edge_angulars_group(
            definition=definition,
            start_point=origin,
            x_dir=x_dir,
            y_dir=y_dir,
            z_dir=z_dir,
            piece_length=piece_length,
            is_tensor=True
        )

        if invert_side:
            reflection_plane = AllplanGeo.Plane3D(origin, y_dir)
            mirror = AllplanGeo.Matrix3D()
            mirror.SetReflection(reflection_plane)
            geometry = AllplanGeo.Transform(geometry, mirror)
            edge = AllplanGeo.Transform(edge, mirror)

        return [geometry], [edge]

    geometry = create_single_angular(definition, origin, x_dir, y_dir, z_dir, invert_profile=False)
    edge = create_edge_angulars_group(
        definition=definition,
        start_point=origin,
        x_dir=x_dir,
        y_dir=y_dir,
        z_dir=z_dir,
        piece_length=piece_length
    )

    if invert_side:
        reflection_plane = AllplanGeo.Plane3D(origin, z_dir)
        mirror = AllplanGeo.Matrix3D()
        mirror.SetReflection(reflection_plane)
        geometry = AllplanGeo.Transform(geometry, mirror)
        edge = AllplanGeo.Transform(edge, mirror)

    return [geometry], [edge]

def create_angulars_on_line(definition: dict,
                            start_point: AllplanGeo.Point3D,
                            end_point: AllplanGeo.Point3D,
                            invert_side: bool,
                            rotation_deg: float,
                            rotation_y_deg: float = 0.0,
                            gap: float = 10.0,
                            face_normal: AllplanGeo.Vector3D = None,
                            face_point: AllplanGeo.Point3D = None,
                            face_polygon: AllplanGeo.Polygon3D = None,
                            wall_element=None,
                            is_opposite_face: bool = False,
                            is_free_mode: bool = False) -> tuple[list[AllplanGeo.BRep3D], list[AllplanGeo.Line3D]]:
    """Genera la lista de geometrías posicionadas a lo largo de la línea.

    Si se proporciona face_normal y face_point, los angulares se posicionan fuera del muro
    (sobresaliendo) según la normal de la cara, con las perforaciones acopladas a la superficie.
    """
    wall_bbox = None
    if wall_element:
        wall_bbox = get_bounding_box_from_wall_element(wall_element)

    is_tensor = bool(definition.get("is_tensor", False))
    if not is_tensor:
        rotation_deg = rotation_deg + 90.0
    if is_tensor and not is_free_mode:
        return [], []

    base_vector = get_base_vector(start_point, end_point, face_normal, is_opposite_face)
    x_dir, y_dir, z_dir = decompose_vector(base_vector, rotation_deg, face_normal, is_opposite_face)
    x_dir, y_dir, z_dir = apply_local_y_rotation(x_dir, y_dir, z_dir, rotation_y_deg)

    line_length = base_vector.GetLength()
    if line_length < 1e-6:
        return [], []

    piece_length = definition.get("piece_length", definition.get("length", 0.0))

    if piece_length <= line_length:
        max_pieces_float = (line_length + gap) / (piece_length + gap)
        piece_count = int(math.floor(max_pieces_float))

        if piece_count < 1:
            piece_count = 0
        else:
            total_length = piece_count * piece_length + (piece_count - 1) * gap
            if total_length > line_length + 1e-3:
                piece_count = max(0, piece_count - 1)
    else:
        piece_count = 0

    if piece_count == 0:
        return []

    geometries: list[AllplanGeo.BRep3D] = []
    edges: list[AllplanGeo.Line3D] = []

    start_offset = 0.0

    for index in range(piece_count):
        offset_y = start_offset + index * (piece_length + gap)
        line_origin = move_point(start_point, x_dir, offset_y)

        if face_normal and face_point:
            projected_origin = project_point_to_plane(line_origin, face_point, face_normal)
            origin = projected_origin
        else:
            origin = line_origin

        if is_tensor:
            tensor = create_tensor_solid(
                origin=origin,
                x_dir=x_dir,
                y_dir=y_dir,
                z_dir=z_dir,
                invert_profile=False,
                rotation_deg=rotation_deg
            )
            edge = create_edge_angulars_group(
                definition=definition,
                start_point=origin,
                x_dir=x_dir,
                y_dir=y_dir,
                z_dir=z_dir,
                piece_length=piece_length,
                is_tensor = True
            )

            if invert_side:
                reflection_plane = AllplanGeo.Plane3D(origin, y_dir)
                mirror = AllplanGeo.Matrix3D()
                mirror.SetReflection(reflection_plane)
                tensor = AllplanGeo.Transform(tensor, mirror)
                edge = AllplanGeo.Transform(edge, mirror)

            edges.append(edge)
            geometries.append(tensor)
        else:
            geometry = create_single_angular(definition, origin, x_dir, y_dir, z_dir, invert_profile=False)
            edge = create_edge_angulars_group(
                definition=definition,
                start_point=origin,
                x_dir=x_dir,
                y_dir=y_dir,
                z_dir=z_dir,
                piece_length=piece_length
            )

            if invert_side:
                reflection_plane = AllplanGeo.Plane3D(origin, z_dir)
                mirror = AllplanGeo.Matrix3D()
                mirror.SetReflection(reflection_plane)
                geometry = AllplanGeo.Transform(geometry, mirror)
                edge = AllplanGeo.Transform(edge, mirror)

            edges.append(edge)
            geometries.append(geometry)

    return geometries, edges

def create_edge_angulars_group(definition,
                                start_point: AllplanGeo.Point3D,
                                x_dir: AllplanGeo.Vector3D,
                                y_dir: AllplanGeo.Vector3D,
                                z_dir: AllplanGeo.Vector3D,
                                piece_length: float,
                                is_tensor: bool = False) -> AllplanGeo.Line3D:

    thickness = definition["thickness"]
    if not is_tensor:
        guide_start = move_point(start_point, x_dir, -piece_length / 2.0)
        guide_end = move_point(start_point, x_dir, piece_length / 2.0)

        origin = move_point(guide_start, x_dir, 0.0)
        origin = move_point(origin, z_dir, thickness)
        origin = move_point(origin, y_dir, thickness)

        final = move_point(guide_end, x_dir, 0.0)
        final = move_point(final, z_dir, thickness)
        final = move_point(final, y_dir, thickness)
    else:
        guide_start = start_point
        guide_end = move_point(start_point, x_dir, piece_length)

        origin = move_point(start_point, x_dir, 0.0)
        origin = move_point(origin, z_dir, definition["vertical"])
        origin = move_point(origin, y_dir, -thickness)

        final = move_point(guide_end, x_dir, 0.0)
        final = move_point(final, z_dir, definition["vertical"])
        final = move_point(final, y_dir, -thickness)

    axis_origin = local_to_world(origin, x_dir, y_dir, z_dir, 0.0, 0.0, 0.0)
    axis_point = AllplanGeo.Axis3D(axis_origin, AllplanGeo.Vector3D(guide_start, guide_end))
    pnt_inici = AllplanGeo.Rotate(origin, axis_point, AllplanGeo.Angle.FromDeg(0.0))
    pnt_final = AllplanGeo.Rotate(final, axis_point, AllplanGeo.Angle.FromDeg(0.0))
    line = AllplanGeo.Line3D(pnt_inici, pnt_final)

    return line

def get_base_vector(start_point: AllplanGeo.Point3D,
                            end_point: AllplanGeo.Point3D,
                            face_normal: AllplanGeo.Vector3D = None,
                            is_opposite_face: bool = False) -> AllplanGeo.Vector3D:

    if face_normal:
        start_n, end_n, reversed_line = normalize_line_direction(start_point, end_point)

        is_negative_face = False
        normal = normalize_vector(face_normal)
        if normal:
            if is_opposite_face:
                is_negative_face = True
            elif abs(normal.X) > abs(normal.Y) and abs(normal.X) > abs(normal.Z) and normal.X > 0:
                is_negative_face = True

        if is_negative_face:
            start_point, end_point = end_n, start_n
        else:
            start_point, end_point = start_n, end_n


    base_vector = vector_from_points(start_point, end_point)
    return base_vector

def decompose_vector(base_vector: AllplanGeo.Vector3D,
                     rotation_deg: float,
                     face_normal: AllplanGeo.Vector3D = None,
                     is_opposite_face: bool = False) -> tuple[AllplanGeo.Vector3D, AllplanGeo.Vector3D, AllplanGeo.Vector3D]:
    x_dir = normalize_vector(base_vector)

    if face_normal:
        normal = normalize_vector(face_normal)

        if normal:
            z_dir = vector_scale(normal, -1.0)
            z_dir = normalize_vector(z_dir)

            y_dir = vector_cross(z_dir, x_dir)
            if y_dir.GetLength() < 1e-6:
                reference_up = AllplanGeo.Vector3D(0.0, 0.0, 1.0)
                y_dir = vector_cross(reference_up, x_dir)
                if y_dir.GetLength() < 1e-6:
                    reference_up = AllplanGeo.Vector3D(0.0, 1.0, 0.0)
                    y_dir = vector_cross(reference_up, x_dir)
            y_dir = normalize_vector(y_dir)

            z_dir_before = z_dir
            z_dir = normalize_vector(vector_cross(x_dir, y_dir))

            dot_product = vector_dot(z_dir_before, z_dir)

            if dot_product < 0.5:
                z_dir = z_dir_before
    else:
        reference_up = AllplanGeo.Vector3D(0.0, 0.0, 1.0)
        y_dir = vector_cross(reference_up, x_dir)
        if y_dir.GetLength() < 1e-6:
            reference_up = AllplanGeo.Vector3D(0.0, 1.0, 0.0)
            y_dir = vector_cross(reference_up, x_dir)
        y_dir = normalize_vector(y_dir)
        z_dir = normalize_vector(vector_cross(x_dir, y_dir))

    if abs(rotation_deg) > 1e-6:
        if not face_normal or not is_opposite_face:
            rotation_rad = math.radians(rotation_deg)
            y_dir = rotate_vector_around_axis(y_dir, x_dir, rotation_rad)
            z_dir = rotate_vector_around_axis(z_dir, x_dir, rotation_rad)
            y_dir = normalize_vector(y_dir)
            if face_normal:
                z_dir = normalize_vector(vector_cross(x_dir, y_dir))
            else:
                z_dir = normalize_vector(z_dir)
    if face_normal and y_dir.Z < 0:
        y_dir = vector_scale(y_dir, -1.0)
        z_dir = normalize_vector(vector_cross(x_dir, y_dir))

    return x_dir, y_dir, z_dir


def create_handles(build_ele: BuildingElement,
                   line: AllplanGeo.Line3D,
                   face_normal: AllplanGeo.Vector3D | None = None,
                   face_point: AllplanGeo.Point3D | None = None) -> list[HandleProperties]:
    """Crea los handles para manipular los puntos de la línea de angulares"""
    handle_list = []

    punto_inicial = line.StartPoint
    punto_final = line.EndPoint

    line_direction_vec = AllplanGeo.Vector3D(
        punto_final.X - punto_inicial.X,
        punto_final.Y - punto_inicial.Y,
        punto_final.Z - punto_inicial.Z
    )
    line_direction = normalize_vector(line_direction_vec) or AllplanGeo.Vector3D(1.0, 0.0, 0.0)

    if face_normal:
        normal = normalize_vector(face_normal)
        if normal:
            line_midpoint = AllplanGeo.Point3D(
                (punto_inicial.X + punto_final.X) / 2.0,
                (punto_inicial.Y + punto_final.Y) / 2.0,
                (punto_inicial.Z + punto_final.Z) / 2.0
            )
            plane_origin = line_midpoint
            plane = AllplanGeo.Plane3D(plane_origin, normal)

            handle_list.append(
                HandleProperties(
                    "PuntoInicialHandle",
                    punto_inicial,
                    punto_inicial,
                    [HandleParameterData("PuntoInicial", HandleParameterType.POINT)],
                    HandleDirection.XYZ_DIR,
                    plane=plane,
                    info_text="Punto inicial de la línea"
                )
            )

            handle_list.append(
                HandleProperties(
                    "PuntoFinalHandle",
                    punto_final,
                    punto_inicial,
                    [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                    HandleDirection.XYZ_DIR,
                    plane=plane,
                    info_text="Punto final de la línea"
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
                    info_text="Punto inicial de la línea"
                )
            )

            handle_list.append(
                HandleProperties(
                "PuntoFinalHandle",
                punto_final,
                punto_inicial,
                [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                HandleDirection.XYZ_DIR,
                info_text="Punto final de la línea"
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
                info_text="Punto inicial de la línea"
            )
        )

        handle_list.append(
            HandleProperties(
                "PuntoFinalHandle",
                punto_final,
                punto_inicial,
                [HandleParameterData("PuntoFinal", HandleParameterType.POINT)],
                HandleDirection.XYZ_DIR,
                info_text="Punto final de la línea"
            )
        )

    return handle_list

SELECTING_WALL = 0
SELECTING_LINE = 1
STOPPED = 2
CANCEL = 3
SELECTING_FACE = 4
SELECTING_POSITION = 5

def check_allplan_version(_build_ele: BuildingElement, _version: float) -> bool:
    return True

_ACTIVE_ANGULAR_SCRIPT_OBJECT = None

def create_script_object(build_ele: BuildingElement, script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    global _ACTIVE_ANGULAR_SCRIPT_OBJECT
    _ACTIVE_ANGULAR_SCRIPT_OBJECT = AngularLineScript(build_ele, script_object_data)
    return _ACTIVE_ANGULAR_SCRIPT_OBJECT

def set_active_palette_page_index(page_index: int) -> None:
    """Reenvía el cambio de pestaña del módulo al ScriptObject activo."""
    if _ACTIVE_ANGULAR_SCRIPT_OBJECT is not None:
        _ACTIVE_ANGULAR_SCRIPT_OBJECT.set_active_palette_page_index(page_index)

class WallSelectResult:
    """Resultado de la selección de un muro completo"""
    def __init__(self):
        self.element = None
        self.element_guid = None
        self.is_selected = False

class WallSelectInteractor(BaseScriptObjectInteractor):
    """Interactor para seleccionar un muro completo (sin necesidad de seleccionar cara)"""

    def __init__(self, result: WallSelectResult, prompt_msg: str = "Seleccione el muro"):
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
        if not self.coord_input:
            return True

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
        selected_element = self.coord_input.GetSelectedElement()

        if selected_element.IsNull():
            return True

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        self.result.element = selected_element
        self.result.element_guid = str(selected_element.GetModelElementUUID())
        self.result.is_selected = True

        return False

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT

    def on_mouse_leave(self):
        pass

class AngularLineScript(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)

        self.build_ele = build_ele
        self.state: int | None = None

        self.build_ele.TipoAngular.value = self.build_ele.TipoAngular.value.replace("'", "")
        for tipo_param_name in (
            "TipoAngular_200_460",
            "TipoAngular_200_310",
            "TipoAngular_200_150",
            "TipoAngular_250_460",
            "TipoAngular_250_310",
            "TipoAngular_250_150",
            "TipoAngular_Tensor",
            "TipoAngular_200_460_Grupal",
            "TipoAngular_200_310_Grupal",
            "TipoAngular_200_150_Grupal",
            "TipoAngular_250_460_Grupal",
            "TipoAngular_250_310_Grupal",
            "TipoAngular_250_150_Grupal",
            "TipoAngular_Tensor_Grupal",
        ):
            if hasattr(self.build_ele, tipo_param_name):
                getattr(self.build_ele, tipo_param_name).selected_value = self.build_ele.TipoAngular.value

        self.preview_active = False
        self.script_object_interactor: BaseScriptObjectInteractor | None = None
        self.last_geometries: list[AllplanGeo.BRep3D] = []
        self.last_definition_key: str | None = None

        self.face_select_result = SolidFaceSelectResult()
        self.wall_select_result = WallSelectResult()
        self.line_result = LineInteractorResult()
        self.position_result = PointInteractorResult()

        self.detected_wall = None
        self.detected_wall_guid = None
        # self.wall_allplan_id = None
        self.face_point = None
        self.face_normal = None
        self.face_polygon = None
        self.face_local_system = None
        self._z_unique_from_group = 0  # Se rellena desde script_object_data.param_list en __init__ para usar en EDIT

        # EDIT: precargar desde param_list. CREATE: resetear paleta a valores por defecto (no precargar creación anterior).
        self._restored_from_saved_state = False
        if getattr(self, "is_modification_mode", False):
            if hasattr(self, "script_object_data") and script_object_data:
                param_list_src = getattr(script_object_data, "param_list", None)
                if param_list_src:
                    self._apply_param_list_to_build_ele(param_list_src)
                    _params = parse_params_list_to_dict(param_list_src)
                    self._z_unique_from_group = _params.get("z_unique", 0)
                    try:
                        self._z_unique_from_group = float(self._z_unique_from_group) if self._z_unique_from_group else 0
                    except (TypeError, ValueError):
                        self._z_unique_from_group = 0
        else:
            self._z_unique_from_group = 0
            # self._reset_build_ele_for_create()

        self.is_editing_existing = self._check_if_editing_existing()
        self.is_free_mode = self._get_free_mode()
        self.needs_auto_update = self._should_update_position()
        self.position_updated_in_start_input = False
        self.is_opposite_face_detected = False

        if self.is_modification_mode:
            self._load_existing_points()

    def _get_free_mode(self) -> bool:
        """Obtiene el estado del modo libre desde las propiedades"""
        if hasattr(self.build_ele, 'angular_libre'):
            val = self.build_ele.angular_libre.value
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ('true', '1', 'yes')
            return bool(val)
        return False

    def _get_distribution_type(self) -> str:
        """Obtiene el tipo de distribución seleccionado en la paleta."""
        if hasattr(self.build_ele, "TipoDistribucion"):
            return normalize_distribution_type(getattr(self.build_ele.TipoDistribucion, "value", "Individual"))
        return DISTRIBUTION_INDIVIDUAL

    def _is_individual_distribution(self) -> bool:
        """Devuelve True si el flujo debe posicionar una sola pieza por punto."""
        return self._get_distribution_type() == DISTRIBUTION_INDIVIDUAL

    def _get_angle_degrees(self, param_name: str, default: float = 0.0) -> float:
        """Lee un parámetro Angle de la paleta en grados."""
        if not hasattr(self.build_ele, param_name):
            return default

        value = getattr(getattr(self.build_ele, param_name), "value", default)
        try:
            return value.GetDeg() if hasattr(value, "GetDeg") else float(value)
        except (TypeError, ValueError):
            return default

    def _get_individual_axis_rotations(self) -> tuple[float, float]:
        """Obtiene los giros adicionales disponibles solo en distribución individual."""
        if not self._is_individual_distribution():
            return 0.0, 0.0

        return (
            self._get_angle_degrees("RotacionEjeX"),
            self._get_angle_degrees("RotacionEjeY"),
        )

    def _is_manual_z_enabled(self) -> bool:
        if not hasattr(self.build_ele, "UsarValorZManual"):
            return False

        value = getattr(self.build_ele.UsarValorZManual, "value", False)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)

    def _set_individual_z_value(self, z_value: float) -> None:
        if hasattr(self.build_ele, "ValorZIndividual"):
            self.build_ele.ValorZIndividual.value = float(z_value)

    def _get_individual_z_value(self, fallback: float = 0.0) -> float:
        if not hasattr(self.build_ele, "ValorZIndividual"):
            return fallback

        try:
            return float(self.build_ele.ValorZIndividual.value)
        except (TypeError, ValueError):
            return fallback

    def _resolve_individual_z_from_point(self, point: AllplanGeo.Point3D, update_from_point: bool) -> float:
        if update_from_point and not self._is_manual_z_enabled():
            self._set_individual_z_value(point.Z)
            return float(point.Z)

        return self._get_individual_z_value(point.Z)

    def _get_verticalized_face_normal(self) -> AllplanGeo.Vector3D | None:
        if not self.face_normal:
            return None

        normal_xy = AllplanGeo.Vector3D(self.face_normal.X, self.face_normal.Y, 0.0)
        normal_xy = normalize_vector(normal_xy)
        if normal_xy and normal_xy.GetLength() > 1e-6:
            return normal_xy

        return normalize_vector(self.face_normal)

    def _project_point_to_individual_vertical_face(self, point: AllplanGeo.Point3D, z_value: float) -> AllplanGeo.Point3D:
        if not (self.face_point and self.face_normal):
            return AllplanGeo.Point3D(point.X, point.Y, z_value)

        normal = self._get_verticalized_face_normal()
        if not normal or normal.GetLength() < 1e-6:
            return AllplanGeo.Point3D(point.X, point.Y, z_value)

        delta = AllplanGeo.Vector3D(point.X - self.face_point.X, point.Y - self.face_point.Y, 0.0)
        distance = vector_dot(delta, normal)
        return AllplanGeo.Point3D(
            point.X - normal.X * distance,
            point.Y - normal.Y * distance,
            z_value
        )

    def _project_line_to_individual_vertical_face(self, line: AllplanGeo.Line3D, z_value: float = None) -> AllplanGeo.Line3D:
        if z_value is None:
            z_value = self._get_individual_z_value((line.StartPoint.Z + line.EndPoint.Z) / 2.0)

        start = self._project_point_to_individual_vertical_face(line.StartPoint, z_value)
        end = self._project_point_to_individual_vertical_face(line.EndPoint, z_value)
        return AllplanGeo.Line3D(start, end)

    def _create_geometries_for_distribution(
        self,
        *,
        distribution_type: str,
        definition: dict,
        start_point: AllplanGeo.Point3D,
        end_point: AllplanGeo.Point3D,
        invert_side: bool,
        rotation_deg: float,
        gap: float,
    ) -> tuple[list[AllplanGeo.BRep3D], list[AllplanGeo.Line3D]]:
        distribution_type = normalize_distribution_type(distribution_type)
        print(f"[DISTRIBUTION] Tipo seleccionado: {distribution_type}")

        if distribution_type == DISTRIBUTION_INDIVIDUAL:
            print("[DISTRIBUTION][INDIVIDUAL] Entrando al flujo individual")
            rotation_x_deg, rotation_y_deg = self._get_individual_axis_rotations()
            placement_center = AllplanGeo.Point3D(
                (start_point.X + end_point.X) / 2.0,
                (start_point.Y + end_point.Y) / 2.0,
                (start_point.Z + end_point.Z) / 2.0
            )
            placement_dir = normalize_vector(vector_from_points(start_point, end_point))
            if placement_dir and placement_dir.GetLength() > 1e-6:
                start_point = placement_center
                end_point = move_point(placement_center, placement_dir, definition.get("piece_length", definition.get("length", 0.0)))
            else:
                piece_length = definition.get("piece_length", definition.get("length", 0.0))
                x_dir = self._get_individual_horizontal_axis_on_face()
                if piece_length > 0 and x_dir and x_dir.GetLength() > 1e-6:
                    start_point = move_point(placement_center, x_dir, -piece_length / 2.0)
                    end_point = move_point(placement_center, x_dir, piece_length / 2.0)

            face_normal_for_creation = None if self.is_free_mode else self.face_normal
            if face_normal_for_creation:
                verticalized_normal = self._get_verticalized_face_normal()
                if verticalized_normal:
                    face_normal_for_creation = verticalized_normal
                face_normal_for_creation = vector_scale(face_normal_for_creation, -1.0)
                print("[DISTRIBUTION][INDIVIDUAL] Normal invertida para apoyar la cara perforada contra el muro")

            rotation_for_creation = rotation_deg + rotation_x_deg - 90.0
            print(f"[DISTRIBUTION][INDIVIDUAL] Rotacion compensada para cara perforada paralela al muro: {rotation_for_creation} (x={rotation_x_deg}, y={rotation_y_deg})")

            geometries, edges = create_single_angular_on_line(
                definition=definition,
                start_point=start_point,
                end_point=end_point,
                invert_side=invert_side,
                rotation_deg=rotation_for_creation,
                rotation_y_deg=rotation_y_deg,
                face_normal=face_normal_for_creation,
                face_point=None if self.is_free_mode else self.face_point,
                is_opposite_face=False,
                is_free_mode=self.is_free_mode,
            )
            print(f"[DISTRIBUTION][INDIVIDUAL] Geometrias generadas: {len(geometries) if geometries else 0}")
            return geometries, edges

        print("[DISTRIBUTION][GRUPAL] Entrando al flujo grupal actual")
        geometries, edges = create_angulars_on_line(
            definition=definition,
            start_point=start_point,
            end_point=end_point,
            invert_side=invert_side,
            rotation_deg=rotation_deg,
            gap=gap,
            face_normal=None,
            face_point=None,
            face_polygon=None,
            wall_element=None,
            is_opposite_face=False,
            is_free_mode=True,
        )
        print(f"[DISTRIBUTION][GRUPAL] Geometrias generadas: {len(geometries) if geometries else 0}")
        return geometries, edges

    def _reset_build_ele_for_create(self) -> None:
        """Reset SOLO para CREATE. Nunca se llama en EDIT."""
        be = self.build_ele

        # NO tocar z_unique
        # NO tocar pmp_pare (se calcula en CREATE)

        if hasattr(be, "SavedState"):
            be.SavedState.value = ""

        if hasattr(be, "PuntoInicial"):
            be.PuntoInicial.value = None
        if hasattr(be, "PuntoFinal"):
            be.PuntoFinal.value = None

        if hasattr(be, "SeparacionAngulares"):
            be.SeparacionAngulares.value = 10.0

        if hasattr(be, "TipoDistribucion"):
            be.TipoDistribucion.value = "Individual"

        if hasattr(be, "InvertirAngular"):
            be.InvertirAngular.value = False

        if hasattr(be, "RotacionManual"):
            be.RotacionManual.value = 0.0

        if hasattr(be, "RotacionEjeX"):
            be.RotacionEjeX.value = 0.0

        if hasattr(be, "RotacionEjeY"):
            be.RotacionEjeY.value = 0.0

        if hasattr(be, "UsarValorZManual"):
            be.UsarValorZManual.value = False

        if hasattr(be, "ValorZIndividual"):
            be.ValorZIndividual.value = 0.0

        if hasattr(be, "SiLlevaNeopreno"):
            be.SiLlevaNeopreno.value = False

        if hasattr(be, "angular_libre"):
            be.angular_libre.value = True

    def _serialize_state_to_json(self) -> str:
        """
        Serializa el estado actual de build_ele a JSON para guardar en SavedState.
        Esquema v1 mínimo: p0, p1, tipo, sep, invert, rot, libre, lleva_neopreno, grosor_neopreno, pmp_pare, v.
        """
        try:
            p0 = getattr(self.build_ele.PuntoInicial, "value", None) if hasattr(self.build_ele, "PuntoInicial") else None
            p1 = getattr(self.build_ele.PuntoFinal, "value", None) if hasattr(self.build_ele, "PuntoFinal") else None
            if p0 is None or p1 is None:
                return ""

            rot_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else 0.0
            rot_deg = rot_val.GetDeg() if hasattr(rot_val, "GetDeg") else float(rot_val) if rot_val is not None else 0.0
            rot_x_deg, rot_y_deg = self._get_individual_axis_rotations()

            libre_val = getattr(self, "is_free_mode", False)
            if hasattr(self.build_ele, "angular_libre") and hasattr(self.build_ele.angular_libre, "value"):
                v = self.build_ele.angular_libre.value
                libre_val = v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes")

            state = {
                "v": 1,
                "p0": [p0.X, p0.Y, p0.Z],
                "p1": [p1.X, p1.Y, p1.Z],
                "tipo": str(getattr(self.build_ele.TipoAngular, "value", "") or "") if hasattr(self.build_ele, "TipoAngular") else "",
                "distribucion": self._get_distribution_type(),
                "sep": float(getattr(self.build_ele.SeparacionAngulares, "value", 10.0) or 10.0) if hasattr(self.build_ele, "SeparacionAngulares") else 10.0,
                "invert": bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else False,
                "rot": float(rot_deg),
                "rot_x": float(rot_x_deg),
                "rot_y": float(rot_y_deg),
                "usar_z_manual": self._is_manual_z_enabled(),
                "valor_z_individual": float(getattr(self.build_ele.ValorZIndividual, "value", 0.0) or 0.0) if hasattr(self.build_ele, "ValorZIndividual") else 0.0,
                "libre": bool(libre_val),
                "lleva_neopreno": bool(getattr(self.build_ele.SiLlevaNeopreno, "value", False)) if hasattr(self.build_ele, "SiLlevaNeopreno") else False,
                "pmp_pare": str(getattr(self.build_ele.pmp_pare, "value", "") or "") if hasattr(self.build_ele, "pmp_pare") else "",
            }
            return json.dumps(state, separators=(",", ":"))
        except Exception as e:
            print(f"[SO] Error serializando SavedState: {e}")
            return ""

    def _deserialize_state_from_json(self, json_str: str) -> bool:
        """
        Toma JSON de SavedState y carga build_ele.
        """
        if not json_str or not str(json_str).strip():
            return False
        try:
            state = json.loads(json_str)
            p0 = state.get("p0")
            p1 = state.get("p1")
            if not p0 or not p1 or len(p0) != 3 or len(p1) != 3:
                return False

            if hasattr(self.build_ele, "PuntoInicial"):
                self.build_ele.PuntoInicial.value = AllplanGeo.Point3D(float(p0[0]), float(p0[1]), float(p0[2]))
            if hasattr(self.build_ele, "PuntoFinal"):
                self.build_ele.PuntoFinal.value = AllplanGeo.Point3D(float(p1[0]), float(p1[1]), float(p1[2]))

            tipo = state.get("tipo") or state.get("TipoAngular")
            if hasattr(self.build_ele, "TipoAngular"):
                # Clave exacta del combo (ej. ANG200_L460, TENSOR)
                tipo_key = str(tipo or getattr(self.build_ele.TipoAngular, "value", "") or "").strip()
                self.build_ele.TipoAngular.value = tipo_key
            distribucion = state.get("distribucion") or state.get("TipoDistribucion") or DISTRIBUTION_INDIVIDUAL
            if hasattr(self.build_ele, "TipoDistribucion"):
                self.build_ele.TipoDistribucion.value = "Individual" if normalize_distribution_type(distribucion) == DISTRIBUTION_INDIVIDUAL else "Grupal"
            sep = state.get("sep") if state.get("sep") is not None else state.get("SeparacionAngulares")
            if hasattr(self.build_ele, "SeparacionAngulares"):
                try:
                    self.build_ele.SeparacionAngulares.value = float(sep if sep is not None else getattr(self.build_ele.SeparacionAngulares, "value", 10.0))
                except (TypeError, ValueError):
                    pass
            invert = state.get("invert") if "invert" in state else state.get("invertido")
            if hasattr(self.build_ele, "InvertirAngular"):
                self.build_ele.InvertirAngular.value = bool(invert if invert is not None else getattr(self.build_ele.InvertirAngular, "value", False))
            libre = state.get("libre") if "libre" in state else state.get("Libre")
            if hasattr(self.build_ele, "angular_libre"):
                self.build_ele.angular_libre.value = bool(libre if libre is not None else getattr(self.build_ele.angular_libre, "value", False))

            rot_deg = float(state.get("rot", 0.0))
            if hasattr(self.build_ele, "RotacionManual"):
                try:
                    self.build_ele.RotacionManual.value = float(state["rot"])
                except Exception:
                    self.build_ele.RotacionManual.value = rot_deg

            if hasattr(self.build_ele, "RotacionEjeX"):
                self.build_ele.RotacionEjeX.value = float(state.get("rot_x", state.get("RotacionEjeX", 0.0)) or 0.0)

            if hasattr(self.build_ele, "RotacionEjeY"):
                self.build_ele.RotacionEjeY.value = float(state.get("rot_y", state.get("RotacionEjeY", 0.0)) or 0.0)

            if hasattr(self.build_ele, "UsarValorZManual"):
                self.build_ele.UsarValorZManual.value = bool(state.get("usar_z_manual", state.get("UsarValorZManual", False)))

            if hasattr(self.build_ele, "ValorZIndividual"):
                valor_z = state.get("valor_z_individual") if "valor_z_individual" in state else state.get("ValorZIndividual")
                if valor_z is not None:
                    self.build_ele.ValorZIndividual.value = float(valor_z)

            if hasattr(self.build_ele, "SiLlevaNeopreno"):
                lleva_val = state.get("lleva_neopreno") if "lleva_neopreno" in state else state.get("SiLlevaNeopreno", False)
                self.build_ele.SiLlevaNeopreno.value = bool(lleva_val)

            if hasattr(self.build_ele, "pmp_pare"):
                self.build_ele.pmp_pare.value = str(state.get("pmp_pare", "")).replace("'", "")

            self._restored_state = state
            print("[SO] ✓ SavedState restaurado desde JSON")
            return True
        except Exception as e:
            print(f"[SO] Error deserializando SavedState: {e}")
            return False

    def _apply_param_list_to_build_ele(self, param_list_src: list) -> None:
        """
        Aplica los parámetros del param_list del grupo a build_ele para precargar
        el diálogo al editar (SiLlevaNeopreno, GrosorNeopreno, PuntoInicial, etc.).
        """
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
                    if key in ("RotacionManual", "RotacionEjeX", "RotacionEjeY"):
                        rot_deg = float(value) if value is not None else 0.0
                        attr.value = rot_deg
                    elif key in ("PuntoInicial", "PuntoFinal") and isinstance(value, AllplanGeo.Point3D):
                        attr.value = value
                    else:
                        attr.value = value
                except Exception as e:
                    print(f"[SO] No se pudo aplicar param_list[{key}]: {e}")
            # LongitudLinea = distancia entre PuntoInicial y PuntoFinal (calculado, no persistido)
            if hasattr(self.build_ele, "LongitudLinea") and hasattr(self.build_ele, "PuntoInicial") and hasattr(self.build_ele, "PuntoFinal"):
                try:
                    p0 = getattr(self.build_ele.PuntoInicial, "value", None)
                    p1 = getattr(self.build_ele.PuntoFinal, "value", None)
                    if p0 is not None and p1 is not None:
                        self.build_ele.LongitudLinea.value = vector_from_points(p0, p1).GetLength()
                except Exception:
                    pass
        except Exception as e:
            print(f"[SO] Error aplicando param_list a build_ele: {e}")

    def _restore_saved_state(self) -> bool:
        """
        Restaura el estado guardado desde build_ele o desde el PythonPartGroup si existe.
        Se llama en __init__ cuando se edita una instancia existente.
        Intenta SavedState, PolylineState, StateData en build_ele; luego PythonPartService si está en modo modificación.
        """
        try:
            # Primero intentar desde build_ele (parámetros normales)
            param_names = ['SavedState', 'PolylineState', 'StateData']
            for param_name in param_names:
                try:
                    if hasattr(self.build_ele, param_name):
                        param = getattr(self.build_ele, param_name)
                        if hasattr(param, 'value'):
                            state_json = param.value
                            if state_json and isinstance(state_json, str) and state_json.strip():
                                if self._deserialize_state_from_json(state_json):
                                    print(f"[SO] ✓ Estado previo restaurado desde build_ele.{param_name}")
                                    return True
                except Exception as e:
                    print(f"[SO] No se pudo leer parámetro {param_name} desde build_ele: {e}")
                    continue

            # Si no se encontró en build_ele y estamos en modo modificación,
            # intentar leer desde el PythonPartGroup usando PythonPartService
            try:
                if getattr(self, 'is_modification_mode', False) and hasattr(self, 'modification_ele_list'):
                    python_part_adapter = self.modification_ele_list.get_base_element_adapter(self.document)
                    if not python_part_adapter.IsNull():
                        success, name, parameter = AllplanBaseElements.PythonPartService.GetParameter(python_part_adapter)
                        if success and parameter:
                            if isinstance(parameter, str):
                                param_lines = parameter.split('\n')
                            elif isinstance(parameter, (list, tuple)):
                                param_lines = parameter
                            else:
                                param_lines = []
                            for line in param_lines:
                                if isinstance(line, str):
                                    line = line.strip()
                                    if line.startswith('SavedState'):
                                        if '=' in line:
                                            state_json = line.split('=', 1)[1].strip()
                                            if state_json:
                                                print(f"[SO] Encontrado SavedState en PythonPartGroup: {len(state_json)} caracteres")
                                                if self._deserialize_state_from_json(state_json):
                                                    print("[SO] ✓ Estado previo restaurado desde PythonPartGroup.SavedState")
                                                    return True
            except Exception as e:
                print(f"[SO] Error intentando leer estado desde PythonPartGroup: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"[SO] Error restaurando estado: {e}")
            import traceback
            traceback.print_exc()
        return False

    def _save_state_to_build_ele(self):
        """Guardar SavedState al final (CREATE y EDIT). Llamar siempre en ambos modos."""
        ss = self._serialize_state_to_json()
        if ss and hasattr(self.build_ele, "SavedState") and hasattr(self.build_ele.SavedState, "value"):
            self.build_ele.SavedState.value = ss
            print(f"[SO] ✓ SavedState guardado ({len(ss)} chars)")

    def _sync_line_to_build_ele(self) -> None:
        """
        Sincroniza line_result.input_line → build_ele.PuntoInicial / PuntoFinal.
        Recalcula LongitudLinea para que la paleta muestre la longitud al mover inicio/fin.
        Llamar en cuanto se confirma la línea (LineInteractor / selección) o se mueve un handle.
        """
        if not getattr(self, "line_result", None) or not self.line_result.input_line:
            return
        line = self.line_result.input_line
        start_pt = getattr(line, "StartPoint", None)
        end_pt = getattr(line, "EndPoint", None)
        if start_pt is None or end_pt is None:
            return
        if hasattr(self.build_ele, "PuntoInicial") and hasattr(self.build_ele.PuntoInicial, "value"):
            self.build_ele.PuntoInicial.value = start_pt
        if hasattr(self.build_ele, "PuntoFinal") and hasattr(self.build_ele.PuntoFinal, "value"):
            self.build_ele.PuntoFinal.value = end_pt
        if hasattr(self.build_ele, "LongitudLinea"):
            try:
                self.build_ele.LongitudLinea.value = vector_from_points(start_pt, end_pt).GetLength()
            except Exception:
                pass

    def _build_group_global_params(
        self,
        *,
        z_unique,
        total_elements: int,
        punto_inicial,
        punto_final,
        tipo_angular_key: str,
        distribution_type: str,
        separation: float,
        libre: bool,
        rot_deg: float,
        invertido: bool,
        lleva_neopreno: bool,
        pmp_pare_value: str,
        saved_state_str: str,
    ) -> dict:
        """
        Arma el diccionario completo de global_params para PythonPartGroup.
        Incluye SavedState, SiLlevaNeopreno, GrosorNeopreno (float para RadioButton) y PMP_*.
        Usar en CREATE, EDIT y on_cancel_function para no duplicar lógica y asegurar
        que el grupo siempre se guarde con SavedState (Allplan puede restaurar al editar).
        """
        def_angular = ANGULAR_CATALOG.get(tipo_angular_key) if tipo_angular_key else None
        num_forats = get_num_forats_from_definition(def_angular) if def_angular else 0
        nom = get_nom_from_angular_key(tipo_angular_key) if tipo_angular_key else ""
        neopre = "Si" if lleva_neopreno else "No"
        rot_x_deg, rot_y_deg = self._get_individual_axis_rotations()

        # grosor_float = self._grosor_neopreno_to_float(grosor_neopre_value)
        length_mm_str = f"{float(def_angular['length']):.2f}mm"
        return {
            "z_unique": z_unique,
            "TotalElements": total_elements,
            "PuntoInicial": punto_inicial,
            "PuntoFinal": punto_final,
            "TipoAngular": tipo_angular_key,
            "TipoDistribucion": "Individual" if normalize_distribution_type(distribution_type) == DISTRIBUTION_INDIVIDUAL else "Grupal",
            "UsarValorZManual": self._is_manual_z_enabled(),
            "ValorZIndividual": float(getattr(self.build_ele.ValorZIndividual, "value", 0.0) or 0.0) if hasattr(self.build_ele, "ValorZIndividual") else 0.0,
            "SeparacionAngulares": separation,
            "Libre": libre,
            "RotacionManual": rot_deg,
            "RotacionEjeX": rot_x_deg,
            "RotacionEjeY": rot_y_deg,
            "InvertirAngular": invertido,
            "SiLlevaNeopreno": lleva_neopreno,
            "SavedState": saved_state_str if saved_state_str else "",
            "pmp_pare": pmp_pare_value if pmp_pare_value else "",
            "PMP_FG_ANG_DETALL": "",
            "PMP_FG_ANG_FORATS": num_forats,
            "PMP_FG_ANG_NOM": nom,
            "PMP_FG_ANGULAR_NEOPRE": neopre,
            "PMP_FG_ANG_NEOPRE": length_mm_str
        }

    def _check_if_editing_existing(self) -> bool:
        """Verifica si se está editando un angular existente"""
        # Verificar solo si hay puntos guardados para reconstruir
        if (hasattr(self.build_ele, 'PuntoInicial') and
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

    def _load_existing_points(self):
        """Carga los puntos existentes desde las propiedades del BuildingElement.
        Si ya restauramos desde SavedState, build_ele ya tiene los valores; solo actualizamos line_result."""
        try:
            punto_inicial = getattr(self.build_ele, 'PuntoInicial', None)
            punto_final = getattr(self.build_ele, 'PuntoFinal', None)

            if punto_inicial and punto_final and hasattr(punto_inicial, 'value') and hasattr(punto_final, 'value'):
                if punto_inicial.value and punto_final.value:
                    p1 = punto_inicial.value
                    p2 = punto_final.value
                    is_default = (abs(p1.X) < 1e-6 and abs(p1.Y) < 1e-6 and abs(p1.Z) < 1e-6 and
                                 abs(p2.X - 1000.0) < 1e-6 and abs(p2.Y) < 1e-6 and abs(p2.Z) < 1e-6)
                    # No usar defaults si ya restauramos desde SavedState
                    if not is_default or self._restored_from_saved_state:
                        self.line_result.input_line = AllplanGeo.Line3D(p1, p2)

            muro_guid_prop = getattr(self.build_ele, 'MuroGUID', None)
            muro_connection_prop = getattr(self.build_ele, 'MuroConnection', None)

            if muro_guid_prop and hasattr(muro_guid_prop, 'value'):
                pass

            if muro_connection_prop and hasattr(muro_connection_prop, 'value'):
                conn = muro_connection_prop.value
                if hasattr(conn, 'uuid'):
                    pass
                if hasattr(conn, 'element'):
                    pass

            wall_element = self._get_wall_element()
            if wall_element:
                pass

            if wall_element and (not hasattr(wall_element, 'IsNull') or not wall_element.IsNull()):
                self.detected_wall = wall_element
                real_wall_guid = str(wall_element.GetModelElementUUID())
                self.detected_wall_guid = real_wall_guid
                # self.wall_allplan_id = get_wall_ifc_id(wall_element)
                if hasattr(self.build_ele, 'MuroGUID'):
                    self.build_ele.MuroGUID.value = real_wall_guid

                if hasattr(self.build_ele, 'MuroConnection'):
                    try:
                        conn = self.build_ele.MuroConnection.value
                        if not hasattr(conn, 'element') or not conn.element.IsValid() or \
                           (hasattr(conn, 'uuid') and str(conn.uuid) == "00000000-0000-0000-0000-000000000000"):
                            conn.element = wall_element
                    except Exception as e:
                        try:
                            conn = self.build_ele.MuroConnection.value
                            conn.element = wall_element
                        except Exception as e2:
                            pass

                self._load_face_info_from_properties()
            else:
                pass
        except Exception as e:
            import traceback

    def _load_face_info_from_properties(self):
        """Carga la información de la cara desde las propiedades guardadas"""
        try:
            if not self.detected_wall:
                wall_element = self._get_wall_element()
                if wall_element and (not hasattr(wall_element, 'IsNull') or not wall_element.IsNull()):
                    self.detected_wall = wall_element
                    self.detected_wall_guid = str(wall_element.GetModelElementUUID())
                    # self.wall_allplan_id = get_wall_ifc_id(wall_element)
                    if hasattr(self.build_ele, 'MuroGUID'):
                        self.build_ele.MuroGUID.value = self.detected_wall_guid

                    if hasattr(self.build_ele, 'MuroConnection'):
                        try:
                            conn = self.build_ele.MuroConnection.value
                            if not hasattr(conn, 'element') or not conn.element.IsValid() or \
                               (hasattr(conn, 'uuid') and str(conn.uuid) == "00000000-0000-0000-0000-000000000000"):
                                conn.element = wall_element
                        except Exception:
                            try:
                                conn = self.build_ele.MuroConnection.value
                                conn.element = wall_element
                            except Exception:
                                pass
            else:
                pass

            has_cara_normal = (hasattr(self.build_ele, 'CaraNormalX') and
                hasattr(self.build_ele, 'CaraNormalY') and
                              hasattr(self.build_ele, 'CaraNormalZ'))

            if has_cara_normal:
                self.face_normal = AllplanGeo.Vector3D(
                    self.build_ele.CaraNormalX.value,
                    self.build_ele.CaraNormalY.value,
                    self.build_ele.CaraNormalZ.value
                )
                self.face_normal = normalize_vector(self.face_normal) or self.face_normal
            else:
                pass

            has_punto_clic = (hasattr(self.build_ele, 'PuntoClicX') and
                hasattr(self.build_ele, 'PuntoClicY') and
                             hasattr(self.build_ele, 'PuntoClicZ'))

            if has_punto_clic:
                self.face_point = AllplanGeo.Point3D(
                    self.build_ele.PuntoClicX.value,
                    self.build_ele.PuntoClicY.value,
                    self.build_ele.PuntoClicZ.value
                )
            else:
                pass

            if self.detected_wall and self.face_normal and self.face_point:
                stored_normal = self._get_stored_normal()
                stored_point = self._get_stored_point()

                is_selected, face_polygon, intersect_result = self._find_face_on_wall(
                    self.detected_wall,
                    stored_normal,
                    stored_point
                )

                if face_polygon:
                    self.face_polygon = face_polygon
                    self.face_normal = stored_normal
                    if intersect_result and hasattr(intersect_result, 'IntersectionPoint'):
                        if not self.face_point:
                            self.face_point = intersect_result.IntersectionPoint
                else:
                    pass
            else:
                pass

            if self.face_polygon and self.face_normal:
                stored_normal = AllplanGeo.Vector3D(
                    self.build_ele.CaraNormalX.value,
                    self.build_ele.CaraNormalY.value,
                    self.build_ele.CaraNormalZ.value
                )
                stored_normal = normalize_vector(stored_normal) or stored_normal
                self.face_normal = stored_normal

                self.face_local_system = calculate_local_coordinate_system(
                    self.face_polygon, self.face_normal
                )
                if self.face_local_system:
                    origin = self.face_local_system['origin']
                else:
                    pass
            else:
                pass
        except Exception as e:
            import traceback

    def _should_update_position(self) -> bool:
        """Verifica si debe actualizarse automáticamente la posición"""
        if self.is_free_mode:
            return False

        has_connection = hasattr(self.build_ele, 'MuroConnection')
        has_guid = hasattr(self.build_ele, 'MuroGUID')
        has_uv = (hasattr(self.build_ele, 'PosicionRelativaU') and
                  hasattr(self.build_ele, 'PosicionRelativaV') and
                  self.build_ele.PosicionRelativaU.value is not None and
                  self.build_ele.PosicionRelativaV.value is not None)

        if not has_uv:
            return False

        if has_connection:
            conn = self.build_ele.MuroConnection.value
            return hasattr(conn, 'element') and conn.element.IsValid()

        return has_guid and bool(self.build_ele.MuroGUID.value)

    def _get_wall_element(self):
        """Obtiene el elemento muro desde la conexión o GUID"""
        wall_element = None

        if hasattr(self.build_ele, 'MuroConnection'):
            conn = self.build_ele.MuroConnection.value
            if conn:
                if hasattr(conn, 'element'):
                    if conn.element.IsValid():
                        wall_element = conn.element
        else:
            pass

        if not wall_element or (hasattr(wall_element, 'IsNull') and wall_element.IsNull()):
            if hasattr(self.build_ele, 'MuroGUID'):
                if self.build_ele.MuroGUID.value:
                    try:
                        wall_guid = AllplanEleAdapter.GUID.FromString(self.build_ele.MuroGUID.value)
                        wall_element = AllplanEleAdapter.BaseElementAdapter.FromGUID(
                            wall_guid,
                            self.document
                        )
                        if wall_element:
                            pass
                    except Exception as e:
                        import traceback
                else:
                    pass
            else:
                pass

        return wall_element

    def _get_stored_normal(self):
        """Obtiene la normal almacenada"""
        return AllplanGeo.Vector3D(
            self.build_ele.CaraNormalX.value if hasattr(self.build_ele, 'CaraNormalX') else 0,
            self.build_ele.CaraNormalY.value if hasattr(self.build_ele, 'CaraNormalY') else 0,
            self.build_ele.CaraNormalZ.value if hasattr(self.build_ele, 'CaraNormalZ') else 1
        )

    def _get_stored_point(self):
        """Obtiene el punto almacenado"""
        return AllplanGeo.Point3D(
            self.build_ele.PuntoClicX.value if hasattr(self.build_ele, 'PuntoClicX') else 0,
            self.build_ele.PuntoClicY.value if hasattr(self.build_ele, 'PuntoClicY') else 0,
            self.build_ele.PuntoClicZ.value if hasattr(self.build_ele, 'PuntoClicZ') else 0
        )

    def _find_face_index(self, wall_element, selected_face_polygon, selected_face_normal=None):
        """Encuentra el índice de una cara seleccionada comparándola con todas las caras del muro.

        Args:
            wall_element: Elemento del muro
            selected_face_polygon: Polígono de la cara seleccionada
            selected_face_normal: Normal de la cara seleccionada (CRÍTICO para distinguir caras opuestas)

        Returns:
            face_index (int) o None si no se encuentra
        """
        try:
            wall_geo = wall_element.GetModelGeometry()
            if not wall_geo:
                wall_geo = wall_element.GetGeometry()

            if isinstance(wall_geo, AllplanGeo.BRep3D):
                error, wall_geo = AllplanGeo.CreatePolyhedron(wall_geo)
                if error != AllplanGeo.eGeometryErrorCode.eOK:
                    return None

            if not wall_geo or not isinstance(wall_geo, AllplanGeo.Polyhedron3D):
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

                selected_normal = vector_cross(v1, v2)
                selected_normal = normalize_vector(selected_normal)

            faces_count = wall_geo.GetFacesCount()
            candidates = []

            for i in range(faces_count):
                face = wall_geo.GetFace(i)
                success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(wall_geo, face)

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

                distance = AllplanGeo.CalcLength(
                    AllplanGeo.Vector3D(
                        face_center.X - selected_center.X,
                        face_center.Y - selected_center.Y,
                        face_center.Z - selected_center.Z
                    )
                )

                p0 = face_polygon.GetPoint(0)
                p1 = face_polygon.GetPoint(1)
                p2 = face_polygon.GetPoint(2)

                v1 = AllplanGeo.Vector3D(p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z)
                v2 = AllplanGeo.Vector3D(p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z)

                face_normal = vector_cross(v1, v2)
                face_normal_normalized = normalize_vector(face_normal)

                dot = 0.0
                if selected_normal and face_normal_normalized:
                    dot = abs(vector_dot(face_normal_normalized, selected_normal))

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

    def _get_face_by_index(self, wall_element, face_index):
        """Obtiene una cara específica del muro por su índice.

        Returns:
            (success, face_polygon, face_normal) tuple
        """
        try:
            wall_geo = wall_element.GetModelGeometry()
            if not wall_geo:
                wall_geo = wall_element.GetGeometry()

            if isinstance(wall_geo, AllplanGeo.BRep3D):
                error, wall_geo = AllplanGeo.CreatePolyhedron(wall_geo)
                if error != AllplanGeo.eGeometryErrorCode.eOK:
                    return False, None, None

            if not wall_geo or not isinstance(wall_geo, AllplanGeo.Polyhedron3D):
                return False, None, None

            faces_count = wall_geo.GetFacesCount()
            if face_index < 0 or face_index >= faces_count:
                return False, None, None

            face = wall_geo.GetFace(face_index)
            success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(wall_geo, face)

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

            face_normal = vector_cross(v1, v2)
            face_normal = normalize_vector(face_normal)
            if not face_normal:
                return False, None, None

            return True, face_polygon, face_normal

        except Exception:
            return False, None, None

    def _find_face_on_wall(self, wall_element, stored_normal, stored_point):
        """Encuentra la cara del muro que coincide con la normal guardada"""
        try:
            view_projection = None
            input_document = self.document
            if hasattr(self, 'coord_input') and self.coord_input:
                try:
                    view_projection = self.coord_input.GetViewWorldProjection()
                    input_document = self.coord_input.GetInputViewDocument()
                except Exception:
                    pass

            stored_normal_normalized = normalize_vector(stored_normal)
            if not stored_normal_normalized:
                return False, None, None

            center_2d = AllplanGeo.Point2D(stored_point.X, stored_point.Y)

            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectWallFace(
                    wall_element, center_2d, True,
                    view_projection,
                    input_document, True
                )

            if face_polygon and intersect_result:
                face_normal = intersect_result.FaceNv
                if face_normal:
                    face_normal_norm = normalize_vector(face_normal)
                    if face_normal_norm and stored_normal_normalized:
                        dot = face_normal_norm.DotProduct(stored_normal_normalized)
                        if abs(dot) > 0.7:
                            return True, face_polygon, intersect_result

            is_selected, face_polygon, intersect_result = \
                AllplanBaseElements.FaceSelectService.SelectPolyhedronFace(
                    wall_element, center_2d, True,
                    view_projection,
                    input_document, True
                )

            if face_polygon and intersect_result:
                face_normal = intersect_result.FaceNv
                if face_normal:
                    face_normal_norm = normalize_vector(face_normal)
                    if face_normal_norm and stored_normal_normalized:
                        dot = face_normal_norm.DotProduct(stored_normal_normalized)
                        if abs(dot) > 0.7:
                            return True, face_polygon, intersect_result

            try:
                wall_geo = wall_element.GetModelGeometry()
                if not wall_geo:
                    wall_geo = wall_element.GetGeometry()

                    if isinstance(wall_geo, AllplanGeo.BRep3D):
                        error, polyhedron = AllplanGeo.CreatePolyhedron(wall_geo)
                        if error == AllplanGeo.eGeometryErrorCode.eOK:
                            wall_geo = polyhedron

                    if wall_geo and isinstance(wall_geo, AllplanGeo.Polyhedron3D):
                        candidate_faces = []
                        faces_count = wall_geo.GetFacesCount()

                        for i in range(faces_count):
                            face = wall_geo.GetFace(i)
                            success, _, face_points = AllplanGeo.PolyhedronUtil.GetFacePoints(wall_geo, face)

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

                                face_normal = vector_cross(v1, v2)
                                face_normal = normalize_vector(face_normal)

                                if face_normal:
                                    dot = abs(face_normal.DotProduct(stored_normal_normalized))

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

                                    distance_vec = AllplanGeo.Vector3D(
                                        stored_point.X - face_center.X,
                                        stored_point.Y - face_center.Y,
                                        stored_point.Z - face_center.Z
                                    )
                                    distance_to_stored = AllplanGeo.CalcLength(distance_vec)
                                    MAX_DISTANCE = 1000.0

                                    if distance_to_stored <= MAX_DISTANCE:
                                        candidate_faces.append({
                                            'index': i,
                                            'polygon': face_polygon,
                                            'normal': face_normal,
                                            'center': face_center,
                                            'dot': dot,
                                            'distance': distance_to_stored
                                        })

                    if candidate_faces:
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
                            def __init__(self, normal, point):
                                self.FaceNv = normal
                                self.IntersectionPoint = point

                        intersect_result = FakeIntersectResult(face_normal, face_center)
                        return True, face_polygon, intersect_result
            except Exception:
                pass

            try:
                lateral_faces = get_wall_lateral_faces(wall_element)

                best_match = None
                best_dot = -1.0
                for face_info in lateral_faces:
                    face_normal = face_info.get('normal')
                    face_poly = face_info.get('polygon')
                    if face_normal and face_poly:
                        face_normal_norm = normalize_vector(face_normal)
                        if face_normal_norm:
                            dot = abs(face_normal_norm.DotProduct(stored_normal_normalized))
                            if dot > best_dot and dot > 0.7:
                                best_dot = dot
                                best_match = face_info

                if best_match:
                    class FakeIntersectResult:
                        def __init__(self, normal, point):
                            self.FaceNv = normal
                            self.IntersectionPoint = point

                    fake_result = FakeIntersectResult(
                        best_match['normal'],
                        stored_point
                    )
                    return True, best_match['polygon'], fake_result
            except Exception:
                pass

            return False, None, None
        except Exception:
            return False, None, None

    def _update_angular_position(self):
        """Actualiza la posición del angular cuando el muro se mueve"""
        try:
            wall_element = self._get_wall_element()
            if not wall_element or (hasattr(wall_element, 'IsNull') and wall_element.IsNull()):
                return False
            self.detected_wall = wall_element
            self.detected_wall_guid = str(wall_element.GetModelElementUUID())
            # self.wall_allplan_id = get_wall_ifc_id(wall_element)
            if hasattr(self.build_ele, 'MuroGUID'):
                self.build_ele.MuroGUID.value = self.detected_wall_guid

            if not self.line_result.input_line:
                return False

            has_start_uv = (hasattr(self.build_ele, 'PosicionRelativaU_Inicio') and
                           hasattr(self.build_ele, 'PosicionRelativaV_Inicio') and
                           self.build_ele.PosicionRelativaU_Inicio.value is not None and
                           self.build_ele.PosicionRelativaV_Inicio.value is not None)
            has_end_uv = (hasattr(self.build_ele, 'PosicionRelativaU_Fin') and
                         hasattr(self.build_ele, 'PosicionRelativaV_Fin') and
                         self.build_ele.PosicionRelativaU_Fin.value is not None and
                         self.build_ele.PosicionRelativaV_Fin.value is not None)

            has_center_uv = (hasattr(self.build_ele, 'PosicionRelativaU') and
                            hasattr(self.build_ele, 'PosicionRelativaV') and
                            self.build_ele.PosicionRelativaU.value is not None and
                            self.build_ele.PosicionRelativaV.value is not None)

            if not (has_start_uv and has_end_uv) and not has_center_uv:
                return False

            self.face_normal = None
            self.face_polygon = None
            self.face_point = None

            has_index = (
                hasattr(self.build_ele, 'CaraIndice') and
                self.build_ele.CaraIndice.value is not None and
                self.build_ele.CaraIndice.value >= 0
            )

            if has_index:
                stored_face_index = self.build_ele.CaraIndice.value
                is_selected, face_polygon, face_normal = self._get_face_by_index(
                    wall_element,
                    stored_face_index
                )

                if is_selected and face_polygon:
                    stored_normal = self._get_stored_normal()
                    stored_normal_norm = normalize_vector(stored_normal)
                    face_normal_norm = normalize_vector(face_normal)

                    if stored_normal_norm and face_normal_norm:
                        if stored_normal_norm.DotProduct(face_normal_norm) < 0:
                            face_normal = AllplanGeo.Vector3D(
                                -face_normal.X,
                                -face_normal.Y,
                                -face_normal.Z
                            )

                    self.face_normal = face_normal
                    self.face_polygon = face_polygon

                    result = AllplanGeo.CalcMinMax(face_polygon)
                    minmax = result[0] if isinstance(result, tuple) else result
                    self.face_point = AllplanGeo.Point3D(
                        (minmax.Min.X + minmax.Max.X) / 2.0,
                        (minmax.Min.Y + minmax.Max.Y) / 2.0,
                        (minmax.Min.Z + minmax.Max.Z) / 2.0
                    )

            if not self.face_polygon:
                stored_normal = self._get_stored_normal()
                stored_point = self._get_stored_point()

                is_selected, face_polygon, intersect_result = self._find_face_on_wall(
                    wall_element,
                    stored_normal,
                    stored_point
                )

                if is_selected and face_polygon:
                    self.face_normal = intersect_result.FaceNv if intersect_result else stored_normal
                    self.face_point = intersect_result.IntersectionPoint if intersect_result else stored_point
                    self.face_polygon = face_polygon

                    face_index = self._find_face_index(wall_element, face_polygon, self.face_normal)
                    if face_index is not None and hasattr(self.build_ele, 'CaraIndice'):
                        self.build_ele.CaraIndice.value = face_index

            if not self.face_polygon:
                return False

            stored_normal = self._get_stored_normal()
            found_normal = self.face_normal if self.face_normal else stored_normal
            found_normal_norm = normalize_vector(found_normal) if found_normal else None
            stored_normal_norm = normalize_vector(stored_normal) if stored_normal else None

            original_face_polygon = self.face_polygon
            original_face_normal = found_normal if found_normal else stored_normal

            is_opposite_face = False
            if found_normal_norm and stored_normal_norm:
                dot_product = found_normal_norm.DotProduct(stored_normal_norm)
                if dot_product < -0.5:
                    is_opposite_face = True
                    self.is_opposite_face_detected = True
                    opposite_polygon, opposite_normal, opposite_point = find_opposite_face_info(
                        wall_element, stored_normal
                    )
                    if opposite_polygon and opposite_normal and opposite_point:
                        self.face_normal = opposite_normal
                        self.face_point = opposite_point

                        if hasattr(self.build_ele, 'CaraNormalX'):
                            self.build_ele.CaraNormalX.value = opposite_normal.X
                        if hasattr(self.build_ele, 'CaraNormalY'):
                            self.build_ele.CaraNormalY.value = opposite_normal.Y
                        if hasattr(self.build_ele, 'CaraNormalZ'):
                            self.build_ele.CaraNormalZ.value = opposite_normal.Z
                    else:
                        self.is_opposite_face_detected = True
                        self.face_polygon = self.face_polygon if self.face_polygon else self.face_polygon
                        inverted_normal = AllplanGeo.Vector3D(
                            -found_normal_norm.X,
                            -found_normal_norm.Y,
                            -found_normal_norm.Z
                        )
                        self.face_normal = inverted_normal

                        if hasattr(self.build_ele, 'CaraNormalX'):
                            self.build_ele.CaraNormalX.value = inverted_normal.X
                        if hasattr(self.build_ele, 'CaraNormalY'):
                            self.build_ele.CaraNormalY.value = inverted_normal.Y
                        if hasattr(self.build_ele, 'CaraNormalZ'):
                            self.build_ele.CaraNormalZ.value = inverted_normal.Z
                else:
                    self.is_opposite_face_detected = False
                    if not self.face_normal:
                        self.face_normal = stored_normal
                    if not self.face_point:
                        self.face_point = stored_point
                    if not self.face_polygon:
                        self.face_polygon = self.face_polygon
            else:
                if not self.face_normal:
                    self.face_normal = stored_normal
                if not self.face_point:
                    self.face_point = stored_point
                if not self.face_polygon:
                    self.face_polygon = face_polygon

            polygon_for_local_system = original_face_polygon if is_opposite_face else self.face_polygon
            normal_for_local_system = (
                original_face_normal if is_opposite_face
                else (self.face_normal if self.face_normal else stored_normal)
            )

            has_stored_axes = (
                hasattr(self.build_ele, 'AxisU_X') and
                hasattr(self.build_ele, 'AxisV_X')
            )

            if has_stored_axes:
                axis_u_final = AllplanGeo.Vector3D(
                    self.build_ele.AxisU_X.value,
                    self.build_ele.AxisU_Y.value,
                    self.build_ele.AxisU_Z.value
                )
                axis_v_final = AllplanGeo.Vector3D(
                    self.build_ele.AxisV_X.value,
                    self.build_ele.AxisV_Y.value,
                    self.build_ele.AxisV_Z.value
                )

                result = AllplanGeo.CalcMinMax(polygon_for_local_system)
                minmax = result[0] if isinstance(result, tuple) else result
                origin = AllplanGeo.Point3D(
                    (minmax.Min.X + minmax.Max.X) / 2.0,
                    (minmax.Min.Y + minmax.Max.Y) / 2.0,
                    (minmax.Min.Z + minmax.Max.Z) / 2.0
                )

                vertices = [polygon_for_local_system.GetPoint(i) for i in range(polygon_for_local_system.Count())]
                u_coords = []
                v_coords = []

                for vertex in vertices:
                    vec_from_origin = AllplanGeo.Vector3D(
                        vertex.X - origin.X,
                        vertex.Y - origin.Y,
                        vertex.Z - origin.Z
                    )
                    u_coords.append(vec_from_origin.DotProduct(axis_u_final))
                    v_coords.append(vec_from_origin.DotProduct(axis_v_final))

                width = max(u_coords) - min(u_coords)
                height = max(v_coords) - min(v_coords)

                local_system = {
                    'origin': origin,
                    'axis_u': axis_u_final,
                    'axis_v': axis_v_final,
                    'axis_w': normal_for_local_system,
                    'width': width,
                    'height': height
                }
            else:
                local_system = calculate_local_coordinate_system(polygon_for_local_system, normal_for_local_system)
                if not local_system:
                    return False

            if is_opposite_face:
                opposite_polygon, opposite_normal, opposite_point = find_opposite_face_info(
                    wall_element, stored_normal
                )
                if opposite_polygon and opposite_normal and opposite_point:
                    self.face_polygon = opposite_polygon
                else:
                    self.face_polygon = self.face_polygon
            else:
                self.face_polygon = self.face_polygon

            self.face_local_system = local_system

            if has_start_uv and has_end_uv:
                u_start = self.build_ele.PosicionRelativaU_Inicio.value
                v_start = self.build_ele.PosicionRelativaV_Inicio.value
                u_end = self.build_ele.PosicionRelativaU_Fin.value
                v_end = self.build_ele.PosicionRelativaV_Fin.value

                new_start = calculate_position_from_uv(u_start, v_start, local_system)
                new_end = calculate_position_from_uv(u_end, v_end, local_system)

                if not new_start or not new_end:
                    return False

                new_start = self._clamp_point_to_face(new_start, local_system)
                new_end = self._clamp_point_to_face(new_end, local_system)

                if self.face_normal and self.face_point:
                    line_before_projection = AllplanGeo.Line3D(new_start, new_end)
                    line_after_projection = project_line_on_face(line_before_projection, self.face_point, self.face_normal)
                    new_start = line_after_projection.StartPoint
                    new_end = line_after_projection.EndPoint
            else:
                u_rel = self.build_ele.PosicionRelativaU.value
                v_rel = self.build_ele.PosicionRelativaV.value

                line_center_new = calculate_position_from_uv(u_rel, v_rel, local_system)
                if not line_center_new:
                    return False

                current_line = self.line_result.input_line
                line_length = vector_from_points(current_line.StartPoint, current_line.EndPoint).GetLength()
                if line_length < 0.1:
                    return False

                axis_u = local_system['axis_u']
                axis_v = local_system['axis_v']

                line_u_component = self.build_ele.LineaOrientacionU.value if hasattr(self.build_ele, 'LineaOrientacionU') else 1.0
                line_v_component = self.build_ele.LineaOrientacionV.value if hasattr(self.build_ele, 'LineaOrientacionV') else 0.0

                line_vector_new = AllplanGeo.Vector3D(
                    axis_u.X * line_u_component + axis_v.X * line_v_component,
                    axis_u.Y * line_u_component + axis_v.Y * line_v_component,
                    axis_u.Z * line_u_component + axis_v.Z * line_v_component
                )
                line_vector_new = normalize_vector(line_vector_new)
                if not line_vector_new:
                    return False

                half_length = line_length / 2.0

                new_start = AllplanGeo.Point3D(
                    line_center_new.X - line_vector_new.X * half_length,
                    line_center_new.Y - line_vector_new.Y * half_length,
                    line_center_new.Z - line_vector_new.Z * half_length
                )

                new_end = AllplanGeo.Point3D(
                    line_center_new.X + line_vector_new.X * half_length,
                    line_center_new.Y + line_vector_new.Y * half_length,
                    line_center_new.Z + line_vector_new.Z * half_length
                )

                new_start = self._clamp_point_to_face(new_start, local_system)
                new_end = self._clamp_point_to_face(new_end, local_system)

                if self.face_normal and self.face_point:
                    line_before_projection = AllplanGeo.Line3D(new_start, new_end)
                    line_after_projection = project_line_on_face(line_before_projection, self.face_point, self.face_normal)
                    new_start = line_after_projection.StartPoint
                    new_end = line_after_projection.EndPoint

            self.line_result.input_line = AllplanGeo.Line3D(new_start, new_end)

            if hasattr(self.build_ele, 'PuntoInicial'):
                self.build_ele.PuntoInicial.value = new_start
            if hasattr(self.build_ele, 'PuntoFinal'):
                self.build_ele.PuntoFinal.value = new_end

            line_midpoint = AllplanGeo.Point3D(
                (new_start.X + new_end.X) / 2.0,
                (new_start.Y + new_end.Y) / 2.0,
                (new_start.Z + new_end.Z) / 2.0
            )
            self.face_point = line_midpoint

            if hasattr(self.build_ele, 'PuntoClicX'):
                self.build_ele.PuntoClicX.value = line_midpoint.X
            if hasattr(self.build_ele, 'PuntoClicY'):
                self.build_ele.PuntoClicY.value = line_midpoint.Y
            if hasattr(self.build_ele, 'PuntoClicZ'):
                self.build_ele.PuntoClicZ.value = line_midpoint.Z

            if local_system:
                rel_pos_start = calculate_relative_position(new_start, local_system)
                if rel_pos_start:
                    if hasattr(self.build_ele, 'PosicionRelativaU_Inicio'):
                        self.build_ele.PosicionRelativaU_Inicio.value = rel_pos_start['u']
                    if hasattr(self.build_ele, 'PosicionRelativaV_Inicio'):
                        self.build_ele.PosicionRelativaV_Inicio.value = rel_pos_start['v']

                rel_pos_end = calculate_relative_position(new_end, local_system)
                if rel_pos_end:
                    if hasattr(self.build_ele, 'PosicionRelativaU_Fin'):
                        self.build_ele.PosicionRelativaU_Fin.value = rel_pos_end['u']
                    if hasattr(self.build_ele, 'PosicionRelativaV_Fin'):
                        self.build_ele.PosicionRelativaV_Fin.value = rel_pos_end['v']

                line_center_new = AllplanGeo.Point3D(
                    (new_start.X + new_end.X) / 2.0,
                    (new_start.Y + new_end.Y) / 2.0,
                    (new_start.Z + new_end.Z) / 2.0
                )
                rel_pos_center = calculate_relative_position(line_center_new, local_system)
                if rel_pos_center:
                    if hasattr(self.build_ele, 'PosicionRelativaU'):
                        self.build_ele.PosicionRelativaU.value = rel_pos_center['u']
                    if hasattr(self.build_ele, 'PosicionRelativaV'):
                        self.build_ele.PosicionRelativaV.value = rel_pos_center['v']

            if wall_element:
                self.detected_wall = wall_element
                self.detected_wall_guid = str(wall_element.GetModelElementUUID())
                # self.wall_allplan_id = get_wall_ifc_id(wall_element)
                if hasattr(self.build_ele, 'MuroGUID'):
                    self.build_ele.MuroGUID.value = self.detected_wall_guid

                if hasattr(self.build_ele, 'MuroConnection'):
                    try:
                        conn = self.build_ele.MuroConnection.value
                        if not hasattr(conn, 'element') or not conn.element.IsValid() or \
                           (hasattr(conn, 'uuid') and str(conn.uuid) == "00000000-0000-0000-0000-000000000000"):
                            conn.element = wall_element
                    except Exception:
                        try:
                            conn = self.build_ele.MuroConnection.value
                            conn.element = wall_element
                        except Exception:
                            pass

            if hasattr(self.build_ele, 'LongitudLinea'):
                line_length = vector_from_points(new_start, new_end).GetLength()
                self.build_ele.LongitudLinea.value = line_length

            return True

        except Exception:
            return False

    def start_input(self):
        """Inicia el input del script"""
        is_individual_distribution = self._is_individual_distribution()

        if not self.is_modification_mode and is_individual_distribution:
            self.line_result = LineInteractorResult()
            self.position_result = PointInteractorResult()
            self.wall_select_result = WallSelectResult()
            self.face_select_result = SolidFaceSelectResult()

        self._update_incremental_growth()

        if is_individual_distribution:
            self.is_free_mode = False
        elif hasattr(self.build_ele, 'angular_libre'):
            val = self.build_ele.angular_libre.value
            if isinstance(val, bool):
                self.is_free_mode = val
            elif isinstance(val, str):
                self.is_free_mode = val.lower() in ('true', '1', 'yes')
            else:
                self.is_free_mode = bool(val)
        else:
            self.is_free_mode = False

        if hasattr(self.build_ele, 'angular_libre'):
            self.build_ele.angular_libre.value = bool(self.is_free_mode)

        if self.needs_auto_update:
            success = self._update_angular_position()

            if success:
                self.position_updated_in_start_input = True

                if not self.detected_wall:
                    self._load_face_info_from_properties()

                if self.face_polygon and self.face_normal and not self.face_local_system:
                    if (hasattr(self.build_ele, 'CaraNormalX') and
                        hasattr(self.build_ele, 'CaraNormalY') and
                        hasattr(self.build_ele, 'CaraNormalZ')):
                        stored_normal = AllplanGeo.Vector3D(
                            self.build_ele.CaraNormalX.value,
                            self.build_ele.CaraNormalY.value,
                            self.build_ele.CaraNormalZ.value
                        )
                        stored_normal = normalize_vector(stored_normal) or stored_normal
                        self.face_normal = stored_normal

                    self.face_local_system = calculate_local_coordinate_system(
                        self.face_polygon, self.face_normal
                    )

            self.state = STOPPED
            self.script_object_interactor = None
            return

        if self.is_modification_mode:
            self.is_free_mode = self._get_free_mode()

            if not self.is_free_mode and self._should_update_position():
                success = self._update_angular_position()

                if success:
                    if not self.detected_wall:
                        self._load_face_info_from_properties()

                    if self.face_polygon and self.face_normal and not self.face_local_system:
                        if (hasattr(self.build_ele, 'CaraNormalX') and
                            hasattr(self.build_ele, 'CaraNormalY') and
                            hasattr(self.build_ele, 'CaraNormalZ')):
                            stored_normal = AllplanGeo.Vector3D(
                                self.build_ele.CaraNormalX.value,
                                self.build_ele.CaraNormalY.value,
                                self.build_ele.CaraNormalZ.value
                            )
                            stored_normal = normalize_vector(stored_normal) or stored_normal
                            self.face_normal = stored_normal

                        self.face_local_system = calculate_local_coordinate_system(
                            self.face_polygon, self.face_normal
                        )

            if not self.detected_wall:
                self._load_face_info_from_properties()

            if self.line_result.input_line:
                self.state = STOPPED
                self.script_object_interactor = None
                self.preview_active = True
                return
            else:
                pass

        if is_individual_distribution:
            self.state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el muro para el angular individual"
            )
        elif self.is_free_mode:
            self.state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el muro (opcional)"
            )
        else:
            self.state = SELECTING_WALL
            self.script_object_interactor = SolidFaceSelectInteractor(
                self.face_select_result,
                "Seleccione la cara del muro para los angulares"
            )

    def start_next_input(self):
        """Gestiona la transición entre interactors"""
        if self.state == SELECTING_WALL:
            if self._is_individual_distribution():
                if self.wall_select_result.is_selected:
                    print("[INPUT][INDIVIDUAL] Muro seleccionado; pasando a seleccion de cara")
                    self._process_wall_selection_free()
                    self.state = SELECTING_FACE
                    self.face_select_result = SolidFaceSelectResult()
                    self.script_object_interactor = SolidFaceSelectInteractor(
                        self.face_select_result,
                        "Seleccione la cara del muro para orientar el angular"
                    )
                else:
                    self.state = CANCEL
                    self.script_object_interactor = None
            elif self.is_free_mode:
                if self.wall_select_result.is_selected:
                    self._process_wall_selection_free()
                self.state = SELECTING_LINE
                self._start_line_input()
            else:
                if self.face_select_result.is_selected:
                    self._process_wall_selection()
                    self.state = SELECTING_LINE
                    self._start_line_input()
                else:
                    self.state = CANCEL
                    self.script_object_interactor = None

        elif self.state == SELECTING_FACE:
            if self.face_select_result.is_selected:
                print("[INPUT][INDIVIDUAL] Cara seleccionada; pasando a seleccion de posicion")
                self._process_wall_selection()
                self.state = SELECTING_POSITION
                self._start_position_input()
            else:
                self.state = CANCEL
                self.script_object_interactor = None

        elif self.state == SELECTING_LINE:
            if self.line_result.input_line:
                self._process_line_input()

            self.script_object_interactor = None
            self.preview_active = True

        elif self.state == SELECTING_POSITION:
            print("[INPUT][INDIVIDUAL] Posicion seleccionada; construyendo linea interna")
            self._process_position_input()
            self.script_object_interactor = None
            self.preview_active = True

    def _process_wall_selection_free(self):
        """Procesa la selección del muro en modo libre (solo referencia)"""
        element_guid_str = self.wall_select_result.element_guid
        selected_element = self.wall_select_result.element

        self.detected_wall = selected_element
        real_wall_guid = str(selected_element.GetModelElementUUID())
        self.detected_wall_guid = real_wall_guid

        # self.wall_allplan_id = get_wall_ifc_id(selected_element)

        if hasattr(self.build_ele, 'MuroConnection'):
            self.build_ele.MuroConnection.value.element = selected_element

        if hasattr(self.build_ele, 'MuroGUID'):
            self.build_ele.MuroGUID.value = real_wall_guid

    def _process_wall_selection(self):
        """Procesa la selección del muro"""
        self.face_point = self.face_select_result.face_point
        self.face_normal = self.face_select_result.face_normal
        self.face_polygon = self.face_select_result.face_polygon

        element_guid_str = self.face_select_result.element_guid
        selected_element = self.face_select_result.element

        self.detected_wall = selected_element

        real_wall_guid = str(selected_element.GetModelElementUUID())
        self.detected_wall_guid = real_wall_guid

        # self.wall_allplan_id = get_wall_ifc_id(selected_element)

        if hasattr(self.build_ele, 'MuroConnection'):
            self.build_ele.MuroConnection.value.element = selected_element

            if str(self.build_ele.MuroConnection.value.uuid) == "00000000-0000-0000-0000-000000000000":
                element_guid = AllplanEleAdapter.BaseElementAdapterParentElementService.FromString(element_guid_str)
                element_from_guid = AllplanBaseElements.ElementsService.GetElement(element_guid)

                if element_from_guid and element_from_guid.IsValid():
                    self.build_ele.MuroConnection.value.element = element_from_guid
                    real_wall_guid = str(element_from_guid.GetModelElementUUID())
                    self.detected_wall_guid = real_wall_guid
        else:
            pass

        if hasattr(self.build_ele, 'MuroGUID'):
            self.build_ele.MuroGUID.value = real_wall_guid
        else:
            pass

        if self.face_normal:
            self.face_normal = normalize_vector(self.face_normal) or self.face_normal
        if self.face_normal:
            if hasattr(self.build_ele, 'CaraNormalX'):
                self.build_ele.CaraNormalX.value = self.face_normal.X
            if hasattr(self.build_ele, 'CaraNormalY'):
                self.build_ele.CaraNormalY.value = self.face_normal.Y
            if hasattr(self.build_ele, 'CaraNormalZ'):
                self.build_ele.CaraNormalZ.value = self.face_normal.Z

        if self.face_point:
            if hasattr(self.build_ele, 'PuntoClicX'):
                self.build_ele.PuntoClicX.value = self.face_point.X
            if hasattr(self.build_ele, 'PuntoClicY'):
                self.build_ele.PuntoClicY.value = self.face_point.Y
            if hasattr(self.build_ele, 'PuntoClicZ'):
                self.build_ele.PuntoClicZ.value = self.face_point.Z

        face_index = self._find_face_index(selected_element, self.face_polygon, self.face_normal)
        if face_index is not None and hasattr(self.build_ele, 'CaraIndice'):
            self.build_ele.CaraIndice.value = face_index

        if self.face_polygon and self.face_normal:
            self.face_local_system = calculate_local_coordinate_system(
                self.face_polygon,
                self.face_normal
            )

    def _clamp_point_to_face(self,
                             point: AllplanGeo.Point3D,
                             local_system: dict = None) -> AllplanGeo.Point3D:
        """Limita un punto a los límites de la cara usando coordenadas relativas U, V"""
        if local_system is None:
            local_system = self.face_local_system

        if not local_system:
            if self.face_polygon and self.face_normal and self.face_point:
                projected_point = project_point_to_plane(point, self.face_point, self.face_normal)
                clamped = clamp_point_to_face_bounds(projected_point, self.face_polygon, self.face_normal)
                return clamped
            return point

        if self.face_point and self.face_normal:
            point = project_point_to_plane(point, self.face_point, self.face_normal)

        relative = calculate_relative_position(point, local_system)
        if not relative:
            return point

        u_clamped = min(max(relative['u'], 0.0), 1.0)
        v_clamped = min(max(relative['v'], 0.0), 1.0)

        clamped_point = calculate_position_from_uv(u_clamped, v_clamped, local_system)
        if clamped_point:
            return clamped_point
        else:
            return point

    def _clamp_line_to_face(self,
                            line: AllplanGeo.Line3D,
                            local_system: dict = None) -> tuple[AllplanGeo.Line3D, dict]:
        """Limita una línea a los límites de la cara usando coordenadas relativas"""
        if local_system is None:
            local_system = self.face_local_system

        if not local_system:
            if self.face_polygon and self.face_normal:
                clamped_line = clamp_line_to_face_bounds(line, self.face_polygon, self.face_normal)
                return clamped_line, None
            return line, None

        start = self._clamp_point_to_face(line.StartPoint, local_system)
        end = self._clamp_point_to_face(line.EndPoint, local_system)

        return AllplanGeo.Line3D(start, end), local_system

    def _get_individual_horizontal_axis_on_face(self) -> AllplanGeo.Vector3D:
        """Obtiene el eje longitudinal más horizontal dentro del plano de la cara."""
        local_system = self.face_local_system
        if not local_system and self.face_polygon and self.face_normal:
            local_system = calculate_local_coordinate_system(self.face_polygon, self.face_normal)
            if local_system:
                self.face_local_system = local_system

        candidates = []
        if local_system:
            for key in ("axis_u", "axis_v"):
                axis = local_system.get(key)
                axis = normalize_vector(axis) if axis else None
                if axis and axis.GetLength() > 1e-6:
                    candidates.append(axis)

        if not candidates and self.face_normal:
            normal = normalize_vector(self.face_normal)
            if normal:
                global_x = AllplanGeo.Vector3D(1.0, 0.0, 0.0)
                dot = vector_dot(global_x, normal)
                projected = AllplanGeo.Vector3D(
                    global_x.X - dot * normal.X,
                    global_x.Y - dot * normal.Y,
                    global_x.Z - dot * normal.Z
                )
                projected = normalize_vector(projected)
                if projected and projected.GetLength() > 1e-6:
                    candidates.append(projected)

        if not candidates:
            return AllplanGeo.Vector3D(1.0, 0.0, 0.0)

        return normalize_vector(min(candidates, key=lambda item: abs(item.Z)))

    def _apply_individual_manual_z(self, point: AllplanGeo.Point3D) -> AllplanGeo.Point3D:
        """Aplica la Z global indicada en paleta para el posicionamiento individual."""
        z_value = self._get_individual_z_value(point.Z)
        return AllplanGeo.Point3D(point.X, point.Y, z_value)

    def _build_individual_line_from_position(self, position: AllplanGeo.Point3D) -> AllplanGeo.Line3D:
        """Construye una línea interna de pieza desde el punto clicado."""
        angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
        definition = ANGULAR_CATALOG.get(angular_key, None)
        if not definition:
            return AllplanGeo.Line3D()

        piece_length = definition.get("piece_length", definition.get("length", 0.0))
        if piece_length <= 0:
            return AllplanGeo.Line3D()

        z_value = self._resolve_individual_z_from_point(position, update_from_point=True)
        position = self._project_point_to_individual_vertical_face(position, z_value)

        x_dir = self._get_individual_horizontal_axis_on_face()
        start = move_point(position, x_dir, -piece_length / 2.0)
        end = move_point(position, x_dir, piece_length / 2.0)
        return self._project_line_to_individual_vertical_face(AllplanGeo.Line3D(start, end), z_value)

    def _build_individual_centered_preview_line(self, line: AllplanGeo.Line3D) -> AllplanGeo.Line3D:
        """Construye la guía visual centrada en el punto de colocación del angular."""
        if not line:
            return AllplanGeo.Line3D()

        angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
        definition = ANGULAR_CATALOG.get(angular_key, None)
        if not definition:
            return line

        piece_length = definition.get("piece_length", definition.get("length", 0.0))
        if piece_length <= 0:
            return line

        x_dir = normalize_vector(vector_from_points(line.StartPoint, line.EndPoint))
        if not x_dir or x_dir.GetLength() < 1e-6:
            return line

        center = AllplanGeo.Point3D(
            (line.StartPoint.X + line.EndPoint.X) / 2.0,
            (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
            (line.StartPoint.Z + line.EndPoint.Z) / 2.0
        )
        start = move_point(center, x_dir, -piece_length / 2.0)
        end = move_point(center, x_dir, piece_length / 2.0)
        preview_line = AllplanGeo.Line3D(start, end)

        if self.face_normal and self.face_point:
            preview_line = self._project_line_to_individual_vertical_face(preview_line)

        return preview_line

    def _start_position_input(self):
        """Inicia el tercer click: posición final del angular individual."""
        self.position_result = PointInteractorResult()
        self.script_object_interactor = PointInteractor(
            self.position_result,
            True,
            "Indique la posición del angular individual",
            preview_function=self.preview_position_function,
        )

    def preview_position_function(self):
        """Preview de la línea interna que se creará desde el punto clicado."""
        point = self.position_result.input_point
        if not point:
            return

        line = self._build_individual_line_from_position(point)
        if line == AllplanGeo.Line3D():
            return

        preview_line = self._build_individual_centered_preview_line(line)
        model_list = ModelEleList()
        model_list.append_geometry_3d(preview_line)
        if model_list:
            AllplanBaseElements.DrawElementPreview(
                self.document,
                AllplanGeo.Matrix3D(),
                model_list,
                True,
                None
            )

    def _process_position_input(self):
        """Convierte el tercer click en línea interna y procesa la pieza."""
        point = self.position_result.input_point
        if not point:
            return

        line = self._build_individual_line_from_position(point)
        if line == AllplanGeo.Line3D():
            return

        self.line_result.input_line = line
        self._process_line_input(apply_incremental_growth=False)

    def _restart_interactor_for_current_distribution(self) -> bool:
        """Reinicia el primer input cuando cambia el tipo de distribución."""
        coord_input = getattr(self.script_object_interactor, "coord_input", None)

        self.line_result = LineInteractorResult()
        self.position_result = PointInteractorResult()
        self.wall_select_result = WallSelectResult()
        self.face_select_result = SolidFaceSelectResult()
        self.preview_active = False

        is_individual_distribution = self._is_individual_distribution()
        self.is_free_mode = False if is_individual_distribution else self._get_free_mode()
        if hasattr(self.build_ele, 'angular_libre'):
            self.build_ele.angular_libre.value = bool(self.is_free_mode)

        if is_individual_distribution:
            self.state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el muro para el angular individual"
            )
        elif self.is_free_mode:
            self.state = SELECTING_WALL
            self.script_object_interactor = WallSelectInteractor(
                self.wall_select_result,
                "Seleccione el muro (opcional)"
            )
        else:
            self.state = SELECTING_WALL
            self.script_object_interactor = SolidFaceSelectInteractor(
                self.face_select_result,
                "Seleccione la cara del muro para los angulares"
            )

        if coord_input:
            self.script_object_interactor.start_input(coord_input)
            return True
        return False

    def _start_line_input(self):
        """Inicia el interactor de línea"""
        is_individual_distribution = self._get_distribution_type() == DISTRIBUTION_INDIVIDUAL
        if self.is_free_mode:
            if is_individual_distribution:
                prompt_msg = "Indique punto y dirección para el angular individual"
            else:
                prompt_msg = "Defina la línea para los angulares - Posicionamiento libre"
        else:
            if is_individual_distribution:
                prompt_msg = "Indique punto y dirección para el angular individual"
            else:
                prompt_msg = "Defina la línea para los angulares"

        print(f"[LINE_INPUT] Inicio: distribucion={self._get_distribution_type()} allow_pick_up={not is_individual_distribution}")
        self.script_object_interactor = LineInteractor(
            self.line_result,
            True,
            prompt_msg,
            allow_pick_up=not is_individual_distribution,
            preview_function=self.preview_line_function,
        )

    def preview_line_function(self, line: AllplanGeo.Line3D) -> ModelEleList:
        """Función de preview para la línea.

        Si hay una cara seleccionada y no está en modo libre, proyecta y recorta la línea a los límites.
        Si el crecimiento incremental está activado, ajusta la línea según incrementos.
        """
        if not line:
            return ModelEleList()

        self._update_incremental_growth()

        if not self.is_free_mode and self.face_polygon and self.face_normal and self.face_point:
            if self._is_individual_distribution():
                line = self._project_line_to_individual_vertical_face(line)
            else:
                projected_line = project_line_on_face(line, self.face_point, self.face_normal)
                line = clamp_line_to_face_bounds(projected_line, self.face_polygon, self.face_normal)

        try:
            angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
            if angular_key and angular_key in ANGULAR_CATALOG:
                definition = ANGULAR_CATALOG[angular_key]
                piece_length = definition.get("piece_length", definition.get("length", 0.0))

                separation = 10.0
                if hasattr(self.build_ele, 'SeparacionAngulares'):
                    try:
                        separation = max(0.0, float(self.build_ele.SeparacionAngulares.value))
                    except (ValueError, TypeError):
                        pass

                if piece_length > 0:
                    if self._get_distribution_type() == DISTRIBUTION_INDIVIDUAL:
                        line = set_line_length(line, piece_length)
                    else:
                        increment = piece_length + separation
                        line = adjust_line_length_incremental(line, increment)
        except (ValueError, TypeError, AttributeError):
            pass

        model_list = ModelEleList()
        model_list.append_geometry_3d(line)
        return model_list

    def _prepare_line(self, line: AllplanGeo.Line3D) -> tuple[AllplanGeo.Line3D, dict]:
        """Prepara la línea proyectándola y limitándola a la cara"""
        local_system = None

        if not self.is_free_mode and self.face_normal and self.face_point:
            line = project_line_on_face(line, self.face_point, self.face_normal)
            line, local_system = self._clamp_line_to_face(line)

        if not local_system and not self.is_free_mode and self.face_polygon and self.face_normal:
            local_system = calculate_local_coordinate_system(self.face_polygon, self.face_normal)
            if local_system:
                self.face_local_system = local_system

        return line, local_system

    def _process_line_input(self, apply_incremental_growth: bool = True):
        """Procesa la línea dibujada por el usuario

        Args:
            apply_incremental_growth: Si True, aplica crecimiento incremental (solo durante creación).
                                     Si False, omite el crecimiento incremental (útil durante edición con handles).
        """
        if not self.line_result.input_line:
            return

        self._update_incremental_growth()

        line = self.line_result.input_line
        is_individual_distribution = self._is_individual_distribution()
        print("[LINE_INPUT] Recibida p0=", line.StartPoint, "p1=", line.EndPoint, "distribucion=", self._get_distribution_type())

        if not self.is_free_mode:
            if is_individual_distribution and self.face_normal and self.face_point:
                line = self._project_line_to_individual_vertical_face(line)
                local_system = self.face_local_system
                if not local_system and self.face_polygon and self.face_normal:
                    local_system = calculate_local_coordinate_system(
                        self.face_polygon,
                        self.face_normal
                    )
            else:
                line, local_system = self._prepare_line(line)
            self.line_result.input_line = line

            if local_system:
                self.face_local_system = local_system
            elif not self.face_local_system and self.face_polygon and self.face_normal:
                self.face_local_system = calculate_local_coordinate_system(
                    self.face_polygon,
                    self.face_normal
                )

        if apply_incremental_growth:
            try:
                angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
                if angular_key and angular_key in ANGULAR_CATALOG:
                    definition = ANGULAR_CATALOG[angular_key]
                    piece_length = definition.get("piece_length", definition.get("length", 0.0))

                    separation = 10.0
                    if hasattr(self.build_ele, 'SeparacionAngulares'):
                        try:
                            separation = max(0.0, float(self.build_ele.SeparacionAngulares.value))
                        except (ValueError, TypeError):
                            pass

                    if piece_length > 0:
                        if is_individual_distribution:
                            adjusted_line = set_line_length(line, piece_length)
                        else:
                            increment = piece_length + separation
                            adjusted_line = adjust_line_length_incremental(line, increment)
                        self.line_result.input_line = adjusted_line
                        line = adjusted_line
            except (ValueError, TypeError, AttributeError):
                pass

        if not self.is_free_mode and self.face_polygon and self.face_normal and self.face_point:
            if not self.face_local_system:
                if (hasattr(self.build_ele, 'CaraNormalX') and
                    hasattr(self.build_ele, 'CaraNormalY') and
                    hasattr(self.build_ele, 'CaraNormalZ')):
                    stored_normal = AllplanGeo.Vector3D(
                        self.build_ele.CaraNormalX.value,
                        self.build_ele.CaraNormalY.value,
                        self.build_ele.CaraNormalZ.value
                    )
                    stored_normal = normalize_vector(stored_normal) or stored_normal
                    self.face_normal = stored_normal
                self.face_local_system = calculate_local_coordinate_system(
                    self.face_polygon, self.face_normal
                )

            if is_individual_distribution:
                line = self._project_line_to_individual_vertical_face(line)
            else:
                line, local_system = self._clamp_line_to_face(line)
                if local_system:
                    self.face_local_system = local_system

                line = clamp_line_to_face_bounds(line, self.face_polygon, self.face_normal)
            self.line_result.input_line = line

            if hasattr(self.build_ele, 'PuntoInicial'):
                self.build_ele.PuntoInicial.value = line.StartPoint
            if hasattr(self.build_ele, 'PuntoFinal'):
                self.build_ele.PuntoFinal.value = line.EndPoint

        if not self.is_free_mode and self.face_local_system:
            line_center = AllplanGeo.Point3D(
                (line.StartPoint.X + line.EndPoint.X) / 2.0,
                (line.StartPoint.Y + line.EndPoint.Y) / 2.0,
                (line.StartPoint.Z + line.EndPoint.Z) / 2.0
            )

            rel_pos = calculate_relative_position(line_center, self.face_local_system)

            if rel_pos:
                if hasattr(self.build_ele, 'PosicionRelativaU'):
                    self.build_ele.PosicionRelativaU.value = rel_pos['u']
                if hasattr(self.build_ele, 'PosicionRelativaV'):
                    self.build_ele.PosicionRelativaV.value = rel_pos['v']

            rel_pos_start = calculate_relative_position(line.StartPoint, self.face_local_system)
            if rel_pos_start:
                if hasattr(self.build_ele, 'PosicionRelativaU_Inicio'):
                    self.build_ele.PosicionRelativaU_Inicio.value = rel_pos_start['u']
                if hasattr(self.build_ele, 'PosicionRelativaV_Inicio'):
                    self.build_ele.PosicionRelativaV_Inicio.value = rel_pos_start['v']

            rel_pos_end = calculate_relative_position(line.EndPoint, self.face_local_system)
            if rel_pos_end:
                if hasattr(self.build_ele, 'PosicionRelativaU_Fin'):
                    self.build_ele.PosicionRelativaU_Fin.value = rel_pos_end['u']
                if hasattr(self.build_ele, 'PosicionRelativaV_Fin'):
                    self.build_ele.PosicionRelativaV_Fin.value = rel_pos_end['v']

            line_vector = AllplanGeo.Vector3D(
                line.EndPoint.X - line.StartPoint.X,
                line.EndPoint.Y - line.StartPoint.Y,
                line.EndPoint.Z - line.StartPoint.Z
            )
            line_vector = normalize_vector(line_vector)
            if line_vector:
                axis_u = self.face_local_system['axis_u']
                axis_v = self.face_local_system['axis_v']

                line_u = vector_dot(line_vector, axis_u)
                line_v = vector_dot(line_vector, axis_v)

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

        if self.detected_wall:
            real_wall_guid = str(self.detected_wall.GetModelElementUUID())
            self.detected_wall_guid = real_wall_guid

            if hasattr(self.build_ele, 'MuroGUID'):
                self.build_ele.MuroGUID.value = real_wall_guid

            if hasattr(self.build_ele, 'MuroConnection'):
                try:
                    conn = self.build_ele.MuroConnection.value
                    if not hasattr(conn, 'element') or not conn.element.IsValid() or \
                       (hasattr(conn, 'uuid') and str(conn.uuid) == "00000000-0000-0000-0000-000000000000"):
                        conn.element = self.detected_wall
                except Exception:
                    try:
                        conn = self.build_ele.MuroConnection.value
                        conn.element = self.detected_wall
                    except Exception:
                        pass

        if hasattr(self.build_ele, 'PuntoInicial'):
            self.build_ele.PuntoInicial.value = line.StartPoint
        if hasattr(self.build_ele, 'PuntoFinal'):
            self.build_ele.PuntoFinal.value = line.EndPoint

        # Siempre sincronizar la línea final a build_ele para que on_cancel/param_list tengan los puntos
        self._sync_line_to_build_ele()
        print("[LINE_INPUT] Final p0=", self.line_result.input_line.StartPoint, "p1=", self.line_result.input_line.EndPoint)

    def _update_incremental_growth(self):
        """Calcula y actualiza el valor de CrecimientoIncremental basado en piece_length + separation"""
        if not hasattr(self.build_ele, 'CrecimientoIncremental'):
            return

        try:
            angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
            if angular_key and angular_key in ANGULAR_CATALOG:
                definition = ANGULAR_CATALOG[angular_key]
                piece_length = definition.get("piece_length", definition.get("length", 0.0))

                separation = 10.0
                if hasattr(self.build_ele, 'SeparacionAngulares'):
                    try:
                        separation = max(0.0, float(self.build_ele.SeparacionAngulares.value))
                    except (ValueError, TypeError):
                        pass

                if piece_length > 0:
                    if self._get_distribution_type() == DISTRIBUTION_INDIVIDUAL:
                        increment = piece_length
                    else:
                        increment = piece_length + separation
                    self.build_ele.CrecimientoIncremental.value = increment
                else:
                    self.build_ele.CrecimientoIncremental.value = 0.0
            else:
                self.build_ele.CrecimientoIncremental.value = 0.0
        except (ValueError, TypeError, AttributeError):
            self.build_ele.CrecimientoIncremental.value = 0.0

    def _sync_individual_line_to_z_value(self) -> bool:
        """Actualiza la línea individual existente al ValorZIndividual indicado."""
        if not self._is_individual_distribution() or not hasattr(self.build_ele, "ValorZIndividual"):
            return False

        try:
            z_value = float(self.build_ele.ValorZIndividual.value)
        except (TypeError, ValueError):
            return False

        start_point = getattr(getattr(self.build_ele, "PuntoInicial", None), "value", None)
        end_point = getattr(getattr(self.build_ele, "PuntoFinal", None), "value", None)
        if start_point is None or end_point is None:
            return False

        line_vector = vector_from_points(start_point, end_point)
        line_length = line_vector.GetLength()
        if line_length < 1e-6:
            return False

        line_dir = normalize_vector(line_vector)
        center = AllplanGeo.Point3D(
            (start_point.X + end_point.X) / 2.0,
            (start_point.Y + end_point.Y) / 2.0,
            z_value
        )
        updated_start = move_point(center, line_dir, -line_length / 2.0)
        updated_end = move_point(center, line_dir, line_length / 2.0)
        updated_line = AllplanGeo.Line3D(updated_start, updated_end)

        self.is_free_mode = False
        if hasattr(self.build_ele, "angular_libre"):
            self.build_ele.angular_libre.value = False

        if not (self.face_normal and self.face_point):
            self._load_existing_points()
            self._load_face_info_from_properties()

        if self.face_normal and self.face_point:
            updated_line = self._project_line_to_individual_vertical_face(updated_line, z_value)

        self.line_result.input_line = updated_line
        self._process_line_input(apply_incremental_growth=False)
        return True

    def modify_element_property(self, name: str, _value) -> bool:
        if name == "TipoAngular":
            if hasattr(self.build_ele, 'TipoAngular'):
                if self.build_ele.TipoAngular.value not in ANGULAR_CATALOG:
                    first_key = next(iter(ANGULAR_CATALOG.keys()))
                    self.build_ele.TipoAngular.value = first_key
            self._update_incremental_growth()

        if name == "SeparacionAngulares":
            if hasattr(self.build_ele, 'SeparacionAngulares'):
                try:
                    separation = float(self.build_ele.SeparacionAngulares.value)
                    if separation < 0.0:
                        self.build_ele.SeparacionAngulares.value = 10.0
                except (ValueError, TypeError):
                    self.build_ele.SeparacionAngulares.value = 10.0
            self._update_incremental_growth()

        if name == "TipoDistribucion":
            distribution_type = self._get_distribution_type()
            print(f"[DISTRIBUTION] Cambio de combobox detectado: {distribution_type}")
            if distribution_type == DISTRIBUTION_INDIVIDUAL:
                self.is_free_mode = False
                if hasattr(self.build_ele, 'angular_libre'):
                    self.build_ele.angular_libre.value = False
            self._restart_interactor_for_current_distribution()
            return True

        if name == "ValorZIndividual" and self._sync_individual_line_to_z_value():
            self.execute()
            return True

        if self.script_object_interactor is not None:
            return True

        if name == "angular_libre":
            self.is_free_mode = False if self._is_individual_distribution() else self._get_free_mode()

        self.execute()
        return True

    def set_active_palette_page_index(self, page_index: int) -> None:
        """Sincroniza la distribución con la pestaña activa de la paleta."""
        try:
            page_index = int(page_index)
        except (TypeError, ValueError):
            return

        if not hasattr(self.build_ele, "TipoDistribucion"):
            return

        if page_index == 0:
            distribution_value = "Individual"
        elif page_index == 1:
            distribution_value = "Grupal"
        else:
            return

        if self.build_ele.TipoDistribucion.value == distribution_value:
            return

        self.build_ele.TipoDistribucion.value = distribution_value
        print(f"[DISTRIBUTION] Cambio de pestana detectado: {distribution_value}")

        if distribution_value == "Individual":
            self.is_free_mode = False
            if hasattr(self.build_ele, 'angular_libre'):
                self.build_ele.angular_libre.value = False
        else:
            if hasattr(self.build_ele, 'angular_libre'):
                self.build_ele.angular_libre.value = True
            self.is_free_mode = self._get_free_mode()

        self._restart_interactor_for_current_distribution()

    def move_handle(self,
                    handle_prop: HandleProperties,
                    input_pnt: AllplanGeo.Point3D) -> CreateElementResult:
        """Actualiza la geometría al mover un handle point

        Limita el punto movido a los límites de la cara del muro usando el sistema local (solo en modo acoplado).
        """
        self.is_free_mode = self._get_free_mode()
        is_individual_distribution = self._is_individual_distribution()

        self._update_incremental_growth()

        if not self.is_free_mode and not is_individual_distribution:
            if not (self.face_polygon and self.face_normal and self.face_point):
                self._load_existing_points()
                if not (self.face_polygon and self.face_normal and self.face_point):
                    self._load_face_info_from_properties()

            if self.face_polygon and self.face_normal and self.face_point:
                if not self.face_local_system:
                    if (hasattr(self.build_ele, 'CaraNormalX') and
                        hasattr(self.build_ele, 'CaraNormalY') and
                        hasattr(self.build_ele, 'CaraNormalZ')):
                        stored_normal = AllplanGeo.Vector3D(
                            self.build_ele.CaraNormalX.value,
                            self.build_ele.CaraNormalY.value,
                            self.build_ele.CaraNormalZ.value
                        )
                        stored_normal = normalize_vector(stored_normal) or stored_normal
                        self.face_normal = stored_normal

                    self.face_local_system = calculate_local_coordinate_system(
                        self.face_polygon, self.face_normal
                    )

                if self.face_local_system:
                    input_pnt = self._clamp_point_to_face(input_pnt)
                else:
                    input_pnt = clamp_point_to_face_bounds(
                        input_pnt, self.face_polygon, self.face_normal
                    )

        HandlePropertiesService.update_property_value(self.build_ele, handle_prop, input_pnt)

        start_prop = getattr(self.build_ele, 'PuntoInicial', None)
        end_prop = getattr(self.build_ele, 'PuntoFinal', None)
        start_point = start_prop.value if start_prop and hasattr(start_prop, 'value') else None
        end_point = end_prop.value if end_prop and hasattr(end_prop, 'value') else None

        if start_point and end_point:
            self.line_result.input_line = AllplanGeo.Line3D(start_point, end_point)
            if is_individual_distribution:
                self.line_result.input_line = self._project_line_to_individual_vertical_face(self.line_result.input_line)
            self._process_line_input(apply_incremental_growth=False)
        else:
            self.line_result.input_line = None

        return self.execute()

    def on_preview_draw(self):
        if self.preview_active and self.line_result.input_line:
            model_list = ModelEleList()
            model_list.append_geometry_3d(self.line_result.input_line)
            AllplanBaseElements.DrawElementPreview(self.document, AllplanGeo.Matrix3D(), model_list, True, None)

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
            "",  # subGroupName
            long_name,
            short_name,
            1,  # lineColorID
            1,  # lineThicknessID
            1,  # lineStyleID
            True,  # bVisible
            True,  # bModifiable
        )

    def create_angulars(self, geometries: list[AllplanGeo.BRep3D], edges: list[AllplanGeo.Line3D], definition: dict, pmp_pare: str = None) -> List[AllplanBasisElements.ModelElement3D]:
        """Crea ModelElement3D individuales con los angulares aplicando layer, color y PMP_PARE.

        En CREATE y EDIT se reaplican atributos usando el valor persistido en build_ele.

        Args:
            geometries: Lista de geometrías BRep3D
            definition: Diccionario con definición del angular (color, etc.)
            pmp_pare: Valor de PMP_PARE a aplicar (debe venir desde param_list del grupo, fallback a build_ele solo para casos especiales)

        Returns:
            List[ModelElement3D]: Lista de elementos 3D creados
        """
        elements = []

        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(ANG_LAYER, self.document)

        props = AllplanBaseElements.CommonProperties()
        props.GetGlobalProperties()
        props.Color = definition["color"]
        props.Layer = layer_id

        # Si es None, usar string vacío
        if pmp_pare is None:
            pmp_pare = ""

        attr_id = getattr(self, "attr_pmp_pare_id", 0)
        attr_wall_id = getattr(self, "attr_pmp_wall_id", 0)
        attr_detall_id = getattr(self, "attr_pmp_fg_ang_detall_id", 0)
        attr_forats_id = getattr(self, "attr_pmp_fg_ang_forats_id", 0)
        attr_nom_id = getattr(self, "attr_pmp_fg_ang_nom_id", 0)
        attr_neopre_id = getattr(self, "attr_pmp_fg_angular_neopre_id", 0)
        attr_grosor_neopre_id = getattr(self, "attr_pmp_fg_ang_neopre_id", 0)

        # Atributos PMP_FG_*: recalcular y setear al final (salida, no entrada). Valores desde build_ele.
        num_forats = get_num_forats_from_definition(definition)
        angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
        nom_value = get_nom_from_angular_key(angular_key) if angular_key else ""

        lleva_neopreno = bool(getattr(self.build_ele.SiLlevaNeopreno, "value", False)) if hasattr(self.build_ele, 'SiLlevaNeopreno') else False
        neopre_value = "Si" if lleva_neopreno else "No"

        grosor_length_value = ""
        if lleva_neopreno:
            grosor_length_value = float(definition["length"])

        for line in geometries:
            elem = AllplanBasisElements.ModelElement3D(props, line)

            attr_list = BuildingElementAttributeList()

            if attr_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_id, pmp_pare.replace("'", ""))

            if attr_wall_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_wall_id, pmp_pare.replace("'", ""))

            if attr_detall_id > 0:
                attr_list.add_attribute(attr_detall_id, "")

            if attr_forats_id > 0:
                attr_list.add_attribute(attr_forats_id, num_forats)

            if attr_nom_id > 0 and nom_value:
                attr_list.add_attribute(attr_nom_id, nom_value)

            if attr_neopre_id > 0:
                attr_list.add_attribute(attr_neopre_id, neopre_value)

            if attr_grosor_neopre_id > 0:
                attr_list.add_attribute(attr_grosor_neopre_id, grosor_length_value)

            if attr_list.get_attribute_list():
                elem.SetAttributes(attr_list.get_attribute_list())

            elements.append(elem)

        for line in edges:
            elem = AllplanBasisElements.ModelElement3D(props, line)

            attr_list = BuildingElementAttributeList()

            if attr_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_id, pmp_pare.replace("'", ""))

            if attr_wall_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_wall_id, pmp_pare.replace("'", ""))

            if attr_detall_id > 0:
                attr_list.add_attribute(attr_detall_id, "")

            if attr_forats_id > 0:
                attr_list.add_attribute(attr_forats_id, num_forats)

            if attr_nom_id > 0 and nom_value:
                attr_list.add_attribute(attr_nom_id, nom_value)

            if attr_neopre_id > 0:
                attr_list.add_attribute(attr_neopre_id, neopre_value)

            if attr_grosor_neopre_id > 0:
                attr_list.add_attribute(attr_grosor_neopre_id, grosor_length_value)

            if attr_list.get_attribute_list():
                elem.SetAttributes(attr_list.get_attribute_list())

            elements.append(elem)

        for line in edges:
            elem = AllplanBasisElements.ModelElement3D(props, line)

            attr_list = BuildingElementAttributeList()

            if attr_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_id, pmp_pare.replace("'", ""))

            if attr_wall_id > 0 and pmp_pare:
                attr_list.add_attribute(attr_wall_id, pmp_pare.replace("'", ""))

            if attr_detall_id > 0:
                attr_list.add_attribute(attr_detall_id, "")

            if attr_forats_id > 0:
                attr_list.add_attribute(attr_forats_id, num_forats)

            if attr_nom_id > 0 and nom_value:
                attr_list.add_attribute(attr_nom_id, nom_value)

            if attr_neopre_id > 0:
                attr_list.add_attribute(attr_neopre_id, neopre_value)

            if attr_grosor_neopre_id > 0:
                attr_list.add_attribute(attr_grosor_neopre_id, grosor_length_value)

            if attr_list.get_attribute_list():
                elem.SetAttributes(attr_list.get_attribute_list())

            elements.append(elem)

        return elements

    def create_individual_pythonparts_from_elements(self, elements_list: List[AllplanBasisElements.ModelElement3D],
                                                   start_point: AllplanGeo.Point3D = None,
                                                   end_point: AllplanGeo.Point3D = None,
                                                   angular_key: str = None,
                                                   invert_side: bool = None,
                                                   rotation_deg: float = None,
                                                   is_free_mode: bool = None,
                                                   is_modify: bool = False,
                                                   pmp_pare: str = None) -> List[PythonPart]:
        """
        Convierte una lista de ModelElement3D en PythonParts individuales.
        Cada elemento 3D se envuelve en su propia PythonPart para que GSI pueda leerlos individualmente.

        Args:
            elements_list: Lista de ModelElement3D creados
            start_point: Punto inicial de la línea (para reconstrucción en edición)
            end_point: Punto final de la línea (para reconstrucción en edición)
            angular_key: Clave del angular del catálogo
            invert_side: Si se invierte el lado del angular
            rotation_deg: Rotación en grados
            is_free_mode: Si está en modo libre

        Returns:
            Lista de PythonParts individuales
        """
        pythonparts_list = []
        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        for idx, element in enumerate(elements_list):
            try:
                common_props = element.GetCommonProperties() if hasattr(element, 'GetCommonProperties') else AllplanBaseElements.CommonProperties()
                if not hasattr(common_props, 'Layer') or common_props.Layer <= 0:

                    layer_id = AllplanBaseElements.LayerService.GetIDByShortName(ANG_LAYER, self.document)
                    common_props.Layer = layer_id

                attr_list = BuildingElementAttributeList()
                attr_pmp_id = getattr(self, "attr_pmp_pare_id", 0)
                attr_wall_id = getattr(self, "attr_pmp_wall_id", 0)
                attr_detall_id = getattr(self, "attr_pmp_fg_ang_detall_id", 0)
                attr_forats_id = getattr(self, "attr_pmp_fg_ang_forats_id", 0)
                attr_nom_id = getattr(self, "attr_pmp_fg_ang_nom_id", 0)
                attr_neopre_id = getattr(self, "attr_pmp_fg_angular_neopre_id", 0)
                attr_largo_neopre_id = getattr(self, "attr_pmp_fg_ang_neopre_id", 0)

                #  Usar pmp_pare pasado como parámetro (NO leer desde build_ele)
                wall_pare = pmp_pare.replace("'", "") if pmp_pare else ""
                if wall_pare and attr_pmp_id > 0:
                    attr_list.add_attribute(attr_pmp_id, wall_pare)

                if attr_wall_id and attr_wall_id > 0:
                    attr_list.add_attribute(attr_wall_id, wall_pare)

                if attr_detall_id > 0:
                    attr_list.add_attribute(attr_detall_id, "")

                if attr_forats_id > 0 and angular_key:
                    definition = ANGULAR_CATALOG.get(angular_key)
                    if definition:
                        num_forats = get_num_forats_from_definition(definition)
                        attr_list.add_attribute(attr_forats_id, num_forats)

                if attr_nom_id > 0 and angular_key:
                    nom_value = get_nom_from_angular_key(angular_key)
                    if nom_value:
                        attr_list.add_attribute(attr_nom_id, nom_value)

                if attr_neopre_id > 0:
                    lleva_neopreno = False
                    if hasattr(self.build_ele, 'SiLlevaNeopreno'):
                        lleva_neopreno = bool(self.build_ele.SiLlevaNeopreno.value)
                    neopre_value = "Si" if lleva_neopreno else "No"
                    attr_list.add_attribute(attr_neopre_id, neopre_value)

                if attr_largo_neopre_id > 0:
                    lleva_neopreno_local = False
                    if hasattr(self.build_ele, 'SiLlevaNeopreno'):
                        lleva_neopreno_local = bool(self.build_ele.SiLlevaNeopreno.value)

                    largo_neopre_value = ""
                    if lleva_neopreno_local and angular_key:
                        definition = ANGULAR_CATALOG.get(angular_key)
                        if definition:
                            largo_neopre_value = float(definition["length"])
                            attr_list.add_attribute(attr_largo_neopre_id, largo_neopre_value)

                attribute_list = attr_list.get_attribute_list()

                element_name = f"Angular_{str(wall_pare).replace(' ', '_')[:30]}_{idx}" if wall_pare else f"AngularElement_{idx}"

                views = [View2D3D([element])]
                params = {
                    'ElementIndex': idx,
                    'ElementType': type(element).__name__,
                    'Layer': common_props.Layer,
                    'Color': common_props.Color,
                    'Pen': common_props.Pen,
                    'Stroke': common_props.Stroke
                }

                if start_point is not None:
                    params['StartX'] = start_point.X
                    params['StartY'] = start_point.Y
                    params['StartZ'] = start_point.Z
                if end_point is not None:
                    params['EndX'] = end_point.X
                    params['EndY'] = end_point.Y
                    params['EndZ'] = end_point.Z
                if angular_key is not None:
                    params['AngularKey'] = angular_key
                if invert_side is not None:
                    params['InvertSide'] = bool(invert_side)
                if rotation_deg is not None:
                    params['Rotation'] = float(rotation_deg)
                if hasattr(self.build_ele, "RotacionEjeX"):
                    params['RotationX'] = self._get_angle_degrees("RotacionEjeX")
                if hasattr(self.build_ele, "RotacionEjeY"):
                    params['RotationY'] = self._get_angle_degrees("RotacionEjeY")
                if is_free_mode is not None:
                    params['FreeMode'] = bool(is_free_mode)

                #  Hash del elemento individual
                hash_value = create_element_hash(
                    "angular_elem",
                    stable=is_modify,
                    Index=idx
                )
                param_list = create_params_list_from_dict(params)

                pythonpart = PythonPart(
                    element_name,
                    parameter_list=param_list,
                    hash_value=hash_value,
                    python_file=python_file_name,
                    views=views,
                    common_props=common_props,
                    attribute_list=attribute_list
                )

                pythonparts_list.append(pythonpart)

            except Exception as e:
                import traceback
                traceback.print_exc()
                continue

        return pythonparts_list


    def execute(self) -> CreateElementResult:
        """Dispatcher principal: separa CREATE y EDIT en funciones independientes."""

        # VERIFICACION DE QUE ID SE PRECARGA
        print("========== EXECUTE START ==========")
        print(f"[EXECUTE] Angulares.py version: {ANGULARES_SCRIPT_VERSION}")
        print("[EXECUTE]  z_unique y pmp_pare existen en build_ele (con Persistent>MODEL_AND_FAVORITE)")

        if self.state == CANCEL:
            return CreateElementResult()

        # Detectar modo
        if hasattr(self.build_ele, 'IsModify'):
            is_modify = self.build_ele.IsModify
        else:
            is_modify = getattr(self, 'is_modification_mode', False)

        print("[MODE]", "EDIT" if is_modify else "CREATE")

        self.is_editing_existing = is_modify

        # Dispatcher: separar CREATE y EDIT completamente
        if is_modify:
            return self._execute_modify()
        else:
            return self._execute_create()

    def _execute_create(self) -> CreateElementResult:
        """Lógica completa de CREACIÓN: detecta muro, calcula PMP_PARE, genera z_unique, crea geometrías."""
        print("[CREATE] Iniciando creación...")

        #  z_unique: asegurar que esté en build_ele
        self.build_ele.z_unique.value = random.random() * 3600
        # if hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value"):
        #     if not self.build_ele.z_unique.value or self.build_ele.z_unique.value == 0:
        #         self.build_ele.z_unique.value = random.random() * 3600
        z_unique = float(self.build_ele.z_unique.value) if (hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value") and self.build_ele.z_unique.value) else 0.0

        #  Obtener línea del interactor
        if not self.line_result.input_line:
            print("[CREATE]  ERROR: No hay línea para crear geometría")
            return CreateElementResult([])

        start_point = self.line_result.input_line.StartPoint
        end_point = self.line_result.input_line.EndPoint

        #  Guardar puntos en build_ele
        if hasattr(self.build_ele, 'PuntoInicial'):
            self.build_ele.PuntoInicial.value = start_point
        if hasattr(self.build_ele, 'PuntoFinal'):
            self.build_ele.PuntoFinal.value = end_point

        #  Obtener definición
        definition = ANGULAR_CATALOG.get(self.build_ele.TipoAngular.value, None)
        if definition is None:
            print("[CREATE]  ERROR: No se encontró definición para TipoAngular")
            return CreateElementResult([])

        try:
            separation = max(0.0, float(self.build_ele.SeparacionAngulares.value))
        except (ValueError, TypeError):
            separation = 10.0

        #  Detectar muro → calcular PMP_PARE → guardar en build_ele
        wall_pare = None
        wall = self._get_wall_element() if hasattr(self, '_get_wall_element') else None
        if wall:
            try:
                wall_id = get_wall_ifc_id(wall)
                if wall_id:
                    wall_pare = wall_id
                    print(f"[CREATE] PMP_PARE calculado desde muro: {wall_pare}")
            except Exception as e:
                print(f"[CREATE]  Error obteniendo material del muro: {e}")

        if not wall_pare:
            wall_pare = "MURO_NO_DEFINIDO"

        #  Guardar pmp_pare en build_ele (ahora existe en .pyp con Persistent>MODEL_AND_FAVORITE)
        if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, 'value'):
            try:
                self.build_ele.pmp_pare.value = wall_pare.replace("'", "")
                print(f"[CREATE]  pmp_pare guardado en build_ele: '{wall_pare}'")
            except Exception as e:
                print(f"[CREATE]  ERROR al guardar pmp_pare en build_ele: {e}")

        print(f"[CREATE]  PMP_PARE también se guardará en build_ele y en atributos del elemento")

        # Crear geometría siempre usando build_ele (ya restaurado o recién asignado)
        start_point = self.build_ele.PuntoInicial.value if hasattr(self.build_ele, "PuntoInicial") else start_point
        end_point = self.build_ele.PuntoFinal.value if hasattr(self.build_ele, "PuntoFinal") else end_point
        separation = max(0.0, float(getattr(self.build_ele.SeparacionAngulares, "value", 10.0) or 10.0)) if hasattr(self.build_ele, "SeparacionAngulares") else separation
        rot_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else 0.0
        rotation_deg = rot_val.GetDeg() if hasattr(rot_val, "GetDeg") else float(rot_val) if rot_val is not None else 0.0
        invert_side = bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else False
        distribution_type = self._get_distribution_type()
        print(f"[CREATE][INPUTS] tipo={self.build_ele.TipoAngular.value} distribucion={distribution_type} sep={separation} inv={invert_side} rot={rotation_deg}")

        geometries, edges = self._create_geometries_for_distribution(
            distribution_type=distribution_type,
            definition=definition,
            start_point=start_point,
            end_point=end_point,
            invert_side=invert_side,
            rotation_deg=rotation_deg,
            gap=separation,
        )

        if not geometries:
            print("[CREATE]  ERROR: No se pudo generar geometría")
            return CreateElementResult([])

        #  Guardar last_geometries para preview/on_cancel
        self.last_geometries = list(geometries)
        self.last_definition_key = self.build_ele.TipoAngular.value

        #  Obtener IDs de atributos
        self.attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "pmp_pare")
        self.attr_pmp_wall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_WALL_ID")
        self.attr_pmp_fg_ang_detall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_DETALL")
        self.attr_pmp_fg_ang_forats_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_FORATS")
        self.attr_pmp_fg_ang_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_NOM")
        self.attr_pmp_fg_angular_neopre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANGULAR_NEOPRE")
        self.attr_pmp_fg_ang_neopre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_NEOPRE")

        #  create_angulars() - SIEMPRE aplica PMP_PARE
        self.elements = self.create_angulars(geometries, edges, definition, pmp_pare=wall_pare)


        if not self.elements:
            print("[CREATE]  ERROR: No se crearon elementos")
            return CreateElementResult([])

        #  Guardar parámetros geométricos
        angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, 'TipoAngular') else None
        invert_side = self.build_ele.InvertirAngular.value if hasattr(self.build_ele, 'InvertirAngular') else False
        rotation_deg = self.build_ele.RotacionManual.value if hasattr(self.build_ele, 'RotacionManual') else 0.0

        #  create_individual_pythonparts_from_elements() - is_modify=False → hash random
        individual_pythonparts = self.create_individual_pythonparts_from_elements(
            self.elements,
            start_point=start_point,
            end_point=end_point,
            angular_key=angular_key,
            invert_side=invert_side,
            rotation_deg=rotation_deg,
            is_free_mode=self.is_free_mode,
            is_modify=False,
            pmp_pare=wall_pare
        )

        if not individual_pythonparts:
            print("[CREATE]  ERROR: No se crearon PythonParts individuales")
            return CreateElementResult([])

        # param_list: mínimo geométrico + SiLlevaNeopreno/GrosorNeopreno + SavedState (para precarga en EDIT)
        punto_inicial = self.build_ele.PuntoInicial.value if hasattr(self.build_ele, "PuntoInicial") else start_point
        punto_final = self.build_ele.PuntoFinal.value if hasattr(self.build_ele, "PuntoFinal") else end_point
        tipo_angular_key = self.build_ele.TipoAngular.value if hasattr(self.build_ele, "TipoAngular") else ""
        distribution_type = self._get_distribution_type()
        libre = getattr(self, "is_free_mode", True)
        rot_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else 0.0
        rot = rot_val.GetDeg() if hasattr(rot_val, "GetDeg") else float(rot_val) if rot_val is not None else 0.0
        invertido = bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else False
        lleva_neopreno = bool(getattr(self.build_ele.SiLlevaNeopreno, "value", False)) if hasattr(self.build_ele, "SiLlevaNeopreno") else False

        saved_state_str = self._serialize_state_to_json()

        print("[CHECK] z_unique antes del group:", z_unique)
        global_params = self._build_group_global_params(
            z_unique=z_unique,
            total_elements=len(individual_pythonparts),
            punto_inicial=punto_inicial,
            punto_final=punto_final,
            tipo_angular_key=tipo_angular_key,
            distribution_type=distribution_type,
            separation=separation,
            libre=libre,
            rot_deg=rot,
            invertido=invertido,
            lleva_neopreno=lleva_neopreno,
            pmp_pare_value=wall_pare or "",
            saved_state_str=saved_state_str or "",
        )
        print(f"[CREATE] global_params: z_unique={global_params.get('z_unique')}, SiLlevaNeopreno={lleva_neopreno}, SavedState={len(saved_state_str or '')} chars")

        group_hash = create_element_hash(
            "angular_group",
            stable=False,  # CREATE = random
            z_unique=z_unique
        )

        param_list = create_params_list_from_dict(global_params)
        z_unique_in_param_list = any('z_unique' in p for p in param_list)
        if not z_unique_in_param_list:
            print("[CREATE]  ERROR CRÍTICO: z_unique NO está en param_list antes de crear grupo")

        # Solo vive en param_list del grupo
        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        pythonpart_group = PythonPartGroup(
            "Angulares",
            param_list,
            group_hash,
            python_file_name,
            individual_pythonparts,
        )

        model_elem_list = pythonpart_group.create()

        if not model_elem_list or len(model_elem_list) == 0:
            print("[CREATE]  ERROR: model_elem_list está vacío")
            return CreateElementResult([])

        # z_unique está en param_list del grupo; pmp_pare y PMP_* se aplican como atributos en create_angulars

        #------------verificacion de creacion id -----------------------------
        print("========== BEFORE GROUP CREATE ==========")
        print(f"z_unique antes de group: {z_unique} (solo en param_list, no en build_ele)")

        #  Guardar longitud de línea
        line_vector = vector_from_points(start_point, end_point)
        final_line_length = line_vector.GetLength()
        self.build_ele.LongitudLinea.value = final_line_length

        #  Crear handles
        handles = create_handles(
            self.build_ele,
            self.line_result.input_line,
            None if self.is_free_mode else self.face_normal,
            None if self.is_free_mode else self.face_point
        )

        #  Crear connect_to_ele si hay muro
        connect_to_ele = ConnectToElements()
        if hasattr(self.build_ele, 'MuroGUID') and self.build_ele.MuroGUID.value:
            connect_to_ele.connection_elements.append(self.build_ele.MuroGUID.value)

        # Guardar SavedState al final (CREATE siempre)
        self._save_state_to_build_ele()

        #  Return final
        print(f"[CREATE]  Creación completada: {len(model_elem_list)} elementos")
        print(f"[CREATE] ========== param_list ANTES DEL RETURN (CREATE) ==========")
        for idx, param_str in enumerate(param_list):
            print(f"[CREATE] param_list[{idx}]: {param_str.strip()}")
        print(f"[CREATE] ==========================================================")
        return CreateElementResult(
            elements=model_elem_list,
            handles=handles,
            placement_point=AllplanGeo.Point3D(0.0, 0.0, 0.0),
            connect_to_ele=connect_to_ele,
            uuid_parameter_name="PythonPartUUID",
            multi_placement=distribution_type == DISTRIBUTION_INDIVIDUAL
        )


    def _execute_modify(self) -> CreateElementResult:
        """Lógica completa de EDICIÓN: lee TODO desde build_ele, NO detecta muro, NO recalcula PMP_PARE, hash estable."""
        print("[EDIT] Iniciando edición...")
        print("========== EXECUTE MODIFY ==========")

        # 1Solo usar SavedState si faltan puntos (para no pisar cambios del usuario).
        print("[EDIT] ========== LEER ESTADO (build_ele primero, SavedState solo si faltan puntos) ==========")
        start_point = None
        end_point = None
        tipo_angular_key = ""
        separation = 10.0
        distribution_type = self._get_distribution_type()
        libre = getattr(self, "is_free_mode", True)
        rot = 0.0
        invertido = False
        lleva_neopreno = False
        largo_neopre_value = 240
        wall_pare = ""

        start_point = getattr(self.build_ele.PuntoInicial, "value", None) if hasattr(self.build_ele, "PuntoInicial") else None
        end_point = getattr(self.build_ele.PuntoFinal, "value", None) if hasattr(self.build_ele, "PuntoFinal") else None
        # Fallback a SavedState SOLO si falta algo
        if start_point is None or end_point is None:
            saved_state_str = (self.build_ele.SavedState.value or "").strip() if hasattr(self.build_ele, "SavedState") and hasattr(self.build_ele.SavedState, "value") else ""
            state = parse_saved_state(saved_state_str) if saved_state_str else {}
            p0_fallback = saved_state_to_point3d(state, "p0")
            p1_fallback = saved_state_to_point3d(state, "p1")
            if p0_fallback is not None and p1_fallback is not None:
                start_point, end_point = p0_fallback, p1_fallback
                if hasattr(self.build_ele, "PuntoInicial"):
                    self.build_ele.PuntoInicial.value = start_point
                if hasattr(self.build_ele, "PuntoFinal"):
                    self.build_ele.PuntoFinal.value = end_point
                print(f"[EDIT] Puntos desde SavedState (fallback): {start_point} → {end_point}")
            else:
                print("[EDIT] ERROR: No hay puntos en build_ele ni en SavedState")
                return CreateElementResult(elements=[], handles=[], elements_to_delete=None)
        else:
            print(f"[EDIT] Puntos desde build_ele (paleta): {start_point} → {end_point}")
        # Esta es la línea geométrica final (de build_ele o fallback SavedState)
        if getattr(self, "line_result", None):
            self.line_result.input_line = AllplanGeo.Line3D(start_point, end_point)

        # Resto de parámetros desde build_ele
        tipo_angular_key = getattr(self.build_ele.TipoAngular, "value", "").strip() if hasattr(self.build_ele, "TipoAngular") else ""

        #  Obtener definición (tipo_angular_key ya viene de SavedState o build_ele)
        definition = ANGULAR_CATALOG.get(tipo_angular_key, None)
        if not definition:
            print("[EDIT]  ERROR: No se encontró definición para TipoAngular")
            return CreateElementResult(elements=[], handles=[], elements_to_delete=None)

        if self._is_individual_distribution():
            if not (self.face_normal and self.face_point):
                self._load_face_info_from_properties()

            current_line = AllplanGeo.Line3D(start_point, end_point)
            current_length = vector_from_points(start_point, end_point).GetLength()
            center = AllplanGeo.Point3D(
                (start_point.X + end_point.X) / 2.0,
                (start_point.Y + end_point.Y) / 2.0,
                (start_point.Z + end_point.Z) / 2.0,
            )
            if not self._is_manual_z_enabled() and hasattr(self.build_ele, "ValorZIndividual"):
                if abs(float(getattr(self.build_ele.ValorZIndividual, "value", 0.0) or 0.0)) <= 1e-6 and abs(center.Z) > 1e-6:
                    self.build_ele.ValorZIndividual.value = center.Z

            if current_length < 1e-6:
                piece_length = definition.get("piece_length", definition.get("length", 0.0))
                x_dir = self._get_individual_horizontal_axis_on_face()
                if piece_length > 0 and x_dir and x_dir.GetLength() > 1e-6:
                    current_line = AllplanGeo.Line3D(
                        move_point(center, x_dir, -piece_length / 2.0),
                        move_point(center, x_dir, piece_length / 2.0),
                    )

            current_line = self._project_line_to_individual_vertical_face(current_line)
            start_point = current_line.StartPoint
            end_point = current_line.EndPoint
            if hasattr(self.build_ele, "PuntoInicial"):
                self.build_ele.PuntoInicial.value = start_point
            if hasattr(self.build_ele, "PuntoFinal"):
                self.build_ele.PuntoFinal.value = end_point
            if getattr(self, "line_result", None):
                self.line_result.input_line = current_line


        try:
            separation = max(0.0, float(getattr(self.build_ele.SeparacionAngulares, "value", 10.0) or 10.0))
        except (ValueError, TypeError):
            separation = 10.0
        rot_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else 0.0
        rot = rot_val.GetDeg() if hasattr(rot_val, "GetDeg") else float(rot_val) if rot_val is not None else 0.0
        invertido = bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else False
        lleva_neopreno = bool(getattr(self.build_ele.SiLlevaNeopreno, "value", False)) if hasattr(self.build_ele, "SiLlevaNeopreno") else False
        largo_neopre_value = float(definition["length"])
        wall_pare = str(getattr(self.build_ele.pmp_pare, "value", "") or "").strip().replace("'", "") if hasattr(self.build_ele, "pmp_pare") else ""
        if not wall_pare:
            wall_pare = "SIN_PARE"
        if hasattr(self.build_ele, "angular_libre") and hasattr(self.build_ele.angular_libre, "value"):
            v = self.build_ele.angular_libre.value
            libre = v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes")
        else:
            libre = True

        # LongitudLinea = distancia entre p0 y p1 (siempre calculado desde PuntoInicial/PuntoFinal, no persistido)
        if hasattr(self.build_ele, "LongitudLinea") and start_point is not None and end_point is not None:
            try:
                self.build_ele.LongitudLinea.value = vector_from_points(start_point, end_point).GetLength()
            except Exception:
                pass

        print("[EDIT] ========== LEYENDO z_unique y pmp_pare (después de SavedState) ==========")
        z_unique = 0.0
        if hasattr(self.build_ele, "z_unique") and hasattr(self.build_ele.z_unique, "value"):
            try:
                z_unique = float(self.build_ele.z_unique.value)
            except (ValueError, TypeError):
                z_unique = 0.0
        print(f"[EDIT]  z_unique final: {z_unique}")

        if not wall_pare:
            wall_pare = ""
            if hasattr(self.build_ele, "pmp_pare") and hasattr(self.build_ele.pmp_pare, "value"):
                try:
                    wall_pare = str(self.build_ele.pmp_pare.value).strip().replace("'", "")
                except Exception:
                    pass
            if not wall_pare:
                wall_pare = "SIN_PARE"
            print(f"[EDIT]  pmp_pare: '{wall_pare}'")

        # EDIT: SIEMPRE intentar leer el hash existente. z_unique NO decide nada.
        existing_group_hash = None
        if hasattr(self.build_ele, "get_hash"):
            try:
                existing_group_hash = self.build_ele.get_hash()
                if existing_group_hash:
                    print(f"[EDIT] Hash del grupo existente: {existing_group_hash[:20]}...")
            except Exception as e:
                print(f"[EDIT] ERROR al obtener hash existente: {e}")
        print("[EDIT] ==========================================================")

        # Actualizar is_free_mode (variable interna)
        self.is_free_mode = libre

        print(f"[EDIT]  z_unique para hash: {z_unique}")

        # Crear geometría con start_point/end_point desde SavedState (NO volver a leer build_ele para la línea)
        separation = max(0.0, float(getattr(self.build_ele.SeparacionAngulares, "value", 10.0) or 10.0)) if hasattr(self.build_ele, "SeparacionAngulares") else separation
        rot_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else 0.0
        rot = rot_val.GetDeg() if hasattr(rot_val, "GetDeg") else float(rot_val) if rot_val is not None else 0.0
        invertido = bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else False

        # ===== LOG DE VERIFICACIÓN: INPUTS ANTES DE GENERAR GEOMETRÍA =====
        print("[EDIT][INPUTS] p0=", start_point, "p1=", end_point)
        distribution_type = self._get_distribution_type()
        print("[EDIT][INPUTS] tipo=", tipo_angular_key, "distribucion=", distribution_type, "sep=", separation, "inv=", invertido, "rot=", rot)

        geometries, edges = self._create_geometries_for_distribution(
            distribution_type=distribution_type,
            definition=definition,
            start_point=start_point,
            end_point=end_point,
            invert_side=invertido,
            rotation_deg=rot,
            gap=separation,
        )

        # ===== LOG DE VERIFICACIÓN: RESULTADO DE GEOMETRÍA =====
        print("[EDIT][GEOM] count=", len(geometries) if geometries else 0)

        if not geometries:
            print("[EDIT] ERROR: no geometries, NO reemplazar")
            return CreateElementResult(elements=[], handles=[], elements_to_delete=None)

        #  Obtener IDs de atributos
        self.attr_pmp_pare_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "pmp_pare")
        self.attr_pmp_wall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_WALL_ID")
        self.attr_pmp_fg_ang_detall_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_DETALL")
        self.attr_pmp_fg_ang_forats_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_FORATS")
        self.attr_pmp_fg_ang_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_NOM")
        self.attr_pmp_fg_angular_neopre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANGULAR_NEOPRE")
        self.attr_pmp_fg_ang_neopre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.document, "PMP_FG_ANG_NEOPRE")

        #  create_angulars() - Pasa is_modify=True (aunque ya no importa, se aplica PMP_PARE igual)
        self.elements = self.create_angulars(geometries, edges, definition, pmp_pare=wall_pare)

        if not self.elements:
            print("[EDIT]  ERROR: No se crearon elementos")
            return CreateElementResult(elements=[], handles=[], elements_to_delete=None)

        #  Parámetros geométricos ya vienen de SavedState o build_ele (tipo_angular_key, invertido, rot)

        #  create_individual_pythonparts_from_elements() - IMPORTANTE: is_modify=True
        #  Pasar pmp_pare desde param_list (NO desde build_ele)
        individual_pp = self.create_individual_pythonparts_from_elements(
            self.elements,
            start_point=start_point,
            end_point=end_point,
            angular_key=tipo_angular_key or None,
            invert_side=invertido,
            rotation_deg=rot,
            is_free_mode=self.is_free_mode,
            is_modify=True,
            pmp_pare=wall_pare
        )

        if not individual_pp:
            print("[EDIT]  ERROR: No se crearon PythonParts individuales")
            return CreateElementResult(elements=[], handles=[], elements_to_delete=None)

        #  HASH DEL GROUP — En EDIT solo usar hash existente. NUNCA recalcular.
        if existing_group_hash:
            group_hash = existing_group_hash
            print(f"[EDIT] Usando hash del grupo existente (estable): {group_hash[:20]}...")
            print(f"[EDIT] Hash completo: {group_hash}")
        else:
            print("[EDIT] ERROR CRÍTICO: no se pudo obtener hash del grupo existente")
            return CreateElementResult(
                elements=[],
                handles=[],
                elements_to_delete=None
            )

        punto_inicial_edit = self.build_ele.PuntoInicial.value if hasattr(self.build_ele, "PuntoInicial") else start_point
        punto_final_edit = self.build_ele.PuntoFinal.value if hasattr(self.build_ele, "PuntoFinal") else end_point
        tipo_key_edit = self.build_ele.TipoAngular.value if hasattr(self.build_ele, "TipoAngular") else tipo_angular_key
        distribution_type_edit = self._get_distribution_type()
        libre_edit = getattr(self, "is_free_mode", True)
        rot_edit_val = getattr(self.build_ele.RotacionManual, "value", 0.0) if hasattr(self.build_ele, "RotacionManual") else rot
        rot_edit = rot_edit_val.GetDeg() if hasattr(rot_edit_val, "GetDeg") else float(rot_edit_val) if rot_edit_val is not None else 0.0
        invertido_edit = bool(getattr(self.build_ele.InvertirAngular, "value", False)) if hasattr(self.build_ele, "InvertirAngular") else invertido
        lleva_neopreno_edit = bool(getattr(self.build_ele.SiLlevaNeopreno, "value", False)) if hasattr(self.build_ele, "SiLlevaNeopreno") else lleva_neopreno


        # Justo antes de armar global_params: serializar SavedState desde build_ele
        saved_state_edit = self._serialize_state_to_json()
        wall_pare_edit = str(getattr(self.build_ele.pmp_pare, "value", "") or "").strip().replace("'", "") if hasattr(self.build_ele, "pmp_pare") else wall_pare

        print("[CHECK] z_unique antes del group:", z_unique)
        global_params = self._build_group_global_params(
            z_unique=z_unique,
            total_elements=len(individual_pp),
            punto_inicial=punto_inicial_edit,
            punto_final=punto_final_edit,
            tipo_angular_key=tipo_key_edit,
            distribution_type=distribution_type_edit,
            separation=separation,
            libre=libre_edit,
            rot_deg=rot_edit,
            invertido=invertido_edit,
            lleva_neopreno=lleva_neopreno_edit,
            pmp_pare_value=wall_pare_edit or "",
            saved_state_str=saved_state_edit or "",
        )
        print(f"[EDIT] global_params: z_unique={global_params.get('z_unique')}, SiLlevaNeopreno={lleva_neopreno_edit}, SavedState={len(saved_state_edit or '')} chars")

        param_list = create_params_list_from_dict(global_params)
        print(f"[EDIT] ========== param_list ANTES DEL RETURN (EDIT) ==========")
        for idx, param_str in enumerate(param_list):
            print(f"[EDIT] param_list[{idx}]: {param_str.strip()}")
        print(f"[EDIT] ==========================================================")
        python_file_name = self.build_ele.pyp_file_name if hasattr(self.build_ele, 'pyp_file_name') else ""

        pythonpart_group = PythonPartGroup(
            "Angulares",
            param_list,
            group_hash,
            python_file_name,
            individual_pp
        )

        model_elem_list = pythonpart_group.create()

        if not model_elem_list or len(model_elem_list) == 0:
            print("[EDIT]  ERROR: model_elem_list está vacío")
            return CreateElementResult(elements=[], handles=[], elements_to_delete=None)

        # Lo que persiste para la próxima edición es el param_list del grupo (SavedState ya va dentro de global_params).
        self._save_state_to_build_ele()

        #  HANDLES
        line = AllplanGeo.Line3D(start_point, end_point)
        handles = create_handles(
            self.build_ele,
            line,
            None if self.is_free_mode else self.face_normal,
            None if self.is_free_mode else self.face_point
        )

        #  RETURN FINAL: igual que Neoprenos — NO pasar elements_to_delete; el framework reemplaza por UUID.
        #  Si se pasa elements_to_delete, Allplan borra el grupo y luego añade el nuevo; un fallo en ese flujo hace que el angular desaparezca.
        print(f"[EDIT]  Edición completada: {len(model_elem_list)} elementos")
        return CreateElementResult(
            elements=model_elem_list,
            handles=handles,
            placement_point=AllplanGeo.Point3D(0, 0, 0),
            uuid_parameter_name="PythonPartUUID"
        )


    def on_cancel_function(self) -> OnCancelFunctionResult:
        return OnCancelFunctionResult.CREATE_ELEMENTS

