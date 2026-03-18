from __future__ import annotations

from typing import List, Tuple, Optional

import NemAll_Python_BaseElements as AllplanBaseElements

import Instalaciones.PolyLib as PBL


def _merge_attributes(base_attrs: List, override_attrs: List) -> List:
    """
    Fusiona dos listas de atributos de Allplan.
    Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.
    """
    if not base_attrs and not override_attrs:
        return []

    attr_dict = {}

    for attr in base_attrs or []:
        attr_dict[attr.Id] = attr

    for attr in override_attrs or []:
        attr_dict[attr.Id] = attr

    merged_list = [attr_dict[key] for key in sorted(attr_dict.keys())]
    return merged_list


def _process_auto_numbering(
    attribute_list: List,
    inst_type: str,
    so: PBL.script_object.PolylineScriptObject,
    forced_number: Optional[int] = None,
) -> Tuple[List, bool]:
    """
    Aplica numeración automática sobre el atributo 1083 (formato 'TV-X').
    Utiliza so.init_storage para obtener el siguiente número cuando no hay forced_number.
    """
    if not attribute_list:
        return attribute_list, False

    new_attr_list: List = []
    modified = False
    target_id = 1083

    for attr in attribute_list:
        if hasattr(attr, "Id") and attr.Id == target_id:
            if forced_number is not None:
                new_value = f"TV-{forced_number}"
                new_attr_list.append(
                    AllplanBaseElements.AttributeString(target_id, new_value)
                )
                modified = True
                continue
            elif getattr(attr, "Value", None) == "TV":
                if getattr(so, "init_storage", None):
                    num = so.init_storage._get_next_number(inst_type)
                    so.init_storage._save_numbering_file()
                    new_value = f"TV-{num}"
                    new_attr_list.append(
                        AllplanBaseElements.AttributeString(target_id, new_value)
                    )
                    modified = True
                    continue

        new_attr_list.append(attr)

    return new_attr_list, modified


def _extract_number_from_attrs(attribute_list: List) -> Optional[int]:
    """
    Extrae el número entero del atributo 1083 (formato 'TV-X').
    """
    if not attribute_list:
        return None

    target_id = 1083
    prefix = "TV-"

    for attr in attribute_list:
        try:
            if hasattr(attr, "Id") and attr.Id == target_id:
                val_str = str(getattr(attr, "Value", ""))

                if prefix in val_str:
                    num_part = val_str.replace(prefix, "").strip()
                    if num_part.isdigit():
                        return int(num_part)

                elif val_str.isdigit():
                    return int(val_str)

        except Exception:
            continue

    return None


def _apply_attributes_to_model_elem(model_elem, attr_list: List):
    """
    Empaqueta y aplica una lista de atributos a un elemento 3D de Allplan
    usando la estructura AttributeSet -> Attributes.
    """
    if not model_elem or not attr_list:
        return model_elem

    try:
        attr_set_list = [AllplanBaseElements.AttributeSet(attr_list)]
        attributes = AllplanBaseElements.Attributes(attr_set_list)
        model_elem.SetAttributes(attributes)
        return model_elem
    except Exception as e:
        print(f"[Error] Al aplicar atributos: {e}")
        return model_elem

