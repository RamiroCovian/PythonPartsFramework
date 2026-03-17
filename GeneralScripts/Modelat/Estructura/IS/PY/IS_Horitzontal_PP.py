"""
Script for TableScalable
"""
import hashlib
import random

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate
import NemAll_Python_AllplanSettings as AllplanSettings
import collections

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart
from PythonPartUtil import PythonPartUtil
from BuildingElementAttributeList import BuildingElementAttributeList

print('Load IS_Horitzontal_PP.py')


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

    TDHoritzontal = PP_IS_Horitzontal(build_ele.zUnique.value, build_ele.DistanciaEntreTD.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,
                                build_ele.ColisPar.value, build_ele.PotaPar.value, build_ele.ForatsPar.value, #matrius
                                build_ele.Ample_forat_femella.value, build_ele.Altura_forat_femella.value, build_ele.Separacio_forat_femella.value,
                                build_ele.Femelles.value, #matriu Femelles
                                build_ele.posicio_centre_masses.value,
                                build_ele.IsFirstCancam.value, build_ele.Dis1cancam.value,
                                build_ele.IsSecondCancam.value, build_ele.Dis2cancam.value,
                                build_ele.PestanyaSuperior.value, build_ele.PestanyaInferior.value,
                                build_ele.EncaixosPar.value) #matriu

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not TDHoritzontal.is_valid():
        return ([], [])


    handle_list = TDHoritzontal.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDHoritzontal.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2108, TDHoritzontal.get_codi_cara_a()),
                        AllplanBaseElements.AttributeString(2047, TDHoritzontal.get_codi_cara_b()),
                        AllplanBaseElements.AttributeString(2110, TDHoritzontal.get_codi_cara_c()),
                        AllplanBaseElements.AttributeString(2120, TDHoritzontal.get_codi_cara_d()),

                        AllplanBaseElements.AttributeString(2121, TDHoritzontal.get_codi_cara_a_inv()),
                        AllplanBaseElements.AttributeString(2122, TDHoritzontal.get_codi_cara_b_inv()),
                        AllplanBaseElements.AttributeString(2128, TDHoritzontal.get_codi_cara_c_inv()),
                        AllplanBaseElements.AttributeString(2129, TDHoritzontal.get_codi_cara_d_inv()),

                        AllplanBaseElements.AttributeString(2446, TDHoritzontal.get_codi_pota_inv()),

                        AllplanBaseElements.AttributeString(2430, TDHoritzontal.get_codi_pestanyes()),
                        AllplanBaseElements.AttributeString(2435, TDHoritzontal.get_codi_cancam()),
                        #AllplanBaseElements.AttributeString(2432, TDHoritzontal.get_codi_colis()),
                        #AllplanBaseElements.AttributeString(2429, TDHoritzontal.get_codi_encaix()),
                        #AllplanBaseElements.AttributeString(2434, TDHoritzontal.get_codi_femella()),
                        AllplanBaseElements.AttributeString(2431, TDHoritzontal.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2433, TDHoritzontal.get_codi_pota()),
                        AllplanBaseElements.AttributeString(2445, TDHoritzontal.get_seccio()),
                        AllplanBaseElements.AttributeString(220, TDHoritzontal.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, "EN "),
                        AllplanBaseElements.AttributeString(508, "TUB HOR")]

    pythonpart = PythonPart ("PP_IS_Horitzontal",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class PP_IS_Horitzontal():
    """
    Definition of class Table
    """

    def __init__(self, zUnique, DistanciaEntreTD, BarraAmple, BarraAltura, BarraLlargada, BarraGruix,
                    IsUseGlobalProp, FounColor, BarraLayer,
                    ColisPar, PotaPar, ForatsPar, #matrius
                    Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                    Femelles, #matriu
                    posicio_centre_masses,
                    IsFirstCancam, Dis1cancam,
                    IsSecondCancam, Dis2cancam,
                    PestanyaSuperior, PestanyaInferior,
                    EncaixosPar, invertirPestanyes = False, retallInici = 0, llargBarraAmbRetallFinal = 0, llargadaOriginal = 5550):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """
        self.zUnique = zUnique
        self.DistanciaEntreTD = DistanciaEntreTD
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
        self.Femelles = Femelles #matriu
        self.posicio_centre_masses = posicio_centre_masses
        self.IsFirstCancam = IsFirstCancam
        self.Dis1cancam = Dis1cancam
        self.IsSecondCancam = IsSecondCancam
        self.Dis2cancam = Dis2cancam
        self.PestanyaSuperior = PestanyaSuperior
        self.PestanyaInferior = PestanyaInferior
        self.invertirPestanyes = invertirPestanyes

        self.EncaixosPar = EncaixosPar

        self.retallInici = retallInici
        #if self.retallInici > 0:
        #    self.PestanyaInferior = False

        self.llargBarraAmbRetallFinal = llargBarraAmbRetallFinal

        #if self.llargBarraAmbRetallFinal < llargadaOriginal and self.llargBarraAmbRetallFinal != 0:
        #    self.PestanyaSuperior = False


        self.matrixPosXAux =[]
        self.matrixPosYAux =[]

        self.FemellesAux = []

        self.m_TD_Horitzontal = None

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
        param_list.append ("Femelles = %s\n" % self.Femelles)#matriu
        param_list.append ("posicio_centre_masses = %s\n" % self.posicio_centre_masses)
        param_list.append ("IsFirstCancam = %s\n" % self.IsFirstCancam)
        param_list.append ("Dis1cancam = %s\n" % self.Dis1cancam)
        param_list.append ("IsSecondCancam = %s\n" % self.IsSecondCancam)
        param_list.append ("Dis2cancam = %s\n" % self.Dis2cancam)
        param_list.append ("PestanyaSuperior = %s\n" % self.PestanyaSuperior)
        param_list.append ("PestanyaInferior = %s\n" % self.PestanyaInferior)
        param_list.append ("invertirPestanyes = %s\n" % self.invertirPestanyes)
        param_list.append ("EncaixosPar = %s\n" % self.EncaixosPar)
        return param_list

    def __repr__(self):
        return 'TD_Horitzontal(zUnique=%s, DistanciaEntreTD=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s'\
            'BarraLayer=%s'\
            'ColisPar=%s, PotaPar=%s, ForatsPar=%s'\
            'Ample_forat_femella=%s, Altura_forat_femella=%s'\
            'Separacio_forat_femella=%s, Femelles=%s'\
            'posicio_centre_masses=%s, IsFirstCancam=%s'\
            'Dis1cancam=%s, IsSecondCancam=%s'\
            'Dis2cancam=%s, PestanyaSuperior=%s'\
            'PestanyaInferior=%s, invertirPestanyes=%s, EncaixosPar=%s)\n' \
            % (self.zUnique, self.DistanciaEntreTD, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer,
               self.ColisPar, self.PotaPar, self.ForatsPar,
               self.Ample_forat_femella, self.Altura_forat_femella,
               self.Separacio_forat_femella, self.Femelles,
               self.posicio_centre_masses, self.IsFirstCancam,
               self.Dis1cancam, self.IsSecondCancam,
               self.Dis2cancam, self.PestanyaSuperior,
               self.PestanyaInferior, self.invertirPestanyes, self.EncaixosPar )

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
        return "TD_Horitzontal_PP.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.BarraAmple <= 0 or self.BarraAltura <= 0 or self.BarraLlargada <= 0 :#or self.BarraGruix <= 0:
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

        return str(self.BarraLlargada - self.retallInici )

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

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(0, self.BarraAmple, self.BarraAltura),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraAmple", HandleDirection.y_dir),
                                         ("BarraAltura", HandleDirection.z_dir)],
                                        HandleDirection.yz_dir),
                                        HandleProperties("BarraLlargada",
                                        AllplanGeo.Point3D(self.BarraLlargada, 0, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraLlargada", HandleDirection.x_dir)],
                                        HandleDirection.x_dir)
                      ]

        return handle_list

    def getTDType(self) :
        return "Horitzontal"

    def get_common_props(self):
        common_prop = self.get_foundation_common_props()
        return common_prop

    def set_pos_mat(self, matrixPosX, matrixPosY):
        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY


    def set_retalls(self, retallInici, llargBarraAmbRetallFinal):
        self.retallInici = retallInici
        self.llargBarraAmbRetallFinal = llargBarraAmbRetallFinal

    def pestanya_inf_False(self):
        self.PestanyaInferior = False

    def return_femelles(self):
        return self.Femelles

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
                TDCollectionFemella = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Amplitud Posicio Profunditat Pestanya Separator')
                femellaCollection = TDCollectionFemella(Encaix = iEncaix.BarraFront,
                                            EncaixOr = iEncaix.Orientacio,
                                            Longitud = iEncaix.Longitud, #30,#listLong[i],
                                            Amplitud = iEncaix.Amplitud,
                                            Posicio = iEncaix.Posicio,
                                            Profunditat = iEncaix.Profunditat,
                                            Pestanya = PestanyaValue,
                                            Separator='')

                self.EncaixosPar.append(femellaCollection)
                encaixos.pop(nEncAfegir)
                #print("encaix afegit: " + str(iEncaix.Posicio))

    def add_PP_positions_femelles(self, TDV_count, offsetX, offsetY, orientacio, separacioFemella, Posicio, listFemelles, listFemelles2):
        '''
        if len(self.Femelles) <= TDV_count+1 :
            FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
            bob = FemellesCollection( Femella = False,
                                    FemellaOr = orientacio,
                                    PosFemellaX = Posicio,
                                    PosFemellaY = offsetY,
                                    Separacio_forat_femella = separacioFemella,
                                    Separator = '')
            self.Femelles.append(bob)
        else:
            self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(Femella = True)
            self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(PosFemellaX = Posicio)
            self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(PosFemellaY = offsetY)
            self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(FemellaOr = orientacio)
            self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(Separacio_forat_femella = separacioFemella)
        '''

        '''
        #print("listFemelles")
        #print(listFemelles)
        trobat = False

        for femellaAux in listFemelles:
            if femellaAux.Femella:
                for femella in self.Femelles:
                    if femella.PosFemellaX == femellaAux.PosFemellaX and femella.PosFemellaY == femellaAux.PosFemellaY:
                        femella = femella.replace(Femella = femellaAux.Femella)
                        trobat = True
                    #else:
                        #femella = femella.replace(Femella = False)
                        #femella = femella.replace(Femella = False)


            if not trobat and femellaAux.Femella:
                self.Femelles.append(femellaAux)
            trobat = False


        #print(self.Femelles)
        '''
        inici = len(listFemelles2)
        inici = TDV_count
        for i in range(inici, len(listFemelles)+inici):

            if listFemelles[i-inici].FemellaOr == "Sup" or listFemelles[i-inici].FemellaOr == "Inf" or orientacio == "Sup" or orientacio == "Inf":
                POSFemellaY = 0
            else:
                POSFemellaY = listFemelles[i-inici].PosFemellaY


            if len(self.Femelles) <= i+1 :
                FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                bob = FemellesCollection( Femella = listFemelles[i-inici].Femella,
                                        FemellaOr = listFemelles[i-inici].FemellaOr,
                                        PosFemellaX = listFemelles[i-inici].PosFemellaX,
                                        PosFemellaY = POSFemellaY,
                                        Separacio_forat_femella = listFemelles[i-inici].Separacio_forat_femella,
                                        Separator = '')
                self.Femelles.append(bob)
            else:
                self.Femelles[i] = self.Femelles[i]._replace(Femella = listFemelles[i-inici].Femella)
                self.Femelles[i] = self.Femelles[i]._replace(FemellaOr = listFemelles[i-inici].FemellaOr)
                self.Femelles[i] = self.Femelles[i]._replace(PosFemellaX = listFemelles[i-inici].PosFemellaX)
                self.Femelles[i] = self.Femelles[i]._replace(PosFemellaY = POSFemellaY)
                self.Femelles[i] = self.Femelles[i]._replace(Separacio_forat_femella = listFemelles[i-inici].Separacio_forat_femella)

    #FEMELLES
    def create_PP_positions_femelles(self, ampleTDV, alturaTDV, matrixPosX, matrixPosY, matrixMostrar, offsetX, orientacio, Ample_forat_femellaVert, barraLlargadaReal, offsetHor,FemellesAux = [], desplXI = 0):
        """
        Create a list of transformations to position all TD verticals around the table

        Returns:
            List of Matrix3D transformations
        """
        '''
        for nSeg in range(TDV_count,len(matrixPosX)):
            if matrixPosX[TDV_count+nSeg]:
                print("Afegir femella")
                if
                    FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                    bob = FemellesCollection( Femella = matrixMostrar[_+1],
                                            FemellaOr = orientacio[_+1],
                                            #PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar,
                                            PosFemellaX = deltax + posX - desplXI,
                                            #PosFemellaX =  posX,
                                            PosFemellaY = offsetY,
                                            Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                            Separator = '')
                    self.Femelles.append(bob)
                else:
                self.Femelles[_+1] = self.Femelles[_+1]._replace(Femella = matrixMostrar[_+1])
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(FemellaOr = orientacio[_+1])
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = matrixPosX[_+1] - desplXI - (ampleTDV[_+1]/2 + ampleTDV[0]/2) + ampleTDV[0] )
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)
        '''

        pestanya_alc = 3
        pestanya_ampl = 15

        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = self.DistanciaEntreTD

        trans_list = list()

        #------------------ Create the chairs for the front

        rotation_angle = AllplanGeo.Angle()
        rotation_angle.SetDeg(180)
        rotation_matrix = AllplanGeo.Matrix3D()
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                   AllplanGeo.Point3D(0, 0, 0)),
                                 rotation_angle)

        #------------------ Add the PP
        #TDTotalSpace = distanciaentreTDVerticals + ampleTDV
        TDTotalSpace = distanciaentreTDVerticals + 30
        #TDV_count = int((self.BarraLlargada - (ampleTDV ) - ampleTDV) / TDTotalSpace)
        #TDV_count = int((self.BarraLlargada - (30 ) - 30) / TDTotalSpace) ultim bo
        TDV_count = 0
        resta = barraLlargadaReal
        i = 0
        while resta > 0:
            newSpace = distanciaentreTDVerticals #+ ampleTDV[i]
            resta = resta - newSpace
            TDV_count += 1

        if TDV_count > 0:
            #deltax =  distanciaentreTDVerticals + ampleTDV
            deltax =  distanciaentreTDVerticals #+ ampleTDV[0]

            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(0, 0, 0))
            trans_list.append(trans_matrix)


            #espaiCentrar = self.BarraAmple/2 - self.Altura_forat_femella/2
            if orientacio[0] == 'Esq' or orientacio[0] =='Dre':
                offsetY = alturaTDV[0]/2 - pestanya_ampl/2 - offsetHor
            else:
                offsetY = 0
            espaiCentrar = offsetX #+ ampleTDV/2
            self.Femelles[0] = self.Femelles[0]._replace(Femella = matrixMostrar[0])
            self.Femelles[0] = self.Femelles[0]._replace(PosFemellaX = 0 + matrixPosX[0] - espaiCentrar)
            self.Femelles[0] = self.Femelles[0]._replace(PosFemellaY = offsetY + matrixPosY[0] - desplXI)
            self.Femelles[0] = self.Femelles[0]._replace(FemellaOr = orientacio[0])
            self.Femelles[0] = self.Femelles[0]._replace(Separacio_forat_femella = ampleTDV[0] - 0.75)

            if len(self.EncaixosPar) >2:
                if self.EncaixosPar[2].Encaix == True:
                    self.Femelles[0] = self.Femelles[0]._replace(Femella = False)
                    #("posa femelles a false en 0")

            for _ in range(TDV_count-1):
                trans_matrix = AllplanGeo.Matrix3D()

                posX = 0
                if len(matrixPosX) > _+1:
                    posX = matrixPosX[_+1]


                while len(ampleTDV) < _+2:
                    ampleTDV.append(self.BarraAmple)

                while len(alturaTDV) < _+2:
                    alturaTDV.append(self.BarraAltura)

                while len(matrixPosY) < _+2:
                    matrixPosY.append(0)

                if _+1 < len(orientacio) and _+1 < len(alturaTDV) and _+1 < len(matrixPosY):
                    if orientacio[_+1] == 'Esq' or orientacio[_+1] == 'Dre':
                        offsetY = alturaTDV[_+1]/2 - pestanya_ampl/2 + matrixPosY[_+1] - offsetHor
                    else:
                        offsetY = 0

                    #offsetY = matrixPosY[_+1]
                else:
                    offsetY = alturaTDV[_+1]/2 - pestanya_ampl/2

                #trans_matrix.Translate(AllplanGeo.Vector3D(deltax, self.BarraAltura + deltay, 0))

                '''
                if _ >= len(self.Femelles):
                    TDCollectionFemella = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                    femellaCollection = TDCollectionFemella(Femella = matrixMostrar[_+1],
                                                    FemellaOr = orientacio[_+1],
                                                    PosFemellaX = 31.,
                                                    PosFemellaY = offsetY,
                                                    Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                                    Separator='')
                    self.Femelles.append(femellaCollection)
                '''

                if len(self.matrixPosXAux) >= TDV_count and  len(self.matrixPosYAux) >= TDV_count and TDV_count != 0 and _+1 <= len(self.matrixPosXAux)-1 and len(self.Femelles) >= _:
                    #trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.matrixPosXAux[_+1] - espaiCentrar, matrixPosY[_+1], 0))
                    trans_matrix.Translate(AllplanGeo.Vector3D(deltax , matrixPosY[_+1], 0))

                    if len(self.Femelles) <= _+1 :
                        FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                        bob = FemellesCollection( Femella = matrixMostrar[_+1],
                                                FemellaOr = orientacio[_+1],
                                                #PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar,
                                                PosFemellaX = deltax + posX,
                                                #PosFemellaX =  posX,
                                                PosFemellaY = offsetY,
                                                Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                                Separator = '')
                        self.Femelles.append(bob)
                    else:
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(Femella = matrixMostrar[_+1])
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(FemellaOr = orientacio[_+1])
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar)
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax  + posX)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = posX)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)

                    #aplicar ofsetYper si no esta centrada
                else:
                    trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.BarraGruix*2 , matrixPosY[_+1], 0))#- espaiCentrar + self.BarraGruix, matrixPosY[_+1], 0))
                    if len(self.Femelles) <= _+1 :
                        FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                        if _+1 < len(matrixMostrar):
                            mostrar = matrixMostrar[_+1]
                        else:
                            mostrar = True
                        bob = FemellesCollection( Femella = mostrar,
                                                FemellaOr = orientacio[_+1],
                                                #PosFemellaX = deltax - espaiCentrar,
                                                #PosFemellaX = deltax + self.BarraGruix*2 + posX,
                                                PosFemellaX = deltax + self.BarraGruix*2 + posX,
                                                PosFemellaY = offsetY,
                                                Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                                Separator = '')
                        self.Femelles.append(bob)
                    else:
                        if _+1 < len(matrixMostrar):
                            self.Femelles[_+1] = self.Femelles[_+1]._replace(Femella = matrixMostrar[_+1])
                        else:
                            self.Femelles[_+1] = self.Femelles[_+1]._replace(Femella = True)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(FemellaOr = orientacio[_+1])
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax - espaiCentrar)
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax + self.BarraGruix*2 + posX)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX =  posX)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)

                if _+1 < TDV_count:
                    trans_list.append(trans_matrix)
                    deltax += distanciaentreTDVerticals #+ ampleTDV[_+1] + self.BarraGruix*2

            '''
            _ += 1

            if len(self.Femelles) <= TDV_count+1 :
                FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                if _+1 < len(matrixMostrar):
                    mostrar = matrixMostrar[_+1]
                else:
                    mostrar = True
                bob = FemellesCollection( Femella = mostrar,
                                        FemellaOr = orientacio[_+1],
                                        #PosFemellaX = barraLlargadaReal - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar) + matrixPosX[_+1] ,
                                        PosFemellaX =  matrixPosX[_+1] ,
                                        PosFemellaY = offsetY,
                                        Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                        Separator = '')
                self.Femelles.append(bob)
            else:
                if _+1 < len(matrixMostrar):
                    if _+1 < len(matrixMostrar):
                        self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(Femella = matrixMostrar[_+1])
                    else:
                        self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(Femella = True)
                #self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(PosFemellaX = barraLlargadaReal - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar) + matrixPosX[_+1])
                self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(PosFemellaX = matrixPosX[_+1])
                self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(PosFemellaY = offsetY)
                self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(FemellaOr = orientacio[_+1])
                self.Femelles[TDV_count+1] = self.Femelles[TDV_count+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)

            for i in range(TDV_count+2,len(self.Femelles)):
                self.Femelles.pop()
            '''
            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(barraLlargadaReal - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar), matrixPosY[_+1]/2, 0))
            trans_list.append(trans_matrix)

        return trans_list

    '''
    def create_PP_positions_encaix(self, ampleTDV, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, offsetY, offsetX, orientacio):
        """
        Create a list of transformations to position all TD verticals around the table

        Returns:
            List of Matrix3D transformations
        """


        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = self.DistanciaEntreTD

        trans_list = list()

        #------------------ Create the chairs for the front

        rotation_angle = AllplanGeo.Angle()
        rotation_angle.SetDeg(180)
        rotation_matrix = AllplanGeo.Matrix3D()
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                   AllplanGeo.Point3D(0, 0, 0)),
                                 rotation_angle)

        #------------------ Add the PP
        TDTotalSpace = distanciaentreTDVerticals + ampleTDV
        TDV_count = int((self.BarraLlargada - (ampleTDV ) - ampleTDV) / TDTotalSpace)

        #print("int: " + str(int((self.BarraLlargada - (ampleTDV ) - ampleTDV) / TDTotalSpace)))
        residu = ((self.BarraLlargada - (ampleTDV ) - ampleTDV) / TDTotalSpace) - int((self.BarraLlargada - (ampleTDV ) - ampleTDV) / TDTotalSpace)
        #print("residu: " + str(residu))
        sumatori = residu / TDV_count
        #print("sumatori: " + str(sumatori))


        if TDV_count > 0:
            deltax =  distanciaentreTDVerticals + ampleTDV

            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(0, 0, 0))
            trans_list.append(trans_matrix)

            pestanya = True
            if offsetY[0] == 0:
                pestanya = False

            #espaiCentrar = self.BarraAmple/2 - self.Altura_forat_femella/2
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Encaix = True)
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(EncaixOr = orientacio)
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Longitud = ampleTDV)
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Posicio = 0 - offsetX + matrixcentrar[0])
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Profunditat = offsetY[0])
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Pestanya = pestanya)

            for _ in range(3,TDV_count+3):
                pestanya = True
                if offsetY[_-2] == 0:
                    pestanya = False
                trans_matrix = AllplanGeo.Matrix3D()
                #trans_matrix.Translate(AllplanGeo.Vector3D(deltax, self.BarraAltura + deltay, 0))

                if _ >= len(self.EncaixosPar):
                    TDCollectionFemella = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                    encaixosCollection = TDCollectionFemella(Encaix =  matrixMostrar[_-2],
                                                    EncaixOr = orientacio,
                                                    Longitud = ampleTDV,
                                                    Posicio = deltax + self.matrixPosXAux[_-2] - offsetX + 15,
                                                    Profunditat = offsetY[_-2] ,
                                                    Pestanya = pestanya,
                                                    Separator='')
                    self.EncaixosPar.append(encaixosCollection)

                if TDV_count != 0 and _+1 <= len(self.matrixPosXAux)-1 and len(self.EncaixosPar) >= _:
                    trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.matrixPosXAux[_-2]- offsetX, self.matrixPosYAux[_-2], 0))

                    if len(self.EncaixosPar) <= _+1 :
                        EncaixosParCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                        bob = EncaixosParCollection( Encaix = matrixMostrar[_],
                                                EncaixOr = orientacio,
                                                Longitud = ampleTDV,
                                                Posicio = deltax - self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-1],
                                                Profunditat = offsetY[_-2],
                                                Pestanya = pestanya,
                                                Separator = '')
                        self.EncaixosPar.append(bob)
                    else:
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Encaix = matrixMostrar[_-2])
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(EncaixOr = orientacio)
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Longitud = ampleTDV)
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Posicio = deltax + self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-1]) #offsetX*100
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Profunditat = offsetY[_-2])
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Pestanya = pestanya)
                    #aplicar ofsetYper si no esta centrada


                trans_list.append(trans_matrix)
                deltax += distanciaentreTDVerticals + ampleTDV

            if len(self.EncaixosPar) <= TDV_count+3 :
                EncaixosParCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                bob = EncaixosParCollection( Encaix = matrixMostrar[_],
                                        EncaixOr = orientacio,
                                        Longitud = ampleTDV,
                                        Posicio = self.BarraLlargada - ampleTDV + self.matrixPosXAux[_-2] + matrixcentrar[_-1],
                                        Profunditat = offsetY[_-2],
                                        Pestanya = pestanya,
                                        Separator = '')
                self.EncaixosPar.append(bob)
            else:
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(Encaix = matrixMostrar[_-2])
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(EncaixOr = orientacio)
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(Longitud = ampleTDV)
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(Posicio = self.BarraLlargada - ampleTDV + self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-1])
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(Profunditat = offsetY[_-2])
                self.EncaixosPar[TDV_count+3] = self.EncaixosPar[TDV_count+3]._replace(Pestanya = pestanya)

            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(self.BarraLlargada - ampleTDV, 0, 0))
            trans_list.append(trans_matrix)



            if len(self.EncaixosPar)>TDV_count:
                #self.EncaixosPar = self.EncaixosPar[:TDV_count]
                for i in range(TDV_count+4,len(self.EncaixosPar)):
                    self.EncaixosPar.pop()

        return trans_list
    '''

    def create_PP_positions_encaix(self, ampleTDV, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, offsetY, offsetX, orientacio, barraLlargadaReal):
        """
        Create a list of transformations to position all TD verticals around the table

        Returns:
            List of Matrix3D transformations
        """


        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = self.DistanciaEntreTD

        trans_list = list()

        #------------------ Create the chairs for the front

        rotation_angle = AllplanGeo.Angle()
        rotation_angle.SetDeg(180)
        rotation_matrix = AllplanGeo.Matrix3D()
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(),
                                                   AllplanGeo.Point3D(0, 0, 0)),
                                 rotation_angle)

        #------------------ Add the PP
        TDTotalSpace = distanciaentreTDVerticals

        TDV_count = 0
        resta = barraLlargadaReal
        i = 0
        while resta > 0:
            newSpace = distanciaentreTDVerticals #+ ampleTDV[i]
            resta = resta - newSpace
            TDV_count += 1

        if TDV_count > 0:
            deltax =  distanciaentreTDVerticals #+ ampleTDV[0]

            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(0, 0, 0))
            trans_list.append(trans_matrix)

            pestanya = True
            #if offsetY[0] == 0:
            #    pestanya = False

            #espaiCentrar = self.BarraAmple/2 - self.Altura_forat_femella/2
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Encaix = True)
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(EncaixOr = orientacio)
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Longitud = ampleTDV[0])
            #self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Longitud = matrixPosX[0] )
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Posicio = 0 - offsetX + matrixcentrar[0])
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Profunditat = offsetY[0])
            self.EncaixosPar[2] = self.EncaixosPar[2]._replace(Pestanya = pestanya)
            print("-------DELTAX---------")
            for _ in range(3,TDV_count+2):
                print(deltax)
                pestanya = True
                #if offsetY[_-2] == 0:
                #    pestanya = False
                trans_matrix = AllplanGeo.Matrix3D()
                #trans_matrix.Translate(AllplanGeo.Vector3D(deltax, self.BarraAltura + deltay, 0))

                #print(str(_) + " " + str(self.matrixPosXAux[_-2]))

                if _ >= len(self.EncaixosPar):
                    TDCollectionFemella = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                    encaixosCollection = TDCollectionFemella(Encaix =  matrixMostrar[_-2],
                                                    EncaixOr = orientacio,
                                                    Longitud = ampleTDV[_-2] +2,
                                                    Posicio = deltax + self.matrixPosXAux[_-2] - offsetX + 15,
                                                    Profunditat = offsetY[_-2] +1,
                                                    Pestanya = pestanya,
                                                    Separator='')
                    self.EncaixosPar.append(encaixosCollection)

                if TDV_count != 0 and _+1 <= len(self.matrixPosXAux)-1 and len(self.EncaixosPar) >= _:
                    #trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.matrixPosXAux[_-2] - offsetX , self.matrixPosYAux[_-2], 0))
                    trans_matrix.Translate(AllplanGeo.Vector3D(deltax , self.matrixPosYAux[_-2], 0))

                    if len(self.EncaixosPar) <= _+1 :
                        EncaixosParCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                        bob = EncaixosParCollection( Encaix = matrixMostrar[_],
                                                EncaixOr = orientacio,
                                                Longitud = ampleTDV[_-2]  +2,
                                                Posicio = deltax - self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-2],
                                                Profunditat = offsetY[_-2] +1,
                                                Pestanya = pestanya,
                                                Separator = '')
                        self.EncaixosPar.append(bob)
                    else:
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Encaix = matrixMostrar[_-2])
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(EncaixOr = orientacio)
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Longitud = ampleTDV[_-2] +2)
                        #self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Posicio = deltax + self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-2]) #offsetX*100
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Posicio = self.matrixPosXAux[_-2] + ampleTDV[_-2]/2) #offsetX*100
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Profunditat = offsetY[_-2] +1)
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Pestanya = pestanya)
                    #aplicar ofsetYper si no esta centrada
                '''
                else:
                    trans_matrix.Translate(AllplanGeo.Vector3D(deltax , 0, 0))
                    if len(self.EncaixosPar) <= _+1 :
                        EncaixosParCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                        bob = EncaixosParCollection( Encaix = True,
                                                EncaixOr = orientacio,
                                                Longitud = ampleTDV,
                                                Posicio = deltax,
                                                Profunditat = offsetY,
                                                Pestanya = pestanya,
                                                Separator = '')
                        self.EncaixosPar.append(bob)
                    else:
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(Encaix = True)
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(EncaixOr = orientacio)
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(Longitud = ampleTDV)
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(Posicio = deltax)
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(Profunditat = offsetY)
                        self.EncaixosPar[_+1] = self.EncaixosPar[_+1]._replace(Pestanya = pestanya)
                '''

                trans_list.append(trans_matrix)
                deltax += distanciaentreTDVerticals #+ ampleTDV[_-2]




            if len(self.EncaixosPar) <= TDV_count+2 :
                EncaixosParCollection = collections.namedtuple('StirrupList', 'Encaix EncaixOr Longitud Posicio Profunditat Pestanya  Separator')
                bob = EncaixosParCollection( Encaix = matrixMostrar[_],
                                        EncaixOr = orientacio,
                                        Longitud = ampleTDV[_-1] +2,
                                        #Posicio = barraLlargadaReal  + self.matrixPosXAux[_-2] + matrixcentrar[_-2],#- ampleTDV[_-2]
                                        Posicio = self.matrixPosXAux[_-1] ,#- ampleTDV[_-2]
                                        Profunditat = offsetY[_-1] +1,
                                        Pestanya = pestanya,
                                        Separator = '')
                self.EncaixosPar.append(bob)
            else:
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Encaix = matrixMostrar[_-1])
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(EncaixOr = orientacio)
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Longitud = ampleTDV[_-1] +2 )
                #self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Posicio = barraLlargadaReal - ampleTDV[_-2] + self.matrixPosXAux[_-2] - offsetX + matrixcentrar[_-2])
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Posicio = self.matrixPosXAux[_-1] + ampleTDV[_-1]/2)
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Profunditat = offsetY[_-1] +1)
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Pestanya = pestanya)


            trans_matrix = AllplanGeo.Matrix3D()
            #trans_matrix.Translate(AllplanGeo.Vector3D(barraLlargadaReal - ampleTDV[_-2], 0, 0))
            trans_matrix.Translate(AllplanGeo.Vector3D(barraLlargadaReal , self.matrixPosYAux[_-1], 0))
            trans_list.append(trans_matrix)



            if len(self.EncaixosPar)>TDV_count+1:
                #self.EncaixosPar = self.EncaixosPar[:TDV_count]
                for i in range(TDV_count+4,len(self.EncaixosPar)):
                    self.EncaixosPar.pop()

            '''
            for enc in self.EncaixosPar:
                print(enc)
            '''

        print("----END DELTAX---------")


        return trans_list


    def set_false_encaix(self):
        for i in range(2,len(self.EncaixosPar)):
            self.EncaixosPar[i] = self.EncaixosPar[i]._replace(Encaix = False)

    def set_false_femelles(self):
        for i in range(0,len(self.Femelles)):
            self.Femelles[i] = self.Femelles[i]._replace(Femella = False)


    def create_superior(self, pos:AllplanGeo.Vector3D):
        novaBarra = self.create()
        novaBarra = AllplanGeo.Move(novaBarra, pos)
        return novaBarra

    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''
        self.amplada_femella = 50
        self.alcada_femella = 200
        self.llargada_femella = 50

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
        self.codi_pota = "#"

        self.cara_a = "#" #Esq
        self.cara_b = "#" #Dre
        self.cara_c = "#" #Sup
        self.cara_d = "#" #Inf

        self.cara_a_inv = "" #Esq Invertida
        self.cara_b_inv = "" #Dre Invertida
        self.cara_c_inv = "" #Sup Invertida
        self.cara_d_inv = "" #Inf Invertida

        self.codi_pota_inv = ""

        elements = []

        ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        barra = ele1

        #cub vermell per orientar el costat inferior
        ind_inf = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.BarraAltura, self.BarraGruix)
        common_prop = AllplanBaseElements.CommonProperties()
        common_prop.Color = 6 #Vermell
        #vector = AllplanGeo.Vector3D(0, 0, 0)
        #ind_inf = AllplanGeo.Move(ind_inf, vector)
        elements.append(AllplanBasisElements.ModelElement3D(common_prop, ind_inf))



        #Encaixos
        dades_encaix = self.EncaixosPar
        i = 0
        for Iencaix in dades_encaix:
            EncaixActiu = Iencaix[0]
            if EncaixActiu:
                ele2 = self.create_encaix(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]#forat
            i += 1
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
            '''
            #polyhedron
            eleint1 = self.create_cilinderinterior_cancam1()
            eleint2 = self.create_cilinderinterior_cancam2()

            barra = AllplanGeo.MakeBoolean(barra, eleint1)
            barra = barra[3]
            barra = AllplanGeo.MakeBoolean(barra, eleint2)
            barra = barra[3]
            if self.IsFirstCancam:
                ele1 = self.create_cilinder_cancam1()
                ele2 = self.create_cilinder_cancam2()

                #barra = AllplanGeo.MakeBoolean(barra, ele1)
                #barra = barra[2]
                #barra = AllplanGeo.MakeBoolean(barra, ele2)
                #barra = barra[2]

            if self.IsSecondCancam:
                ele1 = self.create_cilinder_cancam11()
                ele2 = self.create_cilinder_cancam22()
                #barra = AllplanGeo.MakeBoolean(barra, ele1)
                #barra = barra[2]
                #barra = AllplanGeo.MakeBoolean(barra, ele2)
                #barra = barra[2]
            '''


        #Femelles
        dades_femella = self.Femelles
        i = 0
        self.codi_femella += "S:@"+str(self.Separacio_forat_femella)+"@|L:@"+str(self.Altura_forat_femella)+"@|M:@"+str(self.Ample_forat_femella)+"@#"
        for Ifemella in dades_femella:
            femellaActiva = Ifemella[0]
            if femellaActiva:
                ele2 = self.create_femelles(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[3]
            i += 1
        #Femelles2
        dades_femella = self.FemellesAux
        i = 0
        self.codi_femella += "S:@"+str(self.Separacio_forat_femella)+"@|L:@"+str(self.Altura_forat_femella)+"@|M:@"+str(self.Ample_forat_femella)+"@#"
        for Ifemella in dades_femella:
            femellaActiva = Ifemella[0]
            if femellaActiva:
                ele2 = self.create_femelles(i)
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
                ele8 = self.create_colis(i)
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

        '''
        axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(0,1,0))
        Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
        barra = AllplanGeo.Rotate(barra,axis_point, Angle)
        '''

        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]

        elements.append(AllplanBasisElements.ModelElement3D(common_prop, barra))


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
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura )
        #crear cuboid interior
        if self.BarraGruix != 0:
            geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraLlargada,
                                                            self.BarraAmple - self.BarraGruix*2,
                                                            self.BarraAltura - self.BarraGruix*2)

            #es crea el vector per posicionarlo al centre i es resten els volums
            vector = AllplanGeo.Vector3D(0, self.BarraGruix, self.BarraGruix)
            geometry2 = AllplanGeo.Move(geometry2, vector)

        if self.BarraGruix*2 < self.BarraAmple and self.BarraGruix*2 < self.BarraAltura and self.BarraGruix != 0:
            geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)
            geometry = geometry[3]
        else:
            geometry = geometry1


        #retall inici
        geometry3 = AllplanGeo.Polyhedron3D.CreateCuboid(self.retallInici,
                                                            self.BarraAmple ,
                                                            self.BarraAltura )

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(0, 0, 0)
        geometry3 = AllplanGeo.Move(geometry3, vector)

        if self.retallInici != 0:
            geometry = AllplanGeo.MakeBoolean(geometry, geometry3)
            geometry = geometry[3]


        #retall final
        geometry4 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraLlargada - self.retallInici - self.llargBarraAmbRetallFinal+1,
                                                            self.BarraAmple,
                                                            self.BarraAltura )

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(self.llargBarraAmbRetallFinal + self.retallInici, 0, 0)
        geometry4 = AllplanGeo.Move(geometry4, vector)
        if self.llargBarraAmbRetallFinal > 0 and self.llargBarraAmbRetallFinal < self.BarraLlargada:
            geometry = AllplanGeo.MakeBoolean(geometry, geometry4)
            geometry = geometry[3]


        return  geometry


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

        if posColis >= self.retallInici -1 and (posColis < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):


            if orientacio == 'Inf' or orientacio == 'Sup':
                if orientacio == 'Inf':
                    self.cara_d += "COL|P:@"+str(posColis)+"@#"
                    posInv = self.BarraLlargada-posColis
                    self.cara_d_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_d_inv
                else:
                    self.cara_c += "COL|P:@"+str(posColis)+"@#"
                    posInv = self.BarraLlargada-posColis
                    self.cara_c_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_c_inv
                #colis = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc , self.BarraAmple, colis_forat_alc )
                colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_ampl, colis_forat_alc)
                #colis = AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)

            else:
                if orientacio == 'Esq':
                    self.cara_a += "COL|P:@"+str(posColis)+"@#"
                    posInv = self.BarraLlargada-posColis
                    self.cara_a_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_a_inv
                else:
                    self.cara_b += "COL|P:@"+str(posColis)+"@#"
                    posInv = self.BarraLlargada-posColis
                    self.cara_b_inv = "COL|P:@"+str(posInv)+"@#" + self.cara_b_inv
                #colis = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_forat_alc, self.BarraAltura)
                colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_forat_alc, colis_ampl)
                #colis = AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)

            vector = self.vector_colis_int_bool(num_colis)
            colis_int = AllplanGeo.Move(colis_int, vector)

            vector = self.vector_colis(num_colis)
        #colis = AllplanGeo.Move(colis, vector)

        #colis = AllplanGeo.MakeBoolean(colis, colis_int)

        #colis = colis[3]

        #axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(1,0,0))
        #Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
        #colis = AllplanGeo.Rotate(colis,axis_point,Angle)

        #return colis

    def vector_colis(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_alcada = 3

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), 0, -colis_alcada )
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), -colis_alcada, 0 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), 0, self.BarraAltura )
        else:
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), self.BarraAmple , 0)

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
        colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc-self.BarraGruix*2, colis_alcada, self.BarraAmple - self.BarraGruix*4)

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2,  self.BarraAmple/2 - colis_ampl/2, -colis_alcada )
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2, -colis_alcada, self.BarraAltura/2 - colis_ampl/2 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2,  self.BarraAmple/2 - colis_ampl/2, self.BarraAmple  )
        else:
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2, self.BarraAmple ,self.BarraAltura/2 - colis_ampl/2 )

        return vector


    def create_colis_int(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis.orientacio
        posColis = DColis.Posicio
        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_alcada = 3

        if posColis >= self.retallInici -1 and (posColis < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

            if orientacio == 'Inf' or orientacio == 'Sup':
                colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_ampl, self.BarraGruix)
            else:
                colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, self.BarraGruix, colis_ampl)
            vector = self.vector_colis_int(num_colis)
            colis_int = AllplanGeo.Move(colis_int, vector)

            return colis_int
        colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(1,0,0)
        vector = AllplanGeo.Vector3D(-10, -10  ,-10)
        return AllplanGeo.Move(colis_int, vector)

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
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2 , self.BarraAmple/2 - colis_ampl/2 , 0)
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2 , 0, self.BarraAltura/2 - colis_ampl/2 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2, self.BarraAmple/2 - colis_ampl/2, self.BarraAltura - self.BarraGruix)
        else:
            vector = AllplanGeo.Vector3D(posColis - colis_alc/2, self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - colis_ampl/2 )

        return vector


    #POTA #POTES
    def create_pota(self, num_pota):
        dades_pota = self.PotaPar
        DPota = dades_pota[num_pota]

        posPota = DPota[1]

        if posPota >= self.retallInici -1 and (posPota < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

            #self.codi_pota += "["+str(num_pota+1)+"]P:@"+str(posPota) + "@#"
            self.codi_pota += "P:@"+str(posPota) + "@#"
            potaInv = self.BarraLlargada - posPota
            self.codi_pota_inv = "P:@"+str(potaInv) + "@#" + self.codi_pota_inv

            pota_alc = 13
            pota_ample = 13

            pota = AllplanGeo.Polyhedron3D.CreateCuboid( pota_alc ,pota_ample, self.BarraAltura)
            vector = AllplanGeo.Vector3D(posPota - pota_ample/2, self.BarraAmple/2 - pota_ample/2, 0)

            pota = AllplanGeo.Move(pota, vector)

            return pota
        else:
            pota = AllplanGeo.Polyhedron3D.CreateCuboid( 1 ,1, 1)
            vector = AllplanGeo.Vector3D(-10, -10, -10)

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

        if posForat >= self.retallInici -1 and (posForat < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

            if orientacio == 'Inf' or orientacio == 'Sup':
                forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alc, forat_ampl, altura)
                forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alcB, forat_amplB, altura)
            else:
                forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alc, altura, forat_ampl)
                forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alcB, altura, forat_amplB)
            vector, vectorB = self.vector_forats_int(num_forat)
            #forat_int = AllplanGeo.Move(forat_int, vector)

            if esCompleta:
                forat_int = AllplanGeo.Move(forat_int, vector)
                forat_intB = AllplanGeo.Move(forat_intB, vectorB)
                forat_intC = AllplanGeo.MakeBoolean(forat_int, forat_intB)
                forat_int = forat_intC[2]
            else:
                forat_int = AllplanGeo.Move(forat_int, vector)
        else:
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(1,1,1)
            vector = AllplanGeo.Vector3D(-10,-10,-10)
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
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , self.BarraAmple/2 - forat_ampl/2 , 0)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, self.BarraAmple/2 - forat_amplB/2, self.BarraAltura - self.BarraGruix)
            self.cara_d += codi1
            self.cara_d_inv += codi_inv1
            self.cara_c += codi2
            self.cara_c_inv += codi_inv2
        elif orientacio == 'Dre':# or (orientacio == 'Esq' and esCompleta):#v
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , 0, self.BarraAltura/2 - forat_ampl/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - forat_amplB/2 )
            self.cara_b += codi1
            self.cara_b_inv += codi_inv1
            self.cara_a += codi2
            self.cara_a_inv += codi_inv2
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, self.BarraAmple/2 - forat_ampl/2, self.BarraAltura - self.BarraGruix)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 , self.BarraAmple/2 - forat_amplB/2 , 0)
            self.cara_c += codi1
            self.cara_c_inv += codi_inv1
            self.cara_d += codi2
            self.cara_d_inv += codi_inv2
        else:
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - forat_ampl/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 , 0, self.BarraAltura/2 - forat_amplB/2 )
            self.cara_a += codi1
            self.cara_a_inv += codi_inv1
            self.cara_b += codi2
            self.cara_b_inv += codi_inv2
        return vector, vectorB


    #FEMELLES
    def create_femelles(self, nFemella):
        dades_femelles = self.Femelles
        Dfemella = dades_femelles[nFemella]
        profunditatFemella = 3.1
        try:
            profunditatFemella = Dfemella.profunditatFemella
        except Exception as e:
            print("profunditatFemella error")

        #print(Dfemella)

        posicio = Dfemella[1]


        PosFemellaX = Dfemella[2] - 0.25

        FemellesInv = False
        if hasattr(Dfemella, "tubGirat"):
            FemellesInv = Dfemella.tubGirat

        #print("---------------")
        #print("PosFemellaX: " + str(PosFemellaX))
        #print("self.retallInici: " + str(self.retallInici))

        if PosFemellaX >= self.retallInici -1 and (PosFemellaX < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

            codi = "FEM@|P:@"+str(PosFemellaX)+"@#"
            posinv = self.BarraLlargada - PosFemellaX
            codi_inv = "FEM@|P:@"+str(posinv)+"@#"

            if Dfemella.Separacio_forat_femella != 0:#Dfemella[4] != 0:
                Separacio_forat_femella = Dfemella[4] + 0.5
            else:
                Separacio_forat_femella = self.Separacio_forat_femella
                PosFemellaX = Dfemella[2] - Separacio_forat_femella/2 - self.Altura_forat_femella/2 - 0.25
                if FemellesInv:
                    PosFemellaX = Dfemella[2] - self.Ample_forat_femella/2 - 0.25


            if Dfemella.PosFemellaY != 0: #Dfemella[3] != 0:
                PosFemellaY = Dfemella[3]
                ample_forat_fem = 15
            else:
                if posicio == "Dre" or posicio == "Esq":
                    if hasattr(Dfemella, "Ample_forat_femella"):
                        if Dfemella.Ample_forat_femella == 0:
                            ample_forat_fem = self.Ample_forat_femella
                        else:
                            ample_forat_fem = Dfemella.Ample_forat_femella
                    PosFemellaY = self.BarraAltura/2 - ample_forat_fem/2
                    if FemellesInv:
                        PosFemellaY = self.BarraAmple/2 - self.Ample_forat_femella/2

                else:
                    PosFemellaY = self.BarraAltura/2 - self.Ample_forat_femella/2
                    if FemellesInv:
                        PosFemellaY = self.BarraAltura/2 - Separacio_forat_femella/2 - self.Altura_forat_femella

                ample_forat_fem = self.Ample_forat_femella
            if hasattr(Dfemella, "Ample_forat_femella"):
                if Dfemella.Ample_forat_femella == 0:
                    ample_forat_fem = self.Ample_forat_femella
                else:
                    ample_forat_fem = Dfemella.Ample_forat_femella

            PosFemellaY -= 0.25
            self.codi_femella += "["+str(nFemella+1)+"]C:@"+str(posicio)+"@|P:@"+str(PosFemellaX)+"@#"


            #crear 2 cubs
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, ample_forat_fem + 0.5 ,profunditatFemella)

            #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY , 0)
            femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaX  + Separacio_forat_femella , PosFemellaY, 0)
            femella_11 = AllplanGeo.Move(femella_1, vector)
            if FemellesInv:
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(ample_forat_fem + 0.5,self.Altura_forat_femella ,profunditatFemella)

                #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
                vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY , 0)
                femella_12 = AllplanGeo.Move(femella_1, vector)
                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
                vector = AllplanGeo.Vector3D(PosFemellaX  , PosFemellaY + Separacio_forat_femella, 0)
                femella_11 = AllplanGeo.Move(femella_1, vector)


            femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

            if posicio == "Dre":
                self.cara_b += codi
                posinv = self.BarraLlargada - PosFemellaX
                self.cara_b_inv = codi_inv + self.cara_b_inv
                femella = femella[2]
                return femella

            elif posicio == "Sup":
                self.cara_c += codi
                posinv = self.BarraLlargada - PosFemellaX
                self.cara_c_inv = codi_inv + self.cara_c_inv
                #orientar Sup
                '''
                axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(1,0,0))
                Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
                femella_sup = AllplanGeo.Rotate(femella[2],axis_point, Angle)
                vector = AllplanGeo.Vector3D(0, self.BarraAmple , 0)
                femella_sup = AllplanGeo.Move(femella_sup,vector)
                '''
                if FemellesInv:
                    femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(ample_forat_fem + 0.5, profunditatFemella , self.Altura_forat_femella)

                    vector = AllplanGeo.Vector3D(PosFemellaX , self.BarraAmple - self.BarraGruix, PosFemellaY)
                    femella_12 = AllplanGeo.Move(femella_1, vector)
                    vector = AllplanGeo.Vector3D( PosFemellaX , self.BarraAmple - self.BarraGruix, PosFemellaY + Separacio_forat_femella)
                    femella_11 = AllplanGeo.Move(femella_1, vector)

                    femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                    femella_sup = femella[2]
                    return femella_sup


                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, profunditatFemella,ample_forat_fem + 0.5 )

                vector = AllplanGeo.Vector3D(PosFemellaX, self.BarraAmple - self.BarraGruix, PosFemellaY )
                femella_12 = AllplanGeo.Move(femella_1, vector)
                vector = AllplanGeo.Vector3D( PosFemellaX + Separacio_forat_femella , self.BarraAmple - self.BarraGruix, PosFemellaY)
                femella_11 = AllplanGeo.Move(femella_1, vector)

                femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                femella_sup = femella[2]
                return femella_sup

            elif posicio == "Esq":
                self.cara_a += codi
                posinv = self.BarraLlargada - PosFemellaX
                self.cara_a_inv = codi_inv + self.cara_a_inv
                #orientar Esq
                if FemellesInv:
                    femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( ample_forat_fem + 0.5 ,self.Altura_forat_femella, profunditatFemella)

                    vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY, self.BarraAltura- self.BarraGruix)
                    femella_12 = AllplanGeo.Move(femella_1, vector)
                    vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY + Separacio_forat_femella ,self.BarraAltura- self.BarraGruix)
                    femella_11 = AllplanGeo.Move(femella_1, vector)

                    femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                    return femella [2]

                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella, ample_forat_fem + 0.5 ,profunditatFemella)

                vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY, self.BarraAltura- self.BarraGruix)
                femella_12 = AllplanGeo.Move(femella_1, vector)
                vector = AllplanGeo.Vector3D(PosFemellaX + Separacio_forat_femella , PosFemellaY,self.BarraAltura- self.BarraGruix)
                femella_11 = AllplanGeo.Move(femella_1, vector)

                femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                return femella [2]

            elif posicio == "Inf":
                self.cara_d += codi
                posinv = self.BarraLlargada - PosFemellaX
                self.cara_d_inv = codi_inv + self.cara_d_inv
                #orientar Inf
                #femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix, self.Altura_forat_femella , ample_forat_fem )

                if FemellesInv:
                    femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(ample_forat_fem +0.5, profunditatFemella, self.Altura_forat_femella)

                    #vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura - self.BarraGruix, PosFemellaX )
                    #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.amplada_femella/2, self.BarraAltura/2 - self.llargada_femella/2 - self.BarraGruix , PosFemellaX )
                    vector = AllplanGeo.Vector3D(PosFemellaX, 0, PosFemellaY )
                    femella_12 = AllplanGeo.Move(femella_1, vector)
                    #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix , PosFemellaX )
                    vector = AllplanGeo.Vector3D( PosFemellaX  , 0, PosFemellaY + Separacio_forat_femella)
                    femella_11 = AllplanGeo.Move(femella_1, vector)

                    femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                    return femella[2]

                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, profunditatFemella,ample_forat_fem +0.5)

                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura - self.BarraGruix, PosFemellaX )
                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.amplada_femella/2, self.BarraAltura/2 - self.llargada_femella/2 - self.BarraGruix , PosFemellaX )
                vector = AllplanGeo.Vector3D(PosFemellaX, 0, PosFemellaY )
                femella_12 = AllplanGeo.Move(femella_1, vector)
                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix , PosFemellaX )
                vector = AllplanGeo.Vector3D( PosFemellaX + Separacio_forat_femella, 0, PosFemellaY)
                femella_11 = AllplanGeo.Move(femella_1, vector)

                femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                return femella[2]

            else:
                femella = femella[2]

            return femella
        vector = AllplanGeo.Vector3D(-1, 0, 0)
        return AllplanGeo.Move(AllplanGeo.Polyhedron3D.CreateCuboid(1, 1,1), vector)
    '''
    #Cancam1
    def create_cilinder_cancam1(self):
        #polyhedron
        #----- create cylinder interior
        self.codi_cancam += "G:@"+str(self.posicio_centre_masses)+"@#"
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            pass
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        #------ create a cylinder exterior

        cylinder = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    20,
            radiusMinor=    20,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra1 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra1 = barra1[3]


            profile_points =   [
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2 +0.1, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2 +0.1, self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2 , self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                            AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura+20),
                            ]

            path = AllplanGeo.Polyline3D(path_points)

            error_code, swept_polyhedron = AllplanGeo.CreateSweptPolyhedron3D(
                profiles=      profiles,
                path=          path,
                closecaps=     True,
                railrotation=  True,
                rotAxis=       AllplanGeo.Vector3D())

            if error_code == AllplanGeo.eOK:
                barra1 = AllplanGeo.MakeBoolean(barra1,swept_polyhedron)
                barra1 = barra1[2]

        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra1

    #Cancam1
    def create_cilinder_cancam11(self):
        #polyhedron
        #----- create cylinder interior
        self.codi_cancam += "G:@"+str(self.posicio_centre_masses)+"@#"
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            pass
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        #------ create a cylinder exterior

        cylinder = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    20,
            radiusMinor=    20,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra1 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra1 = barra1[3]

            profile_points =   [
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2 +0.1, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2 +0.1, self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2 , self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                            AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura+20),
                            ]

            path = AllplanGeo.Polyline3D(path_points)

            error_code, swept_polyhedron = AllplanGeo.CreateSweptPolyhedron3D(
                profiles=      profiles,
                path=          path,
                closecaps=     True,
                railrotation=  True,
                rotAxis=       AllplanGeo.Vector3D())

            if error_code == AllplanGeo.eOK:
                barra1 = AllplanGeo.MakeBoolean(barra1,swept_polyhedron)
                barra1 = barra1[2]

        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra1

    #Cancam2
    def create_cilinder_cancam2(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            pass
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )


        #------ create a cylinder

        cylinder = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    20,
            radiusMinor=    20,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra2 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra2 = barra2[3]

            profile_points =   [
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2 +0.1, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2 +0.1, self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2 , self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura),
                            AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura+20),
                            ]

            path = AllplanGeo.Polyline3D(path_points)

            error_code, swept_polyhedron = AllplanGeo.CreateSweptPolyhedron3D(
                profiles=      profiles,
                path=          path,
                closecaps=     True,
                railrotation=  True,
                rotAxis=       AllplanGeo.Vector3D())

            if error_code == AllplanGeo.eOK:
                barra2 = AllplanGeo.MakeBoolean(barra2,swept_polyhedron)
                barra2 = barra2[2]
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra2

    #Cancam2
    def create_cilinder_cancam22(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            pass
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )


        #------ create a cylinder

        cylinder = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura ) ),
            radiusMajor=    20,
            radiusMinor=    20,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra2 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra2 = barra2[3]

            profile_points =   [
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2 +0.1, self.BarraAmple/2, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2 +0.1, self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2 , self.BarraAmple/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura),
                            AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura+20),
                            ]

            path = AllplanGeo.Polyline3D(path_points)

            error_code, swept_polyhedron = AllplanGeo.CreateSweptPolyhedron3D(
                profiles=      profiles,
                path=          path,
                closecaps=     True,
                railrotation=  True,
                rotAxis=       AllplanGeo.Vector3D())

            if error_code == AllplanGeo.eOK:
                barra2 = AllplanGeo.MakeBoolean(barra2,swept_polyhedron)
                barra2 = barra2[2]
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra2

    #Cancam interior 1
    def create_cilinderinterior_cancam1(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            return polyhedronint
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

    #Cancam interior 1
    def create_cilinderinterior_cancam11(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses - self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            return polyhedronint
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

    #Cancam interior 2
    def create_cilinderinterior_cancam2(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis1cancam/2, self.BarraAmple/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            return polyhedronint
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 20, 20 , self.BarraGruix )

    #Cancam interior 2
    def create_cilinderinterior_cancam22(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(self.posicio_centre_masses + self.Dis2cancam/2, self.BarraAmple/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 8)

        if error_code == AllplanGeo.eOK:
            return polyhedronint
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 20, 20 , self.BarraGruix )
    '''
    #CANCAMS
    def create_cancams(self):

        self.codi_cancam += "G:@"+str(self.posicio_centre_masses)+"@#"

        #falta revisar el if aquest
        #IF ex_cancam1 =1 AND dis_centreMases1 <> 0 AND pos_centreMases <> 0 THEN
        #if build_ele.IsFirstCancam.value and build_ele.Dis1cancam.value > 0 and and build_ele.posicio_centre_masses.value > 0:# no entiendo <>, es mayor o menor que?
        cancam_x = 50
        cancam_y = 50
        cancam_z = 100

        #crear 2 cubs
        #cancam_1 = AllplanGeo.Polyhedron3D.CreateCuboid( cancam_z, self.BarraAmple - self.BarraGruix*2 -0.065 ,self.BarraAltura - self.BarraGruix*2)
        cancam_1 = AllplanGeo.Polyhedron3D.CreateCuboid( 13, 13 ,self.BarraGruix)

        #cancam1
        #vector = AllplanGeo.Vector3D( self.posicio_centre_masses - self.Dis1cancam/2, self.BarraGruix, self.BarraAltura - self.BarraGruix*2 )
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses - self.Dis1cancam/2 -6.5, self.BarraAmple/2 - 6.5, self.BarraAltura - self.BarraGruix )
        cancam_12 = AllplanGeo.Move(cancam_1, vector)
        #vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis1cancam/2, self.BarraGruix, (self.BarraAltura/2)-(self.BarraGruix*2) )
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis1cancam/2 -6.5, self.BarraAmple/2 - 6.5, self.BarraAltura-self.BarraGruix )
        cancam_11 = AllplanGeo.Move(cancam_1, vector)

        #cancam2
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis2cancam/2 -6.5, self.BarraAmple/2 - 6.5, self.BarraAltura - self.BarraGruix )
        cancam_22 = AllplanGeo.Move(cancam_1, vector)
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis2cancam/2 -6.5,self.BarraAmple/2 - 6.5, self.BarraAltura - self.BarraGruix )
        cancam_21 = AllplanGeo.Move(cancam_1, vector)


        cancams1 = AllplanGeo.Polyhedron3D.CreateCuboid( 1, 1 ,1)
        vector = AllplanGeo.Vector3D(-10, -10,-10)
        cross1 = AllplanGeo.Move(cancams1, vector)
        cross2 = AllplanGeo.Move(cancams1, vector)


        if self.IsFirstCancam and self.IsSecondCancam:
            #cancams_10 = AllplanGeo.MakeBoolean(cancam_11, cancam_12)
            #cancams_20 = AllplanGeo.MakeBoolean(cancam_21, cancam_22)
            #cancams = AllplanGeo.MakeBoolean(cancams_10[2], cancams_20[2])
            #cancams = cancams[2]
            PosCancamMin = self.posicio_centre_masses - self.Dis1cancam/2
            PosCancamMax = self.posicio_centre_masses + self.Dis1cancam/2
            if PosCancamMin >= self.retallInici -1 and (PosCancamMax < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

                cross1 = self.create_cuboid_cancam_1()
                self.codi_cancam += "[1]D:@"+str(self.Dis1cancam)+"@#"

            PosCancamMin = self.posicio_centre_masses - self.Dis2cancam/2
            PosCancamMax = self.posicio_centre_masses + self.Dis2cancam/2
            if PosCancamMin >= self.retallInici -1 and (PosCancamMax < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):
                cross2 = self.create_cuboid_cancam_2()
                self.codi_cancam += "[2]D:@"+str(self.Dis2cancam)+"@#"


            cancams = AllplanGeo.MakeBoolean(cross1, cross2)
            cancams = cancams[2]
        elif self.IsFirstCancam and not self.IsSecondCancam:
            #Fer Forats
            #cancams = AllplanGeo.MakeBoolean(cancam_11, cancam_12)
            #cancams = cancams[2]

            PosCancamMin = self.posicio_centre_masses - self.Dis1cancam/2
            PosCancamMax = self.posicio_centre_masses + self.Dis1cancam/2

            if PosCancamMin >= self.retallInici -1 and (PosCancamMax < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

                cancams = self.create_cuboid_cancam_1()

                self.codi_cancam += "[1]D:@"+str(self.Dis1cancam)+"@#"
            else:
                cancams = AllplanGeo.Polyhedron3D.CreateCuboid( 1, 1 ,1)
                vector = AllplanGeo.Vector3D(-10, -10,-10)
                cancams = AllplanGeo.Move(cancams, vector)
        elif self.IsSecondCancam and not self.IsFirstCancam:
            #Fer Forats
            #cancams = AllplanGeo.MakeBoolean(cancam_21, cancam_22)
            #cancams = cancams[2]

            PosCancamMin = self.posicio_centre_masses - self.Dis2cancam/2
            PosCancamMax = self.posicio_centre_masses + self.Dis2cancam/2

            if PosCancamMin >= self.retallInici -1 and (PosCancamMax < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

                cancams = self.create_cuboid_cancam_2()

                self.codi_cancam += "[2]D:@"+str(self.Dis2cancam)+"@#"
            else:
                cancams = AllplanGeo.Polyhedron3D.CreateCuboid( 1, 1 ,1)
                vector = AllplanGeo.Vector3D(-10, -10,-10)
                cancams = AllplanGeo.Move(cancams, vector)
        else:# not self.IsFirstCancam and not self.IsSecondCancam:
            cancams = AllplanGeo.Polyhedron3D.CreateCuboid( 0 ,0, 0)


        return cancams

    def create_cuboid_cancam_1(self):
        ampleCross = 20
        AlturaCross = 1
        ele1 = AllplanGeo.Polyhedron3D.CreateCuboid( AlturaCross, ampleCross , self.BarraGruix )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis1cancam/2 - AlturaCross/2 , self.BarraAmple/2 -ampleCross/2 , self.BarraAltura-0.5)
        ele1 = AllplanGeo.Move(ele1, vector)
        ele2 = AllplanGeo.Polyhedron3D.CreateCuboid( ampleCross, AlturaCross , self.BarraGruix )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis1cancam/2 - ampleCross/2, self.BarraAmple/2 -AlturaCross/2, self.BarraAltura-0.5)
        ele2 = AllplanGeo.Move(ele2, vector)

        cross = AllplanGeo.MakeBoolean(ele1, ele2)

        ele1 = AllplanGeo.Polyhedron3D.CreateCuboid( AlturaCross, ampleCross , self.BarraGruix )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses + self.Dis1cancam/2 - AlturaCross/2 , self.BarraAmple/2 -ampleCross/2 , self.BarraAltura-0.5)
        ele1 = AllplanGeo.Move(ele1, vector)
        ele2 = AllplanGeo.Polyhedron3D.CreateCuboid( ampleCross, AlturaCross , self.BarraGruix )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses + self.Dis1cancam/2 - ampleCross/2, self.BarraAmple/2 -AlturaCross/2, self.BarraAltura-0.5)
        ele2 = AllplanGeo.Move(ele2, vector)

        cross2 = AllplanGeo.MakeBoolean(ele1, ele2)
        cross = AllplanGeo.MakeBoolean(cross[2], cross2[2])
        return  cross[2]

    def create_cuboid_cancam_2(self):
        ampleCross = 20
        AlturaCross = 1
        ele1 = AllplanGeo.Polyhedron3D.CreateCuboid( AlturaCross, ampleCross , 0.5 )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis2cancam/2 - AlturaCross/2 , self.BarraAmple/2 -ampleCross/2 , self.BarraAltura-0.5)
        ele1 = AllplanGeo.Move(ele1, vector)
        ele2 = AllplanGeo.Polyhedron3D.CreateCuboid( ampleCross, AlturaCross , 0.5 )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis2cancam/2 - ampleCross/2, self.BarraAmple/2 -AlturaCross/2, self.BarraAltura-0.5)
        ele2 = AllplanGeo.Move(ele2, vector)

        cross = AllplanGeo.MakeBoolean(ele1, ele2)

        ele1 = AllplanGeo.Polyhedron3D.CreateCuboid( ampleCross, AlturaCross , 0.5 )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses + self.Dis2cancam/2 - ampleCross/2 , self.BarraAmple/2 -AlturaCross/2 , self.BarraAltura-0.5)
        ele1 = AllplanGeo.Move(ele1, vector)
        ele2 = AllplanGeo.Polyhedron3D.CreateCuboid( AlturaCross, ampleCross , 0.5 )
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses + self.Dis2cancam/2 - AlturaCross/2, self.BarraAmple/2 -ampleCross/2, self.BarraAltura-0.5)
        ele2 = AllplanGeo.Move(ele2, vector)

        cross2 = AllplanGeo.MakeBoolean(ele1, ele2)
        cross = AllplanGeo.MakeBoolean(cross[2], cross2[2])
        return  cross[2]

    #PESTANYES
    def create_pestanyes_sup(self):
        pestanyesInv = self.invertirPestanyes
        if pestanyesInv:
            self.codi_pestanyes +=  "[2]C:@S@INV#"
            pestanya_alc = 3
            pestanya_ampl = self.BarraAltura/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15
            #pestanya_ampl = 15


            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc, 1.5, pestanya_ampl )

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, self.Ample_forat_femella ,self.BarraGruix)
            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella)
            vector = AllplanGeo.Vector3D(self.BarraLlargada, 0, (self.BarraAltura-pestanya_ampl)/2)
            #vector = AllplanGeo.Vector3D(self.BarraLlargada, self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura/2-self.Altura_forat_femella/2)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D( self.BarraLlargada, self.BarraAmple - 1.5, (self.BarraAltura-pestanya_ampl)/2)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(self.BarraLlargada, self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura/2-self.Altura_forat_femella/2)#self.BarraAltura-(self.alcada_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)

        else:
            self.codi_pestanyes +=  "[2]C:@S@#"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAmple/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15
            #pestanya_ampl = 15


            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc, pestanya_ampl,  1.5 )

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, self.Ample_forat_femella ,self.BarraGruix)
            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella)
            vector = AllplanGeo.Vector3D(self.BarraLlargada,(self.BarraAmple-pestanya_ampl)/2, 0)
            #vector = AllplanGeo.Vector3D(self.BarraLlargada, self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura/2-self.Altura_forat_femella/2)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D( self.BarraLlargada, (self.BarraAmple-pestanya_ampl)/2,  self.BarraAltura - 1.5)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(self.BarraLlargada, self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura/2-self.Altura_forat_femella/2)#self.BarraAltura-(self.alcada_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)
        return pestanya_sup[2]


    def create_pestanyes_inf(self):
        pestanyesInv = self.invertirPestanyes
        if pestanyesInv:
            self.codi_pestanyes += "[1]C:@I@#INV"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAltura/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15
            #pestanya_ampl = 15

            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc ,1.5 ,pestanya_ampl )
            pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc, 1.5 ,pestanya_ampl)

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )
            #pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )
            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella)
            #pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella,)

            vector = AllplanGeo.Vector3D( -pestanya_alc, 0, (self.BarraAltura-pestanya_ampl)/2)
            #vector = AllplanGeo.Vector3D(-self.Ample_forat_femella, self.BarraAmple/2 + self.Separacio_forat_femella/2, self.BarraAltura/2-self.Altura_forat_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D( -pestanya_alc,  self.BarraAmple - 1.5, (self.BarraAltura-pestanya_ampl)/2)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(-self.Ample_forat_femella, self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura/2-self.Altura_forat_femella/2)#self.BarraAltura-(self.alcada_femella/2)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_2,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)
        else:
            self.codi_pestanyes += "[1]C:@I@#"

            pestanya_alc = 3
            pestanya_ampl = self.BarraAmple/2
            if pestanya_ampl > 15:
                pestanya_ampl = 15
            #pestanya_ampl = 15

            pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc ,pestanya_ampl ,1.5)
            pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid( pestanya_alc ,pestanya_ampl, 1.5)

            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )
            #pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.llargada_femella, self.BarraGruix ,self.alcada_femella )
            #pestanya_sup_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella)
            #pestanya_sup_2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Ample_forat_femella ,self.BarraGruix, self.Altura_forat_femella,)

            vector = AllplanGeo.Vector3D( -pestanya_alc,(self.BarraAmple-pestanya_ampl)/2, 0)
            #vector = AllplanGeo.Vector3D(-self.Ample_forat_femella, self.BarraAmple/2 + self.Separacio_forat_femella/2, self.BarraAltura/2-self.Altura_forat_femella/2)
            pestanya_sup_1 = AllplanGeo.Move(pestanya_sup_1,vector)
            vector = AllplanGeo.Vector3D( -pestanya_alc, (self.BarraAmple-pestanya_ampl)/2,  self.BarraAltura - 1.5)#self.BarraAltura-(self.alcada_femella/2)
            #vector = AllplanGeo.Vector3D(-self.Ample_forat_femella, self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura/2-self.Altura_forat_femella/2)#self.BarraAltura-(self.alcada_femella/2)
            pestanya_sup_2 = AllplanGeo.Move(pestanya_sup_2,vector)

            pestanya_sup = AllplanGeo.MakeUnion(pestanya_sup_1, pestanya_sup_2)
            pestanya_sup = AllplanGeo.MakeBoolean(pestanya_sup_1, pestanya_sup_2)
        return pestanya_sup[2]

    #ENCAIX
    def create_encaix(self, nEncaix):
        '''
        es crea el cuboid amb les mesures per restar per la part superior/inferior per crear l'encaix

        return: Polyhedron3D
        '''
        geometry =  AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)
        geometry = self.crear_encaix_geo(geometry, nEncaix)
        return geometry

    def crear_encaix_geo(self, geometry, nEncaix):
        dades_encaixos = self.EncaixosPar
        DEncaix = dades_encaixos[nEncaix]

        mostrar = DEncaix[0]

        orientacio = DEncaix.EncaixOr
        longEncaix = DEncaix.Longitud + 2
        try:
            if DEncaix.Amplitud != 0:
                AmplEncaix = DEncaix.Amplitud + 2
            else:
                AmplEncaix = self.BarraAmple
        except:
            AmplEncaix = self.BarraAmple

        posEncaix = DEncaix.Posicio - longEncaix/2
        profEncaix = DEncaix.Profunditat + 1
        TePestanya = DEncaix.Pestanya


        Trans_ref_encaix = 0.0

        if posEncaix >= self.retallInici -1 and (posEncaix < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):


            #codi_encaix
            self.codi_encaix +=  "["+str(nEncaix+1)+"]C:@"+str(orientacio)+"@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            posInvEnca = self.BarraLlargada - DEncaix[3]

            altura_fem = 3
            alcada_fem = 15

            if orientacio == "Dre":
                self.cara_b += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
                self.cara_b_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_b_inv

                cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid(longEncaix, AmplEncaix ,profEncaix)


                vector = AllplanGeo.Vector3D(posEncaix , 0, 0)
                cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

                if TePestanya:
                    pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, self.BarraGruix, altura_fem )
                    pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, self.BarraGruix, altura_fem )

                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAltura/2 - AmplEncaix/2, profEncaix - altura_fem )
                    pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAltura/2 + AmplEncaix/2 - self.BarraGruix, profEncaix - altura_fem)
                    pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

                    pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                    pestanya_inf = pestanya_inf[2]
                    cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                    return cuboid_encaix_amb_pestanya[3]
                else:
                    return cuboid_encaix_inf
            elif orientacio == "Sup":
                self.cara_c += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
                self.cara_c_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_c_inv

                cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid(longEncaix, profEncaix, AmplEncaix)
                vector = AllplanGeo.Vector3D(posEncaix , 0, self.BarraAltura/2 - AmplEncaix/2)
                cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

                if TePestanya:
                    #crear pestanyes, orientarles i substract al cuboid_encaix_inf

                    pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, altura_fem, self.BarraGruix )
                    pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, altura_fem, self.BarraGruix )
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  profEncaix - altura_fem, self.BarraAltura/2 + AmplEncaix/2-self.BarraGruix)
                    pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  profEncaix - altura_fem, self.BarraAltura/2 - AmplEncaix/2)
                    pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)
                    pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                    pestanya_inf = pestanya_inf[2]

                    cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                    return cuboid_encaix_amb_pestanya[3]
                else:
                    return cuboid_encaix_inf
            elif orientacio == "Esq":
                self.cara_a += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
                self.cara_a_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_a_inv

                cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid( longEncaix, AmplEncaix ,profEncaix )
                vector = AllplanGeo.Vector3D(posEncaix, self.BarraAltura/2 - AmplEncaix/2, self.BarraAltura - profEncaix)
                cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)


                if TePestanya: #and esq
                    #crear pestanyes, orientarles i substract al cuboid_encaix_inf
                    pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, self.BarraGruix, altura_fem )
                    pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, self.BarraGruix, altura_fem )
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAltura/2 - AmplEncaix/2, self.BarraAltura -profEncaix )
                    pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAltura/2 + AmplEncaix/2 - self.BarraGruix, self.BarraAltura -profEncaix)
                    pestanya_inf_1 = AllplanGeo.Move(pestanya_inf_1,vector)

                    pestanya_inf = AllplanGeo.MakeBoolean(pestanya_inf_1, pestanya_inf_2)
                    pestanya_inf = pestanya_inf[2]
                    cuboid_encaix_amb_pestanya = AllplanGeo.MakeBoolean(cuboid_encaix_inf, pestanya_inf)
                    return cuboid_encaix_amb_pestanya[3]
                else:
                    return cuboid_encaix_inf
            elif orientacio == "Inf":
                self.cara_d += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
                self.cara_d_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_d_inv

                cuboid_encaix_inf = AllplanGeo.Polyhedron3D.CreateCuboid(longEncaix, profEncaix, AmplEncaix)
                vector = AllplanGeo.Vector3D(posEncaix, self.BarraAmple - profEncaix, self.BarraAltura/2 - AmplEncaix/2)
                cuboid_encaix_inf = AllplanGeo.Move(cuboid_encaix_inf,vector)

                if TePestanya:
                    #crear pestanyes, orientarles i substract al cuboid_encaix_inf

                    pestanya_inf_1 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, altura_fem, self.BarraGruix )
                    pestanya_inf_2 = AllplanGeo.Polyhedron3D.CreateCuboid( alcada_fem, altura_fem, self.BarraGruix )
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAmple - profEncaix , self.BarraAltura/2 + AmplEncaix/2-self.BarraGruix)
                    pestanya_inf_2 = AllplanGeo.Move(pestanya_inf_1,vector)
                    vector = AllplanGeo.Vector3D(posEncaix + longEncaix/2 - alcada_fem/2,  self.BarraAmple - profEncaix , self.BarraAltura/2 - AmplEncaix/2)
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

    #PROPS lAYERS / CAPES
    def get_foundation_common_props(self): #-> AllplanBaseElements.CommonProperties:

        common_prop = AllplanBaseElements.CommonProperties()
        '''
        common_prop.Color   = build_ele.FounColor.value
        common_prop.Pen     = build_ele.FounPen.value
        common_prop.Stroke  = build_ele.FounStroke.value
        '''
        common_prop.Color   = self.FounColor
        common_prop.Layer   = self.BarraLayer
        if self.IsUseGlobalProp:
            common_prop.GetGlobalProperties()

        return common_prop

    def getAmplada(self):
        return self.amplada_femella

    def definir_amplada(self, amplada):
        self.amplada_femella = amplada

