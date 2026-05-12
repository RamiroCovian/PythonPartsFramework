# Registro de implementación (Saneamiento PolyLib)

Bitácora de cambios en la instalación **Saneamiento** (librería bajo `Instalaciones`): correcciones, nuevas funciones y decisiones técnicas. **Orden cronológico inverso** (lo más reciente arriba).

---

## Convención — qué registrar aquí

**A partir de ahora**, cada arreglo, implementación o cambio relevante que hagamos en este módulo debe quedar reflejado en este archivo en la misma sesión de trabajo (o en el cierre de la tarea).

En cada entrada conviene incluir:

- **Fecha** (día del cambio).
- **Título corto** (una línea).
- **Qué se hizo** (objetivo o resumen).
- **Síntoma / causa** (si aplica).
- **Solución** (breve; detalle en código).
- **Archivos** (rutas relativas a `Saneamiento/` o `Instalaciones/` según convenga).

Las entradas pueden ser más cortas que el ejemplo largo de la sincronización de diámetro; lo importante es que quede **rastro auditable** para revisiones futuras y soporte.

---

## 2026-04-07 — Codos Ø25 (45°/90°): split, registro, pipeline y ajuste geométrico

### Qué se hizo

- Se separó la lógica de codos en scripts dedicados:
  - `Colze_basic_25m_f_45_script.py` (solo codo 45°).
  - `Colze_basic_25m_f_90_script.py` (solo codo 90°).
- Ambos scripts se migraron al formato estándar de PythonPart usado en Saneamiento (`BaseScriptObject` + `CreateElementResult` + clase `...Script`).
- Se registraron codos en `polyline_reg_saneamiento.py`:
  - alta explícita de `codo_45` y `codo_90` en `elements3D`,
  - inclusión de `codo_45` en `installation_types["Fecal"]["elems"]`.
- Se corrigió error de ejecución al finalizar (`'codo_90'`) por clave no registrada en catálogo.
- Se integró inserción automática de codos en `saneamiento_polyline.py` + `utils/geo_handler.py`:
  - carga de templates `codo_45` / `codo_90` para Fecal Ø25,
  - inserción en vértices de giro dentro de `PipelineProcessor`.
- Se corrigió la clasificación de giros para no confundir 45° con 90°:
  - decisión principal por ángulo real en planta (XY),
  - detector de 90° por eje dominante queda como fallback en casos no-XY.

### Geometría `codo_45` (iteraciones y estado)

- Se reemplazó la geometría inicial por una nueva basada en las medidas del croquis de usuario.
- Se ajustó el método de sólido para compatibilidad de librería siguiendo patrón de `Clima`:
  - `CreatePolyhedron(polygon, path)` + `CreateBRep3D(...)`.
- Se incluyó hot-reload de módulos `Colze_basic_25m_f_45_script` y `Colze_basic_25m_f_90_script` en `saneamiento_polyline.py` para evitar lecturas de versión en caché durante pruebas.
- Se aplicaron ajustes de orientación del `codo_45` solicitados por usuario:
  - inversión por mirror (temporal),
  - posterior reemplazo por intercambio directo de valores verticales en `PARAMS` (sin mirror), como criterio final pedido.
- Ajuste posterior de mantenimiento:
  - refactor ligero del script `Colze_basic_25m_f_45_script.py` para reducir repetición en atributos y simplificar lectura de atributo padre,
  - se restauran en `PARAMS` las claves `pmp_diametre` y `pmp_seccio` por requerimiento funcional.
- Ajuste posterior funcional de copias `codo_45`:
  - el script genera ahora 3 elementos superpuestos (original + 2 copias),
  - ambas copias con color `5` y atributo `6_CC_IS = IS`,
  - una de las copias además con `Material = CAVITAT`.
- Ajuste posterior de pipeline para visualizar copias de `codo_45`:
  - en `saneamiento_polyline.py` se registran también los elementos extra devueltos por `codo_45` (`codo_45_inner`, `codo_45_inner_2`),
  - en `utils/geo_handler.py` se insertan estos templates extra en el mismo nodo/transformación del codo principal.

