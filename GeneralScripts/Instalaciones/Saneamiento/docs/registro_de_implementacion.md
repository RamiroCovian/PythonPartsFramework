# Registro de implementación — Saneamiento

## 2026-05-04 — Numeración absoluta (ATTR01) no aplicada en polilínea

- **Síntoma:** Los tubos generados por la polilínea de Saneamiento no recibían la numeración absoluta en el atributo personalizado 01 (formato `TAF-{Ø}. {n}`), a diferencia del módulo Agua.
- **Causa:** `_apply_absolute_numbering_attr01` existía en `pyp-scripts/utils/attributes_utils.py` pero no se invocaba desde `saneamiento_polyline.py`; solo estaba cableada en `Agua/pyp-scripts/agua_polyline.py`.
- **Solución:** En `_create_elements_with_layers_attrs`, tras aplicar capas y atributos de paleta, se llama a `_apply_absolute_numbering_attr01` para cada elemento `tubo_saneamiento` (diámetro desde `seg_info` o `so.diameter_type`; distribución desde segmento o `so.distribution_type`). Al final del bucle se llama a `init_storage._save_numbering_file()` para persistir contadores (paridad con Agua).
- **Archivos:** `Saneamiento/pyp-scripts/saneamiento_polyline.py`, este registro.
