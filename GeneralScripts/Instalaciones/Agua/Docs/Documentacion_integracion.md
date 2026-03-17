# Integración polilínea ⇔ PythonParts (Agua)

## Objetivo

Unificar el flujo entre la polilínea de `Agua` y los PythonParts de tuberías (`polietile` IS/TD y `multicapa`), de forma que:

- El diámetro elegido en la polilínea controle la geometría 3D (dimensiones) del tubo.
- El tipo de agua (`water_type`) viaje desde la polilínea hasta el modelo.
- Los tubos complejos (TD, multicapa) se recorran correctamente a lo largo de la polilínea.

---

## 1. Flujo de datos desde la polilínea

Archivo clave: `agua_polyline.py`

- En el hook `_create_elements_for_segment_group`:
  - Se lee la configuración de instalación actual: `so.current_inst_config`.
  - Se determina el diámetro efectivo:
    - Si el usuario eligió uno en la paleta (`so.diameter_list` / `so.diameter_type`), se usa ese.
    - Si no, se usa el diámetro por defecto del modelo (`model_base["diameter"]`).
  - Para los sistemas de agua que usan tuberías instaladas:

```python
if model_base and element_type_core in ["polietile", "multicapa"]:
    # water_type viene de SegmentInfo
    water_type = segments[0].info.water_type  # si existe

    conduct_model = so._get_pythonpart_installed(
        element_key=selected_inst[0].key,
        exec_kwargs={
            "diameter": diameter,
            "dist_type": so.distribution_type,  # "IS" o "TD"
            "water_type": water_type,
        },
    )
```

- El resultado del PythonPart (`conduct_model`) se combina con el modelo de codo y se pasa al `PipelineProcessor`:

```python
elem3D_list = [
    {"type": "tubo_agua", "elem": conduct_model[0], "rotate": True, "color": 1},
]

if len(conduct_model) > 1:
    elem3D_list.append(
        {"type": "tubo_agua_inner", "elem": conduct_model[1], "rotate": True, "color": 1}
    )

elem3D_list.append({"type": "codo_90", "elem": codo_model[0], "rotate": True})

processor = PipelineProcessor(elem3D_list=elem3D_list, element_type="tubo_agua")
elements_generated = processor.process(segments=segments)
```

---

## 2. PythonPart de polietileno (`polietile_script.py`)

Archivo: `Agua/pyp-scripts/polietile_script.py`

- `execute` ahora acepta parámetros de la polilínea:

```python
def execute(self, *args, **kwargs) -> CreateElementResult:
    diameter = args[0] if args else kwargs.get("diameter")
    dist_type = kwargs.get("dist_type")     # "IS" o "TD"
    water_type = kwargs.get("water_type")   # "Fred", "Calent", etc.
```

### 2.1. Diámetro (`DiametroAplicar`)

- El `diameter` que viene de la polilínea se vuelca en `build_ele.DiametroAplicar`:

```python
if diameter is not None:
    diam_attr = getattr(self.build_ele, "DiametroAplicar", None)
    diam_int = int(diameter)  # si es posible
    if diam_int is not None:
        if diam_attr is not None and hasattr(diam_attr, "value"):
            diam_attr.value = diam_int
        else:
            setattr(self.build_ele, "DiametroAplicar", diam_int)
```

- Los modelos `TubPolietileModel` (IS) y `TubPolietileTDModel` (TD) leen `DiametroAplicar` y lo usan para seleccionar el índice de `PARAMS`, por encima del valor del combo.

### 2.2. Tipo de agua (`water_type`)

- Se traslada el tipo de agua al `build_ele` para que los modelos no tengan que usar el valor por defecto:

```python
if water_type:
    if dist_type == "IS":
        target_names = ["TipoDeAguaIS", "TipoDeAgua"]
    elif dist_type == "TD":
        target_names = ["TipoDeAguaTD", "TipoDeAgua"]
    else:
        target_names = ["TipoDeAgua"]

    for name in target_names:
        attr = getattr(self.build_ele, name, None)
        if attr is not None and hasattr(attr, "value"):
            attr.value = str(water_type)
        else:
            setattr(self.build_ele, name, str(water_type))
```

### 2.3. Ejecución del modelo

- En función de `dist_type` se llama al modelo correspondiente:

```python
if dist_type == "IS":
    tub = TubPolietileModel(self.build_ele, self.doc)
else:
    tub = TubPolietileTDModel(self.build_ele, self.doc)

model_ele_list = tub.build()
return CreateElementResult(model_ele_list)
```

---

## 3. PythonPart de multicapa (`multicapa_script.py`)

Archivo: `Agua/pyp-scripts/multicapa_script.py`

- `execute` ahora acepta `diameter`, `dist_type` y `water_type` igual que polietile:

```python
def execute(self, *args, **kwargs) -> CreateElementResult:
    diameter = args[0] if args else kwargs.get("diameter")
    dist_type = kwargs.get("dist_type")
    water_type = kwargs.get("water_type")
```

