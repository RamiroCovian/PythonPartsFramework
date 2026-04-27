# -*- coding: utf-8 -*-
"""Tub PVC Tricapa horizontal con flecha """

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements

from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData


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

        40.0: {"largo_anillo": 40.0, "altura_flecha": 1.0, "grosor_anillo_x": 13.75, "grosor_anillo_y": 5.0, "sobresale_anillo": 5.0}
    }

    # Constantes generales
    SOBRESALE_ANILLO = 10.0
    FLECHA_FACTOR_LARGO, FLECHA_OFFSET_Z, FLECHA_DIST_ANILLO = 0.7, 0.5, 30.0

    # Colores
    COLORES = {"general": 67, "l3000_d110": 7, "flecha": 27}
    LAYER = 40148  # IS_CON_SANE_FAB (is cone fab)

    def __init__(
        self,
        tipo_tubo: int = 0,
        doc=None,
        largo_total_mm: float | None = None,
    ):
        self.tipo_tubo = tipo_tubo
        self.doc = doc
        # Polilínea: longitud total del tramo (mm); el anillo mantiene largo_anillo del config.
        self.largo_total_mm = largo_total_mm

    # ===== API pública =====
    def create_result(self) -> CreateElementResult:
        """Crea los elementos 3D (tubo + flecha) según la paleta."""
        largo, diametro, config = self._get_config()

        brep = self._build_tube(largo, diametro, config)
        flecha_poly = self._build_arrow(largo, diametro, config)

        # Aplicar rotación de 180° para todos los diámetros
        z_flecha = diametro * config["altura_flecha"] + self.FLECHA_OFFSET_Z
        brep, flecha_poly = self._apply_180_transform(brep, flecha_poly, z_flecha)

        # Configurar propiedades y colores
        tipo = self.tipo_tubo
        props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        # Ø110 (tipo 0 = 1 m Pluvial, tipo 1 = 3 m): color 7; Ø40 (2/3): general
        props.Color = (
            self.COLORES["l3000_d110"]
            if tipo in (0, 1)
            else self.COLORES["general"]
        )
        props.ColorByLayer = False  # Permitir modificar el color independientemente de la layer
        props.Layer = self.LAYER  # IS_CON_SANE_FAB (is cone fab)

        flecha_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        flecha_props.Color = self.COLORES["flecha"]
        flecha_props.ColorByLayer = False  # Permitir modificar el color independientemente de la layer
        flecha_props.Layer = self.LAYER  # IS_CON_SANE_FAB (is cone fab)

        # Crear ModelElement3D para el tubo
        tube_element = AllplanBasisElements.ModelElement3D(props, brep)

        # Agregar atributos personalizados según el tipo de tubo
        attr_list = []
        if tipo == 0:  # L1000_D110 (1mm)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-110"))  # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))     # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))      # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, "12100"))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15

            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm(attr_list, tipo)
        elif tipo == 1:  # L3000_D110 (3mm azul)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-110"))  # Custom attribute 01
            attr_list.append(AllplanBaseElements.AttributeString(1084, "Ø110"))     # Custom attribute 02
            attr_list.append(AllplanBaseElements.AttributeString(1085, ""))         # Custom attribute 03
            attr_list.append(AllplanBaseElements.AttributeString(1086, ""))         # Custom attribute 04
            attr_list.append(AllplanBaseElements.AttributeString(1087, ""))         # Custom attribute 05
            attr_list.append(AllplanBaseElements.AttributeString(1895, ""))         # Custom attribute 06
            attr_list.append(AllplanBaseElements.AttributeString(1896, "110"))      # Custom attribute 07
            attr_list.append(AllplanBaseElements.AttributeString(1897, ""))         # Custom attribute 08
            attr_list.append(AllplanBaseElements.AttributeString(1898, ""))    # Custom attribute 09
            attr_list.append(AllplanBaseElements.AttributeString(1899, "12100"))         # Custom attribute 10
            attr_list.append(AllplanBaseElements.AttributeString(1900, ""))         # Custom attribute 11
            attr_list.append(AllplanBaseElements.AttributeString(1901, ""))         # Custom attribute 12
            attr_list.append(AllplanBaseElements.AttributeString(1902, ""))         # Custom attribute 13
            attr_list.append(AllplanBaseElements.AttributeString(1903, ""))         # Custom attribute 14
            attr_list.append(AllplanBaseElements.AttributeString(1904, ""))         # Custom attribute 15

            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_110mm(attr_list, tipo)
        elif tipo == 2:  # L1000_D40 (1Ml)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40"))   # Custom attribute 01
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

            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_40mm(attr_list, tipo)
        elif tipo == 3:  # L3000_D40 (3Ml)
            attr_list.append(AllplanBaseElements.AttributeString(1083, "TS-40"))   # Custom attribute 01
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

            # Agregar atributos de usuario adicionales si hay documento disponible
            if self.doc:
                self._add_user_attributes_40mm(attr_list, tipo)

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

    def _get_config(self) -> tuple[float, float, dict]:
        """Obtiene configuración completa del tubo basada en el tipo seleccionado."""
        largo, diametro = self.TIPOS.get(self.tipo_tubo, (1000.0, 110.0))
        config = self.CONFIG[diametro]
        if self.largo_total_mm is not None:
            la = float(config["largo_anillo"])
            largo = max(float(self.largo_total_mm), la + 1.0)
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

        # Rotar flecha sobre sí misma (alrededor de su centro en Z)
        # Cuando rota 180° en X alrededor del origen, Y se invierte.
        # Para que rote sobre sí misma, rotamos alrededor de su propio centro Z
        rot_matrix = AllplanGeo.Matrix3D()
        rot_matrix.SetRotation(
            AllplanGeo.Line3D(0, 0, z_flecha, 1, 0, z_flecha),  # Eje X a altura z_flecha
            AllplanGeo.Angle(math.radians(180))
        )
        flecha = AllplanGeo.Transform(flecha, rot_matrix)

        return brep, flecha

    def _add_user_attributes_110mm(self, attr_list, tipo):
        """Agrega atributos de usuario para tubos de 110mm según el tipo (1mm o 3mm azul)."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_area_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_area")
            attr_pmp_densitat_lineal_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_densitat_lineal")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: según tipo (tipo 0 = 1mm: KN07_005_003, tipo 1 = 3mm azul: KN07_005_004)
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                carticulo_value = "KN07_005_004" if tipo == 0 else "KN07_005_004"
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, carticulo_value))

            # pmp_nom: "TS-110"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-110"))

            # pmp_area: 12100.000000 (AttributeDouble)
            if attr_pmp_area_id and attr_pmp_area_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 12100.000000))

            # pmp_densitat_lineal: 0.2288 (AttributeDouble)
            if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, 0.2288))

            # pmp_diametre: 110 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_diametre_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "110"))

            # pmp_seccio: 110 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_seccio_id, 110))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "110"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Tub_PVC_TricapaV_005] Advertencia al agregar atributos de usuario 110mm: {e}")

    def _add_user_attributes_40mm(self, attr_list, tipo):
        """Agrega atributos de usuario para tubos de 40mm según el tipo (1Ml o 3Ml)."""
        if not self.doc:
            return

        try:
            # Obtener IDs de atributos por nombre
            attr_6_cc_is_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "6_CC_IS")
            attr_pmp_carticulo_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_CARTICULO")
            attr_pmp_nom_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_nom")
            attr_pmp_area_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_area")
            attr_pmp_densitat_lineal_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_densitat_lineal")
            attr_pmp_diametre_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_diametre")
            attr_pmp_seccio_id = AllplanBaseElements.AttributeService.GetAttributeID(self.doc, "pmp_seccio")

            # 6_CC_IS: "IS"
            if attr_6_cc_is_id and attr_6_cc_is_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_6_cc_is_id, ""))

            # pmp_CARTICULO: según tipo (tipo 2 = 1Ml: KN07_005_001, tipo 3 = 3Ml: KN07_005_002)
            if attr_pmp_carticulo_id and attr_pmp_carticulo_id > 0:
                carticulo_value = "KN07_005_001" if tipo == 2 else "KN07_005_002"
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_carticulo_id, carticulo_value))

            # pmp_nom: "TS-40"
            if attr_pmp_nom_id and attr_pmp_nom_id > 0:
                attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_nom_id, "TS-40"))

            # pmp_area: 1600.000000 (AttributeDouble)
            if attr_pmp_area_id and attr_pmp_area_id > 0:
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_area_id, 1600.000000))

            # pmp_densitat_lineal: 0.2900 (mismo valor para tipo 2 = 1Ml y tipo 3 = 3Ml)
            if attr_pmp_densitat_lineal_id and attr_pmp_densitat_lineal_id > 0:
                densitat_value = 0.2900
                attr_list.append(AllplanBaseElements.AttributeDouble(attr_pmp_densitat_lineal_id, densitat_value))

            # pmp_diametre: 40 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_diametre_id and attr_pmp_diametre_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_diametre_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_diametre_id, "40"))

            # pmp_seccio: 40 (AttributeInt o AttributeString según el tipo)
            if attr_pmp_seccio_id and attr_pmp_seccio_id > 0:
                try:
                    attr_list.append(AllplanBaseElements.AttributeInteger(attr_pmp_seccio_id, 40))
                except:
                    attr_list.append(AllplanBaseElements.AttributeString(attr_pmp_seccio_id, "40"))

        except Exception as e:
            # No bloquear la creación si hay problemas con los atributos
            print(f"[Tub_PVC_TricapaV_005] Advertencia al agregar atributos de usuario 40mm: {e}")

    def _build_arrow(self, largo: float, diametro: float, config: dict) -> AllplanGeo.Polygon3D:
        """Construye la flecha direccional."""
        flecha_largo = diametro * self.FLECHA_FACTOR_LARGO
        z_flecha = diametro * config["altura_flecha"] + self.FLECHA_OFFSET_Z

        # Obtener valores de recorte (trim_in recorta al inicio, trim_out al final)
        trim_in = config.get('trim_in', 0.0)
        trim_out = config.get('trim_out', 0.0)

        # Calcular posición según donde esté el anillo
        largo_anillo = config["largo_anillo"]
        largo_tubo = max(largo - largo_anillo, 0.0)

        # Determinar orientación de la flecha basándose en 'anillo_inicio'
        # La flecha debe apuntar HACIA donde está el anillo (hacia donde fluye el agua)
        # Si anillo_inicio=False, el anillo está al final, la flecha apunta hacia el final (sentido=+1)
        # Si anillo_inicio=True, el anillo está al inicio, la flecha apunta hacia el inicio (sentido=-1)
        anillo_en_inicio = config.get('anillo_inicio', True)

        if anillo_en_inicio:
            # Anillo al inicio: flecha cerca del final apuntando hacia el inicio (donde está el anillo)
            # Ajustar por trim_out ya que el tubo se recorta al final
            base_x = max(largo_tubo - flecha_largo - self.FLECHA_DIST_ANILLO - trim_out, trim_in)
            sentido = -1  # Apunta hacia atrás (hacia el inicio donde está el anillo)
        else:
            # Anillo al final: flecha cerca del inicio apuntando hacia el final (donde está el anillo)
            # Ajustar por trim_in ya que el tubo se recorta al inicio
            base_x = self.FLECHA_DIST_ANILLO + trim_in
            sentido = +1  # Apunta hacia adelante (hacia el final donde está el anillo)

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

        # Usar sobresale_anillo del config si existe, sino usar la constante global
        sobresale_anillo = config.get("sobresale_anillo", self.SOBRESALE_ANILLO)
        diam_anillo = diametro + 2 * sobresale_anillo

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
        p_anillo = AllplanGeo.Point3D(-sobresale_anillo, -sobresale_anillo, z_anillo)

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


# --- Clase Principal del PythonPart ---
class TubPvcTricapaVScript(BaseScriptObject):
    """Clase principal del PythonPart que modela un armaflex."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.doc = self.coord_input.GetInputViewDocument()

    def get_attributes(self, *args, **kwargs):
        return []

    def execute(self, *args, **kwargs) -> CreateElementResult:
        """Ejecuta la creación del tubo PVC Tricapa con flecha."""
        tipo_tubo_raw = kwargs.get("TipoTubo", args[0] if args else 0)
        try:
            tipo_tubo = int(tipo_tubo_raw.value)
        except (AttributeError, TypeError):
            tipo_tubo = int(tipo_tubo_raw)
        lt = kwargs.get("LargoTramoMm")
        largo_total = None
        if lt is not None:
            try:
                largo_total = float(lt.value) if hasattr(lt, "value") else float(lt)
            except (TypeError, ValueError):
                largo_total = None
        return TuboPVCConFlecha(
            tipo_tubo, self.doc, largo_total_mm=largo_total
        ).create_result()