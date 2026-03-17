"""
Script for Chair
"""
import hashlib

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate
import NemAll_Python_AllplanSettings as AllplanSettings
import collections
import random

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart
from PythonPartUtil import PythonPartUtil
from BuildingElementAttributeList import BuildingElementAttributeList

print('Load TD_Vertical_PP.py')

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
    return create_element(build_ele, doc)

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    del doc # param not needed

    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()

    build_ele.zUnique.value = random.random() * 3600

    TDVertical = PP_EN_Vertical(build_ele.zUnique.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,
                                build_ele.ColisPar.value, build_ele.PotaPar.value, build_ele.ForatsPar.value,#matrius
                                build_ele.Ample_forat_femella.value, build_ele.Altura_forat_femella.value, build_ele.Separacio_forat_femella.value,
                                build_ele.femelles.value, #matriu
                                build_ele.posicio_centre_masses.value,
                                build_ele.IsFirstCancam.value, build_ele.Dis1cancam.value,
                                build_ele.IsSecondCancam.value, build_ele.Dis2cancam.value,
                                build_ele.PestanyaSuperior.value, build_ele.PestanyaInferior.value,
                                build_ele.EncaixosPar.value) #matriu


    #build_ele.BarraAltura.value = build_ele.BarraAmple.value
    if not TDVertical.is_valid():
        return ([], [])


    handle_list = TDVertical.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDVertical.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2108, TDVertical.get_codi_cara_a()),
                AllplanBaseElements.AttributeString(2047, TDVertical.get_codi_cara_b()),
                AllplanBaseElements.AttributeString(2110, TDVertical.get_codi_cara_c()),
                AllplanBaseElements.AttributeString(2120, TDVertical.get_codi_cara_d()),

                AllplanBaseElements.AttributeString(2121, TDVertical.get_codi_cara_a_inv()),
                AllplanBaseElements.AttributeString(2122, TDVertical.get_codi_cara_b_inv()),
                AllplanBaseElements.AttributeString(2128, TDVertical.get_codi_cara_c_inv()),
                AllplanBaseElements.AttributeString(2129, TDVertical.get_codi_cara_d_inv()),

                AllplanBaseElements.AttributeString(2446, TDVertical.get_codi_pota_inv()),

                AllplanBaseElements.AttributeString(2430, TDVertical.get_codi_pestanyes()),
                AllplanBaseElements.AttributeString(2435, TDVertical.get_codi_cancam()),
                #AllplanBaseElements.AttributeString(2432, TDVertical.get_codi_colis()),
                #AllplanBaseElements.AttributeString(2429, TDVertical.get_codi_encaix()),
                #AllplanBaseElements.AttributeString(2434, TDVertical.get_codi_femella()),
                AllplanBaseElements.AttributeString(2431, TDVertical.get_codi_mesures()),
                AllplanBaseElements.AttributeString(2433, TDVertical.get_codi_pota()),
                AllplanBaseElements.AttributeString(2445, TDVertical.get_seccio()),
                AllplanBaseElements.AttributeString(220, TDVertical.get_llargada()),
                AllplanBaseElements.AttributeString(2103, "EN "),
                AllplanBaseElements.AttributeString(508, "TUB VER")]

    pythonpart = PythonPart ("PP_EN_Vertical",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()


    return (model_elem_list, handle_list)


class PP_EN_Vertical():
    """ implementation of the TD BAR 1
    """

    def __init__(self, zUnique = random.random() * 3600, BarraAmple = 30, BarraAltura = 30, BarraLlargada = 260, BarraGruix = 1.5,
                    IsUseGlobalProp = False, FounColor = 1, BarraLayer = 2,
                    ColisPar = [],#matrius
                    PotaPar = [],
                    ForatsPar = [],
                    Ample_forat_femella = 15, Altura_forat_femella = 3.75, Separacio_forat_femella = 50,
                    femelles= [], #matriu
                    posicio_centre_masses = 1500.00,
                    IsFirstCancam = False, Dis1cancam = 500,
                    IsSecondCancam = False, Dis2cancam = 1000,
                    PestanyaSuperior = False, PestanyaInferior = False,
                    EncaixosPar= [],
                    matrixPosXAux = [],
                    matrixPosYAux = [],
                    teTDHoritzontal = False, matrixPosTDH = [],
                    invertirPestanyes = False):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """

        self.zUnique = zUnique
        self.BarraAmple = BarraAmple
        self.BarraAltura = BarraAltura
        self.BarraLlargada = BarraLlargada
        self.BarraGruix = BarraGruix
        self.IsUseGlobalProp = IsUseGlobalProp
        self.FounColor = FounColor
        self.BarraLayer = BarraLayer
        self.ColisPar = ColisPar #matriu
        self.PotaPar = PotaPar #matrius
        self.ForatsPar = ForatsPar #matrius
        self.Ample_forat_femella = Ample_forat_femella
        self.Altura_forat_femella= Altura_forat_femella
        self.Separacio_forat_femella = Separacio_forat_femella
        self.femelles = femelles #matriu
        self.posicio_centre_masses = posicio_centre_masses
        self.IsFirstCancam = IsFirstCancam
        self.Dis1cancam = Dis1cancam
        self.IsSecondCancam = IsSecondCancam
        self.Dis2cancam = Dis2cancam
        self.PestanyaSuperior = PestanyaSuperior
        self.PestanyaInferior = PestanyaInferior
        self.EncaixosPar = EncaixosPar

        self.EncaixosAux = []

        self.matrixPosXAux = matrixPosXAux
        self.matrixPosYAux = matrixPosYAux

        self.teTDHoritzontal = teTDHoritzontal
        self.matrixPosTDH = matrixPosTDH

        self.m_TD_Vertical = None

        self.invertirPestanyes = invertirPestanyes


    def set_params_list(self, llistadeDades):

        self.BarraAmple = llistadeDades[0]
        self.BarraAltura = llistadeDades[1]
        self.BarraLlargada = llistadeDades[2]
        self.BarraGruix = llistadeDades[3]
        self.IsUseGlobalProp = llistadeDades[4]
        self.FounColor = llistadeDades[5]
        self.BarraLayer = llistadeDades[6]
        self.ColisPar = llistadeDades[7] #matriu
        self.PotaPar = llistadeDades[8] #matrius
        #self.ForatsPar = ForatsPar #matrius
        self.Ample_forat_femella = llistadeDades[9]
        self.Altura_forat_femella= llistadeDades[10]
        self.Separacio_forat_femella = llistadeDades[11]
        self.femelles = llistadeDades[12] #matriu
        self.posicio_centre_masses = llistadeDades[13]
        self.IsFirstCancam = llistadeDades[14]
        self.Dis1cancam = llistadeDades[15]
        self.IsSecondCancam = llistadeDades[16]
        self.Dis2cancam = llistadeDades[17]
        self.PestanyaSuperior = llistadeDades[18]
        self.PestanyaInferior = llistadeDades[19]
        self.EncaixosPar = llistadeDades[20]

        #Actualitzar Pos
        #afegr n barrres Interiors

    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """

        param_list = []
        param_list.append ("zUnique = %s\n" % self.zUnique)
        param_list.append ("BarraAmple = %s\n" % self.BarraAmple)
        param_list.append ("BarraAltura = %s\n" % self.BarraAltura)
        param_list.append ("BarraLlargada = %s\n" % self.BarraLlargada)
        param_list.append ("BarraGruix = %s\n" % self.BarraGruix)
        param_list.append ("IsUseGlobalProp = %s\n" % self.IsUseGlobalProp)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)
        param_list.append ("ColisPar = %s\n" % self.ColisPar)#matriu
        param_list.append ("PotaPar = %s\n" % self.PotaPar)#matriu
        param_list.append ("ForatsPar = %s\n" % self.ForatsPar)#matriu
        param_list.append ("Ample_forat_femella = %s\n" % self.Ample_forat_femella)
        param_list.append ("Altura_forat_femella = %s\n" % self.Altura_forat_femella)
        param_list.append ("Separacio_forat_femella = %s\n" % self.Separacio_forat_femella)
        param_list.append ("femelles = %s\n" % self.femelles)#matriu
        param_list.append ("posicio_centre_masses = %s\n" % self.posicio_centre_masses)
        param_list.append ("IsFirstCancam = %s\n" % self.IsFirstCancam)
        param_list.append ("Dis1cancam = %s\n" % self.Dis1cancam)
        param_list.append ("IsSecondCancam = %s\n" % self.IsSecondCancam)
        param_list.append ("Dis2cancam = %s\n" % self.Dis2cancam)
        param_list.append ("PestanyaSuperior = %s\n" % self.PestanyaSuperior)
        param_list.append ("PestanyaInferior = %s\n" % self.PestanyaInferior)
        param_list.append ("EncaixosPar = %s\n" % self.EncaixosPar)
        return param_list

    def __repr__(self):
        return 'PP_EN_Vertical(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s'\
            'BarraLayer=%s'\
            'ColisPar=%s, PotaPar=%s, ForatsPar=%s'\
            'Ample_forat_femella=%s, Altura_forat_femella=%s'\
            'Separacio_forat_femella=%s, femelles=%s'\
            'posicio_centre_masses=%s, IsFirstCancam=%s'\
            'Dis1cancam=%s, IsSecondCancam=%s'\
            'Dis2cancam=%s, PestanyaSuperior=%s'\
            'PestanyaInferior=%s, EncaixosPar=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer,
               self.ColisPar, self.PotaPar, self.ForatsPar,
               self.Ample_forat_femella, self.Altura_forat_femella,
               self.Separacio_forat_femella, self.femelles,
               self.posicio_centre_masses, self.IsFirstCancam,
               self.Dis1cancam, self.IsSecondCancam,
               self.Dis2cancam, self.PestanyaSuperior,
               self.PestanyaInferior, self.EncaixosPar )

    def hash (self):
        """
        Calculate hash value for script

        Returns:
            Hash string
        """
        param_string = self.__repr__()
        hash_val = hashlib.sha224(param_string.encode('utf-8')).hexdigest()
        return hash_val

    def filename(self):
        """
        Python script filename

        Returns:
            Script filename
        """
        return "TD_Vertical_PP.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.BarraAmple <= 0 or self.BarraAltura <= 0 or self.BarraLlargada <= 0 or self.BarraGruix <= 0:
            return False

        return True

    def get_ref_enc_llargada(self):
        return 0

    def get_codi_pestanyes(self):

        return self.codi_pestanyes

    def get_codi_cancam(self):

        return self.codi_cancam

    def get_codi_colis(self):

        return self.codi_colis

    def get_codi_encaix(self):

        return self.codi_encaix

    def get_codi_femella(self):
        return self.codi_femella

    def get_codi_mesures(self):

        return self.codi_mesures

    def get_seccio(self):

        if self.BarraAmple > self.BarraAltura:
            return str(self.BarraAmple) + "x " + str(self.BarraAltura) + "x " + str(self.BarraGruix)

        return str(self.BarraAltura) + "x " + str(self.BarraAmple) + "x " + str(self.BarraGruix)

    def get_llargada(self):

        return str(self.BarraLlargada)

    def get_codi_pota(self):

        return self.codi_pota

    def get_codi_pota_inv(self):

        return "#" + self.codi_pota_inv

    def get_codi_cara_a(self):

        return self.cara_a

    def get_codi_cara_a_inv(self):

        return "#" + self.cara_a_inv

    def get_codi_cara_b(self):

        return self.cara_b

    def get_codi_cara_b_inv(self):

        return "#" + self.cara_b_inv

    def get_codi_cara_c(self):

        return self.cara_c

    def get_codi_cara_c_inv(self):

        return "#" + self.cara_c_inv

    def get_codi_cara_d(self):

        return self.cara_d

    def get_codi_cara_d_inv(self):

        return "#" + self.cara_d_inv

    def volume(self):
        """
        Calculate the volume in m³

        Returns:
            Calculated volume
        """
        return 10
        err, volume, _, _ = AllplanGeo.CalcMass(self.m_TD_Vertical)
        if err:
            return 0.0
        return volume / 1000000000

    def afegir_encaixos_frontals(self, encaixos, listLong, PestanyaValue):
        #print("-----------")

        for nEncaixafegit in self.EncaixosPar:
            trobat = False
            i = 0
            nEncAfegir = 0
            while i < len(encaixos):
                iEncaix = encaixos[i]
                if nEncaixafegit.Encaix == iEncaix.BarraFront and nEncaixafegit.EncaixOr == iEncaix.Orientacio and nEncaixafegit.Posicio == iEncaix.Posicio and nEncaixafegit.Profunditat == iEncaix.Profunditat:
                    #print("actual: " + str(nEncaixafegit.Posicio))
                    #print("nou: " + str(iEncaix.Posicio))
                    nEncAfegir = i
                    trobat = True
                if nEncaixafegit.Posicio == iEncaix.Posicio and nEncaixafegit.Profunditat == iEncaix.Profunditat:
                    if nEncaixafegit.Encaix != iEncaix.BarraFront:
                        nEncaixafegit = nEncaixafegit._replace(Encaix = iEncaix.BarraFront)
                    if nEncaixafegit.EncaixOr != iEncaix.Orientacio:
                        nEncaixafegit = nEncaixafegit._replace(EncaixOr = iEncaix.Orientacio)
                    nEncAfegir = i
                    trobat = True
                i += 1

            if not trobat and len(encaixos)>0:
                iEncaix = encaixos[nEncAfegir]
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya Separator')
                femellaCollection = TDCollectionFemella(Encaix = iEncaix.BarraFront,
                                            EncaixOr = iEncaix.Orientacio,
                                            Longitud = iEncaix.Longitud, #30,#listLong[i],
                                            Posicio = iEncaix.Posicio,
                                            Profunditat = iEncaix.Profunditat,
                                            Pestanya = PestanyaValue,
                                            Separator='')

                self.EncaixosPar.append(femellaCollection)
                encaixos.pop(nEncAfegir)
                #print("encaix afegit: " + str(iEncaix.Posicio))

        #print("self.EncaixosPar")
        #print(self.EncaixosPar)

        '''
        self.EncaixosAux = []
        i = 0

        for iEncaix in encaixos:
            TDCollectionFemella = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya Separator')
            femellaCollection = TDCollectionFemella(Encaix = iEncaix.BarraFront,
                                            EncaixOr = iEncaix.Orientacio,
                                            Longitud = 30,#listLong[i],
                                            Posicio = iEncaix.Posicio,
                                            Profunditat = iEncaix.Profunditat,
                                            Pestanya = False,
                                            Separator='')

            self.EncaixosAux.append(femellaCollection)
            i+=1
        '''

    #femelles
    def actualitzar_femelles_TDH(self, listFemellesAnt ,listFemellesAct, nTDVAct, offsetY, offsetYAnt, crearFemellesxEncaixInf, desplInf, crearFemellesxEncaixSup, desplSup, separacioFemellaInf, separacioFemellaSup,separacioFemellaInt):
        #listFemellesAnt[0] = BarraHor
        #listFemellesAnt[1] = Posicio
        #listFemellesAnt[2] = Orientacio
        #listFemellesAnt[3] = AutoLongitud
        #listFemellesAnt[4] = Altura

        #if crearFemellesxEncaixInf:
        while len(self.femelles) <= 3:
            TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Separator')
            femellaCollection = TDCollectionFemella(Femella = True,
                                            FemellaOr = desplInf,
                                            PosFemellaX = 0,
                                            PosFemellaY = 0,
                                            Separacio_forat_femella = separacioFemellaInf,
                                            PosFemellaXOri = 0 ,
                                            Separator='')
            self.femelles.append(femellaCollection)
        else:
            self.femelles[3] = self.femelles[3]._replace(Femella = crearFemellesxEncaixInf)
            self.femelles[3] = self.femelles[3]._replace(FemellaOr = desplInf)
            self.femelles[3] = self.femelles[3]._replace(PosFemellaX = 0)
            self.femelles[3] = self.femelles[3]._replace(PosFemellaXOri = 0)
            self.femelles[3] = self.femelles[3]._replace(PosFemellaY = 0)
            self.femelles[3] = self.femelles[3]._replace(Separacio_forat_femella = separacioFemellaInf)

        if crearFemellesxEncaixSup:
            while len(self.femelles) <= 4:
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Separator')
                femellaCollection = TDCollectionFemella(Femella = True,
                                                FemellaOr = desplSup,
                                                PosFemellaX = self.BarraLlargada - separacioFemellaSup ,
                                                PosFemellaY = 0,
                                                Separacio_forat_femella = separacioFemellaSup,
                                                PosFemellaXOri = self.BarraLlargada -  separacioFemellaSup - self.BarraGruix*2,
                                                Separator='')
                self.femelles.append(femellaCollection)
            else:
                self.femelles[4] = self.femelles[4]._replace(Femella = True)
                self.femelles[4] = self.femelles[4]._replace(FemellaOr = desplSup)
                self.femelles[4] = self.femelles[4]._replace(PosFemellaX = self.BarraLlargada - separacioFemellaSup )
                self.femelles[4] = self.femelles[4]._replace(PosFemellaXOri = self.BarraLlargada -  separacioFemellaSup - self.BarraGruix*2)
                self.femelles[4] = self.femelles[4]._replace(PosFemellaY = 0)
                self.femelles[4] = self.femelles[4]._replace(Separacio_forat_femella = separacioFemellaSup)

        nTDV = 5

        #espaiCentrar = (self.BarraAmple - self.Altura_forat_femella)/2
        espaiCentrar = 0

        for y in range(len(listFemellesAnt)):
            #if nTDV + y + len(listFemellesAnt)  >= len(self.femelles):
            while nTDV + y + 1 >= len(self.femelles):
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Separator')
                femellaCollection = TDCollectionFemella(Femella = False,
                                                FemellaOr = "Sup",
                                                PosFemellaX = 400,
                                                PosFemellaY = offsetYAnt[y],
                                                Separacio_forat_femella = self.Separacio_forat_femella,
                                                PosFemellaXOri = 400,
                                                Separator='')
                self.femelles.append(femellaCollection)


            if len(listFemellesAnt) != 0 and y < len(listFemellesAnt):
                if nTDVAct != 0 and listFemellesAnt[y][3]:
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Femella = listFemellesAnt[y][0])
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(FemellaOr = 'Inf')
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaX = listFemellesAnt[y][1]  - listFemellesAnt[y][4]/2 + espaiCentrar)
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaXOri = listFemellesAnt[y][1] + espaiCentrar)
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaY = offsetYAnt[y])
                    self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Separacio_forat_femella = listFemellesAnt[y][4])
        for y in range(len(listFemellesAct)):

            #if offsetY[y] != 0:
            #    offsetY[y] = (self.BarraAmple/2 - self.Ample_forat_femella/2) + offsetY[y]
            #offsetY[y] = offsetY[y]

            offset = len(listFemellesAnt)
            #if nTDV + y + len(listFemellesAnt)  >= len(self.femelles):
            while nTDV + offset + y + 1 >= len(self.femelles):
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Separator')
                femellaCollection = TDCollectionFemella(Femella = False,
                                                FemellaOr = "Sup",
                                                PosFemellaX = 400,
                                                PosFemellaY = offsetY[y],
                                                Separacio_forat_femella = self.Separacio_forat_femella,
                                                PosFemellaXOri = 400,
                                                Separator='')
                self.femelles.append(femellaCollection)

            #if len(listFemellesAnt) != 0 and y < len(listFemellesAnt):
            #    if nTDVAct != 0 and listFemellesAnt[y][3]:
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Femella = listFemellesAnt[y][0])
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(FemellaOr = 'Inf')
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaX = listFemellesAnt[y][1]  - listFemellesAnt[y][4]/2 + espaiCentrar)
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaXOri = listFemellesAnt[y][1] + espaiCentrar)
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaY = offsetYAnt[y])
            #        self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Separacio_forat_femella = listFemellesAnt[y][4])

            if nTDVAct < len(self.femelles):
                #if listFemellesAnt[y][0] == 'Inf':
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Femella = listFemellesAct[y][0])
                if listFemellesAct[y][3]:
                    self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(FemellaOr = 'Sup')
                else:
                    self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(FemellaOr = listFemellesAct[y][2])
                #else:
                    #self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Femella = False)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaX = listFemellesAct[y][1] - listFemellesAct[y][4]/2 + espaiCentrar)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaXOri = listFemellesAct[y][1] + espaiCentrar)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaY = offsetY[y])
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Separacio_forat_femella = listFemellesAct[y][4])

                    #self.femelles[x+3] = self.femelles[x+3]._replace(Posfemella = matrixPOSH[nTDV]*1000 + espaiCentrar)
            #else:
                #self.femelles[i] = self.femelles[i]._replace(Femella = False)

        return self.femelles
    #--------------------------
    #femelles
    def actualitzar_femelles_ENH(self, listFemellesAnt ,listFemellesAct, nTDVAct, offsetY, offsetYAnt, crearFemellesxEncaixInf, desplInf, crearFemellesxEncaixSup, desplSup, separacioFemellaInf, separacioFemellaSup,separacioFemellaInt):
        #listFemellesAnt[0] = BarraHor
        #listFemellesAnt[1] = Posicio
        #listFemellesAnt[2] = Orientacio
        #listFemellesAnt[3] = AutoLongitud
        #listFemellesAnt[4] = Altura
        #listFemellesAnt[5] = AmpleForatFem
        #listFemellesAnt[6] = tubGirat
        #listFemellesAnt[7] = Ample



        if crearFemellesxEncaixInf:
            while len(self.femelles) <= 3:
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Altura_forat_femella tubGirat Separator')
                femellaCollection = TDCollectionFemella(Femella = True,
                                                FemellaOr = desplInf,
                                                PosFemellaX = 0,
                                                PosFemellaY = 0,
                                                Separacio_forat_femella = separacioFemellaInf,
                                                PosFemellaXOri = 0 ,
                                                Ample_forat_femella = 0,
                                                Altura_forat_femella = 0,
                                                tubGirat = False,
                                                Separator='')
                self.femelles.append(femellaCollection)
            else:
                self.femelles[3] = self.femelles[3]._replace(Femella = True)
                self.femelles[3] = self.femelles[3]._replace(FemellaOr = desplInf)
                self.femelles[3] = self.femelles[3]._replace(PosFemellaX = 0)
                self.femelles[3] = self.femelles[3]._replace(PosFemellaXOri = 0)
                self.femelles[3] = self.femelles[3]._replace(PosFemellaY = 0)
                self.femelles[3] = self.femelles[3]._replace(Separacio_forat_femella = separacioFemellaInf)
                self.femelles[3] = self.femelles[3]._replace(Ample_forat_femella = 0)
                self.femelles[3] = self.femelles[3]._replace(Altura_forat_femella = 0)
                self.femelles[3] = self.femelles[3]._replace(tubGirat = False)

        if crearFemellesxEncaixSup:
            while len(self.femelles) <= 4:
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Altura_forat_femella tubGirat Separator')
                femellaCollection = TDCollectionFemella(Femella = True,
                                                FemellaOr = desplSup,
                                                PosFemellaX = self.BarraLlargada - separacioFemellaSup ,
                                                PosFemellaY = 0,
                                                Separacio_forat_femella = separacioFemellaSup,
                                                PosFemellaXOri = self.BarraLlargada -  separacioFemellaSup - self.BarraGruix*2,
                                                Ample_forat_femella = 0,
                                                Altura_forat_femella = 0,
                                                tubGirat = False,
                                                Separator='')
                self.femelles.append(femellaCollection)
            else:
                self.femelles[4] = self.femelles[4]._replace(Femella = True)
                self.femelles[4] = self.femelles[4]._replace(FemellaOr = desplSup)
                self.femelles[4] = self.femelles[4]._replace(PosFemellaX = self.BarraLlargada - separacioFemellaSup )
                self.femelles[4] = self.femelles[4]._replace(PosFemellaXOri = self.BarraLlargada -  separacioFemellaSup - self.BarraGruix*2)
                self.femelles[4] = self.femelles[4]._replace(PosFemellaY = 0)
                self.femelles[4] = self.femelles[4]._replace(Separacio_forat_femella = separacioFemellaSup)
                self.femelles[4] = self.femelles[4]._replace(Ample_forat_femella = 0)
                self.femelles[4] = self.femelles[4]._replace(Altura_forat_femella = 0)
                self.femelles[4] = self.femelles[4]._replace(tubGirat = False)

        nTDV = 5

        #espaiCentrar = (self.BarraAmple - self.Altura_forat_femella)/2
        espaiCentrar = 0

        for y in range(len(listFemellesAnt)):

            #if offsetY[y] != 0:
            #    offsetY[y] = (self.BarraAmple/2 - self.Ample_forat_femella/2) + offsetY[y]
            #offsetY[y] = offsetY[y]

            offset = len(listFemellesAnt)
            #if nTDV + y + len(listFemellesAnt)  >= len(self.femelles):
            while nTDV + offset + y + 1 >= len(self.femelles):
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Altura_forat_femella tubGirat Separator')
                femellaCollection = TDCollectionFemella(Femella = False,
                                                FemellaOr = "Sup",
                                                PosFemellaX = 400,
                                                PosFemellaY = 15,
                                                Separacio_forat_femella = self.Separacio_forat_femella,
                                                PosFemellaXOri = 400,
                                                Ample_forat_femella = 0,
                                                Altura_forat_femella = 0,
                                                tubGirat = False,
                                                Separator='')
                self.femelles.append(femellaCollection)


            if nTDVAct != 0 and listFemellesAnt[y][3]:
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Femella = listFemellesAnt[y][0])
                #self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(FemellaOr = 'Inf')
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(FemellaOr = listFemellesAnt[y][2])
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaX = listFemellesAnt[y][1]  - listFemellesAnt[y][4]/2 + espaiCentrar)
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaXOri = listFemellesAnt[y][1] + espaiCentrar)
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(PosFemellaY = offsetYAnt[y])
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Separacio_forat_femella = listFemellesAnt[y][7])
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Ample_forat_femella = listFemellesAnt[y][5])
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(Altura_forat_femella = 2)
                self.femelles[nTDV + y] = self.femelles[nTDV + y]._replace(tubGirat = listFemellesAnt[y][6])

        for y in range(len(listFemellesAct)):
            offset = len(listFemellesAnt)

            #if nTDV + y + len(listFemellesAnt)  >= len(self.femelles):
            while nTDV + offset + y + 1 >= len(self.femelles):
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella PosFemellaXOri Ample_forat_femella Altura_forat_femella tubGirat Separator')
                femellaCollection = TDCollectionFemella(Femella = False,
                                                FemellaOr = "Sup",
                                                PosFemellaX = 400,
                                                PosFemellaY = 15,
                                                Separacio_forat_femella = self.Separacio_forat_femella,
                                                PosFemellaXOri = 0,
                                                Ample_forat_femella = 0,
                                                Altura_forat_femella = 0,
                                                tubGirat = False,
                                                Separator='')
                self.femelles.append(femellaCollection)

            if nTDVAct < len(self.femelles):
                #if listFemellesAnt[y][0] == 'Inf':
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Femella = listFemellesAct[y][0])
                #if listFemellesAct[y][3]:
                #    self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(FemellaOr = 'Sup')
                #else:
                #    self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(FemellaOr = listFemellesAct[y][2])
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(FemellaOr = listFemellesAct[y][2])
                #else:
                    #self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Femella = False)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaX = listFemellesAct[y][1] - listFemellesAct[y][4]/2 + espaiCentrar)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaXOri = listFemellesAct[y][1] + espaiCentrar)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(PosFemellaY = offsetY[y])
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Separacio_forat_femella = listFemellesAct[y][7])
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Ample_forat_femella = listFemellesAct[y][5])
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(Altura_forat_femella = 2)
                self.femelles[nTDV + offset + y] = self.femelles[nTDV + offset + y]._replace(tubGirat = listFemellesAct[y][6])

                    #self.femelles[x+3] = self.femelles[x+3]._replace(Posfemella = matrixPOSH[nTDV]*1000 + espaiCentrar)
            #else:
                #self.femelles[i] = self.femelles[i]._replace(Femella = False)

        return self.femelles
    #--------------------------

    def create_PP_positions_femelles(self, ampleTDV, alturaTDV, matrixPosX, matrixPosY, matrixMostrar, offsetX, orientacio, Ample_forat_femellaVert, barraLlargadaReal, offsetHor,FemellesAux = [], desplXI = 0):
        pass


    def set_false_encaix(self):
        for i in range(2,len(self.EncaixosPar)):
            self.EncaixosPar[i] = self.EncaixosPar[i]._replace(Encaix = False)

    def set_false_femelles(self):
        for i in range(0,len(self.femelles)):
            self.femelles[i] = self.femelles[i]._replace(Femella = False)

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(self.BarraAmple, self.BarraAltura, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraAmple", HandleDirection.x_dir),
                                         ("BarraAltura", HandleDirection.y_dir)],
                                        HandleDirection.xy_dir),
                                        HandleProperties("BarraLlargada",
                                        AllplanGeo.Point3D(0, 0, self.BarraLlargada),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraLlargada", HandleDirection.z_dir)],
                                        HandleDirection.z_dir)
                      ]

        return handle_list

    def getTDType(self) :
        return "Vertical"

    def get_common_props(self):

        common_prop = self.get_foundation_common_props()
        return common_prop

    def create_TD_positions(self, DistanciaEntreTD, matrixPosX, matrixPosY, nTDs):
        """
        Create a list of transformations to position all chairs around the table

        Returns:
            List of Matrix3D transformations
        """

        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = DistanciaEntreTD

        trans_list = list()



        #------------------ Create the chairs for the front

        rotation_angle = AllplanGeo.Angle()
        rotation_angle.SetDeg(180)
        rotation_matrix = AllplanGeo.Matrix3D()
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                   AllplanGeo.Point3D(0, 0, 0)),
                                 rotation_angle)

        rotation_angle.SetDeg(90)

        rotation_matrix = AllplanGeo.Matrix3D()

        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                   AllplanGeo.Point3D(0, 0, 1000)),
                                 rotation_angle)

        rotation_angle.SetDeg(-90)

        rotation_matrix1 = AllplanGeo.Matrix3D()

        rotation_matrix1.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                    AllplanGeo.Point3D(0, 0, 1000)),
                                  rotation_angle)


        #------------------ Add the chair at the left and right table

        #chair_count = int(self.BarraLlargada / nTDs)
        chair_count = nTDs

        if chair_count > 0:
            seat_size_real = self.BarraAmple / chair_count

            deltay = (seat_size_real - DistanciaEntreTD) / 2.

            for _ in range(chair_count):
                trans_matrix = AllplanGeo.Matrix3D(rotation_matrix)
                trans_matrix.Translate(AllplanGeo.Vector3D(0, deltay, 0))

                trans_list.append(trans_matrix)

                deltay += seat_size_real

        return trans_list


