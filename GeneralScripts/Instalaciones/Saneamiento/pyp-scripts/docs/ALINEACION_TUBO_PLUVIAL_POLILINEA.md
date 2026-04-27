# Alineación del tubo Pluvial con la polilínea (Saneamiento / PolyLib)

Documentación del ajuste aplicado para que el tubo **Pluvial** Ø110 (`tub_pvc_tricapa_p_110`, geometría compartida vía `TuboPVCConFlecha` en `tub_pvc_tricapa_v_script.py`) coincida con el **inicio y el recorrido** del segmento de polilínea, y no quede “metido” respecto a los puntos inicial y final. Pluvial Ø40 sigue usando `tub_pvc_tricapa_v`.

## Contexto del problema

- El modelo 3D del tubo Pluvial es **asimétrico**: cuerpo cilíndrico + **anillo** (y en el PythonPart completo también hay flecha; en el flujo de polilínea solo se usa el **primer** elemento del resultado, el tubo).
- En `PipelineProcessor` (`utils/geo_handler.py`) el tramo se colocaba llevando el **centroide** del BRep al **punto medio** del segmento (`p_centro`), tras escalar la longitud al valor del tramo (`longitud_recortada`).
- En geometrías con anillo concentrado en un extremo, el **centroide no coincide** con el eje geométrico “útil” entre el primer y último punto del tramo. El largo escalaba bien con la polilínea, pero el sólido **arrancaba y terminaba antes** que los vértices de la polilínea (desplazamiento respecto al eje del segmento).

## Solución implementada

Se añadió un paso **solo para saneamiento** (`element_type_core == "tubo_saneamiento"`), después de `modificar_dimensiones_brep` y `_aplicar_transformacion`:

1. **Método nuevo:** `_align_saneamiento_tube_along_segment` en la clase `PipelineProcessor`.
2. **Qué hace:**
   - Toma el `ModelElement3D` ya orientado en el espacio modelo.
   - Lee los vértices del BRep.
   - Define el **inicio efectivo del tramo** en línea recta:  
     `p_line_start = seg.start + v_unit * (cut_start + offset_inicio)`  
     (misma lógica que los recortes por codo ya usados en `process`).
   - Proyecta cada vértice sobre la dirección del segmento `v_unit` con origen en `p_line_start` (producto escalar).
   - Calcula el mínimo de esas proyecciones `t_min`. Si no es ~0, el sólido está desplazado a lo largo del eje.
   - Aplica un `Move` del BRep un vector **`v_unit * (-t_min)`** para que la proyección mínima quede en **0**, es decir, que el tubo **empiece alineado** con el inicio efectivo del segmento en la dirección de la polilínea.
3. **Dónde se llama:** en `PipelineProcessor.process()`, inmediatamente después de crear el elemento **outer** y, si existe, el **inner** (misma corrección para ambos).

## Archivos tocados

| Archivo | Cambio |
|---------|--------|
| `Instalaciones/Saneamiento/pyp-scripts/utils/geo_handler.py` | Nuevo `_align_saneamiento_tube_along_segment`; llamadas condicionales a `tubo_saneamiento` tras `_aplicar_transformacion`. |

## Notas

- No altera el flujo de **Agua** u otras instalaciones que usan `conducto` u otros `element_type_core`; la condición es explícitamente `tubo_saneamiento`.
- Si el escalado longitudinal ya iguala la extensión del sólido a `longitud_recortada`, al fijar el **inicio** en el eje el **final** queda coherente con el tramo. Si en tramos muy especiales (p. ej. casos límite 3D) hubiera desfase residual, habría que revisar con ese caso concreto.

## Fecha

Documento alineado con el cambio registrado en el repositorio de scripts de **Instalaciones / Saneamiento** (PolyLib + `saneamiento_polyline`).
