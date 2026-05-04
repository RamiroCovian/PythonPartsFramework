# -*- coding: utf-8 -*-
"""Tub PVC Tricapa horizontal con flecha """

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult


# ========= Requisito del usuario: siempre incluir esta función =========
def check_allplan_version(_build_ele: BuildingElement,
                          _version: str) -> bool:
    """ Check the current Allplan version

    Args:
        _build_ele: building element with the parameter properties
        _version:   the current Allplan version

    Returns:
        True
    """

    # Support all versions
    return True
# ======================================================================


class TuboPVCConFlecha:
    """Constructor de tubo PVC tricapa (sección rectangular) con anillo y flecha superior."""

    # Configuración por tipo de tubo {tipo: (largo, diametro)}
    TIPOS = {0: (1000.0, 110.0), 1: (3000.0, 110.0), 2: (1000.0, 40.0), 3: (3000.0, 40.0)}

    # Configuración por diámetro (ambos con anillo al final, misma lógica)
    CONFIG = {
        110.0: {"largo_anillo": 60.0, "altura_flecha": 0.1, "grosor_anillo_x": 45.0, "grosor_anillo_y": 10.0},

        40.0: {"largo_anillo": 40.0, "altura_flecha": 1.0, "grosor_anillo_x": 15.0, "grosor_anillo_y": 10.0}
    }

    # Constantes generales
    SOBRESALE_ANILLO = 10.0
    FLECHA_FACTOR_LARGO, FLECHA_OFFSET_Z, FLECHA_DIST_ANILLO = 0.7, 0.5, 30.0

    # Colores
    COLORES = {"general": 67, "l3000_d110": 7, "flecha": 27}

    def __init__(self, build_ele: BuildingElement):
        self.build_ele = build_ele

    # ===== API pública =====
    def create_result(self) -> CreateElementResult:
        """Crea los elementos 3D (tubo + flecha) según la paleta."""
        largo, diametro, config = self._get_config(self.build_ele)

        brep = self._build_tube(largo, diametro, config)
        flecha_poly = self._build_arrow(largo, diametro, config)

        # Aplicar rotación de 180° para todos los diámetros
        z_flecha = diametro * config["altura_flecha"] + self.FLECHA_OFFSET_Z
        brep, flecha_poly = self._apply_180_transform(brep, flecha_poly, z_flecha)

        # Configurar propiedades y colores
        tipo = int(getattr(getattr(self.build_ele, "TipoTubo", None), "value", 0) or 0)
        props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        props.Color = self.COLORES["l3000_d110"] if tipo == 1 else self.COLORES["general"]

        flecha_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        flecha_props.Color = self.COLORES["flecha"]

        # Crear ModelElement3D para el tubo
        tube_element = AllplanBasisElements.ModelElement3D(props, brep)

        # Agregar atributos personalizados según el tipo de tubo
        attr_list = []
        if tipo == 0:  # L1000_D110
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-110."))  # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))     # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))      # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, "12100"))    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15
        elif tipo == 1:  # L3000_D110
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-110."))  # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))     # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))      # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, "12100"))    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15
        elif tipo == 2:  # L1000_D40
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40."))   # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))      # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))       # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, "1600"))     # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15
        elif tipo == 3:  # L3000_D40
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40."))   # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø40"))      # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "40"))       # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, "1600"))     # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, ""))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15

        # Asignar atributos al elemento
        if attr_list:
            attr_set_list = []
            attr_set_list.append(AllplanBaseElements.AttributeSet(attr_list))
            attributes = AllplanBaseElements.Attributes(attr_set_list)
            tube_element.SetAttributes(attributes)

        return CreateElementResult([
            tube_element,
            AllplanBasisElements.ModelElement3D(flecha_props, flecha_poly)
        ])

    # ======= Internos =======

    def _get_config(self, build_ele: BuildingElement) -> tuple[float, float, dict]:
        """Obtiene configuración completa del tubo basada en el tipo seleccionado."""
        tipo = int(getattr(getattr(build_ele, "TipoTubo", None), "value", 0) or 0)
        largo, diametro = self.TIPOS.get(tipo, (1000.0, 110.0))
        config = self.CONFIG[diametro]
        return largo, diametro, config

    def _get_rotation_matrix(self) -> AllplanGeo.Matrix3D:
        """Matriz de rotación para orientar el tubo horizontalmente."""
        matrix = AllplanGeo.Matrix3D()
        matrix.SetRotation(AllplanGeo.Line3D(0, 0, 0, 0, 1, 0), AllplanGeo.Angle(math.radians(90)))
        return matrix

    def _apply_180_transform(self, brep: AllplanGeo.BRep3D, flecha: AllplanGeo.Polygon3D,
                             z_flecha: float) -> tuple[AllplanGeo.BRep3D, AllplanGeo.Polygon3D]:
        """Aplica rotación de 180° en X para todos los tubos."""
        # Rotar tubo 180° en X
        eje_x = AllplanGeo.Axis3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0))
        brep = AllplanGeo.Rotate(brep, eje_x, AllplanGeo.Angle(math.radians(180)))

        # Rotar y trasladar flecha
        rot_matrix = AllplanGeo.Matrix3D()
        rot_matrix.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1, 0, 0), AllplanGeo.Angle(math.radians(180)))
        flecha = AllplanGeo.Transform(flecha, rot_matrix)

        if z_flecha != 0.0:
            tras_matrix = AllplanGeo.Matrix3D()
            tras_matrix.SetTranslation(AllplanGeo.Vector3D(0, 0, 2 * z_flecha))
            flecha = AllplanGeo.Transform(flecha, tras_matrix)

        return brep, flecha

    def _build_arrow(self, largo: float, diametro: float, config: dict) -> AllplanGeo.Polygon3D:
        """Construye la flecha direccional."""
        flecha_largo = diametro * self.FLECHA_FACTOR_LARGO
        z_flecha = diametro * config["altura_flecha"] + self.FLECHA_OFFSET_Z

        # Calcular posición antes de la rotación (anillo siempre al final)
        largo_anillo = config["largo_anillo"]
        largo_tubo = max(largo - largo_anillo, 0.0)

        # La flecha se coloca cerca del final donde está el anillo (antes de rotar)
        base_x = max(largo_tubo - flecha_largo - self.FLECHA_DIST_ANILLO, 0.0)
        sentido = 1  # Apunta hacia adelante (hacia el final del tubo - dirección del flujo)

        # Puntos de la flecha (forma de flecha simple)
        y_centro, y_span = diametro * 0.5, diametro * 0.15
        punta_x = base_x + sentido * flecha_largo

        puntos = [
            AllplanGeo.Point3D(base_x, y_centro - y_span, z_flecha),
            AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span, z_flecha),
            AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro - y_span * 2, z_flecha),
            AllplanGeo.Point3D(punta_x, y_centro, z_flecha),
            AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span * 2, z_flecha),
            AllplanGeo.Point3D(punta_x - sentido * y_span * 2, y_centro + y_span, z_flecha),
            AllplanGeo.Point3D(base_x, y_centro + y_span, z_flecha),
        ]
        puntos.append(puntos[0])  # Cerrar polígono
        return AllplanGeo.Polygon3D(puntos)

    def _build_tube(self, largo: float, diametro: float, config: dict) -> AllplanGeo.BRep3D:
        """Construye el tubo con anillo."""
        largo_anillo = config["largo_anillo"]
        largo_tubo = max(largo - largo_anillo, 0.0)
        diam_anillo = diametro + 2 * self.SOBRESALE_ANILLO

        # Grosores específicos para cada tipo de tubo
        grosor_x = config["grosor_anillo_x"]
        grosor_y = config["grosor_anillo_y"]

        # Crear tubo principal
        tubo = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)),
            diametro, diametro, largo_tubo
        )

        # Posición del anillo: siempre al final (se rotará después)
        z_anillo = largo_tubo
        p_anillo = AllplanGeo.Point3D(-self.SOBRESALE_ANILLO, -self.SOBRESALE_ANILLO, z_anillo)

        # Crear anillo exterior
        anillo_ext = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(p_anillo, AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)),
            diam_anillo, diam_anillo, largo_anillo
        )

        # Crear hendidura interior del anillo (con grosores específicos para cada tipo)
        anillo_int = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(p_anillo.X + grosor_x, p_anillo.Y + grosor_y, p_anillo.Z),
                AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)
            ),
            diam_anillo - 2 * grosor_x, diam_anillo - 2 * grosor_y, largo_anillo
        )

        # Crear anillo con hendidura (exterior - interior)
        err, anillo = AllplanGeo.MakeSubtraction(anillo_ext, anillo_int)
        if err != 0:
            raise RuntimeError(f"Error creando hendidura en anillo: {err}")

        err, brep = AllplanGeo.MakeUnion(tubo, anillo)
        if err != 0:
            raise RuntimeError(f"Error uniendo tubo y anillo: {err}")

        # Rotar para eje longitudinal horizontal
        return AllplanGeo.Transform(brep, self._get_rotation_matrix())


# ===== Punto de entrada estándar de PythonPart =====
def create_element(build_ele: BuildingElement, _doc) -> CreateElementResult:
    """Instancia la clase y delega la creación del elemento."""
    return TuboPVCConFlecha(build_ele).create_result()
