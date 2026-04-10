# PolylineLib/utils.py
# -*- coding: utf-8 -*-
"""
Utilitarios: JSON_PATH, helpers para escritorio, color por path, flush stdout.
"""
import os, sys, math
import importlib, pkgutil
import json
import unicodedata

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .models import SegmentInfo, SupportJson


def import_pythonpart_class(class_name):
    """
    Busca clases PythonPart dentro de cualquier subcarpeta de /instalaciones/
    """
    for module in pkgutil.iter_modules():
        try:
            mod = importlib.import_module(module.name)
            if hasattr(mod, class_name):
                return getattr(mod, class_name)
        except:
            pass

    raise ImportError(f"No se encontró el PythonPart: {class_name}")

def _flush():
    try: sys.stdout.flush()
    except Exception: pass

def desktop_dir() -> str:
    """Directorio Desktop del usuario (crea si no existe)."""
    up = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    d  = os.path.join(up, "Desktop")
    os.makedirs(d, exist_ok=True)
    print("[PolylineLib] usando Desktop:", d)
    return d

def make_color_from_path(path: int) -> int:
    try:
        p = int(path)
    except Exception:
        p = 1
    return max(1, min(p, 255))

def dividir_polyline_en_segmentos(self, elem_2d):
        """
        Divide un ModelElement2D (Polyline2D) en segmentos individuales
        Retorna una lista de ModelElement2D, uno por cada segmento
        """
        # Obtener la polyline
        polyline = elem_2d.GetGeometryObject()
        puntos = polyline.Points

        # Lista para almacenar los nuevos elementos
        segmentos = []

        # Crear un segmento por cada par de puntos consecutivos
        for i in range(len(puntos) - 1):
            punto_inicio = puntos[i]
            punto_fin = puntos[i + 1]

            # Crear nueva polyline de 2 puntos (un segmento)
            nueva_polyline = AllplanGeo.Polyline2D()
            nueva_polyline += punto_inicio
            nueva_polyline += punto_fin

            # Crear nuevo ModelElement2D con las mismas propiedades
            nuevo_elem = AllplanBasisElements.ModelElement2D(
                elem_2d.GetCommonProperties(),
                nueva_polyline
            )

            # Copiar propiedades adicionales
            nuevo_elem.SetPatternCurveProperties(elem_2d.GetPatternCurveProperties())
            nuevo_elem.SetEndSymbolsProperties(elem_2d.GetEndSymbolsProperties())

            segmentos.append(nuevo_elem)

        return segmentos

def modify_brep_en_polyline(self, elem_2d_or_points, elem_3d, end_point=None, altura_z=None):

        """
        Centra y alinea un ModelElement3D con la dirección de una polyline o dos puntos.
        Ahora además permite modificar la altura (Z) del objeto resultante.

        Parámetros:
            elem_2d_or_points  -> ModelElement2D o Point2D
            elem_3d            -> ModelElement3D a transformar
            punto_fin          -> si el primer argumento es un Point2D se requiere el segundo
            altura_z           -> (float) nueva posición Z (si None, se conserva la original)
        """
        # =====================================
        # 1) Determinar puntos y dirección base
        # =====================================
        if isinstance(elem_2d_or_points, AllplanBasisElements.ModelElement2D):
            polyline = elem_2d_or_points.GetGeometryObject()
            start_point = polyline.Points[0] # type: ignore
            end_point = polyline.Points[-1] # type: ignore
        else:
            start_point = elem_2d_or_points
            if end_point is None:
                raise ValueError("Debe proporcionar punto_fin cuando se pasa un Point2D")

        # Centro de la polyline en XY
        centro_x = (start_point.X + end_point.X) / 2.0
        centro_y = (start_point.Y + end_point.Y) / 2.0

        # Calcular ángulo 2D en XY
        delta_x = end_point.X - start_point.X
        delta_y = end_point.Y - start_point.Y
        angulo_grados = math.degrees(math.atan2(delta_y, delta_x))

        # =====================================
        # 2) Obtener el BRep original y su centro
        # =====================================
        brep = elem_3d.GetGeometryObject()
        err, vertices = brep.GetVertices()

        centro_brep_x = sum(v.X for v in vertices) / len(vertices)
        centro_brep_y = sum(v.Y for v in vertices) / len(vertices)
        centro_brep_z = sum(v.Z for v in vertices) / len(vertices)

        # Si altura_z es None, se usa el centro_z original.
        z_final = altura_z if altura_z else centro_brep_z

        # =====================================
        # 3) Crear matriz de transformación
        # =====================================
        matriz = AllplanGeo.Matrix3D()

        # A) Llevar el BRep a su origen
        matriz.Translate(AllplanGeo.Vector3D(-centro_brep_x, -centro_brep_y, -centro_brep_z))

        # B) Rotar alrededor del eje Z
        eje_rotacion = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0),
            AllplanGeo.Point3D(0, 0, 1)
        )
        matriz_rot = AllplanGeo.Matrix3D()
        matriz_rot.SetRotation(eje_rotacion, AllplanGeo.Angle.FromDeg(angulo_grados))
        matriz = matriz * matriz_rot

        # C) Trasladar el BRep al centro XY y altura final Z

        matriz.Translate(AllplanGeo.Vector3D(centro_x, centro_y, z_final))

        # =====================================
        # 4) Aplicar la transformación y crear el nuevo elemento
        # =====================================
        nuevo_brep = AllplanGeo.Transform(brep, matriz)

        return AllplanBasisElements.ModelElement3D(
            elem_3d.GetCommonProperties(),
            nuevo_brep
        )

