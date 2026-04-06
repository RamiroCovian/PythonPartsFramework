"""
Script para convertir todos los ejemplos JSON al nuevo formato:
1. techo: objeto -> array
2. Agregar tubos_is (inventados) basados en las subdivisiones IS
3. Agregar descripcion a obstaculos
4. Convertir un orden_obligatorio a orden_libre (solo en caminos con 2+ obligatorios)

NO modifica archivos que ya tienen techo como array.
"""
import json
import os
import re
import sys
from pathlib import Path


def generar_tubos_is(subdivisiones):
    """Genera tubos_is inventados para cada IS."""
    tubos = []
    tid = 1
    for is_data in subdivisiones:
        is_id = is_data.get('id', f'IS{tid}')
        verts = is_data['vertices']
        xs = [v['x'] for v in verts]
        ys = [v['y'] for v in verts]
        zs = [v['z'] for v in verts]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        z_avg = sum(zs) / len(zs)
        # Z del eje: techo + offset (~148mm para extraccion_impulsion)
        z_eje = z_avg + 150
        
        margen = 50
        x0 = x_min + margen
        x1 = x_max - margen
        y0 = y_min + margen
        y1 = y_max - margen
        
        alto = y1 - y0
        if alto < 200:
            continue
            
        # Crear 2-3 tubos horizontales por IS dependiendo del alto
        n_tubos = 2 if alto < 1000 else 3
        step = alto / (n_tubos + 1)
        
        for i in range(n_tubos):
            y_tubo = round(y0 + step * (i + 1), 1)
            tubos.append({
                "id": f"T{tid}",
                "is_id": is_id,
                "punto_inicio": {"x": round(x0, 1), "y": y_tubo, "z": round(z_eje, 1)},
                "punto_fin": {"x": round(x1, 1), "y": y_tubo, "z": round(z_eje, 1)}
            })
            tid += 1
    
    return tubos


def agregar_descripcion_obstaculos(obstaculos):
    """Agrega descripcion a obstaculos que no la tienen."""
    for i, obs in enumerate(obstaculos):
        if 'descripcion' not in obs:
            obs_id = obs.get('id', f'Obs_{i+1}')
            verts = obs.get('vertices', [])
            if verts:
                xs = [v['x'] for v in verts]
                ys = [v['y'] for v in verts]
                cx = (min(xs) + max(xs)) / 2
                cy = (min(ys) + max(ys)) / 2
                obs['descripcion'] = f"Obstáculo {obs_id} centrado en ({cx:.0f}, {cy:.0f})"
    return obstaculos


def convertir_un_obligatorio_a_libre(nodos):
    """Convierte un orden_obligatorio a orden_libre (el del medio si hay varios)."""
    obligatorios = [(i, n) for i, n in enumerate(nodos) if n.get('tipo') == 'orden_obligatorio']
    
    if len(obligatorios) < 2:
        return nodos  # No convertir si hay 0 o 1 obligatorio
    
    # Convertir el del medio
    idx_medio = len(obligatorios) // 2
    pos, nodo = obligatorios[idx_medio]
    
    # Guardar ID original y los vecinos
    old_id = nodo['id']
    prev_ids = nodo.get('anteriores', [])
    next_ids = nodo.get('siguientes', [])
    
    # Cambiar tipo a libre
    new_id = old_id.replace('O', 'L', 1) if old_id.startswith('O') else f'L_{old_id}'
    nodo['id'] = new_id
    nodo['tipo'] = 'orden_libre'
    nodo['anteriores'] = []
    nodo['siguientes'] = []
    
    # Re-encadenar: el nodo anterior debe apuntar al siguiente del libre
    for n in nodos:
        # Actualizar siguientes que apuntaban al viejo ID
        if old_id in n.get('siguientes', []):
            n['siguientes'] = [next_ids[0] if next_ids else s for s in n['siguientes'] if s != old_id]
            if next_ids and next_ids[0] not in n['siguientes']:
                n['siguientes'].append(next_ids[0])
        # Actualizar anteriores que apuntaban al viejo ID
        if old_id in n.get('anteriores', []):
            n['anteriores'] = [prev_ids[0] if prev_ids else s for s in n['anteriores'] if s != old_id]
            if prev_ids and prev_ids[0] not in n['anteriores']:
                n['anteriores'].append(prev_ids[0])
    
    return nodos


