from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import NemAll_Python_BaseElements as AllplanBaseElements

import Instalaciones.PolyLib as PBL

ATTR_PERSO_01_ID = 1083


def _normalize_attribute_list(raw_attrs: Any) -> List:
    """
    Convierte distintos contenedores de atributos de Allplan a lista plana
    de atributos (objetos con .Id / .Value).
    Acepta:
    - list/tuple de atributos
    - AttributeSet (GetAttributes)
    - Attributes (GetAttributeSets)
    """
    if not raw_attrs:
        return []

    if isinstance(raw_attrs, (list, tuple)):
        normalized = []
        for item in raw_attrs:
            if hasattr(item, "Id"):
                normalized.append(item)
            elif hasattr(item, "GetAttributes"):
                try:
                    for nested in item.GetAttributes() or []:
                        if hasattr(nested, "Id"):
                            normalized.append(nested)
                except Exception:
                    continue
            elif hasattr(item, "GetAttributeSets"):
                try:
                    for attr_set in item.GetAttributeSets() or []:
                        if not hasattr(attr_set, "GetAttributes"):
                            continue
                        for nested in attr_set.GetAttributes() or []:
                            if hasattr(nested, "Id"):
                                normalized.append(nested)
                except Exception:
                    continue
        return normalized

    # Caso AttributeSet
    if hasattr(raw_attrs, "GetAttributes"):
        try:
            nested_attrs = raw_attrs.GetAttributes() or []
            return [a for a in nested_attrs if hasattr(a, "Id")]
        except Exception:
            pass

    # Caso Attributes (contenedor de sets)
    if hasattr(raw_attrs, "GetAttributeSets"):
        normalized = []
        try:
            for attr_set in raw_attrs.GetAttributeSets() or []:
                if not hasattr(attr_set, "GetAttributes"):
                    continue
                for attr in attr_set.GetAttributes() or []:
                    if hasattr(attr, "Id"):
                        normalized.append(attr)
        except Exception:
            return []
        return normalized

    return []


def _merge_attributes(base_attrs: List, override_attrs: List) -> List:
    """
    Fusiona dos listas de atributos de Allplan.
    Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.
    """
    base_norm = _normalize_attribute_list(base_attrs)
    override_norm = _normalize_attribute_list(override_attrs)

    if not base_norm and not override_norm:
        return []

    attr_dict = {}

    for attr in base_norm:
        attr_dict[attr.Id] = attr

    for attr in override_norm:
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
    attribute_list = _normalize_attribute_list(attribute_list)
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
    attribute_list = _normalize_attribute_list(attribute_list)
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
    attr_list = _normalize_attribute_list(attr_list)
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


def _get_attributes_from_model_elem(model_elem: Any) -> List:
    """
    Extrae los atributos actuales de un ModelElement3D y los devuelve
    como lista plana de atributos.
    """
    if model_elem is None or not hasattr(model_elem, "GetAttributes"):
        return []
    try:
        raw_attrs = model_elem.GetAttributes()
    except Exception:
        return []
    return _normalize_attribute_list(raw_attrs)


def _has_material_cavitat(elem: Any, doc: Any) -> bool:
    """
    Comprueba si el elemento tiene Material = CAVITAT.
    Se usa para omitir numeración/atributos en elementos "outer" de TD.
    """
    if not elem or not doc or not hasattr(elem, "GetAttributes"):
        return False

    try:
        material_attr_id = AllplanBaseElements.AttributeService.GetAttributeID(
            doc, "Material"
        )
        if not material_attr_id or material_attr_id <= 0:
            return False

        attrs = elem.GetAttributes()
        if not attrs or not hasattr(attrs, "GetAttributeSets"):
            return False

        for attr_set in attrs.GetAttributeSets() or []:
            if not hasattr(attr_set, "GetAttributes"):
                continue
            for attr in attr_set.GetAttributes() or []:
                if getattr(attr, "Id", None) != material_attr_id:
                    continue
                value = str(getattr(attr, "Value", "")).strip().upper()
                if value == "CAVITAT":
                    return True
    except Exception:
        return False

    return False


def _get_first_attr_value(custom_attrs: Dict[str, Any]) -> Optional[str]:
    if not custom_attrs:
        return None
    for value in custom_attrs.values():
        txt = str(value).strip() if value is not None else ""
        if txt:
            return txt
    return None


def _upsert_named_attributes(
    elem: Any, doc: Any, attr_name_value_pairs: List[Tuple[str, str]]
) -> None:
    """
    Inserta o actualiza atributos string por nombre manteniendo el resto.
    """
    if elem is None or doc is None or not attr_name_value_pairs:
        return

    attr_ids: List[Tuple[int, str]] = []
    for attr_name, attr_value in attr_name_value_pairs:
        try:
            attr_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, attr_name)
        except Exception:
            attr_id = 0
        if attr_id and attr_id > 0:
            attr_ids.append((int(attr_id), attr_value))

    if not attr_ids:
        return

    attrs = elem.GetAttributes() if hasattr(elem, "GetAttributes") else None
    if not attrs or not hasattr(attrs, "GetAttributeSets"):
        new_attrs = [
            AllplanBaseElements.AttributeString(attr_id, attr_value)
            for attr_id, attr_value in attr_ids
        ]
        elem.SetAttributes(
            AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet(new_attrs)])
        )
        return

    attr_sets = list(attrs.GetAttributeSets() or [])
    found_by_id = {attr_id: False for attr_id, _ in attr_ids}

    for attr_set in attr_sets:
        attr_list = list(attr_set.GetAttributes() or [])
        for attr in attr_list:
            current_id = getattr(attr, "Id", None)
            for attr_id, attr_value in attr_ids:
                if current_id == attr_id:
                    attr.Value = attr_value
                    found_by_id[attr_id] = True
        attr_set.SetAttributes(attr_list)

    if attr_sets:
        first_set = attr_sets[0]
        first_attr_list = list(first_set.GetAttributes() or [])
        for attr_id, attr_value in attr_ids:
            if not found_by_id[attr_id]:
                first_attr_list.append(
                    AllplanBaseElements.AttributeString(attr_id, attr_value)
                )
        first_set.SetAttributes(first_attr_list)
    else:
        created_attrs = [
            AllplanBaseElements.AttributeString(attr_id, attr_value)
            for attr_id, attr_value in attr_ids
        ]
        attr_sets = [AllplanBaseElements.AttributeSet(created_attrs)]

    attrs.SetAttributeSets(attr_sets)
    elem.SetAttributes(attrs)


