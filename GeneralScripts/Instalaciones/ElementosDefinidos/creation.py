# -*- coding: utf-8 -*-
"""
Helpers para crear elementos 3D desde element_markers o free_placed_points.
El script (fontaneria, etc.) proporciona el callback que crea cada elemento
en el documento; este módulo solo itera y llama al callback.
"""
from __future__ import annotations

from typing import Any, Callable, List, Optional

try:
    import NemAll_Python_Geometry as AllplanGeo
except Exception:
    AllplanGeo = None


def create_elements_from_free_placed_points(
    script_object: Any,
    coord_input: Any,
    create_element_callback: Callable[
        [Any, Any, str, Any], bool
    ],
) -> int:
    """
    Itera free_placed_points del script_object, crea un elemento 3D en cada posición
    mediante create_element_callback(build_ele, doc, element_type, pos) y vacía la lista.

    create_element_callback debe devolver True si creó el elemento.
    Devuelve el número de elementos creados.
    """
    free_list = getattr(script_object, "free_placed_points", None) or []
    if not free_list:
        return 0
    doc = None
    if coord_input is not None:
        try:
            doc = coord_input.GetInputViewDocument()
        except Exception:
            pass
    if doc is None:
        return 0
    build_ele = getattr(script_object, "build_ele", None)
    created = 0
    for fp in free_list:
        pos = fp.get("pos")
        element_type = (
            str(fp.get("element_type", "t_sortida") or "t_sortida").strip().lower()
        )
        if pos is None or not hasattr(pos, "X"):
            continue
        if AllplanGeo is not None:
            p_mid = AllplanGeo.Point3D(pos.X, pos.Y, pos.Z)
        else:
            p_mid = pos

        # Aplicar rotación específica del punto libre (si existe) solo para este elemento
        prev_values = {}
        rotation_keys = (("RotX", "rot_x"), ("RotY", "rot_y"), ("RotZ", "rot_z"))
        if build_ele is not None:
            try:
                for attr_name, fp_key in rotation_keys:
                    param = getattr(build_ele, attr_name, None)
                    if param is None or not hasattr(param, "value"):
                        continue
                    prev_values[attr_name] = param.value
                    fp_val = fp.get(fp_key, None)
                    if fp_val is None:
                        # Si no hay rotación guardada para este punto, dejar el valor global
                        continue
                    try:
                        param.value = float(fp_val)
                    except Exception:
                        pass
            except Exception:
                prev_values = {}

        try:
            if create_element_callback(build_ele, doc, element_type, p_mid):
                created += 1
        except Exception as ex:
            print(
                f"[ElementosDefinidos] Error creando elemento {element_type} en punto libre: {ex}"
            )
        finally:
            # Restaurar los valores de rotación originales de la paleta
            if build_ele is not None and prev_values:
                try:
                    for attr_name, old_val in prev_values.items():
                        param = getattr(build_ele, attr_name, None)
                        if param is None or not hasattr(param, "value"):
                            continue
                        param.value = old_val
                except Exception:
                    pass
    script_object.free_placed_points = []
    return created


def iterate_element_markers(
    script_object: Any,
) -> List[dict]:
    """
    Devuelve la lista de element_markers del script_object para que el script
    los recorra en _finalize_and_create_now y cree cada elemento 3D.
    Cada marcador tiene kind, pos (Point3D), radius, element_type, path_idx, pt_idx, etc.
    """
    return list(getattr(script_object, "element_markers", []) or [])
