# Funcionalidad: Volver a Editar PythonPartGroup

Esta documentación explica cómo funciona la funcionalidad de volver a editar un PythonPartGroup después de haberlo creado, permitiendo continuar la edición con doble clic.




      
        <!-- Parámetro oculto para guardar el estado de las polilíneas (para poder restaurar al editar) -->
        <Parameter>
            <Name>SavedState</Name>
            <Text>SavedState</Text>
            <Value></Value>
            <Visible>False</Visible>
            <Enable>False</Enable>
            <ValueType>String</ValueType>
            <Persistent>Model</Persistent>
        </Parameter>  

        
## Resumen

Cuando se crea un PythonPartGroup, el estado de edición (polilíneas, segmentos, etc.) se guarda automáticamente en el parámetro `SavedState` del PythonPartGroup. Al hacer doble clic en el PythonPartGroup, Allplan automáticamente:

1. Detecta el doble clic y entra en modo modificación
2. Restaura el estado guardado desde el PythonPartGroup
3. Inicia el interactor para continuar editando

## Flujo de Funcionamiento

### 1. Guardado del Estado al Crear PythonPartGroup

Cuando se finaliza la creación y se crea el PythonPartGroup, el estado se guarda automáticamente:

**Ubicación en el código:** `Saneamiento.py`, método `_finalize_and_create_now()` (línea ~7050)

```python
# Agregar estado serializado para poder restaurarlo al editar
state_json = self._serialize_state_to_json()
if state_json:
    global_params['SavedState'] = state_json
    print(f"[SO] Estado guardado en PythonPartGroup ({len(state_json)} caracteres)")
```

El estado incluye:
- `saved_paths`: Lista de polilíneas (paths) creadas
- `saved_segments`: Lista de segmentos con sus propiedades (diámetro, sistema, tipo de instalación, etc.)

### 2. Detección de Doble Clic (Automático en Allplan)

Allplan detecta automáticamente el doble clic en un PythonPartGroup y:
- Establece `is_modification_mode = True` en el script_object
- Proporciona acceso al elemento a través de `modification_ele_list`
- Llama al método `__init__()` del script_object

**No se requiere código adicional** - esto es manejado automáticamente por el framework de Allplan.

### 3. Restauración del Estado al Editar

Cuando se edita un PythonPartGroup existente, el estado se restaura automáticamente:

**Ubicación en el código:** `Saneamiento.py`, método `__init__()` (línea ~1486)

```python
# Restaurar estado guardado si existe (al editar una instancia existente)
self._restore_saved_state()
```

El método `_restore_saved_state()` (línea ~1688) intenta restaurar el estado desde:

1. **Primero:** Parámetros de `build_ele` (SavedState, PolylineState, StateData)
2. **Segundo:** Parámetro `SavedState` del PythonPartGroup usando `PythonPartService`

**Código clave para leer desde PythonPartGroup:**

```python
# Si no se encontró en build_ele y estamos en modo modificación,
# intentar leer desde el PythonPartGroup usando PythonPartService
try:
    is_modification_mode = getattr(self, 'is_modification_mode', False)
    if is_modification_mode and hasattr(self, 'modification_ele_list'):
        python_part_adapter = self.modification_ele_list.get_base_element_adapter(self.document)
        if not python_part_adapter.IsNull():
            success, name, parameter = AllplanBaseElements.PythonPartService.GetParameter(python_part_adapter)
            if success and parameter:
                # Normalizar parámetros a lista
                if isinstance(parameter, str):
                    param_lines = parameter.split('\n')
                elif isinstance(parameter, (list, tuple)):
                    param_lines = parameter
                else:
                    param_lines = []
                
                # Buscar 'SavedState' en los parámetros
                for line in param_lines:
                    if isinstance(line, str):
                        line = line.strip()
                        if line.startswith('SavedState'):
                            if '=' in line:
                                state_json = line.split('=', 1)[1].strip()
                                if state_json:
                                    if self._deserialize_state_from_json(state_json):
                                        print(f"[SO] ✓ Estado previo restaurado desde PythonPartGroup.SavedState")
                                        return True
except Exception as e:
    print(f"[SO] Error intentando leer estado desde PythonPartGroup: {e}")
```

