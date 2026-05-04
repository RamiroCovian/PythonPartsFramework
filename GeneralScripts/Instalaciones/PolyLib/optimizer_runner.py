# -*- coding: utf-8 -*-
"""
Subprocess runner for Caminos_Optimos_Lib.

Executes the optimizer in its own venv Python because it requires
numpy, plotly, and networkx which Allplan's embedded Python may not have.

If the venv's python.exe is broken (base interpreter moved/deleted),
falls back to finding a working system Python and injecting the venv's
site-packages via PYTHONPATH.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _find_lib_root() -> Path:
    """Locate the Caminos_Optimos_Lib directory relative to this file."""
    here = Path(__file__).resolve().parent
    candidate = here.parent / "Caminos_Optimos_Lib"
    if candidate.is_dir():
        return candidate
    for parent in here.parents:
        candidate = parent / "Caminos_Optimos_Lib"
        if candidate.is_dir():
            return candidate
        candidate = parent / "Instalaciones" / "Caminos_Optimos_Lib"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        "No se encontró Caminos_Optimos_Lib. "
        "Debe estar en el mismo nivel que PolyLib/."
    )


def _venv_python_path(lib_root: Path) -> Path:
    """Ruta esperada del python.exe dentro del venv (puede estar roto)."""
    if sys.platform == "win32":
        return lib_root / "venv" / "Scripts" / "python.exe"
    return lib_root / "venv" / "bin" / "python"


def _venv_site_packages(lib_root: Path) -> Optional[Path]:
    """Directorio site-packages del venv, o None si no existe."""
    base = lib_root / "venv" / "Lib" / "site-packages"        # Windows
    if base.is_dir():
        return base
    # Linux/Mac layout: venv/lib/pythonX.Y/site-packages
    lib_dir = lib_root / "venv" / "lib"
    if lib_dir.is_dir():
        for child in lib_dir.iterdir():
            sp = child / "site-packages"
            if sp.is_dir():
                return sp
    return None


def _probe_python(exe: Path) -> bool:
    """Comprueba que un ejecutable Python funciona lanzando un no-op."""
    try:
        r = subprocess.run(
            [str(exe), "-c", "import sys; sys.exit(0)"],
            capture_output=True,
            timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def _find_system_python() -> Optional[Path]:
    """Busca un Python funcional en el PATH y ubicaciones comunes de Windows."""
    # 1. Candidatos en PATH
    for name in ("python", "python3", "python3.11", "python3.10", "python3.9"):
        try:
            result = subprocess.run(
                ["where", name] if sys.platform == "win32" else ["which", name],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.strip().splitlines():
                p = Path(line.strip())
                if p.is_file() and _probe_python(p):
                    return p
        except Exception:
            pass

    # 2. Ubicaciones comunes en Windows
    common_roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python",
        Path("C:/Python311"),
        Path("C:/Python310"),
        Path("C:/Python39"),
        Path("C:/Python38"),
        Path("C:/Users") / os.environ.get("USERNAME", "") / "AppData" / "Local" / "Programs" / "Python",
    ]
    for root in common_roots:
        if not root.exists():
            continue
        # Puede ser una carpeta con subcarpetas Python311, Python310, ...
        candidates = list(root.glob("Python*/python.exe")) + [root / "python.exe"]
        for p in candidates:
            if p.is_file() and _probe_python(p):
                return p

    return None


def _resolve_python_and_env(lib_root: Path) -> Tuple[Path, Dict[str, str]]:
    """Devuelve (python_exe, env) listos para el subprocess.

    Estrategia:
    1. Usar venv/python.exe si funciona.
    2. Si está roto, buscar Python del sistema + inyectar site-packages del venv
       via PYTHONPATH para que numpy/networkx/plotly sigan disponibles.

    Raises:
        FileNotFoundError: Si no se encuentra ningún Python funcional.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    venv_py = _venv_python_path(lib_root)

    # Intento 1: venv directo
    if venv_py.is_file() and _probe_python(venv_py):
        print(f"[OPTIMIZER] Usando venv Python: {venv_py}")
        return venv_py, env

    print(f"[OPTIMIZER] venv Python roto o no encontrado ({venv_py}). Buscando Python del sistema...")

    # Intento 2: Python del sistema + site-packages del venv vía PYTHONPATH
    system_py = _find_system_python()
    if system_py is None:
        raise FileNotFoundError(
            "No se encontró ningún Python funcional en el sistema.\n"
            f"El venv está en: {venv_py}\n"
            "Solución: recree el venv con 'python -m venv venv && pip install -r requirements.txt' "
            f"dentro de {lib_root}"
        )

    site_pkgs = _venv_site_packages(lib_root)
    if site_pkgs:
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(site_pkgs) + (os.pathsep + existing if existing else "")
        print(f"[OPTIMIZER] PYTHONPATH → {env['PYTHONPATH']}")

    print(f"[OPTIMIZER] Usando Python del sistema: {system_py}")
    return system_py, env


