# ElementosNoDefinidos

## 1. Propósito actual del módulo

`ElementosNoDefinidos` permite capturar puntos de usuario para describir caminos cuando todavía no existen elementos 3D definitivos por cada punto.

Su responsabilidad actual es:

1. Capturar puntos indicativos del usuario.
2. Guardar su tipo lógico.
3. Asociar cada punto a un camino.
4. Detectar conexiones entre caminos distintos.
5. Preparar una lista estructurada de caminos y nodos para que `Caminos_Optimos_Lib` la consuma.

Importante:

- `ElementosNoDefinidos` ya no debe considerarse el generador del JSON final completo de optimización.
- El JSON final completo pertenece al flujo de `Caminos_Optimos_Lib`.
- Este módulo prepara la parte de entrada correspondiente a los caminos.


## 2. Qué problema resuelve

Hay casos en los que el usuario conoce el recorrido lógico, pero todavía no quiere modelar geometría final.

En ese escenario, el módulo permite marcar:

- dónde empieza el camino,
- dónde termina,
- qué puntos intermedios son obligatorios o libres,
- qué caminos distintos se conectan o cruzan,
- y qué color o agrupación visual pertenece a cada recorrido.

La salida de este módulo no es la ruta optimizada final, sino la base de datos de entrada para que otro sistema la procese.


## 3. Qué entrega exactamente

Al finalizar la captura (`1020`), el módulo deja preparada en memoria la estructura que `Caminos_Optimos_Lib` puede leer como base de entrada de multi-camino.

Las dos propiedades principales son:

- `script_object.caminos_optimos_caminos_data`
- `script_object.caminos_optimos_input_data`

La diferencia entre ambas:

### `script_object.caminos_optimos_caminos_data`

Contiene sólo la lista de caminos:

```python
[
    {
        "id": "camino_1",
        "nombre": "Camino 1 (...)",
        "nodos": [...]
    }
]
```

### `script_object.caminos_optimos_input_data`

Contiene una estructura parcial lista para integrarse en el input global:

```python
{
    "id": "elementos_no_definidos",
    "nombre": "Elementos No Definidos",
    "caminos": [...]
}
```

Esta estructura todavía no incluye:

- `techo`
- `subdivisiones_is`
- `tubos_is`
- `obstaculos`
- `configuracion`

Esos bloques deben añadirse en el flujo que construya el input completo para `Caminos_Optimos_Lib`.


## 4. Flujo funcional vigente

### Paso 1. Activación

El usuario entra en modo de puntos no definidos mediante el evento `1019`.

### Paso 2. Captura

Cada clic agrega un punto a:

- `script_object.puntos_no_definidos`

Cada punto conserva:

- posición,
- tipo,
- color,
- `path_key`,
- tipo de camino,
- información de puntos comunes si aplica,
- orden de captura.

### Paso 3. Finalización

Al ejecutar `1020`:

1. Se calcula la topología de puntos comunes.
2. Se generan junctions.
3. Se adapta la lista de puntos al formato esperado por `Caminos_Optimos_Lib`.
4. Se guarda esa estructura en memoria.

No se crea automáticamente la polilínea final de negocio.


## 5. Archivos importantes

### `constants.py`

Define:

- tipos de punto,
- etiquetas de UI,
- formas geométricas del preview.

Tipos base:

- `inicio`
- `final`
- `intermedio_libre`
- `intermedio_ordenado`
- `bifurcación`


### `palette.py`

Lee desde `build_ele` los parámetros de paleta.

Responsabilidades principales:

- obtener tipo de camino,
- obtener tipo de punto,
- obtener color,
- generar `path_key`,
- leer flags de detección de puntos comunes,
- leer tolerancia de detección.


### `preview.py`

Se ocupa del preview visual.

Responsabilidades:

- crear la geometría de los marcadores,
- dibujar la forma correcta por tipo,
- mostrar los puntos capturados.


### `serialization.py`

Convierte `puntos_no_definidos` a un formato serializable y restaura el estado al cargar.


### `common_points.py`

Agrupa puntos cercanos de caminos distintos para identificar cruces o conexiones.


### `handlers.py`

Es el centro del flujo operativo.

Hace:

- activación del modo captura,
- lectura del clic,
- asignación de tipo/color/path_key,
- detección de puntos comunes,
- cálculo de topología,
- cálculo de junctions,
- preparación de la estructura para `Caminos_Optimos_Lib`.


### `caminos_optimos_adapter.py`

Es el archivo más importante del contrato actual.

Su responsabilidad es transformar `puntos_no_definidos` a la estructura de caminos/nodos que entiende `Caminos_Optimos_Lib`.

Funciones principales:

