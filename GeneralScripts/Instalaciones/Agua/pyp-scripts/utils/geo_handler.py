import math
import os
import importlib.util
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Utility as PythonUtility

from typing import List


class GeometryHandler:
    def center_and_connect_models_v10(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v11.

        REGLA SIMPLIFICADA — solo el segmento FRONTERA rota en la transición:
        ──────────────────────────────────────────────────────────────────────
        Dado un cambio de plano entre dos segmentos consecutivos:

          ... XZ[n-1]  XZ[n]  |  XY[n+1]  XY[n+2] ...
                          ↑ frontera fin

          ... XY[n-1]  XY[n]  |  XZ[n+1]  XZ[n+2] ...
                                       ↑ frontera inicio

        Solo el segmento inmediatamente adyacente a la transición recibe
        el adjacent_xy_roll del segmento XY contiguo.
        El resto del grupo XZ/YZ solo recibe el extra_roll de +90°.

        Además, el segmento frontera se recorta TRIM_BOUNDARY mm para
        evitar solapamiento en la unión.

        Tabla de resultados para los 6 segmentos del documento:
          line_1 (XZ) → roll=90°  (solo +view, no es frontera)
          line_2 (XZ) → roll=90°  (solo +view, no es frontera)
          line_3 (XZ) → roll=135° (+view+45°, ES frontera con line_4) + trim 10mm
          line_4 (XY) → roll=0°   (plano XY normal)
          line_5 (XY) → roll=0°
          line_6 (XY) → roll=0°
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        TRIM_BOUNDARY = 20.0  # mm de recorte en el segmento frontera

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_Z = 0.1

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # =====================================================================
        # PASO 1: recopilar view_mode y angulo_xy
        # =====================================================================
        seg_view_modes = []
        seg_angulo_xy = []
        for item in data_list:
            seg = item.get("segment")
            if seg:
                seg_view_modes.append(getattr(seg, "view_mode", "XY"))
                seg_angulo_xy.append(getattr(seg.data, "angulo_xy", 0.0))
            else:
                seg_view_modes.append("XY")
                seg_angulo_xy.append(0.0)

        # =====================================================================
        # PASO 2: detectar grupos por view_mode
        # =====================================================================
        grupos = []
        if data_list:
            vm_actual = seg_view_modes[0]
            idx_inicio = 0
            for idx in range(1, len(data_list)):
                if seg_view_modes[idx] != vm_actual:
                    grupos.append((vm_actual, list(range(idx_inicio, idx))))
                    vm_actual = seg_view_modes[idx]
                    idx_inicio = idx
            grupos.append((vm_actual, list(range(idx_inicio, len(data_list)))))

        if debug:
            print(f"\n--- Grupos detectados por view_mode ---")
            for g_vm, g_idx in grupos:
                names = [
                    getattr(data_list[k].get("segment"), "name", f"Seg_{k}")
                    for k in g_idx
                    if data_list[k].get("segment")
                ]
                print(f"  [{g_vm}] indices={g_idx} → {names}")
            print()

        # =====================================================================
        # PASO 3: effective_yaw  (dirección de viaje propia)
        #
        # · Grupo XY   → propio angulo_xy con herencia delta_z interna
        # · Grupo XZ/YZ → propio angulo_xy individual de cada segmento
        # =====================================================================
        effective_yaw = [0.0] * len(data_list)
        for g_vm, g_idx in grupos:
            if g_vm == "XY":
                last_xy_angle = None
                for k in g_idx:
                    seg = data_list[k].get("segment")
                    if not seg:
                        effective_yaw[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )
                        continue
                    dz = abs(getattr(seg.data, "delta_z", 0.0))
                    if dz < UMBRAL_Z:
                        last_xy_angle = getattr(seg.data, "angulo_xy", 0.0)
                        effective_yaw[k] = last_xy_angle
                    else:
                        effective_yaw[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )
            else:
                for k in g_idx:
                    seg = data_list[k].get("segment")
                    effective_yaw[k] = (
                        getattr(seg.data, "angulo_xy", 0.0) if seg else 0.0
                    )

        # =====================================================================
        # PASO 4: extra_roll_by_view (+90° solo para XZ/YZ)
        # =====================================================================
        extra_roll_by_view = [
            90.0 if seg_view_modes[i] in ("XZ", "YZ") else 0.0
            for i in range(len(data_list))
        ]

        # =====================================================================
        # PASO 5: adjacent_xy_roll  +  boundary_trim
        #
        # Solo el segmento FRONTERA (inmediatamente en la transición) recibe
        # el ángulo del grupo XY adyacente.
        # Todos los demás segmentos del grupo XZ/YZ → 0°.
        #
        # Frontera FIN   → último  segmento del grupo XZ/YZ antes de un XY
        #                  toma angulo_xy del PRIMER segmento del grupo XY siguiente
        # Frontera INICIO → primer segmento del grupo XZ/YZ después de un XY
        #                   toma angulo_xy del ÚLTIMO segmento del grupo XY anterior
        #
        # boundary_trim[i] = True si ese segmento es frontera y debe recortarse.
        # =====================================================================
        adjacent_xy_roll = [0.0] * len(data_list)
        boundary_trim = [False] * len(data_list)

        for g_num, (g_vm, g_idx) in enumerate(grupos):
            if g_vm == "XY":
                continue

            # ── Frontera FIN: XZ/YZ → XY ─────────────────────────────────────
            # Buscar grupo XY inmediatamente siguiente
            for g2_vm, g2_idx in grupos[g_num + 1 :]:
                if g2_vm == "XY" and g2_idx:
                    frontera_idx = g_idx[-1]  # último del grupo XZ/YZ
                    ref_angle = seg_angulo_xy[g2_idx[0]]
                    adjacent_xy_roll[frontera_idx] = ref_angle
                    boundary_trim[frontera_idx] = True
                    if debug:
                        fn = getattr(
                            data_list[frontera_idx].get("segment"),
                            "name",
                            f"Seg_{frontera_idx}",
                        )
                        rn = getattr(
                            data_list[g2_idx[0]].get("segment"),
                            "name",
                            f"Seg_{g2_idx[0]}",
                        )
                        print(
                            f"  Frontera FIN  [{frontera_idx}]{fn} "
                            f"← angulo_xy de [{g2_idx[0]}]{rn} = {ref_angle:.2f}°  "
                            f"(trim={TRIM_BOUNDARY}mm)"
                        )
                break  # solo el grupo XY inmediatamente siguiente

            # ── Frontera INICIO: XY → XZ/YZ ──────────────────────────────────
            # Buscar grupo XY inmediatamente anterior
            for g2_vm, g2_idx in reversed(grupos[:g_num]):
                if g2_vm == "XY" and g2_idx:
                    frontera_idx = g_idx[0]  # primero del grupo XZ/YZ
                    ref_angle = seg_angulo_xy[g2_idx[-1]]
                    adjacent_xy_roll[frontera_idx] = ref_angle
                    boundary_trim[frontera_idx] = True
                    if debug:
                        fn = getattr(
                            data_list[frontera_idx].get("segment"),
                            "name",
                            f"Seg_{frontera_idx}",
                        )
                        rn = getattr(
                            data_list[g2_idx[-1]].get("segment"),
                            "name",
                            f"Seg_{g2_idx[-1]}",
                        )
                        print(
                            f"  Frontera INI  [{frontera_idx}]{fn} "
                            f"← angulo_xy de [{g2_idx[-1]}]{rn} = {ref_angle:.2f}°  "
                            f"(trim={TRIM_BOUNDARY}mm)"
                        )
                break  # solo el grupo XY inmediatamente anterior

        # =====================================================================
        # DEBUG — tabla resumen
        # =====================================================================
        if debug:
            print(f"\n--- Tabla de rotaciones por segmento (v11) ---")
            print(
                f"  {'i':<3} {'nombre':<12} {'vm':<4} {'ang_xy':>8} "
                f"{'yaw':>8} {'+view':>6} {'+adj':>6} {'roll':>7} {'trim':>5}"
            )
            print(f"  {'-'*68}")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                vm = seg_view_modes[idx]
                ang = seg_angulo_xy[idx]
                yaw = effective_yaw[idx]
                ev = extra_roll_by_view[idx]
                ar = adjacent_xy_roll[idx]
                seg_ar = getattr(seg.data, "angulo_rotacion", 0) if seg else 0
                total_r = seg_ar + ev + ar
                trim = f"{TRIM_BOUNDARY:.0f}mm" if boundary_trim[idx] else "—"
                print(
                    f"  {idx:<3} {name:<12} {vm:<4} {ang:>8.2f}° "
                    f"{yaw:>8.2f}° {ev:>5.0f}° {ar:>5.0f}° {total_r:>6.1f}° {trim:>5}"
                )
            print()

        # =====================================================================
        # LOOP PRINCIPAL
        # =====================================================================
        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

                # ── Extensiones en uniones (solo tubos dinámicos) ─────────────
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175
                    MAX_ANGLE_RAD = math.pi - 0.0175

                    if i > 0:
                        prev_item = data_list[i - 1]
                        prev_tipo_s = prev_item.get("type", "")
                        prev_tipo_s = (
                            prev_tipo_s
                            if isinstance(prev_tipo_s, str)
                            else (prev_tipo_s[0] if prev_tipo_s else "")
                        )
                        if prev_tipo_s == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito anterior → ext_inicio=0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_inicio: {math.degrees(a_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )

                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        next_tipo_s = next_item.get("type", "")
                        next_tipo_s = (
                            next_tipo_s
                            if isinstance(next_tipo_s, str)
                            else (next_tipo_s[0] if next_tipo_s else "")
                        )
                        if next_tipo_s == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito siguiente → ext_final=0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_final: {math.degrees(a_rad):.1f}° → {extension_final:.2f}mm"
                                    )

                longitud_original = getattr(data, "longitud_3d", 0.0)

                # ── Recorte de 10mm si es segmento frontera ───────────────────
                if boundary_trim[i] and is_dinamic:
                    longitud_original = max(0.0, longitud_original - TRIM_BOUNDARY)
                    if debug:
                        print(
                            f"  {item_name} [FRONTERA] longitud recortada "
                            f"{TRIM_BOUNDARY}mm → {longitud_original:.2f}mm"
                        )

                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | "
                        f"ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0
                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        rot_xy = effective_yaw[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )
                        total_roll_m = (
                            getattr(data, "angulo_rotacion", 0)
                            + extra_roll_by_view[i]
                            + adjacent_xy_roll[i]
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] "
                                f"vm={seg_view_modes[i]} | yaw={rot_xy:.2f}° | "
                                f"pitch={rot_pitch:.2f}° | roll={total_roll_m:.1f}°"
                            )

                        if abs(total_roll_m) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_m),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        rot_xy = effective_yaw[i]
                        long_xy_seg = getattr(data, "longitud_xy", 0.0)
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))
                        total_roll_t = (
                            getattr(data, "angulo_rotacion", 0)
                            + extra_roll_by_view[i]
                            + adjacent_xy_roll[i]
                        )

                        if debug:
                            frontera_tag = " [FRONTERA]" if boundary_trim[i] else ""
                            print(
                                f"  {item_name}{frontera_tag} "
                                f"[vm={seg_view_modes[i]}] "
                                f"yaw={rot_xy:.2f}° | pitch={rot_pitch:.2f}° | "
                                f"roll={total_roll_t:.1f}° "
                                f"(+view={extra_roll_by_view[i]:.0f}° "
                                f"+adj={adjacent_xy_roll[i]:.0f}°)"
                            )

                        # 1) Roll total
                        if abs(total_roll_t) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_t),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # 2) Yaw
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # 3) Pitch
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        desplazamiento_neto = (
                            longitud_original / 2.0
                            + (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v9(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v9.

        SEPARACIÓN EXPLÍCITA DE YAW y ROLL DE SECCIÓN TRANSVERSAL:
        ────────────────────────────────────────────────────────────
        En v8 el ángulo del grupo XY adyacente se usaba como YAW para los
        segmentos XZ/YZ, lo que provocaba que line_2 y line_3 viajaran en el
        plano equivocado (su eje de pitch quedaba rotado 45° mal).

        Solución v9: dos tablas independientes.

        ① effective_yaw[i]
           · Grupo XY  → propio angulo_xy (con herencia delta_z interna).
           · Grupo XZ/YZ → propio angulo_xy de CADA segmento (0° en el
             ejemplo: line_1/2/3 viajan en el plano XZ).
           Se usa exclusivamente para la rotación de YAW (alrededor de Z)
           y para el eje del PITCH.

        ② adjacent_xy_roll[i]
           · Grupo XY  → 0°.
           · Grupo XZ/YZ → angulo_xy del primer segmento del grupo XY
             siguiente (forward) o del último del grupo XY anterior
             (backward).  0° si no hay grupo XY adyacente.
           Se suma al roll total para orientar la sección transversal
           en la dirección del conducto XY al que se conecta.

        Roll total = angulo_rotacion + extra_roll_by_view + adjacent_xy_roll
                                        (90° si XZ/YZ)

        Ejemplo con los segmentos del documento:
          line_1 (XZ, Δz=0)    → yaw=0°   | roll=0+90+45=135° | pitch=0°
          line_2 (XZ, Δz≠0)    → yaw=0°   | roll=0+90+45=135° | pitch=45°
          line_3 (XZ, vertical) → yaw=0°   | roll=0+90+45=135° | pitch=90°
          line_4 (XY, 45°)      → yaw=45°  | roll=0            | pitch=0°
          line_5 (XY, 90°)      → yaw=90°  | roll=0            | pitch=0°
          line_6 (XY, 180°)     → yaw=180° | roll=0            | pitch=0°
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_Z = 0.1  # mm

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # =========================================================================
        # PRE-PROCESADO PASO 1: recopilar view_mode y angulo_xy por segmento
        # =========================================================================
        seg_view_modes = []
        seg_angulo_xy = []
        for item in data_list:
            seg = item.get("segment")
            if seg:
                seg_view_modes.append(getattr(seg, "view_mode", "XY"))
                seg_angulo_xy.append(getattr(seg.data, "angulo_xy", 0.0))
            else:
                seg_view_modes.append("XY")
                seg_angulo_xy.append(0.0)

        # =========================================================================
        # PRE-PROCESADO PASO 2: detectar grupos por view_mode
        # =========================================================================
        grupos = []
        if data_list:
            vm_actual = seg_view_modes[0]
            idx_inicio = 0
            for idx in range(1, len(data_list)):
                if seg_view_modes[idx] != vm_actual:
                    grupos.append((vm_actual, list(range(idx_inicio, idx))))
                    vm_actual = seg_view_modes[idx]
                    idx_inicio = idx
            grupos.append((vm_actual, list(range(idx_inicio, len(data_list)))))

        if debug:
            print(f"\n--- Grupos detectados por view_mode ---")
            for g_vm, g_idx in grupos:
                names = [
                    getattr(data_list[k].get("segment"), "name", f"Seg_{k}")
                    for k in g_idx
                    if data_list[k].get("segment")
                ]
                print(f"  {g_vm}: indices={g_idx} → {names}")
            print()

        # =========================================================================
        # PRE-PROCESADO PASO 3: effective_yaw  (solo para la rotación de viaje)
        #
        # · Grupo XY  → propio angulo_xy con herencia delta_z interna.
        # · Grupo XZ/YZ → propio angulo_xy de CADA segmento individual.
        #   (NO hereda del grupo XY adyacente — eso va en adjacent_xy_roll)
        # =========================================================================
        effective_yaw = [0.0] * len(data_list)

        for g_vm, g_idx in grupos:
            if g_vm == "XY":
                # Herencia delta_z dentro del grupo XY
                last_xy_angle = None
                for k in g_idx:
                    seg = data_list[k].get("segment")
                    if not seg:
                        effective_yaw[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )
                        continue
                    dz = abs(getattr(seg.data, "delta_z", 0.0))
                    if dz < UMBRAL_Z:
                        last_xy_angle = getattr(seg.data, "angulo_xy", 0.0)
                        effective_yaw[k] = last_xy_angle
                    else:
                        effective_yaw[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )
            else:
                # XZ / YZ: cada segmento usa su propio angulo_xy
                for k in g_idx:
                    seg = data_list[k].get("segment")
                    effective_yaw[k] = (
                        getattr(seg.data, "angulo_xy", 0.0) if seg else 0.0
                    )

        # =========================================================================
        # PRE-PROCESADO PASO 4: adjacent_xy_roll
        #
        # Para grupos XZ/YZ: ángulo del primer segmento XY adyacente.
        # Se aplica como ROLL adicional para orientar la sección transversal
        # de manera que coincida con la cara del conducto XY contiguo.
        # Grupos XY → 0° (no necesitan corrección).
        # =========================================================================
        adjacent_xy_roll = [0.0] * len(data_list)

        for g_num, (g_vm, g_idx) in enumerate(grupos):
            if g_vm == "XY":
                continue  # grupos XY no necesitan roll adicional

            ref_angle = None

            # Buscar hacia adelante: primer grupo XY posterior
            for g2_vm, g2_idx in grupos[g_num + 1 :]:
                if g2_vm == "XY" and g2_idx:
                    ref_angle = seg_angulo_xy[g2_idx[0]]
                    if debug:
                        ref_name = getattr(
                            data_list[g2_idx[0]].get("segment"),
                            "name",
                            f"Seg_{g2_idx[0]}",
                        )
                        print(
                            f"  Grupo {g_vm} {g_idx}: adjacent_xy_roll FORWARD → "
                            f"{ref_name} angulo_xy={ref_angle:.2f}°"
                        )
                    break

            # Si no hay XY adelante, buscar hacia atrás
            if ref_angle is None:
                for g2_vm, g2_idx in reversed(grupos[:g_num]):
                    if g2_vm == "XY" and g2_idx:
                        ref_angle = seg_angulo_xy[g2_idx[-1]]
                        if debug:
                            ref_name = getattr(
                                data_list[g2_idx[-1]].get("segment"),
                                "name",
                                f"Seg_{g2_idx[-1]}",
                            )
                            print(
                                f"  Grupo {g_vm} {g_idx}: adjacent_xy_roll BACKWARD → "
                                f"{ref_name} angulo_xy={ref_angle:.2f}°"
                            )
                        break

            if ref_angle is None:
                ref_angle = 0.0
                if debug:
                    print(f"  Grupo {g_vm} {g_idx}: sin ref XY → adjacent_xy_roll=0°")

            for k in g_idx:
                adjacent_xy_roll[k] = ref_angle

        # =========================================================================
        # PRE-PROCESADO PASO 5: extra_roll_by_view  (+90° para XZ/YZ)
        # =========================================================================
        extra_roll_by_view = [
            90.0 if seg_view_modes[idx] in ("XZ", "YZ") else 0.0
            for idx in range(len(data_list))
        ]

        if debug:
            print(f"\n--- Tabla de rotaciones por segmento (v9) ---")
            print(
                f"  {'idx':<4} {'nombre':<12} {'vm':<4} {'ang_xy':>8} "
                f"{'yaw':>8} {'+view':>6} {'+adj':>6} {'roll_total':>10}"
            )
            print(f"  {'-'*70}")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                vm = seg_view_modes[idx]
                ang = seg_angulo_xy[idx]
                yaw = effective_yaw[idx]
                ev = extra_roll_by_view[idx]
                ar = adjacent_xy_roll[idx]
                seg_ar = getattr(seg.data, "angulo_rotacion", 0) if seg else 0
                total_r = seg_ar + ev + ar
                print(
                    f"  {idx:<4} {name:<12} {vm:<4} {ang:>8.2f}° "
                    f"{yaw:>8.2f}° {ev:>5.0f}° {ar:>5.0f}° {total_r:>9.1f}°"
                )
            print()
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

                # ── Extensiones en uniones (solo tubos dinámicos) ────────────────
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175
                    MAX_ANGLE_RAD = math.pi - 0.0175

                    if i > 0:
                        prev_item = data_list[i - 1]
                        prev_tipo_s = prev_item.get("type", "")
                        prev_tipo_s = (
                            prev_tipo_s
                            if isinstance(prev_tipo_s, str)
                            else (prev_tipo_s[0] if prev_tipo_s else "")
                        )
                        if prev_tipo_s == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito anterior → ext_inicio=0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_inicio: {math.degrees(a_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )

                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        next_tipo_s = next_item.get("type", "")
                        next_tipo_s = (
                            next_tipo_s
                            if isinstance(next_tipo_s, str)
                            else (next_tipo_s[0] if next_tipo_s else "")
                        )
                        if next_tipo_s == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito siguiente → ext_final=0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_final: {math.degrees(a_rad):.1f}° → {extension_final:.2f}mm"
                                    )

                longitud_original = getattr(data, "longitud_3d", 0.0)
                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | "
                        f"ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    # Punto medio geométrico
                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0
                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        rot_xy = effective_yaw[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )
                        total_roll_m = (
                            getattr(data, "angulo_rotacion", 0)
                            + extra_roll_by_view[i]
                            + adjacent_xy_roll[i]
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] "
                                f"vm={seg_view_modes[i]} | yaw={rot_xy:.2f}° | "
                                f"pitch={rot_pitch:.2f}° | roll_total={total_roll_m:.1f}°"
                            )

                        # 1) Roll total alrededor del eje X local (antes del yaw)
                        if abs(total_roll_m) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_m),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # 2) Yaw alrededor de Z
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # 3) Pitch
                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # Ángulos para este segmento
                        rot_xy = effective_yaw[i]  # YAW: dirección de viaje
                        long_xy_seg = getattr(data, "longitud_xy", 0.0)
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))

                        # Roll total = angulo_rotacion + 90°(si XZ/YZ) + ángulo_XY_adyacente
                        total_roll_t = (
                            getattr(data, "angulo_rotacion", 0)
                            + extra_roll_by_view[i]
                            + adjacent_xy_roll[i]
                        )

                        if debug:
                            print(
                                f"  {item_name} [vm={seg_view_modes[i]}] "
                                f"ang_xy_propio={seg_angulo_xy[i]:.2f}° | "
                                f"yaw={rot_xy:.2f}° | pitch={rot_pitch:.2f}° | "
                                f"roll_total={total_roll_t:.1f}° "
                                f"(ar={getattr(data,'angulo_rotacion',0):.0f}° "
                                f"+view={extra_roll_by_view[i]:.0f}° "
                                f"+adj={adjacent_xy_roll[i]:.0f}°)"
                            )

                        # 1) Roll total alrededor del eje X local (BREP aún a lo largo de X)
                        if abs(total_roll_t) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_t),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # 2) Yaw alrededor de Z (dirección horizontal de viaje)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # 3) Pitch: inclinación en el plano correcto según yaw
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Centro ajustado por extensiones
                        desplazamiento_neto = (
                            longitud_original / 2.0
                            + (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    # -- funciona bastante bien --
    def center_and_connect_models_v8(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v8.

        REGLA DE ROTACIÓN — effective_rot_xy por agrupación de view_mode:
        ─────────────────────────────────────────────────────────────────
        1. Se detectan grupos de segmentos consecutivos con el mismo view_mode.
        2. Los grupos XY usan su propio angulo_xy (con la herencia delta_z
           ya existente para segmentos inclinados dentro del grupo XY).
        3. Los grupos XZ/YZ usan el angulo_xy del PRIMER segmento XY
           en la transición adyacente:
             · XZ/YZ → XY : primer segmento del grupo XY siguiente
             · XY   → XZ/YZ : último segmento del grupo XY anterior
           Fallback: si no hay XY en ninguno de los dos lados → 0°.

        Ejemplo con los segmentos del documento:
          line_1 (XZ) ┐
          line_2 (XZ) ├─ grupo XZ → ref = line_4.angulo_xy = 45°
          line_3 (XZ) ┘
          line_4 (XY) ┐
          line_5 (XY) ├─ grupo XY → usan su propio angulo_xy
          line_6 (XY) ┘

        EXTRA ROLL — compensación de view_mode:
        ────────────────────────────────────────
        El BREP está modelado para viajar en el plano XY.
        Los segmentos XZ/YZ reciben +90° de roll alrededor del eje de
        viaje (antes del yaw) para corregir la sección transversal.
        Funciona en ambas direcciones: XY→XZ/YZ y XZ/YZ→XY.
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_Z = 0.1  # mm – por debajo se considera "sin componente Z" (XY puro)

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # =========================================================================
        # PRE-PROCESADO PASO 1: recopilar view_mode y angulo_xy por segmento
        # =========================================================================
        seg_view_modes = []
        seg_angulo_xy = []
        for item in data_list:
            seg = item.get("segment")
            if seg:
                seg_view_modes.append(getattr(seg, "view_mode", "XY"))
                seg_angulo_xy.append(getattr(seg.data, "angulo_xy", 0.0))
            else:
                seg_view_modes.append("XY")
                seg_angulo_xy.append(0.0)

        # =========================================================================
        # PRE-PROCESADO PASO 2: detectar grupos por view_mode
        #
        # Genera lista de grupos: [(view_mode, [indices]), ...]
        # =========================================================================
        grupos = []
        if data_list:
            vm_actual = seg_view_modes[0]
            idx_inicio = 0
            for idx in range(1, len(data_list)):
                if seg_view_modes[idx] != vm_actual:
                    grupos.append((vm_actual, list(range(idx_inicio, idx))))
                    vm_actual = seg_view_modes[idx]
                    idx_inicio = idx
            grupos.append((vm_actual, list(range(idx_inicio, len(data_list)))))

        if debug:
            print(f"\n--- Grupos detectados por view_mode ---")
            for g_vm, g_idx in grupos:
                names = [
                    getattr(data_list[k].get("segment"), "name", f"Seg_{k}")
                    for k in g_idx
                    if data_list[k].get("segment")
                ]
                print(f"  {g_vm}: indices={g_idx} → {names}")
            print()

        # =========================================================================
        # PRE-PROCESADO PASO 3: effective_rot_xy
        #
        # · Grupos XY  → cada segmento usa su propio angulo_xy.
        #                Los segmentos con delta_z != 0 DENTRO del grupo XY
        #                heredan del último segmento XY puro del mismo grupo.
        # · Grupos XZ/YZ → todos los segmentos del grupo usan el angulo_xy
        #                  del primer segmento XY en la transición adyacente:
        #                  primero busca hacia adelante (grupo XY siguiente),
        #                  si no existe busca hacia atrás (grupo XY anterior).
        # =========================================================================
        effective_rot_xy = [0.0] * len(data_list)

        for g_num, (g_vm, g_idx) in enumerate(grupos):

            if g_vm == "XY":
                # Herencia delta_z dentro del grupo XY
                last_xy_angle = None
                for k in g_idx:
                    seg = data_list[k].get("segment")
                    if not seg:
                        effective_rot_xy[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )
                        continue
                    dz = abs(getattr(seg.data, "delta_z", 0.0))
                    if dz < UMBRAL_Z:
                        last_xy_angle = getattr(seg.data, "angulo_xy", 0.0)
                        effective_rot_xy[k] = last_xy_angle
                    else:
                        # segmento inclinado dentro del grupo XY → hereda
                        effective_rot_xy[k] = (
                            last_xy_angle if last_xy_angle is not None else 0.0
                        )

            else:
                # Grupo XZ o YZ → buscar referencia en grupos XY adyacentes
                ref_angle = None

                # Buscar hacia adelante: primer grupo XY posterior
                for g2_vm, g2_idx in grupos[g_num + 1 :]:
                    if g2_vm == "XY" and g2_idx:
                        first_xy_idx = g2_idx[0]
                        ref_angle = seg_angulo_xy[first_xy_idx]
                        if debug:
                            ref_name = getattr(
                                data_list[first_xy_idx].get("segment"),
                                "name",
                                f"Seg_{first_xy_idx}",
                            )
                            print(
                                f"  Grupo {g_vm} {g_idx}: ref FORWARD → "
                                f"{ref_name} angulo_xy={ref_angle:.2f}°"
                            )
                        break

                # Si no hay XY adelante, buscar hacia atrás
                if ref_angle is None:
                    for g2_vm, g2_idx in reversed(grupos[:g_num]):
                        if g2_vm == "XY" and g2_idx:
                            last_xy_idx = g2_idx[-1]
                            ref_angle = seg_angulo_xy[last_xy_idx]
                            if debug:
                                ref_name = getattr(
                                    data_list[last_xy_idx].get("segment"),
                                    "name",
                                    f"Seg_{last_xy_idx}",
                                )
                                print(
                                    f"  Grupo {g_vm} {g_idx}: ref BACKWARD → "
                                    f"{ref_name} angulo_xy={ref_angle:.2f}°"
                                )
                            break

                if ref_angle is None:
                    ref_angle = 0.0
                    if debug:
                        print(f"  Grupo {g_vm} {g_idx}: sin ref XY → fallback 0°")

                for k in g_idx:
                    effective_rot_xy[k] = ref_angle

        if debug:
            print(f"\n--- effective_rot_xy (v8: agrupación por view_mode) ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                tipo = item.get("type", "")
                vm = seg_view_modes[idx]
                print(
                    f"  [{idx}] {name} ({tipo or 'tubo'}) | view_mode={vm} | "
                    f"angulo_xy_propio={seg_angulo_xy[idx]:.2f}° → "
                    f"effective={effective_rot_xy[idx]:.2f}°"
                )
            print()
        # =========================================================================

        # =========================================================================
        # PRE-PROCESADO PASO 4: extra_roll_by_view
        #
        # El BREP está modelado para el plano XY. Los segmentos XZ/YZ necesitan
        # +90° de roll alrededor del eje de viaje para corregir la sección.
        # =========================================================================
        extra_roll_by_view = [
            90.0 if seg_view_modes[idx] in ("XZ", "YZ") else 0.0
            for idx in range(len(data_list))
        ]

        if debug:
            print(f"--- extra_roll_by_view (XZ/YZ → +90°, XY → 0°) ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                if seg:
                    name = getattr(seg, "name", f"Seg_{idx}")
                    print(
                        f"  [{idx}] {name} | view_mode={seg_view_modes[idx]} "
                        f"→ extra_roll={extra_roll_by_view[idx]:.0f}°"
                    )
            print()
        # =========================================================================
        OVERLAP_SEGURIDAD = 0  # 2mm de solape extra para asegurar contacto

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

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
                        if prev_item.get("type") != "manguito":
                            vec_prev = prev_item["segment"].data.vector_normalizado
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el inicio del segundo segmento del codo, recortamos
                                    extension_inicio = -15.4
                                    if debug:
                                        print(
                                            f"  {item_name} - Inicio: Detectado 135°, aplicando recorte -22.5"
                                        )
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (
                                        CONDUCTO_WIDTH / 2.0
                                    ) * math.tan(a_rad / 2.0)
                                    extension_inicio = (
                                        extension_teorica + OVERLAP_SEGURIDAD
                                    )

                    # 2. Extensión al FINAL
                    extension_final = 0.0
                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        if next_item.get("type") != "manguito":
                            vec_next = next_item["segment"].data.vector_normalizado
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el final del primer segmento del codo, alargamos
                                    extension_final = 15.4
                                    if debug:
                                        print(
                                            f"  {item_name} - Final: Detectado 135°, aplicando alargue 22.5"
                                        )
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (
                                        CONDUCTO_WIDTH / 2.0
                                    ) * math.tan(a_rad / 2.0)
                                    extension_final = (
                                        extension_teorica + OVERLAP_SEGURIDAD
                                    )

                    # 3. Aplicación de longitud
                    longitud_original = getattr(data, "longitud_3d", 0.0)
                    longitud_total = (
                        longitud_original + extension_inicio + extension_final
                    )

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | "
                        f"ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    # Punto medio geométrico
                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0
                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] "
                                f"view_mode={seg_view_modes[i]} | "
                                f"rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}° | "
                                f"extra_roll={extra_roll_by_view[i]:.0f}° | "
                                f"angulo_rotacion={getattr(data, 'angulo_rotacion', 0):.1f}°"
                            )

                        # Roll: angulo_rotacion del dato + compensación por view_mode
                        total_roll_m = (
                            getattr(data, "angulo_rotacion", 0) + extra_roll_by_view[i]
                        )
                        if abs(total_roll_m) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_m),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — ángulo efectivo de grupo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # ─── ROT_XY efectivo (por grupo de view_mode) ─────────
                        rot_xy = effective_rot_xy[i]
                        long_xy_seg = getattr(data, "longitud_xy", 0.0)
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))

                        if debug:
                            print(
                                f"  {item_name} [view_mode={seg_view_modes[i]}] "
                                f"angulo_xy_propio={seg_angulo_xy[i]:.2f}° | "
                                f"effective_rot_xy={rot_xy:.2f}° | "
                                f"rot_pitch={rot_pitch:.2f}° | "
                                f"extra_roll={extra_roll_by_view[i]:.0f}°"
                            )

                        # Roll: angulo_rotacion del dato + compensación por view_mode
                        total_roll_t = (
                            getattr(data, "angulo_rotacion", 0) + extra_roll_by_view[i]
                        )
                        if abs(total_roll_t) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_t),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — ángulo efectivo de grupo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch — eje perpendicular orientado por rot_xy efectivo
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Centro ajustado por extensiones
                        desplazamiento_neto = (
                            longitud_original / 2.0
                            + (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v7(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v7.

        REGLA DE ROTACIÓN (definitiva):
        ────────────────────────────────
        La rotación XY de la sección transversal del conducto se determina por
        el ÚLTIMO segmento PURAMENTE horizontal (delta_z ≈ 0) anterior al segmento
        actual.  Cualquier segmento que tenga componente Z (vertical puro, inclinado
        XZ o YZ) HEREDA ese ángulo, sin importar su propio angulo_xy.

        Esto cubre todos los casos:
        XY(0°) → XY(-45°) → Z↓ → XZ(0°) → XY(0°)
                                ↑           ↑
                            hereda -45°   hereda -45°  ← CORREGIDO en v6

        Clasificación de cada segmento:
        "XY puro"   : abs(delta_z) < UMBRAL_Z   → usa su propio angulo_xy
        "con Z"     : abs(delta_z) >= UMBRAL_Z   → hereda del XY puro anterior
                        (incluye vertical puro Y segmentos inclinados XZ/YZ)

        Pasadas del pre-procesado:
        Forward  → propaga el último XY puro hacia adelante
        Backward → cubre verticales que aparecen antes del primer XY puro

        NUEVO en v7 — extra_roll_by_view:
        ────────────────────────────────
        El BREP de cada segmento está modelado para viajar en el plano XY.
        Cuando view_mode es 'XZ' o 'YZ', la sección transversal queda girada
        90° respecto al plano de trabajo real → se compensa con +90° de roll
        alrededor del eje de viaje (antes del yaw).
        Funciona en ambas direcciones: XY→XZ/YZ y XZ/YZ→XY.
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_Z = 0.1  # mm – por debajo se considera "sin componente Z" (XY puro)

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # =========================================================================
        # PRE-PROCESADO: effective_rot_xy
        #
        # Criterio: un segmento "tiene XY propio" solo si abs(delta_z) < UMBRAL_Z.
        # Cualquier segmento con componente Z hereda del último XY puro.
        # =========================================================================
        raw_rot_xy = []
        for item in data_list:
            seg = item.get("segment")
            if not seg:
                raw_rot_xy.append(None)
                continue
            d = seg.data
            delta_z = abs(getattr(d, "delta_z", 0.0))

            if delta_z < UMBRAL_Z:
                # XY puro → contribuye con su propio ángulo
                raw_rot_xy.append(getattr(d, "angulo_xy", 0.0))
            else:
                # Tiene Z (vertical o inclinado) → hereda
                raw_rot_xy.append(None)

        # Forward pass: propaga el último XY puro conocido hacia adelante
        last_known = None
        for idx in range(len(raw_rot_xy)):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known

        # Backward pass: cubre None al inicio (segmentos Z antes de cualquier XY)
        last_known = None
        for idx in range(len(raw_rot_xy) - 1, -1, -1):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known

        # Fallback final
        effective_rot_xy = [v if v is not None else 0.0 for v in raw_rot_xy]

        if debug:
            print(f"\n--- effective_rot_xy (v7: hereda si delta_z != 0) ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                tipo = item.get("type", "")
                if seg:
                    d = seg.data
                    dz = abs(getattr(d, "delta_z", 0.0))
                    orig = getattr(d, "angulo_xy", "?")
                    long_xy = getattr(d, "longitud_xy", 0.0)
                    fuente = (
                        "XY-propio" if dz < UMBRAL_Z else f"hereda (delta_z={dz:.1f})"
                    )
                    print(
                        f"  [{idx}] {name} ({tipo or 'tubo'}) | {fuente} | "
                        f"angulo_xy={orig}° long_xy={long_xy:.1f} → effective={effective_rot_xy[idx]:.2f}°"
                    )
            print()
        # =========================================================================

        # =========================================================================
        # PRE-PROCESADO: extra_roll_by_view
        #
        # El BREP de cada segmento está modelado para viajar en el plano XY.
        # Cuando el view_mode es 'XZ' o 'YZ', la sección transversal queda
        # girada 90° respecto al plano de trabajo real → compensamos con +90° de
        # roll alrededor del eje de viaje (aplicado antes del yaw).
        #
        # Funciona en ambas direcciones:
        #   XY → XZ/YZ  y  XZ/YZ → XY
        # =========================================================================
        extra_roll_by_view = []
        for idx, item_vm in enumerate(data_list):
            seg_vm = item_vm.get("segment")
            if seg_vm:
                vm = getattr(seg_vm, "view_mode", "XY")
                extra_roll_by_view.append(90.0 if vm in ("XZ", "YZ") else 0.0)
            else:
                extra_roll_by_view.append(0.0)

        if debug:
            print(f"--- extra_roll_by_view (XZ/YZ → +90°, XY → 0°) ---")
            for idx, item_vm in enumerate(data_list):
                seg_vm = item_vm.get("segment")
                if seg_vm:
                    vm = getattr(seg_vm, "view_mode", "XY")
                    name_vm = getattr(seg_vm, "name", f"Seg_{idx}")
                    print(
                        f"  [{idx}] {name_vm} | view_mode={vm} → extra_roll={extra_roll_by_view[idx]:.0f}°"
                    )
            print()
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

                # ── Extensiones en uniones (solo tubos dinámicos) ────────────────
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175
                    MAX_ANGLE_RAD = math.pi - 0.0175

                    if i > 0:
                        prev_item = data_list[i - 1]
                        prev_tipo_s = prev_item.get("type", "")
                        prev_tipo_s = (
                            prev_tipo_s
                            if isinstance(prev_tipo_s, str)
                            else (prev_tipo_s[0] if prev_tipo_s else "")
                        )
                        if prev_tipo_s == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito anterior → ext_inicio=0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_inicio: {math.degrees(a_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )

                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        next_tipo_s = next_item.get("type", "")
                        next_tipo_s = (
                            next_tipo_s
                            if isinstance(next_tipo_s, str)
                            else (next_tipo_s[0] if next_tipo_s else "")
                        )
                        if next_tipo_s == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito siguiente → ext_final=0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_final: {math.degrees(a_rad):.1f}° → {extension_final:.2f}mm"
                                    )

                longitud_original = getattr(data, "longitud_3d", 0.0)
                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | "
                        f"ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    # Punto medio geométrico
                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0
                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] rot_xy={rot_xy:.2f}° | "
                                f"rot_pitch={rot_pitch:.2f}° | "
                                f"extra_roll={extra_roll_by_view[i]:.0f}° | "
                                f"angulo_rotacion={getattr(data, 'angulo_rotacion', 0):.1f}°"
                            )

                        # Roll: angulo_rotacion del dato + compensación por view_mode
                        total_roll_m = (
                            getattr(data, "angulo_rotacion", 0) + extra_roll_by_view[i]
                        )
                        if abs(total_roll_m) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_m),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — ángulo efectivo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # ─── ROT_XY efectivo ──────────────────────────────────
                        rot_xy = effective_rot_xy[i]

                        # Pitch: ángulo de inclinación con respecto al plano XY
                        long_xy_seg = getattr(data, "longitud_xy", 0.0)
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))

                        if debug:
                            dz_val = abs(getattr(data, "delta_z", 0.0))
                            fuente = (
                                "XY-propio"
                                if dz_val < UMBRAL_Z
                                else f"hereda(dz={dz_val:.1f})"
                            )
                            vm_name = getattr(segment, "view_mode", "XY")
                            print(
                                f"  {item_name} [{fuente}] view_mode={vm_name} "
                                f"rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}° | "
                                f"long_xy={long_xy_seg:.2f} | "
                                f"extra_roll={extra_roll_by_view[i]:.0f}°"
                            )

                        # Roll: angulo_rotacion del dato + compensación por view_mode
                        total_roll_t = (
                            getattr(data, "angulo_rotacion", 0) + extra_roll_by_view[i]
                        )
                        if abs(total_roll_t) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(total_roll_t),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — ángulo efectivo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch — el eje usa rot_xy efectivo para garantizar que la
                        # inclinación ocurra en el plano XZ o YZ correcto
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Centro ajustado por extensiones
                        desplazamiento_neto = (
                            longitud_original / 2.0
                            + (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v6(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v6.

        REGLA DE ROTACIÓN (definitiva):
        ────────────────────────────────
        La rotación XY de la sección transversal del conducto se determina por
        el ÚLTIMO segmento PURAMENTE horizontal (delta_z ≈ 0) anterior al segmento
        actual.  Cualquier segmento que tenga componente Z (vertical puro, inclinado
        XZ o YZ) HEREDA ese ángulo, sin importar su propio angulo_xy.

        Esto cubre todos los casos:
        XY(0°) → XY(-45°) → Z↓ → XZ(0°) → XY(0°)
                                ↑           ↑
                            hereda -45°   hereda -45°  ← CORREGIDO en v6

        Clasificación de cada segmento:
        "XY puro"   : abs(delta_z) < UMBRAL_Z   → usa su propio angulo_xy
        "con Z"     : abs(delta_z) >= UMBRAL_Z   → hereda del XY puro anterior
                        (incluye vertical puro Y segmentos inclinados XZ/YZ)

        Pasadas del pre-procesado:
        Forward  → propaga el último XY puro hacia adelante
        Backward → cubre verticales que aparecen antes del primer XY puro
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_Z = 0.1  # mm – por debajo se considera "sin componente Z" (XY puro)

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # =========================================================================
        # PRE-PROCESADO: effective_rot_xy
        #
        # Criterio: un segmento "tiene XY propio" solo si abs(delta_z) < UMBRAL_Z.
        # Cualquier segmento con componente Z hereda del último XY puro.
        # =========================================================================
        raw_rot_xy = []
        for item in data_list:
            seg = item.get("segment")
            if not seg:
                raw_rot_xy.append(None)
                continue
            d = seg.data
            delta_z = abs(getattr(d, "delta_z", 0.0))

            if delta_z < UMBRAL_Z:
                # XY puro → contribuye con su propio ángulo
                raw_rot_xy.append(getattr(d, "angulo_xy", 0.0))
            else:
                # Tiene Z (vertical o inclinado) → hereda
                raw_rot_xy.append(None)

        # Forward pass: propaga el último XY puro conocido hacia adelante
        last_known = None
        for idx in range(len(raw_rot_xy)):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known

        # Backward pass: cubre None al inicio (segmentos Z antes de cualquier XY)
        last_known = None
        for idx in range(len(raw_rot_xy) - 1, -1, -1):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known

        # Fallback final
        effective_rot_xy = [v if v is not None else 0.0 for v in raw_rot_xy]

        if debug:
            print(f"\n--- effective_rot_xy (v6: hereda si delta_z != 0) ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                tipo = item.get("type", "")
                if seg:
                    d = seg.data
                    dz = abs(getattr(d, "delta_z", 0.0))
                    orig = getattr(d, "angulo_xy", "?")
                    long_xy = getattr(d, "longitud_xy", 0.0)
                    fuente = (
                        "XY-propio" if dz < UMBRAL_Z else f"hereda (delta_z={dz:.1f})"
                    )
                    print(
                        f"  [{idx}] {name} ({tipo or 'tubo'}) | {fuente} | "
                        f"angulo_xy={orig}° long_xy={long_xy:.1f} → effective={effective_rot_xy[idx]:.2f}°"
                    )
            print()
        # =========================================================================
        # PRE-PROCESADO: extra_roll_by_view
        #
        # El BREP de cada segmento está modelado para viajar en el plano XY.
        # Cuando el view_mode es 'XZ' o 'YZ', la sección transversal queda
        # girada 90° respecto al plano de trabajo real → compensamos con +90° de
        # roll alrededor del eje de viaje (aplicado antes del yaw).
        #
        # Funciona en ambas direcciones:
        #   XY → XZ/YZ  y  XZ/YZ → XY
        # =========================================================================
        extra_roll_by_view = []
        for idx, item_vm in enumerate(data_list):
            seg_vm = item_vm.get("segment")
            if seg_vm:
                vm = getattr(seg_vm, "view_mode", "XY")
                extra_roll_by_view.append(90.0 if vm in ("XZ", "YZ") else 0.0)
            else:
                extra_roll_by_view.append(0.0)

        if debug:
            print(f"--- extra_roll_by_view (XZ/YZ → +90°, XY → 0°) ---")
            for idx, item_vm in enumerate(data_list):
                seg_vm = item_vm.get("segment")
                if seg_vm:
                    vm = getattr(seg_vm, "view_mode", "XY")
                    name_vm = getattr(seg_vm, "name", f"Seg_{idx}")
                    print(
                        f"  [{idx}] {name_vm} | view_mode={vm} → extra_roll={extra_roll_by_view[idx]:.0f}°"
                    )
            print()
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

                # ── Extensiones en uniones (solo tubos dinámicos) ────────────────
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175
                    MAX_ANGLE_RAD = math.pi - 0.0175

                    if i > 0:
                        prev_item = data_list[i - 1]
                        prev_tipo_s = prev_item.get("type", "")
                        prev_tipo_s = (
                            prev_tipo_s
                            if isinstance(prev_tipo_s, str)
                            else (prev_tipo_s[0] if prev_tipo_s else "")
                        )
                        if prev_tipo_s == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito anterior → ext_inicio=0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_inicio: {math.degrees(a_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )

                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        next_tipo_s = next_item.get("type", "")
                        next_tipo_s = (
                            next_tipo_s
                            if isinstance(next_tipo_s, str)
                            else (next_tipo_s[0] if next_tipo_s else "")
                        )
                        if next_tipo_s == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito siguiente → ext_final=0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_final: {math.degrees(a_rad):.1f}° → {extension_final:.2f}mm"
                                    )

                longitud_original = getattr(data, "longitud_3d", 0.0)
                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | "
                        f"ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    # Punto medio geométrico
                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0
                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}°"
                            )

                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # ─── ROT_XY efectivo ──────────────────────────────────
                        # Si delta_z ≈ 0 → usa el propio angulo_xy (ya está en effective)
                        # Si delta_z != 0 → hereda del último XY puro (ya está en effective)
                        rot_xy = effective_rot_xy[i]

                        # Pitch: ángulo de inclinación con respecto al plano XY
                        # atan2(delta_z, longitud_xy):
                        #   XY puro   → pitch = 0°
                        #   Z puro    → pitch = ±90°
                        #   Inclinado → pitch = ±45° (o el ángulo real)
                        long_xy_seg = getattr(data, "longitud_xy", 0.0)
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))

                        if debug:
                            dz_val = abs(getattr(data, "delta_z", 0.0))
                            fuente = (
                                "XY-propio"
                                if dz_val < UMBRAL_Z
                                else f"hereda(dz={dz_val:.1f})"
                            )
                            print(
                                f"  {item_name} [{fuente}] "
                                f"rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}° | "
                                f"long_xy={long_xy_seg:.2f}"
                            )

                        # Roll
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — ángulo efectivo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch — el eje usa rot_xy efectivo para garantizar que la
                        # inclinación ocurra en el plano XZ o YZ correcto según la
                        # dirección horizontal del conducto
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0,
                                0,
                                0,
                                math.sin(rad_xy),  #  componente X del eje perpendicular
                                -math.cos(
                                    rad_xy
                                ),  # -componente Y del eje perpendicular
                                0,
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Centro ajustado por extensiones
                        desplazamiento_neto = (
                            longitud_original / 2.0
                            + (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v5(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
        """
        Versión v5.

        REGLA DE ROTACIÓN (simplificada y correcta):
        ─────────────────────────────────────────────
        • Segmento CON componente XY (longitud_xy >= UMBRAL_XY):
            → usa su propio data.angulo_xy  (nunca se hereda ni se sobreescribe)

        • Segmento SIN componente XY  (longitud_xy < UMBRAL_XY = vertical puro):
            → hereda el effective_rot_xy del segmento horizontal más cercano.
            Primero busca hacia ATRÁS; si no hay, busca hacia ADELANTE.
            El eje del pitch también usará ese ángulo heredado para que la
            inclinación se aplique en el plano XZ o YZ correcto.

        Esto cubre:
        XY → Z (descenso vertical)          ✓  hereda ángulo del XY anterior
        Z  → XY (subida / retorno plano)    ✓  el XY siguiente da su propio ángulo
        XY → XZ/YZ (inclinado con delta_z)  ✓  el segmento inclinado tiene XY propio
        XZ/YZ → XY                          ✓  ídem
        """
        elementos_transformados = []
        last_real_end_point = None
        last_segment = None

        def get_dot_product(v1, v2):
            if not v1 or not v2:
                return 1.0
            return v1.X * v2.X + v1.Y * v2.Y + v1.Z * v2.Z

        def same_direction(seg1, seg2, tol_deg=1):
            if not seg1 or not seg2:
                return False
            diff = abs((seg1.data.angulo_xy - seg2.data.angulo_xy + 180) % 360 - 180)
            return diff < tol_deg

        CONDUCTO_WIDTH = conducto_width
        TIPOS_ACCESORIOS = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]
        UMBRAL_XY = 0.1  # mm – por debajo se considera "sin componente XY"

        if debug:
            print(f"\n{'#'*70}")
            print(f"# PROCESANDO DATA LIST: {len(data_list)}")
            print(f"{'#'*70}")

        # # =========================================================================
        # # PRE-PROCESADO: effective_rot_xy
        # #
        # # Paso 1 – marcar cada slot:
        # #   • tiene XY propio  → guardar data.angulo_xy
        # #   • sin XY (vertical)→ None  (se rellena en paso 2)
        # #
        # # Paso 2 – relleno bidireccional:
        # #   Forward:  propaga el último angulo_xy conocido hacia los None
        # #   Backward: propaga el primer angulo_xy conocido hacia los None iniciales
        # # =========================================================================
        # raw_rot_xy = []
        # for item in data_list:
        #     seg = item.get("segment")
        #     if not seg:
        #         raw_rot_xy.append(None)
        #         continue
        #     d       = seg.data
        #     long_xy = getattr(d, 'longitud_xy', 0.0)
        #     # Solo tiene orientación XY propia si realmente se mueve en XY
        #     raw_rot_xy.append(d.angulo_xy if long_xy >= UMBRAL_XY else None)
        # =========================================================================
        # PRE-PROCESADO: effective_rot_xy (CORREGIDO)
        # =========================================================================
        raw_rot_xy = []
        for item in data_list:
            seg = item.get("segment")
            if not seg:
                raw_rot_xy.append(None)
                continue

            d = seg.data
            long_xy = getattr(d, "longitud_xy", 0.0)
            delta_z = abs(getattr(d, "delta_z", 0.0))

            # REGLA DE ORO: Solo los segmentos "planos" definen la dirección XY.
            # Un segmento inclinado (con delta_z significativo) debe heredar
            # la rotación de los tramos horizontales para no salirse del plano.
            # Usamos un umbral para decidir si el tramo es lo suficientemente horizontal.
            es_horizontal = delta_z < (
                long_xy * 0.5
            )  # Ejemplo: pendiente menor a 30° aprox.
            # O simplemente: es_horizontal = delta_z < 1.0 (si el desnivel es casi cero)

            if long_xy >= UMBRAL_XY and es_horizontal:
                raw_rot_xy.append(d.angulo_xy)
            else:
                # Si es vertical PURO o inclinado con mucha pendiente -> Hereda
                raw_rot_xy.append(None)

        # Forward pass: hereda del anterior
        last_known = None
        for idx in range(len(raw_rot_xy)):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known  # hereda

        # Backward pass: rellena None que quedaron al inicio (verticales sin XY previo)
        last_known = None
        for idx in range(len(raw_rot_xy) - 1, -1, -1):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            elif last_known is not None:
                raw_rot_xy[idx] = last_known

        # None residuales → 0.0
        effective_rot_xy = [v if v is not None else 0.0 for v in raw_rot_xy]

        if debug:
            print(f"\n--- effective_rot_xy ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                tipo = item.get("type", "")
                if seg:
                    d = seg.data
                    long_xy = getattr(d, "longitud_xy", 0.0)
                    orig = getattr(d, "angulo_xy", "?")
                    tiene = "XY-propio" if long_xy >= UMBRAL_XY else "vertical→hereda"
                    print(
                        f"  [{idx}] {name} ({tipo or 'tubo'}) | {tiene} | angulo_xy_orig={orig}° → effective={effective_rot_xy[idx]:.2f}°"
                    )
            print()
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # Vector de dirección actual
                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
                    )
                    vec_curr.Normalize()

                # Continuidad de inicio para segmentos en la misma dirección
                if (
                    last_real_end_point is not None
                    and last_segment is not None
                    and same_direction(last_segment, segment)
                ):
                    start_point = last_real_end_point

                extension_inicio = 0.0
                extension_final = 0.0

                # ── Cálculo de extensiones (solo tubos dinámicos) ────────────────
                if is_dinamic:
                    MIN_ANGLE_RAD = 0.0175  # ~1°
                    MAX_ANGLE_RAD = math.pi - 0.0175  # ~179°

                    # Vecino anterior
                    if i > 0:
                        prev_item = data_list[i - 1]
                        prev_tipo = prev_item.get("type", "")
                        prev_tipo_s = (
                            prev_tipo
                            if isinstance(prev_tipo, str)
                            else (prev_tipo[0] if prev_tipo else "")
                        )
                        if prev_tipo_s == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito anterior → ext_inicio=0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_inicio: {math.degrees(a_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )
                            else:
                                extension_inicio = 0.0

                    # Vecino siguiente
                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        next_tipo = next_item.get("type", "")
                        next_tipo_s = (
                            next_tipo
                            if isinstance(next_tipo, str)
                            else (next_tipo[0] if next_tipo else "")
                        )
                        if next_tipo_s == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} – manguito siguiente → ext_final=0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < a_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    a_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} – ext_final: {math.degrees(a_rad):.1f}° → {extension_final:.2f}mm"
                                    )
                            else:
                                extension_final = 0.0

                longitud_original = getattr(data, "longitud_3d", 0.0)
                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(
                        f"  long_orig={longitud_original:.2f} | ext_i={extension_inicio:.2f} | ext_f={extension_final:.2f} | total={longitud_total:.2f}"
                    )

                # ── BREPs ────────────────────────────────────────────────────────
                list_elem_3d = item.get("element3d", [])
                lista_elem_3d_modified = []
                if is_dinamic:
                    for elem in list_elem_3d:
                        lista_elem_3d_modified.append(
                            self.modificar_dimensiones_brep(elem, longitud_total)
                        )
                else:
                    lista_elem_3d_modified = list_elem_3d

                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, verts = brep.GetVertices()

                    # Punto medio geométrico del segmento (para manguitos / fallback)
                    pmx = (start_point.X + data.end.X) / 2.0
                    pmy = (start_point.Y + data.end.Y) / 2.0
                    pmz = (start_point.Z + data.end.Z) / 2.0

                    if verts:
                        pmx = sum(v.X for v in verts) / len(verts)
                        pmy = sum(v.Y for v in verts) / len(verts)
                        pmz = sum(v.Z for v in verts) / len(verts)

                    nuevo_brep = None

                    # ──────────────────────────────────────────────────────────
                    # CASO 1 – MANGUITO
                    # ──────────────────────────────────────────────────────────
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vp = brep.GetVertices()
                            if vp:
                                cx = sum(v.X for v in vp) / len(vp)
                                cy = sum(v.Y for v in vp) / len(vp)
                                cz = sum(v.Z for v in vp) / len(vp)
                            else:
                                cx, cy, cz = pmx, pmy, pmz
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (cx, cy, cz)
                        else:
                            cx, cy, cz = self._temp_manguito_center.get(i, (0, 0, 0))

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -cx + (longitud_original / 2.0), -cy, -cz
                            ),
                        )

                        # *** Usa effective_rot_xy (heredado si es vertical) ***
                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            print(
                                f"  {item_name} [manguito] rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}°"
                            )

                        # Roll
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch — eje perpendicular al rot_xy efectivo
                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                (start_point.X + data.end.X) / 2.0,
                                (start_point.Y + data.end.Y) / 2.0,
                                (start_point.Z + data.end.Z) / 2.0,
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 2 – DIFUSOR
                    # ──────────────────────────────────────────────────────────
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2
                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                ni = data_list[j]
                                nt_s = ni.get("type", "")
                                nt_s = (
                                    nt_s
                                    if isinstance(nt_s, str)
                                    else (nt_s[0] if nt_s else "")
                                )
                                if nt_s not in TIPOS_ACCESORIOS:
                                    punto_inicio_real = getattr(
                                        ni["segment"].data, "start", start_point
                                    )
                                    break
                            _, vd = brep.GetVertices()
                            if vd:
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -sum(v.Z for v in vd) / len(vd),
                                    ),
                                )
                            if ang_int != 0:
                                mr = AllplanGeo.Matrix3D()
                                mr.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, mr)
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                        elif point_role == "final":
                            punto_final_real = getattr(
                                data,
                                "end",
                                AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                ),
                            )
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    ni = data_list[j]
                                    nt_s = ni.get("type", "")
                                    nt_s = (
                                        nt_s
                                        if isinstance(nt_s, str)
                                        else (nt_s[0] if nt_s else "")
                                    )
                                    if nt_s not in TIPOS_ACCESORIOS:
                                        punto_final_real = getattr(
                                            ni["segment"].data, "end", punto_final_real
                                        )
                                        break
                            cdz = 0
                            _, vd = brep.GetVertices()
                            if vd:
                                cdz = sum(v.Z for v in vd) / len(vd)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -sum(v.X for v in vd) / len(vd),
                                        -sum(v.Y for v in vd) / len(vd),
                                        -cdz,
                                    ),
                                )
                            rot_diff = (
                                180
                                if ang_int == 0
                                else (
                                    0
                                    if ang_int in [180, 179, 178]
                                    else (
                                        -data.angulo_xy
                                        if ang_int in [-90, 89, 90, -89]
                                        else 0
                                    )
                                )
                            )
                            mr = AllplanGeo.Matrix3D()
                            mr.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, mr)
                            padding = 60
                            ltc = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )
                            if ang_int in [0, 180, 179, 178]:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - cdz + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep, AllplanGeo.Vector3D(pmx, pmy, pmz)
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # ──────────────────────────────────────────────────────────
                    # CASO 3 – TUBOS DINÁMICOS (recto, inclinado, vertical)
                    # ──────────────────────────────────────────────────────────
                    else:
                        nx = sum(v.X for v in verts) / len(verts) if verts else 0
                        ny = sum(v.Y for v in verts) / len(verts) if verts else 0
                        nz = sum(v.Z for v in verts) / len(verts) if verts else 0
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        long_xy_seg = getattr(data, "longitud_xy", 0.0)

                        # ─── ROT_XY ───────────────────────────────────────────
                        # Segmento CON componente XY → usa su propio angulo_xy
                        # Segmento SIN componente XY → hereda del horizontal más cercano
                        # effective_rot_xy[i] ya tiene la lógica correcta del pre-procesado
                        rot_xy = effective_rot_xy[i]

                        # ─── ROT_PITCH ────────────────────────────────────────
                        # Para segmentos con XY: inclinación relativa al plano XY
                        # Para verticales puros: atan2(dz, 0) = ±90°
                        rot_pitch = math.degrees(math.atan2(data.delta_z, long_xy_seg))

                        if debug:
                            tiene_xy = long_xy_seg >= UMBRAL_XY
                            print(
                                f"  {item_name} ({'XY-propio' if tiene_xy else 'hereda'}) "
                                f"rot_xy={rot_xy:.2f}° | rot_pitch={rot_pitch:.2f}° | "
                                f"long_xy={long_xy_seg:.2f}"
                            )

                        # Roll (si el segmento tiene rotación axial definida)
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (planta) — aplica SIEMPRE el ángulo efectivo
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (elevación/descenso) — solo si hay componente Z
                        # El eje de rotación usa rot_xy efectivo, garantizando que
                        # el pitch siempre ocurra en el plano XZ o YZ correcto
                        # (el plano definido por la dirección horizontal del conducto)
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            # Eje perpendicular a la dirección horizontal del conducto
                            # = gira 90° en XY respecto a la dirección de avance
                            axis = AllplanGeo.Line3D(
                                0,
                                0,
                                0,
                                math.sin(rad_xy),  #  sin(rot_xy)
                                -math.cos(rad_xy),  # -cos(rot_xy)
                                0,
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Centro del segmento ajustado por extensiones
                        desplazamiento_neto = (longitud_original / 2.0) + (
                            (extension_final - extension_inicio) / 2.0
                        )
                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as ex:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {ex}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v4(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
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
        UMBRAL_XY = 0.1  # mm — por debajo de esto se considera sin componente XY

        raw_rot_xy = []  # None si el segmento no tiene orientación XY propia
        for item in data_list:
            seg = item.get("segment")
            if not seg:
                raw_rot_xy.append(None)
                continue
            d = seg.data
            long_xy = getattr(d, "longitud_xy", 0.0)
            if long_xy >= UMBRAL_XY:
                raw_rot_xy.append(d.angulo_xy)
            else:
                raw_rot_xy.append(None)  # vertical puro → hereda de vecinos

        # Primer sub-pase: rellena con el vecino anterior conocido
        last_known = None
        for idx in range(len(raw_rot_xy)):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            else:
                raw_rot_xy[idx] = last_known  # puede quedar None si es el primero

        # Segundo sub-pase: rellena con el vecino siguiente (para los que aún son None)
        last_known = None
        for idx in range(len(raw_rot_xy) - 1, -1, -1):
            if raw_rot_xy[idx] is not None:
                last_known = raw_rot_xy[idx]
            else:
                raw_rot_xy[idx] = last_known  # puede quedar None si no hay ninguno

        # Convertir None residuales a 0.0 (caso extremo: lista sin segmentos XY)
        effective_rot_xy = [v if v is not None else 0.0 for v in raw_rot_xy]

        if debug:
            print(f"\n--- effective_rot_xy pre-calculado ---")
            for idx, item in enumerate(data_list):
                seg = item.get("segment")
                name = getattr(seg, "name", f"Seg_{idx}") if seg else f"Item_{idx}"
                orig = (
                    getattr(getattr(seg, "data", None), "angulo_xy", "?")
                    if seg
                    else "?"
                )
                print(
                    f"  [{idx}] {name}: angulo_xy_original={orig} → effective_rot_xy={effective_rot_xy[idx]}"
                )
            print()
        # =========================================================================
        # FIN PRE-PROCESADO
        # =========================================================================

        for i, item in enumerate(data_list):
            try:
                segment = item.get("segment")
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")

                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
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
                        prev_tipo_raw = prev_item.get("type", "")
                        prev_tipo_str = (
                            prev_tipo_raw
                            if isinstance(prev_tipo_raw, str)
                            else (prev_tipo_raw[0] if len(prev_tipo_raw) > 0 else "")
                        )

                        if prev_tipo_str == "manguito":
                            extension_final = 0.0
                            if debug:
                                print(
                                    f"  {item_name} - Manguito anterior detectado, ext inicio = 0"
                                )
                        else:
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(
                                p_data.delta_x, p_data.delta_y, p_data.delta_z
                            )
                            vec_prev.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            angle_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < angle_rad < MAX_ANGLE_RAD:
                                extension_inicio = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    angle_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} - Ext inicio: {math.degrees(angle_rad):.1f}° → {extension_inicio:.2f}mm"
                                    )
                            else:
                                extension_inicio = 0.0
                                if debug:
                                    print(
                                        f"  {item_name} - Ángulo insignificante ({math.degrees(angle_rad):.1f}°), ext inicio = 0"
                                    )

                    # --- VECINO SIGUIENTE ---
                    if i < len(data_list) - 1:
                        next_idx = i + 1
                        next_item = data_list[next_idx]
                        next_tipo_raw = next_item.get("type", "")
                        next_tipo_str = (
                            next_tipo_raw
                            if isinstance(next_tipo_raw, str)
                            else (next_tipo_raw[0] if len(next_tipo_raw) > 0 else "")
                        )

                        if next_tipo_str == "manguito":
                            extension_inicio = 0.0
                            if debug:
                                print(
                                    f"  {item_name} - Manguito siguiente detectado, ext final = 0"
                                )
                        else:
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(
                                n_data.delta_x, n_data.delta_y, n_data.delta_z
                            )
                            vec_next.Normalize()
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            angle_rad = math.acos(dot)
                            if MIN_ANGLE_RAD < angle_rad < MAX_ANGLE_RAD:
                                extension_final = (CONDUCTO_WIDTH / 2.0) * math.tan(
                                    angle_rad / 2.0
                                )
                                if debug:
                                    print(
                                        f"  {item_name} - Ext final: {math.degrees(angle_rad):.1f}° → {extension_final:.2f}mm"
                                    )
                            else:
                                extension_final = 0.0
                                if debug:
                                    print(
                                        f"  {item_name} - Ángulo insignificante ({math.degrees(angle_rad):.1f}°), ext final = 0"
                                    )

                # 4. GEOMETRÍA FINAL DEL SEGMENTO
                longitud_original = getattr(data, "longitud_3d", 0.0)
                longitud_total = longitud_original + extension_inicio + extension_final

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(f"  Long original: {longitud_original}")
                    print(
                        f"  Ext inicio: {extension_inicio}, Ext final: {extension_final}"
                    )
                    print(f"  Long total: {longitud_total}")

                # 5. PROCESAR BREPS
                lista_elem_3d_modified = []
                list_elem_3d = item.get("element3d", [])

                if is_dinamic:
                    for elem_3d in list_elem_3d:
                        brep_ajustado = self.modificar_dimensiones_brep(
                            elem_3d, longitud_total
                        )
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                conn_type_list = []
                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, vertices = brep.GetVertices()

                    punto_medio_x = (start_point.X + data.end.X) / 2.0
                    punto_medio_y = (start_point.Y + data.end.Y) / 2.0
                    punto_medio_z = (start_point.Z + data.end.Z) / 2.0

                    centro_brep_geom = AllplanGeo.Point3D(
                        punto_medio_x, punto_medio_y, punto_medio_z
                    )
                    if vertices:
                        nx = sum(v.X for v in vertices) / len(vertices)
                        ny = sum(v.Y for v in vertices) / len(vertices)
                        nz = sum(v.Z for v in vertices) / len(vertices)
                        centro_brep_geom = AllplanGeo.Point3D(nx, ny, nz)

                    nuevo_brep = None

                    # --- CASO 1: MANGUITOS ---
                    if tipo_str == "manguito":
                        segment_brep = None
                        if e == 0:
                            _, vertices_principal = brep.GetVertices()
                            if vertices_principal:
                                centro_manguito_x = sum(
                                    v.X for v in vertices_principal
                                ) / len(vertices_principal)
                                centro_manguito_y = sum(
                                    v.Y for v in vertices_principal
                                ) / len(vertices_principal)
                                centro_manguito_z = sum(
                                    v.Z for v in vertices_principal
                                ) / len(vertices_principal)
                            else:
                                centro_manguito_x = centro_brep_geom.X
                                centro_manguito_y = centro_brep_geom.Y
                                centro_manguito_z = centro_brep_geom.Z
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (
                                centro_manguito_x,
                                centro_manguito_y,
                                centro_manguito_z,
                            )
                        else:
                            centro_manguito_x, centro_manguito_y, centro_manguito_z = (
                                self._temp_manguito_center.get(i, (0, 0, 0))
                            )

                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -centro_manguito_x + (longitud_original / 2.0),
                                -centro_manguito_y,
                                -centro_manguito_z,
                            ),
                        )

                        # *** CAMBIO: usar effective_rot_xy en lugar de data.angulo_xy raw ***
                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            long_xy_val = getattr(data, "longitud_xy", 0)
                            print(
                                f"  {item_name} [manguito] rot_xy={rot_xy:.2f}° (longitud_xy={long_xy_val:.3f}) rot_pitch={rot_pitch:.2f}°"
                            )

                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ),
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # --- CASO 2: DIFUSORES ---
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2

                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            punto_inicio_real = start_point
                            for j in range(i + 1, len(data_list)):
                                next_item = data_list[j]
                                next_tipo = next_item.get("type", "")
                                next_tipo_str = (
                                    next_tipo
                                    if isinstance(next_tipo, str)
                                    else (next_tipo[0] if len(next_tipo) > 0 else "")
                                )
                                if next_tipo_str not in TIPOS_ACCESORIOS:
                                    next_data = next_item["segment"].data
                                    punto_inicio_real = getattr(
                                        next_data, "start", start_point
                                    )
                                    if debug:
                                        print(
                                            f"  Usando inicio del segmento {j}: ({punto_inicio_real.X:.1f}, {punto_inicio_real.Y:.1f}, {punto_inicio_real.Z:.1f})"
                                        )
                                    break

                            _, vertices_dif = brep.GetVertices()
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -centro_dif_x, -centro_dif_y, -centro_dif_z
                                    ),
                                )

                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = punto_inicio_real.X + w_cubo
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )

                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                            if debug:
                                print(
                                    f"  Posición final difusor: ({offset_x:.1f}, {offset_y:.1f}, {punto_inicio_real.Z + 11:.1f})"
                                )

                        elif point_role == "final":
                            punto_final_real = (
                                data.end
                                if hasattr(data, "end")
                                else AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                )
                            )

                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    next_item = data_list[j]
                                    next_tipo = next_item.get("type", "")
                                    next_tipo_str = (
                                        next_tipo
                                        if isinstance(next_tipo, str)
                                        else (
                                            next_tipo[0] if len(next_tipo) > 0 else ""
                                        )
                                    )
                                    if next_tipo_str not in TIPOS_ACCESORIOS:
                                        next_data = next_item["segment"].data
                                        punto_final_real = getattr(
                                            next_data, "end", punto_final_real
                                        )
                                        if debug:
                                            print(
                                                f"  Usando final del segmento {j}: ({punto_final_real.X:.1f}, {punto_final_real.Y:.1f}, {punto_final_real.Z:.1f})"
                                            )
                                        break

                            _, vertices_dif = brep.GetVertices()
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -centro_dif_x, -centro_dif_y, -centro_dif_z
                                    ),
                                )
                            else:
                                centro_dif_z = 0

                            rot_diff = 0
                            if ang_int == 0:
                                rot_diff = 180
                            elif ang_int in [180, 179, 178]:
                                rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]:
                                rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 60

                            long_total_conducto = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )

                            if es_horizontal_pura:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                w_cubo = (long_total_conducto + padding) * factor
                                if ang_int in [180, 179, 178]:
                                    w_cubo = -long_total_conducto - padding
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - centro_dif_z + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                w_cubo = (long_total_conducto + padding) * factor
                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - centro_dif_z + 11,
                                    ),
                                )
                        else:
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    punto_medio_x, punto_medio_y, punto_medio_z
                                ),
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )

                    # --- CASO 3: TUBOS DINÁMICOS Y RESTO ---
                    else:
                        nx = (
                            sum(v.X for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        ny = (
                            sum(v.Y for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        nz = (
                            sum(v.Z for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # *** CAMBIO PRINCIPAL: usar effective_rot_xy en lugar de data.angulo_xy raw ***
                        # Antes:  rot_xy = 0.0 if getattr(data, 'longitud_xy', 0) < 0.1 else data.angulo_xy
                        # Ahora:  siempre se usa el valor pre-calculado que hereda del vecino XY
                        rot_xy = effective_rot_xy[i]
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        if debug:
                            long_xy_val = getattr(data, "longitud_xy", 0)
                            print(
                                f"  {item_name} rot_xy={rot_xy:.2f}° (longitud_xy={long_xy_val:.3f}) rot_pitch={rot_pitch:.2f}°"
                            )

                        # Roll
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta) — usa el ángulo efectivo (heredado si es vertical)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación) — el eje de rotación usa rot_xy efectivo para
                        # que el pitch se aplique en el plano correcto aun cuando longitud_xy=0
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        desplazamiento_neto = (longitud_original / 2.0) + (
                            (extension_final - extension_inicio) / 2.0
                        )

                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(
                                prop, nuevo_brep
                            ),
                        }
                        elementos_transformados.append(segment_brep)

            except Exception as e:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v2(
        self,
        data_list,
        conducto_width=75,
        color=None,
        point_role=None,
        point_side=None,
        debug=True,
    ):
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
                if not segment:
                    continue
                data = segment.data
                item_name = getattr(segment, "name", f"Segment_{i}")
                start_point = getattr(data, "start", None)
                if start_point is None:
                    continue
                tipo_str = item.get("type", "")

                # 1. IDENTIFICAR TIPO
                # tipo_raw = item.get('type', "")
                # tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else tipo_raw)

                # NOTA: Ya no saltamos los manguitos, los procesamos
                is_dinamic = tipo_str not in TIPOS_ACCESORIOS

                # 2. OBTENER VECTOR ACTUAL
                vec_curr = getattr(data, "vector_normalizado", None)
                if vec_curr is None:
                    vec_curr = AllplanGeo.Vector3D(
                        getattr(data, "delta_x", 0),
                        getattr(data, "delta_y", 0),
                        getattr(data, "delta_z", 0),
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
                        if prev_item.get("type") != "manguito":
                            vec_prev = prev_item["segment"].data.vector_normalizado
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_prev, vec_curr))
                            )
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el inicio del segundo segmento del codo, recortamos
                                    extension_inicio = -15.4
                                    if debug:
                                        print(
                                            f"  {item_name} - Inicio: Detectado 135°, aplicando recorte -22.5"
                                        )
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (
                                        CONDUCTO_WIDTH / 2.0
                                    ) * math.tan(a_rad / 2.0)
                                    extension_inicio = extension_teorica

                    # 2. Extensión al FINAL
                    extension_final = 0.0
                    if i < len(data_list) - 1:
                        next_item = data_list[i + 1]
                        if next_item.get("type") != "manguito":
                            vec_next = next_item["segment"].data.vector_normalizado
                            dot = max(
                                -1.0, min(1.0, get_dot_product(vec_curr, vec_next))
                            )
                            a_rad = math.acos(dot)

                            if 0.0001 < a_rad < SAFE_MAX_ANGLE:
                                # --- IF DISTINTO PARA 135° ---
                                if abs(a_rad - ANGULO_ESPECIAL_RAD) < TOLERANCIA:
                                    # En el final del primer segmento del codo, alargamos
                                    extension_final = 15.4
                                    if debug:
                                        print(
                                            f"  {item_name} - Final: Detectado 135°, aplicando alargue 22.5"
                                        )
                                else:
                                    # Lógica inicial (Tangente)
                                    extension_teorica = (
                                        CONDUCTO_WIDTH / 2.0
                                    ) * math.tan(a_rad / 2.0)
                                    extension_final = extension_teorica

                    # 3. Aplicación de longitud
                    longitud_original = getattr(data, "longitud_3d", 0.0)
                    longitud_total = (
                        longitud_original + extension_inicio + extension_final
                    )

                if debug and is_dinamic:
                    print(f"\n{item_name}")
                    print(f"  Long original: {longitud_original}")
                    print(
                        f"  Ext inicio: {extension_inicio}, Ext final: {extension_final}"
                    )
                    print(f"  Long total: {longitud_total}")

                # 5. PROCESAR BREPS
                lista_elem_3d_modified = []
                list_elem_3d = item.get("element3d", [])

                if is_dinamic:
                    for elem_3d in list_elem_3d:
                        brep_ajustado = None
                        # Asumimos que esta función estira el BREP simétricamente desde el centro
                        brep_ajustado = self.modificar_dimensiones_brep(
                            elem_3d, longitud_total
                        )
                        lista_elem_3d_modified.append(brep_ajustado)
                else:
                    lista_elem_3d_modified = list_elem_3d

                # Procesar cada elemento 3D
                conn_type_list = []
                segment_brep = None
                for e, elem_3d in enumerate(lista_elem_3d_modified):
                    prop = elem_3d.GetCommonProperties()
                    if is_dinamic and color:
                        prop.Color = color

                    brep = elem_3d.GetGeometryObject()
                    _, vertices = brep.GetVertices()  # type: ignore

                    # Cálculo de centro auxiliar para manguitos
                    punto_medio_x = (start_point.X + data.end.X) / 2.0
                    punto_medio_y = (start_point.Y + data.end.Y) / 2.0
                    punto_medio_z = (start_point.Z + data.end.Z) / 2.0

                    centro_brep_geom = AllplanGeo.Point3D(
                        punto_medio_x, punto_medio_y, punto_medio_z
                    )
                    if vertices:
                        nx = sum(v.X for v in vertices) / len(vertices)
                        ny = sum(v.Y for v in vertices) / len(vertices)
                        nz = sum(v.Z for v in vertices) / len(vertices)
                        centro_brep_geom = AllplanGeo.Point3D(nx, ny, nz)

                    nuevo_brep = None

                    # --- CASO 1: MANGUITOS ---

                    if tipo_str == "manguito":
                        segment_brep = None
                        if (
                            e == 0
                        ):  # Solo calculamos centro y transformaciones con el primer BREP
                            # Recalcular el centro del BREP principal (el primero)
                            _, vertices_principal = brep.GetVertices()  # type: ignore
                            if vertices_principal:
                                centro_manguito_x = sum(
                                    v.X for v in vertices_principal
                                ) / len(vertices_principal)
                                centro_manguito_y = sum(
                                    v.Y for v in vertices_principal
                                ) / len(vertices_principal)
                                centro_manguito_z = sum(
                                    v.Z for v in vertices_principal
                                ) / len(vertices_principal)
                            else:
                                centro_manguito_x = centro_brep_geom.X
                                centro_manguito_y = centro_brep_geom.Y
                                centro_manguito_z = centro_brep_geom.Z

                            # Guardar el centro para usar en todos los BREPs del manguito
                            if not hasattr(self, "_temp_manguito_center"):
                                self._temp_manguito_center = {}
                            self._temp_manguito_center[i] = (
                                centro_manguito_x,
                                centro_manguito_y,
                                centro_manguito_z,
                            )
                        else:
                            # Usar el centro calculado del primer BREP
                            centro_manguito_x, centro_manguito_y, centro_manguito_z = (
                                self._temp_manguito_center.get(i, (0, 0, 0))
                            )

                        # 1. Resetear al origen usando el centro del BREP principal
                        # Esto mantiene la posición relativa de los detalles
                        brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                -centro_manguito_x + (longitud_original / 2.0),
                                -centro_manguito_y,
                                -centro_manguito_z,
                            ),
                        )

                        # 2. Calcular ángulos
                        rot_xy = (
                            0.0
                            if getattr(data, "longitud_xy", 0) < 0.1
                            else data.angulo_xy
                        )
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        # 3. Aplicar rotaciones: Roll
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.1:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación)
                        if abs(rot_pitch) > 0.1:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # 4. Mover al punto medio del segmento del manguito
                        # El punto medio ya está calculado correctamente
                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ),
                        )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )
                    # --- CASO 2: DIFUSORES ---
                    elif tipo_str == "difusor":
                        move_offset = 0
                        if point_side == 0:
                            move_offset = CONDUCTO_WIDTH / 2
                        elif point_side == 2:
                            move_offset = -CONDUCTO_WIDTH / 2

                        ang_int = int(data.angulo_xy)

                        if debug:
                            print(
                                f"  start_point: ({start_point.X:.1f}, {start_point.Y:.1f}, {start_point.Z:.1f})"
                            )

                        if point_role == "inicial":
                            # DIFUSOR INICIAL: Debe estar al inicio absoluto del conducto
                            # Buscar el primer segmento dinámico para obtener el punto de inicio real
                            punto_inicio_real = start_point

                            # Si el difusor no es el primer elemento, buscar el inicio del primer tubo
                            # Buscar el primer tubo después del difusor
                            for j in range(i + 1, len(data_list)):
                                next_item = data_list[j]
                                next_tipo = next_item.get("type", "")
                                next_tipo_str = (
                                    next_tipo
                                    if isinstance(next_tipo, str)
                                    else (next_tipo[0] if len(next_tipo) > 0 else "")
                                )
                                # Encontrar el primer segmento dinámico
                                if next_tipo_str not in TIPOS_ACCESORIOS:
                                    next_data = next_item["segment"].data
                                    punto_inicio_real = getattr(
                                        next_data, "start", start_point
                                    )
                                    if debug:
                                        print(
                                            f"  Usando inicio del segmento {j}: ({punto_inicio_real.X:.1f}, {punto_inicio_real.Y:.1f}, {punto_inicio_real.Z:.1f})"
                                        )
                                    break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices()  # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -centro_dif_x, -centro_dif_y, -centro_dif_z
                                    ),
                                )

                            # Aplicar rotación
                            if ang_int != 0:
                                matriz_rot = AllplanGeo.Matrix3D()
                                matriz_rot.Rotation(
                                    AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                    AllplanGeo.Angle.FromDeg(data.angulo_xy),
                                )
                                brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular offset basado en ángulo
                            w_cubo = -60 if ang_int in [0, 90, 89] else 60
                            offset_x = (
                                punto_inicio_real.X + w_cubo
                            )  # (w_cubo if ang_int in [180, 178, 179] else move_offset)
                            offset_y = punto_inicio_real.Y + (
                                move_offset if ang_int in [0, 180, 178, 179] else w_cubo
                            )

                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    offset_x, offset_y - 1, punto_inicio_real.Z + 11
                                ),
                            )

                            if debug:
                                print(
                                    f"  Posición final difusor: ({offset_x:.1f}, {offset_y:.1f}, {punto_inicio_real.Z + 11:.1f})"
                                )

                        elif point_role == "final":
                            # DIFUSOR FINAL: Debe estar al final absoluto del conducto
                            # Buscar el último segmento dinámico
                            punto_final_real = (
                                data.end
                                if hasattr(data, "end")
                                else AllplanGeo.Point3D(
                                    start_point.X + data.delta_x,
                                    start_point.Y + data.delta_y,
                                    start_point.Z + data.delta_z,
                                )
                            )

                            # Si hay más segmentos después, buscar el final del último tubo
                            if i < len(data_list) - 1:
                                for j in range(len(data_list) - 1, i, -1):
                                    next_item = data_list[j]
                                    next_tipo = next_item.get("type", "")
                                    next_tipo_str = (
                                        next_tipo
                                        if isinstance(next_tipo, str)
                                        else (
                                            next_tipo[0] if len(next_tipo) > 0 else ""
                                        )
                                    )
                                    # Encontrar el último segmento dinámico
                                    if next_tipo_str not in TIPOS_ACCESORIOS:
                                        next_data = next_item["segment"].data
                                        punto_final_real = getattr(
                                            next_data, "end", punto_final_real
                                        )
                                        if debug:
                                            print(
                                                f"  Usando final del segmento {j}: ({punto_final_real.X:.1f}, {punto_final_real.Y:.1f}, {punto_final_real.Z:.1f})"
                                            )
                                        break

                            # Resetear BREP al origen
                            _, vertices_dif = brep.GetVertices()  # type: ignore
                            if vertices_dif:
                                centro_dif_x = sum(v.X for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_y = sum(v.Y for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                centro_dif_z = sum(v.Z for v in vertices_dif) / len(
                                    vertices_dif
                                )
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        -centro_dif_x, -centro_dif_y, -centro_dif_z
                                    ),
                                )
                            else:
                                centro_dif_z = 0

                            # Calcular rotación para difusor final
                            rot_diff = 0
                            if ang_int == 0:
                                rot_diff = 180
                            elif ang_int in [180, 179, 178]:
                                rot_diff = 0
                            elif ang_int in [-90, 89, 90, -89]:
                                rot_diff = -data.angulo_xy

                            matriz_rot = AllplanGeo.Matrix3D()
                            matriz_rot.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                                AllplanGeo.Angle.FromDeg(rot_diff),
                            )
                            brep = AllplanGeo.Transform(brep, matriz_rot)

                            # Calcular posición final
                            es_horizontal_pura = ang_int in [0, 180, 179, 178]
                            padding = 60

                            # Calcular desde el punto inicial al final
                            long_total_conducto = AllplanGeo.CalcLength(
                                AllplanGeo.Line3D(
                                    (
                                        data_list[0]["segment"].data.start
                                        if data_list[0].get("type", "")
                                        not in TIPOS_ACCESORIOS
                                        else start_point
                                    ),
                                    punto_final_real,
                                )
                            )

                            if es_horizontal_pura:
                                factor = -1 if ang_int in [180, 179, 178] else 1
                                w_cubo = (long_total_conducto + padding) * factor
                                if ang_int in [180, 179, 178]:
                                    w_cubo = -long_total_conducto - padding

                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + (padding * factor),
                                        punto_final_real.Y + move_offset,
                                        punto_final_real.Z - centro_dif_z + 11,
                                    ),
                                )
                            else:
                                factor = -1 if ang_int in [-90, -89] else 1
                                w_cubo = (long_total_conducto + padding) * factor

                                nuevo_brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        punto_final_real.X + move_offset,
                                        punto_final_real.Y + (padding * factor),
                                        punto_final_real.Z - centro_dif_z + 11,
                                    ),
                                )
                        else:
                            # Caso por defecto (sin point_role definido)
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    punto_medio_x, punto_medio_y, punto_medio_z
                                ),
                            )

                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )
                    else:
                        # 1. Resetear al Origen (0,0,0) usando el centroide geométrico
                        # Esto asegura que las rotaciones se hagan sobre el centro de la pieza
                        nx = (
                            sum(v.X for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        ny = (
                            sum(v.Y for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        nz = (
                            sum(v.Z for v in vertices) / len(vertices)
                            if vertices
                            else 0
                        )
                        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-nx, -ny, -nz))

                        # 2. Calcular Ángulos
                        rot_xy = (
                            0.0
                            if getattr(data, "longitud_xy", 0) < 0.1
                            else data.angulo_xy
                        )
                        rot_pitch = math.degrees(
                            math.atan2(data.delta_z, getattr(data, "longitud_xy", 0))
                        )

                        # print("############################################## ITEMS ROT: ", rot_xy, rot_pitch)
                        # 3. Aplicar Rotaciones
                        # Roll
                        if abs(getattr(data, "angulo_rotacion", 0)) > 0.001:
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(
                                AllplanGeo.Line3D(0, 0, 0, 1, 0, 0),
                                AllplanGeo.Angle.FromDeg(data.angulo_rotacion),
                            )
                            brep = AllplanGeo.Transform(brep, m)

                        # Yaw (Planta)
                        m = AllplanGeo.Matrix3D()
                        m.Rotation(
                            AllplanGeo.Line3D(0, 0, 0, 0, 0, 1),
                            AllplanGeo.Angle.FromDeg(rot_xy),
                        )
                        brep = AllplanGeo.Transform(brep, m)

                        # Pitch (Elevación)
                        if abs(rot_pitch) > 0.001:
                            rad_xy = math.radians(rot_xy)
                            axis = AllplanGeo.Line3D(
                                0, 0, 0, math.sin(rad_xy), -math.cos(rad_xy), 0
                            )
                            m = AllplanGeo.Matrix3D()
                            m.Rotation(axis, AllplanGeo.Angle.FromDeg(rot_pitch))
                            brep = AllplanGeo.Transform(brep, m)

                        # Calcular el punto medio del segmento EXTENDIDO
                        # Punto medio = start + vec * (long_original/2 + (ext_final - ext_inicio)/2)
                        desplazamiento_neto = (longitud_original / 2.0) + (
                            (extension_final - extension_inicio) / 2.0
                        )

                        mid_x = start_point.X + vec_curr.X * desplazamiento_neto
                        mid_y = start_point.Y + vec_curr.Y * desplazamiento_neto
                        mid_z = start_point.Z + vec_curr.Z * desplazamiento_neto

                        # desplazamiento_centro = (extension_final - extension_inicio) / 2.0
                        # mid_x = start_point.X + (getattr(data, 'delta_x', 0) * 0.5) + (vec_curr.X * desplazamiento_centro)
                        # mid_y = start_point.Y + (getattr(data, 'delta_y', 0) * 0.5) + (vec_curr.Y * desplazamiento_centro)
                        # mid_z = start_point.Z + (getattr(data, 'delta_z', 0) * 0.5) + (vec_curr.Z * desplazamiento_centro)

                        nuevo_brep = AllplanGeo.Move(
                            brep, AllplanGeo.Vector3D(mid_x, mid_y, mid_z)
                        )
                        elementos_transformados.append(
                            {
                                "index": i,
                                "element_type": tipo_str,
                                "element": AllplanBasisElements.ModelElement3D(
                                    prop, nuevo_brep
                                ),
                            }
                        )
            except Exception as e:
                if debug:
                    print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")

        if debug:
            print(f"\n{'='*70}")
            print(f"COMPLETADO: {len(elementos_transformados)} elementos procesados")
            print(f"{'='*70}\n")

        return elementos_transformados

    def center_and_connect_models_v1(
        self,
        data_list,
        overlap_mm=0.0,
        color=None,
        layers=[],
        layer_default=0,
        default_attrs=[],
        point_role=None,
        point_side=None,
        debug=True,
    ) -> List:
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
            item_name = item["segment"].name
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
                    direccion = (
                        "ARRIBA ↑"
                        if delta_z > 0
                        else "ABAJO ↓" if delta_z < 0 else "PUNTO"
                    )
                    print(f"SEGMENTO VERTICAL DETECTADO: {direccion}")
            else:
                # Caso normal: Segmento con componente horizontal
                # Ángulo en plano XY (rotación alrededor del eje Z)
                angulo_xy = (
                    segment.data.angulo_xy
                )  # math.degrees(math.atan2(delta_y, delta_x))

                # Ángulo de inclinación (elevación desde el plano XY)
                angulo_inclinacion = math.degrees(math.atan2(delta_z, distancia_xy))

            # Ángulo de rotación del elemento (alrededor de su propio eje X)
            angulo_rotacion_elemento = getattr(segment.data, "angulo_rotacion", 0)

            longitud_con_solape = longitud_segmento + (2 * overlap_mm)
            if debug:
                print(f"Longitud final con solape: {longitud_con_solape:.2f}mm")

            # Modificar dimensiones según el tipo
            dinamic_flag = item["type"][0] not in [
                "manguito",
                "codo_45",
                "codo_90",
                "conexion",
                "difusor",
            ]
            lista_elem_3d_modified = []

            if dinamic_flag:
                for elem_3d in list_elem_3d:
                    brep_ajustado = self.modificar_dimensiones_brep(
                        elem_3d, longitud_con_solape
                    )
                    lista_elem_3d_modified.append(brep_ajustado)
            else:
                lista_elem_3d_modified = list_elem_3d

            # Procesar cada elemento 3D
            for e, elem_3d in enumerate(lista_elem_3d_modified):
                prop = elem_3d.GetCommonProperties()
                if len(layers) > 0:
                    prop.Layer = next(
                        (d.get(item_name) for d in layers if item_name in d),
                        layer_default,
                    )
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

                centro_brep = AllplanGeo.Point3D(
                    punto_medio_x, punto_medio_y, punto_medio_z
                )
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
                    move = conducto_width / 2
                elif point_side == 2:
                    move = -conducto_width / 2
                else:
                    move = 0  # -conducto_width/2-2

                if item["type"][0] == "manguito":
                    nuevo_brep = AllplanGeo.Move(
                        brep,
                        AllplanGeo.Vector3D(
                            punto_medio_x - centro_brep.Y - ny / 2,
                            punto_medio_y - centro_brep.Y,
                            punto_medio_z - centro_brep.Y,
                        ),
                    )
                elif item["type"][0] == "difusor":
                    if point_role == "inicial":
                        if int(segment.data.angulo_xy) != 0:
                            matriz_rotacion_propia = AllplanGeo.Matrix3D()
                            eje_x = AllplanGeo.Line3D(
                                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                            )
                            matriz_rotacion_propia.SetRotation(
                                eje_x, AllplanGeo.Angle.FromDeg(segment.data.angulo_xy)
                            )
                            brep = AllplanGeo.Transform(brep, matriz_rotacion_propia)

                        W_CUBO = -120 if segment.data.angulo_xy in [0, 90, 89] else 120
                        if int(segment.data.angulo_xy) in [0, 180, 178, 179]:
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    start_point.X + W_CUBO,
                                    start_point.Y + move,
                                    punto_medio_z - nz + 11,
                                ),
                            )
                        else:
                            # W_CUBO = 80 if segment.data.angulo_xy == 0 else -80
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    start_point.X - move,
                                    start_point.Y + W_CUBO,
                                    punto_medio_z - nz + 11,
                                ),
                            )
                    elif point_role == "final":
                        angulo_rotacion = 0
                        if int(segment.data.angulo_xy) in [0]:
                            angulo_rotacion = 180
                        elif int(segment.data.angulo_xy) in [180, 179, 178]:
                            angulo_rotacion = 0
                        elif int(segment.data.angulo_xy) in [-90, 89, 90, -89]:
                            angulo_rotacion = -segment.data.angulo_xy

                        matriz_rotacion_propia = AllplanGeo.Matrix3D()
                        eje_x = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                        )
                        matriz_rotacion_propia.SetRotation(
                            eje_x, AllplanGeo.Angle.FromDeg(angulo_rotacion)
                        )
                        brep = AllplanGeo.Transform(brep, matriz_rotacion_propia)

                        if int(segment.data.angulo_xy) in [0, 180, 179, 178]:
                            W_CUBO = (
                                (-longitud_con_solape - 80)
                                if int(segment.data.angulo_xy) in [180, 179, 178]
                                else longitud_con_solape + 80
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    start_point.X + W_CUBO,
                                    start_point.Y + move,
                                    punto_medio_z - nz + 11,
                                ),
                            )
                        else:
                            W_CUBO = (
                                (-longitud_con_solape - 80)
                                if int(segment.data.angulo_xy) in [-90, -89]
                                else longitud_con_solape + 80
                            )
                            nuevo_brep = AllplanGeo.Move(
                                brep,
                                AllplanGeo.Vector3D(
                                    start_point.X + move,
                                    start_point.Y + W_CUBO,
                                    punto_medio_z - nz + 11,
                                ),
                            )
                    else:
                        nuevo_brep = AllplanGeo.Move(
                            brep,
                            AllplanGeo.Vector3D(
                                punto_medio_x, punto_medio_y, punto_medio_z
                            ),
                        )
                else:
                    # Paso 1: Trasladar al origen
                    brep_trasladado = AllplanGeo.Move(
                        brep,
                        AllplanGeo.Vector3D(
                            -centro_brep.X, -centro_brep.Y, -centro_brep.Z
                        ),
                    )

                    # Paso 2: Rotación del elemento alrededor de su propio eje X (antes de otras rotaciones)
                    # Esto es importante para orientar correctamente codos y conexiones
                    if abs(angulo_rotacion_elemento) > 0.001:
                        matriz_rotacion_propia = AllplanGeo.Matrix3D()
                        eje_x = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                        )
                        matriz_rotacion_propia.SetRotation(
                            eje_x, AllplanGeo.Angle.FromDeg(angulo_rotacion_elemento)
                        )
                        brep_rotado_propio = AllplanGeo.Transform(
                            brep_trasladado, matriz_rotacion_propia
                        )

                        if debug:
                            print(
                                f"Aplicada rotación propia del elemento: {angulo_rotacion_elemento:.2f}°"
                            )
                    else:
                        brep_rotado_propio = brep_trasladado

                    # Paso 3: Rotación en plano XY (alrededor del eje Z)
                    matriz_rotacion_xy = AllplanGeo.Matrix3D()
                    eje_z = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                    )
                    matriz_rotacion_xy.SetRotation(
                        eje_z, AllplanGeo.Angle.FromDeg(angulo_xy)
                    )

                    brep_rotado_xy = AllplanGeo.Transform(
                        brep_rotado_propio, matriz_rotacion_xy
                    )

                    # Paso 4: Rotación de inclinación (alrededor del eje Y local)
                    if abs(angulo_inclinacion) > 0.001:
                        matriz_rotacion_inclinacion = AllplanGeo.Matrix3D()

                        # Calcular el eje Y después de la rotación XY
                        eje_y_x = math.sin(math.radians(angulo_xy))
                        eje_y_y = -math.cos(math.radians(angulo_xy))
                        eje_y = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0),
                            AllplanGeo.Point3D(eje_y_x, eje_y_y, 0),
                        )

                        matriz_rotacion_inclinacion.SetRotation(
                            eje_y, AllplanGeo.Angle.FromDeg(angulo_inclinacion)
                        )
                        brep_rotado_final = AllplanGeo.Transform(
                            brep_rotado_xy, matriz_rotacion_inclinacion
                        )

                        if debug:
                            print(
                                f"Aplicada rotación de inclinación: {angulo_inclinacion:.2f}°"
                            )
                    else:
                        brep_rotado_final = brep_rotado_xy

                    # Paso 5: Trasladar al punto medio del segmento (en 3D)
                    nuevo_brep = AllplanGeo.Move(
                        brep_rotado_final,
                        AllplanGeo.Vector3D(
                            punto_medio_x, punto_medio_y, punto_medio_z
                        ),
                    )

                # Crear el ModelElement3D transformado
                elementos_transformados.append(
                    AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
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

    def split_list_by_ducts_connections(self, data_list, connection_types=None):
        """
        Separa los elementos en conductos y conexiones, manteniendo el índice
        de referencia para saber dónde debe insertarse cada conexión.
        """
        if connection_types is None:
            connection_types = ["manguito", "codo_45", "codo_90", "conexion", "difusor"]

        ducts = []
        connections = []

        for i, item in enumerate(data_list):
            tipo_raw = item.get("type", "")
            tipo_str = (
                tipo_raw
                if isinstance(tipo_raw, str)
                else (tipo_raw[0] if len(tipo_raw) > 0 else "")
            )
            if tipo_str in connection_types:
                connection = {"insert_at_index": i, "item": item}
                connections.append(connection)
            else:
                duct = {"insert_at_index": i, "item": item}
                ducts.append(duct)

        return {"ducts": ducts, "connections": connections}

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
                tipo_raw = item.get("type", "")
                tipo_str = (
                    tipo_raw
                    if isinstance(tipo_raw, str)
                    else (tipo_raw[0] if len(tipo_raw) > 0 else "")
                )

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
                tipo_raw = item.get("type", "")
                tipo_str = (
                    tipo_raw
                    if isinstance(tipo_raw, str)
                    else (tipo_raw[0] if len(tipo_raw) > 0 else "")
                )

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

    def modificar_dimensiones_brep(
        self, model_element, nueva_longitud
    ) -> AllplanBasisElements.ModelElement3D:
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
            model_element.GetCommonProperties(), nuevo_brep
        )
        # print(f"  Escalado BREP: {longitud_actual:.2f}mm → {nueva_longitud:.2f}mm (factor: {factor_escala:.3f})")
        return nuevo_model

    def modificar_dimensiones_brep_v1(
        self, model_element, nueva_longitud
    ) -> AllplanBasisElements.ModelElement3D:
        """
        Modifica la longitud (eje X) de un elemento 3D representado por BRep3D.
        """
        # 1. Acceder a la sección BRep3D
        geo = model_element.GetGeometryObject()

        # 2. Acceder a los vertices
        initial_vertices = geo.GetVertices()

        # 3. Determinar la longitud actual (máxima X)
        longitud_actual = max(v.X for v in initial_vertices[1])  # Debería ser 1500

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
            model_element.GetCommonProperties(), nuevo_brep
        )

        return nuevo_model


