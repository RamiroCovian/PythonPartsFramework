# Paleta: tipos de instalación y diámetros (Saneamiento librería)

Cambios en el registro PolyLib de saneamiento: nombres en el combo y unificación **Fecal** con diámetros 25 / 40 / 110 mm.

## Objetivo

- **Pluvial:** etiqueta sin “(Tricapa)”; tipo de instalación `tub_pvc_tricapa_v` con diámetro **110 mm** en paleta. En polilínea Ø110 se usa el PythonPart **`tub_pvc_tricapa_p_110`**; Ø40 (si aplica) sigue en **`tub_pvc_tricapa_v`** (`TipoTubo=2`).
- **Fecal:** una sola opción en el combo (etiqueta **“Fecal”**, sin “Basic” ni “Tricapa”), tipo `tub_pvc_tricapa`, diámetros **25, 40, 110**.
- El antiguo **Fecal (Basic)** deja de aparecer como instalación independiente; el tubo **Ø25** usa el PythonPart `tub_pvc_basic_f_25` (`tub_pvc_basic_f_25_script.py` / `TubPvcBasicF25Script`).

## Archivos tocados

### `polyline_reg_saneamiento.py`

- `tub_pvc_tricapa_v`: `label` → **"Pluvial"** (antes “Pluvial (Tricapa)”).
- Eliminada la entrada `installation_types` del antiguo basic (ya no sale en el combo).
- `tub_pvc_tricapa` (clave del **tipo de instalación** en el combo Fecal): `label` → **"Fecal"**; `diameter` → **`[25, 40, 110]`**. El PythonPart Ø40 se registra aparte como `tub_pvc_tricapa_f_40` (ver `elements3D`).
- En **`elements3D`**: `create_element("tub_pvc_basic_f_25", ...)` → módulo `pyp-scripts.tub_pvc_basic_f_25_script`, clase `TubPvcBasicF25Script`, clave `get_pythonpart("tub_pvc_basic_f_25")` cuando Fecal está en **25 mm**.

### `saneamiento_polyline.py` (hook de preview / geometría)

- Solo se consideran instalaciones **`tub_pvc_tricapa`** y **`tub_pvc_tricapa_v`** (el Ø25 no es un `installation_type`, es un `element_key` aparte).
- **Fecal** (`tub_pvc_tricapa`):
  - diámetro **25** → `element_key="tub_pvc_basic_f_25"`, `exec_kwargs` con rotación `rot_x=180`.
  - diámetro **110** → `element_key="tub_pvc_tricapa_f_110"` (`tub_pvc_tricapa_f_110_script.py` / `TubPvcTricapaF110Script`; color tubo **4** en el script).
  - diámetro **40** → `element_key="tub_pvc_tricapa_f_40"`, `TipoTubo=2`.
- **Pluvial** (`tub_pvc_tricapa_v`):
  - diámetro **110** → `element_key="tub_pvc_tricapa_p_110"` (`tub_pvc_tricapa_p_110_script.py` / `TubPvcTricapaP110Script`).
  - otro diámetro (p. ej. 40) → `element_key="tub_pvc_tricapa_v"`, `TipoTubo=2`.

## Comportamiento esperado en la UI

- Combo de instalación: **Pluvial** y **Fecal**.
- Combo de diámetro (cuando aplica): Pluvial **110**; Fecal **25 | 40 | 110**.

## Fecha

Misma línea temporal que la migración a formato librería PolyLib (`saneamiento_polyline.pyp` + `polyline_reg_saneamiento.py`).
