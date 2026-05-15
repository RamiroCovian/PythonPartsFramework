# Documentación: Gestión de Caminos via JSON

## Flujo General


```
┌──────────────┐     ┌─────────────┐     ┌───────────────┐     ┌─────────────┐     ┌──────────────┐
│  L. PUNTOS   │────▶│ L. generar  │────▶│               │────▶│  L. leer    │────▶│ L. POLILINEA │
│ (Allplan)    │     │    JSON     │     │ Optimización  │     │    JSON     │     │  (Allplan)   │
└──────────────┘     └─────────────┘     │  (black box)  │     └─────────────┘     └──────────────┘
                          │              └───────────────┘           │
                     export_*.json                            output.json
```

1. El usuario dibuja puntos/nodos en Allplan asignándoles roles (Inicial, Paso, Bifurcación, Final)
2. **Exportar JSON** genera un archivo con la estructura de grafo (nodos + conexiones)
3. El algoritmo de optimización consume ese JSON y calcula las trayectorias
4. El algoritmo devuelve un JSON con las polilíneas resueltas
5. **Importar JSON** lee ese resultado y recrea la geometría optimizada en Allplan


---

## Parte 1: JSON de Exportación (lo que nosotros generamos)

Este es el JSON que la librería produce al pulsar **"Exportar JSON"**.
El algoritmo de optinización lo consume como input.

### Estructura completa

```json
{
  "caminos": [
    {
      "id": "camino_0",
      "tipo": "electrico",
      "nodos": [
        {
          "id": "P0",
          "tipo": "inicio",
          "coordenadas": [1200.5, 3400.0, 2800.0],
          "anteriores": [],
          "siguientes": ["P1"],
          "metadata": {
            "orden": 0,
            "path_id": 0,
            "segment_id": 0,
            "color_id": 1,
            "diameter": 110.0,
            "section_type": "circular",
            "system": "default"
          }
        },
        {
          "id": "P1",
          "tipo": "intermedio_obligado",
          "coordenadas": [2500.0, 3400.0, 2800.0],
          "anteriores": ["P0"],
          "siguientes": ["P2"],
          "metadata": { ... }
        },
        {
          "id": "P2",
          "tipo": "final",
          "coordenadas": [4000.0, 3400.0, 2800.0],
          "anteriores": ["P1"],
          "siguientes": [],
          "metadata": { ... }
        }
      ]
    }
  ],
  "layer_default": {},
  "selected_inst_type": "electrico",
  "applied_layers": "{}",
  "applied_default_attrs": "{}",
  "applied_custom_attrs": "{}"
}
```

### Campos del JSON de exportación

#### Nivel raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `caminos` | array | Lista de caminos. Cada camino es una red de nodos interconectados |
| `layer_default` | object | Configuración de layer por defecto de Allplan |
| `selected_inst_type` | string | Tipo de instalación seleccionado en la paleta (ej. `"electrico"`) |
| `applied_layers` | string | Layers aplicados (JSON serializado) |
| `applied_default_attrs` | string | Atributos por defecto aplicados (JSON serializado) |
| `applied_custom_attrs` | string | Atributos personalizados aplicados (JSON serializado) |

#### Camino (`caminos[]`)

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador único del camino (ej. `"camino_0"`) |
| `tipo` | string | Tipo de instalación (ej. `"electrico"`, `"datos"`, `"hvac"`, `"agua"`) |
| `nodos` | array | Lista de nodos que forman el grafo del camino |

#### Nodo (`caminos[].nodos[]`)

Cada nodo representa un punto del camino con sus conexiones explícitas.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador único del nodo (ej. `"P0"`, `"P1"`) |
| `tipo` | string | Tipo del nodo (ver tabla de tipos abajo) |
| `coordenadas` | array[3] | Posición `[x, y, z]` en milímetros (coordenadas de Allplan) |
| `anteriores` | array | IDs de los nodos que conectan **hacia** este nodo |
| `siguientes` | array | IDs de los nodos hacia los que este nodo **sale** |
| `metadata` | object | Información adicional del nodo (uso interno, puede ignorarse) |

#### Metadata del nodo (`caminos[].nodos[].metadata`)

Estos campos son informativos. El algoritmo puede ignorarlos si no los necesita.

| Campo | Tipo | Descripción |
|---|---|---|
| `orden` | int | Orden secuencial del punto en su path |
| `path_id` | int | Índice del path al que pertenece (0-based) |
| `segment_id` | int | Índice del segmento al que pertenece |
| `color_id` | int | ID de color en Allplan |
| `diameter` | float | Diámetro del conducto/cable en mm |
| `section_type` | string | Tipo de sección (ej. `"circular"`) |
| `system` | string | Sistema al que pertenece (ej. `"default"`) |


