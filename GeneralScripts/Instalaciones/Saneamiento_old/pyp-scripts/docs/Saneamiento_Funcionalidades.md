En este Archivo se destacan cuales son todas las funcionalidades tanto de la polilinea como de saneamiento, cual es el alcance de todo lo que puede hacer
Este archivo es valido para Saneamiento.py 
No para su versión base.


## 1_ Crear Polilíneas

### Descripción General

La funcionalidad de creación de polilíneas permite al usuario dibujar trayectorias 3D mediante la selección de puntos en el espacio. Las polilíneas pueden ser simples (líneas rectas entre puntos) o complejas (múltiples segmentos conectados).

### Modos de Operación

El sistema opera en dos modos principales controlados por el checkbox "Crear polilínea" (evento 1001):

#### Modo Creación (create_mode = ON)
- **Activación**: Activar el checkbox "Crear polilínea" en la paleta
- 
- **Comportamiento**: Permite agregar nuevos puntos para crear una polilínea activa
- 
- **Características**:
  - Click en espacio vacío → Agrega un nuevo vértice al final de la polilínea activa
  - Click sobre midpoint → Inserta un punto en el segmento existente
  - Click sobre segmento (con modo insertar activo) → Inserta punto en el segmento
  - Drag de vértices activos → Permite mover puntos de la polilínea en edicion
  
  - Snapping automático → Se conecta automáticamente a puntos existentes si están cerca (< HIT_TOL_VERTEX)


--------------------------------------------

#### Modo Edición (create_mode = OFF)
- **Activación**: Desactivar el checkbox "Crear polilínea"
- **Comportamiento**: Permite editar polilíneas ya guardadas
- **Características**:
  - Drag de vértices guardados → Mover puntos de polilíneas existentes
  - Selección por marco → Click en espacio vacío, arrastrar, soltar para seleccionar múltiples segmentos
  - Click en segmento individual → Seleccionar segmento individual
  - Click en midpoint → Insertar punto en segmento guardado
  - Extensión de polilíneas → Conectar nueva polilínea activa a extremos de polilíneas guardadas, lo que hace es visualmente conectar ambas para seguir extendiendo la polilinea
image.png


--------------------------------------------


### Proceso de Creación

#### Paso 1: Activar Modo Creación
1. Activar el checkbox "Crear polilínea" en la paleta (evento 1001)
2. El sistema entra en modo creación (`create_mode = True`)
3. Se muestra un mensaje indicando el modo activo

#### Paso 2: Agregar Puntos
1. **Click en espacio vacío**: Agrega un nuevo punto al final de la polilínea activa
   - El punto se agrega a `self.points[]`
   - Se actualiza `self.current_point`
   - Se muestra preview visual de la polilínea en construcción

2. **Validación de ángulos** (si está activada):
   - Verifica que el mouse esté cerca de la línea propuesta
   - Distancia perpendicular máxima: `MAX_PERP_DIST_MM`
   - Si el mouse está demasiado lejos, se ignora el click

3. **Snapping automático**:
   - Busca puntos existentes en `saved_paths` dentro del radio `HIT_TOL_VERTEX`
   - Si encuentra un punto cercano, ajusta automáticamente la posición
   - Permite uniones automáticas entre polilíneas

#### Paso 3: Inserción de Puntos Intermedios

**Opción A: Click en Midpoint**
- Los midpoints son visibles en cada segmento
- Click directo en el midpoint inserta un punto en esa posición
- Se divide el segmento en dos nuevos segmentos

**Opción B: Click en Segmento (con modo insertar activo)**
- Activar checkbox "Mode Insertar punto"
- Click sobre cualquier segmento proyecta el punto más cercano
- Inserta el punto en la posición proyectada

#### Paso 4: Guardar Polilínea
1. **Guardar sin finalizar** (evento 1002):
   - Guarda la polilínea activa en `saved_paths`
   - Crea segmentos por defecto en `saved_segments`
   - Limpia la polilínea activa para continuar creando
   - Muestra mensaje de confirmación con estadísticas

2. **Finalizar y crear** (evento 1003 / ESC):
   - Guarda la polilínea activa
   - Genera elementos 3D en el documento
   - Entra en modo preview/edición de layers
   - Permite ajustar layers antes de confirmar

### Estructura de Datos

#### Polilínea Activa (en creación)
```python
self.points = []  # Lista de Point3D que forman la polilínea en construcción
self.current_point = Point3D()  # Punto actual del cursor
```

#### Polilíneas Guardadas
```python
self.script_object.saved_paths = [
    [Point3D, Point3D, ...],  # Polilínea 1
    [Point3D, Point3D, ...],  # Polilínea 2
    ...
]
```

#### Segmentos con Información de Sección
```python
self.script_object.saved_segments = [
    {
        'points': [Point3D, Point3D],
        'diameter': 110.0,
        'section_type': '110mm',
        'system': 'Pluvial',
        'label': 'D110 P',
        'installation_type_horizontal': ...,
        'installation_type_vertical': ...,
        'face': ...
    },
    ...
]
```

### Funciones Clave

#### `save_current_polyline()`
- Guarda la polilínea activa en `saved_paths`
- Crea segmentos por defecto con información de sección
- Maneja extensión de polilíneas existentes si `extend_target` está activo
- Muestra confirmación al usuario

#### `_create_default_segments_for_new_path(path_idx)`
- Crea segmentos con sección por defecto para una nueva polilínea
- Lee valores de la paleta (diámetro, sistema, tipo de instalación)
- Asigna etiquetas automáticas según el diámetro y sistema

#### `_insert_on_segment(seg, q, keep_selection_left)`
- Inserta un punto en un segmento existente
- Divide el segmento en dos nuevos segmentos
- Propaga la información de sección a los nuevos segmentos

### Validaciones y Restricciones

1. **Mínimo de puntos**: Se requieren al menos 2 puntos para crear una polilínea válida
2. **Validación de ángulos**: Si está activada, verifica proximidad del mouse a la línea propuesta
3. **Tolerancia de snapping**: `HIT_TOL_VERTEX` define el radio de detección para uniones automáticas
4. **Distancia perpendicular máxima**: `MAX_PERP_DIST_MM` limita la desviación permitida del ángulo propuesto

### Flujo Completo de Creación

```
1. Usuario activa "Crear polilínea" (checkbox)
   ↓
2. Sistema entra en create_mode = True
   ↓
3. Usuario hace click en espacio vacío
   ↓
4. Sistema agrega punto a self.points[]
   ↓
5. Sistema muestra preview visual
   ↓
6. Usuario agrega más puntos (pasos 3-5)
   ↓
7. Usuario presiona "Guardar" (1002) o "Finalizar" (1003)
   ↓
8. Sistema guarda en saved_paths y crea segmentos en saved_segments
   ↓
9. Si finalizar: Sistema genera elementos 3D y entra en modo preview
```

