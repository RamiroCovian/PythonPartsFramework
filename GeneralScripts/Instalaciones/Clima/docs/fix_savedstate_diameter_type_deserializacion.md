# Fix: deserialización de `diameter_type` en SavedState (polilínea)

Documento técnico del cambio en **PolyLib** que corrige el error  
`ValueError: invalid literal for int() with base 10: '150x150'` al restaurar el estado guardado de la polilínea **Clima** (y mantiene compatibilidad con instalaciones que usan diámetro numérico).

---

## 1. Resumen del problema

| Aspecto | Detalle |
|--------|---------|
| **Síntoma visible** | En consola/log: `[SO] Error deserializando estado: invalid literal for int() with base 10: '150x150'` (a veces duplicado si se intenta leer estado desde varias fuentes). |
| **Consecuencia para el usuario** | El **SavedState** no se aplica correctamente; la polilínea puede arrancar como “primera creación” o sin recuperar diámetro / resto de campos del bloque que falló. |
| **Causa raíz** | **Desajuste de contrato** entre **serialización** y **deserialización** del campo JSON `diameter_type`. |

---

## 2. Dónde encaja en el flujo de la polilínea

1. **Guardar estado**  
   - Módulo: `Instalaciones/PolyLib/script_object.py`  
   - Método: `PolylineScriptObject._serialize_state_to_json()` (aprox. líneas 2012–2078).  
   - Construye un diccionario `state` y lo serializa con `json.dumps`.  
   - Para el diámetro escribe (aprox. línea **2060**):

     ```python
     "diameter_type": f"{getattr(self.build_ele, ParamNames.Installation.DIAMETER_TYPE).value}",
     ```

   - En **perfil Clima**, el parámetro de paleta del diámetro es un **combo de texto** (`150x150`, `750x150`, `reductor`, etc.).  
   - Por tanto, en el JSON el valor queda como **cadena**, p. ej. `"150x150"` (a veces número si otro perfil guarda entero).

2. **Restaurar estado**  
   - Módulo: `Instalaciones/PolyLib/interactor.py`  
   - Método: `PolylineInteractor._deserialize_state_from_json(self, json_str: str)` (aprox. líneas 421 en adelante).  
   - Se invoca al **iniciar entrada** / edición cuando hay una cadena JSON en parámetros como `SavedState`, `PolylineState`, `StateData`, o embebida en **PythonPartGroup** (lógica previa en el mismo `interactor`, aprox. líneas 369–405).  
   - Tras `json.loads`, se reasignan `build_ele` y `script_object` desde `state`.

3. **El fallo concreto (antes del fix)**  
   - En la rama `if "diameter_type" in state:` se hacía:

     ```python
     _value = int(state["diameter_type"])
     ```

   - Eso es correcto solo si el valor es **numérico** (p. ej. tubo de saneamiento en mm como entero).  
   - Con **Clima**, `state["diameter_type"] == "150x150"` → `int("150x150")` lanza **ValueError** y **toda** la deserialización aborta (bloque `try` del método).

---

## 3. Líneas eliminadas sustituidas (referencia histórica)

En **`PolyLib/interactor.py`**, método **`PolylineInteractor._deserialize_state_from_json`**, antes del fix existía el siguiente bloque (sustituido por completo; **las líneas en disco dependían de la revisión**; el texto es literal de la versión previa):

```python
            if "diameter_type" in state:
                _value = int(state["diameter_type"])

                param = getattr(self.script_object.build_ele, ParamNames.Installation.DIAMETER_TYPE)
                param.value = _value

                self.script_object.diameter_type = _value
```

---

## 4. Líneas agregadas: rango exacto y texto completo

- **Archivo:** `Instalaciones/PolyLib/interactor.py`  
- **Método:** `PolylineInteractor._deserialize_state_from_json`  
- **Rango de líneas (inclusive):** desde la línea **537** hasta la línea **561** (25 líneas en la revisión donde se aplicó este documento).

**Código completo agregado (sin recortes, orden y espaciado como en el fichero):**

```
            if "diameter_type" in state:
                raw_di = state["diameter_type"]
                if isinstance(raw_di, bool):
                    parsed_di = raw_di
                elif isinstance(raw_di, int):
                    parsed_di = raw_di
                elif isinstance(raw_di, float):
                    parsed_di = int(raw_di) if float(raw_di).is_integer() else raw_di
                else:
                    s_di = str(raw_di).strip()
                    if not s_di:
                        parsed_di = ""
                    elif "x" in s_di.lower() or any(c.isalpha() for c in s_di):
                        # Clima: "150x150", "750x150", "reductor", etc.
                        parsed_di = s_di
                    else:
                        try:
                            parsed_di = int(float(s_di))
                        except ValueError:
                            parsed_di = s_di

                param = getattr(self.script_object.build_ele, ParamNames.Installation.DIAMETER_TYPE)
                param.value = parsed_di

                self.script_object.diameter_type = parsed_di
```

**Mismo bloque, línea de archivo → contenido exacto (una entrada por línea física 537–561):**

