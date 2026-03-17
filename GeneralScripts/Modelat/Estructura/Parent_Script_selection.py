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
import json
import xml.etree.ElementTree as ElementTree
import os
import re
import subprocess


#from pynput.mouse import Listener
from ScriptObjectInteractors.PointInteractor import PointInteractor, PointInteractorResult
from ScriptObjectInteractors.SingleElementSelectInteractor import SingleElementSelectInteractor, SingleElementSelectResult
from ScriptObjectInteractors.MultiElementSelectInteractor import MultiElementSelectInteractor, MultiElementSelectInteractorResult

from XMLReader.XmlDataTreeReader import XmlDataTreeReader
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil

from DocumentManager import DocumentManager
#from BuildingElementInputService import BuildingElementInputService
from typing import List, TYPE_CHECKING, cast
from AnyValueByType import AnyValueByType
from FileNameService import FileNameService


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
from .EN.PY.EN_Conjunt_8_clase_PPEN_solids import EN_Conjunt_8
#from .IS.PY.IS_Conjunt_8_clase_PPIS_Tubes_Solids import IS_Conjunt_8
#from .IS.PY.IS_Conjunt_8_clase_PPIS_Tubes_Solids_from2023 import IS_Conjunt_8
from .IS.PY.IS_Conjunt_8_clase_PPIS_solids import IS_Conjunt_8

from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
from BuildingElementListService import BuildingElementListService
from PythonPartTransaction import PythonPartTransaction, ConnectToPythonPart, ConnectToElements
from StringTableService import StringTableService, BuildingElementMaterialStringTable
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementXML import BuildingElementXML
from BuildingElementStringTable import BuildingElementStringTable
from ParameterProperty import ParameterProperty

from Utils.PythonPart.ModifyPythonPartUtil import ModifyPythonPartUtil
from Utils.PythonPart.ModifyPythonPartParameterUtil import ModifyPythonPartParameterUtil


from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from PythonPartUtil import PythonPartUtil
from TypeCollections.ModelEleList import ModelEleList
from TypeCollections.ModificationElementList import ModificationElementList
from TypeCollections.PolyhedronTypesList import PolyhedronTypesList


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

LlargadaMaximaTD = 5750

LlargadaMaximaEN = 1200
LlargadaMinimaEN = 400
alcadaMaximaEN = 3000

LlargadaMaximaIS = 5650
alcadaMaximaIS = 2150



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
    #del version

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
    #build_ele.zUnique.value =  random.random() * 3600

    BaseScriptObj = Conjunt_8_Parent(build_ele, script_object_data)

    return BaseScriptObj


def get_file_name_with_num(fileName: str, n):
    extension = ''
    lastDig = ''
    while fileName != '' and (lastDig != '.' and lastDig != '\\'):
        lastDig = fileName[len(fileName)-1]
        extension = lastDig + extension
        fileName = fileName[0:len(fileName)-1]
    return fileName + str(n) + extension

def get_file_name(fileName: str):
    extension = ''
    lastDig = ''
    while lastDig != '\\' and len(fileName) > 0:
        lastDig = fileName[len(fileName)-1]
        extension = lastDig + extension
        fileName = fileName[0:len(fileName)-1]

    return  extension


def delete_anterior(build_ele: BuildingElement,
                     doc      : AllplanElementAdapter.DocumentAdapter,
                     listTubs = []):
    """ print the attributes

    Args:
        build_ele: building element with the parameter properties
        doc:       document of the Allplan drawing files
    """

    attr_manager = AllplanBaseElements.AttributeDataManager

    read_state = AllplanBaseElements.eAttibuteReadState.values[0]


    listNames = []
    for name in listTubs:
        listNames.append(get_file_name(name) )


    elemtsToDelete =  AllplanElementAdapter.BaseElementAdapterList()

    listDocumnets = AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
    for docValue in range(0,len(listDocumnets)):
        #docDrawingFile = AllplanBaseElements.DrawingFileService()
        #docAdapter = AllplanElementAdapter.DocumentAdapter()
        #doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[docValue][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

        #doc = DocumentManager.get_instance().document
        #doc = AllplanElementAdapter.DocumentNameService.GetDocumentNameByFileIndex(listDocumnets[docValue][1], True, True, "TEST")
        docDrawingFile = AllplanBaseElements.DrawingFileService()
        docAdapter = AllplanElementAdapter.DocumentAdapter()
        doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[docValue][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)


        doc = DocumentManager.get_instance().document
        for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
            n = 0
            trobat = False
            while n < len(listTubs) and not trobat :
                if str(element.GetElementUUID()) == listTubs[n]:
                    #AllplanBaseElements.DeleteElements(doc= doc, elements = [element] )
                    #elem = element.FromGUID(element.GetModelElementUUID(), doc)
                    elemtsToDelete.append(element)
                    trobat = True
                n += 1

        AllplanBaseElements.DeleteElements(doc= doc, elements= elemtsToDelete)

        #AllplanBaseElements.DeleteElements(doc= doc, elements= AllplanBaseElements.ElementsSelectService.SelectAllElements(doc))





