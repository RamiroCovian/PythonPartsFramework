# Documentación Técnica: ElementosDefinidos

## 1. Resumen y Propósito

`ElementosDefinidos` es un módulo reutilizable para gestionar elementos especiales de una instalación, como accesorios, piezas de conexión o macros 3D, sin duplicar la lógica en cada script de instalación.

La feature resuelve dos problemas principales:

1. Evitar que cada instalación (`Agua`, `Electricidad`, etc.) implemente por separado la misma lógica de interacción:
   - selección y deselección de elementos,
   - arrastre,
   - rotación desde paleta,
   - preview 2D/3D,
   - serialización y restauración de estado.

2. Estandarizar la exportación estructurada de la información para depuración y consumo posterior:
   - nodos,
   - caminos,
   - relaciones `anteriores` y `siguientes`,
   - puntos comunes (`common_points`),
   - `junctions`,
   - grafo exportable en JSON.

En términos funcionales, el módulo permite que un script consumidor declare qué elementos existen y cómo generar su geometría final, mientras `ElementosDefinidos` se encarga del ciclo completo de interacción, visualización y export.

## 2. Arquitectura y Componentes Clave

### Archivos principales

- [ElementosDefinidos/__init__.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/__init__.py)  
  Punto de entrada público del módulo. Reexporta helpers, handlers, controllers, façade y utilidades de export.

- [ElementosDefinidos/base.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/base.py)  
  Define las abstracciones base para elementos definidos y macros (`BaseDefinedElement`, `BaseMacroElement`, `CallbackDefinedElement`).

- [ElementosDefinidos/catalogo.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/catalogo.py)  
  Centraliza el catálogo de elementos por instalación y las reglas de validación de ubicación.

- [ElementosDefinidos/palette.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/palette.py)  
  Lee parámetros de paleta (`DefinedElementType`, `TipoPuntoLibre`, `RotX/Y/Z`, tolerancias y cotas).

- [ElementosDefinidos/handlers.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/handlers.py)  
  Núcleo operativo del módulo. Gestiona eventos, altas de elementos, puntos libres, construcción de export y escritura de JSON de debug.

- [ElementosDefinidos/interaction.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/interaction.py)  
  Helpers reutilizables de interacción visual:
  - matrices de rotación,
  - sincronización paleta <-> modelo,
  - highlight,
  - etiquetas de rotación,
  - dibujo de preview 3D.

- [ElementosDefinidos/free_points_controller.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/free_points_controller.py)  
  Controlador de interacción para `free_placed_points`.

- [ElementosDefinidos/element_markers_controller.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/element_markers_controller.py)  
  Controlador de interacción para `element_markers`, correspondiente al flujo clásico `1015/1016`.

- [ElementosDefinidos/controller_facade.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/controller_facade.py)  
  Fachada pública que unifica la integración del módulo en scripts consumidores.

- [ElementosDefinidos/common_points.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/common_points.py)  
  Construye topología de puntos comunes y `junctions`.

- [ElementosDefinidos/optimizer_graph.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/optimizer_graph.py)  
  Convierte estado interactivo en un export estructurado con nodos, caminos y segmentos.

- [ElementosDefinidos/creation.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/creation.py)  
  Delega la creación del 3D final a callbacks del script consumidor.

- [ElementosDefinidos/serialization.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/serialization.py)  
  Serializa y deserializa `element_markers` y `free_placed_points`.

### Relación entre componentes

La arquitectura sigue una separación por responsabilidades:

1. `catalogo.py` y `palette.py` resuelven configuración y semántica.
2. `handlers.py` ejecuta la lógica de negocio del alta y del export.
3. `interaction.py` encapsula comportamiento visual y utilidades de rotación.
4. `free_points_controller.py` y `element_markers_controller.py` encapsulan interacción de mouse y preview.
5. `controller_facade.py` unifica ambos controladores detrás de una sola API.
6. `common_points.py` y `optimizer_graph.py` transforman el estado interactivo en topología y JSON exportable.
7. `creation.py` convierte el estado final en elementos Allplan definitivos.

### Dependencias clave

- `NemAll_Python_Geometry`
- `NemAll_Python_BaseElements`
- `NemAll_Python_BasisElements`
- `NemAll_Python_Utility`

Estas dependencias se usan de forma defensiva: el módulo intenta importarlas y, cuando no están disponibles, degrada comportamiento o evita lanzar excepciones durante análisis estático.

## 3. Flujo de Implementación (Paso a Paso)

### Paso 1. Definir una API pública reutilizable

El módulo se expone desde [__init__.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/__init__.py), evitando imports profundos desde los scripts consumidores.

La integración moderna se apoya en la fachada de [controller_facade.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/controller_facade.py).

