import math
import NemAll_Python_Geometry      as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements  as AllplanBaseElements

from typing import List


class GeometryHandler:
    def center_and_connect_models_v4(self,
                                data_list,
                                conducto_width=75,
                                color=None,
                                layers=[],
                                layer_default=0,
                                default_attrs=[],
                                point_role=None,
                                point_side=None,
                                reference_orientation_angle=None,
                                debug=True):
        """
        Versión Corregida: "Mira a través" de codos y manguitos para calcular
        los ángulos correctamente y cerrar los huecos.
        """
        elementos_transformados = []

        def get_dot_product(v1, v2):
            if not v1 or not v2: return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        # CONSTANTES
        CONDUCTO_WIDTH = conducto_width
        DEFAULT_MANGUITO_INSERTION = 50
        # Lista de elementos que NO definen trayectoria (son accesorios)
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        parse_data = self.split_list_by_connections_pairs(data_list=data_list)

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"# PROCESANDO DATA LIST IN GROUPS: {len(parse_data)}")

        for segment in parse_data:
            data_segment = []
            is_connection_group = False

            if "connection_groups" in segment:
                data_segment = segment["connection_groups"]
                is_connection_group = True
                if debug:
                    print(f"\n>>> Grupo de conexión detectado: {len(data_segment)} elementos")
            elif "remaining_list" in segment:
                data_segment = segment["remaining_list"]
                is_connection_group = False
                if debug:
                    print(f"\n>>> Elementos restantes: {len(data_segment)}")

            if is_connection_group and len(data_segment) == 2:
                print("####################################################### GROUP: ", data_segment)
                for i, item in enumerate(data_segment):
                    segment = item.get("segment")
                    if not segment: continue
                    data = segment.data
                    item_name = getattr(segment, 'name', f"Segment_{i}")
                    start_point = getattr(data, 'start', None)
                    if start_point is None: continue

                    # 1. IDENTIFICAR TIPO
                    tipo_raw = item.get('type', "")
                    tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw)>0 else "")

                    # Es dinámico si NO es un accesorio
                    is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                    # 2. OBTENER VECTOR ACTUAL
                    vec_curr = getattr(data, 'vector_normalizado', None)
                    if vec_curr is None:
                        vec_curr = AllplanGeo.Vector3D(getattr(data, 'delta_x', 0), getattr(data, 'delta_y', 0), getattr(data, 'delta_z', 0))
                        vec_curr.Normalize()

                    extension_inicio = 0.0
                    extension_final = 0.0

                    # if is_dinamic:
                    #     # =========================================================
                    #     # A) BÚSQUEDA HACIA ATRÁS (PREV)
                    #     # =========================================================
                    #     vec_prev = None
                    #     is_prev_manguito = False

                    #     for prev_idx in range(i - 1, -1, -1):
                    #         prev_item = data_list[prev_idx]

                    #         # Chequeo de vecino inmediato (solo en la primera iteración)
                    #         if prev_idx == i - 1:
                    #             if "manguito" in tipo_str: is_prev_manguito = True

                    #         # Si es un conducto real, tomamos su vector y paramos
                    #         if tipo_str not in TIPOS_ACCESORIOS:
                    #             p_data = prev_item["segment"].data
                    #             vec_prev = getattr(p_data, 'vector_normalizado', None)
                    #             if vec_prev is None:
                    #                 vec_prev = AllplanGeo.Vector3D(p_data.delta_x, p_data.delta_y, p_data.delta_z)
                    #                 vec_prev.Normalize()
                    #             break
                    #         # Si es accesorio (codo/manguito), CONTINUAMOS el bucle buscando el siguiente tubo

                    #     # Cálculo extensión inicio
                    #     if vec_prev:
                    #         dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                    #         angle_rad = math.acos(dot)
                    #         if angle_rad > 0.017: # > 1 grado
                    #             extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                    #     # if is_prev_manguito:
                    #     #     # overlap_val = overlap_mm if overlap_mm > 0 else DEFAULT_MANGUITO_INSERTION
                    #     #     extension_inicio = max(extension_inicio, DEFAULT_MANGUITO_INSERTION)

                    #     # =========================================================
                    #     # B) BÚSQUEDA HACIA ADELANTE (NEXT)
                    #     # =========================================================
                    #     vec_next = None
                    #     is_next_manguito = False

                    #     for next_idx in range(i + 1, len(data_list)):
                    #         next_item = data_list[next_idx]

                    #         # Chequeo de vecino inmediato
                    #         if next_idx == i + 1:
                    #             if "manguito" in tipo_str: is_next_manguito = True

                    #         # Si es un conducto real, tomamos su vector y paramos
                    #         if tipo_str not in TIPOS_ACCESORIOS:
                    #             n_data = next_item["segment"].data
                    #             vec_next = getattr(n_data, 'vector_normalizado', None)
                    #             if vec_next is None:
                    #                 vec_next = AllplanGeo.Vector3D(n_data.delta_x, n_data.delta_y, n_data.delta_z)
                    #                 vec_next.Normalize()
                    #             break
                    #         # Si es accesorio, CONTINUAMOS buscando el siguiente tubo para sacar el ángulo real

                    #     # Cálculo extensión final
                    #     if vec_next:
                    #         dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                    #         angle_rad = math.acos(dot)
                    #         if angle_rad > 0.017:
                    #             extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                        # if is_next_manguito:
                        #     # overlap_val = DEFAULT_MANGUITO_INSERTION
                        #     extension_final = max(extension_final, DEFAULT_MANGUITO_INSERTION)

                    # 3. CÁLCULO DE GEOMETRÍA FINAL
                    # longitud_total incluye las extensiones necesarias para tocar el vértice del codo o entrar al manguito
                    longitud_total = getattr(data, 'longitud_3d', 0) #- (DEFAULT_MANGUITO_INSERTION * 2) #+ extension_inicio + extension_final #+ DEFAULT_MANGUITO_INSERTION

                    print("############################# extensiones: ", longitud_total, extension_inicio, extension_final)
                    # 3. CÁLCULO DE GEOMETRÍA FINAL
                    # longitud_total incluye las extensiones necesarias para tocar el vértice del codo o entrar al manguito
                    # manguito_extra = DEFAULT_MANGUITO_INSERTION # mm para asegurar que no haya luz visual
                    # longitud_total = getattr(data, 'longitud_3d', 0) + extension_inicio + extension_final #+ (manguito_extra if not is_dinamic else 0)

                    # El desplazamiento_centro compensa si crecemos más de un lado que del otro
                    desplazamiento_centro = (extension_final - extension_inicio) / 2.0 -(DEFAULT_MANGUITO_INSERTION * 2)

                    mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                    mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                    mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                    # 4. PROCESAR BREPS
                    lista_elem_3d_modified = []
                    list_elem_3d = item.get("element3d", [])

                    if is_dinamic:
                        for elem_3d in list_elem_3d:
                            # Asumimos que esta función estira el BREP simétricamente desde el centro
                            brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                            lista_elem_3d_modified.append(brep_ajustado)
                    else:
                        lista_elem_3d_modified = list_elem_3d

                    for e, elem_3d in enumerate(lista_elem_3d_modified):
                        prop = elem_3d.GetCommonProperties()

                        # Layers
                        layer_to_use = layer_default
                        if layers:
                            found = next((d.get(item_name) for d in layers if isinstance(d, dict) and item_name in d), None)
                            if found is not None: layer_to_use = found
                        prop.Layer = layer_to_use
                        if is_dinamic and color: prop.Color = color

                        brep = elem_3d.GetGeometryObject()

                        # Centrar BREP en 0,0,0 para rotar
                        _, vertices = brep.GetVertices() # type: ignore

                        # Cálculo de centro auxiliar para manguitos
                        punto_medio_x = (start_point.X + data.end.X) / 2.0
                        punto_medio_y = (start_point.Y + data.end.Y) / 2.0
                        punto_medio_z = (start_point.Z + data.end.Z) / 2.0

                        centro_brep_geom = AllplanGeo.Point3D(punto_medio_x, punto_medio_y, punto_medio_z)
                        if vertices:
                            nx = sum(v.X for v in vertices)/len(vertices)
                            ny = sum(v.Y for v in vertices)/len(vertices)
                            nz = sum(v.Z for v in vertices)/len(vertices)
                            centro_brep_geom = AllplanGeo.Point3D(nx, ny, nz)

                        nuevo_brep = None

                        # --- CASO 1: MANGUITOS ---
                        if tipo_str == "manguito":
                            # Se mantienen en su posición original calculada
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                punto_medio_x - centro_brep_geom.Y - ny/2 - DEFAULT_MANGUITO_INSERTION,
                                punto_medio_y - centro_brep_geom.Y,
                                punto_medio_z - centro_brep_geom.Y
                            ))

                        # --- CASO 2: DIFUSORES ---
                        elif tipo_str == "difusor":
                            # (Lógica de difusor mantenida igual que tu original)
                            conducto_width = 75
                            move_offset = 0
                            if point_side == 0: move_offset = conducto_width/2
                            elif point_side == 2: move_offset = -conducto_width/2
                            ang_int = int(data.angulo_xy)

                            if point_role == "inicial":
                                if ang_int != 0:
                                    matriz_rot = AllplanGeo.Matrix3D()
                                    matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(data.angulo_xy))
                                    brep = AllplanGeo.Transform(brep, matriz_rot)

                                w_cubo = -120 if ang_int in [0, 90, 89] else 120
                                offset_x = start_point.X + (w_cubo if ang_int in [180, 178, 179] else -move_offset)
                                offset_y = start_point.Y + (move_offset if ang_int in [0, 180, 178, 179] else w_cubo)

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    offset_x, offset_y -1, mid_z + 11
                                ))
                            elif point_role == "final":
                                rot_diff = 0
                                if ang_int == 0: rot_diff = 180
                                elif ang_int in [180, 179, 178]: rot_diff = 0
                                elif ang_int in [-90, 89, 90, -89]: rot_diff = -data.angulo_xy

                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_diff))
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                                es_horizontal_pura = ang_int in [0, 180, 179, 178]
                                padding = 80
                                if es_horizontal_pura:
                                    factor = -1 if ang_int in [180, 179, 178] else 1
                                    w_cubo = (longitud_total + padding) * factor
                                    if ang_int in [180, 179, 178]: w_cubo = (-longitud_total - padding)
                                    nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        start_point.X + w_cubo, start_point.Y + move_offset, mid_z - nz + 11
                                    ))
                                else:
                                    factor = -1 if ang_int in [-90, -89] else 1
                                    w_cubo = (longitud_total + padding) * factor
                                    nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        start_point.X + move_offset, start_point.Y + w_cubo, mid_z - nz + 11
                                    ))
                            else:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))

                        # --- CASO 3: CONDUCTOS Y ELEMENTOS ESTÁNDAR ---
                        else:
                            # 1. Resetear al Origen (0,0,0) usando el centroide geométrico
                            # Esto asegura que las rotaciones se hagan sobre el centro de la pieza
                            nx = sum(v.X for v in vertices)/len(vertices) if vertices else 0
                            ny = sum(v.Y for v in vertices)/len(vertices) if vertices else 0
                            nz = sum(v.Z for v in vertices)/len(vertices) if vertices else 0
                            brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                            # 2. Calcular Ángulos
                            # Si hay componente Z y el usuario definió orientación, se aplica siempre.
                            len_xy = float(getattr(data, 'longitud_xy', 0) or 0.0)
                            has_z = abs(getattr(data, 'delta_z', 0.0)) > 1e-6
                            if has_z:
                                if reference_orientation_angle is not None:
                                    try:
                                        rot_xy = math.degrees(float(reference_orientation_angle))
                                    except Exception:
                                        rot_xy = 0.0
                                else:
                                    rot_xy = 0.0
                            else:
                                rot_xy = data.angulo_xy
                            rot_pitch = math.degrees(math.atan2(data.delta_z, len_xy))

                            # 3. Aplicar Rotaciones
                            # Roll
                            if abs(getattr(data, 'angulo_rotacion', 0)) > 0.001:
                                m = AllplanGeo.Matrix3D()
                                m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                                brep = AllplanGeo.Transform(brep, m)

                            # Yaw (Planta)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                            brep = AllplanGeo.Transform(brep, m)

                            # Pitch (Elevación)
                            if abs(rot_pitch) > 0.001:
                                rad_xy = math.radians(rot_xy)
                                axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                                m = AllplanGeo.Matrix3D()
                                m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                                brep = AllplanGeo.Transform(brep, m)

                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                            # if i == 0:
                            #     nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            #         punto_medio_x, mid_y, mid_z
                            #     ))
                            # if i == 2:
                            #     nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            #         punto_medio_x - DEFAULT_MANGUITO_INSERTION, mid_y, mid_z
                            #     ))

                        elementos_transformados.append(AllplanBasisElements.ModelElement3D(prop, nuevo_brep))

            else:
                for i, item in enumerate(data_segment):
                    segment = item.get("segment")
                    if not segment: continue
                    data = segment.data
                    item_name = getattr(segment, 'name', f"Segment_{i}")
                    start_point = getattr(data, 'start', None)
                    if start_point is None: continue

                    # 2. OBTENER VECTOR ACTUAL
                    vec_curr = getattr(data, 'vector_normalizado', None)
                    if vec_curr is None:
                        vec_curr = AllplanGeo.Vector3D(getattr(data, 'delta_x', 0), getattr(data, 'delta_y', 0), getattr(data, 'delta_z', 0))
                        vec_curr.Normalize()

                    extension_inicio = 0.0
                    extension_final = 0.0

                    vec_prev = None
                    for prev_idx in range(i - 1, -1, -1):
                        prev_item = data_list[prev_idx]
                        p_data = prev_item["segment"].data
                        vec_prev = getattr(p_data, 'vector_normalizado', None)
                        if vec_prev is None:
                            vec_prev = AllplanGeo.Vector3D(p_data.delta_x, p_data.delta_y, p_data.delta_z)
                            vec_prev.Normalize()
                        break

                    if vec_prev:
                        dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                        angle_rad = math.acos(dot)
                        if angle_rad > 0.017:
                            extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                    # B) Búsqueda del tramo SIGUIENTE válido para el ángulo
                    vec_next = None
                    for next_idx in range(i + 1, len(data_list)):
                        next_item = data_list[next_idx]
                        n_data = next_item["segment"].data
                        vec_next = getattr(n_data, 'vector_normalizado', None)
                        if vec_next is None:
                            vec_next = AllplanGeo.Vector3D(n_data.delta_x, n_data.delta_y, n_data.delta_z)
                            vec_next.Normalize()
                        break

                    if vec_next:
                        dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                        angle_rad = math.acos(dot)
                        if angle_rad > 0.017:
                            extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                    # 3. CÁLCULO DE GEOMETRÍA FINAL
                    longitud_total = getattr(data, 'longitud_3d', 0) + extension_inicio + extension_final
                    # if i == 0:
                    #     longitud_total = getattr(data, 'longitud_3d', 0) + extension_inicio + extension_final - DEFAULT_MANGUITO_INSERTION

                    # print(f"############################# extensiones {i}: ", longitud_total, extension_inicio, extension_final)
                    # El desplazamiento_centro compensa si crecemos más de un lado que del otro
                    desplazamiento_centro = (extension_final - extension_inicio) / 2.0

                    mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                    mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                    mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                    # 4. PROCESAR BREPS
                    lista_elem_3d_modified = []
                    list_elem_3d = item.get("element3d", [])

                    for elem_3d in list_elem_3d:
                            # Asumimos que esta función estira el BREP simétricamente desde el centro
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                        lista_elem_3d_modified.append(brep_ajustado)

                    # Procesar cada elemento 3D
                    for e, elem_3d in enumerate(lista_elem_3d_modified):
                        prop = elem_3d.GetCommonProperties()

                        # Gestión de Capas
                        layer_to_use = layer_default
                        if layers:
                            found = next((d.get(item_name) for d in layers if isinstance(d, dict) and item_name in d), None)
                            if found is not None: layer_to_use = found
                        prop.Layer = layer_to_use
                        prop.Color = color

                        brep = elem_3d.GetGeometryObject()
                        _, vertices = brep.GetVertices() # type: ignore

                        # Cálculo de centro auxiliar para manguitos
                        punto_medio_x = (start_point.X + data.end.X) / 2.0
                        punto_medio_y = (start_point.Y + data.end.Y) / 2.0
                        punto_medio_z = (start_point.Z + data.end.Z) / 2.0

                        # centro_brep_geom = AllplanGeo.Point3D(punto_medio_x, punto_medio_y, punto_medio_z)
                        if vertices:
                            nx = sum(v.X for v in vertices)/len(vertices)
                            ny = sum(v.Y for v in vertices)/len(vertices)
                            nz = sum(v.Z for v in vertices)/len(vertices)
                            #centro_brep_geom = AllplanGeo.Point3D(nx, ny, nz)

                            brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        nuevo_brep = None
                        # 2. Calcular Ángulos
                        # Si hay componente Z y el usuario definió orientación, se aplica siempre.
                        len_xy = float(getattr(data, 'longitud_xy', 0) or 0.0)
                        has_z = abs(getattr(data, 'delta_z', 0.0)) > 1e-6
                        if has_z:
                            if reference_orientation_angle is not None:
                                try:
                                    rot_xy = math.degrees(float(reference_orientation_angle))
                                except Exception:
                                    rot_xy = 0.0
                            else:
                                rot_xy = 0.0
                        else:
                            rot_xy = data.angulo_xy
                        rot_pitch = math.degrees(math.atan2(data.delta_z, len_xy))

                        # 3. Aplicar Rotaciones
                        # Roll
                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación)
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # 4. Mover a la posición final calculada
                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                        print("##################################################### item_name: ",i, item_name)
                        # if i == 0:
                        #     nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                        #             mid_x + DEFAULT_MANGUITO_INSERTION, mid_y, mid_z
                        #     ))
                        # if i == 1:
                        #     nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                        #         mid_x, mid_y +55, mid_z
                        #     ))

                        elementos_transformados.append(AllplanBasisElements.ModelElement3D(prop, nuevo_brep))

        # Atributos finales
        print("################################### elementos_transformados: ", elementos_transformados)
        for i, element in enumerate(elementos_transformados):
            attr_list = default_attrs.copy()
            attr_set_list = [AllplanBaseElements.AttributeSet(attr_list)]
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            element.SetAttributes(attributes)

        if debug:
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados\n")

        return elementos_transformados

    def center_and_connect_models(self,
                            data_list,
                            conducto_width=75,
                            color=None,
                            layers=[],
                            layer_default=0,
                            default_attrs=[],
                            point_role=None,
                            point_side=None,
                            reference_orientation_angle=None,
                            adj_vec_start=None,
                            adj_vec_end=None,
                            debug=True):
        """
        Versión robusta que ignora elementos intermedios (manguitos) para el cálculo
        de ángulos y asegura que todos los objetos se generen.

        adj_vec_start / adj_vec_end: vectores normalizados del segmento adyacente
        en otro path cuando el grupo empieza/termina en un corte en vértice.
        """
        elementos_transformados = []
        list_atts_apply = []

        prev_segment_ang = 0
        next_segment_ang = 0

        def get_dot_product(v1, v2):
            if not v1 or not v2: return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        # CONSTANTES
        CONDUCTO_WIDTH = conducto_width
        DEFAULT_MANGUITO_INSERTION = 50
        MANGUITO_LENGTH = 110
        # Lista de elementos que NO definen trayectoria (son accesorios)
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        is_prev_manguito = False
        is_next_manguito = False

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment: continue
                data = segment.data
                item_name = getattr(segment, 'name', f"Segment_{i}")
                start_point = getattr(data, 'start', None)
                if start_point is None: continue

                # 1. IDENTIFICAR TIPO
                tipo_raw = item.get('type', "")
                tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw)>0 else "")

                # Es dinámico si NO es un accesorio.
                # EXCEPCIÓN: Rejibands (U) NO deben “estirarse” con modificar_dimensiones_brep,
                # porque genera geometría inválida (y luego Allplan falla en CreateElements).
                tipo_l = str(tipo_str).lower()
                is_rejiband = "rejiband" in tipo_l
                is_dinamic = (tipo_str not in TIPOS_ACCESORIOS) and (not is_rejiband)

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, 'vector_normalizado', None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(getattr(data, 'delta_x', 0), getattr(data, 'delta_y', 0), getattr(data, 'delta_z', 0))
                    vec_curr.Normalize()

                extension_inicio = 0.0
                extension_final = 0.0

                prev_item_index = 0
                next_item_index = 0

                if is_dinamic:
                    # =========================================================
                    # A) BÚSQUEDA HACIA ATRÁS (PREV)
                    # =========================================================
                    vec_prev = None
                    for prev_idx in range(i - 1, -1, -1):
                        prev_item = data_list[prev_idx]

                        tipo_raw = prev_item.get('type', "")
                        tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw)>0 else "")
                        # Chequeo de vecino inmediato (solo en la primera iteración)
                        if prev_idx == i - 1:
                            if "manguito" in tipo_str: is_prev_manguito = True

                        # Si es un conducto real, tomamos su vector y paramos
                        if tipo_str not in TIPOS_ACCESORIOS:
                            p_data = prev_item["segment"].data
                            prev_item_index = prev_idx + 1
                            vec_prev = getattr(p_data, 'vector_normalizado', None)
                            if vec_prev is None:
                                vec_prev = AllplanGeo.Vector3D(p_data.delta_x, p_data.delta_y, p_data.delta_z)
                                vec_prev.Normalize()
                            break
                        # Si es accesorio (codo/manguito), CONTINUAMOS el bucle buscando el siguiente tubo

                    # Fallback: vector del path adyacente en corte de vértice
                    # (aplica cuando no hay conducto real anterior en el grupo)
                    is_vertex_cut_start = False
                    if vec_prev is None and adj_vec_start is not None:
                        vec_prev = adj_vec_start
                        is_vertex_cut_start = True

                    # Cálculo extensión inicio
                    if vec_prev:
                        dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                        angle_rad = math.acos(dot)
                        if angle_rad > 0.017: # > 1 grado
                            if is_vertex_cut_start:
                                # Retracción: el otro tubo ya cubre la esquina,
                                # este se acorta para no solaparse.
                                extension_inicio = -(CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)
                            else:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                    if is_prev_manguito:
                        # overlap_val = overlap_mm if overlap_mm > 0 else DEFAULT_MANGUITO_INSERTION
                        extension_inicio = max(extension_inicio, DEFAULT_MANGUITO_INSERTION)

                    # =========================================================
                    # B) BÚSQUEDA HACIA ADELANTE (NEXT)
                    # =========================================================
                    vec_next = None
                    for next_idx in range(i + 1, len(data_list)):
                        next_item = data_list[next_idx]

                        tipo_raw = next_item.get('type', "")
                        tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw)>0 else "")
                        # Chequeo de vecino inmediato
                        if next_idx == i + 1:
                            if "manguito" in tipo_str: is_next_manguito = True

                        # Si es un conducto real, tomamos su vector y paramos
                        if tipo_str not in TIPOS_ACCESORIOS:
                            n_data = next_item["segment"].data
                            next_item_index = next_idx + 1
                            vec_next = getattr(n_data, 'vector_normalizado', None)
                            if vec_next is None:
                                vec_next = AllplanGeo.Vector3D(n_data.delta_x, n_data.delta_y, n_data.delta_z)
                                vec_next.Normalize()
                            break
                        # Si es accesorio, CONTINUAMOS buscando el siguiente tubo para sacar el ángulo real

                    # Fallback: vector del path adyacente en corte de vértice
                    # (aplica cuando no hay siguiente conducto real en el grupo)
                    is_vertex_cut_end = False
                    if vec_next is None and adj_vec_end is not None:
                        vec_next = adj_vec_end
                        is_vertex_cut_end = True

                    # Cálculo extensión final
                    if vec_next:
                        dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                        angle_rad = math.acos(dot)
                        if angle_rad > 0.017:
                            extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)

                    if is_next_manguito:
                        # overlap_val = DEFAULT_MANGUITO_INSERTION
                        extension_final = max(extension_final, DEFAULT_MANGUITO_INSERTION)

                # 3. CÁLCULO DE GEOMETRÍA FINAL
                # print(f"############################################ item_name: {item_name} - {is_prev_manguito} - {is_next_manguito} - {DEFAULT_MANGUITO_INSERTION}")
                # longitud_total incluye las extensiones necesarias para tocar el vértice del codo o entrar al manguito
                longitud_total = getattr(data, 'longitud_3d', 0) + extension_inicio + extension_final
                if is_prev_manguito or is_next_manguito:
                    longitud_total = getattr(data, 'longitud_3d', 0) + extension_inicio + extension_final - DEFAULT_MANGUITO_INSERTION

                # El desplazamiento_centro compensa si crecemos más de un lado que del otro
                desplazamiento_centro = (extension_final - extension_inicio) / 2.0

                mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                # 4. PROCESAR BREPS
                lista_elem_3d_modified = []
                list_elem_3d = item.get("element3d", [])

                if is_dinamic:
                    for elem_3d in list_elem_3d:
                        # Asumimos que esta función estira el BREP simétricamente desde el centro
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                # Procesar cada elemento 3D
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()

                    # Gestión de Capas
                    layer_to_use = layer_default
                    if layers:
                        found = next((d.get(item_name) for d in layers if isinstance(d, dict) and item_name in d), None)
                        if found is not None: layer_to_use = found
                    prop.Layer = layer_to_use

                    if is_dinamic and color: prop.Color = color

                    brep = elem_3d.GetGeometryObject()

                    # Centrar BREP en 0,0,0 para rotar
                    _, vertices = brep.GetVertices() # type: ignore

                    # Cálculo de centro auxiliar para manguitos
                    punto_medio_x = (start_point.X + data.end.X) / 2.0
                    punto_medio_y = (start_point.Y + data.end.Y) / 2.0
                    punto_medio_z = (start_point.Z + data.end.Z) / 2.0

                    centro_brep_geom = AllplanGeo.Point3D(punto_medio_x, punto_medio_y, punto_medio_z)
                    if vertices:
                        nx = sum(v.X for v in vertices)/len(vertices)
                        ny = sum(v.Y for v in vertices)/len(vertices)
                        nz = sum(v.Z for v in vertices)/len(vertices)
                        centro_brep_geom = AllplanGeo.Point3D(nx, ny, nz)

                    nuevo_brep = None
                    segment_ang = int(data.angulo_xy)


                    # --- CASO 1: MANGUITOS ---
                    if tipo_str == "manguito":
                        move_y = punto_medio_y - centro_brep_geom.Y
                        move_x = punto_medio_x - centro_brep_geom.Y
                        if segment_ang == 0 and  prev_segment_ang == 0 and next_segment_ang in [44, 45, -45, -44]:
                            move_x = punto_medio_x - centro_brep_geom.Y - DEFAULT_MANGUITO_INSERTION/2
                            move_y = punto_medio_y - centro_brep_geom.Y + 15.53
                        elif segment_ang == 180 and prev_segment_ang in [0, 180] and next_segment_ang in [-135, -134, 135, 134]:
                            move_y = punto_medio_y - centro_brep_geom.Y - 15.53

                        # Se mantienen en su posición original calculada
                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            move_x,
                            move_y,
                            punto_medio_z - centro_brep_geom.Y
                        ))

                    # --- CASO 2: DIFUSORES ---
                    elif tipo_str == "difusor":
                        # Lógica compleja de difusor mantenida intacta pero optimizada
                        conducto_width = 75
                        move_offset = 0
                        if point_side == 0: move_offset = conducto_width/2
                        elif point_side == 2: move_offset = -conducto_width/2

                        # Pre-cálculo de W_CUBO y lógica de posición
                        ang_int = int(data.angulo_xy)

                        if point_role == "inicial":
                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(data.angulo_xy))
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Determinar W_CUBO
                            w_cubo = -120 if ang_int in [0, 90, 89] else 120

                            offset_x = start_point.X + (w_cubo if ang_int in [180, 178, 179] else -move_offset)
                            offset_y = start_point.Y + (move_offset if ang_int in [0, 180, 178, 179] else w_cubo)

                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                offset_x, offset_y -1, mid_z + 11
                            ))

                        elif point_role == "final":
                            rot_diff = 0
                            if ang_int == 0: rot_diff = 180
                            elif ang_int in [180, 179, 178]: rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]: rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_diff))
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Determinar offsets finales
                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 80

                            if es_horizontal_pura:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                w_cubo = (longitud_total + padding) * factor
                                # Corrección lógica original:
                                if ang_int in [180, 179, 178]: w_cubo = (-longitud_total - padding)

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    start_point.X + w_cubo, start_point.Y + move_offset, mid_z - nz + 11
                                ))
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                w_cubo = (longitud_total + padding) * factor

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    start_point.X + move_offset, start_point.Y + w_cubo, mid_z - nz + 11
                                ))
                        else:
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))

                    else:
                        # 1. Resetear al Origen (0,0,0) usando el centroide geométrico
                        # Esto asegura que las rotaciones se hagan sobre el centro de la pieza
                        nx = sum(v.X for v in vertices)/len(vertices) if vertices else 0
                        ny = sum(v.Y for v in vertices)/len(vertices) if vertices else 0
                        nz = sum(v.Z for v in vertices)/len(vertices) if vertices else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # 2. Calcular Ángulos
                        len_xy = float(getattr(data, 'longitud_xy', 0) or 0.0)
                        has_z = abs(getattr(data, 'delta_z', 0.0)) > 1e-6
                        is_purely_vertical = has_z and len_xy < 1e-3

                        if is_purely_vertical:
                            # Segmento puramente vertical: angulo_xy indefinido,
                            # usar reference_orientation_angle como orientación.
                            if reference_orientation_angle is not None:
                                try:
                                    rot_xy = math.degrees(float(reference_orientation_angle))
                                except Exception:
                                    rot_xy = 0.0
                            else:
                                rot_xy = 0.0
                        else:
                            # Segmento con componente XY (horizontal o inclinado):
                            # usar el ángulo real del segmento en planta.
                            rot_xy = data.angulo_xy
                        rot_pitch = math.degrees(math.atan2(data.delta_z, len_xy))

                        # 3. Aplicar Rotaciones
                        # Roll
                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación)
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                        if is_prev_manguito:
                            if prev_item_index != 0:
                                prev_item = data_list[prev_item_index]
                                prev_data = prev_item["segment"].data
                                prev_segment_ang = int(prev_data.angulo_xy)
                            print(f"################################################### prev_item: {item_name}: ", segment_ang, prev_segment_ang, next_segment_ang)
                            if segment_ang == 0 and prev_segment_ang == 0 and next_segment_ang in [44, 45, -45, -44]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        punto_medio_x - DEFAULT_MANGUITO_INSERTION/2 + 6.25, punto_medio_y + 15.53, mid_z
                                    ))
                            elif segment_ang == 0 and  prev_segment_ang == 0 and next_segment_ang in [-90, -89, 90, 89]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                            punto_medio_x - DEFAULT_MANGUITO_INSERTION, punto_medio_y, mid_z
                                    ))
                            elif segment_ang in [180, 179] and prev_segment_ang in [180, 179] and next_segment_ang in [-135, -134, 135, 134]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        punto_medio_x + DEFAULT_MANGUITO_INSERTION/2 - 6.25, punto_medio_y - 15.53, mid_z
                                ))
                            else:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))

                            is_prev_manguito = False
                        if is_next_manguito:
                            if next_item_index != 0:
                                next_item = data_list[next_item_index]
                                next_data = next_item["segment"].data
                                next_segment_ang = int(next_data.angulo_xy)
                            print(f"################################################### next_item: {item_name}: ", segment_ang, prev_segment_ang, next_segment_ang)

                            if segment_ang == 0 and prev_segment_ang == 0 and next_segment_ang in [44, 45, -45, -44]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        punto_medio_x + DEFAULT_MANGUITO_INSERTION/2 - 6.25, punto_medio_y + 15.53, mid_z
                                ))
                            elif segment_ang == 0 and prev_segment_ang == 0 and next_segment_ang in [-90, -89, 90, 89]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        punto_medio_x + DEFAULT_MANGUITO_INSERTION, punto_medio_y, mid_z
                                ))
                            elif segment_ang in [180, 179] and prev_segment_ang == 0 and next_segment_ang in [-135, -134, 135, 134]:
                                print(f"################################################### ingreso:")
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        punto_medio_x + DEFAULT_MANGUITO_INSERTION/ + 6.25, punto_medio_y, mid_z
                                ))
                            else:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))

                            is_next_manguito = False

                        _meta = item.get("metadata") or {}
                        _psi = _meta.get("path_segment_index")
                        try:
                            _storage_idx = int(_psi) if _psi is not None else i
                        except (TypeError, ValueError):
                            _storage_idx = i
                        segment_brep = {
                            "index": _storage_idx,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        }
                        elementos_transformados.append(segment_brep)

                    # elementos_transformados.append(AllplanBasisElements.ModelElement3D(prop, nuevo_brep))

            except Exception as e:
                if debug: print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        # Asignación de atributos finales
        # for i, element in enumerate(elementos_transformados):
        #     attr_list = default_attrs.copy()

        #     attr_set_list = []
        #     attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
        #     attributes = AllplanBaseElements.Attributes(attr_set_list)
        #     element.SetAttributes(attributes)
        #     list_atts_apply.append(element)

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v1(self, data_list,
                                overlap_mm=0.0,
                                color=None,
                                layers=[],
                                layer_default=0,
                                default_attrs = [],
                                point_role = None,
                                point_side = None,
                                debug=True) -> List:
            """
            Centra cada modelo 3D en su propio segmento con soporte para rotación en 3D.

            Soporta segmentos en cualquier dirección (XY y Z):
            - Segmentos horizontales (plano XY)
            - Segmentos verticales (eje Z)
            - Segmentos inclinados (combinación XY + Z)

            Args:
                data_list: Lista de diccionarios con 'element3d' y 'segment'
                solapamiento_mm: Milímetros adicionales de longitud (por defecto 0mm)
                solapamiento_porcentaje: Porcentaje adicional de longitud (0.003 = 0.3%)
                debug: Si es True, imprime información de depuración

            Returns:
                Lista de AllplanBasisElements.ModelElement3D transformados
            """

            elementos_transformados = []
            list_atts_apply = []
            list_name_segment = []
            for i, item in enumerate(data_list):
                item_name = item['segment'].name
                if debug:
                    print(f"\n{'#'*70}")
                    print(f"# PROCESANDO ITEM {i+1}: {item_name}")
                    print(f"{'#'*70}")

                list_elem_3d = item["element3d"]
                # obj_type = item["type"]
                segment = item["segment"]

                start_point = segment.data.start
                end_point = segment.data.end

                # Calcular longitud 3D del segmento (incluyendo componente Z)
                longitud_segmento = segment.data.longitud_3d

                # Calcular ángulos del segmento en 3D
                delta_x = end_point.X - start_point.X
                delta_y = end_point.Y - start_point.Y
                delta_z = end_point.Z - start_point.Z

                # Calcular distancia en el plano XY
                distancia_xy = math.sqrt(delta_x**2 + delta_y**2)

                # CASO ESPECIAL: Segmento completamente vertical
                if distancia_xy < 0.001:  # Prácticamente vertical (ΔX≈0, ΔY≈0)
                    angulo_xy = 0.0  # No hay dirección horizontal definida

                    # Rotación de 90° o -90° según la dirección Z
                    if delta_z > 0:
                        angulo_inclinacion = 90.0  # Hacia arriba
                    elif delta_z < 0:
                        angulo_inclinacion = -90.0  # Hacia abajo
                    else:
                        angulo_inclinacion = 0.0  # Segmento de longitud cero

                    if debug:
                        direccion = "ARRIBA ↑" if delta_z > 0 else "ABAJO ↓" if delta_z < 0 else "PUNTO"
                        print(f"SEGMENTO VERTICAL DETECTADO: {direccion}")
                else:
                    # Caso normal: Segmento con componente horizontal
                    # Ángulo en plano XY (rotación alrededor del eje Z)
                    angulo_xy = segment.data.angulo_xy #math.degrees(math.atan2(delta_y, delta_x))

                    # Ángulo de inclinación (elevación desde el plano XY)
                    angulo_inclinacion = math.degrees(math.atan2(delta_z, distancia_xy))

                # Ángulo de rotación del elemento (alrededor de su propio eje X)
                angulo_rotacion_elemento = getattr(segment.data, 'angulo_rotacion', 0)

                longitud_con_solape = longitud_segmento + (2 * overlap_mm)
                if debug:
                    print(f"Longitud final con solape: {longitud_con_solape:.2f}mm")

                # Modificar dimensiones según el tipo
                dinamic_flag = item['type'][0] not in ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
                lista_elem_3d_modified = []

                if dinamic_flag:
                    for elem_3d in list_elem_3d:
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_con_solape)
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                # Procesar cada elemento 3D
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if len(layers) > 0:
                        prop.Layer = next((d.get(item_name) for d in layers if item_name in d), layer_default)
                    else:
                        # Si layer_default es 0, no sobreescribir el layer del elemento
                        # (en algunos proyectos layer 0 puede estar apagado/invisible).
                        if layer_default:
                            prop.Layer = layer_default

                    if dinamic_flag and color:
                        prop.Color = color

                    list_name_segment.append(item_name)

                    brep = elem_3d.GetGeometryObject()
                    _, vertices = brep.GetVertices()

                    # Calcular punto medio del segmento (en 3D) -- lo usamos también como fallback
                    punto_medio_x = (start_point.X + end_point.X) / 2.0
                    punto_medio_y = (start_point.Y + end_point.Y) / 2.0
                    punto_medio_z = (start_point.Z + end_point.Z) / 2.0

                    centro_brep = AllplanGeo.Point3D(punto_medio_x, punto_medio_y, punto_medio_z)
                    # --- Calcular centro del BRep con fallback si no hay vértices ---
                    if vertices:
                        nx = sum(v.X for v in vertices) / len(vertices)
                        ny = sum(v.Y for v in vertices) / len(vertices)
                        nz = sum(v.Z for v in vertices) / len(vertices)
                        centro_brep = AllplanGeo.Point3D(nx, ny, nz)

                    # === TRANSFORMACIÓN EN 3D ===
                    nuevo_brep = None
                    conducto_width = 75
                    move = 0
                    if point_side == 0:
                        move = conducto_width/2
                    elif point_side == 2:
                        move = -conducto_width/2
                    else:
                        move = 0 #-conducto_width/2-2

                    if item['type'][0] == "manguito":
                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            punto_medio_x - centro_brep.Y - ny/2, punto_medio_y - centro_brep.Y, punto_medio_z - centro_brep.Y
                        ))
                    elif item['type'][0] == "difusor":
                        if point_role == "inicial":
                            if int(segment.data.angulo_xy) != 0:
                                matriz_rotacion_propia = AllplanGeo.Matrix3D()
                                eje_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
                                matriz_rotacion_propia.SetRotation(eje_x, AllplanGeo.Angle.FromDeg(segment.data.angulo_xy))
                                brep = AllplanGeo.Transform(brep, matriz_rotacion_propia)

                            W_CUBO = -120 if segment.data.angulo_xy in [0, 90, 89] else 120
                            if int(segment.data.angulo_xy) in [0,180, 178, 179]:
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    start_point.X + W_CUBO, start_point.Y + move, punto_medio_z -nz +11,
                                ))
                            else:
                                # W_CUBO = 80 if segment.data.angulo_xy == 0 else -80
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                        start_point.X -move, start_point.Y + W_CUBO, punto_medio_z -nz +11,
                                    ))
                        elif point_role == "final":
                            angulo_rotacion = 0
                            if int(segment.data.angulo_xy) in [0]:
                                angulo_rotacion = 180
                            elif int(segment.data.angulo_xy) in [180, 179,178]:
                                angulo_rotacion = 0
                            elif int(segment.data.angulo_xy) in [-90, 89, 90, -89]:
                                angulo_rotacion = -segment.data.angulo_xy

                            matriz_rotacion_propia = AllplanGeo.Matrix3D()
                            eje_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
                            matriz_rotacion_propia.SetRotation(eje_x, AllplanGeo.Angle.FromDeg(angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, matriz_rotacion_propia)

                            if int(segment.data.angulo_xy) in [0, 180, 179, 178]:
                                W_CUBO = (-longitud_con_solape -80) if int(segment.data.angulo_xy) in [180, 179, 178] else longitud_con_solape+80
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    start_point.X + W_CUBO, start_point.Y + move, punto_medio_z -nz +11,
                                ))
                            else:
                                W_CUBO = (-longitud_con_solape -80) if int(segment.data.angulo_xy) in [-90, -89] else longitud_con_solape+80
                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    start_point.X + move, start_point.Y + W_CUBO, punto_medio_z -nz +11,
                                ))
                        else:
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ))
                    else:
                        # Paso 1: Trasladar al origen
                        brep_trasladado = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            -centro_brep.X, -centro_brep.Y, -centro_brep.Z
                        ))

                        # Paso 2: Rotación del elemento alrededor de su propio eje X (antes de otras rotaciones)
                        # Esto es importante para orientar correctamente codos y conexiones
                        if abs(angulo_rotacion_elemento) > 0.001:
                            matriz_rotacion_propia = AllplanGeo.Matrix3D()
                            eje_x = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
                            matriz_rotacion_propia.SetRotation(eje_x, AllplanGeo.Angle.FromDeg(angulo_rotacion_elemento))
                            brep_rotado_propio = AllplanGeo.Transform(brep_trasladado, matriz_rotacion_propia)

                            if debug:
                                print(f"Aplicada rotación propia del elemento: {angulo_rotacion_elemento:.2f}°")
                        else:
                            brep_rotado_propio = brep_trasladado

                        # Paso 3: Rotación en plano XY (alrededor del eje Z)
                        matriz_rotacion_xy = AllplanGeo.Matrix3D()
                        eje_z = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1))
                        matriz_rotacion_xy.SetRotation(eje_z, AllplanGeo.Angle.FromDeg(angulo_xy))

                        brep_rotado_xy = AllplanGeo.Transform(brep_rotado_propio, matriz_rotacion_xy)

                        # Paso 4: Rotación de inclinación (alrededor del eje Y local)
                        if abs(angulo_inclinacion) > 0.001:
                            matriz_rotacion_inclinacion = AllplanGeo.Matrix3D()

                            # Calcular el eje Y después de la rotación XY
                            eje_y_x = math.sin(math.radians(angulo_xy))
                            eje_y_y = -math.cos(math.radians(angulo_xy))
                            eje_y = AllplanGeo.Line3D(
                                AllplanGeo.Point3D(0, 0, 0),
                                AllplanGeo.Point3D(eje_y_x, eje_y_y, 0)
                            )

                            matriz_rotacion_inclinacion.SetRotation(eje_y, AllplanGeo.Angle.FromDeg(angulo_inclinacion))
                            brep_rotado_final = AllplanGeo.Transform(brep_rotado_xy, matriz_rotacion_inclinacion)

                            if debug:
                                print(f"Aplicada rotación de inclinación: {angulo_inclinacion:.2f}°")
                        else:
                            brep_rotado_final = brep_rotado_xy

                        # Paso 5: Trasladar al punto medio del segmento (en 3D)
                        nuevo_brep = AllplanGeo.Move(brep_rotado_final, AllplanGeo.Vector3D(
                            punto_medio_x, punto_medio_y, punto_medio_z
                        ))

                    # Crear el ModelElement3D transformado
                    elementos_transformados.append(
                        AllplanBasisElements.ModelElement3D(
                            prop,
                            nuevo_brep
                        )
                    )

            for i, element in enumerate(elementos_transformados):
                attr_list = default_attrs.copy()

                attr_set_list = []
                attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
                attributes = AllplanBaseElements.Attributes(attr_set_list)
                element.SetAttributes(attributes)
                list_atts_apply.append(element)

            if debug:
                print(f"\n{'='*70}")
                print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
                print(f"{'='*70}\n")

            return list_atts_apply

    def split_list_by_connections_pairs(self, data_list, connection_types=None):
        """
        Busca todos los elementos con tipos de conexión y crea grupos de 2 elementos
        (elemento_previo + conexión), retornando una lista única con segmentos en orden.

        Args:
            data_list: Lista de elementos
            connection_types: Lista de tipos de conexión a buscar

        Returns:
            list: Lista de diccionarios con claves 'connection_groups' o 'remaining_list'
                [{"remaining_list": [...]}, {"connection_groups": [prev, conn]}, ...]

        Ejemplo:
            Input: [C1, C2, M1, C3, C4, M2, C5]
            Output: [
                {"remaining_list": [C1, C2]},
                {"connection_groups": [C2, M1]},  # Solo 2 elementos
                {"remaining_list": [C3, C4]},
                {"connection_groups": [C4, M2]},  # Solo 2 elementos
                {"remaining_list": [C5]}
            ]
        """

        # Tipos de conexión por defecto si no se proporcionan
        if connection_types is None:
            connection_types = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        # Buscar todos los índices de conexiones
        connection_indices = []

        for i, item in enumerate(data_list):
            try:
                tipo_raw = item.get('type', "")
                tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else "")

                if tipo_str in connection_types:
                    connection_indices.append(i)

            except (AttributeError, TypeError, IndexError):
                continue

        # Si no se encuentran conexiones, retornar toda la lista como remaining
        if not connection_indices:
            return [{"remaining_list": data_list}]

        # Crear lista de resultados con segmentos en orden
        result = []
        used_indices = set()
        current_pos = 0

        for conn_index in connection_indices:
            # Determinar el rango para este grupo de conexión
            # Solo incluye: elemento_previo + conexión (2 elementos)
            start_idx = max(0, conn_index - 1)
            end_idx = conn_index  # SOLO hasta la conexión, NO incluye el siguiente

            # Agregar elementos restantes ANTES de este grupo de conexión
            remaining_before = []
            for i in range(current_pos, start_idx):
                if i not in used_indices:
                    remaining_before.append(data_list[i])
                    used_indices.add(i)

            if remaining_before:
                result.append({"remaining_list": remaining_before})

            # Crear grupo de conexión (solo 2 elementos: previo + conexión)
            group = []
            for i in range(start_idx, end_idx + 1):
                if i not in used_indices:
                    group.append(data_list[i])
                    used_indices.add(i)

            if group:
                result.append({"connection_groups": group})

            # Actualizar posición actual (siguiente elemento después de la conexión)
            current_pos = conn_index + 1

        # Agregar elementos restantes DESPUÉS de todas las conexiones
        remaining_after = []
        for i in range(current_pos, len(data_list)):
            if i not in used_indices:
                remaining_after.append(data_list[i])
                used_indices.add(i)

        if remaining_after:
            result.append({"remaining_list": remaining_after})

        return result

    def split_list_by_all_connections(self, data_list, connection_types=None):
        """
        Searches for ALL items with connection types and creates groups of 3 elements,
        returning a single list with segments in order.

        Args:
            data_list: List of items
            connection_types: List of connection types to search for

        Returns:
            list: List of dictionaries with keys 'connection_groups' or 'remaining_list'
                [{"remaining_list": [...]}, {"connection_groups": [prev, conn, next]}, ...]
        """

        # Default connection types if not provided
        if connection_types is None:
            connection_types = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        # Search for all connection indices
        connection_indices = []

        for i, item in enumerate(data_list):
            try:
                tipo_raw = item.get('type', "")
                tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else "")

                if tipo_str in connection_types:
                    connection_indices.append(i)

            except (AttributeError, TypeError, IndexError):
                continue

        # If no connections found, return entire list as remaining
        if not connection_indices:
            return [{"remaining_list": data_list}]

        # Create result list with segments in order
        result = []
        used_indices = set()
        current_pos = 0

        for conn_index in connection_indices:
            # Determine the range for this connection group
            start_idx = max(0, conn_index - 1)
            end_idx = min(len(data_list) - 1, conn_index + 1)

            # Add remaining items BEFORE this connection group
            remaining_before = []
            for i in range(current_pos, start_idx):
                if i not in used_indices:
                    remaining_before.append(data_list[i])
                    used_indices.add(i)

            if remaining_before:
                result.append({"remaining_list": remaining_before})

            # Create connection group
            group = []
            for i in range(start_idx, end_idx + 1):
                if i not in used_indices:
                    group.append(data_list[i])
                    used_indices.add(i)

            if group:
                result.append({"connection_groups": group})

            # Update current position
            current_pos = end_idx + 1

        # Add any remaining items AFTER all connections
        remaining_after = []
        for i in range(current_pos, len(data_list)):
            if i not in used_indices:
                remaining_after.append(data_list[i])
                used_indices.add(i)

        if remaining_after:
            result.append({"remaining_list": remaining_after})

        return result

    def modificar_dimensiones_brep(self, model_element, nueva_longitud) -> AllplanBasisElements.ModelElement3D:
        """
        Modifica la longitud (eje X) de un elemento 3D representado por BRep3D.
        """
        # 1. Acceder a la sección BRep3D
        geo = model_element.GetGeometryObject()

        # 2. Acceder a los vertices
        initial_vertices = geo.GetVertices()

        # 3. Determinar la longitud actual (máxima X)
        longitud_actual = max(v.X for v in initial_vertices[1]) # Debería ser 1500

        # Si la nueva longitud es igual a la actual, no hacemos nada
        if nueva_longitud == longitud_actual:
            print(f"La longitud ya es {nueva_longitud}. No se requiere modificación.")
            return model_element

        # 4. Modificar los vértices
        nuevo_bloque_vertices = []

        for v in initial_vertices[1]:
            # se reemplaza por la nueva longitud.
            if v.X == longitud_actual:
                v = AllplanGeo.Point3D(nueva_longitud, v.Y, v.Z)

            nuevo_bloque_vertices.append(v)

        # 5. Actualizar el elemento (Simulación de actualización)
        print(f"Longitud original: {longitud_actual}")
        print(f"Nueva longitud: {nueva_longitud}")
        print("--- Vértices Actualizados ---")

        # Crear nuevo BRep vacío
        # Calcula dimensiones desde tus vértices
        p_min = nuevo_bloque_vertices[6]  # vértice mínimo
        p_max = nuevo_bloque_vertices[2]  # vértice máximo

        # Crear paralelepípedo directamente
        polyhedron = AllplanGeo.Polyhedron3D.CreateCuboid(p_min, p_max)

        # Convertir a BRep
        _, nuevo_brep = AllplanGeo.CreateBRep3D(polyhedron)

        nuevo_model = AllplanBasisElements.ModelElement3D(
            model_element.GetCommonProperties(),
            nuevo_brep
        )

        return nuevo_model

