# Documentación — Instalación Clima (Allplan PythonParts)

Instalación MEP de **climatización** basada en **polilínea**: permite trazar recorridos de planta tipo retícula con giros en múltiplos de **90°** y además un “quiebro” predefinido en **±14.42°** (el segmento de `±14.42°` se transforma en el PythonPart `Quiebro`). Genera tramos (`tram_recte`) y codos (`colze`) como geometría 3D previa y, al finalizar, como PythonParts. Forma parte del paquete compartido `Instalaciones` junto con **PolyLib** y **GeometryTools**.

---

## 1. Contexto en `Instalaciones`

| Componente | Función respecto a Clima |
|------------|---------------------------|
| **`Instalaciones/__init__.py`** | Paquete Python; puede estar vacío. Debe existir para importar `Instalaciones.Clima`, `Instalaciones.PolyLib`, etc. |
| **`Instalaciones/PolyLib`** | Motor de polilínea: registro de instalaciones, interactor, `PolylineScriptObject`, hooks de previsualización y de capas/atributos. Ver `PolyLib/README.md`. |
| **`Instalaciones/GeometryTools`** | Utilidades 3D (`CreateSmartGeo`: cilindros, cuboides, bucles, booleanas). La **polilínea activa** usa sobre todo BREP de catálogo; varios módulos `*_3D.py` de Clima sí importan `CreateSmartGeo`. |

---

## 2. Estructura de la carpeta `Clima`

```
Clima/
├── DOCUMENTACION.md          ← este archivo
├── polyline_reg_clima.py     ← Registro de la instalación "CLIMA" (metadatos + setup)
├── pyp-library/
│   ├── ___pyp__               ← Definición XML del PythonPart (paleta)
│   ├── clima_polyline.pyp    ← Copia/alternativa del XML de parámetros
│   ├── clima_polylinebackup.pyp
│   ├── tram_recte.pyp
│   └── colze.pyp
└── pyp-scripts/
    ├── clima_polyline.py      ← Script principal de la polilínea (hooks)
    ├── utils/
    │   ├── geo_handler.py    ← GeometryHandler + PipelineProcessor
    │   └── segments.py
    ├── tram_recte_script.py  ← PythonPart "tram recte" (registrado)
    ├── Tram_recte.py         ← Lógica/modelo del tramo
    ├── colze_script.py       ← PythonPart "colze" (registrado)
    ├── colze.py
    ├── tram_recte_script.py
    └── …                     ← Otros piezas (catálogo / futuro): conducto_*, codo_90_*, conexion_*, difusor_*, manguito_*, reduccions, pantalons, etc.
```

El **punto de entrada** que Allplan carga como PythonPart de polilínea es el script indicado en el XML (`___pyp__` / `clima_polyline.pyp`):  
`Instalaciones\Clima\pyp-scripts\clima_polyline.py`.

---

## 3. Registro — `polyline_reg_clima.py`

- **`INSTALLATION_INFO["name"]`**: `"CLIMA"` — debe coincidir con `default_installation` en el script de polilínea (mayúsculas).
- **`label`**: "Instalación de Clima" (texto visible).
- **Ángulos globales**: `[0, 14.42, -14.42, 90, 180, 270]`.
- **Capas** (`layers`): claves tipo `IS_CON_VENT_FAB`, `IS_CON_VENT_EIX`, etc. Los `default_layers` pueden quedar con espacio en blanco hasta configuración en proyecto.

### Tipos de instalación (`installation_types`)

Hay **dos entradas** con la misma clave técnica `tram_recte` y etiquetas distintas:

| Label     | Rol típico | Color | Mismo `key` |
|-----------|------------|-------|-------------|
| Impulsió  | Impulsión  | 19    | `tram_recte` |
| Retorn    | Retorno    | 5     | `tram_recte` |

Ambas:

- `is_individual`: **True** (un PythonPart por segmento en el flujo estándar PolyLib).
- Ángulos permitidos: **0°, ±14.42°, 90°, 180°, 270°** (en `allowed_angles`: `"0|14.42|-14.42|90|180|270"`).
- **Diámetro**: lista de secciones rectangulares en texto, p. ej. `"150x150"` … `"750x150"`.
- **Accesorios lógicos** (`elems`): `codo_90`, `conexion`.
- **Conexiones** (`ElementTypes`): codo, bifurcación, reducción.

