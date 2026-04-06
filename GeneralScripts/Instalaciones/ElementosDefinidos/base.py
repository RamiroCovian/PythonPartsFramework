# -*- coding: utf-8 -*-
"""
Clases base para elementos que funcionan como elementos definidos de la instalación.
Un mismo objeto puede tener una función predefinida única o varias (inicio, final,
intermedio_ordenado, intermedio_libre, bifurcación).
"""
from __future__ import annotations

from abc import ABC
from typing import List, Any, Optional

# Tipos genéricos para no depender de Allplan en la base (se inyectan en implementaciones)
try:
    import NemAll_Python_Geometry as AllplanGeo

    Point3D = AllplanGeo.Point3D
except Exception:
    AllplanGeo = None  # type: ignore
    Point3D = Any  # type: ignore


# Funciones posibles de un punto en la polilínea (selector de tipo de punto)
POSIBLES_FUNCIONES: List[str] = [
    "inicio",
    "final",
    "intermedio_ordenado",
    "intermedio_libre",
    "bifurcación",
]

# Mapeo con roles numéricos usados en PolylineLib (constants.ROLE_LABEL)
# 0=Inicial, 1=Paso, 2=Bifurcacion, 3=Final; "intermedio_libre" no es un rol fijo (punto libre)
FUNCION_TO_ROLE: dict = {
    "inicio": 0,
    "final": 3,
    "intermedio_ordenado": 1,
    "intermedio_libre": 1,  # mismo rol lógico; la posición es libre en el tramo
    "bifurcación": 2,
}


class BaseDefinedElement(ABC):
    """
    Clase base para los elementos que tienen que funcionar como elementos definidos
    de la instalación. Relaciona un punto (inicio, final, intermedio, bifurcación)
    con un elemento concreto; las opciones de objeto dependen de cada instalación.
    """

    # --- Inicialización (identificación y capacidades) ---
    nombre: str  # identificación en ComboBox
    posibles_funciones: List[str]  # selector de función dinámico según elemento
    funcion_defecto: str  # función por defecto al colocar

    # --- Guardado (estado al colocar en la polilínea) ---
    posicion: Any  # Point3D
    funcion_seleccionada: str
    rotacion: float  # grados
    id_camino: int
    orden_en_camino: int

    def __init__(
        self,
        nombre: str,
        posibles_funciones: Optional[List[str]] = None,
        funcion_defecto: Optional[str] = None,
    ):
        self.nombre = nombre
        self.posibles_funciones = list(posibles_funciones or POSIBLES_FUNCIONES)
        self.funcion_defecto = funcion_defecto or self.posibles_funciones[0]
        self.posicion = None
        self.funcion_seleccionada = self.funcion_defecto
        self.rotacion = 0.0
        self.id_camino = 0
        self.orden_en_camino = 0

    def can_be_used_in_role(self, funcion: str) -> bool:
        """Indica si este elemento puede colocarse en la función dada (inicio/final/intermedio/bifurcación)."""
        return funcion in self.posibles_funciones

    def _get_3d_geometry(self, build_ele: Any, doc: Any) -> List[Any]:
        """
        Obtiene la lista de geometría 3D del elemento (ModelElement3D o equivalente).
        Las subclases deben implementar este método; la base devuelve lista vacía.
        """
        return []

    def generate_preview(self, build_ele: Any = None, doc: Any = None) -> List[Any]:
        """Añade 3D del elemento para la previsualización. Retorna lista de ModelElement3D (o equivalente)."""
        if build_ele is None or doc is None:
            return []
        return list(self._get_3d_geometry(build_ele, doc) or [])

    def generate_final_3d(self, build_ele: Any = None, doc: Any = None) -> List[Any]:
        """Genera 3D para la generación final. Retorna lista de ModelElement3D (o equivalente)."""
        if build_ele is None or doc is None:
            return []
        return list(self._get_3d_geometry(build_ele, doc) or [])


class BaseMacroElement(BaseDefinedElement):
    """
    Elemento definido que toma su geometría de un macro (SymbolElement).
    La previsualización y el 3D definitivo se obtienen leyendo el 3D del macro.
    """

    elemento_macro: Any  # SymbolElement o equivalente

    def __init__(
        self,
        nombre: str,
        elemento_macro: Any,
        posibles_funciones: Optional[List[str]] = None,
        funcion_defecto: Optional[str] = None,
    ):
        super().__init__(
            nombre=nombre,
            posibles_funciones=posibles_funciones,
            funcion_defecto=funcion_defecto,
        )
        self.elemento_macro = elemento_macro

    def _get_3d_geometry(self, build_ele: Any, doc: Any) -> List[Any]:
        """
        Lee el 3D del macro (elemento_macro) y retorna la lista de ModelElement3D.
        Prueba GetModelElement3DList(), GetModelGeometry() y métodos habituales
        de la API Allplan para símbolos/macros. Las subclases pueden redefinir
        si su tipo de macro expone otra API.
        """
        if self.elemento_macro is None:
            return []
        el = self.elemento_macro
        # GetModelElement3DList() (común en símbolos/macros Allplan)
        try:
            if hasattr(el, "GetModelElement3DList") and callable(
                el.GetModelElement3DList
            ):
                lst = el.GetModelElement3DList()
                if lst is not None:
                    return list(lst) if not isinstance(lst, list) else lst
        except Exception:
            pass
        # GetModelGeometry() -> geometría que se puede envolver en ModelElement3D
        try:
            if hasattr(el, "GetModelGeometry") and callable(el.GetModelGeometry):
                geo = el.GetModelGeometry()
                if geo is not None and AllplanGeo is not None:
                    try:
                        from NemAll_Python_BasisElements import AllplanBasisElements
                        from NemAll_Python_BaseElements import AllplanBaseElements

                        common_props = (
                            getattr(
                                AllplanBaseElements, "GetGlobalNamespace"
                            )().GetCommonProperties()
                            if hasattr(AllplanBaseElements, "GetGlobalNamespace")
                            else None
                        )
                        if common_props is not None:
                            return [
                                AllplanBasisElements.ModelElement3D(common_props, geo)
                            ]
                    except Exception:
                        pass
        except Exception:
            pass
        return []


class CallbackDefinedElement(BaseDefinedElement):
    """
    Elemento definido cuya geometría 3D se obtiene mediante un callback (p. ej. el
    create_element del PythonPart). Permite usar la API de BaseDefinedElement
    sin definir una subclase por cada tipo; el script pasa la función que retorna
    (model_list, _, _) o model_list.
    """

    def __init__(
        self,
        nombre: str,
        callback_geometria: Any,  # (build_ele, doc) -> list o (model_list, _, _)
        posibles_funciones: Optional[List[str]] = None,
        funcion_defecto: Optional[str] = None,
    ):
        super().__init__(
            nombre=nombre,
            posibles_funciones=posibles_funciones,
            funcion_defecto=funcion_defecto,
        )
        self._callback_geometria = callback_geometria

    def _get_3d_geometry(self, build_ele: Any, doc: Any) -> List[Any]:
        if not callable(self._callback_geometria):
            return []
        try:
            result = self._callback_geometria(build_ele, doc)
            if result is None:
                return []
            # create_element suele devolver (model_list, [], [])
            if isinstance(result, tuple) and len(result) >= 1:
                model_list = result[0]
                return list(model_list) if model_list else []
            if isinstance(result, list):
                return list(result)
            return []
        except Exception:
            return []
