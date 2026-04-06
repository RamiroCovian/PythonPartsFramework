"""
Funciones de reporte y estructuras de resultado para el sistema de tuberias.

Contiene las dataclasses ResultadoCamino y Segmento, y funciones para
generar reportes en consola y Markdown.
"""

import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from .modelos.punto import Punto3D


def calcular_distancia(p1: Punto3D, p2: Punto3D) -> float:
    """Calcula la distancia euclidiana entre dos puntos."""
    return np.sqrt(
        (p2.x - p1.x)**2 + 
        (p2.y - p1.y)**2 + 
        (p2.z - p1.z)**2
    )


@dataclass
class Segmento:
    """Representa un segmento del camino."""
    inicio: Punto3D
    fin: Punto3D
    longitud: float
    
    @classmethod
    def desde_puntos(cls, p1: Punto3D, p2: Punto3D) -> 'Segmento':
        longitud = calcular_distancia(p1, p2)
        return cls(inicio=p1, fin=p2, longitud=longitud)


@dataclass
class ResultadoCamino:
    """Resultado del calculo del camino."""
    puntos: List[Punto3D]
    segmentos: List[Segmento]
    longitud_total: float
    puntos_obligatorios_visitados: List[Punto3D]
    puntos_libres_visitados: List[Punto3D]
    es_valido: bool
    mensaje: str = ""
    num_conectores_inicio: int = 0
    num_conectores_fin: int = 0


def obtener_nombre_punto(punto: Punto3D, indice_codo: int = 0) -> str:
    """Obtiene el nombre corto de un punto para mostrar en segmentos."""
    if punto.id:
        # Limpiar el ID para formato corto
        id_limpio = punto.id.replace("codo_", "C")
        return id_limpio
    return f"C{indice_codo}"


def generar_resultado_markdown(resultado: ResultadoCamino, nombre_ejemplo: str, subtipo: str, angulos_codo: list, angulo_movimiento: int) -> str:
    """Genera un resumen del resultado en formato Markdown."""
    from datetime import datetime
    
    lineas = [
        f"# {nombre_ejemplo}",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Configuración",
        "",
        f"- **Subtipo:** {subtipo}",
        f"- **Ángulos de codo permitidos:** {angulos_codo}",
        f"- **Ángulo de movimiento (pathfinding):** {angulo_movimiento}°",
        "",
        "## Resultado",
        "",
        f"**Estado:** {'✅ VÁLIDO' if resultado.es_valido else '❌ INVÁLIDO'}",
        "",
    ]
    
    # Tabla de segmentos
    lineas.append("### Segmentos del Camino")
    lineas.append("")
    lineas.append("| Segmento | Longitud | Ángulo |")
    lineas.append("|----------|----------|--------|")
    
    consumo_total = 0.0
    puntos = resultado.puntos
    
    for i, seg in enumerate(resultado.segmentos):
        nombre_inicio = obtener_nombre_punto(seg.inicio)
        nombre_fin = obtener_nombre_punto(seg.fin)
        nombre_segmento = f"{nombre_inicio}-{nombre_fin}"
        
        # Calcular angulo con segmento anterior
        angulo_str = "-"
        if i > 0 and i < len(puntos) - 1:
            p1 = puntos[i-1]
            p2 = puntos[i]
            p3 = puntos[i+1]
            
            v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
            v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
            
            norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if norm1 > 0.1 and norm2 > 0.1:
                cos_ang = np.dot(v1, v2) / (norm1 * norm2)
                cos_ang = np.clip(cos_ang, -1, 1)
                angulo = np.degrees(np.arccos(cos_ang))
                angulo_interno = 180 - angulo
                angulo_str = f"{angulo_interno:.2f}°"
        
        lineas.append(f"| {nombre_segmento} | {seg.longitud:.1f} mm | {angulo_str} |")
        consumo_total += seg.longitud
    
    lineas.append("")
    lineas.append(f"**Consumo Total:** {consumo_total:.1f} mm ({consumo_total/1000:.2f} m)")
    lineas.append("")
    
    # Puntos obligatorios
    if resultado.puntos_obligatorios_visitados:
        lineas.append("### Puntos Obligatorios (orden de prioridad)")
        lineas.append("")
        for i, p in enumerate(resultado.puntos_obligatorios_visitados, 1):
            lineas.append(f"{i}. **{p.id}** en `({p.x:.0f}, {p.y:.0f}, {p.z:.0f})`")
        lineas.append("")
    
    # Puntos libres
    if resultado.puntos_libres_visitados:
        lineas.append("### Puntos Libres Visitados")
        lineas.append("")
        for p in resultado.puntos_libres_visitados:
            lineas.append(f"- **{p.id}** en `({p.x:.0f}, {p.y:.0f}, {p.z:.0f})`")
        lineas.append("")
    
    return "\n".join(lineas)


def imprimir_resultado(resultado: ResultadoCamino) -> str:
    """Genera un resumen del resultado del camino."""
    lineas = [
        "",
        "=" * 60,
        "RESULTADO DEL CALCULO DE CAMINO",
        "=" * 60,
        f"Estado: {'VALIDO' if resultado.es_valido else 'INVALIDO'}",
        "",
    ]
    
    # Detalle de segmentos con formato solicitado
    lineas.append("SEGMENTOS DEL CAMINO:")
    lineas.append("-" * 55)
    lineas.append(f"  {'Segmento':16} {'Longitud':>10}   {'Angulo':>8}")
    lineas.append("-" * 55)
    
    consumo_total = 0.0
    puntos = resultado.puntos
    
    for i, seg in enumerate(resultado.segmentos):
        nombre_inicio = obtener_nombre_punto(seg.inicio)
        nombre_fin = obtener_nombre_punto(seg.fin)
        nombre_segmento = f"{nombre_inicio}-{nombre_fin}"
        
        # Calcular angulo con segmento anterior
        angulo_str = "-"
        if i > 0 and i < len(puntos) - 1:
            p1 = puntos[i-1]
            p2 = puntos[i]
            p3 = puntos[i+1]
            
            v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
            v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
            
            norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if norm1 > 0.1 and norm2 > 0.1:
                cos_ang = np.dot(v1, v2) / (norm1 * norm2)
                cos_ang = np.clip(cos_ang, -1, 1)
                angulo = np.degrees(np.arccos(cos_ang))
                angulo_interno = 180 - angulo
                angulo_str = f"{angulo_interno:.1f}°"
        
        lineas.append(f"  {nombre_segmento:16} {seg.longitud:8.1f} mm   {angulo_str:>8}")
        consumo_total += seg.longitud
    
    lineas.append("-" * 40)
    lineas.append(f"  CONSUMO TOTAL DE TUBO:      {consumo_total:10.1f} mm")
    lineas.append(f"                              {consumo_total/1000:10.2f} m")
    lineas.append("=" * 60)
    
    # Info adicional
    lineas.append("")
    lineas.append("PUNTOS OBLIGATORIOS (orden de prioridad):")
    for i, p in enumerate(resultado.puntos_obligatorios_visitados, 1):
        lineas.append(f"  {i}. {p.id} en ({p.x:.0f}, {p.y:.0f}, {p.z:.0f})")
    
    if resultado.puntos_libres_visitados:
        lineas.append("")
        lineas.append("PUNTOS LIBRES VISITADOS:")
        for p in resultado.puntos_libres_visitados:
            lineas.append(f"  - {p.id} en ({p.x:.0f}, {p.y:.0f}, {p.z:.0f})")
    
    lineas.append("")
    
    return "\n".join(lineas)
