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

import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import subprocess
from TypeCollections.ModelEleList import ModelEleList



def install_packages(package):
    prg_path = AllplanSettings.AllplanPaths.GetPrgPath() + "\\"

    target_dir = f"{AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()}PythonParts-site-packages"
    print("target_dir ETC: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )

    target_dir = (
        f"{AllplanSettings.AllplanPaths.GetUsrPath()}Local\\PythonParts-site-packages"
    )
    print("target_dir USR: ")
    print(target_dir)
    subprocess.check_call(
        [
            prg_path + "Python\\Python.exe",
            "-m",
            "pip",
            "install",
            "--target",
            target_dir,
            "--upgrade",
            package,
        ]
    )


try:
    import formulas as formulas
except ImportError:
    install_packages("formulas")
    print("instalando paquetes: formulas")
    import formulas as formulas

try:
    import schedula as sh
except ImportError:
    install_packages("schedula")
    print("instalando paquetes: schedula")
    import schedula as sh

try:
    import numpy as np
except ImportError:
    install_packages("numpy")
    print("instalando paquetes: numpy")
    import numpy as np

try:
    import regex as rg
except ImportError:
    install_packages("regex")
    print("instalando paquetes: regex")
    import regex as rg

try:
    import six as six
except ImportError:
    install_packages("six")
    print("instalando paquetes: regex")
    import six as six


print('Load Angulars.py')


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
    TDHoritzontal = Angulars(build_ele.zUnique.value, build_ele,  build_ele.Ample.value, build_ele.Altura.value, build_ele.Llargada.value, build_ele.nEncaixos.value)

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not TDHoritzontal.is_valid():
        return ([], [])


    handle_list = TDHoritzontal.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDHoritzontal.create())])]

    attr_list = [#AllplanBaseElements.AttributeString(2431, TDHoritzontal.get_codi_mesures()),
                        AllplanBaseElements.AttributeString(2445, TDHoritzontal.get_seccio()),
                        AllplanBaseElements.AttributeString(220, TDHoritzontal.get_llargada()),
                        AllplanBaseElements.AttributeString(2103, "TH SUP "),
                        AllplanBaseElements.AttributeString(508, "TUB HOR")]

    pythonpart = PythonPart ("Angulars",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class Angulars():
    """
    Definition of class Table
    """

    #def __init__(self, zUnique, DistanciaEntreTD, BarraAmple, BarraAltura, BarraLlargada, BarraGruix, invertirPeca,
    def __init__(self, build_ele, zUnique, BarraAmple, BarraAltura, BarraLlargada, Gruix, nEncaixos, invertirPared = False, angle = [(AllplanGeo.Point3D(),AllplanGeo.Point3D(0,0,1)), AllplanGeo.Angle.FromDeg(0)] ):
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
        self.Gruix = Gruix
        self.nEncaixos = nEncaixos
        self.angle = angle

        self.invertirpared = invertirPared


        self.matrixPosXAux =[]
        self.matrixPosYAux =[]

        self.FemellesAux = []
        self.EncaixosPar = []



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
        param_list.append ("nEncaixos = %s\n" % self.nEncaixos)
        return param_list

    def __repr__(self):
        #return 'TD_Horitzontal(zUnique=%s, DistanciaEntreTD=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s, invertirPeca=%s,' \
        return 'TD_Horitzontal(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, nEncaixos=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.nEncaixos)
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
        if self.BarraAmple <= 0 or self.BarraAltura <= 0 or self.BarraLlargada <= 0:
            return False

        return True

    def get_ref_enc_llargada(self):
        return 0


    def get_seccio(self):

        if self.BarraAmple > self.BarraAltura:
            return str(self.BarraAmple) + "x " + str(self.BarraAltura) + "x " + str(self.nEncaixos)

        return str(self.BarraAltura) + "x " + str(self.BarraAmple) + "x " + str(self.nEncaixos)

    def get_llargada(self):

        return str(self.BarraLlargada)



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


    def get_common_props(self):
        common_prop = self.get_foundation_common_props()
        return common_prop



    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''

        #codis:
        ref_enc_llargada = 0.00

        elements = []
        elements = ModelEleList()
        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()
        ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        barra = ele1

        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]

        elements.append(AllplanBasisElements.ModelElement3D(common_prop, barra))




        return elements
        #return barra


    def create_angular(self, n, pos):

        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada/self.nEncaixos, self.BarraAmple, self.BarraAltura )
        #return geometry2

        geometry1 = AllplanGeo.Move(geometry1, pos)

        desply =  0+self.Gruix#self.Gruix
        if self.invertirpared:
            desply = -self.BarraAmple -self.Gruix

        pos = AllplanGeo.Vector3D(pos.X,desply,self.Gruix)
        #llargadaEncaix = (self.BarraLlargada- (self.Gruix*self.nEncaixos + self.Gruix))/self.nEncaixos
        llargadaEncaix = (self.BarraLlargada)/self.nEncaixos

        geometryEncaixos = AllplanGeo.Polyhedron3D.CreateCuboid( llargadaEncaix, self.BarraAmple, self.BarraAltura-self.Gruix )
        geometryEncaixos = AllplanGeo.Move(geometryEncaixos, pos)

        geometry1 = AllplanGeo.MakeBoolean(geometry1, geometryEncaixos)
        #geometry1 = geometry1[3]

        return geometry1[3]



    #BARRA

    def create_barra(self):
        '''
        Es crea dos cuboids, un amb l'ample, altura i llargada indicada, i el segon igual menys el gruix indicat,
        es fauna operació bool i es retorna el model coincident.

        return: Polyhedron3D
        '''

        desply1 = 0#self.Gruix
        if self.invertirpared:
            desply1 = -self.BarraAmple

        pos1 = AllplanGeo.Vector3D(0,desply1,0)
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada/self.nEncaixos, self.BarraAmple, self.BarraAltura )
        #return geometry2
        geometry1 = AllplanGeo.Move(geometry1, pos1)


        desply2 =  0+self.Gruix#self.Gruix
        if self.invertirpared:
            desply2 = -self.BarraAmple -self.Gruix

        pos2 = AllplanGeo.Vector3D(0,desply2,self.Gruix)
        #llargadaEncaix = (self.BarraLlargada- (self.Gruix*self.nEncaixos + self.Gruix))/self.nEncaixos
        llargadaEncaix = (self.BarraLlargada)/self.nEncaixos

        geometryEncaixos = AllplanGeo.Polyhedron3D.CreateCuboid( llargadaEncaix, self.BarraAmple, self.BarraAltura-self.Gruix )
        geometryEncaixos = AllplanGeo.Move(geometryEncaixos, pos2)

        pos3 = AllplanGeo.Vector3D(pos1.X + llargadaEncaix ,desply2,0)
        geometry1 = AllplanGeo.MakeBoolean(geometry1, geometryEncaixos)
        geometry1 = geometry1[3]


        pos = AllplanGeo.Vector3D(pos1.X + llargadaEncaix + self.Gruix ,desply1,pos1.Z)
        llargadaEncaix = (self.BarraLlargada)/self.nEncaixos
        for n in range(1,self.nEncaixos):
            geometryEncaixos = self.create_angular(n, pos)
            pos = AllplanGeo.Vector3D(pos.X + llargadaEncaix + self.Gruix ,desply1,0)
            #pos2 = AllplanGeo.Vector3D(pos2.X + llargadaEncaix + self.Gruix ,desply,0)
            geometry2 = AllplanGeo.MakeBoolean(geometry1, geometryEncaixos)
            geometry1 = geometry2[2]

        '''
        pos = AllplanGeo.Vector3D(self.Gruix,desply,0)
        llargadaEncaix = (self.BarraLlargada- (self.Gruix*self.nEncaixos + self.Gruix))/self.nEncaixos
        for n in range(1,self.nEncaixos):
            geometryEncaixos = AllplanGeo.Polyhedron3D.CreateCuboid( llargadaEncaix, self.BarraAmple- self.Gruix, self.BarraAltura-self.Gruix )
            geometryEncaixos = AllplanGeo.Move(geometryEncaixos, pos)

            pos = AllplanGeo.Vector3D(pos.X + llargadaEncaix + self.Gruix ,desply,0)
            geometry2 = AllplanGeo.MakeBoolean(geometry1, geometryEncaixos)
            geometry1 = geometry2[2]

        '''
        #AllplanGeo.Rotate( AllplanGeo.Point3D(),self.angle[1] )
        axis_point = AllplanGeo.Axis3D(self.angle[0][0], AllplanGeo.Vector3D(self.angle[0][0], self.angle[0][1]))
        #axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(), AllplanGeo.Vector3D(0,1,0))
        geometry1 = AllplanGeo.Rotate(geometry1,axis_point, self.angle[1])

        return  geometry1




        desply = 0#self.Gruix
        if self.invertirpared:
            desply = -self.BarraAmple

        pos = AllplanGeo.Vector3D(0,desply,0)
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura )

        geometryInclinat = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura )
        axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(), AllplanGeo.Vector3D(1,0,0))
        geometry2 = AllplanGeo.Rotate(geometryInclinat,axis_point,  AllplanGeo.Angle.FromDeg(45))
        geometry2 = AllplanGeo.MakeBoolean(geometry1, geometryInclinat)
        geometry2 = geometry2[2]
        #return geometry2

        geometry1 = AllplanGeo.Move(geometry1, pos)

        desply = self.Gruix
        if self.invertirpared:
            desply = -self.BarraAmple
        #crear cuboid interior
        #geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid(self.BarraLlargada,
        #                                                    self.BarraAmple-1.5,
        #                                                    self.BarraAltura-1.5)
        #geometry = AllplanGeo.MakeBoolean(geometry1, geometry2)
        #geometry1 = geometry[3]
        pos = AllplanGeo.Vector3D(self.Gruix,desply,0)
        llargadaEncaix = (self.BarraLlargada- (self.Gruix*self.nEncaixos + self.Gruix))/self.nEncaixos
        for n in range(0,self.nEncaixos):
            geometryEncaixos = AllplanGeo.Polyhedron3D.CreateCuboid( llargadaEncaix, self.BarraAmple- self.Gruix, self.BarraAltura-self.Gruix )
            geometryEncaixos = AllplanGeo.Move(geometryEncaixos, pos)

            pos = AllplanGeo.Vector3D(pos.X + llargadaEncaix + self.Gruix ,desply,0)
            geometry2 = AllplanGeo.MakeBoolean(geometry1, geometryEncaixos)
            geometry1 = geometry2[3]


        #AllplanGeo.Rotate( AllplanGeo.Point3D(),self.angle[1] )
        axis_point = AllplanGeo.Axis3D(self.angle[0][0], AllplanGeo.Vector3D(self.angle[0][0], self.angle[0][1]))
        #axis_point = AllplanGeo.Axis3D(AllplanGeo.Point3D(), AllplanGeo.Vector3D(0,1,0))
        geometry1 = AllplanGeo.Rotate(geometry1,axis_point, self.angle[1])

        return  geometry1


    #PROPS lAYERS / CAPES
    def get_foundation_common_props(self): #-> AllplanBaseElements.CommonProperties:

        common_prop = AllplanBaseElements.CommonProperties()
        '''
        common_prop.Color   = build_ele.FounColor.value
        common_prop.Pen     = build_ele.FounPen.value
        common_prop.Stroke  = build_ele.FounStroke.value
        '''
        #common_prop.Color   = self.FounColor
        #common_prop.Layer   = self.BarraLayer
        #if self.IsUseGlobalProp:
        #    common_prop.GetGlobalProperties()
        common_prop.GetGlobalProperties()

        return common_prop

    def getAmplada(self):
        return self.amplada_femella

    def definir_amplada(self, amplada):
        self.amplada_femella = amplada


