"""
Script for IS_conjunt - Vertical - Group
"""
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Geometry as Geometry
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
from .IS_LProvisional import LProvisional


from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from HandleProperties import HandleProperties
from HandleDirection import HandleDirection
from CreateElementResult import CreateElementResult
from Utils import LibraryBitmapPreview
from PreviewSymbols import PreviewSymbols
from Utils import TextReferencePointPosition

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

    #build_ele.actualitzaTubs.value = False
    build_ele.change_property(handle_prop, input_pnt)

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
    if event_id == 1000:#recalcul IS
        while len(build_ele.dadesTubHor.value) != 0:
            build_ele.dadesTubHor.value.pop()
        build_ele.IntegerISSelectorHor.value = recalcul_n_barres(build_ele)
        build_ele.MostrarTub.value = True
        build_ele.refactor.value = True
    elif event_id == 1001:#forat base
        build_ele.crearForat.value = True

    elif event_id == 1002:#crear creu interior amb tubs als extrems d'aquesta
        build_ele.crearCreu.value = True

    elif event_id == 1003:#forat amb adaptacio de horitzontals fins trobar une vertical
        build_ele.crearForat2.value = True

    elif event_id == 1004:#Forat amb adaptació de verticals fins trobar la horitzontal mes proxima
        build_ele.crearForat3.value = True

    elif event_id == 1005:#Crear creu interior a tubs propers?
        build_ele.crearCreuSenseTubsExteriors.value = True

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

    build_ele.BarraLayer.value = 40068
    build_ele.zUnique.value = random.random()*3600
    crearLlistaFullHoritzontals(build_ele)

    group_elems = [] #All elements of suite
    group_elems_preview = [] #All elements of suite
    handle_list = []
    preview_symbols = PreviewSymbols()

    mostratError = False


    nHorSeleccionat = getNumFromText(build_ele, build_ele.SelectorTubHor.value, 3)

    while build_ele.IntegerISSelectorHor.value +1 > len(build_ele.dadesTubHor.value):
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value+1, nHorSeleccionat)

    if build_ele.SelectorPP.value != 1:
        build_ele.actualitzaTubs.value = True
        liniesAutomatitzacio = crearLiniesAutomatitzacio(build_ele, doc, nHorSeleccionat)

        for linia in liniesAutomatitzacio:
            group_elems_preview.append(linia)

        handle_list = create_handles_linies(build_ele)
        if build_ele.crearForat.value :
            crear_forat_auto(build_ele, doc, nHorSeleccionat, 1)
            build_ele.crearForat.value = False

        if build_ele.crearCreu.value :
            crear_creu_auto(build_ele, doc, nHorSeleccionat)
            build_ele.crearCreu.value = False

        if build_ele.crearForat2.value :
            crear_forat_auto(build_ele, doc, nHorSeleccionat, 2)
            build_ele.crearForat2.value = False

        if build_ele.crearForat3.value :
            crear_forat_auto(build_ele, doc, nHorSeleccionat, 3)
            build_ele.crearForat3.value = False

        if build_ele.crearCreuSenseTubsExteriors.value :
            crear_creu_auto(build_ele, doc, nHorSeleccionat)
            build_ele.crearCreuSenseTubsExteriors.value = False

    if build_ele.RotarTubAnt.value and not build_ele.RotarTub.value:
        build_ele.desplX.value = 50

    if build_ele.actualitzaTubs.value:

        #for posBarraHor in range(0, build_ele.IntegerISSelectorHor.value):#len(build_ele.dadesTubHor.value)):
        #    if build_ele.dadesTubHor.value[posBarraHor].LlargadaAut :
        #        llargada = set_llargadaAut(build_ele, posBarraHor, build_ele.dadesTubHor.value[posBarraHor].RotarTub)
        #        if build_ele.dadesTubHor.value[posBarraHor].tipusTubAuto:
        #            detectar_tipus_tub(build_ele, doc, posBarraHor, nHorSeleccionat)
        #        else:
        #            mostratError = detectar_es_posible(build_ele, doc, posBarraHor, nHorSeleccionat, mostratError)
        for posBarraHor in range(0, build_ele.IntegerISSelectorHor.value):#len(build_ele.dadesTubHor.value)):

            if nHorSeleccionat == posBarraHor:
                if nHorSeleccionat != build_ele.TubAnt.value:
                    mostrar_valors_hor(build_ele, nHorSeleccionat)
                else:
                    guardar_valors_hor(build_ele, nHorSeleccionat)


            if build_ele.dadesTubHor.value[posBarraHor].LlargadaAut :#and build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                llargada = set_llargadaAut(build_ele, posBarraHor, build_ele.dadesTubHor.value[posBarraHor].RotarTub)

                if build_ele.dadesTubHor.value[posBarraHor].tipusTubAuto:
                    detectar_tipus_tub(build_ele, doc, posBarraHor, nHorSeleccionat)#, encaixAmbTubInf, encaixAmbTubSup)
                else:
                    mostratError = detectar_es_posible(build_ele, doc, posBarraHor, nHorSeleccionat, mostratError)
            #print("[" + str(posBarraHor) + "]" + str(build_ele.dadesTubHor.value[posBarraHor].Llargada) + " -- " + str(build_ele.dadesTubHor.value[posBarraHor].desplX))
            llargada = build_ele.dadesTubHor.value[posBarraHor].Llargada #- build_ele.dadesTubHor.value[posBarraHor].retallFinal
            if llargada <= 0:
                llargada = 50
            if build_ele.dadesTubHor.value[posBarraHor].desplY < 0 and build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                    #matrix_PosHor.SetValue(13, 0)
                    build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace(desplY = 0)
                    llargada = llargada - build_ele.dadesTubHor.value[posBarraHor].desplY


            if nHorSeleccionat == posBarraHor:
                build_ele.BarraLlargada.value = llargada

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

            AtributoPers01 = ""
            AtributoPers03 = str(0)
            AtributoPers05 = "0;0;;"
            AtributoPersIdentRetalls = "0;0"


            if build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB A":

                AtributoPers01 = "A;L2150_FEMELLA_TLAT"
                AtributoPers03 = str(2150)
                retallFinal = 2150 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = "352,5;655;y;Female"


                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  15, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 3.75, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            False, False,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, False, #EncaixosPar
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 2150) #)

            elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB B":

                AtributoPers01 = "B;L650_MASCLE_TRAVSIMPLE"
                AtributoPers03 = str(650)
                retallFinal = 650 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = "302,5;;m;Male"

                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  14, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            llargada == 650 and build_ele.dadesTubHor.value[posBarraHor].retallFinal <= 0, build_ele.dadesTubHor.value[posBarraHor].retallInicial == 0,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, True, #EncaixosPar))
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 650) #)

            elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB C":

                AtributoPers01 = "C;L650_LLIS_TRAVSIMPLE"
                AtributoPers03 = str(650)
                retallFinal = 650 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = ";;;None"

                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  4, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            False, False,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, False, #EncaixosPar))
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 650) #)

            elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB D":

                AtributoPers01 = "D;L1350_LLIS_TRAVDOBLE"
                AtributoPers03 = str(1350)
                retallFinal = 1350 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = ";;;None"

                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  86, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            False, False,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, False, #EncaixosPar))
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 1350) #)

            elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB E":

                AtributoPers01 = "E;L5550_MASCLE_TLON"
                AtributoPers03 = str(5550)
                retallFinal = 5550 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = "652,5;1355;m;Male"

                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  123, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            llargada == 5550 and build_ele.dadesTubHor.value[posBarraHor].retallFinal <= 0, build_ele.dadesTubHor.value[posBarraHor].retallInicial == 0,#True, True,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, True, #EncaixosPar))
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 5550) #)

            elif build_ele.dadesTubHor.value[posBarraHor].TipusTub == "TUB F":

                AtributoPers01 = "F;L1350_MASCLE_TRAVDOBLE"
                AtributoPers03 = str(1350)
                retallFinal = 1350 - llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                AtributoPersIdentRetalls = str(build_ele.dadesTubHor.value[posBarraHor].retallInicial) + ";"+ str(retallFinal)
                AtributoPers05 = "302,5;655;y;Male"

                TubHoritzontal = PP_IS_Horitzontal(random.random() * 3600,0, 50, 20,llargada, 1.5,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                            False,  8, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                            colis, potes, forats, #ColisPar, PotaPar, #matrius
                                            15, 2.5, 30,#build_ele.dadesTubHor.value[posBarraHor].Ample_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Altura_forat_femella, build_ele.dadesTubHor.value[posBarraHor].Separacio_forat_femella,
                                            femelles, #Femelles, #matriu
                                            llargada/2, #posicio_centre_masses,
                                            False,100, #IsFirstCancam, Dis1cancam,
                                            False, 500, #IsSecondCancam, Dis2cancam,
                                            llargada == 1350 and build_ele.dadesTubHor.value[posBarraHor].retallFinal <= 0, build_ele.dadesTubHor.value[posBarraHor].retallInicial <= 0,#PestanyaSuperior, PestanyaInferior,
                                            encaixos, True, #EncaixosPar))
                                            build_ele.dadesTubHor.value[posBarraHor].retallInicial, llargada - build_ele.dadesTubHor.value[posBarraHor].retallFinal, 1350) #)

            if nHorSeleccionat == posBarraHor:
                build_ele.BarraLlargadaOriginal.value = int(AtributoPers03)

            if not TubHoritzontal.is_valid():
                return[]

            matrix_PosHor = AllplanGeo.Matrix3D()
            if build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                            point2=  AllplanGeo.Point3D(0,0,1))
                matrix_PosHor.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))


            if not build_ele.dadesTubHor.value[posBarraHor].posAutomatica: # build_ele.dadesTubHor.value[posBarraHor].LlargadaAut
                matrix_PosHor.SetValue(12, build_ele.dadesTubHor.value[posBarraHor].desplX)
                matrix_PosHor.SetValue(13, build_ele.dadesTubHor.value[posBarraHor].desplY)
                if build_ele.dadesTubHor.value[posBarraHor].desplX < (-50):
                    matrix_PosHor.SetValue(12, -50)
                if build_ele.dadesTubHor.value[posBarraHor].desplY < 0 and build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                    matrix_PosHor.SetValue(13, 0)
                    llargada = llargada - build_ele.dadesTubHor.value[posBarraHor].desplY
            else:
                matrix_PosHor.SetValue(12, get_posicioX(build_ele, posBarraHor))
                matrix_PosHor.SetValue(13, get_posicioY(build_ele, posBarraHor))
            matrix_PosHor.SetValue(14, 0 )


            table_brepAux = TubHoritzontal.create()
            common_propsHor = AllplanBaseElements.CommonProperties()
            common_propsHor = TubHoritzontal.get_common_props()
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

            Rotar = "Horitzontal"
            if build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                Rotar = "Vertical"
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

                                    AllplanBaseElements.AttributeString(1947, ""),#build_ele.dadesTubHor.value[posBarraHor].TipusTub),#

                                    AllplanBaseElements.AttributeString(2430, TubHoritzontal.get_codi_pestanyes()),
                                    AllplanBaseElements.AttributeString(2435, TubHoritzontal.get_codi_cancam()),
                                    AllplanBaseElements.AttributeString(2431, TubHoritzontal.get_codi_mesures()),
                                    AllplanBaseElements.AttributeString(2433, TubHoritzontal.get_codi_pota()),
                                    AllplanBaseElements.AttributeString(2445, TubHoritzontal.get_seccio()),#
                                    AllplanBaseElements.AttributeString(220,  TubHoritzontal.get_llargada()),
                                    AllplanBaseElements.AttributeString(2455, TubHoritzontal.get_llargada()),
                                    AllplanBaseElements.AttributeString(2103, "T" + str(AtributoPersIdentRetalls)),#build_ele.DENHorInt.value),
                                    #AllplanBaseElements.AttributeString(1083, build_ele.DENHorInt.value), #Atributo Personalizado 01
                                    AllplanBaseElements.AttributeString(1083, AtributoPers01), #Atributo Personalizado 01
                                    AllplanBaseElements.AttributeString(1084, TubHoritzontal.get_seccio()),#Atributo Personalizado 02
                                    #AllplanBaseElements.AttributeString(1085, TubHoritzontal.get_llargada()),#Atributo Personalizado 03
                                    AllplanBaseElements.AttributeString(1085, AtributoPers03),#Atributo Personalizado 03
                                    AllplanBaseElements.AttributeString(1086, " "),#Atributo Personalizado 04
                                    AllplanBaseElements.AttributeString(1087, AtributoPers05),#Atributo Personalizado 05
                                    AllplanBaseElements.AttributeString(1095, " "),
                                    AllplanBaseElements.AttributeString(1096, " "),
                                    AllplanBaseElements.AttributeString(1097, " "),
                                    AllplanBaseElements.AttributeString(1098, " "),
                                    AllplanBaseElements.AttributeString(1099, " "),
                                    AllplanBaseElements.AttributeString(1900, " "),
                                    AllplanBaseElements.AttributeString(1901, " "),
                                    AllplanBaseElements.AttributeString(1902, " "),
                                    AllplanBaseElements.AttributeString(1903, " "),
                                    AllplanBaseElements.AttributeString(1904, " "),
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


            if build_ele.dadesTubHor.value[posBarraHor].Mostrar and \
                build_ele.dadesTubHor.value[posBarraHor].Llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial -  build_ele.dadesTubHor.value[posBarraHor].retallFinal > 0:
                group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = TubHoritzontal.get_params_list(),
                                        hash_value = TubHoritzontal.hash(), python_file = TubHoritzontal.filename(),
                                        views = table_viewsAux, matrix = matrix_PosHor, common_props = common_propsHor, attribute_list = table_attr_listAux))
                group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = TubHoritzontal.get_params_list(),
                                        hash_value = TubHoritzontal.hash(), python_file = TubHoritzontal.filename(),
                                        views = table_viewsAux, matrix = matrix_PosHor, common_props = common_propsHor, attribute_list = table_attr_listAux))


                vertx = Geometry.Point3D(matrix_PosHor[12], matrix_PosHor[13],   matrix_PosHor[14])
                #preview_symbols#group_elems_preview
                colorNum = 4
                posXNum = -80
                posYNum = 20
                if build_ele.dadesTubHor.value[posBarraHor].RotarTub: #Vertical
                    colorNum = 4
                    posYNum = 80
                    vertx = Geometry.Point3D(matrix_PosHor[12] , matrix_PosHor[13]+ build_ele.dadesTubHor.value[posBarraHor].retallInicial,   matrix_PosHor[14])
                else: #horitzontal
                    colorNum = 8
                    vertx = Geometry.Point3D(matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].retallInicial, matrix_PosHor[13],   matrix_PosHor[14])

                if build_ele.MostrarTDNums.value:
                    preview_symbols.add_text(text=              str(posBarraHor),
                                    reference_point=   vertx + AllplanGeo.Point3D(posXNum,posYNum,0),
                                    ref_pnt_pos=       TextReferencePointPosition.CENTER_RIGHT,
                                    height=            build_ele.tamanyNumId.value*5,
                                    color=             colorNum,
                                    rotation_angle=    AllplanGeo.Angle())

                #preview_symbols.add_cross(reference_point=  vertx,
                #                      width=            25,
                #                      color=            6)


                if build_ele.dadesTubHor.value[posBarraHor].esProvisional:
                    if crear_LProvisional(build_ele,posBarraHor,matrix_PosHor, False, False , 1) != []:
                        llistaLProv = []
                        try:
                            llistaLProv = getLActives(build_ele, posBarraHor)
                        except Exception as e:
                            llistaLProv = [1,2,3,4]
                            print("Llista Provisional no creada" + str(e))
                        for numL in llistaLProv:
                            #if esFinal:
                            listLProvisional = crear_LProvisional(build_ele,posBarraHor,matrix_PosHor, False, False , numL)
                            if len(listLProvisional) > 2:
                                group_elems.append(listLProvisional[0])
                                group_elems_preview.append(listLProvisional[0])



                if build_ele.dadesTubHor.value[posBarraHor].mostrarLiniaA and build_ele.mostrarEix.value:

                    punt_central = matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].desplX + build_ele.dadesTubHor.value[posBarraHor].retallInicial
                    if not build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                        pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].retallInicial, matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinA, matrix_PosHor[14] )
                    else:
                        pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] , matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].retallInicial + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinA, matrix_PosHor[14] )
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
                    llargadaLinia = llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTubHor.value[posBarraHor].Altura, llargadaLinia, not build_ele.dadesTubHor.value[posBarraHor].RotarTub, pointUbi, int(linia), layer)
                    if polyhedronCentral != []:
                        group_elems.append(polyhedronCentral[0])
                        group_elems_preview.append(polyhedronCentral[0])
                    #    group_elems.append(polyhedronCentral[3])
                    #    group_elems_preview.append(polyhedronCentral[3])
                if build_ele.dadesTubHor.value[posBarraHor].mostrarLiniaB and build_ele.mostrarEix.value:
                    punt_central = matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].desplX + build_ele.dadesTubHor.value[posBarraHor].retallInicial
                    if not build_ele.dadesTubHor.value[posBarraHor].RotarTub:
                        pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] + build_ele.dadesTubHor.value[posBarraHor].retallInicial, matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinB, matrix_PosHor[14] )
                    else:
                        pointUbi = AllplanGeo.Point3D(matrix_PosHor[12] , matrix_PosHor[13] + build_ele.dadesTubHor.value[posBarraHor].retallInicial + build_ele.dadesTubHor.value[posBarraHor].Altura/2 + build_ele.dadesTubHor.value[posBarraHor].desplLinB, matrix_PosHor[14] )
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
                    llargadaLinia = llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTubHor.value[posBarraHor].Altura, llargadaLinia, not build_ele.dadesTubHor.value[posBarraHor].RotarTub, pointUbi, int(linia), layer)
                    if polyhedronCentral != []:
                        group_elems.append(polyhedronCentral[0])
                        group_elems_preview.append(polyhedronCentral[0])
                    #    group_elems.append(polyhedronCentral[3])
                    #    group_elems_preview.append(polyhedronCentral[3])
    else:
        liniesAutomatitzacio = crearLiniesTamanyIS(build_ele, doc, nHorSeleccionat)

        for linia in liniesAutomatitzacio:
            group_elems.append(linia)
            group_elems_preview.append(linia)


    #if build_ele.mostrarNomIS.value:
    #    nameText =  PreviewSymbols()
    #    nameText.add_text(text=     str(build_ele.NomIS.value),
    #                    reference_point=   AllplanGeo.Point3D(0,build_ele.ISAmplada.value + 100 ,0),
    #                    ref_pnt_pos=       TextReferencePointPosition.TOP_LEFT,#.CENTER_RIGHT,
    #                    height=            30,
    #                    color=             colorNum,
    #                    rotation_angle=    AllplanGeo.Angle())
    #    group_elems.append(nameText)
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
    build_ele.RotarTubAnt.value = build_ele.RotarTub.value
    build_ele.actualitzaTubs.value = True
    build_ele.BarraLlargadaReal.value = build_ele.BarraLlargada.value - build_ele.retallInicial.value - build_ele.retallFinal.value
    crearLlistaFullHoritzontals(build_ele)

    #return (model_elem_list, handle_list)
    if build_ele.SelectorPP.value == 1:
        handle_list = create_handles(build_ele)

    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview,
                                placement_point= None,
                                multi_placement= False,
                                preview_symbols = preview_symbols)