### 4. Inicio Automático del Modo de Edición

Una vez restaurado el estado, el interactor se inicia automáticamente y activa el modo de creación si hay datos restaurados:

**Ubicación en el código:** `Saneamiento.py`, método `start_input()` (línea ~1791)

```python
def start_input(self):
    self.script_object_interactor = PolylineInteractor(self)
    self.script_object_interactor.start_input(self.coord_input)
    
    # Si hay datos guardados, activar automáticamente el modo de creación
    if self.saved_paths or self.saved_segments:
        if self.script_object_interactor:
            self.script_object_interactor.create_mode = True
            print(f"[SO] ✓ Modo creación activado automáticamente (datos restaurados)")
            self.script_object_interactor._update_create_mode_display()
            self.script_object_interactor._print_prompt()
```

## Métodos Clave Implementados

### `_serialize_state_to_json()` (línea ~1609)

Serializa el estado actual (`saved_paths` y `saved_segments`) a formato JSON para guardarlo en el PythonPartGroup.

**Formato del JSON:**
```json
{
    "paths": [
        [{"X": x1, "Y": y1, "Z": z1}, {"X": x2, "Y": y2, "Z": z2}, ...],
        ...
    ],
    "segments": [
        {
            "points": [{"X": x1, "Y": y1, "Z": z1}, {"X": x2, "Y": y2, "Z": z2}],
            "diameter": 110.0,
            "system": "Pluvial",
            "installation_type_horizontal": "FABRICA",
            "installation_type_vertical": "TD",
            "face": "X",
            ...
        },
        ...
    ]
}
```

### `_deserialize_state_from_json()` (línea ~1646)

Deserializa el estado desde JSON y restaura `saved_paths` y `saved_segments`.

### `_restore_saved_state()` (línea ~1688)

Intenta restaurar el estado desde múltiples fuentes:
1. Parámetros de `build_ele`
2. Parámetro `SavedState` del PythonPartGroup (en modo modificación)

### `_save_state_to_build_ele()` (línea ~1757)

Guarda el estado actual en los parámetros de `build_ele` antes de crear elementos.

## Verificación del Funcionamiento

Para verificar que la funcionalidad está trabajando correctamente:

1. **Crear un PythonPartGroup:**
   - Crear una polilínea con el script
   - Activar el checkbox "Crear PythonPart"
   - Finalizar la creación (ESC o botón "Finalizar y crear")
   - Verificar en la consola: `[SO] Estado guardado en PythonPartGroup (X caracteres)`

2. **Editar el PythonPartGroup:**
   - Hacer doble clic en el PythonPartGroup creado
   - Verificar en la consola:
     - `[SO] Inicialización - is_modification_mode=True`
     - `[SO] Encontrado SavedState en PythonPartGroup: X caracteres`
     - `[SO] ✓ Estado previo restaurado desde PythonPartGroup.SavedState`
     - `[SO] Estado restaurado: X paths, Y segments`
     - `[SO] ✓ Modo creación activado automáticamente (datos restaurados)`

3. **Continuar editando:**
   - Deberías ver las polilíneas restauradas en el editor
   - Puedes agregar nuevos puntos, modificar segmentos, etc.
   - Al finalizar, los cambios se guardan en el PythonPartGroup

4. **Finalizar edición:**
   - Presionar ESC o el botón "Finalizar y crear"
   - Verificar en la consola:
     - `[SO] ========== MODO MODIFICACIÓN: ACTUALIZANDO PYTHONPARTGROUP ==========`
     - `[SO] ✓ Estado guardado en build_ele.SavedState (X caracteres)`
     - `[SO] ✓ Estado actualizado en PythonPartGroup (X caracteres)`
     - `[SO] ✓ Estado actualizado en PythonPartGroup - Allplan regenerará los elementos automáticamente`
   - Allplan regenerará automáticamente los elementos del PythonPartGroup con los nuevos datos