### Archivos

`pyp-scripts/Colze_basic_25m_f_45_script.py`, `pyp-scripts/Colze_basic_25m_f_90_script.py`, `polyline_reg_saneamiento.py`, `pyp-scripts/saneamiento_polyline.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Fecal Ø40: traslación manual XYZ de flecha

### Qué se hizo

- Se añadió ajuste manual por matriz de traslación para reposicionar la flecha en el script de Ø40.
- Nuevas constantes globales en `tub_pvc_tricapa_f_40_script.py`:
  - `FLECHA_MANUAL_TRASL_X`
  - `FLECHA_MANUAL_TRASL_Y`
  - `FLECHA_MANUAL_TRASL_Z`
- La traslación se aplica a `flecha_brep` después de la rotación de 180° en X.
- Ajuste adicional en pipeline: `_aplicar_transformacion(..., preserve_local_offset=True)` para la flecha, evitando que la normalización al centro anule el offset manual.
- Ajuste posterior: recentrado explícito de la flecha en origen local antes de aplicar `FLECHA_MANUAL_TRASL_X/Y/Z`, para evitar offsets extremos (p. ej. `-600`) y que el ajuste sea fino alrededor de 0.
- Ajuste posterior: anclaje relativo al tramo con `FLECHA_POS_REL_TRAMO` (0..1). Así la posición de la flecha se mantiene proporcional al tubo cuando cambia el largo; `FLECHA_MANUAL_TRASL_X/Y/Z` queda como microajuste.
- Ajuste posterior (simplificación solicitada): se eliminan `FLECHA_POS_REL_TRAMO` y `FLECHA_MANUAL_TRASL_X/Y/Z`; la posición longitudinal vuelve a controlarse únicamente por `FLECHA_DIST_ANILLO`.

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_40_script.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Hot-reload de módulos de Saneamiento para reducir efecto caché

### Síntoma

Durante ajustes finos (por ejemplo posición de flecha), los cambios en `.py` no se reflejaban de inmediato hasta reiniciar Allplan.

### Solución

Se añadió `_reload_saneamiento_runtime_modules()` en `saneamiento_polyline.py`, ejecutado al inicio de `_create_elements_for_segment_group`, para recargar módulos clave (`polyline_reg_saneamiento`, scripts tricapa y `geo_handler`) antes de crear elementos.

### Ajuste posterior

El primer enfoque usaba `importlib.import_module(...)` con rutas que contienen `pyp-scripts` (guion), lo que generaba error de import en runtime. Se cambió el hot-reload para recargar desde `sys.modules` (módulos ya cargados por Allplan) filtrando por sufijos objetivo.

### Archivos

`pyp-scripts/saneamiento_polyline.py`

---

## 2026-04-07 — `tub_pvc_tricapa_f_40_script`: limpieza total de Ø110

### Qué se hizo

- El script `tub_pvc_tricapa_f_40_script.py` quedó dedicado solo a **Fecal Ø40**.
- Se eliminó toda la lógica residual de **Ø110**:
  - tipos 0/1 en selección de opciones,
  - atributos TS-110 / diámetro 110,
  - helper `_add_user_attributes_110mm`.
- Se dejó únicamente el flujo 40 mm (1ML/3ML) con atributos y copias correspondientes.

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_40_script.py`

---

## 2026-04-07 — Pluvial Ø110: flecha propia en `tub_pvc_tricapa_p_110_script`

### Qué se hizo

- `tub_pvc_tricapa_p_110_script.py` pasa de delegar ciegamente la flecha a `tub_pvc_tricapa_v` a crear una flecha propia.
- La nueva flecha de Ø110 se modela como **BRep** (no `Polygon3D`) con lógica equivalente de posicionamiento por `FLECHA_DIST_ANILLO`.
- Se mantiene la geometría/atributos del tubo base (builder existente) y se añade flecha propia con color 27 y layer 40148.
- En `saneamiento_polyline.py`, el rebuild por tramo para `tub_pvc_tricapa_p_110` devuelve lista completa para que el pipeline inserte también la flecha.
- Ajuste posterior de posicionamiento: recentrado de flecha en origen local y recolocación longitudinal con `x_pos = base_x - (largo_tubo * 0.5)` para evitar que aparezca demasiado lejos del tubo.

