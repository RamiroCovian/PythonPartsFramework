from __future__ import annotations

import os

import NemAll_Python_BasisElements as AllplanBasisElements
from NemAll_Python_BaseElements import LayerService

import Instalaciones.PolyLib as PBL

_SANEAMIENTO_LAYER_FALLBACK_BY_KEY = {
    "IS_CON_SANE_FAB": 40148,
    "IS CON SANE FAB": 40148,
    "IS_CON_SANE_OBR": 40149,
    "IS CON SANE OBR": 40149,
    "KN_X_AIGUA": 40106,
    "KN X AIGUA": 40106,
    "KN_Y_AIGUA": 40108,
    "KN Y AIGUA": 40108,
    "KN_AIGUA": 40061,
    "KN AIGUA": 40061,
}
# Por defecto **desactivado**; activar con ``SANEAMIENTO_LAYER_DEBUG=1`` (o true/yes).
_SANEAMIENTO_LAYER_DEBUG = str(
    os.getenv("SANEAMIENTO_LAYER_DEBUG", "0")
).strip().lower() in ("1", "true", "yes")


def layer_debug_enabled() -> bool:
    """True si el rastro de capas está activo (por defecto no; ver ``SANEAMIENTO_LAYER_DEBUG``)."""
    return _SANEAMIENTO_LAYER_DEBUG


def _resolve_document(so: PBL.script_object.PolylineScriptObject):
    """Documento de vista o `so.doc` (p. ej. al finalizar tras `CancelInput`)."""
    doc = None
    try:
        ci = getattr(so, "coord_input", None)
        if ci is not None:
            doc = ci.GetInputViewDocument()
    except Exception:
        doc = None
    if doc is None:
        doc = getattr(so, "doc", None)
    return doc


def _document_candidates(so: PBL.script_object.PolylineScriptObject) -> list:
    """Vista activa y `so.doc` (p. ej. tras CancelInput la vista puede fallar)."""
    out = []
    for d in (_resolve_document(so), getattr(so, "doc", None)):
        if d is None:
            continue
        if not any(id(d) == id(x) for x in out):
            out.append(d)
    return out


def _get_layer_id_by_name(doc, layer_name: str) -> int:
    """
    Port de saneamiento_old.get_layer_id_by_name:
    devuelve 0 si no existe o no se puede resolver.
    """
    if not doc or not layer_name or not isinstance(layer_name, str):
        return 0
    try:
        return int(LayerService.GetIDByShortName(layer_name.strip(), doc) or 0)
    except Exception:
        return 0


def _ensure_layer_id(doc, layer_name_or_id, fallback_id: int = 40148) -> int:
    """
    Port de saneamiento_old.ensure_layer_id:
    - si recibe nombre y existe en doc -> id real
    - si no existe -> fallback_id
    - si recibe id positivo -> id
    """
    if isinstance(layer_name_or_id, str) and layer_name_or_id.strip():
        lid = _get_layer_id_by_name(doc, layer_name_or_id)
        return lid if lid else int(fallback_id)
    if isinstance(layer_name_or_id, int) and layer_name_or_id > 0:
        return int(layer_name_or_id)
    return int(fallback_id)


