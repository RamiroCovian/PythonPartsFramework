# -*- coding: utf-8 -*-
"""Script de creacion de Polilineas """

from __future__ import annotations
from typing import List, Optional, Tuple, Set
import traceback
import math
import inspect


import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as PythonUtility


from BaseScriptObject import BaseScriptObject
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult


# ===== Config =====

# Sizes and Tolerances
DRAG_SCALE             = 1.5
HANDLE_SIZE            = 90.0    # mm
HIT_TOL_SEGMENT        = 80.0    # mm (captura de segmentos)
HIT_TOL_VERTEX         = 30.0    # mm (captura de puntos)
HOVER_SCALE            = 1.25
MAX_PERP_DIST_MM       = 20.0    # Ajusta este valor según preferencia
MIN_INSERT_OFFSET_MM   = 2.0     # distancia mínima a extremos para insertar
MIN_SEG_LEN_MM         = 1.0     # evitar segmentos casi nulos

# Colors
BRANCH_ANCHOR_COLOR    = 7       # 7 = magenta (preview de anclaje para bifurcar)
BOX_SELECTED_SEG_COLOR = 9       # 9 = marrón
HANDLE_COLOR_IDX       = 2       # 2 = amarillo (puntos)
INSERT_PREVIEW_COLOR   = 6       # cian para el punto fantasma
MIDPOINT_COLOR         = 4       # color neutro para marcadores de punto medio
PREVIEW_SAVED_COLOR    = 3       # 3 = verde (polilíneas guardadas en preview únicamente)
RECT_COLOR             = 8
SEGMENT_HOVER_COLOR    = 1       # 1 = rojo (segmento bajo mouse)
SEGMENT_SEL_COLOR      = 5       # 5 = azul (segmento seleccionado)
SELECTED_VERTEX_COLOR  = 5

# Midpoints (visual)
MIDPOINT_HIT_TOL       = 12.0    # mm
MIDPOINT_PEN           = 13      # trazo gordo para que se vean
MIDPOINT_SIZE_FACTOR   = 0.90    # tamaño relativo al HANDLE_SIZE
MIDPOINT_Z_BIAS        = 1.0     # mm

# Overlay para segmentos resaltados (evitar z-fighting y mejorar visibilidad)
SEGMENT_OVERLAY_PEN    = 13      # trazo más gordo para que se note
SEGMENT_OVERLAY_Z_BIAS = 1.0     # mm: levanta el tramo resaltado sobre la poly base

# Selection by Box
RECT_PEN               = 12

# ===== Obligatorios =====
def check_allplan_version(_build_ele, _version) -> bool:
    return True


def create_script_object(build_ele, script_object_data):
    return PolylineScriptObject(build_ele, script_object_data)


# ===== Script Object =====
class PolylineScriptObject(BaseScriptObject):
    def __init__(self, build_ele, script_object_data):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.script_object_interactor: Optional[PolylineInteractor] = None

        # Cambio: en lugar de solo puntos, guardamos segmentos con información de sección
        self.saved_segments = []
        self.saved_paths = []

        print(f"[SO] *** SCRIPT OBJECT INICIALIZADO ***")

    def start_input(self):
        self.script_object_interactor = PolylineInteractor(self)
        self.script_object_interactor.start_input(self.coord_input)

    def start_next_input(self):
        """Cleanup resources when transitioning to next input or shutting down"""
        try:
            # Cleanup interactor resources if it exists
            if self.script_object_interactor is not None:
                self.script_object_interactor._cleanup_resources()

            # Clear saved data to prevent accumulation
            self.saved_segments.clear()
            self.saved_paths.clear()

            # Set interactor to None
            self.script_object_interactor = None

            print("[SO] Resources cleaned up in start_next_input")

        except Exception as ex:
            print(f"[SO] Error during cleanup in start_next_input: {ex}")
            # Ensure interactor is still set to None even if cleanup fails
            self.script_object_interactor = None


    def execute(self):
        from CreateElementResult import CreateElementResult

        if not self.saved_paths and not self.saved_segments:
            return CreateElementResult([])

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        elements = []

        # Crear elementos desde saved_segments (con información de sección)
        for segment_info in self.saved_segments:
            if len(segment_info['points']) >= 2:
                line = AllplanGeo.Line3D(segment_info['points'][0], segment_info['points'][1])
                segment_prop = AllplanBaseElements.CommonProperties()
                segment_prop.GetGlobalProperties()
                segment_prop = self._get_properties_for_diameter(segment_prop, segment_info.get('diameter', 110.0))
                elements.append(AllplanBasisElements.ModelElement3D(segment_prop, line))

        # Mantener compatibilidad con saved_paths
        for pts in self.saved_paths:
            if len(pts) >= 2:
                poly = AllplanGeo.Polyline3D()
                for pt in pts:
                    poly += pt
                elements.append(AllplanBasisElements.ModelElement3D(com_prop, poly))

        return CreateElementResult(elements)

    def _get_properties_for_diameter(self, base_prop, diameter: float):
        prop = AllplanBaseElements.CommonProperties()
        prop.GetGlobalProperties()
        return prop

    def _finalize_and_create_now(self):
        try:
            if not self.saved_paths:
                print("[SO] No hay paths guardados para crear")
                return

            com_prop = AllplanBaseElements.CommonProperties()
            com_prop.GetGlobalProperties()
            elems: List[AllplanBasisElements.ModelElement3D] = []

            for pts in self.saved_paths:
                if len(pts) < 2:
                    continue
                poly = AllplanGeo.Polyline3D()
                for p in pts:
                    poly += p
                elems.append(AllplanBasisElements.ModelElement3D(com_prop, poly))

            if elems:
                AllplanBaseElements.CreateElements(
                    self.coord_input.GetInputViewDocument(),
                    AllplanGeo.Matrix3D(),
                    elems, [], None
                )
                print(f"[SO] Creados {len(elems)} elementos en el documento")

            self.saved_paths.clear()
            self.saved_segments.clear()
        except Exception as ex:
            print(f"[SO] Error en _finalize_and_create_now: {ex}")
            try:
                self.saved_paths.clear()
                self.saved_segments.clear()
            except:
                pass


    def on_control_event(self, event_id: int):
        """1001=sync crear checkbox; 1002=guardar; 1003=finalizar(ESC); 1004=borrar"""
        print(f"[SO] *** EVENTO RECIBIDO: {event_id} ***")

        if self.script_object_interactor is None:
            print(f"[SO] Creando interactor...")
            try:
                self.start_input()
            except Exception as ex:
                print(f"[SO] Error creando interactor: {ex}")
                return False

        intr = self.script_object_interactor

        def _finalize_now():
            try:
                if intr:
                    intr.save_current_polyline()
                self._finalize_and_create_now()
                for name in ("CancelFunction", "OnCancelFunction", "CancelInput", "Cancel"):
                    meth = getattr(self.coord_input, name, None)
                    if callable(meth):
                        try:
                            meth(); break
                        except Exception as ex:
                            print(f"[SO] coord_input.{name}() ex: {ex}")
                return True
            except Exception as ex:
                print(f"[SO] Error en finalizar: {ex}")
                return False

        handlers = {
            1001: lambda: (setattr(intr, "create_mode", not intr.create_mode),
                           intr._update_create_mode_display(),
                           intr._apply_create_mode_changes(), True)[-1],
            1002: lambda: (intr.save_current_polyline(),
                           print(f"[SO] Guardadas: {len(self.saved_paths)} polilíneas"), True)[-1],
            1003: _finalize_now,
            1004: lambda: (intr.delete_selected_segments_by_box()
                           if intr.selected_segments else intr.delete_selected_or_hovered_segment()),
            1007: intr.apply_section_to_selected,
            1008: intr.show_sections_info
        }

        try:
            return bool(handlers.get(event_id, lambda: (print(f"[SO] *** EVENTO NO RECONOCIDO: {event_id} ***"), False)[-1])())
        except Exception as ex:
            print(f"[SO] *** ERROR PROCESANDO EVENTO {event_id}: {ex} ***")
            try:
                if self.script_object_interactor is not None:
                    self.script_object_interactor._cleanup_resources()
            except Exception as cleanup_ex:
                print(f"[SO] Error durante limpieza tras excepción: {cleanup_ex}")
            return False