### Archivos

`pyp-scripts/tub_pvc_tricapa_p_110_script.py`, `pyp-scripts/saneamiento_polyline.py`

---

## 2026-04-07 — Fecal Ø110: flecha propia en `tub_pvc_tricapa_f_110_script`

### Qué se hizo

- `tub_pvc_tricapa_f_110_script.py` ahora incorpora flecha propia BRep (no `Polygon3D`) con lógica completa equivalente a 110 pluvial:
  - construcción de perfil de flecha,
  - extrusión a BRep,
  - rotación 180° en X,
  - recentrado local,
  - reposición en X con `x_pos = base_x - (largo_tubo * 0.5)`,
  - control longitudinal por `FLECHA_DIST_ANILLO`.
- Se mantiene recoloreado del tubo fecal a color 4.
- En `saneamiento_polyline.py`, el rebuild por tramo de `tub_pvc_tricapa_f_110` devuelve lista completa para insertar también la flecha en polilínea.

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_110_script.py`, `pyp-scripts/saneamiento_polyline.py`

---

## 2026-04-07 — Ø25 básico: copias visibles en polilínea (superpuestas al original)

### Síntoma

En `tub_pvc_basic_f_25_script.py` el PythonPart crea 3 elementos (original + 2 copias), pero en polilínea solo aparecía el original.

### Causa

El hook de saneamiento tomaba `conduct_model[0]` como template principal y no inyectaba `conduct_model[1:]` en el pipeline por tramo.

### Solución

- Se añadió soporte de `saneamiento_extra_templates` en `PipelineProcessor`.
- Para cada tramo, esos templates extra se escalan, transforman y alinean igual que el original.
- En `saneamiento_polyline.py`, cuando `element_key == "tub_pvc_basic_f_25"`, se pasa `conduct_model[1:]` como extras.

### Archivos

`pyp-scripts/utils/geo_handler.py`, `pyp-scripts/saneamiento_polyline.py`

---

## 2026-04-07 — Debug temporal para Ø25 básico (original + copias)

### Qué se hizo

- Se añadieron `print` de depuración en:
  - `tub_pvc_basic_f_25_script.py`: creación de original/copia_1/copia_2 con dimensiones, color y layer.
  - `utils/geo_handler.py`: inserción de templates extra por tramo (conteo y propiedades de cada copia añadida).

### Objetivo

Confirmar si los 3 elementos se generan/insertan correctamente y si el problema observado es de visibilidad por solape total.

### Archivos

`pyp-scripts/tub_pvc_basic_f_25_script.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Ø25 copias: extra de 15 mm en un solo lado (no 7.5/7.5)

### Síntoma

Las copias Ø25 (40 mm de ancho) quedaban centradas respecto al original (25 mm), dejando 0.00750 m a cada lado.

### Solución

- En `tub_pvc_basic_f_25_script.py` se añadió desplazamiento lateral para copias:
  - (Ajuste reemplazado) se descartó el offset local por su dependencia de ejes/rotaciones.
- Implementación final: offset global en Z desde pipeline para copias extras de Ø25:
  - `saneamiento_extra_world_offset_z_mm = -7.5` en `saneamiento_polyline.py`.
  - aplicación del `Move(..., Vector3D(0,0,offset))` tras alineación en `geo_handler.py`.
