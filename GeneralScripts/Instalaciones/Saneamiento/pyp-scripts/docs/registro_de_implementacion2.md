# Registro de implementación 2 (Saneamiento PolyLib)

Bitácora activa desde este punto de la conversación.  
**A partir de ahora**, los cambios nuevos se documentan aquí.

---

## 2026-05-15 — Fecal Ø40: flecha mal orientada en trazados YZ

- **Síntoma:** En vista/plano YZ la flecha del ``tub_pvc_tricapa_f_40`` no coincidía con el sentido del fluido (pluvial Ø110 bien).
- **Causa:** El tubo se dejaba alargado en **+Z** y solo la flecha recibía ``Ry(-90)``, distinto del marco de ``TuboPVCConFlecha`` (+X tras ``Ry(90)`` + ``Rx(180)``) y de la cadena pluvial ``flip`` + ``Rz(180)``.
- **Solución:** Terminar ``_build_tube`` como v_script (``Ry(90)`` + ``Rx(180)``); misma cadena de flecha que p_110/f_110 (sin ``Ry`` extra); ``MODEL_ROT_Z_DEG = 180`` como pluvial.
- **Archivos:** `pyp-scripts/tub_pvc_tricapa_f_40_script.py`, este registro.

---

## 2026-05-15 — Debug: capas/atributos apagados por defecto; trazas ``seg.info`` / ``seg.data``

- **Cambio:** ``SANEAMIENTO_LAYER_DEBUG`` y ``SANEAMIENTO_ATTR_DEBUG`` pasan a **0** por defecto (`layers_utils.py`, `attributes_utils.py`). Siguen activables con ``=1`` o con ``SANEAMIENTO_DEBUG_HOOKS=1`` (capas/atributos vía ``_saneamiento_*_trace``).
- **Nuevo:** ``SANEAMIENTO_DEBUG_SEGMENT_INFO`` y ``SANEAMIENTO_DEBUG_SEGMENT_DATA`` (por defecto **1**): líneas ``[SANEAMIENTO][SEGINFO]`` / ``[SEGDATA]`` en ``_create_elements_for_segment_group`` (`saneamiento_polyline.py`). Desactivar con ``=0``. El volcado crudo ``SANEAMIENTO_DEBUG_SEGMENTS_DUMP`` sigue aparte (por defecto 0).
- **Archivos:** `pyp-scripts/utils/layers_utils.py`, `pyp-scripts/utils/attributes_utils.py`, `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Capa de tubo aplicada a codos si había atributos en la misma clave

- **Síntoma:** Tras aplicar sólo capa al 2.º tubo (`applied_layers` en clave PolyLib, p. ej. `seg_0_elem_2`), los codos del 1.er 2×45 (`pipe_idx` 2–3) tomaban esa capa **OBR** aunque la entrada paleta fuese `type=tubo`.
- **Causa:** ``_resolve_assignment_key`` devolvía la primera clave presente en ``applied_attributes`` **antes** de validar ``applied_layers`` y ``reject_applied_layer_types``. Si el usuario había aplicado atributos en `seg_0_elem_2`, los codos recibían ``layer_key``=esa cadena y forcían la capa del tubo.
- **Solución:** Resolver ``layer_key`` sólo desde ``applied_layers`` (sin atajo por ``applied_attributes``); eliminar variable muerta.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Atributos de paleta: 2×45° un vértice heredaba el de otro

- **Síntoma:** Al aplicar atributos sólo al 2.º grupo de codos (2×45° del 2.º vértice), también se actualizaba el 1.er grupo.
- **Causa:** Para codos se hacía fallback a ``layer_key`` (pensada para capas en el mismo paquete) y/o la cadena ``seg_0_elem_3`` coincide entre el **2.º BRep** del 1.er 2×45 (``pipe_idx`` 3) y la clave PolyLib del vértice siguiente.
- **Solución:** En ``_saneamiento_resolve_applied_attributes_list``, si el elemento es codo, buscar atributos **sólo** en ``poly_key`` del preview (``seg_idx`` = vértice del path), sin ``layer_key`` ni ``seg_*_elem_{pipe_idx}``.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Atributos de paleta no llegaban al tubo (clave PolyLib vs `pipe_idx`)

- **Síntoma:** Tras «Aplicar atributo» en un tubo, el valor no se veía en el tramo esperado; en consola `applied_attributes` tenía p. ej. `seg_0_elem_2` mientras el tubo del 2.º tramo usa `seg_0_elem_4` en el pipeline.
- **Causa:** `apply_attributes_input` en PolyLib guarda con `seg_{path}_elem_{layer_idx}` donde `layer_idx` es `key[3]` (`final_idx`) del preview en `generated_elements`, no el índice secuencial `pipe_idx` del hook Saneamiento.
- **Solución:** `_saneamiento_polylib_preview_storage_key` localiza el preview `tubo`/`codo` por `seg_idx` y obtiene `key[3]`; `_saneamiento_resolve_applied_attributes_list` prueba primero esa clave y luego `layer_key`.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Debug de aplicación de atributos (botón «Aplicar atributo», hook sin tocar PolyLib)

- **Necesidad:** Trazabilidad al guardar `applied_attributes` y al fusionar/aplicar sobre cada BRep en `_create_elements_with_layers_attrs`, sin modificar `PolyLib`.
- **Solución:** `attribute_debug_enabled()` / `format_attributes_for_debug()` en `utils/attributes_utils.py` (`SANEAMIENTO_ATTR_DEBUG=1` para activar; por defecto **off** desde 2026-05-15). En `saneamiento_polyline.py`, `_saneamiento_attr_trace()` alinea con `SANEAMIENTO_DEBUG_HOOKS`; interceptar `EventIds.ATTRIBUTE_APPLY` en el `on_control_event` envuelto de `create_script_object` y volcar estado post-handler (`_saneamiento_trace_attribute_apply_after_button`); líneas `[SANEAMIENTO][ATTRDBG]` en el hook por elemento (palette vs modelo, merge).
- **Archivos:** `pyp-scripts/utils/attributes_utils.py`, `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Capa de paleta sólo en el cuerpo principal (no en copias BRep ni `_inner`)

