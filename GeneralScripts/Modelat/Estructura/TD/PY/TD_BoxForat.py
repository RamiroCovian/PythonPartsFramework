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

print('Load TD_BoxForat.py')

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

    TDVertical = BoxForat(build_ele.zUnique.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value,
                               build_ele.ForatsPar.value) #matriu


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
                AllplanBaseElements.AttributeString(2103, "TV "),
                AllplanBaseElements.AttributeString(508, "TUB VER")]

    pythonpart = PythonPart ("BoxForat",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()


    return (model_elem_list, handle_list)


class BoxForat():
    """ implementation of the TD BAR 1
    """

    def __init__(self, zUnique = random.random() * 3600, BarraAmple = 30, BarraAltura = 30, BarraLlargada = 260, BarraGruix = 1.5,
                    IsUseGlobalProp = False, FounColor = 1, BarraLayer = 2,
                    ForatsPar = [], isHor = False, nForat = 0):
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
        self.ForatsPar = ForatsPar #matrius
        self.isHor = isHor
        self.nForat = nForat

        self.EncaixosAux = []

        self.m_TD_Vertical = None


    def set_params_list(self, llistadeDades):

        self.BarraAmple = llistadeDades[0]
        self.BarraAltura = llistadeDades[1]
        self.BarraLlargada = llistadeDades[2]
        self.BarraGruix = llistadeDades[3]
        self.IsUseGlobalProp = llistadeDades[4]
        self.FounColor = llistadeDades[5]
        self.BarraLayer = llistadeDades[6]
        self.ForatsPar = llistadeDades[7] #matrius

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
        param_list.append ("ForatsPar = %s\n" % self.ForatsPar)#matriu
        param_list.append ("nForat = %s\n" % self.nForat)

        return param_list

    def __repr__(self):
        return 'BoxForat(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s'\
            'BarraLayer=%s'\
            'ForatsPar=%s, nForat=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix,
               self.IsUseGlobalProp, self.FounColor,
               self.BarraLayer,
               self.ForatsPar, self.nForat)

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
        return "TD_BoxForat.py"

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

        return str(self.ForatsPar[self.nForat].ProfunditatTFF) + "x " + str(30) + "x " + str(self.BarraGruix)

    def get_llargada(self):

        return str(100)

    def get_codi_pota(self):

        return self.codi_pota

    def get_codi_pota_inv(self):

        return "#" + self.codi_pota_inv

    def get_codi_cara_a(self):

        return "#TFF"#self.cara_a

    def get_codi_cara_a_inv(self):

        return "#"# + self.cara_a_inv

    def get_codi_cara_b(self):

        return "#"#self.cara_b

    def get_codi_cara_b_inv(self):

        return "#"# + self.cara_b_inv

    def get_codi_cara_c(self):

        return "#"#self.cara_c

    def get_codi_cara_c_inv(self):

        return "#"# + self.cara_c_inv

    def get_codi_cara_d(self):

        return "#"#self.cara_d

    def get_codi_cara_d_inv(self):

        return "#"# + self.cara_d_inv

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




