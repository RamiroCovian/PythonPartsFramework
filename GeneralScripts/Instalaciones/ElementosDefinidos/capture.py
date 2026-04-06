# -*- coding: utf-8 -*-
"""
Captura de punto libre y agregado de marcadores para elementos definidos.
Proporciona ElementPointCaptureMixin para usar con PolylineInteractor (u otro host)
junto con el catálogo de ElementosDefinidos.
"""
from __future__ import annotations

from typing import Tuple, Any, Optional

from . import catalogo


def _label_to_key(instalacion: str, label: str) -> str:
    """Convierte el valor del ComboBox (label) a key interna según instalación."""
    if not instalacion:
        return (label or "").strip().lower().replace(" ", "_") or "circle"
    inst = (instalacion or "").strip().upper()
    label_str = (label or "").strip()
    if inst == "AGUA":
        return catalogo.label_a_key_agua(label_str)
    items = catalogo.get_elementos_para_instalacion(instalacion)
    label_lower = label_str.lower()
    for e in items:
        if (e.get("label") or "").strip().lower() == label_lower:
            return e.get("key", label_str)
    return label_str or "circle"


class ElementPointCaptureMixin:
    """
    Mixin que implementa la captura de punto libre y el agregado de marcadores
    de elementos definidos usando el catálogo (validar_ubicacion_elemento, label_a_key).
    Para usar: heredar junto con PolylineInteractor y definir instalacion (ej. "AGUA").
    Requiere que el host tenga: build_ele, element_markers, coord_input,
    _set_prompt(), _draw_preview(), _save_state_to_build_ele().
    """

    def _init_element_capture_state(self) -> None:
        """Inicializa el estado de captura de punto si el host no lo define. Llamar desde __init__ del host."""
        if not hasattr(self, "element_point_capture_mode"):
            self.element_point_capture_mode = False
        if not hasattr(self, "element_point_capture_preview"):
            self.element_point_capture_preview = None
        if not hasattr(self, "element_selected_point"):
            self.element_selected_point = None

    def _get_instalacion(self) -> Optional[str]:
        """Instalación para el catálogo (ej. 'AGUA', 'ELECTRICIDAD'). Por defecto desde self.instalacion."""
        return getattr(self, "instalacion", None)

    def _get_defined_element_settings_from_catalog(self) -> Tuple[str, float]:
        """Obtiene (element_key, radius) desde build_ele usando el catálogo según instalación."""
        build_ele = getattr(self, "build_ele", None)
        if build_ele is None:
            return "t_sortida", 50.0
        raw = str(
            getattr(getattr(build_ele, "DefinedElementType", None), "value", "T sortida") or "T sortida"
        ).strip()
        instalacion = self._get_instalacion()
        element_key = _label_to_key(instalacion or "", raw)
        radius = 50.0
        try:
            radius = float(
                getattr(getattr(build_ele, "ElementRadius", None), "value", 50) or 50.0
            )
        except Exception:
            radius = 50.0
        if radius <= 0.0:
            radius = 50.0
        return element_key, radius

    def _get_defined_element_z_abs(self) -> float:
        """Obtiene la cota Z absoluta para elemento definido desde build_ele."""
        try:
            build_ele = getattr(self, "build_ele", None)
            if build_ele is None:
                return 0.0
            return float(
                getattr(getattr(build_ele, "ElementZAbs", None), "value", 0) or 0.0
            )
        except Exception:
            return 0.0

    def start_element_point_capture(self) -> bool:
        """Activa/desactiva el modo de captura de punto libre para elementos definidos."""
        self._init_element_capture_state()
        if self.element_point_capture_mode:
            self.element_point_capture_mode = False
            self.element_point_capture_preview = None
            try:
                self._set_prompt("Click: agregar punto | ESC: terminar")
            except Exception:
                pass
            return True

        try:
            import NemAll_Python_Geometry as AllplanGeo
        except Exception:
            AllplanGeo = None

        self.element_point_capture_mode = True
        if self.element_selected_point is not None and AllplanGeo is not None:
            self.element_point_capture_preview = AllplanGeo.Point3D(
                self.element_selected_point.X,
                self.element_selected_point.Y,
                self.element_selected_point.Z,
            )
        else:
            self.element_point_capture_preview = None
        try:
            self._set_prompt("Elemento (libre): Click para seleccionar punto")
        except Exception:
            pass
        print("[ELEMENTO] Modo captura de punto LIBRE activado")
        return True

    def _handle_element_point_capture(self, mouse_msg: int, raw_pnt: Any) -> bool:
        """Maneja captura de punto libre: movimiento actualiza preview; clic fija element_selected_point."""
        self._init_element_capture_state()
        try:
            import NemAll_Python_Geometry as AllplanGeo
        except Exception:
            AllplanGeo = None

        coord_input = getattr(self, "coord_input", None)
        if coord_input and getattr(coord_input, "IsMouseMove", None) and coord_input.IsMouseMove(mouse_msg):
            if AllplanGeo is not None:
                self.element_point_capture_preview = AllplanGeo.Point3D(
                    raw_pnt.X, raw_pnt.Y, raw_pnt.Z
                )
            try:
                self._draw_preview(raw_pnt)
            except Exception:
                pass
            return True

        # Click: fijar el punto (si no hay AllplanGeo, usar objeto con .X/.Y/.Z para compatibilidad)
        if AllplanGeo is not None:
            self.element_selected_point = AllplanGeo.Point3D(
                raw_pnt.X, raw_pnt.Y, raw_pnt.Z
            )
        else:
            _x = getattr(raw_pnt, "X", 0)
            _y = getattr(raw_pnt, "Y", 0)
            _z = getattr(raw_pnt, "Z", 0)
            self.element_selected_point = type("Point3D", (), {"X": _x, "Y": _y, "Z": _z})()
        self.element_point_capture_mode = False
        self.element_point_capture_preview = None
        try:
            self._set_prompt("Click: agregar punto | ESC: terminar")
        except Exception:
            pass
        p = self.element_selected_point
        if hasattr(p, "X"):
            print(
                f"[ELEMENTO] Punto libre seleccionado: ({p.X:.1f}, {p.Y:.1f}, {p.Z:.1f})"
            )
        # En modo Smart, agregar marcador inmediatamente (comportamiento interactor)
        try:
            if getattr(self, "_current_mode", lambda: None)() == "Smart":
                if not getattr(self, "create_mode", True):
                    try:
                        getattr(self, "_change_mode", lambda: None)()
                    except Exception:
                        pass
                try:
                    return bool(self._add_defined_element_marker())
                except Exception:
                    return True
        except Exception:
            pass
        try:
            self._save_state_to_build_ele()
        except Exception:
            pass
        try:
            self._draw_preview(raw_pnt)
        except Exception:
            pass
        return True

    def _add_defined_element_marker(self) -> bool:
        """
        Añade un marcador de elemento definido usando el catálogo.
        Lee DefinedElementType, ElementPointMode, ElementRadius, ElementZAbs de build_ele.
        Valida con validar_ubicacion_elemento antes de añadir.
        """
        self._init_element_capture_state()
        try:
            import NemAll_Python_Geometry as AllplanGeo
            from NemAll_Python_Base import PythonUtility
        except Exception:
            AllplanGeo = None
            PythonUtility = None

        build_ele = getattr(self, "build_ele", None)
        if build_ele is None and PythonUtility:
            PythonUtility.ShowMessageBox(
                "No hay paleta (build_ele) asociada.",
                PythonUtility.MB_OK,
            )
            return False

        try:
            mode = int(
                getattr(getattr(build_ele, "ElementPointMode", None), "value", 0) or 0
            )
        except Exception:
            mode = 0
        kind = "start" if mode == 0 else ("end" if mode == 1 else "free")
        funcion_seleccionada = (
            "inicio" if mode == 0 else ("final" if mode == 1 else "intermedio_libre")
        )

        instalacion = self._get_instalacion()
        if instalacion:
            raw_label = str(
                getattr(
                    getattr(build_ele, "DefinedElementType", None), "value", "T sortida"
                )
                or "T sortida"
            ).strip()
            element_key = _label_to_key(instalacion, raw_label)
            ok, msg = catalogo.validar_ubicacion_elemento(
                instalacion, element_key, funcion_seleccionada
            )
            if not ok and PythonUtility:
                PythonUtility.ShowMessageBox(msg or "Ubicación no válida.", PythonUtility.MB_OK)
                return False
            element_type = element_key
            radius = 50.0
            try:
                radius = float(
                    getattr(getattr(build_ele, "ElementRadius", None), "value", 50)
                    or 50.0
                )
            except Exception:
                radius = 50.0
            if radius <= 0.0:
                radius = 50.0
            z_abs = self._get_defined_element_z_abs()
        else:
            # Sin instalación: delegar en el host (comportamiento circle/square/triangle)
            get_settings = getattr(self, "_get_defined_element_settings", None)
            if callable(get_settings):
                element_type, radius = get_settings()
            else:
                element_type, radius = self._get_defined_element_settings_from_catalog()
            z_abs = getattr(self, "_get_defined_element_z_abs", self._get_defined_element_z_abs)()

        if kind == "free":
            if self.element_selected_point is None:
                if PythonUtility:
                    PythonUtility.ShowMessageBox(
                        "Modo Libre: primero pulsa 'Seleccionar punto' y haz click en el punto deseado.",
                        PythonUtility.MB_OK,
                    )
                return False
            if AllplanGeo is not None:
                pos = AllplanGeo.Point3D(
                    self.element_selected_point.X,
                    self.element_selected_point.Y,
                    self.element_selected_point.Z,
                )
            else:
                pos = self.element_selected_point
        else:
            # start/end: posición desde puntos de la polilínea si existe
            points = getattr(self, "points", None) or []
            if kind == "start" and points:
                p0 = points[0]
                pos = AllplanGeo.Point3D(p0.X, p0.Y, p0.Z) if AllplanGeo else p0
            elif kind == "end" and points:
                p0 = points[-1]
                pos = AllplanGeo.Point3D(p0.X, p0.Y, p0.Z) if AllplanGeo else p0
            elif self.element_selected_point is not None:
                p = self.element_selected_point
                pos = AllplanGeo.Point3D(p.X, p.Y, p.Z) if AllplanGeo else p
            else:
                if PythonUtility:
                    PythonUtility.ShowMessageBox(
                        "Selecciona primero un punto o dibuja la polilínea.",
                        PythonUtility.MB_OK,
                    )
                return False

        marker = {
            "kind": kind,
            "pos": pos,
            "radius": radius,
            "element_type": element_type,
            "z_abs": z_abs,
            "path_idx": None,
            "pt_idx": None,
        }
        element_markers = getattr(self, "element_markers", None)
        if element_markers is None:
            self.element_markers = []
            element_markers = self.element_markers
        element_markers.append(marker)
        self.element_selected_point = None

        try:
            self._save_state_to_build_ele()
        except Exception:
            pass
        try:
            coord_input = getattr(self, "coord_input", None)
            current_point = getattr(self, "current_point", None)
            if coord_input and current_point is not None and getattr(coord_input, "GetCurrentPoint", None):
                cp = coord_input.GetCurrentPoint(current_point)
                if cp is not None and getattr(cp, "GetPoint", None):
                    self._draw_preview(cp.GetPoint())
            else:
                self._draw_preview(pos)
        except Exception:
            pass

        px = getattr(pos, "X", 0)
        py = getattr(pos, "Y", 0)
        pz = getattr(pos, "Z", 0)
        print(
            f"[ELEMENTO] Elemento agregado ({element_type}) en punto {kind}: ({px:.1f}, {py:.1f}, {pz:.1f})"
        )
        return True
