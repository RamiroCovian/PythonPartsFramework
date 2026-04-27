# Anexo Específico de la Instalación de Agua

## 1. Finalidad de este anexo

Este anexo complementa el manual global y recoge únicamente las particularidades de la instalación de Agua.

El objetivo es que el usuario sepa qué elementos, sistemas y reglas concretas debe tener en cuenta cuando trabaja con Agua, sin mezclar esta información con el funcionamiento común del resto de instalaciones.

## 2. Qué se documenta aquí

En este anexo se explican:

- los sistemas disponibles dentro de Agua;
- las distribuciones utilizadas;
- los diámetros habituales;
- los accesorios automáticos;
- los elementos definidos propios de Agua;
- y las limitaciones o avisos que el usuario debe conocer.

## 3. Sistemas disponibles en Agua

En la instalación de Agua, el usuario puede trabajar con estos sistemas:

- Polietilè;
- Multicapa;
- Armaflex.

Cada uno de ellos pertenece a la misma instalación general, pero representa una solución distinta dentro del modelo.

`[[CAPTURA-AGUA-01: desplegable con los sistemas disponibles en Agua]]`

## 4. Distribuciones en Agua

En Agua el usuario trabaja principalmente con estas distribuciones:

- TD;
- IS.

La distribución condiciona cómo se comporta la instalación y qué configuración se aplica al resultado final.

### 4.1. Qué debe tener en cuenta el usuario

- La distribución debe elegirse antes de dibujar.
- Si se cambia después, conviene revisar el resultado.
- No todos los sistemas se comportan igual en todas las distribuciones.

### 4.2. Caso especial

En la configuración actual, si el usuario intenta trabajar con combinaciones no admitidas en ciertos sistemas, la herramienta muestra un aviso para corregir la configuración.

Conviene revisar especialmente los casos de Multicapa y Armaflex cuando la distribución elegida no sea la adecuada.

`[[CAPTURA-AGUA-02: campo de distribución y ejemplo de aviso por combinación no admitida]]`

## 5. Diámetros en Agua

En la instalación de Agua, los diámetros más habituales en la configuración actual son:

- 20;
- 25.

El diámetro afecta a:

- el tamaño del tubo;
- los accesorios compatibles;
- la geometría final;
- y parte de la información asociada al elemento.

### 5.1. Recomendación

Si se modifica el diámetro después de dibujar, conviene revisar:

- uniones;
- codos;
- bifurcaciones;
- y el resultado final en pantalla.

## 6. Accesorios automáticos en Agua

Agua genera automáticamente distintos accesorios en función del recorrido.

### 6.1. Codos

En Agua, el usuario debe tener presente que el sistema trabaja principalmente con codos de 90 grados.

Esto significa que el recorrido debe plantearse teniendo en cuenta esa lógica de giro.

### 6.2. Uniones o manguitos

Se generan cuando dos tramos deben unirse en línea.

### 6.3. Bifurcaciones

Se generan cuando el recorrido lo requiere y la geometría del trazado lo justifica.

`[[CAPTURA-AGUA-03: ejemplo real de un codo de 90 grados generado en Agua]]`

## 7. Qué diferencia a Agua de otras instalaciones

Una diferencia importante respecto a otras instalaciones es que Agua debe explicarse con sus propias reglas de uso.

Por ejemplo:

- en Agua hay sistemas como Polietilè, Multicapa y Armaflex;
- en otras instalaciones puede haber familias completamente distintas;
- en Agua el usuario debe pensar en codos de 90 grados;
- mientras que en otras instalaciones, como Saneamiento, puede haber además codos de 45 grados.

Por eso no conviene meter toda esta información específica dentro del manual global. Es mejor explicarla en anexos separados.

## 8. Elementos definidos propios de Agua

Además del recorrido principal, Agua permite insertar elementos definidos propios del sistema.

En la configuración actual, Agua trabaja con elementos definidos como:

- Colze Base;
- Clau de Pas;
- Taps;
- T sortida.

### 8.1. Qué debe entender el usuario

Estos elementos no forman parte del trazado automático básico, sino que se colocan cuando el usuario necesita completar la instalación con piezas específicas.

`[[CAPTURA-AGUA-04: paleta de Elementos Definidos en Agua]]`

## 9. Macros en Agua

Agua también permite insertar macros como complemento del recorrido.

Se recomienda:

- dibujar primero el recorrido principal;
- revisar la geometría;
- y después insertar las macros necesarias.

## 10. Layers y atributos en Agua

Agua utiliza sus propios layers y parte de su propia lógica de atributos.

### 10.1. Qué debe saber el usuario

- No todos los sistemas aplican exactamente la misma información.
- La distribución influye en el comportamiento del resultado.
- Algunos elementos pueden conservar configuraciones específicas del propio modelo.

Lo importante es comprobar siempre:

- que el layer aplicado es el correcto;
- que la distribución es la adecuada;
- y que la instalación final se corresponde con el sistema seleccionado.

## 11. Puntos a revisar con especial atención

En Agua conviene revisar especialmente estos puntos:

### 11.1. Sistema seleccionado

Comprobar siempre si se está trabajando en Polietilè, Multicapa o Armaflex.

### 11.2. Distribución

Comprobar si el trabajo corresponde realmente a TD o IS.

### 11.3. Giros del recorrido

Tener presente que la lógica habitual de Agua se apoya en giros de 90 grados.

### 11.4. Resultado después de un cambio

Si se cambia diámetro, sistema o distribución, conviene revisar el recorrido antes de finalizar.

## 12. Cómo replicar esta documentación en otras instalaciones

La mejor forma de documentar el conjunto completo no es ampliar indefinidamente el manual global, sino crear un anexo específico para cada instalación.

La estructura recomendada para cada instalación es esta:

1. Sistemas disponibles.
2. Distribuciones disponibles.
3. Diámetros.
4. Accesorios automáticos.
5. Elementos definidos propios.
6. Macros, si aplica.
7. Layers y atributos a vigilar.
8. Limitaciones o avisos especiales.
9. Casos prácticos o ejemplos visuales.

## 13. Resumen final

El manual global ya explica correctamente el funcionamiento común.

Lo que faltaba era separar las particularidades de cada instalación en anexos independientes. Este documento resuelve esa necesidad para Agua y puede usarse como modelo para crear otros anexos, por ejemplo:

- anexo de Saneamiento;
- anexo de Ventilación;
- anexo de Electricidad.
