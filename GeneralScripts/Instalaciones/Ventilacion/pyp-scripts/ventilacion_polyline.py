# -*- coding: utf-8 -*-
"""Ejemplo mínimo de polilínea usando polyline_base_lib.

- Dibujar polilínea
- Botones Guardar / Finalizar
- Crea una caja hueca (ducto mock) por segmento
"""
from __future__ import annotations

import importlib

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings

import Instalaciones.PolyLib as PBL
from Instalaciones.PolyLib import script_object as PBL_object
from Instalaciones.PolyLib import interactor as PBL_interactor
from Instalaciones.PolyLib.models import Ventilacion, GeneratedElement
from Instalaciones.PolyLib.storage import PolylineStorage

from .utils.geo_handler import GeometryHandler, PipelineProcessor
from .utils.segments import (
    DynamicSegmentBuilder,
    ElementConfig,
    ConditionType,
    InsertPosition,
)

from NemAll_Python_BaseElements import LayerService

# ---------------- CUSTOM ABSOLUTE ENUM PATH ----------------
project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()
error, base_path = AllplanBaseElements.ProjectService.GetProjectPath(project_name, host_name)
if error != 0:
    base_path = AllplanSettings.AllplanPaths.GetCurPrjPath()

# ---------------- ENABLE - SHOW PARAMS ----------------
profile = Ventilacion.profile()

# ---------------- DEFAULT CONFIG PARAMS ----------------
INST_NAME = "VENTILACION"
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

    return script_object

# ========================================
# HOOKS PERSONALIZADOS
# ========================================
def _create_elements_for_segment_group(segments, so: PBL.script_object.PolylineScriptObject):
    """
    Genera la geometría 3D de los elementos sin crear PythonParts.
    Devuelve una lista de elementos generados para un grupo de segmentos.
    """
    base_color = 0
    diameter = 0
    _model_conduct = None
    element_type_core = None
    elements_generated = []

    builder = DynamicSegmentBuilder()
    geo_handler = GeometryHandler()

    model_base = so.current_inst_config

    if model_base:
        element_type_core = model_base["key"]
        base_color = model_base["color"]

        if so.diameter_list and so.diameter_type:
            diameter = so.diameter_type
        else:
            diameter = model_base["diameter"]


    selected_inst = [
        item for item in so.pythonparts_modules
        if item.key == element_type_core
    ]
    # ------------------------------------------------------------------
    # CASO A: Conductos Normales / Aislados
    # ------------------------------------------------------------------
    if model_base and element_type_core in ["conducto_normal", "conducto_aislado"]:

        if element_type_core == "conducto_normal":
            # Antes: value=base_color -> Ahora: exec_args=(base_color,)
            _model_conduct = so._get_pythonpart_installed(
                element_key=selected_inst[0].key,
                exec_args=(base_color,),
                attr_kwargs={"color": base_color}
            )

            model3D_manguito = [
                item for item in so.pythonparts_modules
                if item.key == "manguito"
            ]

            manguito_key = model3D_manguito[0].key
            manguito = so._get_pythonpart_installed(element_key=manguito_key)

            builder.add_configuration(
                ElementConfig(
                    element_3d=manguito,
                    condition_type=ConditionType.SAME_ANGLE.value,
                    insert_position=InsertPosition.MIDDLE.value,
                    name_prefix=manguito_key,
                )
            )

        if element_type_core == "conducto_aislado":
            # Antes: value=diameter, modify_elem=True
            # Ahora: pasamos el diámetro a la ejecución y a los atributos por nombre
            _model_conduct = so._get_pythonpart_installed(
                element_key=selected_inst[0].key,
                exec_args=(diameter,),
                attr_kwargs={"value": diameter}
            )

        segment_group_parse = builder.create_segment_group(
            segments,
            _model_conduct,
            element_type_core,
        )

        elements_generated = geo_handler.center_and_connect_models_v2(
            data_list=segment_group_parse,
            conducto_width=diameter,
            color=base_color,
            debug=False
        )

    # ------------------------------------------------------------------
    # CASO B: Conducto Recuperador
    # ------------------------------------------------------------------
    elif model_base and element_type_core in ["conducto_recuperador"]:

        conduct_model = so._get_pythonpart_installed(
            element_key=selected_inst[0].key
        )

        # Búsqueda optimizada de accesorios
        codo_key = next((item.key for item in so.pythonparts_modules if item.key == "codo_90"), None)
        conv_key = next((item.key for item in so.pythonparts_modules if item.key == "conexion"), None)

        codo_model = so._get_pythonpart_installed(element_key=codo_key) if codo_key else None
        conexion_model = so._get_pythonpart_installed(element_key=conv_key) if conv_key else None


        if conduct_model and conexion_model and codo_model:
            elem3D_list = [
                {"type": "conducto_recuperador", "elem": conduct_model[0], "rotate": True, "color": 1},
                {"type": "conexion", "elem": conexion_model[0], "rotate": True},
                {"type": "codo_90", "elem": codo_model[0], "rotate": True},
            ]

            processor = PipelineProcessor(
                elem3D_list=elem3D_list,
                element_type="conducto_recuperador"
            )
            elements_generated = processor.process(segments=segments)

    return elements_generated