#-------------------CREAR BARRA --------------+
    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''
        #print("Create model TD 1")
        #

        #codis:
        ref_enc_llargada = 0.00
        self.codi_pestanyes = "#Z:@"+str(ref_enc_llargada)+"@#"
        self.codi_cancam = "#"
        self.codi_colis = "#"
        self.codi_encaix = "#"
        self.codi_femella = "#"
        #if self.BarraAmple > self.BarraAltura:
        self.codi_mesures = "#X:@"+str(self.ForatsPar[self.nForat].ProfunditatTFF)+"Y:@"+str(30)+"@|Z:@" +str(100)+"@|T:@"+str(self.BarraGruix)+"@#"
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
        #ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        #barra = ele1
        #barra = AllplanGeo.Polyhedron3D.CreateCuboid(0.1,0.1,0.1)

        hihaForat= False

        #Forats
        dades_Forats = self.ForatsPar
        '''
        i = 0
        for iForat in dades_Forats:
            foratActiu = iForat.Forat
            if foratActiu and iForat.MostrarBox:
                ele2 = self.create_forats(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[2]
            i += 1
        '''
        if self.nForat < len(dades_Forats):
            foratActiu = dades_Forats[self.nForat].Forat
            if foratActiu :#and dades_Forats[self.nForat].MostrarBox:
                ele2 = self.create_forats(self.nForat)
                #barra = AllplanGeo.MakeBoolean(barra, ele2)
                #barra = barra[2]
                barra = ele2
                hihaForat = True

        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]
        self.m_TD_Vertical = barra

        if self.isHor:
            vector = AllplanGeo.Vector3D(0, 1, 0)
            Point = AllplanGeo.Point3D(0, 0, 0)

            axis = AllplanGeo.Axis3D(Point, vector)
            #Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
            Angle = AllplanGeo.Angle.FromDeg(90)
            barra = AllplanGeo.Rotate(barra, axis, Angle) # type: ignore


            vector = AllplanGeo.Vector3D(1, 0, 0)
            Point = AllplanGeo.Point3D(0, 0, 0)

            axis = AllplanGeo.Axis3D(Point, vector)
            #Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
            Angle = AllplanGeo.Angle.FromDeg(90)
            barra = AllplanGeo.Rotate(barra, axis, Angle) # type: ignore


        elements.append(AllplanBasisElements.ModelElement3D(common_prop, barra))

        #------------------------
        pyp_util = PythonPartUtil()

        #self.model_ele_list = BuildingElementAttributeList()

        #Atributs
        attribute_list = BuildingElementAttributeList()


        pyp_util.add_attribute_list(attribute_list)


        pyp_util.add_pythonpart_view_2d3d(elements)
        #------------------------

        if not hihaForat:
            barra = AllplanGeo.Polyhedron3D.CreateCuboid(0.1,0.1,0.1)
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
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple - self.BarraGruix*2,
                                                        self.BarraAltura - self.BarraGruix*2,
                                                        self.BarraLlargada)
                                                        #self.BarraLlargada - self.BarraGruix*2)

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(self.BarraGruix, self.BarraGruix, 0)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)

        return  geometry[3]



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

        profunditatTFF = DForats.ProfunditatTFF


        altura = self.BarraGruix
        #if esCompleta and (orientacio == 'Sup' or orientacio == 'Inf'):
        #    altura = self.BarraAltura
        #elif esCompleta and (orientacio == 'Esq' or orientacio == 'Dre'):
        #    altura = self.BarraAmple
        #else:
        #    altura = self.BarraGruix

        if orientacio == 'Inf' or orientacio == 'Sup':
            BoxExterior =  AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple,15, forat_alc+60)
            BoxExterior =  AllplanGeo.Polyhedron3D.CreateCuboid(30,profunditatTFF, 100)
            BoxInterior =  AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraAmple-self.BarraGruix*2, 15-self.BarraGruix*2, forat_alc+60 - self.BarraGruix*2)
            BoxInterior =  AllplanGeo.Polyhedron3D.CreateCuboid(30-self.BarraGruix*2, profunditatTFF-self.BarraGruix*2, 100 )
        else:
            BoxExterior =  AllplanGeo.Polyhedron3D.CreateCuboid(15, self.BarraAltura, forat_alc+60)
            BoxExterior =  AllplanGeo.Polyhedron3D.CreateCuboid(profunditatTFF, 30, 100)
            BoxInterior =  AllplanGeo.Polyhedron3D.CreateCuboid(15-self.BarraGruix*2, self.BarraAltura-self.BarraGruix*2, 100 )
            BoxInterior =  AllplanGeo.Polyhedron3D.CreateCuboid(profunditatTFF-self.BarraGruix*2, 30-self.BarraGruix*2, 100 )


        vectorInterior = AllplanGeo.Vector3D(self.BarraGruix, self.BarraGruix, 0)
        BoxInterior = AllplanGeo.Move(BoxInterior, vectorInterior )

        BoxExterior = AllplanGeo.MakeBoolean(BoxExterior, BoxInterior)
        BoxExterior = BoxExterior[3]


        if orientacio == 'Inf' or orientacio == 'Sup':
            #forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(altura, forat_alc, forat_ampl)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_ampl, altura, forat_alc)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(20, altura, 50)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid(forat_amplB, altura, forat_alcB)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid(10, altura, 10)

        else:
            #forat_int = AllplanGeo.Polyhedron3D.CreateCuboid(forat_alc, altura, forat_ampl)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid( altura, forat_ampl, forat_alc)
            forat_int = AllplanGeo.Polyhedron3D.CreateCuboid( altura, 20, 50)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid( altura, forat_amplB, forat_alcB)
            forat_intB = AllplanGeo.Polyhedron3D.CreateCuboid( altura, 10, 10)


        vector, vectorB= self.vector_forats_int(num_forat)

        if orientacio == 'Inf' :#or orientacio == 'Sup':
            vectorCentral = AllplanGeo.Vector3D(self.BarraAmple/2 - 30/2,0,vector.Z-25)
        elif orientacio == 'Sup':
            vectorCentral = AllplanGeo.Vector3D(self.BarraAmple/2 - 30/2,0,vector.Z-25)
        else:
            vectorCentral = AllplanGeo.Vector3D(0,self.BarraAltura/2-30/2,vector.Z-25)

        BoxExterior = AllplanGeo.Move(BoxExterior, vectorCentral )

        if esCompleta:
            forat_int = AllplanGeo.Move(forat_int, vector)
            forat_intB = AllplanGeo.Move(forat_intB, vectorB)
            forat_intC = AllplanGeo.MakeBoolean(forat_int, forat_intB)
            forat_int = forat_intC[2]
        else:
            forat_int = AllplanGeo.Move(forat_int, vector)

        BoxExterior = AllplanGeo.MakeBoolean(BoxExterior, forat_int)

        foratsAux = self.vector_forats_int_Aux(num_forat, vectorCentral, vector)
        #return foratsAux[2]
        BoxExterior = AllplanGeo.MakeBoolean(BoxExterior[3], foratsAux)

        if orientacio == "Inf":
            vectorPos = AllplanGeo.Vector3D(0,-profunditatTFF,0)

        elif orientacio == "Sup":
            vectorPos = AllplanGeo.Vector3D(0,self.BarraAltura,0)

        elif orientacio == "Esq":
            vectorPos = AllplanGeo.Vector3D(self.BarraAmple,0,0)

        elif orientacio == "Dre":
            vectorPos = AllplanGeo.Vector3D(-profunditatTFF,0,0)

        else:
            vectorPos = AllplanGeo.Vector3D(0,0,0)
            print("Orientació no valida")

        BoxExterior = AllplanGeo.Move(BoxExterior[3], vectorPos)
        return BoxExterior

    def vector_forats_int_Aux(self, num_forat, vectorCentral, vector):
        dades_forat = self.ForatsPar
        Dforat = dades_forat[num_forat]

        orientacio = Dforat.orientacio
        posForat = Dforat.Posicio
        forat_alc = Dforat.Llargada
        forat_ampl = Dforat.Amplada
        esCompleta = Dforat.Complet
        forat_alcB = Dforat.LlargadaB
        forat_amplB = Dforat.AmpladaB

        ProfunditatTFF = Dforat.ProfunditatTFF


        if orientacio == 'Inf' :#or (orientacio == 'Sup' and esCompleta):#V
            foratSup1 = AllplanGeo.Polyhedron3D.CreateCuboid(10 , self.BarraGruix, 10)
            foratSup2 = AllplanGeo.Polyhedron3D.CreateCuboid(3 , self.BarraGruix, 3)

            vectorSup = AllplanGeo.Vector3D(3.5 ,ProfunditatTFF-self.BarraGruix,3.5)
            foratSup2 = AllplanGeo.Move(foratSup2, vectorSup)

            vectorSup = AllplanGeo.Vector3D(0 , 0,0)
            foratSup1 = AllplanGeo.Move(foratSup1, vectorSup)

            foratSup = AllplanGeo.MakeBoolean(foratSup1, foratSup2)
            foratSup = foratSup[2]
            foratInf = foratSup

            vectorSup = AllplanGeo.Vector3D( self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z+forat_alc+10)
            vectorSup = AllplanGeo.Vector3D( self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z+100-15-25)
            foratSup = AllplanGeo.Move(foratSup, vectorSup)

            vectorInf = AllplanGeo.Vector3D( self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z-20)
            foratInf = AllplanGeo.Move(foratInf, vectorInf)

            foratsAux = AllplanGeo.MakeBoolean(foratSup, foratInf)
        elif orientacio == 'Dre' :#or (orientacio == 'Esq' and esCompleta):#v
            foratSup1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix,10 , 10)
            foratSup2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix,3 , 3)

            vectorSup = AllplanGeo.Vector3D(15-self.BarraGruix,3.5 ,3.5)
            foratSup2 = AllplanGeo.Move(foratSup2, vectorSup)

            vectorSup = AllplanGeo.Vector3D(0,0 ,0)
            foratSup1 = AllplanGeo.Move(foratSup1, vectorSup)

            foratSup = AllplanGeo.MakeBoolean(foratSup1, foratSup2)
            foratSup = foratSup[2]
            foratInf = foratSup

            vectorSup = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z+10)
            vectorSup = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z+100-25-15)
            foratSup = AllplanGeo.Move(foratSup, vectorSup)

            vectorInf = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z-20)
            foratInf = AllplanGeo.Move(foratInf, vectorInf)

            foratsAux = AllplanGeo.MakeBoolean(foratSup, foratInf)
        elif orientacio == 'Sup':

            foratSup1 = AllplanGeo.Polyhedron3D.CreateCuboid(10 , self.BarraGruix, 10)
            foratSup2 = AllplanGeo.Polyhedron3D.CreateCuboid(3 , self.BarraGruix, 3)

            vectorSup = AllplanGeo.Vector3D(3.5 ,0,3.5)
            foratSup2 = AllplanGeo.Move(foratSup2, vectorSup)

            vectorSup = AllplanGeo.Vector3D(0 ,ProfunditatTFF-self.BarraGruix,0)
            foratSup1 = AllplanGeo.Move(foratSup1, vectorSup)

            foratSup = AllplanGeo.MakeBoolean(foratSup1, foratSup2)
            foratSup = foratSup[2]
            foratInf = foratSup

            vectorSup = AllplanGeo.Vector3D(self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z+forat_alc+10)
            vectorSup = AllplanGeo.Vector3D(self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z+100-15-25)
            foratSup = AllplanGeo.Move(foratSup, vectorSup)

            vectorInf = AllplanGeo.Vector3D(self.BarraAmple/2 - 5,vectorCentral.Y,vector.Z-20)
            foratInf = AllplanGeo.Move(foratInf, vectorInf)

            foratsAux = AllplanGeo.MakeBoolean(foratSup, foratInf)
        else:
            foratSup1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix,10 , 10)
            foratSup2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraGruix,3 , 3)

            vectorSup = AllplanGeo.Vector3D(0,3.5 ,3.5)
            foratSup2 = AllplanGeo.Move(foratSup2, vectorSup)

            vectorSup = AllplanGeo.Vector3D(ProfunditatTFF-self.BarraGruix,0 ,0)
            foratSup1 = AllplanGeo.Move(foratSup1, vectorSup)

            foratSup = AllplanGeo.MakeBoolean(foratSup1, foratSup2)
            foratSup = foratSup[2]
            foratInf = foratSup

            vectorSup = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z+10)
            vectorSup = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z+100-25-15)
            foratSup = AllplanGeo.Move(foratSup, vectorSup)

            vectorInf = AllplanGeo.Vector3D(0,self.BarraAltura/2-5,vector.Z-20)
            foratInf = AllplanGeo.Move(foratInf, vectorInf)

            foratsAux = AllplanGeo.MakeBoolean(foratSup, foratInf)
        return foratsAux [2]


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

        ProfunditatTFF = Dforat.ProfunditatTFF


        vector = AllplanGeo.Vector3D(0,0,0)
        vectorB = AllplanGeo.Vector3D(0,0,0)

        codi1 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"#"
        codi2 = "FOR@|P:@"+str(posForat)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"#"
        posinv = self.BarraLlargada - posForat
        codi_inv1 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alc)+"x"+str(forat_ampl)+"#"
        codi_inv2 = "FOR@|P:@"+str(posinv)+"@"+str(forat_alcB)+"x"+str(forat_amplB)+"#"

        if orientacio == 'Inf' :#or (orientacio == 'Sup' and esCompleta):#V
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_ampl/2, 0 , posForat - forat_alc/2)
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - 20/2, 0 , posForat - 50/2)
            vectorB = AllplanGeo.Vector3D( self.BarraAmple/2 - 10/2 , ProfunditatTFF  - self.BarraGruix , posForat - 10/2)
            self.cara_d += codi1
            self.cara_d_inv += codi_inv1
            self.cara_c += codi2
            self.cara_c_inv += codi_inv2
        elif orientacio == 'Dre' :#or (orientacio == 'Esq' and esCompleta):#v
            vector = AllplanGeo.Vector3D(0, self.BarraAltura/2 - forat_ampl/2,  posForat - forat_alc/2)
            vector = AllplanGeo.Vector3D(0, self.BarraAltura/2 - 20/2,  posForat - 50/2)
            vectorB = AllplanGeo.Vector3D(ProfunditatTFF - self.BarraGruix , 5 + self.BarraAltura/2 - forat_amplB/2, 20 + posForat - forat_alcB/2)
            self.cara_b += codi1
            self.cara_b_inv += codi_inv1
            self.cara_a += codi2
            self.cara_a_inv += codi_inv2
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - forat_ampl/2 , ProfunditatTFF  - self.BarraGruix , posForat - forat_alc/2)
            vector = AllplanGeo.Vector3D( self.BarraAmple/2 - 20/2 , ProfunditatTFF  - self.BarraGruix , posForat - 50/2)
            vectorB = AllplanGeo.Vector3D( self.BarraAmple/2 - 10/2, 0 , posForat - 10/2)
            self.cara_c += codi1
            self.cara_c_inv += codi_inv1
            self.cara_d += codi2
            self.cara_d_inv += codi_inv2
        else:
            vector = AllplanGeo.Vector3D(ProfunditatTFF - self.BarraGruix , self.BarraAltura/2 - forat_ampl/2,  posForat - forat_alc/2)
            vector = AllplanGeo.Vector3D(ProfunditatTFF - self.BarraGruix , self.BarraAltura/2 - 20/2,  posForat - 50/2)
            vectorB = AllplanGeo.Vector3D(0, 5 + self.BarraAltura/2 - forat_amplB/2,  20 + posForat - forat_alcB/2)
            self.cara_a += codi1
            self.cara_a_inv += codi_inv1
            self.cara_b += codi2
            self.cara_b_inv += codi_inv2
        return vector, vectorB



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
