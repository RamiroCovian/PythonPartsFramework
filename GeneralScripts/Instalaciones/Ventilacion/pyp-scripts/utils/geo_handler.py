import math
import NemAll_Python_Geometry      as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements


class GeometryHandler:
    def center_and_connect_models_v2(self,
                            data_list,
                            conducto_width=75,
                            color=None,
                            point_role=None,
                            point_side=None,
                            debug=False):
        """
        Versión robusta que ignora elementos intermedios (manguitos) para el cálculo
        de ángulos y asegura que todos los objetos se generen.
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None
        last_dynamic_data = None
        roll_state = {'roll_final': 0.0, 'last_angulo_z': None}

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg1:
                return False

            a1 = seg1.data.angulo_xy
            a2 = seg2.data.angulo_xy

            diff = abs((a1 - a2 + 180) % 360 - 180)
            return diff < tol_deg

        # CONSTANTES
        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment: continue
                data = segment.data
                item_name = getattr(segment, 'name', f"Segment_{i}")
                start_point = getattr(data, 'start', None)
                if start_point is None: continue
                tipo_str =  item.get('type', "")

                # 1. IDENTIFICAR TIPO
                # tipo_raw = item.get('type', "")
                # tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else tipo_raw)

                # NOTA: Ya no saltamos los manguitos, los procesamos
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, 'vector_normalizado', None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(getattr(data, 'delta_x', 0), getattr(data, 'delta_y', 0), getattr(data, 'delta_z', 0))
                    vec_curr.Normalize()

                #CONTINUIDAD ENTRE SEGMENTOS RECTOS
                if (

                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0
                desplazamiento_neto = 0.0

                _next_seg  = data_list[i + 1].get("segment") if i < len(data_list) - 1 else None
                _next_data = _next_seg.data if _next_seg else None
                roll_final = self._get_rotation_strategy(
                    data, segment.info, roll_state,
                    is_first=(i == 0), next_data=_next_data,
                )
                # 3. LOGICA DE CONEXION (Solo para tubos dinamicos)
                # ── Extensiones en uniones (solo tubos dinamicos) ────────────────
                if is_dinamic:
                    vec_curr = data.vector_normalizado
                    SAFE_MAX_ANGLE = math.radians(175.0)

                    # Tolerancia para detectar 135° (por si hay decimales como 134.99)
                    ANGULO_ESPECIAL_RAD = math.radians(135.0)
                    TOLERANCIA = math.radians(1.0)

                    # 1. Extension al INICIO
                    extension_inicio = 0.0
                    if i > 0:
                        prev_item = data_list[i - 1]

                        if prev_item.get('type') != "manguito":
                            vec_prev = prev_item["segment"].data.vector_normalizado
                            dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el inicio del segundo segmento del codo, recortamos
                                    extension_inicio = -15.4
                                    if debug: print(f"  {item_name} - Inicio: Detectado 135°, aplicando recorte -22.5")
                                else:
                                    # Logica inicial (Tangente)
                                    extension_teorica = (CONDUCTO_WIDTH / 2.0) * math.tan(a_rad / 2.0)
                                    extension_inicio = extension_teorica

                    # 2. Extension al FINAL
                    extension_final = 0.0
                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        if next_item.get('type') != "manguito":
                            vec_next = next_item["segment"].data.vector_normalizado
                            dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el final del primer segmento del codo, alargamos
                                    extension_final = 15.4
                                    if debug: print(f"  {item_name} - Final: Detectado 135°, aplicando alargue 22.5")
                                else:
                                    # Logica inicial (Tangente)
                                    extension_teorica = (CONDUCTO_WIDTH / 2.0) * math.tan(a_rad / 2.0)
                                    extension_final = extension_teorica

                    # 3. Aplicacion de longitud
                    longitud_original = getattr(data, 'longitud_3d', 0.0)
                    longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(f"  Long original: {longitud_original}")
                    print(f"  Ext inicio: {extension_inicio}, Ext final: {extension_final}")
                    print(f"  Long total: {longitud_total}")

                # 5. PROCESAR BREPS
                lista_elem_3d_modified = []
                list_elem_3d = item.get("element3d", [])

                if is_dinamic:
                    for elem_3d in list_elem_3d:
                        brep_ajustado = None
                        # Asumimos que esta funcion estira el BREP simetricamente desde el centro
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                # Procesar cada elemento 3D
                conn_type_list = []
                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color: prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, vertices = brep.GetVertices() # type: ignore

                    # Calculo de centro auxiliar para manguitos
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
                        segment_brep = None
                        if e == 0:  # Solo calculamos centro y transformaciones con el primer BREP
                            # Recalcular el centro del BREP principal (el primero)
                            _, vertices_principal = brep.GetVertices() # type: ignore
                            if vertices_principal:
                                centro_manguito_x = sum(v.X for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_y = sum(v.Y for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_z = sum(v.Z for v in vertices_principal) / len(vertices_principal)
                            else:
                                centro_manguito_x = centro_brep_geom.X
                                centro_manguito_y = centro_brep_geom.Y
                                centro_manguito_z = centro_brep_geom.Z

                            # Guardar el centro para usar en todos los BREPs del manguito
                            if not hasattr(self, '_temp_manguito_center'):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (centro_manguito_x, centro_manguito_y, centro_manguito_z)
                        else:
                            # Usar el centro calculado del primer BREP
                            centro_manguito_x, centro_manguito_y, centro_manguito_z = self._temp_manguito_center.get(i, (0, 0, 0))

                        # 1. Resetear al origen usando el centro del BREP principal
                        # Esto mantiene la posicion relativa de los detalles
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            -centro_manguito_x + (longitud_original / 2.0),
                            -centro_manguito_y,
                            -centro_manguito_z
                        ))

                        # 2. Roll (spin on own axis before alignment)
                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        # 3. Align X axis to segment direction
                        ref_data = last_dynamic_data if last_dynamic_data is not None else data
                        brep = AllplanGeo.Transform(brep, self._build_alignment_matrix(ref_data.vector_normalizado))

                        # 4. Mover al punto medio del segmento del manguito
                        # El punto medio ya esta calculado correctamente
                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            punto_medio_x,
                            punto_medio_y,
                            punto_medio_z
                        ))

                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
                    # --- CASO 2: DIFUSORES ---
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0: move_offset = CONDUCTO_WIDTH/2
                        elif point_side == 2: move_offset = -CONDUCTO_WIDTH/2

                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})")

                        if point_role == "inicial":
                            # DIFUSOR INICIAL: Debe estar al inicio absoluto del conducto
                            # Buscar el primer segmento dinamico para obtener el punto de inicio real
                            punto_inicio_real = start_point

                            # Si el difusor no es el primer elemento, buscar el inicio del primer tubo
                            # Buscar el primer tubo despues del difusor
                            for j in range(i + 1, len(data_list)):
                                next_item = data_list[j]
                                next_tipo = next_item.get('type', "")
                                next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                # Encontrar el primer segmento dinamico
                                if next_tipo_str not in TIPOS_ACCESORIOS:
                                    next_data = next_item["segment"].data
                                    punto_inicio_real = getattr(next_data, 'start', start_point)
                                    if debug:
                                        print(f"  Usando inicio del segmento {j}: ({punto_inicio_real.X:.1f}, {punto_inicio_real.Y:.1f}, {punto_inicio_real.Z:.1f})")
                                    break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices() # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))

                            # Aplicar rotacion
                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(data.angulo_xy))
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular offset basado en angulo
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo  #(w_cubo if ang_int in [180, 178, 179] else move_offset)
                            offset_y = punto_inicio_real.Y + (move_offset if ang_int in [0, 180, 178, 179] else w_cubo)

                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                offset_x, offset_y - 1, punto_inicio_real.Z + 11
                            ))

                            if debug:
                                print(f"  Posición final difusor: ({offset_x:.1f}, {offset_y:.1f}, {punto_inicio_real.Z + 11:.1f})")

                        elif point_role == "final":
                            # DIFUSOR FINAL: Debe estar al final absoluto del conducto
                            # Buscar el ultimo segmento dinamico
                            punto_final_real = data.end if hasattr(data, 'end') else AllplanGeo.Point3D(
                                start_point.X + data.delta_x,
                                start_point.Y + data.delta_y,
                                start_point.Z + data.delta_z
                            )

                            # Si hay mas segmentos despues, buscar el final del ultimo tubo
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    next_item = data_list[j]
                                    next_tipo = next_item.get('type', "")
                                    next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                    # Encontrar el ultimo segmento dinamico
                                    if next_tipo_str not in TIPOS_ACCESORIOS:
                                        next_data = next_item["segment"].data
                                        punto_final_real = getattr(next_data, 'end', punto_final_real)
                                        if debug:
                                            print(f"  Usando final del segmento {j}: ({punto_final_real.X:.1f}, {punto_final_real.Y:.1f}, {punto_final_real.Z:.1f})")
                                        break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices() # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))
                            else:
                                centro_dif_z = 0

                            # Calcular rotacion para difusor final
                            rot_diff = 0
                            if ang_int == 0: rot_diff = 180
                            elif ang_int in [180, 179, 178]: rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]: rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_diff))
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular posicion final
                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 60

                            # Calcular desde el punto inicial al final
                            long_total_conducto = AllplanGeo.CalcLength(AllplanGeo.Line3D(
                                data_list[0]["segment"].data.start if data_list[0].get('type', '') not in TIPOS_ACCESORIOS else start_point,
                                punto_final_real
                            ))

                            if es_horizontal_pura:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                w_cubo = (long_total_conducto + padding) * factor
                                if ang_int in [180, 179, 178]:
                                    w_cubo = (-long_total_conducto - padding)

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    punto_final_real.X + (padding * factor),
                                    punto_final_real.Y + move_offset,
                                    punto_final_real.Z - centro_dif_z + 11
                                ))
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                w_cubo = (long_total_conducto + padding) * factor

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    punto_final_real.X + move_offset,
                                    punto_final_real.Y + (padding * factor),
                                    punto_final_real.Z - centro_dif_z + 11
                                ))
                        else:
                            # Caso por defecto (sin point_role definido)
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ))

                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
                    else:
                        # 1. Resetear al Origen (0,0,0) usando el centroide geometrico
                        # Esto asegura que las rotaciones se hagan sobre el centro de la pieza
                        nx = sum(v.X for v in vertices)/len(vertices) if vertices else 0
                        ny = sum(v.Y for v in vertices)/len(vertices) if vertices else 0
                        nz = sum(v.Z for v in vertices)/len(vertices) if vertices else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # tipo_segmento_val = getattr(data, 'tipo_segmento', '')
                        # if debug:
                        #     print(f"  [{item_name}] tipo_str={tipo_str!r}  tipo_segmento={tipo_segmento_val!r}  roll_final={roll_final:.3f}  aplica_rot={tipo_segmento_val in ('horizontal','vertical')}")
                        # if tipo_segmento_val in ('horizontal', 'vertical'):
                            # 2. Roll: angulo_rotacion base + roll_final por historial de inclinacion
                        total_roll = getattr(data, 'angulo_rotacion', 0.0) + roll_final
                        if abs(total_roll) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(total_roll))
                            brep = AllplanGeo.Transform(brep, m)

                        # 3. Align X axis to segment direction
                        brep = AllplanGeo.Transform(brep, self._build_alignment_matrix(data.vector_normalizado))

                        # Calcular el punto medio del segmento EXTENDIDO
                        # Punto medio = start + vec * (long_original/2 + (ext_final - ext_inicio)/2)
                        desplazamiento_neto = (longitud_original / 2.0) + ((extension_final - extension_inicio) / 2.0)

                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        # desplazamiento_centro = (extension_final - extension_inicio) / 2.0
                        # mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                        # mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                        # mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
                        if is_dinamic:
                            last_dynamic_data = data
            except Exception as e:
                if debug: print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v3(self,
                            data_list,
                            conducto_width=75,
                            color=None,
                            point_role=None,
                            point_side=None,
                            debug=True):
        """
        Versión robusta que ignora elementos intermedios (manguitos) para el cálculo
        de ángulos y asegura que todos los objetos se generen.
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg1:
                return False

            a1 = seg1.data.angulo_xy
            a2 = seg2.data.angulo_xy

            diff = abs((a1 - a2 + 180) % 360 - 180)
            return diff < tol_deg

        # CONSTANTES
        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment: continue
                data = segment.data
                item_name = getattr(segment, 'name', f"Segment_{i}")
                start_point = getattr(data, 'start', None)
                if start_point is None: continue
                tipo_str =  item.get('type', "")

                # 1. IDENTIFICAR TIPO
                # tipo_raw = item.get('type', "")
                # tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else tipo_raw)

                # NOTA: Ya no saltamos los manguitos, los procesamos
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, 'vector_normalizado', None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(getattr(data, 'delta_x', 0), getattr(data, 'delta_y', 0), getattr(data, 'delta_z', 0))
                    vec_curr.Normalize()

                #CONTINUIDAD ENTRE SEGMENTOS RECTOS
                if (

                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0
                desplazamiento_neto = 0.0

                # 3. LÓGICA DE CONEXIÓN (Solo para tubos dinámicos)
                # ── Extensiones en uniones (solo tubos dinámicos) ────────────────
                if is_dinamic:
                    vec_curr = data.vector_normalizado
                    SAFE_MAX_ANGLE = math.radians(175.0)

                    # Tolerancia para detectar 135° (por si hay decimales como 134.99)
                    ANGULO_ESPECIAL_RAD = math.radians(135.0)
                    TOLERANCIA = math.radians(1.0)

                    # 1. Extensión al INICIO
                    extension_inicio = 0.0
                    if i > 0:
                        prev_item = data_list[i - 1]
                        if prev_item.get('type') != "manguito":
                            vec_prev = prev_item["segment"].data.vector_normalizado
                            dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el inicio del segundo segmento del codo, recortamos
                                    extension_inicio = -15.4
                                    if debug: print(f"  {item_name} - Inicio: Detectado 135°, aplicando recorte -22.5")
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (CONDUCTO_WIDTH / 2.0) * math.tan(a_rad / 2.0)
                                    extension_inicio = extension_teorica

                    # 2. Extensión al FINAL
                    extension_final = 0.0
                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        if next_item.get('type') != "manguito":
                            vec_next = next_item["segment"].data.vector_normalizado
                            dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el final del primer segmento del codo, alargamos
                                    extension_final = 15.4
                                    if debug: print(f"  {item_name} - Final: Detectado 135°, aplicando alargue 22.5")
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (CONDUCTO_WIDTH / 2.0) * math.tan(a_rad / 2.0)
                                    extension_final = extension_teorica

                    # 3. Aplicación de longitud
                    longitud_original = getattr(data, 'longitud_3d', 0.0)
                    longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(f"  Long original: {longitud_original}")
                    print(f"  Ext inicio: {extension_inicio}, Ext final: {extension_final}")
                    print(f"  Long total: {longitud_total}")

                # 5. PROCESAR BREPS
                lista_elem_3d_modified = []
                list_elem_3d = item.get("element3d", [])

                if is_dinamic:
                    for elem_3d in list_elem_3d:
                        brep_ajustado = None
                        # Asumimos que esta función estira el BREP simétricamente desde el centro
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                # Procesar cada elemento 3D
                conn_type_list = []
                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color: prop.Color = color

                    brep = elem_3d.GetGeometryObject()
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
                        segment_brep = None
                        if e == 0:  # Solo calculamos centro y transformaciones con el primer BREP
                            # Recalcular el centro del BREP principal (el primero)
                            _, vertices_principal = brep.GetVertices() # type: ignore
                            if vertices_principal:
                                centro_manguito_x = sum(v.X for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_y = sum(v.Y for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_z = sum(v.Z for v in vertices_principal) / len(vertices_principal)
                            else:
                                centro_manguito_x = centro_brep_geom.X
                                centro_manguito_y = centro_brep_geom.Y
                                centro_manguito_z = centro_brep_geom.Z

                            # Guardar el centro para usar en todos los BREPs del manguito
                            if not hasattr(self, '_temp_manguito_center'):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (centro_manguito_x, centro_manguito_y, centro_manguito_z)
                        else:
                            # Usar el centro calculado del primer BREP
                            centro_manguito_x, centro_manguito_y, centro_manguito_z = self._temp_manguito_center.get(i, (0, 0, 0))

                        # 1. Resetear al origen usando el centro del BREP principal
                        # Esto mantiene la posición relativa de los detalles
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            -centro_manguito_x + (longitud_original / 2.0),
                            -centro_manguito_y,
                            -centro_manguito_z
                        ))

                        # 2. Calcular ángulos
                        rot_xy = 0.0 if getattr(data, 'longitud_xy', 0) < 0.1 else data.angulo_xy
                        rot_pitch = math.degrees(math.atan2(data.delta_z, getattr(data, 'longitud_xy', 0)))

                        # 3. Aplicar rotaciones: Roll
                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación)
                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # 4. Mover al punto medio del segmento del manguito
                        # El punto medio ya está calculado correctamente
                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            punto_medio_x,
                            punto_medio_y,
                            punto_medio_z
                        ))

                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
                    # --- CASO 2: DIFUSORES ---
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0: move_offset = CONDUCTO_WIDTH/2
                        elif point_side == 2: move_offset = -CONDUCTO_WIDTH/2

                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})")

                        if point_role == "inicial":
                            # DIFUSOR INICIAL: Debe estar al inicio absoluto del conducto
                            # Buscar el primer segmento dinámico para obtener el punto de inicio real
                            punto_inicio_real = start_point

                            # Si el difusor no es el primer elemento, buscar el inicio del primer tubo
                            # Buscar el primer tubo después del difusor
                            for j in range(i + 1, len(data_list)):
                                next_item = data_list[j]
                                next_tipo = next_item.get('type', "")
                                next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                # Encontrar el primer segmento dinámico
                                if next_tipo_str not in TIPOS_ACCESORIOS:
                                    next_data = next_item["segment"].data
                                    punto_inicio_real = getattr(next_data, 'start', start_point)
                                    if debug:
                                        print(f"  Usando inicio del segmento {j}: ({punto_inicio_real.X:.1f}, {punto_inicio_real.Y:.1f}, {punto_inicio_real.Z:.1f})")
                                    break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices() # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))

                            # Aplicar rotación
                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(data.angulo_xy))
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular offset basado en ángulo
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo  #(w_cubo if ang_int in [180, 178, 179] else move_offset)
                            offset_y = punto_inicio_real.Y + (move_offset if ang_int in [0, 180, 178, 179] else w_cubo)

                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                offset_x, offset_y - 1, punto_inicio_real.Z + 11
                            ))

                            if debug:
                                print(f"  Posición final difusor: ({offset_x:.1f}, {offset_y:.1f}, {punto_inicio_real.Z + 11:.1f})")

                        elif point_role == "final":
                            # DIFUSOR FINAL: Debe estar al final absoluto del conducto
                            # Buscar el último segmento dinámico
                            punto_final_real = data.end if hasattr(data, 'end') else AllplanGeo.Point3D(
                                start_point.X + data.delta_x,
                                start_point.Y + data.delta_y,
                                start_point.Z + data.delta_z
                            )

                            # Si hay más segmentos después, buscar el final del último tubo
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    next_item = data_list[j]
                                    next_tipo = next_item.get('type', "")
                                    next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                    # Encontrar el último segmento dinámico
                                    if next_tipo_str not in TIPOS_ACCESORIOS:
                                        next_data = next_item["segment"].data
                                        punto_final_real = getattr(next_data, 'end', punto_final_real)
                                        if debug:
                                            print(f"  Usando final del segmento {j}: ({punto_final_real.X:.1f}, {punto_final_real.Y:.1f}, {punto_final_real.Z:.1f})")
                                        break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices() # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))
                            else:
                                centro_dif_z = 0

                            # Calcular rotación para difusor final
                            rot_diff = 0
                            if ang_int == 0: rot_diff = 180
                            elif ang_int in [180, 179, 178]: rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]: rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_diff))
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular posición final
                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 60

                            # Calcular desde el punto inicial al final
                            long_total_conducto = AllplanGeo.CalcLength(AllplanGeo.Line3D(
                                data_list[0]["segment"].data.start if data_list[0].get('type', '') not in TIPOS_ACCESORIOS else start_point,
                                punto_final_real
                            ))

                            if es_horizontal_pura:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                w_cubo = (long_total_conducto + padding) * factor
                                if ang_int in [180, 179, 178]:
                                    w_cubo = (-long_total_conducto - padding)

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    punto_final_real.X + (padding * factor),
                                    punto_final_real.Y + move_offset,
                                    punto_final_real.Z - centro_dif_z + 11
                                ))
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                w_cubo = (long_total_conducto + padding) * factor

                                nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                    punto_final_real.X + move_offset,
                                    punto_final_real.Y + (padding * factor),
                                    punto_final_real.Z - centro_dif_z + 11
                                ))
                        else:
                            # Caso por defecto (sin point_role definido)
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ))

                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
                    else:
                        # 1. Resetear al Origen (0,0,0) usando el centroide geométrico
                        # Esto asegura que las rotaciones se hagan sobre el centro de la pieza
                        nx = sum(v.X for v in vertices)/len(vertices) if vertices else 0
                        ny = sum(v.Y for v in vertices)/len(vertices) if vertices else 0
                        nz = sum(v.Z for v in vertices)/len(vertices) if vertices else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # 2. Calcular Ángulos
                        rot_xy = 0.0 if getattr(data, 'longitud_xy', 0) < 0.1 else data.angulo_xy
                        rot_pitch = math.degrees(math.atan2(data.delta_z, getattr(data, 'longitud_xy', 0)))

                        # print("############################################## ITEMS ROT: ", rot_xy, rot_pitch)
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

                        # Calcular el punto medio del segmento EXTENDIDO
                        # Punto medio = start + vec * (long_original/2 + (ext_final - ext_inicio)/2)
                        desplazamiento_neto = (longitud_original / 2.0) + ((extension_final - extension_inicio) / 2.0)

                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        # desplazamiento_centro = (extension_final - extension_inicio) / 2.0
                        # mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                        # mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                        # mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })
            except Exception as e:
                if debug: print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def _get_rotation_strategy(self, data, info, roll_state: dict,
                               is_first: bool = False, next_data=None) -> float:
        """Evalua y actualiza el roll persistido basado en el historial de segmentos.

        Muta roll_state en el lugar cuando encuentra un segmento inclinado valido.
        Retorna el roll a aplicar (distinto de 0 solo para 'horizontal' o 'vertical').
        tipo_str es el tipo de componente (conducto_normal, manguito, etc.).
        La logica geometrica se basa en data.tipo_segmento (inclinado, horizontal, vertical).

        is_first : True cuando este es el primer segmento de data_list (i == 0).
        next_data: data del siguiente segmento (puede ser None).
        """
        tipo_segmento = getattr(data, 'tipo_segmento', '')
        angulo_z      = getattr(data, 'angulo_z', 0.0)
        sentido_z     = getattr(data, 'sentido_z', '')
        view_mode     = getattr(info, 'view_mode', '')

        # Caso especial: primer segmento vertical dibujado en vista ZX.
        # Se rota usando el angulo_xy del segmento siguiente (default 45.0).
        if (is_first
                and tipo_segmento in ['vertical']
                and view_mode in ['XZ', 'ZX']):
            angulo_xy_next = getattr(next_data, 'angulo_xy', 45.0) if next_data is not None else 45.0
            return angulo_xy_next

        if (is_first
                and tipo_segmento == 'inclinado'
                and view_mode == 'XYZ'):
            angulo_xy_next = getattr(next_data, 'angulo_xy', 45.0) if next_data is not None else 45.0
            vec_n = getattr(data, 'vector_normalizado')

            # if vec_n is not None:
            theta = math.degrees(math.acos(max(-1.0, min(1.0, float(vec_n.X)))))
            # else:
                # theta = abs(angulo_z)   # fallback si no hay vector_normalizado
            # sign = -1.0 if sentido_z == 'ascendente' else 1.0
            print("######### vec_n: ", vec_n, theta, angulo_z, theta + angulo_xy_next)
            # Actualizar roll_state para que el siguiente segmento horizontal herede el roll
            return  theta + angulo_xy_next

        if (tipo_segmento == 'inclinado' and view_mode not in ['XY', 'XYZ']
                and angulo_z != 0.0
                and sentido_z in ('ascendente', 'descendente')
                and angulo_z != roll_state['last_angulo_z']):
            sign = -1.0 if sentido_z == 'ascendente' else 1.0
            roll_state['roll_final']    = sign * abs(angulo_z)
            roll_state['last_angulo_z'] = angulo_z

        if tipo_segmento in ('horizontal', 'vertical'):
            return roll_state['roll_final']
        return 0.0

    def _build_alignment_matrix(self, vec_norm):
        """Rotation matrix aligning local X axis to vec_norm (Rodrigues formula)."""
        vx = vec_norm.X
        vy = vec_norm.Y
        vz = vec_norm.Z
        ax, ay, az = 0.0, -vz, vy
        sin_a = math.sqrt(ax * ax + ay * ay + az * az)
        cos_a = vx
        m = AllplanGeo.Matrix3D()
        if sin_a < 1e-9:
            if cos_a < 0:
                m.Rotation(AllplanGeo.Line3D(0, 0, 0, 0, 0, 1), AllplanGeo.Angle.FromDeg(180.0))
            return m
        angle_deg = math.degrees(math.atan2(sin_a, cos_a))
        m.Rotation(
            AllplanGeo.Line3D(0, 0, 0, ax / sin_a, ay / sin_a, az / sin_a),
            AllplanGeo.Angle.FromDeg(angle_deg)
        )
        return m

    def modificar_dimensiones_brep(self, model_element, nueva_longitud) -> AllplanBasisElements.ModelElement3D:
        """
        Escala un BREP en su eje longitudinal (X local) manteniendo su geometría original.
        """
        geo = model_element.GetGeometryObject()

        # Obtener dimensiones actuales
        _, vertices = geo.GetVertices()
        if not vertices:
            return model_element

        # Calcular longitud actual en X
        x_coords = [v.X for v in vertices]
        longitud_actual = max(x_coords) - min(x_coords)

        if abs(longitud_actual) < 0.001:  # Evitar división por cero
            return model_element

        # Calcular factor de escala
        factor_escala = nueva_longitud / longitud_actual

        # Crear matriz de transformación para escalar solo en X
        matriz = AllplanGeo.Matrix3D()
        matriz.Scaling(factor_escala, 1.0, 1.0)  # Escala X, mantiene Y y Z

        # Aplicar transformación
        nuevo_brep = AllplanGeo.Transform(geo, matriz)

        # Crear nuevo ModelElement con las mismas propiedades
        nuevo_model = AllplanBasisElements.ModelElement3D(
            model_element.GetCommonProperties(),
            nuevo_brep
        )
        # print(f"  Escalado BREP: {longitud_actual:.2f}mm → {nueva_longitud:.2f}mm (factor: {factor_escala:.3f})")
        return nuevo_model


