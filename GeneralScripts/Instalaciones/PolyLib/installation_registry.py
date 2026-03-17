# -*- coding: utf-8 -*-
"""Installation and element registry helpers for the polyline base library.

This module is intentionally decoupled from Allplan specifics so it can be
imported from regular Python as well as from the Allplan runtime.  The public
API mirrors the behaviour of the internal working prototype so that each
installation can self-register and expose its catalog of PythonParts without
duplicating boilerplate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type
import importlib
import os
import pathlib

try:  # Optional dependency – only available inside Allplan
    from ControlPropertiesUtil import ControlPropertiesUtil  # type: ignore
except Exception:  # pragma: no cover - outside Allplan
    ControlPropertiesUtil = None  # type: ignore


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ElementDefinition:
    """Description of a single catalogued PythonPart."""

    key: str
    label: str
    module_path: str
    pythonpart: str
    roles: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    dinamic: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InstallationDefinition:
    """Metadata for an installation and its available elements."""

    name: str
    label: str
    angles: List[float] = field(default_factory=list)
    angles_read: str = ""
    installation_types: List[Dict[str, Any]] = field(default_factory=list)
    default_layers: Dict[str, Any] = field(default_factory=dict)
    layers: List[Dict[str, str]] = field(default_factory=list)
    elements3D: List[ElementDefinition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internal storage
# ---------------------------------------------------------------------------

_INSTALLATIONS: Dict[str, InstallationDefinition] = {}
_ELEMENT_CLASSES: Dict[str, Type[Any]] = {}
_AUTOLOADED_KEYS: set[str] = set()

# ---------------------------------------------------------------------------
# Registry utilities
# ---------------------------------------------------------------------------

def _ensure_element_definition(data: Dict[str, Any]) -> ElementDefinition:
    return ElementDefinition(
        key=str(data["key"]),
        label=str(data.get("label", data["key"])),
        module_path=str(data.get("module_path", "")),
        pythonpart=str(data.get("pythonpart", "")),
        roles=list(data.get("roles", [0, 1, 2, 3])),
        dinamic=bool(data.get("dinamic", False)),
        metadata=dict(data.get("metadata", {})),
    )


def _ensure_installation_definition(data: Dict[str, Any]) -> InstallationDefinition:
    elements = [_ensure_element_definition(el) for el in data.get("elements3D", [])]
    return InstallationDefinition(
        name=str(data["name"]),
        label=str(data.get("label", data["name"])),
        angles=list(data.get("angles", [])),
        angles_read=str(data.get("angles_read", "")),
        installation_types=list(data.get("installation_types", [])),
        default_layers=dict(data.get("default_layers", {})),
        layers=list(data.get("layers", [])),
        elements3D=elements,
        metadata=dict(data.get("metadata", {})),
    )


def register_installation(definition: Dict[str, Any], import_base: Optional[str] = None) -> None:
    """Register an installation and (optionally) preload its PythonParts."""
    inst = _ensure_installation_definition(definition)
    _INSTALLATIONS[inst.name] = inst

    for element in inst.elements3D:
        module_path = element.module_path
        if import_base and not module_path.startswith(import_base):
            module_path = f"{import_base}.{module_path}"
        if module_path:
            try:
                module = importlib.import_module(module_path)
                cls = getattr(module, element.pythonpart)
                _ELEMENT_CLASSES[element.key] = cls
            except Exception:
                # Fall back to lazy loading if the module cannot be imported now.
                pass


def register_pythonpart(key: str, cls: Type[Any]) -> None:
    """Manually associate a pythonpart class with a catalog key."""
    _ELEMENT_CLASSES[key] = cls


def get_installations() -> Dict[str, InstallationDefinition]:
    return dict(_INSTALLATIONS)


def get_installation(name: str) -> Optional[InstallationDefinition]:
    return _INSTALLATIONS.get(name)


def get_elements_for(name: str) -> List[ElementDefinition]:
    inst = get_installation(name)
    return list(inst.elements3D) if inst else []


def get_pythonpart(key: str) -> Optional[Type[Any]]:
    return _ELEMENT_CLASSES.get(key)

# ---------------------------------------------------------------------------
# Auto discovery
# ---------------------------------------------------------------------------

def auto_load_installations(
    base_folder: str = "Instalaciones",
    inst_name: Optional[str] = "",
) -> None:
    """Import every `polyline_*.py` under the provided folders so they can call
    `register_installation`.

    The helper mirrors the behaviour of the existing production setup but keeps
    the list of search locations configurable so projects can adapt it to their
    workspace.
    """
    # if base_folder in _AUTOLOADED_KEYS:
    #     return
    # default_candidates: List[str] = []
    program_data = os.environ.get("PROGRAMDATA")
    main_path = os.path.join("ProgramData", "Nemetschek", "Allplan", "2025", "Etc", "PythonPartsFramework", "GeneralScripts")
    if program_data:
        main_path = os.path.join(program_data, "Nemetschek", "Allplan", "2025", "Etc", "PythonPartsFramework", "GeneralScripts")

    try:
        base = os.path.join(main_path, base_folder)
    except Exception:
        print("[auto_load_installations] No existe:", base_folder)
        return

    for sub in os.listdir(base):
        subfolder = os.path.join(base, sub)
        if not os.path.isdir(subfolder):
            continue

        for f in os.listdir(subfolder):
            if f.startswith(f"polyline_reg_{inst_name}") and f.endswith(".py"):
                import_path = f"{base_folder}.{sub}.{f[:-3]}"
                mod = importlib.import_module(import_path)
                if hasattr(mod, "setup"):
                    import_path_base = f"{base_folder}.{sub}"
                    mod.setup(import_path_base)  # ⬅ ejecutar registro

# ---------------------------------------------------------------------------
# Palette helpers
# ---------------------------------------------------------------------------

def _get_build_ele_value(build_ele, prop_name: str) -> Optional[Any]:
    try:
        prop = getattr(build_ele, prop_name)
    except Exception:
        return None
    if hasattr(prop, "value"):
        return getattr(prop, "value")
    return prop


def _set_build_ele_value(build_ele, prop_name: str, value: Any) -> bool:
    try:
        prop = getattr(build_ele, prop_name)
    except Exception:
        return False

    try:
        if hasattr(prop, "value"):
            prop.value = value
        else:
            setattr(build_ele, prop_name, value)
        return True
    except Exception:
        return False


def _set_value_list(ctrl_prop_util, prop_name: str, values: List[str]) -> None:
    if ctrl_prop_util is None:
        return
    try:
        ctrl_prop_util.set_value_list(prop_name, "|".join(values))
    except Exception:
        pass


def ensure_installation_palette(
    build_ele,
    *,
    installation_name: Optional[str] = None,
    installation_property: str = "InstallationName",
    element_key_property: str = "ElementKey",
    installation_type_property: str = "InstallationType",
    supported_angles_property: str = "SupportedAngles",
    ctrl_prop_util=None,
) -> Optional[str]:
    """Synchronise palette controls with the registry contents.

    Returns the installation name that ended up being selected.
    """

    selected_installation = (
        installation_name
        or _get_build_ele_value(build_ele, installation_property)
        or (next(iter(_INSTALLATIONS.keys()), None))
    )

    if not selected_installation or selected_installation not in _INSTALLATIONS:
        return selected_installation

    inst = _INSTALLATIONS[selected_installation]
    _set_build_ele_value(build_ele, installation_property, selected_installation)

    if inst.angles_read:
        _set_build_ele_value(build_ele, supported_angles_property, inst.angles_read)

    element_labels = [el.label for el in inst.elements3D]
    installation_types = [it.get("label", it.get("key", "")) for it in inst.installation_types]

    if ctrl_prop_util is None and ControlPropertiesUtil is not None:
        # Attempt to instantiate ControlPropertiesUtil if possible
        try:
            ctrl_prop_util = ControlPropertiesUtil([], [build_ele])  # type: ignore
        except Exception:
            ctrl_prop_util = None

    _set_value_list(ctrl_prop_util, element_key_property, element_labels)
    _set_value_list(ctrl_prop_util, installation_type_property, installation_types)

    if element_labels:
        _set_build_ele_value(build_ele, element_key_property, element_labels[0])
    if installation_types:
        _set_build_ele_value(build_ele, installation_type_property, installation_types[0])

    return selected_installation


def describe_installation(name: str) -> Dict[str, Any]:
    inst = get_installation(name)
    if inst is None:
        return {}
    return {
        "name": inst.name,
        "label": inst.label,
        "angles": list(inst.angles),
        "angles_read": inst.angles_read,
        "installation_types": list(inst.installation_types),
        "elements3D": [el.__dict__.copy() for el in inst.elements3D],
        "metadata": dict(inst.metadata),
    }


__all__ = [
    "ElementDefinition",
    "InstallationDefinition",
    "auto_load_installations",
    "describe_installation",
    "ensure_installation_palette",
    "get_elements_for",
    "get_installation",
    "get_installations",
    "get_pythonpart",
    "register_installation",
    "register_pythonpart",
]

