"""Script Object con interactor personalizado que maneja process_mouse_msg"""

from __future__ import annotations

import NemAll_Python_Utility as PythonUtility
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_AllplanSettings as AllplanSettings
from TypeCollections.ModificationElementList import ModificationElementList

from PythonPartUtil import PythonPartUtil

from typing import Any

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from CreateElementResult import CreateElementResult
from ScriptObjectInteractors.BaseScriptObjectInteractor import (
    BaseScriptObjectInteractor,
)
from PythonPartTransaction import PythonPartTransaction, ConnectToPythonPart, ConnectToElements

from .Angulars import Angulars

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from TypeCollections.ModelEleList import ModelEleList
from DocumentManager import DocumentManager
from dataclasses import dataclass
import os
import math
import json
import hashlib
import random
import subprocess
from ScriptObjectInteractors.PointInteractor import (
    PointInteractor,
    PointInteractorResult,
)


PMP_FG_ANG_NOM      = 2607
PMP_FG_ANG_CARA     = 2608
PMP_FG_ANG_DETALL   = 2609
VAL_PMP_FG_ANG_NOM      = "TEXT"
VAL_PMP_FG_ANG_CARA     = "LLISA/RUGOSA"
VAL_PMP_FG_ANG_DETALL   = "TEXT"



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
    import formulas as formulas
except ImportError:
    install_packages("formulas")
    print("instalando paquetes: formulas")
    import formulas as formulas

try:
    import schedula as sh
except ImportError:
    install_packages("schedula")
    print("instalando paquetes: schedula")
    import schedula as sh

try:
    import numpy as np
except ImportError:
    install_packages("numpy")
    print("instalando paquetes: numpy")
    import numpy as np

try:
    import regex as rg
except ImportError:
    install_packages("regex")
    print("instalando paquetes: regex")
    import regex as rg

try:
    import six as six
except ImportError:
    install_packages("six")
    print("instalando paquetes: regex")
    import six as six

# Definicion global de IDs atributos

LINE_INPUT = 0
USER_EDITION = 1
CANCEL = 2

def check_allplan_version(_build_ele: BuildingElement, _version: float) -> bool:
    """Verifica compatibilidad de versión"""
    return True


def create_script_object(
    build_ele: BuildingElement, script_object_data: BaseScriptObjectData
) -> BaseScriptObject:
    """Crea el script object"""
    return CustomLineScript(build_ele, script_object_data)