---

## Parte 2: Tipos de Nodo

Los nodos tienen un `tipo` que define su rol en el grafo.

| `tipo` en JSON | Rol en Allplan | Descripción | `anteriores` | `siguientes` |
|---|---|---|---|---|
| `inicio` | Inicial | Punto de origen del camino (tablero, equipo, toma principal) | `[]` vacío | 1 o más IDs |
| `intermedio_obligado` | Paso | Punto intermedio por el que el camino **debe** pasar (caja de registro, switch, válvula) | 1 o más IDs | 1 o más IDs |
| `intermedio_libre` | Paso | Punto de referencia opcional, no obliga paso | `[]` vacío | `[]` vacío |
| `bifurcacion` | Bifurcación | Punto donde el camino se **divide** en múltiples ramas | 1 o más IDs | 2 o más IDs |
| `convergencia` | Bifurcación | Punto donde múltiples ramas **convergen** en una | 2 o más IDs | 1 o más IDs |
| `final` | Final | Punto de destino (tomacorriente, difusor, grifo) | 1 o más IDs | `[]` vacío |


---

## Parte 3: Cómo se construyen las conexiones `anteriores` / `siguientes`

Las conexiones forman un **grafo dirigido** que describe cómo fluye el camino.

### Reglas

- Cada nodo lista explícitamente a quién apunta (`siguientes`) y de quién viene (`anteriores`)
- Las conexiones son **bidireccionales consistentes**: si A tiene a B en `siguientes`, entonces B tiene a A en `anteriores`
- El flujo va de `inicio` → `intermedio_obligado` → `bifurcacion`/`convergencia` → `final`

### Ejemplo: camino lineal simple

```
inicio ──▶ intermedio ──▶ final
```

```json
[
  { "id": "A", "tipo": "inicio",              "anteriores": [],    "siguientes": ["B"] },
  { "id": "B", "tipo": "intermedio_obligado",  "anteriores": ["A"], "siguientes": ["C"] },
  { "id": "C", "tipo": "final",               "anteriores": ["B"], "siguientes": [] }
]
```

### Ejemplo: bifurcación (1 entrada, 2 salidas)

```
                    ┌──▶ final_1
inicio ──▶ bif ────┤
                    └──▶ final_2
```

```json
[
  { "id": "A",  "tipo": "inicio",      "anteriores": [],    "siguientes": ["BIF"] },
  { "id": "BIF","tipo": "bifurcacion",  "anteriores": ["A"], "siguientes": ["F1", "F2"] },
  { "id": "F1", "tipo": "final",       "anteriores": ["BIF"], "siguientes": [] },
  { "id": "F2", "tipo": "final",       "anteriores": ["BIF"], "siguientes": [] }
]
```

### Ejemplo: convergencia (3 entradas, 1 salida)

```
inicio_1 ──┐
inicio_2 ──┼──▶ conv ──▶ final
inicio_3 ──┘
```

```json
[
  { "id": "I1",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "I2",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "I3",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "CONV","tipo": "convergencia",  "anteriores": ["I1","I2","I3"], "siguientes": ["F"] },
  { "id": "F",   "tipo": "final",        "anteriores": ["CONV"],          "siguientes": [] }
]
```

### Ejemplo: convergencia + bifurcación combinadas

```
inicio_1 ──┐                    ┌──▶ final_1
inicio_2 ──┼──▶ conv ──▶ bif ──┤
inicio_3 ──┘                    └──▶ final_2
```

```json
[
  { "id": "I1",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "I2",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "I3",  "tipo": "inicio",       "anteriores": [],                "siguientes": ["CONV"] },
  { "id": "CONV","tipo": "convergencia",  "anteriores": ["I1","I2","I3"], "siguientes": ["BIF"] },
  { "id": "BIF", "tipo": "bifurcacion",  "anteriores": ["CONV"],          "siguientes": ["F1","F2"] },
  { "id": "F1",  "tipo": "final",        "anteriores": ["BIF"],           "siguientes": [] },
  { "id": "F2",  "tipo": "final",        "anteriores": ["BIF"],           "siguientes": [] }
]
```


---

## Parte 4: JSON de Importación (lo que el algoritmo nos devuelve)

Después de optimizar, el algoritmo devuelve un JSON con las trayectorias resueltas.
La librería lo consume al pulsar **"Importar JSON"**.

### Estructura esperada

