# Manual de Usuario Global de Instalaciones

## 1. Objetivo del documento

Este manual describe el funcionamiento global del sistema de instalaciones implementado sobre `PolyLib`, `MacroCore`, `ElementosDefinidos` y `ElementosNoDefinidos`, tomando la instalación de `Agua` como ejemplo de referencia.

El objetivo es documentar el comportamiento funcional completo para usuario final y para personal técnico que necesite entender cómo se trabaja con la herramienta en Allplan:

- cómo se crea una instalación;
- cómo se edita;
- cómo se asignan atributos y layers;
- cómo se insertan macros y elementos especiales;
- cómo se usan los puntos no definidos y los puntos libres;
- cómo funciona la copia por atributo padre;
- cómo se guardan y restauran los datos;
- y qué partes cambian entre instalaciones y cuáles son comunes.

## 2. Alcance

Este manual aplica a todas las instalaciones que usan la misma base funcional. En la práctica, el flujo es común entre instalaciones como:

- Agua;
- Electricidad;
- Ventilación;
- y otras instalaciones futuras montadas sobre la misma arquitectura.

Lo que cambia entre instalaciones es, principalmente:

- el nombre comercial de la instalación;
- los elementos disponibles;
- los layers por defecto;
- ciertos atributos por defecto;
- y algunas reglas geométricas concretas de tubos, codos, tes, manguitos o accesorios.

Lo que no cambia es el funcionamiento general de la herramienta.

## 3. Cómo leer este manual

Cuando se cite `Agua`, debe entenderse como ejemplo real de una instalación concreta.

Cuando se hable de “instalación”, se está describiendo un comportamiento común reutilizable.

Para las capturas se utiliza el marcador:

`[[CAPTURA-XX: descripción de la imagen a insertar]]`

La recomendación es sustituir cada marcador por una captura real de la interfaz, del estado del modelo o del resultado en pantalla.

## 4. Visión general del sistema

El sistema de instalaciones se apoya en cuatro bloques funcionales:

### 4.1. `PolyLib`

Es la base del sistema. Gestiona:

- la polilínea;
- los modos de dibujo;
- la edición de segmentos;
- la aplicación de atributos y layers;
- la generación final de PythonParts;
- la persistencia del estado;
- y la copia de elementos a otros archivos de dibujo en función del atributo padre.

### 4.2. `MacroCore`

Gestiona la lógica común de macros:

- lectura de parámetros de macro desde la paleta;
- selección del punto de colocación;
- previsualización real de la macro;
- inserción final de macros en el documento;
- y control de cota y rotación.

### 4.3. `ElementosDefinidos`

Gestiona elementos especiales definidos por la instalación, por ejemplo:

- `T sortida`;
- `Clau de Pas`;
- `Colze Base`;
- `Taps`.

Permite trabajar con dos modelos:

- marcadores sobre la polilínea;
- puntos libres colocados directamente en el espacio.

### 4.4. `ElementosNoDefinidos`

Gestiona puntos lógicos de recorrido cuando todavía no existe geometría final.

Sirve para:

- definir intenciones de trazado;
- marcar inicios, finales y bifurcaciones;
- detectar puntos comunes entre caminos;
- y preparar una topología lógica que luego puede convertirse en geometría o exportarse.

## 5. Diferencia entre lo común y lo específico de cada instalación

En todas las instalaciones existe un patrón común:

1. El usuario selecciona el tipo de instalación.
2. Define parámetros de dibujo y configuración.
3. Dibuja o edita la polilínea.
4. La herramienta genera previsualización de segmentos y conexiones.
5. El usuario puede aplicar layers, atributos y orientación.
6. El usuario puede añadir macros, elementos definidos, puntos libres o puntos no definidos.
7. Al finalizar, el sistema crea los PythonParts y, si corresponde, genera copias por atributo padre.

Las diferencias por instalación suelen limitarse a:

- catálogo de elementos;
- diámetros disponibles;
- combinaciones permitidas;
- tipo de distribución;
- reglas geométricas específicas;
- nombres de layers;
- y atributos por defecto.