### Características Avanzadas

#### Extensión de Polilíneas
- Permite extender polilíneas guardadas desde sus extremos
- Se detecta automáticamente cuando el primer punto de la activa está cerca de un extremo
- Fusiona la nueva polilínea con la existente

#### Unión Automática de Paths
- Al finalizar, el sistema une automáticamente paths consecutivos que se tocan
- Usa tolerancia de 1e-3 mm para detectar puntos coincidentes
- Reduce el número de polilíneas guardadas

#### Persistencia de Estado
- El estado se guarda en `build_ele` usando JSON serialization
- Se restaura automáticamente al editar una instancia existente
- Permite continuar trabajando después de cerrar/reabrir

### Comandos de la Paleta

- **1001**: Toggle "Crear polilínea" (ON/OFF)
- **1002**: Guardar polilínea activa (sin finalizar)
- **1003**: Finalizar y crear elementos (ESC también funciona)
- **1004**: Borrar segmento seleccionado/hover
- **1007**: Aplicar sección a segmentos seleccionados
- **1009**: Aplicar layers a segmentos seleccionados
- **1010**: Invertir flechas en segmentos seleccionados
- **1011**: Aplicar atributos a segmentos seleccionados

### Notas Técnicas

- Los puntos se almacenan como `AllplanGeo.Point3D`
- Las polilíneas se crean usando `AllplanGeo.Polyline3D()`
- Los elementos se generan como `AllplanBasisElements.ModelElement3D`
- El sistema usa coordenadas 3D (X, Y, Z) para todas las operaciones
- La visualización en tiempo real usa preview elements que se actualizan dinámicamente

---

## 2_ Cambio de Diámetros entre Secciones

### Descripción General

El sistema permite cambiar el diámetro de los tubos a lo largo de una polilínea. Cuando se detecta un cambio de diámetro entre segmentos consecutivos, el sistema crea automáticamente un **reductor** (elemento de transición) para conectar los dos diámetros diferentes.

### Aplicación Manual de Diámetros

#### Método 1: Aplicar Diámetro a Segmentos Seleccionados

1. **Seleccionar segmento(s)**:
   - Click en un segmento individual de polilínea guardada
   - O arrastrar para crear un marco de selección (selección múltiple)

2. **Seleccionar diámetro en la paleta**:
   - Usar el control "Diámetro a Aplicar" según el tipo de saneamiento:
     - **Pluvial**: Control "DiametroAplicarPluvial"
     - **Fecal**: Control "DiametroAplicarFecal"
   - O usar "Diámetro Personalizado" para valores específicos

3. **Aplicar diámetro** (evento 1007):
   - Presionar el botón "Aplicar Sección" o evento 1007
   - El diámetro se actualiza en `saved_segments`
   - Se actualiza la etiqueta del segmento (ej: "D110 P", "D40 F")

#### Función: `apply_section_to_selected()`
- Aplica el diámetro seleccionado en la paleta a los segmentos seleccionados
- Soporta selección individual o múltiple (por marco)
- Actualiza la información de sección sin modificar layers

### Detección Automática de Reductores

El sistema detecta automáticamente cambios de diámetro y crea reductores en los siguientes casos:

#### Condiciones para Crear Reductores

1. **Segmentos colineales (rectos)**:
   - Los segmentos deben ser casi colineales (mismo eje)
   - Tolerancia: `abs(dot_product) >= 0.999`
   - No se crean reductores en codos (ángulos)

2. **Cambios de diámetro soportados**:
   - **25mm ↔ 40mm**: Reductor tipo 0 (R40-25mm)
   - **40mm ↔ 110mm**: Reductor tipo 2 (R110-40mm)
   - **110mm ↔ 25mm**: ❌ NO soportado (sin reductor)

#### Proceso de Detección

```python
# Para cada vértice intermedio en la polilínea:
for i in range(1, len(pts) - 1):
    pa, pb, pc = pts[i-1], pts[i], pts[i+1]
    
    # Obtener diámetros de segmentos adyacentes
    d1 = diámetro del segmento (pa -> pb)
    d2 = diámetro del segmento (pb -> pc)
    
    # Verificar si son colineales
    v1 = vector normalizado (pb - pa)
    v2 = vector normalizado (pc - pb)
    dot_product = producto punto (v1, v2)
    is_straight = abs(dot_product) >= 0.999
    
    # Detectar cambios de diámetro
    if is_straight and cambio_detectado:
        crear_reductor()
```

### Tipos de Reductores Soportados

#### 1. Reductor 40mm → 25mm (Tipo 0)

**Configuración**:
- **Recortes**:
  - `REDUCER_40_25_TRIM_IN = 0.0 mm` (lado 40mm)
  - `REDUCER_40_25_TRIM_OUT = 0.0 mm` (lado 25mm)
- **Pivote**: (-20.0, -12.5, -12.0) mm
- **Rotaciones extra**: (0°, 0°, 0°)

**Uso**: Transición de 40mm a 25mm en segmentos rectos

#### 2. Reductor 25mm → 40mm (Tipo 0, Invertido)

**Configuración**:
- **Recortes**:
  - `REDUCER_25_40_TRIM_IN = -40.0 mm` (lado 25mm)
  - `REDUCER_25_40_TRIM_OUT = 32.0 mm` (lado 40mm)
- **Pivote**: (-28.0, -12.5, -12.0) mm
- **Rotaciones extra**: (0°, 0°, 0°)

**Uso**: Transición de 25mm a 40mm en segmentos rectos

#### 3. Reductor 110mm → 40mm (Tipo 2)

**Configuración**:
- **Recortes**:
  - `REDUCER_110_40_TRIM_IN = 103.65 mm` (lado 110mm)
  - `REDUCER_110_40_TRIM_OUT = 61.25 mm` (lado 40mm)
- **Pivote**: (55.0, -95.0, 55.0) mm
- **Rotaciones extra**: (-90°, 0°, 0°)

**Uso**: Transición de 110mm a 40mm en segmentos rectos

#### 4. Reductor 40mm → 110mm (Tipo 2, Invertido)

**Configuración**:
- **Recortes** (invertidos):
  - `REDUCER_110_40_TRIM_OUT = 61.25 mm` (lado 40mm)
  - `REDUCER_110_40_TRIM_IN = 103.65 mm` (lado 110mm)
- **Pivote**: (55.0, -95.0, 55.0) mm
- **Rotaciones extra**: (-90°, 0°, 0°)

**Uso**: Transición de 40mm a 110mm en segmentos rectos

