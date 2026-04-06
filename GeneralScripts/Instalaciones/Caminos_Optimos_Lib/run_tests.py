import subprocess, sys, glob

files = sorted(glob.glob('ejemplos/**/*.json', recursive=True) + glob.glob('inputs/**/*.json', recursive=True))
passed, failed, failures = 0, 0, []

for f in files:
    name = f.replace('\\', '/').split('/')[-1]
    if name == 'plantilla.json':
        continue
    r = subprocess.run([sys.executable, 'main.py', f, '--no-mostrar'], capture_output=True, text=True, timeout=120)
    out = r.stdout + r.stderr
    if 'Estado: VALIDO' in out:
        passed += 1
    else:
        failed += 1
        err = ''
        for line in out.split('\n'):
            if 'ERROR' in line or 'Traceback' in line:
                err = line.strip()[:80]
                break
        failures.append(f'{name}: {err}')

print(f'TOTAL: {passed} PASS, {failed} FAIL')
for fn in failures:
    print(f'  {fn}')
