# Registro de implementación — Saneamiento (PolyLib / pyp-scripts)

Bitácora de cambios funcionales en scripts de saneamiento.

---

## 2026-05-13 — Bifurcación TE: hueco entre Y y tubos según orden de dibujo

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con la misma geometría final, si primero se dibujan los dos tramos del troncal y luego la rama, la TE encaja bien; si se dibuja troncal parcial → rama → segundo tramo del troncal, puede aparecer un hueco entre la bifurcación y los tubos (recortes desacoplados de la orientación TE). |
| **Causa** | En `register_te_cuts_into` el par “troncal” se elegía con **max(\|dot\|)** entre direcciones en el nodo. Cuando los dos tramos del path principal no son claramente opuestos a 180° frente a la rama (p. ej. geometría casi alineada con la rama por orden de captura), un par **rama + tramo** puede tener \|dot\|=1 y ganar frente al par troncal real (~135°, \|dot\|≈0.707). Eso asignaba `trim_main_in` / `trim_main_out` al segmento equivocado. Además, con Ø iguales, `conn_in`/`conn_out` dependían del orden de índices en el `vertex_map`, no de la geometría como en `build_te_params`. |
| **Solución** | Alinear con `te_orientation.build_te_params`: par troncal = **mínimo** producto escalar entre pares (umbral `< -0.5`). Con troncal simétrico, fijar `conn_in`/`conn_out` con `base_main` y `dot` como en orientación; mantener el intercambio de trims según `branch_along_main`. |
| **Archivos** | `utils/vertex_utils.py` (`register_te_cuts_into`). |

---

## 2026-05-13 (2) — Recortes TE con hints desde build_te_params

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con path 0 de **3 tramos** y bifurcación, seguía apreciándose desajuste pese al cambio anterior; en log, `main_dir_3d` de la TE es vertical pero el tramo asociado al insertar la pieza sigue mostrando `v_unit` diagonal y recortes incoherentes entre tramos. |
| **Causa** | Posibles empates o desfases entre `_seg_dir_from_conn` (recortes) y `_norm_vec_3d_from_conn` + orden fijo de tuplas en `build_te_params`; lo robusto es no rederivar el par troncal/rama para cortes. |
| **Solución** | `build_te_params` expone `_te_cut_main_indices` y `_te_cut_branch_idx` por nodo. `compute_segment_cuts_for_all_paths(..., te_nodes=...)` los pasa a `register_te_cuts_into` para aplicar trims exactamente a las mismas conexiones que la orientación TE. Sin hints válidos se mantiene el fallback geométrico. |
| **Archivos** | `utils/te_orientation.py`, `utils/vertex_utils.py`, `saneamiento_polyline.py`. |

---

## 2026-05-13 (3) — Swap TE trim_main_in/out con troncal en L y rama ~45°

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Hueco bajo la Y con path 0 de 3 tramos (aproximación diagonal al nodo + salida vertical); logs muestran `main_dir_3d` vertical y rama diagonal pero recortes absurdos en el tubo vertical. |
| **Causa** | Tras fijar troncal/rama con hints, el bloque simétrico seguía usando `base_main = v_main_a` (primer tramo del par). Si ese vector es casi paralelo a la **rama**, `branch_along_main > 0` activa el intercambio `trim_main_in ↔ trim_main_out` pensado para el troncal colineal. En geometría en L, eso asigna el recorte **grande** (`main_out` en pluvial ~132 mm) al tubo **vertical** y el pequeño al diagonal → hueco. |
| **Solución** | Con `te_node_params` que incluye `main_dir_3d`, asignar `conn_in`/`conn_out` por alineación con ese eje y calcular `branch_along_main` como `v_branch · main_dir_3d` (igual que en depuración TE), no respecto a `base_main` del primer tramo. Sin `main_dir_3d`, se mantiene la lógica anterior. |
| **Archivos** | `utils/vertex_utils.py` (`register_te_cuts_into`). Corrección posterior: paréntesis de más en `_norm3` (`float(t[2]))` → `float(t[2])`) que impedía importar el módulo. |

---

## 2026-05-13 (4) — Bifurcación TE en planos XZ / YZ: roll +90° en X

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Las TE (bifurcaciones) quedaban mal orientadas cuando el troncal está en vista/plano **XZ** o **YZ** (sección transversal desfasada respecto a los tubos). |
| **Causa** | Los conductos reciben `extra_roll_by_view` (+90° alrededor del eje de viaje) para compensar que el BREP está modelado en **XY**. La colocación TE en `_aplicar_transformacion` aplicaba la preparación plano XY→XZ/YZ y el giro del troncal, pero **no** el roll equivalente en X que alinea la cruz con el resto del saneamiento. |
| **Solución** | Tras la cadena de preparación + `ang` (+ rama elevada si aplica), aplicar una rotación **adicional de +90° alrededor del eje X** (primero en el orden de aplicación al sólido: `mat = R_x(90°) * mat`) en los ramos `plane == "XZ"` y `plane == "YZ"`. |
| **Archivos** | `utils/geo_handler.py` (bloque TE, PARTE 2). |

