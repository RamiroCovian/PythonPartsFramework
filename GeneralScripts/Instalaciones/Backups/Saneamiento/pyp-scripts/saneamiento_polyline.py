# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib
import sys

import NemAll_Python_BaseElements as AllplanBaseElements

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Saneamiento
from Instalaciones.PolyLib.parameters import ParamNames
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.geo_handler import PipelineProcessor

# ---------------- CUSTOM NUM_TD PATH ----------------
project_name, host_name = (
    AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
)
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(
    project_name, host_name
)
if error != 0:
    error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(
        project_name, ""
    )

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Saneamiento.profile()

# ---------------- DEFAULT CONFIG PARAMS ----------------
INST_NAME = "SANEAMIENTO"
CONFIG = PBL.script_object.PolylineBaseConfig(
    default_installation=INST_NAME.upper(),
    parameters_show=profile.show,
    parameters_enabled=profile.enabled,
    num_td_path=base_path,
    limit_angles=True,
    allowed_angles=[0.0, 45.0, 90.0, 135.0, 180.0, -45.0, -90.0, -135.0],
)

# ------ MODULES LOADED FOR TEST ------
reload_module = [
    PBL,
    PBL_interactor,
    PBL_object,
]


def _reload_saneamiento_runtime_modules():
    """
    Hot-reload de scripts de saneamiento en tiempo de ejecución para evitar
    cerrar/abrir Allplan en cada ajuste fino de PythonParts.
    """
    # En Allplan, algunos nombres de módulo pueden incluir "pyp-scripts" (con guion),
    # lo que no siempre permite import_module directo. Reutilizamos módulos ya cargados.
    target_suffixes = (
        "polyline_reg_saneamiento",
        "tub_pvc_tricapa_f_40_script",
        "tub_pvc_tricapa_v_script",
        "tub_pvc_tricapa_p_110_script",
        "tub_pvc_tricapa_f_110_script",
        "utils.geo_handler",
    )
    loaded = list(sys.modules.items())
    for mod_name, mod in loaded:
        if not mod or not isinstance(mod_name, str):
            continue
        if "Instalaciones.Saneamiento" not in mod_name:
            continue
        if not mod_name.endswith(target_suffixes):
            continue
        try:
            importlib.reload(mod)
        except Exception as ex:
            print(f"[SANEAMIENTO][HOT-RELOAD] {mod_name}: {ex}")