## 6. Flujo general de trabajo

El flujo recomendado de uso es el siguiente:

1. Seleccionar la instalación.
2. Seleccionar el tipo principal de elemento.
3. Configurar diámetro, distribución y demás parámetros de paleta.
4. Elegir modo de dibujo.
5. Dibujar el recorrido principal.
6. Revisar la previsualización de tubos y accesorios.
7. Ajustar layers y atributos.
8. Insertar macros o elementos especiales si procede.
9. Insertar soportes si procede.
10. Finalizar la creación.
11. Revisar el resultado generado en el documento y las posibles copias en otros archivos de dibujo.

`[[CAPTURA-01: paleta principal completa de la instalación con las secciones visibles]]`

## 7. Modos principales de trabajo

La herramienta se organiza en torno a tres modos principales:

### 7.1. Modo creación

Es el modo en el que se dibuja una nueva polilínea.

En este modo el usuario:

- hace clic para definir puntos;
- genera segmentos consecutivos;
- construye un camino nuevo;
- y ve una previsualización de la instalación antes de crear los objetos definitivos.

### 7.2. Modo edición

Es el modo en el que se modifica una polilínea ya existente o el recorrido activo.

En este modo el usuario puede:

- seleccionar segmentos;
- borrar tramos;
- modificar diámetros;
- insertar puntos;
- y corregir la geometría antes de finalizar.

### 7.3. Modo extender

Es el modo en el que se continúa un trazado existente o se interactúa con elementos ya guardados sin iniciar una polilínea completamente nueva.

## 8. Parámetros principales de la paleta

Los nombres exactos pueden variar en visibilidad según la instalación, pero funcionalmente los bloques son los mismos.

### 8.1. Selección de instalación

- `InstallationType`

Permite escoger el tipo base de instalación. En Agua, por ejemplo, puede corresponder a:

- `Polietilè`;
- `Multicapa`;
- `Armaflex`.

Este parámetro condiciona:

- el catálogo de geometrías;
- las conexiones permitidas;
- los diámetros disponibles;
- y parte de los atributos y reglas geométricas.

`[[CAPTURA-02: combo de tipo de instalación desplegado con opciones visibles]]`

### 8.2. Diámetro

- `DiameterType`
- `DiameterTypeStr`
- `DiameterModify`

Permiten definir o modificar el diámetro del recorrido o de segmentos ya seleccionados.

El diámetro influye en:

- la geometría generada;
- la selección del PythonPart correcto;
- los atributos por defecto;
- y la compatibilidad con ciertos accesorios, como tes o reducciones.

### 8.3. Distribución

- `DistributionType`

En Agua, la distribución distingue principalmente entre:

- `TD`;
- `IS`.

Esta selección afecta a:

- el tipo de geometría;
- el conjunto de atributos aplicados;
- el atributo padre;
- y el tratamiento de capas y materiales en algunos elementos.

### 8.4. Tipo de agua

- `WaterType`

Se usa cuando la instalación necesita distinguir variantes internas del sistema.

### 8.5. Modos de dibujo

- `PointMode`
- `ExtendPolyline`
- `EditPolyline`
- `CreatePolyline`

Controlan si el usuario está:

- extendiendo;
- editando;
- o creando.

### 8.6. Limitación angular

- `CheckBoxLimitarAngulos`
- `RotationAngle`
- botón `DefineOrientation`

Permiten restringir el dibujo a determinados ángulos o definir una orientación de referencia.

En instalaciones como Agua, el sistema trabaja con restricciones reales de ángulo según el tipo de instalación.

### 8.7. Layers

- `LayerTypes`
- botón `aplicarLayers`

Permiten asignar el layer activo a elementos seleccionados.

Esta acción no genera elementos nuevos; modifica la configuración aplicada a los existentes o a los seleccionados.

### 8.8. Atributos manuales

- `AttributeValue`
- botón `AttributeApply`

Permiten aplicar atributos manuales a los elementos seleccionados.

Su uso es especialmente importante cuando se quiere completar información antes de finalizar.

### 8.9. Opciones generales

