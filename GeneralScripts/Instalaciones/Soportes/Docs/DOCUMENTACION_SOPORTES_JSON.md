## Soportes desde JSON

Este documento describe el flujo completo para generar soportes en Allplan a partir de un fichero JSON externo:

- Lectura y validación del JSON (`SoportesFromJson.py`).
- Generación de la geometría 3D (`Soportes.py` / `SupportModel`).
- Posicionamiento y orientación en 3D usando `position1` y `position2`.

---

### 1. Archivos implicados

- **`Soportes.py`**  
  Script principal de generación del soporte 3D (`SupportModel`) que Allplan llama desde el PythonPart.

- **`SoportesFromJson.py`**  
  Script auxiliar que:
  - Lee un fichero JSON externo con la definición de los soportes.
  - Valida y convierte los datos a un modelo de Python (`SupportJson`).
  - Calcula longitudes de los tramos.
  - Genera listas de puntos para previsualización en polilínea.

---

### 2. Formato del JSON

El fichero JSON esperado tiene la siguiente estructura general:

```json
{
  "supports": [
    {
      "type": "OMEGA",
      "subtype": "VARIFIX",
      "position1": [x, y, z],
      "position2": [x, y, z],
      "inclination_angle_deg": 5.0,
      "height_a": 110.0,
      "length_b": 30.5
    }
  ]
}
```

- **`type`**: tipo de soporte (por ejemplo, `"OMEGA"` o `"ZETA"`).
- **`subtype`**: variante dentro del tipo (por ejemplo, `"VARIFIX"`, `"Venti.(SVP)"`, `"Electr./Clima(SEP)"`, etc.).
- **`position1`**: primer punto \([x, y, z]\) de la posición del soporte (origen del soporte en 3D).
- **`position2`**: segundo punto \([x, y, z]\) que define la dirección completa del soporte (en planta y en Z).
- **`inclination_angle_deg`**: (opcional) Ángulo de inclinación del soporte en grados: orientación de punta a punta para mantenerse paralelo al IS (elemento PythonPart posicionado en la polilínea). Si no se indica, la inclinación se deduce de `position1` y `position2`.
- **`height_a`**: altura vertical del soporte (se usa para `HEIGHT_VERTICAL`).
- **`length_b`**: longitud nominal del soporte en el eje X local (se usa para `LEN_X_HORIZONTAL`, con un descuento de 6 mm).

#### Ubicación del JSON

Por defecto se utiliza un archivo llamado **`Soportes_mock.json`** en la misma carpeta que `SoportesFromJson.py` (`Soportes`).  

Si este archivo **no existe**, el propio script `SoportesFromJson.py` genera un JSON de **ejemplo** con un soporte OMEGA–VARIFIX, que se puede editar a mano para hacer pruebas.

⚠️ Importante: si el archivo ya existe, **no se sobreescribe automáticamente** al ejecutar `SoportesFromJson.py`. Para regenerarlo con un nuevo mock hay que:

- Borrar manualmente `Soportes_mock.json`, o
- Editar directamente el contenido del JSON.

---

### 3. API del script `SoportesFromJson.py`

#### 3.1. Dataclass `SupportJson`

Cada soporte se representa internamente como:

```python
SupportJson(
    type: str,
    subtype: str,
    position1: (float, float, float),
    position2: (float, float, float),
    inclination_angle_deg: Optional[float] = None,  # ángulo de inclinación (paralelo al IS)
    height_a: float,
    length_b: float,
)
```

#### 3.2. Funciones principales

- **`get_default_json_path() -> Path`**  
  Devuelve la ruta por defecto del JSON (`Soportes_mock.json` en la carpeta `Soportes`).

- **`ensure_mock_json(path: Path | None = None) -> Path`**  
  - Si el fichero indicado no existe, crea un JSON de ejemplo con un soporte.  
  - Devuelve siempre la ruta final al archivo JSON.

- **`load_supports_from_json(path: str | Path | None = None) -> List[SupportJson]`**  
  - Lee el JSON (o crea el mock si no existe).  
  - Valida y convierte los datos en una lista de `SupportJson`.  
  - Ignora entradas inválidas, escribiendo un mensaje por consola.

- **`compute_segment_length(support: SupportJson) -> float`**  
  Devuelve la longitud de la polilínea entre `position1` y `position2`.  
  Útil, por ejemplo, para cálculos auxiliares.

- **`build_preview_polyline_points(supports: List[SupportJson]) -> List[tuple[float, float, float]]`**  
  Genera una lista de puntos \[(p1, p2, p1, p2, ...)\] con las posiciones de todos los soportes.  
  Estos puntos se pueden usar para una previsualización en polilínea (líneas y/o puntos) antes de generar el 3D.