- `build_caminos_optimos_caminos_data(...)`
- `build_caminos_optimos_partial_input(...)`


### `optimizer_graph.py`

Este archivo existía para construir un grafo tipo salida.

Hoy no es la pieza principal del contrato con `Caminos_Optimos_Lib`.

La pieza principal para integración actual es `caminos_optimos_adapter.py`.


## 6. Modelo de datos interno

Cada punto capturado se guarda como `dict` en:

- `script_object.puntos_no_definidos`

Ejemplo conceptual:

```python
{
    "pos": <Point3D-like>,
    "tipo": "inicio",
    "color_id": 1,
    "path_key": "modo:1|color:1",
    "tipo_camino": 1,
    "es_punto_comun": False,
    "common_node_id": None,
    "path_key_comun_con": None,
    "orden": 0,
}
```

Campos relevantes:

- `pos`
  Posición del punto.

- `tipo`
  Tipo lógico capturado en UI.

- `color_id`
  Color visual del punto y criterio de agrupación si no existe `PathId`.

- `path_key`
  Clave del camino.

- `tipo_camino`
  Modo lógico de camino.

- `common_node_id`
  Identificador compartido si el punto conecta con otro camino.

- `orden`
  Orden de captura.


## 7. Cómo se define un camino

Un camino se construye agrupando puntos por `path_key`.

`path_key` se obtiene así:

1. Si existe `PathId`, se usa como prioridad.
2. Si no existe, se genera un fallback con:
   - tipo de camino,
   - color.

Ejemplos:

- `path:3`
- `modo:1|color:1`
- `modo:1|color:4`


## 8. Detección de puntos comunes

Cuando la detección está activa, al agregar un punto nuevo el sistema revisa si hay un punto de otro camino dentro de una tolerancia.

Si lo encuentra:

- el nuevo punto se ancla a esa posición,
- ambos quedan relacionados con el mismo `common_node_id`,
- se registra la relación entre caminos.

Esto sirve para:

- identificar cruces,
- detectar conexiones,
- construir topología,
- enriquecer el contexto de los recorridos.


## 9. Topología y junctions

Al finalizar (`1020`) se calculan dos salidas auxiliares:

### `script_object.common_points_topology`

Incluye:

- nodos comunes,
- aristas entre caminos,
- adyacencia.

### `script_object.common_junctions`

Incluye:

- posición del nodo común,
- caminos involucrados,
- tipos de punto involucrados,
- sugerencia heurística de elemento.

Estas estructuras son útiles para análisis y depuración, pero no son el input principal del optimizador.


## 10. Contrato actual con `Caminos_Optimos_Lib`

`Caminos_Optimos_Lib` espera, para la parte de caminos, algo con este shape:

```json
{
  "caminos": [
    {
      "id": "camino_1",
      "nombre": "Camino 1",
      "nodos": [
        {
          "id": "A1",
          "tipo": "inicio",
          "coordenadas": { "x": 0, "y": 0, "z": 0 },
          "anteriores": [],
          "siguientes": ["O1_1"]
        },
        {
          "id": "O1_1",
          "tipo": "orden_obligatorio",
          "coordenadas": { "x": 1000, "y": 0, "z": 0 },
          "anteriores": ["A1"],
          "siguientes": ["B1"]
        },
        {
          "id": "L1_1",
          "tipo": "orden_libre",
          "coordenadas": { "x": 1200, "y": 200, "z": 0 },
          "anteriores": [],
          "siguientes": []
        },
        {
          "id": "B1",
          "tipo": "fin",
          "coordenadas": { "x": 2000, "y": 0, "z": 0 },
          "anteriores": ["O1_1"],
          "siguientes": []
        }
      ]
    }
  ]
}
```

Esto coincide con lo que normaliza `Caminos_Optimos_Lib` en:

- `src/procesamiento/entrada.py`


## 11. Mapeo actual de tipos

El adaptador hace esta conversión:

- `inicio` -> `inicio`
- `final` -> `fin`
- `intermedio_libre` -> `orden_libre`
- `intermedio_ordenado` -> `orden_obligatorio`
- `bifurcación` -> `orden_obligatorio`

Esto se implementa en:

