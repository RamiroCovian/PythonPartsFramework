"""
Script for EN_conjunt - Vertical - Group
"""
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import collections
import math
import random
import ctypes

import BuildingElementValueUtil
#from pynput.mouse import Listener
from typing import List, Any, Optional

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil

from DocumentManager import DocumentManager
#from BuildingElementInputService import BuildingElementInputService
from typing import List
from AnyValueByType import AnyValueByType
from .EN_Horitzontal_Inf_PP import PP_EN_Horitzontal_Inf
from .EN_Horitzontal_Sup_PP import PP_EN_Horitzontal_Sup
from .EN_Horitzontal_reforc import PP_EN_Horitzontal_reforc
from .EN_Vertical_PP import PP_EN_Vertical
from .EN_Horitzontal_PP import PP_EN_Horitzontal
from .EN_Inclinat_PP import PP_EN_Inclinat
from .EN_Premarc import PP_EN_Premarc
from .EN_Horitzontal_Front import EN_Horitzontal_Front
from .EN_liniaInterior import LiniaInterior
from .EN_CreateText import TextSpline

from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from HandleProperties import HandleProperties
from HandleDirection import HandleDirection
from CreateElementResult import CreateElementResult
from Utils import LibraryBitmapPreview




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
    del build_ele
    #opcionsTD = build_ele.opcionsTD.value
    del version

    # Support all versions
    return True



def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

    #print("------------------------------------------------------------------------------------")
    #print(handle_prop)
    #print(input_pnt)
    #print("------------------------------------------------------------------------------------")

    build_ele.change_property(handle_prop, input_pnt)

    #with Listener() as listener:
    #    listener.join()
    '''
    if build_ele.ReduirTempsCarrega.value:
        if build_ele.intervalTempsCarrega.value != 20:
            build_ele.intervalTempsCarrega.value += 1
        else:
            build_ele.intervalTempsCarrega.value = 0
            return create_element(build_ele, doc)
    else:
        return create_element(build_ele, doc)
    '''
    if build_ele.PointXTempsCarrega.value == input_pnt.X and build_ele.PointYTempsCarrega.value == input_pnt.Y and build_ele.PointZTempsCarrega.value == input_pnt.Z :
        return create_element(build_ele, doc)

    build_ele.PointXTempsCarrega.value = input_pnt.X
    build_ele.PointYTempsCarrega.value = input_pnt.Y
    build_ele.PointZTempsCarrega.value = input_pnt.Z


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

def on_control_event(build_ele, event_id: int):
    nVer = 0
    lennVer = len(build_ele.SelectorENV.value)
    nVerS = build_ele.SelectorENV.value[lennVer-1:]

    if len(build_ele.SelectorENV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorENV.value[6]
        nVer2 = int(nVerS2)
        nVer = nVer2 *10 + nVer
    else:
        if nVerS != 'r':
            nVer = int(nVerS)
    if event_id == 1000:
        guardar_valors_inici(build_ele,nVer)
    elif event_id == 1001:
        #mostrar valors actual TDV
        copiar_valors_Vert(build_ele,nVer)
        #ShowMessageBox("S'han Copiat les dades de la Barra Vertical " + str(nVer), 1001)
        ctypes.windll.user32.MessageBoxW(0, "S'han Copiat les dades de la Barra Vertical "+ str(nVer), "Alerta", 0)
    elif event_id == 1002:
        #mostrar valors actual TDV
        if not pegar_valors_Vert(build_ele,nVer):
            print("no s'ha pegat correctament, torna-ho a intentar")
            ctypes.windll.user32.MessageBoxW(0, "No s'ha pegat correctament, torna-ho a intentar ", 0)

        else:
            ctypes.windll.user32.MessageBoxW(0, "S'han Pegat les dades de la Barra Vertical " + str(build_ele.DadesVertCopy.value[0].nBarraGuardada) + " a la Barra " + str(nVer), 6)

        mostrar_valors_actuals(build_ele, nVer)
    elif event_id == 1003:
        build_ele.UpdateBalconeraFinestraEN.value = True
    doc = DocumentManager.get_instance().document
    create_element(build_ele, doc)

def on_cancel_function(self) -> bool:
    """ Called when ESC key is pressed.

    Returns:
        True when the PythonPart framework should terminate the PythonPart, False otherwise.
    """

    build_ele = self.build_ele

    #recorrer buscant algun edit
    set_all_edit_to_false(self.build_ele)

    #mostrar valors actual TDV
    nVer = 0
    lennVer = len(build_ele.SelectorENV.value)
    nVerS = build_ele.SelectorENV.value[lennVer-1:]

    if len(build_ele.SelectorENV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorENV.value[6]
        nVer2 = int(nVerS2)
        nVer = nVer2 *10 + nVer
    else:
        if nVerS != 'r':
            nVer = int(nVerS)
    mostrar_valors_actuals(self.build_ele, nVer)

    #guardar valors_actuals
    guardar_valors_actuals(self.build_ele, nVer)

    print("ESC pressed")
    if self.modification_mode:
        AllplanBaseElements.DrawingService.ResetAndDrawHiddenElement(self.coord_input.GetInputViewDocument(),
                                                                DocumentManager.get_instance().pythonpart_element)
    print("ESC pressed and saved")
    return True


def compare_attributes(build_ele: BuildingElement,
                     doc      : AllplanElementAdapter.DocumentAdapter,
                     tub):
    """ print the attributes

    Args:
        build_ele: building element with the parameter properties
        doc:       document of the Allplan drawing files
    """

    attr_manager = AllplanBaseElements.AttributeDataManager

    read_state = AllplanBaseElements.eAttibuteReadState.values[0]


    for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
        if not (attributes := AllplanBaseElements.ElementsAttributeService.GetAttributes(element, read_state)):
            continue

        max_name_len = 0

        #for attr_id, _ in attributes:
        #    max_name_len = max(max_name_len, len(attr_manager.GetAttributeName(attr_id)))

        printed = False

        max_name_len += 2
        esIgual, DEN = tub_es_igual(tub, attributes)
        if esIgual:
            return True, DEN

    return False, "T"

    #PythonUtility.ShowMessageBox("The attribute log is shown in the Trace window", PythonUtility.MB_OK)

def tub_es_igual(horitzontalPP, attributes):

    att_A = att_B = att_C = att_D = att_A_INV = att_B_INV = att_C_INV = att_D_INV = att_pota_inv = att_pestanyes = att_cancam = att_mesures = att_pota = att_seccio = ""
    att_A1 = att_A2 = att_B1 = att_B2 = att_C1 = att_C2 = att_D1 = att_D2 = att_A_INV1 = att_A_INV2 = att_B_INV1 = att_B_INV2 = att_C_INV1 = att_C_INV2 = att_D_INV1 = att_D_INV2 = "#"
    #att_llargada = 0
    DEN = "T"
    for attr_id, value in attributes:
        attr_name = AllplanBaseElements.AttributeDataManager.GetAttributeName(attr_id)

        if attr_id == 2108:
            att_A = value
        elif attr_id == 2494:
            att_A1 = value
        elif attr_id == 2495:
            att_A2 = value
        elif attr_id == 2047:
            att_B = value
        elif attr_id == 2496:
            att_B1 = value
        elif attr_id == 2497:
            att_B2 = value
        elif attr_id == 2110:
            att_C = value
        elif attr_id == 2498:
            att_C1 = value
        elif attr_id == 2499:
            att_C2 = value
        elif attr_id == 2120:
            att_D = value
        elif attr_id == 2500:
            att_D1 = value
        elif attr_id == 2501:
            att_D2 = value
        elif attr_id == 2121:
            att_A_INV = value
        elif attr_id == 2502:
            att_A_INV1 = value
        elif attr_id == 2503:
            att_A_INV2 = value
        elif attr_id == 2122:
            att_B_INV = value
        elif attr_id == 2504:
            att_B_INV1 = value
        elif attr_id == 2505:
            att_B_INV2 = value
        elif attr_id == 2128:
            att_C_INV = value
        elif attr_id == 2506:
            att_C_INV1 = value
        elif attr_id == 2507:
            att_C_INV2 = value
        elif attr_id == 2129:
            att_D_INV = value
        elif attr_id == 2508:
            att_D_INV1 = value
        elif attr_id == 2509:
            att_D_INV2 = value
        elif attr_id == 2446:
            att_pota_inv = value
        elif attr_id == 2430:
            att_pestanyes = value
        elif attr_id == 2435:
            att_cancam = value
        elif attr_id == 2431:
            att_mesures = value
        elif attr_id == 2433:
            att_pota = value
        elif attr_id == 2445:
            att_seccio = value
        elif attr_id == 1083:
            DEN = value


    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d_inv()) )

    caresiguals = False
    if att_A == cara_a and att_A1 == cara_a1 and att_A2 == cara_a2 and att_B == cara_b and att_B1 == cara_b1 and att_B2 == cara_b2 and att_C == cara_c and att_C1 == cara_c1 and att_C2 == cara_c2 and att_D == cara_d and att_D1 == cara_d1 and att_D2 == cara_d2 and att_A_INV == cara_e and att_A_INV1 == cara_e1 and att_A_INV2 == cara_e2 and att_B_INV == cara_f and att_B_INV1 == cara_f1 and att_B_INV2 == cara_f2 and att_C_INV == cara_g and att_C_INV1 == cara_g1 and att_C_INV2 == cara_g2 and att_D_INV == cara_h and att_D_INV1 == cara_h1 and att_D_INV2 == cara_h2 :
        caresiguals = True
    if horitzontalPP.get_codi_cara_a()[:254] == att_A  and horitzontalPP.get_codi_cara_b()[:254] == att_B and horitzontalPP.get_codi_cara_c()[:254] == att_C and horitzontalPP.get_codi_cara_d()[:254] == att_D and horitzontalPP.get_codi_cara_a_inv()[:254] == att_A_INV and horitzontalPP.get_codi_cara_b_inv()[:254] == att_B_INV and horitzontalPP.get_codi_cara_c_inv()[:254] == att_C_INV and horitzontalPP.get_codi_cara_d_inv()[:254] == att_D_INV:
        caresiguals = True

    if caresiguals and horitzontalPP.get_codi_pota_inv() == att_pota_inv and horitzontalPP.get_codi_pestanyes() == att_pestanyes and horitzontalPP.get_codi_cancam() == att_cancam and horitzontalPP.get_codi_mesures() == att_mesures and horitzontalPP.get_codi_pota() == att_pota and horitzontalPP.get_seccio() == att_seccio :
        #print("att_A: "         + str(att_A) +           " _ " + str(horitzontalPP.get_codi_cara_a())     + " = " +  str(horitzontalPP.get_codi_cara_a() == att_A))
        #print("att_B: "           + str(att_B) +         " _ " + str(horitzontalPP.get_codi_cara_b())     + " = " +  str(horitzontalPP.get_codi_cara_b() == att_B))
        #print("att_C: "           + str(att_C) +         " _ " + str(horitzontalPP.get_codi_cara_c())     + " = " +  str(horitzontalPP.get_codi_cara_c() == att_C))
        #print("att_D: "           + str(att_D) +         " _ " + str(horitzontalPP.get_codi_cara_d())     + " = " +  str(horitzontalPP.get_codi_cara_d() == att_D))
        #print("att_A_INV: "       + str(att_A_INV) +     " _ " + str(horitzontalPP.get_codi_cara_a_inv()) + " = " +  str(horitzontalPP.get_codi_cara_a_inv() == att_A_INV))
        #print("att_B_INV: "       + str(att_B_INV) +     " _ " + str(horitzontalPP.get_codi_cara_b_inv()) + " = " +  str(horitzontalPP.get_codi_cara_b_inv() == att_B_INV))
        #print("att_C_INV: "       + str(att_C_INV) +     " _ " + str(horitzontalPP.get_codi_cara_c_inv()) + " = " +  str(horitzontalPP.get_codi_cara_c_inv() == att_C_INV))
        #print("att_D_INV: "       + str(att_D_INV) +     " _ " + str(horitzontalPP.get_codi_cara_d_inv()) + " = " +  str(horitzontalPP.get_codi_cara_d_inv() == att_D_INV))
        #print("att_pota_inv: "    + str(att_pota_inv) +  " _ " + str(horitzontalPP.get_codi_pota_inv() )  + " = " +  str(horitzontalPP.get_codi_pota_inv() == att_pota_inv))
        #print("att_pestanyes: "   + str(att_pestanyes) + " _ " + str(horitzontalPP.get_codi_pestanyes())  + " = " +  str(horitzontalPP.get_codi_pestanyes() == att_pestanyes))
        #print("att_cancam: "      + str(att_cancam) +    " _ " + str(horitzontalPP.get_codi_cancam() )    + " = " +  str(horitzontalPP.get_codi_cancam() == att_cancam))
        #print("att_mesures: "     + str(att_mesures) +   " _ " + str(horitzontalPP.get_codi_mesures())    + " = " +  str(horitzontalPP.get_codi_mesures() == att_mesures))
        #print("att_pota: "        + str(att_pota) +      " _ " + str(horitzontalPP.get_codi_pota() )      + " = " +  str(horitzontalPP.get_codi_pota() == att_pota))
        #print("att_seccio: "      + str(att_seccio) +    " _ " + str(horitzontalPP.get_seccio() )         + " = " +  str(horitzontalPP.get_seccio() == att_seccio))
        #print("att_llargada: "    + str(att_llargada) +  " _ " +  str(horitzontalPP.get_llargada() == att_llargada) + " _ " + str(horitzontalPP.get_llargada()))
        return True, DEN
    return False, DEN


'''
def initialize_control_properties(build_ele     : BuildingElement,
                                  ctrl_prop_util: ControlPropertiesUtil,
                                  doc           : AllplanElementAdapter.DocumentAdapter) -> None:
    """ initialize the control properties

    Args:
        build_ele     : building element
        ctrl_prop_util: control properties
        doc           : document
    """

    modify_control_properties(build_ele, ctrl_prop_util, "", 2001, doc)


def modify_control_properties(build_ele     : BuildingElement,
                              ctrl_prop_util: ControlPropertiesUtil,
                              _value_name   : str,
                              event_id      : int,
                              _doc          : AllplanElementAdapter.DocumentAdapter) -> bool:
    """ modify the control properties

    Args:
        build_ele     : building element
        ctrl_prop_util: control properties
        _value_name   : name of the modified value
        event_id      : event ID
        doc           : document

    Returns:
        update the property palette
    """

    if event_id == 2001:
        #ctrl_prop_util.set_text("FileTest", build_ele.FileTest.value)
        ctrl_prop_util.build_ele_list[0].FileTest.value = "valor modificat"
        #print(ctrl_prop_util.build_ele_list[0].BarresHorListToShowEN.valuelist)

        return True



    return True
'''

def create_element(build_ele, doc):

    result = create_element_class(build_ele, doc)
    #model_elem_list = result["model_elem_list"]
    model_elem_list = result["elements"]
    handle_list = result["handles"]
    model_elem_list_preview = result["preview_elements"]
    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview)
                                #preview_elements=   model_elem_list_preview)

def create_element_class(build_ele, doc, placement_mat = AllplanGeo.Matrix3D()): # type: ignore
    """
    Create horitzontalPPInf element

    Args:
        build_ele: the building element.
        doc:       input document
    """

    build_ele.zUnique.value = random.random() * 3600

    '''
    Attr_state = AllplanBaseElements.eAttibuteReadState.ReadAll

    CreateElementResult(LibraryBitmapPreview.create_libary_bitmap_preview( \
                                    AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() +
                                    r"Examples\PythonParts\ServiceExamples\ElementsAttributeService.png"))


    attr_list = [(attribute.attribute_id, attribute.value) for attribute in build_ele.ElementAttributes.value if attribute.attribute_id]

    AllplanBaseElements.ElementsAttributeService.ChangeAttributes(attr_list, AllplanBaseElements.ElementsSelectService.SelectAllElements(doc))
    '''
    #del doc
    #drawingService = AllplanBaseElements.DrawingFileService()
    #print("zUnique: " + str(build_ele.zUnique.value))
    #print("AttributeID:" + str(build_ele.AttributeID.value))

    crearLlistaVerticals(build_ele)
    crearLlistaReforc(build_ele)
    crearLlistaHoritzontals(build_ele)
    crearLlistaFullHoritzontals(build_ele)

    # Definir nListEncaixVert
    update_mat_nListVert(build_ele)

    #definir els valors inicials i borrar els valors que sobren
    if build_ele.EncaixVertList.value == [] or len(build_ele.EncaixVertList.value) <= build_ele.LengthListEncaixVert.value:
        set_values(build_ele, build_ele.LengthListEncaixVert.value)
    if build_ele.LengthListEncaixVert.value < len(build_ele.EncaixVertList.value):
        remove_values(build_ele, build_ele.LengthListEncaixVert.value)

    nVer = 0
    lennVer = len(build_ele.SelectorENV.value)
    nVerS = build_ele.SelectorENV.value[lennVer-1:]
    if len(build_ele.SelectorENV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorENV.value[6]
        nVer2 = int(nVerS2)
        nVer = nVer2 *10 + nVer
    else:
        if nVerS != 'r':
            nVer = int(nVerS)


    nRef = 0
    if getNumFromText(build_ele, build_ele.SelectorReforcEN.value, 7) != "":
        nRef = getNumFromText(build_ele, build_ele.SelectorReforcEN.value, 7)


    group_elems = [] #All elements of suite
    group_elems_preview = [] #All elements of suite
    handle_list = []

    mostrarActual = ""
    if build_ele.SelectorPPEN.value == 1 and build_ele.SelectorENH.value == "EN Inferior":
        mostrarActual = "ENHINF"
    elif build_ele.SelectorPPEN.value == 1 and build_ele.SelectorENH.value == "EN Superior":
        mostrarActual = "ENHSUP"
    elif build_ele.SelectorPPEN.value == 1 and build_ele.SelectorENH.value == "Mes Tubs...":
        mostrarActual = "ENHInt"
    elif build_ele.SelectorPPEN.value == 2:
        if build_ele.SelectorPPAnt.value != 2 and build_ele.SelectorPPEN.value == 2:
            mostrar_valors_actuals(build_ele, nVer)
        mostrarActual = "ENV"+str(nVer)
    elif build_ele.SelectorPPEN.value == 4:
        mostrarActual = "ENR"+str(nRef)
    elif build_ele.SelectorPPEN.value == 3:
        nBalcFin = 0
        lenBalcFin = len(build_ele.SelectorBalcFinEN.value)
        nBalcFinS = build_ele.SelectorBalcFinEN.value[lenBalcFin-1:]
        if len(build_ele.SelectorBalcFinEN.value) >= 10:
            nBalcFin = int(nBalcFinS)
            nBalcFinS2 = build_ele.SelectorBalcFinEN.value[-2]
            nBalcFin2 = int(nBalcFinS2)
            nBalcFin = nBalcFin2 *10 + nBalcFin
        else:
            if nBalcFinS != ' ' and nBalcFinS != 'n' and nBalcFinS != 'r':
                nBalcFin = int(nBalcFinS)

        if build_ele.SelectorBalcFinAnt.value != nBalcFin:
            mostrar_BalcFine(build_ele, nBalcFin)
        else:
            guardar_valors_BalcFine(build_ele, nBalcFin)
        mostrarActual = "ENBalconeraFinestra"+str(nBalcFin)
        handle_list = create_handles_balconeresFinestres(build_ele)

        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0 , build_ele.PosicioZBalconeraEN.value)
        lineX = create_polyline_interior(build_ele, 0, 0, build_ele.AmpleBalconeraEN.value, True, pointUbi)
        if lineX != []:
            #group_elems.append(lineX[0])
            group_elems_preview.append(lineX[0])
            group_elems_preview.append(lineX[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))

        lineZ = create_polyline_interior(build_ele, 0,0,build_ele.LlargadaBalconeraEN.value, False, pointUbi)
        if lineZ != []:
            #group_elems.append(lineZ[0])
            group_elems_preview.append(lineZ[0])
            group_elems_preview.append(lineZ[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0 , build_ele.PosicioZBalconeraEN.value + build_ele.LlargadaBalconeraEN.value)
        lineX = create_polyline_interior(build_ele, 0, 0, build_ele.AmpleBalconeraEN.value, True, pointUbi)
        if lineX != []:
            #group_elems.append(lineX[0])
            group_elems_preview.append(lineX[0])
            group_elems_preview.append(lineX[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value + build_ele.AmpleBalconeraEN.value, 0 , build_ele.PosicioZBalconeraEN.value)
        lineZ = create_polyline_interior(build_ele, 0,0,build_ele.LlargadaBalconeraEN.value, False, pointUbi)
        if lineZ != []:
            #group_elems.append(lineZ[0])
            group_elems_preview.append(lineZ[0])
            group_elems_preview.append(lineZ[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))

        if build_ele.UpdateBalconeraFinestraEN.value:

            trobatAnt, posBarraAntBalcFines = buscar_anterior_mes_proper(build_ele, build_ele.PosicioXBalconeraEN.value)
            trobatSeg, posBarraSegBalcFines = buscar_seguent_mes_proper(build_ele, build_ele.PosicioXBalconeraEN.value + build_ele.AmpleBalconeraEN.value)

            if build_ele.VerticalAutoBalcEN.value:
                build_ele.SelectorTDHorEsqBalcEN.value = "Tub " + str(posBarraAntBalcFines)
                build_ele.SelectorTDHorDreBalcEN.value = "Tub  " + str(posBarraSegBalcFines)
            else:
                if getNumFromText(build_ele, build_ele.SelectorTDHorEsqBalcEN.value, 3) != "":
                    posBarraAntBalcFines = getNumFromText(build_ele, build_ele.SelectorTDHorEsqBalcEN.value, 3)
                if getNumFromText(build_ele, build_ele.SelectorTDHorDreBalcEN.value, 3) != "":
                    posBarraSegBalcFines = getNumFromText(build_ele, build_ele.SelectorTDHorDreBalcEN.value, 3)

                if posBarraSegBalcFines > posBarraAntBalcFines:
                    trobatSeg = True
                    trobatAnt = True
                else:
                    trobatSeg = False
                    trobatAnt = False


            nHorSup=0
            if getNumFromText(build_ele, build_ele.SelectorTDHorSupBalcEN.value, 3) != "":
                nHorSup = getNumFromText(build_ele, build_ele.SelectorTDHorSupBalcEN.value, 3)
            if getNumFromText(build_ele, build_ele.SelectorTDHorInfBalcEN.value, 3) != "":
                nHorInf = getNumFromText(build_ele, build_ele.SelectorTDHorInfBalcEN.value, 3)

            if not trobatAnt:
                posBarraAntBalcFines = 0

            if not trobatSeg:
                posBarraSegBalcFines = build_ele.IntegerENSelector.value-1
            #if trobatAnt and trobatSeg:

            posInfBalcFine = build_ele.SelectorTDHorSupBalcEN.value
            posSupBalcFine = build_ele.SelectorTDHorInfBalcEN.value


                #else:
                #    nHorInf = 0

            if build_ele.SelectorTDHorInfBalcEN.value != "EN Inferior" and build_ele.SelectorTDHorInfBalcEN.value != "EN Superior":
                build_ele.BarresHorListEN.value[nHorInf] = build_ele.BarresHorListEN.value[nHorInf]._replace(BarraHor = True)
                #build_ele.BarresHorListEN.value[nHorInf] = build_ele.BarresHorListEN.value[nHorInf]._replace(Posicio = build_ele.PosicioZBalconeraEN.value - 80 - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2)
                build_ele.BarresHorListEN.value[nHorInf] = build_ele.BarresHorListEN.value[nHorInf]._replace(Posicio = build_ele.PosicioZBalconeraEN.value - 5 - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2 )
                build_ele.BarresHorListEN.value[nHorInf] = build_ele.BarresHorListEN.value[nHorInf]._replace(BarraInici = "Tub "+str(posBarraAntBalcFines))
                build_ele.BarresHorListEN.value[nHorInf] = build_ele.BarresHorListEN.value[nHorInf]._replace(BarraFinal = "Tub "+str(posBarraSegBalcFines))

            if build_ele.SelectorTDHorSupBalcEN.value != "EN Superior" and build_ele.SelectorTDHorSupBalcEN.value != "EN Inferior":
                if build_ele.TipusPortaEN.value == 'Corredissa':
                    build_ele.dadesTDHortInterEN.value[nHorSup] = build_ele.dadesTDHortInterEN.value[nHorSup]._replace(Altura = 30 )
                    build_ele.dadesTDHortInterEN.value[nHorSup] = build_ele.dadesTDHortInterEN.value[nHorSup]._replace(Ample = 70 )
                build_ele.BarresHorListEN.value[nHorSup] = build_ele.BarresHorListEN.value[nHorSup]._replace(BarraHor = True)
                #build_ele.BarresHorListEN.value[nHorSup] = build_ele.BarresHorListEN.value[nHorSup]._replace(Posicio = build_ele.PosicioZBalconeraEN.value + build_ele.LlargadaBalconeraEN.value + 80 + build_ele.dadesTDHortInterEN.value[nHorSup].Altura/2)
                build_ele.BarresHorListEN.value[nHorSup] = build_ele.BarresHorListEN.value[nHorSup]._replace(Posicio = build_ele.PosicioZBalconeraEN.value + build_ele.LlargadaBalconeraEN.value + 5 -build_ele.BarraAlturaInf.value)#+ build_ele.dadesTDHortInterEN.value[nHorSup].Altura/2)
                build_ele.BarresHorListEN.value[nHorSup] = build_ele.BarresHorListEN.value[nHorSup]._replace(BarraInici = "Tub "+str(posBarraAntBalcFines))
                build_ele.BarresHorListEN.value[nHorSup] = build_ele.BarresHorListEN.value[nHorSup]._replace(BarraFinal = "Tub "+str(posBarraSegBalcFines))
            nHorSup2 = "EN Superior"
            if build_ele.TipusPortaEN.value == 'Corredissa':
                if getNumFromText(build_ele, build_ele.SelectorTDHorSupBalcCorredisa.value, 3) != "":
                    nHorSup2 = getNumFromText(build_ele, build_ele.SelectorTDHorSupBalcCorredisa.value, 3)
                if build_ele.SelectorTDHorSupBalcCorredisa.value != "EN Inferior" and build_ele.SelectorTDHorSupBalcCorredisa.value != "EN Superior":
                    build_ele.BarresHorListEN.value[nHorSup2] = build_ele.BarresHorListEN.value[nHorSup2]._replace(BarraHor = True)
                    build_ele.dadesTDHortInterEN.value[nHorSup2] = build_ele.dadesTDHortInterEN.value[nHorSup2]._replace(Altura = 30 )
                    build_ele.dadesTDHortInterEN.value[nHorSup2] = build_ele.dadesTDHortInterEN.value[nHorSup2]._replace(Ample = 70 )
                    #build_ele.BarresHorListEN.value[nHorSup2] = build_ele.BarresHorListEN.value[nHorSup2]._replace(Posicio = build_ele.PosicioZBalconeraEN.value + build_ele.LlargadaBalconeraEN.value + 6 + 30 + 280 )
                    build_ele.BarresHorListEN.value[nHorSup2] = build_ele.BarresHorListEN.value[nHorSup2]._replace(Posicio = build_ele.BarresHorListEN.value[nHorSup].Posicio + build_ele.dadesTDHortInterEN.value[nHorSup].Altura + 280 )
                    build_ele.BarresHorListEN.value[nHorSup2] = build_ele.BarresHorListEN.value[nHorSup2]._replace(BarraInici = "Tub "+str(posBarraAntBalcFines))
                    build_ele.BarresHorListEN.value[nHorSup2] = build_ele.BarresHorListEN.value[nHorSup2]._replace(BarraFinal = "Tub "+str(posBarraSegBalcFines))
            #else:
                #nHorSup = build_ele.desplZS.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value/2
            if nVer != posBarraAntBalcFines:
                if posBarraAntBalcFines != 0:
                    #build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value - 80 - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple)
                    #build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value - 5 - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple)
                    #build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs +  build_ele.dadesTDVertEN.value[0].BarraAmple + (build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2)
                    build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - 5)
                build_ele.dadesTDVertEN.value[posBarraAntBalcFines] = build_ele.dadesTDVertEN.value[posBarraAntBalcFines]._replace(MostrarTDVertical = True)
            else:
                build_ele.dadesTDVertEN.value[posBarraAntBalcFines] = build_ele.dadesTDVertEN.value[posBarraAntBalcFines]._replace(MostrarTDVertical = True)
                if posBarraAntBalcFines != 0:
                    #build_ele.desplXVertAbs.value = build_ele.PosicioXBalconeraEN.value - 80 - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple
                    #build_ele.desplXVertAbs.value = build_ele.PosicioXBalconeraEN.value  - 5 - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple
                    build_ele.desplXVertAbs.value =build_ele.PosicioXBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple  - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - 5
            if nVer != posBarraSegBalcFines:
                if posBarraSegBalcFines != build_ele.IntegerENSelector.value-1:
                    #build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value )#+ 80 )#+ build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2)
                    build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple   )
                    #build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines] = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value - build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple)
                build_ele.dadesTDVertEN.value[posBarraSegBalcFines] = build_ele.dadesTDVertEN.value[posBarraSegBalcFines]._replace(MostrarTDVertical = True)
            else:
                if posBarraSegBalcFines != build_ele.IntegerENSelector.value-1:
                    build_ele.dadesTDVertEN.value[posBarraSegBalcFines] = build_ele.dadesTDVertEN.value[posBarraSegBalcFines]._replace(MostrarTDVertical = True)
                #build_ele.desplXVertAbs.value = build_ele.PosicioXBalconeraEN.value + build_ele.AmpleBalconeraEN.value + 80 #+ build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2
                #build_ele.desplXVertAbs.value = build_ele.PosicioXBalconeraEN.value + build_ele.AmpleBalconeraEN.value + 5 #+ build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2
                build_ele.desplXVertAbs.value = build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple #+ build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2

            if build_ele.TipusPortaEN.value == 'Corredissa':


                for i in range(0,3):
                    nHor1 = 0
                    desplIntCorr = 0
                    if i == 0:
                        desplIntCorr = 510
                        if getNumFromText(build_ele, build_ele.SelectorTDHorCorred1.value, 3) != "":
                            nHor1 = getNumFromText(build_ele, build_ele.SelectorTDHorCorred1.value, 3)
                    elif i == 1:
                        desplIntCorr = 510 + 30 + 640
                        if getNumFromText(build_ele, build_ele.SelectorTDHorCorred2.value, 3) != "":
                            nHor1 = getNumFromText(build_ele, build_ele.SelectorTDHorCorred2.value, 3)
                    else:
                        desplIntCorr = 510 + 30 + 640 + 30 +370
                        if getNumFromText(build_ele, build_ele.SelectorTDHorCorred3.value, 3) != "":
                            nHor1 = getNumFromText(build_ele, build_ele.SelectorTDHorCorred3.value, 3)
                    posBarraCorred1 = nHor1
                    if nVer != posBarraCorred1:
                        if posBarraCorred1 != 0:
                            build_ele.listDesplVerticalsEN.value[posBarraCorred1] = build_ele.listDesplVerticalsEN.value[posBarraCorred1]._replace(desplXAbs = build_ele.PosicioXBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple  + desplIntCorr - 5 )
                        if build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value > build_ele.listDesplVerticalsEN.value[posBarraCorred1].desplXAbs:
                            build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(MostrarTDVertical = True)
                        else:
                            build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(MostrarTDVertical = False)
                    else:
                        if posBarraCorred1 != 0:
                            build_ele.desplXVertAbs.value =build_ele.PosicioXBalconeraEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple + desplIntCorr - 5
                        if build_ele.PosicioXBalconeraEN.value + 5 + build_ele.AmpleBalconeraEN.value > build_ele.desplXVertAbs.value:
                            build_ele.MostrarENVertical.value = True
                            build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(MostrarTDVertical = True)
                        else:
                            build_ele.MostrarENVertical.value = False
                            build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(MostrarTDVertical = False)
                    build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(BarraInferior = "Tub "+ str(nHorSup))
                    build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(BarraAmple = 30)
                    build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(BarraAltura = 70)
                    build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(FemellaSup = True)
                    build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(FemellaInf = True)
                    if nHorSup2 == "EN Superior":
                        build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(BarraSuperior = str(nHorSup2))
                    else:
                        build_ele.dadesTDVertEN.value[posBarraCorred1] = build_ele.dadesTDVertEN.value[posBarraCorred1]._replace(BarraSuperior = "Tub "+ str(nHorSup2))



            #if not trobatAnt:
            #    print("No hi ha barra Anterior, recoloca la balconera / finestra")
            #    ctypes.windll.user32.MessageBoxW(0, "No hi ha barra Anterior, recoloca la balconera / finestra " , 1)



            #if not trobatSeg:
            #    print("No hi ha barra Seguent, recoloca la balconera / finestra")
            #    ctypes.windll.user32.MessageBoxW(0, "No hi ha barra Seguent, recoloca la balconera / finestra " , 1)


            build_ele.nBarresTDHoritzontalInf.value = 2
            if len(build_ele.listDesplHoritzontalsInfEN.value) < 2:
                add_baraInferior(build_ele, 2)
            #inferior multiple
            build_ele.SepararTDHoritzontalInf.value = True
            #primera barra fins pos barra Anterior
            if posBarraAntBalcFines == 0:
                build_ele.listDesplHoritzontalsInfEN.value[0] = build_ele.listDesplHoritzontalsInfEN.value[0]._replace(BarraLlargadaInf = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple)
            else:
                build_ele.listDesplHoritzontalsInfEN.value[0] = build_ele.listDesplHoritzontalsInfEN.value[0]._replace(BarraLlargadaInf = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple + build_ele.dadesTDVertEN.value[0].BarraAmple)#+ build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2)
            build_ele.listDesplHoritzontalsInfEN.value[0] = build_ele.listDesplHoritzontalsInfEN.value[0]._replace(desplX = 0)
            #segona barra fins final de barra seguent
            build_ele.listDesplHoritzontalsInfEN.value[1] = build_ele.listDesplHoritzontalsInfEN.value[1]._replace(desplX = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs  + build_ele.dadesTDVertEN.value[0].BarraAmple)#- build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2)
            if build_ele.BarraLlargadaInfEN.value > (build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple):
                #build_ele.listDesplHoritzontalsInfEN.value[1] = build_ele.listDesplHoritzontalsInfEN.value[1]._replace(BarraLlargadaInf = build_ele.BarraLlargadaEN.value - (build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple ))#- build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2))
                build_ele.listDesplHoritzontalsInfEN.value[1] = build_ele.listDesplHoritzontalsInfEN.value[1]._replace(BarraLlargadaInf = build_ele.BarraLlargadaEN.value - build_ele.listDesplHoritzontalsInfEN.value[1].desplX )#- build_ele.dadesTDVertEN.value[0].BarraAmple)
            else:
                build_ele.listDesplHoritzontalsInfEN.value[1] = build_ele.listDesplHoritzontalsInfEN.value[1]._replace(BarraLlargadaInf = 100)

            #CREAR PORTA (PREMARC)
            build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(MostrarInclinat = True)
            build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Posicio = 0)

            if trobatAnt and trobatSeg:
                print("trobatANt and trobatSeg")

                if posBarraAntBalcFines == 0:
                    #build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + (build_ele.dadesTDVertEN.value[0].BarraAmple/2 - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2) - 10)
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = (build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple) - (build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple)  - 10)
                else:
                    #build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - 10)
                    #build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + (build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2 - build_ele.dadesTDVertEN.value[posBarraSegBalcFines].BarraAmple/2) - 10)
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - (build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple)   - 10)
                if build_ele.SelectorTDHorSupBalcEN.value != "EN Superior" and build_ele.SelectorTDHorSupBalcEN.value != "EN Inferior":
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.BarresHorListEN.value[nHorSup].Posicio  + build_ele.BarraAlturaInf.value + 1)
                else:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value + 1)
                if posBarraAntBalcFines == 0:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplX = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple + 5)#build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 + 5)
                else:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplX = build_ele.PosicioXBalconeraEN.value)#build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 + 5)
                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplY = build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplYAbs)
            elif not trobatAnt and trobatSeg:
                print("not trobatAnt and trobatSeg")

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsEN.value[0].desplXAbs - build_ele.dadesTDVertEN.value[0].BarraAmple - 10)
                if build_ele.SelectorTDHorSupBalcEN.value != "EN Superior" and build_ele.SelectorTDHorSupBalcEN.value != "EN Inferior":
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.BarresHorListEN.value[nHorSup].Posicio - build_ele.dadesTDHortInterEN.value[nHorSup].Altura/2 - 6)
                else:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value )

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplX = build_ele.listDesplVerticalsEN.value[0].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple + 5)#build_ele.PosicioXBalconeraEN.value)#build_ele.listDesplVerticalsEN.value[0].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple + 5)
                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplY = build_ele.listDesplVerticalsEN.value[0].desplYAbs)

            elif trobatAnt and not trobatSeg:
                print("trobatAnt and not trobatSeg")

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[build_ele.IntegerENSelector.value-1].desplXAbs - build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs - build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple - 10)
                if build_ele.SelectorTDHorSupBalcEN.value != "EN Superior" and build_ele.SelectorTDHorSupBalcEN.value != "EN Inferior":
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.BarresHorListEN.value[nHorSup].Posicio - build_ele.dadesTDHortInterEN.value[nHorSup].Altura/2 - 6)
                else:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value  +1 )

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplX = build_ele.PosicioXBalconeraEN.value)#build_ele.listDesplVerticalsEN.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertEN.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 + 5)
            else:
                print("else")

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Llargada = build_ele.listDesplVerticalsEN.value[build_ele.IntegerENSelector.value-1].desplXAbs - build_ele.listDesplVerticalsEN.value[0].desplXAbs  - 10)
                if build_ele.SelectorTDHorSupBalcEN.value != "EN Superior" and build_ele.SelectorTDHorSupBalcEN.value != "EN Inferior":
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.BarresHorListEN.value[nHorSup].Posicio + 1 )
                else:
                    build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value  + 1)

                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplX = build_ele.listDesplVerticalsEN.value[0].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple+ 5)#build_ele.PosicioXBalconeraEN.value)#build_ele.listDesplVerticalsEN.value[0].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple + 5)
                build_ele.dadesENInclinades.value[0] = build_ele.dadesENInclinades.value[0]._replace(desplY = build_ele.listDesplVerticalsEN.value[0].desplYAbs)


            #AFEGIR BARRA REFORÇ
            #modificar barra reforç 0 de posBarraAntBalcFines a posBarraSegBalcFines i mostrarla
            Nref = 0
            if getNumFromText(build_ele, build_ele.SelectorREFInfBalcEN.value, 7) != "":
                Nref = getNumFromText(build_ele, build_ele.SelectorREFInfBalcEN.value, 7)

            if build_ele.SelectorReforcEN.value == "Varifix " + str(Nref):
                build_ele.BarresRefListToShowEN.value[Nref] = build_ele.BarresRefListToShowEN.value[Nref]._replace(BarraRef = True)
                build_ele.BarresRefListToShowEN.value[Nref] = build_ele.BarresRefListToShowEN.value[Nref]._replace(BarraIni = "Tub " + str(posBarraAntBalcFines))
                build_ele.BarresRefListToShowEN.value[Nref] = build_ele.BarresRefListToShowEN.value[Nref]._replace(BarraFin = "Tub " + str(posBarraSegBalcFines))
                build_ele.BarresRefListToShowEN.value[Nref] = build_ele.BarresRefListToShowEN.value[Nref]._replace(Posicio = build_ele.PosicioZBalconeraEN.value )
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraRef = True)
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraIni = "Tub " + str(posBarraAntBalcFines))
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraFin = "Tub " + str(posBarraSegBalcFines))
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(Posicio = build_ele.PosicioZBalconeraEN.value - 30)
            else:
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraRef = True)
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraIni = "Tub " + str(posBarraAntBalcFines))
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(BarraFin = "Tub " + str(posBarraSegBalcFines))
                build_ele.BarresRefListEN.value[Nref] = build_ele.BarresRefListEN.value[Nref]._replace(Posicio = build_ele.PosicioZBalconeraEN.value - 30)

            build_ele.UpdateBalconeraFinestraEN.value = False
        build_ele.SelectorBalcFinAnt.value = nBalcFin
    elif build_ele.SelectorPPEN.value == 5:
        print("SelectorPPEN = 5")


    #build_ele.IntegerENSelector.value = len(build_ele.nListEncaixVert.value)

    guardar_valors_inici(build_ele,nVer)

    if build_ele.SelectorENVAnt.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPEN.value):
        mostrar_valors_actuals(build_ele, nVer)
        set_all_edit_to_false(build_ele)
        #guardar_valors_inici(build_ele,nVer)

    hihaVertEditant = False
    '''
    for nbarra in range(0,len(build_ele.BarresVertListToShow.value)):
        if(build_ele.BarresVertListToShow.value[nbarra].Edit):
            hihaVertEditant = True
    build_ele.VertEditant.value = hihaVertEditant
    '''



    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()


    #------------------ Definir valors Barra Inferior

    #Afegir Barra Horitzontal al group_elems

    try:
        IntegerENSelector = build_ele.IntegerENSelector.value-1
        inici = build_ele.nListBarresHor.value[IntegerENSelector].Posicio
        final = build_ele.nListBarresHor.value[IntegerENSelector].Posicio + build_ele.nListBarresHor.value[IntegerENSelector].nTotal
        llargadaPlus = 0
        for nBarraHorFinal in range(inici, final):
            if nBarraHorFinal >= len(build_ele.BarresHorListEN.value):
                set_values_barresHor(build_ele, nBarraHorFinal)
            if build_ele.BarresHorListEN.value[nBarraHorFinal].BarraHor and build_ele.BarresHorListEN.value[nBarraHorFinal].Longitud >  llargadaPlus:
                llargadaPlus = build_ele.BarresHorListEN.value[nBarraHorFinal].Longitud + 30
    except Exception as e:
        llargadaPlus = 0
        print("No hi ha dades suficients per llargadaPlus: " + e)

    llargadaInf = build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value
    desplXSeparat = build_ele.desplXI.value
    desplYSeparat = 0
    if build_ele.SepararTDHoritzontalInf.value:
        #build_ele.BarraLlargadaEN.value = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf
        desplXSeparat = build_ele.listDesplHoritzontalsInfEN.value[0].desplX
        llargadaInf = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf + desplXSeparat
        desplYSeparat = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf
        #build_ele.BarraAmpleInf.value = build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf
        #build_ele.BarraAlturaInf.value = build_ele.listDesplHoritzontalsInfEN.value[0].BarraAlturaInf


    llargadaINF1 = 30
    if build_ele.llargadaigualHor.value:
        llargadaINF1 = build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value
        llargadaINF1 = llargadaInf
    else:
        if not build_ele.SepararTDHoritzontalInf.value:
            llargadaINF1 = build_ele.BarraLlargadaInfEN.value
        else:
            llargadaINF1 = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf

    vermellInf = build_ele.FounColorInf.value
    if build_ele.VermellInf.value:
        vermellInf = 6

    horitzontalPPInf = ""
    if build_ele.TubInferior.value == "L":
        horitzontalPPInf = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaINF1, build_ele.BarraGruix.value, build_ele.InvertirENHoritzontalInf.value, False,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInf, build_ele.BarraLayer.value,
                                retallInici= desplXSeparat,
                                Encaixos = build_ele.EncaixosParINF.value) #EncaixosPar)
    else:
        horitzontalPPInf = PP_EN_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreEN.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaINF1, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInf, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaINFerior,
                                [])#build_ele.EncaixosParINF.value) #EncaixosPar)

        #horitzontalPPInf = horitzontalPPInf

    if not horitzontalPPInf.is_valid():
        return[]

    build_ele.DENInf.value = "L"
    if build_ele.TubInferior.value != "L":
        build_ele.DENInf.value = "T"

    #definir atributs de la Barra Horitzontal Inferior
    horitzontal_Brep = horitzontalPPInf.create()
    common_propsInf = AllplanBaseElements.CommonProperties()
    common_propsInf = horitzontalPPInf.get_common_props()

    if build_ele.reconeixerDen.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPPInf)
        if (tubEsIgual):
            build_ele.DENInf.value = DEN


    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_d_inv()) )

    if  mostrarActual == "ENHINF":
        common_propsInf.Color = vermellInf#Vermell
        if not build_ele.SepararTDHoritzontalInf.value:
            handle_list = horitzontalPPInf.create_handles()
        else:
            handle_list = []

    atrENEsp = definirAtributPers(build_ele,0,"TubInferior")
    atr02 = "TUB(" + str(build_ele.BarraAmpleInf.value) + str(build_ele.BarraAlturaInf.value) +  str(build_ele.BarraGruix.value)  + ")"
    atr05 = "Cara_X"
    if build_ele.InvertirENHoritzontalInf.value:
        atr05 = "Cara_Y"
    if not build_ele.TubInferior.value == "L":
        atr02 = "XAPA(" + str(build_ele.BarraAmpleInf.value) + str(build_ele.BarraAlturaInf.value) +  str(build_ele.BarraGruix.value)  + ")"
        atr05 = "Baix"

    table_attr_list = [ AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                        AllplanBaseElements.AttributeString(2108,  cara_a),
                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                        AllplanBaseElements.AttributeString(2047,  cara_b),
                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                        AllplanBaseElements.AttributeString(2110,  cara_c),
                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                        AllplanBaseElements.AttributeString(2120,  cara_d),
                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                        AllplanBaseElements.AttributeString(2121,  cara_e),
                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                        AllplanBaseElements.AttributeString(2122,  cara_f),
                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                        AllplanBaseElements.AttributeString(2128,  cara_g),
                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                        AllplanBaseElements.AttributeString(2129,  cara_h),
                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                        AllplanBaseElements.AttributeString(2509,  cara_h2),

                        AllplanBaseElements.AttributeString(1947, atrENEsp),

                        AllplanBaseElements.AttributeString(2430, horitzontalPPInf.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPPInf.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPPInf.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2446, horitzontalPPInf.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2431, horitzontalPPInf.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2445, horitzontalPPInf.get_seccio()),
                        #AllplanBaseElements.AttributeString(220, horitzontalPPInf.get_llargada()),
                        AllplanBaseElements.AttributeString(220, str(llargadaINF1)),
                        #AllplanBaseElements.AttributeString(2455, horitzontalPPInf.get_llargada()),
                        AllplanBaseElements.AttributeString(2455, str(llargadaINF1)),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPPInf.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, str(llargadaINF1)),
                        AllplanBaseElements.AttributeString(1087, atr05),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                        AllplanBaseElements.AttributeString(508, "L")]
    table_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsInf, horitzontal_Brep)])]



    #------------------ Definir valors Barra Superior
    '''
    horitzontalPP2 = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreEN.value, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value) #EncaixosPar)
    '''



    listEncaixAdj = []
    listEncaixAdj = Encaixos_hor_amb_verticals(build_ele)
    horitzontalPPSup = HoritzontalPPSupL = ""

    table_views2 = ""

    vermellSup = build_ele.FounColorSup.value
    if build_ele.VermellSup.value:
        vermellSup = 6

    llargadaSup = build_ele.BarraLlargadaEN.value
    AmpleSup = build_ele.BarraAmpleSup.value


    if build_ele.TubSuperior.value == "EXD":
        AmpleSup = build_ele.BarraAmpleSup.value
        horitzontalPPSup = PP_EN_Horitzontal_Sup(random.random() * 3600, AmpleSup, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruix.value, build_ele.InvertirENHoritzontalSup.value,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    build_ele.dadesTDVertEN.value[0].BarraAmple , build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1].BarraAmple,
                                    build_ele.IsUseGlobalProp.value, vermellSup, build_ele.BarraLayer.value, listEncaixAdj)
        #horitzontalPPSup = horitzontalPPSup

        if not horitzontalPPSup.is_valid():
            return[]

        orientacioLsup = True
        if build_ele.InvertirENHoritzontalSup.value:
            orientacioLsup = False
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = True
        else:
            orientacioLsup = True
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = False
        #HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value, build_ele.BarraAlturaSup.value + build_ele.BarraGruix.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value, orientacioLsup,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
        HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleSupL.value, 50, llargadaSup, build_ele.BarraGruix.value, orientacioLsup, build_ele.InvertirENHoritzontalSupLUpDown.value,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    build_ele.IsUseGlobalProp.value, vermellSup, build_ele.BarraLayer.value)

        if not HoritzontalPPSupL.is_valid():
            return[]

        build_ele.DENSup.value = "E "
        #definir atributs de la Barra Horitzontal Superior
        horitzontal_Brep2 = horitzontalPPSup.create()
        horitzontalSupL_Brep = HoritzontalPPSupL.create()

        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPPSup)
            if (tubEsIgual):
                build_ele.DENSup.value = DEN
        atrENEsp = definirAtributPers(build_ele,0,"TubSuperior")

        cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_d_inv()) )

        common_propsSup = AllplanBaseElements.CommonProperties()
        common_propsSup = horitzontalPPSup.get_common_props()
        if  mostrarActual == "ENHSUP":
            if build_ele.VermellSup.value:
                common_propsSup.Color = 6 #RED
            #handle_list = horitzontalPPSup.create_handles()
        table_attr_list2 = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                            AllplanBaseElements.AttributeString(2108,  cara_a),
                            AllplanBaseElements.AttributeString(2494,  cara_a1),
                            AllplanBaseElements.AttributeString(2495,  cara_a2),
                            AllplanBaseElements.AttributeString(2047,  cara_b),
                            AllplanBaseElements.AttributeString(2496,  cara_b1),
                            AllplanBaseElements.AttributeString(2497,  cara_b2),
                            AllplanBaseElements.AttributeString(2110,  cara_c),
                            AllplanBaseElements.AttributeString(2498,  cara_c1),
                            AllplanBaseElements.AttributeString(2499,  cara_c2),
                            AllplanBaseElements.AttributeString(2120,  cara_d),
                            AllplanBaseElements.AttributeString(2500,  cara_d1),
                            AllplanBaseElements.AttributeString(2501,  cara_d2),

                            AllplanBaseElements.AttributeString(2121,  cara_e),
                            AllplanBaseElements.AttributeString(2502,  cara_e1),
                            AllplanBaseElements.AttributeString(2503,  cara_e2),
                            AllplanBaseElements.AttributeString(2122,  cara_f),
                            AllplanBaseElements.AttributeString(2504,  cara_f1),
                            AllplanBaseElements.AttributeString(2505,  cara_f2),
                            AllplanBaseElements.AttributeString(2128,  cara_g),
                            AllplanBaseElements.AttributeString(2506,  cara_g1),
                            AllplanBaseElements.AttributeString(2507,  cara_g2),
                            AllplanBaseElements.AttributeString(2129,  cara_h),
                            AllplanBaseElements.AttributeString(2508,  cara_h1),
                            AllplanBaseElements.AttributeString(2509,  cara_h2),


                            AllplanBaseElements.AttributeString(1947, atrENEsp),

                            AllplanBaseElements.AttributeString(2431, horitzontalPPSup.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2445, horitzontalPPSup.get_seccio()),
                            AllplanBaseElements.AttributeString(220, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, horitzontalPPSup.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                            AllplanBaseElements.AttributeString(508, "EN")]

        build_ele.DENSup.value = "L"
        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, HoritzontalPPSupL)
            if (tubEsIgual):
                build_ele.DENSup.value = DEN


        cara_a, cara_a1, cara_a2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d_inv()) )
        table_attr_list2L = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                            AllplanBaseElements.AttributeString(2108,  cara_a),
                            AllplanBaseElements.AttributeString(2494,  cara_a1),
                            AllplanBaseElements.AttributeString(2495,  cara_a2),
                            AllplanBaseElements.AttributeString(2047,  cara_b),
                            AllplanBaseElements.AttributeString(2496,  cara_b1),
                            AllplanBaseElements.AttributeString(2497,  cara_b2),
                            AllplanBaseElements.AttributeString(2110,  cara_c),
                            AllplanBaseElements.AttributeString(2498,  cara_c1),
                            AllplanBaseElements.AttributeString(2499,  cara_c2),
                            AllplanBaseElements.AttributeString(2120,  cara_d),
                            AllplanBaseElements.AttributeString(2500,  cara_d1),
                            AllplanBaseElements.AttributeString(2501,  cara_d2),

                            AllplanBaseElements.AttributeString(2121,  cara_e),
                            AllplanBaseElements.AttributeString(2502,  cara_e1),
                            AllplanBaseElements.AttributeString(2503,  cara_e2),
                            AllplanBaseElements.AttributeString(2122,  cara_f),
                            AllplanBaseElements.AttributeString(2504,  cara_f1),
                            AllplanBaseElements.AttributeString(2505,  cara_f2),
                            AllplanBaseElements.AttributeString(2128,  cara_g),
                            AllplanBaseElements.AttributeString(2506,  cara_g1),
                            AllplanBaseElements.AttributeString(2507,  cara_g2),
                            AllplanBaseElements.AttributeString(2129,  cara_h),
                            AllplanBaseElements.AttributeString(2508,  cara_h1),
                            AllplanBaseElements.AttributeString(2509,  cara_h2),


                            AllplanBaseElements.AttributeString(1947, ""),

                            AllplanBaseElements.AttributeString(2431, HoritzontalPPSupL.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2445, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(220, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                            AllplanBaseElements.AttributeString(508, "L")]
        table_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2)])]
        table_views2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontalSupL_Brep)])]
    elif build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior":
        llargadaSup =  build_ele.BarraLlargadaEN.value
        if build_ele.TubSuperior.value == "TUB Interior":
            AmpleSup = build_ele.BarraAmpleSupTubInt.value
            build_ele.PestanyaSuperiorSUP.value = True
            build_ele.PestanyaInferiorSUP.value = True
            llargadaSup = build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1].BarraAmple
        else:
            build_ele.PestanyaSuperiorSUP.value = False
            build_ele.PestanyaInferiorSUP.value = False

        femellesSup = getFemelles(build_ele, AmpleSup)

        horitzontalPPSup = PP_EN_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreEN.value, AmpleSup, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellSup, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value + femellesSup, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value + listEncaixAdj) #EncaixosPar)
        '''
        horitzontalPPSup = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                [])
        '''
        #horitzontalPPSup = horitzontalPPSup

        if not horitzontalPPSup.is_valid():
            return[]

        horitzontal_Brep2 = horitzontalPPSup.create()


        build_ele.DENSup.value = "T"
        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPPSup)
            if (tubEsIgual):
                build_ele.DENSup.value = DEN

        cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPPSup.get_codi_cara_d_inv()) )

        atrENEsp = definirAtributPers(build_ele,0,"TubSuperior")

        common_propsSup = AllplanBaseElements.CommonProperties()
        common_propsSup = horitzontalPPSup.get_common_props()
        if  mostrarActual == "ENHSUP":
            common_propsSup.Color = vermellSup #RED
            #handle_list = horitzontalPPSup.create_handles()
        table_attr_list2 = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                            AllplanBaseElements.AttributeString(2108,  cara_a),
                            AllplanBaseElements.AttributeString(2494,  cara_a1),
                            AllplanBaseElements.AttributeString(2495,  cara_a2),
                            AllplanBaseElements.AttributeString(2047,  cara_b),
                            AllplanBaseElements.AttributeString(2496,  cara_b1),
                            AllplanBaseElements.AttributeString(2497,  cara_b2),
                            AllplanBaseElements.AttributeString(2110,  cara_c),
                            AllplanBaseElements.AttributeString(2498,  cara_c1),
                            AllplanBaseElements.AttributeString(2499,  cara_c2),
                            AllplanBaseElements.AttributeString(2120,  cara_d),
                            AllplanBaseElements.AttributeString(2500,  cara_d1),
                            AllplanBaseElements.AttributeString(2501,  cara_d2),

                            AllplanBaseElements.AttributeString(2121,  cara_e),
                            AllplanBaseElements.AttributeString(2502,  cara_e1),
                            AllplanBaseElements.AttributeString(2503,  cara_e2),
                            AllplanBaseElements.AttributeString(2122,  cara_f),
                            AllplanBaseElements.AttributeString(2504,  cara_f1),
                            AllplanBaseElements.AttributeString(2505,  cara_f2),
                            AllplanBaseElements.AttributeString(2128,  cara_g),
                            AllplanBaseElements.AttributeString(2506,  cara_g1),
                            AllplanBaseElements.AttributeString(2507,  cara_g2),
                            AllplanBaseElements.AttributeString(2129,  cara_h),
                            AllplanBaseElements.AttributeString(2508,  cara_h1),
                            AllplanBaseElements.AttributeString(2509,  cara_h2),

                            AllplanBaseElements.AttributeString(2446, horitzontalPPSup.get_codi_pota_inv()),

                            AllplanBaseElements.AttributeString(2430, horitzontalPPSup.get_codi_pestanyes()),
                            AllplanBaseElements.AttributeString(2435, horitzontalPPSup.get_codi_cancam()),
                            AllplanBaseElements.AttributeString(2433, horitzontalPPSup.get_codi_pota()),

                            AllplanBaseElements.AttributeString(1947, atrENEsp),

                            AllplanBaseElements.AttributeString(2431, horitzontalPPSup.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2445, horitzontalPPSup.get_seccio()),
                            AllplanBaseElements.AttributeString(220, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, horitzontalPPSup.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, horitzontalPPSup.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                            AllplanBaseElements.AttributeString(508, "EN")]
        table_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2)])]


        orientacioLsup = True
        if build_ele.InvertirENHoritzontalSup.value:
            orientacioLsup = False
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = True
        else:
            orientacioLsup = True
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = False

        valorAnt = build_ele.TubSuperior.value
        build_ele.TubSuperior.value = "TUB Interior + L"
        femellesSup = getFemelles(build_ele, AmpleSup)
        build_ele.TubSuperior.value = valorAnt
        #HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value, build_ele.BarraAlturaSup.value + build_ele.BarraGruix.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value, orientacioLsup,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
        HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleSupL.value, 50, build_ele.BarraLlargadaEN.value-5, build_ele.BarraGruix.value, orientacioLsup, build_ele.InvertirENHoritzontalSupLUpDown.value,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    build_ele.IsUseGlobalProp.value, vermellSup, build_ele.BarraLayer.value, femellesSup)

        if not HoritzontalPPSupL.is_valid():
            return[]


        horitzontalSupL_Brep = HoritzontalPPSupL.create()
        build_ele.DENSup.value = "L"
        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, HoritzontalPPSupL)
            if (tubEsIgual):
                build_ele.DENSup.value = DEN


        cara_a, cara_a1, cara_a2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d_inv()) )
        table_attr_list2L = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                            AllplanBaseElements.AttributeString(2108,  cara_a),
                            AllplanBaseElements.AttributeString(2494,  cara_a1),
                            AllplanBaseElements.AttributeString(2495,  cara_a2),
                            AllplanBaseElements.AttributeString(2047,  cara_b),
                            AllplanBaseElements.AttributeString(2496,  cara_b1),
                            AllplanBaseElements.AttributeString(2497,  cara_b2),
                            AllplanBaseElements.AttributeString(2110,  cara_c),
                            AllplanBaseElements.AttributeString(2498,  cara_c1),
                            AllplanBaseElements.AttributeString(2499,  cara_c2),
                            AllplanBaseElements.AttributeString(2120,  cara_d),
                            AllplanBaseElements.AttributeString(2500,  cara_d1),
                            AllplanBaseElements.AttributeString(2501,  cara_d2),

                            AllplanBaseElements.AttributeString(2121,  cara_e),
                            AllplanBaseElements.AttributeString(2502,  cara_e1),
                            AllplanBaseElements.AttributeString(2503,  cara_e2),
                            AllplanBaseElements.AttributeString(2122,  cara_f),
                            AllplanBaseElements.AttributeString(2504,  cara_f1),
                            AllplanBaseElements.AttributeString(2505,  cara_f2),
                            AllplanBaseElements.AttributeString(2128,  cara_g),
                            AllplanBaseElements.AttributeString(2506,  cara_g1),
                            AllplanBaseElements.AttributeString(2507,  cara_g2),
                            AllplanBaseElements.AttributeString(2129,  cara_h),
                            AllplanBaseElements.AttributeString(2508,  cara_h1),
                            AllplanBaseElements.AttributeString(2509,  cara_h2),


                            AllplanBaseElements.AttributeString(1947, ""),

                            AllplanBaseElements.AttributeString(2431, HoritzontalPPSupL.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2445, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(220, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                            AllplanBaseElements.AttributeString(508, "L")]
        table_views2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontalSupL_Brep)])]
    else: #build_ele.TubSuperior.value == "L"
        AmpleSup = build_ele.BarraAmpleSupL.value

        orientacioLsup = True
        if build_ele.InvertirENHoritzontalSup.value:
            orientacioLsup = False
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = True
        else:
            orientacioLsup = True
            if build_ele.InvertirENHoritzontalSupL.value:
                orientacioLsup = False

        femellesSup = getFemelles(build_ele, AmpleSup)
        llargadaSup = llargadaSup - build_ele.dadesTDVertEN.value[0].Gruix - 1 - build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1].Gruix - 1
        #HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value, build_ele.BarraAlturaSup.value + build_ele.BarraGruix.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value, orientacioLsup,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
        HoritzontalPPSupL = PP_EN_Horitzontal_Inf(random.random() * 3600, AmpleSup, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruix.value, orientacioLsup, build_ele.InvertirENHoritzontalSupLUpDown.value,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    build_ele.IsUseGlobalProp.value, vermellSup, build_ele.BarraLayer.value,
                                    femellesSup  )
                                    #Separacio_forat_femella = 40, Altura_forat_femella = 3, Ample_forat_femella = 7.5)#femellesSup

        if not HoritzontalPPSupL.is_valid():
            return[]

        build_ele.DENSup.value = "T "
        #definir atributs de la Barra Horitzontal Superior
        horitzontalSupL_Brep = HoritzontalPPSupL.create()


        common_propsSup = AllplanBaseElements.CommonProperties()
        common_propsSup = HoritzontalPPSupL.get_common_props()
        if  mostrarActual == "ENHSUP":
            common_propsSup.Color = vermellSup #RED

        build_ele.DENSup.value = "L"
        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, HoritzontalPPSupL)
            if (tubEsIgual):
                build_ele.DENSup.value = DEN
        atrENEsp = definirAtributPers(build_ele,1,"TubSuperior")

        cara_a, cara_a1, cara_a2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(HoritzontalPPSupL.get_codi_cara_d_inv()) )

        table_attr_list2L = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                            AllplanBaseElements.AttributeString(2108,  cara_a),
                            AllplanBaseElements.AttributeString(2494,  cara_a1),
                            AllplanBaseElements.AttributeString(2495,  cara_a2),
                            AllplanBaseElements.AttributeString(2047,  cara_b),
                            AllplanBaseElements.AttributeString(2496,  cara_b1),
                            AllplanBaseElements.AttributeString(2497,  cara_b2),
                            AllplanBaseElements.AttributeString(2110,  cara_c),
                            AllplanBaseElements.AttributeString(2498,  cara_c1),
                            AllplanBaseElements.AttributeString(2499,  cara_c2),
                            AllplanBaseElements.AttributeString(2120,  cara_d),
                            AllplanBaseElements.AttributeString(2500,  cara_d1),
                            AllplanBaseElements.AttributeString(2501,  cara_d2),

                            AllplanBaseElements.AttributeString(2121,  cara_e),
                            AllplanBaseElements.AttributeString(2502,  cara_e1),
                            AllplanBaseElements.AttributeString(2503,  cara_e2),
                            AllplanBaseElements.AttributeString(2122,  cara_f),
                            AllplanBaseElements.AttributeString(2504,  cara_f1),
                            AllplanBaseElements.AttributeString(2505,  cara_f2),
                            AllplanBaseElements.AttributeString(2128,  cara_g),
                            AllplanBaseElements.AttributeString(2506,  cara_g1),
                            AllplanBaseElements.AttributeString(2507,  cara_g2),
                            AllplanBaseElements.AttributeString(2129,  cara_h),
                            AllplanBaseElements.AttributeString(2508,  cara_h1),
                            AllplanBaseElements.AttributeString(2509,  cara_h2),


                            AllplanBaseElements.AttributeString(1947, atrENEsp),

                            AllplanBaseElements.AttributeString(2431, HoritzontalPPSupL.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2445, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(220, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, HoritzontalPPSupL.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, HoritzontalPPSupL.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            #AllplanBaseElements.AttributeString(1083,  "E-L"),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            #AllplanBaseElements.AttributeString(2103, "E-L"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                            AllplanBaseElements.AttributeString(508, "L")]
        table_views2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontalSupL_Brep)])]




    #Definir valors de la barra Vertical Inicial
    Encaixos, Femelles, Potes, Forats, Colis = get_valors_actuals(build_ele, 0, AmpleSup)

    '''
    #--------CREATE VERTICAL--------- POSAR DADES MATRIUS [0]
    chair = PP_EN_Vertical(random.random() * 3600, build_ele.dadesTDVertEN.value[0].BarraAmple+10, build_ele.dadesTDVertEN.value[0].BarraAltura, build_ele.BarraLlargadaVert.value,build_ele.dadesTDVertEN.value[0].Gruix,
                            build_ele.IsUseGlobalPropVert.value, build_ele.FounColorVert.value, build_ele.BarraLayerVert.value,
                            Colis, Potes, Forats, #matrius ------
                            build_ele.dadesTDVertEN.value[0].Ample_forat_femellaVert, build_ele.dadesTDVertEN.value[0].Altura_forat_femellaVert, build_ele.dadesTDVertEN.value[0].Separacio_forat_femellaVert,
                            Femelles, #matriu -----
                            build_ele.dadesTDVertEN.value[0].posicio_centre_massesVert,
                            build_ele.dadesTDVertEN.value[0].IsFirstCancamVert, build_ele.dadesTDVertEN.value[0].Dis1cancamVert,
                            build_ele.dadesTDVertEN.value[0].IsSecondCancamVert, build_ele.dadesTDVertEN.value[0].Dis2cancamVert,
                            build_ele.dadesTDVertEN.value[0].PestanyaSuperiorVert, build_ele.dadesTDVertEN.value[0].PestanyaInferiorVert,
                            Encaixos)

    chair_brep = chair.create()
    common_props = chair.get_common_props()
    if  mostrarActual == "ENV0":
        common_props.Color = 6#Vermell
        #handle_list = chair.create_handles()
    chair_attr_list = [AllplanBaseElements.AttributeDouble(AllplanBaseElements.ATTRNR_VOLUME, chair.volume())]
    chairs_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, chair_brep)])]
    #----------END CREATE VERTICAL----------------------
    '''

    matrixPosX = []
    matrixPosY = []
    matrixcentrar = []
    matrixOffsetY = []
    matrixOr = []

    matrixMostrar = []
    matrixMostrarInf = []
    matrixMostrarSup = []

    for i in range(0,build_ele.IntegerENSelector.value):
        matrixcentrar.append(build_ele.dadesTDVertEN.value[i].BarraAmple/2)
        matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs )
        matrixPosY.append(build_ele.listDesplVerticalsEN.value[i].desplY)
        matrixMostrar.append(build_ele.dadesTDVertEN.value[i].MostrarTDVertical)
        matrixMostrarInf.append(((build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].PestanyaInferiorVert and build_ele.dadesTDVertEN.value[i].FemellaInf) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.EncaixHorInf.value and not build_ele.dadesTDVertEN.value[i].EncaixInf) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].FemellaInf))and build_ele.dadesTDVertEN.value[i].BarraInferior == "EN Inferior")
        matrixMostrarSup.append(((build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].PestanyaSuperiorVert and build_ele.dadesTDVertEN.value[i].FemellaSup) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.EncaixHorSup.value and not build_ele.dadesTDVertEN.value[i].EncaixSup) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].FemellaSup))and build_ele.dadesTDVertEN.value[i].BarraSuperior == "EN Superior")
    listAmples = []
    listAmples2 = []
    listAltures = []
    for TDVert in build_ele.dadesTDVertEN.value:
        listAmples.append(TDVert.BarraAmple - TDVert.Gruix*2)
        listAmples2.append(TDVert.BarraAmple)
        listAltures.append(TDVert.BarraAltura)
    #Crear Encaixos i Femelles en les Barres Horitzontals
    offsetXI = build_ele.desplXI.value
    offsetXS = build_ele.desplXS.value

    #for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
    if not build_ele.ReduirTempsCarrega.value and build_ele.TubSuperior.value != "L":

        #if (build_ele.desplYI.value != 0.0 and build_ele.desplYI.value > 0.0) or (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):
        """
        if (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):

            if build_ele.invertirEncaixInf.value:
                horitzontalPPInf.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                    if build_ele.dadesTDVertEN.value[i].EncaixInf:
                        matrixOr.append("Esq")
                    else:
                        matrixOr.append("Inf")
                trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    matrixOffsetY.append(  build_ele.listDesplVerticalsEN.value[i].desplY + build_ele.dadesTDVertEN.value[i].BarraAltura - build_ele.desplYI.value)
                trans_list = horitzontalPPInf.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXI, 'Sup', build_ele.BarraLlargadaEN.value)
                horitzontalPPInf.set_false_femelles()
        elif (build_ele.EncaixHorInf.value and build_ele.desplYI.value <= 0.0):
            if build_ele.invertirEncaixInf.value:
                horitzontalPPInf.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                    if build_ele.dadesTDVertEN.value[i].EncaixInf:
                        matrixOr.append("Esq")
                    else:
                        matrixOr.append("Sup")
                trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    matrixOffsetY.append( build_ele.BarraAmpleInf.value - build_ele.listDesplVerticalsEN.value[i].desplY + build_ele.desplYI.value)#build_ele.dadesTDVertEN.value[i].BarraAltura

                trans_list = horitzontalPPInf.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXI, 'Inf', build_ele.BarraLlargadaEN.value )
                horitzontalPPInf.set_false_femelles()
        else:
            horitzontalPPInf.set_false_encaix()

            #matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                #matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs )
                matrixOr.append("Esq")
            trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value,[], build_ele.desplXI.value)
        """
        matrixOffsetY = []
        matrixOr = []
        if build_ele.EncaixHorSup.value and build_ele.desplYS.value > 0.0 and (build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior"):
            if build_ele.invertirEncaixSup.value:
                horitzontalPPSup.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                    if build_ele.dadesTDVertEN.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Inf")
                trans_listSup = horitzontalPPSup.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value,build_ele.desplYS.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    matrixOffsetY.append(  build_ele.listDesplVerticalsEN.value[i].desplY + build_ele.dadesTDVertEN.value[i].BarraAltura - build_ele.desplYS.value)#build_ele.dadesTDVertEN.value[i].BarraAltura
                trans_listSup = horitzontalPPSup.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXS, 'Sup', build_ele.BarraLlargadaEN.value)
                horitzontalPPSup.set_false_femelles()
        elif build_ele.EncaixHorSup.value and build_ele.desplYS.value <= 0.0:
            if build_ele.invertirEncaixSup.value:
                horitzontalPPSup.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                    #matrixPosX.append(build_ele.desplXS.value + build_ele.BarraAmpleSup.value - build_ele.listDesplVerticalsEN.value[i].desplX + build_ele.dadesTDVertEN.value[i].BarraAmple)
                    if build_ele.dadesTDVertEN.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Sup")
                trans_listSup = horitzontalPPSup.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value,build_ele.desplYS.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                    #matrixOffsetY.append(build_ele.BarraAmpleSup.value + build_ele.desplYS.value + build_ele.listDesplVerticalsEN.value[i].desplY )
                    matrixOffsetY.append(AmpleSup + build_ele.desplYS.value + build_ele.listDesplVerticalsEN.value[i].desplY )
                trans_listSup = horitzontalPPSup.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXS, 'Inf', build_ele.BarraLlargadaEN.value)
                horitzontalPPSup.set_false_femelles()
        else:
            horitzontalPPSup.set_false_encaix()
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                matrixOr.append("Dre")
            trans_listSup = horitzontalPPSup.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXS, matrixOr, build_ele.Ample_forat_femellaVert.value,build_ele.BarraLlargadaEN.value, build_ele.desplYS.value,[], build_ele.desplXI.value)



    update_mat_nListVert(build_ele)

    contadorPPH = 0
    contadorPPV = 0
    contadorPPI = 0

    vectorH1 = AllplanGeo.Matrix3D()
    vectorH1.SetValue(12, build_ele.desplXI.value)
    #print(vectorH1)
    #vectorH1.SetValue(12, desplXSeparat)
    vectorH1.SetValue(13, build_ele.desplYI.value)
    if not build_ele.InvertirENHoritzontalInf.value:
        vectorH1.SetValue(13, build_ele.desplYI.value - (build_ele.BarraAmpleInf.value - build_ele.dadesTDVertEN.value[0].BarraAltura))

    vectorH1.SetValue(14, 0)


    common_propsObject = AllplanBaseElements.CommonProperties()
    common_propsObject.Layer = 40055#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 16 #GRIS

    common_propsObjectRecess = AllplanBaseElements.CommonProperties()
    common_propsObjectRecess.Layer = 40054#56811#build_ele.BarraLayer.value#64178
    common_propsObjectRecess.Color = 16 #GRIS

    if not build_ele.SepararTDHoritzontalInf.value:
        llargadaInfCavitat = build_ele.BarraLlargadaEN.value
    else:
        llargadaInfCavitat = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf
    horitzontalPPOBject = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, llargadaInfCavitat, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBjectRecess = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, llargadaInfCavitat, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value)]

    horitzontal_BrepObject = horitzontalPPOBject.create()
    horitzontal_BrepObjectRecess = horitzontalPPOBjectRecess.create()

    TranslationFather = vectorH1
    TranslationFather.SetValue(12, placement_mat[12] + vectorH1[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH1[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH1[14])
    vectorH1  = TranslationFather

    vectorH1C = AllplanGeo.Matrix3D()
    vectorH1C.SetValue(12, vectorH1[12])
    vectorH1C.SetValue(13, vectorH1[13])
    vectorH1C.SetValue(14, vectorH1[14] - 5)

    table_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject)])]
    table_views_objectRecess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObjectRecess)])]


    if build_ele.MostrarTDHoritzontalInf.value :#and not build_ele.SepararTDHoritzontalInf.value:
        #horitzontalPPInf with translate has to be the firsrt element because of group modification
        # Define python part for TDHoritzontal
        #if not build_ele.SepararTDHoritzontalInf.value:



        group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = horitzontalPPInf.get_params_list(),
                                    hash_value = horitzontalPPInf.hash(), python_file = horitzontalPPInf.filename(),
                                    views = table_views, matrix = TranslationFather, common_props = common_propsInf, attribute_list = table_attr_list))
        group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = horitzontalPPInf.get_params_list(),
                                    hash_value = horitzontalPPInf.hash(), python_file = horitzontalPPInf.filename(),
                                    views = table_views, matrix = TranslationFather, common_props = common_propsInf, attribute_list = table_attr_list))

        #if not build_ele.SepararTDHoritzontalInf.value:
        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
        #                            hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
        #                            views = table_views_object, matrix = vectorH1C, common_props = common_propsObject, attribute_list = table_attr_listObject))

        #group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
        #                                hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
        #                                views = table_views_object, matrix = vectorH1C, common_props = common_propsObject, attribute_list = table_attr_listObject))

        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectRecess.get_params_list(),
        #                            hash_value = horitzontalPPOBjectRecess.hash(), python_file = horitzontalPPOBjectRecess.filename(),
        #                            views = table_views_objectRecess, matrix = vectorH1C, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))

        #group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectRecess.get_params_list(),
        #                                hash_value = horitzontalPPOBjectRecess.hash(), python_file = horitzontalPPOBjectRecess.filename(),
        #                                views = table_views_objectRecess, matrix = vectorH1C, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))
        """
        else:
            vectorH1.SetValue(12, 0)
            vectorH1.SetValue(13, 0)

            #vectorH1.SetValue(12, build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf)
            #vectorH1.SetValue(13, build_ele.listDesplHoritzontalsInfEN.value[0].BarraAlturaInf)
            vectorH1.SetValue(14, 0)
        """
        """
        for i in range(0, len(build_ele.ColisParINF.value)):

            if build_ele.ColisParINF.value[i].Colis and build_ele.ColisParINF.value[i].MostrarBox and build_ele.ColisParINF.value[i].Posicio < build_ele.BarraLlargadaEN.value:
                boxsColis = createColisInf(build_ele,0, i)
                group_elems.append(boxsColis)
        """

        #if not build_ele.SepararTDHoritzontalInf.value:
        if build_ele.mostrarLiniaIntInf1.value:
            if len(build_ele.listDesplHoritzontalsInfEN.value)<=0:
                add_baraInferior(build_ele, 1)
            punt_central = TranslationFather[12] + desplXSeparat + build_ele.desplXI.value + build_ele.BarraAlturaInf.value/2
            pointUbi = AllplanGeo.Point3D(TranslationFather[12] + desplXSeparat, vectorH1[13] + build_ele.BarraAmpleInf.value/2 , vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
            if build_ele.SepararTDHoritzontalInf.value:
                punt_central = TranslationFather[12] +desplXSeparat + build_ele.listDesplHoritzontalsInfEN.value[0].desplX + build_ele.listDesplHoritzontalsInfEN.value[0].BarraAlturaInf/2
                pointUbi = AllplanGeo.Point3D(TranslationFather[12] + desplXSeparat, vectorH1[13] + build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf/2 + build_ele.listDesplHoritzontalsInfEN.value[0].desplLinA, vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
            if (len(build_ele.SelectorLiniaInf.value)) <=1:
                build_ele.SelectorLiniaInf.value = "Tipus 1"
            linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
            polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf,llargadaINF1, True, pointUbi, int(linia), build_ele.SelectorLayerInfEN.value, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])
                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
        if build_ele.mostrarLiniaIntInf2.value:
            if len(build_ele.listDesplHoritzontalsInfEN.value)<=0:
                add_baraInferior(build_ele, 1)
            punt_central = TranslationFather[12] + desplXSeparat + build_ele.desplXI.value + build_ele.BarraAlturaInf.value/2
            pointUbi = AllplanGeo.Point3D(TranslationFather[12] +desplXSeparat, vectorH1[13] + build_ele.BarraAmpleInf.value/2 , vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
            if build_ele.SepararTDHoritzontalInf.value:
                punt_central = TranslationFather[12] + desplXSeparat + build_ele.listDesplHoritzontalsInfEN.value[0].desplX + build_ele.listDesplHoritzontalsInfEN.value[0].BarraAlturaInf/2
                pointUbi = AllplanGeo.Point3D(TranslationFather[12] + desplXSeparat, vectorH1[13] + build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf/2 + build_ele.listDesplHoritzontalsInfEN.value[0].desplLinB, vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
            if (len(build_ele.SelectorLiniaInf.value)) <=1:
                build_ele.SelectorLiniaInf.value = "Tipus 1"
            linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
            polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsInfEN.value[0].BarraAmpleInf,llargadaINF1, True, pointUbi, int(linia), build_ele.SelectorLayerInfEN.value, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])
                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))


    listHoritzontalPP = []
    listElements = []

    if build_ele.SepararTDHoritzontalInf.value:
        for nBarresInf in range(1, build_ele.nBarresTDHoritzontalInf.value):
            elements , lHoritzontalPP, elements_model_eleList = crear_barres_inferiors_multiples(build_ele, nBarresInf, mostrarActual, doc, placement_mat)
            listHoritzontalPP.append(lHoritzontalPP)
            listElements.append(elements)
            #for model in elements_model_eleList:
            #    model_ele_list2.append(model)
            #    preview_ele_list.append(model)


    contadorPPH += 1

    #Posicionar Barra Superior
    vectorH2 = AllplanGeo.Matrix3D()
    vectorH2.SetValue(12, build_ele.desplXS.value)
    if build_ele.TubSuperior.value == "L":
        vectorH2.SetValue(12, build_ele.desplXS.value + build_ele.dadesTDVertEN.value[0].Gruix + 1)
    vectorH2.SetValue(13, build_ele.desplYS.value)

    llargadaVertical = build_ele.BarraLlargadaVert.value
    llargadaVertical = build_ele.desplZS.value + build_ele.BarraAlturaInf.value #- build_ele.BarraAlturaSup.value/2


    #if build_ele.desplYI.value == 0.0 or build_ele.EncaixHorInf.value:
    '''
    if not build_ele.EncaixHorInf.value:
        #if build_ele.desplYS.value != 0.0 :
        if build_ele.EncaixHorSup.value :
            llargadaVertical = build_ele.BarraLlargadaVert.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value
        else:
            llargadaVertical = build_ele.BarraLlargadaVert.value + build_ele.BarraAlturaInf.value
    else:
        #if build_ele.desplYS.value != 0.0 :
        if build_ele.EncaixHorSup.value:
            llargadaVertical = build_ele.BarraLlargadaVert.value - build_ele.BarraAlturaSup.value
        else:
            llargadaVertical = build_ele.BarraLlargadaVert.value
    '''

    vectorH2.SetValue(14, llargadaVertical)


    horitzontalPPOBject2 = PP_EN_Horitzontal(random.random() * 3600, 0, AmpleSup, build_ele.BarraAlturaSup.value+10, llargadaSup, 0,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                #build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2L = PP_EN_Horitzontal(random.random() * 3600, 0, build_ele.BarraAmpleSupL.value, 50+10, llargadaSup, 0,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                #build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2Recess = PP_EN_Horitzontal(random.random() * 3600, 0, AmpleSup, build_ele.BarraAlturaSup.value+10, llargadaSup, 0,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                #build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2LRecess = PP_EN_Horitzontal(random.random() * 3600, 0, build_ele.BarraAmpleSupL.value, 50+10, llargadaSup, 0,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                #build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])

    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2L = horitzontalPPOBject2L.create()

    horitzontal_BrepObject2Recess = horitzontalPPOBject2Recess.create()
    horitzontal_BrepObject2LRecess = horitzontalPPOBject2LRecess.create()

    TranslationFather = vectorH2
    TranslationFather.SetValue(12, placement_mat[12] + vectorH2[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH2[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH2[14])
    vectorH2  = TranslationFather


    vectorH2C = AllplanGeo.Matrix3D()
    vectorH2C.SetValue(12, vectorH2[12])
    vectorH2C.SetValue(13, vectorH2[13])
    vectorH2C.SetValue(14, vectorH2[14]-5)


    vectorH2L = AllplanGeo.Matrix3D()
    vectorH2L2 = AllplanGeo.Matrix3D()
    vectorH2L.SetValue(12, vectorH2[12])
    vectorH2L2.SetValue(12, vectorH2[12])
    if build_ele.TubSuperior.value == "TUB Interior":
        vectorH2.SetValue(12, vectorH2[12] + build_ele.dadesTDVertEN.value[0].BarraAmple)
        vectorH2C.SetValue(12, vectorH2[12])

        vectorH2L.SetValue(12, build_ele.desplXSL.value )
        vectorH2L.SetValue(13, build_ele.desplYSL.value )
        vectorH2L.SetValue(14, build_ele.desplZSL.value + build_ele.BarraAlturaInf.value )

    elif build_ele.TubSuperior.value == "L":
        vectorH2L.SetValue(13, vectorH2[13])
        vectorH2L.SetValue(14, vectorH2[14] )
    else:
        if build_ele.InvertirENHoritzontalSup.value :
            vectorH2L.SetValue(13,  vectorH2[13] - 50)
            vectorH2L2.SetValue(13, vectorH2[13] - 50)
            if build_ele.InteriorENHoritzontalSupL.value:
                vectorH2L.SetValue(13,  vectorH2L[13] + build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value)
                vectorH2L2.SetValue(13, vectorH2L2[13] + build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value)
            if build_ele.InvertirENHoritzontalSupL.value:
                vectorH2L.SetValue(13,  vectorH2[13] + build_ele.BarraAmpleSup.value)
                vectorH2L2.SetValue(13, vectorH2[13] + build_ele.BarraAmpleSup.value)
                if build_ele.InteriorENHoritzontalSupL.value:
                    vectorH2L.SetValue(13,  vectorH2[13] - build_ele.BarraGruix.value)
                    vectorH2L2.SetValue(13, vectorH2[13] - build_ele.BarraGruix.value )

        else:
            vectorH2L.SetValue(13,  vectorH2[13] + build_ele.BarraAmpleSup.value)
            vectorH2L2.SetValue(13, vectorH2[13] + build_ele.BarraAmpleSup.value)
            if build_ele.InteriorENHoritzontalSupL.value:
                vectorH2L.SetValue(13,  vectorH2L[13] - build_ele.BarraAmpleSup.value - build_ele.BarraGruix.value)
                vectorH2L2.SetValue(13, vectorH2L2[13] - build_ele.BarraAmpleSup.value - build_ele.BarraGruix.value)
            if build_ele.InvertirENHoritzontalSupL.value :
                vectorH2L.SetValue(13,  vectorH2[13] - 50)
                vectorH2L2.SetValue(13, vectorH2[13] - 50)
                if build_ele.InteriorENHoritzontalSupL.value:
                    vectorH2L.SetValue(13,  vectorH2L[13] + build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value)
                    vectorH2L2.SetValue(13, vectorH2L2[13] + build_ele.BarraAmpleSup.value + build_ele.BarraGruix.value)


        vectorH2L.SetValue(14, vectorH2[14] + 15)
        vectorH2L2.SetValue(14, vectorH2[14] + 10)



    if build_ele.MostrarTDHoritzontalSup.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
        table_views_object2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2L)])]
        table_views_object2Recess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObject2Recess)])]
        table_views_object2LRecess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObject2LRecess)])]
        #if build_ele.TubSuperior.value == "EXD" or build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior" or build_ele.TubSuperior.value == "L":
        if build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior" :
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props= common_propsObject, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props= common_propsObject, attribute_list = table_attr_listObject))
        #if build_ele.TubSuperior.value == "EXD" or build_ele.TubSuperior.value == "L":
        #    group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2LRecess.get_params_list(),
        #                                hash_value = horitzontalPPOBject2LRecess.hash(), python_file = horitzontalPPOBject2LRecess.filename(),
        #                                views = table_views_object2LRecess, matrix = vectorH2L2, common_props= common_propsObjectRecess, attribute_list = table_attr_listObject))
        #    group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2LRecess.get_params_list(),
        #                                hash_value = horitzontalPPOBject2LRecess.hash(), python_file = horitzontalPPOBject2LRecess.filename(),
        #                                views = table_views_object2LRecess, matrix = vectorH2L2, common_props= common_propsObjectRecess, attribute_list = table_attr_listObject))


        #Afegir Barra Horitzontal al group_elems
        if build_ele.TubSuperior.value == "EXD" or build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior":
            group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = horitzontalPPSup.get_params_list(),
                                        hash_value = horitzontalPPSup.hash(), python_file = horitzontalPPSup.filename(),
                                        views = table_views2, matrix = vectorH2, common_props= common_propsSup, attribute_list = table_attr_list2))
            group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = horitzontalPPSup.get_params_list(),
                                        hash_value = horitzontalPPSup.hash(), python_file = horitzontalPPSup.filename(),
                                        views = table_views2, matrix = vectorH2, common_props= common_propsSup, attribute_list = table_attr_list2))
        if (build_ele.TubSuperior.value == "EXD" and build_ele.mostrarL.value) or (build_ele.TubSuperior.value == "TUB Interior" and build_ele.mostrarL.value) or build_ele.TubSuperior.value == "L":
            group_elems.append(PythonPart ("PP_EN_Horitzontal_L", parameter_list = HoritzontalPPSupL.get_params_list(),
                                        hash_value = HoritzontalPPSupL.hash(), python_file = HoritzontalPPSupL.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props= common_propsSup, attribute_list = table_attr_list2L))
            group_elems_preview.append(PythonPart ("PP_EN_Horitzontal_L", parameter_list = HoritzontalPPSupL.get_params_list(),
                                        hash_value = HoritzontalPPSupL.hash(), python_file = HoritzontalPPSupL.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props= common_propsSup, attribute_list = table_attr_list2L))

        """
        if  build_ele.IsFirstCancamSUP.value:
            if build_ele.posicio_centre_massesSUP.value  + build_ele.Dis1cancamSUP.value/ 2 < build_ele.BarraLlargadaEN.value and build_ele.posicio_centre_massesSUP.value  + build_ele.Dis2cancamSUP.value/ 2 < build_ele.BarraLlargadaEN.value:
                cilindre = createCancam(build_ele, llargadaVertical)
                group_elems.append(cilindre)


        for i in range(0, len(build_ele.ColisParSUP.value)):

            if build_ele.ColisParSUP.value[i].Colis and build_ele.ColisParSUP.value[i].MostrarBox and build_ele.ColisParSUP.value[i].Posicio < build_ele.BarraLlargadaEN.value:
                boxsColis = createColis(build_ele, llargadaVertical, i)
                group_elems.append(boxsColis)
        """

        if build_ele.mostrarLiniaIntSup1.value:
            punt_central = vectorH2[12] + build_ele.desplXS.value + build_ele.BarraAlturaSup.value/2
            pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + AmpleSup/2 + build_ele.desplLiniaIntSup1.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
            if (len(build_ele.SelectorLiniaSup.value)) <=1:
                build_ele.SelectorLiniaSup.value = "Tipus 1"
            linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]

            llargadaEixSup = build_ele.BarraLlargadaEN.value
            try:
                llargadaEixSup = float(horitzontalPPSup.get_llargada())
            except Exception as e :
                print("llargada superior incorrecta 1")
            polyhedronCentral = create_polyline_interior(build_ele, punt_central, AmpleSup, llargadaEixSup, True, pointUbi, int(linia), build_ele.SelectorLayerSupEN.value, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])
                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
        if build_ele.mostrarLiniaIntSup2.value:
            punt_central = vectorH2[12] + build_ele.desplXS.value + build_ele.BarraAlturaSup.value/2
            pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + AmpleSup/2 + build_ele.desplLiniaIntSup2.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
            if (len(build_ele.SelectorLiniaSup.value)) <=1:
                build_ele.SelectorLiniaSup.value = "Tipus 1"
            linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
            llargadaEixSup = build_ele.BarraLlargadaEN.value
            try:
                llargadaEixSup = float(horitzontalPPSup.get_llargada())
            except Exception as e :
                print("llargada superior incorrecta 2")
            polyhedronCentral = create_polyline_interior(build_ele, punt_central, AmpleSup, llargadaEixSup, True, pointUbi, int(linia), build_ele.SelectorLayerSupEN.value, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])
                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))




    #En cas de que la llargada sigui inferior a la distancia entre TD
    '''
    if build_ele.IntegerENSelector.value < 3 :
        natrix0 = AllplanGeo.Matrix3D()
        group_elems.append(PythonPart ("PP_EN_Vertical", parameter_list = chair.get_params_list(),
                            hash_value = chair.hash(), python_file = chair.filename(),
                            views = chairs_views, matrix = natrix0, attribute_list = chair_attr_list))
        contadorPPV += 1

        #verticalPPOBject = PP_TD_Vertical(build_ele.dadesTDVertEN.value[0].BarraAmple+10, build_ele.dadesTDVertEN.value[0].BarraAltura, build_ele.BarraLlargadaVert.value,build_ele.dadesTDVertEN.value[0].Gruix,
        verticalPPOBject = PP_EN_Vertical(random.random() * 3600, build_ele.BarraAmpleVert.value+10, build_ele.BarraAlturaVert.value, build_ele.BarraLlargadaVert.value, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color,  common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.dadesTDVertEN.value[0].PestanyaSuperiorVert, build_ele.dadesTDVertEN.value[0].PestanyaInferiorVert,
                                [])

        natrix0C = AllplanGeo.Matrix3D()
        natrix0C.SetValue(12, natrix0[12]-5)
        natrix0C.SetValue(13, natrix0[13])
        natrix0C.SetValue(14, natrix0[14])

        vertical_BrepObject = verticalPPOBject.create()
        vertical_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, vertical_BrepObject)])]

        group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = verticalPPOBject.get_params_list(),
                                    hash_value = verticalPPOBject.hash(), python_file = verticalPPOBject.filename(),
                                    views = vertical_views_object, matrix = natrix0C, attribute_list = table_attr_listObject))



        natrix1 = AllplanGeo.Matrix3D()
        natrix1.SetValue(12, build_ele.BarraLlargadaEN.value - build_ele.BarraAmpleInf.value)
        group_elems.append(PythonPart ("PP_EN_Vertical", parameter_list = chair.get_params_list(),
                            hash_value = chair.hash(), python_file = chair.filename(),
                            views = chairs_views, matrix = natrix1, attribute_list = chair_attr_list))
        contadorPPV += 1


        #verticalPPOBject = PP_TD_Vertical(build_ele.dadesTDVertEN.value[0].BarraAmple+10, build_ele.dadesTDVertEN.value[0].BarraAltura, build_ele.BarraLlargadaVert.value,build_ele.dadesTDVertEN.value[0].Gruix,
        verticalPPOBject2 = PP_EN_Vertical(random.random() * 3600, build_ele.BarraAmpleVert.value+10, build_ele.BarraAlturaVert.value, build_ele.BarraLlargadaVert.value, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color,  common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.dadesTDVertEN.value[0].PestanyaSuperiorVert, build_ele.dadesTDVertEN.value[0].PestanyaInferiorVert,
                                [])

        vertical_BrepObject2 = verticalPPOBject2.create()
        vertical_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, vertical_BrepObject2)])]

        natrix1C = AllplanGeo.Matrix3D()
        natrix1C.SetValue(12, natrix1[12]-5)
        natrix1C.SetValue(13, natrix1[13])
        natrix1C.SetValue(14, natrix1[14])


        group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = verticalPPOBject2.get_params_list(),
                                    hash_value = verticalPPOBject2.hash(), python_file = verticalPPOBject2.filename(),
                                    views = vertical_views_object2, matrix = natrix1C, attribute_list = table_attr_listObject))

    '''
    #Crear Barres verticals
    if not build_ele.ReduirTempsCarrega.value:
        try:

            '''
            while build_ele.IntegerENSelector.value > len(trans_list):
                trans_matrix = AllplanGeo.Matrix3D()
                trans_matrix.Translate(AllplanGeo.Vector3D(build_ele.listDesplVerticalsEN.value[len(trans_list)-1].desplXAbs, build_ele.listDesplVerticalsEN.value[len(trans_list)-1].desplYAbs, 0))
                trans_list.append(trans_matrix)
            '''
            # Define python parts for TDVertical
            j = 0

            #for matrix in trans_list:
            for nVertMat in range(0,build_ele.IntegerENSelector.value):
                matrix = AllplanGeo.Matrix3D()
                matrix.SetValue(12, build_ele.listDesplVerticalsEN.value[nVertMat].desplXAbs )#tipus desplaçament desplXAbs#+ build_ele.dadesTDVertEN.value[j].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2)
                matrix.SetValue(13, build_ele.listDesplVerticalsEN.value[nVertMat].desplYAbs)
                matrix.SetValue(14, 0)
                i = j-1

                if j >= len(build_ele.dadesTDVertEN.value):
                    set_values(build_ele, j)
                lennVer = len(build_ele.SelectorENV.value)

                '''
                if build_ele.dadesTDVertEN.value[j].esProvisional:
                    build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(EncaixSup= True)
                    build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(EncaixInf= True)
                    build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaSuperiorVert = False)
                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                        build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaInferiorVert = True)
                    else:
                        build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaInferiorVert = False)
                    if j == nVer:
                        build_ele.encaixSup.value = True
                        build_ele.encaixInf.value = True
                        if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                            build_ele.PestanyaInferiorVert.value = True
                        else:
                            build_ele.PestanyaInferiorVert.value = False
                '''

                #Definir valors de la barra Vertical j
                Encaixos, Femelles, Potes, Forats, Colis = get_valors_actuals(build_ele, j, AmpleSup)

                """
                for nForat in range(0,len(Forats)):
                    if Forats[nForat].Forat and Forats[nForat].MostrarBox and build_ele.dadesTDVertEN.value[j].MostrarTDVertical and build_ele.listDesplVerticalsEN.value[j].desplXAbs <= build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value:
                        group_elems.append(createBoxForat(build_ele, j, Forats, nForat))
                """

                ampleAnt = 0
                ampleSeg = 0
                if j > 0:
                    ampleAnt = build_ele.dadesTDVertEN.value[j-1].BarraAmple
                    ampleSeg = build_ele.dadesTDVertEN.value[j].BarraAmple

                #----------------------------Posicionar Absolut Vertical---------------

                mostrar = True
                nHor1 = 0
                while mostrar and nHor1 < len(build_ele.BarresHorListEN.value):
                    if build_ele.BarresHorListEN.value[nHor1].Edit:
                        mostrar = False
                    nHor1 += 1
                nVer1 = 0

                '''
                while mostrar and nVer1 < len(build_ele.BarresVertListToShow.value):
                    if build_ele.BarresVertListToShow.value[nVer1].Edit:
                        mostrar = False
                    nVer1 += 1
                '''
                #Definir i mostrar la variable posicio desde la posicio 0 absolut(centre primera vertical)
                #build_ele.listDesplVerticalsEN.value[j] =  build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = matrix[12] + build_ele.listDesplVerticalsEN.value[j].desplX )
                #build_ele.listDesplVerticalsEN.value[j] =  build_ele.listDesplVerticalsEN.value[j]._replace(desplYAbs = matrix[13] )


                #if j == nVer and mostrar:
                mostrarInterior = False
                for nValueEdit in range(0,len(build_ele.BarresHorListEN.value)):
                    if build_ele.BarresHorListEN.value[nValueEdit].acabatEditar and not  build_ele.BarresHorListEN.value[nValueEdit].Edit:
                        build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplXAbs
                        build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplYAbs
                    if build_ele.BarresHorListEN.value[nValueEdit].Edit:
                        mostrarInterior = True
                '''
                for nValueEdit in range(0,len(build_ele.BarresVertListToShow.value)):
                    if build_ele.BarresVertListToShow.value[nValueEdit].acabatEditar and not build_ele.BarresVertListToShow.value[nValueEdit].Edit:
                        build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplXAbs
                        build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplYAbs
                    if build_ele.BarresVertListToShow.value[nValueEdit].Edit:
                        mostrarInterior = True
                '''
                if not mostrarInterior:
                    if build_ele.DistanciaEntreTDAnt.value != build_ele.DistanciaEntreEN.value :
                        #build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = matrix[12])#no modificar posicio al canviar la distancia
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = build_ele.DistanciaEntreEN.value * j )
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplYAbs = matrix[13])
                        if j == nVer and build_ele.SelectorPPEN.value == 2:
                            build_ele.desplXVertAbs.value = matrix[12]
                            build_ele.desplYVertAbs.value = matrix[13]
                    #elif build_ele.BarraLlargadaAnt.value != build_ele.BarraLlargadaEN.value and j != build_ele.len(trans_list)-1 and build_ele.listDesplVerticalsEN.value[j].desplXAbs == 0 and j != 0 :
                    elif build_ele.BarraLlargadaAnt.value != build_ele.BarraLlargadaEN.value and j != build_ele.IntegerENSelector.value  and build_ele.listDesplVerticalsEN.value[j].desplXAbs == 0 and j != 0 :
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = matrix[12])
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplX = 0)

                    else:
                        if j == nVer and build_ele.SelectorPPEN.value == 2:
                            #si no esta mostrat
                            #if "TDVer"+str(nVer) == build_ele.SelectorENV.value:
                            if nVer != 0 and build_ele.desplXVertAbs.value == 0:
                                #build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplXAbs
                                #build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsEN.value[j].desplYAbs
                                build_ele.desplXVertAbs.value = build_ele.DistanciaEntreEN.value * nVer
                                build_ele.desplYVertAbs.value = 0
                            else:
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = build_ele.desplXVertAbs.value )
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplYAbs = build_ele.desplYVertAbs.value)
                        else:
                            if j != 0 and build_ele.listDesplVerticalsEN.value[j].desplXAbs == 0:
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = build_ele.DistanciaEntreEN.value * j )
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplYAbs = 0)
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplX = build_ele.listDesplVerticalsEN.value[j].desplXAbs - matrix[12])
                                build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplY = 0)

                    if j == nVer and build_ele.SelectorPPEN.value == 2:
                        build_ele.desplXVert.value = build_ele.desplXVertAbs.value - matrix[12]
                        build_ele.desplYVert.value = build_ele.desplYVertAbs.value #- matrix[13]
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplX = build_ele.desplXVertAbs.value - matrix[12])
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplY = build_ele.desplYVertAbs.value - matrix[13])
                    else:
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplX = build_ele.listDesplVerticalsEN.value[j].desplXAbs - matrix[12])
                        build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplY = build_ele.listDesplVerticalsEN.value[j].desplYAbs - matrix[13])


                    #if j == build_ele.IntegerENSelector.value-1:

                    #if j == len(trans_list)-1:
                if j == build_ele.IntegerENSelector.value-1:
                    #print("posicio Final: " + str(build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[j].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple))
                    build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplXAbs = build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[j].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple)#- build_ele.dadesTDVertEN.value[j].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2)
                    build_ele.listDesplVerticalsEN.value[j] = build_ele.listDesplVerticalsEN.value[j]._replace(desplX = 0)

                        #build_ele.listDesplVerticalsEN.value[0] = build_ele.listDesplVerticalsEN.value[0]._replace(desplX = build_ele.listDesplVerticalsEN.value[0].desplXAbs)


                    #----------------------------END Posicionar Absolut Vertical---------------

                #matrix.SetValue(12, matrix[12] - ampleAnt/2 - ampleSeg/2)
                matrix0 = AllplanGeo.Matrix3D()
                #matrix0.SetValue(12, matrix[12] + build_ele.listDesplVerticalsEN.value[j].desplX)
                matrix0.SetValue(12, build_ele.listDesplVerticalsEN.value[j].desplXAbs + (build_ele.dadesTDVertEN.value[j].BarraAmple+build_ele.dadesTDVertEN.value[0].BarraAmple)/2 )
                matrix0.SetValue(12, build_ele.listDesplVerticalsEN.value[j].desplXAbs +build_ele.dadesTDVertEN.value[0].BarraAmple )
                if j== 0 :
                    matrix0.SetValue(12, build_ele.listDesplVerticalsEN.value[j].desplXAbs - (build_ele.dadesTDVertEN.value[j].BarraAmple-build_ele.dadesTDVertEN.value[0].BarraAmple)/2 )
                    matrix0.SetValue(13, matrix[13] + build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                else:
                    #matrix0.SetValue(13, matrix[13] )
                    matrix0.SetValue(13, build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                    matrix.SetValue(13,build_ele.listDesplVerticalsEN.value[j].desplYAbs)
                matrix0.SetValue(14, build_ele.BarraAlturaInf.value)



                llargadaVertical = build_ele.BarraLlargadaVert.value

                posHorInfAux = 0
                alturaInf = 0
                if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
                    nHorInf = build_ele.dadesTDVertEN.value[j].BarraInferior
                    if getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3) != "":
                        nHorInf = getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3)

                        if build_ele.dadesTDVertEN.value[j].EncaixInf:
                            matrix0.SetValue(14, build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.BarraAlturaInf.value +build_ele.dadesTDHortInterEN.value[nHorInf].Altura )
                            alturaInf = 0
                        else:
                            matrix0.SetValue(14, build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.BarraAlturaInf.value)
                            alturaInf = build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                else:
                    #matrix0.SetValue(14, build_ele.BarraAlturaInf.value )
                    try:
                        matrix0.SetValue(14, build_ele.BarraAlturaInf.value + build_ele.listDesplVerticalsEN.value[j].desplZAbs)
                    except Exception as e:
                        matrix0.SetValue(14, build_ele.BarraAlturaInf.value)
                        print(" ----------------- NO existeix desplZAbs en listDesplVerticalsEN")
                    alturaInf = 0



                #Definir Posicio dels encaixoS es funcio si el deslpaçament es > 0 o < 0
                #Definir si posa encaix o femella
                crearFemellesxEncaixInf = False
                desplInf = "Esq"
                desplSup = "Esq"
                trobatInf = False

                for nBarraInfEnc in range(0,build_ele.nBarresTDHoritzontalInf.value):
                    if nBarraInfEnc >= len(build_ele.listDesplHoritzontalsInfEN.value):
                        add_baraInferior(build_ele, nBarraInfEnc)
                    if not trobatInf and build_ele.SepararTDHoritzontalInf.value and build_ele.listDesplVerticalsEN.value[j].desplXAbs >= build_ele.listDesplHoritzontalsInfEN.value[nBarraInfEnc].desplX and build_ele.listDesplVerticalsEN.value[j].desplXAbs <=  build_ele.listDesplHoritzontalsInfEN.value[nBarraInfEnc].desplX + build_ele.listDesplHoritzontalsInfEN.value[nBarraInfEnc].BarraLlargadaInf:
                        #encaixosAux.append(bob)
                        trobatInf = True
                #if build_ele.desplYI.value != 0.0 or build_ele.EncaixHorInf.value:#or (build_ele.dadesTDVertEN.value[j].BarraAltura.value > build_ele.BarraAmpleInf.value):
                '''
                if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                    if build_ele.EncaixHorInf.value and not build_ele.dadesTDVertEN.value[j].EncaixInf :#or (build_ele.dadesTDVertEN.value[j].BarraAltura.value > build_ele.BarraAmpleInf.value):
                        crearFemellesxEncaixInf = True
                        matrix0.SetValue(14, matrix[14])
                        llargadaVertical += build_ele.BarraAlturaInf.value
                        build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaInferiorVert = False)
                        if build_ele.desplYI.value > 0.0 :
                            desplInf = "Esq"
                        else:
                            desplInf = "Dre"
                    else:
                        crearFemellesxEncaixInf = False

                        if not trobatInf and build_ele.SepararTDHoritzontalInf.value:
                            matrix0.SetValue(14, 0 )
                            crearFemellesxEncaixInf = False
                        #build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaInferiorVert = True)
                '''
                crearFemellesxEncaixSup = False
                #if build_ele.desplYS.value != 0.0 :
                '''
                if build_ele.EncaixHorSup.value and not build_ele.dadesTDVertEN.value[j].EncaixSup :

                    crearFemellesxEncaixSup = True
                    build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaSuperiorVert = False)
                    if build_ele.desplYS.value > 0.0 :
                        desplSup = "Esq"
                    else:
                        desplSup = "Dre"
                else:
                    crearFemellesxEncaixSup = False
                    llargadaVertical -= build_ele.BarraAlturaSup.value
                    #build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(PestanyaSuperiorVert = True)
                '''
                if not build_ele.dadesTDVertEN.value[j].LlargadaAut and j == nVer:
                    BarrallargadaVert = build_ele.BarraLlargadaIndiv.value
                elif not build_ele.dadesTDVertEN.value[j].LlargadaAut :
                    BarrallargadaVert = build_ele.dadesTDVertEN.value[j].BarraAlcada
                else:
                    BarrallargadaVert = build_ele.desplZS.value

                posHorInf = build_ele.BarraAlturaInf.value
                posHorSup = build_ele.desplZS.value + build_ele.BarraAlturaSup.value
                nHorInf = 0
                nHorSup = 0
                #if not build_ele.dadesTDVertEN.value[j].EncaixInf or not build_ele.dadesTDVertEN.value[j].EncaixSup :
                #if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior" or build_ele.dadesTDVertEN.value[j].BarraSuperior != "EN Superior":
                alturaInf = 0

                posHorInf = build_ele.BarraAlturaInf.value
                if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
                    if getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3) != "":
                        nHorInf = getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3)

                        #posHorInf = build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                        if not build_ele.dadesTDVertEN.value[j].EncaixInf:
                            alturaInf = build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.BarraAlturaInf.value#+ build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                        else:
                            alturaInf = -build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.dadesTDHortInterEN.value[nHorInf].Altura + build_ele.BarraAlturaInf.value

                if build_ele.dadesTDVertEN.value[j].LlargadaAut:# build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior":
                    if not build_ele.dadesTDVertEN.value[j].EncaixSup:
                        posHorSup = build_ele.desplZS.value + build_ele.BarraAlturaSup.value + build_ele.BarraAlturaInf.value
                        #alturaInf = build_ele.BarraAlturaInf.value
                    else:
                        posHorSup = build_ele.desplZS.value + build_ele.BarraAlturaInf.value #- build_ele.BarraAlturaSup.value/2
                else:
                    posHorSup = build_ele.dadesTDVertEN.value[j].BarraAlcada + build_ele.BarraAlturaInf.value
                    #alturaInf += build_ele.BarraAlturaInf.value

                if build_ele.dadesTDVertEN.value[j].BarraSuperior != "EN Superior":
                    #alturaInf -= build_ele.BarraAlturaInf.value
                    nHorSup = 0
                    if getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraSuperior, 3) != "":
                        nHorSup = getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraSuperior, 3)
                        if not build_ele.dadesTDVertEN.value[j].EncaixSup:
                            posHorSup = build_ele.BarresHorListEN.value[nHorSup].Posicio + build_ele.dadesTDHortInterEN.value[nHorSup].Altura + build_ele.BarraAlturaInf.value#+ alturaInf
                        else:
                            posHorSup = build_ele.BarresHorListEN.value[nHorSup].Posicio + build_ele.BarraAlturaInf.value#+ alturaInf#- build_ele.dadesTDHortInterEN.value[nHorSup].Altura/2

                #BarrallargadaVert += posHorSup - posHorInf
                if build_ele.dadesTDVertEN.value[j].LlargadaAut:
                    if posHorSup > posHorInf :
                        BarrallargadaVert = posHorSup - posHorInf #(- altura hor)+ alturaInf

                    else:
                        BarrallargadaVert = 30
                else:
                    build_ele.dadesTDVertEN.value[j].BarraAlcada
                if (j == 0 or j == build_ele.IntegerENSelector.value-1) and build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior" and build_ele.dadesTDVertEN.value[j].LlargadaAut and build_ele.TubSuperior.value == "TUB Interior":
                    if  build_ele.dadesTDVertEN.value[j].EncaixSup:
                        BarrallargadaVert = BarrallargadaVert + build_ele.BarraAlturaSup.value  #+ build_ele.BarraAlturaInf.value

                vermellVert =  build_ele.dadesTDVertEN.value[j].FounColor
                if build_ele.dadesTDVertEN.value[j].vermell:
                    vermellVert = 6

                if build_ele.dadesTDVertEN.value[j].LlargadaAut and j == nVer:
                    build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(BarraAlcada = BarrallargadaVert)


                #-------------------- crear TD Interior cada vegada -----------------------
                TDV_Int = PP_EN_Vertical(random.random() * 3600, build_ele.dadesTDVertEN.value[j].BarraAmple, build_ele.dadesTDVertEN.value[j].BarraAltura, BarrallargadaVert ,build_ele.dadesTDVertEN.value[j].Gruix,
                                            build_ele.IsUseGlobalPropVert.value, vermellVert, build_ele.BarraLayerVert.value,
                                            Colis, Potes, Forats, #matrius -------------------------------
                                            build_ele.dadesTDVertEN.value[j].Ample_forat_femellaVert, build_ele.dadesTDVertEN.value[j].Altura_forat_femellaVert, build_ele.dadesTDVertEN.value[j].Separacio_forat_femellaVert,
                                            Femelles, #matriu Femelles -------------------------------------
                                            build_ele.dadesTDVertEN.value[j].posicio_centre_massesVert,
                                            build_ele.dadesTDVertEN.value[j].IsFirstCancamVert, build_ele.dadesTDVertEN.value[j].Dis1cancamVert,
                                            build_ele.dadesTDVertEN.value[j].IsSecondCancamVert, build_ele.dadesTDVertEN.value[j].Dis2cancamVert,
                                            build_ele.dadesTDVertEN.value[j].PestanyaSuperiorVert, build_ele.dadesTDVertEN.value[j].PestanyaInferiorVert,
                                            Encaixos,
                                            [],[],False, [],
                                            build_ele.dadesTDVertEN.value[j].PestanyesInv)#build_ele.pestanyesInvVert.value)#Encaixos

                verticalPPOBject5 = PP_EN_Vertical(random.random() * 3600,build_ele.dadesTDVertEN.value[j].BarraAmple + 6 , build_ele.dadesTDVertEN.value[j].BarraAltura + 2, BarrallargadaVert,0,
                                        False,  common_propsObject.Color,  common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        [], [],[], #ColisPar, PotaPar, #matrius
                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                        [], #Femelles, #matriu
                                        0, #posicio_centre_masses,
                                        False, 0, #IsFirstCancam, Dis1cancam,
                                        False, 0, #IsSecondCancam, Dis2cancam,
                                        False, False,
                                        [])
                verticalPPOBject5Recess = PP_EN_Vertical(random.random() * 3600,build_ele.dadesTDVertEN.value[j].BarraAmple + 6 , build_ele.dadesTDVertEN.value[j].BarraAltura, BarrallargadaVert,0,
                                        False,  common_propsObjectRecess.Color,  common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        [], [],[], #ColisPar, PotaPar, #matrius
                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                        [], #Femelles, #matriu
                                        0, #posicio_centre_masses,
                                        False, 0, #IsFirstCancam, Dis1cancam,
                                        False, 0, #IsSecondCancam, Dis2cancam,
                                        False, False,
                                        [])


                #----------------------END crear TD_Vertical cada vegada-----------------------

                listFemellesAnt = []
                listFemellesAnt2 = []
                posnListTDIAnt2 = 0
                listFemellesAct = []
                if  j < len(build_ele.nListBarresHor.value):
                    inici = build_ele.nListBarresHor.value[j-1].Posicio
                    final = build_ele.nListBarresHor.value[j-1].Posicio + build_ele.nListBarresHor.value[j-1].nTotal

                    if j-2 >= 0:
                        iniciAnt = build_ele.nListBarresHor.value[j-2].Posicio
                        finalAnt = build_ele.nListBarresHor.value[j-2].Posicio + build_ele.nListBarresHor.value[j-2].nTotal

                    #diferenciaAlturaFemella = 0
                    #if trobat and build_ele.SepararTDHoritzontalInf.value:
                    #    diferenciaAlturaFemella = build_ele.barraAlturaInf.value


                    offsetYAnt = []
                    offsetY = []

                    #for nbarraHorAnterior in range(0,build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal):
                    for nbarraHorAnterior in range(0,len(build_ele.BarresHorListEN.value)-1):
                        #print(nbarraHorAnterior)
                        #if nbarraHorAnterior == 35:
                        #    print(nbarraHorAnterior)
                        if nbarraHorAnterior >= len(build_ele.BarresHorListEN.value):
                            set_values_barresHor(build_ele, nbarraHorAnterior)
                        if nbarraHorAnterior >= len(build_ele.dadesTDHortInterEN.value):
                            set_valors_hor_ini(build_ele, 0, nbarraHorAnterior)

                        if len(build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal) == 5:
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-1]
                        elif len(build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal) == 6:
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-2]
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-1] + NBarraFinal
                        else:
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-3]
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-2] + NBarraFinal
                            NBarraFinal = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraFinal[-1] + NBarraFinal


                        if len(build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici) == 5:
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-1]
                        elif len(build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici) == 6:
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-2]
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-1] + NBarraInici
                        else:
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-3]
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-2] + NBarraInici
                            NBarraInici = build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraInici[-1] + NBarraInici



                        NBarraFinal = int(NBarraFinal)
                        NBarraInici = int(NBarraInici)


                        if NBarraFinal == j:
                            if nbarraHorAnterior >= len(build_ele.dadesTDHortInterEN.value):
                                set_valors_hor_ini(build_ele, 0, nbarraHorAnterior)
                            ampleForatFem = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2
                            ampleForatFemInv = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2
                            tubGirat = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].pestanyesInv
                            if ampleForatFem > 15:
                                ampleForatFem = 15
                            if ampleForatFemInv > 15:
                                ampleForatFemInv = 15

                            alturaInfFem = build_ele.BarraAlturaInf.value/2
                            alturaInfEncaix = build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                            plusaltura = (30 - build_ele.dadesTDHortInterEN.value[nHorInf].Altura)
                            if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                alturaInfFem = -4
                                alturaInfEncaix = 0#build_ele.BarraAlturaInf.value
                                plusaltura = 0

                            desplZVertical = build_ele.listDesplVerticalsEN.value[j].desplZAbs

                            if  build_ele.dadesTDVertEN.value[NBarraFinal].EncaixInf:#not build_ele.EncaixHorInf.value or
                                #listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].PestanyaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarraAlturaInf.value -1 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem])
                                if tubGirat:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura - 15/2  , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura - 15/2  , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                    else:
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio  - build_ele.BarresHorListEN.value[nHorInf].Posicio -  (ampleForatFemInv )/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio  - build_ele.BarresHorListEN.value[nHorInf].Posicio -  (ampleForatFemInv )/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                else:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor ,  build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor ,  build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                    else:
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  - build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  - build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])

                            else:
                                #listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].PestanyaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem])
                                if tubGirat:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura - (ampleForatFemInv )/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura - (ampleForatFemInv )/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                    else:
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])

                                else:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                    else:
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)  + alturaInfEncaix - build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAnt.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaSup and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)  + alturaInfEncaix - build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])


                            if tubGirat:
                                offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                                offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                            else:
                                offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2 -  ampleForatFem  + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs + ampleForatFem/2 )
                                offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2 -  ampleForatFem  + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs + ampleForatFem/2 )

                        if NBarraInici == j:
                            if nbarraHorAnterior >= len(build_ele.dadesTDHortInterEN.value):
                                set_valors_hor_ini(build_ele, 0, nbarraHorAnterior)
                            ampleForatFem = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2
                            ampleForatFemInv = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2
                            tubGirat = build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].pestanyesInv
                            if ampleForatFem > 15:
                                ampleForatFem = 15
                            if ampleForatFemInv > 15:
                                ampleForatFemInv = 15

                            alturaInfFem = build_ele.BarraAlturaInf.value/2
                            alturaInfEncaix = build_ele.dadesTDHortInterEN.value[nHorInf].Altura + build_ele.BarraAlturaInf.value
                            if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                alturaInfFem = -4
                                alturaInfEncaix = 0#build_ele.BarraAlturaInf.value

                            desplZVertical = build_ele.listDesplVerticalsEN.value[j].desplZAbs

                            if  build_ele.dadesTDVertEN.value[NBarraInici].EncaixInf:#not build_ele.EncaixHorInf.value or
                                #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].PestanyaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarraAlturaInf.value -1 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFem ])

                                if tubGirat:
                                    #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf) - alturaInfFem  -4 - ampleForatFemInv - ampleForatFemInv/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample, ampleForatFemInv, tubGirat ])
                                    #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf) - alturaInfFem  -4 - ampleForatFemInv - ampleForatFemInv/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample, ampleForatFemInv, tubGirat ])
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarraAlturaInf.value + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv - (4.25*2))/2 - 0.25, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample, ampleForatFemInv, tubGirat ])
                                        #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarraAlturaInf.value + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv - (4.25*2))/2 - 0.25, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample, ampleForatFemInv, tubGirat ])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (15 )/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (15 )/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                    else:
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  -  (ampleForatFemInv )/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  -  (ampleForatFemInv )/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ])

                                else:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio  - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio  - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ])
                                    else:
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio  - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura, ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ])

                            else:
                                if tubGirat:
                                    #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)+1.5 - ampleForatFemInv/2 + alturaInfEncaix, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ,ampleForatFemInv, tubGirat])
                                    #listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)+1.5 - ampleForatFemInv/2 + alturaInfEncaix, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample ,ampleForatFemInv, tubGirat])
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor ,build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor ,build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                    else:
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2 , build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.dadesTDHortInterEN.value[nHorInf].Altura -  (ampleForatFemInv )/2 , getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFemInv, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample])

                                else:
                                    if build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - desplZVertical + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                    else:
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)  + alturaInfEncaix - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2, build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])
                                        listFemellesAct.append([build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].femellaInf and build_ele.BarresHorListEN.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorListEN.value[nbarraHorAnterior].Posicio - (posHorInf)  + alturaInfEncaix - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2, getOrientacioInv(build_ele.BarresHorListEN.value[nbarraHorAnterior].Orientacio), build_ele.BarresHorListEN.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura ,ampleForatFem, tubGirat, build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Altura])


                            if tubGirat:
                                offsetY.append( build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                                offsetY.append( build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs )
                            else:
                                offsetY.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2 -ampleForatFem + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs + ampleForatFem/2 )
                                offsetY.append(build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].Ample/2 -ampleForatFem + build_ele.dadesTDHortInterEN.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs + ampleForatFem/2 )

                separacioFemellaInf = build_ele.BarraAlturaInf.value
                separacioFemellaSup = build_ele.BarraAlturaSup.value
                separacioFemellaInt = build_ele.BarraAlturaVert.value - build_ele.BarraGruix.value * 2
                '''
                if j > 0:
                    if build_ele.dadesTDVertEN.value[j-1].MostrarTDVertical:
                        n = 1
                    else:
                        n = 2
                    iniciAnt = build_ele.nListBarresHor.value[j-n].Posicio
                    finalAnt = build_ele.nListBarresHor.value[j-n].Posicio + build_ele.nListBarresHor.value[j-n].nTotal
                    #for nBarraHor in range(iniciAnt,finalAnt):
                    #    offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 - build_ele.dadesTDVertEN.value[j].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)


                #inici = build_ele.nListBarresHor.value[j].Posicio
                #final = build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal
                for nBarraHor in range(inici,final):
                    offsetY.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 - build_ele.dadesTDVertEN.value[j].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)
                #'''


                if not trobatInf and build_ele.SepararTDHoritzontalInf.value:
                    crearFemellesxEncaixInf = False

                """
                offsetY = []
                offsetYAnt = []
                if j > 0:
                    if build_ele.dadesTDVertEN.value[j-1].MostrarTDVertical:
                        n = 1
                    else:
                        n = 2
                    iniciAnt = 0#build_ele.nListBarresHor.value[j-n].Posicio
                    finalAnt = 30#build_ele.nListBarresHor.value[j-n].Posicio + build_ele.nListBarresHor.value[j-n].nTotal
                    for nBarraHor in range(iniciAnt,finalAnt):
                        #offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 - build_ele.dadesENVert.value[j].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)
                        ampleForatFem = build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2/2
                        if ampleForatFem > 15/2:
                            ampleForatFem = 15/2
                        offsetYAnt.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 -  ampleForatFem  + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)


                while j >= len(build_ele.nListBarresHor.value):
                    i = len(build_ele.nListBarresHor.value)
                    ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                    bob = ENCollection( Posicio = build_ele.nListBarresHor.value[i-1].Posicio + build_ele.nListBarresHor.value[i-1].nTotal,
                                        nTotal = 8)
                    build_ele.nListBarresHor.value.append(bob)
                    set_valors_hor_ini(build_ele, j, 8)

                inici = 0#build_ele.nListBarresHor.value[j].Posicio
                final = 30#build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal
                for nBarraHor in range(inici,final):
                    #offsetY.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 - build_ele.dadesENVert.value[j].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)
                    ampleForatFem = build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2/2
                    if ampleForatFem > 15/2:
                        ampleForatFem = 15/2
                    offsetY.append(build_ele.dadesTDHortInterEN.value[nBarraHor].Ample/2 -ampleForatFem + build_ele.dadesTDHortInterEN.value[nBarraHor].desplY - build_ele.listDesplVerticalsEN.value[j].desplYAbs)
                """
                #FemellesAux = TDV_Int.actualitzar_femelles_TDH(listFemellesAnt, listFemellesAct, j, offsetY, offsetYAnt, crearFemellesxEncaixInf and build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior", desplInf, crearFemellesxEncaixSup and build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior", desplSup, separacioFemellaInf , separacioFemellaSup, separacioFemellaInt)
                FemellesAux = TDV_Int.actualitzar_femelles_ENH(listFemellesAnt, listFemellesAct, j, offsetY, offsetYAnt, crearFemellesxEncaixInf, desplInf, crearFemellesxEncaixSup, desplSup, separacioFemellaInf , separacioFemellaSup, separacioFemellaInt)
                '''
                if j != 0:
                    if not build_ele.dadesTDVertEN.value[j-1].MostrarTDVertical:
                        if j-2 >= 0:
                            if posnListTDIAnt2 >= 0:
                                FemellesAux = TDV_Int.actualitzar_femelles_TDH(listFemellesAnt2, listFemellesAct, j, offsetY, offsetYAnt, crearFemellesxEncaixInf and build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior", desplInf, crearFemellesxEncaixSup and build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior", desplSup, separacioFemellaInf , separacioFemellaSup, separacioFemellaInt)
                '''
                build_ele.DENVert.value = "T"


                estaEditant = False
                for posBarraHor in range(0, len(build_ele.BarresHorListEN.value)-1):#recorrer totes les Barres Horitzontals de cada vertical
                    testEditBarraHorInterior = build_ele.BarresHorListEN.value[posBarraHor].Edit
                    if testEditBarraHorInterior == True:
                        estaEditant = True
                    #if  mostrarActual == "TDV"+str(j) and not estaEditant and nVer == j:
                    #    common_props.Color = 6#Vermell



                try:

                    if  j < len(build_ele.nListBarresHor.value):
                        inici = build_ele.nListBarresHor.value[j].Posicio
                        final = build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal



                        for posBarraHor in range(inici, final):#recorrer totes les Barres Horitzontals de cada vertical
                            #posBarraHorinJ = j * NombreBarresHorInt + posBarraHor - inici
                            #----------------------- Afegir Barra Hor -----------------------------------
                            NBarraFinal = build_ele.BarresHorListEN.value[posBarraHor].BarraFinal[-1]
                            NBarraInici = build_ele.BarresHorListEN.value[posBarraHor].BarraInici[-1]
                            NBarraFinal = int(NBarraFinal)
                            NBarraInici = int(NBarraInici)
                            if posBarraHor >= len(build_ele.BarresHorListEN.value):
                                set_values_barresHor(build_ele, posBarraHor)

                            tubHorSeleccionat = 0
                            if getNumFromText(build_ele, build_ele.SelectorTDHTotalEN.value, 3) != "":
                                tubHorSeleccionat = getNumFromText(build_ele, build_ele.SelectorTDHTotalEN.value, 3)

                            if build_ele.SelectorPPEN.value == 1 and build_ele.SelectorENH.value == "Mes Tubs..." and tubHorSeleccionat == posBarraHor and not build_ele.BarresHorListEN.value[posBarraHor].Edit:
                                build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Edit = True)
                                build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Edit = True)
                                mostrar_valors_horToShow(build_ele, posBarraHor)
                            if build_ele.SelectorPPEN.value == 1 and build_ele.SelectorENH.value == "Mes Tubs..." and tubHorSeleccionat == posBarraHor and build_ele.BarresHorListEN.value[posBarraHor].Edit:
                                guardar_valors_horToShow(build_ele, posBarraHor)
                                #guardar_valors_hor(build_ele, j, posBarraHor)
                            if build_ele.SelectorPPEN.value != 1 or build_ele.SelectorENH.value != "Mes Tubs...":
                                #build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Edit = False)
                                build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Edit = False)
                                #print(build_ele.BarresHorListEN.value[posBarraHor].Edit)

                            if build_ele.SelectorTDHTotalEN.value != build_ele.SelectorTDHTotalAntEN.value :#or build_ele.SelectorENH.value != build_ele.SelectorTDHAnt.value:
                                tubHorSeleccionatAnt = 0
                                if isinstance(build_ele.SelectorTDHTotalAntEN.value, str):
                                    if getNumFromText(build_ele, build_ele.SelectorTDHTotalAntEN.value, 3) != "":
                                        tubHorSeleccionatAnt = getNumFromText(build_ele, build_ele.SelectorTDHTotalAntEN.value, 3)
                                else:
                                    tubHorSeleccionatAnt = build_ele.SelectorTDHTotalAntEN.value


                                build_ele.BarresHorListEN.value[tubHorSeleccionatAnt] = build_ele.BarresHorListEN.value[tubHorSeleccionatAnt]._replace(Edit = False)
                            build_ele.SelectorTDHTotalAntEN.value = build_ele.SelectorTDHTotalEN.value
                            build_ele.SelectorTDHAnt.value = build_ele.SelectorENH.value

                            #if NBarraInici < len(trans_list)  and build_ele.BarresHorListEN.value[posBarraHor].BarraHor:
                            if NBarraInici < build_ele.IntegerENSelector.value  :#and build_ele.BarresHorListEN.value[posBarraHor].BarraHor:
                                #if NBarraFinal+1 < len(trans_list):
                                if NBarraFinal+1 < build_ele.IntegerENSelector.value:
                                    if not build_ele.BarresHorListEN.value[posBarraHor].AutoLongitud:
                                        llargada = build_ele.BarresHorListEN.value[posBarraHor].Longitud
                                    else:
                                        if build_ele.dadesTDVertEN.value[NBarraFinal].MostrarTDVertical :#and not build_ele.BarresVertList.value[j*NombreBarresVertInt].BarraVert:
                                            if NBarraInici == 0 and NBarraFinal == build_ele.IntegerENSelector.value -1 :
                                                #print("1 - de 0  a ultima : "+ str(posBarraHor))
                                                llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple -  build_ele.dadesTDHortInterEN.value[posBarraHor].desplX#- build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2
                                            elif NBarraInici == 0:
                                                #print("1 - de 0  a n : "+ str(posBarraHor))
                                                llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs #- build_ele.dadesTDVertEN.value[0].BarraAmple/2 + build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2
                                            elif NBarraFinal == build_ele.IntegerENSelector.value -1:
                                                #print("1 - de n  a ultima : "+ str(posBarraHor))
                                                llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple -  build_ele.dadesTDHortInterEN.value[posBarraHor].desplX#- build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple
                                            else:
                                                #print("1 - de n  a n : "+ str(posBarraHor))
                                                #llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple  + (build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDHortInterEN.value[NBarraInici].desplX
                                                llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple  - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX#+ (build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDHortInterEN.value[NBarraInici].desplX
                                        elif not build_ele.dadesTDVertEN.value[NBarraFinal].MostrarTDVertical and build_ele.BarresVertList.value[(NBarraFinal)*NombreBarresVertInt].BarraVert:
                                            llargada = build_ele.BarresVertList.value[(NBarraFinal)*NombreBarresVertInt].PosicioAbs - build_ele.dadesTDVertInter.value[(NBarraFinal)*NombreBarresVertInt].BarraAmple/2 - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX
                                        else:
                                            llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal+1].desplXAbs - build_ele.dadesTDVertEN.value[NBarraFinal+1].BarraAmple/2 - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX

                                else:
                                    if not build_ele.BarresHorListEN.value[posBarraHor].AutoLongitud:
                                        llargada = build_ele.BarresHorListEN.value[posBarraHor].Longitud
                                    else:
                                        #if NBarraFinal == len(trans_list)-1:
                                        if NBarraInici == 0 and NBarraFinal == build_ele.IntegerENSelector.value -1 :
                                            #print("2 - de 0  a ultima : "+ str(posBarraHor))
                                            llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX#- build_ele.dadesTDVertEN.value[0].BarraAmple #- build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple
                                        elif NBarraFinal == build_ele.IntegerENSelector.value -1:
                                            #print("2 - de n  a ultima : "+ str(posBarraHor))
                                            #llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple# - build_ele.dadesTDVertEN.value[0].BarraAmple/2 + build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - (build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple - (build_ele.dadesTDVertEN.value[0].BarraAmple/2))
                                            #llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs  - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple# - build_ele.dadesTDVertEN.value[0].BarraAmple/2 + build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - (build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple - (build_ele.dadesTDVertEN.value[0].BarraAmple/2))
                                            #llargada = (build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple - build_ele.dadesTDVertEN.value[0].BarraAmple) - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple#build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2
                                            llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX#build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2
                                        #if NBarraFinal == build_ele.IntegerENSelector.value -1:
                                        #    llargada = build_ele.listDesplVerticalsEN.value[NBarraFinal].desplXAbs - build_ele.dadesTDVertEN.value[NBarraFinal].BarraAmple/2 - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2
                                        else:
                                            llargada = build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple

                                if llargada <= 0:
                                    llargada = 30
                                build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Longitud = llargada)

                                testEditBarraHorInterior = build_ele.BarresHorListEN.value[posBarraHor].Edit

                                if testEditBarraHorInterior :#and nVer == j:
                                    #si esta buit
                                    while len(build_ele.dadesTDHortInterEN.value) <= j * NombreBarresHorInt + (posBarraHor - inici)*NombreBarresHorInt:
                                        set_valors_hor_ini(build_ele, j, len(build_ele.dadesTDHortInterEN.value))

                                    if build_ele.dadesTDHortInterEN.value[posBarraHor].acabatEditar == False:
                                        build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(acabatEditar = True)
                                    #si no estan mostrats
                                    if  build_ele.BarresHorListEN.value[posBarraHor].acabatEditar == False and build_ele.BarresHorListEN.value[posBarraHor].Edit == True: #al clicar a edit
                                        #mostrar valors
                                        mostrar_valors_hor(build_ele, j, posBarraHor - inici)
                                        build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(estaEditant = True)
                                        build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(acabatEditar = True)
                                        build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Edit = True)
                                        build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(acabatEditar = True)

                                    #guardar valors
                                    guardar_valors_hor(build_ele, j, posBarraHor - inici)
                                else:
                                    if len(build_ele.dadesTDHortInterEN.value) <= j * NombreBarresHorInt + (posBarraHor - inici)*3:
                                        set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                    if build_ele.dadesTDHortInterEN.value[posBarraHor].acabatEditar == True :#and nVer == j:
                                        #guardar valors
                                        #guardar_valors_hor(build_ele, j, posBarraHor - inici)
                                        if build_ele.SelectorPPEN.value == 2:
                                            mostrar_valors_actuals(build_ele, nVer)

                                        build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(acabatEditar = False)
                                        build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(acabatEditar = False)
                                if len(build_ele.dadesTDHortInterEN.value) <= j * NombreBarresHorInt + 3  :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.ColisHorInt.value) <= j * NombreBarresHorInt + (posBarraHor - inici) *3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.PotesHorInt.value) <= j * NombreBarresHorInt + (posBarraHor - inici) *3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.ForatsHorInt.value) <= j * NombreBarresHorInt + (posBarraHor - inici) *10  + 10 :
                                    set_valors_hor_ini(build_ele, j, j * NombreBarresHorInt + (posBarraHor - inici) *10  + 10)
                                if len(build_ele.FemellesHorInt.value) <= j * NombreBarresHorInt + (posBarraHor - inici) *3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor-inici)
                                if len(build_ele.FemellesHorIntAux.value) <= j*20+ ((posBarraHor - inici + 2)*4 )+ 3 :
                                    set_valors_hor_femelles2(build_ele, j, posBarraHor-inici)
                                if len(build_ele.EncaixHorInt.value) <= j * NombreBarresHorInt + (posBarraHor - inici) *3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)


                                colis = [build_ele.ColisHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 0],
                                            build_ele.ColisHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 1],
                                            build_ele.ColisHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 2]]
                                potes = [build_ele.PotesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 0],
                                            build_ele.PotesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 1],
                                            build_ele.PotesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 2]]
                                forats = [build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 0],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 1],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 2],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 3],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 4],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 5],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 6],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 7],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 8],
                                        build_ele.ForatsHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *10 + 9]]
                                femelles = [build_ele.FemellesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 0],
                                            build_ele.FemellesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 1],
                                            build_ele.FemellesHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 2]]
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 0],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 1],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 2],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 3]  ]
                                encaixos = [build_ele.EncaixHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 0],
                                            build_ele.EncaixHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 1],
                                            build_ele.EncaixHorInt.value[j * NombreBarresHorInt + (posBarraHor - inici) *3 + 2]]

                                for nBarraVertical in range(0, len(build_ele.dadesTDVertEN.value)):
                                    #print(str(build_ele.dadesTDVertEN.value[nBarraVertical].BarraInferior) + "== 'Tub " + str(posBarraHor)+"'")
                                    #print(str(build_ele.dadesTDVertEN.value[nBarraVertical].BarraSuperior) + "== 'Tub " + str(posBarraHor)+"'")
                                    if build_ele.dadesTDVertEN.value[nBarraVertical].BarraInferior == "Tub " +str(posBarraHor):#Numeracio malament #+ str(j*(posBarraHor - inici)):
                                        pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 +0.5
                                        pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2

                                        if NBarraInici != 0:
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple) - ( build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2)
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple)
                                        else:
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple) + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple + (build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2)
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs

                                        orientInfA =  "Esq"
                                        desplY = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplYAbs
                                        desplYInf = build_ele.dadesTDHortInterEN.value[posBarraHor].desplY
                                        puntCentralY = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 + desplY
                                        puntCentralYInf = build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + desplYInf

                                        Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple - 2.0
                                        Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2
                                        if Ample_forat_femella >= 15:
                                            Ample_forat_femella = 15

                                        posFemellaY = puntCentralY - puntCentralYInf + Ample_forat_femella
                                        if build_ele.dadesTDVertEN.value[nBarraVertical].EncaixInf:
                                            orientInfA =  "Esq"
                                            if Ample_forat_femella< 15:
                                                posFemellaY = desplY - desplYInf + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 -  Ample_forat_femella/2
                                            else:
                                                posFemellaY = puntCentralY - puntCentralYInf + Ample_forat_femella/2
                                                posFemellaY = desplY - desplYInf + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 - Ample_forat_femella/2
                                            if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                                                if desplY - desplYInf == 0:
                                                    posFemellaY = 0.1
                                                else:

                                                    posFemellaY = desplY - desplYInf
                                                Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura - 2
                                                Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2
                                                if Ample_forat_femella >= 15:
                                                    Ample_forat_femella = 15
                                        else:
                                            desplY = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplYAbs
                                            desplYInf = build_ele.dadesTDHortInterEN.value[posBarraHor].desplY
                                            puntCentralY = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 + desplY
                                            puntCentralYInf = build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + desplYInf
                                            posFemellaY = 0.0

                                            if (puntCentralY > puntCentralYInf) :
                                                orientInfA = "Sup"
                                            else:
                                                orientInfA = "Inf"

                                        if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                                            pos = pos + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - Ample_forat_femella/2
                                        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Ample_forat_femella tubGirat')
                                        bob = TDHorCollection(Femella = build_ele.dadesTDVertEN.value[nBarraVertical].MostrarTDVertical and build_ele.dadesTDVertEN.value[nBarraVertical].FemellaInf,
                                                            FemellaOr = orientInfA,
                                                            PosFemellaX = pos,
                                                            PosFemellaY = posFemellaY,
                                                            Separacio_forat_femella = Separacio_forat_femella,
                                                            Ample_forat_femella = Ample_forat_femella,
                                                            tubGirat = build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv)
                                        femelles.append(bob)
                                        orientInv = getOrientacioInv(orientInfA)
                                        bob = bob._replace(FemellaOr = orientInv)
                                        femelles.append(bob)
                                    #if build_ele.dadesTDVertEN.value[nBarraVertical].BarraSuperior == "Tub " + str(j) + "."+ str(posBarraHor - inici+1):
                                    if build_ele.dadesTDVertEN.value[nBarraVertical].BarraSuperior == "Tub " + str(posBarraHor):#Numeracio Malament #+ str(j*(posBarraHor - inici)):
                                        pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2 -0.5
                                        pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2 -0.5
                                        pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2


                                        if NBarraInici != 0:
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple) - ( build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2)
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple)
                                        else:
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple) + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple + (build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2)
                                            pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs


                                        desplY = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplYAbs
                                        desplYSup = build_ele.dadesTDHortInterEN.value[posBarraHor].desplY
                                        puntCentralY = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 + desplY
                                        puntCentralYSup = build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + desplYSup
                                        Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple - 2.0
                                        Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2
                                        if Ample_forat_femella >= 15:
                                            Ample_forat_femella = 15

                                        orientSupA =  "Dre"
                                        posFemellaY = puntCentralY - puntCentralYSup + Ample_forat_femella
                                        if build_ele.dadesTDVertEN.value[nBarraVertical].EncaixSup:
                                            orientSupA =  "Dre"
                                            if Ample_forat_femella< 15:
                                                posFemellaY = puntCentralY - puntCentralYSup + Ample_forat_femella
                                            else:
                                                posFemellaY = puntCentralY - puntCentralYSup + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 - Ample_forat_femella
                                                posFemellaY = desplY - desplYSup + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 - Ample_forat_femella/2
                                            if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                                                if desplY - desplYSup == 0:
                                                    posFemellaY = 0.1
                                                else:
                                                    posFemellaY = desplY - desplYSup
                                                Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura - 2
                                                Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2
                                                if Ample_forat_femella >= 15:
                                                    Ample_forat_femella = 15

                                        else:
                                            desplY = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplYAbs
                                            desplYSup = build_ele.dadesTDHortInterEN.value[posBarraHor].desplY
                                            puntCentralY = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 + desplY
                                            puntCentralYSup = build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + desplYSup
                                            posFemellaY = 0.0
                                            if (puntCentralY > puntCentralYSup) :
                                                orientSupA = "Sup"
                                            else:
                                                orientSupA = "Inf"

                                        '''
                                        if orientacio == "Sup" or orientacio == "Inf":
                                            posY = 0
                                        else:
                                            if barraInici == "Inferior" and orientacio == "Dre":
                                                posY = Altura/2 - 15/2 + desply - build_ele.desplYI.value + desplAct - build_ele.listDesplVerticalsEN.value[j].desplY - build_ele.dadesTDHortInterEN.value[barraSupHor].desplY
                                            else:
                                                if orientacio == "Esq":
                                                    posY = Altura/2 - 15/2 + desply  - desplAct - build_ele.listDesplVerticalsEN.value[j].desplY #- build_ele.dadesTDHortInterEN.value
                                                else:
                                                    posY = Altura/2 - 15/2 + desply   - build_ele.listDesplVerticalsEN.value[j].desplY - build_ele.dadesTDHortInterEN.value[barraSupHor].desplY
                                        '''


                                        if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                                            pos = pos + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - Ample_forat_femella/2
                                        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Ample_forat_femella tubGirat')
                                        bob = TDHorCollection(Femella = build_ele.dadesTDVertEN.value[nBarraVertical].MostrarTDVertical and build_ele.dadesTDVertEN.value[nBarraVertical].FemellaSup,
                                                            FemellaOr = orientSupA,
                                                            PosFemellaX = pos,
                                                            PosFemellaY = posFemellaY,
                                                            Separacio_forat_femella = Separacio_forat_femella,
                                                            Ample_forat_femella = Ample_forat_femella,
                                                            tubGirat = build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv)
                                        femelles.append(bob)
                                        orientInv = getOrientacioInv(orientSupA)
                                        bob = bob._replace(FemellaOr = orientInv)
                                        femelles.append(bob)

                                """
                                for nForat in range(0,len(forats)):
                                    if forats[nForat].Forat and forats[nForat].MostrarBox and build_ele.BarresHorListEN.value[posBarraHor].BarraHor:
                                        group_elems.append(createBoxForatHorInt(build_ele, posBarraHor, forats,j,nForat))
                                """

                                vermellHor = build_ele.dadesTDHortInterEN.value[posBarraHor].FounColor
                                if build_ele.dadesTDHortInterEN.value[posBarraHor].vermell:
                                    vermellHor = 6

                                tableAux = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura,llargada, build_ele.dadesTDHortInterEN.value[posBarraHor].Gruix,#DistanciaEntreEN(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreEN), BarraGruix,
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].IsUseGlobalProp, vermellHor, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].Ample_forat_femella, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura_forat_femella, build_ele.dadesTDHortInterEN.value[posBarraHor].Separacio_forat_femella,
                                                        femelles, #Femelles, #matriu
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].posicio_centre_masses, #posicio_centre_masses,
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].IsFirstCancam, build_ele.dadesTDHortInterEN.value[posBarraHor].Dis1cancam, #IsFirstCancam, Dis1cancam,
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].IsSecondCancam, build_ele.dadesTDHortInterEN.value[posBarraHor].Dis2cancam, #IsSecondCancam, Dis2cancam,
                                                        build_ele.dadesTDHortInterEN.value[posBarraHor].PestanyaSup, build_ele.dadesTDHortInterEN.value[posBarraHor].PestanyaInf,#PestanyaSuperior, PestanyaInferior,
                                                        encaixos,build_ele.dadesTDHortInterEN.value[posBarraHor].pestanyesInv) #EncaixosPar))

                                if not tableAux.is_valid():
                                    return[]


                                posInici = build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs


                                matrix_Aux = AllplanGeo.Matrix3D()
                                if build_ele.BarresHorListEN.value[posBarraHor].Orientacio == 'Inf' and not build_ele.BarresHorListEN.value[posBarraHor].AutoLongitud :
                                    #matrix_Aux.SetValue(12, matrix[12] + build_ele.listDesplVerticalsEN.value[j].desplX - llargada - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX  + build_ele.listDesplVerticalsEN.value[j].desplX  )
                                    #matrix_Aux.SetValue(12, build_ele.listDesplVerticalsEN.value[j].desplXAbs - build_ele.dadesTDVertEN.value[j].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 2 - llargada)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)

                                    matrix_Aux.SetValue(12, posInici - build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 1.5 - llargada)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)
                                    matrix_Aux.SetValue(12, posInici )#+ build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 1.5 - llargada)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)

                                else:
                                    #matrix_Aux.SetValue(12, matrix[12] + build_ele.listDesplVerticalsEN.value[j].desplX + build_ele.dadesTDVertEN.value[j].BarraAmple - build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)
                                    #matrix_Aux.SetValue(12, build_ele.listDesplVerticalsEN.value[j].desplXAbs + build_ele.dadesTDVertEN.value[j].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 2)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)
                                    if NBarraInici == 0:
                                        matrix_Aux.SetValue(12, posInici + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)#/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 1.5)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)
                                    else:
                                        matrix_Aux.SetValue(12, posInici + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple + build_ele.dadesTDVertEN.value[0].BarraAmple + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)# + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 1.5)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)

                                matrix_Aux.SetValue(13, build_ele.dadesTDHortInterEN.value[posBarraHor].desplY)
                                #matrix_Aux.SetValue(13, matrix[13] + build_ele.dadesTDHortInterEN.value[posBarraHor].desplY)
                                #if build_ele.desplYI.value == 0 or not build_ele.EncaixHorInf.value:

                                if not build_ele.EncaixHorInf.value:
                                    matrix_Aux.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value )#- build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2 -1 )
                                else:
                                    matrix_Aux.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value)#- build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2 -1 )


                                # contadorPPI += 1

                                '''

                                if posBarraHor >= len(build_ele.BarresAdjListEN.value) or posBarraHor >= len(build_ele.dadesAdj.value):
                                    set_valors_Adjacents(build_ele,posBarraHor)


                                if build_ele.BarresHorListEN.value[posBarraHor].Edit and nVer==j and build_ele.BarresAdjListToShowEN.value[0].Save:
                                    guardar_valors_adjacents(build_ele, posBarraHor)
                                    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Save = False)
                                elif build_ele.BarresHorListEN.value[posBarraHor].Edit and nVer==j and build_ele.BarresAdjListToShowEN.value[0].Edit:
                                    mostrar_valors_adjacents(build_ele, posBarraHor)
                                    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Edit = False)

                                if build_ele.BarresAdjListEN.value[posBarraHor].BarraAdj:
                                    #--------CREATE HORITZONTAL--------- POSAR DADES MATRIUS [0]


                                    if len(build_ele.dadesTDVertInter.value) <= j :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.BarresAdjListEN.value) <= posBarraHor :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.ColisAdj.value) <= (posBarraHor) * 4 :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.PotesAdj.value) <= (posBarraHor) * 4 :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.ForatsAdj.value) <= (posBarraHor) * 4 :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.FemellesAdj.value) <= (posBarraHor) * 4 :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.EncaixAdj.value) <= (posBarraHor) * 4 :
                                        set_valors_Adjacents(build_ele, posBarraHor)


                                    colis = [build_ele.ColisAdj.value[posBarraHor * 3 +  0],
                                            build_ele.ColisAdj.value[posBarraHor * 3  + 1],
                                            build_ele.ColisAdj.value[posBarraHor * 3  + 2]]
                                    potes = [build_ele.PotesAdj.value[posBarraHor * 3  + 0],
                                                build_ele.PotesAdj.value[posBarraHor * 3  + 1],
                                                build_ele.PotesAdj.value[posBarraHor * 3  + 2]]
                                    forats = [build_ele.ForatsAdj.value[posBarraHor * 3  + 0],
                                                build_ele.ForatsAdj.value[posBarraHor * 3  + 1],
                                                build_ele.ForatsAdj.value[posBarraHor * 3  + 2]]
                                    femelles = [build_ele.FemellesAdj.value[posBarraHor * 3  + 0],
                                                build_ele.FemellesAdj.value[posBarraHor * 3  + 1],
                                                build_ele.FemellesAdj.value[posBarraHor * 3  + 2]]
                                    encaixos = [build_ele.EncaixAdj.value[posBarraHor * 3  + 0],
                                                build_ele.EncaixAdj.value[posBarraHor * 3  + 1],
                                                build_ele.EncaixAdj.value[posBarraHor * 3  + 2]]

                                    if  build_ele.BarresAdjListEN.value[posBarraHor].Longitud <= 0:
                                        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Orientacio = 'Dre')
                                        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Longitud = 100)

                                    if len(build_ele.dadesTDVertInter.value) > posBarraHor:
                                        separacioFemellaNovaInf = build_ele.dadesTDVertInter.value[posBarraHor].BarraAmple
                                    else:
                                        separacioFemellaNovaInf = 30


                                    novaHor = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura,build_ele.BarresAdjListEN.value[posBarraHor].Longitud, build_ele.dadesTDHortInterEN.value[posBarraHor].Gruix,#DistanciaEntreEN(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreEN), BarraGruix,
                                                        build_ele.dadesAdj.value[posBarraHor].IsUseGlobalProp, build_ele.dadesAdj.value[posBarraHor].FounColor, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                                        TDV_Int.Ample_forat_femella,TDV_Int.Altura_forat_femella,30,
                                                        femelles, #Femelles, #matriu
                                                        build_ele.dadesAdj.value[posBarraHor].posicio_centre_masses, #posicio_centre_masses,
                                                        build_ele.dadesAdj.value[posBarraHor].IsFirstCancam, build_ele.dadesAdj.value[posBarraHor].Dis1cancam, #IsFirstCancam, Dis1cancam,
                                                        build_ele.dadesAdj.value[posBarraHor].IsSecondCancam, build_ele.dadesAdj.value[posBarraHor].Dis2cancam, #IsSecondCancam, Dis2cancam,
                                                        False, False,#build_ele.dadesAdj.value[posBarraHor].pestanyaSup, build_ele.dadesAdj.value[posBarraHor].pestanyaInf,#PestanyaSuperior, PestanyaInferior,
                                                        encaixos) #EncaixosPar))


                                    novaHor_brep = novaHor.create()
                                    novaHor_common_props = novaHor.get_common_props()


                                    build_ele.DENHorInt.value = "T"
                                    atrENEsp = definirAtributPers(build_ele,posBarraHor,"TubHoritzontal")
                                    if atrENEsp == "Xapa Frontal":
                                        build_ele.DENHorInt.value = "X"
                                    if build_ele.reconeixerDen.value:
                                        tubEsIgual, DEN = compare_attributes(build_ele, doc, novaHor)
                                        if (tubEsIgual):
                                            build_ele.DENHorInt.value = DEN

                                    cara_a, cara_a1, cara_a2 = dividirAtribut(str(novaHor.get_codi_cara_a()) )
                                    cara_b, cara_b1, cara_b2 = dividirAtribut(str(novaHor.get_codi_cara_b()) )
                                    cara_c, cara_c1, cara_c2 = dividirAtribut(str(novaHor.get_codi_cara_c()) )
                                    cara_d, cara_d1, cara_d2 = dividirAtribut(str(novaHor.get_codi_cara_d()) )

                                    cara_e, cara_e1, cara_e2 = dividirAtribut(str(novaHor.get_codi_cara_a_inv()) )
                                    cara_f, cara_f1, cara_f2 = dividirAtribut(str(novaHor.get_codi_cara_b_inv()) )
                                    cara_g, cara_g1, cara_g2 = dividirAtribut(str(novaHor.get_codi_cara_c_inv()) )
                                    cara_h, cara_h1, cara_h2 = dividirAtribut(str(novaHor.get_codi_cara_d_inv()) )

                                    novaHor_attr_list = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value),

                                                        AllplanBaseElements.AttributeString(2108,  cara_a),
                                                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                                                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                                                        AllplanBaseElements.AttributeString(2047,  cara_b),
                                                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                                                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                                                        AllplanBaseElements.AttributeString(2110,  cara_c),
                                                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                                                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                                                        AllplanBaseElements.AttributeString(2120,  cara_d),
                                                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                                                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                                                        AllplanBaseElements.AttributeString(2121,  cara_e),
                                                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                                                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                                                        AllplanBaseElements.AttributeString(2122,  cara_f),
                                                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                                                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                                                        AllplanBaseElements.AttributeString(2128,  cara_g),
                                                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                                                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                                                        AllplanBaseElements.AttributeString(2129,  cara_h),
                                                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                                                        AllplanBaseElements.AttributeString(2509,  cara_h2),


                                                        AllplanBaseElements.AttributeString(2446, novaHor.get_codi_pota_inv()),

                                                        AllplanBaseElements.AttributeString(1947, atrENEsp),

                                                        AllplanBaseElements.AttributeString(2430, novaHor.get_codi_pestanyes()),
                                                        AllplanBaseElements.AttributeString(2435, novaHor.get_codi_cancam()),
                                                        AllplanBaseElements.AttributeString(2431, novaHor.get_codi_mesures()),
                                                        AllplanBaseElements.AttributeString(2433, novaHor.get_codi_pota()),
                                                        AllplanBaseElements.AttributeString(2445, novaHor.get_seccio()),
                                                        AllplanBaseElements.AttributeString(220, novaHor.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2103, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(508, "EN")]
                                    novaHor_views = [View2D3D ([AllplanBasisElements.ModelElement3D(novaHor_common_props, novaHor_brep)])]


                                    matrix_Adj = AllplanGeo.Matrix3D()
                                    matrix_Adj.SetValue(12, matrix_Aux[12] + build_ele.BarresAdjListEN.value[posBarraHor].Posicio)
                                    matrix_Adj.SetValue(13, matrix_Aux[13])
                                    matrix_Adj.SetValue(14, matrix_Aux[14])

                                    reOrinetacio = ""
                                    if build_ele.BarresAdjListEN.value[posBarraHor].Orientacio == 'Esq' :
                                        matrix_Adj.SetValue(13, matrix_Aux[13] + build_ele.dadesTDHortInterEN.value[posBarraHor].Ample - build_ele.BarresAdjListEN.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Inf"
                                    elif build_ele.BarresAdjListEN.value[posBarraHor].Orientacio == 'Sup' :
                                        matrix_Adj.SetValue(14, matrix_Aux[14] + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura - build_ele.BarresAdjListEN.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Esq"
                                    elif build_ele.BarresAdjListEN.value[posBarraHor].Orientacio == 'Dre' :
                                        matrix_Adj.SetValue(13, matrix_Aux[13] - build_ele.dadesTDHortInterEN.value[posBarraHor].Ample + build_ele.BarresAdjListEN.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Sup"
                                    elif build_ele.BarresAdjListEN.value[posBarraHor].Orientacio == 'Inf' :
                                        matrix_Adj.SetValue(14, matrix_Aux[14] - build_ele.dadesTDHortInterEN.value[posBarraHor].Altura + build_ele.BarresAdjListEN.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Dre"
                                    else:
                                        print("no hauria d'entrar aqui")

                                    listEncaixAdj = []
                                    TDCollection = collections.namedtuple('StirrupList', 'BarraFront Orientacio Longitud Amplitud Posicio Profunditat Pestanya Separator')
                                    bob = TDCollection( BarraFront = build_ele.BarresAdjListEN.value[posBarraHor].BarraAdj,
                                                        Orientacio = reOrinetacio,
                                                        Longitud = build_ele.BarresAdjListEN.value[posBarraHor].Longitud,
                                                        Amplitud = build_ele.dadesTDHortInterEN.value[posBarraHor].Ample,
                                                        Posicio = build_ele.BarresAdjListEN.value[posBarraHor].Posicio + build_ele.BarresAdjListEN.value[posBarraHor].Longitud/2,
                                                        Profunditat = build_ele.BarresAdjListEN.value[posBarraHor].Profunditat,
                                                        Pestanya = False,
                                                        Separator = '')
                                    if build_ele.BarresAdjListEN.value[posBarraHor].Profunditat > 0:
                                        listEncaixAdj.append(bob)

                                    tableAux.afegir_encaixos_frontals(listEncaixAdj,[],False)


                                    horitzontalPPOBject4 = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura+10,build_ele.BarresAdjListEN.value[posBarraHor].Longitud, 0,#DistanciaEntreEN(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreEN), BarraGruix,
                                                        False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                    horitzontalPPOBject4Recess = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura+10,build_ele.BarresAdjListEN.value[posBarraHor].Longitud, 0,#DistanciaEntreEN(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreEN), BarraGruix,
                                                        False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])

                                    horitzontalPPOBject4_brep2 = horitzontalPPOBject4.create()
                                    horitzontalPPOBject4_common_props = horitzontalPPOBject4.get_common_props()
                                    horitzontalPPOBject4_brep2Recess = horitzontalPPOBject4Recess.create()
                                    horitzontalPPOBject4_common_propsRecess = horitzontalPPOBject4Recess.get_common_props()

                                    horitzontal_views_object4 = [View2D3D ([AllplanBasisElements.ModelElement3D(horitzontalPPOBject4_common_props, horitzontalPPOBject4_brep2)])]
                                    horitzontal_views_object4Recess = [View2D3D ([AllplanBasisElements.ModelElement3D(horitzontalPPOBject4_common_propsRecess, horitzontalPPOBject4_brep2Recess)])]

                                    TranslationFather = matrix_Adj
                                    TranslationFather.SetValue(12, placement_mat[12] + matrix_Adj[12])
                                    TranslationFather.SetValue(13, placement_mat[13] + matrix_Adj[13])
                                    TranslationFather.SetValue(14, placement_mat[14] + matrix_Adj[14])
                                    matrix_Adj  = TranslationFather


                                    matrix_AdjC = AllplanGeo.Matrix3D()
                                    matrix_AdjC.SetValue(12, matrix_Adj[12])
                                    matrix_AdjC.SetValue(13, matrix_Adj[13])
                                    matrix_AdjC.SetValue(14, matrix_Adj[14]-5)

                                    if matrix_Adj[12]< build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value:
                                        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4.get_params_list(),
                                        #                hash_value = horitzontalPPOBject4.hash(), python_file = horitzontalPPOBject4.filename(),
                                        #                views = horitzontal_views_object4, matrix = matrix_AdjC, common_props = horitzontalPPOBject4_common_props, attribute_list = table_attr_listObject))
                                        #group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4.get_params_list(),
                                        #                hash_value = horitzontalPPOBject4.hash(), python_file = horitzontalPPOBject4.filename(),
                                        #                views = horitzontal_views_object4, matrix = matrix_AdjC, common_props = horitzontalPPOBject4_common_props, attribute_list = table_attr_listObject))
                                        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4Recess.get_params_list(),
                                                        hash_value = horitzontalPPOBject4Recess.hash(), python_file = horitzontalPPOBject4Recess.filename(),
                                                        views = horitzontal_views_object4Recess, matrix = matrix_AdjC, common_props = horitzontalPPOBject4_common_propsRecess, attribute_list = table_attr_listObject))
                                        group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4Recess.get_params_list(),
                                                        hash_value = horitzontalPPOBject4Recess.hash(), python_file = horitzontalPPOBject4Recess.filename(),
                                                        views = horitzontal_views_object4Recess, matrix = matrix_AdjC, common_props = horitzontalPPOBject4_common_propsRecess, attribute_list = table_attr_listObject))

                                        group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = novaHor.get_params_list(),
                                                                    hash_value = novaHor.hash(), python_file = novaHor.filename(),
                                                                    views = novaHor_views, matrix = matrix_Adj, common_props = novaHor_common_props, attribute_list = novaHor_attr_list))
                                        group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = novaHor.get_params_list(),
                                                                    hash_value = novaHor.hash(), python_file = novaHor.filename(),
                                                                    views = novaHor_views, matrix = matrix_Adj, common_props = novaHor_common_props, attribute_list = novaHor_attr_list))

                                        punt_central = matrix_Adj[12] + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Adj[12], matrix_Adj[13] + build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2, matrix_Adj[14] + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura, build_ele.BarresAdjListEN.value[posBarraHor].Longitud, True, pointUbi)
                                        group_elems.append(polyhedronCentral)
                                        group_elems_preview.append(polyhedronCentral)

                                '''



                                table_brepAux = tableAux.create()
                                common_propsHor = AllplanBaseElements.CommonProperties()
                                common_propsHor = tableAux.get_common_props()
                                if testEditBarraHorInterior:
                                    common_propsHor.Color = vermellHor #Vermell
                                    #handle_list = tableAux.create_handles()

                                build_ele.DENHorInt.value = "T "
                                atrENEsp = definirAtributPers(build_ele,posBarraHor,"TubHoritzontal")
                                if atrENEsp == "Xapa Frontal":
                                    build_ele.DENHorInt.value = "X"
                                if build_ele.reconeixerDen.value:
                                    tubEsIgual, DEN = compare_attributes(build_ele, doc, tableAux)
                                    if (tubEsIgual):
                                        build_ele.DENHorInt.value = DEN


                                cara_a, cara_a1, cara_a2 = dividirAtribut(str(tableAux.get_codi_cara_a()) )
                                cara_b, cara_b1, cara_b2 = dividirAtribut(str(tableAux.get_codi_cara_b()) )
                                cara_c, cara_c1, cara_c2 = dividirAtribut(str(tableAux.get_codi_cara_c()) )
                                cara_d, cara_d1, cara_d2 = dividirAtribut(str(tableAux.get_codi_cara_d()) )

                                cara_e, cara_e1, cara_e2 = dividirAtribut(str(tableAux.get_codi_cara_a_inv()) )
                                cara_f, cara_f1, cara_f2 = dividirAtribut(str(tableAux.get_codi_cara_b_inv()) )
                                cara_g, cara_g1, cara_g2 = dividirAtribut(str(tableAux.get_codi_cara_c_inv()) )
                                cara_h, cara_h1, cara_h2 = dividirAtribut(str(tableAux.get_codi_cara_d_inv()) )

                                table_attr_listAux = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value),

                                                        AllplanBaseElements.AttributeString(2108,  cara_a),
                                                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                                                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                                                        AllplanBaseElements.AttributeString(2047,  cara_b),
                                                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                                                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                                                        AllplanBaseElements.AttributeString(2110,  cara_c),
                                                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                                                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                                                        AllplanBaseElements.AttributeString(2120,  cara_d),
                                                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                                                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                                                        AllplanBaseElements.AttributeString(2121,  cara_e),
                                                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                                                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                                                        AllplanBaseElements.AttributeString(2122,  cara_f),
                                                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                                                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                                                        AllplanBaseElements.AttributeString(2128,  cara_g),
                                                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                                                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                                                        AllplanBaseElements.AttributeString(2129,  cara_h),
                                                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                                                        AllplanBaseElements.AttributeString(2509,  cara_h2),


                                                        AllplanBaseElements.AttributeString(2446, tableAux.get_codi_pota_inv()),#

                                                        AllplanBaseElements.AttributeString(1947, atrENEsp),#

                                                        AllplanBaseElements.AttributeString(2430, tableAux.get_codi_pestanyes()),
                                                        AllplanBaseElements.AttributeString(2435, tableAux.get_codi_cancam()),
                                                        AllplanBaseElements.AttributeString(2431, tableAux.get_codi_mesures()),
                                                        AllplanBaseElements.AttributeString(2433, tableAux.get_codi_pota()),
                                                        AllplanBaseElements.AttributeString(2445, tableAux.get_seccio()),#
                                                        AllplanBaseElements.AttributeString(220, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2455, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2103, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(1083, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(1084, tableAux.get_seccio()),
                                                        AllplanBaseElements.AttributeString(1085, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(1087, "Horitzontal"),
                                                        AllplanBaseElements.AttributeString(508, "EN")]
                                table_viewsAux = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsHor, table_brepAux)])]


                                horitzontalPPOBject3 = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample + 2, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura+6,llargada, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                horitzontalPPOBject3Recess = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample + 2 , build_ele.dadesTDHortInterEN.value[posBarraHor].Altura+6,llargada, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                horitzontal_BrepObject3 = horitzontalPPOBject3.create()
                                horitzontal_views_object3 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject3)])]
                                horitzontal_BrepObject3Recess = horitzontalPPOBject3Recess.create()
                                horitzontal_views_object3Recess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObject3Recess)])]

                                TranslationFather = matrix_Aux
                                TranslationFather.SetValue(12, placement_mat[12] + matrix_Aux[12])
                                TranslationFather.SetValue(13, placement_mat[13] + matrix_Aux[13])
                                TranslationFather.SetValue(14, placement_mat[14] + matrix_Aux[14])
                                matrix_Aux  = TranslationFather

                                matrix_AuxC = AllplanGeo.Matrix3D()
                                matrix_AuxC.SetValue(12, matrix_Aux[12])
                                matrix_AuxC.SetValue(13, matrix_Aux[13] - 1)
                                matrix_AuxC.SetValue(14, matrix_Aux[14] - 3)

                                if matrix_Aux[12] - placement_mat[12]< build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value and build_ele.BarresHorListEN.value[posBarraHor].BarraHor:

                                    #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3.get_params_list(),
                                    #                    hash_value = horitzontalPPOBject3.hash(), python_file = horitzontalPPOBject3.filename(),
                                    #                    views = horitzontal_views_object3, matrix = matrix_AuxC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                                    #group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3.get_params_list(),
                                    #                    hash_value = horitzontalPPOBject3.hash(), python_file = horitzontalPPOBject3.filename(),
                                    #                    views = horitzontal_views_object3, matrix = matrix_AuxC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                                    group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3Recess.get_params_list(),
                                                        hash_value = horitzontalPPOBject3Recess.hash(), python_file = horitzontalPPOBject3Recess.filename(),
                                                        views = horitzontal_views_object3Recess, matrix = matrix_AuxC, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))
                                    group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3Recess.get_params_list(),
                                                        hash_value = horitzontalPPOBject3Recess.hash(), python_file = horitzontalPPOBject3Recess.filename(),
                                                        views = horitzontal_views_object3Recess, matrix = matrix_AuxC, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))


                                    group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = tableAux.get_params_list(),
                                                            hash_value = tableAux.hash(), python_file = tableAux.filename(),
                                                            views = table_viewsAux, matrix = matrix_Aux, common_props = common_propsHor, attribute_list = table_attr_listAux))
                                    group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = tableAux.get_params_list(),
                                                            hash_value = tableAux.hash(), python_file = tableAux.filename(),
                                                            views = table_viewsAux, matrix = matrix_Aux, common_props = common_propsHor, attribute_list = table_attr_listAux))


                                    if build_ele.dadesTDHortInterEN.value[posBarraHor].mostrarLiniaVertA:
                                        punt_central = matrix_Aux[12] + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12], matrix_Aux[13] + build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplLinA, matrix_Aux[14] + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
                                        if (len(build_ele.dadesTDHortInterEN.value[posBarraHor].linia) > 1):
                                            linia = build_ele.dadesTDHortInterEN.value[posBarraHor].linia[len(build_ele.dadesTDHortInterEN.value[posBarraHor].linia)-1]
                                        else:
                                            build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(linia = "Tipus 1")
                                            linia = "1"
                                        if (len(build_ele.dadesTDHortInterEN.value[posBarraHor].layer) > 1):
                                            layer = build_ele.dadesTDHortInterEN.value[posBarraHor].layer
                                        else:
                                            build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(layer = "EN_FIXACIO_X")
                                            layer = "EN_FIXACIO_X"
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura, llargada, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                                        if polyhedronCentral != []:
                                            group_elems.append(polyhedronCentral[0])
                                            group_elems_preview.append(polyhedronCentral[0])
                                            group_elems.append(polyhedronCentral[3])
                                            group_elems_preview.append(polyhedronCentral[3])
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                    if build_ele.dadesTDHortInterEN.value[posBarraHor].mostrarLiniaVertB:
                                        punt_central = matrix_Aux[12] + build_ele.dadesTDHortInterEN.value[posBarraHor].desplX + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12], matrix_Aux[13] + build_ele.dadesTDHortInterEN.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInterEN.value[posBarraHor].desplLinB, matrix_Aux[14] + build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
                                        if (len(build_ele.dadesTDHortInterEN.value[posBarraHor].linia) > 1):
                                            linia = build_ele.dadesTDHortInterEN.value[posBarraHor].linia[len(build_ele.dadesTDHortInterEN.value[posBarraHor].linia)-1]
                                        else:
                                            build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(linia = "Tipus 1")
                                            linia = "1"
                                        if (len(build_ele.dadesTDHortInterEN.value[posBarraHor].layer) > 1):
                                            layer = build_ele.dadesTDHortInterEN.value[posBarraHor].layer
                                        else:
                                            build_ele.dadesTDHortInterEN.value[posBarraHor] = build_ele.dadesTDHortInterEN.value[posBarraHor]._replace(layer = "EN_FIXACIO_X")
                                            layer = "EN_FIXACIO_X"
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura, llargada, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                                        if polyhedronCentral != []:
                                            group_elems.append(polyhedronCentral[0])
                                            group_elems_preview.append(polyhedronCentral[0])
                                            group_elems.append(polyhedronCentral[3])
                                            group_elems_preview.append(polyhedronCentral[3])
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))

                                    if build_ele.MostrarTDNums.value:
                                        numHor = create_num_on_view_Hor(build_ele, posBarraHor, matrix_Aux)
                                        group_elems_preview.append(numHor)


                                contadorPPI += 1


                except Exception as e:
                    print("no s'ha creat Horitzontal [hor - "+ str(posBarraHor)+ "]:", e)


                #if (build_ele.desplYI.value != 0 or build_ele.EncaixHorInf.value) and not build_ele.invertirEncaixInf.value:
                if  build_ele.EncaixHorInf.value and not build_ele.invertirEncaixInf.value:
                    print("set femelles false")
                    horitzontalPPInf.set_false_femelles()
                    #for pphor in listHoritzontalPP:
                    #    pphor.set_false_femelles()
                #if build_ele.desplYS.value != 0 and not build_ele.invertirEncaixSup.value:
                if build_ele.EncaixHorSup.value and not build_ele.invertirEncaixSup.value:
                    if build_ele.TubSuperior.value == "EXD" or build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior":
                        horitzontalPPSup.set_false_femelles()


                #print(j)
                TDV_Int_brep = TDV_Int.create()
                common_propsVert = TDV_Int.get_common_props()
                inici = build_ele.nListBarresHor.value[j].Posicio
                final = build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal
                testEditBarraHorInterior = False
                testEditBarraVertInterior = False
                for posBarraHor in range(0, len(build_ele.BarresHorListEN.value)-1):#recorrer totes les Barres Horitzontals de cada vertical
                    if build_ele.BarresHorListEN.value[posBarraHor].Edit:
                        testEditBarraHorInterior = True
                for i in range(0,len(build_ele.BarresVertListToShow.value)):
                    if build_ele.BarresVertListToShow.value[i].Edit:
                        testEditBarraVertInterior = True

                build_ele.DENVert.value = "T "
                if build_ele.reconeixerDen.value:
                    tubEsIgual, DEN = compare_attributes(build_ele, doc, TDV_Int)
                    if (tubEsIgual):
                        build_ele.DENVert.value = DEN

                cara_a, cara_a1, cara_a2 = dividirAtribut(str(TDV_Int.get_codi_cara_a()) )
                cara_b, cara_b1, cara_b2 = dividirAtribut(str(TDV_Int.get_codi_cara_b()) )
                cara_c, cara_c1, cara_c2 = dividirAtribut(str(TDV_Int.get_codi_cara_c()) )
                cara_d, cara_d1, cara_d2 = dividirAtribut(str(TDV_Int.get_codi_cara_d()) )

                cara_e, cara_e1, cara_e2 = dividirAtribut(str(TDV_Int.get_codi_cara_a_inv()) )
                cara_f, cara_f1, cara_f2 = dividirAtribut(str(TDV_Int.get_codi_cara_b_inv()) )
                cara_g, cara_g1, cara_g2 = dividirAtribut(str(TDV_Int.get_codi_cara_c_inv()) )
                cara_h, cara_h1, cara_h2 = dividirAtribut(str(TDV_Int.get_codi_cara_d_inv()) )

                if  mostrarActual == "ENV"+str(j) and not testEditBarraVertInterior and not testEditBarraHorInterior and nVer == j:
                    common_propsVert.Color = vermellVert #Vermell
                    #handle_list = TDV_Int.create_handles()

                atrENEsp = definirAtributPers(build_ele,j,"TubVertical")
                TDV_Int_attr_list = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value),

                                        AllplanBaseElements.AttributeString(2108,  cara_a),
                                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                                        AllplanBaseElements.AttributeString(2047,  cara_b),
                                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                                        AllplanBaseElements.AttributeString(2110,  cara_c),
                                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                                        AllplanBaseElements.AttributeString(2120,  cara_d),
                                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                                        AllplanBaseElements.AttributeString(2121,  cara_e),
                                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                                        AllplanBaseElements.AttributeString(2122,  cara_f),
                                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                                        AllplanBaseElements.AttributeString(2128,  cara_g),
                                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                                        AllplanBaseElements.AttributeString(2129,  cara_h),
                                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                                        AllplanBaseElements.AttributeString(2509,  cara_h2),


                                        AllplanBaseElements.AttributeString(2446, TDV_Int.get_codi_pota_inv()),

                                        AllplanBaseElements.AttributeString(1947, atrENEsp),

                                        AllplanBaseElements.AttributeString(2430, TDV_Int.get_codi_pestanyes()),
                                        AllplanBaseElements.AttributeString(2435, TDV_Int.get_codi_cancam()),
                                        #AllplanBaseElements.AttributeString(2432, TDV_Int.get_codi_colis()),
                                        #AllplanBaseElements.AttributeString(2429, TDV_Int.get_codi_encaix()),
                                        #AllplanBaseElements.AttributeString(2434, TDV_Int.get_codi_femella()),
                                        AllplanBaseElements.AttributeString(2431, TDV_Int.get_codi_mesures()),
                                        AllplanBaseElements.AttributeString(2433, TDV_Int.get_codi_pota()),
                                        AllplanBaseElements.AttributeString(2445, TDV_Int.get_seccio()),
                                        AllplanBaseElements.AttributeString(2455, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(220, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(1083, build_ele.DENVert.value),
                                        AllplanBaseElements.AttributeString(1084, TDV_Int.get_seccio()),
                                        AllplanBaseElements.AttributeString(1085, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(1087, "Vertical"),
                                        AllplanBaseElements.AttributeString(2103, build_ele.DENVert.value),
                                        AllplanBaseElements.AttributeString(508, "EN")]
                TDV_Ints_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsVert, TDV_Int_brep)])]

                matrixMostrar = []
                #for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                if not build_ele.ReduirTempsCarrega.value:
                    for i in range(0,build_ele.IntegerENSelector.value):
                        matrixMostrar.append(build_ele.dadesTDVertEN.value[i].MostrarTDVertical)

                if j< len(matrixMostrar):
                    if matrixMostrar[j] and matrix0[12]< build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value:

                        """
                        if build_ele.dadesTDVertEN.value[j].esProvisional:
                            group_elems.append(crear_LProvisionals(build_ele,j,matrix0))
                        """

                        vertical_BrepObject5 = verticalPPOBject5.create()
                        vertical_views_object5 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, vertical_BrepObject5)])]


                        vertical_BrepObject5Recess = verticalPPOBject5Recess.create()
                        vertical_views_object5Recess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, vertical_BrepObject5Recess)])]

                        TranslationFather = matrix0
                        TranslationFather.SetValue(12, placement_mat[12] + matrix0[12])
                        TranslationFather.SetValue(13, placement_mat[13] + matrix0[13])
                        TranslationFather.SetValue(14, placement_mat[14] + matrix0[14])
                        matrix0  = TranslationFather

                        matrix0C = AllplanGeo.Matrix3D()
                        matrix0C.SetValue(12, matrix0[12] - 3)
                        matrix0C.SetValue(13, matrix0[13] - 1)
                        matrix0C.SetValue(14, matrix0[14] )


                        #group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                        #                        hash_value = verticalPPOBject5.hash(), python_file = verticalPPOBject5.filename(),
                        #                        views = vertical_views_object5, matrix = matrix0C, common_props = common_propsObject, attribute_list = table_attr_listObject))
                        #group_elems_preview.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                        #                        hash_value = verticalPPOBject5.hash(), python_file = verticalPPOBject5.filename(),
                        #                        views = vertical_views_object5, matrix = matrix0C, common_props = common_propsObject, attribute_list = table_attr_listObject))

                        if j != 0 and j != build_ele.IntegerENSelector.value -1 :
                            group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5Recess.hash(), python_file = verticalPPOBject5Recess.filename(),
                                                    views = vertical_views_object5Recess, matrix = matrix0C, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))
                            group_elems_preview.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5Recess.hash(), python_file = verticalPPOBject5Recess.filename(),
                                                    views = vertical_views_object5Recess, matrix = matrix0C, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))

                        group_elems.append(PythonPart ("PP_EN_Vertical", parameter_list = get_var_chair_vert(build_ele, j, FemellesAux),
                                                hash_value = TDV_Int.hash(), python_file = TDV_Int.filename(),
                                                views = TDV_Ints_views, matrix = matrix0, common_props = common_propsVert, attribute_list = TDV_Int_attr_list))
                        group_elems_preview.append(PythonPart ("PP_EN_Vertical", parameter_list = get_var_chair_vert(build_ele, j, FemellesAux),
                                                hash_value = TDV_Int.hash(), python_file = TDV_Int.filename(),
                                                views = TDV_Ints_views, matrix = matrix0, common_props = common_propsVert, attribute_list = TDV_Int_attr_list))


                        if build_ele.listDesplVerticalsEN.value[j].mostrarLiniaVertA:
                            punt_central = matrix0[12] + build_ele.listDesplVerticalsEN.value[j].desplX + build_ele.dadesTDVertEN.value[j].BarraAltura/2
                            pointUbi = AllplanGeo.Point3D(matrix0[12] + build_ele.dadesTDVertEN.value[j].BarraAmple/2 + build_ele.listDesplVerticalsEN.value[j].desplLinA, matrix0[13] + build_ele.dadesTDVertEN.value[j].BarraAltura/2 , matrix0[14])
                            if (len(build_ele.dadesTDVertEN.value[j].linia)) <=1:
                                build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(linia = "Tipus 1")
                            linia = build_ele.dadesTDVertEN.value[j].linia[len(build_ele.dadesTDVertEN.value[j].linia)-1]
                            if len(build_ele.dadesTDVertEN.value[j].layer) == 0:
                                build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(layer = "EN_FIXACIO_X")
                            layer = build_ele.dadesTDVertEN.value[j].layer
                            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDVertEN.value[j].BarraAltura, BarrallargadaVert, False, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                            if polyhedronCentral != []:
                                group_elems.append(polyhedronCentral[0])
                                group_elems_preview.append(polyhedronCentral[0])
                                group_elems.append(polyhedronCentral[3])
                                group_elems_preview.append(polyhedronCentral[3])
                                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                        if build_ele.listDesplVerticalsEN.value[j].mostrarLiniaVertB:
                            punt_central = matrix0[12] + build_ele.listDesplVerticalsEN.value[j].desplX + build_ele.dadesTDVertEN.value[j].BarraAltura/2
                            pointUbi = AllplanGeo.Point3D(matrix0[12] + build_ele.dadesTDVertEN.value[j].BarraAmple/2 + build_ele.listDesplVerticalsEN.value[j].desplLinB, matrix0[13] + build_ele.dadesTDVertEN.value[j].BarraAltura/2 , matrix0[14])
                            if (len(build_ele.dadesTDVertEN.value[j].linia)) <=1:
                                build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(linia = "Tipus 1")
                            linia = build_ele.dadesTDVertEN.value[j].linia[len(build_ele.dadesTDVertEN.value[j].linia)-1]
                            if len(build_ele.dadesTDVertEN.value[j].layer) == 0:
                                build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(layer = "EN_FIXACIO_X")
                            layer = build_ele.dadesTDVertEN.value[j].layer
                            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDVertEN.value[j].BarraAltura, BarrallargadaVert, False, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                            if polyhedronCentral != []:
                                group_elems.append(polyhedronCentral[0])
                                group_elems_preview.append(polyhedronCentral[0])
                                group_elems.append(polyhedronCentral[3])
                                group_elems_preview.append(polyhedronCentral[3])
                                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))

                        if build_ele.MostrarTDNums.value:

                            posHorInf = build_ele.BarraAlturaInf.value
                            if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
                                nHorInf = 0
                                if getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3) != "":
                                    nHorInf = getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3)

                                    if not build_ele.dadesTDVertEN.value[j].EncaixInf:
                                        posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2
                                    else:
                                        posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2
                            llargadaAct = float(TDV_Int.get_llargada()) + posHorInf
                            numeroTDV = create_num_on_view(build_ele, j, matrix0, llargadaAct)
                            group_elems_preview.append(numeroTDV)


                        contadorPPV += 1
                j += 1
        except  Exception as e:
            print("No s'han creat Barres ["+str(j)+"]", e)


        inici = 0
        final = build_ele.NumBarresRef.value


        for posBarraRef in range(inici, final):#recorrer totes les Barres Reforcs de cada vertical
            #----------------------- Afegir Barra Ref -----------------------------------
            if posBarraRef >= len(build_ele.BarresRefListEN.value):
                set_values_barresRef(build_ele, posBarraRef)


            if nRef == posBarraRef and build_ele.SelectorPPEN.value == 4:

                #si esta buit
                while len(build_ele.dadesENReftInter.value) <= posBarraRef:
                    set_valors_Ref_ini(build_ele, posBarraRef)
                if build_ele.dadesENReftInter.value[posBarraRef].acabatEditar == False:
                    build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(acabatEditar = True)
                #si no estan mostrats
                #if  build_ele.BarresRefListToShowEN.value[0].acabatEditar == False and nRef == posBarraRef: #al clicar a edit
                if  build_ele.valueAntReforc.value != nRef and nRef == posBarraRef: #al clicar a edit

                    #build_ele.BarresRefListEN.value[posBarraRef] = build_ele.BarresRefListEN.value[posBarraRef]._replace(Edit = True)
                    #mostrar valors
                    mostrar_valors_Ref(build_ele, posBarraRef)
                    build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(estaEditant = True)
                    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(acabatEditar = True)

                #guardar valors
                guardar_valors_Ref(build_ele, posBarraRef)
            else:
                if len(build_ele.dadesENReftInter.value) <= posBarraRef:
                    set_valors_Ref_ini(build_ele, posBarraRef)
                if build_ele.dadesENReftInter.value[posBarraRef].acabatEditar == True and nRef == posBarraRef:
                    #guardar valors
                    #guardar_valors_Ref(build_ele, j, posBarraRef - inici)
                    #mostrar_valors_actuals(build_ele, posBarraRef)
                    if build_ele.SelectorPPEN.value == 2:
                        mostrar_valors_actuals(build_ele, nVer)
                    elif build_ele.SelectorPPEN.value == 1:
                        print("build_ele.SelectorPPEN.value: " + str(build_ele.SelectorPPEN.value))
                    elif build_ele.SelectorPPEN.value == 3:
                        print("build_ele.SelectorPPEN.value: " + str(build_ele.SelectorPPEN.value))
                    build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(acabatEditar = False)
                    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(acabatEditar = False)
            if len(build_ele.dadesENReftInter.value) <= posBarraRef  :
                set_valors_Ref_ini(build_ele, posBarraRef)
            if len(build_ele.EncaixRefInt.value) <= posBarraRef:
                set_valors_Ref_ini(build_ele, posBarraRef)



            llargada = build_ele.BarresRefListEN.value[posBarraRef].Longitud
            BarraIniciRef = 0
            BarraFinalRef = 1
            if getNumFromText(build_ele, build_ele.BarresRefListEN.value[posBarraRef].BarraIni, 3) != "":
                BarraIniciRef = getNumFromText(build_ele, build_ele.BarresRefListEN.value[posBarraRef].BarraIni, 3)
            if getNumFromText(build_ele, build_ele.BarresRefListEN.value[posBarraRef].BarraFin, 3) != "":
                BarraFinalRef = getNumFromText(build_ele, build_ele.BarresRefListEN.value[posBarraRef].BarraFin, 3)



            while len(build_ele.dadesENReftInter.value) <= posBarraRef:
                set_valors_Ref_ini(build_ele, posBarraRef)

            if build_ele.BarresRefListEN.value[posBarraRef].BarraRef:
                llargada = build_ele.BarresRefListEN.value[posBarraRef].Longitud
                if build_ele.BarresRefListEN.value[posBarraRef].AutoLongitud:
                    if build_ele.listDesplVerticalsEN.value[BarraFinalRef].desplXAbs -(build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple) > 0:
                        if BarraIniciRef == 0:
                            #llargada = build_ele.listDesplVerticalsEN.value[BarraFinalRef].desplXAbs - build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs  + (build_ele.dadesTDVertEN.value[BarraFinalRef].BarraAmple/2 - build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple/2)
                            llargada = build_ele.listDesplVerticalsEN.value[BarraFinalRef].desplXAbs - build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs  + build_ele.dadesENReftInter.value[posBarraRef].desplX
                        else:
                            llargada = build_ele.listDesplVerticalsEN.value[BarraFinalRef].desplXAbs - build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs - build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple  + build_ele.dadesENReftInter.value[posBarraRef].desplX
                    else:
                        print("El segon tub ha d'estar en una posicio mes avançada que el primer")
                        ctypes.windll.user32.MessageBoxW(0, "El segon tub ha d'estar en una posicio mes avançada que el primer, selecciona els tubs inicial i final de forma correcta del reforç '" + str(posBarraRef) +"' (longitud " + str(build_ele.listDesplVerticalsEN.value[BarraFinalRef].desplXAbs -(build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple)) + ")", 0)
                        llargada = 30
                else:
                    llargada = build_ele.BarresRefListEN.value[posBarraRef].Longitud


                encaixos = []


                reforcRef = PP_EN_Horitzontal_reforc(random.random() * 3600, build_ele.dadesENReftInter.value[posBarraRef].Ample, build_ele.dadesENReftInter.value[posBarraRef].Altura,llargada-5 , build_ele.dadesENReftInter.value[posBarraRef].Gruix, build_ele.BarresRefListEN.value[posBarraRef].Orientacio,# (ENV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada( ), BarraGruix,
                                    build_ele.dadesENReftInter.value[posBarraRef].IsUseGlobalProp, build_ele.dadesENReftInter.value[posBarraRef].FounColor, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    encaixos) #EncaixosPar))
                if not reforcRef.is_valid():
                    return[]

                matrix_AuxR = AllplanGeo.Matrix3D()
                if BarraIniciRef == 0:
                    matrix_AuxR.SetValue(12, build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs  + build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 + 2.5  + build_ele.dadesENReftInter.value[posBarraRef].desplX)
                else:
                    matrix_AuxR.SetValue(12, build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplXAbs  + build_ele.dadesTDVertEN.value[0].BarraAmple + build_ele.dadesTDVertEN.value[BarraIniciRef].BarraAmple + 2.5  + build_ele.dadesENReftInter.value[posBarraRef].desplX)
                matrix_AuxR.SetValue(13, build_ele.listDesplVerticalsEN.value[BarraIniciRef].desplYAbs + build_ele.dadesENReftInter.value[posBarraRef].desplY)
                matrix_AuxR.SetValue(14, build_ele.BarresRefListEN.value[posBarraRef].Posicio)

                TranslationFather = matrix_AuxR
                TranslationFather.SetValue(12, placement_mat[12] + matrix_AuxR[12])
                TranslationFather.SetValue(13, placement_mat[13] + matrix_AuxR[13])
                TranslationFather.SetValue(14, placement_mat[14] + matrix_AuxR[14])
                matrix_AuxR = TranslationFather


                table_brepAuxR = reforcRef.create()
                common_propsR = reforcRef.get_common_props()

                reforcRefDEN= "V"
                if build_ele.reconeixerDen.value:
                    tubEsIgual, DEN = compare_attributes(build_ele, doc, reforcRef)
                    if (tubEsIgual):
                        reforcRefDEN = DEN

                atrENEsp = definirAtributPers(build_ele,0,"TubReforc")


                cara_a, cara_a1, cara_a2 = dividirAtribut(str(reforcRef.get_codi_cara_a()) )
                cara_b, cara_b1, cara_b2 = dividirAtribut(str(reforcRef.get_codi_cara_b()) )
                cara_c, cara_c1, cara_c2 = dividirAtribut(str(reforcRef.get_codi_cara_c()) )
                cara_d, cara_d1, cara_d2 = dividirAtribut(str(reforcRef.get_codi_cara_d()) )

                cara_e, cara_e1, cara_e2 = dividirAtribut(str(reforcRef.get_codi_cara_a_inv()) )
                cara_f, cara_f1, cara_f2 = dividirAtribut(str(reforcRef.get_codi_cara_b_inv()) )
                cara_g, cara_g1, cara_g2 = dividirAtribut(str(reforcRef.get_codi_cara_c_inv()) )
                cara_h, cara_h1, cara_h2 = dividirAtribut(str(reforcRef.get_codi_cara_d_inv()) )

                if  mostrarActual == "ENR"+str(nRef) and build_ele.BarresRefListEN.value[posBarraRef].BarraRef and nRef == posBarraRef :
                    common_propsR.Color = 6 #Vermell

                table_attr_listAux = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                                        AllplanBaseElements.AttributeString(2108,  cara_a),
                                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                                        AllplanBaseElements.AttributeString(2047,  cara_b),
                                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                                        AllplanBaseElements.AttributeString(2110,  cara_c),
                                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                                        AllplanBaseElements.AttributeString(2120,  cara_d),
                                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                                        AllplanBaseElements.AttributeString(2121,  cara_e),
                                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                                        AllplanBaseElements.AttributeString(2122,  cara_f),
                                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                                        AllplanBaseElements.AttributeString(2128,  cara_g),
                                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                                        AllplanBaseElements.AttributeString(2129,  cara_h),
                                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                                        AllplanBaseElements.AttributeString(2509,  cara_h2),

                                        AllplanBaseElements.AttributeString(2446, reforcRef.get_codi_pota_inv()),
                                        AllplanBaseElements.AttributeString(2433, reforcRef.get_codi_pota()),

                                        AllplanBaseElements.AttributeString(1947, atrENEsp),

                                        AllplanBaseElements.AttributeString(2431, reforcRef.get_codi_mesures()),
                                        AllplanBaseElements.AttributeString(2445, reforcRef.get_seccio()),
                                        AllplanBaseElements.AttributeString(220, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(2455, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(2103, reforcRefDEN),
                                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value),
                                        AllplanBaseElements.AttributeString(508, "EN"),
                                        AllplanBaseElements.AttributeString(1083, reforcRefDEN),
                                        AllplanBaseElements.AttributeString(1084, reforcRef.get_seccio()),
                                        AllplanBaseElements.AttributeString(1085, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(2455, reforcRef.get_llargada())]
                table_viewsAuxR = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsR, table_brepAuxR)])]

                ReforcPPOBjectR = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesENReftInter.value[posBarraRef].Ample, build_ele.dadesENReftInter.value[posBarraRef].Altura+10,llargada, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                ReforcPPOBjectRRecess = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.dadesENReftInter.value[posBarraRef].Ample, build_ele.dadesENReftInter.value[posBarraRef].Altura+10,llargada, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                #ReforcPPOBjectR = PP_EN_Horitzontal_reforc(random.random() * 3600, build_ele.dadesENReftInter.value[posBarraRef].Ample, build_ele.dadesENReftInter.value[posBarraRef].Altura+10,llargada, build_ele.dadesENReftInter.value[posBarraRef].Gruix,False,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                #                        False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                #                        [])

                Reforc_BrepObjectR = ReforcPPOBjectR.create()
                Reforc_views_objectR = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, Reforc_BrepObjectR)])]
                Reforc_BrepObjectRRecess = ReforcPPOBjectRRecess.create()
                Reforc_views_objectRecess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, Reforc_BrepObjectRRecess)])]

                matrix_AuxRC = AllplanGeo.Matrix3D()
                matrix_AuxRC.SetValue(12, matrix_AuxR[12])
                matrix_AuxRC.SetValue(13, matrix_AuxR[13])
                matrix_AuxRC.SetValue(14, matrix_AuxR[14] - 5)


                #group_elems.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR.get_params_list(),
                #                    hash_value = ReforcPPOBjectR.hash(), python_file = ReforcPPOBjectR.filename(),
                #                    views = Reforc_views_objectR, matrix = matrix_AuxRC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                #group_elems_preview.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR.get_params_list(),
                #                    hash_value = ReforcPPOBjectR.hash(), python_file = ReforcPPOBjectR.filename(),
                #                    views = Reforc_views_objectR, matrix = matrix_AuxRC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                group_elems.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectRRecess.get_params_list(),
                                    hash_value = ReforcPPOBjectRRecess.hash(), python_file = ReforcPPOBjectRRecess.filename(),
                                    views = Reforc_views_objectRecess, matrix = matrix_AuxRC, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))
                group_elems_preview.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectRRecess.get_params_list(),
                                    hash_value = ReforcPPOBjectRRecess.hash(), python_file = ReforcPPOBjectRRecess.filename(),
                                    views = Reforc_views_objectRecess, matrix = matrix_AuxRC, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))


                group_elems.append(PythonPart ("PP_EN_Reforc_reforc", parameter_list = reforcRef.get_params_list(),
                                        hash_value = reforcRef.hash(), python_file = reforcRef.filename(),
                                        views = table_viewsAuxR, matrix = matrix_AuxR, common_props = common_propsR, attribute_list = table_attr_listAux))
                group_elems_preview.append(PythonPart ("PP_EN_Reforc_reforc", parameter_list = reforcRef.get_params_list(),
                                        hash_value = reforcRef.hash(), python_file = reforcRef.filename(),
                                        views = table_viewsAuxR, matrix = matrix_AuxR, common_props = common_propsR, attribute_list = table_attr_listAux))


                if build_ele.dadesENReftInter.value[posBarraRef].mostrarLiniaVertA:
                    punt_central = matrix_AuxR[12] + build_ele.dadesENReftInter.value[posBarraRef].desplX + build_ele.dadesENReftInter.value[posBarraRef].Altura/2
                    pointUbi = AllplanGeo.Point3D(matrix_AuxR[12], matrix_AuxR[13] + build_ele.dadesENReftInter.value[posBarraRef].Ample/2 + build_ele.dadesENReftInter.value[posBarraRef].desplLinA, matrix_AuxR[14] + build_ele.dadesENReftInter.value[posBarraRef].Altura/2)
                    if len(build_ele.dadesENReftInter.value[posBarraRef].linia) == 0:
                        build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(linia = "Tipus 1")
                    linia = build_ele.dadesENReftInter.value[posBarraRef].linia[len(build_ele.dadesENReftInter.value[posBarraRef].linia)-1]
                    if len(build_ele.dadesENReftInter.value[posBarraRef].layer) == 0:
                        build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(layer = "EN_FIXACIO_X")
                    layer = build_ele.dadesENReftInter.value[posBarraRef].layer
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesENReftInter.value[posBarraRef].Altura, llargada-5, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                    if polyhedronCentral != []:
                        group_elems.append(polyhedronCentral[0])
                        group_elems_preview.append(polyhedronCentral[0])
                        group_elems.append(polyhedronCentral[3])
                        group_elems_preview.append(polyhedronCentral[3])
                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                if build_ele.dadesENReftInter.value[posBarraRef].mostrarLiniaVertB:
                    punt_central = matrix_AuxR[12] + build_ele.dadesENReftInter.value[posBarraRef].desplX + build_ele.dadesENReftInter.value[posBarraRef].Altura/2
                    pointUbi = AllplanGeo.Point3D(matrix_AuxR[12], matrix_AuxR[13] + build_ele.dadesENReftInter.value[posBarraRef].Ample/2 + build_ele.dadesENReftInter.value[posBarraRef].desplLinB, matrix_AuxR[14] + build_ele.dadesENReftInter.value[posBarraRef].Altura/2)
                    if len(build_ele.dadesENReftInter.value[posBarraRef].linia) == 0:
                        build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(linia = "Tipus 1")
                    linia = build_ele.dadesENReftInter.value[posBarraRef].linia[len(build_ele.dadesENReftInter.value[posBarraRef].linia)-1]
                    if len(build_ele.dadesENReftInter.value[posBarraRef].layer) == 0:
                        build_ele.dadesENReftInter.value[posBarraRef] = build_ele.dadesENReftInter.value[posBarraRef]._replace(layer = "EN_FIXACIO_X")
                    layer = build_ele.dadesENReftInter.value[posBarraRef].layer
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesENReftInter.value[posBarraRef].Altura, llargada-5, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
                    if polyhedronCentral != []:
                        group_elems.append(polyhedronCentral[0])
                        group_elems_preview.append(polyhedronCentral[0])
                        group_elems.append(polyhedronCentral[3])
                        group_elems_preview.append(polyhedronCentral[3])
                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))


                if build_ele.MostrarTDNums.value:
                    numeroTDR = create_num_on_view_ref(build_ele, posBarraRef, matrix_AuxR)
                    group_elems_preview.append(numeroTDR)

                contadorPPI += 1



        inici = 0
        final = 1


        try:
            #PREMARC
            for posBarraIncl in range(inici, final):#recorrer totes les Barres Inclinades
                if posBarraIncl >= len(build_ele.dadesENInclinades.value):
                    set_valors_incl(build_ele, posBarraIncl)
                #----------------------- Afegir Barra Incl -----------------------------------
                #inclinatPP = PP_EN_Inclinat(random.random() * 3600,30 , build_ele.dadesENInclinades.value[posBarraIncl].Altura, build_ele.dadesENInclinades.value[posBarraIncl].Llargada, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                #                    build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value # IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                #                    ) #EncaixosPar)
                inclinatPP = PP_EN_Premarc(random.random() * 3600, build_ele.ProfBalconeraEN.value, build_ele.dadesENInclinades.value[posBarraIncl].Altura , build_ele.dadesENInclinades.value[posBarraIncl].Llargada, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, 40098 # IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    ) #EncaixosPar)

                #inclinatPP = inclinatPP

                if not inclinatPP.is_valid():
                    return[]



                #definir atributs de la Barra Horitzontal Inferior
                horitzontal_Brep = inclinatPP.create()
                common_propsIncl = AllplanBaseElements.CommonProperties()
                common_propsIncl = inclinatPP.get_common_props()
                if  mostrarActual == "ENINCL":
                    common_propsIncl.Color = 6#Vermell

                inclinatfDEN= build_ele.nomPremarcEN.value
                if build_ele.reconeixerDen.value:
                    tubEsIgual, DEN = compare_attributes(build_ele, doc, inclinatPP)
                    if (tubEsIgual):
                        inclinatfDEN = DEN

                cara_a, cara_a1, cara_a2 = dividirAtribut(str(inclinatPP.get_codi_cara_a()) )
                cara_b, cara_b1, cara_b2 = dividirAtribut(str(inclinatPP.get_codi_cara_b()) )
                cara_c, cara_c1, cara_c2 = dividirAtribut(str(inclinatPP.get_codi_cara_c()) )
                cara_d, cara_d1, cara_d2 = dividirAtribut(str(inclinatPP.get_codi_cara_d()) )

                cara_e, cara_e1, cara_e2 = dividirAtribut(str(inclinatPP.get_codi_cara_a_inv()) )
                cara_f, cara_f1, cara_f2 = dividirAtribut(str(inclinatPP.get_codi_cara_b_inv()) )
                cara_g, cara_g1, cara_g2 = dividirAtribut(str(inclinatPP.get_codi_cara_c_inv()) )
                cara_h, cara_h1, cara_h2 = dividirAtribut(str(inclinatPP.get_codi_cara_d_inv()) )

                table_attr_list_incl = [ AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                                    AllplanBaseElements.AttributeString(2108,  cara_a),
                                    AllplanBaseElements.AttributeString(2494,  cara_a1),
                                    AllplanBaseElements.AttributeString(2495,  cara_a2),
                                    AllplanBaseElements.AttributeString(2047,  cara_b),
                                    AllplanBaseElements.AttributeString(2496,  cara_b1),
                                    AllplanBaseElements.AttributeString(2497,  cara_b2),
                                    AllplanBaseElements.AttributeString(2110,  cara_c),
                                    AllplanBaseElements.AttributeString(2498,  cara_c1),
                                    AllplanBaseElements.AttributeString(2499,  cara_c2),
                                    AllplanBaseElements.AttributeString(2120,  cara_d),
                                    AllplanBaseElements.AttributeString(2500,  cara_d1),
                                    AllplanBaseElements.AttributeString(2501,  cara_d2),

                                    AllplanBaseElements.AttributeString(2121,  cara_e),
                                    AllplanBaseElements.AttributeString(2502,  cara_e1),
                                    AllplanBaseElements.AttributeString(2503,  cara_e2),
                                    AllplanBaseElements.AttributeString(2122,  cara_f),
                                    AllplanBaseElements.AttributeString(2504,  cara_f1),
                                    AllplanBaseElements.AttributeString(2505,  cara_f2),
                                    AllplanBaseElements.AttributeString(2128,  cara_g),
                                    AllplanBaseElements.AttributeString(2506,  cara_g1),
                                    AllplanBaseElements.AttributeString(2507,  cara_g2),
                                    AllplanBaseElements.AttributeString(2129,  cara_h),
                                    AllplanBaseElements.AttributeString(2508,  cara_h1),
                                    AllplanBaseElements.AttributeString(2509,  cara_h2),

                                    AllplanBaseElements.AttributeString(2431, inclinatPP.get_codi_mesures()),
                                    AllplanBaseElements.AttributeString(2445, inclinatPP.get_seccio()),
                                    AllplanBaseElements.AttributeString(220, inclinatPP.get_llargada()),
                                    AllplanBaseElements.AttributeString(2455, inclinatPP.get_llargada()),
                                    AllplanBaseElements.AttributeString(2103, inclinatfDEN),
                                    AllplanBaseElements.AttributeString(1083, inclinatfDEN),
                                    AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value ),
                                    AllplanBaseElements.AttributeString(508, "E-I")]
                table_views_incl = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsIncl, horitzontal_Brep)])]


                z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                            point2=  AllplanGeo.Point3D(0,0,1))

                # ---- rotation ----

                vectorI1 = AllplanGeo.Matrix3D()
                if build_ele.RotarPremarcEN.value:
                    vectorI1.Rotation(z_axis, AllplanGeo.Angle.FromDeg(180))
                    vectorI1.SetValue(12, build_ele.dadesENInclinades.value[posBarraIncl].desplX + build_ele.dadesENInclinades.value[posBarraIncl].Llargada )
                    vectorI1.SetValue(13, build_ele.dadesENInclinades.value[posBarraIncl].desplY + build_ele.ProfBalconeraEN.value -10 + build_ele.PosicioYBalconeraEN.value )
                else:
                    vectorI1.SetValue(12, build_ele.dadesENInclinades.value[posBarraIncl].desplX)
                    vectorI1.SetValue(13, build_ele.dadesENInclinades.value[posBarraIncl].desplY + build_ele.PosicioYBalconeraEN.value)

                vectorI1.SetValue(14, -6)

                TranslationFather = vectorI1
                TranslationFather.SetValue(12, placement_mat[12] + vectorI1[12])
                TranslationFather.SetValue(13, placement_mat[13] + vectorI1[13])
                TranslationFather.SetValue(14, placement_mat[14] + vectorI1[14])
                vectorI1 = TranslationFather


                if build_ele.dadesENInclinades.value[posBarraIncl].MostrarInclinat and build_ele.MostrarBalconeraEN.value:
                    group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = inclinatPP.get_params_list(),
                                            hash_value = inclinatPP.hash(), python_file = inclinatPP.filename(),
                                            views = table_views_incl, matrix = vectorI1, common_props = common_propsIncl, attribute_list = table_attr_list_incl))
                    group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = inclinatPP.get_params_list(),
                                            hash_value = inclinatPP.hash(), python_file = inclinatPP.filename(),
                                            views = table_views_incl, matrix = vectorI1, common_props = common_propsIncl, attribute_list = table_attr_list_incl))
        except Exception as e:
            print("No s'ha pogut crear el Premarc " + str(e))



    '''
    if build_ele.SepararTDHoritzontalInf.value:
        for nBarresInf in range(0, build_ele.nBarresTDHoritzontalInf.value):
            elements , lHoritzontalPP = crear_barres_inferiors_multiples(build_ele, nBarresInf, mostrarActual)
            listHoritzontalPP.append(lHoritzontalPP)
            listElements.append(elements)
    '''
    '''
    for pphor in listHoritzontalPP:
        horitzontal_BrepppHor = pphor.create()
    '''
    for elements in listElements:
        for elenment in elements:
            group_elems.append(elenment)
            group_elems_preview.append(elenment)


    #definir atributs de la Barra Horitzontal Inferior

    pythonpartgroup = PythonPartGroup (build_ele.NomTDEN.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)
    pythonpartgroup_preview = PythonPartGroup (build_ele.NomTDEN.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems_preview)


    model_elem_list = pythonpartgroup.create()
    model_elem_list_preview = pythonpartgroup_preview.create()

    #guardar_valors_inici(build_ele,nVer)
    build_ele.valueAntReforc.value = nRef
    build_ele.SelectorPPAnt.value = build_ele.SelectorPPEN.value
    build_ele.SelectorENVAnt.value = nVer
    build_ele.DistanciaEntreTDAnt.value = build_ele.DistanciaEntreEN.value
    build_ele.BarraLlargadaAnt.value = build_ele.BarraLlargadaEN.value

    #return (model_elem_list, handle_list)

    result = {
        "elements"              :  model_elem_list,
        "handles"               :  handle_list,
        "preview_elements"      :  model_elem_list_preview,
        "group_elems"           :  group_elems,
        "group_elems_preview"   :  group_elems_preview}

    return result

    #return CreateElementResult(elements=            model_elem_list,
    #                            handles=            handle_list,
    #                            preview_elements=   model_elem_list_preview)

def create_polyline_interior(build_ele, punt_central, llargadaX, llargadaZ, isHor, pointUbi, linia = 1, layer = "EN_FIXACIO_X", posYdiferent = 0):

    posX = pointUbi.X
    posY = pointUbi.Y
    posZ = pointUbi.Z

    llargadaY = 1

    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()

    common_propsLinia = AllplanBaseElements.CommonProperties()
    common_propsLinia.GetGlobalProperties()

    common_propsLinia2 = AllplanBaseElements.CommonProperties()
    common_propsLinia2.GetGlobalProperties()

    common_propsLinia.Layer = 40100#(EN_FIXACIO_Y)#Canvair a X
    #if layer == "EN_FIXACIO_Y":
    common_propsLinia2.Layer = 40099#(EN_FIXACIO_X)#Canviar a Y
    common_propsLinia.Stroke = linia
    common_propsLinia2.Stroke = linia
    if linia == 2:
        common_propsLinia.Stroke = 97
        common_propsLinia2.Stroke = 97

    #------------------ Set the values
    if (isHor):
        liniaInterior = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        liniaInterior2 = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        if not liniaInterior.is_valid():
            return[]

        liniaInterior_brep = liniaInterior.create()
        liniaInterior_brep2 = liniaInterior2.create()
        liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                   AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                   AllplanBaseElements.AttributeString(1083, " ")]
        liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]
        liniaInterior_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia2, liniaInterior_brep2)])]

        vectorPOS = AllplanGeo.Matrix3D()
        vectorPOS.SetValue(12, posX )#+ build_ele.desplXI.value )
        vectorPOS.SetValue(13,  posYdiferent - 150)#+ build_ele.desplYI.value )
        vectorPOS.SetValue(14, posZ )

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.SetValue(12, posX )#+ build_ele.desplXI.value )
        vectorPOSInv.SetValue(13, posYdiferent + 150 + 60)#+ build_ele.desplYI.value )
        vectorPOSInv.SetValue(14, posZ )

        return [PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list),
                common_propsLinia,
                liniaInterior_brep,
                PythonPart ("liniaInterior", parameter_list = liniaInterior2.get_params_list(),
                                    hash_value = liniaInterior2.hash(), python_file = liniaInterior2.filename(),
                                    views = liniaInterior_views2, matrix = vectorPOSInv, common_props = common_propsLinia2, attribute_list = liniaInterior_attr_list)
                ]
    else:

        liniaInterior = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        liniaInterior2 = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        if not liniaInterior.is_valid():
            return[]

        liniaInterior_brep = liniaInterior.create()
        liniaInterior_brep2 = liniaInterior2.create()
        liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                   AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                   AllplanBaseElements.AttributeString(1083, " ")]
        liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]
        liniaInterior_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia2, liniaInterior_brep2)])]
        handle_list = liniaInterior.create_handles()

        vectorPOS = AllplanGeo.Matrix3D()
        vectorPOS.SetValue(12, posX )
        vectorPOS.SetValue(13, posY - 0.25)
        vectorPOS.SetValue(13, posYdiferent - 150)
        vectorPOS.SetValue(14, posZ )

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.SetValue(12, posX )
        vectorPOSInv.SetValue(13, posYdiferent + 150 + 60)
        vectorPOSInv.SetValue(14, posZ )


        return [PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list),
                common_propsLinia,
                liniaInterior_brep,
                PythonPart ("liniaInterior", parameter_list = liniaInterior2.get_params_list(),
                                    hash_value = liniaInterior2.hash(), python_file = liniaInterior2.filename(),
                                    views = liniaInterior_views2, matrix = vectorPOSInv, common_props = common_propsLinia2, attribute_list = liniaInterior_attr_list)
                ]

def get_var_chair_vert(build_ele, i, FemellesAux):
    '''
    passar totes les variables entrades per l'usuari a String
    get: i -> posicio[] de la barra a retornar
         FemellesAux -> lista de femelles a afegir

    return: retorna llista de strings dels parametres

    '''
    param_list = []
    param_list.append ("BarraAmple = %s\n" % build_ele.BarraAmpleVert.value)
    param_list.append ("BarraAltura = %s\n" % build_ele.BarraAlturaVert.value)
    param_list.append ("BarraLlargada = %s\n" % build_ele.BarraLlargadaVert.value)
    param_list.append ("BarraGruix = %s\n" % build_ele.BarraGruixVert.value)
    param_list.append ("IsUseGlobalProp = %s\n" % build_ele.IsUseGlobalPropVert.value)
    param_list.append ("FounColor = %s\n" % build_ele.FounColorVert.value)
    param_list.append ("BarraLayer = %s\n" % build_ele.BarraLayerVert.value)
    Colis = []
    for y in range(build_ele.nListColisVert.value[i].Posicio, build_ele.nListColisVert.value[i].Posicio + build_ele.nListColisVert.value[i].nTotal):
        Colis.append(build_ele.ColisVertList.value[y])
    param_list.append ("ColisPar = %s\n" % Colis)#matriu ---------------------COLIS------------
    Potes = []
    for y in range(build_ele.nListPotesVert.value[i].Posicio, build_ele.nListPotesVert.value[i].Posicio + build_ele.nListPotesVert.value[i].nTotal):
        Potes.append(build_ele.PotesVertList.value[y])
    param_list.append ("PotaPar = %s\n" % Potes)#matriu --------------------POTES-------------
    Forats = []
    for y in range(build_ele.nListForatsVert.value[i].Posicio, build_ele.nListForatsVert.value[i].Posicio + build_ele.nListForatsVert.value[i].nTotal):
        Forats.append(build_ele.ForatsVertListEN.value[y])
    param_list.append ("ForatsPar = %s\n" % Forats)#matriu --------------------Forats-------------
    param_list.append ("Ample_forat_femella = %s\n" % build_ele.dadesTDVertEN.value[i].Ample_forat_femellaVert)
    param_list.append ("Altura_forat_femella = %s\n" % build_ele.dadesTDVertEN.value[i].Altura_forat_femellaVert)
    param_list.append ("Separacio_forat_femella = %s\n" %build_ele.dadesTDVertEN.value[i].Separacio_forat_femellaVert)

    Femelles = []
    for y in range(build_ele.nListFemellesVert.value[i].Posicio, build_ele.nListFemellesVert.value[i].Posicio + build_ele.nListFemellesVert.value[i].nTotal):
        Femelles.append(build_ele.FemellesVertListEN.value[y])

    listFemelles = Femelles+FemellesAux

    param_list.append ("Femelles = %s\n" % listFemelles)#matriu -------------FEMELLES--------------------
    param_list.append ("posicio_centre_masses = %s\n" % build_ele.dadesTDVertEN.value[i].posicio_centre_massesVert)
    param_list.append ("IsFirstCancam = %s\n" % build_ele.dadesTDVertEN.value[i].IsFirstCancamVert)
    param_list.append ("Dis1cancam = %s\n" % build_ele.dadesTDVertEN.value[i].Dis1cancamVert)
    param_list.append ("IsSecondCancam = %s\n" % build_ele.dadesTDVertEN.value[i].IsSecondCancamVert)
    param_list.append ("Dis2cancam = %s\n" % build_ele.dadesTDVertEN.value[i].Dis2cancamVert)
    param_list.append ("PestanyaSuperior = %s\n" % build_ele.dadesTDVertEN.value[i].PestanyaSuperiorVert)
    param_list.append ("PestanyaInferior = %s\n" % build_ele.dadesTDVertEN.value[i].PestanyaInferiorVert)
    Encaixos = []
    for i in range(build_ele.nListEncaixVert.value[i].Posicio, build_ele.nListEncaixVert.value[i].Posicio + build_ele.nListEncaixVert.value[i].nTotal):
        Encaixos.append(build_ele.EncaixVertList.value[i])
    param_list.append ("EncaixosPar = %s\n" % Encaixos)
    return param_list

def inicialitzar_valors_inici(build_ele,nVer):
    set_values(build_ele, nVer)
    set_values_encaix(build_ele,nVer)
    set_values_femelles(build_ele, nVer)
    set_values_potes(build_ele, nVer)
    set_values_forats(build_ele, nVer)
    set_values_colis(build_ele, nVer)
    set_values_barresHor(build_ele, nVer)
    set_values_BarresVert(build_ele, nVer)
    set_values_BarresFront(build_ele, nVer)

    set_valors_hor_femelles(build_ele, nVer)
    set_valors_hor_femelles2(build_ele, nVer, nVer)

    set_valors_hor_ini(build_ele, nVer, 4)
    set_valors_Vert_ini(build_ele, nVer, NombreBarresVertInt)

    set_valors_Adjacents(build_ele, nVer*4)
    set_values_BarresFrontAux(build_ele, nVer*5)
    set_valors_Frontals(build_ele, nVer*5)

    #set_values_desplVerticals(build_ele, nVer)


def update_mat_nListVert(build_ele):
    '''
    actualitzar matrius de dades o inserir si no existeixen valors
    get: build_ele -> valors

    return: retorna llista de strings dels parametres

    '''
    #*********ENCAIXOS***********
    build_ele.LengthListEncaixVert.value = build_ele.IntegerENSelector.value *3
    if build_ele.nListEncaixVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListEncaixVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListEncaixVert.value):
            for posicions in range(len(build_ele.nListEncaixVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListEncaixVert.value[posicions-1].Posicio + build_ele.nListEncaixVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListEncaixVert.value.append(bob)
        else:
            posIni = len(build_ele.nListEncaixVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListEncaixVert.value)):
                build_ele.nListEncaixVert.value.pop()
    #*********FEMELLES**********
    build_ele.LengthListFemellesVert.value = build_ele.IntegerENSelector.value *3
    if build_ele.nListFemellesVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListFemellesVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListFemellesVert.value):
            for posicions in range(len(build_ele.nListFemellesVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListFemellesVert.value[posicions-1].Posicio + build_ele.nListFemellesVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListFemellesVert.value.append(bob)
        else:
            posIni = len(build_ele.nListFemellesVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListFemellesVert.value)):
                build_ele.nListFemellesVert.value.pop()

    #*********Potes**********
    build_ele.LengthListPotesVert.value = build_ele.IntegerENSelector.value *3
    if build_ele.nListPotesVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListPotesVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListPotesVert.value):
            for posicions in range(len(build_ele.nListPotesVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListPotesVert.value[posicions-1].Posicio + build_ele.nListPotesVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListPotesVert.value.append(bob)
        else:
            posIni = len(build_ele.nListPotesVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListPotesVert.value)):
                build_ele.nListPotesVert.value.pop()

    #*********Forats**********
    posAnt = 0
    for nposForat in range(0, len(build_ele.nListForatsVert.value)):
        build_ele.nListForatsVert.value[nposForat] = build_ele.nListForatsVert.value[nposForat]._replace(Posicio = posAnt)
        build_ele.nListForatsVert.value[nposForat] = build_ele.nListForatsVert.value[nposForat]._replace(nTotal = 10)
        posAnt += 10
    build_ele.LengthListForatsVert.value = build_ele.IntegerENSelector.value *10
    if build_ele.nListForatsVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListForatsVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListForatsVert.value):
            for posicions in range(len(build_ele.nListForatsVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListForatsVert.value[posicions-1].Posicio + build_ele.nListForatsVert.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListForatsVert.value.append(bob)
        else:
            posIni = len(build_ele.nListForatsVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListForatsVert.value)):
                build_ele.nListForatsVert.value.pop()

    #*********Colis**********
    build_ele.LengthListColisVert.value = build_ele.IntegerENSelector.value *3
    if build_ele.nListColisVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListColisVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListColisVert.value):
            for posicions in range(len(build_ele.nListColisVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListColisVert.value[posicions-1].Posicio + build_ele.nListColisVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListColisVert.value.append(bob)
        else:
            posIni = len(build_ele.nListColisVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListColisVert.value)):
                build_ele.nListColisVert.value.pop()

    #*********BarresHor**********
    build_ele.LengthListEncaixVert.value = build_ele.IntegerENSelector.value *NombreBarresHorInt
    if build_ele.nListBarresHor.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = NombreBarresHorInt)
            posAnt += NombreBarresHorInt
            build_ele.nListBarresHor.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListBarresHor.value):
            for posicions in range(len(build_ele.nListBarresHor.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresHor.value[posicions-1].Posicio + build_ele.nListBarresHor.value[posicions-1].nTotal,
                                    nTotal = NombreBarresHorInt)
                build_ele.nListBarresHor.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresHor.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListBarresHor.value)):
                build_ele.nListBarresHor.value.pop()

    #*********BarresVert**********
    if build_ele.nListBarresVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = NombreBarresVertInt)
            posAnt += NombreBarresVertInt
            build_ele.nListBarresVert.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListBarresVert.value):
            for posicions in range(len(build_ele.nListBarresVert.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresVert.value[posicions-1].Posicio + build_ele.nListBarresVert.value[posicions-1].nTotal,
                                    nTotal = NombreBarresVertInt)
                build_ele.nListBarresVert.value.append(bob)
        else:
            posAnt = 0
            for posicions in range(0,build_ele.IntegerENSelector.value):
                build_ele.nListBarresVert.value[posicions] = build_ele.nListBarresVert.value[posicions]._replace(Posicio = posAnt)
                build_ele.nListBarresVert.value[posicions] = build_ele.nListBarresVert.value[posicions]._replace(nTotal = NombreBarresVertInt)
                posAnt += NombreBarresVertInt


            posIni = len(build_ele.nListBarresVert.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListBarresVert.value)):
                build_ele.nListBarresVert.value.pop()
    #*********BarresFront**********
    if build_ele.nListBarresFront.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListBarresFront.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListBarresFront.value):
            for posicions in range(len(build_ele.nListBarresFront.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresFront.value[posicions-1].Posicio + build_ele.nListBarresFront.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListBarresFront.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresFront.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListBarresFront.value)):
                build_ele.nListBarresFront.value.pop()

    #*********BarresFrontAux**********

    #nTotat de 5 a 10


    if build_ele.nListBarresFrontAux.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerENSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListBarresFrontAux.value.append(bob)
    else:
        if build_ele.IntegerENSelector.value > len(build_ele.nListBarresFrontAux.value):
            for posicions in range(len(build_ele.nListBarresFrontAux.value),build_ele.IntegerENSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresFrontAux.value[posicions-1].Posicio + build_ele.nListBarresFrontAux.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListBarresFrontAux.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresFrontAux.value)
            for posicions in range(build_ele.IntegerENSelector.value, len(build_ele.nListBarresFrontAux.value)):
                build_ele.nListBarresFrontAux.value.pop()

    #for barraVert in build_ele.dadesTDVertEN.value:
    #    print(str(barraVert.BarraSuperior))

def guardar_valors_actuals(build_ele, i):
    '''
    Guardar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''
    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs desplZAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                     desplXAbs = build_ele.desplXVertAbs.value,
                                     desplY =build_ele.desplYVert.value,
                                     desplYAbs = build_ele.desplYVertAbs.value,
                                     desplZAbs = build_ele.desplZVertAbs.value,
                                     mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                     desplLinA =build_ele.desplVertLinA.value,
                                     mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                     desplLinB =build_ele.desplVertLinB.value)
    while len(build_ele.listDesplVerticalsEN.value) <= i:
        build_ele.listDesplVerticalsEN.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplX = build_ele.desplXVert.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplY = build_ele.desplYVert.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplXAbs = build_ele.desplXVertAbs.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplYAbs = build_ele.desplYVertAbs.value )
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplZAbs = build_ele.desplZVertAbs.value )
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplLinA = build_ele.desplVertLinA.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplLinB = build_ele.desplVertLinB.value)

    '''
    #DesplaçamentsVerticalsInt
    if len(build_ele.listDesplVerticalsInteriors.value) <= i:
        build_ele.listDesplVerticalsInteriors.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplX = build_ele.desplXVert.value)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplY = build_ele.desplYVert.value)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplLinA = build_ele.desplVertLinA.value)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplLinB = build_ele.desplVertLinB.value)
    '''
    #DADES TDV UNIQUES
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'MostrarTDVertical BarraAmple BarraAltura LlargadaAut BarraAlcada BarraSuperior BarraInferior Gruix '+
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf invertirEncaixSup invertirEncaixInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert PestanyesInv '+
                                                   'esProvisional '+
                                                   'linia layer vermell '+
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical= build_ele.MostrarENVertical.value,
                                           BarraAmple = build_ele.BarraAmpleVert.value,
                                            BarraAltura = build_ele.BarraAlturaVert.value,
                                            LlargadaAut = build_ele.llargadaAutomatica.value,
                                            BarraAlcada = build_ele.BarraLlargadaIndiv.value,
                                            BarraSuperior = build_ele.SelectorENHorSup.value,
                                            BarraInferior = build_ele.SelectorENHorInf.value,
                                            Gruix = build_ele.BarraGruixVert.value,
                                            EncaixSup = build_ele.encaixSup.value,
                                            EncaixInf = build_ele.encaixInf.value,
                                            FemellaSup = build_ele.femellaSup.value,
                                            FemellaInf = build_ele.femellaInf.value,
                                            invertirEncaixSup = build_ele.invertirEncaixVertSup.value,
                                            invertirEncaixInf = build_ele.invertirEncaixVertInf.value,
                                            Ample_forat_femellaVert = build_ele.Ample_forat_femellaVert.value,
                                            Altura_forat_femellaVert = build_ele.Altura_forat_femellaVert.value,
                                            Separacio_forat_femellaVert = build_ele.Separacio_forat_femellaVert.value,
                                            posicio_centre_massesVert= build_ele.posicio_centre_massesVert.value,
                                            IsFirstCancamVert= build_ele.IsFirstCancamVert.value,
                                            Dis1cancamVert= build_ele.Dis1cancamVert.value,
                                            IsSecondCancamVert= build_ele.IsSecondCancamVert.value,
                                            Dis2cancamVert = build_ele.Dis2cancamVert.value,
                                            PestanyaSuperiorVert = build_ele.PestanyaSuperiorVert.value,
                                            PestanyaInferiorVert = build_ele.PestanyaInferiorVert.value,
                                            PestanyesInv = build_ele.pestanyesInvVert.value,
                                            esProvisional = build_ele.esProvisional.value,
                                            linia = build_ele.SelectorLiniaVert.value,
                                            layer = build_ele.SelectorLayerVertEN.value,
                                            vermell = build_ele.esVermellVert.value,
                                            FounColor = build_ele.FounColorVert.value)
    if len(build_ele.dadesTDVertEN.value) <= i:
        build_ele.dadesTDVertEN.value.append(bobDadesGlobal)
    else:
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(MostrarTDVertical = build_ele.MostrarENVertical.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAmple = build_ele.BarraAmpleVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAltura = build_ele.BarraAlturaVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(LlargadaAut = build_ele.llargadaAutomatica.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAlcada = build_ele.BarraLlargadaIndiv.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraSuperior = build_ele.SelectorENHorSup.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraInferior = build_ele.SelectorENHorInf.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Gruix = build_ele.BarraGruixVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(EncaixInf = build_ele.encaixInf.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(EncaixSup = build_ele.encaixSup.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaInf = build_ele.femellaInf.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaSup = build_ele.femellaSup.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(invertirEncaixSup = build_ele.invertirEncaixVertSup.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(invertirEncaixInf = build_ele.invertirEncaixVertInf.value)
        #build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaInf = False)
        #build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaSup = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Ample_forat_femellaVert = build_ele.Ample_forat_femellaVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Altura_forat_femellaVert = build_ele.Altura_forat_femellaVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Separacio_forat_femellaVert = build_ele.Separacio_forat_femellaVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(posicio_centre_massesVert = build_ele.posicio_centre_massesVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(IsFirstCancamVert = build_ele.IsFirstCancamVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Dis1cancamVert = build_ele.Dis1cancamVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(IsSecondCancamVert = build_ele.IsSecondCancamVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Dis2cancamVert = build_ele.Dis2cancamVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyaSuperiorVert = build_ele.PestanyaSuperiorVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyaInferiorVert = build_ele.PestanyaInferiorVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyesInv = build_ele.pestanyesInvVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(esProvisional = build_ele.esProvisional.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(linia = build_ele.SelectorLiniaVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(layer = build_ele.SelectorLayerVertEN.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(vermell = build_ele.esVermellVert.value)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FounColor = build_ele.FounColorVert.value)


    #****************ENCAIXOS*****************
    if i < len(build_ele.nListEncaixVert.value):
        inici = build_ele.nListEncaixVert.value[i].Posicio
        final = build_ele.nListEncaixVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.EncaixVertList.value):
            set_values_encaix(build_ele, x)
        if build_ele.EncaixVertListToShow.value != [] and len(build_ele.EncaixVertListToShow.value) > y:
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Encaix = build_ele.EncaixVertListToShow.value[y].Encaix)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(EncaixOr = build_ele.EncaixVertListToShow.value[y].EncaixOr)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Longitud = build_ele.EncaixVertListToShow.value[y].Longitud)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Amplitud = build_ele.EncaixVertListToShow.value[y].Amplitud)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Posicio = build_ele.EncaixVertListToShow.value[y].Posicio)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Profunditat = build_ele.EncaixVertListToShow.value[y].Profunditat)
            build_ele.EncaixVertList.value[x] = build_ele.EncaixVertList.value[x]._replace(Pestanya = build_ele.EncaixVertListToShow.value[y].Pestanya)
        y += 1

    #***************FEMELLES******************
    if i < len(build_ele.nListFemellesVert.value):
        inici = build_ele.nListFemellesVert.value[i].Posicio
        final = build_ele.nListFemellesVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.FemellesVertListEN.value):
            set_values_femelles(build_ele, x)
        if build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(Femella = build_ele.FemellesVertListToShow.value[y].Femella)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(FemellaOr = build_ele.FemellesVertListToShow.value[y].FemellaOr)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaX = build_ele.FemellesVertListToShow.value[y].PosFemellaX)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaY = build_ele.FemellesVertListToShow.value[y].PosFemellaY)
            if y >= len(build_ele.dadesTDVertEN.value):
                set_values(build_ele, y)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(Ample_forat_femella = build_ele.dadesTDVertEN.value[y].Ample_forat_femellaVert)

            try:
                build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaXOri = build_ele.FemellesVertListToShow.value[y].PosFemellaXOri)
            except Exception as e:
                build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaXOri = 0)
        y += 1

    #***************Potes******************
    if i < len(build_ele.nListPotesVert.value):
        inici = build_ele.nListPotesVert.value[i].Posicio
        final = build_ele.nListPotesVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.PotesVertList.value):
            set_values_potes(build_ele, x)
        if build_ele.PotesVertListToShow.value != [] and len(build_ele.PotesVertListToShow.value) > y:
            build_ele.PotesVertList.value[x] = build_ele.PotesVertList.value[x]._replace(Pota = build_ele.PotesVertListToShow.value[y].Pota)
            build_ele.PotesVertList.value[x] = build_ele.PotesVertList.value[x]._replace(Posicio = build_ele.PotesVertListToShow.value[y].Posicio)
        y += 1

    #***************Forats******************
    if i < len(build_ele.nListForatsVert.value):
        inici = build_ele.nListForatsVert.value[i].Posicio
        final = build_ele.nListForatsVert.value[i].nTotal
    else:
        inici = 0
        final = 10
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.ForatsVertListEN.value):
            set_values_forats(build_ele, x)
        if build_ele.ForatsVertListToShowEN.value != [] and len(build_ele.ForatsVertListToShowEN.value) > y:
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(Forat = build_ele.ForatsVertListToShowEN.value[y].Forat)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(orientacio = build_ele.ForatsVertListToShowEN.value[y].orientacio)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(Posicio = build_ele.ForatsVertListToShowEN.value[y].Posicio)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(Llargada = build_ele.ForatsVertListToShowEN.value[y].Llargada)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(Amplada = build_ele.ForatsVertListToShowEN.value[y].Amplada)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(Complet = build_ele.ForatsVertListToShowEN.value[y].Complet)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(LlargadaB = build_ele.ForatsVertListToShowEN.value[y].LlargadaB)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(AmpladaB = build_ele.ForatsVertListToShowEN.value[y].AmpladaB)
            build_ele.ForatsVertListEN.value[x] = build_ele.ForatsVertListEN.value[x]._replace(MostrarBox = False)
        y += 1


    #***************Colis******************
    if i < len(build_ele.nListColisVert.value):
        inici = build_ele.nListColisVert.value[i].Posicio
        final = build_ele.nListColisVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.ColisVertList.value):
            set_values_colis(build_ele, x)
        if build_ele.ColisVertListToShow.value != [] and len(build_ele.ColisVertListToShow.value) > y:
            build_ele.ColisVertList.value[x] = build_ele.ColisVertList.value[x]._replace(Colis = build_ele.ColisVertListToShow.value[y].Colis)
            build_ele.ColisVertList.value[x] = build_ele.ColisVertList.value[x]._replace(orientacio = build_ele.ColisVertListToShow.value[y].orientacio)
            build_ele.ColisVertList.value[x] = build_ele.ColisVertList.value[x]._replace(Posicio = build_ele.ColisVertListToShow.value[y].Posicio)
            build_ele.ColisVertList.value[x] = build_ele.ColisVertList.value[x]._replace(Llargada = build_ele.ColisVertListToShow.value[y].Llargada)
            build_ele.ColisVertList.value[x] = build_ele.ColisVertList.value[x]._replace(Amplada = build_ele.ColisVertListToShow.value[y].Amplada)
        y += 1

    #***************BarresHor******************
    '''
    if i < len(build_ele.nListBarresHor.value):
        inici = build_ele.nListBarresHor.value[i].Posicio
        final = build_ele.nListBarresHor.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.BarresHorListEN.value):
            set_values_barresHor(build_ele, x)
        if build_ele.BarresHorListToShowEN.value != [] and len(build_ele.BarresHorListToShowEN.value) > y:
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(BarraHor = build_ele.BarresHorListToShowEN.value[y].BarraHor)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(Orientacio = build_ele.BarresHorListToShowEN.value[y].Orientacio)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(Posicio = build_ele.BarresHorListToShowEN.value[y].Posicio)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(AutoLongitud = build_ele.BarresHorListToShowEN.value[y].AutoLongitud)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(Longitud = build_ele.BarresHorListToShowEN.value[y].Longitud)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(Edit = build_ele.BarresHorListToShowEN.value[y].Edit)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(acabatEditar = build_ele.BarresHorListToShowEN.value[y].acabatEditar)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(BarraInici = build_ele.BarresHorListToShowEN.value[y].BarraInici)
            build_ele.BarresHorListEN.value[x] = build_ele.BarresHorListEN.value[x]._replace(BarraFinal = build_ele.BarresHorListToShowEN.value[y].BarraFinal)
        y += 1
    '''

    #***************BarresVert******************
    if i < len(build_ele.nListBarresVert.value):
        inici = build_ele.nListBarresVert.value[i].Posicio
        final = build_ele.nListBarresVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.BarresVertList.value):
            set_values_BarresVert(build_ele, x)
        if build_ele.BarresVertListToShow.value != [] and len(build_ele.BarresVertListToShow.value) > y:
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(BarraVert = build_ele.BarresVertListToShow.value[y].BarraVert)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(Posicio = build_ele.BarresVertListToShow.value[y].Posicio)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(PosicioAbs = build_ele.BarresVertListToShow.value[y].PosicioAbs)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(PosicioZ = build_ele.BarresVertListToShow.value[y].PosicioZ)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(AutoLongitud = build_ele.BarresVertListToShow.value[y].AutoLongitud)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(Longitud = build_ele.BarresVertListToShow.value[y].Longitud)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(BarraInici = build_ele.BarresVertListToShow.value[y].BarraInici)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(Edit = build_ele.BarresVertListToShow.value[y].Edit)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(EncaixInf = build_ele.BarresVertListToShow.value[y].EncaixInf)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(EncaixSup = build_ele.BarresVertListToShow.value[y].EncaixSup)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(EditFront = build_ele.BarresVertListToShow.value[y].EditFront)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(PestanyaSup = build_ele.BarresVertListToShow.value[y].PestanyaSup)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(PestanyaInf = build_ele.BarresVertListToShow.value[y].PestanyaInf)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(acabatEditar = build_ele.BarresVertListToShow.value[y].acabatEditar)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(editiantFrontals = build_ele.BarresVertListToShow.value[y].editiantFrontals)
            #build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaSup = build_ele.BarresVertListToShow.value[y].FemellaSup)
            #build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaInf = build_ele.BarresVertListToShow.value[y].FemellaInf)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaSup = False)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaInf = False)
        y += 1

    #***************BarresFront******************
    '''
    #Ampliacio de 6 a 10
    if i < len(build_ele.nListBarresFront.value):
        if build_ele.nListBarresFront.value[i].nTotal != 10:
            build_ele.nListBarresFront.value[i] = build_ele.nListBarresFront.value[i]._replace(nTotal = 10)

    if i < len(build_ele.nListBarresFront.value):
        inici = build_ele.nListBarresFront.value[i].Posicio
        final = build_ele.nListBarresFront.value[i].nTotal
    else:
        inici = 0
        final = 0
    y = 0
    for x in range(inici, inici+final):
        if x >= len(build_ele.BarresFrontList.value):
            set_values_BarresFront(build_ele, x)
        if build_ele.BarresFrontListToShow.value != [] and len(build_ele.BarresFrontListToShow.value) > y:
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(BarraFront = build_ele.BarresFrontListToShow.value[y].BarraFront)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Amplitud = build_ele.BarresFrontListToShow.value[y].Amplitud)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Altura = build_ele.BarresFrontListToShow.value[y].Altura)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Orientacio = build_ele.BarresFrontListToShow.value[y].Orientacio)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Posicio = build_ele.BarresFrontListToShow.value[y].Posicio)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Longitud = build_ele.BarresFrontListToShow.value[y].Longitud)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Profunditat = build_ele.BarresFrontListToShow.value[y].Profunditat)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Edit = build_ele.BarresFrontListToShow.value[y].Edit)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(Save = build_ele.BarresFrontListToShow.value[y].Save)
            build_ele.BarresFrontList.value[x] = build_ele.BarresFrontList.value[x]._replace(acabatEditar = build_ele.BarresFrontListToShow.value[y].acabatEditar)
        y += 1
    '''

def mostrar_valors_actuals(build_ele, i):
    '''
    mostrar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''
    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs desplZAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                    desplXAbs = build_ele.desplXVertAbs.value,
                                    desplY = build_ele.desplYVert.value,
                                    desplYAbs = build_ele.desplYVertAbs.value,
                                    desplZAbs = build_ele.desplZVertAbs.value,
                                    mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                    desplLinA =build_ele.desplVertLinA.value,
                                    mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                    desplLinB =build_ele.desplVertLinB.value)
    while len(build_ele.listDesplVerticalsEN.value) <= i:
        build_ele.listDesplVerticalsEN.value.append(bobDespl)
    else:
        build_ele.desplXVert.value = build_ele.listDesplVerticalsEN.value[i].desplX
        build_ele.desplYVert.value = build_ele.listDesplVerticalsEN.value[i].desplY
        build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsEN.value[i].desplXAbs
        build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsEN.value[i].desplYAbs
        build_ele.desplZVertAbs.value = build_ele.listDesplVerticalsEN.value[i].desplZAbs
        build_ele.mostrarLiniaVertA.value = build_ele.listDesplVerticalsEN.value[i].mostrarLiniaVertA
        build_ele.desplVertLinA.value = build_ele.listDesplVerticalsEN.value[i].desplLinA
        build_ele.mostrarLiniaVertB.value = build_ele.listDesplVerticalsEN.value[i].mostrarLiniaVertB
        build_ele.desplVertLinB.value = build_ele.listDesplVerticalsEN.value[i].desplLinB

    '''
    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                    desplY =build_ele.desplYVert.value,
                                    mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                    desplLinA =build_ele.desplVertLinA.value,
                                    mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                    desplLinB =build_ele.desplVertLinB.value)
    #DesplaçamentsVerticals Interiors
    while len(build_ele.listDesplVerticalsInteriors.value) <= i:
        build_ele.listDesplVerticalsInteriors.value.append(bobDespl)
    else:
        build_ele.desplXVert.value = build_ele.listDesplVerticalsInteriors.value[i].desplX
        build_ele.desplYVert.value = build_ele.listDesplVerticalsInteriors.value[i].desplY
        build_ele.mostrarLiniaVertA.value = build_ele.listDesplVerticalsInteriors.value[i].mostrarLiniaVertA
        build_ele.desplVertLinA.value = build_ele.listDesplVerticalsInteriors.value[i].desplLinA
        build_ele.mostrarLiniaVertB.value = build_ele.listDesplVerticalsInteriors.value[i].mostrarLiniaVertB
        build_ele.desplVertLinB.value = build_ele.listDesplVerticalsInteriors.value[i].desplLinB
    '''

    #DADES TDV UNIQUES
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'MostrarTDVertical BarraAmple BarraAltura LlargadaAut BarraAlcada BarraSuperior BarraInferior Gruix '+
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf invertirEncaixSup invertirEncaixInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert PestanyesInv '+
                                                   'esProvisional '+
                                                   'linia layer vermell '+
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical = build_ele.MostrarENVertical.value,
                                            BarraAmple = build_ele.BarraAmpleVert.value,
                                            BarraAltura = build_ele.BarraAlturaVert.value,
                                            LlargadaAut = build_ele.llargadaAutomatica.value,
                                            BarraAlcada = build_ele.BarraLlargadaIndiv.value,
                                            BarraSuperior = "EN Superior",#build_ele.SelectorENHorSup.value,
                                            BarraInferior = "EN Inferior",#build_ele.SelectorENHorInf.value,
                                            Gruix = build_ele.BarraGruixVert.value,
                                            EncaixSup = build_ele.encaixSup.value,
                                            EncaixInf = build_ele.encaixInf.value,
                                            FemellaSup = build_ele.femellaSup.value,
                                            FemellaInf = build_ele.femellaInf.value,
                                            invertirEncaixSup = build_ele.invertirEncaixVertSup.value,
                                            invertirEncaixInf = build_ele.invertirEncaixVertInf.value,
                                            Ample_forat_femellaVert = build_ele.Ample_forat_femellaVert.value,
                                            Altura_forat_femellaVert = build_ele.Ample_forat_femellaVert.value,
                                            Separacio_forat_femellaVert = build_ele.Separacio_forat_femellaVert.value,
                                            posicio_centre_massesVert= build_ele.posicio_centre_massesVert.value,
                                            IsFirstCancamVert= build_ele.IsFirstCancamVert.value,
                                            Dis1cancamVert= build_ele.Dis1cancamVert.value,
                                            IsSecondCancamVert= build_ele.IsSecondCancamVert.value,
                                            Dis2cancamVert = build_ele.Dis2cancamVert.value,
                                            PestanyaSuperiorVert = build_ele.PestanyaSuperiorVert.value,
                                            PestanyaInferiorVert = build_ele.PestanyaInferiorVert.value,
                                            PestanyesInv = build_ele.pestanyesInvVert.value,
                                            esProvisional = build_ele.esProvisional.value,
                                            linia = build_ele.SelectorLiniaVert.value,
                                            layer = build_ele.SelectorLayerVertEN.value,
                                            vermell = build_ele.esVermellVert.value,
                                            FounColor = build_ele.FounColorVert.value)
    if len(build_ele.dadesTDVertEN.value) <= i:
        build_ele.dadesTDVertEN.value.append(bobDadesGlobal)
    else:
        build_ele.MostrarENVertical.value = build_ele.dadesTDVertEN.value[i].MostrarTDVertical
        build_ele.BarraAmpleVert.value = build_ele.dadesTDVertEN.value[i].BarraAmple
        build_ele.BarraAlturaVert.value = build_ele.dadesTDVertEN.value[i].BarraAltura
        build_ele.llargadaAutomatica.value = build_ele.dadesTDVertEN.value[i].LlargadaAut
        build_ele.BarraLlargadaIndiv.value = build_ele.dadesTDVertEN.value[i].BarraAlcada
        build_ele.SelectorENHorSup.value = build_ele.dadesTDVertEN.value[i].BarraSuperior
        build_ele.SelectorENHorInf.value = build_ele.dadesTDVertEN.value[i].BarraInferior
        build_ele.BarraGruixVert.value = build_ele.dadesTDVertEN.value[i].Gruix
        build_ele.encaixSup.value = build_ele.dadesTDVertEN.value[i].EncaixSup
        build_ele.encaixInf.value = build_ele.dadesTDVertEN.value[i].EncaixInf
        build_ele.femellaSup.value = build_ele.dadesTDVertEN.value[i].FemellaSup
        build_ele.femellaInf.value = build_ele.dadesTDVertEN.value[i].FemellaInf
        build_ele.invertirEncaixVertSup.value =  build_ele.dadesTDVertEN.value[i].invertirEncaixSup
        build_ele.invertirEncaixVertInf.value =  build_ele.dadesTDVertEN.value[i].invertirEncaixInf
        #build_ele.femellaSup.value = False#build_ele.dadesTDVertEN.value[i].FemellaSup
        #build_ele.femellaInf.value = False#build_ele.dadesTDVertEN.value[i].FemellaInf
        build_ele.Ample_forat_femellaVert.value = build_ele.dadesTDVertEN.value[i].Ample_forat_femellaVert
        build_ele.Separacio_forat_femellaVert.value = build_ele.dadesTDVertEN.value[i].Separacio_forat_femellaVert
        build_ele.posicio_centre_massesVert.value = build_ele.dadesTDVertEN.value[i].posicio_centre_massesVert
        build_ele.IsFirstCancamVert.value = build_ele.dadesTDVertEN.value[i].IsFirstCancamVert
        build_ele.Dis1cancamVert.value = build_ele.dadesTDVertEN.value[i].Dis1cancamVert
        build_ele.IsSecondCancamVert.value = build_ele.dadesTDVertEN.value[i].IsSecondCancamVert
        build_ele.Dis2cancamVert.value = build_ele.dadesTDVertEN.value[i].Dis2cancamVert
        build_ele.PestanyaSuperiorVert.value = build_ele.dadesTDVertEN.value[i].PestanyaSuperiorVert
        build_ele.PestanyaInferiorVert.value = build_ele.dadesTDVertEN.value[i].PestanyaInferiorVert
        build_ele.pestanyesInvVert.value = build_ele.dadesTDVertEN.value[i].PestanyesInv
        build_ele.esProvisional.value = build_ele.dadesTDVertEN.value[i].esProvisional
        build_ele.SelectorLiniaVert.value = build_ele.dadesTDVertEN.value[i].linia
        build_ele.SelectorLayerVertEN.value = build_ele.dadesTDVertEN.value[i].layer
        build_ele.esVermellVert.value = build_ele.dadesTDVertEN.value[i].vermell
        build_ele.FounColorVert.value = build_ele.dadesTDVertEN.value[i].FounColor


    #****************** MATRIUS ***********************
    #**********ENCAIXOS*************
    build_ele.EncaixVertListToShow.value = []
    if i < len(build_ele.nListEncaixVert.value):
        inici = build_ele.nListEncaixVert.value[i].Posicio
        final = build_ele.nListEncaixVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.EncaixVertList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
            bob = TDCollection( Encaix = False,
                                EncaixOr = "Esq",
                                Longitud = 31.,
                                Amplitud = 30,
                                Posicio = 0.,
                                Profunditat = 11.0,
                                Pestanya = False,
                                Separator = '')

            build_ele.EncaixVertListToShow.value.append(bob)
        else:
            build_ele.EncaixVertListToShow.value.append(build_ele.EncaixVertList.value[x])

    #**********FEMELLES*************
    build_ele.FemellesVertListToShow.value = []
    if i < len(build_ele.nListFemellesVert.value):
        inici = build_ele.nListFemellesVert.value[i].Posicio
        final = build_ele.nListFemellesVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.FemellesVertListEN.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Separator')
            bob = TDCollection( Femella = False,
                                FemellaOr = "Esq",
                                PosFemellaX = 400.,
                                PosFemellaY = 0.,
                                Separacio_forat_femella = 50,
                                PosFemellaXOri  = 0,
                                Separator = '')


            build_ele.FemellesVertListToShow.value.append(bob)
        else:
            build_ele.FemellesVertListToShow.value.append(build_ele.FemellesVertListEN.value[x])

    #**********Potes*************
    build_ele.PotesVertListToShow.value = []
    if i < len(build_ele.nListPotesVert.value):
        inici = build_ele.nListPotesVert.value[i].Posicio
        final = build_ele.nListPotesVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.PotesVertList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Pota Posicio Separator')
            bob = TDCollection( Pota = False,
                                Posicio = 400.,
                                Separator = '')

            build_ele.PotesVertListToShow.value.append(bob)
        else:
            build_ele.PotesVertListToShow.value.append(build_ele.PotesVertList.value[x])

    #**********Forats*************
    build_ele.ForatsVertListToShowEN.value = []
    if i < len(build_ele.nListForatsVert.value):
        inici = build_ele.nListForatsVert.value[i].Posicio
        final = build_ele.nListForatsVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.ForatsVertListEN.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
            bob = TDCollection( Forat = False,
                                orientacio = "Esq",
                                Posicio = 400,
                                Llargada = 25,
                                Amplada = 25,
                                Complet = False,
                                LlargadaB = 3,
                                AmpladaB = 3,
                                MostrarBox = False,
                                Separator = '')

            build_ele.ForatsVertListToShowEN.value.append(bob)
        else:
            build_ele.ForatsVertListToShowEN.value.append(build_ele.ForatsVertListEN.value[x])

    #**********Colis*************
    build_ele.ColisVertListToShow.value = []
    if i < len(build_ele.nListColisVert.value):
        inici = build_ele.nListColisVert.value[i].Posicio
        final = build_ele.nListColisVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.ColisVertList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Colis orientacio Posicio Llargada Amplada Separator')
            bob = TDCollection( Colis = False,
                                orientacio = 'Sup',
                                Posicio = 400.,
                                Llargada = 170,
                                Amplada = 12,
                                Separator = '')

            build_ele.ColisVertListToShow.value.append(bob)
        else:
            build_ele.ColisVertListToShow.value.append(build_ele.ColisVertList.value[x])

     #**********BarresHor*************
    '''
    build_ele.BarresHorListToShowEN.value = []
    if i < len(build_ele.nListBarresHor.value):
        inici = build_ele.nListBarresHor.value[i].Posicio
        final = build_ele.nListBarresHor.value[i].nTotal
    else:
        inici = 0
        final = 0
    pos = 0
    for x in range(inici, inici+final):
        pos += 400
        if len(build_ele.BarresHorListEN.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'BarraHor Orientacio Posicio AutoLongitud Longitud BarraInici BarraFinal Edit acabatEditar Separator')
            bob = TDCollection( BarraHor = False,
                                Orientacio = 'Sup',
                                Posicio = pos,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici= "Tub 0",
                                BarraFinal= "Tub "+str(i+1),
                                Edit = False,
                                acabatEditar = False,
                                Separator = '')

            build_ele.BarresHorListToShowEN.value.append(bob)
        else:
            build_ele.BarresHorListToShowEN.value.append(build_ele.BarresHorListEN.value[x])
    '''

    #**********BarresVert*************

    build_ele.BarresVertListToShow.value = []
    if i < len(build_ele.nListBarresVert.value):
        inici = build_ele.nListBarresVert.value[i].Posicio
        final = build_ele.nListBarresVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.BarresVertList.value) <= x:
        #if len(build_ele.BarresVertList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf Separator')
            bob = TDCollection( BarraVert = False,
                                Posicio = 400.,
                                PosicioAbs = 0,
                                PosicioZ = 0,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici = 'Inferior',
                                EditFront = False,
                                Edit = False,
                                EncaixInf = True,#
                                EncaixSup = True,#
                                PestanyaSup = False,
                                PestanyaInf = False,
                                acabatEditar = False,
                                editiantFrontals = False,
                                FemellaSup = False,
                                FemellaInf = False,
                                Separator = '')

            build_ele.BarresVertListToShow.value.append(bob)
        else:
            build_ele.BarresVertListToShow.value.append(build_ele.BarresVertList.value[x])


    #**********BarresFront*************

    '''
    if build_ele.nListBarresFront.value[i].nTotal != 10:
        build_ele.nListBarresFront.value[i] = build_ele.nListBarresFront.value[i]._replace(nTotal = 10)

    build_ele.BarresFrontListToShow.value = []
    if i < len(build_ele.nListBarresFront.value):
        inici = build_ele.nListBarresFront.value[i].Posicio
        final = build_ele.nListBarresFront.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.BarresFrontList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar Separator')
            bob = TDCollection( BarraFront = False,
                               Amplitud = 30,
                               Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False,
                                Separator= '')

            build_ele.BarresFrontListToShow.value.append(bob)
        else:
            build_ele.BarresFrontListToShow.value.append(build_ele.BarresFrontList.value[x])
    '''

    test = "testSTOP"


def set_values(build_ele, i):
    '''
    Guardar valors del TD actualment seleccionat (no llistes)
    get: i -> Posicio

    return: -

    '''

    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs desplZAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = 0,
                                     desplXAbs = 0,
                                    desplY = 0,
                                    desplYAbs = 0,
                                    desplZAbs = 0,
                                    mostrarLiniaVertA = True,
                                    desplLinA =0,
                                    mostrarLiniaVertB = False,
                                    desplLinB =0)
    while len(build_ele.listDesplVerticalsEN.value) <= i:
        build_ele.listDesplVerticalsEN.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplX = 0)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplY = 0)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplXAbs = 0 )
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplYAbs = 0 )
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplZAbs = 0 )
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(mostrarLiniaVertA = True)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplLinA = 0)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(mostrarLiniaVertB = False)
        build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplLinB = 0)

    lennVer = len(build_ele.SelectorENV.value)
    nVerS = build_ele.SelectorENV.value[lennVer-1:]


    #if i == nVer:
    #    build_ele.listDesplVerticalsEN.value[i] = build_ele.listDesplVerticalsEN.value[i]._replace(desplXAbs = build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[i].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2)


    #DesplaçamentsVerticals Interiors
    while len(build_ele.listDesplVerticalsInteriors.value) <= i:
        build_ele.listDesplVerticalsInteriors.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplX = 0)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplY = 0)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(mostrarLiniaVertA = True)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplLinA = 0)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(mostrarLiniaVertB = False)
        build_ele.listDesplVerticalsInteriors.value[i] = build_ele.listDesplVerticalsInteriors.value[i]._replace(desplLinB = 0)

    #DADES TDV UNIQUES
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'MostrarTDVertical BarraAmple BarraAltura LlargadaAut BarraAlcada BarraSuperior BarraInferior Gruix '+
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf invertirEncaixSup invertirEncaixInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert PestanyesInv '+
                                                   'esProvisional '+
                                                   'linia layer vermell '+
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical = False,
                                            BarraAmple = 40,
                                            BarraAltura = 50,
                                            LlargadaAut = True,
                                            BarraAlcada = 2600,
                                            BarraSuperior = "EN Superior",
                                            BarraInferior = "EN Inferior",
                                            Gruix = 1.5,
                                            EncaixSup = True,#
                                            EncaixInf = True,#
                                            FemellaSup = False,
                                            FemellaInf = False,
                                            invertirEncaixSup = False,
                                            invertirEncaixInf = False,
                                            Ample_forat_femellaVert = 15,
                                            Altura_forat_femellaVert = 2,#3.75,
                                            Separacio_forat_femellaVert = 50,
                                            posicio_centre_massesVert= 500.00,
                                            IsFirstCancamVert= False,
                                            Dis1cancamVert= 500,
                                            IsSecondCancamVert= False,
                                            Dis2cancamVert = 1000,
                                            PestanyaSuperiorVert = False,
                                            PestanyaInferiorVert = False,
                                            PestanyesInv = False,
                                            esProvisional = False,
                                            linia = "Tipus 1",
                                            layer = "EN_ESTRUCTURA",
                                            vermell = False,
                                            FounColor = 1)
    while len(build_ele.dadesTDVertEN.value) <= i:
        build_ele.dadesTDVertEN.value.append(bobDadesGlobal)
    else:
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAmple = 40)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAltura = 50)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraAlcada = 2600)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(LlargadaAut = True)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraSuperior = "EN Superior")
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(BarraInferior = "EN Inferior")
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Gruix = 1.5)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(EncaixSup = True)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(EncaixInf = True)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(invertirEncaixSup = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(invertirEncaixInf = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Ample_forat_femellaVert = 15)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Altura_forat_femellaVert = 15)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Separacio_forat_femellaVert = 50)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(posicio_centre_massesVert = 500.00)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(IsFirstCancamVert = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Dis1cancamVert = 500)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(IsSecondCancamVert = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(Dis2cancamVert = 1000)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyaSuperiorVert = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyaInferiorVert = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(PestanyesInv = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaSup = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FemellaInf = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(esProvisional = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(linia = "Tipus 1")
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(layer = "EN_ESTRUCTURA")
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(vermell = False)
        build_ele.dadesTDVertEN.value[i] = build_ele.dadesTDVertEN.value[i]._replace(FounColor = 1)

    if len(build_ele.dadesTDVertEN.value) <= build_ele.IntegerENSelector.value:
        set_values(build_ele, build_ele.IntegerENSelector.value)
    build_ele.dadesTDVertEN.value[0] = build_ele.dadesTDVertEN.value[0]._replace(MostrarTDVertical = True)
    build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1] = build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1]._replace(MostrarTDVertical = True)

def set_values_BarresVertListToShow(build_ele, i):
    if len(build_ele.BarresVertListToShow.value) <= i:
        TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf Separator')
        bob = TDCollection( BarraVert = False,
                            Posicio = 400.,
                            PosicioAbs = 0,
                            PosicioZ = 0,
                            AutoLongitud = True,
                            Longitud = 100,
                            BarraInici = 'Inferior',
                            EditFront = False,
                            Edit = False,
                            EncaixInf = True,
                            EncaixSup = True,
                            PestanyaSup = False,
                            PestanyaInf = False,
                            acabatEditar = False,
                            editiantFrontals = False,
                            FemellaSup = False,
                            FemellaInf = False,
                            Separator = '')

        build_ele.BarresVertListToShow.value.append(bob)


def set_values_encaix(build_ele, i):
    '''
    Guardar valors del encaix del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.EncaixVertList.value) <= i:
        for x in range(len(build_ele.EncaixVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
            bob = TDCollection( Encaix = False,
                                EncaixOr = "Esq",
                                Longitud = 31.,
                                Amplitud = 30,
                                Posicio = 0.,
                                Profunditat = 11.0,
                                Pestanya = False,
                                Separator = '')

            build_ele.EncaixVertList.value.append(bob)

def set_values_femelles(build_ele, i):
    '''
    Guardar valors de les femelles del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.FemellesVertListEN.value) <= i:
        for x in range(len(build_ele.FemellesVertListEN.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Separator')
            bob = TDCollection( Femella = False,
                                FemellaOr = "Esq",
                                PosFemellaX = 400.,
                                PosFemellaY = 0.,
                                Separacio_forat_femella = 0,
                                PosFemellaXOri = 0,
                                Ample_forat_femella = 2,#3,
                                Separator = '')

            build_ele.FemellesVertListEN.value.append(bob)

def set_values_potes(build_ele, i):
    '''
    Guardar valors de les potes del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.PotesVertList.value) <= i:
        for x in range(len(build_ele.PotesVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Pota Posicio Separator')
            bob = TDCollection( Pota = False,
                                Posicio = 400.,
                                Separator = '')

            build_ele.PotesVertList.value.append(bob)

def set_values_forats(build_ele, i):
    '''
    Guardar valors de les Forats del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.ForatsVertListEN.value) <= i:
        for x in range(len(build_ele.ForatsVertListEN.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
            bob = TDCollection( Forat = False,
                                orientacio = "Esq",
                                Posicio = 400,
                                Llargada = 25,
                                Amplada = 25,
                                Complet = False,
                                LlargadaB = 3,
                                AmpladaB = 3,
                                MostrarBox = False,
                                Separator = '')

            build_ele.ForatsVertListEN.value.append(bob)

def set_values_colis(build_ele, i):
    '''
    Guardar valors dels Colis del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.ColisVertList.value) <= i:
        for x in range(len(build_ele.ColisVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Colis orientacio Posicio Llargada Amplada Separator')
            bob = TDCollection( Colis = False,
                                orientacio = 'Sup',
                                Posicio = 400.,
                                Llargada = 170,
                                Amplada = 12,
                                Separator = '')

            build_ele.ColisVertList.value.append(bob)

def set_values_barresHor(build_ele, i):
    '''
    Guardar valors de les Barres Horitzontals del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    pos = 0
    cont = 0
    if len(build_ele.BarresHorListEN.value) <= i:
        for x in range(len(build_ele.BarresHorListEN.value), i+1):
            if cont == NombreBarresHorInt:
                pos = 0
                cont= 0
            cont += 1
            pos += 400
            TDCollection = collections.namedtuple('StirrupList', 'BarraHor Orientacio Posicio AutoLongitud Longitud BarraInici BarraFinal Edit acabatEditar Separator')
            bob = TDCollection( BarraHor = False,
                                Orientacio = 'Sup',
                                acabatEditar = False,
                                Posicio = pos,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici = "Tub 0",
                                BarraFinal = "Tub "+str(i+1),
                                Edit = False,
                                Separator = '')

            build_ele.BarresHorListEN.value.append(bob)

    inici = len(build_ele.nListBarresHor.value)
    final = build_ele.nListBarresHor.value[len(build_ele.nListBarresHor.value)-1].Posicio + build_ele.nListBarresHor.value[len(build_ele.nListBarresHor.value)-1].nTotal

    pos = 0
    for aux in range(inici, final):
        pos += 400
        TDCollection = collections.namedtuple('StirrupList', 'BarraHor Orientacio Posicio AutoLongitud Longitud BarraInici BarraFinal Edit acabatEditar Separator')
        bob = TDCollection( BarraHor = False,
                            Orientacio = 'Sup',
                            acabatEditar = False,
                            Posicio = pos,
                            AutoLongitud = True,
                            Longitud = 100,
                            BarraInici = 'Tub 0',
                            BarraFinal = "Tub "+str(i+1),
                            Edit = False,
                            Separator = '')

        build_ele.BarresHorListEN.value.append(bob)

def set_values_barresRef(build_ele, i):
    '''
    Guardar valors de les Barres Reforç del EN actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    pos = 0
    cont = 0
    if len(build_ele.BarresRefListEN.value) <= i:
        for x in range(len(build_ele.BarresRefListEN.value), i+1):
            if cont == 3:
                pos = 0
                cont= 0
            cont += 1
            pos += 400
            ENCollection = collections.namedtuple('StirrupList', 'BarraRef Orientacio Posicio BarraIni BarraFin AutoLongitud Longitud Edit acabatEditar Separator')
            bob = ENCollection( BarraRef = False,
                                Orientacio = 'Sup',
                                acabatEditar = False,
                                Posicio = pos,
                                BarraIni = 'Tub 0',
                                BarraFin = 'Tub 1',
                                AutoLongitud = True,
                                Longitud = 100,
                                Edit = False,
                                Separator = '')

            build_ele.BarresRefListEN.value.append(bob)

    '''
    inici = len(build_ele.nListBarresRef.value)
    final = build_ele.nListBarresRef.value[len(build_ele.nListBarresRef.value)-1].Posicio + build_ele.nListBarresRef.value[len(build_ele.nListBarresRef.value)-1].nTotal
    for aux in range(inici, final):
        pos += 400
        ENCollection = collections.namedtuple('StirrupList', 'BarraRef Orientacio Posicio BarraIni AutoLongitud Longitud Edit acabatEditar Separator')
        bob = ENCollection( BarraRef = False,
                            Orientacio = 'Sup',
                            acabatEditar = False,
                            Posicio = pos,
                            BarraIni = 'Barra0',
                            AutoLongitud = True,
                            Longitud = 100,
                            Edit = False,
                            Separator = '')

        build_ele.BarresRefListEN.value.append(bob)
    '''

def set_values_BarresVert(build_ele, i):

    if len(build_ele.BarresVertList.value) <= i:
        for x in range(len(build_ele.BarresVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf Separator')
            bob = TDCollection( BarraVert = False,
                                acabatEditar = False,
                                Posicio = 0.,
                                PosicioAbs=0,
                                PosicioZ = 0,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici = 'Inferior',
                                EditFront = False,
                                Edit = False,
                                EncaixInf = True,
                                EncaixSup = True,
                                PestanyaSup = False,
                                PestanyaInf = False,
                                editiantFrontals = False,
                                FemellaSup = False,
                                FemellaInf = False,
                                Separator = '')

            build_ele.BarresVertList.value.append(bob)

    inici = len(build_ele.nListBarresVert.value)
    final = build_ele.nListBarresVert.value[len(build_ele.nListBarresVert.value)-1].Posicio + build_ele.nListBarresVert.value[len(build_ele.nListBarresVert.value)-1].nTotal
    for aux in range(inici, final):
        TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf Separator')
        bob = TDCollection( BarraVert = False,
                           acabatEditar = False,
                            Posicio = 0.,
                            PosicioAbs= 0,
                            PosicioZ = 0,
                            AutoLongitud = True,
                            Longitud = 100,
                            BarraInici = 'Inferior',
                            EditFront = False,
                            Edit = False,
                            EncaixInf = True,
                            EncaixSup = True,
                            editiantFrontals = False,
                            PestanyaSup = False,
                            PestanyaInf = False,
                            FemellaSup = False,
                            FemellaInf = False,
                            Separator = '')

        build_ele.BarresVertList.value.append(bob)

def set_values_BarresFront(build_ele, i):

    if len(build_ele.BarresFrontList.value) <= i:
        for x in range(len(build_ele.BarresFrontList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar Separator')
            bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False,
                                Separator= '')

            build_ele.BarresFrontList.value.append(bob)

    inici = len(build_ele.nListBarresFront.value)
    final = build_ele.nListBarresFront.value[len(build_ele.nListBarresFront.value)-1].Posicio + build_ele.nListBarresFront.value[len(build_ele.nListBarresFront.value)-1].nTotal
    for aux in range(inici, final):
        TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar Separator')
        bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Sup',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False,
                                Separator= '')


        build_ele.BarresFrontList.value.append(bob)

def remove_values(build_ele, i):
    '''
    elimina valors en cas de que s'hagi reduit la llargada per no acommular valors innecessaris
    get: i -> Posicio

    return: -

    '''
    for x in range(i*NombreBarresVertInt, len(build_ele.listDesplVerticalsEN.value)):
        build_ele.listDesplVerticalsEN.value.pop()

    for x in range(i*2, len(build_ele.listDesplVerticalsInteriors.value)):
        build_ele.listDesplVerticalsInteriors.value.pop()

    for x in range(i*18, len(build_ele.dadesTDVertEN.value)):
        build_ele.dadesTDVertEN.value.pop()

    for x in range(i*3, len(build_ele.EncaixVertList.value)):
        build_ele.EncaixVertList.value.pop()

    for x in range(i*3, len(build_ele.FemellesVertListEN.value)):
        build_ele.FemellesVertListEN.value.pop()

    for x in range(i*3, len(build_ele.PotesVertList.value)):
        build_ele.PotesVertList.value.pop()

    for x in range(i*12, len(build_ele.ForatsVertListEN.value)):
        build_ele.ForatsVertListEN.value.pop()

    for x in range(i*5, len(build_ele.ColisVertList.value)):
        build_ele.ColisVertList.value.pop()

    for x in range(i*NombreBarresHorInt, len(build_ele.BarresHorListEN.value)):
        build_ele.BarresHorListEN.value.pop()

    for x in range(i*8, len(build_ele.BarresRefListEN.value)):
        build_ele.BarresRefListEN.value.pop()

    for x in range(i*17, len(build_ele.BarresVertList.value)):
        build_ele.BarresVertList.value.pop()

    for x in range(i*12, len(build_ele.BarresFrontList.value)):
        build_ele.BarresFrontList.value.pop()

    for x in range(i*10, len(build_ele.nListBarresFrontAux.value)):
        build_ele.BarresFrontListAux.value.pop()

'''
def actualitzar_amb_noves_femelles(build_ele, FemellesAux, i):
    ''''''
    Afegir Femelles entremig i moure valors endevant en la llista
    get: FemellesAux -> Femelles a Inserir
         i -> Posicio

    return: -

    ''''''
    #***************FEMELLES******************
    inici = build_ele.nListFemellesVert.value[i].Posicio + build_ele.nListFemellesVert.value[i].nTotal
    final = inici + len(FemellesAux)

    listAnt = build_ele.FemellesVertListEN.value
    y = 0
    for x in range(inici, final):
        if x >= len(build_ele.FemellesVertListEN.value):
            build_ele.FemellesVertListEN.value.append(FemellesAux[y])
        elif build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(Femella = FemellesAux[y].Femella)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(FemellaOr = FemellesAux[y].FemellaOr)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaX = FemellesAux[y].PosFemellaX)
        y += 1

    y = build_ele.nListFemellesVert.value[i].nTotal + build_ele.nListFemellesVert.value[i].Posicio
    for x in range(final, len(build_ele.FemellesVertListEN.value)+len(FemellesAux)):
        if x >= len(build_ele.FemellesVertListEN.value):
            build_ele.FemellesVertListEN.value.append(listAnt[y])
        elif build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(Femella = listAnt[y].Femella)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(FemellaOr = listAnt[y].FemellaOr)
            build_ele.FemellesVertListEN.value[x] = build_ele.FemellesVertListEN.value[x]._replace(PosFemellaX = listAnt[y].PosFemellaX)
        y += 1

    build_ele.nListFemellesVert.value[i] = build_ele.nListFemellesVert.value[i]._replace(nTotal = build_ele.nListFemellesVert.value[i].nTotal + len(FemellesAux))
    if i+1 < len(build_ele.nListFemellesVert.value):
        build_ele.nListFemellesVert.value[i+1] = build_ele.nListFemellesVert.value[i+1]._replace(Posicio = build_ele.nListFemellesVert.value[i+1].Posicio + len(FemellesAux))
    for x  in range(build_ele.nListFemellesVert.value[i+1], len(build_ele.nListFemellesVert.value)):
        build_ele.nListFemellesVert.value[x] = build_ele.nListFemellesVert.value[x]._replace(Posicio = build_ele.nListFemellesVert.value[x].Posicio + build_ele.nListFemellesVert.value[x-1].nTotal)
'''

def mostrar_valors_horToShow(build_ele, posBarraHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges al BarresHorListToShowEN
    get: posBarraHor -> posicio[] barra Horitzontal

    return: -

    '''
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(BarraHor = build_ele.BarresHorListEN.value[posBarraHor].BarraHor)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Orientacio = build_ele.BarresHorListEN.value[posBarraHor].Orientacio)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Posicio = build_ele.BarresHorListEN.value[posBarraHor].Posicio)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(AutoLongitud = build_ele.BarresHorListEN.value[posBarraHor].AutoLongitud)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Longitud = build_ele.BarresHorListEN.value[posBarraHor].Longitud)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(BarraInici = build_ele.BarresHorListEN.value[posBarraHor].BarraInici)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(BarraFinal = build_ele.BarresHorListEN.value[posBarraHor].BarraFinal)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(Edit = build_ele.BarresHorListEN.value[posBarraHor].Edit)
    build_ele.BarresHorListToShowEN.value[0] = build_ele.BarresHorListToShowEN.value[0]._replace(acabatEditar = build_ele.BarresHorListEN.value[posBarraHor].acabatEditar)


def guardar_valors_horToShow(build_ele, posBarraHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges al BarresHorListToShowEN
    get: posBarraHor -> posicio[] barra Horitzontal

    return: -

    '''
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(BarraHor = build_ele.BarresHorListToShowEN.value[0].BarraHor)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Orientacio = build_ele.BarresHorListToShowEN.value[0].Orientacio)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Posicio = build_ele.BarresHorListToShowEN.value[0].Posicio)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(AutoLongitud = build_ele.BarresHorListToShowEN.value[0].AutoLongitud)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Longitud = build_ele.BarresHorListToShowEN.value[0].Longitud)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(BarraInici = build_ele.BarresHorListToShowEN.value[0].BarraInici)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(BarraFinal = build_ele.BarresHorListToShowEN.value[0].BarraFinal)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(Edit = build_ele.BarresHorListToShowEN.value[0].Edit)
    build_ele.BarresHorListEN.value[posBarraHor] = build_ele.BarresHorListEN.value[posBarraHor]._replace(acabatEditar = build_ele.BarresHorListToShowEN.value[0].acabatEditar)


#mostrar valors
def mostrar_valors_hor(build_ele, nBarraVert, nHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorListEN.value[nHor].Edit)

    build_ele.desplXVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplX
    build_ele.desplYVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplY

    build_ele.desplXHorAbs.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplX
    build_ele.desplYHorAbs.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplY
    #build_ele.desplZHorAbs.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplZ
    build_ele.desplZHorAbs.value = build_ele.BarresHorListEN.value[nBarraVert * NombreBarresHorInt + nHor].Posicio

    build_ele.mostrarLiniaVertA.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].mostrarLiniaVertA
    build_ele.desplVertLinA.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplLinA
    build_ele.mostrarLiniaVertB.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].mostrarLiniaVertB
    build_ele.desplVertLinB.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].desplLinB

    build_ele.SelectorLiniaHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].linia
    build_ele.SelectorLayerHorEN.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].layer

    build_ele.BarraAmpleHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].Ample
    build_ele.BarraAlturaHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].Altura
    #build_ele.BarraLlargadaVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].Llargada
    build_ele.BarraGruixHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].Gruix

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].IsUseGlobalProp
    build_ele.FounColorHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert * NombreBarresHorInt + nHor].BarraLayer

    build_ele.ColisVertListToShow.value[0] = build_ele.ColisHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 0]
    build_ele.ColisVertListToShow.value[1] = build_ele.ColisHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 1]
    build_ele.ColisVertListToShow.value[2] = build_ele.ColisHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 2]

    build_ele.PotesVertListToShow.value[0] = build_ele.PotesHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 0]
    build_ele.PotesVertListToShow.value[1] = build_ele.PotesHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 1]
    build_ele.PotesVertListToShow.value[2] = build_ele.PotesHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 2]

    build_ele.ForatsVertListToShowEN.value[0] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 0]
    build_ele.ForatsVertListToShowEN.value[0] = build_ele.ForatsVertListToShowEN.value[0]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[1] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 1]
    build_ele.ForatsVertListToShowEN.value[1] = build_ele.ForatsVertListToShowEN.value[1]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[2] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 2]
    build_ele.ForatsVertListToShowEN.value[2] = build_ele.ForatsVertListToShowEN.value[2]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[3] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 3]
    build_ele.ForatsVertListToShowEN.value[3] = build_ele.ForatsVertListToShowEN.value[3]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[4] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 4]
    build_ele.ForatsVertListToShowEN.value[4] = build_ele.ForatsVertListToShowEN.value[4]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[5] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 5]
    build_ele.ForatsVertListToShowEN.value[5] = build_ele.ForatsVertListToShowEN.value[5]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[6] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 6]
    build_ele.ForatsVertListToShowEN.value[6] = build_ele.ForatsVertListToShowEN.value[6]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[7] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 7]
    build_ele.ForatsVertListToShowEN.value[7] = build_ele.ForatsVertListToShowEN.value[7]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[8] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 8]
    build_ele.ForatsVertListToShowEN.value[8] = build_ele.ForatsVertListToShowEN.value[8]._replace(MostrarBox = False)
    build_ele.ForatsVertListToShowEN.value[9] = build_ele.ForatsHorInt.value[nBarraVert * NombreBarresHorInt + nHor*10 + 9]
    build_ele.ForatsVertListToShowEN.value[9] = build_ele.ForatsVertListToShowEN.value[9]._replace(MostrarBox = False)

    build_ele.FemellesVertListToShow.value[0] = build_ele.FemellesHorInt.value[nBarraVert * NombreBarresHorInt + nHor* 3 + 0]
    build_ele.FemellesVertListToShow.value[1] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1]
    build_ele.FemellesVertListToShow.value[2] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2]

    build_ele.Ample_forat_femellaVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella

    build_ele.posicio_centre_massesVert.value =  build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].posicio_centre_masses
    build_ele.IsFirstCancamVert.value=  build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].IsFirstCancam
    build_ele.Dis1cancamVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Dis1cancam
    build_ele.IsSecondCancamVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].IsSecondCancam
    build_ele.Dis2cancamVert.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Dis2cancam
    build_ele.PestanyaSuperiorHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].PestanyaSup
    build_ele.PestanyaInferiorHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].PestanyaInf
    build_ele.femellaSup.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].femellaSup
    build_ele.femellaInf.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].femellaInf

    build_ele.pestanyesInv.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].pestanyesInv

    build_ele.AtrPersAutomatic.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].AtrPersAutomatic
    build_ele.AtributPersonTub.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].AtributPersonTub
    build_ele.esVermellHor.value = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].vermell


    build_ele.EncaixVertListToShow.value[0] = build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0]
    build_ele.EncaixVertListToShow.value[1] = build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1]
    build_ele.EncaixVertListToShow.value[2] = build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2]

#guardar valors
def guardar_valors_hor(build_ele, nBarraVert, nHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorListEN.value[nHor].Edit)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplY = build_ele.desplYVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplX = build_ele.desplXHorAbs.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplY = build_ele.desplYHorAbs.value)
    build_ele.BarresHorListEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorListEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Posicio = build_ele.desplZHorAbs.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(linia = build_ele.SelectorLiniaHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(layer = build_ele.SelectorLayerHorEN.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample = build_ele.BarraAmpleHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura = build_ele.BarraAlturaHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Llargada = build_ele.BarraLlargadaVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Gruix = build_ele.BarraGruixHor.value)


    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(FounColor = build_ele.FounColorHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 +  1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 0] = build_ele.ForatsVertListToShowEN.value[0]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 1] = build_ele.ForatsVertListToShowEN.value[1]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 2] = build_ele.ForatsVertListToShowEN.value[2]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 3] = build_ele.ForatsVertListToShowEN.value[3]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 4] = build_ele.ForatsVertListToShowEN.value[4]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 5] = build_ele.ForatsVertListToShowEN.value[5]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 6] = build_ele.ForatsVertListToShowEN.value[6]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 7] = build_ele.ForatsVertListToShowEN.value[7]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 8] = build_ele.ForatsVertListToShowEN.value[8]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 9] = build_ele.ForatsVertListToShowEN.value[9]

    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesVertListToShow.value[2]


    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0]._replace(Separacio_forat_femella = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1]._replace(Separacio_forat_femella = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2]._replace(Separacio_forat_femella = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)


    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaSup = build_ele.PestanyaSuperiorHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaInf = build_ele.PestanyaInferiorHor.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(femellaSup = build_ele.femellaSup.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(femellaInf = build_ele.femellaInf.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(pestanyesInv = build_ele.pestanyesInv.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(AtrPersAutomatic = build_ele.AtrPersAutomatic.value)
    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(AtributPersonTub = build_ele.AtributPersonTub.value)

    build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInterEN.value[nBarraVert* NombreBarresHorInt + nHor]._replace(vermell = build_ele.esVermellHor.value)


    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.EncaixVertListToShow.value[0]
    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.EncaixVertListToShow.value[1]
    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.EncaixVertListToShow.value[2]



#guardar valors premarcs
def guardar_valors_incl(build_ele, nBarraVert, nHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -
    dadesENInclinades
    dadesENInclinades
    '''
    #build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorListEN.value[nHor].Edit)

    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(MostrarInclinat = build_ele.MostrarInclinat.value)

    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(nom = build_ele.nomPremarcEN.value)

    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplX = build_ele.desplXVertAbs.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplY = build_ele.desplYVertAbs.value)

    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample = build_ele.BarraAmpleVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura = build_ele.BarraAlturaVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Llargada = build_ele.BarraLlargadaVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Gruix = build_ele.BarraGruixVert.value)


    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(FounColor = build_ele.FounColor.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    '''
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 +  1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 0] = build_ele.ForatsVertListToShowEN.value[0]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 1] = build_ele.ForatsVertListToShowEN.value[1]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 2] = build_ele.ForatsVertListToShowEN.value[2]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 3] = build_ele.ForatsVertListToShowEN.value[3]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 4] = build_ele.ForatsVertListToShowEN.value[4]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 5] = build_ele.ForatsVertListToShowEN.value[5]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 6] = build_ele.ForatsVertListToShowEN.value[6]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 7] = build_ele.ForatsVertListToShowEN.value[7]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 8] = build_ele.ForatsVertListToShowEN.value[8]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 9] = build_ele.ForatsVertListToShowEN.value[9]

    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesVertListToShow.value[2]


    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0]._replace(Separacio_forat_femella = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1]._replace(Separacio_forat_femella = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2]._replace(Separacio_forat_femella = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    '''
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)


    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaInf = build_ele.PestanyaInferiorVert.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(femellaSup = build_ele.femellaSup.value)
    build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesENInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(femellaInf = build_ele.femellaInf.value)

    '''
    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.EncaixVertListToShow.value[0]
    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.EncaixVertListToShow.value[1]
    build_ele.EncaixHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.EncaixVertListToShow.value[2]
    '''


#set valors Vert
def set_valors_incl(build_ele, nBarraVert):
    '''
    definir valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    while nBarraVert >= len(build_ele.dadesENInclinades.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'MostrarInclinat nom Ample Altura Llargada Gruix desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf femellaSup femellaInf Posicio Angle')
        bob = TDHorCollection(MostrarInclinat = False,
                              nom = "",
                            Ample = 950,
                            Altura = 2180,
                            Llargada = build_ele.BarraLlargadaVert.value,
                            Gruix = build_ele.BarraGruixVert.value,
                            desplX = 0.0,
                            desplY = 0.0,
                            mostrarLiniaVertA = True,
                            desplLinA = 0,
                            mostrarLiniaVertB = False,
                            desplLinB = 0,
                            estaEditant = False,
                            acabatEditar = False,
                            IsUseGlobalProp = False,
                            FounColor = 1,
                            BarraLayer = 1,
                            Ample_forat_femella = 15,
                            Altura_forat_femella = 2,#3.0,
                            Separacio_forat_femella = 30,
                            posicio_centre_masses = 500,
                            IsFirstCancam = False,
                            Dis1cancam = 500,
                            IsSecondCancam =False,
                            Dis2cancam = 1000,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            femellaSup = True,
                            femellaInf = True,
                            Posicio = 0,
                            Angle = 0)
        build_ele.dadesENInclinades.value.append(bob)

    '''
    while nBarraVert * 3 + nHor * 3 + 3 >= len(build_ele.ColisHorInt.value):
        build_ele.ColisHorInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1] = build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1]._replace(Colis = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.PotesHorInt.value):
        build_ele.PotesHorInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1] = build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1]._replace(Pota = False)
    while nBarraVert * 3 + nHor *3 + 8 >= len(build_ele.ForatsHorInt.value):
        build_ele.ForatsHorInt.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1] = build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1]._replace(Forat = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.FemellesHorInt.value):
        build_ele.FemellesHorInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1] = build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1]._replace(Femella = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.EncaixHorInt.value):
        build_ele.EncaixHorInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1] = build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1]._replace(Encaix = False)
    '''

#set valors Vert
def set_valors_hor_femelles(build_ele, nBarraVert):
    '''
    definir valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''
    while (nBarraVert+2 + 2) * NombreBarresVertInt + 5 >= len(build_ele.FemellesHorIntAux.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
        bob = TDHorCollection(Femella = False,
                            FemellaOr = 'Esq',
                            PosFemellaX = 0.0,
                            PosFemellaY = 0.0,
                            Separacio_forat_femella = 0.0)
        build_ele.FemellesHorIntAux.value.append(bob)

#set valors Vert
def set_valors_hor_femelles2(build_ele, j, nBarraVert):
    '''
    definir valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''
    while j*150+ ((nBarraVert + 2)* NombreBarresVertInt )+ 3 >= len(build_ele.FemellesHorIntAux.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
        bob = TDHorCollection(Femella = False,
                            FemellaOr = 'Esq',
                            PosFemellaX = 0.0,
                            PosFemellaY = 0.0,
                            Separacio_forat_femella = 0.0)
        build_ele.FemellesHorIntAux.value.append(bob)


def add_femella(build_ele, nBarraHor, j , nBarraVert, pos, pos2, orientacio, separacioForatfemella, mostrar, Ample, Altura, desply, desplAct, barraInici, barraSupHor):
    afegit = False

    if nBarraHor == 0:
        x = j* 20 + nBarraVert
        while x+1 > len(build_ele.FemellesHorIntAuxInf.value):
            TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
            bob = TDHorCollection(Femella = False,
                                  FemellaOr = 'Esq',
                                  PosFemellaX = 0.0,
                                  PosFemellaY = 0.0,
                                  Separacio_forat_femella = 30)
            build_ele.FemellesHorIntAuxInf.value.append(bob)
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(Femella = mostrar)
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(FemellaOr = orientacio)
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(PosFemellaX = pos2)
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(PosFemellaY = Altura/2 - 15/2 + desply - build_ele.desplYI.value)
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(Separacio_forat_femella = separacioForatfemella)
        afegit = True

    elif nBarraHor == 1:
        x = j* 20 + 4 + nBarraVert
        while x+1 > len(build_ele.FemellesHorIntAuxSup.value):
            TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
            bob = TDHorCollection(Femella = False,
                                  FemellaOr = 'Dre',
                                  PosFemellaX = 0.0,
                                  PosFemellaY = 0.0,
                                  Separacio_forat_femella = 30)
            build_ele.FemellesHorIntAuxSup.value.append(bob)
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(Femella = mostrar)
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(FemellaOr = orientacio)
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(PosFemellaX = pos2)
        if Altura/2 - 15/2 + desply - build_ele.desplYS.value == 0:
            desply = desply+0.1
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(PosFemellaY = Altura/2 - 15/2 + desply - build_ele.desplYS.value)
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(Separacio_forat_femella = separacioForatfemella)
        afegit = True
    else:
        x = nBarraHor
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(Femella = mostrar)
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(FemellaOr = orientacio)
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(PosFemellaX = pos - 0.5)
        if orientacio == "Sup" or orientacio == "Inf":
            posY = 0
        else:
            if barraInici == "Inferior" and orientacio == "Dre":
                posY = Altura/2 - 15/2 + desply - build_ele.desplYI.value + desplAct - build_ele.listDesplVerticalsEN.value[j].desplY - build_ele.dadesTDHortInterEN.value[barraSupHor].desplY
            else:
                if orientacio == "Esq":
                    posY = Altura/2 - 15/2 + desply  - desplAct - build_ele.listDesplVerticalsEN.value[j].desplY #- build_ele.dadesTDHortInterEN.value
                else:
                    posY = Altura/2 - 15/2 + desply   - build_ele.listDesplVerticalsEN.value[j].desplY - build_ele.dadesTDHortInterEN.value[barraSupHor].desplY
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(PosFemellaY = posY)
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(Separacio_forat_femella = separacioForatfemella + 0.75)
        afegit = True
    return afegit

def set_femella_to_false(build_ele, j, k,):

    if len(build_ele.FemellesHorIntAuxInf.value)>(j*20) + k :
        x = (j*20) + k  #horInf
        build_ele.FemellesHorIntAuxInf.value[x] = build_ele.FemellesHorIntAuxInf.value[x]._replace(Femella = False)
    if len(build_ele.FemellesHorIntAuxSup.value)>(j*20+4) + k :
        x = (j*20+4) + k  #horSup
        build_ele.FemellesHorIntAuxSup.value[x] = build_ele.FemellesHorIntAuxSup.value[x]._replace(Femella = False)
    if len(build_ele.FemellesHorIntAux.value)>(j*20+16) + k :
        x = (j*20+8) + k  #barra1
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(Femella = False)
        x = (j*20+12) + k  #barra2
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(Femella = False)
        x = (j*20+16) + k  #barra3
        build_ele.FemellesHorIntAux.value[x] = build_ele.FemellesHorIntAux.value[x]._replace(Femella = False)

def get_fem_aux(build_ele, nBarra):
    listFemelles = []
    x = nBarra * 4
    end = (nBarra ) * 4 + 4

    while x != end:
        listFemelles.append(build_ele.FemellesHorIntAux.value[x])
        x += 1

    return listFemelles

#set valors Vert
def set_valors_hor_ini(build_ele, nBarraVert, nHor):
    '''
    definir valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    while nBarraVert * 3 + nHor >= len(build_ele.dadesTDHortInterEN.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'Ample Altura Llargada Gruix desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf femellaSup femellaInf pestanyesInv AtrPersAutomatic AtributPersonTub linia layer vermell')
        bob = TDHorCollection(Ample = 10,
                            Altura = 50,
                            Llargada = build_ele.BarraLlargadaEN.value,
                            Gruix = build_ele.BarraGruixVert.value,
                            desplX = 0.0,
                            desplY = 0.0,
                            mostrarLiniaVertA = True,
                            desplLinA = 0,
                            mostrarLiniaVertB = False,
                            desplLinB = 0,
                            estaEditant = False,
                            acabatEditar = False,
                            IsUseGlobalProp = False,
                            FounColor = 1,
                            BarraLayer = 40076,
                            Ample_forat_femella = 15,
                            Altura_forat_femella = 2,#3.0,
                            Separacio_forat_femella = 30,
                            posicio_centre_masses = 500,
                            IsFirstCancam = False,
                            Dis1cancam = 500,
                            IsSecondCancam =False,
                            Dis2cancam = 1000,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            femellaSup = True,
                            femellaInf = True,
                            pestanyesInv = False,
                            AtrPersAutomatic = True,
                            AtributPersonTub = "EXD",
                            linia = "Tipus 1",
                            layer = "EN_ESTRUCTURA",
                            vermell= False)
        build_ele.dadesTDHortInterEN.value.append(bob)

    while nBarraVert * 3 + nHor * 3 + 3 >= len(build_ele.ColisHorInt.value):
        build_ele.ColisHorInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1] = build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1]._replace(Colis = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.PotesHorInt.value):
        build_ele.PotesHorInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1] = build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1]._replace(Pota = False)
    while nBarraVert * 3 + nHor *3 + 8 >= len(build_ele.ForatsHorInt.value):
        build_ele.ForatsHorInt.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1] = build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1]._replace(Forat = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.FemellesHorInt.value):
        build_ele.FemellesHorInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1] = build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1]._replace(Femella = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.EncaixHorInt.value):
        build_ele.EncaixHorInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1] = build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1]._replace(Encaix = False)

#mostrar valors Vert
def mostrar_valors_Vert(build_ele, nBarraVert, nVert):
    nBarresVertInt = NombreBarresVertInt
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(estaEditant = build_ele.BarresVertListToShow.value[nVert].Edit)

    build_ele.BarraAmpleVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraAmple
    build_ele.BarraAlturaVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraAltura
    build_ele.BarraGruix.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraGruix


    build_ele.desplXVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].desplX
    build_ele.desplYVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].desplY
    build_ele.desplXVertAbs.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].desplXAbs
    build_ele.desplYVertAbs.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].desplYAbs

    #build_ele.desplXVert.value = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].desplX
    #build_ele.desplYVert.value  = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].desplY
    build_ele.mostrarLiniaVertA.value = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].mostrarLiniaVertA
    build_ele.desplVertLinA.value = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].desplLinA
    build_ele.mostrarLiniaVertB.value = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].mostrarLiniaVertB
    build_ele.desplVertLinB.value = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert].desplLinB

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraLayer

    build_ele.Ample_forat_femellaVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].Separacio_forat_femella

    build_ele.ColisVertListToShow.value[0] = build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0]
    build_ele.ColisVertListToShow.value[1] = build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1]
    build_ele.ColisVertListToShow.value[2] = build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2]

    build_ele.PotesVertListToShow.value[0] = build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0]
    build_ele.PotesVertListToShow.value[1] = build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1]
    build_ele.PotesVertListToShow.value[2] = build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2]

    build_ele.ForatsVertListToShowEN.value[0] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 0]
    build_ele.ForatsVertListToShowEN.value[1] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 1]
    build_ele.ForatsVertListToShowEN.value[2] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 2]
    build_ele.ForatsVertListToShowEN.value[3] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 3]
    build_ele.ForatsVertListToShowEN.value[4] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 4]
    build_ele.ForatsVertListToShowEN.value[5] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 5]
    build_ele.ForatsVertListToShowEN.value[6] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 6]
    build_ele.ForatsVertListToShowEN.value[7] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 7]
    build_ele.ForatsVertListToShowEN.value[8] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 8]
    build_ele.ForatsVertListToShowEN.value[9] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 9]

    build_ele.FemellesVertListToShow.value[0] = build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0]
    build_ele.FemellesVertListToShow.value[1] = build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1]
    build_ele.FemellesVertListToShow.value[2] = build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2]

    build_ele.posicio_centre_massesVert.value =  build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].posicio_centre_masses
    build_ele.IsFirstCancamVert.value=  build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].IsFirstCancam
    build_ele.Dis1cancamVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].Dis1cancam
    build_ele.IsSecondCancamVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].IsSecondCancam
    build_ele.Dis2cancamVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].Dis2cancam

    build_ele.EncaixVertListToShow.value[0] = build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0]
    build_ele.EncaixVertListToShow.value[1] = build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1]
    build_ele.EncaixVertListToShow.value[2] = build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2]

    build_ele.PestanyaSuperiorVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].pestanyaSup
    build_ele.PestanyaInferiorVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].pestanyaInf

    #build_ele.femellaSup.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].FemellaSupe
    #build_ele.femellaInf.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].FemellaInfe
    build_ele.BarresVertListToShow.value[nVert] = build_ele.BarresVertListToShow.value[nVert]._replace(FemellaSup = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].FemellaSupe)
    build_ele.BarresVertListToShow.value[nVert] = build_ele.BarresVertListToShow.value[nVert]._replace(FemellaInf = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].FemellaInfe)
#guardar valors Vert
def guardar_valors_Vert(build_ele, nBarraVert, nVert):
    nBarresVertInt = NombreBarresVertInt
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(estaEditant = build_ele.BarresVertListToShow.value[nVert].Edit)

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(BarraAmple = build_ele.BarraAmpleVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(BarraAltura = build_ele.BarraAlturaVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(BarraGruix = build_ele.BarraGruix.value)


    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(desplY = build_ele.desplYVert.value)

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(desplXAbs = build_ele.desplXVertAbs.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(desplYAbs = build_ele.desplYVertAbs.value)

    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(desplX = build_ele.desplXVert.value )
    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(desplY = build_ele.desplYVert.value )
    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert] = build_ele.listDesplVerticalsInteriors.value[nBarraVert * nBarresVertInt + nVert]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)

    build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 0] = build_ele.ForatsVertListToShowEN.value[0]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 1] = build_ele.ForatsVertListToShowEN.value[1]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 2] = build_ele.ForatsVertListToShowEN.value[2]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 3] = build_ele.ForatsVertListToShowEN.value[3]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 4] = build_ele.ForatsVertListToShowEN.value[4]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 5] = build_ele.ForatsVertListToShowEN.value[5]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 6] = build_ele.ForatsVertListToShowEN.value[6]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 7] = build_ele.ForatsVertListToShowEN.value[7]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 8] = build_ele.ForatsVertListToShowEN.value[8]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 9] = build_ele.ForatsVertListToShowEN.value[9]

    build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2] = build_ele.FemellesVertListToShow.value[2]

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)

    #build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert] = build_ele.EncaixVertListToShow.value[nVert]
    build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 0] = build_ele.EncaixVertListToShow.value[0]
    build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 1] = build_ele.EncaixVertListToShow.value[1]
    build_ele.EncaixVertInt.value[nBarraVert * nBarresVertInt + nVert* 4 + 2] = build_ele.EncaixVertListToShow.value[2]

    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(pestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(pestanyaInf = build_ele.PestanyaInferiorVert.value)


    #build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(FemellaSupe = build_ele.femellaSup.value)
    #build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(FemellaInfe = build_ele.femellaInf.value)

    #build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(FemellaSupe = build_ele.BarresVertListToShow.value[nVert].FemellaSup)
    #build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(FemellaInfe = build_ele.BarresVertListToShow.value[nVert].FemellaInf)

#set valors Vert
def set_valors_Ref_ini(build_ele, nBarraVert):
    '''
    definir valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    while nBarraVert >= len(build_ele.dadesENReftInter.value):
        ENRefCollection = collections.namedtuple('StirrupList', 'Ample Altura Llargada Gruix Orientacio desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf linia layer')
        bob = ENRefCollection(Ample = 30,
                            Altura = 30,
                            Llargada = build_ele.BarraLlargadaVert.value,
                            #Gruix = build_ele.BarraGruixVert.value,
                            Gruix = 2,
                            Orientacio = "Inf",
                            desplX = 0.0,
                            desplY = 0.0,
                            mostrarLiniaVertA = True,
                            desplLinA = 0,
                            mostrarLiniaVertB = False,
                            desplLinB = 0,
                            estaEditant = False,
                            acabatEditar = False,
                            IsUseGlobalProp = False,
                            FounColor = 1,
                            BarraLayer = 40076,
                            Ample_forat_femella = 15,
                            Altura_forat_femella = 2,#3.0,
                            Separacio_forat_femella = 30,
                            posicio_centre_masses = 500,
                            IsFirstCancam = False,
                            Dis1cancam = 500,
                            IsSecondCancam =False,
                            Dis2cancam = 1000,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            linia = "Tipus 1",
                            layer = "EN_ESTRUCTURA")
        build_ele.dadesENReftInter.value.append(bob)

    '''
    while nBarraVert  * 3 + 3 >= len(build_ele.ColisRefInt.value):
        build_ele.ColisRefInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisRefInt.value[len(build_ele.ColisRefInt.value)-1] = build_ele.ColisRefInt.value[len(build_ele.ColisRefInt.value)-1]._replace(Colis = False)
    while nBarraVert  *3 + 3 >= len(build_ele.PotesRefInt.value):
        build_ele.PotesRefInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesRefInt.value[len(build_ele.PotesRefInt.value)-1] = build_ele.PotesRefInt.value[len(build_ele.PotesRefInt.value)-1]._replace(Pota = False)
    while nBarraVert  *3 + 8 >= len(build_ele.ForatsRefInt.value):
        build_ele.ForatsRefInt.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsRefInt.value[len(build_ele.ForatsRefInt.value)-1] = build_ele.ForatsRefInt.value[len(build_ele.ForatsRefInt.value)-1]._replace(Forat = False)
    while nBarraVert  *3 + 3 >= len(build_ele.FemellesRefInt.value):
        build_ele.FemellesRefInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesRefInt.value[len(build_ele.FemellesRefInt.value)-1] = build_ele.FemellesRefInt.value[len(build_ele.FemellesRefInt.value)-1]._replace(Femella = False)

    while nBarraVert  *3 + 3 >= len(build_ele.EncaixRefInt.value):
        build_ele.EncaixRefInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixRefInt.value[len(build_ele.EncaixRefInt.value)-1] = build_ele.EncaixRefInt.value[len(build_ele.EncaixRefInt.value)-1]._replace(Encaix = False)
    '''

#set valors Vert
def set_valors_Vert_ini(build_ele, nBarraVert, Nvert):
    nBarresVertInt = NombreBarresVertInt
    while nBarraVert * nBarresVertInt + Nvert >= len(build_ele.dadesTDVertInter.value)-1:
        TDVertCollection = collections.namedtuple('StirrupList', 'estaEditant acabatEditar BarraAmple BarraAltura BarraGruix desplX desplXAbs desplY desplYAbs IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam pestanyaSup pestanyaInf FemellaSup FemellaInf FemellaSupe FemellaInfe')
        bob = TDVertCollection( estaEditant = False,
                                acabatEditar = False,
                                BarraAmple = 30,
                                BarraAltura = 30,
                                BarraGruix = 1.5,
                                desplX = 0.0,
                                desplXAbs = 0,
                                desplY = 0.0,
                                desplYAbs = 0,
                                IsUseGlobalProp = False,
                                FounColor = 1,
                                BarraLayer = 40076,
                                Ample_forat_femella = 15,
                                Altura_forat_femella = 2,#3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = True,
                                pestanyaInf = True,
                                FemellaSup = False,
                                FemellaInf = False,
                                FemellaSupe = False,
                                FemellaInfe= False)
        build_ele.dadesTDVertInter.value.append(bob)

    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.ColisVertInt.value):
        build_ele.ColisVertInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisVertInt.value[len(build_ele.ColisVertInt.value)-1] = build_ele.ColisVertInt.value[len(build_ele.ColisVertInt.value)-1]._replace(Colis = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.PotesVertInt.value):
        build_ele.PotesVertInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesVertInt.value[len(build_ele.PotesVertInt.value)-1] = build_ele.PotesVertInt.value[len(build_ele.PotesVertInt.value)-1]._replace(Pota = False)
    while (nBarraVert * nBarresVertInt + Nvert) * 10 + 10 >= len(build_ele.ForatsVertInt.value):
        build_ele.ForatsVertInt.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsVertInt.value[len(build_ele.ForatsVertInt.value)-1] = build_ele.ForatsVertInt.value[len(build_ele.ForatsVertInt.value)-1]._replace(Forat = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.FemellesVertInt.value):
        build_ele.FemellesVertInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesVertInt.value[len(build_ele.FemellesVertInt.value)-1] = build_ele.FemellesVertInt.value[len(build_ele.FemellesVertInt.value)-1]._replace(Femella = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.EncaixVertInt.value):
        build_ele.EncaixVertInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixVertInt.value[len(build_ele.EncaixVertInt.value)-1] = build_ele.EncaixVertInt.value[len(build_ele.EncaixVertInt.value)-1]._replace(Encaix = False)

"""
def get_valors_actuals(build_ele, j):
    '''
    retorna valors de la Barra Actual
    get:j -> posicio[] de la barra

    return: Encaixos[], Femelles[], Potes[], Forats[], Colis[]

    '''
    Encaixos = []
    for x in range(build_ele.nListEncaixVert.value[j].Posicio, build_ele.nListEncaixVert.value[j].Posicio + build_ele.nListEncaixVert.value[j].nTotal):
        if x >= len(build_ele.EncaixVertList.value):
            set_values_encaix(build_ele, x)
        Encaixos.append(build_ele.EncaixVertList.value[x])

    Femelles = []
    for x in range(build_ele.nListFemellesVert.value[j].Posicio, build_ele.nListFemellesVert.value[j].Posicio + build_ele.nListFemellesVert.value[j].nTotal):
        if x >= len(build_ele.FemellesVertListEN.value):
            set_values_femelles(build_ele, x)
        Femelles.append(build_ele.FemellesVertListEN.value[x])

    Potes = []
    for x in range(build_ele.nListPotesVert.value[j].Posicio, build_ele.nListPotesVert.value[j].Posicio + build_ele.nListPotesVert.value[j].nTotal):
        if x >= len(build_ele.PotesVertList.value):
            set_values_potes(build_ele, x)
        Potes.append(build_ele.PotesVertList.value[x])

    Forats = []
    for x in range(build_ele.nListForatsVert.value[j].Posicio, build_ele.nListForatsVert.value[j].Posicio + build_ele.nListForatsVert.value[j].nTotal):
        if x >= len(build_ele.ForatsVertListEN.value):
            set_values_forats(build_ele, x)
        Forats.append(build_ele.ForatsVertListEN.value[x])

    Colis = []
    for x in range(build_ele.nListColisVert.value[j].Posicio, build_ele.nListColisVert.value[j].Posicio + build_ele.nListColisVert.value[j].nTotal):
        if x >= len(build_ele.ColisVertList.value):
            set_values_colis(build_ele, x)
        Colis.append(build_ele.ColisVertList.value[x])

    return Encaixos, Femelles, Potes, Forats, Colis
"""
def get_valors_actuals(build_ele, j, AmpleSup):
    '''
    retorna valors de la Barra Actual
    get:j -> posicio[] de la barra

    return: Encaixos[], Femelles[], Potes[], Forats[], Colis[]

    '''

    while j >= len(build_ele.nListEncaixVert.value):
        i = len(build_ele.nListEncaixVert.value)
        ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
        bob = ENCollection( Posicio = build_ele.nListEncaixVert.value[i-1].Posicio + build_ele.nListEncaixVert.value[i-1].nTotal,
                            nTotal = 3)
        build_ele.nListEncaixVert.value.append(bob)

    Encaixos = []
    for x in range(build_ele.nListEncaixVert.value[j].Posicio, build_ele.nListEncaixVert.value[j].Posicio + build_ele.nListEncaixVert.value[j].nTotal):
        if x >= len(build_ele.EncaixVertList.value):
            set_values_encaix(build_ele, x)
        Encaixos.append(build_ele.EncaixVertList.value[x])
    #if not build_ele.dadesTDVertEN.value[j].EncaixSup :#and build_ele.desplYS.value - (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) >= 0:
    nBarraINF = 0
    nBarraSup = 1
    posicioInicial = build_ele.BarraAlturaInf.value
    posicoFinal = build_ele.desplZS.value + build_ele.BarraAlturaSup.value/2 + build_ele.BarraAlturaInf.value
    sumatori = 0
    alturaInf = 0#-build_ele.BarraAlturaInf.value
    alturaSup = build_ele.BarraAlturaSup.value
    ampleSup = AmpleSup
    if build_ele.dadesTDVertEN.value[j].BarraSuperior != "EN Superior":
        if len(build_ele.dadesTDVertEN.value[j].BarraSuperior) == 5:
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-1]
            nBarraSup = int(nBarraSup)
        elif len(build_ele.dadesTDVertEN.value[j].BarraSuperior) == 6:
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-2]
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-1] + nBarraSup
            nBarraSup = int(nBarraSup)
        elif len(build_ele.dadesTDVertEN.value[j].BarraSuperior) == 7:
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-3]
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-2] + nBarraSup
            nBarraSup = build_ele.dadesTDVertEN.value[j].BarraSuperior[-1] + nBarraSup
            nBarraSup = int(nBarraSup)
        posicoFinal = build_ele.BarresHorListEN.value[nBarraSup].Posicio
        if nBarraSup >= len(build_ele.dadesTDHortInterEN.value):
            set_valors_hor_ini(build_ele, 0, nBarraSup)
        alturaSup = build_ele.dadesTDHortInterEN.value[nBarraSup].Altura


    if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
        nBarraInf = 0
        if len(build_ele.dadesTDVertEN.value[j].BarraInferior) == 5:
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-1]
            nBarraInf = int(nBarraInf)
        elif len(build_ele.dadesTDVertEN.value[j].BarraInferior) == 6:
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-2]
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-1] + nBarraInf
            nBarraInf = int(nBarraInf)
        elif len(build_ele.dadesTDVertEN.value[j].BarraInferior) == 7:
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-3]
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-2] + nBarraInf
            nBarraInf = build_ele.dadesTDVertEN.value[j].BarraInferior[-1] + nBarraInf
            nBarraInf = int(nBarraInf)
        posicioInicial = build_ele.BarresHorListEN.value[nBarraInf].Posicio
        if nBarraInf >= len(build_ele.dadesTDHortInterEN.value):
            set_valors_hor_ini(build_ele, 0, nBarraInf)
        alturaInf = build_ele.dadesTDHortInterEN.value[nBarraInf].Altura


        if not build_ele.dadesTDVertEN.value[j].EncaixInf:
            sumatori += build_ele.dadesTDHortInterEN.value[nBarraInf].Altura

        orientacioInf = "Dre"
        try:
            if build_ele.dadesTDVertEN.value[j].invertirEncaixInf:
                orientacioInf = "Esq"
        except Exception as e:
            build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(invertirEncaixInf = build_ele.invertirEncaixVertInf.value)
            print("valor invertirEncaixInf no guardat a la barra: " + str(j))
        if build_ele.dadesTDVertEN.value[j].invertirEncaixInf:
            orientacioInf = "Esq"

        posicio =  build_ele.dadesTDHortInterEN.value[nBarraInf].Altura/2
        if orientacioInf == "Dre":
            Profunditat = build_ele.dadesTDHortInterEN.value[nBarraInf].desplY + build_ele.dadesTDHortInterEN.value[nBarraInf].Ample + (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) +1
        else:
            Profunditat = build_ele.dadesTDHortInterEN.value[nBarraInf].desplY + build_ele.dadesTDHortInterEN.value[nBarraInf].Ample + (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) +1
            #Profunditat = build_ele.dadesTDVertEN.value[j].BarraAltura - Profunditat
        ENCollection = collections.namedtuple('StirrupList', 'BarraFront EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
        bob = ENCollection( BarraFront = not build_ele.dadesTDVertEN.value[j].EncaixInf,
                            EncaixOr = orientacioInf,
                            Longitud = alturaInf,
                            Amplitud = build_ele.dadesTDVertEN.value[j].BarraAmple,
                            Posicio = posicio,# build_ele.desplZS.value ,#- build_ele.BarraAlturaSup.value/2,#+ build_ele.BarraAlturaInf.value,
                            Profunditat = Profunditat ,
                            Pestanya = False,
                            Separator = '')
        if Profunditat > 0:
            Encaixos.append(bob)

    #posicio = posicoFinal + alturaSup/2 - posicioInicial
    posicio = posicoFinal - (posicioInicial ) +alturaSup/2 #+ build_ele.BarraAlturaInf.value #+ sumatori - alturaSup/2
    if  build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior":
        posicio = posicoFinal - (posicioInicial - alturaInf/2) + alturaSup/2 #+ sumatori - alturaSup/2
        #posicio = posicoFinal - posicioInicial + alturaSup/2
        posicio = posicoFinal - posicioInicial - build_ele.BarraAlturaInf.value #- alturaSup/2 #+alturaInf/2
    if  build_ele.dadesTDVertEN.value[j].BarraInferior == "EN Inferior":
        posicio = posicoFinal - (posicioInicial ) +alturaSup/2 + build_ele.BarraAlturaInf.value
        if build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior":
            posicio = posicoFinal - posicioInicial
        Profunditat =  build_ele.desplYS.value + (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) +1
    else:
        Profunditat = build_ele.dadesTDHortInterEN.value[nBarraSup].desplY + build_ele.dadesTDHortInterEN.value[nBarraSup].Ample + (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) +1

    if build_ele.dadesTDVertEN.value[j].EncaixInf and not build_ele.dadesTDVertEN.value[j].EncaixSup and build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
        posicio -= alturaInf


    orientacioSup = "Dre"

    try:
        if build_ele.dadesTDVertEN.value[j].invertirEncaixSup:
            orientacioSup = "Esq"
    except Exception as e:
        build_ele.dadesTDVertEN.value[j] = build_ele.dadesTDVertEN.value[j]._replace(invertirEncaixSup = build_ele.invertirEncaixVertSup.value)
        print("valor invertirEncaixSup no guardat a la barra: " + str(j))
    if build_ele.dadesTDVertEN.value[j].invertirEncaixSup:
        orientacioSup = "Esq"

    if build_ele.dadesTDVertEN.value[j].BarraSuperior == "EN Superior":
        if orientacioSup == "Esq":
            Profunditat = build_ele.dadesTDVertEN.value[j].BarraAltura - Profunditat
        else:
            Profunditat = build_ele.desplYS.value + (-build_ele.listDesplVerticalsEN.value[j].desplYAbs) + ampleSup
    ENCollection = collections.namedtuple('StirrupList', 'BarraFront EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
    bob = ENCollection( BarraFront = not build_ele.dadesTDVertEN.value[j].EncaixSup,
                        EncaixOr = orientacioSup,
                        Longitud = alturaSup,
                        Amplitud = build_ele.dadesTDVertEN.value[j].BarraAmple,
                        Posicio = posicio,# build_ele.desplZS.value ,#- build_ele.BarraAlturaSup.value/2,#+ build_ele.BarraAlturaInf.value,
                        Profunditat = Profunditat ,
                        Pestanya = False,
                        Separator = '')
    if Profunditat > 0:
        Encaixos.append(bob)

    while j >= len(build_ele.nListFemellesVert.value):
        i = len(build_ele.nListFemellesVert.value)
        ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
        bob = ENCollection( Posicio = build_ele.nListFemellesVert.value[i-1].Posicio + build_ele.nListFemellesVert.value[i-1].nTotal,
                            nTotal = 3)
        build_ele.nListFemellesVert.value.append(bob)
    Femelles = []
    for x in range(build_ele.nListFemellesVert.value[j].Posicio, build_ele.nListFemellesVert.value[j].Posicio + build_ele.nListFemellesVert.value[j].nTotal):
        if x >= len(build_ele.FemellesVertListEN.value):
            set_values_femelles(build_ele, x)
        Femelles.append(build_ele.FemellesVertListEN.value[x])

    if (j == 0 or j == build_ele.IntegerENSelector.value-1) and ( build_ele.TubSuperior.value == "TUB Interior"):
        orientSupA = "Inf"
        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Separator')
        bob = TDHorCollection(Femella = build_ele.MostrarTDHoritzontalSup.value,
                            FemellaOr = orientSupA,
                            PosFemellaX = build_ele.desplZS.value ,#- build_ele.BarraAlturaSup.value/2 ,
                            PosFemellaY = build_ele.desplYS.value - build_ele.listDesplVerticalsEN.value[j].desplYAbs + AmpleSup/2 - AmpleSup/4,
                            Separacio_forat_femella = build_ele.BarraAlturaSup.value ,
                            PosFemellaXOri = 0,
                            Ample_forat_femella = AmpleSup/2,#3,
                            Separator = '')
        Femelles.append(bob)
        orientSupA = "Sup"
        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Separator')
        bob = TDHorCollection(Femella = build_ele.MostrarTDHoritzontalSup.value,
                            FemellaOr = orientSupA,
                            PosFemellaX = build_ele.desplZS.value ,#- build_ele.BarraAlturaSup.value/2 ,
                            PosFemellaY = build_ele.desplYS.value - build_ele.listDesplVerticalsEN.value[j].desplYAbs + AmpleSup/2 - AmpleSup/4,
                            Separacio_forat_femella = build_ele.BarraAlturaSup.value ,
                            PosFemellaXOri = 0,
                            Ample_forat_femella = AmpleSup/2,#3,
                            Separator = '')
        Femelles.append(bob)


    while j >= len(build_ele.nListPotesVert.value):
        i = len(build_ele.nListPotesVert.value)
        ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
        bob = ENCollection( Posicio = build_ele.nListPotesVert.value[i-1].Posicio + build_ele.nListPotesVert.value[i-1].nTotal,
                            nTotal = 3)
        build_ele.nListPotesVert.value.append(bob)
    Potes = []
    for x in range(build_ele.nListPotesVert.value[j].Posicio, build_ele.nListPotesVert.value[j].Posicio + build_ele.nListPotesVert.value[j].nTotal):
        if x >= len(build_ele.PotesVertList.value):
            set_values_potes(build_ele, x)
        Potes.append(build_ele.PotesVertList.value[x])

    Forats = []
    while j >= len(build_ele.nListForatsVert.value):
        i = len(build_ele.nListForatsVert.value)
        ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
        bob = ENCollection( Posicio = build_ele.nListForatsVert.value[i-1].Posicio + build_ele.nListForatsVert.value[i-1].nTotal,
                            nTotal = 3)
        build_ele.nListForatsVert.value.append(bob)
    for x in range(build_ele.nListForatsVert.value[j].Posicio, build_ele.nListForatsVert.value[j].Posicio + build_ele.nListForatsVert.value[j].nTotal):
        if x >= len(build_ele.ForatsVertListEN.value):
            set_values_forats(build_ele, x)
        Forats.append(build_ele.ForatsVertListEN.value[x])

    Colis = []
    while j >= len(build_ele.nListColisVert.value):
        i = len(build_ele.nListColisVert.value)
        ENCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
        bob = ENCollection( Posicio = build_ele.nListColisVert.value[i-1].Posicio + build_ele.nListColisVert.value[i-1].nTotal,
                            nTotal = 3)
        build_ele.nListColisVert.value.append(bob)
    for x in range(build_ele.nListColisVert.value[j].Posicio, build_ele.nListColisVert.value[j].Posicio + build_ele.nListColisVert.value[j].nTotal):
        if x >= len(build_ele.ColisVertList.value):
            set_values_colis(build_ele, x)
        Colis.append(build_ele.ColisVertList.value[x])

    return Encaixos, Femelles, Potes, Forats, Colis


def mostrar_valors_adjacents(build_ele,posBarraHor):

    if build_ele.BarresAdjListEN.value[posBarraHor].Longitud <= 0:
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(BarraAdj = False)
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Orientacio = 'Sup')
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Posicio = 0.0)
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Longitud = 100)
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Edit = False)
        build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(acabatEditar = False)

    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(BarraAdj = build_ele.BarresAdjListEN.value[posBarraHor].BarraAdj)
    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Orientacio = build_ele.BarresAdjListEN.value[posBarraHor].Orientacio)
    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Posicio = build_ele.BarresAdjListEN.value[posBarraHor].Posicio)
    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Longitud = build_ele.BarresAdjListEN.value[posBarraHor].Longitud)
    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(Edit = build_ele.BarresAdjListEN.value[posBarraHor].Edit)
    build_ele.BarresAdjListToShowEN.value[0] = build_ele.BarresAdjListToShowEN.value[0]._replace(acabatEditar = build_ele.BarresAdjListEN.value[posBarraHor].acabatEditar)


    build_ele.BarraAmpleVert.value = build_ele.dadesAdj.value[posBarraHor].Ample
    build_ele.BarraAlturaVert.value = build_ele.dadesAdj.value[posBarraHor].Altura
    build_ele.BarraGruixVert.value = build_ele.dadesAdj.value[posBarraHor].Gruix


    build_ele.desplXVert.value = build_ele.dadesAdj.value[posBarraHor].desplX
    build_ele.desplYVert.value = build_ele.dadesAdj.value[posBarraHor].desplY

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesAdj.value[posBarraHor].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesAdj.value[posBarraHor].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesAdj.value[posBarraHor].BarraLayer

    build_ele.Ample_forat_femellaVert.value = build_ele.dadesAdj.value[posBarraHor].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesAdj.value[posBarraHor].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesAdj.value[posBarraHor].Separacio_forat_femella

    build_ele.ColisVertListToShow.value[0] = build_ele.ColisAdj.value[posBarraHor * 3 + 0 ]
    build_ele.ColisVertListToShow.value[1] = build_ele.ColisAdj.value[posBarraHor * 3 + 1 ]
    build_ele.ColisVertListToShow.value[2] = build_ele.ColisAdj.value[posBarraHor * 3 + 2 ]

    build_ele.PotesVertListToShow.value[0] = build_ele.PotesAdj.value[posBarraHor * 3 + 0 ]
    build_ele.PotesVertListToShow.value[1] = build_ele.PotesAdj.value[posBarraHor * 3 + 1 ]
    build_ele.PotesVertListToShow.value[2] = build_ele.PotesAdj.value[posBarraHor * 3 + 2 ]

    build_ele.ForatsVertListToShowEN.value[0] = build_ele.ForatsAdj.value[posBarraHor * 3 + 0 ]
    build_ele.ForatsVertListToShowEN.value[1] = build_ele.ForatsAdj.value[posBarraHor * 3 + 1 ]
    build_ele.ForatsVertListToShowEN.value[2] = build_ele.ForatsAdj.value[posBarraHor * 3 + 2 ]

    build_ele.FemellesVertListToShow.value[0] = build_ele.FemellesAdj.value[posBarraHor * 3 + 0 ]
    build_ele.FemellesVertListToShow.value[1] = build_ele.FemellesAdj.value[posBarraHor * 3 + 1 ]
    build_ele.FemellesVertListToShow.value[2] = build_ele.FemellesAdj.value[posBarraHor * 3 + 2 ]

    build_ele.posicio_centre_massesVert.value =  build_ele.dadesAdj.value[posBarraHor].posicio_centre_masses
    build_ele.IsFirstCancamVert.value=  build_ele.dadesAdj.value[posBarraHor].IsFirstCancam
    build_ele.Dis1cancamVert.value = build_ele.dadesAdj.value[posBarraHor].Dis1cancam
    build_ele.IsSecondCancamVert.value = build_ele.dadesAdj.value[posBarraHor].IsSecondCancam
    build_ele.Dis2cancamVert.value = build_ele.dadesAdj.value[posBarraHor].Dis2cancam

    build_ele.EncaixVertListToShow.value[0] = build_ele.EncaixAdj.value[posBarraHor * 3 + 0 ]
    build_ele.EncaixVertListToShow.value[1] = build_ele.EncaixAdj.value[posBarraHor * 3 + 1 ]
    build_ele.EncaixVertListToShow.value[2] = build_ele.EncaixAdj.value[posBarraHor * 3 + 2 ]

    build_ele.PestanyaSuperiorVert.value = build_ele.dadesAdj.value[posBarraHor].pestanyaSup
    build_ele.PestanyaInferiorVert.value = build_ele.dadesAdj.value[posBarraHor].pestanyaInf

def guardar_valors_adjacents(build_ele,posBarraHor):

    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(BarraAdj = build_ele.BarresAdjListToShowEN.value[0].BarraAdj)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Orientacio = build_ele.BarresAdjListToShowEN.value[0].Orientacio)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Posicio = build_ele.BarresAdjListToShowEN.value[0].Posicio)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Longitud = build_ele.BarresAdjListToShowEN.value[0].Longitud)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Profunditat = build_ele.BarresAdjListToShowEN.value[0].Profunditat)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(Edit = build_ele.BarresAdjListToShowEN.value[0].Edit)
    build_ele.BarresAdjListEN.value[posBarraHor] = build_ele.BarresAdjListEN.value[posBarraHor]._replace(acabatEditar = build_ele.BarresAdjListToShowEN.value[0].acabatEditar)

    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Ample = build_ele.BarraAmpleVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Altura = build_ele.BarraAlturaVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Gruix = build_ele.BarraGruixVert.value)


    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(desplY = build_ele.desplYVert.value)

    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)


    build_ele.ColisAdj.value[posBarraHor * 3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisAdj.value[posBarraHor * 3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisAdj.value[posBarraHor * 3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesAdj.value[posBarraHor * 3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesAdj.value[posBarraHor * 3 + 1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesAdj.value[posBarraHor * 3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.FemellesAdj.value[posBarraHor * 3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesAdj.value[posBarraHor * 3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesAdj.value[posBarraHor * 3 + 2] = build_ele.FemellesVertListToShow.value[2]

    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)

    build_ele.EncaixAdj.value[posBarraHor * 3 + 0] = build_ele.EncaixVertListToShow.value[0]
    build_ele.EncaixAdj.value[posBarraHor * 3 + 1] = build_ele.EncaixVertListToShow.value[1]
    build_ele.EncaixAdj.value[posBarraHor * 3 + 2] = build_ele.EncaixVertListToShow.value[2]

    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(pestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesAdj.value[posBarraHor] = build_ele.dadesAdj.value[posBarraHor]._replace(pestanyaInf = build_ele.PestanyaInferiorVert.value)

#set valors Vert
def set_valors_Adjacents(build_ele, nBarraAdj):

    while nBarraAdj >= len(build_ele.BarresAdjListEN.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraAdj Orientacio Posicio Longitud Profunditat Edit acabatEditar')
        bob = TDVertCollection( BarraAdj = False,
                                Orientacio = 'Sup',
                                Posicio = 0.0,
                                Longitud = 100.0,
                                Profunditat = 0,
                                Edit = False,
                                acabatEditar = False)
        build_ele.BarresAdjListEN.value.append(bob)

    while nBarraAdj >= len(build_ele.dadesAdj.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'estaEditant acabatEditar Ample Altura Gruix desplX desplY IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam pestanyaSup pestanyaInf')
        bob = TDVertCollection( estaEditant = False,
                                acabatEditar = False,
                                Ample = 30,
                                Altura = 30,
                                Gruix= 15,
                                desplX = 0.0,
                                desplY = 0.0,
                                IsUseGlobalProp = False,
                                FounColor = 1,
                                BarraLayer = 40076,
                                Ample_forat_femella = 15,
                                Altura_forat_femella = 2,#3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = False,
                                pestanyaInf = False)
        build_ele.dadesAdj.value.append(bob)

    while nBarraAdj  * 3 + 3 >= len(build_ele.ColisAdj.value):
        build_ele.ColisAdj.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisAdj.value[len(build_ele.ColisAdj.value)-1] = build_ele.ColisAdj.value[len(build_ele.ColisAdj.value)-1]._replace(Colis = False)
    while nBarraAdj  * 3 + 3 >= len(build_ele.PotesAdj.value):
        build_ele.PotesAdj.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesAdj.value[len(build_ele.PotesAdj.value)-1] = build_ele.PotesAdj.value[len(build_ele.PotesAdj.value)-1]._replace(Pota = False)
    while nBarraAdj  * 3 + 3 >= len(build_ele.ForatsAdj.value):
        build_ele.ForatsAdj.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsAdj.value[len(build_ele.ForatsAdj.value)-1] = build_ele.ForatsAdj.value[len(build_ele.ForatsAdj.value)-1]._replace(Forat = False)
    while nBarraAdj  * 3 + 3 >= len(build_ele.FemellesAdj.value):
        build_ele.FemellesAdj.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesAdj.value[len(build_ele.FemellesAdj.value)-1] = build_ele.FemellesAdj.value[len(build_ele.FemellesAdj.value)-1]._replace(Femella = False)
    while nBarraAdj  * 3 + 3 >= len(build_ele.EncaixAdj.value):
        build_ele.EncaixAdj.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixAdj.value[len(build_ele.EncaixAdj.value)-1] = build_ele.EncaixAdj.value[len(build_ele.EncaixAdj.value)-1]._replace(Encaix = False)


#--------------------Barres Frontals ------------------------------
def mostrar_valors_Frontals(build_ele,posBarraHor,posBarraFrontShow):

    if build_ele.BarresFrontList.value[posBarraHor].Longitud <= 0:
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(BarraFront = False)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Amplitud = 30)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Altura = 40)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Orientacio = 'Esq')
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Posicio = 0.0)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Longitud = 100)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Profunditat = 10)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Edit = False)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Save = False)
        build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(acabatEditar = False)

    '''
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(BarraFront = build_ele.BarresFrontList.value[posBarraHor].BarraFront)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Amplitud = build_ele.BarresFrontList.value[posBarraHor].Amplitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Altura = build_ele.BarresFrontList.value[posBarraHor].Altura)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Orientacio = build_ele.BarresFrontList.value[posBarraHor].Orientacio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Posicio = build_ele.BarresFrontList.value[posBarraHor].Posicio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Longitud = build_ele.BarresFrontList.value[posBarraHor].Longitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Profunditat = build_ele.BarresFrontList.value[posBarraHor].Profunditat)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Edit = build_ele.BarresFrontList.value[posBarraHor].Edit)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Save = build_ele.BarresFrontList.value[posBarraHor].Save)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(acabatEditar = build_ele.BarresFrontList.value[posBarraHor].acabatEditar)
    '''

    build_ele.BarraAmpleVert.value = build_ele.dadesFront.value[posBarraHor].Ample
    build_ele.BarraAlturaVert.value = build_ele.dadesFront.value[posBarraHor].Altura
    build_ele.BarraGruixVert.value = build_ele.dadesFront.value[posBarraHor].Gruix


    build_ele.desplXVert.value = build_ele.dadesFront.value[posBarraHor].desplX
    build_ele.desplYVert.value = build_ele.dadesFront.value[posBarraHor].desplY

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesFront.value[posBarraHor].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesFront.value[posBarraHor].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesFront.value[posBarraHor].BarraLayer

    build_ele.PestanyaSuperiorVert.value = build_ele.dadesFront.value[posBarraHor].pestanyaSup
    build_ele.PestanyaInferiorVert.value = build_ele.dadesFront.value[posBarraHor].pestanyaInf

def guardar_valors_Frontals(build_ele,posBarraHor, posBarraFrontShow):
    '''
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(BarraFront = build_ele.BarresFrontListToShow.value[posBarraFrontShow].BarraFront)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Amplitud = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Amplitud)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Altura = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Altura)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Orientacio = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Orientacio)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Posicio = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Posicio)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Longitud = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Longitud)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Profunditat = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Profunditat)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Edit = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Edit)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(Save = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Save)
    build_ele.BarresFrontList.value[posBarraHor] = build_ele.BarresFrontList.value[posBarraHor]._replace(acabatEditar = build_ele.BarresFrontListToShow.value[posBarraFrontShow].acabatEditar)
    '''

    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(Ample = build_ele.BarraAmpleVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(Altura = build_ele.BarraAlturaVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(Gruix = build_ele.BarraGruixVert.value)


    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(desplY = build_ele.desplYVert.value)

    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)


    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(pestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesFront.value[posBarraHor] = build_ele.dadesFront.value[posBarraHor]._replace(pestanyaInf = build_ele.PestanyaInferiorVert.value)

#--------------------Barres Frontals ------------------------------
def mostrar_valors_FrontalsAux(build_ele,posBarraHor,posBarraFrontShow):

    if build_ele.BarresFrontListAux.value[posBarraHor].Longitud <= 0:
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(BarraFront = False)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Amplitud = 30)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Altura = 40)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Orientacio = 'Esq')
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Posicio = 0.0)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Longitud = 100)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Profunditat = 10)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Edit = False)
        build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(acabatEditar = False)

    '''
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(BarraFront = build_ele.BarresFrontListAux.value[posBarraHor].BarraFront)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Amplitud = build_ele.BarresFrontListAux.value[posBarraHor].Amplitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Altura = build_ele.BarresFrontListAux.value[posBarraHor].Altura)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Orientacio = build_ele.BarresFrontListAux.value[posBarraHor].Orientacio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Posicio = build_ele.BarresFrontListAux.value[posBarraHor].Posicio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Longitud = build_ele.BarresFrontListAux.value[posBarraHor].Longitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Profunditat = build_ele.BarresFrontListAux.value[posBarraHor].Profunditat)
    '''
    #build_ele.BarraAmpleVert.value = build_ele.dadesFrontAux.value[posBarraHor].Ample
    #build_ele.BarraAlturaVert.value = build_ele.dadesFrontAux.value[posBarraHor].Altura
    #build_ele.BarraGruixVert.value = build_ele.dadesFrontAux.value[posBarraHor].Gruix


    build_ele.desplXVert.value = build_ele.dadesFrontAux.value[posBarraHor].desplX
    build_ele.desplYVert.value = build_ele.dadesFrontAux.value[posBarraHor].desplY

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesFrontAux.value[posBarraHor].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesFrontAux.value[posBarraHor].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesFrontAux.value[posBarraHor].BarraLayer

    build_ele.PestanyaSuperiorVert.value = build_ele.dadesFrontAux.value[posBarraHor].pestanyaSup
    build_ele.PestanyaInferiorVert.value = build_ele.dadesFrontAux.value[posBarraHor].pestanyaInf

def guardar_valors_FrontalsAux(build_ele,posBarraHor, posBarraFrontShow):
    '''
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(BarraFront = build_ele.BarresFrontListToShow.value[posBarraFrontShow].BarraFront)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Amplitud = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Amplitud)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Altura = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Altura)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Orientacio = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Orientacio)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Posicio = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Posicio)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Longitud = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Longitud)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Profunditat = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Profunditat)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Edit = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Edit)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(Save = build_ele.BarresFrontListToShow.value[posBarraFrontShow].Save)
    build_ele.BarresFrontListAux.value[posBarraHor] = build_ele.BarresFrontListAux.value[posBarraHor]._replace(acabatEditar = build_ele.BarresFrontListToShow.value[posBarraFrontShow].acabatEditar)
    '''
    #build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(Ample = build_ele.BarraAmpleVert.value)
    #build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(Altura = build_ele.BarraAlturaVert.value)
    #build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(Gruix = build_ele.BarraGruixVert.value)


    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(desplY = build_ele.desplYVert.value)

    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(pestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesFrontAux.value[posBarraHor] = build_ele.dadesFrontAux.value[posBarraHor]._replace(pestanyaInf = build_ele.PestanyaInferiorVert.value)


def set_values_BarresFrontAux(build_ele, i):

    while len(build_ele.BarresFrontListAux.value) <= i:
        for x in range(len(build_ele.BarresFrontListAux.value), i+10):
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar Separator')
            bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False,
                                Separator= '')

            build_ele.BarresFrontListAux.value.append(bob)

    while len(build_ele.dadesFrontAux.value) <= i+1:
        TDVertCollection = collections.namedtuple('StirrupList', 'estaEditant acabatEditar Amplitud Altura Gruix desplX desplY IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam pestanyaSup pestanyaInf')
        bob = TDVertCollection( estaEditant = False,
                                acabatEditar = False,
                                Amplitud = 30,
                                Altura = 40,
                                Gruix= 15,
                                desplX = 0.0,
                                desplY = 0.0,
                                IsUseGlobalProp = False,
                                FounColor = 1,
                                BarraLayer = 40076,
                                Ample_forat_femella = 15 ,
                                Altura_forat_femella = 2,#3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = False,
                                pestanyaInf = False)
        build_ele.dadesFrontAux.value.append(bob)

#set valors Vert
def set_valors_Frontals(build_ele, nBarraFront):

    while nBarraFront >= len(build_ele.BarresFrontList.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
        bob = TDVertCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False)
        build_ele.BarresFrontList.value.append(bob)

    while nBarraFront >= len(build_ele.dadesFront.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'estaEditant acabatEditar Amplitud Altura Gruix desplX desplY IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam pestanyaSup pestanyaInf')
        bob = TDVertCollection( estaEditant = False,
                                acabatEditar = False,
                                Amplitud = 30,
                                Altura = 40,
                                Gruix= 15,
                                desplX = 0.0,
                                desplY = 0.0,
                                IsUseGlobalProp = False,
                                FounColor = 1,
                                BarraLayer = 40076,
                                Ample_forat_femella = 15 ,
                                Altura_forat_femella = 2,#3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = False,
                                pestanyaInf = False)
        build_ele.dadesFront.value.append(bob)

    while nBarraFront  * 3 + 3 >= len(build_ele.ColisFront.value):
        build_ele.ColisFront.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisFront.value[len(build_ele.ColisFront.value)-1] = build_ele.ColisFront.value[len(build_ele.ColisFront.value)-1]._replace(Colis = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.PotesFront.value):
        build_ele.PotesFront.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesFront.value[len(build_ele.PotesFront.value)-1] = build_ele.PotesFront.value[len(build_ele.PotesFront.value)-1]._replace(Pota = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.ForatsFront.value):
        build_ele.ForatsFront.value.append(build_ele.ForatsVertListToShowEN.value[0])
        build_ele.ForatsFront.value[len(build_ele.ForatsFront.value)-1] = build_ele.ForatsFront.value[len(build_ele.ForatsFront.value)-1]._replace(Forat = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.FemellesFront.value):
        build_ele.FemellesFront.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesFront.value[len(build_ele.FemellesFront.value)-1] = build_ele.FemellesFront.value[len(build_ele.FemellesFront.value)-1]._replace(Femella = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.EncaixFront.value):
        build_ele.EncaixFront.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixFront.value[len(build_ele.EncaixFront.value)-1] = build_ele.EncaixFront.value[len(build_ele.EncaixFront.value)-1]._replace(Encaix = False)

"""
def createCancam(build_ele, altura):
    cancamSup1 = CilindreCancam(build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraGruix.value,
                                    build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                    build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                    build_ele.FounColor.value, build_ele.BarraLayer.value)

    if not cancamSup1.is_valid():
        return[]
    cancamSup1_Brep = cancamSup1.create()
    common_props_cancamSup1 = cancamSup1.get_common_props()

    views_cancamSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_cancamSup1, cancamSup1.create())])]

    attr_list_cancamSup = [AllplanBaseElements.AttributeString(2103, "TDCilindreCancam "),
                            AllplanBaseElements.AttributeString(508, "Cancam")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.posicio_centre_massesSUP.value)
    vectorCan.SetValue(13, build_ele.desplYS.value)
    vectorCan.SetValue(14, altura)

    return PythonPart ("PP_TD_CilindreCancam", parameter_list = cancamSup1.get_params_list(),
                                    hash_value = cancamSup1.hash(), python_file = cancamSup1.filename(),
                                    views = views_cancamSup, matrix = vectorCan, attribute_list = attr_list_cancamSup)


def createColis(build_ele, altura, i):

    ColisSup = BoxColis(random.random() * 3600, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraGruix.value,
                                    build_ele.ColisParSUP.value, i,
                                    build_ele.FounColor.value, build_ele.BarraLayer.value)

    if not ColisSup.is_valid():
        return[]
    ColisSup_Brep = ColisSup.create()
    common_props_ColisSup = ColisSup.get_common_props()

    views_ColisSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_ColisSup, ColisSup.create())])]

    if build_ele.ColisParSUP.value[i].orientacio == "Sup":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA SUP "),
                                AllplanBaseElements.AttributeString(508, "COLIS")]
    elif build_ele.ColisParSUP.value[i].orientacio == "Inf":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA INF "),
                                AllplanBaseElements.AttributeString(508, "COLIS")]
    elif build_ele.ColisParSUP.value[i].orientacio == "Esq":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA ESQ "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]
    else:
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA DRE "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.ColisParSUP.value[i].Posicio )
    vectorCan.SetValue(13, build_ele.desplYS.value)
    vectorCan.SetValue(14, altura)

    return PythonPart ("PP_TD_CilindreCancam", parameter_list = ColisSup.get_params_list(),
                                    hash_value = ColisSup.hash(), python_file = ColisSup.filename(),
                                    views = views_ColisSup, matrix = vectorCan, attribute_list = attr_list_ColisSup)

def createColisInf(build_ele, altura, i):

    ColisSup = BoxColis(random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, build_ele.BarraGruix.value,
                                    build_ele.ColisParINF.value, i,
                                    build_ele.FounColor.value, build_ele.BarraLayer.value)

    if not ColisSup.is_valid():
        return[]
    ColisSup_Brep = ColisSup.create()
    common_props_ColisSup = ColisSup.get_common_props()

    views_ColisSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_ColisSup, ColisSup.create())])]

    if build_ele.ColisParINF.value[i].orientacio == "Sup":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA SUP "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]
    elif build_ele.ColisParINF.value[i].orientacio == "Inf":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA INF "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]
    elif build_ele.ColisParINF.value[i].orientacio == "Esq":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA ESQ "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]
    else:
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA DRE "),
                             AllplanBaseElements.AttributeString(508, "COLIS")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.ColisParINF.value[i].Posicio )
    vectorCan.SetValue(13, build_ele.desplYI.value)
    vectorCan.SetValue(14, 0)

    return PythonPart ("PP_TD_CilindreCancam", parameter_list = ColisSup.get_params_list(),
                                    hash_value = ColisSup.hash(), python_file = ColisSup.filename(),
                                    views = views_ColisSup, matrix = vectorCan, attribute_list = attr_list_ColisSup)


def createBoxForat(build_ele, i, forats, nForat):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDVertEN.value[i].BarraAmple, build_ele.dadesTDVertEN.value[i].BarraAltura, build_ele.BarraLlargadaVert.value, build_ele.BarraGruix.value,
                                    False, build_ele.FounColor.value, build_ele.BarraLayer.value, forats, False, nForat)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]


    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),
                             AllplanBaseElements.AttributeString(508, "FORAT")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.listDesplVerticalsEN.value[i].desplXAbs - (build_ele.dadesTDVertEN.value[i].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2) )
    vectorCan.SetValue(13, build_ele.listDesplVerticalsEN.value[i].desplYAbs)
    vectorCan.SetValue(14, 0)#barrainici pos
    nHorInf = 0
    if build_ele.dadesTDVertEN.value[i].BarraInferior != "EN Inferior":
        if len(build_ele.dadesTDVertEN.value[i].BarraInferior) == 7:
            nHorInfCentenes = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-3])
            nHorInfDecenes = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-1])
            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertEN.value[i].BarraInferior) == 6:
            nHorInfDecenes = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-1])
            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertEN.value[i].BarraInferior) == 5:
            nHorInf = int(build_ele.dadesTDVertEN.value[i].BarraInferior[-1])

        if not build_ele.dadesTDVertEN.value[i].EncaixInf:
            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio - build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2
        else:
            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio + build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2 +1 #- build_ele.BarraAlturaInf.value/2# + build_ele.BarraAlturaSup.value/2 + 1.25
        vectorCan.SetValue(14, posHorInf)#barrainici pos


    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, attribute_list = attr_list_nBoxForat)

def createBoxForatVertInt(build_ele, i, forats,nForats):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDVertInter.value[i].BarraAmple, build_ele.dadesTDVertInter.value[i].BarraAltura, build_ele.BarraLlargadaVert.value, build_ele.BarraGruix.value,
                                    False, build_ele.FounColor.value, build_ele.BarraLayer.value, forats, False, nForats)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]


    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),
                             AllplanBaseElements.AttributeString(508, "FORAT")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs - (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) )
    vectorCan.SetValue(13, build_ele.dadesTDVertInter.value[i].desplYAbs)
    vectorCan.SetValue(14, 0)

    if not build_ele.BarresVertList.value[i].EncaixInf:
        vectorCan.SetValue(14, build_ele.BarraAlturaInf.value )

    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, attribute_list = attr_list_nBoxForat)


def createBoxForatHorInt(build_ele, posBarraHor, forats, i, nForats):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDHortInterEN.value[posBarraHor].Ample, build_ele.dadesTDHortInterEN.value[posBarraHor].Altura, build_ele.BarraLlargadaVert.value, build_ele.BarraGruix.value,
                                    False, build_ele.FounColor.value, build_ele.BarraLayer.value, forats, True, nForats)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]


    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),
                             AllplanBaseElements.AttributeString(508, "FORAT")]

    vectorCan = AllplanGeo.Matrix3D()
    #vectorCan.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs + (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) + build_ele.ForatsHorInt.value[posBarraHor].Posicio)
    vectorCan.SetValue(12, build_ele.listDesplVerticalsEN.value[i].desplXAbs + build_ele.dadesTDVertEN.value[i].BarraAmple/2 + build_ele.dadesTDVertEN.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 2 )#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInterEN.value[posBarraHor].desplX)
    #vectorCan.SetValue(13, build_ele.dadesTDVertEN.value[i].desplYAbs)
    vectorCan.SetValue(13, build_ele.dadesTDHortInterEN.value[posBarraHor].desplY)
    #vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio)
    if not build_ele.EncaixHorInf.value:
        vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
        #vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio - build_ele.ForatsHorInt.value[posBarraHor].Posicio)
        vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
    else:
        vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio - build_ele.dadesTDHortInterEN.value[posBarraHor].Altura/2)
        #vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio - build_ele.ForatsHorInt.value[posBarraHor].Posicio)
        vectorCan.SetValue(14, build_ele.BarresHorListEN.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value/2 - build_ele.dadesTDHortInterEN.value[posBarraHor].Altura)



    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, attribute_list = attr_list_nBoxForat)
"""


def set_all_edit_to_false(build_ele):

    for nbarra in range(0,len(build_ele.BarresHorListToShowEN.value)):
        if(build_ele.BarresHorListToShowEN.value[nbarra].Edit):
            build_ele.BarresHorListToShowEN.value[nbarra] = build_ele.BarresHorListToShowEN.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresHorListEN.value)):
        if(build_ele.BarresHorListEN.value[nbarra].Edit):
            build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresVertListToShow.value)):
        if(build_ele.BarresVertListToShow.value[nbarra].Edit):
            build_ele.BarresVertListToShow.value[nbarra] = build_ele.BarresVertListToShow.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresAdjListToShowEN.value)):
        if(build_ele.BarresAdjListToShowEN.value[nbarra].Edit):
            build_ele.BarresAdjListToShowEN.value[nbarra] = build_ele.BarresAdjListToShowEN.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresAdjListEN.value)):
        if(build_ele.BarresAdjListEN.value[nbarra].Edit):
            build_ele.BarresAdjListEN.value[nbarra] = build_ele.BarresAdjListEN.value[nbarra]._replace(Edit = False)

    '''
    for nbarra in range(0,len(build_ele.BarresFrontListToShow.value)):
        if(build_ele.BarresFrontListToShow.value[nbarra].Edit):
            build_ele.BarresFrontListToShow.value[nbarra] = build_ele.BarresFrontListToShow.value[nbarra]._replace(Edit = False)
    '''
    for nbarra in range(0,len(build_ele.BarresFrontList.value)):
        if(build_ele.BarresFrontList.value[nbarra].Edit):
            build_ele.BarresFrontList.value[nbarra] = build_ele.BarresFrontList.value[nbarra]._replace(Edit = False)


    for nbarra in range(0, len(build_ele.BarresHorListEN.value)):
        if nbarra< len(build_ele.BarresHorListEN.value):
            if(build_ele.BarresHorListEN.value[nbarra].Edit) or build_ele.BarresHorListEN.value[nbarra].acabatEditar:
                build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(Edit = False)
                build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(acabatEditar = False)

    for nbarra in range(0,len(build_ele.dadesTDHortInterEN.value)):
        if(build_ele.dadesTDHortInterEN.value[nbarra].estaEditant):
            build_ele.dadesTDHortInterEN.value[nbarra] = build_ele.dadesTDHortInterEN.value[nbarra]._replace(estaEditant = False)
            build_ele.dadesTDHortInterEN.value[nbarra] = build_ele.dadesTDHortInterEN.value[nbarra]._replace(acabatEditar = False)

    for nbarra in range(0, len(build_ele.BarresVertList.value)):
        if nbarra < len(build_ele.BarresVertList.value):
            if(build_ele.BarresVertList.value[nbarra].Edit):
                build_ele.BarresVertList.value[nbarra] = build_ele.BarresVertList.value[nbarra]._replace(Edit = False)
                build_ele.BarresVertList.value[nbarra] = build_ele.BarresVertList.value[nbarra]._replace(EditFront = False)

    for n in range(0,len(build_ele.nListBarresFrontAux.value)):
        inici = build_ele.nListBarresFrontAux.value[n].Posicio
        final = build_ele.nListBarresFrontAux.value[n].Posicio + build_ele.nListBarresFrontAux.value[n].nTotal

        for nbarra in range(inici, final):
            if  nbarra < len(build_ele.dadesFrontAux.value):
                if(build_ele.dadesFrontAux.value[nbarra].estaEditant) :
                    build_ele.dadesFrontAux.value[nbarra] = build_ele.dadesFrontAux.value[nbarra]._replace(estaEditant = False)
                    build_ele.dadesFrontAux.value[nbarra] = build_ele.dadesFrontAux.value[nbarra]._replace(acabatEditar = False)

    for nbarra in range(0,len(build_ele.BarresFrontListAux.value)):
        if(build_ele.BarresFrontListAux.value[nbarra].Edit):
            build_ele.BarresFrontListAux.value[nbarra] = build_ele.BarresFrontListAux.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.dadesAdj.value)):
        if(build_ele.dadesAdj.value[nbarra].estaEditant):
            build_ele.dadesAdj.value[nbarra] = build_ele.dadesAdj.value[nbarra]._replace(estaEditant = False)
            build_ele.dadesAdj.value[nbarra] = build_ele.dadesAdj.value[nbarra]._replace(acabatEditar = False)

    for n in range(0,len(build_ele.nListBarresFront.value)):
        inici = build_ele.nListBarresFront.value[n].Posicio
        final = build_ele.nListBarresFront.value[n].Posicio + build_ele.nListBarresFront.value[n].nTotal

        for nbarra in range(inici, final):
            if nbarra < len(build_ele.dadesFront.value):
                if(build_ele.dadesFront.value[nbarra].estaEditant):
                    build_ele.dadesFront.value[nbarra] = build_ele.dadesFront.value[nbarra]._replace(estaEditant = False)
                    build_ele.dadesFront.value[nbarra] = build_ele.dadesFront.value[nbarra]._replace(acabatEditar = False)



def check_all_edit_true(build_ele):

    isTrue = False
    for nbarra in range(0,len(build_ele.BarresHorListToShowEN.value)):
        if(build_ele.BarresHorListToShowEN.value[nbarra].Edit):
            isTrue = True
            build_ele.BarresHorListToShowEN.value[nbarra] = build_ele.BarresHorListToShowEN.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresHorListEN.value)):
        if(build_ele.BarresHorListEN.value[nbarra].Edit):
            isTrue = True
            build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(Edit = False)


    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresVertListToShow.value)):
            if(build_ele.BarresVertListToShow.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresVertListToShow.value[nbarra] = build_ele.BarresVertListToShow.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresAdjListToShowEN.value)):
            if(build_ele.BarresAdjListToShowEN.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresAdjListToShowEN.value[nbarra] = build_ele.BarresAdjListToShowEN.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresAdjListEN.value)):
            if(build_ele.BarresAdjListEN.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresAdjListEN.value[nbarra] = build_ele.BarresAdjListEN.value[nbarra]._replace(Edit = False)

    '''
    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresFrontListToShow.value)):
            if(build_ele.BarresFrontListToShow.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresFrontListToShow.value[nbarra] = build_ele.BarresFrontListToShow.value[nbarra]._replace(Edit = False)
    '''
    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresFrontList.value)):
            if(build_ele.BarresFrontList.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresFrontList.value[nbarra] = build_ele.BarresFrontList.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for n in range(0,len(build_ele.nListBarresHor.value)):
            inici = build_ele.nListBarresHor.value[n].Posicio
            final = build_ele.nListBarresHor.value[n].Posicio + build_ele.nListBarresHor.value[n].nTotal

            for nbarra in range(inici, final):
                if nbarra< len(build_ele.BarresHorListEN.value):
                    if(build_ele.BarresHorListEN.value[nbarra].Edit):
                        isTrue = True
                        build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(Edit = False)
                        build_ele.BarresHorListEN.value[nbarra] = build_ele.BarresHorListEN.value[nbarra]._replace(acabatEditar = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.dadesTDHortInterEN.value)):
            if(build_ele.dadesTDHortInterEN.value[nbarra].estaEditant):
                isTrue = True
                build_ele.dadesTDHortInterEN.value[nbarra] = build_ele.dadesTDHortInterEN.value[nbarra]._replace(estaEditant = False)
                build_ele.dadesTDHortInterEN.value[nbarra] = build_ele.dadesTDHortInterEN.value[nbarra]._replace(acabatEditar = False)

    if not isTrue:
        for n in range(0,len(build_ele.nListBarresVert.value)):
            inici = build_ele.nListBarresVert.value[n].Posicio
            final = build_ele.nListBarresVert.value[n].Posicio + build_ele.nListBarresVert.value[n].nTotal

            for nbarra in range(inici, final):
                if nbarra< len(build_ele.BarresVertList.value):
                    if(build_ele.BarresVertList.value[nbarra].Edit):
                        isTrue = True
                        build_ele.BarresVertList.value[nbarra] = build_ele.BarresVertList.value[nbarra]._replace(Edit = False)
                        build_ele.BarresVertList.value[nbarra] = build_ele.BarresVertList.value[nbarra]._replace(EditFront = False)

    if not isTrue:
        for n in range(0,len(build_ele.nListBarresFrontAux.value)):
            inici = build_ele.nListBarresFrontAux.value[n].Posicio
            final = build_ele.nListBarresFrontAux.value[n].Posicio + build_ele.nListBarresFrontAux.value[n].nTotal

            for nbarra in range(inici, final):
                if  nbarra < len(build_ele.dadesFrontAux.value):
                    if(build_ele.dadesFrontAux.value[nbarra].estaEditant) :
                        isTrue = True
                        build_ele.dadesFrontAux.value[nbarra] = build_ele.dadesFrontAux.value[nbarra]._replace(estaEditant = False)
                        build_ele.dadesFrontAux.value[nbarra] = build_ele.dadesFrontAux.value[nbarra]._replace(acabatEditar = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresFrontListAux.value)):
            if(build_ele.BarresFrontListAux.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresFrontListAux.value[nbarra] = build_ele.BarresFrontListAux.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.dadesAdj.value)):
            if(build_ele.dadesAdj.value[nbarra].estaEditant):
                isTrue = True
                build_ele.dadesAdj.value[nbarra] = build_ele.dadesAdj.value[nbarra]._replace(estaEditant = False)
                build_ele.dadesAdj.value[nbarra] = build_ele.dadesAdj.value[nbarra]._replace(acabatEditar = False)

    if not isTrue:
        for n in range(0,len(build_ele.nListBarresFront.value)):
            inici = build_ele.nListBarresFront.value[n].Posicio
            final = build_ele.nListBarresFront.value[n].Posicio + build_ele.nListBarresFront.value[n].nTotal

            for nbarra in range(inici, final):
                if nbarra < len(build_ele.dadesFront.value):
                    if(build_ele.dadesFront.value[nbarra].estaEditant):
                        isTrue = True
                        build_ele.dadesFront.value[nbarra] = build_ele.dadesFront.value[nbarra]._replace(estaEditant = False)
                        build_ele.dadesFront.value[nbarra] = build_ele.dadesFront.value[nbarra]._replace(acabatEditar = False)
    return isTrue


def guardar_valors_inici(build_ele, nVer):
    #Guardar/mostra valors a/de la matriu de valors
    if build_ele.IntegerTDSelectorAnterior.value == -1:
        build_ele.IntegerTDSelectorAnterior.value = nVer

        mostrar_valors_actuals(build_ele, nVer)
        #incicialitzar tot desde 0
        inicialitzar_valors_inici(build_ele, build_ele.IntegerENSelector.value)

        if len(build_ele.dadesTDVertEN.value) >= 2:
            build_ele.dadesTDVertEN.value[1] = build_ele.dadesTDVertEN.value[1]._replace(MostrarTDVertical = False)
    else:
        #if (build_ele.SelectorENVAnt.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPEN.value)):
        if build_ele.IntegerTDSelectorAnterior.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPEN.value):
            if not check_all_edit_true(build_ele):
                guardar_valors_actuals(build_ele, build_ele.IntegerTDSelectorAnterior.value)
            build_ele.IntegerTDSelectorAnterior.value = nVer
            mostrar_valors_actuals(build_ele, nVer)

        else: #build_ele.IntegerTDSelectorAnterior.value == nVer:
            guardar = True
            for i in range(0,len(build_ele.BarresHorListEN.value)):
                BarresHor = build_ele.BarresHorListEN.value[i]
                #if (not BarresHor.Edit and BarresHor.acabatEditar) or (not BarresVert.Edit or BarresVert.acabatEditar):
                if BarresHor.Edit or BarresHor.acabatEditar:
                    guardar = False

            for i in range(0,len(build_ele.BarresVertListToShow.value)):
                BarresVert = build_ele.BarresVertListToShow.value[i]
                #if (not BarresHor.Edit and BarresHor.acabatEditar) or (not BarresVert.Edit or BarresVert.acabatEditar):
                if BarresVert.Edit or BarresVert.acabatEditar:
                    guardar = False

            if guardar:
                guardar_valors_actuals(build_ele, nVer)
                mostrar_valors_actuals(build_ele, nVer)

def crear_barres_inferiors_multiples(build_ele, nBarraInf, mostrarActual, doc,placement_mat):

    group_elems = []

    #if build_ele.nBarresTDHoritzontalInf.value != len(build_ele.listDesplHoritzontalsInfEN.value):
    if nBarraInf >= len(build_ele.listDesplHoritzontalsInfEN.value):
        #add_baraInferior(build_ele, len(build_ele.listDesplHoritzontalsInfEN.value))
        add_baraInferior(build_ele, nBarraInf)
    else:
        while len(build_ele.listDesplHoritzontalsInfEN.value) > build_ele.nBarresTDHoritzontalInf.value:
            build_ele.listDesplHoritzontalsInfEN.value.pop()
    #llargadaInf = build_ele.BarraLlargadaEN.value + build_ele.ExtenderInf.value
    llargadaInf = build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf
    #if build_ele.SepararTDHoritzontalInf.value:
        #build_ele.BarraLlargadaEN.value = build_ele.listDesplHoritzontalsInfEN.value[0].BarraLlargadaInf
        #llargadaInf = build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf
        #build_ele.BarraAmpleInf.value = build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraAmpleInf
        #build_ele.BarraAlturaInf.value = build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraAlturaInf

    #if nBarraInf>= len(build_ele.listDesplHoritzontalsInfEN.value):


    '''
    horitzontalPPInf = PP_EN_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreEN.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value, #ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value + build_ele.FemellesHorIntAuxInf.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParINF.value, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf) #EncaixosPar)
    '''
    vermellInf = build_ele.FounColorInf.value
    if build_ele.VermellInf.value:
        vermellInf = 6

    if build_ele.TubInferior.value == "L":
        horitzontalPPInf = PP_EN_Horitzontal_Inf(random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruix.value, build_ele.InvertirENHoritzontalInf.value, False,#Randomz, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInf, build_ele.BarraLayer.value,
                                retallInici= build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX,
                                Encaixos = build_ele.EncaixosParINF.value) #EncaixosPar)
    else:
        horitzontalPPInf = PP_EN_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreEN.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruix.value,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInf, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaINFerior,
                                [])#build_ele.EncaixosParINF.value) #EncaixosPar)


    if not horitzontalPPInf.is_valid():
        return[]


    #definir atributs de la Barra Horitzontal Inferior
    horitzontal_Brep = horitzontalPPInf.create()
    common_props = AllplanBaseElements.CommonProperties()
    common_props = horitzontalPPInf.get_common_props()

    build_ele.DENInf.value = "L"
    if build_ele.TubInferior.value != "L":
        build_ele.DENInf.value = "T"
    if build_ele.reconeixerDen.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPPInf)
        if (tubEsIgual):
            build_ele.DENInf.value = DEN

    atrENEsp = definirAtributPers(build_ele,nBarraInf,"TubInferior")


    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPPInf.get_codi_cara_d_inv()) )

    common_props.Color = 1
    if build_ele.VermellInf.value:
        common_props.Color = vermellInf#Vermell
    #seccio = ""
    #if build_ele.BarraAmpleInf.value > build_ele.BarraAlturaInf.value:
    #    seccio = str(build_ele.BarraAmpleInf.value) + "x " + str(build_ele.BarraAlturaInf.value) +"x " +str(build_ele.BarraLlargadaEN.value) + "x " + str(build_ele.BarraGruix.value)
    #else:
    #    seccio = str(build_ele.BarraAlturaInf.value) + "x " + str(build_ele.BarraAmpleInf.value) +"x " +str(build_ele.BarraLlargadaEN.value)+ "x " + str(build_ele.BarraGruix.value)
    atr05 = "cara_X"
    if build_ele.InvertirENHoritzontalInf.value:
        atr05 = "cara_Y"
    if not build_ele.TubInferior.value == "L":
        atr05 = "Baix"
    table_attr_list = [ AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),

                        AllplanBaseElements.AttributeString(2108,  cara_a),
                        AllplanBaseElements.AttributeString(2494,  cara_a1),
                        AllplanBaseElements.AttributeString(2495,  cara_a2),
                        AllplanBaseElements.AttributeString(2047,  cara_b),
                        AllplanBaseElements.AttributeString(2496,  cara_b1),
                        AllplanBaseElements.AttributeString(2497,  cara_b2),
                        AllplanBaseElements.AttributeString(2110,  cara_c),
                        AllplanBaseElements.AttributeString(2498,  cara_c1),
                        AllplanBaseElements.AttributeString(2499,  cara_c2),
                        AllplanBaseElements.AttributeString(2120,  cara_d),
                        AllplanBaseElements.AttributeString(2500,  cara_d1),
                        AllplanBaseElements.AttributeString(2501,  cara_d2),

                        AllplanBaseElements.AttributeString(2121,  cara_e),
                        AllplanBaseElements.AttributeString(2502,  cara_e1),
                        AllplanBaseElements.AttributeString(2503,  cara_e2),
                        AllplanBaseElements.AttributeString(2122,  cara_f),
                        AllplanBaseElements.AttributeString(2504,  cara_f1),
                        AllplanBaseElements.AttributeString(2505,  cara_f2),
                        AllplanBaseElements.AttributeString(2128,  cara_g),
                        AllplanBaseElements.AttributeString(2506,  cara_g1),
                        AllplanBaseElements.AttributeString(2507,  cara_g2),
                        AllplanBaseElements.AttributeString(2129,  cara_h),
                        AllplanBaseElements.AttributeString(2508,  cara_h1),
                        AllplanBaseElements.AttributeString(2509,  cara_h2),


                        AllplanBaseElements.AttributeString(1947, atrENEsp),

                        AllplanBaseElements.AttributeString(2430, horitzontalPPInf.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPPInf.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPPInf.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2446, horitzontalPPInf.get_codi_pota_inv()),


                        AllplanBaseElements.AttributeString(2431, horitzontalPPInf.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2445, horitzontalPPInf.get_seccio()),
                        AllplanBaseElements.AttributeString(220, horitzontalPPInf.get_llargada()),
                        AllplanBaseElements.AttributeString(2455, horitzontalPPInf.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPPInf.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, horitzontalPPInf.get_llargada()),
                        AllplanBaseElements.AttributeString(1087, atr05),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value),
                        AllplanBaseElements.AttributeString(508, "L")]


    table_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, horitzontal_Brep)])]




    #-------------------------------
    """
    matrixPosX = []
    matrixPosY = []
    matrixcentrar = []
    matrixOffsetY = []
    matrixOr = []

    matrixMostrar = []
    matrixMostrarInf = []
    matrixMostrarSup = []
    for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
        matrixcentrar.append(build_ele.dadesTDVertEN.value[i].BarraAmple/2)
        matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
        matrixPosY.append(build_ele.listDesplVerticalsEN.value[i].desplY)
        matrixMostrar.append(build_ele.dadesTDVertEN.value[i].MostrarTDVertical)
        matrixMostrarInf.append(((build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].PestanyaInferiorVert and build_ele.dadesTDVertEN.value[i].FemellaInf) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.EncaixHorInf.value and not build_ele.dadesTDVertEN.value[i].EncaixInf) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].FemellaInf))and build_ele.dadesTDVertEN.value[i].BarraInferior == "EN Inferior")
        matrixMostrarSup.append(((build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].PestanyaSuperiorVert and build_ele.dadesTDVertEN.value[i].FemellaSup) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.EncaixHorSup.value and not build_ele.dadesTDVertEN.value[i].EncaixSup) or (build_ele.dadesTDVertEN.value[i].MostrarTDVertical and build_ele.dadesTDVertEN.value[i].FemellaSup))and build_ele.dadesTDVertEN.value[i].BarraSuperior == "EN Superior")
    listAmples = []
    listAmples2 = []
    listAltures = []
    for TDVert in build_ele.dadesTDVertEN.value:
        listAmples.append(TDVert.BarraAmple - TDVert.Gruix*2)
        listAmples2.append(TDVert.BarraAmple)
        listAltures.append(TDVert.BarraAltura)
    #Crear Encaixos i Femelles en les Barres Horitzontals
    offsetXI = build_ele.desplXI.value
    offsetXS = build_ele.desplXS.value
    #if (build_ele.desplYI.value != 0.0 and build_ele.desplYI.value > 0.0) or (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):


    if (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):

        if build_ele.invertirEncaixInf.value:
            horitzontalPPInf.set_false_encaix()
            matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                if build_ele.dadesTDVertEN.value[i].EncaixInf:
                    matrixOr.append("Esq")
                else:
                    matrixOr.append("Inf")
            trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#
        else:
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                matrixOffsetY.append(  build_ele.listDesplVerticalsEN.value[i].desplY + build_ele.dadesTDVertEN.value[i].BarraAltura - build_ele.desplYI.value)
            trans_list = horitzontalPPInf.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXI, 'Sup', build_ele.BarraLlargadaEN.value)
            horitzontalPPInf.set_false_femelles()
    elif (build_ele.EncaixHorInf.value and build_ele.desplYI.value <= 0.0):
        if build_ele.invertirEncaixInf.value:
            horitzontalPPInf.set_false_encaix()
            matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs)
                if build_ele.dadesTDVertEN.value[i].EncaixInf:
                    matrixOr.append("Esq")
                else:
                    matrixOr.append("Sup")
            trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#
        else:
            for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
                matrixOffsetY.append( build_ele.BarraAmpleInf.value - build_ele.listDesplVerticalsEN.value[i].desplY + build_ele.desplYI.value)#build_ele.dadesTDVertEN.value[i].BarraAltura

            trans_list = horitzontalPPInf.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXI, 'Inf', build_ele.BarraLlargadaEN.value )
            horitzontalPPInf.set_false_femelles()
    else:
        horitzontalPPInf.set_false_encaix()

        matrixPosX = []
        for i in range(0,len(build_ele.listDesplVerticalsEN.value)):
            matrixPosX.append(build_ele.listDesplVerticalsEN.value[i].desplXAbs )
            matrixOr.append("Esq")
        trans_list = horitzontalPPInf.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaEN.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#
    """
    #-------------------------------------------------

    vectorH1Mult = AllplanGeo.Matrix3D()
    vectorH1Mult.SetValue(12, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX )#+ build_ele.dadesTDVertEN.value[0].BarraAmple)
    vectorH1Mult.SetValue(13, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplY)
    vectorH1Mult.SetValue(14, 0)

    TranslationFather = vectorH1Mult
    TranslationFather.SetValue(12, placement_mat[12] + vectorH1Mult[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH1Mult[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH1Mult[14])
    vectorH1Mult  = TranslationFather


    if build_ele.SepararTDHoritzontalInf.value:
        #horitzontalPPInf with translate has to be the firsrt element because of group modification
        # Define python part for TDHoritzontal


        group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = horitzontalPPInf.get_params_list(),
                                    hash_value = horitzontalPPInf.hash(), python_file = horitzontalPPInf.filename(),
                                    views = table_views, matrix = vectorH1Mult, common_props = common_props, attribute_list = table_attr_list))


        #--------
        common_propsObject = AllplanBaseElements.CommonProperties()
        common_propsObject.Layer = 40055#KN_XPS_CAVITAT
        common_propsObject.Color = 16 #blanc
        common_propsObjectRecess = AllplanBaseElements.CommonProperties()
        common_propsObjectRecess.Layer = 40054#KN_XPS_RECESS
        common_propsObjectRecess.Color = 16 #blanc

        horitzontalPPOBject = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, llargadaInf, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    [], [], [],#ColisPar, PotaPar, #matrius
                                    0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                    [], #Femelles, #matriu
                                    0, #posicio_centre_masses,
                                    False, 0, #IsFirstCancam, Dis1cancam,
                                    False, 0, #IsSecondCancam, Dis2cancam,
                                    build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                    [])#, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf) #EncaixosPar))
        horitzontalPPOBjectRecess = PP_EN_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, llargadaInf, 0,#DistanciaEntreEN, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    [], [], [],#ColisPar, PotaPar, #matrius
                                    0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                    [], #Femelles, #matriu
                                    0, #posicio_centre_masses,
                                    False, 0, #IsFirstCancam, Dis1cancam,
                                    False, 0, #IsSecondCancam, Dis2cancam,
                                    build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                    [])#, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf) #EncaixosPar))

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                                AllplanBaseElements.AttributeString(507, build_ele.NomTDEN.value)]

        horitzontal_BrepObject = horitzontalPPOBject.create()
        horitzontal_BrepObjectRecess = horitzontalPPOBjectRecess.create()

        vectorH1CA = AllplanGeo.Matrix3D()
        vectorH1CA.SetValue(12, vectorH1Mult[12])
        vectorH1CA.SetValue(13, vectorH1Mult[13])
        vectorH1CA.SetValue(14, vectorH1Mult[14] - 5)

        table_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject)])]
        table_views_objectRecess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObjectRecess)])]
        #-----------


        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
        #                            hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
        #                            views = table_views_object, matrix = vectorH1CA, common_props=common_propsObject, attribute_list = table_attr_listObject))
        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectRecess.get_params_list(),
        #                            hash_value = horitzontalPPOBjectRecess.hash(), python_file = horitzontalPPOBjectRecess.filename(),
        #                            views = table_views_objectRecess, matrix = vectorH1CA, common_props=common_propsObjectRecess, attribute_list = table_attr_listObject))
        '''
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
                                    hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
                                    views = table_views_object, matrix = vectorH1C, attribute_list = table_attr_listObject))
        '''

        """
        for i in range(0, len(build_ele.ColisParINF.value)):
            if build_ele.ColisParINF.value[i].Colis and build_ele.ColisParINF.value[i].MostrarBox and build_ele.ColisParINF.value[i].Posicio < build_ele.BarraLlargadaEN.value:
                boxsColis = createColisInf(build_ele,0, i)
                group_elems.append(boxsColis)

        """


        #if build_ele.SepararTDHoritzontalInf.value:
        if build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].mostrarLiniaA:
            punt_central = build_ele.desplXI.value + build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX + build_ele.BarraAlturaInf.value/2
            pointUbi = AllplanGeo.Point3D(vectorH1Mult[12], build_ele.desplYI.value + build_ele.BarraAmpleInf.value/2 + build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplLinA,  build_ele.BarraAlturaInf.value/2 + placement_mat[14])
            if (len(build_ele.SelectorLiniaInf.value)) <=1:
                build_ele.SelectorLiniaInf.value = "Tipus 1"
            linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
            layer = build_ele.SelectorLayerInfEN.value[len(build_ele.SelectorLayerInfEN.value)-1]
            polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.BarraAmpleInf.value,build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
        if build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].mostrarLiniaB:
            punt_central = build_ele.desplXI.value + build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplX + build_ele.BarraAlturaInf.value/2
            pointUbi = AllplanGeo.Point3D(vectorH1Mult[12], build_ele.desplYI.value + build_ele.BarraAmpleInf.value/2 + build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].desplLinB, build_ele.BarraAlturaInf.value/2 + placement_mat[14])
            linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
            layer = build_ele.SelectorLayerInfEN.value[len(build_ele.SelectorLayerInfEN.value)-1]
            polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.BarraAmpleInf.value,build_ele.listDesplHoritzontalsInfEN.value[nBarraInf].BarraLlargadaInf, True, pointUbi, int(linia), layer, posYdiferent= placement_mat[13])
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])



        return group_elems, horitzontalPPInf, []
    return [], [], []


def add_baraInferior(build_ele, nBarraInf):
    while nBarraInf >= len(build_ele.listDesplHoritzontalsInfEN.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraAmpleInf BarraAlturaInf BarraLlargadaInf desplX desplY mostrarLiniaA desplLinA mostrarLiniaB desplLinB Separator')
        bob = TDVertCollection( BarraAmpleInf = 30,
                               BarraAlturaInf = 30,
                               BarraLlargadaInf = 1300,
                               desplX = 0,
                               desplY = 0,
                               mostrarLiniaA = True,
                               desplLinA = 0,
                               mostrarLiniaB = False,
                               desplLinB = 5,
                               Separator = '')
        build_ele.listDesplHoritzontalsInfEN.value.append(bob)

def crearLlistaVerticals(build_ele):
    for barra in range(0, build_ele.IntegerENSelector.value):
        if barra >= len(build_ele.valueListBarresComboBox.value):
            build_ele.valueListBarresComboBox.value.append("Tub " + str(barra))
        else:
            build_ele.valueListBarresComboBox.value[barra] = "Tub " + str(barra)
    for barra in range(build_ele.IntegerENSelector.value, len(build_ele.valueListBarresComboBox.value)):
        build_ele.valueListBarresComboBox.value.pop()


def crearLlistaReforc(build_ele):
    for barra in range(0, build_ele.NumBarresRef.value):
        if barra >= len(build_ele.valueListReforcComboBoxEN.value):
            build_ele.valueListReforcComboBoxEN.value.append("Varifix" + str(barra))
        else:
            build_ele.valueListReforcComboBoxEN.value[barra] = "Varifix " + str(barra)
    while len(build_ele.valueListReforcComboBoxEN.value) > build_ele.NumBarresRef.value:
        build_ele.valueListReforcComboBoxEN.value.pop()

def crearLlistaHoritzontals(build_ele):

    #build_ele.valueVertListBarresHorSupEN.value = []
    if len(build_ele.valueVertListBarresHorSupEN.value) == 0:
        build_ele.valueVertListBarresHorSupEN.value.append("EN Superior")
    else:
        build_ele.valueVertListBarresHorSupEN.value[0] = "EN Superior"

    if len(build_ele.valueVertListBarresHorInfEN.value) == 0:
        build_ele.valueVertListBarresHorInfEN.value.append("EN Inferior")
    else:
        build_ele.valueVertListBarresHorInfEN.value[0] = "EN Inferior"
    barraVert = 0
    barraVertAux = 0
    Afegits = 1
    for barra in range(0, len(build_ele.BarresHorListEN.value)):

        if Afegits >= len(build_ele.valueVertListBarresHorSupEN.value):
            if build_ele.BarresHorListEN.value[barra].BarraHor:
                #build_ele.valueVertListBarresHorSupEN.value.append("Tub " + str(barraVert) + "." + str(barraVertAux+1))
                #build_ele.valueVertListBarresHorInfEN.value.append("Tub " + str(barraVert) + "." + str(barraVertAux+1))
                build_ele.valueVertListBarresHorSupEN.value.append("Tub " + str(barra))
                build_ele.valueVertListBarresHorInfEN.value.append("Tub " + str(barra))

                Afegits += 1
        else:
            if build_ele.BarresHorListEN.value[barra].BarraHor:
                #build_ele.valueVertListBarresHorSupEN.value[Afegits] = "Tub " + str(barraVert) + "." + str(barraVertAux+1)
                #build_ele.valueVertListBarresHorInfEN.value[Afegits] = "Tub " + str(barraVert) + "." + str(barraVertAux+1)
                build_ele.valueVertListBarresHorSupEN.value[Afegits] = "Tub " + str(barra)
                build_ele.valueVertListBarresHorInfEN.value[Afegits] = "Tub " + str(barra)
                Afegits += 1


        barraVertAux += 1
        if barraVertAux == NombreBarresHorInt:
            barraVert += 1
            barraVertAux = 0

    while Afegits < len(build_ele.valueVertListBarresHorSupEN.value):
        build_ele.valueVertListBarresHorSupEN.value.pop()

    while Afegits < len(build_ele.valueVertListBarresHorInfEN.value):
        build_ele.valueVertListBarresHorInfEN.value.pop()

def crearLlistaFullHoritzontals(build_ele):

    #build_ele.valueVertListBarresHorSupEN.value = []
    if len(build_ele.valueListBarresHorBalcEN.value) == 0:
        build_ele.valueListBarresHorBalcEN.value.append("EN Superior")
    else:
        build_ele.valueListBarresHorBalcEN.value[0] = "EN Superior"

    if len(build_ele.valueListBarresHorBalcEN.value) == 1:
        build_ele.valueListBarresHorBalcEN.value.append("EN Inferior")
    else:
        build_ele.valueListBarresHorBalcEN.value[1] = "EN Inferior"
    barraVert = 0
    barraVertAux = 0
    Afegits = 2
    for barra in range(0, len(build_ele.BarresHorListEN.value)):

        if Afegits >= len(build_ele.valueListBarresHorBalcEN.value):
            build_ele.valueListBarresHorBalcEN.value.append("Tub " + str(barra))

            Afegits += 1
        else:
            build_ele.valueListBarresHorBalcEN.value[Afegits] = "Tub " + str(barra)
            Afegits += 1

        if Afegits-2 >= len(build_ele.valueListBarresHorBalcOnlyNum.value):
            build_ele.valueListBarresHorBalcOnlyNum.value.append("Tub " + str(barra))
        else:
            build_ele.valueListBarresHorBalcOnlyNum.value[Afegits-2] = "Tub " + str(barra)



        barraVertAux += 1
        if barraVertAux == NombreBarresHorInt:
            barraVert += 1
            barraVertAux = 0

    while Afegits < len(build_ele.valueListBarresHorBalcEN.value):
        build_ele.valueListBarresHorBalcEN.value.pop()


def copiar_valors_Vert(build_ele,nVer):

    if len(build_ele.DadesVertCopy.value) == 0:
        CopyDadesCollection = collections.namedtuple('StirrupList', 'nBarraGuardada BarraAmple BarraAltura BarraLlargada desplY esProvisional LlargadaAut TreureEncaixSup TreureEncaixInf FemellaSup FemellaInf invertirEncaixSup invertirEncaixInf Separator')
        bob = CopyDadesCollection(nBarraGuardada = nVer,
                                  BarraAmple = build_ele.dadesTDVertEN.value[nVer].BarraAmple,
                                  BarraAltura = build_ele.dadesTDVertEN.value[nVer].BarraAltura,
                                  BarraLlargada = build_ele.dadesTDVertEN.value[nVer].BarraAlcada,
                                  desplY = build_ele.listDesplVerticalsEN.value[nVer].desplYAbs,
                                  esProvisional= build_ele.dadesTDVertEN.value[nVer].esProvisional,
                                  LlargadaAut= build_ele.dadesTDVertEN.value[nVer].LlargadaAut,
                                  TreureEncaixSup = build_ele.dadesTDVertEN.value[nVer].EncaixSup,
                                  TreureEncaixInf = build_ele.dadesTDVertEN.value[nVer].EncaixInf,
                                  invertirEncaixSup = build_ele.dadesTDVertEN.value[nVer].invertirEncaixSup,
                                  invertirEncaixInf = build_ele.dadesTDVertEN.value[nVer].invertirEncaixInf,
                                  FemellaSup = build_ele.dadesTDVertEN.value[nVer].FemellaSup,
                                  FemellaInf = build_ele.dadesTDVertEN.value[nVer].FemellaInf,
                                  Separator = '')
        build_ele.DadesVertCopy.value.append(bob)

    else:
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(nBarraGuardada = nVer)

        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraAmple = build_ele.dadesTDVertEN.value[nVer].BarraAmple)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraAltura = build_ele.dadesTDVertEN.value[nVer].BarraAltura)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraLlargada = build_ele.dadesTDVertEN.value[nVer].BarraAlcada)

        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(desplY = build_ele.listDesplVerticalsEN.value[nVer].desplYAbs)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(esProvisional = build_ele.dadesTDVertEN.value[nVer].esProvisional)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(LlargadaAut = build_ele.dadesTDVertEN.value[nVer].LlargadaAut)

        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(TreureEncaixSup = build_ele.dadesTDVertEN.value[nVer].EncaixSup)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(TreureEncaixInf = build_ele.dadesTDVertEN.value[nVer].EncaixInf)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(FemellaSup = build_ele.dadesTDVertEN.value[nVer].FemellaSup)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(FemellaInf = build_ele.dadesTDVertEN.value[nVer].FemellaInf)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(invertirEncaixSup = build_ele.dadesTDVertEN.value[nVer].invertirEncaixSup)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(invertirEncaixInf = build_ele.dadesTDVertEN.value[nVer].invertirEncaixInf)



    a = 0
    for nVerA in  range(nVer*10, nVer*10+10 ):
        if a >= len(build_ele.ForatsVertListCopy.value) :
            ForatsCopyDadesCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
            bob = ForatsCopyDadesCollection(Forat = build_ele.ForatsVertListEN.value[nVerA].Forat,
                                            orientacio = build_ele.ForatsVertListEN.value[nVerA].orientacio,
                                            Posicio = build_ele.ForatsVertListEN.value[nVerA].Posicio,
                                            Llargada = build_ele.ForatsVertListEN.value[nVerA].Llargada,
                                            Amplada = build_ele.ForatsVertListEN.value[nVerA].Amplada,
                                            Complet = build_ele.ForatsVertListEN.value[nVerA].Complet,
                                            LlargadaB = build_ele.ForatsVertListEN.value[nVerA].LlargadaB,
                                            AmpladaB = build_ele.ForatsVertListEN.value[nVerA].AmpladaB ,
                                            MostrarBox = False,
                                            Separator = '')
            build_ele.ForatsVertListCopy.value.append(bob)
        else:
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Forat = build_ele.ForatsVertListEN.value[nVerA].Forat)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(orientacio = build_ele.ForatsVertListEN.value[nVerA].orientacio)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Posicio = build_ele.ForatsVertListEN.value[nVerA].Posicio)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Llargada = build_ele.ForatsVertListEN.value[nVerA].Llargada )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Amplada = build_ele.ForatsVertListEN.value[nVerA].Amplada )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Complet = build_ele.ForatsVertListEN.value[nVerA].Complet )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(LlargadaB = build_ele.ForatsVertListEN.value[nVerA].LlargadaB )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(AmpladaB = build_ele.ForatsVertListEN.value[nVerA].AmpladaB )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(MostrarBox = False)
        if a >= len(build_ele.BarresFrontListCopy.value) :
            ForatsCopyDadesCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar Separator')
            bob = ForatsCopyDadesCollection(BarraFront = build_ele.BarresFrontList.value[nVerA].BarraFront,
                                            Amplitud = build_ele.BarresFrontList.value[nVerA].Amplitud,
                                            Altura = build_ele.BarresFrontList.value[nVerA].Altura,
                                            Orientacio = build_ele.BarresFrontList.value[nVerA].Orientacio,
                                            Posicio = build_ele.BarresFrontList.value[nVerA].Posicio,
                                            Longitud = build_ele.BarresFrontList.value[nVerA].Longitud,
                                            Profunditat = build_ele.BarresFrontList.value[nVerA].Profunditat,
                                            Edit =False,
                                            Save = False,
                                            acabatEditar = False,
                                            Separator = '')
            build_ele.BarresFrontListCopy.value.append(bob)
        else:

            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(BarraFront = build_ele.BarresFrontList.value[nVerA].BarraFront)
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Amplitud = build_ele.BarresFrontList.value[nVerA].Amplitud)
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Altura = build_ele.BarresFrontList.value[nVerA].Altura)
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Orientacio = build_ele.BarresFrontList.value[nVerA].Orientacio )
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Posicio = build_ele.BarresFrontList.value[nVerA].Posicio )
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Longitud = build_ele.BarresFrontList.value[nVerA].Longitud )
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Profunditat = build_ele.BarresFrontList.value[nVerA].Profunditat )
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Edit = False)
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(Save = False)
            build_ele.BarresFrontListCopy.value[a] = build_ele.BarresFrontListCopy.value[a]._replace(acabatEditar = False)
        a += 1
    build_ele.teValorsCopiats.value = True

def pegar_valors_Vert(build_ele,nVer):
    allPegat = False

    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(BarraAmple = build_ele.DadesVertCopy.value[0].BarraAmple)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(BarraAltura = build_ele.DadesVertCopy.value[0].BarraAltura)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(BarraAlcada = build_ele.DadesVertCopy.value[0].BarraLlargada)

    build_ele.listDesplVerticalsEN.value[nVer] = build_ele.listDesplVerticalsEN.value[nVer]._replace(desplYAbs = build_ele.DadesVertCopy.value[0].desplY)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(esProvisional = build_ele.DadesVertCopy.value[0].esProvisional)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(LlargadaAut = build_ele.DadesVertCopy.value[0].LlargadaAut)

    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(EncaixSup = build_ele.DadesVertCopy.value[0].TreureEncaixSup)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(EncaixInf = build_ele.DadesVertCopy.value[0].TreureEncaixInf)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(invertirEncaixSup = build_ele.DadesVertCopy.value[0].invertirEncaixSup)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(invertirEncaixInf = build_ele.DadesVertCopy.value[0].invertirEncaixInf)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(FemellaSup = build_ele.DadesVertCopy.value[0].FemellaSup)
    build_ele.dadesTDVertEN.value[nVer] = build_ele.dadesTDVertEN.value[nVer]._replace(FemellaInf = build_ele.DadesVertCopy.value[0].FemellaInf)



    a = 0
    for nVerA in  range(nVer*10, nVer*10+10 ):
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(Forat = build_ele.ForatsVertListCopy.value[a].Forat)
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(orientacio = build_ele.ForatsVertListCopy.value[a].orientacio)
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(Posicio = build_ele.ForatsVertListCopy.value[a].Posicio)
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(Llargada =build_ele.ForatsVertListCopy.value[a].Llargada )
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(Amplada =build_ele.ForatsVertListCopy.value[a].Amplada )
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(Complet =build_ele.ForatsVertListCopy.value[a].Complet )
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(LlargadaB =build_ele.ForatsVertListCopy.value[a].LlargadaB )
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(AmpladaB =build_ele.ForatsVertListCopy.value[a].AmpladaB )
        build_ele.ForatsVertListEN.value[nVerA] = build_ele.ForatsVertListEN.value[nVerA]._replace(MostrarBox = False)

        #inici = build_ele.nListBarresFront.value[nVer].Posicio
        #final = build_ele.nListBarresFront.value[nVer].nTotal
        #for nVerA in  range(inici, inici+final):
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(BarraFront = build_ele.BarresFrontListCopy.value[a].BarraFront)
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Amplitud = build_ele.BarresFrontListCopy.value[a].Amplitud)
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Altura = build_ele.BarresFrontListCopy.value[a].Altura)
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Orientacio = build_ele.BarresFrontListCopy.value[a].Orientacio )
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Posicio = build_ele.BarresFrontListCopy.value[a].Posicio )
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Longitud = build_ele.BarresFrontListCopy.value[a].Longitud )
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Profunditat = build_ele.BarresFrontListCopy.value[a].Profunditat )
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Edit = False)
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(Save = False)
        build_ele.BarresFrontList.value[nVerA] = build_ele.BarresFrontList.value[nVerA]._replace(acabatEditar = False)
        a += 1
    allPegat = True
    return allPegat

"""
def crear_LProvisionals(build_ele,j, vectorH1):
    Lprovisionals = LProvisional(random.random() * 3600, build_ele.dadesTDVertEN.value[j].BarraAmple + 2, build_ele.dadesTDVertEN.value[j].BarraAltura, build_ele.dadesTDVertEN.value[j].BarraAlcada - 76, build_ele.dadesTDVertEN.value[j].Gruix,
                                False, 7, build_ele.BarraLayerVert.value) #matriu

    if not Lprovisionals.is_valid():
        return[]


    Lprovisionals_BrepObject = Lprovisionals.create()
    common_props_Lprovisionals = Lprovisionals.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "L "),
                             AllplanBaseElements.AttributeString(508, "L Provisional")]

    vectorH1A = AllplanGeo.Matrix3D()
    vectorH1A.SetValue(12, vectorH1[12] - 76 )
    vectorH1A.SetValue(13, vectorH1[13] + build_ele.dadesTDVertEN.value[j].BarraAltura/2 - 17.5/2)
    vectorH1A.SetValue(14, vectorH1[14] )

    PP_Lprovisional = PythonPart("TD_LProvisional", parameter_list = Lprovisionals.get_params_list(),
                                hash_value = Lprovisionals.hash(), python_file = Lprovisionals.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1A, attribute_list = attr_list_Lprovisionals)

    return PP_Lprovisional
"""

def create_num_on_view(build_ele, j, vectorH1, llargadaAut):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesTDVertEN.value[j].BarraAmple + 2, build_ele.dadesTDVertEN.value[j].BarraAltura, build_ele.dadesTDVertEN.value[j].BarraAlcada - 30, build_ele.dadesTDVertEN.value[j].Gruix,
                                False, 8, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                                AllplanBaseElements.AttributeString(1083, "num ID "),
                                AllplanBaseElements.AttributeString(508, "num")]

    vectorH1B = AllplanGeo.Matrix3D()
    vectorH1B.SetValue(12, vectorH1[12] - build_ele.dadesTDVertEN.value[j].BarraAmple  - (20*build_ele.tamanyNumId.value))
    vectorH1B.SetValue(13, vectorH1[13]  )
    #vectorH1B.SetValue(14, build_ele.dadesTDVertEN.value[j].BarraAlcada + vectorH1[14] )
    vectorH1B.SetValue(14, llargadaAut  + vectorH1[14])
    if j == 0:
        vectorH1B.SetValue(14, build_ele.dadesTDVertEN.value[j].BarraAlcada - 100 )

    test = PythonPart("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props=common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return test

def create_num_on_view_Hor(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesTDHortInterEN.value[j].Ample + 2, build_ele.dadesTDHortInterEN.value[j].Altura, build_ele.dadesTDHortInterEN.value[j].Llargada - 30, build_ele.dadesTDHortInterEN.value[j].Gruix,
                                False, 4, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                                AllplanBaseElements.AttributeString(1083, "num ID "),
                                AllplanBaseElements.AttributeString(508, "num")]

    vectorH1B = AllplanGeo.Matrix3D()
    vectorH1B.SetValue(12, vectorH1[12] - (20*build_ele.tamanyNumId.value) - 100)
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, vectorH1[14] )
    if j == 0:
        vectorH1B.SetValue(14, vectorH1[14] - 100 )

    test = PythonPart("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props=common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return test

def create_num_on_view_ref(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesENReftInter.value[j].Ample + 2, build_ele.dadesENReftInter.value[j].Altura, build_ele.dadesENReftInter.value[j].Llargada - 30, build_ele.dadesTDVertEN.value[j].Gruix,
                                False, 51, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                                AllplanBaseElements.AttributeString(1083, "num ID "),
                                AllplanBaseElements.AttributeString(508, "num")]

    vectorH1B = AllplanGeo.Matrix3D()
    vectorH1B.SetValue(12, vectorH1[12] - build_ele.dadesENReftInter.value[j].Ample )
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, build_ele.BarresRefListEN.value[j].Posicio + build_ele.dadesENReftInter.value[j].Altura + 10 )
    if j == 0:
        vectorH1B.SetValue(14, build_ele.BarresRefListEN.value[j].Posicio - 100 )

    test = PythonPart("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props=common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return test


def create_handles_balconeresFinestres(build_ele ):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargadaEN.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value + build_ele.AmpleBalconeraEN.value, 0, build_ele.PosicioZBalconeraEN.value + build_ele.LlargadaBalconeraEN.value),
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0, build_ele.PosicioZBalconeraEN.value),
                                        [("AmpleBalconeraEN", HandleDirection.x_dir),
                                         ("LlargadaBalconeraEN", HandleDirection.z_dir)],
                                        HandleDirection.xy_dir),
                        HandleProperties("BarraPosicio",
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0, build_ele.PosicioZBalconeraEN.value ),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("PosicioXBalconeraEN", HandleDirection.x_dir),
                                         ("PosicioZBalconeraEN", HandleDirection.z_dir)],
                                        HandleDirection.xy_dir)
                                        #HandleProperties("LlargadaBalconeraEN",
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0, build_ele.LlargadaBalconeraEN.value),
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconeraEN.value, 0, 0),
                                        #[("BarraLlargada", HandleDirection.z_dir)],
                                        #HandleDirection.z_dir)
                      ]

        return handle_list


def buscar_anterior_mes_proper(build_ele, posicioX):

    trobatAnt = False
    posNAntMesPropera = 1
    posicioAntMesPropera = 0.0

    #for nBarra in range(1,len(build_ele.listDesplVerticalsEN.value)):
    for nBarra in range(1,build_ele.IntegerENSelector.value):
        if build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs < posicioX and build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs >= posicioAntMesPropera and build_ele.dadesTDVertEN.value[nBarra].MostrarTDVertical and not build_ele.dadesTDVertEN.value[nBarra].esProvisional and  build_ele.dadesTDVertEN.value[nBarra].BarraSuperior == "EN Superior" and  build_ele.dadesTDVertEN.value[nBarra].BarraInferior == "EN Inferior" :
            posicioAntMesPropera = build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs #+ 80
            trobatAnt = True
            posNAntMesPropera = nBarra


    print("pos Ant mes propera: " + str(posicioAntMesPropera))
    return trobatAnt, posNAntMesPropera

def buscar_seguent_mes_proper(build_ele, posicioX):

    trobatSeg = False
    posNSegMesPropera = 1
    #posicioSegMesPropera = build_ele.BarraLlargadaEN.value + build_ele.DistanciaEntreEN.value
    posicioSegMesPropera = (build_ele.IntegerENSelector.value-1) * build_ele.DistanciaEntreEN.value
    posicioSegMesPropera = build_ele.listDesplVerticalsEN.value[build_ele.IntegerENSelector.value-1].desplXAbs

    #for nBarra in range(1,len(build_ele.listDesplVerticalsEN.value)):
    for nBarra in range(1,build_ele.IntegerENSelector.value-1):
        if build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs > posicioX and build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs <= posicioSegMesPropera and build_ele.dadesTDVertEN.value[nBarra].MostrarTDVertical and not build_ele.dadesTDVertEN.value[nBarra].esProvisional and  build_ele.dadesTDVertEN.value[nBarra].BarraSuperior == "EN Superior" and  build_ele.dadesTDVertEN.value[nBarra].BarraInferior == "EN Inferior" :
            posicioSegMesPropera = build_ele.listDesplVerticalsEN.value[nBarra].desplXAbs
            trobatSeg = True
            posNSegMesPropera = nBarra


    print("pos Seg mes propera: " + str(posicioSegMesPropera))
    return trobatSeg, posNSegMesPropera

def afegir_balconera_finestra(build_ele, nBalcFin):

     while nBalcFin >= len(build_ele.dadesBalcFinesEN.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'Mostrar AmpleBalconeraEN LlargadaBalconeraEN PosicioXBalconeraEN PosicioZBalconeraEN BarraHorSup BarraHorInf BarraVertEsq BarraVertDre')
        bob = TDVertCollection(Mostrar = True,
                               AmpleBalconeraEN = 400,
                               LlargadaBalconeraEN = 400,
                               PosicioXBalconeraEN = 600,
                               PosicioZBalconeraEN = 800,
                               BarraHorSup = "Tub 0",
                               BarraHorInf = "EN Inferior",
                               BarraVertEsq = "Tub 0",
                               BarraVertDre = "Tub 1")
        build_ele.dadesBalcFinesEN.value.append(bob)

def mostrar_BalcFine(build_ele, nBalcFin):
    if len(build_ele.dadesBalcFinesEN.value) <= nBalcFin:
        afegir_balconera_finestra(build_ele, nBalcFin)
    if build_ele.dadesBalcFinesEN.value[nBalcFin].AmpleBalconeraEN == 0:
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(Mostrar = True)
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(AmpleBalconeraEN = 600)
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(LlargadaBalconeraEN = 1000)
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(PosicioXBalconeraEN = 200)
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(PosicioZBalconeraEN = 60)
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraHorSup = "Tub 0")
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraHorInf = "EN Inferior")
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraVertEsq = "Tub 0")
        build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraVertDre = "Tub 1")
    build_ele.MostrarBalconeraEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].Mostrar
    build_ele.AmpleBalconeraEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].AmpleBalconeraEN
    build_ele.LlargadaBalconeraEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].LlargadaBalconeraEN
    build_ele.PosicioXBalconeraEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].PosicioXBalconeraEN
    build_ele.PosicioZBalconeraEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].PosicioZBalconeraEN
    build_ele.SelectorTDHorSupBalcEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].BarraHorSup
    build_ele.SelectorTDHorInfBalcEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].BarraHorInf
    build_ele.SelectorTDHorEsqBalcEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].BarraVertEsq
    build_ele.SelectorTDHorDreBalcEN.value = build_ele.dadesBalcFinesEN.value[nBalcFin].BarraVertDre

def guardar_valors_BalcFine(build_ele, nBalcFin):
    if len(build_ele.dadesBalcFinesEN.value) < nBalcFin:
        afegir_balconera_finestra(build_ele, nBalcFin+1)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(Mostrar = build_ele.MostrarBalconeraEN.value )
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(AmpleBalconeraEN = build_ele.AmpleBalconeraEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(LlargadaBalconeraEN = build_ele.LlargadaBalconeraEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(PosicioXBalconeraEN = build_ele.PosicioXBalconeraEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(PosicioZBalconeraEN = build_ele.PosicioZBalconeraEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraHorSup = build_ele.SelectorTDHorSupBalcEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraHorInf = build_ele.SelectorTDHorInfBalcEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraVertEsq = build_ele.SelectorTDHorEsqBalcEN.value)
    build_ele.dadesBalcFinesEN.value[nBalcFin] = build_ele.dadesBalcFinesEN.value[nBalcFin]._replace(BarraVertDre = build_ele.SelectorTDHorDreBalcEN.value)

def Encaixos_hor_amb_verticals(build_ele):
    listEncaixAdj = []
    for nVert in range(0,build_ele.IntegerENSelector.value):
        if nVert >= len(build_ele.dadesTDVertEN.value):
            set_values(build_ele, nVert)

        prof = build_ele.dadesTDVertEN.value[nVert].BarraAlcada - build_ele.desplZS.value + build_ele.BarraAlturaInf.value #- build_ele.BarraAlturaSup.value/2
        if build_ele.dadesTDVertEN.value[nVert].BarraSuperior == "EN Superior":

            if not build_ele.dadesTDVertEN.value[nVert].LlargadaAut:
                prof = build_ele.dadesTDVertEN.value[nVert].BarraAlcada - build_ele.desplZS.value #+ build_ele.BarraAlturaSup.value/2
                #BarraFront = (build_ele.desplZS.value  - build_ele.BarraAlturaSup.value/2) < build_ele.dadesTDVertEN.value[nVert].BarraAlcada and build_ele.dadesTDVertEN.value[nVert].MostrarTDVertical and  build_ele.dadesTDVertEN.value[nVert].EncaixSup #and coincideix
                BarraFront = (build_ele.desplZS.value  - build_ele.BarraAlturaSup.value/2) <= build_ele.dadesTDVertEN.value[nVert].BarraAlcada and build_ele.dadesTDVertEN.value[nVert].MostrarTDVertical and  build_ele.dadesTDVertEN.value[nVert].EncaixSup #and coincideix
            else:
                prof = -1
                BarraFront = False
                #if nVert == 0 or nVert == build_ele.IntegerENSelector.value-1:
                #    prof = 8
                #    BarraFront = True
            if prof == 0 and build_ele.dadesTDVertEN.value[nVert].EncaixSup:
                BarraFront = True

            if nVert == 0 :
                posicio = build_ele.listDesplVerticalsEN.value[nVert].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple/2
            elif nVert == build_ele.IntegerENSelector.value-1:
                posicio = build_ele.BarraLlargadaEN.value - build_ele.dadesTDVertEN.value[nVert].BarraAmple/2
            else:
                posicio = build_ele.listDesplVerticalsEN.value[nVert].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple/2 + build_ele.dadesTDVertEN.value[nVert].BarraAmple

            barraLlargada = build_ele.BarraLlargadaEN.value
            if build_ele.TubSuperior.value == "TUB Interior":
                barraLlargada -= build_ele.dadesTDVertEN.value[0].BarraAmple
                #posicio -=  build_ele.dadesTDVertEN.value[nVert].BarraAmple
                posicio = build_ele.listDesplVerticalsEN.value[nVert].desplXAbs + (build_ele.dadesTDVertEN.value[nVert].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2 ) + build_ele.dadesTDVertEN.value[nVert].BarraAmple/2
                if nVert == 0:
                    posicio -= build_ele.dadesTDVertEN.value[0].BarraAmple
                if posicio > barraLlargada - build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.dadesTDVertEN.value[build_ele.IntegerENSelector.value-1].BarraAmple:
                    BarraFront = False
            if posicio < 0 :
                BarraFront = False

            ENCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
            bob = ENCollection( Encaix = BarraFront,#BarraFront = BarraFront,
                                EncaixOr = "Dre",
                                Longitud = build_ele.dadesTDVertEN.value[nVert].BarraAmple,
                                Amplitud = build_ele.dadesTDVertEN.value[nVert].BarraAltura + build_ele.listDesplVerticalsEN.value[nVert].desplYAbs,
                                Posicio = posicio,
                                Profunditat = prof +1 ,
                                Pestanya = False,
                                Separator = '')
            if BarraFront:
                listEncaixAdj.append(bob)

        '''
        else:
            #nBarraInf = 0
            nBarraSup = 1
            #posicioInicial = 0
            #posicoFinal = build_ele.desplZS.value
            #if build_ele.dadesTDVertEN.value[nVert].BarraSuperior != "EN Superior":
            if len(build_ele.dadesTDVertEN.value[nVert].BarraSuperior) == 5:
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-1]
                nBarraSup = int(nBarraSup)
            elif len(build_ele.dadesTDVertEN.value[nVert].BarraSuperior) == 6:
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-2]
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-1] + nBarraSup
                nBarraSup = int(nBarraSup)
            elif len(build_ele.dadesTDVertEN.value[nVert].BarraSuperior) == 7:
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-3]
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-2] + nBarraSup
                nBarraSup = build_ele.dadesTDVertEN.value[nVert].BarraSuperior[-1] + nBarraSup
                nBarraSup = int(nBarraSup)
            #posicoFinal = build_ele.BarresHorListEN.value[nBarraSup].Posicio - build_ele.dadesTDHortInterEN.value[nBarraSup].Altura/2
            """
            if build_ele.dadesTDVertEN.value[nVert].BarraInferior != "EN Inferior":
                if len(build_ele.dadesTDVertEN.value[nVert].BarraInferior) == 5:
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-1]
                    nBarraInf = int(nBarraInf)
                elif len(build_ele.dadesTDVertEN.value[nVert].BarraInferior) == 6:
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-2]
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-1] + nBarraInf
                    nBarraInf = int(nBarraInf)
                elif len(build_ele.dadesTDVertEN.value[nVert].BarraInferior) == 7:
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-3]
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-2] + nBarraInf
                    nBarraInf = build_ele.dadesTDVertEN.value[nVert].BarraInferior[-1] + nBarraInf
                    nBarraInf = int(nBarraInf)
                posicioInicial = build_ele.BarresHorListEN.value[nBarraInf].Posicio
            """

            if not build_ele.dadesTDVertEN.value[nVert].LlargadaAut:
                prof = build_ele.dadesTDVertEN.value[nVert].BarraAlcada - build_ele.BarresHorListEN.value[nBarraSup].Posicio + build_ele.dadesTDHortInterEN.value[nBarraSup].Altura/2
                BarraFront = (build_ele.BarresHorListEN.value[nBarraSup].Posicio  - build_ele.dadesTDHortInterEN.value[nBarraSup].Altura/2) < build_ele.dadesTDVertEN.value[nVert].BarraAlcada and build_ele.dadesTDVertEN.value[nVert].MostrarTDVertical and not build_ele.dadesTDVertEN.value[nVert].EncaixSup #and coincideix
                BarraFront = (build_ele.BarresHorListEN.value[nBarraSup].Posicio  - build_ele.dadesTDHortInterEN.value[nBarraSup].Altura/2) <= build_ele.dadesTDVertEN.value[nVert].BarraAlcada and build_ele.dadesTDVertEN.value[nVert].MostrarTDVertical and not build_ele.dadesTDVertEN.value[nVert].EncaixSup #and coincideix
            else:
                prof = -1
                BarraFront = False
            if prof == 0 :
                BarraFront = True
        '''


    return listEncaixAdj


#mostrar valors
def mostrar_valors_Ref(build_ele, nBarraVert):
    '''
    mostrar valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(BarraRef = build_ele.BarresRefListEN.value[nBarraVert].BarraRef)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(Orientacio = build_ele.BarresRefListEN.value[nBarraVert].Orientacio)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(Posicio = build_ele.BarresRefListEN.value[nBarraVert].Posicio)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(BarraIni = build_ele.BarresRefListEN.value[nBarraVert].BarraIni)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(BarraFin = build_ele.BarresRefListEN.value[nBarraVert].BarraFin)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(AutoLongitud = build_ele.BarresRefListEN.value[nBarraVert].AutoLongitud)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(Longitud = build_ele.BarresRefListEN.value[nBarraVert].Longitud)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(Edit = build_ele.BarresRefListEN.value[nBarraVert].Edit)
    build_ele.BarresRefListToShowEN.value[0] = build_ele.BarresRefListToShowEN.value[0]._replace(acabatEditar = build_ele.BarresRefListEN.value[nBarraVert].acabatEditar)


    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(estaEditant = build_ele.BarresRefListToShowEN.value[0].Edit)

    #build_ele.desplXVert.value = build_ele.dadesENReftInter.value[nBarraVert ].desplX
    #build_ele.desplYVert.value = build_ele.dadesENReftInter.value[nBarraVert ].desplY

    build_ele.desplXVertAbsRef.value = build_ele.dadesENReftInter.value[nBarraVert ].desplX
    build_ele.desplYVertAbsRef.value = build_ele.dadesENReftInter.value[nBarraVert ].desplY

    build_ele.mostrarLiniaVertA.value = build_ele.dadesENReftInter.value[nBarraVert ].mostrarLiniaVertA
    build_ele.desplVertLinA.value = build_ele.dadesENReftInter.value[nBarraVert ].desplLinA
    build_ele.mostrarLiniaVertB.value = build_ele.dadesENReftInter.value[nBarraVert ].mostrarLiniaVertB
    build_ele.desplVertLinB.value = build_ele.dadesENReftInter.value[nBarraVert ].desplLinB

    build_ele.BarraAmpleRef.value = build_ele.dadesENReftInter.value[nBarraVert ].Ample
    build_ele.BarraAlturaRef.value = build_ele.dadesENReftInter.value[nBarraVert ].Altura
    #build_ele.BarraLlargadaVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Llargada
    build_ele.BarraGruixRef.value = build_ele.dadesENReftInter.value[nBarraVert ].Gruix

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesENReftInter.value[nBarraVert ].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesENReftInter.value[nBarraVert ].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesENReftInter.value[nBarraVert ].BarraLayer

    '''
    build_ele.ColisVertListToShow.value[0] = build_ele.ColisRefInt.value[nBarraVert *3 + 0]
    build_ele.ColisVertListToShow.value[1] = build_ele.ColisRefInt.value[nBarraVert *3 + 1]
    build_ele.ColisVertListToShow.value[2] = build_ele.ColisRefInt.value[nBarraVert *3 + 2]

    build_ele.PotesVertListToShow.value[0] = build_ele.PotesRefInt.value[nBarraVert *3 + 0]
    build_ele.PotesVertListToShow.value[1] = build_ele.PotesRefInt.value[nBarraVert *3 + 1]
    build_ele.PotesVertListToShow.value[2] = build_ele.PotesRefInt.value[nBarraVert *3 + 2]

    build_ele.ForatsVertListToShowEN.value[0] = build_ele.ForatsRefInt.value[nBarraVert *3 + 0]
    build_ele.ForatsVertListToShowEN.value[1] = build_ele.ForatsRefInt.value[nBarraVert *3 + 1]
    build_ele.ForatsVertListToShowEN.value[2] = build_ele.ForatsRefInt.value[nBarraVert *3 + 2]
    build_ele.ForatsVertListToShowEN.value[3] = build_ele.ForatsRefInt.value[nBarraVert *3 + 3]
    build_ele.ForatsVertListToShowEN.value[4] = build_ele.ForatsRefInt.value[nBarraVert *3 + 4]
    build_ele.ForatsVertListToShowEN.value[5] = build_ele.ForatsRefInt.value[nBarraVert *3 + 5]
    build_ele.ForatsVertListToShowEN.value[6] = build_ele.ForatsRefInt.value[nBarraVert *3 + 6]
    build_ele.ForatsVertListToShowEN.value[7] = build_ele.ForatsRefInt.value[nBarraVert *3 + 7]

    build_ele.FemellesVertListToShow.value[0] = build_ele.FemellesRefInt.value[nBarraVert *3 + 0]
    build_ele.FemellesVertListToShow.value[1] = build_ele.FemellesRefInt.value[nBarraVert *3 + 1]
    build_ele.FemellesVertListToShow.value[2] = build_ele.FemellesRefInt.value[nBarraVert *3 + 2]
    '''

    build_ele.Ample_forat_femellaVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Separacio_forat_femella

    #build_ele.posicio_centre_massesVert.value =  build_ele.dadesENReftInter.value[nBarraVert ].posicio_centre_masses
    #build_ele.IsFirstCancamVert.value=  build_ele.dadesENReftInter.value[nBarraVert ].IsFirstCancam
    #build_ele.Dis1cancamVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Dis1cancam
    #build_ele.IsSecondCancamVert.value = build_ele.dadesENReftInter.value[nBarraVert ].IsSecondCancam
    #build_ele.Dis2cancamVert.value = build_ele.dadesENReftInter.value[nBarraVert ].Dis2cancam
    #build_ele.PestanyaSuperiorVert.value = build_ele.dadesENReftInter.value[nBarraVert ].PestanyaSup
    #build_ele.PestanyaInferiorVert.value = build_ele.dadesENReftInter.value[nBarraVert ].PestanyaInf

    #build_ele.EncaixVertListToShow.value[0] = build_ele.EncaixRefInt.value[nBarraVert *3 + 0]
    #build_ele.EncaixVertListToShow.value[1] = build_ele.EncaixRefInt.value[nBarraVert *3 + 1]
    #build_ele.EncaixVertListToShow.value[2] = build_ele.EncaixRefInt.value[nBarraVert *3 + 2]


#guardar valors
def guardar_valors_Ref(build_ele, nBarraVert):
    '''
    mostrar valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(BarraRef = build_ele.BarresRefListToShowEN.value[0].BarraRef)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(Orientacio = build_ele.BarresRefListToShowEN.value[0].Orientacio)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(Posicio = build_ele.BarresRefListToShowEN.value[0].Posicio)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(BarraIni = build_ele.BarresRefListToShowEN.value[0].BarraIni)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(BarraFin = build_ele.BarresRefListToShowEN.value[0].BarraFin)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(AutoLongitud = build_ele.BarresRefListToShowEN.value[0].AutoLongitud)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(Longitud = build_ele.BarresRefListToShowEN.value[0].Longitud)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(Edit = build_ele.BarresRefListToShowEN.value[0].Edit)
    build_ele.BarresRefListEN.value[nBarraVert] = build_ele.BarresRefListEN.value[nBarraVert]._replace(acabatEditar = build_ele.BarresRefListToShowEN.value[0].acabatEditar)


    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(estaEditant = build_ele.BarresRefListToShowEN.value[0].Edit)

    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplX = build_ele.desplXVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplY = build_ele.desplYVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplX = build_ele.desplXVertAbsRef.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplY = build_ele.desplYVertAbsRef.value)

    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Ample = build_ele.BarraAmpleRef.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Altura = build_ele.BarraAlturaRef.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Llargada = build_ele.BarraLlargadaVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Gruix = build_ele.BarraGruixRef.value)


    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    '''
    build_ele.ColisRefInt.value[nBarraVert *3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisRefInt.value[nBarraVert *3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisRefInt.value[nBarraVert *3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesRefInt.value[nBarraVert *3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesRefInt.value[nBarraVert *3 +  1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesRefInt.value[nBarraVert *3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsRefInt.value[nBarraVert *3 + 0] = build_ele.ForatsVertListToShowEN.value[0]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 1] = build_ele.ForatsVertListToShowEN.value[1]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 2] = build_ele.ForatsVertListToShowEN.value[2]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 3] = build_ele.ForatsVertListToShowEN.value[3]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 4] = build_ele.ForatsVertListToShowEN.value[4]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 5] = build_ele.ForatsVertListToShowEN.value[5]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 6] = build_ele.ForatsVertListToShowEN.value[6]
    build_ele.ForatsRefInt.value[nBarraVert *3 + 7] = build_ele.ForatsVertListToShowEN.value[7]

    build_ele.FemellesRefInt.value[nBarraVert *3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesRefInt.value[nBarraVert *3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesRefInt.value[nBarraVert *3 + 2] = build_ele.FemellesVertListToShow.value[2]


    build_ele.FemellesRefInt.value[nBarraVert *3 + 0] = build_ele.FemellesRefInt.value[nBarraVert *3 + 0]._replace(Separacio_forat_femella = build_ele.dadesENReftInter.value[nBarraVert ].Separacio_forat_femella)
    build_ele.FemellesRefInt.value[nBarraVert *3 + 1] = build_ele.FemellesRefInt.value[nBarraVert *3 + 1]._replace(Separacio_forat_femella = build_ele.dadesENReftInter.value[nBarraVert ].Separacio_forat_femella)
    build_ele.FemellesRefInt.value[nBarraVert *3 + 2] = build_ele.FemellesRefInt.value[nBarraVert *3 + 2]._replace(Separacio_forat_femella = build_ele.dadesENReftInter.value[nBarraVert ].Separacio_forat_femella)

    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)

    '''

    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(PestanyaSup = build_ele.PestanyaSuperiorVert.value)
    #build_ele.dadesENReftInter.value[nBarraVert ] = build_ele.dadesENReftInter.value[nBarraVert ]._replace(PestanyaInf = build_ele.PestanyaInferiorVert.value)

    #build_ele.EncaixRefInt.value[nBarraVert *3 + 0] = build_ele.EncaixVertListToShow.value[0]
    #build_ele.EncaixRefInt.value[nBarraVert *3 + 1] = build_ele.EncaixVertListToShow.value[1]
    #build_ele.EncaixRefInt.value[nBarraVert *3 + 2] = build_ele.EncaixVertListToShow.value[2]


def definirAtributPers(build_ele,n,tipusTub):
    nomAtr = ""
    #Si tubSuperior es EXD
    if tipusTub == "TubSuperior":
        if not build_ele.AtrPersAutomaticSup.value:
            nomAtr = build_ele.AtributPersonTubSup.value
        else:
            if build_ele.TubSuperior.value == "EXD":
                nomAtr = "EXD" #1
            elif build_ele.TubSuperior.value == "L":
                nomAtr = "L DALT"#4
            else:
                nomAtr = "TUB DALT"#7

    #Si tub Inferior
    if tipusTub == "TubInferior":
        if not build_ele.AtrPersAutomaticInf.value:
            nomAtr = build_ele.AtributPersonTubSup.value
        else:
            if build_ele.TubInferior.value == "L":
                if build_ele.SepararTDHoritzontalInf.value:
                    #if hi ha Vertical a la posicio
                    inferiorSota1Verical = False
                    for i in range(0, len(build_ele.dadesTDVertEN.value) ):
                        if i == 0:
                            if build_ele.listDesplHoritzontalsInfEN.value[n].BarraLlargadaInf == build_ele.dadesTDVertEN.value[i].BarraAmple and 0 == build_ele.listDesplHoritzontalsInfEN.value[n].desplX:
                                inferiorSota1Verical = True
                        elif i == build_ele.IntegerENSelector.value -1:
                            if build_ele.listDesplHoritzontalsInfEN.value[n].BarraLlargadaInf == build_ele.dadesTDVertEN.value[i].BarraAmple and (build_ele.listDesplVerticalsEN.value[i].desplXAbs ) == build_ele.listDesplHoritzontalsInfEN.value[n].desplX - build_ele.dadesTDVertEN.value[0].BarraAmple:
                                inferiorSota1Verical = True
                        else:
                            if build_ele.listDesplHoritzontalsInfEN.value[n].BarraLlargadaInf == build_ele.dadesTDVertEN.value[i].BarraAmple and (build_ele.listDesplVerticalsEN.value[i].desplXAbs ) == build_ele.listDesplHoritzontalsInfEN.value[n].desplX - build_ele.dadesTDVertEN.value[0].BarraAmple:
                                inferiorSota1Verical = True
                    if inferiorSota1Verical:
                        nomAtr = "LB CURTA"#3
                    else:
                        nomAtr = "LB LLARGA"#8
                else:
                    nomAtr = "LB COMPLETA"#2
            else:
                nomAtr = "TUB BAIX"#5

    #Si es un tub Horitzontal
    if tipusTub == "TubHoritzontal":
        if not build_ele.dadesTDHortInterEN.value[n].AtrPersAutomatic:
            nomAtr = build_ele.dadesTDHortInterEN.value[n].AtributPersonTub
        else:
            if build_ele.dadesTDHortInterEN.value[n].Gruix >= build_ele.dadesTDHortInterEN.value[n].Ample/2 or build_ele.dadesTDHortInterEN.value[n].Gruix >= build_ele.dadesTDHortInterEN.value[n].Altura/2:#Xapa
                nomAtr = "XAPA FRONTAL"#11
            else :#build_ele.dadesTDHortInterEN.value[n].Gruix >= build_ele.dadesTDHortInterEN.value[n].Ample/2 or build_ele.dadesTDHortInterEN.value[n].Gruix >= build_ele.dadesTDHortInterEN.value[n].Altura/2:#Tub
                if build_ele.dadesTDHortInterEN.value[n].desplX != 0:
                    #comprovar llargada automatica? o desplX?
                    nomAtr = "TUB FRONTAL"#13
                else:
                    if not build_ele.BarresHorListEN.value[n].AutoLongitud and build_ele.dadesTDHortInterEN.value[n].desplX == 0 :
                        mateixFinal = False
                        for i in range(0, len(build_ele.dadesTDVertEN.value) ):
                            NBarraInici = 0
                            if len(build_ele.BarresHorListEN.value[n].BarraInici) == 5:
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-1])
                            elif len(build_ele.BarresHorListEN.value[n].BarraInici) == 6:
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-2])
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-1] + NBarraInici)
                            else:
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-3])
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-2] + NBarraInici)
                                NBarraInici = int(build_ele.BarresHorListEN.value[n].BarraInici[-1] + NBarraInici)

                            posfinalHor = build_ele.BarresHorListEN.value[n].Longitud + (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple)
                            if NBarraInici == 0:
                                posfinalHor = build_ele.BarresHorListEN.value[n].Longitud + (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple)
                            else:
                                posfinalHor = build_ele.dadesTDVertEN.value[0].BarraAmple + build_ele.BarresHorListEN.value[n].Longitud + (build_ele.listDesplVerticalsEN.value[NBarraInici].desplXAbs + build_ele.dadesTDVertEN.value[NBarraInici].BarraAmple)

                            if NBarraInici == 0:
                                if build_ele.dadesTDVertEN.value[0].BarraAmple + build_ele.listDesplVerticalsEN.value[i].desplXAbs + build_ele.dadesTDVertEN.value[i].BarraAmple == posfinalHor:
                                    mateixFinal = True
                            else:
                                if build_ele.dadesTDVertEN.value[0].BarraAmple + build_ele.listDesplVerticalsEN.value[i].desplXAbs + build_ele.dadesTDVertEN.value[i].BarraAmple == posfinalHor:
                                    mateixFinal = True

                        if mateixFinal:
                            nomAtr = "TUB FRONTAL MIXTE"
                    #for i in range(0, len(build_ele.dadesTDVertEN.value) ):
                    #if not build_ele.BarresHorListEN.value[n].AutoLongitud and build_ele.BarresHorListEN.value[n].Longitud

                        #nomAtr = "Tub Frontal Mixte"
                    else:
                        InferiorSota1Verical = False
                        SuperiorSota1Verical = False
                        for i in range(0, len(build_ele.dadesTDVertEN.value) ):
                            if build_ele.dadesTDVertEN.value[i].BarraInferior == "Tub " + str(n):
                                InferiorSota1Verical = True
                            if build_ele.dadesTDVertEN.value[i].BarraSuperior == "Tub " + str(n):
                                SuperiorSota1Verical = True
                        if InferiorSota1Verical:
                            nomAtr = "TUB BAIX"#5
                        elif SuperiorSota1Verical:
                            nomAtr = "TUB DALT"#4
                        else:
                            nomAtr = "TUB HORITZONTAL"#12
            #else:
                #nomAtr = "Tub Horitzontal"#
    if tipusTub == "TubVertical":
        nomAtr = "TUB VERTICAL"
    return nomAtr

def dividirAtribut(atributSencer):
    cara_ = atributSencer
    cara_1 = "#"
    cara_2 = "#"
    if len(cara_) > 200:
        cara_1 = cara_[200:]
        if len(cara_1) > 200:
            cara_2 = cara_1[200:]
            if len(cara_2) > 200:
                ctypes.windll.user32.MessageBoxW(0, "Hi ha un atribut mes llard de 600 caracters", 0)
            cara_1 = cara_1[0:200]
        cara_ = cara_[0:200]
    return cara_, cara_1, cara_2

def getOrientacioInv(Orientacio):
    if Orientacio == "Esq":
        return "Dre"
    elif Orientacio == "Dre":
        return "Esq"
    elif Orientacio == "Sup":
        return "Inf"
    elif Orientacio == "Inf":
        return "Sup"
    else:
        return ""

def getFemelles(build_ele, AmpleSup):
    femelles = []
    for nBarraVertical in range(0, build_ele.IntegerENSelector.value):
        if build_ele.dadesTDVertEN.value[nBarraVertical].BarraSuperior == "EN Superior" :#Numeracio Malament #+ str(j*(posBarraHor - inici)):

            if build_ele.TubSuperior.value == "TUB":
                if nBarraVertical == 0:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs
                else:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs + build_ele.dadesTDVertEN.value[0].BarraAmple  #+ build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 #- build_ele.dadesTDVertEN.value[0].BarraAmple/2 ) #+ build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2
            elif build_ele.TubSuperior.value == "L" or build_ele.TubSuperior.value == "TUB Interior + L":
                if nBarraVertical == 0:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs - build_ele.desplXS.value - build_ele.dadesTDVertEN.value[0].Gruix - 1 - 2.25
                    #pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs +  build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.desplXS.value - build_ele.dadesTDVertEN.value[0].Gruix - 1 - 2.25 #+ (build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2)
                else:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs +  build_ele.dadesTDVertEN.value[0].BarraAmple - build_ele.desplXS.value - build_ele.dadesTDVertEN.value[0].Gruix - 1 - 2.25 #+ (build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2)

            else:#"TUB Interior"
                if nBarraVertical == 0:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs -build_ele.dadesTDVertEN.value[0].BarraAmple
                else:
                    pos = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplXAbs #+ (build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertEN.value[0].BarraAmple/2 ) #+ build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2


            desplYSup = build_ele.desplYS.value
            desplY = build_ele.listDesplVerticalsEN.value[nBarraVertical].desplYAbs
            puntCentralY = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 + desplY
            puntCentralYSup = AmpleSup/2 + desplYSup
            Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple - 3.0
            if build_ele.TubSuperior.value == "L" or build_ele.TubSuperior.value == "TUB Interior + L":
                Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple -0.50
            Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2
            if Ample_forat_femella >= 15:
                Ample_forat_femella = 15

            posFemellaY = puntCentralY - puntCentralYSup + Ample_forat_femella

            orientSupA =  "Dre"
            if build_ele.dadesTDVertEN.value[nBarraVertical].EncaixSup:
                orientSupA =  "Dre"
                if Ample_forat_femella< 15:
                    posFemellaY = desplY - desplYSup + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2 -  Ample_forat_femella/2
                else:
                    posFemellaY = puntCentralY - puntCentralYSup + Ample_forat_femella/2 -1.5
                if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                    if desplY - desplYSup == 0:
                        posFemellaY = 0.1
                    else:
                        posFemellaY = desplY - desplYSup
                    Separacio_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura - 3
                    Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2
                    if Ample_forat_femella >= 15:
                        Ample_forat_femella = 15
            else:
                posFemellaY = 0.0
                if not build_ele.dadesTDVertEN.value[nBarraVertical].invertirEncaixSup :
                    orientSupA = "Sup"
                else:
                    orientSupA = "Inf"


            profunditatFemella = 3.1
            #ample_forat_femella = 15
            if build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv:
                pos = pos + build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple/2 - Ample_forat_femella/2



            if build_ele.TubSuperior.value == "L" or build_ele.TubSuperior.value == "TUB Interior + L":
                BarrallargadaVert = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAlcada
                #if build_ele.TubSuperior.value == "L":
                if not build_ele.dadesTDVertEN.value[nBarraVertical].LlargadaAut:
                    BarrallargadaVert = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAlcada #- posHorInf + alturaInf
                else:
                    BarrallargadaVert = build_ele.desplZS.value + build_ele.BarraAlturaSup.value
                #else:
                #    if not build_ele.dadesTDVertEN.value[nBarraVertical].LlargadaAut:
                #        BarrallargadaVert = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAlcada #- posHorInf + alturaInf
                #    else:
                #        BarrallargadaVert = build_ele.desplZS.value + build_ele.BarraAlturaSup.value
                #        #BarrallargadaVert = build_ele.desplZSL.value + build_ele.BarraAlturaSup.value
                posHorInf = 0
                j=nBarraVertical
                if build_ele.dadesTDVertEN.value[j].BarraInferior != "EN Inferior":
                    nHorInf = 0
                    if getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3) != "":
                        nHorInf = getNumFromText(build_ele, build_ele.dadesTDVertEN.value[j].BarraInferior, 3)

                    #posHorInf = build_ele.dadesTDHortInterEN.value[nHorInf].Altura
                        if not build_ele.dadesTDVertEN.value[j].EncaixInf:
                            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio - build_ele.BarraAlturaInf.value   #- (build_ele.BarraAlturaInf.value/2 + build_ele.dadesTDHortInterEN.value[nHorInf].Altura/2)
                            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio - build_ele.BarraAlturaInf.value
                        else:
                            posHorInf = build_ele.BarresHorListEN.value[nHorInf].Posicio - build_ele.BarraAlturaInf.value + build_ele.dadesTDHortInterEN.value[nHorInf].Altura


                profunditatFemella = BarrallargadaVert + posHorInf - (build_ele.desplZS.value - build_ele.BarraAlturaSup.value/2)
                if build_ele.TubSuperior.value == "L":
                    profunditatFemella = BarrallargadaVert + posHorInf - build_ele.desplZS.value
                else:
                    profunditatFemella = BarrallargadaVert + posHorInf - build_ele.desplZSL.value
                #if (nBarraVertical == 0 or nBarraVertical == build_ele.IntegerENSelector.value-1) and not build_ele.dadesTDVertEN.value[nBarraVertical].LlargadaAut:
                #    profunditatFemella += 10
                #elif (nBarraVertical == 0 or nBarraVertical == build_ele.IntegerENSelector.value-1) and  build_ele.dadesTDVertEN.value[nBarraVertical].LlargadaAut:
                #    profunditatFemella += 0#no detecta be la llargada!!
                #elif build_ele.dadesTDVertEN.value[nBarraVertical].LlargadaAut:
                if not build_ele.dadesTDVertEN.value[nBarraVertical].EncaixSup:
                    profunditatFemella = 3.1
                #else:
                #    profunditatFemella = 3.1


                #calcular la amplada de la femella segons l'amplada de el tub Vertical - gruix
                #Ample_forat_femella = 15#build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura/2

                if profunditatFemella != 3.1:
                    Ample_forat_femella = build_ele.dadesTDVertEN.value[nBarraVertical].BarraAltura + build_ele.dadesTDVertEN.value[nBarraVertical].Gruix * 2



            TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella profunditatFemella Ample_forat_femella ample_forat_femella tubGirat')
            bob = TDHorCollection(Femella = build_ele.dadesTDVertEN.value[nBarraVertical].MostrarTDVertical and build_ele.dadesTDVertEN.value[nBarraVertical].FemellaSup,
                                FemellaOr = orientSupA,
                                PosFemellaX = pos,
                                PosFemellaY = posFemellaY,
                                Separacio_forat_femella = Separacio_forat_femella,#build_ele.dadesTDVertEN.value[nBarraVertical].BarraAmple - 3.0,
                                profunditatFemella =  profunditatFemella,
                                ample_forat_femella = Ample_forat_femella,
                                Ample_forat_femella = Ample_forat_femella,
                                tubGirat = build_ele.dadesTDVertEN.value[nBarraVertical].PestanyesInv)
            femelles.append(bob)
            if build_ele.TubSuperior.value == "TUB" or build_ele.TubSuperior.value == "TUB Interior":
                bob = bob._replace(FemellaOr = getOrientacioInv(orientSupA))
                femelles.append(bob)

    return femelles


def getNumFromText(build_ele, Text, nMax):
    num = ""
    if len(Text) > nMax:
        if len(Text) == nMax+4:
           Centenes = int(Text[-3])
           Decenes = int(Text[-2])
           Unitats = int(Text[-1])
           num = Centenes*100 + Decenes*10 + Unitats
        elif len(Text) == nMax+3:
            Decenes = int(Text[-2])
            Unitats = int(Text[-1])
            num = Decenes*10 + Unitats
        elif len(Text) == nMax+2:
            num = int(Text[-1])
    return num


class EN_Conjunt_8():
    """
        Definition of class Table
    """

    def __init__(self, build_ele, doc, placement_mat = AllplanGeo.Matrix3D()):

        self.build_ele_TD = build_ele
        self.doc_TD = doc

        self.placement_mat = placement_mat
        #self.build_ele_ctrl_props_list = build_ele_ctrl_props_list


    def get_params_list(self):
        return self.build_ele_TD

    #def __repr__(self):

    #def hash(self):

    def filename(self):
        return "EN_Conjunt_8_clase.py"

    #def create_handles(self):

    def create(self):
        doc = AllplanElementAdapter.DocumentAdapter()
        #create_element_class(self.build_ele, doc=doc)

        result = create_element_class(self.build_ele_TD , self.doc_TD, self.placement_mat)
        model_elem_list = result["elements"]
        handle_list = result["handles"]
        model_elem_list_preview = result["preview_elements"]
        group_elems = result["group_elems"]
        group_elems_preview = result["group_elems_preview"]

        result = {
            "elements"              :  model_elem_list,
            "handles"               :  handle_list,
            "preview_elements"      :  model_elem_list_preview,
            "group_elems"           :  group_elems,
            "group_elems_preview"   :  group_elems_preview}
        return result

        return CreateElementResult( elements=           model_elem_list,
                                    handles=            handle_list,
                                    preview_elements=   model_elem_list_preview)


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
        prop = self.build_ele_TD.get_property(name)

        print("prop: " + str(prop))

        if prop is not None:
            BuildingElementValueUtil.update_value(name, value, self.build_ele_TD, self.build_ele_TD)# ,self.build_ele_ctrl_props_list)


    def on_control_event(self, build_ele, event_id: int):
        on_control_event(build_ele, event_id)