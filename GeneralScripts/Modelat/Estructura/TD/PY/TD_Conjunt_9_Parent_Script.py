"""
Script for horitzontalPP - Vertical - Group
"""
from typing import List, Any, Optional

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_Utility as PythonUtility
import NemAll_Python_IFW_Input as AllplanIFW

import collections
import math
import random
import ctypes
import BuildingElementValueUtil

#from pynput.mouse import Listener
from ScriptObjectInteractors.PointInteractor import PointInteractor, PointInteractorResult

from BaseScriptObject import BaseScriptObject, BaseScriptObjectData

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil

from DocumentManager import DocumentManager
#from BuildingElementInputService import BuildingElementInputService
from typing import List
from AnyValueByType import AnyValueByType

#from .TD_Vertical_PP import PP_TD_Vertical
#from .TD_Horitzontal_PP import PP_TD_Horitzontal
#from .TD_Horitzontal_Inf_PP import PP_TD_Horitzontal_Inf
#from .TD_Horitzontal_Front import TD_Horitzontal_Front
#from .TD_CilindreCancam import CilindreCancam
#from .TD_CilindreForatXPS import CilindreForatXPS
#from .TD_BoxColis import BoxColis
#from .TD_BoxForat import BoxForat
#from .TD_LProvisional import LProvisional
#from .TD_liniaInterior import LiniaInterior
#from .TD_CreateText import TextSpline
#from .TD_CilindreForat import CilindreForat
#from .TD_Horitzontal_reforc import PP_TD_Horitzontal_reforc
#from .EN_Premarc import PP_EN_Premarc

from .TD_Conjunt_8_clase import TD_Conjunt_8
from .EN.EN_Conjunt_8_clase import EN_Conjunt_8
from .IS.IS_Conjunt_8_clase import IS_Conjunt_8

from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
from PythonPartTransaction import PythonPartTransaction
from StringTableService import StringTableService
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementXML import BuildingElementXML


from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from PythonPartUtil import PythonPartUtil
from TypeCollections.ModelEleList import ModelEleList
from TypeCollections.ModificationElementList import ModificationElementList


from BuildingElementAttributeList import BuildingElementAttributeList

from HandleProperties import HandleProperties
from HandleDirection import HandleDirection

from CreateElementResult import CreateElementResult
from Utils import LibraryBitmapPreview, FormatUtil

docAux = AllplanElementAdapter.DocumentAdapter

NombreBarresVertInt = 30
NombreBarresHorInt = 3


print('Load TD_Conjunt.py')

def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    #del build_ele
    #opcionsTD = build_ele.opcionsTD.value
    del version

    # Support all versions
    return True



