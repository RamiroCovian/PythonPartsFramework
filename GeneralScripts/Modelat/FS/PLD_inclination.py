"""Module providing paythonpart FS."""

import random

import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
from HandleProperties import HandleProperties
from HandleDirection import HandleDirection
from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
import NemAll_Python_BaseElements as AllplanBaseElements
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList
import NemAll_Python_AllplanSettings as AllplanSettings
from DocumentManager import DocumentManager

print('Load PLD inclination.py')

def check_allplan_version(build_ele, version):
    """ Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """
    del build_ele
    del version
    return True

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """Move handle function

    Args:
        build_ele (_type_): _description_
        handle_prop (_type_): _description_
        input_pnt (_type_): _description_
        doc (_type_): _description_

    Returns:
        _type_: _description_
    """
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def on_control_event(build_ele: BuildingElement, event_id: int):
    """Control event function

    Args:
        build_ele (BuildingElement): _description_
        event_id (int): _description_
    """
    # Events ID
    envent_id_create_figure = 1000

    doc = DocumentManager.get_instance().document
    if event_id == envent_id_create_figure:
        create_element(build_ele, doc)

def create_element(build_ele:   BuildingElement,
                   _doc:        AllplanEleAdapter.DocumentAdapter) -> CreateElementResult:
    """Creation of the cuboid

    Args:
        build_ele: building element with the parameter properties
        _doc:      document of the Allplan drawing files

    Returns:
        created element result
    """
    # Get values
    # PLD
    # Define name parameters
    z_unique = build_ele.zUnique.value
    ancho_pld = build_ele.AnchoPLD.value
    alto_pld = build_ele.LargoPLD.value
    z_rotation = build_ele.ZRotationInput.value
    type_pld = build_ele.TypePLD.value
    layer_value_name = build_ele.LayerValueName.value
    borde_afilado_selector = build_ele.SelectorBordeAfilado.value
    # grosor_pld = build_ele.EspesorPLD.value if hasattr(build_ele, self.name_parameter_grosor_pld) else self.default_grosor_pld
    # Define model element and add figures
    model_elements = ModelEleList()

    pld_element = PLD(_doc, z_unique, ancho_pld, alto_pld, z_rotation, type_pld, layer_value_name, borde_afilado_selector)

    # Create elements
    model_elements += pld_element.create()

    # Create handles after update values
    handle_list = pld_element.create_handles()

    return CreateElementResult(elements = model_elements, handles = handle_list)

