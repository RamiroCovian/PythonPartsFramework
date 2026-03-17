# DOCUMENTACIÓN COMPLETA — POLILÍNEA ALLPLAN

Este documento combina la **versión descriptiva original (LIMPIA)** y la **versión técnica extendida** en un único archivo de referencia.

---

## PARTE 1 — DESCRIPCIÓN GENERAL (LIMPIA)


# Documentación Técnica — Script de Creación y Edición de Polilíneas (Allplan PythonParts)

## 1) Resumen 
Este componente implementa un **Script Object** y su **Interactor** para **crear y editar polilíneas** dentro de Allplan con funciones avanzadas: *snap* a ángulos a 45°, inserción de puntos sobre segmentos, selección por marco, fusión/extendido de polilíneas, y limpieza robusta de recursos y segmentos huérfanos. La arquitectura se divide en dos clases principales: `PolylineScriptObject` (ciclo de vida, creación de elementos) y `PolylineInteractor` (lógica de UI/edición). 

---

## 2) Alcance y casos de uso
- **Dibujo guiado** de polilíneas con *snapping* a 0°, 45°, 90°, … y **bloqueo de giros cerrados de 45°** para evitar geometría incómoda. 
- **Inserción de vértices** en segmentos existentes con vista previa y tolerancias configurables. 
- **Selección por marco** de múltiples segmentos y **borrado con fragmentación** segura de polilíneas.  
- **Edición directa** de vértices guardados (+ fusión automática cuando extremos coinciden).  
- **Propagación de metadatos de “sección”** cuando se parte un segmento e **integridad** tras *drag* o inserciones.  

---

## 3) Requisitos & dependencias
El script usa APIs de Allplan (geometría, elementos base/básicos, ajustes, input y utilitarios) e integra un `BaseScriptObject` común:  
`NemAll_Python_Geometry`, `NemAll_Python_BaseElements`, `NemAll_Python_BasisElements`, `NemAll_Python_AllplanSettings`, `NemAll_Python_IFW_Input`, `NemAll_Python_Utility`.   
Hereda de `BaseScriptObject` y usa `OnCancelFunctionResult`. 

> **Compatibilidad de versión:** `check_allplan_version` retorna `True` (sin restricciones explícitas de build). 

**Distribución**: el archivo `.pyp` acompaña al `.py` para ser usado como PythonPart en Allplan (coloque ambos junto a sus módulos base).

---

## 4) Parámetros de configuración (constantes)
- **Tamaños y tolerancias**: `HANDLE_SIZE`, `HIT_TOL_SEGMENT`, `HIT_TOL_VERTEX`, `MAX_PERP_DIST_MM`, `MIN_INSERT_OFFSET_MM`, `MIN_SEG_LEN_MM`. 
- **Colores/estilos**: `SEGMENT_HOVER_COLOR`, `SEGMENT_SEL_COLOR`, `MIDPOINT_*`, `SEGMENT_OVERLAY_*`, `RECT_PEN`, etc. 

Estas constantes controlan **capturas**, **feedback visual** (puntos/segmentos/midpoints) y **tolerancias** de inserción/borrado.

---

## 5) Arquitectura del componente

### 5.1. Script Object — `PolylineScriptObject`
- Mantiene **estado persistente** entre interacciones: `saved_paths` (listas de puntos) y `saved_segments` (segmentos con metadatos: diámetro, sistema, etiqueta). 
- **Entrada**: inicializa e invoca al `PolylineInteractor`. 
- **Ejecución**: construye `ModelElement3D` desde segmentos y/o polilíneas y devuelve `CreateElementResult`.  
- **Finalización inmediata** (crear ya): crea elementos en el documento y **limpia buffers**. 
- **Ciclo de vida**: `start_next_input` purga recursos y colecciones para evitar acumulación. 

**Eventos de control** (mapeo de IDs):  
`1001` (toggle crear), `1002` (guardar), `1003` (finalizar/ESC), `1004` (borrar), `1007` (aplicar sección), `1008` (mostrar info de secciones). 

