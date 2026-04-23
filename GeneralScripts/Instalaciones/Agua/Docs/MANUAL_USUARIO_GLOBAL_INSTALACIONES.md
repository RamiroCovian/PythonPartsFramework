# Manual de Usuario Global de Instalaciones

## 1. Finalidad del manual

Este manual explica cómo funciona una instalación dentro de Allplan desde el punto de vista del usuario.

Se ha tomado la instalación de Agua como ejemplo, pero el funcionamiento general es común al resto de instalaciones. Lo que cambia entre unas y otras son algunos elementos concretos, ciertos nombres de layer y algunos atributos, pero la forma de trabajar es prácticamente la misma.

El objetivo de este documento es que cualquier usuario pueda entender:

- cómo empezar una instalación;
- cómo dibujarla;
- cómo editarla;
- cómo aplicar layers y atributos;
- cómo insertar elementos definidos, macros y soportes;
- cómo funcionan las copias o duplicados;
- y qué comprobaciones conviene hacer antes de finalizar.

## 2. A quién va dirigido

Este manual está pensado para usuarios que necesiten modelar instalaciones en Allplan y entender el comportamiento general de la herramienta, sin entrar en detalles de programación ni en nombres internos del sistema.

## 3. Cómo se complementa este manual

Este documento se organiza en dos grandes bloques:

1. El funcionamiento global de las instalaciones.
2. Las particularidades de cada instalación.

En la primera parte se explica la lógica de uso común a todos los sistemas.

En la segunda parte se recogen las diferencias específicas de cada instalación, por ejemplo:

- los tipos de instalación disponibles;
- las distribuciones admitidas;
- los diámetros disponibles;
- los accesorios automáticos;
- los elementos definidos propios;
- las limitaciones o avisos especiales;
- y cualquier diferencia importante respecto a otras instalaciones.

De este modo, el usuario puede entender primero el funcionamiento general y después consultar, dentro del mismo manual, la unidad concreta de la instalación con la que vaya a trabajar.

## 4. Qué partes son comunes en todas las instalaciones

Todas las instalaciones comparten la misma lógica de trabajo:

1. Se selecciona el tipo de instalación.
2. Se configuran los parámetros principales en la paleta.
3. Se dibuja o edita el recorrido.
4. Se revisa la previsualización.
5. Se añaden, si hace falta, elementos definidos, macros o soportes.
6. Se aplican layers y atributos.
7. Se finaliza la creación.

Lo que cambia entre instalaciones suele ser:

- el tipo de elementos disponibles;
- los diámetros;
- las conexiones;
- algunos layers;
- y algunos atributos asociados a cada sistema.

## 5. Vista general del trabajo con una instalación

El trabajo habitual con una instalación se basa en tres ideas:

- dibujar un recorrido;
- enriquecer ese recorrido con información;
- y generar el resultado final.

En la práctica, esto significa que primero se crea el trazado principal y después se añaden o ajustan el resto de elementos necesarios.

`[[CAPTURA-01: paleta principal completa de la instalación con sus apartados visibles]]`
![alt text](CAPTURA-01.png)

## 6. Flujo de trabajo recomendado

El orden más recomendable para trabajar es este:

1. Elegir el tipo de instalación.
2. Elegir el tipo de tubo o sistema.
3. Definir diámetro, distribución y resto de parámetros básicos.
4. Dibujar el recorrido principal.
5. Revisar uniones, codos y bifurcaciones.
6. Aplicar layers y atributos si es necesario.
7. Insertar elementos definidos, macros o soportes.
8. Comprobar que la información esté completa.
9. Pulsar el botón de finalizar.

Seguir este orden ayuda a evitar correcciones posteriores innecesarias.

## 7. Modos principales de trabajo

La herramienta suele trabajar con tres modos principales.

### 6.1. Modo creación

Es el modo que se utiliza para dibujar un recorrido nuevo.

En este modo el usuario va definiendo puntos y la instalación crea el trazado entre ellos.

### 6.2. Modo edición

Es el modo que se utiliza para corregir o modificar un recorrido ya dibujado.

En este modo se pueden seleccionar tramos, borrar partes, cambiar diámetros o ajustar la geometría.

### 6.3. Modo extender

Es el modo que se utiliza para continuar un recorrido ya existente sin empezar desde cero.

## 8. Qué debe configurar el usuario antes de dibujar

Antes de empezar a dibujar conviene revisar los campos principales de la paleta.

### 7.1. Tipo de instalación

