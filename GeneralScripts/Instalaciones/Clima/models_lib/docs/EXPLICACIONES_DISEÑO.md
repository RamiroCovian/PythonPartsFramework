# Explicaciones de Diseño - polyline_base_lib

**Documento de referencia personal** para entender las decisiones técnicas  
**Versión:** 1.0  
**Fecha:** 2025-01-15

---

## Índice

1. [Preguntas Frecuentes - Decisiones de Diseño](#preguntas-frecuentes-decisiones-de-diseño)
2. [Resumen Ejecutivo - Respuestas Rápidas](#resumen-ejecutivo-respuestas-rápidas)
3. [Puntos Clave para Recordar](#puntos-clave-para-recordar)
4. [Escenarios de Conversación con tu Jefe](#escenarios-de-conversación-con-tu-jefe)
5. [Tips para la Conversación](#tips-para-la-conversación)

---

## Preguntas Frecuentes - Decisiones de Diseño

### 1. ¿Por qué el hook se llama 1 vez por segmento y no 1 vez por path completo?

**Razón técnica:**
Cada segmento puede tener propiedades diferentes (diámetro, material, layer, etc.). Si pasáramos el path completo, la instalación tendría que iterar manualmente por todos los segmentos para crear los elementos.

**Razón de mantenibilidad:**
Al llamar el hook una vez por segmento, el código de la instalación es más simple:
- No necesita bucles
- Maneja un solo segmento a la vez
- Más fácil de debuggear
- Logs más claros (un log por segmento)

**Razón de flexibilidad:**
Algunas instalaciones pueden necesitar lógica diferente según el tipo de segmento (horizontal vs vertical, FABRICA vs OBRA, etc.). Con un hook por segmento, esta lógica queda encapsulada en un solo lugar.

**Ejemplo:**

```python
# Si fuera 1 hook por path (más complejo):
def element_creation_hook(path_segments: List[SegmentMetadata], ...):
    elements = []
    for seg in path_segments:  # ← Bucle manual
        if seg.is_horizontal():
            # ... lógica horizontal
        else:
            # ... lógica vertical
    return elements

# Con 1 hook por segmento (más simple):
def element_creation_hook(seg_meta: SegmentMetadata, ...):
    # Ya estás en un segmento específico
    if self._is_horizontal(seg_meta):
        # ... lógica horizontal
    else:
        # ... lógica vertical
    return elements
```

---

### 2. ¿Por qué usar `@dataclass` en lugar de un diccionario simple?

**Razón de seguridad:**
Los diccionarios pueden tener errores de typo en las keys:

```python
# Con dict (propenso a errores):
diameter = seg['diamter']  # ← Typo: "diamter" en lugar de "diameter"
# Error: KeyError en runtime

# Con @dataclass:
diameter = seg_meta.diamter  # ← IDE detecta el error inmediatamente
# IDE: "SegmentMetadata has no attribute 'diamter'. Did you mean 'diameter'?"
```

**Razón de documentación:**
El `@dataclass` autodocumenta qué campos existen y sus tipos:

```python
# Con dict: tienes que adivinar qué keys existen
seg = {'points': [...], 'diameter': 110.0, ...}  # ¿Qué más hay?

# Con @dataclass: el código ES la documentación
@dataclass
class SegmentMetadata:
    points: List[Any]        # ← Claramente tipado
    diameter: float = 110.0  # ← Default visible
    system: str = "Pluvial"  # ← Default visible
```

**Razón de IDE support:**
Con `@dataclass`, el IDE puede:
- Autocompletar campos
- Detectar errores de tipo
- Mostrar documentación en hover
- Refactorizar de forma segura

---

### 3. ¿Por qué separar propiedades básicas de metadata custom?

**Razón de estandarización:**
Todas las instalaciones necesitan ciertas propiedades básicas:
- `points`: geometría del segmento
- `diameter`: tamaño
- `system`: tipo de sistema
- `label`: identificación

Al tenerlas como campos dedicados (no en `custom`), garantizamos que siempre existen y están tipadas.

**Razón de extensibilidad:**
Cada instalación tiene necesidades específicas:
- Saneamiento: `installation_type_horizontal`, `installation_type_vertical`, `face`
- Clima: `velocidad_aire`, `caudal`, `presion`, `aislamiento`
- Electricidad: `voltaje`, `corriente`, `fase`

El diccionario `custom` permite añadir cualquier metadata sin modificar la librería base.

**Ejemplo:**

```python
# Propiedades comunes (todas las instalaciones):
seg_meta.diameter  # ← Siempre existe, tipado como float
seg_meta.system    # ← Siempre existe, tipado como str

# Propiedades específicas (solo para tu instalación):
seg_meta.custom['velocidad_aire']  # ← Solo en Clima
seg_meta.custom['face']            # ← Solo en Saneamiento
```

---

### 4. ¿Por qué `points` es siempre una lista de 2 elementos?

**Razón de simplicidad:**
Un segmento es, por definición, una línea entre dos puntos. No más, no menos.

**Razón de consistencia:**
Si permitiéramos N puntos, habría ambigüedad:
- ¿Es un segmento con curvas?
- ¿Son múltiples subsegmentos?
- ¿Cómo se calculan transformaciones?

Con 2 puntos (inicio y fin), todo es predecible.

**Razón de paths:**
Si un usuario dibuja una polilínea con 5 puntos, la librería la divide automáticamente en 4 segmentos:

```
Puntos capturados: [P1, P2, P3, P4, P5]

Segmentos generados:
- Segmento 1: [P1, P2]
- Segmento 2: [P2, P3]
- Segmento 3: [P3, P4]
- Segmento 4: [P4, P5]
```

Esto facilita la gestión de propiedades individuales por segmento.

---

### 5. ¿Por qué el layer se asigna en el hook y no en la librería?

**Razón de especificidad:**
Cada instalación tiene su propia lógica de layers:

```python
# Saneamiento:
# - Horizontal FABRICA → Layer 40148
# - Horizontal OBRA → Layer 40149
# - Vertical EN cara X → Layer 40106

# Clima:
# - Impulsión → Layer 50200
# - Retorno → Layer 50201

# Electricidad:
# - Alta tensión → Layer 60100
# - Baja tensión → Layer 60101
```

La librería no puede conocer todas estas reglas específicas.

**Razón de flexibilidad:**
La lógica de layers puede depender de:
- Tipo de instalación
- Diámetro
- Orientación (horizontal/vertical)
- Metadata custom (`installation_type_horizontal`, `face`, etc.)
- Configuraciones del proyecto

Al delegar esto al hook, cada instalación tiene control total.

**Solución:**
La librería proporciona `seg_meta.custom` con toda la metadata necesaria, y el hook traduce esa metadata al layer de Allplan correspondiente.

---

### 6. ¿Por qué usar `Optional[int]` para `path_id` y `segment_id`?

**Razón de flexibilidad de uso:**
No todos los contextos necesitan IDs de organización:
- **Captura interactiva:** sí, para relacionar segmentos de un mismo path
- **Import JSON:** sí, para preservar agrupaciones
- **Creación programática:** tal vez no (elementos independientes)

Al ser opcionales (`None` por defecto), no obligamos a proporcionar estos valores si no son relevantes.

**Razón de compatibilidad:**
Scripts antiguos que no usaban IDs pueden migrar gradualmente sin necesidad de cambios masivos.

---

### 7. ¿Por qué `diameter` es float y no string (como "110mm")?

**Razón de cálculos:**
El diámetro se usa en cálculos geométricos:

```python
# Cálculo de área de sección:
area = math.pi * (seg_meta.diameter / 2) ** 2

# Cálculo de offset para modelado:
offset = seg_meta.diameter / 2

# Comparaciones:
if seg_meta.diameter >= 110.0:
    # ... es bajante
else:
    # ... es tubería de pared
```

Si fuera string ("110mm"), habría que parsearlo constantemente.

**Razón de tipado:**
Con `float`, el IDE puede:
- Detectar errores de tipo
- Sugerir operaciones matemáticas
- Validar rangos

**Solución híbrida:**
La librería proporciona AMBOS:
- `diameter`: `float` para cálculos (110.0)
- `section_type`: `str` para display ("110mm", "400x200", etc.)

---

### 8. ¿Por qué permitir `layer` tanto como string como número?

**Razón de compatibilidad con Allplan:**
Allplan acepta layers de dos formas:
- Número: `40148` (layer numérico)
- Nombre: `"IS_CON_SANE_FAB"` (layer con nombre)

Al permitir ambos tipos (`Optional[str]`), la librería es compatible con cualquier workflow.

**Razón de migración:**
Algunos proyectos usan números, otros nombres. Al soportar ambos, facilitamos la migración sin cambios masivos.

**Implementación:**

```python
# En el hook:
if isinstance(layer_value, int):
    common_prop.Layer = layer_value  # Asignar como int
elif isinstance(layer_value, str):
    common_prop.Layer = int(layer_value)  # Convertir si es string numérico
```

---

### 9. ¿Por qué `point_roles` es una lista de números y no un enum?

**Razón de simplicidad:**
Los roles son valores sencillos (0, 1, 2, 3) que representan:
- 0 = Inicial
- 1 = Paso
- 2 = Bifurcación
- 3 = Final

Una lista de ints es suficiente y más fácil de serializar (JSON, etc.).

**Razón de performance:**
Comparar ints es más rápido que comparar enums:

```python
# Con int (rápido):
if seg_meta.point_roles[0] == 2:
    # ... es bifurcación

# Con enum (más verboso):
if seg_meta.point_roles[0] == PointRole.BIFURCATION:
    # ... es bifurcación
```

**Documentación:**
Los valores están documentados en el docstring de `SegmentMetadata` y en constantes del módulo:

```python
POINT_ROLE_START = 0
POINT_ROLE_INTERMEDIATE = 1
POINT_ROLE_BIFURCATION = 2
POINT_ROLE_END = 3
```

---

### 10. ¿Por qué la librería devuelve `SegmentMetadata` en lugar de los elementos 3D directamente?

**Razón de separación de responsabilidades:**
- **Librería:** gestiona la interacción de usuario (captura de puntos, edición, etc.) y organiza la información
- **Instalación:** conoce cómo crear modelos 3D específicos (tubos PVC, conductos de chapa, etc.)

La librería no puede conocer todos los tipos de modelos 3D de todas las instalaciones.

**Razón de flexibilidad:**
Diferentes instalaciones crean diferentes modelos:
- Saneamiento: tubo PVC con flecha direccional
- Clima: conducto rectangular con aislamiento
- Electricidad: bandeja portacables con tapa

Al devolver metadata estructurada, cada instalación implementa su lógica específica en el hook.

**Razón de testabilidad:**
Es más fácil testear que la metadata es correcta (comparar valores) que testear geometría 3D compleja (comparar BReps).

---

### 11. ¿Por qué usar helpers externos (`get_segment_length`, etc.) en lugar de métodos de la clase?

**Razón de inmutabilidad:**
`SegmentMetadata` es un `@dataclass` puro (solo datos, sin lógica). Esto facilita:
- Serialización/deserialización
- Testing
- Debugging (print de toda la estructura)

**Razón de modularidad:**
Los helpers están en el módulo `polyline_base_lib`, disponibles globalmente:

```python
import polyline_base_lib as PBL

length = PBL.get_segment_length(seg_meta)
direction = PBL.get_segment_direction_vector(seg_meta)
```

Esto permite usarlos en cualquier contexto, no solo con instancias de `SegmentMetadata`.

**Razón de compatibilidad:**
Si en el futuro se cambia la estructura interna de `SegmentMetadata`, los helpers pueden adaptarse sin romper código cliente.

---

### 12. ¿Por qué no incluir la geometría 3D (BRep) en `SegmentMetadata`?

**Razón de responsabilidad:**
`SegmentMetadata` describe QUÉ es el segmento (geometría, propiedades, metadata), no CÓMO se visualiza (modelo 3D).

La creación del modelo 3D es responsabilidad del hook, que puede:
- Crear diferentes modelos según el contexto
- Aplicar transformaciones específicas
- Manejar errores de modelado
- Usar fallbacks (líneas simples si falla el modelo complejo)

**Razón de eficiencia:**
No todos los contextos necesitan geometría 3D:
- Exportar a JSON: solo necesita metadata
- Cálculos de longitudes totales: solo necesita puntos
- Validaciones: solo necesita propiedades

Crear geometría 3D es costoso. Al separarlo, optimizamos performance.

---

### 13. ¿Por qué permitir metadata custom ilimitada en lugar de campos fijos?

**Razón de evolución:**
Las necesidades de las instalaciones cambian con el tiempo:
- Nuevas normativas pueden requerir campos adicionales
- Nuevas funcionalidades necesitan nueva metadata
- Integraciones con otros sistemas requieren datos específicos

Con `custom` dict, se pueden añadir campos sin modificar la librería.

**Razón de retrocompatibilidad:**
Scripts antiguos siguen funcionando aunque se añadan nuevos campos al `custom` dict. No hay breaking changes.

**Razón de múltiples instalaciones:**
Cada instalación tiene necesidades únicas:
- Saneamiento: pendiente, material, tipo instalación
- Clima: velocidad aire, caudal, presión
- Electricidad: voltaje, corriente, fase

Un conjunto fijo de campos no puede cubrir todos los casos.

---

## Resumen Ejecutivo - Respuestas Rápidas

Para conversaciones con tu jefe, aquí están las respuestas en 1 frase:

| Pregunta | Respuesta Corta |
|----------|-----------------|
| **¿Por qué hook 1 vez por segmento?** | Cada segmento tiene propiedades diferentes y así el código es más simple (no necesita bucles). |
| **¿Por qué `@dataclass`?** | Evita errores de typo, el IDE autocompleta y detecta errores antes de ejecutar. |
| **¿Por qué separar básico de custom?** | Lo común a todas las instalaciones va en campos dedicados, lo específico va en `custom`. |
| **¿Por qué `points` tiene 2 elementos?** | Un segmento es una línea entre 2 puntos, si hay más puntos se dividen en múltiples segmentos. |
| **¿Por qué layer en el hook?** | Cada instalación tiene su lógica de layers (Saneamiento usa 40148/40149, Clima otros, etc.). |
| **¿Por qué `path_id` opcional?** | No todos los contextos necesitan agrupar segmentos (ej: elementos independientes). |
| **¿Por qué `diameter` es float?** | Para hacer cálculos (área, offsets, comparaciones), si fuera string habría que parsearlo siempre. |
| **¿Por qué `layer` string o número?** | Allplan acepta ambos y así facilitamos migración de proyectos existentes. |
| **¿Por qué `point_roles` es lista de ints?** | Más simple y rápido que enums, los valores están documentados (0=Inicial, 1=Paso, etc.). |
| **¿Por qué devolver metadata y no 3D?** | La librería gestiona interacción, la instalación sabe cómo crear sus modelos específicos. |
| **¿Por qué helpers externos?** | `SegmentMetadata` es solo datos (inmutable), los helpers son funciones reutilizables. |
| **¿Por qué no BRep en metadata?** | No todos los contextos necesitan 3D (ej: export JSON), y crearlo es costoso. |
| **¿Por qué custom ilimitado?** | Las necesidades evolucionan y cada instalación es diferente, no hay breaking changes. |

---

## Puntos Clave para Recordar

### Arquitectura General

**Separación de responsabilidades:**
- **Librería:** maneja interacción de usuario (captura, edición, undo, bifurcación)
- **Instalación:** implementa lógica específica (layers, modelos 3D, metadata custom)

**Flujo de datos:**
```
Usuario captura puntos → Librería crea SegmentMetadata → Hook crea elementos 3D
```

### Diseño de Datos

**Campos obligatorios vs opcionales:**
- **Obligatorio:** `points` (geometría básica)
- **Con defaults seguros:** `diameter`, `system`, `section_type`, `label`
- **Opcionales:** `layer`, `path_id`, `segment_id`, `color_id`
- **Extensible:** `custom` dict (cualquier metadata adicional)

**Tipos de datos:**
- `float` para valores numéricos que se usan en cálculos (`diameter`)
- `str` para valores descriptivos (`section_type`, `label`)
- `Dict[str, Any]` para metadata flexible (`custom`)

### Extensibilidad

**Añadir nuevos campos sin modificar librería:**
```python
seg_meta.custom['nuevo_campo'] = valor
```

**Cada instalación define su metadata:**
- Saneamiento: `installation_type_horizontal`, `face`
- Clima: `velocidad_aire`, `caudal`
- Tu instalación: lo que necesites

---

## Escenarios de Conversación con tu Jefe

### Escenario 1: "¿Por qué no pasas toda la polilínea de una vez al hook?"

**Respuesta:**
"Porque cada segmento puede tener propiedades diferentes. Si en un path de 5 segmentos el usuario cambia el diámetro del segmento 3, solo ese tiene diameter=40, los demás tienen 110. Si paso todo junto, el hook tiene que iterar manualmente. Así es más simple: 1 llamada = 1 segmento = 1 conjunto de propiedades."

**Ejemplo concreto:**
"En Saneamiento, un segmento horizontal FABRICA va a layer 40148, pero si luego va vertical EN cara X va a layer 40106. Con un hook por segmento, cada uno aplica su lógica específica sin complicar el código."

---

### Escenario 2: "¿Por qué usas `@dataclass`? Un dict es más simple."

**Respuesta:**
"El dict es simple pero propenso a errores. Si escribo `seg['diamter']` en lugar de `seg['diameter']`, falla en runtime. Con `@dataclass`, el IDE me avisa antes de ejecutar. Además el código se autodocumenta: veo qué campos existen y sus tipos sin tener que buscar en otra parte."

**Ejemplo concreto:**
"Si Braian tiene que usar esto para crear los modelos 3D, con `@dataclass` su IDE le autocompleta `seg_meta.` y le muestra todos los campos disponibles. Con dict tiene que adivinar o leer documentación."

---

### Escenario 3: "¿Por qué no metes todo en `custom`? ¿Para qué tener `diameter`, `system`, etc. separados?"

**Respuesta:**
"Porque hay campos que TODAS las instalaciones necesitan: geometría (`points`), tamaño (`diameter`), tipo de sistema (`system`). Al tenerlos como campos dedicados garantizo que siempre existen con valores válidos. En `custom` va lo específico de cada instalación que otras no necesitan."

**Ejemplo concreto:**
"Saneamiento necesita `installation_type_horizontal` y `face`, pero Clima no. Clima necesita `velocidad_aire` y `caudal`, pero Saneamiento no. Eso va en `custom`. Pero ambos necesitan `diameter` y `points`, por eso van en campos fijos."

---

### Escenario 4: "¿Por qué `diameter` es float y no string tipo '110mm'?"

**Respuesta:**
"Porque se usa en cálculos matemáticos: área de sección, offsets para modelado, comparaciones (si diameter >= 110 es bajante). Si fuera string, tendría que parsearlo cada vez. Pero sí tengo `section_type` como string para display."

**Ejemplo concreto:**
"En el hook de Braian, cuando crea el tubo 3D necesita calcular `radio = diameter / 2` para el BRep. Con float es directo, con string tendría que hacer `float(section_type.replace('mm', ''))` en cada cálculo."

---

### Escenario 5: "¿Por qué el layer se asigna en el hook y no lo decide la librería?"

**Respuesta:**
"Porque cada instalación tiene su propia lógica de layers. Saneamiento horizontal FABRICA va a layer 40148, OBRA a 40149. Clima tiene otros layers completamente diferentes. La librería no puede saber todas estas reglas. Por eso devuelvo la metadata completa en `custom` y el hook de cada instalación traduce eso al layer que necesita."

**Ejemplo concreto:**
"En el hook de Saneamiento leo `installation_type_horizontal` del `custom`, y según si es 'FABRICA' u 'OBRA' asigno layer 40148 o 40149. Esta regla es específica de Saneamiento, Clima tiene otras reglas totalmente distintas."

---

### Escenario 6: "¿Por qué devuelves metadata en lugar de crear directamente los elementos 3D?"

**Respuesta:**
"Separación de responsabilidades. La librería maneja la interacción de usuario (captura puntos, edición, undo, bifurcación), pero no sabe cómo crear modelos 3D específicos de cada instalación. Saneamiento crea tubos PVC con flechas, Clima conductos rectangulares con aislamiento. Eso lo sabe cada instalación en su hook."

**Ejemplo concreto:**
"Si metiera la lógica de crear tubos PVC en la librería, ¿qué hago cuando venga Clima que usa conductos de chapa? ¿Y Electricidad con bandejas? Con hooks, cada instalación implementa su propia creación de 3D usando la metadata que le paso."

---

### Escenario 7: "¿Esto es compatible con el código viejo de Saneamiento?"

**Respuesta:**
"Sí. El código viejo usaba dicts sin estructura. Tengo `SegmentMetadata.from_legacy(dict)` que convierte los dicts viejos al formato nuevo. Y `seg_meta.to_dict()` que convierte al revés si hace falta. La metadata custom se accede con `.get()` que es seguro aunque el campo no exista."

**Ejemplo concreto:**
"Si Saneamiento quiere mantener su paleta actual, puede. Solo cambia el script `.py` que usa la librería, la paleta `.pyp` queda igual. Y su lógica de layers, botones específicos, todo se mantiene en el hook personalizado."

---

### Escenario 8: "¿Por qué `custom` es un dict libre y no campos específicos?"

**Respuesta:**
"Porque las necesidades evolucionan. Si mañana una normativa requiere un nuevo campo, se añade en `custom` sin modificar la librería. Y cada instalación tiene necesidades únicas que otras no comparten. Con `custom` dict no hay breaking changes cuando algo cambia."

**Ejemplo concreto:**
"Hoy Saneamiento necesita `pendiente`, pero si mañana necesita `inspector_notes` o `fecha_instalacion`, lo añade en `custom` sin tocar la librería. Y eso no afecta a Clima que tiene sus propios campos en su `custom`."

---

## Tips para la Conversación

### Si te preguntan algo que no sabes:

**Respuesta honesta:**
"No tengo todos los detalles técnicos en la cabeza ahora mismo, pero el diseño está documentado. ¿Puedo revisar el código específico y te respondo en 10 minutos?"

### Si te cuestionan una decisión:

**Enfoque constructivo:**
"Entiendo tu punto. La razón por la que lo hice así es [razón]. Si ves una forma mejor, puedo ajustarlo, el código está estructurado para ser flexible."

### Si te piden justificar el tiempo invertido:

**Enfoque de valor:**
"Esta librería reduce código de 6500 líneas a 500 por instalación (92% menos). Eso significa:
- Menos bugs potenciales
- Más fácil de mantener
- Nuevas instalaciones se crean en días en lugar de semanas
- Features nuevas (bifurcación, undo) vienen gratis para todas las instalaciones"

---

**Versión del documento:** 1.0  
**Última actualización:** 2025-01-15