## Solución de Problemas

### El estado no se restaura

**Posibles causas:**
1. El parámetro `SavedState` no existe en el PythonPartGroup
   - **Solución:** Verificar que `_finalize_and_create_now()` está guardando el estado correctamente

2. El formato del parámetro no es el esperado
   - **Solución:** Verificar que `PythonPartService.GetParameter()` devuelve el formato correcto

3. `modification_ele_list` o `document` no están disponibles
   - **Solución:** Verificar que estos atributos están disponibles en `BaseScriptObject`

### El modo de creación no se activa automáticamente

**Verificar:**
- Que `saved_paths` o `saved_segments` no están vacíos después de `_restore_saved_state()`
- Que `start_input()` se está llamando correctamente
- Que el interactor se está creando correctamente

### El doble clic no funciona

**Verificar:**
- Que el PythonPartGroup se creó correctamente
- Que el archivo `.pyp` tiene la configuración correcta para permitir edición
- Que Allplan está en modo de edición (no solo visualización)

## Notas Importantes

1. **El estado se guarda en el PythonPartGroup**, no en elementos individuales. Esto permite que todo el grupo se edite como una unidad.

2. **El formato del parámetro SavedState** puede variar según cómo Allplan almacena los parámetros. El código maneja tanto formato string como lista.

3. **La restauración automática** solo funciona si el estado fue guardado previamente. En la primera creación, no hay estado que restaurar (esto es normal).

4. **El modo de creación se activa automáticamente** si hay datos restaurados, permitiendo continuar editando inmediatamente sin necesidad de activar manualmente el checkbox.

## 5. Actualización del Estado al Finalizar Edición

Cuando se finaliza la edición de un PythonPartGroup existente (en modo modificación), el estado actualizado se guarda automáticamente:

**Ubicación en el código:** `Saneamiento.py`, método `_finalize_and_create_now()` (línea ~7101)

```python
# Verificar si estamos en modo modificación
is_modification_mode = getattr(self, 'is_modification_mode', False)

if is_modification_mode:
    # En modo modificación, solo actualizar el estado del PythonPartGroup existente
    # Allplan regenerará automáticamente los elementos basándose en los parámetros actualizados
    self._save_state_to_build_ele()
    self._update_pythonpartgroup_state()
```

El método `_update_pythonpartgroup_state()` (línea ~1790) actualiza el estado directamente en el PythonPartGroup:

```python
def _update_pythonpartgroup_state(self):
    """
    Actualiza el estado guardado en el PythonPartGroup cuando estamos en modo modificación.
    Esto permite que los cambios se persistan cuando se finaliza la edición.
    """
    # Obtener el adapter del PythonPartGroup
    python_part_adapter = self.modification_ele_list.get_base_element_adapter(self.document)
    
    # Leer parámetros actuales y actualizar SavedState
    # El estado se guarda tanto en build_ele como directamente en el PythonPartGroup
```

**Comportamiento en modo modificación:**
- No se crea un nuevo PythonPartGroup
- Se actualiza el estado en `build_ele` (que Allplan usa para regenerar elementos)
- Se actualiza el estado directamente en el PythonPartGroup
- Allplan regenera automáticamente los elementos basándose en los parámetros actualizados

## 6. ¿Por qué Desaparecen los Sólidos al Volver a Editar?

### Explicación del Comportamiento

Cuando haces doble clic en un PythonPartGroup y regresas a la interacción, los sólidos 3D de la instalación desaparecen y solo ves las polilíneas para seguir editando. Este es el **comportamiento esperado y normal** de Allplan.

### 1. Dos Representaciones Diferentes

El código maneja **dos representaciones diferentes** del mismo elemento:

#### A) Representación de Edición (Polilíneas)
- **Cuándo se usa:** Durante la edición interactiva
- **Qué devuelve:** El método `execute()` (líneas 1824-1893) devuelve solo **líneas y polilíneas** desde `saved_segments` y `saved_paths`:

