# Instalación: Saneamiento

## 1. Descripción general
- Esta instalación sirve para dibujar y editar redes de evacuación.
- Está pensada para trabajar con trazados de saneamiento con accesorios automáticos.
- Lo que la diferencia de otras instalaciones es la combinación de sistemas y diámetros propios de saneamiento, con cambios automáticos de uniones y piezas en cada tramo.

## 2. Sistemas disponibles
- Sistemas visibles en la paleta:
  - **Pluvial**
  - **Fecal**
- Diferencias principales:
  - **Pluvial** trabaja con una configuración más limitada de diámetro.
  - **Fecal** permite más opciones de diámetro.
- Al cambiar de sistema, la herramienta adapta automáticamente los elementos que se colocan en el trazado.

## 3. Distribuciones disponibles
- En esta instalación, la distribución no es un ajuste práctico para el flujo de usuario.
- Para el manual: **no aplica**.

## 4. Diámetros
- Diámetros disponibles por sistema:
  - **Pluvial:** 110
  - **Fecal:** 25, 40 y 110
- Reglas especiales:
  - El diámetro disponible depende del sistema seleccionado.
- Al cambiar el diámetro de un tramo:
  - Se actualiza el tramo.
  - Se recalculan automáticamente las uniones y accesorios de la zona.
- Cambio de diámetro entre dos tramos consecutivos en línea recta:
  - Se coloca automáticamente una unión de transición.
- Cambio de diámetro en un codo:
  - Se ajusta el codo al diámetro correspondiente y se recalcula la unión.
- Cambio de diámetro en una bifurcación o Te:
  - Se intenta colocar la pieza compatible.
  - Si no existe combinación válida, aparece aviso.
- Elementos automáticos en estos casos:
  - Reducciones y uniones de transición.
  - Bifurcaciones compatibles con la combinación detectada.
- Mensaje detectado:
  - **“No existe una TE para la combinación de diámetros seleccionada.\n\nCombinación detectada: …\n\nModifique los diámetros de los segmentos para que coincidan con los tipos de TE disponibles.”**

## 5. Accesorios automáticos
- Accesorios generados automáticamente:
  - Codos.
  - Bifurcaciones tipo Y.
  - Uniones.
  - Reducciones.
- Tipos de codos disponibles:
  - 45°
  - 90°
- Tipos de tes o bifurcaciones disponibles:
  - Bifurcaciones para las combinaciones habituales de esta instalación.
  - Bifurcación de transición en casos concretos.
- Manguitos, reducciones y otras uniones:
  - Se crean de forma automática en cambios de diámetro o encuentros en línea.
- Limitaciones o incompatibilidades:
  - No todas las combinaciones de diámetros en bifurcación están disponibles.
  - Cuando no hay pieza compatible, se muestra aviso y el usuario debe ajustar diámetros.

## 6. Reglas geométricas y validaciones
- Longitud mínima de tubo: **350 mm**.
- Longitud máxima de tubo: **pendiente de confirmar**.
- Si no se cumple la longitud mínima:
  - El tramo puede no resolverse correctamente.
  - Mensaje exacto: **pendiente de confirmar**.
- Si se supera la longitud máxima:
  - **pendiente de confirmar**.
- Otras reglas geométricas importantes:
  - La herramienta recorta automáticamente extremos de tramo para encajar accesorios.
  - El sentido del trazado influye en el resultado de algunas piezas.

## 7. Elementos definidos propios de esta instalación
- Elemento definido visible:
  - **Caixa Connexions 200**
- Para qué sirve:
  - Para insertar un elemento de conexión en un punto de la instalación.
- Cuándo conviene usarlo:
  - En puntos de inicio, final o en puntos intermedios donde se necesite registro o conexión.
- Tipos de punto admitidos:
  - **Inicio**
  - **Final**
  - **Intermedio ordenado**
  - **Intermedio libre**
    - En paleta se muestra como **Intermedio o libre**.
- Restricciones o mensajes en punto no válido:
  - **pendiente de confirmar**.

## 8. Macros
- Esta instalación incluye uso específico de macros en su propia página de paleta.
- Tipos de macro habituales:
  - Macro de librería.
- Particularidades de uso:
  - Selección de punto de inserción.
  - Posición en cota.
  - Ajuste por altura respecto al piso cuando procede.
- Detalles de orientación exacta: **pendiente de confirmar**.

