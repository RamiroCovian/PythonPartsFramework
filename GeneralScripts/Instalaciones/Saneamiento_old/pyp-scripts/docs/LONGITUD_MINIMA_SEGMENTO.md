# Longitud mínima de segmento – Documentación

Documentación de la implementación de longitud mínima de segmentos en el script de Saneamiento (polilíneas 3D). Evita segmentos residuales o demasiado cortos que dificultan la edición y ensucian el modelo.

---

## 1. Resumen

Se aplican **dos valores mínimos** configurables desde la paleta (con constantes por defecto en código):

| Concepto | Uso principal |
|----------|----------------|
| **Longitud mínima de segmento** | Al **añadir** puntos (trazado) y al **arrastrar** vértices. El segmento nunca queda por debajo de este valor. |
| **Longitud mínima para insertar punto** | Al **insertar** un punto en un segmento existente. Los dos tramos resultantes deben ser ≥ este valor. |

Ambos son editables en la paleta (1–5000 mm) y tienen valor por defecto 600 mm en el script.

---

## 2. Parámetros en la paleta

En la página **Dimensiones / Parámetros del tubo** del PythonPart Saneamiento:

- **Longitud mínima de segmento (mm)**  
  - Nombre interno: `LongitudMinimaSegmento`  
  - Valor por defecto: 600  
  - Rango: 1–5000 mm  
  - Afecta: trazado (añadir punto), arrastre de vértices y preview.

- **Longitud mínima para insertar punto (mm)**  
  - Nombre interno: `LongitudMinimaInsertar`  
  - Valor por defecto: 600  
  - Rango: 1–5000 mm  
  - Afecta: inserción de punto en un segmento (midpoint o clic en segmento).

---

## 3. Constantes en código

En `Saneamiento.py`, sección *Parámetros de Inserción*:

```text
DEFAULT_MIN_SEGMENT_LENGTH_MM = 600.0   # Por defecto si la paleta no devuelve valor válido
DEFAULT_MIN_INSERT_SEGMENT_LENGTH_MM = 600.0   # Idem para la longitud mínima al insertar
```

- Si la paleta no devuelve un valor válido (o no existe el parámetro), se usan estas constantes.
- Los getters que leen de la paleta son:
  - `_get_min_segment_length_mm()` → `LongitudMinimaSegmento`
  - `_get_min_insert_segment_length_mm()` → `LongitudMinimaInsertar`

---

## 4. Comportamiento por operación

### 4.1 Añadir punto (trazado, clic en vacío)

- **Longitud usada:** Longitud mínima de segmento (paleta).
- **Comportamiento:**
  - Si la distancia del último punto al clic es **menor** que el mínimo pero mayor que un umbral numérico (~0): el nuevo punto se coloca **exactamente a la distancia mínima** en la dirección del clic (“estirado” al mínimo). El clic **sí se acepta**.
  - Si la distancia es **mayor o igual** al mínimo: el punto se coloca donde se hizo clic.
  - Si la distancia es **casi cero** (clic sobre el último punto): no se añade punto y se muestra *"Punto demasiado cerca del anterior"*.
- **Preview:** La línea de goma muestra el tramo “estirado” al mínimo cuando el cursor está por debajo del mínimo, y en la paleta aparece *"Se colocará a distancia mínima (X mm)"*.

### 4.2 Insertar punto en un segmento (midpoint o clic en segmento con modo insertar)

- **Longitud usada:** Longitud mínima para insertar punto (paleta).
- **Comportamiento:**
  - No se permite insertar si, al partir el segmento, **alguno de los dos tramos resultantes** quedaría por debajo de este mínimo.
  - Condiciones:
    - El segmento debe tener longitud ≥ **2 × mínimo para insertar** (para que quepan dos tramos de al menos el mínimo).
    - El parámetro `t` de inserción debe estar en `[t_min, 1 - t_min]`, con `t_min = mínimo_insertar / longitud_segmento`.
  - Si no se cumple: el clic no inserta punto (no hay mensaje específico de “segmento corto”; simplemente no se inserta).

### 4.3 Arrastrar vértice (polilíneas guardadas)

- **Longitud usada:** Longitud mínima de segmento (paleta).
- **Comportamiento:**
  - Al **soltar** el vértice se comprueban los dos segmentos adyacentes.
  - Si **alguno** queda con longitud &lt; mínimo: se **revierte** la posición del vértice a la anterior y se muestra *"No se puede mover: quedaría un segmento menor al mínimo (X mm)"*.
  - Si ambos segmentos son ≥ mínimo: el movimiento se confirma y se actualizan segmentos/geometría según la lógica existente.

### 4.4 Guardar polilínea

- **No** se valida longitud mínima al guardar.
- La longitud mínima se aplica solo en las operaciones anteriores (añadir, insertar, arrastrar), por lo que no se esperan segmentos por debajo del mínimo al guardar. No existe validación adicional ni mensaje de “segmentos menores al mínimo” en el guardado.

---

## 5. Resumen rápido por valor

| Valor (paleta / constante) | Añadir punto | Insertar punto | Arrastrar vértice | Preview (goma) |
|---------------------------|--------------|----------------|-------------------|----------------|
| **Longitud mínima de segmento** | ✅ Estirar al mínimo | — | ✅ Revertir si &lt; mínimo | ✅ Mostrar estirado + mensaje |
| **Longitud mínima para insertar** | — | ✅ No insertar si algún tramo &lt; mínimo | — | — |

---

## 6. Notas técnicas

- **`MIN_SEG_LEN_MM = 1.0`** se usa solo en `_can_insert_here` para rechazar inserción en segmentos prácticamente nulos (evitar divisiones por cero y segmentos degenerados). No es el mínimo configurable por el usuario.
- **Preview:** En modo creación, si hay al menos un punto y el cursor está a distancia &lt; mínimo del último punto, la polilínea de preview se dibuja hasta la distancia mínima en la dirección del cursor y se muestra el mensaje de “Se colocará a distancia mínima”.
- Los valores de la paleta se leen en tiempo de ejecución; no hace falta recargar el script para que un cambio en la paleta tenga efecto en la siguiente operación.

---

## 7. Archivos implicados

- **Script:** `PythonPartsExampleScripts/saneamiento/Saneamiento.py`  
  - Constantes: `DEFAULT_MIN_SEGMENT_LENGTH_MM`, `DEFAULT_MIN_INSERT_SEGMENT_LENGTH_MM`  
  - Getters: `_get_min_segment_length_mm()`, `_get_min_insert_segment_length_mm()`  
  - Lógica: añadir punto (~13720), `_can_insert_here` (~13928), arrastre (~13581), preview (~15140, ~15350), `save_current_polyline` (sin validación de longitud).

- **Paleta:** `Library/Examples/PythonParts/saneamiento/Saneamiento.pyp`  
  - Parámetros: `LongitudMinimaSegmento`, `LongitudMinimaInsertar` (tipo Length, 1–5000 mm, valor por defecto 600).