def _parse_diameter_palette_value(raw):
    """Normaliza el valor del combo DiameterType (int, float o '110 mm')."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return int(round(float(raw)))
    s = str(raw).strip().lower().replace("mm", "").strip()
    try:
        return int(round(float(s)))
    except (TypeError, ValueError):
        return None


def _diameter_list_as_ints(diameter_list):
    if not diameter_list:
        return []
    out = []
    for x in diameter_list:
        v = _parse_diameter_palette_value(x)
        if v is not None:
            out.append(v)
    return out


def _patch_resolve_installation_config_sync_diameter(so):
    """
    PolyLib actualiza `so.diameter_type` al cambiar InstallationType pero no siempre
    escribe el mismo valor en `build_ele.DiameterType`, de modo que la paleta puede
    seguir mostrando p. ej. 110 mm mientras la lógica usa el primer diámetro del
    nuevo tipo (25 mm en Fecal). Sin tocar PolyLib: envolvemos resolve_installation_config.
    """
    if getattr(so, "_saneamiento_resolve_diameter_patched", False):
        return
    so._saneamiento_resolve_diameter_patched = True
    orig = so.resolve_installation_config

    def wrapped():
        prev_ui = None
        try:
            param = getattr(so.build_ele, ParamNames.Installation.DIAMETER_TYPE, None)
            if param is not None and hasattr(param, "value"):
                prev_ui = _parse_diameter_palette_value(param.value)
        except Exception:
            pass

        result = orig()
        valid = _diameter_list_as_ints(so.diameter_list)
        if not valid:
            return result

        chosen = None
        if prev_ui is not None and prev_ui in valid:
            chosen = prev_ui
        else:
            chosen = _parse_diameter_palette_value(so.diameter_type)

        if chosen is None:
            chosen = valid[0]

        so.diameter_type = chosen
        try:
            param = getattr(so.build_ele, ParamNames.Installation.DIAMETER_TYPE, None)
            if param is not None:
                param.value = chosen
        except Exception:
            pass

        return result

    so.resolve_installation_config = wrapped


def check_allplan_version(_build_ele, _version):
    for module in reload_module:
        try:
            importlib.reload(module)
        except Exception as e:
            print(f"Error al recargar el módulo {module.__name__}: {e}")
    return True


def create_script_object(build_ele, script_object_data):
    script_object = PBL.script_object.initialize_script_object(
        build_ele, script_object_data, CONFIG
    )
    # HOOK: Creación de elementos para previsualizacion
    script_object.element_creation_preview_hook = _create_elements_for_segment_group

    # HOOK: Creación de elementos para crear elementos 3D finales
    script_object.element_creation_layer_attrs_hook = _create_elements_with_layers_attrs

    _patch_resolve_installation_config_sync_diameter(script_object)

    return script_object


# ========================================
# HOOKS PERSONALIZADOS
# ========================================
def _create_elements_for_segment_group(
    segments, so: PBL.script_object.PolylineScriptObject
):
    """
    Genera la geometría 3D de los elementos sin crear PythonParts.
    Devuelve una lista de elementos generados para un grupo de segmentos.
    """
    print("################################## so.saved_segments: ", segments)
    elements_generated = []
    _reload_saneamiento_runtime_modules()

    # Guardamos la orientación 3D de referencia
    so.reference_orientation_angle = getattr(so, "reference_orientation_angle", None)

    model_base = so.current_inst_config
    element_type_core = None
    base_color = None
    if model_base:
        element_type_core = model_base["key"]
        base_color = model_base["color"]

    # Diámetro activo (combo o primer valor del tipo de instalación)
    if so.diameter_list is not None and so.diameter_type is not None:
        diam = int(so.diameter_type)
    elif model_base:
        raw_d = model_base["diameter"]
        diam = int(raw_d[0] if isinstance(raw_d, (list, tuple)) else raw_d)
    else:
        diam = None

    # ------------------------------------------------------------------
    # CASO A: Saneamiento — Pluvial / Fecal (cada diámetro → su PythonPart)
    # ------------------------------------------------------------------
    if (
        model_base
        and element_type_core in ("tub_pvc_tricapa", "tub_pvc_tricapa_v")
        and diam is not None
    ):
        if element_type_core == "tub_pvc_tricapa":
            if diam == 25:
                element_key = "tub_pvc_basic_f_25"
                exec_kwargs = {"rot_x": 180.0, "rot_y": 0.0, "rot_z": 0.0}
            elif diam == 110:
                element_key = "tub_pvc_tricapa_f_110"
                exec_kwargs = {}
            else:
                element_key = "tub_pvc_tricapa_f_40"
                exec_kwargs = {"TipoTubo": 2}
        else:
            # Pluvial: Ø110 → script dedicado; otro diámetro (p. ej. 40) → tricapa_v
            if diam == 110:
                element_key = "tub_pvc_tricapa_p_110"
                exec_kwargs = {}
            else:
                element_key = "tub_pvc_tricapa_v"
                exec_kwargs = {"TipoTubo": 2}

        conduct_model = so._get_pythonpart_installed(
            element_key=element_key,
            exec_kwargs=exec_kwargs,
            attr_kwargs=exec_kwargs,
        )

        if conduct_model:
            # AQUI CAPAZ YA PODRIAS OBTENER LOS MODEL 3D DE CODOS, REDUCTORES, UNIONES, ETC.
            # USAR SIEMPRE LA FUNCION "so._get_pythonpart_installed" PARA LLAMAR A LOS SCRIPTS

            # YA TENIENDO TODOS LOS SCRIPTS (MODEL 3D)
            # TE QUEDA IMPLEMENTAR LA LOGICA PARA  GENERAR EL 3D EN BASE A LO QUE LLEGA AQUI "segments"
            # CONSEJO: AGREGAR EN LA CARPETA UTILS LOS METODOS DE CLASE PARA GENERAR EL 3D.
            # TE DEJO DE EJEMPLO ACA ABAJO.. (BORRAR Y MODIFICAR COMO TE GUSTE)
            elem3D_list = [
                {
                    "type": "tubo_saneamiento",
                    "elem": conduct_model[0],
                    "rotate": True,
                    "color": base_color,
                }
            ]
            # Tricapa con anillo: regenerar por longitud de tramo (el anillo no se escala).
            # Ø25 básico sigue usando solo el template + escalado en el pipeline.
            _rebuild_ring_tube_keys = frozenset(
                {
                    "tub_pvc_tricapa_p_110",
                    "tub_pvc_tricapa_f_110",
                    "tub_pvc_tricapa_v",
                    "tub_pvc_tricapa_f_40",
                }
            )
            proc_kw = dict(
                elem3D_list=elem3D_list,
                element_type="tubo_saneamiento",
                build_ele=getattr(so, "build_ele", None),
                doc=so.coord_input.GetInputViewDocument() if so.coord_input else None,
            )
            if element_key in _rebuild_ring_tube_keys:

                def _rebuild_tubo_saneamiento(length_mm: float):
                    elems = so._get_pythonpart_installed(
                        element_key=element_key,
                        exec_kwargs={**exec_kwargs, "LargoTramoMm": float(length_mm)},
                        attr_kwargs=exec_kwargs,
                    )
                    if not elems:
                        return None
                    # Los scripts con flecha propia BRep deben devolver lista completa.
                    if element_key in (
                        "tub_pvc_tricapa_f_40",
                        "tub_pvc_tricapa_p_110",
                        "tub_pvc_tricapa_f_110",
                    ):
                        return elems
                    return elems[0]

                proc_kw["saneamiento_tube_rebuild"] = _rebuild_tubo_saneamiento

            processor = PipelineProcessor(**proc_kw)
            elements_generated = processor.process(
                segments=segments, segment_cuts=None
            )

    return elements_generated


def _create_elements_with_layers_attrs(
    elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject
) -> list:
    """
    Integra atributos + atributos padre + layers + numeración absoluta.
    Reutiliza metadata persistida en PolyLib (applied_attributes/applied_layers).
    """
    elements_generated_final = elements_generated

    return elements_generated_final


# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================
#
# Las funciones auxiliares de atributos y layers se han movido a:
#   - utils/attributes_utils.py
#   - utils/layers_utils.py
# y se importan al inicio de este módulo.