---

### 4. Prueba rápida desde consola

Se puede comprobar el funcionamiento básico del script sin entrar en Allplan:

1. Abrir una consola en la carpeta `Soportes`.
2. Ejecutar:

   ```bash
   python SoportesFromJson.py
   ```

3. El script:
   - Creará `Soportes_mock.json` si no existe.
   - Leerá el archivo JSON.
   - Mostrará por consola los soportes leídos y la longitud de cada tramo.

Si esta prueba funciona, la lectura/parsing del JSON y los cálculos básicos están correctos.

---

### 5. Integración con `Soportes.py` (SupportModel)

Esta sección describe cómo `Soportes.py` utiliza la información del JSON para crear y posicionar los soportes en Allplan.

#### 5.1. Importación del módulo JSON

En la cabecera de `Soportes.py` se intenta importar `SoportesFromJson.py` de forma robusta:

- Primero: `from SoportesFromJson import SupportJson, load_supports_from_json, compute_segment_length`.
- Si falla por `ImportError`, se prueba: `from .SoportesFromJson import ...`.
- Si ambas fallan, se deja un `load_supports_from_json` vacío (devuelve lista vacía) y se continúa con el comportamiento clásico sin JSON.

En el log de Allplan pueden aparecer mensajes como:

- `"[Soportes] SoportesFromJson importado como módulo suelto."`
- `"[Soportes] SoportesFromJson importado como módulo de paquete."`
- `"[Soportes] Aviso: no se pudo importar SoportesFromJson: ..."`

#### 5.2. Flujo de `create_element`

La función principal de creación en `Soportes.py` es:

```python
def create_element(build_ele, doc):
    model_list = []

    # 1) Intentar leer soportes desde JSON externo
    json_supports = load_supports_from_json()

    if json_supports:
        # Crear un soporte 3D por cada entrada en el JSON
        ...
        return (model_list, [], [])

    # 2) Fallback: comportamiento clásico si no hay JSON
    support = SupportModel(build_ele, doc)
    model_list = support.build()
    return (model_list, [], [])
```

Comportamiento:

- **Si el JSON contiene datos** (`json_supports` no está vacío):
  - Se crea un `SupportModel` por cada `SupportJson`.
  - Para cada uno se aplican tipo/subtipo, dimensiones y orientación según el JSON.
  - Se devuelven todos los soportes creados desde el JSON.
- **Si el JSON está vacío o no se puede leer**, se usa el comportamiento clásico:
  - Se crea un único soporte según los parámetros del PythonPart (paleta).

#### 5.3. Selección de tipo y subtipo (`type` / `subtype`)

Dentro de `SupportModel` se utiliza el método:

- **`apply_json_definition(self, support_json)`**

Que hace lo siguiente:

- Lee `support_json.type` y lo normaliza (`"OMEGA"` → `"Omega"`, `"ZETA"` → `"Zeta"`).
- Si el tipo existe en `PARAMS`, actualiza `self.type_support`.
- Lee `support_json.subtype` y, con una heurística, lo mapea a los textos de `MAP_SUPPORT`:
  - Para `Omega`:
    - Contiene `"VARIFIX"` → `"Varifix"`.
    - Contiene `"ELECTR"` o `"CLIMA"` → `"Electr./Clima(SEP)"`.
    - Contiene `"VENT"` o `"SVP"` → `"Venti.(SVP)"`.
  - Para `Zeta`:
    - Contiene `"110X200"` → `"110x200mm"`.
    - Contiene `"205X200"` → `"205x200mm"`.
    - Contiene `"205X152"` / `"205X152.26"` → `"205x152.26mm"`.
    - Contiene `"0MM"` → `"0mm"`.
- Protege el índice (`idx`) contra valores fuera de rango y actualiza:
  - `self.support_idx`.
  - `self.param = dict(PARAMS[self.type_support][idx])`.

En el log se puede ver algo como:

- `"[SupportModel] Tipo de soporte seleccionado: 'Omega'"`
- `"[SupportModel] Omega/ Zeta: support_key='Venti.(SVP)', idx=0"`
- `"[SupportModel] Configuración desde JSON: type='Omega', subtype='VARIFIX', idx=2"`

#### 5.4. Dimensiones desde el JSON (`length_b` / `height_a`)

Después de aplicar el tipo/subtipo, `create_element` ajusta las dimensiones:

- **Longitud del soporte**:
  - Se lee `length_b` del JSON.
  - Se calcula `length_mm = length_b - 6.0`.
  - Si `length_mm > 0`, se llama a:
    - `support.set_length(length_mm)`
  - Internamente, `set_length` cambia `self.param["LEN_X_HORIZONTAL"]` para usar esta longitud.