def create_handles(build_ele ):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("ISllargada",
                                        AllplanGeo.Point3D(build_ele.ISllargada.value -50 , build_ele.ISAmplada.value, 0 ),
                                        AllplanGeo.Point3D(-50, 0, 0),
                                        [("ISllargada", HandleDirection.x_dir),
                                         ("ISAmplada", HandleDirection.y_dir)], # type: ignore
                                        HandleDirection.xy_dir),
                        HandleProperties("BarraPosicio",
                                        #AllplanGeo.Point3D(build_ele.PosicioXlinia.value, 0, build_ele.ISAmplada.value ),
                                        AllplanGeo.Point3D(0-50, 0, 0 ),
                                        AllplanGeo.Point3D(-50, 0, 0),
                                        [("desplX", HandleDirection.x_dir),
                                         ("desplY", HandleDirection.y_dir)],# type: ignore
                                        HandleDirection.xy_dir)
                                        #HandleProperties("Llargadalinia",
                                        #AllplanGeo.Point3D(build_ele.PosicioXlinia.value, 0, build_ele.Llargadalinia.value),
                                        #AllplanGeo.Point3D(build_ele.PosicioXlinia.value, 0, 0),
                                        #[("BarraLlargada", HandleDirection.z_dir)],
                                        #HandleDirection.z_dir)
                      ]

        return handle_list

def create_handles_linies(build_ele ):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(build_ele.PosicioXlinia.value -50 + build_ele.Amplelinia.value , build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value, 0 ),
                                        AllplanGeo.Point3D(build_ele.PosicioXlinia.value  -50, build_ele.PosicioYlinia.value , 0),
                                        [("Amplelinia", HandleDirection.x_dir),
                                         ("Llargadalinia", HandleDirection.y_dir)],# type: ignore
                                        HandleDirection.xy_dir,
                                        False,
                                        info_text= "Tamany"),
                        HandleProperties("BarraPosicio",
                                        AllplanGeo.Point3D(build_ele.PosicioXlinia.value -50 , build_ele.PosicioYlinia.value,  0 ),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("PosicioXlinia", HandleDirection.x_dir),
                                         ("PosicioYlinia", HandleDirection.y_dir)],# type: ignore
                                        HandleDirection.xy_dir,
                                        False,
                                        info_text= "Posicio")
                                        #HandleProperties("Llargadalinia",
                                        #AllplanGeo.Point3D(build_ele.PosicioXlinia.value, 0, build_ele.Llargadalinia.value),
                                        #AllplanGeo.Point3D(build_ele.PosicioXlinia.value, 0, 0),
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
    if build_ele.dadesTubHor.value[j].TipusTub == "TUB A" or build_ele.dadesTubHor.value[j].TipusTub == "TUB E" or build_ele.dadesTubHor.value[j].TipusTub == "TUB F" or build_ele.dadesTubHor.value[j].TipusTub == "TUB D":
        posicio = 0
        Separacio_forat_femella = 46.25
        if build_ele.dadesTubHor.value[j].TipusTub == "TUB E" or build_ele.dadesTubHor.value[j].TipusTub == "TUB F" :
            posicio = -50
            Separacio_forat_femella = 47.5
        elif build_ele.dadesTubHor.value[j].TipusTub == "TUB D":
            posicio = -100
            Separacio_forat_femella = 47.5

        orientSupA =  "Sup"
        while posicio < build_ele.dadesTubHor.value[j].Llargada:
            TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella profunditatFemella Ample_forat_femella ample_forat_femella Altura_forat_femella tubGirat')
            bob = TDHorCollection(Femella = True,
                                FemellaOr = orientSupA,
                                PosFemellaX = posicio,
                                PosFemellaY = 0,
                                Separacio_forat_femella = Separacio_forat_femella,#build_ele.dadesTubHor.value[nBarraVertical].BarraAmple - 3.0,
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

    common_propsLinia.Layer = 40163#(IS_EIXOS)   #40068 #40100#(EN_FIXACIO_Y)#Canvair a X
    #if layer == "EN_FIXACIO_Y":
    common_propsLinia2.Layer = 40163#(IS_EIXOS)     #40068 #40099#(EN_FIXACIO_X)#Canviar a Y
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
                liniaInterior_brep]#,
                #PythonPart ("liniaInterior", parameter_list = liniaInterior2.get_params_list(),
                #                    hash_value = liniaInterior2.hash(), python_file = liniaInterior2.filename(),
                #                    views = liniaInterior_views2, matrix = vectorPOSInv, common_props = common_propsLinia2, attribute_list = liniaInterior_attr_list)
                #]
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
                liniaInterior_brep#,
                #PythonPart ("liniaInterior", parameter_list = liniaInterior2.get_params_list(),
                #                    hash_value = liniaInterior2.hash(), python_file = liniaInterior2.filename(),
                #                    views = liniaInterior_views2, matrix = vectorPOSInv, common_props = common_propsLinia2, attribute_list = liniaInterior_attr_list)
                ]

def crearLiniesAutomatitzacio(build_ele, doc, posBarraHor):
    group_elems_preview = []
    pointUbi = AllplanGeo.Point3D(build_ele.PosicioXlinia.value - 50, build_ele.PosicioYlinia.value , 0 )
    lineX = create_polyline_interior(build_ele, 0, 0, build_ele.Amplelinia.value, True, pointUbi)
    if lineX != []:
        #group_elems.append(lineX[0])
        group_elems_preview.append(lineX[0])
        #group_elems_preview.append(lineX[3])
        #preview_symbols.add_arrow(pointUbi, build_ele.Amplelinia.value, 1, AllplanGeo.Angle(0))
        #preview_symbols.add_filled_rectangle(pointUbi, int(build_ele.Amplelinia.value/4), 1, AllplanGeo.Angle(0))
    pointUbi = AllplanGeo.Point3D(build_ele.PosicioXlinia.value - 25, build_ele.PosicioYlinia.value + 25, 0 )
    lineZ = create_polyline_interior(build_ele, 0,0,build_ele.Llargadalinia.value, False, pointUbi)
    if lineZ != []:
        #group_elems.append(lineZ[0])
        group_elems_preview.append(lineZ[0])
        #group_elems_preview.append(lineZ[3])
        #preview_symbols.add_arrow(pointUbi, build_ele.Llargadalinia.value, 1, AllplanGeo.Angle(90))
    pointUbi = AllplanGeo.Point3D(build_ele.PosicioXlinia.value - 50, build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value , 0 )
    lineX = create_polyline_interior(build_ele, 0, 0, build_ele.Amplelinia.value, True, pointUbi)
    if lineX != []:
        #group_elems.append(lineX[0])
        group_elems_preview.append(lineX[0])
        #group_elems_preview.append(lineX[3])
    pointUbi = AllplanGeo.Point3D(build_ele.PosicioXlinia.value + build_ele.Amplelinia.value - 25, build_ele.PosicioYlinia.value +25, 0)
    lineZ = create_polyline_interior(build_ele, 0,0,build_ele.Llargadalinia.value, False, pointUbi)
    if lineZ != []:
        #group_elems.append(lineZ[0])
        group_elems_preview.append(lineZ[0])
        #group_elems_preview.append(lineZ[3])

    return group_elems_preview


