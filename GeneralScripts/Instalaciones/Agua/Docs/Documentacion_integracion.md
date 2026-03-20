# Integracion polilinea <-> PythonParts (Agua)

## Objetivo

Documentar el estado actual de la integracion entre polilinea y PythonParts de `Agua`, incluyendo:

- Seleccion dinamica correcta por sistema (`Polietile`, `Multicapa`, `Armaflex`), diametro y distribucion.
- Reglas de atributos/layers para elementos TD con doble BRep (`outer` + `inner`).
- Casos especiales `inner-only` (reductores y TE mixtas) y su comportamiento de paleta.
- Validaciones y mensajes al usuario para combinaciones no soportadas.

---

## 1) Flujo general de generacion

Archivo principal: `Agua/pyp-scripts/agua_polyline.py`.

1. La polilinea guarda por segmento: diametro, distribucion, sistema y tipo de agua.
2. Se instancian templates base (`tubo`, `codo`, `manguito`, `te`).
3. `PipelineProcessor` (en `utils/geo_handler.py`) reconstruye cada elemento por segmento/nodo con seleccion dinamica por diametros.
4. `_create_elements_with_layers_attrs(...)` aplica:
   - defaults del modelo generado,
   - attrs/layers de paleta,
   - atributo padre,
   - numeracion.

---

## 2) Seleccion dinamica por sistema de tubo

Archivo: `Agua/pyp-scripts/utils/geo_handler.py`.

### 2.1 Problema corregido

Antes, la creacion dinamica de tubo usaba siempre familia polietileno; por eso en `Multicapa TD` podia crear `TubPolietileTDModel`.

### 2.2 Implementacion actual

- Se normaliza `seg_info.system` a familia interna:
  - `polietile`
  - `multicapa`
  - `armaflex`
- Se cargan clases por familia y distribucion:
  - `TubPolietileModel` / `TubPolietileTDModel`
  - `TubMulticapaTDModel`
  - `ArmaflexModel` (TD)
- El cache de tubo incluye familia y agua:
  - `(family, dist, diameter, water)`

Resultado: `Multicapa TD` y `Armaflex TD` usan su clase correcta, sin contaminarse con `Polietile`.

---

## 3) Reglas TD outer/inner (layers y atributos)

Archivos:

- `Agua/pyp-scripts/agua_polyline.py`
- `Agua/pyp-scripts/utils/attributes_utils.py`
- `Agua/pyp-scripts/utils/geo_handler.py`

### 3.1 Regla funcional

Para elementos TD con par `outer + inner`:

- `outer` con `Material=CAVITAT`:
  - conserva su material y su layer default de modelo,
  - no se pisan attrs/layer desde paleta.
- `inner`:
  - si recibe attrs/layer de paleta,
  - si recibe atributo padre.

### 3.2 Atributo padre por distribucion

- `TD`: solo `pmp_pare`.
- `IS`: `pmp_pare` + `6_CC_IS`.

Adicionalmente, en TD se elimina explicitamente `6_CC_IS` si llega por defaults previos.

---

## 4) Preservacion de atributos al transformar BReps

Archivo: `Agua/pyp-scripts/utils/geo_handler.py`.

### Problema corregido

En varias rutas de transformacion/retorno se recreaba `ModelElement3D` sin copiar atributos, perdiendo por ejemplo `Material=CAVITAT`.

### Solucion

Se centralizo la creacion con helper interno que siempre copia atributos del modelo fuente en los modelos transformados.

Impacto:

- Codos TD, manguitos TD y TE TD mantienen atributos de origen tras rotacion/escalado/traslado.

---

## 5) Casos especiales inner-only

### 5.1 Manguito reductor TD (ej. 25-20)

Archivos:

- `Agua/pyp-scripts/utils/geo_handler.py`
- `Agua/pyp-scripts/manguito_005_td.py`

Comportamiento:

