# Estructura de Datos de Polilíneas - Documentación Técnica

## 📋 Resumen Ejecutivo

Cuando el usuario introduce una polilínea, el sistema guarda **únicamente los datos geométricos básicos** (puntos y configuración de segmentos). Los elementos especiales como **bifurcaciones, codos, reductores y manguitos se detectan dinámicamente durante la generación del 3D**, analizando la geometría y las relaciones entre puntos.

---

## 💾 Datos que se Guardan

### 1. `saved_paths` - Lista de Polilíneas

**Tipo**: `List[List[AllplanGeo.Point3D]]`

**Descripción**: Almacena las polilíneas completas que el usuario ha dibujado. Cada polilínea es una lista de puntos 3D.

**Estructura**:
```python
self.saved_paths = [
    [Point3D(x1, y1, z1), Point3D(x2, y2, z2), Point3D(x3, y3, z3), ...],  # Path 0
    [Point3D(x1, y1, z1), Point3D(x2, y2, z2), ...],                      # Path 1
    ...
]
```

**Ejemplo**:
```python
# Una polilínea con 3 puntos
saved_paths[0] = [
    AllplanGeo.Point3D(0.0, 0.0, 0.0),      # Punto inicial
    AllplanGeo.Point3D(1000.0, 0.0, 0.0),   # Punto medio
    AllplanGeo.Point3D(1000.0, 1000.0, 0.0) # Punto final
]
```

**Ubicación en código**: Línea ~1390 en `PolylineScriptObject.__init__()`

**Cuándo se guarda**: Cuando el usuario presiona el botón "Guardar" (evento 1002) o cuando se finaliza (evento 1003)

---

### 2. `saved_segments` - Información de Segmentos

**Tipo**: `List[Dict]`

**Descripción**: Almacena información detallada de cada segmento (tramo entre dos puntos consecutivos). Cada segmento tiene su propia configuración de diámetro, sistema, tipo de instalación, etc.

**Estructura del diccionario**:
```python
segment_info = {
    'points': [Point3D(p1), Point3D(p2)],           # Puntos inicio y fin del segmento
    'diameter': 110.0,                              # Diámetro en mm (25, 40, o 110)
    'section_type': "110mm",                        # Tipo de sección como string
    'system': 'Pluvial',                            # Sistema: 'Pluvial' o 'Sanitario'
    'label': "Ø110 Pluvial",                        # Etiqueta para mostrar
    'installation_type_horizontal': 'FABRICA',      # Tipo de instalación horizontal
    'installation_type_vertical': 'TD',             # Tipo de instalación vertical
    'face': 'X',                                    # Cara de referencia
    'arrow_inverted': False                         # Si la flecha está invertida (opcional)
}
```

**Ejemplo completo**:
```python
self.saved_segments = [
    {
        'points': [Point3D(0, 0, 0), Point3D(1000, 0, 0)],
        'diameter': 110.0,
        'section_type': "110mm",
        'system': 'Pluvial',
        'label': "Ø110 Pluvial",
        'installation_type_horizontal': 'FABRICA',
        'installation_type_vertical': 'TD',
        'face': 'X'
    },
    {
        'points': [Point3D(1000, 0, 0), Point3D(1000, 1000, 0)],
        'diameter': 40.0,
        'section_type': "40mm",
        'system': 'Sanitario',
        'label': "Ø40 Sanitario",
        'installation_type_horizontal': 'FABRICA',
        'installation_type_vertical': 'TD',
        'face': 'X'
    }
]
```

**Ubicación en código**: Línea ~1389 en `PolylineScriptObject.__init__()`

**Cuándo se crea**: 
- Automáticamente cuando se guarda una nueva polilínea (método `_create_default_segments_for_new_path()`)
- Cuando se extiende una polilínea existente (método `_create_default_segments_for_extension()`)
- Cuando el usuario configura manualmente la sección de un segmento

---

## 🔍 Detección de Elementos Especiales

### ⚠️ IMPORTANTE: Detección Dinámica

**Los elementos especiales (bifurcaciones, codos, reductores, manguitos) NO se guardan explícitamente**. Se detectan **durante la generación del 3D** en el método `_finalize_and_create_now()`.

**Razón**: La detección depende de:
- La geometría completa de todas las polilíneas
- Las relaciones entre puntos de diferentes paths
- Los cambios de diámetro entre segmentos
- Los ángulos entre segmentos consecutivos