def _create_elements_with_layers_attrs(elements_generated, path_idx: int, so: PBL.script_object.PolylineScriptObject) -> list:
    """
    Funcion hook para aplicar atributos y layers por defecto y personalizados.
    elements_generated = self.element_list: List[List[GeneratedElement]]
    """
    if so._config and not so.init_storage:
        inst_name = str(so._config.default_installation).lower()
        so.init_storage = PolylineStorage(name=inst_name)
        so.init_storage.base_path = so._config.num_td_path

    elements_generated_final = []

    forced_number = None
    current_group_id = 0  # <--- Definida al inicio para evitar UnboundLocalError

    for i, element in enumerate(elements_generated):
        element_type = element.element_type
        element_model = element.element
        seg_idx = element.index

        storage_key = f"seg_{path_idx}_elem_{seg_idx}"
        key_individual = f"seg_{path_idx}_elem_{i}"

        # --- 1. LÓGICA DE NUMERACIÓN ---
        # (Se mantiene la lógica de current_group_id que definimos antes)
        if so.init_storage:
            if so.is_individual_mode:
                # MODO INDIVIDUAL, si ya tiene número en el caché persistente, lo mantenemos
                old_attrs = so.applied_default_attributes.get(key_individual)
                existing_num = _extract_number_from_attrs(old_attrs) if old_attrs else None

                if existing_num:
                    forced_number = existing_num
                elif element_type == so.element_type_core:
                    forced_number = so.init_storage._get_next_number(so.element_type_core)
                else:
                    forced_number = None
            else:
                # MODO GRUPAL (Tu requerimiento principal)
                if element_type == so.element_type_core:
                    group_key = f"path_{path_idx}_group_{current_group_id}"

                    # PASO CRÍTICO: Intentamos recuperar el número del caché global primero
                    if group_key in so.global_group_numbers:
                        forced_number = so.global_group_numbers[group_key]
                    else:
                        # Solo si el grupo es REALMENTE nuevo (ej. tras un manguito nuevo), pedimos número
                        new_num = so.init_storage._get_next_number(so.element_type_core)
                        so.global_group_numbers[group_key] = new_num
                        forced_number = new_num
                        # Guardamos en disco inmediatamente para que otros procesos lo vean
                        so.init_storage._save_numbering_file()
                else:
                    # Es un manguito: actúa como frontera de grupo
                    forced_number = None
                    current_group_id += 1

        # --- 2. OBTENCIÓN DE ATRIBUTOS (CON FILTRO DE SEGURIDAD) ---
        base_attrs = None
        cached_attrs = so.applied_default_attributes.get(key_individual)

        # Para tipos multi-diámetro se omite el caché: podría tener un diámetro distinto al actual.
        # Para tipos de diámetro único se mantiene la validación original basada en TV.
        if cached_attrs and not so.diameter_list:
            has_tv_attr = any(hasattr(a, "Id") and a.Id == 1083 for a in cached_attrs)
            if (element_type == so.element_type_core and has_tv_attr) or \
               (element_type != so.element_type_core and not has_tv_attr):
                base_attrs = cached_attrs

        if not base_attrs:
            # Para multi-diámetro busca primero con clave compuesta (element_type_diameter_type)
            diameter_key = (
                f"{element_type}_{so.diameter_type}"
                if so.diameter_list and so.diameter_type
                else element_type
            )
            base_attrs = so.default_attributes.get(diameter_key) or so.default_attributes.get(element_type, [])

        # --- 3. MEZCLA Y PROCESAMIENTO ---
        elem_attrs = so.applied_attributes.get(storage_key, [])
        # Aseguramos que merged_attrs sea una copia para no contaminar el origen
        merged_attrs = _merge_attributes(base_attrs, elem_attrs) if elem_attrs else list(base_attrs)

        # 4. PROCESAR AUTO-NUMBERING
        # Si NO es core, forzamos que forced_number sea None y que se limpie cualquier 1083 residual
        processed_attrs, _ = _process_auto_numbering(
            merged_attrs,
            inst_type=so.element_type_core,
            so=so,
            forced_number=forced_number if element_type == so.element_type_core else None
        )

        # 5. GUARDAR Y APLICAR
        element_model = _apply_attributes_to_model_elem(element_model, processed_attrs)
        so.applied_default_attributes[key_individual] = processed_attrs

        # Capas y finalización
        element_model = _apply_layer_to_element(element_model, storage_key, so) # type: ignore
        element.element = element_model
        elements_generated_final.append(element)

        # --- LÓGICA DE INSERCIÓN DE CUBOIDE ---
        # 1. Al inicio del camino (i == 0)
        # 2. O si el elemento anterior fue un manguito (current_group_id aumentó)
        is_first_in_path = (i == 0)

        # Verificamos si el elemento anterior en el bucle causó un cambio de grupo
        # (Esto implica que el elemento ACTUAL es el primero del nuevo grupo)
        is_first_after_manguito = False
        if i > 0:
            prev_element_type = elements_generated[i-1].element_type
            if prev_element_type != so.element_type_core:
                is_first_after_manguito = True

        if element_type in ["conducto_normal", "conducto_aislado"] and (is_first_in_path or is_first_after_manguito):
            model_base = so.current_inst_config
            diameter = 100
            if model_base:
                if so.diameter_list and so.diameter_type:
                    diameter = so.diameter_type
                else:
                    diameter = model_base["diameter"]
            # Índice real en saved_paths = cantidad de conductos ANTES de posición i
            # (los manguitos intercalados en data_list no consumen puntos en saved_paths)
            pt_idx = sum(1 for j in range(i)
                         if elements_generated[j].element_type in ["conducto_normal", "conducto_aislado"])

            # Creamos el cuboide con pt_idx correcto
            cuboid_model = _create_cuboide_label(diameter, pt_idx, path_idx, so, attr_list=processed_attrs)

            # Guardar attrs para la polilínea: {path_idx: {pt_idx: attrs}}
            if so._polyline_attrs is None:
                so._polyline_attrs = {}
            if path_idx not in so._polyline_attrs:
                so._polyline_attrs[path_idx] = {}
            if pt_idx not in so._polyline_attrs[path_idx]:
                so._polyline_attrs[path_idx][pt_idx] = processed_attrs
            # Lo envolvemos en el formato de diccionario esperado
            # En lugar de crear un diccionario {}, creamos una instancia de la clase
            cuboid_item = GeneratedElement(
                element=cuboid_model,
                element_type="CUBOID_LABEL",
                index=i
            )
            # Lo añadimos a la lista final
            elements_generated_final.append(cuboid_item)

    if so.init_storage:
        so.init_storage._save_numbering_file()

    return elements_generated_final