class PipelineProcessor:
    def __init__(
        self,
        elem3D_list,
        element_type=None,
        debug=False,
        build_ele=None,
        doc=None,
    ):
        """
        Args:
            elem3D_list: [{'type': 'conducto', 'elem': model}, ...]
        """
        self.templates = {item["type"]: item["elem"] for item in elem3D_list}
        self.debug = debug
        self.offset_codo = 0
        self.element_type_core = element_type
        # TE nodes (bifurcaciones) opcional: { (x,y,z): {"yaw_deg": float, ...} }
        self.te_nodes = {}
        self.build_ele = build_ele
        self.doc = doc
        # Cache de modelos de manguito por distribución + par de diámetros
        self._manguito_model_cache = {}
        self._manguito_classes = None
        # Cache de modelos de tubo por distribución + diámetro
        self._tubo_model_cache = {}
        self._tubo_classes = None
        # Cache de modelos de TE por distribución + trío de diámetros
        self._te_model_cache = {}
        self._te_classes = None
        # Evita mostrar el mismo aviso de TE inválida múltiples veces en un ciclo.
        self._te_invalid_warning_cache = set()
        # Orientación global capturada por PolyLib (start_orientation_capture).
        self.reference_orientation_angle = None
        # Si el usuario cancela una corrección de diámetro en codo, el ciclo de
        # generación debe abortarse para no crear reductores en un nodo angular.
        self.cancelled_by_elbow_diameter_conflict = False

    @staticmethod
    def _segment_diameter(seg_item, default=20.0) -> float:
        try:
            info = getattr(seg_item, "info", None)
            d = getattr(info, "diameter", None) if info is not None else None
            if isinstance(d, (list, tuple)) and d:
                d = d[0]
            if d is None:
                return float(default)
            return float(d)
        except Exception:
            return float(default)

    @staticmethod
    def _format_segment_label(diameter_mm: int, current_label: str = "") -> str:
        suffix = "P"
        try:
            parts = str(current_label or "").strip().split()
            if len(parts) > 1 and parts[-1]:
                suffix = parts[-1]
        except Exception:
            suffix = "P"
        return f"D{int(diameter_mm)} {suffix}"

    def _set_segment_diameter(self, seg_item, diameter_mm: int) -> bool:
        info = getattr(seg_item, "info", None)
        if info is None:
            return False
        try:
            old_diam = getattr(info, "diameter", None)
            info.diameter = int(diameter_mm)
            info.section_type = f"{int(diameter_mm)} mm"
            info.label = self._format_segment_label(
                int(diameter_mm), getattr(info, "label", "")
            )
            print(
                f"[AGUA][ELBOW][DIAM] segmento actualizado "
                f"{old_diam}mm -> {int(diameter_mm)}mm"
            )
            return True
        except Exception as ex:
            print(f"[AGUA][ELBOW][DIAM] No se pudo actualizar segmento: {ex}")
            return False

    def _ask_elbow_diameter(self, d_prev: float, d_next: float):
        di_prev = int(round(float(d_prev)))
        di_next = int(round(float(d_next)))
        diam_mayor = max(di_prev, di_next)
        diam_menor = min(di_prev, di_next)
        warning_message = (
            "ADVERTENCIA: Cambio de diámetro detectado en codo\n\n"
            f"Diámetro segmento anterior: {di_prev}mm\n"
            f"Diámetro segmento siguiente: {di_next}mm\n\n"
            "Los codos no permiten cambio de diámetro.\n"
            "¿Qué diámetro desea usar para ambos segmentos?\n\n"
            f"Sí: Usar diámetro MAYOR ({diam_mayor}mm)\n"
            f"No: Usar diámetro MENOR ({diam_menor}mm)\n"
            "Cancelar: No crear y corregir manualmente"
        )

        try:
            if hasattr(PythonUtility, "MB_YESNOCANCEL"):
                response = PythonUtility.ShowMessageBox(
                    warning_message, PythonUtility.MB_YESNOCANCEL
                )
            elif hasattr(PythonUtility, "MB_YESNO"):
                response = PythonUtility.ShowMessageBox(
                    warning_message, PythonUtility.MB_YESNO
                )
            else:
                PythonUtility.ShowMessageBox(warning_message, PythonUtility.MB_OK)
                response = getattr(PythonUtility, "IDCANCEL", None)
        except Exception as ex:
            print(f"[AGUA][ELBOW][DIAM] Error mostrando advertencia: {ex}")
            response = getattr(PythonUtility, "IDCANCEL", None)

        if response == getattr(PythonUtility, "IDYES", None):
            return diam_mayor
        if response == getattr(PythonUtility, "IDNO", None):
            return diam_menor
        return None

    def resolve_elbow_diameter_conflicts(self, segments: list) -> bool:
        """
        En un codo, el fitting tiene un único diámetro nominal. Si los dos
        segmentos adyacentes difieren, se unifica antes de calcular recortes y
        antes de decidir manguitos. La orientación se determina con los vectores:
        prev = p_curr - p_prev, next = p_next - p_curr; si cambia el eje
        dominante es un codo ortogonal.
        """
        from .vertex_utils import is_90_deg_turn

        self.cancelled_by_elbow_diameter_conflict = False
        for idx in range(1, len(segments)):
            seg_prev = segments[idx - 1]
            seg_curr = segments[idx]
            p_prev = getattr(getattr(seg_prev, "data", None), "start", None)
            p_curr = getattr(getattr(seg_prev, "data", None), "end", None)
            p_next = getattr(getattr(seg_curr, "data", None), "end", None)
            if not (p_prev and p_curr and p_next):
                continue
            if not is_90_deg_turn(p_prev, p_curr, p_next):
                continue

            d_prev = self._segment_diameter(seg_prev)
            d_next = self._segment_diameter(seg_curr)
            di_prev = int(round(float(d_prev)))
            di_next = int(round(float(d_next)))
            if di_prev == di_next:
                continue

            print(
                "[AGUA][ELBOW][DIAM] conflicto en codo idx=%s "
                "d_prev=%s d_next=%s node=(%.3f,%.3f,%.3f)"
                % (idx, di_prev, di_next, p_curr.X, p_curr.Y, p_curr.Z)
            )
            selected = self._ask_elbow_diameter(d_prev, d_next)
            if selected is None:
                self.cancelled_by_elbow_diameter_conflict = True
                print(
                    "[AGUA][ELBOW][DIAM] generación cancelada por conflicto "
                    f"de diámetro en codo idx={idx}"
                )
                return False

            if di_prev != selected:
                self._set_segment_diameter(seg_prev, selected)
            if di_next != selected:
                self._set_segment_diameter(seg_curr, selected)

        return True

    def _resolve_vertical_rotation_angle(self, p_prev, p_mid) -> float:
        """
        Prioridad de orientación vertical (port de fontaneria.py):
        1) reference_orientation_angle capturada,
        2) ángulo del tramo previo horizontal.
        """
        ref_orientation = getattr(self, "reference_orientation_angle", None)
        if ref_orientation is not None:
            return float(ref_orientation)

        if p_prev is None or p_mid is None:
            return 0.0

        prev_dx = p_mid.X - p_prev.X
        prev_dy = p_mid.Y - p_prev.Y
        prev_dz = p_mid.Z - p_prev.Z
        prev_len = math.sqrt(prev_dx * prev_dx + prev_dy * prev_dy + prev_dz * prev_dz)

        if prev_len > 1e-6 and abs(prev_dz) < 1e-6:
            return math.atan2(prev_dy, prev_dx)

        return 0.0

    def _load_manguito_classes(self):
        """
        Carga dinámica de clases de manguito para poder elegir tipo por diámetros
        (M20, M25, reductor 25-20) igual que en fontaneria.
        """
        if self._manguito_classes is not None:
            return self._manguito_classes

        classes = {"IS": None, "TD": None}
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            is_path = os.path.join(base_dir, "manguito_005_is.py")
            td_path = os.path.join(base_dir, "manguito_005_td.py")

            if os.path.exists(is_path):
                spec_is = importlib.util.spec_from_file_location(
                    "agua_manguito_005_is_runtime",
                    is_path,
                )
                if spec_is and spec_is.loader:
                    mod_is = importlib.util.module_from_spec(spec_is)
                    spec_is.loader.exec_module(mod_is)
                    classes["IS"] = getattr(mod_is, "ManguitoModel", None)

            if os.path.exists(td_path):
                spec_td = importlib.util.spec_from_file_location(
                    "agua_manguito_005_td_runtime",
                    td_path,
                )
                if spec_td and spec_td.loader:
                    mod_td = importlib.util.module_from_spec(spec_td)
                    spec_td.loader.exec_module(mod_td)
                    classes["TD"] = getattr(mod_td, "ManguitoTDModel", None)
        except Exception as ex:
            print(f"[AGUA] Error cargando clases de manguito por diámetro: {ex}")

        self._manguito_classes = classes
        return classes

    def _get_manguito_models_for_diameters(self, d1, d2, distribution_type="IS"):
        """
        Devuelve model_list de manguito ajustado al par de diámetros.
        Soporta IS/TD y cachea por par para evitar reconstrucciones repetidas.
        """
        try:
            di1 = int(round(float(d1)))
            di2 = int(round(float(d2)))
        except Exception:
            return []

        dist = "TD" if str(distribution_type).upper() == "TD" else "IS"
        cache_key = (dist, tuple(sorted((di1, di2))))
        cached = self._manguito_model_cache.get(cache_key)
        if cached is not None:
            print(
                f"[AGUA][MANGUITO] cache hit dist={dist} pair={cache_key[1]} elems={len(cached)}"
            )
            return cached

        if self.build_ele is None or self.doc is None:
            return []

        classes = self._load_manguito_classes()
        ModelClass = classes.get(dist) if classes else None
        if ModelClass is None:
            return []

        try:
            try:
                manguito_obj = ModelClass(self.build_ele, self.doc)
            except TypeError:
                manguito_obj = ModelClass(self.build_ele)

            if hasattr(manguito_obj, "set_diameters"):
                manguito_obj.set_diameters(di1, di2)

            type_manguito = getattr(manguito_obj, "type_manguito", None)
            model_list = manguito_obj.build() or []
            print(
                f"[AGUA][MANGUITO] build dist={dist} d1={di1} d2={di2} pair={cache_key[1]} "
                f"type_manguito={type_manguito} elems={len(model_list)}"
            )
            self._manguito_model_cache[cache_key] = model_list
            return model_list
        except Exception as ex:
            print(
                f"[AGUA] Error creando manguito para diámetros {di1}-{di2} ({dist}): {ex}"
            )
            self._manguito_model_cache[cache_key] = []
            return []

    def _normalize_tube_family(self, tube_system=None) -> str:
        """
        Normaliza el sistema de tubo del segmento a una familia interna.
        """
        raw = str(tube_system or "").strip().lower()
        if "multi" in raw:
            return "multicapa"
        if "arma" in raw:
            return "armaflex"
        if "poli" in raw:
            return "polietile"
        return "polietile"

    def _load_tubo_classes(self):
        """
        Carga dinámica de clases de tubo (IS/TD) para instanciar por diámetro real
        de cada segmento, evitando que todos tomen el último diámetro global.
        """
        if self._tubo_classes is not None:
            return self._tubo_classes

        classes = {
            "polietile": {"IS": None, "TD": None},
            "multicapa": {"IS": None, "TD": None},
            "armaflex": {"IS": None, "TD": None},
        }
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            is_path = os.path.join(base_dir, "tub_polietile_007_is.py")
            td_path = os.path.join(base_dir, "tub_polietile_007_td.py")
            multicapa_td_path = os.path.join(base_dir, "tub_multicapa_008_td.py")
            armaflex_td_path = os.path.join(base_dir, "armaflex_009_td.py")

            if os.path.exists(is_path):
                spec_is = importlib.util.spec_from_file_location(
                    "agua_tub_polietile_007_is_runtime",
                    is_path,
                )
                if spec_is and spec_is.loader:
                    mod_is = importlib.util.module_from_spec(spec_is)
                    spec_is.loader.exec_module(mod_is)
                    classes["polietile"]["IS"] = getattr(
                        mod_is, "TubPolietileModel", None
                    )

            if os.path.exists(td_path):
                spec_td = importlib.util.spec_from_file_location(
                    "agua_tub_polietile_007_td_runtime",
                    td_path,
                )
                if spec_td and spec_td.loader:
                    mod_td = importlib.util.module_from_spec(spec_td)
                    spec_td.loader.exec_module(mod_td)
                    classes["polietile"]["TD"] = getattr(
                        mod_td, "TubPolietileTDModel", None
                    )

            if os.path.exists(multicapa_td_path):
                spec_mc_td = importlib.util.spec_from_file_location(
                    "agua_tub_multicapa_008_td_runtime",
                    multicapa_td_path,
                )
                if spec_mc_td and spec_mc_td.loader:
                    mod_mc_td = importlib.util.module_from_spec(spec_mc_td)
                    spec_mc_td.loader.exec_module(mod_mc_td)
                    classes["multicapa"]["TD"] = getattr(
                        mod_mc_td, "TubMulticapaTDModel", None
                    )

            if os.path.exists(armaflex_td_path):
                spec_af_td = importlib.util.spec_from_file_location(
                    "agua_armaflex_009_td_runtime",
                    armaflex_td_path,
                )
                if spec_af_td and spec_af_td.loader:
                    mod_af_td = importlib.util.module_from_spec(spec_af_td)
                    spec_af_td.loader.exec_module(mod_af_td)
                    classes["armaflex"]["TD"] = getattr(
                        mod_af_td, "ArmaflexModel", None
                    )
        except Exception as ex:
            print(f"[AGUA][TUBO] Error cargando clases dinámicas: {ex}")

        self._tubo_classes = classes
        return classes

    def _set_build_ele_diameter_and_water(
        self, diameter_mm: int, dist: str, water_type=None
    ):
        """
        Sincroniza build_ele con diámetro/tipo de agua para crear el modelo correcto.
        """
        if self.build_ele is None:
            return
        try:
            diam_attr = getattr(self.build_ele, "DiametroAplicar", None)
            if diam_attr is not None and hasattr(diam_attr, "value"):
                diam_attr.value = int(diameter_mm)
            else:
                setattr(self.build_ele, "DiametroAplicar", int(diameter_mm))
        except Exception:
            pass

        if water_type is None:
            return
        try:
            target_names = (
                ["TipoDeAguaIS", "TipoDeAgua"]
                if dist == "IS"
                else ["TipoDeAguaTD", "TipoDeAgua"]
            )
            for name in target_names:
                try:
                    attr = getattr(self.build_ele, name, None)
                    if attr is not None and hasattr(attr, "value"):
                        attr.value = str(water_type)
                    else:
                        setattr(self.build_ele, name, str(water_type))
                except Exception:
                    continue
        except Exception:
            pass

    def _get_tubo_models_for_segment(
        self, diameter_mm, distribution_type="IS", water_type=None, tube_system=None
    ):
        """
        Devuelve [outer, inner?] del tubo para el diámetro/distribución del segmento.
        """
        try:
            di = int(round(float(diameter_mm)))
        except Exception:
            di = 20
        dist = "TD" if str(distribution_type).upper() == "TD" else "IS"
        family = self._normalize_tube_family(tube_system)
        water_key = str(water_type or "").strip().lower()
        cache_key = (family, dist, di, water_key)
        cached = self._tubo_model_cache.get(cache_key)
        if cached is not None:
            return cached

        if self.build_ele is None or self.doc is None:
            return []

        classes = self._load_tubo_classes()
        family_classes = classes.get(family, {}) if classes else {}
        ModelClass = family_classes.get(dist) if family_classes else None
        if ModelClass is None and classes:
            # Fallback seguro: polietilè
            ModelClass = classes.get("polietile", {}).get(dist)
        if ModelClass is None:
            return []

        try:
            self._set_build_ele_diameter_and_water(di, dist, water_type=water_type)
            tubo_obj = ModelClass(self.build_ele, self.doc)
            model_list = tubo_obj.build() or []
            self._tubo_model_cache[cache_key] = model_list
            print(
                f"[AGUA][TUBO] build family={family} dist={dist} diam={di} "
                f"water={water_key or '-'} elems={len(model_list)} (cache miss)"
            )
            return model_list
        except Exception as ex:
            print(
                f"[AGUA][TUBO] Error creando modelo dinámico family={family} "
                f"dist={dist} diam={di}: {ex}"
            )
            self._tubo_model_cache[cache_key] = []
            return []

    def _load_te_classes(self):
        """Carga dinámica de clases Te (IS/TD) para selección por diámetros."""
        if self._te_classes is not None:
            return self._te_classes

        classes = {"IS": None, "TD": None}
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            is_path = os.path.join(base_dir, "te_003_is.py")
            td_path = os.path.join(base_dir, "te_003_td.py")

            if os.path.exists(is_path):
                spec_is = importlib.util.spec_from_file_location(
                    "agua_te_003_is_runtime",
                    is_path,
                )
                if spec_is and spec_is.loader:
                    mod_is = importlib.util.module_from_spec(spec_is)
                    spec_is.loader.exec_module(mod_is)
                    classes["IS"] = getattr(mod_is, "TeModel", None)

            if os.path.exists(td_path):
                spec_td = importlib.util.spec_from_file_location(
                    "agua_te_003_td_runtime",
                    td_path,
                )
                if spec_td and spec_td.loader:
                    mod_td = importlib.util.module_from_spec(spec_td)
                    spec_td.loader.exec_module(mod_td)
                    classes["TD"] = getattr(mod_td, "TeTDModel", None)
        except Exception as ex:
            print(f"[AGUA][TE] Error cargando clases dinámicas: {ex}")

        self._te_classes = classes
        return classes

    def _get_te_models_for_diameters(
        self,
        d_main_in,
        d_main_out,
        d_branch,
        distribution_type="IS",
        mirror_model_x: bool = False,
    ):
        """
        Devuelve [outer, inner?] de TE para el nodo según diámetros reales
        (main_in, main_out, branch) y distribución IS/TD.
        """
        try:
            di_in = int(round(float(d_main_in)))
            di_out = int(round(float(d_main_out)))
            di_branch = int(round(float(d_branch)))
        except Exception:
            return []

        dist = "TD" if str(distribution_type).upper() == "TD" else "IS"

        def _is_supported_te_combo(di_in, di_out, di_branch):
            if di_in == di_out == di_branch and di_in in (20, 25, 32):
                return True
            triple_sorted = tuple(sorted((di_in, di_out, di_branch)))
            if di_in == 25 and di_out == 25 and di_branch == 20:
                return True
            if di_branch == 25 and triple_sorted == (20, 25, 25):
                return True
            if di_branch == 20 and triple_sorted == (20, 20, 25):
                return True
            return False

        if not _is_supported_te_combo(di_in, di_out, di_branch):
            warn_key = (dist, di_in, di_out, di_branch)
            if warn_key not in self._te_invalid_warning_cache:
                self._te_invalid_warning_cache.add(warn_key)
                msg = (
                    "No existe una TE para la combinación de diámetros seleccionada.\n\n"
                    f"Combinación detectada: {di_in}-{di_out}-{di_branch} ({dist}).\n\n"
                    "Modifique los diámetros de los segmentos para que coincidan "
                    "con los tipos de TE disponibles."
                )
                try:
                    PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
                except Exception:
                    print(f"[AGUA][TE] {msg}")
            print(
                f"[AGUA][TE] combinación no soportada dist={dist} "
                f"di_in={di_in} di_out={di_out} di_branch={di_branch}"
            )
            return []

        cache_key = (dist, di_in, di_out, di_branch, bool(mirror_model_x))
        cached = self._te_model_cache.get(cache_key)
        if cached is not None:
            print(
                f"[AGUA][TE] cache hit dist={dist} di_in={di_in} di_out={di_out} "
                f"di_branch={di_branch} mirror_model_x={mirror_model_x} elems={len(cached)}"
            )
            return cached

        if self.build_ele is None or self.doc is None:
            return []

        classes = self._load_te_classes()
        ModelClass = classes.get(dist) if classes else None
        if ModelClass is None:
            return []

        try:
            try:
                te_obj = ModelClass(self.build_ele, self.doc)
            except TypeError:
                te_obj = ModelClass(self.build_ele)

            if hasattr(te_obj, "set_diameters"):
                # Convención alineada con fontaneria.py:
                # set_diameters(main_in, branch, main_out)
                # - normal:    (main_in, branch, main_out)
                # - invertida: (main_out, branch, main_in)
                if mirror_model_x:
                    te_obj.set_diameters(di_out, di_branch, di_in)
                else:
                    te_obj.set_diameters(di_in, di_branch, di_out)

            type_te = getattr(te_obj, "type_te", None)
            model_list = te_obj.build() or []
            self._te_model_cache[cache_key] = model_list
            print(
                f"[AGUA][TE] build dist={dist} di_in={di_in} di_out={di_out} "
                f"di_branch={di_branch} mirror_model_x={mirror_model_x} "
                f"type_te={type_te} elems={len(model_list)}"
            )
            return model_list
        except Exception as ex:
            print(
                f"[AGUA][TE] Error creando modelo dinámico dist={dist} "
                f"di_in={di_in} di_out={di_out} di_branch={di_branch}: {ex}"
            )
            self._te_model_cache[cache_key] = []
            return []

    def modificar_dimensiones_brep(
        self, model_element, nueva_longitud
    ) -> AllplanBasisElements.ModelElement3D:
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

        # Crear nuevo ModelElement con las mismas propiedades y atributos.
        # Sin esto se pierde, por ejemplo, Material=CAVITAT en outer TD.
        nuevo_model = AllplanBasisElements.ModelElement3D(
            model_element.GetCommonProperties(), nuevo_brep
        )
        try:
            src_attrs = (
                model_element.GetAttributes()
                if hasattr(model_element, "GetAttributes")
                else None
            )
            if src_attrs:
                nuevo_model.SetAttributes(src_attrs)
        except Exception:
            pass
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
        v_base = AllplanGeo.Vector3D(0, 1, 0)

        dot = v_base.X * v_salida.X + v_base.Y * v_salida.Y
        cross_z = v_base.X * v_salida.Y - v_base.Y * v_salida.X

        # math.atan2 devuelve el ángulo exacto del giro entre los dos vectores
        angulo_rad = math.atan2(cross_z, dot)
        angulo_deg = math.degrees(angulo_rad)

        # Limpieza de precisión decimal para valores casi exactos (25, 30, 45, 90, etc.)
        if abs(angulo_deg - round(angulo_deg)) < eps:
            angulo_deg = float(round(angulo_deg))

        return angulo_deg

    def _aplicar_transformacion(
        self,
        model_element,
        segment_data,
        rotation_angle=0,
        elem_type="conducto",
        custom_position=None,
        next_seg=None,
        prev_seg=None,
        custom_yaw_deg: float | None = None,
        custom_mirror_x_local: bool = False,
    ) -> AllplanBasisElements.ModelElement3D:
        """
        Aplica transformaciones separando lógica horizontal (XY) y vertical (ZX/Pitch).
        """
        prop = model_element.GetCommonProperties()
        brep = model_element.GetGeometryObject()

        def _build_model_with_source_attrs(transformed_brep):
            nuevo_model = AllplanBasisElements.ModelElement3D(prop, transformed_brep)
            try:
                src_attrs = (
                    model_element.GetAttributes()
                    if hasattr(model_element, "GetAttributes")
                    else None
                )
                if src_attrs:
                    nuevo_model.SetAttributes(src_attrs)
            except Exception:
                pass
            return nuevo_model

        # 1. POSICIONAMIENTO INICIAL
        # Determinamos el punto de inserción (vértice o centro)
        p_destino = custom_position if custom_position else segment_data.start

        # 2. NORMALIZACIÓN (ORIGEN 0,0,0)
        # Para conductos rectos normalizamos al centro, pero codos, TES y manguitos
        # ya vienen centrados desde su propio modelador (IS/TD) y debemos conservar
        # ese origen para mantener la alineación y el encaje en nodo.
        if elem_type not in ("codo_90", "te", "manguito"):
            centro = self._get_center_from_vertices(brep)
            brep = AllplanGeo.Move(
                brep, AllplanGeo.Vector3D(-centro.X, -centro.Y, -centro.Z)
            )

        # ==========================================
        # PARTE 1: TRANSFORMACIONES LOCALES (ROLL)
        # ==========================================
        if abs(rotation_angle) > 0.015:
            matriz_roll = AllplanGeo.Matrix3D()
            eje_x_local = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
            )
            matriz_roll.SetRotation(
                eje_x_local, AllplanGeo.Angle.FromDeg(rotation_angle)
            )
            brep = AllplanGeo.Transform(brep, matriz_roll)

        # Manguito reductor: invertir orientación local (como fontaneria.py)
        # para el caso 25->20 usando el mismo modelo base 20-25.
        if elem_type == "manguito" and custom_mirror_x_local:
            try:
                mirror_x = AllplanGeo.Matrix3D()
                mirror_x.SetScaling(-1, 1, 1)
                brep = AllplanGeo.Transform(brep, mirror_x)
            except Exception:
                pass

        # ==========================================
        # PARTE 2: LÓGICA VERTICAL (PITCH / ZX)
        # ==========================================
        # TE: aplicar mirrors/rotación/elevación como en fontaneria.py
        if elem_type == "te" and custom_yaw_deg is not None:
            te_params = getattr(self, "te_nodes", {}).get(
                (round(p_destino.X, 3), round(p_destino.Y, 3), round(p_destino.Z, 3)),
                None,
            )
            if te_params:
                # Debug TE: por defecto ON (hasta estabilizar orientación XZ/YZ)
                debug_te = str(os.getenv("AGUA_DEBUG_TE", "1")).strip() not in (
                    "",
                    "0",
                    "false",
                    "False",
                )
                debug_te_pos = str(os.getenv("AGUA_DEBUG_TE_POS", "1")).strip() not in (
                    "",
                    "0",
                    "false",
                    "False",
                )
                ang = float(te_params.get("ang_rad", 0.0) or 0.0)
                plane = str(te_params.get("plane", "XY") or "XY")
                main_dir_3d = te_params.get("main_dir_3d", None)
                branch_dir_3d = te_params.get("branch_dir_3d", None)
                offset_perp_local = float(
                    te_params.get("offset_perp_local", 0.0) or 0.0
                )
                need_mx = bool(te_params.get("need_mirror_x_local", False))
                need_my = bool(te_params.get("need_mirror_y_local", False))
                branch_elevated = bool(te_params.get("branch_elevated", False))
                need_mz = bool(te_params.get("need_mirror_z_local", False))
                model_mirror_x = bool(te_params.get("model_mirror_x", False))
                di_in = int(round(float(te_params.get("d_main_in", 0) or 0)))
                di_out = int(round(float(te_params.get("d_main_out", 0) or 0)))
                di_branch = int(round(float(te_params.get("d_branch", 0) or 0)))

                if debug_te_pos:
                    try:
                        _e, _verts = brep.GetVertices()
                        if _verts:
                            minx = min(v.X for v in _verts)
                            miny = min(v.Y for v in _verts)
                            minz = min(v.Z for v in _verts)
                            maxx = max(v.X for v in _verts)
                            maxy = max(v.Y for v in _verts)
                            maxz = max(v.Z for v in _verts)
                            cx = (minx + maxx) * 0.5
                            cy = (miny + maxy) * 0.5
                            cz = (minz + maxz) * 0.5
                            print(
                                "[DBG TE POS] BREP_LOCAL bbox_min=(%.3f,%.3f,%.3f) bbox_max=(%.3f,%.3f,%.3f) bbox_center=(%.3f,%.3f,%.3f)"
                                % (minx, miny, minz, maxx, maxy, maxz, cx, cy, cz)
                            )
                        print(
                            "[DBG TE POS] APPLY_MOVE world_node=(%.3f,%.3f,%.3f) (Move after transforms)"
                            % (p_destino.X, p_destino.Y, p_destino.Z)
                        )
                    except Exception:
                        pass

                if debug_te:
                    print(
                        "[DBG TE] APPLY node=(%.3f,%.3f,%.3f) plane=%s ang=%.1f° mx=%s my=%s mz=%s elevated=%s offset_perp=%.2f"
                        % (
                            round(p_destino.X, 3),
                            round(p_destino.Y, 3),
                            round(p_destino.Z, 3),
                            plane,
                            math.degrees(ang),
                            str(need_mx),
                            str(need_my),
                            str(need_mz),
                            str(branch_elevated),
                            offset_perp_local,
                        )
                    )
                    print(
                        "[DBG TE] MODEL_FLAGS model_mirror_x=%s di_in=%s di_out=%s di_branch=%s"
                        % (
                            str(model_mirror_x),
                            str(di_in),
                            str(di_out),
                            str(di_branch),
                        )
                    )

                mat = AllplanGeo.Matrix3D()
                # Mirrors locales como en fontaneria: SIEMPRE antes de rotaciones (independiente del plano)
                if need_mx:
                    mirror_mat = AllplanGeo.Matrix3D()
                    mirror_mat.SetScaling(1, -1, 1)
                    mat = mat * mirror_mat
                if need_my:
                    mirror_mat = AllplanGeo.Matrix3D()
                    mirror_mat.SetScaling(-1, -1, 1)
                    mat = mat * mirror_mat

                # Desplazamiento local perpendicular al troncal (offset de centrado)
                if abs(offset_perp_local) > 1e-3 and plane == "XY":
                    # En XY, el eje perpendicular al troncal (X) es el eje Y local.
                    brep = AllplanGeo.Move(
                        brep, AllplanGeo.Vector3D(0.0, offset_perp_local, 0.0)
                    )

                # Caso especial robusto: troncal casi vertical (Z). La orientación por plano es ambigua,
                # así que alineamos X local -> troncal (3D) y luego giramos alrededor del troncal para
                # alinear Y local -> rama. Esto evita inversiones en el caso (Z + rama ±Y).
                try:
                    if (
                        isinstance(main_dir_3d, (list, tuple))
                        and isinstance(branch_dir_3d, (list, tuple))
                        and len(main_dir_3d) == 3
                        and len(branch_dir_3d) == 3
                    ):
                        mx, my, mz = (
                            float(main_dir_3d[0]),
                            float(main_dir_3d[1]),
                            float(main_dir_3d[2]),
                        )
                        bx, by, bz = (
                            float(branch_dir_3d[0]),
                            float(branch_dir_3d[1]),
                            float(branch_dir_3d[2]),
                        )

                        mnorm = math.sqrt(mx * mx + my * my + mz * mz)
                        bnorm = math.sqrt(bx * bx + by * by + bz * bz)
                        if mnorm > 1e-9 and bnorm > 1e-9:
                            mx, my, mz = mx / mnorm, my / mnorm, mz / mnorm
                            bx, by, bz = bx / bnorm, by / bnorm, bz / bnorm

                            if abs(mx) < 0.05 and abs(my) < 0.05 and abs(mz) > 0.95:
                                if debug_te:
                                    print(
                                        "[DBG TE] SPECIAL_VERTICAL main=(%.3f,%.3f,%.3f) branch=(%.3f,%.3f,%.3f)"
                                        % (mx, my, mz, bx, by, bz)
                                    )
                                # Secuencia determinista (estable): X local -> ±Z con rotación fija en Y,
                                # luego yaw en Z para alinear +Y local con la proyección de la rama (XY).
                                axis_y = AllplanGeo.Line3D(
                                    AllplanGeo.Point3D(0, 0, 0),
                                    AllplanGeo.Point3D(0, 1, 0),
                                )
                                axis_z = AllplanGeo.Line3D(
                                    AllplanGeo.Point3D(0, 0, 0),
                                    AllplanGeo.Point3D(0, 0, 1),
                                )

                                # X->+Z: rotY(-90°). X->-Z: rotY(+90°).
                                r_main = AllplanGeo.Matrix3D()
                                r_main.SetRotation(
                                    axis_y,
                                    AllplanGeo.Angle(
                                        -math.pi / 2 if mz >= 0 else math.pi / 2
                                    ),
                                )
                                mat = mat * r_main

                                # Yaw TE vertical:
                                # 1) tomar ángulo de la rama en XY respecto al eje X
                                #    (atan2(by, bx)),
                                # 2) aplicar desfase local de -90° del modelo TE.
                                if abs(bx) + abs(by) > 1e-9:
                                    ref_orientation = getattr(
                                        self, "reference_orientation_angle", None
                                    )
                                    theta_branch_xy = math.atan2(by, bx)
                                    theta_base = theta_branch_xy
                                    theta_source = "branch atan2(by,bx)"
                                    if not math.isfinite(theta_base):
                                        theta_base = (
                                            float(ref_orientation)
                                            if ref_orientation is not None
                                            else 0.0
                                        )
                                        theta_source = (
                                            "reference_orientation_angle"
                                            if ref_orientation is not None
                                            else "fallback=0"
                                        )
                                    theta = theta_base - (math.pi / 2.0)
                                    if debug_te:
                                        print(
                                            "[DBG TE] SPECIAL_VERTICAL theta=%.1f° (base=%.1f° source=%s, branch_xy=%.1f°, ref=%s, offset=-90°)"
                                            % (
                                                math.degrees(theta),
                                                math.degrees(theta_base),
                                                theta_source,
                                                math.degrees(theta_branch_xy),
                                                (
                                                    (
                                                        "%.1f°"
                                                        % math.degrees(
                                                            float(ref_orientation)
                                                        )
                                                    )
                                                    if ref_orientation is not None
                                                    else "None"
                                                ),
                                            )
                                        )
                                    r_yaw = AllplanGeo.Matrix3D()
                                    r_yaw.SetRotation(axis_z, AllplanGeo.Angle(theta))
                                    mat = mat * r_yaw

                                if need_mz:
                                    mirror_z_mat = AllplanGeo.Matrix3D()
                                    mirror_z_mat.SetScaling(1, 1, -1)
                                    mat = mat * mirror_z_mat

                                brep = AllplanGeo.Transform(brep, mat)
                                brep = AllplanGeo.Move(
                                    brep,
                                    AllplanGeo.Vector3D(
                                        p_destino.X, p_destino.Y, p_destino.Z
                                    ),
                                )
                                return _build_model_with_source_attrs(brep)
                except Exception:
                    pass

                # --- Plano XY (comportamiento existente) ---
                if plane == "XY":
                    if debug_te:
                        print("[DBG TE] PATH=XY")
                    axis_z = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                    )

                    rot_mat = AllplanGeo.Matrix3D()
                    rot_mat.SetRotation(axis_z, AllplanGeo.Angle(ang))
                    mat = mat * rot_mat

                    if branch_elevated:
                        if debug_te:
                            print(
                                "[DBG TE] XY branch_elevated: rotate branch -90° + mirror_z=%s"
                                % str(need_mz)
                            )
                        axis_x_rotated = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0),
                            AllplanGeo.Point3D(math.cos(ang), math.sin(ang), 0),
                        )
                        rot_branch_mat = AllplanGeo.Matrix3D()
                        rot_branch_mat.SetRotation(
                            axis_x_rotated, AllplanGeo.Angle(-math.pi / 2)
                        )
                        mat = mat * rot_branch_mat

                        if need_mz:
                            mirror_z_mat = AllplanGeo.Matrix3D()
                            mirror_z_mat.SetScaling(1, 1, -1)
                            mat = mat * mirror_z_mat

                # --- Plano XZ: preparar XY->XZ y rotar alrededor de Y ---
                elif plane == "XZ":
                    if debug_te:
                        print("[DBG TE] PATH=XZ")
                    axis_x = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                    )
                    axis_y = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
                    )

                    # Preparación: “acostar” el modelo de XY a XZ (Y local pasa a Z)
                    prep = AllplanGeo.Matrix3D()
                    prep.SetRotation(axis_x, AllplanGeo.Angle(-math.pi / 2))
                    mat = mat * prep

                    rot = AllplanGeo.Matrix3D()
                    rot.SetRotation(axis_y, AllplanGeo.Angle(ang))
                    mat = mat * rot

                    if branch_elevated:
                        trunk_axis = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0),
                            AllplanGeo.Point3D(math.cos(ang), 0.0, math.sin(ang)),
                        )
                        rot_branch_mat = AllplanGeo.Matrix3D()
                        rot_branch_mat.SetRotation(
                            trunk_axis, AllplanGeo.Angle(-math.pi / 2)
                        )
                        mat = mat * rot_branch_mat

                        if need_mz:
                            mirror_z_mat = AllplanGeo.Matrix3D()
                            mirror_z_mat.SetScaling(1, 1, -1)
                            mat = mat * mirror_z_mat

                # --- Plano YZ: preparar XY->YZ y rotar alrededor de X ---
                elif plane == "YZ":
                    if debug_te:
                        print("[DBG TE] PATH=YZ")
                    axis_z = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
                    )
                    axis_x = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                    )

                    # Preparación: girar 90° en Z para que X local pase a Y global
                    prep = AllplanGeo.Matrix3D()
                    # Nota: para replicar la mano/convención de fontaneria.py en YZ,
                    # el mapeo correcto es -90° (evita que la TE quede “al lado contrario”).
                    prep.SetRotation(axis_z, AllplanGeo.Angle(-math.pi / 2))
                    mat = mat * prep

                    rot = AllplanGeo.Matrix3D()
                    rot.SetRotation(axis_x, AllplanGeo.Angle(ang))
                    mat = mat * rot

                    if branch_elevated:
                        trunk_axis = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0),
                            AllplanGeo.Point3D(0.0, math.cos(ang), math.sin(ang)),
                        )
                        rot_branch_mat = AllplanGeo.Matrix3D()
                        rot_branch_mat.SetRotation(
                            trunk_axis, AllplanGeo.Angle(-math.pi / 2)
                        )
                        mat = mat * rot_branch_mat

                        if need_mz:
                            mirror_z_mat = AllplanGeo.Matrix3D()
                            mirror_z_mat.SetScaling(1, 1, -1)
                            mat = mat * mirror_z_mat

                brep = AllplanGeo.Transform(brep, mat)
                brep = AllplanGeo.Move(
                    brep, AllplanGeo.Vector3D(p_destino.X, p_destino.Y, p_destino.Z)
                )
                return _build_model_with_source_attrs(brep)

        # Para codos, usamos la lógica completa de fontaneria (por puntos),
        # y evitamos el pipeline simplificado pitch/yaw de abajo.
        if elem_type == "codo_90" and next_seg:
            # Allplan mantiene el intérprete vivo entre ejecuciones del PythonPart.
            # Forzamos recarga para no quedarnos con una versión cacheada del helper.
            import importlib
            from . import elbow_orientation as elbow_orientation_module

            elbow_orientation_module = importlib.reload(elbow_orientation_module)
            apply_elbow_transform = elbow_orientation_module.apply_elbow_transform

            p_prev = getattr(segment_data, "start", None)
            p_mid = getattr(segment_data, "end", None)
            p_next = getattr(next_seg, "end", None)
            ref = getattr(self, "reference_orientation_angle", None)
            if p_prev and p_mid and p_next:
                brep = apply_elbow_transform(
                    brep,
                    p_prev=p_prev,
                    p_mid=p_mid,
                    p_next=p_next,
                    reference_orientation_angle=ref,
                )
                # Traslado final al mundo y retorno (saltamos el resto de rotaciones)
                brep = AllplanGeo.Move(
                    brep, AllplanGeo.Vector3D(p_destino.X, p_destino.Y, p_destino.Z)
                )
                return _build_model_with_source_attrs(brep)

        # Manguito en transición vertical: aplicar la misma prioridad de orientación
        # que en fontaneria (orientación capturada o tramo horizontal previo).
        if elem_type == "manguito" and next_seg:
            p_prev = getattr(segment_data, "start", None)
            p_mid = getattr(segment_data, "end", None)
            p_next = getattr(next_seg, "end", None)
            if p_prev is not None and p_mid is not None and p_next is not None:
                dx = p_next.X - p_prev.X
                dy = p_next.Y - p_prev.Y
                dz = p_next.Z - p_prev.Z
                is_vertical_transition = (
                    abs(dx) < 1e-6 and abs(dy) < 1e-6 and abs(dz) > 1e-6
                )

                if is_vertical_transition:
                    yaw_ref = self._resolve_vertical_rotation_angle(p_prev, p_mid)
                    mat = AllplanGeo.Matrix3D()

                    if abs(yaw_ref) > 1e-6:
                        axis_z = AllplanGeo.Line3D(
                            AllplanGeo.Point3D(0, 0, 0),
                            AllplanGeo.Point3D(0, 0, 1),
                        )
                        mat_z = AllplanGeo.Matrix3D()
                        mat_z.SetRotation(axis_z, AllplanGeo.Angle(yaw_ref))
                        mat = mat_z

                    axis_y = AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0),
                        AllplanGeo.Point3D(0, 1, 0),
                    )
                    angle_y = -math.pi / 2.0 if dz > 0 else math.pi / 2.0
                    mat_y = AllplanGeo.Matrix3D()
                    mat_y.SetRotation(axis_y, AllplanGeo.Angle(angle_y))

                    mat = mat_y * mat if abs(yaw_ref) > 1e-6 else mat_y
                    brep = AllplanGeo.Transform(brep, mat)
                    brep = AllplanGeo.Move(
                        brep, AllplanGeo.Vector3D(p_destino.X, p_destino.Y, p_destino.Z)
                    )
                    return _build_model_with_source_attrs(brep)

        # 2.1. Orientación Base (Poner de pie si el destino es vertical)
        # Si el codo debe ir en vertical, primero rotamos 90° en su eje X local
        if elem_type == "codo_90" and next_seg:
            angulo_rotacion = (
                segment_data.angulo_z
                if int(segment_data.angulo_z) != 0
                else next_seg.angulo_z
            )
            matriz_vertical = AllplanGeo.Matrix3D()
            eje_x_local = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
            )
            # Lo rotamos para que apunte hacia arriba/abajo antes de la rotación final
            matriz_vertical.SetRotation(
                eje_x_local, AllplanGeo.Angle.FromDeg(angulo_rotacion)
            )
            brep = AllplanGeo.Transform(brep, matriz_vertical)

        # 2.2. Inclinación Específica (Pitch)
        angulo_pitch = 0.0
        if elem_type in ["conducto", "conexion", "manguito"]:
            angulo_pitch = segment_data.angulo_z
        elif elem_type == "codo_90" and next_seg:
            angulo_pitch = -(next_seg.angulo_z + segment_data.angulo_z)
            if int(segment_data.angulo_z) in [90, -90] and int(next_seg.angulo_xy) == 0:
                angulo_pitch = next_seg.angulo_z + segment_data.angulo_z
            elif int(next_seg.angulo_xy) == 180:
                angulo_pitch = next_seg.angulo_xy * 2

        if abs(angulo_pitch) > 0.01:
            matriz_pitch = AllplanGeo.Matrix3D()
            # Eje Y local como pivote de elevación
            eje_y_pitch = AllplanGeo.Line3D(
                AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 1, 0)
            )
            matriz_pitch.SetRotation(
                eje_y_pitch, AllplanGeo.Angle.FromDeg(-angulo_pitch)
            )
            brep = AllplanGeo.Transform(brep, matriz_pitch)

        # ==========================================
        # PARTE 3: LÓGICA HORIZONTAL (YAW / XY)
        # ==========================================
        angulo_yaw = 0.0
        if elem_type in ["conducto", "conexion", "manguito", "te"]:
            angulo_yaw = (
                float(custom_yaw_deg)
                if custom_yaw_deg is not None
                else segment_data.angulo_xy
            )
            # Port de fontaneria.py para verticales:
            # si el tramo es vertical y no hay yaw explícito, usar orientación capturada
            # (o, en su defecto, el ángulo del tramo previo horizontal).
            if custom_yaw_deg is None:
                try:
                    v = getattr(segment_data, "vector_normalizado", None)
                    is_vertical_seg = (
                        v is not None
                        and abs(v.X) < 1e-6
                        and abs(v.Y) < 1e-6
                        and abs(v.Z) > 1e-6
                    )
                    if is_vertical_seg:
                        prev_start = getattr(prev_seg, "start", None)
                        prev_end = getattr(prev_seg, "end", None)
                        # Heredar yaw del tramo horizontal anterior cuando exista.
                        # Si no existe, mantener fallback actual.
                        p_ref_start = (
                            prev_start
                            if prev_start is not None and prev_end is not None
                            else getattr(segment_data, "start", None)
                        )
                        p_ref_end = (
                            prev_end
                            if prev_start is not None and prev_end is not None
                            else getattr(segment_data, "end", None)
                        )
                        ref_yaw = self._resolve_vertical_rotation_angle(
                            p_ref_start,
                            p_ref_end,
                        )
                        if abs(ref_yaw) > 1e-6:
                            angulo_yaw = math.degrees(ref_yaw)
                except Exception:
                    pass
        else:
            # AJUSTE ESPECIAL PARA CODOS
            # En el nodo del codo, el tramo de ENTRADA es el segmento actual,
            # y el tramo de SALIDA es el siguiente segmento.
            v_entrada = segment_data.vector_normalizado
            v_salida = next_seg.vector_normalizado  # type: ignore

            # Inversión de cara (Flip) si el giro es a la derecha
            cross_z = v_entrada.X * v_salida.Y - v_entrada.Y * v_salida.X
            if cross_z < 0:
                m_flip = AllplanGeo.Matrix3D()
                m_flip.Rotation(
                    AllplanGeo.Line3D(
                        AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0)
                    ),
                    AllplanGeo.Angle.FromDeg(180),
                )
                brep = AllplanGeo.Transform(brep, m_flip)

            # Ángulo basado en la dirección de salida
            angulo_yaw = self.obtener_rotacion_codo(v_salida)

        # Aplicar rotación horizontal final
        matriz_yaw = AllplanGeo.Matrix3D()
        eje_z_global = AllplanGeo.Line3D(
            AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(0, 0, 1)
        )
        matriz_yaw.Rotation(eje_z_global, AllplanGeo.Angle.FromDeg(angulo_yaw))
        brep = AllplanGeo.Transform(brep, matriz_yaw)

        # ==========================================
        # PARTE 4: AJUSTES DE ALINEACIÓN Y TRASLACIÓN
        # ==========================================
        if elem_type == "codo_90":
            # Alineamos el codo con la bisectriz para que encaje con los recortes
            v_bisector = AllplanGeo.Vector3D(
                v_entrada.X - v_salida.X,
                v_entrada.Y - v_salida.Y,
                v_entrada.Z - v_salida.Z,
            )
            v_bisector.Normalize()
            dist_ajuste = (self.offset_codo / 2.0) - 2.3
            brep = AllplanGeo.Move(brep, v_bisector * dist_ajuste)

        # Traslado a la coordenada real en el espacio Allplan
        brep = AllplanGeo.Move(
            brep, AllplanGeo.Vector3D(p_destino.X, p_destino.Y, p_destino.Z)
        )

        return _build_model_with_source_attrs(brep)

    def process(self, segments, default_attrs=None, segment_cuts=None) -> list:
        """
        Procesa los segmentos y ubica conductos y codos con soporte
        para pendientes verticales (Pitch). Sin conexiones.

        segment_cuts: opcional dict {seg_idx: {"start": mm, "end": mm}} con recortes
        por codo/manguito (véase vertex_utils.compute_segment_cuts_for_path).
        """
        result_list = []
        element_index = 0
        num_seg = len(segments)
        segment_cuts = segment_cuts or {}

        # Detección de codos 90° compatible con fontaneria (cambio de eje dominante)
        from .vertex_utils import is_90_deg_turn

        # info de TE: opcional, se puede inyectar desde fuera
        te_nodes = getattr(self, "te_nodes", {}) or {}
        inserted_te_keys = set()
        cross_path_elbows = getattr(self, "cross_path_elbows", {}) or {}
        inserted_cross_path_elbows = set()
        cross_path_manguitos = getattr(self, "cross_path_manguitos", {}) or {}
        inserted_cross_path_manguitos = set()
        debug_te_pos = str(os.getenv("AGUA_DEBUG_TE_POS", "1")).strip() not in (
            "",
            "0",
            "false",
            "False",
        )

        def _build_aux_seg_data(p_start, p_end):
            """Construye un objeto mínimo compatible con _aplicar_transformacion(codo)."""
            obj = type("AuxSegData", (), {})()
            obj.start = p_start
            obj.end = p_end
            dx = p_end.X - p_start.X
            dy = p_end.Y - p_start.Y
            dz = p_end.Z - p_start.Z
            ln = math.sqrt(dx * dx + dy * dy + dz * dz)
            if ln > 1e-9:
                obj.vector_normalizado = AllplanGeo.Vector3D(dx / ln, dy / ln, dz / ln)
            else:
                obj.vector_normalizado = AllplanGeo.Vector3D(0.0, 0.0, 0.0)
            obj.angulo_xy = math.degrees(math.atan2(dy, dx)) if ln > 1e-9 else 0.0
            obj.angulo_z = 0.0
            return obj

        for i, seg_item in enumerate(segments):
            seg = seg_item.data
            v_unit = seg.vector_normalizado

            # -------------------------------------------------------
            # 1. DETERMINAR RECORTES (Offsets por codo + recortes por fitting)
            # -------------------------------------------------------
            offset_inicio = 0.0
            offset_final = 0.0

            if i > 0:
                # offset inicio si en el vértice start del segmento actual hay codo
                p_prev = getattr(segments[i - 1].data, "start", None)
                p_curr = getattr(segments[i - 1].data, "end", None)
                p_next = getattr(seg, "end", None)
                if (
                    p_prev
                    and p_curr
                    and p_next
                    and is_90_deg_turn(p_prev, p_curr, p_next)
                ):
                    offset_inicio = self.offset_codo

            if i < num_seg - 1:
                # offset final si en el vértice end del segmento actual hay codo
                next_seg = segments[i + 1].data
                p_prev = getattr(seg, "start", None)
                p_curr = getattr(seg, "end", None)
                p_next = getattr(next_seg, "end", None)
                if (
                    p_prev
                    and p_curr
                    and p_next
                    and is_90_deg_turn(p_prev, p_curr, p_next)
                ):
                    offset_final = self.offset_codo

            cuts = segment_cuts.get(i, {"start": 0.0, "end": 0.0})
            cut_start = float(cuts.get("start", 0.0))
            cut_end = float(cuts.get("end", 0.0))

            # -------------------------------------------------------
            # 2. CONDUCTO (TRAMO RECTO) - OUTER + INNER (opcional)
            # -------------------------------------------------------
            if self.element_type_core in self.templates:
                longitud_recortada = (
                    seg.longitud_3d - offset_inicio - offset_final - cut_start - cut_end
                )

                if longitud_recortada > 0:
                    # Centro del tramo recortado: desde start + cut_start, mitad del tramo útil
                    dist_al_centro = cut_start + (longitud_recortada / 2.0)
                    p_centro = AllplanGeo.Point3D(
                        seg.start.X + v_unit.X * dist_al_centro,
                        seg.start.Y + v_unit.Y * dist_al_centro,
                        seg.start.Z + v_unit.Z * dist_al_centro,
                    )

                    # Diámetro/distribución por segmento (como fontaneria: no usar último global)
                    seg_info = getattr(seg_item, "info", None)
                    seg_diameter = (
                        getattr(seg_info, "diameter", 20.0)
                        if seg_info is not None
                        else 20.0
                    )
                    if isinstance(seg_diameter, (list, tuple)) and seg_diameter:
                        seg_diameter = seg_diameter[0]
                    seg_dist = (
                        getattr(seg_info, "distribution_type", "IS")
                        if seg_info is not None
                        else "IS"
                    )
                    seg_water = (
                        getattr(seg_info, "water_type", None)
                        if seg_info is not None
                        else None
                    )
                    seg_system = (
                        getattr(seg_info, "system", None)
                        if seg_info is not None
                        else None
                    )
                    seg_dist = "TD" if str(seg_dist).upper() == "TD" else "IS"

                    dynamic_tube_models = self._get_tubo_models_for_segment(
                        seg_diameter,
                        distribution_type=seg_dist,
                        water_type=seg_water,
                        tube_system=seg_system,
                    )
                    tube_outer_tpl = (
                        dynamic_tube_models[0]
                        if dynamic_tube_models
                        else self.templates[self.element_type_core]
                    )
                    tube_inner_tpl = (
                        dynamic_tube_models[1]
                        if len(dynamic_tube_models) > 1
                        else self.templates.get(f"{self.element_type_core}_inner")
                    )
                    print(
                        f"[AGUA][TUBO] seg={i} diam={seg_diameter} dist={seg_dist} "
                        f"system={seg_system} "
                        f"modelo_outer={'dinamico' if dynamic_tube_models else 'template'}"
                    )

                    # OUTER
                    model_cond = self.modificar_dimensiones_brep(
                        tube_outer_tpl, longitud_recortada
                    )
                    prev_seg_data = segments[i - 1].data if i > 0 else None
                    element = self._aplicar_transformacion(
                        model_cond,
                        seg,
                        custom_position=p_centro,
                        prev_seg=prev_seg_data,
                    )

                    result_list.append(
                        {
                            "element": element,
                            "element_type": self.element_type_core,
                            "index": element_index,
                        }
                    )
                    element_index += 1

                    # INNER opcional: por convenio usamos "<core>_inner"
                    inner_key = f"{self.element_type_core}_inner"
                    if tube_inner_tpl is not None:
                        model_inner = self.modificar_dimensiones_brep(
                            tube_inner_tpl, longitud_recortada
                        )
                        element_inner = self._aplicar_transformacion(
                            model_inner,
                            seg,
                            custom_position=p_centro,
                            prev_seg=prev_seg_data,
                        )
                        result_list.append(
                            {
                                "element": element_inner,
                                "element_type": inner_key,
                                "index": element_index,
                            }
                        )
                        element_index += 1

            # -------------------------------------------------------
            # 3. CODO EN EL NODO FINAL DEL SEGMENTO
            # -------------------------------------------------------
            if i < num_seg - 1:
                next_seg = segments[i + 1].data
                p_prev = getattr(seg, "start", None)
                p_curr = getattr(seg, "end", None)
                p_next = getattr(next_seg, "end", None)
                node_key = (
                    (round(p_curr.X, 3), round(p_curr.Y, 3), round(p_curr.Z, 3))
                    if p_curr
                    else None
                )
                te_info_at_node = te_nodes.get(node_key) if node_key else None

                # -------------------------------------------------------
                # 3.A TE (BIFURCACIÓN) EN EL NODO (si aplica)
                # -------------------------------------------------------
                if "te" in self.templates and p_curr:
                    if te_info_at_node and node_key not in inserted_te_keys:
                        inserted_te_keys.add(node_key)
                        center_pt_raw = te_info_at_node.get("center_pt")
                        if (
                            isinstance(center_pt_raw, (tuple, list))
                            and len(center_pt_raw) == 3
                        ):
                            pos_nodo = AllplanGeo.Point3D(
                                float(center_pt_raw[0]),
                                float(center_pt_raw[1]),
                                float(center_pt_raw[2]),
                            )
                        else:
                            # Fallback: conservar comportamiento previo si no hay center_pt.
                            pos_nodo = p_curr
                        yaw = float(te_info_at_node.get("yaw_deg", 0.0) or 0.0)

                        # Selección de TE por diámetro (lógica equivalente a fontaneria.py)
                        te_dist = str(
                            te_info_at_node.get("distribution_type", "IS") or "IS"
                        )
                        te_dist = "TD" if te_dist.upper() == "TD" else "IS"
                        d_main_in = te_info_at_node.get("d_main_in", None)
                        d_main_out = te_info_at_node.get("d_main_out", None)
                        d_branch = te_info_at_node.get("d_branch", None)
                        if d_main_in is None or d_main_out is None or d_branch is None:
                            # Fallback: inferir con segmento actual/siguiente para no romper.
                            try:
                                info_curr = getattr(segments[i], "info", None)
                                info_next = (
                                    getattr(segments[i + 1], "info", None)
                                    if i + 1 < len(segments)
                                    else None
                                )
                                d_main_in = getattr(info_curr, "diameter", 20.0)
                                d_main_out = getattr(info_next, "diameter", d_main_in)
                                d_branch = d_main_in
                            except Exception:
                                d_main_in = d_main_out = d_branch = 20.0

                        mirror_model_x = bool(
                            te_info_at_node.get("model_mirror_x", False)
                            or (
                                (d_main_in is not None and d_main_out is not None)
                                and int(round(float(d_main_in)))
                                < int(round(float(d_main_out)))
                            )
                        )

                        dyn_te_models = self._get_te_models_for_diameters(
                            d_main_in,
                            d_main_out,
                            d_branch,
                            distribution_type=te_dist,
                            mirror_model_x=mirror_model_x,
                        )
                        te_outer_model = (
                            dyn_te_models[0] if dyn_te_models else self.templates["te"]
                        )
                        # Algunos modelos TD de TE mixta se modelan como "inner-only"
                        # y devuelven un único BRep dinámico. En ese caso debe tratarse
                        # como te_inner (con attrs/layer de paleta) y no crear inner template.
                        is_inner_only_te = False
                        try:
                            diam_set = {
                                int(round(float(d_main_in))),
                                int(round(float(d_main_out))),
                                int(round(float(d_branch))),
                            }
                            is_inner_only_te = (
                                te_dist == "TD"
                                and len(dyn_te_models) == 1
                                and len(diam_set) > 1
                            )
                        except Exception:
                            is_inner_only_te = False
                        te_inner_model = (
                            dyn_te_models[1]
                            if len(dyn_te_models) > 1
                            else self.templates.get("te_inner")
                        )
                        print(
                            "[AGUA][TE] node=%s dist=%s di_in=%s di_out=%s di_branch=%s "
                            "modelo_outer=%s elems_dyn=%s"
                            % (
                                str(node_key),
                                te_dist,
                                str(d_main_in),
                                str(d_main_out),
                                str(d_branch),
                                "dinamico" if dyn_te_models else "template",
                                str(len(dyn_te_models)),
                            )
                        )
                        if mirror_model_x:
                            print(
                                "[AGUA][TE] mirror_model_x=True (orden invertido de set_diameters)"
                            )
                        if is_inner_only_te:
                            print(
                                "[AGUA][TE] TE TD inner-only detectada: "
                                "se trata como te_inner y se omite inner template"
                            )

                        if debug_te_pos:
                            try:
                                print(
                                    "[DBG TE POS] CREATE key=%s center_pt=(%.3f,%.3f,%.3f) pos_nodo=(%.3f,%.3f,%.3f) seg_start=(%.3f,%.3f,%.3f) seg_end=(%.3f,%.3f,%.3f) v_unit=(%.3f,%.3f,%.3f) cut_start=%.2f cut_end=%.2f"
                                    % (
                                        str(node_key),
                                        pos_nodo.X,
                                        pos_nodo.Y,
                                        pos_nodo.Z,
                                        pos_nodo.X,
                                        pos_nodo.Y,
                                        pos_nodo.Z,
                                        seg.start.X,
                                        seg.start.Y,
                                        seg.start.Z,
                                        seg.end.X,
                                        seg.end.Y,
                                        seg.end.Z,
                                        v_unit.X,
                                        v_unit.Y,
                                        v_unit.Z,
                                        float(cut_start),
                                        float(cut_end),
                                    )
                                )
                            except Exception:
                                pass
                        element_te = self._aplicar_transformacion(
                            te_outer_model,
                            seg,
                            elem_type="te",
                            custom_position=pos_nodo,
                            custom_yaw_deg=yaw,
                        )
                        result_list.append(
                            {
                                "element": element_te,
                                "element_type": (
                                    "te_inner" if is_inner_only_te else "te"
                                ),
                                "index": element_index,
                            }
                        )
                        element_index += 1

                        # TE inner opcional (TD): mismo nodo y orientación que la outer
                        if is_inner_only_te:
                            te_inner_model = None
                        if te_inner_model is not None:
                            element_te_inner = self._aplicar_transformacion(
                                te_inner_model,
                                seg,
                                elem_type="te",
                                custom_position=pos_nodo,
                                custom_yaw_deg=yaw,
                            )
                            result_list.append(
                                {
                                    "element": element_te_inner,
                                    "element_type": "te_inner",
                                    "index": element_index,
                                }
                            )
                            element_index += 1

                if (
                    p_prev
                    and p_curr
                    and p_next
                    and node_key not in te_nodes
                    and is_90_deg_turn(p_prev, p_curr, p_next)
                ):
                    pos_nodo = seg.end

                    # Codo exterior (outer)
                    element_codo_outer = self._aplicar_transformacion(
                        self.templates["codo_90"],
                        seg,
                        elem_type="codo_90",
                        custom_position=pos_nodo,
                        next_seg=next_seg,
                    )

                    result_list.append(
                        {
                            "element": element_codo_outer,
                            "element_type": "codo_90",
                            "index": element_index,
                        }
                    )
                    element_index += 1

                    # Codo interior (inner), si existe plantilla registrada
                    if "codo_90_inner" in self.templates:
                        element_codo_inner = self._aplicar_transformacion(
                            self.templates["codo_90_inner"],
                            seg,
                            elem_type="codo_90",
                            custom_position=pos_nodo,
                            next_seg=next_seg,
                        )

                        result_list.append(
                            {
                                "element": element_codo_inner,
                                "element_type": "codo_90_inner",
                                "index": element_index,
                            }
                        )
                        element_index += 1

                # Manguito en vértice colineal (0° o 180°)
                # En fontaneria se crea siempre en tramos rectos, incluso si no hay cambio de diámetro.
                if "manguito" in self.templates:
                    # Si este nodo es una TE, NO crear manguito (se muestra la TE).
                    if p_curr:
                        if node_key in te_nodes:
                            continue

                    # Regla:
                    # - Crear si el tramo es colineal (dot ~ ±1)
                    # - O si hay cambio de diámetro entre segmentos consecutivos (aunque el dot no sea perfecto por pendientes/ruido)
                    def _get_seg_diam(_seg_item):
                        try:
                            info = getattr(_seg_item, "info", None)
                            d = (
                                getattr(info, "diameter", None)
                                if info is not None
                                else None
                            )
                            if isinstance(d, (list, tuple)) and d:
                                return float(d[0])
                            if d is None:
                                return None
                            return float(d)
                        except Exception:
                            return None

                    d_curr = _get_seg_diam(segments[i])
                    d_next = _get_seg_diam(segments[i + 1])
                    diam_change = (
                        d_curr is not None
                        and d_next is not None
                        and abs(float(d_curr) - float(d_next)) > 1e-6
                    )

                    v1 = seg.vector_normalizado
                    v2 = next_seg.vector_normalizado
                    dot = AllplanGeo.Vector3D.DotProduct(v1, v2)
                    # colineal si dot ~ 1 (mismo sentido) o dot ~ -1 (sentido opuesto)
                    is_colinear = abs(abs(dot) - 1.0) < 0.01

                    if is_colinear or diam_change:
                        pos_nodo = seg.end
                        # Distribución local del nodo (IS/TD): tomar del tramo actual;
                        # si falta, usar el siguiente; fallback IS.
                        dist_type = "IS"
                        try:
                            info_curr = getattr(segments[i], "info", None)
                            info_next = (
                                getattr(segments[i + 1], "info", None)
                                if i + 1 < len(segments)
                                else None
                            )
                            dist_raw = (
                                getattr(info_curr, "distribution_type", None)
                                or getattr(info_next, "distribution_type", None)
                                or "IS"
                            )
                            dist_type = "TD" if str(dist_raw).upper() == "TD" else "IS"
                        except Exception:
                            dist_type = "IS"

                        print(
                            "[AGUA][MANGUITO] node=(%.3f,%.3f,%.3f) seg=%s->%s "
                            "dot=%.4f colinear=%s diam_change=%s d_curr=%s d_next=%s dist=%s"
                            % (
                                pos_nodo.X,
                                pos_nodo.Y,
                                pos_nodo.Z,
                                str(i),
                                str(i + 1),
                                float(dot),
                                str(is_colinear),
                                str(diam_change),
                                str(d_curr),
                                str(d_next),
                                dist_type,
                            )
                        )

                        # Elegir modelo de manguito por PAR DE DIÁMETROS (port de fontaneria).
                        dyn_models = self._get_manguito_models_for_diameters(
                            d_curr if d_curr is not None else 20.0,
                            d_next if d_next is not None else 20.0,
                            distribution_type=dist_type,
                        )
                        manguito_outer_model = (
                            dyn_models[0] if dyn_models else self.templates["manguito"]
                        )
                        # Reductor TD (p.ej. 25-20) puede venir como único BRep "inner".
                        # En ese caso NO debemos tratarlo como outer ni crear inner template extra.
                        is_inner_only_reducer = (
                            dist_type == "TD"
                            and len(dyn_models) == 1
                            and d_curr is not None
                            and d_next is not None
                            and int(round(float(d_curr))) != int(round(float(d_next)))
                        )
                        print(
                            f"[AGUA][MANGUITO] modelo_outer={'dinamico' if dyn_models else 'template'} "
                            f"elems_dyn={len(dyn_models)}"
                        )
                        if is_inner_only_reducer:
                            print(
                                "[AGUA][MANGUITO] reductor TD inner-only detectado: "
                                "se trata como manguito_inner y se omite inner template"
                            )

                        # Reductor 25->20: mirror local para invertir el sentido.
                        need_mirror_x = False
                        try:
                            if d_curr is not None and d_next is not None:
                                di1 = int(round(float(d_curr)))
                                di2 = int(round(float(d_next)))
                                if {di1, di2} == {20, 25} and di1 > di2:
                                    need_mirror_x = True
                        except Exception:
                            need_mirror_x = False
                        if need_mirror_x:
                            print("[AGUA][MANGUITO] mirror_x_local=True (caso 25->20)")

                        element_manguito = self._aplicar_transformacion(
                            manguito_outer_model,
                            seg,
                            elem_type="manguito",
                            custom_position=pos_nodo,
                            next_seg=next_seg,
                            custom_mirror_x_local=need_mirror_x,
                        )
                        result_list.append(
                            {
                                "element": element_manguito,
                                "element_type": (
                                    "manguito_inner"
                                    if is_inner_only_reducer
                                    else "manguito"
                                ),
                                "index": element_index,
                            }
                        )
                        element_index += 1

                        # TD opcional: manguito inner (si existe en modelo dinámico o templates)
                        manguito_inner_model = None
                        if is_inner_only_reducer:
                            manguito_inner_model = None
                        elif len(dyn_models) > 1:
                            manguito_inner_model = dyn_models[1]
                        elif "manguito_inner" in self.templates:
                            manguito_inner_model = self.templates["manguito_inner"]

                        if manguito_inner_model is not None:
                            print(
                                "[AGUA][MANGUITO] creando inner "
                                f"(fuente={'dinamico' if len(dyn_models) > 1 else 'template'})"
                            )
                            element_manguito_inner = self._aplicar_transformacion(
                                manguito_inner_model,
                                seg,
                                elem_type="manguito",
                                custom_position=pos_nodo,
                                next_seg=next_seg,
                                custom_mirror_x_local=need_mirror_x,
                            )
                            result_list.append(
                                {
                                    "element": element_manguito_inner,
                                    "element_type": "manguito_inner",
                                    "index": element_index,
                                }
                            )
                            element_index += 1

            # -------------------------------------------------------
            # 3.C CODO EN NODO COMPARTIDO ENTRE PATHS (grado=2)
            # -------------------------------------------------------
            if "codo_90" in self.templates:
                for at_start in (False, True):
                    cp_info = cross_path_elbows.get((i, at_start))
                    if not cp_info:
                        continue
                    node_key_cp = cp_info.get("node_key")
                    other_pt = cp_info.get("other_point")
                    if not node_key_cp or not other_pt:
                        continue
                    if (
                        node_key_cp in te_nodes
                        or node_key_cp in inserted_cross_path_elbows
                    ):
                        continue

                    if at_start:
                        node_pt = getattr(seg, "start", None)
                        away_pt = getattr(seg, "end", None)
                    else:
                        node_pt = getattr(seg, "end", None)
                        away_pt = getattr(seg, "start", None)
                    if not node_pt or not away_pt:
                        continue

                    seg_for_elbow = (
                        _build_aux_seg_data(away_pt, node_pt) if at_start else seg
                    )
                    next_for_elbow = _build_aux_seg_data(node_pt, other_pt)

                    element_codo_outer = self._aplicar_transformacion(
                        self.templates["codo_90"],
                        seg_for_elbow,
                        elem_type="codo_90",
                        custom_position=node_pt,
                        next_seg=next_for_elbow,
                    )
                    result_list.append(
                        {
                            "element": element_codo_outer,
                            "element_type": "codo_90",
                            "index": element_index,
                        }
                    )
                    element_index += 1

                    if "codo_90_inner" in self.templates:
                        element_codo_inner = self._aplicar_transformacion(
                            self.templates["codo_90_inner"],
                            seg_for_elbow,
                            elem_type="codo_90",
                            custom_position=node_pt,
                            next_seg=next_for_elbow,
                        )
                        result_list.append(
                            {
                                "element": element_codo_inner,
                                "element_type": "codo_90_inner",
                                "index": element_index,
                            }
                        )
                        element_index += 1

                    inserted_cross_path_elbows.add(node_key_cp)
                    break

            # -------------------------------------------------------
            # 3.D MANGUITO EN NODO COMPARTIDO ENTRE PATHS (grado=2 colineal)
            # -------------------------------------------------------
            if "manguito" in self.templates:
                for at_start in (False, True):
                    cp_info = cross_path_manguitos.get((i, at_start))
                    if not cp_info:
                        continue
                    node_key_cp = cp_info.get("node_key")
                    other_pt = cp_info.get("other_point")
                    if not node_key_cp or not other_pt:
                        continue
                    if (
                        node_key_cp in te_nodes
                        or node_key_cp in inserted_cross_path_manguitos
                    ):
                        continue

                    if at_start:
                        node_pt = getattr(seg, "start", None)
                        away_pt = getattr(seg, "end", None)
                    else:
                        node_pt = getattr(seg, "end", None)
                        away_pt = getattr(seg, "start", None)
                    if not node_pt or not away_pt:
                        continue

                    seg_for_conn = (
                        _build_aux_seg_data(away_pt, node_pt) if at_start else seg
                    )
                    next_for_conn = _build_aux_seg_data(node_pt, other_pt)

                    def _get_seg_diam(_seg_item):
                        try:
                            info = getattr(_seg_item, "info", None)
                            d = (
                                getattr(info, "diameter", None)
                                if info is not None
                                else None
                            )
                            if isinstance(d, (list, tuple)) and d:
                                return float(d[0])
                            if d is None:
                                return None
                            return float(d)
                        except Exception:
                            return None

                    d_curr = _get_seg_diam(seg_item)
                    d_next = cp_info.get("other_diameter", d_curr)
                    if isinstance(d_next, (list, tuple)) and d_next:
                        d_next = d_next[0]
                    if d_next is None:
                        d_next = d_curr
                    dist_type = "IS"
                    try:
                        info_curr = getattr(seg_item, "info", None)
                        dist_raw = getattr(info_curr, "distribution_type", None) or "IS"
                        dist_type = "TD" if str(dist_raw).upper() == "TD" else "IS"
                    except Exception:
                        dist_type = "IS"

                    dyn_models = self._get_manguito_models_for_diameters(
                        d_curr if d_curr is not None else 20.0,
                        d_next if d_next is not None else 20.0,
                        distribution_type=dist_type,
                    )
                    manguito_outer_model = (
                        dyn_models[0] if dyn_models else self.templates["manguito"]
                    )
                    is_inner_only_reducer = False

                    element_manguito = self._aplicar_transformacion(
                        manguito_outer_model,
                        seg_for_conn,
                        elem_type="manguito",
                        custom_position=node_pt,
                        next_seg=next_for_conn,
                        custom_mirror_x_local=False,
                    )
                    result_list.append(
                        {
                            "element": element_manguito,
                            "element_type": (
                                "manguito_inner"
                                if is_inner_only_reducer
                                else "manguito"
                            ),
                            "index": element_index,
                        }
                    )
                    element_index += 1

                    manguito_inner_model = None
                    if len(dyn_models) > 1:
                        manguito_inner_model = dyn_models[1]
                    elif "manguito_inner" in self.templates:
                        manguito_inner_model = self.templates["manguito_inner"]

                    if manguito_inner_model is not None:
                        element_manguito_inner = self._aplicar_transformacion(
                            manguito_inner_model,
                            seg_for_conn,
                            elem_type="manguito",
                            custom_position=node_pt,
                            next_seg=next_for_conn,
                            custom_mirror_x_local=False,
                        )
                        result_list.append(
                            {
                                "element": element_manguito_inner,
                                "element_type": "manguito_inner",
                                "index": element_index,
                            }
                        )
                        element_index += 1

                    inserted_cross_path_manguitos.add(node_key_cp)
                    break

        return result_list