- **Síntoma:** Al cambiar capa desde la paleta sobre un tubo (u otro accesorio) cuyo script devuelve varios BRep (`tubo_saneamiento_copy_dyn_*`, `*_inner`, etc.), el hook aplicaba la misma capa a todos los sólidos del mismo PythonPart; se quería conservar capa/color del script en copias y piezas interiores.
- **Solución:** Tras resolver `layer_key`, si `element_type` es secundario (`_inner` en el nombre o subcadena `_copy_`), sustituir por clave sintética fuera de `applied_layers` (`__saneamiento_palette_original_only__`), de modo que `_apply_layer_to_element` no cambia la capa y tampoco se fusionan atributos de paleta en esa pieza.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py` (`_is_saneamiento_palette_secondary_geometry`, `_saneamiento_skip_palette_secondary_geometry_key`, integración en `_create_elements_with_layers_attrs`), este registro.

---

## 2026-05-15 — Capa de tubo mal aplicada: 2.º tubo afectaba codos y 3.er tramo

- **Síntoma:** Al asignar capa «obra» al **2.º tubo**, PolyLib guardaba p. ej. `seg_0_elem_2` (`layer_idx` = índice de pipeline del vértice). El hook intentaba también `seg_{path}_elem_{ordinal}` como candidato; el 3.er tubo generaba `seg_0_elem_2` por ordinal == 2 y reutilizaba la capa del 2.º. Los codos con `pipe_idx==2` coincidían con la misma clave y cogían la capa del tubo.
- **Solución:** Resolver capa de `tubo_saneamiento` con `_saneamiento_find_applied_layer_key_for_tube` (`type=tubo`, `elem_idx` = ordinal de tramo). Quitar candidato ordinal `seg_*_elem_{tube_segment_idx}`. En codos y demás accesorios, `_resolve_assignment_key(..., reject_applied_layer_types=tubo)` para no usar entradas de paleta guardadas como tubo. Flechas/anexos: solo `last_tube_layer_key` + `storage_key` (sin fallback ordinal).
- **2026-05-15 (seguimiento):** El fallback de tubo seguía usando vecinos `±1/±2` sobre `storage_key`; el 1.er tubo (`seg_0_elem_0`) encontraba en paleta `seg_0_elem_0+2=seg_0_elem_2` y robaba la capa del 2.º tramo. Además, tras `reject` de tipo `tubo`, `default_key` seguía siendo `seg_0_elem_2` y `_apply_layer_to_element` aplicaba igual la capa al codo. **Corrección:** fallback de tubo sin vecinos; si `default_key` sólo tiene entrada `tubo` y el caller rechaza tubo, devolver clave sintética `__saneamiento_skip_tubo_palette__` (no está en `applied_layers` → se conserva capa del script).
- **2026-05-15 (fecal 110, 3.º tubo):** PolyLib puede guardar la capa del 3.er tubo en `seg_0_elem_4` (`layer_idx` del click) mientras el **2.º** tubo en el pipeline también tiene `storage_key=seg_0_elem_4` (`pipe_idx=4`). El fallback aceptaba la entrada sin comprobar `elem_idx` del payload vs `tube_segment_idx`. **Corrección:** si `applied_layers[storage_key]` es `type=tubo` y `elem_idx != tube_segment_idx`, usar clave sintética `__saneamiento_tubo_elem_mismatch_*__`.
- **2026-05-15 (multicel., codos Pluvial):** Con selección por marco, PolyLib guarda codos en `seg_*_elem_{1,3,5,7}` según `layer_idx`, pero el segundo `codo_45` de cada 2×45° tiene `pipe_idx` 10, 11, etc. sin entrada propia; el vecino ±2 no alcanzaba la clave correcta y tras `reject` tubo quedaba capa FAB. **Corrección:** `_saneamiento_find_applied_layer_key_for_codo` + contador 1-based alineado con `elem_idx` del `AppliedLayer` (`type=codo`).
- **2026-05-15 (un solo codo, vecinos):** Con sólo `seg_0_elem_7` (`elem_idx=4`) en paleta, el vértice 2 (`pipe_idx` 6) incluía `seg_0_elem_7` como vecino (+1) y aplicaba capa ajena. **Corrección:** `require_applied_codo_elem_idx` en `_resolve_assignment_key` para exigir coincidencia en filas `type=codo`.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Debug de aplicación de capas (palette → modelo)

- **Síntoma / necesidad:** Poco rastro al resolver `layer_key`, entrada en `applied_layers` y capa del modelo antes/después del hook.
- **Solución:** `layer_debug_enabled()` en `utils/layers_utils.py`; logs al omitir capa (sin clave en `applied_layers`); hook `_create_elements_with_layers_attrs` imprime resumen y una línea por elemento con `_saneamiento_layer_trace()` (`SANEAMIENTO_LAYER_DEBUG=1` **o** `SANEAMIENTO_DEBUG_HOOKS`). **2026-05-15 (ter):** por defecto **desactivado** (`SANEAMIENTO_LAYER_DEBUG=0`).
- **Archivos:** `pyp-scripts/utils/layers_utils.py`, `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-15 — Limitador de ángulos: evitar giros relativos 135°/180° (vértices «45° cerrados»)