### 3.1. Distribución

- Actualmente solo existe versión TD:

```python
if dist_type == "IS":
    PythonUtility.ShowMessageBox(
        "Este tipo de tub multicapa no existe o no está disponible para la distribución IS.",
        PythonUtility.MB_OK,
    )
    return CreateElementResult([])
```

### 3.2. Mapeo de diámetro a tipo de multicapa

- El diámetro de la polilínea se traduce en el valor del combo `TipoTubMulticapa`, que lee `TubMulticapaTDModel`:

```python
if diameter is not None:
    diam_int = int(diameter)  # si es posible
    if diam_int == 20:
        tipo_valor = "Ø20/2mm"
    elif diam_int == 25:
        tipo_valor = "Ø25/2,5mm"
    elif diam_int == 32:
        tipo_valor = "Ø32/3mm"

    if tipo_valor:
        tipo_attr = getattr(self.build_ele, "TipoTubMulticapa", None)
        if tipo_attr is not None and hasattr(tipo_attr, "value"):
            tipo_attr.value = tipo_valor
        else:
            setattr(self.build_ele, "TipoTubMulticapa", tipo_valor)
```

### 3.3. Tipo de agua

- Igual que en polietile TD, se deja disponible en `TipoDeAguaTD` / `TipoDeAgua`:

```python
if water_type:
    for name in ("TipoDeAguaTD", "TipoDeAgua"):
        attr = getattr(self.build_ele, name, None)
        if attr is not None and hasattr(attr, "value"):
            attr.value = str(water_type)
        else:
            setattr(self.build_ele, name, str(water_type))
```

---

## 4. Generación de outer + inner a lo largo de la polilínea

Para los modelos TD de polietileno, el PythonPart devuelve **dos** elementos 3D:

- Outer: aislamiento.
- Inner: tubo interior.

Archivo: `Agua/pyp-scripts/utils/geo_handler.py` (`PipelineProcessor.process`).

- Se usa como `element_type_core = "tubo_agua"` y se añade una convención:
  - Outer → clave `"tubo_agua"`.
  - Inner → clave `"tubo_agua_inner"`.

- En el tramo recto, se generan ambos cuando existe la plantilla inner:

```python
if self.element_type_core in self.templates:
    longitud_recortada = seg.longitud_3d - offset_inicio - offset_final
    if longitud_recortada > 0:
        # Punto central del tramo
        dist_al_centro = offset_inicio + (longitud_recortada / 2.0)
        p_centro = AllplanGeo.Point3D(
            seg.start.X + v_unit.X * dist_al_centro,
            seg.start.Y + v_unit.Y * dist_al_centro,
            seg.start.Z + v_unit.Z * dist_al_centro,
        )

        # OUTER
        model_cond = self.modificar_dimensiones_brep(
            self.templates[self.element_type_core], longitud_recortada
        )
        element = self._aplicar_transformacion(
            model_cond, seg, custom_position=p_centro
        )
        result_list.append({...})

        # INNER opcional: "<core>_inner"
        inner_key = f"{self.element_type_core}_inner"
        if inner_key in self.templates:
            model_inner = self.modificar_dimensiones_brep(
                self.templates[inner_key], longitud_recortada
            )
            element_inner = self._aplicar_transformacion(
                model_inner, seg, custom_position=p_centro
            )
            result_list.append({...})
```

Con esto, el tramo TD de polietileno se dibuja como dos BReps paralelos, siguiendo exactamente la misma geometría de la polilínea.

---

## 5. Resumen del flujo completo

1. El usuario define una polilínea de agua (`agua_polyline.py`), eligiendo:
   - Diámetro.
   - Tipo de agua (agua fría, caliente, retorno, etc.).
   - Distribución IS / TD.
2. Cada `SegmentInfo` guarda:
   - `diameter`, `distribution_type`, `water_type`, `system`.
3. `_create_elements_for_segment_group`:
   - Llama al PythonPart correspondiente (`polietile_script`, `multicapa_script`) pasando `diameter`, `dist_type`, `water_type`.
4. El PythonPart:
   - Vuelca `diameter` en `DiametroAplicar` o `TipoTubMulticapa`.
   - Vuelca `water_type` en `TipoDeAgua*`.
   - Llama al modelo 3D (`TubPolietileModel`, `TubPolietileTDModel`, `TubMulticapaTDModel`).
5. El modelo:
   - Elige parámetros (`PARAMS`) en función de tipo de agua + diámetro.
   - Devuelve outer (+ inner si aplica).
6. `PipelineProcessor`:
   - Escala y coloca outer (+ inner) por cada segmento de la polilínea.
   - Añade codos donde hay cambios de dirección.

Este documento sirve como referencia de cómo viajan los parámetros clave (diámetro y tipo de agua) y cómo se conectan polilínea, PythonParts y modelos 3D en la integración de instalaciones de agua.