def crearLiniesTamanyIS(build_ele, doc, posBarraHor):
    group_elems_preview = []
    pointUbi = AllplanGeo.Point3D(0 - 50, 0 , 0 )
    lineX = create_polyline_interior(build_ele, 0, 0, build_ele.ISllargada.value, True, pointUbi)
    if lineX != []:
        group_elems_preview.append(lineX[0])
        #group_elems_preview.append(lineX[3])
    pointUbi = AllplanGeo.Point3D(0 - 25,  25, 0 )
    lineZ = create_polyline_interior(build_ele, 0,0,build_ele.ISAmplada.value, False, pointUbi)
    if lineZ != []:
        group_elems_preview.append(lineZ[0])
        #group_elems_preview.append(lineZ[3])
    pointUbi = AllplanGeo.Point3D(0 - 50, build_ele.ISAmplada.value , 0 )
    lineX = create_polyline_interior(build_ele, 0, 0, build_ele.ISllargada.value, True, pointUbi)
    if lineX != []:
        group_elems_preview.append(lineX[0])
        #group_elems_preview.append(lineX[3])
    pointUbi = AllplanGeo.Point3D(build_ele.ISllargada.value - 25, 25, 0)
    lineZ = create_polyline_interior(build_ele, 0,0,build_ele.ISAmplada.value, False, pointUbi)
    if lineZ != []:
        group_elems_preview.append(lineZ[0])
        #group_elems_preview.append(lineZ[3])

    return group_elems_preview

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
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provSupEsq = build_ele.provSupEsq.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provSupDre = build_ele.provSupDre.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfEsq = build_ele.provInfEsq.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfDre = build_ele.provInfDre.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfCen = build_ele.provInfCen.value)

        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(linia = build_ele.TipusLinia.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(RotarTub = build_ele.RotarTub.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tipusTubAuto = build_ele.tipusTubAuto.value)

        if build_ele.RotarTub.value:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = build_ele.SelectorTubInferior.value)
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = build_ele.SelectorTubSuperior.value)
        else:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = build_ele.SelectorTubInferiorHor.value)
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = build_ele.SelectorTubSuperiorHor.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(posAutomatica = build_ele.posAutomatica.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallInicial = build_ele.retallInicial.value)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallFinal = build_ele.BarraLlargada.value - build_ele.retallFinal.value)
        if build_ele.retallFinal.value <= 0:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallFinal = 0)
        else:
            build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallFinal = build_ele.retallFinal.value)

    if build_ele.dadesTubHor.value[j].tipusTubAuto:
        encaixAmbTubInf = encaix_pestanyes_amb_inferior(build_ele, "doc", j, j)
        encaixAmbTubSup = encaix_pestanyes_amb_superior(build_ele, "doc", j, j)
        if build_ele.dadesTubHor.value[j].posAutomatica:
            if ((not encaixAmbTubInf and build_ele.dadesTubHor.value[j].retallInicial == 0) and \
                (not encaixAmbTubSup and build_ele.dadesTubHor.value[j].retallFinal == 0)):
                build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = "TUB C")
                #print(str(j)+" - NO Encaixa amb Inici i Final")
            elif ((  encaixAmbTubInf and build_ele.dadesTubHor.value[j].retallInicial == 0) and \
                  (  encaixAmbTubSup and build_ele.dadesTubHor.value[j].retallFinal == 0)):
                build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = "TUB B")
                #print(str(j)+" - NO Encaixa amb Inici i Final")
            else:
                build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = "TUB B")
                #print(str(j)+" - Encaixa amb Inici i Final")
        nHorSeleccionat = getNumFromText(build_ele, build_ele.SelectorTubHor.value, 3)
        detectar_tipus_tub(build_ele, DocumentManager, j, nHorSeleccionat, encaixAmbTubInf,encaixAmbTubSup)

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
    build_ele.provSupEsq.value = build_ele.dadesTubHor.value[j].provSupEsq
    build_ele.provSupDre.value = build_ele.dadesTubHor.value[j].provSupDre
    build_ele.provInfEsq.value = build_ele.dadesTubHor.value[j].provInfEsq
    build_ele.provInfDre.value = build_ele.dadesTubHor.value[j].provInfDre
    build_ele.provInfCen.value = build_ele.dadesTubHor.value[j].provInfCen
    build_ele.TipusLinia.value = build_ele.dadesTubHor.value[j].linia
    build_ele.RotarTub.value = build_ele.dadesTubHor.value[j].RotarTub
    build_ele.RotarTubAnt.value = build_ele.dadesTubHor.value[j].RotarTub
    build_ele.tipusTubAuto.value = build_ele.dadesTubHor.value[j].tipusTubAuto
    build_ele.SelectorTubInferior.value = build_ele.dadesTubHor.value[j].tubInferior
    build_ele.SelectorTubSuperior.value = build_ele.dadesTubHor.value[j].tubSuperior
    build_ele.SelectorTubInferiorHor.value = build_ele.dadesTubHor.value[j].tubInferior
    build_ele.SelectorTubSuperiorHor.value = build_ele.dadesTubHor.value[j].tubSuperior
    build_ele.posAutomatica.value = build_ele.dadesTubHor.value[j].posAutomatica
    build_ele.retallInicial.value = build_ele.dadesTubHor.value[j].retallInicial
    if build_ele.dadesTubHor.value[j].retallFinal <= 0:
        build_ele.retallFinal.value = 0
    else:
        build_ele.retallFinal.value = build_ele.dadesTubHor.value[j].retallFinal

    build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallFinal = build_ele.retallFinal.value)



def set_values_tub_hor(build_ele, j, actual):
    #print("set_values_tub_hor")

    #DADES TDV UNIQUES
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'Mostrar Ample Altura LlargadaAut Llargada Gruix '+
                                                   'desplX desplY ' +
                                                   'mostrarLiniaA desplLinA mostrarLiniaB desplLinB ' +
                                                   'IsUseGlobalProp FounColor BarraLayer '
                                                   'Ample_forat_femella Altura_forat_femella Separacio_forat_femella '+
                                                   'PestanyaSuperior PestanyaInferior PestanyesInv '+
                                                   'esProvisional '+
                                                   'provSupEsq provSupDre provInfEsq provInfDre provInfCen '+
                                                   'linia layer TipusTub RotarTub tipusTubAuto '+
                                                   'tubInferior tubSuperior posAutomatica ' +
                                                   'retallInicial retallFinal')
    bobDadesGlobal = TDCollectionDadesVert(Mostrar = True,
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
                                            provSupEsq = True,
                                            provSupDre = True,
                                            provInfEsq = True,
                                            provInfDre = True,
                                            provInfCen = False,
                                            linia = "Tipus 1",
                                            layer = "EN_ESTRUCTURA",
                                            TipusTub = "TUB E",
                                            RotarTub = False,
                                            tipusTubAuto = True,
                                            tubInferior = "Tub 0",
                                            tubSuperior = "Tub 1",
                                            posAutomatica = True,
                                            retallInicial = 0,
                                            retallFinal = 0
                                            )

    extremsVert = 0
    interiorsVert = 0
    posinteriorVert = 650
    tubinf = "Tub 0"
    tubsup = "Tub 1"
    tubsupExt = "Tub 1"
    exteriorEsq = 4
    exteriorDre = 5
    build_ele.ExteriorEsquerra.value = 4
    build_ele.ExteriorDreta.value = 5


    while len(build_ele.dadesTubHor.value) <= j:
        if len(build_ele.dadesTubHor.value) != 0:
            if len(build_ele.dadesTubHor.value) * 700 < build_ele.ISAmplada.value:
                bobDadesGlobal = bobDadesGlobal._replace(desplY = len(build_ele.dadesTubHor.value) * 700 )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
                bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
                bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))
                bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = True)
                tubsupExt = "Tub "+str(len(build_ele.dadesTubHor.value))

                #elif len(build_ele.dadesTubHor.value) * 700 == build_ele.ISAmplada.value:
            elif len(build_ele.dadesTubHor.value) * 700 > build_ele.ISAmplada.value and (len(build_ele.dadesTubHor.value)-1) * 700 < build_ele.ISAmplada.value-50:
                bobDadesGlobal = bobDadesGlobal._replace(desplY = build_ele.ISAmplada.value -50 )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
                bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
                bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))
                bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                tubsupExt = "Tub "+str(len(build_ele.dadesTubHor.value))
            else:
                bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                bobDadesGlobal = bobDadesGlobal._replace(retallInicial = 0)
                bobDadesGlobal = bobDadesGlobal._replace(retallFinal = 0)
                if extremsVert <= 1:
                    bobDadesGlobal = bobDadesGlobal._replace(TipusTub = "TUB A" )
                    bobDadesGlobal = bobDadesGlobal._replace(RotarTub = True)
                    bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub 0")
                    bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = tubsupExt)
                    bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = False)
                    bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISAmplada.value)
                    bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                    if actual == len(build_ele.dadesTubHor.value)-1:
                        build_ele.BarraLlargada.value = build_ele.ISAmplada.value
                    bobDadesGlobal = bobDadesGlobal._replace(desplY = 0)
                    if extremsVert == 1:
                        bobDadesGlobal = bobDadesGlobal._replace(desplX = build_ele.ISllargada.value-50)
                        bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = False)
                        exteriorEsq = len(build_ele.dadesTubHor.value)-1
                        exteriorDre = len(build_ele.dadesTubHor.value)
                        build_ele.ExteriorEsquerra.value = len(build_ele.dadesTubHor.value)-1
                        build_ele.ExteriorDreta.value = len(build_ele.dadesTubHor.value)
                    extremsVert += 1
                else:
                    bobDadesGlobal = bobDadesGlobal._replace(TipusTub = "TUB B" )
                    bobDadesGlobal = bobDadesGlobal._replace(RotarTub = True)
                    bobDadesGlobal = bobDadesGlobal._replace(tubInferior = tubinf)
                    bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = tubsup)
                    bobDadesGlobal = bobDadesGlobal._replace(desplX = posinteriorVert)
                    bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
                    bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = True)

                    if posinteriorVert + 700 < build_ele.ISllargada.value-100:
                        posinteriorVert += 700
                    else:
                        posinteriorVert = 650

                        tubinf = "Tub " + str(getNumFromText(build_ele, tubinf, 3)+1 )
                        tubsup = "Tub " + str(getNumFromText(build_ele, tubsup, 3)+1 )
        else:
            bobDadesGlobal = bobDadesGlobal._replace(desplY = len(build_ele.dadesTubHor.value) * 700 )#+ build_ele.dadesTubHor.value[0].Ample)
            bobDadesGlobal = bobDadesGlobal._replace(Llargada = build_ele.ISllargada.value )#+ build_ele.dadesTubHor.value[0].Ample)
            bobDadesGlobal = bobDadesGlobal._replace(posAutomatica = True)
            bobDadesGlobal = bobDadesGlobal._replace(LlargadaAut = True)
            bobDadesGlobal = bobDadesGlobal._replace(tubInferior = "Tub "+str(exteriorEsq))
            bobDadesGlobal = bobDadesGlobal._replace(tubSuperior = "Tub "+str(exteriorDre))
            bobDadesGlobal = bobDadesGlobal._replace(desplX = 0)
            bobDadesGlobal = bobDadesGlobal._replace(RotarTub = False)
            if actual == 0:
                build_ele.RotarTub.value = False
                build_ele.SelectorTubInferiorHor.value = "Tub "+str(exteriorEsq)
                build_ele.SelectorTubSuperiorHor.value = "Tub "+str(exteriorDre)#SelectorTubSuperiorHor
                build_ele.retallInicial.value = 0
                build_ele.retallFinal.value = 0#SelectorTubSuperiorHor
        build_ele.dadesTubHor.value.append(bobDadesGlobal)


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
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provSupEsq = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provSupDre = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfEsq = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfDre = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(provInfCen = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(linia = "Tipus 1")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(layer = "EN_ESTRUCTURA")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(TipusTub = "TUB E")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tipusTubAuto = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(RotarTub = False)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubInferior = "Tub 0")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(tubSuperior = "Tub 1")
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(posAutomatica = True)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallInicial = 0)
        build_ele.dadesTubHor.value[j] = build_ele.dadesTubHor.value[j]._replace(retallFinal = 0)

    #fer nomes quan es fa recalcul
    if build_ele.refactor.value:
        for x in range(0, len(build_ele.dadesTubHor.value)):
            if not build_ele.dadesTubHor.value[x].RotarTub:
                if x == actual:
                    build_ele.posAutomatica.value = True
                    build_ele.llargadaAutomatica.value = True
                    build_ele.SelectorTubInferiorHor.value = "Tub "+str(exteriorEsq)
                    build_ele.SelectorTubSuperiorHor.value = "Tub "+str(exteriorDre)#SelectorTubSuperiorHor
                else:
                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(posAutomatica = True)
                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(LlargadaAut = True)
                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubInferior = "Tub "+str(exteriorEsq))
                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubSuperior = "Tub "+str(exteriorDre))
            else:
                if build_ele.dadesTubHor.value[x].tubSuperior == "Tub 0":
                    if x == actual:
                        build_ele.MostrarTub.value = False
                    else:
                        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

    build_ele.refactor.value = False

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

    for x in range(i*18, len(build_ele.dadesTubHor.value)):
        build_ele.dadesTubHor.value.pop()

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

def recalcul_n_barres(build_ele):
    nbarres = 30

    tubsHoritzontals = int(math.floor((build_ele.ISAmplada.value)/700) + 2)
    tubsHoritzontals = int((build_ele.ISAmplada.value - 100)/700) + 1
    tubsVerticals = int(math.floor((build_ele.ISllargada.value)/700) )
    tubsVerticals = int((build_ele.ISllargada.value - 100)/700 )

    #print("#####################################################################")
    #print("tubsHoritzontals: "+str(tubsHoritzontals))
    #print("tubsVerticals: "+str(tubsVerticals))

    tubsINteriorsVerticals = math.floor(tubsVerticals*tubsHoritzontals)#interiors
    nbarres = tubsINteriorsVerticals + tubsHoritzontals + 3 #4 exteriors

    #print("nbarres: "+str(nbarres))
    #print("#####################################################################")

    return nbarres

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

def getLetterFromText(build_ele, Text, nMax):
    num = ""
    if len(Text) > nMax:
        if len(Text) == nMax+4:
           Centenes = Text[-3]
           Decenes = Text[-2]
           Unitats = Text[-1]
           num = Centenes + Decenes + Unitats
        elif len(Text) == nMax+3:
            Decenes = Text[-2]
            Unitats = Text[-1]
            num = Decenes + Unitats
        elif len(Text) == nMax+2:
            num = Text[-1]
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
    posInf = 50
    if not build_ele.dadesTubHor.value[nTubInf].posAutomatica:
        posInf -= 50
    if build_ele.dadesTubHor.value[posBarraHor].RotarTub: # build_ele.dadesTubHor.value[posBarraHor].LlargadaAut
        if build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            return build_ele.dadesTubHor.value[posBarraHor].desplX  + build_ele.dadesTubHor.value[nTubInf].Altura
        else:
            return build_ele.dadesTubHor.value[posBarraHor].desplX
    else:
        if build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            return build_ele.dadesTubHor.value[nTubInf].desplX  + build_ele.dadesTubHor.value[posBarraHor].desplX + posInf
        else:
            return build_ele.dadesTubHor.value[posBarraHor].desplX + posInf

def get_posicioY(build_ele, posBarraHor):
    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
    if build_ele.dadesTubHor.value[posBarraHor].RotarTub and build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
        return build_ele.dadesTubHor.value[nTubInf].desplY + build_ele.dadesTubHor.value[nTubInf].Altura
    return build_ele.dadesTubHor.value[posBarraHor].desplY

def set_llargadaAut(build_ele, posBarraHor, esVertical):
    if esVertical:
        nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
        posInf = build_ele.dadesTubHor.value[posBarraHor].desplY
        if build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            posInf += build_ele.dadesTubHor.value[nTubInf].desplY + build_ele.dadesTubHor.value[nTubInf].Altura
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplY
    else:
        posInf = build_ele.dadesTubHor.value[posBarraHor].desplX
        if build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
            posInf = build_ele.dadesTubHor.value[nTubInf].desplX + build_ele.dadesTubHor.value[nTubInf].Altura + build_ele.dadesTubHor.value[posBarraHor].desplX
            if not build_ele.dadesTubHor.value[nTubInf].posAutomatica:
                posInf -= 50
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplX
        if not build_ele.dadesTubHor.value[nTubSup].posAutomatica and build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            posSup -= 50
    if posSup-posInf > 0:
        build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace (Llargada = posSup - posInf)
    else:
        build_ele.dadesTubHor.value[posBarraHor] = build_ele.dadesTubHor.value[posBarraHor]._replace (Llargada = 50)
    return build_ele.dadesTubHor.value[posBarraHor].Llargada

