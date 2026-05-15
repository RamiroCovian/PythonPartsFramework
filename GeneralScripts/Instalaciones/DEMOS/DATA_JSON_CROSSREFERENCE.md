# Crossreference Detallado `data.json`

Objetivo: dejar claro, **campo por campo**, qué se rellena, qué puede quedar vacío, y si con lo actual podemos reconstruir al 100%.


## 1) Contexto de esquema 

- `saved_paths`
- `data`
- `layer_default`
- `selected_inst_type`
- `applied_layers`
- `applied_default_attrs`
- `applied_custom_attrs`

No se evalúan otros formatos aquí.

---

## 2) Mapeo detallado campo a campo

### `saved_paths`
- **Tipo esperado:** `list[list[Point3D-like]]`
- **Origen:** puntos guardados de polilíneas (`saved_paths` en interactor/script state)
- **Se rellena cuando:** hay al menos un path aceptado/guardado
- **Puede quedar vacío:** sí (`[]`) si no se guardó ninguna polilínea
- **Qué permite reconstruir:** geometría base completa de la polilínea (topología por orden de puntos)
- **Dependencia crítica:** es el campo más importante para reconstrucción geométrica

### `data`
- **Tipo esperado:** `list[segment_dict]` (ej. `line_1`, `line_2`, ...)
- **Origen:** datos derivados por segmento (delta, longitudes, ángulos, tipo segmento, vector, etc.)
- **Se rellena cuando:** se calcularon segmentos desde `saved_paths`
- **Puede quedar vacío:** sí (`[]`) si no hubo cálculo/segmentación
- **Qué permite reconstruir:** no es necesario para dibujar la línea, pero sí para análisis/QA/cálculos/validación
- **Observación:** puede reutilizarse para verificar integridad geométrica al reimportar

### `layer_default`
- **Tipo esperado:** en tu `data.json` actual es `dict` (`default`, `layer_polyline`, `layer_cuboid_label`)
- **Origen:** defaults de capa por instalación/tipo
- **Se rellena cuando:** se inicializan defaults de instalación correctamente
- **Puede quedar vacío/parcial:** sí
- **Qué permite reconstruir:** asignación de capas por defecto al regenerar
- **Riesgo si falta:** se reconstruye geometría, pero con capas incorrectas o fallback

### `selected_inst_type`
- **Tipo esperado:** `string`
- **Origen:** selección activa de tipo de instalación en paleta/interactor
- **Se rellena cuando:** existe `script_object_interactor` y hay tipo seleccionado
- **Puede quedar vacío:** sí (`""`)
- **Qué permite reconstruir:** contexto de negocio (tipo de conducto/sistema), reglas de defaults y módulos asociados
- **Riesgo si falta:** el modelo puede regenerar, pero con lógica de tipo incorrecta o genérica

### `applied_layers`
- **Tipo esperado real en archivo:** `string` JSON serializado (`"{}"`, `"{...}"`)
- **Origen:** overrides de capa aplicados por segmento/elemento
- **Se rellena cuando:** hubo aplicación manual/específica de capas
- **Puede quedar vacío:** sí (`"{}"`)
- **Qué permite reconstruir:** respetar overrides por elemento (en vez de solo defaults)
- **Riesgo si falta:** regenera, pero pierde personalizaciones de capa

### `applied_default_attrs`
- **Tipo esperado real en archivo:** `string` JSON serializado
- **Origen:** atributos default aplicados a elementos generados
- **Se rellena cuando:** se serializan attrs de default mapping por elemento
- **Puede quedar vacío/parcial:** sí (`"{}"` o entradas con muchos `val: ""`)
- **Qué permite reconstruir:** metadatos funcionales por elemento (IDs de atributos, valores base)
- **Riesgo si falta:** geometría sí, pero pérdida de metadatos/documentación/etiquetado

### `applied_custom_attrs`
- **Tipo esperado real en archivo:** `string` JSON serializado
- **Origen:** atributos custom aplicados por usuario/regla
- **Se rellena cuando:** existen custom attrs efectivos
- **Puede quedar vacío/parcial:** sí (`"{}"` o subset de elementos)
- **Qué permite reconstruir:** customización por elemento (clasificación, códigos internos, etc.)
- **Riesgo si falta:** pérdida de personalización, aunque la forma geométrica pueda regenerar

---

## 3) Qué significa “en blanco” 

Hay 4 estados válidos distintos:

1. `[]` -> no hay colección de datos (paths/segmentos)
2. `""` -> string no informado (`selected_inst_type`)
3. `"{}"` -> objeto vacío serializado como texto (applied_*)
4. `val: ""` dentro de atributos -> atributo presente sin valor útil

Conclusión: “vacío” no siempre significa error; depende del campo y de si es obligatorio para el flujo.

---

## 4) ¿Con lo actual se puede reconstruir la polilínea?

## Sí, para polilínea base:
- Con `saved_paths` se puede reconstruir la geometría principal.
- `data` ayuda para control/consistencia, pero no es estrictamente necesario para redibujar.

## No al 100% de fidelidad funcional total (sin supuestos):
Faltan garantías absolutas si no están siempre presentes:
- `selected_inst_type` consistente,
- defaults/overrides de capas,
- atributos default/custom completos y parseables,
- cualquier lógica runtime no serializada (módulos/parametrías dinámicas de generación).

---

## 5) Conclusión final punto por punto (lo que sí / lo que no / lo que falta)

### A. Lo que SÍ podemos hacer hoy con lo que tenemos
1. Rehacer geometría de polilínea desde `saved_paths`.
2. Recalcular o validar segmentos usando `data`.
3. Recuperar parte del contexto de instalación (`selected_inst_type`).
4. Restaurar capas/attrs cuando `applied_*` viene poblado y parsea bien.

### B. Lo que NO está garantizado hoy al 100%
1. Reproducción exacta de todas las decisiones de negocio si `selected_inst_type` está vacío/inconsistente.
2. Reaplicación exacta de capa/atributos si `applied_layers` o attrs vienen vacíos/parciales.
3. Fidelidad completa de cualquier comportamiento dependiente de estado runtime no serializado.

### C. Qué necesitamos para “100% working” (rebuild fiel y robusto)
1. **Contrato único de esquema** (el de este documento) y validación estricta en import/export.
2. **Campos obligatorios mínimos** en guardado:
   - geometría (`saved_paths`),
   - tipo de instalación (`selected_inst_type`),
   - capas efectivas finalizadas por elemento (si aplica),
   - attrs efectivas finalizadas por elemento (si aplica).
3. **Normalizar tipos**:
   - evitar `applied_*` como string JSON; guardarlos como objeto nativo JSON.
4. **Validación al cargar**:
   - checks de obligatoriedad,
   - fallbacks explícitos con warning,
   - reporte de campos faltantes.
5. **Test de round-trip**:
   - export -> import -> regenerate -> comparar (geometría + capas + attrs).

---

## CONCLUSION 2

Si el objetivo inmediato es reconstrucción de trazado, estás bien.  
Si el objetivo es “reconstrucción idéntica funcional/documental al 100%”, hace falta cerrar contrato de esquema + obligatoriedad + validación de metadatos.