### Reductores Después de Codos

Cuando hay un cambio simultáneo de **ángulo** (codo) y **diámetro** en el mismo vértice, el sistema coloca el reductor después del codo con un espaciado adicional.

#### Configuración de Espaciado

- **Reductores 110mm→40mm después de codos**:
  - `REDUCER_AFTER_ELBOW_SPACING_110MM = 10.0 mm`
  - Pivote ajustado: (55.0, -95.0, 55.0) mm

- **Reductores 40mm→25mm después de codos**:
  - `REDUCER_AFTER_ELBOW_SPACING_40MM = 10.0 mm`
  - Pivote ajustado: (-60.0, -12.5, -12.0) mm

#### Proceso

1. Se detecta un codo en el vértice
2. Se verifica si hay cambio de diámetro
3. Si ambos ocurren, se coloca el codo primero
4. Luego se coloca el reductor con el espaciado adicional

### Aplicación de Recortes

Cuando se detecta un reductor, el sistema aplica recortes automáticos a los tubos adyacentes:

#### Ejemplo: Reductor 40mm → 25mm

```python
# Segmento entrante (40mm)
end_trims[i-1] = max(end_trims[i-1], REDUCER_40_25_TRIM_IN)  # 0.0 mm

# Segmento saliente (25mm)
start_trims[i] = max(start_trims[i], REDUCER_40_25_TRIM_OUT)  # 0.0 mm
```

Los recortes aseguran que los tubos no se superpongan con el reductor y que la conexión sea precisa.

### Limitaciones y Restricciones

#### Cambios NO Soportados

- **110mm ↔ 25mm**: 
  - ❌ NO se crea reductor automáticamente
  - Los segmentos se crean con sus diámetros respectivos
  - No hay elemento de transición
  - **Nota**: Las constantes existen en el código pero no se utilizan

#### Cambios Soportados

- ✅ **25mm ↔ 40mm**: Reductor tipo 0
- ✅ **40mm ↔ 110mm**: Reductor tipo 2

### Flujo Completo de Cambio de Diámetro

```
1. Usuario crea polilínea con puntos
   ↓
2. Usuario aplica diferentes diámetros a segmentos (evento 1007)
   ↓
3. Sistema guarda diámetros en saved_segments
   ↓
4. Al finalizar (evento 1003), sistema analiza vértices
   ↓
5. Para cada vértice intermedio:
   a. Obtiene diámetros de segmentos adyacentes
   b. Verifica si son colineales (rectos)
   c. Si hay cambio de diámetro soportado:
      - Aplica recortes a tubos
      - Registra reductor para colocar
   ↓
6. Sistema coloca reductores en posiciones registradas
   ↓
7. Genera elementos 3D (tubos + reductores)
```

### Ejemplos de Uso

#### Ejemplo 1: Cambio Simple 110mm → 40mm

```
Polilínea: P1(110mm) → P2 → P3(40mm)
           [Tubo 110mm] [Reductor] [Tubo 40mm]
```

#### Ejemplo 2: Cambio 40mm → 25mm → 40mm

```
Polilínea: P1(40mm) → P2 → P3(25mm) → P4 → P5(40mm)
           [Tubo 40mm] [R40-25] [Tubo 25mm] [R25-40] [Tubo 40mm]
```

#### Ejemplo 3: Cambio con Codo

```
Polilínea: P1(110mm) → P2(110mm, codo 90°) → P3(40mm)
           [Tubo 110mm] [Codo 90°] [Espacio 10mm] [Reductor] [Tubo 40mm]
```

### Funciones Clave

#### `apply_section_to_selected()`
- Aplica diámetro desde la paleta a segmentos seleccionados
- Actualiza `saved_segments` con nuevo diámetro y etiqueta

#### `_apply_diameter_to_segment(path_idx, seg_idx, diameter)`
- Actualiza o crea información de segmento con nuevo diámetro
- Mantiene configuración de layers si `apply_layers=False`
- Genera etiqueta automática según diámetro y sistema

#### `_find_diameter_for_segment(p1, p2)`
- Busca el diámetro asignado a un segmento específico
- Consulta `saved_segments` para encontrar coincidencia
- Retorna diámetro por defecto si no se encuentra

### Configuración de Reductores

Todas las constantes de configuración están definidas en las líneas 986-1076 del código:

- **Recortes** (`TRIM_IN`, `TRIM_OUT`): Ajustan longitud de tubos adyacentes
- **Pivotes** (`PIVOT_X`, `PIVOT_Y`, `PIVOT_Z`): Punto de referencia para posicionamiento
- **Offsets** (`OFFSET_X`, `OFFSET_Y`, `OFFSET_Z`): Ajustes finos de posición
- **Rotaciones extra** (`EXTRA_ROT_X`, `EXTRA_ROT_Y`, `EXTRA_ROT_Z`): Rotaciones adicionales

### Notas Técnicas

- Los reductores se detectan **solo en segmentos rectos** (colineales)
- Los cambios de diámetro en **codos** requieren colocación manual después del codo
- El sistema usa **tolerancia de 1e-3 mm** para comparar diámetros
- Los recortes se aplican usando `max()` para preservar recortes existentes (de codos, bifurcaciones, etc.)
- Los reductores se numeran automáticamente si el sistema de numeración está activo

---

## 3_ Bifurcaciones

### Descripción General

Las bifurcaciones son elementos que permiten dividir una línea de saneamiento en dos o más ramas. El sistema detecta automáticamente puntos donde múltiples polilíneas se conectan y crea el elemento de bifurcación apropiado según los diámetros involucrados.

### Detección Automática de Bifurcaciones

#### Condiciones para Crear Bifurcaciones

1. **Punto de conexión múltiple**:
   - Al menos 2 polilíneas diferentes se conectan en el mismo punto
   - El punto debe estar entre segmentos **rectos** (colineales)
   - **NO** se crean bifurcaciones en codos (puntos con ángulos)

2. **Validación de colinealidad**:
   - Los segmentos adyacentes al punto deben ser casi colineales
   - Tolerancia de ángulo: `angle_tolerance_deg = 10.0°`
   - Si el ángulo es < 10° o > 170°, se considera recto

3. **Tolerancia de posición**:
   - Los puntos se redondean a 1mm para agrupar conexiones cercanas
   - `point_key = (round(X, 0), round(Y, 0), round(Z, 0))`

#### Proceso de Detección