```python
from ElementosDefinidos import (
    DefinedElementsFacadeConfig,
    ensure_defined_elements_interaction_state,
    handle_defined_elements_mouse_message,
    draw_defined_elements_preview,
)
```

Con esto, el script consumidor no necesita coordinar manualmente `free_points_controller` y `element_markers_controller`.

### Paso 2. Modelar el dominio de elementos definidos

[base.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/base.py) define las clases base que representan un elemento definido reutilizable.

El patrón principal es:

- `BaseDefinedElement`: interfaz común para preview y geometría final.
- `BaseMacroElement`: especializado en elementos basados en macro.
- `CallbackDefinedElement`: especializado en elementos construidos desde callbacks Python.

Esto desacopla la interacción del mecanismo concreto de generación geométrica.

### Paso 3. Resolver catálogo y configuración desde paleta

[catalogo.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/catalogo.py) normaliza:

- elementos disponibles por instalación,
- funciones permitidas por elemento,
- traducción entre labels de UI y claves internas,
- validación de ubicación.

[palette.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/palette.py) se encarga de leer valores del `build_ele`, como:

- tipo de elemento,
- tipo de punto libre,
- rotaciones,
- tolerancia de selección,
- cota absoluta.

Esta separación permite mantener la lógica de negocio independiente de la representación XML de la paleta.

### Paso 4. Encapsular interacción visual y rotación

[interaction.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/interaction.py) concentra el comportamiento reutilizable de preview.

Responsabilidades principales:

- leer `RotX`, `RotY`, `RotZ` desde paleta,
- construir matrices de rotación,
- sincronizar rotación del elemento con la paleta,
- dibujar modelos 3D,
- resaltar el elemento activo,
- dibujar etiquetas de rotación.

Snippet representativo:

```python
def sync_rotation_from_palette(build_ele: Any, data: dict) -> dict:
    data["rot_x"] = get_rotation_value(build_ele, "RotX", "ElementRotX")
    data["rot_y"] = get_rotation_value(build_ele, "RotY", "ElementRotY")
    data["rot_z"] = get_rotation_value(build_ele, "RotZ", "ElementRotZ")
    return data
```

Este helper evita que cada script consumidor tenga que repetir lectura y sincronización de rotaciones.

### Paso 5. Separar los dos modos de interacción

El módulo soporta dos modelos distintos de trabajo:

1. `element_markers`  
   Flujo clásico donde primero se captura un punto y luego se agrega el elemento.

2. `free_placed_points`  
   Flujo tipo “modo puntos libres”, donde el clic sobre el plano crea directamente el elemento lógico.

#### 5.1 Controlador de puntos libres

[free_points_controller.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/free_points_controller.py) encapsula:

- selección,
- deselección,
- arrastre,
- doble clic para recolocación,
- umbral de drag,
- preview del cursor,
- highlight del elemento seleccionado,
- sincronización de rotación con paleta,
- guardado y restauración del estado efímero.

#### 5.2 Controlador de markers

[element_markers_controller.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/element_markers_controller.py) encapsula el flujo equivalente para `element_markers`.

Ambos controladores comparten utilidades de [interaction.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/interaction.py), pero mantienen su lógica de estado por separado.

### Paso 6. Unificar la integración mediante una fachada

La fachada de [controller_facade.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/controller_facade.py) es la capa que un consumidor como `Agua` debe usar.

Responsabilidades:

- inicializar estado,
- preparar eventos previos a `1015`, `1016`, `1017`, `1018`,
- enrutar cambios de propiedades,
- enrutar mensajes de mouse,
- dibujar preview agregado.

Snippet representativo:

```python
config = DefinedElementsFacadeConfig(
    get_model_list_callback=...,
    create_final_element_callback=...,
    fallback_preview_factory=...,
)

handle_defined_elements_mouse_message(
    script_object,
    intr,
    mouse_msg,
    pnt,
    msg_info,
    config,
)
```

El objetivo es que el script consumidor provea callbacks de dominio y no tenga que conocer el detalle interno del módulo.

### Paso 7. Gestionar altas y persistencia en handlers

[handlers.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/handlers.py) funciona como núcleo de negocio del módulo.

Puntos principales:

- alta de `element_markers`,
- alta de `free_placed_points`,
- captura de punto,
- finalización del modo de puntos libres,
- sincronización con estado serializado,
- actualización automática del export.

#### 7.1 Alta de puntos libres

La función `handle_click_add_free_point(...)`:

1. Lee `flag` y `element_type` desde paleta.
2. Valida si el elemento puede colocarse en esa función.
3. Calcula rotaciones iniciales.
4. Resuelve `path_key`.
5. Intenta hacer snap a un punto común preexistente.
6. Guarda el punto en `script_object.free_placed_points`.
7. Dispara reconstrucción del export de debug.

