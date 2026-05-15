# Documentación: Sistema de Orientación 3D

## 📋 Descripción General

El sistema de orientación 3D permite definir una dirección de referencia en el plano XY que se utiliza para orientar todos los tubos y codos generados. La orientación se define mediante dos puntos que forman una línea en el plano horizontal (Z=0), y el ángulo resultante se guarda como referencia para la rotación de elementos.

## 🔄 Flujo de Trabajo

### Flujo Completo del Usuario

1. **Activar modo**: Usuario presiona el botón "Definir orientación" (Evento 1012)
2. **Primer punto**: Usuario hace clic en el plano XY para definir el primer punto
3. **Segundo punto**: Usuario hace clic nuevamente para definir el segundo punto
4. **Guardar**: Usuario presiona el botón "Definir orientación" nuevamente para guardar la orientación
5. **Desactivar**: El modo se desactiva automáticamente después de guardar
6. **Reactivar**: Usuario puede presionar el botón nuevamente para definir una nueva orientación

### Estados del Sistema

- **Modo inactivo**: `orientation_capture_mode = False`
- **Modo activo, esperando primer punto**: `orientation_capture_mode = True`, `orientation_line_start = None`
- **Modo activo, esperando segundo punto**: `orientation_capture_mode = True`, `orientation_line_start != None`, `orientation_line_end = None`
- **Modo activo, línea completa**: `orientation_capture_mode = True`, ambos puntos definidos, esperando guardar

---

## 📦 Variables de Estado

### En `PolylineScriptObject` (Script Object)

```python
# Orientación 3D de referencia (ángulo en radianes desde eje X)
self.reference_orientation_angle = None
```

**Ubicación**: Línea ~1393 en `__init__`

**Descripción**: Almacena el ángulo de orientación en radianes calculado desde la línea definida. Este valor se utiliza posteriormente para rotar los elementos 3D (tubos, codos, etc.).

---

### En `PolylineInteractor` (Interactor)

```python
# ============================================================================
# ORIENTACIÓN 3D: Captura de línea de referencia en plano XY
# ============================================================================
self.orientation_capture_mode = False  # True cuando estamos capturando línea de orientación
self.orientation_line_start = None  # Primer punto de la línea de orientación (Point3D)
self.orientation_line_end = None  # Segundo punto de la línea de orientación (Point3D) - guardado al completar
self.orientation_line_preview = None  # Segundo punto temporal durante captura (Point3D)
```

**Ubicación**: Líneas ~7130-7136 en `__init__`

**Descripción**:
- `orientation_capture_mode`: Flag que indica si el modo de captura está activo
- `orientation_line_start`: Primer punto de la línea (se fuerza Z=0 para estar en plano XY)
- `orientation_line_end`: Segundo punto guardado después del segundo clic (antes de guardar la orientación)
- `orientation_line_preview`: Punto temporal del cursor durante el movimiento del mouse

---

## 🎯 Métodos Principales

### 1. `start_orientation_capture()`

**Ubicación**: Líneas ~7451-7482

**Descripción**: Método toggle que maneja la activación/desactivación del modo de captura y el guardado de la orientación.

**Lógica**:
- Si el modo está activo y hay línea completa → Guarda la orientación y desactiva el modo
- Si el modo está activo pero no hay línea completa → Cancela el modo
- Si el modo no está activo → Activa el modo

