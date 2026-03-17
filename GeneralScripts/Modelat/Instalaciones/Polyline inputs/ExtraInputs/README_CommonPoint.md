# CommonPoint – Identificación y Gestión de Puntos Comunes entre Caminos (Allplan PythonPart)

**Autor:** Tomas Tessio  
**Estado:** En desarrollo. Falta ajustar tolerancias, validar en entorno Allplan real y afinar experiencia de usuario.

---

## 📘 Objetivo general

**CommonPoint** busca establecer una base para la **identificación y tratamiento de puntos comunes entre caminos o polilíneas**, dentro de un flujo de trabajo de ingeniería o arquitectura en Allplan.

El propósito principal es **detectar nodos coincidentes o compartidos entre distintos recorridos** (por clave o por proximidad), permitir su **visualización directa en el modelo**, y crear una **estructura persistente** que luego sirva de insumo a algoritmos más complejos de análisis de conectividad o generación de rutas óptimas.

---

## ⚙️ Qué permite hacer

### 1. Captura por roles
- Capturar puntos con rol: **Inicial**, **Paso**, **Bifurcación** o **Final**.  
- Asignar cada punto a un `PathId` y `SegmentId` para agruparlo dentro de un camino lógico.
- Visualizar en tiempo real los puntos capturados (cada uno marcado con un cuadrado).  
- Al marcar un punto **Final**, se crea la polilínea correspondiente y se exporta al archivo JSON en el escritorio.

### 2. Edición avanzada
- Mover vértices existentes mediante *drag & drop*.
- Insertar puntos intermedios con “**Mode Insertar punto**”.
- Doble clic en extremos para **extender** caminos.
- Crear **bifurcaciones** a partir de un punto existente (botón `1006`).
- Borrar segmentos o secciones completas por clic o selección con marco.

### 3. Persistencia estructurada
- Cada sesión exporta un JSON (`common_points_XXXXXXXX.json`) en el escritorio.  
- El archivo conserva toda la información de cada camino: roles, coordenadas, colores, etc.  
- Este formato permitirá futuras integraciones con sistemas de análisis o sincronización externa.

---

## 🧩 Hacia dónde apunta

Este módulo es una **etapa preliminar de una arquitectura de “ruteo inteligente”**.  
Busca establecer una capa de información donde los caminos puedan **interconectarse mediante puntos comunes**, que más adelante podrían:

- Servir de base a algoritmos de optimización de recorrido.  
- Permitir validaciones de topología o continuidad entre caminos.  
- Ser reutilizados para generar **redes, tramas o estructuras de conexión** dentro del modelo 3D.  

A largo plazo, el objetivo es que el sistema pueda **detectar coincidencias automáticas** y proponer conexiones entre elementos constructivos (tuberías, bandejas, caminos eléctricos, etc.) de forma semiautomática.

---

## ⚙️ Parámetros esperados (en el .pyp)
- `PathId`, `SegmentId`, `PointRole`
- `CommonProp` y `SymbolCommonProps` (propiedades gráficas)
- `CheckBoxValue`: activa el modo “Insertar punto”
- Botones de evento (`EventId`):
  - 2100–2103 → definir rol (Inicial, Paso, Bifurcación, Final)
  - 1001–1006 → crear, guardar, finalizar, borrar o bifurcar

---

## 📏 Tolerancias y comportamiento
- **Tolerancia de interacción:** 5 mm (por defecto)
- **Elemento marcador:** cuadrado plano de 50 mm de lado (centra cada punto)
- **Proyección base:** XY por defecto, con coordenada Z habilitada
- **Persistencia de color:** basada en `PathId`

---

## 🧠 Estado actual y próximos pasos

- ✅ Implementa captura + edición completa con roles.  
- ✅ Exporta y mantiene persistencia JSON.  
- ⚠️ Falta integrar detección automática de **puntos comunes** (por clave o proximidad).  
- ⚠️ Requiere validación visual de tolerancias (dependientes de escala y unidad del modelo).  
- ⚙️ En futuras versiones se incluirá:
  - Filtro visual para resaltar puntos comunes.  
  - Elementos 3D específicos por tipo de conexión (no solo cuadrados).  
  - Integración con módulos de análisis de rutas.

---

## 🧑‍💻 Autoría
**Desarrollado por:** Tomas Tessio  
**Versión:** inicial experimental  


