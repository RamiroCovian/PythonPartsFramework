"""Script Object con interactor personalizado que maneja process_mouse_msg"""

from __future__ import annotations

import NemAll_Python_Utility as PythonUtility
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_AllplanSettings as AllplanSettings

from PythonPartUtil import PythonPartUtil

from typing import Any

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from CreateElementResult import CreateElementResult
from ScriptObjectInteractors.BaseScriptObjectInteractor import (
    BaseScriptObjectInteractor,
)
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from TypeCollections.ModelEleList import ModelEleList
from DocumentManager import DocumentManager
from dataclasses import dataclass
import os
import json
import subprocess
from ScriptObjectInteractors.PointInteractor import (
    PointInteractor,
    PointInteractorResult,
)

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

# ids de atributos
# -- ARNAU --
id_l1_izquierdo = 2001
id_l1_derecho = 2002
id_l2_izquierdo = 2003
id_l2_derecho = 2004
id_l3_izquierdo = 2005
id_l3_derecho = 2006
id_l4_izquierdo = 2007
id_l4_derecho = 2008
id_e1_izquierdo = 2009
id_e1_derecho = 2010
id_e2_izquierdo = 2011
id_e2_derecho = 2012
id_e3_izquierdo = 2013
id_e3_derecho = 2014
id_peso_total = 2015
id_peso_arm = 2016
id_peso_neg = 2017
id_barres_B_izquierdo = 2018
id_barres_B_derecho = 2019
id_barres_B_diametro_izq = 2020
id_barres_B_diametro_der = 2021
id_barres_A_izquierdo = 2022
id_barres_A_derecho = 2023
id_barres_A_diametro_izq = 2024
id_barres_A_diametro_der = 2025
id_barres_e1_diametro_izq = 2026
id_barres_e1_diametro_der = 2027
id_barres_e1_b_izq = 2028
id_barres_e1_b_der = 2029
id_barres_e1_a_izq = 2030
id_barres_e1_a_der = 2031
id_barres_e1_separacion_izq = 2032
id_barres_e1_separacion_der = 2033
id_barres_e3_diametro_izq = 2034
id_barres_e3_diametro_der = 2035
id_barres_e3_b_izq = 2036
id_barres_e3_b_der = 2037
id_barres_e3_a_izq = 2038
id_barres_e3_a_der = 2039
id_barres_e2_diametro_izq = 2040
id_barres_e2_diametro_der = 2041
id_barres_e2_b_izq = 2042
id_barres_e2_b_der = 2043
id_barres_e2_a_izq = 2044
id_barres_e2_a_der = 2045
id_barres_s_izquierdo = 2046
id_barres_s_derecho = 2047
id_barres_s_diametro_izq = 2048
id_barres_s_diametro_der = 2049
id_barres_e4_diametro_izq = 2050
id_barres_e4_diametro_der = 2051
id_barres_e4_b_izq = 2052
id_barres_e4_b_der = 2053
id_barres_e4_a_izq = 2054
id_barres_e4_a_der = 2055

