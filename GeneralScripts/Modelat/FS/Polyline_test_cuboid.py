""" Example script for Polyline2D/3D
"""
import random

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_BaseElements as AllplanBaseElements
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from CreateElementResult import CreateElementResult
from PythonPartUtil import PythonPartUtil

from TypeCollections.ModelEleList import ModelEleList
from BuildingElement import BuildingElement
from Utils import LibraryBitmapPreview

print('Load Polyline_test.py')

def check_allplan_version(_build_ele: BuildingElement,
                          _version  : str) -> bool:
    """ Check the current Allplan version

    Args:
        _build_ele: building element with the parameter properties
        _version:   the current Allplan version

    Returns:
        True
    """

    # Support all versions
    return True


def create_preview(_build_ele: BuildingElement,
                   _doc      : AllplanEleAdapter.DocumentAdapter) -> CreateElementResult:
    """ Creation of the element preview
ö
    Args:
        _build_ele: building element with the parameter properties
        _doc:       document of the Allplan drawing files

    Returns:
        created elements for the preview
    """

    return CreateElementResult(LibraryBitmapPreview.create_library_bitmap_preview( \
                               f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}"
                               r"Examples\PythonParts\PaletteExamples\GeometryElements\Polyline.png"))


def create_script_object(build_ele         : BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    """ Creation of the script object

    Args:
        build_ele:          building element with the parameter properties
        script_object_data: script object data

    Returns:
        created script object
    """
    build_ele.zUnique.value = random.random() * 3600
    return Polyline(build_ele, script_object_data)


class Polyline(BaseScriptObject):
    """ Definition of class Polyline
    """

    def __init__(self,
                 build_ele         : BuildingElement,
                 script_object_data: BaseScriptObjectData):
        """ Initialization

        Args:
            build_ele:          building element with the parameter properties
            script_object_data: script object data
        """

        super().__init__(script_object_data)

        self.build_ele = build_ele

    def create_cuboid(self, ancho, alto, grosor):
        """_summary_

        Args:
            ancho (_type_): _description_
            alto (_type_): _description_
            grosor (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = ancho,
            width     = alto,
            height    = grosor
        )

        common_props   = AllplanBaseElements.CommonProperties()

        model_ele_list = ModelEleList(common_props)
        model_ele_list.append_geometry_3d(cuboid)

        return model_ele_list

    def execute(self) -> CreateElementResult:
        """ execute the script

        Returns:
            created element result
        """

        build_ele = self.build_ele

        ancho_cuboid = build_ele.AnchoPLD.value
        alto_cuboid = build_ele.LargoPLD.value
        espesor_cuboid = build_ele.EspesorPLD.value

        cuboid = self.create_cuboid(ancho_cuboid, alto_cuboid, espesor_cuboid)

        python_part_util = PythonPartUtil(build_ele.CommonProp2D.value)
        python_part_util.add_pythonpart_view_2d3d(cuboid)

        return CreateElementResult(python_part_util.create_pythonpart(build_ele,
                                                                  type_uuid = "b09d5feb-949f-44d8-99ca-08516a66ea1c",
                                                                  type_display_name = "PythonPart with sub objects"))
