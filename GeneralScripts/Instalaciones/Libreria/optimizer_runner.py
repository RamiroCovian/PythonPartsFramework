# -*- coding: utf-8 -*-
"""
Subprocess runner for Caminos_Optimos_Lib.

Executes the optimizer in its own venv Python because it requires
numpy, plotly, and networkx which Allplan's embedded Python may not have.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


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
        "Debe estar en el mismo nivel que Libreria/."
    )


def _find_venv_python(lib_root: Path) -> Path:
    """Locate the venv python executable."""
    if sys.platform == "win32":
        python = lib_root / "venv" / "Scripts" / "python.exe"
    else:
        python = lib_root / "venv" / "bin" / "python"
    if not python.is_file():
        raise FileNotFoundError(
            f"No se encontró el Python del venv en: {python}\n"
            "Asegúrese de que el venv de Caminos_Optimos_Lib esté creado."
        )
    return python


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
    """
    root = Path(lib_root) if lib_root else _find_lib_root()
    python_exe = _find_venv_python(root)
    main_py = root / "main.py"

    if not main_py.is_file():
        raise FileNotFoundError(f"No se encontró main.py en: {main_py}")

    input_path = Path(input_json_path).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Archivo de entrada no existe: {input_path}")

    cmd = [
        str(python_exe),
        str(main_py),
        str(input_path),
        "--no-mostrar",
    ]

    print(f"[OPTIMIZER] Running: {' '.join(cmd)}")
    print(f"[OPTIMIZER] CWD: {root}")

    import os as _os
    env = _os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
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
    """Locate the _grafo.json produced by the optimizer.

    The optimizer writes outputs to ``<input_parent>/../outputs/<stem>_grafo.json``.
    """
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
