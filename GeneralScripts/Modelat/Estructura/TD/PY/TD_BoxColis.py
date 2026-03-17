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

print('Load TD_BoxColis.py')


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

    TDBoxColis = BoxColis(random.random() * 3600, build_ele.Ample.value, build_ele.BarraAltura.value, build_ele.BarraGruix.value,
                            build_ele.ColisPar.value,0,
                            build_ele.FounColor.value, build_ele.BarraLayer.value)

    #build_ele.BarraAltura.value = build_ele.Ample.value

    if not TDBoxColis.is_valid():
        return ([], [])

    handle_list = TDBoxColis.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDBoxColis.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2103, "TH TDBoxColis ")]

    '''
    pythonpart = PythonPart ("TD_CilindreCancam",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)
    '''

    pythonpart = PythonPart ("PP_TD_Horitzontal",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)


    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class BoxColis():
    """
    Definition of class Table
    """

    def __init__(self,zUnique,  Ample, BarraAltura, BarraGruix,
                 ColisPar, i,
                 FounColor, BarraLayer):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """
        self.zUnique = zUnique
        self.Ample = Ample
        self.BarraAltura = BarraAltura
        self.BarraGruix = BarraGruix

        self.identificador = i

        self.ColisPar = ColisPar
        self.FounColor = FounColor
        self.BarraLayer = BarraLayer

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.Ample.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("Ample",
                                        AllplanGeo.Point3D(0, self.Ample, self.BarraAltura),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Ample", HandleDirection.y_dir),
                                         ("BarraAltura", HandleDirection.z_dir)],
                                        HandleDirection.yz_dir),
                                        HandleProperties("BarraLlargada",
                                        AllplanGeo.Point3D(self.BarraAltura, 0, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraLlargada", HandleDirection.x_dir)],
                                        HandleDirection.x_dir)
                      ]

        return handle_list

    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("zUnique = %s\n" % self.zUnique)
        param_list.append ("Ample = %s\n" % self.Ample)
        param_list.append ("BarraAltura = %s\n" % self.BarraAltura)
        param_list.append ("BarraGruix = %s\n" % self.BarraGruix)
        param_list.append ("ColisPar = %s\n" % self.ColisPar)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)

        return param_list

    def __repr__(self):

        return 'TD_BoxColis( zUnique=%s, Ample=%s , BarraAltura =%s, BarraGruix=%s'\
            'ColisPar=%s '\
            'FounColor=%s, BarraLayer=%s)\n '\
            % (self.zUnique, self.Ample, self.BarraAltura, self.BarraGruix,
               self.ColisPar,
               self.FounColor, self.BarraLayer )

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
        return "TD_BoxColis.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.Ample<= 0 :
            return False

        return True

    def getTDType(self) :
        return "CilindreCancam"

    def get_common_props(self):
        common_prop = self.get_foundation_common_props()
        return common_prop

    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''

        elements = []

        #self.add_atribute_codi_mesures(build_ele, _doc)

        #ele1 = self.create_barra()
        #barra = ele1
        barra = AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)

        #colis
        '''
        dades_colis = self.ColisPar
        i = 0
        for Icolis in dades_colis:
            colisActiu = Icolis[0]
            if colisActiu:
                #ele3 = self.create_colis_int(i)
                #barra = AllplanGeo.MakeBoolean(barra, ele3)
                #barra = barra[3]#Forat
                ele2 = self.create_colis(i)
                barra = AllplanGeo.MakeBoolean(barra, ele2)
                barra = barra[2]#Colis
            i += 1
        '''


        ele2 = self.create_colis(self.identificador)
        barra = AllplanGeo.MakeBoolean(barra, ele2)
        barra = barra[2]#Colis

        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]

        elements.append(AllplanBasisElements.ModelElement3D(common_prop, barra))


        return barra

    #BARRA
    def create_barra(self):
        '''
        Es crea dos cuboids, un amb l'ample, altura i llargada indicada, i el segon igual menys el gruix indicat,
        es fauna operació bool i es retorna el model coincident.

        return: Polyhedron3D
        '''
        #creació cuboid exterior
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( 1000, self.Ample, self.BarraAltura )
        #crear cuboid interior
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(1000,
                                                            self.Ample - self.BarraGruix*2,
                                                            self.BarraAltura - self.BarraGruix*2)

        #es crea el vector per posicionarlo al centre i es resten els volums
        vector = AllplanGeo.Vector3D(0, self.BarraGruix, self.BarraGruix)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)



        return  geometry[3]


    #COLIS
    def create_colis(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis[1]
        posColis = DColis[2]

        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada

        colis_forat_alc = 3
        #colis gruix 0.00900

        if orientacio == 'Inf' or orientacio == 'Sup':
            colis = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc + 18 , self.Ample, colis_forat_alc )
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_ampl, colis_forat_alc)

        else:
            colis = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc + 18, colis_forat_alc, self.BarraAltura)
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_forat_alc, colis_ampl)

        vector = self.vector_colis_int_bool(num_colis)
        colis_int = AllplanGeo.Move(colis_int, vector)

        vector = self.vector_colis(num_colis)
        colis = AllplanGeo.Move(colis, vector)

        colis = AllplanGeo.MakeBoolean(colis, colis_int)
        colis = colis[3]

        #axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Vector3D(1,0,0))
        #Angle = AllplanGeo.Angle(1.5708)#90Deg = 1.5708rad
        #colis = AllplanGeo.Rotate(colis,axis_point,Angle)

        return colis

    def vector_colis(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis[1]
        posColis = DColis[2]

        colis_alc = DColis.Llargada + 18
        colis_ampl = DColis.Amplada
        colis_alcada = 3

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), 0, -colis_alcada )
            vector = AllplanGeo.Vector3D(0 - (colis_alc/2) , 0, -colis_alcada )
            vector = AllplanGeo.Vector3D(0 - (colis_alc/2), 0, -3.1 )

        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), -colis_alcada, 0 )
            vector = AllplanGeo.Vector3D(0 - (colis_alc/2) , -colis_alcada-0.1, 0 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), 0, self.BarraAltura )
            vector = AllplanGeo.Vector3D(0- (colis_alc/2), 0, self.BarraAltura )
        else:
            vector = AllplanGeo.Vector3D(posColis - (colis_alc/2), self.Ample , 0)
            vector = AllplanGeo.Vector3D(0 - (colis_alc/2), self.Ample , 0)

        return vector

    def vector_colis_int_bool(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis[1]
        posColis = DColis[2]

        colis_alc = DColis.Llargada +18
        colis_ampl = DColis.Amplada
        colis_alcada = 3
        vector = AllplanGeo.Vector3D(0,0,0)
        colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc-self.BarraGruix*2, colis_alcada, self.BarraAltura - self.BarraGruix*4)

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2,  self.Ample/2 - colis_ampl/2, -colis_alcada )
            vector = AllplanGeo.Vector3D(0 + 18/2 - colis_alc/2,  self.Ample/2 - colis_ampl/2, -colis_alcada )
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2, -colis_alcada, self.BarraAltura/2 - colis_ampl/2 )
            vector = AllplanGeo.Vector3D(0 + 18/2 - colis_alc/2, -colis_alcada-0.1, self.BarraAltura/2 - colis_ampl/2 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2,  self.Ample/2 - colis_ampl/2, self.BarraAltura  )
            vector = AllplanGeo.Vector3D(0 + 18/2 - colis_alc/2,  self.Ample/2 - colis_ampl/2, self.BarraAltura  )
        else:
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2, self.Ample ,self.BarraAltura/2 - colis_ampl/2 )
            vector = AllplanGeo.Vector3D(0 + 18/2 - colis_alc/2, self.Ample ,self.BarraAltura/2 - colis_ampl/2 )

        return vector


    def create_colis_int(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis[1]
        posColis = DColis[2]

        colis_alc = DColis.Llargada
        colis_ampl = DColis.Amplada
        colis_forat_alc = 3

        if orientacio == 'Inf' or orientacio == 'Sup':
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, colis_ampl, self.BarraGruix)
        else:
            colis_int = AllplanGeo.Polyhedron3D.CreateCuboid(colis_alc, self.BarraGruix, colis_ampl)
        vector = self.vector_colis_int(num_colis)
        colis_int = AllplanGeo.Move(colis_int, vector)

        return colis_int

    def vector_colis_int(self, num_colis):
        dades_colis = self.ColisPar
        DColis = dades_colis[num_colis]

        orientacio = DColis[1]
        posColis = DColis[2]
        colis_alc = DColis.Llargada +18
        colis_ampl = DColis.Amplada
        vector = AllplanGeo.Vector3D(0,0,0)

        if orientacio == 'Inf':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2 , self.Ample/2 - colis_ampl/2 , 0)
        elif orientacio == 'Dre':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2 , 0, self.BarraAltura/2 - colis_ampl/2 )
        elif orientacio == 'Sup':
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2, self.Ample/2 - colis_ampl/2, self.BarraAltura - self.BarraGruix)
        else:
            vector = AllplanGeo.Vector3D(posColis + 18/2 - colis_alc/2, self.Ample - self.BarraGruix, self.BarraAltura/2 - colis_ampl/2 )

        return vector



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


        return common_prop

    def getAmplada(self):
        return self.amplada_femella

    def definir_amplada(self, amplada):
        self.amplada_femella = amplada