class CustomLineScript(BaseScriptObject):
    """Script object que usa interactor personalizado con process_mouse_msg"""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        """Inicializa el script object"""
        super().__init__(script_object_data)

        self.build_ele = build_ele
        #self.crearListaElementos()
        self.point_result = PointInteractorResult()
        self.vector_length = []
        self.attributes = BuildingElementAttributeList()
        self.preview_active = False  # Control de preview activo

        self.list_points = []
        self.abscissa = None
        self.state = None
        self.preview_elements = []


    def start_input(self):
        """Inicia la captura con interactor personalizado"""
        print("Iniciando captura con interactor personalizado")

        first = len(self.list_points) == 0

        self.state = LINE_INPUT
        self.script_object_interactor = PointInteractor(
            interactor_result=self.point_result,
            is_first_input=first,
            request_text="Input Point",
            preview_function=self.preview_line_function,
            default_input_value=None,
            abscissa_element=self.abscissa
        )

    def preview_line_function(self):
        model_list = ModelEleList()
        if len(self.list_points) >=1:
            for i in range(len(self.list_points) - 1):
                line = AllplanGeometry.Line3D(self.list_points[i], self.list_points[i+1])
                model_list.append_geometry_3d(line)

            line = AllplanGeometry.Line3D(self.list_points[len(self.list_points) - 1], self.point_result.input_point)
            model_list.append_geometry_3d(line)


            AllplanBaseElements.DrawElementPreview(self.document, AllplanGeometry.Matrix3D(),
                                        model_list, True, None)

        return

    def start_next_input(self):
        """Continuar captura si no hemos terminado"""
        # print(f"Puntos capturados: {len(self.point_result.points)}")

        if self.point_result.input_point != PointInteractorResult():
            self.list_points.append(self.point_result.input_point)

            if len(self.list_points) > 1:
                self.abscissa = AllplanGeometry.Line3D(self.list_points[-2], self.list_points[-1])

            if len(self.list_points) < 2:
                self.start_input()

            else:
                # Cuando terminamos de capturar puntos, activar preview persistente
                self.script_object_interactor = None
                self.preview_active = True
                print("Captura de puntos completada - Preview persistente activado")

    def modify_element_property(self,
                            name  : str,
                            _value: Any) -> bool:
        """ modify the element property

        Args:
            name:   name
            _value: value

        Returns:
            update palette state
        """

        if name == "SelectorGruix":
            if _value == "Gruix 15 mm":
                self.build_ele.Gruix.value = 15
            elif _value == "Gruix 20 mm":
                self.build_ele.Gruix.value = 20
            elif _value == "Gruix 35 mm":
                self.build_ele.Gruix.value = 35
            elif _value == "Gruix 120 mm":
                self.build_ele.Gruix.value = 120

        if self.script_object_interactor is not None:
            return True

        else:
            self.execute()

        return False



    def on_preview_draw(self):
        """Maneja el evento de preview draw - se llama continuamente"""
        if self.preview_active and len(self.list_points) >= 2:
            self.draw_persistent_preview()

    def draw_persistent_preview(self):
        """Dibuja preview persistente de la polilínea capturada"""
        if not self.list_points or not self.coord_input:
            return

        print(
            f"Debug: Dibujando preview persistente con {len(self.list_points)} puntos"
        )

        # Crear elementos de preview
        preview_elements = []

        # Dibujar líneas entre todos los puntos capturados
        for i in range(len(self.list_points) - 1):
            line = AllplanGeometry.Line3D(
                self.list_points[i], self.list_points[i + 1]
            )
            common_props = AllplanBaseElements.CommonProperties()
            common_props.GetGlobalProperties()
            common_props.Color = 6  # Color de preview
            common_props.Pen = 2  # Grosor medio
            preview_elements.append(
                AllplanBasisElements.ModelElement3D(common_props, line)
            )

        # Dibujar el preview
        if preview_elements:
            AllplanBaseElements.DrawElementPreview(
                self.coord_input.GetInputViewDocument(),
                AllplanGeometry.Matrix3D(),
                preview_elements + self.concrete,
                False,
                None,
            )





    def execute(self) -> CreateElementResult:
        """Crea el elemento línea en el drawing file"""
        print("execute")

        if self.state == CANCEL:
            return CreateElementResult()

        # Desactivar preview cuando se ejecuta
        self.preview_active = False

        # Verificar que tenemos suficientes puntos
        if len(self.list_points) < 1:
            print("No hay suficientes puntos para crear líneas")
            return CreateElementResult([])

        elements = ModelEleList()
        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()

        # 2. Crear líneas individuales y calcular longitudes
        total_length = 0.0
        print("\n--- LONGITUDES DE LAS LÍNEAS ---")
        # vector_length = []

        build_ele = self.build_ele
        build_ele.zUnique.value = random.random() * 3600
        llargada = self.distancia(self.list_points[0], self.list_points[1])
        build_ele.Llargada.value = llargada
        puntAux = AllplanGeometry.Point3D(self.list_points[0].X + llargada,
                                          self.list_points[0].Y,
                                          self.list_points[0].Z)

        #angle = self.angulo_en_punto(self.list_points[0],puntAux, self.list_points[1], en_grados=True)
        angle, puntosAxis = self.angulo_y_eje_dos_puntos(self.list_points[0],puntAux, self.list_points[1], en_grados=True)
        for punto in puntosAxis:
            punto.X = punto.X - self.list_points[0].X
            punto.Y = punto.Y - self.list_points[0].Y
            punto.Z = punto.Z - self.list_points[0].Z
        angle = [puntosAxis, AllplanGeometry.Angle.FromDeg(angle)]
        angular = Angulars(build_ele.zUnique.value, build_ele,  build_ele.Ample.value, build_ele.Altura.value, build_ele.Llargada.value, build_ele.Gruix.value, build_ele.nEncaixos.value, invertirPared = build_ele.invertirPared.value, angle =angle )
        elements = angular.create()
        self.concrete = elements

        #line = AllplanGeometry.Line3D(self.list_points[0], self.list_points[1])
        #newPoint = AllplanGeometry.Vector3D()
        #cuboid = AllplanGeometry.Move(line, newPoint)
        pntInici = AllplanGeometry.Point3D(-50, build_ele.Gruix.value + 25, build_ele.Gruix.value + 25)
        pntFinal = AllplanGeometry.Point3D( build_ele.Llargada.value + 50, build_ele.Gruix.value + 25, build_ele.Gruix.value + 25)
        axis_point = AllplanGeometry.Axis3D(angle[0][0], AllplanGeometry.Vector3D(angle[0][0], angle[0][1]))
        pntInici = AllplanGeometry.Rotate(pntInici, axis_point, angle[1])
        pntFinal = AllplanGeometry.Rotate(pntFinal, axis_point, angle[1])

        line = AllplanGeometry.Line3D(pntInici, pntFinal)

        #axis_point = AllplanGeometry.Axis3D(angle[0][0], AllplanGeometry.Vector3D(angle[0][0], angle[0][1]))
        #axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(), AllplanGeo.Vector3D(0,1,0))
        #line = AllplanGeometry.Rotate(polyline, angle[1])

        elements.append_geometry_3d(line)

        #AllplanBaseElements.RotateElements(__doc__, self.concrete,
        #                                   AllplanGeometry.Point2D(self.list_points[0].X, self.list_points[0].Y),
        #                                   angle[1], AllplanIFW.ViewWorldProjection())

        placement_point=AllplanGeometry.Point3D()
        placement_point = self.list_points[0]

        return CreateElementResult(
            elements=elements, placement_point=placement_point
        )

    def angulo_en_punto(self, a , b, c, en_grados=True):
        """
        Calcula el ángulo en el punto 'a' entre los vectores a->b y a->c.
        """
        # vectores AB y AC
        ab = (b.X - a.X, b.Y - a.Y, b.Z - a.Z)
        ac = (c.X - a.X, c.Y - a.Y, c.Z - a.Z)

        # producto escalar y magnitudes
        dot = ab[0]*ac[0] + ab[1]*ac[1] + ab[2]*ac[2]
        norm_ab = math.sqrt(ab[0]**2 + ab[1]**2 + ab[2]**2)
        norm_ac = math.sqrt(ac[0]**2 + ac[1]**2 + ac[2]**2)

        # coseno del ángulo
        cos_theta = dot / (norm_ab * norm_ac)

        # proteger contra errores numéricos
        cos_theta = max(-1.0, min(1.0, cos_theta))

        ang = math.acos(cos_theta)
        angulo =  math.degrees(ang) if en_grados else ang

        return angulo

    def angulo_y_eje_dos_puntos(self, b: AllplanGeometry.Point3D, a: AllplanGeometry.Point3D,  c: AllplanGeometry.Point3D, en_grados=True):
        """
        Calcula el ángulo en el punto b formado por (a, b, c),
        y devuelve también el eje de rotación como dos Point3D (origen, extremo).
        """
        # Convertir a arrays
        A = np.array([a.X, a.Y, a.Z])
        B = np.array([b.X, b.Y, b.Z])
        C = np.array([c.X, c.Y, c.Z])

        # Vectores
        BA = A - B
        BC = C - B

        # Normalizar vectores
        BA_norm = BA / np.linalg.norm(BA)
        BC_norm = BC / np.linalg.norm(BC)

        # Ángulo por producto escalar
        cos_ang = np.clip(np.dot(BA_norm, BC_norm), -1.0, 1.0)
        angulo = math.acos(cos_ang)
        if en_grados:
            angulo = math.degrees(angulo)

        # Eje de rotación como vector normal
        eje = np.cross(BA, BC)
        if np.linalg.norm(eje) < 1e-9:  # si son colineales, no hay eje definido
            eje = np.array([0.0, 0.0, 0.0])
        else:
            eje = eje / np.linalg.norm(eje)

        # Dos puntos que definen el eje (pasando por B)
        eje_p1 = AllplanGeometry.Point3D(B[0], B[1], B[2])
        eje_p2 = AllplanGeometry.Point3D(B[0] + eje[0], B[1] + eje[1], B[2] + eje[2])

        return angulo, (eje_p1, eje_p2)


    def distancia(self, p1, p2):
        return math.sqrt(
            (p2.X - p1.X)**2 +
            (p2.Y - p1.Y)**2 +
            (p2.Z - p1.Z)**2
        )


    def on_cancel_function(self) -> OnCancelFunctionResult:
        """Maneja la presión de ESC"""
        print("on_cancel_function")
        try:

            #if self.state == CANCEL:
            #    return OnCancelFunctionResult.CANCEL_INPUT

            #self.get_values_from_excel()

            #concrete = self._build_ferralla_model_elements(AllplanGeometry.Point3D(0,0,0))
            elements = ModelEleList()
            for elem in self.concrete:
                elements.append_geometry_3d(elem.GeometryObject)

            placement_matrix = AllplanGeometry.Matrix3D()
            placement_matrix.Translate(AllplanGeometry.Vector3D(self.list_points[0]))
            #placement_pnt = self.get_placement_point(self.list_points[0], self.list_points[1])
            #placement_matrix.Translate(AllplanGeometry.Vector3D(placement_pnt))
            #angle = self.get_lines_angle(AllplanGeometry.Line3D(placement_pnt, self.list_points[-1]), AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X + self.total_length,placement_pnt.Y, placement_pnt.Z)))
            #placement_matrix.Translate(AllplanGeometry.Vector3D(placement_pnt))
            #placement_matrix.Rotation(AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X, placement_pnt.Y, placement_pnt.Z + 100)), angle)

            self.attributes.add_attribute(PMP_FG_ANG_NOM   , VAL_PMP_FG_ANG_NOM)
            self.attributes.add_attribute(PMP_FG_ANG_CARA  , VAL_PMP_FG_ANG_CARA)
            self.attributes.add_attribute(PMP_FG_ANG_DETALL, VAL_PMP_FG_ANG_DETALL)


            pp_util = PythonPartUtil()
            pp_util.add_pythonpart_view_2d3d(elements)
            pp_util.add_attribute_list(self.attributes)
            pp = pp_util.create_pythonpart(
                self.build_ele, placement_matrix=placement_matrix
            )

            insertion_matrix = AllplanGeometry.Matrix3D()
            AllplanBaseElements.CreateElements(
                self.document, insertion_matrix, pp, [], None
            )

            #pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())#, connect_to_pyp= connectionPP ,connect_to_ele=connectionEle )
            #base_elems = AllplanElementAdapter.BaseElementAdapterList()
            #base_elems = pyp_transaction.execute(
            #    placement_matrix =  AllplanGeometry.Matrix3D(),
            #    view_world_projection= AllplanIFW.ViewWorldProjection(),
            #    model_ele_list = pp,#pythonpart_group,#pythonParts,
            #    modification_ele_list= ModificationElementList(),
            #    uuid_parameter_name = "TD Python",#get_file_name(self.list_of_filenames[nPPChild]),#
            #    # elements_to_delete=build_ele.created_elems.value
            #)
        except Exception as e:
            return OnCancelFunctionResult.CANCEL_INPUT

        return OnCancelFunctionResult.CANCEL_INPUT

    def get_placement_point(self, pt1: AllplanGeometry.Point3D, pt2: AllplanGeometry.Point3D):
        p1, p2, dist, v = self.get_distance(pt1, pt2)

        v_unit = v / dist

        p0 = p1 - v_unit * dist

        return AllplanGeometry.Point3D(p0[0], p0[1], p0[2])

    def get_distance(self, pt1: AllplanGeometry.Point3D, pt2: AllplanGeometry.Point3D):
        p1 = np.array([pt1.X, pt1.Y, pt1.Z])
        p2 = np.array([pt2.X, pt2.Y, pt2.Z])

        v = p2 - p1

        dist = np.linalg.norm(v)

        return p1, p2, dist, v

    def get_lines_angle(self, destino: AllplanGeometry.Line3D, origen: AllplanGeometry.Line3D) -> AllplanGeometry.Angle:
        p10 = np.array([destino.StartPoint.X, destino.StartPoint.Y, destino.StartPoint.Z])
        p11 = np.array([destino.EndPoint.X, destino.EndPoint.Y, destino.EndPoint.Z])

        p20 = np.array([origen.StartPoint.X, origen.StartPoint.Y, origen.StartPoint.Z])
        p21 = np.array([origen.EndPoint.X, origen.EndPoint.Y, origen.EndPoint.Z])

        v1 = p11 - p10
        v2 = p21 - p20

        dot_product = np.dot(v1, v2)
        norms = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_theta = np.clip(dot_product / norms, -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)

        cross = np.cross(v2, v1)

        normal = np.array([0, 0, 1])

        sign = np.sign(np.dot(cross, normal))

        signed_angle_rad = angle_rad * sign
        signed_angle_deg = np.degrees(signed_angle_rad)

        angle = AllplanGeometry.Angle()
        angle.SetDeg(signed_angle_deg)
        return angle