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

print('Load TD_Horitzontal_Inf_PP.py')


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

    #TDHoritzontal = PP_EN_Horitzontal_Inf(build_ele.zUnique.value, build_ele.DistanciaEntreTD.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value, build_ele.invertirPeca.value,
    TDHoritzontal = PP_TD_Horitzontal_Inf(build_ele.zUnique.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value, build_ele.invertirPeca.value,False,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value)

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not TDHoritzontal.is_valid():
        return ([], [])


    handle_list = TDHoritzontal.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDHoritzontal.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2431, TDHoritzontal.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2445, TDHoritzontal.get_seccio()),
                        AllplanBaseElements.AttributeString(220, TDHoritzontal.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, "TH SUP "),
                        AllplanBaseElements.AttributeString(508, "TUB HOR")]

    pythonpart = PythonPart ("PP_TD_Horitzontal_Inf",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class PP_TD_Horitzontal_Inf():
    """
    Definition of class Table
    """

    #def __init__(self, zUnique, DistanciaEntreTD, BarraAmple, BarraAltura, BarraLlargada, BarraGruix, invertirPeca,
    def __init__(self, zUnique, BarraAmple, BarraAltura, BarraLlargada, BarraGruix, invertirPeca, invertirSup,
                    foratsL,
                    IsUseGlobalProp, FounColor, BarraLayer,
                    femelles = [],
                    Ample_forat_femella = 15, Altura_forat_femella = 3.75, Separacio_forat_femella = 30,
                    retallInici = 0, llargBarraAmbRetallFinal = 0):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """
        self.zUnique = zUnique
        #self.DistanciaEntreTD = DistanciaEntreTD
        self.BarraAmple = BarraAmple
        self.BarraAltura = BarraAltura
        self.BarraLlargada = BarraLlargada
        self.BarraGruix = BarraGruix
        self.invertirPeca = invertirPeca
        self.invertirSup = invertirSup
        self.IsUseGlobalProp = IsUseGlobalProp
        self.FounColor = FounColor
        self.BarraLayer = BarraLayer

        self.ForatsPar = foratsL

        self.retallInici = retallInici
        self.llargBarraAmbRetallFinal = llargBarraAmbRetallFinal


        self.matrixPosXAux =[]
        self.matrixPosYAux =[]

        self.FemellesAux = []
        self.EncaixosPar = []
        self.Femelles = femelles

        self.Ample_forat_femella = Ample_forat_femella
        self.Altura_forat_femella = Altura_forat_femella
        self.Separacio_forat_femella = Separacio_forat_femella


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
        param_list.append ("InvertirPeca = %s\n" % self.invertirPeca)
        param_list.append ("IsUseGlobalProp = %s\n" % self.IsUseGlobalProp)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)
        param_list.append ("Femelles = %s\n" % self.Femelles)#matriu
        param_list.append ("Ample_forat_femella = %s\n" % self.Ample_forat_femella)
        param_list.append ("Altura_forat_femella = %s\n" % self.Altura_forat_femella)
        param_list.append ("Separacio_forat_femella = %s\n" % self.Separacio_forat_femella)
        return param_list

    def __repr__(self):
        #return 'TD_Horitzontal(zUnique=%s, DistanciaEntreTD=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s, invertirPeca=%s,' \
        return 'TD_Horitzontal(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s, invertirPeca=%s, invertirSup=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s,'\
            'BarraLayer=%s,'\
            'self.Femelles=%s,'\
            'Ample_forat_femella=%s, Altura_forat_femella=%s, Separacio_forat_femella=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix, self.invertirPeca,  self.invertirSup,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer,
               self.Femelles,
               self.Ample_forat_femella, self.Altura_forat_femella, self.Separacio_forat_femella)
            #% (self.zUnique, self.DistanciaEntreTD, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix, self.invertirPeca,


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
        if self.BarraAmple <= 0 or self.BarraAltura <= 0 or self.BarraLlargada <= 0 or self.BarraGruix <= 0:
            return False

        return True

    def get_ref_enc_llargada(self):
        return 0

    def get_codi_pestanyes(self):

        return self.codi_pestanyes

    def get_codi_cancam(self):

        return "#"

    def get_codi_colis(self):

        return "#"

    def get_codi_encaix(self):

        return "#"


    def get_codi_mesures(self):

        return self.codi_mesures

    def get_seccio(self):

        if self.BarraAmple > self.BarraAltura:
            return str(self.BarraAmple) + "x " + str(self.BarraAltura) + "x " + str(self.BarraGruix)

        return str(self.BarraAltura) + "x " + str(self.BarraAmple) + "x " + str(self.BarraGruix)

    def get_llargada(self):

        return str(self.BarraLlargada)

    def get_codi_pota(self):

        return "#"

    def get_codi_pota_inv(self):

        return "#"

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

    def get_codi_femella(self):

        return self.codi_femella

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


    def create_superior(self, pos:AllplanGeo.Vector3D):
        novaBarra = self.create()
        novaBarra = AllplanGeo.Move(novaBarra, pos)
        return novaBarra

    def set_false_encaix(self):
        return

    def set_false_femelles(self):
        return

    def afegir_encaixos_frontals(self, encaixos, listLong, PestanyaValue):
        #print("-----------")

        for nEncaixafegit in self.EncaixosPar:
            trobat = False
            i = 0
            nEncAfegir = 0
            while i < len(encaixos):
                iEncaix = encaixos[i]
                if nEncaixafegit.Encaix == iEncaix.BarraFront and nEncaixafegit.EncaixOr == iEncaix.Orientacio and nEncaixafegit.Posicio == iEncaix.Posicio and nEncaixafegit.Profunditat == iEncaix.Profunditat:
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

        inici = len(listFemelles2)-1
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


        pestanya_alc = 3
        pestanya_ampl = 15

        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = 1170

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
            if len(self.Femelles) < 1 :
                FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                bob = FemellesCollection( Femella = matrixMostrar[0],
                                        FemellaOr = orientacio[0],
                                        #PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar,
                                        PosFemellaX = deltax + 0 - desplXI,
                                        #PosFemellaX =  posX,
                                        PosFemellaY = offsetY,
                                        Separacio_forat_femella = ampleTDV[0] - 0.75,
                                        Separator = '')
                self.Femelles.append(bob)
            self.Femelles[0] = self.Femelles[0]._replace(Femella = matrixMostrar[0])
            self.Femelles[0] = self.Femelles[0]._replace(PosFemellaX = 0 + matrixPosX[0] - espaiCentrar)
            if orientacio[0] == 'Esq' or orientacio[0] =='Dre':
                self.Femelles[0] = self.Femelles[0]._replace(PosFemellaY = offsetY + matrixPosY[0] - desplXI)
            else:
                self.Femelles[0] = self.Femelles[0]._replace(PosFemellaY = 0)
            self.Femelles[0] = self.Femelles[0]._replace(FemellaOr = orientacio[0])
            self.Femelles[0] = self.Femelles[0]._replace(Separacio_forat_femella = ampleTDV[0] - 0.75)

            if len(self.EncaixosPar) >2:
                if self.EncaixosPar[2].Encaix == True:
                    self.Femelles[0] = self.Femelles[0]._replace(Femella = False)
                    #("posa femelles a false en 0")

            for _ in range(TDV_count):
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

                if len(matrixPosX) >= TDV_count and  len(self.matrixPosYAux) >= TDV_count and TDV_count != 0 and _+1 <= len(matrixPosX)-1 and len(self.Femelles) >= _:
                    #trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.matrixPosXAux[_+1] - espaiCentrar, matrixPosY[_+1], 0))
                    #trans_matrix.Translate(AllplanGeo.Vector3D(deltax , matrixPosY[_+1], 0))
                    trans_matrix.Translate(AllplanGeo.Vector3D(posX - desplXI - ampleTDV[_+1]/2 + ampleTDV[0]/2 , matrixPosY[_+1], 0))

                    if len(self.Femelles) <= _+1 :
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
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar)
                        #self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = deltax  + posX)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = posX - desplXI - (ampleTDV[_+1]/2 + ampleTDV[0]/2) + ampleTDV[0] )
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)

                    #aplicar ofsetYper si no esta centrada
                else:
                    #trans_matrix.Translate(AllplanGeo.Vector3D(deltax + self.BarraGruix*2 , matrixPosY[_+1], 0))#- espaiCentrar + self.BarraGruix, matrixPosY[_+1], 0))
                    #trans_matrix.Translate(AllplanGeo.Vector3D(posX - desplXI , matrixPosY[_+1], 0))#- espaiCentrar + self.BarraGruix, matrixPosY[_+1], 0))
                    trans_matrix.Translate(AllplanGeo.Vector3D(posX - desplXI - (ampleTDV[_+1]/2 + ampleTDV[0]/2), matrixPosY[_+1], 0))#- espaiCentrar + self.BarraGruix, matrixPosY[_+1], 0))

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
                                                PosFemellaX = deltax + self.BarraGruix*2 + posX - desplXI,
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
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX =  posX - desplXI -(ampleTDV[_+1]/2 + ampleTDV[0]/2) + ampleTDV[0]  )
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                        self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)

                if _+1 < TDV_count:
                    trans_list.append(trans_matrix)
                    deltax += distanciaentreTDVerticals #- (ampleTDV[_+1]-30)/2 #+ ampleTDV[_+1] + self.BarraGruix*2


            #_ += 1
            '''
            if len(self.Femelles) <= TDV_count+1 :
                FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                if _+1 < len(matrixMostrar):
                    mostrar = matrixMostrar[_+1]
                else:
                    mostrar = True
                bob = FemellesCollection( Femella = mostrar,
                                        FemellaOr = orientacio[_+1],
                                        PosFemellaX = barraLlargadaReal - desplXI - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar),# + matrixPosX[_+1] ,
                                        #PosFemellaX =  matrixPosX[_+1] ,
                                        PosFemellaY = offsetY,
                                        Separacio_forat_femella = ampleTDV[_+1] - 0.75,
                                        Separator = '')
                self.Femelles.append(bob)
            else:
                if _+1 < len(matrixMostrar):
                    if _+1 < len(matrixMostrar):
                        self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(Femella = matrixMostrar[_+1])
                    else:
                        self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(Femella = True)
                self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(PosFemellaX = barraLlargadaReal - desplXI - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar) )#+ matrixPosX[_+1])
                #self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(PosFemellaX = matrixPosX[_+1])
                self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(PosFemellaY = offsetY)
                self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(FemellaOr = orientacio[_+1])
                self.Femelles[TDV_count] = self.Femelles[TDV_count]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)
            '''


            trans_matrix = AllplanGeo.Matrix3D()
            trans_matrix.Translate(AllplanGeo.Vector3D(barraLlargadaReal - desplXI - (ampleTDV[_+1] + self.BarraGruix*2 - espaiCentrar), matrixPosY[_+1]/2, 0))
            trans_list.append(trans_matrix)

            for i in range(TDV_count+2,len(self.Femelles)):#potser canviar +2 -> +1
                self.Femelles.pop()

            #for femellaAux in  FemellesAux:
            for _ in  range(TDV_count,len(matrixMostrar)-1):
                #if femellaAux.Femella:
                    #self.Femelles.append(femellaAux)

                    #self.Femelles[len(self.Femelles)-1] = self.Femelles[len(self.Femelles)-1]._replace(Femella = femellaAux.Femella)
                    #self.Femelles[len(self.Femelles)-1] = self.Femelles[len(self.Femelles)-1]._replace(PosFemellaX = femellaAux.PosFemellaX)
                    #self.Femelles[len(self.Femelles)-1] = self.Femelles[len(self.Femelles)-1]._replace(PosFemellaY = femellaAux.PosFemellaY)
                    #self.Femelles[len(self.Femelles)-1] = self.Femelles[len(self.Femelles)-1]._replace(FemellaOr = femellaAux.FemellaOr)
                    #self.Femelles[len(self.Femelles)-1] = self.Femelles[len(self.Femelles)-1]._replace(Separacio_forat_femella = femellaAux.Separacio_forat_femella)
                if _+1 < len(orientacio) and _+1 < len(alturaTDV) and _+1 < len(matrixPosY):
                    if orientacio[_+1] == 'Esq' or orientacio[_+1] == 'Dre':
                        offsetY = alturaTDV[_+1]/2 - pestanya_ampl/2 + matrixPosY[_+1] - offsetHor
                    else:
                        offsetY = 0

                    #offsetY = matrixPosY[_+1]
                else:
                    offsetY = alturaTDV[_+1]/2 - pestanya_ampl/2

                if len(self.Femelles) <= _+1 :
                    FemellesCollection = collections.namedtuple('StirrupList', 'Femella FemellaOr PosFemellaX PosFemellaY Separacio_forat_femella Separator')
                    bob = FemellesCollection( Femella = matrixMostrar[_+1],
                                            FemellaOr = orientacio[_+1],
                                            #PosFemellaX = deltax + self.matrixPosXAux[_+1] - espaiCentrar,
                                            PosFemellaX = matrixPosX[_+1] - desplXI - (ampleTDV[_+1]/2 + ampleTDV[0]/2) + ampleTDV[0] ,
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
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaX = matrixPosX[_+1] - desplXI - (ampleTDV[_+1]/2 + ampleTDV[0]/2) + ampleTDV[0] )
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(PosFemellaY = offsetY)
                    self.Femelles[_+1] = self.Femelles[_+1]._replace(Separacio_forat_femella = ampleTDV[_+1] - 0.75)


        return trans_list

    def create_PP_positions_encaix(self, ampleTDV, matrixPosX, matrixPosY, matrixcentrar, matrixMostrar, offsetY, offsetX, orientacio, barraLlargadaReal):
        """
        Create a list of transformations to position all TD verticals around the table

        Returns:
            List of Matrix3D transformations
        """


        self.matrixPosXAux = matrixPosX
        self.matrixPosYAux = matrixPosY

        #chair_seat_width = self.DistanciaEntreTD
        distanciaentreTDVerticals = 1170

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
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Posicio = self.matrixPosXAux[_-2] + ampleTDV[_-2]/2 - ampleTDV[_+1]/2 + ampleTDV[0]/2) #offsetX*100
                        self.EncaixosPar[_] = self.EncaixosPar[_]._replace(Posicio = matrixPosX[_-2] + ampleTDV[_-2]/2 - ampleTDV[_+1]/2 + ampleTDV[0]/2 - (ampleTDV[_-2]/2 + ampleTDV[0]/2) + ampleTDV[0] )
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
                deltax += distanciaentreTDVerticals  #- (ampleTDV[_-2] - 30)/2




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
                #self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Posicio = self.matrixPosXAux[_-1] + ampleTDV[_-1]/2 - ampleTDV[_+1]/2 + ampleTDV[0]/2)
                self.EncaixosPar[TDV_count+2] = self.EncaixosPar[TDV_count+2]._replace(Posicio = matrixPosX[_-1] + ampleTDV[_-1]/2 - ampleTDV[_+1]/2 + ampleTDV[0]/2 - (ampleTDV[_-1]/2 + ampleTDV[0]/2) )
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



    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''

        #codis:
        ref_enc_llargada = 0.00
        self.codi_pestanyes = "#Z:@"+str(ref_enc_llargada)+"@#"

        #if self.BarraAmple > self.BarraAltura:
        self.codi_mesures = "#X:@"+str(self.BarraAmple)+"Y:@"+str(self.BarraAltura)+"@|Z:@" +str(self.BarraLlargada)+"@|T:@"+str(self.BarraGruix)+"@#"
        #else:
        #    self.codi_mesures = "#X:@"+str(self.BarraAltura)+"Y:@"+str(self.BarraAmple)+"@|Z:@" +str(self.BarraLlargada)+"@|T:@"+str(self.BarraGruix)+"@#"

        self.cara_a = "#L" + str(self.invertirPeca) #Esq
        self.cara_a_inv = "" #Esq Invertida

        self.cara_b = "#" #Dre
        self.cara_c = "#" #Sup
        self.cara_d = "#" #Inf

        self.cara_b_inv = "" #Dre Invertida
        self.cara_c_inv = "" #Sup Invertida
        self.cara_d_inv = "" #Inf Invertida

        self.codi_femella = "#"

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
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraLlargada,
                                                            self.BarraAmple - self.BarraGruix,
                                                            self.BarraAltura - self.BarraGruix)

        #es crea el vector per posicionarlo al centre i es resten els volums
        alturaInt = 0
        if self.invertirSup:
            alturaInt = self.BarraGruix
        if self.invertirPeca:
            vector = AllplanGeo.Vector3D(0, self.BarraGruix, alturaInt)
        else:
            vector = AllplanGeo.Vector3D(0, 0, alturaInt)

        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)


        #retall inici
        geometry3 = AllplanGeo.Polyhedron3D.CreateCuboid(self.retallInici,
                                                            self.BarraAmple ,
                                                            self.BarraAltura )

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(0, 0, 0)
        geometry3 = AllplanGeo.Move(geometry3, vector)

        if self.retallInici != 0:
            geometry = AllplanGeo.MakeBoolean(geometry[3], geometry3)
            #geometry = geometry[3]

        '''
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
        '''

        return  geometry[3]
        #return  geometry[3]

    #FEMELLES
    def create_femelles(self, nFemella):
        dades_femelles = self.Femelles
        Dfemella = dades_femelles[nFemella]

        #print(Dfemella)

        posicio = Dfemella[1]


        PosFemellaX = Dfemella[2] - 0.25

        #print("---------------")
        #print("PosFemellaX: " + str(PosFemellaX))
        #print("self.retallInici: " + str(self.retallInici))

        if PosFemellaX >= self.retallInici -1 and (PosFemellaX < self.retallInici + self.llargBarraAmbRetallFinal or self.llargBarraAmbRetallFinal == 0):

            #codi = "FEM@|P:@"+str(PosFemellaX)+"@#"
            #posinv = self.BarraLlargada - PosFemellaX
            #codi_inv = "FEM@|P:@"+str(posinv)+"@#"



            if Dfemella[4] != 0:
                Separacio_forat_femella = Dfemella[4] + 0.5
            else:
                Separacio_forat_femella = self.Separacio_forat_femella
                PosFemellaX = Dfemella[2] - Separacio_forat_femella/2 - self.Altura_forat_femella/2 - 0.25

            if Dfemella[3] != 0:
                PosFemellaY = Dfemella[3]
                ample_forat_fem = 15
            else:
                if posicio == "Dre" or posicio == "Esq":
                    PosFemellaY = self.BarraAmple/2 - self.Ample_forat_femella/2
                else:
                    PosFemellaY = self.BarraAltura/2 - self.Ample_forat_femella/2

                ample_forat_fem = self.Ample_forat_femella

            PosFemellaY -= 0.25
            self.codi_femella += "["+str(nFemella+1)+"]C:@"+str(posicio)+"@|P:@"+str(PosFemellaX)+"|Y:@"+str(PosFemellaY)+"@#"

            codi = "FEM@|P:@"+str(PosFemellaX)+"|Y:@"+str(PosFemellaY)+"|A:@"+str(ample_forat_fem)+"@#"
            Y_inv = self.BarraAmple - PosFemellaY - self.Ample_forat_femella
            posinv = self.BarraLlargada - PosFemellaX
            codi_inv = "FEM@|P:@"+str(posinv)+"|Y:@"+str(Y_inv)+"|A:@"+str(ample_forat_fem)+"@#" #+ self.cara_b_inv

            #crear 2 cubs
            femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, ample_forat_fem + 0.5 ,3.1)

            #vector = AllplanGeo.Vector3D(0, self.BarraGruix/2 - self.llargada_femella/2 , PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaX , PosFemellaY , 0)
            femella_12 = AllplanGeo.Move(femella_1, vector)
            #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix, PosFemellaX )
            vector = AllplanGeo.Vector3D(PosFemellaX  + Separacio_forat_femella , PosFemellaY, 0)
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

                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, 3.1,ample_forat_fem + 0.5 )

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
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.Altura_forat_femella, ample_forat_fem + 0.5 ,3.1)

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
                femella_1 = AllplanGeo.Polyhedron3D.CreateCuboid(self.Altura_forat_femella, 3.1,ample_forat_fem +0.5)

                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 + self.Separacio_forat_femella/2 , self.BarraAltura - self.BarraGruix, PosFemellaX )
                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.amplada_femella/2, self.BarraAltura/2 - self.llargada_femella/2 - self.BarraGruix , PosFemellaX )
                vector = AllplanGeo.Vector3D(PosFemellaX, 0, PosFemellaY )
                femella_12 = AllplanGeo.Move(femella_1, vector)
                #vector = AllplanGeo.Vector3D(self.BarraAmple/2 - self.Separacio_forat_femella/2 - self.Ample_forat_femella, self.BarraAltura - self.BarraGruix , PosFemellaX )
                vector = AllplanGeo.Vector3D( PosFemellaX + Separacio_forat_femella , 0, PosFemellaY)
                femella_11 = AllplanGeo.Move(femella_1, vector)

                femella = AllplanGeo.MakeBoolean(femella_11, femella_12)

                return femella[2]

            else:
                femella = femella[2]

            return femella
        vector = AllplanGeo.Vector3D(-1, 0, 0)
        return AllplanGeo.Move(AllplanGeo.Polyhedron3D.CreateCuboid(1, 1,1), vector)


    def create_forats(self, num_forat):
        dades_forats = self.ForatsPar
        DForats = dades_forats[num_forat]

        orientacio = DForats.orientacio
        posForat = DForats.Posicio
        posForatY = DForats.PosicioY
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
        posForatY = Dforat.PosicioY
        forat_alc = Dforat.Llargada
        forat_ampl = Dforat.Amplada
        esCompleta = Dforat.Complet
        forat_alcB = Dforat.LlargadaB
        forat_amplB = Dforat.AmpladaB

        vector = AllplanGeo.Vector3D(0,0,0)
        vectorB = AllplanGeo.Vector3D(0,0,0)

        codi1 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"y"+str(posForatY)+"#"
        codi2 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"y"+str(posForatY)+"#"
        posinv = self.BarraLlargada - posForat
        codi_inv1 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"y"+str(posForatY)+"#"
        codi_inv2 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"y"+str(posForatY)+"#"

        if orientacio == 'Inf' :#or (orientacio == 'Sup' and esCompleta):#V
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , self.BarraAmple/2 - forat_ampl/2 , 0)
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , posForatY - forat_ampl/2, 0)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, self.BarraAmple/2 - forat_amplB/2, self.BarraAltura - self.BarraGruix)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, posForatY - forat_amplB/2, self.BarraAltura - self.BarraGruix)
            self.cara_d += codi1
            self.cara_d_inv += codi_inv1
            self.cara_c += codi2
            self.cara_c_inv += codi_inv2
        elif orientacio == 'Dre':# or (orientacio == 'Esq' and esCompleta):#v
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , 0, self.BarraAltura/2 - forat_ampl/2 )
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2 , 0, posForatY - forat_ampl/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - forat_amplB/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2, self.BarraAmple - self.BarraGruix, posForatY - forat_amplB/2 )
            self.cara_b += codi1
            self.cara_b_inv += codi_inv1
            self.cara_a += codi2
            self.cara_a_inv += codi_inv2
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, self.BarraAmple/2 - forat_ampl/2, self.BarraAltura - self.BarraGruix)
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, posForatY -forat_ampl/2, self.BarraAltura - self.BarraGruix)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 , self.BarraAmple/2 - forat_amplB/2 , 0)
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 ,posForatY - forat_amplB/2 , 0)
            self.cara_c += codi1
            self.cara_c_inv += codi_inv1
            self.cara_d += codi2
            self.cara_d_inv += codi_inv2
        else:
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, self.BarraAmple - self.BarraGruix, self.BarraAltura/2 - forat_ampl/2 )
            vector = AllplanGeo.Vector3D(posForat - forat_alc/2, self.BarraAmple - self.BarraGruix, posForatY - forat_ampl/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 , 0, self.BarraAltura/2 - forat_amplB/2 )
            vectorB = AllplanGeo.Vector3D(posForat - forat_alcB/2 , 0, posForatY - forat_amplB/2 )
            self.cara_a += codi1
            self.cara_a_inv += codi_inv1
            self.cara_b += codi2
            self.cara_b_inv += codi_inv2
        return vector, vectorB



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