### 5.2. Interactor — `PolylineInteractor`
- Gestiona **modos**: `create_mode` (dibujo) & `insert_mode` (inserción de vértices). 
- Administra **selecciones**: segmentos activos/guardados, *hover*, *drag* de vértices, *midpoints* clicables, y **selección por marco**. 
- Implementa **limpieza integral** de recursos y estados, y **recolector de “huérfanos”** (`_cleanup_orphaned_segments`).  

---

## 6) Flujo de interacción (UX)

### 6.1. Inicio y *paleta*
- Sincroniza `create_mode` desde el **checkbox** `"CrearPolylinea"` y muestra *prompt* contextual.  
- `insert_mode` lee `"CheckBoxInsertarPunto"`; existe también `"CheckBoxLimitarAngulos"`. 

**Prompt por defecto**: drag de vértices, selección por marco, midpoints clicables, `1004` borrar, `1002` guardar, `ESC/1003` finalizar. 

### 6.2. Dibujo (Crear = ON)
- **Click en punto activo** → inicia *drag*.   
- **Click en midpoint** → inserta punto en el segmento (si permitido).   
- **Click en segmento** → si `insert_mode` ON, proyecta y **propone inserción**; si OFF, **selecciona** el segmento.   
- **Click en vacío** → agrega vértice al final, con validación de ángulos y distancia perpendicular máxima del mouse al *snap*.  

**Fusión automática**: si el último punto cae cerca de un **extremo** de otra polilínea, **fusiona** y limpia la activa. 

### 6.3. Edición (Crear = OFF)
- **Drag de vértice guardado** (con backup de posición original y actualización de segmentos afectados al soltar).   
- **Insertar en midpoint/segmento** con las mismas reglas del modo crear.  
- **Selección por marco**: inicia con click–drag–click, y al finalizar **marca segmentos** dentro del rectángulo (excluye polilíneas con <2 pts).  

### 6.4. Inserción guiada y vista previa
Mientras `insert_mode` está activo y el mouse está sobre un segmento (no sobre midpoint), se **proyecta** el cursor al segmento y, si se cumplen tolerancias, se muestra **punto fantasma** de inserción. 

---

## 7) Reglas geométricas clave

### 7.1. Proyección a segmento
`_segment_project_point(a, b, p)` devuelve `(t, q)` con el punto proyectado **clampado** al tramo `[a,b]`. 

### 7.2. Validación de ángulos (snap a 45°)
- Direcciones permitidas: múltiplos de 45°.  
- Prohíbe “**giro cerrado**” de 45° (complementario 135° respecto del tramo anterior).  
- También evita volver exactamente en sentido contrario (≈180°) durante el *snapping* dinámico en movimiento.  

### 7.3. Distancia perpendicular máxima del click (*feedback* UX)
Si `Limitar ángulos` está ON, el click que agregaría un punto **se ignora** si el mouse real está a más de `MAX_PERP_DIST_MM` de la línea propuesta por el *snap*, con mensaje en paleta. 

### 7.4. Fragmentación segura al borrar por marco
Si no se borran **todos** los segmentos de una polilínea, se **divide** en fragmentos válidos (≥2 puntos) y se reescribe `saved_paths`. 

---

## 8) Persistencia y creación de elementos
- **Ejecución** (`execute`): convierte `saved_segments` en `Line3D` con propiedades, y `saved_paths` en `Polyline3D`, devolviendo `CreateElementResult`.  
- **Creación inmediata en documento** (`_finalize_and_create_now`): compone `ModelElement3D` y llama a `CreateElements`, luego **limpia** buffers.  

> Nota: `_get_properties_for_diameter` está preparado para mapear diámetros a `CommonProperties` específicos. Actualmente devuelve propiedades globales (personalizable). 

---

