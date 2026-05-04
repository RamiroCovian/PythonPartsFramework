# Bifurcación y unión de segmentos y paths (Saneamiento)

Documentación de la implementación relacionada con **unión de segmentos entre sí**, **unión de paths entre sí** y **bifurcaciones** (vértices compartidos entre varios paths) en el script de Saneamiento (Allplan 2025).

---

## 1. Modelo de datos

### 1.1 Estructuras principales

- **`saved_paths`** (lista de listas de `Point3D`): cada elemento es una polilínea guardada; cada polilínea es una secuencia de vértices. Varios paths pueden compartir el mismo vértice (misma coordenada) en bifurcaciones.
- **`saved_segments`** (lista de diccionarios): cada entrada describe un segmento (tramo entre dos vértices consecutivos de un path) con `points`, `diameter`, `section_type`, `label`, `installation_type_horizontal`, `installation_type_vertical`, `face`, etc. Los `points` de cada segmento son referencias a los mismos `Point3D` que aparecen en `saved_paths` (o copias con la misma posición).

Un **path** es una polilínea lógica (una sola línea continua). Un **segmento** es un tramo entre dos vértices consecutivos de un path, con atributos de sección e instalación. Varios paths pueden **confluir en un mismo vértice** (bifurcación); ese vértice existe en cada path por separado pero con la misma posición.

---

## 2. Unión de segmentos/polilíneas al crear

### 2.1 Snap al colocar el primer punto

Al estar en **modo Crear polilínea** (`create_mode=True`), al colocar el **primer punto** se hace **snap a extremos** de paths ya guardados:

- Se recorren todos los `saved_paths` y se buscan vértices que estén a distancia ≤ `HIT_TOL_VERTEX` del punto del ratón.
- Se priorizan los **extremos** (primer o último vértice de cada path) para uniones fiables.
- Si el primer punto hace snap a un extremo de un path guardado, se guarda **`extend_target`**:
  - `(path_idx, "start")` si se hizo snap al **inicio** del path.
  - `(path_idx, "end")` si se hizo snap al **final** del path.

Así, la polilínea que se está dibujando queda “enganchada” a un path existente y al guardar se fusiona con él en lugar de crear un path nuevo.

**Código de referencia:** búsqueda de `snap_path_idx` / `snap_vertex_idx` y asignación de `extend_target` en el flujo de colocación del primer punto (aprox. líneas 13894–13946).

### 2.2 Fusión al guardar (`save_current_polyline`)

Al llamar a **`save_current_polyline()`**:

#### A) Extensión explícita (`extend_target` definido)

Si `extend_target` está definido y hay al menos 2 puntos en la polilínea activa:

- **Extensión por el final** (`side == "end"`):  
  Se añaden los puntos nuevos (desde el segundo de la activa, el primero es el ancla) al final del path `pidx`.  
  Se crean segmentos por defecto para la extensión con **`_create_default_segments_for_extension(pidx, start_seg, len(base))`**, incluyendo el **segmento conector** (último vértice antiguo → primer vértice nuevo), usando `start_seg = len(base) - len(new_points) - 1`.

- **Extensión por el inicio** (`side == "start"`):  
  Se hace *prepend* de los puntos nuevos (en orden invertido) al path `pidx` y se reemplaza el path.  
  Se crean segmentos por defecto para el tramo prependido con **`_create_default_segments_for_extension(pidx, 0, len(prepend))`**.

Después se limpia `extend_target`.

#### B) Fusión por coincidencia de extremos (sin `extend_target`)

Si no hay `extend_target` pero la nueva polilínea tiene ≥2 puntos, se comprueba si **une con un extremo** de algún path existente (comparación con tolerancia `_pt_eq`, p. ej. 1e-3):

1. **Nuevo empieza donde termina existente** → se añade la nueva (sin duplicar el primer punto) al final del path existente.
2. **Nuevo termina donde empieza existente** → se añade la nueva (sin duplicar el último punto) al inicio del path existente.
3. **Nuevo empieza donde empieza existente** → se invierte la nueva y se hace *prepend* al existente.
4. **Nuevo termina donde termina existente** → se invierte la nueva y se hace *append* al existente.