def _create_cuboide_label(width: int, index: int, path_index: int,
                          so: PBL.script_object.PolylineScriptObject,
                          attr_list: list | None = None) -> AllplanBasisElements.ModelElement3D | None:
    """Crea un cuboide y lo rota según el ángulo Z del segmento actual."""
    import math

    if path_index >= len(so.saved_paths):
        return None

    pts = so.saved_paths[path_index]

    # 1. Validación de puntos
    if len(pts) <= index + 1:
        if len(pts) > 1: index = len(pts) - 2
        else: return None

    p1 = pts[index]
    p2 = pts[index + 1]

    # 2. Propiedades y Layer
    default_id = 0
    if hasattr(so, "default_layers") and "layer_cuboid_label" in so.default_layers:
        default_id = LayerService.GetIDByShortName(so.default_layers["layer_cuboid_label"], so.doc)

    com_prop = AllplanBaseElements.CommonProperties()
    com_prop.GetGlobalProperties()
    com_prop.Layer = default_id
    com_prop.Color = 2

    # 3. Creación de Geometría Base (en el origen)
    c_dim = float(width)
    c_height = 30.0

    # Cuboide centrado en el origen local
    local_p1 = AllplanGeo.Point3D(-c_dim/2, -c_dim/2, 0)
    local_p2 = AllplanGeo.Point3D(c_dim/2, c_dim/2, c_height)
    cuboide_geo = AllplanGeo.Polyhedron3D.CreateCuboid(local_p1, local_p2)

    dx = p2.X - p1.X
    dy = p2.Y - p1.Y
    dz = p2.Z - p1.Z

    # Longitudes proyectadas en cada PLANO
    longitud_xy = math.sqrt(dx**2 + dy**2)  # Proyección en plano HORIZONTAL (suelo)

    elevacion = math.degrees(math.atan2(dz, longitud_xy)) if longitud_xy > 0 else (90.0 if dz > 0 else -90.0)
    matriz_rotacion = AllplanGeo.Matrix3D()

    # Definimos el eje X local para la rotación (como en tu ejemplo del codo)
    eje_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(1,0,0))
    if elevacion > 85 or elevacion < -85:
        eje_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,1,0))

    # Aplicamos la rotación de inclinación
    matriz_rotacion.SetRotation(eje_x_local, AllplanGeo.Angle.FromDeg(elevacion))
    cuboide_geo = AllplanGeo.Transform(cuboide_geo, matriz_rotacion)

    # 5. TRASLACIÓN AL PUNTO FINAL
    # Punto medio del segmento
    mid_point = AllplanGeo.Point3D((p1.X + p2.X) / 2, (p1.Y + p2.Y) / 2, (p1.Z + p2.Z) / 2)

    # Traslación final para colocarlo en su sitio (elevado un poco en Z local)
    matriz_posicion = AllplanGeo.Matrix3D()
    # Offset para que el cuboide no quede "dentro" del tubo (ajustar según radio del tubo)

    c_length = float(width)

    # Elevamos el cuboide un poco sobre el punto medio (eje Z)
    offset_z = mid_point.Z + (c_length / 2)
    matriz_posicion.SetTranslation(AllplanGeo.Vector3D(mid_point.X, mid_point.Y , offset_z))
    if elevacion > 85 or elevacion < -85:
        offset_x = mid_point.X - (c_length / 2) - c_height
        if elevacion < -85:
            offset_x = mid_point.X + (c_length / 2) + c_height
        matriz_posicion.SetTranslation(AllplanGeo.Vector3D(offset_x, mid_point.Y , mid_point.Z))

    cuboide_geo = AllplanGeo.Transform(cuboide_geo, matriz_posicion)

    model_elem = AllplanBasisElements.ModelElement3D(com_prop, cuboide_geo)

    # Aplicar atributos personalizados si se pasaron
    if attr_list:
        model_elem = _apply_attributes_to_model_elem(model_elem, attr_list)

    return model_elem