- **Altura vertical**:
  - Se lee `height_a` del JSON.
  - Si `height_a > 0`, se asigna:
    - `self.param["HEIGHT_VERTICAL"] = float(height_a)`

En resumen:

- `length_b` → `LEN_X_HORIZONTAL = length_b - 6 mm`.
- `height_a` → `HEIGHT_VERTICAL = height_a`.

#### 5.5. Orientación y posición en 3D (`position1` / `position2` / `inclination_angle_deg`)

El soporte se genera inicialmente en coordenadas locales (eje X, origen en (0,0,0)).  
Después, se orienta y se coloca en el espacio usando `position1` y `position2`. Opcionalmente, el JSON puede incluir **`inclination_angle_deg`**: el ángulo de inclinación del soporte (orientación de punta a punta) para mantenerse paralelo al IS (elemento PythonPart en la polilínea). Si no se indica, la inclinación se deduce del vector entre ambos puntos.

- Se extraen:

  ```python
  (x1, y1, z1) = position1
  (x2, y2, z2) = position2
  ```

- Se calcula el vector 3D entre ambos puntos:

  ```python
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1
  direction_vec = Vector3D(dx, dy, dz)  # salvo el caso casi nulo
  ```

- Se crea una matriz de rotación que alinea el eje X local `(1, 0, 0)` con ese vector:

  ```python
  mat_rot = Matrix3D()
  start_dir = Vector3D(1.0, 0.0, 0.0)
  mat_rot.SetRotation(start_dir, direction_vec)
  ```

- Se crea una matriz de traslación al punto inicial `position1`:

  ```python
  mat_tra = Matrix3D()
  mat_tra.SetTranslation(Vector3D(x1, y1, z1))
  ```

- Se compone la transformación final:

  ```python
  placement_mat = mat_tra * mat_rot
  ```

- Para cada `ModelElement3D` creado por `support.build()`:

  ```python
  elem.GeometryObject = AllplanGeometry.Transform(elem.GeometryObject, placement_mat)
  ```

Efectos:

- `position1` → punto inicial (origen) del soporte en 3D.
- `position2` → define la **dirección completa** del soporte, incluyendo:
  - Ángulo en planta (diferencias en X e Y).
  - Inclinación en Z (diferencia en Z).
- El soporte queda alineado con la recta que une `position1` y `position2`, con la longitud que marca `length_b - 6 mm`.

#### 5.6. Comportamiento en caso de error

En cualquier error al leer JSON, aplicar dimensiones u orientar el soporte, se escriben avisos en el log:

- Problemas leyendo el JSON:
  - `"[Soportes] Aviso: error leyendo JSON externo de soportes: ..."`
- Problemas con longitud/altura:
  - `"[Soportes] Aviso: error aplicando longitud/altura desde JSON, se mantienen valores por defecto: ..."`
- Problemas de orientación:
  - `"[Soportes] Aviso: error orientando soporte según position1/position2: ..."`

En todos estos casos, el script intenta seguir adelante usando los valores por defecto de `SupportModel` para no romper el flujo de trabajo en Allplan.

---

### 6. Resumen funcional

- **Entrada**: fichero JSON `Soportes_mock.json` con una lista de soportes (`supports`).
- **Procesado**:
  - `SoportesFromJson.py` lee y valida el JSON → `SupportJson`.
  - `Soportes.py`:
    - Ajusta tipo y subtipo (`type`/`subtype`) → `PARAMS` / `MAP_SUPPORT`.
    - Ajusta longitud (`length_b - 6 mm`) y altura (`height_a`).
    - Genera la geometría local del soporte (`SupportModel.build()`).
    - Orienta y coloca el soporte de `position1` a `position2` en 3D.
- **Fallback**: si no hay JSON, se usa el comportamiento original del PythonPart (paleta).

## Soportes desde JSON

Este documento describe el uso del script `SoportesFromJson.py` para leer soportes desde un fichero JSON externo, generar una previsualización en polilínea y preparar los datos necesarios para crear el 3D en Allplan.

---

### 1. Archivos implicados

- **`Supports.py`**  
  Script principal de generación del soporte 3D (`SupportModel`).

- **`SoportesFromJson.py`**  
  Script auxiliar que:
  - Lee un fichero JSON externo con la definición de los soportes.
  - Valida y convierte los datos a un modelo de Python (`SupportJson`).
  - Calcula longitudes de los tramos.
  - Genera listas de puntos para previsualización en polilínea.

---

### 2. Formato del JSON

El fichero JSON esperado tiene la siguiente estructura general:

```json
{
  "supports": [
    {
      "type": "OMEGA",
      "subtype": "VARIFIX",
      "position1": [x, y, z],
      "position2": [x, y, z],
      "inclination_angle_deg": 5.0,
      "height_a": 110.0,
      "length_b": 30.5
    }
  ]
}
```

- **`type`**: tipo de soporte (por ejemplo, `"OMEGA"` o `"Zeta"`).
- **`subtype`**: variante dentro del tipo (por ejemplo, `"VARIFIX"`, `"VENTI.(SVP)"`, etc.).
- **`position1`**: primer punto \([x, y, z]\) de la posición del soporte.
- **`position2`**: segundo punto \([x, y, z]\) de la posición del soporte.
- **`height_a`** y **`length_b`**: alturas y longitudes adicionales (actualmente solo se almacenan, se pueden usar más adelante).

#### Ubicación del JSON

Por defecto se utiliza un archivo llamado **`Supports_mock.json`** en la misma carpeta que `SoportesFromJson.py` (`Soportes`).  

Si este archivo **no existe**, el propio script genera un JSON de **ejemplo** con un soporte OMEGA–VARIFIX, que se puede editar a mano para hacer pruebas.

---

### 3. API del script `SoportesFromJson.py`

#### 3.1. Dataclass `SupportJson`

Cada soporte se representa internamente como:

```python
SupportJson(
    type: str,
    subtype: str,
    position1: (float, float, float),
    position2: (float, float, float),
    inclination_angle_deg: Optional[float] = None,  # ángulo de inclinación (paralelo al IS)
    height_a: float,
    length_b: float,
)
```

#### 3.2. Funciones principales

- **`get_default_json_path() -> Path`**  
  Devuelve la ruta por defecto del JSON (`Supports_mock.json` en la carpeta `Supports`).

- **`ensure_mock_json(path: Path | None = None) -> Path`**  
  - Si el fichero indicado no existe, crea un JSON de ejemplo con un soporte.  
  - Devuelve siempre la ruta final al archivo JSON.

- **`load_supports_from_json(path: str | Path | None = None) -> List[SupportJson]`**  
  - Lee el JSON (o crea el mock si no existe).  
  - Valida y convierte los datos en una lista de `SupportJson`.  
  - Ignora entradas inválidas, escribiendo un mensaje por consola.

- **`compute_segment_length(support: SupportJson) -> float`**  
  Devuelve la longitud de la polilínea entre `posicion1` y `posicion2`.  
  Se puede utilizar, por ejemplo, para ajustar la longitud del soporte:

  ```python
  length = compute_segment_length(soporte)
  support_model.set_length(length)
  ```

- **`build_preview_polyline_points(soportes: List[SoporteJson]) -> List[tuple[float, float, float]]`**  
  Genera una lista de puntos \[(p1, p2, p1, p2, ...)\] con las posiciones de todos los soportes.  
  Estos puntos se pueden usar para una previsualización en polilínea (líneas y/o puntos) antes de generar el 3D.

---

### 4. Prueba rápida desde consola

Se puede comprobar el funcionamiento básico del script sin entrar en Allplan:

1. Abrir una consola en la carpeta `Soportes`.
2. Ejecutar:

   ```bash
   python SoportesFromJson.py
   ```

3. El script:
   - Creará `Soportes_mock.json` si no existe.
   - Leerá el archivo JSON.
   - Mostrará por consola los soportes leídos y la longitud de cada tramo.

Si esta prueba funciona, la lectura/parsing del JSON y los cálculos de longitud están correctos.

---

### 5. Uso previsto desde otros scripts / Allplan

Un uso típico desde un script de Allplan podría ser:

```python
from Soportes.SoportesFromJson import (
    load_soportes_from_json,
    compute_segment_length,
    build_preview_polyline_points,
)

# 1) Leer soportes desde el JSON
soportes = load_soportes_from_json()  # usa la ruta por defecto

# 2) Generar puntos para previsualización en polilínea
preview_points = build_preview_polyline_points(soportes)
# Aquí se puede crear la polilínea de previsualización usando preview_points

# 3) Para cada soporte, calcular longitud real y crear el 3D
for soporte in soportes:
    length = compute_segment_length(soporte)

    # Pseudocódigo de integración con SupportModel:
    # support_model = SupportModel(build_ele, doc)
    # support_model.set_length(length)
    # ... posicionar el soporte según posicion1/posicion2 ...
    # model_list.extend(support_model.build())
```

La integración exacta con `SupportModel` y la polilínea de Allplan se puede ajustar según las necesidades del proyecto, pero este documento recoge la base de cómo se leen y se preparan los datos desde el JSON externo.

