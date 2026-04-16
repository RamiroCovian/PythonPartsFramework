# MacroCore: Modularización de la Gestión de Macros

## 1. Resumen y Propósito

`MacroCore` es un módulo compartido que centraliza la lógica reusable de macros dentro del ecosistema de instalaciones de Allplan. Su objetivo es desacoplar la funcionalidad genérica de macros del código específico de cada instalación, de forma que `Agua`, `Electricidad` u otras futuras instalaciones puedan reutilizar la misma base sin duplicar implementación.

Antes de esta modularización, la lógica de macros vivía mezclada con lógica específica de `Agua`. Eso dificultaba:

- reutilizar comportamiento entre instalaciones;
- mantener previews, placement y serialización de forma consistente;
- extender la feature con nuevas capacidades, como rotaciones `X/Y/Z`, sin replicar código.

La feature resuelve ese problema creando una capa base, `MacroCoreManager`, que concentra el flujo común de:

- lectura de parámetros de macro desde paleta;
- creación de marcadores de macro;
- preview real con `LibraryElement`;
- overlay de macros ya colocadas;
- placement con traslación y rotación;
- serialización/deserialización del estado;
- materialización final de macros como PythonParts.

## 2. Arquitectura y Componentes Clave

### Archivos principales creados o modificados

- `MacroCore/manager.py`
- `MacroCore/__init__.py`
- `Agua/pyp-scripts/macros/macro_manager.py`
- `Agua/pyp-scripts/agua_polyline.py`
- `Agua/pyp-library/agua_polyline.pyp`

### Relación entre componentes

La arquitectura quedó organizada en tres capas:

1. `PolyLib.MarkerManager`  
   Base transversal del sistema de markers. Provee el ciclo de vida general: eventos, mouse, selección, preview base, serialización y creación de PythonParts.

2. `MacroCoreManager`  
   Subclase reusable de `MarkerManager` que agrega el comportamiento genérico de macros. No conoce detalles de una instalación concreta, pero sí entiende los parámetros estándar de macros y cómo representar una macro real en Allplan.

3. `AguaMacroManager`  
   Subclase específica de `MacroCoreManager` para `Agua`. Conserva solo la lógica que depende del dominio de `Agua`, por ejemplo:
   - selección de `Room/Story/Locales`;
   - manejo de `DefinedElementType`;
   - carga de templates de elementos propios de la instalación.

La relación puede resumirse así:

```python
class MarkerManager:
    ...

class MacroCoreManager(MarkerManager):
    # lógica reusable de macros
    ...

class AguaMacroManager(MacroCoreManager):
    # integración específica de Agua
    ...
```

### Dependencias clave introducidas

En `MacroCore` se apoyan estas dependencias principales:

- `Instalaciones.PolyLib.marker_manager.MarkerManager`
- `NemAll_Python_Geometry` para `Point3D`, `Matrix3D`, `Line3D`, `Angle`
- `NemAll_Python_BasisElements` para `LibraryElement`, `LibraryElementProperties`
- `NemAll_Python_AllplanSettings`
- `NemAll_Python_Utility`
- `FileNameService` para resolver rutas estándar/globales
- `PythonPartUtil` para convertir macros en PythonParts finales

Además, `Agua` importa `MacroCore` explícitamente en `Agua/pyp-scripts/agua_polyline.py` y utiliza `AguaMacroManager` como `marker_manager_factory`.

## 3. Flujo de Implementación (Paso a Paso)

### Paso 1. Extraer la lógica genérica de macros a un módulo compartido

Se creó el paquete `MacroCore` con una API mínima:

```python
from .manager import MacroCoreManager

__all__ = ["MacroCoreManager"]
```

La clase principal, `MacroCoreManager`, encapsula la funcionalidad reusable. Esto permite que otras instalaciones hereden del core sin volver a implementar el flujo de macros desde cero.

### Paso 2. Estandarizar la lectura de parámetros de paleta

`MacroCoreManager` define nombres de parámetros estándar como atributos de clase:

```python
MACRO_POINT_MODE_PARAM = "MarkerPointMode"
MACRO_LIBRARY_TYPE_PARAM = "MacroLibraryElementType"
MACRO_SMART_PATH_PARAM = "MacroSmartSymbolPath"
MACRO_FIXTURE_PATH_PARAM = "MacroFixturePath"
MACRO_SELECTED_LOCAL_Z_PARAM = "MacroSelectedLocalZ"
MACRO_Z_RELATIVE_PARAM = "MacroZRelative"
MACRO_Z_ABS_PARAM = "MacroZAbs"
MACRO_ROT_X_PARAM = "MacroRotX"
MACRO_ROT_Y_PARAM = "MacroRotY"
MACRO_ROT_Z_PARAM = "MacroRotZ"
```

Esto resuelve dos problemas:

- unifica el contrato entre la paleta `.pyp` y el manager;
- facilita que una instalación nueva pueda sobrescribir nombres si usara otra convención.

En `Agua/pyp-library/agua_polyline.pyp` ya existen los parámetros necesarios para este contrato, incluyendo:

- `MarkerPointMode`
- `MacroSelectedLocalZ`
- `MacroZAbs`
- `MacroZRelative`
- `MacroSmartSymbolPath`
- `MacroFixturePath`
- `MacroRotX`, `MacroRotY`, `MacroRotZ`

### Paso 3. Resolver la configuración efectiva de la macro

El método `get_macro_settings_from_palette()` traduce el estado de la paleta a una estructura de configuración consumible por el resto del flujo.

Responsabilidades principales:

- traducir `MarkerPointMode` a `start`, `end` o `free`;
- determinar si la macro es `SmartSymbol` o `Fixture`;
- leer la ruta seleccionada;
- decidir la cota final `z_abs`;
- soportar modo manual y modo relativo a local;
- leer rotaciones `X/Y/Z`.

La parte más importante del cálculo es la resolución de altura:

```python
if selected_z > -100000.0:
    z_relative = ...
    z_abs = selected_z + z_relative
    self.current_floor_z = selected_z
    self.current_floor_index = 0
    auto_detect = True
else:
    z_abs = ...
    z_relative = z_abs
    self.current_floor_z = z_abs
    self.current_floor_index = -1
    auto_detect = False
```

Esto permite dos modos operativos:

- sin local seleccionado: usar `MacroZAbs`;
- con local seleccionado: usar `MacroSelectedLocalZ + MacroZRelative`.

### Paso 4. Crear marcadores de macro desacoplados del documento final

El método `_add_macro_library_marker()` genera un marker interno y lo guarda en `self.macro_markers`.

Ese marker concentra el estado necesario para:

- preview;
- overlay;
- serialización;
- creación final del PythonPart.

Estructura relevante del marker:

```python
marker = {
    "kind": kind,
    "pos": pos,
    "lib_type": lib_type,
    "smart_path": smart_path,
    "fixture_path": fixture_path,
    "z_abs": ...,
    "z_relative": ...,
    "rot_x": ...,
    "rot_y": ...,
    "rot_z": ...,
}
```

Este diseño evita recalcular todo desde la paleta cada vez y hace que el flujo sea persistible.

### Paso 5. Reemplazar el preview genérico por un preview real de macro

Uno de los cambios funcionales más importantes fue dejar de representar las macros solo con marcadores esquemáticos y usar un `LibraryElement` real como preview.

Esto ocurre en dos contextos:

- preview bajo cursor, mediante `get_macro_cursor_preview_geo()`;
- overlay de macros ya colocadas, mediante `draw_marker_preview()`.

El método `_create_library_preview_elements()` delega en `create_library_element_from_marker()` para construir el preview real.

### Paso 6. Construir el `LibraryElement` real para SmartSymbols y Fixtures

`create_library_element_from_marker()` resuelve el tipo de macro y crea el `LibraryElementProperties` adecuado.

Caso `SmartSymbol`:

```python
lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
    smart_path,
    AllplanBasisElements.LibraryElementType.eSmartSymbol,
    placement_mat,
)
```

Caso `Fixture`:

```python
lib_ele_prop = AllplanBasisElements.LibraryElementProperties(
    "", "", "",
    fixture_path,
    AllplanBasisElements.LibraryElementType.eFixtureSingleFile,
    placement_mat,
)
```

