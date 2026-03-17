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
import Utils as Utils


from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart
from PythonPartUtil import PythonPartUtil
from BuildingElementAttributeList import BuildingElementAttributeList
import Utils.Text3DUtil

print('Load EN_CreateText.py')

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

    ENTextSpline = TextSpline(build_ele.zUnique.value, build_ele.BarraAmple.value, build_ele.BarraAltura.value, build_ele.BarraLlargada.value, build_ele.BarraGruix.value,
                                build_ele.IsUseGlobalProp.value, build_ele.FounColor.value, build_ele.BarraLayer.value, build_ele.Text3D.value) #matriu

    build_ele.BarraAltura.value = build_ele.BarraAmple.value
    if not ENTextSpline.is_valid():
        return ([], [])




    handle_list = ENTextSpline.create_handles()
    views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, ENTextSpline.create())])]

    attr_list = [AllplanBaseElements.AttributeString(2445, ENTextSpline.get_seccio()),
                AllplanBaseElements.AttributeString(220, ENTextSpline.get_llargada()),
                AllplanBaseElements.AttributeString(2103, "TEXT"),
                AllplanBaseElements.AttributeString(508, "TEXT SPLINE")]


    pythonpart = PythonPart ("TextSpline",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = views,
                             matrix = AllplanGeo.Matrix3D(),
                             attribute_list = attr_list)


    model_elem_list = pythonpart.create()

    '''
    text_3d = Utils.Text3DUtil.Text3DUtil()

    if text_3d is None:
        return

    bsplines = text_3d.get_bsplines(AllplanGeo.Point3D(), str(build_ele.Text3D.value), AllplanGeo.Point3D(0,100,0), 50, AllplanGeo.Angle())


    #model_elem_list.append(AllplanBasisElements.ModelElement3D(bsplines))

    for i in range(len(bsplines)):
        text_3d = AllplanBasisElements.ModelElement3D(common_props, bsplines[i])
        model_elem_list.append(text_3d)


    #model_elem_list.append(AllplanBasisElements.ModelElement3D(common_props, bsplines))
    '''


    return (model_elem_list, handle_list)


class TextSpline():
    """ implementation of the EN BAR 1
    """

    def __init__(self, zUnique = random.random() * 3600, BarraAmple = 30, BarraAltura = 30, BarraLlargada = 260, BarraGruix = 1.5,
                    IsUseGlobalProp = False, FounColor = 1, BarraLayer = 2, textEntrada = "", tamanyNumId = 5):
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
        self.TextEntrada = textEntrada
        self.TamanyNumId = tamanyNumId


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
        param_list.append ("TextEntrada = %s\n" % self.TextEntrada)
        param_list.append ("TamanyNumId = %s\n" % self.TamanyNumId)

        return param_list

    def __repr__(self):
        return 'EN_CreateText(zUnique=%s, BarraAmple=%s, BarraAltura=%s, BarraLlargada=%s, BarraGruix=%s,' \
            'IsUseGlobalProp=%s, FounColor=%s, BarraLayer=%s, TextEntrada=%s, TamanyNumId=%s)\n' \
            % (self.zUnique, self.BarraAmple, self.BarraAltura, self.BarraLlargada, self.BarraGruix,
               self.IsUseGlobalProp, self.FounColor, self.BarraLayer, self.TextEntrada, self.TamanyNumId)

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
        return "EN_CreateText.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.BarraAmple <= 0 or self.BarraAltura <= 0 or self.BarraLlargada <= 0 or self.BarraGruix <= 0:
            return False

        return True

    def get_ref_enc_llargada(self):
        return 0

    def get_seccio(self):

        if self.BarraAmple > self.BarraAltura:
            return str(self.BarraAmple) + "x " + str(self.BarraAltura) + "x " + str(self.BarraGruix)

        return str(self.BarraAltura) + "x " + str(self.BarraAmple) + "x " + str(self.BarraGruix)

    def get_llargada(self):

        return str(self.BarraLlargada)


    def volume(self):
        """
        Calculate the volume in m³

        Returns:
            Calculated volume
        """
        return 10
        err, volume, _, _ = AllplanGeo.CalcMass(self.m_EN_Vertical)
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
        return "EN_CreateText"

    def get_common_props(self):

        common_prop = self.get_foundation_common_props()
        return common_prop