def modify_lenght_brep(self, model_element, new_length):
        """
        Modifica la longitud (eje X) de un elemento 3D representado por BRep3D.

        Asume que la longitud es la dimensión máxima a lo largo del eje X,
        y que se extiende desde X=0 hasta la longitud máxima.
        """

        # 1. Acceder a la sección BRep3D
        # (Esto depende de cómo se estructura realmente tu objeto 'model_element'
        # en tu entorno de desarrollo, aquí se simula la estructura)
        geo = model_element.GetGeometryObject()

        initial_vertices = geo.GetVertices()
        # initial_vertices = brep_data.Vertices
        # 2. Parsear los vértices (Simulación: convertimos la lista de strings/tuples a una lista de tuplas de floats)
        # Ejemplo de parsing simplificado: (0, 0, 75) -> (0.0, 0.0, 75.0)
        # parsed_vertices = []

        # 3. Determinar la longitud actual (máxima X)
        longitud_actual = max(v.X for v in initial_vertices[1]) # Debería ser 1500

        # Si la nueva longitud es igual a la actual, no hacemos nada
        if new_length == longitud_actual:
            print(f"La longitud ya es {new_length}. No se requiere modificación.")
            return model_element

        # 4. Modificar los vértices
        nuevo_bloque_vertices = []

        for v in initial_vertices[1]:
            print(v)
            # Si la coordenada X es la longitud máxima actual (1500),
            # se reemplaza por la nueva longitud.
            if v.X == longitud_actual:
                v = AllplanGeo.Point3D(new_length, v.Y, v.Z)

            nuevo_bloque_vertices.append(v)

        print(nuevo_bloque_vertices)


        # 5. Actualizar el elemento (Simulación de actualización)
        print(f"Longitud original: {longitud_actual}")
        print(f"Nueva longitud: {new_length}")
        print("--- Vértices Actualizados ---")

        # Crear nuevo BRep vacío
        # Calcula dimensiones desde tus vértices
        p_min = nuevo_bloque_vertices[6]  # vértice mínimo
        p_max = nuevo_bloque_vertices[2]  # vértice máximo

        # Crear paralelepípedo directamente
        polyhedron = AllplanGeo.Polyhedron3D.CreateCuboid(p_min, p_max)

        # Convertir a BRep
        err, nuevo_brep = AllplanGeo.CreateBRep3D(polyhedron)

        nuevo_model = AllplanBasisElements.ModelElement3D(
            model_element.GetCommonProperties(),
            nuevo_brep
        )

        return nuevo_model

def get_distance_between_points(self, points: list) -> float:

        first_point = points[0]
        last_point = points[-1]
                # pts2 = poly
        # p1 = AllplanGeo.Point2D(pts2.X, pts2.Y)
        result = first_point.GetDistance(last_point)
        return result