def convertir_archivo(filepath):
    """Convierte un archivo JSON al nuevo formato."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modificado = False
    
    # 1. Techo: objeto -> array
    techo = data.get('techo')
    if techo and not isinstance(techo, list):
        data['techo'] = [techo]
        modificado = True
    
    # 2. Agregar tubos_is si no existe
    if 'tubos_is' not in data and 'subdivisiones_is' in data:
        tubos = generar_tubos_is(data['subdivisiones_is'])
        if tubos:
            # Insertar tubos_is despues de subdivisiones_is
            new_data = {}
            for key, val in data.items():
                new_data[key] = val
                if key == 'subdivisiones_is':
                    new_data['tubos_is'] = tubos
            data = new_data
            modificado = True
    
    # 3. Descripcion en obstaculos
    if 'obstaculos' in data:
        had_desc = any('descripcion' in o for o in data['obstaculos'])
        agregar_descripcion_obstaculos(data['obstaculos'])
        if not had_desc and data['obstaculos']:
            modificado = True
    
    # 4. Convertir un obligatorio a libre
    if 'caminos' in data:
        # Multi-camino: convertir en el primer camino que tenga 2+ obligatorios
        converted = False
        for camino in data['caminos']:
            nodos = camino.get('nodos', [])
            obligs = [n for n in nodos if n.get('tipo') == 'orden_obligatorio']
            if len(obligs) >= 2 and not converted:
                convertir_un_obligatorio_a_libre(nodos)
                converted = True
                modificado = True
    elif 'nodos' in data:
        # Single-camino
        nodos = data['nodos']
        obligs = [n for n in nodos if n.get('tipo') == 'orden_obligatorio']
        if len(obligs) >= 2:
            # Check if already has a libre
            has_libre = any(n.get('tipo') == 'orden_libre' for n in nodos)
            if not has_libre:
                convertir_un_obligatorio_a_libre(nodos)
                modificado = True
    
    if modificado:
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        # Compactar coordenadas {x, y, z} a una sola linea
        pattern = r'\{\s*\n\s*"x":\s*([^,\n]+),\s*\n\s*"y":\s*([^,\n]+),\s*\n\s*"z":\s*([^\n\}]+)\s*\n\s*\}'
        json_str = re.sub(pattern, r'{ "x": \1, "y": \2, "z": \3 }', json_str)
        # Compactar punto_inicio/punto_fin objetos a una linea
        pattern2 = r'"(punto_inicio|punto_fin)":\s*\{\s*"x":\s*([^,]+),\s*"y":\s*([^,]+),\s*"z":\s*([^\}]+)\}'
        json_str = re.sub(pattern2, r'"\1": { "x": \2, "y": \3, "z": \4}', json_str)
        # Compactar tubos_is entries a una linea cada uno
        pattern3 = r'\{\s*"id":\s*"(T\d+)",\s*"is_id":\s*"(IS\d+)",\s*"punto_inicio":\s*\{([^}]+)\},\s*"punto_fin":\s*\{([^}]+)\}\s*\}'
        json_str = re.sub(pattern3, r'{ "id": "\1", "is_id": "\2", "punto_inicio": {\3}, "punto_fin": {\4} }', json_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str + '\n')
        return True
    return False


OFFSETS = {
    'extraccion_impulsion': 147.5,  # distancia_techo(110) + radio(37.5)
    'aislado': 190.0,               # distancia_techo(110) + radio(80)
    'recuperador': 190.0,           # distancia_techo(110) + radio(80)
}


def fix_z_nodos(filepath):
    """Corrige Z de todos los nodos para que estén a la altura del eje del tubo.
    Z_eje = Z_techo + offset_subtipo."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Obtener Z del techo (primer vertice del primer techo)
    techo = data.get('techo', [])
    if isinstance(techo, list):
        z_techo = techo[0]['vertices'][0]['z']
    else:
        z_techo = techo['vertices'][0]['z']
    
    # Obtener subtipo
    config = data.get('configuracion', {})
    subtipo = config.get('subtipo_tuberia', 'extraccion_impulsion').lower()
    offset = OFFSETS.get(subtipo, 147.5)
    z_eje = z_techo + offset
    
    modificado = False
    
    def fix_nodo(nodo):
        nonlocal modificado
        coords = nodo.get('coordenadas', {})
        if 'z' in coords:
            old_z = coords['z']
            # Solo corregir si Z está al nivel del techo o por debajo del eje
            if abs(old_z - z_techo) < 1.0 or old_z < z_eje - 0.1:
                coords['z'] = z_eje
                if old_z != z_eje:
                    modificado = True
    
    # Multi-camino
    if 'caminos' in data:
        for camino in data['caminos']:
            for nodo in camino.get('nodos', []):
                fix_nodo(nodo)
    
    # Single-camino
    if 'nodos' in data:
        for nodo in data['nodos']:
            fix_nodo(nodo)
    
    if modificado:
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        # Compactar coordenadas
        pattern = r'\{\s*\n\s*"x":\s*([^,\n]+),\s*\n\s*"y":\s*([^,\n]+),\s*\n\s*"z":\s*([^\n\}]+)\s*\n\s*\}'
        json_str = re.sub(pattern, r'{ "x": \1, "y": \2, "z": \3 }', json_str)
        pattern3 = r'\{\s*"id":\s*"(T\d+)",\s*"is_id":\s*"(IS\d+)",\s*"punto_inicio":\s*\{([^}]+)\},\s*"punto_fin":\s*\{([^}]+)\}\s*\}'
        json_str = re.sub(pattern3, r'{ "id": "\1", "is_id": "\2", "punto_inicio": {\3}, "punto_fin": {\4} }', json_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str + '\n')
        return True, subtipo, z_techo, z_eje
    return False, subtipo, z_techo, z_eje


