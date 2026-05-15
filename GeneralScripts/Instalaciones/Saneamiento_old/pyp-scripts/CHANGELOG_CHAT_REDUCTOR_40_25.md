# Documentacion del chat: Reductor 40-25

Fecha: 2026-03-20

## Objetivo inicial

Corregir y entender la rotacion del reductor `40mm <-> 25mm` en `Saneamiento.py`, y revisar por que no aparecia el cuboide adicional definido en `Tapreduction_010.py`.

## Analisis funcional realizado

Se reviso la logica de deteccion, colocacion y orientacion de reductores en `Saneamiento.py`.

### Casos de orientacion detectados (tipo 0: 40-25)

- `40 -> 25`:
  - Se considera orientacion normal (`is_reversed = False`).
  - Direccion base usada: `v1`.
- `25 -> 40`:
  - Se considera invertido (`is_reversed = True`).
  - Direccion base usada: `-v2`.
- Cambio con angulo (despues de codo):
  - Se marca como `is_after_elbow` cuando para el reductor almacenado `v1 == v2`.
  - Usa constantes `REDUCER_AFTER_ELBOW_*`.

### Influencia de `path_idx`

- `path_idx` no determina el volteo del reductor.
- Se usa para trazabilidad/keys/layer overrides.
- El sentido real depende del orden geometrico del path (`d1/d2`).

## Cambios aplicados en codigo

## 1) `Saneamiento.py`: ajuste de rotacion invertida 25->40

Se elimino la rotacion adicional de 180 grados para `reducer_type == 0` cuando `is_reversed`.

Motivo:
- El sentido ya estaba resuelto por `direction` (`v1` o `-v2`).
- Esa rotacion extra podia provocar doble inversion en algunos escenarios.

Resultado esperado:
- Comportamiento mas consistente al invertir el sentido de dibujo.

## 2) `Tapreduction_010.py`: matriz de traslacion global

Se agregaron parametros hardcodeados:

- `TRANS_X`
- `TRANS_Y`
- `TRANS_Z`

Y se aplico una `Matrix3D` de traslacion al conjunto generado para ajustar posicionamiento del reductor sin tocar otras logicas.

## 3) `Tapreduction_010.py`: union temporal del cuboide adicional

En un paso intermedio se unio `cuboide_centro` al `brep` principal con `MakeUnion` para forzar su visibilidad en `Saneamiento.py`.

## 4) `Saneamiento.py`: extraccion de todas las geometrias del resultado

Se detecto que `Saneamiento.py` tomaba solo `result.elements[0]` al crear reductor, por lo que geometria adicional podia perderse.

Se modifico para:
- Extraer todas las geometrias de `result.elements`.
- Procesarlas para el flujo de creacion del reductor.

## 5) Cambio final para piezas independientes (tap + cuboide)

Segun el requerimiento:
- Tap reductor y cuboide adicional deben ser independientes (no unidos).

Se ajusto:

- `Tapreduction_010.py`:
  - Se retiro la union `MakeUnion` del cuboide adicional con el cuerpo principal.
- `Saneamiento.py`:
  - Se trabaja con lista `reducer_parts` (no una sola geometria).
  - Se aplican las mismas transformaciones a cada subgeometria:
    - centrado,
    - pivote,
    - rotaciones,
    - traslacion a vertice,
    - offsets.
  - Se crea un `ModelElement3D` por subgeometria.
  - Los atributos funcionales del tap (RED.Ø40-25, etc.) se aplican solo al elemento principal.
  - Se agregan todas las piezas al array final `elems`.

Objetivo:
- Que aparezcan tanto tap como cuboide.
- Que puedan comportarse como piezas separadas dentro del resultado.

## Observaciones de logs relevantes del usuario

- Se confirmo import local de `Tapreduction_010.py` desde:
  - `C:\ProgramData\Nemetschek\Allplan\2025\Etc\PythonPartsFramework\GeneralScripts\Instalaciones\Saneamiento\pyp-scripts\Tapreduction_010.py`
- Se confirmo deteccion y creacion de reductor `D40-D25`.
- Se confirmo flujo de colocacion en `Saneamiento.py`:
  - deteccion de reductor recto,
  - aplicacion de transforms,
  - creacion de `ModelElement3D`.

## 6) Conservacion de atributos/propiedades por subpieza

Se amplio la extraccion de partes del reductor para conservar metadatos originales:

- `source_attrs`: atributos propios por subelemento.
- `source_props`: propiedades comunes del subelemento (incluye color).

Aplicacion final:

- Si una parte trae `source_attrs`, se reasignan a esa parte.
- Se mantiene la `Layer` calculada por `Saneamiento.py`.
- Se conserva el color propio de cada subpieza cuando hay `source_props`.

Ademas, se corrigio la llamada al creador del reductor para pasar documento real:

- Antes: `create_reducer_element(..., None)`
- Ahora: `create_reducer_element(..., reducer_doc)`

Esto habilita que `Tapreduction_010.py` pueda resolver y aplicar atributos dependientes de documento (por ejemplo `Material=CAVITAT`).

## 7) Correccion de color final (tap/cuboides)

Para tipo 0 (`Tapreduction_010.py`), se forzo regla de fallback si no llega color en propiedades fuente:

- parte principal (tap): color `50`
- cuboides auxiliares: color `7`

Con esto se evita heredar el color de flujo general (ej. `70`) en subpiezas del reductor.

## 8) Limpieza

Se eliminaron logs temporales de debug por subpieza usados durante diagnostico:

- trazas de `DEBUG Reducer part[...]`
- trazas de color aplicado por parte
- trazas de aplicacion/no aplicacion de atributos originales

## 9) Estabilizacion de rotacion en polilineas inclinadas

Se detecto un comportamiento intermitente donde el reductor "rotaba sobre si mismo"
entre casos similares, dependiendo de la inclinacion de la polilinea (roll alrededor
del eje longitudinal).

Correccion aplicada en `Saneamiento.py`:

- despues de orientar el reductor de `+X local` al vector del tramo, se agrega una
  fase de estabilizacion de roll alrededor del propio eje del reductor.
- la estabilizacion usa como referencia el `Z global` proyectado al plano perpendicular
  al eje del tramo, siguiendo el mismo criterio usado previamente para tubos no 25mm.
- se aplica una rotacion minima adicional alrededor del eje del tramo para fijar
  una "cara estable" del reductor y evitar giros aparentes por inclinacion.

Resultado:

- orientacion visual consistente del reductor en trazados inclinados.
- se evita variacion entre dos ejecuciones donde antes uno quedaba "bien" y otro
  parecia girado sobre si mismo.

## Estado actual

Quedo implementado el enfoque de piezas independientes:

- `Tapreduction_010.py` devuelve tap + cuboide adicional separados.
- `Saneamiento.py` transforma y crea elementos para todas las subgeometrias devueltas.
- Tap y cuboides se crean como piezas separadas.
- Se conservan atributos/propiedades por parte cuando la API los entrega.
- Colores correctos para tap y cuboides segun `Tapreduction_010.py`.
- Rotacion estabilizada del reductor en polilineas inclinadas (sin giro sobre si mismo).

Si aparece una regresion futura, el siguiente paso recomendado es volver a loguear en runtime:

- cantidad de `result.elements`,
- cantidad de `reducer_parts` extraidas,
- y tipos/clases de geometria extraida por elemento.

Esto permite confirmar si la perdida sucede en:
- el script productor (`Tapreduction_010.py`),
- la extraccion en `Saneamiento.py`,
- o una etapa de visualizacion/agrupacion de Allplan.

