# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib
import sys
import traceback

import NemAll_Python_BaseElements as AllplanBaseElements

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Saneamiento
from Instalaciones.PolyLib.parameters import ParamNames
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.geo_handler import PipelineProcessor
from .utils.te_orientation import build_te_params
from .utils.vertex_utils import (
    compute_segment_cuts_for_all_paths,
    detect_bifurcations,
    detect_cross_path_elbows,
    detect_cross_path_manguitos,
)

# Claves de codos por diámetro/sistema:
# - Ø25 fecal mantiene codo_45/codo_90 dedicados.
# - Ø40 fecal usa codo_45_40 y codo_90_40.
# - Ø110 fecal usa codo_45_110 y codo_90_110.
# En ambos casos, 90° se resuelve como 2x45 salvo cambio de plano en el pipeline.
FECAL_ELBOW_KEYS_BY_DIAMETER = {
    25: ("codo_45", "codo_90"),
    40: ("codo_45_40", "codo_90_40"),
    110: ("codo_45_110", "codo_90_110"),
}
PLUVIAL_ELBOW_KEYS_BY_DIAMETER = {
    110: ("codo_45_110_p", "codo_90_110_p"),
}

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
    # Igual que Saneamiento_old: solo recto y giros de 45/90 (izq/der),
    # sin ángulos "cerrados" (135/180) en el limitador.
    allowed_angles=[0.0, 45.0, 90.0, -45.0, -90.0],
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
        "tub_pvc_basic_f_25_script",
        "tub_pvc_tricapa_f_40_script",
        "tub_pvc_tricapa_v_script",
        "tub_pvc_tricapa_p_110_script",
        "tub_pvc_tricapa_f_110_script",
        "Colze_basic_25m_f_45_script",
        "Colze_basic_25m_f_90_script",
        "colze_rigid_40mm_f_45_script",
        "Colze_rigid_40m_f_90_script",
        "Colze_rigid_110m_f_45_script",
        "Colze_rigid_110m_f_90_script",
        "Colze_rigid_110m_p_45_script",
        "Colze_rigid_110m_p_90_script",
        "DerivacionY45_script",
        "Derivacion110m_f_script",
        "utils.elbow_orientation",
        "utils.geo_handler",
        "utils.trim_config",
        "utils.vertex_utils",
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
            if mod_name.endswith("utils.geo_handler") or mod_name.endswith(
                "DerivacionY45_script"
            ) or mod_name.endswith("Derivacion110m_f_script"):
                for _gh_mn, _gh_mod in list(sys.modules.items()):
                    if _gh_mn.endswith("utils.geo_handler") and _gh_mod is not None:
                        setattr(_gh_mod, "_DERIV_Y45_D40_CLASS", None)
                        setattr(_gh_mod, "_DERIV_Y45_D40_LOAD_FAILED", False)
                        setattr(_gh_mod, "_DERIV_Y110_D110_CLASS", None)
                        setattr(_gh_mod, "_DERIV_Y110_D110_LOAD_FAILED", False)
                        break
        except Exception as ex:
            print(f"[SANEAMIENTO][HOT-RELOAD] {mod_name}: {ex}")

    # importlib.reload actualiza el módulo, pero `from .utils.geo_handler import
    # PipelineProcessor` dejó la referencia a la clase antigua: re-enlazar.
    try:
        _poly = sys.modules.get(__name__)
        if _poly is not None:
            for _mn, _mod in list(sys.modules.items()):
                if _mn.endswith("utils.geo_handler") and _mod is not None:
                    _pc = getattr(_mod, "PipelineProcessor", None)
                    if _pc is not None:
                        _poly.PipelineProcessor = _pc
                        break
    except Exception as _ex:
        print(f"[SANEAMIENTO][HOT-RELOAD] rebind PipelineProcessor: {_ex}")


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
    try:
        print(
            f"[SANEAMIENTO][DEBUG] segments_count={len(segments)} "
            f"diameter_type={getattr(so, 'diameter_type', None)} "
            f"installation={getattr(getattr(so, 'build_ele', None), 'InstallationType', None)}"
        )
    except Exception:
        pass
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
        print(
            f"[SANEAMIENTO][DEBUG] conduct_key={element_key} "
            f"exec_kwargs={exec_kwargs} "
            f"loaded={bool(conduct_model)} "
            f"len={len(conduct_model) if conduct_model else 0}"
        )

        if conduct_model:
            codo_45_model = None
            codo_90_model = None
            # Codos dedicados por sistema/diámetro.
            # Fecal: Ø25/Ø40/Ø110. Pluvial: Ø110 (misma geometría que fecal con script propio).
            if element_type_core == "tub_pvc_tricapa":
                elbow_keys = FECAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam))
            else:
                elbow_keys = PLUVIAL_ELBOW_KEYS_BY_DIAMETER.get(int(diam))

            if elbow_keys:
                codo_45_key, codo_90_key = elbow_keys
                codo_45_exec_kwargs = (
                    {}
                    if codo_45_key in ("codo_45_110", "codo_45_110_p")
                    else {"TipoSaneamiento": 0}
                )
                codo_45_model = so._get_pythonpart_installed(
                    element_key=codo_45_key,
                    exec_kwargs=codo_45_exec_kwargs,
                    attr_kwargs=codo_45_exec_kwargs,
                )
                # codo_90_40 se resuelve con script dedicado 87° para cambio de plano.
                # El resto mantiene TipoSaneamiento explícito para los scripts duales.
                codo_90_exec_kwargs = (
                    {}
                    if codo_90_key in ("codo_90_40", "codo_90_110", "codo_90_110_p")
                    else {"TipoSaneamiento": 1}
                )
                codo_90_model = so._get_pythonpart_installed(
                    element_key=codo_90_key,
                    exec_kwargs=codo_90_exec_kwargs,
                    attr_kwargs=codo_90_exec_kwargs,
                )
                print(
                    f"[SANEAMIENTO][DEBUG] elbows diam={diam} "
                    f"c45_key={codo_45_key} c45_len={len(codo_45_model) if codo_45_model else 0} "
                    f"c90_key={codo_90_key} c90_len={len(codo_90_model) if codo_90_model else 0}"
                )

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
            if codo_45_model:
                elem3D_list.append(
                    {"type": "codo_45", "elem": codo_45_model[0], "rotate": True}
                )
                if len(codo_45_model) > 1:
                    elem3D_list.append(
                        {"type": "codo_45_inner", "elem": codo_45_model[1], "rotate": True}
                    )
                if len(codo_45_model) > 2:
                    elem3D_list.append(
                        {"type": "codo_45_inner_2", "elem": codo_45_model[2], "rotate": True}
                    )
            if codo_90_model:
                elem3D_list.append(
                    {"type": "codo_90", "elem": codo_90_model[0], "rotate": True}
                )
                if len(codo_90_model) > 1:
                    elem3D_list.append(
                        {"type": "codo_90_inner", "elem": codo_90_model[1], "rotate": True}
                    )
                if len(codo_90_model) > 2:
                    elem3D_list.append(
                        {
                            "type": "codo_90_inner_2",
                            "elem": codo_90_model[2],
                            "rotate": True,
                        }
                    )
            if element_type_core == "tub_pvc_tricapa" and 40 in _diameter_list_as_ints(
                model_base.get("diameter", [])
            ):
                bif_te = so._get_pythonpart_installed(
                    element_key="bifurcacion_y40",
                    exec_kwargs={},
                    attr_kwargs={},
                )
                if bif_te:
                    elem3D_list.append(
                        {"type": "te", "elem": bif_te[0], "rotate": True}
                    )
            if element_type_core == "tub_pvc_tricapa_v" and 110 in _diameter_list_as_ints(
                model_base.get("diameter", [])
            ):
                bif_te110 = so._get_pythonpart_installed(
                    element_key="bifurcacion_y110_pluvial",
                    exec_kwargs={},
                    attr_kwargs={},
                )
                if bif_te110:
                    elem3D_list.append(
                        {"type": "te", "elem": bif_te110[0], "rotate": True}
                    )
            # Tricapa con anillo: regenerar por longitud de tramo (el anillo no se escala).
            # Ø25 básico sigue usando solo el template + escalado en el pipeline.
            _rebuild_ring_tube_keys = frozenset(
                {
                    "tub_pvc_basic_f_25",
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

                def _rebuild_tubo_saneamiento(length_mm: float, seg_info=None):
                    # Resolver modelo por segmento para soportar rutas mixtas
                    # (p.ej. un tramo Pluvial 110 y otro Fecal 110 en la misma polilínea).
                    local_key = element_key
                    local_exec_kwargs = dict(exec_kwargs)
                    try:
                        seg_d = getattr(seg_info, "diameter", None)
                        if isinstance(seg_d, (list, tuple)) and seg_d:
                            seg_d = seg_d[0]
                        seg_d = int(seg_d) if seg_d is not None else None
                    except Exception:
                        seg_d = None
                    seg_system = str(getattr(seg_info, "system", "") or "").strip().lower()

                    if seg_d == 110:
                        local_key = (
                            "tub_pvc_tricapa_f_110"
                            if seg_system == "fecal"
                            else "tub_pvc_tricapa_p_110"
                        )
                        local_exec_kwargs = {}
                    elif seg_d == 40:
                        local_key = (
                            "tub_pvc_tricapa_f_40"
                            if seg_system == "fecal"
                            else "tub_pvc_tricapa_v"
                        )
                        local_exec_kwargs = {"TipoTubo": 2}
                    elif seg_d == 25:
                        local_key = "tub_pvc_basic_f_25"
                        local_exec_kwargs = {
                            "rot_x": 180.0,
                            "rot_y": 0.0,
                            "rot_z": 0.0,
                        }
                    print(
                        f"[SANEAMIENTO][REBUILD] seg_d={seg_d} seg_system={seg_system} "
                        f"-> key={local_key}"
                    )

                    elems = so._get_pythonpart_installed(
                        element_key=local_key,
                        exec_kwargs={
                            **local_exec_kwargs,
                            "LargoTramoMm": float(length_mm),
                        },
                        attr_kwargs=local_exec_kwargs,
                    )
                    if not elems:
                        print(
                            f"[SANEAMIENTO][DEBUG][REBUILD] key={local_key} "
                            f"returned empty for length={length_mm}"
                        )
                        return None
                    print(
                        f"[SANEAMIENTO][DEBUG][REBUILD] key={local_key} "
                        f"len={len(elems)} exec={local_exec_kwargs}"
                    )
                    # Los scripts con flecha propia BRep deben devolver lista completa.
                    if local_key in (
                        "tub_pvc_basic_f_25",
                        "tub_pvc_tricapa_f_40",
                        "tub_pvc_tricapa_p_110",
                        "tub_pvc_tricapa_f_110",
                    ):
                        return elems
                    return elems[0]

                proc_kw["saneamiento_tube_rebuild"] = _rebuild_tubo_saneamiento

            processor = PipelineProcessor(**proc_kw)
            processor.saneamiento_fecal_tricapa_install = (
                element_type_core == "tub_pvc_tricapa"
            )
            processor.reference_orientation_angle = getattr(
                so, "reference_orientation_angle", None
            )
            path_idx = next(
                (i for i, sg in enumerate(so.segment_groups) if sg is segments),
                0,
            )
            split_segment_groups = list(so.segment_groups)

            vertex_map, te_vertices = detect_bifurcations(split_segment_groups)
            if te_vertices:
                print(
                    f"[SANEAMIENTO] Bifurcaciones detectadas (TE): {len(te_vertices)}"
                )

            cross_path_elbows_all = detect_cross_path_elbows(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )
            cross_path_manguitos_all = detect_cross_path_manguitos(
                split_segment_groups, vertex_map=vertex_map, te_vertices=te_vertices
            )

            processor.te_nodes = (
                build_te_params(split_segment_groups, vertex_map, te_vertices)
                if te_vertices
                else {}
            )
            # TE 40-40-40; TE 110-110-110 solo pluvial (Derivacion110m_f_script + orientación old).
            if processor.te_nodes:
                for _te_params in processor.te_nodes.values():
                    try:
                        di_in = int(round(float(_te_params.get("d_main_in", 0) or 0)))
                        di_out = int(round(float(_te_params.get("d_main_out", 0) or 0)))
                        di_br = int(round(float(_te_params.get("d_branch", 0) or 0)))
                        if di_in == 40 and di_out == 40 and di_br == 40:
                            _te_params["use_saneamiento_old_d40_orientation"] = True
                        elif (
                            di_in == 110
                            and di_out == 110
                            and di_br == 110
                            and bool(_te_params.get("bif_y110_pluvial_only"))
                        ):
                            _te_params[
                                "use_saneamiento_old_d110_pluvial_orientation"
                            ] = True
                    except Exception:
                        pass
            processor.cross_path_elbows = {
                (seg_idx, is_start): data
                for (p_idx, seg_idx, is_start), data in cross_path_elbows_all.items()
                if p_idx == path_idx
            }
            processor.cross_path_manguitos = {
                (seg_idx, is_start): {
                    **data,
                    "other_diameter": (
                        getattr(
                            getattr(
                                split_segment_groups[data["other_path_idx"]][
                                    data["other_seg_idx"]
                                ],
                                "info",
                                None,
                            ),
                            "diameter",
                            None,
                        )
                        if isinstance(data.get("other_path_idx"), int)
                        and isinstance(data.get("other_seg_idx"), int)
                        and 0 <= data["other_path_idx"] < len(split_segment_groups)
                        and 0
                        <= data["other_seg_idx"]
                        < len(split_segment_groups[data["other_path_idx"]])
                        else None
                    ),
                }
                for (p_idx, seg_idx, is_start), data in cross_path_manguitos_all.items()
                if p_idx == path_idx
            }

            all_cuts = compute_segment_cuts_for_all_paths(split_segment_groups)
            segment_cuts = {
                seg_idx: all_cuts.get((path_idx, seg_idx), {"start": 0.0, "end": 0.0})
                for seg_idx in range(len(segments))
            }

            try:
                elements_generated = processor.process(
                    segments=segments, segment_cuts=segment_cuts
                )
                print(
                    f"[SANEAMIENTO][DEBUG] process_ok generated={len(elements_generated) if elements_generated else 0}"
                )
            except Exception as ex:
                print(
                    f"[SANEAMIENTO][DEBUG][ERROR] processor.process failed: {ex} "
                    f"(type={type(ex).__name__})"
                )
                print(traceback.format_exc())
                raise

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