#-------------------CREAR BARRA --------------+
    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''
        #print("Create model TD 1")
        #
        self.amplada_femella = self.Ample_forat_femella
        self.alcada_femella = self.Altura_forat_femella
        self.llargada_femella = self.Ample_forat_femella

        #codis:
        ref_enc_llargada = 0.00
        self.codi_pestanyes = "#Z:@"+str(ref_enc_llargada)+"@#"
        self.codi_cancam = "#"
        self.codi_colis = "#"
        self.codi_encaix = "#"
        self.codi_femella = "#"
        #if self.BarraAmple > self.BarraAltura:
        self.codi_mesures = "#X:@"+str(self.BarraAmple)+"Y:@"+str(self.BarraAltura)+"@|Z:@" +str(self.BarraLlargada)+"@|T:@"+str(self.BarraGruix)+"@#"
        #else:
        #    self.codi_mesures = "#X:@"+str(self.BarraAltura)+"Y:@"+str(self.BarraAmple)+"@|Z:@" +str(self.BarraLlargada)+"@|T:@"+str(self.BarraGruix)+"@#"
        #self.codi_mesures = "#X:@"+str(self.BarraAmple)+"Y:@"+str(self.BarraAltura)+"@|Z:@" +str(self.BarraLlargada)+"@|T:@"+str(self.BarraGruix)+"@#"
        self.codi_pota = "#"

        self.cara_a = "#" #Esq
        self.cara_b = "#" #Dre
        self.cara_c = "#" #Sup
        self.cara_d = "#" #Inf

        self.cara_a_inv = "" #Esq Invertida
        self.cara_b_inv = "" #Dre Invertida
        self.cara_c_inv = "" #Sup Invertida
        self.cara_d_inv = "" #Inf Invertida

        self.codi_pota_inv = "" #Potes Invertides

        elements = []
        ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        barra = ele1

        #cub vermell per orientar el costat inferior
        ind_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.BarraAltura, self.BarraGruix)
        common_prop = AllplanBaseElements.CommonProperties()
        common_prop.Color = 6 #Vermell
        vector = AllplanGeo.Vector3D(-10, 0, 0)
        ind_inf = AllplanGeo.Move(ind_inf, vector)
        #elements.append(AllplanBasisElements.ModelElement3D(common_prop, ind_inf))


        #Encaixos
        #ordenar

        #print("Encaixos NO ordenats")
        #print(self.EncaixosPar)
        for i in range(len(self.EncaixosPar)):
            lowest_value_index = i
            for j in range(i+1,len(self.EncaixosPar)):
                if self.EncaixosPar[i].Posicio < self.EncaixosPar[j].Posicio:
                    lowest_value_index = j
            self.EncaixosPar[i], self.EncaixosPar[lowest_value_index] = self.EncaixosPar[lowest_value_index], self.EncaixosPar[i]
        #print("Encaixos ordenats")
        #print(self.EncaixosPar)


        dades_encaix = self.EncaixosPar
        i = 0
        auxIencaix = []
        auxIencaixBool = False
        for Iencaix in dades_encaix:
            if Iencaix == 0 or auxIencaixBool ==True:
                auxIencaix.append(Iencaix)
                auxIencaixBool = True
            else:
                EncaixActiu = Iencaix[0]
                if EncaixActiu:
                    ele2 = self.create_encaix(i)
                    barra = AllplanGeo.MakeBoolean(barra, ele2)
                    barra = barra[3]#forat
            i += 1
        '''
        #EncaixosAux
        i = 0
        dades_encaixAux = self.EncaixosAux
        print("dades_encaix: ")
        print(dades_encaix)
        for Iencaix in dades_encaixAux:
            EncaixActiu = Iencaix[0]
            if EncaixActiu:
                ele2 = self.create_encaix_Aux(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]#forat
            i += 1
        '''
        #Pestanya Superior
        if self.PestanyaSuperior:
            ele2 = self.create_pestanyes_sup()
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[2]#unio
        #Pestanya Inferior
        if self.PestanyaInferior:
            ele2 = self.create_pestanyes_inf()
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[2]
        #Cancams
        if self.IsFirstCancam or self.IsSecondCancam:
            ele2 = self.create_cancams()
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[3]
        #femelles
        dades_femella = self.femelles
        i = 0
        self.codi_femella += "S:@"+str(self.Separacio_forat_femella)+"@|L:@"+str(self.Altura_forat_femella)+"@|M:@"+str(self.Ample_forat_femella)+"@#"
        for Ifemella in dades_femella:
            femellaActiva = Ifemella[0]
            if femellaActiva:
                ele2 = self.create_femelles( i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]
            i += 1
        #colis
        dades_colis = self.ColisPar
        i = 0
        for Icolis in dades_colis:
            colisActiu = Icolis[0]
            if colisActiu:
                ele3 = self.create_colis_int(i)
                barra = AllplanGeo.MakeBoolean(barra, ele3)
                barra = barra[3]#Forat
                #ele2 = self.create_colis(i)
                #barra = AllplanGeo.MakeBoolean(barra, ele2)
                #barra = barra[2]#Colis
            i += 1
        #potes
        dades_Potes = self.PotaPar
        i = 0
        for IPotes in dades_Potes:
            potaActiu = IPotes[0]
            if potaActiu:
                ele2 = self.create_pota(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]
            i += 1

        #Forats
        dades_Forats = self.ForatsPar
        i = 0
        for iForat in dades_Forats:
            foratActiu = iForat.Forat
            if foratActiu:
                ele2 = self.create_forats(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]
            i += 1

        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]
        self.m_TD_Vertical = barra


        elements.append(AllplanBasisElements.ModelElement3D(common_prop, barra))

        #------------------------
        pyp_util = PythonPartUtil()

        #self.model_ele_list = BuildingElementAttributeList()

        #Atributs
        attribute_list = BuildingElementAttributeList()

        #codi_pestanyes
        attribute_list.add_attribute(2430, self.codi_pestanyes)
        #codi_cancam
        attribute_list.add_attribute(2435, self.codi_cancam)
        #codi_colis
        attribute_list.add_attribute(2432, self.codi_colis)
        #codi_encaix
        attribute_list.add_attribute(2429, self.codi_encaix)
        #codi_femella
        attribute_list.add_attribute(2434, self.codi_femella)
        #codi_mesures
        attribute_list.add_attribute(2431, self.codi_mesures)
        #codi_pota
        attribute_list.add_attribute(2433, self.codi_pota)

        pyp_util.add_attribute_list(attribute_list)


        pyp_util.add_pythonpart_view_2d3d(elements)
        #------------------------
        #print("self.codi_femella: " + str(self.codi_femella))
        #print("ESQ - self.cara_a: " + self.cara_a)
        #print("self.cara_a_inv: " + self.cara_a_inv)
        #print("DRE - self.cara_b: " + self.cara_b)
        #print("self.cara_b_inv: " + self.cara_b_inv)
        #print("SUP - self.cara_c: " + self.cara_c)
        #print("self.cara_c_inv: " + self.cara_c_inv)
        #print("INF - self.cara_d: " + self.cara_d)
        #print("self.cara_d_inv: " + self.cara_d_inv)


        return barra

    def create_identificador(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''
        #cub vermell per orientar el costat inferior
        ind_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.BarraAltura, self.BarraGruix)
        common_prop = AllplanBaseElements.CommonProperties()
        common_prop.Color = 6 #Vermell
        #vector = AllplanGeo.Vector3D(0, 0, 0)
        #ind_inf = AllplanGeo.Move(ind_inf, vector)

        return ind_inf

    #BARRA
    def create_barra(self):
        '''
        Es crea dos cuboids, un amb l'ample, altura i llargada indicada, i el segon igual menys el gruix indicat,
        es fauna operació bool i es retorna el model coincident.

        return: Polyhedron3D
        '''
        #creació cuboid exterior
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAmple, self.BarraAltura, self.BarraLlargada)
        #crear cuboid interior
        if self.BarraGruix != 0:
            geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple - self.BarraGruix*2,
                                                        self.BarraAltura - self.BarraGruix*2,
                                                        self.BarraLlargada)
                                                        #self.BarraLlargada - self.BarraGruix*2)

        #es crea el vector per posicionarlo al centre i es resten els volums
            vector = AllplanGeo.Vector3D(self.BarraGruix, self.BarraGruix, 0)
            geometry2 = AllplanGeo.Move(geometry2, vector)

        if self.BarraGruix*2 < self.BarraAmple and self.BarraGruix*2 < self.BarraAltura and self.BarraGruix != 0:
            geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)
            geometry = geometry[3]
        else:
            geometry = geometry1

        return geometry

    #COLIS
    def create_colis(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_forat_alc = 3

        self.codi_colis += "["+str(num_colis+1)+"]C:@"+str(orientacio)+"@|P:@"+str(posColis)+"@#"

        #colis gruix 0.00900

        if orientacio == 'Inf' or orientacio == 'Sup':
            if orientacio == 'Inf':
                self.cara_d += "COL|P:@"+str(posColis)+"@#"
                posInv = self.BarraLlargada-posColis
                self.cara_d_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_d_inv
            else:
                self.cara_c += "COL|P:@"+str(posColis)+"@#"
                posInv = self.BarraLlargada-posColis
                self.cara_c_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_c_inv
            colis = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple, colis_forat_alc, colis_alc )
            #colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple - self.BarraGruix*4, colis_forat_alc, colis_alc-self.BarraGruix*2)
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_ampl, colis_forat_alc, colis_alc)
        else:
            if orientacio == 'Esq':
                self.cara_a += "COL|P:@"+str(posColis)+"@#"
                posInv = self.BarraLlargada-posColis
                self.cara_a_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_a_inv
            else:
                self.cara_b += "COL|P:@"+str(posColis)+"@#"
                posInv = self.BarraLlargada-posColis
                self.cara_b_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_b_inv
            colis = AllplanGeo.Polyhedron3D.CreateCuboid(colis_forat_alc, self.BarraAltura, colis_alc )
            #colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_forat_alc, self.BarraAmple - self.BarraGruix*4, colis_alc-self.BarraGruix*2)
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_forat_alc, colis_ampl, colis_alc)
        vector = self.vector_colis_int_bool(num_colis)
        colis_int = AllplanGeo.Move(colis_int, vector)

        vector = self.vector_colis(num_colis)
        colis = AllplanGeo.Move(colis, vector)

        colis = AllplanGeo.MakeBoolean(colis, colis_int)
        colis = colis[3]

        return colis

    def vector_colis(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_alcada = 3
        vector = AllplanGeo.Vector3D(0,0,0)

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D( 0, -colis_alcada,posColis - (colis_alc/2) )
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(-colis_alcada, 0, posColis - (colis_alc/2))
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(0,self.BarraAltura, posColis - (colis_alc/2))
        else:
            vector = AllplanGeo.Vector3D(self.BarraAmple , 0, posColis - (colis_alc/2))

        return vector

    def vector_colis_int_bool(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_alcada = 3
        vector = AllplanGeo.Vector3D(0,0,0)
        colis_int = AllplanGeo.Polyhedron3D.CreateCuboid( colis_alcada, self.BarraAmple - self.BarraGruix*4, colis_alc-self.BarraGruix*2)

        if orientacio == 'Inf':
            #vector = AllplanGeo.Vector3D( self.BarraGruix*2, -colis_alcada , posColis + self.BarraGruix)
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - colis_ampl/2, -colis_alcada , posColis - colis_alc/2)
        elif orientacio == 'Dre':
            #vector = AllplanGeo.Vector3D(-colis_alcada, self.BarraGruix*2,  posColis + self.BarraGruix )
            vector = AllplanGeo.Vector3D(-colis_alcada, self.BarraAltura/2 - colis_ampl/2,  posColis - colis_alc/2)
        elif orientacio == 'Sup':
            #vector = AllplanGeo.Vector3D( self.BarraGruix*2 , self.BarraAmple , posColis + self.BarraGruix)
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - colis_ampl/2 , self.BarraAltura , posColis - colis_alc/2)
        else :
            #vector = AllplanGeo.Vector3D(self.BarraAmple , self.BarraGruix*2,  posColis + self.BarraGruix )
            vector = AllplanGeo.Vector3D(self.BarraAmple , self.BarraAltura/2 - colis_ampl/2,  posColis - colis_alc/2)

        return vector


    def create_colis_int(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_forat_alc = 3

        if orientacio == 'Inf' or orientacio == 'Sup':
            #colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple - self.BarraGruix*4, self.BarraGruix, colis_alc-self.BarraGruix*2)
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_ampl, self.BarraGruix, colis_alc)
        else:
            #colis_int = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.BarraAmple - self.BarraGruix*4, colis_alc-self.BarraGruix*2)
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, colis_ampl, colis_alc)
        vector = self.vector_colis_int(num_colis)
        colis_int = AllplanGeo.Move(colis_int, vector)

        return colis_int

    def vector_colis_int(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_alcada = 3
        vector = AllplanGeo.Vector3D(0,0,0)

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(self.BarraAmple/2 - colis_ampl/2, 0, posColis - colis_alc/2)
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(0, self.BarraAltura/2 - colis_ampl/2,  posColis - colis_alc/2)
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(self.BarraAmple/2 - colis_ampl/2, self.BarraAltura - self.BarraGruix, posColis - colis_alc/2)
        else:
            vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - colis_ampl/2, posColis - colis_alc/2)

        return vector

    #POTA
    def create_pota(self, num_pota):
        dades_pota = self.PotaPar
        DPota = dades_pota[num_pota]

        posPota = DPota[1]

        #self.codi_pota += "["+str(num_pota+1)+"]P:@"+str(posPota) + "@#"
        self.codi_pota += "P:@"+str(posPota) + "@#"
        potaInv = self.BarraLlargada - posPota
        self.codi_pota_inv = "P:@"+str(potaInv) + "@#" + self.codi_pota_inv

        pota_alc = 13
        pota_ample = 13

        pota = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAmple ,pota_ample, pota_alc)
        vector = AllplanGeo.Vector3D( 0, self.BarraAltura/2-pota_ample/2 ,posPota - pota_ample/2)

        pota = AllplanGeo.Move(pota, vector)

        return pota

    def create_forats(self, num_forat):
        dades_forats = self.ForatsPar
        DForats = dades_forats[num_forat]

        orientacio = DForats.orientacio
        posForat = DForats.Posicio
        forat_alc = DForats.Llargada
        forat_ampl = DForats.Amplada
        esCompleta = DForats.Complet
        forat_alcB = DForats.LlargadaB
        forat_amplB = DForats.AmpladaB

        altura = self.BarraGruix
        #if esCompleta and (orientacio == 'Sup' or orientacio == 'Inf'):
        #    altura = self.BarraAltura
        #elif esCompleta and (orientacio == 'Esq' or orientacio == 'Dre'):
        #    altura = self.BarraAmple
        #else:
        #    altura = self.BarraGruix


        if orientacio == 'Inf' or orientacio == 'Sup':
            #forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(altura, forat_alc, forat_ampl)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_ampl, altura, forat_alc)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid(forat_amplB, altura, forat_alcB)

        else:
            #forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alc, altura, forat_ampl)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid( altura, forat_ampl, forat_alc)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid( altura, forat_amplB, forat_alcB)

        vector, vectorB= self.vector_forats_int(num_forat)

        if esCompleta:
            forat_int = AllplanGeo.Move(forat_int, vector)
            forat_intB = AllplanGeo.Move(forat_intB, vectorB)
            forat_intC = AllplanGeo.MakeBoolean(forat_int, forat_intB)
            forat_int = forat_intC[2]
        else:
            forat_int = AllplanGeo.Move(forat_int, vector)

        return forat_int

    def vector_forats_int(self, num_forat):
        dades_forat = self.ForatsPar
        Dforat = dades_forat[num_forat]

        orientacio = Dforat.orientacio
        posForat = Dforat.Posicio
        forat_alc = Dforat.Llargada
        forat_ampl = Dforat.Amplada
        esCompleta = Dforat.Complet
        forat_alcB = Dforat.LlargadaB
        forat_amplB = Dforat.AmpladaB

        vector = AllplanGeo.Vector3D(0,0,0)
        vectorB = AllplanGeo.Vector3D(0,0,0)

        codi1 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"#"
        codi2 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"#"
        posinv = self.BarraLlargada - posForat
        codi_inv1 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"#"
        codi_inv2 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"#"

        if orientacio == 'Inf' :#or (orientacio == 'Sup' and esCompleta):#V
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_ampl/2, 0 , posForat - forat_alc/2)
            vectorB = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_amplB/2 , self.BarraAltura  - self.BarraGruix , posForat - forat_alcB/2)
            self.cara_d += codi1
            self.cara_d_inv += codi_inv1
            self.cara_c += codi2
            self.cara_c_inv += codi_inv2
        elif orientacio == 'Dre' :#or (orientacio == 'Esq' and esCompleta):#v
            vector = AllplanGeo.Vector3D(0, self.BarraAltura/2 - forat_ampl/2,  posForat - forat_alc/2)
            vectorB = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix , self.BarraAltura/2 - forat_amplB/2,  posForat - forat_alcB/2)
            self.cara_b += codi1
            self.cara_b_inv += codi_inv1
            self.cara_a += codi2
            self.cara_a_inv += codi_inv2
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_ampl/2 , self.BarraAltura  - self.BarraGruix , posForat - forat_alc/2)
            vectorB = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_amplB/2, 0 , posForat - forat_alcB/2)
            self.cara_c += codi1
            self.cara_c_inv += codi_inv1
            self.cara_d += codi2
            self.cara_d_inv += codi_inv2
        else:
            vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix , self.BarraAltura/2 - forat_ampl/2,  posForat - forat_alc/2)
            vectorB = AllplanGeo.Vector3D(0, self.BarraAltura/2 - forat_amplB/2,  posForat - forat_alcB/2)
            self.cara_a += codi1
            self.cara_a_inv += codi_inv1
            self.cara_b += codi2
            self.cara_b_inv += codi_inv2
        return vector, vectorB

    #femelles
    '''
    def create_femelles(self, nFemella):
        dades_femelles = self.femelles
        Dfemella = dades_femelles[nFemella]

        posicio = Dfemella[1]
        PosFemellaX = Dfemella[2]

        if Dfemella[4] != 0:
            Separacio_forat_femella = Dfemella[4] - self.Altura_forat_femella *2 + 0.5
        else:
            Separacio_forat_femella = self.Separacio_forat_femella + 0.5


        if Dfemella[3] != 0:
            PosFemellaY = Dfemella[3]
            ample_forat_fem = self.Ample_forat_femella
        else:
            if posicio == "Dre" or posicio == "Esq":
                PosFemellaY = self.BarraAmple/2 - self.Ample_forat_femella/2
            else:
                PosFemellaY = self.BarraAltura/2 - self.Ample_forat_femella/2

            ample_forat_fem = self.Ample_forat_femella

        PosFemellaX -= 0.25
        PosFemellaY -= 0.25

        self.codi_femella += "C:@"+str(posicio)+"@|P:@"+str(PosFemellaX)+"@#"


        posinv = self.BarraLlargada - PosFemellaX
        if Dfemella.PosFemellaXOri:
            posinv = self.BarraLlargada - Dfemella.PosFemellaXOri
            PosOriginal = Dfemella.PosFemellaXOri
        else:
            PosOriginal = PosFemellaX





        #crear 2 cubs
        femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella + 0.5 ,3.1, self.Altura_forat_femella)

        #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
        vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX )
        femella_12 = AllplanGeo.Move(femella_1, vector)
        #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
        vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX  + Separacio_forat_femella + self.Altura_forat_femella)
        femella_11 = AllplanGeo.Move(femella_1, vector)

        femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

        if posicio == "Dre":
            self.cara_b += "FEM@|P:@"+str(PosOriginal)+"@#"
            self.cara_b_inv = "FEM@|P:@"+str(posinv)+"@#" + self.cara_b_inv
            femella = femella[2]
            return femella

        elif posicio == "Sup":
            self.cara_c += "FEM@|P:@"+str(PosOriginal)+"@#"
            self.cara_c_inv = "FEM@|P:@"+str(posinv)+"@#" + self.cara_c_inv
            #crear 2 cubs
            #femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella  ,self.BarraGruix, self.Altura_forat_femella)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,self.Ample_forat_femella + 0.5 , self.Altura_forat_femella)

            #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaY , 0, PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
            vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX  + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)
            #orientar Sup

            axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(0,0,1))
            #Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
            Angle = AllplanGeo.Angle.FromDeg(90)
            femella_sup = AllplanGeo.Rotate(femella[2],axis_point, Angle)
            vector = AllplanGeo.Vector3D(self.BarraAmple , 0, 0)
            femella_sup = AllplanGeo.Move(femella_sup,vector)

            return femella_sup

        elif posicio == "Esq":
            self.cara_a += "FEM@|P:@"+str(PosOriginal)+"@#"
            self.cara_a_inv = "FEM@|P:@"+str(posinv)+"@#" + self.cara_a_inv
            #orientar Esq
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella + 0.5  ,3.1, self.Altura_forat_femella)

            vector = AllplanGeo.Vector3D( PosFemellaY , self.BarraAltura- self.BarraGruix, PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            vector = AllplanGeo.Vector3D( PosFemellaY , self.BarraAltura- self.BarraGruix, PosFemellaX + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)

            femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

            return femella [2]

        elif posicio == "Inf":
            self.cara_d += "FEM@|P:@"+str(PosOriginal)+"@#"
            self.cara_d_inv = "FEM@|P:@"+str(posinv)+"@#" + self.cara_d_inv
            #orientar Inf
            #femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella , self.Ample_forat_femella ,self.BarraGruix)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,self.Ample_forat_femella + 0.5 , self.Altura_forat_femella)

            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura - self.BarraGruix, PosFemellaX )
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.amplada_femella/2, self.BarraAltura/2 - self.llargada_femella/2 - self.BarraGruix , PosFemellaX )
            vector = AllplanGeo.Vector3D(0, PosFemellaY , PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix , PosFemellaX )
            vector = AllplanGeo.Vector3D(0, PosFemellaY, PosFemellaX + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)

            femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

            return femella[2]

        else:
            femella = femella[2]

        return femella
    '''

    def create_femelles(self, nFemella):
        dades_femelles = self.femelles
        Dfemella = dades_femelles[nFemella]

        posicio = Dfemella[1]
        PosFemellaX = Dfemella[2]

        ample_forat_fem = 2


        femellesInv = False
        if hasattr(Dfemella, "tubGirat"):
            femellesInv = Dfemella.tubGirat

        if Dfemella[4] != 0:
            Separacio_forat_femella = Dfemella[4] - self.Altura_forat_femella *2 + 0.5
        else:
            Separacio_forat_femella = self.Separacio_forat_femella + 0.5


        if Dfemella.Ample_forat_femella == 0:
            ample_forat_fem = self.Ample_forat_femella
        else:
            ample_forat_fem = Dfemella.Ample_forat_femella
        #print("Dfemella.Ample_forat_femella: " + str(Dfemella.Ample_forat_femella))


        if Dfemella[3] != 0:
            if not femellesInv:
                PosFemellaY = Dfemella[3]
            else:
                PosFemellaY = Dfemella.PosFemellaY
            #ample_forat_fem = self.Ample_forat_femella
            #ample_forat_fem = self.BarraAmple/2
        else:
            if not femellesInv:
                if posicio == "Dre" or posicio == "Esq":
                    PosFemellaY = self.BarraAmple/2 - ample_forat_fem/2
                else:
                    PosFemellaY = self.BarraAltura/2 - ample_forat_fem/2
            else:
                PosFemellaY = 0

            #ample_forat_fem = self.BarraAmple/2
            ample_forat_fem = self.Ample_forat_femella



        PosFemellaX -= 0.25
        PosFemellaY -= 0.25

        self.codi_femella += "C:@"+str(posicio)+"@|P:@"+str(PosFemellaX)+"|Y:@"+str(PosFemellaY)+"@#"


        posinv = self.BarraLlargada - PosFemellaX
        if Dfemella.PosFemellaXOri:
            posinv = self.BarraLlargada - Dfemella.PosFemellaXOri
            PosOriginal = Dfemella.PosFemellaXOri
        else:
            PosOriginal = PosFemellaX





        #crear 2 cubs
        femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella + 0.5 ,3.1, self.Altura_forat_femella)
        femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( ample_forat_fem + 0.5 ,3.1, self.Altura_forat_femella)
        #crear 2 cubs invertits
        if femellesInv:
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella, self.BarraGruix + 0.5, ample_forat_fem + 0.5)

        #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
        vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX )
        femella_12 = AllplanGeo.Move(femella_1, vector)
        if femellesInv:
            vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)

        #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
        vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX  + Separacio_forat_femella + self.Altura_forat_femella)
        femella_11 = AllplanGeo.Move(femella_1, vector)

        if femellesInv:
            vector = AllplanGeo.Vector3D( PosFemellaY  + Separacio_forat_femella + self.Altura_forat_femella , 0, PosFemellaX )
            femella_11 = AllplanGeo.Move(femella_1, vector)

        femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

        if posicio == "Dre":
            self.cara_b += "FEM@|P:@"+str(PosOriginal)+"|Y:@"+str(PosFemellaY)+"|A:@"+str(ample_forat_fem)+"@#"
            Y_inv = self.BarraAmple - PosFemellaY - self.Ample_forat_femella
            self.cara_b_inv = "FEM@|P:@"+str(posinv)+"|Y:@"+str(Y_inv)+"|A:@"+str(ample_forat_fem)+"@#" + self.cara_b_inv
            femella = femella[2]
            return femella

        elif posicio == "Sup":
            self.cara_c += "FEM@|P:@"+str(PosOriginal)+"|Y:@"+str(PosFemellaY)+"|A:@"+str(ample_forat_fem)+"@#"
            Y_inv = self.BarraAmple - PosFemellaY - self.Altura_forat_femella
            self.cara_c_inv = "FEM@|P:@"+str(posinv)+"|Y:@"+str(Y_inv)+"|A:@"+str(ample_forat_fem)+"@#" + self.cara_c_inv
            #crear 2 cubs
            #femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella  ,self.BarraGruix, self.Altura_forat_femella)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,self.Ample_forat_femella + 0.5 , self.Altura_forat_femella)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,ample_forat_fem + 0.5 , self.Altura_forat_femella)

            if femellesInv:
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, 3.1,ample_forat_fem + 0.5 )


            #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaY , 0, PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
            vector = AllplanGeo.Vector3D( PosFemellaY , 0, PosFemellaX  + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)
            #orientar Sup

            axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(0,0,1))
            Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
            femella_sup = AllplanGeo.Rotate(femella[2],axis_point, Angle)
            vector = AllplanGeo.Vector3D(self.BarraAmple , 0, 0)
            femella_sup = AllplanGeo.Move(femella_sup,vector)

            return femella_sup

        elif posicio == "Esq":
            self.cara_a += "FEM@|P:@"+str(PosOriginal)+"|Y:@"+str(PosFemellaY)+"|A:@"+str(ample_forat_fem)+"@#"
            Y_inv = self.BarraAmple - PosFemellaY - self.Ample_forat_femella
            self.cara_a_inv = "FEM@|P:@"+str(posinv)+"|Y:@"+str(Y_inv)+"|A:@"+str(ample_forat_fem)+"@#" + self.cara_a_inv
            #orientar Esq
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella + 0.5  ,3.1, self.Altura_forat_femella)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( ample_forat_fem + 0.5  ,3.1, self.Altura_forat_femella)
            if femellesInv:
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella, self.BarraGruix + 0.5, ample_forat_fem + 0.5)


            vector = AllplanGeo.Vector3D( PosFemellaY , self.BarraAltura- self.BarraGruix, PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            if femellesInv:
                vector = AllplanGeo.Vector3D( PosFemellaY , self.BarraAltura- self.BarraGruix, PosFemellaX )
                femella_12 = AllplanGeo.Move(femella_1, vector)
            vector = AllplanGeo.Vector3D( PosFemellaY , self.BarraAltura- self.BarraGruix, PosFemellaX + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)
            if femellesInv:
                vector = AllplanGeo.Vector3D( PosFemellaY + Separacio_forat_femella + self.Altura_forat_femella , self.BarraAltura- self.BarraGruix, PosFemellaX )
                femella_11 = AllplanGeo.Move(femella_1, vector)

            femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

            return femella [2]

        elif posicio == "Inf":
            self.cara_d += "FEM@|P:@"+str(PosOriginal)+"|Y:@"+str(PosFemellaY)+"|A:@"+str(ample_forat_fem)+"@#"
            Y_inv = self.BarraAmple - PosFemellaY - self.Altura_forat_femella
            self.cara_d_inv = "FEM@|P:@"+str(posinv)+"|Y:@"+str(Y_inv)+"|A:@"+str(ample_forat_fem)+"@#" + self.cara_d_inv
            #orientar Inf
            #femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella , self.Ample_forat_femella ,self.BarraGruix)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,self.Ample_forat_femella + 0.5 , self.Altura_forat_femella)
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(3.1,ample_forat_fem + 0.5 , self.Altura_forat_femella)
            if femellesInv:
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix + 0.5, self.Altura_forat_femella, ample_forat_fem + 0.5)

            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura - self.BarraGruix, PosFemellaX )
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.amplada_femella/2, self.BarraAltura/2 - self.llargada_femella/2 - self.BarraGruix , PosFemellaX )
            vector = AllplanGeo.Vector3D(0, PosFemellaY , PosFemellaX )
            femella_12 = AllplanGeo.Move(femella_1, vector)
            if femellesInv:
                vector = AllplanGeo.Vector3D(0, PosFemellaY , PosFemellaX )
                femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix , PosFemellaX )
            vector = AllplanGeo.Vector3D(0, PosFemellaY, PosFemellaX + Separacio_forat_femella + self.Altura_forat_femella)
            femella_11 = AllplanGeo.Move(femella_1, vector)
            if femellesInv:
                vector = AllplanGeo.Vector3D(0, PosFemellaY + Separacio_forat_femella + self.Altura_forat_femella, PosFemellaX )
                femella_11 = AllplanGeo.Move(femella_1, vector)

            femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

            return femella[2]

        else:
            femella = femella[2]

        return femella

    #CANCAMS
    def create_cancams(self):

        self.codi_cancam += "G:@"+str(self.posicio_centre_masses)+"@#"

        #falta revisar el if aquest
        #IF ex_cancam1 =1 AND dis_centreMases1 <> 0 AND pos_centreMases <> 0 THEN
        #if build_ele.IsFirstCancam.value and build_ele.Dis1cancam.value > 0 and and build_ele.posicio_centre_masses.value > 0:# no entiendo <>, es mayor o menor que?
        cancam_x = 500
        cancam_y = 500
        cancam_z = 100

        #crear 2 cubs
        cancam_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAmple - self.BarraGruix*2 -0.065 , self.BarraAltura - self.BarraGruix*2, cancam_z)

        #cancam1
        vector = AllplanGeo.Vector3D(self.BarraGruix, self.BarraAltura - self.BarraGruix*2, self.posicio_centre_masses - self.Dis1cancam )
        cancam_12 = AllplanGeo.Move(cancam_1, vector)
        vector = AllplanGeo.Vector3D(self.BarraGruix, (self.BarraAltura/2)-(self.BarraGruix*2), self.posicio_centre_masses + self.Dis1cancam )
        cancam_11 = AllplanGeo.Move(cancam_1, vector)

        #cancam2
        vector = AllplanGeo.Vector3D(self.BarraGruix, self.BarraAltura - self.BarraGruix*2, self.posicio_centre_masses - self.Dis2cancam )
        cancam_22 = AllplanGeo.Move(cancam_1, vector)
        vector = AllplanGeo.Vector3D(self.BarraGruix, (self.BarraAltura/2)-(self.BarraGruix*2), self.posicio_centre_masses + self.Dis2cancam )
        cancam_21 = AllplanGeo.Move(cancam_1, vector)

        if self.IsFirstCancam and self.IsSecondCancam:
            cancams_10 = AllplanGeo.MakeBoolean(cancam_11, cancam_12)
            cancams_20 = AllplanGeo.MakeBoolean(cancam_21, cancam_22)
            cancams = AllplanGeo.MakeBoolean(cancams_10[2], cancams_20[2])
            cancams = cancams[2]
            self.codi_cancam += "[1]D:@"+str(self.Dis1cancam)+"@#"
            self.codi_cancam += "[2]D:@"+str(self.Dis2cancam)+"@#"
        elif self.IsFirstCancam:
            #Fer Forats
            cancams = AllplanGeo.MakeBoolean(cancam_11, cancam_12)
            cancams = cancams[2]

            self.codi_cancam += "[1]D:@"+str(self.Dis1cancam)+"@#"
        elif self.IsSecondCancam:
            #Fer Forats
            cancams = AllplanGeo.MakeBoolean(cancam_21, cancam_22)
            cancams = cancams[2]

            self.codi_cancam += "[2]D:@"+str(self.Dis2cancam)+"@#"
        else:
            cancams = AllplanGeo.Polyhedron3D.CreateCuboid( 0 ,0, 0)

        return cancams

    #PESTANYES
    def create_pestanyes_sup(self):
        invertirPestanyes = self.invertirPestanyes
        if invertirPestanyes:
            self.codi_pestanyes +=  "[2]C:@S@#"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAmple/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix ,self.alcada_femella ,self.llargada_femella)
            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(pestanya_ampl, self.BarraGruix, pestanya_alc )


            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - pestanya_ampl/2, 0,self.BarraLlargada)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - pestanya_ampl/2, self.BarraAltura - self.BarraGruix, self.BarraLlargada)#build_ele.BarraAltura.value-(self.alcada_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)
            return pestanya_sup[2]
        else:
            self.codi_pestanyes +=  "[2]C:@S@#"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAltura/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix ,self.alcada_femella ,self.llargada_femella)
            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraGruix, pestanya_ampl, pestanya_alc )


            vector = AllplanGeo.Vector3D(0, self.BarraAltura/2 - pestanya_ampl/2, self.BarraLlargada)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix,  self.BarraAltura/2 - pestanya_ampl/2, self.BarraLlargada)#build_ele.BarraAltura.value-(self.alcada_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)
            return pestanya_sup[2]


    def create_pestanyes_inf(self):
        invertirPestanyes = self.invertirPestanyes
        if invertirPestanyes:
            self.codi_pestanyes += "[1]C:@I@#"


            pestanya_alc = 3
            pestanya_ampl = self.BarraAmple/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15

            pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_ampl, self.BarraGruix, pestanya_alc )
            pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_ampl, self.BarraGruix, pestanya_alc )
            #pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix ,self.alcada_femella ,self.llargada_femella)
            #vector = AllplanGeo.Vector3D(self.BarraAltura/2-self.Altura_forat_femella/2, (self.BarraAltura-self.alcada_femella)/2, -self.llargada_femella)

            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - pestanya_ampl/2 , 0, -pestanya_alc)
            pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

            vector = AllplanGeo.Vector3D(   self.BarraAmple/2 - pestanya_ampl/2 , self.BarraAltura - self.BarraGruix, -pestanya_alc)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(self.BarraAltura/2+self.Altura_forat_femella/2 - self.Ample_forat_femella, (self.BarraAltura-self.alcada_femella)/2, -self.llargada_femella)#build_ele.BarraAltura.value-(self.alcada_femella/2)
            pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_2,vector)

            pestanya_inf = AllplanGeo.MakeUnion(pestanya_inf_1, pestanya_inf_2)
            pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)

            return pestanya_inf[2]
        else:
            self.codi_pestanyes += "[1]C:@I@#"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAltura/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15

            pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraGruix, pestanya_ampl, pestanya_alc )
            pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraGruix, pestanya_ampl, pestanya_alc )
            #pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix ,self.alcada_femella ,self.llargada_femella)
            #vector = AllplanGeo.Vector3D(self.BarraAltura/2-self.Altura_forat_femella/2, (self.BarraAltura-self.alcada_femella)/2, -self.llargada_femella)

            vector = AllplanGeo.Vector3D( 0, self.BarraAltura/2 - pestanya_ampl/2 , -pestanya_alc)
            pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

            vector = AllplanGeo.Vector3D(  self.BarraAmple - self.BarraGruix,  self.BarraAltura/2 - pestanya_ampl/2 , -pestanya_alc)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(self.BarraAltura/2+self.Altura_forat_femella/2 - self.Ample_forat_femella, (self.BarraAltura-self.alcada_femella)/2, -self.llargada_femella)#build_ele.BarraAltura.value-(self.alcada_femella/2)
            pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_2,vector)

            pestanya_inf = AllplanGeo.MakeUnion(pestanya_inf_1, pestanya_inf_2)
            pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)

            return pestanya_inf[2]

    #ENCAIX
    def create_encaix(self, nEncaix):
        '''
        es crea el cuboid amb les mesures per restar per la part superior/inferior per crear l'encaix

        return: Polyhedron3D
        '''
        geometry =  AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)
        geometry = self.crear_encaix_geo(geometry, nEncaix, self.EncaixosPar[nEncaix])
        return geometry

    #ENCAIXAux
    def create_encaix_Aux(self, nEncaix):
        '''
        es crea el cuboid amb les mesures per restar per la part superior/inferior per crear l'encaix

        return: Polyhedron3D
        '''
        geometry =  AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)
        geometry = self.crear_encaix_geo(geometry, nEncaix, self.EncaixosAux[nEncaix])
        return geometry

    def crear_encaix_geo(self, geometry, nEncaix, DEncaix):
        #dades_encaixos = self.EncaixosPar
        #DEncaix = Encaixos[nEncaix]

        orientacio = DEncaix.EncaixOr
        longEncaix = DEncaix.Longitud + 2
        amplitudEncaix = 30
        posEncaix = DEncaix.Posicio - longEncaix/2
        posEncaixOrig = DEncaix.Posicio
        profEncaix = DEncaix.Profunditat +1
        TePestanya = DEncaix.Pestanya

        Trans_ref_encaix = 0.0

        #codi_encaix
        self.codi_encaix +=  "["+str(nEncaix+1)+"]C:@"+str(orientacio)+"@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posEncaixOrig)+"@|Z:@"+str(Trans_ref_encaix)+"@#"
        posInvEnca = self.BarraLlargada - posEncaixOrig

        altura_fem = 3
        alcada_fem = 15

        if orientacio == "Dre":
            self.cara_b +=  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posEncaixOrig)+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            self.cara_b_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_b_inv

            cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAmple, profEncaix ,longEncaix)

            vector = AllplanGeo.Vector3D(0 , 0, posEncaix)
            cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

            if TePestanya:
                #pestanya_inf = self.crear_pestanyes_encaixos(nEncaix)
                pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, altura_fem, alcada_fem )
                pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, altura_fem, alcada_fem )

                vector = AllplanGeo.Vector3D(0,  profEncaix-altura_fem, posEncaix + longEncaix/2 - alcada_fem/2 )
                pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix, profEncaix-altura_fem, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

                pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                pestanya_inf = pestanya_inf[2]
                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                return cuboid_encaix_amb_pestanya[3]
            else:
                return cuboid_encaix_inf
        elif orientacio == "Sup":
            self.cara_c +=  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posEncaixOrig)+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            self.cara_c_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_c_inv

            cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( profEncaix, self.BarraAltura,longEncaix)
            vector = AllplanGeo.Vector3D( 0, 0, posEncaix )
            cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

            if TePestanya:
                #crear pestanyes, orientarles i substract al cuboid_encaix_inf
                pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid(  altura_fem, self.BarraGruix, alcada_fem)
                pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura_fem, self.BarraGruix, alcada_fem)

                vector = AllplanGeo.Vector3D( profEncaix - altura_fem, self.BarraAltura-self.BarraGruix, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                vector = AllplanGeo.Vector3D( profEncaix - altura_fem , 0, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)
                pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                pestanya_inf = pestanya_inf[2]

                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                return cuboid_encaix_amb_pestanya[3]
            else:
                return cuboid_encaix_inf
        elif orientacio == "Esq":
            self.cara_a +=  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posEncaixOrig)+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            self.cara_a_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_a_inv


            '''
            cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAltura ,profEncaix ,longEncaix)

            #orientar l'encaix
            axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(0,0,1))
            #Angle = AllplanGeo.Angle(3.14159)#180Deg = 3.14159rad
            Angle = AllplanGeo.Angle.FromDeg(180)
            cuboid_encaix_inf = AllplanGeo.Rotate(cuboid_encaix_inf,axis_point, Angle)
            vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.BarraAltura/2, self.BarraAltura ,  posEncaix)
            cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)
            '''
            cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAmple, profEncaix ,longEncaix)

            vector = AllplanGeo.Vector3D(0 , self.BarraAltura - profEncaix, posEncaix)
            cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)


            if TePestanya: #and esq
                 #pestanya_inf = self.crear_pestanyes_encaixos(nEncaix)
                pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, altura_fem, alcada_fem )
                pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, altura_fem, alcada_fem )

                vector = AllplanGeo.Vector3D(0,  self.BarraAltura - profEncaix, posEncaix + longEncaix/2 - alcada_fem/2 )
                pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix, self.BarraAltura - profEncaix, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

                pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                pestanya_inf = pestanya_inf[2]
                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)

                return cuboid_encaix_amb_pestanya[3]
            else:
                return cuboid_encaix_inf
        elif orientacio == "Inf":
            self.cara_d +=  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posEncaixOrig)+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            self.cara_d_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_d_inv

            cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( profEncaix, self.BarraAltura,longEncaix)
            vector = AllplanGeo.Vector3D( self.BarraAmple - profEncaix, 0, posEncaix )
            cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

            if TePestanya:
                #crear pestanyes, orientarles i substract al cuboid_encaix_inf

                pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid(  altura_fem, self.BarraGruix, alcada_fem)
                pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura_fem, self.BarraGruix, alcada_fem)
                vector = AllplanGeo.Vector3D( self.BarraAmple - profEncaix , self.BarraAltura-self.BarraGruix, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                vector = AllplanGeo.Vector3D( self.BarraAmple - profEncaix , 0, posEncaix + longEncaix/2 - alcada_fem/2)
                pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)
                pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                pestanya_inf = pestanya_inf[2]

                cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                return cuboid_encaix_amb_pestanya[3]
            else:
                return cuboid_encaix_inf
        else:
            return geometry

        return geometry

    #PESTANYES ENCAIXOS
    def crear_pestanyes_encaixos(self, nEncaix):
        dades_encaixos = self.EncaixosPar

        DEncaix = dades_encaixos[nEncaix]

        orientacio = DEncaix[1]
        longEncaix = DEncaix[2]
        posEncaix = DEncaix[3]
        profEncaix = DEncaix[4]
        TePestanya = DEncaix[5]

        pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.llargada_femella, self.amplada_femella)
        pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.llargada_femella, self.amplada_femella)

        vector = AllplanGeo.Vector3D(0, profEncaix-self.llargada_femella, posEncaix + (longEncaix-self.amplada_femella)/2)
        pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

        vector = AllplanGeo.Vector3D(self.BarraAmple - self.BarraGruix, profEncaix - self.llargada_femella, posEncaix + (longEncaix-self.amplada_femella)/2)
        pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_2,vector)

        pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
        pestanya_inf = pestanya_inf[2]

        return pestanya_inf

    #PROPS lAYERS / CAPES
    def get_foundation_common_props(self): #-> AllplanBaseElements.CommonProperties:

        common_prop = AllplanBaseElements.CommonProperties()

        '''
        common_prop.Pen     = build_ele.FounPen.value
        common_prop.Stroke  = build_ele.FounStroke.value
        '''
        common_prop.Layer   = self.BarraLayer
        common_prop.Color   = self.FounColor
        if self.IsUseGlobalProp:
            common_prop.GetGlobalProperties()

        return common_prop

    def get_seat_width(self):
        """
        Get property for seat width

        Returns:
            the seat width.
        """

        return self.BarraAmple

    def getAmplada(self):
        return self.amplada_femella

    def definir_amplada(self, amplada):
        self.amplada_femella = amplada