Es el campo donde el usuario elige el sistema con el que va a trabajar.

En Agua, por ejemplo, puede elegir entre varias opciones como:

- Polietilè;
- Multicapa;
- Armaflex.

Este campo define qué geometría y qué comportamiento tendrá la instalación.

`[[CAPTURA-02: desplegable del tipo de instalación abierto con las opciones visibles]]`
![alt text](CAPTURA-02.png)

### 7.2. Diámetro

El diámetro condiciona:

- el tamaño del elemento principal;
- las piezas de conexión compatibles;
- y parte de los atributos asociados.

Antes de dibujar, conviene comprobar que el diámetro seleccionado es el correcto.

### 7.3. Distribución

La distribución define cómo debe comportarse la instalación dentro del sistema.

En Agua es habitual trabajar con modos como:

- TD;
- IS.

La distribución puede afectar a:

- la forma de los elementos;
- los atributos aplicados;
- y el comportamiento de ciertos accesorios.

### 7.4. Tipo de agua u otras variantes

Algunas instalaciones incluyen campos adicionales para distinguir variantes internas del sistema. Si la paleta muestra este dato, conviene definirlo antes de empezar.

### 7.5. Ángulos y orientación

Si la instalación trabaja con limitación angular o con orientación definida, estos parámetros deben comprobarse al inicio para evitar tener que rehacer el recorrido más adelante.

## 9. Cómo dibujar una instalación

El dibujo de la instalación se basa en una secuencia de clics que definen el recorrido.

### 8.1. Inicio del recorrido

El usuario hace clic en el primer punto del trazado.

### 8.2. Continuación del recorrido

Cada clic adicional añade un nuevo tramo.

La herramienta va construyendo la instalación entre esos puntos y mostrando una previsualización del resultado.

### 8.3. Qué ve el usuario mientras dibuja

Mientras se dibuja, la herramienta no solo muestra la línea del recorrido, sino también el comportamiento previsto de la instalación:

- tramos principales;
- cambios de dirección;
- uniones;
- bifurcaciones.

`[[CAPTURA-03: ejemplo de instalación en fase de dibujo con previsualización activa]]`
![alt text](CAPTURA-03.png)

## 10. Cómo se generan automáticamente los accesorios

Una vez definido el recorrido, la herramienta interpreta la geometría y coloca automáticamente los accesorios necesarios.

### 9.1. Codos

Cuando el recorrido cambia de dirección, la herramienta genera el codo correspondiente.

### 9.2. Manguitos o uniones

Cuando dos tramos deben unirse de forma alineada, la herramienta genera la unión correspondiente.

### 9.3. Bifurcaciones o tes

Cuando un punto conecta tres direcciones, la herramienta genera la bifurcación adecuada.

### 9.4. Regla general de prioridad

Si un punto funciona como bifurcación, prevalece la bifurcación sobre otras soluciones.

Esto significa que el sistema no coloca varias piezas incompatibles en el mismo punto.

`[[CAPTURA-04: ejemplo comparativo de un codo, una unión y una bifurcación]]`
![alt text](CAPTURA-04A.png)![alt text](CAPTURA-04B.png)![alt text](CAPTURA-04C.png)

## 11. Cómo editar una instalación ya dibujada

Una vez creado el recorrido, el usuario puede modificarlo.

### 10.1. Seleccionar tramos

Se pueden seleccionar:

- tramos individuales;
- varios tramos a la vez;
- o zonas concretas del recorrido.

### 10.2. Borrar una sección

El botón de borrar elimina el tramo o la parte seleccionada.

Después del borrado, la herramienta vuelve a analizar la conexión entre los tramos que quedan y reajusta automáticamente las piezas necesarias.

### 10.3. Cambiar el diámetro

El botón de modificar diámetro actualiza el diámetro del tramo o de la selección activa.

Después del cambio, la instalación vuelve a reconstruir el resultado para adaptarlo al nuevo valor.

## 12. Layers

El usuario puede trabajar con los layers definidos por defecto o aplicar otros manualmente.

### 11.1. Layers por defecto

Cada instalación ya trae una configuración base de layers.

### 11.2. Aplicar layers manualmente

Desde la paleta, el usuario puede seleccionar un layer y aplicar ese layer a los elementos seleccionados.

Esto es útil cuando se necesita clasificar el modelo de una forma concreta antes de finalizar.

`[[CAPTURA-05: ejemplo del apartado de layers en la paleta y su aplicación sobre la instalación]]`
![alt text](CAPTURA-05.png)

