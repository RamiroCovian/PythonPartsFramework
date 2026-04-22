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

## 3. Qué partes son comunes en todas las instalaciones

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

## 4. Vista general del trabajo con una instalación

El trabajo habitual con una instalación se basa en tres ideas:

- dibujar un recorrido;
- enriquecer ese recorrido con información;
- y generar el resultado final.

En la práctica, esto significa que primero se crea el trazado principal y después se añaden o ajustan el resto de elementos necesarios.

`[[CAPTURA-01: paleta principal completa de la instalación con sus apartados visibles]]`
![alt text](CAPTURA-01.png)

## 5. Flujo de trabajo recomendado

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

## 6. Modos principales de trabajo

La herramienta suele trabajar con tres modos principales.

### 6.1. Modo creación

Es el modo que se utiliza para dibujar un recorrido nuevo.

En este modo el usuario va definiendo puntos y la instalación crea el trazado entre ellos.

### 6.2. Modo edición

Es el modo que se utiliza para corregir o modificar un recorrido ya dibujado.

En este modo se pueden seleccionar tramos, borrar partes, cambiar diámetros o ajustar la geometría.

### 6.3. Modo extender

Es el modo que se utiliza para continuar un recorrido ya existente sin empezar desde cero.

## 7. Qué debe configurar el usuario antes de dibujar

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

## 8. Cómo dibujar una instalación

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

## 9. Cómo se generan automáticamente los accesorios

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

## 10. Cómo editar una instalación ya dibujada

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

## 11. Layers

El usuario puede trabajar con los layers definidos por defecto o aplicar otros manualmente.

### 11.1. Layers por defecto

Cada instalación ya trae una configuración base de layers.

### 11.2. Aplicar layers manualmente

Desde la paleta, el usuario puede seleccionar un layer y aplicar ese layer a los elementos seleccionados.

Esto es útil cuando se necesita clasificar el modelo de una forma concreta antes de finalizar.

`[[CAPTURA-05: ejemplo del apartado de layers en la paleta y su aplicación sobre la instalación]]`
![alt text](CAPTURA-05.png)

## 12. Atributos

Además de la geometría, la instalación puede llevar información adicional en forma de atributos.

### 12.1. Atributos automáticos

Parte de los atributos se asignan automáticamente según el tipo de instalación, el elemento y la configuración elegida.

### 12.2. Atributos aplicados por el usuario

La paleta también permite aplicar atributos manualmente a una selección.

Esto es útil cuando el usuario necesita completar o corregir información antes de crear el resultado final.

### 12.3. Atributo padre

En determinadas instalaciones existe un atributo principal que sirve para organizar y relacionar elementos. Este dato es importante porque también puede influir en las copias o duplicados automáticos.

## 13. Qué revisar antes de finalizar

Antes de pulsar el botón de finalizar, se recomienda comprobar:

- que el recorrido es correcto;
- que los diámetros son los adecuados;
- que los layers necesarios están aplicados;
- que los atributos importantes están informados;
- y que los elementos definidos están bien colocados.

Si falta información, la herramienta puede mostrar un aviso antes de continuar.

`[[CAPTURA-06: mensaje de aviso previo a finalizar cuando falta información]]`
![alt text](CAPTURA-06.png)

## 14. Rotación y orientación

Algunos elementos admiten rotación y orientación.

Esto se aplica especialmente a:

- elementos definidos;
- macros;
- ciertos accesorios que requieren una posición concreta.

Cuando la paleta muestra campos de rotación u orientación, el usuario puede utilizarlos para ajustar la posición final del elemento.

`[[CAPTURA-07: ejemplo de orientación o rotación aplicada a un elemento]]`
![alt text](CAPTURA-07.png)

## 15. Macros

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

## 16. Elementos definidos

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

## 17. Puntos no definidos

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

## 18. Soportes

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

## 19. Cómo funcionan los duplicados o copias

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

## 20. Qué ocurre al pulsar el botón de finalizar

Cuando el usuario pulsa el botón de finalizar, la herramienta:

1. revisa la información disponible;
2. reconstruye los elementos necesarios;
3. aplica atributos y layers;
4. incorpora elementos definidos, macros o soportes;
5. crea el resultado definitivo;
6. y actualiza las copias relacionadas si las hubiera.

En ese momento la instalación pasa de estar en fase de preparación a quedar creada como resultado final en el documento.

## 21. Recomendaciones prácticas de uso

- Configurar primero el sistema antes de empezar a dibujar.
- No cambiar de criterio de diámetro continuamente durante el dibujo si no es necesario.
- Revisar la distribución antes de finalizar.
- Aplicar layers y atributos cuando el recorrido ya esté claro.
- Insertar macros y elementos definidos cuando la base principal esté estable.
- Revisar los avisos antes de aceptar la creación final.

## 22. Resumen final

La herramienta de instalaciones está pensada para que el usuario dibuje un recorrido, lo complete con la información necesaria y genere un resultado final coherente dentro de Allplan.

Aunque cada instalación tenga sus particularidades, el funcionamiento general es siempre el mismo:

- configurar;
- dibujar;
- revisar;
- completar;
- y finalizar.

Por eso, entendiendo bien el ejemplo de Agua, se entiende también el comportamiento general del resto de instalaciones.