def get_llargadaAut(build_ele, posBarraHor, esVertical):
    if esVertical:
        nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
        posInf = build_ele.dadesTubHor.value[posBarraHor].desplY
        if build_ele.dadesTubHor.value[posBarraHor].posAutomatica:
            posInf += build_ele.dadesTubHor.value[nTubInf].desplY + build_ele.dadesTubHor.value[nTubInf].Altura
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplY
    else:
        nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubInferior, 3)
        posInf = build_ele.dadesTubHor.value[nTubInf].desplX + build_ele.dadesTubHor.value[nTubInf].Altura
        #if not build_ele.dadesTubHor.value[nTubInf].posAutomatica:
        #    posInf -= 50
        nTubSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[posBarraHor].tubSuperior, 3)
        posSup = build_ele.dadesTubHor.value[nTubSup].desplX
        #if not build_ele.dadesTubHor.value[nTubSup].posAutomatica:
        #    posSup -= 50
    if build_ele.dadesTubHor.value[posBarraHor].posAutomatica and build_ele.dadesTubHor.value[posBarraHor].LlargadaAut:
        if posSup-posInf > 0:
            return (posSup-posInf) - build_ele.dadesTubHor.value[posBarraHor].retallInicial
        else:
            return build_ele.dadesTubHor.value[posBarraHor].Llargada
    else:
        return build_ele.dadesTubHor.value[posBarraHor].Llargada - build_ele.dadesTubHor.value[posBarraHor].retallInicial




def crear_creu_auto(build_ele, doc, nHorSeleccionat):
    costats = ["Esq", "Dre", "Inf", "Sup" ]
    nCreats = 0
    llistaTubs = {
        #"Esq" : None,
        #"Dre" : None,
        #"Inf" : None,
        #"Sup" : None
    }
    if build_ele.crearCreuSenseTubsExteriors.value:# NO Crear barres quadrat
        costats = []
        nCreats =  0
        ''' PROV'''
        '''
        llistaTubs["Esq"] = detectar_vertical_anterior(build_ele, -1, nHorSeleccionat,\
            posX = build_ele.PosicioXlinia.value + 51, \
            posY = build_ele.PosicioYlinia.value +  build_ele.Llargadalinia.value / 2)
        if llistaTubs["Esq"] != None:
            if build_ele.dadesTubHor.value[llistaTubs["Esq"]].desplX < build_ele.PosicioXlinia.value - 61:
                costats.append("Esq")
        llistaTubs["Dre"] = detectar_vertical_seguent(build_ele, -1, nHorSeleccionat, \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2 - 51, \
            posY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value / 2)
        if llistaTubs["Dre"] != None:
            if build_ele.dadesTubHor.value[llistaTubs["Dre"]].desplX > build_ele.PosicioXlinia.value + build_ele.Amplelinia.value + 61:
                costats.append("Dre")
        llistaTubs["Inf"] = detectar_horitzontal_anterior(build_ele, -1, nHorSeleccionat,  \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2 , \
            posY = build_ele.PosicioYlinia.value + 51)
        if llistaTubs["Inf"] != None:
            if build_ele.dadesTubHor.value[llistaTubs["Inf"]].desplY < build_ele.PosicioYlinia.value - 61:
                costats.append("Inf")
        llistaTubs["Sup"] = detectar_horitzontal_seguent(build_ele, -1, nHorSeleccionat, \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2, \
            posY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value  - 51)
        if llistaTubs["Sup"] != None:
            if build_ele.dadesTubHor.value[llistaTubs["Sup"]].desplY > build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value + 61:
                costats.append("Sup")

        print("------costats: " + str(costats))
        nCreats, llistaTubs2 = crear_barres_quadrat(build_ele, doc, nHorSeleccionat, costats)
        for cost in llistaTubs:
            if llistaTubs2[cost] != None:
                llistaTubs[cost] = llistaTubs2[cost]

        detectar_colisio_tubs(build_ele, doc, nHorSeleccionat, nCreats, llistaTubs)
        ocultar_interiors(build_ele, nHorSeleccionat, llistaExteriorsForat = llistaTubs)
        '''
        llistaTubs["Esq"] = detectar_vertical_anterior(build_ele, -1, nHorSeleccionat,\
            posX = build_ele.PosicioXlinia.value + 51, \
            posY = build_ele.PosicioYlinia.value +  build_ele.Llargadalinia.value / 2)
        llistaTubs["Dre"] = detectar_vertical_seguent(build_ele, -1, nHorSeleccionat, \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2 - 51, \
            posY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value / 2)
        llistaTubs["Inf"] = detectar_horitzontal_anterior(build_ele, -1, nHorSeleccionat,  \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2 , \
            posY = build_ele.PosicioYlinia.value + 51)
        llistaTubs["Sup"] = detectar_horitzontal_seguent(build_ele, -1, nHorSeleccionat, \
            posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value / 2, \
            posY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value  - 51)

        ocultar_interiors(build_ele, nHorSeleccionat, llistaExteriorsForat = llistaTubs)

    else: # Crear barres quadrat
        #print("Crear barres quadrat")
        nCreats, llistaTubs = crear_barres_quadrat(build_ele, doc, nHorSeleccionat, costats)
        if llistaTubs["Esq"] == build_ele.ExteriorEsquerra.value and llistaTubs["Inf"] == 0:
            build_ele.dadesTubHor.value[llistaTubs["Dre"]] = build_ele.dadesTubHor.value[llistaTubs["Dre"]]._replace(Llargada = build_ele.dadesTubHor.value[llistaTubs["Dre"]].Llargada -50)
        if llistaTubs["Dre"] == build_ele.ExteriorDreta.value and llistaTubs["Inf"] == 0:
            build_ele.dadesTubHor.value[llistaTubs["Esq"]] = build_ele.dadesTubHor.value[llistaTubs["Esq"]]._replace(Llargada = build_ele.dadesTubHor.value[llistaTubs["Esq"]].Llargada -50)

        detectar_colisio_tubs(build_ele, doc, nHorSeleccionat, nCreats, llistaTubs)


    crear_barra_Horitzontal(build_ele, nHorSeleccionat, build_ele.PosicioXlinia.value, build_ele.PosicioXlinia.value  + build_ele.Amplelinia.value - 100, build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value/2 - 25, "D")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(esProvisional = True )
    if llistaTubs["Esq"] != None:
        asignar_barra_inferior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Esq"])
    if llistaTubs["Dre"] != None:
        asignar_barra_superior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Dre"])

    crear_barra_Vertical(build_ele, nHorSeleccionat, build_ele.PosicioYlinia.value + 50 , build_ele.PosicioYlinia.value  + build_ele.Llargadalinia.value/2 - 25, build_ele.PosicioXlinia.value + build_ele.Amplelinia.value/2 - 75, "C")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(esProvisional = True )
    if llistaTubs["Inf"] != None:
        asignar_barra_inferior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Inf"])
    asignar_barra_superior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, build_ele.IntegerISSelectorHor.value-2)

    crear_barra_Vertical(build_ele, nHorSeleccionat, build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value/2 +25, build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value -50, build_ele.PosicioXlinia.value + build_ele.Amplelinia.value/2 -75, "C")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(esProvisional = True )
    asignar_barra_inferior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, build_ele.IntegerISSelectorHor.value-3)
    if llistaTubs["Sup"] != None:
        asignar_barra_superior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Sup"])



def crear_forat_auto(build_ele, doc, nHorSeleccionat, tipusForat):

    lenDadesTubHorAct = build_ele.IntegerISSelectorHor.value
    costats = []
    if build_ele.PosicioXlinia.value <= 0: #forat esquerra
        costats.append("Esq")

    if build_ele.PosicioYlinia.value <= 0: #forat abaix
        costats.append("Inf")

    if build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  >= build_ele.ISllargada.value : # forat dreta
        costats.append("Dre")

    if build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value >= build_ele.ISAmplada.value: #forat adalt
        costats.append("Sup")


    if tipusForat == 3:
        nCreats, llistaTubs = crear_barres_quadrat3(build_ele, doc, nHorSeleccionat, costats)
    elif tipusForat == 2:
        nCreats, llistaTubs = crear_barres_quadrat2(build_ele, doc, nHorSeleccionat, costats)
    else:
        nCreats, llistaTubs = crear_barres_quadrat(build_ele, doc, nHorSeleccionat, costats)

    detectar_colisio_tubs(build_ele, doc, nHorSeleccionat, nCreats, llistaTubs)

def detectar_tub_sobre_tub(build_ele, posTubNou, nHorSeleccionat ):

    tubNou = build_ele.dadesTubHor.value[posTubNou]
    for nTub in range(0, build_ele.IntegerISSelectorHor.value):
        tubExistent = build_ele.dadesTubHor.value[nTub]
        if nTub != posTubNou:
            if tubNou.RotarTub: #Vertical
                if tubNou.RotarTub == tubExistent.RotarTub and \
                    tubNou.desplX == tubExistent.desplX and \
                    tubNou.desplY >= tubExistent.desplY and \
                    tubNou.Llargada <= tubExistent.Llargada and \
                    tubNou.desplY + tubNou.Llargada - tubNou.retallInicial - tubNou.retallFinal <= \
                    tubExistent.desplY + tubExistent.Llargada - tubExistent.retallInicial - tubExistent.retallFinal :
                    return True, nTub
            else:#Horitzontal
                if tubNou.RotarTub == tubExistent.RotarTub and \
                    tubNou.desplX >= tubExistent.desplX and \
                    tubNou.desplY == tubExistent.desplY and \
                    tubNou.Llargada <= tubExistent.Llargada and \
                    tubNou.desplY + tubNou.Llargada - tubNou.retallInicial - tubNou.retallFinal <= \
                    tubExistent.desplY + tubExistent.Llargada - tubExistent.retallInicial - tubExistent.retallFinal :
                        return True, nTub
    return False, posTubNou

