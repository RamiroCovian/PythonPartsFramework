# Documentación Técnica: `ElementosDefinidos`

## 1. Resumen y Propósito

`ElementosDefinidos` encapsula la lógica necesaria para colocar, validar, previsualizar, serializar y finalmente materializar elementos 3D "definidos" sobre una instalación, con foco principal en el dominio de `AGUA`.

La feature resuelve dos necesidades principales:

- Unificar la lógica de captura y validación para elementos como `T sortida`, `Colze base`, `Clau de Pas` y `Tapón`, evitando que cada script anfitrión replique reglas de negocio y acceso a paleta.
- Preparar una representación estructurada de la red colocada, incluyendo:
  - marcadores y puntos libres,
  - topología de `common_points`,
  - y un export de nodos con `id`, `tipo`, `coordenadas`, `anterior` y `siguientes`.

Desde el punto de vista técnico, el módulo desacopla tres responsabilidades que en integraciones como `Agua/fontaneria.py` suelen aparecer mezcladas:

- Lectura de configuración desde `build_ele`.
- Reglas de catálogo y validación de ubicación.
- Conversión del estado capturado en estructuras exportables y/o en elementos 3D definitivos.

## 2. Arquitectura y Componentes Clave

### Archivos principales

- `ElementosDefinidos/base.py`
  Define las abstracciones base (`BaseDefinedElement`, `BaseMacroElement`, `CallbackDefinedElement`) y el vocabulario común de funciones posibles (`inicio`, `final`, `intermedio_ordenado`, `intermedio_libre`, `bifurcación`).

- `ElementosDefinidos/catalogo.py`
  Centraliza el catálogo por instalación, las etiquetas de UI, el mapeo `label -> key` y las reglas de validación de ubicación por tipo de elemento.

- `ElementosDefinidos/palette.py`
  Encapsula la lectura segura de parámetros desde `build_ele`: tipo de elemento, radio, modo de punto, tipo de punto libre, tolerancia y cota `Z`.

- `ElementosDefinidos/capture.py`
  Implementa `ElementPointCaptureMixin`, que integra captura de punto libre, preview y alta de `element_markers` en interactores tipo `PolylineInteractor`.

- `ElementosDefinidos/handlers.py`
  Expone funciones operativas para scripts host: activar captura, agregar marcadores, manejar puntos libres, aplicar rotaciones y construir datos de `common_points`.

- `ElementosDefinidos/creation.py`
  Recorre `free_placed_points` y `element_markers` para delegar la creación real del 3D al callback del script host.

- `ElementosDefinidos/serialization.py`
  Convierte `Point3D` a estructuras serializables y viceversa para persistir estado.

- `ElementosDefinidos/common_points.py`
  Implementa la detección de puntos comunes por proximidad, la construcción de topología (`nodes`, `edges`, `adjacency`) y la generación de `junctions`.

- `ElementosDefinidos/optimizer_graph.py`
  Convierte `element_markers`, `saved_paths` y `free_placed_points` a una lista exportable de nodos y a un contenedor listo para consumo externo.

- `ElementosDefinidos/__init__.py`
  Reexporta la API pública del módulo.

### Relación entre componentes

El flujo lógico del módulo es el siguiente:

1. `palette.py` obtiene valores desde `build_ele`.
2. `catalogo.py` traduce labels y valida reglas de negocio.
3. `capture.py` o `handlers.py` convierten la interacción del usuario en estado capturado:
   - `element_markers`
   - `free_placed_points`
4. `serialization.py` permite persistir/restaurar ese estado.
5. `creation.py` materializa el 3D usando callbacks del script host.
6. `common_points.py` deriva topología de intersecciones sobre `saved_paths`.
7. `optimizer_graph.py` exporta la red como nodos conectados.

### Dependencias clave

- Dependencias Allplan opcionales, cargadas de forma defensiva:
  - `NemAll_Python_Geometry`
  - `NemAll_Python_Utility`
  - `NemAll_Python_BasisElements`
  - `NemAll_Python_BaseElements`
- El módulo evita acoplarse a una implementación concreta de creación 3D: esa responsabilidad sigue en el script consumidor mediante callbacks.