**Código**:
```python
def start_orientation_capture(self):
    """
    Toggle del modo de captura de línea de orientación en el plano XY.
    - Si el modo está activo y ya hay línea definida: guarda y desactiva
    - Si el modo está activo pero no hay línea: cancela
    - Si el modo no está activo: activa el modo
    """
    if self.orientation_capture_mode:
        # Modo ya está activo
        if self.orientation_line_start is not None and self.orientation_line_end is not None:
            # Ya hay línea definida: guardar y desactivar
            print("[INT] Guardando orientación 3D y desactivando modo...")
            self._save_orientation_from_line()
            self._cancel_orientation_capture()
            return True
        else:
            # No hay línea completa: cancelar modo
            print("[INT] Cancelando captura de orientación 3D")
            self._cancel_orientation_capture()
            return True
    else:
        # Modo no está activo: activar modo
        self.orientation_capture_mode = True
        self.orientation_line_start = None
        self.orientation_line_end = None
        self.orientation_line_preview = None
        print("[INT] Modo captura de orientación 3D activado")
        print("[INT] Click en el plano XY para definir el primer punto de la línea de orientación")
        # Actualizar el prompt
        msg = "Orientación 3D: Click para definir primer punto de la línea de orientación (plano XY)"
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
        return True
```

**Evento asociado**: 1012 (botón "Definir orientación")

---

### 2. `_handle_orientation_capture(mouse_msg, raw_pnt)`

**Ubicación**: Líneas ~7484-7544

**Descripción**: Maneja todos los eventos de mouse durante la captura de orientación (movimiento y clics).

**Lógica**:
1. Si ya hay línea completa → Solo actualizar preview visual
2. Si es movimiento del mouse → Actualizar preview temporal
3. Si es clic izquierdo:
   - Si no hay primer punto → Capturar primer punto (Z=0)
   - Si ya hay primer punto → Capturar segundo punto (Z=0), validar distancia mínima, guardar en `orientation_line_end`

**Código**:
```python
def _handle_orientation_capture(self, mouse_msg, raw_pnt):
    """Maneja la captura de la línea de orientación"""
    # Si ya tenemos ambos puntos, solo mostrar preview
    if self.orientation_line_start is not None and self.orientation_line_end is not None:
        # Durante el movimiento, actualizar el preview con la línea ya definida
        if self.coord_input.IsMouseMove(mouse_msg):
            self._draw_preview(raw_pnt)
        return True
    
    # Detectar movimiento del mouse
    if self.coord_input.IsMouseMove(mouse_msg):
        # Durante el movimiento, actualizar el preview
        if self.orientation_line_start is not None:
            self.orientation_line_preview = raw_pnt
            self._draw_preview(raw_pnt)
        return True

    # Click izquierdo: capturar punto
    is_left = (getattr(mouse_msg, 'Button', 1) == 1)
    if not is_left:
        return True
    if self.orientation_line_start is None:
        # Primer punto: forzar Z=0 para estar en el plano XY
        self.orientation_line_start = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
        self.orientation_line_end = None  # Asegurar que está limpio
        print(f"[INT] Primer punto de orientación capturado: ({self.orientation_line_start.X:.2f}, {self.orientation_line_start.Y:.2f}, 0.0)")
        msg = "Orientación 3D: Click para definir segundo punto de la línea de orientación"
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
        self.orientation_line_preview = None
        return True
    else:
        # Segundo punto: forzar Z=0 para estar en el plano XY
        p2 = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
        
        # Calcular el ángulo de la línea respecto al eje X
        dx = p2.X - self.orientation_line_start.X
        dy = p2.Y - self.orientation_line_start.Y
        dist_xy = (dx*dx + dy*dy) ** 0.5
        
        if dist_xy < 1e-6:
            print("[INT] Error: La línea de orientación es demasiado corta. Intente con otro punto.")
            # No cancelar, solo mostrar error y esperar otro clic
            return True
        
        # Guardar el segundo punto (pero NO guardar la orientación aún)
        self.orientation_line_end = p2
        self.orientation_line_preview = None  # Limpiar preview ya que tenemos el punto final
        
        # Calcular ángulo para mostrar feedback
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        print(f"[INT] Segundo punto de orientación capturado: ({p2.X:.2f}, {p2.Y:.2f}, 0.0)")
        print(f"[INT] Ángulo calculado: {angle_deg:.2f}° (desde eje X)")
        print(f"[INT] ✓ Línea de orientación definida. Presione el botón 'Definir orientación' para guardar.")
        
        # Actualizar el prompt para indicar que debe presionar el botón
        msg = "Orientación 3D: ✓ Línea definida. Presione 'Definir orientación' para guardar."
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))
        
        return True
```