def crear_barres_quadrat(build_ele, doc, nHorSeleccionat, costats):
    posicionsNousTubs = {
        "Esq" : None,
        "Dre" : None,
        "Sup" : None,
        "Inf" : None,
    }

    nTubsquadrat = 0
    if len(costats) == 0:
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 4
        print("crear 4")
    if len(costats) == 1:
        if "Esq" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats,posAutomatica=False, llargadaAutomatica= False)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Sup"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Sup"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplX)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplX)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
        elif "Inf" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        elif "Dre" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica = True)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica = True)
        elif "Sup" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 3
        print("crear 3")
    elif len(costats) == 2:
        if "Esq" in costats and "Dre" in costats:
            print("2 Hor")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tipus=3)
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tipus=3)
        elif "Sup" in costats and "Inf" in costats:
            print("2 Vert")
            #posicionsNousTubs["Sup"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats)#, tipus=3)
            #posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats)#, tipus=3)
        elif "Esq" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tipus=2)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], llargadaAutomatica=True)
        elif "Esq" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, tipus=2)
            build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(desplY = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplY + 50)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica=False)
        elif "Dre" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, tipus=1)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica=True, llargadaAutomatica=False)
        elif "Dre" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"])#, posAutomatica=True, llargadaAutomatica=True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]].Llargada - 50)

        nTubsquadrat = 2
        print("crear 2")
    elif len(costats) == 3:
        if "Esq" in costats and "Dre" in costats and "Inf" in costats:
            print("1 Hor")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_inf(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
        elif "Esq" in costats and "Dre" in costats and "Sup" in costats:
            print("1 Hor")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_sup(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
        elif "Esq" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        elif "Dre" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
        nTubsquadrat = 1
        print("crear 1")
    elif len(costats) == 4:
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)#, tipus=2)
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 4
        print("crear 4")

    tubsTrobatsSobreposats = []
    for NouTub in posicionsNousTubs: #.values():
        if posicionsNousTubs[NouTub] != None:
            posNouTub = posicionsNousTubs[NouTub]
            trobat, posicio = detectar_tub_sobre_tub(build_ele, posNouTub, nHorSeleccionat )
            if trobat :
                tubsTrobatsSobreposats.append(NouTub)
                #if NouTub != "Esq" and NouTub != "Dre":
                #if posicio != build_ele.ExteriorEsquerra.value and posicio != build_ele.ExteriorDreta.value:
                build_ele.dadesTubHor.value[posNouTub] = build_ele.dadesTubHor.value[posNouTub]._replace(Mostrar = False)
                posicionsNousTubs[NouTub] = posicio # type: ignore

    for tub in tubsTrobatsSobreposats:
        posTubEsq = posicionsNousTubs["Esq"]
        posTubDre = posicionsNousTubs["Dre"]
        posTubInf = posicionsNousTubs["Inf"]
        posTubSup = posicionsNousTubs["Sup"]
        if tub == "Sup" :
            if posicionsNousTubs["Esq"] != None and posTubEsq != build_ele.ExteriorEsquerra.value:
                build_ele.dadesTubHor.value[posTubEsq] = build_ele.dadesTubHor.value[posTubEsq]._replace(LlargadaAut = True)
                asignar_barra_superior(build_ele, posTubEsq, nHorSeleccionat, posTubSup)
            if posicionsNousTubs["Dre"] != None and posTubDre != build_ele.ExteriorDreta.value:
                build_ele.dadesTubHor.value[posTubDre] = build_ele.dadesTubHor.value[posTubDre]._replace(LlargadaAut = True)
                asignar_barra_superior(build_ele, posTubDre, nHorSeleccionat, posTubSup)

        elif tub == "Inf":
            if posicionsNousTubs["Esq"] != None and posTubEsq != build_ele.ExteriorEsquerra.value:
                if not build_ele.dadesTubHor.value[posTubEsq].posAutomatica:
                    build_ele.dadesTubHor.value[posTubEsq] = build_ele.dadesTubHor.value[posTubEsq]._replace(posAutomatica = True)
                    build_ele.dadesTubHor.value[posTubEsq] = build_ele.dadesTubHor.value[posTubEsq]._replace(desplX = build_ele.dadesTubHor.value[posTubEsq].desplX - 50)
                asignar_barra_inferior(build_ele, posTubEsq, nHorSeleccionat, posTubInf)
            if posicionsNousTubs["Dre"] != None and posTubDre != build_ele.ExteriorDreta.value:
                if not build_ele.dadesTubHor.value[posTubDre].posAutomatica:
                    build_ele.dadesTubHor.value[posTubDre] = build_ele.dadesTubHor.value[posTubDre]._replace(posAutomatica = True)
                    build_ele.dadesTubHor.value[posTubDre] = build_ele.dadesTubHor.value[posTubDre]._replace(desplX = build_ele.dadesTubHor.value[posTubDre].desplX - 50)
                asignar_barra_inferior(build_ele, posTubDre, nHorSeleccionat, posTubInf)
            if not "Sup" in tubsTrobatsSobreposats :
                if posTubEsq != build_ele.ExteriorEsquerra.value and posTubDre == build_ele.ExteriorDreta.value and build_ele.PosicioYlinia.value  > 0:
                    build_ele.dadesTubHor.value[posTubEsq] = build_ele.dadesTubHor.value[posTubEsq]._replace(Llargada = build_ele.dadesTubHor.value[posTubEsq].Llargada - 50)
                if posTubDre != build_ele.ExteriorDreta.value and posTubEsq == build_ele.ExteriorEsquerra.value and build_ele.PosicioYlinia.value > 0:
                    build_ele.dadesTubHor.value[posTubDre] = build_ele.dadesTubHor.value[posTubDre]._replace(Llargada = build_ele.dadesTubHor.value[posTubDre].Llargada - 50)


    llistatnouValors = get_valors_posicionsNousTubs(build_ele, posicionsNousTubs)
    detectar_conjunt_tipus_tub(build_ele, doc, nHorSeleccionat, llistatnouValors)

    #assignar_infSup_corresponents(build_ele, nHorSeleccionat)

    return nTubsquadrat , posicionsNousTubs

def crear_barres_quadrat2(build_ele, doc, nHorSeleccionat, costats):
    posicionsNousTubs = {
        "Esq" : None,
        "Dre" : None,
        "Sup" : None,
        "Inf" : None,
    }
    nTubsquadrat = 4
    if len(costats) == 0:
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], tubSup = posicionsNousTubs["Sup"], posAutomatica = True, llargadaAutomatica = True, tipus=2)
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], tubSup = posicionsNousTubs["Sup"], posAutomatica = True, llargadaAutomatica = True, tipus=2)
        nTubsquadrat = 4
        print("crear 4")
    if len(costats) == 1:
        if "Esq" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], tubSup = posicionsNousTubs["Sup"], posAutomatica = True, llargadaAutomatica = True)
        elif "Inf" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Sup"], posAutomatica = False, llargadaAutomatica = False, tipus = 2)
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Sup"], posAutomatica = False, llargadaAutomatica = False, tipus = 2)
        elif "Dre" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], tubSup = posicionsNousTubs["Sup"], posAutomatica = True, llargadaAutomatica = True)
        elif "Sup" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, posAutomatica= True, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], posAutomatica = True, llargadaAutomatica = False, tipus = 2)
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Inf"], posAutomatica = True, llargadaAutomatica = False, tipus = 2)
        nTubsquadrat = 3
        print("crear 3")
    elif len(costats) == 2:
        if "Esq" in costats and "Dre" in costats:
            print("2 Hor")
        elif "Sup" in costats and "Inf" in costats:
            print("2 Vert")
        elif "Esq" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, llargadaAutomatica=True)#, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Sup"], posAutomatica = False, llargadaAutomatica = False, tipus=2)
        elif "Esq" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, llargadaAutomatica=True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubInf=posicionsNousTubs["Inf"], posAutomatica=True, llargadaAutomatica=False, tipus = 2)
        elif "Dre" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubSup=posicionsNousTubs["Sup"], posAutomatica=False, llargadaAutomatica=False, tipus=2)
        elif "Dre" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, tubInf=posicionsNousTubs["Inf"], tipus=2)
        nTubsquadrat = 2
        print("crear 2")
    elif len(costats) == 3:
        if "Esq" in costats and "Dre" in costats and "Inf" in costats:
            print("1 Hor")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_inf(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
        elif "Esq" in costats and "Dre" in costats and "Sup" in costats:
            print("1 Hor")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_sup(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
        elif "Esq" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        elif "Dre" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
        print("crear 1")
        nTubsquadrat = 1
    elif len(costats) == 4:
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 4
        print("crear 4")

    llistatnouValors = get_valors_posicionsNousTubs(build_ele, posicionsNousTubs)
    detectar_conjunt_tipus_tub(build_ele, doc, nHorSeleccionat, llistatnouValors)
    return nTubsquadrat , posicionsNousTubs

def crear_barres_quadrat3(build_ele, doc, nHorSeleccionat, costats):
    posicionsNousTubs = {
        "Esq" : None,
        "Dre" : None,
        "Sup" : None,
        "Inf" : None,
    }
    nTubsquadrat = 0
    if len(costats) == 0:
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
        posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
        posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 4
        print("crear 4")
    elif len(costats) == 1:
        if "Esq" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats,posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica = True)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica = True)
        elif "Inf" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        elif "Dre" in costats:
            print("2 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica = True)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica = True)
        elif "Sup" in costats:
            print("1 Hor 2 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
            llargadaAct = get_llargadaAut(build_ele, posicionsNousTubs["Dre"], True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(LlargadaAut = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(Llargada =  llargadaAct + 50)
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
            llargadaAct = get_llargadaAut(build_ele, posicionsNousTubs["Esq"], True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]]._replace(LlargadaAut = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]]._replace(Llargada =  llargadaAct + 50)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 3
        print("crear 3")
    elif len(costats) == 2:
        if "Esq" in costats and "Dre" in costats:
            print("2 Hor")
        elif "Sup" in costats and "Inf" in costats:
            print("2 Vert")
        elif "Esq" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats,llargadaAutomatica=True, tipus=2)
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], llargadaAutomatica=False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Sup"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Sup"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplX)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
        elif "Esq" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True,llargadaAutomatica=True, tipus=2)
            #build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(desplY = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplY + 50)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
            llargadaAct = get_llargadaAut(build_ele, posicionsNousTubs["Dre"], True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(LlargadaAut = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]]._replace(Llargada = llargadaAct + 50)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubSup = posicionsNousTubs["Dre"], posAutomatica=False, llargadaAutomatica=False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Dre"]].desplX +50)
        elif "Dre" in costats and "Inf" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=False, llargadaAutomatica=True, tipus=1)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"], posAutomatica=True, llargadaAutomatica=False)
        elif "Dre" in costats and "Sup" in costats:
            print("1 Hor 1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, posAutomatica=True, llargadaAutomatica=True)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
            llargadaAct = get_llargadaAut(build_ele, posicionsNousTubs["Esq"], True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]]._replace(LlargadaAut = False)
            build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Esq"]]._replace(Llargada = llargadaAct + 50)
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"])#, posAutomatica=True, llargadaAutomatica=True)
            build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]] = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]]._replace(Llargada = build_ele.dadesTubHor.value[posicionsNousTubs["Inf"]].Llargada - 50)
        nTubsquadrat = 2
        print("crear 2")
    elif len(costats) == 3:
        if "Esq" in costats and "Dre" in costats and "Inf" in costats:
            print("1 Hor")
            posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_inf(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Sup"])
        elif "Esq" in costats and "Dre" in costats and "Sup" in costats:
            print("1 Hor")
            posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats)
            ocultar_horitzontals_sup(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Inf"])
        elif "Esq" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Dre"])
        elif "Dre" in costats and "Inf" in costats and "Sup" in costats:
            print("1 Vert")
            posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
            posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, posicionsNousTubs["Esq"])
        nTubsquadrat = 1
        print("crear 1")
    elif len(costats) == 4:
        posicionsNousTubs["Dre"] = crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Esq"] = crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats)
        posicionsNousTubs["Sup"] = crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        posicionsNousTubs["Inf"] = crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = posicionsNousTubs["Esq"] , tubSup = posicionsNousTubs["Dre"], posAutomatica = True, llargadaAutomatica = True)
        nTubsquadrat = 4
        print("crear 4")
    llistatnouValors = get_valors_posicionsNousTubs(build_ele, posicionsNousTubs)
    detectar_conjunt_tipus_tub(build_ele, doc, nHorSeleccionat, llistatnouValors)
    return nTubsquadrat , posicionsNousTubs

def get_valors_posicionsNousTubs(build_ele, posicionsNousTubs):
    llistatnouValors = []
    if posicionsNousTubs["Esq"] != None:
        llistatnouValors.append(posicionsNousTubs["Esq"])
    if posicionsNousTubs["Dre"] != None:
        llistatnouValors.append(posicionsNousTubs["Dre"])
    if posicionsNousTubs["Inf"] != None:
        llistatnouValors.append(posicionsNousTubs["Inf"])
    if posicionsNousTubs["Sup"] != None:
        llistatnouValors.append(posicionsNousTubs["Sup"])
    return llistatnouValors

def ocultar_horitzontals_sup(build_ele, doc, nHorSeleccionat, tubSup):
    for x in range(0, build_ele.IntegerISSelectorHor.value):
        if not build_ele.dadesTubHor.value[x].RotarTub and (build_ele.dadesTubHor.value[tubSup].desplY < build_ele.dadesTubHor.value[x].desplY):
            if x == nHorSeleccionat:
                build_ele.MostrarTub.value = False
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

def ocultar_horitzontals_inf(build_ele, doc, nHorSeleccionat, tubInf):
    for x in range(0, build_ele.IntegerISSelectorHor.value):
        if not build_ele.dadesTubHor.value[x].RotarTub and (build_ele.dadesTubHor.value[tubInf].desplY > build_ele.dadesTubHor.value[x].desplY):
            if x == nHorSeleccionat:
                build_ele.MostrarTub.value = False
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

def posicio_llarga_barra_horitzontal(build_ele, doc, nHorSeleccionat, noutub):
    '''
    detectar Vertical anterior per Sup i Inf #es crida cada vegada que es crea un tub Hor Sup o Inf
    '''
    verticalMesProper = detectar_vertical_anterior(build_ele, noutub, nHorSeleccionat)
    verticalMesProperDre = detectar_vertical_seguent(build_ele, noutub, nHorSeleccionat)
    if verticalMesProper != None and build_ele.dadesTubHor.value[noutub].posAutomatica:
        asignar_barra_inferior(build_ele, noutub, nHorSeleccionat, verticalMesProper)
    if verticalMesProperDre != None and build_ele.dadesTubHor.value[noutub].LlargadaAut:
        asignar_barra_superior(build_ele, noutub, nHorSeleccionat, verticalMesProperDre)

def posicio_llarga_barra_vertical(build_ele, doc, nHorSeleccionat, noutub):
    '''
    detectar Horitzontal anterior per Sup i Inf #es crida cada vegada que es crea un tub Vertical Sup o Inf
    '''
    verticalMesProper = detectar_horitzontal_anterior(build_ele, noutub, nHorSeleccionat)
    verticalMesProperDre = detectar_horitzontal_seguent(build_ele, noutub, nHorSeleccionat)
    if verticalMesProper != None and build_ele.dadesTubHor.value[noutub].posAutomatica:
        asignar_barra_inferior(build_ele, noutub, nHorSeleccionat, verticalMesProper)
    if verticalMesProperDre != None and build_ele.dadesTubHor.value[noutub].LlargadaAut:
        asignar_barra_superior(build_ele, noutub, nHorSeleccionat, verticalMesProperDre)

def get_posicions_tubsexteriors(build_ele, x):
    posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX
    posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX + build_ele.dadesTubHor.value[x].Llargada

    posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
    posVerticalSup = build_ele.dadesTubHor.value[x].desplY + build_ele.dadesTubHor.value[x].Llargada


    #obtenirPosicionsIniciiFinal
    if not build_ele.dadesTubHor.value[x].posAutomatica and not build_ele.dadesTubHor.value[x].LlargadaAut:
        if not build_ele.dadesTubHor.value[x].RotarTub:#Tub Horitzontal
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX
            posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX + build_ele.dadesTubHor.value[x].Llargada
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = build_ele.dadesTubHor.value[x].desplY #+ build_ele.dadesTubHor.value[x].Llargada
        else:
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX
            posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3 ))
    elif not build_ele.dadesTubHor.value[x].posAutomatica and build_ele.dadesTubHor.value[x].LlargadaAut:
        if not build_ele.dadesTubHor.value[x].RotarTub:#Tub Horitzontal
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX
            posHoritzontalDre = get_posicioX(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3 ))
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = build_ele.dadesTubHor.value[x].desplY
        else:
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX
            posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3 ))
    elif  build_ele.dadesTubHor.value[x].posAutomatica and not build_ele.dadesTubHor.value[x].LlargadaAut:
        if not build_ele.dadesTubHor.value[x].RotarTub:#Tub Horitzontal
            posHoritzontalEsq = posHoritzontal = get_posicioX(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 ))
            posHoritzontalDre = get_posicioX(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 )) + build_ele.dadesTubHor.value[x].Llargada
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = build_ele.dadesTubHor.value[x].desplY
        else:
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX + 50
            posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX
            posVerticalInf = posVertical = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 )) + 50
            posVerticalSup = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 )) + build_ele.dadesTubHor.value[x].Llargada
    elif  build_ele.dadesTubHor.value[x].posAutomatica and  build_ele.dadesTubHor.value[x].LlargadaAut:
        if not build_ele.dadesTubHor.value[x].RotarTub:#Tub Horitzontal
            posHoritzontalEsq = posHoritzontal = get_posicioX(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 ))
            posHoritzontalDre = get_posicioX(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3 ))
            posVerticalInf = posVertical = build_ele.dadesTubHor.value[x].desplY
            posVerticalSup = build_ele.dadesTubHor.value[x].desplY
        else:
            posHoritzontalEsq = posHoritzontal = build_ele.dadesTubHor.value[x].desplX + 50
            posHoritzontalDre = build_ele.dadesTubHor.value[x].desplX
            posVerticalInf = posVertical = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3 )) + 50
            posVerticalSup = get_posicioY(build_ele, getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3 ))

    return posHoritzontalEsq, posHoritzontal , posHoritzontalDre, posVerticalInf, posVertical, posVerticalSup