def compactar_json(filepath):
    """Re-lee y re-escribe un JSON con coordenadas compactadas.
    Tambien corrige techo doblemente anidado [[{...}]] -> [{...}]."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fix double-wrapped techo
    techo = data.get('techo')
    if isinstance(techo, list) and len(techo) == 1 and isinstance(techo[0], list):
        data['techo'] = techo[0]
    
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    # Compactar coordenadas {x, y, z} a una sola linea
    pattern = r'\{\s*\n\s*"x":\s*([^,\n]+),\s*\n\s*"y":\s*([^,\n]+),\s*\n\s*"z":\s*([^\n\}]+)\s*\n\s*\}'
    json_str = re.sub(pattern, r'{ "x": \1, "y": \2, "z": \3 }', json_str)
    # Compactar tubos_is entries a una linea
    pattern3 = r'\{\s*"id":\s*"(T\d+)",\s*"is_id":\s*"(IS\d+)",\s*"punto_inicio":\s*\{([^}]+)\},\s*"punto_fin":\s*\{([^}]+)\}\s*\}'
    json_str = re.sub(pattern3, r'{ "id": "\1", "is_id": "\2", "punto_inicio": {\3}, "punto_fin": {\4} }', json_str)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(json_str + '\n')


def main():
    base = Path(__file__).parent.parent / 'ejemplos'
    mode = sys.argv[1] if len(sys.argv) > 1 else 'compact'
    
    # Encontrar todos los JSON de ejemplo (excluir outputs)
    json_files = []
    for pattern in ['basico/*.json', 'hibrido/*.json', 'real/*.json', 'ejemplo_input.json']:
        json_files.extend(base.glob(pattern))
    
    print(f"Encontrados {len(json_files)} archivos JSON (modo: {mode})")
    
    converted = 0
    skipped = 0
    for fp in sorted(json_files):
        rel = fp.relative_to(base)
        try:
            if mode == 'compact':
                compactar_json(fp)
                print(f"  [OK] {rel}")
                converted += 1
            elif mode == 'fix_z':
                ok, subtipo, z_techo, z_eje = fix_z_nodos(fp)
                if ok:
                    print(f"  [OK] {rel} ({subtipo}: Z {z_techo} -> {z_eje})")
                    converted += 1
                else:
                    print(f"  [--] {rel} ({subtipo}: Z ya correcto)")
                    skipped += 1
            else:
                if convertir_archivo(fp):
                    print(f"  [OK] {rel}")
                    converted += 1
                else:
                    print(f"  [--] {rel} (sin cambios)")
                    skipped += 1
        except Exception as e:
            print(f"  [ERR] {rel}: {e}")
    
    print(f"\nProcesados: {converted}, Sin cambios: {skipped}")


if __name__ == '__main__':
    main()