Esto permite que si el usuario modifica la geometría, los elementos se recalculen automáticamente.

---

### 1. Detección de Codos (Elbows)

**Cuándo se detecta**: Durante `_finalize_and_create_now()`, antes de crear los tubos

**Lógica de detección**:

1. **Iterar sobre cada vértice** (punto que no es inicio ni fin de path):
   ```python
   for path_idx, pts in enumerate(self.saved_paths):
       for i in range(1, len(pts) - 1):  # Vértices intermedios
           p_prev = pts[i-1]
           p_curr = pts[i]
           p_next = pts[i+1]
   ```

2. **Calcular vectores de entrada y salida**:
   ```python
   v1 = (p_curr - p_prev)  # Vector de entrada
   v2 = (p_next - p_curr)  # Vector de salida
   ```

3. **Calcular ángulo entre vectores**:
   ```python
   # Normalizar vectores
   v1_norm = v1 / |v1|
   v2_norm = v2 / |v2|
   
   # Producto punto (coseno del ángulo)
   dot = v1_norm · v2_norm
   angle_rad = arccos(dot)
   angle_deg = degrees(angle_rad)
   ```

4. **Determinar tipo de codo**:
   - Si `angle_deg ≈ 45°` → **Codo 45°**
   - Si `angle_deg ≈ 90°` → **Codo 90°**
   - Si `angle_deg > 5°` → **Codo con ángulo específico**

5. **Determinar orientación**:
   - `H→H`: Horizontal a horizontal
   - `H→V`: Horizontal a vertical
   - `V→H`: Vertical a horizontal
   - `V→V`: Vertical a vertical

**Ubicación en código**: Líneas ~2574-3282 en `_finalize_and_create_now()`

**Estructura de datos generada**:
```python
elbows_to_place = [
    (p_curr, v1, v2, d1, d2, color_idx, elbow_type, vertex_idx),
    # p_curr: punto donde va el codo
    # v1, v2: vectores de entrada y salida
    # d1, d2: diámetros de entrada y salida
    # color_idx: color según diámetro/sistema
    # elbow_type: tipo de codo (45°, 90°, etc.)
    # vertex_idx: índice del vértice en el path
]
```

---

### 2. Detección de Reductores

**Cuándo se detecta**: Durante `_finalize_and_create_now()`, al mismo tiempo que los codos

**Lógica de detección**:

1. **Detectar cambio de diámetro entre segmentos consecutivos**:
   ```python
   for i in range(len(pts) - 1):
       seg_in = _find_segment_info(pts[i-1], pts[i])      # Segmento anterior
       seg_out = _find_segment_info(pts[i], pts[i+1])     # Segmento siguiente
       
       d1 = seg_in.get('diameter', 110.0)
       d2 = seg_out.get('diameter', 110.0)
   ```

2. **Verificar si hay cambio de diámetro válido**:
   - **25mm → 40mm**: Usa reductor R25-40mm
   - **40mm → 110mm**: Usa reductor R40-110mm
   - **110mm → 40mm**: Usa reductor R110-40mm
   - **40mm → 25mm**: Usa reductor R40-25mm
   - **110mm ↔ 25mm**: NO soportado (no se coloca reductor)

3. **Calcular recortes de tubos**:
   - Los tubos se recortan para dejar espacio al reductor
   - Los recortes dependen del tipo de reductor

**Ubicación en código**: Líneas ~3100-3282 en `_finalize_and_create_now()`

**Estructura de datos generada**:
```python
reducers_to_place = [
    (p_curr, v1, v2, d1, d2, color_idx, reducer_type, vertex_idx),
    # p_curr: punto donde va el reductor
    # v1, v2: vectores de entrada y salida
    # d1: diámetro de entrada
    # d2: diámetro de salida
    # color_idx: color según diámetro/sistema
    # reducer_type: tipo de reductor (1=R25-40, 2=R110-40, etc.)
    # vertex_idx: índice del vértice en el path
]
```

---

### 3. Detección de Bifurcaciones

**Cuándo se detecta**: Durante `_finalize_and_create_now()`, después de calcular codos y reductores

**Lógica de detección**:

1. **Iterar sobre todos los segmentos de todos los paths**:
   ```python
   for path_idx, pts in enumerate(self.saved_paths):
       for seg_idx in range(len(pts) - 1):
           p1, p2 = pts[seg_idx], pts[seg_idx + 1]
   ```

