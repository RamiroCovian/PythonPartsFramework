"""
Script for IS_conjunt - Vertical - Group
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

#from pynput.mouse import Listener

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil

from DocumentManager import DocumentManager
from BuildingElementInputService import BuildingElementInputService
from typing import List
from AnyValueByType import AnyValueByType
#from .EN_Horitzontal_Inf_PP import PP_EN_Horitzontal_Inf
#from .EN_Horitzontal_Sup_PP import PP_EN_Horitzontal_Sup
#from .EN_Horitzontal_reforc import PP_EN_Horitzontal_reforc
#from .EN_Vertical_PP import PP_EN_Vertical
from .IS_Horitzontal_PP import PP_IS_Horitzontal
#from .EN_Inclinat_PP import PP_EN_Inclinat
#from .EN_Premarc import PP_EN_Premarc
#from .EN_Horitzontal_Front import EN_Horitzontal_Front
from .EN_liniaInterior import LiniaInterior
from .EN_CreateText import TextSpline


from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from HandleProperties import HandleProperties
from HandleDirection import HandleDirection
from CreateElementResult import CreateElementResult
from Utils import LibraryBitmapPreview


NombreBarresVertInt = 30
NombreBarresHorInt = 3

print('Load IS_Conjunt.py')

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
     return create_element(build_ele, doc)

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
    if event_id == 1000:
        while len(build_ele.dadesTubHor.value) != 0:
            build_ele.dadesTubHor.value.pop()

    doc = DocumentManager.get_instance().document
    create_element(build_ele, doc)

def on_cancel_function(self) -> bool:
    """ Called when ESC key is pressed.

    Returns:
        True when the PythonPart framework should terminate the PythonPart, False otherwise.
    """

    build_ele = self.build_ele

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


def create_element(build_ele, doc): # type: ignore


    #build_ele.zUnique.value = random.random()*3600
    crearLlistaFullHoritzontals(build_ele)

    group_elems = [] #All elements of suite
    group_elems_preview = [] #All elements of suite
    handle_list = []


    nHorSeleccionat = getNumFromText(build_ele, build_ele.SelectorTubHor.value, 3)
    print("nHorSeleccionat: " + str(nHorSeleccionat))

    while build_ele.IntegerISSelectorHor.value +1 > len(build_ele.dadesTubHor.value):
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value+1, nHorSeleccionat)

    for posBarraHor in range(0, build_ele.IntegerISSelectorHor.value):#len(build_ele.dadesTubHor.value)):

        if nHorSeleccionat == posBarraHor:
            if nHorSeleccionat != build_ele.TubAnt.value:
                mostrar_valors_hor(build_ele, nHorSeleccionat)
                print("mostrar "+ str(nHorSeleccionat))
            else:
                #guardar_valors_hor(build_ele, nHorSeleccionat)
                print("guardar ")
                guardar_valors_hor(build_ele, nHorSeleccionat)
            print("tubInferior: " + str( build_ele.dadesTubHor.value[posBarraHor].tubInferior))
            print("build_ele.tubInferior.value: " + str( build_ele.SelectorTubInferior.value))

            print("tubSuperior: " + str( build_ele.dadesTubHor.value[posBarraHor].tubSuperior))
            print("build_ele.tubSuperior.value: " + str( build_ele.SelectorTubSuperior.value))



        if build_ele.dadesTubHor.value[posBarraHor].LlargadaAut :#and build_ele.dadesTubHor.value[posBarraHor].RotarTub:
            llargada = set_llargadaAut(build_ele, posBarraHor, build_ele.dadesTubHor.value[posBarraHor].RotarTub)
        llargada = build_ele.dadesTubHor.value[posBarraHor].Llargada

        #Definir valors de la barra Vertical Inicial
        encaixos, femelles, potes, forats, colis = get_valors_actuals(build_ele, posBarraHor)

        TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  15, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 3.75, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, False) #EncaixosPar))


        if build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB A":

            TubHoritzontal = PP_IS_Horitzontal(0,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  15, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 3.75, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, False) #EncaixosPar))

        elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB B":

            TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  14, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        True, True,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, True) #EncaixosPar))

        elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB C":

            TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  4, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, False) #EncaixosPar))

        elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB D":

            TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  86, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, False) #EncaixosPar))

        elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB E":

            TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  123, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        True, True,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, True) #EncaixosPar))

        elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB F":

            TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                        False,  8, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                        15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                        femelles, #Femelles, #matriu
                                        llargada/2, #posicio_centre_masses,
                                        False,100, #IsFirstCancam, Dis1cancam,
                                        False, 500, #IsSecondCancam, Dis2cancam,
                                        True, False,#PestanyaSuperior, PestanyaInferior,
                                        encaixos, True) #EncaixosPar))


        if not TubHoritzontal.is_valid():
            return[]

        matrix_PosHor = AllplanGeo.Matrix3D()
        if build_ele.dadesTubHor.value[posBarraHor].RotarTub:
            z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                        point2=  AllplanGeo.Point3D(0,0,1))
            matrix_PosHor.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))


        if not build_ele.dadesTubHor.value[posBarraHor].posAutomatica: # build_ele.dadesTubHor.value[posBarraHor].LlargadaAut
            matrix_PosHor.SetValue(12, build_ele.dadesTubHor.value[posBarraHor].desplX )
        else:
            matrix_PosHor.SetValue(12, get_posicioX(build_ele, posBarraHor))
        if not build_ele.dadesTubHor.value[posBarraHor].posAutomatica: # build_ele.dadesTubHor.value[posBarraHor].LlargadaAut
            matrix_PosHor.SetValue(13, build_ele.dadesTubHor.value[posBarraHor].desplY)
        else:
            matrix_PosHor.SetValue(13, get_posicioY(build_ele, posBarraHor))
        matrix_PosHor.SetValue(14, 0 )

        table_brepAux = TubHoritzontal.create()
        common_propsHor = AllplanBaseElements.CommonProperties()
        common_propsHor = TubHoritzontal.get_common_props()
        #if testEditBarraHorInterior:
            #common_propsHor.Color = build_ele.dadesTubHor.value[posBarraHor].FounColor#Vermell
            #handle_list = TubHoritzontal.create_handles()

        build_ele.DENHorInt.value = "T "
        atrENEsp = " "#definirAtributPers(build_ele,posBarraHor,"TubHoritzontal")
        if atrENEsp == "Xapa Frontal":
            build_ele.DENHorInt.value = "X"
        if build_ele.reconeixerDen.value:
            tubEsIgual, DEN = compare_attributes(build_ele, doc, TubHoritzontal)
            if (tubEsIgual):
                build_ele.DENHorInt.value = DEN


        cara_a, cara_a1, cara_a2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(TubHoritzontal.get_codi_cara_d_inv()) )

        table_attr_listAux = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                AllplanBaseElements.AttributeString(507, build_ele.NomIS.value),

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


                                AllplanBaseElements.AttributeString(2446, TubHoritzontal.get_codi_pota_inv()),#

                                AllplanBaseElements.AttributeString(1947, build_ele.dadesTubHor.value[posBarraHor].TipusTub),#

                                AllplanBaseElements.AttributeString(2430, TubHoritzontal.get_codi_pestanyes()),
                                AllplanBaseElements.AttributeString(2435, TubHoritzontal.get_codi_cancam()),
                                AllplanBaseElements.AttributeString(2431, TubHoritzontal.get_codi_mesures()),
                                AllplanBaseElements.AttributeString(2433, TubHoritzontal.get_codi_pota()),
                                AllplanBaseElements.AttributeString(2445, TubHoritzontal.get_seccio()),#
                                AllplanBaseElements.AttributeString(220,  TubHoritzontal.get_llargada()),
                                AllplanBaseElements.AttributeString(2455, TubHoritzontal.get_llargada()),
                                AllplanBaseElements.AttributeString(2103, build_ele.DENHorInt.value),
                                AllplanBaseElements.AttributeString(1083, build_ele.DENHorInt.value),
                                AllplanBaseElements.AttributeString(1084, TubHoritzontal.get_seccio()),
                                AllplanBaseElements.AttributeString(1085, TubHoritzontal.get_llargada()),
                                AllplanBaseElements.AttributeString(1087, "Horitzontal"),
                                AllplanBaseElements.AttributeString(508, "IS")]
        table_viewsAux = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsHor, table_brepAux)])]


        common_propsObjectRecess = AllplanBaseElements.CommonProperties()
        common_propsObjectRecess.Layer = 40054#56811#build_ele.BarraLayer.value#64178
        common_propsObjectRecess.Color = 16 #GRIS

        CavitatTubRecess = PP_IS_Horitzontal(random.random() * 3600,0, 50+10, 20,llargada, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectRecess.Color, common_propsObjectRecess.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
        horitzontal_BrepObject3Recess = CavitatTubRecess.create()
        horitzontal_views_object3Recess = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectRecess, horitzontal_BrepObject3Recess)])]

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomIS.value)]

        PosCavitatHor = AllplanGeo.Matrix3D()
        PosCavitatHor.SetValue(12, matrix_PosHor[12])
        PosCavitatHor.SetValue(13, matrix_PosHor[13] - 5)
        PosCavitatHor.SetValue(14, matrix_PosHor[14] )

        #if matrix_PosHor[12]< build_ele.BarraLlargada.value + build_ele.ExtenderInf.value and build_ele.BarresHorList.value[posBarraHor].BarraHor:

        #group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = CavitatTubRecess.get_params_list(),
        #                    hash_value = CavitatTubRecess.hash(), python_file = CavitatTubRecess.filename(),
        #                    views = horitzontal_views_object3Recess, matrix = PosCavitatHor, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))
        #group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = CavitatTubRecess.get_params_list(),
        #                    hash_value = CavitatTubRecess.hash(), python_file = CavitatTubRecess.filename(),
        #                    views = horitzontal_views_object3Recess, matrix = PosCavitatHor, common_props = common_propsObjectRecess, attribute_list = table_attr_listObject))


        group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = TubHoritzontal.get_params_list(),
                                hash_value = TubHoritzontal.hash(), python_file = TubHoritzontal.filename(),
                                views = table_viewsAux, matrix = matrix_PosHor, common_props = common_propsHor, attribute_list = table_attr_listAux))
        group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = TubHoritzontal.get_params_list(),
                                hash_value = TubHoritzontal.hash(), python_file = TubHoritzontal.filename(),
                                views = table_viewsAux, matrix = matrix_PosHor, common_props = common_propsHor, attribute_list = table_attr_listAux))



        if build_ele.dadesTubHor.value[posBarraHor].mostrarLiniaA:
            punt_central = matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].desplX
            pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] , matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinB, matrix_PosHor[14] )
            if (len(build_ele.dadesTubHor.value[posBarraHor].linia) > 1):
                linia = build_ele.dadesTubHor.value[posBarraHor].linia[len(build_ele.dadesTubHor.value[posBarraHor].linia)-1]
            else:
                build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace(linia = "Tipus 1")
                linia = "1"
            if (len(build_ele.dadesTubHor.value[posBarraHor].layer) > 1):
                layer = build_ele.dadesTubHor.value[posBarraHor].layer
            else:
                build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace(layer = "EN_FIXACIO_X")
                layer = "EN_FIXACIO_X"
            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTubHor.value[posBarraHor].Altura, llargada, not build_ele.dadesTubHor.value[posBarraHor].RotarTub, pointUbi, int(linia), layer)
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])
        if build_ele.dadesTubHor.value[posBarraHor].mostrarLiniaB:
            punt_central = matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].desplX
            pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] , matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinB, matrix_PosHor[14] )
            if (len(build_ele.dadesTubHor.value[posBarraHor].linia) > 1):
                linia = build_ele.dadesTubHor.value[posBarraHor].linia[len(build_ele.dadesTubHor.value[posBarraHor].linia)-1]
            else:
                build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace(linia = "Tipus 1")
                linia = "1"
            if (len(build_ele.dadesTubHor.value[posBarraHor].layer) > 1):
                layer = build_ele.dadesTubHor.value[posBarraHor].layer
            else:
                build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace(layer = "EN_FIXACIO_X")
                layer = "EN_FIXACIO_X"
            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTubHor.value[posBarraHor].Altura, llargada, not build_ele.dadesTubHor.value[posBarraHor].RotarTub, pointUbi, int(linia), layer)
            if polyhedronCentral != []:
                group_elems.append(polyhedronCentral[0])
                group_elems_preview.append(polyhedronCentral[0])
                group_elems.append(polyhedronCentral[3])
                group_elems_preview.append(polyhedronCentral[3])


        if build_ele.MostrarTDNums.value:
            numHor = create_num_on_view_Hor(build_ele, posBarraHor, matrix_PosHor)
            group_elems_preview.append(numHor)
            group_elems_preview.append(numHor)





    #definir atributs de la Barra Horitzontal Inferior

    pythonpartgroup = PythonPartGroup (build_ele.NomIS.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)
    pythonpartgroup_preview = PythonPartGroup (build_ele.NomIS.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems_preview)


    model_elem_list = pythonpartgroup.create()
    model_elem_list_preview = pythonpartgroup_preview.create()

    #guardar_valors_inici(build_ele,nVer)
    #build_ele.valueAntReforc.value = nRef
    #build_ele.SelectorPPAnt.value = build_ele.SelectorPP.value
    #build_ele.SelectorTDVAnt.value = nVer
    #build_ele.DistanciaEntreTDAnt.value = build_ele.DistanciaEntreTD.value
    #build_ele.BarraLlargadaAnt.value = build_ele.BarraLlargada.value
    build_ele.TubAnt.value = nHorSeleccionat
    crearLlistaFullHoritzontals(build_ele)

    #return (model_elem_list, handle_list)
    handle_list = create_handles(build_ele)

    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview)


def create_handles(build_ele ):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("ISllargada",
                                        AllplanGeo.Point3D(build_ele.ISllargada.value , build_ele.ISAmplada.value, 0 ),
                                        AllplanGeo.Point3D(build_ele.ISllargada.value, build_ele.ISAmplada.value, 0),
                                        [("ISllargada", HandleDirection.x_dir),
                                         ("ISAmplada", HandleDirection.y_dir)],
                                        HandleDirection.xy_dir),
                        HandleProperties("BarraPosicio",
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, build_ele.ISAmplada.value ),
                                        AllplanGeo.Point3D(0, 0, 0 ),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("PosicioXBalconera", HandleDirection.x_dir),
                                         ("PosicioZBalconera", HandleDirection.y_dir)],
                                        HandleDirection.xy_dir)
                                        #HandleProperties("LlargadaBalconera",
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, build_ele.LlargadaBalconera.value),
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, 0),
                                        #[("BarraLlargada", HandleDirection.z_dir)],
                                        #HandleDirection.z_dir)
                      ]

        return handle_list


def get_valors_actuals(build_ele, j):
    '''
    retorna valors de la Barra Actual
    get:j -> posicio[] de la barra

    return: Encaixos[], Femelles[], Potes[], Forats[], Colis[]

    '''

    Encaixos = []

    Femelles = []
    if build_ele.dadesTubHor.value[j].TipusTub == "TUB A" :
        posicio = 0
        orientSupA =  "Sup"
        while posicio < build_ele.dadesTubHor.value[j].Llargada:
            TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella profunditatFemella Ample_forat_femella ample_forat_femella Altura_forat_femella tubGirat')
            bob = TDHorCollection(Femella = True,
                                FemellaOr = orientSupA,
                                PosFemellaX = posicio,
                                PosFemellaY = 0,
                                Separacio_forat_femella = 46.25,#build_ele.dadesTDVert.value[nBarraVertical].BarraAmple - 3.0,
                                profunditatFemella =  3.1,
                                ample_forat_femella = 15,
                                Ample_forat_femella = 15,
                                Altura_forat_femella = 5,
                                tubGirat = False)
            Femelles.append(bob)
            bob = bob._replace(FemellaOr = getOrientacioInv(orientSupA))
            Femelles.append(bob)
            posicio += 700

    Potes = []

    Forats = []
    if build_ele.dadesTubHor.value[j].TipusTub == "TUB A" or build_ele.dadesTubHor.value[j].TipusTub == "TUB B" or build_ele.dadesTubHor.value[j].TipusTub == "TUB E" or build_ele.dadesTubHor.value[j].TipusTub == "TUB F":
        posicio = 375 #"TUB A"
        if build_ele.dadesTubHor.value[j].TipusTub == "TUB E":
            posicio = 675
        elif build_ele.dadesTubHor.value[j].TipusTub == "TUB B" or build_ele.dadesTubHor.value[j].TipusTub == "TUB F":
            posicio = 325
        while posicio < build_ele.dadesTubHor.value[j].Llargada:
            TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox Separator')
            bob = TDCollection( Forat = True,
                                orientacio = "Sup",
                                Posicio = posicio,
                                Llargada = 45,
                                Amplada = 25,
                                Complet = True,
                                LlargadaB = 45,
                                AmpladaB = 25,
                                MostrarBox = False,
                                Separator = '')
            if build_ele.dadesTubHor.value[j].TipusTub == "TUB E":
                posicio += 1400
            else:
                posicio += 700
            Forats.append(bob)

    Colis = []


    return Encaixos, Femelles, Potes, Forats, Colis


def create_polyline_interior(build_ele, punt_central, llargadaX, llargadaZ, isHor, pointUbi, linia = 1, layer = "EN_FIXACIO_X", posYdiferent = 200):

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
        vectorPOS.SetValue(13, posY)#+ build_ele.desplYI.value )
        vectorPOS.SetValue(14, posZ + 200)

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.SetValue(12, posX )#+ build_ele.desplXI.value )
        vectorPOSInv.SetValue(13, posY)#+ build_ele.desplYI.value )
        vectorPOSInv.SetValue(14, posZ - 200 )

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
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                        point2=  AllplanGeo.Point3D(1,0,0))
        vectorPOS.Rotation(z_axis, AllplanGeo.Angle.FromDeg(-90))
        vectorPOS.SetValue(12, posX - 25 )
        vectorPOS.SetValue(13, posY - 25 )
        vectorPOS.SetValue(14, posZ + 200)

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.Rotation(z_axis, AllplanGeo.Angle.FromDeg(-90))
        vectorPOSInv.SetValue(12, posX - 25 )
        vectorPOSInv.SetValue(13, posY - 25 )
        vectorPOSInv.SetValue(14, posZ - 200 )


        return [PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list),
                common_propsLinia,
                liniaInterior_brep,
                PythonPart ("liniaInterior", parameter_list = liniaInterior2.get_params_list(),
                                    hash_value = liniaInterior2.hash(), python_file = liniaInterior2.filename(),
                                    views = liniaInterior_views2, matrix = vectorPOSInv, common_props = common_propsLinia2, attribute_list = liniaInterior_attr_list)
                ]



def guardar_valors_hor(build_ele, j):
    '''
    Guardar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''
    #DADES TDV UNIQUES
    while len(build_ele.dadesTubHor.value) <= j:
        set_values_tub_hor(build_ele, j, j)
    else:
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Mostrar = build_ele.MostrarTub.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = build_ele.TipusTUB.value)
        #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Ample = 40)
        #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Altura = 50)
        if build_ele.TipusTUB.value == "TUB A":
            if build_ele.BarraLlargada.value > 2150:
                ctypes.windll.user32.MessageBoxW(0, "la llargada del tub tipus TUB A no pot ser mes gran a 2150", 0)
                build_ele.BarraLlargada.value = 2150
        elif build_ele.TipusTUB.value == "TUB E":
            if build_ele.BarraLlargada.value > 5650:
                ctypes.windll.user32.MessageBoxW(0, "la llargada del tub tipus TUB E no pot ser mes gran a 5650", 0)
                build_ele.BarraLlargada.value = 5650

        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Llargada = build_ele.BarraLlargada.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(LlargadaAut = build_ele.llargadaAutomatica.value)
        #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Gruix = 1.5)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplX = build_ele.desplX.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplY = build_ele.desplY.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(mostrarLiniaA = build_ele.mostrarLiniaA.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplLinA = build_ele.desplLinA.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(mostrarLiniaB = build_ele.mostrarLiniaB.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplLinB = build_ele.desplLinB.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(IsUseGlobalProp = build_ele.IsUseGlobalProp.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(FounColor = build_ele.FounColor.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(BarraLayer = build_ele.BarraLayer.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Ample_forat_femella = build_ele.Ample_forat_femella.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Altura_forat_femella = build_ele.Altura_forat_femella.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femella.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyaSuperior = build_ele.PestanyaSuperior.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyaInferior = build_ele.PestanyaInferior.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyesInv = build_ele.PestanyesInv.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(esProvisional = build_ele.esProvisional.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(linia = build_ele.TipusLinia.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(RotarTub = build_ele.RotarTub.value)
        if build_ele.RotarTub.value:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = build_ele.SelectorTubInferior.value)
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = build_ele.SelectorTubSuperior.value)
        else:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = build_ele.SelectorTubInferiorHor.value)
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = build_ele.SelectorTubSuperiorHor.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(posAutomatica = build_ele.posAutomatica.value)



def mostrar_valors_hor(build_ele, j):
    '''
    mostrar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''

    #DADES TDV UNIQUES
    if len(build_ele.dadesTubHor.value) <= j:
        set_values_tub_hor(build_ele, j, j)

    build_ele.MostrarTub.value = build_ele.dadesTubHor.value[j].Mostrar
    build_ele.TipusTUB.value = build_ele.dadesTubHor.value[j].TipusTub
    #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Ample = 40)
    #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Altura = 50)
    build_ele.BarraLlargada.value = build_ele.dadesTubHor.value[j].Llargada
    build_ele.llargadaAutomatica.value = build_ele.dadesTubHor.value[j].LlargadaAut
    #build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Gruix = 1.5)
    build_ele.desplX.value = build_ele.dadesTubHor.value[j].desplX
    build_ele.desplY.value = build_ele.dadesTubHor.value[j].desplY
    build_ele.mostrarLiniaA.value = build_ele.dadesTubHor.value[j].mostrarLiniaA
    build_ele.desplLinA.value = build_ele.dadesTubHor.value[j].desplLinA
    build_ele.mostrarLiniaB.value = build_ele.dadesTubHor.value[j].mostrarLiniaB
    build_ele.desplLinB.value = build_ele.dadesTubHor.value[j].desplLinB
    build_ele.IsUseGlobalProp.value = build_ele.dadesTubHor.value[j].IsUseGlobalProp
    build_ele.FounColor.value = build_ele.dadesTubHor.value[j].FounColor
    build_ele.BarraLayer.value = build_ele.dadesTubHor.value[j].BarraLayer
    build_ele.Ample_forat_femella.value = build_ele.dadesTubHor.value[j].Ample_forat_femella
    build_ele.Altura_forat_femella.value = build_ele.dadesTubHor.value[j].Altura_forat_femella
    build_ele.Separacio_forat_femella.value = build_ele.dadesTubHor.value[j].Separacio_forat_femella
    build_ele.PestanyaSuperior.value = build_ele.dadesTubHor.value[j].PestanyaSuperior
    build_ele.PestanyaInferior.value = build_ele.dadesTubHor.value[j].PestanyaInferior
    build_ele.PestanyesInv.value = build_ele.dadesTubHor.value[j].PestanyesInv
    build_ele.esProvisional.value = build_ele.dadesTubHor.value[j].esProvisional
    build_ele.TipusLinia.value = build_ele.dadesTubHor.value[j].linia
    build_ele.RotarTub.value = build_ele.dadesTubHor.value[j].RotarTub
    build_ele.SelectorTubInferior.value = build_ele.dadesTubHor.value[j].tubInferior
    build_ele.SelectorTubSuperior.value = build_ele.dadesTubHor.value[j].tubSuperior
    build_ele.SelectorTubInferiorHor.value = build_ele.dadesTubHor.value[j].tubInferior
    build_ele.SelectorTubSuperiorHor.value = build_ele.dadesTubHor.value[j].tubSuperior
    build_ele.posAutomatica.value = build_ele.dadesTubHor.value[j].posAutomatica



def set_values_tub_hor(build_ele, j, actual):
    #DADES TDV UNIQUES
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'Mostrar Ample Altura LlargadaAut Llargada Gruix '+
                                                   'desplX desplY ' +
                                                   'mostrarLiniaA desplLinA mostrarLiniaB desplLinB ' +
                                                   'IsUseGlobalProp FounColor BarraLayer '
                                                   'Ample_forat_femella Altura_forat_femella Separacio_forat_femella '+
                                                   'PestanyaSuperior PestanyaInferior PestanyesInv '+
                                                   'esProvisional '+
                                                   'linia layer TipusTub RotarTub '+
                                                   'tubInferior tubSuperior posAutomatica')
    bobDadesGlobal = TDCollectionDadesVert(Mostrar = False,
                                            Ample = 40,
                                            Altura = 50,
                                            LlargadaAut = True,
                                            Llargada = 1450,
                                            Gruix = 1.5,
                                            desplX = 0,
                                            desplY = 0,
                                            mostrarLiniaA = True,
                                            desplLinA = 0,
                                            mostrarLiniaB = False,
                                            desplLinB = 0,
                                            IsUseGlobalProp = False,
                                            FounColor = 1,
                                            BarraLayer = 1,
                                            Ample_forat_femella = 15,
                                            Altura_forat_femella = 2,#3.75,
                                            Separacio_forat_femella= 50,
                                            PestanyaSuperior = False,
                                            PestanyaInferior = False,
                                            PestanyesInv = False,
                                            esProvisional = False,
                                            linia = "Tipus 1",
                                            layer = "EN_ESTRUCTURA",
                                            TipusTub = "TUB E",
                                            RotarTub = False,
                                            tubInferior = "Tub 0",
                                            tubSuperior = "Tub 1",
                                            posAutomatica = True
                                            )

    extremsVert = 0
    interiorsVert = 0
    posinteriorVert = 650
    tubinf = "Tub 0"
    tubsup = "Tub 1"
    exteriorEsq = 4
    exteriorDre = 5
    print("Set Values tub hor")
    while len(build_ele.dadesTubHor.value) <= j:
        if len(build_ele.dadesTubHor.value) != 0:
            if len(build_ele.dadesTubHor.value) * 700 < build_ele.ISAmplada.value:
                bobDadesGlobal = bobDadesGlobal._replace(desplY = len(build_ele.dadesTubHor.value) * 700 )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
                bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
                bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))

                #elif len(build_ele.dadesTubHor.value) * 700 == build_ele.ISAmplada.value:
            elif len(build_ele.dadesTubHor.value) * 700 > build_ele.ISAmplada.value and (len(build_ele.dadesTubHor.value)-1) * 700 < build_ele.ISAmplada.value-50:
                bobDadesGlobal = bobDadesGlobal._replace(desplY = build_ele.ISAmplada.value -50 )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
                bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
                bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))
            else:
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                if extremsVert <= 1:
                    bobDadesGlobal = bobDadesGlobal._replace(TipusTub = "TUB A" )
                    bobDadesGlobal = bobDadesGlobal._replace(RotarTub = True)
                    bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub 0")
                    bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub 2")
                    bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = False)
                    bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISAmplada.value)
                    if actual == len(build_ele.dadesTubHor.value)-1:
                        build_ele.BarraLlargada.value = build_ele.ISAmplada.value
                    bobDadesGlobal = bobDadesGlobal._replace(desplY = 0)
                    if extremsVert == 1:
                        bobDadesGlobal = bobDadesGlobal._replace(desplX = build_ele.ISllargada.value)
                        bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                        exteriorEsq = len(build_ele.dadesTubHor.value)-1
                        exteriorDre = len(build_ele.dadesTubHor.value)
                    extremsVert += 1
                else:
                    bobDadesGlobal = bobDadesGlobal._replace(TipusTub = "TUB B" )
                    bobDadesGlobal = bobDadesGlobal._replace(RotarTub = True)
                    bobDadesGlobal = bobDadesGlobal._replace(tubInferior = tubinf)
                    bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = tubsup)
                    bobDadesGlobal = bobDadesGlobal._replace(desplX = posinteriorVert)
                    bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                    bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = True)

                    if posinteriorVert + 700 < build_ele.ISllargada.value:
                        posinteriorVert += 700
                    else:
                        posinteriorVert = 650

                        tubinf = "Tub " + str(getNumFromText(build_ele, tubinf, 3)+1)
                        tubsup = "Tub "+ str(getNumFromText(build_ele, tubsup, 3)+1)
        else:
            bobDadesGlobal = bobDadesGlobal._replace(desplY = len(build_ele.dadesTubHor.value) * 700 )#+ build_ele.dadesTubHor.value[0].Ample)
            bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
            bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
            bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
            bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
            bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))
            bobDadesGlobal = bobDadesGlobal._replace(desplX = 0)
            bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
            if actual == 0:
                build_ele.RotarTub.value = False
                build_ele.SelectorTubInferiorHor.value = "Tub "+str(exteriorEsq)
                build_ele.SelectorTubSuperiorHor.value = "Tub "+str(exteriorDre)#SelectorTubSuperiorHor
        build_ele.dadesTubHor.value.append(bobDadesGlobal)
    for x in range(0, len(build_ele.dadesTubHor.value)):
        if not build_ele.dadesTubHor.value[x].RotarTub:
            if x == actual:
                build_ele.SelectorTubInferiorHor.value = "Tub "+str(exteriorEsq)
                build_ele.SelectorTubSuperiorHor.value = "Tub "+str(exteriorDre)#SelectorTubSuperiorHor
            else:
                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubInferior = "Tub "+str(exteriorEsq))
                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubSuperior = "Tub "+str(exteriorDre))

    else:
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Mostrar = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Ample = 40)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Altura = 50)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Llargada = 5550)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(LlargadaAut = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Gruix = 1.5)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplX = 0)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplY = 0)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(mostrarLiniaA = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplLinA = 0)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(mostrarLiniaB = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(desplLinB = 0)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(IsUseGlobalProp = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(FounColor = 1)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(BarraLayer = 1)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Ample_forat_femella = 15)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Altura_forat_femella = 15)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(Separacio_forat_femella = 50)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyaSuperior = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyaInferior = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(PestanyesInv = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(esProvisional = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(linia = "Tipus 1")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(layer = "EN_ESTRUCTURA")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = "TUB E")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(RotarTub = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = "Tub 0")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = "Tub 1")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(posAutomatica = True)

def remove_values(build_ele, i):
    '''
    elimina valors en cas de que s'hagi reduit la llargada per no acommular valors innecessaris
    get: i -> Posicio

    return: -

    '''
    for x in range(i*NombreBarresVertInt, len(build_ele.listDesplVerticals.value)):
        build_ele.listDesplVerticals.value.pop()

    for x in range(i*2, len(build_ele.listDesplVerticalsInteriors.value)):
        build_ele.listDesplVerticalsInteriors.value.pop()

    for x in range(i*18, len(build_ele.dadesTDVert.value)):
        build_ele.dadesTDVert.value.pop()

    for x in range(i*3, len(build_ele.EncaixVertList.value)):
        build_ele.EncaixVertList.value.pop()

    for x in range(i*3, len(build_ele.FemellesVertList.value)):
        build_ele.FemellesVertList.value.pop()

    for x in range(i*3, len(build_ele.PotesVertList.value)):
        build_ele.PotesVertList.value.pop()

    for x in range(i*12, len(build_ele.ForatsVertList.value)):
        build_ele.ForatsVertList.value.pop()

    for x in range(i*5, len(build_ele.ColisVertList.value)):
        build_ele.ColisVertList.value.pop()

    for x in range(i*NombreBarresHorInt, len(build_ele.BarresHorList.value)):
        build_ele.BarresHorList.value.pop()

    for x in range(i*8, len(build_ele.BarresRefList.value)):
        build_ele.BarresRefList.value.pop()

    for x in range(i*17, len(build_ele.BarresVertList.value)):
        build_ele.BarresVertList.value.pop()

    for x in range(i*12, len(build_ele.BarresFrontList.value)):
        build_ele.BarresFrontList.value.pop()

    for x in range(i*10, len(build_ele.nListBarresFrontAux.value)):
        build_ele.BarresFrontListAux.value.pop()


def get_var_chair_vert(build_ele, i, FemellesAux):
    '''
    passar totes les variables entrades per l'usuari a String
    get: i -> posicio[] de la barra a retornar
         FemellesAux -> lista de femelles a afegir

    return: retorna llista de strings dels parametres

    '''
    param_list = []

    return param_list


def create_num_on_view_Hor(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesTubHor.value[j].Ample + 2, build_ele.dadesTubHor.value[j].Altura, build_ele.dadesTubHor.value[j].Llargada - 30, build_ele.dadesTubHor.value[j].Gruix,
                                False, 4, build_ele.dadesTubHor.value[j].BarraLayer, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                                AllplanBaseElements.AttributeString(1083, "num ID "),
                                AllplanBaseElements.AttributeString(508, "num")]

    vectorH1B = AllplanGeo.Matrix3D()
    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(1,0,0))
    vectorH1B.Rotation(z_axis, AllplanGeo.Angle.FromDeg(-90))
    vectorH1B.SetValue(12, vectorH1[12] - (20*build_ele.tamanyNumId.value) - 100)
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, vectorH1[14] )
    if j == 0:
        vectorH1B.SetValue(14, vectorH1[14] - 100 )

    test = PythonPart("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props=common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return test


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


def crearLlistaFullHoritzontals(build_ele):

    Afegits = 0
    AfegitsVert = 0
    for barra in range(0, build_ele.IntegerISSelectorHor.value):
        if build_ele.IntegerISSelectorHor.value < len(build_ele.dadesTubHor.value):
            if not build_ele.dadesTubHor.value[barra].RotarTub:
                if Afegits >= len(build_ele.valueListBarresHorBalcOnlyNum.value):
                    build_ele.valueListBarresHorBalcOnlyNum.value.append("Tub " + str(barra))
                else:
                    build_ele.valueListBarresHorBalcOnlyNum.value[Afegits] = "Tub " + str(barra)

                Afegits += 1
            else:
                if AfegitsVert >= len(build_ele.valueListBarresHorBalcOnlyNumVert.value):
                    build_ele.valueListBarresHorBalcOnlyNumVert.value.append("Tub " + str(barra))
                else:
                    build_ele.valueListBarresHorBalcOnlyNumVert.value[AfegitsVert] = "Tub " + str(barra)
                AfegitsVert += 1



    while Afegits < len(build_ele.valueListBarresHorBalcOnlyNum.value):
        build_ele.valueListBarresHorBalcOnlyNum.value.pop()
    while AfegitsVert < len(build_ele.valueListBarresHorBalcOnlyNumVert.value):
        build_ele.valueListBarresHorBalcOnlyNumVert.value.pop()

def get_posicioX(build_ele, posBarraHor):
    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
    if build_ele.dadesTubHor.value[posBarraHor].RotarTub: # build_ele.dadesTubHor.value[posBarraHor].LlargadaAut
        return build_ele.dadesTubHor.value[posBarraHor].desplX + build_ele.dadesTubHor.value[nTubInf].Altura
    return build_ele.dadesTubHor.value[posBarraHor].desplX

def get_posicioY(build_ele, posBarraHor):
    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
    if build_ele.dadesTubHor.value[posBarraHor].RotarTub and build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
        return build_ele.dadesTubHor.value[nTubInf].desplY + build_ele.dadesTubHor.value[nTubInf].Altura
    return build_ele.dadesTubHor.value[posBarraHor].desplY

def set_llargadaAut(build_ele, posBarraHor, esVertical):
    if esVertical:
        nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
        posInf = build_ele.dadesTubHor.value[nTubInf].desplY + build_ele.dadesTubHor.value[nTubInf].Altura
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplY
    else:
        nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
        posInf = build_ele.dadesTubHor.value[nTubInf].desplX + build_ele.dadesTubHor.value[nTubInf].Altura
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplX
    if posSup-posInf > 0:
        build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace (Llargada = posSup-posInf)
    else:
        build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace (Llargada = 50)


