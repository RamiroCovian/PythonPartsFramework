# Registro de implementación — Saneamiento

## 2026-05-13 — Bifurcación (TE): tubos separados según orden de dibujo

**Síntoma:** Dibujando primero un tramo, luego la rama a 45° y después el segundo tramo del troncal, la TE quedaba visualmente separada de los tubos. Con dos tramos rectos del troncal y luego la rama, el resultado era correcto.

**Causa:** En `geo_handler.PolygonScriptInteractorModel.process`, el bloque que suma recortes extra de codos (45°, 90°, 2×45°) y `offset_codo` sobre `segment_cuts` se ejecutaba **antes** de colocar la TE y **no** comprobaba si el vértice era un nodo TE. Los recortes de TE ya llegan correctos desde `vertex_utils.register_te_cuts_into` (vía `compute_segment_cuts_for_all_paths`). Al sumar encima los trims de codo del troncal local (ángulo que antes parecía un codo hasta completar la tercera pierna), el tubo quedaba demasiado recortado y la derivación desalineada.

**Solución:** Si el vértice coincide con una clave de `te_nodes` (mismo redondeo que el resto del flujo TE), no aplicar en ese vértice offsets ni recortes adicionales de codo en ese bloque inicial.

**Archivos:** `pyp-scripts/utils/geo_handler.py`

---

## 2026-05-13 (6) — TE vertical: rama YZ con bz\<0

**Síntoma:** Rama en plano YZ hacia “abajo”: la boca no encajaba con el tramo; **arriba** izq/dcha bien con solo yaw.

**Causa:** `atan2(by,bx)` ignora **bz** si **bx≈0**. Un **Rx(atan2(bz,by))** no era equivalente a emparejar con el caso simétrico “arriba”.

**Solución:** Mismo yaw que siempre +, si `mz<0`, `Ry+Rz`; si `abs(bx)<0.12` y `bz<0`, **mirror** `scale(1,1,-1)`.

**Archivos:** `pyp-scripts/utils/geo_handler.py`

---

## 2026-05-13 (7) — TE en YZ inclinado: marco canónico + SPECIAL_VERTICAL

**Síntoma:** Polilínea en YZ inclinada: TE desencajada de tubos; `plane=YZ` en lugar de la ruta vertical afinada.

**Causa:** `build_te_params` solo forzaba `VERTICAL` si el troncal era casi paralelo a **Z** mundo.

**Solución:** Atajo ampliado a troncal en plano YZ empinado (`|mz|≥0.5`); marco canónico + **`mat = mat * R(ref→main)`** (Allplan: `punto * M`, ver (8)).

**Archivos:** `pyp-scripts/utils/te_orientation.py`, `pyp-scripts/utils/geo_handler.py`

---

## 2026-05-13 (8) — Orden `mat * R` para TE YZ inclinada (convención Allplan)

**Síntoma:** Seguía falsa torsión (“dos planos”) con YZ inclinado.

**Causa:** Se usaba `R * mat_canon` como en notación columna; Allplan aplica **`geometry * Matrix`**.

**Solución:** **`mat = mat * mat_back`** tras la cadena canónica.

**Archivos:** `pyp-scripts/utils/geo_handler.py`

---

## 2026-05-13 (2) — Bifurcación TE en XZ / YZ: +90° en eje X

**Síntoma:** Orientación incorrecta de las bifurcaciones con troncal en planos XZ o YZ.

**Causa:** Falta del mismo tipo de compensación por vista (`extra_roll_by_view`) que ya tienen los tubos respecto al modelo en XY.

**Solución:** En `_aplicar_transformacion`, para TE con `plane` XZ o YZ, aplicar rotación adicional +90° en X tras preparar el plano.

**Archivos:** `pyp-scripts/utils/geo_handler.py`

---

## 2026-05-13 (3) — TE vertical (bajante −Z): Ry(180°) en SPECIAL_VERTICAL

**Síntoma:** Con `plane=VERTICAL` y troncal hacia −Z, la rama de la TE queda mirando al lado opuesto del tramo (el +90° en X solo afecta a `plane` XZ/YZ, no a este atajo).

**Causa:** El desfase −90° sobre `atan2(by,bx)` no compensa bien la bajante (`mz < 0`) solo con yaw en Z.

**Solución:** En `SPECIAL_VERTICAL`, si `mz < 0`, tras el yaw aplicar **Ry(180°)** y **Rz(180°)** (ejes **Y** y **Z** mundo).

**Archivos:** `pyp-scripts/utils/geo_handler.py`
