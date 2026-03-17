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

print('Load FS_Conjunt.py')

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

class FS:
    """Definition of class FS
    """
    def __init__(self):
        """Initialize with default values"""
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
        self.default_color_pld = 7
        self.color_pld = self.default_color_pld
        # Type PLD
        self.default_type_pld = "OMNIA"
        self.type_pld = self.default_type_pld

        # XPS
        self.default_color_xps = 1
        self.color_xps = self.default_color_xps

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

    def set_rotation_values(self, build_ele: BuildingElement) -> None:
        """ Function to set rotation values

        Args:
            build_ele (BuildingElement): _description_
        """
        if hasattr(build_ele, self.name_parameter_z_rotation_input):
            self.z_rotation = build_ele.ZRotationInput.value
        else:
           self.default_rotation = 0

    def set_values_pld(self, build_ele: BuildingElement) -> None:
        """ Function to set values from 'build_ele' PLD

        Args:
            build_ele (BuildingElement): _description_
        """
        # PLD
        self.z_unique = build_ele.zUnique.value if hasattr(build_ele, self.name_parameter_zunique) else self.default_z_unique
        self.ancho_pld = build_ele.AnchoPLD.value if hasattr(build_ele, self.name_parameter_ancho_pld) else self.defaul_ancho_pld
        self.alto_pld = build_ele.LargoPLD.value if hasattr(build_ele, self.name_parameter_ancho_pld) else self.default_alto_pld
        self.grosor_pld = build_ele.EspesorPLD.value if hasattr(build_ele, self.name_parameter_grosor_pld) else self.default_grosor_pld

    def set_values_xps(self, build_ele: BuildingElement) -> None:
        """Function to set values from 'build_ele' XPS

        Args:
            build_ele (BuildingElement): _description_
        """
        # XPS
        # Definir desface por cada lado
        desface_value_by_side = self.default_desfasado_pld * 2

        # Actualizar pld data
        self.set_values_pld(build_ele)

        # Set values XPS ancho y alto teniendo en cuenta el desface
        self.alto_xps = self.alto_pld - desface_value_by_side
        self.ancho_xps = self.ancho_pld - desface_value_by_side

        # set espesor value
        self.grosor_xps = build_ele.EspesorXPS.value if hasattr(build_ele, self.name_parameter_grosor_xps) else self.default_grosor_xps

    def set_all_values(self, build_ele: BuildingElement):
        """Function to set all necessary values

        Args:
            build_ele (BuildingElement): _description_
        """
        # Measures
        self.set_values_pld(build_ele)
        self.set_values_xps(build_ele)
        # Rotation
        self.set_rotation_values(build_ele)
        # color
        self.set_type_pld(build_ele)
        self.set_color_pld()
        self.set_color_xps()
        # Layers
        self.set_layer_names(build_ele)

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

    def set_type_pld(self, build_ele: BuildingElement):
        """_summary_

        Args:
            build_ele (BuildingElement): _description_
        """
        # Get PLD type selection

        type_pld = build_ele.get_property(self.name_parameter_type_pld)
        self.type_pld = type_pld.value if type_pld is not None else self.default_type_pld

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

        return self.default_color_xps

    def set_color_pld(self) -> None:
        """Function to set PLD color
        """
        self.color_pld = self.get_color_pld()

    def get_color_xps(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Constantes
        ancho_xps_lower_value = 596

        # Grosor XPS
        grosor_xps_value_120 = 120
        grosor_xps_value_100 = 100
        grosor_xps_value_70 = 70
        grosor_xps_value_50 = 50
        grosor_xps_value_40 = 40

        # Valores redondeados para comparación
        ancho_xps_round = round(self.ancho_xps)

        # Colors:
        color_1200x120 = 206
        color_1200x100 = 134
        color_1200x70 = 13
        color_1200x50 = 12
        color_1200x40 = 235
        color_600x120 = 14
        color_600x100 = 198
        color_600x70 = 11
        color_600x50 = 8
        color_600x40 = 220
        color_default = self.default_color_xps

        # Validation ancho XPS low to high value
        if ancho_xps_round > ancho_xps_lower_value:

            # Validate iterating for the differents grosor values:
            if self.grosor_xps == grosor_xps_value_120:
                return color_1200x120
            if self.grosor_xps == grosor_xps_value_100:
                return color_1200x100
            if self.grosor_xps == grosor_xps_value_70:
                return color_1200x70
            if self.grosor_xps == grosor_xps_value_50:
                return color_1200x50
            if self.grosor_xps == grosor_xps_value_40:
                return color_1200x40

        # Validation ancho XPS min to low value
        else:

            # Validate iterating for the differents grosor values:
            if self.grosor_xps == grosor_xps_value_120:
                return color_600x120
            if self.grosor_xps == grosor_xps_value_100:
                return color_600x100
            if self.grosor_xps == grosor_xps_value_70:
                return color_600x70
            if self.grosor_xps == grosor_xps_value_50:
                return color_600x50
            if self.grosor_xps == grosor_xps_value_40:
                return color_600x40

        return color_default

    def set_color_xps(self) -> None:
        """ Function to set color XPS
        """
        self.color_xps = self.get_color_xps()

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

    def set_and_return_attributes_xps(self):
        """Set XPS attributes

        Returns:
            _type_: _description_
        """
        # Define constantes
        min_value_ancho_xps = 600

        # Define values: alto, ancho, grosor
        alto_value_attribute = 3000
        ancho_value_attribute = 600 if self.ancho_xps <= min_value_ancho_xps else 1200
        grosor_value_attribute = round(self.grosor_xps)

        attribute_list = BuildingElementAttributeList()

        # Define attributes

        attribute_custom_01 = f"{alto_value_attribute}x{ancho_value_attribute}x{grosor_value_attribute}mm"
        attribute_custom_05 = f"{alto_value_attribute}x{ancho_value_attribute}x{grosor_value_attribute}"

        attr_list = [
            AllplanBaseElements.AttributeString(1083, attribute_custom_01), # atrribute personalizado 01
            AllplanBaseElements.AttributeString(1084, ""), # atrribute personalizado 02
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

    def set_layer_names(self, build_ele: BuildingElement) -> None:
        """Set layer names

        Args:
            build_ele (BuildingElement): _description_
        """
        layer_value_name = build_ele.LayerValueName.value
        self.layer_name_pld = f"FS_PLD-{layer_value_name}"
        self.layer_name_xps = f"FS_XPS-{layer_value_name}"

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

    # Create XPS
    def create_xps_cuboid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = self.ancho_xps,
            width     = self.alto_xps,
            height    = self.grosor_xps
        )

        return cuboid

    def move_xps_cuboid(self, cuboid):
        """_summary_

        Args:
            cuboid (_type_): _description_

        Returns:
            _type_: _description_
        """
        initial_x_axis = self.default_desfasado_pld
        initial_y_axis = self.default_desfasado_pld
        initial_z_elevetion = self.grosor_pld

        # Position XPS plate above PLD with 2mm offset from each edge and elevetion in Z axis to avoid overlap
        return AllplanGeo.Move(cuboid, AllplanGeo.Vector3D(initial_x_axis, initial_y_axis, initial_z_elevetion))

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
    def create_pld_bordes_afilados(self, build_ele: BuildingElement):
        """Create pld bordes afilados

        Args:
            build_ele (BuildingElement): _description_

        Returns:
            _type_: _description_
        """
        # Get value borde afilado selector
        borde_afilado_selector = build_ele.get_property(self.name_parameter_borde_afilado_selector)
        borde_afilado_selector_value = borde_afilado_selector.value if borde_afilado_selector is not None else self.borde_afilado_left

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

    # Create XPS
    def create_xps(self):
        """Create XPS function

        Returns:
            _type_: _description_
        """
        # Create XPS and move
        xps_cuboid = self.create_xps_cuboid()
        xps_cuboid = self.move_xps_cuboid(xps_cuboid)
        return xps_cuboid

    # Common properties
    # PLD
    def set_and_get_common_properties_pld(self, _doc: AllplanEleAdapter.DocumentAdapter):
        """Function to set and get common properties PLD

        Args:
            _doc (AllplanEleAdapter.DocumentAdapter): _description_

        Returns:
            _type_: _description_
        """
        common_properties_pld = AllplanBaseElements.CommonProperties()
        # Set color PLD
        common_properties_pld.Color = self.color_pld
        # Set layer PLD
        layer_pld_id = AllplanBaseElements.LayerService.GetIDByShortName(self.layer_name_pld, _doc)
        common_properties_pld.Layer = layer_pld_id
        return common_properties_pld

    # XPS
    def set_and_get_common_properties_xps(self, _doc: AllplanEleAdapter.DocumentAdapter):
        """Function to set and get common properties XPS

        Args:
            _doc (AllplanEleAdapter.DocumentAdapter): _description_

        Returns:
            _type_: _description_
        """
        common_properties_xps = AllplanBaseElements.CommonProperties()
        # Get and set color XPS
        common_properties_xps.Color = self.color_xps
        # Set layer XPS
        layer_xps_id = AllplanBaseElements.LayerService.GetIDByShortName(self.layer_name_xps, _doc)
        common_properties_xps.Layer = layer_xps_id
        return common_properties_xps

    # Handles
    def create_handles(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        handle_list = []

        # handle_parameter_data_ancho_pld = HandleParameterData("AnchoPLD", HandleParameterType.X_DISTANCE)

        # initial_handle_point_pld = AllplanGeo.Point3D(self.ancho_pld, 0, 0)

        # handle_ancho_pld = HandleProperties("ancho_pld",
        #                    initial_handle_point_pld,
        #                    AllplanGeo.Point3D(0, 0, 0),
        #                    [handle_parameter_data_ancho_pld],
        #                    HandleDirection.X_DIR, )

        # if self.z_rotation != 0:

        handle_parameter_data_ancho_pld = HandleParameterData("AnchoPLD", HandleParameterType.POINT_DISTANCE)

        handle_ancho_pld = HandleProperties("ancho_pld",
                        self.handle_point_cuboid_pld_rotated_ancho,
                        self.handle_ref_point_cuboid_pld_rotated_ancho,
                        [handle_parameter_data_ancho_pld],
                        HandleDirection.POINT_DIR)
            #handle_ancho_pld.handle_point = AllplanGeo.Point3D(2100, 900, 0)
            # handle_ancho_pld.ref_point = self.handle_ref_point_cuboid_pld_rotated_ancho
            # handle_ancho_pld.handle_point = self.handle_point_cuboid_pld_rotated_ancho


        # handle_ancho_pld.handle_point = AllplanGeo.Point3D(2000, 0, 0)
        handle_list.append(handle_ancho_pld)

        # initial_handle_point_xps = AllplanGeo.Point3D(0, self.alto_pld, 0)

        # handle_parameter_data_alto_pld = HandleParameterData("LargoPLD", HandleParameterType.Y_DISTANCE)

        # handle_alto_pld =  HandleProperties("alto_pld",
        #                    initial_handle_point_xps,
        #                    AllplanGeo.Point3D(0, 0, 0),
        #                    [handle_parameter_data_alto_pld],
        #                    HandleDirection.Y_DIR)

        # if self.z_rotation != 0:

        handle_parameter_data_alto_pld = HandleParameterData("LargoPLD", HandleParameterType.POINT_DISTANCE)

        handle_alto_pld =  HandleProperties("alto_pld",
                        self.handle_point_cuboid_pld_rotated_alto,
                        self.handle_ref_point_cuboid_pld_rotated_alto,
                        [handle_parameter_data_alto_pld],
                        HandleDirection.POINT_DIR)
            #handle_ancho_pld.handle_point = AllplanGeo.Point3D(2100, 900, 0)
            # handle_parameter_data_alto_pld = HandleParameterData("LargoPLD", HandleParameterType.POINT_DISTANCE)
            # handle_alto_pld.ref_point = self.handle_ref_point_cuboid_pld_rotated_alto
            # handle_alto_pld.handle_point = self.handle_point_cuboid_pld_rotated_alto

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
    def create(self, build_ele: BuildingElement, _doc: AllplanEleAdapter.DocumentAdapter):
        """_summary_

        Args:
            build_ele (BuildingElement): _description_

        Returns:
            _type_: _description_
        """
        # Set all values
        self.set_all_values(build_ele)

        # Validate creation
        if not self.is_valid():
            print("No valid Create XPS or PLD")

        # Create cuboids
        # Create PLD bordes afilados
        pld_cuboid, pld_bordes_afilados_cuboid = self.create_pld_bordes_afilados(build_ele)

        # Create XPS
        xps_cuboid = self.create_xps()

        # If rotation
        if self.z_rotation != 0:
            # Rotate cuboids
            # Rotate PLD cuboid
            pld_bordes_afilados_cuboid = self.rotate_cuboid(pld_bordes_afilados_cuboid)
            pld_cuboid = self.rotate_cuboid(pld_cuboid)
            # Set handle point pdl cuboid rotated ancho y alto
            # Handle point ancho PLD
            # Rotate XPS cuboid
            xps_cuboid = self.rotate_cuboid(xps_cuboid)


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
        common_properties_pld = self.set_and_get_common_properties_pld(_doc)
        # XPS
        common_properties_xps = self.set_and_get_common_properties_xps(_doc)

        # Add PLD borde afinado to model elements
        model_elements.append_geometry_3d(pld_bordes_afilados_cuboid, common_properties_pld)

        # Add XPS cuboid and its common properties
        model_elements.append_geometry_3d(xps_cuboid, common_properties_xps)

        # Set attributes
        # PLD attributes
        pld_attributes = self.set_and_return_attributes_pld()
        model_elements.set_element_attributes(0, pld_attributes.get_attribute_list())
        # XPS attributes
        xps_attributes = self.set_and_return_attributes_xps()
        model_elements.set_element_attributes(1, xps_attributes.get_attribute_list())

        return model_elements

def create_element(build_ele:   BuildingElement,

                   _doc:        AllplanEleAdapter.DocumentAdapter) -> CreateElementResult:
    """Creation of the cuboid

    Args:
        build_ele: building element with the parameter properties
        _doc:      document of the Allplan drawing files

    Returns:
        created element result
    """
    fs_element = FS()

    # Create elements
    model_elements = fs_element.create(build_ele, _doc)

    # Create handles after update values
    handle_list = fs_element.create_handles()

    return CreateElementResult(elements = model_elements, handles = handle_list)
