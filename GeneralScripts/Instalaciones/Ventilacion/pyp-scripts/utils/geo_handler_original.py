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
                        point_role=None,
                        point_side=None,
                        debug=True):
        """
        Versión robusta que ignora elementos intermedios (manguitos) para el cálculo
        de ángulos y asegura que todos los objetos se generen.

        CAMBIO v3: Se agrega pre-procesado de rot_xy efectivo para cada segmento.
        Los segmentos verticales (longitud_xy ≈ 0) y los que cambian de plano
        heredan la orientación XY del segmento anterior o siguiente más cercano,
        evitando que rot_xy caiga a 0 por defecto.
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

        # =========================================================================
        # PRE-PROCESADO: Calcular effective_rot_xy para cada elemento
        #
        # Regla:
        #   - Si el segmento tiene componente XY (longitud_xy >= umbral): usa data.angulo_xy
        #   - Si es vertical puro o sin componente XY: busca hacia atrás el XY más
        #     cercano; si no lo hay, busca hacia adelante.
        #   - Para accesorios (manguitos, codos, etc.) se aplica la misma lógica.
        #
        # Esto resuelve tanto XY→ZX/ZY como ZX/ZY→XY en una sola pasada doble.
        # =========================================================================
        UMBRAL_XY = 0.1   # mm — por debajo de esto se considera sin componente XY

        raw_rot_xy = []   # None si el segmento no tiene orientación XY propia
        for item in data_list:
            seg = item.get("segment")
            if not seg:
                raw_rot_xy.append(None)
                continue
            d = seg.data
            long_xy = getattr(d, 'longitud_xy', 0.0)
            if long_xy >= UMBRAL_XY:
                raw_rot_xy.append(d.angulo_xy)
            else:
                raw_rot_xy.append(None)   # vertical puro → hereda de vecinos

        # Primer sub-pase: rellena con el vecino anterior conocido
        last_known = None
        for idx in range(len(raw_rot_xy)):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            else:
                raw_rot_xy[idx] = last_known   # puede quedar None si es el primero

        # Segundo sub-pase: rellena con el vecino siguiente (para los que aún son None)
        last_known = None
        for idx in range(len(raw_rot_xy) - 1, -1, -1):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            else:
                raw_rot_xy[idx] = last_known   # puede quedar None si no hay ninguno

        # Convertir None residuales a 0.0 (caso extremo: lista sin segmentos XY)
        effective_rot_xy = [v if v is not None else 0.0 for v in raw_rot_xy]

        if debug:
            print(f"\n--- effective_rot_xy pre-calculado ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, 'name', f"Seg_{idx}") if seg else f"Item_{idx}"
                orig = getattr(getattr(seg, 'data', None), 'angulo_xy', '?') if seg else '?'
                print(f"  [{idx}] {name}: angulo_xy_original={orig} → effective_rot_xy={effective_rot_xy[idx]}")
            print()
        # =========================================================================
        # FIN PRE-PROCESADO
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment: continue
                data = segment.data
                item_name = getattr(segment, 'name', f"Segment_{i}")
                start_point = getattr(data, 'start', None)
                if start_point is None: continue
                tipo_str = item.get('type', "")

                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, 'vector_normalizado', None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, 'delta_x', 0),
                        getattr(data, 'delta_y', 0),
                        getattr(data, 'delta_z', 0)
                    )
                    vec_curr.Normalize()

                # CONTINUIDAD ENTRE SEGMENTOS RECTOS
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
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175
                    MAX_ANGLE_RAD = math.pi - 0.0175

                    # --- VECINO ANTERIOR ---
                    if i > 0:
                        prev_idx = i - 1
                        prev_item = data_list[prev_idx]
                        prev_tipo_raw = prev_item.get('type', "")
                        prev_tipo_str = prev_tipo_raw if isinstance(prev_tipo_raw, str) else (prev_tipo_raw[0] if len(prev_tipo_raw) > 0 else "")

                        if prev_tipo_str == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(f"  {item_name} - Manguito anterior detectado, ext inicio = 0")
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(p_data.delta_x, p_data.delta_y, p_data.delta_z)
                            vec_prev.Normalize()
                            dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                            angle_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < angle_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)
                                if debug:
                                    print(f"  {item_name} - Ext inicio: {math.degrees(angle_rad):.1f}° → {extension_inicio:.2f}mm")
                            else:
                                extension_inicio = 0.0
                                if debug:
                                    print(f"  {item_name} - Ángulo insignificante ({math.degrees(angle_rad):.1f}°), ext inicio = 0")

                    # --- VECINO SIGUIENTE ---
                    if i < len(data_list) - 1:
                        next_idx = i + 1
                        next_item = data_list[next_idx]
                        next_tipo_raw = next_item.get('type', "")
                        next_tipo_str = next_tipo_raw if isinstance(next_tipo_raw, str) else (next_tipo_raw[0] if len(next_tipo_raw) > 0 else "")

                        if next_tipo_str == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(f"  {item_name} - Manguito siguiente detectado, ext final = 0")
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(n_data.delta_x, n_data.delta_y, n_data.delta_z)
                            vec_next.Normalize()
                            dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                            angle_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < angle_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(angle_rad / 2.0)
                                if debug:
                                    print(f"  {item_name} - Ext final: {math.degrees(angle_rad):.1f}° → {extension_final:.2f}mm")
                            else:
                                extension_final = 0.0
                                if debug:
                                    print(f"  {item_name} - Ángulo insignificante ({math.degrees(angle_rad):.1f}°), ext final = 0")

                # 4. GEOMETRÍA FINAL DEL SEGMENTO
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
                        brep_ajustado = self.modificar_dimensiones_brep(elem_3d, longitud_total)
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                conn_type_list = []
                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color: prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, vertices = brep.GetVertices()

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
                        if e == 0:
                            _, vertices_principal = brep.GetVertices()
                            if vertices_principal:
                                centro_manguito_x = sum(v.X for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_y = sum(v.Y for v in vertices_principal) / len(vertices_principal)
                                centro_manguito_z = sum(v.Z for v in vertices_principal) / len(vertices_principal)
                            else:
                                centro_manguito_x = centro_brep_geom.X
                                centro_manguito_y = centro_brep_geom.Y
                                centro_manguito_z = centro_brep_geom.Z
                            if not hasattr(self, '_temp_manguito_center'):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (centro_manguito_x, centro_manguito_y, centro_manguito_z)
                        else:
                            centro_manguito_x, centro_manguito_y, centro_manguito_z = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            -centro_manguito_x + (longitud_original / 2.0),
                            -centro_manguito_y,
                            -centro_manguito_z
                        ))

                        # *** CAMBIO: usar effective_rot_xy en lugar de data.angulo_xy raw ***
                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(math.atan2(data.delta_z, getattr(data, 'longitud_xy', 0)))

                        if debug:
                            long_xy_val = getattr(data, 'longitud_xy', 0)
                            print(f"  {item_name} [manguito] rot_xy={rot_xy:.2f}° (longitud_xy={long_xy_val:.3f}) rot_pitch={rot_pitch:.2f}°")

                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        m = AllplanGeo.Matrix3D()
                        m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                            punto_medio_x, punto_medio_y, punto_medio_z
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
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                next_item = data_list[j]
                                next_tipo = next_item.get('type', "")
                                next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                if next_tipo_str not in TIPOS_ACCESORIOS:
                                    next_data = next_item["segment"].data
                                    punto_inicio_real = getattr(next_data, 'start', start_point)
                                    if debug:
                                        print(f"  Usando inicio del segmento {j}: ({punto_inicio_real.X:.1f}, {punto_inicio_real.Y:.1f}, {punto_inicio_real.Z:.1f})")
                                    break

                            _, vertices_dif = brep.GetVertices()
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))

                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(data.angulo_xy))
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (move_offset if ang_int in [0, 180, 178, 179] else w_cubo)

                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                offset_x, offset_y - 1, punto_inicio_real.Z + 11
                            ))

                            if debug:
                                print(f"  Posición final difusor: ({offset_x:.1f}, {offset_y:.1f}, {punto_inicio_real.Z + 11:.1f})")

                        elif point_role == "final":
                            punto_final_real = data.end if hasattr(data, 'end') else AllplanGeo.Point3D(
                                start_point.X + data.delta_x,
                                start_point.Y + data.delta_y,
                                start_point.Z + data.delta_z
                            )

                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    next_item = data_list[j]
                                    next_tipo = next_item.get('type', "")
                                    next_tipo_str = next_tipo if isinstance(next_tipo, str) else (next_tipo[0] if len(next_tipo) > 0 else "")
                                    if next_tipo_str not in TIPOS_ACCESORIOS:
                                        next_data = next_item["segment"].data
                                        punto_final_real = getattr(next_data, 'end', punto_final_real)
                                        if debug:
                                            print(f"  Usando final del segmento {j}: ({punto_final_real.X:.1f}, {punto_final_real.Y:.1f}, {punto_final_real.Z:.1f})")
                                        break

                            _, vertices_dif = brep.GetVertices()
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(vertices_dif)
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(vertices_dif)
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(vertices_dif)
                                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro_dif_x, -centro_dif_y, -centro_dif_z))
                            else:
                                centro_dif_z = 0

                            rot_diff = 0
                            if ang_int == 0: rot_diff = 180
                            elif ang_int in [180, 179, 178]: rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]: rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_diff))
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 60

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
                            nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ))

                        elementos_transformados.append({
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        })

                    # --- CASO 3: TUBOS DINÁMICOS Y RESTO ---
                    else:
                        nx = sum(v.X for v in vertices)/len(vertices) if vertices else 0
                        ny = sum(v.Y for v in vertices)/len(vertices) if vertices else 0
                        nz = sum(v.Z for v in vertices)/len(vertices) if vertices else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # *** CAMBIO PRINCIPAL: usar effective_rot_xy en lugar de data.angulo_xy raw ***
                        # Antes:  rot_xy = 0.0 if getattr(data, 'longitud_xy', 0) < 0.1 else data.angulo_xy
                        # Ahora:  siempre se usa el valor pre-calculado que hereda del vecino XY
                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(math.atan2(data.delta_z, getattr(data, 'longitud_xy', 0)))

                        if debug:
                            long_xy_val = getattr(data, 'longitud_xy', 0)
                            print(f"  {item_name} rot_xy={rot_xy:.2f}° (longitud_xy={long_xy_val:.3f}) rot_pitch={rot_pitch:.2f}°")

                        # Roll
                        if abs(getattr(data, 'angulo_rotacion', 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(AllplanGeo.Line3D(0,0,0, 1,0,0), AllplanGeo.Angle.FromDeg(data.angulo_rotacion))
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta) — usa el ángulo efectivo (heredado si es vertical)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(AllplanGeo.Line3D(0,0,0, 0,0,1), AllplanGeo.Angle.FromDeg(rot_xy))
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación) — el eje de rotación usa rot_xy efectivo para
                        # que el pitch se aplique en el plano correcto aun cuando longitud_xy=0
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(0,0,0, math.sin(rad_xy), -math.cos(rad_xy), 0)
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        desplazamiento_neto = (longitud_original / 2.0) + ((extension_final - extension_inicio) / 2.0)

                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z))
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as e:
                if debug: print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v2(self,
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

    def modificar_dimensiones_brep_v1(self, model_element, nueva_longitud) -> AllplanBasisElements.ModelElement3D:
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

