# Integración de elementos definidos (T sortida, Colze base, Clau de Pas, Tapón)

**Guía rápida para compañeros**: Ver **[GUIA_USO_ELEMENTOS_DEFINIDOS.md](GUIA_USO_ELEMENTOS_DEFINIDOS.md)** (paso a paso, configuración, problemas habituales).

---

## 1. Módulo ElementosDefinidos

- **base.py**: Clases `BaseDefinedElement` y `BaseMacroElement` con:
  - `nombre`, `posibles_funciones`, `funcion_defecto`
  - `posicion`, `funcion_seleccionada`, `rotacion`, `id_camino`, `orden_en_camino`
  - Métodos: `generate_preview()`, `generate_final_3d()`, `can_be_used_in_role()`
  - `POSIBLES_FUNCIONES`, `FUNCION_TO_ROLE`
- **catalogo.py**: Por instalación (Agua, Electricidad):
  - Qué elementos existen y en qué funciones pueden ir (inicio, final, intermedio_ordenado, intermedio_libre, bifurcación).
  - Condiciones por defecto y validación `validar_ubicacion_elemento()`.
  - `get_value_list_elementos(instalacion)` para el ComboBox de elemento.
  - `get_value_list_tipo_punto(instalacion, element_label_or_key)` para el ComboBox de tipo de punto (opciones según elemento).
  - `label_a_key_agua(label)`, `label_tipo_punto_to_funcion(label)` para convertir valores de UI a keys/funciones internas.
  - `LABELS_AGUA`, `LABELS_FUNCION` (etiquetas para UI).
- **capture.py**: `ElementPointCaptureMixin` para captura de punto libre y añadido de marcadores usando el catálogo.

## 2. Código del compañero que debes usar

### PolylineLib
- **install.py**: `register_installation()`, `get_elements_for(instalacion)`, `get_pythonpart(key)` — registro de instalaciones y elementos 3D con roles.
- **constants.py**: `ROLE_LABEL` (0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final) — coincide con las funciones inicio/final/intermedio/bifurcación.
- **models.py**: `Capture3D` con `role`, `element_key`, `element_label`, `installation` — modelo de punto con elemento asignado.
- **interactor.py**: `PolylineInteractor` — captura de polilínea, `element_markers` para marcadores de elementos definidos, eventos 1015 (Seleccionar punto) y 1016 (Agregar elemento).

### Electricidad
- **polyline_register.py**: Ejemplo de registro de instalación con `elements3D` y `roles: [0, 3]` (inicio/final).
- **_polyline/polyline_test.py**: Uso de `PolylineInteractor` y paleta con `DefinedElementType` y `ElementPointMode`.

### GeometryTools
- **CreateSmartGeo** (create_smart_geo): Utilidades de geometría si en tu flujo necesitas cálculos geométricos para colocar elementos.

## 3. Integración de entrada de puntos en la polilínea

La lógica ya está en **Agua/fontaneria.py** (y en el script de puntos del compañero en Electricidad). Para unificar con el módulo ElementosDefinidos:

### UI (paleta)
- **Pestaña "Dibujar polilínea"**  
  - Elemento (`DefinedElementType`), Posición (`ElementPointMode`: 0=Inicio, 1=Final, 2=Intermedio).  
  - Botones:
    - 1015 (Seleccionar punto para elemento definido) → `start_element_point_capture()` / `ElementPointCaptureMixin.start_element_point_capture`.
    - 1016 (Agregar elemento definido) → `add_defined_element_marker()` / `_add_defined_element_marker`.
    - 1013 (Seleccionar punto para macro) → `start_macro_point_capture()` (wrapper en `ElementosDefinidos` sobre `PolylineInteractor.start_macro_point_capture`).
    - 1014 (Agregar macro en inicio/final/libre) → `add_macro_library_marker()` (wrapper en `ElementosDefinidos` sobre `PolylineInteractor._add_macro_library_marker`).

- **Pestaña "Modo puntos libres"**  
  - Orden recomendado:
    1. ComboBox **Elemento** (`DefinedElementType`).
    2. ComboBox **Tipo de punto** (`TipoPuntoLibre`) con ValueList condicional según elemento (p. ej. T sortida/Clau de Pas → `"Intermedio ordenado|Intermedio libre"`; Colze base/Tapón → `"Inicio|Final"`).
    3. Botón **Añadir punto** (EventId 1017) → `on_anadir_punto_libre(...)`.
    4. Botón **Finalizar** (EventId 1018) → `on_finalizar_puntos_libres(...)`.
  - Para el ComboBox tipo de punto se puede usar `get_value_list_tipo_punto("AGUA", element_label)` o una expresión condicional en el `.pyp`.

