"""
Punto de entrada principal del sistema Caminos Optimos.

USO:
    python main.py <archivo.json>
    python main.py inputs/mi_proyecto.json
    
    Opciones:
        --no-mostrar    No abrir el navegador automáticamente
        --no-guardar    No guardar archivos de salida
"""

import sys
from pathlib import Path

from src.cargador_json import ejecutar_desde_json


def main():
    """Funcion principal."""
    
    print("=" * 60)
    print("CAMINOS OPTIMOS - Sistema de Optimizacion de Tuberias")
    print("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("\nUso: python main.py <archivo.json>")
        print("\nEjemplo:")
        print("  python main.py inputs/mi_proyecto.json")
        print("\nPlantilla disponible en: inputs/plantilla.json")
        print("Ejemplos disponibles en: ejemplos/")
        return
    
    archivo = sys.argv[1]
    
    # Opciones
    mostrar = "--no-mostrar" not in sys.argv
    guardar = "--no-guardar" not in sys.argv
    
    # Verificar que existe
    if not Path(archivo).exists():
        print(f"\nError: No se encontró el archivo '{archivo}'")
        print("\nArchivos disponibles:")
        print("  - inputs/plantilla.json (plantilla base)")
        for f in Path("ejemplos").glob("*.json"):
            print(f"  - {f}")
        return
    
    # Ejecutar
    print(f"\nProcesando: {archivo}")
    print("-" * 60)
    
    ejecutar_desde_json(archivo, mostrar=mostrar, guardar=guardar)
    
    print("\n" + "=" * 60)
    print("COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
