# Documentación JSON de Soportes

Guía de referencia del contrato JSON consumido por `SoportesFromJson.py` y aplicado en `Soportes.py`.

## 1) Contrato oficial

```json
{
  "soportes": [
    {
      "tipo": "Omega",
      "subtipo": "Agua",
      "superficie": "Perforado",
      "posicion1": [0.0, 0.0, 0.0],
      "posicion2": [1000.0, 0.0, 0.0],
      "angulo_inclinacion": 0.0,
      "cota_a": 110.0,
      "cota_b": 300.0
    }
  ]
}
```

## 2) Campos y obligatoriedad

| Campo | Obligatorio | Descripción |
|---|---|---|
| `tipo` | Sí | `Omega` o `Zeta` |
| `subtipo` | Sí | Valor semántico (no por medidas) |
| `superficie` | Recomendado | `Liso` o `Perforado` |
| `posicion1` | Sí | Punto 3D inicial `[x, y, z]` |
| `posicion2` | Sí | Punto 3D final `[x, y, z]` |
| `cota_a` | Sí | Cota A (altura vertical) |
| `cota_b` | Sí | Cota B (longitud base) |
| `angulo_inclinacion` | No | Giro adicional en grados |

Notas sobre `superficie`:
- Si llega vacía o no llega, el parser aplica fallback a `Perforado` y deja aviso en log.
- Si llega con valor inválido (distinto de `Liso`/`Perforado`), el soporte se invalida.

## 3) Reglas de negocio

### 3.1 Regla general por subtipo semántico

`subtipo` gobierna la instalación funcional (`Ventilación`, `Clima`, `Electricidad`, `Agua`, `Saneamiento`) y, con ello, capa (`layer`) y nombre (`pmp_nom`) en las combinaciones aplicables.

### 3.2 Reglas para `Omega`

Mapeo de subtipo semántico -> variante interna:

| Subtipo semántico | Variante interna |
|---|---|
| `Ventilacion` | `Venti.(SVP)` |
| `Clima` | `Varifix` |
| `Electricidad` | `Electr./Clima(SEP)` |
| `Varifix` | `Varifix` |
| `Agua` | `Varifix` |
| `Saneamiento` | `Varifix` |

Reglas adicionales:
- `Electr./Clima(SEP)`:
  - `Electricidad` -> `IS_SUPORTS_ELECTRICITAT` + `SUPORT ELECTRICITAT (SEP)`
- `Varifix`:
  - `Clima` -> `IS_SUPORTS_CLIMA` + `SUPORT CLIMA (SCP)`
  - `Agua` -> `IS_SUPORTS_AIGUA` + `SUPORT AIGUA`
  - `Saneamiento` -> `IS_SUPORTS_SANE` + `SUPORT SANE`
  - Si el soporte cae en variante `Varifix`, deben cumplirse `cota_a > 0` y `cota_b > 0`

### 3.3 Reglas para `Zeta`

- `subtipo` debe ser semántico (`Agua`, `Saneamiento`, `Ventilacion`, `Electricidad`, `Clima`)
- `subtipo` no define medidas por nombre (no usar `205x200mm`, `110x200mm`, etc.)
- La variante geométrica se decide únicamente por `cota_a`:
  - `cota_a == 0` -> variante `0mm` (**forzado a `PARAMS["Zeta"][0]`**)
  - `cota_a > 0` -> variante base con ala (`205x200mm`)
- Restricciones:
  - `cota_a` puede ser `0`, pero no puede ser `< 0`
  - `cota_b` debe ser `> 0`

Interacción entre `cota_a` y `subtipo` en Zeta:

**`cota_a == 0` (variante 0mm):**
- Layer y `pmp_nom` se conservan de PARAMS (`IS_SUPORTS_LINEALS`), **independientemente del subtipo**.
- `ATTR05` se conserva: `LINEAL;VARIFIX`.
- `ATTR01` sí se ajusta por subtipo: `W6` para Ventilación, `W1` para el resto.

**`cota_a > 0` (variante con ala):**
- El `subtipo` semántico define layer y `pmp_nom`:
  - `Ventilacion` -> layer `IS_SUPORTS_VENT` + `pmp_nom = SUPORT VENTILACIO (SVP)` + `ATTR01 = W6`
  - `Clima` -> layer `IS_SUPORTS_CLIMA` + `pmp_nom = SUPORT CLIMA (SCP)` + `ATTR01 = W1`
  - `Electricidad` -> layer `IS_SUPORTS_ELECTRICITAT` + `pmp_nom = SUPORT ELECTRICITAT (SEP)` + `ATTR01 = W1`
  - `Agua` -> layer `IS_SUPORTS_AIGUA` + `pmp_nom = SUPORT AIGUA` + `ATTR01 = W1`
  - `Saneamiento` -> layer `IS_SUPORTS_SANE` + `pmp_nom = SUPORT SANE` + `ATTR01 = W1`