**Validaciones**:
- Distancia mínima entre puntos: 1e-6 (1 micrómetro)
- Ambos puntos se fuerzan a Z=0 (plano XY)

---

### 3. `_save_orientation_from_line()`

**Ubicación**: Líneas ~7546-7574

**Descripción**: Calcula y guarda la orientación desde los puntos ya definidos (`orientation_line_start` y `orientation_line_end`).

**Cálculo**:
- Calcula el vector diferencia: `dx = end.X - start.X`, `dy = end.Y - start.Y`
- Calcula el ángulo usando `atan2(dy, dx)` (en radianes)
- Guarda en `self.script_object.reference_orientation_angle`
- Actualiza la información en la paleta

**Código**:
```python
def _save_orientation_from_line(self):
    """Guarda la orientación desde la línea definida (orientation_line_start y orientation_line_end)"""
    if self.orientation_line_start is None or self.orientation_line_end is None:
        print("[INT] Error: No hay línea de orientación completa para guardar")
        return False
    
    # Calcular el ángulo de la línea respecto al eje X
    dx = self.orientation_line_end.X - self.orientation_line_start.X
    dy = self.orientation_line_end.Y - self.orientation_line_start.Y
    dist_xy = (dx*dx + dy*dy) ** 0.5
    
    if dist_xy < 1e-6:
        print("[INT] Error: La línea de orientación es demasiado corta. No se guarda.")
        return False
    
    # Calcular ángulo en radianes (atan2 devuelve ángulo desde +X hacia +Y)
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    # Guardar en el script object
    self.script_object.reference_orientation_angle = angle_rad
    
    print(f"[INT] ✓ Orientación 3D guardada: {angle_deg:.2f}° (desde eje X)")
    print(f"[INT]   Todos los tubos y codos se rotarán para seguir esta orientación")
    
    # Actualizar información en la paleta
    self._update_orientation_info()
    
    return True
```

**Retorno**: `True` si se guardó correctamente, `False` si hay error

---

### 4. `_cancel_orientation_capture()`

**Ubicación**: Líneas ~7576-7586

**Descripción**: Cancela el modo de captura y limpia todos los estados temporales.

**Código**:
```python
def _cancel_orientation_capture(self):
    """Cancela el modo de captura de orientación y restaura el estado normal"""
    if self.orientation_capture_mode:
        print("[INT] Cancelando captura de orientación 3D")
        self.orientation_capture_mode = False
        self.orientation_line_start = None
        self.orientation_line_end = None
        self.orientation_line_preview = None
        self._print_prompt()
        return True
    return False
```

**Uso**: Se llama desde:
- `start_orientation_capture()` cuando se cancela o guarda
- `on_cancel_function()` cuando se presiona ESC
- `_finalize_now()` cuando se presiona el botón finalizar (1003)

---

## 🔧 Métodos Auxiliares

### 1. `_update_orientation_info()`

**Ubicación**: Líneas ~7588-7622

**Descripción**: Actualiza el texto informativo en la paleta con la orientación actual.

**Formato del texto**:
- Si no hay orientación: `"No definida"`
- Si hay orientación: `"{ángulo}° - {dirección} ({eje})"` (ej: `"45.0° - Noreste (NE) (Diagonal X+/Y+)"`)

