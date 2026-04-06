# Caminos Optimos

Sistema de optimizacion de rutas de tuberias de ventilacion para techos inclinados.

## Descripcion

Calcula la ruta optima de una tuberia de ventilacion bajo techos inclinados con IS
(instalaciones sanitarias). Soporta:

- **Optimizacion de ruta** con restriccion de angulos de codo (45°/90°/135°)
- **Techos inclinados** definidos por vertices, con multiples IS
- **Obstaculos** con estrategia `saltar` (pasa por encima) o `rodear` (desvio horizontal)
- **Multi-camino** secuencial: cada tuberia calculada se convierte en obstaculo para las siguientes
- **Generacion automatica de soportes** (OMEGA / ZETA) a lo largo de la ruta
- **Visualizacion 3D interactiva** con Plotly
- **Salida JSON** del grafo IS con nodos, segmentos y soportes

## Estructura del Proyecto

```
Caminos_Optimos/
├── caminos_optimos/           # API publica de libreria
│   └── __init__.py            #   calcular(), obtener_version()
├── src/                       # Codigo fuente principal
│   ├── modelos/               #   Punto3D, Obstaculo, TuboIS, Soporte
│   ├── procesamiento/         #   pipeline.py, entrada.py, resultado.py
│   ├── post_procesamiento/    #   asignacion_is.py, generador_soportes.py
│   ├── algoritmos/            #   RRT* con angulos + cruces tubo
│   ├── visualizacion/         #   visualizador_3d.py (Plotly)
│   └── reportes.py            #   ResultadoCamino, generar_resultado_markdown
├── ejemplos/
│   ├── basico/                #   JSONs de ejemplo
│   └── real/                  #   Casos reales
├── EJM_LIB/                   # Plantillas para uso como libreria
│   ├── iniciar.py             #   Gestor de entorno virtual
│   └── ejemplo_basico_libreria.py
├── pyproject.toml             # Metadata del paquete caminos-optimos
├── requirements.txt
├── main.py                    # Punto de entrada CLI
└── README.md
```

## Instalacion

### Uso como script directo

```powershell
cd Caminos_Optimos
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### Uso como libreria desde otro proyecto

Copiar `EJM_LIB/iniciar.py` a la carpeta padre de `Caminos_Optimos/`:

```
mi_proyecto/
├── iniciar.py          <- copiar desde EJM_LIB/
├── mi_script.py
└── Caminos_Optimos/    <- esta carpeta
```

Primera ejecucion (crea venv e instala):
```powershell
python iniciar.py mi_script.py
```

---

## Uso como Script CLI

```powershell
.\venv\Scripts\python.exe main.py ejemplos/basico/ejm_colega_is01_is02_extraccion_impulsion.json
.\venv\Scripts\python.exe main.py mi_proyecto.json --no-mostrar   # sin abrir navegador
.\venv\Scripts\python.exe main.py mi_proyecto.json --no-guardar   # sin guardar archivos
```

**Salidas generadas** en `ejemplos/outputs/` (o junto al JSON de entrada):
- `<nombre>.html` — visualizacion 3D interactiva
- `<nombre>.md` — reporte con segmentos, angulos y tabla de soportes
- `<nombre>_grafo.json` — grafo IS con nodos, segmentos y soportes

---

## Uso como Libreria Python

```python
import caminos_optimos

print(caminos_optimos.obtener_version())  # "1.0.0"

resultado = caminos_optimos.calcular(
    archivo_json = "Caminos_Optimos/ejemplos/basico/mi_proyecto.json",
    mostrar      = False,   # no abrir navegador
    guardar      = True,    # guardar HTML, MD y grafo JSON
)

if resultado['exito'] and resultado['valido']:
    print(f"Longitud: {resultado['longitud_mm']:.0f} mm")
    print(f"Soportes: {resultado['num_soportes']}")
    print(f"HTML    : {resultado['archivo_html']}")
    print(f"Grafo IS: {resultado['archivo_grafo_json']}")
else:
    print("Error:", resultado.get('error', 'Ruta invalida'))