- **Síntoma:** Con «limitar ángulos» activo, el snap seguía permitiendo trazados con giros relativos de 135° (p. ej. combinaciones del registry `ANGLES_45`), generando esquinas agudas no contempladas por codos/tubería.
- **Causa:** `resolve_installation_config` copiaba `model_base["angles"]` (octante completo) en `angle_steps`; PolyLib interpreta esos valores como **deltas** respecto al tramo anterior, no solo como rumbos absolutos.
- **Solución:** Tras cada `resolve_installation_config`, fijar `angle_steps` a `CONFIG.allowed_angles` (`0/±45/±90`) si `limit_angles` es verdadero, sin cambiar `allowed_angles` ni el registry.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py` (`_apply_saneamiento_angle_steps_for_snap`, envoltorio existente), este registro.

---

## 2026-04-07 — Cambio de bitácora activa

- Por solicitud del usuario, el registro operativo pasa de `registro_de_implementacion.md` a `registro_de_implementacion2.md`.
- Los cambios futuros de Saneamiento se documentarán en este archivo.

---

## 2026-05-14 — «Invertir cabal» no afectaba la rama TE (troncal sí)

- **Síntoma:** Con TE simétrica y `branch_along_main > 0`, el pipeline sólo voltea la rama (`paths_to_flip`). La supresión tras «Invertir cabal» se **perdía** si la firma de puntos comparaba mal (redondeo/precisión): volvía la auto-inversión **sólo en la rama** y anulaba el botón ahí, no en el troncal.
- **Solución:** Firma **por path** (estructura conservada) y comparación con **tolerancia en mm** (`_paths_te_flip_signatures_equivalent`, atol 2 mm) en lugar de igualdad exacta de tuplas redondeadas.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-14 — TE simétrica ``along > 0``: restaurar auto-inversión + supresión tras «Invertir cabal»

- **Síntoma:** Omitir siempre la auto-inversión en TE troncal simétrico con la bandera activa dejó sin alinear la rama cuando **no** era cabal sin sentido (`branch_along_main > 0`): mirrors en X/Y quedaban en false y faltaba `_FlippedSeg`.
- **Solución:** Volver a aplicar auto-inversión salvo en (1) TE simétrica con `along < 0`, (2) TE simétrica con `along > 0` mientras la firma de `saved_paths` / `saved_optimized_paths` coincida con la guardada al pulsar «Invertir cabal» (`so._saneamiento_te_flip_suppress_signature`). Si el usuario edita puntos, la firma cambia y vuelve la auto-inversión.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py` (`_paths_signature_te_flip`, `_te_flip_suppress_after_invert_active`, `_compute_branch_invert_paths`, `_invertir_caval_saneamiento`), `pyp-scripts/utils/te_orientation.py` (comentario), este registro.