```python
# Línea 1873-1883: Solo crea líneas/polilíneas
for segment_info in self.saved_segments:
    line = AllplanGeo.Line3D(...)
    elements.append(AllplanBasisElements.ModelElement3D(..., line))
```

#### B) Representación Final (Sólidos 3D)
- **Cuándo se usa:** Al finalizar la creación
- **Qué crea:** El método `_finalize_and_create_now()` (línea 1903+) crea los **sólidos 3D** (tubos, codos, reductores, bifurcaciones) y los agrupa en el PythonPartGroup

### 2. Qué se Guarda en SavedState

Al crear el PythonPartGroup, **solo se guardan las polilíneas y segmentos** (líneas 7124-7127):

```python
state_json = self._serialize_state_to_json()  # Solo paths y segments
global_params['SavedState'] = state_json
```

**No se guardan los sólidos 3D** - estos se generan dinámicamente a partir de las polilíneas cuando se finaliza la creación.

### 3. Qué Sucede al Hacer Doble Clic

Cuando haces doble clic en un PythonPartGroup:

1. **Allplan entra en modo modificación** automáticamente
2. **Se restaura el estado** desde `SavedState` (solo polilíneas/segmentos)
3. **Se llama a `execute()`**, que devuelve solo polilíneas/líneas para edición
4. **Allplan oculta temporalmente** los sólidos 3D del PythonPartGroup y muestra solo la representación de edición

### 4. Por Qué Desaparecen los Sólidos

Este es el **comportamiento esperado** de Allplan al editar un PythonPartGroup:

- ✅ Los sólidos 3D **siguen existiendo** en el PythonPartGroup
- 🔒 Se **ocultan temporalmente** mientras estás en modo edición
- 📝 Solo se muestra la **representación de edición** (polilíneas)
- 🔄 Al finalizar la edición, Allplan **regenera los sólidos** desde los parámetros actualizados

### 5. Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│ CREACIÓN INICIAL                                             │
└─────────────────────────────────────────────────────────────┘
  │
  ├─> Usuario crea polilíneas
  ├─> _finalize_and_create_now() crea sólidos 3D
  ├─> Se crea PythonPartGroup con sólidos
  └─> Sólidos visibles en el modelo ✅

┌─────────────────────────────────────────────────────────────┐
│ DOBLE CLIC (Modo Modificación)                              │
└─────────────────────────────────────────────────────────────┘
  │
  ├─> Allplan detecta doble clic
  ├─> Allplan llama create_element() (si existe)
  ├─> Allplan OCULTA automáticamente los sólidos del grupo 🔒
  ├─> Allplan inicia ScriptObject
  ├─> __init__() restaura SavedState (polilíneas)
  ├─> execute() devuelve polilíneas para edición
  └─> Solo polilíneas visibles durante edición 📝

┌─────────────────────────────────────────────────────────────┐
│ FINALIZAR EDICIÓN                                            │
└─────────────────────────────────────────────────────────────┘
  │
  ├─> _finalize_and_create_now() actualiza SavedState
  ├─> _update_pythonpartgroup_state() actualiza parámetros
  ├─> Allplan regenera PythonPartGroup desde parámetros
  ├─> Allplan MUESTRA automáticamente los sólidos regenerados ✅
  └─> Sólidos actualizados visibles en el modelo
