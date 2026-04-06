#!/usr/bin/env python3
"""
Inicializador automatico - Caminos Optimos Library.

╔══════════════════════════════════════════════════════════════════════════════╗
║  IMPORTANTE: Este archivo debe estar en la carpeta PADRE de la libreria      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Estructura correcta:                                                        ║
║                                                                              ║
║  mi_proyecto/                                                                ║
║  ├── iniciar.py          ← ESTE ARCHIVO AQUI                                 ║
║  ├── mi_script.py                                                            ║
║  └── Caminos_Optimos/    ← la libreria                                       ║
║      ├── src/                                                                ║
║      ├── pyproject.toml                                                      ║
║      └── ...                                                                 ║
║                                                                              ║
║  Uso:                                                                        ║
║      python iniciar.py                      # Solo configura el entorno      ║
║      python iniciar.py mi_script.py         # Configura y ejecuta script     ║
║      python iniciar.py mi_script.py arg1    # Con argumentos                 ║
║                                                                              ║
║  Primera ejecucion: ~60 segundos (crea venv e instala dependencias)          ║
║  Siguientes ejecuciones: inmediatas                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR   = Path(__file__).resolve().parent
LIBRERIA_DIR = SCRIPT_DIR / "Caminos_Optimos"
VENV_DIR     = LIBRERIA_DIR / "venv"
REQUIREMENTS = LIBRERIA_DIR / "requirements.txt"


def _python_venv():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _pip_venv():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"


def _en_venv() -> bool:
    py = _python_venv()
    if not py.exists():
        return False
    return Path(sys.executable).resolve() == py.resolve()


def _venv_existe() -> bool:
    return _python_venv().exists()


def _crear_venv() -> bool:
    print("  Creando entorno virtual...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True, capture_output=True
        )
        print("  OK - Entorno virtual creado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e}")
        return False


def _instalar_dependencias() -> bool:
    pip = _pip_venv()
    print("  Instalando dependencias...")
    subprocess.run([str(pip), "install", "--upgrade", "pip", "-q"], capture_output=True)
    try:
        subprocess.run([str(pip), "install", "-r", str(REQUIREMENTS)], check=True)
        print("  OK - Dependencias instaladas")
        return True
    except subprocess.CalledProcessError:
        print("  ERROR instalando dependencias")
        return False


def _instalar_libreria() -> bool:
    pip = _pip_venv()
    print("  Instalando libreria caminos-optimos (editable)...")
    try:
        subprocess.run(
            [str(pip), "install", "-e", str(LIBRERIA_DIR)],
            check=True, capture_output=True
        )
        print("  OK - Libreria instalada")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR instalando libreria: {e}")
        return False


def _verificar_instalacion() -> bool:
    pip = _pip_venv()
    if not pip.exists():
        return False
    try:
        result = subprocess.run(
            [str(pip), "freeze"], capture_output=True, text=True, check=True
        )
        instalados = {l.split("==")[0].lower() for l in result.stdout.split("\n") if "==" in l}
        requeridos = {"numpy", "plotly", "networkx"}
        return requeridos.issubset(instalados)
    except Exception:
        return False


def configurar_entorno() -> bool:
    print("=" * 60)
    print("CONFIGURACION AUTOMATICA DEL ENTORNO")
    print("=" * 60)

    if not LIBRERIA_DIR.exists():
        print(f"ERROR: No se encontro la libreria en: {LIBRERIA_DIR}")
        print("Asegurese de que 'Caminos_Optimos/' este en la misma carpeta que 'iniciar.py'")
        return False

    if not _venv_existe():
        if not _crear_venv():
            return False
    else:
        print("  OK - Entorno virtual existente")

    if not _verificar_instalacion():
        if not _instalar_dependencias():
            return False
        if not _instalar_libreria():
            return False
    else:
        print("  OK - Dependencias verificadas")

    print("=" * 60)
    print("ENTORNO LISTO")
    print("=" * 60)
    return True


def ejecutar_script(script_path: str, args: list) -> int:
    python = _python_venv()
    print(f"\nEjecutando: {Path(script_path).name}")
    print("-" * 60)
    result = subprocess.run([str(python), script_path] + args, cwd=SCRIPT_DIR)
    return result.returncode


def main():
    if not _en_venv():
        if not configurar_entorno():
            print("\nERROR configurando el entorno")
            return 1
    else:
        print("Ejecutando en entorno virtual")

    if len(sys.argv) > 1:
        script = sys.argv[1]
        args   = sys.argv[2:]

        script_path = Path(script)
        if not script_path.is_absolute():
            script_path = SCRIPT_DIR / script

        if not script_path.exists():
            print(f"\nERROR: Script no encontrado: {script}")
            return 1

        if _en_venv():
            print(f"Ejecutando: {script_path.name}")
            print("-" * 60)
            import runpy
            sys.argv = [str(script_path)] + args
            runpy.run_path(str(script_path), run_name="__main__")
            return 0
        else:
            return ejecutar_script(str(script_path), args)
    else:
        print("\nUso:")
        print("  python iniciar.py ejemplo_basico_libreria.py")
        print("  python iniciar.py mi_script.py ruta/mi_proyecto.json")
        print("\nEntorno listo para usar.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
