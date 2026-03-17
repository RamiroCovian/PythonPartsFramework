"""
Script Name: SwitchScript
Description: PythonPart para crear un interruptor inteligente
Author: Diego Ferreyra
"""
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_BaseElements as AllplanBase
import NemAll_Python_AllplanSettings as AllplanGlobalSettings
import NemAll_Python_BasisElements as AllplanBasisElements

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList

from .switch_object import SwitchObject


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    """Genera la vista previa del PythonParts."""
    common_prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    first_prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
    first_prop.Color = 17

    switch_parts = SwitchObject.create_switch_geometry()
    model_ele_list = ModelEleList()

    for index, geometry_item in enumerate(switch_parts):
        if geometry_item:
            prop = first_prop if index == 0 else common_prop
            model_ele_list.append(AllplanBasisElements.ModelElement3D(prop, geometry_item))

    return model_ele_list, []

def create_script_object(build_ele, script_object_data):
    return SwitchScript(build_ele, script_object_data)


class SwitchScript(BaseScriptObject):
    def __init__(self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.coord_input = script_object_data.coord_input
        self.device_type = "switch"
        self.z_relative = 1000 # DISTANCIA ENTRE EL PISO Y EL OBJETO
        self.floor_index = 0
        self.floor_count = 0
        self.z_absolute = 0
        self.model_ele_list = ModelEleList()

    # -------------------------------------------------------------------------
    # OBTIENE CANTIDAD DE PLANTAS DEFINIDAS COMO ROOM O STORY
    # -------------------------------------------------------------------------
    def _get_floor_count(self) -> tuple:
        """Obtiene las alturas Z de las stories o rooms del modelo."""
        elements = AllplanBase.ElementsSelectService.SelectAllElements(
            self.coord_input.GetActiveViewDocument()
        )
        stories = []
        coord_z = set()

        for el in elements:
            if el.GetDisplayName() in ("Story", "Room"):
                vertices = el.GetModelGeometry().GetVertices()
                stories.append(vertices)
                z_values = [p.Z for p in vertices]
                coord_z.update([float(min(z_values)), float(max(z_values))])

        coord_z_sorted = sorted(coord_z)

        if len(coord_z_sorted) > 1:
            coord_z_sorted = coord_z_sorted[:-1]

        return coord_z_sorted, len(stories)

    # -------------------------------------------------------------------------
    # OBTIENE EL PISO DE ACUERDO A LA POSICION DEL MOUSE EN EL OBJETO 3D
    # -------------------------------------------------------------------------
    def _get_floor_index(self, click_z, coord_z_sorted) -> int:
        """Determina el índice del piso según la coordenada Z del clic."""
        if not coord_z_sorted:
            return 0

        if click_z < 0:
            return -1

        for i in range(len(coord_z_sorted) - 1):
            if coord_z_sorted[i] <= click_z < coord_z_sorted[i + 1]:
                return i

        return int(len(coord_z_sorted) - 1)

    # -------------------------------------------------------------------------
    # SETEA LAS VARIABLES DEFINIDAS EN EL FILE .PYP
    # -------------------------------------------------------------------------
    def _set_build_ele_params(self) -> None:
        """Asigna los valores calculados al BuildingElement."""
        self.build_ele.FLOOR_INDEX.value = self.floor_index
        self.build_ele.Z_ABSOLUTE.value = self.z_absolute
        self.build_ele.FLOOR_COUNT.value = self.floor_count
        self.build_ele.Z_RELATIVE.value = self.z_relative
        self.build_ele.DEVICE_TYPE.value = self.device_type

    # -------------------------------------------------------------------------
    # CREA OBJETO 3D
    # -------------------------------------------------------------------------
    def _create_geometry_elements(self, position) -> None:
        """Crea los elementos 3D del interruptor transformados a la posición."""
        switch_parts = SwitchObject.create_switch_geometry()

        mat = AllplanGeometry.Matrix3D()
        mat.SetTranslation(AllplanGeometry.Vector3D(position.X, position.Y, position.Z))

        common_prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        first_prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
        first_prop.Color = 17

        for index, geometry_item in enumerate(switch_parts):
            if not geometry_item:
                continue
            transformed_geo = AllplanGeometry.Transform(geometry_item, mat)
            prop = first_prop if index == 0 else common_prop
            element = AllplanBasisElements.ModelElement3D(prop, transformed_geo)
            self.model_ele_list.append(element)

    # -------------------------------------------------------------------------
    # EJECUCIÓN PRINCIPAL
    # -------------------------------------------------------------------------
    def execute(self) -> CreateElementResult:
        """Ejecuta la creación del interruptor en la posición seleccionada."""
        input_pt = self.coord_input.GetCurrentPoint().GetPoint()
        click_z = input_pt.Z

        coord_z_sorted, self.floor_count = self._get_floor_count()
        self.floor_index = self._get_floor_index(click_z, coord_z_sorted)
        self.z_absolute = click_z + self.z_relative

        self._set_build_ele_params()

        position = AllplanGeometry.Point3D(input_pt.X, input_pt.Y, self.z_absolute)
        self._create_geometry_elements(position)

        return CreateElementResult(self.model_ele_list)