#### 3.2.1 Ejemplos mínimos de fragmentos `.pyp` (para copiar/pegar)

**ComboBox de elemento (pestaña Dibujar polilínea o Modo puntos libres):**

```xml
<Parameter>
  <Name>DefinedElementType</Name>
  <ValueType>StringComboBox</ValueType>
  <ValueList>
T sortida|Colze base|Clau de Pas|Taps
  </ValueList>
  <DefaultValue>Colze base</DefaultValue>
</Parameter>
```

**ComboBox de tipo de punto (pestaña Modo puntos libres, con ValueList condicional):**

```xml
<Parameter>
  <Name>TipoPuntoLibre</Name>
  <ValueType>StringComboBox</ValueType>
  <ValueList>
if DefinedElementType in ("T sortida", "Clau de Pas"):
    return "Intermedio ordenado|Intermedio libre"
else:
    return "Inicio|Final"
  </ValueList>
  <DefaultValue>Intermedio libre</DefaultValue>
</Parameter>
```

**Botones para eventos (ejemplo):**

```xml
<!-- Pestaña Dibujar polilínea -->
<Parameter>
  <Name>SeleccionarPuntoElementoDefinido</Name>
  <ValueType>Button</ValueType>
  <EventId>1015</EventId>
  <Text>Seleccionar punto</Text>
</Parameter>

<Parameter>
  <Name>AgregarElementoDefinido</Name>
  <ValueType>Button</ValueType>
  <EventId>1016</EventId>
  <Text>Agregar elemento</Text>
</Parameter>

<!-- Pestaña Modo puntos libres -->
<Parameter>
  <Name>AnadirPuntoLibre</Name>
  <ValueType>Button</ValueType>
  <EventId>1017</EventId>
  <Text>Añadir punto</Text>
</Parameter>

<Parameter>
  <Name>FinalizarPuntosLibres</Name>
  <ValueType>Button</ValueType>
  <EventId>1018</EventId>
  <Text>Finalizar</Text>
</Parameter>
```

Estos fragmentos son una base genérica; cada equipo puede ajustar nombres de parámetros, textos y pestañas, manteniendo **los mismos `EventId` y `ValueType`** para que las funciones del módulo `ElementosDefinidos` funcionen sin cambios.

### Restricciones (catálogo Agua; centralizadas en catalogo.py)
- **T sortida**: solo **intermedio** (intermedio_ordenado, intermedio_libre).
- **Clau de Pas**: solo **intermedio** (intermedio_ordenado, intermedio_libre).
- **Colze base**: solo **inicio** o **final**.
- **Tapón**: solo **inicio** o **final**.

Al añadir marcador, llamar a `validar_ubicacion_elemento(instalacion, element_key, funcion_seleccionada)` antes de añadir a `element_markers`.

### Marcadores y generación final
- **element_markers** (modo polilínea): cada marcador tiene `kind` (start/end/free), `pos` (Point3D), `radius`, `element_type` (t_sortida, colze_base, clau_de_pas, taps), `path_idx`, `pt_idx`. En “Finalizar y crear” (1003) se recorren y se crean los 3D.
- **free_placed_points** (modo puntos libres): lista de diccionarios con `pos`, `flag` (inicio/final/intermedio_ordenado/intermedio_libre), `element_type`, `order`. Al pulsar **Finalizar** (1018) se llama a `_create_elements_from_free_placed_points()`: se crean los 3D en cada posición y se vacía la lista. Los `element_type` deben coincidir con las keys del catálogo (t_sortida, colze_base, clau_de_pas, taps).  
  En la implementación actual de **Agua/fontaneria**, la **previsualización** de estos puntos libres usa ya el **mismo model_list 3D** que se crea al finalizar (no iconos 2D), y se aplica opcionalmente una matriz de rotación a partir de parámetros de paleta (`RotX`, `RotY`, `RotZ`) antes de trasladar al punto.

## 4. Resumen de archivos de Agua para elementos definidos