```python
# 1. Recorrer todos los segmentos de todas las polilíneas
for path_idx, pts in enumerate(saved_paths):
    for seg_idx in range(len(pts) - 1):
        p1, p2 = pts[seg_idx], pts[seg_idx + 1]
        
        # 2. Verificar si p1 está entre segmentos rectos
        if seg_idx > 0:
            p_prev = pts[seg_idx - 1]
            if are_segments_straight(p_prev, p1, p2):
                # Agregar a bifurcation_points
                bifurcation_points[p1_key].append((path_idx, seg_idx, True))
        
        # 3. Verificar si p2 está entre segmentos rectos
        if seg_idx < len(pts) - 2:
            p_next = pts[seg_idx + 2]
            if are_segments_straight(p1, p2, p_next):
                # Agregar a bifurcation_points
                bifurcation_points[p2_key].append((path_idx, seg_idx, False))

# 4. Filtrar puntos con múltiples polilíneas
for point_key, connections in bifurcation_points.items():
    unique_paths = set(conn[0] for conn in connections)
    if len(unique_paths) >= 2:  # Bifurcación real
        crear_bifurcacion()
```

### Tipos de Bifurcaciones Soportadas

El sistema detecta automáticamente el tipo de bifurcación según los diámetros de los segmentos conectados:

#### 1. Bifurcación D110-D110 (Derivación 45°)

**Detección**:
- Al menos un segmento de 110mm conectado en el punto
- **NO** hay segmentos de 40mm en la bifurcación
- Usa modelo: `BifurcacionDerivacion45` con `TipoTubo=0`

**Configuración**:
- **Rama Izquierda**:
  - Offset: (55.0, 170.0, -55.0) mm
  - Rotaciones: (180°, 0°, 90°) + rotación base Z
- **Rama Derecha**:
  - Offset: (55.0, 170.0, -55.0) mm
  - Rotaciones: (0°, 0°, -90°) + rotación base Z

**Recortes**:
- Tubo principal: `BIF110_MAIN_TRIM_IN = 140.0 mm`, `BIF110_MAIN_TRIM_OUT = 47.0 mm`
- Rama: `BIF110_BRANCH_TRIM_IN = 148.0 mm`, `BIF110_BRANCH_TRIM_OUT = 0.0 mm`

#### 2. Bifurcación D110-D40 (Conjunto Reducción)

**Detección**:
- Al menos un segmento de 110mm **Y** un segmento de 40mm conectados
- Usa modelo: `ConjuntosReduccion` con `TipoTubo=0`

**Configuración**:
- **Rama Izquierda**:
  - Offset: (-150.78, -79.22, 50.0) mm
  - Rotaciones: (180°, 0°, 90°) + rotación base Z
- **Rama Derecha**:
  - Offset: (-150.78, -79.22, 50.0) mm
  - Rotaciones: (0°, 0°, -90°) + rotación base Z

**Recortes**:
- Tubo principal D110: `BIF110_40_MAIN_TRIM_IN = 109.60 mm`, `BIF110_40_MAIN_TRIM_OUT = 2.00 mm`
- Rama D40: `BIF110_40_BRANCH_TRIM_IN = 111.0 mm`, `BIF110_40_BRANCH_TRIM_OUT = 0.0 mm`

**Nota**: En bifurcaciones D110-D40, el tubo de 40mm es **siempre** la rama.

#### 3. Bifurcación D40-D40 (Derivación 45°)

**Detección**:
- Al menos un segmento de 40mm conectado en el punto
- **NO** hay segmentos de 110mm en la bifurcación
- Usa modelo: `BifurcacionDerivacion45` con `TipoTubo=2`

**Configuración**:
- **Rama Izquierda**:
  - Offset: (20.0, 100.0, -20.0) mm
  - Rotaciones: (180°, 0°, 90°) + rotación base Z
- **Rama Derecha**:
  - Offset: (20.0, 100.0, -20.0) mm
  - Rotaciones: (0°, 0°, -90°) + rotación base Z

**Recortes**:
- Tubo principal: `BIF40_MAIN_TRIM_IN = 71.0 mm`, `BIF40_MAIN_TRIM_OUT = 30.0 mm`
- Rama: `BIF40_BRANCH_TRIM_IN = 70.6 mm`, `BIF40_BRANCH_TRIM_OUT = 0.0 mm`

### Determinación de Tubo Principal vs Rama

El sistema determina automáticamente qué segmento es el "tubo principal" (continúa recto) y cuál es la "rama" (sale en 45°):

#### Lógica de Determinación

1. **Bifurcación D110-D40**:
   - El tubo de **110mm** es siempre el principal
   - El tubo de **40mm** es siempre la rama

2. **Bifurcación D110-D110 o D40-D40**:
   - Compara la **longitud de las polilíneas** conectadas
   - La polilínea más larga → tubo principal
   - Si tienen la misma longitud, usa el `path_idx` menor → tubo principal

```python
# Ejemplo de lógica
current_path_len = len(saved_paths[path_idx])
is_main_tube = True

for other_path_idx in unique_paths:
    if other_path_idx != path_idx:
        other_path_len = len(saved_paths[other_path_idx])
        if other_path_len > current_path_len:
            is_main_tube = False  # Otra polilínea es más larga
            break
        elif other_path_len == current_path_len and other_path_idx < path_idx:
            is_main_tube = False  # Misma longitud, pero otro path tiene índice menor
            break
```

### Orientación y Rotación de Bifurcaciones

#### Cálculo de Rotación Base

1. **Vector del tubo principal**:
   - Se normaliza el vector del segmento principal
   - Se calcula el ángulo en el plano XY: `angle_main = atan2(Y, X)`

2. **Determinación de lado (izquierda/derecha)**:
   - **Segmentos horizontales**: Producto cruzado en Z
     ```python
     cross_z = main_vector.X * branch_vector.Y - main_vector.Y * branch_vector.X
     ```
   - **Segmentos verticales**: Componente X de la rama
     ```python
     cross_z = -branch_vector.X  # X positivo = derecha
     ```
   - `cross_z > 0` → Rama a la izquierda
   - `cross_z < 0` → Rama a la derecha

3. **Rotación final**:
   ```python
   base_rot_z = math.degrees(angle_main)
   rot_z = base_rot_z + BIFURCATION_ROT_Z_LEFT/RIGHT
   ```

#### Bifurcaciones Verticales

Cuando el segmento principal es **vertical**, se aplican rotaciones adicionales:

**Detección de verticalidad**:
```python
dz_abs = abs(main_vector.Z)
dxy = (main_vector.X**2 + main_vector.Y**2) ** 0.5
is_vertical = dz_abs > 0.707 and dxy < 0.707  # ~45° threshold
```

**Rotaciones adicionales**:
- **D110-D110 Vertical**:
  - Izquierda: (-270°, 0°, -180°)
  - Derecha: (270°, 0°, 180°)