def run_optimizer(
    input_json_path: str,
    timeout: int = 120,
    lib_root: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the Caminos_Optimos_Lib optimizer as a subprocess.

    Args:
        input_json_path: Absolute path to the input JSON file.
        timeout: Maximum seconds to wait for the process (default 120).
        lib_root: Override path to Caminos_Optimos_Lib root directory.

    Returns:
        Parsed dict from the ``_grafo.json`` output file.

    Raises:
        RuntimeError: If the subprocess fails or the output is not found.
        TimeoutError: If the subprocess exceeds *timeout*.
        FileNotFoundError: If no working Python is found.
    """
    root = Path(lib_root) if lib_root else _find_lib_root()
    python_exe, env = _resolve_python_and_env(root)
    main_py = root / "main.py"

    if not main_py.is_file():
        raise FileNotFoundError(f"No se encontró main.py en: {main_py}")

    input_path = Path(input_json_path).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Archivo de entrada no existe: {input_path}")

    cmd = [str(python_exe), str(main_py), str(input_path), "--no-mostrar"]

    print(f"[OPTIMIZER] Running: {input_path}")
    # print(f"[OPTIMIZER] CWD: {root}")

    try:
        print("############################ SUBPROCESS ############################")
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"El optimizador tardó más de {timeout}s. "
            "Intente con un camino más corto o aumente el timeout."
        ) from exc

    def _safe_print(msg: str) -> None:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", errors="replace").decode("ascii"))

    _safe_print(f"[OPTIMIZER] Exit code: {result.returncode}")
    if result.stdout:
        for line in result.stdout.strip().split("\n")[-20:]:
            _safe_print(f"[OPTIMIZER] {line}")
    if result.stderr:
        for line in result.stderr.strip().split("\n")[-10:]:
            _safe_print(f"[OPTIMIZER ERR] {line}")

    if result.returncode != 0:
        raise RuntimeError(
            f"El optimizador terminó con error (código {result.returncode}).\n"
            f"Stderr: {result.stderr[-500:] if result.stderr else '(vacío)'}"
        )

    grafo_path = _find_grafo_output(input_path, root)
    if grafo_path is None:
        raise RuntimeError(
            "El optimizador finalizó pero no se encontró el archivo _grafo.json. "
            f"Buscado en: {root / 'ejemplos' / 'outputs'}"
        )

    print(f"[OPTIMIZER] Reading grafo from: {grafo_path}")
    with open(grafo_path, "r", encoding="utf-8") as f:
        grafo = json.load(f)

    return grafo


def _find_grafo_output(input_path: Path, lib_root: Path) -> Optional[Path]:
    """Locate the _grafo.json produced by the optimizer."""
    stem = input_path.stem
    outputs_dir = input_path.parent.parent / "outputs"
    candidate = outputs_dir / f"{stem}_grafo.json"
    if candidate.is_file():
        return candidate

    outputs_dir = lib_root / "ejemplos" / "outputs"
    candidate = outputs_dir / f"{stem}_grafo.json"
    if candidate.is_file():
        return candidate

    return None