- Ajuste posterior: al recrear `ModelElement3D` tras el `Move`, se preservan explícitamente los atributos del elemento extra (`GetAttributes` → `SetAttributes`) para no perder `6_CC_IS` / `Material=CAVITAT`.
- Ajuste posterior (solicitud funcional): para Ø25 se elimina el offset aplicado en pipeline y las copias se dejan nacer/transformar desde el mismo origen que el original. El desborde geométrico 25x40 sobre 25x25 se usa tal cual.
- Ajuste posterior: en copias extra del pipeline se activa `preserve_local_offset=True` para que no se recentren automáticamente y se respete su ubicación local tal cual.
- Ajuste posterior: para resolver desfase entre original/copias, se fuerza coincidencia de centro 3D entre cada copia y el original ya transformado del tramo (match de centros + `Move`), preservando properties/attributes.
- Ajuste posterior (solicitud): se elimina ese match de centros en `geo_handler` y el centrado de copias se define directamente en el script `tub_pvc_basic_f_25_script.py` con `COPY_CENTER_OFFSET_Z = -7.5` al crear cada copia.
- Ajuste posterior (alineación con `Saneamiento_old/Tubpvcbasic_002.py`): se eliminan offsets manuales de copias y se vuelve al comportamiento original (copias creadas en mismo origen de script y transformadas con la misma ruta estándar del pipeline, sin `preserve_local_offset`).

### Resultado esperado

Diferencia total de 15 mm concentrada en un solo lado (0.01500 m), con 0.00000 m en el otro lado.

### Archivos

`pyp-scripts/tub_pvc_basic_f_25_script.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Ø25 copias: `6_CC_IS` relleno con `IS`

### Qué se hizo

- En `_add_copy_attributes()` de `tub_pvc_basic_f_25_script.py`, el valor de `6_CC_IS` para copias (`idx 1` y `idx 2`) pasa de `""` a `"IS"`.
- Ajuste posterior:
  - `Material=CAVITAT` se mueve a `idx == 2` (segunda copia), según criterio funcional solicitado.
  - Se agregan `print` de debug con IDs/valores realmente escritos para `6_CC_IS` y `Material`.
  - Se incluye `tub_pvc_basic_f_25_script` en el hot-reload de `saneamiento_polyline.py` para evitar que cambios de atributos queden sin cargar por caché.

### Objetivo

Que ambas copias muestren `6_CC_IS = IS` en atributos, como requiere el flujo de saneamiento.

### Archivos

`pyp-scripts/tub_pvc_basic_f_25_script.py`

---

## 2026-04-07 — Fix cambio Pluvial 110 -> Fecal 110 con mismo diámetro

### Síntoma

Al usar "modificar diámetro" en un tramo Ø110 y cambiar instalación (Pluvial/Fecal) manteniendo 110 mm, el segmento seguía con sistema anterior (ej. Pluvial).

### Causa

En `PolyLib/interactor.py`, `change_diameter_selected_seg()` y `change_diameter_selected_segments_by_box()` actualizaban diámetro/label pero no refrescaban `seg_info.system`.

### Solución

Se actualiza también metadata del segmento en ambos flujos:
- `seg_info.system = selected_inst_type` (si existe),
- `distribution_type` y `water_type` desde estado actual de la paleta,
- recalculado de `label` con el sistema actualizado.

### Ajuste posterior

Se detectó que la creación de geometría seguía usando un único `element_key` global por ruta.  
Se corrigió rebuild por tramo para resolver PythonPart **por segmento** (usando `seg_info.system` + `seg_info.diameter`), permitiendo mezcla real Pluvial/Fecal con mismo diámetro 110 en la misma polilínea.

### Ajuste posterior 2

En rutas mixtas por diámetro/sistema, se añadió manejo dinámico de extras del rebuild por segmento:
- extras tipo flecha se insertan como flecha,
- extras BRep no flecha se insertan como copias dinámicas del tramo (p.ej. Ø25 básico),
evitando que todos los tramos hereden la geometría del último `element_key` global.

### Ajuste posterior 3 (Ø25 original corto)

Se detectó que, en rebuild por segmento, `tub_pvc_basic_f_25` devolvía el original en L=70 (el script no usa `LargoTramoMm`), mientras las copias sí se escalaban en pipeline.  
Se añade escalado explícito del `model_cond` cuando `seg_info.diameter == 25`, para que el original siga la longitud de la polilínea igual que las copias.

### Archivos

`Instalaciones/PolyLib/interactor.py`, `pyp-scripts/saneamiento_polyline.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Fix converter error en Finalizar/ESC para Pluvial/Fecal Ø110