## 9) Gestión de estado, limpieza y robustez
- **Limpieza integral** al cambiar de input o ante excepciones: borra *preview*, colecciones temporales, índices y *flags*. 
- **Segmentos huérfanos**: se eliminan los registros que ya no correspondan a caminos (`saved_paths`), evitando **fugas** y estados corruptos. 
- **Propagación de secciones** tras *split*: reemplaza el segmento original por dos nuevos clonando metadatos (diámetro, etiqueta, sistema). 

---

## 10) Tabla de comandos / eventos
| ID | Acción | Detalle |
|----|-------|---------|
| 1001 | Toggle **Crear** | Sincroniza checkbox, refresca UI, y aplica cambios de modo.  |
| 1002 | **Guardar** | Añade la polilínea activa a `saved_paths` (log de cantidad).  |
| 1003 | **Finalizar / ESC** | Guarda la activa (si existe), crea elementos y cancela input.  |
| 1004 | **Borrar** | Si hay selección por marco, borra los segmentos; si no, borra selección/hover.  |
| 1007 | **Aplicar sección** | Aplica metadatos de sección a la selección (hook).  |
| 1008 | **Info de secciones** | Muestra resumen (hook).  |

---

## 11) Guía de uso (operativa)

1. **Activar “Crear Polilínea”** en la paleta. El *prompt* indica controles (drag, marco, midpoints, borrar, guardar, finalizar).    
2. **Opcional**: activar **Limitar ángulos** (snap a 45° y bloqueos de giro).   
3. **Dibuje** con clicks; use midpoints para dividir tramos; **inserte** con `insert_mode` ON.    
4. **Guardar** (`1002`) para consolidar en `saved_paths`. Finalice con `ESC/1003` para **crear** en el documento.    
5. **Editar** (Crear=OFF): *drag* de vértices guardados, inserciones, **selección por marco** y **borrado** con fragmentación.   

---

## 12) Buenas prácticas y extensibilidad
- **Propiedades por diámetro**: implementar la tabla de mapeo en `_get_properties_for_diameter` para aplicar estilos por `diameter`/`section_type`. 
- **Validaciones**: ajustar `MAX_PERP_DIST_MM` y tolerancias de *snap* según el flujo de trabajo.  
- **Eventos adicionales**: los hooks `1007/1008` permiten integrar catálogos de secciones o reportes rápidos. 
- **Limpieza**: mantener `start_next_input` y `_cleanup_resources` para sesiones largas (evitar pérdidas de rendimiento).  

---

## 13) Solución de problemas
- **No puedo insertar punto**: verifique que **no** esté sobre un midpoint (entra directo) y que `insert_mode` esté ON; confirme distancia a extremos (> `MIN_INSERT_OFFSET_MM`).  
- **Click ignorado con Limitar ángulos**: probablemente el mouse esté a más de `MAX_PERP_DIST_MM` del *snap* o el ángulo propuesto es inválido (p.ej. giro cerrado de 45°).  
- **Segmentos “desincronizados” tras mover vértices**: el sistema actualiza automáticamente `saved_segments`, pero si aparecen inconsistencias, el **limpiador de huérfanos** las depura.  

---

## 14) Apéndice A — Referencias rápidas (constantes)
- **Tolerancias**: `HIT_TOL_VERTEX`, `HIT_TOL_SEGMENT`, `MIDPOINT_HIT_TOL` → controlan alcance de *hover/click*.  
- **Estilos**: `SEGMENT_HOVER_COLOR`, `SEGMENT_SEL_COLOR`, `MIDPOINT_PEN`, `RECT_PEN`, `SEGMENT_OVERLAY_PEN`. 

---

## 15) Apéndice B — Diagrama de estados (simplificado)

```
[Crear=ON] ----(1001)----> [Crear=OFF]
    |                         |
    | click vacío             | drag vértice guardado
    v                         v
  agrega punto            mueve/merge/fusiona
    |
    +-- midpoint --> inserta punto
    |
    +-- seg + Insert ON --> proyecta->inserta
    |
    +-- seg + Insert OFF --> selecciona seg
```

> La **selección por marco** sólo es válida en **Crear=OFF** y sin otros estados activos (no *drag*, no *extend*, no polilínea activa). 