- `CreatePythonPart`
- `AddPolilyne`
- `AddCube`
- `FunctionalName`

Sirven para controlar:

- si se crea PythonPartGroup;
- si la polilínea de eje se añade al resultado;
- si se crea geometría auxiliar;
- y con qué nombre funcional se agrupa el resultado.

## 9. Botones y acciones principales

Los eventos base del sistema son comunes a todas las instalaciones.

### 9.1. `1003` Finalizar creación

Acción de cierre del proceso de modelado.

Esta acción:

- valida el estado;
- genera los elementos finales;
- crea PythonParts;
- inserta macros y elementos definidos;
- añade soportes;
- y ejecuta la copia por atributo padre si aplica.

### 9.2. `1004` Borrar sección

Elimina:

- segmentos seleccionados por caja;
- un punto de corte seleccionado;
- o un tramo seleccionado individualmente.

### 9.3. `1007` Modificar diámetro

Aplica el nuevo diámetro:

- a los segmentos seleccionados;
- o al segmento activo.

Si no hay selección, el sistema avisa al usuario.

### 9.4. `1009` Aplicar layers

Aplica el layer seleccionado a los elementos seleccionados.

### 9.5. `1011` Aplicar atributo

Aplica el atributo manual introducido por el usuario a la selección activa.

### 9.6. `1012` Definir orientación

Inicia la captura de orientación 3D, normalmente mediante una referencia en XY.

`[[CAPTURA-03: ejemplo de modo orientación activo y línea de referencia]]`

## 10. Funcionamiento paso a paso del trazado principal

### 10.1. Selección inicial

El usuario debe comenzar configurando:

- la instalación;
- el tipo;
- el diámetro;
- la distribución;
- y cualquier dato base de la paleta.

### 10.2. Inicio del dibujo

En modo creación, cada clic define un punto de la polilínea.

A partir de esos puntos, el sistema:

- guarda la secuencia del camino;
- calcula segmentos;
- detecta nodos;
- y prepara la previsualización de tubos y accesorios.

### 10.3. Previsualización

Antes de generar el resultado final, la herramienta representa:

- el elemento principal de la instalación;
- los accesorios automáticos;
- y, cuando aplica, elementos derivados como manguitos, codos o tes.

La previsualización no es todavía el resultado final definitivo, pero sí refleja la lógica geométrica prevista.

`[[CAPTURA-04: recorrido en previsualización antes de finalizar]]`

### 10.4. Guardado y reconstrucción interna

El sistema va almacenando:

- paths guardados;
- segmentos reconstruidos;
- metadatos persistentes;
- atributos aplicados;
- layers aplicados;
- y estado serializado.

Esto permite que la instalación se pueda reabrir y seguir editando.

## 11. Generación automática de accesorios

Una vez definido el recorrido, la instalación genera automáticamente piezas auxiliares según la topología.

### 11.1. Codo

Se genera cuando en un nodo coinciden dos conexiones no colineales.

### 11.2. Manguito

Se genera cuando en un nodo coinciden dos conexiones colineales.

### 11.3. Te o bifurcación

Se genera cuando en un nodo existen tres conexiones.

### 11.4. Prioridad entre accesorios

La prioridad funcional es:

1. `TE` si existen tres conexiones.
2. `Codo` si hay dos conexiones no colineales.
3. `Manguito` si hay dos conexiones colineales.

Si un nodo se resuelve como `TE`, no se crea además un codo o un manguito en ese mismo nodo.

`[[CAPTURA-05: ejemplo comparativo de codo, manguito y te en nodos distintos]]`

## 12. Edición de recorridos existentes

Una vez dibujada o recuperada una instalación, el usuario puede editarla.

### 12.1. Selección

La selección puede hacerse:

- por tramo individual;
- por caja;
- o sobre ciertos nodos o puntos de corte.

### 12.2. Borrado

Al borrar segmentos o nodos, el sistema reconstruye la conectividad.

Como consecuencia, puede:

- desaparecer un accesorio;
- aparecer otro distinto;
- cambiar el tipo de unión;
- o regenerarse la lógica de codos, manguitos y tes.

