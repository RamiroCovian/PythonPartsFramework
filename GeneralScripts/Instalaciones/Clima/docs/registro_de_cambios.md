# Registro de cambios — Clima

## 2026-05-05 — Error al restaurar SavedState (`int('150x150')`)

- **Síntoma:** Log `Error deserializando estado: invalid literal for int() with base 10: '150x150'` al iniciar/edición desde PythonPartGroup; `diameter_type` en JSON es texto (`150x150`, `reductor`, …).
- **Causa:** `_deserialize_state_from_json` en PolyLib aplicaba siempre `int(state["diameter_type"])`, válido en instalaciones con diámetro numérico pero no en perfil Clima (combo string).
- **Solución:** Coerción al restaurar: entero/`float` entero como antes; cadenas con `x` o letras se dejan como `str`; cadenas puramente numéricas siguen pasando por `int(float(...))`.

**Archivos:** `PolyLib/interactor.py`, este documento.  
**Documentación ampliada:** `Clima/docs/fix_savedstate_diameter_type_deserializacion.md`

## 2026-04-30 — Reductor en Retorn no se generaba

- **Síntoma:** En polilínea Retorn, el tramo intermedio quedaba con `diameter='reductor'` y se instanciaba `tram_recte` en lugar del PythonPart `reduccions`.
- **Causa:** `_reduccion_factory` en `clima_polyline.py` devolvía `None` para cualquier instalación distinta de Impulsió, así que el `PipelineProcessor` no creaba la geometría de reductor.
- **Solución:** Permitir también la etiqueta `Retorn`; `ReduccionsScript` ya mapea `installation_type` que empieza por `ret` a `redretorn`.

**Archivos:** `Clima/pyp-scripts/clima_polyline.py`

## 2026-04-30 — Retorn 750×150 → Impulsió pasaba a 150×150

- **Síntoma:** Con Retorn y diámetro 750×150, al cambiar solo el combo de instalación a Impulsió (dejando el de sección en 750×150), la previsualización y la geometría usaban 150×150.
- **Causa:** `resolve_installation_config` (PolyLib) asigna `diameter_type` al primer valor de la lista al cambiar el tipo; en Clima `connections` no incluye REDUCION, así que `get_segments` no usa el diámetro por segmento y depende solo de `diameter_type`. El parámetro de paleta `DiameterTypeStr` podía seguir en 750×150.
- **Solución:** Tras `InstallationType`, hook `modify_element_property` en `clima_polyline` reaplica un diámetro válido: prioriza el valor de `DiameterTypeStr` si está en la nueva lista, si no el diámetro previo, y regenera la vista.

**Archivos:** `Clima/pyp-scripts/clima_polyline.py`

## 2026-04-30 — Retorn: reductor más largo que el tramo (p. ej. 1,375 m con tramo 1,175 m)

- **Síntoma:** 150×150 – reductor – 750×150 en Retorn medía ~1,375 m cuando el segmento polilínea era 1,175 m (Impulsió ya se había corregido en el eje/proyección).
- **Causa:** En `_BaseReduccionModel`, `slope_proj` usaba `length_total - 2*s_ref` (rodilla catálogo 200 mm Retorn / 300 mm Impl) pero el tramo recto real viene del combo `straight_len` (suele 300 mm). El largo físico es `2*straight_len + slope_proj`, así que si `straight_len > s_ref` la pieza crecía en `2*(straight_len - s_ref)` (200 mm en el caso típico).
- **Solución:** Calcular `slope_proj = max(0, length_total - 2*straight_len)` para que el desarrollo coincida con `length_total` del tramo.

**Archivos:** `Clima/pyp-scripts/reduccions.py`, `Clima/pyp-library/reduccions.py`