---

## 16) Historial / Notas
- Esta documentación cubre el archivo base (`polilinea_base_orig.py`) y su `.pyp` asociado. Para mantener consistencia, sincronice cualquier cambio de UI (paleta) con los nombres de propiedades usados por el Interactor.  



---

## 2) Métricas del código

- Líneas totales: **2536**

- Clases: **2**  |  Funciones de nivel superior: **3**  |  Constantes: **25**


## 3) Imports y dependencias

- `BaseScriptObject`
- `CreateElementResult`
- `ScriptObjectInteractors.OnCancelFunctionResult`
- `__future__`
- `collections`
- `collections`
- `typing`
- `NemAll_Python_AllplanSettings`
- `NemAll_Python_BaseElements`
- `NemAll_Python_BasisElements`
- `NemAll_Python_Geometry`
- `NemAll_Python_IFW_Input`
- `NemAll_Python_Utility`
- `inspect`
- `math`
- `math`
- `traceback`


## 4) Constantes y parámetros (top‑level)

- `DRAG_SCALE             = 1.5`
- `HANDLE_SIZE            = 90.0    # mm`
- `HIT_TOL_SEGMENT        = 80.0    # mm (captura de segmentos)`
- `HIT_TOL_VERTEX         = 30.0    # mm (captura de puntos)`
- `HOVER_SCALE            = 1.25`
- `MAX_PERP_DIST_MM       = 20.0    # Ajusta este valor según preferencia`
- `MIN_INSERT_OFFSET_MM   = 2.0     # distancia mínima a extremos para insertar`
- `MIN_SEG_LEN_MM         = 1.0     # evitar segmentos casi nulos`
- `BRANCH_ANCHOR_COLOR    = 7       # 7 = magenta (preview de anclaje para bifurcar)`
- `BOX_SELECTED_SEG_COLOR = 9       # 9 = marrón`
- `HANDLE_COLOR_IDX       = 2       # 2 = amarillo (puntos)`
- `INSERT_PREVIEW_COLOR   = 6       # cian para el punto fantasma`
- `MIDPOINT_COLOR         = 4       # color neutro para marcadores de punto medio`
- `PREVIEW_SAVED_COLOR    = 3       # 3 = verde (polilíneas guardadas en preview únicamente)`
- `RECT_COLOR             = 8`
- `SEGMENT_HOVER_COLOR    = 1       # 1 = rojo (segmento bajo mouse)`
- `SEGMENT_SEL_COLOR      = 5       # 5 = azul (segmento seleccionado)`
- `SELECTED_VERTEX_COLOR  = 5`
- `MIDPOINT_HIT_TOL       = 12.0    # mm`
- `MIDPOINT_PEN           = 13      # trazo gordo para que se vean`
- `MIDPOINT_SIZE_FACTOR   = 0.90    # tamaño relativo al HANDLE_SIZE`
- `MIDPOINT_Z_BIAS        = 1.0     # mm`
- `SEGMENT_OVERLAY_PEN    = 13      # trazo más gordo para que se note`
- `SEGMENT_OVERLAY_Z_BIAS = 1.0     # mm: levanta el tramo resaltado sobre la poly base`
- `RECT_PEN               = 12`


## 5) Clases y métodos

### Clase `PolylineScriptObject` (línea 70) — bases: BaseScriptObject

**Métodos**:

- `__init__(self, build_ele, script_object_data)`  *(línea 71)*

- `start_input(self)`  *(línea 82)*

- `start_next_input(self)`  *(línea 86)*

    > Cleanup resources when transitioning to next input or shutting down


- `execute(self)`  *(línea 108)*

- `_get_properties_for_diameter(self, base_prop, diameter)`  *(línea 137)*

- `_finalize_and_create_now(self)`  *(línea 142)*

- `on_control_event(self, event_id)`  *(línea 179)*

    > 1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar




### Clase `PolylineInteractor` (línea 236) — bases: (sin bases explícitas)

**Métodos**:

- `_clear_editing_state(self)`  *(línea 237)*

    > Centraliza la limpieza de todos los estados temporales de edición, selección, inserción, drag, hover, bifurcación, etc.
    > Llamar siempre que se requiera un reset completo de la UI/estado de edición.


- `delete_selected_segments_by_box(self)`  *(línea 258)*

    > Borra los segmentos seleccionados por marco. Si se seleccionan todos los segmentos de una polilínea,
    > se borra toda la polilínea. Si se seleccionan solo algunos, se eliminan esos segmentos y se dividen
    > las polilíneas en fragmentos válidos (≥2 puntos).


- `__init__(self, script_object)`  *(línea 309)*

- `__del__(self)`  *(línea 355)*

    > Destructor to ensure cleanup when object is garbage collected


- `_cleanup_resources(self)`  *(línea 363)*

    > Comprehensive cleanup of all resources to prevent memory leaks


- `_cleanup_orphaned_segments(self)`  *(línea 411)*

    > Remove segments that reference non-existent polyline paths to prevent accumulation


- `_update_segments_after_vertex_drag(self, path_idx, vertex_idx, original_point)`  *(línea 452)*

    > Actualiza las coordenadas de los segmentos afectados después de mover un vértice.
    > Se llama cuando se termina el drag de un vértice guardado para sincronizar saved_segments.


- `_propagate_section_info_after_split(self, path_idx, original_seg_idx, original_section_info, original_end_point)`  *(línea 496)*

    > Propaga la información de sección del segmento original a los dos nuevos segmentos
    > después de insertar un punto intermedio.


- `_is_original_segment(self, segment_info, original_start, original_end)`  *(línea 568)*

    > Verifica si un segmento es el segmento original que se va a dividir.


- `start_input(self, coord_input)`  *(línea 596)*

- `_print_prompt(self)`  *(línea 618)*

- `toggle_create_mode(self)`  *(línea 626)*

- `sync_create_mode_from_checkbox(self)`  *(línea 631)*

    > Sincroniza el modo de creación con el valor del checkbox en la paleta


- `_update_create_mode_display(self)`  *(línea 663)*

    > Actualiza el texto de feedback en la paleta y el estado visual del botón


- `_apply_create_mode_changes(self)`  *(línea 681)*

    > Aplica los cambios correspondientes al cambiar de modo


- `_get_palette_insert_mode(self)`  *(línea 694)*

    > Obtiene el modo de inserción desde la paleta de manera segura


- `_get_palette_limit_angles(self)`  *(línea 699)*

    > Lee el checkbox 'Limitar ángulos' de la paleta.
    > Nota: actualmente no se utiliza en la lógica; se deja listo para futuras mejoras.


- `_sync_insert_mode_from_palette(self)`  *(línea 705)*

- `_dist_sq(self, a, b)`  *(línea 716)*

- `_segment_len(self, a, b)`  *(línea 720)*

- `_segment_project_point(self, a, b, p)`  *(línea 723)*

- `_midpoint(self, a, b)`  *(línea 735)*

- `_is_valid_angle(self, new_point)`  *(línea 738)*

    > Valida el nuevo segmento según el modo "Limitar ángulos":
    > - El ángulo absoluto del segmento debe ser múltiplo de 45° (0,45,90,...).
    > - Además, se prohíbe que el giro entre el último segmento y el nuevo sea de 45° (ángulo cerrado de 45°).
    > Si el checkbox "Limitar ángulos" está OFF, no se aplica ninguna restricción.


- `_find_hover_index(self, p)`  *(línea 787)*

- `_find_hover_saved_point(self, p, only_extremes)`  *(línea 800)*

- `_find_nearby_extreme(self, p, exclude_path)`  *(línea 814)*

    > Busca extremos de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path


- `_find_nearby_vertex(self, p, exclude_path)`  *(línea 829)*

    > Busca cualquier vértice de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path


- `_find_hover_segment(self, p, preferred_kind)`  *(línea 846)*

- `_find_hover_midpoint(self, p)`  *(línea 879)*