---

## 2026-05-14 — «Invertir cabal» sin efecto con TE troncal simétrica + `SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE`

- **Síntoma:** El botón invertía `saved_paths`, pero el preview seguía igual: `_compute_branch_invert_paths` aplicaba `_FlippedSeg` otra vez tras el clic porque `branch_along_main` pasaba de negativo a positivo y el `continue` sólo cubría `along < 0`.
- **Solución:** Con la bandera activa, omitir auto-inversión de paths en **todo** nodo TE de troncal simétrico (`di_main_in == di_main_out`), sin filtrar por signo de `along`.
- **Archivos:** `pyp-scripts/saneamiento_polyline.py`, `pyp-scripts/utils/te_orientation.py` (comentario), este registro.

---

## 2026-05-14 — Corrección: mirror Y TE siempre en «caval sin sentido»; toggle sólo afecta paths

- **Síntoma:** Con `SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE=True`, la TE quedaba desalineada (rama hacia arriba-derecha, modelo hacia abajo-derecha): se había desactivado `need_mirror_y_local` junto con la inversión de polilíneas.
- **Causa:** El mirror Y en `te_orientation` es orientación del **modelo** respecto a la geometría dibujada; la auto-inversión en `saneamiento_polyline` es otra capa (sentido de paths). Anular el mirror rompía el encaje sin sustituirlo por otra corrección.
- **Solución:** Volver a aplicar siempre `need_mirror_y_local = (branch_along_main < 0)` en el bloque TE simétrica. El flag `SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE` queda para omitir `paths_to_flip` en `_compute_branch_invert_paths` en TE troncal simétrica (véase condición vigente en código). Comentarios del constante actualizados.
- **Archivos:** `pyp-scripts/utils/te_orientation.py`, este registro.

---

## 2026-05-14 — Toggle «caval sin sentido»: sólo advertencia TE (sin mirror Y ni auto-inversión de paths)

- **Síntoma / objetivo:** En bifurcaciones TE donde aparece el cartel «caval sin sentido sera creado», el usuario quería poder **desactivar** la corrección automática (mirror Y local en orientación TE **y** auto-inversión de rama/troncal en el pipeline), dejando **sólo el aviso**.
- **Solución (evolución 2026-05-14):** Constante global `SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE` en `utils/te_orientation.py`. Tras la corrección posterior, el flag **ya no** desactiva el mirror Y; controla si `saneamiento_polyline._compute_branch_invert_paths` omite inversiones de paths en nodos TE con **troncal simétrico** (actualizado otra vez para cubrir cualquier signo de `branch_along_main`, ver entrada «Invertir cabal sin efecto»). El cartel y el mirror Y se mantienen para alinear la pieza.
- **Archivos:** `pyp-scripts/utils/te_orientation.py`, `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-14 — Default `SANEAMIENTO_CAVAL_SIN_SENTIDO_SOLO_AVISO_TE = True`

- **Cambio:** Por decisión del usuario, el valor por defecto de la bandera pasa a **`True`** (sin auto-inversión de polilíneas en el caso TE citado; mirror y aviso se conservan).
- **Archivos:** `pyp-scripts/utils/te_orientation.py`, `pyp-scripts/saneamiento_polyline.py`, este registro.

---

## 2026-05-13 — TE «invertir cabal»: troncal en plano XY cuando la rama conecta en *start* y `branch_along_main > 0`

- **Síntoma:** Tras «Invertir cabal» en una bifurcación tipo TE, el **path troncal** (p. ej. path 0) **no** invertía el sentido de caudal cuando los logs mostraban rama en `is_start` y `branch_along_main` **positivo** (`along ≈ +0.707`). Solo la rama reaccionaba; el caudal quedaba incoherente frente al caso espejo.
- **Causa:** En `_compute_branch_invert_paths`, el bloque `if is_branch_start` sólo añadía `_add_mains_flip()` cuando `branch_along_main < 0`. El caso `is_branch_start` + `along > 0` (equivalente simétrico tras invertir polilíneas) **omitía** el par colineal del troncal.
- **Solución:** Para `is_branch_start`, invertir troncales cuando `abs(branch_along_main) > eps` (misma heurística «axial clara» que en rama-en-*end*), conservando el caso `|along| ≈ 0` (sólo rama, sin tocar troncal).
- **Archivos:** `pyp-scripts/saneamiento_polyline.py` (`_compute_branch_invert_paths`, docstring y cabecera de sección), este registro.