## 13. Atributos

Además de la geometría, la instalación puede llevar información adicional en forma de atributos.

### 12.1. Atributos automáticos

Parte de los atributos se asignan automáticamente según el tipo de instalación, el elemento y la configuración elegida.

### 12.2. Atributos aplicados por el usuario

La paleta también permite aplicar atributos manualmente a una selección.

Esto es útil cuando el usuario necesita completar o corregir información antes de crear el resultado final.

### 12.3. Atributo padre

En determinadas instalaciones existe un atributo principal que sirve para organizar y relacionar elementos. Este dato es importante porque también puede influir en las copias o duplicados automáticos.

## 14. Qué revisar antes de finalizar

Antes de pulsar el botón de finalizar, se recomienda comprobar:

- que el recorrido es correcto;
- que los diámetros son los adecuados;
- que los layers necesarios están aplicados;
- que los atributos importantes están informados;
- y que los elementos definidos están bien colocados.

Si falta información, la herramienta puede mostrar un aviso antes de continuar.

`[[CAPTURA-06: mensaje de aviso previo a finalizar cuando falta información]]`
![alt text](CAPTURA-06.png)

## 15. Rotación y orientación

Algunos elementos admiten rotación y orientación.

Esto se aplica especialmente a:

- elementos definidos;
- macros;
- ciertos accesorios que requieren una posición concreta.

Cuando la paleta muestra campos de rotación u orientación, el usuario puede utilizarlos para ajustar la posición final del elemento.

`[[CAPTURA-07: ejemplo de orientación o rotación aplicada a un elemento]]`
![alt text](CAPTURA-07.png)

## 16. Macros

La herramienta permite colocar macros de librería dentro de la instalación.

### 15.1. Para qué sirven

Las macros permiten insertar objetos ya preparados, por ejemplo elementos de librería que deben colocarse en puntos concretos del recorrido.

### 15.2. Qué debe hacer el usuario

El flujo habitual es:

1. Elegir el tipo de macro.
2. Elegir el archivo correspondiente.
3. Elegir dónde se colocará.
4. Ajustar altura y rotación si es necesario.
5. Insertar la macro.

### 15.3. Dónde puede colocarse

La macro puede situarse:

- al inicio del recorrido;
- al final;
- o en un punto libre.

### 15.4. Altura de la macro

La altura puede definirse directamente o en relación con un local seleccionado, según el caso.

`[[CAPTURA-08: bloque de la paleta para insertar macros]]`
![alt text](CAPTURA-08.png)

`[[CAPTURA-09: ejemplo de macro previsualizada dentro de la instalación]]`
![alt text](CAPTURA-09.png)

## 17. Elementos definidos

Además del recorrido principal, la herramienta permite añadir elementos definidos propios de la instalación.

En Agua, por ejemplo, pueden existir elementos como válvulas, salidas o piezas concretas del sistema.

### 16.1. Cómo se insertan

Hay dos formas habituales:

- insertarlos sobre un punto del recorrido;
- o insertarlos como punto libre.

### 16.2. Qué debe hacer el usuario

El usuario debe:

1. elegir el tipo de elemento;
2. seleccionar el punto de inserción;
3. ajustar rotación o altura si hace falta;
4. confirmar la colocación.

`[[CAPTURA-10: bloque de la paleta para insertar Elementos Definidos]]`
![alt text](CAPTURA-10.png)

`[[CAPTURA-11: inserción de un elemento especial como punto libre]]`
![alt text](CAPTURA-11.png)

## 18. Puntos no definidos

Los puntos no definidos sirven para marcar la lógica del recorrido sin colocar todavía un elemento final.

Son útiles para describir:

- inicios;
- finales;
- intermedios;
- bifurcaciones;
- conexiones entre caminos.

### 17.1. Para qué sirven

Ayudan a organizar recorridos complejos y a definir la intención del trazado antes de convertirlo en una solución completa.

### 17.2. Puntos comunes

Si varios caminos coinciden en un punto o pasan muy cerca, la herramienta puede interpretar que existe una relación entre ellos.

Esto ayuda a construir una topología coherente.

`[[CAPTURA-12: ejemplo de puntos no definidos en distintos colores]]`
![alt text](CAPTURA-12.png)

`[[CAPTURA-13: ejemplo de punto común entre dos caminos]]`
![alt text](CAPTURA-13.png)

## 19. Soportes

La herramienta también permite trabajar con soportes.

