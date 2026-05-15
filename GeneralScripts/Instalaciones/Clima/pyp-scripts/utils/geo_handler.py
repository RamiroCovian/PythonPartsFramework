import math
import NemAll_Python_Geometry      as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements  as AllplanBaseElements
from NemAll_Python_BaseElements import AttributeService

from typing import Any, List, Optional, Sequence, Tuple

from .codo_placement_offsets import get_colze_yaw_extra_deg, resolve_codo_translation_world_mm
from . import placement_logic as _placement

_LOG_TAPA = "[ClimaPolyline][TAPA]"


def _valid_attribute_id(raw: Any) -> bool:
    """Allplan suele devolver Id > 0; 0 o -1 = no encontrado / error."""
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return False
    return v > 0


def _expand_documents_for_attribute_lookup(doc: Any) -> List[Any]:
    """
    Añade candidatos (proyecto, catálogo…) al adaptador de dibujo, sin asumir API fija.
    """
    if doc is None:
        return []
    seen: set[int] = set()
    out: List[Any] = []

    def _add(d: Any) -> None:
        if d is None:
            return
        k = id(d)
        if k in seen:
            return
        seen.add(k)
        out.append(d)

    _add(doc)
    for meth in (
        "GetProjectDocument",
        "GetMasterDocument",
        "GetCatalogDocument",
        "GetAttributeCatalogDocument",
        "GetStdLibDocument",
    ):
        fn = getattr(doc, meth, None)
        if callable(fn):
            try:
                _add(fn())
            except Exception:
                pass
    try:
        from DocumentManager import DocumentManager

        inst = DocumentManager.get_instance()
        if inst is not None:
            _add(getattr(inst, "document", None))
    except Exception:
        pass
    return out


def _resolve_user_attr_string_id(
    docs: Any,
    primary_name: str,
    name_aliases: Optional[Sequence[str]] = None,
    id_fallback: Optional[int] = None,
    log_tag: str = _LOG_TAPA,
) -> int:
    """Resuelve ID de atributo de texto por nombre(s) en uno o varios documentos + fallback."""
    doc_list: List[Any] = []
    seen_doc: set[int] = set()

    def _collect(d0: Any) -> None:
        for x in _expand_documents_for_attribute_lookup(d0):
            k = id(x)
            if k in seen_doc:
                continue
            seen_doc.add(k)
            doc_list.append(x)

    if docs is None:
        pass
    elif isinstance(docs, (list, tuple)):
        for d in docs:
            _collect(d)
    else:
        _collect(docs)

    order: List[str] = []
    seen: set[str] = set()
    for n in (primary_name,) + tuple(name_aliases or ()):
        if not n or not str(n).strip():
            continue
        key = str(n).strip()
        if key in seen:
            continue
        seen.add(key)
        order.append(key)
    try:
        print(
            f"{log_tag} resolve: {len(doc_list)} doc candidate(s), try_names={order}",
        )
        for di, d in enumerate(doc_list):
            print(f"{log_tag}   doc[{di}]={d!r} type={type(d).__name__}")
    except Exception:
        pass
    for di, d in enumerate(doc_list):
        for name in order:
            try:
                raw = AttributeService.GetAttributeID(d, name)
                aid = int(raw) if raw is not None else 0
            except Exception as ex:
                try:
                    print(f"{log_tag} doc[{di}] GetAttributeID({name!r}) error: {ex}")
                except Exception:
                    pass
                aid = 0
            try:
                print(f"{log_tag} doc[{di}] GetAttributeID(name={name!r}) -> {aid}")
            except Exception:
                pass
            if _valid_attribute_id(aid):
                try:
                    print(f"{log_tag} OK id={aid} from doc[{di}] name={name!r}")
                except Exception:
                    pass
                return aid
    if id_fallback is not None:
        try:
            fid = int(id_fallback)
        except Exception:
            fid = 0
        if _valid_attribute_id(fid):
            try:
                print(f"{log_tag} using id_fallback -> {fid}")
            except Exception:
                pass
            return fid
    try:
        print(
            f"{log_tag} FAILED: attribute not in catalog for these documents (-1 = undefined). "
            f"Create the attribute in the project or set IMPULSIO_LAST_SEGMENT_TAPA_ATTR_ID_FALLBACK in clima_polyline.py"
        )
    except Exception:
        pass
    return 0


