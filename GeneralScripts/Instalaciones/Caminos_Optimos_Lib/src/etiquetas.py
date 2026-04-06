"""
Utilidades de etiquetado con subindices Unicode para puntos del sistema.

Formato:
  - label_sub('A', 1)       -> 'A₁'
  - label_sub('C', 1, 2)    -> 'C₁₋₂'
  - label_sub('U', 2, 3)    -> 'U₂₋₃'
  - label_sub('A')           -> 'A'
"""

_SUB_DIGITS = '₀₁₂₃₄₅₆₇₈₉'


def to_subscript(n) -> str:
    """Convierte un numero entero a su representacion en subindice Unicode."""
    return ''.join(_SUB_DIGITS[int(d)] for d in str(n))


def label_sub(letra: str, camino_idx: int = None, item_idx: int = None) -> str:
    """
    Genera etiqueta con subindices Unicode.
    
    Sin camino_idx: devuelve la letra tal cual.
    Solo camino_idx: X₁
    Ambos: X₁₋₂
    """
    if camino_idx is None:
        return letra
    if item_idx is None:
        return f"{letra}{to_subscript(camino_idx)}"
    return f"{letra}{to_subscript(camino_idx)}₋{to_subscript(item_idx)}"