def _remove_named_attributes(elem: Any, doc: Any, attr_names: List[str]) -> None:
    """
    Elimina atributos por nombre (si existen) manteniendo el resto intacto.
    """
    if elem is None or doc is None or not attr_names:
        return

    remove_ids = set()
    for attr_name in attr_names:
        try:
            attr_id = AllplanBaseElements.AttributeService.GetAttributeID(doc, attr_name)
        except Exception:
            attr_id = 0
        if attr_id and attr_id > 0:
            remove_ids.add(int(attr_id))

    if not remove_ids:
        return

    attrs = elem.GetAttributes() if hasattr(elem, "GetAttributes") else None
    if not attrs or not hasattr(attrs, "GetAttributeSets"):
        return

    attr_sets = list(attrs.GetAttributeSets() or [])
    for attr_set in attr_sets:
        attr_list = list(attr_set.GetAttributes() or [])
        filtered = [a for a in attr_list if getattr(a, "Id", None) not in remove_ids]
        attr_set.SetAttributes(filtered)

    attrs.SetAttributeSets(attr_sets)
    elem.SetAttributes(attrs)


def _set_parent_attributes(
    elem: Any, custom_attrs: Dict[str, Any], doc: Any, distribution_type: str = "IS"
) -> None:
    """
    Aplica atributos padre con lógica de fontaneria:
    - TD: solo pmp_pare
    - IS: 6_CC_IS + pmp_pare
    """
    if elem is None or doc is None or not custom_attrs:
        return
    if _has_material_cavitat(elem, doc):
        return

    attr_value = _get_first_attr_value(custom_attrs)
    if not attr_value:
        return

    dist = "TD" if str(distribution_type).upper() == "TD" else "IS"
    if dist == "TD":
        pairs = [("pmp_pare", attr_value)]
    else:
        pairs = [("6_CC_IS", attr_value), ("pmp_pare", attr_value)]

    _upsert_named_attributes(elem, doc, pairs)
    if dist == "TD":
        # Regla estricta TD: nunca conservar 6_CC_IS en atributos padre.
        _remove_named_attributes(elem, doc, ["6_CC_IS"])


def _apply_absolute_numbering_attr01(
    elem: Any,
    so: PBL.script_object.PolylineScriptObject,
    diameter_mm: int,
    distribution_type: str = "IS",
) -> Optional[int]:
    """
    Aplica numeración absoluta en ATTR01 con formato: TAF-{diam}. {num}
    Devuelve el número asignado o None si no se pudo aplicar.
    """
    if elem is None or so is None:
        return None

    doc = None
    try:
        doc = so.coord_input.GetInputViewDocument() if so.coord_input else None
    except Exception:
        doc = None

    if doc and _has_material_cavitat(elem, doc):
        return None

    if not hasattr(so, "init_storage") or not so.init_storage:
        return None

    dist = "TD" if str(distribution_type).upper() == "TD" else "IS"
    key_for_numbering = f"{dist}_Tubo_{int(diameter_mm)}mm"
    next_num = so.init_storage._get_next_number(key_for_numbering)

    attrs = elem.GetAttributes() if hasattr(elem, "GetAttributes") else None
    if not attrs or not hasattr(attrs, "GetAttributeSets"):
        new_val = f"TAF-{int(diameter_mm)}. {next_num}"
        new_attr = AllplanBaseElements.AttributeString(ATTR_PERSO_01_ID, new_val)
        elem.SetAttributes(
            AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet([new_attr])])
        )
        return next_num

    attr_sets = list(attrs.GetAttributeSets() or [])
    found = False
    for attr_set in attr_sets:
        attr_list = list(attr_set.GetAttributes() or [])
        for attr in attr_list:
            if getattr(attr, "Id", None) == ATTR_PERSO_01_ID:
                base_value = str(getattr(attr, "Value", "") or "").strip()
                if not base_value:
                    base_value = f"TAF-{int(diameter_mm)}."
                attr.Value = f"{base_value} {next_num}"
                found = True
        attr_set.SetAttributes(attr_list)

    if not found:
        new_val = f"TAF-{int(diameter_mm)}. {next_num}"
        new_attr = AllplanBaseElements.AttributeString(ATTR_PERSO_01_ID, new_val)
        if attr_sets:
            first_set = attr_sets[0]
            first_attrs = list(first_set.GetAttributes() or [])
            first_attrs.append(new_attr)
            first_set.SetAttributes(first_attrs)
        else:
            attr_sets = [AllplanBaseElements.AttributeSet([new_attr])]

    attrs.SetAttributeSets(attr_sets)
    elem.SetAttributes(attrs)
    return next_num