def _merge_user_attribute_string(
    model_element,
    docs: Any,
    attr_name: str,
    value: str,
    *,
    name_aliases: Optional[Sequence[str]] = None,
    id_fallback: Optional[int] = None,
    log_tag: str = _LOG_TAPA,
) -> bool:
    """Sustituye o añade un AttributeString; conserva demás atributos. Devuelve True si hubo SetAttributes."""
    if model_element is None or not attr_name:
        try:
            print(f"{log_tag} skip: no element or attr_name (element={model_element!r})")
        except Exception:
            pass
        return False
    if docs is None:
        try:
            print(f"{log_tag} skip: docs is None (cannot resolve attribute id)")
        except Exception:
            pass
        return False
    attr_id = _resolve_user_attr_string_id(
        docs, str(attr_name), name_aliases=name_aliases, id_fallback=id_fallback, log_tag=log_tag
    )
    if not _valid_attribute_id(attr_id):
        return False
    kept: List[Any] = []
    try:
        attrs = model_element.GetAttributes()
        if attrs:
            for attr_set in attrs.GetAttributeSets():  # type: ignore[attr-defined]
                for a in attr_set.GetAttributes() or []:
                    try:
                        if int(getattr(a, "Id", -1)) != attr_id:
                            kept.append(a)
                    except Exception:
                        kept.append(a)
    except Exception as ex:
        try:
            print(f"{log_tag} read existing attributes (non-fatal): {ex}")
        except Exception:
            pass
    kept.append(AllplanBaseElements.AttributeString(attr_id, str(value)))
    try:
        model_element.SetAttributes(
            AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet(kept)])
        )
    except Exception as ex:
        try:
            print(f"{log_tag} SetAttributes FAILED: {ex}")
        except Exception:
            pass
        return False
    try:
        verify = model_element.GetAttributes()
        if verify:
            for attr_set in verify.GetAttributeSets():  # type: ignore[attr-defined]
                for a in attr_set.GetAttributes() or []:
                    if int(getattr(a, "Id", -1)) == attr_id:
                        print(f"{log_tag} OK on element: Id={attr_id} Value={getattr(a, 'Value', a)!r}")
                        return True
        print(f"{log_tag} verify: attribute id {attr_id} not read back after SetAttributes")
    except Exception as ex:
        try:
            print(f"{log_tag} verify skipped: {ex}")
        except Exception:
            pass
    return True


