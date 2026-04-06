"""
Cargador de datos desde archivos JSON.

Modulo delgado: carga el JSON, delega el procesamiento a procesamiento/,
y se encarga de guardar los outputs (HTML, Markdown, grafo IS).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

from .reportes import generar_resultado_markdown
from .procesamiento import procesar_datos


def cargar_ejemplo(archivo_json: str) -> Dict[str, Any]:
    """Carga un ejemplo desde un archivo JSON."""
    with open(archivo_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def ejecutar_desde_json(archivo_json: str, mostrar: bool = True, guardar: bool = True):
    """
    Ejecuta el procesamiento completo desde un archivo JSON.
    
    Args:
        archivo_json: Ruta al archivo JSON
        mostrar: Si True, abre la visualizacion en el navegador
        guardar: Si True, guarda el HTML en outputs/
        
    Returns:
        Visualizador3D generado (o None si fallo)
    """
    # Cargar datos
    datos = cargar_ejemplo(archivo_json)
    
    # Procesar
    from .algoritmos.general.algoritmo import BajarImposibleError
    try:
        vis, resultado, grafo_is = procesar_datos(datos)
    except BajarImposibleError as e:
        print(f"\n  *** {e}")
        print("\n  El proceso se detuvo. No se genera visualización.\n")
        return None
    
    # Guardar HTML, Markdown y grafo IS
    output_html = None
    if guardar:
        archivo_json_path = Path(archivo_json)
        output_dir = archivo_json_path.parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        # Guardar HTML
        nombre_html = archivo_json_path.stem + ".html"
        output_html = output_dir / nombre_html
        vis.guardar_html(str(output_html))
        print(f"\nArchivo guardado: {output_html}")
        
        # Guardar Markdown con el reporte
        if resultado:
            nombre_md = archivo_json_path.stem + ".md"
            output_md = output_dir / nombre_md
            
            # Extraer config del subtipo para el reporte
            from .procesamiento import obtener_config_subtipo
            config = datos.get('configuracion', {})
            subtipo = config.get('subtipo_tuberia', 'extraccion_impulsion').lower()
            config_subtipo = obtener_config_subtipo(subtipo)
            subtipo_obj = config_subtipo['subtipo_obj']
            
            contenido_md = generar_resultado_markdown(
                resultado=resultado,
                nombre_ejemplo=datos.get('nombre', 'Sin Nombre'),
                subtipo=subtipo,
                angulos_codo=subtipo_obj.angulos_permitidos if subtipo_obj else [],
                angulo_movimiento=config_subtipo['angulo_giro']
            )
            
            # Agregar seccion de soportes al MD si existen
            soportes_lista = None
            if grafo_is:
                # Single-camino: soportes en grafo_is['soportes']
                soportes_lista = grafo_is.get('soportes')
                # Multi-camino: soportes por camino en grafo_is['caminos'][i]['soportes']
                if not soportes_lista and 'caminos' in grafo_is:
                    soportes_lista = []
                    for cam in grafo_is.get('caminos', []):
                        soportes_lista.extend(cam.get('soportes', []))
            
            if soportes_lista:
                n_h = sum(1 for s in soportes_lista if s.get('tipo') == 'horizontal')
                n_v = sum(1 for s in soportes_lista if s.get('tipo') == 'vertical')
                n_std = sum(1 for s in soportes_lista if s.get('subtipo') == 'Ventilación')
                n_var = sum(1 for s in soportes_lista if s.get('subtipo') == 'VARIFIX')
                lineas_sp = [
                    "",
                    "### Soportes de Ventilación",
                    "",
                    f"**Total:** {len(soportes_lista)} soportes "
                    f"(horizontal={n_h}, vertical={n_v} | OMEGA={n_std}, ZETA={n_var})",
                    "",
                    "| Orientación | Subtipo | Posición 1 | Posición 2 | A (mm) | B (mm) |",
                    "|-------------|---------|------------|------------|--------|--------|",
                ]
                for sp in soportes_lista:
                    p1 = sp['posicion1']
                    p2 = sp['posicion2']
                    lineas_sp.append(
                        f"| {sp.get('tipo','')} | {sp.get('subtipo','')} "
                        f"| ({p1[0]:.0f},{p1[1]:.0f},{p1[2]:.0f}) "
                        f"| ({p2[0]:.0f},{p2[1]:.0f},{p2[2]:.0f}) "
                        f"| {sp.get('cota_a','')} | {sp.get('cota_b','')} |"
                    )
                contenido_md += "\n" + "\n".join(lineas_sp)
            
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(contenido_md)
            
            print(f"Reporte guardado: {output_md}")
        
        # Guardar grafo IS como JSON (con coordenadas compactas)
        # IMPORTANTE: Si es multi-camino y hay caminos invalidos, NO generar JSON
        # ya que seria consumido por otro programa que renderizaria datos invalidos
        es_multicamino = 'caminos' in datos and datos.get('caminos')
        generar_json = True
        
        if es_multicamino and resultado and not resultado.es_valido:
            generar_json = False
            print(f"\n*** ATENCION: Multi-camino con caminos INVALIDOS ***")
            print(f"*** NO se genera JSON de salida (seria consumido con datos invalidos) ***")
            # Igual guardamos el HTML para debug/visualizacion
            print(f"*** HTML guardado para depuracion: {output_html} ***")
        
        if grafo_is and generar_json:
            nombre_grafo = archivo_json_path.stem + "_grafo.json"
            output_grafo = output_dir / nombre_grafo
            with open(output_grafo, 'w', encoding='utf-8') as f:
                json_str = json.dumps(grafo_is, indent=2, ensure_ascii=False)
                # Compactar objetos coordenadas de 5 lineas a 1
                pattern = r'\{\n\s+"x":\s*([^,\n]+),\n\s+"y":\s*([^,\n]+),\n\s+"z":\s*([^\n\}]+)\n\s+\}'
                json_str = re.sub(pattern, r'{ "x": \1, "y": \2, "z": \3 }', json_str)
                # Compactar segmentos a una linea
                pattern_seg = r'\{\n\s+"id":\s*(\d+),\n\s+"n1_id":\s*"([^"]+)",\n\s+"n2_id":\s*"([^"]+)",\n\s+"IS":\s*("IS\d+"|null)\n\s+\}'
                json_str = re.sub(pattern_seg, r'{ "id": \1, "n1_id": "\2", "n2_id": "\3", "IS": \4 }', json_str)
                # Compactar anteriores/siguientes arrays a una linea
                pattern_arr = r'"(anteriores|siguientes)":\s*\[\s*\n\s*((?:"[^"]*"(?:,\s*\n\s*"[^"]*")*)?)\s*\n\s*\]'
                def _compact_arr(m):
                    key = m.group(1)
                    items = m.group(2).strip()
                    if not items:
                        return f'"{key}": []'
                    items_clean = re.sub(r'\s*\n\s*', ' ', items)
                    return f'"{key}": [{items_clean}]'
                json_str = re.sub(pattern_arr, _compact_arr, json_str)
                f.write(json_str)
            print(f"Grafo IS guardado: {output_grafo}")
    
    # Mostrar solo si la ruta es valida
    if mostrar:
        if resultado and resultado.es_valido:
            print("Abriendo visualizacion en navegador...")
            if guardar and output_html:
                import webbrowser
                webbrowser.open(str(output_html.resolve()))
            else:
                vis.mostrar()
        else:
            print("  Ruta INVALIDA - no se abre visualizacion.")
    
    return vis