# ========================================
# APLICACIÓN DE ATRIBUTOS
# ========================================
def _merge_attributes(base_attrs: list, override_attrs: list) -> list:
    """
    Fusiona dos listas de atributos de Allplan.
    Los atributos en override_attrs sobrescriben los de base_attrs si tienen el mismo ID.

    Args:
        base_attrs: Lista base de atributos (AttributeString, AttributeDouble, etc.)
        override_attrs: Lista de atributos que sobrescriben los base

    Returns:
        Lista fusionada de atributos sin duplicados por ID

    Example:
        base = [AttributeString(Id: 55015, Value: "IS08"),
                AttributeString(Id: 55010, Value: "")]
        override = [AttributeString(Id: 55015, Value: "testtt00009")]

        result = _merge_attributes(base, override)
        # result tendrá Id 55015 con valor "testtt00009" y Id 55010 con valor ""
    """
    # Diccionario para rastrear atributos por ID
    # Clave: ID del atributo, Valor: objeto de atributo completo
    attr_dict = {}

    # 1. Primero agregar todos los atributos base
    for attr in base_attrs:
        attr_dict[attr.Id] = attr

    # 2. Sobrescribir/agregar con los atributos de override
    for attr in override_attrs:
        attr_dict[attr.Id] = attr

    # 3. Convertir el diccionario de vuelta a lista
    # Ordenar por ID para mantener consistencia (opcional)
    merged_list = [attr_dict[key] for key in sorted(attr_dict.keys())]

    return merged_list

