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
from ScriptObjectInteractors.SingleElementSelectInteractor import SingleElementSelectInteractor, SingleElementSelectResult
from ScriptObjectInteractors.MultiElementSelectInteractor import MultiElementSelectInteractor, MultiElementSelectInteractorResult

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

from .TD.PY.TD_Conjunt_8_clase_PPTD_Solids import TD_Conjunt_8
from .EN.PY.EN_Conjunt_8_clase_PPEN import EN_Conjunt_8
#from .IS.PY.IS_Conjunt_8_clase_PPIS import IS_Conjunt_8
#from .IS.PY.IS_Conjunt_8_clase_PPIS_Tubes import IS_Conjunt_8
from .IS.PY.IS_Conjunt_8_clase_PPIS_Tubes_Simple import IS_Conjunt_8

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

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult
from PreviewSymbols import PreviewSymbols

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
    build_ele.zUnique.value =  random.random() * 3600

    return Conjunt_8_Parent(build_ele, script_object_data)

    #return Conjunt_8_Parent(coord_input, pyp_path, global_str_table_service,
    #                            build_ele_list, build_ele_composite, build_ele_ctrl_props_list, modify_uuid_list)


    '''
    TD_conjunt  =  TD_Conjunt_8(build_ele, doc)
    result = TD_conjunt.create()

    #model_elem_list = result["elements"]
    handle_list = result["handles"]
    #model_elem_list_preview = result["preview_elements"]
    group_elems = result["group_elems"]
    group_elems_preview = result["group_elems_preview"]




    pythonpartgroup = Conjunt_8_Parent (build_ele.NomTD.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)


    model_elem_list = pythonpartgroup.create()

    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview)
                                #preview_elements=   model_elem_list_preview)
    '''


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

        super().__init__(script_object_data)
        #
        #build_ele = cast(PythonPartElementConnectionBuildingElement, build_ele)
        #

        #def crearLlistaVerticals(build_ele):
        try:
            for barra in range(0, build_ele.IntegerTDSelector.value):
                if barra >= len(build_ele.valueListBarresComboBox.value):
                    build_ele.valueListBarresComboBox.value.append("Tub " + str(barra))
                else:
                    build_ele.valueListBarresComboBox.value[barra] = "Tub " + str(barra)
        except Exception as e:
            print("No existeix la llista valueListBarresComboBox al PYP")

        self.build_ele = build_ele

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


        #selection elements
        self.element_list = []
        self.element_list3D = []
        self.element_listTD = []
        self.paredTD        = []
        self.element_listEN = []
        self.element_listIS = []

        self.list_of_build_ele : List[BuildingElement] = []



        self.selection_result = MultiElementSelectInteractorResult()



        #----------------- read the data and show the palette


        print("TEST Conjunt_9_parent")

        self.INPUT_MODE = 0


    def start_input(self):
        """ start the input
        """

        print("start_input START")

        self.conjuntSelected = self.build_ele.SelectorPPPare.value

        self.doc = self.coord_input.GetInputViewDocument()

        allowed_types = [AllplanElementAdapter.Beam_TypeUUID,
                        AllplanElementAdapter.Column_TypeUUID]

        selection_filter = allowed_types

        self.script_object_interactor = MultiElementSelectInteractor(
            self.selection_result,
            None, #selection_filter,
            prompt_msg = "Selecciona els elements"
        )


    def start_next_input(self):
        """ start the next input
        """
        print("start_next_input ")

        if not bool(self.element_list):
            print("not bool(self.element_list) ")
            self.element_list = [
                element
                for element in self.selection_result.sel_elements#GetSelectedElements(self.doc)
                #for element in self.post_element_selection.GetSelectedElements(self.doc)
            ]

            #print("self.element_list: ")
            #print(self.element_list)

            list_adapters = AllplanElementAdapter.BaseElementAdapterList()

            for elem in self.element_list:
                #self.element_list3D.append(elem)
                #msg = self.get_msg(elem)
                attribues = self.get_atributes_from_solid(elem)
                #PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
                list_adapters.append(elem)

                atribPersKey = str(1947)

                if atribPersKey in attribues:
                    if attribues[atribPersKey] == "TD" or attribues[atribPersKey] == "Porta" or attribues[atribPersKey] == "Finestra":
                        self.build_ele.SelectorPPPare.value = 2
                        self.conjuntSelected = 2
                        if attribues[atribPersKey] != "TD":
                            self.element_listTD.append(elem)
                        else:
                            self.paredTD.append(elem)
                    elif attribues[atribPersKey] == "EN":
                        self.build_ele.SelectorPPPare.value = 3
                        self.conjuntSelected = 3
                        self.element_listEN.append(elem)
                    elif attribues[atribPersKey] == "IS":
                        self.build_ele.SelectorPPPare.value = 4
                        self.conjuntSelected = 4
                        self.element_listIS.append(elem)
                    else:
                        self.build_ele.SelectorPPPare.value = 1
                        self.conjuntSelected = 1


                '''
                # Append attribute
                thisElem = AllplanElementAdapter.BaseElementAdapterList()
                thisElem.append(elem)
                AllplanBaseElements.ElementsAttributeService.ChangeAttribute(2447, 'TEST', thisElem)
                '''

            AllplanIFW.HighlightService.HighlightElements(list_adapters)

            #self.script_object_interactor = None

            #return True


        self.script_object_interactor = PointInteractor(
            interactor_result = self.point_input_result,
            is_first_input    = True,
            request_text      = "Place the element",
            preview_function  = self.draw_preview_point
        )
        if self.point_input_result.input_point != PointInteractorResult():
            self.input_pnt = self.point_input_result.input_point
            self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))
            if self.point_input_result.input_point != AllplanGeo.Point3D(0,0,0):
                print(self.input_pnt)
                self.script_object_interactor = None


    def get_atributes_from_solid(self, elem: AllplanElementAdapter.BaseElementAdapter):

        listAtrib = {}

        for attribute in elem.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAll):
            #msg += "\t" + str(attribute[0]) + " " + str(AllplanBaseElements.AttributeService.GetAttributeName(self.doc, attribute[0])) + "=" + str(attribute[1]) + "\n"
            #print( "\t" + str(attribute[0]) + " " + str(AllplanBaseElements.AttributeService.GetAttributeName(self.doc, attribute[0])) + "=" + str(attribute[1]) + "\n")
            #listAtrib[numIDAtt] = valueAtt
            listAtrib[str(attribute[0])] = str(attribute[1])
        return listAtrib


    def execute(self) -> CreateElementResult:
        """ execute the script

        Returns:
            created element result
        """
        print("execute START")

        python_part_util = PythonPartUtil()

        cube_element = self.get_cuboid()
        python_part_util.add_pythonpart_view_2d3d(cube_element)
        #python_part_util.add_architecture_elements([cube_element])

        #self.conjuntSelected = self.build_ele.SelectorPPPare.value






        if self.conjuntSelected != 1:

            llargadaPerAfegir = 0
            llargadaAfegida = 0
            ultimAfegit = False

            pared_model_elem_list = []
            pared_handle_list = []
            preview_symbols = PreviewSymbols()

            doc = DocumentManager.get_instance().document#self.__doc__

            llargada, amplada, alcada = self.values_from_solid3D(self.paredTD)

            print("largada pieza: " + str(llargada))
            print("Amplio pieza: " + str(amplada))
            print("Altura pieza: " + str(alcada))



            cube_element = self.get_cuboid()
            print("retorna Cube")
            return CreateElementResult(cube_element,
                                   multi_placement = False,
                                   placement_point = self.input_pnt)



        else:
            cube_element = self.get_cuboid()
            print("retorna Cube")
            return CreateElementResult(cube_element,
                                   multi_placement = False,
                                   placement_point = self.input_pnt)


    def modify_element_property(self, _name: str, _value: Any) -> bool:

        """ Modify property of element

        Args:
            page:  page index of the modified property
            name:  name of the modified property
            value: new value
        """
        #                        self,
        #                        page : int,
        #                        name : str,
        #                        value: Any):

        print("modify_element_property")
        return True


    def on_cancel_function(self):
        """
        Check for input function cancel in case of ESC

        Returns:
            True/False for success.
        """
        print("on_cancel_function START")

        try:
            self.create_element()
            #self.palette_service.close_palette()

            #create_element(build_ele= self.build_ele_list, doc = self.__doc__)
        except Exception as e:
            print("on_cancel_function() - self.create_element() not possible")


        self.script_object_interactor = None    # terminate the selection interactor
        return OnCancelFunctionResult.CANCEL_INPUT


        return True

    def on_preview_draw(self):
        """
        Handles the preview draw event
        """
        print("on_preview_draw START")
        #print("-----on_preview_draw")
        #print("self.first_point_input: " + str(self.first_point_input))
        input_pnt = self.input_pnt

        if self.first_point_input:
            input_pnt = self.coord_input.GetCurrentPoint(self.first_point).GetPoint()
            self.draw_preview(input_pnt, False)
            print("--End -- self.draw_preview")
            return

        #
        #print("-----on_preview_draw")

        self.draw_preview(input_pnt, False)

        print("on_preview_draw END")


    def on_mouse_leave(self):
        """
        Handles the mouse leave event
        """
        print("-----on_mouse_leave")
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

        print("process_mouse_msg: ")

        #self.update_palette()

        if self.coord_input.IsMouseMove(mouse_msg):
            input_pnt = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, self.current_point,
                                                    True).GetPoint()
            self.draw_preview(input_pnt, True)
            return True

        #print("------------- process_mouse_msg: " + str(self.input_pnt))
        if self.first_point_input or self.placement_mat != AllplanGeo.Matrix3D():
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

        print("create_element _ ")

        python_part_util = PythonPartUtil()

        cube_element = self.get_cuboid()
        python_part_util.add_pythonpart_view_2d3d(cube_element)
        #python_part_util.add_architecture_elements([cube_element])

        if self.conjuntSelected != 1:
            llargadaPerAfegir = 0
            llargadaAfegida = 0
            ultimAfegit = False

            build_ele = self.build_ele #self.build_ele_list[1] #self.palette_service.build_ele_list #self.build_ele_script
            doc = DocumentManager.get_instance().document#self.__doc__

            TD_conjunt  =  TD_Conjunt_8(build_ele, DocumentManager.get_instance().document)

            for nBuild_ele in range( len(self.list_of_build_ele)):

                if self.conjuntSelected == 2:
                    llargada, amplada, alcada = self.values_from_solid3D(self.paredTD)
                    #llargadaActual = llargada
                    llargadaActual = llargada - llargadaAfegida

                    posNovaMatrix = AllplanGeo.Matrix3D()
                    posNovaMatrix.SetValue(12, self.point_input_result.input_point.X)
                    posNovaMatrix.SetValue(13, self.point_input_result.input_point.Y)
                    posNovaMatrix.SetValue(14, self.point_input_result.input_point.Z)
                    '''
                    if llargadaAfegida != 0:
                        posNovaMatrix.SetValue(12, self.point_input_result.input_point.X + llargadaAfegida)

                    if llargadaActual > 5750:
                        llargadaActual = 5750
                        llargadaAfegida += 5750
                    else:
                        llargadaAfegida += llargadaActual
                        ultimAfegit =True
                    '''
                    ultimAfegit =True
                    TD_conjunt  =  TD_Conjunt_8(self.build_ele, DocumentManager.get_instance().document, placement_mat= posNovaMatrix, element_listTD = self.element_listTD, BarraLlargada=llargadaActual, TDAlcada = alcada)
                    #TD_conjunt  =  TD_Conjunt_8(self.list_of_build_ele[nBuild_ele], DocumentManager.get_instance().document, placement_mat= posNovaMatrix, BarraLlargada=llargadaActual, TDAlcada = alcada)#, element_listTD = self.element_listTD)#, BarraLlargada=llargada, TDAlcada = alcada)
                    #TD_conjunt  =  TD_Conjunt_8(build_ele, DocumentManager.get_instance().document, self.placement_mat)#,self.placement_mat)
                    #TD_conjunt.transform(self.placement_mat)
                    #TD_conjunt.move(self.placement_mat)
                elif self.conjuntSelected == 3:
                    TD_conjunt  =  EN_Conjunt_8(build_ele, DocumentManager.get_instance().document, self.placement_mat)
                elif self.conjuntSelected == 4:
                    TD_conjunt  =  IS_Conjunt_8(build_ele, DocumentManager.get_instance().document, placement_mat=self.placement_mat, element_listIS=self.element_listIS)

                self.conjunt = TD_conjunt
                self.result = TD_conjunt.create()

                model_elem_list = self.result["elements"]
                handle_list = self.result["handles"]
                model_elem_list_preview = self.result["preview_elements"]
                group_elems = self.result["group_elems"]
                group_elems_preview = self.result["group_elems_preview"]

                common_props   = AllplanBaseElements.CommonProperties()

                python_part_util.add_pythonpart_view_2d3d(model_elem_list)
                print("acaba en CONJUNT")


            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               model_elem_list + cube_element , [], None)
        else:
            cube_element = self.get_cuboid()
            print("acaba en cub")
            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               cube_element , [], None)


        #python_part_util.add_pythonpart_view_2d3d(cube_element)

        #python_part_util.add_architecture_elements([cube_element])


        print("pyp_transaction -- 1")
        #self.build_ele.zUnique.value =  random.random() * 3600
        pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())
        base_elems = pyp_transaction.execute(
            placement_matrix =  AllplanGeo.Matrix3D(),
            view_world_projection= AllplanIFW.ViewWorldProjection(),
            model_ele_list=
                python_part_util.create_pythonpart(
                    self.build_ele_list,
                    type_display_name = "PythonPart Parent with child objects",
                    #placement_matrix = AllplanGeo.Matrix3D(),
                    placement_matrix = self.placement_mat,
                    local_placement_matrix = AllplanGeo.Matrix3D()
                ),
            modification_ele_list= ModificationElementList(),
            uuid_parameter_name = "Pared Python",
            #modify_uuid_list = self.modify_uuid_list
            # elements_to_delete=build_ele.created_elems.value
        )

        print("Conjunt_creat")

        #return pyp_transaction


        #return CreateElementResult(base_elems,
        #                       multi_placement = True)


        #return CreateElementResult(model_elem_list, handle_list,
        #                        multi_placement = True,
        #                        placement_point = self.input_pnt)#,

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

        #if self.conjuntSelected == 2:
        #    self.conjunt  =  TD_Conjunt_8(self.build_ele_list[1], DocumentManager.get_instance().document)
        #if self.conjuntSelected == 3:
        #    self.conjunt  =  EN_Conjunt_8(self.build_ele_list[2], DocumentManager.get_instance().document)
        #if self.conjuntSelected == 4:
        #    self.conjunt  =  IS_Conjunt_8(self.build_ele_list[3], DocumentManager.get_instance().document)

        return True

    def draw_preview(self, input_pnt, b_use_input_pnt):

        print("----draw_preview")

        #build_ele = self.palette_service.build_ele_list
        #doc = self.__doc__
        doc = DocumentManager.get_instance().document
        #self.conjunt = TD_Conjunt_8(build_ele[0], doc)
        #if self.conjunt != None:
        #    self.result = self.conjunt.create()
        #print("--doc --draw_preview")

        #self.gestio_palette_fills(self.pyp_path)


        try:
            #print("--try --draw_preview")
            self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))
            #print("--setTranslation --draw_preview")


            #if self.first_point_input:
            #    #print("--first_point_input --draw_preview")
            #    self.placement_mat = AllplanGeo.Matrix3D()
            #    self.placement_mat.SetTranslation(AllplanGeo.Vector3D(input_pnt))

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
                #self.build_ele.zUnique.value =  random.random() * 3600
                AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                                    self.placement_mat,
                                                    self.result["elements"], True, True)

                return None
            else:
                #self.build_ele.zUnique.value =  random.random() * 3600
                AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                                self.placement_mat,#AllplanGeo.Matrix3D(),
                                                self.get_cuboid(), False, True)
                return None

            #print("--PostDrawElementPreview --draw_preview")
        except Exception as e:
            print("No hi ha cap Conjunt seleccionat: " + str(e))
            #return False
            #AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
            #                                    self.placement_mat,#AllplanGeo.Matrix3D(),
            #                                    self.get_cuboid(), False, True)

        return None

        #print("--End -- draw_preview")
        #actulitzar valors pallete
        #self.palette_service.show_palette()

    def draw_preview_point(self):
        preview_symbols = PreviewSymbols()
        #preview_symbols.add_text("Select position", AllplanGeo.Point3D(), )

        placement_matrix = AllplanGeo.Matrix3D()
        placement_matrix.SetTranslation(
            AllplanGeo.Vector3D(
                self.point_input_result.input_point
            )
        )

        preview_symbols.draw(
            placement_matrix,
            self.coord_input.GetViewWorldProjection()
        )

    def on_control_event(self, event_id: int):
        #print("self.On_control_event")
        #print("event_id: " + str(event_id))

        if self.conjunt != None:
            '''
            if self.conjuntSelected == 2:
                self.conjunt.on_control_event(self.build_ele_list[1], event_id)
            elif self.conjuntSelected == 3:
                self.conjunt.on_control_event(self.build_ele_list[2], event_id)
            elif self.conjuntSelected == 4:
                self.conjunt.on_control_event(self.build_ele_list[3], event_id)
            '''
            self.conjunt.on_control_event(self.build_ele, event_id)



    def values_from_solid3D(self, element_list):#build_ele, placement_mat, element_list):

        amplada  = 0 #max 2150
        llargada = 0 #max 5650

        iniciConjunt = True
        puntInferiorEsqIS = AllplanGeo.Point3D()
        puntInferiorDreIS = AllplanGeo.Point3D()
        puntSuperiorEsqIS = AllplanGeo.Point3D()
        puntSuperiorDreIS = AllplanGeo.Point3D()
        puntAltIS         = AllplanGeo.Point3D()
        puntBaixIS         = AllplanGeo.Point3D()

        llargada = 5750
        amplada = 2500


        llistaPosicions = []
        pos = 0
        for element in element_list:

            puntEsq = 0
            puntDre = 0
            puntInf = 0
            puntSup = 0
            puntAlt = 0
            puntBaix = 0

            #print(element.GetGeometry())
            #print(element.GetModelGeometry())
            geo = element.GetGeometry()
            llistaVertex = geo.GetVertices()

            inici = True
            for vert in llistaVertex:
                if inici:
                    #puntInferiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                    #puntInferiorDre = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                    #puntSuperiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                    #puntSuperiorDre = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)

                    puntEsq = vert.X
                    puntDre = vert.X
                    puntInf = vert.Y
                    puntSup = vert.Y
                    puntAlt = vert.Z
                    puntBaix= vert.Z

                    inici = False
                else:

                    if vert.X <= puntEsq:
                        puntEsq = vert.X
                    if vert.X >= puntDre:
                        puntDre = vert.X
                    if vert.Y <= puntInf:
                        puntInf = vert.Y
                    if vert.Y >= puntSup:
                        puntSup = vert.Y
                    if vert.Z >= puntAlt:
                        puntAlt = vert.Z
                    if vert.Z <= puntBaix:
                        puntBaix = vert.Z

            #puntElement
            puntInferiorEsq = AllplanGeo.Point3D(puntEsq, puntInf, 0)
            puntInferiorDre = AllplanGeo.Point3D(puntDre, puntInf, 0)
            puntSuperiorEsq = AllplanGeo.Point3D(puntEsq, puntSup, 0)
            puntSuperiorDre = AllplanGeo.Point3D(puntDre, puntSup, 0)
            puntAlt = AllplanGeo.Point3D(0, 0, puntAlt)
            puntBaix = AllplanGeo.Point3D(0, 0, puntBaix)


            #posicionsElement
            newPos = [puntInferiorEsq, puntInferiorDre, puntSuperiorEsq, puntSuperiorDre]
            llistaPosicions.append(newPos)

            if iniciConjunt:
                puntInferiorEsqIS = AllplanGeo.Point3D(puntInferiorEsq.X, puntInferiorEsq.Y, 0)#puntInferiorEsq
                puntInferiorDreIS = AllplanGeo.Point3D(puntInferiorDre.X, puntInferiorDre.Y, 0)#puntInferiorDre
                puntSuperiorEsqIS = AllplanGeo.Point3D(puntSuperiorEsq.X, puntSuperiorEsq.Y, 0)#puntSuperiorEsq
                puntSuperiorDreIS = AllplanGeo.Point3D(puntSuperiorDre.X, puntSuperiorDre.Y, 0)#puntSuperiorDre
                puntAltIS           = AllplanGeo.Point3D(0, 0, puntAlt.Z)#puntAlt
                puntBaixIS          = AllplanGeo.Point3D(0, 0, puntBaix.Z)#puntBaix
                iniciConjunt = False

            if puntInferiorDre.X >= puntInferiorDreIS.X :
                puntInferiorDreIS.X = puntInferiorDre.X
            if puntInferiorDre.Y <= puntInferiorDreIS.Y:
                puntInferiorDreIS.Y = puntInferiorDre.Y
            if puntInferiorEsq.X <= puntInferiorEsqIS.X:
                puntInferiorEsqIS.X = puntInferiorEsq.X
            if puntInferiorEsq.Y <= puntInferiorEsqIS.Y:
                puntInferiorEsqIS.Y = puntInferiorEsq.Y
            if  puntSuperiorDre.X >= puntSuperiorDreIS.X:
                puntSuperiorDreIS.X = puntSuperiorDre.X
            if puntSuperiorDre.Y >= puntSuperiorDreIS.Y:
                puntSuperiorDreIS.Y = puntSuperiorDre.Y
            if  puntSuperiorEsq.X <= puntSuperiorEsqIS.X:
                puntSuperiorEsqIS.X = puntSuperiorEsq.X
            if puntSuperiorEsq.Y >= puntSuperiorEsqIS.Y:
                puntSuperiorEsqIS.Y = puntSuperiorEsq.Y
            if puntAlt.Z >= puntAltIS.Z:
                puntAltIS.Z = puntAlt.Z
            if puntBaix.Z <= puntBaixIS.Z:
                puntBaixIS.Z = puntBaix.Z


            pos += 1


        llargada = puntInferiorEsqIS.GetDistance(puntInferiorDreIS)
        llargada = puntInferiorDreIS.X - puntInferiorEsqIS.X
        amplada = puntInferiorEsqIS.GetDistance(puntSuperiorEsqIS)
        amplada = puntSuperiorEsqIS.Y - puntInferiorEsqIS.Y
        alcada = puntBaixIS.GetDistance(puntAltIS)
        alcada = puntAltIS.Z - puntBaixIS.Z

        #build_ele.ISAmplada.value  = amplada
        return llargada, amplada, alcada



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

class Object3DFilter():
    """ implementation of the 3D object filter """

    def __call__(self, element: AllplanElementAdapter.BaseElementAdapter):
        """ execute the filtering

        Args:
            element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

        return element.Is3DElement()