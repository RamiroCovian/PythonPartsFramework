# Atributos en Saneamiento: por nombre / por ID y flujo "Aplicar atributos"

Este documento describe cómo funcionan los atributos en `Saneamiento.py` (por nombre o por ID) y el proceso completo cuando el usuario escribe un valor (por ejemplo "BRAIAN") en la paleta y pulsa **Aplicar atributos** sobre un tubo, codo, etc.

---

## 1. ¿Por nombre o por ID?

El script **no** usa siempre lo mismo: depende del atributo.

- **Atributos tipo `pmp_*` o `PMP_*`** (por ejemplo `pmp_pare`, `pmp_nom`, `pmp_seccio`) → se resuelven **siempre por nombre** con la API de Allplan (`GetAttributeID(doc, "nombre")`).
- **Custom attribute 01 … 15 y "Custom attribute"** → se usan **por ID fijo** (mapa `CUSTOM_ATTRIBUTE_IDS` en el script).
- **Otros** (por ejemplo `6_CC_IS`, `Material`) → por defecto **por nombre**. Si en vuestra instalación uno de ellos corresponde a un Custom attribute concreto, se puede mapear en `SCRIPT_ATTR_TO_FIXED_ID` y pasará a usarse **por ID**.

Toda la resolución pasa por la función **`get_attribute_id(doc, name)`**:

| Tipo de nombre | Comportamiento |
|----------------|----------------|
| `pmp_*` / `PMP_*` | Por **nombre** (API Allplan). |
| Clave en `SCRIPT_ATTR_TO_FIXED_ID` | Por **ID** (valor del diccionario). |
| Clave en `CUSTOM_ATTRIBUTE_IDS` (ej. "Custom attribute 01") | Por **ID** (1083, 1084, …). |
| Resto (ej. `"Material"`, `"6_CC_IS"`) | Por **nombre** (API Allplan). |

### Constantes en el script

- **`CUSTOM_ATTRIBUTE_IDS`**: mapa nombre → ID para Custom attribute 01 (1083) hasta Custom attribute 15 (1904) y "Custom attribute" (1947).
- **`SCRIPT_ATTR_TO_FIXED_ID`**: mapa opcional nombre lógico → ID (por ejemplo `"6_CC_IS": 1895` si en vuestra instalación 6_CC_IS es el Custom attribute 06).

### Atributos que escribe "Aplicar atributos"

El botón **Aplicar atributos** solo escribe en estos dos atributos del elemento (tubo, codo, etc.):

- **6_CC_IS**
- **pmp_pare**

El texto que el usuario escribe en la paleta (por ejemplo "BRAIAN") es el **valor** que se asigna a ambos; no es el nombre de otro atributo.

### Atributo "Material"

- **No** se escribe con "Aplicar atributos".
- Solo se **lee** en el script para detectar elementos con `Material = "CAVITAT"` y no aplicarles atributos padre (ni numeración). Se resuelve por **nombre** en `get_attribute_id(doc, "Material")`.

---

## 2. Caso completo: poner "BRAIAN" a un tubo y aceptar

Flujo desde que el usuario escribe "BRAIAN" en la paleta hasta que el tubo (o codo, etc.) tiene los atributos con ese valor.

### 2.1 En la paleta

- El usuario abre el expander **"Atributos Padre"** en la paleta del PythonPart.
- En **"Valor atributo"** (`ValorAtributos`) escribe **BRAIAN**.
- Pulsa el botón **"Aplicar atributos"** (EventId **1011**).

### 2.2 Disparo del evento

- Allplan envía el evento **1011** al ScriptObject.
- El manejador de eventos del script llama a:
  - `intr.apply_attributes_to_selected()`

### 2.3 Lectura del valor

- `apply_attributes_to_selected()` lee el contenido de la paleta:
  - `valor_atributos = _safe_get_palette_property("ValorAtributos", "")` → **"BRAIAN"**.
- Si el valor está vacío, se muestra el mensaje de error y no se hace nada más.
- Si no, se usa ese string (p. ej. `"BRAIAN"`) para los atributos.

### 2.4 Sobre qué se aplica

- Se aplica a los **segmentos seleccionados**:
  - Si hay varios segmentos seleccionados (`selected_segments`), se recorre esa lista.
  - Si no, se usa el segmento actualmente seleccionado o bajo el cursor (`selected_seg` o `hover_seg`).
- Para cada uno se llama a:
  - `_apply_attributes_to_segment(path_idx, seg_idx, "BRAIAN")`.