| Elemento    | PythonPart (Agua/TD)   | Creación en documento              |
|------------|------------------------|------------------------------------|
| T sortida  | Te_Sortida_004.py      | TeSortidaCreateElement(build_ele, doc) |
| Colze base | Colze_Base_002.py      | ColzeBaseCreateElement(build_ele, doc) |
| Clau de Pas| Clau_de_Pas_006.py     | ClauDePasCreateElement(build_ele, doc)  |
| Tapón      | Taps_010.py            | TapsCreateElement(build_ele, doc)      |

## 5. Uso de ElementosDefinidos en fontaneria (opcional)

- Sustituir la lógica dispersa de `_get_defined_element_settings()` por la key obtenida con `label_a_key_agua(build_ele.DefinedElementType.value)`.
- Sustituir las comprobaciones “solo inicio/final” y “solo intermedio” por `validar_ubicacion_elemento("AGUA", element_key, funcion_seleccionada)`.
- Opcionalmente rellenar el ValueList de `DefinedElementType` en `initialize_control_properties` con `get_value_list_elementos("AGUA")` para mantener una sola fuente de verdad (catálogo).

## 6. Captura de punto libre y marcadores (capture.py)

La lógica de captura de punto libre y de agregado de marcadores de elementos definidos está en el módulo **ElementosDefinidos** mediante el mixin `ElementPointCaptureMixin` (archivo `capture.py`). En **fontaneria** el flujo “modo puntos libres” está implementado directamente en el script (no usando el mixin), pero la validación y el catálogo son los mismos.

### Uso del mixin (opcional)

- Heredar de `ElementPointCaptureMixin` y del interactor (p. ej. `PolylineInteractor`), con el mixin **antes** del interactor:
  ```python
  from ElementosDefinidos import ElementPointCaptureMixin
  from PolylineLib.interactor import PolylineInteractor

  class MiInteractor(ElementPointCaptureMixin, PolylineInteractor):
      instalacion = "AGUA"
  ```
- Definir **instalacion** para que el mixin use el catálogo y `validar_ubicacion_elemento`.

### Eventos (referencia fontaneria / PolylineLib)

- **1013** (pestaña Dibujar polilínea, macros):  
  - `start_macro_point_capture(intr)` (desde `ElementosDefinidos`) → modo “siguiente clic = punto libre para macro”.
- **1014** (pestaña Dibujar polilínea, macros):  
  - `add_macro_library_marker(intr)` (desde `ElementosDefinidos`) → añadir marcador de macro a `macro_markers` (se materializa en el `PythonPartGroup` final).
- **1015** (pestaña Dibujar polilínea, elementos definidos):  
  - `start_element_point_capture()` — modo “siguiente clic = punto para elemento intermedio”.
- **1016** (pestaña Dibujar polilínea, elementos definidos):  
  - `add_defined_element_marker()` / `_add_defined_element_marker()` — añadir marcador a `element_markers`.
- **1017** (pestaña Modo puntos libres):  
  - Activar “siguiente clic = añadir punto libre” por medio de `on_anadir_punto_libre(...)`; la previsualización del elemento sigue al cursor.
- **1018** (pestaña Modo puntos libres):  
  - `on_finalizar_puntos_libres(...)` → crear elementos 3D en cada punto libre (vía `create_elements_from_free_placed_points`) y vaciar la lista.

### Requisitos del host (mixin)

- **Estado**: `element_markers` (lista de marcadores).
- **Paleta**: `build_ele` con `DefinedElementType`, `ElementPointMode` (o `TipoPuntoLibre` en modo puntos libres), `ElementRadius`, `ElementZAbs`.
- **Interacción**: `coord_input`, `_set_prompt()`, `_draw_preview()`, `_save_state_to_build_ele()`.

Para **modo puntos libres** sin mixin (como en fontaneria): el script mantiene `free_placed_points` en el script object, lee `TipoPuntoLibre` para el tipo de punto, y en preview dibuja los **propios elementos 3D** de cada tipo (model_list devuelto por los PythonParts Colze/T/Clau/Taps) en las posiciones de `free_placed_points` y bajo el cursor mientras se espera el clic.  
Adicionalmente, fontaneria aplica una matriz de rotación (`Matrix3D`) construida a partir de ángulos en la paleta (`RotX`, `RotY`, `RotZ` en la pestaña “Modo puntos libres”), de forma que la orientación que se ve en preview coincide con la orientación final.