# ids de atributos
# -- MATIAS --
# id_l1_izquierdo = 5001
# id_l1_derecho = 5002
# id_l2_izquierdo = 5003
# id_l2_derecho = 5004
# id_l3_izquierdo = 5005
# id_l3_derecho = 5006
# id_l4_izquierdo = 5007
# id_l4_derecho = 5008
# id_e1_izquierdo = 5009
# id_e1_derecho = 5010
# id_e2_izquierdo = 5011
# id_e2_derecho = 5012
# id_e3_izquierdo = 5013
# id_e3_derecho = 5014
# id_peso_total = 5015
# id_peso_arm = 5016
# id_peso_neg = 5017
# id_barres_B_izquierdo = 5023
# id_barres_B_derecho = 5024
# id_barres_B_diametro_izq = 5018
# id_barres_B_diametro_der = 5019
# id_barres_A_izquierdo = 5020
# id_barres_A_derecho = 5021
# id_barres_A_diametro_izq = 5022
# id_barres_A_diametro_der = 5025
# id_barres_e1_diametro_izq = 5026
# id_barres_e1_diametro_der = 5027
# id_barres_e1_b_izq = 5028
# id_barres_e1_b_der = 5029
# id_barres_e1_a_izq = 5030
# id_barres_e1_a_der = 5031
# id_barres_e1_separacion_izq = 5032
# id_barres_e1_separacion_der = 5033
# id_barres_e3_diametro_izq = 5034
# id_barres_e3_diametro_der = 5035
# id_barres_e3_b_izq = 5036
# id_barres_e3_b_der = 5037
# id_barres_e3_a_izq = 5038
# id_barres_e3_a_der = 5039
# id_barres_e2_diametro_izq = 5040
# id_barres_e2_diametro_der = 5041
# id_barres_e2_b_izq = 5042
# id_barres_e2_b_der = 5043
# id_barres_e2_a_izq = 5044
# id_barres_e2_a_der = 5045
# id_barres_s_izquierdo = 5046
# id_barres_s_derecho = 5047
# id_barres_s_diametro_izq = 5048
# id_barres_s_diametro_der = 5049
# id_barres_e4_diametro_izq = 5050
# id_barres_e4_diametro_der = 5051
# id_barres_e4_b_izq = 5052
# id_barres_e4_b_der = 5053
# id_barres_e4_a_izq = 5054
# id_barres_e4_a_der = 5055

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
        self.crearListaElementos()
        self.point_result = PointInteractorResult()
        self.vector_length = []
        self.attributes = BuildingElementAttributeList()
        self.preview_active = False  # Control de preview activo

        self.list_points = []
        self.abscissa = None
        self.state = None

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

            if len(self.list_points) < 4:
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

        if self.script_object_interactor is not None:
            return True

        else:
            self.execute()

        return False

    def _build_ferralla_model_elements(self, ref_point: AllplanGeometry.Point3D):
        """Devuelve los elementos de la Ferralla."""

        model_ele_list = []

        try:
            punto_min_1 = AllplanGeometry.Point3D(ref_point.X, ref_point.Y, ref_point.Z)
            punto_max_1 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value,
                ref_point.Y + self.build_ele.base_extremo_izq.value,
                ref_point.Z +  self.build_ele.altura_extremo_izq.value,
            )
            cuboide_1 = AllplanGeometry.Polyhedron3D.CreateCuboid(
                punto_min_1, punto_max_1
            )

            punto_min_2 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value, ref_point.Y, ref_point.Z
            )
            punto_max_2 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value
                + self.build_ele.largo_eje_izq.value,
                ref_point.Y + self.build_ele.base_eje_izq.value,
                ref_point.Z + self.build_ele.altura_eje_izq.value,
            )
            cuboide_2 = AllplanGeometry.Polyhedron3D.CreateCuboid(
                punto_min_2, punto_max_2
            )

            punto_min_2_2 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value
                + self.build_ele.largo_eje_izq.value,
                ref_point.Y,
                ref_point.Z,
            )
            punto_max_2_2 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value
                + self.build_ele.largo_eje_izq.value
                + self.build_ele.largo_eje_der.value,
                ref_point.Y + self.build_ele.base_eje_der.value,
                ref_point.Z + self.build_ele.altura_eje_der.value,
            )
            cuboide_2_2 = AllplanGeometry.Polyhedron3D.CreateCuboid(
                punto_min_2_2, punto_max_2_2
            )

            punto_min_3 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value
                + self.build_ele.largo_eje_izq.value
                + self.build_ele.largo_eje_der.value,
                ref_point.Y,
                ref_point.Z,
            )
            punto_max_3 = AllplanGeometry.Point3D(
                ref_point.X + self.build_ele.largo_extremo_izq.value
                + self.build_ele.largo_eje_izq.value
                + self.build_ele.largo_eje_der.value
                + self.build_ele.largo_extremo_der.value,
                ref_point.Y + self.build_ele.base_extremo_der.value,
                ref_point.Z + self.build_ele.altura_extremo_der.value,
            )
            cuboide_3 = AllplanGeometry.Polyhedron3D.CreateCuboid(
                punto_min_3, punto_max_3
            )

            # Validar que todos los cuboides sean válidos antes de unirlos
            if (
                cuboide_1.IsValid()
                and cuboide_2.IsValid()
                and cuboide_2_2.IsValid()
                and cuboide_3.IsValid()
            ):
                print("Todos los cuboides son válidos, procediendo con la unión...")

                # Unir cuboide_1 y cuboide_2 primero
                err1, union_temp = AllplanGeometry.MakeUnion(cuboide_1, cuboide_2)

                if (
                    err1 == AllplanGeometry.eGeometryErrorCode.eOK
                    and union_temp.IsValid()
                ):
                    print("Primera unión exitosa")

                    # Unir el resultado con cuboide_2_2
                    err2, union_temp_2 = AllplanGeometry.MakeUnion(
                        union_temp, cuboide_2_2
                    )

                    if (
                        err2 == AllplanGeometry.eGeometryErrorCode.eOK
                        and union_temp_2.IsValid()
                    ):
                        print("Segunda unión exitosa")

                        # Unir el resultado con cuboide_3
                        err3, union_final = AllplanGeometry.MakeUnion(
                            union_temp_2, cuboide_3
                        )

                        if (
                            err3 == AllplanGeometry.eGeometryErrorCode.eOK
                            and union_final.IsValid()
                        ):
                            print("Unión final exitosa - agregando elemento único")
                            model_ele_list.append(
                                union_final
                            )  # Solo agregar el elemento unido
                            return model_ele_list
                        else:
                            print(
                                "Error en la tercera unión, usando cuboides separados"
                            )
                            model_ele_list.append(cuboide_1)
                            model_ele_list.append(cuboide_2)
                            model_ele_list.append(cuboide_2_2)
                            model_ele_list.append(cuboide_3)
                    else:
                        print("Error en la segunda unión, usando cuboides separados")
                        model_ele_list.append(cuboide_1)
                        model_ele_list.append(cuboide_2)
                        model_ele_list.append(cuboide_2_2)
                        model_ele_list.append(cuboide_3)
                else:
                    print("Error en la primera unión, usando cuboides separados")
                    model_ele_list.append(cuboide_1)
                    model_ele_list.append(cuboide_2)
                    model_ele_list.append(cuboide_2_2)
                    model_ele_list.append(cuboide_3)
            else:
                print(
                    "Algunos cuboides no son válidos, usando los válidos por separado"
                )
                if cuboide_1.IsValid():
                    model_ele_list.append(cuboide_1)
                if cuboide_2.IsValid():
                    model_ele_list.append(cuboide_2)
                if cuboide_2_2.IsValid():
                    model_ele_list.append(cuboide_2_2)
                if cuboide_3.IsValid():
                    model_ele_list.append(cuboide_3)

        except Exception as e:
            print(f"Error creando cuboide: {str(e)}")

        return []

    def detectar_rangos_superpuestos(self, leixos_value):
        """
        Detecta qué rangos están disponibles para un valor de Leixos dado
        Args:
            leixos_value: valor de Leixos para verificar
        Returns:
            lista de rangos que coinciden con el valor
        """
        try:
            usr_path = AllplanSettings.AllplanPaths.GetUsrPath()
            config_file = os.path.join(usr_path, "config_formulas.json")

            if not os.path.exists(config_file):
                return []

            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            rangos_coincidentes = []
            for rango in config["ranges"]:
                if rango["leixos_min"] <= leixos_value <= rango["leixos_max"]:
                    rangos_coincidentes.append(rango["name"])

            return rangos_coincidentes

        except Exception as e:
            print(f"Error detectando rangos superpuestos: {e}")
            return []

    def crearListaElementos(self):
        print("Ingreso a crearListaElementos")
        print(
            f"Lista de elementos cargados: {self.build_ele.ListaElementosDinamica.value}"
        )
        lista_actual = self.build_ele.ListaElementosDinamica.value
        # lista_inicial = ["Rango 2"]
        rangos_disponibles = self.detectar_rangos_superpuestos(
            self.build_ele.Leixos.value
        )

        # Cambiamos presentacion de rango al usuario para que sea mas claro
        rangos_disponibles = [
            "Rango 4 (Con y sin pared)" if rango == "Rango 4" else rango
            for rango in rangos_disponibles
            if rango != "Rango 5"
        ]
        # Mostrar lista de rangos disponibles
        print(f"Lista de rangos disponibles: {rangos_disponibles}")

        debe_actualizar = (
            len(lista_actual) == 0
            or len(lista_actual) != len(rangos_disponibles)
            or (len(rangos_disponibles) > 0 and lista_actual != rangos_disponibles)
            or (
                rangos_disponibles == ["Rango 4 (Con y sin pared)"]
                and lista_actual != rangos_disponibles
            )
        )

        if debe_actualizar:
            # ListaElementosDinamica espera una lista de strings
            self.build_ele.ListaElementosDinamica.value = rangos_disponibles
            print(
                f"Lista de elementos actualizada: {self.build_ele.ListaElementosDinamica.value}"
            )
            if len(rangos_disponibles) > 0:
                self.build_ele.SelectorElemento.value = rangos_disponibles[0]

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
                preview_elements,
                False,
                None,
            )

    def get_base_data(self, valores_entrada, build_ele=None):
        try:
            if (config := self.load_config()) is None:
                return None

            # Cargar archivo Excel del rango seleccionado
            usr_path = AllplanSettings.AllplanPaths.GetUsrPath()
            excel_file = os.path.join(usr_path, config["excel_file"])
            if not os.path.exists(excel_file):
                print(f"Archivo Excel no encontrado: {excel_file}")
                return None

            sheet_name = config["sheet_name"]

            # Cargar modelo Excel
            model = formulas.ExcelModel().load(excel_file)

            ok, selected_range, fallback = self.get_selected_range_on_excel(valores_entrada, build_ele, config)
            if not ok or selected_range is None:
                return fallback

            cell_base_extremo_izq = selected_range["outputs"]["base_extremo_izq"]
            cell_altura_extremo_izq = selected_range["outputs"]["altura_extremo_izq"]
            cell_base_eje_izq = selected_range["outputs"]["base_eje_izq"]
            cell_altura_eje_izq = selected_range["outputs"]["altura_eje_izq"]
            cell_base_eje_der = selected_range["outputs"]["base_eje_der"]
            cell_altura_eje_der = selected_range["outputs"]["altura_eje_der"]
            cell_base_extremo_der = selected_range["outputs"]["base_extremo_der"]
            cell_altura_extremo_der = selected_range["outputs"]["altura_extremo_der"]

            results = {}

            key_cell_base_extremo_izq = f"'[{config["excel_file"]}]{sheet_name}'!{cell_base_extremo_izq}"
            key_cell_altura_extremo_izq = f"'[{config["excel_file"]}]{sheet_name}'!{cell_altura_extremo_izq}"
            key_cell_base_eje_izq = f"'[{config["excel_file"]}]{sheet_name}'!{cell_base_eje_izq}"
            key_cell_altura_eje_izq = f"'[{config["excel_file"]}]{sheet_name}'!{cell_altura_eje_izq}"
            key_cell_base_eje_der = f"'[{config["excel_file"]}]{sheet_name}'!{cell_base_eje_der}"
            key_cell_altura_eje_der = f"'[{config["excel_file"]}]{sheet_name}'!{cell_altura_eje_der}"
            key_cell_base_extremo_der = f"'[{config["excel_file"]}]{sheet_name}'!{cell_base_extremo_der}"
            key_cell_altura_extremo_der = f"'[{config["excel_file"]}]{sheet_name}'!{cell_altura_extremo_der}"

            solution = model.calculate(outputs=[
                key_cell_base_extremo_izq,
                key_cell_altura_extremo_izq,
                key_cell_base_eje_izq,
                key_cell_altura_eje_izq,
                key_cell_base_eje_der,
                key_cell_altura_eje_der,
                key_cell_base_extremo_der,
                key_cell_altura_extremo_der
            ])

            results["base_extremo_izq"] = self.get_solution_value(solution, key_cell_base_extremo_izq)
            results["altura_extremo_izq"] = self.get_solution_value(solution, key_cell_altura_extremo_izq)
            results["base_eje_izq"] = self.get_solution_value(solution, key_cell_base_eje_izq)
            results["altura_eje_izq"] = self.get_solution_value(solution, key_cell_altura_eje_izq)
            results["base_eje_der"] = self.get_solution_value(solution, key_cell_base_eje_der)
            results["altura_eje_der"] = self.get_solution_value(solution, key_cell_altura_eje_der)
            results["base_extremo_der"] = self.get_solution_value(solution, key_cell_base_extremo_der)
            results["altura_extremo_der"] = self.get_solution_value(solution, key_cell_altura_extremo_der)

            return results


        except Exception as e:
            print(f"Error en calcular_con_formulas_library: {e}")
            return None

    def calcular_con_formulas_library(self, valores_entrada, build_ele=None):
        """
        Lee los valores de los inputs del Excel y los usa para calcular los outputs
        usando configuración JSON para determinar qué rangos y celdas usar
        Args:
            valores_entrada: dict con los valores de los inputs
            build_ele: building element para acceder a parámetros adicionales
        Returns:
            dict con los valores de los outputs
        """
        try:
            if (config := self.load_config()) is None:
                return None

            # Cargar archivo Excel del rango seleccionado
            usr_path = AllplanSettings.AllplanPaths.GetUsrPath()
            excel_file = os.path.join(usr_path, config["excel_file"])
            if not os.path.exists(excel_file):
                print(f"Archivo Excel no encontrado: {excel_file}")
                return None

            sheet_name = config["sheet_name"]

            # Cargar modelo Excel
            xl_model = formulas.ExcelModel().loads(excel_file).finish(circular=True)

            ok, selected_range, fallback = self.get_selected_range_on_excel(valores_entrada, build_ele, config)
            if not ok:
                return fallback
            if selected_range is None:
                return fallback

            # Construir inputs usando la configuración
            inputs_dict = {}
            for param_name, cell_ref in selected_range["inputs"].items():
                if param_name == "leixos":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = valores_entrada.get("Leixos", 0)
                elif param_name == "a1sab_esq":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = valores_entrada.get("A1sabEsq", 0)
                elif param_name == "a2sab_d":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = (
                        valores_entrada.get("A2sabD", 0),
                    )
                elif param_name == "arm_sup":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = valores_entrada.get("ArmSuperior", 0)
                elif param_name == "arm_inf":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = valores_entrada.get("ArmInferior", 0)
                elif param_name == "canto_sabata":
                    inputs_dict[
                        f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                    ] = valores_entrada.get("CantoSabata", 0)

            print(f"Inputs configurados: {inputs_dict}")

            # Calcular
            solution = xl_model.calculate(inputs=inputs_dict)

            # Extraer resultados usando la configuración
            results = {}
            for output_name, cell_ref in selected_range["outputs"].items():
                cell_key = f"'[{config["excel_file"]}]{sheet_name}'!{cell_ref}"
                value = self.get_solution_value(solution, cell_key)
                results[output_name] = (value)

            print(f"Resultados calculados: {results}")
            return results

        except Exception as e:
            print(f"Error en calcular_con_formulas_library: {e}")
            return None

    def get_solution_value(self, solution, cell_key):
        if cell_key in solution:
            value = solution[cell_key].value
            if hasattr(value, "__iter__") and not isinstance(value, str):
                if value[0][0] is not None:
                    return float(value[0][0])
            else:
                if value is not None:
                    return float(value)
        else:
            print(f"Celda de salida no encontrada: {cell_key}")

        return 0.0

    def load_config(self):
        try:
            # Cargar configuración JSON
            usr_path = AllplanSettings.AllplanPaths.GetUsrPath()
            config_file = os.path.join(usr_path, "config_formulas.json")

            if not os.path.exists(usr_path):
                print(f"Carpeta de usuario no encontrada: {usr_path}")
                return None

            if not os.path.exists(config_file):
                print(f"Archivo de configuración no encontrado: {config_file}")
                return None

            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"Error en calcular_con_formulas_library: {e}")
            return None

    def get_selected_range_on_excel(self, valores_entrada, build_ele, config):
        # Obtener valor de Leixos para determinar el rango
        leixos_value = valores_entrada.get("Leixos", 0)
        print(f"Buscando rango para Leixos = {leixos_value}")

        rangos_coincidentes = []
        for rango in config["ranges"]:
            if rango["leixos_min"] <= leixos_value <= rango["leixos_max"]:
                rangos_coincidentes.append(rango)
                print(
                    f"Rango encontrado: {rango['name']} ({rango['leixos_min']} - {rango['leixos_max']})"
                )

        rango_seleccionado = build_ele.SelectorElemento.value
        print(f"SelectorElemento value: {rango_seleccionado}")
        print("Valor de RadioGroupValue: ", build_ele.RadioGroupValue.value)

        # Manejar el caso especial de "Rango 4 (Con y sin pared)"
        if rango_seleccionado == "Rango 4 (Con y sin pared)":
            if build_ele.RadioGroupValue.value == 2:
                rango_seleccionado = "Rango 5"
            else:
                rango_seleccionado = "Rango 4"

        print(f"Rango seleccionado: {rango_seleccionado}")

        if not rango_seleccionado:
            print(f"No se encontró rango para Leixos = {leixos_value}")
            print("Usando valores por defecto del archivo de configuración")
            if "defaults" in config and "fallback_values" in config["defaults"]:
                return False, None, config["defaults"]["fallback_values"]
            return False, None, None

        # Buscar el rango por nombre
        selected_range = None
        for rango in config["ranges"]:
            if rango["name"] == rango_seleccionado:
                selected_range = rango
                break

        if not selected_range:
            print(f"No se encontró rango con nombre: {rango_seleccionado}")
            print("Usando valores por defecto del archivo de configuración")
            if "defaults" in config and "fallback_values" in config["defaults"]:
                return False, None, config["defaults"]["fallback_values"]
            return False, None, None

        print(f"Rango seleccionado: {selected_range}")
        return True, selected_range, None

    def _crear_placement_matrix(self) -> AllplanGeometry.Matrix3D:
        """Crea una matriz de placement"""
        placement_matrix = AllplanGeometry.Matrix3D()
        # Verificar que tenemos suficientes puntos antes de crear la matriz
        if len(self.list_points) >= 3:
            # Establecer posición inicial (P1)
            p1 = self.list_points[0]
            placement_matrix.SetTranslation(AllplanGeometry.Vector3D(p1.X, p1.Y, p1.Z))

            # Establecer la orientación basada en la dirección de P1 a P3
            p1 = self.list_points[0]
            p3 = self.list_points[2]

            # Crear vector de dirección de P1 a P3
            direction_vector = AllplanGeometry.Vector3D(p1, p3)

            # Vector de referencia (eje X por defecto)
            reference_vector = AllplanGeometry.Vector3D(1, 0, 0)

            # Establecer la rotación usando los vectores de dirección
            placement_matrix.SetRotation(reference_vector, direction_vector)

            return placement_matrix

        # Usar matriz por defecto si no hay suficientes puntos
        return placement_matrix

    def execute(self) -> CreateElementResult:
        """Crea el elemento línea en el drawing file"""
        print("execute")

        if self.state == CANCEL:
            return CreateElementResult()

        # Desactivar preview cuando se ejecuta
        self.preview_active = False

        # Verificar que tenemos suficientes puntos
        if len(self.list_points) < 4:
            print("No hay suficientes puntos para crear líneas")
            return CreateElementResult([])

        elements = ModelEleList()
        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()

        # 1. Crear polilínea con todos los puntos
        # if len(self.point_result.points) >= 2:
        #     polyline = AllplanGeometry.Polyline3D()
        #     for point in self.point_result.points:
        #         polyline += point

        #     # Crear elemento de polilínea
        #     common_props_polyline = AllplanBaseElements.CommonProperties()
        #     common_props_polyline.GetGlobalProperties()
        #     common_props_polyline.Color = 2  # Color rojo para la polilínea
        #     common_props_polyline.Pen = 3    # Grosor más grueso

        #     polyline_element = AllplanBasisElements.ModelElement3D(common_props_polyline, polyline)
        #     elements.append(polyline_element)
        #     print(f"Polilínea creada con {len(self.point_result.points)} puntos")

        # 2. Crear líneas individuales y calcular longitudes
        total_length = 0.0
        print("\n--- LONGITUDES DE LAS LÍNEAS ---")
        # vector_length = []
        if self.state == LINE_INPUT:
            for i in range(len(self.list_points) - 1):
                # Crear línea entre puntos consecutivos
                line = AllplanGeometry.Line3D(
                    self.list_points[i], self.list_points[i + 1]
                )

                elements.append_geometry_3d(line)

                # Calcular longitud usando Vector3D
                vector = AllplanGeometry.Vector3D(
                    self.list_points[i], self.list_points[i + 1]
                )
                length = vector.GetLength()
                self.vector_length.append(length)
                total_length += length

                # Imprimir información de la línea
                print(
                    f"Línea {i+1}: P{i+1}({self.list_points[i].X:.1f}, {self.list_points[i].Y:.1f}, {self.list_points[i].Z:.1f}) -> "
                    f"P{i+2}({self.list_points[i+1].X:.1f}, {self.list_points[i+1].Y:.1f}, {self.list_points[i+1].Z:.1f}) "
                    f"= {length:.2f} mm"
                )

            print(f"Vector length: {self.vector_length}")
            if len(self.vector_length) == 3:
                self.build_ele.A1sabEsq.value = self.vector_length[0] * 2 / 1000
                self.build_ele.Leixos.value = total_length / 1000
                self.build_ele.A2sabD.value = self.vector_length[2] * 2 / 1000

            print("Inputs actualizados desde polilinea")
            print(f"A1sabEsq: {self.build_ele.A1sabEsq.value}")
            print(f"Leixos: {self.build_ele.Leixos.value}")
            print(f"A2sabD: {self.build_ele.A2sabD.value}")

            print(f"\nLongitud total de todas las líneas: {total_length:.2f} mm")
            print(f"Número total de líneas creadas: {len(self.list_points) - 1}")
        elif self.state == USER_EDITION:
            print("Inputs actualizados desde paleta")
            print(f"A1sabEsq: {self.build_ele.A1sabEsq.value}")
            print(f"Leixos: {self.build_ele.Leixos.value}")
            print(f"A2sabD: {self.build_ele.A2sabD.value}")


        print("--- FIN LONGITUDES ---\n")

        # Crear lista de elementos dinamicos
        print("disparando desde execute crearListaElementos")
        self.crearListaElementos()

        if len(self.build_ele.ListaElementosDinamica.value) == 0:
            PythonUtility.ShowMessageBox(f"La longitud de Leixos ({self.build_ele.Leixos.value}) supera el màximo permitido", PythonUtility.MB_OK)
            return CreateElementResult()

        valores_a_escribir = {
            "Leixos": self.build_ele.Leixos.value,
            "A1sabEsq": self.build_ele.A1sabEsq.value,
            "A2sabD": self.build_ele.A2sabD.value,
            "ArmSuperior": self.build_ele.ArmSuperior.value,
            "ArmInferior": self.build_ele.ArmInferior.value,
            "CantoSabata": self.build_ele.CantoSabata.value,
        }

        eje_medio = self.build_ele.Leixos.value - (self.build_ele.A1sabEsq.value / 2) - (self.build_ele.A2sabD.value / 2)

        excel_response = self.get_base_data(valores_a_escribir, self.build_ele)

        if excel_response is not None:
            largo_extremo_izq = self.build_ele.A1sabEsq.value * 1000
            base_extremo_izq = excel_response["base_extremo_izq"] * 1000
            altura_extremo_izq = excel_response["altura_extremo_izq"] * 1000

            largo_eje_izq = (eje_medio / 2) * 1000
            base_eje_izq = excel_response["base_eje_izq"] * 1000
            altura_eje_izq = excel_response["altura_eje_izq"] * 1000

            largo_eje_der = (eje_medio / 2) * 1000
            base_eje_der = excel_response["base_eje_der"] * 1000
            altura_eje_der = excel_response["altura_eje_der"] * 1000

            largo_extremo_der = self.build_ele.A2sabD.value * 1000
            base_extremo_der = excel_response["base_extremo_der"] * 1000
            altura_extremo_der = excel_response["altura_extremo_der"] * 1000

            self.build_ele.largo_extremo_izq.value = largo_extremo_izq
            self.build_ele.base_extremo_izq.value = base_extremo_izq
            self.build_ele.altura_extremo_izq.value = altura_extremo_izq

            self.build_ele.largo_eje_izq.value = largo_eje_izq
            self.build_ele.base_eje_izq.value = base_eje_izq
            self.build_ele.altura_eje_izq.value = altura_eje_izq

            self.build_ele.largo_eje_der.value = largo_eje_der
            self.build_ele.base_eje_der.value = base_eje_der
            self.build_ele.altura_eje_der.value = altura_eje_der

            self.build_ele.largo_extremo_der.value = largo_extremo_der
            self.build_ele.base_extremo_der.value = base_extremo_der
            self.build_ele.altura_extremo_der.value = altura_extremo_der

            self.total_length = largo_extremo_izq + largo_eje_izq + largo_eje_der + largo_extremo_der

        else:
            print("Usando valores calculados por defecto (Lectura Excel falló)")
            self.build_ele.base_extremo_izq.value = 0.4 * 1000
            self.build_ele.altura_extremo_izq.value = 0.3 * 1000
            self.build_ele.largo_extremo_izq.value = 1.19 * 1000
            self.build_ele.base_extremo_der.value = 0.4 * 1000
            self.build_ele.altura_extremo_der.value = 0.3 * 1000
            self.build_ele.largo_extremo_der.value = 1.19 * 1000
            self.build_ele.base_eje_izq.value = 0.4 * 1000
            self.build_ele.altura_eje_izq.value = 0.45 * 1000
            self.build_ele.largo_eje_izq.value = 2.95 * 1000
            self.build_ele.base_eje_der.value = 0.4 * 1000
            self.build_ele.altura_eje_der.value = 0.45 * 1000
            self.build_ele.largo_eje_der.value = 2.95 * 1000
            self.total_length = self.build_ele.largo_extremo_izq.value + self.build_ele.largo_eje_izq.value + self.build_ele.largo_eje_der.value + self.build_ele.largo_extremo_der.value

        placement_pnt = self.get_placement_point(self.list_points[0], self.list_points[1])
        concrete = self._build_ferralla_model_elements(placement_pnt)
        angle = self.get_lines_angle(AllplanGeometry.Line3D(placement_pnt, self.list_points[-1]), AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X + self.total_length,placement_pnt.Y, placement_pnt.Z)))
        for elem in concrete:
            elem = AllplanGeometry.Rotate(elem, AllplanGeometry.Axis3D(AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X, placement_pnt.Y, placement_pnt.Z + 100))), angle)
            elements.append_geometry_3d(elem)

        self.state = USER_EDITION
        return CreateElementResult(
            elements=elements, placement_point=AllplanGeometry.Point3D()
        )

    def get_values_from_excel(self):
        """Crea el elemento línea en el drawing file"""
        # Desactivar preview cuando se ejecuta
        self.preview_active = False

        # Verificar que tenemos suficientes puntos
        if len(self.list_points) < 4:
            print("No hay suficientes puntos para crear líneas")
            return

        # 1. Crear polilínea con todos los puntos
        # if len(self.point_result.points) >= 2:
        #     polyline = AllplanGeometry.Polyline3D()
        #     for point in self.point_result.points:
        #         polyline += point

        #     # Crear elemento de polilínea
        #     common_props_polyline = AllplanBaseElements.CommonProperties()
        #     common_props_polyline.GetGlobalProperties()
        #     common_props_polyline.Color = 2  # Color rojo para la polilínea
        #     common_props_polyline.Pen = 3    # Grosor más grueso

        #     polyline_element = AllplanBasisElements.ModelElement3D(common_props_polyline, polyline)
        #     elements.append(polyline_element)
        #     print(f"Polilínea creada con {len(self.point_result.points)} puntos")

        # 2. Crear líneas individuales y calcular longitudes

        valores_a_escribir = {
            "Leixos": self.build_ele.Leixos.value,
            "A1sabEsq": self.build_ele.A1sabEsq.value,
            "A2sabD": self.build_ele.A2sabD.value,
            "ArmSuperior": self.build_ele.ArmSuperior.value,
            "ArmInferior": self.build_ele.ArmInferior.value,
            "CantoSabata": self.build_ele.CantoSabata.value,
        }


        excel_response = self.calcular_con_formulas_library(
            valores_a_escribir, self.build_ele
        )
        print(f"Valores recalculados del excel:\n")
        for key, value in excel_response.items():
            print(f"   {key}: {value}")

        # Usar valores desde Excel, sino valores por defecto
        if excel_response is not None:
            print("Usando valores recalculados desde Excel")

            eje_medio = self.build_ele.Leixos.value - (self.build_ele.A1sabEsq.value / 2) - (self.build_ele.A2sabD.value / 2)

            largo_extremo_izq = self.build_ele.A1sabEsq.value * 1000
            base_extremo_izq = excel_response["base_extremo_izq"] * 1000
            altura_extremo_izq = excel_response["altura_extremo_izq"] * 1000

            largo_eje_izq = (eje_medio / 2) * 1000
            base_eje_izq = excel_response["base_eje_izq"] * 1000
            altura_eje_izq = excel_response["altura_eje_izq"] * 1000

            largo_eje_der = (eje_medio / 2) * 1000
            base_eje_der = excel_response["base_eje_der"] * 1000
            altura_eje_der = excel_response["altura_eje_der"] * 1000

            largo_extremo_der = self.build_ele.A2sabD.value * 1000
            base_extremo_der = excel_response["base_extremo_der"] * 1000
            altura_extremo_der = excel_response["altura_extremo_der"] * 1000

            self.build_ele.largo_extremo_izq.value = largo_extremo_izq
            self.build_ele.base_extremo_izq.value = base_extremo_izq
            self.build_ele.altura_extremo_izq.value = altura_extremo_izq

            self.build_ele.largo_eje_izq.value = largo_eje_izq
            self.build_ele.base_eje_izq.value = base_eje_izq
            self.build_ele.altura_eje_izq.value = altura_eje_izq

            self.build_ele.largo_eje_der.value = largo_eje_der
            self.build_ele.base_eje_der.value = base_eje_der
            self.build_ele.altura_eje_der.value = altura_eje_der

            self.build_ele.largo_extremo_der.value = largo_extremo_der
            self.build_ele.base_extremo_der.value = base_extremo_der
            self.build_ele.altura_extremo_der.value = altura_extremo_der

            self.total_length = largo_extremo_izq + largo_eje_izq + largo_eje_der + largo_extremo_der

            # Parámetros opcionales - se setean en 0 si no existen
            parametro_l1_izquierdo = excel_response.get("L1_izquierdo", 0.0)
            parametro_l1_derecho = excel_response.get("L1_derecho", 0.0)
            parametro_l2_izquierdo = excel_response.get("L2_izquierdo", 0.0)
            parametro_l2_derecho = excel_response.get("L2_derecho", 0.0)
            parametro_l3_izquierdo = excel_response.get("L3_izquierdo", 0.0)
            parametro_l3_derecho = excel_response.get("L3_derecho", 0.0)
            parametro_l4_izquierdo = excel_response.get("L4_izquierdo", 0.0)
            parametro_l4_derecho = excel_response.get("L4_derecho", 0.0)
            parametro_e1_izquierdo = int(excel_response.get("E1_izquierdo", 0))
            parametro_e1_derecho = int(excel_response.get("E1_derecho", 0))
            parametro_e2_izquierdo = int(excel_response.get("E2_izquierdo", 0))
            parametro_e2_derecho = int(excel_response.get("E2_derecho", 0))
            parametro_e3_izquierdo = int(excel_response.get("E3_izquierdo", 0))
            parametro_e3_derecho = int(excel_response.get("E3_derecho", 0))
            parametro_peso_total = excel_response.get("peso_total", 0.0)
            parametro_peso_arm = excel_response.get("peso_arm", 0.0)
            parametro_peso_neg = excel_response.get("peso_neg", 0.0)
            parametro_barres_B_izquierdo = int(
                excel_response.get("barres_B_izquierdo", 0)
            )
            parametro_barres_B_derecho = int(excel_response.get("barres_B_derecho", 0))
            parametro_barres_B_diametro_izq = excel_response.get(
                "barres_B_diametro_izq", 0.0
            )
            parametro_barres_B_diametro_der = excel_response.get(
                "barres_B_diametro_der", 0.0
            )
            parametro_barres_A_izquierdo = int(
                excel_response.get("barres_A_izquierdo", 0)
            )
            parametro_barres_A_derecho = int(excel_response.get("barres_A_derecho", 0))
            parametro_barres_A_diametro_izq = excel_response.get(
                "barres_A_diametro_izq", 0.0
            )
            parametro_barres_A_diametro_der = excel_response.get(
                "barres_A_diametro_der", 0.0
            )
            parametro_barres_e1_diametro_izq = excel_response.get(
                "barres_e1_diametro_izq", 0.0
            )
            parametro_barres_e1_diametro_der = excel_response.get(
                "barres_e1_diametro_der", 0.0
            )
            parametro_barres_e1_b_izq = excel_response.get("barres_e1_b_izq", 0.0)
            parametro_barres_e1_b_der = excel_response.get("barres_e1_b_der", 0.0)
            parametro_barres_e1_a_izq = excel_response.get("barres_e1_a_izq", 0.0)
            parametro_barres_e1_a_der = excel_response.get("barres_e1_a_der", 0.0)
            parametro_barres_e1_separacion_izq = excel_response.get(
                "barres_e1_separacion_izq", 0.0
            )
            parametro_barres_e1_separacion_der = excel_response.get(
                "barres_e1_separacion_der", 0.0
            )
            parametro_barres_e3_diametro_izq = excel_response.get(
                "barres_e3_diametro_izq", 0.0
            )
            parametro_barres_e3_diametro_der = excel_response.get(
                "barres_e3_diametro_der", 0.0
            )
            parametro_barres_e3_b_izq = excel_response.get("barres_e3_b_izq", 0.0)
            parametro_barres_e3_b_der = excel_response.get("barres_e3_b_der", 0.0)
            parametro_barres_e3_a_izq = excel_response.get("barres_e3_a_izq", 0.0)
            parametro_barres_e3_a_der = excel_response.get("barres_e3_a_der", 0.0)
            parametro_barres_e2_diametro_izq = excel_response.get(
                "barres_e2_diametro_izq", 0.0
            )
            parametro_barres_e2_diametro_der = excel_response.get(
                "barres_e2_diametro_der", 0.0
            )
            parametro_barres_e2_b_izq = excel_response.get("barres_e2_b_izq", 0.0)
            parametro_barres_e2_b_der = excel_response.get("barres_e2_b_der", 0.0)
            parametro_barres_e2_a_izq = excel_response.get("barres_e2_a_izq", 0.0)
            parametro_barres_e2_a_der = excel_response.get("barres_e2_a_der", 0.0)
            parametro_barres_s_izquierdo = int(
                excel_response.get("barres_s_izquierdo", 0)
            )
            parametro_barres_s_derecho = int(excel_response.get("barres_s_derecho", 0))
            parametro_barres_s_diametro_izq = excel_response.get(
                "barres_s_diametro_izq", 0.0
            )
            parametro_barres_s_diametro_der = excel_response.get(
                "barres_s_diametro_der", 0.0
            )
            parametro_barres_e4_diametro_izq = excel_response.get(
                "barres_e4_diametro_izq", 0.0
            )
            parametro_barres_e4_diametro_der = excel_response.get(
                "barres_e4_diametro_der", 0.0
            )
            parametro_barres_e4_b_izq = excel_response.get("barres_e4_b_izq", 0.0)
            parametro_barres_e4_b_der = excel_response.get("barres_e4_b_der", 0.0)
            parametro_barres_e4_a_izq = excel_response.get("barres_e4_a_izq", 0.0)
            parametro_barres_e4_a_der = excel_response.get("barres_e4_a_der", 0.0)

            # Setear parámetros en el building element

            if parametro_l1_izquierdo != 0.0:
                self.attributes.add_attribute(id_l1_izquierdo, parametro_l1_izquierdo)
            if parametro_l1_derecho != 0.0:
                self.attributes.add_attribute(id_l1_derecho, parametro_l1_derecho)
            if parametro_l2_izquierdo != 0.0:
                self.attributes.add_attribute(id_l2_izquierdo, parametro_l2_izquierdo)
            if parametro_l2_derecho != 0.0:
                self.attributes.add_attribute(id_l2_derecho, parametro_l2_derecho)
            if parametro_l3_izquierdo != 0.0:
                self.attributes.add_attribute(id_l3_izquierdo, parametro_l3_izquierdo)
            if parametro_l3_derecho != 0.0:
                self.attributes.add_attribute(id_l3_derecho, parametro_l3_derecho)
            if parametro_l4_izquierdo != 0.0:
                self.attributes.add_attribute(id_l4_izquierdo, parametro_l4_izquierdo)
            if parametro_l4_derecho != 0.0:
                self.attributes.add_attribute(id_l4_derecho, parametro_l4_derecho)
            if parametro_e1_izquierdo != 0:
                self.attributes.add_attribute(id_e1_izquierdo, parametro_e1_izquierdo)
            if parametro_e1_derecho != 0:
                self.attributes.add_attribute(id_e1_derecho, parametro_e1_derecho)
            if parametro_e2_izquierdo != 0:
                self.attributes.add_attribute(id_e2_izquierdo, parametro_e2_izquierdo)
            if parametro_e2_derecho != 0:
                self.attributes.add_attribute(id_e2_derecho, parametro_e2_derecho)
            if parametro_e3_izquierdo != 0:
                self.attributes.add_attribute(id_e3_izquierdo, parametro_e3_izquierdo)
            if parametro_e3_derecho != 0:
                self.attributes.add_attribute(id_e3_derecho, parametro_e3_derecho)
            if parametro_peso_total != 0.0:
                self.attributes.add_attribute(id_peso_total, parametro_peso_total)
            if parametro_peso_arm != 0.0:
                self.attributes.add_attribute(id_peso_arm, parametro_peso_arm)
            if parametro_peso_neg != 0.0:
                self.attributes.add_attribute(id_peso_neg, parametro_peso_neg)

            if parametro_barres_B_izquierdo != 0:
                # Verificar si el atributo existe antes de agregarlo
                try:
                    doc = DocumentManager.get_instance().document
                    attrib_type = AllplanBaseElements.AttributeService.GetAttributeType(
                        doc, id_barres_B_izquierdo
                    )
                    if attrib_type:
                        self.attributes.add_attribute(
                            id_barres_B_izquierdo, parametro_barres_B_izquierdo
                        )
                    else:
                        print(
                            f"Advertencia: El atributo con ID {id_barres_B_izquierdo} no está definido en el sistema"
                        )
                except Exception as e:
                    print(f"Error al verificar atributo {id_barres_B_izquierdo}: {e}")
            if parametro_barres_B_derecho != 0:
                self.attributes.add_attribute(
                    id_barres_B_derecho, parametro_barres_B_derecho
                )
            if parametro_barres_B_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_B_diametro_izq, parametro_barres_B_diametro_izq
                )
            if parametro_barres_B_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_B_diametro_der, parametro_barres_B_diametro_der
                )
            if parametro_barres_A_izquierdo != 0:
                self.attributes.add_attribute(
                    id_barres_A_izquierdo, parametro_barres_A_izquierdo
                )
            if parametro_barres_A_derecho != 0:
                self.attributes.add_attribute(
                    id_barres_A_derecho, parametro_barres_A_derecho
                )
            if parametro_barres_A_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_A_diametro_izq, parametro_barres_A_diametro_izq
                )
            if parametro_barres_A_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_A_diametro_der, parametro_barres_A_diametro_der
                )
            if parametro_barres_e1_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_diametro_izq, parametro_barres_e1_diametro_izq
                )
            if parametro_barres_e1_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_diametro_der, parametro_barres_e1_diametro_der
                )
            if parametro_barres_e1_b_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_b_izq, parametro_barres_e1_b_izq
                )
            if parametro_barres_e1_b_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_b_der, parametro_barres_e1_b_der
                )
            if parametro_barres_e1_a_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_a_izq, parametro_barres_e1_a_izq
                )
            if parametro_barres_e1_a_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_a_der, parametro_barres_e1_a_der
                )
            if parametro_barres_e1_separacion_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_separacion_izq, parametro_barres_e1_separacion_izq
                )
            if parametro_barres_e1_separacion_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e1_separacion_der, parametro_barres_e1_separacion_der
                )
            if parametro_barres_e3_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_diametro_izq, parametro_barres_e3_diametro_izq
                )
            if parametro_barres_e3_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_diametro_der, parametro_barres_e3_diametro_der
                )
            if parametro_barres_e3_b_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_b_izq, parametro_barres_e3_b_izq
                )
            if parametro_barres_e3_b_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_b_der, parametro_barres_e3_b_der
                )
            if parametro_barres_e3_a_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_a_izq, parametro_barres_e3_a_izq
                )
            if parametro_barres_e3_a_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e3_a_der, parametro_barres_e3_a_der
                )
            if parametro_barres_e2_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_diametro_izq, parametro_barres_e2_diametro_izq
                )
            if parametro_barres_e2_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_diametro_der, parametro_barres_e2_diametro_der
                )
            if parametro_barres_e2_b_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_b_izq, parametro_barres_e2_b_izq
                )
            if parametro_barres_e2_b_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_b_der, parametro_barres_e2_b_der
                )
            if parametro_barres_e2_a_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_a_izq, parametro_barres_e2_a_izq
                )
            if parametro_barres_e2_a_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e2_a_der, parametro_barres_e2_a_der
                )
            if parametro_barres_s_izquierdo != 0:
                self.attributes.add_attribute(
                    id_barres_s_izquierdo, parametro_barres_s_izquierdo
                )
            if parametro_barres_s_derecho != 0:
                self.attributes.add_attribute(
                    id_barres_s_derecho, parametro_barres_s_derecho
                )
            if parametro_barres_s_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_s_diametro_izq, parametro_barres_s_diametro_izq
                )
            if parametro_barres_s_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_s_diametro_der, parametro_barres_s_diametro_der
                )
            if parametro_barres_e4_diametro_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_diametro_izq, parametro_barres_e4_diametro_izq
                )
            if parametro_barres_e4_diametro_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_diametro_der, parametro_barres_e4_diametro_der
                )
            if parametro_barres_e4_b_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_b_izq, parametro_barres_e4_b_izq
                )
            if parametro_barres_e4_b_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_b_der, parametro_barres_e4_b_der
                )
            if parametro_barres_e4_a_izq != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_a_izq, parametro_barres_e4_a_izq
                )
            if parametro_barres_e4_a_der != 0.0:
                self.attributes.add_attribute(
                    id_barres_e4_a_der, parametro_barres_e4_a_der
                )

            # Mostrar información de parámetros opcionales
            print("Parámetros opcionales:")
            for key, value in excel_response.items():
                if key not in [
                    "base_extremo_izq",
                    "altura_extremo_izq",
                    "largo_extremo_izq",
                    "base_extremo_der",
                    "altura_extremo_der",
                    "largo_extremo_der",
                    "largo_eje_izq",
                    "base_eje_izq",
                    "altura_eje_izq",
                    "largo_eje_der",
                    "base_eje_der",
                    "altura_eje_der",
                ]:
                    print(
                        f"   {key}: {value:.2f} [m] ({'leído desde Excel' if value != 0.0 else 'valor por defecto'})"
                    )

        else:
            print("Usando valores calculados por defecto (Lectura Excel falló)")
            self.build_ele.base_extremo_izq.value = 0.4 * 1000
            self.build_ele.altura_extremo_izq.value = 0.3 * 1000
            self.build_ele.largo_extremo_izq.value = 1.19 * 1000
            self.build_ele.base_extremo_der.value = 0.4 * 1000
            self.build_ele.altura_extremo_der.value = 0.3 * 1000
            self.build_ele.largo_extremo_der.value = 1.19 * 1000
            self.build_ele.base_eje_izq.value = 0.4 * 1000
            self.build_ele.altura_eje_izq.value = 0.45 * 1000
            self.build_ele.largo_eje_izq.value = 2.95 * 1000
            self.build_ele.base_eje_der.value = 0.4 * 1000
            self.build_ele.altura_eje_der.value = 0.45 * 1000
            self.build_ele.largo_eje_der.value = 2.95 * 1000
            self.total_length = self.build_ele.largo_extremo_izq.value + self.build_ele.largo_eje_izq.value + self.build_ele.largo_eje_der.value + self.build_ele.largo_extremo_der.value

        return

    def on_cancel_function(self) -> OnCancelFunctionResult:
        """Maneja la presión de ESC"""
        print("on_cancel_function")
        try:

            if self.state == CANCEL:
                return OnCancelFunctionResult.CANCEL_INPUT

            self.get_values_from_excel()

            concrete = self._build_ferralla_model_elements(AllplanGeometry.Point3D(0,0,0))
            elements = ModelEleList()
            for elem in concrete:
                elements.append_geometry_3d(elem)

            placement_matrix = AllplanGeometry.Matrix3D()
            placement_pnt = self.get_placement_point(self.list_points[0], self.list_points[1])
            angle = self.get_lines_angle(AllplanGeometry.Line3D(placement_pnt, self.list_points[-1]), AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X + self.total_length,placement_pnt.Y, placement_pnt.Z)))
            placement_matrix.Translate(AllplanGeometry.Vector3D(placement_pnt))
            placement_matrix.Rotation(AllplanGeometry.Line3D(placement_pnt, AllplanGeometry.Point3D(placement_pnt.X, placement_pnt.Y, placement_pnt.Z + 100)), angle)

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