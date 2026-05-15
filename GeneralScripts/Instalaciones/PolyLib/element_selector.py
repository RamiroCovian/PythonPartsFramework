"""
ElementSelector — Selector interactivo de elementos Allplan para el optimizador de caminos.

Gestiona tres tipos de elementos seleccionables por el usuario:

  · Techos IS   — sólidos 3D con atributo 1947 = "IS". Se extrae la cara superior
                  (vértices de mayor Z) y se genera un polígono de contorno.

  · Subdivisiones IS — sólidos con atributo 507 = "ISx". Se extrae su bbox superior
                       como zona de sub-división del techo.

  · Tubos IS    — líneas 3D con atributo 1947 = "IS-x". Se extraen sus endpoints
                  como segmentos de conducto existente.

  · Obstáculos  — sólidos 3D en capas de instalaciones (clima, saneamiento, ventilación).
                  Se detectan por ID de capa (LayerService), se obtiene su bbox completa
                  de 8 vértices y se exportan con modo "saltar". El ID se lee del
                  atributo 1083 del elemento.

El resultado acumulado queda en ScriptObject bajo las claves:
  techos_is, subdivisiones_is, tubos_is, obstaculos
"""

import math
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .interactor import PolylineInteractor

import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as PythonUtility
import NemAll_Python_IFW_ElementAdapter as AllplanAdapter

from NemAll_Python_BaseElements import LayerService


