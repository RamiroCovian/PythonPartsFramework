# ElementosNoDefinidos

## 1. Resumen y Propósito

`ElementosNoDefinidos` implementa una feature de captura manual de puntos lógicos para describir recorridos antes de que exista geometría 3D final.

La feature resuelve dos necesidades concretas:

- Permite que el usuario defina la intención del recorrido sin depender todavía de tubos, codos o accesorios modelados.
- Proporciona un modelo intermedio estable que otros módulos pueden consumir para exportación, análisis topológico o generación posterior.

Desde el punto de vista funcional, el módulo permite:

- capturar puntos de tipo `inicio`, `final`, `intermedio_libre`, `intermedio_ordenado` y `bifurcación`,
- agrupar esos puntos por camino,
- detectar puntos comunes entre caminos distintos,
- generar topología de cruce,
- y exponer un formato exportado uniforme (`nodos_export_data`) para consumidores como `Agua`.

El módulo no genera directamente el modelo 3D final. Su contrato actual es dejar preparado:

- `script_object.puntos_no_definidos`
- `script_object.common_points_topology`
- `script_object.common_junctions`
- `script_object.nodos_export_data`

Esto desacopla la captura de entrada respecto de la lógica de generación o exportación final.

---

## 2. Arquitectura y Componentes Clave

### Archivos principales

- `ElementosNoDefinidos/__init__.py`
  Punto de entrada del módulo. Reexporta las funciones públicas que usan consumidores externos.

- `ElementosNoDefinidos/constants.py`
  Define el dominio base del módulo: tipos de punto, labels de UI, formas geométricas y constantes de detección visual.

- `ElementosNoDefinidos/palette.py`
  Encapsula la lectura de parámetros desde `build_ele`. Traduce los valores de la paleta al modelo interno del módulo.

- `ElementosNoDefinidos/handlers.py`
  Implementa la lógica principal de negocio:
  - activación del modo de captura,
  - captura de clics,
  - detección de puntos comunes,
  - construcción de topología,
  - generación de junctions,
  - construcción del contrato exportado `nodos_export_data`.

- `ElementosNoDefinidos/preview.py`
  Implementa la representación visual de los puntos en el viewport de Allplan.

- `ElementosNoDefinidos/serialization.py`
  Serializa y restaura el modelo interno `puntos_no_definidos`.

- `ElementosNoDefinidos/common_points.py`
  Contiene la lógica de agrupación por proximidad para detectar cruces y conexiones compartidas entre caminos.

- `ElementosNoDefinidos/optimizer_graph.py`
  Mantiene un exportador alternativo tipo grafo para escenarios de optimización. No forma parte del contrato principal consumido por `Agua`, pero reutiliza el mismo modelo base de puntos.

### Relación entre componentes

La arquitectura sigue una separación bastante clara por responsabilidad:

1. `constants.py` define el vocabulario del dominio.
2. `palette.py` traduce el estado de la UI a valores internos.
3. `handlers.py` usa esa información para construir y actualizar el estado.
4. `common_points.py` se usa desde `handlers.py` y `preview.py` para resolver cruces por proximidad.
5. `preview.py` representa el estado capturado visualmente.
6. `serialization.py` permite persistir y restaurar el estado.
7. `__init__.py` expone la API pública del módulo.

### Dependencias clave

El módulo depende principalmente de la API de Allplan:

- `NemAll_Python_Geometry`
- `NemAll_Python_BasisElements`
- `NemAll_Python_BaseElements`
- `NemAll_Python_Utility`

También depende del contrato de integración con el consumidor:

- `script_object.build_ele`
- `script_object.puntos_no_definidos`
- `interactor.coord_input`
- `interactor.current_point`
- `interactor._draw_preview(...)`

No se introducen dependencias externas de terceros fuera del runtime de Allplan y la librería estándar de Python.

---

## 3. Flujo de Implementación (Paso a Paso)

### Paso 1. Definición del dominio de puntos

La implementación empieza en `constants.py`, donde se define el vocabulario base del módulo.

Se establecen:

- los tipos de punto,
- el mapping entre labels visibles y claves internas,
- y la forma geométrica usada en preview para cada tipo.

Snippet representativo:

```python
TIPO_INICIO = "inicio"
TIPO_FINAL = "final"
TIPO_INTERMEDIO_LIBRE = "intermedio_libre"
TIPO_BIFURCACION = "bifurcación"
TIPO_INTERMEDIO_ORDENADO = "intermedio_ordenado"
```

Esta separación evita acoplar la lógica a textos de UI. La paleta trabaja con labels; el motor trabaja con claves internas estables.

### Paso 2. Traducción del estado de paleta a datos internos

`palette.py` centraliza toda la lectura desde `build_ele`. Esto evita duplicar `getattr(...)` y concentra en un solo lugar la interpretación de parámetros.