```

## 7. Cómo Funciona el Mecanismo de Ocultación de Allplan

### Dos Funciones con Propósitos Diferentes

Allplan utiliza **dos funciones diferentes** en el ciclo de vida de un PythonPartGroup:

#### A) `create_element()` (Función Global del Script)
- **Cuándo se llama:**
  - Al crear el PythonPartGroup por primera vez
  - Al regenerar el PythonPartGroup (por ejemplo, cuando cambian parámetros)
  - Al entrar en modo modificación (doble clic)
- **Propósito:** Crear los elementos **finales** del PythonPartGroup (sólidos 3D)
- **Ubicación:** Función global en `Saneamiento.py` (no está implementada en tu código actual)

#### B) `execute()` (Método del ScriptObject)
- **Cuándo se llama:** Durante la edición interactiva
- **Propósito:** Devolver elementos **temporales** para edición (polilíneas)
- **Ubicación:** Método del `PolylineScriptObject` (línea 1824)

### Mecanismo de Ocultación Automático

Cuando haces doble clic en un PythonPartGroup, Allplan ejecuta el siguiente proceso:

1. **Allplan detecta el doble clic** y entra en modo modificación
2. **Allplan llama a `create_element()`** para regenerar el PythonPartGroup
   - Si no existe `create_element()`, Allplan usa los elementos ya creados
3. **Allplan oculta temporalmente** los elementos del PythonPartGroup
   - Esto es **automático** - no requiere código adicional
4. **Allplan inicia el ScriptObject** y llama a `execute()`
   - `execute()` devuelve las polilíneas para edición (líneas 1872-1893)
5. **Allplan muestra solo** lo que devuelve `execute()` (polilíneas)
6. **Al finalizar la edición**, Allplan vuelve a mostrar los elementos del PythonPartGroup

### Cómo Controlarlo desde el Código

**No puedes evitar** que Allplan oculte los sólidos durante la edición - esto es parte del comportamiento del framework. Sin embargo, **sí puedes controlar** qué se muestra durante la edición modificando `execute()`.

#### Opción 1: Mostrar Sólidos Durante la Edición (NO RECOMENDADO)

Podrías modificar `execute()` para generar una vista previa de los sólidos, pero:

- ⚠️ **Muy costoso en rendimiento** - regenerar sólidos en cada frame de edición
- ⚠️ **Puede causar confusión visual** - mezclar sólidos con polilíneas
- ⚠️ **No es el patrón estándar** de Allplan

```python
def execute(self):
    # ⚠️ NO RECOMENDADO: Generar sólidos en execute()
    # Esto sería muy lento y no es el patrón estándar
    
    if is_modification_mode:
        # Generar sólidos desde saved_segments (similar a _finalize_and_create_now)
        # Pero esto sería muy costoso en rendimiento
        pass
```

#### Opción 2: Mantener el Comportamiento Actual (RECOMENDADO)

El comportamiento actual es el **estándar y recomendado**:

- ✅ `execute()` devuelve polilíneas para edición (rápido y claro)
- ✅ Los sólidos se regeneran al finalizar la edición
- ✅ Separación clara entre modo edición y modo visualización

### Resumen del Mecanismo

| Aspecto | Detalle |
|--------|---------|
| **Ocultación automática** | Allplan oculta automáticamente los elementos del PythonPartGroup al entrar en modo edición |
| **No se puede desactivar** | Es parte del framework de Allplan - no hay forma de evitarlo desde el código |
| **Control de visualización** | Puedes controlar qué se muestra durante la edición modificando `execute()` |
| **Regeneración automática** | Al finalizar la edición, Allplan regenera el PythonPartGroup desde los parámetros actualizados |

### Conclusión

La ocultación de los sólidos es un **comportamiento automático del framework de Allplan**. No necesitas código adicional para ocultar los sólidos - Allplan lo hace automáticamente. Tu código solo controla **qué se muestra durante la edición** a través de `execute()`, que devuelve polilíneas para edición (comportamiento estándar y recomendado).

## Código Completo de Referencia

Los métodos clave ya están implementados en `Saneamiento.py`:

- **Línea ~1486:** Llamada a `_restore_saved_state()` en `__init__()`
- **Línea ~1688:** Método `_restore_saved_state()` completo
- **Línea ~1609:** Método `_serialize_state_to_json()`
- **Línea ~1646:** Método `_deserialize_state_from_json()`
- **Línea ~1757:** Método `_save_state_to_build_ele()`
- **Línea ~1790:** Método `_update_pythonpartgroup_state()` - **NUEVO**
- **Línea ~1791:** Método `start_input()` con activación automática
- **Línea ~7101:** Detección de modo modificación en `_finalize_and_create_now()` - **ACTUALIZADO**
- **Línea ~7135:** Guardado del estado en PythonPartGroup (modo creación)