Para `.lfx`, además se replica el patrón de `LibraryDialogs.py` usando `SetPolyline(...)` como soporte específico del tipo de fixture.

Este cambio resuelve una limitación previa: el usuario ahora ve la macro real durante la captura y también en el overlay de edición.

### Paso 7. Aplicar rotaciones en los ejes X, Y y Z

La rotación se implementó en `_build_macro_placement_matrix()`. Ese método construye una `Matrix3D` a partir de:

- punto de colocación;
- cota absoluta final;
- ángulos `rot_x`, `rot_y`, `rot_z`.

Implementación clave:

```python
mat = AllplanGeo.Matrix3D()
if rot_x != 0.0:
    mat.Rotation(
        AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(1, 0, 0)),
        AllplanGeo.Angle.FromDeg(rot_x),
    )
if rot_y != 0.0:
    mat.Rotation(
        AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 1, 0)),
        AllplanGeo.Angle.FromDeg(rot_y),
    )
if rot_z != 0.0:
    mat.Rotation(
        AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 0, 1)),
        AllplanGeo.Angle.FromDeg(rot_z),
    )
mat.Translate(AllplanGeo.Vector3D(placement_point))
```

Detalle importante de implementación:

- la API de Allplan no acepta `float` directamente en `Matrix3D.Rotation`;
- fue necesario usar `AllplanGeo.Angle.FromDeg(...)`.

Esto asegura que la rotación funcione tanto en:

- preview del cursor;
- overlay de macros ya colocadas;
- inserción final.

### Paso 8. Persistir el estado de las macros, incluyendo rotaciones

`MacroCoreManager` sobrescribe `serialize_markers()` y `deserialize_markers()` para agregar `rot_x`, `rot_y` y `rot_z` al estado persistido.

Esto garantiza que al editar o restaurar el objeto:

- las macros mantengan su rotación;
- el overlay reconstruya el estado visual correcto;
- no se pierda información entre sesiones de edición.

### Paso 9. Materializar las macros como PythonParts en la creación final

La creación final se concentra en `append_macro_pythonparts()`.

El flujo es:

1. iterar `self.macro_markers`;
2. construir el `LibraryElement` real desde cada marker;
3. pasarlo a `PythonPartUtil`;
4. añadir una geometría mínima auxiliar para asegurar representación/soporte del PythonPart;
5. generar el PythonPart final y agregarlo al grupo de salida.

Esto desacopla completamente la representación temporal de la representación persistente.

### Paso 10. Reintegrar el core en Agua

En `Agua/pyp-scripts/macros/macro_manager.py`, `AguaMacroManager` ahora hereda de `MacroCoreManager`:

```python
from Instalaciones.MacroCore import MacroCoreManager

class AguaMacroManager(MacroCoreManager):
    ...
```

A partir de ese punto, `Agua` conserva solo la lógica específica de la instalación:

- selección de local (`_handle_room_selection`, `_clear_room_selection`);
- lectura de `DefinedElementType`;
- geometría de elementos definidos;
- carga de templates de módulos PythonPart propios de Agua.

Esto es el punto central de la modularización: `Agua` deja de ser el lugar donde vive la lógica reusable de macros y pasa a ser únicamente la capa de integración.

### Paso 11. Conectar el manager modularizado al entry point de Agua

En `Agua/pyp-scripts/agua_polyline.py`, la feature se integra de dos maneras:

1. se importa `AguaMacroManager`;
2. se lo registra como `marker_manager_factory` del config principal.

```python
CONFIG = PBL.script_object.PolylineBaseConfig(
    ...
    marker_manager_factory=lambda so, be: AguaMacroManager(so, be),
)
```

Además, `MacroCore` se agrega a la lista de módulos recargables durante desarrollo para que la iteración sea consistente.

En resumen, `MacroCore` convierte la gestión de macros en una capacidad reusable del framework de instalaciones, en lugar de un comportamiento embebido en `Agua`. La instalación `Agua` sigue controlando sus particularidades, pero delega al core todo el comportamiento transversal de macros: lectura de paleta, preview real, placement, rotación, persistencia y creación final.