**Código**:
```python
def _update_orientation_info(self):
    """Actualiza la información de orientación 3D en la paleta"""
    try:
        ref_angle = getattr(self.script_object, 'reference_orientation_angle', None)
        
        if ref_angle is None:
            info_text = "No definida"
        else:
            angle_deg = math.degrees(ref_angle)
            # Normalizar ángulo a [0, 360)
            angle_deg = angle_deg % 360.0
            if angle_deg < 0:
                angle_deg += 360.0
            
            # Determinar dirección cardinal/principal
            direction = self._get_direction_from_angle(angle_deg)
            
            # Determinar eje/cota principal
            axis_info = self._get_axis_info_from_angle(angle_deg)
            
            # Formatear texto
            info_text = f"{angle_deg:.1f}° - {direction} ({axis_info})"
        
        # Actualizar en la paleta
        self._safe_set_palette_property("Orientacion3DInfo", info_text)
        
        # Forzar actualización de la paleta
        try:
            if hasattr(self.script_object, 'palette_service') and self.script_object.palette_service:
                self.script_object.palette_service.update_palette(self.script_object.build_ele, show_palette=True)
        except Exception as palette_ex:
            print(f"[INT] No se pudo actualizar paleta: {palette_ex}")
            
    except Exception as ex:
        print(f"[INT] Error actualizando información de orientación: {ex}")
```

**Propiedad de paleta**: `Orientacion3DInfo` (tipo Text)

---

### 2. `_get_direction_from_angle(angle_deg: float) -> str`

**Ubicación**: Líneas ~7624-7645

**Descripción**: Determina la dirección cardinal/principal desde el ángulo en grados.

**Direcciones**:
- Este (E): 337.5° - 22.5°
- Noreste (NE): 22.5° - 67.5°
- Norte (N): 67.5° - 112.5°
- Noroeste (NO): 112.5° - 157.5°
- Oeste (O): 157.5° - 202.5°
- Suroeste (SO): 202.5° - 247.5°
- Sur (S): 247.5° - 292.5°
- Sureste (SE): 292.5° - 337.5°

**Código**:
```python
def _get_direction_from_angle(self, angle_deg: float) -> str:
    """Determina la dirección cardinal/principal desde el ángulo"""
    # Normalizar a [0, 360)
    angle_deg = angle_deg % 360.0
    
    # Direcciones principales con tolerancia de ±22.5°
    if 337.5 <= angle_deg or angle_deg < 22.5:
        return "Este (E)"
    elif 22.5 <= angle_deg < 67.5:
        return "Noreste (NE)"
    elif 67.5 <= angle_deg < 112.5:
        return "Norte (N)"
    elif 112.5 <= angle_deg < 157.5:
        return "Noroeste (NO)"
    elif 157.5 <= angle_deg < 202.5:
        return "Oeste (O)"
    elif 202.5 <= angle_deg < 247.5:
        return "Suroeste (SO)"
    elif 247.5 <= angle_deg < 292.5:
        return "Sur (S)"
    else:  # 292.5 <= angle_deg < 337.5
        return "Sureste (SE)"
```

---

### 3. `_get_axis_info_from_angle(angle_deg: float) -> str`

**Ubicación**: Líneas ~7647-7679

**Descripción**: Determina el eje/cota principal desde el ángulo en grados.

**Lógica**:
- Si `abs_x > abs_y * 1.5`: Dominante en X (Eje X+ o X-)
- Si `abs_y > abs_x * 1.5`: Dominante en Y (Eje Y+ o Y-)
- Si ambos similares: Diagonal (X+/Y+, X-/Y+, X-/Y-, X+/Y-)

**Código**:
```python
def _get_axis_info_from_angle(self, angle_deg: float) -> str:
    """Determina el eje/cota principal desde el ángulo"""
    # Normalizar a [0, 360)
    angle_deg = angle_deg % 360.0
    
    # Calcular componentes X e Y normalizadas
    angle_rad = math.radians(angle_deg)
    comp_x = math.cos(angle_rad)
    comp_y = math.sin(angle_rad)
    
    # Determinar componente dominante
    abs_x = abs(comp_x)
    abs_y = abs(comp_y)
    
    if abs_x > abs_y * 1.5:  # Dominante en X
        if comp_x > 0:
            return "Eje X+"
        else:
            return "Eje X-"
    elif abs_y > abs_x * 1.5:  # Dominante en Y
        if comp_y > 0:
            return "Eje Y+"
        else:
            return "Eje Y-"
    else:  # Diagonal (ambos componentes similares)
        if comp_x > 0 and comp_y > 0:
            return "Diagonal X+/Y+"
        elif comp_x < 0 and comp_y > 0:
            return "Diagonal X-/Y+"
        elif comp_x < 0 and comp_y < 0:
            return "Diagonal X-/Y-"
        else:  # comp_x > 0 and comp_y < 0
            return "Diagonal X+/Y-"
```