```

**Claves del diccionario retornado:**
| Clave | Tipo | Descripcion |
|-------|------|-------------|
| `exito` | bool | True si no hubo excepcion |
| `valido` | bool | True si la ruta geometrica es valida |
| `longitud_mm` | float | Longitud total de la tuberia en mm |
| `num_soportes` | int | Cantidad de soportes generados |
| `archivo_html` | str | Ruta al HTML generado (None si guardar=False) |
| `archivo_md` | str | Ruta al Markdown generado |
| `archivo_grafo_json` | str | Ruta al JSON del grafo IS con soportes |
| `visualizador` | obj | Objeto Visualizador3D para uso avanzado |
| `error` | str | Mensaje de error (si exito=False) |

---

## Formato de Entrada JSON

```json
{
    "id": "mi_caso",
    "nombre": "Mi Proyecto",
    "techo": [
        {
            "id": "techo_principal",
            "vertices": [
                { "x": 0, "y": 0, "z": 2800 },
                { "x": 6000, "y": 0, "z": 2900 },
                { "x": 6000, "y": 4000, "z": 2900 },
                { "x": 0, "y": 4000, "z": 2800 }
            ]
        }
    ],
    "subdivisiones_is": [
        { "id": "IS1", "vertices": [ ... ] },
        { "id": "IS2", "vertices": [ ... ] }
    ],
    "tubos_is": [
        { "id": "T1", "is_id": "IS1",
          "punto_inicio": { "x": 100, "y": 550, "z": 2976 },
          "punto_fin":    { "x": 2900, "y": 550, "z": 2976 } }
    ],
    "nodos": [
        { "id": "A", "tipo": "inicio",
          "coordenadas": { "x": 500, "y": 2000, "z": 2947 },
          "anteriores": [], "siguientes": ["B"] },
        { "id": "B", "tipo": "fin",
          "coordenadas": { "x": 5500, "y": 2000, "z": 3113 },
          "anteriores": ["A"], "siguientes": [] }
    ],
    "obstaculos": [
        { "id": "Viga", "vertices": [ ... ], "modo": ["saltar"] }
    ],
    "configuracion": {
        "subtipo_tuberia": "extraccion_impulsion",
        "estrategia_colision": ["saltar"]
    }
}
```

### Subtipos disponibles

| Subtipo | Dimensiones | Angulos | Descripcion |
|---------|-------------|---------|-------------|
| `extraccion_impulsion` | 75x75 mm | 45°/135° | Ductos de extraccion e impulsion |
| `aislado` | 160x160 mm | 45°/135° | Ductos con aislamiento termico |
| `recuperador` | 160x160 mm | 90° | Ductos ortogonales |

### Estrategias de colision con obstaculos

| Estrategia | Descripcion |
|------------|-------------|
| `saltar` | La tuberia sube para pasar por encima del obstaculo |
| `rodear` | La tuberia se desvía horizontalmente |

---

## Soportes Generados

El sistema genera soportes automaticamente a lo largo de la ruta:

- **OMEGA** (estandar): cuando hay dos tubos IS paralelos que flanquean la tuberia
- **ZETA** (varifix): cuando solo hay un tubo IS disponible
- **Horizontal**: ducto orientado en Y, soporte cruza en X
- **Vertical**: ducto orientado en X, soporte cruza en Y

Los soportes se incluyen en el `_grafo.json` de salida:
```json
{
  "soportes": [
    { "tipo": "horizontal", "subtipo": "Ventilacion",
      "posicion1": [25.0, 1256.3, 6045.0],
      "posicion2": [725.0, 1256.3, 6045.0],
      "cota_a": 110.0, "cota_b": 680.0 }
  ]
}
```

---

## Multi-Camino

Para calcular multiples tuberias donde cada una evita las anteriores:

```json
{
    "nombre": "Proyecto Multi-Camino",
    "caminos": [
        { "id": "camino_1", "nombre": "Tuberia 1",
          "nodos": [ ... ], "configuracion": { ... } },
        { "id": "camino_2", "nombre": "Tuberia 2",
          "nodos": [ ... ], "configuracion": { ... } }
    ],
    "techo": [ ... ],
    "subdivisiones_is": [ ... ],
    "tubos_is": [ ... ]
}
```

---

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## Dependencias

Ver `requirements.txt`. Paquetes principales:
- `numpy>=1.21.0` — calculos geometricos
- `plotly>=5.15.0` — visualizacion 3D interactiva
- `networkx>=3.0` — grafo de nodos IS

---

## Licencia

Propietario - TECHTIVA 2026