---

## 2026-05-13 (5) — TE troncal vertical (plane=VERTICAL): rama mirando al lado contrario

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con troncal casi en **−Z** (bajante) y rama en el plano **YZ** (`branch_dir` con `bx≈0`), la Y queda girada ~180° respecto al tubo de la rama; el fix +90° en X de XZ/YZ **no** se aplica porque ese nodo usa `plane=VERTICAL` y sale por `SPECIAL_VERTICAL` antes de esas ramas. |
| **Causa** | El yaw `theta = atan2(by,bx) − π/2` tras `Ry(±90°)` encaja con la convención del modelo para troncal **+Z**; para **−Z** (`mz < 0`) la boca de rama queda respecto al tramo como si el giro correctivo fuera en **Y**, no como un extra de yaw en **Z**. |
| **Solución** | En `SPECIAL_VERTICAL`, si `mz < 0`, tras el yaw `Rz(theta)` componer **`mat = mat * R_z(π) * R_y(π)`** (sobre el sólido: primero **Ry**, luego **Rz**). Log opcional `[DBG TE] SPECIAL_VERTICAL mz<0 → Ry(180°) + Rz(180°)`. |
| **Archivos** | `utils/geo_handler.py` (`SPECIAL_VERTICAL`). |

---

## 2026-05-13 (6) — TE vertical: rama YZ con bz\<0 (mirror en Z)

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con bajante y rama en vista YZ “hacia abajo”, la boca de la Y apuntaba “arriba”; las ramas “hacia arriba” cuadran bien solo con rotaciones. |
| **Causa** | Con **bx≈0**, `atan2(by,bx)` no usa **bz**. Un pitch extra en **X** no replica el criterio visual de arriba/abajo. |
| **Solución** | Mantener el mismo yaw `atan2(by,bx)−π/2` y `Ry+Rz` si `mz<0`; si `abs(bx)<0.12` y `bz<0`, aplicar **espejo** `scale(1,1,-1)` (mirror Z). |
| **Archivos** | `utils/geo_handler.py` (`SPECIAL_VERTICAL`). |

---

## 2026-05-13 (7) — TE troncal en YZ inclinado: mismo pipeline que eje Z

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con polilínea en **YZ inclinada** (troncal no paralelo a Z mundo), la TE usaba `plane=YZ` y `PATH=YZ` en lugar de `SPECIAL_VERTICAL`; las rotaciones no acompañaban a los tubos (huecos / piezas sueltas). |
| **Causa** | El atajo `VERTICAL` en `build_te_params` solo aceptaba troncal **casi** eje Z (`my≈0`); un troncal en el plano YZ con componente en **Y** caía en la lógica 2D `ang` + roll distinta. |
| **Solución** | Ampliar el atajo a **plano YZ empinado** (`mx≈0`, `hypot(my,mz)≥0.99`, `|mz|≥0.5`). En `SPECIAL_VERTICAL`, si el troncal no es eje Z: llevar `main` y `branch` a un marco canónico `(0,0,±1)`, aplicar la cadena existente, luego componer con **`mat = mat * R(ref→main)`** (convención Allplan: `punto * M` → el factor **izquierdo** de los dos se aplica primero; `p * mat_canon * R` requiere post-multiplicar `R`, no `R * mat_canon`). Helpers `_te_mat_rotate_unit_to_unit`, `_te_rotate_vec_u_to_v`. |
| **Archivos** | `utils/te_orientation.py`, `utils/geo_handler.py`. |

---

## 2026-05-13 (8) — TE YZ inclinado: orden de matriz Allplan (`mat * R_mundo`)

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Tras el marco canónico, la TE en YZ inclinada seguía girando mal (“dos planos”). |
| **Causa** | Se componía `mat = R(ref→main) * mat_canon` como si fuera columna; en Allplan el habitual es **`geometry * Matrix`** (`p * M`): el primer factor aplicado a `p` es el de la **izquierda** en `p * mat_canon * R`. |
| **Solución** | Tras la cadena canónica: **`mat = mat * mat_back`** (equivalente a `p * mat_canon * R`). |
| **Archivos** | `utils/geo_handler.py` (`SPECIAL_VERTICAL`). |

---

## 2026-05-13 (9) — Flecha de flujo: pegada a la cara exterior del tubo

