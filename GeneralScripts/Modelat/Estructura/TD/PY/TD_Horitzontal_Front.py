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

print('Load TD_Horitzontal_Front.py')


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

    TDHoritzontal = TD_Horitzontal_Front(build_ele.DistanciaEntreTD.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,
                                build_ele.ColisPar.value, build_ele.PotaPar.value, #matrius
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
                        AllplanBaseElements.AttributeString(2103, "TH "),
                        AllplanBaseElements.AttributeString(508, "TUB HOR")]

    pythonpart = PythonPart ("PP_TD_Horitzontal",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class TD_Horitzontal_Front():
    """
    Definition of class Table
    """

    def __init__(self, DistanciaEntreTD, BarraAmple, BarraAltura, BarraLlargada, BarraGruix,
                    IsUseGlobalProp, FounColor, BarraLayer,
                    ColisPar, PotaPar, #matrius
                    Ample_forat_femella, Altura_forat_femella, Separacio_forat_femella,
                    Femelles, #matriu
                    posicio_centre_masses,
                    IsFirstCancam, Dis1cancam,
                    IsSecondCancam, Dis2cancam,
                    PestanyaSuperior, PestanyaInferior,
                    EncaixosPar):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """
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
        self.EncaixosPar = EncaixosPar

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
        param_list.append ("BarraAmple = %s\n" % self.BarraAmple)
        param_list.append ("BarraAltura = %s\n" % self.BarraAltura)
        param_list.append ("BarraLlargada = %s\n" % self.BarraLlargada)
        param_list.append ("BarraGruix = %s\n" % self.BarraGruix)
        param_list.append ("IsUseGlobalProp = %s\n" % self.IsUseGlobalProp)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)
        param_list.append ("ColisPar = %s\n" % self.ColisPar)#matriu
        param_list.append ("PotaPar = %s\n" % self.PotaPar)#matriu
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
        param_list.append ("EncaixosPar = %s\n" % self.EncaixosPar)
        return param_list

    def __repr__(self):
        return 'TD_Horitzontal(DistanciaEntreTD=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s'\
            'BarraLayer=%s'\
            'ColisPar=%s, PotaPar=%s'\
            'Ample_forat_femella=%s, Altura_forat_femella=%s'\
            'Separacio_forat_femella=%s, Femelles=%s'\
            'posicio_centre_masses=%s, IsFirstCancam=%s'\
            'Dis1cancam=%s, IsSecondCancam=%s'\
            'Dis2cancam=%s, PestanyaSuperior=%s'\
            'PestanyaInferior=%s, EncaixosPar=%s)\n' \
            % (self.DistanciaEntreTD, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer,
               self.ColisPar, self.PotaPar,
               self.Ample_forat_femella, self.Altura_forat_femella,
               self.Separacio_forat_femella, self.Femelles,
               self.posicio_centre_masses, self.IsFirstCancam,
               self.Dis1cancam, self.IsSecondCancam,
               self.Dis2cancam, self.PestanyaSuperior,
               self.PestanyaInferior, self.EncaixosPar )

    def hash(self):
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

        if self.BarraAmple > self.BarraAltura:#self.BarraLlargada > self.BarraAltura:#if self.BarraAmple > self.BarraAltura:
            return str(self.BarraAmple) + "x " + str(self.BarraAltura) + "x " + str(self.BarraGruix)

        return str(self.BarraAltura) + "x " + str(self.BarraAmple) + "x " + str(self.BarraGruix)
        #return str(self.BarraAltura) + "x " + str(self.BarraLlargada) + "x " + str(self.BarraGruix)

    def get_llargada(self):

        return str(self.BarraAmple)

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

    def return_femelles(self):
        return self.Femelles


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
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraLlargada - self.BarraGruix*2,
                                                            self.BarraAmple ,
                                                            self.BarraAltura - self.BarraGruix*2)

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(self.BarraGruix, 0,  self.BarraGruix)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)



        return  geometry[3]



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