# ===== Interactor =====
class PolylineInteractor:
    def _clear_editing_state(self):
        """
        Centraliza la limpieza de todos los estados temporales de edición, selección, inserción, drag, hover, bifurcación, etc.
        Llamar siempre que se requiera un reset completo de la UI/estado de edición.
        """
        self.is_dragging = False
        self.drag_index = -1
        self.saved_dragging = None
        self.saved_dragging_original_point = None
        self.hover_index = -1
        self.hover_seg = None
        self.selected_seg = None
        self.insert_preview_p = None
        self.insert_target = None
        self.saved_hover_point = None
        self.hover_mid = None
        self.extend_target = None
        # No limpia self.points ni self.current_point (eso depende del contexto)
        # Limpia selección por marcos
        self._clear_box_selection_state()
    # ---------- Borrar segmentos seleccionados por marco ----------
    def delete_selected_segments_by_box(self) -> bool:
        """
        Borra los segmentos seleccionados por marco. Si se seleccionan todos los segmentos de una polilínea,
        se borra toda la polilínea. Si se seleccionan solo algunos, se eliminan esos segmentos y se dividen
        las polilíneas en fragmentos válidos (≥2 puntos).
        """
        if not self.selected_segments:
            return False

        from collections import defaultdict
        to_delete = defaultdict(set)  # path_idx -> set(seg_idx)
        for kind, path_idx, seg_idx in self.selected_segments:
            if kind == 'saved':
                to_delete[path_idx].add(seg_idx)

        changed = False
        new_saved_paths = []
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx not in to_delete:
                new_saved_paths.append(pts)
                continue
            seg_indices = to_delete[path_idx]
            if len(seg_indices) == len(pts) - 1:
                # Se seleccionaron todos los segmentos: borrar toda la polilínea
                changed = True
                continue
            # Si no, fragmentar en partes válidas (≥2 puntos)
            fragment = [pts[0]]
            for i in range(len(pts) - 1):
                if i in seg_indices:
                    if len(fragment) >= 2:
                        new_saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment])
                        changed = True
                    fragment = [pts[i+1]]
                else:
                    fragment.append(pts[i+1])
            if len(fragment) >= 2:
                new_saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in fragment])
                changed = True

        if changed:
            self.script_object.saved_paths = new_saved_paths
            self.selected_seg = None
            self.hover_seg = None
            self.insert_preview_p = None
            self.insert_target = None
            self.hover_mid = None
            self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())
        return changed


    def __init__(self, script_object: PolylineScriptObject):
        self.script_object = script_object

        # Modo creación (toggle con 1001) - OFF por defecto
        self.create_mode = False

        # Polilínea activa (en edición/creación)
        self.points = []
        self.current_point = AllplanGeo.Point3D()

        # Estado de edición (activa)
        self.hover_index = -1
        self.drag_index = -1
        self.is_dragging = False

        # Drag de vértices guardados (edición)
        self.saved_dragging = None  # (path_idx, pt_idx)
        self.saved_dragging_original_point = None  # Coordenadas originales antes del drag

        # : extensión de polilínea guardada ---
        # Si no es None, al guardar se fusiona la activa a esa polilínea (start/end)
        self.extend_target = None  # (path_idx, 'start'|'end')

        # Segmentos: hover + seleccionado persistente
        # Formato: ('active'|'saved', path_idx, seg_idx); active => path_idx = -1
        self.hover_seg = None
        self.selected_seg = None

        # Inserción (controlado por CheckBox en paleta)
        self.insert_mode = False
        self.insert_preview_p = None
        self.insert_target = None

        # Midpoint hover
        self.hover_mid = None

        # Selección por marco
        self.box_selecting = False
        self.box_start = None
        self.box_curr = None
        self.selected_segments = set()  # (kind, path_idx, seg_idx)

        # Propiedades
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()

    def __del__(self):
        """Destructor to ensure cleanup when object is garbage collected"""
        try:
            self._cleanup_resources()
        except Exception:
            # Ignore errors during destruction to prevent issues with garbage collection
            pass

    def _cleanup_resources(self):
        """Comprehensive cleanup of all resources to prevent memory leaks"""
        try:
            print("[INT] Starting resource cleanup...")

            # Clear all preview elements
            self._clear_preview()

            # Clear all temporary data structures
            self.points.clear()
            self.selected_segments.clear()

            # Reset all indices and flags
            self.hover_index = -1
            self.drag_index = -1
            self.is_dragging = False
            self.saved_dragging = None
            self.saved_dragging_original_point = None
            self.extend_target = None
            self.hover_seg = None
            self.selected_seg = None
            self.insert_mode = False
            self.insert_preview_p = None
            self.insert_target = None
            self.hover_mid = None
            self.saved_hover_point = None
            self.saved_dragging_original_point = None
            self.box_selecting = False
            self.box_start = None
            self.box_curr = None

            # Clean up orphaned segments (segments that reference non-existent paths)
            self._cleanup_orphaned_segments()

            # Force garbage collection hint
            self.current_point = AllplanGeo.Point3D()

            print("[INT] Resource cleanup completed successfully")

        except Exception as ex:
            print(f"[INT] Error during resource cleanup: {ex}")
            # Continue cleanup even if some parts fail
            try:
                self.points.clear()
                self.selected_segments.clear()
            except:
                pass

    def _cleanup_orphaned_segments(self):
        """Remove segments that reference non-existent polyline paths to prevent accumulation"""
        try:
            if not hasattr(self.script_object, 'saved_segments') or not self.script_object.saved_segments:
                return

            valid_segments = []
            total_segments = len(self.script_object.saved_segments)

            for segment_info in self.script_object.saved_segments:
                try:
                    points = segment_info.get('points', [])
                    if len(points) >= 2:
                        # Check if this segment still corresponds to an existing path
                        segment_still_valid = False
                        for pts in self.script_object.saved_paths:
                            if len(pts) >= 2:
                                for i in range(len(pts) - 1):
                                    if (self._points_equal(pts[i], points[0]) and
                                        self._points_equal(pts[i + 1], points[1])):
                                        segment_still_valid = True
                                        break
                            if segment_still_valid:
                                break

                        if segment_still_valid:
                            valid_segments.append(segment_info)

                except Exception:
                    # Skip malformed segments
                    continue

            # Update saved_segments with only valid ones
            removed_count = total_segments - len(valid_segments)
            if removed_count > 0:
                self.script_object.saved_segments = valid_segments
                print(f"[INT] Removed {removed_count} orphaned segments from saved_segments")

        except Exception as ex:
            print(f"[INT] Error cleaning orphaned segments: {ex}")

    def _update_segments_after_vertex_drag(self, path_idx: int, vertex_idx: int, original_point: AllplanGeo.Point3D):
        """
        Actualiza las coordenadas de los segmentos afectados después de mover un vértice.
        Se llama cuando se termina el drag de un vértice guardado para sincronizar saved_segments.
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= vertex_idx < len(pts)):
                return

            # Actualizar segmentos afectados por el vértice movido
            segments_updated = 0

            for segment_info in self.script_object.saved_segments:
                if not isinstance(segment_info, dict):
                    continue

                seg_path = segment_info.get('path_idx', -1)
                seg_idx = segment_info.get('seg_idx', -1)

                if seg_path == path_idx and seg_idx >= 0:
                    points = segment_info.get('points', [])
                    if len(points) >= 2:
                        # Actualizar puntos del segmento
                        if seg_idx == vertex_idx:
                            # El vértice movido es el inicio del segmento
                            segment_info['points'][0] = AllplanGeo.Point3D(pts[vertex_idx].X, pts[vertex_idx].Y, pts[vertex_idx].Z)
                            segments_updated += 1
                        elif seg_idx + 1 == vertex_idx:
                            # El vértice movido es el final del segmento
                            segment_info['points'][1] = AllplanGeo.Point3D(pts[vertex_idx].X, pts[vertex_idx].Y, pts[vertex_idx].Z)
                            segments_updated += 1

            if segments_updated > 0:
                print(f"[INT] Actualizados {segments_updated} segmentos después de mover vértice {vertex_idx} en polilínea {path_idx}")
            else:
                print(f"[INT] No se encontraron segmentos para actualizar después de mover vértice {vertex_idx} en polilínea {path_idx}")

        except Exception as ex:
            print(f"[INT] Error actualizando segmentos después de drag: {ex}")

    def _propagate_section_info_after_split(self, path_idx: int, original_seg_idx: int, original_section_info: dict, original_end_point: AllplanGeo.Point3D):
        """
        Propaga la información de sección del segmento original a los dos nuevos segmentos
        después de insertar un punto intermedio.
        """
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return

            pts = self.script_object.saved_paths[path_idx]

            # Después de la inserción, tenemos:
            # - Segmento 1: pts[original_seg_idx] -> pts[original_seg_idx + 1] (hasta punto insertado)
            # - Segmento 2: pts[original_seg_idx + 1] -> pts[original_seg_idx + 2] (desde punto insertado hasta final)

            if original_seg_idx + 2 >= len(pts):
                print(f"[INT] Error: índices fuera de rango después de inserción")
                return

            # Remover el segmento original de saved_segments usando el punto final original guardado
            original_segments = []
            filtered_segments = []

            for seg in self.script_object.saved_segments:
                if self._is_original_segment(seg, pts[original_seg_idx], original_end_point):
                    original_segments.append(seg)
                else:
                    filtered_segments.append(seg)

            self.script_object.saved_segments = filtered_segments

            if original_segments:
                print(f"[INT] Removido {len(original_segments)} segmento(s) original(es)")

            # Crear dos nuevos segmentos con la misma información de sección
            # Primer segmento: del punto original al punto insertado
            first_segment_info = {
                'points': [
                    AllplanGeo.Point3D(pts[original_seg_idx].X, pts[original_seg_idx].Y, pts[original_seg_idx].Z),
                    AllplanGeo.Point3D(pts[original_seg_idx + 1].X, pts[original_seg_idx + 1].Y, pts[original_seg_idx + 1].Z)
                ],
                'diameter': original_section_info.get('diameter', 110.0),
                'section_type': original_section_info.get('section_type', '110mm'),
                'system': original_section_info.get('system', 'Pluvial'),
                'label': original_section_info.get('label', 'D110 P'),
                'path_idx': path_idx,
                'seg_idx': original_seg_idx
            }

            # Segundo segmento: del punto insertado al punto final original (ahora en posición +2)
            second_segment_info = {
                'points': [
                    AllplanGeo.Point3D(pts[original_seg_idx + 1].X, pts[original_seg_idx + 1].Y, pts[original_seg_idx + 1].Z),
                    AllplanGeo.Point3D(pts[original_seg_idx + 2].X, pts[original_seg_idx + 2].Y, pts[original_seg_idx + 2].Z)
                ],
                'diameter': original_section_info.get('diameter', 110.0),
                'section_type': original_section_info.get('section_type', '110mm'),
                'system': original_section_info.get('system', 'Pluvial'),
                'label': original_section_info.get('label', 'D110 P'),
                'path_idx': path_idx,
                'seg_idx': original_seg_idx + 1
            }

            # Añadir ambos segmentos a saved_segments
            self.script_object.saved_segments.append(first_segment_info)
            self.script_object.saved_segments.append(second_segment_info)

            print(f"[INT] Propagada información de sección a 2 nuevos segmentos: {original_section_info.get('label', 'Sin etiqueta')}")

        except Exception as ex:
            print(f"[INT] Error propagando información de sección después de split: {ex}")

    def _is_original_segment(self, segment_info: dict, original_start: AllplanGeo.Point3D, original_end: AllplanGeo.Point3D) -> bool:
        """
        Verifica si un segmento es el segmento original que se va a dividir.
        """
        try:
            if not isinstance(segment_info, dict) or 'points' not in segment_info:
                return False

            points = segment_info['points']
            if len(points) < 2:
                return False

            # Verificar si los puntos coinciden con el segmento original
            start_match = self._points_equal(points[0], original_start)
            end_match = self._points_equal(points[1], original_end)

            if start_match and end_match:
                print(f"[INT] Encontrado segmento original para remover: {segment_info.get('label', 'Sin etiqueta')}")
                return True

            return False

        except Exception as ex:
            print(f"[INT] Error verificando segmento original: {ex}")
            return False


    # ---------- Inicio ----------
    def start_input(self, coord_input):
        self.coord_input = coord_input
        self._sync_insert_mode_from_palette()

        # Sincronización inicial: leer el estado del checkbox y aplicarlo
        try:
            checkbox_value = self._safe_get_palette_property("CrearPolylinea")
            if hasattr(checkbox_value, "value"):
                self.create_mode = bool(checkbox_value.value)
                print(f"[INT] Estado inicial del checkbox: {checkbox_value.value} -> create_mode = {self.create_mode}")
            else:
                # Valor por defecto
                self.create_mode = False
                print(f"[INT] Checkbox no encontrado, usando valor por defecto: create_mode = {self.create_mode}")
        except Exception as ex:
            self.create_mode = False
            print(f"[INT] Error leyendo estado inicial: {ex}")

        # Actualizar display inicial
        self._update_create_mode_display()
        self._print_prompt()

    def _print_prompt(self):
        msg = (
            "Edición: drag vértices guardados; selección por marco (clic vacío→mover→clic); "
            "midpoints clicables; clic en segmento para seleccionar; "
            "1004=borrar segmento; 1002=guardar; ESC/1003=finalizar"
        )
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert(msg))

    def toggle_create_mode(self):
        self.create_mode = not self.create_mode
        self._update_create_mode_display()
        self._apply_create_mode_changes()

    def sync_create_mode_from_checkbox(self):
        """Sincroniza el modo de creación con el valor del checkbox en la paleta"""
        try:
            # Leer el valor actual del checkbox de manera segura
            checkbox_value = self._safe_get_palette_property("CrearPolylinea", None)

            if checkbox_value is None:
                # No hacemos nada si no podemos leer el valor
                return

            # Convertir a booleano de manera segura
            try:
                if isinstance(checkbox_value, bool):
                    new_mode = checkbox_value
                elif hasattr(checkbox_value, '__bool__'):
                    new_mode = bool(checkbox_value)
                else:
                    new_mode = bool(checkbox_value)
            except Exception as conv_ex:
                print(f"[INT] Error convirtiendo valor del checkbox: {conv_ex}")
                return

            # Comparar con el estado actual - solo cambiar si realmente es diferente
            if new_mode != self.create_mode:
                self.create_mode = new_mode
                self._update_create_mode_display()
                self._apply_create_mode_changes()

        except Exception as ex:
            print(f"[INT] Error sincronizando checkbox: {ex}")
            traceback.print_exc()

    def _update_create_mode_display(self):
        """Actualiza el texto de feedback en la paleta y el estado visual del botón"""
        print(f"[INT] Crear polilínea: OFF")
        try:
            # Actualizar texto de feedback de manera segura
            self._safe_set_palette_property("FirstText", "")

            # Intentar actualizar la paleta si es posible
            try:
                if hasattr(self.script_object, 'palette_service') and self.script_object.palette_service:
                    self.script_object.palette_service.update_palette(self.script_object.build_ele, show_palette=True)
            except Exception as palette_ex:
                print(f"[INT] No se pudo actualizar paleta: {palette_ex}")

        except Exception as ex:
            print(f"[INT] Error actualizando displays: {ex}")
            traceback.print_exc()

    def _apply_create_mode_changes(self):
        """Aplica los cambios correspondientes al cambiar de modo"""
        if not self.create_mode:
            self.save_current_polyline()  # guarda lo que estuvieras creando/extendiéndo
        self._clear_editing_state()
        # Si activamos crear, desactivar modo insertar para evitar confusiones
        if self.create_mode and self.insert_mode:
            self.insert_mode = False
            print("[INT] Insert mode: OFF (por activar Crear)")
        self._print_prompt()
        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

    # ---------- Paleta -> modo insertar ----------
    def _get_palette_insert_mode(self) -> Optional[bool]:
        """Obtiene el modo de inserción desde la paleta de manera segura"""
        # Renombrado en paleta: antes "CheckBoxValue" (duplicado). Ahora único: "CheckBoxInsertarPunto"
        return self._safe_get_palette_property("CheckBoxInsertarPunto", None)

    def _get_palette_limit_angles(self) -> Optional[bool]:
        """Lee el checkbox 'Limitar ángulos' de la paleta.
        Nota: actualmente no se utiliza en la lógica; se deja listo para futuras mejoras.
        """
        return self._safe_get_palette_property("CheckBoxLimitarAngulos", None)

    def _sync_insert_mode_from_palette(self):
        new_mode = self._get_palette_insert_mode()
        if new_mode is None:
            return
        if new_mode != self.insert_mode:
            self.insert_mode = new_mode
            print(f"[INT] Insert mode (checkbox): {'ON' if self.insert_mode else 'OFF'}")
            self.insert_preview_p = None
            self.insert_target = None

    # ---------- Utilidades ----------
    def _dist_sq(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        dx, dy, dz = a.X - b.X, a.Y - b.Y, a.Z - b.Z
        return dx*dx + dy*dy + dz*dz

    def _segment_len(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> float:
        return (self._dist_sq(a, b)) ** 0.5

    def _segment_project_point(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, p: AllplanGeo.Point3D) -> Tuple[float, AllplanGeo.Point3D]:
        vx, vy, vz = b.X - a.X, b.Y - a.Y, b.Z - a.Z
        wx, wy, wz = p.X - a.X, p.Y - a.Y, p.Z - a.Z
        vv = vx*vx + vy*vy + vz*vz
        if vv <= 1e-12:
            return 0.0, AllplanGeo.Point3D(a.X, a.Y, a.Z)
        t = (vx*wx + vy*wy + vz*wz) / vv
        if t < 0.0:   t = 0.0
        elif t > 1.0: t = 1.0
        q = AllplanGeo.Point3D(a.X + t*vx, a.Y + t*vy, a.Z + t*vz)
        return t, q

    def _midpoint(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> AllplanGeo.Point3D:
        return AllplanGeo.Point3D((a.X + b.X) * 0.5, (a.Y + b.Y) * 0.5, (a.Z + b.Z) * 0.5)

    def _is_valid_angle(self, new_point: AllplanGeo.Point3D) -> bool:
        """
        Valida el nuevo segmento según el modo "Limitar ángulos":
        - El ángulo absoluto del segmento debe ser múltiplo de 45° (0,45,90,...).
        - Además, se prohíbe que el giro entre el último segmento y el nuevo sea de 45° (ángulo cerrado de 45°).
        Si el checkbox "Limitar ángulos" está OFF, no se aplica ninguna restricción.
        """
        # Si no hay punto previo o el modo limitar ángulos está OFF, permitir
        if len(self.points) < 1:
            return True

        limit_angles = self._get_palette_limit_angles()
        if not limit_angles:
            return True

        # Vectores en XY
        last_point = self.points[-1]
        dx = new_point.X - last_point.X
        dy = new_point.Y - last_point.Y

        # Evitar validación en segmentos demasiado cortos
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return True

        # 1) Restringir dirección absoluta del nuevo segmento a múltiplos de 45°
        angle_deg = (math.degrees(math.atan2(dy, dx)) % 360.0)
        valid_angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        tolerance = 1.0
        if not any(abs(angle_deg - va) <= tolerance for va in valid_angles):
            return False

        # 2) Prohibir giro "cerrado" de 45° entre el último segmento y el nuevo
        if len(self.points) >= 2:
            prev_point = self.points[-2]
            pvx = last_point.X - prev_point.X
            pvy = last_point.Y - prev_point.Y
            # Si el segmento previo es válido
            if abs(pvx) > 1e-6 or abs(pvy) > 1e-6:
                prev_ang = (math.degrees(math.atan2(pvy, pvx)) % 360.0)
                # Diferencia mínima entre direcciones (0..180)
                delta = abs((angle_deg - prev_ang + 180.0) % 360.0 - 180.0)
                # Ángulo cerrado de 45° implica que el ángulo complementario (abierto) es 135°
                # Por tanto, cuando delta ≈ 135°, el ángulo cerrado es 45° y se debe bloquear.
                if abs((180.0 - delta) - 45.0) <= tolerance:
                    # Giro cerrado de 45° detectado -> prohibido
                    return False

        return True

    def _find_hover_index(self, p: AllplanGeo.Point3D) -> int:
        if not self.points:
            return -1
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = -1
        best_d2 = max_d2 + 1.0
        for i, pt in enumerate(self.points):
            d2 = self._dist_sq(p, pt)
            if d2 <= max_d2 and d2 < best_d2:
                best_d2 = d2
                best = i
        return best

    def _find_hover_saved_point(self, p: AllplanGeo.Point3D, only_extremes: bool = False) -> Optional[Tuple[int, int, AllplanGeo.Point3D]]:
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None
        best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            indices = range(len(pts))
            for i in indices:
                q = pts[i]
                d2 = self._dist_sq(p, q)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = (path_idx, i, q)
        return best

    def _find_nearby_extreme(self, p: AllplanGeo.Point3D, exclude_path: int = -1) -> Optional[Tuple[int, str]]:
        """Busca extremos de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path"""
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx == exclude_path:
                continue
            if len(pts) >= 2:
                # Check start
                if self._dist_sq(p, pts[0]) <= max_d2:
                    return (path_idx, 'start')
                # Check end
                if self._dist_sq(p, pts[-1]) <= max_d2:
                    return (path_idx, 'end')
        return None

    def _find_nearby_vertex(self, p: AllplanGeo.Point3D, exclude_path: int = -1) -> Optional[Tuple[int, int]]:
        """Busca cualquier vértice de polilíneas guardadas cerca del punto p, excluyendo la polilínea exclude_path"""
        max_d2 = HIT_TOL_VERTEX * HIT_TOL_VERTEX
        best = None
        best_d2 = max_d2 + 1.0
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if path_idx == exclude_path:
                continue
            for i, q in enumerate(pts):
                d2 = self._dist_sq(p, q)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = (path_idx, i)
        return best

    # NUEVO: preferencia de búsqueda por tipo de segmento
    # preferred_kind: 'active', 'saved' o None (ambos)
    def _find_hover_segment(self, p: AllplanGeo.Point3D, preferred_kind: Optional[str] = None) -> Optional[Tuple[str, int, int]]:
        max_d2 = HIT_TOL_SEGMENT * HIT_TOL_SEGMENT
        best: Optional[Tuple[str, int, int]] = None
        best_d2 = max_d2 + 1.0

        # Activa
        if preferred_kind in (None, 'active'):
            if len(self.points) >= 2:
                for i in range(len(self.points) - 1):
                    a, b = self.points[i], self.points[i+1]
                    _, q = self._segment_project_point(a, b, p)
                    dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                    d2 = dx*dx + dy*dy + dz*dz
                    if d2 <= max_d2 and d2 < best_d2:
                        best_d2 = d2
                        best = ('active', -1, i)

        # Guardadas
        if preferred_kind in (None, 'saved'):
            for path_idx, pts in enumerate(self.script_object.saved_paths):
                if len(pts) < 2:
                    continue
                for i in range(len(pts) - 1):
                    a, b = pts[i], pts[i+1]
                    _, q = self._segment_project_point(a, b, p)
                    dx, dy, dz = p.X - q.X, p.Y - q.Y, p.Z - q.Z
                    d2 = dx*dx + dy*dy + dz*dz
                    if d2 <= max_d2 and d2 < best_d2:
                        best_d2 = d2
                        best = ('saved', path_idx, i)

        return best

    def _find_hover_midpoint(self, p: AllplanGeo.Point3D) -> Optional[Tuple[str, int, int, AllplanGeo.Point3D]]:
        max_d2 = MIDPOINT_HIT_TOL * MIDPOINT_HIT_TOL
        best = None
        best_d2 = max_d2 + 1.0

        # Activa
        if len(self.points) >= 2:
            for i in range(len(self.points) - 1):
                a, b = self.points[i], self.points[i+1]
                mp = self._midpoint(a, b)
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = ('active', -1, i, mp)

        # Guardadas
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) < 2:
                continue
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i+1]
                mp = self._midpoint(a, b)
                d2 = self._dist_sq(p, mp)
                if d2 <= max_d2 and d2 < best_d2:
                    best_d2 = d2
                    best = ('saved', path_idx, i, mp)

        return best

    def _seg_equal(self, a: Optional[Tuple[str, int, int]], b: Optional[Tuple[str, int, int]]) -> bool:
        if a is None or b is None:
            return False
        return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

    def _clear_selection_if_invalid(self):
        sel = self.selected_seg
        if sel is None:
            return
        kind, path_idx, seg_idx = sel
        if kind == 'active':
            if seg_idx < 0 or seg_idx >= max(0, len(self.points) - 1):
                self.selected_seg = None
        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                self.selected_seg = None
            else:
                pts = self.script_object.saved_paths[path_idx]
                if seg_idx < 0 or seg_idx >= max(0, len(pts) - 1):
                    self.selected_seg = None

    def _can_start_box_selection(self) -> bool:
        """
        Verifica si se puede iniciar la selección por marcos según el estado actual.
        Evita conflictos con otros modos activos.
        """
        # No permitir selección por marcos si estamos en modo creación
        if self.create_mode:
            return False

        # No permitir si estamos arrastrando elementos
        if self.is_dragging or self.saved_dragging is not None:
            return False

        # No permitir si estamos extendiendo una polilínea
        if self.extend_target is not None:
            return False

        # No permitir si hay una polilínea activa en creación
        if self.points:
            return False

        # Solo permitir en modo edición (create_mode=False) y sin estados activos
        return True

    def _clear_box_selection_state(self):
        """
        Limpia completamente el estado de selección por marcos.
        Útil para evitar estados inconsistentes al cambiar de modo.
        """
        if self.box_selecting:
            print("[INT] Cancelando selección por marcos en curso debido a cambio de modo")

        self.box_selecting = False
        self.box_start = None
        self.box_curr = None
        self.selected_segments.clear()

    def _point_in_rect_xy(self, p: AllplanGeo.Point3D, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D) -> bool:
        xmin, xmax = (a.X, b.X) if a.X <= b.X else (b.X, a.X)
        ymin, ymax = (a.Y, b.Y) if a.Y <= b.Y else (b.Y, a.Y)
        return (xmin <= p.X <= xmax) and (ymin <= p.Y <= ymax)

    # ---------- Entrada de mouse ----------
    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        # Sincronizar siempre el modo crear desde la paleta (checkbox)
        self.sync_create_mode_from_checkbox()
        # Sincronizar modo insertar desde la paleta
        self._sync_insert_mode_from_palette()


        # --- SNAP A ÁNGULOS VÁLIDOS SI LIMITAR ÁNGULOS ESTÁ ACTIVO ---
        raw_pnt = self.coord_input.GetInputPoint(
            mouse_msg, pnt, msg_info, self.current_point, bool(self.points)
        ).GetPoint()

        # Aplicar snapping si estamos en modo creación y limitar ángulos está activo
        if self.create_mode and self._get_palette_limit_angles():
            # Determinar el punto de referencia para el snapping
            if self.is_dragging and self.drag_index == len(self.points) - 1:
                # Dragging el último punto
                if len(self.points) >= 2:
                    last_point = self.points[-2]
                    prev_point_for_filter = self.points[-3] if len(self.points) >= 3 else None
                else:
                    last_point = None
                    prev_point_for_filter = None
            else:
                # Agregando nuevo punto o no dragging
                if len(self.points) >= 1:
                    last_point = self.points[-1]
                    prev_point_for_filter = self.points[-2] if len(self.points) >= 2 else None
                else:
                    last_point = None
                    prev_point_for_filter = None

            if last_point:
                dx = raw_pnt.X - last_point.X
                dy = raw_pnt.Y - last_point.Y
                dz = raw_pnt.Z - last_point.Z
                dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                if dist > 1e-6:
                    angle = math.atan2(dy, dx)
                    angle_deg = (math.degrees(angle) % 360.0)
                    valid_angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
                    tolerance = 1.0
                    # Si hay segmento anterior, filtrar los ángulos que NO generan giro cerrado de 45° ni permiten volver sobre sí mismo
                    if prev_point_for_filter:
                        pvx = last_point.X - prev_point_for_filter.X
                        pvy = last_point.Y - prev_point_for_filter.Y
                        prev_ang = (math.degrees(math.atan2(pvy, pvx)) % 360.0)
                        def is_valid_snap(va):
                            delta = abs((va - prev_ang + 180.0) % 360.0 - 180.0)
                            # Bloquear giro cerrado de 45° (delta ≈ 135°) y volver sobre sí mismo (delta ≈ 180°)
                            if abs((180.0 - delta) - 45.0) <= tolerance:
                                return False
                            if abs(delta - 180.0) <= tolerance:
                                return False
                            return True
                        filtered_angles = [va for va in valid_angles if is_valid_snap(va)]
                        # Si todos los ángulos están prohibidos (raro), usar todos
                        snap_angles = filtered_angles if filtered_angles else valid_angles
                    else:
                        snap_angles = valid_angles
                    # Buscar el ángulo permitido más cercano que no forme giro cerrado de 45°
                    closest = min(snap_angles, key=lambda va: abs(angle_deg - va))
                    snap_angle_rad = math.radians(closest)
                    snap_dx = dist * math.cos(snap_angle_rad)
                    snap_dy = dist * math.sin(snap_angle_rad)
                    current_pnt = AllplanGeo.Point3D(last_point.X + snap_dx, last_point.Y + snap_dy, raw_pnt.Z)
                else:
                    current_pnt = raw_pnt
            else:
                current_pnt = raw_pnt
        else:
            current_pnt = raw_pnt        # Movimiento
        if self.coord_input.IsMouseMove(mouse_msg):
            # Drag de activo
            if self.is_dragging and 0 <= self.drag_index < len(self.points):
                self.points[self.drag_index] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.current_point = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.hover_index = -1
                self.hover_seg = None
                self.hover_mid = None
                self.insert_preview_p = None
                self.insert_target = None
                self.saved_hover_point = None
                self._clear_selection_if_invalid()

            # Drag de guardado (solo Crear=OFF)
            elif (not self.create_mode) and self.saved_dragging is not None:
                pidx, vidx = self.saved_dragging
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self.saved_hover_point = None
                self.hover_mid = None
                self.hover_seg = None

            else:
                # ¿Rectángulo de selección activo?
                if self.box_selecting and (self.box_start is not None):
                    self.box_curr = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                else:
                    # Prioridad: puntos activos -> midpoints -> segmentos -> vértices guardados
                    self.hover_index = self._find_hover_index(current_pnt) if self.create_mode else -1
                    self.hover_mid = None if self.hover_index != -1 else self._find_hover_midpoint(current_pnt)
                    # FORZAR tipo según modo:
                    if self.create_mode:
                        self.hover_seg = None if (self.hover_index != -1 or self.hover_mid is not None) else self._find_hover_segment(current_pnt, preferred_kind='active')
                    else:
                        self.hover_seg = None if (self.hover_mid is not None) else self._find_hover_segment(current_pnt, preferred_kind='saved')

                    # Para edición (Crear=OFF): también trackeamos vértices guardados
                    self.saved_hover_point = None
                    if not self.create_mode and self.hover_mid is None and self.hover_seg is None:
                        self.saved_hover_point = self._find_hover_saved_point(current_pnt)

                    # Inserción preview (solo cuando NO hay midpoint bajo mouse)
                    if self.insert_mode and (self.hover_seg is not None) and (self.hover_mid is None):
                        a, b = self._get_segment_endpoints(self.hover_seg)
                        if a and b:
                            t, q = self._segment_project_point(a, b, current_pnt)
                            if self._can_insert_here(a, b, t):
                                self.insert_preview_p = q
                                self.insert_target = self.hover_seg
                            else:
                                self.insert_preview_p = None
                                self.insert_target = None
                        else:
                            self.insert_preview_p = None
                            self.insert_target = None
                    else:
                        self.insert_preview_p = None
                        self.insert_target = None

            self._draw_preview(current_pnt)
            return True

        # Click izquierdo
        is_left = (getattr(mouse_msg, 'Button', 1) == 1)

        if is_left:
            # Soltar drags en curso
            if self.is_dragging:
                self.is_dragging = False
                self.drag_index = -1
                self._clear_selection_if_invalid()
                self._draw_preview(current_pnt)
                return True
            if self.saved_dragging is not None:
                pidx, vidx = self.saved_dragging
                pts = self.script_object.saved_paths[pidx]
                if vidx == 0 or vidx == len(pts) - 1:  # es extremo
                    merge_target = self._find_nearby_extreme(current_pnt, exclude_path=pidx)
                    if merge_target:
                        target_pidx, target_end = merge_target
                        self._merge_polylines(pidx, 'start' if vidx == 0 else 'end', target_pidx, target_end)
                    else:
                        # mover normalmente
                        pts[vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                        if self.saved_dragging_original_point is not None:
                            self._update_segments_after_vertex_drag(pidx, vidx, self.saved_dragging_original_point)
                else:
                    # mover normalmente
                    pts[vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                    if self.saved_dragging_original_point is not None:
                        self._update_segments_after_vertex_drag(pidx, vidx, self.saved_dragging_original_point)
                self.saved_dragging = None
                self.saved_dragging_original_point = None
                self._draw_preview(current_pnt)
                return True

            # --- MODO CREAR=ON: agregar puntos a polilínea activa ---
            if self.create_mode:
                # 1) Click sobre PUNTO ACTIVO -> iniciar drag
                self.hover_index = self._find_hover_index(current_pnt)
                if self.hover_index != -1:
                    self.is_dragging = True
                    self.drag_index = self.hover_index
                    self.points[self.drag_index] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                    self._clear_selection_if_invalid()
                    self._draw_preview(current_pnt)
                    return True

                # 2) Click sobre MIDPOINT -> insertar punto directo
                self.hover_mid = self._find_hover_midpoint(current_pnt)
                if self.hover_mid is not None:
                    kind, path_idx, seg_idx, mp = self.hover_mid
                    seg = (kind, path_idx, seg_idx)
                    a, b = self._get_segment_endpoints(seg)
                    if a and b and self._can_insert_here(a, b, 0.5):
                        self._insert_on_segment(seg, mp, keep_selection_left=True)
                        self.insert_preview_p = None
                        self.insert_target = None
                        self.hover_seg = None
                        self.hover_mid = None
                        self._draw_preview(current_pnt)
                        return True

                # 3) Click sobre SEGMENTO: prioridad insertar si está activo
                self.hover_seg = self._find_hover_segment(current_pnt, preferred_kind='active')
                if self.hover_seg is not None:
                    a, b = self._get_segment_endpoints(self.hover_seg)
                    if self.insert_mode and a and b:
                        t, q = self._segment_project_point(a, b, current_pnt)
                        if self._can_insert_here(a, b, t):
                            self._insert_on_segment(self.hover_seg, q, keep_selection_left=True)
                            self.insert_preview_p = None
                            self.insert_target = None
                            self.hover_seg = None
                            self.hover_mid = None
                            self._draw_preview(current_pnt)
                            return True
                    # Solo si NO está en modo insertar, permitir selección de segmento
                    if not self.insert_mode:
                        if self._seg_equal(self.selected_seg, self.hover_seg):
                            self.selected_seg = None
                        else:
                            self.selected_seg = self.hover_seg
                        self._draw_preview(current_pnt)
                        return True

                # 4) Click en vacío -> agregar vértice al final de la ACTIVA

                # Verificar ángulos válidos si está activada la limitación
                limit_angles = self._get_palette_limit_angles()
                if limit_angles:
                    # --- NUEVO: Solo permitir click si el mouse está cerca de la línea propuesta ---
                    # Usar la dirección del snap (current_pnt) y la línea desde last_point
                    last_point = self.points[-1] if self.points else None
                    if last_point is not None:
                        # Calcular proyección perpendicular del mouse a la línea propuesta
                        # (línea: last_point -> current_pnt)
                        # Distancia perpendicular del mouse real (raw_pnt) a la línea propuesta
                        # Usar la proyección del raw_pnt sobre la línea last_point-current_pnt
                        # Si la distancia es mayor a un umbral, ignorar el click
                        # Solo si el segmento propuesto no es demasiado corto
                        seg_len = self._segment_len(last_point, current_pnt)
                        if seg_len > 1e-6:
                            # Vector de la línea propuesta
                            vx = current_pnt.X - last_point.X
                            vy = current_pnt.Y - last_point.Y
                            # Vector del mouse real
                            wx = raw_pnt.X - last_point.X
                            wy = raw_pnt.Y - last_point.Y
                            # Proyección escalar
                            t = (vx*wx + vy*wy) / max(vx*vx + vy*vy, 1e-12)
                            # Punto proyectado sobre la línea
                            proj_x = last_point.X + t * vx
                            proj_y = last_point.Y + t * vy
                            # Distancia perpendicular
                            perp_dist = ((raw_pnt.X - proj_x)**2 + (raw_pnt.Y - proj_y)**2) ** 0.5
                            if perp_dist > MAX_PERP_DIST_MM:
                                # Feedback visual
                                self._safe_set_palette_property("FirstText", f"El mouse está demasiado lejos del ángulo propuesto (>{int(MAX_PERP_DIST_MM)} mm)")
                                return True  # Ignorar el click
                            else:
                                self._safe_set_palette_property("FirstText", "")

                    if not self._is_valid_angle(current_pnt):
                        PythonUtility.ShowMessageBox("Ángulo inválido", PythonUtility.MB_OK)
                        return True  # No agregar el punto

                self.points.append(AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z))
                self.current_point = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self._clear_selection_if_invalid()
                self._draw_preview(current_pnt)

                # Verificación automática de fusión durante creación
                if len(self.points) >= 2:
                    nearby = self._find_nearby_extreme(self.points[-1])
                    if nearby:
                        target_path, target_end = nearby
                        # Agregar la polilínea activa a saved_paths temporalmente
                        new_path_idx = len(self.script_object.saved_paths)
                        self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points])
                        self._merge_polylines(target_path, target_end, new_path_idx, 'end')  # El último punto es el que está cerca
                        # Limpiar
                        self.points.clear()
                        self._clear_editing_state()
                        self._draw_preview(current_pnt)
                        return True

                    # Verificación de vértices intermedios: mover si cerca
                    nearby_vertex = self._find_nearby_vertex(self.points[-1])
                    if nearby_vertex:
                        target_path, target_vertex_idx = nearby_vertex
                        target_point = self.script_object.saved_paths[target_path][target_vertex_idx]
                        current_point = self.points[-1]
                        delta_x = target_point.X - current_point.X
                        delta_y = target_point.Y - current_point.Y
                        delta_z = target_point.Z - current_point.Z
                        # Trasladar toda la polilínea activa
                        for p in self.points:
                            p.X += delta_x
                            p.Y += delta_y
                            p.Z += delta_z
                        print(f"[INT] Polilínea movida al vértice intermedio {target_vertex_idx} de polilínea {target_path} durante creación")
                        # Actualizar current_point
                        self.current_point = AllplanGeo.Point3D(target_point.X, target_point.Y, target_point.Z)
                        self._draw_preview(current_pnt)
                        return True

                return True

            # --- MODO CREAR=OFF: edición (guardadas) ---
            # A) Click en vértice GUARDADO -> iniciar drag de guardado
            self.saved_hover_point = self._find_hover_saved_point(current_pnt)
            if self.saved_hover_point is not None:
                pidx, vidx, _ = self.saved_hover_point
                # Capturar coordenadas originales antes del drag
                original_point = self.script_object.saved_paths[pidx][vidx]
                self.saved_dragging_original_point = AllplanGeo.Point3D(original_point.X, original_point.Y, original_point.Z)
                self.saved_dragging = (pidx, vidx)
                self.script_object.saved_paths[pidx][vidx] = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                self._draw_preview(current_pnt)
                return True

            # B) Click en MIDPOINT -> insertar punto directo (edición)
            self.hover_mid = self._find_hover_midpoint(current_pnt)
            if self.hover_mid is not None:
                kind, path_idx, seg_idx, mp = self.hover_mid
                seg = (kind, path_idx, seg_idx)
                a, b = self._get_segment_endpoints(seg)
                if a and b and self._can_insert_here(a, b, 0.5):
                    self._insert_on_segment(seg, mp, keep_selection_left=True)
                    self.insert_preview_p = None
                    self.insert_target = None
                    self.hover_seg = None
                    self.hover_mid = None
                    self._draw_preview(current_pnt)
                    return True

            # C) Click sobre SEGMENTO GUARDADO: prioridad insertar si está activo
            self.hover_seg = self._find_hover_segment(current_pnt, preferred_kind='saved')
            if self.hover_seg is not None:
                a, b = self._get_segment_endpoints(self.hover_seg)
                if self.insert_mode and a and b:
                    t, q = self._segment_project_point(a, b, current_pnt)
                    if self._can_insert_here(a, b, t):
                        self._insert_on_segment(self.hover_seg, q, keep_selection_left=True)
                        self.insert_preview_p = None
                        self.insert_target = None
                        self.hover_seg = None
                        self.hover_mid = None
                        self._draw_preview(current_pnt)
                        return True
                # Solo si NO está en modo insertar, permitir selección de segmento guardado
                if not self.insert_mode:
                    if self._seg_equal(self.selected_seg, self.hover_seg):
                        self.selected_seg = None
                    else:
                        self.selected_seg = self.hover_seg
                    print(f"[INT] Toggle selección seg guardado: {self.selected_seg}")
                    self._draw_preview(current_pnt)
                    return True

            # D) Selección por marco de segmentos - Solo si no hay conflictos de modo
            # Verificar que no estemos en modos que entren en conflicto
            if self._can_start_box_selection():
                if not self.box_selecting:
                    self.box_selecting = True
                    self.box_start = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                    self.box_curr = AllplanGeo.Point3D(current_pnt.X, current_pnt.Y, current_pnt.Z)
                    print("[INT] Iniciando selección por marco")
                else:
                    # Finalizar selección por marco
                    # Validar coordenadas del rectángulo de selección
                    if (self.box_start is not None and self.box_curr is not None and
                        not (self.box_start.X == self.box_curr.X and self.box_start.Y == self.box_curr.Y)):

                        sel: Set[Tuple[str, int, int]] = set()
                        for pidx, pts in enumerate(self.script_object.saved_paths):
                            if len(pts) < 2:  # Validar que la polilínea tenga al menos 2 puntos
                                continue
                            for seg_idx in range(len(pts) - 1):
                                a, b = pts[seg_idx], pts[seg_idx + 1]
                                if self._point_in_rect_xy(a, self.box_start, self.box_curr) and self._point_in_rect_xy(b, self.box_start, self.box_curr):
                                    sel.add(('saved', pidx, seg_idx))
                        self.selected_segments = sel
                        if sel:
                            print(f"[INT] Seleccionados {len(sel)} segmentos por marco")
                        else:
                            print("[INT] Ningún segmento seleccionado en el rectángulo")
                    else:
                        # Rectángulo inválido: limpiar selección
                        self.selected_segments.clear()
                        print("[INT] Rectángulo de selección inválido - selección cancelada")

                    self.box_selecting = False
                    self.box_start = None
                    self.box_curr = None
            else:
                # Si no se puede iniciar selección por marco, informar al usuario
                if not self.box_selecting:
                    print("[INT] Selección por marco no disponible en el modo actual")

            self._draw_preview(current_pnt)
            return True

        return True

    # ---------- Inserción ----------
    def _get_segment_endpoints(self, seg: Tuple[str, int, int]) -> Tuple[Optional[AllplanGeo.Point3D], Optional[AllplanGeo.Point3D]]:
        kind, path_idx, seg_idx = seg
        if kind == 'active':
            if len(self.points) >= 2 and 0 <= seg_idx < len(self.points) - 1:
                return self.points[seg_idx], self.points[seg_idx+1]
            return None, None
        if kind == 'saved':
            if 0 <= path_idx < len(self.script_object.saved_paths):
                pts = self.script_object.saved_paths[path_idx]
                if len(pts) >= 2 and 0 <= seg_idx < len(pts) - 1:
                    return pts[seg_idx], pts[seg_idx+1]
        return None, None

    def _can_insert_here(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, t: float) -> bool:
        seg_len = self._segment_len(a, b)
        if seg_len < MIN_SEG_LEN_MM:
            return False
        t_min = MAX_EPS(MIN_INSERT_OFFSET_MM / max(seg_len, 1e-6))
        return (t > t_min) and (t < 1.0 - t_min)

    def _insert_on_segment(self, seg: Tuple[str, int, int], q: AllplanGeo.Point3D, keep_selection_left: bool = True):
        kind, path_idx, seg_idx = seg

        if kind == 'active':
            if not (0 <= seg_idx < len(self.points) - 1):
                return
            self.points.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))

            if self.selected_seg and self.selected_seg[0] == 'active':
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = ('active', -1, seg_idx if keep_selection_left else seg_idx + 1)
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ('active', -1, self.selected_seg[2] + 1)

        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return
            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return

            # Antes de insertar, guardar la información de sección del segmento original
            original_section_info = self._get_segment_section_info('saved', path_idx, seg_idx)
            original_end_point = None
            if original_section_info:
                # Guardar el punto final original antes de la inserción
                original_end_point = AllplanGeo.Point3D(pts[seg_idx + 1].X, pts[seg_idx + 1].Y, pts[seg_idx + 1].Z)

            # Insertar el nuevo punto
            pts.insert(seg_idx + 1, AllplanGeo.Point3D(q.X, q.Y, q.Z))

            # Después de la inserción, propagar la información de sección a ambos segmentos nuevos
            if original_section_info and original_end_point:
                self._propagate_section_info_after_split(path_idx, seg_idx, original_section_info, original_end_point)

            if self.selected_seg and self.selected_seg[0] == 'saved' and self.selected_seg[1] == path_idx:
                if self.selected_seg[2] == seg_idx:
                    self.selected_seg = ('saved', path_idx, seg_idx if keep_selection_left else seg_idx + 1)
                elif self.selected_seg[2] > seg_idx:
                    self.selected_seg = ('saved', path_idx, self.selected_seg[2] + 1)

        self.insert_preview_p = None
        self.insert_target = None

    # ---------- Borrar sección ----------
    def delete_selected_or_hovered_segment(self) -> bool:
        # Si no hay selección, reintenta con el hover actual; si tampoco hay, recalcula según modo
        target = self.selected_seg if self.selected_seg is not None else self.hover_seg

        if target is None:
            curr = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
            if self.create_mode:
                target = self._find_hover_segment(curr, preferred_kind='active')
            else:
                target = self._find_hover_segment(curr, preferred_kind='saved')

        if not target:
            print("[INT] Borrar sección: sin objetivo (ni seleccionado ni hover).")
            return False

        kind, path_idx, seg_idx = target
        print(f"[INT] Borrar sección -> objetivo: {target}")

        if kind == 'active':
            if len(self.points) < 2 or not (0 <= seg_idx < len(self.points) - 1):
                return False
            left  = self.points[:seg_idx+1]
            right = self.points[seg_idx+1:]

            if len(right) >= 2:
                self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])

            self.points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left]

        elif kind == 'saved':
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False
            pts = self.script_object.saved_paths[path_idx]
            if len(pts) < 2 or not (0 <= seg_idx < len(pts) - 1):
                return False

            left  = pts[:seg_idx+1]
            right = pts[seg_idx+1:]

            new_paths: List[List[AllplanGeo.Point3D]] = []
            if len(left) >= 2:
                new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in left])
            if len(right) >= 2:
                new_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in right])

            self.script_object.saved_paths.pop(path_idx)
            for offset, path in enumerate(new_paths):
                self.script_object.saved_paths.insert(path_idx + offset, path)

        else:
            return False

        self._clear_editing_state()
        self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())
        return True

    # ---------- Guardar / Finalizar ----------
    def on_cancel_function(self):
        """ESC: guardar si corresponde y CREAR INMEDIATO para no depender de execute()."""
        try:
            print("[INT] ESC/Finalizar: guardando y creando inmediatamente...")
            self.save_current_polyline()
            self.script_object._finalize_and_create_now()

            # Cleanup resources before finishing
            self._cleanup_resources()
            self._clear_editing_state()
            return OnCancelFunctionResult.CREATE_ELEMENTS
        except Exception as ex:
            print(f"[INT] Error during cancel function: {ex}")
            # Ensure cleanup happens even if save fails
            try:
                self._cleanup_resources()
                self._clear_editing_state()
            except:
                pass
            return OnCancelFunctionResult.CREATE_ELEMENTS

    def save_current_polyline(self):
        saved_successfully = False
        polyline_info = ""

        # Verificación automática de fusión: si los extremos están cerca de otros extremos, fusionar automáticamente
        if len(self.points) >= 2:
            start_extreme = self._find_nearby_extreme(self.points[0])
            end_extreme = self._find_nearby_extreme(self.points[-1])

            if start_extreme is not None or end_extreme is not None:
                # Priorizar el extremo más cercano (si ambos están cerca, elegir el que esté más cerca)
                candidates = []
                if start_extreme:
                    dist_start = self._dist_sq(self.points[0], self.script_object.saved_paths[start_extreme[0]][0 if start_extreme[1] == 'start' else -1])
                    candidates.append((dist_start, 0, start_extreme))  # 0 para start
                if end_extreme:
                    dist_end = self._dist_sq(self.points[-1], self.script_object.saved_paths[end_extreme[0]][0 if end_extreme[1] == 'start' else -1])
                    candidates.append((dist_end, -1, end_extreme))  # -1 para end

                if candidates:
                    # Elegir el candidato más cercano
                    candidates.sort(key=lambda x: x[0])
                    _, point_idx, (target_path, target_end) = candidates[0]

                    # Agregar la nueva polilínea temporalmente
                    new_path_idx = len(self.script_object.saved_paths)
                    self.script_object.saved_paths.append([AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points])

                    # Fusionar
                    self._merge_polylines(target_path, target_end, new_path_idx, 'start' if point_idx == 0 else 'end')

                    saved_successfully = True
                    polyline_info = f"Fusionada automáticamente con polilínea {target_path}"
                    print(f"[INT] Polilínea fusionada automáticamente con {target_path} en extremo {target_end}")

                    # Limpiar y salir
                    self.points.clear()
                    self._clear_editing_state()
                    self._clear_preview()
                    self._cleanup_orphaned_segments()
                    return

        # Verificación de vértices intermedios: si cerca, mover pero no fusionar
        if len(self.points) >= 2:
            start_vertex = self._find_nearby_vertex(self.points[0])
            end_vertex = self._find_nearby_vertex(self.points[-1])

            if start_vertex is not None or end_vertex is not None:
                candidates = []
                if start_vertex:
                    dist_start = self._dist_sq(self.points[0], self.script_object.saved_paths[start_vertex[0]][start_vertex[1]])
                    candidates.append((dist_start, 0, start_vertex))  # 0 para start
                if end_vertex:
                    dist_end = self._dist_sq(self.points[-1], self.script_object.saved_paths[end_vertex[0]][end_vertex[1]])
                    candidates.append((dist_end, -1, end_vertex))  # -1 para end

                if candidates:
                    # Elegir el candidato más cercano
                    candidates.sort(key=lambda x: x[0])
                    _, point_idx, (target_path, target_vertex_idx) = candidates[0]

                    # Solo mover, no fusionar
                    target_point = self.script_object.saved_paths[target_path][target_vertex_idx]
                    current_point = self.points[point_idx]
                    delta_x = target_point.X - current_point.X
                    delta_y = target_point.Y - current_point.Y
                    delta_z = target_point.Z - current_point.Z

                    # Trasladar toda la polilínea activa
                    for p in self.points:
                        p.X += delta_x
                        p.Y += delta_y
                        p.Z += delta_z

                    print(f"[INT] Polilínea movida al vértice intermedio {target_vertex_idx} de polilínea {target_path}")

        # Si estamos EXTENDIENDO una guardada, fusiona en su lugar
        if self.extend_target is not None and len(self.points) >= 2:
            pidx, side = self.extend_target
            if 0 <= pidx < len(self.script_object.saved_paths):
                base = self.script_object.saved_paths[pidx]
                if side == 'end':
                    # points = [anchor, p1, p2, ...] -> añadir p1.. al final
                    new_points = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points[1:]]
                    base.extend(new_points)

                    # Crear segmentos con sección por defecto para los nuevos segmentos
                    self._create_default_segments_for_extension(pidx, len(base) - len(new_points), len(base))

                else:  # 'start'
                    # Prepend en orden correcto: ... p2, p1, anchor, base...
                    prepend = list(reversed(self.points[1:]))
                    new_path = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in prepend] + base
                    self.script_object.saved_paths[pidx] = new_path

                    # Crear segmentos con sección por defecto para los nuevos segmentos
                    self._create_default_segments_for_extension(pidx, 0, len(prepend))

                print(f"[INT] Extensión fusionada en polilínea guardada #{pidx} ({side}).")
                saved_successfully = True
                polyline_info = f"Polilínea #{pidx + 1} extendida ({side})\nNuevos puntos: {len(self.points) - 1}"
            self.extend_target = None

        else:
            # Comportamiento normal: guardar como nueva si hay ≥2 puntos
            if len(self.points) >= 2:
                new_path = [AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in self.points]
                self.script_object.saved_paths.append(new_path)

                # Crear segmentos con sección por defecto
                self._create_default_segments_for_new_path(len(self.script_object.saved_paths) - 1)

                saved_successfully = True
                polyline_info = f"Nueva polilínea guardada #{len(self.script_object.saved_paths)}\nPuntos: {len(self.points)}"

        # Mostrar popup de confirmación si se guardó exitosamente
        if saved_successfully:
            total_polylines = len(self.script_object.saved_paths)
            message = f"✅ Polilínea guardada exitosamente!\n\n{polyline_info}\n\nTotal de polilíneas: {total_polylines}"
            PythonUtility.ShowMessageBox(message, PythonUtility.MB_OK)

        # Reset temporal de la activa
        self.points.clear()
        self._clear_editing_state()
        self._clear_preview()

        # Periodic cleanup of orphaned segments to prevent accumulation
        self._cleanup_orphaned_segments()

    def _create_default_segments_for_new_path(self, path_idx: int):
        """Crea segmentos con sección por defecto para una nueva polilínea"""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        default_diameter = self._get_default_diameter()
        system = self._get_current_system()

        for seg_idx in range(len(pts) - 1):
            label = self._format_segment_label(default_diameter, system)
            segment_info = {
                'points': [pts[seg_idx], pts[seg_idx + 1]],
                'diameter': default_diameter,
                'section_type': f'{int(default_diameter)}mm',
                'system': system,
                'label': label,
                'path_idx': path_idx,
                'seg_idx': seg_idx
            }
            self.script_object.saved_segments.append(segment_info)

    def _create_default_segments_for_extension(self, path_idx: int, start_seg: int, end_seg: int):
        """Crea segmentos con sección por defecto para una extensión"""
        if not (0 <= path_idx < len(self.script_object.saved_paths)):
            return

        pts = self.script_object.saved_paths[path_idx]
        default_diameter = self._get_default_diameter()
        system = self._get_current_system()

        for seg_idx in range(start_seg, min(end_seg, len(pts) - 1)):
            # Solo crear si no existe ya un segmento para esta posición
            existing = self._get_segment_section_info('saved', path_idx, seg_idx)
            if not existing:
                label = self._format_segment_label(default_diameter, system)
                segment_info = {
                    'points': [pts[seg_idx], pts[seg_idx + 1]],
                    'diameter': default_diameter,
                    'section_type': f"{default_diameter}mm",
                    'system': system,
                    'label': label,
                    'path_idx': path_idx,
                    'seg_idx': seg_idx
                }
                self.script_object.saved_segments.append(segment_info)

    def _merge_polylines(self, path1: int, end1: str, path2: int, end2: str):
        """Fusiona dos polilíneas conectándolas por sus extremos, trasladando la segunda (nueva) para que coincida con la primera (existente)"""
        if path1 == path2:
            return

        pts1 = self.script_object.saved_paths[path1]
        pts2 = self.script_object.saved_paths[path2]

        # Determinar puntos extremos
        end1_point = pts1[0] if end1 == 'start' else pts1[-1]
        end2_point = pts2[0] if end2 == 'start' else pts2[-1]

        # Calcular traslación para que end2_point coincida con end1_point (trasladar path2 hacia path1)
        delta_x = end1_point.X - end2_point.X
        delta_y = end1_point.Y - end2_point.Y
        delta_z = end1_point.Z - end2_point.Z

        # Trasladar pts2
        translated_pts2 = [AllplanGeo.Point3D(p.X + delta_x, p.Y + delta_y, p.Z + delta_z) for p in pts2]

        # Determinar el orden de concatenación y evitar puntos duplicados
        if end1 == 'end' and end2 == 'start':
            new_pts = pts1 + translated_pts2[1:]  # pts1 termina en end1_point, translated_pts2 empieza en end1_point
        elif end1 == 'start' and end2 == 'end':
            new_pts = list(reversed(translated_pts2[:-1])) + pts1  # translated_pts2 termina en end1_point, pts1 empieza en end1_point
        elif end1 == 'end' and end2 == 'end':
            new_pts = pts1 + list(reversed(translated_pts2[:-1]))  # Ambos terminan en end1_point
        elif end1 == 'start' and end2 == 'start':
            new_pts = list(reversed(translated_pts2)) + pts1[1:]  # Ambos empiezan en end1_point
        else:
            return  # Caso no válido

        # Remove consecutive duplicate points
        i = 0
        while i < len(new_pts) - 1:
            if self._points_equal(new_pts[i], new_pts[i+1]):
                del new_pts[i+1]
            else:
                i += 1

        # Asegurar que path1 < path2 para remover el mayor primero
        if path1 > path2:
            path1, path2 = path2, path1

        # Crear nuevos segmentos preservando información de sección
        new_segments = []
        for i in range(len(new_pts) - 1):
            # Intentar encontrar información de sección del segmento correspondiente
            existing = None
            if end1 == 'end' and end2 == 'start':
                if i < len(pts1) - 1:
                    existing = self._get_segment_section_info('saved', path1, i)
                else:
                    seg_idx_in_path2 = i - (len(pts1) - 1)
                    existing = self._get_segment_section_info('saved', path2, seg_idx_in_path2)
            # Para otros casos, simplificar: usar valores por defecto por ahora
            # TODO: implementar mapeo completo para todos los casos

            if existing:
                segment_info = {
                    'points': [new_pts[i], new_pts[i+1]],
                    'diameter': existing['diameter'],
                    'section_type': existing['section_type'],
                    'system': existing['system'],
                    'label': existing['label'],
                    'path_idx': path1,
                    'seg_idx': i
                }
            else:
                # Valores por defecto
                default_diameter = self._get_default_diameter()
                system = self._get_current_system()
                label = self._format_segment_label(default_diameter, system)
                segment_info = {
                    'points': [new_pts[i], new_pts[i+1]],
                    'diameter': default_diameter,
                    'section_type': f"{default_diameter}mm",
                    'system': system,
                    'label': label,
                    'path_idx': path1,
                    'seg_idx': i
                }
            new_segments.append(segment_info)

        # Remover segmentos de path1 y path2
        self.script_object.saved_segments = [
            s for s in self.script_object.saved_segments
            if s.get('path_idx') not in (path1, path2)
        ]

        # Agregar nuevos segmentos
        self.script_object.saved_segments.extend(new_segments)

        # Actualizar path_idx de segmentos > path2
        for s in self.script_object.saved_segments:
            if s.get('path_idx', -1) > path2:
                s['path_idx'] -= 1

        # Reemplazar path1 con la nueva polilínea
        self.script_object.saved_paths[path1] = new_pts

        # Remover path2
        self.script_object.saved_paths.pop(path2)

        print(f"[INT] Polilíneas fusionadas con traslación: {path1} y {path2} -> nueva en {path1}")

        print(f"[INT] Polilíneas fusionadas con traslación: {path1} y {path2} -> nueva en {path1}")

    def _get_default_diameter(self) -> float:
        """Obtiene el diámetro por defecto usando la opción actualmente seleccionada en la paleta de gestión de secciones"""
        try:
            # Usar el diámetro actualmente seleccionado en la paleta de gestión de secciones
            return self._get_diameter_to_apply()
        except Exception as ex:
            print(f"[INT] Error obteniendo diámetro por defecto desde paleta: {ex}")
            return 110.0  # Fallback seguro

    # ---------- Preview ----------
    def _clear_preview(self):
        """Clear all preview elements completely"""
        try:
            # Create empty elements list to clear the preview
            empty_elems: List[AllplanBasisElements.ModelElement3D] = []

            # Use DrawElementPreview with empty list to clear previous previews
            AllplanBaseElements.DrawElementPreview(
                self.coord_input.GetInputViewDocument(),
                AllplanGeo.Matrix3D(),
                empty_elems,
                True,  # Clear previous elements
                None
            )

            print("[INT] Preview elements cleared")

        except Exception as ex:
            print(f"[INT] Error clearing preview: {ex}")

    def on_preview_draw(self):
        self._sync_insert_mode_from_palette()
        hover = self.coord_input.GetCurrentPoint(self.current_point).GetPoint()
        self._draw_preview(hover)

    def on_mouse_leave(self):
        self.on_preview_draw()

    def _line_with_zbias(self, a: AllplanGeo.Point3D, b: AllplanGeo.Point3D, z_bias: float):
        pa = AllplanGeo.Point3D(a.X, a.Y, a.Z + z_bias)
        pb = AllplanGeo.Point3D(b.X, b.Y, b.Z + z_bias)
        return AllplanGeo.Line3D(pa, pb)


    def _draw_preview(self, hover: Optional[AllplanGeo.Point3D]):
        elems: List[AllplanBasisElements.ModelElement3D] = []

        base_prop   = self._clone_properties(self.com_prop)
        handle_prop = self._clone_properties(self.com_prop)
        handle_prop.Color = HANDLE_COLOR_IDX  # amarillo

        saved_prop  = self._clone_properties(self.com_prop)
        saved_prop.Color = PREVIEW_SAVED_COLOR  # Color verde solo para preview de polilíneas guardadas

        seg_hover_prop = self._clone_properties(self.com_prop)
        seg_hover_prop.Color = SEGMENT_HOVER_COLOR
        seg_hover_prop.ColorByLayer = False
        seg_hover_prop.PenByLayer = False
        seg_hover_prop.StrokeByLayer = False
        try:
            seg_hover_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass

        seg_sel_prop = self._clone_properties(self.com_prop)
        seg_sel_prop.Color = SEGMENT_SEL_COLOR
        seg_sel_prop.ColorByLayer = False
        seg_sel_prop.PenByLayer = False
        seg_sel_prop.StrokeByLayer = False
        try:
            seg_sel_prop.Pen = max(SEGMENT_OVERLAY_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass

        ins_prev_prop = self._clone_properties(self.com_prop)
        ins_prev_prop.Color = INSERT_PREVIEW_COLOR

        branch_anchor_prop = self._clone_properties(self.com_prop)
        branch_anchor_prop.Color = BRANCH_ANCHOR_COLOR

        # Midpoints props (con pen propio y sin ByLayer)
        mid_prop = self._clone_properties(self.com_prop)
        mid_prop.Color = MIDPOINT_COLOR
        mid_prop.PenByLayer = False
        mid_prop.ColorByLayer = False
        mid_prop.StrokeByLayer = False
        try:
            mid_prop.Pen = max(MIDPOINT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass
        mid_size = HANDLE_SIZE * MIDPOINT_SIZE_FACTOR

        # Rectángulo de selección
        rect_prop = self._clone_properties(self.com_prop)
        rect_prop.Color = RECT_COLOR
        rect_prop.PenByLayer = False
        rect_prop.ColorByLayer = False
        rect_prop.StrokeByLayer = False
        try:
            rect_prop.Pen = max(RECT_PEN, getattr(self.com_prop, "Pen", 1))
        except Exception:
            pass

        # Guardadas
        for path_idx, pts in enumerate(self.script_object.saved_paths):
            if len(pts) >= 2:
                # Dibujar segmentos individuales con color de selección si están seleccionados (por click o por marco)
                for seg_idx in range(len(pts) - 1):
                    a, b = pts[seg_idx], pts[seg_idx + 1]
                    # ¿Está seleccionado por click o por marco?
                    is_selected = False
                    if self.selected_seg and self.selected_seg[0] == 'saved' and self.selected_seg[1] == path_idx and self.selected_seg[2] == seg_idx:
                        is_selected = True
                    if ('saved', path_idx, seg_idx) in getattr(self, 'selected_segments', set()):
                        is_selected = True
                    # ¿Está hover?
                    is_hovered = self.hover_seg and self.hover_seg[0] == 'saved' and self.hover_seg[1] == path_idx and self.hover_seg[2] == seg_idx
                    # Propiedades
                    if is_selected:
                        prop = seg_sel_prop
                    elif is_hovered and not self.is_dragging:
                        prop = seg_hover_prop
                    else:
                        # Verificar si este segmento tiene sección configurada
                        section_info = self._get_segment_section_info('saved', path_idx, seg_idx)
                        if section_info:
                            prop = self._clone_properties(self.com_prop)
                            # Aplicar color específico según diámetro y sistema
                            diameter = section_info.get('diameter', 110.0)
                            system = section_info.get('system', 'Pluvial')
                            prop.Color = self._get_section_color_for_preview(diameter, system)
                            prop.ColorByLayer = False
                        else:
                            prop = saved_prop
                    # Crear línea del segmento
                    line = AllplanGeo.Line3D(a, b)
                    elems.append(AllplanBasisElements.ModelElement3D(prop, line))
                    # Etiqueta de texto en el punto medio si hay info de sección con label
                    if is_selected and self._get_segment_section_info('saved', path_idx, seg_idx) and self._get_segment_section_info('saved', path_idx, seg_idx).get('label'):
                        self._add_text_label(elems, a, b, str(self._get_segment_section_info('saved', path_idx, seg_idx)['label']))

                # Midpoints (guardadas)
                for si in range(len(pts) - 1):
                    a, b = pts[si], pts[si+1]
                    mp = self._midpoint(a, b)
                    is_selected = False
                    if self.selected_seg and self.selected_seg[0] == 'saved' and self.selected_seg[1] == path_idx and self.selected_seg[2] == si:
                        is_selected = True
                    if ('saved', path_idx, si) in getattr(self, 'selected_segments', set()):
                        is_selected = True
                    is_hovered = self.hover_seg and self.hover_seg[0] == 'saved' and self.hover_seg[1] == path_idx and self.hover_seg[2] == si
                    if is_selected:
                        elems.extend(self._create_cross_marker(mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    elif is_hovered and not self.is_dragging:
                        elems.extend(self._create_cross_marker(mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    else:
                        elems.extend(self._create_cross_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

                # Vértices de polilíneas guardadas: handlers circulares (igual estilo que activa)
                for vidx, vpt in enumerate(pts):
                    size = HANDLE_SIZE * 0.60
                    # si el vértice está siendo arrastrado (guardado), agrandar
                    if self.saved_dragging is not None and self.saved_dragging == (path_idx, vidx):
                        size = HANDLE_SIZE * DRAG_SCALE
                    # si hay hover del punto guardado
                    if self.saved_hover_point is not None and self.saved_hover_point[0] == path_idx and self.saved_hover_point[1] == vidx and not self.is_dragging:
                        size = HANDLE_SIZE * HOVER_SCALE
                    elems.extend(self._create_point_marker(vpt, handle_prop, size))

        # Activa + rubber-band (si hay activa)
        if self.points:
            poly = AllplanGeo.Polyline3D()
            for pt in self.points:
                poly += pt
            if hover is not None and not self.is_dragging and self.hover_seg is None and self.create_mode:
                poly += hover
            elems.append(AllplanBasisElements.ModelElement3D(base_prop, poly))

            # Handles (activa)
            for idx, pt in enumerate(self.points):
                size = HANDLE_SIZE * 0.65
                if idx == self.hover_index and not self.is_dragging:
                    size = HANDLE_SIZE * HOVER_SCALE
                if idx == self.drag_index and self.is_dragging:
                    size = HANDLE_SIZE * DRAG_SCALE
                elems.extend(self._create_point_marker(pt, handle_prop, size))

            # Selección/hover en activa (con overlay + z-bias)
            selected_i = self.selected_seg[2] if (self.selected_seg and self.selected_seg[0] == 'active') else -1
            hovered_i  = self.hover_seg[2]    if (self.hover_seg    and self.hover_seg[0]    == 'active') else -1

            if selected_i != -1 and 0 <= selected_i < len(self.points) - 1:
                a, b = self.points[selected_i], self.points[selected_i+1]
                elems.append(AllplanBasisElements.ModelElement3D(
                    seg_sel_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)
                ))

            if self.hover_seg and self.hover_seg[0] == 'active' and not self.is_dragging:
                si = self.hover_seg[2]
                if si != selected_i and 0 <= si < len(self.points) - 1:
                    a, b = self.points[si], self.points[si+1]
                    elems.append(AllplanBasisElements.ModelElement3D(
                        seg_hover_prop, self._line_with_zbias(a, b, SEGMENT_OVERLAY_Z_BIAS)
                    ))

            # Midpoints (activa) como cruzetas
            if len(self.points) >= 2:
                for si in range(len(self.points) - 1):
                    a, b = self.points[si], self.points[si+1]
                    mp = self._midpoint(a, b)
                    if si == selected_i:
                        elems.extend(self._create_cross_marker(mp, seg_sel_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    elif si == hovered_i and not self.is_dragging:
                        elems.extend(self._create_cross_marker(mp, seg_hover_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))
                    else:
                        elems.extend(self._create_cross_marker(mp, mid_prop, mid_size, z_bias=MIDPOINT_Z_BIAS))

        # Punto fantasma de inserción (checkbox ON)
        if self.insert_mode and self.insert_preview_p is not None and self.insert_target is not None:
            elems.extend(self._create_point_marker(self.insert_preview_p, ins_prev_prop, HANDLE_SIZE * 0.95))

        # Rectángulo de selección (si está activo)
        if self.box_selecting and self.box_start is not None and self.box_curr is not None:
            a = self.box_start; b = self.box_curr
            p1 = AllplanGeo.Point3D(a.X, a.Y, a.Z)
            p2 = AllplanGeo.Point3D(b.X, a.Y, a.Z)
            p3 = AllplanGeo.Point3D(b.X, b.Y, a.Z)
            p4 = AllplanGeo.Point3D(a.X, b.Y, a.Z)
            for (s, e) in [(p1,p2),(p2,p3),(p3,p4),(p4,p1)]:
                elems.append(AllplanBasisElements.ModelElement3D(rect_prop, AllplanGeo.Line3D(s, e)))

        # Feedback visual para fusión de polilíneas (línea cyan)
        if self.saved_dragging is not None and hover is not None:
            pidx, vidx = self.saved_dragging
            pts = self.script_object.saved_paths[pidx]
            if vidx == 0 or vidx == len(pts) - 1:
                merge_target = self._find_nearby_extreme(hover, exclude_path=pidx)
                if merge_target:
                    target_pidx, target_end = merge_target
                    target_pts = self.script_object.saved_paths[target_pidx]
                    target_point = target_pts[0] if target_end == 'start' else target_pts[-1]
                    # Dibujar línea cyan entre hover y target_point
                    cyan_prop = self._clone_properties(self.com_prop)
                    cyan_prop.Color = 6  # cyan
                    elems.append(AllplanBasisElements.ModelElement3D(cyan_prop, AllplanGeo.Line3D(hover, target_point)))

        # --- FEEDBACK VISUAL: cruceta grande y roja sobre el mouse si el ángulo es válido ---
        # Solo en modo creación, con Limitar ángulos activo, y si hover existe
        if self.create_mode and hover is not None:
            limit_angles = self._get_palette_limit_angles()
            # Solo mostrar si el ángulo sería válido
            if limit_angles:
                if len(self.points) < 1:
                    show_cross = True
                else:
                    last_point = self.points[-1]
                    dx = hover.X - last_point.X
                    dy = hover.Y - last_point.Y
                    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
                        show_cross = False
                    else:
                        angle_deg = (math.degrees(math.atan2(dy, dx)) % 360.0)
                        valid_angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
                        tolerance = 1.0
                        if not any(abs(angle_deg - va) <= tolerance for va in valid_angles):
                            show_cross = False
                        elif len(self.points) >= 2:
                            prev = self.points[-2]
                            v1x = last_point.X - prev.X
                            v1y = last_point.Y - prev.Y
                            v2x = hover.X - last_point.X
                            v2y = hover.Y - last_point.Y
                            ang1 = math.degrees(math.atan2(v1y, v1x)) % 360.0
                            ang2 = angle_deg
                            delta = abs(ang2 - ang1)
                            if delta > 180.0:
                                delta = 360.0 - delta
                            if abs((180.0 - delta) - 45.0) <= tolerance:
                                show_cross = False
                            else:
                                show_cross = True
                        else:
                            show_cross = True
                if show_cross:
                    # Handler grande y rojo
                    cross_size = HANDLE_SIZE * 1.2
                    cross_prop = self._clone_properties(self.com_prop)
                    cross_prop.Color = 5  # azul
                    cross_prop.PenByLayer = False
                    cross_prop.ColorByLayer = False
                    cross_prop.StrokeByLayer = False
                    cross_elems = self._create_cross_marker(hover, cross_prop, cross_size, z_bias=4.0)
                    elems.extend(cross_elems)

        AllplanBaseElements.DrawElementPreview(
            self.coord_input.GetInputViewDocument(),
            AllplanGeo.Matrix3D(),
            elems,
            True,  # Clear previous elements to prevent memory accumulation
            None
        )

    # ---------- Gestión de Secciones ----------
    def apply_section_to_selected(self):
        """Aplica la sección seleccionada en la paleta a los segmentos seleccionados"""
        try:
            # Obtener el diámetro a aplicar
            diameter = self._get_diameter_to_apply()
            if diameter <= 0:
                print("[INT] Error: diámetro inválido")
                return False

            applied_count = 0

            # Aplicar a segmentos seleccionados por marco
            if self.selected_segments:
                for kind, path_idx, seg_idx in self.selected_segments:
                    if kind == 'saved':
                        if self._apply_diameter_to_segment(path_idx, seg_idx, diameter):
                            applied_count += 1

            # Si no hay selección por marco, aplicar al segmento hover/seleccionado
            elif self.selected_seg or self.hover_seg:
                target = self.selected_seg or self.hover_seg
                kind, path_idx, seg_idx = target
                if kind == 'saved':
                    if self._apply_diameter_to_segment(path_idx, seg_idx, diameter):
                        applied_count += 1

            if applied_count > 0:
                print(f"[INT] Aplicado diámetro {diameter}mm a {applied_count} segmento(s)")
                self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())
                return True
            else:
                print("[INT] No hay segmentos seleccionados para aplicar sección")
                print("[INT] AYUDA: Para seleccionar segmentos:")
                print("[INT] - Haz clic en un segmento de polilínea guardada")
                print("[INT] - O arrastra para crear un marco de selección")
                return False

        except Exception as ex:
            print(f"[INT] Error aplicando sección: {ex}")
            return False

    def _get_diameter_to_apply(self) -> float:
        """Obtiene el diámetro a aplicar desde la paleta"""
        try:
            # Primero verificar si hay diámetro personalizado
            custom_diameter = self._safe_get_palette_property("DiametroPersonalizado")

            if custom_diameter is not None and custom_diameter > 0:
                return float(custom_diameter)

            # Determinar el tipo de saneamiento para usar el control correcto
            saneamiento_type = self._safe_get_palette_property("Saneamiento")

            selected_diameter = None

            if saneamiento_type is not None:
                if saneamiento_type == 0:  # Pluvial
                    selected_diameter = self._safe_get_palette_property("DiametroAplicarPluvial")
                    if selected_diameter is None:
                        # Usar diámetro por defecto para pluvial
                        return 110.0
                else:  # Fecal (saneamiento_type == 1)
                    # Para fecal, intentar primero el control específico
                    selected_diameter = self._safe_get_palette_property("DiametroAplicarFecal")

                    # Si no existe, intentar el control general de diámetro
                    if selected_diameter is None:
                        selected_diameter = self._safe_get_palette_property("Diametro")

                    # Si tampoco existe, usar diámetro por defecto para fecal
                    if selected_diameter is None:
                        return 40.0

            # Si tenemos un valor específico válido, usarlo
            if selected_diameter is not None and selected_diameter > 0:
                return float(selected_diameter)

            # Fallback al control original por compatibilidad (solo si los otros no funcionaron)
            fallback_diameter = self._safe_get_palette_property("DiametroAplicar")

            if fallback_diameter is not None and fallback_diameter > 0:
                return float(fallback_diameter)

            # Como último recurso, usar el diámetro por defecto del tipo de saneamiento
            default_diameter = self._get_default_diameter()
            return default_diameter

        except Exception as ex:
            print(f"[INT] Error obteniendo diámetro: {ex}")
            return 110.0  # Valor seguro por defecto

    def _apply_diameter_to_segment(self, path_idx: int, seg_idx: int, diameter: float) -> bool:
        """Aplica un diámetro específico a un segmento guardado"""
        try:
            if not (0 <= path_idx < len(self.script_object.saved_paths)):
                return False

            pts = self.script_object.saved_paths[path_idx]
            if not (0 <= seg_idx < len(pts) - 1):
                return False

            # Obtener los puntos del segmento actual
            point1 = pts[seg_idx]
            point2 = pts[seg_idx + 1]

            # Obtener sistema actual y generar etiqueta
            system = self._get_current_system()
            label = self._format_segment_label(diameter, system)

            # Buscar si ya existe una configuración para este segmento
            segment_found = False
            for i, existing_segment in enumerate(self.script_object.saved_segments):
                existing_points = existing_segment['points']
                if (len(existing_points) >= 2 and
                    self._points_equal(existing_points[0], point1) and
                    self._points_equal(existing_points[1], point2)):
                    # Actualizar el segmento existente
                    self.script_object.saved_segments[i] = {
                        'points': [point1, point2],
                        'diameter': diameter,
                        'section_type': f"{diameter}mm",
                        'system': system,
                        'label': label
                    }
                    segment_found = True
                    print(f"[INT] Segmento {path_idx}-{seg_idx} actualizado con diámetro {diameter}mm, sistema {system}")
                    break

        # Si no se encontró, agregar como nuevo
            if not segment_found:
                segment_info = {
                    'points': [point1, point2],
                    'diameter': diameter,
            'section_type': f"{diameter}mm",
            'system': system,
            'label': label
                }
                self.script_object.saved_segments.append(segment_info)
                print(f"[INT] Segmento {path_idx}-{seg_idx} configurado con diámetro {diameter}mm, sistema {system}")

            # Forzar redibujado para actualizar las etiquetas
            self._draw_preview(self.coord_input.GetCurrentPoint(self.current_point).GetPoint())

            return True

        except Exception as ex:
            print(f"[INT] Error aplicando diámetro a segmento: {ex}")
            return False

    def show_sections_info(self):
        """Muestra información de las secciones configuradas"""
        try:
            print("[INT] === INFORMACIÓN DE SECCIONES ===")

            # Información general
            total_paths = len(self.script_object.saved_paths)
            total_segments_with_section = len(self.script_object.saved_segments)

            print(f"[INT] Polilíneas guardadas: {total_paths}")
            print(f"[INT] Segmentos con sección configurada: {total_segments_with_section}")

            # Para debugging: mostrar todos los segmentos
            for i, segment_info in enumerate(self.script_object.saved_segments):
                diameter = segment_info.get('diameter', 0)
                points = segment_info.get('points', [])
                if len(points) >= 2:
                    p1 = points[0]
                    p2 = points[1]
                    print(f"[INT] Segment {i}: {diameter}mm from ({p1.X:.1f},{p1.Y:.1f}) to ({p2.X:.1f},{p2.Y:.1f})")

            if not self.script_object.saved_segments:
                print("[INT] No hay segmentos con sección configurada")
                # Mostrar información de polilíneas sin sección
                total_segments_available = sum(len(pts) - 1 for pts in self.script_object.saved_paths if len(pts) >= 2)
                print(f"[INT] Segmentos disponibles para configurar: {total_segments_available}")
                return

            # Agrupar por diámetro
            from collections import defaultdict
            sections_by_diameter = defaultdict(int)

            for segment_info in self.script_object.saved_segments:
                diameter = segment_info['diameter']
                sections_by_diameter[diameter] += 1

            print(f"[INT] Total de segmentos con sección: {len(self.script_object.saved_segments)}")
            for diameter, count in sorted(sections_by_diameter.items()):
                print(f"[INT] - Diámetro {diameter}mm: {count} segmento(s)")

            # Información de estado actual
            print(f"[INT] Estado actual:")
            print(f"[INT] - Selección por marco: {len(self.selected_segments) if hasattr(self, 'selected_segments') else 0} segmentos")
            print(f"[INT] - Segmento seleccionado: {'Sí' if self.selected_seg else 'No'}")
            print(f"[INT] - Segmento hover: {'Sí' if self.hover_seg else 'No'}")

            # Actualizar texto en la paleta si es posible
            try:
                info_text = f"Segmentos: {len(self.script_object.saved_segments)}\n"
                for diameter, count in sorted(sections_by_diameter.items()):
                    info_text += f"⌀{diameter}mm: {count}\n"

                # Intentar actualizar algún campo de texto en la paleta
                if hasattr(self.script_object.build_ele, "FirstText"):
                    self.script_object.build_ele.FirstText.value = info_text.strip()

            except Exception as ex:
                print(f"[INT] No se pudo actualizar texto en paleta: {ex}")

            return True

        except Exception as ex:
            print(f"[INT] Error mostrando información de secciones: {ex}")
            return False

    def _get_segment_section_info(self, kind: str, path_idx: int, seg_idx: int) -> Optional[dict]:
        """Obtiene información de sección para un segmento específico"""
        if kind != 'saved':
            return None

        # Buscar en saved_segments usando path_idx y seg_idx si están presentes
        for segment_info in self.script_object.saved_segments:
            if (segment_info.get('path_idx') == path_idx and
                segment_info.get('seg_idx') == seg_idx):
                return segment_info

        # Fallback: buscar por puntos (para compatibilidad)
        if 0 <= path_idx < len(self.script_object.saved_paths):
            pts = self.script_object.saved_paths[path_idx]
            if 0 <= seg_idx < len(pts) - 1:
                expected_p1 = pts[seg_idx]
                expected_p2 = pts[seg_idx + 1]

                for segment_info in self.script_object.saved_segments:
                    points = segment_info.get('points', [])
                    if (len(points) >= 2 and
                        self._points_equal(points[0], expected_p1) and
                        self._points_equal(points[1], expected_p2)):
                        return segment_info

        return None

    def _points_equal(self, p1: AllplanGeo.Point3D, p2: AllplanGeo.Point3D, tolerance: float = 1e-6) -> bool:
        """Compara dos puntos con tolerancia"""
        return (abs(p1.X - p2.X) < tolerance and
                abs(p1.Y - p2.Y) < tolerance and
                abs(p1.Z - p2.Z) < tolerance)

    def _get_section_properties(self, diameter: float):
        """Obtiene las propiedades visuales según el diámetro del segmento"""
        prop = self._clone_properties(self.com_prop)
        # Usar propiedades por defecto del sistema (sin asignar colores específicos)
        return prop

    def _get_section_color_for_preview(self, diameter: float, system: str) -> int:
        """
        Obtiene el color específico para preview según diámetro y sistema.
        - Pluvial 110mm: color 7
        - Fecal 110mm: color 4
        - Fecal 40mm: color 66
        - Fecal 25mm: color 70
        """
        try:
            diameter_int = int(round(diameter))
            system_lower = system.lower().strip()

            if system_lower.startswith('pluvial') and diameter_int == 110:
                return 7
            elif system_lower.startswith('fecal'):
                if diameter_int == 110:
                    return 4
                elif diameter_int == 40:
                    return 66
                elif diameter_int == 25:
                    return 70

            # Color por defecto si no coincide con ninguna especificación
            return PREVIEW_SAVED_COLOR

        except Exception:
            return PREVIEW_SAVED_COLOR

    # ---------- Utilidades de Paleta (Sincronización Segura) ----------
    def _safe_get_palette_property(self, property_name: str, default_value=None):
        """Obtiene una propiedad de la paleta de manera segura"""
        try:
            if not hasattr(self.script_object, 'build_ele') or self.script_object.build_ele is None:
                return default_value

            if not hasattr(self.script_object.build_ele, property_name):
                return default_value

            prop = getattr(self.script_object.build_ele, property_name)

            if hasattr(prop, "value"):
                return prop.value
            else:
                return prop
        except Exception as ex:
            print(f"[INT] Error obteniendo propiedad {property_name}: {ex}")
            return default_value

    def _safe_set_palette_property(self, property_name: str, value) -> bool:
        """Establece una propiedad de la paleta de manera segura"""
        try:
            if not hasattr(self.script_object, 'build_ele') or self.script_object.build_ele is None:
                return False

            if not hasattr(self.script_object.build_ele, property_name):
                return False

            prop = getattr(self.script_object.build_ele, property_name)
            if hasattr(prop, "value"):
                prop.value = value
            else:
                setattr(self.script_object.build_ele, property_name, value)
            return True
        except Exception as ex:
            print(f"[INT] Error estableciendo propiedad {property_name}: {ex}")
            return False

    # ---------- Helpers ----------
    def _clone_properties(self, src_prop):
        dst = AllplanBaseElements.CommonProperties()
        dst.GetGlobalProperties()
        for name in ("Color", "Pen", "Stroke", "ColorByLayer", "PenByLayer", "StrokeByLayer", "Layer"):
            try:
                setattr(dst, name, getattr(src_prop, name))
            except Exception:
                pass
        return dst

    def _get_current_system(self) -> str:
        """Devuelve el sistema actual en texto ('Pluvial'|'Fecal') según la paleta."""
        try:
            saneamiento_type = self._safe_get_palette_property("Saneamiento")

            if saneamiento_type is not None:
                system = "Pluvial" if saneamiento_type == 0 else "Fecal"
                return system
        except Exception as ex:
            print(f"[INT] Error en _get_current_system: {ex}")

        return "Pluvial"

    def _format_segment_label(self, diameter: float, system: str) -> str:
        """Formatea la etiqueta de segmento: D110 P (pluvial) o D25 F, D40 F, D110 F (fecal)."""
        try:
            d = int(round(float(diameter)))
        except Exception:
            d = int(diameter) if isinstance(diameter, (int, float)) else 0

        # Determinar la letra del sistema
        if system.strip().lower().startswith('fecal'):
            label = f"D{d} F"
        else:
            label = f"D{d} P"

        return label

    def _create_cross_marker(self, point, properties, size, z_bias: float = 0.0):
        """Dibuja una cruz (cruzeta) en torno al punto, en ejes X/Y y una pequeña marca Z."""
        half = max(size * 0.5, 0.1)
        px = getattr(point, 'X', 0.0)
        py = getattr(point, 'Y', 0.0)
        pz = getattr(point, 'Z', 0.0) + (z_bias or 0.0)

        p1 = AllplanGeo.Point3D(px - half, py,        pz)
        p2 = AllplanGeo.Point3D(px + half, py,        pz)
        p3 = AllplanGeo.Point3D(px,        py - half, pz)
        p4 = AllplanGeo.Point3D(px,        py + half, pz)
        p5 = AllplanGeo.Point3D(px,        py,        pz - half)
        p6 = AllplanGeo.Point3D(px,        py,        pz + half)

        return [
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p1, p2)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p3, p4)),
            AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(p5, p6)),
        ]

    def _create_point_marker(self, point, properties, size, z_bias: float = 0.0):
        # Draw circular handler marker in XY plane around the given point.
        # Replaces previous cross-shaped marker for better UX.
        import math
        radius = max(size * 0.5, 0.1)
        cx = getattr(point, 'X', 0.0)
        cy = getattr(point, 'Y', 0.0)
        cz = getattr(point, 'Z', 0.0) + (z_bias or 0.0)

        segments = 32  # number of segments to approximate the circle
        elems = []
        prev_pt = None
        for i in range(segments + 1):  # +1 to close loop
            ang = (2.0 * math.pi) * (i / segments)
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            curr_pt = AllplanGeo.Point3D(x, y, cz)
            if prev_pt is not None:
                elems.append(AllplanBasisElements.ModelElement3D(properties, AllplanGeo.Line3D(prev_pt, curr_pt)))
            prev_pt = curr_pt
        return elems

    def _add_text_label(self, elems_list, point_a: AllplanGeo.Point3D, point_b: AllplanGeo.Point3D, text: str):
        """Añade un TextElement 2D en el centro del segmento, rotado según la dirección del segmento."""
        try:
            # Calcular centro del segmento
            cx = (point_a.X + point_b.X) * 0.5
            cy = (point_a.Y + point_b.Y) * 0.5
            loc = AllplanGeo.Point2D(cx, cy)

            # Crear propiedades específicas para el texto
            text_com_prop = AllplanBaseElements.CommonProperties()
            # No llamar GetGlobalProperties() para evitar escala global

            text_prop = AllplanBasisElements.TextProperties()
            text_prop.Height = 0.30  # Valor fijo pequeño
            text_prop.Width  = 0.30
            text_prop.IsScaleDependent = False

            elems_list.append(AllplanBasisElements.TextElement(text_com_prop, text_prop, text, loc))
        except Exception as ex:
            print(f"[INT] No se pudo crear etiqueta de texto: {ex}")
# --- utilidad para acotar t mínimo razonable en segmentos cortos ---
def MAX_EPS(x: float) -> float:
    return max(min(x, 0.49), 0.0)


""""
FLUJO:

- Botón 1001 = "Crear polilínea" -> TOGGLE ON/OFF (OFF por defecto)
    * OFF: edición (drag vértices de guardadas, selección por marco, inserción por midpoint/segmento)
    * ON : creación normal (agregar puntos, drag de activos, borrar secciones, insertar)
- Midpoints visibles con z-bias y pen propio, clicables para insertar
- CheckBox 'Mode Insertar punto' controla inserción por clic sobre segmento
- 1004: borrar segmento seleccionado/hover
- 1002: guardar activa · 1003/ESC: finalizar (guarda activa y CREA INMEDIATAMENTE)
"""