- Si el modelo dinamico devuelve 1 solo BRep en TD reductor, se trata como `manguito_inner`.
- Se omite crear `manguito_inner` desde template.
- El modelo especial queda preparado para paleta (layer/attrs normales, sin `Material=CAVITAT` de outer).

### 5.2 TE TD mixta inner-only

Archivos:

- `Agua/pyp-scripts/utils/geo_handler.py`
- `Agua/pyp-scripts/te_003_td.py`

Comportamiento:

- Si la TE dinamica TD mixta devuelve 1 solo BRep, se trata como `te_inner`.
- Se omite `te_inner` template.
- Para `type_te >= 3`, se aplican attrs de `_create_attributes()` (no attrs de outer CAVITAT).

---

## 6) Priorizacion correcta de defaults por diametro real

Archivo: `Agua/pyp-scripts/agua_polyline.py`.

Se invirtio la prioridad del merge de defaults:

- ahora ganan los attrs del modelo dinamico real (diametro efectivo),
- los defaults cacheados por key quedan como base/fallback.

Esto corrige casos donde se generaba diametro 25 pero quedaban attrs de 20.

---

## 7) Resolucion robusta de keys de paleta (inner)

Archivo: `Agua/pyp-scripts/agua_polyline.py`.

Para `*_inner` se agrego fallback de key (`seg_*_elem_*`) en indices vecinos cuando hay corrimiento entre seleccion y reconstruccion final.

Objetivo: evitar perdidas de layer/atributo padre por desalineacion de key en elementos inner.

---

## 8) Mensajes al usuario por distribucion no soportada

Archivos:

- `Agua/pyp-scripts/multicapa_script.py`
- `Agua/pyp-scripts/armaflex_script.py`

Si el usuario intenta `IS` en esos sistemas, el mensaje ahora incluye pasos:

1. Volver a modo creacion.
2. Cambiar distribucion a TD.
3. Volver a modo configuracion.

---

## 9) Validacion de combinaciones de TE no soportadas

Archivo: `Agua/pyp-scripts/utils/geo_handler.py`.

Se agrego validacion previa de combinacion `(di_in, di_out, di_branch)` para TE (IS y TD):

- Si no existe TE para esa combinacion (ej. `20-25-20`), se muestra mensaje y no se crea TE fallback incorrecta.
- El mensaje indica que deben ajustarse diametros de segmentos para coincidir con tipos de TE disponibles.
- Se cachea la advertencia para no repetir popups identicos en bucle.

---

## 10) Ajustes de parametros de modelos TD

### Manguito TD

Archivo: `Agua/pyp-scripts/manguito_005_td.py`

- Correccion de parametros `M25`:
  - `LAYER_SHORT_INNER` correcto.
  - `Material=CAVITAT` en outer.

### TE TD

Archivo: `Agua/pyp-scripts/te_003_td.py`

- Fallback de layer para casos especiales (`LAYER_SHORT_OUTER` -> `LAYER_SHORT_INNER` / `LAYER_SHORT` cuando aplica).

---

## 11) Estado funcional esperado

1. Tuberia dinamica respeta sistema real (`Polietile`, `Multicapa`, `Armaflex`).
2. En TD con outer+inner:
   - outer CAVITAT protegido,
   - inner por paleta.
3. Atributo padre:
   - TD: solo `pmp_pare`,
   - IS: `pmp_pare` + `6_CC_IS`.
4. Reducers y TE mixtas inner-only reciben comportamiento de inner.
5. Combinaciones TE invalidas muestran error y no generan geometria incorrecta.

---

## 12) Archivos impactados (resumen)

- `Agua/pyp-scripts/agua_polyline.py`
- `Agua/pyp-scripts/utils/geo_handler.py`
- `Agua/pyp-scripts/utils/attributes_utils.py`
- `Agua/pyp-scripts/manguito_005_td.py`
- `Agua/pyp-scripts/te_003_td.py`
- `Agua/pyp-scripts/multicapa_script.py`
- `Agua/pyp-scripts/armaflex_script.py`