def _process_auto_numbering(
    attribute_list: list,
    inst_type: str,
    so: PBL.script_object.PolylineScriptObject,
    forced_number: int | None = None
) -> tuple[list, bool]:
    if not attribute_list:
        return attribute_list, False

    new_attr_list = []
    modified = False
    target_id = 1083

    for attr in attribute_list:
        if hasattr(attr, "Id") and attr.Id == target_id:
            # SIEMPRE generamos el valor si hay un forced_number,
            # o si el valor es exactamente "TV" (semilla inicial)
            if forced_number is not None:
                new_value = f"TV-{forced_number}"
                new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
                modified = True
                continue
            elif attr.Value == "TV":
                # Caso de rescate: si no hay forced_number pero detectamos la semilla
                if so.init_storage:
                    num = so.init_storage._get_next_number(inst_type)
                    so.init_storage._save_numbering_file()
                    new_value = f"TV-{num}"
                    new_attr_list.append(AllplanBaseElements.AttributeString(target_id, new_value))
                    modified = True
                    continue

        new_attr_list.append(attr)

    return new_attr_list, modified

def _extract_number_from_attrs(attribute_list: list) -> int | None:
    """
    Extrae el número entero del atributo 1083 (formato 'TV-X').
    """
    if not attribute_list:
        return None

    target_id = 1083
    prefix = "TV-"

    for attr in attribute_list:
        try:
            # Verificamos si es el atributo correcto
            if hasattr(attr, "Id") and attr.Id == target_id:
                val_str = str(attr.Value)

                # Si el valor ya tiene el formato "TV-5", extraemos el 5
                if prefix in val_str:
                    num_part = val_str.replace(prefix, "").strip()
                    if num_part.isdigit():
                        return int(num_part)

                # Si por alguna razón solo está el número como string
                elif val_str.isdigit():
                    return int(val_str)

        except Exception as e:
            print(f"[EXTRACT] Error procesando atributo: {e}")
            continue

    return None

def _apply_attributes_to_model_elem(model_elem, attr_list):
        """
        Empaqueta y aplica una lista de atributos a un elemento 3D de Allplan
        usando la estructura AttributeSet -> Attributes.
        """
        if not attr_list:
            return
        try:
            attr_set_list = []
            # Creamos el set de atributos
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            # Creamos el objeto Attributes contenedor
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            # Aplicamos al elemento
            model_elem.SetAttributes(attributes)
            return model_elem
        except Exception as e:
            print(f"[Error] Al aplicar atributos: {e}")

# ========================================
# APLICACIÓN DE LAYERS
# ========================================
def _apply_layer_to_element(model_elem: AllplanBasisElements.ModelElement3D,
                            key_layer: str,
                            so: PBL.script_object.PolylineScriptObject) -> AllplanBasisElements.ModelElement3D:
        """
        Responsabilidad única: Buscar el ID del layer y aplicarlo al elemento.
        """
        layer_id = _get_layer_id(key_layer, so)
        if layer_id is not None:
            try:
                props = model_elem.CommonProperties
                props.Layer = layer_id
                model_elem.CommonProperties = props
            except Exception as e:
                print(f"[Error] Fallo al setear layer en {key_layer}: {e}")
                pass
        else:
            print(f"[Warn] No se pudo determinar un ID de Layer válido para {key_layer}")

        return model_elem

def _get_layer_id(key_applied_layer_attr: str, so: PBL.script_object.PolylineScriptObject):
        """
        Obtiene el ID del layer apropiado para un elemento.
        Prioridad: global default → default por subtipo → layer específico guardado.
        """
        doc = so.coord_input.GetInputViewDocument()
        layer_id = 0

        # 1. Default global de la instalación
        if so.default_layers:
            default_id = LayerService.GetIDByShortName(so.default_layers.get("default", ""), doc) # type: ignore
            if default_id:
                layer_id = default_id

        # 2. Default por subtipo (installation_types[i]["default_layer"])
        if so.current_inst_config:
            type_layer = so.current_inst_config.get("default_layer", "")
            if type_layer:
                type_id = LayerService.GetIDByShortName(type_layer, doc) # type: ignore
                if type_id:
                    layer_id = type_id

        # 3. Layer específico guardado por el usuario (mayor prioridad)
        if hasattr(so, "applied_layers") and so.applied_layers:
            layer_data = so.applied_layers.get(key_applied_layer_attr, None)
            if layer_data and isinstance(layer_data, dict):
                layer_name_str = layer_data.get("layer")
                if layer_name_str:
                    specific_id = LayerService.GetIDByShortName(layer_name_str, doc) # type: ignore
                    if specific_id:
                        layer_id = specific_id
        return layer_id

