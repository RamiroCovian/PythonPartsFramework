"""
Script for horitzontalPP - Vertical - Group
"""


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
from typing import List, Any, Optional

from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil

from DocumentManager import DocumentManager
#from BuildingElementInputService import BuildingElementInputService
from BuildingElementService import BuildingElementService
from typing import List
from AnyValueByType import AnyValueByType

from .TD_Vertical_PP import PP_TD_Vertical
from .TD_Horitzontal_PP import PP_TD_Horitzontal
from .TD_Horitzontal_Inf_PP import PP_TD_Horitzontal_Inf
from .TD_Horitzontal_Front import TD_Horitzontal_Front
from .TD_CilindreCancam import CilindreCancam
from .TD_CilindreForatXPS import CilindreForatXPS
from .TD_BoxColis import BoxColis
from .TD_BoxForat import BoxForat
from .TD_LProvisional import LProvisional
from .TD_liniaInterior import LiniaInterior
from .TD_CreateText import TextSpline
from .TD_CilindreForat import CilindreForat
from .TD_Horitzontal_reforc import PP_TD_Horitzontal_reforc
from .TD_Premarc import PP_EN_Premarc


from PythonPart import View2D3D, View2D, View3D, PythonPart, PythonPartGroup
from PythonPartUtil import PythonPartUtil


from BuildingElementAttributeList import BuildingElementAttributeList

from HandleProperties import HandleProperties
from HandleDirection import HandleDirection

from CreateElementResult import CreateElementResult
from Utils import LibraryBitmapPreview

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



def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

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


def on_control_event(build_ele, event_id: int):
    nVer = 0
    lennVer = len(build_ele.SelectorTDV.value)
    nVerS = build_ele.SelectorTDV.value[lennVer-1:]

    if len(build_ele.SelectorTDV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorTDV.value[6]
        nVer2 = int(nVerS2)
        nVer = nVer2 *10 + nVer
    else:
        if nVerS != 'r':
            nVer = int(nVerS)
    if event_id == 1000:
        print("Boto Actualitzar pressed")
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
        build_ele.UpdateBalconeraFinestra.value = True
    elif event_id == 1004:

        trobatAnt, posBarraAntBalcFines = buscar_anterior_mes_proper(build_ele, build_ele.PosicioXBalconera.value)
        trobatSeg, posBarraSegBalcFines = buscar_seguent_mes_proper(build_ele, build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value)
        if trobatAnt and trobatSeg:
            for nBarraVert in range(0, build_ele.IntegerTDSelector.value):
                if build_ele.listDesplVerticalsTD.value[nBarraVert].desplXAbs < build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs and build_ele.listDesplVerticalsTD.value[nBarraVert].desplXAbs > build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs:
                    build_ele.listDesplVerticalsTD.value[nBarraVert] = build_ele.listDesplVerticalsTD.value[nBarraVert]._replace(desplXAbs = build_ele.DistanciaEntreTD.value*nBarraVert)
                    build_ele.dadesTDVertTD.value[nBarraVert] = build_ele.dadesTDVertTD.value[nBarraVert]._replace(esProvisional = False)
                    build_ele.dadesTDVertTD.value[nBarraVert] = build_ele.dadesTDVertTD.value[nBarraVert]._replace(BarraSuperior = "TD Superior")
                    build_ele.dadesTDVertTD.value[nBarraVert] = build_ele.dadesTDVertTD.value[nBarraVert]._replace(BarraInferior = "TD Inferior")

            for nBarraHor in range(0, len(build_ele.BarresHorList.value)):
                if build_ele.BarresHorList.value[nBarraHor].BarraInici == "Tub " + str(posBarraAntBalcFines) and build_ele.BarresHorList.value[nBarraHor].BarraFinal == "Tub " + str(posBarraSegBalcFines):
                    build_ele.BarresHorList.value[nBarraHor] = build_ele.BarresHorList.value[nBarraHor]._replace(BarraHor = False)
    #elif event_id == 1005:
    #    doc = DocumentManager.get_instance().document
    #    for model_element in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
    #        if verificar_pythonpart_en_locales(model_element,doc) == None:
    #            print("El PythonPart no está en ningún local")
    elif event_id == 1006:
        pos = build_ele.posIniAutoL.value
        nForats = build_ele.nForatsAutoL.value
        orientacio = build_ele.orientacioAutoL.value
        pos = build_ele.posIniAutoL.value
        posY = build_ele.posYAutoL.value#build_ele.BarraAltura.value/2
        llargada = build_ele.llargadaAutoL.value
        amplada = build_ele.ampladaAutoL.value
        for nForat in range(0, nForats):
            if len(build_ele.ForatsParSUPL.value) <= nForat:
                TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio PosicioY Llargada Amplada Complet LlargadaB AmpladaB MostrarBox ')
                bob = TDCollection( Forat = True,
                                    orientacio = orientacio,
                                    Posicio = pos,
                                    PosicioY = posY,
                                    Llargada = llargada,
                                    Amplada = amplada,
                                    Complet = False,
                                    LlargadaB = 20,
                                    AmpladaB = 10,
                                    MostrarBox = False
                                    )
                build_ele.ForatsParSUPL.value.append(bob)
            else:
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(Forat = True)
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(orientacio = orientacio)
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(Posicio = pos)
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(PosicioY = posY)
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(Llargada = llargada)
                build_ele.ForatsParSUPL.value[nForat] = build_ele.ForatsParSUPL.value[nForat]._replace(Amplada = amplada)
            pos += build_ele.distanciaAutoL.value

    doc = DocumentManager.get_instance().document
    if event_id != 1005:
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
    lennVer = len(build_ele.SelectorTDV.value)
    nVerS = build_ele.SelectorTDV.value[lennVer-1:]

    if len(build_ele.SelectorTDV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorTDV.value[6]
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

def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeo.Point2D, msg_info: AllplanIFW.AddMsgInfo
    ) -> bool:
        """Handles the process mouse message event

        Args:
            mouse_msg: the mouse message.
            pnt      : the input point.
            msg_info : additional message info.

        Returns:
            True/False for success.
        """

        if not bool(self.element_list):
            self.element_list = [
                element
                for element in self.post_element_selection.GetSelectedElements(self.doc)
            ]

            list_adapters = AllplanElementAdapter.BaseElementAdapterList()

            for elem in self.element_list:
                msg = self.get_msg(elem)
                PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
                list_adapters.append(elem)

            AllplanIFW.HighlightService.HighlightElements(list_adapters)
            # AllplanIFW.InputFunctionStarter.RemoveFunction() peta el AllPlan

            return True

        else:
            create_element(self.build_ele, self.doc)

        return True

def get_msg(self, elem: AllplanElementAdapter.BaseElementAdapter):
        msg = ""
        msg += "Name:                " + str(elem.GetDisplayName()) + "\n"
        msg += "Drawing file number: " + str(elem.GetDrawingfileNumber()) + "\n"
        msg += "Element adapter type:" + str(elem.GetElementAdapterType().GetTypeName()) + "\n"
        msg += "Model element UUID:  " + str(elem.GetModelElementUUID()) + "\n"
        msg += "Is 3D element:       " + str(elem.Is3DElement()) + "\n"

        msg += "Geometry:" + "\n"
        modelGeom3D = elem.GetModelGeometry()
        msg += str(modelGeom3D) + "\n"

        msg += "TYPE: " + str(elem.GetArchElementType()) + "\n"


        msg += "ArchGeom: " + str(elem.GetGroundViewArchitectureElementGeometry()) + "\n"

        msg += "PureArchGeom: " + str(elem.GetPureArchitectureElementGeometry()) + "\n"

        msg += "Attributes:" + "\n"

def print_attributes(build_ele: BuildingElement,
                     doc      : AllplanElementAdapter.DocumentAdapter):
    """ print the attributes

    Args:
        build_ele: building element with the parameter properties
        doc:       document of the Allplan drawing files
    """

    attr_manager = AllplanBaseElements.AttributeDataManager

    read_state = AllplanBaseElements.eAttibuteReadState.values[0]

    print("----------------------------------------------------------------------")
    print("Print_Attributes()")
    print()

    for element in AllplanBaseElements.ElementsSelectService.SelectAllElements(doc):
        if not (attributes := AllplanBaseElements.ElementsAttributeService.GetAttributes(element, read_state)):
            continue

        max_name_len = 0

        for attr_id, _ in attributes:
            max_name_len = max(max_name_len, len(attr_manager.GetAttributeName(attr_id)))

        printed = False

        max_name_len += 2

        for attr_id, value in attributes:
            attr_name = AllplanBaseElements.AttributeDataManager.GetAttributeName(attr_id)
            if not printed :#and attr_id == 1083 and value.startswith('T'):
                print(" ID   Name " + " " * (max_name_len - 2) + "Value")
                printed = True

            #if attr_id == 1083 and value.startswith('T'):
            print(f"{attr_id:>4}  {attr_name}{'.' * (max_name_len - len(attr_name))} {value}")

        print()

    #PythonUtility.ShowMessageBox("The attribute log is shown in the Trace window", PythonUtility.MB_OK)


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
        #print("att_A: "         + str(att_A) +         " _ " +  str(horitzontalPP.get_codi_cara_a() == att_A))
        #print("att_B: "           + str(att_B) +         " _ " +  str(horitzontalPP.get_codi_cara_b() == att_B))
        #print("att_C: "           + str(att_C) +         " _ " +  str(horitzontalPP.get_codi_cara_c() == att_C))
        #print("att_D: "           + str(att_D) +         " _ " +  str(horitzontalPP.get_codi_cara_d() == att_D))
        #print("att_A_INV: "       + str(att_A_INV) +     " _ " +  str(horitzontalPP.get_codi_cara_a_inv() == att_A_INV))
        #print("att_B_INV: "       + str(att_B_INV) +     " _ " +  str(horitzontalPP.get_codi_cara_b_inv() == att_B_INV))
        #print("att_C_INV: "       + str(att_C_INV) +     " _ " +  str(horitzontalPP.get_codi_cara_c_inv() == att_C_INV))
        #print("att_D_INV: "       + str(att_D_INV) +     " _ " +  str(horitzontalPP.get_codi_cara_d_inv() == att_D_INV))
        #print("att_pota_inv: "    + str(att_pota_inv) +  " _ " +  str(horitzontalPP.get_codi_pota_inv() == att_pota_inv))
        #print("att_pestanyes: "   + str(att_pestanyes) + " _ " +  str(horitzontalPP.get_codi_pestanyes() == att_pestanyes))
        #print("att_cancam: "      + str(att_cancam) +    " _ " +  str(horitzontalPP.get_codi_cancam() == att_cancam))
        #print("att_mesures: "     + str(att_mesures) +   " _ " +  str(horitzontalPP.get_codi_mesures() == att_mesures))
        #print("att_pota: "        + str(att_pota) +      " _ " +  str(horitzontalPP.get_codi_pota() == att_pota))
        #print("att_seccio: "      + str(att_seccio) +    " _ " +  str(horitzontalPP.get_seccio() == att_seccio))
        #print("att_llargada: "    + str(att_llargada) +  " _ " +  str(horitzontalPP.get_llargada() == att_llargada) + " _ " + str(horitzontalPP.get_llargada()))
        return True, DEN
    return False, DEN

#import NemAll_Python_Geometry as AllplanGeo
#import NemAll_Python_BaseElements as AllplanBasisElements

'''
def detectar_locales(document):
    locales = []
    #for elem in document.GetElements():
    for elem in AllplanBaseElements.ElementsSelectService.SelectAllElements(document):
        read_state = AllplanBaseElements.eAttibuteReadState.values[0]
        # Verificamos si el elemento es un local mediante atributos
        attributes = AllplanBaseElements.ElementsAttributeService.GetAttributes(elem, read_state)
        for attr_id, value in attributes:
            if value == "Room Name" or value == "Room Number":
                locales.append(elem)
            if attr_id == 231:
                print("local: " + str(elem))
                locales.append(elem)
    return locales


def obtener_rango_coordenadas(elemento):
    # Supón que el elemento tiene atributos de posición y tamaño
    base_point = elemento.GetBasePoint()  # Obtener punto base del elemento
    length = elemento.GetAttribute("Length")  # Supón que estas propiedades existen
    width = elemento.GetAttribute("Width")
    height = elemento.GetAttribute("Height")

    # Crear puntos mínimos y máximos en función del punto base y las dimensiones
    min_point = AllplanGeo.Point3D(base_point.X, base_point.Y, base_point.Z)
    max_point = AllplanGeo.Point3D(
        base_point.X + length,
        base_point.Y + width,
        base_point.Z + height
    )
    return min_point, max_point

def esta_dentro_del_local(model_element, local):
    min_local, max_local = obtener_rango_coordenadas(local)
    min_model, max_model = obtener_rango_coordenadas(model_element)

    # Verificar si el PythonPart está dentro del rango del local en todas las coordenadas
    return (
        min_local.X <= min_model.X <= max_local.X and
        min_local.Y <= min_model.Y <= max_local.Y and
        min_local.Z <= min_model.Z <= max_local.Z
    )

def verificar_pythonpart_en_locales(model_element, document):
    locales = detectar_locales(document)
    for local in locales:
        if esta_dentro_del_local(model_element, local):
            nombre_local = local.GetAttribute("Room Name")
            print(f"El PythonPart se encuentra en el local: {nombre_local}")
            return nombre_local
    return None
'''

'''
def detectar_locales(document):
    locales = []

    for elem in AllplanBaseElements.ElementsSelectService.SelectAllElements(document):#document.GetElements():
        # Filtrar elementos que tengan atributos específicos de un local
        if elem.HasAttribute("Room Name") and elem.HasAttribute("Room Number"):
            locales.append(elem)
    return locales

def obtener_extremos(elemento):
    # Obtener la geometría y calcular extremos manualmente
    geometry = elemento.GetGeometry()  # Obtener la geometría del elemento
    min_x, min_y, min_z = float("inf"), float("inf"), float("inf")
    max_x, max_y, max_z = float("-inf"), float("-inf"), float("-inf")

    # Recorrer los puntos de la geometría
    for point in geometry.GetPoints():
        min_x, min_y, min_z = min(min_x, point.X), min(min_y, point.Y), min(min_z, point.Z)
        max_x, max_y, max_z = max(max_x, point.X), max(max_y, point.Y), max(max_z, point.Z)

    return (min_x, min_y, min_z), (max_x, max_y, max_z)

def esta_dentro_del_local(model_element, local):
    min_local, max_local = obtener_extremos(local)
    min_model, max_model = obtener_extremos(model_element)

    # Verificar si el elemento está dentro del área delimitada del local
    dentro_x = min_local[0] <= min_model[0] <= max_local[0] and min_local[0] <= max_model[0] <= max_local[0]
    dentro_y = min_local[1] <= min_model[1] <= max_local[1] and min_local[1] <= max_model[1] <= max_local[1]
    dentro_z = min_local[2] <= min_model[2] <= max_local[2] and min_local[2] <= max_model[2] <= max_local[2]

    return dentro_x and dentro_y and dentro_z

def verificar_pythonpart_en_locales(model_element, document):
    locales = detectar_locales(document)
    for local in locales:
        if esta_dentro_del_local(model_element, local):
            nombre_local = local.GetAttribute("Room Name")
            print(f"El PythonPart se encuentra en el local: {nombre_local}")
            return nombre_local
    print("El PythonPart no está en ningún local")
    return None

'''


def create_pythonpart(build_ele: BuildingElement, doc) -> PythonPart:
    """Create a PythonPart containing cube geometry and some attributes

    Args:
        build_ele: BuildingElement object containing parameter values

    Returns:
        PythonPart object
    """
    result = create_element_class(build_ele, doc)
    #model_elem_list = result["model_elem_list"]
    model_elem_list         = result["elements"           ]
    handle_list             = result["handles"            ]
    model_elem_list_preview = result["preview_elements"   ]
    group_elems             = result["group_elems"        ]
    group_elems_preview     = result["group_elems_preview"]
    placement_point         = result["placement_point"    ]
    multi_placement         = result["multi_placement"    ]
    preview_symbols         = result["preview_symbols"    ]
    build_ele               = result["build_ele"          ]

    return model_elem_list#group_elems
                                #preview_elements=   model_elem_list_preview)
    #return python_part_util.get_pythonpart(build_ele,
    #                                       type_uuid = "23b28875-bc0e-4e8b-b0df-e36d0d1c432c",
    #                                       type_display_name = "PythonPart with attributes")


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


def create_element_class(build_ele, doc, placement_mat = AllplanGeo.Matrix3D() ):
    """
    Create horitzontalPP element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    #del doc
    build_ele.zUnique.value = random.random() * 3600

    drawingService = AllplanBaseElements.DrawingFileService()



    #doc = AllplanElementAdapter.DocumentAdapter()

    crearLlistaVerticals(build_ele)
    crearLlistaHoritzontals(build_ele)
    crearLlistaFullHoritzontals(build_ele)
    crearLlistaReforc(build_ele)

    # Definir nListEncaixVert
    update_mat_nListVert(build_ele)

    #definir els valors inicials i borrar els valors que sobren
    if build_ele.EncaixVertList.value == [] or len(build_ele.EncaixVertList.value) < build_ele.LengthListEncaixVert.value:
        #set_values(build_ele, build_ele.LengthListEncaixVert.value)
        set_values_encaix(build_ele, build_ele.LengthListEncaixVert.value)
    if build_ele.LengthListEncaixVert.value < len(build_ele.EncaixVertList.value):
        remove_values(build_ele, build_ele.LengthListEncaixVert.value)

    nVer = 0
    lennVer = len(build_ele.SelectorTDV.value)
    nVerS = build_ele.SelectorTDV.value[lennVer-1:]
    if len(build_ele.SelectorTDV.value) >= 8:
        nVer = int(nVerS)
        nVerS2 = build_ele.SelectorTDV.value[6]
        nVer2 = int(nVerS2)
        nVer = nVer2 *10 + nVer
    else:
        if nVerS != 'r':
            nVer = int(nVerS)

    group_elems = [] #All elements of suite
    group_elems_preview = [] #
    model_ele_list  = []
    model_ele_list2  = []
    preview_ele_list   = []
    placement_matrix = []
    handle_list = None

    mostrarActual = ""
    nHorInt = 0
    if len(build_ele.SelectorTDHTotal.value) == 7:
        nHorEsqCentenes = int(build_ele.SelectorTDHTotal.value[-3])
        nHorEsqDecenes = int(build_ele.SelectorTDHTotal.value[-2])
        nHorEsqUnitats = int(build_ele.SelectorTDHTotal.value[-1])
        nHorInt = nHorEsqCentenes*100 + nHorEsqDecenes*10 + nHorEsqUnitats
    elif len(build_ele.SelectorTDHTotal.value) == 6:
        nHorEsqDecenes = int(build_ele.SelectorTDHTotal.value[-2])
        nHorEsqUnitats = int(build_ele.SelectorTDHTotal.value[-1])
        nHorInt = nHorEsqDecenes*10 + nHorEsqUnitats
    elif len(build_ele.SelectorTDHTotal.value) == 5:
        nHorInt = int(build_ele.SelectorTDHTotal.value[-1])

    if build_ele.SelectorPPTD.value == 1 and build_ele.SelectorTDHTD.value == "Mes Tubs...":
        mostrar_tubHorInt(build_ele, nHorInt)

    nRef = 0
    if len(build_ele.SelectorReforc.value) > 6:
        if len(build_ele.SelectorReforc.value) == 10:
            nHorInfCentenes = int(build_ele.SelectorReforc.value[-3])
            nHorInfDecenes = int(build_ele.SelectorReforc.value[-2])
            nHorInfUnitats = int(build_ele.SelectorReforc.value[-1])
            nRef = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.SelectorReforc.value) == 9:
            nHorInfDecenes = int(build_ele.SelectorReforc.value[-2])
            nHorInfUnitats = int(build_ele.SelectorReforc.value[-1])
            nRef = nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.SelectorReforc.value) == 8:
            nRef = int(build_ele.SelectorReforc.value[-1])


    if (build_ele.SelectorPPTD.value != 1 and build_ele.SelectorPPAnt.value == 1) or build_ele.SelectorTDHTD.value != "Mes Tubs..." or nHorInt != build_ele.SelectorTDHTotalAnt.value:
        try:
            build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)] = build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)]._replace(Edit = False)
            build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)] = build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)]._replace(acabatEditar = False)
        except Exception as e:
            print("Barra Hor int no Guardada")

    if build_ele.SelectorPPTD.value == 1 and build_ele.SelectorTDHTD.value == "TD Inferior":
        mostrarActual = "TDHINF"
        if len(build_ele.BarresHorList.value) > nHorInt:
            build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Edit = False)
    elif build_ele.SelectorPPTD.value == 1 and build_ele.SelectorTDHTD.value == "TD Superior":
        mostrarActual = "TDHSUP"
        if len(build_ele.BarresHorList.value) > nHorInt:
            build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Edit = False)
    elif build_ele.SelectorPPTD.value == 1 and build_ele.SelectorTDHTD.value == "Mes Tubs...":
        mostrarActual = "TDHMesTubs"
        #print("build_ele.SelectorPPAnt.value: " + str(build_ele.SelectorPPAnt.value))
        #print("build_ele.SelectorTDHTotalAnt.value: " + str(build_ele.SelectorTDHTotalAnt.value))
        #print("build_ele.SelectorTDTipusHor.value: " + str(build_ele.SelectorTDTipusHor.value))
        if build_ele.SelectorPPAnt.value != 1 or nHorInt != build_ele.SelectorTDHTotalAnt.value or build_ele.SelectorTDTipusHor.value != "TDHMesTubs":#mostrarActual != "TDHMesTubs":
            mostrar_valors_hor(build_ele, 0, nHorInt)
            print("mostrar")
            build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Edit = True)
            #build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)] = build_ele.BarresHorList.value[int(build_ele.SelectorTDHTotalAnt.value)]._replace(Edit = False)
        else:
            print("guardar")
            #guardar_valors_hor(build_ele, 0, nHorInt)
    elif build_ele.SelectorPPTD.value == 2:
        mostrarActual = "TDV"+str(nVer)
    elif build_ele.SelectorPPTD.value == 4:
        mostrarActual = "TDR"+str(nRef)
    elif build_ele.SelectorPPTD.value == 3:
        nBalcFin = 0
        lenBalcFin = len(build_ele.SelectorBalcFin.value)
        nBalcFinS = build_ele.SelectorBalcFin.value[lenBalcFin-1:]
        if len(build_ele.SelectorBalcFin.value) >= 11:
            nBalcFin = int(nBalcFinS)
            nBalcFinS2 = build_ele.SelectorBalcFin.value[-2]
            nBalcFin2 = int(nBalcFinS2)
            nBalcFin = nBalcFin2 *10 + nBalcFin
        else:
            if nBalcFinS != ' ' and nBalcFinS != 'n' and nBalcFinS != 'r':
                nBalcFin = int(nBalcFinS)

        if build_ele.SelectorBalcFinAnt.value != nBalcFin:
            mostrar_BalcFine(build_ele, nBalcFin)
        else:
            guardar_valors_BalcFine(build_ele, nBalcFin)
        mostrarActual = "TDBalconeraFinestra"+str(nBalcFin)
        handle_list = create_handles_balconeresFinestres(build_ele)

        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0 , build_ele.PosicioZBalconera.value)
        lineX = create_polyline_interior(build_ele, 0, 0, build_ele.AmpleBalconera.value, True, pointUbi)
        if lineX != []:
            #group_elems.append(lineX[0])
            group_elems_preview.append(lineX[0])
            group_elems_preview.append(lineX[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))

        lineZ = create_polyline_interior(build_ele, 0,0,build_ele.LlargadaBalconera.value, False, pointUbi)
        if lineZ != []:
            #group_elems.append(lineZ[0])
            group_elems_preview.append(lineZ[0])
            group_elems_preview.append(lineZ[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0 , build_ele.PosicioZBalconera.value + build_ele.LlargadaBalconera.value)
        lineX = create_polyline_interior(build_ele, 0, 0, build_ele.AmpleBalconera.value, True, pointUbi)
        if lineX != []:
            #group_elems.append(lineX[0])
            group_elems_preview.append(lineX[0])
            group_elems_preview.append(lineX[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineX[1], lineX[2]))
        pointUbi = AllplanGeo.Point3D(build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value, 0 , build_ele.PosicioZBalconera.value)
        lineZ = create_polyline_interior(build_ele, 0,0,build_ele.LlargadaBalconera.value, False, pointUbi)
        if lineZ != []:
            #group_elems.append(lineZ[0])
            group_elems_preview.append(lineZ[0])
            group_elems_preview.append(lineZ[3])
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[0]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(lineZ[1], lineZ[2]))

        if build_ele.UpdateBalconeraFinestra.value:
            trobatSeg = True
            trobatAnt = True
            if build_ele.VerticalAutoBalc.value:
                trobatAnt, posBarraAntBalcFines = buscar_anterior_mes_proper(build_ele, build_ele.PosicioXBalconera.value)
                trobatSeg, posBarraSegBalcFines = buscar_seguent_mes_proper(build_ele, build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value)

                build_ele.SelectorTDHorEsqBalc.value = "Tub " + str(posBarraAntBalcFines)
                build_ele.SelectorTDHorDreBalc.value = "Tub  " + str(posBarraSegBalcFines)
            else:
                if len(build_ele.SelectorTDHorEsqBalc.value) == 7:
                    nHorEsqCentenes = int(build_ele.SelectorTDHorEsqBalc.value[-3])
                    nHorEsqDecenes = int(build_ele.SelectorTDHorEsqBalc.value[-2])
                    nHorEsqUnitats = int(build_ele.SelectorTDHorEsqBalc.value[-1])
                    nHorEsq = nHorEsqCentenes*100 + nHorEsqDecenes*10 + nHorEsqUnitats
                elif len(build_ele.SelectorTDHorEsqBalc.value) == 6:
                    nHorEsqDecenes = int(build_ele.SelectorTDHorEsqBalc.value[-2])
                    nHorEsqUnitats = int(build_ele.SelectorTDHorEsqBalc.value[-1])
                    nHorEsq = nHorEsqDecenes*10 + nHorEsqUnitats
                elif len(build_ele.SelectorTDHorEsqBalc.value) == 5:
                    nHorEsq = int(build_ele.SelectorTDHorEsqBalc.value[-1])
                posBarraAntBalcFines = nHorEsq

                if len(build_ele.SelectorTDHorDreBalc.value) == 7:
                    nHorDreCentenes = int(build_ele.SelectorTDHorDreBalc.value[-3])
                    nHorDreDecenes = int(build_ele.SelectorTDHorDreBalc.value[-2])
                    nHorDreUnitats = int(build_ele.SelectorTDHorDreBalc.value[-1])
                    nHorDre = nHorDreCentenes*100 + nHorDreDecenes*10 + nHorDreUnitats
                elif len(build_ele.SelectorTDHorDreBalc.value) == 6:
                    nHorDreDecenes = int(build_ele.SelectorTDHorDreBalc.value[-2])
                    nHorDreUnitats = int(build_ele.SelectorTDHorDreBalc.value[-1])
                    nHorDre = nHorDreDecenes*10 + nHorDreUnitats
                elif len(build_ele.SelectorTDHorDreBalc.value) == 5:
                    nHorDre = int(build_ele.SelectorTDHorDreBalc.value[-1])
                posBarraSegBalcFines = nHorDre

                if posBarraSegBalcFines > posBarraAntBalcFines:
                    trobatSeg = True
                    trobatAnt = True
                else:
                    trobatSeg = False
                    trobatAnt = False

            if nVer != posBarraAntBalcFines:
                build_ele.dadesTDVertTD.value[posBarraAntBalcFines] = build_ele.dadesTDVertTD.value[posBarraAntBalcFines]._replace(MostrarTDVertical = True)
                build_ele.dadesTDVertTD.value[posBarraAntBalcFines] = build_ele.dadesTDVertTD.value[posBarraAntBalcFines]._replace(esProvisional = False)
                build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines] = build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconera.value - 80 - build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple)
            else:
                build_ele.MostrarTDVertical.value = True
                build_ele.esProvisional.value = False
                build_ele.desplXVertAbs.value = build_ele.PosicioXBalconera.value - 80 - build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple
            if nVer != posBarraSegBalcFines:
                build_ele.dadesTDVertTD.value[posBarraSegBalcFines] = build_ele.dadesTDVertTD.value[posBarraSegBalcFines]._replace(MostrarTDVertical = True)
                build_ele.dadesTDVertTD.value[posBarraSegBalcFines] = build_ele.dadesTDVertTD.value[posBarraSegBalcFines]._replace(esProvisional = False)
                build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines] = build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines]._replace(desplXAbs = build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value + 80 )#+ build_ele.dadesTDVertTD.value[posBarraSegBalcFines].BarraAmple/2)
            else:
                build_ele.MostrarTDVertical.value = True
                build_ele.esProvisional.value =False
                build_ele.desplXVertAbs.value = build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value + 80 #+ build_ele.dadesTDVertTD.value[posBarraSegBalcFines].BarraAmple/2


            nItermVal = 0
            nIntermitges = []
            #for barresIntermitges in range(posBarraAntBalcFines+1,posBarraSegBalcFines):
            for barresIntermitges in range(1,build_ele.IntegerTDSelector.value-1):
                if build_ele.listDesplVerticalsTD.value[barresIntermitges].desplXAbs > build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs and build_ele.listDesplVerticalsTD.value[barresIntermitges].desplXAbs < build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs:
                    build_ele.dadesTDVertTD.value[barresIntermitges] = build_ele.dadesTDVertTD.value[barresIntermitges]._replace(esProvisional = True)
                    if build_ele.SelectorTDHorSupBalc.value == "TD Superior":
                        build_ele.dadesTDVertTD.value[barresIntermitges] = build_ele.dadesTDVertTD.value[barresIntermitges]._replace(BarraSuperior = build_ele.SelectorTDHorSupBalc.value)
                        build_ele.dadesTDVertTD.value[barresIntermitges] = build_ele.dadesTDVertTD.value[barresIntermitges]._replace(BarraInferior = build_ele.SelectorTDHorInfBalc.value)
                    else:
                        build_ele.dadesTDVertTD.value[barresIntermitges] = build_ele.dadesTDVertTD.value[barresIntermitges]._replace(BarraSuperior = "TD Superior")
                        build_ele.dadesTDVertTD.value[barresIntermitges] = build_ele.dadesTDVertTD.value[barresIntermitges]._replace(BarraInferior = build_ele.SelectorTDHorSupBalc.value)
                    nItermVal += 1
                    nIntermitges.append(barresIntermitges)


            if trobatAnt and trobatSeg:

                posInfBalcFine = build_ele.SelectorTDHorSupBalc.value
                posSupBalcFine = build_ele.SelectorTDHorInfBalc.value
                nHorSup = 0
                nHorInf = 1

                if len(build_ele.SelectorTDHorSupBalc.value) > 3:
                    if len(build_ele.SelectorTDHorSupBalc.value) == 7:
                        nHorSupCentenes = int(build_ele.SelectorTDHorSupBalc.value[-3])
                        nHorSupDecenes = int(build_ele.SelectorTDHorSupBalc.value[-2])
                        nHorSupUnitats = int(build_ele.SelectorTDHorSupBalc.value[-1])
                        nHorSup = nHorSupCentenes*100 + nHorSupDecenes*10 + nHorSupUnitats
                    elif len(build_ele.SelectorTDHorSupBalc.value) == 6:
                        nHorSupDecenes = int(build_ele.SelectorTDHorSupBalc.value[-2])
                        nHorSupUnitats = int(build_ele.SelectorTDHorSupBalc.value[-1])
                        nHorSup = nHorSupDecenes*10 + nHorSupUnitats
                    elif len(build_ele.SelectorTDHorSupBalc.value) == 5:
                        nHorSup = int(build_ele.SelectorTDHorSupBalc.value[-1])
                    #else:
                    #    nHorSup = 0
                if len(build_ele.SelectorTDHorInfBalc.value) > 3:
                    if len(build_ele.SelectorTDHorInfBalc.value) == 7:
                        nHorInfCentenes = int(build_ele.SelectorTDHorInfBalc.value[-3])
                        nHorInfDecenes = int(build_ele.SelectorTDHorInfBalc.value[-2])
                        nHorInfUnitats = int(build_ele.SelectorTDHorInfBalc.value[-1])
                        nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                    elif len(build_ele.SelectorTDHorInfBalc.value) == 6:
                        nHorInfDecenes = int(build_ele.SelectorTDHorInfBalc.value[-2])
                        nHorInfUnitats = int(build_ele.SelectorTDHorInfBalc.value[-1])
                        nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                    elif len(build_ele.SelectorTDHorInfBalc.value) == 5:
                        nHorInf = int(build_ele.SelectorTDHorInfBalc.value[-1])
                    #else:
                    #    nHorInf = 0

                if build_ele.SelectorTDHorInfBalc.value != "TD Inferior" and build_ele.SelectorTDHorInfBalc.value != "TD Superior":
                    build_ele.BarresHorList.value[nHorInf] = build_ele.BarresHorList.value[nHorInf]._replace(BarraHor = True)
                    build_ele.BarresHorList.value[nHorInf] = build_ele.BarresHorList.value[nHorInf]._replace(Posicio = build_ele.PosicioZBalconera.value - 80 - build_ele.dadesTDHortInter.value[nHorInf].Altura/2)
                    build_ele.BarresHorList.value[nHorInf] = build_ele.BarresHorList.value[nHorInf]._replace(BarraInici = "Tub "+str(posBarraAntBalcFines))
                    build_ele.BarresHorList.value[nHorInf] = build_ele.BarresHorList.value[nHorInf]._replace(BarraFinal = "Tub "+str(posBarraSegBalcFines))

                if build_ele.SelectorTDHorSupBalc.value != "TD Superior" and build_ele.SelectorTDHorSupBalc.value != "TD Inferior":
                    build_ele.BarresHorList.value[nHorSup] = build_ele.BarresHorList.value[nHorSup]._replace(BarraHor = True)
                    build_ele.BarresHorList.value[nHorSup] = build_ele.BarresHorList.value[nHorSup]._replace(Posicio = build_ele.PosicioZBalconera.value + build_ele.LlargadaBalconera.value + 80 + build_ele.dadesTDHortInter.value[nHorSup].Altura/2)
                    build_ele.BarresHorList.value[nHorSup] = build_ele.BarresHorList.value[nHorSup]._replace(BarraInici = "Tub "+str(posBarraAntBalcFines))
                    build_ele.BarresHorList.value[nHorSup] = build_ele.BarresHorList.value[nHorSup]._replace(BarraFinal = "Tub "+str(posBarraSegBalcFines))


                nbarraInter = 0
                ultimaBarraPosicionada = 0


                if build_ele.SelectorTDHorInfBalc.value != "TD Inferior" or build_ele.SelectorTDHorSupBalc.value != "TD Superior":
                    for barraNoMostrada in range(posBarraAntBalcFines+1, build_ele.IntegerTDSelector.value-1):
                        if build_ele.listDesplVerticalsTD.value[barraNoMostrada].desplXAbs > build_ele.BarraLlargadaTD.value and nbarraInter < len(nIntermitges):
                            trobat = False
                            posInterior = False
                            for barraInterior in range(0, len(nIntermitges)):
                                if barraNoMostrada == barraInterior :
                                    trobat = True
                            if build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs > build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs and build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs < build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs :#or (build_ele.listDesplVerticalsTD.value[barraNoMostrada].desplXAbs > build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value):
                                posInterior = True

                            if  not trobat and build_ele.SelectorTDHorSupBalc.value != "TD Superior" and build_ele.dadesTDVertTD.value[barraNoMostrada].esProvisional != True:
                                build_ele.listDesplVerticalsTD.value[barraNoMostrada] = build_ele.listDesplVerticalsTD.value[barraNoMostrada]._replace(desplXAbs = build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs)
                                nbarraInter += 1

                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(MostrarTDVertical = True)
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(BarraSuperior = build_ele.SelectorTDHorSupBalc.value)
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(BarraInferior = build_ele.SelectorTDHorInfBalc.value)
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(esProvisional = True)
                                ultimaBarraPosicionada = barraNoMostrada +1


                    nbarraInter = 0

                    #--------posicio quan hi ha dos?????? no funciona
                    for barraNoMostrada in range(ultimaBarraPosicionada, build_ele.IntegerTDSelector.value-1):
                        if build_ele.SelectorTDHorInfBalc.value != "TD Inferior" and nbarraInter < len(nIntermitges):
                            trobat = False
                            posInterior = False
                            for barraInterior in range(0, len(nIntermitges)):
                                if barraNoMostrada == barraInterior:
                                    trobat = True
                            if build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs > build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs and build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs < build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs :#or (build_ele.listDesplVerticalsTD.value[barraNoMostrada].desplXAbs > build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value):
                                posInterior = True

                            if (barraNoMostrada != posBarraAntBalcFines and barraNoMostrada != posBarraSegBalcFines) and not trobat and build_ele.dadesTDVertTD.value[barraNoMostrada].esProvisional != True:#and build_ele.SelectorTDHorSupBalc.value != "TD Superior":
                                build_ele.listDesplVerticalsTD.value[barraNoMostrada] = build_ele.listDesplVerticalsTD.value[barraNoMostrada]._replace(desplXAbs = build_ele.listDesplVerticalsTD.value[nIntermitges[nbarraInter]].desplXAbs)
                                nbarraInter += 1
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(MostrarTDVertical = True)
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(BarraSuperior = build_ele.SelectorTDHorInfBalc.value)
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(BarraInferior = "TD Inferior")
                                build_ele.dadesTDVertTD.value[barraNoMostrada] = build_ele.dadesTDVertTD.value[barraNoMostrada]._replace(esProvisional = True)


            if not trobatAnt:
                print("No hi ha barra Anterior, recoloca la balconera / finestra")
                ctypes.windll.user32.MessageBoxW(0, "No hi ha barra Anterior, recoloca la balconera / finestra " , 1)


            if not trobatSeg:
                print("No hi ha barra Seguent, recoloca la balconera / finestra")
                ctypes.windll.user32.MessageBoxW(0, "No hi ha barra Seguent, recoloca la balconera / finestra " , 1)



            #CREAR PORTA (PREMARC)
            nIncl = 0
            if len(build_ele.SelectorBalcFin.value) > 9:
                if len(build_ele.SelectorBalcFin.value) == 12:
                    nInclCentenes = int(build_ele.SelectorBalcFin.value[-3])
                    nInclDecenes = int(build_ele.SelectorBalcFin.value[-2])
                    nInclUnitats = int(build_ele.SelectorBalcFin.value[-1])
                    nIncl = nInclCentenes*100 + nInclDecenes*10 + nInclUnitats
                elif len(build_ele.SelectorBalcFin.value) == 11:
                    nInclDecenes = int(build_ele.SelectorBalcFin.value[-2])
                    nInclUnitats = int(build_ele.SelectorBalcFin.value[-1])
                    nIncl = nInclDecenes*10 + nInclUnitats
                elif len(build_ele.SelectorBalcFin.value) == 10:
                    nIncl = int(build_ele.SelectorBalcFin.value[-1])
            print("[nIncl]: " + str(nIncl))

            build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(MostrarInclinat = True)
            build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(Mostrar=True)
            #build_ele.dadesBalcFines.value[nIncl] = build_ele.dadesBalcFines.value[nIncl]._replace(Mostrar=True)
            build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Posicio = 0)
            if build_ele.SelectorTDHorInfBalc.value != "TD Inferior" or build_ele.SelectorTDHorSupBalc.value != "TD Superior":
                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Posicio = build_ele.PosicioZBalconera.value - 80 - build_ele.dadesTDHortInter.value[nHorInf].Altura/2)

            if trobatAnt and trobatSeg:

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Llargada = build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs - build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple)
                if build_ele.SelectorTDHorSupBalc.value != "EN Superior" and build_ele.SelectorTDHorSupBalc.value != "EN Inferior":
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.BarresHorList.value[nHorSup].Posicio - build_ele.dadesTDHortInter.value[nHorSup].Altura/2)
                else:
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value/2)

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplX = build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2)
                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplY = build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplYAbs)
            elif not trobatAnt:

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Llargada = build_ele.listDesplVerticalsTD.value[posBarraSegBalcFines].desplXAbs - build_ele.listDesplVerticalsTD.value[0].desplXAbs - build_ele.dadesTDVertTD.value[0].BarraAmple)
                if build_ele.SelectorTDHorSupBalc.value != "EN Superior" and build_ele.SelectorTDHorSupBalc.value != "EN Inferior":
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.BarresHorList.value[nHorSup].Posicio - build_ele.dadesTDHortInter.value[nHorSup].Altura/2)
                else:
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value/2)

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplX = build_ele.listDesplVerticalsTD.value[0].desplXAbs + build_ele.dadesTDVertTD.value[0].BarraAmple)
                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplY = build_ele.listDesplVerticalsTD.value[0].desplYAbs)

            elif not trobatSeg:

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Llargada = build_ele.listDesplVerticalsTD.value[len(IntegerTDSelector)-1].desplXAbs - build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs - build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple)
                if build_ele.SelectorTDHorSupBalc.value != "EN Superior" and build_ele.SelectorTDHorSupBalc.value != "EN Inferior":
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.BarresHorList.value[nHorSup].Posicio - build_ele.dadesTDHortInter.value[nHorSup].Altura/2)
                else:
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value/2)

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplX = build_ele.listDesplVerticalsTD.value[posBarraAntBalcFines].desplXAbs + build_ele.dadesTDVertTD.value[posBarraAntBalcFines].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2)
            else:

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Llargada = build_ele.listDesplVerticalsTD.value[len(IntegerTDSelector)-1].desplXAbs - build_ele.listDesplVerticalsTD.value[0].desplXAbs - build_ele.dadesTDVertTD.value[0].BarraAmple)
                if build_ele.SelectorTDHorSupBalc.value != "EN Superior" and build_ele.SelectorTDHorSupBalc.value != "EN Inferior":
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.BarresHorList.value[nHorSup].Posicio - build_ele.dadesTDHortInter.value[nHorSup].Altura/2)
                else:
                    build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(Altura = build_ele.desplZS.value + build_ele.BarraAlturaInf.value - build_ele.BarraAlturaSup.value/2)

                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplX = build_ele.listDesplVerticalsTD.value[0].desplXAbs + build_ele.dadesTDVertTD.value[0].BarraAmple)
                build_ele.dadesTDInclinades.value[nIncl] = build_ele.dadesTDInclinades.value[nIncl]._replace(desplY = build_ele.listDesplVerticalsTD.value[0].desplYAbs)


            build_ele.UpdateBalconeraFinestra.value = False
        build_ele.SelectorBalcFinAnt.value = nBalcFin
        guardar_valors_incl(build_ele,nBalcFin)



    #build_ele.IntegerTDSelector.value = len(build_ele.nListEncaixVert.value)

    guardar_valors_inici(build_ele,nVer)

    if build_ele.SelectorTDVAnt.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPTD.value and build_ele.SelectorPPTD.value == 2):
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





    #------------------ Definir valors Barra Inferior

    #Afegir Barra Horitzontal al group_elems

    try:
        IntegerTDSelector = build_ele.IntegerTDSelector.value-1
        inici = build_ele.nListBarresHor.value[IntegerTDSelector].Posicio
        final = build_ele.nListBarresHor.value[IntegerTDSelector].Posicio + build_ele.nListBarresHor.value[IntegerTDSelector].nTotal
        llargadaPlus = 0
        for nBarraHorFinal in range(inici, final):
            if nBarraHorFinal >= len(build_ele.BarresHorList.value):
                set_values_barresHor(build_ele, nBarraHorFinal)
            if build_ele.BarresHorList.value[nBarraHorFinal].BarraHor and build_ele.BarresHorList.value[nBarraHorFinal].Longitud >  llargadaPlus:
                llargadaPlus = build_ele.BarresHorList.value[nBarraHorFinal].Longitud + 30
    except Exception as e:
        llargadaPlus = 0
        print("No hi ha dades suficients per llargadaPlus: " + e)

    llargadaInf = build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value
    desplXSeparat = build_ele.desplXI.value
    desplYSeparat = 0
    if build_ele.SepararTDHoritzontalInf.value:
        #build_ele.BarraLlargadaTD.value = build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf
        desplXSeparat = build_ele.listDesplHoritzontalsInf.value[0].desplX
        llargadaInf = build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf + desplXSeparat
        desplYSeparat = build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf
        #build_ele.BarraAmpleInf.value = build_ele.listDesplHoritzontalsInf.value[0].BarraAmpleInf
        #build_ele.BarraAlturaInf.value = build_ele.listDesplHoritzontalsInf.value[0].BarraAlturaInf

    vermellInf = build_ele.FounColorInf.value
    vermellInfPrev = 1
    if  mostrarActual == "TDHINF":
        vermellInfPrev = 4
    if build_ele.SelectorTDHInf.value == "Tub":
        build_ele.FounColorInf.value = 1#Gris
        if build_ele.VermellInf.value:
            #build_ele.FounColor.value = 6#Vermell
            vermellInf = 6

        horitzontalPP = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInf, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value, #ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParINF.value, desplXSeparat, desplYSeparat) #EncaixosPar)

        horitzontalPPPrev = PP_TD_Horitzontal(random.random() * 3601,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, vermellInfPrev, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value, #ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParINF.value, desplXSeparat, desplYSeparat) #EncaixosPar)
        colorPrev = 1

    else:
        horitzontalPP = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value, build_ele.InvertirTDHoritzontalInf.value, build_ele.InvertirTDHoritzontalInf2.value,
                    [],
                    build_ele.IsUseGlobalProp.value, vermellInf, 40001)
        horitzontalPPPrev = PP_TD_Horitzontal_Inf( random.random() * 3601, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value, build_ele.InvertirTDHoritzontalInf.value, build_ele.InvertirTDHoritzontalInf2.value,
                    [],
                    build_ele.IsUseGlobalProp.value, vermellInfPrev, 40001)



    if not horitzontalPP.is_valid():
        return[]

    build_ele.DENInf.value = "T "

    #definir atributs de la Barra Horitzontal Inferior
    common_propsInf = AllplanBaseElements.CommonProperties()
    common_propsInf.GetGlobalProperties()

    horitzontal_Brep = horitzontalPP.create()
    horitzontal_BrepPrev = horitzontalPPPrev.create()
    common_propsInf = horitzontalPP.get_common_props()
    common_propsInfPrev = horitzontalPPPrev.get_common_props()
    common_propsInfPrev.LinkType    = AllplanBasisElements.LinkType.eLinkToRoom

    #if build_ele.VermellInf.value:
    #    common_propsInf.Color = 6#Vermell
    if  mostrarActual == "TDHINF":
        #common_propsInfPrev.Color = 4#Verd
        if not build_ele.SepararTDHoritzontalInf.value:
            handle_list = horitzontalPP.create_handles()
        else:
            handle_list = None

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d_inv()) )

    tubEsIgual = False
    if build_ele.comprovarDEN.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPP)
    if (tubEsIgual):
        build_ele.DENInf.value = DEN

    table_attr_list = [ AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                        AllplanBaseElements.AttributeString(2446, horitzontalPP.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2430, horitzontalPP.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPP.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2431, horitzontalPP.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPP.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2445, horitzontalPP.get_seccio()),
                        AllplanBaseElements.AttributeString(220,  horitzontalPP.get_llargada()),
                        #AllplanBaseElements.AttributeString(220,  str(llargadaInf)),
                        AllplanBaseElements.AttributeString(2455, horitzontalPP.get_llargada()),
                        #AllplanBaseElements.AttributeString(2455, str(llargadaInf)),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPP.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, horitzontalPP.get_llargada()),
                        AllplanBaseElements.AttributeString(1087, "Baix"),
                        AllplanBaseElements.AttributeString(508, "TD")]
    table_viewsInf = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsInf, horitzontal_Brep)])]
    table_viewsInfPrev = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsInfPrev, horitzontal_BrepPrev)])]


    llargadaSup = build_ele.BarraLlargadaTD.value
    if not build_ele.mantenirLlargadaSup.value:
        llargadaSup = build_ele.BarraLlargadaSupInd.value

    desplXSeparatSup = 0
    desplYSeparatSup = 0
    if build_ele.SepararTDHoritzontalSup.value:
        desplXSeparatSup = build_ele.listDesplHoritzontalsSup.value[0].desplX
        llargadaSup = build_ele.listDesplHoritzontalsSup.value[0].BarraLlargadaSup + desplXSeparatSup
        desplYSeparatSup = build_ele.listDesplHoritzontalsSup.value[0].BarraLlargadaSup

    #------------------ Definir valors Barra Superior
    if build_ele.SelectorTDHSup.value == "Tub":
        horitzontalPP2 = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruixSup.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value, desplXSeparatSup, desplYSeparatSup ) #EncaixosPar)
    elif build_ele.SelectorTDHSup.value == "L":
        #femellesSupL = []
        if build_ele.MostrarFemellesSup.value:
            femellesSupL = build_ele.FemellesSUP.value
        horitzontalPP2 = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, build_ele.BarraGruixSupL.value, build_ele.InvertirTDHoritzontalSup.value, build_ele.InvertirTDHoritzontalSup2.value,
                    build_ele.ForatsParSUPL.value,
                    build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, 40001,
                    femellesSupL,
                    build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,
                    retallInici = desplXSeparatSup)
    else:
        horitzontalPP2 = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruixSup.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value, desplXSeparatSup, desplYSeparatSup) #EncaixosPar)
        horitzontalPP2L = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, build_ele.BarraGruixSupL.value, build_ele.InvertirTDHoritzontalSup.value, build_ele.InvertirTDHoritzontalSup2.value,
                    build_ele.ForatsParSUPL.value,
                    build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, 40001,
                    retallInici = desplXSeparatSup)

    if not horitzontalPP2.is_valid():
        return[]


    build_ele.DENSup.value = "T "
    #definir atributs de la Barra Horitzontal Superior
    horitzontal_Brep2 = horitzontalPP2.create()
    common_propsSup = horitzontalPP2.get_common_props()
    #horitzontal_Brep2Prev = horitzontalPP2Prev.create()
    common_propsSupPrev = horitzontalPP2.get_common_props()
    tubEsIgual = False
    if build_ele.comprovarDEN.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPP2)
    if build_ele.VermellSup.value:
        common_propsSup.Color = 6#Vermell
    if (tubEsIgual):
        build_ele.DENSup.value = DEN
    if  mostrarActual == "TDHSUP":
        common_propsSupPrev.Color = 4 #Verd
        #handle_list = horitzontalPP2.create_handles()

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_d_inv()) )



    table_attr_list2 = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                        AllplanBaseElements.AttributeString(2446, horitzontalPP2.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2430, horitzontalPP2.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPP2.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2431, horitzontalPP2.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPP2.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2445, horitzontalPP2.get_seccio()),
                        AllplanBaseElements.AttributeString(220, horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(2455, horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPP2.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(1087, "Dalt"),
                        AllplanBaseElements.AttributeString(508, "TD")]
    table_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2)])]
    table_views2Prev = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSupPrev, horitzontal_Brep2)])]

    if build_ele.SelectorTDHSup.value == "Tub + L":
        horitzontal_Brep2L = horitzontalPP2L.create()
        common_propsL = horitzontalPP2L.get_common_props()
        tubEsIgual2 = False
        if build_ele.comprovarDEN.value:
            tubEsIgual2, DEN = compare_attributes(build_ele, doc, horitzontalPP2L)
        if (tubEsIgual2):
            build_ele.DENSup.value = DEN
        #if  mostrarActual == "TDHSUP":
        if build_ele.VermellSup.value:
            common_propsL.Color = 6 #RED

        cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_d_inv()) )



        table_attr_list2L = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                            AllplanBaseElements.AttributeString(2446, horitzontalPP2L.get_codi_pota_inv()),

                            AllplanBaseElements.AttributeString(2430, horitzontalPP2L.get_codi_pestanyes()),
                            AllplanBaseElements.AttributeString(2435, horitzontalPP2L.get_codi_cancam()),
                            AllplanBaseElements.AttributeString(2431, horitzontalPP2L.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2433, horitzontalPP2L.get_codi_pota()),
                            AllplanBaseElements.AttributeString(2445, horitzontalPP2L.get_seccio()),
                            AllplanBaseElements.AttributeString(220, horitzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, horitzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, horitzontalPP2L.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, horitzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(508, "TD")]
        table_views2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsL, horitzontal_Brep2L)])]



    #Definir valors de la barra Vertical Inicial
    Encaixos, Femelles, Potes, Forats, Colis = get_valors_actuals(build_ele, 0)

    #--------CREATE VERTICAL--------- POSAR DADES MATRIUS [0]
    #chair = PP_TD_Vertical(random.random() * 3600, build_ele.dadesTDVertTD.value[0].BarraAmple+10, build_ele.dadesTDVertTD.value[0].BarraAltura, build_ele.BarraLlargadaVert.value,build_ele.dadesTDVertTD.value[0].Gruix,
    #                        build_ele.IsUseGlobalPropVert.value, build_ele.FounColorVert.value, build_ele.BarraLayerVert.value,
    #                        Colis, Potes, Forats, #matrius ------
    #                        build_ele.dadesTDVertTD.value[0].Ample_forat_femellaVert, build_ele.dadesTDVertTD.value[0].Altura_forat_femellaVert, build_ele.dadesTDVertTD.value[0].Separacio_forat_femellaVert,
    #                        Femelles, #matriu -----
    #                        build_ele.dadesTDVertTD.value[0].posicio_centre_massesVert,
    #                        build_ele.dadesTDVertTD.value[0].IsFirstCancamVert, build_ele.dadesTDVertTD.value[0].Dis1cancamVert,
    #                        build_ele.dadesTDVertTD.value[0].IsSecondCancamVert, build_ele.dadesTDVertTD.value[0].Dis2cancamVert,
    #                        build_ele.dadesTDVertTD.value[0].PestanyaSuperiorVert, build_ele.dadesTDVertTD.value[0].PestanyaInferiorVert,
    #                        Encaixos)
    #
    #chair_brep = chair.create()
    #common_props = chair.get_common_props()
    #if  mostrarActual == "TDV0":
    #    common_props.Color = 6#Vermell
    #    #handle_list = chair.create_handles()
    #chair_attr_list = [AllplanBaseElements.AttributeDouble(AllplanBaseElements.ATTRNR_VOLUME, chair.volume())]
    #chairs_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, chair_brep)])]
    #----------END CREATE VERTICAL----------------------
    matrixPosX = []
    matrixPosY = []
    matrixcentrar = []
    matrixOffsetY = []
    matrixOr = []

    matrixMostrar = []
    matrixMostrarInf = []
    matrixMostrarSup = []
    #for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
    if not build_ele.ReduirTempsCarrega.value:
        for i in range(0,build_ele.IntegerTDSelector.value):
            matrixcentrar.append(build_ele.dadesTDVertTD.value[i].BarraAmple/2)
            matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs )
            matrixPosY.append(build_ele.listDesplVerticalsTD.value[i].desplY)
            matrixMostrar.append(build_ele.dadesTDVertTD.value[i].MostrarTDVertical)
            matrixMostrarInf.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaInferiorVert and build_ele.dadesTDVertTD.value[i].FemellaInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorInf.value and not build_ele.dadesTDVertTD.value[i].EncaixInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaInf))and build_ele.dadesTDVertTD.value[i].BarraInferior == "TD Inferior")
            matrixMostrarSup.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaSuperiorVert and build_ele.dadesTDVertTD.value[i].FemellaSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorSup.value and not build_ele.dadesTDVertTD.value[i].EncaixSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaSup))and build_ele.dadesTDVertTD.value[i].BarraSuperior == "TD Superior")
        listAmples = []
        listAmples2 = []
        listAltures = []
        for TDVert in build_ele.dadesTDVertTD.value:
            listAmples.append(TDVert.BarraAmple - TDVert.Gruix*2)
            listAmples2.append(TDVert.BarraAmple)
            listAltures.append(TDVert.BarraAltura)
        #Crear Encaixos i Femelles en les Barres Horitzontals
        offsetXI = build_ele.desplXI.value
        offsetXS = build_ele.desplXS.value
        if build_ele.SelectorTDHSup.value == "L":
            offsetXS = build_ele.desplXSL.value
        #if (build_ele.desplYI.value != 0.0 and build_ele.desplYI.value > 0.0) or (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):
        if (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):

            if build_ele.invertirEncaixInf.value:
                horitzontalPP.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    if build_ele.dadesTDVertTD.value[i].EncaixInf:
                        matrixOr.append("Esq")
                    else:
                        matrixOr.append("Inf")
                trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append(  build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.dadesTDVertTD.value[i].BarraAltura - build_ele.desplYI.value)
                trans_list = horitzontalPP.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXI, 'Sup', build_ele.BarraLlargadaTD.value)
                horitzontalPP.set_false_femelles()
        elif (build_ele.EncaixHorInf.value and build_ele.desplYI.value <= 0.0):
            if build_ele.invertirEncaixInf.value:
                horitzontalPP.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    if build_ele.dadesTDVertTD.value[i].EncaixInf:
                        matrixOr.append("Esq")
                    else:
                        matrixOr.append("Sup")
                trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value,[], build_ele.desplXI.value)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append( build_ele.BarraAmpleInf.value - build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.desplYI.value)#build_ele.dadesTDVertTD.value[i].BarraAltura

                trans_list = horitzontalPP.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXI, 'Inf', build_ele.BarraLlargadaTD.value )
                horitzontalPP.set_false_femelles()
        else:
            horitzontalPP.set_false_encaix()

            #matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                #matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs )
                matrixOr.append("Esq")
            trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value,[], build_ele.desplXI.value)

        matrixOffsetY = []
        matrixOr = []
        desplYS = build_ele.desplYS.value
        desplXS = build_ele.desplXS.value
        if build_ele.SelectorTDHSup.value == "L":
            desplYS = build_ele.desplYSL.value
            desplXS = build_ele.desplXSL.value

        if build_ele.EncaixHorSup.value and desplYS > 0.0:
            if build_ele.invertirEncaixSup.value:
                horitzontalPP2.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    if build_ele.dadesTDVertTD.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Inf")
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, llargadaSup, desplYS,[], desplXS)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append(  build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.dadesTDVertTD.value[i].BarraAltura - desplYS)#build_ele.dadesTDVertTD.value[i].BarraAltura
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXS, 'Sup', llargadaSup)
                horitzontalPP2.set_false_femelles()
        elif build_ele.EncaixHorSup.value and desplYS <= 0.0:
            if build_ele.invertirEncaixSup.value:
                horitzontalPP2.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    #matrixPosX.append(build_ele.desplXS.value + build_ele.BarraAmpleSup.value - build_ele.listDesplVerticalsTD.value[i].desplX + build_ele.dadesTDVertTD.value[i].BarraAmple)
                    if build_ele.dadesTDVertTD.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Sup")
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, llargadaSup, desplYS,[], desplXS)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append(build_ele.BarraAmpleSup.value + desplYS + build_ele.listDesplVerticalsTD.value[i].desplY )
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXS, 'Inf', llargadaSup)
                horitzontalPP2.set_false_femelles()
        else:
            horitzontalPP2.set_false_encaix()
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixOr.append("Dre")
            if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXS, matrixOr, build_ele.Ample_forat_femellaVert.value,llargadaSup, desplYS,[], desplXS)

    #--build_ele.IntegerTDSelector.value = len(trans_list)

    update_mat_nListVert(build_ele)

    contadorPPH = 0
    contadorPPV = 0
    contadorPPI = 0

    vectorH1 = AllplanGeo.Matrix3D()
    vectorH1.SetValue(12, build_ele.desplXI.value )
    vectorH1.SetValue(13, build_ele.desplYI.value)

    TranslationFather = vectorH1
    TranslationFather.SetValue(12, placement_mat[12] + vectorH1[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH1[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH1[14])
    vectorH1  = TranslationFather

    common_propsObjectInf = AllplanBaseElements.CommonProperties()
    common_propsObjectInf.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    #common_propsObject.Color = 31 #blanc

    common_propsObjectInf2 = AllplanBaseElements.CommonProperties()
    common_propsObjectInf2.Layer = 40055#(KN_XPS_CAVITAT)
    #common_propsObject2.Color = 31 #blanc

    ampleInferior = 60
    colorCavitat = getColorCavitat(ampleInferior)
    common_propsObjectInf.Color = colorCavitat
    common_propsObjectInf2.Color = colorCavitat
    #horitzontalPPOBject = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, build_ele.BarraLlargadaTD.value, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
    horitzontalPPOBject = PP_TD_Horitzontal(random.random() * 3600,0, ampleInferior, build_ele.BarraAlturaInf.value+10, llargadaInf+10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectInf.Color, common_propsObjectInf.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparat)

    #horitzontalPPOBjectA = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, build_ele.BarraLlargadaTD.value, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
    horitzontalPPOBjectA = PP_TD_Horitzontal(random.random() * 3600,0, ampleInferior, build_ele.BarraAlturaInf.value+10, llargadaInf+10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectInf2.Color, common_propsObjectInf2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparat)

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                            #AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)
                            ]

    horitzontal_BrepObject = horitzontalPPOBject.create()
    horitzontal_BrepObjectA = horitzontalPPOBjectA.create()

    vectorH1C = AllplanGeo.Matrix3D()
    vectorH1C.SetValue(12, vectorH1[12] - 5)
    vectorH1C.SetValue(13, vectorH1[13])
    vectorH1C.SetValue(14, vectorH1[14] - 5)


    table_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectInf, horitzontal_BrepObject)])]
    table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectInf2, horitzontal_BrepObjectA)])]


    if build_ele.MostrarTDHoritzontalInf.value :
        #horitzontalPP with translate has to be the firsrt element because of group modification
        # Define python part for TDHoritzontal

        group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP.get_params_list(),
                                    hash_value = horitzontalPP.hash(), python_file = horitzontalPP.filename(),
                                    views = table_viewsInf, matrix = vectorH1, common_props = common_propsInf, attribute_list = table_attr_list))
        group_elems_preview.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPPPrev.get_params_list(),
                                    hash_value = horitzontalPPPrev.hash(), python_file = horitzontalPPPrev.filename(),
                                    views = table_viewsInfPrev, matrix = vectorH1, common_props = common_propsInfPrev, attribute_list = table_attr_list))

        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsInf, horitzontal_Brep))
        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsInfPrev, group_elems[len(group_elems)-1]))
        model_ele_list2.append([AllplanBasisElements.ModelElement3D(common_propsInfPrev, horitzontal_BrepPrev)])
        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsInf, horitzontal_Brep))
        #placement_matrix.append(vectorH1)

        if build_ele.MostrarRecessInf.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
                                        hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
                                        views = table_views_object, matrix = vectorH1C, common_props = common_propsObjectInf, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
                                        hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
                                        views = table_views_object, matrix = vectorH1C, common_props = common_propsObjectInf, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf, horitzontal_BrepObject))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf, horitzontal_BrepObject))

        if build_ele.MostrarCavitatInf.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectA.get_params_list(),
                                        hash_value = horitzontalPPOBjectA.hash(), python_file = horitzontalPPOBjectA.filename(),
                                        views = table_views_object_2, matrix = vectorH1C, common_props = common_propsObjectInf2, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectA.get_params_list(),
                                        hash_value = horitzontalPPOBjectA.hash(), python_file = horitzontalPPOBjectA.filename(),
                                        views = table_views_object_2, matrix = vectorH1C, common_props = common_propsObjectInf2, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf2, horitzontal_BrepObjectA))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf2, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectInf, horitzontal_BrepObjectA))

        for i in range(0, len(build_ele.ColisParINF.value)):
            if build_ele.ColisParINF.value[i].Colis and build_ele.ColisParINF.value[i].MostrarBox and build_ele.ColisParINF.value[i].Posicio < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
                boxsColis = createColisInf(build_ele,0, i)
                if boxsColis != []:
                    group_elems.append(boxsColis)
                    group_elems_preview.append(boxsColis)
                    boxCavi = createColisCavitatHorInf(build_ele, 0, i)
                    if boxCavi != []:
                        for caviLayersColis in boxCavi:
                            group_elems.append(caviLayersColis)
                            group_elems_preview.append(caviLayersColis)

                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(boxsColis[1], boxsColis[2]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(boxsColis[1], boxsColis[2]))

        for i in range(0, len(build_ele.PotaParINF.value)):
            #if build_ele.PotaParINF.value[i].Forat and build_ele.ForatsParINF.value[i].orientacio  == "Inf" and build_ele.ForatsParINF.value[i].Posicio < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
            if build_ele.PotaParINF.value[i].Pota and build_ele.PotaParINF.value[i].Posicio < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
                cilindreForat = createCilindreInf(build_ele,i)
                if cilindreForat != [] and len(cilindreForat) > 2 :
                    group_elems.append(cilindreForat[0])
                    group_elems_preview.append(cilindreForat[0])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(cilindreForat[1], cilindreForat[2]))
                    group_elems.append(cilindreForat[3])
                    group_elems_preview.append(cilindreForat[3])

                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(cilindreForat[1], cilindreForat[2]))

        if build_ele.SepararTDHoritzontalInf.value:
            if build_ele.listDesplHoritzontalsInf.value[0].mostrarLiniaA:
                punt_central = desplXSeparat + build_ele.listDesplHoritzontalsInf.value[0].desplX + build_ele.listDesplHoritzontalsInf.value[0].BarraAlturaInf/2
                pointUbi = AllplanGeo.Point3D(desplXSeparat, vectorH1[13] + build_ele.listDesplHoritzontalsInf.value[0].BarraAmpleInf/2 + build_ele.listDesplHoritzontalsInf.value[0].desplLinA, vectorH1[14] +  build_ele.listDesplHoritzontalsInf.value[0].BarraAlturaInf/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsInf.value[0].BarraAmpleInf,build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf, True, pointUbi, int(linia), build_ele.SelectorLayerInf.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
            if build_ele.listDesplHoritzontalsInf.value[0].mostrarLiniaB:
                punt_central = desplXSeparat + build_ele.listDesplHoritzontalsInf.value[0].desplX + build_ele.listDesplHoritzontalsInf.value[0].BarraAlturaInf/2
                pointUbi = AllplanGeo.Point3D(desplXSeparat, vectorH1[13] + build_ele.listDesplHoritzontalsInf.value[0].BarraAmpleInf/2 + build_ele.listDesplHoritzontalsInf.value[0].desplLinB, vectorH1[14] +  build_ele.listDesplHoritzontalsInf.value[0].BarraAlturaInf/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsInf.value[0].BarraAmpleInf,build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf, True, pointUbi, int(linia), build_ele.SelectorLayerInf.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
        else:
            if build_ele.mostrarLiniaIntInf1.value:
                punt_central = vectorH1[12] + build_ele.desplXI.value + build_ele.BarraAlturaInf.value/2
                pointUbi = AllplanGeo.Point3D(vectorH1[12], vectorH1[13] + build_ele.BarraAmpleInf.value/2 + build_ele.desplLiniaIntInf1.value, vectorH1[14] + build_ele.BarraAlturaInf.value/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleInf.value, build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value, True, pointUbi, int(linia), build_ele.SelectorLayerInf.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
            if build_ele.mostrarLiniaIntInf2.value:
                punt_central = vectorH1[12] + build_ele.desplXI.value + build_ele.BarraAlturaInf.value/2
                pointUbi = AllplanGeo.Point3D(vectorH1[12], vectorH1[13] + build_ele.BarraAmpleInf.value/2 + build_ele.desplLiniaIntInf2.value, vectorH1[14] + build_ele.BarraAlturaInf.value/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleInf.value, build_ele.BarraLlargadaTD.value, True, pointUbi, int(linia), build_ele.SelectorLayerInf.value)
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


    contadorPPH += 1

    #Posicionar Barra Superior
    vectorH2 = AllplanGeo.Matrix3D()
    vectorH2.SetValue(12, build_ele.desplXS.value)
    vectorH2.SetValue(13, build_ele.desplYS.value)
    if build_ele.SelectorTDHSup.value == "L":
        vectorH2.SetValue(12, build_ele.desplXSL.value)
        vectorH2.SetValue(13, build_ele.desplYSL.value)

    llargadaVertical = build_ele.BarraLlargadaVert.value


    #if build_ele.desplYI.value == 0.0 or build_ele.EncaixHorInf.value:
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

    vectorH2.SetValue(14, llargadaVertical + 1 )

    TranslationFather = vectorH2
    TranslationFather.SetValue(12, placement_mat[12] + vectorH2[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH2[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH2[14])
    vectorH2  = TranslationFather


    common_propsObjectSup = AllplanBaseElements.CommonProperties()
    common_propsObjectSup2 = AllplanBaseElements.CommonProperties()
    common_propsObjectSup.Layer = 40054#(KN_XPS_RECESS)
    common_propsObjectSup2.Layer = 40055#(KN_XPS_CAVITAT)
    ampleSupCavitat = build_ele.BarraAmpleSup.value
    alturaSupCavitat = build_ele.BarraAlturaSup.value
    if build_ele.SelectorTDHSup.value == "L":
        ampleSupCavitat = build_ele.BarraAmpleSupL.value
        alturaSupCavitat = build_ele.BarraAlturaSupL.value

    colorCavitat = getColorCavitat(ampleSupCavitat)
    common_propsObjectSup.Color = colorCavitat
    common_propsObjectSup2.Color = colorCavitat
    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleSupCavitat, alturaSupCavitat+10, llargadaSup + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup.Color, common_propsObjectSup.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparatSup)
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, ampleSupCavitat, alturaSupCavitat+10, llargadaSup + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup2.Color, common_propsObjectSup2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparatSup)
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()

    vectorH2C = AllplanGeo.Matrix3D()
    vectorH2C.SetValue(12, vectorH2[12]-5)
    vectorH2C.SetValue(13, vectorH2[13])
    vectorH2C.SetValue(14, vectorH2[14]-5)


    if build_ele.MostrarTDHoritzontalSup.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A)])]

        if build_ele.MostrarRecessSup.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))

        if build_ele.MostrarCavitatSup.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A))


        #Afegir Barra Horitzontal al group_elems
        group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP2.get_params_list(),
                                    hash_value = horitzontalPP2.hash(), python_file = horitzontalPP2.filename(),
                                    views = table_views2, matrix = vectorH2, common_props = common_propsSup, attribute_list = table_attr_list2))
        group_elems_preview.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP2.get_params_list(),
                                    hash_value = horitzontalPP2.hash(), python_file = horitzontalPP2.filename(),
                                    views = table_views2Prev, matrix = vectorH2, common_props = common_propsSupPrev, attribute_list = table_attr_list2))
        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2))
        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsSup, group_elems[len(group_elems)-1]))
        model_ele_list2.append([AllplanBasisElements.ModelElement3D(common_propsSupPrev, horitzontal_Brep2)])
        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2))
        #placement_matrix.append(vectorH2)
        #Afegir Barra Horitzontal al group_elems
        if build_ele.SelectorTDHSup.value == "Tub + L":
            vectorH2L = AllplanGeo.Matrix3D()
            vectorH2L.SetValue(12, build_ele.desplXSL.value + placement_mat[12])
            vectorH2L.SetValue(13, build_ele.desplYSL.value + placement_mat[13])
            vectorH2L.SetValue(14, vectorH2[14] + build_ele.BarraAlturaSup.value + 1)
            group_elems.append(PythonPart ("PP_TD_Horitzontal_L", parameter_list = horitzontalPP2L.get_params_list(),
                                        hash_value = horitzontalPP2L.hash(), python_file = horitzontalPP2L.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props = common_propsL, attribute_list = table_attr_list2L))
            group_elems_preview.append(PythonPart ("PP_TD_Horitzontal_L", parameter_list = horitzontalPP2L.get_params_list(),
                                        hash_value = horitzontalPP2L.hash(), python_file = horitzontalPP2L.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props = common_propsL, attribute_list = table_attr_list2L))
            cav, cav_prev = crear_cavitat_hor(build_ele, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, vectorH2L, desplXSeparatSup)
            for e in cav:
                group_elems.append(e)
            for e_prev in cav_prev:
                group_elems_preview.append(e_prev)

        if  build_ele.IsFirstCancamSUP.value:
            if build_ele.posicio_centre_massesSUP.value  + build_ele.Dis1cancamSUP.value/ 2 < llargadaSup:
                firstCancam = True
                secondCancam = False
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
        if  build_ele.IsSecondCancamSUP.value:
            if build_ele.posicio_centre_massesSUP.value  + build_ele.Dis2cancamSUP.value/ 2 < llargadaSup:
                firstCancam = False
                secondCancam = True
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)

        for i in range(0, len(build_ele.ColisParSUP.value)):
            if build_ele.ColisParSUP.value[i].Colis and build_ele.ColisParSUP.value[i].MostrarBox and build_ele.ColisParSUP.value[i].Posicio < llargadaSup:
                boxsColis = createColis(build_ele, llargadaVertical, i)
                group_elems.append(boxsColis)
                group_elems_preview.append(boxsColis)
                cavitatColis = createColisCavitatHorSup(build_ele, llargadaVertical, i)
                if cavitatColis != []:
                    for cavCapa in cavitatColis:
                        group_elems.append(cavCapa)
                        group_elems_preview.append(cavCapa)



        if build_ele.SepararTDHoritzontalSup.value:
            if build_ele.listDesplHoritzontalsSup.value[0].mostrarLiniaA:
                punt_central = placement_mat[12] + desplXSeparatSup + build_ele.listDesplHoritzontalsSup.value[0].desplX + build_ele.listDesplHoritzontalsSup.value[0].BarraAlturaSup/2
                pointUbi = AllplanGeo.Point3D(desplXSeparatSup + vectorH2[12], vectorH2[13] + build_ele.listDesplHoritzontalsSup.value[0].BarraAmpleSup/2 + build_ele.listDesplHoritzontalsSup.value[0].desplLinA, vectorH2[14] +  build_ele.listDesplHoritzontalsSup.value[0].BarraAlturaSup/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsSup.value[0].BarraAmpleSup,build_ele.listDesplHoritzontalsSup.value[0].BarraLlargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
            if build_ele.listDesplHoritzontalsSup.value[0].mostrarLiniaB:
                punt_central = placement_mat[12] + desplXSeparatSup + build_ele.listDesplHoritzontalsSup.value[0].desplX + build_ele.listDesplHoritzontalsSup.value[0].BarraAlturaSup/2
                pointUbi = AllplanGeo.Point3D(desplXSeparatSup + vectorH2[12], vectorH2[13] + build_ele.listDesplHoritzontalsSup.value[0].BarraAmpleSup/2 + build_ele.listDesplHoritzontalsSup.value[0].desplLinB, vectorH2[14] +  build_ele.listDesplHoritzontalsSup.value[0].BarraAlturaSup/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsSup.value[0].BarraAmpleSup,build_ele.listDesplHoritzontalsSup.value[0].BarraLlargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
        else:
            if build_ele.mostrarLiniaIntSup1.value:
                punt_central = vectorH2[12] + build_ele.desplXS.value + build_ele.BarraAlturaSup.value/2
                pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSup.value/2 + build_ele.desplLiniaIntSup1.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSup.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)

                if build_ele.SelectorTDHSup.value == "L":
                    punt_central = vectorH2[12] + build_ele.desplXSL.value + build_ele.BarraAlturaSupL.value/2
                    pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSupL.value/2 + build_ele.desplLiniaIntSup1.value , vectorH2[14] + build_ele.BarraAlturaSupL.value/2)
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSupL.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
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
                pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSup.value/2 + build_ele.desplLiniaIntSup2.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSup.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if build_ele.SelectorTDHSup.value == "L":
                    punt_central = vectorH2[12] + build_ele.desplXSL.value + build_ele.BarraAlturaSupL.value/2
                    pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSupL.value/2 + build_ele.desplLiniaIntSup2.value , vectorH2[14] + build_ele.BarraAlturaSupL.value/2)
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSupL.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)


                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))



    #Crear Barres verticals
    if not build_ele.ReduirTempsCarrega.value:
        try:

            while build_ele.IntegerTDSelector.value > len(trans_list):
                trans_matrix = AllplanGeo.Matrix3D()
                trans_matrix.Translate(AllplanGeo.Vector3D(build_ele.listDesplVerticalsTD.value[len(trans_list)-1].desplXAbs, build_ele.listDesplVerticalsTD.value[len(trans_list)-1].desplYAbs, 0))
                trans_list.append(trans_matrix)
            # Define python parts for TDVertical
            while len(trans_list) > build_ele.IntegerTDSelector.value:
                trans_list.pop()
            j = 0

            #for matrix in trans_list:
            for matrix in trans_list:

                TranslationFather = matrix
                TranslationFather.SetValue(12, placement_mat[12] + matrix[12])
                TranslationFather.SetValue(13, placement_mat[13] + matrix[13])
                TranslationFather.SetValue(14, placement_mat[14] + matrix[14])
                matrix  = TranslationFather


                i = j-1

                if j >= len(build_ele.dadesTDVertTD.value):
                    set_values(build_ele, j)
                lennVer = len(build_ele.SelectorTDV.value)

                if build_ele.dadesTDVertTD.value[j].esProvisional:
                    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(EncaixSup= True)
                    #build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(EncaixInf= True)
                    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaSuperiorVert = False)
                    #if build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior":
                    #    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaInferiorVert = True)
                    #else:
                    #    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaInferiorVert = False)
                    if j == nVer:
                        build_ele.encaixSup.value = True
                        #build_ele.encaixInf.value = True
                        #if build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior":
                        #    build_ele.PestanyaInferiorVert.value = True
                        #else:
                        #    build_ele.PestanyaInferiorVert.value = False

                #Definir valors de la barra Vertical j
                Encaixos, Femelles, Potes, Forats, Colis = get_valors_actuals(build_ele, j)

                for nForat in range(0,len(Forats)):
                    if Forats[nForat].Forat and build_ele.dadesTDVertTD.value[j].MostrarTDVertical and build_ele.listDesplVerticalsTD.value[j].desplXAbs <= build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:#and Forats[nForat].MostrarBox
                        if createBoxForat(build_ele, j, Forats, nForat) != []:
                            if Forats[nForat].MostrarBox:
                                group_elems.append(createBoxForat(build_ele, j, Forats, nForat))
                                group_elems_preview.append(createBoxForat(build_ele, j, Forats, nForat))
                            for cavVert in (createBoxForatCavitat(build_ele, j, Forats, nForat)):
                                group_elems.append(cavVert)
                                group_elems_preview.append(cavVert)
                            for cavVert in (createBoxForatCavitatXPS(build_ele, j, Forats, nForat)):
                                group_elems.append(cavVert)
                                group_elems_preview.append(cavVert)


                ampleAnt = 0
                ampleSeg = 0
                if j > 0:
                    ampleAnt = build_ele.dadesTDVertTD.value[j-1].BarraAmple
                    ampleSeg = build_ele.dadesTDVertTD.value[j].BarraAmple

                #----------------------------Posicionar Absolut Vertical---------------

                mostrar = True
                nHor1 = 0
                while mostrar and nHor1 < len(build_ele.BarresHorList.value):
                    if build_ele.BarresHorList.value[nHor1].Edit:
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
                #build_ele.listDesplVerticalsTD.value[j] =  build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = matrix[12] + build_ele.listDesplVerticalsTD.value[j].desplX )
                #build_ele.listDesplVerticalsTD.value[j] =  build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = matrix[13] )


                #if j == nVer and mostrar:
                mostrarInterior = False
                for nValueEdit in range(0,len(build_ele.BarresHorList.value)):
                    if build_ele.BarresHorList.value[nValueEdit].acabatEditar and not  build_ele.BarresHorList.value[nValueEdit].Edit:
                        if j == nVer:
                            build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplXAbs
                            build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                            build_ele.BarresHorList.value[nValueEdit] = build_ele.BarresHorList.value[nValueEdit]._replace(acabatEditar= False)
                    if build_ele.BarresHorList.value[nValueEdit].Edit:
                        mostrarInterior = True
                '''
                for nValueEdit in range(0,len(build_ele.BarresVertListToShow.value)):
                    if build_ele.BarresVertListToShow.value[nValueEdit].acabatEditar and not build_ele.BarresVertListToShow.value[nValueEdit].Edit:
                        build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplXAbs
                        build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                    if build_ele.BarresVertListToShow.value[nValueEdit].Edit:
                        mostrarInterior = True
                '''
                if not mostrarInterior:
                    if build_ele.DistanciaEntreTDAnt.value != build_ele.DistanciaEntreTD.value :
                        #build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = matrix[12])#no modificar posicio al canviar la distancia
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.DistanciaEntreTD.value * j )
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = matrix[13] - placement_mat[13])
                        if j == nVer and build_ele.SelectorPPTD.value == 2:
                            build_ele.desplXVertAbs.value = matrix[12] - placement_mat[12]
                            build_ele.desplYVertAbs.value = matrix[13] - placement_mat[13]
                    elif build_ele.BarraLlargadaAnt.value != build_ele.BarraLlargadaTD.value and j != len(trans_list)-1 and build_ele.listDesplVerticalsTD.value[j].desplXAbs == 0 and j != 0 :
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = matrix[12] - placement_mat[12])
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = 0)

                    else:
                        if j == nVer and build_ele.SelectorPPTD.value == 2 and build_ele.SelectorPPAnt.value == 2:
                            #si no esta mostrat
                            #if "TDVer"+str(nVer) == build_ele.SelectorTDV.value:
                            '''
                            if nVer == 0 :#and build_ele.desplXVertAbs.value == 0:
                                #build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplXAbs
                                #build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                build_ele.desplXVertAbs.value = build_ele.DistanciaEntreTD.value * nVer
                                build_ele.desplYVertAbs.value = 0
                            else:
                            '''
                            build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.desplXVertAbs.value)
                            build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = build_ele.desplYVertAbs.value)
                        if j == nVer and build_ele.SelectorPPTD.value == 2 and build_ele.SelectorPPAnt.value != 2:
                            '''
                            if nVer == 0: # and build_ele.desplXVertAbs.value == 0:
                                #build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplXAbs
                                #build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                build_ele.desplXVertAbs.value = build_ele.DistanciaEntreTD.value * nVer
                                build_ele.desplYVertAbs.value = build_ele.desplYVertAbs.value
                            else:
                            '''
                            build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplXAbs
                            build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                            build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.listDesplVerticalsTD.value[j].desplXAbs)
                            build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = build_ele.listDesplVerticalsTD.value[j].desplYAbs)
                        else:
                            if j == 0 :#and build_ele.listDesplVerticalsTD.value[j].desplXAbs == 0:

                                build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.DistanciaEntreTD.value * j)
                                build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = build_ele.listDesplVerticalsTD.value[j].desplYAbs)
                                build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = build_ele.listDesplVerticalsTD.value[j].desplXAbs - matrix[12] - placement_mat[12])
                                build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplY = build_ele.listDesplVerticalsTD.value[j].desplYAbs)
                            else:
                                if j == nVer and build_ele.SelectorPPTD.value == 2 and build_ele.SelectorPPAnt.value != 2:
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.desplXVertAbs.value)
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = build_ele.desplYVertAbs.value)
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = build_ele.desplXVertAbs.value - matrix[12] - placement_mat[12])
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplY = build_ele.desplYVertAbs.value - matrix[13] - placement_mat[13])
                                else:
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.listDesplVerticalsTD.value[j].desplXAbs)
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplYAbs = build_ele.listDesplVerticalsTD.value[j].desplYAbs)
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = build_ele.listDesplVerticalsTD.value[j].desplXAbs - matrix[12] - placement_mat[12])
                                    build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplY = build_ele.listDesplVerticalsTD.value[j].desplYAbs - matrix[13] - placement_mat[13])

                    if j == nVer and build_ele.SelectorPPTD.value == 2:
                        build_ele.desplXVert.value = build_ele.desplXVertAbs.value - matrix[12] - placement_mat[12]
                        build_ele.desplYVert.value = build_ele.desplYVertAbs.value #- matrix[13]
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = build_ele.desplXVertAbs.value - matrix[12] - placement_mat[12])
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplY = build_ele.desplYVertAbs.value - matrix[13] - placement_mat[13])
                    else:
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = build_ele.listDesplVerticalsTD.value[j].desplXAbs )#- matrix[12])
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplY = build_ele.listDesplVerticalsTD.value[j].desplYAbs )#- matrix[13])


                    #if j == build_ele.IntegerTDSelector.value-1:

                    if j == len(trans_list)-1:
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplXAbs = build_ele.BarraLlargadaTD.value - build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2)
                        build_ele.listDesplVerticalsTD.value[j] = build_ele.listDesplVerticalsTD.value[j]._replace(desplX = 0)


                    #----------------------------END Posicionar Absolut Vertical---------------

                #matrix.SetValue(12, matrix[12] - ampleAnt/2 - ampleSeg/2)
                matrix0 = AllplanGeo.Matrix3D()
                #matrix0.SetValue(12, matrix[12] + build_ele.listDesplVerticalsTD.value[j].desplX)
                matrix0.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs- (build_ele.dadesTDVertTD.value[j].BarraAmple-build_ele.dadesTDVertTD.value[0].BarraAmple)/2 )

                #matrix0.SetValue(13, matrix[13] )
                matrix0.SetValue(13, build_ele.listDesplVerticalsTD.value[j].desplYAbs )
                matrix.SetValue(13,build_ele.listDesplVerticalsTD.value[j].desplYAbs)

                matrix0.SetValue(14, build_ele.BarraAlturaInf.value + 1)

                llargadaVertical = build_ele.BarraLlargadaVert.value

                posHorInfAux = 0
                alturaInf = 0
                if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior" and build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Superior":
                    nHorInf = build_ele.dadesTDVertTD.value[j].BarraInferior
                    if len(build_ele.dadesTDVertTD.value[j].BarraInferior) > 3:
                        if len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 7:
                            nHorInfCentenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-3])
                            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 6:
                            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 5:
                            nHorInf = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                        #tubVert = build_ele.dadesTDVertTD.value[j].BarraInferior[-3]
                        #tubHor = build_ele.dadesTDVertTD.value[j].BarraInferior[-1]
                        #nHorInf = int(tubVert) * NombreBarresHorInt + (int(tubHor)-1)

                        if build_ele.dadesTDVertTD.value[j].EncaixInf:
                            matrix0.SetValue(14, build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 )
                            alturaInf = 0
                        else:
                            matrix0.SetValue(14, build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2 )
                            alturaInf = build_ele.dadesTDHortInter.value[nHorInf].Altura

                TranslationFather = matrix0
                TranslationFather.SetValue(12, placement_mat[12] + matrix0[12])
                TranslationFather.SetValue(13, placement_mat[13] + matrix0[13])
                TranslationFather.SetValue(14, placement_mat[14] + matrix0[14])
                matrix0  = TranslationFather

                #Definir Posicio dels encaixoS es funcio si el deslpaçament es > 0 o < 0
                #Definir si posa encaix o femella
                crearFemellesxEncaixInf = False
                desplInf = "Esq"
                desplSup = "Esq"
                trobatInf = False

                for nBarraInfEnc in range(0,build_ele.nBarresTDHoritzontalInf.value):
                    if nBarraInfEnc >= len(build_ele.listDesplHoritzontalsInf.value):
                        add_baraInferior(build_ele, nBarraInfEnc)
                    if not trobatInf and build_ele.SepararTDHoritzontalInf.value and build_ele.listDesplVerticalsTD.value[j].desplXAbs + build_ele.dadesTDVertTD.value[j].BarraAmple >= build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].desplX and build_ele.listDesplVerticalsTD.value[j].desplXAbs - build_ele.dadesTDVertTD.value[j].BarraAmple  <=  build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].desplX + build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].BarraLlargadaInf:
                        #encaixosAux.append(bob)
                        trobatInf = True
                #if build_ele.desplYI.value != 0.0 or build_ele.EncaixHorInf.value:#or (build_ele.dadesTDVertTD.value[j].BarraAltura.value > build_ele.BarraAmpleInf.value):
                if build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior":
                    if build_ele.EncaixHorInf.value and not build_ele.dadesTDVertTD.value[j].EncaixInf :#or (build_ele.dadesTDVertTD.value[j].BarraAltura.value > build_ele.BarraAmpleInf.value):
                        crearFemellesxEncaixInf = True
                        matrix0.SetValue(14, matrix[14])
                        llargadaVertical += build_ele.BarraAlturaInf.value
                        build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaInferiorVert = False)
                        if build_ele.desplYI.value > 0.0 :
                            desplInf = "Esq"
                        else:
                            desplInf = "Dre"
                    else:
                        crearFemellesxEncaixInf = False

                        if not trobatInf and build_ele.SepararTDHoritzontalInf.value:
                            matrix0.SetValue(14, 0 )
                            crearFemellesxEncaixInf = False
                        #build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaInferiorVert = True)

                crearFemellesxEncaixSup = False
                #if build_ele.desplYS.value != 0.0 :
                if build_ele.EncaixHorSup.value and not build_ele.dadesTDVertTD.value[j].EncaixSup :

                    crearFemellesxEncaixSup = True
                    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaSuperiorVert = False)
                    if build_ele.desplYS.value > 0.0 :
                        desplSup = "Esq"
                    else:
                        desplSup = "Dre"
                else:
                    crearFemellesxEncaixSup = False
                    llargadaVertical -= build_ele.BarraAlturaSup.value
                    #build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(PestanyaSuperiorVert = True)

                BarrallargadaVert = build_ele.BarraLlargadaVert.value

                nHorInf = nHorSup = 0
                if build_ele.dadesTDVertTD.value[j].LlargadaAut:

                    posHorSup = build_ele.BarraLlargadaVert.value
                    posHorInf = 0

                    if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior" or build_ele.dadesTDVertTD.value[j].BarraSuperior != "TD Superior":
                        if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior":
                            if len(build_ele.dadesTDVertTD.value[j].BarraInferior) > 3:
                                if len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 7:
                                    nHorInfCentenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-3])
                                    nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                                    nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                                    nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                                elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 6:
                                    nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                                    nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                                    nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                                elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 5:
                                    nHorInf = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                                if not build_ele.dadesTDVertTD.value[j].EncaixInf:
                                    posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2
                                else:
                                    posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 #+1 #- build_ele.BarraAlturaInf.value/2# + build_ele.BarraAlturaSup.value/2 + 1.25
                        else:
                            if build_ele.dadesTDVertTD.value[j].EncaixInf:
                                posHorInf = build_ele.BarraAlturaInf.value
                        if build_ele.dadesTDVertTD.value[j].BarraSuperior != "TD Superior":
                            if len(build_ele.dadesTDVertTD.value[j].BarraSuperior) > 3:
                                if len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 7:
                                    nHorSupCentenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-3])
                                    nHorSupDecenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-2])
                                    nHorSupUnitats = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                                    nHorSup = nHorSupCentenes*100 + nHorSupDecenes*10 + nHorSupUnitats
                                elif len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 6:
                                    nHorSupDecenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-2])
                                    nHorSupUnitats = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                                    nHorSup = nHorSupDecenes*10 + nHorSupUnitats
                                elif len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 5:
                                    nHorSup = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                                #tubVert = build_ele.dadesTDVertTD.value[j].BarraSuperior[-3]
                                #tubHor = build_ele.dadesTDVertTD.value[j].BarraSuperior[-1]
                                #nHorSup = int(tubVert) * NombreBarresHorInt + (int(tubHor)-1)
                                if not build_ele.dadesTDVertTD.value[j].EncaixSup:
                                    posHorSup = build_ele.BarresHorList.value[nHorSup].Posicio + build_ele.dadesTDHortInter.value[nHorSup].Altura/2 - posHorInf
                                else:
                                    posHorSup = build_ele.BarresHorList.value[nHorSup].Posicio - build_ele.dadesTDHortInter.value[nHorSup].Altura/2 - posHorInf #- 1 #+ build_ele.BarraAlturaInf.value#/2 #+ build_ele.BarraAlturaSup.value/2 + 1.25
                        else:
                            if not build_ele.dadesTDVertTD.value[j].EncaixSup:
                                posHorSup = vectorH2[14] - placement_mat[14] - posHorInf + build_ele.BarraAlturaSup.value
                            else:
                                posHorSup = vectorH2[14] - placement_mat[14] -posHorInf

                        #if build_ele.dadesTDVertTD.value[j].EncaixInf and build_ele.dadesTDVertTD.value[j].EncaixSup:
                        #    posHorSup -= build_ele.dadesTDHortInter.value[nHorSup].Altura/2 - build_ele.dadesTDHortInter.value[nHorInf].Altura/2

                        if build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior" and build_ele.dadesTDVertTD.value[j].BarraSuperior != "TD Superior" and not build_ele.dadesTDVertTD.value[j].EncaixSup and build_ele.dadesTDVertTD.value[j].EncaixInf:
                            posHorSup -= 1

                    else:
                        posHorSup = vectorH2[14] - placement_mat[14]
                        if not build_ele.dadesTDVertTD.value[j].EncaixSup:
                            posHorSup = posHorSup + build_ele.BarraAlturaSup.value #- posHorInf
                        else:
                            posHorSup = posHorSup  #- build_ele.BarraAlturaSup.value - posHorInf

                        if not build_ele.dadesTDVertTD.value[j].EncaixInf:
                            posHorSup = posHorSup #+ build_ele.BarraAlturaInf.value - posHorInf
                        else:
                            posHorSup = posHorSup - build_ele.BarraAlturaInf.value - 1 #- posHorInf



                    BarrallargadaVert = posHorSup + alturaInf
                    if not trobatInf and build_ele.SepararTDHoritzontalInf.value and build_ele.dadesTDVertTD.value[j].EncaixInf:
                        BarrallargadaVert += build_ele.BarraAlturaInf.value
                    build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(BarraAlcada = BarrallargadaVert)


                else:
                    #calcular llargada fins la Horitzontal Adient
                    BarrallargadaVert = build_ele.dadesTDVertTD.value[j].BarraAlcada

                if build_ele.dadesTDVertTD.value[j].FounColor== 0:
                    build_ele.dadesTDVertTD.value[j]= build_ele.dadesTDVertTD.value[j]._replace(FounColor = 1)



                TDV_Int = PP_TD_Vertical(random.random() * 3600, build_ele.dadesTDVertTD.value[j].BarraAmple, build_ele.dadesTDVertTD.value[j].BarraAltura, BarrallargadaVert,build_ele.dadesTDVertTD.value[j].Gruix,
                                            #build_ele.IsUseGlobalPropVert.value, build_ele.FounColorVert.value, build_ele.BarraLayerVert.value,
                                            build_ele.IsUseGlobalPropVert.value, build_ele.dadesTDVertTD.value[j].FounColor, build_ele.BarraLayerVert.value,
                                            Colis, Potes, Forats, #matrius -------------------------------
                                            build_ele.dadesTDVertTD.value[j].Ample_forat_femellaVert, build_ele.dadesTDVertTD.value[j].Altura_forat_femellaVert, build_ele.dadesTDVertTD.value[j].Separacio_forat_femellaVert,
                                            Femelles, #matriu Femelles -------------------------------------
                                            build_ele.dadesTDVertTD.value[j].posicio_centre_massesVert,
                                            build_ele.dadesTDVertTD.value[j].IsFirstCancamVert, build_ele.dadesTDVertTD.value[j].Dis1cancamVert,
                                            build_ele.dadesTDVertTD.value[j].IsSecondCancamVert, build_ele.dadesTDVertTD.value[j].Dis2cancamVert,
                                            build_ele.dadesTDVertTD.value[j].PestanyaSuperiorVert, build_ele.dadesTDVertTD.value[j].PestanyaInferiorVert,
                                            Encaixos)#Encaixos

                common_propsObjectVert = AllplanBaseElements.CommonProperties()
                common_propsObjectVert2 = AllplanBaseElements.CommonProperties()
                common_propsObjectVert.Layer = 40054#(KN_XPS_RECESS)
                common_propsObjectVert2.Layer = 40055#(KN_XPS_CAVITAT)
                colorCavitat = getColorCavitat(build_ele.dadesTDVertTD.value[j].BarraAltura)
                common_propsObjectVert.Color = colorCavitat
                common_propsObjectVert2.Color = colorCavitat
                verticalPPOBject5 = PP_TD_Vertical(random.random() * 3600,build_ele.dadesTDVertTD.value[j].BarraAmple +10 , build_ele.dadesTDVertTD.value[j].BarraAltura, BarrallargadaVert + 10,0,
                                        False,  common_propsObjectVert.Color,  common_propsObjectVert.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        [], [],[], #ColisPar, PotaPar, #matrius
                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                        [], #Femelles, #matriu
                                        0, #posicio_centre_masses,
                                        False, 0, #IsFirstCancam, Dis1cancam,
                                        False, 0, #IsSecondCancam, Dis2cancam,
                                        False, False,
                                        [])
                verticalPPOBject5A = PP_TD_Vertical(random.random() * 3600,build_ele.dadesTDVertTD.value[j].BarraAmple +10 , build_ele.dadesTDVertTD.value[j].BarraAltura, BarrallargadaVert + 10 ,0,
                                        False,  common_propsObjectVert2.Color,  common_propsObjectVert2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
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


                    offsetYAnt = []
                    offsetY = []



                    #for nbarraHorAnterior in range(0,build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal):
                    for nbarraHorAnterior in range(0,len(build_ele.BarresHorList.value)-1):

                        if nbarraHorAnterior >= len(build_ele.BarresHorList.value):
                            set_values_barresHor(build_ele, nbarraHorAnterior)
                        if nbarraHorAnterior >= len(build_ele.dadesTDHortInter.value):
                            set_valors_hor_ini(build_ele, 0, nbarraHorAnterior)

                        if len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal) >= 5 :
                            if len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal) == 5:
                                NBarraFinal = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-1]
                                NBarraFinal = int(NBarraFinal)
                            elif len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal) == 6:
                                NBarraFinalUnitats = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-1]
                                NBarraFinalDecenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-2]
                                NBarraFinal = int(NBarraFinalDecenes)*10 + int(NBarraFinalUnitats)
                            elif len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal) == 7:
                                NBarraFinalUnitats = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-1]
                                NBarraFinalDecenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-2]
                                NBarraFinalCentenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraFinal[-3]
                                NBarraFinal = int(NBarraFinalCentenes) * 100 + int(NBarraFinalDecenes)*10 + int(NBarraFinalUnitats)
                            else:
                                NBarraFinal = 0
                        else:
                            NBarraFinal = 0
                        if len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici) >= 5 :
                            if len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici) == 5:
                                NBarraInici = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-1]
                                NBarraInici = int(NBarraInici)
                            elif len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici) == 6:
                                NBarraIniciUnitats = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-1]
                                NBarraIniciDecenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-2]
                                NBarraInici = int(NBarraIniciDecenes)*10 + int(NBarraIniciUnitats)
                            elif len(build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici) == 7:
                                NBarraIniciUnitats = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-1]
                                NBarraIniciDecenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-2]
                                NBarraIniciCentenes = build_ele.BarresHorList.value[nbarraHorAnterior].BarraInici[-3]
                                NBarraInici = int(NBarraIniciCentenes) * 100 + int(NBarraIniciDecenes)*10 + int(NBarraIniciUnitats)
                            else:
                                NBarraInici = 0
                        else:
                            NBarraInici = 0

                        sumatoriAlçada = 0

                        if trobatInf and build_ele.dadesTDVertTD.value[NBarraInici].EncaixInf:
                            sumatoriAlçada = build_ele.BarraAlturaInf.value

                        if NBarraFinal == j:
                            posInf = build_ele.BarraAlturaInf.value
                            if build_ele.dadesTDVertTD.value[NBarraFinal].BarraInferior != "TD Inferior":
                                posInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 - 1
                                if  not build_ele.dadesTDVertTD.value[NBarraFinal].EncaixInf:
                                    posInf = build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2
                            else:
                                if  not build_ele.dadesTDVertTD.value[NBarraFinal].EncaixInf:
                                    posInf =  0
                            if not build_ele.EncaixHorInf.value or build_ele.dadesTDVertTD.value[NBarraFinal].EncaixInf:
                                listFemellesAnt.append([build_ele.BarresHorList.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorList.value[nbarraHorAnterior].Posicio - posInf -1 , build_ele.BarresHorList.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorList.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInter.value[nbarraHorAnterior].Altura ])

                            else:
                                listFemellesAnt.append([build_ele.BarresHorList.value[nbarraHorAnterior].BarraHor , build_ele.BarresHorList.value[nbarraHorAnterior].Posicio + sumatoriAlçada - posInf, build_ele.BarresHorList.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorList.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInter.value[nbarraHorAnterior].Altura ])
                            offsetYAnt.append(build_ele.dadesTDHortInter.value[nbarraHorAnterior].Ample/2 - build_ele.dadesTDVertTD.value[NBarraInici].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInter.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsTD.value[NBarraFinal].desplYAbs)



                        if NBarraInici == j:
                            posInf = build_ele.BarraAlturaInf.value
                            if build_ele.dadesTDVertTD.value[NBarraInici].BarraInferior != "TD Inferior":
                                posInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 - 1
                                if  not build_ele.dadesTDVertTD.value[NBarraInici].EncaixInf:
                                    posInf = build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2
                            else:
                                if  not build_ele.dadesTDVertTD.value[NBarraInici].EncaixInf:
                                    posInf =  0
                            if not build_ele.EncaixHorInf.value or build_ele.dadesTDVertTD.value[NBarraInici].EncaixInf:
                                listFemellesAct.append([build_ele.BarresHorList.value[nbarraHorAnterior].BarraHor and not build_ele.BarresHorList.value[nbarraHorAnterior].Xapa , build_ele.BarresHorList.value[nbarraHorAnterior].Posicio - posInf -1 , build_ele.BarresHorList.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorList.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInter.value[nbarraHorAnterior].Altura ])

                            else:
                                listFemellesAct.append([build_ele.BarresHorList.value[nbarraHorAnterior].BarraHor and not build_ele.BarresHorList.value[nbarraHorAnterior].Xapa , build_ele.BarresHorList.value[nbarraHorAnterior].Posicio - posInf + sumatoriAlçada, build_ele.BarresHorList.value[nbarraHorAnterior].Orientacio, build_ele.BarresHorList.value[nbarraHorAnterior].AutoLongitud, build_ele.dadesTDHortInter.value[nbarraHorAnterior].Altura ])
                            offsetY.append(build_ele.dadesTDHortInter.value[nbarraHorAnterior].Ample/2 - build_ele.dadesTDVertTD.value[NBarraInici].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInter.value[nbarraHorAnterior].desplY - build_ele.listDesplVerticalsTD.value[NBarraInici].desplYAbs)


                separacioFemellaInf = build_ele.BarraAlturaInf.value
                separacioFemellaSup = build_ele.BarraAlturaSup.value
                separacioFemellaInt = build_ele.BarraAlturaVert.value - build_ele.BarraGruixVert.value * 2

                if j > 0:
                    if build_ele.dadesTDVertTD.value[j-1].MostrarTDVertical:
                        n = 1
                    else:
                        n = 2
                    iniciAnt = build_ele.nListBarresHor.value[j-n].Posicio
                    finalAnt = build_ele.nListBarresHor.value[j-n].Posicio + build_ele.nListBarresHor.value[j-n].nTotal
                    #for nBarraHor in range(iniciAnt,finalAnt):
                    #    offsetYAnt.append(build_ele.dadesTDHortInter.value[nBarraHor].Ample/2 - build_ele.dadesTDVertTD.value[j].Ample_forat_femellaVert/2 + build_ele.dadesTDHortInter.value[nBarraHor].desplY - build_ele.listDesplVerticalsTD.value[j].desplYAbs)

                if not trobatInf and build_ele.SepararTDHoritzontalInf.value:
                    crearFemellesxEncaixInf = False


                FemellesAux = TDV_Int.actualitzar_femelles_TDH(listFemellesAnt, listFemellesAct, j, offsetY, offsetYAnt, crearFemellesxEncaixInf and build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior", desplInf, crearFemellesxEncaixSup and build_ele.dadesTDVertTD.value[j].BarraSuperior == "TD Superior", desplSup, separacioFemellaInf , separacioFemellaSup, separacioFemellaInt)
                build_ele.DENVert.value = "T "


                estaEditant = False
                for posBarraHor in range(0, len(build_ele.BarresHorList.value)-1):#recorrer totes les Barres Horitzontals de cada vertical
                    testEditBarraHorInterior = build_ele.BarresHorList.value[posBarraHor].Edit
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
                            if len(build_ele.BarresHorList.value[posBarraHor].BarraFinal) >= 5 :
                                if len(build_ele.BarresHorList.value[posBarraHor].BarraFinal) == 5:
                                    NBarraFinal = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-1]
                                    NBarraFinal = int(NBarraFinal)
                                elif len(build_ele.BarresHorList.value[posBarraHor].BarraFinal) == 6:
                                    NBarraFinalUnitats = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-1]
                                    NBarraFinalDecenes = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-2]
                                    NBarraFinal = int(NBarraFinalDecenes)*10 + int(NBarraFinalUnitats)
                                elif len(build_ele.BarresHorList.value[posBarraHor].BarraFinal) == 7:
                                    NBarraFinalUnitats = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-1]
                                    NBarraFinalDecenes = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-2]
                                    NBarraFinalCentenes = build_ele.BarresHorList.value[posBarraHor].BarraFinal[-3]
                                    NBarraFinal = int(NBarraFinalCentenes) * 100 + int(NBarraFinalDecenes)*10 + int(NBarraFinalUnitats)
                                else:
                                    NBarraFinal = 0
                            else:
                                NBarraFinal = 0
                            if len(build_ele.BarresHorList.value[posBarraHor].BarraInici) >= 5 :
                                if len(build_ele.BarresHorList.value[posBarraHor].BarraInici) == 5:
                                    NBarraInici = build_ele.BarresHorList.value[posBarraHor].BarraInici[-1]
                                    NBarraInici = int(NBarraInici)
                                elif len(build_ele.BarresHorList.value[posBarraHor].BarraInici) == 6:
                                    NBarraIniciUnitats = build_ele.BarresHorList.value[posBarraHor].BarraInici[-1]
                                    NBarraIniciDecenes = build_ele.BarresHorList.value[posBarraHor].BarraInici[-2]
                                    NBarraInici = int(NBarraIniciDecenes)*10 + int(NBarraIniciUnitats)
                                elif len(build_ele.BarresHorList.value[posBarraHor].BarraInici) == 7:
                                    NBarraIniciUnitats = build_ele.BarresHorList.value[posBarraHor].BarraInici[-1]
                                    NBarraIniciDecenes = build_ele.BarresHorList.value[posBarraHor].BarraInici[-2]
                                    NBarraIniciCentenes = build_ele.BarresHorList.value[posBarraHor].BarraInici[-3]
                                    NBarraInici = int(NBarraIniciCentenes) * 100 + int(NBarraIniciDecenes)*10 + int(NBarraIniciUnitats)
                                else:
                                    NBarraInici = 0
                            else:
                                NBarraInici = 0
                            if posBarraHor >= len(build_ele.BarresHorList.value):
                                set_values_barresHor(build_ele, posBarraHor)


                            if NBarraInici < len(trans_list)  and build_ele.BarresHorList.value[posBarraHor].BarraHor:
                                if NBarraFinal+1 < len(trans_list):
                                    if not build_ele.BarresHorList.value[posBarraHor].AutoLongitud:
                                        llargada = build_ele.BarresHorList.value[posBarraHor].Longitud
                                    else:
                                        if build_ele.dadesTDVertTD.value[NBarraFinal].MostrarTDVertical :#and not build_ele.BarresVertList.value[j*NombreBarresVertInt].BarraVert:
                                            llargada = build_ele.listDesplVerticalsTD.value[NBarraFinal].desplXAbs - build_ele.dadesTDVertTD.value[NBarraFinal].BarraAmple/2 - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInter.value[posBarraHor].desplX
                                        elif not build_ele.dadesTDVertTD.value[NBarraFinal].MostrarTDVertical and build_ele.BarresVertList.value[(NBarraFinal)*NombreBarresVertInt].BarraVert:
                                            llargada = build_ele.BarresVertList.value[(NBarraFinal)*NombreBarresVertInt].PosicioAbs - build_ele.dadesTDVertInter.value[(NBarraFinal)*NombreBarresVertInt].BarraAmple/2 - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInter.value[posBarraHor].desplX
                                        else:
                                            llargada = build_ele.listDesplVerticalsTD.value[NBarraFinal+1].desplXAbs - build_ele.dadesTDVertTD.value[NBarraFinal+1].BarraAmple/2 - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInter.value[posBarraHor].desplX

                                else:
                                    if not build_ele.BarresHorList.value[posBarraHor].AutoLongitud:
                                        llargada = build_ele.BarresHorList.value[posBarraHor].Longitud
                                    else:
                                        if NBarraFinal == len(trans_list)-1:
                                            llargada = build_ele.listDesplVerticalsTD.value[NBarraFinal].desplXAbs - build_ele.dadesTDVertTD.value[NBarraFinal].BarraAmple/2 - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDHortInter.value[posBarraHor].desplX
                                        else:
                                            llargada = build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple

                                if llargada <= 0:
                                    llargada = 30
                                build_ele.BarresHorList.value[posBarraHor] = build_ele.BarresHorList.value[posBarraHor]._replace(Longitud = llargada)

                                testEditBarraHorInterior = build_ele.BarresHorList.value[posBarraHor].Edit

                                if testEditBarraHorInterior :#and nVer == j:
                                    #si esta buit
                                    while len(build_ele.dadesTDHortInter.value) <= j * NombreBarresHorInt + (posBarraHor - inici)*NombreBarresHorInt:
                                        set_valors_hor_ini(build_ele, j, len(build_ele.dadesTDHortInter.value))

                                    if build_ele.dadesTDHortInter.value[posBarraHor].acabatEditar == False:
                                        build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(acabatEditar = True)
                                    #si no estan mostrats
                                    if  build_ele.BarresHorList.value[posBarraHor].acabatEditar == False and build_ele.BarresHorList.value[posBarraHor].Edit == True: #al clicar a edit
                                        #mostrar valors
                                        mostrar_valors_hor(build_ele, 0, posBarraHor)
                                        build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(estaEditant = True)
                                        build_ele.BarresHorList.value[posBarraHor] = build_ele.BarresHorList.value[posBarraHor]._replace(acabatEditar = True)

                                    #guardar valors
                                    guardar_valors_hor(build_ele, 0, posBarraHor)
                                else:
                                    if len(build_ele.dadesTDHortInter.value) <= j * NombreBarresHorInt + (posBarraHor - inici)*3:
                                        set_valors_hor_ini(build_ele, 0, posBarraHor )
                                    if build_ele.dadesTDHortInter.value[posBarraHor].acabatEditar == True :#and nVer == j:
                                        #guardar valors
                                        #guardar_valors_hor(build_ele, j, posBarraHor - inici)
                                        #print("mostrar_valors_actuals 5")
                                        if build_ele.SelectorPPTD.value == 2:
                                            mostrar_valors_actuals(build_ele, nVer)

                                        build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(acabatEditar = False)
                                        build_ele.BarresHorList.value[posBarraHor] = build_ele.BarresHorList.value[posBarraHor]._replace(acabatEditar = False)
                                if len(build_ele.dadesTDHortInter.value) <= j * NombreBarresHorInt + 3  :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.ColisHorInt.value) <= posBarraHor * 3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.PotesHorInt.value) <= posBarraHor * 3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.ForatsHorInt.value) <= posBarraHor *10  + 10 :#j * NombreBarresHorInt + (posBarraHor - inici) *10  + 10 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor)
                                if len(build_ele.FemellesHorInt.value) <= posBarraHor * 3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)
                                if len(build_ele.FemellesHorIntAux.value) <= j*20+ ((posBarraHor - inici + 2)*4 )+ 3 :
                                    set_valors_hor_femelles2(build_ele, j, posBarraHor-inici)
                                if len(build_ele.EncaixHorInt.value) <= posBarraHor * 3  + 3 :
                                    set_valors_hor_ini(build_ele, j, posBarraHor - inici)


                                colis = [build_ele.ColisHorInt.value[posBarraHor * 3 + 0],
                                         build_ele.ColisHorInt.value[posBarraHor * 3 + 1],
                                         build_ele.ColisHorInt.value[posBarraHor * 3 + 2]]
                                potes = [build_ele.PotesHorInt.value[posBarraHor * 3 + 0],
                                         build_ele.PotesHorInt.value[posBarraHor * 3 + 1],
                                         build_ele.PotesHorInt.value[posBarraHor * 3 + 2]]
                                forats = [build_ele.ForatsHorInt.value[posBarraHor *10 + 0],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 1],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 2],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 3],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 4],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 5],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 6],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 7],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 8],
                                          build_ele.ForatsHorInt.value[posBarraHor *10 + 9]]
                                femelles = [build_ele.FemellesHorInt.value[posBarraHor * 3 + 0],
                                            build_ele.FemellesHorInt.value[posBarraHor * 3 + 1],
                                            build_ele.FemellesHorInt.value[posBarraHor * 3 + 2],]
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 0],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 1],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 2],
                                            #build_ele.FemellesHorIntAux.value[j*20+ ((posBarraHor - inici + 2)*4 )+ 3]  ]
                                encaixos = [build_ele.EncaixHorInt.value[posBarraHor * 3 + 0],
                                            build_ele.EncaixHorInt.value[posBarraHor * 3 + 1],
                                            build_ele.EncaixHorInt.value[posBarraHor * 3 + 2]]

                                for nBarraVertical in range(0, len(build_ele.dadesTDVertTD.value)-1):
                                    if build_ele.dadesTDVertTD.value[nBarraVertical].BarraInferior == "Tub " +str(posBarraHor):#Numeracio malament #+ str(j*(posBarraHor - inici)):
                                        #pos = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2 -0.5
                                        pos = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs + build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDVertTD.value[nBarraVertical].BarraAmple/2 -0.5 - build_ele.dadesTDHortInter.value[posBarraHor].desplX

                                        orientInfA =  "Esq"
                                        desplY = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplYAbs
                                        desplYInf = build_ele.dadesTDHortInter.value[posBarraHor].desplY
                                        puntCentralY = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 + desplY
                                        puntCentralYInf = build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + desplYInf

                                        posFemellaY = puntCentralY - puntCentralYInf + 7.5
                                        posFemellaY = desplY - desplYInf + build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 - 7.5
                                        if build_ele.dadesTDVertTD.value[nBarraVertical].EncaixInf:
                                            orientInfA =  "Esq"
                                            #posFemellaY = puntCentralY - puntCentralYInf + 7.5
                                            posFemellaY = puntCentralY - puntCentralYInf/2 + 7.5
                                            posFemellaY = puntCentralY - puntCentralYInf + 7.5
                                            posFemellaY = desplY - desplYInf + build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 - 7.5
                                            #posFemellaY = puntCentralY - 7.5
                                        else:
                                            desplY = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplYAbs
                                            desplYInf = build_ele.dadesTDHortInter.value[posBarraHor].desplY
                                            puntCentralY = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 + desplY
                                            puntCentralYInf = build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + desplYInf
                                            posFemellaY = 0.0

                                            if (puntCentralY > puntCentralYInf) :
                                                orientInfA = "Sup"
                                            else:
                                                orientInfA = "Inf"


                                        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
                                        bob = TDHorCollection(Femella = build_ele.dadesTDVertTD.value[nBarraVertical].MostrarTDVertical and build_ele.dadesTDVertTD.value[nBarraVertical].FemellaInf,
                                                            FemellaOr = orientInfA,
                                                            PosFemellaX = pos,
                                                            PosFemellaY = posFemellaY,
                                                            Separacio_forat_femella = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAmple - 3.0)
                                        femelles.append(bob)
                                    #if build_ele.dadesTDVertTD.value[nBarraVertical].BarraSuperior == "Tub " + str(j) + "."+ str(posBarraHor - inici+1):
                                    if build_ele.dadesTDVertTD.value[nBarraVertical].BarraSuperior == "Tub " + str(posBarraHor): #+ str(j*(posBarraHor - inici)):
                                        #pos = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[nBarraVertical].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2 -0.5
                                        #pos = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplXAbs - build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2 -0.5
                                        pos = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplXAbs - (build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs + build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2) - build_ele.dadesTDVertTD.value[nBarraVertical].BarraAmple/2 -0.5 - build_ele.dadesTDHortInter.value[posBarraHor].desplX

                                        desplY = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplYAbs
                                        desplYSup = build_ele.dadesTDHortInter.value[posBarraHor].desplY
                                        puntCentralY = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 + desplY
                                        puntCentralYSup = build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + desplYSup

                                        orientSupA =  "Dre"
                                        posFemellaY = puntCentralY - puntCentralYSup + 7.5
                                        posFemellaY = desplY - desplYSup + build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 - 7.5
                                        if build_ele.dadesTDVertTD.value[nBarraVertical].EncaixSup:
                                            orientSupA =  "Dre"
                                            #posFemellaY = puntCentralY - puntCentralYSup + 7.5
                                            posFemellaY = puntCentralY - puntCentralYSup/2 + 7.5
                                            #if build_ele.dadesTDHortInter.value[posBarraHor].Ample == 30:
                                            #    posFemellaY = puntCentralY - puntCentralYSup + 7.5
                                            #else:
                                            posFemellaY = puntCentralY - puntCentralYSup + 7.5
                                            posFemellaY = desplY - desplYSup + build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 - 7.5

                                            #posFemellaY =  puntCentralY -7.5
                                        else:
                                            desplY = build_ele.listDesplVerticalsTD.value[nBarraVertical].desplYAbs
                                            desplYSup = build_ele.dadesTDHortInter.value[posBarraHor].desplY
                                            puntCentralY = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAltura/2 + desplY
                                            puntCentralYSup = build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + desplYSup
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
                                                posY = Altura/2 - 15/2 + desply - build_ele.desplYI.value + desplAct - build_ele.listDesplVerticalsTD.value[j].desplY - build_ele.dadesTDHortInter.value[barraSupHor].desplY
                                            else:
                                                if orientacio == "Esq":
                                                    posY = Altura/2 - 15/2 + desply  - desplAct - build_ele.listDesplVerticalsTD.value[j].desplY #- build_ele.dadesTDHortInter.value
                                                else:
                                                    posY = Altura/2 - 15/2 + desply   - build_ele.listDesplVerticalsTD.value[j].desplY - build_ele.dadesTDHortInter.value[barraSupHor].desplY
                                        '''

                                        TDHorCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella')
                                        bob = TDHorCollection(Femella = build_ele.dadesTDVertTD.value[nBarraVertical].MostrarTDVertical and build_ele.dadesTDVertTD.value[nBarraVertical].FemellaSup,
                                                            FemellaOr = orientSupA,
                                                            PosFemellaX = pos,
                                                            PosFemellaY = posFemellaY,
                                                            Separacio_forat_femella = build_ele.dadesTDVertTD.value[nBarraVertical].BarraAmple - 3.0)
                                        femelles.append(bob)

                                for nForat in range(0,len(forats)):
                                    if forats[nForat].Forat and build_ele.BarresHorList.value[posBarraHor].BarraHor:#and forats[nForat].MostrarBox
                                        #group_elems.append(createBoxForatHorInt(build_ele, posBarraHor, forats,j,nForat))
                                        if forats[nForat].MostrarBox:
                                            group_elems.append(createBoxForatHorInt(build_ele, posBarraHor, forats, NBarraInici,nForat))
                                            group_elems_preview.append(createBoxForatHorInt(build_ele, posBarraHor, forats, NBarraInici,nForat))
                                        for cavHor in (createBoxForatCavitatHorInt(build_ele, posBarraHor, forats, NBarraInici,nForat)):
                                            group_elems.append(cavHor)
                                            group_elems_preview.append(cavHor)
                                        for cavHor in (createBoxForatCavitatHorIntXPS(build_ele, posBarraHor, forats, NBarraInici,nForat)):
                                            group_elems.append(cavHor)
                                            group_elems_preview.append(cavHor)


                                GlobalPropLayer = 40001
                                if build_ele.BarresHorList.value[posBarraHor].Xapa:
                                    build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(PestanyaSup = False)
                                    build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(PestanyaInf = False)
                                    if build_ele.BarresHorList.value[posBarraHor].Layer == "KN_ELECTRICITAT_REINFORCEMENT":
                                        GlobalPropLayer = 40073#(KN_ELECTRICITAT_REINFORCEMENT)
                                    elif build_ele.BarresHorList.value[posBarraHor].Layer == "KN_AIGUA_REINFORCEMENT":
                                        GlobalPropLayer = 40074#(KN_AIGUA_REINFORCEMENT)
                                tableAux = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInter.value[posBarraHor].Ample, build_ele.dadesTDHortInter.value[posBarraHor].Altura,llargada-1, build_ele.dadesTDHortInter.value[posBarraHor].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                        False, build_ele.dadesTDHortInter.value[posBarraHor].FounColor, GlobalPropLayer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        colis, potes, forats, #ColisPar, PotaPar, #matrius
                                                        build_ele.dadesTDHortInter.value[posBarraHor].Ample_forat_femella, build_ele.dadesTDHortInter.value[posBarraHor].Altura_forat_femella, build_ele.dadesTDHortInter.value[posBarraHor].Separacio_forat_femella,
                                                        femelles, #Femelles, #matriu
                                                        build_ele.dadesTDHortInter.value[posBarraHor].posicio_centre_masses, #posicio_centre_masses,
                                                        build_ele.dadesTDHortInter.value[posBarraHor].IsFirstCancam, build_ele.dadesTDHortInter.value[posBarraHor].Dis1cancam, #IsFirstCancam, Dis1cancam,
                                                        build_ele.dadesTDHortInter.value[posBarraHor].IsSecondCancam, build_ele.dadesTDHortInter.value[posBarraHor].Dis2cancam, #IsSecondCancam, Dis2cancam,
                                                        build_ele.dadesTDHortInter.value[posBarraHor].PestanyaSup, build_ele.dadesTDHortInter.value[posBarraHor].PestanyaInf,#PestanyaSuperior, PestanyaInferior,
                                                        encaixos) #EncaixosPar))

                                if not tableAux.is_valid():
                                    return[]


                                posInici = build_ele.listDesplVerticalsTD.value[NBarraInici].desplXAbs


                                matrix_Aux = AllplanGeo.Matrix3D()

                                if build_ele.BarresHorList.value[posBarraHor].Orientacio == 'Inf' and not build_ele.BarresHorList.value[posBarraHor].AutoLongitud :
                                    #matrix_Aux.SetValue(12, matrix[12] + build_ele.listDesplVerticalsTD.value[j].desplX - llargada - build_ele.dadesTDHortInter.value[posBarraHor].desplX  + build_ele.listDesplVerticalsTD.value[j].desplX  )
                                    #matrix_Aux.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs - build_ele.dadesTDVertTD.value[j].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 2 - llargada)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)
                                    matrix_Aux.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + posInici - build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 - build_ele.dadesTDVertTD.value[NBarraInici].Gruix + 2 - llargada)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)
                                else:
                                    #matrix_Aux.SetValue(12, matrix[12] + build_ele.listDesplVerticalsTD.value[j].desplX + build_ele.dadesTDVertTD.value[j].BarraAmple - build_ele.dadesTDHortInter.value[posBarraHor].desplX)
                                    #matrix_Aux.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs + build_ele.dadesTDVertTD.value[j].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.BarraGruix.value + 2)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)
                                    matrix_Aux.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + posInici + build_ele.dadesTDVertTD.value[NBarraInici].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 - build_ele.dadesTDVertTD.value[NBarraInici].Gruix + 2 )#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)

                                matrix_Aux.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY)
                                #matrix_Aux.SetValue(13, matrix[13] + build_ele.dadesTDHortInter.value[posBarraHor].desplY)
                                #if build_ele.desplYI.value == 0 or not build_ele.EncaixHorInf.value:

                                if not build_ele.EncaixHorInf.value:
                                    matrix_Aux.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)
                                else:
                                    matrix_Aux.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)

                                TranslationFather = matrix_Aux
                                TranslationFather.SetValue(12, placement_mat[12] + matrix_Aux[12])
                                TranslationFather.SetValue(13, placement_mat[13] + matrix_Aux[13])
                                TranslationFather.SetValue(14, placement_mat[14] + matrix_Aux[14])
                                matrix_Aux  = TranslationFather

                                # contadorPPI += 1
                                '''
                                if posBarraHor >= len(build_ele.BarresAdjList.value) or posBarraHor >= len(build_ele.dadesAdj.value):
                                    set_valors_Adjacents(build_ele,posBarraHor)


                                if build_ele.BarresHorList.value[posBarraHor].Edit and nVer==j and build_ele.BarresAdjListToShow.value[0].Save:
                                    guardar_valors_adjacents(build_ele, posBarraHor)
                                    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Save = False)
                                elif build_ele.BarresHorList.value[posBarraHor].Edit and nVer==j and build_ele.BarresAdjListToShow.value[0].Edit:
                                    mostrar_valors_adjacents(build_ele, posBarraHor)
                                    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Edit = False)

                                if build_ele.BarresAdjList.value[posBarraHor].BarraAdj:
                                    #--------CREATE HORITZONTAL--------- POSAR DADES MATRIUS [0]


                                    if len(build_ele.dadesTDVertInter.value) <= j :
                                        set_valors_Adjacents(build_ele, posBarraHor)
                                    if len(build_ele.BarresAdjList.value) <= posBarraHor :
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

                                    if  build_ele.BarresAdjList.value[posBarraHor].Longitud <= 0:
                                        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Orientacio = 'Dre')
                                        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Longitud = 100)

                                    if len(build_ele.dadesTDVertInter.value) > posBarraHor:
                                        separacioFemellaNovaInf = build_ele.dadesTDVertInter.value[posBarraHor].BarraAmple
                                    else:
                                        separacioFemellaNovaInf = 30


                                    novaHor = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInter.value[posBarraHor].Ample, build_ele.dadesTDHortInter.value[posBarraHor].Altura,build_ele.BarresAdjList.value[posBarraHor].Longitud, build_ele.dadesTDHortInter.value[posBarraHor].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                        build_ele.dadesAdj.value[posBarraHor].IsUseGlobalProp, build_ele.dadesAdj.value[posBarraHor].FounColor, build_ele.dadesAdj.value[posBarraHor].BarraLayer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
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

                                    tubEsIgual = False
                                    if build_ele.comprovarDEN.value:
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
                                                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                                                        AllplanBaseElements.AttributeString(2430, novaHor.get_codi_pestanyes()),
                                                        AllplanBaseElements.AttributeString(2435, novaHor.get_codi_cancam()),
                                                        AllplanBaseElements.AttributeString(2431, novaHor.get_codi_mesures()),
                                                        AllplanBaseElements.AttributeString(2433, novaHor.get_codi_pota()),
                                                        AllplanBaseElements.AttributeString(2445, novaHor.get_seccio()),
                                                        AllplanBaseElements.AttributeString(220, novaHor.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2455, novaHor.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2103, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(1083, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(508, "TD")]
                                    novaHor_views = [View2D3D ([AllplanBasisElements.ModelElement3D(novaHor_common_props, novaHor_brep)])]


                                    matrix_Adj = AllplanGeo.Matrix3D()
                                    matrix_Adj.SetValue(12, matrix_Aux[12] + build_ele.BarresAdjList.value[posBarraHor].Posicio)
                                    matrix_Adj.SetValue(13, matrix_Aux[13])
                                    matrix_Adj.SetValue(14, matrix_Aux[14])

                                    reOrinetacio = ""
                                    if build_ele.BarresAdjList.value[posBarraHor].Orientacio == 'Esq' :
                                        matrix_Adj.SetValue(13, matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample - build_ele.BarresAdjList.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Inf"
                                    elif build_ele.BarresAdjList.value[posBarraHor].Orientacio == 'Sup' :
                                        matrix_Adj.SetValue(14, matrix_Aux[14] + build_ele.dadesTDHortInter.value[posBarraHor].Altura - build_ele.BarresAdjList.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Esq"
                                    elif build_ele.BarresAdjList.value[posBarraHor].Orientacio == 'Dre' :
                                        matrix_Adj.SetValue(13, matrix_Aux[13] - build_ele.dadesTDHortInter.value[posBarraHor].Ample + build_ele.BarresAdjList.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Sup"
                                    elif build_ele.BarresAdjList.value[posBarraHor].Orientacio == 'Inf' :
                                        matrix_Adj.SetValue(14, matrix_Aux[14] - build_ele.dadesTDHortInter.value[posBarraHor].Altura + build_ele.BarresAdjList.value[posBarraHor].Profunditat)
                                        reOrinetacio = "Dre"
                                    else:
                                        print("no hauria d'entrar aqui")

                                    listEncaixAdj = []
                                    TDCollection = collections.namedtuple('StirrupList', 'BarraFront Orientacio Longitud Amplitud Posicio Profunditat Pestanya')
                                    bob = TDCollection( BarraFront = build_ele.BarresAdjList.value[posBarraHor].BarraAdj,
                                                        Orientacio = reOrinetacio,
                                                        Longitud = build_ele.BarresAdjList.value[posBarraHor].Longitud,
                                                        Amplitud = build_ele.dadesTDHortInter.value[posBarraHor].Ample,
                                                        Posicio = build_ele.BarresAdjList.value[posBarraHor].Posicio + build_ele.BarresAdjList.value[posBarraHor].Longitud/2,
                                                        Profunditat = build_ele.BarresAdjList.value[posBarraHor].Profunditat,
                                                        Pestanya = False
                                                        )
                                    if build_ele.BarresAdjList.value[posBarraHor].Profunditat > 0:
                                        listEncaixAdj.append(bob)

                                    tableAux.afegir_encaixos_frontals(listEncaixAdj,[],False)

                                    common_propsObjectNovaHor = AllplanBaseElements.CommonProperties()
                                    common_propsObjectNovaHor2 = AllplanBaseElements.CommonProperties()
                                    common_propsObjectNovaHor.Layer = 40054#(KN_XPS_RECESS)
                                    colorCavitat = getColorCavitat(build_ele.dadesTDHortInter.value[posBarraHor].Ample)
                                    common_propsObjectNovaHor.Color = colorCavitat
                                    common_propsObjectNovaHor2.Color = colorCavitat

                                    horitzontalPPOBject4 = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInter.value[posBarraHor].Ample, build_ele.dadesTDHortInter.value[posBarraHor].Altura+10,build_ele.BarresAdjList.value[posBarraHor].Longitud + 10, 0,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                        False, common_propsObjectNovaHor.Color, common_propsObjectNovaHor.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                    horitzontalPPOBject4A = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesTDHortInter.value[posBarraHor].Ample, build_ele.dadesTDHortInter.value[posBarraHor].Altura+10,build_ele.BarresAdjList.value[posBarraHor].Longitud + 10, 0,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                        False, common_propsObjectNovaHor2.Color, common_propsObjectNovaHor2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])

                                    horitzontalPPOBject4_brep2 = horitzontalPPOBject4.create()
                                    horitzontalPPOBject4_brep2A = horitzontalPPOBject4A.create()

                                    horitzontal_views_object4 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor, horitzontalPPOBject4_brep2)])]
                                    horitzontal_views_object4_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor2, horitzontalPPOBject4_brep2A)])]


                                    matrix_AdjC = AllplanGeo.Matrix3D()
                                    matrix_AdjC.SetValue(12, matrix_Adj[12] - 5)
                                    matrix_AdjC.SetValue(13, matrix_Adj[13])
                                    matrix_AdjC.SetValue(14, matrix_Adj[14]-5)



                                    if matrix_Adj[12] - placement_mat[12] < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
                                        #if build_ele.BarresHorList.value[posBarraHor].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
                                        if build_ele.MostrarCavitatsRecess.value:
                                            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4.get_params_list(),
                                                            hash_value = horitzontalPPOBject4.hash(), python_file = horitzontalPPOBject4.filename(),
                                                            views = horitzontal_views_object4, matrix = matrix_AdjC, common_props = common_propsObjectNovaHor, attribute_list = table_attr_listObject))
                                            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4.get_params_list(),
                                                            hash_value = horitzontalPPOBject4.hash(), python_file = horitzontalPPOBject4.filename(),
                                                            views = horitzontal_views_object4, matrix = matrix_AdjC, common_props = common_propsObjectNovaHor, attribute_list = table_attr_listObject))
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor, horitzontalPPOBject4_brep2))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor, group_elems[len(group_elems)-1]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor, horitzontalPPOBject4_brep2))
                                        #if build_ele.BarresHorList.value[posBarraHor].MostrarCavitat and build_ele.MostrarCavitats.value:
                                        if build_ele.MostrarCavitats.value:
                                            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4A.get_params_list(),
                                                            hash_value = horitzontalPPOBject4A.hash(), python_file = horitzontalPPOBject4A.filename(),
                                                            views = horitzontal_views_object4_2, matrix = matrix_AdjC, common_props = common_propsObjectNovaHor2, attribute_list = table_attr_listObject))
                                            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject4A.get_params_list(),
                                                            hash_value = horitzontalPPOBject4A.hash(), python_file = horitzontalPPOBject4A.filename(),
                                                            views = horitzontal_views_object4_2, matrix = matrix_AdjC, common_props = common_propsObjectNovaHor2, attribute_list = table_attr_listObject))
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor2, horitzontalPPOBject4_brep2A))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor2, group_elems[len(group_elems)-1]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHor2, horitzontalPPOBject4_brep2A))

                                        group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = novaHor.get_params_list(),
                                                                    hash_value = novaHor.hash(), python_file = novaHor.filename(),
                                                                    views = novaHor_views, matrix = matrix_Adj, common_props = novaHor_common_props, attribute_list = novaHor_attr_list))
                                        group_elems_preview.append(PythonPart ("PP_TD_Horitzontal", parameter_list = novaHor.get_params_list(),
                                                                    hash_value = novaHor.hash(), python_file = novaHor.filename(),
                                                                    views = novaHor_views, matrix = matrix_Adj, common_props = novaHor_common_props, attribute_list = novaHor_attr_list))
                                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(novaHor_common_props, novaHor_brep))
                                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(novaHor_common_props, group_elems[len(group_elems)-1]))
                                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(novaHor_common_props, novaHor_brep))

                                        punt_central = matrix_Adj[12] + build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Adj[12], matrix_Adj[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2, matrix_Adj[14] + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInter.value[posBarraHor].Altura, build_ele.BarresAdjList.value[posBarraHor].Longitud, True, pointUbi)
                                        if polyhedronCentral != []:
                                            group_elems.append(polyhedronCentral[0])
                                            group_elems_preview.append(polyhedronCentral[0])
                                            group_elems.append(polyhedronCentral[3])
                                            group_elems_preview.append(polyhedronCentral[3])
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))

                                '''

                                build_ele.DENHorInt.value = "T "

                                table_brepAux = tableAux.create()
                                common_propsHor = tableAux.get_common_props()
                                common_propsHorPrev = tableAux.get_common_props()
                                tubEsIgual = False
                                if build_ele.comprovarDEN.value:
                                    tubEsIgual, DEN = compare_attributes(build_ele, doc, tableAux)
                                if (tubEsIgual):
                                    build_ele.DENHorInt.value = DEN
                                #if testEditBarraHorInterior:
                                #    common_propsHor.Color = 4 #Verd
                                if build_ele.dadesTDHortInter.value[posBarraHor].vermell:
                                    common_propsHor.Color = 6 #Verd
                                    common_propsHorPrev.Color = 6#Vermell
                                    #handle_list = tableAux.create_handles()

                                cara_a, cara_a1, cara_a2 = dividirAtribut(str(tableAux.get_codi_cara_a()) )
                                cara_b, cara_b1, cara_b2 = dividirAtribut(str(tableAux.get_codi_cara_b()) )
                                cara_c, cara_c1, cara_c2 = dividirAtribut(str(tableAux.get_codi_cara_c()) )
                                cara_d, cara_d1, cara_d2 = dividirAtribut(str(tableAux.get_codi_cara_d()) )

                                cara_e, cara_e1, cara_e2 = dividirAtribut(str(tableAux.get_codi_cara_a_inv()) )
                                cara_f, cara_f1, cara_f2 = dividirAtribut(str(tableAux.get_codi_cara_b_inv()) )
                                cara_g, cara_g1, cara_g2 = dividirAtribut(str(tableAux.get_codi_cara_c_inv()) )
                                cara_h, cara_h1, cara_h2 = dividirAtribut(str(tableAux.get_codi_cara_d_inv()) )

                                table_attr_listAux = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                                                        AllplanBaseElements.AttributeString(2430, tableAux.get_codi_pestanyes()),
                                                        AllplanBaseElements.AttributeString(2435, tableAux.get_codi_cancam()),
                                                        AllplanBaseElements.AttributeString(2431, tableAux.get_codi_mesures()),
                                                        AllplanBaseElements.AttributeString(2433, tableAux.get_codi_pota()),
                                                        AllplanBaseElements.AttributeString(2445, tableAux.get_seccio()),#
                                                        AllplanBaseElements.AttributeString(220,  tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2455, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2455, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(1085, tableAux.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2103, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(1083, build_ele.DENHorInt.value),
                                                        AllplanBaseElements.AttributeString(1084, tableAux.get_seccio()),
                                                        AllplanBaseElements.AttributeString(1087, "Horitzontal"),
                                                        AllplanBaseElements.AttributeString(508, "TD")]
                                table_viewsAux = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsHor, table_brepAux)])]
                                table_viewsAuxPrev = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsHorPrev, table_brepAux)])]

                                common_propsObjectAdj = AllplanBaseElements.CommonProperties()
                                common_propsObjectAdj2 = AllplanBaseElements.CommonProperties()
                                common_propsObjectAdj.Layer = 40054#(KN_XPS_RECESS)
                                if build_ele.BarresHorList.value[posBarraHor].Xapa:
                                    if build_ele.BarresHorList.value[posBarraHor].Layer == "KN_ELECTRICITAT_REINFORCEMENT":
                                        common_propsObjectAdj.Layer = 40073#(KN_ELECTRICITAT_REINFORCEMENT)
                                    elif build_ele.BarresHorList.value[posBarraHor].Layer == "KN_AIGUA_REINFORCEMENT":
                                        common_propsObjectAdj.Layer = 40074#(KN_AIGUA_REINFORCEMENT)
                                common_propsObjectAdj2.Layer = 40055#(KN_XPS_CAVITAT)
                                colorCavitat = getColorCavitat(build_ele.dadesTDHortInter.value[posBarraHor].Ample)
                                common_propsObjectAdj.Color = colorCavitat
                                common_propsObjectAdj2.Color = colorCavitat


                                distXapa = 0
                                distXapaY = build_ele.dadesTDHortInter.value[posBarraHor].Ample
                                distXapaZ = 10
                                llargadaPlusCavitat = 10
                                if build_ele.BarresHorList.value[posBarraHor].Xapa:
                                    distXapa = 15
                                    distXapaY = build_ele.BarresHorList.value[posBarraHor].ProfunditatXapa
                                    distXapaZ = 30
                                    llargadaPlusCavitat = 0

                                horitzontalPPOBject3 = PP_TD_Horitzontal(random.random() * 3600,0,  distXapaY, build_ele.dadesTDHortInter.value[posBarraHor].Altura + distXapaZ,llargada + (distXapa*2) + llargadaPlusCavitat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObjectAdj.Color, common_propsObjectAdj.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                horitzontalPPOBject3A = PP_TD_Horitzontal(random.random() * 3600,0, distXapaY, build_ele.dadesTDHortInter.value[posBarraHor].Altura + distXapaZ ,llargada + (distXapa*2) + llargadaPlusCavitat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                                        False, common_propsObjectAdj2.Color, common_propsObjectAdj2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                        [], [],[], #ColisPar, PotaPar, #matrius
                                                        0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                        [], #Femelles, #matriu
                                                        0, #posicio_centre_masses,
                                                        False, 0, #IsFirstCancam, Dis1cancam,
                                                        False, 0, #IsSecondCancam, Dis2cancam,
                                                        False, False,#PestanyaSuperior, PestanyaInferior,
                                                        [])
                                horitzontal_BrepObject3 = horitzontalPPOBject3.create()
                                horitzontal_BrepObject3A = horitzontalPPOBject3A.create()
                                horitzontal_views_object3 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectAdj, horitzontal_BrepObject3)])]
                                horitzontal_views_object3_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectAdj2, horitzontal_BrepObject3A)])]

                                matrix_AuxC = AllplanGeo.Matrix3D()
                                matrix_AuxC.SetValue(12, matrix_Aux[12] - distXapa - llargadaPlusCavitat/2)
                                matrix_AuxC.SetValue(13, matrix_Aux[13] )
                                matrix_AuxC.SetValue(14, matrix_Aux[14] - distXapaZ/2)
                                if build_ele.BarresHorList.value[posBarraHor].Xapa:
                                    matrix_AuxC.SetValue(13, matrix_Aux[13] - (build_ele.BarresHorList.value[posBarraHor].ProfunditatXapa - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2)


                                if matrix_Aux[12] - placement_mat[12] < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:

                                    #if build_ele.BarresHorList.value[posBarraHor].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
                                    if build_ele.MostrarCavitatsRecess.value:
                                        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3.get_params_list(),
                                                            hash_value = horitzontalPPOBject3.hash(), python_file = horitzontalPPOBject3.filename(),
                                                            views = horitzontal_views_object3, matrix = matrix_AuxC, common_props = common_propsObjectAdj, attribute_list = table_attr_listObject))
                                        group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3.get_params_list(),
                                                            hash_value = horitzontalPPOBject3.hash(), python_file = horitzontalPPOBject3.filename(),
                                                            views = horitzontal_views_object3, matrix = matrix_AuxC, common_props = common_propsObjectAdj, attribute_list = table_attr_listObject))
                                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj, horitzontal_BrepObject3))
                                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj, group_elems[len(group_elems)-1]))
                                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj, horitzontal_BrepObject3))
                                    #if build_ele.BarresHorList.value[posBarraHor].MostrarCavitat and build_ele.MostrarCavitats.value:
                                    if build_ele.MostrarCavitats.value:
                                        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3A.get_params_list(),
                                                            hash_value = horitzontalPPOBject3A.hash(), python_file = horitzontalPPOBject3A.filename(),
                                                            views = horitzontal_views_object3_2, matrix = matrix_AuxC, common_props = common_propsObjectAdj2, attribute_list = table_attr_listObject))
                                        group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject3A.get_params_list(),
                                                            hash_value = horitzontalPPOBject3A.hash(), python_file = horitzontalPPOBject3A.filename(),
                                                            views = horitzontal_views_object3_2, matrix = matrix_AuxC, common_props = common_propsObjectAdj2, attribute_list = table_attr_listObject))
                                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj2, horitzontal_BrepObject3A))
                                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj2, group_elems[len(group_elems)-1]))
                                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectAdj2, horitzontal_BrepObject3A))

                                    group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = tableAux.get_params_list(),
                                                            hash_value = tableAux.hash(), python_file = tableAux.filename(),
                                                            views = table_viewsAux, matrix = matrix_Aux, common_props = common_propsHor, attribute_list = table_attr_listAux))
                                    group_elems_preview.append(PythonPart ("PP_TD_Horitzontal", parameter_list = tableAux.get_params_list(),
                                                            hash_value = tableAux.hash(), python_file = tableAux.filename(),
                                                            views = table_viewsAuxPrev  , matrix = matrix_Aux, common_props = common_propsHorPrev, attribute_list = table_attr_listAux))
                                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsHor, table_brepAux))
                                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsHor, group_elems[len(group_elems)-1]))
                                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsHor, table_brepAux))



                                    if build_ele.BarresHorList.value[posBarraHor].Xapa:
                                        layer = GlobalPropLayer
                                        punt_central = matrix_Aux[12] + build_ele.dadesTDHortInter.value[posBarraHor].desplX
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12] + 5, matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinB, matrix_Aux[14] + 5)
                                        lineX = create_polyline_interior(build_ele, punt_central+5, build_ele.dadesTDHortInter.value[posBarraHor].Altura - 10, llargada-10, True, pointUbi, int(linia), layer, 15)
                                        if lineX != []:
                                            #group_elems.append(lineX[0])
                                            group_elems.append(lineX[0])
                                            group_elems.append(lineX[3])
                                            group_elems_preview.append(lineX[0])
                                            group_elems_preview.append(lineX[3])
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12] + 5, matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinB, matrix_Aux[14] + build_ele.dadesTDHortInter.value[posBarraHor].Altura -5 )
                                        lineX = create_polyline_interior(build_ele, punt_central+5, build_ele.dadesTDHortInter.value[posBarraHor].Altura - 10, llargada-10, True, pointUbi, int(linia), layer, 15)
                                        if lineX != []:
                                            #group_elems.append(lineX[0])
                                            group_elems.append(lineX[0])
                                            group_elems.append(lineX[3])
                                            group_elems_preview.append(lineX[0])
                                            group_elems_preview.append(lineX[3])
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12] + 5, matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinB, matrix_Aux[14] + 5 )
                                        lineX = create_polyline_interior(build_ele, punt_central+5, build_ele.dadesTDHortInter.value[posBarraHor].Altura - 10, build_ele.dadesTDHortInter.value[posBarraHor].Altura-10, False, pointUbi, int(linia), layer, 15)
                                        if lineX != []:
                                            #group_elems.append(lineX[0])
                                            group_elems.append(lineX[0])
                                            group_elems.append(lineX[3])
                                            group_elems_preview.append(lineX[0])
                                            group_elems_preview.append(lineX[3])
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12] + llargada - 5, matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinB, matrix_Aux[14] + 5 )
                                        lineX = create_polyline_interior(build_ele, punt_central+5, build_ele.dadesTDHortInter.value[posBarraHor].Altura - 10, build_ele.dadesTDHortInter.value[posBarraHor].Altura-10, False, pointUbi, int(linia), layer, 15)
                                        if lineX != []:
                                            #group_elems.append(lineX[0])
                                            group_elems.append(lineX[0])
                                            group_elems.append(lineX[3])
                                            group_elems_preview.append(lineX[0])
                                            group_elems_preview.append(lineX[3])


                                    if build_ele.dadesTDHortInter.value[posBarraHor].mostrarLiniaVertA:
                                        punt_central = matrix_Aux[12] + build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12], matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinA, matrix_Aux[14] + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)
                                        if (len(build_ele.dadesTDHortInter.value[posBarraHor].linia) > 1):
                                            linia = build_ele.dadesTDHortInter.value[posBarraHor].linia[len(build_ele.dadesTDHortInter.value[posBarraHor].linia)-1]
                                        else:
                                            build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(linia = "Tipus 1")
                                            linia = "1"
                                        if (len(build_ele.dadesTDHortInter.value[posBarraHor].layer) > 1):
                                            layer = build_ele.dadesTDHortInter.value[posBarraHor].layer
                                        else:
                                            build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(layer = "TD_FIXACIO")
                                            layer = "TD_FIXACIO"
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInter.value[posBarraHor].Altura, llargada, True, pointUbi, int(linia), layer)
                                        if polyhedronCentral != []:
                                            group_elems.append(polyhedronCentral[0])
                                            group_elems_preview.append(polyhedronCentral[0])
                                            group_elems.append(polyhedronCentral[3])
                                            group_elems_preview.append(polyhedronCentral[3])
                                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                    if build_ele.dadesTDHortInter.value[posBarraHor].mostrarLiniaVertB:
                                        punt_central = matrix_Aux[12] + build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2
                                        pointUbi = AllplanGeo.Point3D(matrix_Aux[12], matrix_Aux[13] + build_ele.dadesTDHortInter.value[posBarraHor].Ample/2 + build_ele.dadesTDHortInter.value[posBarraHor].desplLinB, matrix_Aux[14] + build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)
                                        if (len(build_ele.dadesTDHortInter.value[posBarraHor].linia) > 1):
                                            linia = build_ele.dadesTDHortInter.value[posBarraHor].linia[len(build_ele.dadesTDHortInter.value[posBarraHor].linia)-1]
                                        else:
                                            build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(linia = "Tipus 1")
                                            linia = "1"
                                        if (len(build_ele.dadesTDHortInter.value[posBarraHor].layer) > 1):
                                            layer = build_ele.dadesTDHortInter.value[posBarraHor].layer
                                        else:
                                            build_ele.dadesTDHortInter.value[posBarraHor] = build_ele.dadesTDHortInter.value[posBarraHor]._replace(layer = "TD_FIXACIO")
                                            layer = "TD_FIXACIO"
                                        polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDHortInter.value[posBarraHor].Altura, llargada, True, pointUbi, int(linia), layer)
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
                                        if numHor != [] and len(numHor) > 2:
                                            #group_elems.append(numHor)
                                            group_elems_preview.append(numHor[0])
                                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(numHor[1],numHor[2]))


                                contadorPPI += 1


                except Exception as e:
                    print("no s'ha creat interior:", e)



                #if (build_ele.desplYI.value != 0 or build_ele.EncaixHorInf.value) and not build_ele.invertirEncaixInf.value:
                if  build_ele.EncaixHorInf.value and not build_ele.invertirEncaixInf.value:
                    horitzontalPP.set_false_femelles()
                #if build_ele.desplYS.value != 0 and not build_ele.invertirEncaixSup.value:
                if build_ele.EncaixHorSup.value and not build_ele.invertirEncaixSup.value:
                    horitzontalPP2.set_false_femelles()


                #-------------Barres Frontals ---------------
                try:

                    if j * 5 + 10 >= len(build_ele.BarresFrontList.value) or j * 10 >= len(build_ele.dadesFront.value):
                        set_valors_Frontals(build_ele,j * 10)


                    inici = build_ele.nListBarresFront.value[j].Posicio
                    final = build_ele.nListBarresFront.value[j].nTotal
                    encaixosAux = []
                    listLong = []
                    for barraFrontal in range(inici, inici+final):

                        if build_ele.BarresFrontList.value[barraFrontal].BarraFront:
                            encaixosAux.append(build_ele.BarresFrontList.value[barraFrontal])
                            encaixosAux[len(encaixosAux)-1] = encaixosAux[len(encaixosAux)-1]._replace(Longitud = build_ele.BarresFrontList.value[barraFrontal].Altura)


                            listLong.append(build_ele.BarraAlturaVert.value)
                            #--------CREATE HORITZONTAL--------- POSAR DADES MATRIUS [0]

                            if len(build_ele.BarresFrontList.value) <= j :
                                set_valors_Frontals(build_ele, barraFrontal)



                            novaHorFront = TD_Horitzontal_Front(0, build_ele.BarresFrontList.value[barraFrontal].Amplitud, build_ele.BarresFrontList.value[barraFrontal].Altura, build_ele.BarresFrontList.value[barraFrontal].Longitud, 1.5, #build_ele.dadesTDHortInter.value[posBarraVertinJ].Ample, build_ele.dadesTDHortInter.value[posBarraVertinJ].Altura,build_ele.BarresFrontList.value[posBarraVert].Longitud, build_ele.dadesTDHortInter.value[posBarraVertinJ].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                build_ele.IsUseGlobalProp.value, 23, build_ele.BarraLayer.value, # build_ele.dadesFront.value[posBarraVert].IsUseGlobalProp, build_ele.dadesFront.value[posBarraVert].FounColor, build_ele.dadesFront.value[posBarraVert].BarraLayer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                [], [], #colis, potes, #ColisPar, PotaPar, #matrius
                                                1.5, 3.75, 30, #TDV_Int.Ample_forat_femella,TDV_Int.Altura_forat_femella,30,
                                                [], #femelles, #Femelles, #matriu
                                                0,#build_ele.dadesFront.value[posBarraVert].posicio_centre_masses, #posicio_centre_masses,
                                                False, 0, #build_ele.dadesFront.value[posBarraVert].IsFirstCancam, build_ele.dadesFront.value[posBarraVert].Dis1cancam, #IsFirstCancam, Dis1cancam,
                                                False, 0, #build_ele.dadesFront.value[posBarraVert].IsSecondCancam, build_ele.dadesFront.value[posBarraVert].Dis2cancam, #IsSecondCancam, Dis2cancam,
                                                False, False, #build_ele.dadesFront.value[posBarraVert].pestanyaSup, build_ele.dadesFront.value[posBarraVert].pestanyaInf,#PestanyaSuperior, PestanyaInferior,
                                                []) #encaixos) #EncaixosPar))


                            novaHorFront_brep = novaHorFront.create()
                            novaHorFront_common_props = novaHorFront.get_common_props()

                            cara_a, cara_a1, cara_a2 = dividirAtribut(str(novaHorFront.get_codi_cara_a()) )
                            cara_b, cara_b1, cara_b2 = dividirAtribut(str(novaHorFront.get_codi_cara_b()) )
                            cara_c, cara_c1, cara_c2 = dividirAtribut(str(novaHorFront.get_codi_cara_c()) )
                            cara_d, cara_d1, cara_d2 = dividirAtribut(str(novaHorFront.get_codi_cara_d()) )

                            cara_e, cara_e1, cara_e2 = dividirAtribut(str(novaHorFront.get_codi_cara_a_inv()) )
                            cara_f, cara_f1, cara_f2 = dividirAtribut(str(novaHorFront.get_codi_cara_b_inv()) )
                            cara_g, cara_g1, cara_g2 = dividirAtribut(str(novaHorFront.get_codi_cara_c_inv()) )
                            cara_h, cara_h1, cara_h2 = dividirAtribut(str(novaHorFront.get_codi_cara_d_inv()) )

                            novaHorFront_attr_list = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                                                        AllplanBaseElements.AttributeString(2446, novaHorFront.get_codi_pota_inv()),

                                                        AllplanBaseElements.AttributeString(2430, novaHorFront.get_codi_pestanyes()),
                                                        AllplanBaseElements.AttributeString(2435, novaHorFront.get_codi_cancam()),
                                                        AllplanBaseElements.AttributeString(2431, novaHorFront.get_codi_mesures()),
                                                        AllplanBaseElements.AttributeString(2433, novaHorFront.get_codi_pota()),
                                                        AllplanBaseElements.AttributeString(2445, novaHorFront.get_seccio()),
                                                        AllplanBaseElements.AttributeString(220,  novaHorFront.get_llargada()),
                                                        AllplanBaseElements.AttributeString(2455, novaHorFront.get_llargada()),
                                                        AllplanBaseElements.AttributeString(1083, "TIS"),
                                                        AllplanBaseElements.AttributeString(1084, novaHorFront.get_seccio()),
                                                        AllplanBaseElements.AttributeString(1085, novaHorFront.get_llargada()),
                                                        AllplanBaseElements.AttributeString(1087, "CONSOLE"),
                                                        AllplanBaseElements.AttributeString(2103, "TIS"),
                                                        AllplanBaseElements.AttributeString(508, " ")]#TD

                            z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                            point2=  AllplanGeo.Point3D(0,0,1))

                            matrix_Front = AllplanGeo.Matrix3D()
                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Esq' :
                                # ---- rotation ----
                                matrix_Front.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))

                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Dre' :
                                # ---- rotation ----
                                matrix_Front.Rotation(z_axis, AllplanGeo.Angle.FromDeg(270))

                            matrix_Front.SetValue(12, matrix[12] - placement_mat[12])
                            matrix_Front.SetValue(13, matrix[13] - placement_mat[13])

                            matrix_Front.SetValue(14, build_ele.BarresFrontList.value[barraFrontal].Posicio + build_ele.BarraAlturaInf.value - build_ele.BarresFrontList.value[barraFrontal].Altura/2)
                            #if (build_ele.desplYI.value != 0 or build_ele.EncaixHorInf.value):
                            #if build_ele.EncaixHorInf.value
                                #matrix_Front.SetValue(14, build_ele.BarresFrontList.value[barraFrontal].Posicio - build_ele.BarresFrontList.value[barraFrontal].Altura/2)
                            if not build_ele.dadesTDVertTD.value[j].EncaixInf:
                                matrix_Front.SetValue(14, build_ele.BarresFrontList.value[barraFrontal].Posicio  - build_ele.BarresFrontList.value[barraFrontal].Altura/2)
                            else:
                                matrix_Front.SetValue(14, build_ele.BarresFrontList.value[barraFrontal].Posicio + build_ele.BarraAlturaInf.value - build_ele.BarresFrontList.value[barraFrontal].Altura/2 +1 )



                            novaHorFront_views = [View2D3D ([AllplanBasisElements.ModelElement3D(novaHorFront_common_props, novaHorFront_brep)])]


                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Esq' :
                                matrix_Front.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs + build_ele.dadesTDVertTD.value[j].BarraAmple/2 +  build_ele.BarresFrontList.value[barraFrontal].Amplitud/2 - (build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2))#- profunditat
                                matrix_Front.SetValue(13, matrix[13] - placement_mat[13] + build_ele.listDesplVerticalsTD.value[j].desplY + build_ele.dadesTDVertTD.value[j].BarraAltura - build_ele.BarresFrontList.value[barraFrontal].Profunditat) #- profunditat
                            elif build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Inf' :
                                matrix_Front.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs + build_ele.dadesTDVertTD.value[j].BarraAmple - build_ele.BarresFrontList.value[barraFrontal].Profunditat - (build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2)) #- profunditat
                            elif build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Dre' :
                                matrix_Front.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs + build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.BarresFrontList.value[barraFrontal].Amplitud/2 - (build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2))
                                matrix_Front.SetValue(13, matrix[13] - placement_mat[13] + build_ele.BarresFrontList.value[barraFrontal].Profunditat)#- build_ele.BarraAmpleVert.value) #+ profunditat
                            elif build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Sup' :
                                matrix_Front.SetValue(12, build_ele.listDesplVerticalsTD.value[j].desplXAbs - build_ele.BarresFrontList.value[barraFrontal].Longitud + build_ele.BarresFrontList.value[barraFrontal].Profunditat - (build_ele.dadesTDVertTD.value[j].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2)) #+ profunditat
                            else:
                                print("no hauria d'entrar aqui")

                            TranslationFather = matrix_Front
                            TranslationFather.SetValue(12, placement_mat[12] + matrix_Front[12])
                            TranslationFather.SetValue(13, placement_mat[13] + matrix_Front[13])
                            TranslationFather.SetValue(14, placement_mat[14] + matrix_Front[14])
                            matrix_Front  = TranslationFather

                            common_propsObjectNovaHorFront = AllplanBaseElements.CommonProperties()
                            common_propsObjectNovaHorFront2 = AllplanBaseElements.CommonProperties()
                            common_propsObjectNovaHorFront.Layer = 40054#(KN_XPS_RECESS)
                            common_propsObjectNovaHorFront2.Layer = 40055#(KN_XPS_CAVITAT)
                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Esq' or build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Dre':
                                colorCavitat = getColorCavitat(build_ele.BarresFrontList.value[barraFrontal].Longitud + 10)
                                common_propsObjectNovaHorFront.Color = colorCavitat
                                common_propsObjectNovaHorFront2.Color = colorCavitat
                            else:
                                colorCavitat = getColorCavitat(build_ele.BarresFrontList.value[barraFrontal].Amplitud + 10)
                                common_propsObjectNovaHorFront.Color = colorCavitat
                                common_propsObjectNovaHorFront2.Color = colorCavitat

                            #horitzontalPPOBject5 = PP_TD_Horitzontal(random.random() * 3600, 0,  build_ele.BarresFrontList.value[barraFrontal].Longitud, build_ele.BarresFrontList.value[barraFrontal].Altura+10, build_ele.BarresFrontList.value[barraFrontal].Amplitud,  0, #0, build_ele.dadesTDHortInter.value[posBarraVert].Ample, build_ele.dadesTDHortInter.value[posBarraVert].Altura+10,build_ele.BarresAdjList.value[posBarraVert].Longitud, build_ele.dadesTDHortInter.value[posBarraVert].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                            horitzontalPPOBject5 = PP_TD_Horitzontal(random.random() * 3600, 0, build_ele.BarresFrontList.value[barraFrontal].Amplitud + 10, build_ele.BarresFrontList.value[barraFrontal].Altura+10,  build_ele.BarresFrontList.value[barraFrontal].Longitud + 10,  0, #0, build_ele.dadesTDHortInter.value[posBarraVert].Ample, build_ele.dadesTDHortInter.value[posBarraVert].Altura+10,build_ele.BarresAdjList.value[posBarraVert].Longitud, build_ele.dadesTDHortInter.value[posBarraVert].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                False, common_propsObjectNovaHorFront.Color, common_propsObjectNovaHorFront.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                [], [],[], #ColisPar, PotaPar, #matrius
                                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                [], #Femelles, #matriu
                                                0, #posicio_centre_masses,
                                                False, 0, #IsFirstCancam, Dis1cancam,
                                                False, 0, #IsSecondCancam, Dis2cancam,
                                                False, False,#PestanyaSuperior, PestanyaInferior,
                                                [])
                            horitzontalPPOBject5A = PP_TD_Horitzontal(random.random() * 3600, 0, build_ele.BarresFrontList.value[barraFrontal].Amplitud + 10, build_ele.BarresFrontList.value[barraFrontal].Altura+10,  build_ele.BarresFrontList.value[barraFrontal].Longitud + 10,  0, #0, build_ele.dadesTDHortInter.value[posBarraVert].Ample, build_ele.dadesTDHortInter.value[posBarraVert].Altura+10,build_ele.BarresAdjList.value[posBarraVert].Longitud, build_ele.dadesTDHortInter.value[posBarraVert].Gruix,#DistanciaEntreTD(TDV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada(DistanciaEntreTD), BarraGruix,
                                                False, common_propsObjectNovaHorFront2.Color, common_propsObjectNovaHorFront2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                                [], [],[], #ColisPar, PotaPar, #matrius
                                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                                [], #Femelles, #matriu
                                                0, #posicio_centre_masses,
                                                False, 0, #IsFirstCancam, Dis1cancam,
                                                False, 0, #IsSecondCancam, Dis2cancam,
                                                False, False,#PestanyaSuperior, PestanyaInferior,
                                                [])

                            #if not horitzontalPPOBject5.is_valid():
                            #    print("Cavitat Frontal incorrecta")


                            horitzontalPPOBject5_brep = horitzontalPPOBject5.create()
                            horitzontalPPOBject5_brepA = horitzontalPPOBject5A.create()

                            horitzontal_views_object5 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront, horitzontalPPOBject5_brep)])]
                            horitzontal_views_object5_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront2, horitzontalPPOBject5_brepA)])]

                            matrix_FrontC = AllplanGeo.Matrix3D()
                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Esq' :
                                # ---- rotation ----
                                matrix_FrontC.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
                                matrix_FrontC.SetValue(12, matrix_Front[12] + 5)

                            if build_ele.BarresFrontList.value[barraFrontal].Orientacio == 'Dre' :
                                # ---- rotation ----
                                matrix_FrontC.Rotation(z_axis, AllplanGeo.Angle.FromDeg(270))
                                matrix_FrontC.SetValue(12, matrix_Front[12] - 5)


                            matrix_FrontC.SetValue(13, matrix_Front[13])
                            matrix_FrontC.SetValue(14, matrix_Front[14] - 5)


                            if build_ele.listDesplVerticalsTD.value[j].desplXAbs < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
                                #if build_ele.dadesTDVertTD.value[j].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
                                if build_ele.MostrarCavitatsRecess.value:
                                    group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject5.get_params_list(),
                                                hash_value = horitzontalPPOBject5.hash(), python_file = horitzontalPPOBject5.filename(),
                                                views = horitzontal_views_object5, matrix = matrix_FrontC, common_props = common_propsObjectNovaHorFront, attribute_list = table_attr_listObject))
                                    group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject5.get_params_list(),
                                                hash_value = horitzontalPPOBject5.hash(), python_file = horitzontalPPOBject5.filename(),
                                                views = horitzontal_views_object5, matrix = matrix_FrontC, common_props = common_propsObjectNovaHorFront, attribute_list = table_attr_listObject))
                                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront, horitzontalPPOBject5_brep))
                                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront, group_elems[len(group_elems)-1]))
                                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront, horitzontalPPOBject5_brep))
                                #if build_ele.dadesTDVertTD.value[j].MostrarCavitat and build_ele.MostrarCavitats.value:
                                if build_ele.MostrarCavitats.value:
                                    group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject5A.get_params_list(),
                                                hash_value = horitzontalPPOBject5A.hash(), python_file = horitzontalPPOBject5A.filename(),
                                                views = horitzontal_views_object5_2, matrix = matrix_FrontC,  common_props = common_propsObjectNovaHorFront2, attribute_list = table_attr_listObject))
                                    group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject5A.get_params_list(),
                                                hash_value = horitzontalPPOBject5A.hash(), python_file = horitzontalPPOBject5A.filename(),
                                                views = horitzontal_views_object5_2, matrix = matrix_FrontC,  common_props = common_propsObjectNovaHorFront2, attribute_list = table_attr_listObject))
                                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront2, horitzontalPPOBject5_brepA))
                                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront2, group_elems[len(group_elems)-1]))
                                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectNovaHorFront2, horitzontalPPOBject5_brepA))

                                group_elems.append(PythonPart ("TD_Horitzontal_Front", parameter_list = novaHorFront.get_params_list(),
                                                        hash_value = novaHorFront.hash(), python_file = novaHorFront.filename(),
                                                        views = novaHorFront_views, matrix = matrix_Front,  common_props = novaHorFront_common_props, attribute_list = novaHorFront_attr_list))
                                group_elems_preview.append(PythonPart ("TD_Horitzontal_Front", parameter_list = novaHorFront.get_params_list(),
                                                        hash_value = novaHorFront.hash(), python_file = novaHorFront.filename(),
                                                        views = novaHorFront_views, matrix = matrix_Front,  common_props = novaHorFront_common_props, attribute_list = novaHorFront_attr_list))
                                #model_ele_list.append(AllplanBasisElements.ModelElement3D(novaHorFront_common_props, novaHorFront_brep))
                                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(novaHorFront_common_props, group_elems[len(group_elems)-1]))
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(novaHorFront_common_props, novaHorFront_brep))

                            '''
                            punt_central = matrix_Front[12] +30/2
                            pointUbi = AllplanGeo.Point3D(matrix_Front[12], matrix_Front[13] + 30/2, matrix_Front[14] + 30/2)
                            print("PointUbi: " + str(pointUbi))
                            polyhedronCentral = create_polyline_interior(build_ele, punt_central, 30, 30, True, pointUbi)
                            group_elems.append(polyhedronCentral)
                            '''

                    TDV_Int.afegir_encaixos_frontals(encaixosAux, listLong, False)
                    encaixosAux= []
                    despl = build_ele.desplYI.value
                    if build_ele.desplYI.value < 0 or (build_ele.EncaixHorInf.value and build_ele.desplYI.value <= 0):
                        despl = build_ele.BarraAmpleInf.value + build_ele.desplYI.value - build_ele.listDesplVerticalsTD.value[j].desplYAbs
                        orient = 'Dre'
                    else:
                        despl =  build_ele.dadesTDVertTD.value[j].BarraAltura - build_ele.desplYI.value + build_ele.listDesplVerticalsTD.value[j].desplYAbs
                        #despl =   build_ele.desplYI.value + build_ele.barraAlturaInf.value - build_ele.listDesplVerticalsTD.value[j].desplY
                        orient = 'Esq'
                    #if (build_ele.desplYI.value != 0 or build_ele.EncaixHorInf.value) and build_ele.invertirEncaixInf.value:

                    LongitudInf = build_ele.BarraAlturaInf.value
                    if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior" and build_ele.dadesTDVertTD.value[j].BarraInferior != 0:
                        if len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 7:
                            nHorInfCentenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-3])
                            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 6:
                            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 5:
                            nHorInf = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                        #tubVert = build_ele.dadesTDVertTD.value[j].BarraInferior[-3]
                        #tubHor = build_ele.dadesTDVertTD.value[j].BarraInferior[-1]
                        #nHorInf = int(tubVert) * NombreBarresHorInt + (int(tubHor)-1)
                        LongitudInf = build_ele.dadesTDHortInter.value[nHorInf].Altura
                        despl = build_ele.dadesTDHortInter.value[nHorInf].Ample +build_ele.dadesTDHortInter.value[nHorInf].desplY - build_ele.listDesplVerticalsTD.value[j].desplYAbs


                        if not build_ele.BarresVertList.value[j].EncaixInf:
                                desplY = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                desplYInf = build_ele.dadesTDHortInter.value[nHorInf].desplY
                                puntCentralY = build_ele.dadesTDVertTD.value[j].BarraAltura/2 + desplY
                                puntCentralYInf = build_ele.dadesTDHortInter.value[nHorInf].Ample/2 + desplYInf

                                if (puntCentralY > puntCentralYInf) :
                                    orient = "Dre"
                                    despl = build_ele.dadesTDHortInter.value[nHorInf].Ample +build_ele.dadesTDHortInter.value[nHorInf].desplY - build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                else:
                                    orient = "Esq"

                    if build_ele.EncaixHorInf.value and build_ele.invertirEncaixInf.value and not build_ele.dadesTDVertTD.value[j].EncaixInf:
                        #build_ele.dadesTDVertInter.value[j] = build_ele.dadesTDVertInter.value[j]._replace(FemellaInfe = True)
                        TDVertCollection = collections.namedtuple('StirrupList', 'BarraFront Orientacio Posicio Longitud Amplitud Profunditat Edit acabatEditar')
                        bob = TDVertCollection( BarraFront = not build_ele.dadesTDVertTD.value[j].EncaixInf,
                                                Orientacio = orient,
                                                Longitud = LongitudInf,
                                                Amplitud = build_ele.dadesTDVertTD.value[j].BarraAmple,
                                                Posicio = LongitudInf /2,
                                                Profunditat = despl ,#+ ,#10.0, #calcular prof matrixOffsetY???
                                                Edit = False,
                                                acabatEditar = False)
                        if not build_ele.SepararTDHoritzontalInf.value:
                            encaixosAux.append(bob)
                        else:
                            trobatInf = False
                            for nBarraInfEnc in range(0,build_ele.nBarresTDHoritzontalInf.value):
                                if not trobatInf and build_ele.listDesplVerticalsTD.value[j].desplXAbs >= build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].desplX and build_ele.listDesplVerticalsTD.value[j].desplXAbs <=  build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].desplX + build_ele.listDesplHoritzontalsInf.value[nBarraInfEnc].BarraLlargadaInf:
                                    encaixosAux.append(bob)
                                    trobatInf = True


                    if build_ele.desplYS.value <= 0 and build_ele.EncaixHorSup.value:
                        despl = build_ele.BarraAmpleSup.value + build_ele.desplYS.value - build_ele.listDesplVerticalsTD.value[j].desplY
                        orient = 'Dre'
                    else:
                        if (build_ele.EncaixHorSup.value):
                            despl =  build_ele.dadesTDVertTD.value[j].BarraAltura - build_ele.desplYS.value + build_ele.listDesplVerticalsTD.value[j].desplYAbs
                            orient = 'Esq'
                    #if build_ele.desplYS.value != 0 and build_ele.invertirEncaixSup.value:

                    LongitudSup = build_ele.BarraAlturaSup.value
                    if build_ele.dadesTDVertTD.value[j].BarraSuperior != "TD Superior":
                        if len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 7:
                            nHorSupCentenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-3])
                            nHorSupDecenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-2])
                            nHorSupUnitats = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                            nHorSup = nHorSupCentenes*100 + nHorSupDecenes*10 + nHorSupUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 6:
                            nHorSupDecenes = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-2])
                            nHorSupUnitats = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                            nHorSup = nHorSupDecenes*10 + nHorSupUnitats
                        elif len(build_ele.dadesTDVertTD.value[j].BarraSuperior) == 5:
                            nHorSup = int(build_ele.dadesTDVertTD.value[j].BarraSuperior[-1])
                        #tubVert = build_ele.dadesTDVertTD.value[j].BarraSuperior[-3]
                        #tubHor = build_ele.dadesTDVertTD.value[j].BarraSuperior[-1]
                        #nHorSup = int(tubVert) * NombreBarresHorInt + (int(tubHor)-1)
                        LongitudSup = build_ele.dadesTDHortInter.value[nHorSup].Altura
                        despl = build_ele.dadesTDHortInter.value[nHorSup].Ample +build_ele.dadesTDHortInter.value[nHorSup].desplY - build_ele.listDesplVerticalsTD.value[j].desplYAbs


                        if not build_ele.BarresVertList.value[j].EncaixSup:
                                desplY = build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                desplYSup = build_ele.dadesTDHortInter.value[nHorSup].desplY
                                puntCentralY = build_ele.dadesTDVertTD.value[j].BarraAltura/2 + desplY
                                puntCentralYSup = build_ele.dadesTDHortInter.value[nHorSup].Ample/2 + desplYSup
                                '''if (desplY < 0 and desplY < desplYSup) or (desplYSup > 0 and desplY < desplYSup):
                                    orientSupA = "Inf"
                                elif (desplY >= 0 and desplY > desplYSup) or (desplYSup <= 0 and desplY > desplYSup):
                                    orientSupA = "Sup"
                                '''
                                if (puntCentralY > puntCentralYSup) :
                                    orient = "Dre"
                                    despl = build_ele.dadesTDHortInter.value[nHorSup].Ample +build_ele.dadesTDHortInter.value[nHorSup].desplY - build_ele.listDesplVerticalsTD.value[j].desplYAbs
                                else:
                                    orient = "Esq"
                                    despl = (build_ele.dadesTDVertTD.value[j].BarraAltura + build_ele.listDesplVerticalsTD.value[j].desplYAbs) - build_ele.dadesTDHortInter.value[nHorSup].desplY



                    if build_ele.EncaixHorSup.value and build_ele.invertirEncaixSup.value :
                        TDVertCollection = collections.namedtuple('StirrupList', 'BarraFront Orientacio Posicio Longitud Amplitud Profunditat Edit acabatEditar')
                        bob = TDVertCollection( BarraFront = not build_ele.dadesTDVertTD.value[j].EncaixSup,
                                                Orientacio = orient,
                                                Longitud = LongitudSup,
                                                Amplitud = build_ele.dadesTDVertTD.value[j].BarraAmple,
                                                #Posicio = build_ele.BarraLlargadaVert.value - LongitudSup /2,
                                                Posicio = build_ele.dadesTDVertTD.value[j].BarraAlcada - LongitudSup /2,
                                                Profunditat = despl ,#+ ,#10.0, #calcular prof matrixOffsetY???
                                                Edit = False,
                                                acabatEditar = False)
                        encaixosAux.append(bob)

                    TDV_Int.afegir_encaixos_frontals(encaixosAux, listLong, True)
                except  Exception as e:
                    print("No s'ha creat la barra Frontal correctament. Error: ", e)


                TDV_Int_brep = TDV_Int.create()
                common_propsVert = TDV_Int.get_common_props()
                common_propsVertPrev = TDV_Int.get_common_props()
                inici = build_ele.nListBarresHor.value[j].Posicio
                final = build_ele.nListBarresHor.value[j].Posicio + build_ele.nListBarresHor.value[j].nTotal
                testEditBarraHorInterior = False
                testEditBarraVertInterior = False
                for posBarraHor in range(0, len(build_ele.BarresHorList.value)-1):#recorrer totes les Barres Horitzontals de cada vertical
                    if build_ele.BarresHorList.value[posBarraHor].Edit:
                        testEditBarraHorInterior = True
                for i in range(0,len(build_ele.BarresVertListToShow.value)):
                    if build_ele.BarresVertListToShow.value[i].Edit:
                        testEditBarraVertInterior = True


                tubEsIgual = False
                if build_ele.comprovarDEN.value:
                    tubEsIgual, DEN = compare_attributes(build_ele, doc, TDV_Int)
                if (tubEsIgual):
                    build_ele.DENVert.value = DEN
                if  mostrarActual == "TDV"+str(j) and not testEditBarraVertInterior and not testEditBarraHorInterior and nVer == j:
                    common_propsVertPrev.Color = 4 #verd
                if build_ele.dadesTDVertTD.value[j].vermell:
                    common_propsVert.Color = 6 #Vermell
                    #handle_list = TDV_Int.create_handles()

                cara_a, cara_a1, cara_a2 = dividirAtribut(str(TDV_Int.get_codi_cara_a()) )
                cara_b, cara_b1, cara_b2 = dividirAtribut(str(TDV_Int.get_codi_cara_b()) )
                cara_c, cara_c1, cara_c2 = dividirAtribut(str(TDV_Int.get_codi_cara_c()) )
                cara_d, cara_d1, cara_d2 = dividirAtribut(str(TDV_Int.get_codi_cara_d()) )

                cara_e, cara_e1, cara_e2 = dividirAtribut(str(TDV_Int.get_codi_cara_a_inv()) )
                cara_f, cara_f1, cara_f2 = dividirAtribut(str(TDV_Int.get_codi_cara_b_inv()) )
                cara_g, cara_g1, cara_g2 = dividirAtribut(str(TDV_Int.get_codi_cara_c_inv()) )
                cara_h, cara_h1, cara_h2 = dividirAtribut(str(TDV_Int.get_codi_cara_d_inv()) )
                TDV_Int_attr_list = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                                        AllplanBaseElements.AttributeString(2430, TDV_Int.get_codi_pestanyes()),
                                        AllplanBaseElements.AttributeString(2435, TDV_Int.get_codi_cancam()),
                                        #AllplanBaseElements.AttributeString(2432, TDV_Int.get_codi_colis()),
                                        #AllplanBaseElements.AttributeString(2429, TDV_Int.get_codi_encaix()),
                                        #AllplanBaseElements.AttributeString(2434, TDV_Int.get_codi_femella()),
                                        AllplanBaseElements.AttributeString(2431, TDV_Int.get_codi_mesures()),
                                        AllplanBaseElements.AttributeString(2433, TDV_Int.get_codi_pota()),
                                        AllplanBaseElements.AttributeString(2445, TDV_Int.get_seccio()),
                                        AllplanBaseElements.AttributeString(220, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(2455, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(2103, build_ele.DENVert.value),
                                        AllplanBaseElements.AttributeString(1083, build_ele.DENVert.value),
                                        AllplanBaseElements.AttributeString(1084, TDV_Int.get_seccio()),
                                        AllplanBaseElements.AttributeString(1085, TDV_Int.get_llargada()),
                                        AllplanBaseElements.AttributeString(1087, "Vertical"),
                                        AllplanBaseElements.AttributeString(508, "TD")]
                TDV_Ints_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsVert, TDV_Int_brep)])]
                TDV_Ints_viewsPrev = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsVertPrev, TDV_Int_brep)])]

                if j< len(matrixMostrar):
                    if matrixMostrar[j] and matrix0[12] - placement_mat[12]< build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:

                        if build_ele.dadesTDVertTD.value[j].esProvisional:
                            esExtrem = False
                            esFinal = False

                            if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior":
                                numsRetornar = [0,1,2,3]
                                if j == 0 or build_ele.listDesplVerticalsTD.value[j].desplXAbs == build_ele.listDesplVerticalsTD.value[0].desplXAbs:
                                    esExtrem = True
                                    esFinal = False
                                    numsRetornar = [1,3]#finalDre
                                if j == build_ele.IntegerTDSelector.value-1 or build_ele.listDesplVerticalsTD.value[build_ele.IntegerTDSelector.value-1].desplXAbs == build_ele.listDesplVerticalsTD.value[j].desplXAbs:
                                    esExtrem = True
                                    esFinal = True
                                    numsRetornar = [0,2]#finalEsq

                                if build_ele.dadesTDVertTD.value[j].esExtrem:
                                    esExtrem = True
                                    if build_ele.listDesplVerticalsTD.value[j].desplXAbs < build_ele.BarraLlargadaTD.value/2:
                                        esFinal = False
                                        numsRetornar = [1,3]#finalDre
                                    else:
                                        esFinal = True
                                        numsRetornar = [0,2]#finalEsq
                            else:
                                numsRetornar = [2,3,4]
                                if j == 0 or build_ele.listDesplVerticalsTD.value[j].desplXAbs == build_ele.listDesplVerticalsTD.value[0].desplXAbs:
                                    esExtrem = True
                                    esFinal = False
                                    numsRetornar = [3,4]#finalDre
                                if j == build_ele.IntegerTDSelector.value-1 or build_ele.listDesplVerticalsTD.value[build_ele.IntegerTDSelector.value-1].desplXAbs == build_ele.listDesplVerticalsTD.value[j].desplXAbs:
                                    esExtrem = True
                                    esFinal = True
                                    numsRetornar = [2,4]#finalEsq

                                if build_ele.dadesTDVertTD.value[j].esExtrem:
                                    esExtrem = True
                                    if build_ele.listDesplVerticalsTD.value[j].desplXAbs < build_ele.BarraLlargadaTD.value/2:
                                        esFinal = False
                                        numsRetornar = [3,4]#finalDre
                                    else:
                                        esFinal = True
                                        numsRetornar = [2,4]#finalEsq




                            if crear_LProvisionals(build_ele,j,matrix0, esExtrem, esFinal, 1) != []:


                                for numL in numsRetornar:
                                    #if esFinal:
                                    listLProvisional = crear_LProvisionals(build_ele,j,matrix0, esExtrem, esFinal, numL)
                                    if len(listLProvisional) > 2:
                                        group_elems.append(listLProvisional[0])
                                        group_elems_preview.append(listLProvisional[0])
                                        preview_ele_list.append(AllplanBasisElements.ModelElement3D(listLProvisional[1], listLProvisional[2]))


                        vertical_BrepObject5 = verticalPPOBject5.create()
                        vertical_BrepObject5A = verticalPPOBject5A.create()
                        vertical_views_object5 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectVert, vertical_BrepObject5)])]
                        vertical_views_object5_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectVert2, vertical_BrepObject5A)])]

                        matrix0C = AllplanGeo.Matrix3D()
                        matrix0C.SetValue(12, matrix0[12] - 5)
                        matrix0C.SetValue(13, matrix0[13] )
                        matrix0C.SetValue(14, matrix0[14] - 5)

                        #if build_ele.dadesTDVertTD.value[j].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
                        if build_ele.MostrarCavitatsRecess.value:
                            group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5.hash(), python_file = verticalPPOBject5.filename(),
                                                    views = vertical_views_object5, matrix = matrix0C, common_props = common_propsObjectVert, attribute_list = table_attr_listObject))
                            group_elems_preview.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5.hash(), python_file = verticalPPOBject5.filename(),
                                                    views = vertical_views_object5, matrix = matrix0C, common_props = common_propsObjectVert, attribute_list = table_attr_listObject))
                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert, verticalPPOBject5))
                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert, group_elems[len(group_elems)-1]))
                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert, verticalPPOBject5))

                        #if build_ele.dadesTDVertTD.value[j].MostrarCavitat and build_ele.MostrarCavitats.value:
                        if build_ele.MostrarCavitats.value:
                            group_elems.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5A.hash(), python_file = verticalPPOBject5A.filename(),
                                                    views = vertical_views_object5_2, matrix = matrix0C, common_props = common_propsObjectVert2, attribute_list = table_attr_listObject))
                            group_elems_preview.append(PythonPart ("Cavitat_Vertical", parameter_list = get_var_chair_vert(build_ele, j, []),
                                                    hash_value = verticalPPOBject5A.hash(), python_file = verticalPPOBject5A.filename(),
                                                    views = vertical_views_object5_2, matrix = matrix0C, common_props = common_propsObjectVert2, attribute_list = table_attr_listObject))
                            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert2, verticalPPOBject5A))
                            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert2, group_elems[len(group_elems)-1]))
                            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectVert2, verticalPPOBject5A))

                        group_elems.append(PythonPart ("PP_TD_Vertical", parameter_list = get_var_chair_vert(build_ele, j, FemellesAux),
                                                hash_value = TDV_Int.hash(), python_file = TDV_Int.filename(),
                                                views = TDV_Ints_views, matrix = matrix0, common_props = common_propsVert, attribute_list = TDV_Int_attr_list))
                        group_elems_preview.append(PythonPart ("PP_TD_Vertical", parameter_list = get_var_chair_vert(build_ele, j, FemellesAux),
                                                hash_value = TDV_Int.hash(), python_file = TDV_Int.filename(),
                                                views = TDV_Ints_viewsPrev, matrix = matrix0, common_props = common_propsVertPrev, attribute_list = TDV_Int_attr_list))

                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsVert, TDV_Int_brep))
                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsVert, group_elems[len(group_elems)-1]))
                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsVert, TDV_Int_brep))
                        #placement_matrix.append(matrix0)


                        if build_ele.listDesplVerticalsTD.value[j].mostrarLiniaVertA:
                            punt_central = matrix0[12] + build_ele.listDesplVerticalsTD.value[j].desplX + build_ele.dadesTDVertTD.value[j].BarraAltura/2
                            pointUbi = AllplanGeo.Point3D(matrix0[12] + build_ele.dadesTDVertTD.value[j].BarraAmple/2 + build_ele.listDesplVerticalsTD.value[j].desplLinA, matrix0[13] + build_ele.dadesTDVertTD.value[j].BarraAltura/2 , matrix0[14])
                            if len(build_ele.dadesTDVertTD.value[j].linia)< 6  or build_ele.dadesTDVertTD.value[j].linia == '':
                                build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(linia = "tipus 1")
                            linia = build_ele.dadesTDVertTD.value[j].linia[len(build_ele.dadesTDVertTD.value[j].linia)-1]
                            if len(build_ele.dadesTDVertTD.value[j].layer) == 0:
                                build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(layer = "TD_FIXACIO")
                            layer = build_ele.dadesTDVertTD.value[j].layer
                            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDVertTD.value[j].BarraAltura, BarrallargadaVert, False, pointUbi, int(linia), layer)
                            if polyhedronCentral != []:
                                group_elems.append(polyhedronCentral[0])
                                group_elems_preview.append(polyhedronCentral[0])
                                group_elems.append(polyhedronCentral[3])
                                group_elems_preview.append(polyhedronCentral[3])
                                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                        if build_ele.listDesplVerticalsTD.value[j].mostrarLiniaVertB:
                            punt_central = matrix0[12] + build_ele.listDesplVerticalsTD.value[j].desplX + build_ele.dadesTDVertTD.value[j].BarraAltura/2
                            pointUbi = AllplanGeo.Point3D(matrix0[12] + build_ele.dadesTDVertTD.value[j].BarraAmple/2 + build_ele.listDesplVerticalsTD.value[j].desplLinB, matrix0[13] + build_ele.dadesTDVertTD.value[j].BarraAltura/2 , matrix0[14])
                            if len(build_ele.dadesTDVertTD.value[j].linia)< 6  or build_ele.dadesTDVertTD.value[j].linia == '':
                                build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(linia = "tipus 1")
                            linia = build_ele.dadesTDVertTD.value[j].linia[len(build_ele.dadesTDVertTD.value[j].linia)-1]
                            if len(build_ele.dadesTDVertTD.value[j].layer) == 0:
                                build_ele.dadesTDVertTD.value[j] = build_ele.dadesTDVertTD.value[j]._replace(layer = "TD_FIXACIO")
                            layer = build_ele.dadesTDVertTD.value[j].layer
                            polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesTDVertTD.value[j].BarraAltura, BarrallargadaVert, False, pointUbi, int(linia), layer)
                            if polyhedronCentral != []:
                                group_elems.append(polyhedronCentral[0])
                                group_elems_preview.append(polyhedronCentral[0])
                                group_elems.append(polyhedronCentral[3])
                                group_elems_preview.append(polyhedronCentral[3])
                                #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                                #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))

                        if build_ele.MostrarTDNums.value:
                            numeroTDV = create_num_on_view(build_ele, j, matrix0)
                            if numeroTDV != [] and len(numeroTDV) > 2:
                                #group_elems.append(numeroTDV)
                                group_elems_preview.append(numeroTDV[0])
                                #preview_ele_list.append(AllplanBasisElements.ModelElement3D(numeroTDV[1],numeroTDV[2]))


                        contadorPPV += 1
                j += 1
        except  Exception as e:
            print("No s'han creat Barres ["+str(j)+"]: ", e)

    #Barres reforç
    try:
        inici = 0
        final = build_ele.NumBarresRef.value


        for posBarraRef in range(inici, final):#recorrer totes les Barres Reforcs de cada vertical
            #----------------------- Afegir Barra Ref -----------------------------------
            if posBarraRef >= len(build_ele.BarresRefListTD.value):
                set_values_barresRef(build_ele, posBarraRef)


            if nRef == posBarraRef and build_ele.SelectorPPTD.value == 4:

                #si esta buit
                while len(build_ele.dadesENReftInterTD.value) <= posBarraRef:
                    set_valors_Ref_ini(build_ele, posBarraRef)
                if build_ele.dadesENReftInterTD.value[posBarraRef].acabatEditar == False:
                    build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(acabatEditar = True)
                #si no estan mostrats
                #if  build_ele.BarresRefListToShowTD.value[0].acabatEditar == False and nRef == posBarraRef: #al clicar a edit
                if  build_ele.valueAntReforc.value != nRef and nRef == posBarraRef: #al clicar a edit

                    #build_ele.BarresRefListTD.value[posBarraRef] = build_ele.BarresRefListTD.value[posBarraRef]._replace(Edit = True)
                    #mostrar valors
                    mostrar_valors_Ref(build_ele, posBarraRef)
                    build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(estaEditant = True)
                    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(acabatEditar = True)

                #guardar valors
                guardar_valors_Ref(build_ele, posBarraRef)
            else:
                if len(build_ele.dadesENReftInterTD.value) <= posBarraRef:
                    set_valors_Ref_ini(build_ele, posBarraRef)
                if build_ele.dadesENReftInterTD.value[posBarraRef].acabatEditar == True and nRef == posBarraRef:
                    #guardar valors
                    #guardar_valors_Ref(build_ele, j, posBarraRef - inici)
                    #mostrar_valors_actuals(build_ele, posBarraRef)
                    if build_ele.SelectorPPTD.value == 2:
                        mostrar_valors_actuals(build_ele, nVer)
                    elif build_ele.SelectorPPTD.value == 1:
                        print("build_ele.SelectorPPTD.value: " + str(build_ele.SelectorPPTD.value))
                    elif build_ele.SelectorPPTD.value == 3:
                        print("build_ele.SelectorPPTD.value: " + str(build_ele.SelectorPPTD.value))
                    build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(acabatEditar = False)
                    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(acabatEditar = False)
            if len(build_ele.dadesENReftInterTD.value) <= posBarraRef  :
                set_valors_Ref_ini(build_ele, posBarraRef)
            if len(build_ele.EncaixRefInt.value) <= posBarraRef:
                set_valors_Ref_ini(build_ele, posBarraRef)



            llargada = build_ele.BarresRefListTD.value[posBarraRef].Longitud
            BarraIniciRef = 0
            BarraFinalRef = 1
            if len(build_ele.BarresRefListTD.value[posBarraRef].BarraIni) > 3:
                if len(build_ele.BarresRefListTD.value[posBarraRef].BarraIni) == 7:
                    nHorInfCentenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-3])
                    nHorInfDecenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-2])
                    nHorInfUnitats = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-1])
                    BarraIniciRef = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.BarresRefListTD.value[posBarraRef].BarraIni) == 6:
                    nHorInfDecenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-2])
                    nHorInfUnitats = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-1])
                    BarraIniciRef = nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.BarresRefListTD.value[posBarraRef].BarraIni) == 5:
                    BarraIniciRef = int(build_ele.BarresRefListTD.value[posBarraRef].BarraIni[-1])

            if len(build_ele.BarresRefListTD.value[posBarraRef].BarraFin) > 3:
                if len(build_ele.BarresRefListTD.value[posBarraRef].BarraFin) == 7:
                    nHorInfCentenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-3])
                    nHorInfDecenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-2])
                    nHorInfUnitats = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-1])
                    BarraFinalRef = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.BarresRefListTD.value[posBarraRef].BarraFin) == 6:
                    nHorInfDecenes = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-2])
                    nHorInfUnitats = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-1])
                    BarraFinalRef = nHorInfDecenes*10 + nHorInfUnitats
                elif len(build_ele.BarresRefListTD.value[posBarraRef].BarraFin) == 5:
                    BarraFinalRef = int(build_ele.BarresRefListTD.value[posBarraRef].BarraFin[-1])


            while len(build_ele.dadesENReftInterTD.value) <= posBarraRef:
                set_valors_Ref_ini(build_ele, posBarraRef)

            if build_ele.BarresRefListTD.value[posBarraRef].BarraRef:
                llargada = build_ele.BarresRefListTD.value[posBarraRef].Longitud
                if build_ele.BarresRefListTD.value[posBarraRef].AutoLongitud:
                    if build_ele.listDesplVerticalsTD.value[BarraFinalRef].desplXAbs -(build_ele.listDesplVerticalsTD.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertTD.value[BarraIniciRef].BarraAmple) > 0:
                        llargada = build_ele.listDesplVerticalsTD.value[BarraFinalRef].desplXAbs - build_ele.dadesTDVertTD.value[BarraFinalRef].BarraAmple/2 -(build_ele.listDesplVerticalsTD.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertTD.value[BarraIniciRef].BarraAmple/2 )- build_ele.dadesENReftInterTD.value[posBarraRef].desplX
                    else:
                        print("El segon tub ha d'estar en una posicio mes avançada que el primer")
                        ctypes.windll.user32.MessageBoxW(0, "El segon tub ha d'estar en una posicio mes avançada que el primer, selecciona els tubs inicial i final de forma correcta del reforç '" + str(posBarraRef) +"' (longitud " + str(build_ele.listDesplVerticalsTD.value[BarraFinalRef].desplXAbs -(build_ele.listDesplVerticalsTD.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertTD.value[BarraIniciRef].BarraAmple)) + ")", 0)
                        llargada = 30
                else:
                    llargada = build_ele.BarresRefListTD.value[posBarraRef].Longitud


                encaixos = []

                reforcRef = PP_TD_Horitzontal_reforc(random.random() * 3600, build_ele.dadesENReftInterTD.value[posBarraRef].Ample, build_ele.dadesENReftInterTD.value[posBarraRef].Altura,llargada-5 , build_ele.dadesENReftInterTD.value[posBarraRef].Gruix, False,# (ENV BarraLlargada), BarraAmple, BarraAltura,BarraLlargada( ), BarraGruix,
                                    build_ele.dadesENReftInterTD.value[posBarraRef].IsUseGlobalProp, build_ele.dadesENReftInterTD.value[posBarraRef].FounColor, build_ele.dadesENReftInterTD.value[posBarraRef].BarraLayer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    encaixos) #EncaixosPar))
                if not reforcRef.is_valid():
                    return[]

                matrix_AuxR = AllplanGeo.Matrix3D()
                matrix_AuxR.SetValue(12, build_ele.listDesplVerticalsTD.value[BarraIniciRef].desplXAbs + build_ele.dadesTDVertTD.value[BarraIniciRef].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 + 2.5  + build_ele.dadesENReftInterTD.value[posBarraRef].desplX)
                matrix_AuxR.SetValue(13, build_ele.listDesplVerticalsTD.value[BarraIniciRef].desplYAbs + build_ele.dadesENReftInterTD.value[posBarraRef].desplY)
                matrix_AuxR.SetValue(14, build_ele.BarresRefListTD.value[posBarraRef].Posicio)

                TranslationFather = matrix_AuxR
                TranslationFather.SetValue(12, placement_mat[12] + matrix_AuxR[12])
                TranslationFather.SetValue(13, placement_mat[13] + matrix_AuxR[13])
                TranslationFather.SetValue(14, placement_mat[14] + matrix_AuxR[14])
                matrix_AuxR  = TranslationFather

                table_brepAuxR = reforcRef.create()
                common_propsR = reforcRef.get_common_props()
                common_propsR.Layer = 40001#56811#build_ele.BarraLayer.value#64178
                common_propsR.Color = 1

                reforcRefDEN= "V"
                tubEsIgual = False
                if build_ele.comprovarDEN.value:
                    tubEsIgual, DEN = compare_attributes(build_ele, doc, reforcRef)
                if (tubEsIgual):
                    reforcRefDEN = DEN

                if  mostrarActual == "TDR"+str(nRef) and build_ele.BarresRefListTD.value[posBarraRef].BarraRef and nRef == posBarraRef :
                    common_propsR.Color = 6 #Vermell

                cara_a, cara_a1, cara_a2 = dividirAtribut(str(reforcRef.get_codi_cara_a()) )
                cara_b, cara_b1, cara_b2 = dividirAtribut(str(reforcRef.get_codi_cara_b()) )
                cara_c, cara_c1, cara_c2 = dividirAtribut(str(reforcRef.get_codi_cara_c()) )
                cara_d, cara_d1, cara_d2 = dividirAtribut(str(reforcRef.get_codi_cara_d()) )

                cara_e, cara_e1, cara_e2 = dividirAtribut(str(reforcRef.get_codi_cara_a_inv()) )
                cara_f, cara_f1, cara_f2 = dividirAtribut(str(reforcRef.get_codi_cara_b_inv()) )
                cara_g, cara_g1, cara_g2 = dividirAtribut(str(reforcRef.get_codi_cara_c_inv()) )
                cara_h, cara_h1, cara_h2 = dividirAtribut(str(reforcRef.get_codi_cara_d_inv()) )

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


                                        AllplanBaseElements.AttributeString(2431, reforcRef.get_codi_mesures()),
                                        AllplanBaseElements.AttributeString(2445, reforcRef.get_seccio()),
                                        AllplanBaseElements.AttributeString(220, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(2103, "V"),
                                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),
                                        AllplanBaseElements.AttributeString(1083, reforcRefDEN),
                                        AllplanBaseElements.AttributeString(1084, reforcRef.get_seccio()),
                                        AllplanBaseElements.AttributeString(1085, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(220, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(2455, reforcRef.get_llargada()),
                                        AllplanBaseElements.AttributeString(508, "TD")]
                table_viewsAuxR = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsR, table_brepAuxR)])]

                colorCavitat = getColorCavitat(build_ele.dadesENReftInterTD.value[posBarraRef].Ample)
                common_propsObject = AllplanBaseElements.CommonProperties()
                common_propsObject.Layer = 40055#56811#build_ele.BarraLayer.value#64178
                common_propsObject.Color = colorCavitat

                common_propsObject2 = AllplanBaseElements.CommonProperties()
                common_propsObject2.Layer = 40054#56811#build_ele.BarraLayer.value#64178
                common_propsObject2.Color = colorCavitat


                '''
                ReforcPPOBjectR = PP_TD_Horitzontal_reforc(random.random() * 3600, build_ele.dadesENReftInterTD.value[posBarraRef].Ample, build_ele.dadesENReftInterTD.value[posBarraRef].Altura+10,llargada, build_ele.dadesENReftInterTD.value[posBarraRef].Gruix,False,# , BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                        False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                        [])
                '''

                ReforcPPOBjectR = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesENReftInterTD.value[posBarraRef].Ample, build_ele.dadesENReftInterTD.value[posBarraRef].Altura+10, llargada, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])

                ReforcPPOBjectR2 = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.dadesENReftInterTD.value[posBarraRef].Ample, build_ele.dadesENReftInterTD.value[posBarraRef].Altura+10, llargada, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [], [],#ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])

                #if not ReforcPPOBjectR.is_valid():
                #    return[]

                Reforc_BrepObjectR = ReforcPPOBjectR.create()
                Reforc_views_objectR = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, Reforc_BrepObjectR)])]

                Reforc_BrepObjectR2 = ReforcPPOBjectR2.create()
                Reforc_views_objectR2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, Reforc_BrepObjectR2)])]

                matrix_AuxRC = AllplanGeo.Matrix3D()
                matrix_AuxRC.SetValue(12, matrix_AuxR[12] - 2.5 )
                matrix_AuxRC.SetValue(13, matrix_AuxR[13] )
                matrix_AuxRC.SetValue(14, matrix_AuxR[14] - 5)

                if build_ele.MostrarCavitatsRecess.value:
                    group_elems.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR.get_params_list(),
                                        hash_value = ReforcPPOBjectR.hash(), python_file = ReforcPPOBjectR.filename(),
                                        views = Reforc_views_objectR, matrix = matrix_AuxRC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                    group_elems_preview.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR.get_params_list(),
                                        hash_value = ReforcPPOBjectR.hash(), python_file = ReforcPPOBjectR.filename(),
                                        views = Reforc_views_objectR, matrix = matrix_AuxRC, common_props = common_propsObject, attribute_list = table_attr_listObject))
                if build_ele.MostrarCavitats.value:
                    group_elems.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR2.get_params_list(),
                                        hash_value = ReforcPPOBjectR2.hash(), python_file = ReforcPPOBjectR2.filename(),
                                        views = Reforc_views_objectR2, matrix = matrix_AuxRC, common_props = common_propsObject2, attribute_list = table_attr_listObject))
                    group_elems_preview.append(PythonPart ("Cavitat_Reforc", parameter_list = ReforcPPOBjectR2.get_params_list(),
                                        hash_value = ReforcPPOBjectR2.hash(), python_file = ReforcPPOBjectR2.filename(),
                                        views = Reforc_views_objectR2, matrix = matrix_AuxRC, common_props = common_propsObject2, attribute_list = table_attr_listObject))


                group_elems.append(PythonPart ("PP_TD_Reforc", parameter_list = reforcRef.get_params_list(),
                                        hash_value = reforcRef.hash(), python_file = reforcRef.filename(),
                                        views = table_viewsAuxR, matrix = matrix_AuxR, common_props = common_propsR, attribute_list = table_attr_listAux))
                group_elems_preview.append(PythonPart ("PP_TD_Reforc", parameter_list = reforcRef.get_params_list(),
                                        hash_value = reforcRef.hash(), python_file = reforcRef.filename(),
                                        views = table_viewsAuxR, matrix = matrix_AuxR, common_props = common_propsR, attribute_list = table_attr_listAux))


                if build_ele.dadesENReftInterTD.value[posBarraRef].mostrarLiniaVertA:
                    punt_central = matrix_AuxR[12] + build_ele.dadesENReftInterTD.value[posBarraRef].desplX + build_ele.dadesENReftInterTD.value[posBarraRef].Altura/2
                    pointUbi = AllplanGeo.Point3D(matrix_AuxR[12], matrix_AuxR[13] + build_ele.dadesENReftInterTD.value[posBarraRef].Ample/2 + build_ele.dadesENReftInterTD.value[posBarraRef].desplLinA, matrix_AuxR[14] + build_ele.dadesENReftInterTD.value[posBarraRef].Altura/2)
                    if len(build_ele.dadesENReftInterTD.value[posBarraRef].linia) == 0:
                        build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(linia = "Tipus 1")
                    linia = build_ele.dadesENReftInterTD.value[posBarraRef].linia[len(build_ele.dadesENReftInterTD.value[posBarraRef].linia)-1]
                    if len(build_ele.dadesENReftInterTD.value[posBarraRef].layer) == 0:
                        build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(layer = "TD_FIXACIO")
                    layer = build_ele.dadesENReftInterTD.value[posBarraRef].layer
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesENReftInterTD.value[posBarraRef].Altura, llargada-2, True, pointUbi, int(linia), layer)
                    if polyhedronCentral != []:
                        group_elems.append(polyhedronCentral[0])
                        group_elems_preview.append(polyhedronCentral[0])
                        group_elems.append(polyhedronCentral[3])
                        group_elems_preview.append(polyhedronCentral[3])
                        #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                if build_ele.dadesENReftInterTD.value[posBarraRef].mostrarLiniaVertB:
                    punt_central = matrix_AuxR[12] + build_ele.dadesENReftInterTD.value[posBarraRef].desplX + build_ele.dadesENReftInterTD.value[posBarraRef].Altura/2
                    pointUbi = AllplanGeo.Point3D(matrix_AuxR[12], matrix_AuxR[13] + build_ele.dadesENReftInterTD.value[posBarraRef].Ample/2 + build_ele.dadesENReftInterTD.value[posBarraRef].desplLinB, matrix_AuxR[14] + build_ele.dadesENReftInterTD.value[posBarraRef].Altura/2)
                    if len(build_ele.dadesENReftInterTD.value[posBarraRef].linia) == 0:
                        build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(linia = "Tipus 1")
                    linia = build_ele.dadesENReftInterTD.value[posBarraRef].linia[len(build_ele.dadesENReftInterTD.value[posBarraRef].linia)-1]
                    if len(build_ele.dadesENReftInterTD.value[posBarraRef].layer) == 0:
                        build_ele.dadesENReftInterTD.value[posBarraRef] = build_ele.dadesENReftInterTD.value[posBarraRef]._replace(layer = "TD_FIXACIO")
                    layer = build_ele.dadesENReftInterTD.value[posBarraRef].layer
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.dadesENReftInterTD.value[posBarraRef].Altura, llargada-2, True, pointUbi, int(linia), layer)
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

    except  Exception as e:
        print("No s'han creat Barres Reforç ", e)

    try:
        inici = 0
        final = 1
        #PREMARC
        for posBarraIncl in range(inici, final):#recorrer totes les Barres Inclinades
            if posBarraIncl >= len(build_ele.dadesTDInclinades.value):
                set_valors_incl(build_ele, posBarraIncl)
            #----------------------- Afegir Barra Incl -----------------------------------
            #inclinatPP = PP_EN_Inclinat(random.random() * 3600,30 , build_ele.dadesTDInclinades.value[posBarraIncl].Altura, build_ele.dadesTDInclinades.value[posBarraIncl].Llargada, build_ele.BarraGruix.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
            #                    build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value # IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
            #                    ) #EncaixosPar)
            inclinatPP = PP_EN_Premarc(random.random() * 3600,30 , build_ele.dadesTDInclinades.value[posBarraIncl].Altura, build_ele.dadesTDInclinades.value[posBarraIncl].Llargada, 1.5,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, 17, 40120 # IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
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

            inclinatfDEN= "Premarc."
            tubEsIgual = False
            if build_ele.comprovarDEN.value:
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
                                AllplanBaseElements.AttributeString(507, build_ele.dadesTDInclinades.value[posBarraIncl].nom ),
                                AllplanBaseElements.AttributeString(508, "E-I")]
            table_views_incl = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsIncl, horitzontal_Brep)])]


            z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                        point2=  AllplanGeo.Point3D(0,-1,0))

            # ---- rotation ----

            vectorI1 = AllplanGeo.Matrix3D()
            #vectorI1.Rotation(z_axis, AllplanGeo.Angle.FromDeg(build_ele.dadesTDInclinades.value[posBarraIncl].Angle))

            #vectorI1.SetValue(12, build_ele.desplXI.value)
            vectorI1.SetValue(12, build_ele.dadesTDInclinades.value[posBarraIncl].desplX)

            #vectorI1.SetValue(13, build_ele.desplYI.value)
            vectorI1.SetValue(13, build_ele.dadesTDInclinades.value[posBarraIncl].desplY)

            vectorI1.SetValue(14, 0)

            TranslationFather = vectorI1
            TranslationFather.SetValue(12, placement_mat[12] + vectorI1[12])
            TranslationFather.SetValue(13, placement_mat[13] + vectorI1[13])
            TranslationFather.SetValue(14, placement_mat[14] + vectorI1[14])
            vectorI1  = TranslationFather


            #if build_ele.dadesTDInclinades.value[posBarraIncl].MostrarInclinat and build_ele.dadesBalcFines.value[nBalcFin].Mostrar:
            if build_ele.dadesTDInclinades.value[posBarraIncl].MostrarInclinat and build_ele.MostrarBalconera.value:
                group_elems.append(PythonPart ("PP_EN_Horitzontal", parameter_list = inclinatPP.get_params_list(),
                                        hash_value = inclinatPP.hash(), python_file = inclinatPP.filename(),
                                        views = table_views_incl, matrix = vectorI1, common_props = common_propsIncl, attribute_list = table_attr_list_incl))
                group_elems_preview.append(PythonPart ("PP_EN_Horitzontal", parameter_list = inclinatPP.get_params_list(),
                                        hash_value = inclinatPP.hash(), python_file = inclinatPP.filename(),
                                        views = table_views_incl, matrix = vectorI1, common_props = common_propsIncl, attribute_list = table_attr_list_incl))



    except Exception as e:
        print("no s'ha creat Premarc: ", e)

    if build_ele.SepararTDHoritzontalInf.value:
        for nBarresInf in range(1, build_ele.nBarresTDHoritzontalInf.value):
            elements , lHoritzontalPP, elements_model_eleList = crear_barres_inferiors_multiples(build_ele, doc, nBarresInf, mostrarActual, placement_mat)
            listHoritzontalPP.append(lHoritzontalPP)
            listElements.append(elements)
            #for model in elements_model_eleList:
            #    model_ele_list2.append(model)
            #    preview_ele_list.append(model)
    if build_ele.SepararTDHoritzontalSup.value:
        for nBarresInf in range(1, build_ele.nBarresTDHoritzontalSup.value):
            elements , lHoritzontalPP, elements_model_eleList = crear_barres_superiors_multiples(build_ele, doc, nBarresInf, mostrarActual, placement_mat)
            listHoritzontalPP.append(lHoritzontalPP)
            listElements.append(elements)

    '''
    for pphor in listHoritzontalPP:
        horitzontal_BrepppHor = pphor.create()
    '''
    for elements in listElements:
        for elenment in elements:
            if elenment != []:
                group_elems.append(elenment)
                group_elems_preview.append(elenment)
                #model_ele_list.append(elenment)

    #definir atributs de la Barra Horitzontal Inferior
    #horitzontal_Brep = horitzontalPP.create()


    pythonpartgroup = PythonPartGroup (build_ele.NomTD.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems)

    pythonpartgroup_preview = PythonPartGroup (build_ele.NomTD.value, build_ele.get_params_list(), build_ele.get_hash(),
                                       build_ele.pyp_file_name, group_elems_preview)


    model_elem_list = pythonpartgroup.create()
    model_elem_list_preview = pythonpartgroup_preview.create()

    #for macro in model_elem_list:
        #print(macro)
        #print(macro.GetCommonProperties())
        ##macro_prop             = AllplanBasisElements.MacroProperties()
        ##macro_prop.LinkType    = AllplanBasisElements.LinkType.eLinkToRoom
        ##macro_prop.LinkType    = AllplanBasisElements.eLinkToRoom
        #macro1 = macro.GetAttributes()
        #macro1.LinkType    = AllplanBasisElements.LinkType.eLinkToRoom

        #macro.append(macro_prop)

    #macroGroupElem = model_elem_list[len(model_elem_list)-1]
    #macro_prop = macroGroupElem.MacroGroupProperties
    #macro_prop.LinkType    = AllplanBasisElements.LinkType.eLinkToRoom
    #macroGroupElem.MacroGroupProperties.LinkType = AllplanBasisElements.LinkType.eLinkToRoom

    #for macro in model_elem_list_preview:
    #    print(macro)

    #guardar_valors_inici(build_ele,nVer)
    build_ele.SelectorPPAnt.value = build_ele.SelectorPPTD.value
    build_ele.SelectorTDVAnt.value = nVer
    build_ele.DistanciaEntreTDAnt.value = build_ele.DistanciaEntreTD.value
    build_ele.BarraLlargadaAnt.value = build_ele.BarraLlargadaTD.value
    build_ele.SelectorTDHTotalAnt.value = nHorInt
    build_ele.SelectorTDTipusHor.value = mostrarActual
    build_ele.valueAntReforc.value = nRef




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
    #                            #preview_elements=   model_elem_list_preview)

    #return CreateElementResult(model_elem_list, handle_list)
    #return CreateElementResult(model_ele_list2, preview_ele_list)
    #return (model_elem_list, handle_list)

def create_polyline_interior(build_ele, punt_central, llargadaX, llargadaZ, isHor, pointUbi, linia = 1, layer = "TD_FIXACIO", posYdiferent = 200):

    posX = pointUbi.X
    posY = pointUbi.Y
    posZ = pointUbi.Z

    llargadaY = 1

    common_propsLinia = AllplanBaseElements.CommonProperties()
    common_propsLinia.GetGlobalProperties()

    common_propsLinia.Layer = 40036#(TD_FIXACIO)
    if layer == "TD_NO_CARAGOLAR":
        common_propsLinia.Layer = 40037#(TD_NO_CARAGOLAR)
    if layer == "KN_ELECTRICITAT_REINFORCEMENT" or layer == "40073" or layer == 40073:
        common_propsLinia.Layer = 40073#(KN_ELECTRICITAT_REINFORCEMENT)
    if layer == "KN_AIGUA_REINFORCEMENT" or layer == "40074"  or layer == 40074:
        common_propsLinia.Layer = 40074#(KN_AIGUA_REINFORCEMENT)
    common_propsLinia.Stroke = linia
    if linia == 2:#tipo de trazo 97
        common_propsLinia.Stroke = 97

    #------------------ Set the values
    if (isHor):
        liniaInterior = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        if not liniaInterior.is_valid():
            return[]

        liniaInterior_brep = liniaInterior.create()
        liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                   AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                   AllplanBaseElements.AttributeString(1083, " ")]
        liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]

        vectorPOS = AllplanGeo.Matrix3D()

        #z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
        #                        point2=  AllplanGeo.Point3D(0,1,0))
        #vectorPOS.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))

        vectorPOS.SetValue(12, posX )#+ build_ele.desplXI.value )
        vectorPOS.SetValue(13, 0 - posYdiferent)#+ build_ele.desplYI.value )
        vectorPOS.SetValue(14, posZ )

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.SetValue(12, posX )#+ build_ele.desplXI.value )
        vectorPOSInv.SetValue(13, posYdiferent + 60)#+ build_ele.desplYI.value )
        vectorPOSInv.SetValue(14, posZ )

        return [PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list),
                common_propsLinia,
                liniaInterior_brep,
                PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOSInv, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list)
                ]

    else:

        liniaInterior = LiniaInterior(random.random() * 3600, llargadaZ, isHor)
        if not liniaInterior.is_valid():
            return[]

        liniaInterior_brep = liniaInterior.create()
        liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                   AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                   AllplanBaseElements.AttributeString(1083, " ")]
        liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]
        handle_list = liniaInterior.create_handles()

        vectorPOS = AllplanGeo.Matrix3D()
        #z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
        #                        point2=  AllplanGeo.Point3D(0,0,1))
        #vectorPOS.Rotation(z_axis, AllplanGeo.Angle.FromDeg(45))

        vectorPOS.SetValue(12, posX )
        vectorPOS.SetValue(13, posY - 0.25)
        vectorPOS.SetValue(13, 0 - posYdiferent)
        vectorPOS.SetValue(14, posZ )

        vectorPOSInv = AllplanGeo.Matrix3D()
        vectorPOSInv.SetValue(12, posX )
        vectorPOSInv.SetValue(13, posYdiferent + 60)
        vectorPOSInv.SetValue(14, posZ )


        return [PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list),
                common_propsLinia,
                liniaInterior_brep,
                PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                    hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                    views = liniaInterior_views, matrix = vectorPOSInv, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list)
                ]

def get_var_chair_vert(build_ele, i, FemellesAux):
    '''
    passar totes les variables entrades per l'usuari a String
    get: i -> posicio[] de la barra a retornar
         FemellesAux -> lista de femelles a afegir

    return: retorna llista de strings dels parametres

    '''
    param_list = []
    #param_list.append ("BarraAmple = %s\n" % build_ele.BarraAmpleVert.value)
    param_list.append ("BarraAmpleVert = %s\n" % build_ele.BarraAmpleVert.value)
    #param_list.append ("BarraAltura = %s\n" % build_ele.BarraAlturaVert.value)
    param_list.append ("BarraAlturaVert = %s\n" % build_ele.BarraAlturaVert.value)
    #param_list.append ("BarraLlargada = %s\n" % build_ele.BarraLlargadaVert.value)
    param_list.append ("BarraLlargadaVert = %s\n" % build_ele.BarraLlargadaVert.value)
    #param_list.append ("BarraGruix = %s\n" % build_ele.BarraGruixVert.value)
    param_list.append ("BarraGruixVert = %s\n" % build_ele.BarraGruixVert.value)
    #param_list.append ("IsUseGlobalProp = %s\n" % build_ele.IsUseGlobalPropVert.value)
    param_list.append ("IsUseGlobalPropVert = %s\n" % build_ele.IsUseGlobalPropVert.value)
    #param_list.append ("FounColor = %s\n" % build_ele.FounColorVert.value)
    param_list.append ("FounColorVert = %s\n" % build_ele.FounColorVert.value)
    #param_list.append ("BarraLayer = %s\n" % build_ele.BarraLayerVert.value)
    param_list.append ("BarraLayerVert = %s\n" % build_ele.BarraLayerVert.value)
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
        Forats.append(build_ele.ForatsVertList.value[y])
    param_list.append ("ForatsPar = %s\n" % Forats)#matriu --------------------Forats-------------
    param_list.append ("Ample_forat_femella = %s\n" % build_ele.dadesTDVertTD.value[i].Ample_forat_femellaVert)
    param_list.append ("Altura_forat_femella = %s\n" % build_ele.dadesTDVertTD.value[i].Altura_forat_femellaVert)
    param_list.append ("Separacio_forat_femella = %s\n" %build_ele.dadesTDVertTD.value[i].Separacio_forat_femellaVert)

    Femelles = []
    for y in range(build_ele.nListFemellesVert.value[i].Posicio, build_ele.nListFemellesVert.value[i].Posicio + build_ele.nListFemellesVert.value[i].nTotal):
        Femelles.append(build_ele.FemellesVertListTD.value[y])

    listFemelles = Femelles+FemellesAux

    param_list.append ("Femelles = %s\n" % listFemelles)#matriu -------------FEMELLES--------------------
    param_list.append ("posicio_centre_masses = %s\n" % build_ele.dadesTDVertTD.value[i].posicio_centre_massesVert)
    param_list.append ("IsFirstCancam = %s\n" % build_ele.dadesTDVertTD.value[i].IsFirstCancamVert)
    param_list.append ("Dis1cancam = %s\n" % build_ele.dadesTDVertTD.value[i].Dis1cancamVert)
    param_list.append ("IsSecondCancam = %s\n" % build_ele.dadesTDVertTD.value[i].IsSecondCancamVert)
    param_list.append ("Dis2cancam = %s\n" % build_ele.dadesTDVertTD.value[i].Dis2cancamVert)
    param_list.append ("PestanyaSuperior = %s\n" % build_ele.dadesTDVertTD.value[i].PestanyaSuperiorVert)
    param_list.append ("PestanyaInferior = %s\n" % build_ele.dadesTDVertTD.value[i].PestanyaInferiorVert)
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
    set_valors_Vert_ini(build_ele, nVer, 10)

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
    build_ele.LengthListEncaixVert.value = build_ele.IntegerTDSelector.value *3
    if build_ele.nListEncaixVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListEncaixVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListEncaixVert.value):
            for posicions in range(len(build_ele.nListEncaixVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListEncaixVert.value[posicions-1].Posicio + build_ele.nListEncaixVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListEncaixVert.value.append(bob)
        else:
            posIni = len(build_ele.nListEncaixVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListEncaixVert.value)):
                build_ele.nListEncaixVert.value.pop()
    #*********FEMELLES**********
    build_ele.LengthListFemellesVert.value = build_ele.IntegerTDSelector.value *3
    if build_ele.nListFemellesVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListFemellesVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListFemellesVert.value):
            for posicions in range(len(build_ele.nListFemellesVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListFemellesVert.value[posicions-1].Posicio + build_ele.nListFemellesVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListFemellesVert.value.append(bob)
        else:
            posIni = len(build_ele.nListFemellesVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListFemellesVert.value)):
                build_ele.nListFemellesVert.value.pop()

    #*********Potes**********
    build_ele.LengthListPotesVert.value = build_ele.IntegerTDSelector.value *3
    if build_ele.nListPotesVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListPotesVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListPotesVert.value):
            for posicions in range(len(build_ele.nListPotesVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListPotesVert.value[posicions-1].Posicio + build_ele.nListPotesVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListPotesVert.value.append(bob)
        else:
            posIni = len(build_ele.nListPotesVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListPotesVert.value)):
                build_ele.nListPotesVert.value.pop()

    #*********Forats**********
    posAnt = 0
    for nposForat in range(0, len(build_ele.nListForatsVert.value)):
        build_ele.nListForatsVert.value[nposForat] = build_ele.nListForatsVert.value[nposForat]._replace(Posicio = posAnt)
        build_ele.nListForatsVert.value[nposForat] = build_ele.nListForatsVert.value[nposForat]._replace(nTotal = 10)
        posAnt += 10
    build_ele.LengthListForatsVert.value = build_ele.IntegerTDSelector.value *10
    if build_ele.nListForatsVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListForatsVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListForatsVert.value):
            for posicions in range(len(build_ele.nListForatsVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListForatsVert.value[posicions-1].Posicio + build_ele.nListForatsVert.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListForatsVert.value.append(bob)
        else:
            posIni = len(build_ele.nListForatsVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListForatsVert.value)):
                build_ele.nListForatsVert.value.pop()

    #*********Colis**********
    build_ele.LengthListColisVert.value = build_ele.IntegerTDSelector.value *3
    if build_ele.nListColisVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 3)
            posAnt += 3
            build_ele.nListColisVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListColisVert.value):
            for posicions in range(len(build_ele.nListColisVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListColisVert.value[posicions-1].Posicio + build_ele.nListColisVert.value[posicions-1].nTotal,
                                    nTotal = 3)
                build_ele.nListColisVert.value.append(bob)
        else:
            posIni = len(build_ele.nListColisVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListColisVert.value)):
                build_ele.nListColisVert.value.pop()

    #*********BarresHor**********
    build_ele.LengthListEncaixVert.value = build_ele.IntegerTDSelector.value *NombreBarresHorInt
    if build_ele.nListBarresHor.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = NombreBarresHorInt)
            posAnt += NombreBarresHorInt
            build_ele.nListBarresHor.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListBarresHor.value):
            for posicions in range(len(build_ele.nListBarresHor.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresHor.value[posicions-1].Posicio + build_ele.nListBarresHor.value[posicions-1].nTotal,
                                    nTotal = NombreBarresHorInt)
                build_ele.nListBarresHor.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresHor.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListBarresHor.value)):
                build_ele.nListBarresHor.value.pop()

    #*********BarresVert**********
    if build_ele.nListBarresVert.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = NombreBarresVertInt)
            posAnt += NombreBarresVertInt
            build_ele.nListBarresVert.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListBarresVert.value):
            for posicions in range(len(build_ele.nListBarresVert.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresVert.value[posicions-1].Posicio + build_ele.nListBarresVert.value[posicions-1].nTotal,
                                    nTotal = NombreBarresVertInt)
                build_ele.nListBarresVert.value.append(bob)
        else:
            posAnt = 0
            for posicions in range(0,build_ele.IntegerTDSelector.value):
                build_ele.nListBarresVert.value[posicions] = build_ele.nListBarresVert.value[posicions]._replace(Posicio = posAnt)
                build_ele.nListBarresVert.value[posicions] = build_ele.nListBarresVert.value[posicions]._replace(nTotal = NombreBarresVertInt)
                posAnt += NombreBarresVertInt


            posIni = len(build_ele.nListBarresVert.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListBarresVert.value)):
                build_ele.nListBarresVert.value.pop()
    #*********BarresFront**********
    if build_ele.nListBarresFront.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListBarresFront.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListBarresFront.value):
            for posicions in range(len(build_ele.nListBarresFront.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresFront.value[posicions-1].Posicio + build_ele.nListBarresFront.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListBarresFront.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresFront.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListBarresFront.value)):
                build_ele.nListBarresFront.value.pop()

    #*********BarresFrontAux**********

    #nTotat de 5 a 10


    if build_ele.nListBarresFrontAux.value == []:
        posAnt = 0
        for posicions in range(0,build_ele.IntegerTDSelector.value):
            TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
            bob = TDCollection( Posicio = posAnt,
                                nTotal = 10)
            posAnt += 10
            build_ele.nListBarresFrontAux.value.append(bob)
    else:
        if build_ele.IntegerTDSelector.value > len(build_ele.nListBarresFrontAux.value):
            for posicions in range(len(build_ele.nListBarresFrontAux.value),build_ele.IntegerTDSelector.value):
                TDCollection = collections.namedtuple('StirrupList', 'Posicio nTotal')
                bob = TDCollection( Posicio = build_ele.nListBarresFrontAux.value[posicions-1].Posicio + build_ele.nListBarresFrontAux.value[posicions-1].nTotal,
                                    nTotal = 10)
                build_ele.nListBarresFrontAux.value.append(bob)
        else:
            posIni = len(build_ele.nListBarresFrontAux.value)
            for posicions in range(build_ele.IntegerTDSelector.value, len(build_ele.nListBarresFrontAux.value)):
                build_ele.nListBarresFrontAux.value.pop()


    #DADES TDV UNIQUES
    i = build_ele.IntegerTDSelector.value
    TDCollectionDadesVert = collections.namedtuple('namedtuple', 'MostrarTDVertical BarraAmple BarraAltura LlargadaAut BarraAlcada BarraSuperior BarraInferior Gruix '+
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert '+
                                                   'esProvisional esExtrem '+
                                                   'MostrarRecess MostrarCavitat '+
                                                   'linia layer vermell ' +
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical= True,
                                           BarraAmple = build_ele.BarraAmpleVert.value,
                                            BarraAltura = build_ele.BarraAlturaVert.value,
                                            LlargadaAut = build_ele.llargadaAutomatica.value,
                                            BarraAlcada = build_ele.BarraLlargadaIndiv.value,
                                            BarraSuperior = build_ele.SelectorTDHorSup.value,
                                            BarraInferior = build_ele.SelectorTDHorInf.value,
                                            Gruix = build_ele.BarraGruixVert.value,
                                            EncaixSup = build_ele.encaixSup.value,
                                            EncaixInf = build_ele.encaixInf.value,
                                            FemellaSup = build_ele.femellaSup.value,
                                            FemellaInf = build_ele.femellaInf.value,
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
                                            esProvisional = build_ele.esProvisional.value,
                                            esExtrem = build_ele.esExtrem.value,
                                            MostrarRecess = build_ele.MostrarRecessVert.value,
                                            MostrarCavitat = build_ele.MostrarCavitatVert.value,
                                            linia = build_ele.SelectorLiniaVert.value,
                                            layer = build_ele.SelectorLayerVert.value,
                                            vermell = build_ele.esVermellVert.value,
                                            FounColor = build_ele.FounColorVert.value
                                            )
    while len(build_ele.dadesTDVertTD.value) <= i:
        build_ele.dadesTDVertTD.value.append(bobDadesGlobal)
    else:
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarTDVertical = build_ele.MostrarTDVertical.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAmple = build_ele.BarraAmpleVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAltura = build_ele.BarraAlturaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(LlargadaAut = build_ele.llargadaAutomatica.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAlcada = build_ele.BarraLlargadaIndiv.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraSuperior = build_ele.SelectorTDHorSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraInferior = build_ele.SelectorTDHorInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Gruix = build_ele.BarraGruixVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixInf = build_ele.encaixInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixSup = build_ele.encaixSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaInf = build_ele.femellaInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaSup = build_ele.femellaSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Ample_forat_femellaVert = build_ele.Ample_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Altura_forat_femellaVert = build_ele.Altura_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Separacio_forat_femellaVert = build_ele.Separacio_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(posicio_centre_massesVert = build_ele.posicio_centre_massesVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsFirstCancamVert = build_ele.IsFirstCancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis1cancamVert = build_ele.Dis1cancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsSecondCancamVert = build_ele.IsSecondCancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis2cancamVert = build_ele.Dis2cancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaSuperiorVert = build_ele.PestanyaSuperiorVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaInferiorVert = build_ele.PestanyaInferiorVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esProvisional = build_ele.esProvisional.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esExtrem = build_ele.esExtrem.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarRecess = build_ele.MostrarRecessVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarCavitat = build_ele.MostrarCavitatVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(linia = build_ele.SelectorLiniaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(layer = build_ele.SelectorLayerVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(vermell = build_ele.esVermellVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FounColor = build_ele.FounColorVert.value)

    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                     desplXAbs = build_ele.desplXVertAbs.value,
                                    desplY =build_ele.desplYVert.value,
                                    desplYAbs = build_ele.desplYVertAbs.value,
                                    mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                    desplLinA =build_ele.desplVertLinA.value,
                                    mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                    desplLinB =build_ele.desplVertLinB.value)
    while len(build_ele.listDesplVerticalsTD.value) <= i:
        build_ele.listDesplVerticalsTD.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplX = build_ele.desplXVert.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplY = build_ele.desplYVert.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplXAbs = build_ele.desplXVertAbs.value )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplYAbs = build_ele.desplYVertAbs.value )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinA = build_ele.desplVertLinA.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinB = build_ele.desplVertLinB.value)


def guardar_valors_actuals(build_ele, i):
    '''
    Guardar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''
    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                     desplXAbs = build_ele.desplXVertAbs.value,
                                    desplY =build_ele.desplYVert.value,
                                    desplYAbs = build_ele.desplYVertAbs.value,
                                    mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                    desplLinA =build_ele.desplVertLinA.value,
                                    mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                    desplLinB =build_ele.desplVertLinB.value)
    while len(build_ele.listDesplVerticalsTD.value) <= i:
        build_ele.listDesplVerticalsTD.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplX = build_ele.desplXVert.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplY = build_ele.desplYVert.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplXAbs = build_ele.desplXVertAbs.value )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplYAbs = build_ele.desplYVertAbs.value )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinA = build_ele.desplVertLinA.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinB = build_ele.desplVertLinB.value)

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
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert '+
                                                   'esProvisional esExtrem '+
                                                   'MostrarRecess MostrarCavitat '+
                                                   "linia layer vermell "+
                                                   'FounColor')

    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical= build_ele.MostrarTDVertical.value,
                                           BarraAmple = build_ele.BarraAmpleVert.value,
                                            BarraAltura = build_ele.BarraAlturaVert.value,
                                            LlargadaAut = build_ele.llargadaAutomatica.value,
                                            BarraAlcada = build_ele.BarraLlargadaIndiv.value,
                                            BarraSuperior = build_ele.SelectorTDHorSup.value,
                                            BarraInferior = build_ele.SelectorTDHorInf.value,
                                            Gruix = build_ele.BarraGruixVert.value,
                                            EncaixSup = build_ele.encaixSup.value,
                                            EncaixInf = build_ele.encaixInf.value,
                                            FemellaSup = build_ele.femellaSup.value,
                                            FemellaInf = build_ele.femellaInf.value,
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
                                            esProvisional = build_ele.esProvisional.value,
                                            esExtrem = build_ele.esExtrem.value,
                                            MostrarRecess = build_ele.MostrarRecessVert.value,
                                            MostrarCavitat = build_ele.MostrarCavitatVert.value,
                                            linia = build_ele.SelectorLiniaVert.value,
                                            layer = build_ele.SelectorLayerVert.value,
                                            vermell = build_ele.esVermellVert.value,
                                            FounColor = build_ele.FounColorVert.value
                                            )
    if len(build_ele.dadesTDVertTD.value) <= i:
        build_ele.dadesTDVertTD.value.append(bobDadesGlobal)
    else:
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarTDVertical = build_ele.MostrarTDVertical.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAmple = build_ele.BarraAmpleVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAltura = build_ele.BarraAlturaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(LlargadaAut = build_ele.llargadaAutomatica.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAlcada = build_ele.BarraLlargadaIndiv.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraSuperior = build_ele.SelectorTDHorSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraInferior = build_ele.SelectorTDHorInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Gruix = build_ele.BarraGruixVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixInf = build_ele.encaixInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixSup = build_ele.encaixSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaInf = build_ele.femellaInf.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaSup = build_ele.femellaSup.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Ample_forat_femellaVert = build_ele.Ample_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Altura_forat_femellaVert = build_ele.Altura_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Separacio_forat_femellaVert = build_ele.Separacio_forat_femellaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(posicio_centre_massesVert = build_ele.posicio_centre_massesVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsFirstCancamVert = build_ele.IsFirstCancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis1cancamVert = build_ele.Dis1cancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsSecondCancamVert = build_ele.IsSecondCancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis2cancamVert = build_ele.Dis2cancamVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaSuperiorVert = build_ele.PestanyaSuperiorVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaInferiorVert = build_ele.PestanyaInferiorVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esProvisional = build_ele.esProvisional.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esExtrem = build_ele.esExtrem.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarRecess = build_ele.MostrarRecessVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarCavitat = build_ele.MostrarCavitatVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(linia = build_ele.SelectorLiniaVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(layer = build_ele.SelectorLayerVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(vermell = build_ele.esVermellVert.value)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FounColor = build_ele.FounColorVert.value)


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
        if x >= len(build_ele.FemellesVertListTD.value):
            set_values_femelles(build_ele, x)
        if build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(Femella = build_ele.FemellesVertListToShow.value[y].Femella)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(FemellaOr = build_ele.FemellesVertListToShow.value[y].FemellaOr)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaX = build_ele.FemellesVertListToShow.value[y].PosFemellaX)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaY = build_ele.FemellesVertListToShow.value[y].PosFemellaY)
            try:
                build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaXOri = build_ele.FemellesVertListToShow.value[y].PosFemellaXOri)
            except Exception as e:
                build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaXOri = 0)
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
        if x >= len(build_ele.ForatsVertList.value):
            set_values_forats(build_ele, x)
        if build_ele.ForatsVertListToShow.value != [] and len(build_ele.ForatsVertListToShow.value) > y:
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(Forat = build_ele.ForatsVertListToShow.value[y].Forat)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(orientacio = build_ele.ForatsVertListToShow.value[y].orientacio)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(Posicio = build_ele.ForatsVertListToShow.value[y].Posicio)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(Llargada = build_ele.ForatsVertListToShow.value[y].Llargada)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(Amplada = build_ele.ForatsVertListToShow.value[y].Amplada)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(Complet = build_ele.ForatsVertListToShow.value[y].Complet)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(LlargadaB = build_ele.ForatsVertListToShow.value[y].LlargadaB)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(AmpladaB = build_ele.ForatsVertListToShow.value[y].AmpladaB)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(MostrarBox = build_ele.ForatsVertListToShow.value[y].MostrarBox)
            build_ele.ForatsVertList.value[x] = build_ele.ForatsVertList.value[x]._replace(ProfunditatTFF = build_ele.ForatsVertListToShow.value[y].ProfunditatTFF)
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
        if x >= len(build_ele.BarresHorList.value):
            set_values_barresHor(build_ele, x)
        if build_ele.BarresHorListToShowTD.value != [] and len(build_ele.BarresHorListToShowTD.value) > y:
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(BarraHor = build_ele.BarresHorListToShowTD.value[y].BarraHor)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(Orientacio = build_ele.BarresHorListToShowTD.value[y].Orientacio)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(Posicio = build_ele.BarresHorListToShowTD.value[y].Posicio)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(AutoLongitud = build_ele.BarresHorListToShowTD.value[y].AutoLongitud)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(Longitud = build_ele.BarresHorListToShowTD.value[y].Longitud)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(Edit = build_ele.BarresHorListToShowTD.value[y].Edit)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(acabatEditar = build_ele.BarresHorListToShowTD.value[y].acabatEditar)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(BarraInici = build_ele.BarresHorListToShowTD.value[y].BarraInici)
            build_ele.BarresHorList.value[x] = build_ele.BarresHorList.value[x]._replace(BarraFinal = build_ele.BarresHorListToShowTD.value[y].BarraFinal)
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
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaSup = build_ele.BarresVertListToShow.value[y].FemellaSup)
            build_ele.BarresVertList.value[x] = build_ele.BarresVertList.value[x]._replace(FemellaInf = build_ele.BarresVertListToShow.value[y].FemellaInf)
        y += 1

    #***************BarresFront******************

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



def mostrar_valors_actuals(build_ele, i):
    '''
    mostrar valors del TD actualment seleccionat
    get: i -> Posicio

    return: -

    '''
    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = build_ele.desplXVert.value,
                                    desplXAbs = build_ele.desplXVertAbs.value,
                                    desplY = build_ele.desplYVert.value,
                                    desplYAbs = build_ele.desplYVertAbs.value,
                                    mostrarLiniaVertA =build_ele.mostrarLiniaVertA.value,
                                    desplLinA =build_ele.desplVertLinA.value,
                                    mostrarLiniaVertB =build_ele.mostrarLiniaVertB.value,
                                    desplLinB =build_ele.desplVertLinB.value)
    while len(build_ele.listDesplVerticalsTD.value) <= i:
        build_ele.listDesplVerticalsTD.value.append(bobDespl)
    else:
        build_ele.desplXVert.value = build_ele.listDesplVerticalsTD.value[i].desplX
        build_ele.desplYVert.value = build_ele.listDesplVerticalsTD.value[i].desplY
        build_ele.desplXVertAbs.value = build_ele.listDesplVerticalsTD.value[i].desplXAbs
        build_ele.desplYVertAbs.value = build_ele.listDesplVerticalsTD.value[i].desplYAbs
        build_ele.mostrarLiniaVertA.value = build_ele.listDesplVerticalsTD.value[i].mostrarLiniaVertA
        build_ele.desplVertLinA.value = build_ele.listDesplVerticalsTD.value[i].desplLinA
        build_ele.mostrarLiniaVertB.value = build_ele.listDesplVerticalsTD.value[i].mostrarLiniaVertB
        build_ele.desplVertLinB.value = build_ele.listDesplVerticalsTD.value[i].desplLinB

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
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert '+
                                                   'esProvisional esExtrem '+
                                                   'MostrarRecess MostrarCavitat '+
                                                   'linia layer vermell '+
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical = build_ele.MostrarTDVertical.value,
                                            BarraAmple = build_ele.BarraAmpleVert.value,
                                            BarraAltura = build_ele.BarraAlturaVert.value,
                                            LlargadaAut = build_ele.llargadaAutomatica.value,
                                            BarraAlcada = build_ele.BarraLlargadaIndiv.value,
                                            BarraSuperior = "TD Superior",#build_ele.SelectorTDHorSup.value,
                                            BarraInferior = "TD Inferior",#build_ele.SelectorTDHorInf.value,
                                            Gruix = build_ele.BarraGruixVert.value,
                                            EncaixSup = build_ele.encaixSup.value,
                                            EncaixInf = build_ele.encaixInf.value,
                                            FemellaSup = build_ele.femellaSup.value,
                                            FemellaInf = build_ele.femellaInf.value,
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
                                            esProvisional = build_ele.esProvisional.value,
                                            esExtrem = build_ele.esExtrem.value,
                                            MostrarRecess = build_ele.MostrarRecessVert.value,
                                            MostrarCavitat = build_ele.MostrarCavitatVert.value,
                                            linia = build_ele.SelectorLiniaVert.value,
                                            layer = build_ele.SelectorLayerVert.value,
                                            vermell = build_ele.esVermellVert.value,
                                            FounColor = build_ele.FounColorVert.value)

    if len(build_ele.dadesTDVertTD.value) <= i:
        build_ele.dadesTDVertTD.value.append(bobDadesGlobal)
    else:
        build_ele.MostrarTDVertical.value = build_ele.dadesTDVertTD.value[i].MostrarTDVertical
        build_ele.BarraAmpleVert.value = build_ele.dadesTDVertTD.value[i].BarraAmple
        build_ele.BarraAlturaVert.value = build_ele.dadesTDVertTD.value[i].BarraAltura
        build_ele.llargadaAutomatica.value = build_ele.dadesTDVertTD.value[i].LlargadaAut
        build_ele.BarraLlargadaIndiv.value = build_ele.dadesTDVertTD.value[i].BarraAlcada
        build_ele.SelectorTDHorSup.value = build_ele.dadesTDVertTD.value[i].BarraSuperior
        build_ele.SelectorTDHorInf.value = build_ele.dadesTDVertTD.value[i].BarraInferior
        build_ele.BarraGruixVert.value = build_ele.dadesTDVertTD.value[i].Gruix
        build_ele.encaixSup.value = build_ele.dadesTDVertTD.value[i].EncaixSup
        build_ele.encaixInf.value = build_ele.dadesTDVertTD.value[i].EncaixInf
        build_ele.femellaSup.value = build_ele.dadesTDVertTD.value[i].FemellaSup
        build_ele.femellaInf.value = build_ele.dadesTDVertTD.value[i].FemellaInf
        build_ele.Ample_forat_femellaVert.value = build_ele.dadesTDVertTD.value[i].Ample_forat_femellaVert
        build_ele.Separacio_forat_femellaVert.value = build_ele.dadesTDVertTD.value[i].Separacio_forat_femellaVert
        build_ele.posicio_centre_massesVert.value = build_ele.dadesTDVertTD.value[i].posicio_centre_massesVert
        build_ele.IsFirstCancamVert.value = build_ele.dadesTDVertTD.value[i].IsFirstCancamVert
        build_ele.Dis1cancamVert.value = build_ele.dadesTDVertTD.value[i].Dis1cancamVert
        build_ele.IsSecondCancamVert.value = build_ele.dadesTDVertTD.value[i].IsSecondCancamVert
        build_ele.Dis2cancamVert.value = build_ele.dadesTDVertTD.value[i].Dis2cancamVert
        build_ele.PestanyaSuperiorVert.value = build_ele.dadesTDVertTD.value[i].PestanyaSuperiorVert
        build_ele.PestanyaInferiorVert.value = build_ele.dadesTDVertTD.value[i].PestanyaInferiorVert
        build_ele.esProvisional.value = build_ele.dadesTDVertTD.value[i].esProvisional
        build_ele.esExtrem.value = build_ele.dadesTDVertTD.value[i].esExtrem
        build_ele.MostrarRecessVert.value = build_ele.dadesTDVertTD.value[i].MostrarRecess
        build_ele.MostrarCavitatVert.value = build_ele.dadesTDVertTD.value[i].MostrarCavitat
        build_ele.SelectorLiniaVert.value = build_ele.dadesTDVertTD.value[i].linia
        build_ele.SelectorLayerVert.value = build_ele.dadesTDVertTD.value[i].layer
        build_ele.esVermellVert.value = build_ele.dadesTDVertTD.value[i].vermell
        build_ele.FounColorVert.value = build_ele.dadesTDVertTD.value[i].FounColor



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
            TDCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya ')
            bob = TDCollection( Encaix = False,
                                EncaixOr = "Esq",
                                Longitud = 31.,
                                Amplitud = 30,
                                Posicio = 0.,
                                Profunditat = 11.0,
                                Pestanya = False)

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
        if len(build_ele.FemellesVertListTD.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri ')
            bob = TDCollection( Femella = False,
                                FemellaOr = "Esq",
                                PosFemellaX = 400.,
                                PosFemellaY = 0.,
                                Separacio_forat_femella = 50,
                                PosFemellaXOri  = 0)


            build_ele.FemellesVertListToShow.value.append(bob)
        else:
            build_ele.FemellesVertListToShow.value.append(build_ele.FemellesVertListTD.value[x])

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
            TDCollection = collections.namedtuple('StirrupList', 'Pota Posicio ')
            bob = TDCollection( Pota = False,
                                Posicio = 400.)

            build_ele.PotesVertListToShow.value.append(bob)
        else:
            build_ele.PotesVertListToShow.value.append(build_ele.PotesVertList.value[x])

    #**********Forats*************
    build_ele.ForatsVertListToShow.value = []
    if i < len(build_ele.nListForatsVert.value):
        inici = build_ele.nListForatsVert.value[i].Posicio
        final = build_ele.nListForatsVert.value[i].nTotal
    else:
        inici = 0
        final = 0
    for x in range(inici, inici+final):
        if len(build_ele.ForatsVertList.value) <= x:
            TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox ProfunditatTFF ')
            bob = TDCollection( Forat = False,
                                orientacio = "Inf",
                                Posicio = 400,
                                Llargada = 10,
                                Amplada = 10,
                                Complet = False,
                                LlargadaB = 50,
                                AmpladaB = 20,
                                MostrarBox = True,
                                ProfunditatTFF = 15)

            build_ele.ForatsVertListToShow.value.append(bob)
        else:
            build_ele.ForatsVertListToShow.value.append(build_ele.ForatsVertList.value[x])

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
            TDCollection = collections.namedtuple('StirrupList', 'Colis orientacio Posicio Llargada Amplada ')
            bob = TDCollection( Colis = False,
                                orientacio = 'Sup',
                                Posicio = 400.,
                                Llargada = 170,
                                Amplada = 12)

            build_ele.ColisVertListToShow.value.append(bob)
        else:
            build_ele.ColisVertListToShow.value.append(build_ele.ColisVertList.value[x])

     #**********BarresHor*************
    '''
    build_ele.BarresHorListToShowTD.value = []
    if i < len(build_ele.nListBarresHor.value):
        inici = build_ele.nListBarresHor.value[i].Posicio
        final = build_ele.nListBarresHor.value[i].nTotal
    else:
        inici = 0
        final = 0
    pos = 0
    for x in range(inici, inici+final):
        pos += 400
        if len(build_ele.BarresHorList.value) <= x:
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

            build_ele.BarresHorListToShowTD.value.append(bob)
        else:
            build_ele.BarresHorListToShowTD.value.append(build_ele.BarresHorList.value[x])
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
            TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf ')
            bob = TDCollection( BarraVert = False,
                                Posicio = 400.,
                                PosicioAbs = 0,
                                PosicioZ = 0,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici = 'Inferior',
                                EditFront = False,
                                Edit = False,
                                EncaixInf = False,
                                EncaixSup = False,
                                PestanyaSup = True,
                                PestanyaInf = True,
                                acabatEditar = False,
                                editiantFrontals = False,
                                FemellaSup = True,
                                FemellaInf = True)

            build_ele.BarresVertListToShow.value.append(bob)
        else:
            build_ele.BarresVertListToShow.value.append(build_ele.BarresVertList.value[x])

    #**********BarresFront*************
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
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
            bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False)

            build_ele.BarresFrontListToShow.value.append(bob)
        else:
            build_ele.BarresFrontListToShow.value.append(build_ele.BarresFrontList.value[x])
    test = "testSTOP"

def set_values(build_ele, i):
    '''
    Guardar valors del TD actualment seleccionat (no llistes)
    get: i -> Posicio

    return: -

    '''

    #DesplaçamentsVerticals
    TDCollectionDesplVert = collections.namedtuple('namedtuple', 'desplX desplXAbs desplY desplYAbs mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB')
    bobDespl = TDCollectionDesplVert(desplX = 0,
                                     desplXAbs = 0,
                                    desplY = 0,
                                    desplYAbs = 0,
                                    mostrarLiniaVertA = True,
                                    desplLinA =0,
                                    mostrarLiniaVertB = False,
                                    desplLinB =0)
    while len(build_ele.listDesplVerticalsTD.value) <= i:
        build_ele.listDesplVerticalsTD.value.append(bobDespl)
    else:
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplX = 0)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplY = 0)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplXAbs = 0 )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplYAbs = 0 )
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertA = True)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinA = 0)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(mostrarLiniaVertA = False)
        build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplLinB = 0)

    lennVer = len(build_ele.SelectorTDV.value)
    nVerS = build_ele.SelectorTDV.value[lennVer-1:]


    #if i == nVer:
    #    build_ele.listDesplVerticalsTD.value[i] = build_ele.listDesplVerticalsTD.value[i]._replace(desplXAbs = build_ele.BarraLlargadaTD.value - build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2)


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
                                                   'EncaixSup EncaixInf FemellaSup FemellaInf '+
                                                   'Ample_forat_femellaVert Altura_forat_femellaVert Separacio_forat_femellaVert '+
                                                   'posicio_centre_massesVert IsFirstCancamVert Dis1cancamVert IsSecondCancamVert Dis2cancamVert '+
                                                   'PestanyaSuperiorVert PestanyaInferiorVert '+
                                                   'esProvisional esExtrem '+
                                                   'MostrarRecess MostrarCavitat '+
                                                   'linia layer vermell '+
                                                   'FounColor')
    bobDadesGlobal = TDCollectionDadesVert(MostrarTDVertical = True,
                                            BarraAmple = 30,
                                            BarraAltura = 60,
                                            LlargadaAut = True,
                                            BarraAlcada = 2600,
                                            BarraSuperior = "TD Superior",
                                            BarraInferior = "TD Inferior",
                                            Gruix = 1.5,
                                            EncaixSup = False,
                                            EncaixInf = False,
                                            FemellaSup = True,
                                            FemellaInf = True,
                                            Ample_forat_femellaVert = 15,
                                            Altura_forat_femellaVert = 3.75,
                                            Separacio_forat_femellaVert = 50,
                                            posicio_centre_massesVert= 500.00,
                                            IsFirstCancamVert= False,
                                            Dis1cancamVert= 500,
                                            IsSecondCancamVert= False,
                                            Dis2cancamVert = 1000,
                                            PestanyaSuperiorVert = True,
                                            PestanyaInferiorVert = True,
                                            esProvisional = False,
                                            esExtrem = False,
                                            MostrarRecess = True,
                                            MostrarCavitat = True,
                                            linia = 1,
                                            layer = "TD_ESTRUCTURA",
                                            vermell = False,
                                            FounColor = 23)
    while len(build_ele.dadesTDVertTD.value) <= i:
        build_ele.dadesTDVertTD.value.append(bobDadesGlobal)
    else:
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarTDVertical = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAmple = 30)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAltura = 30)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraAlcada = 2600)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(LlargadaAut = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraSuperior = "TD Superior")
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(BarraInferior = "TD Inferior")
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Gruix = 1.5)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixSup = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(EncaixInf = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Ample_forat_femellaVert = 15)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Altura_forat_femellaVert = 3.75)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Separacio_forat_femellaVert = 30)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(posicio_centre_massesVert = 500.00)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsFirstCancamVert = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis1cancamVert = 500)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(IsSecondCancamVert = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(Dis2cancamVert = 1000)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaSuperiorVert = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(PestanyaInferiorVert = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaSup = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FemellaInf = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esProvisional = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(esExtrem = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarRecess = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(MostrarCavitat = True)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(linia = 1)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(layer = "TD_ESTRUCTURA")
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(vermell = False)
        build_ele.dadesTDVertTD.value[i] = build_ele.dadesTDVertTD.value[i]._replace(FounColor = 1)

def set_values_BarresVertListToShow(build_ele, i):
    if len(build_ele.BarresVertListToShow.value) <= i:
        TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf  linia layer vermell')
        bob = TDCollection( BarraVert = False,
                            Posicio = 400.,
                            PosicioAbs = 0,
                            PosicioZ = 0,
                            AutoLongitud = True,
                            Longitud = 100,
                            BarraInici = 'Inferior',
                            EditFront = False,
                            Edit = False,
                            EncaixInf = False,
                            EncaixSup = False,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            acabatEditar = False,
                            editiantFrontals = False,
                            FemellaSup = True,
                            FemellaInf = True,
                            linia = 1,
                            layer = "TD_ESTRUCTURA",
                            vermell = False)

        build_ele.BarresVertListToShow.value.append(bob)


def set_values_barresRef(build_ele, i):
    '''
    Guardar valors de les Barres Reforç del EN actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    pos = 0
    cont = 0
    if len(build_ele.BarresRefListTD.value) <= i:
        for x in range(len(build_ele.BarresRefListTD.value), i+1):
            if cont == 3:
                pos = 0
                cont= 0
            cont += 1
            pos += 400
            ENCollection = collections.namedtuple('StirrupList', 'BarraRef Orientacio Posicio BarraIni BarraFin AutoLongitud Longitud Edit acabatEditar ')
            bob = ENCollection( BarraRef = False,
                                Orientacio = 'Sup',
                                acabatEditar = False,
                                Posicio = pos,
                                BarraIni = 'Tub 0',
                                BarraFin = 'Tub 1',
                                AutoLongitud = True,
                                Longitud = 100,
                                Edit = False)

            build_ele.BarresRefListTD.value.append(bob)

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

        build_ele.BarresRefListTD.value.append(bob)
    '''

def set_values_encaix(build_ele, i):
    '''
    Guardar valors del encaix del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.EncaixVertList.value) <= i:
        for x in range(len(build_ele.EncaixVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya ')
            bob = TDCollection( Encaix = False,
                                EncaixOr = "Esq",
                                Longitud = 31.,
                                Amplitud = 30,
                                Posicio = 0.,
                                Profunditat = 11.0,
                                Pestanya = False)

            build_ele.EncaixVertList.value.append(bob)

def set_values_femelles(build_ele, i):
    '''
    Guardar valors de les femelles del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.FemellesVertListTD.value) <= i:
        for x in range(len(build_ele.FemellesVertListTD.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri ')
            bob = TDCollection( Femella = False,
                                FemellaOr = "Esq",
                                PosFemellaX = 400.,
                                PosFemellaY = 0.,
                                Separacio_forat_femella = 0,
                                PosFemellaXOri = 0)

            build_ele.FemellesVertListTD.value.append(bob)

def set_values_potes(build_ele, i):
    '''
    Guardar valors de les potes del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.PotesVertList.value) <= i:
        for x in range(len(build_ele.PotesVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Pota Posicio ')
            bob = TDCollection( Pota = False,
                                Posicio = 400.)

            build_ele.PotesVertList.value.append(bob)

def set_values_forats(build_ele, i):
    '''
    Guardar valors de les Forats del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.ForatsVertList.value) <= i:
        for x in range(len(build_ele.ForatsVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox ProfunditatTFF ')
            bob = TDCollection( Forat = False,
                                orientacio = "Inf",
                                Posicio = 400,
                                Llargada = 10,
                                Amplada = 10,
                                Complet = False,
                                LlargadaB = 50,
                                AmpladaB = 20,
                                MostrarBox = True,
                                ProfunditatTFF = 15)

            build_ele.ForatsVertList.value.append(bob)

def set_values_colis(build_ele, i):
    '''
    Guardar valors dels Colis del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    if len(build_ele.ColisVertList.value) <= i:
        for x in range(len(build_ele.ColisVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'Colis orientacio Posicio Llargada Amplada ')
            bob = TDCollection( Colis = False,
                                orientacio = 'Sup',
                                Posicio = 400.,
                                Llargada = 170,
                                Amplada = 12)

            build_ele.ColisVertList.value.append(bob)

def set_values_barresHor(build_ele, i):
    '''
    Guardar valors de les Barres Horitzontals del TD actualment seleccionat o inicia valors si ni existeixen
    get: i -> Posicio

    return: -

    '''
    pos = 0
    cont = 0
    if len(build_ele.BarresHorList.value) <= i:
        for x in range(len(build_ele.BarresHorList.value), i+1):
            if cont == NombreBarresHorInt:
                pos = 0
                cont= 0
            cont += 1
            pos += 400
            TDCollection = collections.namedtuple('StirrupList', 'BarraHor Orientacio Posicio AutoLongitud Longitud BarraInici BarraFinal Edit acabatEditar MostrarRecess MostrarCavitat Xapa ProfunditatXapa Layer ')
            bob = TDCollection( BarraHor = False,
                                Orientacio = 'Sup',
                                acabatEditar = False,
                                Posicio = pos,
                                AutoLongitud = True,
                                Longitud = 100,
                                BarraInici = "Tub 0",
                                BarraFinal = "Tub "+str(i+1),
                                Edit = False,
                                MostrarRecess = True,
                                MostrarCavitat = True,
                                Xapa = False,
                                ProfunditatXapa = 5,
                                Layer = "TD_ESTRUCTURA")

            build_ele.BarresHorList.value.append(bob)

    inici = len(build_ele.nListBarresHor.value)
    final = build_ele.nListBarresHor.value[len(build_ele.nListBarresHor.value)-1].Posicio + build_ele.nListBarresHor.value[len(build_ele.nListBarresHor.value)-1].nTotal

    pos = 0
    for aux in range(inici, final):
        pos += 400
        TDCollection = collections.namedtuple('StirrupList', 'BarraHor Orientacio Posicio AutoLongitud Longitud BarraInici BarraFinal Edit acabatEditar MostrarRecess MostrarCavitat Xapa ProfunditatXapa Layer ')
        bob = TDCollection( BarraHor = False,
                            Orientacio = 'Sup',
                            acabatEditar = False,
                            Posicio = pos,
                            AutoLongitud = True,
                            Longitud = 100,
                            BarraInici = 'Tub 0',
                            BarraFinal = "Tub "+str(i+1),
                            Edit = False,
                            MostrarRecess = True,
                            MostrarCavitat = True,
                            Xapa = False,
                            ProfunditatXapa = 5,
                            Layer = "TD_ESTRUCTURA")

        build_ele.BarresHorList.value.append(bob)

def set_values_BarresVert(build_ele, i):

    if len(build_ele.BarresVertList.value) <= i:
        for x in range(len(build_ele.BarresVertList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf ')
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
                                EncaixInf = False,
                                EncaixSup = False,
                                PestanyaSup = True,
                                PestanyaInf = True,
                                editiantFrontals = False,
                                FemellaSup = True,
                                FemellaInf = True)

            build_ele.BarresVertList.value.append(bob)

    inici = len(build_ele.nListBarresVert.value)
    final = build_ele.nListBarresVert.value[len(build_ele.nListBarresVert.value)-1].Posicio + build_ele.nListBarresVert.value[len(build_ele.nListBarresVert.value)-1].nTotal
    for aux in range(inici, final):
        TDCollection = collections.namedtuple('StirrupList', 'BarraVert Posicio PosicioAbs PosicioZ AutoLongitud Longitud BarraInici EditFront Edit EncaixInf EncaixSup acabatEditar editiantFrontals PestanyaSup PestanyaInf FemellaSup FemellaInf ')
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
                            EncaixInf = False,
                            EncaixSup = False,
                            editiantFrontals = False,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            FemellaSup = True,
                            FemellaInf = True)

        build_ele.BarresVertList.value.append(bob)

def set_values_BarresFront(build_ele, i):

    if len(build_ele.BarresFrontList.value) <= i:
        for x in range(len(build_ele.BarresFrontList.value), i+1):
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
            bob = TDCollection( BarraFront = False,
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

    inici = len(build_ele.nListBarresFront.value)
    final = build_ele.nListBarresFront.value[len(build_ele.nListBarresFront.value)-1].Posicio + build_ele.nListBarresFront.value[len(build_ele.nListBarresFront.value)-1].nTotal
    for aux in range(inici, final):
        TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
        bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Sup',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False)


        build_ele.BarresFrontList.value.append(bob)

def remove_values(build_ele, i):
    '''
    elimina valors en cas de que s'hagi reduit la llargada per no acommular valors innecessaris
    get: i -> Posicio

    return: -

    '''
    for x in range(i*NombreBarresVertInt, len(build_ele.listDesplVerticalsTD.value)):
        build_ele.listDesplVerticalsTD.value.pop()

    for x in range(i*2, len(build_ele.listDesplVerticalsInteriors.value)):
        build_ele.listDesplVerticalsInteriors.value.pop()

    for x in range(i*18, len(build_ele.dadesTDVertTD.value)):
        build_ele.dadesTDVertTD.value.pop()

    for x in range(i*3, len(build_ele.EncaixVertList.value)):
        build_ele.EncaixVertList.value.pop()

    for x in range(i*3, len(build_ele.FemellesVertListTD.value)):
        build_ele.FemellesVertListTD.value.pop()

    for x in range(i*3, len(build_ele.PotesVertList.value)):
        build_ele.PotesVertList.value.pop()

    for x in range(i*13, len(build_ele.ForatsVertList.value)):
        build_ele.ForatsVertList.value.pop()

    for x in range(i*5, len(build_ele.ColisVertList.value)):
        build_ele.ColisVertList.value.pop()

    for x in range(i*NombreBarresHorInt, len(build_ele.BarresHorList.value)):
        build_ele.BarresHorList.value.pop()


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

    listAnt = build_ele.FemellesVertListTD.value
    y = 0
    for x in range(inici, final):
        if x >= len(build_ele.FemellesVertListTD.value):
            build_ele.FemellesVertListTD.value.append(FemellesAux[y])
        elif build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(Femella = FemellesAux[y].Femella)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(FemellaOr = FemellesAux[y].FemellaOr)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaX = FemellesAux[y].PosFemellaX)
        y += 1

    y = build_ele.nListFemellesVert.value[i].nTotal + build_ele.nListFemellesVert.value[i].Posicio
    for x in range(final, len(build_ele.FemellesVertListTD.value)+len(FemellesAux)):
        if x >= len(build_ele.FemellesVertListTD.value):
            build_ele.FemellesVertListTD.value.append(listAnt[y])
        elif build_ele.FemellesVertListToShow.value != [] and len(build_ele.FemellesVertListToShow.value) > y:
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(Femella = listAnt[y].Femella)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(FemellaOr = listAnt[y].FemellaOr)
            build_ele.FemellesVertListTD.value[x] = build_ele.FemellesVertListTD.value[x]._replace(PosFemellaX = listAnt[y].PosFemellaX)
        y += 1

    build_ele.nListFemellesVert.value[i] = build_ele.nListFemellesVert.value[i]._replace(nTotal = build_ele.nListFemellesVert.value[i].nTotal + len(FemellesAux))
    if i+1 < len(build_ele.nListFemellesVert.value):
        build_ele.nListFemellesVert.value[i+1] = build_ele.nListFemellesVert.value[i+1]._replace(Posicio = build_ele.nListFemellesVert.value[i+1].Posicio + len(FemellesAux))
    for x  in range(build_ele.nListFemellesVert.value[i+1], len(build_ele.nListFemellesVert.value)):
        build_ele.nListFemellesVert.value[x] = build_ele.nListFemellesVert.value[x]._replace(Posicio = build_ele.nListFemellesVert.value[x].Posicio + build_ele.nListFemellesVert.value[x-1].nTotal)
'''

#mostrar valors
def mostrar_valors_hor(build_ele, nBarraVert, nHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorList.value[nHor].Edit)

    build_ele.desplXVert.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplX
    build_ele.desplYVert.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplY

    build_ele.desplXHorAbs.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplX
    build_ele.desplYHorAbs.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplY



    build_ele.mostrarLiniaVertA.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].mostrarLiniaVertA
    build_ele.desplVertLinA.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplLinA
    build_ele.mostrarLiniaVertB.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].mostrarLiniaVertB
    build_ele.desplVertLinB.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].desplLinB

    build_ele.SelectorLiniaHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].linia
    build_ele.SelectorLayerHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].layer


    build_ele.BarraAmpleHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].Ample
    build_ele.BarraAlturaHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].Altura
    #build_ele.BarraLlargadaVert.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].Llargada
    build_ele.BarraGruixHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].Gruix

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].IsUseGlobalProp
    build_ele.FounColorHor.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesTDHortInter.value[nBarraVert * NombreBarresHorInt + nHor].BarraLayer

    if len(build_ele.ColisHorInt.value) < nHor* 3 + 2:
        set_valors_hor_ini(build_ele, nBarraVert, nHor)
    build_ele.ColisVertListToShow.value[0] = build_ele.ColisHorInt.value[nHor* 3 + 0]
    build_ele.ColisVertListToShow.value[1] = build_ele.ColisHorInt.value[nHor* 3 + 1]
    build_ele.ColisVertListToShow.value[2] = build_ele.ColisHorInt.value[nHor* 3 + 2]

    build_ele.PotesVertListToShow.value[0] = build_ele.PotesHorInt.value[nHor* 3 + 0]
    build_ele.PotesVertListToShow.value[1] = build_ele.PotesHorInt.value[nHor* 3 + 1]
    build_ele.PotesVertListToShow.value[2] = build_ele.PotesHorInt.value[nHor* 3 + 2]

    if len(build_ele.ForatsHorInt.value) <= nHor *10  + 10 :
        set_valors_hor_ini(build_ele, nBarraVert, nHor)
    build_ele.ForatsHorListToShow.value[0] = build_ele.ForatsHorInt.value[nHor*10 + 0]#[nBarraVert * NombreBarresHorInt + nHor*10 + 0]
    build_ele.ForatsHorListToShow.value[1] = build_ele.ForatsHorInt.value[nHor*10 + 1]#[nBarraVert * NombreBarresHorInt + nHor*10 + 1]
    build_ele.ForatsHorListToShow.value[2] = build_ele.ForatsHorInt.value[nHor*10 + 2]#[nBarraVert * NombreBarresHorInt + nHor*10 + 2]
    build_ele.ForatsHorListToShow.value[3] = build_ele.ForatsHorInt.value[nHor*10 + 3]#[nBarraVert * NombreBarresHorInt + nHor*10 + 3]
    build_ele.ForatsHorListToShow.value[4] = build_ele.ForatsHorInt.value[nHor*10 + 4]#[nBarraVert * NombreBarresHorInt + nHor*10 + 4]
    build_ele.ForatsHorListToShow.value[5] = build_ele.ForatsHorInt.value[nHor*10 + 5]#[nBarraVert * NombreBarresHorInt + nHor*10 + 5]
    build_ele.ForatsHorListToShow.value[6] = build_ele.ForatsHorInt.value[nHor*10 + 6]#[nBarraVert * NombreBarresHorInt + nHor*10 + 6]
    build_ele.ForatsHorListToShow.value[7] = build_ele.ForatsHorInt.value[nHor*10 + 7]#[nBarraVert * NombreBarresHorInt + nHor*10 + 7]
    build_ele.ForatsHorListToShow.value[8] = build_ele.ForatsHorInt.value[nHor*10 + 8]#[nBarraVert * NombreBarresHorInt + nHor*10 + 8]
    build_ele.ForatsHorListToShow.value[9] = build_ele.ForatsHorInt.value[nHor*10 + 9]#[nBarraVert * NombreBarresHorInt + nHor*10 + 9]

    build_ele.FemellesVertListToShow.value[0] = build_ele.FemellesHorInt.value[nHor * 3 + 0]
    build_ele.FemellesVertListToShow.value[1] = build_ele.FemellesHorInt.value[nHor * 3 + 1]
    build_ele.FemellesVertListToShow.value[2] = build_ele.FemellesHorInt.value[nHor * 3 + 2]

    build_ele.Ample_forat_femellaVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella

    build_ele.posicio_centre_massesVert.value =  build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].posicio_centre_masses
    build_ele.IsFirstCancamVert.value=  build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].IsFirstCancam
    build_ele.Dis1cancamVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].Dis1cancam
    build_ele.IsSecondCancamVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].IsSecondCancam
    build_ele.Dis2cancamVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].Dis2cancam
    build_ele.PestanyaSuperiorVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].PestanyaSup
    build_ele.PestanyaInferiorVert.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].PestanyaInf

    build_ele.esVermellHor.value = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor].vermell


    build_ele.EncaixVertListToShow.value[0] = build_ele.EncaixHorInt.value[nHor * 3 + 0]
    build_ele.EncaixVertListToShow.value[1] = build_ele.EncaixHorInt.value[nHor * 3 + 1]
    build_ele.EncaixVertListToShow.value[2] = build_ele.EncaixHorInt.value[nHor * 3 + 2]

#guardar valors
def guardar_valors_hor(build_ele, nBarraVert, nHor):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraHor = build_ele.BarresHorListToShowTD.value[0].BarraHor)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Orientacio = build_ele.BarresHorListToShowTD.value[0].Orientacio)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Posicio = build_ele.BarresHorListToShowTD.value[0].Posicio)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(AutoLongitud = build_ele.BarresHorListToShowTD.value[0].AutoLongitud)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Longitud = build_ele.BarresHorListToShowTD.value[0].Longitud)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraInici = build_ele.BarresHorListToShowTD.value[0].BarraInici)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraFinal = build_ele.BarresHorListToShowTD.value[0].BarraFinal)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Edit = build_ele.BarresHorListToShowTD.value[0].Edit)
    #build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.BarresHorList.value[nBarraVert* NombreBarresHorInt + nHor]._replace(acabatEditar = build_ele.BarresHorListToShowTD.value[0].acabatEditar)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorList.value[nHor].Edit)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplX = build_ele.desplXVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplY = build_ele.desplYVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplX = build_ele.desplXHorAbs.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplY = build_ele.desplYHorAbs.value)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(linia = build_ele.SelectorLiniaHor.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(layer = build_ele.SelectorLayerHor.value)


    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample = build_ele.BarraAmpleHor.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura = build_ele.BarraAlturaHor.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Llargada = build_ele.BarraLlargadaHor.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Gruix = build_ele.BarraGruixHor.value)


    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(FounColor = build_ele.FounColorHor.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    build_ele.ColisHorInt.value[nHor* 3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisHorInt.value[nHor* 3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisHorInt.value[nHor* 3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesHorInt.value[nHor* 3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesHorInt.value[nHor* 3 + 1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesHorInt.value[nHor* 3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsHorInt.value[nHor*10 + 0] = build_ele.ForatsHorListToShow.value[0]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 1] = build_ele.ForatsHorListToShow.value[1]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 2] = build_ele.ForatsHorListToShow.value[2]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 3] = build_ele.ForatsHorListToShow.value[3]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 4] = build_ele.ForatsHorListToShow.value[4]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 5] = build_ele.ForatsHorListToShow.value[5]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 6] = build_ele.ForatsHorListToShow.value[6]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 7] = build_ele.ForatsHorListToShow.value[7]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 8] = build_ele.ForatsHorListToShow.value[8]#nBarraVert* NombreBarresHorInt +
    build_ele.ForatsHorInt.value[nHor*10 + 9] = build_ele.ForatsHorListToShow.value[9]#nBarraVert* NombreBarresHorInt +

    build_ele.FemellesHorInt.value[nHor* 3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesHorInt.value[nHor* 3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesHorInt.value[nHor* 3 + 2] = build_ele.FemellesVertListToShow.value[2]


    build_ele.FemellesHorInt.value[nHor* 3 + 0] = build_ele.FemellesHorInt.value[nHor* 3 + 0]._replace(Separacio_forat_femella = build_ele.dadesTDHortInter.value[nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nHor* 3 + 1] = build_ele.FemellesHorInt.value[nHor* 3 + 1]._replace(Separacio_forat_femella = build_ele.dadesTDHortInter.value[nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nHor* 3 + 2] = build_ele.FemellesHorInt.value[nHor* 3 + 2]._replace(Separacio_forat_femella = build_ele.dadesTDHortInter.value[nHor].Separacio_forat_femella)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)


    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaSup = build_ele.PestanyaSuperiorVert.value)
    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(PestanyaInf = build_ele.PestanyaInferiorVert.value)

    build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDHortInter.value[nBarraVert* NombreBarresHorInt + nHor]._replace(vermell = build_ele.esVermellHor.value)


    build_ele.EncaixHorInt.value[nHor * 3 + 0] = build_ele.EncaixVertListToShow.value[0]
    build_ele.EncaixHorInt.value[nHor * 3 + 1] = build_ele.EncaixVertListToShow.value[1]
    build_ele.EncaixHorInt.value[nHor * 3 + 2] = build_ele.EncaixVertListToShow.value[2]


#guardar valors premarcs
def guardar_valors_incl(build_ele, nBalcFin):
    '''
    mostrar valors de les Barres Horitzontals intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nHor -> posicio[][] del valor dins de la Barra Vertical

    return: -
    dadesTDInclinades
    dadesTDInclinades
    '''

    if nBalcFin >= len(build_ele.dadesTDInclinades.value):
        set_valors_incl(build_ele, nBalcFin)


    #build_ele.dadesTDInclinades.value[nBarraVert* NombreBarresHorInt + nHor] = build_ele.dadesTDInclinades.value[nBarraVert* NombreBarresHorInt + nHor]._replace(estaEditant = build_ele.BarresHorList.value[nHor].Edit)

    build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(MostrarInclinat = build_ele.MostrarBalconera.value)
    build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(nom = build_ele.nomPremarc.value)

    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(desplX = build_ele.desplXVertAbs.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(desplY = build_ele.desplYVertAbs.value)

    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(desplLinA = build_ele.desplVertLinA.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(desplLinB = build_ele.desplVertLinB.value)

    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Ample = build_ele.BarraAmpleVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Altura = build_ele.BarraAlturaVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Llargada = build_ele.BarraLlargadaVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Gruix = build_ele.BarraGruixVert.value)


    build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(BarraLayer = build_ele.BarraLayerVert.value)

    '''
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.ColisVertListToShow.value[0]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.ColisVertListToShow.value[1]
    build_ele.ColisHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.ColisVertListToShow.value[2]

    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.PotesVertListToShow.value[0]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 +  1] = build_ele.PotesVertListToShow.value[1]
    build_ele.PotesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.PotesVertListToShow.value[2]

    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 0] = build_ele.ForatsVertListToShow.value[0]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 1] = build_ele.ForatsVertListToShow.value[1]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 2] = build_ele.ForatsVertListToShow.value[2]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 3] = build_ele.ForatsVertListToShow.value[3]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 4] = build_ele.ForatsVertListToShow.value[4]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 5] = build_ele.ForatsVertListToShow.value[5]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 6] = build_ele.ForatsVertListToShow.value[6]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 7] = build_ele.ForatsVertListToShow.value[7]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 8] = build_ele.ForatsVertListToShow.value[8]
    build_ele.ForatsHorInt.value[nBarraVert* NombreBarresHorInt + nHor*10 + 9] = build_ele.ForatsVertListToShow.value[9]

    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesVertListToShow.value[0]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesVertListToShow.value[1]
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesVertListToShow.value[2]


    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 0]._replace(Separacio_forat_femella = build_ele.dadesTDInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 1]._replace(Separacio_forat_femella = build_ele.dadesTDInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2] = build_ele.FemellesHorInt.value[nBarraVert* NombreBarresHorInt + nHor* 3 + 2]._replace(Separacio_forat_femella = build_ele.dadesTDInclinades.value[nBarraVert* NombreBarresHorInt + nHor].Separacio_forat_femella)
    '''
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Ample_forat_femella = build_ele.Ample_forat_femellaVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Altura_forat_femella = build_ele.Altura_forat_femellaVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Separacio_forat_femella = build_ele.Separacio_forat_femellaVert.value)


    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(posicio_centre_masses = build_ele.posicio_centre_massesVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(IsFirstCancam = build_ele.IsFirstCancamVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Dis1cancam = build_ele.Dis1cancamVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(IsSecondCancam = build_ele.IsSecondCancamVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(Dis2cancam = build_ele.Dis2cancamVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(PestanyaSup = build_ele.PestanyaSuperiorVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(PestanyaInf = build_ele.PestanyaInferiorVert.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(femellaSup = build_ele.femellaSup.value)
    #build_ele.dadesTDInclinades.value[nBalcFin] = build_ele.dadesTDInclinades.value[nBalcFin]._replace(femellaInf = build_ele.femellaInf.value)

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

    while nBarraVert >= len(build_ele.dadesTDInclinades.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'MostrarInclinat nom Ample Altura Llargada Gruix desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf femellaSup femellaInf Posicio Angle')
        bob = TDHorCollection(MostrarInclinat = False,
                              nom = "Premarc.",
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
                            Altura_forat_femella = 3.0,
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
        build_ele.dadesTDInclinades.value.append(bob)

    '''
    while nBarraVert * 3 + nHor * 3 + 3 >= len(build_ele.ColisHorInt.value):
        build_ele.ColisHorInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1] = build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1]._replace(Colis = False)
    while nBarraVert * 3 + nHor *3 + 3 >= len(build_ele.PotesHorInt.value):
        build_ele.PotesHorInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1] = build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1]._replace(Pota = False)
    while nBarraVert * 3 + nHor *3 + 8 >= len(build_ele.ForatsHorInt.value):
        build_ele.ForatsHorInt.value.append(build_ele.ForatsVertListToShow.value[0])
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
                posY = Altura/2 - 15/2 + desply - build_ele.desplYI.value + desplAct - build_ele.listDesplVerticalsTD.value[j].desplY - build_ele.dadesTDHortInter.value[barraSupHor].desplY
            else:
                if orientacio == "Esq":
                    posY = Altura/2 - 15/2 + desply  - desplAct - build_ele.listDesplVerticalsTD.value[j].desplY #- build_ele.dadesTDHortInter.value
                else:
                    posY = Altura/2 - 15/2 + desply   - build_ele.listDesplVerticalsTD.value[j].desplY - build_ele.dadesTDHortInter.value[barraSupHor].desplY
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

    while nBarraVert * 3 + nHor >= len(build_ele.dadesTDHortInter.value):
        TDHorCollection = collections.namedtuple('StirrupList', 'Ample Altura Llargada Gruix desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf linia layer vermell')
        bob = TDHorCollection(Ample = 30,
                            Altura = 30,
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
                            BarraLayer = 40001,
                            Ample_forat_femella = 15,
                            Altura_forat_femella = 3.0,
                            Separacio_forat_femella = 30,
                            posicio_centre_masses = 500,
                            IsFirstCancam = False,
                            Dis1cancam = 500,
                            IsSecondCancam =False,
                            Dis2cancam = 1000,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            linia = "Tipus 1",
                            layer = "TD_FIXACIO",
                            vermell = False
                            )
        build_ele.dadesTDHortInter.value.append(bob)

    while nHor * 3 + 3 >= len(build_ele.ColisHorInt.value):
        build_ele.ColisHorInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1] = build_ele.ColisHorInt.value[len(build_ele.ColisHorInt.value)-1]._replace(Colis = False)
    while nHor * 3 + 3 >= len(build_ele.PotesHorInt.value):
        build_ele.PotesHorInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1] = build_ele.PotesHorInt.value[len(build_ele.PotesHorInt.value)-1]._replace(Pota = False)
    while nHor * 10 + 10 >= len(build_ele.ForatsHorInt.value):
        build_ele.ForatsHorInt.value.append(build_ele.ForatsHorListToShow.value[0])
        build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1] = build_ele.ForatsHorInt.value[len(build_ele.ForatsHorInt.value)-1]._replace(Forat = False)
    while nHor * 3 + 3 >= len(build_ele.FemellesHorInt.value):
        build_ele.FemellesHorInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1] = build_ele.FemellesHorInt.value[len(build_ele.FemellesHorInt.value)-1]._replace(Femella = False)
    while nHor * 3 + 3 >= len(build_ele.EncaixHorInt.value):
        build_ele.EncaixHorInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1] = build_ele.EncaixHorInt.value[len(build_ele.EncaixHorInt.value)-1]._replace(Encaix = False)

#mostrar valors Vert
def mostrar_valors_Vert(build_ele, nBarraVert, nVert):
    nBarresVertInt = NombreBarresVertInt
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(estaEditant = build_ele.BarresVertListToShow.value[nVert].Edit)

    build_ele.BarraAmpleVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraAmple
    build_ele.BarraAlturaVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraAltura
    build_ele.BarraGruixVert.value = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert].BarraGruix


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

    if (nBarraVert * nBarresVertInt + nVert)* 10 + 10 > len(build_ele.ForatsVertInt.value):
        set_valors_Vert_ini(build_ele, nBarraVert, nVert)

    build_ele.ForatsVertListToShow.value[0] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 0]
    build_ele.ForatsVertListToShow.value[1] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 1]
    build_ele.ForatsVertListToShow.value[2] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 2]
    build_ele.ForatsVertListToShow.value[3] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 3]
    build_ele.ForatsVertListToShow.value[4] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 4]
    build_ele.ForatsVertListToShow.value[5] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 5]
    build_ele.ForatsVertListToShow.value[6] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 6]
    build_ele.ForatsVertListToShow.value[7] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 7]
    build_ele.ForatsVertListToShow.value[8] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 8]
    build_ele.ForatsVertListToShow.value[9] = build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 9]

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
    build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert] = build_ele.dadesTDVertInter.value[nBarraVert * nBarresVertInt + nVert]._replace(BarraGruix = build_ele.BarraGruixVert.value)


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

    if (nBarraVert * nBarresVertInt + nVert)* 10 + 10 > len(build_ele.ForatsVertInt.value):
        set_valors_Vert_ini(build_ele, nBarraVert, nVert)
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 0] = build_ele.ForatsVertListToShow.value[0]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 1] = build_ele.ForatsVertListToShow.value[1]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 2] = build_ele.ForatsVertListToShow.value[2]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 3] = build_ele.ForatsVertListToShow.value[3]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 4] = build_ele.ForatsVertListToShow.value[4]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 5] = build_ele.ForatsVertListToShow.value[5]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 6] = build_ele.ForatsVertListToShow.value[6]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 7] = build_ele.ForatsVertListToShow.value[7]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 8] = build_ele.ForatsVertListToShow.value[8]
    build_ele.ForatsVertInt.value[(nBarraVert * nBarresVertInt + nVert)* 10 + 9] = build_ele.ForatsVertListToShow.value[9]

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
                                BarraLayer = 40001,
                                Ample_forat_femella = 15,
                                Altura_forat_femella = 3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = True,
                                pestanyaInf = True,
                                FemellaSup = True,
                                FemellaInf = True,
                                FemellaSupe = True,
                                FemellaInfe= True)
        build_ele.dadesTDVertInter.value.append(bob)

    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.ColisVertInt.value):
        build_ele.ColisVertInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisVertInt.value[len(build_ele.ColisVertInt.value)-1] = build_ele.ColisVertInt.value[len(build_ele.ColisVertInt.value)-1]._replace(Colis = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.PotesVertInt.value):
        build_ele.PotesVertInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesVertInt.value[len(build_ele.PotesVertInt.value)-1] = build_ele.PotesVertInt.value[len(build_ele.PotesVertInt.value)-1]._replace(Pota = False)
    while (nBarraVert * nBarresVertInt + Nvert) * 10 + 10 >= len(build_ele.ForatsVertInt.value):
        build_ele.ForatsVertInt.value.append(build_ele.ForatsVertListToShow.value[0])
        build_ele.ForatsVertInt.value[len(build_ele.ForatsVertInt.value)-1] = build_ele.ForatsVertInt.value[len(build_ele.ForatsVertInt.value)-1]._replace(Forat = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.FemellesVertInt.value):
        build_ele.FemellesVertInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesVertInt.value[len(build_ele.FemellesVertInt.value)-1] = build_ele.FemellesVertInt.value[len(build_ele.FemellesVertInt.value)-1]._replace(Femella = False)
    while nBarraVert * nBarresVertInt + Nvert * 4 + 3 >= len(build_ele.EncaixVertInt.value):
        build_ele.EncaixVertInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixVertInt.value[len(build_ele.EncaixVertInt.value)-1] = build_ele.EncaixVertInt.value[len(build_ele.EncaixVertInt.value)-1]._replace(Encaix = False)

#set valors Vert
def set_valors_Ref_ini(build_ele, nBarraVert):
    '''
    definir valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    while nBarraVert >= len(build_ele.dadesENReftInterTD.value):
        ENRefCollection = collections.namedtuple('StirrupList', 'Ample Altura Llargada Gruix desplX desplY mostrarLiniaVertA desplLinA mostrarLiniaVertB desplLinB estaEditant acabatEditar IsUseGlobalProp FounColor BarraLayer Ample_forat_femella Altura_forat_femella Separacio_forat_femella posicio_centre_masses IsFirstCancam Dis1cancam IsSecondCancam Dis2cancam PestanyaSup PestanyaInf linia layer')
        bob = ENRefCollection(Ample = 30,
                            Altura = 30,
                            Llargada = build_ele.BarraLlargadaVert.value,
                            #Gruix = build_ele.BarraGruixVert.value,
                            Gruix = 2,
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
                            Altura_forat_femella = 3.0,
                            Separacio_forat_femella = 30,
                            posicio_centre_masses = 500,
                            IsFirstCancam = False,
                            Dis1cancam = 500,
                            IsSecondCancam =False,
                            Dis2cancam = 1000,
                            PestanyaSup = True,
                            PestanyaInf = True,
                            linia = "Tipus 1",
                            layer = "TD_FIXACIO")
        build_ele.dadesENReftInterTD.value.append(bob)

    '''
    while nBarraVert  * 3 + 3 >= len(build_ele.ColisRefInt.value):
        build_ele.ColisRefInt.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisRefInt.value[len(build_ele.ColisRefInt.value)-1] = build_ele.ColisRefInt.value[len(build_ele.ColisRefInt.value)-1]._replace(Colis = False)
    while nBarraVert  *3 + 3 >= len(build_ele.PotesRefInt.value):
        build_ele.PotesRefInt.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesRefInt.value[len(build_ele.PotesRefInt.value)-1] = build_ele.PotesRefInt.value[len(build_ele.PotesRefInt.value)-1]._replace(Pota = False)
    while nBarraVert  *3 + 8 >= len(build_ele.ForatsRefInt.value):
        build_ele.ForatsRefInt.value.append(build_ele.ForatsVertListToShow.value[0])
        build_ele.ForatsRefInt.value[len(build_ele.ForatsRefInt.value)-1] = build_ele.ForatsRefInt.value[len(build_ele.ForatsRefInt.value)-1]._replace(Forat = False)
    while nBarraVert  *3 + 3 >= len(build_ele.FemellesRefInt.value):
        build_ele.FemellesRefInt.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesRefInt.value[len(build_ele.FemellesRefInt.value)-1] = build_ele.FemellesRefInt.value[len(build_ele.FemellesRefInt.value)-1]._replace(Femella = False)

    while nBarraVert  *3 + 3 >= len(build_ele.EncaixRefInt.value):
        build_ele.EncaixRefInt.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixRefInt.value[len(build_ele.EncaixRefInt.value)-1] = build_ele.EncaixRefInt.value[len(build_ele.EncaixRefInt.value)-1]._replace(Encaix = False)
    '''

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
        if x >= len(build_ele.FemellesVertListTD.value):
            set_values_femelles(build_ele, x)
        Femelles.append(build_ele.FemellesVertListTD.value[x])


    Potes = []
    for x in range(build_ele.nListPotesVert.value[j].Posicio, build_ele.nListPotesVert.value[j].Posicio + build_ele.nListPotesVert.value[j].nTotal):
        if x >= len(build_ele.PotesVertList.value):
            set_values_potes(build_ele, x)
        Potes.append(build_ele.PotesVertList.value[x])

    Forats = []
    for x in range(build_ele.nListForatsVert.value[j].Posicio, build_ele.nListForatsVert.value[j].Posicio + build_ele.nListForatsVert.value[j].nTotal):
        if x >= len(build_ele.ForatsVertList.value):
            set_values_forats(build_ele, x)
        Forats.append(build_ele.ForatsVertList.value[x])

    Colis = []
    for x in range(build_ele.nListColisVert.value[j].Posicio, build_ele.nListColisVert.value[j].Posicio + build_ele.nListColisVert.value[j].nTotal):
        if x >= len(build_ele.ColisVertList.value):
            set_values_colis(build_ele, x)
        Colis.append(build_ele.ColisVertList.value[x])

    return Encaixos, Femelles, Potes, Forats, Colis

def mostrar_valors_adjacents(build_ele,posBarraHor):

    if build_ele.BarresAdjList.value[posBarraHor].Longitud <= 0:
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(BarraAdj = False)
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Orientacio = 'Sup')
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Posicio = 0.0)
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Longitud = 100)
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Edit = False)
        build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(acabatEditar = False)

    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(BarraAdj = build_ele.BarresAdjList.value[posBarraHor].BarraAdj)
    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Orientacio = build_ele.BarresAdjList.value[posBarraHor].Orientacio)
    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Posicio = build_ele.BarresAdjList.value[posBarraHor].Posicio)
    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Longitud = build_ele.BarresAdjList.value[posBarraHor].Longitud)
    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(Edit = build_ele.BarresAdjList.value[posBarraHor].Edit)
    build_ele.BarresAdjListToShow.value[0] = build_ele.BarresAdjListToShow.value[0]._replace(acabatEditar = build_ele.BarresAdjList.value[posBarraHor].acabatEditar)


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

    #build_ele.ForatsVertListToShow.value[0] = build_ele.ForatsAdj.value[posBarraHor * 3 + 0 ]
    #build_ele.ForatsVertListToShow.value[1] = build_ele.ForatsAdj.value[posBarraHor * 3 + 1 ]
    #build_ele.ForatsVertListToShow.value[2] = build_ele.ForatsAdj.value[posBarraHor * 3 + 2 ]

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

    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(BarraAdj = build_ele.BarresAdjListToShow.value[0].BarraAdj)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Orientacio = build_ele.BarresAdjListToShow.value[0].Orientacio)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Posicio = build_ele.BarresAdjListToShow.value[0].Posicio)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Longitud = build_ele.BarresAdjListToShow.value[0].Longitud)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Profunditat = build_ele.BarresAdjListToShow.value[0].Profunditat)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(Edit = build_ele.BarresAdjListToShow.value[0].Edit)
    build_ele.BarresAdjList.value[posBarraHor] = build_ele.BarresAdjList.value[posBarraHor]._replace(acabatEditar = build_ele.BarresAdjListToShow.value[0].acabatEditar)

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

    while nBarraAdj >= len(build_ele.BarresAdjList.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraAdj Orientacio Posicio Longitud Profunditat Edit acabatEditar')
        bob = TDVertCollection( BarraAdj = False,
                                Orientacio = 'Sup',
                                Posicio = 0.0,
                                Longitud = 100.0,
                                Profunditat = 0,
                                Edit = False,
                                acabatEditar = False)
        build_ele.BarresAdjList.value.append(bob)

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
                                BarraLayer = 40001,
                                Ample_forat_femella = 15,
                                Altura_forat_femella = 3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = True,
                                pestanyaInf = True)
        build_ele.dadesAdj.value.append(bob)

    while nBarraAdj  * 3 + 3 >= len(build_ele.ColisAdj.value):
        build_ele.ColisAdj.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisAdj.value[len(build_ele.ColisAdj.value)-1] = build_ele.ColisAdj.value[len(build_ele.ColisAdj.value)-1]._replace(Colis = False)
    while nBarraAdj  * 3 + 3 >= len(build_ele.PotesAdj.value):
        build_ele.PotesAdj.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesAdj.value[len(build_ele.PotesAdj.value)-1] = build_ele.PotesAdj.value[len(build_ele.PotesAdj.value)-1]._replace(Pota = False)
    #while nBarraAdj  * 3 + 3 >= len(build_ele.ForatsAdj.value):
    #    build_ele.ForatsAdj.value.append(build_ele.ForatsVertListToShow.value[0])
    #    build_ele.ForatsAdj.value[len(build_ele.ForatsAdj.value)-1] = build_ele.ForatsAdj.value[len(build_ele.ForatsAdj.value)-1]._replace(Forat = False)
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

    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(BarraFront = build_ele.BarresFrontListAux.value[posBarraHor].BarraFront)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Amplitud = build_ele.BarresFrontListAux.value[posBarraHor].Amplitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Altura = build_ele.BarresFrontListAux.value[posBarraHor].Altura)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Orientacio = build_ele.BarresFrontListAux.value[posBarraHor].Orientacio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Posicio = build_ele.BarresFrontListAux.value[posBarraHor].Posicio)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Longitud = build_ele.BarresFrontListAux.value[posBarraHor].Longitud)
    build_ele.BarresFrontListToShow.value[posBarraFrontShow] = build_ele.BarresFrontListToShow.value[posBarraFrontShow]._replace(Profunditat = build_ele.BarresFrontListAux.value[posBarraHor].Profunditat)

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
            TDCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
            bob = TDCollection( BarraFront = False,
                                Amplitud = 30,
                                Altura = 40,
                                Orientacio = 'Esq',
                                Posicio = 100.0,
                                Longitud = 100.0,
                                Profunditat = 10.0,
                                Edit = False,
                                Save = False,
                                acabatEditar = False)

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
                                BarraLayer = 40001,
                                Ample_forat_femella = 15 ,
                                Altura_forat_femella = 3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = True,
                                pestanyaInf = True)
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
                                BarraLayer = 40001,
                                Ample_forat_femella = 15 ,
                                Altura_forat_femella = 3.75 ,
                                Separacio_forat_femella = 30,
                                posicio_centre_masses = 500,
                                IsFirstCancam = False,
                                Dis1cancam = 500,
                                IsSecondCancam =False,
                                Dis2cancam = 1000,
                                pestanyaSup = True,
                                pestanyaInf = True)
        build_ele.dadesFront.value.append(bob)

    while nBarraFront  * 3 + 3 >= len(build_ele.ColisFront.value):
        build_ele.ColisFront.value.append(build_ele.ColisVertListToShow.value[0])
        build_ele.ColisFront.value[len(build_ele.ColisFront.value)-1] = build_ele.ColisFront.value[len(build_ele.ColisFront.value)-1]._replace(Colis = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.PotesFront.value):
        build_ele.PotesFront.value.append(build_ele.PotesVertListToShow.value[0])
        build_ele.PotesFront.value[len(build_ele.PotesFront.value)-1] = build_ele.PotesFront.value[len(build_ele.PotesFront.value)-1]._replace(Pota = False)
    #while nBarraFront  * 3 + 3 >= len(build_ele.ForatsFront.value):
    #    build_ele.ForatsFront.value.append(build_ele.ForatsVertListToShow.value[0])
    #    build_ele.ForatsFront.value[len(build_ele.ForatsFront.value)-1] = build_ele.ForatsFront.value[len(build_ele.ForatsFront.value)-1]._replace(Forat = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.FemellesFront.value):
        build_ele.FemellesFront.value.append(build_ele.FemellesVertListToShow.value[0])
        build_ele.FemellesFront.value[len(build_ele.FemellesFront.value)-1] = build_ele.FemellesFront.value[len(build_ele.FemellesFront.value)-1]._replace(Femella = False)
    while nBarraFront  * 3 + 3 >= len(build_ele.EncaixFront.value):
        build_ele.EncaixFront.value.append(build_ele.EncaixVertListToShow.value[0])
        build_ele.EncaixFront.value[len(build_ele.EncaixFront.value)-1] = build_ele.EncaixFront.value[len(build_ele.EncaixFront.value)-1]._replace(Encaix = False)


def createCancam(build_ele, altura, firstCancam, secondCancam, primerCilimdre, segonCilindre):
    cancamSup1 = CilindreCancam(random.random() * 3600, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraGruixSup.value,
                                    firstCancam, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                    secondCancam, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                    23, 40002, True, primerCilimdre, segonCilindre)

    if not cancamSup1.is_valid():
        return[]
    cancamSup1_Brep = cancamSup1.create()
    common_props_cancamSup1 = cancamSup1.get_common_props()

    views_cancamSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_cancamSup1, cancamSup1.create())])]

    attr_list_cancamSup = [AllplanBaseElements.AttributeString(2103, "TDCilindreCancam "),
                            AllplanBaseElements.AttributeString(1083, "FEMELLA HEXAGONAL M10"),
                            AllplanBaseElements.AttributeString(1087, "Cancam"),
                            AllplanBaseElements.AttributeString(508, " ")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.posicio_centre_massesSUP.value + build_ele.desplXS.value)
    vectorCan.SetValue(13, build_ele.desplYS.value)
    vectorCan.SetValue(14, altura)

    return PythonPart ("PP_TD_CilindreCancam", parameter_list = cancamSup1.get_params_list(),
                                    hash_value = cancamSup1.hash(), python_file = cancamSup1.filename(),
                                    views = views_cancamSup, matrix = vectorCan, common_props = common_props_cancamSup1, attribute_list = attr_list_cancamSup)

def createPolylineCancam(build_ele, altura, firstCancam, secondCancam, primerCilimdre, segonCilindre):

    common_propsLinia = AllplanBaseElements.CommonProperties()
    common_propsLinia.GetGlobalProperties()

    common_propsLinia.Layer = 40001#(TD_Estructura)
    liniaInterior = LiniaInterior(random.random() * 3600, 20, False)
    if not liniaInterior.is_valid():
        return[]

    liniaInterior_brep = liniaInterior.create()
    liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                AllplanBaseElements.AttributeString(1083, " "),
                                AllplanBaseElements.AttributeString(1085, "1"),
                                AllplanBaseElements.AttributeString(1087, "Cancam")]
    liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]
    handle_list = liniaInterior.create_handles()

    vectorPOS = AllplanGeo.Matrix3D()
    vectorPOS.SetValue(12, build_ele.posicio_centre_massesSUP.value - build_ele.Dis1cancamSUP.value/2 + build_ele.desplXS.value)
    vectorPOS.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value/2)
    vectorPOS.SetValue(14, altura + build_ele.BarraAlturaSup.value)
    if firstCancam:
        if primerCilimdre:
            vectorPOS.SetValue(12, build_ele.posicio_centre_massesSUP.value - build_ele.Dis1cancamSUP.value/2 + build_ele.desplXS.value)
            vectorPOS.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value/2)
            vectorPOS.SetValue(14, altura + build_ele.BarraAlturaSup.value)
        else:
            vectorPOS.SetValue(12, build_ele.posicio_centre_massesSUP.value + build_ele.Dis1cancamSUP.value/2 + build_ele.desplXS.value)
            vectorPOS.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value/2)
            vectorPOS.SetValue(14, altura + build_ele.BarraAlturaSup.value)
    elif secondCancam:
        if primerCilimdre:
            vectorPOS.SetValue(12, build_ele.posicio_centre_massesSUP.value - build_ele.Dis2cancamSUP.value/2 + build_ele.desplXS.value)
            vectorPOS.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value/2)
            vectorPOS.SetValue(14, altura + build_ele.BarraAlturaSup.value)
        else:
            vectorPOS.SetValue(12, build_ele.posicio_centre_massesSUP.value + build_ele.Dis2cancamSUP.value/2 + build_ele.desplXS.value)
            vectorPOS.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value/2)
            vectorPOS.SetValue(14, altura + build_ele.BarraAlturaSup.value)

    return PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list)

def createColis(build_ele, altura, i):

    ColisSup = BoxColis(random.random() * 3600, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, build_ele.BarraGruixSup.value,
                                    build_ele.ColisParSUP.value, i,
                                    23, build_ele.BarraLayer.value)

    if not ColisSup.is_valid():
        return[]
    ColisSup_Brep = ColisSup.create()
    common_props_ColisSup = ColisSup.get_common_props()

    views_ColisSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_ColisSup, ColisSup.create())])]

    if build_ele.ColisParSUP.value[i].orientacio == "Sup":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA SUP "),
                                AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                                AllplanBaseElements.AttributeString(1087, "Reforc "),
                                AllplanBaseElements.AttributeString(508, " ")]#COLIS
    elif build_ele.ColisParSUP.value[i].orientacio == "Inf":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA INF "),
                                AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                                AllplanBaseElements.AttributeString(1087, "Reforc-Inferior "),
                                AllplanBaseElements.AttributeString(508, " ")]#COLIS
    elif build_ele.ColisParSUP.value[i].orientacio == "Esq":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA ESQ "),
                            AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS
    else:
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA DRE "),
                            AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.ColisParSUP.value[i].Posicio + build_ele.desplXS.value)
    vectorCan.SetValue(13, build_ele.desplYS.value)
    vectorCan.SetValue(14, altura + 1)

    return PythonPart ("PP_TD_BoxColis", parameter_list = ColisSup.get_params_list(),
                                    hash_value = ColisSup.hash(), python_file = ColisSup.filename(),
                                    views = views_ColisSup, matrix = vectorCan, common_props = common_props_ColisSup, attribute_list = attr_list_ColisSup)


def createColisCavitatHorSup(build_ele, altura, i):

    common_propsObject = AllplanBaseElements.CommonProperties()
    common_propsObject.Layer = 40054#(KN_XPS_RECESS)
    common_propsObject.Color = 31 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    common_propsObjectEsp = AllplanBaseElements.CommonProperties()
    common_propsObjectEsp.Layer = 40067#(KN_ESPONJA)
    common_propsObjectEsp.Color = 31 #blanc

    ampleCavForat = build_ele.MesuraXPS.value #140
    alturaCavForat = 150
    llargadaCavForat = 250

    colorCavitat = getColorCavitat(ampleCavForat)
    common_propsObject.Color = colorCavitat
    common_propsObject2.Color = colorCavitat
    colorCavitat = getColorCavitat(20 + build_ele.BarraAmpleSup.value + build_ele.desplYS.value)
    common_propsObjectEsp.Color = colorCavitat

    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject22 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2Esponja = PP_TD_Horitzontal(random.random() * 3600, 0, 20 + build_ele.BarraAmpleSup.value + build_ele.desplYS.value, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectEsp.Color, common_propsObjectEsp.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject22 = horitzontalPPOBject22.create()
    horitzontal_BrepObject2Esponja = horitzontalPPOBject2Esponja.create()


    vectorCav = AllplanGeo.Matrix3D()
    vectorCav.SetValue(12, build_ele.desplXS.value + build_ele.ColisParSUP.value[i].Posicio  - llargadaCavForat/2)#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)

    alturaColis = altura


    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(1,0,0))
    if build_ele.ColisParSUP.value[i].orientacio == "Inf":
        #vectorCav.SetValue(13, build_ele.desplYS.value - (ampleCavForat - build_ele.BarraAmpleSup.value) + 20)
        vectorCav.SetValue(14, alturaColis - alturaCavForat)

    elif build_ele.ColisParSUP.value[i].orientacio == "Sup":
        #vectorCav.SetValue(13, build_ele.desplYS.value - (ampleCavForat - build_ele.BarraAmpleSup.value) + 20)
        vectorCav.SetValue(14, alturaColis + build_ele.BarraAlturaSup.value )

    elif build_ele.ColisParSUP.value[i].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        #vectorCav.SetValue(13, build_ele.desplYS.value  )
        vectorCav.SetValue(14, alturaColis + (build_ele.BarraAlturaSup.value)/2 - ampleCavForat/2 )

    elif build_ele.ColisParSUP.value[i].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        #vectorCav.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value + alturaCavForat)
        #vectorCav.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleSup.value + alturaCavForat)
        vectorCav.SetValue(14, alturaColis + (build_ele.BarraAlturaSup.value)/2 - ampleCavForat/2 )


    vectorCavEsp = AllplanGeo.Matrix3D(vectorCav)
    vectorCavEsp.SetValue(13, -20)


    if build_ele.MostrarTDHoritzontalSup.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject22)])]
        table_views_object_2Esp = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectEsp, horitzontal_BrepObject2Esponja)])]

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT"),
                            #AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT"),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

        group_elems = []

        if build_ele.MostrarRecessSup.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))
        if build_ele.MostrarCavitatSup.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject22.get_params_list(),
                                    hash_value = horitzontalPPOBject22.hash(), python_file = horitzontalPPOBject22.filename(),
                                    views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))
        if build_ele.MostrarEsponja.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2Esponja.get_params_list(),
                                    hash_value = horitzontalPPOBject2Esponja.hash(), python_file = horitzontalPPOBject2Esponja.filename(),
                                    views = table_views_object_2Esp, matrix = vectorCavEsp, common_props = common_propsObjectEsp, attribute_list = table_attr_listObject))
        return group_elems
    return []


def createColisInf(build_ele, altura, i):

    ColisSup = BoxColis(random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, build_ele.BarraGruixInf.value,
                                    build_ele.ColisParINF.value, i,
                                    23, build_ele.BarraLayer.value)

    if not ColisSup.is_valid():
        return[]
    ColisSup_Brep = ColisSup.create()
    common_props_ColisSup = ColisSup.get_common_props()

    views_ColisSup = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_ColisSup, ColisSup.create())])]

    if build_ele.ColisParINF.value[i].orientacio == "Sup":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA SUP "),
                                AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                                AllplanBaseElements.AttributeString(1087, "Reforc "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS
    elif build_ele.ColisParINF.value[i].orientacio == "Inf":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA INF "),
                                AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                                AllplanBaseElements.AttributeString(1087, "Reforc-Inferior "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS
    elif build_ele.ColisParINF.value[i].orientacio == "Esq":
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA ESQ "),
                            AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS
    else:
        attr_list_ColisSup = [AllplanBaseElements.AttributeString(2103, "CHAPA DRE "),
                            AllplanBaseElements.AttributeString(1083, "REFORÇ COLÍS 168x30x3mm "),
                             AllplanBaseElements.AttributeString(508, " ")]#COLIS

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.ColisParINF.value[i].Posicio )
    vectorCan.SetValue(13, build_ele.desplYI.value)
    vectorCan.SetValue(14, 0)

    return PythonPart ("PP_TD_BoxColis", parameter_list = ColisSup.get_params_list(),
                                    hash_value = ColisSup.hash(), python_file = ColisSup.filename(),
                                    views = views_ColisSup, matrix = vectorCan, common_props = common_props_ColisSup, attribute_list = attr_list_ColisSup)

def createColisCavitatHorInf(build_ele, altura, i):

    common_propsObject = AllplanBaseElements.CommonProperties()
    common_propsObject.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 31 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    ampleCavForat = 140
    alturaCavForat = 150
    llargadaCavForat = 250

    colorCavitat = getColorCavitat(ampleCavForat)
    common_propsObject.Color = colorCavitat
    common_propsObject2.Color = colorCavitat

    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject22 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                False, False,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject22 = horitzontalPPOBject22.create()


    vectorCav = AllplanGeo.Matrix3D()
    vectorCav.SetValue(12, build_ele.desplXI.value + build_ele.ColisParINF.value[i].Posicio  - llargadaCavForat/2)#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)

    alturaColis = 0


    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(1,0,0))
    if build_ele.ColisParINF.value[i].orientacio == "Inf":
        vectorCav.SetValue(13, build_ele.desplYS.value - (ampleCavForat - build_ele.BarraAmpleInf.value)/2)
        vectorCav.SetValue(14, alturaColis - alturaCavForat)

    elif build_ele.ColisParINF.value[i].orientacio == "Sup":
        vectorCav.SetValue(13, build_ele.desplYS.value - (ampleCavForat - build_ele.BarraAmpleInf.value)/2)
        vectorCav.SetValue(14, alturaColis + build_ele.BarraAlturaInf.value )

    elif build_ele.ColisParINF.value[i].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.desplYS.value  )
        vectorCav.SetValue(14, alturaColis + (build_ele.BarraAlturaInf.value)/2 - ampleCavForat/2 )

    elif build_ele.ColisParINF.value[i].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.desplYS.value + build_ele.BarraAmpleInf.value + alturaCavForat)
        vectorCav.SetValue(14, alturaColis + (build_ele.BarraAlturaInf.value)/2 - ampleCavForat/2 )



    if build_ele.MostrarTDHoritzontalInf.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject22)])]

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT COLIS"),
                                 #AllplanBaseElements.AttributeString(508, " "),
                                AllplanBaseElements.AttributeString(2103, "CAVITAT COLIS"),
                                AllplanBaseElements.AttributeString(1083, "CAVITAT COLIS"),
                                AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

        group_elems = []

        if build_ele.MostrarRecessInf.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))

        if build_ele.MostrarCavitatInf.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject22.get_params_list(),
                                    hash_value = horitzontalPPOBject22.hash(), python_file = horitzontalPPOBject22.filename(),
                                    views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))
        return group_elems
    return []

def createCilindreInf(build_ele, i ):
    Cilindre = CilindreForat(random.random() * 3600, 20 , 5, 1.5,
                            1, 40003)


    if not Cilindre.is_valid():
        return[]
    Cilindre_Brep = Cilindre.create()
    common_props_Cilindre = Cilindre.get_common_props()

    views_Cilindre = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Cilindre, Cilindre_Brep)])]

    attr_list_Cilindre = [AllplanBaseElements.AttributeString(2103, "Forat INF "),
                                AllplanBaseElements.AttributeString(1083, "FEMELLA REMATXADA M10 "),
                                AllplanBaseElements.AttributeString(1087, "Rematxable"),
                             AllplanBaseElements.AttributeString(508, " ")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.PotaParINF.value[i].Posicio )
    vectorCan.SetValue(13, build_ele.desplYI.value + build_ele.BarraAmpleInf.value/2 - 20/2)
    vectorCan.SetValue(14, -5)


    common_propsLinia = AllplanBaseElements.CommonProperties()
    common_propsLinia.GetGlobalProperties()

    common_propsLinia.Layer = 40001#(TD_Estructura)
    liniaInterior = LiniaInterior(random.random() * 3600, 5, False)
    if not liniaInterior.is_valid():
        return[]

    liniaInterior_brep = liniaInterior.create()
    liniaInterior_attr_list = [AllplanBaseElements.AttributeString(508, " "),
                                AllplanBaseElements.AttributeString(2103, "LINIA INTERIOR"),
                                AllplanBaseElements.AttributeString(1083, " "),
                                AllplanBaseElements.AttributeString(1085, "1"),
                                AllplanBaseElements.AttributeString(1087, "Rematxable")]
    liniaInterior_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsLinia, liniaInterior_brep)])]
    handle_list = liniaInterior.create_handles()

    vectorPOS = AllplanGeo.Matrix3D()
    vectorPOS.SetValue(12, build_ele.PotaParINF.value[i].Posicio )
    vectorPOS.SetValue(13, build_ele.desplYI.value + build_ele.BarraAmpleInf.value/2 )
    vectorPOS.SetValue(14, -5)

    return [PythonPart ("TD_CilindreForat", parameter_list = Cilindre.get_params_list(),
                                    hash_value = Cilindre.hash(), python_file = Cilindre.filename(),
                                    views = views_Cilindre, matrix = vectorCan, common_props = common_props_Cilindre, attribute_list = attr_list_Cilindre),
            common_props_Cilindre,
            Cilindre_Brep,
            PythonPart ("liniaInterior", parameter_list = liniaInterior.get_params_list(),
                                hash_value = liniaInterior.hash(), python_file = liniaInterior.filename(),
                                views = liniaInterior_views, matrix = vectorPOS, common_props = common_propsLinia, attribute_list = liniaInterior_attr_list)]


def createBoxForat(build_ele, i, forats, nForat):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDVertTD.value[i].BarraAmple, build_ele.dadesTDVertTD.value[i].BarraAltura, build_ele.BarraLlargadaVert.value, build_ele.BarraGruixVert.value,
                                    False, 23, 40052, forats, False, nForat)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(nBoxForat.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(nBoxForat.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(nBoxForat.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(nBoxForat.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(nBoxForat.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(nBoxForat.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(nBoxForat.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(nBoxForat.get_codi_cara_d_inv()) )

    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),

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

                            AllplanBaseElements.AttributeString(2446, nBoxForat.get_codi_pota_inv()),

                            AllplanBaseElements.AttributeString(2430, nBoxForat.get_codi_pestanyes()),
                            AllplanBaseElements.AttributeString(2435, nBoxForat.get_codi_cancam()),
                            AllplanBaseElements.AttributeString(2431, nBoxForat.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2433, nBoxForat.get_codi_pota()),
                            AllplanBaseElements.AttributeString(2445, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(1084, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(220, nBoxForat.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, nBoxForat.get_llargada()),

                            AllplanBaseElements.AttributeString(1083, "TFF"),
                            AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),
                            AllplanBaseElements.AttributeString(220, "100")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) )
    vectorCan.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs)
    vectorCan.SetValue(14, 0)#barrainici pos
    nHorInf = 0
    if build_ele.dadesTDVertTD.value[i].BarraInferior != "TD Inferior":
        if len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 7:
            nHorInfCentenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-3])
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 6:
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 5:
            nHorInf = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])

        if not build_ele.dadesTDVertTD.value[i].EncaixInf:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2
        else:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 +1 #- build_ele.BarraAlturaInf.value/2# + build_ele.BarraAlturaSup.value/2 + 1.25
        vectorCan.SetValue(14, posHorInf)#barrainici pos
    else:
        if build_ele.dadesTDVertTD.value[i].EncaixInf:
            vectorCan.SetValue(14,  build_ele.BarraAlturaInf.value)#barrainici pos

    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, common_props = common_props_nBoxForat, attribute_list = attr_list_nBoxForat)

def createBoxForatCavitat(build_ele, i, forats, nForat):
    common_propsObject = AllplanBaseElements.CommonProperties()
    #common_propsObject.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Layer = 40067#(KN_ESPONJA)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 31 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    ampleCavForat = 50
    alturaCavForat = 20
    llargadaCavForat = 120

    if forats[nForat].orientacio == "Inf" or forats[nForat].orientacio == "Sup":
        colorCavitat = getColorCavitat(alturaCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat
    else:
        colorCavitat = getColorCavitat(ampleCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat

    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, alturaCavForat , llargadaCavForat, ampleCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, alturaCavForat , llargadaCavForat, ampleCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()


    vectorCav = AllplanGeo.Matrix3D()
    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - alturaCavForat/2)
    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs)
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Esq":
    #    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs)
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Dre":
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Sup":
    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(0,0,1))
    if forats[nForat].orientacio == "Inf":
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - alturaCavForat)

    elif forats[nForat].orientacio == "Sup":
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs + build_ele.dadesTDVertTD.value[i].BarraAltura)

    elif forats[nForat].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) )
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2)

    elif forats[nForat].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) + build_ele.dadesTDVertTD.value[i].BarraAmple + alturaCavForat)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2)


    vectorCav.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2)#barrainici pos
    if build_ele.dadesTDVertTD.value[i].EncaixInf:
        vectorCav.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2 + build_ele.BarraAlturaInf.value)#barrainici pos

    nHorInf = 0
    if build_ele.dadesTDVertTD.value[i].BarraInferior != "TD Inferior":
        if len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 7:
            nHorInfCentenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-3])
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 6:
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 5:
            nHorInf = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])

        if not build_ele.dadesTDVertTD.value[i].EncaixInf:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2 + forats[nForat].Posicio - llargadaCavForat/2
        else:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 +1 + forats[nForat].Posicio  - llargadaCavForat/2 #- build_ele.BarraAlturaInf.value/2# + build_ele.BarraAlturaSup.value/2 + 1.25
        vectorCav.SetValue(14, posHorInf )#barrainici pos

    if build_ele.dadesTDVertTD.value[i].MostrarTDVertical:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject2A)])]

        table_attr_listObject = [#AllplanBaseElements.AttributeString(508, " "),
                                 AllplanBaseElements.AttributeString(508, "CAVITAT"),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT"),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

        group_elems = []


        #if build_ele.dadesTDVertTD.value[i].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
        if build_ele.MostrarEsponja.value:#build_ele.MostrarCavitatsRecess.value:

            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                    hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                    views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))

        #if build_ele.dadesTDVertTD.value[i].MostrarCavitat and build_ele.MostrarCavitats.value:
        if build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                    hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                    views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))
        return group_elems
    return []

def createBoxForatCavitatXPS(build_ele, i, forats, nForat):
    common_propsObject = AllplanBaseElements.CommonProperties()
    common_propsObject.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    #common_propsObject.Layer = 40067#(KN_ESPONJA)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 31 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    ampleCavForat = 20
    #alturaCavForat = 40
    #if build_ele.tipusCavitatTFFVert.value == "60":
    #    alturaCavForat = 60
    alturaCavForat = build_ele.MesuraXPS.value - build_ele.dadesTDVertTD.value[i].BarraAltura - build_ele.listDesplVerticalsTD.value[i].desplYAbs

    llargadaCavForat = 50

    if forats[nForat].orientacio == "Inf" or forats[nForat].orientacio == "Sup":
        colorCavitat = getColorCavitat(alturaCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat
    else:
        colorCavitat = getColorCavitat(ampleCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat

    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, alturaCavForat , llargadaCavForat, ampleCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, alturaCavForat , llargadaCavForat, ampleCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()


    colorCavitat = getColorCavitat(20)

    common_props_Cilindre = AllplanBaseElements.CommonProperties()
    #common_props_Cilindre.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_props_Cilindre.Layer = 40057#(KN_PLD_RECESS)
    common_props_Cilindre.Color = colorCavitat

    common_props_Cilindre2 = AllplanBaseElements.CommonProperties()
    common_props_Cilindre2.Layer = 40055#(KN_XPS_CAVITAT)
    common_props_Cilindre2.Color = colorCavitat

    CilindreXPS = CilindreForatXPS(random.random() * 3600, 1 , 2, 1.5,
                            common_props_Cilindre.Color, common_props_Cilindre.Layer)
    CilindreXPS2 = CilindreForatXPS(random.random() * 3600, 20 , 5, 1.5,
                            common_props_Cilindre2.Color, common_props_Cilindre2.Layer)

    if not CilindreXPS.is_valid():
        return[]
    Cilindre_Brep = CilindreXPS.create()
    Cilindre_Brep2 = CilindreXPS2.create()
    common_props_Cilindre = CilindreXPS.get_common_props()
    common_props_Cilindre2 = CilindreXPS2.get_common_props()

    views_Cilindre = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Cilindre, Cilindre_Brep)])]
    views_Cilindre2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Cilindre2, Cilindre_Brep2)])]

    attr_list_Cilindre = [AllplanBaseElements.AttributeString(2103, "Cilindre Forat XPS "),
                                 AllplanBaseElements.AttributeString(508, "CAVITAT"),
                                #AllplanBaseElements.AttributeString(508, " ")
                                AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                                AllplanBaseElements.AttributeString(1087, "HOLE")]


    vectorCan = AllplanGeo.Matrix3D()

    if forats[nForat].orientacio == "Sup" or forats[nForat].orientacio == "Inf":
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(1,0,0))
    else:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(0,1,0))

    vectorCan.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))


    vectorCav = AllplanGeo.Matrix3D()
    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - alturaCavForat/2)
    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs)
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Esq":
    #    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs)
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Dre":
    #if build_ele.ForatsVertList.value[nForat].orientacio == "Sup":
    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(0,0,1))

    if forats[nForat].orientacio == "Sup":
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - alturaCavForat)

        vectorCan.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCan.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - alturaCavForat)

    elif forats[nForat].orientacio == "Inf":
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs + build_ele.dadesTDVertTD.value[i].BarraAltura)

        vectorCan.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCan.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs + build_ele.dadesTDVertTD.value[i].BarraAltura + alturaCavForat + 20)


    elif forats[nForat].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) )
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2)

        vectorCan.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - alturaCavForat - 20)
        vectorCan.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2 + 2)

    elif forats[nForat].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) + build_ele.dadesTDVertTD.value[i].BarraAmple + alturaCavForat)
        vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2)

        vectorCan.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) + build_ele.dadesTDVertTD.value[i].BarraAmple + alturaCavForat )
        vectorCan.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAltura)/2 + 2)

    vectorCav.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2)#barrainici pos
    if forats[nForat].orientacio == "Sup" or forats[nForat].orientacio == "Inf":
        vectorCan.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2 + 17)
    else:
        vectorCan.SetValue(14, forats[nForat].Posicio + 10)

    if build_ele.dadesTDVertTD.value[i].EncaixInf:
        vectorCav.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2 + build_ele.BarraAlturaInf.value)#barrainici pos

        vectorCan.SetValue(14, forats[nForat].Posicio - llargadaCavForat/2 + build_ele.BarraAlturaInf.value + 17)

    nHorInf = 0
    if build_ele.dadesTDVertTD.value[i].BarraInferior != "TD Inferior":
        if len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 7:
            nHorInfCentenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-3])
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 6:
            nHorInfDecenes = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-2])
            nHorInfUnitats = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])
            nHorInf = nHorInfDecenes*10 + nHorInfUnitats
        elif len(build_ele.dadesTDVertTD.value[i].BarraInferior) == 5:
            nHorInf = int(build_ele.dadesTDVertTD.value[i].BarraInferior[-1])

        if not build_ele.dadesTDVertTD.value[i].EncaixInf:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio - build_ele.dadesTDHortInter.value[nHorInf].Altura/2 + forats[nForat].Posicio - llargadaCavForat/2
        else:
            posHorInf = build_ele.BarresHorList.value[nHorInf].Posicio + build_ele.dadesTDHortInter.value[nHorInf].Altura/2 +1 + forats[nForat].Posicio  - llargadaCavForat/2 #- build_ele.BarraAlturaInf.value/2# + build_ele.BarraAlturaSup.value/2 + 1.25
        if build_ele.dadesTDVertTD.value[i].BarraInferior != "TD Inferior":
            vectorCav.SetValue(14, posHorInf )#barrainici pos

            vectorCan.SetValue(14, posHorInf + 17)
        else:
            vectorCav.SetValue(14, posHorInf )#barrainici pos

            vectorCan.SetValue(14, posHorInf  + alturaCavForat)


    table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
    table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject2A)])]

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT"),
                        AllplanBaseElements.AttributeString(2103, "CAVITAT"),#Cavitat TFF XPS
                        AllplanBaseElements.AttributeString(1083, "CAVITAT"),#Cavitat TFF XPS
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

    group_elems = []

    #if build_ele.dadesTDVertTD.value[i].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
    if build_ele.MostrarCavitatsRecess.value:
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                    hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                    views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))
    #if build_ele.dadesTDVertTD.value[i].MostrarCavitat and build_ele.MostrarCavitats.value:
    if build_ele.MostrarCavitats.value:
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                    hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                    views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))
    group_elems.append(PythonPart ("TD_CilindreForatXPS", parameter_list = CilindreXPS.get_params_list(),
                                    hash_value = CilindreXPS.hash(), python_file = CilindreXPS.filename(),
                                    views = views_Cilindre, matrix = vectorCan, common_props = common_props_Cilindre, attribute_list = attr_list_Cilindre))
    group_elems.append(PythonPart ("TD_CilindreForatXPS", parameter_list = CilindreXPS2.get_params_list(),
                                    hash_value = CilindreXPS2.hash(), python_file = CilindreXPS2.filename(),
                                    views = views_Cilindre2, matrix = vectorCan, common_props = common_props_Cilindre2, attribute_list = attr_list_Cilindre))

    return group_elems
    return []

def createBoxForatVertInt(build_ele, i, forats,nForats):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDVertInter.value[i].BarraAmple, build_ele.dadesTDVertInter.value[i].BarraAltura, build_ele.BarraLlargadaVert.value, build_ele.BarraGruixVert.value,
                                    False, 23, 40052, forats, False, nForats)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]


    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),
                            AllplanBaseElements.AttributeString(1083, "TFF"),
                             AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),
                            AllplanBaseElements.AttributeString(2445, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(1084, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(220, "100")]

    vectorCan = AllplanGeo.Matrix3D()
    vectorCan.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs - (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) )
    vectorCan.SetValue(13, build_ele.dadesTDVertInter.value[i].desplYAbs)
    vectorCan.SetValue(14, 0)

    if not build_ele.BarresVertList.value[i].EncaixInf:
        vectorCan.SetValue(14, build_ele.BarraAlturaInf.value )

    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, common_props = common_props_nBoxForat, attribute_list = attr_list_nBoxForat)


def createBoxForatHorInt(build_ele, posBarraHor, forats, i, nForats):

    nBoxForat = BoxForat(random.random() * 3600, build_ele.dadesTDHortInter.value[posBarraHor].Ample, build_ele.dadesTDHortInter.value[posBarraHor].Altura, build_ele.BarraLlargadaVert.value, 1.5,
                                    False, 23, 40052, forats, True, nForats)

    if not nBoxForat.is_valid():
        return[]
    nBoxForat_Brep = nBoxForat.create()
    common_props_nBoxForat = nBoxForat.get_common_props()

    views_nBoxForat = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_nBoxForat, nBoxForat.create())])]

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(nBoxForat.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(nBoxForat.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(nBoxForat.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(nBoxForat.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(nBoxForat.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(nBoxForat.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(nBoxForat.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(nBoxForat.get_codi_cara_d_inv()) )

    attr_list_nBoxForat = [AllplanBaseElements.AttributeString(2103, "FORAT"),

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

                            AllplanBaseElements.AttributeString(2446, nBoxForat.get_codi_pota_inv()),

                            AllplanBaseElements.AttributeString(2430, nBoxForat.get_codi_pestanyes()),
                            AllplanBaseElements.AttributeString(2435, nBoxForat.get_codi_cancam()),
                            AllplanBaseElements.AttributeString(2431, nBoxForat.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2433, nBoxForat.get_codi_pota()),
                            AllplanBaseElements.AttributeString(2445, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(1084, nBoxForat.get_seccio()),
                            AllplanBaseElements.AttributeString(220, nBoxForat.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, nBoxForat.get_llargada()),
                            AllplanBaseElements.AttributeString(1083, "TFF"),
                             AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),
                            AllplanBaseElements.AttributeString(220, "100")]

    vectorCan = AllplanGeo.Matrix3D()
    #vectorCan.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs + (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) + build_ele.ForatsHorInt.value[posBarraHor].Posicio)
    vectorCan.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.listDesplVerticalsTD.value[i].desplXAbs + build_ele.dadesTDVertTD.value[i].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.dadesTDVertTD.value[i].Gruix + 2 )#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)
    #vectorCan.SetValue(13, build_ele.dadesTDVertTD.value[i].desplYAbs)
    vectorCan.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY)
    if not build_ele.EncaixHorInf.value:
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2)
    else:
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2 - 30/2)#+ build_ele.BarraAlturaInf.value/2 - build_ele.dadesTDHortInter.value[posBarraHor].Altura)

        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (30/2 + build_ele.dadesTDHortInter.value[posBarraHor].Altura)/2 +7.5 )


    return PythonPart ("PP_BoxForat", parameter_list = nBoxForat.get_params_list(),
                                    hash_value = nBoxForat.hash(), python_file = nBoxForat.filename(),
                                    views = views_nBoxForat, matrix = vectorCan, common_props = common_props_nBoxForat, attribute_list = attr_list_nBoxForat)


def createBoxForatCavitatHorInt(build_ele, posBarraHor, forats, i, nForat):

    common_propsObject = AllplanBaseElements.CommonProperties()
    #common_propsObject.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Layer = 40067#(KN_ESPONJA)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 31 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    ampleCavForat = 50
    alturaCavForat = 20
    llargadaCavForat = 120

    if forats[nForat].orientacio == "Esq" or forats[nForat].orientacio == "Dre":
        colorCavitat = getColorCavitat(alturaCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat
    else:
        colorCavitat = getColorCavitat(ampleCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat


    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()


    vectorCav = AllplanGeo.Matrix3D()
    #vectorCav.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs + (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) + build_ele.ForatsHorInt.value[posBarraHor].Posicio)
    vectorCav.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.listDesplVerticalsTD.value[i].desplXAbs + build_ele.dadesTDVertTD.value[i].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.dadesTDVertTD.value[i].Gruix + 2 + forats[nForat].Posicio - llargadaCavForat/2)#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)
    #vectorCav.SetValue(13, build_ele.dadesTDVertTD.value[i].desplYAbs)

    alturaEncaix = 0

    if not build_ele.EncaixHorInf.value:
        alturaEncaix = build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2
    else:
        alturaEncaix = build_ele.BarraAlturaInf.value/2 - build_ele.dadesTDHortInter.value[posBarraHor].Altura


    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(1,0,0))
    if forats[nForat].orientacio == "Inf":
    #    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix - alturaCavForat)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - alturaCavForat - (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2))

    elif forats[nForat].orientacio == "Sup":
    #    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
    #    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs + build_ele.dadesTDVertTD.value[i].BarraAltura)
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix + build_ele.dadesTDHortInter.value[posBarraHor].Altura )
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2))

    elif forats[nForat].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY  )
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )

    elif forats[nForat].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY + build_ele.dadesTDHortInter.value[posBarraHor].Ample + alturaCavForat)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )


    #vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio)



    if build_ele.BarresHorList.value[posBarraHor].BarraHor:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject2A)])]

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT"),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

        group_elems = []

        #if build_ele.BarresHorList.value[posBarraHor].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
        if build_ele.MostrarEsponja.value: #build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                    hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                    views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))

        #if build_ele.BarresHorList.value[posBarraHor].MostrarCavitat and build_ele.MostrarCavitats.value:
        if build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                    hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                    views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))
        return group_elems
    return []


def createBoxForatCavitatHorIntXPS(build_ele, posBarraHor, forats, i, nForat):

    common_propsObject = AllplanBaseElements.CommonProperties()
    common_propsObject.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_propsObject.Color = 3 #blanc

    common_propsObject2 = AllplanBaseElements.CommonProperties()
    common_propsObject2.Layer = 40055#(KN_XPS_CAVITAT)
    common_propsObject2.Color = 31 #blanc

    ampleCavForat = 20
    alturaCavForat = 40
    if build_ele.tipusCavitatTFFHor.value == "60":
        alturaCavForat = 60
    llargadaCavForat = 50

    if forats[nForat].orientacio == "Esq" or forats[nForat].orientacio == "Dre":
        colorCavitat = getColorCavitat(alturaCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat
    else:
        colorCavitat = getColorCavitat(ampleCavForat)
        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat


    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, ampleCavForat, alturaCavForat, llargadaCavForat, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                [])
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()


    colorCavitat = getColorCavitat(20)

    common_props_Cilindre = AllplanBaseElements.CommonProperties()
    #common_props_Cilindre.Layer = 40054#(KN_XPS_RECESS)#56811#build_ele.BarraLayer.value#64178
    common_props_Cilindre.Layer = 40057#(KN_PLD_RECESS)
    common_props_Cilindre.Color = colorCavitat

    common_props_Cilindre2 = AllplanBaseElements.CommonProperties()
    common_props_Cilindre2.Layer = 40055#(KN_XPS_CAVITAT)
    common_props_Cilindre2.Color = colorCavitat

    CilindreXPS = CilindreForatXPS(random.random() * 3600, 1 , 2, 1.5,
                            common_props_Cilindre.Color, common_props_Cilindre.Layer)
    CilindreXPS2 = CilindreForatXPS(random.random() * 3600, 20 , 5, 1.5,
                            common_props_Cilindre2.Color, common_props_Cilindre2.Layer)

    if not CilindreXPS.is_valid():
        return[]
    Cilindre_Brep = CilindreXPS.create()
    Cilindre_Brep2 = CilindreXPS2.create()
    common_props_Cilindre = CilindreXPS.get_common_props()
    common_props_Cilindre2 = CilindreXPS2.get_common_props()

    views_Cilindre = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Cilindre, Cilindre_Brep)])]
    views_Cilindre2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Cilindre2, Cilindre_Brep2)])]

    attr_list_Cilindre = [AllplanBaseElements.AttributeString(2103, "Cilindre Forat XPS "),
                                 AllplanBaseElements.AttributeString(508, "CAVITAT"),
                                 #AllplanBaseElements.AttributeString(508, " ")
                                AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                                AllplanBaseElements.AttributeString(1087, "CAVITAT")]


    vectorCan = AllplanGeo.Matrix3D()

    if forats[nForat].orientacio == "Sup" or forats[nForat].orientacio == "Inf":
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(0,0,0))
    else:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                    point2=  AllplanGeo.Point3D(0,0,1))

    vectorCan.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))


    vectorCav = AllplanGeo.Matrix3D()
    #vectorCav.SetValue(12, build_ele.dadesTDVertInter.value[i].desplXAbs + (build_ele.dadesTDVertInter.value[i].BarraAmple/2 - build_ele.dadesTDVertInter.value[0].BarraAmple/2) + build_ele.ForatsHorInt.value[posBarraHor].Posicio)
    vectorCav.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.listDesplVerticalsTD.value[i].desplXAbs + build_ele.dadesTDVertTD.value[i].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.dadesTDVertTD.value[i].Gruix + 2 + forats[nForat].Posicio - llargadaCavForat/2)#+ build_ele.ForatsHorInt.value[posBarraHor].Posicio)#- build_ele.dadesTDHortInter.value[posBarraHor].desplX)

    if forats[nForat].orientacio == "Sup" or forats[nForat].orientacio == "Inf":
        vectorCan.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.listDesplVerticalsTD.value[i].desplXAbs + build_ele.dadesTDVertTD.value[i].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.dadesTDVertTD.value[i].Gruix + 2 + forats[nForat].Posicio - llargadaCavForat/2 + 15)

    else:
        vectorCan.SetValue(12, build_ele.dadesTDHortInter.value[posBarraHor].desplX + build_ele.listDesplVerticalsTD.value[i].desplXAbs + build_ele.dadesTDVertTD.value[i].BarraAmple/2 + build_ele.dadesTDVertTD.value[0].BarraAmple/2 -build_ele.dadesTDVertTD.value[i].Gruix + 2 + forats[nForat].Posicio - llargadaCavForat/2 + 33)



    #vectorCav.SetValue(13, build_ele.dadesTDVertTD.value[i].desplYAbs)

    alturaEncaix = 0

    if not build_ele.EncaixHorInf.value:
        alturaEncaix = build_ele.BarraAlturaInf.value - build_ele.dadesTDHortInter.value[posBarraHor].Altura/2
    else:
        alturaEncaix = build_ele.BarraAlturaInf.value/2 - build_ele.dadesTDHortInter.value[posBarraHor].Altura


    z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(1,0,0))
    if forats[nForat].orientacio == "Sup":
    #    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix - alturaCavForat )
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - alturaCavForat - (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2))

        vectorCan.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2 + 2)
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix - alturaCavForat )
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - alturaCavForat - (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2) - 20)


    elif forats[nForat].orientacio == "Inf":
    #    vectorCav.SetValue(12, build_ele.listDesplVerticalsTD.value[i].desplXAbs - (build_ele.dadesTDVertTD.value[i].BarraAmple/2 - build_ele.dadesTDVertTD.value[0].BarraAmple/2) - (ampleCavForat - build_ele.dadesTDVertTD.value[i].BarraAmple)/2)
    #    vectorCav.SetValue(13, build_ele.listDesplVerticalsTD.value[i].desplYAbs + build_ele.dadesTDVertTD.value[i].BarraAltura)
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix )#+ build_ele.dadesTDHortInter.value[posBarraHor].Altura )
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2))

        vectorCan.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - (ampleCavForat - build_ele.dadesTDHortInter.value[posBarraHor].Ample)/2 +2)
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + alturaEncaix )#+ build_ele.dadesTDHortInter.value[posBarraHor].Altura )
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio + (build_ele.dadesTDHortInter.value[posBarraHor].Altura/2) + alturaCavForat)

    elif forats[nForat].orientacio == "Esq":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY  )
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )

        vectorCan.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCan.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY - alturaCavForat )
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )

    elif forats[nForat].orientacio == "Dre":
        vectorCav.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCav.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY + build_ele.dadesTDHortInter.value[posBarraHor].Ample + alturaCavForat)
        vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )

        vectorCan.Rotation(z_axis, AllplanGeo.Angle.FromDeg(90))
        vectorCan.SetValue(13, build_ele.dadesTDHortInter.value[posBarraHor].desplY + build_ele.dadesTDHortInter.value[posBarraHor].Ample + alturaCavForat +20 )
        vectorCan.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio - (ampleCavForat/2) )


    #vectorCav.SetValue(14, build_ele.BarresHorList.value[posBarraHor].Posicio)




    table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject2)])]
    table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject2A)])]

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT"),
                        AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                        AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

    group_elems = []



    #if build_ele.BarresHorList.value[posBarraHor].MostrarRecess and build_ele.MostrarCavitatsRecess.value:
    if build_ele.MostrarCavitatsRecess.value:
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                views = table_views_object2, matrix = vectorCav, common_props = common_propsObject, attribute_list = table_attr_listObject))
    #if build_ele.BarresHorList.value[posBarraHor].MostrarCavitat and build_ele.MostrarCavitats.value:
    if build_ele.MostrarCavitats.value:
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                views = table_views_object_2, matrix = vectorCav, common_props = common_propsObject2, attribute_list = table_attr_listObject))

    group_elems.append(PythonPart ("TD_CilindreForatXPS", parameter_list = CilindreXPS.get_params_list(),
                                hash_value = CilindreXPS.hash(), python_file = CilindreXPS.filename(),
                                views = views_Cilindre, matrix = vectorCan, common_props = common_props_Cilindre, attribute_list = attr_list_Cilindre))
    group_elems.append(PythonPart ("TD_CilindreForatXPS", parameter_list = CilindreXPS2.get_params_list(),
                                hash_value = CilindreXPS2.hash(), python_file = CilindreXPS2.filename(),
                                views = views_Cilindre2, matrix = vectorCan, common_props = common_props_Cilindre2, attribute_list = attr_list_Cilindre))

    return group_elems

def set_all_edit_to_false(build_ele):

    #for nbarra in range(0,len(build_ele.BarresHorListToShowTD.value)):
    #    if(build_ele.BarresHorListToShowTD.value[nbarra].Edit):
    #        build_ele.BarresHorListToShowTD.value[nbarra] = build_ele.BarresHorListToShowTD.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresHorList.value)):
        if(build_ele.BarresHorList.value[nbarra].Edit):
            build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresVertListToShow.value)):
        if(build_ele.BarresVertListToShow.value[nbarra].Edit):
            build_ele.BarresVertListToShow.value[nbarra] = build_ele.BarresVertListToShow.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresAdjListToShow.value)):
        if(build_ele.BarresAdjListToShow.value[nbarra].Edit):
            build_ele.BarresAdjListToShow.value[nbarra] = build_ele.BarresAdjListToShow.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresAdjList.value)):
        if(build_ele.BarresAdjList.value[nbarra].Edit):
            build_ele.BarresAdjList.value[nbarra] = build_ele.BarresAdjList.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresFrontListToShow.value)):
        if(build_ele.BarresFrontListToShow.value[nbarra].Edit):
            build_ele.BarresFrontListToShow.value[nbarra] = build_ele.BarresFrontListToShow.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresFrontList.value)):
        if(build_ele.BarresFrontList.value[nbarra].Edit):
            build_ele.BarresFrontList.value[nbarra] = build_ele.BarresFrontList.value[nbarra]._replace(Edit = False)

    for n in range(0,len(build_ele.nListBarresHor.value)):
        inici = build_ele.nListBarresHor.value[n].Posicio
        final = build_ele.nListBarresHor.value[n].Posicio + build_ele.nListBarresHor.value[n].nTotal

        for nbarra in range(inici, final):
            if nbarra< len(build_ele.BarresHorList.value):
                if(build_ele.BarresHorList.value[nbarra].Edit):
                    build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(Edit = False)
                    build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(acabatEditar = False)

    for nbarra in range(0,len(build_ele.dadesTDHortInter.value)):
        if(build_ele.dadesTDHortInter.value[nbarra].estaEditant):
            build_ele.dadesTDHortInter.value[nbarra] = build_ele.dadesTDHortInter.value[nbarra]._replace(estaEditant = False)
            build_ele.dadesTDHortInter.value[nbarra] = build_ele.dadesTDHortInter.value[nbarra]._replace(acabatEditar = False)

    for n in range(0,len(build_ele.nListBarresVert.value)):
        inici = build_ele.nListBarresVert.value[n].Posicio
        final = build_ele.nListBarresVert.value[n].Posicio + build_ele.nListBarresVert.value[n].nTotal

        for nbarra in range(inici, final):
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
    #for nbarra in range(0,len(build_ele.BarresHorListToShowTD.value)):
    #    if(build_ele.BarresHorListToShowTD.value[nbarra].Edit):
    #        isTrue = True
    #        build_ele.BarresHorListToShowTD.value[nbarra] = build_ele.BarresHorListToShowTD.value[nbarra]._replace(Edit = False)

    for nbarra in range(0,len(build_ele.BarresHorList.value)):
        if(build_ele.BarresHorList.value[nbarra].Edit):
            isTrue = True
            build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(Edit = False)


    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresVertListToShow.value)):
            if(build_ele.BarresVertListToShow.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresVertListToShow.value[nbarra] = build_ele.BarresVertListToShow.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresAdjListToShow.value)):
            if(build_ele.BarresAdjListToShow.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresAdjListToShow.value[nbarra] = build_ele.BarresAdjListToShow.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresAdjList.value)):
            if(build_ele.BarresAdjList.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresAdjList.value[nbarra] = build_ele.BarresAdjList.value[nbarra]._replace(Edit = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.BarresFrontListToShow.value)):
            if(build_ele.BarresFrontListToShow.value[nbarra].Edit):
                isTrue = True
                build_ele.BarresFrontListToShow.value[nbarra] = build_ele.BarresFrontListToShow.value[nbarra]._replace(Edit = False)

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
                if nbarra< len(build_ele.BarresHorList.value):
                    if(build_ele.BarresHorList.value[nbarra].Edit):
                        isTrue = True
                        build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(Edit = False)
                        build_ele.BarresHorList.value[nbarra] = build_ele.BarresHorList.value[nbarra]._replace(acabatEditar = False)

    if not isTrue:
        for nbarra in range(0,len(build_ele.dadesTDHortInter.value)):
            if(build_ele.dadesTDHortInter.value[nbarra].estaEditant):
                isTrue = True
                build_ele.dadesTDHortInter.value[nbarra] = build_ele.dadesTDHortInter.value[nbarra]._replace(estaEditant = False)
                build_ele.dadesTDHortInter.value[nbarra] = build_ele.dadesTDHortInter.value[nbarra]._replace(acabatEditar = False)

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
        inicialitzar_valors_inici(build_ele, build_ele.IntegerTDSelector.value)
    else:
        #if (build_ele.SelectorTDVAnt.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPTD.value)):
        if build_ele.IntegerTDSelectorAnterior.value != nVer or (build_ele.SelectorPPAnt.value != build_ele.SelectorPPTD.value):
            if not check_all_edit_true(build_ele):
                guardar_valors_actuals(build_ele, build_ele.IntegerTDSelectorAnterior.value)
            build_ele.IntegerTDSelectorAnterior.value = nVer
            mostrar_valors_actuals(build_ele, nVer)

        else: #build_ele.IntegerTDSelectorAnterior.value == nVer:
            guardar = True
            for i in range(0,len(build_ele.BarresHorList.value)):
                BarresHor = build_ele.BarresHorList.value[i]
                #if (not BarresHor.Edit and BarresHor.acabatEditar) or (not BarresVert.Edit or BarresVert.acabatEditar):
                if BarresHor.Edit or BarresHor.acabatEditar:
                    guardar = False

            if build_ele.SelectorPPTD == 1:
                for i in range(0,len(build_ele.BarresHorListToShowTD.value)):
                    BarresHor = build_ele.BarresHorListToShowTD.value[i]
                    #if (not BarresHor.Edit and BarresHor.acabatEditar) or (not BarresVert.Edit or BarresVert.acabatEditar):
                    if BarresHor.Edit or BarresHor.acabatEditar:
                        guardar = False

            '''
            for i in range(0,len(build_ele.BarresVertListToShow.value)):
                BarresVert = build_ele.BarresVertListToShow.value[i]
                #if (not BarresHor.Edit and BarresHor.acabatEditar) or (not BarresVert.Edit or BarresVert.acabatEditar):
                if BarresVert.Edit or BarresVert.acabatEditar:
                    guardar = False
            '''
            if guardar:
                guardar_valors_actuals(build_ele, nVer)
                mostrar_valors_actuals(build_ele, nVer)

def crear_barres_inferiors_multiples(build_ele, doc, nBarraInf, mostrarActual, placement_mat):

    group_elems = []
    model_ele_list = []
    model_ele_list2 = []
    placement_matrix = []

    #if build_ele.nBarresTDHoritzontalInf.value != len(build_ele.listDesplHoritzontalsInf.value):
    if nBarraInf >= len(build_ele.listDesplHoritzontalsInf.value):
        #add_baraInferior(build_ele, len(build_ele.listDesplHoritzontalsInf.value))
        add_baraInferior(build_ele, nBarraInf)
    else:
        while len(build_ele.listDesplHoritzontalsInf.value) > build_ele.nBarresTDHoritzontalInf.value:
            build_ele.listDesplHoritzontalsInf.value.pop()
    llargadaInf = build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value
    desplXSeparat = build_ele.desplXI.value
    desplYSeparat = 0
    if build_ele.SepararTDHoritzontalInf.value:
        #build_ele.BarraLlargadaTD.value = build_ele.listDesplHoritzontalsInf.value[0].BarraLlargadaInf
        desplXSeparat = build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX

    #if nBarraInf>= len(build_ele.listDesplHoritzontalsInf.value):

    if build_ele.SelectorTDHInf.value == "Tub":
        horitzontalPP = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColorInf.value, 40001,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParINF.value, build_ele.PotaParINF.value, build_ele.ForatsParINF.value, #ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaINF.value, build_ele.Altura_forat_femellaINF.value, build_ele.Separacio_forat_femellaINF.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesINF.value + build_ele.FemellesHorIntAuxInf.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesINF.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamINF.value, build_ele.Dis1cancamINF.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamINF.value, build_ele.Dis2cancamINF.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParINF.value, build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf) #EncaixosPar)
    else:
        horitzontalPP = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value, llargadaInf, build_ele.BarraGruixInf.value, build_ele.InvertirTDHoritzontalInf.value, build_ele.InvertirTDHoritzontalInf2.value,
                    [],
                    build_ele.IsUseGlobalProp.value, build_ele.FounColorInf.value, 40001,
                    retallInici=desplXSeparat)

    if not horitzontalPP.is_valid():
        return[]

    build_ele.DENInf.value = "T "

    #definir atributs de la Barra Horitzontal Inferior
    horitzontal_Brep = horitzontalPP.create()
    common_propsInf = horitzontalPP.get_common_props()
    tubEsIgual = False
    if build_ele.comprovarDEN.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPP)
    if (tubEsIgual):
        build_ele.DENInf.value = DEN
    if  mostrarActual == "TDHINF":
        common_propsInf.Color = 6#Vermell
    seccio = ""
    if build_ele.BarraAmpleInf.value > build_ele.BarraAlturaInf.value:
        seccio = str(build_ele.BarraAmpleInf.value) + "x " + str(build_ele.BarraAlturaInf.value) +"x " + str(build_ele.BarraGruixInf.value)
    else:
        seccio = str(build_ele.BarraAlturaInf.value) + "x " + str(build_ele.BarraAmpleInf.value) + "x " + str(build_ele.BarraGruixInf.value)

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP.get_codi_cara_d_inv()) )

    table_attr_list = [ AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                        AllplanBaseElements.AttributeString(2446, horitzontalPP.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2430, horitzontalPP.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPP.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2431, horitzontalPP.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPP.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2445, seccio),
                        AllplanBaseElements.AttributeString(220, str(build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf)),
                        AllplanBaseElements.AttributeString(2455, str(build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf)),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENInf.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPP.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, str(build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf)),
                        AllplanBaseElements.AttributeString(1087, "Baix"),
                        AllplanBaseElements.AttributeString(508, "TD")]
    table_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsInf, horitzontal_Brep)])]
    if not build_ele.SepararTDHoritzontalInf.value:
        handle_list = horitzontalPP.create_handles()
    else:
        handle_list = None



    #-------------------------------
    matrixPosX = []
    matrixPosY = []
    matrixcentrar = []
    matrixOffsetY = []
    matrixOr = []

    matrixMostrar = []
    matrixMostrarInf = []
    matrixMostrarSup = []
    for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
        matrixcentrar.append(build_ele.dadesTDVertTD.value[i].BarraAmple/2)
        matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
        matrixPosY.append(build_ele.listDesplVerticalsTD.value[i].desplY)
        matrixMostrar.append(build_ele.dadesTDVertTD.value[i].MostrarTDVertical)
        matrixMostrarInf.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaInferiorVert and build_ele.dadesTDVertTD.value[i].FemellaInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorInf.value and not build_ele.dadesTDVertTD.value[i].EncaixInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaInf))and build_ele.dadesTDVertTD.value[i].BarraInferior == "TD Inferior")
        matrixMostrarSup.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaSuperiorVert and build_ele.dadesTDVertTD.value[i].FemellaSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorSup.value and not build_ele.dadesTDVertTD.value[i].EncaixSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaSup))and build_ele.dadesTDVertTD.value[i].BarraSuperior == "TD Superior")
    listAmples = []
    listAmples2 = []
    listAltures = []
    for TDVert in build_ele.dadesTDVertTD.value:
        listAmples.append(TDVert.BarraAmple - TDVert.Gruix*2)
        listAmples2.append(TDVert.BarraAmple)
        listAltures.append(TDVert.BarraAltura)
    #Crear Encaixos i Femelles en les Barres Horitzontals
    offsetXI = build_ele.desplXI.value
    offsetXS = build_ele.desplXS.value
    #if (build_ele.desplYI.value != 0.0 and build_ele.desplYI.value > 0.0) or (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):


    if (build_ele.EncaixHorInf.value and build_ele.desplYI.value > 0.0):

        if build_ele.invertirEncaixInf.value:
            horitzontalPP.set_false_encaix()
            matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                if build_ele.dadesTDVertTD.value[i].EncaixInf:
                    matrixOr.append("Esq")
                else:
                    matrixOr.append("Inf")
            trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#
        else:
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixOffsetY.append(  build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.dadesTDVertTD.value[i].BarraAltura - build_ele.desplYI.value)
            trans_list = horitzontalPP.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXI, 'Sup', build_ele.BarraLlargadaTD.value)
            horitzontalPP.set_false_femelles()
    elif (build_ele.EncaixHorInf.value and build_ele.desplYI.value <= 0.0):
        if build_ele.invertirEncaixInf.value:
            horitzontalPP.set_false_encaix()
            matrixPosX = []
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                if build_ele.dadesTDVertTD.value[i].EncaixInf:
                    matrixOr.append("Esq")
                else:
                    matrixOr.append("Sup")
            trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#
        else:
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixOffsetY.append( build_ele.BarraAmpleInf.value - build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.desplYI.value)#build_ele.dadesTDVertTD.value[i].BarraAltura

            trans_list = horitzontalPP.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXI, 'Inf', build_ele.BarraLlargadaTD.value )
            horitzontalPP.set_false_femelles()
    else:
        horitzontalPP.set_false_encaix()

        matrixPosX = []
        for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
            matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs )
            matrixOr.append("Esq")
        trans_list = horitzontalPP.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarInf, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, build_ele.BarraLlargadaTD.value, build_ele.desplYI.value, build_ele.FemellesHorIntAuxInf.value, build_ele.desplXI.value)#

    #-------------------------------------------------

    vectorH1 = AllplanGeo.Matrix3D()
    vectorH1.SetValue(12, build_ele.desplXI.value)
    vectorH1.SetValue(13, build_ele.desplYI.value)

    TranslationFather = vectorH1
    TranslationFather.SetValue(12, placement_mat[12] + vectorH1[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH1[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH1[14])
    vectorH1  = TranslationFather

    if build_ele.MostrarTDHoritzontalInf.value:
        #horitzontalPP with translate has to be the firsrt element because of group modification
        # Define python part for TDHoritzontal


        group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP.get_params_list(),
                                    hash_value = horitzontalPP.hash(), python_file = horitzontalPP.filename(),
                                    views = table_views, matrix = vectorH1, common_props = common_propsInf, attribute_list = table_attr_list))


        #--------
        common_propsObject = AllplanBaseElements.CommonProperties()
        #common_propsObject.Layer = 56811#build_ele.BarraLayer.value#64178
        common_propsObject.Layer = 40054#build_ele.BarraLayer.value#64178
        common_propsObject.Color = 31 #blanc

        common_propsObject2 = AllplanBaseElements.CommonProperties()
        #common_propsObject.Layer = 56811#build_ele.BarraLayer.value#64178
        common_propsObject2.Layer = 40055#build_ele.BarraLayer.value#64178
        common_propsObject2.Color = 31 #blanc

        colorCavitat = getColorCavitat( build_ele.BarraAmpleInf.value)

        common_propsObject.Color = colorCavitat
        common_propsObject2.Color = colorCavitat

        horitzontalPPOBject = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, build_ele.BarraLlargadaTD.value+10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    False, common_propsObject.Color, common_propsObject.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    [], [], [],#ColisPar, PotaPar, #matrius
                                    0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                    [], #Femelles, #matriu
                                    0, #posicio_centre_masses,
                                    False, 0, #IsFirstCancam, Dis1cancam,
                                    False, 0, #IsSecondCancam, Dis2cancam,
                                    build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                    [], build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf) #EncaixosPar))
        horitzontalPPOBjectA = PP_TD_Horitzontal(random.random() * 3600,0, build_ele.BarraAmpleInf.value, build_ele.BarraAlturaInf.value+10, build_ele.BarraLlargadaTD.value + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                    False, common_propsObject2.Color, common_propsObject2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                    [], [], [],#ColisPar, PotaPar, #matrius
                                    0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                    [], #Femelles, #matriu
                                    0, #posicio_centre_masses,
                                    False, 0, #IsFirstCancam, Dis1cancam,
                                    False, 0, #IsSecondCancam, Dis2cancam,
                                    build_ele.PestanyaSuperiorINF.value, build_ele.PestanyaInferiorINF.value,#PestanyaSuperior, PestanyaInferior,
                                    [], build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX, build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf) #EncaixosPar))

        table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                                 #AllplanBaseElements.AttributeString(508, " "),
                                AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                                AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                                AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)]

        horitzontal_BrepObject = horitzontalPPOBject.create()
        horitzontal_BrepObjectA = horitzontalPPOBjectA.create()

        vectorH1CA = AllplanGeo.Matrix3D()
        vectorH1CA.SetValue(12, vectorH1[12] - 5)
        vectorH1CA.SetValue(13, vectorH1[13])
        vectorH1CA.SetValue(14, 0 - 5)

        table_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject, horitzontal_BrepObject)])]
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObject2, horitzontal_BrepObject)])]
        #-----------


        if build_ele.MostrarRecessInf.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
                                    hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
                                    views = table_views_object, matrix = vectorH1CA, common_props = common_propsObject, attribute_list = table_attr_listObject))
        if build_ele.MostrarCavitatInf.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBjectA.get_params_list(),
                                    hash_value = horitzontalPPOBjectA.hash(), python_file = horitzontalPPOBjectA.filename(),
                                    views = table_views_object2, matrix = vectorH1CA, common_props = common_propsObject2, attribute_list = table_attr_listObject))
        '''
        group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject.get_params_list(),
                                    hash_value = horitzontalPPOBject.hash(), python_file = horitzontalPPOBject.filename(),
                                    views = table_views_object, matrix = vectorH1C, attribute_list = table_attr_listObject))
        '''

        for i in range(0, len(build_ele.ColisParINF.value)):
            if build_ele.ColisParINF.value[i].Colis and build_ele.ColisParINF.value[i].MostrarBox and build_ele.ColisParINF.value[i].Posicio < build_ele.BarraLlargadaTD.value + build_ele.ExtenderInf.value:
                boxsColis = createColisInf(build_ele,0, i)
                if boxsColis != []:
                    group_elems.append(boxsColis)
                    boxCavi = createColisCavitatHorInf(build_ele, 0, i)
                    #if boxCavi != []:
                    #    group_elems.append(boxCavi)



        if build_ele.SepararTDHoritzontalInf.value:
            if build_ele.listDesplHoritzontalsInf.value[nBarraInf].mostrarLiniaA:
                punt_central = vectorH1[12] + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX + build_ele.BarraAlturaInf.value/2
                pointUbi = AllplanGeo.Point3D(vectorH1[12] + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX, vectorH1[13] + build_ele.BarraAmpleInf.value/2 + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplLinA, vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                layer = build_ele.SelectorLayerInf.value[len(build_ele.SelectorLayerInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.BarraAmpleInf.value,build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf, True, pointUbi, int(linia), layer)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
            if build_ele.listDesplHoritzontalsInf.value[nBarraInf].mostrarLiniaB:
                punt_central = vectorH1[12] + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX + build_ele.BarraAlturaInf.value/2
                pointUbi = AllplanGeo.Point3D(vectorH1[12] + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplX, vectorH1[13] + build_ele.BarraAmpleInf.value/2 + build_ele.listDesplHoritzontalsInf.value[nBarraInf].desplLinB, vectorH1[14] +  build_ele.BarraAlturaInf.value/2)
                linia = build_ele.SelectorLiniaInf.value[len(build_ele.SelectorLiniaInf.value)-1]
                layer = build_ele.SelectorLayerInf.value[len(build_ele.SelectorLayerInf.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.BarraAmpleInf.value,build_ele.listDesplHoritzontalsInf.value[nBarraInf].BarraLlargadaInf, True, pointUbi, int(linia), layer)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
            #crear_barres_inferiors_multiples
            return group_elems, horitzontalPP, model_ele_list2
    return [], [], []



def crear_barres_superiors_multiples(build_ele, doc, nBarraSup, mostrarActual, placement_mat):

    group_elems = []
    group_elems_preview = []
    model_ele_list = []
    model_ele_list2 = []
    placement_matrix = []

    #if build_ele.nBarresTDHoritzontalInf.value != len(build_ele.listDesplHoritzontalsInf.value):
    if nBarraSup >= len(build_ele.listDesplHoritzontalsSup.value):
        #add_baraInferior(build_ele, len(build_ele.listDesplHoritzontalsInf.value))
        add_baraSuperior(build_ele, nBarraSup)
    else:
        while len(build_ele.listDesplHoritzontalsSup.value) > build_ele.nBarresTDHoritzontalSup.value:
            build_ele.listDesplHoritzontalsSup.value.pop()


    largadaSup = build_ele.BarraLlargadaTD.value
    if not build_ele.mantenirLlargadaSup.value:
        llargadaSup = build_ele.BarraLlargadaSupInd.value

    desplXSeparatSup = 0#build_ele.desplXS.value
    desplYSeparatSup = 0#build_ele.desplYS.value
    if build_ele.SepararTDHoritzontalSup.value:
        desplXSeparatSup = build_ele.listDesplHoritzontalsSup.value[nBarraSup].desplX
        llargadaSup = build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraLlargadaSup + desplXSeparatSup
        desplYSeparatSup = build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraLlargadaSup

    #------------------ Definir valors Barra Superior
    if build_ele.SelectorTDHSup.value == "Tub":
        horitzontalPP2 = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruixSup.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value, desplXSeparatSup, desplYSeparatSup ) #EncaixosPar)
    elif build_ele.SelectorTDHSup.value == "L":
        #femellesSupL = []
        if build_ele.MostrarFemellesSup.value:
            femellesSupL = build_ele.FemellesSUP.value
        horitzontalPP2 = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, build_ele.BarraGruixSupL.value, build_ele.InvertirTDHoritzontalSup.value, build_ele.InvertirTDHoritzontalSup2.value,
                    build_ele.ForatsParSUPL.value,
                    build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, 40001,
                    femellesSupL,
                    build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,
                    retallInici = desplXSeparatSup)#, llargBarraAmbRetallFinal = desplYSeparatSup)
    else:
        horitzontalPP2 = PP_TD_Horitzontal(random.random() * 3600,build_ele.DistanciaEntreTD.value, build_ele.BarraAmpleSup.value, build_ele.BarraAlturaSup.value, llargadaSup, build_ele.BarraGruixSup.value,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, build_ele.BarraLayer.value,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                build_ele.ColisParSUP.value, build_ele.PotaParSUP.value, build_ele.ForatsParSUP.value,#ColisPar, PotaPar, #matrius
                                build_ele.Ample_forat_femellaSUP.value, build_ele.Altura_forat_femellaSUP.value, build_ele.Separacio_forat_femellaSUP.value,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                build_ele.FemellesSUP.value, #Femelles, #matriu
                                build_ele.posicio_centre_massesSUP.value, #posicio_centre_masses,
                                build_ele.IsFirstCancamSUP.value, build_ele.Dis1cancamSUP.value, #IsFirstCancam, Dis1cancam,
                                build_ele.IsSecondCancamSUP.value, build_ele.Dis2cancamSUP.value, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                build_ele.EncaixosParSUP.value, desplXSeparatSup, desplYSeparatSup) #EncaixosPar)
        horitzontalPP2L = PP_TD_Horitzontal_Inf( random.random() * 3600, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, build_ele.BarraGruixSupL.value, build_ele.InvertirTDHoritzontalSup.value, build_ele.InvertirTDHoritzontalSup2.value,
                    build_ele.ForatsParSUPL.value,
                    build_ele.IsUseGlobalProp.value, build_ele.FounColorSup.value, 40001,
                    retallInici = desplXSeparatSup)#, llargBarraAmbRetallFinal = desplYSeparatSup)

    if not horitzontalPP2.is_valid():
        return[]


    build_ele.DENSup.value = "T "
    #definir atributs de la Barra Horitzontal Superior
    horitzontal_Brep2 = horitzontalPP2.create()
    common_propsSup = horitzontalPP2.get_common_props()
    #horitzontal_Brep2Prev = horitzontalPP2Prev.create()
    common_propsSupPrev = horitzontalPP2.get_common_props()
    tubEsIgual = False
    if build_ele.comprovarDEN.value:
        tubEsIgual, DEN = compare_attributes(build_ele, doc, horitzontalPP2)
    if build_ele.VermellSup.value:
        common_propsSup.Color = 6#Vermell
    if (tubEsIgual):
        build_ele.DENSup.value = DEN
    if  mostrarActual == "TDHSUP":
        common_propsSupPrev.Color = 4 #Verd
        #handle_list = horitzontalPP2.create_handles()

    cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_a()) )
    cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_b()) )
    cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_c()) )
    cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_d()) )

    cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_a_inv()) )
    cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_b_inv()) )
    cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_c_inv()) )
    cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP2.get_codi_cara_d_inv()) )



    table_attr_list2 = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                        AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                        AllplanBaseElements.AttributeString(2446, horitzontalPP2.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2430, horitzontalPP2.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, horitzontalPP2.get_codi_cancam()),
                        AllplanBaseElements.AttributeString(2431, horitzontalPP2.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2433, horitzontalPP2.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2445, horitzontalPP2.get_seccio()),
                        AllplanBaseElements.AttributeString(220,  str(llargadaSup - desplXSeparatSup)),#horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(2455, str(llargadaSup - desplXSeparatSup)),#horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                        AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                        AllplanBaseElements.AttributeString(1084, horitzontalPP2.get_seccio()),#horitzontalPP2.get_seccio()),
                        AllplanBaseElements.AttributeString(1085, str(llargadaSup - desplXSeparatSup)),#horitzontalPP2.get_llargada()),
                        AllplanBaseElements.AttributeString(1087, "Dalt"),
                        AllplanBaseElements.AttributeString(508, "TD")]
    table_views2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2)])]
    table_views2Prev = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsSupPrev, horitzontal_Brep2)])]

    if build_ele.SelectorTDHSup.value == "Tub + L":
        horitzontal_Brep2L = horitzontalPP2L.create()
        common_propsL = horitzontalPP2L.get_common_props()
        tubEsIgual2 = False
        if build_ele.comprovarDEN.value:
            tubEsIgual2, DEN = compare_attributes(build_ele, doc, horitzontalPP2L)
        if (tubEsIgual2):
            build_ele.DENSup.value = DEN
        #if  mostrarActual == "TDHSUP":
        if build_ele.VermellSup.value:
            common_propsL.Color = 6 #RED

        cara_a, cara_a1, cara_a2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_a()) )
        cara_b, cara_b1, cara_b2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_b()) )
        cara_c, cara_c1, cara_c2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_c()) )
        cara_d, cara_d1, cara_d2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_d()) )

        cara_e, cara_e1, cara_e2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_a_inv()) )
        cara_f, cara_f1, cara_f2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_b_inv()) )
        cara_g, cara_g1, cara_g2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_c_inv()) )
        cara_h, cara_h1, cara_h2 = dividirAtribut(str(horitzontalPP2L.get_codi_cara_d_inv()) )



        table_attr_list2L = [AllplanBaseElements.AttributeString(684, "IfcBuildingElementProxy"),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value),

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

                            AllplanBaseElements.AttributeString(2446, horitzontalPP2L.get_codi_pota_inv()),

                            AllplanBaseElements.AttributeString(2430, horitzontalPP2L.get_codi_pestanyes()),
                            AllplanBaseElements.AttributeString(2435, horitzontalPP2L.get_codi_cancam()),
                            AllplanBaseElements.AttributeString(2431, horitzontalPP2L.get_codi_mesures()),
                            AllplanBaseElements.AttributeString(2433, horitzontalPP2L.get_codi_pota()),
                            AllplanBaseElements.AttributeString(2445, horitzontalPP2L.get_seccio()),
                            AllplanBaseElements.AttributeString(220,  str(llargadaSup - desplXSeparatSup)),# = buhoritzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(2455, str(llargadaSup - desplXSeparatSup)), #horitzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(2103, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1083, build_ele.DENSup.value),
                            AllplanBaseElements.AttributeString(1084, horitzontalPP2L.get_seccio()),
                            AllplanBaseElements.AttributeString(1085, str(llargadaSup - desplXSeparatSup)),#horitzontalPP2L.get_llargada()),
                            AllplanBaseElements.AttributeString(1087, "Dalt"),
                            AllplanBaseElements.AttributeString(508, "TD")]
        table_views2L = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsL, horitzontal_Brep2L)])]

    matrixPosX = []
    matrixPosY = []
    matrixcentrar = []
    matrixOffsetY = []
    matrixOr = []

    matrixMostrar = []
    matrixMostrarInf = []
    matrixMostrarSup = []


    if not build_ele.ReduirTempsCarrega.value:
        for i in range(0,build_ele.IntegerTDSelector.value):
            matrixcentrar.append(build_ele.dadesTDVertTD.value[i].BarraAmple/2)
            matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs )
            matrixPosY.append(build_ele.listDesplVerticalsTD.value[i].desplY)
            matrixMostrar.append(build_ele.dadesTDVertTD.value[i].MostrarTDVertical)
            matrixMostrarInf.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaInferiorVert and build_ele.dadesTDVertTD.value[i].FemellaInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorInf.value and not build_ele.dadesTDVertTD.value[i].EncaixInf) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaInf))and build_ele.dadesTDVertTD.value[i].BarraInferior == "TD Inferior")
            matrixMostrarSup.append(((build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].PestanyaSuperiorVert and build_ele.dadesTDVertTD.value[i].FemellaSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.EncaixHorSup.value and not build_ele.dadesTDVertTD.value[i].EncaixSup) or (build_ele.dadesTDVertTD.value[i].MostrarTDVertical and build_ele.dadesTDVertTD.value[i].FemellaSup))and build_ele.dadesTDVertTD.value[i].BarraSuperior == "TD Superior")
        listAmples = []
        listAmples2 = []
        listAltures = []
        for TDVert in build_ele.dadesTDVertTD.value:
            listAmples.append(TDVert.BarraAmple - TDVert.Gruix*2)
            listAmples2.append(TDVert.BarraAmple)
            listAltures.append(TDVert.BarraAltura)
        #Crear Encaixos i Femelles en les Barres Horitzontals
        offsetXI = build_ele.desplXI.value
        offsetXS = build_ele.desplXS.value
        if build_ele.SelectorTDHSup.value == "L":
            offsetXS = build_ele.desplXSL.value

        matrixOffsetY = []
        matrixOr = []
        desplYS = build_ele.desplYS.value
        desplXS = build_ele.desplXS.value
        if build_ele.SelectorTDHSup.value == "L":
            desplYS = build_ele.desplYSL.value
            desplXS = build_ele.desplXSL.value

        if build_ele.EncaixHorSup.value and desplYS > 0.0:
            if build_ele.invertirEncaixSup.value:
                horitzontalPP2.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    #matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    if build_ele.dadesTDVertTD.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Inf")
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, llargadaSup, desplYS,[], desplXS)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append(  build_ele.listDesplVerticalsTD.value[i].desplY + build_ele.dadesTDVertTD.value[i].BarraAltura - desplYS)#build_ele.dadesTDVertTD.value[i].BarraAltura
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, matrixOffsetY, offsetXS, 'Sup', llargadaSup)
                horitzontalPP2.set_false_femelles()
        elif build_ele.EncaixHorSup.value and desplYS <= 0.0:
            if build_ele.invertirEncaixSup.value:
                horitzontalPP2.set_false_encaix()
                #matrixPosX = []
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixPosX.append(build_ele.listDesplVerticalsTD.value[i].desplXAbs)
                    #matrixPosX.append(build_ele.desplXS.value + build_ele.BarraAmpleSup.value - build_ele.listDesplVerticalsTD.value[i].desplX + build_ele.dadesTDVertTD.value[i].BarraAmple)
                    if build_ele.dadesTDVertTD.value[i].EncaixSup:
                        matrixOr.append("Dre")
                    else:
                        matrixOr.append("Sup")
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXI, matrixOr, build_ele.Ample_forat_femellaVert.value, llargadaSup, desplYS,[], desplXS)
            else:
                for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                    matrixOffsetY.append(build_ele.BarraAmpleSup.value + desplYS + build_ele.listDesplVerticalsTD.value[i].desplY )
                if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_encaix(listAmples2, matrixPosX, matrixPosY, matrixcentrar,  matrixMostrar, matrixOffsetY, offsetXS, 'Inf', llargadaSup)
                horitzontalPP2.set_false_femelles()
        else:
            horitzontalPP2.set_false_encaix()
            for i in range(0,len(build_ele.listDesplVerticalsTD.value)):
                matrixOr.append("Dre")
            if (build_ele.MostrarFemellesSup.value and build_ele.SelectorTDHSup.value == "L") or build_ele.SelectorTDHSup.value != "L":
                    trans_listSup = horitzontalPP2.create_PP_positions_femelles(listAmples, listAltures, matrixPosX, matrixPosY, matrixMostrarSup, offsetXS, matrixOr, build_ele.Ample_forat_femellaVert.value,llargadaSup, desplYS,[], desplXS)


    #Posicionar Barra Superior
    vectorH2 = AllplanGeo.Matrix3D()
    vectorH2.SetValue(12, build_ele.desplXS.value)
    vectorH2.SetValue(13, build_ele.desplYS.value)
    if build_ele.SelectorTDHSup.value == "L":
        vectorH2.SetValue(12, build_ele.desplXSL.value)
        vectorH2.SetValue(13, build_ele.desplYSL.value)

    llargadaVertical = build_ele.BarraLlargadaVert.value


    #if build_ele.desplYI.value == 0.0 or build_ele.EncaixHorInf.value:
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

    vectorH2.SetValue(14, llargadaVertical + 1 )

    TranslationFather = vectorH2
    TranslationFather.SetValue(12, placement_mat[12] + vectorH2[12])
    TranslationFather.SetValue(13, placement_mat[13] + vectorH2[13])
    TranslationFather.SetValue(14, placement_mat[14] + vectorH2[14])
    vectorH2  = TranslationFather


    common_propsObjectSup = AllplanBaseElements.CommonProperties()
    common_propsObjectSup2 = AllplanBaseElements.CommonProperties()
    common_propsObjectSup.Layer = 40054#(KN_XPS_RECESS)
    common_propsObjectSup2.Layer = 40055#(KN_XPS_CAVITAT)
    ampleSupCavitat = build_ele.BarraAmpleSup.value
    alturaSupCavitat = build_ele.BarraAlturaSup.value
    if build_ele.SelectorTDHSup.value == "L":
        ampleSupCavitat = build_ele.BarraAmpleSupL.value
        alturaSupCavitat = build_ele.BarraAlturaSupL.value

    colorCavitat = getColorCavitat(ampleSupCavitat)
    common_propsObjectSup.Color = colorCavitat
    common_propsObjectSup2.Color = colorCavitat
    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ampleSupCavitat, alturaSupCavitat+10, llargadaSup + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup.Color, common_propsObjectSup.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparatSup)
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, ampleSupCavitat, alturaSupCavitat+10, llargadaSup + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup2.Color, common_propsObjectSup2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparatSup)
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                            #AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)
                            ]

    vectorH2C = AllplanGeo.Matrix3D()
    vectorH2C.SetValue(12, vectorH2[12]-5)
    vectorH2C.SetValue(13, vectorH2[13])
    vectorH2C.SetValue(14, vectorH2[14]-5)


    if build_ele.MostrarTDHoritzontalSup.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A)])]

        if build_ele.MostrarRecessSup.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))

        if build_ele.MostrarCavitatSup.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A))


        #Afegir Barra Horitzontal al group_elems
        group_elems.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP2.get_params_list(),
                                    hash_value = horitzontalPP2.hash(), python_file = horitzontalPP2.filename(),
                                    views = table_views2, matrix = vectorH2, common_props = common_propsSup, attribute_list = table_attr_list2))
        group_elems_preview.append(PythonPart ("PP_TD_Horitzontal", parameter_list = horitzontalPP2.get_params_list(),
                                    hash_value = horitzontalPP2.hash(), python_file = horitzontalPP2.filename(),
                                    views = table_views2Prev, matrix = vectorH2, common_props = common_propsSupPrev, attribute_list = table_attr_list2))
        #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2))
        #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsSup, group_elems[len(group_elems)-1]))
        model_ele_list2.append([AllplanBasisElements.ModelElement3D(common_propsSupPrev, horitzontal_Brep2)])
        #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsSup, horitzontal_Brep2))
        #placement_matrix.append(vectorH2)
        #Afegir Barra Horitzontal al group_elems
        if build_ele.SelectorTDHSup.value == "Tub + L":
            vectorH2L = AllplanGeo.Matrix3D()
            vectorH2L.SetValue(12, build_ele.desplXSL.value)
            vectorH2L.SetValue(13, build_ele.desplYSL.value)
            vectorH2L.SetValue(14, vectorH2[14] + build_ele.BarraAlturaSup.value + 1)
            group_elems.append(PythonPart ("PP_TD_Horitzontal_L", parameter_list = horitzontalPP2L.get_params_list(),
                                        hash_value = horitzontalPP2L.hash(), python_file = horitzontalPP2L.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props = common_propsL, attribute_list = table_attr_list2L))
            group_elems_preview.append(PythonPart ("PP_TD_Horitzontal_L", parameter_list = horitzontalPP2L.get_params_list(),
                                        hash_value = horitzontalPP2L.hash(), python_file = horitzontalPP2L.filename(),
                                        views = table_views2L, matrix = vectorH2L, common_props = common_propsL, attribute_list = table_attr_list2L))

            cav, cav_prev = crear_cavitat_hor(build_ele, build_ele.BarraAmpleSupL.value, build_ele.BarraAlturaSupL.value, llargadaSup, vectorH2L, desplXSeparatSup)
            for e in cav:
                group_elems.append(e)
            for e_prev in cav_prev:
                group_elems_preview.append(e_prev)

        '''
        if  build_ele.IsFirstCancamSUP.value:
            if build_ele.posicio_centre_massesSUP.value  + build_ele.Dis1cancamSUP.value/ 2 < llargadaSup:
                firstCancam = True
                secondCancam = False
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
        if  build_ele.IsSecondCancamSUP.value:
            if build_ele.posicio_centre_massesSUP.value  + build_ele.Dis2cancamSUP.value/ 2 < llargadaSup:
                firstCancam = False
                secondCancam = True
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, True, False)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
                cilindre = createCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if cilindre != []:
                    group_elems.append(cilindre)
                    group_elems_preview.append(cilindre)
                liniaCancam = createPolylineCancam(build_ele, llargadaVertical, firstCancam, secondCancam, False, True)
                if liniaCancam != []:
                    group_elems.append(liniaCancam)
                    group_elems_preview.append(liniaCancam)
        '''
        for i in range(0, len(build_ele.ColisParSUP.value)):
            if build_ele.ColisParSUP.value[i].Colis and build_ele.ColisParSUP.value[i].MostrarBox and build_ele.ColisParSUP.value[i].Posicio < llargadaSup:
                boxsColis = createColis(build_ele, llargadaVertical, i)
                group_elems.append(boxsColis)
                group_elems_preview.append(boxsColis)
                cavitatColis = createColisCavitatHorSup(build_ele, llargadaVertical, i)
                if cavitatColis != []:
                    for cavCapa in cavitatColis:
                        group_elems.append(cavCapa)
                        group_elems_preview.append(cavCapa)



        if build_ele.SepararTDHoritzontalSup.value:
            if build_ele.listDesplHoritzontalsSup.value[nBarraSup].mostrarLiniaA:
                punt_central = desplYSeparatSup + build_ele.listDesplHoritzontalsSup.value[nBarraSup].desplX + build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAlturaSup/2
                pointUbi = AllplanGeo.Point3D(desplXSeparatSup + vectorH2[12], vectorH2[13] + build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAmpleSup/2 + build_ele.listDesplHoritzontalsSup.value[nBarraSup].desplLinA, vectorH2[14] +  build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAlturaSup/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAmpleSup,build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraLlargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
            if build_ele.listDesplHoritzontalsSup.value[nBarraSup].mostrarLiniaB:
                punt_central = desplYSeparatSup + build_ele.listDesplHoritzontalsSup.value[nBarraSup].desplX + build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAlturaSup/2
                pointUbi = AllplanGeo.Point3D(desplXSeparatSup, vectorH2[13] + build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAmpleSup/2 + build_ele.listDesplHoritzontalsSup.value[nBarraSup].desplLinB, vectorH2[14] +  build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAlturaSup/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central,build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraAmpleSup,build_ele.listDesplHoritzontalsSup.value[nBarraSup].BarraLlargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], group_elems[len(group_elems)-1]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
        else:
            if build_ele.mostrarLiniaIntSup1.value:
                punt_central = vectorH2[12] + build_ele.desplXS.value + build_ele.BarraAlturaSup.value/2
                pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSup.value/2 + build_ele.desplLiniaIntSup1.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSup.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)

                if build_ele.SelectorTDHSup.value == "L":
                    punt_central = vectorH2[12] + build_ele.desplXSL.value + build_ele.BarraAlturaSupL.value/2
                    pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSupL.value/2 + build_ele.desplLiniaIntSup1.value , vectorH2[14] + build_ele.BarraAlturaSupL.value/2)
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSupL.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
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
                pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSup.value/2 + build_ele.desplLiniaIntSup2.value , vectorH2[14] + build_ele.BarraAlturaSup.value/2)
                linia = build_ele.SelectorLiniaSup.value[len(build_ele.SelectorLiniaSup.value)-1]
                polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSup.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)
                if build_ele.SelectorTDHSup.value == "L":
                    punt_central = vectorH2[12] + build_ele.desplXSL.value + build_ele.BarraAlturaSupL.value/2
                    pointUbi = AllplanGeo.Point3D(vectorH2[12], vectorH2[13] + build_ele.BarraAmpleSupL.value/2 + build_ele.desplLiniaIntSup2.value , vectorH2[14] + build_ele.BarraAlturaSupL.value/2)
                    polyhedronCentral = create_polyline_interior(build_ele, punt_central, build_ele.BarraAmpleSupL.value, llargadaSup, True, pointUbi, int(linia), build_ele.SelectorLayerSup.value)


                if polyhedronCentral != []:
                    group_elems.append(polyhedronCentral[0])
                    group_elems_preview.append(polyhedronCentral[0])
                    group_elems.append(polyhedronCentral[3])
                    group_elems_preview.append(polyhedronCentral[3])
                    #model_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))
                    #model_ele_list2.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[0]))
                    #preview_ele_list.append(AllplanBasisElements.ModelElement3D(polyhedronCentral[1], polyhedronCentral[2]))


        return group_elems, horitzontalPP2, group_elems_preview

    return [], [], []

def crear_cavitat_hor(build_ele, ample, altura, llargada, vectorH2, desplXSeparat = 0):
    group_elems = group_elems_preview = []

    common_propsObjectSup = AllplanBaseElements.CommonProperties()
    common_propsObjectSup2 = AllplanBaseElements.CommonProperties()
    common_propsObjectSup.Layer = 40054#(KN_XPS_RECESS)
    common_propsObjectSup2.Layer = 40055#(KN_XPS_CAVITAT)
    colorCavitat = getColorCavitat(ample)
    common_propsObjectSup.Color = colorCavitat
    common_propsObjectSup2.Color = colorCavitat
    horitzontalPPOBject2 = PP_TD_Horitzontal(random.random() * 3600, 0, ample, altura+10, llargada + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup.Color, common_propsObjectSup.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparat)
    horitzontalPPOBject2A = PP_TD_Horitzontal(random.random() * 3600, 0, ample, altura+10, llargada + 10, 0,#DistanciaEntreTD, BarraAmple, BarraAltura,BarraLlargada, BarraGruix,
                                False, common_propsObjectSup2.Color, common_propsObjectSup2.Layer,# IsUseGlobalPropVert, FounColorVert, BarraLayerVert,
                                [], [],[], #ColisPar, PotaPar, #matrius
                                0, 0, 0,#Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                                [], #Femelles, #matriu
                                0, #posicio_centre_masses,
                                False, 0, #IsFirstCancam, Dis1cancam,
                                False, 0, #IsSecondCancam, Dis2cancam,
                                build_ele.PestanyaSuperiorSUP.value, build_ele.PestanyaInferiorSUP.value,#PestanyaSuperior, PestanyaInferior,
                                [],
                                retallInici=desplXSeparat)
    horitzontal_BrepObject2 = horitzontalPPOBject2.create()
    horitzontal_BrepObject2A = horitzontalPPOBject2A.create()

    table_attr_listObject = [AllplanBaseElements.AttributeString(508, "CAVITAT "),
                            #AllplanBaseElements.AttributeString(508, " "),
                            AllplanBaseElements.AttributeString(2103, "CAVITAT "),
                            AllplanBaseElements.AttributeString(1083, "CAVITAT "),
                            AllplanBaseElements.AttributeString(507, build_ele.NomTD.value)
                            ]

    vectorH2C = AllplanGeo.Matrix3D()
    vectorH2C.SetValue(12, vectorH2[12]-5)
    vectorH2C.SetValue(13, vectorH2[13])
    vectorH2C.SetValue(14, vectorH2[14]-5)


    if build_ele.MostrarTDHoritzontalSup.value:
        table_views_object2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2)])]
        table_views_object_2 = [View2D3D ([AllplanBasisElements.ModelElement3D(common_propsObjectSup2, horitzontal_BrepObject2A)])]

        if build_ele.MostrarRecessSup.value and build_ele.MostrarCavitatsRecess.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2.get_params_list(),
                                        hash_value = horitzontalPPOBject2.hash(), python_file = horitzontalPPOBject2.filename(),
                                        views = table_views_object2, matrix = vectorH2C, common_props = common_propsObjectSup, attribute_list = table_attr_listObject))
            #model_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))
            #model_ele_list2.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, group_elems[len(group_elems)-1]))
            #preview_ele_list.append(AllplanBasisElements.ModelElement3D(common_propsObjectSup, horitzontal_BrepObject2))

        if build_ele.MostrarCavitatSup.value and build_ele.MostrarCavitats.value:
            group_elems.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
            group_elems_preview.append(PythonPart ("Cavitat_Horitzontal", parameter_list = horitzontalPPOBject2A.get_params_list(),
                                        hash_value = horitzontalPPOBject2A.hash(), python_file = horitzontalPPOBject2A.filename(),
                                        views = table_views_object_2, matrix = vectorH2C, common_props = common_propsObjectSup2, attribute_list = table_attr_listObject))
    return group_elems, group_elems_preview

def add_baraInferior(build_ele, nBarraInf):
    while nBarraInf >= len(build_ele.listDesplHoritzontalsInf.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraAmpleInf BarraAlturaInf BarraLlargadaInf desplX desplY mostrarLiniaA desplLinA mostrarLiniaB desplLinB ')
        bob = TDVertCollection( BarraAmpleInf = 30,
                               BarraAlturaInf = 30,
                               BarraLlargadaInf = 1300,
                               desplX = 0,
                               desplY = 0,
                               mostrarLiniaA = True,
                               desplLinA = 0,
                               mostrarLiniaB = False,
                               desplLinB = 5)
        build_ele.listDesplHoritzontalsInf.value.append(bob)

def add_baraSuperior(build_ele, nBarraSup):
    while nBarraSup >= len(build_ele.listDesplHoritzontalsSup.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'BarraAmpleSup BarraAlturaSup BarraLlargadaSup desplX desplY mostrarLiniaA desplLinA mostrarLiniaB desplLinB ')
        bob = TDVertCollection( BarraAmpleSup = 30,
                               BarraAlturaSup = 30,
                               BarraLlargadaSup = 1300,
                               desplX = 0,
                               desplY = 0,
                               mostrarLiniaA = True,
                               desplLinA = 0,
                               mostrarLiniaB = False,
                               desplLinB = 5)
        build_ele.listDesplHoritzontalsSup.value.append(bob)

def crearLlistaVerticals(build_ele):
    for barra in range(0, build_ele.IntegerTDSelector.value):
        if barra >= len(build_ele.valueListBarresComboBox.value):
            build_ele.valueListBarresComboBox.value.append("Tub " + str(barra))
        else:
            build_ele.valueListBarresComboBox.value[barra] = "Tub " + str(barra)

def crearLlistaHoritzontals(build_ele):

    #build_ele.valueVertListBarresHorSup.value = []
    if len(build_ele.valueVertListBarresHorSup.value) == 0:
        build_ele.valueVertListBarresHorSup.value.append("TD Superior")
    else:
        build_ele.valueVertListBarresHorSup.value[0] = "TD Superior"

    if len(build_ele.valueVertListBarresHorInf.value) == 0:
        build_ele.valueVertListBarresHorInf.value.append("TD Inferior")
    else:
        build_ele.valueVertListBarresHorInf.value[0] = "TD Inferior"
    barraVert = 0
    barraVertAux = 0
    Afegits = 1
    for barra in range(0, len(build_ele.BarresHorList.value)):

        if Afegits >= len(build_ele.valueVertListBarresHorSup.value):
            if build_ele.BarresHorList.value[barra].BarraHor:
                #build_ele.valueVertListBarresHorSup.value.append("Tub " + str(barraVert) + "." + str(barraVertAux+1))
                #build_ele.valueVertListBarresHorInf.value.append("Tub " + str(barraVert) + "." + str(barraVertAux+1))
                build_ele.valueVertListBarresHorSup.value.append("Tub " + str(barra))
                build_ele.valueVertListBarresHorInf.value.append("Tub " + str(barra))

                Afegits += 1
        else:
            if build_ele.BarresHorList.value[barra].BarraHor:
                #build_ele.valueVertListBarresHorSup.value[Afegits] = "Tub " + str(barraVert) + "." + str(barraVertAux+1)
                #build_ele.valueVertListBarresHorInf.value[Afegits] = "Tub " + str(barraVert) + "." + str(barraVertAux+1)
                build_ele.valueVertListBarresHorSup.value[Afegits] = "Tub " + str(barra)
                build_ele.valueVertListBarresHorInf.value[Afegits] = "Tub " + str(barra)
                Afegits += 1


        barraVertAux += 1
        if barraVertAux == NombreBarresHorInt:
            barraVert += 1
            barraVertAux = 0

    while Afegits < len(build_ele.valueVertListBarresHorSup.value):
        build_ele.valueVertListBarresHorSup.value.pop()

    while Afegits < len(build_ele.valueVertListBarresHorInf.value):
        build_ele.valueVertListBarresHorInf.value.pop()

def crearLlistaFullHoritzontals(build_ele):

    #build_ele.valueVertListBarresHorSup.value = []
    if len(build_ele.valueListBarresHorBalc.value) == 0:
        build_ele.valueListBarresHorBalc.value.append("TD Superior")
    else:
        build_ele.valueListBarresHorBalc.value[0] = "TD Superior"

    if len(build_ele.valueListBarresHorBalc.value) == 1:
        build_ele.valueListBarresHorBalc.value.append("TD Inferior")
    else:
        build_ele.valueListBarresHorBalc.value[1] = "TD Inferior"
    barraVert = 0
    barraVertAux = 0
    Afegits = 2
    for barra in range(0, len(build_ele.BarresHorList.value)):

        if Afegits >= len(build_ele.valueListBarresHorBalc.value):
            build_ele.valueListBarresHorBalc.value.append("Tub " + str(barra))

            Afegits += 1
        else:
            build_ele.valueListBarresHorBalc.value[Afegits] = "Tub " + str(barra)
            Afegits += 1

        if Afegits-2 >= len(build_ele.valueListBarresHorBalcOnlyNum.value):
            build_ele.valueListBarresHorBalcOnlyNum.value.append("Tub " + str(barra))
        else:
            build_ele.valueListBarresHorBalcOnlyNum.value[Afegits-2] = "Tub " + str(barra)



        barraVertAux += 1
        if barraVertAux == NombreBarresHorInt:
            barraVert += 1
            barraVertAux = 0

    while Afegits < len(build_ele.valueListBarresHorBalc.value):
        build_ele.valueListBarresHorBalc.value.pop()


def crearLlistaReforc(build_ele):
    for barra in range(0, build_ele.NumBarresRef.value):
        if barra >= len(build_ele.valueListReforcComboBox.value):
            build_ele.valueListReforcComboBox.value.append("Reforç " + str(barra))
        else:
            build_ele.valueListReforcComboBox.value[barra] = "Reforç " + str(barra)
    while len(build_ele.valueListReforcComboBox.value) > build_ele.NumBarresRef.value:
        build_ele.valueListReforcComboBox.value.pop()
    while len(build_ele.BarresRefListTD.value) > build_ele.NumBarresRef.value:
        build_ele.BarresRefListTD.value.pop()
def copiar_valors_Vert(build_ele,nVer):

    if len(build_ele.DadesVertCopy.value) == 0:
        CopyDadesCollection = collections.namedtuple('StirrupList', 'nBarraGuardada BarraAmple BarraAltura BarraLlargada desplY esProvisional ')
        bob = CopyDadesCollection(nBarraGuardada = nVer,
                                  BarraAmple = build_ele.dadesTDVertTD.value[nVer].BarraAmple,
                                  BarraAltura = build_ele.dadesTDVertTD.value[nVer].BarraAltura,
                                  BarraLlargada = build_ele.dadesTDVertTD.value[nVer].BarraAlcada,
                                  desplY = build_ele.listDesplVerticalsTD.value[nVer].desplYAbs,
                                  esProvisional= build_ele.dadesTDVertTD.value[nVer].esProvisional)
        build_ele.DadesVertCopy.value.append(bob)

    else:
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(nBarraGuardada = nVer)

        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraAmple = build_ele.dadesTDVertTD.value[nVer].BarraAmple)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraAltura = build_ele.dadesTDVertTD.value[nVer].BarraAltura)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(BarraLlargada = build_ele.dadesTDVertTD.value[nVer].BarraAlcada)

        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(desplY = build_ele.listDesplVerticalsTD.value[nVer].desplYAbs)
        build_ele.DadesVertCopy.value[0] = build_ele.DadesVertCopy.value[0]._replace(esProvisional = build_ele.dadesTDVertTD.value[nVer].esProvisional)


    a = 0
    for nVerA in  range(nVer*10, nVer*10+10 ):
        if a >= len(build_ele.ForatsVertListCopy.value) :
            ForatsCopyDadesCollection = collections.namedtuple('StirrupList', 'Forat orientacio Posicio Llargada Amplada Complet LlargadaB AmpladaB MostrarBox ProfunditatTFF ')
            bob = ForatsCopyDadesCollection(Forat = build_ele.ForatsVertList.value[nVerA].Forat,
                                            orientacio = build_ele.ForatsVertList.value[nVerA].orientacio,
                                            Posicio = build_ele.ForatsVertList.value[nVerA].Posicio,
                                            Llargada = build_ele.ForatsVertList.value[nVerA].Llargada,
                                            Amplada = build_ele.ForatsVertList.value[nVerA].Amplada,
                                            Complet = build_ele.ForatsVertList.value[nVerA].Complet,
                                            LlargadaB = build_ele.ForatsVertList.value[nVerA].LlargadaB,
                                            AmpladaB = build_ele.ForatsVertList.value[nVerA].AmpladaB ,
                                            MostrarBox = build_ele.ForatsVertList.value[nVerA].MostrarBox,
                                            ProfunditatTFF = build_ele.ForatsVertList.value[nVerA].ProfunditatTFF)
            build_ele.ForatsVertListCopy.value.append(bob)
        else:
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Forat = build_ele.ForatsVertList.value[nVerA].Forat)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(orientacio = build_ele.ForatsVertList.value[nVerA].orientacio)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Posicio = build_ele.ForatsVertList.value[nVerA].Posicio)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Llargada = build_ele.ForatsVertList.value[nVerA].Llargada )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Amplada = build_ele.ForatsVertList.value[nVerA].Amplada )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(Complet = build_ele.ForatsVertList.value[nVerA].Complet )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(LlargadaB = build_ele.ForatsVertList.value[nVerA].LlargadaB )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(AmpladaB = build_ele.ForatsVertList.value[nVerA].AmpladaB )
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(MostrarBox = build_ele.ForatsVertList.value[nVerA].MostrarBox)
            build_ele.ForatsVertListCopy.value[a] = build_ele.ForatsVertListCopy.value[a]._replace(ProfunditatTFF = build_ele.ForatsVertList.value[nVerA].ProfunditatTFF)
        if a >= len(build_ele.BarresFrontListCopy.value) :
            ForatsCopyDadesCollection = collections.namedtuple('StirrupList', 'BarraFront Amplitud Altura Orientacio Posicio Longitud Profunditat Edit Save acabatEditar')
            bob = ForatsCopyDadesCollection(BarraFront = build_ele.BarresFrontList.value[nVerA].BarraFront,
                                            Amplitud = build_ele.BarresFrontList.value[nVerA].Amplitud,
                                            Altura = build_ele.BarresFrontList.value[nVerA].Altura,
                                            Orientacio = build_ele.BarresFrontList.value[nVerA].Orientacio,
                                            Posicio = build_ele.BarresFrontList.value[nVerA].Posicio,
                                            Longitud = build_ele.BarresFrontList.value[nVerA].Longitud,
                                            Profunditat = build_ele.BarresFrontList.value[nVerA].Profunditat,
                                            Edit =False,
                                            Save = False,
                                            acabatEditar = False)
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

    build_ele.dadesTDVertTD.value[nVer] = build_ele.dadesTDVertTD.value[nVer]._replace(BarraAmple = build_ele.DadesVertCopy.value[0].BarraAmple)
    build_ele.dadesTDVertTD.value[nVer] = build_ele.dadesTDVertTD.value[nVer]._replace(BarraAltura = build_ele.DadesVertCopy.value[0].BarraAltura)
    build_ele.dadesTDVertTD.value[nVer] = build_ele.dadesTDVertTD.value[nVer]._replace(BarraAlcada = build_ele.DadesVertCopy.value[0].BarraLlargada)

    build_ele.listDesplVerticalsTD.value[nVer] = build_ele.listDesplVerticalsTD.value[nVer]._replace(desplYAbs = build_ele.DadesVertCopy.value[0].desplY)
    build_ele.dadesTDVertTD.value[nVer] = build_ele.dadesTDVertTD.value[nVer]._replace(esProvisional = build_ele.DadesVertCopy.value[0].esProvisional)


    a = 0
    for nVerA in  range(nVer*10, nVer*10+10 ):
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(Forat = build_ele.ForatsVertListCopy.value[a].Forat)
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(orientacio = build_ele.ForatsVertListCopy.value[a].orientacio)
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(Posicio = build_ele.ForatsVertListCopy.value[a].Posicio)
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(Llargada =build_ele.ForatsVertListCopy.value[a].Llargada )
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(Amplada =build_ele.ForatsVertListCopy.value[a].Amplada )
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(Complet =build_ele.ForatsVertListCopy.value[a].Complet )
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(LlargadaB =build_ele.ForatsVertListCopy.value[a].LlargadaB )
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(AmpladaB =build_ele.ForatsVertListCopy.value[a].AmpladaB )
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(MostrarBox = build_ele.ForatsVertListCopy.value[a].MostrarBox)
        build_ele.ForatsVertList.value[nVerA] = build_ele.ForatsVertList.value[nVerA]._replace(ProfunditatTFF = build_ele.ForatsVertListCopy.value[a].ProfunditatTFF)

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


def crear_LProvisionals(build_ele,j, vectorH1, esExtrem, esFinal, numL):
    alturaInf = 0
    if not build_ele.dadesTDVertTD.value[j].EncaixInf :
        if build_ele.dadesTDVertTD.value[j].BarraInferior == "TD Inferior":
            alturaInf = build_ele.BarraAlturaInf.value
        else:
            nHorInf = 0
            if build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Inferior" and build_ele.dadesTDVertTD.value[j].BarraInferior != "TD Superior":
                nHorInf = build_ele.dadesTDVertTD.value[j].BarraInferior
                if len(build_ele.dadesTDVertTD.value[j].BarraInferior) > 3:
                    if len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 7:
                        nHorInfCentenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-3])
                        nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                        nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                        nHorInf = nHorInfCentenes*100 + nHorInfDecenes*10 + nHorInfUnitats
                    elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 6:
                        nHorInfDecenes = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-2])
                        nHorInfUnitats = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
                        nHorInf = nHorInfDecenes*10 + nHorInfUnitats
                    elif len(build_ele.dadesTDVertTD.value[j].BarraInferior) == 5:
                        nHorInf = int(build_ele.dadesTDVertTD.value[j].BarraInferior[-1])
            alturaInf = build_ele.dadesTDHortInter.value[nHorInf].Altura
    Lprovisionals = LProvisional(random.random() * 3600, build_ele.dadesTDVertTD.value[j].BarraAmple + 2, build_ele.dadesTDVertTD.value[j].BarraAltura, build_ele.dadesTDVertTD.value[j].BarraAlcada - 76 - alturaInf, build_ele.dadesTDVertTD.value[j].Gruix,
                                False, 7, build_ele.BarraLayerVert.value, esExtrem, esFinal, numL) #matriu

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
    vectorH1A.SetValue(12, vectorH1[12] - 76 )
    vectorH1A.SetValue(13, vectorH1[13] + build_ele.dadesTDVertTD.value[j].BarraAltura/2 - 17.5/2)
    vectorH1A.SetValue(14, vectorH1[14] + alturaInf)

    PP_Lprovisional = [PythonPart ("TD_LProvisional", parameter_list = Lprovisionals.get_params_list(),
                                hash_value = Lprovisionals.hash(), python_file = Lprovisionals.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1A, common_props = common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals),
                        common_props_Lprovisionals,
                        Lprovisionals_BrepObject]

    return PP_Lprovisional


def create_num_on_view(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesTDVertTD.value[j].BarraAmple + 2, build_ele.dadesTDVertTD.value[j].BarraAltura, build_ele.dadesTDVertTD.value[j].BarraAlcada - 30, build_ele.dadesTDVertTD.value[j].Gruix,
                                False, 8, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                             AllplanBaseElements.AttributeString(1083, "num ID"),
                             AllplanBaseElements.AttributeString(508, " ")]#num

    vectorH1B = AllplanGeo.Matrix3D()

    if build_ele.InvertirTDNums.value:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(0,0,1))

        vectorH1B.Rotation(z_axis, AllplanGeo.Angle.FromDeg(180))


    vectorH1B.SetValue(12, vectorH1[12] - build_ele.dadesTDVertTD.value[j].BarraAmple  - (20*build_ele.tamanyNumId.value))
    if build_ele.InvertirTDNums.value:
        vectorH1B.SetValue(12, vectorH1[12] + build_ele.dadesTDVertTD.value[j].BarraAmple  + (20*build_ele.tamanyNumId.value))
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, build_ele.dadesTDVertTD.value[j].BarraAlcada + vectorH1[14] )
    if j == 0:
        vectorH1B.SetValue(14, build_ele.dadesTDVertTD.value[j].BarraAlcada - 100 )

    test = PythonPart ("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props = common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return [test, common_props_Lprovisionals, Lprovisionals_BrepObject]

def create_num_on_view_Hor(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesTDHortInter.value[j].Ample + 2, build_ele.dadesTDHortInter.value[j].Altura, build_ele.dadesTDHortInter.value[j].Llargada - 30, build_ele.dadesTDHortInter.value[j].Gruix,
                                False, 4, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                             AllplanBaseElements.AttributeString(1083, "num ID"),
                             AllplanBaseElements.AttributeString(508, " ")]#num

    vectorH1B = AllplanGeo.Matrix3D()

    if build_ele.InvertirTDNums.value:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                            point2=  AllplanGeo.Point3D(0,0,1))

        vectorH1B.Rotation(z_axis, AllplanGeo.Angle.FromDeg(180))

    vectorH1B.SetValue(12, vectorH1[12] - (20*build_ele.tamanyNumId.value) - 100)
    if build_ele.InvertirTDNums.value:
        vectorH1B.SetValue(12, vectorH1[12] + (20*build_ele.tamanyNumId.value) + 100 )
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, vectorH1[14] )
    if j == 0:
        vectorH1B.SetValue(14, vectorH1[14] - 100 )

    test = PythonPart ("TD_CreateText", parameter_list = numVert.get_params_list(),
                                hash_value = numVert.hash(), python_file = numVert.filename(),
                                views = Lprovisionals_views_object, matrix = vectorH1B, common_props = common_props_Lprovisionals, attribute_list = attr_list_Lprovisionals)

    return [test, common_props_Lprovisionals, Lprovisionals_BrepObject]

def create_num_on_view_ref(build_ele, j, vectorH1):
    numVert = TextSpline(random.random() * 3600, build_ele.dadesENReftInterTD.value[j].Ample + 2, build_ele.dadesENReftInterTD.value[j].Altura, build_ele.dadesENReftInterTD.value[j].Llargada - 30, build_ele.dadesTDVertTD.value[j].Gruix,
                                False, 51, build_ele.BarraLayerVert.value, str(j), build_ele.tamanyNumId.value)

    if not numVert.is_valid():
        return[]


    Lprovisionals_BrepObject = numVert.create()
    common_props_Lprovisionals = numVert.get_common_props()

    Lprovisionals_views_object = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props_Lprovisionals, Lprovisionals_BrepObject)])]

    attr_list_Lprovisionals = [AllplanBaseElements.AttributeString(2103, "num ID "),
                             AllplanBaseElements.AttributeString(508, " ")]#num

    vectorH1B = AllplanGeo.Matrix3D()

    if build_ele.InvertirTDNums.value:
        z_axis = AllplanGeo.Line3D(point1=  AllplanGeo.Point3D(),
                                point2=  AllplanGeo.Point3D(0,0,1))

        vectorH1B.Rotation(z_axis, AllplanGeo.Angle.FromDeg(180))

    vectorH1B.SetValue(12, vectorH1[12] - build_ele.dadesENReftInterTD.value[j].Ample )
    if build_ele.InvertirTDNums.value:
        vectorH1B.SetValue(12, vectorH1[12] + build_ele.dadesENReftInterTD.value[j].Ample )
    vectorH1B.SetValue(13, vectorH1[13]  )
    vectorH1B.SetValue(14, build_ele.BarresRefListTD.value[j].Posicio + build_ele.dadesENReftInterTD.value[j].Altura + 10 )
    if j == 0:
        vectorH1B.SetValue(14, build_ele.BarresRefListTD.value[j].Posicio - 100 )

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
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargadaTD.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconera.value + build_ele.AmpleBalconera.value, 0, build_ele.PosicioZBalconera.value + build_ele.LlargadaBalconera.value),
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, build_ele.PosicioZBalconera.value),
                                        [("AmpleBalconera", HandleDirection.x_dir),
                                         ("LlargadaBalconera", HandleDirection.z_dir)],
                                        HandleDirection.xy_dir),
                        HandleProperties("BarraPosicio",
                                        AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, build_ele.PosicioZBalconera.value ),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("PosicioXBalconera", HandleDirection.x_dir),
                                         ("PosicioZBalconera", HandleDirection.z_dir)],
                                        HandleDirection.xy_dir)
                                        #HandleProperties("LlargadaBalconera",
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, build_ele.LlargadaBalconera.value),
                                        #AllplanGeo.Point3D(build_ele.PosicioXBalconera.value, 0, 0),
                                        #[("BarraLlargada", HandleDirection.z_dir)],
                                        #HandleDirection.z_dir)
                      ]

        return handle_list


def buscar_anterior_mes_proper(build_ele, posicioX):

    trobatAnt = False
    posNAntMesPropera = 0
    posicioAntMesPropera = 0.0

    #for nBarra in range(1,len(build_ele.listDesplVerticalsTD.value)):
    for nBarra in range(1,build_ele.IntegerTDSelector.value):
        if build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs < posicioX and build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs >= posicioAntMesPropera and build_ele.dadesTDVertTD.value[nBarra].MostrarTDVertical and not build_ele.dadesTDVertTD.value[nBarra].esProvisional and  build_ele.dadesTDVertTD.value[nBarra].BarraSuperior == "TD Superior" and  build_ele.dadesTDVertTD.value[nBarra].BarraInferior == "TD Inferior" :
            posicioAntMesPropera = build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs + 80
            trobatAnt = True
            posNAntMesPropera = nBarra

    return trobatAnt, posNAntMesPropera

def buscar_seguent_mes_proper(build_ele, posicioX):

    trobatSeg = False
    posNSegMesPropera = 0
    #posicioSegMesPropera = build_ele.BarraLlargadaTD.value + build_ele.DistanciaEntreTD.value
    posicioSegMesPropera = (build_ele.IntegerTDSelector.value-1) * build_ele.DistanciaEntreTD.value

    #for nBarra in range(1,len(build_ele.listDesplVerticalsTD.value)):
    for nBarra in range(1,build_ele.IntegerTDSelector.value-1):
        if build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs > posicioX and build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs <= posicioSegMesPropera and build_ele.dadesTDVertTD.value[nBarra].MostrarTDVertical and not build_ele.dadesTDVertTD.value[nBarra].esProvisional and  build_ele.dadesTDVertTD.value[nBarra].BarraSuperior == "TD Superior" and  build_ele.dadesTDVertTD.value[nBarra].BarraInferior == "TD Inferior" :
            posicioSegMesPropera = build_ele.listDesplVerticalsTD.value[nBarra].desplXAbs
            trobatSeg = True
            posNSegMesPropera = nBarra

    return trobatSeg, posNSegMesPropera

def afegir_balconera_finestra(build_ele, nBalcFin):

     while nBalcFin >= len(build_ele.dadesBalcFines.value):
        TDVertCollection = collections.namedtuple('StirrupList', 'Mostrar AmpleBalconera LlargadaBalconera PosicioXBalconera PosicioZBalconera BarraHorSup BarraHorInf BarraVertEsq BarraVertDre')
        bob = TDVertCollection(Mostrar = True,
                               AmpleBalconera = 400,
                               LlargadaBalconera = 400,
                               PosicioXBalconera = 600,
                               PosicioZBalconera = 800,
                               BarraHorSup = "TD Superior",
                               BarraHorInf = "TD Inferior",
                               BarraVertEsq = "Tub 0",
                               BarraVertDre = "Tub 1")
        build_ele.dadesBalcFines.value.append(bob)

def mostrar_BalcFine(build_ele, nBalcFin):
    if len(build_ele.dadesBalcFines.value) <= nBalcFin:
        afegir_balconera_finestra(build_ele, nBalcFin)
    if build_ele.dadesBalcFines.value[nBalcFin].AmpleBalconera == 0:
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(Mostrar = True)
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(AmpleBalconera = 400)
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(LlargadaBalconera = 400)
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(PosicioXBalconera = 600)
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(PosicioZBalconera = 800)
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraHorSup = "TD Superior")
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraHorInf = "TD Inferior")
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraVertEsq = "Tub 0")
        build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraVertDre = "Tub 1")
    build_ele.MostrarBalconera.value = build_ele.dadesBalcFines.value[nBalcFin].Mostrar
    build_ele.AmpleBalconera.value = build_ele.dadesBalcFines.value[nBalcFin].AmpleBalconera
    build_ele.LlargadaBalconera.value = build_ele.dadesBalcFines.value[nBalcFin].LlargadaBalconera
    build_ele.PosicioXBalconera.value = build_ele.dadesBalcFines.value[nBalcFin].PosicioXBalconera
    build_ele.PosicioZBalconera.value = build_ele.dadesBalcFines.value[nBalcFin].PosicioZBalconera
    build_ele.SelectorTDHorSupBalc.value = build_ele.dadesBalcFines.value[nBalcFin].BarraHorSup
    build_ele.SelectorTDHorInfBalc.value = build_ele.dadesBalcFines.value[nBalcFin].BarraHorInf
    build_ele.SelectorTDHorEsqBalc.value = build_ele.dadesBalcFines.value[nBalcFin].BarraVertEsq
    build_ele.SelectorTDHorDreBalc.value = build_ele.dadesBalcFines.value[nBalcFin].BarraVertDre

def guardar_valors_BalcFine(build_ele, nBalcFin):
    if len(build_ele.dadesBalcFines.value) < nBalcFin:
        afegir_balconera_finestra(build_ele, nBalcFin+1)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(Mostrar = build_ele.MostrarBalconera.value )
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(AmpleBalconera = build_ele.AmpleBalconera.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(LlargadaBalconera = build_ele.LlargadaBalconera.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(PosicioXBalconera = build_ele.PosicioXBalconera.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(PosicioZBalconera = build_ele.PosicioZBalconera.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraHorSup = build_ele.SelectorTDHorSupBalc.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraHorInf = build_ele.SelectorTDHorInfBalc.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraVertEsq = build_ele.SelectorTDHorEsqBalc.value)
    build_ele.dadesBalcFines.value[nBalcFin] = build_ele.dadesBalcFines.value[nBalcFin]._replace(BarraVertDre = build_ele.SelectorTDHorDreBalc.value)


def mostrar_tubHorInt(build_ele, nHorInt):
    while len(build_ele.BarresHorListToShowTD.value) > 1:
        build_ele.BarresHorListToShowTD.value.pop()

    if nHorInt != build_ele.SelectorTDHTotalAnt.value or (build_ele.SelectorPPTD.value == 1 and build_ele.SelectorPPAnt.value!=1):#error selector Hor
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Edit = True)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(acabatEditar = True)
        #mostrar_valors_hor(build_ele, 0, nHorInt)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(BarraHor = build_ele.BarresHorList.value[nHorInt].BarraHor)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Orientacio = build_ele.BarresHorList.value[nHorInt].Orientacio)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Posicio = build_ele.BarresHorList.value[nHorInt].Posicio)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(AutoLongitud = build_ele.BarresHorList.value[nHorInt].AutoLongitud)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Longitud = build_ele.BarresHorList.value[nHorInt].Longitud)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(BarraInici = build_ele.BarresHorList.value[nHorInt].BarraInici)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(BarraFinal = build_ele.BarresHorList.value[nHorInt].BarraFinal)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Edit = build_ele.BarresHorList.value[nHorInt].Edit)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(acabatEditar = build_ele.BarresHorList.value[nHorInt].acabatEditar)

        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(MostrarRecess = build_ele.BarresHorList.value[nHorInt].MostrarRecess)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(MostrarCavitat = build_ele.BarresHorList.value[nHorInt].MostrarCavitat)

        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Xapa = build_ele.BarresHorList.value[nHorInt].Xapa)
        build_ele.BarresHorListToShowTD.value[0] = build_ele.BarresHorListToShowTD.value[0]._replace(Layer = build_ele.BarresHorList.value[nHorInt].Layer)

        mostrar_valors_hor(build_ele, 0, nHorInt)

    if build_ele.BarresHorList.value[nHorInt].Edit:
        #guardar_valors_hor(build_ele, 0, nHorInt)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(BarraHor = build_ele.BarresHorListToShowTD.value[0].BarraHor)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Orientacio = build_ele.BarresHorListToShowTD.value[0].Orientacio)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Posicio = build_ele.BarresHorListToShowTD.value[0].Posicio)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(AutoLongitud = build_ele.BarresHorListToShowTD.value[0].AutoLongitud)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Longitud = build_ele.BarresHorListToShowTD.value[0].Longitud)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(BarraInici = build_ele.BarresHorListToShowTD.value[0].BarraInici)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(BarraFinal = build_ele.BarresHorListToShowTD.value[0].BarraFinal)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Edit = build_ele.BarresHorListToShowTD.value[0].Edit)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(acabatEditar = build_ele.BarresHorListToShowTD.value[0].acabatEditar)

        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(MostrarRecess = build_ele.BarresHorListToShowTD.value[0].MostrarRecess)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(MostrarCavitat = build_ele.BarresHorListToShowTD.value[0].MostrarCavitat)

        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Xapa = build_ele.BarresHorListToShowTD.value[0].Xapa)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(ProfunditatXapa = build_ele.BarresHorListToShowTD.value[0].ProfunditatXapa)
        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(Layer = build_ele.BarresHorListToShowTD.value[0].Layer)

        build_ele.BarresHorList.value[nHorInt] = build_ele.BarresHorList.value[nHorInt]._replace(acabatEditar = True)


#mostrar valors
def mostrar_valors_Ref(build_ele, nBarraVert):
    '''
    mostrar valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(BarraRef = build_ele.BarresRefListTD.value[nBarraVert].BarraRef)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(Orientacio = build_ele.BarresRefListTD.value[nBarraVert].Orientacio)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(Posicio = build_ele.BarresRefListTD.value[nBarraVert].Posicio)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(BarraIni = build_ele.BarresRefListTD.value[nBarraVert].BarraIni)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(BarraFin = build_ele.BarresRefListTD.value[nBarraVert].BarraFin)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(AutoLongitud = build_ele.BarresRefListTD.value[nBarraVert].AutoLongitud)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(Longitud = build_ele.BarresRefListTD.value[nBarraVert].Longitud)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(Edit = build_ele.BarresRefListTD.value[nBarraVert].Edit)
    build_ele.BarresRefListToShowTD.value[0] = build_ele.BarresRefListToShowTD.value[0]._replace(acabatEditar = build_ele.BarresRefListTD.value[nBarraVert].acabatEditar)


    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(estaEditant = build_ele.BarresRefListToShowTD.value[0].Edit)

    #build_ele.desplXVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplX
    #build_ele.desplYVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplY

    build_ele.desplXVertAbsRef.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplX
    build_ele.desplYVertAbsRef.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplY

    build_ele.mostrarLiniaVertA.value = build_ele.dadesENReftInterTD.value[nBarraVert ].mostrarLiniaVertA
    build_ele.desplVertLinA.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplLinA
    build_ele.mostrarLiniaVertB.value = build_ele.dadesENReftInterTD.value[nBarraVert ].mostrarLiniaVertB
    build_ele.desplVertLinB.value = build_ele.dadesENReftInterTD.value[nBarraVert ].desplLinB

    build_ele.SelectorLiniaRef.value = build_ele.dadesENReftInterTD.value[nBarraVert].linia
    build_ele.SelectorLayerRef.value = build_ele.dadesENReftInterTD.value[nBarraVert].layer

    build_ele.BarraAmpleRef.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Ample
    build_ele.BarraAlturaRef.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Altura
    #build_ele.BarraLlargadaVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Llargada
    build_ele.BarraGruixRef.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Gruix

    build_ele.IsUseGlobalPropVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].IsUseGlobalProp
    build_ele.FounColorVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].FounColor
    build_ele.BarraLayerVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].BarraLayer


    build_ele.Ample_forat_femellaVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Ample_forat_femella
    build_ele.Altura_forat_femellaVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Altura_forat_femella
    build_ele.Separacio_forat_femellaVert.value = build_ele.dadesENReftInterTD.value[nBarraVert ].Separacio_forat_femella



#guardar valors
def guardar_valors_Ref(build_ele, nBarraVert):
    '''
    mostrar valors de les Barres Reforcs intermitges per poder editarles
    get: nBarraVert -> posicio[] barra Vertical
         nRef -> posicio[][] del valor dins de la Barra Vertical

    return: -

    '''

    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(BarraRef = build_ele.BarresRefListToShowTD.value[0].BarraRef)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(Orientacio = build_ele.BarresRefListToShowTD.value[0].Orientacio)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(Posicio = build_ele.BarresRefListToShowTD.value[0].Posicio)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(BarraIni = build_ele.BarresRefListToShowTD.value[0].BarraIni)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(BarraFin = build_ele.BarresRefListToShowTD.value[0].BarraFin)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(AutoLongitud = build_ele.BarresRefListToShowTD.value[0].AutoLongitud)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(Longitud = build_ele.BarresRefListToShowTD.value[0].Longitud)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(Edit = build_ele.BarresRefListToShowTD.value[0].Edit)
    build_ele.BarresRefListTD.value[nBarraVert] = build_ele.BarresRefListTD.value[nBarraVert]._replace(acabatEditar = build_ele.BarresRefListToShowTD.value[0].acabatEditar)


    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(estaEditant = build_ele.BarresRefListToShowTD.value[0].Edit)

    #build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplX = build_ele.desplXVert.value)
    #build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplY = build_ele.desplYVert.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplX = build_ele.desplXVertAbsRef.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplY = build_ele.desplYVertAbsRef.value)

    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(mostrarLiniaVertA = build_ele.mostrarLiniaVertA.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplLinA = build_ele.desplVertLinA.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(mostrarLiniaVertB = build_ele.mostrarLiniaVertB.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(desplLinB = build_ele.desplVertLinB.value)

    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(linia = build_ele.SelectorLiniaRef.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(layer = build_ele.SelectorLayerRef.value)

    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(Ample = build_ele.BarraAmpleRef.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(Altura = build_ele.BarraAlturaRef.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(Llargada = build_ele.BarraLlargadaVert.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(Gruix = build_ele.BarraGruixRef.value)


    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(IsUseGlobalProp = build_ele.IsUseGlobalPropVert.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(FounColor = build_ele.FounColorVert.value)
    build_ele.dadesENReftInterTD.value[nBarraVert ] = build_ele.dadesENReftInterTD.value[nBarraVert ]._replace(BarraLayer = build_ele.BarraLayerVert.value)



def getColorCavitat(ample):
    color = 27
    distanciaMenor = 999

    colors = {
        "4"  : 15,
        "7"  : 27,
        "10" : 110,
        "12" : 107,
        "17" : 105,
        "20" : 47,
        "22" : 125,
        "25" : 4,
        "27" : 212,
        "30" : 33,
        "32" : 50,
        "40" : 5,
        "42" : 21,
        "43" : 188,
        "45" : 38,
        "50" : 116,
        "52" : 61,
        "60" : 251,
        "63" : 83,
        "65" : 93,
        "72" : 122,
        "75" : 208,
        "82" : 100,
        "95" : 53,
        "100": 244,
        "112": 65
    }


    if str(ample) in colors:#colors[ample]!= None:
        color = colors[str(ample)]
    else:

        claus = list(colors.keys())
        #claus.flat[np.abs(claus - ample).argmin()]
        mesProper = -1
        distMenor = -1
        for valor in claus:
            if distMenor == -1:
                mesProper = int(valor)
                distMenor = abs(ample - int(valor))
            else:
                if  abs(ample - int(valor)) < distMenor :
                    mesProper = int(valor)
                    distMenor = abs(ample - int(valor))
        color = colors[str(mesProper)]
        '''
        color = getColorCavitataproximat(ample)
        '''

    return color

def getColorCavitataproximat(ample):
    if ample == 4 or  ample < 6:
        return 15 #lila
    elif ample == 7 or ample >= 6 and ample < 9:
        return 27 #gris
    elif ample == 10 or ample >= 9 and ample < 11:
        return 110 #rosa fluix
    elif ample == 12 or ample >= 11 and ample < 15:
        return 107 #vermell fluix
    elif ample == 17 or ample >= 15 and ample < 19:
        return 105 #vermell
    elif ample == 20 or ample >= 19 and ample < 21:
        return 47 #groc fluix
    elif ample == 22 or ample >= 21 and ample < 24:
        return 125 #lila fluix
    elif ample == 25 or ample >= 24 and ample < 26:
        return 4 #verf
    elif ample == 27 or ample >= 11 and ample < 29:
        return 212 #marro

    elif ample == 30 or ample >= 29 and ample < 31:
        return 33 #verd fort
    elif ample == 32 or ample >= 31 and ample < 37:
        return 50 #verd amb blau
    elif ample == 40 or ample >= 37 and ample < 42:
        return 5 #rosa fosforito
    elif ample == 42 or ample >= 41 and ample < 43:
        return 21 #gris fort
    elif ample == 43 or ample >= 43 and ample < 45:
        return 188 #verdgroc
    elif ample == 45 or ample >= 44 and ample < 48:
        return 38 #verdgrocFort
    elif ample == 50 or ample >= 48 and ample < 52:
        return 116 #blau fort
    elif ample == 52 or ample >= 51 and ample < 57:
        return 61 #blau fluix
    elif ample == 60 or ample >= 57 and ample < 62:
        return 251 #morat

    elif ample == 63 or ample >= 62 and ample < 64:
        return 83 #rosafort
    elif ample == 65 or ample >= 64 and ample < 69:
        return 93 #rosafluixet
    elif ample == 72 or ample >= 69 and ample < 74:
        return 122 #moratBlauFluix
    elif ample == 75 or ample >= 74 and ample < 79:
        return 208 #granate fort
    elif ample == 82 or ample >= 79 and ample < 89:
        return 100 #granateVermellos
    elif ample == 95 or ample >= 89 and ample < 98:
        return 53 #blauVerdos
    elif ample == 100 or ample >= 98 and ample < 106:
        return 244 #moratFort
    elif ample == 112 or ample >= 106:
        return 65 #VerdosFort

    else:
        print("Cavitat amb un ample diferent")
        return 27 #blanc

def dividirAtribut(atributSencer):
    cara_ = atributSencer
    cara_1 = "#"
    cara_2 = "#"
    if len(cara_) > 200:
        cara_1 = cara_[200:]
        if len(cara_1) > 200:
            cara_2 = cara_1[200:]
            if len(cara_2) > 200:
                ctypes.windll.user32.MessageBoxW(0, "Hi ha un atribut mes llarg de 600 caracters", 0)
            cara_1 = cara_1[0:200]
        cara_ = cara_[0:200]
    return cara_, cara_1, cara_2



class TD_Conjunt_8():
    """
    Definition of class Table
    """

    '''
    def __init__(self, zUnique = 0, comprovarDEN = False, NomTD = "TD",  DistanciaEntreTD = 1170, SelectorPPTD = 1,
                 SelectorTDHTD = "TD Inferior", SelectorTDHInf = "Tub", SelectorTDHSup = "Tub",
                 SelectorTDHTotal = "Tub 0", IntegerTDSelector = 10, esVermellHor = False, SelectorTDV = "TDVer 0",
                 IntegerBalcFinSelector = 1, SelectorBalcFin = "Balc/Fin", MesuraXPS = 120,
                 MostrarTDVertical = True, SelectorTDHorInf = "TD Inferior", SelectorTDHorSup = "TD Superior", MostrarTDHoritzontalSup =True,
                 ):

        #Page 1
        self.zUnique = zUnique
        self.comprovarDEN = comprovarDEN
        self.NomTD = NomTD
        self.DistanciaEntreTDAnt = 100
        self.DistanciaEntreTD = DistanciaEntreTD
        self.SelectorPPAnt = 1
        self.SelectorPPTD = SelectorPPTD

        self.SelectorTDHTD = SelectorTDHTD
        self.SelectorTDHInf = SelectorTDHInf
        self.SelectorTDHSup = SelectorTDHSup

        self.valueListBarresHorBalcOnlyNum = []
        self.SelectorTDHTotalAnt = -1
        self.SelectorTDTipusHor = -1

        self.SelectorTDHTotal = SelectorTDHTotal #crear funció que pasi els valors de valueListBarresHorBalcOnlyNum o pasar un valor
        self.IntegerTDSelector = IntegerTDSelector
        self.esVermellHor = esVermellHor

        self.IntegerTDSelectorAnterior = -1
        self.SelectorTDVAnt = -1
        self.SelectorTDV = SelectorTDV

        self.IntegerBalcFinSelector = IntegerBalcFinSelector
        self.SelectorBalcFinAnt = -1
        self.SelectorBalcFin = SelectorBalcFin

        self.MesuraXPS = MesuraXPS
        self.MostrarTDVertical = MostrarTDVertical

        self.valueVertListBarresHorInf = [] #
        self.SelectorTDHorInf = SelectorTDHorInf
        self.valueVertListBarresHorSup = []
        self.SelectorTDHorSup = SelectorTDHorSup

        self.MostrarTDHoritzontalSup = MostrarTDHoritzontalSup
    '''

    def __init__(self, build_ele : BuildingElement, doc, placement_mat = AllplanGeo.Matrix3D() ):

        #self.build_ele_TD = BuildingElement()
        self.build_ele_TD = build_ele#.deep_copy()
        self.doc_TD = doc

        self.placement_mat = placement_mat

        #self.build_ele_ctrl_props_list = build_ele_ctrl_props_list


    def get_params_list(self):
        return self.build_ele_TD

    #def __repr__(self):

    #def hash(self):

    def filename(self):
        return "TD_Conjunt_8_clase.py"

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