# PolyLib — Librería base para instalaciones MEP

Librería compartida para crear PythonParts de polilínea en Allplan 2025.
Gestiona el dibujo de segmentos, la creación de PythonParts, la copia entre planos y la numeración automática.

---

## Estructura mínima de una instalación

```
Instalaciones/
├── PolyLib/                      ← librería (no modificar)
└── MiInstalacion/
    ├── polyline_reg_mi_inst.py   ← registro de la instalación
    └── pyp-scripts/
        └── mi_inst_polyline.py  ← script principal (hooks)
```

---

## 1. Registro — `polyline_reg_ventilacion.py`

Define los metadatos de la instalación y la registra en el sistema.

```python
from Instalaciones.PolyLib.installation_registry import register_installation
from Instalaciones.PolyLib.models import ElementTypes

INSTALLATION_INFO = {
    "name": "MI_INSTALACION",
    "label": "Mi Instalación",
    "angles": [0, 45, 90, 135, 180, -45, -90, -135],
    "default_layers": {
        "default":          "MI_LAYER_DEFAULT",
        "layer_polyline":   "MI_LAYER_EJE",
        "layer_cuboid_label": "MI_LAYER_LABEL",
    },
    "layers": [
        {"key": "MI_LAYER_DEFAULT", "label": "Mi capa principal"},
        {"key": "MI_LAYER_EJE",     "label": "Mi capa eje"},
    ],
    "installation_types": [
        {
            "key": "conducto_normal",      # clave del elemento principal
            "label": "Conducto",
            "is_individual": False,        # True = un PythonPart por segmento
            "min_segment_length": 300,
            "angles": [0, 45, 90, 135, 180, 225, 270, 315],
            "color": 5,
            "diameter": 75,
            "elems": ["manguito"],         # accesorios automáticos
            "connections": [ElementTypes.UNION],
        },
    ],
    "elements3D": [
        {
            "key": "conducto_normal",
            "label": "Conducto",
            "module_path": "pyp-scripts.conducto_normal_script",
            "pythonpart": "ConductoNormalScript",
        },
        {
            "key": "manguito",
            "label": "Manguito",
            "module_path": "pyp-scripts.manguito_script",
            "pythonpart": "ManguitoScript",
        },
    ],
    "summary": {k: [] for k in ["conductos", "manguitos"]},
}

def setup(import_base):
    register_installation(INSTALLATION_INFO, import_base)
```

> **Tip:** usa la función `create_element(key, label)` del archivo de ventilación para generar cada entrada de `elements3D` automáticamente a partir del `key`.

---

## 2. Script principal — `mi_inst_polyline.py`

### 2.1 Inicialización

```python
import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib.models import GeneratedElement

CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation="MI_INSTALACION",
    parameters_show=profile.show,       # AdditionalParametersBase
    parameters_enabled=profile.enabled, # AdditionalParametersBase
    limit_angles=True,
    allowed_angles=[0.0, 45.0, 90.0, 135.0, 180.0, -45.0, -90.0, -135.0],
)

def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )
    # Asignar los dos hooks obligatorios
    script_object.element_creation_preview_hook    = _create_elements_for_segment_group
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs
    return script_object
```

---

### 2.2 Hook de previsualización — `element_creation_preview_hook`

Genera la geometría 3D de los segmentos **sin** crear PythonParts.

La librería llama a este hook en los siguientes momentos (no en cada movimiento del cursor):
- Al cambiar el modo de dibujo (insertar, editar, seleccionar)
- Al guardar un segmento
- Al mover o borrar un vértice
- Al cambiar el tipo de instalación activo

**Firma:**
```python
def _create_elements_for_segment_group(
    segments: list,                              # lista de SegmentItem del camino actual
    so: PBL.script_object.PolylineScriptObject,
) -> list[GeneratedElement]:
```

El hook recibe los segmentos de **un solo camino** y debe devolver una lista de `GeneratedElement`.
La librería lo llama una vez por cada camino (path) y acumula los resultados en `so.element_list`.

**`_get_pythonpart_installed` — obtener la geometría 3D de un elemento del catálogo:**

```python
model_elems = so._get_pythonpart_installed(
    element_key = "conducto_normal",   # key registrado en elements3D
    exec_args   = (color,),            # argumentos posicionales para execute()
    exec_kwargs = {},                  # argumentos keyword para execute()
    attr_args   = (),                  # argumentos para get_attributes()
    attr_kwargs = {"value": diameter}, # keyword para get_attributes()
)
# Retorna: list[ModelElement3D] | None
```