### Síntoma

Al finalizar (`on_cancel_function`) en tramos Ø110 aparecía:
`No to_python (by-value) converter found for ... std::vector<std::vector<Point3D>>`.

### Causa

El rebuild por tramo devolvía la lista completa de elementos para todas las claves tricapa; en Ø110 eso incluye flecha basada en `Polygon3D`, que entraba en el flujo de transformación/inserción de extras y detonaba el converter en cancel.

### Solución

En `saneamiento_polyline.py`, callback `_rebuild_tubo_saneamiento`:
- `tub_pvc_tricapa_f_40` devuelve lista completa (necesaria para su flecha sólida).
- `tub_pvc_tricapa_p_110` y `tub_pvc_tricapa_f_110` devuelven solo `elems[0]` (tubo), evitando pasar extras de 110 por ese flujo.

### Archivos

`pyp-scripts/saneamiento_polyline.py`

---

## 2026-04-07 — Fecal Ø40: flecha visible y corrección de error en cancel

### Síntoma

- No aparecía la flecha en Fecal Ø40 en la polilínea.
- Al cancelar (`ESC`) aparecía error de conversión C++→Python:
  `No to_python (by-value) converter found for ... std::vector<std::vector<Point3D>>`.

### Causa

- En `tub_pvc_tricapa_f_40_script.py` no se estaba generando flecha (a diferencia del script histórico).
- La primera implementación de flecha como `Polygon3D` provocó incompatibilidad en el flujo de cancel.

### Solución

- Se añadió flecha para Ø40 y se cambió a **sólido BRep** (extrusión), evitando el error de converter.
- En el pipeline (`geo_handler.py`) se ajustó la detección de la flecha para aceptar el extra devuelto por rebuild también como BRep (además del caso `Polygon3D`).
- Se mantiene color flecha 27 y layer `IS_CON_SANE_FAB` (40148).

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_40_script.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-04-07 — Fecal Ø40: restaurada hendidura del anillo

### Síntoma

El tubo fecal Ø40 se generaba con anillo macizo (sin hendidura interna).

### Solución

En `tub_pvc_tricapa_f_40_script.py` se rehizo `_build_tube` con el mismo enfoque de tricapa:
- `anillo_ext` y `anillo_int`,
- `MakeSubtraction(anillo_ext, anillo_int)`,
- unión final del anillo hueco con el cuerpo del tubo.