- `_seg_equal(self, a, b)`  *(línea 908)*

- `_clear_selection_if_invalid(self)`  *(línea 913)*

- `_can_start_box_selection(self)`  *(línea 929)*

    > Verifica si se puede iniciar la selección por marcos según el estado actual.
    > Evita conflictos con otros modos activos.


- `_clear_box_selection_state(self)`  *(línea 953)*

    > Limpia completamente el estado de selección por marcos.
    > Útil para evitar estados inconsistentes al cambiar de modo.


- `_point_in_rect_xy(self, p, a, b)`  *(línea 966)*

- `process_mouse_msg(self, mouse_msg, pnt, msg_info)`  *(línea 972)*

- `_get_segment_endpoints(self, seg)`  *(línea 1370)*

- `_can_insert_here(self, a, b, t)`  *(línea 1383)*

- `_insert_on_segment(self, seg, q, keep_selection_left)`  *(línea 1390)*

- `delete_selected_or_hovered_segment(self)`  *(línea 1435)*

- `on_cancel_function(self)`  *(línea 1492)*

    > ESC: guardar si corresponde y CREAR INMEDIATO para no depender de execute().


- `save_current_polyline(self)`  *(línea 1513)*

- `_create_default_segments_for_new_path(self, path_idx)`  *(línea 1642)*

    > Crea segmentos con sección por defecto para una nueva polilínea


- `_create_default_segments_for_extension(self, path_idx, start_seg, end_seg)`  *(línea 1664)*

    > Crea segmentos con sección por defecto para una extensión


- `_merge_polylines(self, path1, end1, path2, end2)`  *(línea 1689)*

    > Fusiona dos polilíneas conectándolas por sus extremos, trasladando la segunda (nueva) para que coincida con la primera (existente)


- `_get_default_diameter(self)`  *(línea 1797)*

    > Obtiene el diámetro por defecto usando la opción actualmente seleccionada en la paleta de gestión de secciones


- `_clear_preview(self)`  *(línea 1807)*

    > Clear all preview elements completely


- `on_preview_draw(self)`  *(línea 1827)*

- `on_mouse_leave(self)`  *(línea 1832)*

- `_line_with_zbias(self, a, b, z_bias)`  *(línea 1835)*

- `_draw_preview(self, hover)`  *(línea 1841)*

- `apply_section_to_selected(self)`  *(línea 2100)*

    > Aplica la sección seleccionada en la paleta a los segmentos seleccionados


- `_get_diameter_to_apply(self)`  *(línea 2141)*

    > Obtiene el diámetro a aplicar desde la paleta


- `_apply_diameter_to_segment(self, path_idx, seg_idx, diameter)`  *(línea 2191)*

    > Aplica un diámetro específico a un segmento guardado


- `show_sections_info(self)`  *(línea 2249)*

    > Muestra información de las secciones configuradas


- `_get_segment_section_info(self, kind, path_idx, seg_idx)`  *(línea 2314)*

    > Obtiene información de sección para un segmento específico


- `_points_equal(self, p1, p2, tolerance)`  *(línea 2341)*

    > Compara dos puntos con tolerancia


- `_get_section_properties(self, diameter)`  *(línea 2347)*

    > Obtiene las propiedades visuales según el diámetro del segmento


- `_get_section_color_for_preview(self, diameter, system)`  *(línea 2353)*

    > Obtiene el color específico para preview según diámetro y sistema.
    > - Pluvial 110mm: color 7
    > - Fecal 110mm: color 4
    > - Fecal 40mm: color 66
    > - Fecal 25mm: color 70


- `_safe_get_palette_property(self, property_name, default_value)`  *(línea 2382)*

    > Obtiene una propiedad de la paleta de manera segura


- `_safe_set_palette_property(self, property_name, value)`  *(línea 2401)*

    > Establece una propiedad de la paleta de manera segura


- `_clone_properties(self, src_prop)`  *(línea 2421)*

- `_get_current_system(self)`  *(línea 2431)*

    > Devuelve el sistema actual en texto ('Pluvial'|'Fecal') según la paleta.


