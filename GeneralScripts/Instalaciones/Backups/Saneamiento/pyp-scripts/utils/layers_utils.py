from __future__ import annotations

import NemAll_Python_BasisElements as AllplanBasisElements
from NemAll_Python_BaseElements import LayerService

import Instalaciones.PolyLib as PBL


def _get_layer_id(
    key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject
) -> int:
    """
    Obtiene el ID del layer apropiado para un elemento.
    Prioriza layers específicos guardados sobre el layer por defecto.
    """
    doc = so.coord_input.GetInputViewDocument()
    layer_id = 0

    if getattr(so, "default_layers", None):
        default_id = LayerService.GetIDByShortName(
            so.default_layers.get("default", ""), doc  # type: ignore[arg-type]
        )
        if default_id:
            layer_id = default_id

    if hasattr(so, "applied_layers") and so.applied_layers:
        layer_data = so.applied_layers.get(key_applied_layer_attr, None)
        if layer_data and isinstance(layer_data, dict):
            layer_name_str = layer_data.get("layer")
            if layer_name_str:
                specific_id = LayerService.GetIDByShortName(
                    layer_name_str, doc  # type: ignore[arg-type]
                )
                if specific_id:
                    layer_id = specific_id
    return layer_id


def _apply_layer_to_element(
    model_elem: AllplanBasisElements.ModelElement3D,
    key_layer: str,
    so: PBL.script_object.PolylineScriptObject,
) -> AllplanBasisElements.ModelElement3D:
    """
    Busca el ID del layer y lo aplica al elemento.
    """
    layer_id = _get_layer_id(key_layer, so)
    if layer_id is not None:
        try:
            props = model_elem.CommonProperties
            props.Layer = layer_id
            model_elem.CommonProperties = props
        except Exception as e:
            print(f"[Error] Fallo al setear layer en {key_layer}: {e}")

    return model_elem