---

## 🔗 Integración con Otros Componentes

### 1. Integración en `process_mouse_msg()`

**Ubicación**: Líneas ~8100-8108

**Descripción**: Intercepta los eventos de mouse cuando el modo de captura está activo.

**Código**:
```python
def process_mouse_msg(self, mouse_msg, pnt, msg_info):
    # Si estamos en modo captura de orientación, manejar eso primero
    if self.orientation_capture_mode:
        raw_pnt = self.coord_input.GetInputPoint(
            mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
        ).GetPoint()
        return self._handle_orientation_capture(mouse_msg, raw_pnt)
    
    # ... resto del código normal ...
```

**Prioridad**: El modo de captura de orientación tiene prioridad sobre otros modos (creación, edición, etc.)

---

### 2. Integración en `on_control_event()`

**Ubicación**: Líneas ~6973-6985

**Descripción**: Registra el handler para el evento 1012 (botón "Definir orientación").

**Código**:
```python
handlers = {
    # ... otros handlers ...
    1012: intr.start_orientation_capture  # Definir orientación 3D
}
```

**Evento**: 1012 (definido en el archivo `.pyp`)

---

### 3. Integración en `on_cancel_function()`

**Ubicación**: Líneas ~8608-8615

**Descripción**: Permite cancelar el modo de captura con ESC sin finalizar el script object.

**Código**:
```python
def on_cancel_function(self):
    """ESC: guardar si corresponde y CREAR INMEDIATO para no depender de execute()."""
    try:
        # Si estamos en modo captura de orientación, cancelar solo eso
        if self.orientation_capture_mode:
            print("[INT] ESC: Cancelando captura de orientación 3D")
            self._cancel_orientation_capture()
            return OnCancelFunctionResult.CONTINUE_INPUT  # Continuar el input, no finalizar
        
        # ... resto del código normal ...
```

**Comportamiento**: Si el modo está activo, ESC solo cancela la captura y continúa el input. Si no está activo, mantiene el comportamiento original (guardar y finalizar).

---

### 4. Integración en `_finalize_now()` (Evento 1003)

**Ubicación**: Líneas ~6916-6922

**Descripción**: Permite cancelar el modo de captura con el botón "Finalizar" sin finalizar el script object.

**Código**:
```python
def _finalize_now():
    try:
        # Si estamos en modo captura de orientación, cancelar solo eso
        if intr.orientation_capture_mode:
            print("[SO] Cancelando captura de orientación 3D (evento 1003)")
            intr._cancel_orientation_capture()
            return True  # No finalizar, solo cancelar orientación
        
        # ... resto del código normal ...
```

---

### 5. Preview Visual en `_draw_preview()`

**Ubicación**: Líneas ~9748-9774

**Descripción**: Dibuja una línea verde que muestra la línea de orientación durante la captura.

**Características**:
- Color: Verde (3)
- Pen: 15 (línea gruesa)
- Z forzado a 0 (plano XY)
- Muestra línea desde `orientation_line_start` hasta:
  - `orientation_line_end` (si ya está definido)
  - `orientation_line_preview` (si está en movimiento)
  - `hover` (punto actual del cursor)