def compute_segment_length(support: SupportJson) -> float:
    """
    Devuelve la longitud de la polilínea (distancia entre posicion1 y posicion2).
    Esta longitud se puede usar, por ejemplo, para `set_length` en `SupportModel`.
    """
    (x1, y1, z1) = support.posicion1
    (x2, y2, z2) = support.posicion2
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    return (dx * dx + dy * dy + dz * dz) ** 0.5

def _as_tuple_3(values) -> Tuple[float, float, float]:
    """Convierte una lista del JSON en una tupla (x, y, z) de float."""
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        raise ValueError(f"posicion inválida (se esperan 3 valores): {values!r}")
    x, y, z = values
    return float(x), float(y), float(z)

def _normalize_token(raw: str) -> str:
    normalized = unicodedata.normalize("NFKD", raw)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().strip()
    return normalized

def _normalize_support_type(raw_type: str) -> str:
    token = _normalize_token(raw_type)
    if token == "omega":
        return "Omega"
    if token == "zeta":
        return "Zeta"
    if token == "cinta":
        return "Cinta"
    return raw_type.strip()

def _normalize_subtype(raw_subtype: str) -> str:
    """
    Normaliza subtipos a etiquetas semánticas canónicas.

    Ejemplos de salida:
    - "Venti.(SVP)" -> "Ventilación"
    - "Electr./Clima(SEP)" -> "Clima"
    - "VARIFIX" -> "Varifix"
    """
    token = _normalize_token(raw_subtype)
    mapping = {
        "ventilacion": "Ventilación",
        "venti.(svp)": "Ventilación",
        "venti svp": "Ventilación",
        "svp": "Ventilación",
        "clima": "Clima",
        "electricidad": "Electricidad",
        "agua": "Agua",
        "saneamiento": "Saneamiento",
        "varifix": "Varifix",
        "electr./clima(sep)": "Clima",
        "electr./clima": "Clima",
    }
    if token in mapping:
        return mapping[token]

    if "varifix" in token:
        return "Varifix"
    if "vent" in token or "svp" in token:
        return "Ventilación"
    if "electr" in token:
        return "Electricidad"
    if "clima" in token:
        return "Clima"
    if "agua" in token:
        return "Agua"
    if "sane" in token:
        return "Saneamiento"
    return raw_subtype.strip()

def _normalize_surface(raw_surface: str) -> str:
    """Normaliza `superficie` a 'Liso' o 'Perforado'."""
    token = _normalize_token(raw_surface)
    mapping = {
        "liso": "Liso",
        "perforado": "Perforado",
    }
    return mapping.get(token, raw_surface.strip())

def _get_required_float(item: dict, names: Tuple[str, ...], label: str) -> float:
    """
    Devuelve el primer valor numérico encontrado en `names`.
    Lanza ValueError si falta el dato obligatorio.
    """
    for name in names:
        if name in item:
            value = item[name]
            if value is None:
                break
            return float(value)
    raise ValueError(f"falta dato obligatorio '{label}'")

def _get_optional_float(
    item: dict, names: Tuple[str, ...], label: str
) -> Optional[float]:
    """
    Devuelve el primer valor numérico opcional encontrado en `names`.
    - Si no existe ninguna clave, devuelve None.
    - Acepta strings con coma decimal (ej.: "90,0").
    """
    for name in names:
        if name in item:
            value = item[name]
            if value is None:
                return None
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                value = value.replace(",", ".")
            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"valor inválido en '{label}': {item[name]!r}"
                ) from exc
    return None

# ------------------------------------------------------------
# Carga / mock de JSON
# ------------------------------------------------------------
def get_default_json_path(name_folder: str | None = "Ventilacion") -> Path:
    """
    Busca 'Soportes_mock.json' en una carpeta hermana dentro de 'Instalaciones'.
    Si la carpeta o el archivo no existen, retorna la ruta en la carpeta local.
    """
    # 1. Definimos la raíz común (Instalaciones/)
    # Estamos en: .../Instalaciones/Polylib/utils.py
    # .parents[1] nos sube a: .../Instalaciones/
    root_dir = Path(__file__).resolve().parents[1]

    # 2. Construimos la ruta deseada
    if name_folder:
        target_path = root_dir / name_folder / f"soporte_{name_folder.lower()}.json"

    # 3. Validación de error: Si no existe el archivo en esa carpeta...
    if not target_path.exists():
        # ...pasamos a la ruta anterior (la misma carpeta del script)
        fallback_path = Path(__file__).with_name("Soportes_mock.json")
        return fallback_path

    return target_path