### 2.5 Guardado en datos del segmento (sin tocar aún el 3D)

- `_apply_attributes_to_segment` **no modifica todavía** el tubo/codo 3D.
- Solo actualiza el estado interno del script:
  - Localiza el segmento por `path_idx` y `seg_idx` (puntos en `saved_paths`).
  - Busca en `saved_segments` un segmento con los mismos dos puntos.
  - **Si lo encuentra**: añade en `saved_segments[i]["custom_attributes"]` una entrada con una clave única (timestamp) y el valor **"BRAIAN"**.
  - **Si no lo encuentra**: crea una nueva entrada en `saved_segments` con `points`, `diameter`, `section_type`, etc., y `"custom_attributes": { attr_key: "BRAIAN" }`.
- Así, **"BRAIAN" queda asociado a ese segmento** en memoria (`saved_segments[].custom_attributes`).

### 2.6 Mensaje y redibujo

- Se muestra el mensaje de éxito (segmentos a los que se aplicó el valor).
- Se redibuja el preview si aplica.

### 2.7 Cuándo se escribe en el tubo/codo 3D

- Los atributos se escriben en el **elemento 3D** (tubo, codo, reductor, etc.) cuando se **construye el modelo** en `create_ele` (por ejemplo al guardar la polilínea o al regenerar el PythonPart).
- Para cada segmento:
  - Se obtienen los atributos guardados con `_find_segment_info(p1, p2)` o `_get_custom_attributes_for_segment(p1, p2)` → devuelven el diccionario `custom_attributes` (p. ej. `{ "attr_...": "BRAIAN" }`).
  - Se llama a **`_add_custom_attributes_to_list(attr_list, custom_attrs, self.document)`**:
    - Se toma el **primer valor** del diccionario → **"BRAIAN"**.
    - Se obtienen los IDs de **6_CC_IS** y **pmp_pare** con **`get_attribute_id(doc, "6_CC_IS")`** y **`get_attribute_id(doc, "pmp_pare")`** (por nombre o por ID según la configuración anterior).
    - Se añaden a `attr_list` los `AttributeString` correspondientes con valor **"BRAIAN"**.
  - Esa lista de atributos se asigna al elemento con `element.SetAttributes(attributes)`.

Resultado en el tubo (o codo, etc.): **6_CC_IS = "BRAIAN"** y **pmp_pare = "BRAIAN"**.

---

## 3. Resumen en tabla

| Paso | Qué ocurre |
|------|------------|
| 1 | Usuario escribe "BRAIAN" en "Valor atributo" y pulsa "Aplicar atributos" (evento 1011). |
| 2 | `handle_event(1011)` llama a `apply_attributes_to_selected()`. |
| 3 | Se lee `ValorAtributos` → `"BRAIAN"`. |
| 4 | Para cada segmento seleccionado (o bajo el cursor) se llama `_apply_attributes_to_segment(..., "BRAIAN")`. |
| 5 | Se actualiza o se crea la entrada en `saved_segments` con `custom_attributes` conteniendo el valor "BRAIAN". |
| 6 | Mensaje de éxito y redibujo del preview. |
| 7 | En la **siguiente construcción del modelo** (`create_ele`), para cada tubo/codo se obtienen sus `custom_attributes`, se llama `_add_custom_attributes_to_list` con ese valor y se asignan **6_CC_IS** y **pmp_pare** al elemento con `SetAttributes`. |

Importante: **"Aplicar atributos" solo guarda el valor en los datos del segmento**. Los elementos 3D se actualizan la **próxima vez que se genere el modelo** (por ejemplo al guardar la polilínea o al volver a abrir/regenerar el PythonPart).

---

## 4. Referencia rápida: nombre vs ID

| Atributo   | Resolución actual |
|-----------|--------------------|
| **pmp_pare** | Por **nombre** (siempre, regla `pmp_*`). |
| **6_CC_IS**  | Por **nombre** por defecto; por **ID** si está en `SCRIPT_ATTR_TO_FIXED_ID`. |
| **Material** | Solo lectura (CAVITAT); por **nombre**. |
| Custom attribute 01 … 15, "Custom attribute" | Por **ID** (mapa `CUSTOM_ATTRIBUTE_IDS`). |

Si en vuestra instalación **6_CC_IS** corresponde a un Custom attribute con ID conocido (por ejemplo 1895), podéis añadir en el script:

```python
SCRIPT_ATTR_TO_FIXED_ID = {"6_CC_IS": 1895}
```

y ese atributo pasará a usarse por ID.
