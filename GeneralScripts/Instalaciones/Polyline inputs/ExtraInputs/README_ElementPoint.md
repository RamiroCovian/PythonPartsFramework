# ElementPoint (Allplan PythonPart)
**Autor:** Tomas Tessio  
**Fecha:** 2025-10-22

> **Estado:** prototipo funcional
> Falta validar a fondo en proyectos reales y ajustar UI/ergonomía según feedback.

## ¿Qué intenta resolver?
Definir **puntos de línea** (inicio, paso, bifurcación, final) **asociados a objetos** de una instalación (interruptor, enchufe, luminaria, caja, tablero, etc.).  
La asociación sirve para:
- reutilizar un **mismo objeto** en **distintos caminos**;
- **restringir** qué rol puede adoptar cada objeto (ej.: interruptor → *final*);
- exportar un **modelo de datos** consistente (JSON) para etapas posteriores (routing/optimización/documentación).

## Flujo de uso
1. En la paleta, elegir `ElementKey` (p. ej. `switch`, `outlet`, `luminaire`, `junction_box`, `panel`).  
2. Elegir `PointRole` o usar los botones (`Inicial/Paso/Bifurcación/Final`).  
   - Si el rol no es válido para el elemento, el script **fuerza** el primer rol permitido y avisa por consola.
3. Clic en el plano para **marcar puntos**. Cada click dibuja un **marcador cuadrado** de referencia.  
4. Al marcar **Final**, se **cierra el tramo**, crea una `Polyline3D` y **persiste** en JSON.  
5. Editor básico:
   - `1001` *Crear* (toggle) → dibujar polilínea activa.
   - `1002` *Guardar* → mueve la activa a “guardadas”.
   - `1003` *Finalizar* → guarda y crea todas en el documento.
   - `1004` *Borrar sección* (placeholder en esta versión compacta).
   - `1006` *Bifurcar* (placeholder).

## Parámetros de paleta (.pyp)
- `ElementKey` (String) — clave de elemento.  
- `PathId` (int) — se usa también como **color**.  
- `SegmentId` (int) — etiqueta opcional del segmento.  
- `PointRole` (int 0..3) — 0 Inicial · 1 Paso · 2 Bifurcación · 3 Final.  
- `CommonProp`, `SymbolCommonProps` (CommonProperties).  
- `EnableAssistWndClick`, `EnableZCoordinate`, `EnableUndoStep`, `SetProjectionBase0`.  
- Botones: 2100..2103 (roles) · 1001/1002/1003/1004/1006 (editor).  
- `CheckBoxValue` — reservado para modo “insertar punto”.

## Catálogo y validación
En `ElementPoint.py`:
```python
ELEMENT_CATALOG = {
  "switch":       {"label": "Interruptor",   "allowed_roles": [3]},
  "outlet":       {"label": "Enchufe",       "allowed_roles": [3]},
  "luminaire":    {"label": "Luminaria",     "allowed_roles": [3]},
  "junction_box": {"label": "Caja conexiones","allowed_roles": [0,1,2,3]},
  "panel":        {"label": "Tablero",       "allowed_roles": [0,1,2,3]}
}
```
Podés **agregar/editar** claves y roles admitidos. El `DEFAULT_ELEMENT_KEY` es `junction_box`.

## Persistencia (JSON)
Archivo: `element_points_XXXXXXXX.json` en el Escritorio. Se **mergea por `path_id`**.  
Ejemplo de estructura por punto:
```json
{
  "x": 1000.0, "y": 250.0, "z": 0.0,
  "segmento": 1,
  "tipo": "Final",
  "color": 1,
  "element": {"key": "switch", "label": "Interruptor"}
}
```

## Tolerancias y marcadores
- Detección de proximidad: **5 mm** (vértice) / ~8 mm (segmento).  
- Marcador: **cuadrado** centrado en el punto (placeholder, ajustable).

## Limitaciones actuales / TODO
- Editor reducido: *borrar/bifurcar/insertar* tienen placeholders. Si necesitás el editor “completo” (drag, midpoints,
  selección por marco, extensiones), se puede portar desde `CommonPoint`.  
- Falta **validación integral** en proyectos grandes (performance y UX).  
- UI: `ElementKey` es `String`. Se recomienda cambiarlo a **lista desplegable** con claves válidas y labels.

## Instalación
1. Copiar `ElementPoint.py` y `ElementPoint.pyp` a tu carpeta de PythonParts.  
2. Cargar el PythonPart en Allplan.  
3. (Opcional) Ajustar el catálogo en el script y las opciones visuales en el `.pyp`.

## Autorización de cambios
El script mantiene compatibilidad con flujos existentes de captura/creación y sólo añade la capa de **elementos** con
validación de roles y persistencia asociada.

---

**Contacto / Autor:** Tomas Tessio
