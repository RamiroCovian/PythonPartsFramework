"""
caminos_optimos - API publica de la libreria Caminos Optimos.

Sistema de optimizacion de rutas de tuberias de ventilacion bajo
techos inclinados. Implementa RRT* con restricciones de angulos de codo,
generacion de soportes, visualizacion 3D y exportacion de grafos IS.

USO RAPIDO:
    import caminos_optimos

    resultado = caminos_optimos.calcular("mi_proyecto.json")
    if resultado['exito']:
        print(f"Ruta VALIDA: {resultado['longitud_mm']:.0f} mm")
        print(f"Soportes generados: {resultado['num_soportes']}")
        print(f"HTML: {resultado['archivo_html']}")
        print(f"Grafo IS: {resultado['archivo_grafo_json']}")

USO AVANZADO:
    resultado = caminos_optimos.calcular(
        archivo_json  = "mi_proyecto.json",
        mostrar       = False,   # no abrir navegador
        guardar       = True,    # guardar outputs
    )
"""

import sys
import os

# --- Asegurar que src/ sea importable desde cualquier directorio de trabajo ---
_LIBRARY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _LIBRARY_ROOT not in sys.path:
    sys.path.insert(0, _LIBRARY_ROOT)

from src.cargador_json import cargar_ejemplo as _cargar_ejemplo

__version__ = "1.0.0"
__all__ = ["calcular", "obtener_version", "__version__"]


def obtener_version() -> str:
    """Devuelve la version instalada de la libreria."""
    return __version__


def calcular(
    archivo_json: str,
    mostrar: bool = False,
    guardar: bool = True,
) -> dict:
    """
    Ejecuta el pipeline completo de optimizacion de rutas de tuberias.

    Procesa un archivo JSON de entrada con la descripcion del espacio
    (techo, obstaculos, puntos de conexion, tubos IS) y calcula la ruta
    optima de la tuberia de ventilacion.

    Args:
        archivo_json: Ruta al archivo JSON de entrada.
                      Puede ser ruta absoluta o relativa al directorio
                      desde donde se ejecuta el script.
        mostrar:      Si True, abre la visualizacion 3D en el navegador
                      al finalizar. Default: False.
        guardar:      Si True, guarda los archivos de salida en
                      <directorio_json>/../outputs/:
                        - <nombre>.html    (visualizacion 3D interactiva)
                        - <nombre>.md      (reporte Markdown)
                        - <nombre>_grafo.json (grafo IS con soportes)
                      Default: True.

    Returns:
        Diccionario con el resultado:
        {
            'exito':            bool,   # True si el proceso finalizo sin excepciones
            'valido':           bool,   # True si la ruta calculada es geometricamente valida
            'longitud_mm':      float,  # Longitud total de la tuberia en mm
            'num_soportes':     int,    # Cantidad de soportes generados
            'archivo_html':     str,    # Ruta al HTML generado (o None)
            'archivo_md':       str,    # Ruta al MD generado (o None)
            'archivo_grafo_json': str,  # Ruta al JSON del grafo IS (o None)
            'visualizador':     obj,    # Objeto Visualizador3D (uso avanzado)
            'error':            str,    # Mensaje de error (si exito=False)
        }

    Raises:
        No lanza excepciones. Todos los errores se capturan y se
        devuelven en resultado['error'].
    """
    from pathlib import Path

    try:
        # Cargar y procesar directamente para tener acceso al grafo IS
        datos = _cargar_ejemplo(archivo_json)
        from src.procesamiento import procesar_datos
        from src.algoritmos.general.algoritmo import BajarImposibleError
        try:
            vis, resultado, grafo_is = procesar_datos(datos)
        except BajarImposibleError as e:
            return {
                'exito': False, 'valido': False, 'longitud_mm': 0.0,
                'num_soportes': 0, 'archivo_html': None, 'archivo_md': None,
                'archivo_grafo_json': None, 'visualizador': None,
                'error': str(e),
            }

        # Determinar rutas de salida
        p = Path(archivo_json)
        output_dir = p.parent.parent / "outputs"
        stem = p.stem

        html_path  = str(output_dir / f"{stem}.html")          if guardar else None
        md_path    = str(output_dir / f"{stem}.md")            if guardar else None
        grafo_path = str(output_dir / f"{stem}_grafo.json")    if guardar else None

        # Metricas directas desde el pipeline (sin depender de archivos)
        valido      = resultado.es_valido if resultado else False
        longitud_mm = resultado.longitud_total if resultado else 0.0

        soportes = []
        if grafo_is:
            soportes = grafo_is.get('soportes', [])
            if not soportes and 'caminos' in grafo_is:
                for cam in grafo_is.get('caminos', []):
                    soportes += cam.get('soportes', [])
        num_soportes = len(soportes)

        # Guardar outputs si se solicita
        if guardar and resultado:
            _guardar_outputs(
                archivo_json=archivo_json, datos=datos, vis=vis,
                resultado=resultado, grafo_is=grafo_is,
                output_dir=output_dir, stem=stem
            )

        if mostrar and vis and valido:
            if guardar and html_path and Path(html_path).exists():
                import webbrowser
                webbrowser.open(str(Path(html_path).resolve()))
            else:
                vis.mostrar()

        return {
            'exito':              True,
            'valido':             valido,
            'longitud_mm':        longitud_mm,
            'num_soportes':       num_soportes,
            'archivo_html':       html_path,
            'archivo_md':         md_path,
            'archivo_grafo_json': grafo_path,
            'visualizador':       vis,
            'error':              None,
        }

    except Exception as e:  # noqa: BLE001
        import traceback
        return {
            'exito':              False,
            'valido':             False,
            'longitud_mm':        0.0,
            'num_soportes':       0,
            'archivo_html':       None,
            'archivo_md':         None,
            'archivo_grafo_json': None,
            'visualizador':       None,
            'error':              str(e),
            'traceback':          traceback.format_exc(),
        }


