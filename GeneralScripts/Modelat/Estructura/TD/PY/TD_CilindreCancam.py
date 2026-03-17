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

print('Load TD_CilindreCancam.py')


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


    TDCilindreCancam = CilindreCancam(build_ele.zUnique.value ,build_ele.Ample.value, build_ele.BarraAltura.value, build_ele.BarraGruix.value,
                                      build_ele.IsFirstCancam.value, build_ele.Dis1cancam.value,
                                      build_ele.IsSecondCancam.value, build_ele.Dis2cancam.value,
                                      build_ele.FounColor.value, build_ele.BarraLayer.value)

    #build_ele.BarraAltura.value = build_ele.BarraAmple.value

    if not TDCilindreCancam.is_valid():
        return ([], [])

    handle_list = TDCilindreCancam.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, TDCilindreCancam.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2103, "TH TDCilindreCancam ")]

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


class CilindreCancam():
    """
    Definition of class Table
    """

    def __init__(self, zUnique, Ample, BarraAltura, BarraGruix,
                 IsFirstCancam, Dis1cancam,
                 IsSecondCancam, Dis2cancam,
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

        self.IsFirstCancam = IsFirstCancam
        self.Dis1cancam = Dis1cancam
        self.IsSecondCancam = IsSecondCancam
        self.Dis2cancam = Dis2cancam
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
        param_list.append ("IsFirstCancam = %s\n" % self.IsFirstCancam)
        param_list.append ("Dis1cancam = %s\n" % self.Dis1cancam)
        param_list.append ("IsSecondCancam = %s\n" % self.IsSecondCancam)
        param_list.append ("Dis2cancam = %s\n" % self.Dis2cancam)
        param_list.append ("FounColor = %s\n" % self.FounColor)
        param_list.append ("BarraLayer = %s\n" % self.BarraLayer)

        return param_list

    def __repr__(self):

        return 'TD_CilindreCancam(zUnique=%s, Ample=%s , BarraAltura =%s, BarraGruix=%s'\
            'IsFirstCancam=%s , Dis1cancam=%s'\
            'IsSecondCancam=%s, Dis2cancam=%s'\
            'FounColor=%s, BarraLayer=%s)\n '\
            % (self.zUnique, self.Ample, self.BarraAltura, self.BarraGruix,
               self.IsFirstCancam,self.Dis1cancam,
               self.IsSecondCancam, self.Dis2cancam,
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
        return "TD_CilindreCancam.py"

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

        '''
        #Cancams
        if self.IsFirstCancam or self.IsSecondCancam:
            ele2 = self.create_cancams()
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[3]
            #polyhedron
            eleint1 = self.create_cilinderinterior_cancam1()
            eleint2 = self.create_cilinderinterior_cancam2()

            barra = AllplanGeo.MakeBoolean(barra, eleint1)
            barra = barra[3]
            barra = AllplanGeo.MakeBoolean(barra, eleint2)
            barra = barra[3]
        '''
        if self.IsFirstCancam:
            ele1 = self.create_cilinder_cancam1()
            ele2 = self.create_cilinder_cancam2()

            barra = AllplanGeo.MakeBoolean(barra, ele1)
            barra = barra[2]
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[2]

            if self.retIndividual:
                if self.retPrimer:
                    return ele1
                elif self.retSegon:
                    return ele2
                else:
                    print("Dades incorrectes a CilindreCanca")


        if self.IsSecondCancam:
            ele1 = self.create_cilinder_cancam11()
            ele2 = self.create_cilinder_cancam22()
            barra = AllplanGeo.MakeBoolean(barra, ele1)
            barra = barra[2]
            barra = AllplanGeo.MakeBoolean(barra, ele2)
            barra = barra[2]

            if self.retIndividual:
                if self.retPrimer:
                    return ele1
                elif self.retSegon:
                    return ele2
                else:
                    print("Dades incorrectes a CilindreCanca")

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



    #Cancam1
    def create_cilinder_cancam1(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    12,
            radiusMinor=    12,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra1 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra1 = barra1[3]


            '''
            profile_points =   [
                                AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis1cancam/2 +0.1, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis1cancam/2 +0.1, self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis1cancam/2 , self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                            AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura+20),
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
            '''

        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra1

    #Cancam1
    def create_cilinder_cancam11(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    12,
            radiusMinor=    12,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra1 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra1 = barra1[3]

            '''
            profile_points =   [
                                AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis2cancam/2 +0.1, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis2cancam/2 +0.1, self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis2cancam/2 , self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                            AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura+20),
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
            '''

        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra1

    #Cancam2
    def create_cilinder_cancam2(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    12,
            radiusMinor=    12,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra2 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra2 = barra2[3]

            '''
            profile_points =   [
                                AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis1cancam/2 +0.1, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis1cancam/2 +0.1, self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis1cancam/2 , self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura),
                            AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura+20),
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
            '''
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra2

    #Cancam2
    def create_cilinder_cancam22(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura ) ),
            radiusMajor=    12.5,
            radiusMinor=    12.5,
            apex=           AllplanGeo.Point3D(0, 0, 20)
        )

        #if the cylinder should be created as a polyhedron, the tessellation must be performed

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(cylinder, 8)

        if error_code == AllplanGeo.eOK:
            barra2 = AllplanGeo.MakeBoolean(polyhedron, polyhedronint)
            barra2 = barra2[3]

            '''
            profile_points =   [
                                AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis2cancam/2 +0.1, self.Ample/2, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis2cancam/2 +0.1, self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis2cancam/2 , self.Ample/2 +0.1, self.BarraAltura),
                                AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                                ]

            profile = AllplanGeo.Polyline3D(profile_points)

            profiles = AllplanGeo.Polyline3DList()
            profiles.append(profile)

            path_points =  [AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura),
                            AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura+20),
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
            '''
        else:
            print("Tessellation failed")
            return  AllplanGeo.Polyhedron3D.CreateCuboid( 2, 2 , 2 )

        return barra2

    #Cancam interior 1
    def create_cilinderinterior_cancam1(self):
        #polyhedron
        #----- create cylinder interior
        cylinderint = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis1cancam/2, self.Ample/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - self.Dis2cancam/2, self.Ample/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis1cancam/2, self.Ample/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
            refPlacement=   AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 + self.Dis2cancam/2, self.Ample/2, self.BarraAltura - self.BarraGruix  ) ),
            radiusMajor=    6.5,
            radiusMinor=    6.5,
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
        cancam_1 = AllplanGeo.Polyhedron3D.CreateCuboid( 20, 20 ,self.BarraGruix)

        #cancam1
        #vector = AllplanGeo.Vector3D( self.posicio_centre_masses - self.Dis1cancam/2, self.BarraGruix, self.BarraAltura - self.BarraGruix*2 )
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses - self.Dis1cancam/2 -10, self.BarraAmple/2 - 10, self.BarraAltura - self.BarraGruix )
        cancam_12 = AllplanGeo.Move(cancam_1, vector)
        #vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis1cancam/2, self.BarraGruix, (self.BarraAltura/2)-(self.BarraGruix*2) )
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis1cancam/2 -10, self.BarraAmple/2 - 10, self.BarraAltura-self.BarraGruix )
        cancam_11 = AllplanGeo.Move(cancam_1, vector)

        #cancam2
        vector = AllplanGeo.Vector3D(self.posicio_centre_masses - self.Dis2cancam/2 -10, self.BarraAmple/2 - 10, self.BarraAltura - self.BarraGruix )
        cancam_22 = AllplanGeo.Move(cancam_1, vector)
        vector = AllplanGeo.Vector3D( self.posicio_centre_masses + self.Dis2cancam/2 -10,self.BarraAmple/2 - 10, self.BarraAltura - self.BarraGruix )
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
    '''


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