Las funciones más relevantes son:

- `get_tipo_camino(...)`
- `get_tipo_punto_orden(...)`
- `get_color_puntos(...)`
- `get_path_key_puntos(...)`
- `get_common_points_detection_enabled(...)`
- `get_common_points_tolerance_mm(...)`

La función clave aquí es `get_path_key_puntos(...)`, porque determina cómo se agrupan los puntos en caminos lógicos:

```python
def get_path_key_puntos(build_ele, color_id: int, tipo_camino: int) -> str:
    try:
        path_param = getattr(build_ele, "PathId", None) if build_ele is not None else None
        path_raw = (
            getattr(path_param, "value", None)
            or getattr(path_param, "Value", None)
            if path_param is not None
            else None
        )
        if path_raw is not None:
            path_id = int(path_raw)
            if path_id > 0:
                return f"path:{path_id}"
    except Exception:
        pass
    return f"modo:{int(tipo_camino)}|color:{int(color_id)}"
```

La prioridad es:

1. usar `PathId` si existe,
2. y en su defecto construir una key derivada de modo y color.

Esto permite soporte tanto explícito como implícito para agrupación de recorridos.

### Paso 3. Activación del modo de captura

La activación del flujo se resuelve en `handlers.py` mediante `on_anadir_punto_no_definido(...)`.

Este método no agrega puntos todavía. Su responsabilidad es preparar el interactor para que los siguientes clics entren en modo de captura.

```python
def on_anadir_punto_no_definido(script_object: Any, intr: Any) -> bool:
    intr.next_click_adds_punto_no_definido = True
    intr.script_object = script_object
    if not hasattr(script_object, "puntos_no_definidos") or not isinstance(
        getattr(script_object, "puntos_no_definidos", None), list
    ):
        script_object.puntos_no_definidos = []
    _try_print_prompt(intr)
    _try_save_state(intr)
    return True
```

Una decisión importante aquí es que el módulo no da por hecho que el consumidor haya inicializado el storage. Si no existe, lo crea.

### Paso 4. Captura de clic y construcción del modelo interno

La lógica principal de alta de puntos está en `handle_click_add_punto_no_definido(...)`.

La secuencia real es:

1. leer tipo de punto desde paleta,
2. leer tipo de camino,
3. resolver color,
4. construir `path_key`,
5. buscar posible ancla en otro camino,
6. crear el dict del punto,
7. persistirlo en `script_object.puntos_no_definidos`.

El modelo interno real que se almacena sigue esta forma:

```python
{
    "pos": pos,
    "tipo": tipo_punto,
    "color_id": color_id,
    "path_key": path_key,
    "tipo_camino": int(tipo_camino),
    "es_punto_comun": anchor is not None,
    "common_node_id": common_node_id if anchor is not None else None,
    "path_key_comun_con": str(anchor.get("path_key")) if anchor is not None else None,
    "orden": len(puntos),
}
```

Este modelo no está pensado como contrato final de integración. Está pensado como fuente estable y serializable desde la cual se derivan otras representaciones.

### Paso 5. Detección de puntos comunes entre caminos

Antes de insertar un nuevo punto, `handle_click_add_punto_no_definido(...)` intenta detectar si el clic cae suficientemente cerca de un punto perteneciente a otro camino.

La búsqueda la realiza `_find_common_anchor(...)`, que:

- trabaja con distancia XY,
- ignora puntos del mismo `path_key`,
- y devuelve el punto más cercano si está dentro de tolerancia.

Si se encuentra un ancla válida:

- el nuevo punto reutiliza esa posición,
- se garantiza un `common_node_id`,
- y se marca el punto como compartido.

Esta decisión simplifica el trabajo del usuario y evita exigir coincidencia exacta al pixel para representar conexiones lógicas.

### Paso 6. Cálculo de topología al finalizar

Al ejecutar `on_finalizar_puntos_no_definidos(...)`, el módulo deja de aceptar clics y calcula salidas derivadas a partir de la colección capturada.

Las dos estructuras principales son:

- `common_points_topology`
- `common_junctions`

La topología se genera en `_build_common_topology(...)`. El algoritmo opera en dos fases:

1. construir nodos explícitos desde `common_node_id`,
2. aplicar fallback por proximidad usando `detect_common_point_groups(...)`.

El resultado contiene:

- `nodes`
- `edges`
- `adjacency`

Esto permite responder de forma estructurada:

- qué caminos se cruzan,
- dónde se cruzan,
- y qué relación de conectividad existe entre ellos.

### Paso 7. Construcción de junctions derivadas

Una vez construida la topología, `handlers.py` deriva `common_junctions` con `_build_common_junctions(...)`.

Cada junction contiene:

- `node_id`
- `x`, `y`, `z`
- `path_keys`
- `path_count`
- `tipos_punto`
- `suggested_element`