### 18.1. Qué hace el usuario

El flujo habitual es:

1. configurar el soporte en la paleta;
2. pulsar el botón para insertarlo;
3. definir su posición;
4. revisar la previsualización;
5. acumularlo o crearlo.

### 18.2. Cuándo conviene colocarlos

Normalmente es más cómodo colocar los soportes cuando el recorrido principal ya está bastante definido.

`[[CAPTURA-14: bloque de soportes en la paleta y preview de un soporte]]`
![alt text](CAPTURA-14.png)

## 20. Cómo funcionan los duplicados o copias

Este punto es importante porque puede generar dudas.

### 19.1. Duplicados no deseados

La herramienta evita repetir elementos iguales cuando no corresponde.

Esto ayuda a que no aparezcan piezas duplicadas por error en el resultado final.

### 19.2. Copias intencionadas

En algunos casos, la instalación puede generar copias en otros archivos de dibujo según la información asociada al elemento.

Estas copias no son un error. Forman parte del funcionamiento previsto de la herramienta.

### 19.3. Qué debe entender el usuario

El usuario debe saber que:

- puede existir un elemento en el archivo principal;
- y puede existir una copia relacionada en otro archivo de dibujo.

Cuando la instalación se actualiza, esas copias también se actualizan para que no queden versiones antiguas.

`[[CAPTURA-15: ejemplo de un elemento original y su copia relacionada en otro archivo]]`
![alt text](CAPTURA-15.png)

## 21. Qué ocurre al pulsar el botón de finalizar

Cuando el usuario pulsa el botón de finalizar, la herramienta:

1. revisa la información disponible;
2. reconstruye los elementos necesarios;
3. aplica atributos y layers;
4. incorpora elementos definidos, macros o soportes;
5. crea el resultado definitivo;
6. y actualiza las copias relacionadas si las hubiera.

En ese momento la instalación pasa de estar en fase de preparación a quedar creada como resultado final en el documento.

## 22. Recomendaciones prácticas de uso

- Configurar primero el sistema antes de empezar a dibujar.
- No cambiar de criterio de diámetro continuamente durante el dibujo si no es necesario.
- Revisar la distribución antes de finalizar.
- Aplicar layers y atributos cuando el recorrido ya esté claro.
- Insertar macros y elementos definidos cuando la base principal esté estable.
- Revisar los avisos antes de aceptar la creación final.

## 23. Resumen final

La herramienta de instalaciones está pensada para que el usuario dibuje un recorrido, lo complete con la información necesaria y genere un resultado final coherente dentro de Allplan.

Aunque cada instalación tenga sus particularidades, el funcionamiento general es siempre el mismo:

- configurar;
- dibujar;
- revisar;
- completar;
- y finalizar.

Por eso, entendiendo bien el ejemplo de Agua, se entiende también el comportamiento general del resto de instalaciones.

## 24. Particularidades de cada instalación

Una vez entendido el funcionamiento general, es importante conocer las diferencias propias de cada instalación.

Estas diferencias no cambian la forma general de trabajar, pero sí modifican:

- los sistemas disponibles;
- los diámetros;
- los accesorios automáticos;
- los elementos definidos;
- y algunas reglas concretas de uso.

## 25. Instalación de Agua

En esta unidad solo se recogen las particularidades de Agua. El uso general de la herramienta ya se ha explicado en los apartados anteriores, por lo que aquí se detallan únicamente las reglas, avisos y casos propios de esta instalación.

### 25.1. Sistemas disponibles en Agua

En la instalación de Agua, el usuario puede trabajar con estos sistemas:

- Polietilè;
- Multicapa;
- Armaflex.

Cada uno de ellos pertenece a la instalación de Agua, pero representa una solución distinta dentro del modelo.

`[[CAPTURA-AGUA-01: desplegable con los sistemas disponibles en Agua]]`
![alt text](CAPTURA-AGUA-01.png)

### 25.2. Distribuciones en Agua

En Agua el usuario puede trabajar con estas distribuciones:

- EN;
- TD;
- IS.

La distribución condiciona el comportamiento del sistema, los layers aplicados y el catálogo de piezas que puede resolverse automáticamente.

Cuando se selecciona la distribución `EN`, la paleta muestra además el campo `Cara (EN)`, que permite indicar si el caso corresponde a `Cara X` o `Cara Y`.

#### 25.2.1. Combinaciones que requieren atención