- **D110-D40 Vertical**:
  - Izquierda: (0°, 0°, 0°) - Sin rotaciones adicionales
  - Derecha: (0°, 0°, 0°) - Sin rotaciones adicionales
- **D40-D40 Vertical**:
  - Izquierda: (-270°, 0°, -180°)
  - Derecha: (270°, 0°, 180°)

**Dirección de la rama**:
- Si `branch_vector.Z > 0` → Rama apunta hacia arriba (rotaciones normales)
- Si `branch_vector.Z < 0` → Rama apunta hacia abajo (rotaciones invertidas)

### Aplicación de Recortes

Los recortes se aplican automáticamente a los tubos conectados a la bifurcación:

#### Recortes en Tubo Principal

- **Inicio del segmento** (`s_trim`): Se suma `BIF*_MAIN_TRIM_IN`
- **Fin del segmento** (`e_trim`): Se suma `BIF*_MAIN_TRIM_OUT`

#### Recortes en Rama

- **Inicio del segmento** (`s_trim`): Se suma `BIF*_BRANCH_TRIM_IN`
- **Fin del segmento** (`e_trim`): Se suma `BIF*_BRANCH_TRIM_OUT`

#### Ejemplo: Bifurcación D40-D40

```python
# Para un segmento de 40mm que es el tubo principal
if p1_key in bifurcation_points:
    connections = bifurcation_points[p1_key]
    unique_paths = set(conn[0] for conn in connections)
    if len(unique_paths) >= 2:  # Es bifurcación
        if is_main_tube:
            s_trim += BIF40_MAIN_TRIM_IN  # 71.0 mm
        else:
            s_trim += BIF40_BRANCH_TRIM_IN  # 70.6 mm
```

### Flujo Completo de Creación de Bifurcaciones

```
1. Usuario crea múltiples polilíneas que se conectan en un punto
   ↓
2. Al finalizar (evento 1003), sistema analiza todos los puntos
   ↓
3. Para cada punto:
   a. Agrupa segmentos que se conectan (tolerancia 1mm)
   b. Verifica si hay al menos 2 polilíneas diferentes
   c. Verifica que los segmentos sean rectos (no codos)
   ↓
4. Si es bifurcación válida:
   a. Identifica diámetros de segmentos conectados
   b. Determina tipo de bifurcación (D110-D110, D110-D40, D40-D40)
   c. Identifica tubo principal vs rama
   ↓
5. Calcula orientación:
   a. Vector del tubo principal (normalizado)
   b. Vector de la rama (normalizado)
   c. Determina lado (izquierda/derecha)
   d. Calcula rotaciones base + adicionales si es vertical
   ↓
6. Aplica recortes a tubos conectados
   ↓
7. Crea elemento de bifurcación con orientación calculada
   ↓
8. Coloca bifurcación en el punto de conexión
```

### Ejemplos de Uso

#### Ejemplo 1: Bifurcación Simple D110-D110

```
Polilínea 1: P1 → P2 → P3 (110mm)
Polilínea 2: P2 → P4 → P5 (110mm)

Punto P2: Bifurcación D110-D110
- Polilínea 1 (más larga) → Tubo principal
- Polilínea 2 → Rama (45°)
```

#### Ejemplo 2: Bifurcación D110-D40

```
Polilínea 1: P1 → P2 → P3 (110mm)
Polilínea 2: P2 → P4 → P5 (40mm)

Punto P2: Bifurcación D110-D40
- Polilínea 1 (110mm) → Tubo principal
- Polilínea 2 (40mm) → Rama (siempre)
```

#### Ejemplo 3: Bifurcación Vertical

```
Polilínea 1: P1(0,0,0) → P2(0,0,3000) (110mm, vertical)
Polilínea 2: P2 → P3(2000,0,3000) (110mm, horizontal)

Punto P2: Bifurcación D110-D110 Vertical
- Rotaciones adicionales aplicadas según dirección de la rama
```

### Limitaciones y Restricciones

#### Bifurcaciones NO Soportadas

- **Bifurcaciones en codos**: No se crean bifurcaciones en puntos que forman ángulos
- **Bifurcaciones con 25mm**: No hay soporte específico para bifurcaciones que involucren solo 25mm
- **Más de 2 ramas**: El sistema detecta múltiples conexiones pero usa el modelo de 2 ramas

#### Bifurcaciones Soportadas

- ✅ **D110-D110**: Derivación 45° entre dos tubos de 110mm
- ✅ **D110-D40**: Conjunto reducción de 110mm a 40mm
- ✅ **D40-D40**: Derivación 45° entre dos tubos de 40mm

### Funciones Clave

#### `are_segments_straight(p_prev, p_middle, p_next)`
- Verifica si dos segmentos consecutivos son colineales
- Calcula el ángulo entre vectores
- Retorna `True` si el ángulo es < 10° o > 170°

#### Detección de bifurcaciones (en `_finalize_and_create_now`)
- Agrupa puntos de conexión con tolerancia de 1mm
- Filtra puntos con múltiples polilíneas
- Identifica tipo de bifurcación según diámetros

#### Cálculo de orientación
- Calcula vectores normalizados del tubo principal y rama
- Determina lado usando producto cruzado
- Aplica rotaciones base + adicionales para verticales

### Configuración de Bifurcaciones

Todas las constantes están definidas en las líneas 1079-1209 del código:

- **Offsets** (`OFFSET_X/Y/Z_LEFT/RIGHT`): Posición de la rama relativa al punto de conexión
- **Rotaciones** (`ROT_X/Y/Z_LEFT/RIGHT`): Rotaciones base para orientar la bifurcación
- **Rotaciones verticales** (`VERTICAL_ROT_X/Y/Z_LEFT/RIGHT`): Rotaciones adicionales para segmentos verticales
- **Recortes** (`MAIN/BRANCH_TRIM_IN/OUT`): Longitudes de recorte para tubos conectados

### Notas Técnicas

- Las bifurcaciones se detectan **solo en segmentos rectos** (colineales)
- El sistema usa **tolerancia de 1mm** para agrupar puntos cercanos
- Los recortes se aplican usando **suma** (`+=`) para acumular con otros recortes
- Las bifurcaciones **NO se numeran** automáticamente (a diferencia de los tubos)
- El sistema detecta automáticamente si el segmento principal es vertical y ajusta las rotaciones
- La dirección de la rama (arriba/abajo) afecta las rotaciones en bifurcaciones verticales

---

## 4_ Selección de Segmentos

### Descripción General

El sistema ofrece dos métodos para seleccionar segmentos de polilíneas guardadas: **selección individual** (click en segmento) y **selección por marco** (arrastrar rectángulo). Ambos métodos permiten aplicar operaciones a múltiples segmentos simultáneamente.

### Selección Individual