Se ajustó además `sobresale_anillo` a 5.0 para mantener coherencia con Ø40 tricapa.

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_40_script.py`

---

## 2026-04-07 — Fecal Ø40: layer principal en IS_CON_SANE_FAB

### Qué se hizo

- El tubo principal de Ø40 (original `i==0`) pasa de `KN_AIGUA` (`40061`) a `IS_CON_SANE_FAB` (`40148`).
- Las copias mantienen sus capas específicas (`40055`, `40054`).

### Archivos

`pyp-scripts/tub_pvc_tricapa_f_40_script.py`

---

## 2026-04-07 — Anillo fijo en saneamiento (no escalar con longitud de tramo)

### Síntoma

Al alargar un tramo en polilínea, el anillo crecía/disminuía junto al tubo porque se escalaba todo el BRep.

### Causa

`PipelineProcessor.modificar_dimensiones_brep` aplicaba escala longitudinal al sólido completo (tubo + anillo).

### Solución

- Para scripts tricapa de saneamiento se añadió rebuild por tramo con `LargoTramoMm`, regenerando geometría en lugar de escalar el template.
- Se incorporó callback opcional `saneamiento_tube_rebuild` en `PipelineProcessor`.
- Scripts ajustados para recibir `LargoTramoMm`: `tub_pvc_tricapa_v`, `tub_pvc_tricapa_p_110`, `tub_pvc_tricapa_f_110`, `tub_pvc_tricapa_f_40`.
- `tub_pvc_basic_f_25` quedó fuera de este rebuild (mantiene flujo anterior).

### Archivos

`pyp-scripts/saneamiento_polyline.py`, `pyp-scripts/utils/geo_handler.py`, `pyp-scripts/tub_pvc_tricapa_v_script.py`, `pyp-scripts/tub_pvc_tricapa_p_110_script.py`, `pyp-scripts/tub_pvc_tricapa_f_110_script.py`, `pyp-scripts/tub_pvc_tricapa_f_40_script.py`

---

## 2026-04-04 — Pluvial Ø110 y Fecal Ø110: scripts separados (`p_110` / `f_110`)

### Qué se hizo

- **`tub_pvc_tricapa_p_110_script.py`** + **`TubPvcTricapaP110Script`**: Pluvial 110 mm (delega en `TuboPVCConFlecha(0, doc)` de `tub_pvc_tricapa_v_script.py`).
- **`tub_pvc_tricapa_f_110_script.py`** + **`TubPvcTricapaF110Script`**: Fecal 110 mm (misma geometría; tubo con color Allplan **4**; flecha sin cambio).
- Claves registro: **`tub_pvc_tricapa_p_110`**, **`tub_pvc_tricapa_f_110`**.
- Hook `saneamiento_polyline.py`: enrutado directo por diámetro; eliminado recoloreado manual de fecal 110 en el hook.
- Se mantiene **`tub_pvc_tricapa_v`** para Pluvial Ø40 (`TipoTubo=2`) y como módulo que define `TuboPVCConFlecha`.

### Archivos

`polyline_reg_saneamiento.py`, `saneamiento_polyline.py`, `PALETA_TIPOS_INSTALACION_SANEAMIENTO.md`, `ALINEACION_TUBO_PLUVIAL_POLILINEA.md`, comentario en `geo_handler.py`.

---

## 2026-04-04 — Renombrado `tub_pvc_tricapa_script` → `tub_pvc_tricapa_f_40_script`

### Qué se hizo

- Fichero: **`tub_pvc_tricapa_f_40_script.py`** (antes `tub_pvc_tricapa_script.py`).
- Clase: **`TubPvcTricapaF40Script`** (antes `TubPvcTricapaScript`).
- Clave registro / `element_key` para Fecal Ø40: **`tub_pvc_tricapa_f_40`**.
- El **`installation_types[].key` "tub_pvc_tricapa"** (combo “Fecal” en PolyLib) **no cambia**.

### Archivos

`polyline_reg_saneamiento.py`, `saneamiento_polyline.py`, comentarios en `geo_handler.py`, `PALETA_TIPOS_INSTALACION_SANEAMIENTO.md`, entradas históricas en este registro donde citaba el script antiguo.

---

## 2026-04-04 — Renombrado `tub_pvc_basic_script` → `tub_pvc_basic_f_25_script`

### Qué se hizo

- Fichero: `tub_pvc_basic_script.py` → **`tub_pvc_basic_f_25_script.py`**.
- Clase del PythonPart: **`TubPvcBasicF25Script`** (antes `TubPvcBasicScript`).
- Clave de registro / `element_key`: **`tub_pvc_basic_f_25`** (convención `create_element`: módulo `pyp-scripts.tub_pvc_basic_f_25_script`).

### Archivos

`polyline_reg_saneamiento.py`, `saneamiento_polyline.py`, comentarios en `geo_handler.py`, `PALETA_TIPOS_INSTALACION_SANEAMIENTO.md`.

---

## 2026-04-04 — Fecal Ø40: anillo en el extremo equivocado tras orientar el tubo

### Síntoma

El tubo seguía bien la polilínea horizontal, pero el **anillo** quedaba del lado incorrecto respecto al sentido esperado (como `tub_pvc_tricapa_v`).

### Causa

`tub_pvc_tricapa_f_40` aplica **180° en X** al BRep del Ø40 **antes** de exportarlo. `tub_pvc_tricapa_v` construye con **Ry(90)** y luego **180° en X**. Tras centrar y aplicar solo Ry(90) en el pipeline, el orden efectivo respecto a la V invertía en qué extremo del eje local (+X) queda el anillo.

### Solución

Después de Ry(90), aplicar **espejo en X** (`Scaling(-1, 1, 1)`) sobre el BRep ya centrado, solo en el caso `tubo_saneamiento` con eje largo dominante Z (tubo tricapa “plano”, no tricapa_v).

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-scripts/utils/geo_handler.py` | Tras `mat_z_to_x`, `mat_flip_x` con `SetScaling(-1,1,1)`. |