def detectar_colisio_tubs(build_ele, doc, nHorSeleccionat, ntubsAfegits, llistaTubs):
    #print("build_ele.IntegerISSelectorHor.value : " + str(build_ele.IntegerISSelectorHor.value))
    #print("ntubsAfegits                         : " + str(ntubsAfegits))
    #print("-------------------------------------:  ----")
    #print("                                     : " + str(build_ele.IntegerISSelectorHor.value - ntubsAfegits))
    lenDadesTubHorAct = build_ele.IntegerISSelectorHor.value-ntubsAfegits
    for x in range(0, lenDadesTubHorAct):


        if x not in llistaTubs.values():

            posHoritzontalEsq, posHoritzontal, posHoritzontalDre, posVerticalInf, posVertical, posVerticalSup = get_posicions_tubsexteriors(build_ele, x)

            if build_ele.dadesTubHor.value[x].RotarTub:#tub Vertical
                if posHoritzontal >= build_ele.PosicioXlinia.value and posHoritzontal < build_ele.PosicioXlinia.value + build_ele.Amplelinia.value :
                    if  (posVerticalSup <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and posVerticalSup > build_ele.PosicioYlinia.value ) and posVertical < build_ele.PosicioYlinia.value :
                        print("ESQ tallar tub VERTICAL a dalt [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        if nHorSeleccionat == x:
                            build_ele.llargadaAutomatica.value = False
                            build_ele.BarraLlargada.value =  build_ele.PosicioYlinia.value - posVertical - 50
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = build_ele.dadesTubHor.value[x].retallFinal + 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                build_ele.BarraLlargada.value = build_ele.PosicioYlinia.value  + 50
                                if x == build_ele.ExteriorDreta.value:
                                    build_ele.BarraLlargada.value =  build_ele.PosicioYlinia.value  + 50


                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(LlargadaAut = False)
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioYlinia.value - posVertical - 50)#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioYlinia.value )#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                                if x == build_ele.ExteriorDreta.value:
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioYlinia.value  + 50)#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = build_ele.dadesTubHor.value[x].retallFinal + 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                        if x != build_ele.ExteriorEsquerra.value and x != build_ele.ExteriorDreta.value:
                            if llistaTubs["Inf"] != None:
                                asignar_barra_superior(build_ele, x, nHorSeleccionat, llistaTubs["Inf"])
                    elif  posVerticalSup > build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and (posVertical >= build_ele.PosicioYlinia.value and posVertical < build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value):
                        print("ESQ tallar tub VERTICAL cap a dalt [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        if nHorSeleccionat == x:
                            build_ele.llargadaAutomatica.value = False
                            build_ele.BarraLlargada.value = posVerticalSup -  posVerticalInf - 50 #posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value)
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf - 50)
                            #build_ele.desplY.value = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.dadesTubHor.value[x].retallInicial + 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                if build_ele.crearForat2.value and x == build_ele.ExteriorDreta.value:
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf - 50)

                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(LlargadaAut = False)
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = posVerticalSup -  posVerticalInf )#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )

                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf )
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = posVerticalSup -  posVerticalInf - 50)#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf )
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.ISAmplada.value)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                if build_ele.crearForat2.value and x == build_ele.ExteriorDreta.value:
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf - 50)

                        #if llistaTubs["Sup"] != None:
                        #    asignar_barra_inferior(build_ele, x, nHorSeleccionat, llistaTubs["Sup"])
                    elif posVerticalSup >= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and posVertical < build_ele.PosicioYlinia.value :
                        print("ESQ tallar tub VERTICAL [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        if nHorSeleccionat == x:
                            build_ele.llargadaAutomatica.value = False
                            build_ele.BarraLlargada.value = posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value)
                            build_ele.posAutomatica.value = False
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf)
                            #build_ele.desplY.value = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.dadesTubHor.value[x].retallFinal )#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = build_ele.dadesTubHor.value[x].retallFinal )#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)

                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = posVerticalSup - (build_ele.dadesTubHor.value[x].Llargada  +  build_ele.dadesTubHor.value[x].desplY))#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posVerticalSup - (build_ele.dadesTubHor.value[x].Llargada  +  build_ele.dadesTubHor.value[x].desplY))#posVerticalSup - (build_ele.Llargadalinia.value  +  build_ele.PosicioYlinia.value) )
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf)
                            #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value )
                            if x == build_ele.ExteriorEsquerra.value or x == build_ele.ExteriorDreta.value:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.ISAmplada.value)#build_ele.dadesTubHor.value[x].retallFinal )#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = 0 )#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                if build_ele.crearForat2.value and x == build_ele.ExteriorDreta.value:
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value - posVerticalInf - 50)

                        if build_ele.PosicioYlinia.value != 0:
                            crear_barra_Vertical(build_ele, nHorSeleccionat, posVerticalInf, build_ele.PosicioYlinia.value, build_ele.dadesTubHor.value[x].desplX, getLetterFromText(build_ele, build_ele.dadesTubHor.value[x].TipusTub, 3))
                            if build_ele.dadesTubHor.value[len(build_ele.dadesTubHor.value)-2].tipusTubAuto:
                                detectar_tipus_tub(build_ele, doc, len(build_ele.dadesTubHor.value)-2, nHorSeleccionat)
                            if build_ele.crearForat2.value and x == build_ele.ExteriorDreta.value:
                                build_ele.dadesTubHor.value[len(build_ele.dadesTubHor.value)-2] = build_ele.dadesTubHor.value[len(build_ele.dadesTubHor.value)-2]._replace(LlargadaAut = False)
                                build_ele.dadesTubHor.value[len(build_ele.dadesTubHor.value)-2] = build_ele.dadesTubHor.value[len(build_ele.dadesTubHor.value)-2]._replace(Llargada = build_ele.PosicioYlinia.value + 50)

                    elif posVertical >= build_ele.PosicioYlinia.value and posVertical + build_ele.dadesTubHor.value[x].Llargada <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value:
                        print("ESQ ocultar Tub  VERTICAL[" + str(x) + "]")
                        if nHorSeleccionat == x:
                            build_ele.MostrarTub.value = False
                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

            else: #tub Horitzontal
                #if (posHoritzontal >= build_ele.PosicioXlinia.value and posHoritzontal <= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) and ( posVertical >= build_ele.PosicioYlinia.value and posVertical <=build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value):
                if ( posVertical >= build_ele.PosicioYlinia.value and posVertical + 50   <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value):
                    if posHoritzontal + build_ele.dadesTubHor.value[x].Llargada >= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value:
                        print("tub a la dreta del cub")
                        print("ESQ tallar i desplaçar tub HORITZONTAL [" + str(x) + "] a " + str(build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) + " i retallar " + str(posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50))
                        if nHorSeleccionat == x:
                            build_ele.retallInicial.value = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50)
                            if build_ele.posAutomatica.value:
                                #build_ele.desplX.value = build_ele.desplX.value + 50

                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50)
                                #build_ele.retallFinal.value = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50

                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = build_ele.BarraLlargadaReal.value - posHoritzontalDre)
                                build_ele.retallFinal.value = build_ele.BarraLlargadaReal.value - posHoritzontalDre

                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50)
                                #build_ele.BarraLlargada.value = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50
                            else:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50)
                                build_ele.retallInicial.value = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50

                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50)
                            if build_ele.dadesTubHor.value[x].posAutomatica:
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplX = build_ele.dadesTubHor.value[x].desplX + 50)

                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) )

                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = build_ele.dadesTubHor.value[x].Llargada - posHoritzontalDre)

                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) )
                            else:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallInicial = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value  - posHoritzontalEsq - 50)

                            #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value - 50)
                        #if llistaTubs["Esq"] != None:
                        #    asignar_barra_inferior(build_ele, x, nHorSeleccionat, llistaTubs["Esq"])
                        if build_ele.PosicioXlinia.value != 0:
                            print("Crear tub a Esquerra del cub")
                            crear_barra_Horitzontal(build_ele, nHorSeleccionat, posHoritzontalEsq - 50, build_ele.PosicioXlinia.value-50, build_ele.dadesTubHor.value[x].desplY, getLetterFromText(build_ele, build_ele.dadesTubHor.value[x].TipusTub, 3))
                            verticalMesProper = detectar_vertical_anterior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat)
                            if verticalMesProper != None:
                                asignar_barra_inferior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, verticalMesProper)
                            if llistaTubs["Esq"] != None:
                                asignar_barra_superior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Esq"])
                            if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].tipusTubAuto:
                                detectar_tipus_tub(build_ele, doc, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat)
                            reasignarTubs(build_ele, x, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat)
                        #if llistaTubs["Esq"] != None:
                        #    asignar_barra_superior(build_ele, build_ele.IntegerISSelectorHor.value-1, nHorSeleccionat, llistaTubs["Esq"])

                    elif posHoritzontal + build_ele.dadesTubHor.value[x].Llargada <= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value and posHoritzontal <= build_ele.PosicioXlinia.value and posHoritzontal + build_ele.dadesTubHor.value[x].Llargada  >= build_ele.PosicioXlinia.value :
                        print("tub a Esquerra del cub")
                        print("retallar final tub HORITZONTAl[" + str(x) + "] a llargada: " + str(build_ele.PosicioXlinia.value - posHoritzontal))
                        if nHorSeleccionat == x:
                            if not build_ele.llargadaAutomatica.value:
                                build_ele.retallFinal.value = posHoritzontalDre - build_ele.PosicioXlinia.value
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal =  posHoritzontalDre - build_ele.PosicioXlinia.value)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioXlinia.value - posHoritzontal)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                #build_ele.BarraLlargada.value = build_ele.PosicioXlinia.value - posHoritzontal
                                if not build_ele.posAutomatica.value:
                                    build_ele.retallFinal.value = build_ele.PosicioXlinia.value - posHoritzontalDre -50
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posHoritzontalDre - build_ele.PosicioXlinia.value - 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                    #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioXlinia.value - posHoritzontal -50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                    #build_ele.BarraLlargada.value = build_ele.PosicioXlinia.value - posHoritzontal -50
                        else:
                            if not build_ele.dadesTubHor.value[x].LlargadaAut:
                                build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posHoritzontalDre - build_ele.PosicioXlinia.value  )#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioXlinia.value - posHoritzontal)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                if not build_ele.dadesTubHor.value[x].posAutomatica:
                                    build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(retallFinal = posHoritzontalDre - build_ele.PosicioXlinia.value - 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                                    #build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Llargada = build_ele.PosicioXlinia.value - posHoritzontal - 50)#posHoritzontalDre - build_ele.PosicioXlinia.value  -50)
                        if llistaTubs["Esq"] != None:
                            asignar_barra_superior(build_ele, x, nHorSeleccionat, llistaTubs["Esq"])
                    elif posHoritzontal + build_ele.dadesTubHor.value[x].Llargada <= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value and posHoritzontal >= build_ele.PosicioXlinia.value:
                        print("ESQ ocultar Tub HORITZONTAL[" + str(x) + "]")
                        if nHorSeleccionat == x:
                            build_ele.MostrarTub.value = False
                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

            detectar_tipus_tub(build_ele, doc, x, nHorSeleccionat)#, encaixAmbTubInf, encaixAmbTubSup)

def ocultar_interiors(build_ele, nHorSeleccionat, ntubsAfegits = 0, llistaExteriorsForat = [] ):


    lenDadesTubHorAct = build_ele.IntegerISSelectorHor.value-ntubsAfegits
    for x in range(0, lenDadesTubHorAct):

        if x not in llistaExteriorsForat.values():

            posHoritzontalEsq, posHoritzontal, posHoritzontalDre, posVerticalInf, posVertical, posVerticalSup = get_posicions_tubsexteriors(build_ele, x)

            if build_ele.dadesTubHor.value[x].RotarTub:#tub Vertical
                if posHoritzontal >= build_ele.PosicioXlinia.value and posHoritzontal < build_ele.PosicioXlinia.value + build_ele.Amplelinia.value :
                    if  (posVerticalSup <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and posVerticalSup > build_ele.PosicioYlinia.value ) and posVertical < build_ele.PosicioYlinia.value :
                        print("ESQ tallar tub VERTICAL a dalt [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        pass
                    elif  posVerticalSup > build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and (posVertical >= build_ele.PosicioYlinia.value and posVertical < build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value):
                        print("ESQ tallar tub VERTICAL cap a dalt [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        pass
                    elif posVerticalSup >= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value and posVertical < build_ele.PosicioYlinia.value :
                        print("ESQ tallar tub VERTICAL [" + str(x) + "] a " + str(build_ele.PosicioYlinia.value) + " i a " + str(build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value))
                        pass
                    elif posVertical >= build_ele.PosicioYlinia.value and posVertical + build_ele.dadesTubHor.value[x].Llargada - build_ele.dadesTubHor.value[x].retallFinal <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value:
                        print("ESQ ocultar Tub  VERTICAL[" + str(x) + "]")
                        if nHorSeleccionat == x:
                            build_ele.MostrarTub.value = False
                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)
            else: #tub Horitzontal
                if ( posVertical >= build_ele.PosicioYlinia.value and posVertical <= build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value):
                    if posHoritzontal + build_ele.dadesTubHor.value[x].Llargada >= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value:
                        print("tub a la dreta del cub")
                        print("ESQ tallar i desplaçar tub HORITZONTAL [" + str(x) + "] a " + str(build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) + " i retallar " + str(posHoritzontalDre - (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - 50))
                        pass
                    elif posHoritzontal + build_ele.dadesTubHor.value[x].Llargada <= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value and posHoritzontal <= build_ele.PosicioXlinia.value and posHoritzontal + build_ele.dadesTubHor.value[x].Llargada  >= build_ele.PosicioXlinia.value :
                        print("tub a Esquerra del cub")
                        print("retallar final tub HORITZONTAl[" + str(x) + "] a llargada: " + str(build_ele.PosicioXlinia.value - posHoritzontal))
                        pass
                    elif posHoritzontal + build_ele.dadesTubHor.value[x].Llargada <= build_ele.PosicioXlinia.value + build_ele.Amplelinia.value and posHoritzontal >= build_ele.PosicioXlinia.value:
                        print("ESQ ocultar Tub HORITZONTAL[" + str(x) + "]")
                        if nHorSeleccionat == x:
                            build_ele.MostrarTub.value = False
                        else:
                            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(Mostrar = False)

def detectar_vertical_anterior(build_ele, x, nHorSeleccionat, posX = -50, posY = 0):
    '''
    x = tub Horitzontal

    return el tub Vertical que el travessa, mes propers
    '''

    if x != -1:
        posY = build_ele.dadesTubHor.value[x].desplY
        posX = build_ele.PosicioXlinia.value -50

    anteriorMesProper = None
    for posTub in range(0, len(build_ele.dadesTubHor.value)):
        if build_ele.dadesTubHor.value[posTub].RotarTub:
            if build_ele.dadesTubHor.value[posTub].desplX < posX:
                sumatoriY = 0
                if build_ele.dadesTubHor.value[posTub].posAutomatica:
                    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posTub].tubInferior, 3)
                    sumatoriY = 50 + get_posicioY(build_ele, nTubInf)
                #print( str(build_ele.dadesTubHor.value[posTub].desplY)  + " + " + str(build_ele.dadesTubHor.value[posTub].retallInicial) + " + " + str(sumatoriY) + " <= " + str(posY) + " and " +  str(build_ele.dadesTubHor.value[posTub].desplY) + " + " + str(build_ele.dadesTubHor.value[posTub].retallInicial) + " + "  + str(build_ele.dadesTubHor.value[posTub].Llargada) + " + " + str(sumatoriY) + " > " +  str(posY))
                #print( str(build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriY) + " <= " + str(posY) + " and " +  str(build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriY) + " > " +  str(posY))
                #print( str(posTub) + ": " +str((build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriY)  <= posY ) + " and " +  str(build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriY > posY))
                if build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriY <= posY  and build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriY > posY :
                    if anteriorMesProper == None:
                        anteriorMesProper = posTub
                    elif build_ele.dadesTubHor.value[posTub].desplX > build_ele.dadesTubHor.value[anteriorMesProper].desplX:
                        anteriorMesProper = posTub

    return anteriorMesProper

def detectar_vertical_seguent(build_ele, x, nHorSeleccionat, posX = 0, posY = 0):
    '''
    x = tub Horitzontal

    return el tub Vertical que el travessa, mes propers
    '''

    if x != -1:
        posY = build_ele.dadesTubHor.value[x].desplY
        posX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value + 50

    seguentExtrem = None
    seguentMesProper = None
    lenDadesTubHorAct = build_ele.IntegerISSelectorHor.value
    for posTub in range(0, len(build_ele.dadesTubHor.value)):
        if build_ele.dadesTubHor.value[posTub].RotarTub and build_ele.dadesTubHor.value[posTub].Mostrar:
            if seguentExtrem == None or build_ele.dadesTubHor.value[posTub].desplX > build_ele.dadesTubHor.value[seguentExtrem].desplX:
                seguentExtrem = posTub
            if build_ele.dadesTubHor.value[posTub].desplX >= posX:
                sumatoriY = 0
                if build_ele.dadesTubHor.value[posTub].posAutomatica:
                    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posTub].tubInferior, 3)
                    sumatoriY = 50 + get_posicioY(build_ele, nTubInf)
                if build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriY <= posY  and build_ele.dadesTubHor.value[posTub].desplY + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriY >= posY :
                    if seguentMesProper == None:
                        seguentMesProper = posTub
                    elif build_ele.dadesTubHor.value[posTub].desplX < build_ele.dadesTubHor.value[seguentMesProper].desplX:
                        seguentMesProper = posTub

    if seguentMesProper != None:
        return seguentMesProper
    else:
        return seguentExtrem