class ElementSelector:

    _TUB_IS_LAYER_NAME: str = "IS_TUB_EIX_SUPERIOR"

    _OBSTACLE_LAYER_NAMES: frozenset = frozenset({
        # Instalación de clima
        "IS_CON_CLIMA_FAB", "IS_AIG_CON_CLIMA_FAB",
        "IS_REJ_CON_CLIMA_FAB", "IS_REJ_AIG_CON_CLIMA_FAB",
        # Instalación de saneamiento
        "IS_CON_SANE_FAB", "IS_CON_SANE_OBR",
        # Ventilación y maquinaria
        "IS_CON_VENT_FAB", "IS_CON_VENT_OBR", "ELEMENTS",
    })

    def __init__(self, interactor: "PolylineInteractor") -> None:
        self._interactor = interactor

    # ------------------------------------------------------------------
    # Propiedad de conveniencia
    # ------------------------------------------------------------------
    @property
    def _so(self):
        """Acceso directo al ScriptObject (fuente de estado compartido)."""
        return self._interactor.script_object

    # ─────────────────────────────────────────────────────────────
    #  Activar / Desactivar
    # ─────────────────────────────────────────────────────────────
    def activar(self) -> None:
        """Limpia el preview y arranca StartElementSelect en Allplan."""
        self._so.selector_preview_elems = []
        self._iniciar_seleccion()

    def desactivar(self) -> bool:
        """Cancela la selección activa eliminando la función de input del stack de Allplan."""
        self._so.post_element_selection = None
        try:
            AllplanIFW.InputFunctionStarter.RemoveFunction()
        except Exception as e:
            print(f"[ElementSelector] Error al desactivar el selector de elementos: {e}")

        return True
    # ─────────────────────────────────────────────────────────────
    #  Selection
    # ─────────────────────────────────────────────────────────────
    def _iniciar_seleccion(self) -> None:
        """Registra un nuevo PostElementSelection y lanza StartElementSelect."""
        self._so.selector_preview_elems = []
        element_filter = AllplanIFW.ElementSelectFilterSetting(True)
        self._so.post_element_selection = AllplanIFW.PostElementSelection()
        AllplanIFW.InputFunctionStarter.StartElementSelect(
            "Seleccionar multiples elementos",
            element_filter,
            self._so.post_element_selection,
            True,
            AllplanIFW.SelectionMode.eSelectSubObject,
        )

    def run_selection_logic(self) -> bool:
        """
        Ejecuta la lógica de extracción de datos de los elementos seleccionados.
        Retorna True si procesó algo, False si no había selección.
        """
        if self._so.post_element_selection is None:
            return True

        selected = self._so.post_element_selection.GetSelectedElements(self._so.doc)
        if not selected:
            return True

        attr_id_techo_tubo = 1947  # "IS" → techo solid ; "IS-x" / "ISx" → tubos Line3D
        attr_id_sub = 507           # "ISx" → subdivisiones sólidos

        self._so.techos_is = []
        self._so.subdivisiones_is = []
        self._so.tubos_is = []
        self._so.obstaculos = []

        techo_groups: List[List] = []  # un grupo por cada sólido IS → un techo independiente
        techo_ids: set = set()    # ids de elems ya clasificados como techo (guard obstaculos)
        subdiv_ids: set = set()   # ids de elems ya clasificados como subdivisión (guard obstaculos)
        tubos_groups: dict = {}   # normalized_is_id → [elems]
        subdiv_groups: dict = {}  # is_id → [elems]

        # Resolver ID de capa IS_TUB_EIX_SUPERIOR una sola vez
        tubo_is_layer_id = None
        try:
            lid = LayerService.GetIDByShortName(self._TUB_IS_LAYER_NAME, self._so.doc)
            if lid is not None and lid >= 0:
                tubo_is_layer_id = lid
        except Exception as ex:
            print(f"[ElementSelector] Error resolviendo capa {self._TUB_IS_LAYER_NAME}: {ex}")

        # ── Clasificación de elementos seleccionados (única pasada) ──────
        # Tubos IS  : capa IS_TUB_EIX_SUPERIOR + attr_id_techo_tubo presente
        # Techos IS : attr_id_techo_tubo == "IS" (sin numero de grupo)
        # Subdiv    : attr_id_sub startswith "IS"
        # Obstaculos: capa en _OBSTACLE_LAYER_NAMES
        layer_id_cache = self._build_layer_id_cache()
        draw_buf: List = []
        changed = False

        for elem in selected:
            val_tt = self._get_IS_attr_value(elem, attr_id_techo_tubo)
            if val_tt is not None:
                upper_tt = val_tt.upper()
                if upper_tt == "IS":
                    techo_groups.append([elem])
                    techo_ids.add(id(elem))

            val_sub = self._get_IS_attr_value(elem, attr_id_sub)
            if val_sub is not None and val_sub.upper().startswith("IS"):
                subdiv_groups.setdefault(val_sub, []).append(elem)
                subdiv_ids.add(id(elem))

            if tubo_is_layer_id is not None:
                try:
                    if elem.GetCommonProperties().Layer == tubo_is_layer_id:
                        val_tt = self._get_IS_attr_value(elem, attr_id_techo_tubo)
                        if val_tt is not None:
                            norm_id = val_tt.upper().replace("-", "")
                            tubos_groups.setdefault(norm_id, []).append(elem)
                        continue
                except Exception:
                    pass

            if id(elem) not in techo_ids and id(elem) not in subdiv_ids and self._is_obstacle_element(elem, layer_id_cache):
                obs = self._extract_obstaculo(elem, layer_id_cache, draw_buf)
                if obs:
                    self._so.obstaculos.append(obs)
                    changed = True
                continue

        # Excluir de subdiv_groups cualquier elemento que ya este en tubos_groups
        tubos_elems_set = {id(e) for elems in tubos_groups.values() for e in elems}
        subdiv_groups = {
            k: [e for e in v if id(e) not in tubos_elems_set]
            for k, v in subdiv_groups.items()
            if any(id(e) not in tubos_elems_set for e in v)
        }

        # ── Generar Techos IS ─────────────────────────────────────────────
        for elems in techo_groups:
            techo_idx = len(self._so.techos_is) + 1
            techo = self._extract_techo_bbox(elems, draw_buf)
            if techo:
                techo['id'] = f"techo_auto_{techo_idx}"
                self._so.techos_is.append(techo)
                changed = True
                print(f"[ElementSelector] Techo '{techo['id']}' acumulado. Total: {len(self._so.techos_is)}")

        # ── Generar Subdivisiones IS ──────────────────────────────────────
        for is_id, elems in subdiv_groups.items():
            subdiv = self._extract_subdivision_bbox(is_id, elems, draw_buf)
            if subdiv:
                self._so.subdivisiones_is.append(subdiv)
                changed = True
        print(f"[ElementSelector] Subdivisión acumulada. Total: {len(self._so.subdivisiones_is)}")

        # ── Generar Tubos IS ──────────────────────────────────────────────
        for is_id, elems in tubos_groups.items():
            nuevos = self._extract_tubos(is_id, elems, draw_buf)
            if nuevos:
                self._so.tubos_is.extend(nuevos)
                changed = True
        print(f"[ElementSelector] Tubo(s) acumulados. Total: {len(self._so.tubos_is)}")

        if changed:
            self._iniciar_seleccion()
            # 1. Asignar el nuevo preview con los elementos recién detectados
            self._so.selector_preview_elems = draw_buf if draw_buf else []
            # 2. Mostrar diálogo
            PythonUtility.ShowMessageBox(
                f"Elementos detectados.\n\n"
                f"Techos IS:        {len(self._so.techos_is)}\n"
                f"Subdivisiones IS: {len(self._so.subdivisiones_is)}\n"
                f"Tubos IS:         {len(self._so.tubos_is)}\n"
                f"Obstáculos:       {len(self._so.obstaculos)}",
                PythonUtility.MB_OK,
            )
            return True
        else:
            PythonUtility.ShowMessageBox(f"Error al guardar elementos:\n", PythonUtility.MB_OK)
            return False

    # ─────────────────────────────────────────────────────────────
    #  Attribute filtering
    # ─────────────────────────────────────────────────────────────

    def _get_IS_attr_value(self, elem: AllplanAdapter.BaseElementAdapter, attr_id: int) -> Optional[str]:
        """Retorna el valor string del atributo attr_id, o None si no existe."""
        if attr_id <= 0:
            return None
        try:
            for attr in elem.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAll):
                if attr[0] == attr_id:
                    return str(attr[1]).strip()
        except Exception as ex:
            print(f"[ElementSelector] Error leyendo atributo {attr_id}: {ex}")
        return None

    def _is_IS_solid(self, elem, attr_id: int) -> bool:
        """Devuelve True si el elemento tiene el atributo attr_id con algún valor."""
        val = self._get_IS_attr_value(elem, attr_id)
        return val is not None and val != ""

    def _extract_subdivision_bbox(self, is_id: str, elems: List, draw_buf: List) -> Optional[dict]:
        """
        Vértices de la CARA SUPERIOR de la subdivisión IS con sus Z reales.
        Mismo algoritmo que _extract_techo_bbox: GetModelGeometry() directo +
        agrupación XY para obtener el vértice superior real de cada esquina.
        """
        try:
            all_verts = []
            _GEO_DIRECT = {"Polyhedron3D", "BRep3D", "Line3D", "Polyline3D"}
            for elem in elems:
                model_geo = None
                try:
                    model_geo = elem.GetModelGeometry()
                except Exception:
                    pass
                if model_geo is not None:
                    if type(model_geo).__name__ in _GEO_DIRECT:
                        # Polyhedron3D devuelto directamente
                        all_verts.extend(self._get_vertices_from_geo(model_geo))
                    else:
                        # Lista/colección de geometrías
                        try:
                            for item in model_geo:
                                all_verts.extend(self._get_vertices_from_geo(item))
                        except TypeError:
                            all_verts.extend(self._get_vertices_from_geo(model_geo))
                else:
                    geo = None
                    for method_name in ("GetGeometryObject", "GetGeometry"):
                        fn = getattr(elem, method_name, None)
                        if fn is not None:
                            geo = fn()
                            if geo is not None:
                                break
                    if geo is not None:
                        all_verts.extend(self._get_vertices_from_geo(geo))

            if not all_verts:
                print(f"[ElementSelector] Subdivisión '{is_id}': sin vértices.")
                return None

            # Agrupación XY → vértice superior real de cada esquina
            xy_tol = 50.0
            xy_groups: List = []
            for v in all_verts:
                placed = False
                for g in xy_groups:
                    if abs(v.X - g[0].X) < xy_tol and abs(v.Y - g[0].Y) < xy_tol:
                        g.append(v)
                        placed = True
                        break
                if not placed:
                    xy_groups.append([v])

            top_verts = [max(g, key=lambda v: v.Z) for g in xy_groups]

            # Bbox de las 4 esquinas con Z real del vértice más cercano de la cara superior
            min_x = min(v.X for v in top_verts)
            max_x = max(v.X for v in top_verts)
            min_y = min(v.Y for v in top_verts)
            max_y = max(v.Y for v in top_verts)

            def nearest_z(x, y):
                return min(top_verts, key=lambda v: (v.X - x) ** 2 + (v.Y - y) ** 2).Z

            corners = [
                AllplanGeo.Point3D(min_x, min_y, nearest_z(min_x, min_y)),
                AllplanGeo.Point3D(max_x, min_y, nearest_z(max_x, min_y)),
                AllplanGeo.Point3D(max_x, max_y, nearest_z(max_x, max_y)),
                AllplanGeo.Point3D(min_x, max_y, nearest_z(min_x, max_y)),
            ]
            vertices = [
                {"x": round(p.X, 10), "y": round(p.Y, 10), "z": round(p.Z, 1)}
                for p in corners
            ]

            # print(
            #     f"[ElementSelector] Subdivisión '{is_id}': "
            #     f"bbox ({min_x:.1f},{min_y:.1f}) - ({max_x:.1f},{max_y:.1f})"
            # )
            self._crear_perimetro_en_documento(corners, draw_buf, z_offset=50, pen=5, color=6)
            return {"id": is_id, "vertices": vertices}

        except Exception as ex:
            print(f"[ElementSelector] Error en _extract_subdivision_bbox ('{is_id}'): {ex}")
            return None

    def _extract_techo_bbox(self, elements: List, draw_buf: List) -> Optional[dict]:
        """
        Extrae los vértices de la CARA SUPERIOR del techo con sus Z reales.
        GetModelGeometry() devuelve el Polyhedron3D directamente (no iterar).
        Para superficies inclinadas: agrupa por proximidad XY y toma el vértice
        con mayor Z de cada grupo (= cara superior) preservando la inclinación.
        """
        try:
            all_verts = []
            for elem in elements:
                model_geo = None
                try:
                    model_geo = elem.GetModelGeometry()
                except Exception:
                    pass
                if model_geo is not None:
                    # GetModelGeometry devuelve el Polyhedron3D directamente — no iterar
                    all_verts.extend(self._get_vertices_from_geo(model_geo))
                else:
                    geo = None
                    for method_name in ("GetGeometryObject", "GetGeometry"):
                        fn = getattr(elem, method_name, None)
                        if fn is not None:
                            geo = fn()
                            if geo is not None:
                                break
                    if geo is not None:
                        all_verts.extend(self._get_vertices_from_geo(geo))

            if not all_verts:
                print("[ElementSelector] Techo: sin vértices.")
                return None

            # Cara superior: para cada esquina XY existen 2 vértices (cara inf y sup).
            # Agrupamos por proximidad XY y tomamos el de max Z → Z real de la cara superior.
            xy_tol = 50.0  # mm — tolerancia para agrupar la misma esquina XY
            xy_groups: List = []
            for v in all_verts:
                placed = False
                for g in xy_groups:
                    if abs(v.X - g[0].X) < xy_tol and abs(v.Y - g[0].Y) < xy_tol:
                        g.append(v)
                        placed = True
                        break
                if not placed:
                    xy_groups.append([v])

            top_verts = [max(g, key=lambda v: v.Z) for g in xy_groups]

            # Ordenar CCW en plano XY
            cx = sum(v.X for v in top_verts) / len(top_verts)
            cy = sum(v.Y for v in top_verts) / len(top_verts)
            top_verts.sort(key=lambda v: math.atan2(v.Y - cy, v.X - cx))

            vertices = [
                {"x": round(v.X, 10), "y": round(v.Y, 10), "z": round(v.Z, 1)}
                for v in top_verts
            ]

            techo_id = "techo_principal" if not self._so.techos_is else f"techo_{len(self._so.techos_is) + 1}"
            # print(
            #     f"[ElementSelector] Techo '{techo_id}': "
            #     f"{len(top_verts)} vértice(s) cara superior"
            # )
            self._dibujar_superficie_techo(top_verts, draw_buf)
            return {"id": techo_id, "vertices": vertices}

        except Exception as ex:
            print(f"[ElementSelector] Error en _extract_techo_bbox: {ex}")
            return None

    def _dibujar_superficie_techo(self, corners: List, draw_buf: List) -> None:
        """Añade el perímetro del techo al buffer (cyan, pluma 2)."""
        self._crear_perimetro_en_documento(corners, draw_buf, z_offset=30, pen=2, color=4)

    def _extract_tubos(self, is_id: str, elems: List, draw_buf: List) -> List[dict]:
        """Extrae tubos IS y acumula sus líneas en draw_buf."""
        tubos = []
        for elem in elems:
            pts = self._get_line_endpoints(elem)
            if pts is None:
                continue
            inicio, fin = pts
            t_id = f"T{len(self._so.tubos_is) + len(tubos) + 1}"
            tubos.append({
                "id": t_id,
                "is_id": is_id,
                "punto_inicio": {
                    "x": round(inicio.X, 10),
                    "y": round(inicio.Y, 10),
                    "z": round(inicio.Z, 1),
                },
                "punto_fin": {
                    "x": round(fin.X, 10),
                    "y": round(fin.Y, 10),
                    "z": round(fin.Z, 1),
                },
            })
            self._dibujar_tubo_en_documento(inicio, fin, draw_buf)
        return tubos

    def _dibujar_tubo_en_documento(
        self, inicio: AllplanGeo.Point3D, fin: AllplanGeo.Point3D, draw_buf: List
    ) -> None:
        """Añade un tubo IS como línea al buffer (verde, pluma 2)."""
        try:
            props = AllplanBaseElements.CommonProperties()
            props.Color = 3  # verde
            props.Layer = 0
            props.Pen = 2
            line = AllplanGeo.Line3D(inicio, fin)
            draw_buf.append(AllplanBasisElements.ModelElement3D(props, line))
        except Exception as ex:
            print(f"[ElementSelector] _dibujar_tubo_en_documento: {ex}")

    def _get_line_endpoints(self, elem) -> Optional[tuple]:
        """Devuelve (StartPoint, EndPoint) del Line3D del elemento (o sus sub-geometrías)."""
        try:
            model_geo = None
            try:
                model_geo = elem.GetModelGeometry()
            except Exception:
                pass

            if model_geo is not None:
                if type(model_geo).__name__ == "Line3D":
                    return (model_geo.StartPoint, model_geo.EndPoint)
                # Intentar iterar si es una colección
                try:
                    for item in model_geo:
                        if type(item).__name__ == "Line3D":
                            return (item.StartPoint, item.EndPoint)
                except TypeError:
                    pass

            # Fallback: geometría directa
            geo = None
            for method_name in ("GetGeometryObject", "GetGeometry"):
                fn = getattr(elem, method_name, None)
                if fn is not None:
                    geo = fn()
                    if geo is not None:
                        break
            if geo is not None:
                if type(geo).__name__ == "Line3D":
                    return (geo.StartPoint, geo.EndPoint)
                endpoints = self._get_segment_endpoints(elem)
                if endpoints:
                    return (endpoints[0], endpoints[1])

            print(f"[ElementSelector] _get_line_endpoints: sin Line3D en {type(elem).__name__}")
            return None

        except Exception as ex:
            print(f"[ElementSelector] Error en _get_line_endpoints: {ex}")
            return None

    # ─────────────────────────────────────────────────────────────
    #  Geometry extraction — grupo de 4 elementos
    # ─────────────────────────────────────────────────────────────

    def _extract_techo_from_four(self, elements: List) -> Optional[dict]:
        """
        Dado un grupo de 4 elementos IS (2 horizontales + 2 verticales) que forman
        el perímetro de un techo, calcula las 4 esquinas como intersección de sus ejes.

        Algoritmo:
        1. Cada elemento aporta 2 endpoints → clasificar como H (eje X) o V (eje Y).
        2. Los 2 segmentos H contribuyen un Y fijo cada uno.
        3. Los 2 segmentos V contribuyen un X fijo cada uno.
        4. Las 4 esquinas = combinaciones (X_v0,Y_h0), (X_v0,Y_h1), (X_v1,Y_h0), (X_v1,Y_h1).
        5. Ordenar CCW y dibujar preview.
        """
        try:
            x_coords = []  # de segmentos con eje principal Y (verticales)
            y_coords = []  # de segmentos con eje principal X (horizontales)
            z_vals = []

            for i, elem in enumerate(elements):
                pts = self._get_segment_endpoints(elem)
                if not pts:
                    print(f"[ElementSelector] Elemento {i+1}/4 sin endpoints válidos, se ignora el grupo.")
                    return None
                ep1, ep2 = pts
                print(
                    f"[ElementSelector] Elem {i+1}: "
                    f"ep1=({ep1.X:.1f}, {ep1.Y:.1f}, {ep1.Z:.1f})  "
                    f"ep2=({ep2.X:.1f}, {ep2.Y:.1f}, {ep2.Z:.1f})"
                )
                dx = abs(ep2.X - ep1.X)
                dy = abs(ep2.Y - ep1.Y)
                z_vals += [ep1.Z, ep2.Z]

                if dx >= dy:
                    # segmento horizontal → eje X → Y es la coordenada fija
                    y_coords.append((ep1.Y + ep2.Y) / 2.0)
                else:
                    # segmento vertical → eje Y → X es la coordenada fija
                    x_coords.append((ep1.X + ep2.X) / 2.0)

            if len(x_coords) != 2 or len(y_coords) != 2:
                msg = (
                    f"Se esperaban 2 segmentos horizontales y 2 verticales.\n"
                    f"Detectados: {len(y_coords)} H  y  {len(x_coords)} V.\n\n"
                    "Verifique que los 4 elementos formen un perímetro rectangular."
                )
                print(f"[ElementSelector] {msg}")
                PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
                return None

            z_avg = sum(z_vals) / len(z_vals)

            # 4 esquinas = producto cartesiano X × Y
            corners = [
                AllplanGeo.Point3D(x, y, z_avg)
                for x in x_coords
                for y in y_coords
            ]

            # Ordenar CCW en plano XY
            cx = sum(p.X for p in corners) / 4
            cy = sum(p.Y for p in corners) / 4
            corners.sort(key=lambda p: math.atan2(p.Y - cy, p.X - cx))

            techo_id = "techo_principal" if not self._so.techos_is else f"techo_{len(self._so.techos_is) + 1}"
            vertices = [
                {"x": round(p.X, 10), "y": round(p.Y, 10), "z": round(p.Z, 1)}
                for p in corners
            ]

            print(f"[ElementSelector] Techo '{techo_id}': {[f'({p.X:.1f},{p.Y:.1f})' for p in corners]}")

            local_buf: List = []
            self._crear_perimetro_en_documento(corners, local_buf)
            if local_buf:
                self._so.selector_preview_elems = list(local_buf)

            return {"id": techo_id, "vertices": vertices}

        except Exception as ex:
            print(f"[ElementSelector] Error extrayendo techo de 4 elementos: {ex}")
            return None

    def _get_vertices_from_geo(self, geo) -> List:
        """
        Extrae vértices Point3D de distintos tipos de geometría Allplan.

        Tipos soportados:
          - Polyhedron3D : GetVertices() → secuencia de Point3D (world coords)
                           Fallback: GetVertex(i) for i in range(GetVerticesCount())
          - BRep3D       : GetVertices() → (error_code, [Point3D])
          - Line3D       : StartPoint / EndPoint
          - Polyline3D   : Points iterable
          - Otros        : intenta GetVertices() con ambas firmas
        """
        geo_type = type(geo).__name__
        try:
            if geo_type == "Polyhedron3D":
                # GetVertices() devuelve la secuencia de vértices directamente
                raw = geo.GetVertices()
                if raw and not isinstance(raw, tuple):
                    verts = list(raw)
                    if verts and hasattr(verts[0], "X"):
                        return verts
                # Fallback: iterar con GetVertex / GetVerticesCount
                count = geo.GetVerticesCount()
                return [geo.GetVertex(i) for i in range(count)]

            elif geo_type == "BRep3D":
                result = geo.GetVertices()
                # GetVertices puede retornar (err, [Point3D]) o directamente [Point3D]
                verts = result[1] if isinstance(result, tuple) and len(result) > 1 else result
                return list(verts) if verts else []

            elif geo_type == "Line3D":
                return [geo.StartPoint, geo.EndPoint]

            elif geo_type == "Polyline3D":
                pts = geo.Points
                n = pts.Count() if hasattr(pts, 'Count') else len(pts)
                return [pts[i] for i in range(n)]

            else:
                # Fallback genérico: prueba ambas firmas de GetVertices()
                raw = geo.GetVertices()
                if isinstance(raw, tuple) and len(raw) > 1:
                    return list(raw[1])
                return list(raw) if raw else []

        except Exception as ex:
            print(f"[ElementSelector] _get_vertices_from_geo ({geo_type}): {ex}")
            return []

    def _get_segment_endpoints(self, elem) -> List:
        """
        Para un elemento 3D del perímetro del techo, retorna sus 2 puntos extremos
        a lo largo del eje de mayor extensión del sólido.

        Divide los vértices en el tercio inicial y final del eje principal
        y promedia cada grupo para obtener un endpoint representativo por extremo.
        Soporta Polyhedron3D, BRep3D, Line3D y Polyline3D.
        """
        try:
            # Obtener objeto de geometría del elemento Allplan
            geo = None
            for method_name in ("GetGeometryObject", "GetGeometry"):
                fn = getattr(elem, method_name, None)
                if fn is not None:
                    geo = fn()
                    if geo is not None:
                        print(f"[ElementSelector] Geometría via {method_name}(): {type(geo).__name__}")
                        break

            if geo is None:
                print(f"[ElementSelector] Sin geometría — elem: {type(elem).__name__}")
                return []

            verts = self._get_vertices_from_geo(geo)
            print(f"[ElementSelector] Vértices obtenidos: {len(verts)}")
            if not verts:
                return []

            min_x = min(v.X for v in verts)
            max_x = max(v.X for v in verts)
            min_y = min(v.Y for v in verts)
            max_y = max(v.Y for v in verts)
            min_z = min(v.Z for v in verts)
            max_z = max(v.Z for v in verts)

            dx = max_x - min_x
            dy = max_y - min_y
            dz = max_z - min_z

            print(f"[ElementSelector] BBox — dx={dx:.1f}  dy={dy:.1f}  dz={dz:.1f}")

            # Eje principal = el de mayor extensión
            if dx >= dy and dx >= dz:
                boundary = dx * 0.3
                end_a = [v for v in verts if v.X <= min_x + boundary]
                end_b = [v for v in verts if v.X >= max_x - boundary]
                print(f"[ElementSelector] Eje X — inicio:{len(end_a)} fin:{len(end_b)}")
            elif dy >= dx and dy >= dz:
                boundary = dy * 0.3
                end_a = [v for v in verts if v.Y <= min_y + boundary]
                end_b = [v for v in verts if v.Y >= max_y - boundary]
                print(f"[ElementSelector] Eje Y — inicio:{len(end_a)} fin:{len(end_b)}")
            else:
                boundary = dz * 0.3
                end_a = [v for v in verts if v.Z <= min_z + boundary]
                end_b = [v for v in verts if v.Z >= max_z - boundary]
                print(f"[ElementSelector] Eje Z — inicio:{len(end_a)} fin:{len(end_b)}")

            if not end_a or not end_b:
                return []

            def centroid(pts):
                return AllplanGeo.Point3D(
                    sum(p.X for p in pts) / len(pts),
                    sum(p.Y for p in pts) / len(pts),
                    sum(p.Z for p in pts) / len(pts),
                )

            return [centroid(end_a), centroid(end_b)]

        except Exception as ex:
            print(f"[ElementSelector] Error en _get_segment_endpoints: {ex}")
            return []

    # ─────────────────────────────────────────────────────────────
    #  Obstacle detection
    # ─────────────────────────────────────────────────────────────

    def _build_layer_id_cache(self) -> dict:
        """Devuelve {layer_id: layer_name} para todas las capas de obstáculos definidas."""
        cache = {}
        for name in self._OBSTACLE_LAYER_NAMES:
            try:
                layer_id = LayerService.GetIDByShortName(name, self._so.doc)
                if layer_id is not None and layer_id >= 0:
                    cache[layer_id] = name
            except Exception as ex:
                print(f"[ElementSelector] _build_layer_id_cache — capa '{name}': {ex}")
        return cache

    def _is_obstacle_element(self, elem, layer_id_cache: dict) -> bool:
        """Devuelve True si el elemento pertenece a una de las capas de obstáculos."""
        try:
            props = elem.GetCommonProperties()
            return props.Layer in layer_id_cache
        except Exception:
            return False

    def _get_all_verts_from_elem(self, elem) -> List:
        """Extrae todos los vértices Point3D de un elemento Allplan."""
        _GEO_DIRECT = {"Polyhedron3D", "BRep3D", "Line3D", "Polyline3D"}
        all_verts = []
        model_geo = None
        try:
            model_geo = elem.GetModelGeometry()
        except Exception:
            pass

        if model_geo is not None:
            if type(model_geo).__name__ in _GEO_DIRECT:
                all_verts.extend(self._get_vertices_from_geo(model_geo))
            else:
                try:
                    for item in model_geo:
                        all_verts.extend(self._get_vertices_from_geo(item))
                except TypeError:
                    all_verts.extend(self._get_vertices_from_geo(model_geo))

        # Fallback siempre activo: si GetModelGeometry no devolvió nada útil
        # (None o BRep3D con vértices vacíos), intentar GetGeometryObject/GetGeometry.
        if not all_verts:
            for method_name in ("GetGeometryObject", "GetGeometry"):
                fn = getattr(elem, method_name, None)
                if fn is not None:
                    try:
                        geo = fn()
                        if geo is not None:
                            all_verts.extend(self._get_vertices_from_geo(geo))
                            if all_verts:
                                break
                    except Exception:
                        pass

        return all_verts

    def _extract_obstaculo(self, elem, layer_id_cache: dict, draw_buf: List) -> Optional[dict]:
        """Extrae un obstáculo 3D con todos sus vértices reales y Z preservadas."""
        try:
            elem_id = self._get_IS_attr_value(elem, 1083)
            if not elem_id:
                elem_id = f"OBS_{id(elem)}"

            _3D_SOLID = {"Polyhedron3D", "BRep3D"}
            all_verts: List = []
            solid_geos: List = []   # geometrías para dibujar

            # 1. GetModelGeometry — solo tipos 3D sólidos
            model_geo = None
            try:
                model_geo = elem.GetModelGeometry()
            except Exception:
                pass

            if model_geo is not None:
                geo_type = type(model_geo).__name__
                if geo_type in _3D_SOLID:
                    all_verts.extend(self._get_vertices_from_geo(model_geo))
                    solid_geos.append(model_geo)
                else:
                    try:
                        for item in model_geo:
                            if type(item).__name__ in _3D_SOLID:
                                all_verts.extend(self._get_vertices_from_geo(item))
                                solid_geos.append(item)
                    except TypeError:
                        pass

            # 2. Fallback: GetGeometryObject / GetGeometry
            if not all_verts:
                for method_name in ("GetGeometryObject", "GetGeometry"):
                    fn = getattr(elem, method_name, None)
                    if fn is not None:
                        try:
                            geo = fn()
                            if geo is not None and type(geo).__name__ in _3D_SOLID:
                                all_verts.extend(self._get_vertices_from_geo(geo))
                                solid_geos.append(geo)
                                if all_verts:
                                    break
                        except Exception:
                            pass

            if not all_verts:
                return None

            # Todos los vértices reales con sus Z preservadas (sin aproximar bbox)
            vertices = [
                {"x": round(v.X, 1), "y": round(v.Y, 1), "z": round(v.Z, 1)}
                for v in all_verts
            ]

            cx = sum(v.X for v in all_verts) / len(all_verts)
            cy = sum(v.Y for v in all_verts) / len(all_verts)
            layer_name = layer_id_cache.get(elem.GetCommonProperties().Layer, "desconocida")

            self._dibujar_obstaculo_preview(solid_geos, draw_buf)

            return {
                "id": elem_id,
                "vertices": vertices,
                "modo": ["saltar"],
                "descripcion": f"Obstáculo '{elem_id}' en capa {layer_name}, centrado en ({cx:.0f}, {cy:.0f})",
            }
        except Exception as ex:
            print(f"[ElementSelector] Error en _extract_obstaculo: {ex}")
            return None

    def _dibujar_obstaculo_preview(self, solid_geos: List, draw_buf: List) -> None:
        """Dibuja los obstáculos como ModelElement3D de su geometría real (igual que element_list)."""
        try:
            props = AllplanBaseElements.CommonProperties()
            props.Color = 5   # naranja
            props.Layer = 0
            props.Pen = 3
            props.ColorByLayer  = False
            props.PenByLayer    = False
            for geo in solid_geos:
                draw_buf.append(AllplanBasisElements.ModelElement3D(props, geo))
        except Exception as ex:
            print(f"[ElementSelector] _dibujar_obstaculo_preview: {ex}")

    def _crear_perimetro_en_documento(
        self, corners: List, draw_buf: List,
        z_offset: float = 0.0, pen: int = 1, color: int = 6
    ) -> None:
        """Añade las líneas del perímetro al buffer draw_buf (sin llamar a CreateElements)."""
        try:
            props = AllplanBaseElements.CommonProperties()
            props.Color = color
            props.Layer = 0
            props.Pen = pen

            draw_corners = (
                [AllplanGeo.Point3D(p.X, p.Y, p.Z + z_offset) for p in corners]
                if z_offset != 0.0 else corners
            )

            n = len(draw_corners)
            for i in range(n):
                line = AllplanGeo.Line3D(draw_corners[i], draw_corners[(i + 1) % n])
                draw_buf.append(AllplanBasisElements.ModelElement3D(props, line))
        except Exception as ex:
            print(f"[ElementSelector] _crear_perimetro_en_documento: {ex}")