```json
{
  "caminos": [
    {
      "tipo": "electrico_1",
      "polilinea": [
        [1200.5, 3400.0, 2800.0],
        [2000.0, 3400.0, 2800.0],
        [2500.0, 3400.0, 2800.0],
        [3000.0, 3000.0, 2800.0],
        [4000.0, 3400.0, 2800.0]
      ],
      "nodos": ["P0", "CONV1", "P1", "BIF1", "F1"]
    },
    {
      "tipo": "electrico_2",
      "polilinea": [
        [1200.5, 3400.0, 2800.0],
        [2000.0, 3400.0, 2800.0],
        [2500.0, 3400.0, 2800.0],
        [3000.0, 4000.0, 2800.0],
        [4000.0, 3800.0, 2800.0]
      ],
      "nodos": ["P0", "CONV1", "P1", "BIF1", "F2"]
    }
  ],
  "nodos": [
    {
      "id": "P0",
      "tipo": "inicio",
      "coord": [1200.5, 3400.0, 2800.0],
      "ant": [],
      "sig": ["CONV1"]
    },
    {
      "id": "CONV1",
      "tipo": "convergencia",
      "coord": [2500.0, 3400.0, 2800.0],
      "ant": ["P0"],
      "sig": ["P1"]
    },
    ...
  ]
}
```

### Campos del JSON de importación

#### Camino (`caminos[]`)

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Identificador del camino resuelto |
| `polilinea` | array | **Trayectoria resuelta**: lista ordenada de puntos `[x, y, z]`. Incluye todos los puntos intermedios calculados por el algoritmo, no solo los nodos originales |
| `nodos` | array | Lista de IDs de los nodos originales por los que pasa esta trayectoria (en orden) |

#### Nodo (`nodos[]`) -- nivel raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador del nodo (coincide con los IDs del input) |
| `tipo` | string | Tipo del nodo (mismos valores que en el input) |
| `coord` | array[3] | Posición `[x, y, z]` |
| `ant` | array | IDs de nodos anteriores |
| `sig` | array | IDs de nodos siguientes |

> **Nota**: En el JSON de importación los campos de conexión usan nombres abreviados:
> `coord` (en vez de `coordenadas`), `ant` (en vez de `anteriores`), `sig` (en vez de `siguientes`).


---

## Parte 5: Diferencia clave entre Export e Import

| | Export (nosotros generamos) | Import (el algoritmo genera) |
|---|---|---|
| **Propósito** | Describir el grafo de nodos para que el algoritmo calcule rutas | Devolver las rutas calculadas como polilíneas dibujables |
| **Camino contiene** | `nodos[]` como **objetos** con coordenadas y conexiones | `polilinea[]` como **array de puntos** `[x,y,z]` + `nodos[]` como **lista de IDs** |
| **Puntos** | Solo los nodos del usuario (inicio, paso, bifurcación, final) | Todos los puntos de la trayectoria (nodos + puntos intermedios calculados) |
| **Conexiones** | Explícitas en cada nodo (`anteriores`/`siguientes`) | Implícitas en el orden de `polilinea` |
| **Nodos a nivel raíz** | No | Sí, lista flat con `id`, `tipo`, `coord`, `ant`, `sig` |


---

## Parte 6:

### Coordenadas
- Las coordenadas están en **milímetros** 
- Formato siempre `[x, y, z]` como array de 3 números
- El eje Z representa la altura

### IDs de nodos
- Los IDs son strings únicos dentro de un camino
- Formato generado: `"P0"`, `"P1"`, `"P2"`, etc.
- El algoritmo debe mantener los mismos IDs en su respuesta para que el sistema pueda hacer la correspondencia

### Múltiples caminos
- Un export puede contener varios caminos en el array `caminos[]`
- Cada camino es independiente (su propio grafo de nodos)
- El `tipo` identifica la instalación (ej. `"electrico"`, `"datos"`, `"hvac"`)

### Campos opcionales que se pueden ignorar
- `metadata` en cada nodo: información interna de Allplan, no necesaria para el algoritmo
- `layer_default`, `applied_layers`, `applied_default_attrs`, `applied_custom_attrs`: configuración de layers de Allplan

### La polilínea de respuesta
- La `polilinea` del import debe tener al menos 2 puntos
- Los puntos intermedios calculados por el algoritmo (que no son nodos originales) se incluyen igualmente
- El orden de los puntos en `polilinea` define la trayectoria a dibujar
- Cada entrada en `caminos[]` del output representa **una ruta completa** de inicio a final (en caso de bifurcaciones, habrá un camino por cada rama)




## Arquitectura General

La librería `polyline_base_lib.py` (alias `PBL`) maneja toda la lógica genérica de
polilíneas: creación, edición, captura de puntos, serialización, exportación e
importación. Los scripts de instalación (ej. `elec_lib_demo.py`) son **capas finas**
que solo aportan:

- Configuración específica (`PolylineBaseConfig`)
- Estilo visual por segmento (`element_creation_hook`)
- Manejo de eventos de UI (`event_handler_hook`)
- Valores de paleta específicos de la instalación

```
┌─────────────────────────────────────┐
│         Script de instalación       │  ← elec_lib_demo.py, ventilacion.py, etc.
│  (hooks, config, estilos visuales)  │
├─────────────────────────────────────┤
│         polyline_base_lib.py        │  ← Librería genérica
│  (interacción, captura, modos,     │
│   export/import JSON, geometría)    │
└─────────────────────────────────────┘
```


---

## Paso 1: Inicialización del ScriptObject

Toda instalación empieza en `create_script_object()`, la función que Allplan llama al
cargar el PythonPart.

```python
import polyline_base_lib as PBL

CONFIG = PBL.PolylineBaseConfig(
    drawing_mode=PBL.DRAWING_MODE_3D_CONSTRAINED,
    enable_capture_mode=True,
    capture_auto_commit_on_final=True,
    # ... más opciones según la instalación
)

def create_script_object(build_ele, script_object_data):
    # 1. Crear el script object con la configuración
    so = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)

    # 2. Conectar los hooks (ver secciones siguientes)
    so.event_handler_hook = on_control_event           # Eventos de botones
    so.element_creation_hook = crear_elementos_segmento  # Estilo visual

    # 3. Habilitar modo transaccional (PythonParts editables)
    PBL.enable_transactional_finalize(so)

    return so
```

### `PBL.initialize_script_object(build_ele, script_object_data, config)`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `build_ele` | BuildingElement | Elemento de construcción proporcionado por Allplan |
| `script_object_data` | ScriptObjectData | Datos del script object proporcionados por Allplan |
| `config` | `PolylineBaseConfig` | Configuración de comportamiento (opcional) |

**Retorna**: `PolylineScriptObject` -- el script object listo para recibir hooks.


---

## Paso 2: Hooks disponibles

Los hooks son funciones que el script de instalación asigna al `script_object` para
personalizar el comportamiento **sin modificar la librería**.

### 2.1 `event_handler_hook` -- Manejo de eventos de paleta

**Asignación:**
```python
so.event_handler_hook = mi_funcion_eventos
```

**Firma:**
```python
def mi_funcion_eventos(build_ele, event_id: int) -> bool:
    """
    Args:
        build_ele: Elemento de construcción (para leer propiedades de paleta)
        event_id: ID numérico del evento (definido en el .pyp con <EventId>)

    Returns:
        True  -> El evento fue manejado, la librería NO lo procesa
        False -> El evento NO fue manejado, la librería puede procesarlo
    """
```

**Cuándo se llama:** Cada vez que el usuario pulsa un botón en la paleta. La librería
llama primero al hook; si retorna `True`, no hace nada más. Si retorna `False` o `None`,
la librería intenta procesar el evento con sus handlers internos (ej. `Finalizar`,
`Borrar Selección`, `Continuar Polilínea`).

**Ejemplo real (de `elec_lib_demo.py`):**

```python
EVENT_EXPORT_JSON = 1030
EVENT_IMPORT_JSON = 1031

def on_control_event(build_ele, event_id):
    so = _global_script_object
    intr = getattr(so, "script_object_interactor", None)

    if event_id == EVENT_EXPORT_JSON:
        tipo = _get_installation_type(build_ele)
        out_dir = os.path.dirname(os.path.abspath(__file__))
        intr.export_json(tipo_instalacion=tipo, output_dir=out_dir)
        return True

    if event_id == EVENT_IMPORT_JSON:
        intr.import_json()
        return True

    return False  # No manejado → la librería decide
```

### 2.2 `element_creation_hook` -- Estilo visual por segmento

**Asignación:**
```python
so.element_creation_hook = mi_funcion_elementos
```

**Firma:**
```python
def mi_funcion_elementos(segment_meta: SegmentMetadata, common_prop) -> list:
    """
    Args:
        segment_meta: Metadata del segmento (puntos, diámetro, sistema, color, etc.)
        common_prop: CommonProperties de Allplan (pen, stroke, color, layer)

    Returns:
        Lista de ModelElement3D para representar este segmento en Allplan
    """
```

**Cuándo se llama:** Durante `execute()` y durante la recreación de geometría en edición.
Se llama **una vez por cada segmento** guardado. Si el hook no está asignado, la librería
crea líneas simples por defecto.

**Ejemplo:**
```python
def crear_elementos_ventilacion(seg_meta, common_prop):
    p1, p2 = seg_meta.points[0], seg_meta.points[-1]
    props = clone_common(common_prop)
    props.Color = 4  # Color específico de ventilación

    # Crear tubería 3D con el diámetro del segmento
    elements = crear_tuberia_3d(p1, p2, seg_meta.diameter, props)
    return elements
```