---

## 2026-04-04 — Saneamiento: tubo horizontal en planta aparecía vertical (columna)

### Síntoma

Polilínea **horizontal** en XY (p. ej. dirección +Y); el tubo tenía la longitud correcta pero quedaba **vertical** (eje Z), no siguiendo el tramo.

### Causa

`tub_pvc_tricapa_f_40` modela el tramo largo en **Z** local. `_aplicar_transformacion` aplica el **yaw** como rotación alrededor del **eje Z global**, que deja invariante la dirección Z local: el tubo seguía alineado con el mundo Z. El pipeline de conducto asume el eje largo en **X** local (como los tubos Agua y como `tub_pvc_tricapa_v`, que ya aplica 90° en Y al construir).

### Solución

Tras centrar el BRep en el origen, si `element_type_core == "tubo_saneamiento"` y la mayor dimensión del bbox es **Z**, aplicar **rotación +90° alrededor de Y** (igual que `tricapa_v`), mapeando el eje largo Z→X antes del pitch/yaw. No se aplica si el eje largo ya es X (tricapa_v) ni para `tub_pvc_basic_f_25` (largo en X).

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-scripts/utils/geo_handler.py` | Bloque en `_aplicar_transformacion` tras normalizar al centro. |

---

## 2026-04-05 — Fecal Ø40 mm: tubo y anillo mal deformados en polilínea

### Síntoma

Con **Fecal** y **Ø40**, el PythonPart correcto (`tub_pvc_tricapa_f_40`, `TipoTubo=2`) se instanciaba y el segmento tenía `diameter=40`, pero la geometría en vista parecía incorrecta (anillo “sobredimensionado” o tubo distorsionado).

### Causa

`PipelineProcessor.modificar_dimensiones_brep` escalaba **solo el eje X** y tomaba como longitud actual `max(X)−min(X)` del BRep. En `tub_pvc_tricapa_f_40_script._build_tube` el tramo largo del cubo va en **Z**; en X solo cabe el diámetro (~40 mm). El factor de escala quedaba ~`L_segmento / 40`, estirando la sección transversal en lugar del eje del tubo.

### Solución

Para `element_type_core == "tubo_saneamiento"` se usa `_modificar_dimensiones_brep_longest_bbox_axis`: se elige el eje (X, Y o Z) con **mayor extensión** en el bounding box de vértices y se aplica `Scaling` solo ahí. `tub_pvc_tricapa_v` (eje largo ya en X tras su rotación) sigue comportándose bien. Log de depuración: `[SANEAMIENTO][TUBO] stretch eje=…`.

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-scripts/utils/geo_handler.py` | Nuevo helper + rama en `modificar_dimensiones_brep`. |

---

## 2026-04-05 — Convención de registro en este `.md`

Se documenta en el propio registro la obligación de **actualizar este archivo** con cada cambio posterior en Saneamiento PolyLib.

**Archivos:** `pyp-scripts/docs/registro_de_implementacion.md`

---

## 2026-04-05 — Sincronización paleta de diámetro al cambiar Pluvial ↔ Fecal

### Síntoma

Tras iniciar con **Pluvial** (Ø110) y pasar a **Fecal**, el combo de diámetro seguía mostrando **110 mm**, pero la geometría y los logs usaban el tubo fecal de **25 mm** (primer valor de la lista `[25, 40, 110]`).

### Causa

En **PolyLib**, `PolylineScriptObject.resolve_installation_config()` actualiza `so.diameter_type` y la lista del combo vía `ctrl_prop_util`, pero **no escribe** el valor coherente en el parámetro de paleta `build_ele.DiameterType`. La UI queda con el valor anterior; la lógica Python usa el nuevo `diameter_type`.

### Solución (sin modificar PolyLib)

