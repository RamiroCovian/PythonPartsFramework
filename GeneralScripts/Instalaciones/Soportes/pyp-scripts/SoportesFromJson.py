import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import unicodedata


# ------------------------------------------------------------
# Modelo de datos
# ------------------------------------------------------------


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


def get_default_json_path() -> Path:
    """
    Devuelve la ruta por defecto del JSON de pruebas, en la misma carpeta
    que este script (carpeta `Soportes`).
    """
    return Path(__file__).with_name("Soportes_mock.json")


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


# ------------------------------------------------------------
# Utilidades para polilínea / 3D
# (cálculos genéricos, independientes de Allplan)
# ------------------------------------------------------------


def compute_segment_length(support: SupportJson) -> float:
    """
    Devuelve la longitud de la polilínea (distancia entre posicion1 y posicion2).
    Esta longitud se puede usar, por ejemplo, para `set_length` en `SupportModel`.
    """
    (x1, y1, z1) = support.posicion1
    (x2, y2, z2) = support.posicion2
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def build_preview_polyline_points(
    supports: List[SupportJson],
) -> List[Tuple[float, float, float]]:
    """
    Genera una lista de puntos para una previsualización en polilínea.

    Para cada soporte se crean dos puntos: `posicion1` y `posicion2`.
    Un consumidor externo (otro script de Allplan) puede usar esta lista para
    crear líneas / puntos sin necesidad de generar el 3D completo.
    """
    points: List[Tuple[float, float, float]] = []
    for s in supports:
        points.append(s.posicion1)
        points.append(s.posicion2)
    return points


if __name__ == "__main__":
    # Pequeña prueba manual al ejecutar el script fuera de Allplan.
    path = get_default_json_path()
    ensure_mock_json(path)
    supports = load_supports_from_json(path)
    print(f"Se han leído {len(supports)} supports desde {path}")
    for s in supports:
        print(s)
        print("  Longitud segmento:", compute_segment_length(s))