## 3. Flujo de Implementación (Paso a Paso)

### Paso 1. Definir el vocabulario común y las capacidades base

La base del módulo establece un contrato semántico único para todos los elementos definidos. En `base.py` se fija el conjunto de funciones válidas y el mapeo lógico a roles.

```python
POSIBLES_FUNCIONES = [
    "inicio",
    "final",
    "intermedio_ordenado",
    "intermedio_libre",
    "bifurcación",
]

FUNCION_TO_ROLE = {
    "inicio": 0,
    "final": 3,
    "intermedio_ordenado": 1,
    "intermedio_libre": 1,
    "bifurcación": 2,
}
```

Esto evita que cada integración redefina qué significa un inicio, un final o una bifurcación.

### Paso 2. Centralizar el catálogo y las reglas de negocio

En `catalogo.py` se modelan las restricciones de colocación por instalación. Para `AGUA`, la lógica de negocio queda encapsulada y no repartida por handlers o UI.

Ejemplo de definición por elemento:

```python
return {
    T_SORTIDA: ["intermedio_ordenado", "intermedio_libre"],
    COLZE_BASE: ["inicio", "final"],
    CLAU_DE_PAS: ["intermedio_ordenado", "intermedio_libre"],
    TAPON: ["inicio", "final"],
}
```

La validación se resuelve mediante `validar_ubicacion_elemento(...)`, que devuelve un `bool` más un mensaje de error listo para UI. Esto permite que el host solo pregunte si una ubicación es válida sin conocer reglas específicas.

### Paso 3. Leer configuración desde la paleta sin acoplar el host

`palette.py` encapsula la lectura de:

- `DefinedElementType`
- `ElementRadius`
- `TipoPuntoLibre`
- `ToleranciaSeleccionPunto`
- `ElementZAbs`
- `ElementPointMode`

Esto resuelve dos problemas:

- Evitar acceso repetitivo y frágil a `build_ele`.
- Normalizar valores por defecto cuando faltan parámetros o vienen con datos inválidos.

### Paso 4. Capturar puntos y construir estado intermedio

La captura se implementa de dos maneras complementarias:

- `ElementPointCaptureMixin` en `capture.py`, pensado para integrarse dentro de un interactor.
- Funciones explícitas en `handlers.py`, pensadas para scripts host que no quieran usar mixins.

Cuando el usuario agrega un elemento sobre polilínea, el resultado todavía no es un 3D definitivo sino un `marker`:

```python
marker = {
    "kind": kind,
    "pos": pos,
    "radius": radius,
    "element_type": element_type,
    "z_abs": z_abs,
    "path_idx": path_idx,
    "pt_idx": pt_idx,
}
```

Cuando el usuario opera en "modo puntos libres", se almacena un registro en `free_placed_points`:

```python
{
    "pos": pos,
    "flag": flag,
    "element_type": element_type,
    "order": order,
    "rot_x": rot_x,
    "rot_y": rot_y,
    "rot_z": rot_z,
}
```

La decisión de diseño es importante: el sistema primero captura intención y contexto, y recién después crea geometría real.

### Paso 5. Persistir y restaurar el estado capturado

`serialization.py` transforma puntos Allplan a dicts simples (`X`, `Y`, `Z`) para que `element_markers` y `free_placed_points` puedan guardarse dentro del estado del script.

Esto hace que la feature sea reentrante: el usuario puede cerrar, reabrir o rehidratar el estado sin perder la estructura colocada.

### Paso 6. Crear los elementos 3D reales

La creación definitiva está desacoplada en `creation.py`. El módulo no conoce cómo crear un `TeSortidaCreateElement` o un `ColzeBaseCreateElement`; solo invoca el callback del host con el contexto correcto.

Además, para `free_placed_points`, aplica rotaciones específicas por punto antes de crear el elemento y restaura luego los valores originales de paleta:

```python
for attr_name, fp_key in rotation_keys:
    param = getattr(build_ele, attr_name, None)
    prev_values[attr_name] = param.value
    fp_val = fp.get(fp_key, None)
    if fp_val is not None:
        param.value = float(fp_val)
```

Esto asegura que la preview, la edición y la creación final compartan la misma orientación.

