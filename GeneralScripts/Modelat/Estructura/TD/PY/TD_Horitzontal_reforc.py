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

print('Load TD_Horitzontal_reforc.py')


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

    TDHoritzontal = PP_TD_Horitzontal_reforc(build_ele.zUnique.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value, build_ele.invertirPeca.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,
                                build_ele.EncaixosPar.value)

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

    pythonpart = PythonPart ("PP_TD_Horitzontal_reforc",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class PP_TD_Horitzontal_reforc():
    """
    Definition of class Table
    """

    #def __init__(self, zUnique, DistanciaEntreTD, BarraAmple, BarraAltura, BarraLlargada, BarraGruix, invertirPeca,
    def __init__(self, zUnique, BarraAmple, BarraAltura, BarraLlargada, BarraGruix, invertirPeca,
                    IsUseGlobalProp, FounColor, BarraLayer,
                    EncaixosPar):
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
        self.IsUseGlobalProp = IsUseGlobalProp
        self.FounColor = FounColor
        self.BarraLayer = BarraLayer
        self.EncaixosPar = EncaixosPar

        self.matrixPosXAux =[]
        self.matrixPosYAux =[]

        self.cara_a = ""
        self.cara_a_inv = ""

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
        param_list.append ("InvertirPeca = %s\n" % self.invertirPeca)
        param_list.append ("IsUseGlobalProp = %s\n" % self.IsUseGlobalProp)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)
        param_list.append ("EncaixosPar = %s\n" % self.EncaixosPar)
        return param_list

    def __repr__(self):
        #return 'TD_Horitzontal(zUnique=%s, DistanciaEntreTD=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s, invertirPeca=%s,' \
        return 'TD_Horitzontal(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s, invertirPeca=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s'\
            'BarraLayer=%s, EncaixosPar=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix, self.invertirPeca,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer, self.EncaixosPar  )

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

        return "#"

    def get_codi_cara_b_inv(self):

        return "#"

    def get_codi_cara_c(self):

        return "#"

    def get_codi_cara_c_inv(self):

        return "#"

    def get_codi_cara_d(self):

        return "#"

    def get_codi_cara_d_inv(self):

        return "#"

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



    def create_superior(self, pos:AllplanGeo.Vector3D):
        novaBarra = self.create()
        novaBarra = AllplanGeo.Move(novaBarra, pos)
        return novaBarra

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

        self.cara_a = "Reforç"
        self.cara_a_inv = ""
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
                                                            self.BarraAltura - self.BarraGruix)

        vector = AllplanGeo.Vector3D(self.BarraGruix, 0, self.BarraGruix)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)
        #geometry = AllplanGeo.MakeBoolean(geometry[3], geometry3)





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

        #codi_encaix
        #self.codi_encaix +=  "["+str(nEncaix+1)+"]C:@"+str(orientacio)+"@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
        posInvEnca = self.BarraLlargada - DEncaix[3]

        altura_fem = 3
        alcada_fem = 15

        if orientacio == "Dre":
            #self.cara_b += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            #self.cara_b_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_b_inv

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
            #self.cara_c += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            #self.cara_c_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_c_inv

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
            #self.cara_a += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            #self.cara_a_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_a_inv

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
            #self.cara_d += "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(DEncaix[3])+"@|Z:@"+str(Trans_ref_encaix)+"@#"
            #self.cara_d_inv =  "ENC@|T:@"+str(TePestanya)+"@|D:@"+str(profEncaix)+"@|P:@"+str(posInvEnca)+"@|Z:@"+str(Trans_ref_encaix)+"@#" + self.cara_d_inv

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