**Código**:
```python
# ============================================================================
# PREVIEW DE LÍNEA DE ORIENTACIÓN 3D
# ============================================================================
if self.orientation_capture_mode and self.orientation_line_start is not None:
    # Crear propiedades para la línea de orientación
    orient_prop = self._clone_properties(self.com_prop)
    orient_prop.Color = 3  # Verde
    orient_prop.ColorByLayer = False
    orient_prop.PenByLayer = False
    orient_prop.StrokeByLayer = False
    orient_prop.Pen = 15  # Línea más gruesa
    
    # Determinar el punto final: usar el punto guardado si existe, sino el preview, sino hover
    if self.orientation_line_end is not None:
        # Ya tenemos el segundo punto guardado
        end_point = self.orientation_line_end
    elif self.orientation_line_preview is not None:
        # Usar el preview del mouse
        end_point = self.orientation_line_preview
    else:
        # Usar el hover actual
        end_point = hover
    
    if end_point is not None:
        # Forzar Z=0 para ambos puntos (plano XY)
        p1_xy = AllplanGeo.Point3D(self.orientation_line_start.X, self.orientation_line_start.Y, 0.0)
        p2_xy = AllplanGeo.Point3D(end_point.X, end_point.Y, 0.0)
        orient_line = AllplanGeo.Line3D(p1_xy, p2_xy)
        elems.append(AllplanBasisElements.ModelElement3D(orient_prop, orient_line))
```

---

## 📝 Configuración en el Archivo .pyp

### Botón "Definir orientación"

**Ubicación**: `Saneamiento.pyp` líneas ~87-100

**Configuración**:
```xml
<!-- Orientación de tubos 3D -->
<Parameter>
    <Name>RowOrientacion3D</Name>
    <Text>Orientación 3D</Text>
    <ValueType>Row</ValueType>
    <Value>OVERALL:1</Value>
    <Parameter>
        <Name>definirOrientacion</Name>
        <Text>Definir orientación</Text>
        <EventId>1012</EventId>
        <Value>0</Value>
        <ValueType>Button</ValueType>
    </Parameter>
</Parameter>
```

### Campo de Información

**Ubicación**: `Saneamiento.pyp` líneas ~102-113

**Configuración**:
```xml
<Parameter>
    <Name>Orientacion3DRow</Name>
    <Text>Orientación Actual</Text>
    <ValueType>Row</ValueType>
    <Value>OVERALL:1</Value>
    <Parameter>
        <Name>Orientacion3DInfo</Name>
        <Text></Text>
        <Value>No definida</Value>
        <ValueType>Text</ValueType>
    </Parameter>
</Parameter>
```

---

## 🎨 Mensajes y Prompts

### Mensajes del Sistema

| Estado | Mensaje |
|--------|---------|
| Modo activado | `"[INT] Modo captura de orientación 3D activado"` |
| Primer punto capturado | `"[INT] Primer punto de orientación capturado: (X, Y, 0.0)"` |
| Segundo punto capturado | `"[INT] Segundo punto de orientación capturado: (X, Y, 0.0)"` |
| Ángulo calculado | `"[INT] Ángulo calculado: XX.XX° (desde eje X)"` |
| Línea definida | `"[INT] ✓ Línea de orientación definida. Presione el botón 'Definir orientación' para guardar."` |
| Orientación guardada | `"[INT] ✓ Orientación 3D guardada: XX.XX° (desde eje X)"` |
| Error línea corta | `"[INT] Error: La línea de orientación es demasiado corta. Intente con otro punto."` |
| Cancelación | `"[INT] Cancelando captura de orientación 3D"` |

### Prompts al Usuario

| Estado | Prompt |
|--------|--------|
| Modo activado | `"Orientación 3D: Click para definir primer punto de la línea de orientación (plano XY)"` |
| Esperando segundo punto | `"Orientación 3D: Click para definir segundo punto de la línea de orientación"` |
| Línea completa | `"Orientación 3D: ✓ Línea definida. Presione 'Definir orientación' para guardar."` |

---

## 🔢 Cálculo del Ángulo

### Fórmula

El ángulo se calcula usando la función `atan2`:

```python
dx = p2.X - p1.X
dy = p2.Y - p1.Y
angle_rad = math.atan2(dy, dx)
angle_deg = math.degrees(angle_rad)
```

### Interpretación

