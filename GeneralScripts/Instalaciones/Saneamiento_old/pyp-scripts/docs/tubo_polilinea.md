# Cómo hacer que el tubo siga el largo de la polilínea

El código en [Saneamiento.py](../Saneamiento.py) ya implementa este comportamiento. Aquí está la explicación del flujo:

---

## 1. Iteración sobre los segmentos de la polilínea

El código recorre cada par de puntos consecutivos (`p1`, `p2`) de la polilínea guardada:

```python
# Línea 2555
for i in range(len(pts) - 1):
    p1, p2 = pts[i], pts[i+1]
```

---

## 2. Cálculo de la longitud del segmento

La longitud se calcula usando la **fórmula de distancia euclidiana 3D**:

```python
# Líneas 2563 y 2638
dx, dy, dz = p2.X - p1.X, p2.Y - p1.Y, p2.Z - p1.Z
seg_len = (dx*dx + dy*dy + dz*dz) ** 0.5  # Distancia 3D
```

Esta fórmula: `sqrt(dx² + dy² + dz²)` da la longitud exacta del segmento en cualquier dirección 3D.

---

## 3. Aplicación de recortes (trims)

Opcionalmente se aplican recortes en los extremos (para codos, bifurcaciones, etc.):

```python
# Línea 2898
new_len = seg_len - (s_trim + e_trim)  # Longitud final del tubo
```

---

## 4. Construcción del tubo en coordenadas locales

La función `_build_local_tube()` (línea 1469) crea el tubo con la longitud calculada, orientado a lo largo del eje +X local:

```python
# Línea 3009
brep, flecha = _build_local_tube(new_len, diameter, arrow_to_end, s_trim, e_trim)
```

Internamente usa `BRep3D.CreateCuboid()` con el `length_mm` especificado.

---

## 5. Orientación y posicionamiento en el espacio 3D

La función clave `_orient_and_place()` (línea 1711) transforma el tubo desde su posición local al espacio mundial:

```python
def _orient_and_place(geom, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D):
    # Calcular vector dirección
    vx = p2.X - p1.X; vy = p2.Y - p1.Y; vz = p2.Z - p1.Z
    norm = (vx*vx + vy*vy + vz*vz) ** 0.5
    vx /= norm; vy /= norm; vz /= norm
    
    # Calcular ángulo de rotación (de eje +X hacia la dirección del segmento)
    dot = max(min(vx*1.0 + vy*0.0 + vz*0.0, 1.0), -1.0)
    angle = math.acos(dot)
    
    # Calcular eje de rotación (producto cruz de X con la dirección)
    ax = 0.0; ay = -vz; az = vy
    
    # Rotar el tubo
    rot_m = AllplanGeo.Matrix3D()
    rot_m.SetRotation(AllplanGeo.Line3D(0, 0, 0, ax, ay, az), AllplanGeo.Angle(angle))
    rotated = AllplanGeo.Transform(geom, rot_m)
    
    # Trasladar a la posición inicial (p1)
    trans_m = AllplanGeo.Matrix3D()
    trans_m.SetTranslation(AllplanGeo.Vector3D(p1.X, p1.Y, p1.Z))
    return AllplanGeo.Transform(rotated, trans_m)
```

Y se aplica así:

```python
# Línea 3010
brep_w = _orient_and_place(brep, np1, np2)
```

---

## Resumen del flujo completo

1. **Obtener puntos** de la polilínea: `p1`, `p2`
2. **Calcular longitud**: `seg_len = sqrt((p2.X-p1.X)² + (p2.Y-p1.Y)² + (p2.Z-p1.Z)²)`
3. **Ajustar longitud** restando recortes: `new_len = seg_len - trims`
4. **Crear tubo** en local con esa longitud: `_build_local_tube(new_len, diameter, ...)`
5. **Rotar y trasladar** al espacio mundial: `_orient_and_place(brep, p1, p2)`
6. **Crear elemento**: `ModelElement3D(props, brep_w)`

---

## Código simplificado de ejemplo

Si quieres implementar algo similar desde cero:

```python
import math
import NemAll_Python_Geometry as AllplanGeo

def crear_tubo_siguiendo_polilinea(puntos, diametro):
    """
    Crea tubos que siguen cada segmento de una polilínea.
    
    Args:
        puntos: Lista de Point3D que forman la polilínea
        diametro: Diámetro del tubo en mm
    """
    tubos = []
    
    for i in range(len(puntos) - 1):
        p1, p2 = puntos[i], puntos[i+1]
        
        # 1. Calcular longitud del segmento
        dx = p2.X - p1.X
        dy = p2.Y - p1.Y
        dz = p2.Z - p1.Z
        longitud = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if longitud < 1.0:  # Evitar segmentos muy cortos
            continue
        
        # 2. Crear tubo en coordenadas locales (eje +X)
        axis = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0))
        tubo_local = AllplanGeo.BRep3D.CreateCuboid(axis, longitud, diametro, diametro)
        
        # 3. Calcular rotación de +X hacia la dirección del segmento
        ux, uy, uz = dx/longitud, dy/longitud, dz/longitud
        dot = max(min(ux, 1.0), -1.0)  # Producto punto con (1,0,0)
        angulo = math.acos(dot)
        
        # Eje de rotación = (1,0,0) x (ux,uy,uz)
        ax, ay, az = 0.0, -uz, uy
        axis_norm = math.sqrt(ax*ax + ay*ay + az*az)
        
        if axis_norm > 1e-9:
            ax, ay, az = ax/axis_norm, ay/axis_norm, az/axis_norm
        else:
            ax, ay, az = 0.0, 0.0, 1.0  # Paralelo a X, usar Z como eje
        
        # 4. Aplicar rotación
        rot = AllplanGeo.Matrix3D()
        rot.SetRotation(AllplanGeo.Line3D(0, 0, 0, ax, ay, az), AllplanGeo.Angle(angulo))
        tubo_rotado = AllplanGeo.Transform(tubo_local, rot)
        
        # 5. Trasladar a la posición p1
        trans = AllplanGeo.Matrix3D()
        trans.SetTranslation(AllplanGeo.Vector3D(p1.X, p1.Y, p1.Z))
        tubo_final = AllplanGeo.Transform(tubo_rotado, trans)
        
        tubos.append(tubo_final)
    
    return tubos
```