### Paso 7. Detectar `common_points` y construir topología

La implementación en `common_points.py` replica el patrón de `ElementosNoDefinidos`, pero adaptado a `saved_paths`.

El proceso es:

1. Aplanar `saved_paths` a una lista de puntos anotados con:
   - `path_idx`
   - `pt_idx`
   - `path_key`
   - `tipo`
2. Agrupar por proximidad espacial dentro de una tolerancia.
3. Filtrar solo grupos que involucren al menos 2 caminos distintos.
4. Construir:
   - `nodes`
   - `edges`
   - `adjacency`

La función principal es `build_common_points_topology(...)`, que devuelve una estructura con:

```python
{
    "node_count": ...,
    "edge_count": ...,
    "nodes": [...],
    "edges": [...],
    "adjacency": {...},
    "points": [...],
}
```

Luego `build_common_junctions(...)` traduce cada nodo común a una estructura más fácil de consumir por lógica de negocio, añadiendo:

- `tipos_punto`
- `element_types`
- `suggested_element`

La heurística para `suggested_element` está pensada para orientar automatismos posteriores, por ejemplo sugerir `t_sortida` cuando confluyen 3 o más caminos.

### Paso 8. Exponer la topología desde el flujo operativo

En `handlers.py` se añadió `build_common_user_points_data(...)`, que encapsula el uso de `common_points.py` dentro del flujo del interactor y guarda el resultado tanto en `intr` como en `script_object`.

```python
topology = build_common_points_topology(
    saved_paths=paths,
    tolerance_mm=tolerance_mm,
)
junctions = build_common_junctions(
    saved_paths=paths,
    topology=topology,
    element_markers=element_markers,
    tolerance_mm=tolerance_mm,
)
```

De esta forma, el script host no necesita repetir wiring ni nombres de atributos.

### Paso 9. Exportar la red como lista de nodos conectados

`optimizer_graph.py` transforma `element_markers`, `saved_paths` y `free_placed_points` en una lista exportable de nodos.

La lógica realiza estas tareas:

1. Resolver a qué camino pertenece cada `element_marker`.
2. Calcular un orden estable dentro del camino.
3. Normalizar el tipo lógico del nodo:
   - `inicio`
   - `final`
   - `codo`
   - `union`
4. Generar IDs semánticos.
5. Completar conectividad:
   - `anterior`
   - `siguientes`

El shape resultante por nodo es:

```python
{
    "id": "...",
    "tipo": "...",
    "coordenadas": {"x": ..., "y": ..., "z": ...},
    "anterior": "... | None",
    "siguientes": ["..."],
    "path_key": "...",
    "path_idx": ...,
    "element_type": "...",
    "source": "...",
}
```

Y el contenedor de exportación:

```python
{
    "id": "elementos_definidos",
    "nombre": "Elementos Definidos",
    "nodos": [...]
}
```

Un detalle relevante es el tratamiento de marcadores intermedios libres: si existe `saved_paths`, se proyectan para obtener una posición relativa coherente dentro del camino; si no existe, se conserva un orden estable por captura.

### Paso 10. Publicar una API pública coherente

`__init__.py` expone una API única para los consumidores del módulo. Esto permite integrar desde `Agua` o desde cualquier otro script sin imports internos frágiles.

Las piezas más relevantes publicadas son:

- captura y handlers
- serialización
- creación
- `detect_common_point_groups`
- `build_common_points_topology`
- `build_common_junctions`
- `build_common_user_points_data`
- `build_nodos_export_data`
- `build_optimizer_graph_json`

## Cierre

La implementación de `ElementosDefinidos` no se limita a dibujar o crear elementos 3D. Su valor principal está en haber convertido una lógica dispersa de UI, validación, preview, persistencia y exportación en un módulo cohesivo, reutilizable y extensible.

Para futuras integraciones, el patrón recomendado es:

1. Delegar lectura de paleta y validación al módulo.
2. Guardar primero estado estructurado (`element_markers`, `free_placed_points`).
3. Crear 3D al final mediante callbacks del host.
4. Derivar topología y export de nodos desde ese mismo estado, sin recalcular reglas de negocio en el script consumidor.