def _guardar_outputs(archivo_json, datos, vis, resultado, grafo_is,
                     output_dir, stem):
    """Guarda HTML, Markdown y JSON de grafo IS en output_dir."""
    import json, re
    from pathlib import Path
    from src.reportes import generar_resultado_markdown
    from src.procesamiento import obtener_config_subtipo

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # HTML
    html_path = output_dir / f"{stem}.html"
    vis.guardar_html(str(html_path))

    # Markdown
    config = datos.get('configuracion', {})
    subtipo = config.get('subtipo_tuberia', 'extraccion_impulsion').lower()
    cfg = obtener_config_subtipo(subtipo)
    subtipo_obj = cfg['subtipo_obj']
    contenido_md = generar_resultado_markdown(
        resultado=resultado,
        nombre_ejemplo=datos.get('nombre', 'Sin Nombre'),
        subtipo=subtipo,
        angulos_codo=subtipo_obj.angulos_permitidos if subtipo_obj else [],
        angulo_movimiento=cfg['angulo_giro'],
    )
    # Seccion de soportes
    soportes_lista = []
    if grafo_is:
        soportes_lista = grafo_is.get('soportes', [])
        if not soportes_lista and 'caminos' in grafo_is:
            for cam in grafo_is.get('caminos', []):
                soportes_lista += cam.get('soportes', [])
    if soportes_lista:
        n_h = sum(1 for s in soportes_lista if s.get('tipo') == 'horizontal')
        n_v = sum(1 for s in soportes_lista if s.get('tipo') == 'vertical')
        lineas = [
            "", "### Soportes de Ventilacion", "",
            f"**Total:** {len(soportes_lista)} (H={n_h}, V={n_v})", "",
            "| Orientacion | Subtipo | Posicion 1 | Posicion 2 | A (mm) | B (mm) |",
            "|-------------|---------|------------|------------|--------|--------|",
        ]
        for sp in soportes_lista:
            p1, p2 = sp['posicion1'], sp['posicion2']
            lineas.append(
                f"| {sp.get('tipo','')} | {sp.get('subtipo','')} "
                f"| ({p1[0]:.0f},{p1[1]:.0f},{p1[2]:.0f}) "
                f"| ({p2[0]:.0f},{p2[1]:.0f},{p2[2]:.0f}) "
                f"| {sp.get('cota_a','')} | {sp.get('cota_b','')} |"
            )
        contenido_md += "\n" + "\n".join(lineas)
    with open(output_dir / f"{stem}.md", 'w', encoding='utf-8') as f:
        f.write(contenido_md)

    # Grafo IS JSON
    es_multicamino = 'caminos' in datos and datos.get('caminos')
    if grafo_is and (resultado.es_valido or not es_multicamino):
        json_str = json.dumps(grafo_is, indent=2, ensure_ascii=False)
        pattern = r'\{\n\s+"x":\s*([^,\n]+),\n\s+"y":\s*([^,\n]+),\n\s+"z":\s*([^\n\}]+)\n\s+\}'
        json_str = re.sub(pattern, r'{ "x": \1, "y": \2, "z": \3 }', json_str)
        with open(output_dir / f"{stem}_grafo.json", 'w', encoding='utf-8') as f:
            f.write(json_str)
