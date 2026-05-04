# Guía de uso: Módulo ElementosDefinidos

Esta guía explica **qué es** el módulo ElementosDefinidos, **para qué sirve**, **cómo usarlo** en sus scripts y **cómo configurarlo** (catálogo, paleta, eventos). Está pensada para que cualquier compañero pueda integrar elementos definidos (T sortida, Colze base, Clau de Pas, Tapón, etc.) en sus PythonParts sin duplicar lógica.

---

## Índice

1. [¿Qué es el módulo ElementosDefinidos?](#1-qué-es-el-módulo-elementosdefinidos)
2. [Estructura del módulo](#2-estructura-del-módulo)
3. [Conceptos clave](#3-conceptos-clave)
4. [Uso rápido: leer el catálogo desde un script](#4-uso-rápido-leer-el-catálogo-desde-un-script)
5. [Integración completa: paleta + eventos + flujo](#5-integración-completa-paleta--eventos--flujo)
6. [Modo puntos libres (paso a paso)](#6-modo-puntos-libres-paso-a-paso)
7. [Modo polilínea (elementos en inicio/final/intermedio)](#7-modo-polilínea-elementos-en-iniciofinalintermedio)
8. [Integración de macros sobre polilínea](#8-integración-de-macros-sobre-polilínea)
9. [Configurar el catálogo (añadir instalación o elemento)](#9-configurar-el-catálogo-añadir-instalación-o-elemento)
10. [Configurar la paleta (.pyp)](#10-configurar-la-paleta-pyp)
11. [Resumen de eventos y parámetros](#11-resumen-de-eventos-y-parámetros)
12. [Preguntas frecuentes y problemas habituales](#12-preguntas-frecuentes-y-problemas-habituales)

---

## 1. ¿Qué es el módulo ElementosDefinidos?

Es un **módulo compartido** que centraliza:

- **Catálogo por instalación**: qué elementos existen (T sortida, Colze base, Clau de Pas, Tapón para Agua; interruptor, enchufe, etc. para Electricidad) y **en qué tipo de punto** pueden colocarse (inicio, final, intermedio ordenado, intermedio libre).
- **Validación**: antes de añadir un punto o marcador, se comprueba que la combinación “elemento + tipo de punto” sea válida (por ejemplo: T sortida solo en intermedio; Colze base solo en inicio o final).
- **Utilidades para la UI**: listas de valores para ComboBox de “Elemento” y “Tipo de punto”, y conversión entre etiquetas de la paleta y claves internas.
- **Captura de punto libre** (opcional): un mixin para que su interactor pueda activar un modo “siguiente clic = colocar elemento” y añadir marcadores usando el catálogo.

**No genera geometría 3D**: la creación real de los elementos (Colze, T sortida, etc.) la hace su script o los PythonParts de Agua/TD (Colze_Base_002, Te_Sortida_004, etc.). El módulo solo dice **qué** se puede colocar **dónde** y ayuda a **validar** y **mostrar opciones** en la paleta.

Desde la reestructuración (2026), **toda la lógica de eventos y lectura de paleta está en el módulo**: su script (fontaneria, Electricidad, etc.) debe **llamar** a las funciones del módulo en lugar de duplicar código. Así el líder y los compañeros tienen una única fuente de verdad.

---

## 2. Estructura del módulo

```
ElementosDefinidos/
├── __init__.py      # Exporta clases y funciones públicas
├── base.py          # BaseDefinedElement, BaseMacroElement, POSIBLES_FUNCIONES
├── catalogo.py      # Catálogo por instalación, validación, ValueList para UI
├── capture.py         # ElementPointCaptureMixin (captura de punto libre + marcadores)
├── palette.py         # Lectura de paleta (tipo elemento, tipo punto, tolerancia)
├── preview.py         # Geometría de preview (círculos, formas por tipo)
├── serialization.py   # Serializar/deserializar element_markers y free_placed_points
├── handlers.py        # Eventos 1015–1018 y lógica de clic (añadir punto, finalizar, seleccionar)
├── creation.py        # Crear elementos 3D desde listas (callback por instalación)
├── editing.py         # find_hover_free_point, get_index_to_select_after_add
├── INTEGRACION.md     # Notas técnicas de integración con PolylineLib/fontaneria
└── GUIA_USO_ELEMENTOS_DEFINIDOS.md  # Esta guía
```

- **base.py**: Clases base y constantes (`inicio`, `final`, `intermedio_ordenado`, `intermedio_libre`, `bifurcación`). Pueden heredar para definir elementos concretos con `generate_preview()` y `generate_final_3d()`.
- **catalogo.py**: Aquí se define **qué elementos** tiene cada instalación y **en qué funciones** pueden ir. Es la “fuente de verdad” para validación y para rellenar los ComboBox de la paleta.
- **capture.py**: Mixin para reutilizar la lógica de “clic = punto libre” y “añadir marcador” en un interactor. Mixin opcional. **palette.py**: get_defined_element_settings, get_tipo_punto_libre_flag, get_free_point_selection_tolerance. **preview.py**: create_point_marker_geometry, draw_marker_for_element_type. **serialization.py**: serialize/deserialize element_markers y free_placed_points. **handlers.py**: llamar start_element_point_capture (1015), add_defined_element_marker (1016), on_anadir_punto_libre (1017), on_finalizar_puntos_libres (1018), handle_click_add_free_point, add_intermediate_element_at_point. **creation.py**: create_elements_from_free_placed_points con callback por instalación. **editing.py**: find_hover_free_point, get_index_to_select_after_add.

---

## 3. Conceptos clave

| Concepto | Significado |
|----------|-------------|
| **Instalación** | Tipo de red: `"AGUA"`, `"ELECTRICIDAD"`, etc. Cada una tiene su lista de elementos y reglas. |
| **Elemento** | Tipo de objeto a colocar: T sortida, Colze base, Clau de Pas, Tapón (Agua); interruptor, enchufe, etc. (Electricidad). |
| **Tipo de punto / Función** | Ubicación lógica: `inicio`, `final`, `intermedio_ordenado`, `intermedio_libre`. |
| **Key** | Identificador interno del elemento: `t_sortida`, `colze_base`, `clau_de_pas`, `taps`. |
| **Label** | Texto para la UI: "T sortida", "Colze base", "Clau de Pas", "Tapón". |
| **Marcador** | Registro en memoria (posición + tipo de punto + tipo de elemento) que luego su script usa para crear el 3D. |
| **Puntos libres** | Puntos colocados **sin** polilínea previa; se guardan en una lista (`free_placed_points`) y al “Finalizar” se crean los elementos 3D en esas posiciones. |

**Restricciones Agua (actuales):**

- **Solo inicio/final**: Colze base, Tapón.
- **Solo intermedio (ordenado o libre)**: T sortida, Clau de Pas.

---

## 4. Uso rápido: leer el catálogo desde un script

Si solo necesitan **validar** o **obtener listas para la UI**:

```python
from ElementosDefinidos import (
    get_elementos_para_instalacion,
    get_value_list_elementos,
    get_value_list_tipo_punto,
    validar_ubicacion_elemento,
    label_a_key_agua,
    label_tipo_punto_to_funcion,
)

# Lista de elementos para el ComboBox "Elemento"
items = get_elementos_para_instalacion("AGUA")
# Cada item: {"key", "label", "posibles_funciones", "funcion_defecto", "solo_inicio_final", "solo_intermedio"}

# Cadena para ValueList del ComboBox de elemento (ej. "T sortida|Colze base|Clau de Pas|Taps")
value_list_elementos = get_value_list_elementos("AGUA")

# Cadena para ValueList del ComboBox "Tipo de punto" según el elemento seleccionado
# Ej.: para "T sortida" → "Intermedio ordenado|Intermedio libre"
#      para "Colze base" → "Inicio|Final"
value_list_tipo = get_value_list_tipo_punto("AGUA", "T sortida")

# Validar antes de añadir un punto o marcador
ok, mensaje = validar_ubicacion_elemento("AGUA", "t_sortida", "intermedio_libre")
if not ok:
    ShowMessageBox(mensaje)

# Convertir valor del ComboBox a key interna (solo Agua)
key = label_a_key_agua("Clau de Pas")  # → "clau_de_pas"

# Convertir valor del ComboBox "Tipo de punto" a función interna
funcion = label_tipo_punto_to_funcion("Intermedio libre")  # → "intermedio_libre"
```

### 4.1 Snippet de integración rápido (puntos libres)

Para integrar **modo puntos libres** en un PythonPart nuevo copiando solo un bloque pequeño:

```python
from ElementosDefinidos import (
    on_anadir_punto_libre,
    on_finalizar_puntos_libres,
    handle_click_add_free_point,
    get_free_point_selection_tolerance,
    find_hover_free_point,
    serialize_free_placed_points,
    deserialize_free_placed_points,
    create_elements_from_free_placed_points,
)


class ScriptObject(object):
    def __init__(self, build_ele, doc):
        self.build_ele = build_ele
        self.doc = doc

        # Puntos libres (modo "Modo puntos libres")
        self.free_placed_points = []

        # Referencia al interactor (se asigna desde el interactor)
        self.interactor = None

    # Serialización opcional (guardar/restaurar puntos libres)
    def _serialize_state_to_json(self):
        import json

        state = {}
        state["free_placed_points"] = serialize_free_placed_points(
            getattr(self, "free_placed_points", []) or []
        )
        return json.dumps(state)

    def _deserialize_state_from_json(self, json_str):
        import json

        state = json.loads(json_str or "{}")
        self.free_placed_points = deserialize_free_placed_points(
            state.get("free_placed_points") or []
        )

    # CALLBACK: creación real del elemento 3D en cada punto libre
    def _create_element_at_free_point(self, build_ele, doc, element_type, pos):
        """
        Crea un elemento 3D en 'pos' del tipo 'element_type'.
        Devuelve True si crea algo, False si no.
        """
        element_type = (element_type or "").strip().lower()

        # Ejemplo para Agua/TD: adapta a tus propios modelos
        from Agua.fontaneria import (
            ColzeBaseCreateElement,
            TeSortidaCreateElement,
            ClauDePasCreateElement,
            TapsCreateElement,
        )

        if element_type == "t_sortida":
            return TeSortidaCreateElement(build_ele, doc, pos)
        elif element_type == "colze_base":
            return ColzeBaseCreateElement(build_ele, doc, pos)
        elif element_type == "clau_de_pas":
            return ClauDePasCreateElement(build_ele, doc, pos)
        elif element_type == "taps":
            return TapsCreateElement(build_ele, doc, pos)

        # TODO: añadir aquí otros tipos si su instalación tiene más
        return False

    def _create_elements_from_free_placed_points(self, coord_input):
        """
        Llamado al pulsar 'Finalizar puntos libres' (1018):
        crea todos los 3D desde free_placed_points y vacía la lista.
        """
        return create_elements_from_free_placed_points(
            self,
            coord_input,
            self._create_element_at_free_point,
        )


def on_control_event(build_ele, event_id, script_object):
    # ... otros eventos ...

    if event_id == 1017:  # Añadir punto libre
        on_anadir_punto_libre(script_object, script_object.interactor, "AGUA")

    elif event_id == 1018:  # Finalizar puntos libres
        on_finalizar_puntos_libres(
            script_object,
            script_object.interactor,
            script_object._create_elements_from_free_placed_points,
        )


class MiInteractor(object):
    def __init__(self, script_object, coord_input):
        self.script_object = script_object
        self.coord_input = coord_input

        # Conectar en ambos sentidos
        self.script_object.interactor = self

        # Estado de puntos libres
        self.next_click_adds_free_point = False
        self.free_point_hover_index = -1
        self.free_point_selected_index = None
        self.free_point_dragging = False
        self.free_point_drag_index = None

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        is_click = self.coord_input.IsMouseClick(mouse_msg)

        # 1) Si estamos en modo “siguiente clic = añadir punto libre”
        if is_click and getattr(self, "next_click_adds_free_point", False):
            consumed = handle_click_add_free_point(
                self,
                self.script_object,
                pnt,
                "AGUA",
            )
            if consumed:
                self.next_click_adds_free_point = False
                return True

        # 2) Hover/selección de puntos libres ya colocados (opcional)
        free_list = getattr(self.script_object, "free_placed_points", []) or []
        if free_list:
            tol = get_free_point_selection_tolerance(
                getattr(self.script_object, "build_ele", None),
                "AGUA",
            )
            idx = find_hover_free_point(pnt, free_list, tol)
            self.free_point_hover_index = idx
            # Aquí normalmente llamarías a tu preview:
            # self._draw_preview(pnt)

        # ... resto de la lógica de ratón ...
        return False
```

Este snippet asume que ya tienen configurada en el `.pyp` la pestaña **“Modo puntos libres”** con:

- `DefinedElementType` y `TipoPuntoLibre` como `StringComboBox`.
- Botones `AnadirPuntoLibre` (EventId 1017) y `FinalizarPuntosLibres` (EventId 1018).

Cada equipo solo debe adaptar el callback `_create_element_at_free_point` para llamar a sus propios PythonParts 3D.

### 4.2 Registrar elementos definidos con `CallbackDefinedElement` (ejemplo Agua)

Si su instalación ya tiene PythonParts que exponen una función `create_element(build_ele, doc, pos)` o similar (como Agua: `Colze_Base_002`, `Te_Sortida_004`, etc.), pueden registrar los elementos definidos una sola vez usando `CallbackDefinedElement` y reutilizar esa definición para **preview** y **3D final**:

```python
from ElementosDefinidos import CallbackDefinedElement, get_elementos_para_instalacion

# Importar las funciones create_element de sus PythonParts
from Agua.Colze_Base_002 import create_element as ColzeBaseCreateElement
from Agua.Te_Sortida_004 import create_element as TeSortidaCreateElement
from Agua.Clau_de_Pas_006 import create_element as ClauDePasCreateElement
from Agua.Taps_010 import create_element as TapsCreateElement

_CREATE_ELEMENT_BY_KEY = {
    "colze_base": ColzeBaseCreateElement,
    "t_sortida": TeSortidaCreateElement,
    "clau_de_pas": ClauDePasCreateElement,
    "taps": TapsCreateElement,
}

_defined_elements = {}
for info in get_elementos_para_instalacion("AGUA"):
    key = info["key"]
    create_fn = _CREATE_ELEMENT_BY_KEY.get(key)
    if create_fn is not None:
        _defined_elements[key] = CallbackDefinedElement(
            nombre=info["label"],
            callback_geometria=create_fn,
            posibles_funciones=info.get("posibles_funciones"),
            funcion_defecto=info.get("funcion_defecto"),
        )


def get_element_model_list(build_ele, doc, element_type: str):
    """Preview 3D de un elemento definido (para puntos libres o marcadores)."""
    elem = _defined_elements.get((element_type or "").strip().lower())
    if elem is None:
        return []
    return elem.generate_preview(build_ele, doc) or []


def create_single_element(build_ele, doc, element_type: str, pos):
    """Crea un elemento 3D en 'pos' usando el registro anterior."""
    elem = _defined_elements.get((element_type or "").strip().lower())
    if elem is None:
        return False
    model_list = elem.generate_final_3d(build_ele, doc)
    if not model_list:
        return False
    # Aquí aplicarían la matriz de rotación/traslación que necesiten
    # (ejemplo simplificado sin transformaciones adicionales):
    from NemAll_Python_BasisElements import AllplanBasisElements
    from NemAll_Python_BaseElements import AllplanBaseElements
    import NemAll_Python_Geometry as AllplanGeo

    common_props = AllplanBaseElements.GetGlobalNamespace().GetCommonProperties()
    mat = AllplanGeo.Matrix3D()
    mat.SetTranslation(AllplanGeo.Vector3D(pos.X, pos.Y, pos.Z))
    AllplanBaseElements.CreateElements(doc, mat, model_list, [], None)
    return True
```

En Agua/fontaneria este patrón ya está aplicado (`_agua_defined_elements`). Para otras instalaciones (Electricidad, Saneamiento, etc.) basta con:

- Añadir sus elementos en `catalogo.py` (`get_elementos_para_instalacion`).
- Mapear cada `key` a la función `create_element` correspondiente.
- Usar `generate_preview` / `generate_final_3d` vía `CallbackDefinedElement` como en el ejemplo.

### 4.3 Uso recomendado: llamar al módulo (sin duplicar lógica)

Para **eventos 1015, 1016, 1017, 1018** y lectura de paleta, **importen y llamen** a las funciones del módulo en lugar de implementar la lógica en su script:

```python
from ElementosDefinidos import (
    get_defined_element_settings,
    get_tipo_punto_libre_flag,
    get_free_point_selection_tolerance,
    find_hover_free_point,
    validar_ubicacion_elemento,
    create_point_marker_geometry,
    draw_marker_for_element_type,
    create_elements_from_free_placed_points,
)
from ElementosDefinidos.handlers import (
    start_element_point_capture,
    add_defined_element_marker,
    on_anadir_punto_libre,
    on_finalizar_puntos_libres,
    handle_element_point_capture_click,
    handle_click_add_free_point,
    add_intermediate_element_at_point,
)
```

En el interactor: delegar 1015 en `start_element_point_capture(intr, "AGUA")`, 1016 en `add_defined_element_marker(intr, "AGUA")`, 1017 en `on_anadir_punto_libre(script_object, intr, "AGUA")`, 1018 en `on_finalizar_puntos_libres(script_object, intr, script_object._create_elements_from_free_placed_points)`. Para el clic que añade un punto libre, llamar `handle_click_add_free_point(intr, script_object, raw_pnt, "AGUA")`. Referencia completa: **fontaneria.py**.

---

## 5. Integración completa: paleta + eventos + flujo

Para tener **paleta + validación + colocación de puntos/marcadores** en su PythonPart:

1. **Paleta (.pyp)**  
   - ComboBox **Elemento** con `ValueList` = `get_value_list_elementos("AGUA")` (o estático: `T sortida|Colze base|Clau de Pas|Taps`).  
   - ComboBox **Tipo de punto** con opciones según el elemento (en Agua/fontaneria se usa un ValueList condicional en el .pyp; ver [Configurar la paleta](#9-configurar-la-paleta-pyp)).  
   - Botones que disparan eventos (por ejemplo 1017 = Añadir punto, 1018 = Finalizar).

2. **Script (Python)**  
   - En el manejador del botón “Añadir punto” (p. ej. 1017): activar un flag “el siguiente clic añade un punto libre” y leer de la paleta `DefinedElementType` y `TipoPuntoLibre` (o el parámetro que tengáis para el tipo de punto).  
   - En el procesamiento del ratón: si ese flag está activo y hay un clic, obtener la posición, llamar a `validar_ubicacion_elemento(instalacion, element_key, funcion)` y, si es correcto, añadir el punto a `free_placed_points` (o a `element_markers` si trabajáis sobre polilínea).  
   - En el botón “Finalizar” (p. ej. 1018): recorrer `free_placed_points` y crear los elementos 3D en el documento (llamando a sus `ColzeBaseCreateElement`, `TeSortidaCreateElement`, etc.).

3. **Catálogo**  
   - Mantener en `catalogo.py` las restricciones por instalación (qué elemento puede ir en inicio/final/intermedio) para que `validar_ubicacion_elemento` y las listas de tipo de punto sean coherentes.

El flujo concreto en **fontaneria** (modo puntos libres) está descrito en [Modo puntos libres (paso a paso)](#6-modo-puntos-libres-paso-a-paso).

---

## 6. Modo puntos libres (paso a paso)

Este modo permite **colocar puntos en el plano sin dibujar antes la polilínea**. Cada punto tiene un tipo (inicio/final/intermedio) y un elemento (T sortida, Colze base, etc.). Al final, “Finalizar” crea los elementos 3D en esas posiciones.

### 6.1 Qué hace el usuario

1. Abrir la paleta del PythonPart e ir a la pestaña **“Modo puntos libres”**.
2. Elegir en el ComboBox **Elemento** (ej. “T sortida”, “Colze base”).
3. Elegir en el ComboBox **Tipo de punto** (las opciones dependen del elemento: para T sortida/Clau de Pas aparecen “Intermedio ordenado” / “Intermedio libre”; para Colze base/Tapón aparecen “Inicio” / “Final”).
4. Pulsar **“Añadir punto”**.
5. Mover el ratón: se muestra una **previsualización** del elemento siguiendo el cursor.  
   - En la referencia genérica del módulo la preview se implementa como iconos 2D (forma T, cuadrado, círculo, triángulo) dibujados desde `preview.py`.  
   - En implementaciones concretas como **Agua/fontaneria**, la preview utiliza directamente el **modelo 3D real** del elemento (model_list devuelto por los PythonParts Colze/T/Clau/Taps), pudiendo además aplicar una rotación adicional definida en la paleta.
6. Hacer **clic** en el plano: se añade el punto (se dibuja el elemento en esa posición; en fontaneria, con su 3D real y orientación).
7. Repetir 2–5 cuantas veces quiera (puede cambiar elemento y tipo de punto entre clics).
8. Pulsar **“Finalizar”**: se crean los elementos 3D (Colze, T sortida, Clau de Pas, Tapón) en cada punto y se vacía la lista de puntos libres.

### 6.2 Qué hace el script (referencia fontaneria)

- **Evento 1017 (Añadir punto)**  
  Activa “siguiente clic = añadir punto libre”. Se lee de la paleta el elemento y el tipo de punto (parámetro `TipoPuntoLibre` en la pestaña “Modo puntos libres”).

- **Al mover el ratón**  
  Si el modo “añadir punto” está activo, se obtiene la posición del cursor con `GetInputPoint(mouse_msg, ...)` y se llama a `_draw_preview(punto)` para dibujar la forma del elemento (T, cuadrado, círculo, triángulo) en esa posición.

- **Al hacer clic**  
  Se lee la posición del clic, se obtiene la función (tipo de punto) con `_get_tipo_punto_libre_flag()` (que usa `TipoPuntoLibre` o un valor por defecto según el elemento), se valida con `validar_ubicacion_elemento("AGUA", element_type, flag)` y, si es correcto, se añade a `script_object.free_placed_points` un diccionario con `pos`, `flag`, `element_type`, `order`. Luego se actualiza el preview.

- **Evento 1018 (Finalizar)**  
  Se llama a `_create_elements_from_free_placed_points()`: para cada entrada en `free_placed_points` se crea el 3D correspondiente (Colze, T sortida, Clau de Pas, Tapón) en esa posición y se vacía la lista.

### 6.3 Estructura de un punto libre

Cada elemento de `free_placed_points` es un diccionario:

```python
{
    "pos": Point3D(x, y, z),
    "flag": "inicio" | "final" | "intermedio_ordenado" | "intermedio_libre",
    "element_type": "t_sortida" | "colze_base" | "clau_de_pas" | "taps",
    "order": 0,  # índice de orden
}
```

---

## 7. Modo polilínea (elementos en inicio/final/intermedio)

En la pestaña **“Dibujar polilínea”** los elementos definidos se colocan **sobre la polilínea** (inicio, final o intermedio). Ahí se usan:

- **DefinedElementType**: ComboBox de elemento.
- **ElementPointMode**: Inicio (0) / Final (1) / Intermedio (2) (en fontaneria puede ser RadioButton en esa pestaña).
- **1015** – Seleccionar punto: activa “siguiente clic = colocar elemento” (para intermedio).
- **1016** – Agregar elemento: añade un marcador a `element_markers` según la posición y el elemento seleccionado.

Los marcadores en `element_markers` tienen la misma idea de validación: antes de añadir, se llama a `validar_ubicacion_elemento(instalacion, element_key, funcion)`.

Al **Finalizar** (1003), además de tubos/codos/tes, se recorren `element_markers` y se crean los 3D en las posiciones indicadas (igual que en modo puntos libres pero con posiciones ligadas a la polilínea).

---

## 8. Integración de macros sobre polilínea

Además de elementos definidos y puntos libres, el módulo `ElementosDefinidos` expone una API mínima para integrar **macros sobre polilínea** reutilizando la lógica de `PolylineLib.interactor.PolylineInteractor`.

### 8.1 API pública para macros

Las siguientes funciones se exportan desde `ElementosDefinidos`:

- `start_macro_point_capture(intr) -> bool`  
  Activa el modo de captura de punto libre para macro.  
  Este helper llama internamente a `intr.start_macro_point_capture()` y está pensado para manejar el evento **1013** de la paleta.

- `add_macro_library_marker(intr) -> bool`  
  Añade un marcador de macro a la lista `macro_markers` del interactor.  
  Este helper llama internamente a `intr._add_macro_library_marker()` y está pensado para manejar el evento **1014**.

### 8.2 Requisitos del interactor para macros

El interactor debe ser compatible con `PolylineInteractor` o implementar, como mínimo:

- Atributos:
  - `macro_markers: list[dict]`
  - `macro_point_capture_mode: bool`
  - `macro_point_capture_preview`
  - `macro_selected_point`
- Métodos:
  - `start_macro_point_capture() -> bool`
  - `_add_macro_library_marker() -> bool`
  - `_draw_preview(point3d)`
  - `_save_state_to_build_ele()`
- Acceso a `build_ele` con parámetros relacionados con macros:
  - `MarkerPointMode`
  - `MacroLibraryElementType`
  - `MacroSmartSymbolPath`
  - `MacroFixturePath`
  - `MacroSelectedLocalZ`

En la práctica, cualquier script que utilice `PolylineInteractor` puede invocar estos helpers directamente desde `ElementosDefinidos` y mantener todo el wiring de eventos en un único lugar.

### 8.3 Paleta (.pyp) para macros

La configuración en el `.pyp` es equivalente a la de `Electricidad/_polyline/pyp-library/polyline_test.pyp`:

- Grupo de parámetros para puntos de macro:
  - `MarkerPointMode` (`RadioButtonGroup`): Inicio, Final, Libre.
  - Botón **Seleccionar punto** con `EventId` **1013**.
- Grupo de parámetros para la macro real:
  - `MacroZAbs` (cota Z).
  - `MacroLibraryElementType` (tipo de macro: SmartSymbol/Fixture).
  - `MacroSmartSymbolPath` / `MacroFixturePath` con su diálogo correspondiente.

La decisión de qué macro se inserta y con qué parámetros pertenece al script o a la configuración de PolylineLib (registro de instalaciones), no al módulo `ElementosDefinidos`.

### 8.4 Ejemplo de integración de eventos

Ejemplo simplificado de integración de eventos de macro en un script host:

```python
from ElementosDefinidos import (
    start_macro_point_capture,
    add_macro_library_marker,
)


class ScriptObject:
    def __init__(self, build_ele, doc):
        self.build_ele = build_ele
        self.doc = doc
        self.script_object_interactor = None  # Se asigna al crear el interactor

    def on_control_event(self, event_id: int) -> bool:
        intr = self.script_object_interactor
        if intr is None:
            return False

        if event_id == 1013:
            # Macro: modo captura de punto libre
            return start_macro_point_capture(intr)

        if event_id == 1014:
            # Macro: añadir marcador en inicio/final/libre según MarkerPointMode
            return add_macro_library_marker(intr)

        return False
```

Con esta integración:

- El evento **1013** activa la captura de punto libre para macro.
- El evento **1014** añade un marcador a `macro_markers`, que posteriormente se materializa como `LibraryElement` en el flujo de finalización del `PythonPartGroup`.

---

## 9. Configurar el catálogo (añadir instalación o elemento)

Todo está en **ElementosDefinidos/catalogo.py**.

### Añadir una nueva instalación

1. En `get_funciones_por_elemento(instalacion)` añadir un bloque para su instalación (por ejemplo `"SANEAMIENTO"`), devolviendo un diccionario `{ "key_elemento": ["inicio", "final", ...], ... }`.
2. En `get_elementos_para_instalacion(instalacion)` añadir la lista de diccionarios con `key`, `label`, `posibles_funciones`, `funcion_defecto`, `solo_inicio_final`, `solo_intermedio`.
3. Si queréis ComboBox “Tipo de punto” dinámico, las funciones deben estar en `LABELS_FUNCION` (ya están inicio, final, intermedio_ordenado, intermedio_libre, bifurcación).

### Añadir o cambiar un elemento (ej. Agua)

1. Añadir la constante y la etiqueta en `LABELS_AGUA` (o la instalación que sea).
2. En `get_funciones_por_elemento("AGUA")` añadir o modificar la lista de funciones para ese elemento.
3. En `get_elementos_para_instalacion("AGUA")` añadir o ajustar el diccionario del elemento (`key`, `label`, `posibles_funciones`, etc.).
4. En `label_a_key_agua` (solo Agua) añadir la regla para mapear el texto del ComboBox a la key si hace falta.

### Cambiar restricciones (ej. “T sortida solo en intermedio”)

Se cambia en `get_funciones_por_elemento`: para ese elemento se deja solo `["intermedio_ordenado", "intermedio_libre"]`. Eso hace que `validar_ubicacion_elemento` rechace inicio/final y que `get_value_list_tipo_punto` devuelva solo esas dos opciones para ese elemento.

---

## 9. Configurar la paleta (.pyp)

### ComboBox “Elemento”

- **Name**: p. ej. `DefinedElementType`.  
- **ValueType**: `StringComboBox`.  
- **ValueList**: puede ser fijo `T sortida|Colze base|Clau de Pas|Taps` o generado en script con `get_value_list_elementos("AGUA")` si tienen inicialización dinámica.

### ComboBox “Tipo de punto” (modo puntos libres)

- **Name**: p. ej. `TipoPuntoLibre`.  
- **ValueType**: `StringComboBox`.  
- **ValueList** condicional (en el .pyp) para que las opciones dependan del elemento seleccionado. En fontaneria.pyp se usa una expresión Python multilínea que devuelve una cadena con `|`:

  - Si `DefinedElementType` es "T sortida" o "Clau de Pas" → `'Intermedio ordenado|Intermedio libre'`.
  - Si no → `'Inicio|Final'`.

Así el usuario solo ve tipos de punto válidos para el elemento elegido.

### Botones y eventos

- **Añadir punto**: EventId 1017 (en modo puntos libres).  
- **Finalizar**: EventId 1018 (crear 3D desde `free_placed_points` y vaciar la lista).  
- Para modo polilínea: 1015 (Seleccionar punto), 1016 (Agregar elemento).

Los IDs pueden ser otros en su script; lo importante es que en `on_control_event` manejen esos IDs y llamen a la lógica correspondiente (activar “siguiente clic”, añadir a `free_placed_points` o `element_markers`, o finalizar).

### Controles de rotación (opcional, modo puntos libres)

Algunas instalaciones (por ejemplo **Agua/fontaneria**) añaden en la pestaña “Modo puntos libres” parámetros numéricos adicionales para controlar la orientación 3D de los elementos definidos antes de crearlos:

- `RotX`, `RotY`, `RotZ` (`ValueType=Double` en el `.pyp`): ángulos en grados de rotación alrededor de los ejes X/Y/Z.

El script puede leer estos valores desde `build_ele` (p. ej. `build_ele.RotX.value`) y construir una `Matrix3D` de transformación usando la API oficial de Allplan (`Matrix3D` + `Angle`, ver [documentación de elementos Allplan](https://pythonparts.allplan.com/2025/manual/features/allplan_elements)).  
Esta matriz se aplica:

- En la **previsualización** (preview 3D de puntos libres), para que el usuario vea el elemento ya orientado.  
- En la **creación definitiva** (callback pasado a `create_elements_from_free_placed_points`), garantizando que lo creado en el documento coincide con lo visto en la preview.

---

## 10. Resumen de eventos y parámetros

| EventId | Uso | Acción |
|---------|-----|--------|
| 1015 | Modo polilínea | Seleccionar punto (siguiente clic = colocar elemento intermedio). |
| 1016 | Modo polilínea | Agregar elemento definido (según posición Inicio/Final/Intermedio y elemento). |
| 1017 | Modo puntos libres | Activar “siguiente clic = añadir punto libre”; previsualización sigue al cursor. |
| 1018 | Modo puntos libres | Finalizar: crear 3D desde `free_placed_points` y vaciar la lista. |

| Parámetro | Descripción |
|-----------|-------------|
| DefinedElementType | ComboBox: tipo de elemento (T sortida, Colze base, Clau de Pas, Taps). |
| TipoPuntoLibre | ComboBox (pestaña puntos libres): tipo de punto (Inicio, Final, Intermedio ordenado, Intermedio libre). |
| ElementPointMode | Radio Inicio/Final/Intermedio en la pestaña “Dibujar polilínea”. |

---

## 11. Preguntas frecuentes y problemas habituales

**P: El tipo de punto no cambia; siempre se registra como “inicio”.**  
R: En modo puntos libres hay que leer el parámetro de la pestaña “Modo puntos libres” (p. ej. `TipoPuntoLibre`). No usar el RadioButton de la otra pestaña (`ElementPointMode`) como fallback para puntos libres, porque por defecto es 0 = Inicio. En fontaneria, `_get_tipo_punto_libre_flag()` lee `TipoPuntoLibre` y, si no está disponible, infiere según el elemento (intermedio_libre para T sortida/Clau de Pas, final para Colze/Tapón).

**P: El ComboBox “Tipo de punto” muestra código o una opción muy larga.**  
R: El ValueList debe ser una **expresión Python que devuelva una sola cadena** (p. ej. con `return 'Inicio|Final'`). Si en el .pyp se pone una expresión en una sola línea con `|`, a veces el parser parte por `|` antes de evaluar; usar la forma multilínea con `if/else` y `return` dentro de `<ValueList>`.

**P: La previsualización no sigue al cursor.**  
R: En el manejo del movimiento del ratón hay que usar la posición del **mensaje de ratón** actual, no el “último punto de entrada”. Usar `GetInputPoint(mouse_msg, pnt, msg_info, ...).GetPoint()` para ese mensaje y pasar ese punto a `_draw_preview()`.

**P: Queremos añadir un nuevo elemento (p. ej. “Válvula”) para Agua.**  
R: Ver [Configurar el catálogo](#8-configurar-el-catálogo-añadir-instalación-o-elemento): añadir la key y label en `catalogo.py`, las funciones permitidas en `get_funciones_por_elemento` y en `get_elementos_para_instalacion`, y la regla en `label_a_key_agua` si usan ese helper. En su script, en el flujo que crea 3D, añadir el caso para esa key y llamar al PythonPart que cree ese elemento.

**P: ¿Dónde se crean realmente los elementos 3D?**  
R: En tu script (fontaneria, Electricidad, etc.). El módulo no crea geometría; solo valida y ofrece helpers. Para puntos libres pueden usar `create_elements_from_free_placed_points(script_object, coord_input, create_element_callback)` de **ElementosDefinidos/creation.py**: el callback (p. ej. `_create_single_element_agua` en fontaneria) recibe `(build_ele, doc, element_type, pos)` y crea el 3D (ColzeBaseCreateElement, TeSortidaCreateElement, etc.). Los marcadores en polilínea se recorren en `_finalize_and_create_now()` y cada script crea el 3D según su instalación.

---

**Versión**: 1.1  
**Última actualización**: 2026 (handlers en handlers.py; fontaneria delega en el módulo)
