"""
Script para convertir todos los JSON de ejemplo al formato de lista plana.

Formato anterior (con claves separadas):
    "inicio": { "id": "A", "tipo": "inicio", "coordenadas": {...}, ... },
    "fin": { ... },
    "obligatorios": [ ... ],
    "libres": [ ... ]

Formato nuevo (lista plana):
    "puntos": [
        { "id": "A", "tipo": "inicio", "coordenadas": { "x": 500, "y": 1000, "z": 2800 }, "anteriores": [], "siguientes": ["O1"] },
        { "id": "O1", "tipo": "orden_obligatorio", ... },
        { "id": "B", "tipo": "fin", ... }
    ]
"""

import json
import re
import sys
from pathlib import Path


def _extraer_coords(p: dict) -> dict:
    """Extrae coordenadas de un punto."""
    if 'coordenadas' in p:
        return p['coordenadas']
    return {'x': p['x'], 'y': p['y'], 'z': p['z']}


def _bloque_a_lista(puntos_data: dict) -> list:
    """Convierte un bloque con inicio/fin/obligatorios/libres a lista plana."""
    inicio = puntos_data.get('inicio', {})
    fin = puntos_data.get('fin', {})
    obligatorios = puntos_data.get('obligatorios', [])
    libres = puntos_data.get('libres', [])

    # Si ya tiene 'tipo', los puntos tienen formato nuevo con claves separadas
    # Solo necesitamos aplanar a lista
    lista = []

    # Inicio
    if inicio:
        inicio_id = inicio.get('id', 'A')
        oblig_sorted = sorted(obligatorios, key=lambda x: x.get('orden', 0))
        oblig_ids = [o.get('id', f'O{i+1}') for i, o in enumerate(oblig_sorted)]
        fin_id = fin.get('id', 'B')

        sig_inicio = inicio.get('siguientes', [oblig_ids[0]] if oblig_ids else [fin_id])
        lista.append({
            'id': inicio_id,
            'tipo': inicio.get('tipo', 'inicio'),
            'coordenadas': _extraer_coords(inicio),
            'anteriores': inicio.get('anteriores', []),
            'siguientes': sig_inicio,
        })

    # Obligatorios (en orden)
    for i, o in enumerate(oblig_sorted if obligatorios else []):
        ant = o.get('anteriores', [inicio_id] if i == 0 else [oblig_ids[i - 1]])
        sig = o.get('siguientes', [fin_id] if i == len(oblig_sorted) - 1 else [oblig_ids[i + 1]])
        lista.append({
            'id': o.get('id', f'O{i+1}'),
            'tipo': o.get('tipo', 'orden_obligatorio'),
            'coordenadas': _extraer_coords(o),
            'anteriores': ant,
            'siguientes': sig,
        })

    # Libres
    for l in libres:
        lista.append({
            'id': l.get('id', 'L'),
            'tipo': l.get('tipo', 'orden_libre'),
            'coordenadas': _extraer_coords(l),
            'anteriores': l.get('anteriores', []),
            'siguientes': l.get('siguientes', []),
        })

    # Fin
    if fin:
        ant_fin = fin.get('anteriores', [oblig_ids[-1]] if oblig_ids else [inicio_id])
        lista.append({
            'id': fin_id,
            'tipo': fin.get('tipo', 'fin'),
            'coordenadas': _extraer_coords(fin),
            'anteriores': ant_fin,
            'siguientes': fin.get('siguientes', []),
        })

    return lista


def _compactar_coords_json(texto: str) -> str:
    """Post-procesa el JSON para poner objetos {x,y,z} en una sola linea."""
    # Compactar "coordenadas": { "x": ..., "y": ..., "z": ... }
    patron_coord = re.compile(
        r'"coordenadas":\s*\{\s*\n\s*"x":\s*([^,\n]+),\s*\n\s*"y":\s*([^,\n]+),\s*\n\s*"z":\s*([^\n\}]+)\s*\n\s*\}',
        re.MULTILINE
    )
    texto = patron_coord.sub(r'"coordenadas": { "x": \1, "y": \2, "z": \3 }', texto)
    
    # Compactar objetos sueltos { "x": ..., "y": ..., "z": ... } (vertices de techo, IS, obstaculos)
    patron_xyz = re.compile(
        r'\{\s*\n\s*"x":\s*([^,\n]+),\s*\n\s*"y":\s*([^,\n]+),\s*\n\s*"z":\s*([^\n\}]+)\s*\n\s*\}',
        re.MULTILINE
    )
    texto = patron_xyz.sub(r'{ "x": \1, "y": \2, "z": \3 }', texto)
    
    # Compactar arrays cortos de strings a una linea
    patron_arr = re.compile(
        r'"(anteriores|siguientes|modo)":\s*\[\s*\n\s*((?:"[^"]*"(?:,\s*\n\s*"[^"]*")*)?)\s*\n\s*\]',
        re.MULTILINE
    )
    def _compactar_arr(m):
        key = m.group(1)
        items = m.group(2).strip()
        if not items:
            return f'"{key}": []'
        # Limpiar saltos de linea entre items
        items_clean = re.sub(r'\s*\n\s*', ' ', items)
        return f'"{key}": [{items_clean}]'
    
    texto = patron_arr.sub(_compactar_arr, texto)
    
    return texto


def convertir_archivo(ruta: Path) -> bool:
    """Convierte un archivo JSON al formato de lista plana."""
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    modificado = False

    # Single-camino: datos['puntos']
    if 'puntos' in datos:
        puntos = datos['puntos']
        # Si es dict con 'inicio'/'fin', convertir a lista
        if isinstance(puntos, dict) and 'inicio' in puntos:
            datos['puntos'] = _bloque_a_lista(puntos)
            modificado = True

    # Multi-camino: datos['caminos'][i]
    if 'caminos' in datos:
        for camino in datos['caminos']:
            if 'inicio' in camino:
                puntos_camino = {
                    'inicio': camino.pop('inicio'),
                    'fin': camino.pop('fin'),
                    'obligatorios': camino.pop('obligatorios', []),
                    'libres': camino.pop('libres', []),
                }
                camino['puntos'] = _bloque_a_lista(puntos_camino)
                modificado = True

    # Siempre re-escribir para compactar coordenadas {x,y,z}
    texto = json.dumps(datos, indent=4, ensure_ascii=False)
    texto = _compactar_coords_json(texto)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    
    if modificado:
        print(f"  CONVERTIDO: {ruta.name}")
    else:
        print(f"  compactado: {ruta.name}")

    return True


def main():
    raiz = Path(__file__).parent.parent / 'ejemplos'
    archivos = sorted(raiz.rglob('*.json'))

    # Excluir outputs
    archivos = [a for a in archivos if 'outputs' not in a.parts and 'ejemplo_output' not in a.name]

    print(f"Archivos a procesar: {len(archivos)}\n")
    total = 0
    for a in archivos:
        if convertir_archivo(a):
            total += 1

    print(f"\nTotal convertidos: {total}")


if __name__ == '__main__':
    main()