En todos estos casos se llama a **`_create_default_segments_for_extension`** para el rango de segmentos nuevos. Si no hay coincidencia, la nueva polilínea se guarda como path nuevo con **`_create_default_segments_for_new_path`**.

**Código de referencia:** `save_current_polyline` (aprox. líneas 14362–14476).

---

## 3. Segmentos por defecto en extensiones

### 3.1 `_create_default_segments_for_extension(path_idx, start_seg, end_seg)`

Crea entradas en **`saved_segments`** para los tramos del path `path_idx` entre los índices de segmento `start_seg` y `end_seg` (sin duplicar segmentos ya existentes).

- **Herencia de instalación y etiqueta:**  
  Se intenta tomar un “template” del segmento adyacente del mismo path:
  - Si `start_seg > 0`, se usa el segmento `start_seg - 1`.
  - Si no, y si `end_seg < len(pts) - 1`, se usa el segmento `end_seg`.  
  Del template se heredan `installation_type_horizontal`, `installation_type_vertical`, `face`, `diameter` y `system`. Si no hay template, se usan los valores de la paleta.

- **Segmento conector:**  
  En la extensión por el final, el rango pasado incluye el segmento que une el último vértice antiguo con el primer vértice nuevo (`start_seg = len(base) - len(new_points) - 1`), de modo que ese tramo también tiene instalación/etiqueta coherente.

Cada nuevo segmento se añade con `points = [pts[seg_idx], pts[seg_idx + 1]]`, diámetro por defecto, `section_type`, `label` formateado y los valores de instalación anteriores.

**Código de referencia:** aprox. líneas 14546–14593.

---

## 4. Bifurcaciones: vértice compartido entre varios paths

En una **bifurcación**, varios paths comparten el mismo punto físico (misma coordenada). Cada path tiene su propio vértice en esa posición; la coincidencia es por coordenadas.

### 4.1 Mover un vértice compartido: `_sync_vertex_to_all_paths`

Al **mover un vértice** (drag en modo edición), ese vértice puede ser compartido por varios paths. Para que la bifurcación se mantenga coherente:

- **`_sync_vertex_to_all_paths(original_point, new_point, exclude=(pidx, vidx))`**  
  Recorre todos los vértices de todos los `saved_paths` y, donde `_points_equal(pt, original_point)` (salvo el vértice excluido `(pidx, vidx)`), sustituye ese vértice por `new_point`. Así, todos los paths que pasaban por `original_point` pasan a pasar por `new_point`.

Se llama:

- En **mouse down** al iniciar el drag del vértice guardado (primer frame).
- En **mouse move** mientras se arrastra (actualizando desde `saved_dragging_last_point` al punto actual).
- En **mouse up** al confirmar la nueva posición (y opcionalmente al revertir si se cancela en modo edición de layers).

**Código de referencia:** aprox. líneas 12378–12409.

### 4.2 Actualizar segmentos tras mover vértice: `_update_segments_after_vertex_drag`

Los **`saved_segments`** guardan `points[0]` y `points[1]` por segmento. Al mover un vértice, esos `Point3D` en los segmentos deben reflejar la nueva posición:

- **`_update_segments_after_vertex_drag(path_idx, vertex_idx, from_point, to_point=None)`**  
  Para cada segmento en `saved_segments`, si `points[0]` o `points[1]` coincide con `from_point` (por `_points_equal`), lo sustituye por `to_point` si se pasa, o por la posición actual del vértice en `saved_paths[path_idx][vertex_idx]` si `to_point is None`.

Así el preview y la geometría de segmentos siguen al vértice tanto **durante el drag** (`to_point` = posición actual del ratón) como **al soltar** (`to_point=None`, usa la posición final del path).

**Código de referencia:** aprox. líneas 12412–12469.

---

