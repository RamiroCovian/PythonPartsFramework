"""
Algoritmo GENERAL de pathfinding para tuberias.

Soporta cualquier combinacion de angulos permitidos (45, 90, 60, etc.)
y multiples modos de evasion por obstaculo (saltar, rodear, bajar).
"""

from .algoritmo import calcular_ruta_general

__all__ = ['calcular_ruta_general']