class GeometryHandler:
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
        element_list = {
            "segments": [],
            "connections": []
        }
        segments = []
        connections = []
        list_atts_apply = []
        # attr_list = default_attrs

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
                if is_dinamic:
                    # Umbrales para considerar ángulos significativos
                    MIN_ANGLE_RAD = 0.0175  # ~1 grado - ignorar variaciones menores
                    MAX_ANGLE_RAD = math.pi - 0.0175  # ~179 grados - prácticamente recto

                    # --- VECINO ANTERIOR ---
                    if i > 0:
                        # Buscar el segmento anterior relevante (saltando manguitos)
                        prev_idx = i - 1
                        prev_item = data_list[prev_idx]
                        prev_tipo_raw = prev_item.get('type', "")
                        prev_tipo_str = prev_tipo_raw if isinstance(prev_tipo_raw, str) else (prev_tipo_raw[0] if len(prev_tipo_raw) > 0 else "")

                        # Si hay manguito, marcar pero NO calcular extensión
                        # Los manguitos ya tienen su propia longitud física
                        if prev_tipo_str == "manguito":
                            # is_prev_manguito = True
                            extension_final = 0.0  # No extender hacia el manguito
                            if debug:
                                print(f"  {item_name} - Manguito anterior detectado, ext inicio = 0")

                        else:
                            # Es otro tubo/segmento dinámico
                            p_data = prev_item["segment"].data
                            vec_prev = AllplanGeo.Vector3D(p_data.delta_x, p_data.delta_y, p_data.delta_z)
                            vec_prev.Normalize()

                            # Calcular ángulo entre vectores
                            dot = max(-1.0, min(1.0, get_dot_product(vec_prev, vec_curr)))
                            angle_rad = math.acos(dot)

                            # Solo aplicar extensión si hay un ángulo significativo
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
                        # Buscar el segmento siguiente relevante (saltando manguitos)
                        next_idx = i + 1
                        next_item = data_list[next_idx]
                        next_tipo_raw = next_item.get('type', "")
                        next_tipo_str = next_tipo_raw if isinstance(next_tipo_raw, str) else (next_tipo_raw[0] if len(next_tipo_raw) > 0 else "")

                        # Si hay manguito, marcar pero NO calcular extensión
                        if next_tipo_str == "manguito":
                            extension_inicio = 0.0  # No extender hacia el manguito
                            if debug:
                                print(f"  {item_name} - Manguito siguiente detectado, ext final = 0")
                        else:
                            # Es otro tubo/segmento dinámico
                            n_data = next_item["segment"].data
                            vec_next = AllplanGeo.Vector3D(n_data.delta_x, n_data.delta_y, n_data.delta_z)
                            vec_next.Normalize()

                            # Calcular ángulo entre vectores
                            dot = max(-1.0, min(1.0, get_dot_product(vec_curr, vec_next)))
                            angle_rad = math.acos(dot)

                            # Solo aplicar extensión si hay un ángulo significativo
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
                        segment_brep = {
                            "index": i,
                            "element_type": tipo_str,
                            "element": AllplanBasisElements.ModelElement3D(prop, nuevo_brep)
                        }
                        elementos_transformados.append(segment_brep)
                        # GUARDAR END REAL PARA CONTINUIDAD
                        # last_real_end_point = AllplanGeo.Point3D(
                        #     start_point.X + vec_curr.X * longitud_total,
                        #     start_point.Y + vec_curr.Y * longitud_total,
                        #     start_point.Z + vec_curr.Z * longitud_total
                        # )
                        # last_segment = segment
                        # conn_type_list = []

                # if len(conn_type_list) != 0 and not segment_brep:
                #     connections.append(conn_type_list)
                # else:
                #     segments.append(segment_brep)
            except Exception as e:
                if debug: print(f"ERROR CRÍTICO en elemento {i} ({tipo_str}): {e}")


        # element_list["segments"] = segments
        # element_list["connections"] = connections

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
            tipo_raw = item.get('type', "")
            tipo_str = tipo_raw if isinstance(tipo_raw, str) else (tipo_raw[0] if len(tipo_raw) > 0 else "")
            if tipo_str in connection_types:
                connection = {
                    "insert_at_index": i,
                    "item": item
                }
                connections.append(connection)
            else:
                duct = {
                    "insert_at_index": i,
                    "item": item
                }
                ducts.append(duct)

        return {
            "ducts": ducts,
            "connections": connections
        }

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
    def __init__(self, elem3D_list, element_type=None, debug=False,
                 conducto_factory=None, codo_factory=None, quiebro_factory=None,
                 reduccion_factory=None, enable_vertex_reducer=False,
                 first_segment_conducto_color: Optional[int] = None,
                 last_segment_conducto_color: Optional[int] = None,
                 conducto_default_body_color: Optional[int] = None,
                 first_segment_tapa_value: Optional[str] = None,
                 last_segment_tapa_value: Optional[str] = None,
                 last_segment_tapa_attr_aliases: Optional[Sequence[str]] = None,
                 last_segment_tapa_attr_id_fallback: Optional[int] = None,
                 attr_documents: Optional[Sequence[Any]] = None):
        """
        Args:
            elem3D_list:       [{'type': 'conducto', 'elem': model}, ...]
            conducto_factory:  Callable(seg) -> ModelElement3D | None
                               Si se proporciona, se usa por segmento en lugar del template.
            codo_factory:      Callable(seg, next_seg) -> ModelElement3D | None
                               Si se proporciona, se usa por codo en lugar del template.
            first_segment_conducto_color: Si no es None, color Allplan del **primer** tramo
                (cuerpo del conducto, no la flecha). Ej.: Retorn / recuperación.
            last_segment_conducto_color: Si no es None, color Allplan del **último** tramo
                (cuerpo del conducto). Ej.: Impulsió.
            conducto_default_body_color: Si no es None, se reaplica al cuerpo (primer
                subelemento) **en cada tramo** antes de los overrides de primero/último.
                Evita que la caché de factorías comparta el mismo ``ModelElement3D`` y que
                el color del tramo 0 contamine el resto (p. ej. Retorn 44 en todos).
            first_segment_tapa_value: Si no es None, asigna ``TAPA`` en el cuerpo del **primer**
                tramo (p. ej. Retorn / pieza entrada recuperador junto al color especial).
            last_segment_tapa_value: Si no es None, asigna este texto al atributo de usuario
                ``TAPA`` en el cuerpo del último tramo (mismo subelemento que el color).
            last_segment_tapa_attr_aliases: Nombres alternativos para buscar el ID del atributo.
            last_segment_tapa_attr_id_fallback: Si los nombres no resuelven, usar este ID (>0).
            attr_documents: Documento(s) candidatos para ``AttributeService.GetAttributeID`` (se
                expanden con catálogo/proyecto cuando la API lo permite).
        """
        self.templates = {item['type']: item['elem'] for item in elem3D_list}
        self.debug = debug
        self.offset_codo = 270
        # El Quiebro está modelado con referencia local distinta al conducto.
        # Quiebro2 está modelado con eje longitudinal local en +Y (como reduccions).
        # La alineación de pipeline usa +X como referencia, por lo que se compensa -90°.
        self.quiebro_yaw_offset_deg = -90.0
        self.element_type_core = element_type
        self.conducto_factory = conducto_factory
        self.codo_factory = codo_factory
        self.quiebro_factory = quiebro_factory
        self.reduccion_factory = reduccion_factory
        self.enable_vertex_reducer = bool(enable_vertex_reducer)
        self.first_segment_conducto_color = first_segment_conducto_color
        self.last_segment_conducto_color = last_segment_conducto_color
        self.conducto_default_body_color = conducto_default_body_color
        self.first_segment_tapa_value = first_segment_tapa_value
        self.last_segment_tapa_value = last_segment_tapa_value
        self.last_segment_tapa_attr_aliases = last_segment_tapa_attr_aliases
        self.last_segment_tapa_attr_id_fallback = last_segment_tapa_attr_id_fallback
        self.attr_documents = tuple(attr_documents) if attr_documents is not None else tuple()

    def _get_trim_in_out_mm(self, seg_item) -> Tuple[float, float]:
        """Recortes hendidura/junta (mm) según `SegmentInfo.diameter` (ver `placement_logic.py`)."""
        info = getattr(seg_item, "info", None)
        diam = getattr(info, "diameter", None) if info is not None else None
        return _placement.get_trim_in_out_mm(diam)

    @staticmethod
    def _diameter_key(seg_item) -> str:
        info = getattr(seg_item, "info", None)
        diam = getattr(info, "diameter", None) if info is not None else None
        return str(diam).strip() if diam is not None else ""

    @staticmethod
    def _is_reductor_segment(seg_item) -> bool:
        return PipelineProcessor._diameter_key(seg_item).lower() == "reductor"

    @staticmethod
    def _diameter_width_mm(seg_item) -> float:
        """Extrae ancho principal desde SegmentInfo.diameter ('350x150' -> 350.0)."""
        key = PipelineProcessor._diameter_key(seg_item)
        if not key:
            return 0.0
        try:
            return float(str(key).split("x", 1)[0].strip())
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _reduccion_axis_length_mm(seg, next_seg_data) -> float:
        """
        Largo axial del tramo reductor para dimensionar la pieza y anclar el centro.

        En transiciones 150×150 ↔ 750×150 la polilínea desplaza el centro lateralmente;
        ``longitud_3d`` es la cuerda √(Δx²+Δy²) y resulta mayor que el avance real según
        el eje del conducto de salida. El modelo del reductor sigue ese eje (+Y local), así
        que aquí se usa la proyección escalar del vector del segmento sobre ``v_out``.
        """
        d_x = float(seg.end.X - seg.start.X)
        d_y = float(seg.end.Y - seg.start.Y)
        d_z = float(seg.end.Z - seg.start.Z)
        v = next_seg_data.vector_normalizado
        axis_len = abs(
            d_x * float(v.X) + d_y * float(v.Y) + d_z * float(v.Z)
        )
        chord = float(getattr(seg, "longitud_3d", 0.0) or 0.0)
        return axis_len if axis_len >= 1.0 else chord

    def _codo_clearance_end_mm(self, seg_item) -> float:
        """Hueco en el extremo final del tramo (tramo entrante al codo en el vértice)."""
        k = self._diameter_key(seg_item)
        if not k:
            return float(self.offset_codo)
        tin, _ = _placement.get_codo90_trim_in_out_mm(k)
        return float(tin)

    def _codo_clearance_start_mm(self, seg_item) -> float:
        """Hueco en el extremo inicial del tramo (tramo saliente del codo en el vértice)."""
        k = self._diameter_key(seg_item)
        if not k:
            return float(self.offset_codo)
        _, tout = _placement.get_codo90_trim_in_out_mm(k)
        return float(tout)

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
        # Extraer los vértices con tolerancia a firmas distintas de GetVertices()
        # (según tipo geométrico/version de API puede devolver 2, 3 o más valores).
        error = 0
        vertices = None
        try:
            raw = brep.GetVertices()
        except Exception:
            raw = None

        if isinstance(raw, (list, tuple)):
            # Caso A: devuelve directamente lista de vértices
            if raw and hasattr(raw[0], "X") and hasattr(raw[0], "Y") and hasattr(raw[0], "Z"):
                vertices = raw
            else:
                # Caso B: devuelve tupla con error + una o más colecciones
                for item in raw:
                    if isinstance(item, int):
                        error = item
                        continue
                    if isinstance(item, (list, tuple)) and item and hasattr(item[0], "X"):
                        vertices = item
                        break

        if error != 0 or not vertices:
            # Fallback para geometrías lineales/atípicas sin lista de vértices utilizable
            try:
                p1 = brep.StartPoint
                p2 = brep.EndPoint
                return AllplanGeo.Point3D(
                    (p1.X + p2.X) * 0.5,
                    (p1.Y + p2.Y) * 0.5,
                    (p1.Z + p2.Z) * 0.5,
                )
            except Exception:
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

    def _aplicar_transformacion(
        self,
        model_element,
        segment_data,
        rotation_angle=0,
        elem_type="conducto",
        custom_position=None,
        next_seg=None,
        codo_diameter_key=None,
        local_center_override=None,
        local_anchor_override=None,
    ) -> AllplanBasisElements.ModelElement3D:
        """
        Aplica transformaciones separando lógica horizontal (XY) y vertical (ZX/Pitch).
        """
        prop = model_element.GetCommonProperties()
        brep = model_element.GetGeometryObject()

        # 1. POSICIONAMIENTO INICIAL
        # Determinamos el punto de inserción (vértice o centro)
        p_destino = custom_position if custom_position else segment_data.start

        # 2. NORMALIZACIÓN (ORIGEN 0,0,0)
        # - Conductos/conexiones: centrado para rotar sin deriva.
        # - Codo: anclaje a una esquina de referencia (evita “offsets mágicos” por cuadrante).
        if elem_type == "codo_90":
            try:
                _err, _verts = brep.GetVertices()
            except Exception:
                _verts = None

            if local_anchor_override is not None:
                anchor = local_anchor_override
                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-anchor.X, -anchor.Y, -anchor.Z))
            elif _verts:
                # El codo se modela cerca del origen; usamos el vértice más “cercano” a (0,0,0)
                # como punto de anclaje para que el nodo de la polilínea coincida siempre.
                anchor = min(_verts, key=lambda v: (v.X * v.X + v.Y * v.Y + v.Z * v.Z))
                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-anchor.X, -anchor.Y, -anchor.Z))
            else:
                # Fallback: si no hay vértices, centrado como antes
                centro = self._get_center_from_vertices(brep)
                brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(-centro.X, -centro.Y, -centro.Z))
        else:
            centro = (
                local_center_override
                if local_center_override is not None
                else self._get_center_from_vertices(brep)
            )
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
        if elem_type in ["conducto", "conexion", "reduccion"]:
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
        elif elem_type == "reduccion":
            # Mantener el cuerpo del reductor estable respecto al eje principal
            # del flujo (usar tramo adyacente cuando el tramo "reductor" interno
            # fue desviado para seguir la línea roja de centrado).
            base_seg = next_seg if next_seg is not None else segment_data
            # `reduccions.py` está modelado con eje longitudinal local en +Y.
            # El pipeline alinea por convención desde +X, así que compensamos -90°.
            angulo_yaw = float(base_seg.angulo_xy) - 90.0
        elif elem_type == "quiebro":
            # Alinear eje local +Y del quiebro2 con el eje del segmento en XY.
            angulo_yaw = float(segment_data.angulo_xy) + float(self.quiebro_yaw_offset_deg)
        else:
            # AJUSTE ESPECIAL PARA CODOS (codo colocado en seg.end entre seg -> next_seg)
            # Convención: el codo “base” está orientado con la entrada en +X.
            v_entrada = segment_data.vector_normalizado
            v_salida = next_seg.vector_normalizado if next_seg else segment_data.vector_normalizado  # type: ignore

            # Sentido del giro en XY (desde v_entrada hacia v_salida, vista desde +Z)
            cross_z = v_entrada.X * v_salida.Y - v_entrada.Y * v_salida.X
            # Flip si el giro es a derechas (cross_z < 0) para reutilizar el mismo template
            if cross_z < 0:
                m_flip = AllplanGeo.Matrix3D()
                eje_x_local = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Point3D(1, 0, 0))
                m_flip.Rotation(eje_x_local, AllplanGeo.Angle.FromDeg(180))
                brep = AllplanGeo.Transform(brep, m_flip)

            # Rotación horizontal: alinear entrada con v_entrada + corrección según modelo colze (depende del giro)
            yaw_extra = get_colze_yaw_extra_deg(cross_z)
            angulo_yaw = self.obtener_rotacion_codo(v_entrada) + yaw_extra

        # Aplicar rotación horizontal final
        matriz_yaw = AllplanGeo.Matrix3D()
        eje_z_global = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,0,1))
        matriz_yaw.Rotation(eje_z_global, AllplanGeo.Angle.FromDeg(angulo_yaw))
        brep = AllplanGeo.Transform(brep, matriz_yaw)

        # Traslado a la coordenada real en el espacio Allplan (+ ajuste por diámetro del codo, mm)
        tx, ty, tz = p_destino.X, p_destino.Y, p_destino.Z
        if elem_type == "codo_90" and next_seg is not None:
            v_in = segment_data.vector_normalizado
            v_out = next_seg.vector_normalizado
            ox, oy, oz = resolve_codo_translation_world_mm(codo_diameter_key, v_in, v_out)
            # En codos puramente horizontales (XY), forzar cota Z segun sentido
            # de giro para mantener consistencia visual del template.
            if abs(float(v_in.Z)) < 1e-6 and abs(float(v_out.Z)) < 1e-6:
                cross_z_xy = float(v_in.X * v_out.Y - v_in.Y * v_out.X)
                oz = 100.0 if cross_z_xy < 0.0 else -100.0
            tx += ox
            ty += oy
            tz += oz

        brep = AllplanGeo.Move(brep, AllplanGeo.Vector3D(tx, ty, tz))

        return AllplanBasisElements.ModelElement3D(prop, brep)

    def process(self, segments, default_attrs=None) -> list:
        """
        Procesa los segmentos y ubica conductos y codos.
        Los conductos se recortan en los extremos donde hay un giro (offset_codo)
        para dejar espacio al codo. El codo se coloca en el vértice.
        """
        result_list = []
        num_seg = len(segments)
        element_index = 0
        # Corrimiento lateral acumulado para mantener continuidad de centros tras reductores.
        offset_x = 0.0
        offset_y = 0.0
        offset_z = 0.0

        def _angle_delta(a, b):
            return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)

        def _signed_angle_delta(a, b):
            return (float(a) - float(b) + 180.0) % 360.0 - 180.0

        QUIEBRO_MIN_ANGLE = 0.5
        QUIEBRO_MAX_ANGLE = 45.0
        QUIEBRO_ANGLE_EPS = 1e-3
        CODO_PERP_DOT_TOL = 0.02
        is_quiebro_segment = [False] * num_seg

        # Detectar "quiebro2" como patrón recto->inclinado->recto:
        # - tramo i tiene giro relativo respecto al previo en (0, 45]
        # - tramo i+1 vuelve a alinearse con el tramo previo (misma dirección base)
        #   para evitar marcar también el tramo de salida.
        for i in range(1, max(0, num_seg - 1)):
            # Un tramo marcado como "reductor" nunca debe convertirse en quiebro.
            if self._is_reductor_segment(segments[i]):
                continue
            prev_seg = segments[i - 1].data
            cur_seg = segments[i].data
            next_seg = segments[i + 1].data
            d_rel_signed = _signed_angle_delta(cur_seg.angulo_xy, prev_seg.angulo_xy)
            d_rel = abs(d_rel_signed)
            back_to_base = _angle_delta(next_seg.angulo_xy, prev_seg.angulo_xy) <= 0.5
            if (
                d_rel > (QUIEBRO_MIN_ANGLE - QUIEBRO_ANGLE_EPS)
                and d_rel <= (QUIEBRO_MAX_ANGLE + QUIEBRO_ANGLE_EPS)
                and back_to_base
            ):
                is_quiebro_segment[i] = True
                _info = getattr(segments[i], "info", None)
                _diam = getattr(_info, "diameter", None) if _info is not None else None
                _incl_h = 90.0 - d_rel
                print(
                    "[ClimaPolyline] Quiebro2 detectado",
                    f"segment_idx={i}",
                    f"delta_rel={round(d_rel_signed, 4)}",
                    f"incl_h={round(_incl_h, 4)}",
                    f"back_to_base={back_to_base}",
                    f"diam={_diam}",
                )

        for i, seg_item in enumerate(segments):
            seg = seg_item.data
            v_unit = seg.vector_normalizado

            # 0) Segmento marcado como "reductor": convertir este tramo en pieza reductora.
            if (
                self._is_reductor_segment(seg_item)
                and self.reduccion_factory
                and 0 < i < (num_seg - 1)
            ):
                prev_item = segments[i - 1]
                next_item = segments[i + 1]
                d_prev = self._diameter_key(prev_item)
                d_next = self._diameter_key(next_item)
                if d_prev and d_next and d_prev != d_next and d_prev.lower() != "reductor" and d_next.lower() != "reductor":
                    len_axis = self._reduccion_axis_length_mm(seg, next_item.data)
                    reduccion_base = self.reduccion_factory(
                        prev_item,
                        next_item,
                        len_axis,
                    )
                    if reduccion_base is not None:
                        reduccion_models = (
                            list(reduccion_base)
                            if isinstance(reduccion_base, (list, tuple))
                            else [reduccion_base]
                        )
                        group_center = None
                        try:
                            group_center = self._get_center_from_vertices(
                                reduccion_models[0].GetGeometryObject()
                            )
                        except Exception:
                            group_center = None

                        # El segmento "reductor" puede quedar inclinado (línea roja interna)
                        # para transportar el nuevo centro de salida. Si centramos la pieza en
                        # ese segmento diagonal, el cuerpo completo se "corre de lado".
                        # Anclamos el reductor al eje principal (entrada/salida) usando el
                        # nodo de entrada + mitad de su longitud sobre la dirección de salida.
                        v_anchor = next_item.data.vector_normalizado
                        half_axis = float(len_axis) * 0.5
                        p_centro = AllplanGeo.Point3D(
                            seg.start.X + (v_anchor.X * half_axis),
                            seg.start.Y + (v_anchor.Y * half_axis),
                            seg.start.Z + (v_anchor.Z * half_axis),
                        )

                        for rm in reduccion_models:
                            if rm is None:
                                continue
                            element_reduccion = self._aplicar_transformacion(
                                rm,
                                seg,
                                elem_type="reduccion",
                                custom_position=p_centro,
                                next_seg=next_item.data,
                                local_center_override=group_center,
                            )
                            result_list.append({
                                "element": element_reduccion,
                                "element_type": "reduccion",
                                "index": element_index
                            })
                            element_index += 1

                        # No acumular corrimiento aquí: la polilínea ya se
                        # corrige aguas arriba en clima_polyline.py. Evita
                        # doble desplazamiento del tramo siguiente.
                        # Este tramo queda representado por el reductor.
                        continue

            if is_quiebro_segment[i]:
                quiebro_base = None
                if self.quiebro_factory and i > 0:
                    quiebro_base = self.quiebro_factory(segments[i - 1], seg_item)

                if quiebro_base is not None:
                    _prev_info = getattr(segments[i - 1], "info", None) if i > 0 else None
                    _prev_diam = getattr(_prev_info, "diameter", None) if _prev_info is not None else None
                    print(
                        "[ClimaPolyline] Generando quiebro",
                        f"segment_idx={i}",
                        f"diam_heredado={_prev_diam}",
                        f"length_input_mm={round(float(seg.longitud_3d), 3)}",
                        f"length_applied_mm={round(float(getattr(seg, 'quiebro_effective_length_mm', seg.longitud_3d)), 3)}",
                    )
                    p_centro = AllplanGeo.Point3D(
                        (seg.start.X + seg.end.X) / 2.0,
                        (seg.start.Y + seg.end.Y) / 2.0,
                        (seg.start.Z + seg.end.Z) / 2.0,
                    )
                    p_centro = AllplanGeo.Point3D(
                        p_centro.X + offset_x,
                        p_centro.Y + offset_y,
                        p_centro.Z + offset_z,
                    )
                    quiebro_models = (
                        list(quiebro_base)
                        if isinstance(quiebro_base, (list, tuple))
                        else [quiebro_base]
                    )
                    # Mantener una referencia local común del conjunto quiebro
                    # (cuerpo + hendiduras + flecha) para preservar su alineación
                    # relativa y evitar descentrados por centroide propio.
                    quiebro_group_center = None
                    try:
                        if quiebro_models and quiebro_models[0] is not None:
                            quiebro_group_center = self._get_center_from_vertices(
                                quiebro_models[0].GetGeometryObject()
                            )
                    except Exception:
                        quiebro_group_center = None
                    for qm in quiebro_models:
                        if qm is None:
                            continue
                        element_quiebro = self._aplicar_transformacion(
                            qm,
                            seg,
                            elem_type="quiebro",
                            custom_position=p_centro,
                            local_center_override=quiebro_group_center,
                        )
                        result_list.append({
                            "element": element_quiebro,
                            "element_type": "quiebro",
                            "index": element_index
                        })
                        element_index += 1
                    try:
                        if quiebro_group_center is not None:
                            print(
                                "[ClimaPolyline] Quiebro group center",
                                f"segment_idx={i}",
                                f"cx={round(float(quiebro_group_center.X), 4)}",
                                f"cy={round(float(quiebro_group_center.Y), 4)}",
                                f"cz={round(float(quiebro_group_center.Z), 4)}",
                            )
                    except Exception:
                        pass
                # Este segmento queda representado por quiebro; no generar conducto/codo.
                continue

            # 1. DETERMINAR RECORTES (Offsets)
            # -------------------------------------------------------
            offset_inicio = 0.0
            offset_final = 0.0

            if i > 0:
                prev_seg = segments[i-1].data
                # Si hay cambio de dirección (giro), recortamos para el codo
                if abs(AllplanGeo.Vector3D.DotProduct(prev_seg.vector_normalizado, v_unit)) < 0.01:
                    offset_inicio = self._codo_clearance_start_mm(seg_item)

            if i < num_seg - 1:
                next_seg = segments[i+1].data
                # Si el siguiente tramo es un giro, recortamos al final
                if abs(AllplanGeo.Vector3D.DotProduct(v_unit, next_seg.vector_normalizado)) < 0.01:
                    offset_final = self._codo_clearance_end_mm(seg_item)

            # 2. CONDUCTO — recortado para dejar hueco al codo
            # -------------------------------------------------------
            conducto_base = None
            use_factory_direct_length = False
            if self.conducto_factory:
                # Si la factoría acepta longitud objetivo, evitamos escalar el BREP
                # para no deformar detalles fijos como hendiduras/caps.
                try:
                    # Pasar SegmentItem (no SegmentData) para conservar info.diameter por tramo.
                    conducto_base = self.conducto_factory(seg_item, seg.longitud_3d)
                    use_factory_direct_length = True
                except TypeError:
                    conducto_base = self.conducto_factory(seg_item)
            else:
                conducto_base = self.templates.get(self.element_type_core)
            if conducto_base is not None:
                trim_in_mm, trim_out_mm = self._get_trim_in_out_mm(seg_item)
                longitud_recortada = (
                    seg.longitud_3d
                    - offset_inicio
                    - offset_final
                    - trim_in_mm
                    - trim_out_mm
                )

                if longitud_recortada > 0:
                    dist_al_centro = offset_inicio + trim_in_mm + (longitud_recortada / 2.0)
                    p_centro = AllplanGeo.Point3D(
                        seg.start.X + v_unit.X * dist_al_centro,
                        seg.start.Y + v_unit.Y * dist_al_centro,
                        seg.start.Z + v_unit.Z * dist_al_centro
                    )
                    p_centro = AllplanGeo.Point3D(
                        p_centro.X + offset_x,
                        p_centro.Y + offset_y,
                        p_centro.Z + offset_z,
                    )
                    if use_factory_direct_length:
                        # Re-generar con longitud recortada final (sin escalado geométrico).
                        try:
                            model_cond = self.conducto_factory(seg_item, longitud_recortada)
                        except TypeError:
                            model_cond = self.modificar_dimensiones_brep(conducto_base, longitud_recortada)
                    else:
                        model_cond = self.modificar_dimensiones_brep(conducto_base, longitud_recortada)

                    model_cond_list = (
                        list(model_cond)
                        if isinstance(model_cond, (list, tuple))
                        else [model_cond]
                    )
                    group_center = None
                    try:
                        if model_cond_list and model_cond_list[0] is not None:
                            group_center = self._get_center_from_vertices(
                                model_cond_list[0].GetGeometryObject()
                            )
                    except Exception:
                        group_center = None
                    if (
                        self.conducto_default_body_color is not None
                        and model_cond_list
                        and model_cond_list[0] is not None
                    ):
                        _body = model_cond_list[0]
                        _cp = _body.GetCommonProperties()
                        _cp.Color = int(self.conducto_default_body_color)
                        _body.SetCommonProperties(_cp)
                    if (
                        i == 0
                        and self.first_segment_conducto_color is not None
                        and model_cond_list
                        and model_cond_list[0] is not None
                    ):
                        _body = model_cond_list[0]
                        _cp = _body.GetCommonProperties()
                        _cp.Color = int(self.first_segment_conducto_color)
                        _body.SetCommonProperties(_cp)
                    if (
                        i == num_seg - 1
                        and self.last_segment_conducto_color is not None
                        and model_cond_list
                        and model_cond_list[0] is not None
                    ):
                        _body = model_cond_list[0]
                        _cp = _body.GetCommonProperties()
                        _cp.Color = int(self.last_segment_conducto_color)
                        _body.SetCommonProperties(_cp)
                    for mc_idx, mc in enumerate(model_cond_list):
                        if mc is None:
                            continue
                        element = self._aplicar_transformacion(
                            mc,
                            seg,
                            custom_position=p_centro,
                            local_center_override=group_center,
                        )
                        if (
                            i == 0
                            and mc_idx == 0
                            and self.first_segment_tapa_value
                            and self.attr_documents
                        ):
                            _merge_user_attribute_string(
                                element,
                                self.attr_documents,
                                "TAPA",
                                self.first_segment_tapa_value,
                                name_aliases=self.last_segment_tapa_attr_aliases,
                                id_fallback=self.last_segment_tapa_attr_id_fallback,
                            )
                        if (
                            i == num_seg - 1
                            and mc_idx == 0
                            and self.last_segment_tapa_value
                            and self.attr_documents
                        ):
                            _merge_user_attribute_string(
                                element,
                                self.attr_documents,
                                "TAPA",
                                self.last_segment_tapa_value,
                                name_aliases=self.last_segment_tapa_attr_aliases,
                                id_fallback=self.last_segment_tapa_attr_id_fallback,
                            )
                        result_list.append({
                            "element": element,
                            "element_type": self.element_type_core,
                            "index": element_index
                        })
                        element_index += 1

            # 3. CODO — en el vértice entre este segmento y el siguiente
            # -------------------------------------------------------
            if i < num_seg - 1:
                # Si alguno de los dos segmentos del vértice es quiebro, no crear codo.
                if is_quiebro_segment[i] or is_quiebro_segment[i + 1]:
                    continue
                # Si el vértice toca un tramo "reductor", no crear codo.
                # El tramo reductor puede quedar diagonal para transportar el
                # nuevo eje de salida y no debe interpretarse como giro de codo.
                if self._is_reductor_segment(segments[i]) or self._is_reductor_segment(segments[i + 1]):
                    continue
                next_seg = segments[i+1].data
                v1 = seg.vector_normalizado
                v2 = next_seg.vector_normalizado
                dot = AllplanGeo.Vector3D.DotProduct(v1, v2)
                pos_nodo = AllplanGeo.Point3D(
                    seg.end.X + offset_x,
                    seg.end.Y + offset_y,
                    seg.end.Z + offset_z,
                )

                # En Clima solo se permite codo para giros de 90°.
                # giros de 45° (u otros) deben resolverse con quiebro2.
                if abs(dot) <= CODO_PERP_DOT_TOL:
                    codo_base = (
                        self.codo_factory(seg_item, segments[i + 1]) if self.codo_factory
                        else self.templates.get("codo_90")
                    )
                    if codo_base is not None:
                        _info = getattr(segments[i], "info", None)
                        _diam = getattr(_info, "diameter", None) if _info is not None else None
                        codo_models = (
                            list(codo_base)
                            if isinstance(codo_base, (list, tuple))
                            else [codo_base]
                        )
                        codo_anchor_ref = None
                        try:
                            if codo_models and codo_models[0] is not None:
                                _err_a, _verts_a = codo_models[0].GetGeometryObject().GetVertices()
                                if _verts_a:
                                    codo_anchor_ref = min(
                                        _verts_a,
                                        key=lambda v: (v.X * v.X + v.Y * v.Y + v.Z * v.Z),
                                    )
                        except Exception:
                            codo_anchor_ref = None

                        transformed_codo_geos = []
                        for cm in codo_models:
                            if cm is None:
                                continue
                            element_codo = self._aplicar_transformacion(
                                cm,
                                seg,
                                elem_type="codo_90",
                                custom_position=pos_nodo,
                                next_seg=next_seg,
                                codo_diameter_key=_diam,
                                local_anchor_override=codo_anchor_ref,
                            )
                            result_list.append({
                                "element": element_codo,
                                "element_type": "codo_90",
                                "index": element_index
                            })
                            transformed_codo_geos.append(element_codo.GetGeometryObject())
                            element_index += 1

                        # Debug: verificar centrado relativo cuerpo/flecha tras transformación global.
                        try:
                            if transformed_codo_geos:
                                ref_c = self._get_center_from_vertices(transformed_codo_geos[0])
                                for g_idx, g in enumerate(transformed_codo_geos):
                                    cc = self._get_center_from_vertices(g)
                                    print(
                                        "[GeoHandler][CodoArrowDebug]"
                                        f" seg_idx={i}"
                                        f" part_idx={g_idx}"
                                        f" center=({cc.X:.3f},{cc.Y:.3f},{cc.Z:.3f})"
                                        f" delta_vs_body=({(cc.X-ref_c.X):.3f},{(cc.Y-ref_c.Y):.3f},{(cc.Z-ref_c.Z):.3f})"
                                    )
                        except Exception:
                            pass
                else:
                    # Tramo recto entre segmentos: inserción por vértice desactivable.
                    if self.reduccion_factory and self.enable_vertex_reducer:
                        reduccion_base = self.reduccion_factory(seg_item, segments[i + 1])
                        if reduccion_base is not None:
                            # Puede venir 1 elemento o una lista (cuerpo+flecha+línea guía).
                            reduccion_models = (
                                list(reduccion_base)
                                if isinstance(reduccion_base, (list, tuple))
                                else [reduccion_base]
                            )
                            # Mantener referencia común del conjunto usando el centro del cuerpo.
                            group_center = None
                            try:
                                group_center = self._get_center_from_vertices(
                                    reduccion_models[0].GetGeometryObject()
                                )
                            except Exception:
                                group_center = None

                            for rm in reduccion_models:
                                if rm is None:
                                    continue
                                element_reduccion = self._aplicar_transformacion(
                                    rm,
                                    seg,
                                    elem_type="reduccion",
                                    custom_position=pos_nodo,
                                    next_seg=next_seg,
                                    local_center_override=group_center,
                                )
                                result_list.append({
                                    "element": element_reduccion,
                                    "element_type": "reduccion",
                                    "index": element_index
                                })
                                element_index += 1

                            # Recentrar tramo(s) de salida: desplazar eje de polilínea
                            # hacia el centro de la boca de salida del reductor.
                            w_in = self._diameter_width_mm(seg_item)
                            w_out = self._diameter_width_mm(segments[i + 1])
                            if w_in > 0.0 and w_out > 0.0:
                                delta_mm = (w_in - w_out) * 0.5
                                # "Normal derecha" del tramo (coherente con yaw del reductor).
                                nx = v1.Y
                                ny = -v1.X
                                nz = 0.0
                                offset_x += nx * delta_mm
                                offset_y += ny * delta_mm
                                offset_z += nz * delta_mm

        return result_list