#### Método
1. **Click en segmento**: Click directo sobre un segmento de polilínea guardada
2. **Toggle**: Click nuevamente en el mismo segmento para deseleccionarlo
3. **Cambio de selección**: Click en otro segmento cambia la selección

#### Características
- Solo un segmento seleccionado a la vez
- El segmento seleccionado se muestra en color azul (color 5)
- Se almacena en `self.selected_seg = (kind, path_idx, seg_idx)`
- Compatible con operaciones: aplicar diámetro, layers, atributos, invertir flechas

#### Uso
```python
# Al hacer click en un segmento guardado
if self.hover_seg is not None:
    if self._seg_equal(self.selected_seg, self.hover_seg):
        self.selected_seg = None  # Deseleccionar
    else:
        self.selected_seg = self.hover_seg  # Seleccionar
```

### Selección por Marco

#### Método
1. **Iniciar selección**: Click en espacio vacío (sin segmentos ni vértices)
2. **Arrastrar**: Mantener presionado y arrastrar para crear un rectángulo
3. **Finalizar**: Soltar el mouse para completar la selección
4. **Resultado**: Todos los segmentos cuyos extremos estén dentro del rectángulo se seleccionan

#### Condiciones para Activar

La selección por marco solo está disponible cuando:
- `create_mode = False` (modo edición activo)
- No hay drag activo (`is_dragging = False`, `saved_dragging = None`)
- No hay extensión activa (`extend_target = None`)
- No hay polilínea activa en creación (`self.points` está vacío)

#### Proceso de Selección

```python
# 1. Iniciar selección
if not self.box_selecting:
    self.box_selecting = True
    self.box_start = Point3D(current_pnt)  # Esquina inicial
    self.box_curr = Point3D(current_pnt)    # Esquina actual

# 2. Durante arrastre (actualizar box_curr)
self.box_curr = Point3D(current_pnt)

# 3. Finalizar selección
if self.box_selecting:
    sel = set()
    for path_idx, pts in enumerate(saved_paths):
        for seg_idx in range(len(pts) - 1):
            a, b = pts[seg_idx], pts[seg_idx + 1]
            # Verificar si ambos extremos están en el rectángulo
            if (_point_in_rect_xy(a, box_start, box_curr) and 
                _point_in_rect_xy(b, box_start, box_curr)):
                sel.add(('saved', path_idx, seg_idx))
    self.selected_segments = sel
```

#### Validación de Rectángulo

- El rectángulo debe tener área > 0 (no puede ser un punto)
- Si el rectángulo es inválido, se limpia la selección
- Los puntos se proyectan al plano de la vista actual para funcionar en cualquier orientación

#### Función: `_point_in_rect_xy(p, a, b)`

```python
# Proyecta puntos 3D al plano 2D de la vista
view_proj = coord_input.GetViewWorldProjection()
p_view = view_proj.WorldToView(p)
a_view = view_proj.WorldToView(a)
b_view = view_proj.WorldToView(b)

# Compara en coordenadas 2D de la vista
xmin, xmax = min(a_view.X, b_view.X), max(a_view.X, b_view.X)
ymin, ymax = min(a_view.Y, b_view.Y), max(a_view.Y, b_view.Y)

return (xmin <= p_view.X <= xmax) and (ymin <= p_view.Y <= ymax)
```

#### Características
- Múltiples segmentos seleccionados simultáneamente
- Los segmentos seleccionados se muestran en color marrón (color 9)
- Se almacenan en `self.selected_segments = set()` de tuplas `(kind, path_idx, seg_idx)`
- Compatible con todas las operaciones: aplicar diámetro, layers, atributos, borrar, invertir flechas

#### Visualización
- **Marco de selección**: Se dibuja un rectángulo en color 8 durante el arrastre
- **Segmentos seleccionados**: Se resaltan en color 9 (marrón) después de finalizar

### Operaciones con Selección

#### Aplicar a Segmentos Seleccionados

Todas las operaciones soportan ambos tipos de selección:

1. **Aplicar Diámetro** (evento 1007):
   ```python
   if self.selected_segments:
       for kind, path_idx, seg_idx in self.selected_segments:
           _apply_diameter_to_segment(path_idx, seg_idx, diameter)
   elif self.selected_seg:
       _apply_diameter_to_segment(path_idx, seg_idx, diameter)
   ```

2. **Aplicar Layers** (evento 1009):
   - Aplica configuración de instalación (horizontal/vertical, cara) a segmentos seleccionados

3. **Aplicar Atributos** (evento 1011):
   - Aplica valor de atributo personalizado a segmentos seleccionados

4. **Invertir Flechas** (evento 1010):
   - Invierte dirección de flechas en segmentos seleccionados

5. **Borrar Segmentos** (evento 1004):
   - Si hay selección por marco: borra todos los segmentos seleccionados
   - Si hay selección individual: borra el segmento seleccionado

### Toggle de Selección Múltiple

Cuando hay segmentos seleccionados por marco, hacer click en un segmento individual:
- Si el segmento **ya está** en la selección → Se quita de la selección
- Si el segmento **no está** en la selección → Se agrega a la selección

Esto permite ajustar la selección por marco con clicks individuales.

### Limpieza de Selección

La selección se limpia automáticamente cuando:
- Se cambia a modo creación (`create_mode = True`)
- Se inicia un drag de vértice
- Se inicia una extensión de polilínea
- Se llama a `_clear_box_selection_state()`

---

## 5_ Modo Edición de Layers

### Descripción General

El modo **Edición de Layers** permite ajustar los layers de los elementos generados (tubos, codos, bifurcaciones, reductores) antes de finalizar y crear los PythonParts definitivos. Es un modo de dos pasos que se activa automáticamente al presionar "Finalizar" (evento 1003).

### Flujo de Dos Pasos

#### Paso 1: Generar Elementos para Preview

1. Usuario presiona "Finalizar" (evento 1003 / ESC)
2. Sistema guarda la polilínea activa si existe
3. Sistema entra en `preview_mode = True`
4. Sistema genera todos los elementos en `generated_elements[]`:
   - Tubos
   - Codos
   - Bifurcaciones
   - Reductores
5. Se muestra mensaje: "Click en elementos para cambiar layer. Presione 'Finalizar y crear' para confirmar."

#### Paso 2: Finalizar y Crear

1. Usuario ajusta layers haciendo click en elementos
2. Usuario presiona "Finalizar y crear" nuevamente
3. Sistema aplica `layer_overrides` a los elementos
4. Sistema crea PythonParts definitivos con los layers ajustados
5. Sistema sale de `preview_mode`

### Generación de Elementos para Preview

#### Función: `_generate_elements_for_preview()`