### Elementos 3D registrados (`elements3D`)

Definidos con `create_element()` (genera `module_path` = `pyp-scripts.<key>_script` y clase `*Script` en PascalCase):

- **`tram_recte`** — dinámico (`dynamic=True`): `TramRecteScript` en `tram_recte_script.py`.
- **`colze`** — `ColzeScript` en `colze_script.py`.

`setup(import_base)` llama a `register_installation` y, de forma **explícita**, vuelve a registrar `tram_recte` y `colze` con `register_pythonpart` si el import falló en el registro genérico (evita que el catálogo quede vacío en caso de error silencioso).

---

## 4. Script principal — `pyp-scripts/clima_polyline.py`

### Configuración

- **`INST_NAME`**: `"CLIMA"`.
- **`PolylineBaseConfig`**:
  - `parameters_show` / `parameters_enabled`: perfil **`Clima`** (`Instalaciones.PolyLib.models.Clima`), que activa entre otros **diámetro en string** (`diameter_type_str`), distribución EN/IS/TD, nombre funcional, etc.
  - `num_td_path`: ruta del proyecto actual (para numeración / TD si la librería la usa).
  - `limit_angles` y `allowed_angles` acotan la orientación en planta.

En el código actual hay líneas que fuerzan visibilidad de **“Polilínea”** en el paleta (`add_polilyne`); el propio archivo indica que conviene **eliminarlas antes de entregar MVP**.

### Hooks

1. **`element_creation_preview_hook`** → `_create_elements_for_segment_group`  
   - Si el tipo activo es `tram_recte`, construye fábricas que llaman a `so._get_pythonpart_installed` con:
     - `element_key="tram_recte"` o `"colze"`,
     - `exec_kwargs`: `installation_type` = label del tipo (p. ej. `"Impulsió"` / `"Retorn"`), `diameter` = `so.diameter_type` o `"150x150"`.
   - Usa **`PipelineProcessor`** (`utils/geo_handler.py`) para encadenar tramos y codos, escalando BREP en el eje X local y orientando codos.
   - Caché interna por `(tipo, label, diámetro)` para no regenerar el mismo modelo en cada segmento.

2. **`element_creation_layer_attrs_hook`** → `_create_elements_with_layers_attrs`  
   - Implementación mínima: devuelve la lista sin modificar. Hay bloques **comentados** para fusión de atributos, numeración automática y capas (referencia para ampliar).

### Recarga en caliente

`check_allplan_version` recarga módulos `PolyLib` (útil en desarrollo).

---

## 5. `PipelineProcessor` y `geo_handler.py`

`PipelineProcessor` concentra la lógica de:

- Plantillas o **fábricas** (`conducto_factory`, `codo_factory`) por segmento.
- **Escalado longitudinal** del BREP (`modificar_dimensiones_brep`).
- Cálculo de **rotación de codos** respecto a una base (`obtener_rotacion_codo`, etc.).

`GeometryHandler` (misma carpeta) es una versión más genérica orientada a listas de ítems con tipos (`conducto`, `manguito`, `codo_90`, …); la polilínea Clima actual se apoya principalmente en `PipelineProcessor`.

---

## 6. GeometryTools en piezas sueltas

Los siguientes archivos importan **`CreateSmartGeo`** para construir o componer geometría:

- `conducto_3D.py`, `codo_90_3D.py`, `conexion_3D.py`, `difusor_3D.py`, `manguito_3D.py`

No todos están enlazados en `INSTALLATION_INFO["elements3D"]` del registro actual; sirven como **biblioteca de piezas** o para futuros `*_script.py` en catálogo.

---

## 7. Perfil PolyLib `Clima` (`PolyLib/models.py`)

La clase **`Clima(BaseInstallation)`** ajusta qué controles del `.pyp` se muestran y cuáles son editables, por ejemplo:

- Muestra: `diameter_type_str`, `distribution_type`, modos de dibujo, etc.
- Habilitados: nombre funcional, tipo de distribución, cara EN, creación de PythonPartGroup, `diameter_type_str`.