#-------------------CREAR BARRA --------------+
    def create(self):
        '''
        Es crean els elements entrats per l'usuari i s'afegeixen al array que els mostra per pantalla
        '''
        #print("Create model EN 1")
        #


        elements = []
        #ele1 = self.create_barra()
        #self.add_atribute_codi_mesures(build_ele, _doc)

        #barra = ele1
        barra = AllplanGeo.Polyhedron3D.CreateCuboid(0.1,0.1,0.1)


        barres = []


        #common props / Layers
        common_prop = self.get_foundation_common_props()

        #barra = AllplanGeo.MakeBoolean(barra, ind_inf)
        #barra = barra[2]
        #barra = self.create_L()

        text_3d = Utils.Text3DUtil.Text3DUtil()

        if text_3d is None:
            return

        polygon = AllplanGeo.Polygon3D()

        bsplines = text_3d.get_bsplines(AllplanGeo.Point3D(), str(self.TextEntrada), AllplanGeo.Point3D(0,100,0), 20*self.TamanyNumId*2, AllplanGeo.Angle())

        if len(bsplines)>0:
           # barra = AllplanGeo.BSpline3D.CreateBSpline(bsplines[0], 0, True)
            barra = AllplanGeo.Line3D(bsplines[0].RefPoint, bsplines[0].StartPoint, bsplines[0].EndPoint)


            #model_elem_list.append(AllplanBasisElements.ModelElement3D(bsplines))

            for i in range(1, len(bsplines)):

                for j in range(len(bsplines[i].Points)):
                    polygon += AllplanGeo.Point3D(bsplines[i].Points[j].X,bsplines[i].Points[j].Y,bsplines[i].Points[j].Z)

                polygon += bsplines[i].Points[0]


        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(AllplanGeo.Vector3D(0,-1,10))
        extruded_solid.SetRefPoint(polygon.Points[0])
        extruded_solid.SetExtrudedArea(area)

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)

        polyhedron = AllplanGeo.Rotate(polyhedron, AllplanGeo.Axis3D(AllplanGeo.Point3D(), AllplanGeo.Vector3D(1,0,0)) ,AllplanGeo.Angle.FromDeg(90))

        return polyhedron

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

    def create_L(self):

        llargada = 30
        altura = 5
        amplada = self.BarraAltura

        #creació cuboid inferior esquerra
        #geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura)
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( llargada, amplada, altura)
        #crear cuboid interior
        #geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAltura, self.BarraAmple, self.BarraLlargada)
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura, amplada, llargada)

        vector = AllplanGeo.Vector3D(llargada-altura, 0, 0)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometryIE = AllplanGeo.MakeBoolean(geometry1, geometry2)

        #creació cuboid inferior dreta
        #geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura)
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( llargada, amplada, altura)
        #crear cuboid interior
        #geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAltura, self.BarraAmple, self.BarraLlargada)
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura, amplada, llargada)

        vector = AllplanGeo.Vector3D(0, 0, 0)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometryID = AllplanGeo.MakeBoolean(geometry1, geometry2)
        vector = AllplanGeo.Vector3D(self.BarraAmple + llargada, 0, 0)
        geometryID = AllplanGeo.Move(geometryID[2], vector)

        #es crea el vector per posicionarlo al centre i es resten els volums
        geometryI = AllplanGeo.MakeBoolean(geometryIE[2], geometryID)


        #creació cuboid Superior esquerra
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( llargada, amplada, altura)
        vector = AllplanGeo.Vector3D(0, 0, llargada-altura)
        geometry1 = AllplanGeo.Move(geometry1, vector)

        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura, amplada, llargada)


        vector = AllplanGeo.Vector3D(llargada-altura, 0, 0)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometrySE = AllplanGeo.MakeBoolean(geometry1, geometry2)

        #creació cuboid superior dreta
        #geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraLlargada, self.BarraAmple, self.BarraAltura)
        geometry1 = AllplanGeo.Polyhedron3D.CreateCuboid( llargada, amplada, altura)
        vector = AllplanGeo.Vector3D(0, 0, llargada-altura)
        geometry1 = AllplanGeo.Move(geometry1, vector)
        #crear cuboid interior
        #geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( self.BarraAltura, self.BarraAmple, self.BarraLlargada)
        geometry2 = AllplanGeo.Polyhedron3D.CreateCuboid( altura, amplada, llargada)

        vector = AllplanGeo.Vector3D(0, 0, 0)
        geometry2 = AllplanGeo.Move(geometry2, vector)
        geometrySD = AllplanGeo.MakeBoolean(geometry1, geometry2)
        vector = AllplanGeo.Vector3D(self.BarraAmple + llargada, 0, 0)
        geometrySD = AllplanGeo.Move(geometrySD[2], vector)

        #es crea el vector per posicionarlo al centre i es resten els volums
        geometryS = AllplanGeo.MakeBoolean(geometrySE[2], geometrySD)
        vector = AllplanGeo.Vector3D(0, 0, self.BarraLlargada)
        geometryS = AllplanGeo.Move(geometryS[2], vector)

        geometry = AllplanGeo.MakeBoolean(geometryS, geometryI[2])


        return  geometry[2]


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