## 9. Soportes
- Esta instalación tiene página específica de soportes.
- Tipos de soporte más habituales:
  - **Zeta** (visible como valor por defecto).
  - Resto de tipos: **pendiente de confirmar**.
- Superficies habituales:
  - **Liso**
  - **Perforado**
- Criterios específicos de uso:
  - Definición de cotas.
  - Ángulo de inclinación.
  - Inserción, creación y edición desde la misma paleta.

## 10. Layers y atributos específicos
- Layers importantes:
  - **IS CON SANE FAB**
  - **IS CON SANE OBR**
  - **KN X AIGUA**
  - **KN Y AIGUA**
  - **KN AIGUA**
- Atributos especialmente relevantes:
  - Valor de atributo aplicado por selección.
  - Atributos de soporte en la página de soportes.
- Datos a revisar antes de finalizar:
  - Sistema activo.
  - Diámetro activo.
  - Layer aplicado en tramos y accesorios.
  - Atributos aplicados en elementos seleccionados.
- Atributos padre o campos críticos:
  - **pendiente de confirmar**.

## 11. Copias, duplicados o comportamiento especial
- Esta instalación puede generar elementos superpuestos en algunos casos.
- Ese comportamiento puede parecer “duplicado”, pero forma parte de la definición de ciertos elementos.
- Cómo entenderlo:
  - No es un error de copia entre archivos.
  - Es una representación prevista para capas, atributos o materiales.

## 12. Mensajes y avisos
- **“No hay instalación guardada para invertir.”**
  - Cuándo aparece: al intentar invertir sin trazado guardado.
  - Qué hacer: guardar o finalizar trazado y volver a intentar.
- **“Instalación invertida: ahora va de final a inicio.”**
  - Cuándo aparece: al invertir correctamente el sentido.
  - Qué hacer: continuar edición con el nuevo sentido.
- **“No se pudo invertir la instalación:\n…”**
  - Cuándo aparece: si falla la inversión.
  - Qué hacer: revisar trazado y repetir la acción.
- **“No existe una TE para la combinación de diámetros seleccionada…”**
  - Cuándo aparece: cuando no hay bifurcación compatible con los diámetros detectados.
  - Qué hacer: modificar diámetros hasta usar una combinación válida.
- **“caval sin sentido sera creado”**
  - Cuándo aparece: en casos concretos de orientación de bifurcación.
  - Qué hacer: revisar sentido del trazado y resultado antes de finalizar.

## 13. Casos prácticos que conviene documentar
- Cambio de sistema de **Pluvial** a **Fecal** manteniendo trazado.
- Cambio de diámetro en línea recta con unión automática.
- Codo 45° y codo 90° en cada diámetro principal.
- Bifurcación válida y bifurcación no válida (con aviso).
- Reducción entre diámetros diferentes.
- Inserción de **Caixa Connexions 200** en punto inicial, final e intermedio.
- Caso de longitud mínima no cumplida.
- Inserción y edición de soporte.
- Inversión de sentido con **Invertir caval**.

## 14. Capturas necesarias
- [CAPTURA-01: paleta de Saneamiento con sistemas **Pluvial** y **Fecal**]
- [CAPTURA-02: selector de diámetro en sistema **Fecal**]
- [CAPTURA-03: acción **Modificar diámetro** sobre un tramo]
- [CAPTURA-04: transición de diámetro en línea recta]
- [CAPTURA-05: codo 45° y codo 90° en un mismo ejemplo]
- [CAPTURA-06: bifurcación válida]
- [CAPTURA-07: aviso de bifurcación no compatible]
- [CAPTURA-08: uso de **Caixa Connexions 200**]
- [CAPTURA-09: página de macros con selección de punto]
- [CAPTURA-10: página de soportes con inserción]
- [CAPTURA-11: aplicación de layer]
- [CAPTURA-12: aplicación de atributo]
- [CAPTURA-13: botón **Invertir caval** con mensaje de confirmación]

## 15. Observaciones finales
- Conviene explicar en el manual que el sentido del trazado puede afectar al resultado de piezas automáticas.
- También conviene advertir que en algunos elementos puede verse superposición intencional.
- Puntos a validar en entorno real antes de cerrar versión final del manual:
  - mensaje exacto de longitud mínima;
  - límite máximo de longitud;
  - listado completo de tipos de soporte.
