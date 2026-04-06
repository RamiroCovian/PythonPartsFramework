# -*- coding: utf-8 -*-
"""
Catálogo de elementos definidos por instalación.
Relaciona cada tipo de elemento con las funciones (inicio, final, intermedio, bifurcación)
en las que puede colocarse. Incluye condiciones por defecto cuando aplican.
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional, Tuple

from .base import POSIBLES_FUNCIONES


# Claves internas de tipo de elemento (coinciden con element_type en marcadores)
T_SORTIDA = "t_sortida"
COLZE_BASE = "colze_base"
CLAU_DE_PAS = "clau_de_pas"
TAPON = "taps"

# Etiquetas para ComboBox / UI
LABELS_AGUA: Dict[str, str] = {
    T_SORTIDA: "T sortida",
    COLZE_BASE: "Colze base",
    CLAU_DE_PAS: "Clau de Pas",
    TAPON: "Tapón",
}

# Etiquetas para el ComboBox "Tipo de punto" (ubicación)
LABELS_FUNCION: Dict[str, str] = {
    "inicio": "Inicio",
    "final": "Final",
    "intermedio_ordenado": "Intermedio ordenado",
    "intermedio_libre": "Intermedio libre",
    "bifurcación": "Bifurcación",
}


def get_funciones_por_elemento(instalacion: str) -> Dict[str, List[str]]:
    """
    Devuelve para cada elemento de la instalación la lista de funciones (tipos de punto)
    donde puede colocarse. Ej.: T sortida → [inicio, final]; Clau de Pas → [intermedio_libre].
    """
    if instalacion.upper() == "AGUA" or instalacion.lower() == "agua":
        # Agua:
        # - T sortida: solo intermedio (ordenado / libre)
        # - Colze base: solo Inicio / Final
        # - Clau de Pas: solo intermedio (ordenado / libre)
        # - Tapón: solo Inicio / Final
        return {
            T_SORTIDA: ["intermedio_ordenado", "intermedio_libre"],
            COLZE_BASE: ["inicio", "final"],
            CLAU_DE_PAS: ["intermedio_ordenado", "intermedio_libre"],
            TAPON: ["inicio", "final"],
        }
    # Electricidad: ej. interruptor/enchufe/luz → final; caja conexiones → varias; etc.
    if instalacion.upper() == "ELECTRICIDAD":
        return {
            "interruptor": ["final"],
            "enchufe": ["final"],
            "luz": ["final"],
            "caja_conexiones": [
                "inicio",
                "final",
                "intermedio_ordenado",
                "intermedio_libre",
                "bifurcación",
            ],
            "difusor": ["final"],
            "manguito_vent": ["intermedio_ordenado", "intermedio_libre", "final"],
        }
    # Saneamiento / Clima: ampliar según catálogo
    return {}


def get_elementos_para_instalacion(instalacion: str) -> List[Dict[str, Any]]:
    """
    Lista de elementos definidos disponibles para una instalación, con sus funciones
    y opciones por defecto. Para alimentar el selector de elemento y el selector
    de tipo de punto en la UI.
    """
    funciones = get_funciones_por_elemento(instalacion)
    if instalacion.upper() == "AGUA" or instalacion.lower() == "agua":
        return [
            {
                "key": T_SORTIDA,
                "label": LABELS_AGUA[T_SORTIDA],
                "posibles_funciones": funciones.get(
                    T_SORTIDA, ["intermedio_ordenado", "intermedio_libre"]
                ),
                "funcion_defecto": "intermedio_libre",
                "solo_inicio_final": False,
                "solo_intermedio": True,
            },
            {
                "key": COLZE_BASE,
                "label": LABELS_AGUA[COLZE_BASE],
                "posibles_funciones": funciones.get(COLZE_BASE, ["inicio", "final"]),
                "funcion_defecto": "final",
                "solo_inicio_final": True,
                "solo_intermedio": False,
            },
            {
                "key": CLAU_DE_PAS,
                "label": LABELS_AGUA[CLAU_DE_PAS],
                "posibles_funciones": funciones.get(
                    CLAU_DE_PAS, ["intermedio_ordenado", "intermedio_libre"]
                ),
                "funcion_defecto": "intermedio_libre",
                "solo_inicio_final": False,
                "solo_intermedio": True,
            },
            {
                "key": TAPON,
                "label": LABELS_AGUA[TAPON],
                "posibles_funciones": funciones.get(TAPON, ["inicio", "final"]),
                "funcion_defecto": "final",
                "solo_inicio_final": True,
                "solo_intermedio": False,
            },
        ]
    if instalacion.upper() == "ELECTRICIDAD":
        items = []
        for key, func_list in funciones.items():
            label = key.replace("_", " ").title()
            solo_final = set(func_list) <= {"final"}
            solo_intermedio = set(func_list) <= {
                "intermedio_ordenado",
                "intermedio_libre",
            }
            items.append(
                {
                    "key": key,
                    "label": label,
                    "posibles_funciones": func_list,
                    "funcion_defecto": func_list[0] if func_list else "final",
                    "solo_inicio_final": not solo_intermedio
                    and "final" in func_list
                    or "inicio" in func_list,
                    "solo_intermedio": solo_intermedio,
                }
            )
        return items
    return []


def get_value_list_elementos(instalacion: str, separador: str = "|") -> str:
    """Cadena ValueList para el ComboBox de elemento (ej. 'T sortida|Colze base|Clau de Pas|Taps')."""
    items = get_elementos_para_instalacion(instalacion)
    return separador.join([e["label"] for e in items])


def get_value_list_tipo_punto(
    instalacion: str, element_label_or_key: str, separador: str = "|"
) -> str:
    """
    Devuelve la cadena ValueList para el ComboBox "Tipo de punto" según el elemento seleccionado.
    element_label_or_key: label de UI (ej. "T sortida") o key interna (ej. "t_sortida").
    """
    items = get_elementos_para_instalacion(instalacion)
    key = (element_label_or_key or "").strip()
    if instalacion.upper() == "AGUA":
        key = label_a_key_agua(key)
    else:
        for e in items:
            if (e.get("key") or "") == key or (e.get("label") or "").strip() == key:
                key = e["key"]
                break
    elem = next((e for e in items if e["key"] == key), None)
    if not elem:
        return separador.join(LABELS_FUNCION.get(f, f) for f in POSIBLES_FUNCIONES if f in LABELS_FUNCION)
    funcs = elem.get("posibles_funciones", [])
    return separador.join(LABELS_FUNCION.get(f, f) for f in funcs if f in LABELS_FUNCION)


def label_tipo_punto_to_funcion(label: str) -> str:
    """Convierte el valor del ComboBox tipo de punto (ej. 'Intermedio libre') a función interna (ej. 'intermedio_libre')."""
    s = (label or "").strip().lower()
    if not s:
        return "intermedio_libre"
    if s in ("inicio", "inicial"):
        return "inicio"
    if s in ("final", "fin"):
        return "final"
    if "ordenado" in s:
        return "intermedio_ordenado"
    if "libre" in s:
        return "intermedio_libre"
    if "bifurc" in s:
        return "bifurcación"
    return "intermedio_libre"


def validar_ubicacion_elemento(
    instalacion: str,
    element_key: str,
    funcion_seleccionada: str,
) -> Tuple[bool, Optional[str]]:
    """
    Valida si el elemento puede colocarse en la función seleccionada (inicio/final/intermedio).
    Devuelve (True, None) si es válido, (False, mensaje_error) si no.
    """
    elementos = get_elementos_para_instalacion(instalacion)
    elem = next((e for e in elementos if e["key"] == element_key), None)
    if not elem:
        return False, f"Elemento '{element_key}' no definido para la instalación."
    if funcion_seleccionada not in elem["posibles_funciones"]:
        return False, (
            f"{elem['label']} solo puede situarse en: {', '.join(elem['posibles_funciones'])}. "
            f"Seleccionado: {funcion_seleccionada}."
        )
    # Reglas de negocio Agua (compatibles con fontaneria.py)
    if elem.get("solo_inicio_final") and funcion_seleccionada not in (
        "inicio",
        "final",
    ):
        return False, (
            f"{elem['label']} solo puede situarse en Inicio o Final de la polilínea, no en puntos intermedios."
        )
    if elem.get("solo_intermedio") and funcion_seleccionada in ("inicio", "final"):
        return False, (
            f"{elem['label']} solo puede situarse en puntos intermedios. "
            "Use 'Intermedio' y 'Seleccionar punto' o clic en la polilínea."
        )
    return True, None


def label_a_key_agua(label: str) -> str:
    """Convierte el valor del ComboBox (label) a key interna para Agua."""
    label_lower = (label or "").strip().lower()
    if "colze" in label_lower or "codo" in label_lower:
        return COLZE_BASE
    if "clau" in label_lower or "válvula" in label_lower or "valvula" in label_lower:
        return CLAU_DE_PAS
    if "tap" in label_lower:
        return TAPON
    return T_SORTIDA