def detectar_horitzontal_anterior(build_ele, x, nHorSeleccionat, posX = 0 , posY = 0):
    '''
    x = tub Vertical

    return el tub Horitzontal que el travessa, mes propers
    '''

    if x != -1:
        posY = build_ele.PosicioYlinia.value -50
        posX = build_ele.dadesTubHor.value[x].desplX

    anteriorMesProper = None
    for posTub in range(0, len(build_ele.dadesTubHor.value)):
        if not build_ele.dadesTubHor.value[posTub].RotarTub:
            if get_posicioY(build_ele, posTub) < posY:
                sumatoriX = 0
                if build_ele.dadesTubHor.value[posTub].posAutomatica:
                    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posTub].tubInferior, 3)
                    sumatoriX = 50 + get_posicioX(build_ele, nTubInf)
                if build_ele.dadesTubHor.value[posTub].desplX + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriX <= posX  and build_ele.dadesTubHor.value[posTub].desplX + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriX > posX :
                    if anteriorMesProper == None:
                        anteriorMesProper = posTub
                    elif get_posicioY(build_ele, posTub) > get_posicioY(build_ele, anteriorMesProper):
                        anteriorMesProper = posTub

    return anteriorMesProper

def detectar_horitzontal_seguent(build_ele, x, nHorSeleccionat, posX = 0, posY = 0):
    '''
    x = tub Vertical

    return el tub Horitzontal que el travessa, mes propers
    '''

    if x != -1:
        posY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value + 50
        posX = build_ele.dadesTubHor.value[x].desplX

    seguentExtrem = None
    seguentMesProper = None
    for posTub in range(0, len(build_ele.dadesTubHor.value)):
        if not build_ele.dadesTubHor.value[posTub].RotarTub and build_ele.dadesTubHor.value[posTub].Mostrar:
            #print(str(posTub) + " : " + str(get_posicioY(build_ele, posTub)) + " > " + str(get_posicioY(build_ele, seguentExtrem)))
            if seguentExtrem == None or get_posicioY(build_ele, posTub) > get_posicioY(build_ele, seguentExtrem):
                seguentExtrem = posTub
            if get_posicioY(build_ele, posTub) > posY:
                sumatoriX = 0


                if build_ele.dadesTubHor.value[posTub].posAutomatica:
                    nTubInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[posTub].tubInferior, 3)
                    sumatoriX = 50 + get_posicioX(build_ele, nTubInf)

                if build_ele.dadesTubHor.value[posTub].desplX + build_ele.dadesTubHor.value[posTub].retallInicial + sumatoriX <= posX  and build_ele.dadesTubHor.value[posTub].desplX + build_ele.dadesTubHor.value[posTub].retallInicial + build_ele.dadesTubHor.value[posTub].Llargada + sumatoriX >= posX :
                    if seguentMesProper == None:
                        seguentMesProper = posTub
                    elif get_posicioY(build_ele, posTub) < get_posicioY(build_ele, seguentMesProper):
                        seguentMesProper = posTub

    if seguentMesProper != None:
        return seguentMesProper
    else:
        return seguentExtrem

def detectar_conjunt_tipus_tub(build_ele, doc, nHorSeleccionat, conjuntTubs):
    '''
    Detectar per cada tub de la llista tipus de tub mes adïent
    segons si va encaixat a un tub amb femella o no
    i que s'hagi de tallar el minim posible
    '''
    for posTub in conjuntTubs:
        detectar_tipus_tub(build_ele, doc, posTub ,nHorSeleccionat)
        #detectar_canvis_adjacents(build_ele, doc, posTub, nHorSeleccionat)

def assignar_infSup_corresponents(build_ele, nHorSeleccionat):
    lenDadesTubHorAct = build_ele.IntegerISSelectorHor.value
    for posTub in range(0, lenDadesTubHorAct):
        if not build_ele.dadesTubHor.value[posTub].RotarTub:
            anteriorMesProper = detectar_vertical_anterior(build_ele, posTub, nHorSeleccionat)
            if anteriorMesProper != None:
                asignar_barra_inferior(build_ele, posTub, nHorSeleccionat, anteriorMesProper)
            seguentMesProper = detectar_vertical_seguent(build_ele, posTub, nHorSeleccionat)
            if seguentMesProper != None:
                asignar_barra_superior(build_ele, posTub, nHorSeleccionat, seguentMesProper)


def detectar_tipus_tub(build_ele, doc, posTub ,nHorSeleccionat, encaixInf = True, encaixSup = True):
    '''
    Detectar tipus de tub mes adïent
    segons si va encaixat a un tub amb femella o no
    i que s'hagi de tallar el minim posible
    '''
    llargadesRealsOriginals = {
            "A": 2150,
            "B": 650,
            "C": 650,
            "D": 1350,
            "E": 5550,
            "F": 1350,
    }

    lleterTipusTub = getLetterFromText(build_ele, build_ele.dadesTubHor.value[posTub].TipusTub, 3)

    #detectar si te femella
    sensePestanyes = False
    encaixAmbTubInf =  encaix_pestanyes_amb_inferior(build_ele, doc, posTub, nHorSeleccionat)
    encaixAmbTubSup =  encaix_pestanyes_amb_superior(build_ele, doc, posTub, nHorSeleccionat)
    if build_ele.dadesTubHor.value[posTub].tipusTubAuto:
        if ((not encaixAmbTubInf and build_ele.dadesTubHor.value[posTub].retallInicial == 0) and \
            (not encaixAmbTubSup and build_ele.dadesTubHor.value[posTub].retallFinal == 0)) and \
            build_ele.dadesTubHor.value[posTub].posAutomatica and \
            build_ele.dadesTubHor.value[posTub].LlargadaAut :
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")#sense pestanyes/mascles
            sensePestanyes = True
            #print(str(posTub)+" - NO Encaixa amb Inici i Final")
        elif not encaixAmbTubInf and \
                build_ele.dadesTubHor.value[posTub].retallInicial == 0 and \
                build_ele.dadesTubHor.value[posTub].posAutomatica:
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")#sense pestanyes/mascles
            sensePestanyes = True
        elif not encaixAmbTubSup and \
                build_ele.dadesTubHor.value[posTub].Llargada == llargadesRealsOriginals[lleterTipusTub] and \
                build_ele.dadesTubHor.value[posTub].retallFinal == 0 and \
                build_ele.dadesTubHor.value[posTub].LlargadaAut:
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")#sense pestanyes/mascles
            sensePestanyes = True
        elif encaixAmbTubInf and \
            (build_ele.dadesTubHor.value[posTub].retallFinal != 0 or build_ele.dadesTubHor.value[posTub].Llargada != llargadesRealsOriginals[lleterTipusTub]) and\
            build_ele.dadesTubHor.value[posTub].posAutomatica:
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB E")#amb pestanyes/mascles
        elif not encaixAmbTubInf and encaixAmbTubSup and \
            build_ele.dadesTubHor.value[posTub].retallInicial != 0 and \
            build_ele.dadesTubHor.value[posTub].LlargadaAut:
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB E")#amb pestanyes/mascles
        else:
            build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB E")#amb pestanyes/mascles
            #print(str(posTub)+" - Encaixa amb Inici i Final")


    #llargada = get_llargadaAut(build_ele, posTub, build_ele.dadesTubHor.value[posTub].RotarTub)
    #if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB E" and (build_ele.dadesTubHor.value[posTub].Llargada - build_ele.dadesTubHor.value[posTub].retallInicial < 1350  ):#or build_ele.dadesTubHor.value[posTub].retallFinal < 1350):
    llargada = build_ele.dadesTubHor.value[posTub].Llargada - build_ele.dadesTubHor.value[posTub].retallInicial - build_ele.dadesTubHor.value[posTub].retallFinal

    #sí el tub es mes gran del permes, canviar al tipus de tub adient per fer el tall mes petit possible
    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB B"  and llargada > 650 :
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB C"  and llargada > 650:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB D"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB D")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB D"  and llargada > 775:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB F"  and llargada > 1350:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB A"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB A"  and llargada > 2150:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB E"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB E")

    #sí el tub es mes petit del permes, canviar al tipus de tub adient per fer el tall mes petit possible
    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB E"  and llargada <= 2150 and build_ele.dadesTubHor.value[posTub].RotarTub:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB A"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB A"  and llargada <= 1350 and not sensePestanyes:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")
    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB A"  and llargada <= 750 and sensePestanyes:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB D"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB D")

    #no es segur aquest canvi
    '''
    #if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB F"  and llargada <= 775:
    #    if nHorSeleccionat == posTub:
    #        build_ele.TipusTUB.value = "TUB D"
    #    build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB D")
    '''
    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB D"  and llargada <= 650:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB C"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB C")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB F"  and llargada <= 650 :
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB B"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB B")



    #si es fa un tall

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB E" and (llargada < 1350):
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB D" and (llargada < 650 ):
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB C"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB C")

    #si es extrem semprw sera A
    if (build_ele.dadesTubHor.value[posTub].desplX == build_ele.dadesTubHor.value[build_ele.ExteriorEsquerra.value].desplX or \
        build_ele.dadesTubHor.value[posTub].desplX == build_ele.dadesTubHor.value[build_ele.ExteriorDreta.value].desplX) and \
        build_ele.dadesTubHor.value[posTub].RotarTub:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB A"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")

    #si es B(marro) i es provisional canviar per C(verd)
    if (build_ele.dadesTubHor.value[posTub].esProvisional) and \
        build_ele.dadesTubHor.value[posTub].RotarTub and    \
        build_ele.dadesTubHor.value[posTub].TipusTub == "TUB B":
        #(build_ele.dadesTubHor.value[posTub].TipusTub == "TUB B" or \
        # (build_ele.dadesTubHor.value[posTub].TipusTub == "TUB A" and (llargada <= 650))):
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB C"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB C")

def detectar_es_posible(build_ele, doc, posTub ,nHorSeleccionat, encaixInf = True, encaixSup = True, mostratError = False):
    '''
    Detectar tipus de tub mes adïent
    segons si va encaixat a un tub amb femella o no
    i que s'hagi de tallar el minim posible
    '''

    teError = False

    #no detecta be quan es mes petit
    #llargada = get_llargadaAut(build_ele, posTub, build_ele.dadesTubHor.value[posTub].RotarTub)
    #if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB E" and (build_ele.dadesTubHor.value[posTub].Llargada - build_ele.dadesTubHor.value[posTub].retallInicial < 1350  ):#or build_ele.dadesTubHor.value[posTub].retallFinal < 1350):
    llargada = build_ele.dadesTubHor.value[posTub].Llargada - build_ele.dadesTubHor.value[posTub].retallInicial - build_ele.dadesTubHor.value[posTub].retallFinal

    #sí el tub es mes gran del permes, canviar al tipus de tub adient per fer el tall mes petit possible
    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB B"  and llargada > 650 :
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")
        teError = True

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB C"  and llargada > 650:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB D"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB D")
        teError = True

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB D"  and llargada > 775:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB F"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB F")
        teError = True

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB F"  and llargada > 1350:
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB A"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB A")
        teError = True

    if build_ele.dadesTubHor.value[posTub].TipusTub == "TUB A"  and llargada > 2150 :
        if nHorSeleccionat == posTub:
            build_ele.TipusTUB.value = "TUB E"
        build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(TipusTub = "TUB E")
        teError = True

    if not mostratError and teError :
        ctypes.windll.user32.MessageBoxW(0, "Tipus de tub Impossible per mesures", 0)
        mostratError = True

    return mostratError

def detectar_canvis_adjacents(build_ele, doc, posTub, nHorSeleccionat):
    pass

def get_pos_femelles(build_ele, x):
    llistatFemelles = []

    encaixos, femelles, potes, forats, colis = get_valors_actuals(build_ele, x)
    for femella in femelles:
        if femella.PosFemellaX >= build_ele.dadesTubHor.value[x].retallInicial:
            llistatFemelles.append(femella.PosFemellaX)

    return llistatFemelles

def encaix_pestanyes_amb_inferior(build_ele, doc, x, nHorSeleccionat):
    posicioAbsoluta = 0
    posicioAbsoluta = []

    numPosInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3)

    if build_ele.dadesTubHor.value[x].RotarTub: #Vertical
        posicioAbsoluta = get_posicioX(build_ele, x) - 50
        if not build_ele.dadesTubHor.value[x].posAutomatica:
            posicioAbsoluta -= 50
        posicioInfAbsoluta = get_posicioX(build_ele, numPosInf)

    else: #Horitzontal
        posicioAbsoluta = get_posicioY(build_ele, x)
        posicioInfAbsoluta = get_posicioY(build_ele, numPosInf)

    #recorrer femelles
    posicionsFemelles =  get_pos_femelles(build_ele, numPosInf)

    for pos in posicionsFemelles:
        #get_posicioFemella absoluta
        posFemAbs = posicioInfAbsoluta + pos

        #si concorda amb alguna
        if posFemAbs == posicioAbsoluta:
            #tub amb pestanya
            return True
        #else
            #tub sense pestanya
    return False