| Línea | Contenido exacto (carácter a carácter como en `interactor.py`) |
|------:|---|
| 537 | `            if "diameter_type" in state:` |
| 538 | `                raw_di = state["diameter_type"]` |
| 539 | `                if isinstance(raw_di, bool):` |
| 540 | `                    parsed_di = raw_di` |
| 541 | `                elif isinstance(raw_di, int):` |
| 542 | `                    parsed_di = raw_di` |
| 543 | `                elif isinstance(raw_di, float):` |
| 544 | `                    parsed_di = int(raw_di) if float(raw_di).is_integer() else raw_di` |
| 545 | `                else:` |
| 546 | `                    s_di = str(raw_di).strip()` |
| 547 | `                    if not s_di:` |
| 548 | `                        parsed_di = ""` |
| 549 | `                    elif "x" in s_di.lower() or any(c.isalpha() for c in s_di):` |
| 550 | `                        # Clima: "150x150", "750x150", "reductor", etc.` |
| 551 | `                        parsed_di = s_di` |
| 552 | `                    else:` |
| 553 | `                        try:` |
| 554 | `                            parsed_di = int(float(s_di))` |
| 555 | `                        except ValueError:` |
| 556 | `                            parsed_di = s_di` |
| 557 | *(línea vacía; 0 caracteres visibles, solo fin de línea)* |
| 558 | `                param = getattr(self.script_object.build_ele, ParamNames.Installation.DIAMETER_TYPE)` |
| 559 | `                param.value = parsed_di` |
| 560 | *(línea vacía)* |
| 561 | `                self.script_object.diameter_type = parsed_di` |

*Si se insertan o borran líneas por encima de este bloque en `interactor.py`, los números 537–561 dejarán de coincidir; la localización estable es la rama `if "diameter_type" in state:` justo después de `water_type` y antes de `if "face_en" in state:`.*

---

## 5. Por qué este diseño

1. **Consistencia con lo guardado**  
   `_serialize_state_to_json` ya escribe el **`.value` del combo** como texto en Clima; la deserialización debe poder **volver** a poner ese mismo texto en `param.value` y en `script_object.diameter_type`.

2. **No romper otras instalaciones**  
   Saneamiento (u otras polilíneas) que persisten **entero** o **string solo numérica** siguen recuperando un **entero** en la práctica (`int`/`int(float(...))`).

3. **Marcadores fuertes de “no es número de tubo único”**  
   La presencia de **`x`** (secciones `Ancho×Alto`) o de **letras** (`reductor`) evita forzar `int` sobre valores que no lo son.

4. **`bool` antes que `int`**  
   En Python, `isinstance(True, int)` es verdadero; por eso los `bool` se tratan antes para no interpretar mal un valor raro guardado como booleano.

---

## 6. Compatibilidad hacia atrás y hacia delante

### 6.1 Estados JSON ya guardados (histórico)

| Contenido antiguo de `diameter_type` | Comportamiento tras el fix |
|-------------------------------------|----------------------------|
| Número JSON entero (`110`) | `parsed_di = int`: **igual que antes**. |
| Número JSON float entero (`110.0`) | `parsed_di = int`: prácticamente igual al caso entero. |
| Cadena numérica `"110"` | `parsed_di = 110`: **equivale** al antiguo `int("110")`. |
| Cadena Clima `"150x150"` / `"750x150"` | `parsed_di` string: **antes fallaba**; **ahora se restaura**. |
| Otros textos especiales (`"reductor"`, etc.) | String conservada; **antes fallaba** si no era convertible a `int`. |

**Conclusión:** No se degrada el caso histórico numérico; se **corrige** el caso Clima (y otros textos).

### 6.2 Riesgos residuales (baja probabilidad)

- **Código de diámetro puramente numérico como cadena sin `x`** (p. ej. `"125"`) sigue pasando por `int(float(...))` → entero **125**. Si algún día un perfil combinara “solo dígitos” pero quisiera forzar texto literal `"125"` en el combo, habría que revisar ese perfil por separado (no es el caso típico de Clima).

- **`float` no entero** en JSON: se deja como `float` en `parsed_di`. Depende de que el control de paleta acepte ese tipo; en flujos numéricos clásicos suele venir entero.

### 6.3 Compatibilidad entre versiones de scripts

- **Proyectos guardados con el fix** siguen generando el mismo JSON que antes en `script_object` (no se cambió la serialización en este trabajo).  
- **Versiones viejas del `interactor`** sin el fix siguen incapaces de cargar `'150x150'`; solo la versión **nueva** de PolyLib soluciona la lectura.  
- Actualizar todos los puntos donde se distribuye PolyLib evita ese desfase.

---

## 7. Archivos relacionados (referencia rápida)

| Archivo | Papel |
|---------|--------|
| `PolyLib/interactor.py` | **Fix:** `_deserialize_state_from_json` — rama `diameter_type`. |
| `PolyLib/script_object.py` | **Sin cambios en este fix:** `_serialize_state_to_json` línea ~2060 donde se escribe `"diameter_type"`. |
| `Clima/pyp-scripts/clima_polyline.py` | Usa `diameter_type` / secciones string; beneficiario directo del fix al reabrir polilínea. |

---

## 8. Registro breve en bitácora del proyecto

Este cambio quedó registrado de forma corta en:

- `Instalaciones/Clima/docs/registro_de_cambios.md` (entrada 2026-05-05 — SavedState `150x150`).

---

## 9. Mensaje clave para el equipo

El bug no era que Allplan “no entienda” `150x150`; era que **`int()` sobre un identificador de sección texto** era incorrecto para Clima. El fix **alinea lectura con escritura** del SavedState conservando comportamiento para diámetros numéricos legacy.