def ensure_mock_json(path: Path | None = None) -> Path:
    """
    Si no existe el JSON indicado, crea un mock mínimo de pruebas con
    la estructura acordada.
    """
    json_path = Path(path) if path is not None else get_default_json_path()

    if json_path.exists():
        return json_path

    # Contenido de ejemplo (se puede editar a mano desde Allplan / explorador)
    mock_data = {
        "soportes": [
            {
                "tipo": "OMEGA",
                "subtipo": "Agua",
                "superficie": "Perforado",
                "posicion1": [0.0, 0.0, 0.0],
                "posicion2": [1000.0, 0.0, 0.0],
                "angulo_inclinacion": 0.0,
                "cota_a": 110.0,
                "cota_b": 300.0,
            }
        ]
    }

    try:
        json_path.write_text(json.dumps(mock_data, indent=4), encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"No se pudo crear el JSON de mock en {json_path}") from exc

    return json_path

def load_supports_from_json(path: str | Path | None = None) -> List[SupportJson]:
    """
    Lee el archivo JSON (real o de mock) y devuelve una lista de `SupportJson`.

    Reglas de validación:
    - Son obligatorios: `tipo`, `subtipo`, `superficie`, `posicion1`, `posicion2`,
      `cota_a`, `cota_b`.
    - Para Varifix, `cota_a` y `cota_b` deben ser > 0.
    - Para Zeta, `cota_a` puede ser 0 pero `cota_b` debe ser > 0.
    - Si un soporte es inválido, se informa por consola y se ignora.

    Compatibilidad:
    - Se aceptan temporalmente nombres legacy (`supports`, `type`, etc.).

    Si `path` es None se usa el JSON por defecto en `Soportes/Soportes_mock.json`.
    Si el archivo no existe, se crea automáticamente un mock válido.
    """
    json_path = Path(path) if path is not None else get_default_json_path()

    # Crear mock si no existe
    if not json_path.exists():
        json_path = ensure_mock_json(json_path)

    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"No se pudo leer el JSON {json_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido en {json_path}: {exc}") from exc

    supports_raw = raw.get("soportes")
    if supports_raw is None:
        # Compatibilidad temporal con versiones antiguas del JSON
        supports_raw = raw.get("supports", [])
    supports: List[SupportJson] = []

    print(f"[SoportesFromJson] JSON path: {json_path}")
    print(f"[SoportesFromJson] Total soportes recibidos: {len(supports_raw)}")

    for idx_item, item in enumerate(supports_raw, start=1):
        try:
            print(f"[SoportesFromJson] RAW soporte #{idx_item}: {item!r}")

            # Clave oficial: `angulo_inclinacion`.
            # Compatibilidad temporal: equivalentes en inglés, typo histórico y clave con acento.
            angulo_inclinacion = _get_optional_float(
                item,
                (
                    "angulo_inclinacion",
                    "ángulo_inclinacion",
                    "inclinacion_angulo",
                ),
                "angulo_inclinacion",
            )
            tipo_raw = str(item.get("tipo", item.get("type", ""))).strip()
            subtipo_raw = str(item.get("subtipo", item.get("subtype", ""))).strip()

            if not tipo_raw:
                raise ValueError("falta dato obligatorio 'tipo'")
            if not subtipo_raw:
                raise ValueError("falta dato obligatorio 'subtipo'")

            surface_raw = str(item.get("superficie", item.get("surface", ""))).strip()
            if not surface_raw:
                # Tolerancia para cargas incompletas: si no llega superficie,
                # asumimos Perforado para no invalidar todo el soporte.
                surface_raw = "Perforado"
                print(
                    "[SoportesFromJson] Aviso soporte #{}: 'superficie' vacía; se usa 'Perforado' por defecto".format(
                        idx_item
                    )
                )

            tipo = _normalize_support_type(tipo_raw)
            subtipo = _normalize_subtype(subtipo_raw)
            superficie = _normalize_surface(surface_raw)
            if superficie not in ("Liso", "Perforado"):
                raise ValueError(
                    "valor inválido en 'superficie' (permitidos: 'Liso'/'Perforado')"
                )

            cota_a = _get_required_float(item, ("cota_a", "height_a"), "cota_a")
            cota_b = _get_required_float(
                item, ("cota_b", "height_b", "length_b"), "cota_b"
            )

            if tipo == "Omega" and subtipo in ("Varifix", "Agua", "Saneamiento"):
                if cota_a <= 0.0 or cota_b <= 0.0:
                    raise ValueError(
                        "para soporte Varifix, 'cota_a' y 'cota_b' deben ser > 0"
                    )

            if tipo == "Zeta":
                if cota_a < 0.0:
                    raise ValueError("para soporte Zeta, 'cota_a' no puede ser < 0")
                if cota_b <= 0.0:
                    raise ValueError("para soporte Zeta, 'cota_b' debe ser > 0")

            if tipo == "Cinta":
                if cota_b <= 0.0:
                    raise ValueError("para soporte Cinta, 'cota_b' debe ser > 0")

            support = SupportJson(
                tipo=tipo,
                subtipo=subtipo,
                superficie=superficie,
                posicion1=_as_tuple_3(item.get("posicion1", item.get("position1"))),
                posicion2=_as_tuple_3(item.get("posicion2", item.get("position2"))),
                angulo_inclinacion=angulo_inclinacion,
                cota_a=cota_a,
                cota_b=cota_b,
            )
            print(
                "[SoportesFromJson] PARSED soporte #{}: tipo='{}', subtipo='{}', "
                "superficie='{}', angulo_inclinacion={}, "
                "posicion1={}, posicion2={}, cota_a={}, cota_b={}".format(
                    idx_item,
                    support.tipo,
                    support.subtipo,
                    support.superficie,
                    support.angulo_inclinacion,
                    support.posicion1,
                    support.posicion2,
                    support.cota_a,
                    support.cota_b,
                )
            )
        except Exception as exc:
            # En caso de error en un soporte concreto, lo ignoramos pero lo dejamos trazado.
            print(f"[SoportesFromJson] Soporte inválido en JSON: {item!r} -> {exc}")
            continue

        if not support.tipo:
            print(f"[SoportesFromJson] Soporte sin tipo, se ignora: {item!r}")
            continue

        supports.append(support)

    return supports

