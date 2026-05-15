# Documentación Completa — Instalación de Clima (Allplan 2025 PythonParts)

> **Versión:** 1.0 · **Fecha:** 2026-05-04  
> **Ámbito:** `GeneralScripts/Instalaciones/Clima`  
> **Plataforma:** Allplan 2025 · Python 3.x

---

## Tabla de contenidos

1. [Descripción general](#1-descripción-general)
2. [Estructura de archivos](#2-estructura-de-archivos)
3. [Registro de instalación](#3-registro-de-instalación--polyline_reg_climapy)
4. [Tipos de distribución](#4-tipos-de-distribución)
5. [Elementos 3D registrados](#5-elementos-3d-registrados)
   - 5.1 [Tram Recte (tramo recto)](#51-tram-recte-tramo-recto)
   - 5.2 [Colze (codo 90°)](#52-colze-codo-90)
   - 5.3 [Quiebro (transición ±14.42°)](#53-quiebro-transición-1442)
   - 5.4 [Reduccions (reducción de sección)](#54-reduccions-reducción-de-sección)
6. [Script principal de polilínea](#6-script-principal-de-polilínea--clima_polylinepy)
7. [PipelineProcessor y geo_handler](#7-pipelineprocessor-y-geo_handlerpy)
8. [Perfil PolyLib Clima](#8-perfil-polylib-clima--polylibmodelspy)
9. [Parámetros del PythonPart (.pyp)](#9-parámetros-del-pythonpart-pyp)
10. [Reglas geométricas y constantes](#10-reglas-geométricas-y-constantes)
11. [Flujo de ejecución](#11-flujo-de-ejecución)
12. [Dependencias](#12-dependencias)
13. [Historial de cambios funcionales](#13-historial-de-cambios-funcionales)
14. [Guía de ampliación](#14-guía-de-ampliación)

---

## 1. Descripción general

La instalación de **Clima** es una de las cinco instalaciones MEP (junto con Agua, Saneamiento, Ventilación y Electricidad) del paquete `Instalaciones` para Allplan 2025.

Permite trazar recorridos de **climatización** mediante una polilínea 3D con giros en múltiplos de **90°** más una transición diagonal especial a **±14.42°**. A medida que el usuario dibuja, se genera geometría 3D de previsualización en tiempo real; al finalizar, los elementos se convierten en PythonParts completos con atributos y capas.

**Características principales:**

| Característica | Valor |
|---|---|
| Nombre interno | `CLIMA` |
| Tipos de distribución | Impulsió (impulsión) · Retorn (retorno) |
| Sección transversal | Rectangular: de 150×150 a 750×150 mm |
| Ángulos permitidos | 0°, ±14.42°, 90°, 180°, 270° |
| Longitud mínima de segmento | 600 mm |
| Piezas automáticas | Codo 90° (`colze`), Quiebro (`quiebro`) |
| Reducción automática | Sí, al cambiar diámetro |

---

## 2. Estructura de archivos

```
Instalaciones/
└── Clima/
    ├── DOCUMENTACION.md               ← Documentación interna original
    ├── DOCUMENTACION_COMPLETA.md      ← Este archivo
    ├── polyline_reg_clima.py          ← Registro de la instalación
    ├── pyp-library/
    │   ├── ___pyp__                   ← Definición XML principal de la paleta
    │   ├── clima_polyline.pyp         ← Parámetros del script de polilínea
    │   ├── clima_polylinebackup.pyp   ← Copia de respaldo
    │   ├── tram_recte.pyp             ← Parámetros del tramo recto
    │   ├── colze.pyp                  ← Parámetros del codo
    │   └── Quiebro.pyp                ← Parámetros del quiebro (paleta completa)
    └── pyp-scripts/
        ├── clima_polyline.py          ← Script principal (hooks de polilínea)
        ├── tram_recte_script.py       ← PythonPart: tramo recto
        ├── Tram_recte.py              ← Modelo/lógica del tramo recto
        ├── colze_script.py            ← PythonPart: codo 90°
        ├── colze.py                   ← Modelo/lógica del codo
        ├── quiebro_script.py          ← PythonPart: transición angular
        ├── quiebro2.py                ← Modelo/lógica del quiebro
        ├── Quiebro.py                 ← Modelo completo (paleta + geometría)
        ├── reduccions.py              ← PythonPart: reducción de sección
        ├── conducto_3D.py             ← Geometría de conducto (biblioteca)
        ├── codo_90_3D.py              ← Geometría de codo 90° (biblioteca)
        ├── conexion_3D.py             ← Geometría de conexión (biblioteca)
        ├── difusor_3D.py              ← Geometría de difusor (biblioteca)
        ├── manguito_3D.py             ← Geometría de manguito (biblioteca)
        └── utils/
            ├── geo_handler.py         ← PipelineProcessor + GeometryHandler
            ├── segments.py            ← Utilidades de segmentos
            └── codo_placement_offsets.py ← Cálculos de rotación y traslación de codos
```

---

## 3. Registro de instalación — `polyline_reg_clima.py`

Este módulo define el **objeto `INSTALLATION_INFO`** que PolyLib utiliza para registrar la instalación en el sistema.

### Metadatos

```python
INSTALLATION_INFO = {
    "name":   "CLIMA",                    # Identificador interno (mayúsculas)
    "label":  "Instalación de Clima",     # Texto visible en la UI
    "icon":   ...,                        # Ícono de la paleta
    "script": "Instalaciones/Clima/pyp-scripts/clima_polyline.py",
}
```

### Ángulos globales

```python
allowed_angles = [0, 14.42, -14.42, 90, 180, 270]
```

El interactor PolyLib hace **snap** automático al ángulo permitido más cercano.  
El valor especial `±14.42°` activa la pieza `Quiebro` en lugar del flujo `tram_recte + colze`.

### Capas

Las claves de capa siguen el patrón `IS_CON_VENT_*`. Los valores por defecto se configuran en el proyecto de Allplan:

| Clave | Descripción |
|---|---|
| `IS_CON_VENT_FAB` | Conducto de fábrica |
| `IS_CON_VENT_EIX` | Eje del conducto |
| `IS_CON_VENT_ACCES` | Accesorios |

### Función `setup(import_base)`

Llama a `register_installation` con el objeto `INSTALLATION_INFO` y, como salvaguarda ante posibles errores de caché del registro, vuelve a registrar explícitamente `tram_recte` y `colze` mediante `register_pythonpart`.

---

## 4. Tipos de distribución

Clima define **dos tipos de distribución**, ambos con la misma clave técnica `tram_recte`:

| Propiedad | Impulsió | Retorn |
|---|---|---|
| **Label** | `"Impulsió"` | `"Retorn"` |
| **Color Allplan** | 19 (claro) | 5 (oscuro) |
| **Clave técnica** | `tram_recte` | `tram_recte` |
| **`is_individual`** | `True` | `True` |
| **Diámetros** | 150×150 … 750×150 | 150×150 … 750×150 |
| **Accesorios** | `codo_90`, `conexion` | `codo_90`, `conexion` |

La distinción de color se usa para diferenciar visualmente el circuito de impulsión del de retorno en planta y sección.

### Lista completa de diámetros disponibles

```
150x150  200x150  250x150  300x150  350x150
400x150  450x150  500x150  550x150  600x150
650x150  700x150  750x150
```

Todos tienen sección rectangular con **altura fija de 150 mm** y ancho variable de 150 a 750 mm.

---

## 5. Elementos 3D registrados

### 5.1 Tram Recte (tramo recto)

**Clave:** `tram_recte` · **Tipo:** dinámico (`dynamic=True`)  
**Script:** `pyp-scripts/tram_recte_script.py` · **Clase:** `TramRecteScript`

Genera la geometría de un **segmento recto** del conducto. Su longitud se determina dinámicamente en función del segmento de la polilínea.

#### Parámetros geométricos (tabla `PARAMS_BASE` — extracto)

| Diámetro | `LEN_X` (mm) | `HEIGHT` (mm) | `CAP_ARM_X` (mm) | `CAP_ARM_Y` (mm) | `CAP_HEIGHT` (mm) |
|---|---|---|---|---|---|
| 150×150 | 200 | 200 | 200 | 25 | 199 |
| 300×150 | 350 | 200 | 350 | 25 | 199 |
| 500×150 | 550 | 200 | 550 | 25 | 199 |
| 750×150 | 800 | 200 | 800 | 25 | 199 |

*(13 diámetros totales, cada uno con ~10 parámetros geométricos)*

#### Atributos de salida

| Atributo | Descripción | Ejemplo |
|---|---|---|
| `ALT` | Altura de la sección | `"150"` |
| `AMPLE` | Anchura de la sección | `"300"` |
| `LENGTH` | Longitud del tramo | valor dinámico |
| `TYPE` | Tipo de pieza | `"TRAM RECTE"` |
| `WARNING` | Estado de validación | `"OK"` |
| `PART_NUMBER` | Número de pieza | generado automáticamente |

#### Escalado BREP

El `PipelineProcessor` escala el BREP del tramo recto longitudinalmente en el eje X local mediante `modificar_dimensiones_brep()`, de forma que un único modelo de catálogo sirve para cualquier longitud sin distorsionar la sección.

---

### 5.2 Colze (codo 90°)

**Clave:** `colze` · **Tipo:** estático  
**Script:** `pyp-scripts/colze_script.py` · **Clase:** `ColzeScript`

Generado automáticamente cada vez que la polilínea dobla **90°**. La geometría procede de presets de catálogo (`SIZE_PRESETS`), uno por cada diámetro.

#### Presets de tamaño (`SIZE_PRESETS` — extracto)

| Diámetro | `LEFT_VERTICAL` (m) | `TOP_HORIZONTAL` (m) | `LEFT_DIAG_45` (m) | `RIGHT_VERTICAL` (m) |
|---|---|---|---|---|
| 150×150 | 0.157 | 0.157 | 0.2859 | 0.200 |
| 300×150 | 0.307 | 0.307 | 0.4723 | 0.350 |
| 500×150 | 0.507 | 0.507 | 0.7330 | 0.550 |
| 750×150 | 0.757 | 0.757 | 1.0606 | 0.800 |

#### Rotación y traslación automáticas

La orientación del codo se calcula en `codo_placement_offsets.py`:

| Dirección de giro | `COLZE_YAW_EXTRA` |
|---|---|
| Giro a la izquierda | 270.0° |
| Giro a la derecha | 90.0° |

La traslación adicional depende del diámetro y se extrae de la tabla `COD0_TRANSLATION_MM_BY_DIAMETER`. El espacio de traslación es `vertex` (alineado con los tramos de entrada/salida en el plano + Z global).

---

### 5.3 Quiebro (transición ±14.42°)

**Clave:** `quiebro` · **Tipo:** estático  
**Scripts:** `pyp-scripts/quiebro_script.py` · `pyp-scripts/Quiebro.py`  
**Clase:** `QuiebroScript`

Pieza especial generada cuando un segmento tiene un ángulo de aproximadamente **±14.42°** (tolerancia: ±0.8°). Produce una transición diagonal suave entre dos tramos rectos.

#### Dimensiones

| Parámetro | Valor |
|---|---|
| `MIN_LENGTH_MM` | 200 mm |
| `MAX_LENGTH_MM` | 1000 mm |
| Ángulo de activación | 14.42° |
| Tolerancia de detección | ±0.8° |

#### Parámetros de geometría (paleta `Quiebro.pyp`)

Expone dos bloques según tipo (**Retorn** / **Impulsió**):

| Parámetro | Descripción |
|---|---|
| `LONG. QUIEBRO` | Longitud total editable del quiebro |
| `CUT_BASE_X` | Ancho de la base del corte diagonal |
| `CUT_LENGTH_Y` | Profundidad del corte diagonal |
| `CUT_OFFSET_X` | Desplazamiento del segundo corte |
| `CAP_ARM_X_BIGGEST` | Ancho de la tapa mayor |
| `CAP_ARM_X_SMALLEST` | Ancho de la tapa menor |

#### Reglas de normalización

Antes de construir el sólido, el script normaliza los valores de entrada para garantizar continuidad del contorno y paralelismo de las diagonales:

1. `CUT_BASE_X` y `CUT_OFFSET_X` se corrigen para mantener la apertura proporcional a la longitud.
2. Los valores de caps (`CAP_ARM_X_*`) no se modifican para conservar el ancho visual.
3. Los recortes diagonales escalan su offset X con la longitud (`auto_tx_scaled`), evitando cuñas interiores al acortar el quiebro.

#### Asignación de longitud (sin deformación)

```python
# CORRECTO: sin distorsionar anchuras internas
model.custom_length = longitud_calculada
params["LONG. QUIEBRO"] = longitud_calculada

# INCORRECTO (no usar):
# model.set_length(longitud_calculada)  ← modifica LEN_X/ARM_LEN_X
```

#### Logs de depuración

Activar con la variable de entorno `QUIEBRO_DEBUG=1`:

```
[QUIEBRO][INIT]      → valores de entrada
[QUIEBRO][NORMALIZE] → correcciones aplicadas
[QUIEBRO][CUT]       → datos del primer recorte
[QUIEBRO][CUT2]      → datos del segundo recorte
```

---

### 5.4 Reduccions (reducción de sección)

**Clave:** `reduccions`  
**Script:** `pyp-scripts/reduccions.py`

Insertada automáticamente cuando cambia el diámetro entre dos segmentos consecutivos. No requiere intervención manual del usuario.

---

## 6. Script principal de polilínea — `clima_polyline.py`

Punto de entrada que Allplan carga como PythonPart de polilínea. Implementa los dos hooks del motor PolyLib.

### Configuración base

```python
INST_NAME = "CLIMA"

config = PolylineBaseConfig(
    parameters_show    = Clima.Show(),
    parameters_enabled = Clima.Enabled(),
    num_td_path        = "<ruta_proyecto_actual>",
    limit_angles       = True,
    allowed_angles     = [0, 14.42, -14.42, 90, 180, 270],
)
```

### Hook 1 — Previsualización en tiempo real

```python
def element_creation_preview_hook(segments, so) -> list[GeneratedElement]:
    ...
```

**Cuándo se invoca:** al cambiar de modo, guardar un segmento, mover/eliminar un vértice o cambiar el tipo de instalación.

**Qué hace:**

1. Para cada grupo de segmentos del tipo `tram_recte`:
   - Crea una factoría de tramos (`conducto_factory`) llamando a `so._get_pythonpart_installed` con `element_key="tram_recte"`.
   - Crea una factoría de codos (`codo_factory`) con `element_key="colze"`.
   - Detecta segmentos de 14.42° y sustituye ambas fábricas por la del `Quiebro`.
2. Pasa las fábricas al `PipelineProcessor`, que ensambla la geometría completa del recorrido.
3. Devuelve `list[GeneratedElement]` con elemento 3D, índice y tipo.

**Caché interna:** por `(tipo, label, diámetro)` para no regenerar el mismo modelo en cada frame.

### Hook 2 — Finalización con capas y atributos

```python
def element_creation_layer_attrs_hook(elements_generated, path_idx, so) -> list[GeneratedElement]:
    ...
```

**Cuándo se invoca:** cuando el usuario guarda/finaliza la polilínea.

**Qué hace (implementación actual):** devuelve la lista sin modificar.  
**Implementación futura (código de referencia comentado en el archivo):** fusión de atributos, numeración automática y asignación de capas por tipo de elemento.

### Recarga en caliente (desarrollo)

```python
check_allplan_version()  # recarga módulos PolyLib sin reiniciar Allplan
```

---

## 7. PipelineProcessor y `geo_handler.py`

Módulo `pyp-scripts/utils/geo_handler.py`. Concentra la lógica de ensamblaje 3D de la instalación.

### Clase `PipelineProcessor`

| Método | Descripción |
|---|---|
| `set_conducto_factory(factory)` | Registra la factoría de tramos rectos |
| `set_codo_factory(factory)` | Registra la factoría de codos |
| `process(segments)` | Recorre los segmentos y genera la geometría completa |
| `modificar_dimensiones_brep(brep, length)` | Escala el BREP en el eje longitudinal |
| `obtener_rotacion_codo(seg_in, seg_out)` | Calcula la rotación del codo según los vectores de entrada/salida |
| `get_colze_yaw_extra_deg(cross_z)` | Devuelve el yaw adicional según el sentido del giro |

### Clase `GeometryHandler`

Versión más genérica, orientada a listas de ítems con tipos (`conducto`, `manguito`, `codo_90`, …). La polilínea Clima activa usa principalmente `PipelineProcessor`.

### Tabla de traslación de codos (`COD0_TRANSLATION_MM_BY_DIAMETER`)

Almacenada en `codo_placement_offsets.py`. Define el desplazamiento adicional (mm) que se aplica al posicionar el codo según el diámetro del conducto, para garantizar la continuidad geométrica con los tramos adyacentes.

```python
COD0_TRANSLATION_MM_BY_DIAMETER = {
    "150x150": (...),
    "300x150": (...),
    "500x150": (...),
    # ...
}
COD0_TRANSLATION_SPACE = "vertex"
```

---

## 8. Perfil PolyLib Clima — `PolyLib/models.py`

La clase `Clima(BaseInstallation)` controla qué parámetros de la paleta se muestran y cuáles son editables.

### Controles visibles (`Clima.Show`)

| Control | Visible |
|---|---|
| `draw_mode_insert` | ✓ |
| `distribution_type` | ✓ |
| `diameter_type_str` | ✓ |
| `diameter_modify` | ✓ |

### Controles habilitados (`Clima.Enabled`)

| Control | Editable |
|---|---|
| `functional_name` | ✓ |
| `distribution_type` | ✓ |
| `create_python_part` | ✓ |
| `diameter_type_str` | ✓ |
| `diameter_modify` | ✓ |

### Registro global

```python
_REGISTRY = {
    "CLIMA":      Clima,
    "AGUA":       Agua,
    "VENTILACION": Ventilacion,
    "ELECTRICIDAD": Electricidad,
    "SANEAMIENTO": Saneamiento,
    "SOPORTES":   Soportes,
}
```

---

## 9. Parámetros del PythonPart (.pyp)

### `clima_polyline.pyp` — Paleta principal

| Sección | Parámetros clave |
|---|---|
| **Instalación** | Tipo de distribución, Diámetro (string), Cara EN |
| **Modos de dibujo** | Punto de inserción, Corte de inserción, Caja de información |
| **Capas** | Selector de tipo, Botón aplicar capa |
| **Atributos** | Campo de valor, Botón aplicar |
| **General** | Crear PythonPartGroup, Añadir polilínea, Nombre funcional |
| **Acciones** | Eliminar segmento, Finalizar |

### `tram_recte.pyp` — Tramo recto

Expone todos los parámetros geométricos de `PARAMS_BASE` organizados por diámetro, más los atributos `ALT`, `AMPLE`, `TYPE`, `WARNING`, `PART_NUMBER`.

### `colze.pyp` — Codo 90°

Expone los 13 presets de tamaño con sus dimensiones geométricas (`LEFT_VERTICAL`, `TOP_HORIZONTAL`, `LEFT_DIAG_45`, etc.).

### `Quiebro.pyp` — Transición angular

Bloques diferenciados por tipo (**Retorn** / **Impulsió**) con:
- Longitud editable (`LONG. QUIEBRO`)
- Parámetros de corte diagonal (`CUT_BASE_X`, `CUT_LENGTH_Y`, `CUT_OFFSET_X`)
- Tamaños de tapa (`CAP_ARM_X_BIGGEST`, `CAP_ARM_X_SMALLEST`)
- Parámetros de flecha y desfases

---

## 10. Reglas geométricas y constantes

### Polilínea Clima

| Constante | Valor | Dónde se define |
|---|---|---|
| `INST_NAME` | `"CLIMA"` | `clima_polyline.py` |
| `allowed_angles` | `[0, ±14.42, 90, 180, 270]` | `clima_polyline.py` · `polyline_reg_clima.py` |
| `min_segment_length` | **600 mm** | `polyline_reg_clima.py` |
| `quiebro_angle_deg` | **14.42°** | `clima_polyline.py` |
| `quiebro_angle_tolerance_deg` | **±0.8°** | `clima_polyline.py` |
| `max_quiebro_segment_length` | **1000 mm** | `clima_polyline.py` · `PolyLib/interactor.py` |

### Pieza Quiebro

| Constante | Valor | Dónde se define |
|---|---|---|
| `MIN_LENGTH_MM` | **200 mm** | `Quiebro.py` |
| `MAX_LENGTH_MM` | **1000 mm** | `Quiebro.py` |

### Codo Colze

| Constante | Valor | Dónde se define |
|---|---|---|
| `COD0_TRANSLATION_SPACE` | `"vertex"` | `codo_placement_offsets.py` |
| `COLZE_YAW_EXTRA_GIRO_IZQUIERDA_DEG` | `270.0°` | `codo_placement_offsets.py` |
| `COLZE_YAW_EXTRA_GIRO_DERECHA_DEG` | `90.0°` | `codo_placement_offsets.py` |

### Restricción de ángulo interior

El interactor PolyLib rechaza cualquier segmento que forme un ángulo interior inferior a **45°** con el segmento anterior (restricción global de todas las instalaciones).

---

## 11. Flujo de ejecución

```
Usuario dibuja vértice
        │
        ▼
PolyLib Interactor
  ├─ Snap al ángulo permitido más cercano
  ├─ Valida longitud mínima (≥ 600 mm)
  │    └─ Si es menor: auto-estira el punto (no muestra diálogo)
  ├─ Detecta segmento de 14.42°
  │    └─ Limita longitud máxima a 1000 mm
  └─ Llama element_creation_preview_hook()
              │
              ▼
       clima_polyline.py
         _create_elements_for_segment_group()
           │
           ├─ Segmento recto → tram_recte + colze (si hay giro)
           │     └─ PipelineProcessor
           │           ├─ modificar_dimensiones_brep() → escala longitud
           │           ├─ obtener_rotacion_codo()      → orienta codo
           │           └─ Traslación por diámetro (COD0_TRANSLATION_MM_BY_DIAMETER)
           │
           └─ Segmento ≈ 14.42° → Quiebro
                 └─ QuiebroScript
                       ├─ Normaliza parámetros de corte
                       ├─ model.custom_length = longitud_calculada
                       └─ Construye sólido con recortes diagonales
              │
              ▼
       GeneratedElement (geometría 3D previsualizada)

Usuario finaliza polilínea
        │
        ▼
element_creation_layer_attrs_hook()
  └─ (futuro) aplica atributos, capas y numeración
        │
        ▼
PythonPartGroup creado en Allplan
```

---

## 12. Dependencias

```
Clima (polilínea)
├── Instalaciones.PolyLib
│   ├── script_object.PolylineScriptObject   ← gestión de polilínea
│   ├── interactor.Interactor                ← interacción de usuario
│   ├── models.Clima                         ← perfil de parámetros
│   └── installation_registry               ← registro de la instalación
├── Instalaciones.Clima.pyp-scripts.utils
│   ├── geo_handler.PipelineProcessor        ← ensamblaje 3D
│   └── codo_placement_offsets               ← rotación/traslación de codos
└── NemAll_Python_*
    ├── NemAll_Python_Geometry               ← tipos geométricos
    ├── NemAll_Python_BaseElements           ← elementos base
    └── NemAll_Python_BasisElements          ← BREP, sólidos

Piezas *_3D.py y futuros *_script.py
└── Instalaciones.GeometryTools.CreateSmartGeo
    ├── cilindros, cuboides                  ← primitivas
    └── operaciones booleanas                ← unión, sustracción
```

---

## 13. Historial de cambios funcionales

| # | Cambio | Archivo(s) afectado(s) |
|---|---|---|
| 1 | Snap de ángulos: solo acepta valores de `allowed_angles`; eliminadas listas hardcodeadas | `PolyLib/interactor.py` · `clima_polyline.py` |
| 2 | Longitud mínima 600 mm con auto-estiramiento (sin diálogo) | `polyline_reg_clima.py` · `PolyLib/interactor.py` |
| 3 | Detección y generación del `Quiebro` para segmentos ≈ ±14.42° | `clima_polyline.py` · `geo_handler.py` |
| 4 | Límite máximo del segmento Quiebro: 1000 mm | `clima_polyline.py` · `PolyLib/interactor.py` |
| 5 | Bugfix: el clamp de 1000 mm no afecta al segmento recto siguiente | `PolyLib/interactor.py` |
| 6 | Longitud del Quiebro vía `model.custom_length` (sin distorsionar sección) | `quiebro_script.py` · `Quiebro.py` |
| 7 | Rotación del codo (`yaw`) según sentido de giro (izq/der) | `codo_placement_offsets.py` · `geo_handler.py` |
| 8 | Traslación del codo por tabla `COD0_TRANSLATION_MM_BY_DIAMETER`, espacio `vertex` | `codo_placement_offsets.py` |
| 9 | Registro reforzado del Quiebro en runtime desde `clima_polyline.py` | `clima_polyline.py` |
| 10 | Paleta `Quiebro.pyp` con bloques Retorn/Impulsió y parámetros de corte diagonal | `pyp-library/Quiebro.pyp` · `Quiebro.py` |
| 11 | Parámetros `CUT_BASE_X`, `CUT_LENGTH_Y`, `CUT_OFFSET_X` controlan las diagonales desde paleta | `Quiebro.py` |
| 12 | Offset X del 2.º recorte anclado al lateral derecho (`auto_tx_scaled`) | `Quiebro.py` |
| 13 | Normalización de entradas antes de construir el sólido (sin tocar caps) | `Quiebro.py` |
| 14 | Logs de depuración del Quiebro activables con `QUIEBRO_DEBUG=1` | `Quiebro.py` |

---

## 14. Guía de ampliación

### Añadir un nuevo elemento 3D

1. Crear `pyp-scripts/<nombre>_script.py` con una clase `<Nombre>Script` que implemente el método `execute()`.
2. Registrar en `polyline_reg_clima.py`:

```python
from Instalaciones.PolyLib.installation_registry import create_element

elements3D = [
    create_element("tram_recte", "Tram Recte", dynamic=True),
    create_element("colze",      "Colze"),
    create_element("nuevo_elem", "Nombre visible"),   # ← añadir aquí
]
```

3. Crear el archivo `.pyp` correspondiente en `pyp-library/`.
4. Invocar la factoría del nuevo elemento desde `element_creation_preview_hook` en `clima_polyline.py`.

### Completar atributos y capas

Descomentar y adaptar el bloque de referencia al final de `element_creation_layer_attrs_hook` en `clima_polyline.py`. El bloque incluye:

- Fusión de atributos por tipo de elemento.
- Numeración automática correlativa.
- Asignación de capa según clave `IS_CON_VENT_*`.

### Añadir un nuevo diámetro

1. Añadir la clave string (p. ej. `"800x150"`) a la lista `diameters` en `polyline_reg_clima.py`.
2. Añadir la entrada correspondiente en `PARAMS_BASE` de `tram_recte_script.py`.
3. Añadir el preset en `SIZE_PRESETS` de `colze_script.py`.
4. Añadir la entrada en `COD0_TRANSLATION_MM_BY_DIAMETER` de `codo_placement_offsets.py`.

### Cambiar la longitud mínima de segmento

Modificar el parámetro `min_segment_length` en `polyline_reg_clima.py`:

```python
installation_types = [
    InstallationType(
        key="tram_recte",
        label="Impulsió",
        min_segment_length=600,   # ← cambiar aquí (mm)
        ...
    ),
]
```

El interactor PolyLib lee este valor automáticamente.

### Cambiar el ángulo del Quiebro

Actualizar en `clima_polyline.py`:

```python
quiebro_angle_deg       = 14.42   # ángulo de activación
quiebro_angle_tolerance_deg = 0.8 # tolerancia ±
```

Y en `polyline_reg_clima.py`:

```python
allowed_angles = [0, 14.42, -14.42, 90, 180, 270]
```

---

*Documentación generada a partir del análisis del código fuente en `GeneralScripts/Instalaciones` (Allplan 2025) — 2026-05-04.*
