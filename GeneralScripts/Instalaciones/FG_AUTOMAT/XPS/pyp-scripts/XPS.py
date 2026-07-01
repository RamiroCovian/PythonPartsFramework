import NemAll_Python_Utility as PythonUtility
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
from NemAll_Python_Geometry import Vector3D  # para normales y utilidades
from NemAll_Python_Geometry import PolyhedronUtil  # puntos de cara (2025+)
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
import NemAll_Python_AllplanSettings as AllplanSettings
import subprocess
import os
from GeneralScripts.BaseScriptObject import BaseScriptObject, BaseScriptObjectData  # base del contrato
from GeneralScripts.CreateElementResult import CreateElementResult                   # wrapper del resultado
from ScriptObjectInteractors.MultiElementSelectInteractor import (
    MultiElementSelectInteractor,
    MultiElementSelectInteractorResult,
)
from TypeCollections import ModelEleList, Curve3DList
import math
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from PythonPartUtil import PythonPartUtil
from BuildingElementAttributeList import BuildingElementAttributeList
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import random

def install_packages(package):
    prg_path = AllplanSettings.AllplanPaths.GetPrgPath() + "\\"

    target_dir = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
    print("target_dir ETC: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )

    target_dir = (
        f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
    )
    print("target_dir USR: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )

try:
    import numpy as np
except ImportError:
    install_packages("numpy")
    print("instalando paquetes: numpy")
    import numpy as np



SIZES_ATTRIBUTE = 1083
XPS_LAYER = "XPS_TEST"
XPS_LAYER_MENSULA = "XPS_MENSULA_TEST"

EDGE_ATTRIBUTE = 1083
WALL_ID_ATTRIBUTE = 1084

PMP_FG_AILLANT = 2569
PMP_FG_XPS_SUP = 2570
PMP_FG_PIR_SUP = 2571
PMP_FG_MENSULA = 2572
PMP_FG_MEN_SUP = 2573


VAL_PMP_FG_AILLANT = "XPS-12345"
VAL_PMP_FG_XPS_SUP = 30.5
VAL_PMP_FG_PIR_SUP = 0.0
VAL_PMP_FG_MENSULA = "SI"
VAL_PMP_FG_MEN_SUP = 15.2


SELECTION = 0
PREVIEW = 1


def check_allplan_version(build_ele, version):
    return True

def create_element(build_ele, doc):
    return ([], [])

def create_script_object(build_ele: BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    """Creation of the script object (Allplan 2025 ScriptObject)"""
    return XpsScriptObject(build_ele, script_object_data)

class XpsScriptObject(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        # 1) inicializa la base y guarda el building element (acceso a parámetros)
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.element_list = []
        self.preview_faces = []
        self.elements = []
        self.element_drawed = False
        self.state = SELECTION

        self.build_ele.INPUT_PMP_FG_AILLANT.value = VAL_PMP_FG_AILLANT
        self.build_ele.INPUT_PMP_FG_XPS_SUP.value = VAL_PMP_FG_XPS_SUP
        self.build_ele.INPUT_PMP_FG_PIR_SUP.value = VAL_PMP_FG_PIR_SUP
        self.build_ele.INPUT_PMP_FG_MENSULA.value = VAL_PMP_FG_MENSULA
        self.build_ele.INPUT_PMP_FG_MEN_SUP.value = VAL_PMP_FG_MEN_SUP

        self.val_pmp_fg_aillant = self.build_ele.INPUT_PMP_FG_AILLANT.value
        self.val_pmp_fg_xps_sup = self.build_ele.INPUT_PMP_FG_XPS_SUP.value
        self.val_pmp_fg_pir_sup = self.build_ele.INPUT_PMP_FG_PIR_SUP.value
        self.val_pmp_fg_mensula = self.build_ele.INPUT_PMP_FG_MENSULA.value
        self.val_pmp_fg_men_sup = self.build_ele.INPUT_PMP_FG_MEN_SUP.value



        self.avoid: list[AllplanEleAdapter.BaseElementAdapter] = []
        # 2) prepara el contenedor del resultado de la selección múltiple
        #    (la propia doc recomienda definirlo en el constructor)
        self.selection_result = MultiElementSelectInteractorResult()

        # 3) cualquier estado previo de tu implementación (caches, etc.)
        #    ej.: self._cached_props = None


    def start_input(self):
        """ start the input
        """
        self.state = SELECTION
        self.script_object_interactor = MultiElementSelectInteractor(
            self.selection_result,
            prompt_msg="Selecciona los elementos"  # mensaje UX en la línea de diálogo
        )

        # Recupera la selección hecha por el usuario (lista de adaptadores)
        # Si en el futuro usas filtros, pásalos aquí con `selection_filter=...`
    # --- Entrada de datos (paso interactivo opcional) ---

    def start_next_input(self):
        """
        Es llamado cuando termina la interacción actual.
        Si no hay más pasos, anula el interactor.
        """
        selected_elements: AllplanEleAdapter.BaseElementAdapterList = getattr(self.selection_result, "sel_elements", [])
        self.state = PREVIEW

        try:
            self.process_selection(selected_elements)

            self.script_object_interactor = None

        except Exception as e:
            PythonUtility.ShowMessageBox(f"Error al procesar GUIDs: {e}", PythonUtility.MB_OK)
            return None

    def process_selection(self, selected_elements):
        self.preview_faces = []

        self.element_list = selected_elements
        if not self.element_list:
            return

        if self.element_list:
            elements = self.filter_elements(self.element_list)
            # self.debug_element_types(elements)

            # Filtrar objetos a evitar
            self.avoid = self.filter_avoid_objects(elements)

            if self.build_ele.do_walls.value == 1:
                # Filtrar los muros
                walls = self.filter_walls(elements)
                markers = self.filter_recess_markers(elements)
                pairs = self.assign_markers_to_walls_3d(walls, markers, tol_z=30.0, tol_xy=400.0, unique=True)
                self.debug_pairs(pairs)

                self.preview_walls(pairs)

            if self.build_ele.do_mensules.value == 1:
                mensules = self.filter_mensules(elements)
                self.preview_mensules(mensules)

            # --- FIN DEBUG LIGERO ---
            # anula el interactor actual

    def preview_walls(self, pairs):
        # --- NUEVO: calcular caras XPS y previsualizarlas ---
        self.preview_faces = self.compute_xps_faces_and_preview(pairs)
        lines = []
        for i, (_wall, face_idx, pts) in enumerate(self.preview_faces, 1):
            if not pts:
                continue
            lines.append(f"Cara {i} (idx={face_idx}) - {len(pts)} puntos")
            for j, p in enumerate(pts):
                lines.append(f"  P{j}: ({p.X:.1f}, {p.Y:.1f}, {p.Z:.1f})")
                if j >= 9:          # limita a 10 puntos por cara para que no explote el popup
                    lines.append("  ...")
                    break

    def preview_mensules(self, mensules: AllplanEleAdapter.BaseElementAdapterList):
        for men in mensules:
            geometries = men.GetModelGeometry()

            for geom in geometries:
                if isinstance(geom, AllplanGeo.Polyhedron3D):
                    faces = self.get_faces_from_polyhedron(geom, None, bounding=False)
                    # {
                    #     'idx': face_group[max_area_idx]['idx'],  # Guardamos un índice de referencia
                    #     'normal': normal,
                    #     'pts': corner_points,  # Solo los 4 puntos de las esquinas
                    #     'area': area
                    # }
                    for face in faces:
                        self.preview_faces.append((men, face['idx'], face['pts']))


            print("MENSULA")
        return

    # --- Creación de elementos ---
    def modify_element_property(self, page: int, name: str) -> bool:

        if self.state == SELECTION:
            return True

        elif self.state == PREVIEW:
            self.process_selection(self.element_list)

        return True


    def execute(self) -> CreateElementResult:
        """
        Crea los elementos del PythonPart.
        Se invoca repetidamente mientras no haya interactor activo.
        """
        # Acceso al documento actual heredado de BaseScriptObject
        doc = self.document

        self.build_ele.z_unique.value = random.random() * 3600

        if self.preview_faces:
        # if self.preview_faces and not self.element_drawed:
            # show_xps = bool(self.build_ele.ShowXPS.value)
            # if show_xps:
            #     self.elements = self._build_xps_model_elements(self.preview_faces)
            # else:
            #     self.elements = self._build_preview_face_elems(self.preview_faces, offset_mm=2.0, thickness_mm=5.0)

            if self.build_ele.do_walls.value == 1:
                offset_mm=45
                thickness_mm= 120

            else:
                offset_mm=0
                thickness_mm= 40

            thickness_mm= float(self.build_ele.XPSGruix.value)
            self.elements = self._build_xps_model_elements(self.preview_faces, offset_mm=offset_mm, thickness_mm=thickness_mm)
            # self.elements = self._build_preview_face_elems(self.preview_faces, offset_mm=2.0, thickness_mm=5.0)
            # self.element_drawed = True

            return CreateElementResult(elements=self.elements,
                                placement_point = AllplanGeo.Point3D()
                                )


        return CreateElementResult()


    def debug_element_types(self, elements):
        """Muestra los tipos de los elementos seleccionados para depuración."""
        type_info = []
        for elem in elements:
            try:
                type_name = elem.GetElementAdapterType().GetTypeName() if hasattr(elem.GetElementAdapterType(), "GetTypeName") else "Tipo desconocido"
                type_info.append(f"→ Tipo: {type_name}")
            except Exception as e:
                type_info.append(f"Error obteniendo tipo: {str(e)}")

        # Mostrar tipos en bloques de 20 líneas
        block_size = 20
        total = len(type_info)
        for i in range(0, total, block_size):
            chunk = type_info[i:i+block_size]
            header = f"Tipos relevantes ({i+1}-{min(i+block_size, total)} de {total}):"
            PythonUtility.ShowMessageBox(header + "\n" + "\n".join(chunk), PythonUtility.MB_OK)

    def filter_avoid_objects(self, elements) -> list[AllplanEleAdapter.BaseElementAdapter]:
        obj = []
        for elem in elements:
            try:
                type_name = elem.GetElementAdapterType().GetTypeName() if hasattr(elem.GetElementAdapterType(), "GetTypeName") else ""
                if "Volume3D" in type_name:
                    attributes = elem.GetAttributes(
                        AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
                    )
                    filtered_attribute = [
                        x
                        for x in attributes
                        if x[0] == 1083 and x[1] is not None and x[1] != "" and x[1] == "EVITAR"
                    ]
                    if len(filtered_attribute) > 0:
                        obj.append(elem)

            except Exception as e:
                pass  # Si hay error, lo ignora (podrías loguear si te interesa)
        return obj

    def filter_walls(self, elements):
        """Filtra los elementos seleccionados para obtener solo los muros por tipo."""
        walls = []
        for elem in elements:
            try:
                type_name = elem.GetElementAdapterType().GetTypeName() if hasattr(elem.GetElementAdapterType(), "GetTypeName") else ""
                if "WallTier" in type_name:
                    walls.append(elem)
            except Exception as e:
                pass  # Si hay error, lo ignora (podrías loguear si te interesa)
        return walls

    def filter_mensules(self, elements: AllplanEleAdapter.BaseElementAdapterList):
        mensules = []
        for elem in elements:
            try:
                type_name = elem.GetElementAdapterType().GetTypeName() if hasattr(elem.GetElementAdapterType(), "GetTypeName") else ""
                if "RecessSmartSymbol" in type_name:
                    attributes = elem.GetAttributes(
                        AllplanBaseElements.eAttibuteReadState.ReadAllAndComputable
                    )
                    filtered_attribute = [
                        x
                        for x in attributes
                        if x[0] == 507 and x[1] is not None and x[1] != "" and x[1] == "MACROMEN"
                    ]
                    if len(filtered_attribute) > 0:
                        mensules.append(elem)

            except Exception as e:
                pass  # Si hay error, lo ignora (podrías loguear si te interesa)

        return mensules


    def filter_elements(self, elements: AllplanEleAdapter.BaseElementAdapterList):
        """
        Filters out elements with unwanted types.
        Returns a list containing only elements whose type is NOT in the excluded types list.
        """
        excluded_types = [
            "AttributeContainer_TypeUUID",
            "Line3D_TypeUUID",
            "GeneralVariableTextBlock_TypeUUID",
            "GeneralVariableText_TypeUUID",
            "ExtendedElement_TypeUUID",
            "PlanePairArea_TypeUUID"
        ]
        filtered_elements = []
        for elem in elements:
            try:
                type_name = elem.GetElementAdapterType().GetTypeName() if hasattr(elem.GetElementAdapterType(), "GetTypeName") else ""
                if type_name not in excluded_types:
                    filtered_elements.append(elem)
            except Exception:
                pass  # Optionally log errors here if needed
        return filtered_elements

    def filter_recess_markers(self, elements: AllplanEleAdapter.BaseElementAdapterList):
        """Filtra RecessTier en layers PANELV/PANELH."""
        markers = []
        for elem in elements:
            type_name = elem.GetElementAdapterType().GetTypeName()
            if "RecessTier" not in type_name:
                continue

            attrs = AllplanBaseElements.ElementsAttributeService.GetAttributes(elem)

            is_triangule = any(
                ((getattr(a, "Id", a[0]) == 2103 or getattr(a, "Id", a[0]) == 55001) and str(getattr(a, "Value", a[1])) == "XMOLDE")
                for a in attrs
            )

            # attrs es lista de (id, valor) según doc
            if is_triangule:
                markers.append(elem)
        return markers

    # ------------------------------
    # Paso 2: emparejar triángulo (DEN=XMOLDE) → muro (versión 3D)
    # ------------------------------

    def _get_model_geometry(self, adapter):
        """Geo del modelo (cae a GetGeometry si no está disponible)."""
        try:
            return adapter.GetModelGeometry()
        except Exception:
            return adapter.GetGeometry()


    def get_wall_floor_point(self, wall_adapter, z_eps=2.0):
        """
        Punto 3D del PISO del muro (coords del proyecto):
        - Z = Zmín de los vértices del Polyhedron3D
        - X,Y = centroide de los vértices con Z≈Zmín (± z_eps)
        """
        geo = self._get_model_geometry(wall_adapter)
        if not isinstance(geo, AllplanGeo.Polyhedron3D):
            return None

        try:
            verts = list(geo.GetVertices())
        except Exception:
            return None
        if not verts:
            return None

        zmin = min(v.Z for v in verts)
        floor_verts = [v for v in verts if abs(v.Z - zmin) <= z_eps]
        use = floor_verts if floor_verts else verts  # fallback raro

        cx = sum(p.X for p in use) / len(use)
        cy = sum(p.Y for p in use) / len(use)
        return AllplanGeo.Point3D(cx, cy, zmin)


    def get_marker_point3d(self, marker_adapter):
        """
        Centro 3D del RecessTier (Polyline2D):
        - XY: centro de la polilínea (ignorando punto de cierre duplicado).
        - Z : piso del MURO más cercano en XY (el triángulo siempre apoya en el piso).
        Devuelve: (Point3D, has_z=True) para que el emparejamiento use 3D.
        """
        # 1) Tomar la Polyline2D del marker
        try:
            geo = marker_adapter.GetModelGeometry()
        except Exception:
            geo = marker_adapter.GetGeometry()

        pl2d = None
        if isinstance(geo, AllplanGeo.Polyline2D):
            pl2d = geo
        elif isinstance(geo, (list, tuple)):
            for g in geo:
                if isinstance(g, AllplanGeo.Polyline2D):
                    pl2d = g
                    break
        if pl2d is None:
            return None  # no es un triángulo 2D válido

        # 2) Centro XY de la polilínea (evita contar dos veces el punto de cierre)
        n = pl2d.Count()
        if n == 0:
            return None
        try:
            p0 = pl2d.GetStartPoint()
            pL = pl2d.GetLastPoint()
            count = n - 1 if (abs(pL.X - p0.X) < 1e-6 and abs(pL.Y - p0.Y) < 1e-6) else n
        except Exception:
            count = n

        sx = sy = 0.0
        for i in range(count):
            pi = pl2d.GetPoint(i)
            sx += float(pi.X)
            sy += float(pi.Y)
        cx = sx / float(count)
        cy = sy / float(count)

        # 3) Z = piso del muro más cercano en XY
        best_z = None
        best_d2 = float("inf")
        try:
            walls_in_sel = self.filter_walls(self.element_list)
        except Exception:
            walls_in_sel = []

        for w in walls_in_sel:
            wp = self.get_wall_floor_point(w)
            if not wp:
                continue
            dx = float(wp.X) - cx
            dy = float(wp.Y) - cy
            d2 = dx*dx + dy*dy
            if d2 < best_d2:
                best_d2 = d2
                best_z = float(wp.Z)

        if best_z is None:
            best_z = 0.0  # último recurso si no hay muros válidos

        return AllplanGeo.Point3D(cx, cy, best_z), True



    def assign_markers_to_walls_3d(self, wall_adapters, marker_adapters,
                                tol_z=30.0, tol_xy=400.0, unique=True):
        """
        Empareja Recess ↔ Muro.

        - Si el Recess trae Z (3D): usa distancia 3D con filtros |ΔZ|<=tol_z y distXY<=tol_xy.
        - Si el Recess es 2D: puntúa solo por XY (distXY<=tol_xy).
        Luego (si unique=True) hace asignación 1–a–1 greedy para repartir en apilados.
        """
        # 1) pisos de muros
        walls = []
        for w in wall_adapters:
            wp = self.get_wall_floor_point(w)
            if wp:
                walls.append((w, wp))
        if not walls:
            return {}

        # 2) candidatos (score, marker, wall)
        candidates = []
        for m in marker_adapters:
            res = self.get_marker_point3d(m)
            if not res:
                continue
            mp, has_z = res

            local_added = False
            for w, wp in walls:
                dx, dy = (wp.X - mp.X), (wp.Y - mp.Y)
                dxy2 = dx*dx + dy*dy
                if dxy2 > tol_xy * tol_xy:
                    continue

                if has_z:
                    dz = mp.Z - wp.Z
                    if abs(dz) > tol_z:
                        continue
                    d2 = dxy2 + dz*dz
                else:
                    d2 = dxy2  # 2D: comparamos solo XY

                candidates.append((d2, m, w))
                local_added = True

            # si el marcador no pasó tolerancias, lo ponemos con todos (mejor fallback)
            if not local_added:
                for w, wp in walls:
                    dx, dy = (wp.X - mp.X), (wp.Y - mp.Y)
                    dxy2 = dx*dx + dy*dy
                    d2 = dxy2 + ((mp.Z - wp.Z)**2 if has_z else 0.0)
                    candidates.append((d2, m, w))

        if not candidates:
            return {}

        # 3) asignación
        pairs = {}
        if unique:
            # 1–a–1: greedy por menor score
            candidates.sort(key=lambda t: t[0])
            used_m = set()
            used_w = set()
            for _, m, w in candidates:
                if m in used_m or w in used_w:
                    continue
                pairs[m] = w
                used_m.add(m); used_w.add(w)
        else:
            # mejor muro por marker (varios markers pueden caer en el mismo muro)
            best = {}
            for d2, m, w in candidates:
                if (m not in best) or (d2 < best[m][0]):
                    best[m] = (d2, w)
            pairs = {m: w for m, (_, w) in best.items()}

        return pairs

    def debug_pairs(self, marker_to_wall):
        """Muestra una lista legible de emparejamientos triángulo→muro."""
        lines = []
        for index, (marker, wall) in enumerate(marker_to_wall.items(), 1):
            try:
                marker_type = marker.GetElementAdapterType().GetTypeName()
                wall_type = wall.GetElementAdapterType().GetTypeName()
                lines.append(f"{index:02d}  marker={marker_type}  →  wall={wall_type}")
            except Exception as exc:
                lines.append(f"{index:02d}  ERROR: {exc}")
        if lines:
            PythonUtility.ShowMessageBox("Emparejamientos triángulo→muro:\n" + "\n".join(lines[:40]), PythonUtility.MB_OK)
    # ------------------------------
    # UTILIDADES para caras de muros (XPS)
    def _get_wall_polyhedron(self, wall_adapter) -> AllplanGeo.Polyhedron3D | None:
        geo = self._get_model_geometry(wall_adapter)
        if isinstance(geo, AllplanGeo.Polyhedron3D):
            return geo
        if isinstance(geo, (list, tuple)):
            for g in geo:
                if isinstance(g, AllplanGeo.Polyhedron3D):
                    return g
        return None

    def _get_face_points(self, poly, face_index):
        """Intenta ambas variantes de PolyhedronUtil.GetFacePoints."""
        pts = []
        try:
            pts = PolyhedronUtil.GetFacePoints(poly, face_index)  # variante (poly, idx)
        except Exception:
            try:
                face = poly.GetFace(face_index)                   # a veces viene envuelto
                pts = PolyhedronUtil.GetFacePoints(poly, face)          # variante (face)
            except Exception:
                pts = []
        return self._as_point3_list(pts)

    def _face_info_list(self, wall_adapter, z_vertical_tol=5):
        poly = self._get_wall_polyhedron(wall_adapter)
        return self.get_faces_from_polyhedron(poly, z_vertical_tol)

    def get_faces_from_polyhedron(self, poly: AllplanGeo.Polyhedron3D | None, z_vertical_tol, bounding = True):
        if poly is None or not poly.IsValid():
            return []

        try:
            face_count = poly.GetFacesCount()
        except Exception:
            # fallback si la API devuelve tupla
            fc = poly.GetFacesCount()
            face_count = fc[1] if isinstance(fc, tuple) else fc

        # Primero agrupamos todas las caras por su vector normal
        normal_groups = {}
        for i in range(face_count):
            nv = None
            try:
                nv = poly.GetNormalVectorOfFace(i)
            except Exception:
                continue
            normal = self._as_vec3(nv)
            if normal is None:
                continue

            # vertical = normal ~ horizontal (Z casi 0)
            if z_vertical_tol is not None and abs(normal.Z) >= z_vertical_tol:
                continue

            # Crear clave de grupo basada en el vector normal (redondeado para evitar errores numéricos)
            key = (round(normal.X, 3), round(normal.Y, 3), round(normal.Z, 3))
            if key not in normal_groups:
                normal_groups[key] = []

            pts = self._get_face_points(poly, i)
            if len(pts) < 3:
                continue

            normal_groups[key].append({
                'idx': i,
                'normal': normal,
                'pts': pts
            })

        faces = []
        if bounding:
            # Ahora procesamos cada grupo para construir caras completas
            for normal_key, face_group in normal_groups.items():
                if not face_group:
                    continue

                # Usamos la normal del primer elemento del grupo
                normal = face_group[0]['normal']

                # Obtenemos todos los puntos de todas las caras en este grupo
                all_points = []
                for face in face_group:
                    all_points.extend(face['pts'])

                if not all_points:
                    continue

                # NUEVA LÓGICA: Extraer solo los 4 puntos extremos (las esquinas)
                # Encontrar los límites mínimos y máximos en cada eje
                min_x = min(p.X for p in all_points)
                max_x = max(p.X for p in all_points)
                min_y = min(p.Y for p in all_points)
                max_y = max(p.Y for p in all_points)
                min_z = min(p.Z for p in all_points)
                max_z = max(p.Z for p in all_points)

                # Crear los 4 puntos de las esquinas (ajustados al plano)
                # La normal nos ayuda a determinar qué coordenada es constante
                nx, ny, nz = abs(normal.X), abs(normal.Y), abs(normal.Z)
                corner_points = []

                if nx > ny and nx > nz:  # La normal apunta principalmente en X
                    # La cara está en un plano YZ
                    x_val = all_points[0].X  # Usamos X del primer punto
                    corner_points = [
                        AllplanGeo.Point3D(x_val, min_y, min_z),
                        AllplanGeo.Point3D(x_val, max_y, min_z),
                        AllplanGeo.Point3D(x_val, max_y, max_z),
                        AllplanGeo.Point3D(x_val, min_y, max_z)
                    ]
                elif ny > nx and ny > nz:  # La normal apunta principalmente en Y
                    # La cara está en un plano XZ
                    y_val = all_points[0].Y  # Usamos Y del primer punto
                    corner_points = [
                        AllplanGeo.Point3D(min_x, y_val, min_z),
                        AllplanGeo.Point3D(max_x, y_val, min_z),
                        AllplanGeo.Point3D(max_x, y_val, max_z),
                        AllplanGeo.Point3D(min_x, y_val, max_z)
                    ]
                else:  # La normal apunta principalmente en Z
                    # La cara está en un plano XY
                    z_val = all_points[0].Z  # Usamos Z del primer punto
                    corner_points = [
                        AllplanGeo.Point3D(min_x, min_y, z_val),
                        AllplanGeo.Point3D(max_x, min_y, z_val),
                        AllplanGeo.Point3D(max_x, max_y, z_val),
                        AllplanGeo.Point3D(min_x, max_y, z_val)
                    ]

                # Calculamos el área usando los 4 puntos de las esquinas
                area = self._polygon_area3d(corner_points, normal)

                # Usamos el índice de la cara con más área como referencia
                max_area_idx = max(range(len(face_group)),
                                key=lambda i: self._polygon_area3d(face_group[i]['pts'], normal))

                faces.append({
                    'idx': face_group[max_area_idx]['idx'],  # Guardamos un índice de referencia
                    'normal': normal,
                    'pts': corner_points,  # Solo los 4 puntos de las esquinas
                    'area': area
                })

        else:
            for normal_key, face_group in normal_groups.items():
                if not face_group:
                    continue

                # Usamos la normal del primer elemento del grupo
                normal = face_group[0]['normal']

                # Obtenemos todos los puntos de todas las caras en este grupo
                all_points = []
                for face in face_group:
                    all_points.extend(face['pts'])

                if not all_points:
                    continue

                points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in all_points]

                # Calculamos el área usando los 4 puntos de las esquinas
                area = self._polygon_area3d(points, normal)

                # Usamos el índice de la cara con más área como referencia
                max_area_idx = max(range(len(face_group)),
                                key=lambda i: self._polygon_area3d(face_group[i]['pts'], normal))

                faces.append({
                    'idx': face_group[max_area_idx]['idx'],  # Guardamos un índice de referencia
                    'normal': normal,
                    'pts': points,  # Solo los 4 puntos de las esquinas
                    'area': area
                })

        # Ordenamos por área (mayor primero)
        faces.sort(key=lambda f: f['area'], reverse=True)
        return faces


    def _polygon_area3d(self, pts, approx_normal=None):
        """Área de un polígono plano en 3D (proyecc. a plano dominante)."""
        if len(pts) < 3:
            return 0.0
        # normal aproximada
        if approx_normal is None:
            v1 = AllplanGeo.Vector3D(pts[1].X - pts[0].X, pts[1].Y - pts[0].Y, pts[1].Z - pts[0].Z)
            v2 = AllplanGeo.Vector3D(pts[2].X - pts[0].X, pts[2].Y - pts[0].Y, pts[2].Z - pts[0].Z)
            n  = AllplanGeo.Vector3D.CrossProduct(v1, v2)
        else:
            n  = approx_normal

        ax, ay, az = abs(n.X), abs(n.Y), abs(n.Z)

        def area2d(seq):
            a = 0.0
            for i in range(len(seq)):
                x1, y1 = seq[i]
                x2, y2 = seq[(i+1) % len(seq)]
                a += (x1*y2 - x2*y1)
            return abs(a) * 0.5

        if ax >= ay and ax >= az:
            # proyectar en YZ
            seq = [(p.Y, p.Z) for p in pts]
        elif ay >= ax and ay >= az:
            # proyectar en XZ
            seq = [(p.X, p.Z) for p in pts]
        else:
            # proyectar en XY
            seq = [(p.X, p.Y) for p in pts]
        return area2d(seq)

    # ------------------------------
    # UTIL: vector “punta” del triángulo (en XY)
    # ------------------------------
    def _triangle_tip_vector_xy(self, marker_adapter):
        try:
            geo = marker_adapter.GetModelGeometry()
        except Exception:
            geo = marker_adapter.GetGeometry()

        pl2d = None
        if isinstance(geo, AllplanGeo.Polyline2D):
            pl2d = geo
        elif isinstance(geo, (list, tuple)):
            for g in geo:
                if isinstance(g, AllplanGeo.Polyline2D):
                    pl2d = g; break
        if pl2d is None:
            return None

        pts = self._as_point2_list(pl2d)
        if len(pts) < 3:
            return None

        # base = par más alejado (O(n^2), pts son pocos)
        import itertools, math
        def d2(a,b): return (a.X-b.X)*(a.X-b.X) + (a.Y-b.Y)*(a.Y-b.Y)
        pairs = [ (d2(pts[i], pts[j]), i, j) for i,j in itertools.combinations(range(len(pts)), 2) ]
        pairs.sort(reverse=True)
        _, iA, iB = pairs[0]
        A, B = pts[iA], pts[iB]

        # tip = punto con mayor distancia perpendicular a la recta AB
        def dist_line_sq(P, A, B):
            ux, uy = (B.X-A.X, B.Y-A.Y)
            vx, vy = (P.X-A.X, P.Y-A.Y)
            num = abs(ux*vy - uy*vx)
            den = (ux*ux + uy*uy) ** 0.5 or 1.0
            return (num/den)**2
        tip_idx = max((k for k in range(len(pts)) if k not in (iA, iB)),
                    key=lambda k: dist_line_sq(pts[k], A, B))
        tip = pts[tip_idx]

        mid = AllplanGeo.Point2D( (A.X+B.X)*0.5, (A.Y+B.Y)*0.5 )
        vx, vy = (tip.X - mid.X), (tip.Y - mid.Y)
        L = (vx*vx + vy*vy) ** 0.5
        if L < 1e-6:
            return None
        return AllplanGeo.Vector3D(vx/L, vy/L, 0.0)


    # ------------------------------
    # Selección de cara "de atrás" y PREVIEW
    # ------------------------------
    def _pick_back_face(self, wall_adapter, marker_adapter):
        """Devuelve (face_index, face_pts) de la cara opuesta a la punta del triángulo."""
        faces = self._face_info_list(wall_adapter)
        if not faces:
            return None

        # si hay muchas verticales, nos quedamos con las dos mayores
        candidates = faces[:2] if len(faces) >= 2 else faces

        v_tip = self._triangle_tip_vector_xy(marker_adapter)
        if v_tip is None:
            # si no hay triángulo válido, como fallback: cara vertical de mayor área
            f = candidates[0]
            return (f['idx'], f['pts'])

        # proyectar normales a XY y comparar con v_tip (queremos la más "opuesta" => dot mínimo)
        def norm_xy(v):
            vx, vy = v.X, v.Y
            l = (vx*vx + vy*vy) ** 0.5
            if l < 1e-9:
                return (0.0, 0.0)
            return (vx/l, vy/l)

        vtx, vty = v_tip.X, v_tip.Y  # ya está normalizado
        best = None
        best_dot = 1e9
        for f in candidates:
            nx, ny = norm_xy(f['normal'])
            dot = nx*vtx + ny*vty
            if dot < best_dot:
                best_dot = dot
                best = f

        if best is None:
            best = candidates[0]
        return (best['idx'], best['pts'])

    def compute_xps_faces_and_preview(self, marker_to_wall):
        """
        Para cada par marker→wall devuelve una lista de (wall_adapter, face_idx, face_pts).
        Si un muro tiene varios markers, pueden repetirse; lo depuramos por (wall, face_idx).
        """
        raw = []
        for marker, wall in marker_to_wall.items():
            res = self._pick_back_face(wall, marker)
            if res is None:
                continue
            face_idx, face_pts = res
            raw.append( (wall, face_idx, face_pts) )

        # quitar duplicados por muro + cara
        unique = {}
        for wall, idx, pts in raw:
            key = (wall, idx)
            if key not in unique:
                unique[key] = (wall, idx, pts)
        return list(unique.values())

    def _build_preview_face_elems(self, preview_faces, *, offset_mm: float = 2.0, thickness_mm: float = 5.0):
        """
        De cada cara (wall, face_id, [Point3D...]) crea un sólido fino (ExtrudedAreaSolid3D)
        en ROJO, desplazado 'offset_mm' fuera del muro y con espesor 'thickness_mm'.
        Devuelve: list[ModelElement3D]
        """
        model_ele_list = ModelEleList()

        # Propiedades rojas (forzadas) para la previsualización
        com = AllplanBaseElements.CommonProperties()
        com.Color = 1
        com.ColorByLayer = False
        com.ForceColor = True
        com.Pen = 7
        com.Stroke = 1

        for element, face_id, pts in preview_faces:
            if not pts or len(pts) < 3:
                continue

            # 1) Normal geométrica con cross product que SÍ retorna vector nuevo
            p0 = pts[0]
            n = None
            for i in range(1, len(pts) - 1):
                v1 = AllplanGeo.Vector3D(); v1.Set(p0, pts[i])
                v2 = AllplanGeo.Vector3D(); v2.Set(p0, pts[i + 1])
                cr = v1 * v2                    # Va x Vb -> Vector3D nuevo
                if not cr.IsZero():
                    cr.Normalize()              # normal unitaria
                    n = cr
                    break
            if n is None:
                n = AllplanGeo.Vector3D(0.0, 0.0, 1.0)

            # 2) Alinear con la normal "oficial" de la cara del muro (si está disponible)
            try:
                poly_geom = element.GetModelGeometry()                         # geometría del muro
                ok, face_n = poly_geom.GetNormalVectorOfFace(int(face_id))  # normal de la cara
                if ok and not face_n.IsZero():
                    # Si apuntan en sentido opuesto, invierte
                    if (n.X * face_n.X + n.Y * face_n.Y + n.Z * face_n.Z) < 0.0:
                        n = AllplanGeo.Vector3D(-n.X, -n.Y, -n.Z)
            except Exception:
                pass

            # 3) Construir el polígono base de la cara
            poly = AllplanGeo.Polygon3D()
            for p in pts:
                poly += AllplanGeo.Point3D(p.X, p.Y, p.Z)
            # Cerrar si hace falta
            if pts[0] != pts[-1]:
                poly += AllplanGeo.Point3D(pts[0].X, pts[0].Y, pts[0].Z)

            # Validar polígono (evita extrusiones inválidas)
            # (GetPlane / IsValid según API de Polygon3D)
            if hasattr(poly, "IsValid") and not poly.IsValid():
                continue

            # 4) Área poligonal para la extrusión
            area = AllplanGeo.PolygonalArea3D()
            area += poly  # el área puede tener 1+ polígonos (huecos), aquí 1

            # 5) Crear ExtrudedAreaSolid3D: espesor hacia la normal exterior
            solid = AllplanGeo.ExtrudedAreaSolid3D()
            solid.SetExtrudedArea(area)
            solid.SetDirection(AllplanGeo.Vector3D(n.X * thickness_mm, n.Y * thickness_mm, n.Z * thickness_mm))

            # 6) Separar del muro un poco (offset) para que no se superponga
            if offset_mm > 0.0:
                solid = AllplanGeo.Move(solid, AllplanGeo.Vector3D(n.X * offset_mm, n.Y * offset_mm, n.Z * offset_mm))

            # 7) Añadir el sólido fino al resultado con propiedades rojas
            model_ele_list.append_geometry_3d(solid, com)

        # Devolver como lista de ModelElement3D
        return model_ele_list


    def _build_xps_model_elements(self, preview_faces, *, offset_mm: float = 2.0, thickness_mm: float = 5.0) -> ModelEleList:
        """Devuelve los elementos de XPS. Si ShowXPS está destildado, los pinta en rojo."""

        # 2) Preparar la lista de elementos y las propiedades base
        """
        De cada cara (wall, face_id, [Point3D...]) crea un sólido fino (ExtrudedAreaSolid3D)
        en ROJO, desplazado 'offset_mm' fuera del muro y con espesor 'thickness_mm'.
        Devuelve: list[ModelElement3D]
        """
        xps_ele_list = []
        line_ele_list = []

        for element, face_id, pts in preview_faces:
            if not pts or len(pts) < 3:
                continue

            # 1) Normal geométrica con cross product que SÍ retorna vector nuevo
            p0 = pts[0]
            n = None
            for i in range(1, len(pts) - 1):
                v1 = AllplanGeo.Vector3D(); v1.Set(p0, pts[i])
                v2 = AllplanGeo.Vector3D(); v2.Set(p0, pts[i + 1])
                cr = v1 * v2                    # Va x Vb -> Vector3D nuevo
                if not cr.IsZero():
                    cr.Normalize()              # normal unitaria
                    n = cr
                    break
            if n is None:
                n = AllplanGeo.Vector3D(0.0, 0.0, 1.0)

            # 2) Alinear con la normal "oficial" de la cara del muro (si está disponible)
            try:
                poly_geom = element.GetModelGeometry()                         # geometría del muro
                ok, face_n = poly_geom.GetNormalVectorOfFace(int(face_id))  # normal de la cara
                if ok and not face_n.IsZero():
                    # Si apuntan en sentido opuesto, invierte
                    if (n.X * face_n.X + n.Y * face_n.Y + n.Z * face_n.Z) < 0.0:
                        n = AllplanGeo.Vector3D(-n.X, -n.Y, -n.Z)
            except Exception:
                pass

            elems = self.create_multiple_panels(n, pts, offset_mm= offset_mm, thickness_mm= thickness_mm)
            for elem in elems:
                xps_ele_list.append(elem)


            if self.build_ele.do_walls.value == 1:
                points_array = [(p.X, p.Y, p.Z) for p in pts]
                puntos = np.array(points_array)
                max_x = np.max(puntos[:, 0])
                min_x = np.min(puntos[:, 0])
                max_y = np.max(puntos[:, 1])
                min_y = np.min(puntos[:, 1])
                max_z = np.max(puntos[:, 2])
                min_z = np.min(puntos[:, 2])

                min_pt = AllplanGeo.Point3D(min_x + (thickness_mm * 2 * n.X), min_y + (thickness_mm * 2 * n.Y), min_z + (thickness_mm * 2 * n.Z))
                # n_line = AllplanGeo.Line3D(min_pt, AllplanGeo.Point3D(min_pt.X + (100 * n.X), min_pt.Y + (100 * n.Y), min_pt.Z + (100 * n.Z)))
                # line_ele_list.append(n_line)
                perp_n = AllplanGeo.Vector3D(-n.Y, n.X, n.Z)
                perp_line = AllplanGeo.Line3D(min_pt, AllplanGeo.Point3D(min_pt.X + ((max_x - min_x) * perp_n.X), min_pt.Y + ((max_y - min_y) * perp_n.Y), min_pt.Z + ((max_z - min_z) * perp_n.Z)))
                line_ele_list.append(perp_line)

        model_ele_list = ModelEleList()

        # Propiedades rojas (forzadas) para la previsualización
        com = AllplanBaseElements.CommonProperties()
        layer_id = AllplanBaseElements.LayerService.GetIDByShortName(XPS_LAYER, self.document)
        if self.build_ele.do_mensules.value == 1:
            layer_id = AllplanBaseElements.LayerService.GetIDByShortName(XPS_LAYER_MENSULA, self.document)

        com.Layer = layer_id
        # com.Color = 1
        # com.ColorByLayer = False
        # com.ForceColor = True
        # com.Pen = 7
        # com.Stroke = 1

        attribute_list = BuildingElementAttributeList()
        attribute_list.add_attribute(SIZES_ATTRIBUTE, "2950x600x120mm")
        attribute_list.add_attribute(WALL_ID_ATTRIBUTE, self.build_ele.wall_id.value)
        if self.build_ele.do_walls.value == 1:
            attribute_list.add_attribute(PMP_FG_AILLANT, self.val_pmp_fg_aillant)
            attribute_list.add_attribute(PMP_FG_XPS_SUP, self.val_pmp_fg_xps_sup)
            attribute_list.add_attribute(PMP_FG_PIR_SUP, self.val_pmp_fg_pir_sup)

        if self.build_ele.do_mensules.value == 1:
            attribute_list.add_attribute(PMP_FG_MENSULA, self.val_pmp_fg_mensula)
            attribute_list.add_attribute(PMP_FG_MEN_SUP, self.val_pmp_fg_men_sup)

        for i, xps in enumerate(xps_ele_list):
            model_ele_list.append_geometry_3d(xps, com)
            model_ele_list.set_element_attributes(i, attribute_list.get_attribute_list())

        line_attribute_list = BuildingElementAttributeList()
        line_attribute_list.add_attribute(EDGE_ATTRIBUTE, "WALL_EDGE")
        line_attribute_list.add_attribute(WALL_ID_ATTRIBUTE, self.build_ele.wall_id.value)
        init_i = len(model_ele_list)
        for i, line in enumerate(line_ele_list):
            model_ele_list.append_geometry_3d(line)
            model_ele_list.set_element_attributes(init_i + i, line_attribute_list.get_attribute_list())

        return model_ele_list


    def create_unique_panel(self, n, pts, *, offset_mm: float = 2.0, thickness_mm: float = 5.0):
        # 3) Construir el polígono base de la cara
        poly = AllplanGeo.Polygon3D()
        for vt in pts:
            poly += AllplanGeo.Point3D(vt.X, vt.Y, vt.Z)
        # Cerrar si hace falta
        if pts[0] != pts[-1]:
            poly += AllplanGeo.Point3D(pts[0].X, pts[0].Y, pts[0].Z)

        # Validar polígono (evita extrusiones inválidas)
        # (GetPlane / IsValid según API de Polygon3D)
        if hasattr(poly, "IsValid") and not poly.IsValid():
            print("Error creating surface")
            return None

        # 4) Área poligonal para la extrusión
        area = AllplanGeo.PolygonalArea3D()
        area += poly  # el área puede tener 1+ polígonos (huecos), aquí 1

        # 5) Crear ExtrudedAreaSolid3D: espesor hacia la normal exterior
        # solid = AllplanGeo.ExtrudedAreaSolid3D()
        # solid.SetExtrudedArea(area)
        # solid.SetDirection(AllplanGeo.Vector3D(n.X * thickness_mm, n.Y * thickness_mm, n.Z * thickness_mm))
        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(n.X * thickness_mm, n.Y * thickness_mm, n.Z * thickness_mm))
        extruded_solid.SetRefPoint(AllplanGeo.Point3D())
        extruded_solid.SetExtrudedArea(area)

        # Create solid from area
        error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)

        # create list of model elements, if extruding was successful
        if error_code is AllplanGeo.eGeometryErrorCode.eOK:
            # 6) Separar del muro un poco (offset) para que no se superponga
            if offset_mm > 0.0:
                polyhedron = AllplanGeo.Move(polyhedron, AllplanGeo.Vector3D(n.X * offset_mm, n.Y * offset_mm, n.Z * offset_mm))

            # 7) Añadir el sólido fino al resultado con propiedades rojas
            return polyhedron
        else:
            print("Extrusion failed")
            return None


    def create_multiple_panels(self, n, pts, *, offset_mm: float = 2.0, thickness_mm: float = 5.0):
        elems = []

        paneles = self.get_xps_points(pts)
        for panel in paneles:
            verts = panel["vertices_3d"]

            # 3) Construir el polígono base de la cara
            poly = AllplanGeo.Polygon3D()
            for vt in verts:
                poly += AllplanGeo.Point3D(vt[0], vt[1], vt[2])
            # Cerrar si hace falta
            if not np.array_equal(verts[0], verts[-1]):
                poly += AllplanGeo.Point3D(verts[0][0], verts[0][1], verts[0][2])

            # Validar polígono (evita extrusiones inválidas)
            # (GetPlane / IsValid según API de Polygon3D)
            if hasattr(poly, "IsValid") and not poly.IsValid():
                print("Error creating surface")
                continue

            # 4) Área poligonal para la extrusión
            area = AllplanGeo.PolygonalArea3D()
            area += poly  # el área puede tener 1+ polígonos (huecos), aquí 1

            # 5) Crear ExtrudedAreaSolid3D: espesor hacia la normal exterior
            # solid = AllplanGeo.ExtrudedAreaSolid3D()
            # solid.SetExtrudedArea(area)
            # solid.SetDirection(AllplanGeo.Vector3D(n.X * thickness_mm, n.Y * thickness_mm, n.Z * thickness_mm))
            extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
            extruded_solid.SetDirection(AllplanGeo.Vector3D(n.X * thickness_mm, n.Y * thickness_mm, n.Z * thickness_mm))
            extruded_solid.SetRefPoint(AllplanGeo.Point3D())
            extruded_solid.SetExtrudedArea(area)

            # Create solid from area
            error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)

            # create list of model elements, if extruding was successful
            if error_code is AllplanGeo.eGeometryErrorCode.eOK:
                # 6) Separar del muro un poco (offset) para que no se superponga
                if offset_mm > 0.0:
                    polyhedron = AllplanGeo.Move(polyhedron, AllplanGeo.Vector3D(n.X * offset_mm, n.Y * offset_mm, n.Z * offset_mm))

                # 7) Añadir el sólido fino al resultado con propiedades rojas
                # model_ele_list.append_geometry_3d(solid, com)
                for av in self.avoid:
                    geom = av.GetGeometry()
                    err, intersect, union, substract1, substract2 = AllplanGeo.MakeBoolean(polyhedron, geom)
                    if err == AllplanGeo.eGeometryErrorCode.eOK:
                        polyhedron = substract1

                if polyhedron.GetVerticesCount() > 0:
                    if self.build_ele.do_mensules.value == 1:
                        area2 = AllplanGeo.PolygonalArea3D()
                        area2 += poly  # el área puede tener 1+ polígonos (huecos), aquí 1

                        extruded_solid2 = AllplanGeo.ExtrudedAreaSolid3D()
                        extruded_solid2.SetDirection(AllplanGeo.Vector3D((n.X * -1 ) * thickness_mm, (n.Y * -1) * thickness_mm, (n.Z * -1) * thickness_mm))
                        extruded_solid2.SetRefPoint(AllplanGeo.Point3D())
                        extruded_solid2.SetExtrudedArea(area2)

                        error_code2, polyhedron2 = AllplanGeo.CreatePolyhedron(extruded_solid2)

                        if error_code2 is AllplanGeo.eGeometryErrorCode.eOK:
                            err2, intersect2, union2, substract2, substract3 = AllplanGeo.MakeBoolean(polyhedron, polyhedron2)
                            if err2 == AllplanGeo.eGeometryErrorCode.eOK:
                                elems.append(union2)
                            else:
                                print("Union failed")
                        else:
                            print("Extrusion failed")
                            continue
                    else:
                        elems.append(polyhedron)
                else:
                    print("Empty substract")
            else:
                print("Extrusion failed")
                continue

        # Devolver como lista de ModelElement3D
        return elems


    def get_xps_points(self, pts):
        # Lista de puntos 3D numpy
        points_array = [(p.X, p.Y, p.Z) for p in pts]
        puntos = np.array(points_array)

        min_x = np.min(puntos[:, 0])
        max_x = np.max(puntos[:, 0])
        min_y = np.min(puntos[:, 1])
        max_y = np.max(puntos[:, 1])
        min_z = np.min(puntos[:, 2])
        max_z = np.max(puntos[:, 2])

        min_vals = np.array([min_x, min_y, min_z])
        max_vals = np.array([max_x, max_y, max_z])

        # Centrar los puntos
        centroide = np.mean(puntos, axis=0)
        puntos_centrados = puntos - centroide

        # Matriz de covarianza
        cov = np.cov(puntos_centrados.T)

        # Autovalores y autovectores
        valores, vectores = np.linalg.eigh(cov)

        # Ordenar de mayor a menor
        idx = np.argsort(valores)[::-1]
        vectores = vectores[:, idx]

        # Ejes del plano
        eje_u = vectores[:, 0]
        eje_v = vectores[:, 1]
        normal = vectores[:, 2]  # El eje con menor varianza

        # Proyección a coordenadas locales (u, v)
        coordenadas_uv = np.column_stack([
            puntos_centrados @ eje_u,
            puntos_centrados @ eje_v
        ])

        ancho = 2950
        alto = 600

        min_u, min_v = np.min(coordenadas_uv, axis=0)
        max_u, max_v = np.max(coordenadas_uv, axis=0)

        nx = int(np.ceil((max_u - min_u) / ancho))
        ny = int(np.ceil((max_v - min_v) / alto))

        paneles = []
        for i in range(nx):
            for j in range(ny):
                u0 = min_u + i * ancho
                u1 = u0 + ancho
                v0 = min_v + j * alto
                v1 = v0 + alto

                # Filtrar puntos dentro del panel
                dentro = (coordenadas_uv[:,0] >= u0) & (coordenadas_uv[:,0] < u1) & \
                        (coordenadas_uv[:,1] >= v0) & (coordenadas_uv[:,1] < v1)

                puntos_panel = puntos[dentro]

                # Calcular vértices del panel en 3D
                esquina1 = centroide + u0 * eje_u + v0 * eje_v
                esquina2 = centroide + u1 * eje_u + v0 * eje_v
                esquina3 = centroide + u1 * eje_u + v1 * eje_v
                esquina4 = centroide + u0 * eje_u + v1 * eje_v
                vertices_panel = np.array([esquina1, esquina2, esquina3, esquina4])

                clipped_points = np.clip(vertices_panel, min_vals, max_vals)

                # Guardar panel como diccionario
                paneles.append({
                    "indices": (i, j),
                    "puntos_3d": puntos_panel,
                    "vertices_3d": clipped_points
                })


                # uv_dentro = coordenadas_uv[dentro]

                # if len(uv_dentro) > 0:
                #     min_u_local, min_v_local = np.min(uv_dentro, axis=0)
                #     max_u_local, max_v_local = np.max(uv_dentro, axis=0)

                #     esquina1 = centroide + min_u_local * eje_u + min_v_local * eje_v
                #     esquina2 = centroide + max_u_local * eje_u + min_v_local * eje_v
                #     esquina3 = centroide + max_u_local * eje_u + max_v_local * eje_v
                #     esquina4 = centroide + min_u_local * eje_u + max_v_local * eje_v

                #     vertices_recortados = np.array([esquina1, esquina2, esquina3, esquina4])

                #     paneles.append({
                #         "indices": (i, j),
                #         "puntos_3d": puntos_panel,
                #         "vertices_3d": vertices_recortados
                #     })

        return paneles



    # === Helpers robustos para Vector3D y listas de Point3D/Point2D ===
    def _as_vec3(self, maybe_vec):
        """Devuelve un Vector3D si el argumento (o algún item de una tupla) lo contiene."""
        if hasattr(maybe_vec, "X") and hasattr(maybe_vec, "Y") and hasattr(maybe_vec, "Z"):
            return maybe_vec
        if isinstance(maybe_vec, (tuple, list)):
            for part in maybe_vec:
                if hasattr(part, "X") and hasattr(part, "Y") and hasattr(part, "Z"):
                    return part
        return None

    def _as_point3_list(self, obj):
        # 1) Un solo Point3D
        if hasattr(obj, "X") and hasattr(obj, "Y") and hasattr(obj, "Z"):
            return [obj]

        # 2) Contenedor estilo Point3DList (API Allplan)
        if hasattr(obj, "Count") and hasattr(obj, "GetPoint"):
            return [obj.GetPoint(i) for i in range(obj.Count())]

        # 3) CASO lista/tupla heterogénea con una sublista de Point3D
        if isinstance(obj, (list, tuple)):
            # 3.a) ¿La propia lista ya es de Point3D?
            if obj and hasattr(obj[0], "X") and hasattr(obj[0], "Y") and hasattr(obj[0], "Z"):
                # Filtramos solo los que realmente son Point3D por seguridad
                return [p for p in obj if hasattr(p, "X") and hasattr(p, "Y") and hasattr(p, "Z")]

            # 3.b) Buscar entre sus elementos una **sublista** que sí sea de Point3D
            for it in obj:
                # Sublista/tupla de Point3D
                if type(it).__name__ == 'Point3DList' and it and hasattr(it[0], "X") and hasattr(it[0], "Y") and hasattr(it[0], "Z"):
                    return [p for p in it if hasattr(p, "X") and hasattr(p, "Y") and hasattr(p, "Z")]

                # Subcontenedor estilo Point3DList (Count/GetPoint)
                if hasattr(it, "Count") and hasattr(it, "GetPoint"):
                    return [it.GetPoint(i) for i in range(it.Count())]

            # 3.c) Fallback: explorar hijos recursivamente por si hay otro nivel de anidación
            for it in obj:
                pts = self._as_point3_list(it)
                if pts:
                    return pts

        # 4) Nada reconocible → no hay puntos
        return []



    def _as_point2_list(self, pl2d):
        """Devuelve lista [Point2D,...] sin punto de cierre duplicado, robusto a tuplas."""
        n = getattr(pl2d, "Count", lambda: 0)()
        if n == 0:
            return []
        # recolectar puntos
        pts = []
        for i in range(n):
            p = pl2d.GetPoint(i)
            # p podría venir envuelto en tupla
            if isinstance(p, (tuple, list)):
                p = next((x for x in p if hasattr(x, "X") and hasattr(x, "Y")), None)
            if p is not None:
                pts.append(p)
        # quitar cierre duplicado
        if len(pts) >= 2 and abs(pts[0].X-pts[-1].X) < 1e-6 and abs(pts[0].Y-pts[-1].Y) < 1e-6:
            pts.pop()
        return pts

    def _close_ring3(self, pts, tol=1e-6):
        if not pts:
            return pts
        p0, pL = pts[0], pts[-1]
        if (abs(p0.X-pL.X) > tol) or (abs(p0.Y-pL.Y) > tol) or (abs(p0.Z-pL.Z) > tol):
            return pts + [p0]
        return pts




    def on_cancel_function(self):
        """Función de cancelación: se llama cuando el usuario cancela la operación."""
        try:
            if self.preview_faces:
                self.build_ele.z_unique.value = random.random() * 3600

                if self.build_ele.do_walls.value == 1:
                    offset_mm=45
                    thickness_mm= 120

                else:
                    offset_mm=0
                    thickness_mm= 40

                thickness_mm= float(self.build_ele.XPSGruix.value)
                elements = self._build_xps_model_elements(self.preview_faces, offset_mm=offset_mm, thickness_mm=thickness_mm)

                pp_util = PythonPartUtil()
                pp_util.add_pythonpart_view_2d3d(elements)
                pp = pp_util.create_pythonpart(self.build_ele, placement_matrix=AllplanGeo.Matrix3D(), type_display_name="PythonPart XPS PIR")

                AllplanBaseElements.CreateElements(self.document,
                                            AllplanGeo.Matrix3D(),
                                            pp, [], None)

        except Exception:
            return OnCancelFunctionResult.CANCEL_INPUT

        return OnCancelFunctionResult.CANCEL_INPUT