### 12.3. Cambio de diámetro

Al modificar el diámetro de un segmento o de un conjunto de segmentos:

- se actualiza la metadata;
- se recalculan elementos dependientes;
- y en la generación final prevalecen los atributos del modelo real generado para ese diámetro.

## 13. Layers

El sistema trabaja con layers por defecto y con layers aplicados manualmente.

### 13.1. Layers por defecto

Cada instalación define sus propios layers base. Por ejemplo, Agua trabaja con layers como:

- `KN_AIGUA_FAB`;
- `IS_CON_VENT_EIX`;
- y otros layers específicos de instalación.

### 13.2. Layers aplicados por el usuario

Cuando el usuario aplica un layer desde paleta:

- ese valor se guarda para los elementos seleccionados;
- y se utiliza durante la creación final si la lógica del elemento no lo bloquea.

### 13.3. Casos en los que el layer no se pisa

En Agua existen piezas TD con geometría `outer + inner` donde el `outer` puede conservar:

- material propio;
- y layer propio del modelo.

En esos casos, el sistema protege esa parte externa para evitar que la paleta destruya una condición técnica necesaria.

## 14. Atributos

Los atributos pueden venir de tres fuentes:

### 14.1. Atributos por defecto del modelo

Se obtienen desde el PythonPart o desde la definición base del elemento.

### 14.2. Atributos personalizados aplicados por el usuario

Se aplican desde paleta sobre elementos seleccionados.

### 14.3. Atributos padre

Son atributos clave para la organización funcional y la copia entre archivos de dibujo.

Los más importantes son:

- `pmp_pare`;
- `6_CC_IS`.

### 14.4. Reglas funcionales típicas

En Agua:

- en `TD` se usa `pmp_pare`;
- en `IS` se usa `pmp_pare` y `6_CC_IS`.

### 14.5. Validación previa a finalizar

Antes de crear el resultado definitivo, el sistema comprueba si hay elementos:

- sin layer;
- o sin atributo padre.

Si detecta elementos incompletos, muestra una advertencia para que el usuario decida:

- continuar;
- o volver a configuración.

`[[CAPTURA-06: mensaje de advertencia previo a finalizar por falta de layer o atributo padre]]`

## 15. Rotación y orientación

El sistema soporta rotaciones en:

- `X`;
- `Y`;
- `Z`.

Estas rotaciones se usan en:

- macros;
- elementos definidos;
- y algunos flujos de colocación especial.

En paleta aparecen habitualmente como:

- `RotX`, `RotY`, `RotZ`;
- o `MacroRotX`, `MacroRotY`, `MacroRotZ`.

## 16. Macros de librería

Las macros permiten insertar objetos de librería sobre la instalación.

### 16.1. Tipos de macro

El sistema soporta:

- `SmartSymbol`;
- `Fixture`.

### 16.2. Parámetros principales

- `MarkerPointMode`
- `MacroLibraryElementType`
- `MacroSmartSymbolPath`
- `MacroFixturePath`
- `MacroSelectedLocalZ`
- `MacroZAbs`
- `MacroZRelative`
- `MacroRotX`
- `MacroRotY`
- `MacroRotZ`

### 16.3. Modos de colocación

La macro puede colocarse:

- al inicio de la polilínea;
- al final;
- o en un punto libre seleccionado por el usuario.

### 16.4. Altura de la macro

La altura puede resolverse de dos maneras:

- mediante cota absoluta;
- o mediante cota relativa a un local seleccionado.

Si se selecciona un local, la cota final se calcula como:

`cota del local + cota relativa`

### 16.5. Flujo de trabajo

1. Elegir tipo de macro.
2. Elegir archivo de librería.
3. Elegir modo de punto.
4. Seleccionar local si se desea trabajar con altura relativa.
5. Definir rotación.
6. Agregar la macro.
7. Revisar el preview real.

`[[CAPTURA-07: bloque de paleta de macros con ruta y parámetros de rotación]]`

`[[CAPTURA-08: ejemplo de preview real de una macro colocada sobre el trazado]]`

## 17. Elementos definidos