En `saneamiento_polyline.py` se **envuelve** `resolve_installation_config` del `script_object` al crear el objeto (`create_script_object`):

1. Antes de llamar al `resolve` original, se lee el diámetro actual de la paleta (`DiameterType`).
2. Después del `resolve`, si ese valor sigue siendo **válido** en la nueva lista de diámetros del tipo de instalación, se unifican `so.diameter_type` y `build_ele.DiameterType` a ese valor (p. ej. se mantiene **110** al pasar de Pluvial a Fecal).
3. Si no es válido, se toma el diámetro que dejó PolyLib y se **sincroniza la paleta** para que coincida con lo que usa el código.

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-scripts/saneamiento_polyline.py` | `_parse_diameter_palette_value`, `_diameter_list_as_ints`, `_patch_resolve_installation_config_sync_diameter`, llamada desde `create_script_object`. |

### Notas

- No altera `Instalaciones/PolyLib`.
- Relacionado con `PALETA_TIPOS_INSTALACION_SANEAMIENTO.md`.

---

## 2026-04-05 — Fecal Ø110: evitar tubo “sin anillo” en polilínea (`tubo_saneamiento`)

### Síntoma

En ciertos casos el tramo se generaba con geometría de tubo de agua (polietileno) en lugar del PythonPart PVC tricapa con anillo.

### Causa

`PipelineProcessor` llamaba a `_get_tubo_models_for_segment()` con `tube_system` del segmento (p. ej. **Fecal**). `_normalize_tube_family` devolvía **`polietile`**, y el modelo dinámico de Agua **sustituía** el template cargado desde `tub_pvc_tricapa_v`.

### Solución

Si `element_type_core == "tubo_saneamiento"`, no se usan modelos dinámicos de tubo: siempre el template del hook (`self.templates["tubo_saneamiento"]`).

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-scripts/utils/geo_handler.py` | Rama que fuerza `dynamic_tube_models = []` para `tubo_saneamiento`. |

---

## 2026-04-06 — String table EN: `saneamiento_polyline_eng.xml`

### Síntoma

Allplan informaba que no existía el fichero de tabla de cadenas en inglés junto al `.pyp`.

### Solución

Creación de `pyp-library/saneamiento_polyline_eng.xml` (tabla mínima; ampliable si se usan `TextId` localizados en el `.pyp`).

### Archivos

| Archivo | Cambio |
|--------|--------|
| `pyp-library/saneamiento_polyline_eng.xml` | Nuevo. |

---

## 2026-04-06 — Paleta Pluvial/Fecal, rutas de tubos y documentación auxiliar

### Qué se hizo

- Registro PolyLib (`polyline_reg_saneamiento.py`): etiquetas **Pluvial** / **Fecal** unificadas; Fecal con diámetros **25, 40, 110**; `tub_pvc_basic_f_25` en `elements3D` para Ø25.
- Hook `saneamiento_polyline.py`: enrutado por `element_key` (`basic_f_25`, `tricapa_f_40`, `tricapa_f_110`, `tricapa_p_110`, `tricapa_v` para Pluvial Ø40).
- Ajuste de alineación de tubo saneamiento en `geo_handler.py` (eje del segmento).
- Colores Ø110 Pluvial/Fecal en scripts dedicados `tub_pvc_tricapa_p_110` / `tub_pvc_tricapa_f_110`.
- Documentos `PALETA_TIPOS_INSTALACION_SANEAMIENTO.md` y `ALINEACION_TUBO_PLUVIAL_POLILINEA.md`.

### Archivos (resumen)

`polyline_reg_saneamiento.py`, `pyp-scripts/saneamiento_polyline.py`, `pyp-scripts/utils/geo_handler.py`, `pyp-scripts/tub_pvc_tricapa_v_script.py`, `pyp-scripts/docs/PALETA_TIPOS_INSTALACION_SANEAMIENTO.md`, `pyp-scripts/docs/ALINEACION_TUBO_PLUVIAL_POLILINEA.md`.

---

*Última actualización del índice: 2026-04-07.*