class PipelineProcessor:
    def __init__(self, elem3D_list, element_type= None, debug=False):
        """
        Args:
            elem3D_list: [{'type': 'conducto', 'elem': model}, ...]
        """
        self.templates = {item['type']: item['elem'] for item in elem3D_list}
        self.debug = debug
        self.offset_codo = 220
        self.element_type_core = element_type

    def modificar_dimensiones_brep(self, model_element, nueva_longitud) -> AllplanBasisElements.ModelElement3D:
        """
        Escala un BREP en su eje longitudinal (X local) manteniendo su geometría original.
        """
        geo = model_element.GetGeometryObject()

        # Obtener dimensiones actuales
        _, vertices = geo.GetVertices()
        if not vertices:
            return model_element

        # Calcular longitud actual en X
        x_coords = [v.X for v in vertices]
        longitud_actual = max(x_coords) - min(x_coords)

        if abs(longitud_actual) < 0.001:  # Evitar división por cero
            return model_element

        # Calcular factor de escala
        factor_escala = nueva_longitud / longitud_actual

        # Crear matriz de transformación para escalar solo en X
        matriz = AllplanGeo.Matrix3D()
        matriz.Scaling(factor_escala, 1.0, 1.0)  # Escala X, mantiene Y y Z

        # Aplicar transformación
        nuevo_brep = AllplanGeo.Transform(geo, matriz)

        # Crear nuevo ModelElement con las mismas propiedades
        nuevo_model = AllplanBasisElements.ModelElement3D(
            model_element.GetCommonProperties(),
            nuevo_brep
        )
        # print(f"  Escalado BREP: {longitud_actual:.2f}mm → {nueva_longitud:.2f}mm (factor: {factor_escala:.3f})")
        return nuevo_model

    def _get_center_from_vertices(self, brep):
        """
        Calcula el centro geométrico promediando todos los vértices del BRep3D.
        Soluciona el error de firma de MinMax3D.
        """
        # Extraer los vértices del BRep
        error, vertices = brep.GetVertices()

        if error != 0 or not vertices:
            # Fallback en caso de que no haya vértices (poco probable)
            return AllplanGeo.Point3D(0, 0, 0)

        # Sumatoria de coordenadas
        sum_x = sum(v.X for v in vertices)
        sum_y = sum(v.Y for v in vertices)
        sum_z = sum(v.Z for v in vertices)
        n = len(vertices)

        return AllplanGeo.Point3D(sum_x / n, sum_y / n, sum_z / n)

    def obtener_rotacion_codo(self, v_salida, eps=1e-6):
        """
        Devuelve el ángulo de rotación del codo en grados
        respecto al primer codo (base).
        """
        v_base = AllplanGeo.Vector3D(1, 0, 0)

        dot = v_base.X * v_salida.X + v_base.Y * v_salida.Y
        cross_z = v_base.X * v_salida.Y - v_base.Y * v_salida.X

        # math.atan2 devuelve el ángulo exacto del giro entre los dos vectores
        angulo_rad = math.atan2(cross_z, dot)
        angulo_deg = math.degrees(angulo_rad)

        # Limpieza de precisión decimal para valores casi exactos (25, 30, 45, 90, etc.)
        if abs(angulo_deg - round(angulo_deg)) < eps:
            angulo_deg = float(round(angulo_deg))

        return angulo_deg

    def _aplicar_transformacion(self, model_element, segment_data, rotation_angle=0, elem_type="conducto",
                            custom_position=None, next_seg=None) -> AllplanBasisElements.ModelElement3D:
        """
        Aplica transformaciones separando lógica horizontal (XY) y vertical (ZX/Pitch).
        """
        prop = model_element.GetCommonProperties()
        brep = model_element.GetGeometryObject()

        # 1. POSICIONAMIENTO INICIAL
        # Determinamos el punto de inserción (vértice o centro)
        p_destino = custom_position if custom_position else segment_data.start

        # 2. NORMALIZACIÓN (ORIGEN 0,0,0)
        # Llevamos el objeto al centro para que las rotaciones no lo desplacen fuera de eje
        centro = self._get_center_from_vertices(brep)
        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro.X, -centro.Y, -centro.Z))

        # ==========================================
        # PARTE 1: TRANSFORMACIONES LOCALES (ROLL)
        # ==========================================
        if abs(rotation_angle) > 0.015:
            matriz_roll = AllplanGeo.Matrix3D()
            eje_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(1,0,0))
            matriz_roll.SetRotation(eje_x_local, AllplanGeo.Angle.FromDeg(rotation_angle))
            brep = AllplanGeo.Transform(brep, matriz_roll)

        # ==========================================
        # PARTE 2: LÓGICA VERTICAL (PITCH / ZX)
        # ==========================================
        # 2.1. Orientación Base (Poner de pie si el destino es vertical)
        # Si el codo debe ir en vertical, primero rotamos 90° en su eje X local
        if elem_type == "codo_90" and next_seg:
            angulo_rotacion = segment_data.angulo_z  if int(segment_data.angulo_z) != 0 else next_seg.angulo_z
            matriz_vertical = AllplanGeo.Matrix3D()
            eje_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(1,0,0))
            # Lo rotamos para que apunte hacia arriba/abajo antes de la rotación final
            matriz_vertical.SetRotation(eje_x_local, AllplanGeo.Angle.FromDeg(angulo_rotacion))
            brep = AllplanGeo.Transform(brep, matriz_vertical)

        # 2.2. Inclinación Específica (Pitch)
        angulo_pitch = 0.0
        if elem_type in ["conducto", "conexion"]:
            angulo_pitch = segment_data.angulo_z
        elif elem_type == "codo_90" and next_seg:
            angulo_pitch = -(next_seg.angulo_z + segment_data.angulo_z)
            if int(segment_data.angulo_z) in [90, -90] and int(next_seg.angulo_xy) == 0:
                angulo_pitch = (next_seg.angulo_z + segment_data.angulo_z)
            elif int(next_seg.angulo_xy) == 180:
                angulo_pitch = next_seg.angulo_xy *2

        if abs(angulo_pitch) > 0.01:
            matriz_pitch = AllplanGeo.Matrix3D()
            # Eje Y local como pivote de elevación
            eje_y_pitch = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,1,0))
            matriz_pitch.SetRotation(eje_y_pitch, AllplanGeo.Angle.FromDeg(-angulo_pitch))
            brep = AllplanGeo.Transform(brep, matriz_pitch)

        # ==========================================
        # PARTE 3: LÓGICA HORIZONTAL (YAW / XY)
        # ==========================================
        angulo_yaw = 0.0
        if elem_type in ["conducto", "conexion"]:
            angulo_yaw = segment_data.angulo_xy
        else:
            # AJUSTE ESPECIAL PARA CODOS
            v_entrada = next_seg.vector_normalizado # type: ignore
            v_salida = segment_data.vector_normalizado

            # Inversión de cara (Flip) si el giro es a la derecha
            cross_z = v_entrada.X * v_salida.Y - v_entrada.Y * v_salida.X
            if cross_z < 0:
                m_flip = AllplanGeo.Matrix3D()
                m_flip.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(1,0,0)),
                                AllplanGeo.Angle.FromDeg(180))
                brep = AllplanGeo.Transform(brep, m_flip)

            # Ángulo basado en la dirección de salida
            angulo_yaw = self.obtener_rotacion_codo(v_salida)

        # Aplicar rotación horizontal final
        matriz_yaw = AllplanGeo.Matrix3D()
        eje_z_global = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,0,1))
        matriz_yaw.Rotation(eje_z_global, AllplanGeo.Angle.FromDeg(angulo_yaw))
        brep = AllplanGeo.Transform(brep, matriz_yaw)

        # ==========================================
        # PARTE 4: AJUSTES DE ALINEACIÓN Y TRASLACIÓN
        # ==========================================
        if elem_type == "codo_90":
            # Alineamos el codo con la bisectriz para que encaje con los recortes
            v_bisector = AllplanGeo.Vector3D(v_entrada.X - v_salida.X,
                                            v_entrada.Y - v_salida.Y,
                                            v_entrada.Z - v_salida.Z)
            v_bisector.Normalize()
            dist_ajuste = (self.offset_codo / 2.0) - 2.3
            brep = AllplanGeo.Move(brep, v_bisector * dist_ajuste)

        # Traslado a la coordenada real en el espacio Allplan
        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(p_destino.X, p_destino.Y, p_destino.Z))

        return AllplanBasisElements.ModelElement3D(prop, brep)

    def process(self, segments, default_attrs=None) -> list:
        """
        Procesa los segmentos y ubica conductos, conexiones y codos
        con soporte para pendientes verticales (Pitch).
        """
        result_list = []
        num_seg = len(segments)
        element_index = 0  # Contador global de elementos
        grupo_index = 0

        for i, seg_item in enumerate(segments):
            seg = seg_item.data
            v_unit = seg.vector_normalizado

            # 1. DETERMINAR RECORTES (Offsets)
            # -------------------------------------------------------
            offset_inicio = 0.0
            offset_final = 0.0

            if i > 0:
                prev_seg = segments[i-1].data
                # Si hay cambio de dirección (giro), recortamos para el codo
                if abs(AllplanGeo.Vector3D.DotProduct(prev_seg.vector_normalizado, v_unit)) < 0.01:
                    offset_inicio = self.offset_codo

            if i < num_seg - 1:
                next_seg = segments[i+1].data
                # Si el siguiente tramo es un giro, recortamos al final
                if abs(AllplanGeo.Vector3D.DotProduct(v_unit, next_seg.vector_normalizado)) < 0.01:
                    offset_final = self.offset_codo

            # 2. AGREGAR CONDUCTO (PARTE RECTA)
            # -------------------------------------------------------
            if self.element_type_core in self.templates:
                longitud_recortada = seg.longitud_3d - offset_inicio - offset_final

                if longitud_recortada > 0:
                    # Calculamos el punto central del conducto en el espacio 3D
                    dist_al_centro = offset_inicio + (longitud_recortada / 2.0)
                    p_centro_conducto = AllplanGeo.Point3D(
                        seg.start.X + v_unit.X * dist_al_centro,
                        seg.start.Y + v_unit.Y * dist_al_centro,
                        seg.start.Z + v_unit.Z * dist_al_centro
                    )

                    model_cond = self.modificar_dimensiones_brep(self.templates[self.element_type_core], longitud_recortada)
                    # Aplicamos transformación (incluye inclinación vertical automática)
                    element = self._aplicar_transformacion(model_cond, seg, custom_position=p_centro_conducto)

                    result_list.append({
                        "element": element,
                        "element_type": self.element_type_core,
                        "index": element_index
                    })
                    element_index += 1


            # 3. AGREGAR CONEXIÓN DE INICIO (MANGUITO)
            # -------------------------------------------------------
            if offset_inicio > 0:
                # Ubicada exactamente donde termina el codo anterior y empieza el conducto
                p_inicio_con = AllplanGeo.Point3D(
                    seg.start.X + v_unit.X * offset_inicio,
                    seg.start.Y + v_unit.Y * offset_inicio,
                    seg.start.Z + v_unit.Z * offset_inicio
                )
                element = self._aplicar_transformacion(
                    self.templates["conexion"], seg,
                    elem_type="conexion",
                    custom_position=p_inicio_con
                )

                result_list.append({
                    "element": element,
                    "element_type": "conexion",
                    "index": grupo_index
                })
                grupo_index = element_index


            # 4. AGREGAR UNIONES FINALES (CODOS O CONEXIONES RECTAS)
            # -------------------------------------------------------
            if i < num_seg - 1:
                next_seg = segments[i+1].data
                v1 = seg.vector_normalizado
                v2 = next_seg.vector_normalizado
                dot = AllplanGeo.Vector3D.DotProduct(v1, v2)
                pos_nodo = seg.end

                # CASO A: TRAMO RECTO (Unión simple)
                if abs(dot) > 0.99:
                    element = self._aplicar_transformacion(
                        self.templates["conexion"], seg,
                        elem_type="conexion",
                        custom_position=pos_nodo
                    )

                    result_list.append({
                        "element": element,
                        "element_type": "conexion",
                        "index": element_index
                    })
                    element_index += 1
                # CASO B: GIRO A 90 GRADOS (Codo)
                elif abs(dot) < 0.01:
                    # Guardamos el índice del grupo (conexión + codo + conexión)
                    grupo_index = element_index

                    # Primero: Conexión al final del conducto antes del codo
                    p_final_con = AllplanGeo.Point3D(
                        seg.end.X - v_unit.X * offset_final,
                        seg.end.Y - v_unit.Y * offset_final,
                        seg.end.Z - v_unit.Z * offset_final
                    )
                    element_conexion_pre = self._aplicar_transformacion(
                        self.templates["conexion"], seg,
                        elem_type="conexion",
                        custom_position=p_final_con
                    )

                    result_list.append({
                        "element": element_conexion_pre,
                        "element_type": "conexion",
                        "index": grupo_index  # Mismo índice para el grupo
                    })

                    # Segundo: El Codo
                    element_codo = self._aplicar_transformacion(
                        self.templates["codo_90"],
                        seg,
                        elem_type="codo_90",
                        custom_position=pos_nodo,
                        next_seg=next_seg
                    )

                    result_list.append({
                        "element": element_codo,
                        "element_type": "codo_90",
                        "index": grupo_index  # Mismo índice para el grupo
                    })

                    element_index += 1  # Incrementamos solo una vez por grupo

                # CASO C: OTROS ÁNGULOS (Opcional)
                else:
                    element = self._aplicar_transformacion(
                        self.templates["conexion"], next_seg,
                        elem_type="conexion",
                        custom_position=pos_nodo
                    )

                    result_list.append({
                        "element": element,
                        "element_type": "conexion",
                        "index": element_index
                    })
                    element_index += 1

        return result_list
