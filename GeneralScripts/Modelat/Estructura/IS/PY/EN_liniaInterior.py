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

print('Load EN_LiniaInterior.py')


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

    EN_LiniaInterior = LiniaInterior(build_ele.zUnique.value, build_ele.BarraLlargada.value, build_ele.isHor.value) #matriu

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not EN_LiniaInterior.is_valid():
        return ([], [])


    handle_list = EN_LiniaInterior.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, EN_LiniaInterior.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2103, "Linia Interior "),
                        AllplanBaseElements.AttributeString(508, "Linia Interior")]

    pythonpart = PythonPart ("EN_liniaInterior",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class LiniaInterior():
    """
    Definition of class Table
    """

    def __init__(self, zUnique, BarraLlargada, isHor):
        """ initialize

        Args:
            coord_input:       API object for the coordinate input, element selection, ... in the Allplan view
            palette_service:   palette service
            build_ele_list:    list with the building elements
            modification_mode: modification mode state
            modify_uuid_list:  UUIDs of the existing elements in the modification mode
        """
        self.zUnique = zUnique
        self.BarraLlargada = BarraLlargada
        self.isHor = isHor



    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("zUnique = %s\n" % self.zUnique)
        param_list.append ("BarraLlargada = %s\n" % self.BarraLlargada)
        param_list.append ("isHor = %s\n" % self.isHor)

        return param_list

    def __repr__(self):
        return 'EN_liniaInterior(zUnique=%s, BarraLlargada=%s, isHor=%s)\n' \
            % (self.zUnique, self.BarraLlargada, self.isHor )

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
        return "EN_liniaInterior.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.BarraLlargada <= 0:
            return False

        return True


    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle
        #build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,

        handle_list = [HandleProperties("BarraLlargada",
                                        AllplanGeo.Point3D(self.BarraLlargada, 0, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("BarraLlargada", HandleDirection.x_dir)],
                                        HandleDirection.x_dir)
                      ]

        return handle_list

    def getTDType(self) :
        return "Linia Interior"

    def get_common_props(self):
        common_prop = self.get_foundation_common_props()
        return common_prop


    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''

        elements = []

        ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        barra = ele1

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


    #BARRA
    def create_barra(self):
        '''
        Es crea dos cuboids, un amb l'ample, altura i llargada indicada, i el segon igual menys el gruix indicat,
        es fauna operació bool i es retorna el model coincident.

        return: Polyhedron3D
        '''

        if self.isHor:
            refPoint = AllplanGeo.Point3D(0,0,0)
            startPoint = AllplanGeo.Point3D(0,0,0)
            endPoint = AllplanGeo.Point3D(self.BarraLlargada, 0,0)
            geometry = AllplanGeo.Line3D(refPoint, startPoint, endPoint)
        else:
            refPoint = AllplanGeo.Point3D(0,0,0)
            startPoint = AllplanGeo.Point3D(0,0,0)
            endPoint = AllplanGeo.Point3D(0, 0,self.BarraLlargada)
            geometry = AllplanGeo.Line3D(refPoint, startPoint, endPoint)


        return  geometry


    #PROPS lAYERS / CAPES
    def get_foundation_common_props(self): #-> AllplanBaseElements.CommonProperties:

        common_prop = AllplanBaseElements.CommonProperties()
        '''
        common_prop.Color   = build_ele.FounColor.value
        common_prop.Pen     = build_ele.FounPen.value
        common_prop.Stroke  = build_ele.FounStroke.value
        '''

        common_prop.GetGlobalProperties()

        return common_prop

    def getAmplada(self):
        return self.amplada_femella

    def definir_amplada(self, amplada):
        self.amplada_femella = amplada

