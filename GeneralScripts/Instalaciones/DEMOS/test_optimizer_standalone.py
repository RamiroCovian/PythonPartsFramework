# -*- coding: utf-8 -*-
"""
Standalone test for the optimizer integration.

Runs the Caminos_Optimos_Lib optimizer on a mock JSON input and
prints the generated output grafo JSON.

Usage (from the DEMOS/ folder):
    python test_optimizer_standalone.py

Or specify a custom input:
    python test_optimizer_standalone.py path/to/input.json
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIBRERIA = HERE.parent / "Libreria"
sys.path.insert(0, str(LIBRERIA))

import optimizer_adapter
import optimizer_runner


def main():
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        instalaciones = HERE.parent
        input_file = instalaciones / "JsonXample" / "inclinado_tres_caminos.json"

    if not input_file.is_file():
        print(f"ERROR: No se encontró el archivo: {input_file}")
        print(f"\nUso: python {Path(__file__).name} [ruta_al_json]")
        return

    print("=" * 60)
    print("TEST: Integración Optimizador")
    print("=" * 60)
    print(f"\nInput: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    is_optimizer_format = "techo" in input_data and "caminos" in input_data
    is_our_export = "caminos" in input_data and "techo" not in input_data

    if is_optimizer_format:
        print("\nFormato detectado: input directo del optimizador")
        print("Ejecutando directamente sin traducción...")
        grafo = optimizer_runner.run_optimizer(
            input_json_path=str(input_file),
        )
    elif is_our_export:
        print("\nFormato detectado: export de polyline_base_lib")
        print("Traduciendo al formato del optimizador...")
        caminos = input_data.get("caminos", [])
        if not caminos:
            print("ERROR: No hay caminos en el JSON")
            return
        camino_dict = caminos[0]
        optimizer_input = optimizer_adapter.build_optimizer_input(camino_dict)

        temp_path = HERE / "optimizer_temp" / "test_input.json"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(optimizer_input, f, ensure_ascii=False, indent=2)
        print(f"Input traducido escrito en: {temp_path}")

        grafo = optimizer_runner.run_optimizer(
            input_json_path=str(temp_path),
        )
    else:
        print("ERROR: Formato JSON no reconocido")
        return

    print("\n" + "=" * 60)
    print("RESULTADO: Grafo JSON de salida")
    print("=" * 60)

    paths = optimizer_adapter.parse_optimizer_output(grafo)
    print(f"\nCaminos encontrados: {len(paths)}")
    for i, path in enumerate(paths):
        print(f"  Camino {i+1}: {len(path)} puntos")
        if path:
            print(f"    Inicio: ({path[0][0]:.1f}, {path[0][1]:.1f}, {path[0][2]:.1f})")
            print(f"    Final:  ({path[-1][0]:.1f}, {path[-1][1]:.1f}, {path[-1][2]:.1f})")

    output_path = HERE / "optimizer_temp" / "test_output_grafo.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(grafo, f, ensure_ascii=False, indent=2)

    print(f"\nJSON de salida guardado en:\n  {output_path}")
    print(f"\nTamaño: {output_path.stat().st_size} bytes")
    print(f"Caminos en grafo: {len(grafo.get('caminos', []))}")

    for i, camino in enumerate(grafo.get("caminos", [])):
        nodos = camino.get("nodos", [])
        segmentos = camino.get("segmentos", [])
        soportes = camino.get("soportes", [])
        print(f"\n  Camino '{camino.get('id', i)}': "
              f"{len(nodos)} nodos, {len(segmentos)} segmentos, {len(soportes)} soportes")

    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