def create_preview(_build_ele: BuildingElement,
                   _doc      : AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """ Creation of library preview

    Args:
        _build_ele: building element with the parameter properties
        _doc:       document of the Allplan drawing files

    Returns:
        created element result
    """

    return CreateElementResult(LibraryBitmapPreview.create_libary_bitmap_preview( \
                                    AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() +
                                    r"Examples\PythonParts\ServiceExamples\ElementsAttributeService.png"))


def create_script_object( build_ele        : BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    """ Creation of the script object

    Args:
        build_ele:          building element with the parameter properties
        script_object_data: script object data

    Returns:
        created script object
    """

    #return PythonPartElementConnection(build_ele, script_object_data)
    return Conjunt_8_Parent(build_ele, script_object_data)
    #return Conjunt_8_Parent(coord_input, pyp_path, global_str_table_service,
    #                            build_ele_list, build_ele_composite, build_ele_ctrl_props_list, modify_uuid_list)


class Conjunt_8_Parent(BaseScriptObject):
    #def __init__(#self, coord_input, pyp_path, str_table_service):
    #            self,
    #            coord_input              : AllplanIFW.CoordinateInput,
    #            pyp_path                 : str,
    #            str_table_service        : StringTableService,
    #            build_ele_list           : List[BuildingElement],
    #            build_ele_composite      : BuildingElementComposite,
    #            build_ele_ctrl_props_list: List[BuildingElementControlProperties],
    #            modify_uuid_list         : List[str]):
    def __init__(self,
                 build_ele         : BuildingElement,
                 script_object_data: BaseScriptObjectData):
        """ Initialization

        Args:
            build_ele:          building element with the parameter properties
            script_object_data: script object data
        """

        #super().__init__(script_object_data)
        #
        #build_ele = cast(PythonPartElementConnectionBuildingElement, build_ele)
        #
        #self.build_ele = build_ele
        #
        #self.sel_result = SingleElementSelectResult()



        self.coord_input        = script_object_data.coord_input#AllplanGeo.Point3D()#coord_input
        self.pyp_path           = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\PMP\\jerarquia" #pyp_path
        pyp_path = self.pyp_path
        self.str_table_service  = StringTableService(pyp_path) # BuildingElementStringTable#str_table_service
        self.first_point_input  = True
        self.first_point        = AllplanGeo.Point3D()
        self.model_ele_list     = None
        self.build_ele_service  = BuildingElementService()
        self.build_ele_composite= BuildingElementComposite#build_ele_composite
        self.control_props_list = script_object_data.control_props_util#build_ele_ctrl_props_list
        self.build_ele_script   = Any

        #self.conjuntSelected = build_ele_list[0].SelectorPPPare.value
        self.conjuntSelected = build_ele.SelectorPPPare.value

        self.build_ele_list     : List[BuildingElement] = [build_ele]#build_ele_list
        #self.build_ele_list.append(build_ele)
        self.build_ele_list_ind = {
            "Parent" : 0
            }

        self.input_pnt = AllplanGeo.Point3D()

        #self.modify_uuid_list = modify_uuid_list

        ####
        self.current_point      = AllplanGeo.Point3D()
        self.valid_input        = False
        self.b_use_input_pnt    = True
        self.polyline_lenght    = 0.0
        self.frist_run_transf   = True
        self.cont_polyline      = AllplanGeo.Polyline3D()

        self.placement_mat = AllplanGeo.Matrix3D()
        self.point_input_result  = PointInteractorResult()

        self.is_update = False





        #----------------- read the data and show the palette

        try:
            if self.build_ele_list[0].FlagEntrada.value == 1:

                #if self.conjuntSelected != 1:
                    #carregar palette TD
                result, build_ele_script, build_ele_list_TD, control_props_list,    \
                build_ele_composite, part_name, file_name = \
                self.build_ele_service.read_data_from_pyp(pyp_path + "\\TD_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                            self.str_table_service.material_str_table)

                self.build_ele_list.append(build_ele_list_TD[0])
                self.build_ele_list_ind["TD"] = 1

                #carregar palette EN
                result, build_ele_script, build_ele_list_EN, control_props_list,    \
                build_ele_composite, part_name, file_name = \
                self.build_ele_service.read_data_from_pyp(pyp_path + "\\EN\\EN_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                            self.str_table_service.material_str_table)

                self.build_ele_list.append(build_ele_list_EN[0])
                self.build_ele_list_ind["EN"] = 2

                #carregar palette IS
                result, build_ele_script, build_ele_list_IS, control_props_list,    \
                build_ele_composite, part_name, file_name = \
                self.build_ele_service.read_data_from_pyp(pyp_path + "\\IS\\IS_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                            self.str_table_service.material_str_table)

                self.build_ele_list.append(build_ele_list_IS[0])
                self.build_ele_list_ind["IS"] = 3

                #self.build_ele_list[0].FlagEntrada.value = 2

                #self.gestio_palette_fills(pyp_path)
            #else:


        except Exception as e:
            #self.conjunt  =  TD_Conjunt_8(build_ele[1], doc)
            #self.result = self.conjunt.create()
            print("Build_ele del fill " + str(e))

        self.gestio_palette_fills(pyp_path)
        print("TEST Conjunt_9_parent")

        self.INPUT_MODE = 0


    def start_input(self):
        """ start the input
        """

        self.conjuntSelected = self.palette_service.build_ele_list[0].SelectorPPPare.value

        #self.modify_element_property_test()

        self.script_object_interactor = PointInteractor(
            interactor_result = self.point_input_result,
            is_first_input    = True,
            request_text      = "Place the element",
            preview_function  = self.draw_preview(self.point_input_result, self.point_input_result)
        )

        #self.conjuntSelected =

        self.INPUT_MODE = 0

        '''
        if self.coord_input.IsMouseMove(mouse_msg):
            input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                    True).GetPoint()
            self.draw_preview(input_pnt, True)
            return True

        #print("------------- process_mouse_msg: " + str(self.input_pnt))
        if self.first_point_input:
            self.input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                    True).GetPoint()
            #print("process_mouse_msg: " + str(self.input_pnt))

            self.first_point_input = False
            #self.script_object_interactor = None

            self.placement_mat = AllplanGeo.Matrix3D()
            self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))

        self.draw_preview(self.input_pnt, True)
        '''


    '''
    def start_next_input(self):
        """ start the next input
        """
    '''

    def execute(self) -> CreateElementResult:
        """ execute the script

        Returns:
            created element result
        """

        python_part_util = PythonPartUtil()

        cube_element = self.get_cuboid()
        python_part_util.add_pythonpart_view_2d3d(cube_element)
        #python_part_util.add_architecture_elements([cube_element])

        if self.conjuntSelected != 1:
            build_ele = self.build_ele_list[1] #self.palette_service.build_ele_list #self.build_ele_script
            doc = DocumentManager.get_instance().document#self.__doc__

            TD_conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)

            if self.conjuntSelected == 2:
                TD_conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)
            elif self.conjuntSelected == 3:
                TD_conjunt  =  EN_Conjunt_8(self.build_ele_list[2], DocumentManager.get_instance().document)
            elif self.conjuntSelected == 4:
                TD_conjunt  =  IS_Conjunt_8(self.build_ele_list[3], DocumentManager.get_instance().document)

            self.result = TD_conjunt.create()

            model_elem_list = self.result["elements"]
            handle_list = self.result["handles"]
            model_elem_list_preview = self.result["preview_elements"]
            group_elems = self.result["group_elems"]
            group_elems_preview = self.result["group_elems_preview"]

            common_props   = AllplanBaseElements.CommonProperties()

            python_part_util.add_pythonpart_view_2d3d(model_elem_list)

            return CreateElementResult(model_elem_list, handle_list,
                                   multi_placement = False,
                                   placement_point = self.input_pnt)

            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               model_elem_list + cube_element , [], None)
        else:
            cube_element = self.get_cuboid()
            return CreateElementResult(cube_element,
                                   multi_placement = False,
                                   placement_point = self.input_pnt)




    #def execute(self) -> CreateElementResult:
    #    """ execute the script
    #    Returns:
    #        created element result
    #    """
    #
    #
    #    return CreateElementResult(self.create_opening_element(), self.create_handles(),
    #                               multi_placement = True,
    #                               placement_point = AllplanGeo.Point3D())

    def gestio_palette_fills(self, pyp_path):
        if self.conjuntSelected == 1:


            result, self.build_ele_script, self.build_ele_list_PA, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(pyp_path + "\\TD_Conjunt_8_Parent_Script.pal", self.str_table_service.str_table, False,
                                                        self.str_table_service.material_str_table)

            #self.pyp_path = pyp_path + "\\TD_Conjunt_8_Parent.pal"

            if not result:
                return

            #self.file_name = 'c:\\programdata\\nemetschek\\allplan\\2023\\etc\\examples\\pythonparts\\test-david\\td_conjunt_8_parent.pyp'
            #self.file_name = pyp_path + '\\td_conjunt_8_parent.pyp'
            print("- self.file_name: " + str(self.file_name))

            self.palette_service = BuildingElementPaletteService([self.build_ele_list[0]], self.build_ele_composite,#self.build_ele_list_PA, self.build_ele_composite,
                                                                    self.build_ele_script,
                                                                    self.control_props_list, self.file_name)

            #self.palette_service.show_palette(part_name )
            self.palette_service.show_palette("\\TD_Conjunt_8_Parent_Script.pal")
            self.palette_service.refresh_palette([self.build_ele_list[0]], self.control_props_list)
            #self.palette_service.show_page_for_element(0, [] )

            self.conjunt  =  None
            #self.result = self.conjunt.create()

        elif self.conjuntSelected == 2: #TD

            result, self.build_ele_script, self.build_ele_list_TD, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(pyp_path + "\\TD_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                        self.str_table_service.material_str_table)

            if not result:
                return

            self.palette_service = BuildingElementPaletteService([self.build_ele_list[1]],
                                                             self.build_ele_composite,
                                                             self.build_ele_script,#pyp_path + "\\EN\\EN_Conjunt_8.pal",
                                                             self.control_props_list,
                                                             #pyp_path)
                                                             self.file_name)

            self.palette_service.show_palette("TD_Conjunt_8")
            #self.palette_service.refresh_palette([self.build_ele_list[1]], self.control_props_list)
            self.palette_service.show_page_for_element(0, [] )
            self.palette_service.refresh_palette([self.build_ele_list[1]], self.control_props_list)


            build_ele = self.palette_service.build_ele_list
            doc = DocumentManager.get_instance().document

            self.conjunt  =  TD_Conjunt_8(self.build_ele_list[1], doc)
            self.result = self.conjunt.create()

        elif self.conjuntSelected == 3: #EN


            result, self.build_ele_script, self.build_ele_list_EN, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(pyp_path + "\\EN\\EN_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                        self.str_table_service.material_str_table)

            if not result:
                return


            self.palette_service = BuildingElementPaletteService([self.build_ele_list[2]],
                                                             self.build_ele_composite,
                                                             self.build_ele_script,#pyp_path + "\\EN\\EN_Conjunt_8.pal",
                                                             self.control_props_list,
                                                             #pyp_path)
                                                             self.file_name)

            self.palette_service.show_palette("EN_Conjunt_8")#carregar palette
            #self.palette_service.refresh_palette([self.build_ele_list[2]], self.control_props_list)
            self.palette_service.show_page_for_element(0, [] )#mostra la palette del EN
            self.palette_service.refresh_palette([self.build_ele_list[2]], self.control_props_list)#actualitza  pestanyes

            build_ele = self.palette_service.build_ele_list
            doc = DocumentManager.get_instance().document

            self.conjunt  =  EN_Conjunt_8(self.build_ele_list[2], doc)
            self.result = self.conjunt.create()


        elif self.conjuntSelected == 4: #IS

            result, self.build_ele_script, self.build_ele_list_IS, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(pyp_path + "\\IS\\IS_Conjunt_8.pal", self.str_table_service.str_table, False,
                                                        self.str_table_service.material_str_table)

            if not result:
                return

            self.palette_service = BuildingElementPaletteService(self.build_ele_list_IS,#[self.build_ele_list[3]],
                                                             self.build_ele_composite,
                                                             self.build_ele_script,#pyp_path + "\\EN\\EN_Conjunt_8.pal",
                                                             self.control_props_list,
                                                             #pyp_path)
                                                             self.file_name)
#
            self.palette_service.show_palette("IS_Conjunt_8")#carregar palette
            #self.palette_service.refresh_palette([self.build_ele_list[3]], self.control_props_list)
            self.palette_service.refresh_palette([self.build_ele_list[3]], self.control_props_list)#actualitza  pestanyes
            self.palette_service.show_page_for_element(0, [] )#mostra la palette del IS


            build_ele = self.palette_service.build_ele_list
            doc = DocumentManager.get_instance().document

            self.conjunt  =  IS_Conjunt_8(self.build_ele_list[3], doc)
            self.result = self.conjunt.create()

        else:
            print("otro")


    '''
    def set_active_palette_page_index(self, active_page_index: int) -> None:
        #self.palette_active_page = active_page_index

        self.palette_service.show_page_for_element(active_page_index, [0])

        print("palette canviada a pagina :" + str(active_page_index))
    '''


    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any):
        """ Modify property of element

        Args:
            page:  page index of the modified property
            name:  name of the modified property
            value: new value
        """

        self.is_update = True


        print("--1-------------------------------")
        print("modify_element_property " + str(page) + " - " + str(name) + " - " + str(value))
        print("---------------------------------")


        '''
        if name == "SelectorPPPare":
            self.conjuntSelected = value
            try:
                if self.palette_service.build_ele_list[0].SelectorPPPare.value == value:
                    self.is_update = True
                else:
                    self.is_update = False
                    #for nPalette in range(0, len(self.palette_service.build_ele_list)):
                    #    self.palette_service.build_ele_list[nPalette].SelectorPPPare.value = value
                    self.palette_service.build_ele_list[0].SelectorPPPare.value = value
                    self.gestio_palette_fills(self.pyp_path)
            except Exception as e:
                print("SelectorPPPare inexistent " + str(e))
        '''


    def modify_element_property_test(self):

        if len(self.build_ele_list) > 1:
            #self.gestio_palette_fills(self.pyp_path)
            print("self.conjuntSelected: " + str(self.conjuntSelected))
            self.conjuntSelected = self.palette_service.build_ele_list[0].SelectorPPPare.value
            #print("self.conjuntSelected: " + str(self.conjuntSelected))
            if self.conjuntSelected == 2:

                #BuildingElementValueUtil.update_value(name, value, self.build_ele_list[1], self.palette_service.build_ele_ctrl_props_list[0])
                self.conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)

            elif self.conjuntSelected == 3:


                #BuildingElementValueUtil.update_value(name, value, self.build_ele_list[2], self.palette_service.build_ele_ctrl_props_list[0])
                #self.update_palette()
                self.conjunt  =  EN_Conjunt_8(self.build_ele_list[2], DocumentManager.get_instance().document)


            elif self.conjuntSelected == 4:


                #BuildingElementValueUtil.update_value(name, value, self.build_ele_list[3], self.palette_service.build_ele_ctrl_props_list[0])

                self.conjunt  =  IS_Conjunt_8(self.build_ele_list[3], DocumentManager.get_instance().document)

            #else:

                #BuildingElementValueUtil.update_value(name, value, self.build_ele_list[0], self.control_props_list[0])
                #BuildingElementValueUtil.update_value(name, value, self.palette_service.build_ele_list[0], self.palette_service.build_ele_ctrl_props_list[0])
            if self.conjunt != None:
                self.result = self.conjunt.create()
        #else:
        #    #BuildingElementValueUtil.update_value(name, value, self.build_ele_list[0], self.control_props_list[0])
        #    BuildingElementValueUtil.update_value(name, value, self.palette_service.build_ele_list[0], self.palette_service.build_ele_ctrl_props_list[0])


        #print("--2-------------------------------")
        #print("modify_element_property " + str(page) + " - " + str(name) + " - " + str(value))
        #print("----------------------------------")

        print("1. crida a update palette desde modify_element_property")

        if self.is_update:
            print("2. crida a update palette desde modify_element_property")
            self.update_palette()

        print("return true")
        #return True


    def on_cancel_function(self):
        """
        Check for input function cancel in case of ESC

        Returns:
            True/False for success.
        """
        try:
            self.create_element()
            self.palette_service.close_palette()

            #create_element(build_ele= self.build_ele_list, doc = self.__doc__)
        except Exception as e:
            print("on_cancel_function() - self.create_element() not possible")

        return True

    def on_preview_draw(self):
        """
        Handles the preview draw event
        """
        #print("-----on_preview_draw")
        #print("self.first_point_input: " + str(self.first_point_input))
        input_pnt = self.input_pnt

        if self.first_point_input:
            input_pnt = self.coord_input.GetCurrentPoint(self.first_point).GetPoint()
            #self.draw_preview(input_pnt, False)
            #print("--End -- self.draw_preview")
            #return

        #
        #print("-----on_preview_draw")

        self.draw_preview(input_pnt, False)

    def on_mouse_leave(self):
        """
        Handles the mouse leave event
        """
        #print("-----on_mouse_leave")
        self.on_preview_draw()

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        """
        Process the mouse message event

        Args:
            mouse_msg:  the mouse message.
            pnt:        the input point in view coordinates
            msg_info:   additional message info.

        Returns:
            True/False for success.
        """

        #print("process_mouse_msg: ")

        #self.update_palette()

        if self.coord_input.IsMouseMove(mouse_msg):
            input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                    True).GetPoint()
            self.draw_preview(input_pnt, True)
            return True

        #print("------------- process_mouse_msg: " + str(self.input_pnt))
        if self.first_point_input:
            self.input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                    True).GetPoint()
            #print("process_mouse_msg: " + str(self.input_pnt))

            self.first_point_input = False

            self.placement_mat = AllplanGeo.Matrix3D()
            self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))

        self.draw_preview(self.input_pnt, True)

        return True


    def create_element(self):
        """
        Create the element

        Args:
            point_list:  Point list
        """

        python_part_util = PythonPartUtil()

        cube_element = self.get_cuboid()
        python_part_util.add_pythonpart_view_2d3d(cube_element)
        #python_part_util.add_architecture_elements([cube_element])

        if self.conjuntSelected != 1:
            build_ele = self.build_ele_list[1] #self.palette_service.build_ele_list #self.build_ele_script
            doc = DocumentManager.get_instance().document#self.__doc__

            TD_conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)

            if self.conjuntSelected == 2:
                TD_conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)
            elif self.conjuntSelected == 3:
                TD_conjunt  =  EN_Conjunt_8(self.build_ele_list[2], DocumentManager.get_instance().document)
            elif self.conjuntSelected == 4:
                TD_conjunt  =  IS_Conjunt_8(self.build_ele_list[3], DocumentManager.get_instance().document)

            self.result = TD_conjunt.create()

            model_elem_list = self.result["elements"]
            handle_list = self.result["handles"]
            model_elem_list_preview = self.result["preview_elements"]
            group_elems = self.result["group_elems"]
            group_elems_preview = self.result["group_elems_preview"]

            common_props   = AllplanBaseElements.CommonProperties()

            python_part_util.add_pythonpart_view_2d3d(model_elem_list)


            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               model_elem_list + cube_element , [], None)
        else:
            cube_element = self.get_cuboid()
            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               cube_element , [], None)


        #python_part_util.add_pythonpart_view_2d3d(cube_element)

        #python_part_util.add_architecture_elements([cube_element])



        pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())
        base_elems = pyp_transaction.execute(
            placement_matrix= AllplanGeo.Matrix3D(),
            view_world_projection= AllplanIFW.ViewWorldProjection(),
            model_ele_list=
                python_part_util.create_pythonpart(
                    self.build_ele_list,
                    type_display_name = "PythonPart Parent with child objects",
                    placement_matrix=self.placement_mat
                ),
            modification_ele_list= ModificationElementList(),
            uuid_parameter_name = "test_uuid",
            #modify_uuid_list = self.modify_uuid_list
            # elements_to_delete=build_ele.created_elems.value
        )


    def update_palette(self) -> bool:
        """ Update the palette

        Args:
            end_node:            number of the end node for the palette
            update_from_palette: the update of the palette is executed from the palette itself
            _show_pal_close_btn: show close button in the palette True/False

        Returns:
            True
        """


        #----------------- update the palette
        print(" -------- update_palette")

        #self.palette_service.refresh_palette([self.build_ele_list[self.conjuntSelected-1]], self.control_props_list)

        if self.conjuntSelected == 2:
            self.conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)
        if self.conjuntSelected == 3:
            self.conjunt  =  EN_Conjunt_8(self.build_ele_list[2], DocumentManager.get_instance().document)
        if self.conjuntSelected == 4:
            self.conjunt  =  IS_Conjunt_8(self.build_ele_list[3], DocumentManager.get_instance().document)

        return True

    def draw_preview(self, input_pnt, b_use_input_pnt):

        #print("----draw_preview")

        #build_ele = self.palette_service.build_ele_list
        #doc = self.__doc__
        doc = DocumentManager.get_instance().document
        #self.conjunt = TD_Conjunt_8(build_ele[0], doc)
        #if self.conjunt != None:
        #    self.result = self.conjunt.create()
        #print("--doc --draw_preview")


        try:
            #print("--try --draw_preview")
            self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))
            #print("--setTranslation --draw_preview")


            #if self.first_point_input:
            #    #print("--first_point_input --draw_preview")
            #    self.placement_mat = AllplanGeo.Matrix3D()
            #    self.placement_mat.SetTranslation(AllplanGeo.Vector3D(input_pnt))

            #print("--PreDrawElementPreview --draw_preview")
            if self.conjunt != None:
                #self.result = self.conjunt.create()
                try:
                    if self.result == None:
                        print(self.result)
                except Exception as e:
                    print("self.result inexistent: " + str(e))
                #print("----------------------------------------------------------")
                #print(self.result)
                '''
                python_part_util = PythonPartUtil()

                cube_element = self.get_cuboid()
                model_elem_list_preview = self.result["preview_elements"]
                python_part_util.add_pythonpart_view_2d3d(model_elem_list_preview)

                pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())
                base_elems = pyp_transaction.execute(
                    placement_matrix= AllplanGeo.Matrix3D(),
                    view_world_projection= AllplanIFW.ViewWorldProjection(),
                    model_ele_list=
                        python_part_util.create_pythonpart(
                            self.build_ele_list,
                            type_display_name = "PythonPart Preview Parent with child objects",
                            placement_matrix=self.placement_mat
                        ),
                    modification_ele_list= ModificationElementList(),
                    uuid_parameter_name = "test_uuid",
                    #modify_uuid_list = self.modify_uuid_list
                    # elements_to_delete=build_ele.created_elems.value
                )
                '''
                AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                                    self.placement_mat,
                                                    self.result["preview_elements"], True, True)

            else:
                AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                                self.placement_mat,#AllplanGeo.Matrix3D(),
                                                self.get_cuboid(), False, True)
            #print("--PostDrawElementPreview --draw_preview")
        except Exception as e:
            print("No hi ha cap Conjunt seleccionat: " + str(e))
            #AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
            #                                    self.placement_mat,#AllplanGeo.Matrix3D(),
            #                                    self.get_cuboid(), False, True)


        #print("--End -- draw_preview")
        #actulitzar valors pallete
        #self.palette_service.show_palette()

    def on_control_event(self, event_id: int):
        #print("self.On_control_event")
        #print("event_id: " + str(event_id))

        if self.conjunt != None:
            if self.conjuntSelected == 2:
                self.conjunt.on_control_event(self.build_ele_list[1], event_id)
            elif self.conjuntSelected == 3:
                self.conjunt.on_control_event(self.build_ele_list[2], event_id)
            elif self.conjuntSelected == 4:
                self.conjunt.on_control_event(self.build_ele_list[3], event_id)



    def get_cuboid(self) -> ModelEleList:
        length = 0
        width = 0

        #if (self.axis_x):
        #    length = self.x + 50
        #    width = (0 - self.thickness) - 50
        #elif(self.axis_y):
        #    length = self.thickness + 50
        #    width = self.y + 50

        # print("------------------POSITION CREATE CUBE-------------------------------")
        # print(self.position)
        # print("-------------------------------------------------")
        posCuboid = AllplanGeo.Point3D()
        posCuboid.X = - 100
        posCuboid.Y = - 100
        self.cuboid_geo     = AllplanGeo.Polyhedron3D.CreateCuboid(AllplanGeo.AxisPlacement3D(posCuboid),
                                                                   200.,200.,200.)

        common_props   = AllplanBaseElements.CommonProperties()
        model_ele_list = ModelEleList(common_props)
        model_ele_list.append_geometry_3d(self.cuboid_geo)

        return model_ele_list