- `_format_segment_label(self, diameter, system)`  *(línea 2444)*

    > Formatea la etiqueta de segmento: D110 P (pluvial) o D25 F, D40 F, D110 F (fecal).


- `_create_cross_marker(self, point, properties, size, z_bias)`  *(línea 2459)*

    > Dibuja una cruz (cruzeta) en torno al punto, en ejes X/Y y una pequeña marca Z.


- `_create_point_marker(self, point, properties, size, z_bias)`  *(línea 2479)*

- `_add_text_label(self, elems_list, point_a, point_b, text)`  *(línea 2501)*

    > Añade un TextElement 2D en el centro del segmento, rotado según la dirección del segmento.




## 6) Funciones de nivel superior

- `check_allplan_version(_build_ele, _version)`  *(línea 61)*

- `create_script_object(build_ele, script_object_data)`  *(línea 65)*

- `MAX_EPS(x)`  *(línea 2522)*

## 7) Mapa de eventos / comandos

- **1001** — ejemplo de aparición: `"""1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar"""`

- **1002** — ejemplo de aparición: `"""1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar"""`

- **1003** — ejemplo de aparición: `"""1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar"""`

- **1004** — ejemplo de aparición: `"""1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar"""`

- **1007** — ejemplo de aparición: `1007: intr.apply_section_to_selected,`

- **1008** — ejemplo de aparición: `1008: intr.show_sections_info`

## 8) Propiedades de paleta y flags detectados

- `CheckBoxInsertarPunto`
- `CheckBoxLimitarAngulos`
- `CheckBoxValue`
- `CrearPolylinea`


## 10) Algoritmos y reglas destacadas (visión general)
- **Construcción de polilíneas** con estados de creación/edición y validaciones de ángulo/distancia.
- **Inserción de vértices** por proyección a segmento y midpoints.
- **Selección por marco** y **borrado con fragmentación** para conservar listas válidas de puntos.
- **Sincronización de segmentos** derivados de `saved_paths` para mantener metadatos coherentes (diámetro/sección/sistema) tras divisiones o *drag*.
- **Limpieza de recursos** al finalizar/abortar y reindexación de estructuras internas.


## 11) Plan de pruebas recomendado
1. **Dibujo básico**: secuencia de 5–6 puntos, validando snap y tolerancias.
2. **Inserción en segmento**: habilitar modo inserción y comprobar proyección y offset mínimo.
3. **Selección por marco**: seleccionar subconjunto y borrar; verificar fragmentación segura.
4. **Fusión de caminos**: arrastrar extremos para coincidir y corroborar unión + limpieza de huérfanos.
5. **Finalizar y crear**: confirmar que los `ModelElement3D` resultantes respetan las propiedades asignadas.


## 12) Rendimiento y memoria
- Evitar mantener *previews* y colecciones grandes entre iteraciones; ejecutar rutinas de limpieza en cambios de estado.
- Ajustar tolerancias para reducir cálculos de proyección/selección en escenas densas.
- Considerar *batching* al crear elementos definitivos si el documento es grande.


## 13) Puntos de extensión sugeridos
- **Propiedades por diámetro/sección**: implementar mapeo en el helper correspondiente para capas, colores, estilos y atributos BIM.
- **Snap avanzado**: permitir granularidad configurable (p. ej., 15° además de 45°).
- **Persistencia externa**: exportar/ importar `saved_paths` en JSON para intercambiar trazados.
- **Herramientas de medición**: longitud total por camino y reportes de metadatos por selección.


## 14) FAQ breve
**¿Por qué no se inserta un punto al click?** Verifique que el cursor no esté sobre un midpoint (ese caso inserta directamente) y que la distancia al tramo cumpla las tolerancias.

**¿Por qué se ignora el click con ángulos limitados?** Si el *snap* propuesto es inválido (p. ej., giro cerrado) o el mouse está fuera de la distancia perpendicular máxima, el click se descarta.