2. **Verificar si el punto está entre segmentos RECTOS (colineales)**:
   ```python
   def are_segments_straight(p_prev, p_middle, p_next, angle_tolerance_deg=10.0):
       # Calcular vectores
       v1 = p_middle - p_prev
       v2 = p_next - p_middle
       
       # Normalizar
       v1_norm = v1 / |v1|
       v2_norm = v2 / |v2|
       
       # Calcular ángulo
       dot = v1_norm · v2_norm
       angle_deg = degrees(arccos(dot))
       
       # Colineales si ángulo < 10° o > 170°
       return angle_deg < 10.0 or angle_deg > 170.0
   ```

3. **Agregar punto a diccionario de bifurcaciones**:
   ```python
   if are_segments_straight(p_prev, p1, p2):
       # p1 está entre segmentos rectos → candidato a bifurcación
       p1_key = (round(p1.X, 0), round(p1.Y, 0), round(p1.Z, 0))
       if p1_key not in bifurcation_points:
           bifurcation_points[p1_key] = []
       bifurcation_points[p1_key].append((path_idx, seg_idx, True))
   ```

4. **Filtrar puntos que son codos**:
   - Si un punto forma un ángulo (no es colineal), NO es bifurcación
   - Solo puntos entre segmentos rectos pueden ser bifurcaciones

5. **Contar paths que pasan por el mismo punto**:
   ```python
   for point_key, connections in bifurcation_points.items():
       unique_paths = set(conn[0] for conn in connections)
       if len(unique_paths) >= 2:
           # Es una bifurcación válida (2 o más paths se cruzan)
   ```

**Ubicación en código**: Líneas ~3284-3363 en `_finalize_and_create_now()`

**Estructura de datos generada**:
```python
bifurcation_points = {
    (x, y, z): [
        (path_idx, seg_idx, is_start),
        (path_idx, seg_idx, is_start),
        ...
    ],
    # Clave: tupla (x, y, z) redondeada a mm
    # Valor: lista de conexiones (path_idx, seg_idx, is_start)
    # is_start: True si el punto es inicio del segmento, False si es fin
}
```

**Uso de bifurcaciones**:
- Se usan para **deshabilitar anillos** en puntos de bifurcación (líneas ~2285-2293)
- Se usan para **generar elementos de bifurcación** en modo preview (líneas ~9058-9069)

---

### 4. Manguitos

**Nota**: En el código actual, los manguitos no se detectan explícitamente como elementos separados. Se manejan como parte de:
- **Codos**: Algunos codos pueden incluir manguitos según el tipo
- **Reductores**: Los reductores pueden incluir manguitos de conexión
- **Tubos**: Los tubos pueden tener manguitos en los extremos según la configuración

Si se necesita detectar manguitos específicamente, se podría hacer:
1. Detectar puntos donde hay cambio de diámetro sin reductor
2. Detectar puntos donde hay conexión entre segmentos del mismo diámetro pero diferentes sistemas
3. Detectar puntos donde hay conexión entre segmentos con diferentes tipos de instalación

---

## 📊 Flujo Completo de Procesamiento

### Fase 1: Guardado (Usuario introduce polilínea)

```
Usuario dibuja polilínea → Guarda (1002)
    ↓
save_current_polyline()
    ↓
saved_paths.append([Point3D, Point3D, ...])
    ↓
_create_default_segments_for_new_path()
    ↓
saved_segments.append({
    'points': [p1, p2],
    'diameter': 110.0,
    'system': 'Pluvial',
    ...
})
```

**Resultado**: Solo se guardan puntos y configuración básica de segmentos.

---

### Fase 2: Generación 3D (Usuario finaliza)

```
Usuario finaliza (1003) → _finalize_and_create_now()
    ↓
1. Unir paths consecutivos que se tocan
    ↓
2. Actualizar saved_segments según paths unidos
    ↓
3. Pre-calcular codos y reductores
   - Iterar vértices
   - Calcular ángulos
   - Detectar cambios de diámetro
   - Generar listas: elbows_to_place, reducers_to_place
    ↓
4. Detectar bifurcaciones
   - Iterar todos los segmentos
   - Verificar colinealidad
   - Generar diccionario: bifurcation_points
    ↓
5. Crear tubos (aplicando recortes)
   - Para cada segmento
   - Recortar según codos/reductores
   - Crear geometría 3D
    ↓
6. Colocar codos
   - En cada vértice detectado
   - Crear geometría 3D del codo
    ↓
7. Colocar reductores
   - En cada cambio de diámetro detectado
   - Crear geometría 3D del reductor
    ↓
8. Colocar bifurcaciones
   - En cada punto de bifurcación detectado
   - Crear geometría 3D de la bifurcación
    ↓
9. Retornar elementos 3D completos
```