- Conviene elegir la distribución antes de empezar a dibujar.
- Si la distribución se cambia después, es necesario revisar de nuevo codos, uniones, bifurcaciones y layers.
- No todos los sistemas de Agua están disponibles en todas las distribuciones.

En la configuración actual:

- `Multicapa` no está disponible en `IS`.
- `Armaflex` no está disponible en `IS`.

Si el usuario intenta trabajar con alguna de esas combinaciones, la herramienta muestra un aviso indicando que ese tipo de tubo no existe o no está disponible para la distribución `IS`, y pide volver a `Modo creación`, cambiar la distribución a `TD` y regresar a `Modo configuración`.

`[[CAPTURA-AGUA-02: campo de distribución en Agua con la opción EN y el campo Cara (EN) visible]]`
![alt text](CAPTURA-AGUA-02.png)

`[[CAPTURA-AGUA-03: aviso mostrado al intentar usar Multicapa o Armaflex en distribución IS]]`
![alt text](CAPTURA-AGUA-03.png)

### 25.3. Diámetros y cambios de diámetro en Agua

En la instalación de Agua, los diámetros más habituales en la configuración actual son:

- 20 mm
- 25 mm

El diámetro afecta a:

- el tamaño del tubo;
- los accesorios compatibles;
- la geometría final;
- y parte de la información asociada al elemento.

#### 25.3.1. Qué ocurre al cambiar el diámetro de un tramo

Cuando se modifica el diámetro de un único tramo, la herramienta muestra una ventana de confirmación con:

- la ruta;
- el segmento;
- el diámetro anterior;
- y el nuevo diámetro.

El usuario debe confirmar el cambio antes de que la geometría se regenere.

`[[CAPTURA-AGUA-04: confirmación de cambio de diámetro sobre un único tramo]]`
![alt text](CAPTURA-AGUA-04.png)

#### 25.3.2. Qué ocurre al cambiar el diámetro de varios tramos

Si hay varios tramos seleccionados, la ventana de confirmación informa de:

- cuántos segmentos se van a modificar;
- qué diámetro o diámetros tenían antes;
- y qué nuevo diámetro se va a aplicar.

Después de aceptar, la instalación reconstruye el resultado con el nuevo valor.

`[[CAPTURA-AGUA-05: confirmación de cambio de diámetro sobre varios tramos seleccionados]]`
![alt text](CAPTURA-AGUA-05.png)

#### 25.3.3. Qué ocurre si el cambio afecta a un codo

Si el cambio de diámetro afecta a un giro resuelto con codo, no aparece un mensaje especial para el codo.

Lo que se muestra es el mensaje general de cambio de diámetro y, al aceptarlo, la herramienta recalcula el encuentro para regenerar el codo con la nueva condición.

`[[CAPTURA-AGUA-06: ejemplo de codo recalculado después de modificar el diámetro del tramo]]`
![alt text](CAPTURA-AGUA-06.png)

#### 25.3.4. Qué ocurre si hay dos tramos consecutivos en la misma dirección con distinto diámetro

Si dos segmentos consecutivos siguen en la misma dirección pero cambian de diámetro, la instalación no coloca un manguito normal, sino un `manguito reductor`.

Este caso es importante porque es la forma habitual de resolver una transición recta entre dos diámetros distintos.

Conviene revisarlo siempre en pantalla para comprobar que la reducción se ha generado justo en el punto esperado.

`[[CAPTURA-AGUA-07: ejemplo de manguito reductor entre dos tramos consecutivos en la misma dirección]]`
![alt text](CAPTURA-AGUA-07.png)

### 25.4. Accesorios automáticos en Agua

En Agua los accesorios automáticos dependen de la geometría del recorrido y de los diámetros de los tramos que se encuentran.

#### 25.4.1. Codos

En Agua la resolución automática de giros se hace con `codos de 90 grados`.

Esto significa que no debe esperarse un codo automático de `45 grados` dentro de esta instalación.

`[[CAPTURA-AGUA-08: ejemplo de codo de 90 grados generado automáticamente en Agua]]`
![alt text](CAPTURA-AGUA-08.png)

#### 25.4.2. Manguitos

Cuando dos tramos consecutivos están alineados y mantienen el mismo diámetro, la herramienta coloca un manguito o unión recta.

#### 25.4.3. Manguitos reductores

Cuando esos dos tramos alineados tienen distinto diámetro, la unión se resuelve mediante un manguito reductor.

#### 25.4.4. Tes o bifurcaciones

Cuando en un mismo punto confluyen tres direcciones, la instalación intenta resolver el encuentro mediante una `Te`.