- [caminos_optimos_adapter.py](c:\Users\ramir\Documents\Nemetschek\Allplan\2025\Usr\Local\PythonPartsScripts\ElementosNoDefinidos\caminos_optimos_adapter.py#L36)

Observación importante:

- `Caminos_Optimos_Lib` no entiende de forma nativa el tipo `bifurcación`.
- Por eso hoy se traduce a `orden_obligatorio`.
- Si el diseñador de `Caminos_Optimos_Lib` quiere otra semántica, esta es una de las primeras reglas a revisar.


## 12. Generación de IDs

El adaptador genera IDs estables por camino:

- `A1`, `A2`, ... para inicios
- `B1`, `B2`, ... para fines
- `O1_1`, `O2_1`, ... para obligatorios
- `L1_1`, `L2_1`, ... para libres

Esto se hace en:

- [caminos_optimos_adapter.py](c:\Users\ramir\Documents\Nemetschek\Allplan\2025\Usr\Local\PythonPartsScripts\ElementosNoDefinidos\caminos_optimos_adapter.py#L49)


## 13. Encadenado lógico

El adaptador encadena sólo:

- `inicio -> obligatorios -> fin`

Los puntos `orden_libre` se entregan sin cadena forzada:

- `anteriores = []`
- `siguientes = []`

Esto está alineado con el modelo de `Caminos_Optimos_Lib`, donde los puntos libres se consideran opcionales.


## 14. Dónde queda preparada la información

Al finalizar el flujo, `handlers.py` deja:

- `script_object.caminos_optimos_caminos_data`
- `script_object.caminos_optimos_input_data`

Esto ocurre en:

- [handlers.py](c:\Users\ramir\Documents\Nemetschek\Allplan\2025\Usr\Local\PythonPartsScripts\ElementosNoDefinidos\handlers.py#L584)


## 15. Qué NO entrega todavía

`ElementosNoDefinidos` no entrega por sí solo el input completo de `Caminos_Optimos_Lib`.

Todavía falta integrar:

- `techo`
- `subdivisiones_is`
- `tubos_is`
- `obstaculos`
- `configuracion`

Eso significa:

- el módulo sí deja lista la parte de caminos,
- pero otro paso debe mezclarla con el resto del contexto del proyecto.


## 16. Integración con `fontaneria.py`

`fontaneria.py` usa:

- `on_anadir_punto_no_definido(...)`
- `handle_click_add_punto_no_definido(...)`
- `on_finalizar_puntos_no_definidos(...)`

Eventos relevantes:

- `1019`: activar modo de captura
- `1020`: finalizar y preparar lista para `Caminos_Optimos_Lib`

Decisión actual:

- `1020` no materializa automáticamente polilíneas;
- `1020` prepara datos para consumo posterior.


## 17. Logs esperables

### Activación

```text
[PUNTOS NO DEFINIDOS] Modo añadir activo (1019). Clics sucesivos añaden puntos hasta 1020.
```

### Punto añadido

```text
[PUNTOS NO DEFINIDOS] Punto añadido: tipo=inicio, color_id=1, path_key=modo:1|color:1, total=1
```

### Sin snap

```text
[PUNTOS COMUNES] Sin snap: path=modo:1|color:1, tolerancia=50.0mm, puntos_previos=0, mas_cercano=n/a
```

### Con snap

```text
[PUNTOS COMUNES] Snap aplicado: nuevo_path=modo:1|color:4 -> anclado_con=modo:1|color:1, node_id=CP-1
```

### Finalización

```text
[PUNTOS COMUNES] Topología generada: nodos=1, conexiones=1
[PUNTOS COMUNES] Junctions generadas: 1
[CAMINOS OPTIMOS] Lista preparada para generador JSON: caminos=2
```


## 18. Qué revisar si algo falla

### Si los caminos salen mal agrupados

Revisar:

- `palette.py`
- `get_path_key_puntos(...)`


### Si la detección de puntos comunes no funciona

Revisar:

- `common_points.py`
- `_find_common_anchor(...)`
- tolerancia configurada


### Si el contrato con `Caminos_Optimos_Lib` no coincide

Revisar primero:

- `caminos_optimos_adapter.py`

Ahí está concentrado:

- el mapeo de tipos,
- la generación de IDs,
- la estructura de `nodos`,
- el encadenado lógico.


## 19. Qué debe revisar el compañero que mantiene `Caminos_Optimos_Lib`

Si esta documentación se comparte con la persona que diseñó `Caminos_Optimos_Lib`, los puntos más importantes a validar con él son:

1. si el mapeo de tipos es correcto,
2. si `bifurcación` debe seguir yendo a `orden_obligatorio`,
3. si la cadena `inicio -> obligatorios -> fin` es suficiente,
4. si los `orden_libre` deben quedarse sin `anteriores/siguientes`,
5. si necesita más metadatos además de `coordenadas`, `tipo`, `id`, `anteriores`, `siguientes`.


## 20. Resumen corto

`ElementosNoDefinidos` captura puntos de usuario, los agrupa por camino, detecta conexiones entre caminos y transforma esa información a la estructura de caminos/nodos que usa `Caminos_Optimos_Lib`. No genera el JSON completo de optimización; prepara la parte de caminos para que otro flujo la integre con techo, IS, obstáculos y configuración.