Los elementos definidos son accesorios especiales controlados por la propia instalación.

En Agua, ejemplos típicos son:

- `T sortida`;
- `Clau de Pas`;
- `Colze Base`;
- `Taps`.

### 17.1. Formas de trabajo

Existen dos modalidades:

- elemento sobre marcador asociado al recorrido;
- elemento colocado como punto libre.

### 17.2. Parámetros principales

- `DefinedElementType`
- `ElementPointMode`
- `ElementRadius`
- `ElementZAbs`
- `RotX`
- `RotY`
- `RotZ`
- `PointType` o `TipoPuntoLibre`

### 17.3. Inserción mediante marcador

Flujo:

1. Activar captura de punto del elemento.
2. Seleccionar un punto válido.
3. Confirmar la inserción del marcador.
4. Ajustar rotación si es necesario.
5. Finalizar la creación.

### 17.4. Inserción mediante punto libre

Flujo:

1. Elegir el tipo de elemento.
2. Elegir la función del punto libre.
3. Hacer clic en el plano.
4. Revisar preview.
5. Finalizar el modo.

### 17.5. Qué hace internamente el sistema

El sistema:

- almacena el punto;
- guarda su rotación;
- genera preview 3D;
- detecta puntos comunes;
- y lo materializa al finalizar.

`[[CAPTURA-09: inserción de un elemento definido mediante marcador]]`

`[[CAPTURA-10: inserción de un elemento definido mediante punto libre]]`

## 18. Puntos no definidos

Los puntos no definidos sirven para describir la lógica del recorrido sin construir todavía la geometría final.

### 18.1. Tipos de punto

El sistema puede trabajar con puntos como:

- inicio;
- final;
- intermedio libre;
- intermedio ordenado;
- bifurcación.

### 18.2. Parámetros de paleta

- `TipoCamino`
- `TipoPuntoOrden`
- `ColorPuntosNoDefinidos`
- `PathId`
- `DeteccionPuntosComunesActiva`
- `ToleranciaPuntosComunesMm`

### 18.3. Para qué sirven

Permiten:

- marcar la intención del recorrido;
- definir topología;
- compartir nodos entre caminos;
- y generar una salida lógica estructurada.

### 18.4. Detección de puntos comunes

Si el usuario crea un punto cerca de otro camino y la detección está activa:

- el sistema puede anclarlo al punto existente;
- marcarlo como punto común;
- y agruparlo dentro de una topología compartida.

### 18.5. Duplicados en puntos no definidos

El módulo evita generar ciertos nodos automáticos si ya existe un nodo explícito equivalente.

Esto impide:

- duplicar cruces;
- contaminar la topología;
- y producir resultados ambiguos.

`[[CAPTURA-11: ejemplo de puntos no definidos con colores distintos por camino]]`

`[[CAPTURA-12: ejemplo de cruce compartido detectado como punto común]]`

## 19. Soportes

La herramienta también incorpora un flujo independiente para soportes.

### 19.1. Parámetros principales

- tipo de soporte;
- subtipo;
- superficie;
- cota A;
- cota B;
- ángulo de inclinación;
- atributo de soporte.

### 19.2. Flujo de uso

1. Configurar parámetros del soporte.
2. Pulsar `Insertar soporte`.
3. Definir posiciones.
4. Revisar preview.
5. Pulsar `Crear soportes` para acumular.
6. Repetir si es necesario.
7. Aplicar atributos o borrar soportes acumulados.

`[[CAPTURA-13: bloque de paleta de soportes y preview del soporte antes de acumular]]`

## 20. Duplicados y copias: diferencias importantes

Aquí es clave distinguir entre dos conceptos distintos:

### 20.1. Eliminación de duplicados geométricos internos

Durante la creación de PythonParts individuales o inserción sin PythonPart:

- el sistema elimina duplicados manteniendo el orden;
- esto evita repetir el mismo objeto dos veces en el resultado final;
- y reduce errores de inserción.

Esto afecta a listas internas de geometría, no a la lógica funcional del modelo.

### 20.2. Duplicados lógicos evitados en topología