En Agua conviene distinguir dos grandes familias:

- `Te iguales`, cuando las tres bocas trabajan con el mismo diámetro.
- `Te reducidas`, cuando una de las bocas trabaja con un diámetro distinto.

En la configuración actual, los casos más representativos son:

- `Te Ø20`;
- `Te Ø25`;
- `Te Ø25-20-25`;
- `Te Ø25-20-20`;
- `Te Ø25-25-20`.

Si el nodo se resuelve como `Te`, en ese mismo punto no se coloca además un codo ni un manguito.

`[[CAPTURA-AGUA-09: ejemplo comparativo de los distintos tipos de Te utilizados en Agua]]`
![alt text](CAPTURA-AGUA-09.png)

#### 25.4.5. Qué ocurre si no existe una Te compatible

Si la combinación de diámetros de entrada, salida y rama no tiene una `Te` disponible, la herramienta muestra un aviso indicando que no existe una `TE` para la combinación de diámetros seleccionada y pide modificar los diámetros de los segmentos para que coincidan con un tipo disponible.

`[[CAPTURA-AGUA-10: aviso mostrado cuando no existe una Te para la combinación de diámetros seleccionada]]`
![alt text](CAPTURA-AGUA-10.png)

### 25.5. Longitudes mínimas y máximas de tubo en Agua

Además del sistema, la distribución y el diámetro, en Agua también hay condiciones de longitud que el usuario debe conocer.

#### 25.5.1. Longitud mínima

La longitud mínima de tramo en la configuración actual es `350 mm`.

Si el usuario dibuja un segmento más corto:

- la herramienta muestra el tipo de instalación;
- indica la longitud mínima requerida;
- indica la longitud real del tramo dibujado;
- y pregunta si se desea ignorar la restricción o cancelar para recolocar el punto.

Esto permite decidir en el momento si se mantiene ese tramo corto o si se corrige antes de seguir dibujando.

`[[CAPTURA-AGUA-11: aviso de longitud mínima no cumplida al dibujar un tramo demasiado corto]]`
![alt text](CAPTURA-AGUA-11.png)

#### 25.5.2. Longitud máxima

La longitud máxima de referencia en Agua es `5,00 m`.

Si un tramo supera esa longitud, la herramienta no muestra un aviso bloqueante, sino que divide automáticamente ese tramo en subtramos más cortos para poder resolver la instalación dentro del límite permitido.

Por eso, cuando se trabaja con recorridos largos, conviene revisar el resultado para comprobar dónde se han producido los cortes y cómo han quedado las uniones generadas.

`[[CAPTURA-AGUA-12: ejemplo de tramo largo dividido automáticamente al superar la longitud máxima]]`
![alt text](CAPTURA-AGUA-12.png)

### 25.6. Elementos definidos propios de Agua

Además del trazado automático, Agua permite insertar elementos definidos propios del sistema.

En la configuración actual, Agua trabaja con elementos definidos como:

- Colze Base;
- Clau de Pas;
- Taps;
- T sortida.

Estos elementos se utilizan para completar la instalación con piezas concretas del sistema una vez que el recorrido principal ya está claro.

Además, algunos de estos elementos pueden mostrar un aviso si se intentan colocar en una distribución no admitida, especialmente en `IS`.

`[[CAPTURA-AGUA-13: paleta de Elementos Definidos en Agua con los tipos disponibles]]`
![alt text](CAPTURA-AGUA-13.png)

### 25.7. Puntos a revisar con especial atención en Agua

Antes de finalizar una instalación de Agua conviene revisar especialmente:

- que el sistema seleccionado sea realmente `Polietilè`, `Multicapa` o `Armaflex`, según el caso;
- que la distribución sea la correcta y, si procede, que `Cara (EN)` también esté bien definida;
- que después de un cambio de diámetro se hayan regenerado correctamente codos, manguitos reductores y Tes;
- que los giros del recorrido respondan a la lógica de `90 grados`;
- que los avisos de longitud mínima se hayan resuelto conscientemente;
- y que los recorridos largos no hayan generado divisiones automáticas en puntos no deseados.

## 26. Próximas unidades por instalación

Este mismo esquema puede repetirse dentro del manual para el resto de instalaciones, por ejemplo:

- Saneamiento;
- Ventilación;
- Electricidad.

La idea es que cada una tenga su propia unidad específica dentro del mismo manual, manteniendo una estructura común para que la consulta sea sencilla.
