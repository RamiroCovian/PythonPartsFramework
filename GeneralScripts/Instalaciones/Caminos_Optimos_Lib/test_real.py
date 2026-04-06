import sys
sys.path.insert(0, '.')
import caminos_optimos

tests = [
    'ejemplos/real/prueba_3caminos_cruce.json',
    'ejemplos/real/prueba_7caminos.json',
    'ejemplos/real/prueba_cuadruple_cruce.json',
    'ejemplos/real/prueba_multiples_caminos.json',
    'ejemplos/real/prueba_tres_caminos.json',
    'ejemplos/real/prueba_triple_cruce.json',
    'ejemplos/real/prueba_triple_cruce_90.json',
    'ejemplos/real/rodear_7caminos.json',
]

passed = 0
failed = 0

for f in tests:
    name = f.split('/')[-1]
    try:
        res = caminos_optimos.calcular(f, mostrar=True, guardar=False)
        exito = res['exito']
        valido = res['valido']
        if exito and valido:
            print('OK:', name)
            passed += 1
        else:
            err = res.get('error', '')
            if err:
                err = str(err)[:80]
            print('FAIL:', name, '- exito=', exito, ', valido=', valido, ', error=', err)
            failed += 1
    except Exception as e:
        print('FAIL:', name, '- exception:', str(e)[:80])
        failed += 1

print('')
print('TOTAL:', passed, 'PASS,', failed, 'FAIL')