### 2.3 `post_process_hook` -- Post-procesado de todos los elementos

**Asignación:**
```python
so.post_process_hook = mi_funcion_postproceso
```

**Firma:**
```python
def mi_funcion_postproceso(elements: list, script_object) -> list:
    """
    Args:
        elements: Lista completa de ModelElement3D generados
        script_object: Referencia al PolylineScriptObject

    Returns:
        Lista modificada de elementos (puede añadir, quitar o modificar)
    """
```

**Cuándo se llama:** Después de que todos los segmentos han sido procesados por
`element_creation_hook`, pero antes de que los elementos se devuelvan a Allplan.


---

## Paso 3: Paleta (.pyp) -- Declarar botones de Export/Import

Los botones se declaran en el archivo `.pyp` de la instalación. Cada botón tiene un
`<EventId>` que se corresponde con la constante en el script Python.

```xml
<Parameter>
    <Name>RowJSON</Name>
    <Text>JSON</Text>
    <ValueType>Row</ValueType>

    <Parameter>
        <Name>exportJSON</Name>
        <Text>Exportar JSON</Text>
        <EventId>1030</EventId>          <!-- Debe coincidir con EVENT_EXPORT_JSON -->
        <Value>0</Value>
        <ValueType>Button</ValueType>
    </Parameter>

    <Parameter>
        <Name>importJSON</Name>
        <Text>Importar JSON</Text>
        <EventId>1031</EventId>          <!-- Debe coincidir con EVENT_IMPORT_JSON -->
        <Value>0</Value>
        <ValueType>Button</ValueType>
    </Parameter>
</Parameter>
```

**Importante:** Los `<EventId>` son números arbitrarios pero deben ser únicos dentro
del `.pyp` y coincidir exactamente con las constantes en el script Python.


---

## Paso 4: Métodos de la librería para Export/Import

Estos métodos están en `PolylineInteractor` (accesible como `so.script_object_interactor`
o simplemente `intr`).

### 4.1 `intr.export_json(...)` -- Exportar JSON

```python
def export_json(
    self,
    camino_id: Optional[str] = None,
    tipo_instalacion: str = "",
    layer_default: Optional[Dict[str, Any]] = None,
    applied_layers: str = "{}",
    applied_default_attrs: str = "{}",
    applied_custom_attrs: str = "{}",
    indent: int = 2,
    output_dir: Optional[str] = None,
) -> str
```

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `camino_id` | No | ID del camino. Si es `None`, se auto-genera (UUID) |
| `tipo_instalacion` | Sí | Tipo de instalación: `"electrico"`, `"ventilacion"`, etc. |
| `layer_default` | No | Dict con configuración de layer por defecto |
| `applied_layers` | No | JSON string de layers aplicados |
| `applied_default_attrs` | No | JSON string de atributos por defecto |
| `applied_custom_attrs` | No | JSON string de atributos personalizados |
| `indent` | No | Indentación del JSON (default: 2) |
| `output_dir` | No | Directorio donde guardar el archivo. Si se proporciona, genera `export_YYYY-MM-DD_HH-MM-SS.json` y muestra diálogo de confirmación |

**Retorna:** El JSON como string (siempre, independientemente de si se guardó a disco).

**Uso mínimo desde el script de instalación:**
```python
tipo = "ventilacion"
out_dir = os.path.dirname(os.path.abspath(__file__))
intr.export_json(tipo_instalacion=tipo, output_dir=out_dir)
```

**Flujo interno:**
1. Llama a `build_camino_model()` para construir el modelo de grafo
2. Llama a `generate_json()` para serializar a JSON
3. Si `output_dir` se proporcionó: genera nombre timestamped, escribe archivo, muestra diálogo


### 4.2 `intr.import_json(...)` -- Importar JSON

```python
def import_json(self, file_path: Optional[str] = None) -> bool
```

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `file_path` | No | Ruta al archivo JSON. Si es `None`, abre un diálogo de selección de archivo |

**Retorna:** `True` si la importación fue exitosa.

**Uso mínimo desde el script de instalación:**
```python
intr.import_json()  # Abre diálogo de selección automáticamente
```

**Flujo interno:**
1. Si no hay `file_path`: abre diálogo nativo de selección de archivo (`tkinter`)
2. Lee y parsea el JSON
3. Auto-detecta el formato (output del optimizador o re-import de nuestro export)
4. Llama a `_restore_from_export_data()` para poblar `saved_paths` y `saved_segments`
5. Muestra diálogo de confirmación con número de caminos y segmentos importados


### 4.3 `intr.build_camino_model(...)` -- Construir modelo (uso avanzado)