- **0°**: Dirección Este (+X)
- **90°**: Dirección Norte (+Y)
- **180°**: Dirección Oeste (-X)
- **270°**: Dirección Sur (-Y)
- **45°**: Dirección Noreste (diagonal X+/Y+)
- **-45°** o **315°**: Dirección Sureste (diagonal X+/Y-)

### Normalización

El ángulo se normaliza al rango [0, 360) para mostrar en la paleta:

```python
angle_deg = angle_deg % 360.0
if angle_deg < 0:
    angle_deg += 360.0
```

---

## ✅ Validaciones

### Validación de Distancia Mínima

**Ubicación**: En `_handle_orientation_capture()` y `_save_orientation_from_line()`

**Código**:
```python
dist_xy = (dx*dx + dy*dy) ** 0.5
if dist_xy < 1e-6:
    print("[INT] Error: La línea de orientación es demasiado corta...")
    return True  # o False según el contexto
```

**Valor**: 1e-6 (1 micrómetro) - evita divisiones por cero y líneas inválidas

### Forzado de Z=0

**Ubicación**: En `_handle_orientation_capture()`

**Código**:
```python
self.orientation_line_start = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
p2 = AllplanGeo.Point3D(raw_pnt.X, raw_pnt.Y, 0.0)
```

**Razón**: La orientación debe estar en el plano horizontal (XY) para ser consistente con la rotación de elementos 3D.

---

## 🚀 Uso del Ángulo Guardado

El ángulo guardado en `self.script_object.reference_orientation_angle` se utiliza posteriormente en la generación de elementos 3D (tubos, codos, reductores, bifurcaciones) para rotarlos según la orientación definida.

**Ejemplo de uso** (conceptual):
```python
# En el código de generación de elementos
if self.script_object.reference_orientation_angle is not None:
    # Aplicar rotación según la orientación de referencia
    rotation_matrix = AllplanGeo.Matrix3D()
    rotation_matrix.SetRotation(
        AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),  # Eje Z
        AllplanGeo.Angle(self.script_object.reference_orientation_angle)
    )
    # Aplicar matriz de rotación a la geometría
```

---

## 📊 Diagrama de Estados

```
[Modo Inactivo]
    |
    | Presionar botón (1012)
    v
[Modo Activo - Esperando Primer Punto]
    |
    | Click (primer punto)
    v
[Modo Activo - Esperando Segundo Punto]
    |
    | Click (segundo punto)
    v
[Modo Activo - Línea Completa]
    |
    | Presionar botón (1012) -> Guardar y desactivar
    | ESC (1003) -> Cancelar
    | Finalizar (1003) -> Cancelar
    v
[Modo Inactivo]
```

---

## 🔍 Debugging

### Logs Importantes

Todos los mensajes de log están prefijados con `[INT]` para facilitar el filtrado:

```python
# Ejemplos de logs
print("[INT] Modo captura de orientación 3D activado")
print(f"[INT] Primer punto de orientación capturado: ({x:.2f}, {y:.2f}, 0.0)")
print(f"[INT] ✓ Orientación 3D guardada: {angle_deg:.2f}° (desde eje X)")
```

### Verificación de Estado

Para verificar el estado actual:

```python
print(f"Modo activo: {self.orientation_capture_mode}")
print(f"Primer punto: {self.orientation_line_start}")
print(f"Segundo punto: {self.orientation_line_end}")
print(f"Ángulo guardado: {self.script_object.reference_orientation_angle}")
```

---

## 📚 Referencias

- **Archivo principal**: `Saneamiento.py`
- **Configuración UI**: `Saneamiento.pyp`
- **Evento del botón**: 1012
- **Propiedad de paleta**: `Orientacion3DInfo`

---

## 🔄 Historial de Cambios

### Versión Actual
- **Toggle del botón**: Activar → Definir → Guardar y desactivar
- **Cancelación con ESC**: Implementada
- **Preview visual**: Línea verde durante captura
- **Información en paleta**: Ángulo, dirección y eje

---

**Última actualización**: Enero 2026
