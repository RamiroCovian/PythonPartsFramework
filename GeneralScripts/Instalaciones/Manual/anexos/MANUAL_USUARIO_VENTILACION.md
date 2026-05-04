# Instalación: Ventilación

## 1. Descripción general
- Esta instalación sirve para dibujar y editar redes de ventilación dentro de Allplan.
- Está pensada para trabajar con conductos y accesorios automáticos a partir de un recorrido polilineal.
- Lo que la diferencia de otras instalaciones es la combinación de tipos de conducto, diámetros, ángulos permitidos y accesorios específicos de ventilación.

## 2. Sistemas disponibles
- Sistemas visibles en la configuración actual:
  - **Conducto Impulsion**
  - **Conducto Extraccion**
  - **Conducto Aislado**
  - **Conducto Recuperador**
- Diferencias principales:
  - **Conducto Impulsion** y **Conducto Extraccion** comparten geometría base, pero usan color y artículo distintos.
  - **Conducto Aislado** trabaja con conducto dinámico y reducción como conexión característica.
  - **Conducto Recuperador** trabaja con otra lógica de generación y solo admite giros de 90 grados.
- Al cambiar de sistema, la herramienta adapta automáticamente el comportamiento del trazado, el diámetro base y los accesorios disponibles.

## 3. Distribuciones disponibles
- En la paleta existe el campo **Tipo de Distribucion**, pero en la configuración registrada de Ventilación no aparece una distribución funcional específica como sí ocurre en Agua.
- Para el manual: **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** si este campo debe usarse o si permanece sin aplicación práctica para el usuario.

## 4. Diámetros
- Diámetros confirmados por sistema:
  - **Conducto Impulsion:** 75 mm
  - **Conducto Extraccion:** 75 mm
  - **Conducto Aislado:** 150 mm y 160 mm
  - **Conducto Recuperador:** 160 mm
- Reglas especiales:
  - El diámetro disponible depende del sistema seleccionado.
  - El botón **Modificar diámetro** recalcula el tramo y las uniones afectadas.
- Cambio de diámetro entre dos tramos consecutivos en línea recta:
  - En conductos compatibles, la herramienta genera automáticamente la transición o la unión correspondiente.
- Cambio de diámetro en sistemas con accesorios:
  - En **Conducto Aislado**, la conexión característica registrada es la **reducción**.
  - En el resto de sistemas, conviene revisar en pantalla cómo se rehace la unión después del cambio.

## 5. Accesorios automáticos
- Accesorios generados automáticamente según el sistema:
  - **Conducto Impulsion / Extraccion:** manguito y difusor.
  - **Conducto Aislado:** reducción.
  - **Conducto Recuperador:** conexión y codo de 90 grados.
- Tipos de accesorios confirmados en el registro:
  - **Manguito**
  - **Difusor**
  - **Conexion**
  - **Codo 90**
- Comportamiento importante:
  - En sistemas normales, el manguito actúa como frontera de grupo para numeración y agrupación.
  - En recuperador, el flujo de creación trabaja con un conjunto de piezas encadenadas: conducto + conexión + codo.
- Limitaciones o incompatibilidades:
  - **Conducto Recuperador** no sigue la misma lógica de ángulos que el resto.
  - **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** si existen avisos específicos cuando el usuario intenta forzar una combinación no compatible.

## 6. Reglas geométricas y validaciones
- Ángulos generales soportados en la instalación:
  - **45 grados**
  - **90 grados**
- Reglas por sistema:
  - **Conducto Impulsion / Extraccion:** 45 y 90 grados.
  - **Conducto Aislado:** 45 y 90 grados.
  - **Conducto Recuperador:** solo 90 grados.
- Longitud mínima por sistema:
  - **Conducto Impulsion / Extraccion:** 300 mm
  - **Conducto Aislado:** 300 mm
  - **Conducto Recuperador:** 350 mm
- Reglas geométricas relevantes:
  - El sistema recalcula recortes para encajar conexiones y codos.
  - La orientación 3D del tramo afecta al resultado de conductos, codos, conexiones y difusores.
  - Existen casos específicos para segmentos verticales y para cambio de plano.
- **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** el mensaje exacto mostrado cuando no se cumple la longitud mínima.

## 7. Elementos definidos propios de esta instalación
- Aquí hay una inconsistencia que conviene documentar con claridad:
  - El registro de Ventilación declara como elementos 3D propios: **Manguito**, **Difusor**, **Conducto recuperador**, **Conexion** y **Codo 90**.
  - Pero la página de **Elemento** del archivo `ventilacion_polyline.pyp` muestra actualmente solo **Caixa Connexions 200**.
- Esto indica una probable herencia o copia de configuración desde otra instalación.
- Para el manual:
  - **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** qué elemento definido debe ver realmente el usuario en Ventilación.
  - **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** si la paleta de Elemento en Ventilación debe corregirse antes de cerrar el manual.

## 8. Macros
- La instalación incluye la misma lógica general de macros que otras instalaciones:
  - selección de punto;
  - selección de macro SmartSymbol;
  - cota manual o relativa a local;
  - confirmación de inserción.
- Particularidades visibles en paleta:
  - selección de punto;
  - selección de local;
  - cota Z o altura sobre piso;
  - selección de macro.
- **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** si en Ventilación hay un uso específico de macros distinto del comportamiento compartido.