| Campo | Detalle |
|--------|---------|
| **Síntoma** | La flecha de sentido quedaba dentro o centrada en el volumen del tubo; se deseaba verla fuera, como pegatina sobre la superficie, sin desplazar el anclaje lógico a lo largo del eje del tramo. |
| **Causa** | Los modelos de flecha se colocan en el centro del tramo (`p_centro`) con el mismo transform que el tubo; la geometría local de la flecha sitúa el símbolo hacia el interior del prisma. Además `segment_data` en `process` es solo `.data` (sin `.info`), así que el offset radial no podía leer el Ø real del segmento. |
| **Solución** | Tras yaw/pitch y el posible flip 180° por cara visible, **`Move`** del BRep según la normal del plano de la flecha (rotada igual que la geo si hay flip) una distancia **`SANEAMIENTO_FLECHA_RADIAL_SCALE * (Ø/2 + SANEAMIENTO_FLECHA_SURFACE_SKIN_MM)`**; desactivación opcional con `SANEAMIENTO_FLECHA_RADIAL_DISABLE=1`. El caller pasa **`flecha_diameter_mm=seg_diameter`** desde el `SegmentItem`. |
| **Archivos** | `utils/geo_handler.py` (`_aplicar_transformacion`, `process`). |

---

## 2026-05-13 (10) — Flecha en YZ/XZ inclinado: misma cadena que el tubo + alineación al eje

| Campo | Detalle |
|--------|---------|
| **Síntoma** | En tramos YZ (u otros no XY) inclinados, la flecha seguía viéndose “dentro” del tubo: el desplazamiento radial usaba una normal solo yaw/pitch, distinta de la orientación real del prisma (faltaba `Z→X`, roll, o el deslizamiento axial del tubo). |
| **Causa** | (1) La normal para el offset **no** reproducía la cadena **Ry(90)+flip** cuando el BRep pasa por `san_z_to_x_applied`; (2) **no** se aplicaba **`Rx(roll)`** en `_aplicar_transformacion` pese al criterio documentado (`angulo_rotacion` + 90° en vista XZ/YZ). |
| **Solución** | Helpers **`_san_flecha_sticker_normal_world`** + rotadores; normal = imagen de local **+Z** con la misma secuencia que el BRep hasta yaw. **`rotation_angle=_san_roll`** con **`_saneamiento_effective_roll_deg`** (extra 90° salvo `SANEAMIENTO_DISABLE_VIEW_ROLL_EXTRA=1`) en tubo/flecha/copias/inner. La flecha **no** debe usar el alineado axial del tubo al polilínea: véase **(11)**. |
| **Archivos** | `utils/geo_handler.py`. |

---

## 2026-05-13 (11) — Flecha: no alinear axial como el tubo (evita solapar el anillo)

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Tras alinear la flecha con `_align_saneamiento_tube_along_segment` (igual que el tubo), la flecha quedaba sobre el **anillo** del tubo en vez de en la zona del fuste, cerca del anillo. |
| **Causa** | Ese helper corrige el prism al **inicio** del tramo en la polilínea; con la geometría corta de la flecha, el desplazamiento axial la empuja hacia el extremo donde está el manguito/anillo. |
| **Solución** | Dejar la flecha solo con `_aplicar_transformacion` (centro de tramo `p_centro` + offset radial en `geo_handler`). No aplicar `_align_saneamiento_tube_along_segment` a la flecha. |
| **Archivos** | `utils/geo_handler.py` (`process`). |

---

## 2026-05-13 (12) — Invertir cabal: TE eje Z no debe rotar (solo tubos/codos)

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Tras "invertir cabal", la bifurcación TE en vista/plano vertical (troncal ~ eje Z) parecía **girar**; solo deberían invertirse sentidos de tubos/codos. |
| **Causa** | `main_dir_3d` pasa de `(0,0,-1)` a `(0,0,+1)` (misma recta, sentido opuesto). En `SPECIAL_VERTICAL` eso cambiaba `r_main` (Ry ±90° según `mz`) y la rama `mz<0 → Ry+Rz`, produciendo una pose distinta para la misma geometría física. |
| **Solución** | Si **`trunk_wz`** (troncal casi paralelo a **Z** mundo), fijar **`(mx,my,mz) = (0,0,-1)`** solo para la cadena de orientación del BRep TE; conservar **`omx,omy,omz`** en `mx0,my0,mz0` cuando **`trunk_wz`** (eje Z puro; el YZ inclinado se trata en **(13)**). |
| **Archivos** | `utils/geo_handler.py` (`SPECIAL_VERTICAL`). |

---

## 2026-05-13 (13) — Invertir cabal: TE en YZ inclinado (troncal sin X)

| Campo | Detalle |
|--------|---------|
| **Síntoma** | Con troncal en **plano YZ inclinado** (`|mx|≈0`), al invertir caudal la TE cambiaba de pose: `ref_z` pasaba de −1 a +1 y variaba el bloque `mz<0 → Ry+Rz`. |
| **Causa** | `ref_z` dependía del **signo** de `mz0` del vector troncal; al invertir, el mismo tramo geométrico invierte `mz0` aunque sea la misma recta. |
| **Solución** | Si `trunk_steep_yz`, no `trunk_wz` y `\|omx\|<0.12`, unificar semieje: si **`tmz>0`**, usar **`-main`** como `mx0`/`mx` de trabajo antes del canon (igual idea que fijar −Z en eje Z puro). |
| **Archivos** | `utils/geo_handler.py` (`SPECIAL_VERTICAL`). |