class ElementSerializer:

    @staticmethod
    def serialize_layers(data) -> str:
        """
        Convierte self.applied_layers a una cadena JSON.
        Al ser tipos nativos (str, int), json.dumps funciona directo.
        """
        try:
            return json.dumps(data)
        except Exception as e:
            print(f"[ERROR] Serializando layers: {e}")
            return ""

    @staticmethod
    def deserialize_layers(json_data) -> Dict:
        """
        Restaura self.applied_layers desde una cadena JSON.
        """
        if not json_data:
            return {}

        try:
            data = json.loads(json_data)
        except Exception as e:
            print(f"[ERROR] Deserializando layers: {e}")
            data = {}

        return data

    @staticmethod
    def serialize_attributes(default_attributes) -> str:
        """
        Convierte self.custom_attributes (objetos Allplan) a una estructura JSON (diccionarios simples).
        """
        import json

        serializable_data = {}

        for key, attr_list in default_attributes.items():
            serialized_list = []
            for attr in attr_list:
                attr_data = {}

                # Detectar tipo y extraer datos
                if isinstance(attr, AllplanBaseElements.AttributeString):
                    attr_data = {
                        "id": attr.Id,
                        "val": attr.Value,
                        "type": "string"
                    }
                elif isinstance(attr, AllplanBaseElements.AttributeInteger):
                    attr_data = {
                        "id": attr.Id,
                        "val": attr.Value,
                        "type": "integer"
                    }
                elif isinstance(attr, AllplanBaseElements.AttributeDouble):
                    attr_data = {
                        "id": attr.Id,
                        "val": attr.Value,
                        "type": "double"
                    }
                # Añadir más tipos si usas (ej: Date)
                if attr_data:
                    serialized_list.append(attr_data)

            serializable_data[key] = serialized_list

        return json.dumps(serializable_data)

    @staticmethod
    def deserialize_attributes(json_data: str) -> Dict:
        """
        Reconstruye self.custom_attributes desde el JSON, creando objetos Allplan nuevamente.
        """
        import json

        if not json_data:
            default_attributes = {}
            return default_attributes

        try:
            raw_data = json.loads(json_data)
            default_attributes = {}

            for key, raw_list in raw_data.items():
                reconstructed_list = []
                for item in raw_list:
                    attr_obj = None
                    attr_id = item["id"]
                    attr_val = item["val"]
                    attr_type = item["type"]

                    # Reconstruir el objeto Allplan según su tipo original
                    if attr_type == "string":
                        attr_obj = AllplanBaseElements.AttributeString(attr_id, attr_val)
                    elif attr_type == "integer":
                        attr_obj = AllplanBaseElements.AttributeInteger(attr_id, int(attr_val))
                    elif attr_type == "double":
                        attr_obj = AllplanBaseElements.AttributeDouble(attr_id, float(attr_val))

                    if attr_obj:
                        reconstructed_list.append(attr_obj)

                if reconstructed_list:
                    default_attributes[key] = reconstructed_list

        except Exception as e:
            print(f"[ERROR] Fallo al deserializar atributos: {e}")
            default_attributes = {}

        return default_attributes

    @staticmethod
    def serialize_attrs(attrs_dict):
        serialized = {}
        for modo, elementos in attrs_dict.items():
            serialized[int(modo)] = {}
            for elem_type, attr_list in elementos.items():
                list_data = []
                for attr in attr_list:
                    list_data.append({
                        "id": attr.Id,
                        "value": attr.Value,
                        "type": type(attr).__name__
                    })
                serialized[int(modo)][elem_type] = list_data

        return json.dumps(serialized, indent=4)

    @staticmethod
    def deserialize_attrs(json_str):
        if not json_str:
            return {}

        data = json.loads(json_str)
        deserialized = {}

        for modo, elementos in data.items():
            deserialized[int(modo)] = {}
            for elem_type, attr_list in elementos.items():
                allplan_attrs = []
                for item in attr_list:
                    # Mapeo de tipos para reconstruir objetos Allplan
                    tipo = item["type"]
                    id_attr = item["id"]
                    val = item["value"]

                    if tipo == "AttributeString":
                        attr = AllplanBaseElements.AttributeString(id_attr, str(val))
                    elif tipo == "AttributeDouble":
                        attr = AllplanBaseElements.AttributeDouble(id_attr, float(val))
                    elif tipo == "AttributeInteger":
                        attr = AllplanBaseElements.AttributeInteger(id_attr, int(val))
                    else:
                        continue # O manejar otros tipos si existen

                    allplan_attrs.append(attr)

                deserialized[int(modo)][elem_type] = allplan_attrs

        return deserialized

    @staticmethod
    def serialize_generated_elements(data_groups):
        """Convierte el array de arrays de elementos en datos serializables."""
        serialized_master_list = []

        for path_group in data_groups:
            serialized_path = []
            for element in path_group:
                # 1. Limpieza de booleanos y parámetros
                clean_params = {}
                if 'params' in element:
                    for k, v in element['params'].items():
                        clean_params[k] = v if not isinstance(v, bool) else (True if v else False)

                # 2. Construcción del ítem serializable
                pos = element['position']
                item = {
                    'type': element['type'],
                    'key': list(element['key']),  # Tupla a Lista para JSON
                    'layer': element['layer'],
                    'path_idx': element['path_idx'],
                    'params': clean_params,
                    'seq_id': element.get('seq_id', 0),
                    'position': [pos.X, pos.Y, pos.Z] # Point3D a Lista
                }

                if 'seg_idx' in element: item['seg_idx'] = element['seg_idx']

                serialized_path.append(item)

            serialized_master_list.append(serialized_path)

        return serialized_master_list

    @staticmethod
    def serialize_generated_elements_v1(data):
        """Convierte la lista de elementos en datos serializables para Allplan/JSON."""
        serialized_list = []

        for element in data:
            # Limpieza profunda de booleanos en params para evitar el error 'true' vs 'True'
            clean_params = {}
            if 'params' in element:
                for k, v in element['params'].items():
                    # Forzamos que los booleanos sean tipos nativos de Python antes de serializar
                    if isinstance(v, bool):
                        clean_params[k] = True if v else False
                    else:
                        clean_params[k] = v

            item = {
                'type': element['type'],
                'key': list(element['key']), # Convertimos tupla a lista para JSON
                'layer': element['layer'],
                'path_idx': element['path_idx'],
                'params': element['params'],
                'seq_id': element.get('seq_id', 0)
            }
            if 'seg_idx' in element: item['seg_idx'] = element['seg_idx']
            if 'vertex_idx' in element: item['vertex_idx'] = element['vertex_idx']

            pos = element['position']
            item['position'] = [pos.X, pos.Y, pos.Z]

            serialized_list.append(item)

        return serialized_list

    @staticmethod
    def deserialize_generated_elements(master_data_list):
        """Reconstruye la estructura de array de arrays con objetos AllplanGeo."""
        generated_elements_hierarchy = []
        if not master_data_list:
            return []

        for path_data in master_data_list:
            current_path_elements = []
            for data in path_data:
                try:
                    # 1. Reconstruir Posición
                    pos_list = data['position']
                    position = AllplanGeo.Point3D(pos_list[0], pos_list[1], pos_list[2])

                    # 2. Reconstruir Geometría según tipo
                    geometry = None
                    params = data.get('params', {})

                    if data['type'] == 'tubo':
                        p1, p2 = params['start_point'], params['end_point']
                        geometry = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(p1[0], p1[1], p1[2]),
                            AllplanGeo.Point3D(p2[0], p2[1], p2[2])
                        )
                    elif data['type'] in ['codo', 'union']:
                        # Si marker_size no existe, usamos fallback de línea (punto)
                        m_size = params.get('marker_size')
                        if m_size is None:
                            geometry = AllplanGeo.Line3D(position, position)
                        else:
                            axis = AllplanGeo.AxisPlacement3D(
                                AllplanGeo.Point3D(position.X - m_size/2,
                                                 position.Y - m_size/2,
                                                 position.Z - m_size/2)
                            )
                            geometry = AllplanGeo.Polyhedron3D.CreateCuboid(axis, m_size, m_size, m_size)

                    # 3. Ensamblar Diccionario de Elemento
                    element = {
                        'type': data['type'],
                        'key': tuple(data['key']), # Volver a Tupla
                        'geometry': geometry,
                        'position': position,
                        'layer': data['layer'],
                        'path_idx': data['path_idx'],
                        'params': params,
                        'seq_id': data.get('seq_id', 0)
                    }
                    if 'seg_idx' in data: element['seg_idx'] = data['seg_idx']

                    current_path_elements.append(element)

                except Exception as e:
                    print(f"[ERROR] Deserializando elemento en ruta {data.get('path_idx')}: {e}")
                    continue

            generated_elements_hierarchy.append(current_path_elements)

        return generated_elements_hierarchy

    @staticmethod
    def deserialize_generated_elements_v1(data_list):
        """Reconstruye los objetos de AllplanGeo con manejo de tipos."""
        generated_elements = []
        if not data_list:
            return []

        for data in data_list:
            try:
                # 1. Reconstruir Posición
                pos_list = data['position']
                position = AllplanGeo.Point3D(pos_list[0], pos_list[1], pos_list[2])

                # 2. Reconstruir Geometría
                geometry = None
                params = data.get('params', {})

                if data['type'] == 'tubo':
                    p1 = params['start_point']
                    p2 = params['end_point']
                    geometry = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(p1[0], p1[1], p1[2]),
                        AllplanGeo.Point3D(p2[0], p2[1], p2[2])
                    )

                elif data['type'] in ['codo', 'union']:
                    # Aquí es donde fallaba por el booleano 'is_fallback_line'
                    is_fallback = params.get('is_fallback_line', False)
                    if is_fallback:
                        geometry = AllplanGeo.Line3D(position, position)
                    else:
                        m_size = params.get('marker_size', 60.0)
                        axis = AllplanGeo.AxisPlacement3D(
                            AllplanGeo.Point3D(position.X - m_size/2,
                                            position.Y - m_size/2,
                                            position.Z - m_size/2)
                        )
                        geometry = AllplanGeo.Polyhedron3D.CreateCuboid(axis, m_size, m_size, m_size)

                # 3. Ensamblar
                element = {
                    'type': data['type'],
                    'key': tuple(data['key']), # Volver a convertir a tupla para consistencia
                    'geometry': geometry,
                    'position': position,
                    'layer': data['layer'],
                    'path_idx': data['path_idx'],
                    'params': params,
                    'seq_id': data.get('seq_id', 0)
                }

                if 'seg_idx' in data: element['seg_idx'] = data['seg_idx']
                # if 'vertex_idx' in data: element['vertex_idx'] = data['vertex_idx']

                generated_elements.append(element)
            except Exception as e:
                print(f"Error procesando elemento: {e}")
                continue

        return generated_elements

    @staticmethod
    def serialize_global_numbers(global_numbers: dict) -> str:
        """
        Convierte el diccionario de numeración de grupos en una cadena JSON
        para su almacenamiento en el archivo .pyp o .xml de Allplan.
        """
        try:
            if not global_numbers:
                return ""
            # Serializamos a JSON para mantener la estructura de diccionario
            return json.dumps(global_numbers)
        except Exception as ex:
            print(f"Error serializando global_group_numbers: {ex}")
            return ""

    @staticmethod
    def deserialize_global_numbers(serialized_data: str) -> dict:
        """
        Recupera el diccionario de numeración desde una cadena JSON.
        Si la cadena es inválida o está vacía, devuelve un diccionario nuevo.
        """
        try:
            if not serialized_data or serialized_data == "":
                return {}

            # Cargamos el JSON de vuelta a un objeto Python
            data = json.loads(serialized_data)

            # Opcional: Aseguramos que las llaves sean strings y valores sean ints
            return {str(k): int(v) for k, v in data.items()}

        except (json.JSONDecodeError, ValueError, TypeError) as ex:
            print(f"Error deserializando global_group_numbers: {ex}")
            return {}

    @staticmethod
    def serialize_persistent_metadata(persistent_metadata: dict) -> str:
        """
        Convierte el diccionario de metadata persistente en una cadena JSON
        para su almacenamiento en el archivo .pyp o .xml de Allplan.
        Cada valor es un SegmentInfo que se serializa como dict.
        """
        try:
            if not persistent_metadata:
                return ""
            serializable = {}
            for key, seg_info in persistent_metadata.items():
                if isinstance(seg_info, SegmentInfo):
                    serializable[key] = {
                        "diameter":          seg_info.diameter,
                        "section_type":      seg_info.section_type,
                        "system":            seg_info.system,
                        "label":             seg_info.label,
                        "distribution_type": seg_info.distribution_type,
                        "water_type":        seg_info.water_type,
                        "face":              seg_info.face,
                    }
                else:
                    # Si por alguna razón ya es un dict, lo guardamos tal cual
                    serializable[key] = seg_info
            return json.dumps(serializable)
        except Exception as ex:
            print(f"Error serializando persistent_metadata: {ex}")
            return ""

    @staticmethod
    def deserialize_persistent_metadata(serialized_data: str) -> dict:
        """
        Recupera el diccionario de metadata persistente desde una cadena JSON.
        Reconstruye cada entrada como un objeto SegmentInfo.
        Si la cadena es inválida o está vacía, devuelve un diccionario vacío.
        """
        try:
            if not serialized_data:
                return {}

            raw = json.loads(serialized_data)
            result: dict[str, SegmentInfo] = {}

            for key, value in raw.items():
                if not isinstance(value, dict):
                    print(f"[WARN] persistent_metadata[{key}] no es un dict, omitiendo.")
                    continue
                result[key] = SegmentInfo(
                    diameter=          value.get("diameter", ""),
                    section_type=      value.get("section_type", ""),
                    system=            value.get("system", ""),
                    label=             value.get("label", ""),
                    distribution_type= value.get("distribution_type", ""),
                    water_type=        value.get("water_type", "") or None,
                    face=              value.get("face", ""),
                )

            return result

        except (json.JSONDecodeError, ValueError, TypeError, KeyError) as ex:
            print(f"Error deserializando persistent_metadata: {ex}")
            return {}