Genera todos los elementos que se crearán y los almacena en `self.generated_elements[]`:

```python
generated_elements = [
    {
        'type': 'tube' | 'elbow' | 'bifurcation' | 'reducer',
        'key': ('tube', path_idx, seg_idx),  # ID único
        'geometry': Line3D | Polyhedron3D,    # Geometría para visualización
        'position': Point3D,                  # Posición del elemento
        'layer': int,                          # Layer calculado automáticamente
        'path_idx': int,                       # Índice de polilínea
        'seg_idx': int                         # Índice de segmento
    },
    ...
]
```

#### Cálculo Automático de Layers

Los layers se calculan automáticamente según:
- **Orientación del segmento** (horizontal vs vertical)
- **Configuración de instalación** del segmento:
  - Horizontal: FABRICA (40148) o OBRA (40149)
  - Vertical: TD (40061), EN cara X (40106), EN cara Y (40108), IS (40061)

```python
def _calculate_layer_from_orientation(p1, p2):
    dx, dy, dz = p2.X - p1.X, p2.Y - p1.Y, p2.Z - p1.Z
    len_xy = (dx*dx + dy*dy) ** 0.5
    dz_abs = abs(dz)
    
    is_horizontal = len_xy > 1e-6 and dz_abs < 50.0
    is_vertical = dz_abs > 50.0 and len_xy < 50.0
    
    if is_horizontal:
        install_h = seg_info.get('installation_type_horizontal', 'OBRA')
        return 40148 if install_h == 'FABRICA' else 40149
    elif is_vertical:
        install_v = seg_info.get('installation_type_vertical', 'TD')
        face = seg_info.get('face', 'X')
        if install_v == 'EN':
            return 40106 if face == 'X' else 40108
        else:
            return 40061
```

### Selección de Elementos en Preview

#### Click en Elemento

1. Usuario hace click en un elemento (tubo, codo, bifurcación, reductor)
2. Sistema detecta qué elemento fue clickeado usando `_point_in_rect_xy()`
3. Sistema almacena el ID del elemento en `self.selected_element_id`
4. Sistema resalta el elemento en color amarillo (color 2)

#### Aplicar Layer a Elemento Seleccionado

1. Usuario configura tipo de instalación en la paleta:
   - Tipo Instalación Horizontal: FABRICA / OBRA
   - Tipo Instalación Vertical: TD / EN / IS
   - Cara EN: X / Y
2. Usuario presiona "Aplicar Layers" (evento 1009)
3. Sistema determina el layer correcto según la configuración
4. Sistema almacena el override en `self.layer_overrides[element_id] = nuevo_layer`
5. Sistema actualiza la visualización

### Aplicación de Layer Overrides

Cuando se finaliza y crea, los overrides se aplican:

```python
# En _finalize_and_create_now()
tube_key = ('tube', path_idx, i)
if tube_key in layer_overrides:
    override_layer = layer_overrides[tube_key]
    seg_prop.Layer = override_layer
    # Recrear elemento con nuevo layer
    tube_element = ModelElement3D(seg_prop, brep_w)
```

### Visualización en Preview

- **Elementos normales**: Se muestran con su layer calculado automáticamente
- **Elemento seleccionado**: Se resalta en color amarillo (color 2)
- **Elementos con override**: Se muestran con el layer modificado

### Información de Secciones

La función `show_sections_info()` muestra estadísticas:
- Total de polilíneas guardadas
- Total de segmentos con sección configurada
- Distribución por diámetro
- Distribución por layers (horizontal/vertical, tipo de instalación)

---

## 6_ Estados de Polilíneas: Guardadas vs Activas

### Descripción General

El sistema mantiene dos estados distintos para las polilíneas: **polilíneas guardadas** (persistentes) y **polilínea activa** (temporal, en creación). Esta separación permite crear múltiples polilíneas y editarlas independientemente.

### Polilíneas Guardadas (saved_paths)

#### Características
- **Persistencia**: Se guardan en `self.script_object.saved_paths[]`
- **Estado**: Permanente hasta que se borren explícitamente
- **Edición**: Se pueden editar (drag vértices, insertar puntos, borrar segmentos)
- **Selección**: Se pueden seleccionar segmentos individuales o por marco
- **Operaciones**: Se pueden aplicar diámetros, layers, atributos

#### Estructura
```python
saved_paths = [
    [Point3D, Point3D, Point3D, ...],  # Polilínea 1
    [Point3D, Point3D, ...],            # Polilínea 2
    ...
]
```

#### Guardado
- Se guardan con el evento 1002 ("Guardar") o 1003 ("Finalizar")
- Se crean automáticamente segmentos por defecto en `saved_segments`
- Se pueden guardar múltiples polilíneas independientes

### Polilínea Activa (points)

#### Características
- **Temporalidad**: Se almacena en `self.points[]` (solo existe durante la creación)
- **Estado**: Temporal, se limpia al guardar o cancelar
- **Creación**: Solo existe cuando `create_mode = True`
- **Edición limitada**: Se pueden mover vértices, pero no seleccionar segmentos

#### Estructura
```python
points = [Point3D, Point3D, Point3D, ...]  # Polilínea en construcción
current_point = Point3D()                   # Punto actual del cursor
```

#### Ciclo de Vida
```
1. Usuario activa "Crear polilínea" (create_mode = True)
   ↓
2. points = []  (vacío)
   ↓
3. Usuario agrega puntos → points = [P1, P2, P3, ...]
   ↓
4. Usuario guarda (1002) o finaliza (1003)
   ↓
5. points se agrega a saved_paths
   ↓
6. points.clear()  (se limpia)
```

### Comparación de Estados

| Característica | Polilíneas Guardadas | Polilínea Activa |
|----------------|---------------------|------------------|
| **Almacenamiento** | `saved_paths[]` | `points[]` |
| **Persistencia** | Permanente | Temporal |
| **Modo** | `create_mode = False` | `create_mode = True` |
| **Edición** | Drag vértices, insertar puntos | Drag vértices, agregar puntos |
| **Selección** | Individual o por marco | No disponible |
| **Aplicar diámetro** | ✅ Sí | ❌ No (se aplica después de guardar) |
| **Aplicar layers** | ✅ Sí | ❌ No |
| **Aplicar atributos** | ✅ Sí | ❌ No |
| **Borrar segmentos** | ✅ Sí (1004) | ✅ Sí (drag + delete) |
| **Visualización** | Color verde (3) | Color según preview |

### Transición entre Estados

#### De Activa a Guardada

```python
def save_current_polyline():
    if len(self.points) >= 2:
        new_path = [Point3D(p.X, p.Y, p.Z) for p in self.points]
        self.script_object.saved_paths.append(new_path)
        
        # Crear segmentos por defecto
        _create_default_segments_for_new_path(len(saved_paths) - 1)
        
        # Limpiar activa
        self.points.clear()
        self._clear_editing_state()
```

