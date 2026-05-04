# Estructura de Datos: polyline_base_lib

**Documento técnico** para desarrolladores de instalaciones (Saneamiento, Clima, etc.)  
**Versión:** 1.0  
**Fecha:** 2025-01-15

---

## Índice

1. [Estructura Principal: SegmentMetadata](#estructura-principal-segmentmetadata)
2. [Ejemplos Reales](#ejemplos-reales)
3. [Hook de Elemento](#hook-de-elemento)
4. [Lista Completa de Info Disponible](#lista-completa-de-info-disponible)
5. [Print de Salida Real](#print-de-salida-real)
6. [Guía de Migración](#guía-de-migración)
7. [Checklist de Validación](#checklist-de-validación)
8. [Resumen](#resumen)

---

## Estructura Principal: SegmentMetadata

```python
# polyline_base_lib.py (líneas 318-413)
@dataclass
class SegmentMetadata:
    """Metadata for a single polyline segment.
    
    """
    
    # GEOMETRÍA (OBLIGATORIO)
    points: List[Any]  # Lista de Point3D (inicio, fin del segmento)
                       # Ejemplo: [Point3D(0, 0, 0), Point3D(1000, 0, 0)]
    
    # PROPIEDADES BÁSICAS (OPCIONALES - tienen defaults)
    diameter: float = 110.0              # Diámetro en mm
    section_type: str = "110mm"          # Tipo de sección (string descriptivo)
    system: str = "Pluvial"              # Sistema (Pluvial/Fecal/Clima/etc.)
    label: str = ""                      # Etiqueta del segmento
    
    # ORGANIZACIÓN (OPCIONALES)
    layer: Optional[str] = None          # Layer de Allplan (puede ser número o nombre)
    path_id: Optional[int] = None        # ID del path (para agrupación)
    segment_id: Optional[int] = None     # ID del segmento dentro del path
    color_id: Optional[int] = None       # Color de Allplan (1-255)
    
    # CAPTURA/ROLES (OPCIONAL - para workflow PointInput)
    point_roles: List[int] = []          # Roles de puntos: 
                                         # [0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final]
    
    # EXTENSIBILIDAD (ILIMITADO)
    custom: Dict[str, Any] = {}          # Diccionario libre para cualquier metadata adicional
```

---

## Ejemplos Reales

### Ejemplo 1: Segmento Horizontal FABRICA 110mm (Saneamiento)

```python
segment_meta = SegmentMetadata(
    # Geometría
    points=[
        AllplanGeo.Point3D(0.0, 0.0, 3000.0),      # Punto inicial (techo)
        AllplanGeo.Point3D(5000.0, 0.0, 3000.0)    # Punto final (techo)
    ],
    
    # Propiedades básicas
    diameter=110.0,
    section_type="110mm",
    system="Pluvial",
    label="SANE P110",
    
    # Organización
    layer=None,  # Se asigna en el hook según metadata
    path_id=1,
    segment_id=1,
    color_id=3,
    
    # Roles (si viene de captura)
    point_roles=[0, 1],  # [Inicial, Paso]
    
    # Metadata específica de Saneamiento
    custom={
        # Configuración de instalación
        'installation_type_horizontal': 'FABRICA',  # OBRA | FABRICA
        'installation_type_vertical': 'TD',         # EN | TD | IS
        'face': 'X',                                # X | Y (para EN)
        
        # Datos técnicos
        'flow_direction': 'downstream',
        'material': 'PVC',
        'pendiente': 2.0,  # % pendiente
        
        # Tracking interno
        'path_idx': 0,     # Índice en saved_paths
        'seg_idx': 0,      # Índice dentro del path
        
        # Metadata adicional
        'installation_date': '2025-12-18',
        'inspector_notes': 'Segmento en buen estado',
        'segment_number': 1
    }
)
```

### Ejemplo 2: Segmento Vertical EN Empotrado 40mm Cara X

```python
segment_meta = SegmentMetadata(
    # Geometría (vertical - Z varía)
    points=[
        AllplanGeo.Point3D(1000.0, 2000.0, 0.0),     # Suelo
        AllplanGeo.Point3D(1000.0, 2000.0, 2800.0)   # Techo
    ],
    
    # Propiedades básicas
    diameter=40.0,
    section_type="40mm",
    system="Fecal",
    label="SANE F40",
    
    # Custom metadata
    custom={
        'installation_type_horizontal': 'OBRA',
        'installation_type_vertical': 'EN',
        'face': 'X',
        'material': 'PVC',
        'is_vertical': True,
        'path_idx': 2,
        'seg_idx': 0
    }
)
```

### Ejemplo 3: Conducto de Clima (Impulsión)

```python
segment_meta = SegmentMetadata(
    # Geometría
    points=[
        AllplanGeo.Point3D(0.0, 0.0, 2500.0),
        AllplanGeo.Point3D(8000.0, 0.0, 2500.0)
    ],
    
    # Propiedades básicas
    diameter=400.0,  # Diámetro en mm (conducto circular)
    section_type="400mm",
    system="Impulsion",
    label="CLIMA IMP 400",
    
    # Custom metadata específica de Clima
    custom={
        'tipo_conducto': 'IMPULSION',
        'velocidad_aire': 4.5,         # m/s
        'caudal': 350.0,               # m³/h
        'presion': 80.0,               # Pa
        'material_conducto': 'Chapa galvanizada',
        'aislamiento': True,
        'espesor_aislamiento': 25.0,   # mm
    }
)
```

---

## Hook de Elemento

La librería llama a este hook una vez por cada segmento al crear elementos 3D:

```python
def element_creation_hook(seg_meta: SegmentMetadata, 
                          common_prop: AllplanBaseElements.CommonProperties):
    """Hook que la instalación implementa.
    
    La librería llama a este hook para cada segmento guardado.
    
    Args:
        seg_meta: SegmentMetadata con toda la info del segmento
        common_prop: CommonProperties base (puede modificarse)
    
    Returns:
        List[ModelElement3D]: Lista de elementos 3D a crear
    """
    
    print("\n" + "="*60)
    print(f"[HOOK] Creando elementos para segmento:")
    print(f"  Points: {len(seg_meta.points)} puntos")
    print(f"  Start: ({seg_meta.points[0].X:.1f}, {seg_meta.points[0].Y:.1f}, {seg_meta.points[0].Z:.1f})")
    print(f"  End: ({seg_meta.points[1].X:.1f}, {seg_meta.points[1].Y:.1f}, {seg_meta.points[1].Z:.1f})")
    print(f"  Diameter: {seg_meta.diameter}mm")
    print(f"  System: {seg_meta.system}")
    print(f"  Section: {seg_meta.section_type}")
    print(f"  Label: {seg_meta.label}")
    print(f"  Custom metadata: {seg_meta.custom}")
    print("="*60)
    
    # PASO 1: TRADUCIR METADATA A LAYER DE ALLPLAN
    
    # Leer metadata de instalación
    installation_h = seg_meta.custom.get('installation_type_horizontal', 'OBRA')
    installation_v = seg_meta.custom.get('installation_type_vertical', 'TD')
    face = seg_meta.custom.get('face', 'X')
    
    # Determinar orientación
    p1, p2 = seg_meta.points[0], seg_meta.points[1]
    dx = abs(p2.X - p1.X)
    dy = abs(p2.Y - p1.Y)
    dz = abs(p2.Z - p1.Z)
    
    is_horizontal = (dz < 10.0 and (dx > 10.0 or dy > 10.0))
    is_vertical = (dx < 10.0 and dy < 10.0 and dz > 10.0)
    
    # Asignar layer según tipo (EJEMPLO SANEAMIENTO)
    if is_horizontal:
        if installation_h == 'FABRICA':
            common_prop.Layer = 40148  # IS_CON_SANE_FAB
            print(f"[HOOK] Layer 40148 (FABRICA)")
        else:
            common_prop.Layer = 40149  # IS_CON_SANE_OBR
            print(f"[HOOK] Layer 40149 (OBRA)")
    
    elif is_vertical:
        if seg_meta.diameter >= 110.0:
            # Bajante
            if installation_v == 'TD':
                common_prop.Layer = 40151
            elif installation_v == 'IS':
                common_prop.Layer = 40152
            else:  # EN
                common_prop.Layer = 40150
            print(f"[HOOK] Layer bajante {common_prop.Layer}")
        else:
            # Pared (25/40mm)
            if installation_v == 'EN':
                if face == 'X':
                    common_prop.Layer = 40106  # KN_X_AIGUA
                else:
                    common_prop.Layer = 40108  # KN_Y_AIGUA
            elif installation_v == 'TD':
                common_prop.Layer = 40061
            else:
                common_prop.Layer = 40061
            print(f"[HOOK] Layer pared {common_prop.Layer}")
    
    # PASO 2: CALCULAR PROPIEDADES GEOMÉTRICAS
    
    import polyline_base_lib as PBL
    
    length = PBL.get_segment_length(seg_meta)  # Longitud en mm
    direction = PBL.get_segment_direction_vector(seg_meta)  # Vector normalizado (dx, dy, dz)
    
    print(f"[HOOK] Length: {length:.1f}mm")
    print(f"[HOOK] Direction: ({direction[0]:.3f}, {direction[1]:.3f}, {direction[2]:.3f})")
    
    # PASO 3: CREAR MODELOS 3D
    
    elements = []
    
    try:
        # Importar modelos
        from Tub_PVC_TricapaV_005 import TuboPVCConFlecha
        
        # Crear builder
        builder = TuboPVCConFlecha(build_ele)
        
        # Obtener config del builder
        config = builder.CONFIG.get(seg_meta.diameter, builder.CONFIG[110.0])
        
        # Construir geometría
        brep = builder._build_tube(length, seg_meta.diameter, config)
        flecha_poly = builder._build_arrow(length, seg_meta.diameter, config)
        
        # Aplicar transformaciones
        # ... (lógica de rotación/traslación) ...
        
        # Crear elementos con layer asignado
        tube_elem = AllplanBasisElements.ModelElement3D(common_prop, brep)
        arrow_elem = AllplanBasisElements.ModelElement3D(arrow_prop, flecha_poly)
        
        elements.extend([tube_elem, arrow_elem])
        
        print(f"[HOOK] Creados {len(elements)} elementos 3D")
        
    except Exception as ex:
        print(f"[HOOK] Error creando modelos: {ex}")
        # Fallback a geometría simple
        line = AllplanGeo.Line3D(p1, p2)
        elements.append(AllplanBasisElements.ModelElement3D(common_prop, line))
    
    return elements
```

### Registro del Hook

```python
def create_script_object(build_ele, script_object_data):
    """Inicializar script con la librería."""
    
    # Crear script object
    script_object = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    
    # Registrar hook de creación de elementos
    script_object.element_creation_hook = element_creation_hook
    
    return script_object
```

---

## Lista Completa de Info Disponible

```python
# INFO DISPONIBLE EN CADA SEGMENTO

# 1. GEOMETRÍA (siempre disponible)
seg_meta.points[0]              # Point3D - inicio del segmento
seg_meta.points[1]              # Point3D - fin del segmento

# Helpers geométricos (módulo polyline_base_lib):
PBL.get_segment_length(seg_meta)           # float - longitud en mm
PBL.get_segment_direction_vector(seg_meta) # tuple - (dx, dy, dz) normalizado
PBL.find_closest_point_on_segment(seg_meta, query_point) # Point3D - punto más cercano

# 2. PROPIEDADES BÁSICAS (siempre disponibles, tienen defaults)
seg_meta.diameter               # float - diámetro en mm (default: 110.0)
seg_meta.section_type           # str - tipo de sección (default: "110mm")
seg_meta.system                 # str - sistema (default: "Pluvial")
seg_meta.label                  # str - etiqueta descriptiva (default: "")

# 3. ORGANIZACIÓN (opcionales, pueden ser None)
seg_meta.layer                  # Optional[str] - layer de Allplan
seg_meta.path_id                # Optional[int] - ID del path (para agrupación)
seg_meta.segment_id             # Optional[int] - ID del segmento dentro del path
seg_meta.color_id               # Optional[int] - color Allplan (1-255)

# 4. ROLES DE CAPTURA (opcional, lista vacía por defecto)
seg_meta.point_roles            # List[int] - roles de puntos
                                # [0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final]

# 5. METADATA CUSTOM (diccionario libre)
# Ejemplos para Saneamiento:
seg_meta.custom['installation_type_horizontal']  # str - tipo instalación horizontal (OBRA/FABRICA)
seg_meta.custom['installation_type_vertical']    # str - tipo instalación vertical (EN/TD/IS)
seg_meta.custom['face']                          # str - cara (X/Y)
seg_meta.custom['material']                      # str - material (PVC, etc.)
seg_meta.custom['flow_direction']                # str - dirección flujo
seg_meta.custom['pendiente']                     # float - pendiente %

# Ejemplos para Clima:
seg_meta.custom['tipo_conducto']      # str - IMPULSION / RETORNO
seg_meta.custom['velocidad_aire']     # float - m/s
seg_meta.custom['caudal']             # float - m³/h
seg_meta.custom['presion']            # float - Pa

# Tracking interno (automático):
seg_meta.custom['path_idx']           # int - índice path en saved_paths
seg_meta.custom['seg_idx']            # int - índice segmento dentro del path

# 6. MÉTODOS ÚTILES
seg_meta.to_dict()                    # Dict - convierte a dict (para JSON/serialización)
SegmentMetadata.from_legacy(dict)     # Crea desde dict (compatibilidad)
```

---

## Print de Salida Real

Output de consola al crear elementos:

```
================================================================================
[mvp_example] _create_demo_elements CALLED!
================================================================================
[mvp_example] Segment #1: Length=5000mm, Vertical=False
[mvp_example] Diameter=110.0mm, System=Pluvial
[mvp_example] Added custom metadata: {
  'flow_direction': 'downstream',
  'material': 'PVC',
  'installation_date': '2025-12-18',
  'inspector_notes': 'Segment at 0,0',
  'segment_number': 1,
  'installation_type_horizontal': 'FABRICA',
  'installation_type_vertical': 'TD',
  'face': 'X',
  'path_idx': 0,
  'seg_idx': 0
}

[HOOK] Creando elementos para segmento:
  Points: 2 puntos
  Start: (0.0, 0.0, 0.0)
  End: (5000.0, 0.0, 0.0)
  Diameter: 110.0mm
  System: Pluvial
  Section: 110mm
  Label: D110 P
  Custom metadata: {...}
================================================================================
[HOOK] Length: 5000.0mm
[HOOK] Direction: (1.000, 0.000, 0.000)
[HOOK] Layer 40148 (FABRICA)
[HOOK] Creating REAL 3D tube (TuboPVCConFlecha)
[HOOK] Created 2 elements (tube + arrow)
[HOOK] Total: 2 elements
================================================================================
```

---

## Guía de Migración

### Paso 1: Crear Wrapper Script

```python
# Archivo: Saneamiento/polilinea_saneamiento.py (nuevo)
"""Script de Saneamiento usando polyline_base_lib."""

import sys
import os

# Importar librería
from Clima.models_lib.py import polyline_base_lib as PBL

# Configurar para Saneamiento
PBL.DEFAULT_SEGMENT_DIAMETER = 110.0
PBL.DEFAULT_SEGMENT_SYSTEM = "Pluvial"
PBL.FUSION_TOLERANCE_MM = 30.0

CONFIG = PBL.PolylineBaseConfig(
    drawing_mode=PBL.DRAWING_MODE_2D,
    allow_insert_point_mode=True,
)

def create_script_object(build_ele, script_object_data):
    """Crear ScriptObject usando la librería."""
    script_object = PBL.initialize_script_object(build_ele, script_object_data, CONFIG)
    
    # Registrar hooks
    script_object.element_creation_hook = element_creation_hook
    script_object.event_handler_hook = on_control_event
    
    return script_object

# Implementar hooks...
```

### Paso 2: Implementar Hook de Elementos

```python
def element_creation_hook(seg_meta, common_prop, build_ele):
    """Hook de creación - traduce metadata a layers y crea 3D."""
    
    # 1. Traducir metadata a layer Allplan
    installation_h = seg_meta.custom.get('installation_type_horizontal', 'OBRA')
    # ... lógica de layers ...
    
    # 2. Crear modelos 3D
    # ... código de creación ...
    
    return elements
```

### Paso 3: Event Handlers (Botones de Palette)

```python
def on_control_event(build_ele, event_id):
    """Handlers para botones específicos de Saneamiento."""
    
    if event_id == 1007:  # Aplicar diámetro
        return _apply_diameter_to_selected(...)
    
    elif event_id == 1009:  # Aplicar layers
        return _apply_layers_to_selected(...)
    
    return True
```

### Paso 4: Mantener Palette

```xml
<!-- polilinea_saneamiento.pyp -->
<Script>
    <Name>Saneamiento\polilinea_saneamiento.py</Name>
    <Title>Saneamiento Polyline (Library)</Title>
    <Version>2.0</Version>
</Script>

<!-- Resto de la palette sin cambios -->
```

---

## Checklist de Validación

### Validar con Braian (Modelos 3D)

Verificar que toda la info necesaria está disponible:

```python
# GEOMETRÍA BÁSICA
seg_meta.points[0], seg_meta.points[1]  # Inicio/fin del segmento
PBL.get_segment_length(seg_meta)        # Longitud total en mm
PBL.get_segment_direction_vector(...)   # Dirección normalizada (dx, dy, dz)

# PROPIEDADES DEL TUBO/CONDUCTO
seg_meta.diameter                       # Diámetro en mm
seg_meta.section_type                   # Tipo de sección ("110mm", "400x200", etc.)
seg_meta.system                         # Sistema (Pluvial/Fecal/Impulsion/Retorno)

# CONFIGURACIÓN DE INSTALACIÓN
seg_meta.custom['installation_type_horizontal']  # OBRA / FABRICA
seg_meta.custom['installation_type_vertical']    # EN / TD / IS
seg_meta.custom['face']                          # X / Y (para EN)

# ORGANIZACIÓN VISUAL (ALLPLAN)
common_prop.Layer                       # Layer de Allplan (40148, 40149, etc.)
seg_meta.color_id                       # Color opcional (1-255)
seg_meta.label                          # Etiqueta descriptiva

# METADATA ADICIONAL (EXTENSIBLE)
seg_meta.custom[...]                    # Cualquier metadata adicional
                                        # Material, velocidad, presión, etc.
```

### Validar Compatibilidad

```python
# COMPATIBILIDAD
SegmentMetadata.from_legacy(dict)       # Convierte dicts viejos a SegmentMetadata
seg_meta.to_dict()                      # Convierte SegmentMetadata a dict
custom.get('key', default)              # Acceso seguro con defaults
```

---

## Resumen

### Estructura de Retorno

```python
SegmentMetadata(
    # GEOMETRÍA (obligatorio)
    points=[Point3D(...), Point3D(...)],
    
    # BÁSICO (con defaults)
    diameter=110.0,
    section_type="110mm",
    system="Pluvial",
    label="SANE P110",
    
    # ORGANIZACIÓN (opcional)
    layer=None,
    path_id=1,
    segment_id=1,
    color_id=3,
    point_roles=[0, 1],
    
    # EXTENSIBLE (ilimitado)
    custom={
        # Metadata específica de instalación
        'installation_type_horizontal': 'FABRICA',
        'installation_type_vertical': 'EN',
        'face': 'X',
        # ... lo que se necesite
    }
)
```

### Helpers Disponibles

```python
PBL.get_segment_length(seg_meta)           # float (mm)
PBL.get_segment_direction_vector(seg_meta) # (dx, dy, dz)
PBL.find_closest_point_on_segment(...)     # Point3D
```

---

**Versión del documento:** 1.0  
**Última actualización:** 2025-01-15