```python
def build_camino_model(
    self,
    camino_id: Optional[str] = None,
    tipo_instalacion: str = "",
) -> CaminoModel
```

Construye un `CaminoModel` a partir del estado actual del interactor (puntos guardados,
segmentos, roles). Útil si necesitas manipular el modelo antes de exportar.

**Retorna:** `CaminoModel` con todos los nodos y conexiones computadas.


### 4.4 `generate_json(...)` -- Serializar a JSON (función standalone)

```python
def generate_json(
    caminos: List[CaminoModel],
    indent: int = 2,
    layer_default: Optional[Dict[str, Any]] = None,
    selected_inst_type: str = "",
    applied_layers: str = "{}",
    applied_default_attrs: str = "{}",
    applied_custom_attrs: str = "{}",
) -> str
```

Función de nivel de módulo (no método de clase). Toma una lista de `CaminoModel` y
devuelve el JSON string. Útil si quieres componer múltiples caminos de diferentes
fuentes antes de serializar.


---

## Paso 5: Clases de datos

### `PolylineBaseConfig`

Configuración de comportamiento del interactor. Se pasa a `initialize_script_object()`.

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `drawing_mode` | str | `DRAWING_MODE_3D_CONSTRAINED` | Modo de dibujo: `DRAWING_MODE_2D`, `DRAWING_MODE_3D_FREE`, `DRAWING_MODE_3D_CONSTRAINED` |
| `z_jump_threshold` | float | `100.0` | Máximo salto Z permitido en modo CONSTRAINED (mm) |
| `enable_capture_mode` | bool | `False` | Habilitar workflow de captura tipo PointInput |
| `capture_auto_commit_on_final` | bool | `True` | Auto-finalizar camino cuando el rol del punto es Final |
| `limit_angles` | bool | `False` | Limitar ángulos a incrementos predefinidos |
| `allow_insert_point_mode` | bool | `False` | Permitir insertar puntos en segmentos existentes |
| `point_mode_property` | str | `"PointMode"` | Nombre de la propiedad de paleta para el modo (Create/Edit) |

### `SegmentMetadata`

Metadata de un segmento individual. Se pasa al `element_creation_hook`.

| Campo | Tipo | Descripción |
|---|---|---|
| `points` | List[Point3D] | Puntos del segmento (mínimo 2: inicio y fin) |
| `diameter` | float | Diámetro en mm |
| `section_type` | str | Tipo de sección (ej. `"circular"`) |
| `system` | str | Sistema (ej. `"default"`, `"Principal"`) |
| `color_id` | int | ID de color Allplan |
| `path_id` | int | Índice del path al que pertenece |
| `segment_id` | int | Índice del segmento dentro del path |
| `point_roles` | List[int] | Roles de los puntos: `[rol_inicio, rol_fin]` |
| `custom` | Dict | Campos adicionales personalizados |

**Constantes de rol:**
```python
CAPTURE_ROLE_INICIAL = 0      # Punto de inicio
CAPTURE_ROLE_PASO = 1         # Punto intermedio
CAPTURE_ROLE_BIFURCACION = 2  # Punto de bifurcación/convergencia
CAPTURE_ROLE_FINAL = 3        # Punto final
```

### `PuntoModel`

Representa un nodo en el JSON de exportación. Normalmente no se crea manualmente
-- `build_camino_model()` lo genera automáticamente.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | str | ID único del nodo |
| `x`, `y`, `z` | float | Coordenadas |
| `orden` | int | Orden secuencial |
| `tipo` | str | Rol interno (`"Inicial"`, `"Paso"`, `"Bifurcacion"`, `"Final"`) |
| `anteriores` | List[str] | IDs de nodos anteriores |
| `siguientes` | List[str] | IDs de nodos siguientes |

### `CaminoModel`

Representa un camino completo para exportar. Normalmente se crea via
`build_camino_model()`.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | str | ID único del camino |
| `tipo_instalacion` | str | Tipo de instalación |
| `puntos` | List[PuntoModel] | Nodos del grafo |


---

## Paso 6: Ejemplo completo -- Script de instalación mínimo

Este es el esqueleto mínimo para un nuevo script de instalación con soporte de
export/import JSON:

```python
"""ventilacion.py -- Instalación de ventilación con export/import JSON."""

import os
import polyline_base_lib as PBL

# --- Constantes de eventos (deben coincidir con el .pyp) ---
EVENT_EXPORT_JSON = 1030
EVENT_IMPORT_JSON = 1031

# --- Configuración ---
CONFIG = PBL.PolylineBaseConfig(
    drawing_mode=PBL.DRAWING_MODE_3D_CONSTRAINED,
    enable_capture_mode=True,
    capture_auto_commit_on_final=True,
)

_so = None

# --- Allplan entry points ---

def check_allplan_version(_build_ele, _version):
    return True

def create_script_object(build_ele, script_object_data):
    global _so
    _so = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    _so.event_handler_hook = _on_event
    _so.element_creation_hook = _crear_segmento
    PBL.enable_transactional_finalize(_so)
    return _so

# --- Hook: eventos de paleta ---

def _on_event(build_ele, event_id):
    intr = getattr(_so, "script_object_interactor", None)
    if intr is None:
        return False

    if event_id == EVENT_EXPORT_JSON:
        intr.export_json(
            tipo_instalacion="ventilacion",
            output_dir=os.path.dirname(os.path.abspath(__file__)),
        )
        return True

    if event_id == EVENT_IMPORT_JSON:
        intr.import_json()
        return True

    return False

# --- Hook: estilo visual por segmento ---

def _crear_segmento(seg_meta, common_prop):
    # Personalizar aquí el aspecto visual de cada segmento
    # Por defecto, crear líneas simples:
    return None  # None = la librería usa su estilo por defecto
```

### `.pyp` mínimo correspondiente

```xml
<!-- Dentro de <Page> de la paleta -->
<Parameter>
    <Name>RowJSON</Name>
    <Text>JSON</Text>
    <ValueType>Row</ValueType>
    <Parameter>
        <Name>exportJSON</Name>
        <Text>Exportar JSON</Text>
        <EventId>1030</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
    </Parameter>
    <Parameter>
        <Name>importJSON</Name>
        <Text>Importar JSON</Text>
        <EventId>1031</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
    </Parameter>
</Parameter>
```


---

## Referencia rápida: Acceso al Interactor

El interactor es el objeto que tiene los métodos de export/import. Se accede desde
el script object:

```python
so = _global_script_object
intr = getattr(so, "script_object_interactor", None)

# Ahora puedes llamar:
intr.export_json(...)
intr.import_json(...)
intr.build_camino_model(...)
```

**Importante:** El interactor solo existe después de que Allplan llama a `start_input()`.
Si necesitas acceder desde `create_script_object()`, el interactor **aún no existe**.
Los hooks se asignan al `script_object` (no al interactor) precisamente por esta razón.


---

## Paso 7: Generar Camino Óptimo (Un solo botón)

A partir de la integración con `Caminos_Optimos_Lib`, la librería ofrece un botón
que ejecuta **todo el flujo automáticamente**: exportar, optimizar, e importar el
resultado.

### Flujo interno

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌────────────────┐     ┌───────────────┐
│  Puntos en      │────▶│ build_camino     │────▶│ optimizer_adapter │────▶│ optimizer_     │────▶│ Previsualizar │
│  Allplan        │     │ _model()         │     │ .build_optimizer  │     │ runner         │     │ polilínea     │
│                 │     │                  │     │ _input()          │     │ .run_optimizer │     │ optimizada    │
└─────────────────┘     └──────────────────┘     └───────────────────┘     │ (subprocess)   │     └───────────────┘
                                                        │                  └────────────────┘            ▲
                                                        │                         │                     │
                                                   input JSON                _grafo.json           optimizer_adapter
                                                   (formato                  (formato                .parse_optimizer
                                                   optimizador)              optimizador)            _output()