def encaix_pestanyes_amb_superior(build_ele, doc, x, nHorSeleccionat):
    posicioAbsoluta = 0
    posicioAbsoluta = []

    #numPosInf = getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubInferior, 3)
    numPosSup = getNumFromText(build_ele, build_ele.dadesTubHor.value[x].tubSuperior, 3)

    if build_ele.dadesTubHor.value[x].RotarTub: #Vertical
        posicioAbsoluta = get_posicioX(build_ele, x) - 50
        if not build_ele.dadesTubHor.value[x].posAutomatica:
            posicioAbsoluta -= 50
        posicioInfAbsoluta = get_posicioX(build_ele, numPosSup)
    else: #Horitzontal
        posicioAbsoluta = get_posicioY(build_ele, x)
        posicioInfAbsoluta = get_posicioY(build_ele, numPosSup)

    #recorrer femelles
    posicionsFemelles =  get_pos_femelles(build_ele, numPosSup)

    for pos in posicionsFemelles:
        posicioInfAbsoluta = 0#get_posicioX(build_ele, numPosSup)
        posFemAbs = posicioInfAbsoluta + pos
        #si concorda amb alguna
        if posFemAbs == posicioAbsoluta:
            #tub amb pestanya
            return True
        #else
            #tub sense pestanya
    #print("---No Trobat---]")
    return False

def te_pestanyes(build_ele, doc, posTub):
    tipusTub = build_ele.dadesTubHor.value[posTub].TipusTub
    if tipusTub == "TUB B" or tipusTub == "TUB E" or tipusTub == "TUB F":
        return True
    return False

def reasignarTubs(build_ele, posAnt, posNou, nHorSeleccionat):
    for posTub in range(0, len(build_ele.dadesTubHor.value)):
        if build_ele.dadesTubHor.value[posTub].RotarTub:
            if build_ele.dadesTubHor.value[posTub].tubInferior == "Tub " +str(posAnt):
                if build_ele.dadesTubHor.value[posNou].desplX + build_ele.dadesTubHor.value[posNou].retallInicial < build_ele.dadesTubHor.value[posTub].desplX and build_ele.dadesTubHor.value[posNou].desplX + build_ele.dadesTubHor.value[posNou].retallInicial + build_ele.dadesTubHor.value[posNou].Llargada > build_ele.dadesTubHor.value[posTub].desplX:#posicio esta entre inici i final de tub nou(posNou)
                    build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(tubInferior = "Tub " +str(posNou))
            if build_ele.dadesTubHor.value[posTub].tubSuperior == "Tub " +str(posAnt):
                if build_ele.dadesTubHor.value[posNou].desplX + build_ele.dadesTubHor.value[posNou].retallInicial < build_ele.dadesTubHor.value[posTub].desplX and build_ele.dadesTubHor.value[posNou].desplX + build_ele.dadesTubHor.value[posNou].retallInicial + build_ele.dadesTubHor.value[posNou].Llargada > build_ele.dadesTubHor.value[posTub].desplX:#posicio esta entre inici i final de tub nou(posNou)
                    build_ele.dadesTubHor.value[posTub] = build_ele.dadesTubHor.value[posTub]._replace(tubSuperior = "Tub " +str(posNou))


def crear_barra_Vertical(build_ele, nHorSeleccionat, posInf, posSup, posX, tipusTub):
    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value> len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB "+str(tipusTub) )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = True)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub 0")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub 1")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  posSup - posInf)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = posInf)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = posX)

def crear_barra_Horitzontal(build_ele, nHorSeleccionat, posEsq, posDre, posY, tipusTub):
    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value> len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB "+str(tipusTub) )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub 0")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub 1")
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  posDre - posEsq)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = posY)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = posEsq)

def asignar_barra_inferior(build_ele, x, nHorSeleccionat, barraInf):
    if x == nHorSeleccionat:
        build_ele.posAutomatica.value = True
        build_ele.SelectorTubInferior.value = "Tub " + str(barraInf)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(posAutomatica = True)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubInferior = "Tub " + str(barraInf))
        if not build_ele.dadesTubHor.value[x].RotarTub:
            build_ele.desplX.value = 0
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplX = 0)
        else:
            build_ele.desplY.value = 0
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplY = 0)

    else:
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(posAutomatica = True)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubInferior = "Tub " + str(barraInf))
        if not build_ele.dadesTubHor.value[x].RotarTub:
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(desplY = 0)

def asignar_barra_superior(build_ele, x, nHorSeleccionat, barraSup):
    if x == nHorSeleccionat:
        build_ele.llargadaAutomatica.value = True
        build_ele.SelectorTubSuperior.value = "Tub " + str(barraSup)
        build_ele.SelectorTubSuperiorHor.value = "Tub " + str(barraSup)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(LlargadaAut = True)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubSuperior = "Tub " + str(barraSup))
    else:
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(LlargadaAut = True)
        build_ele.dadesTubHor.value[x] = build_ele.dadesTubHor.value[x]._replace(tubSuperior = "Tub " + str(barraSup))



def crear_barra_sup_Forat(build_ele, nHorSeleccionat, costats, tubInf = 0, tubSup = 1, posAutomatica = False, llargadaAutomatica = False):
    #afegir Tub Horitzontal
    llargadaRetallada = build_ele.Amplelinia.value - 50
    if build_ele.PosicioXlinia.value + build_ele.Amplelinia.value > build_ele.ISllargada.value:
        llargadaRetallada = build_ele.Amplelinia.value - ( (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - build_ele.ISllargada.value ) - 50
    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value> len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB E" )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub " + str(tubInf))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub " + str(tubSup))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = llargadaAutomatica)
    if "Esq" in costats and "Dre" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  build_ele.Amplelinia.value)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value-50)
    elif "Esq" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  build_ele.Amplelinia.value + 50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(retallFinal =  0)#build_ele.Amplelinia.value + 50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0-50)
    elif "Dre" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada = llargadaRetallada)#build_ele.Amplelinia.value-50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  build_ele.Amplelinia.value-100)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value-50)
    return build_ele.IntegerISSelectorHor.value-1

def crear_barra_inf_Forat(build_ele, nHorSeleccionat, costats, tubInf = 0, tubSup = 1, posAutomatica = False, llargadaAutomatica = False):
    #afegir Tub Horitzontal
    llargadaRetallada =  build_ele.Amplelinia.value - 50
    if build_ele.PosicioXlinia.value + build_ele.Amplelinia.value > build_ele.ISllargada.value:
        llargadaRetallada = build_ele.Amplelinia.value - ( (build_ele.PosicioXlinia.value + build_ele.Amplelinia.value) - build_ele.ISllargada.value ) - 50
    if build_ele.PosicioXlinia.value < 0:
        llargadaRetallada = build_ele.Amplelinia.value - abs(build_ele.PosicioXlinia.value)
    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value> len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB E" )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = False)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub " + str(tubInf))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub " + str(tubSup))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = llargadaAutomatica)
    if "Esq" in costats and "Dre" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  build_ele.Amplelinia.value-50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value-50)
    elif "Esq" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargadaRetallada + 50)#build_ele.Amplelinia.value + 50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(retallFinal =  0)#build_ele.Amplelinia.value + 50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0-50)
    elif "Dre" in costats:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargadaRetallada)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        #build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  build_ele.Amplelinia.value-100)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
        if build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1].posAutomatica:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = 0)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value )
    return build_ele.IntegerISSelectorHor.value-1

def crear_barra_dreta_Forat(build_ele, nHorSeleccionat, costats, tubInf = 0, tubSup = 1, posAutomatica = False, llargadaAutomatica = False, tipus = 1):
    #afegir Tub Vertical
    llargada = build_ele.Llargadalinia.value
    if build_ele.PosicioYlinia.value < 0:
        llargada = build_ele.Llargadalinia.value - abs(build_ele.PosicioYlinia.value)
    if build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value > build_ele.ISAmplada.value:
        #llargada = build_ele.Llargadalinia.value - (build_ele.ISAmplada.value - build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value)
        llargada =build_ele.ISAmplada.value - build_ele.PosicioYlinia.value

    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value> len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB E" )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = True)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub " + str(tubInf))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub " + str(tubSup))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = llargadaAutomatica)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
    if tipus == 1:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada)#build_ele.Llargadalinia.value)
    elif tipus == 3:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada - 100)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada - 50 )#build_ele.Llargadalinia.value - 50)
    if posAutomatica:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value-100)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = 0)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value + build_ele.Amplelinia.value-50)
        if tipus == 3:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value + 50)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)
    return build_ele.IntegerISSelectorHor.value-1

def crear_barra_esquerra_Forat(build_ele, nHorSeleccionat, costats, tubInf = 0, tubSup = 1, posAutomatica = False, llargadaAutomatica = False, tipus = 1):
    #afegir Tub Vertical
    llargada = build_ele.Llargadalinia.value
    if build_ele.PosicioYlinia.value < 0:
        llargada = build_ele.Llargadalinia.value - abs(build_ele.PosicioYlinia.value)
    if build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value > build_ele.ISAmplada.value:
        #llargada = build_ele.Llargadalinia.value - (build_ele.ISAmplada.value - build_ele.PosicioYlinia.value + build_ele.Llargadalinia.value)
        llargada =build_ele.ISAmplada.value - build_ele.PosicioYlinia.value
    build_ele.IntegerISSelectorHor.value = build_ele.IntegerISSelectorHor.value + 1
    if build_ele.IntegerISSelectorHor.value > len(build_ele.dadesTubHor.value)-1:
        set_values_tub_hor(build_ele, build_ele.IntegerISSelectorHor.value, nHorSeleccionat)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Mostrar = True )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(TipusTub = "TUB E" )
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(RotarTub = True)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubInferior = "Tub " + str(tubInf))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(tubSuperior = "Tub " + str(tubSup))
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(LlargadaAut = llargadaAutomatica)
    if tipus == 1:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada)
    elif tipus == 3:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada - 100)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(Llargada =  llargada - 50)
    build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(posAutomatica = posAutomatica)
    if posAutomatica:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value-50)
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = 0)
    else:
        build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplX = build_ele.PosicioXlinia.value )
        if tipus == 3:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value + 50)
        else:
            build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1] = build_ele.dadesTubHor.value[build_ele.IntegerISSelectorHor.value-1]._replace(desplY = build_ele.PosicioYlinia.value)

    return build_ele.IntegerISSelectorHor.value-1

def getLActives(build_ele, posBarraHor):
    LActives = []
    if build_ele.dadesTubHor.value[posBarraHor].provSupEsq:
        LActives.append(2)
    if build_ele.dadesTubHor.value[posBarraHor].provSupDre:
        LActives.append(3)
    if build_ele.dadesTubHor.value[posBarraHor].provInfEsq:
        LActives.append(0)
    if build_ele.dadesTubHor.value[posBarraHor].provInfDre:
        LActives.append(1)
    if build_ele.dadesTubHor.value[posBarraHor].provInfCen:
        LActives.append(4)
    return LActives

def crear_LProvisional(build_ele,j, vectorH1, esExtrem = False, esFinal = False, numL = 0):
    alturaInf = 0

    if build_ele.dadesTubHor.value[j].tubInferior == "TD Inferior":
        alturaInf = 50
    else:
        nHorInf = 0
        if build_ele.dadesTubHor.value[j].tubInferior != "TD Inferior" and build_ele.dadesTubHor.value[j].tubInferior != "TD Superior":
            nHorInf = build_ele.dadesTubHor.value[j].tubInferior
            if len(build_ele.dadesTubHor.value[j].tubInferior) > 3:
                if len(build_ele.dadesTubHor.value[j].tubInferior) == 7:
                    nHorInfCentenes = int(build_ele.dadesTubHor.value[j].tubInferior[-3])
                    nHorInfDecenes = int(build_ele.dadesTubHor.value[j].tubInferior[-2])
                    nHorInfUnitats = int(build_ele.dadesTubHor.value[j].tubInferior[-1])
                    nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.dadesTubHor.value[j].tubInferior) == 6:
                    nHorInfDecenes = int(build_ele.dadesTubHor.value[j].tubInferior[-2])
                    nHorInfUnitats = int(build_ele.dadesTubHor.value[j].tubInferior[-1])
                    nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.dadesTubHor.value[j].tubInferior) == 5:
                    nHorInf = int(build_ele.dadesTubHor.value[j].tubInferior[-1])
        alturaInf = build_ele.dadesTubHor.value[nHorInf].Altura
    Lprovisionals = LProvisional(random.random() * 3600, build_ele.dadesTubHor.value[j].Ample + 12, build_ele.dadesTubHor.value[j].Altura, build_ele.dadesTubHor.value[j].Llargada - 76 , build_ele.dadesTubHor.value[j].Gruix,
                            False, 7, build_ele.BarraLayer.value, esExtrem, esFinal, numL) #matriu

    if not Lprovisionals.is_valid():
        return[]


    Lprovisionals_BrepObject = Lprovisionals.create()
    common_props_Lprovisionals = Lprovisionals.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr01 = "Escaire 75x75 mm"
    if numL == 4:
        attr01 = "Escaire 30x30 mm"


    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "L "),
                            AllplanBaseElements.AttributeString(2103, "L "),
                            AllplanBaseElements.AttributeString(1083, str(attr01)),
                            AllplanBaseElements.AttributeString(1085, "1"),
                             AllplanBaseElements.AttributeString(508, "L Provisional")]

    vectorH1A = AllplanGeo.Matrix3D()
    if build_ele.dadesTubHor.value[j].RotarTub:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(1,0,0))
        vectorH1A.Rotation(z_axis, AllplanGeo.Angle.FromDeg(-90))
        vectorH1A.SetValue(12, vectorH1[12] - 76 - 50)
        vectorH1A.SetValue(13, vectorH1[13] )#+ build_ele.dadesTubHor.value[j].Altura/2 - 17.5/2)
        vectorH1A.SetValue(14, vectorH1[14] + 18.75)#+ alturaInf)
    else:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(0,1,0))
        vectorH1A.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))

        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(1,0,0))
        vectorH1A.Rotation(z_axis, AllplanGeo.Angle.FromDeg(-90))
        vectorH1A.SetValue(12, vectorH1[12] )
        vectorH1A.SetValue(13, vectorH1[13] + 50 + 76)#+ build_ele.dadesTubHor.value[j].Altura/2 - 17.5/2)
        vectorH1A.SetValue(14, vectorH1[14] + 18.75)#+ alturaInf)

    PP_Lprovisional = [PythonPart ("TD_LProvisional", parameter_list = Lprovisionals.get_params_list(),
                                hash_value = Lprovisionals.hash(), python_file = Lprovisionals.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1A, common_props = common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals),
                        common_props_Lprovisionals,
                        Lprovisionals_BrepObject]

    return PP_Lprovisional