class PLD():
    """PLD class
    """

    def __init__(self, doc: AllplanEleAdapter.DocumentAdapter, z_unique: int, ancho_pld, alto_pld, z_rotation: int, type_pld: str,
                 layer_value_name: int, borde_afilado_selector: int|None,  inclination_rotation_angle: int, inclination_selector_axis: int|None):
        """Initialize with default values

        Args:
            doc (AllplanEleAdapter.DocumentAdapter): _description_
            z_unique (int): _description_
            ancho_pld (_type_): _description_
            alto_pld (_type_): _description_
            z_rotation (int): _description_
            type_pld (str): _description_
            layer_value_name (int): _description_
            borde_afilado_selector (int | None): _description_
        """

        # PLD
        self.z_unique = 0
        self.alto_pld = 0
        self.ancho_pld = 0
        self.grosor_pld = 0

        # Default values
        self.default_z_unique = random.random() * 3600
        self.default_alto_pld = 3000 # borde largo - length (interpolables)
        self.defaul_ancho_pld = 1200 # borde corto - weidth (interpolables)
        self.default_grosor_pld = 15 # grosor o espesos - height
        self.default_desfasado_pld = 2
        # XPS
        self.alto_xps = 0
        self.ancho_xps = 0
        self.grosor_xps = 0

        # Default values
        self.default_alto_xps = 2996
        self.default_ancho_xps = 1196
        self.default_grosor_xps = 40

        # Rotation
        self.z_rotation = 0
        self.default_rotation = 0

        # Define name parameters
        # Rotation names
        self.name_parameter_z_rotation_input = 'ZRotationInput'
        self.name_parameter_z_rotation = 'ZRotation'
         # PLD keys
        self.name_parameter_zunique = 'zUnique'
        self.name_parameter_ancho_pld = 'AnchoPLD'
        self.name_parameter_alto_pld = 'LargoPLD'
        self.name_parameter_grosor_pld = 'EspesorPLD'
        self.name_parameter_type_pld = 'TypePLD'
        # XPS keys
        self.name_parameter_grosor_xps = 'EspesorXPS'

        # Define handle points
        # pld
        self.handle_point_cuboid_pld_rotated_ancho =  AllplanGeo.Point3D(0, 0, 0)
        self.handle_ref_point_cuboid_pld_rotated_ancho =  AllplanGeo.Point3D(0, 0, 0)
        self.handle_ref_point_cuboid_pld_rotated_ancho_index = 0
        self.handle_point_cuboid_pld_rotated_ancho_index = 1
        self.handle_point_cuboid_pld_rotated_alto =  AllplanGeo.Point3D(0, 0, 0)
        self.handle_ref_point_cuboid_pld_rotated_alto =  AllplanGeo.Point3D(0, 0, 0)
        self.handle_ref_point_cuboid_pld_rotated_alto_index = 0
        self.handle_point_cuboid_pld_rotated_alto_index = 3

        # xps
        self.handle_point_cuboid_xps_rotated =  AllplanGeo.Point3D(0, 0, 0)

        # Define colors
        # PLD
        self.default_color_pld = 1
        self.color_pld = self.default_color_pld

        # Prisma triangular extrude
        self.lado_x_triangle = 25
        self.lado_y_triangle = 5

        # Borde afilado options
        # Name parameter
        self.name_parameter_borde_afilado_selector = "SelectorBordeAfilado"
        self.borde_afilado_left = 1
        self.borde_afilado_right = 2

        # Layer name
        self.layer_name_pld = ""
        self.layer_name_xps = ""

        # Set PLD values
        self._doc = doc
        self.z_rotation = z_rotation
        self.z_unique = z_unique
        self.ancho_pld = ancho_pld
        self.alto_pld = alto_pld
        self.grosor_pld = self.default_grosor_pld
        self.type_pld = type_pld
        self.layer_name_pld = f"FS_PLD-{layer_value_name}"
        self.borde_afilado_selector = borde_afilado_selector

        # Set inclination values
        self.inclination_rotation_angle = inclination_rotation_angle
        self.inclination_selector_axis = inclination_selector_axis

    def is_valid(self) -> bool:
        """Function to check if is valid create cuboids

        Returns:
            bool: _description_
        """
        # Validate with size constraints
        allowed_xps_thicknesses = [40, 50, 70, 80, 100, 120]
        max_value_rotation = 360
        min_value_rotation = -360

        is_valid = all([
            self.ancho_pld >= 900 and self.ancho_pld <= 1200,  # PLD width between 900-1200mm
            self.alto_pld >= 900 and self.alto_pld <= 3000,  # Length between 900-3000mm
            self.grosor_pld == 15,  # PLD thickness must be exactly 15mm
            self.grosor_xps in allowed_xps_thicknesses,  # XPS thickness must be one of allowed values
            min_value_rotation <= self.z_rotation <= max_value_rotation
        ])
        return is_valid

    def get_center_point(self):
        """Function to get center point

        Returns:
            _type_: _description_
        """
        # Create center point for rotation
        center_x = self.ancho_pld / 2
        center_y = self.alto_pld / 2
        center_z = (self.grosor_pld + self.grosor_xps) / 2
        center_point = AllplanGeo.Point3D(center_x, center_y, center_z)
        return center_point

    def get_color_pld(self):
        """Function to get PLD color

        Returns:
            _type_: _description_
        """
        # Constantes

        # PLD types
        pld_omnia_type = "OMNIA"
        pld_humitat_type = "HUMITAT"
        pld_foc_type = "FOC"

        # Define high values
        alto_pld_high_value = 3000
        alto_pld_low_value = 2500

        # Valores redondeados para comparación
        largo_pld_round = round(self.alto_pld)

        # Colors:
        # OMNIA
        color_omnia_high_value = 120
        color_omnia_default_value = 124
        # HUMITAT
        color_humitat_high_value = 1
        color_humitat_default_value = 65
        # FOC
        color_foc_high_value = 6
        color_foc_default_value = 107

        # OMNIA type
        if self.type_pld == pld_omnia_type:
            if alto_pld_low_value < largo_pld_round <= alto_pld_high_value:
                return color_omnia_high_value
            return color_omnia_default_value

         # HUMITAT type
        if self.type_pld == pld_humitat_type:
            if alto_pld_low_value < largo_pld_round <= alto_pld_high_value:
                return color_humitat_high_value
            return color_humitat_default_value

        # FOC type
        if self.type_pld == pld_foc_type:
            if alto_pld_low_value < largo_pld_round <= alto_pld_high_value:
                return color_foc_high_value
            return color_foc_default_value

        return self.default_color_pld

    def set_and_return_attributes_pld(self):
        """Set PLD attributes

        Returns:
            _type_: _description_
        """
        # Define constantes
        min_value_alto_pld = 2500

        # Define values: alto, ancho, grosor, type, color
        alto_value_attribute = 2500 if self.alto_pld <= min_value_alto_pld else 3000
        ancho_value_attribute = 1200
        grosor_value_attribute = 15
        type_value_attribute = self.type_pld
        # PLD types
        pld_omnia_type = "OMNIA"
        pld_humitat_type = "HUMITAT"

        if self.type_pld == pld_omnia_type:
            color_value_attribute = "VISTA CARA BLAVA"
        elif self.type_pld == pld_humitat_type:
            color_value_attribute = "VISTA CARA VERDA"
        else:
            color_value_attribute = "VISTA CARA VERMELLA"

        attribute_list = BuildingElementAttributeList()

        # Define attributes
        attribute_custom_01 = f"{alto_value_attribute}x{ancho_value_attribute}x{grosor_value_attribute};{type_value_attribute};{color_value_attribute}"
        attribute_custom_02 = f"{alto_value_attribute}x{ancho_value_attribute}x{grosor_value_attribute}"
        attribute_custom_05 = f"{alto_value_attribute}x{ancho_value_attribute}x{grosor_value_attribute}"

        attr_list = [
            AllplanBaseElements.AttributeString(1083, attribute_custom_01), # atrribute personalizado 01
            AllplanBaseElements.AttributeString(1084, attribute_custom_02), # atrribute personalizado 02
            AllplanBaseElements.AttributeString(1085, ""), # atrribute personalizado 03
            AllplanBaseElements.AttributeString(1086, ""), # atrribute personalizado 04
            AllplanBaseElements.AttributeString(1087, attribute_custom_05),  # atrribute personalizado 05
            AllplanBaseElements.AttributeString(1895, ""),  # atrribute personalizado 06
            AllplanBaseElements.AttributeString(1896, ""),  # atrribute personalizado 07
            AllplanBaseElements.AttributeString(1897, ""),  # atrribute personalizado 08
            AllplanBaseElements.AttributeString(1898, ""), # atrribute personalizado 09
            AllplanBaseElements.AttributeString(1899, ""), # atrribute personalizado 10
            AllplanBaseElements.AttributeString(1900, ""), # atrribute personalizado 11
            AllplanBaseElements.AttributeString(1901, ""), # atrribute personalizado 12
            AllplanBaseElements.AttributeString(1902, ""), # atrribute personalizado 13
            AllplanBaseElements.AttributeString(1903, ""), # atrribute personalizado 14
            AllplanBaseElements.AttributeString(1904, "")] # atrribute personalizado 15

        attribute_list.add_attribute_list(list(attr_list))

        return attribute_list

    # Create PLD y XPS
    # Create PLD
    def create_pld_cuboid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = self.ancho_pld,
            width     = self.alto_pld,
            height    = self.grosor_pld
        )

        return cuboid

    # Rotate PLD y XPS
    def rotate_cuboid(self, cuboid):
        """Function to rotate a given cuboid

        Args:
            cuboid (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Convert degrees to radians
        angle_rad = math.radians(self.z_rotation)

        # Create rotation matrix around Z axis
        rotation = AllplanGeo.Matrix3D()
        # Create an Angle object from the radians value
        angle = AllplanGeo.Angle(angle_rad)
        # Get center point
        center_point = self.get_center_point()
        rotation.Rotation(AllplanGeo.Line3D(center_point, AllplanGeo.Vector3D(0, 0, 1)), angle)
        return AllplanGeo.Transform(cuboid, rotation)

    def inclination_rotate_geo_object(self, geometry_object):
        """Function to rotate a given cuboid

        Args:
            geometry_object (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Convert degrees to radians
        angle_rad = math.radians(self.inclination_rotation_angle)
        # Create an Angle object from the radians value
        angle = AllplanGeo.Angle(angle_rad)

        if self.inclination_selector_axis == 1:
            rotation_axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0),
                                    AllplanGeo.Point3D(1, 0, 0))
        elif self.inclination_selector_axis == 1:
            rotation_axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0),
                                    AllplanGeo.Point3D(0, 1, 0))
        else:
            rotation_axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0),
                                    AllplanGeo.Point3D(0, 0, 1))

        # rotation_angle = AllplanGeo.Angle.FromDeg(15)
        transformation_matrix = AllplanGeo.Matrix3D()
        transformation_matrix.SetRotation(rotation_axis, angle)

        geometry_object *= transformation_matrix

        # Create rotation matrix around Z axis
        #rotation = AllplanGeo.Matrix3D()

        # Get center point
        #center_point = self.get_center_point()
        #rotation.Rotation(AllplanGeo.Line3D(center_point, AllplanGeo.Vector3D(0, 0, 1)), angle)
        #return AllplanGeo.Transform(cuboid, rotation)
        return geometry_object

    # Create prisma (Borde perfilado)
    def create_prisma(self):
        """Create triangular prisma

        Returns:
            _type_: _description_
        """
        # Define triangle
        lado_x_triangle = self.lado_x_triangle
        lado_y_triangle = self.lado_y_triangle
        altura_cuboid = self.alto_pld

        # Base triangular (en Z = 0)
        p1 = AllplanGeo.Point3D(0, 0, 0)
        p2 = AllplanGeo.Point3D(lado_x_triangle, 0, 0)
        p3 = AllplanGeo.Point3D(0, lado_y_triangle, 0)

        # create profile to extrude
        # Crear un Polygon3D con todas las caras del prisma
        polygon = AllplanGeo.Polygon3D()

        # Base inferior
        polygon += p1
        polygon += p2
        polygon += p3
        polygon += p1  # Cerrar base

        if not polygon.IsValid():
            print("Profile polygon is not valid")
            return CreateElementResult()

        err, profile_plane = polygon.GetPlane()
        profile_normal_vector = profile_plane.Vector if err is AllplanGeo.eOK else AllplanGeo.Vector3D(0,0,1)
        profile_normal_vector_end_direction = AllplanGeo.Vector3D(0,0,altura_cuboid)
        extrusion_direction =  AllplanGeo.Vector3D(0,0,altura_cuboid)

        rotation_matrix = AllplanGeo.Matrix3D()
        rotation_matrix.SetRotation(profile_normal_vector,
                                    profile_normal_vector_end_direction)

        area = AllplanGeo.PolygonalArea3D()
        area += polygon

        # create polyhedron by extruding the profile
        extruded_solid = AllplanGeo.ExtrudedAreaSolid3D()
        extruded_solid.SetDirection(extrusion_direction)
        extruded_solid.SetRefPoint(polygon.StartPoint)
        extruded_solid.SetExtrudedArea(area)

        error_code, polyhedron = AllplanGeo.CreatePolyhedron(extruded_solid)

        # create list of model elements, if extruding was successful
        if error_code is AllplanGeo.eOK:
            return polyhedron

        return None

    def rotate_prisma_x_axis(self, cuboid):
        """Rotate prisma

        Args:
            cuboid (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Rotate 90° axis X (1,0,0)
        rotation_axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0),
                                  AllplanGeo.Point3D(1, 0, 0))
        # Rotate 90°
        rotation_angle = AllplanGeo.Angle.FromDeg(90)
        transformation_matrix = AllplanGeo.Matrix3D()
        transformation_matrix.SetRotation(rotation_axis,rotation_angle)

        cuboid *= transformation_matrix
        return cuboid

    def rotate_prisma_z_axis(self, cuboid):
        """Rotate prisma

        Args:
            cuboid (_type_): _description_

        Returns:
            _type_: _description_
        """

        # Rotate 180° axis z (0,0,1)
        rotation_axis = AllplanGeo.Line3D(AllplanGeo.Point3D(0, 0, 0),
                                  AllplanGeo.Point3D(0, 0, 1))
        # Rotate 180°
        rotation_angle = AllplanGeo.Angle.FromDeg(180)
        transformation_matrix = AllplanGeo.Matrix3D()
        transformation_matrix.SetRotation(rotation_axis,rotation_angle)

        cuboid *= transformation_matrix
        return cuboid

    def move_prisma(self, cuboid, x_axis_initial=0, y_axis_initial=0, z_axis_initial=0):
        """Move prisma function

        Args:
            cuboid (_type_): _description_
            x_axis_initial (int, optional): _description_. Defaults to 0.
            y_axis_initial (int, optional): _description_. Defaults to 0.
            z_axis_initial (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        initial_x_axis = x_axis_initial
        initial_y_axis = self.alto_pld
        initial_z_elevetion = 0

        initial_x_axis = x_axis_initial
        initial_y_axis = y_axis_initial
        initial_z_elevetion = z_axis_initial

        # Position XPS plate above PLD with 2mm offset from each edge and elevetion in Z axis to avoid overlap
        return AllplanGeo.Move(cuboid, AllplanGeo.Vector3D(initial_x_axis, initial_y_axis, initial_z_elevetion))

    # Creates prismas left and right
    # Create prisma left
    def create_prisma_left(self):
        """Create prisma left

        Returns:
            _type_: Triangular prisma left
        """
        prisma_left = self.create_prisma()
        prisma_left = self.rotate_prisma_x_axis(prisma_left)
        # Change initial point
        # Redifine y axis
        initial_y_axis_prisma_left = self.alto_pld
        prisma_left = self.move_prisma(prisma_left, y_axis_initial=initial_y_axis_prisma_left)
        return prisma_left

    # Create prisma right
    def create_prisma_right(self):
        """Create prisma right

        Returns:
            _type_: Triangular prisma rigth
        """
        prisma_right = self.create_prisma()
        prisma_right = self.rotate_prisma_x_axis(prisma_right)
        prisma_right = self.rotate_prisma_z_axis(prisma_right)
        # Change initial point
        # Redifine y axis
        initial_x_axis_prisma_right = self.ancho_pld
        prisma_right = self.move_prisma(prisma_right, x_axis_initial=initial_x_axis_prisma_right)
        return prisma_right

    # Create PLD bordes afilados
    def create_pld_bordes_afilados(self):
        """Create PLD bordes afilados

        Returns:
            _type_: _description_
        """
        # Get value borde afilado selector
        borde_afilado_selector_value = self.borde_afilado_selector if self.borde_afilado_selector is not None else self.borde_afilado_left

        # Create PLD
        pld_cuboid = self.create_pld_cuboid()
         # Create triangular prismas
        # Prisma left
        prisma_left = self.create_prisma_left()
        # Prisma right
        prisma_right = self.create_prisma_right()
         # Add perfilado to PLD
        if prisma_left is None:
            print("Prisma left was not generated")

        if prisma_right is None:
            print("Prisma right was not generated")

        # Condition: if ancho PLD is less than ancho PLD default
        if self.ancho_pld < self.defaul_ancho_pld:
            # active borde afilado left
            if borde_afilado_selector_value == self.borde_afilado_left:
                # Make subtraction prisma left
                pld_perfilado = AllplanGeo.MakeSubtraction(pld_cuboid, prisma_left)
                # Get PLD pefilado
                pld_perfilado = pld_perfilado[1]
            else:
                # active borde afilado right
                 # Make subtraction prisma right
                pld_perfilado = AllplanGeo.MakeSubtraction(pld_cuboid, prisma_right)
                # Get PLD pefilado
                pld_perfilado = pld_perfilado[1]
        else:
            # When ancho PLD is equal to ancho PLD default -> both edges are activated
            # Make subtraction prisma left
            pld_perfilado = AllplanGeo.MakeSubtraction(pld_cuboid, prisma_left)
            # Get PLD pefilado
            pld_perfilado = pld_perfilado[1]

            # Make subtraction prisma right
            pld_perfilado = AllplanGeo.MakeSubtraction(pld_perfilado, prisma_right)
            # Get PLD pefilado
            pld_perfilado = pld_perfilado[1]

        return pld_cuboid, pld_perfilado

    # PLD
    def set_and_get_common_properties_pld(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        common_properties_pld = AllplanBaseElements.CommonProperties()
        # Set color PLD
        common_properties_pld.Color = self.color_pld
        # Set layer PLD
        layer_pld_id = AllplanBaseElements.LayerService.GetIDByShortName(self.layer_name_pld, self._doc)
        common_properties_pld.Layer = layer_pld_id
        return common_properties_pld

    # Handles
    def create_handles(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        handle_list = []

        handle_parameter_data_ancho_pld = HandleParameterData("AnchoPLD", HandleParameterType.POINT_DISTANCE)

        handle_ancho_pld = HandleProperties("ancho_pld",
                        self.handle_point_cuboid_pld_rotated_ancho,
                        self.handle_ref_point_cuboid_pld_rotated_ancho,
                        [handle_parameter_data_ancho_pld],
                        HandleDirection.POINT_DIR)

        handle_list.append(handle_ancho_pld)

        handle_parameter_data_alto_pld = HandleParameterData("LargoPLD", HandleParameterType.POINT_DISTANCE)

        handle_alto_pld =  HandleProperties("alto_pld",
                        self.handle_point_cuboid_pld_rotated_alto,
                        self.handle_ref_point_cuboid_pld_rotated_alto,
                        [handle_parameter_data_alto_pld],
                        HandleDirection.POINT_DIR)

        handle_list.append(handle_alto_pld)

        return handle_list

    def get_handle_point_from_cuboid_rotated(self, cuboid, vertice_index):
        """_summary_

        Args:
            cuboid (_type_): _description_
            vertice_index (_type_): _description_

        Returns:
            _type_: _description_
        """
        vertices_cuboid = cuboid.GetVertices()
        coords = vertices_cuboid[vertice_index].GetCoords()
        coords_cuboid = AllplanGeo.Point3D(coords[0], coords[1], coords[2])
        return coords_cuboid

     # CREATE ALL
    def create(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Set color
        self.color_pld = self.get_color_pld()

        # Validate creation
        if not self.is_valid():
            print("No valid Create PLD")

        # Create cuboids
        # Create PLD bordes afilados
        pld_cuboid, pld_bordes_afilados_cuboid = self.create_pld_bordes_afilados()

        # If rotation
        if self.z_rotation != 0:
            # Rotate cuboids
            # Rotate PLD cuboid
            pld_bordes_afilados_cuboid = self.rotate_cuboid(pld_bordes_afilados_cuboid)
            pld_cuboid = self.rotate_cuboid(pld_cuboid)

        # If in clination rotation
        if self.inclination_rotation_angle != 0:
            # Rotate cuboids
            # Rotate PLD cuboid

            pld_bordes_afilados_cuboid = self.inclination_rotate_geo_object(pld_bordes_afilados_cuboid)
            pld_cuboid = self.inclination_rotate_geo_object(pld_cuboid)

        self.handle_point_cuboid_pld_rotated_ancho = self.get_handle_point_from_cuboid_rotated(
            pld_cuboid, self.handle_point_cuboid_pld_rotated_ancho_index)
        self.handle_ref_point_cuboid_pld_rotated_ancho = self.get_handle_point_from_cuboid_rotated(
            pld_cuboid, self.handle_ref_point_cuboid_pld_rotated_ancho_index)
        # Handle point alto PLD
        self.handle_point_cuboid_pld_rotated_alto = self.get_handle_point_from_cuboid_rotated(
            pld_cuboid, self.handle_point_cuboid_pld_rotated_alto_index)
        self.handle_ref_point_cuboid_pld_rotated_alto = self.get_handle_point_from_cuboid_rotated(
            pld_cuboid, self.handle_ref_point_cuboid_pld_rotated_alto_index)

        # Define model element and add cuboids
        model_elements = ModelEleList()

        # Get common properties
        # PLD
        common_properties_pld = self.set_and_get_common_properties_pld()

        # Add PLD borde afinado to model elements
        model_elements.append_geometry_3d(pld_bordes_afilados_cuboid, common_properties_pld)

        # Set attributes
        # PLD attributes
        pld_attributes = self.set_and_return_attributes_pld()
        model_elements.set_element_attributes(0, pld_attributes.get_attribute_list())

        return model_elements