## 5. Unión automática de paths al “Finalizar y crear”

En **`_finalize_and_create_now()`**, antes de materializar la red en el documento, se hace una **unión automática** de paths que se tocan por extremos:

- Se comparan paths con tolerancia **`_pts_equal_join`** (p. ej. 1e-3).
- Se repite mientras haya cambios (máx. 100 iteraciones):
  - **Caso 1:** final del path A = inicio del path B → se une A con B (B sin primer punto).
  - **Caso 2:** final del path B = inicio del path A → se une B con A (A sin primer punto).
  - **Caso 3:** inicio de A = inicio de B → se invierte B y se une por el inicio de A.
  - **Caso 4:** final de A = final de B → se invierte B y se une al final de A.

Tras cada iteración, `saved_paths` se sustituye por la lista de paths ya unidos; los índices usados se marcan para no procesarlos dos veces.

Después de unir paths, se **reconstruye `saved_segments`**: para cada tramo de cada path unido se busca un segmento existente con los mismos extremos (por `_pts_equal_join`); si existe se reutiliza; si no, se crea un segmento por defecto con valores de la paleta. Así la lista de segmentos queda alineada con la lista de paths unidos.

**Código de referencia:** aprox. líneas 3723–3912.

---

## 6. Modo edición de layers: no arrastrar vértices

En **modo edición de layers** (`preview_mode=True`) no debe estar activo el arrastre de vértices de paths guardados, para no mezclar “edición de geometría” con “edición de layers”.

- **OnMouseDown:** La lógica “click en vértice guardado → iniciar drag” solo se ejecuta si **`not self.preview_mode`**. En `preview_mode` se fuerza `saved_hover_point = None`.
- **OnMouseMove:**  
  - El bloque que actualiza la posición del vértice al arrastrar solo se ejecuta si **`(not self.create_mode) and (not self.preview_mode) and self.saved_dragging is not None`**.  
  - El cálculo de **`saved_hover_point`** (hover sobre vértices guardados) solo se hace si **`not self.preview_mode`** (junto con `not self.create_mode` y sin hover en midpoint/segmento).
- **OnMouseUp:** Si `saved_dragging is not None` y **`self.preview_mode`**, se **cancela** el drag: se restaura el vértice a `saved_dragging_original_point`, se llama a `_sync_vertex_to_all_paths(current_pt, original_point, ...)` para revertir en todos los paths que compartan ese vértice, y se limpian `saved_dragging` y puntos asociados.

Con esto, en modo edición de layers no se inicia ni se procesa el arrastre de vértices; el movimiento de vértices queda solo para el modo edición de geometría (Crear=OFF y sin preview).

---

## 7. Resumen de flujos

| Acción | Comportamiento |
|--------|----------------|
| Crear polilínea y colocar primer punto cerca de un extremo de path guardado | Snap a ese extremo y se guarda `extend_target` → al guardar se fusiona en ese path. |
| Guardar polilínea que toca por extremo un path existente (sin haber usado extend_target) | Se detecta coincidencia por tolerancia y se fusiona en el path existente; se crean segmentos por defecto con `_create_default_segments_for_extension`. |
| Extensión por inicio/fin con `extend_target` | Se modifica el path en su inicio o final y se crean segmentos con herencia de instalación/etiqueta (incl. segmento conector). |
| Mover vértice en edición (y que sea compartido en bifurcación) | `_sync_vertex_to_all_paths` actualiza ese vértice en todos los paths que lo comparten; `_update_segments_after_vertex_drag` actualiza `points` en `saved_segments`. |
| Finalizar y crear | Se unen automáticamente paths consecutivos que se tocan por extremos; luego se actualiza `saved_segments` para reflejar los paths unidos. |
| Modo edición de layers activo | No se inicia ni se procesa el drag de vértices guardados; al soltar un drag residual se revierte. |

---

*Documento generado a partir de la implementación en `Saneamiento.py` (Allplan 2025, PythonPartsExampleScripts/saneamiento).*
