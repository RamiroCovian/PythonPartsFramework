# Registro de implementación — Clima

## 2026-05-04 — Reducciones: tramo recto no acortaba desde los extremos

- **Síntoma:** Al pasar el tramo recto inicial/final (p. ej. 300 → 200 o 100 mm) en la paleta, la geometría no se acortaba de forma coherente **desde los extremos**; la transición (cono) absorbía parte del cambio.
- **Causa:** Se calculaba `slope_proj = length_total - 2 * straight_len`, de modo que al disminuir `straight_len` crecía la proyección entre rodillas y el cono se alargaba en lugar de mantenerse fijo respecto al nominal de catálogo.
- **Solución:** Fijar la longitud del cono con el nominal `L_cone = max(0, length_total - 2*s_ref)` (`s_ref` = tramo recto de referencia del catálogo por tipo). Posicionar extremos con `y_lo = y_knee_l - straight_len`, `y_hi = y_knee_r + straight_len`. El largo total efectivo pasa a ser `L_cone + 2*straight_len`.
- **Archivos:** `Clima/pyp-scripts/reduccions.py`, este registro.
