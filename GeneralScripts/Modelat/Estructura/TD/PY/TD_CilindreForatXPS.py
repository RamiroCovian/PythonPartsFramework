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

print('Load TD_CilindreForatXPS.py')


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


    TDCilindreForatXPS = CilindreForatXPS(build_ele.zUnique.value ,build_ele.Ample.value, build_ele.BarraAltura.value, build_ele.BarraGruix.value,
                                      build_ele.FounColor.value, build_ele.BarraLayer.value)

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not TDCilindreForatXPS.is_valid():
        return ([], [])

    handle_list = TDCilindreForatXPS.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDCilindreForatXPS.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2103, "TH TDCilindreForatXPS ")]

    '''
    pythonpart = PythonPart ("TD_CilindreForatXPS",
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


class CilindreForatXPS():
    """
    Definition of class Table
    """

    def __init__(self, zUnique, Ample, BarraAltura, BarraGruix,
                 FounColor, BarraLayer,
                 retIndividual = False,
                 retPrimer = False, retSegon = False):
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

        self.FounColor = FounColor
        self.BarraLayer = BarraLayer

        self.retIndividual = retIndividual
        self.retPrimer = retPrimer
        self.retSegon = retSegon

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraAmple",
                                        AllplanGeo.Point3D(0, self.Ample, self.BarraAltura),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraAmple", HandleDirection.y_dir),
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
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)

        return param_list

    def __repr__(self):

        return 'TD_CilindreForatXPS(zUnique=%s, Ample=%s , BarraAltura =%s, BarraGruix=%s'\
            'FounColor=%s, BarraLayer=%s)\n '\
            % (self.zUnique, self.Ample, self.BarraAltura, self.BarraGruix,
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
        return "TD_CilindreForatXPS.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.Ample<= 0 :
            return False

        return True

    def getTDType(self) :
        return "CilindreForatXPS"

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
        #barra = AllplanGeo.Polyhedron3D.CreateCuboid(0,0,0)

        ele1 = self.create_cilinder_cancam()


        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]

        elements.append(AllplanBasisElements.ModelElement3D(common_prop, ele1))


        return ele1

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



    #CilindreCancam1
    def create_cilinder_cancam(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(10 , 8, 0 ) ),
            radiusMajor=    10,
            radiusMinor=    10,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        error_code, polyhedronint = AllplanGeo.CreatePolyhedron(cylinderint, 12)

        if error_code == AllplanGeo.eOK:
            return cylinderint
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )





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

