#!/usr/bin/env python3
"""
Ejemplo basico de uso de la libreria caminos_optimos.

╔══════════════════════════════════════════════════════════════════════════════╗
║  INSTRUCCIONES DE USO                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  1. Copie este archivo y 'iniciar.py' a la carpeta PADRE del proyecto:       ║
║                                                                              ║
║     ANTES:                            DESPUES:                               ║
║     mi_proyecto/                      mi_proyecto/                           ║
║     └── Caminos_Optimos/              ├── Caminos_Optimos/  (la libreria)    ║
║         └── EJM_LIB/                 ├── iniciar.py   <- COPIAR AQUI        ║
║             ├── iniciar.py           └── ejemplo_basico_libreria.py         ║
║             └── ejemplo_basico...        <- COPIAR AQUI                     ║
║                                                                              ║
║  2. Ejecute desde mi_proyecto/:                                              ║
║     python iniciar.py ejemplo_basico_libreria.py                            ║
║                                                                              ║
║  Primera ejecucion: ~60s (crea venv e instala dependencias)                  ║
║  Siguientes ejecuciones: inmediatas                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import caminos_optimos
from pathlib import Path

print("=" * 60)
print("CAMINOS OPTIMOS - Ejemplo Basico de Libreria")
print("=" * 60)
print(f"Version: {caminos_optimos.obtener_version()}")

# Ruta al JSON de ejemplo incluido en la libreria
LIBRERIA_DIR = Path(__file__).parent.parent
EJEMPLO_JSON = LIBRERIA_DIR / "ejemplos" / "basico" / "ejm_saltar_extraccion_impulsion_135deg.json"

print(f"\nProcesando: {EJEMPLO_JSON.name}")
print("-" * 60)

# Calcular ruta optima
resultado = caminos_optimos.calcular(
    archivo_json=str(EJEMPLO_JSON),
    mostrar=False,   # No abrir navegador automaticamente
    guardar=True,    # Guardar outputs (HTML, MD, JSON grafo)
)

# Mostrar resultado
if resultado["exito"]:
    if resultado["valido"]:
        print("\nRuta VALIDA")
        print(f"  Soportes generados : {resultado['num_soportes']}")
        print(f"\nArchivos generados:")
        if resultado["archivo_html"]:
            print(f"  HTML  : {resultado['archivo_html']}")
        if resultado["archivo_md"]:
            print(f"  MD    : {resultado['archivo_md']}")
        if resultado["archivo_grafo_json"]:
            print(f"  Grafo : {resultado['archivo_grafo_json']}")
    else:
        print("\nRuta INVALIDA (ver HTML para depuracion)")
        if resultado["archivo_html"]:
            print(f"  HTML  : {resultado['archivo_html']}")
else:
    print(f"\nERROR: {resultado['error']}")

print("\n" + "=" * 60)
print("COMPLETADO")
print("=" * 60)