En `ElementosDefinidos` y `ElementosNoDefinidos`, el sistema evita crear nodos automáticos duplicados si ya existe un nodo explícito equivalente.

Esto protege:

- la lectura del grafo;
- la interpretación de cruces;
- y la posterior generación de elementos.

### 20.3. Copias a otros archivos de dibujo

Este no es un duplicado erróneo. Es una funcionalidad deliberada.

Cuando un elemento o PythonPart tiene atributo padre `pmp_pare`, el sistema:

1. agrupa elementos por ese valor;
2. busca un archivo de dibujo cargado cuyo nombre contenga ese identificador;
3. copia allí los elementos 3D;
4. guarda los UUID de esas copias;
5. y en una edición posterior elimina las copias previas antes de generar las nuevas.

Esto significa que:

- la instalación principal permanece en el archivo actual;
- y ciertas representaciones 3D pueden replicarse en otros archivos de dibujo relacionados.

### 20.4. Cómo funciona la limpieza de copias previas

Antes de una nueva generación:

- se leen los UUID guardados;
- se localizan los archivos donde se copiaron;
- se eliminan las copias antiguas;
- y se vuelve a generar el conjunto actualizado.

Esto evita que cada edición deje residuos o copias obsoletas.

`[[CAPTURA-14: ejemplo de atributo padre aplicado y archivo destino cargado en Allplan]]`

`[[CAPTURA-15: ejemplo visual del mismo elemento en archivo original y en archivo copiado]]`

## 21. Persistencia y restauración

La herramienta guarda estado serializado para poder reabrir y seguir editando.

Entre los datos persistidos se incluyen:

- paths;
- segmentos;
- marcadores;
- puntos libres;
- puntos no definidos;
- atributos aplicados;
- layers aplicados;
- y referencias a copias creadas en otros archivos.

Esto permite que el usuario no tenga que reconstruir manualmente la instalación desde cero al reabrirla.

## 22. Qué ocurre al pulsar “Finalizar”

Cuando el usuario pulsa `Finalizar`, el sistema hace, en términos generales, lo siguiente:

1. limpia copias previas si existen;
2. reconstruye elementos de la instalación;
3. aplica atributos y layers;
4. crea PythonParts individuales o agrupados;
5. añade polilínea si está activado;
6. añade macros;
7. añade elementos definidos;
8. añade soportes;
9. crea el contenedor final;
10. copia elementos a otros archivos si corresponde por `pmp_pare`;
11. guarda el estado serializado.

## 23. Recomendaciones de uso para el usuario

- Configurar primero la instalación y el diámetro antes de dibujar.
- Revisar la distribución antes de modelar, porque condiciona atributos y geometría.
- Aplicar layers y atributos antes de finalizar.
- Usar elementos definidos y macros solo cuando el trazado principal esté razonablemente estable.
- Revisar especialmente `pmp_pare` y `6_CC_IS` si la instalación depende de copias o de sectorización.
- Si aparecen advertencias al finalizar, corregirlas antes de continuar salvo que exista un motivo claro para omitir esa información.

## 24. Qué debe capturarse para completar este manual

Para dejar este documento listo para entrega final, conviene capturar al menos:

- vista general de la paleta;
- selección del tipo de instalación;
- ejemplo de creación de una polilínea;
- ejemplo de edición de un tramo;
- aplicación de layer;
- aplicación de atributo;
- advertencia de validación previa a finalizar;
- inserción de macro;
- inserción de elemento definido;
- inserción de punto no definido;
- flujo de soportes;
- y ejemplo de copias por atributo padre.

## 25. Resumen ejecutivo

El sistema de instalaciones comparte una base común muy sólida. Aunque cada instalación cambie nombres, piezas o reglas puntuales, el usuario trabaja siempre sobre el mismo patrón:

- dibujar;
- editar;
- enriquecer con atributos y layers;
- insertar elementos auxiliares;
- y finalizar para generar el modelo definitivo.

El caso de Agua demuestra este funcionamiento común y sirve como referencia válida para documentar el resto de instalaciones con cambios menores de catálogo, nomenclatura y configuración.