La heurística `suggested_element` no genera geometría. Solo entrega una sugerencia de alto nivel sobre el tipo de elemento que podría representar ese nodo común.

```python
def _suggest_element(path_count: int, tipos_punto: list) -> str:
    tipos = set(tipos_punto)

    if path_count >= 3:
        return "t_sortida"

    if "bifurcación" in tipos or "bifurcacion" in tipos:
        return "t_sortida"

    if path_count == 2:
        has_inicio = "inicio" in tipos
        has_final = "final" in tipos
        if has_inicio and has_final:
            return "paso"
        if has_inicio or has_final:
            return "colze"
        return "paso"

    return "paso"
```

Esto mantiene el módulo útil para integración y para depuración, sin forzar todavía una capa de generación 3D.

### Paso 8. Construcción del contrato exportado

La versión actual del módulo ya no delega al consumidor la reconstrucción del formato exportado. Esa responsabilidad se trasladó al propio `ElementosNoDefinidos` mediante `build_nodos_export_data(...)`.

Esta función transforma `puntos_no_definidos` en una lista homogénea de nodos exportables:

- `id`
- `tipo`
- `coordenadas`
- `anteriores`
- `siguientes`
- `orden`
- `tipo_camino`
- `color_id`
- `path_key`
- `es_punto_comun`
- `common_node_id`
- `path_key_comun_con`

Snippet representativo:

```python
def build_nodos_export_data(puntos: list) -> list:
    by_key: dict[str, list] = defaultdict(list)
    for p in puntos:
        path_key = str(p.get("path_key") or "default")
        by_key[path_key].append(p)

    nodos = []
    seq_global = 1
    for path_key in sorted(by_key.keys()):
        group = by_key[path_key]
        group.sort(key=lambda item: int(item.get("orden", 0)))
```

La decisión de implementación aquí es importante:

- el almacenamiento interno mantiene `pos`,
- el contrato exportado expone `coordenadas`,
- y la conectividad `anteriores/siguientes` se construye secuencialmente por `path_key` y `orden`.

Al finalizar el flujo, `on_finalizar_puntos_no_definidos(...)` deja disponible:

- `script_object.nodos_export_data = build_nodos_export_data(puntos)`

Esto convierte al módulo en el dueño del contrato exportado, y simplifica a los consumidores.

### Paso 9. Preview visual en Allplan

`preview.py` implementa la capa visual del módulo.

Su responsabilidad se divide en:

1. construir geometría base por tipo de marcador,
2. convertirla a `ModelElement3D`,
3. resaltar puntos comunes con un halo adicional.

Las funciones de geometría base son:

- `_create_circle_lines(...)`
- `_create_square_lines(...)`
- `_create_triangle_lines(...)`
- `_create_rhombus_lines(...)`
- `_create_pentagon_lines(...)`

El método más importante de alto nivel es `draw_all_puntos_no_definidos(...)`, porque:

- dibuja todos los puntos persistidos,
- respeta el color asignado a cada camino,
- y destaca grupos comunes detectados con `detect_common_point_groups(...)`.

Esto permite validar visualmente la conectividad antes de exportar o seguir procesando.

### Paso 10. Persistencia del modelo interno

`serialization.py` se encarga de convertir `Point3D` a `dict` y viceversa.

La persistencia sigue basada en el modelo interno, no en el exportado. Es decir:

- se serializa `puntos_no_definidos`,
- no `nodos_export_data`.

```python
def serialize_puntos_no_definidos(puntos: List[dict]) -> List[dict]:
    out = []
    for p in puntos or []:
        pc = dict(p)
        if "pos" in pc and hasattr(pc["pos"], "X"):
            pc["pos"] = point_to_dict(pc["pos"])
        out.append(pc)
    return out
```

Esta separación es intencional:

- `puntos_no_definidos` es el storage canónico del módulo,
- `nodos_export_data` es una proyección derivada para consumo externo.

### Paso 11. Integración desde consumidores

La API pública expuesta por `__init__.py` sigue siendo el punto de integración recomendado:

```python
from ElementosNoDefinidos import (
    build_nodos_export_data,
    draw_all_puntos_no_definidos,
    draw_preview_at_cursor,
    handle_click_add_punto_no_definido,
    on_anadir_punto_no_definido,
    on_finalizar_puntos_no_definidos,
    serialize_puntos_no_definidos,
    deserialize_puntos_no_definidos,
)
```

En la integración actual con `Agua`, el consumidor:

1. activa el modo de captura,
2. delega la captura de clics al módulo,
3. delega el preview,
4. finaliza el modo,
5. y consume `script_object.nodos_export_data` sin reconstruir el formato.

Esto reduce duplicación, centraliza el contrato y hace más mantenible la evolución futura del módulo.