Internamente hace:
1. Busca la clase registrada con ese `key` en el catálogo.
2. Instancia la clase con `cls(build_ele, so)`.
3. Llama a `inst.execute(*exec_args, **exec_kwargs)` y extrae `.elements`.
4. Si el elemento aún no tiene atributos por defecto, llama a `inst.get_attributes(*attr_args, **attr_kwargs)` y los guarda en `so.default_attributes[element_key]`.

**`GeneratedElement` — dataclass de retorno:**
```python
@dataclass
class GeneratedElement:
    element:      ModelElement3D   # geometría 3D
    index:        int              # posición en la lista de entrada (data_list)
    element_type: str              # key del elemento, ej. "conducto_normal", "manguito"
```

**Estructura de un segmento (SegmentItem):**
```
segment.data.angulo_xy   → float    ángulo horizontal (°)
segment.data.angulo_z    → float    ángulo vertical (°)
segment.data.length      → float    longitud (mm)
segment.start_point      → Point3D
segment.end_point        → Point3D
```

---

### 2.3 Hook de atributos y capas (layers) — `element_creation_layer_attrs_hook`

Aplica atributos Allplan, numeración automática y capas a cada elemento.
La librería lo llama al finalizar el trazado (guardar / finalizar).

**Firma:**
```python
def _create_elements_with_layers_attrs(
    elements_generated: list[GeneratedElement],  # salida del hook anterior
    path_idx: int,                               # índice del camino (0-based)
    so: PBL.script_object.PolylineScriptObject,
) -> list[GeneratedElement]:
```

**Flujo mínimo:**
```python
def _create_elements_with_layers_attrs(elements_generated, path_idx, so):
    result = []
    for i, element in enumerate(elements_generated):
        storage_key = f"seg_{path_idx}_elem_{element.index}"

        # Atributos por defecto del tipo de elemento
        base_attrs = so.default_attributes.get(element.element_type, [])

        # Atributos personalizados aplicados por el usuario (desde el interactor)
        custom_attrs = so.applied_attributes.get(storage_key, [])

        # Mezclar y aplicar
        final_attrs = custom_attrs if custom_attrs else base_attrs
        if final_attrs:
            from NemAll_Python_BaseElements import AttributeSet, Attributes
            element.element.SetAttributes(Attributes([AttributeSet(final_attrs)]))

        result.append(element)
    return result
```

> En la implementación real (`ventilacion_polyline.py`) se añaden:
> - numeración automática correlativa por grupo (`so.init_storage._get_next_number`)
> - cuboides de etiqueta (`_create_cuboide_label`) al inicio de cada sub-grupo
> - guardado de attrs para la polilínea de eje (`so._polyline_attrs`)

---

## 3. Referencia de hooks

| Hook | Cuándo se llama | Retorna |
|------|-----------------|---------|
| `element_creation_preview_hook(segments, so)` | Al cambiar modo de dibujo, guardar, mover/borrar vértice o cambiar tipo de instalación | `list[GeneratedElement]` |
| `element_creation_layer_attrs_hook(elements_generated, path_idx, so)` | Al guardar / finalizar el trazado | `list[GeneratedElement]` |

---

## 4. Helpers útiles del script object (`so`)

| Atributo / método | Descripción |
|-------------------|-------------|
| `so.current_inst_config` | `dict` con la config del tipo de instalación activo |
| `so.pythonparts_modules` | Lista de `ElementDefinition` cargados |
| `so._get_pythonpart_installed(element_key, exec_args, exec_kwargs, attr_args, attr_kwargs)` | Instancia el PythonPart, llama a `execute()` y retorna `list[ModelElement3D]`. También registra atributos por defecto en `so.default_attributes`. |
| `so.default_attributes` | `{element_type: [attrs]}` con atributos por defecto por tipo |
| `so.applied_attributes` | `{storage_key: [attrs]}` con atributos personalizados aplicados desde el interactor |
| `so.saved_paths` | `list[list[Point3D]]` — puntos de cada camino dibujado |
| `so.element_type_core` | Clave del tipo de elemento principal (ej. `"conducto_normal"`) |
| `so.is_individual_mode` | `True` = un PythonPart por segmento |
| `so._polyline_attrs` | `dict | None` — attrs por subgrupo para la polilínea de eje |
| `so.default_layers` | `{"default": "...", "layer_polyline": "...", ...}` |