El registro `_REGISTRY` incluye `"CLIMA"` → perfil `Clima` para coherencia con otras instalaciones (Agua, Saneamiento, …).

---

## 8. Ficheros `.pyp` y `___pyp__`

- Definen la **paleta** (parámetros, expanders, modos de punto, layers, atributos, botón finalizar).
- **`Interactor`**: `False` en la definición actual (el interactor lo gestiona PolyLib según el script).
- Rutas de script en XML usan el prefijo `Instalaciones\Clima\...` coherente con el árbol bajo `GeneralScripts`.

---

## 9. Resumen de dependencias

```text
Clima (polilínea)
  ├── Instalaciones.PolyLib (script_object, interactor, models.Clima, registro vía polyline_reg_clima)
  ├── NemAll_Python_* (Geometría, BaseElements, BasisElements, …)
  └── utils.geo_handler.PipelineProcessor

Piezas *_3D.py / futuros scripts
  └── Instalaciones.GeometryTools.CreateSmartGeo
```

---

## 10. Ampliaciones habituales

- Registrar en `elements3D` nuevas claves y añadir `*_script.py` siguiendo el patrón de `create_element()`.
- Completar `_create_elements_with_layers_attrs` con atributos, capas y numeración (código de referencia ya comentado en `clima_polyline.py`).
- Ajustar `summary` en `INSTALLATION_INFO` si se añaden categorías de listado/informes.

---

*Documentación generada a partir del código en `GeneralScripts/Instalaciones` (Allplan 2025).*

---

## 11. Cambios funcionales aplicados hasta ahora (resumen operativo)

- **Limitador de ángulos (snap) en Clima**: los segmentos aceptan únicamente los valores configurados en `allowed_angles`: `0`, `+14.42`, `-14.42`, `90`, `180`, `270`.
- **Longitud mínima de segmento (Clima)**: se fijó **`min_segment_length = 600 mm`** para `Impulsió` y `Retorn` y el interactor **auto-estira** el punto en vez de mostrar el cuadro de confirmación.
- **Transformación `±14.42°` -> `Quiebro`**:
  - El interactor detecta el patrón de ángulo y (si procede) limita el largo máximo del segmento para que no deforme.
  - En el `PipelineProcessor` de `geo_handler.py` se detecta el segmento “quiebro” y se genera el PythonPart `Quiebro` (no se crean a la vez `tram_recte`/`codo_90` para esa posición).
  - Se añadió trazabilidad mediante `print` al detectar y generar `Quiebro`.
- **Límite máximo del segmento que genera `Quiebro`**:
  - `max_quiebro_segment_length` en `clima_polyline.py` y el clamp en `PolyLib/interactor.py` limitan el segmento asociado a `Quiebro` (valor actual: **`1000 mm`**).
  - En `Quiebro.py`, `MAX_LENGTH_MM` está en **`1000.0`** y el modelo internamente se restringe a `[MIN_LENGTH_MM, MAX_LENGTH_MM]`.
- **Bugfix del clamp afectando también al segmento siguiente**: en `PolyLib/interactor.py` se ajustó la validación para que el clamp se aplique al segmento correcto del patrón de `14.42°`, y **no** al segmento “recto siguiente” en la secuencia `recta -> 14.42° -> recta`.
- **El `Quiebro` no debe deformarse al cambiar la longitud**:
  - En `quiebro_script.py` se evita `model.set_length()` y se setea directamente `model.custom_length` y el parámetro `LONG. QUIEBRO` para no tocar anchuras internas (`LEN_X`/`ARM_LEN_X`).
- **Colocación y orientación del codo (`colze`)**:
  - La rotación horizontal (`yaw`) del `codo_90` depende de la dirección del giro (izquierda/derecha) mediante `get_colze_yaw_extra_deg(cross_z)` en `codo_placement_offsets.py`.
  - La traslación adicional por diámetro usa la tabla `COD0_TRANSLATION_MM_BY_DIAMETER` y la interpretación controlada por `COD0_TRANSLATION_SPACE` (valor actual: **`vertex`**, es decir, desplazamientos alineados con el tramo de entrada y el de salida en el plano + Z global).