class Conjunt_8_Parent(BaseScriptObject):
    """
    Clase principal para la gestión y creación de conjuntos estructurales personalizados en Allplan.

    Esta clase maneja la lógica de selección, creación, modificación y vista previa de elementos estructurales
    compuestos por diferentes subtipos (TD, EN, IS), permitiendo la interacción con el usuario y la integración
    con el sistema de PythonParts de Allplan.

    Args:
        build_ele (BuildingElement): Elemento de construcción principal con las propiedades del conjunto.
        script_object_data (BaseScriptObjectData): Datos auxiliares y utilidades para el script.

    Metodos principales:
        - start_input: Inicia la interacción de selección de elementos.
        - start_next_input: Gestiona la siguiente entrada del usuario.
        - execute: Ejecuta la creación del conjunto estructural.
        - modify_element_property: Modifica propiedades de los elementos.
        - create_element: Crea los elementos en el modelo.
        - draw_preview: Dibuja la vista previa del conjunto.
        - values_from_solid3D: Extrae dimensiones de elementos 3D seleccionados.
        - get_cuboid: Genera un cubo de ejemplo para la vista previa.
    """

    def __init__(self,
                 build_ele         : BuildingElement,
                 script_object_data: BaseScriptObjectData):
        """ Initialization

        Args:
            build_ele:          building element with the parameter properties
            script_object_data: script object data
        """

        #if build_ele.FlagEntrada.value == 1:
        super().__init__(script_object_data)

        try:
            for barra in range(0, build_ele.IntegerTDSelector.value):
                if barra >= len(build_ele.valueListBarresComboBox.value):
                    build_ele.valueListBarresComboBox.value.append("Tub " + str(barra))
                else:
                    build_ele.valueListBarresComboBox.value[barra] = "Tub " + str(barra)
        except Exception as e:
            print("No existeix la llista valueListBarresComboBox al PYP")

        self.build_ele = build_ele
        self.projectName = "None"

        #
        #self.sel_result = SingleElementSelectResult()
        projectAtt = AllplanBaseElements.ProjectAttributeService.GetAttributesFromCurrentProject()
        for elem in projectAtt:
            if str(elem).startswith("(405"):
                nombre = re.findall(r"'(.*?)'", str(elem) )
                self.projectName = nombre[0] if nombre else "None"




        self.coord_input        = script_object_data.coord_input#AllplanGeo.Point3D()#coord_input
        #self.pyp_path           = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura" + "\\Parent_Script_Selection.py"#pyp_path
        self.pyp_path           = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025" + "\\Parent_Script_Selection.py"
        pyp_path = self.pyp_path
        #self.str_table_service  = StringTableService(pyp_path) # BuildingElementStringTable#str_table_service
        self.first_point_input  = True
        self.first_point        = AllplanGeo.Point3D()
        self.model_ele_list     = None
        self.build_ele_service  = BuildingElementService()
        #self.build_ele_composite= BuildingElementComposite#build_ele_composite
        self.control_props_list = script_object_data.control_props_util#build_ele_ctrl_props_list
        self.build_ele_script   = Any

        self.doc = self.coord_input.GetInputViewDocument()

        #self.conjuntSelected = build_ele_list[0].SelectorPPPare.value
        self.conjuntSelected = build_ele.SelectorPPPare.value


        self.build_ele_Orginal = build_ele

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

        self.recalcularIS = False
        self.nrecalcularIS = 0


        self.valorAnt = build_ele.SelectorPPPFill.value


        self.palette = BuildingElementPaletteService(
            build_ele_list            = self.build_ele_list,
            build_ele_composite       = BuildingElementComposite(),
            build_ele_script          = self.build_ele_script,
            build_ele_ctrl_props_list = [],
            picture_path              = "",
            script_object             = None)

        self.palettelist : list[BuildingElementPaletteService] = []



        #selection elements
        self.element_list   = []
        self.element_list3D = []
        self.posChilds = []

        self.element_listTD = []
        self.atr_listTD = []
        self.paredTD        = []
        self.element_listEN = []
        self.atr_listEN = []
        self.paredEN        = []
        self.element_listIS = []
        self.atr_listIS = []
        self.paredIS        = []

        #self.list_of_build_ele : List[BuildingElement] = []
        self.list_of_build_ele  = []
        self.list_of_prop_list  = []
        self.list_of_filenames  = []

        self.mostrarInici = True

        self.llistaElemPerFill = []
        #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura"
        pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025"
        pyp_path += "\\Parent_Script_Selection.py"
        self.selection_result = MultiElementSelectInteractorResult()

        if build_ele.FlagEntrada.value != 1:
            elementsEliminats = False
            #AllplanBaseElements.DeleteElements(doc= self.doc, elements= )

            #self.delete_anterior(self.build_ele, self.doc, build_ele.listUUIDElements.value )
            self.selection_result = None
            #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura"
            pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025"
            for NameChild in build_ele.NameFilesChildren.value:



                #tupleBuildElem = BuildingElementXML.read_element_parameter(pyp_path=NameChild)


                #parametros = self.load_parameters_from_json(build_ele.NameFilesChildren.value)

                #build_ele_list_TD = BuildingElement()
                result, self.build_ele_script, build_ele_list_TD, self.control_props_list,    \
                self.build_ele_composite, part_name, self.file_name = \
                self.build_ele_service.read_data_from_pyp(file_name=str(NameChild),  str_table=BuildingElementStringTable("", False, ""), is_library_preview=False,
                                                            material_str_table=BuildingElementMaterialStringTable("", False, ""), sub_file_name=str(NameChild))#"\\TD_Conjunt_8_child.pyp")


                #if not elementsEliminats:
                #    self.delete_anterior(self.build_ele, self.doc, build_ele_list_TD[0].listUUIDElements.value )
                #    elementsEliminats = True
                self.delete_anterior(self.build_ele, self.doc, build_ele_list_TD[0].listUUIDElements.value )


                self.list_of_build_ele.append(build_ele_list_TD[0])
                self.list_of_prop_list.append(self.control_props_list[0])
                self.llistaElemPerFill.append([])

                self.list_of_filenames.append(NameChild)

                self.input_pnt = build_ele.inputPoint.value
                self.point_input_result.input_point = build_ele.inputPoint.value
                self.placement_mat.SetTranslation(AllplanGeo.Vector3D(self.input_pnt))

                palette = BuildingElementPaletteService(
                                build_ele_list            = build_ele_list_TD,
                                build_ele_composite       = self.build_ele_composite,
                                build_ele_script          = self.build_ele_script,
                                build_ele_ctrl_props_list = self.control_props_list,
                                picture_path              = "",
                                script_object             = None)

                self.palettelist.append(palette)


        else:
            self.selection_result = MultiElementSelectInteractorResult()


        #----------------- read the data and show the palette

        print("TEST Conjunt_9_parent")

        self.INPUT_MODE = 0 #self.selection_result #0


    def start_input(self):
        """ start the input
        """

        print("start_input START")

        if self.build_ele.FlagEntrada.value == 1:
            self.conjuntSelected = self.build_ele.SelectorPPPare.value

            self.doc = self.coord_input.GetInputViewDocument()

            allowed_types = [AllplanElementAdapter.Beam_TypeUUID,
                            AllplanElementAdapter.Column_TypeUUID]

            selection_filter = allowed_types

            self.script_object_interactor = MultiElementSelectInteractor(
                self.selection_result, # type: ignore
                None, #selection_filter,
                prompt_msg = "Selecciona els elements"
            )
        else:
            print("self.input_pnt: " + str(self.input_pnt))
            self.script_object_interactor = None


    def start_next_input(self):
        """ start the next input
        """
        print("start_next_input ")

        if self.build_ele.FlagEntrada.value == 1:

            if not bool(self.element_list):
                self.element_list = [
                    element
                    for element in self.selection_result.sel_elements #GetSelectedElements(self.doc) # type: ignore
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
                                self.atr_listTD.append(attribues[atribPersKey])
                            else:
                                self.paredTD.append(elem)
                        elif attribues[atribPersKey] == "EN" or attribues[atribPersKey] == "PortaEN" or attribues[atribPersKey] == "PortaCorredissa":
                            self.build_ele.SelectorPPPare.value = 3
                            self.conjuntSelected = 3
                            if attribues[atribPersKey] == "EN":
                                self.paredEN.append(elem)
                            else:
                                self.element_listEN.append(elem)
                                self.atr_listEN.append(attribues[atribPersKey])
                        elif attribues[atribPersKey] == "IS" or attribues[atribPersKey] == "Maquina":
                            self.build_ele.SelectorPPPare.value = 4
                            self.conjuntSelected = 4
                            if attribues[atribPersKey] == "IS":
                                self.paredIS.append(elem)
                            else:
                                self.element_listIS.append(elem)
                                self.atr_listIS.append(attribues[atribPersKey])
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
                #self.build_ele.ObjPared.value = self.paredTD
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
            self.build_ele_list[0].inputPoint.value = self.point_input_result.input_point
            if self.point_input_result.input_point != AllplanGeo.Point3D(0,0,0):
                #print(self.input_pnt)
                if self.build_ele.SelectorPPPare.value == 4:
                    if len(self.paredIS) != 0:
                        self.elemCube = self.crear_complemento(self.paredIS[0])

                self.script_object_interactor = None


    def get_atributes_from_solid(self, elem: AllplanElementAdapter.BaseElementAdapter):

        listAtrib = {}

        for attribute in elem.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAll):
            #msg += "\t" + str(attribute[0]) + " " + str(AllplanBaseElements.AttributeService.GetAttributeName(self.doc, attribute[0])) + "=" + str(attribute[1]) + "\n"
            #print( "\t" + str(attribute[0]) + " " + str(AllplanBaseElements.AttributeService.GetAttributeName(self.doc, attribute[0])) + "=" + str(attribute[1]) + "\n")
            #listAtrib[numIDAtt] = valueAtt
            listAtrib[str(attribute[0])] = str(attribute[1])
        return listAtrib

    def copiar_build_ele(self,  build_ele):
        build_ele_new = BuildingElement()
        for page_data in build_ele.get_pages():
            build_ele_new.add_page( page_data.name, page_data.text, page_data.visible_condition, page_data.enable_condition)
        #build_ele_new = build_ele.deep_copy()
        #
        build_ele_new.script_name                      = build_ele.script_name
        build_ele_new.pyp_file_name                    = build_ele.pyp_file_name
        build_ele_new.pyp_file_path                    = build_ele.pyp_file_path
        build_ele_new.title                            = build_ele.title
        build_ele_new.geometry_expand                  = build_ele.geometry_expand
        build_ele_new.read_last_input                  = build_ele.read_last_input
        build_ele_new.is_interactor                    = build_ele.is_interactor
        build_ele_new.element_id                       = build_ele.element_id
        build_ele_new.data_column_width                = build_ele.data_column_width
        build_ele_new.script_uuid                      = build_ele.script_uuid
        build_ele_new.version                          = build_ele.version
        build_ele_new.node_index                       = build_ele.node_index
        build_ele_new.vs_placement_point_input         = build_ele.vs_placement_point_input
        build_ele_new.vs_multi_placement               = build_ele.vs_multi_placement
        #
        build_ele_new.set_reinforcement_definition_list(build_ele.get_reinforcement_definition_list())
        build_ele_new.add_string_tables(*build_ele.get_string_tables())
        build_ele_new.add_material_string_table(build_ele.get_material_string_table())
        build_ele_new.set_insert_matrix(build_ele.get_insert_matrix())

        for prop in build_ele.get_properties():
            #print("prop: " + str(prop))
            build_ele_new.add_property(prop.name, prop.deep_copy())

        return build_ele_new

    def crear_complemento(self, solido_base):
        # Paso 1: Obtener el bounding box del sólido original

        llargada, amplada, alcada = self.values_from_solid3D([solido_base])
        posPared = self.calcular_posiciones([solido_base])

        vec1 = AllplanGeo.Vector3D(llargada,0,0)
        vec2 = AllplanGeo.Vector3D(0,amplada,0)
        vec3 = AllplanGeo.Vector3D(0,0,alcada)
        placemrnt = AllplanGeo.AxisPlacement3D(posPared[0]["InfEsq"])

        placement_matrix = AllplanGeo.AxisPlacement3D()
        placement_matrix.SetOrigin(
            AllplanGeo.Point3D(
                posPared[0]["InfEsq"].X, #self.point_input_result.input_point
                posPared[0]["InfEsq"].Y ,
                posPared[0]["Baix"].Z,
            )
        )


        cubo_completo = AllplanGeo.Polyhedron3D.CreateCuboid(placement_matrix, llargada, amplada , alcada)


        geoSoliDBase = solido_base.GetGeometry()
        #print(geoSoliDBase)

        common_props   = AllplanBaseElements.CommonProperties()
        model_ele_list = ModelEleList(common_props)

        volumen_restante = AllplanGeo.MakeBoolean(cubo_completo, geoSoliDBase)
        if volumen_restante[0] == AllplanGeo.eGeometryErrorCode.eError:
            #volumen_restante = self.get_cuboid()
            return model_ele_list
        else:
            volumen_restante = volumen_restante[3]

        '''
        placement_matrix = AllplanGeo.AxisPlacement3D()
        placement_matrix.SetOrigin(
            AllplanGeo.Point3D(
                posPared[0]["InfEsq"].X - self.point_input_result.input_point.X,
                posPared[0]["InfEsq"].Y - self.point_input_result.input_point.Y,
                posPared[0]["Baix"].Z   - self.point_input_result.input_point.Z
            )
        )

        llargadaCub, ampladaCub, alcadaCub = self.values_from_solid3D([volumen_restante])
        #cubos = AllplanGeo.Polyhedron3D.CreateCuboid(placement_matrix, llargadaCub, ampladaCub, alcadaCub)
        #volumen_restante.SetRefPoint(AllplanGeo.Point3D(posPared[0]["InfEsq"].X - self.point_input_result.input_point.X,
        #                                                posPared[0]["InfEsq"].Y - self.point_input_result.input_point.Y,
        #                                                posPared[0]["Baix"].Z   - self.point_input_result.input_point.Z )
        #                                     )

        #cubos.SetRefPoint(AllplanGeo.Point3D(0,0,0))
        #cubos = AllplanGeo.CreatePolyhedron()


        cuboBuilder = AllplanGeo.Polyhedron3DBuilder(cubos)
        vertexs = []
        for npoint in range(0, cubos.GetVerticesCount()):
            point = cubos.GetVertex(npoint)
            print(cubos.GetVertex(npoint))
            if AllplanGeo.eGeometryErrorCode.eOK:
                cuboBuilder.SetVertex(npoint, AllplanGeo.Point3D(cubos.GetVertex(npoint)[1].X + posPared[0]["InfEsq"].X - self.point_input_result.input_point.X,
                                                cubos.GetVertex(npoint)[1].Y + posPared[0]["InfEsq"].Y - self.point_input_result.input_point.Y,
                                                cubos.GetVertex(npoint)[1].Z + posPared[0]["Baix"].Z   - self.point_input_result.input_point.Z))

                #vertexs.append(AllplanGeo.Point3D(cubos.GetVertex(npoint)[1].X + posPared[0]["InfEsq"].X - self.point_input_result.input_point.X,
                #                    cubos.GetVertex(npoint)[1].Y + posPared[0]["InfEsq"].Y - self.point_input_result.input_point.Y,
                #                    cubos.GetVertex(npoint)[1].Z + posPared[0]["Baix"].Z   - self.point_input_result.input_point.Z))
            print(point)

        '''



        cubos = volumen_restante
        '''
        llargadaRes, ampladaRes, alcadaRes = self.values_from_solid3D([cubos])
        posParedRes = self.calcular_posiciones([cubos])
        placement_matrixRes = AllplanGeo.AxisPlacement3D()
        placement_matrixRes.SetOrigin(
            AllplanGeo.Point3D(
                posParedRes[0]["InfEsq"].X, #self.point_input_result.input_point
                posParedRes[0]["InfEsq"].Y ,
                posParedRes[0]["Baix"].Z,
            )
        )
        cubo_completoRes = AllplanGeo.Polyhedron3D.CreateCuboid(placement_matrixRes, llargadaRes, ampladaRes , alcadaRes)


        #minCubosMasGrandes = self.encajar_cubos_maximos2(cubos, cubo_completoRes, llargadaRes, 50)
        #minCubosMasGrandes = self.greedy_partition_to_rectangles(cubos, 50.0)
        #minCubosMasGrandes = self.crear_sólidos_3d_desde_poligono(cubos, 750, 750, 20)
        #minCubosMasGrandes = self.create_quadrats_porfa(volumen_restante, llargadaRes, ampladaRes)
        minCubosMasGrandes = self.CreateElement(volumen_restante)
        #minCubosMasGrandes = [volumen_restante]
        for cubos in minCubosMasGrandes:
            self.element_listIS.append(cubos)#cuboBuilder.Complete())
            self.atr_listIS.append([])
            model_ele_list.append_geometry_3d(cubos)

        #model_ele_list.append_geometry_3d(cubo_completo)
        #model_ele_list.append_geometry_3d(geoSoliDBase)
        # Paso 4: Añadir el volumen restante al modelo
        #listofelements.append(BuildElement(volumen_restante))

        return model_ele_list
        '''

        volumen = AllplanGeo.CalcMass(volumen_restante)
        if volumen[1] > 1:
            msg = "la pared ha de tenir forma rectangular"
            PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)

        return self.get_cuboid()


    def proyectar_a_2d_2(self, puntos_3d, plano: AllplanGeo.AxisPlacement3D):

        return[(p.X,  p.Y) for p in puntos_3d[0] ]
        #return[(plano.CalcLocalPoint(p).X,  plano.CalcLocalPoint(p).Y) for p in puntos_3d[0] ]
        #return [AllplanGeo.AxisPlacement3D.CalcLocalPoint(plano, p) for p in puntos_3d]
        #return [(plano.ToLocal(p).X, plano.ToLocal(p).Y) for p in puntos_3d]

    def obtener_rectangulos_optim(self, puntos_2d, llargadaRes, ampladaRes):
        # Método sencillo: bounding box general y subdividirlo (mejorable con algoritmo tipo skyline)

        min_x = min(p[0] for p in puntos_2d)
        max_x = max(p[0] for p in puntos_2d)
        min_y = min(p[1] for p in puntos_2d)
        max_y = max(p[1] for p in puntos_2d)

        ancho_total = max_x - min_x
        alto_total = max_y - min_y

        mejor_paso = None
        mejor_rects = []
        menor_cantidad = float('inf')

        '''
        for paso in range(2000, 19, -50):  # Intenta con pasos desde 5000 hasta 20
            rects = []
            x = min_x
            while x < max_x:
                y = min_y
                while y < max_y:
                    cx = x + paso / 2
                    cy = y + paso / 2
                    if self.punto_en_poligono((cx, cy), puntos_2d):
                        rects.append((x, y, x + paso, y + paso))
                    y += paso
                x += paso

            if len(rects) < menor_cantidad and len(rects) > 0:
                menor_cantidad = len(rects)
                mejor_paso = paso
                mejor_rects = rects
        '''

        '''
        for paso in range(12000, 19, -50):  # Intenta con pasos desde 5000 hasta 20
            rects = []
            y = min_y
            while y < max_y:
                cy = y + paso / 2
                x = min_x
                while x < max_x:
                    cx = x + paso / 2
                    if self.punto_en_poligono((cx, cy), puntos_2d):
                        rects.append((x, y, x + paso, y + paso))
                    x += paso
                y += paso

            if len(rects) < menor_cantidad and len(rects) > 1:
                menor_cantidad = len(rects)
                mejor_paso = paso
                mejor_rects = rects

        return mejor_rects
        '''
        # Probar combinaciones de pasos en X y Y
        print(round(llargadaRes))
        for paso_x in range(1500, 19, -20):# round(llargadaRes), 19, -20):
            for paso_y in range(1500, 19, -20):# round(ampladaRes), 19, -20):
                rects = []
                x = min_x
                while x < max_x:
                    y = min_y
                    while y < max_y:
                        cx = x + paso_x / 2
                        cy = y + paso_y / 2
                        if self.punto_en_poligono((cx, cy), puntos_2d):
                            rects.append((x, y, x + paso_x, y + paso_y))
                        y += paso_y
                    x += paso_x

                if 0 < len(rects) < menor_cantidad:
                    menor_cantidad = len(rects)
                    mejor_rects = rects

        return mejor_rects

    def crear_breps_desde_rectangulos(self, rects, altura, plano):
        solidos = []
        for xmin, ymin, xmax, ymax in rects:
            puntos_locales = [
                AllplanGeo.Point3D(xmin, ymin, 0),      AllplanGeo.Point3D(xmax, ymin, 0),
                AllplanGeo.Point3D(xmax, ymax, 0),      AllplanGeo.Point3D(xmin, ymax, 0),
                AllplanGeo.Point3D(xmin, ymin, altura), AllplanGeo.Point3D(xmax, ymin, altura),
                AllplanGeo.Point3D(xmax, ymax, altura), AllplanGeo.Point3D(xmin, ymax, altura),
            ]
            #puntos_globales = [plano.CalcGlobalPoint(p) for p in puntos_locales]
            #caras_idx = [
            #    (0, 1, 2, 3), (4, 5, 6, 7),
            #    (0, 1, 5, 4), (1, 2, 6, 5),
            #    (2, 3, 7, 6), (3, 0, 4, 7)
            #]

            #brep = BRep3D()
            #for i1, i2, i3, i4 in caras_idx:
            #    pol = Polygon3D()
            #    pol += puntos_globales[i1]
            #    pol += puntos_globales[i2]
            #    pol += puntos_globales[i3]
            #    pol += puntos_globales[i4]
            #    brep += BrepFace(pol)
            #solidos.append(brep)
            brep = AllplanGeo.Polyhedron3D.CreateCuboid(AllplanGeo.Point3D(xmin, ymin, 0),AllplanGeo.Point3D(xmax, ymax, altura) )
            solidos.append(brep)
        return solidos

    def create_quadrats_porfa(self, poly_3d, llargadaRes, ampladaRes):
        model_ele_list = []

        # 1. Polígono 3D


        # 2. Plano local (XY)
        plano = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 1, 0))

        # 3. Proyección 2D
        poly_2d = self.proyectar_a_2d_2([poly_3d.GetVertices()], plano)

        # 4. Dividir en rectángulos grandes (aquí solo bounding box)
        rects = self.obtener_rectangulos_optim(poly_2d, llargadaRes, ampladaRes)

        # 5. Extruir
        altura = 20
        breps = self.crear_breps_desde_rectangulos(rects, altura, plano)

        for b in breps:
            model_ele_list.append(b)

        return model_ele_list
        #return (model_ele_list, View2D3D(), None)







    def CreateElement(self, base_points):
        # 1. Polígono 3D


        # 2. Plano local (XY)
        plano = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 1, 0))

        # 3. Proyección 2D
        poly_2d = self.proyectar_a_2d_2([base_points.GetVertices()], plano)

        building_element = []

        solids = self.divide_polygon_into_solids(poly_2d, cell_size=1000.0)

        for solid in solids:
            #points = [
            #    AllplanGeo.Point3D(p.X, p.Y, p.Z) for p in solid.base_points
            #]
            #cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(points[0], points[1], points[3], solid.height)
            building_element.append(solid)
        return building_element

    def divide_polygon_into_solids(self, polygon_3d, cell_size=100.0):
        polygon_xy = [(p[0], p[1]) for p in polygon_3d]
        grid, min_x, min_y, size = self.rasterize_polygon(polygon_xy, cell_size)
        rects = self.find_max_horizontal_rectangles(grid)
        coords = self.rectangles_to_coordinates(rects, min_x, min_y, size)
        solids = []
        for (x1, y1), (x2, y2) in coords:
            '''
            base = [
                AllplanGeo.Point3D(x1, y1, -20),
                AllplanGeo.Point3D(x2, y1, -20),
                AllplanGeo.Point3D(x2, y2, -20),
                AllplanGeo.Point3D(x1, y2, -20)
            ]
            '''
            solids.append(AllplanGeo.Polyhedron3D.CreateCuboid(AllplanGeo.Point3D(x1, y1, -20), AllplanGeo.Point3D(x2, y2, 20)))
        return solids

    def rasterize_polygon(self, polygon_xy, cell_size):
        min_x = min(p[0] for p in polygon_xy)
        max_x = max(p[0] for p in polygon_xy)
        min_y = min(p[1] for p in polygon_xy)
        max_y = max(p[1] for p in polygon_xy)
        cols = int((max_x - min_x) // cell_size) + 1
        rows = int((max_y - min_y) // cell_size) + 1
        grid = [[0 for _ in range(cols)] for _ in range(rows)]

        def point_in_polygon(x, y, poly):
            count = 0
            n = len(poly)
            for i in range(n):
                x1, y1 = poly[i]
                x2, y2 = poly[(i + 1) % n]
                if ((y1 > y) != (y2 > y)):
                    xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-10) + x1
                    if x < xinters:
                        count += 1
            return count % 2 == 1

        for r in range(rows):
            for c in range(cols):
                x = min_x + c * cell_size + cell_size / 2
                y = min_y + r * cell_size + cell_size / 2
                if point_in_polygon(x, y, polygon_xy):
                    grid[r][c] = 1
        return grid, min_x, min_y, cell_size

    def find_max_horizontal_rectangles(self, grid):
        rows = len(grid)
        cols = len(grid[0])
        used = [[False for _ in range(cols)] for _ in range(rows)]
        rectangles = []
        for r in range(rows):
            c = 0
            while c < cols:
                if grid[r][c] == 1 and not used[r][c]:
                    start_c = c
                    while c < cols and grid[r][c] == 1 and not used[r][c]:
                        c += 1
                    end_c = c - 1
                    height = 1
                    while True:
                        if r + height >= rows:
                            break
                        can_expand = all(grid[r + height][cc] == 1 and not used[r + height][cc] for cc in range(start_c, end_c + 1))
                        if not can_expand:
                            break
                        height += 1
                    for rr in range(r, r + height):
                        for cc in range(start_c, end_c + 1):
                            used[rr][cc] = True
                    rectangles.append((r, start_c, r + height - 1, end_c))
                else:
                    c += 1
        return rectangles

    def rectangles_to_coordinates(self, rectangles, min_x, min_y, cell_size):
        coords = []
        for r1, c1, r2, c2 in rectangles:
            x1 = min_x + c1 * cell_size
            y1 = min_y + r1 * cell_size
            x2 = min_x + (c2 + 1) * cell_size
            y2 = min_y + (r2 + 1) * cell_size
            coords.append(((x1, y1), (x2, y2)))
        return coords









    def dividir_poligono_en_rectangulos(self, polygon3d, paso_x, paso_y):
        rectangulos = []
        min_x = min(p.X for p in polygon3d.GetVertices())
        max_x = max(p.X for p in polygon3d.GetVertices())
        min_y = min(p.Y for p in polygon3d.GetVertices())
        max_y = max(p.Y for p in polygon3d.GetVertices())
        min_z = min(p.Z for p in polygon3d.GetVertices())
        max_z = max(p.Z for p in polygon3d.GetVertices())

        x = min_x
        while x + paso_x <= max_x + 1e-6:
            y = min_y
            while y + paso_y <= max_y + 1e-6:
                centro = AllplanGeo.Point2D(x + paso_x / 2.0, y + paso_y / 2.0)
                if self.punto_en_poligono(centro, polygon3d):
                    rect = [
                        #AllplanGeo.Point2D(x, y),
                        #AllplanGeo.Point2D(x + paso_x, y),
                        #AllplanGeo.Point2D(x + paso_x, y + paso_y),
                        #AllplanGeo.Point2D(x, y + paso_y),
                        AllplanGeo.Point3D(x, y, min_z),
                        AllplanGeo.Point3D(x + paso_x, y, min_z),
                        AllplanGeo.Point3D(x + paso_x, y + paso_y, min_z),
                        AllplanGeo.Point3D(x, y + paso_y, min_z),
                        AllplanGeo.Point3D(x, y, max_z),
                        AllplanGeo.Point3D(x + paso_x, y, max_z),
                        AllplanGeo.Point3D(x + paso_x, y + paso_y, max_z),
                        AllplanGeo.Point3D(x, y + paso_y, max_z),
                    ]
                    rectangulos.append(rect)
                y += paso_y
            x += paso_x

        return rectangulos


    def crear_sólidos_3d_desde_poligono(self, polygon3d, paso_x, paso_y, altura_z):
        '''

        model_elements = []
        rectangulos = self.dividir_poligono_en_rectangulos(polygon3d, paso_x, paso_y)

        for puntos_rect in rectangulos:

            poly = AllplanGeo.Polygon2D(puntos_rect)
            startPoint = AllplanGeo.Point3D(puntos_rect[0])
            endPoint   = AllplanGeo.Point3D(puntos_rect[1])
            succes, polygon = AllplanGeo.CreatePolygon3D(poly, AllplanGeo.Plane3D(startPoint, AllplanGeo.Vector3D(startPoint=startPoint,endPoint=endPoint) ) )
            succes, polyhedron = AllplanGeo.CreatePolyhedron(polygon)# (poly, AllplanGeo.Plane3D(startPoint, AllplanGeo.Vector3D(startPoint=startPoint,endPoint=endPoint) ) )
            model_elements.append(polyhedron)
            #if succes == AllplanGeo.eGeometryErrorCode.eOK:
            #    model_elements.append(polyhedron)


        return model_elements
        '''
        model_elements = []
        rectangulos = self.dividir_poligono_en_rectangulos(polygon3d, paso_x, paso_y)

        for puntos_rect in rectangulos:
            # Crear polígono 2D y Path2D
            poly3d = AllplanGeo.Polygon3D(puntos_rect)
            path = AllplanGeo.Path2D()
            area = AllplanGeo.PolygonalArea3D()
            area += poly3d

            # Crear extrusión
            extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
            extruded_solid.SetDirection(AllplanGeo.Vector3D(0, 0, 1))
            extruded_solid.SetRefPoint(poly3d.GetRefPoint() )
            #extruded_solid.SetExtrudedArea(area)

            error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)
            if error_code == AllplanGeo.eGeometryErrorCode.eOK:
                # Crear ModelElement3D para añadir a Allplan
                model_elements.append(polyhedron)

        return model_elements

    def definir_plano_local(self, puntos3d):
        origen = puntos3d[0]
        vec_x = puntos3d[1] - origen
        vec_temp = puntos3d[2] - origen
        vec_z = AllplanGeo.Vector3D.CrossProduct(vec_x, vec_temp)
        vec_y = AllplanGeo.Vector3D.CrossProduct(vec_z, vec_x)

        vec_x.Normalize()
        vec_y.Normalize()
        vec_z.Normalize()

        return AllplanGeo.AxisPlacement3D(origen, vec_x, vec_y)


    def punto_en_poligono(self, punto, poligono):
        x, y = punto[0], punto[1]
        puntos = poligono #.GetVertices()
        dentro = False
        n = len(puntos)
        j = n - 1

        for i in range(n):
            xi, yi = puntos[i][0], puntos[i][1]
            xj, yj = puntos[j][0], puntos[j][1]
            intersecta = ((yi > y) != (yj > y)) and \
                        (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi)
            if intersecta:
                dentro = not dentro
            j = i

        return dentro

    def es_paralelepipedo(self, solido, tolerancia= 1e-3):
        #bbox = solido.GetBoundingBox()
        #dx, dy, dz = self.values_from_solid3D([solido])
        #bbox = self.calcular_posiciones([solido])

        try:
            geo = solido.GetGeometry()
        except Exception as e:
            try:
                geo = solido
            except Exception as e:
                print("--")
            print("-")


        llistaVertex = geo.GetVertices()

        inici = True
        for vert in llistaVertex:
            if inici:
                puntInferiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                puntInferiorDre = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                puntSuperiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                puntSuperiorDre = AllplanGeo.Point3D(vert.X, vert.Y, vert.Z)
                puntAlt = AllplanGeo.Point3D(0, 0, vert.Z)
                puntBaix = AllplanGeo.Point3D(0, 0, vert.Z)

                inici = False
            else:

                if vert.X <= puntInferiorEsq.X and vert.Y <= puntInferiorEsq.Y:
                    puntInferiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, 0)
                if vert.X >= puntInferiorDre.X and vert.Y <= puntInferiorDre.Y:
                    puntInferiorDre = AllplanGeo.Point3D(vert.X, vert.Y, 0)
                if vert.X <= puntSuperiorEsq.X and vert.Y >= puntSuperiorEsq.Y:
                    puntSuperiorEsq = AllplanGeo.Point3D(vert.X, vert.Y, 0)
                if vert.X >= puntSuperiorDre.X and vert.Y >= puntSuperiorDre.Y:
                    puntSuperiorDre = AllplanGeo.Point3D(vert.X, vert.Y, 0)

                if vert.Z >= puntAlt.Z:
                    puntAlt = AllplanGeo.Point3D(0, 0, vert.Z)
                if vert.Z <= puntBaix.Z:
                    puntBaix = AllplanGeo.Point3D(0, 0, vert.Z)




        dx = puntInferiorDre.X - puntInferiorEsq.X
        dy = puntSuperiorEsq.Y - puntInferiorEsq.Y
        dz = puntAlt.Z - puntBaix.Z


        # Comprobamos que no sea plano
        if dx < tolerancia or dy < tolerancia or dz < tolerancia:
            return False


        bbox = self.calcular_posiciones([solido])

        # Comprobamos que el sólido no tenga formas fuera del bounding box
        # Es decir, que intersección entre bbox y solido == solido
        cubo_bbox = AllplanGeo.Polyhedron3D.CreateCuboid(bbox[0]["InfEsq"], bbox[0]["SupDre"])
        resto = AllplanGeo.MakeBoolean(solido, cubo_bbox)
        resto = resto[1]

        # Si el resultado de restar el bbox al sólido es nulo, es un paralelepípedo
        masa = AllplanGeo.CalcMass(resto)
        #masa= round(masa[1]/1000000000, 6 )
        volume= round(masa[1], 6 )
        return not resto.IsValid() or volume < tolerancia


    def calcular_encaje(self, largo_total, ancho_total, x_largo, y_ancho):
        """
        Calcula cuántas piezas de (x_largo, y_ancho) caben en el área (largo_total x ancho_total),
        y devuelve la posición inferior izquierda de cada pieza.
        """
        piezas_x = largo_total // x_largo
        piezas_y = ancho_total // y_ancho
        total_piezas = int(piezas_x * piezas_y)

        posiciones = []
        for i in range(int(piezas_x)):
            for j in range(int(piezas_y)):
                x = i * x_largo
                y = j * y_ancho
                posiciones.append((x, y))

        return total_piezas, posiciones

    def proyectar_a_2d(self, puntos3d, plano_local):
        puntos2d = []
        for pt in puntos3d:
            local = plano_local.GlobalToLocal(pt)
            puntos2d.append(AllplanGeo.Point2D(local.X, local.Y))
        return puntos2d







    def calcular_posiciones(self, element_list):
        llistaPosicions = []
        pos = 0
        iniciConjunt = True

        for element in element_list:

            puntEsq = 0
            puntDre = 0
            puntInf = 0
            puntSup = 0
            puntAlt = 0
            puntBaix = 0

            #print(element.GetGeometry())
            #print(element.GetModelGeometry())
            try:
                geo = element.GetGeometry()
            except Exception as e:
                try:
                    geo = element
                except Exception as e:
                    print("--")
                    continue
                print("-")


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
            newPos = {"InfEsq" : puntInferiorEsq,
                      "InfDre" :puntInferiorDre,
                      "SupEsq" :puntSuperiorEsq,
                      "SupDre" :puntSuperiorDre,
                      "Alt"    :puntAlt,
                      "Baix"   :puntBaix}
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
        return llistaPosicions


    def calcular_encaje_con_recorte(self, largo_total, ancho_total, x_largo, y_ancho, objetosInteriores, posPared):
        """
        Llena un área con piezas alineadas, permitiendo recortes exactos al borde.
        Devuelve:
        - Total de piezas
        - Lista de dicts con posición y tamaño de cada pieza
        - Área total cubierta por las piezas
        """
        llistaPosObjInter = self.calcular_posiciones(objetosInteriores)

        print("llistaPosObjInter: ")
        print(llistaPosObjInter)
        print("posPared: ")
        print(posPared)

        posiciones = []
        area_total = 0.0
        y = 0
        while y < ancho_total:
            altura_pieza = min(y_ancho, ancho_total - y)
            x = 0
            while x < largo_total:
                ancho_pieza = min(x_largo, largo_total - x)

                ancho_balconera = 0
                ############
                for nPosEle in range(0, len(llistaPosObjInter)):
                    posAbsElemeEsq = llistaPosObjInter[nPosEle]["InfEsq"].X
                    posAbsElemeDre = llistaPosObjInter[nPosEle]["InfDre"].X
                    posAbsElemeSup = llistaPosObjInter[nPosEle]["SupEsq"].Y
                    posAbsElemeInf = llistaPosObjInter[nPosEle]["SupDre"].Y

                    posAbsParedEsq = posPared[0]["InfEsq"].X
                    posAbsParedDre = posPared[0]["InfDre"].X
                    posAbsParedSup = posPared[0]["SupEsq"].Y
                    posAbsParedInf = posPared[0]["SupDre"].Y


                    if (posAbsElemeEsq > posAbsParedEsq + x and \
                        posAbsElemeEsq < posAbsParedEsq + x + ancho_pieza and \
                        posAbsElemeDre > posAbsParedEsq + x + ancho_pieza ) : #and \
                        retall = posAbsParedEsq - posAbsParedEsq + x - posAbsElemeEsq - 50 #min(x_largo, largo_total - x)
                        #ancho_pieza = abs((posAbsParedEsq + x) - (posAbsElemeEsq))
                        ancho_piezaAux = math.dist([posAbsParedEsq + x,0,0]  , [posAbsElemeEsq,0,0])
                        if ancho_piezaAux < ancho_pieza:
                            ancho_pieza = ancho_piezaAux
                            print("ancho_pieza: " + str(ancho_pieza))
                            ancho_balconera = posAbsElemeDre - posAbsElemeEsq
                        #print("retall: " + str(retall))
                        #ancho_pieza -= retall



                #############
                posiciones.append({
                    "pos": (x, y),
                    "size": (ancho_pieza, altura_pieza)
                })
                area_total += ancho_pieza * altura_pieza
                x += ancho_pieza + ancho_balconera#x_largo


            y += y_ancho

        total_piezas = len(posiciones)
        return total_piezas, posiciones, area_total

    def calcular_encaje_con_recorteIS(self, largo_total, ancho_total, x_largo, y_ancho, objetosInteriores, posPared):
        """
        Llena un área con piezas alineadas, permitiendo recortes exactos al borde.
        Devuelve:
        - Total de piezas
        - Lista de dicts con posición y tamaño de cada pieza
        - Área total cubierta por las piezas
        """
        llistaPosObjInter = self.calcular_posiciones(objetosInteriores)

        print("llistaPosObjInter: ")
        print(llistaPosObjInter)
        print("posPared: ")
        print(posPared)

        posiciones = []
        area_total = 0.0
        y = 0
        while y < ancho_total:
            altura_pieza = min(y_ancho, ancho_total - y)
            x = 0
            while x < largo_total:
                ancho_pieza = min(x_largo, largo_total - x)
                posiciones.append({
                    "pos": (x, y),
                    "size": (ancho_pieza, altura_pieza)
                })
                area_total += ancho_pieza * altura_pieza
                x += ancho_pieza #x_largo
            y += y_ancho

        total_piezas = len(posiciones)
        return total_piezas, posiciones, area_total




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

        #BuildingElement(self.build_ele)
        #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura"
        pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025"

        if self.conjuntSelected != 1:

            pared_model_elem_list = []
            pared_handle_list = []
            preview_symbols = PreviewSymbols()

            doc = DocumentManager.get_instance().document#self.__doc__


            llargadaPerAfegir = 0
            llargadaAfegida = 0
            alcadaAfegida = 0
            ultimAfegit = False
            ultimAfegitVert = False
            nBuild_ele = 0

            preview_symbols = PreviewSymbols()

            llargada= 0
            amplada = 0
            alcada = 0
            pos = []

            if self.conjuntSelected == 2:
                llargada, amplada, alcada = self.values_from_solid3D(self.paredTD)
                posPared = self.calcular_posiciones(self.paredTD)
                totalPeces, pos, areaTotal = self.calcular_encaje_con_recorte(llargada, amplada,LlargadaMaximaTD, amplada, self.element_listTD, posPared)
            elif self.conjuntSelected == 3:
                llargada, amplada, alcada = self.values_from_solid3D(self.paredEN)
                posPared = self.calcular_posiciones(self.paredEN)
                totalPeces, pos, areaTotal = self.calcular_encaje_con_recorte(llargada, amplada,LlargadaMaximaEN, amplada, self.element_listEN, posPared)
            elif self.conjuntSelected == 4:
                llargada, amplada, alcada = self.values_from_solid3D(self.paredIS)
                posPared = self.calcular_posiciones(self.paredIS)
                if self.build_ele.direccioISInv.value:
                    LlargadaMaximaIS = 2150
                    alcadaMaximaIS = 5650
                else:
                    LlargadaMaximaIS = 5650
                    alcadaMaximaIS = 2150
                if self.build_ele_list[0].FlagEntrada.value == 1:
                    totalPeces, pos, areaTotal = self.calcular_encaje_con_recorteIS(llargada, amplada,LlargadaMaximaIS+50, alcadaMaximaIS, self.element_listIS, posPared)
                #invers
                #self.build_ele_list[0].totalPeces.value, pos, areaTotal = self.calcular_encaje_con_recorteIS(amplada, llargada,LlargadaMaximaIS, alcadaMaximaIS, self.element_listIS, posPared)

            if self.build_ele_list[0].FlagEntrada.value == 1:
                self.build_ele_list[0].totalPeces.value = totalPeces

            while len(self.build_ele.listofPythonChilds.value) < self.build_ele_list[0].totalPeces.value:
                self.build_ele.listofPythonChilds.value.append(len(self.build_ele.listofPythonChilds.value))

            if self.build_ele_list[0].totalPeces.value > 0:
                for nPeca in range(0,self.build_ele_list[0].totalPeces.value):
                    if nPeca >= len(self.build_ele_list[0].listofPositionsChilds.value):
                        if len(pos) > nPeca:
                            #self.posChilds.append(AllplanGeo.Point3D(pos[nPeca]["pos"][0], pos[nPeca]["pos"][1], 0))
                            self.build_ele_list[0].listofPositionsChilds.value.append(AllplanGeo.Point3D(pos[nPeca]["pos"][0], pos[nPeca]["pos"][1], 0))
                        else:
                            while len(pos) <= nPeca:
                                pos.append({
                                    "pos": (0, 0, 0),
                                    "size": (LlargadaMaximaIS, alcadaMaximaIS, 0)
                                })
                            #self.posChilds.append(AllplanGeo.Point3D(pos[nPeca]["pos"][0], pos[nPeca]["pos"][1], 0))
                            self.build_ele_list[0].listofPositionsChilds.value.append(AllplanGeo.Point3D(pos[nPeca]["pos"][0], pos[nPeca]["pos"][1], 0))

                    if nPeca >= len(self.build_ele_list[0].listofMesuresChilds.value):
                        if len(pos) > nPeca:
                            self.build_ele_list[0].listofMesuresChilds.value.append(AllplanGeo.Point3D(pos[nPeca]["size"][0], pos[nPeca]["size"][1], 0))
                        else:
                            while len(pos) <= nPeca:
                                pos.append({
                                    "pos": (0, 0, 0),
                                    "size": (LlargadaMaximaIS, alcadaMaximaIS, 0)
                                })
                            self.build_ele_list[0].listofMesuresChilds.value.append(AllplanGeo.Point3D(pos[nPeca]["size"][0], pos[nPeca]["size"][1], 0))

            if self.build_ele_list[0].totalPeces.value < len(self.build_ele_list[0].listofPositionsChilds.value):
                self.build_ele_list[0].totalPeces.value = len(self.build_ele_list[0].listofPositionsChilds.value)

            nTotalPeca = 0

            #while not ultimAfegit and not ultimAfegitVert:
            for nPeca in range(0,self.build_ele_list[0].totalPeces.value):

                #TD_conjunt  =  TD_Conjunt_8(self.build_ele, DocumentManager.get_instance().document)
                desplacament = 0

                if self.conjuntSelected == 2:
                    #llargada, amplada, alcada = self.values_from_solid3D(self.paredTD)
                    #llargadaActual = llargada
                    posNovaMatrix = AllplanGeo.Matrix3D()

                    desplacament = self.build_ele_list[0].listofPositionsChilds.value[nPeca].X # pos[nPeca]["pos"][0]

                    posNovaMatrix.SetValue(12, desplacament)
                    '''
                    llargadaActual = llargada - llargadaAfegida

                    posNovaMatrix = AllplanGeo.Matrix3D()

                    desplacament = 0

                    posNovaMatrix.SetValue(12, 0)
                    if llargadaAfegida != 0:
                        posNovaMatrix.SetValue(12, llargadaAfegida)
                        desplacament = llargadaAfegida

                    if llargadaActual > LlargadaMaximaTD:
                        llargadaActual = LlargadaMaximaTD
                        llargadaAfegida += LlargadaMaximaTD
                    else:
                        llargadaAfegida += llargadaActual
                        ultimAfegit =True
                        ultimAfegitVert = True

                    '''
                    llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPeca].X #pos[nPeca]["size"][0]
                    alcadaActual   = alcada
                    if self.build_ele_list[0].FlagEntrada.value == 1:
                        while len(self.list_of_build_ele) <= nBuild_ele :
                            self.build_ele_list[0].listofPythonChilds.value.append(nBuild_ele)

                            result, self.build_ele_script, self.build_ele_list_TD, self.control_props_list,    \
                            self.build_ele_composite, part_name, self.file_name = \
                            self.build_ele_service.read_data_from_pyp(pyp_path + "\\TD\\PYP\\TD_Conjunt_8_child.pyp", BuildingElementStringTable("", False, ""), True,
                                                                        BuildingElementMaterialStringTable("", False, ""), pyp_path + "\\TD\\PYP\\TD_Conjunt_8_child.pyp")


                            #self.build_ele_list_TD[0].set_property("BarraLlargadaTD", llargadaActual)
                            #self.build_ele_list_TD[0].set_property("BarraLlargadaVert", alcada)
                            self.build_ele_list_TD[0].BarraLlargadaTD.value = llargadaActual
                            self.build_ele_list_TD[0].BarraLlargadaVert.value = alcada
                            self.build_ele_list_TD[0].inputPoint.value = self.input_pnt
                            self.build_ele_list_TD[0].listofPositionsChilds.value = self.build_ele_list[0].listofPositionsChilds.value
                            self.build_ele_list_TD[0].listofMesuresChilds.value = self.build_ele_list[0].listofMesuresChilds.value

                            self.build_ele_list[0].SelectorPPPFill.value= str(nBuild_ele)
                            self.build_ele_list_TD[0].SelectorPPPFill.value = self.build_ele_list[0].SelectorPPPFill.value

                            self.list_of_build_ele.append(self.build_ele_list_TD[0])#self.copiar_build_ele())#.deep_copy())
                            self.list_of_prop_list.append(self.control_props_list[0])
                            self.llistaElemPerFill.append([])
                            #result, script, build_ele = self.build_ele_service.read_build_ele_from_pyp(self.file_name)

                            #file_name = get_file_name_with_num(self.file_name, nBuild_ele)
                            file_name = self.crate_filename(self.file_name)
                            self.list_of_filenames.append(file_name)
                            self.build_ele_list_TD[0].NameFilesChildren.value = self.list_of_filenames



                        #si es 0 mostrar self.build_ele_list_TD[0]
                        #   (self.build_ele_list[0] = self.build_ele_list_TD[0])

                        TD_conjunt  =  TD_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listTD = self.element_listTD, Pared = self.paredTD , BarraLlargada=llargadaActual, TDAlcada = alcadaActual, numID= nPeca)
                        self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                        TD_conjunt.values_from_solid3D(desplacament, self.list_of_build_ele[nBuild_ele])
                        #self.result = TD_conjunt.get_result()
                        BuildingElementListService.write_to_file(self.list_of_filenames[nBuild_ele], [self.list_of_build_ele[nBuild_ele]])


                        #self.list_of_build_ele[nBuild_ele].FlagEntrada.value = 2
                        self.list_of_build_ele[nBuild_ele].SelectorPPPare.value = 2
                        self.list_of_build_ele[nBuild_ele].listofPythonChilds.value = self.build_ele_list[0].listofPythonChilds.value
                        self.list_of_build_ele[nBuild_ele].SelectorPPPFill.value = str(nBuild_ele)

                        #self.build_ele_list = []
                        #self.build_ele_list.append(self.list_of_build_ele[nBuild_ele])
                        self.valorAnt = nBuild_ele
                    else:
                        #if nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value):
                            #TD_conjunt  =  TD_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listTD = self.element_listTD, Pared = self.paredTD , BarraLlargada=llargadaActual, TDAlcada = alcada)#, element_listTD = self.element_listTD)#, BarraLlargada=llargada, TDAlcada = alcada)
                        if self.mostrarInici or nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value):
                            TD_conjunt  =  TD_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listTD = self.element_listTD, Pared = self.paredTD , BarraLlargada=-1, TDAlcada = -1, numID= nPeca)
                            self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                            self.build_ele_list[0] = self.set_value_list_stringcombobox_TD(self.build_ele_list[0], self.list_of_build_ele[nBuild_ele])
                            self.valorAnt = nBuild_ele
                elif self.conjuntSelected == 3:
                    posNovaMatrix = AllplanGeo.Matrix3D()

                    desplacament = self.build_ele_list[0].listofPositionsChilds.value[nPeca].X # pos[nPeca]["pos"][0]

                    posNovaMatrix.SetValue(12, desplacament)
                    llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPeca].X #pos[nPeca]["size"][0]
                    alcadaActual   = self.build_ele_list[0].listofMesuresChilds.value[nPeca].Y #alcada

                    '''
                    llargada, amplada, alcada = self.values_from_solid3D(self.paredEN)
                    #llargadaActual = llargada
                    llargadaActual = llargada - llargadaAfegida

                    posNovaMatrix = AllplanGeo.Matrix3D()

                    desplacament = 0

                    posNovaMatrix.SetValue(12, 0)
                    if llargadaAfegida != 0:
                        posNovaMatrix.SetValue(12, llargadaAfegida)
                        desplacament = llargadaAfegida

                    if llargadaActual > LlargadaMaximaEN:
                        llargadaActual = LlargadaMaximaEN
                        llargadaAfegida += LlargadaMaximaEN
                    else:
                        llargadaAfegida += llargadaActual
                        ultimAfegit =True
                        ultimAfegitVert = True
                    '''

                    if self.build_ele_list[0].FlagEntrada.value == 1:
                        while len(self.list_of_build_ele) <= nBuild_ele :
                            self.build_ele_list[0].listofPythonChilds.value.append(nBuild_ele)

                            result, self.build_ele_script, self.build_ele_list_TD, self.control_props_list,    \
                            self.build_ele_composite, part_name, self.file_name = \
                            self.build_ele_service.read_data_from_pyp(pyp_path + "\\EN\\PYP\\EN_Conjunt_8_child.pyp", BuildingElementStringTable("", False, ""), True,
                                                                        BuildingElementMaterialStringTable("", False, ""), pyp_path + "\\EN\\PYP\\EN_Conjunt_8_child.pyp")

                            self.build_ele_list_TD[0].BarraLlargadaEN.value = llargadaActual
                            self.build_ele_list_TD[0].BarraLlargadaVert.value = alcada
                            self.build_ele_list_TD[0].inputPoint.value = self.input_pnt
                            self.build_ele_list_TD[0].listofPositionsChilds.value = self.build_ele_list[0].listofPositionsChilds.value
                            self.build_ele_list_TD[0].listofMesuresChilds.value = self.build_ele_list[0].listofMesuresChilds.value


                            self.build_ele_list[0].SelectorPPPFill.value= str(nBuild_ele)
                            self.build_ele_list_TD[0].SelectorPPPFill.value = self.build_ele_list[0].SelectorPPPFill.value

                            self.list_of_build_ele.append(self.build_ele_list_TD[0])#self.copiar_build_ele())#.deep_copy())
                            self.list_of_prop_list.append(self.control_props_list[0])
                            self.llistaElemPerFill.append([])

                            file_name = self.crate_filename(self.file_name)
                            self.list_of_filenames.append(file_name)
                            self.build_ele_list_TD[0].NameFilesChildren.value = self.list_of_filenames

                        TD_conjunt  =  EN_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listEN = self.element_listEN, Pared = self.paredEN , BarraLlargada=llargadaActual, ENAlcada = alcadaActual, numID= nPeca)
                        self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                        TD_conjunt.set_values_tubs_true()
                        TD_conjunt.values_from_solid3D(desplacament, self.list_of_build_ele[nBuild_ele], self.atr_listEN)
                        BuildingElementListService.write_to_file(self.list_of_filenames[nBuild_ele], [self.list_of_build_ele[nBuild_ele]])

                        self.list_of_build_ele[nBuild_ele].SelectorPPPare.value = 3
                        self.list_of_build_ele[nBuild_ele].listofPythonChilds.value = self.build_ele_list[0].listofPythonChilds.value
                        self.list_of_build_ele[nBuild_ele].SelectorPPPFill.value = str(nBuild_ele)

                        self.valorAnt = nBuild_ele

                    else:
                        if self.mostrarInici or nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value):
                            TD_conjunt  =  EN_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listEN = self.element_listEN, Pared = self.paredEN , BarraLlargada=llargadaActual, ENAlcada = alcadaActual, numID= nPeca)
                            self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                            self.build_ele_list[0] = self.set_value_list_stringcombobox_EN(self.build_ele_list[0], self.list_of_build_ele[nBuild_ele])
                            self.valorAnt = nBuild_ele
                elif self.conjuntSelected == 4:



                    posNovaMatrix = AllplanGeo.Matrix3D()

                    posNovaMatrix.SetValue(12, self.build_ele_list[0].listofPositionsChilds.value[nPeca].X ) #pos[nPeca]["pos"][0])
                    posNovaMatrix.SetValue(13, self.build_ele_list[0].listofPositionsChilds.value[nPeca].Y ) #pos[nPeca]["pos"][1])
                    llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPeca].X  #pos[nPeca]["size"][0]
                    alcadaActual   = self.build_ele_list[0].listofMesuresChilds.value[nPeca].Y #pos[nPeca]["size"][1]

                    desplacament =  self.build_ele_list[0].listofPositionsChilds.value[nPeca].X #pos[nPeca]["pos"][0]

                    if self.build_ele_list[0].FlagEntrada.value == 1 or (self.recalcularIS and self.nrecalcularIS == nPeca) or len(self.list_of_build_ele) <= nBuild_ele:

                        while len(self.list_of_build_ele) <= nBuild_ele or (self.recalcularIS and self.nrecalcularIS == nPeca) :
                            if len(self.build_ele_list[0].listofPythonChilds.value) <= nBuild_ele:
                                self.build_ele_list[0].listofPythonChilds.value.append(nBuild_ele)

                            result, self.build_ele_script, self.build_ele_list_TD, self.control_props_list,    \
                            self.build_ele_composite, part_name, self.file_name = \
                            self.build_ele_service.read_data_from_pyp(pyp_path + "\\IS\\PYP\\IS_Conjunt_8_child.pyp", BuildingElementStringTable("", False, ""), True,
                                                                        BuildingElementMaterialStringTable("", False, ""), pyp_path + "\\IS\\PYP\\IS_Conjunt_8_child.pyp")

                            self.build_ele_list_TD[0].ISllargada.value = llargadaActual
                            self.build_ele_list_TD[0].ISAmplada.value = alcada
                            self.build_ele_list_TD[0].direccioISInv.value = self.build_ele.direccioISInv.value
                            self.build_ele_list_TD[0].inputPoint.value = self.input_pnt
                            self.build_ele_list_TD[0].listofPositionsChilds.value = self.build_ele_list[0].listofPositionsChilds.value
                            self.build_ele_list_TD[0].listofMesuresChilds.value = self.build_ele_list[0].listofMesuresChilds.value
                            self.build_ele_list_TD[0].totalPeces.value = self.build_ele_list[0].totalPeces.value

                            self.build_ele_list[0].SelectorPPPFill.value= str(nBuild_ele)
                            self.build_ele_list_TD[0].SelectorPPPFill.value = self.build_ele_list[0].SelectorPPPFill.value


                            if len(self.list_of_build_ele) <= nBuild_ele:
                                self.build_ele_list[0].listDireccioISInv.value.append(self.build_ele.direccioISInv.value)
                                self.build_ele_list_TD[0].listDireccioISInv.value = self.build_ele_list[0].listDireccioISInv.value
                                self.list_of_build_ele.append(self.build_ele_list_TD[0])#self.copiar_build_ele())#.deep_copy())
                                self.list_of_prop_list.append(self.control_props_list[0])
                                self.llistaElemPerFill.append([])
                            else:
                                self.list_of_build_ele[nPeca] = self.build_ele_list_TD[0]#self.copiar_build_ele())#.deep_copy())
                                self.list_of_prop_list[nPeca] = self.control_props_list[0]
                                self.llistaElemPerFill[nPeca] = []

                            file_name = self.crate_filename(self.file_name)
                            if len(self.list_of_filenames) <= nBuild_ele:
                                self.list_of_filenames.append(file_name)

                            '''
                            palette = BuildingElementPaletteService(
                                            build_ele_list            = self.build_ele_list_TD,
                                            build_ele_composite       = self.build_ele_composite,
                                            build_ele_script          = self.build_ele_script,
                                            build_ele_ctrl_props_list = self.control_props_list,
                                            picture_path              = "",
                                            script_object             = None)

                            self.palettelist.append(palette)
                            '''
                            if (self.recalcularIS and self.nrecalcularIS == nPeca) :
                                self.recalcularIS = False


                        self.build_ele_list[0].SelectorPPPFill.value= str(nBuild_ele)


                        if self.build_ele_list[0].listDireccioISInv.value[nPeca]:
                            llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPeca].X + 50 #pos[nPeca]["size"][0]

                        TD_conjunt  =  IS_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listIS = self.element_listIS, Pared = self.paredIS , BarraLlargada=llargadaActual , ISAlcada = alcadaActual)
                        self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                        self.set_value_list_stringcombobox_IS(self.list_of_build_ele[nBuild_ele], self.build_ele_list[0])
                        TD_conjunt.values_from_solid3D(desplacament, self.list_of_build_ele[nBuild_ele])

                        TD_conjunt  =  IS_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listIS = self.element_listIS, Pared = self.paredIS , BarraLlargada=llargadaActual , ISAlcada = alcadaActual)
                        self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                        self.set_value_list_stringcombobox_IS(self.build_ele_list[0], self.list_of_build_ele[nBuild_ele])
                        self.valorAnt = nBuild_ele

                        self.result = TD_conjunt.get_result()
                        BuildingElementListService.write_to_file(self.list_of_filenames[nBuild_ele], [self.list_of_build_ele[nBuild_ele]])

                        self.list_of_build_ele[nBuild_ele].SelectorPPPare.value = 4
                        self.list_of_build_ele[nBuild_ele].listofPythonChilds.value = self.build_ele_list[0].listofPythonChilds.value
                        self.list_of_build_ele[nBuild_ele].SelectorPPPFill.value = str(nBuild_ele)

                        self.valorAnt = nBuild_ele

                    else:
                        if self.mostrarInici or nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value):
                            #if self.build_ele_list[0].totalPeces.value >= len(self.list_of_build_ele[nBuild_ele].listofPositionsChilds.value):
                            #    for posChildUpdate in range(0, len(pos)):
                            #        if posChildUpdate >= len(self.list_of_build_ele[nBuild_ele].listofPositionsChilds.value):
                            #            self.list_of_build_ele[nBuild_ele].listofPositionsChilds.value.append(AllplanGeo.Point3D(pos[posChildUpdate]["pos"][0], pos[posChildUpdate]["pos"][1], 0))


                            if self.build_ele_list[0].listDireccioISInv.value[nPeca]:
                                llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPeca].X + 50 #pos[nPeca]["size"][0]

                            #TD_conjunt  =  IS_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, BarraLlargada=llargadaActual, ISAlcada = alcada)
                            TD_conjunt  =  IS_Conjunt_8(self.list_of_build_ele[nBuild_ele], doc, placement_mat= posNovaMatrix, element_listIS = self.element_listIS, Pared = self.paredIS , BarraLlargada=llargadaActual , ISAlcada = alcadaActual)
                            self.result = TD_conjunt.create_estructura(self.list_of_build_ele[nBuild_ele])
                            self.set_value_list_stringcombobox_IS(self.build_ele_list[0], self.list_of_build_ele[nBuild_ele])
                            self.valorAnt = nBuild_ele

                #if (self.build_ele_list[0].FlagEntrada.value != 1 and self.conjuntSelected != 1):
                if self.conjuntSelected != 1:
                    try:
                        if nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value) or self.build_ele_list[0].FlagEntrada.value == 1 or self.mostrarInici:
                            self.conjunt = TD_conjunt
                            #   self.result = TD_conjunt.get_result()
                            model_elem_list = self.result["elements"]
                            handle_list = self.result["handles"]
                            model_elem_list_preview = self.result["preview_elements"]
                            preview_symbols = self.result["preview_symbols"]

                            if self.build_ele_list[0].FlagEntrada.value == 1:
                                while len(self.llistaElemPerFill) <= nBuild_ele:
                                    self.llistaElemPerFill.append([])

                                for elem in model_elem_list:
                                    self.llistaElemPerFill[nBuild_ele].append(elem)
                            else:
                                posInModel = 0
                                if nBuild_ele == int(self.build_ele_list[0].SelectorPPPFill.value):
                                    self.llistaElemPerFill[nBuild_ele] = []
                                for elem in model_elem_list:
                                    if len(self.llistaElemPerFill[nBuild_ele]) <= posInModel:
                                        self.llistaElemPerFill[nBuild_ele].append(elem)
                                    else:
                                        self.llistaElemPerFill[nBuild_ele][posInModel] = elem

                                    posInModel += 1

                    except Exception as e:
                        preview_symbols = PreviewSymbols()
                        print("Error PythonPart")
                    #common_props   = AllplanBaseElements.CommonProperties()
                    #python_part_util.add_pythonpart_view_2d3d(model_elem_list_preview)

                    #self.build_ele.zUnique.value =  random.random() * 3600

                    print("retorna PythonPart")

                    for elem in pared_handle_list:
                        pared_handle_list.append(handle_list)


                    nBuild_ele += 1

            for elemPP in self.llistaElemPerFill:
                for elemTub in elemPP:
                    pared_model_elem_list.append(elemTub)




            if self.build_ele_list[0].FlagEntrada.value == 2:
                self.mostrarInici = False

            self.build_ele_list[0].FlagEntrada.value = 2
            #self.build_ele_list[0].SelectorPPPFill.value = nBuild_ele

            #return CreateElementResult(python_part,
            #                   multi_placement = True)

            #return CreateElementResult(group_elems, handle_list,
            #return CreateElementResult(model_elem_list, handle_list,

            self.palette.update_palette(-1,True,True)
            return CreateElementResult(pared_model_elem_list, pared_handle_list,
                                   multi_placement = False,
                                   preview_symbols=preview_symbols,
                                   placement_point = self.point_input_result.input_point)#self.input_pnt)

            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               model_elem_list + cube_element , [], None)
        else:
            cube_element = self.get_cuboid()
            print("retorna Cube")
            self.build_ele_list[0].FlagEntrada.value = 2
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



        #print("3 - palette_service: " + str(self.build_ele_list[0].IntegerTDSelector.value))
        n = int(self.build_ele_list[0].SelectorPPPFill.value)
        #valorAnt = int(self.build_ele_list[0].SelectorPPPFill.value)
        if _name != "SelectorPPPFill":
            BuildingElementValueUtil.update_value(_name, _value, self.list_of_build_ele[n], self.list_of_prop_list[n])# ,self.build_ele_ctrl_props_list)

            if _name == "direccioISInv":
                self.build_ele.FlagEntrada.value = 1
                self.build_ele.listofMesuresChilds.value = []
                self.build_ele.listofPositionsChilds.value = []
                self.build_ele.NameFilesChildren.value = []
                self.build_ele.listofPythonChilds.value = []
                self.build_ele.SelectorPPPFill.value = str(0)

                self.build_ele_list[0].FlagEntrada.value = 1

                self.mostrarInici = True

                self.llistaElemPerFill = []
                self.list_of_build_ele = []
                self.list_of_prop_list = []
                self.llistaElemPerFill = []

                for posDir in range(0, len(self.list_of_build_ele)):
                    self.list_of_build_ele[posDir].direccioISInv.value = _value
                    BuildingElementValueUtil.update_value(_name, _value, self.list_of_build_ele[posDir], self.list_of_prop_list[posDir])# ,self.build_ele_ctrl_props_list)

            if _name == "direccioISInvActual":
                self.recalcularIS = True
                self.nrecalcularIS = n
                llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[n].Y #pos[nPeca]["size"][1]
                alcadaActual   = self.build_ele_list[0].listofMesuresChilds.value[n].X  #pos[nPeca]["size"][0]

                self.build_ele_list[0].listofMesuresChilds.value[n].Y = alcadaActual#pos[nPeca]["size"][1]
                self.build_ele_list[0].listofMesuresChilds.value[n].X = llargadaActual

                self.build_ele_list[0].listDireccioISInv.value[n] = self.build_ele_list[0].direccioISInvActual.value

            #prop = self.build_ele_list[0].get_property(_name)
            #prop.value = _value
            #self.list_of_build_ele[n].set_property(name =_name,value = prop )
        else:
            #guardar build_ele_anterior
            #BuildingElementService.write_data_to_default_favorite_file(self.list_of_build_ele[valorAnt])

            BuildingElementListService.write_to_file(self.list_of_filenames[int(self.valorAnt)], [self.list_of_build_ele[int(self.valorAnt)]])
            BuildingElementListService.read_from_file(self.list_of_filenames[int(_value)], self.build_ele_list)


            #self.build_ele_list[0] = self.copiar_build_ele(self.list_of_build_ele[int(_value)])
            #self.build_ele = self.copiar_build_ele(self.list_of_build_ele[int(_value)])

            #self.build_ele =self.list_of_build_ele[int(_value)]
            self.valorAnt = int(_value)

            #self.build_ele_list[0] = self.list_of_build_ele[n]
            #self.palette_service.update_palette(-1, True)


            #self.palettelist[int(_value)].show_palette(part_name= self.list_of_filenames[int(_value)],open_palette= True, is_visual_script=True)

        #self.list_of_build_ele[n].set_property(_name,_value)
        #self.list_of_build_ele[0].modify_value_type(_name, _value)
        #self.list_of_build_ele[0] = self.list_of_build_ele[0]._____._replace(_name = _value)

        self.execute()

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
            print(str(e))


        self.script_object_interactor = None    # terminate the selection interactor
        return OnCancelFunctionResult.CANCEL_INPUT
        #return OnCancelFunctionResult.CREATE_ELEMENTS


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

        self.build_ele.listUUIDElements.value = []
        self.build_ele_list[0].listUUIDElements.value = []

        python_part_util = PythonPartUtil()

        cube_element = self.get_cuboid()
        #cube_element.SetAttributes(attributes)

        #python_part_util.add_architecture_elements([cube_element])
        connect_to_elements = []

        if self.conjuntSelected != 1:
            llargadaPerAfegir = 0
            llargadaAfegida = 0
            ultimAfegit = False

            build_ele = self.build_ele #self.build_ele_list[1] #self.palette_service.build_ele_list #self.build_ele_script
            doc = DocumentManager.get_instance().document#self.__doc__

            #TD_conjunt  =  TD_Conjunt_8(build_ele, DocumentManager.get_instance().document)


            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               model_elem_list , [], None, createUndoStep= True)
        else:
            cube_element = self.get_cuboid()
            print("acaba en cub")
            #AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
            #                               self.placement_mat,#AllplanGeo.Matrix3D(),
            #                               cube_element , [], None)



        #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura"
        pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025"
        pythonpart_group = []#PythonPartGroup.from_build_ele(self.build_ele_list[0])
        sub_build_ele = None
        sub_script= None
        sub_build_ele = None
        pared = []
        LlargadaMaxima = 2000

        if self.conjuntSelected == 2:
            #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura\\TD\\PYP"
            pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025\\TD\\PYP"
            result, sub_script, sub_build_ele = BuildingElementService.read_build_ele_from_pyp(pyp_path + "\\TD_Conjunt_8_child.pyp")
            pared = self.paredTD
            LlargadaMaxima = LlargadaMaximaTD
            llargada, amplada, alcada = self.values_from_solid3D(self.paredTD)
            posPared = self.calcular_posiciones(self.paredTD)
            self.build_ele_list[0].totalPeces.value, pos, areaTotal = self.calcular_encaje_con_recorte(llargada, amplada,LlargadaMaximaTD, amplada, self.element_listTD, posPared)
        elif self.conjuntSelected == 3:
            #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura\\EN\\PYP"
            pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025\\EN\\PYP"
            result, sub_script, sub_build_ele = BuildingElementService.read_build_ele_from_pyp(pyp_path + "\\EN_Conjunt_8_child.pyp")
            pared = self.paredEN
            LlargadaMaxima = LlargadaMaximaEN
            llargada, amplada, alcada = self.values_from_solid3D(self.paredEN)
            posPared = self.calcular_posiciones(self.paredEN)
            self.build_ele_list[0].totalPeces.value, pos, areaTotal = self.calcular_encaje_con_recorte(llargada, amplada,LlargadaMaximaEN, amplada, self.element_listEN, posPared)
        elif self.conjuntSelected == 4:
            #pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + "PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura\\IS\\PYP"
            pyp_path = "\\\\192.168.30.250\\compartit\\ALLPLAN_2025\\STD\\Library\\PythonParts\\2025\\IS\\PYP"
            result, sub_script, sub_build_ele = BuildingElementService.read_build_ele_from_pyp(pyp_path + "\\IS_Conjunt_8_child.pyp")
            pared = self.paredIS
            #LlargadaMaxima = LlargadaMaximaIS
            llargada, amplada, alcada = self.values_from_solid3D(self.paredIS)
            if self.build_ele.direccioISInv.value:
                LlargadaMaximaIS = 2150
                alcadaMaximaIS = 5650
            else:
                LlargadaMaximaIS = 5650
                alcadaMaximaIS = 2150
            posPared = self.calcular_posiciones(self.paredIS)
            self.build_ele_list[0].totalPeces.value, pos, areaTotal = self.calcular_encaje_con_recorteIS(llargada, amplada,LlargadaMaximaIS, alcadaMaximaIS, self.element_listIS, posPared)


        if self.build_ele_list[0].totalPeces.value < len(self.build_ele_list[0].listofPositionsChilds.value):
            self.build_ele_list[0].totalPeces.value = len(self.build_ele_list[0].listofPositionsChilds.value)


        listDocumnets = AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
        while len(listDocumnets) < self.build_ele_list[0].totalPeces.value:
            nouDoc = tuple[str,int]
            nouDoc = ( "DF" + str( int(listDocumnets[len(listDocumnets)-1][1]) + 1) , int(listDocumnets[len(listDocumnets)-1][1]) + 1)
            #nouDoc.append( int(listDocumnets[len(listDocumnets)-1][1]) + 1 )
            #AllplanElementAdapter.DocumentNameService.GetActiveDocumentName()
            listDocumnets.append(nouDoc)


        nTotalPeca = 0
        #while not ultimAfegit and not ultimAfegitVert:
        for nPPChild in range(0,self.build_ele_list[0].totalPeces.value):
        #for nPPChild in range(0, len(self.list_of_build_ele)):


            #if len(build_ele.NameFilesChildren.value) > nPPChild:
            #    build_ele.NameFilesChildren.value[nPPChild] = self.list_of_filenames[nPPChild]
            #else:
            #    build_ele.NameFilesChildren.value.append(self.list_of_filenames[nPPChild])

            for nPPChildPos in range(0,self.build_ele_list[0].totalPeces.value):
                if len(build_ele.NameFilesChildren.value) > nPPChildPos:
                    build_ele.NameFilesChildren.value[nPPChildPos] = self.list_of_filenames[nPPChildPos]
                else:
                    build_ele.NameFilesChildren.value.append(self.list_of_filenames[nPPChildPos])

                if len(self.list_of_build_ele[nPPChild].NameFilesChildren.value) > nPPChildPos:
                    self.list_of_build_ele[nPPChild].NameFilesChildren.value[nPPChildPos] = self.list_of_filenames[nPPChildPos]
                else:
                    self.list_of_build_ele[nPPChild].NameFilesChildren.value.append(self.list_of_filenames[nPPChildPos])

                if nPPChildPos >= len(self.build_ele_list[0].listofPositionsChilds.value):
                    #self.posChilds.append(AllplanGeo.Point3D(pos[nPPChildPos]["pos"][0], pos[nPPChildPos]["pos"][1], 0))
                    self.build_ele_list[0].listofPositionsChilds.value.append(AllplanGeo.Point3D(pos[nPPChildPos]["pos"][0], pos[nPPChildPos]["pos"][1], 0))
                if nPPChildPos >= len(self.list_of_build_ele[nPPChild].listofPositionsChilds.value):
                    self.list_of_build_ele[nPPChild].listofPositionsChilds.value.append(AllplanGeo.Point3D(pos[nPPChildPos]["pos"][0], pos[nPPChildPos]["pos"][1], 0))
                if nPPChildPos >= len(self.build_ele_list[0].listofMesuresChilds.value):
                    self.build_ele_list[0].listofMesuresChilds.value.append(AllplanGeo.Point3D(pos[nPPChildPos]["size"][0], pos[nPPChildPos]["size"][1], 0))
                if nPPChildPos >= len(self.list_of_build_ele[nPPChild].listofMesuresChilds.value):
                    self.list_of_build_ele[nPPChild].listofMesuresChilds.value.append(AllplanGeo.Point3D(pos[nPPChildPos]["size"][0], pos[nPPChildPos]["size"][1], 0))

            llargada, amplada, alcada = self.values_from_solid3D(pared)
            #if self.conjuntSelected == 4:
            #    llargada, alcada, amplada  = self.values_from_solid3D(pared)

            #llargadaActual = llargada
            '''
            llargadaActual = llargada - llargadaAfegida

            posNovaMatrix = AllplanGeo.Matrix3D()
            posNovaMatrix.SetValue(12, self.point_input_result.input_point.X)
            posNovaMatrix.SetValue(13, self.point_input_result.input_point.Y)
            posNovaMatrix.SetValue(14, self.point_input_result.input_point.Z)

            if llargadaAfegida != 0:
                posNovaMatrix.SetValue(12, self.point_input_result.input_point.X + llargadaAfegida)

            if llargadaActual > LlargadaMaxima:
                llargadaActual = LlargadaMaxima
                llargadaAfegida += LlargadaMaxima
            else:
                llargadaAfegida += llargadaActual
                ultimAfegit =True


            if self.conjuntSelected == 4:
            '''
            posNovaMatrix = AllplanGeo.Matrix3D()


            llargadaActual = self.build_ele_list[0].listofMesuresChilds.value[nPPChild].X #pos[nPPChild]["size"][0]
            alcadaActual   = self.build_ele_list[0].listofMesuresChilds.value[nPPChild].X #pos[nPPChild]["size"][1]
            posNovaMatrix.SetValue(12, self.point_input_result.input_point.X + self.build_ele_list[0].listofPositionsChilds.value[nPPChild].X)#pos[nPPChild]["pos"][0])
            posNovaMatrix.SetValue(13, self.point_input_result.input_point.Y + self.build_ele_list[0].listofPositionsChilds.value[nPPChild].Y)#pos[nPPChild]["pos"][1])
            posNovaMatrix.SetValue(14, self.point_input_result.input_point.Z )

            #listDocumnets = AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
            #print(sf)

            docValue = 0
            if len(listDocumnets) > nPPChild:
                docValue = nPPChild
            #for docValue in range(0,len(listDocumnets)):#[listDocumnets[0][1]]:

            doc = DocumentManager.get_instance().document
            doc = AllplanElementAdapter.DocumentNameService.GetDocumentNameByFileIndex(listDocumnets[docValue][1], True, True, "TEST")
            docDrawingFile = AllplanBaseElements.DrawingFileService()
            docAdapter = AllplanElementAdapter.DocumentAdapter()
            doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[docValue][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)
            TD_conjunt = None
            type_display_name = "ERROR"
            if self.conjuntSelected == 2:
                TD_conjunt  =  TD_Conjunt_8(self.list_of_build_ele[nPPChild], doc, placement_mat= posNovaMatrix, BarraLlargada=llargadaActual, TDAlcada = alcada, numID= nPPChild)#, element_listTD = self.element_listTD)#, BarraLlargada=llargada, TDAlcada = alcada)
                type_display_name = "TD_Conjunt_8_child.pyp"
            elif self.conjuntSelected == 3:
                TD_conjunt  =  EN_Conjunt_8(self.list_of_build_ele[nPPChild], doc, placement_mat= posNovaMatrix, BarraLlargada=llargadaActual, ENAlcada = alcadaActual, numID= nPPChild)#, element_listTD = self.element_listTD)#, BarraLlargada=llargada, TDAlcada = alcada)
                type_display_name = "EN_Conjunt_8_child.pyp"
            elif self.conjuntSelected == 4:
                TD_conjunt  =  IS_Conjunt_8(self.list_of_build_ele[nPPChild], doc, placement_mat= posNovaMatrix, BarraLlargada=llargadaActual +50 , ISAlcada = alcadaActual)#, element_listTD = self.element_listTD)#, BarraLlargada=llargada, TDAlcada = alcada)
                type_display_name = "IS_Conjunt_8_child.pyp"

            if TD_conjunt == None:
                return []

            result = TD_conjunt.create()

            #sub_build_ele = cast(TD_Conjunt_8, sub_build_ele)
            #pythonpart = sub_script.create_pythonpart(sub_build_ele)

            #box_pythonpart = cast(PythonPart, sub_script.create_pythonpart(self.list_of_build_ele[nPPChild], self.coord_input.GetActiveViewDocument(), posNovaMatrix))
            box_pythonpart = result["elements"]
            python_part_utilChild = PythonPartUtil()
            python_part_utilChild.add_pythonpart_view_2d3d(box_pythonpart)
            pythonPartsChild = python_part_utilChild.create_pythonpart(
                    self.list_of_build_ele[nPPChild],
                    type_display_name = type_display_name,
                    #placement_matrix = AllplanGeo.Matrix3D(),
                    placement_matrix = self.placement_mat,
                    local_placement_matrix = AllplanGeo.Matrix3D()
                )
            #pythonpart_group.append(box_pythonpart)
            pythonpart_group.append(pythonPartsChild)

            pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())#, connect_to_pyp= connectionPP ,connect_to_ele=connectionEle )
            base_elems = AllplanElementAdapter.BaseElementAdapterList()
            base_elems = pyp_transaction.execute(
                placement_matrix =  AllplanGeo.Matrix3D(),
                view_world_projection= AllplanIFW.ViewWorldProjection(),
                model_ele_list = pythonPartsChild,#pythonpart_group,#pythonParts,

                modification_ele_list= ModificationElementList(),
                uuid_parameter_name = "TD Python",#get_file_name(self.list_of_filenames[nPPChild]),#
                # elements_to_delete=build_ele.created_elems.value
            )

            cont = nTotalPeca
            for elemBase in base_elems:
                if len(self.build_ele.listUUIDElements.value) <= cont:
                    self.build_ele.listUUIDElements.value.append(str(elemBase.GetElementUUID()))
                else:
                    self.build_ele.listUUIDElements.value[cont] = str(elemBase.GetElementUUID())
                if len(self.build_ele_list[0].listUUIDElements.value) <= cont:
                    self.build_ele_list[0].listUUIDElements.value.append(str(elemBase.GetElementUUID()))
                else:
                    self.build_ele_list[0].listUUIDElements.value[cont] = str(elemBase.GetElementUUID())
                if len(self.list_of_build_ele[nPPChild].listUUIDElements.value) <= cont :
                    self.list_of_build_ele[nPPChild].listUUIDElements.value.append(str(elemBase.GetElementUUID()))
                else:
                    self.list_of_build_ele[nPPChild].listUUIDElements.value[cont] = str(elemBase.GetElementUUID())
                cont += 1

            if docValue == 0:
                #if self.build_ele.SelectorPPPare.value != 4:
                self.elemCube = self.get_cuboid()
                for eleMcUB in self.elemCube:
                    python_part_util = PythonPartUtil()
                    python_part_util.add_pythonpart_view_2d3d(eleMcUB) #self.get_cuboid())


                    print("pyp_transaction -- 1")
                    pythonParts = python_part_util.create_pythonpart(
                                self.build_ele_list, #,+ self.list_of_build_ele,
                                type_display_name = "Parent_Script_selection.py",
                                #placement_matrix = AllplanGeo.Matrix3D(),
                                placement_matrix = self.placement_mat,
                                local_placement_matrix = AllplanGeo.Matrix3D()
                            )

                    pyp_transaction = PythonPartTransaction(self.coord_input.GetActiveViewDocument())
                    #self.build_ele.zUnique.value =  random.random() * 3600
                    base_elems = pyp_transaction.execute(
                        placement_matrix =  AllplanGeo.Matrix3D(),
                        view_world_projection= AllplanIFW.ViewWorldProjection(),
                        model_ele_list = pythonParts,
                        modification_ele_list= ModificationElementList(),
                        uuid_parameter_name = "Pared Python",
                        #elements_to_delete = elems_to_delete #build_ele.created_elems.value
                    )

                    for elemBase in base_elems:
                        self.build_ele.listUUIDElements.value.append(elemBase.GetElementUUID())
                        cont += 1
            nTotalPeca = cont

        doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[0][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)


        for nPPChild in range(0,self.build_ele_list[0].totalPeces.value):
            for nPPChildPos in range(0,self.build_ele_list[0].totalPeces.value):
                if len(self.list_of_build_ele[nPPChild].NameFilesChildren.value) > nPPChild:
                    self.list_of_build_ele[nPPChild].NameFilesChildren.value[nPPChild] = self.list_of_filenames[nPPChild]
                else:
                    self.list_of_build_ele[nPPChild].NameFilesChildren.value.append(self.list_of_filenames[nPPChild])



        self.guardar_datos_json()
        #edit
        #ModifyPythonPartParameterUtil.execute(pythonParts[0], self.coord_input, self.list_of_build_ele)


        #return CreateElementResult(python_part_util.create())
        #return python_part_util.get_pythonpart(build_ele)
        for nPPChild in range(0,len(self.list_of_filenames)):
            if len(build_ele.NameFilesChildren.value) < nPPChild or len(build_ele.NameFilesChildren.value) == 0:
                build_ele.NameFilesChildren.value.append(self.list_of_filenames[nPPChild])



        for property in self.build_ele_Orginal.get_properties():
            #print(property)
            try:
                #print(build_ele.get_property(str(property.name)))
                #BuildingElement.get_property
                prop = self.build_ele_list[0].get_property(str(property.name))
                if prop != None:
                    prop.value = property.value
                    #self.build_ele_list[0].set_property(str(property.name), property)
                #build_ele.set_property(str(property.name), property)
                #print(build_ele.get_property(str(property.name)))
            except Exception as e:
                print("Error al guardar valors: " + str(e))


        #return base_elems
        print("Conjunt_creat")

        #return pyp_transaction


        #return CreateElementResult([base_elems],
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

        if event_id == 3000:#recalcul IS
            self.build_ele_list[0].totalPeces.value += 1
            self.build_ele_list[0].listofPythonChilds.value.append(len(self.build_ele_list[0].listofPythonChilds.value))
        elif event_id == 3001:#recalcul IS
            self.build_ele_list[0].totalPeces.value -= 1


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

        if len(element_list) == 0:
            return self.build_ele.llargadaPared.value, self.build_ele.ampladaPared.value, self.build_ele.alcadaPared.value
        amplada  = 0 #max 2150
        llargada = 0 #max 5650

        iniciConjunt = True
        puntInferiorEsqIS = AllplanGeo.Point3D()
        puntInferiorDreIS = AllplanGeo.Point3D()
        puntSuperiorEsqIS = AllplanGeo.Point3D()
        puntSuperiorDreIS = AllplanGeo.Point3D()
        puntAltIS         = AllplanGeo.Point3D()
        puntBaixIS         = AllplanGeo.Point3D()

        llargada = LlargadaMaximaTD
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

            try:
                geo = element.GetGeometry()
            except Exception as e:
                try:
                    geo = element
                except Exception as e:
                    print("--")
                print("-")


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
        self.build_ele.llargadaPared.value = llargada
        self.build_ele.ampladaPared.value = amplada
        self.build_ele.alcadaPared.value = alcada
        return llargada, amplada, alcada



    def get_cuboid(self) -> ModelEleList:
        length = 0
        width = 0

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

    def guardar_datos_json(self):
        nPPchild = 0
        for fileNameChild in self.list_of_filenames:
            if not os.path.exists(fileNameChild):
                open(fileNameChild, "x")
            #fileNameChild = fileNameChild.replace('\\', '/')
            #BuildingElementService.write_data_to_default_favorite_file(self.build_ele_list)
            #params_list = BuildingElementListService.get_params_list([self.list_of_build_ele[nPPchild]], ParameterProperty.Persistent.MODEL_AND_FAVORITE)
            dict_values = self.list_of_build_ele[nPPchild].get_parameter_dict()
            self.guardar_parametros_como_xml(dict_values, fileNameChild, nPPchild)

            nPPchild +=1

            '''
            #tree = ElementTree.parse(str(fileNameChild))
            #root = tree.getroot()
            parametros = []
            for param in root.findall(".//Parameter"):
                nombre = None
                tipo = None
                valor = None

                for child in param:
                    if child.tag == "Name":
                        nombre = child.text
                    elif child.tag == "Value":
                        valor = child.text
                    elif child.tag == "ValueType":
                        tipo = child.text

                if nombre:
                    parametros.append({
                        "nombre": nombre,
                        "tipo": tipo,
                        "valor": valor
                    })

            with open(str(fileNameChild), "w", encoding="utf-8") as f:
                json.dump(parametros, f, indent=4, ensure_ascii=False)
            '''



    def tipo_valor(self, valor):
        """Detecta el tipo de dato como lo usaría una PythonPart."""
        if isinstance(valor, int):
            return "Integer"
        elif isinstance(valor, float):
            return "Double"
        elif isinstance(valor, bool):
            return "Boolean"
        elif isinstance(valor, list):
            #if issubclass(valor[0], "namedtuple"):
            #    return "namedtuple"
            #elif issubclass(valor[0], "StirrupList"):
            #    return "StirrupList"
            #elif issubclass(valor[0], int):
            return "List"
        #elif isinstance(valor, Separator):
        #    return "Separator"
        else:
            return "String"

    def guardar_parametros_como_xml(self, diccionario, ruta_archivo, nBuildEle):
        valueTypeDict = {}


        root = ElementTree.Element("Element")  # Nodo raíz típico
        rootScript = ElementTree.SubElement(root, "Script")
        ElementTree.SubElement(rootScript, "Name").text = "Modelat\\Estructura\\TD\\PY\\TD_Conjunt_8_clase_PPTD_Solids.py"
        #ElementTree.SubElement(rootScript, "Name").text = "C:\\ProgramData\\Nemetschek\\Allplan\\2025\\Etc\\PythonPartsFramework\\GeneralScripts\\Modelat\\Estructura\\TD\\PY\\TD_Conjunt_8_clase_PPTD.py"
        ElementTree.SubElement(rootScript, "Title").text = "Python Part TD 27.0"
        ElementTree.SubElement(rootScript, "Version").text = "27.0"
        ElementTree.SubElement(rootScript, "ReadLastInput").text = "True"
        ElementTree.SubElement(rootScript, "DataColumnWidth").text = "150"

        rootPage = ElementTree.SubElement(root, "Page")  # Nodo raíz típico
        ElementTree.SubElement(rootPage, "Name").text = "Pagina"+str(nBuildEle)
        ElementTree.SubElement(rootPage, "Text").text = "Pagina"+str(nBuildEle)
        ElementTree.SubElement(rootPage, "ValueType").text = "Expander"
        ElementTree.SubElement(rootPage, "ExcludeIdentical").text = "True"


        for clave, valor in diccionario.items():
            property = self.list_of_build_ele[nBuildEle].get_property(clave)#.get_existing_property()
            valueType = property.value_type
            valueTypeDict[property.value_type] = property.value_type

            if valueType != "radiobuttongroup" and valueType != "radiobutton":
                param = ElementTree.SubElement(rootPage, "Parameter")
                ElementTree.SubElement(param, "Name").text = clave

                if str(valueType).startswith("namedtuple") or str(valueType).startswith("StirrupList") or str(valueType).startswith("UShape"):
                    fieldnames = ''
                    fieldnameslist = []
                    coma = False

                    '''
                    if len(valor)>0:
                        for fieldName in valor[0]._fields:
                            if coma :
                                fieldnames += ','
                            else:
                                coma = True
                            fieldnames += fieldName
                            fieldnameslist.append(fieldName)
                    else:
                    '''
                    for fieldName in property.named_tuple_def.field_names:
                        if coma :
                            fieldnames += ','
                        else:
                            coma = True
                        fieldnames += fieldName
                        fieldnameslist.append(fieldName)



                    valors = "["
                    numValor = 0
                    for nValor in valor:
                        listNvalors = ''
                        #llistaValues = self.list_of_build_ele[nBuildEle].__getattribute__(clave)

                        for namValue in fieldnameslist: #nValor._fields: #fieldnameslist:
                            try:
                                #dictionariValues = nValor._asdict[namValue]
                                #value = llistaValues.value[numValor].__getattribute__(namValue)
                                value = nValor.__getattribute__(namValue)
                                listNvalors += str(value) + '|'
                            except Exception as e:
                                listNvalors += ' None|'
                                print("error writing on file: " + str(e) )


                        '''
                        listNvalors = list(nValor)
                        listNvalors = str(listNvalors).replace(' \'','')
                        listNvalors = str(listNvalors).replace('\' ','')
                        listNvalors = str(listNvalors).replace('\'','')
                        listNvalors = str(listNvalors).replace('[','')
                        listNvalors = str(listNvalors).replace(']','')
                        listNvalors = str(listNvalors).replace(',','|')
                        #guarda desordenat?
                        #listNvalors = listNvalors[len(listNvalors) -1 ]
                        '''
                        listNvalors = listNvalors[0:len(listNvalors) -1 ]
                        valors += listNvalors + ';'

                        numValor += 1
                    #valors = valors[0:len(valors)-2]
                    valors += "]"

                    #valors, names = get_names_values_list_pyp(valor)

                    ElementTree.SubElement(param, "Text").text = fieldnames
                    ElementTree.SubElement(param, "Value").text = str(valors)
                    #ElementTree.SubElement(param, "Value").text = str(valor)
                    ElementTree.SubElement(param, "ValueType").text = valueType


                    namedTuple = ElementTree.SubElement(param, "NamedTuple")
                    ElementTree.SubElement(namedTuple, "TypeName").text = property.named_tuple_def.typename


                    ElementTree.SubElement(namedTuple, "FieldNames").text = fieldnames#property.named_tuple_def.field_names
                else:

                    if valueType == 'point3d': #point3d
                        listValors = str(valor).replace('),',');')
                        ElementTree.SubElement(param, "Value").text = str(listValors)
                        ElementTree.SubElement(param, "ValueType").text = "Point3D"
                    elif clave != 'Separator':
                        ElementTree.SubElement(param, "Value").text = str(valor)
                    ElementTree.SubElement(param, "ValueType").text = valueType
                ElementTree.SubElement(param, "Persistent").text = "Model"
            elif valueType == "radiobuttongroup":
                paramRadioBG = ElementTree.SubElement(rootPage, "Parameter")
                #param = ElementTree.SubElement(rootPage, "Parameter")
                ElementTree.SubElement(paramRadioBG, "Name").text = clave
                ElementTree.SubElement(paramRadioBG, "Value").text = str(valor)
                ElementTree.SubElement(paramRadioBG, "ValueType").text = valueType#self.tipo_valor(valor)
                ElementTree.SubElement(paramRadioBG, "Persistent").text = "Model"
            else: #and valueType == "radiobutton":
                paramRadioB = ElementTree.SubElement(paramRadioBG, "Parameter")
                ElementTree.SubElement(paramRadioB, "Name").text = clave
                ElementTree.SubElement(paramRadioB, "Value").text = str(valor)
                ElementTree.SubElement(paramRadioB, "ValueType").text = valueType#self.tipo_valor(valor)
                ElementTree.SubElement(paramRadioB, "Persistent").text = "Model"



            #if valueType == "radiobuttongroup":
            #    while nouValueType == radiobutton



        tree = ElementTree.ElementTree(root)
        tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)

        print(f"Archivo XML guardado en: {ruta_archivo}")



    def load_parameters_from_json(self,json_path):
        if not os.path.exists(json_path):
            print(f"No se encontró el archivo: {json_path}")
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)

        parametros = []
        for p in datos:
            nombre = p["nombre"]
            tipo = p["tipo"]
            valor = p["valor"]

            # Conversión de tipos
            if tipo == "Integer":
                valor = int(valor)
            elif tipo == "Double" or tipo == "Float":
                valor = float(valor)
            elif tipo == "Boolean":
                valor = bool(int(valor))
            elif tipo == "String":
                valor = str(valor)

            # Crea el parámetro como lo usarías en PythonParts
            parametros.append((nombre, valor))

        return parametros


    def crate_filename(self, fileName:str):
        extension = ''
        lastDig = ''
        while fileName != '' and (lastDig != '.' and lastDig != '\\'):
            lastDig = fileName[len(fileName)-1]
            extension = lastDig + extension
            fileName = fileName[0:len(fileName)-1]
        s = str(random.random() * 3600)
        fileNameChild = str(fileName) + str( s.replace('.', '-')) + extension

        extension = ''
        lastDig = ''
        directori = fileNameChild
        while directori != '' and ( lastDig != '\\'):
            lastDig = directori[len(directori)-1]
            extension = lastDig + extension
            #nameFile = lastDig + extension
            directori = directori[0:len(directori)-1]

        fileNameChild = str(directori) + "\\" + self.projectName + extension
        #fileNameChild = str( fileNameChild.replace('TD\\PYP\\', ''))
        if not os.path.exists(fileNameChild):
            return fileNameChild
        else:
            fileNameChild = self.crate_filename(fileName)
            return fileNameChild
        #newName = str(filename) +str( random.random() * 3600)
        #return newName
        #build_ele.NameFilesChildren.value


    def set_value_list_stringcombobox_IS(self, build_ele, build_eleDades):

        build_ele.listofMesuresChilds.value = build_eleDades.listofMesuresChilds.value
        build_ele.listofPythonChilds.value = build_eleDades.listofPythonChilds.value
        build_ele.SelectorPPPFill.ValueList = "[str(value) for value in listofPythonChilds]"
        #build_ele.SelectorTubHor.value
        build_ele.IntegerISSelectorHor.value = len(build_eleDades.dadesTubHor.value)
        build_ele.TipusTUB.ValueList = "TUB A|TUB B|TUB C|TUB D|TUB E|TUB F"

        build_ele.valueListBarresHorBalcOnlyNum.value = build_eleDades.valueListBarresHorBalcOnlyNum.value
        build_ele.valueListBarresHorBalcOnlyNumVert.value = build_eleDades.valueListBarresHorBalcOnlyNumVert.value
        build_ele.TipusLinia.ValueList = "Tipus 1|Tipus 2"

        build_ele.SelectorTubHor.value = build_eleDades.SelectorTubHor.value

        build_ele.direccioISInv.value = build_eleDades.direccioISInv.value

        build_ele.listDireccioISInv.value = build_eleDades.listDireccioISInv.value



        #build_ele = self.copiar_build_ele(build_eleDades)

    def set_value_list_stringcombobox_TD(self, build_ele, build_eleDades):

        #build_ele = self.copiar_build_ele(build_eleDades)

        #build_ele.SelectorTubHor.value
        build_ele.listofPythonChilds.value = build_eleDades.listofPythonChilds.value
        build_ele.SelectorPPPFill.ValueList = "[str(value) for value in listofPythonChilds]"

        build_ele.SelectorTDHTD.ValueList = "TD Inferior|TD Superior|Mes Tubs..."
        build_ele.SelectorTDHInf.ValueList = "Tub|L"
        build_ele.SelectorTDHSup.ValueList = "Tub|L|Tub + L"

        build_ele.valueListBarresHorBalcOnlyNum.value = build_eleDades.valueListBarresHorBalcOnlyNum.value
        build_ele.SelectorTDHTotal.ValueList = "[str(value) for value in valueListBarresHorBalcOnlyNum]"

        build_ele.IntegerTDSelector.value = build_eleDades.IntegerTDSelector.value
        build_ele.SelectorTDV.ValueList = "['TDVer '+str(value) for value in range(0, IntegerTDSelector)]"

        build_ele.IntegerBalcFinSelector.value = build_eleDades.IntegerBalcFinSelector.value
        build_ele.SelectorBalcFin.ValueList = "['Balc/Fin '+str(value) for value in range(0, IntegerBalcFinSelector)]"
        build_ele.valueVertListBarresHorInf.value = build_eleDades.valueVertListBarresHorInf.value
        build_ele.SelectorTDHorInf.ValueList = "[str(value) for value in valueVertListBarresHorInf]"
        build_ele.valueVertListBarresHorSup.value = build_eleDades.valueVertListBarresHorSup.value
        build_ele.SelectorTDHorSup.ValueList = "[str(value) for value in valueVertListBarresHorSup]"
        build_ele.valueListBarresHorBalc.value = build_eleDades.valueListBarresHorBalc.value
        build_ele.SelectorTDHorSupBalc.ValueList = "[str(value) for value in valueListBarresHorBalc]"
        build_ele.SelectorTDHorInfBalc.ValueList = "[str(value) for value in valueListBarresHorBalc]"

        build_ele.SelectorLiniaInf.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerInf.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaSup.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLiniaSup.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaVert.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerVert.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaHor.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerHor.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaRef.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerRef.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"

        build_ele.tipusCavitatTFFVert.ValueList = "40|60"
        build_ele.tipusCavitatTFFHor.ValueList = "40|60"


        build_eleDades.zUnique.value             = build_ele.zUnique.value
        build_eleDades.FlagEntrada.value         = build_ele.FlagEntrada.value
        build_eleDades.inputPoint.value          = build_ele.inputPoint.value
        build_eleDades.llargadaPared.value       = build_ele.llargadaPared.value
        build_eleDades.ampladaPared.value        = build_ele.ampladaPared.value
        build_eleDades.alcadaPared.value         = build_ele.alcadaPared.value
        build_eleDades.listUUIDElements.value    = build_ele.listUUIDElements.value
        build_eleDades.SelectorPPPare.value      = build_ele.SelectorPPPare.value
        build_eleDades.listofPythonChilds.value  = build_ele.listofPythonChilds.value
        build_eleDades.SelectorPPPFill.value     = build_ele.SelectorPPPFill.value
        build_eleDades.NameFilesChildren.value   = build_ele.NameFilesChildren.value


        for property in build_eleDades.get_properties():
            #print(property)
            try:
                #print(build_ele.get_property(str(property.name)))
                #BuildingElement.get_property
                prop = build_ele.get_property(str(property.name))
                if prop != None:
                    #print("name: " + str(property.name))
                    #print("value: " + str(property.value))
                    #print("-----:-------- " )
                    prop.value = property.value
                    #self.build_ele_list[0].set_property(str(property.name), property)
                #build_ele.set_property(str(property.name), property)
                #print(build_ele.get_property(str(property.name)))
            except Exception as e:
                print("Error al guardar valors: " + str(e))

        #self.build_ele_list[0].FlagEntrada.value == 1

        build_ele.FlagEntrada.value = 2

        return build_ele

        #print("")
        #build_ele = build_eleDades


    def set_value_list_stringcombobox_EN(self, build_ele, build_eleDades):

        #build_ele = self.copiar_build_ele(build_eleDades)

        #build_ele.SelectorTubHor.value
        build_ele.listofPythonChilds.value = build_eleDades.listofPythonChilds.value
        build_ele.SelectorPPPFill.ValueList = "[str(value) for value in listofPythonChilds]"

        build_ele.SelectorENH.ValueList = "TD Inferior|TD Superior|Mes Tubs..."
        #build_ele.SelectorTDHInf.ValueList = "Tub|L"
        #build_ele.SelectorTDHSup.ValueList = "Tub|L|Tub + L"

        #build_ele.valueListBarresHorBalcOnlyNum.value = build_eleDades.valueListBarresHorBalcOnlyNum.value
        build_ele.SelectorTDHTotalEN.ValueList = "[str(value) for value in valueListBarresHorBalcOnlyNum]"

        build_ele.IntegerENSelector.value = build_eleDades.IntegerENSelector.value
        build_ele.SelectorENV.ValueList = "['TDVer '+str(value) for value in range(0, IntegerENSelector)]"

        #build_ele.IntegerBalcFinSelector.value = build_eleDades.IntegerBalcFinSelector.value
        #build_ele.SelectorBalcFin.ValueList = "['Balc/Fin '+str(value) for value in range(0, IntegerBalcFinSelector)]"
        build_ele.valueVertListBarresHorInfEN.value = build_eleDades.valueVertListBarresHorInfEN.value
        build_ele.SelectorENHorInf.ValueList = "[str(value) for value in valueVertListBarresHorInfEN]"
        build_ele.valueVertListBarresHorSupEN.value = build_eleDades.valueVertListBarresHorSupEN.value
        build_ele.SelectorENHorSup.ValueList = "[str(value) for value in valueVertListBarresHorSupEN]"
        #build_ele.valueListBarresHorBalc.value = build_eleDades.valueListBarresHorBalc.value
        #build_ele.SelectorTDHorSupBalc.ValueList = "[str(value) for value in valueListBarresHorBalc]"
        #build_ele.SelectorTDHorInfBalc.ValueList = "[str(value) for value in valueListBarresHorBalc]"
        build_ele.AtributPersonTub.ValueList = "EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal"
        build_ele.AtributPersonTubSup.ValueList = "EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal"
        build_ele.AtributPersonTubInf.ValueList = "EXD|LB Complet|LB Curta|Tub Dalt|Tub Baix|L Dalt|LB Llarga|Xapa Frontal|Tub Horitzontal|Tub Frontal"

        build_ele.TubInferior.ValueList = "L|TUB"
        build_ele.TubSuperior.ValueList = "EXD|L|TUB|TUB Interior"

        build_ele.valueListReforcComboBoxEN.value = build_eleDades.valueListReforcComboBoxEN.value
        build_ele.SelectorReforcEN.ValueList = "[str(value) for value in valueListReforcComboBoxEN]"

        build_ele.TipusPortaEN.ValueList = "Porta 1|Corredissa"

        build_ele.valueListBarresHorBalcEN.value = build_eleDades.valueListBarresHorBalcEN.value
        build_ele.SelectorENHorSupBalcCorredisa.ValueList = "[str(value) for value in valueListBarresHorBalcEN]"

        build_ele.valueListBarresComboBox.value = build_eleDades.valueListBarresComboBox.value
        build_ele.SelectorTDHorCorred1.ValueList = "[str(value) for value in valueListBarresComboBox]"
        build_ele.SelectorTDHorCorred2.ValueList = "[str(value) for value in valueListBarresComboBox]"
        build_ele.SelectorTDHorCorred3.ValueList = "[str(value) for value in valueListBarresComboBox]"

        build_ele.SelectorTDHorSupBalcEN.ValueList = "[str(value) for value in valueListBarresHorBalcEN]"
        build_ele.SelectorTDHorInfBalcEN.ValueList = "[str(value) for value in valueListBarresHorBalcEN]"

        build_ele.SelectorREFInfBalcEN.ValueList = "[str(value) for value in valueListReforcComboBoxEN]"
        build_ele.SelectorTDHorEsqBalcEN.ValueList = "[str(value) for value in valueListBarresComboBox]"
        build_ele.SelectorTDHorDreBalcEN.ValueList = "[str(value) for value in valueListBarresComboBox]"

        build_ele.SelectorLiniaInf.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerInfEN.ValueList = "EN_FIXACIO_X|EN_FIXACIO_Y"
        build_ele.SelectorLiniaSup.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerSupEN.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaVert.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerVertEN.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"
        build_ele.SelectorLiniaHor.ValueList = "Tipus 1|Tipus 2"
        build_ele.SelectorLayerHorEN.ValueList = "TD_FIXACIO|TD_NO_CARAGOLAR"



        build_eleDades.zUnique.value             = build_ele.zUnique.value
        build_eleDades.FlagEntrada.value         = build_ele.FlagEntrada.value
        build_eleDades.inputPoint.value          = build_ele.inputPoint.value
        build_eleDades.llargadaPared.value       = build_ele.llargadaPared.value
        build_eleDades.ampladaPared.value        = build_ele.ampladaPared.value
        build_eleDades.alcadaPared.value         = build_ele.alcadaPared.value
        build_eleDades.listUUIDElements.value    = build_ele.listUUIDElements.value
        build_eleDades.SelectorPPPare.value      = build_ele.SelectorPPPare.value
        build_eleDades.listofPythonChilds.value  = build_ele.listofPythonChilds.value
        build_eleDades.SelectorPPPFill.value     = build_ele.SelectorPPPFill.value
        build_eleDades.NameFilesChildren.value   = build_ele.NameFilesChildren.value


        for property in build_eleDades.get_properties():
            try:
                prop = build_ele.get_property(str(property.name))
                if prop != None:
                    prop.value = property.value
            except Exception as e:
                print("Error al guardar valors: " + str(e))


        build_ele.FlagEntrada.value = 2

        return build_ele

    def delete_anterior(self,
                     build_ele: BuildingElement,
                     doc      : AllplanElementAdapter.DocumentAdapter,
                     listTubs = []):
        """ print the attributes

        Args:
            build_ele: building element with the parameter properties
            doc:       document of the Allplan drawing files
        """

        attr_manager = AllplanBaseElements.AttributeDataManager

        read_state = AllplanBaseElements.eAttibuteReadState.values[0]


        listNames = []
        for name in listTubs:
            listNames.append(get_file_name(name) )



        listDocumnets = AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
        ##documName = AllplanElementAdapter.DocumentNameService.GetDocumentNameByFileIndex(listDocumnets[docValue][1], True, True, "TEST")
        docDrawingFile = AllplanBaseElements.DrawingFileService()
        docAdapter = AllplanElementAdapter.DocumentAdapter()
        elemtsToDelete =  AllplanElementAdapter.BaseElementAdapterList()

        for docValue in range(0,len(listDocumnets)):
            #docDrawingFile = AllplanBaseElements.DrawingFileService()
            #docAdapter = AllplanElementAdapter.DocumentAdapter()
            #doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[docValue][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

            #doc = DocumentManager.get_instance().document
            doc = docDrawingFile.LoadFile(docAdapter, listDocumnets[docValue][1], AllplanBaseElements.DrawingFileLoadState.ActiveForeground)

            doc = DocumentManager.get_instance().document
            for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
                n = 0
                trobat = False
                while n < len(listTubs) :#:and not trobat :
                    elemUUID = element.GetElementUUID()
                    if str(element.GetElementUUID()) == listTubs[n]:
                        #AllplanBaseElements.DeleteElements(doc= doc, elements = [element] )
                        #elem = element.FromGUID(element.GetModelElementUUID(), doc)

                        #if element.GetDocument() == doc:
                        elemtsToDelete.append(element)
                        trobat = True
                        #AllplanBaseElements.DeleteElements(doc= doc, elements= elemtsToDelete)
                    n += 1


            AllplanBaseElements.DeleteElements(doc= doc, elements= elemtsToDelete)







class Object3DFilter():
    """
    Filtro para seleccionar únicamente elementos 3D en Allplan.

    Esta clase implementa un filtro callable que puede ser utilizado para filtrar elementos
    y trabajar solo con aquellos que sean objetos 3D.

    Metodos:
        - __call__(element): Devuelve True si el elemento es 3D, False en caso contrario.
    """

    def __call__(self, element: AllplanElementAdapter.BaseElementAdapter):
        """ execute the filtering

        Args:
            element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

        return element.Is3DElement()