## 9. Soportes
- La instalación dispone de página específica de soportes.
- Campos confirmados en paleta:
  - **Tipo de soporte**
  - **Subtipo instalación**
  - **Superficie**
  - **Cota A**
  - **Cota B**
  - **Ángulo de inclinación**
  - modos de edición de soportes;
  - atributo de soporte.
- Datos confirmados por ejemplo de configuración:
  - existe al menos un caso de soporte **Omega**;
  - el subtipo asociado puede ser **Ventilacion**;
  - la superficie puede ser **Perforado**.
- Reglas prácticas:
  - conviene definir tipo, superficie y cotas antes de insertar;
  - los soportes pueden acumularse y crearse después;
  - el modo **Edición Mover** permite recolocar soportes ya acumulados o seleccionados.
- **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** el listado completo de tipos de soporte realmente habilitados en Ventilación.

## 10. Layers y atributos específicos
- Layers base confirmados en el registro:
  - **IS_CON_VENT_FAB**
  - **IS_CON_VENT_FAB_SOB1**
  - **IS_CON_VENT_OBRA**
  - **IS_CON_VENT_EIX**
  - **IS_NOM_CONDUCTE_VENTILACIO** como layer de etiqueta/cuboid label
- Atributos detectados en scripts de Ventilación:
  - **pmp_pare**
  - **6_CC_IS**
  - **pmp_altura**
  - **pmp_amplada**
  - **pmp_area**
  - **pmp_diametre**
  - **pmp_longitud**
  - **pmp_nom**
  - **pmp_seccio**
  - y otros atributos `pmp_*` de clasificación y propiedades físicas.
- Comportamientos relevantes:
  - el sistema usa atributos por defecto definidos en cada pieza;
  - el usuario puede aplicar layers y atributos manualmente desde la paleta;
  - los conductos usan numeración y atributos base que luego pueden completarse con la lógica general de la instalación.
- Casos concretos observados:
  - `conducto_normal` usa `6_CC_IS = IS08`;
  - `conducto_recuperador` usa `6_CC_IS = IS`;
  - varias piezas inicializan `pmp_pare` vacío.

## 11. Copias, duplicados o comportamiento especial
- Ventilación usa la misma lógica general de copias y agrupación que el resto de instalaciones basadas en `PolyLib`.
- Comportamientos relevantes observados:
  - los elementos pueden agruparse por tramos y por fronteras de manguito;
  - la numeración cambia cuando aparece un nuevo grupo;
  - la serialización del estado permite restaurar la instalación en edición.
- Qué debe entender el usuario:
  - un manguito no es solo un accesorio visual; también afecta a la agrupación lógica de la instalación;
  - si el proyecto usa atributo padre y copia a otros archivos, esa lógica sigue siendo la global del sistema.
- **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** si Ventilación está usando en producción copias automáticas a otros archivos de dibujo y en qué casos.

## 12. Mensajes y avisos
- A nivel de código se detectan mensajes técnicos y trazas de depuración, pero no queda claro todavía qué avisos funcionales ve el usuario final en Allplan.
- Mensajes que conviene validar en entorno real:
  - aviso por longitud mínima;
  - aviso por selección o inserción inválida;
  - aviso por combinación de geometría no soportada en recuperador;
  - mensajes de finalización si falta configuración de layers o atributos.
- Para esta unidad:
  - **[PENDIENTE DE CONFIRMAR EN ENTORNO REAL]** recopilar los mensajes reales que aparecen en Ventilación.

## 13. Casos prácticos que conviene documentar
- Cambio entre **Conducto Impulsion** y **Conducto Extraccion**.
- Cambio de diámetro en **Conducto Aislado** entre 150 mm y 160 mm.
- Conducto normal con manguito automático entre tramos alineados.
- Inserción de difusor en un extremo o punto previsto del recorrido.
- Recuperador con giro de 90 grados y conexiones automáticas.
- Intento de giro no compatible en **Conducto Recuperador**.
- Aplicación de layer sobre conductos de ventilación.
- Inserción y edición de soporte con subtipo **Ventilacion**.
- Caso de orientación 3D en un tramo inclinado o vertical.

## 14. Capturas necesarias
- [CAPTURA-VENTILACION-01: paleta de Ventilación con los cuatro sistemas visibles]
- [CAPTURA-VENTILACION-02: selector de diámetro en Conducto Aislado mostrando 150 mm y 160 mm]
- [CAPTURA-VENTILACION-03: ejemplo de Conducto Impulsion con manguito automático]
- [CAPTURA-VENTILACION-04: ejemplo de Conducto Extraccion con difusor]
- [CAPTURA-VENTILACION-05: recuperador con conexión y codo 90]
- [CAPTURA-VENTILACION-06: ejemplo de layer aplicado en Ventilación]
- [CAPTURA-VENTILACION-07: bloque de soportes con subtipo Ventilacion]
- [CAPTURA-VENTILACION-08: orientación 3D o tramo vertical/inclinado]
- [CAPTURA-VENTILACION-09: página de macros de Ventilación]
- [CAPTURA-VENTILACION-10: página de Elemento mostrando el estado real en Ventilación]

## 15. Observaciones finales
- Ventilación está bien definida en el registro técnico de instalaciones, pero la página de **Elemento** de la paleta no parece coherente con ese registro.
- Antes de cerrar la versión definitiva del manual conviene validar en Allplan:
  - el elemento definido real que debe usarse en Ventilación;
  - los mensajes funcionales visibles para el usuario;
  - el comportamiento exacto de recuperador en casos límite;
  - y el catálogo real de soportes habilitados.