- `ATTR05` se fuerza a `ZETA;VARIFIX`.

### 3.4 Reglas para `Cinta`

- Variante única (`idx=0`), no depende del `subtipo`.
- `subtipo` por defecto: `Agua` (es el único uso previsto).
- Layer y atributos ya definidos en `PARAMS["Cinta"][0]`:
  - `LAYER_SHORT` = `IS_CINTA_PERFORADA`
  - `ATTR01` = `CINTA PERFORADA`
  - `ATTR13` = `CARGOL M5X2.5;2`
  - `pmp_nom` = `CINTA PERFORADA`
- Restricciones:
  - `cota_b` debe ser `> 0`
  - `cota_a` se **ignora**: la altura vertical es fija (86 mm desde PARAMS)
  - `superficie` se **ignora**: siempre se fuerza a Liso (sin perforaciones)
- Geometría: forma bilateral (como Omega, ambos laterales).

## 4) Aplicación de cotas y geometría

Una vez resuelta la variante:
- `cota_b` -> `LEN_X_HORIZONTAL = cota_b - 6 mm`
- `cota_a` -> `HEIGHT_VERTICAL = cota_a` (si `cota_a > 0`)

Orientación y colocación:
- Se orienta el soporte con el vector `posicion1 -> posicion2`
- Si existe `angulo_inclinacion`, se aplica rotación adicional alrededor del eje del soporte

## 5) Flujo de ejecución

1. `load_supports_from_json()` lee, valida y normaliza
2. `SupportModel.apply_json_definition()` decide familia y variante interna
3. Se aplican reglas por subtipo semántico (layer/`pmp_nom`/atributos)
4. Se aplican cotas (`cota_a`, `cota_b`)
5. Se crea geometría y se orienta con `posicion1`/`posicion2`
6. Se aplica `angulo_inclinacion` (si existe)

## 6) Ejemplos válidos

### 6.1 Omega - Clima

```json
{
  "tipo": "Omega",
  "subtipo": "Clima",
  "superficie": "Perforado",
  "posicion1": [0, 0, 0],
  "posicion2": [1000, 0, 0],
  "cota_a": 205,
  "cota_b": 700
}
```

### 6.2 Omega - Varifix (Agua)

```json
{
  "tipo": "Omega",
  "subtipo": "Agua",
  "superficie": "Liso",
  "posicion1": [0, 0, 0],
  "posicion2": [800, 0, 0],
  "cota_a": 110,
  "cota_b": 825
}
```

### 6.3 Zeta sin ala vertical (`cota_a = 0`) -> usa `PARAMS["Zeta"][0]`

```json
{
  "tipo": "Zeta",
  "subtipo": "Agua",
  "superficie": "Perforado",
  "posicion1": [0, 0, 0],
  "posicion2": [1200, 0, 0],
  "cota_a": 0,
  "cota_b": 729.3
}
```

### 6.4 Zeta con ala vertical (`cota_a > 0`)

```json
{
  "tipo": "Zeta",
  "subtipo": "Ventilacion",
  "superficie": "Perforado",
  "posicion1": [0, 0, 0],
  "posicion2": [1200, 0, 0],
  "cota_a": 205,
  "cota_b": 200
}
```

## 7) Compatibilidad legacy (temporal)

Se aceptan de forma transitoria:
- Raíz: `supports`
- Campos: `type`, `subtype`, `surface`, `position1`, `position2`, `height_a`, `height_b`, `length_b`, `inclination_angle_deg`, `inclination_angel_deg`

Migrar siempre al contrato oficial:
- `soportes`, `tipo`, `subtipo`, `superficie`, `cota_a`, `cota_b`, `angulo_inclinacion`

## 8) Logs útiles

- `[Soportes] SoportesFromJson recargado: ...`
- `[Soportes] JSON path por defecto: ...`
- `[SoportesFromJson] RAW soporte #N: ...`
- `[SoportesFromJson] Aviso soporte #N: 'superficie' vacía; se usa 'Perforado' por defecto`
- `[SupportModel] Zeta: cota_a=0 -> se usa variante '0mm' (PARAMS['Zeta'][0])`
- `[SupportModel] JSON (Zeta): layer='...', pmp_nom='...', ATTR01='...', ATTR05='...' (...)`
- `[SupportModel] Configuración desde JSON: tipo='...', subtipo='...', idx=...`
- `[SoportesFromJson] Soporte inválido en JSON: ...`
