# -*- coding: utf-8 -*-
"""Shim to provide installation_registry for polyline_base_lib.

Loads the shared registry implementation from
Instalaciones/Clima/models_lib/py/installation_registry.py.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Type
import importlib.util
import os
import sys


def _load_registry_module():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(
        current_dir,
        "..",
        "Clima",
        "models_lib",
        "py",
        "installation_registry.py",
    )
    registry_path = os.path.abspath(registry_path)
    if not os.path.isfile(registry_path):
        return None

    spec = importlib.util.spec_from_file_location(
        "_clima_installation_registry", registry_path
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


_registry = _load_registry_module()


def register_installation(definition: Dict[str, Any], import_base: Optional[str] = None) -> None:
    if _registry and hasattr(_registry, "register_installation"):
        _registry.register_installation(definition, import_base=import_base)


def register_pythonpart(key: str, cls: Type[Any]) -> None:
    if _registry and hasattr(_registry, "register_pythonpart"):
        _registry.register_pythonpart(key, cls)


def get_installations() -> Dict[str, Any]:
    if _registry and hasattr(_registry, "get_installations"):
        return _registry.get_installations()
    return {}


def get_installation(name: str):
    if _registry and hasattr(_registry, "get_installation"):
        return _registry.get_installation(name)
    return None


def get_elements_for(name: str) -> List[Any]:
    if _registry and hasattr(_registry, "get_elements_for"):
        return _registry.get_elements_for(name)
    return []


def get_pythonpart(key: str):
    if _registry and hasattr(_registry, "get_pythonpart"):
        return _registry.get_pythonpart(key)
    return None


def auto_load_installations(
    base_folder: str = "Instalaciones",
    search_paths: Optional[Iterable[str]] = None,
) -> None:
    if _registry and hasattr(_registry, "auto_load_installations"):
        _registry.auto_load_installations(base_folder, search_paths=search_paths)


def ensure_installation_palette(
    build_ele,
    installation_name: Optional[str] = None,
    installation_property: str = "InstallationName",
    element_key_property: str = "ElementKey",
    installation_type_property: str = "InstallationType",
    supported_angles_property: str = "SupportedAngles",
) -> None:
    if _registry and hasattr(_registry, "ensure_installation_palette"):
        _registry.ensure_installation_palette(
            build_ele,
            installation_name=installation_name,
            installation_property=installation_property,
            element_key_property=element_key_property,
            installation_type_property=installation_type_property,
            supported_angles_property=supported_angles_property,
        )