**Resultado**: Geometría 3D completa con todos los elementos detectados y colocados.

---

## 🔑 Puntos Clave

### ✅ Lo que SÍ se guarda:
- **Puntos 3D** de las polilíneas (`saved_paths`)
- **Configuración de segmentos** (`saved_segments`):
  - Diámetro
  - Sistema (Pluvial/Sanitario)
  - Tipo de instalación (horizontal/vertical)
  - Cara de referencia
  - Etiqueta

### ❌ Lo que NO se guarda:
- **Codos**: Se detectan calculando ángulos entre segmentos
- **Reductores**: Se detectan comparando diámetros entre segmentos consecutivos
- **Bifurcaciones**: Se detectan buscando puntos donde se cruzan múltiples paths
- **Manguitos**: No se detectan explícitamente (se manejan como parte de otros elementos)

### 🎯 Ventajas de este enfoque:
1. **Flexibilidad**: Si el usuario modifica la geometría, los elementos se recalculan automáticamente
2. **Consistencia**: Los elementos siempre coinciden con la geometría actual
3. **Simplicidad**: No hay que mantener sincronización entre datos guardados y geometría
4. **Robustez**: Si hay errores en la detección, se pueden corregir sin afectar los datos guardados

### ⚠️ Consideraciones:
1. **Rendimiento**: La detección se hace cada vez que se genera el 3D (puede ser costoso para muchas polilíneas)
2. **Determinismo**: La detección debe ser determinista (mismos inputs → mismos outputs)
3. **Tolerancias**: Las comparaciones de puntos usan tolerancias (1mm) para manejar errores numéricos

---

## 📝 Ejemplo Completo

### Input del Usuario:
```
Polilínea 1: P0(0,0,0) → P1(1000,0,0) → P2(1000,1000,0)
Polilínea 2: P0(1000,0,0) → P3(2000,0,0)
```

### Datos Guardados:
```python
saved_paths = [
    [Point3D(0,0,0), Point3D(1000,0,0), Point3D(1000,1000,0)],
    [Point3D(1000,0,0), Point3D(2000,0,0)]
]

saved_segments = [
    {'points': [P0, P1], 'diameter': 110.0, 'system': 'Pluvial', ...},
    {'points': [P1, P2], 'diameter': 110.0, 'system': 'Pluvial', ...},
    {'points': [P1, P3], 'diameter': 110.0, 'system': 'Pluvial', ...}
]
```

### Detección Durante Generación 3D:

1. **Codo detectado**:
   - Vértice: P1(1000,0,0)
   - Ángulo: 90° (P0→P1→P2)
   - Tipo: Codo 90° H→H

2. **Bifurcación detectada**:
   - Punto: P1(1000,0,0)
   - Paths que pasan: Path 0 (segmento 0 y 1), Path 1 (segmento 0)
   - Tipo: Bifurcación válida (2 paths se cruzan en punto recto)

3. **Elementos generados**:
   - Tubo: P0→P1 (recortado para codo)
   - Codo 90°: En P1
   - Tubo: P1→P2 (recortado para codo)
   - Tubo: P1→P3
   - Bifurcación: En P1

---

## 🔧 Referencias en el Código

| Concepto | Ubicación | Líneas |
|----------|-----------|--------|
| `saved_paths` inicialización | `PolylineScriptObject.__init__()` | ~1390 |
| `saved_segments` inicialización | `PolylineScriptObject.__init__()` | ~1389 |
| Guardado de polilínea | `save_current_polyline()` | ~8686 |
| Creación de segmentos por defecto | `_create_default_segments_for_new_path()` | ~8754 |
| Detección de codos | `_finalize_and_create_now()` | ~2574-3282 |
| Detección de reductores | `_finalize_and_create_now()` | ~3100-3282 |
| Detección de bifurcaciones | `_finalize_and_create_now()` | ~3284-3363 |
| Unión de paths | `_finalize_and_create_now()` | ~1867-1945 |