Snippet simplificado:

```python
free_list.append(
    {
        "pos": pos,
        "flag": flag,
        "element_type": element_type,
        "order": order,
        "path_key": path_key,
        "es_punto_comun": anchor is not None,
        "common_node_id": common_node_id if anchor is not None else None,
        "path_key_comun_con": ...,
        "rot_x": rot_x,
        "rot_y": rot_y,
        "rot_z": rot_z,
    }
)
```

### Paso 8. Incorporar puntos comunes explícitos

La implementación de puntos comunes sigue el mismo principio de `ElementosNoDefinidos`, pero adaptado a `free_placed_points`.

#### 8.1 Detección en el momento del alta

En [handlers.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/handlers.py) se añadieron estos helpers:

- `_find_common_anchor(...)`
- `_next_common_node_id(...)`
- `_ensure_anchor_common_node_id(...)`

La lógica es:

1. buscar un punto de otro `path_key` dentro de tolerancia,
2. si existe, usar su posición como ancla,
3. garantizar que el ancla tenga `common_node_id`,
4. marcar el nuevo punto como común.

#### 8.2 Convención de caminos para definidos

Como `free_placed_points` no venían con `path_key` explícito, el módulo define una regla reusable:

- `inicio` abre un camino lógico nuevo,
- los puntos intermedios continúan el camino actual,
- `final` cierra el camino actual.

Esto se resuelve con:

- `_next_free_path_key(...)`
- `_resolve_free_point_path_key(...)`
- `_close_free_point_path_if_needed(...)`

Esta convención permite que la detección de puntos comunes entre caminos tenga semántica consistente también en instalaciones futuras.

### Paso 9. Construir topología y junctions

[common_points.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/common_points.py) construye:

- grupos de puntos comunes por proximidad,
- `nodes` de topología,
- `edges` entre caminos,
- `adjacency`,
- `common_junctions` con sugerencias de elemento.

En [handlers.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/handlers.py), `build_common_user_points_data(...)` decide qué estrategia usar:

- si hay `free_placed_points`, construye topología a partir de esos puntos,
- si no, usa `saved_paths` y `element_markers`.

Esto evita perder información topológica en flujos donde todavía no existe una polilínea persistida.

### Paso 10. Exportar nodos y grafo

[optimizer_graph.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/optimizer_graph.py) genera dos vistas:

1. `build_nodos_export_data(...)`
2. `build_optimizer_graph_json(...)`

#### 10.1 Criterio de conexión

La conectividad sigue el mismo criterio lineal que `ElementosNoDefinidos`:

1. agrupar por `path_key`,
2. ordenar por `sort_key` u `order`,
3. asignar `anteriores` y `siguientes` por vecindad inmediata.

#### 10.2 IDs de nodos

Si un punto ya trae `common_node_id`, ese valor se preserva como `id` exportado.

```python
def _build_node_id(item: dict, path_index: int, counters: dict, node_tipo: str) -> str:
    data = item.get("data", {}) or {}
    common_node_id = data.get("common_node_id")
    if common_node_id:
        return str(common_node_id)
```

Esto permite que el contrato final refleje explícitamente los puntos comunes detectados al momento del alta.

### Paso 11. Escribir JSON de debug

`build_defined_elements_export_data(...)` en [handlers.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/handlers.py) guarda:

- `script_object.nodos_export_data`
- `script_object.optimizer_graph_data`
- `intr.nodos_export_data`
- `intr.optimizer_graph_data`

Además escribe un JSON de debug configurable mediante:

- `defined_elements_optimizer_graph_output_dir`
- `defined_elements_optimizer_graph_file_name`

Esto permite que cada instalación redirija el debug a su propia carpeta, como hace `Agua`.

### Paso 12. Delegar creación final del 3D

[creation.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/creation.py) no construye el 3D directamente: itera sobre el estado capturado y delega al callback del script consumidor.

Eso mantiene al módulo genérico y evita acoplarlo a una sola instalación o a una sola familia de objetos.

## Notas de mantenimiento

- El módulo ya está preparado para ser consumido desde varias instalaciones.
- La integración recomendada es siempre a través de [controller_facade.py](c:/ProgramData/Nemetschek/Allplan/2025/Etc/PythonPartsFramework/GeneralScripts/Instalaciones/ElementosDefinidos/controller_facade.py), no llamando controllers sueltos salvo que exista una necesidad muy específica.
- Los puntos comunes de `free_placed_points` dependen de la convención `inicio ... final` para separar caminos lógicos.
- El JSON exportado es un artefacto de depuración y contrato técnico; por eso se eliminaron claves internas no requeridas como `kind` e `IS`.
