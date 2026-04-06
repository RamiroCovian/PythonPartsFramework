"""
Ejecuta TODOS los ejemplos JSON y abre cada visualizacion.
Uso: python correr_todos.py
"""
import subprocess, sys, os, glob, time

# Usar el Python del venv si existe
venv_py = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')
if not os.path.exists(venv_py):
    venv_py = sys.executable

files = sorted(
    glob.glob('ejemplos/**/*.json', recursive=True) +
    glob.glob('inputs/**/*.json', recursive=True)
)
# Excluir outputs (grafos, etc.) y plantilla
files = [f for f in files if 'outputs' not in f and 'plantilla' not in f]

passed, failed, timeouts, failures = 0, 0, 0, []

for i, f in enumerate(files):
    name = f.replace('\\', '/').split('/')[-1]

    print(f"\n[{i+1}/{len(files)}] {name}")
    print("=" * 60)

    try:
        r = subprocess.run(
            [venv_py, 'main.py', f],
            timeout=180
        )

        if r.returncode == 0:
            passed += 1
        else:
            failed += 1
            failures.append(f"FALLO: {name}")
    except subprocess.TimeoutExpired:
        timeouts += 1
        failures.append(f"TIMEOUT: {name}")
        print(f"\n*** TIMEOUT (180s): {name} ***")

    # Pausa breve para que el navegador abra la grafica
    time.sleep(1)

print("\n" + "=" * 60)
total = passed + failed + timeouts
print(f"RESUMEN: {passed} OK, {failed} FALLOS, {timeouts} TIMEOUT de {total} ejemplos")
if failures:
    for fn in failures:
        print(f"  {fn}")
print("=" * 60)