def _get_layer_id(
    key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject
) -> int:
    """
    Obtiene el ID del layer apropiado para un elemento.
    Prioriza layers específicos guardados sobre el layer por defecto.
    """
    docs = _document_candidates(so)
    layer_id = 0

    if not docs:
        return layer_id

    if getattr(so, "default_layers", None):
        for doc in docs:
            default_id = _get_layer_id_by_name(
                doc, so.default_layers.get("default", "")
            )
            if default_id:
                layer_id = default_id
                break

    if hasattr(so, "applied_layers") and so.applied_layers:
        layer_data = so.applied_layers.get(key_applied_layer_attr, None)
        if layer_data and isinstance(layer_data, dict):
            layer_name_str = layer_data.get("layer")
            if layer_name_str:
                specific_id = 0
                candidates = [str(layer_name_str)]
                if "_" in str(layer_name_str):
                    # En algunos entornos el short name está con espacios.
                    candidates.append(str(layer_name_str).replace("_", " "))
                if _SANEAMIENTO_LAYER_DEBUG:
                    try:
                        print(
                            f"[SANEAMIENTO][LAYERDBG] requested={layer_name_str} "
                            f"candidates={candidates}"
                        )
                    except Exception:
                        pass
                for candidate in candidates:
                    for doc in docs:
                        specific_id = _get_layer_id_by_name(doc, candidate)
                        if specific_id:
                            break
                    if specific_id:
                        break
                if not specific_id and getattr(so, "layer_types", None):
                    for lt in so.layer_types:
                        if not isinstance(lt, dict):
                            continue
                        if lt.get("key") == layer_name_str or lt.get("label") == layer_name_str:
                            key_try = str(lt.get("key", "") or "")
                            label_try = str(lt.get("label", "") or "")
                            for token in (key_try, key_try.replace("_", " "), label_try):
                                if not token:
                                    continue
                                for doc in docs:
                                    specific_id = _get_layer_id_by_name(doc, token)
                                    if specific_id:
                                        break
                                if specific_id:
                                    break
                            if specific_id:
                                break
                if specific_id:
                    layer_id = specific_id
                else:
                    # Fallback legado Saneamiento_old: cuando el proyecto/doc no resuelve
                    # por short name, usar ID conocido de FAB/OBR.
                    fallback_id = int(
                        _SANEAMIENTO_LAYER_FALLBACK_BY_KEY.get(str(layer_name_str), layer_id)
                    )
                    # Port old: ensure_layer_id(nombre, fallback).
                    layer_id = _ensure_layer_id(docs[0], str(layer_name_str), fallback_id)
                    if _SANEAMIENTO_LAYER_DEBUG:
                        try:
                            print(
                                f"[SANEAMIENTO][LAYERDBG] unresolved requested={layer_name_str} "
                                f"-> fallback_default={layer_id}"
                            )
                        except Exception:
                            pass
    if _SANEAMIENTO_LAYER_DEBUG:
        try:
            print(
                f"[SANEAMIENTO][LAYERDBG] key={key_applied_layer_attr} "
                f"resolved_id={layer_id} docs={len(docs)}"
            )
        except Exception:
            pass
    return layer_id


def _apply_layer_to_element(
    model_elem: AllplanBasisElements.ModelElement3D,
    key_layer: str,
    so: PBL.script_object.PolylineScriptObject,
) -> AllplanBasisElements.ModelElement3D:
    """
    Aplica capa al modelo. Reconstruye `ModelElement3D(props, geo)` como en `geo_handler`:
    en algunos flujos de PythonPart `SetCommonProperties` / asignación a `.CommonProperties`
    no es la que lee `create_individual_pythonpart` vía `GetCommonProperties()`.
    """
    # Si no existe una capa aplicada explícitamente para esta key, respetar la capa
    # que ya trae el modelo (definida por el propio script del fitting/tubo).
    try:
        has_explicit_layer = bool(
            hasattr(so, "applied_layers")
            and isinstance(getattr(so, "applied_layers", None), dict)
            and key_layer in (so.applied_layers or {})
        )
        if not has_explicit_layer:
            if _SANEAMIENTO_LAYER_DEBUG:
                try:
                    al = getattr(so, "applied_layers", None) or {}
                    print(
                        f"[SANEAMIENTO][LAYERDBG] keep script layer key={key_layer!r} "
                        f"(sin entrada en applied_layers; nkeys={len(al)})"
                    )
                except Exception:
                    pass
            return model_elem
    except Exception:
        pass

    layer_id = _get_layer_id(key_layer, so)
    if not layer_id:
        if _SANEAMIENTO_LAYER_DEBUG:
            try:
                print(f"[SANEAMIENTO][LAYERDBG] skip apply key={key_layer} layer_id=0")
            except Exception:
                pass
        return model_elem
    try:
        props = model_elem.GetCommonProperties()
        old_layer = getattr(props, "Layer", None)
        props.Layer = layer_id
        try:
            props.ColorByLayer = False
        except Exception:
            pass
        geo = model_elem.GetGeometryObject()
        out = AllplanBasisElements.ModelElement3D(props, geo)
        try:
            attrs = model_elem.GetAttributes()
            if attrs:
                out.SetAttributes(attrs)
        except Exception:
            pass
        if _SANEAMIENTO_LAYER_DEBUG:
            try:
                new_props = out.GetCommonProperties()
                print(
                    f"[SANEAMIENTO][LAYERDBG] applied key={key_layer} "
                    f"old={old_layer} new={getattr(new_props, 'Layer', None)}"
                )
            except Exception:
                pass
        return out
    except Exception as e:
        print(f"[SANEAMIENTO][LAYER] Fallo reconstruyendo elemento ({key_layer}): {e}")
        return model_elem