```

### 7.1 Método: `intr.generar_camino_optimo(...)`

```python
def generar_camino_optimo(
    self,
    tipo_instalacion: str = "",
    mock_config: Optional[Dict[str, Any]] = None,
    timeout: int = 120,
) -> bool
```

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `tipo_instalacion` | Sí | Tipo de instalación (`"electrico"`, `"ventilacion"`, etc.) |
| `mock_config` | No | Override para `techo`, `obstaculos`, `configuracion`, etc. Si es `None`, el techo se auto-genera a partir del bounding box de los puntos |
| `timeout` | No | Máximo de segundos para esperar al optimizador (default: 120) |

**Retorna:** `True` si la polilínea optimizada se cargó correctamente.

**Pasos internos:**
1. Llama a `build_camino_model()` para obtener el estado actual
2. Llama a `optimizer_adapter.build_optimizer_input()` para traducir al formato del optimizador
3. Escribe el JSON input en `Libreria/optimizer_temp/`
4. Ejecuta `Caminos_Optimos_Lib/main.py` como subproceso usando su `venv`
5. Lee el archivo `_grafo.json` de salida
6. Llama a `optimizer_adapter.parse_optimizer_output()` para extraer las polilíneas
7. Llama a `_restore_from_export_data()` para cargar la geometría optimizada
8. Muestra diálogo de éxito o error

### 7.2 Módulos auxiliares

#### `optimizer_adapter.py`

Traductor entre el formato de nuestra librería y el formato de `Caminos_Optimos_Lib`.

| Función | Descripción |
|---|---|
| `build_optimizer_input(camino_dict, mock_config)` | Traduce `CaminoModel.to_dict()` al input del optimizador. Convierte tipos de nodo, formato de coordenadas `[x,y,z]` → `{x,y,z}`, y agrega `techo`/`obstaculos` |
| `parse_optimizer_output(grafo_json)` | Extrae las polilíneas del `_grafo.json` como listas de `[x,y,z]` |

**Mapeo de tipos de nodo (Export → Optimizador):**

| Nuestro tipo | Tipo del optimizador |
|---|---|
| `inicio` | `inicio` |
| `intermedio_obligado` | `orden_obligatorio` |
| `intermedio_libre` | `orden_libre` |
| `bifurcacion` | `orden_obligatorio` |
| `final` | `fin` |

**Mapeo de tipos de nodo (Grafo → Import):**

| Tipo del grafo | Nuestro tipo |
|---|---|
| `inicio` | `inicio` |
| `final` | `final` |
| `obligatorio` | `intermedio_obligado` |
| `libre` | `intermedio_libre` |
| `codo` | `intermedio_libre` |
| `union` | `intermedio_libre` |
| `conector` | `intermedio_libre` |

#### `optimizer_runner.py`

Ejecutor del optimizador como subproceso.

| Función | Descripción |
|---|---|
| `run_optimizer(input_json_path, timeout, lib_root)` | Ejecuta `main.py --no-mostrar` usando el Python del venv. Devuelve el `_grafo.json` parseado como dict |

**Requisitos:**
- `Caminos_Optimos_Lib/` debe estar al mismo nivel que `Libreria/` (dentro de `Instalaciones/`)
- El `venv` del optimizador debe estar creado con sus dependencias (numpy, plotly, networkx)

### 7.3 Mock config (datos temporalmente hardcodeados)

Como los datos de `techo` y `obstaculos` aún no se obtienen del dibujo de Allplan,
el método los genera automáticamente:

- **`techo`**: Rectángulo plano derivado del bounding box de los puntos dibujados,
  con un margen de 2000mm por lado y Z ligeramente inferior al Z mínimo
- **`obstaculos`**: Lista vacía (no hay detección de obstáculos por ahora)
- **`configuracion`**: Valores por defecto (`subtipo_tuberia: "extraccion_impulsion"`,
  `estrategia_colision: ["saltar"]`)

Para personalizar, pase un dict `mock_config` al método:

```python
intr.generar_camino_optimo(
    tipo_instalacion="ventilacion",
    mock_config={
        "techo": [{"id": "techo_real", "vertices": [...]}],
        "obstaculos": [{"id": "pilar_1", "vertices": [...]}],
        "configuracion": {
            "subtipo_tuberia": "extraccion_impulsion",
            "estrategia_colision": ["rodear"],
        },
    },
)
```

### 7.4 Paleta (.pyp) -- Botón de Generar Camino Óptimo

```xml
<Parameter>
    <Name>generateOptimal</Name>
    <Text>Generar Camino Optimo</Text>
    <EventId>1032</EventId>
    <Value>0</Value>
    <ValueType>Button</ValueType>
</Parameter>
```

### 7.5 Handler en el script de instalación

```python
EVENT_GENERATE_OPTIMAL = 1032

def on_control_event(build_ele, event_id):
    intr = getattr(_so, "script_object_interactor", None)
    if intr is None:
        return False

    if event_id == EVENT_GENERATE_OPTIMAL:
        tipo = _get_installation_type(build_ele)
        intr.generar_camino_optimo(tipo_instalacion=tipo)
        return True

    return False
```


---

## Resumen de archivos involucrados

| Archivo | Ubicación | Rol |
|---|---|---|
| `polyline_base_lib.py` | `Libreria/` | Librería genérica -- interacción, modos, export/import, optimización |
| `optimizer_adapter.py` | `Libreria/` | Traductor de formatos entre nuestra librería y Caminos_Optimos_Lib |
| `optimizer_runner.py` | `Libreria/` | Ejecutor del optimizador como subproceso (venv Python) |
| `mi_instalacion.py` | `DEMOS/` o `Instalaciones/` | Script de instalación -- hooks y config |
| `mi_instalacion.pyp` | Junto al `.py` | Paleta XML -- botones con `<EventId>` |
| `export_*.json` | Directorio del script | Archivo exportado (generado automáticamente) |
| `Caminos_Optimos_Lib/` | `Instalaciones/` | Librería externa del optimizador (con su propio venv) |