#### Extensión de Guardada

Si la polilínea activa comienza cerca de un extremo de una guardada:
- Se detecta automáticamente (`extend_target`)
- Al guardar, se fusiona con la guardada existente
- No se crea una nueva polilínea, se extiende la existente

### Segmentos con Información (saved_segments)

Los segmentos guardados tienen información adicional:

```python
saved_segments = [
    {
        'points': [Point3D, Point3D],
        'diameter': 110.0,
        'section_type': '110mm',
        'system': 'Pluvial',
        'label': 'D110 P',
        'installation_type_horizontal': 'FABRICA',
        'installation_type_vertical': 'TD',
        'face': 'X',
        'custom_attributes': {...},
        'arrow_inverted': False
    },
    ...
]
```

**Nota**: Los segmentos de la polilínea activa **NO** tienen esta información hasta que se guarda.

### Operaciones Disponibles por Estado

#### Polilíneas Guardadas
- ✅ Aplicar diámetro (1007)
- ✅ Aplicar layers (1009)
- ✅ Aplicar atributos (1011)
- ✅ Invertir flechas (1010)
- ✅ Borrar segmentos (1004)
- ✅ Drag de vértices
- ✅ Insertar puntos (midpoint o segmento)
- ✅ Selección individual o por marco

#### Polilínea Activa
- ✅ Agregar puntos (click en espacio vacío)
- ✅ Drag de vértices
- ✅ Insertar puntos (midpoint o segmento)
- ✅ Borrar último punto (drag + delete)
- ❌ Aplicar diámetro (se aplica después de guardar)
- ❌ Aplicar layers (se aplica después de guardar)
- ❌ Aplicar atributos (se aplica después de guardar)
- ❌ Selección de segmentos

---

## 7_ Atributos Personalizados

### Descripción General

El sistema permite agregar **atributos personalizados** a segmentos de polilíneas guardadas. Estos atributos se asignan automáticamente a los elementos 3D cuando se crean (tubos, codos, bifurcaciones, reductores).

### Aplicación de Atributos

#### Método

1. **Seleccionar segmento(s)**:
   - Click en segmento individual, o
   - Selección por marco (múltiples segmentos)

2. **Ingresar valor**:
   - Escribir el valor en el campo "ValorAtributos" de la paleta
   - El valor puede ser cualquier texto

3. **Aplicar** (evento 1011):
   - Presionar el botón "Aplicar Atributos" o evento 1011
   - El valor se guarda en `saved_segments[].custom_attributes`

#### Función: `apply_attributes_to_selected()`

```python
def apply_attributes_to_selected():
    # 1. Obtener valor de la paleta
    valor_atributos = _safe_get_palette_property("ValorAtributos", "")
    
    # 2. Validar que haya un valor
    if not valor_atributos or valor_atributos.strip() == "":
        return False
    
    # 3. Aplicar a segmentos seleccionados
    if self.selected_segments:  # Selección por marco
        for kind, path_idx, seg_idx in self.selected_segments:
            _apply_attributes_to_segment(path_idx, seg_idx, valor_atributos)
    elif self.selected_seg:  # Selección individual
        _apply_attributes_to_segment(path_idx, seg_idx, valor_atributos)
```

### Almacenamiento de Atributos

Los atributos se almacenan en `saved_segments[]`:

```python
segment_info = {
    'points': [Point3D, Point3D],
    'diameter': 110.0,
    ...
    'custom_attributes': {
        'attr_1234567890': 'VALOR_INGRESADO',
        'attr_1234567891': 'OTRO_VALOR',
        ...
    }
}
```

Cada atributo tiene una clave única generada con timestamp para mantener el orden.

### Asignación Automática a Elementos

Cuando se crean los elementos 3D, los atributos se asignan automáticamente:

#### Función: `_add_custom_attributes_to_list()`

```python
def _add_custom_attributes_to_list(attr_list, custom_attrs, doc):
    # Obtener el primer valor (todos son iguales)
    attr_value = next(iter(custom_attrs.values()))
    
    # Obtener IDs de atributos por nombre
    attr_6_cc_is_id = AttributeService.GetAttributeID(doc, "6_CC_IS")
    attr_pmp_pare_id = AttributeService.GetAttributeID(doc, "pmp_pare")
    
    # Asignar el mismo valor a ambos atributos
    attr_list.append(AttributeString(attr_6_cc_is_id, attr_value))
    attr_list.append(AttributeString(attr_pmp_pare_id, attr_value))
```

#### Atributos Asignados

El sistema asigna el valor ingresado a **dos atributos**:
- **`6_CC_IS`**: Atributo de identificación
- **`pmp_pare`**: Atributo de pareja

Ambos reciben el **mismo valor** ingresado por el usuario.

### Aplicación en Elementos

Los atributos se aplican a:
- ✅ **Tubos**: Al crear `ModelElement3D` para cada segmento
- ✅ **Codos**: Al crear elementos de codos
- ✅ **Bifurcaciones**: Al crear elementos de bifurcaciones
- ✅ **Reductores**: Al crear elementos de reductores

#### Ejemplo en Código

```python
# Al crear un tubo
custom_attrs = _get_custom_attributes_for_segment(p1, p2)
if custom_attrs:
    attr_list = []
    _add_custom_attributes_to_list(attr_list, custom_attrs, document)
    attributes = Attributes(attr_set_list)
    tube_element.SetAttributes(attributes)
```

### Múltiples Atributos

Un segmento puede tener **múltiples atributos**:
- Cada vez que se aplica un atributo, se agrega una nueva entrada con timestamp único
- Todos los valores se asignan a `6_CC_IS` y `pmp_pare` cuando se crea el elemento
- El último valor aplicado es el que se usa (o se pueden combinar según la lógica)

### Validaciones

- **Valor vacío**: Si el campo está vacío, se muestra error y no se aplica
- **Segmento no encontrado**: Si el segmento no existe en `saved_segments`, se crea una entrada nueva con valores por defecto
- **Selección vacía**: Si no hay segmentos seleccionados, se muestra mensaje de ayuda

### Notas Técnicas

- Los atributos se buscan por nombre usando `AttributeService.GetAttributeID()`
- Si el atributo no existe en el documento, se omite silenciosamente
- Los atributos se asignan usando `AttributeString()` o `AttributeInt()` según el tipo
- El sistema usa IDs de atributos dinámicos (no hardcodeados) para mayor flexibilidad
- Los atributos se almacenan en `custom_attributes` como diccionario para permitir múltiples valores 