- **Consistencia del snap en PolyLib**: se eliminaron listas hardcodeadas de ángulos y se normalizan contra la configuración (`normalize_angle_list(...)`) para que `Clima` no quede “pisada” por valores de otro instalador.
- **Registro del PythonPart `Quiebro`**: se reforzó el registro en runtime desde `clima_polyline.py` (para evitar problemas por cache del registry al no encontrar `QuiebroScript`).
- **Paleta completa de `Quiebro` parametrizada**:
  - `pyp-library/Quiebro.pyp` ahora expone bloques completos por tipo (**Retorn** / **Impulsió**) para editar geometría, flecha y datos.
  - `pyp-scripts/Quiebro.py` aplica esos valores de paleta en la generación real del modelo (no solo en UI), incluyendo longitud editable, caps, desfases y parámetros de flecha.
- **Control específico de diagonales laterales en `Quiebro`**:
  - Se añadieron parámetros de recorte en paleta para cada tipo: `CutBaseX`, `CutLengthY` y `CutOffsetX`.
  - Esos parámetros gobiernan directamente el triángulo de sustracción que genera las caras inclinadas laterales, permitiendo ajustar su apertura/inclinación sin tocar código.
  - Ajuste posterior: al reducir `CutLengthY`, el modelo ahora achica el quiebro completo manteniendo la inclinación de las diagonales (sin deformación por tramo vertical residual).
  - Ajuste posterior 2: el segundo recorte diagonal escala también su offset en X con la longitud, evitando cuñas interiores o diagonales cruzadas al acortar el quiebro.
  - Ajuste posterior 3: se añadieron logs de depuración para el cálculo de recortes diagonales (`[QUIEBRO][INIT]`, `[QUIEBRO][CUT]`, `[QUIEBRO][CUT2]`). Se activan con `QUIEBRO_DEBUG=1` (por defecto activo en esta fase de diagnóstico).
  - Ajuste posterior 4: el offset X del segundo recorte pasa a calcularse con anclaje al lateral derecho (`auto_tx_scaled`) + delta de usuario, para que al reducir `CutLengthY` no aparezcan cuñas interiores ni desplazamientos hacia el interior.
  - Ajuste posterior 5: al reducir `CutLengthY`, se compensa automáticamente el ancho X de las caps (`CAP_ARM_X_*`) con `cap_x_delta = base_raw - base_scaled` para mantener continuidad del contorno y eliminar el escalón residual (ejemplo típico: 25.7 mm en caso 900 mm).
  - Ajuste posterior 6 (cambio de enfoque): se eliminan las compensaciones geométricas en runtime y se normalizan directamente los datos de entrada (`CAP_ARM_X_BIGGEST`, `CAP_ARM_X_SMALLEST`, `CUT_OFFSET_X`) a valores consistentes antes de construir el sólido. Nuevo log: `[QUIEBRO][NORMALIZE]`.
  - Ajuste posterior 7: para evitar que el quiebro quede "muy ancho" al acortar, la normalización ya no modifica las caps; mantiene el ancho visual y corrige solo `CUT_BASE_X` + `CUT_OFFSET_X` para conservar continuidad y paralelismo de diagonales.

---

## 12. Valores actuales clave (para modificar si cambian las reglas)

Clima (polilínea):

- `allowed_angles`: `0, ±14.42, 90, 180, 270` (en `clima_polyline.py` y `polyline_reg_clima.py`).
- `min_segment_length`: `600 mm` para `Impulsió` y `Retorn`.
- `quiebro_angle_deg`: `14.42`.
- `quiebro_angle_tolerance_deg`: `0.8`.
- `max_quiebro_segment_length`: `1000 mm`.

Quiebro (pieza):

- `MIN_LENGTH_MM`: `200 mm`.
- `MAX_LENGTH_MM`: `1000 mm`.
- Longitud aplicada en `QuiebroScript` vía `model.custom_length` + `param["LONG. QUIEBRO"]` (evita deformación por `set_length()`).

Codo (`colze`):

- `COD0_TRANSLATION_SPACE`: `vertex`.
- `COLZE_YAW_EXTRA_GIRO_IZQUIERDA_DEG`: `270.0`.
- `COLZE_YAW_EXTRA_GIRO_DERECHA_DEG`: `90.0`.
