"""Module providing paythonpart FS."""

import random
from typing import List
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
from DocumentManager import DocumentManager
from .InclinationManager import InclinationManager

print('Load XPS.py')

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
    grosor_xps = build_ele.EspesorXPS.value
    z_rotation = build_ele.ZRotationInput.value
    layer_value_name = build_ele.LayerValueName.value
    # grosor_pld = build_ele.EspesorPLD.value if hasattr(build_ele, self.name_parameter_grosor_pld) else self.default_grosor_pld
    # Define model element and add figures
    model_elements = ModelEleList()

    xps_element = XPS(_doc, z_unique, ancho_pld, alto_pld, grosor_xps, z_rotation, layer_value_name)

    # Create elements
    model_elements += xps_element.create()

    # Create handles after update values
    handle_list = xps_element.create_handles()

    return CreateElementResult(elements = model_elements, handles = handle_list)

class XPS():
    """_XPS class
    """

    def __init__(self, doc: AllplanEleAdapter.DocumentAdapter, z_unique: int,
                 ancho_xps, alto_xps, grosor_xps, z_rotation: int, layer_name: str, initial_position: AllplanGeo.Vector3D|None = None,
                initial_inclination_rotation_list_input: list[tuple[str, int]]|None = None, add_xps_transporte: bool = False,
                 largo_xps_transport_value: int|None = None, cortes_zona_list: List[AllplanGeo.Polyhedron3D] = [], selector_lado_xps_transport_value: int|None = None):
        """Initialize values

        Args:
            doc (AllplanEleAdapter.DocumentAdapter): _description_
            z_unique (int): _description_
            ancho_xps (_type_): _description_
            alto_xps (_type_): _description_
            grosor_xps (_type_): _description_
            z_rotation (int): _description_
            layer_name (str): _description_
            initial_position (AllplanGeo.Vector3D): _description_
            initial_inclinacion_rotacion_lados_list (List): _description_
            add_xps_transporte (bool, optional): _description_. Defaults to False.
            largo_xps_transport_value (int | None, optional): _description_. Defaults to None.
            selector_lado_xps_transport_value (int | None, optional): _description_. Defaults to None.
        """
        # Default values
        self.default_z_unique = random.random() * 3600

        # Set values
        self._doc = doc
        self.z_rotation = z_rotation
        self.z_unique = z_unique
        self.initial_position = initial_position
        self.initial_inclination_rotation_list_input = initial_inclination_rotation_list_input
        # XPS
        # Definir desface por cada lado
        #self.alto_xps = self.alto_pld
        #self.ancho_xps = self.ancho_pld
        #self.grosor_xps = grosor_xps
        #self.layer_name_xps = layer_name

        self.alto_xps = alto_xps
        self.ancho_xps = ancho_xps
        self.grosor_xps = grosor_xps
        self.layer_name_xps = layer_name

        # Initial position XPS
        self.relative_position_xps_x =  2  # Posición relativa X del XPS (respecto al FS)
        self.relative_position_xps_y =  2  # Posición relativa Y del XPS
        self.relative_position_xps_z =  15 # Posición relativa Z del XPS

        # Default values
        self.default_alto_xps = 2996
        self.default_ancho_xps = 1196
        self.default_grosor_xps = 40

        # Rotation
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
        # XPS
        self.default_color_xps = 1
        self.color_xps = self.default_color_xps

        # Layer name
        self.layer_name_pld = ""
        self.layer_name_xps = ""

        # Cavidades
        self.color_cavidad_xps = 11
        self.layer_name_cavidad_xps = "KN_XPS_RECESS"
        self.layer_name_cavidad_corte = "FS_XPS_D-1"

        # XPS transporte
        self.add_xps_transporte = add_xps_transporte
        self.largo_xps_transport_value = largo_xps_transport_value
        self.largo_xps_transport_total = self.largo_xps_transport_value - self.alto_xps
        self.selector_lado_xps_transport_value = selector_lado_xps_transport_value
        self.left_side_selector_lado_xps_transport_value = 1
        self.right_side_selector_lado_xps_transport_value = 2
        self.both_sides_selector_lado_xps_transport_value = 3

        # FS inclination manager class
        # TODO no así
        # self.fs_inclination_manager_class = InclinationManager(self.ancho_pld, self.alto_pld, self.grosor_pld, self.grosor_xps, self.z_unique)

        # Cortes zona
        self.cortes_zona_list = cortes_zona_list

        # Model element list
        self.elements_to_create     = ModelEleList()

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
        center_x = self.ancho_xps / 2
        center_y = self.alto_xps / 2
        center_z = self.grosor_xps / 2
        center_point = AllplanGeo.Point3D(center_x, center_y, center_z)
        return center_point

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

    # Set inital position
    def set_initial_position(self):
        if self.initial_position:
            self.initial_position = AllplanGeo.Vector3D(
                self.initial_position.X + self.relative_position_xps_x,
                self.initial_position.Y + self.relative_position_xps_y,
                self.initial_position.Z + self.relative_position_xps_z)
        return None

    # Create XPS
    # Create XPS cuboid
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

    # Create XPS cuboid transporte
    def create_xps_cuboid_transporte(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = self.ancho_xps,
            width     = self.largo_xps_transport_total,
            height    = self.grosor_xps
        )

        return cuboid

    def move_xps_cuboid(self, cuboid, position: AllplanGeo.Vector3D):
        """_summary_

        Args:
            cuboid (_type_): _description_

        Returns:
            _type_: _description_
        """
        cuboid = AllplanGeo.Move(cuboid, position)
        return cuboid
        # return AllplanGeo.Move(cuboid, position)

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
        #center_point = AllplanGeo.Point3D()
        rotation.Rotation(AllplanGeo.Line3D(center_point, AllplanGeo.Vector3D(0, 0, 1)), angle)
        return AllplanGeo.Transform(cuboid, rotation)

    def get_axis_geo_object_xps_from_3d_points(self, initial_coords_vertice, final_coords_vertice):
        # Using points 3D

        # initial coords

        #initial_coord_xps_x = initial_coords_vertice.X + self.default_desfasado_pld
        #initial_coord_xps_y = initial_coords_vertice.Y + self.default_desfasado_pld
        #initial_coord_xps_z = initial_coords_vertice.Z - 5
        #initial_coords_xps = AllplanGeo.Point3D(initial_coord_xps_x, initial_coord_xps_y, initial_coord_xps_z)

        # initial_vertice_index = 0
        #final_coord_xps_x = final_coords_vertice.X + self.default_desfasado_pld
        #final_coord_xps_y = final_coords_vertice.Y - self.default_desfasado_pld
        #final_coord_xps_z = final_coords_vertice.Z - 5
        #final_coords_xps = AllplanGeo.Point3D(final_coord_xps_x, final_coord_xps_y, final_coord_xps_z)

        #initial_coords = vertices_cuboid[initial_vertice_index].GetCoords()

        #initial_coords_cuboid = AllplanGeo.Point3D(initial_coords[0], initial_coords[1], initial_coords[2])
        #final_vertice_index = 3
        #final_coords = vertices_cuboid[final_vertice_index].GetCoords()
        #final_coords_cuboid = AllplanGeo.Point3D(final_coords[0], final_coords[1], final_coords[2])

        #point_initial = AllplanGeo.Point3D(0, 0, 0)

        initial_coords_xps = AllplanGeo.Point3D(-2,-2,0)
        final_coords_xps = AllplanGeo.Point3D(-2,2996,15)

        return AllplanGeo.Line3D(initial_coords_xps, final_coords_xps)

    def get_axis_geo_object(self, cuboid) -> AllplanGeo.Line3D| None:
        """Get axis geometry object

        Args:
            cuboid (_type_): _description_

        Returns:
            AllplanGeo.Line3D| None: _description_
        """
        #vertices_cuboid = cuboid.GetVertices()
        #error_code, lines3d_list = cuboid.GetEdgesLines()

        if self.inclination_rotation_angle_lado_a:
            # Using points 3D
            #initial_vertice_index = 0
            #initial_coords = vertices_cuboid[initial_vertice_index].GetCoords()

            #initial_coords_cuboid = AllplanGeo.Point3D(initial_coords[0], initial_coords[1], initial_coords[2])
            #final_vertice_index = 3
            #final_coords = vertices_cuboid[final_vertice_index].GetCoords()
            #final_coords_cuboid = AllplanGeo.Point3D(final_coords[0], final_coords[1], final_coords[2])

            #point_initial = AllplanGeo.Point3D(0, 0, 0)

            #return AllplanGeo.Line3D(initial_coords_cuboid, final_coords_cuboid)

            #### line 3D ####
            #index_line = 3 # (Lado A)
            #line3d_cuboid = lines3d_list[index_line]
            #return line3d_cuboid

            #line_3d = AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,15), AllplanGeo.Point3D(0,3000,15))
            #return line_3d

            initial_coords_point_3d = AllplanGeo.Point3D(-2,-2,0)
            final_coords_point_3d = AllplanGeo.Point3D(-2,2996,15)
            return AllplanGeo.Line3D(initial_coords_point_3d, final_coords_point_3d)

        return None

    def inclinate_geometry_object(self, geometry_object: AllplanGeo.Polyhedron3D, inclinacion_rotacion_lados_xps_sorted_list):

        if inclinacion_rotacion_lados_xps_sorted_list:
            for inclinacion_lado in inclinacion_rotacion_lados_xps_sorted_list:
                geometry_object = InclinationManager.inclinar_geometry_object(geometry_object, inclinacion_lado)

        return geometry_object

    # Create XPS
    def create_xps(self):
        """Create XPS function

        Returns:
            _type_: _description_
        """
        # Create XPS and move
        xps_cuboid = self.create_xps_cuboid()
        # Move initial position
        #xps_cuboid_moved = self.move_xps_cuboid(xps_cuboid, self.initial_position)
        return xps_cuboid

    # Corte zona
    def create_corte_zona_xps(self, main_cuboid: AllplanGeo.Polyhedron3D):
        if self.cortes_zona_list:
            for corte_cavidad in self.cortes_zona_list:
                error, intersection, union, subtraction1, subtraction2 = AllplanGeo.MakeBoolean(corte_cavidad, main_cuboid)

                # if the operation was successful, and the resulting elements
                # are valid polyhedrons, create the 3d elements in the drawing file
                if error == AllplanGeo.eGeometryErrorCode.eOK:
                    if intersection.IsValid():
                        self.elements_to_create.append_geometry_3d(subtraction1, self.set_and_get_common_properties_cavidad_xps())

                    if subtraction2.IsValid():
                        self.elements_to_create.append_geometry_3d(subtraction1, self.set_and_get_common_properties_xps())

    # Create XPS
    def create_xps_transporte(self):
        """Create XPS function

        Returns:
            _type_: _description_
        """
        # Create XPS and move
        xps_cuboid = self.create_xps_cuboid_transporte()
        # Move initial position
        #xps_cuboid_moved = self.move_xps_cuboid(xps_cuboid, self.initial_position)
        return xps_cuboid

    def get_vector_3d_lado_cuboid(self, geometry_object: AllplanGeo.Polyhedron3D, initial_index_lado: int, final_index_lado: int):
        vertices_cuboid = geometry_object.GetVertices()
        # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

        # Lado geometry object
        # Using points 3D
        # Initial coords
        initial_vertice_index_lado = initial_index_lado
        initial_coords_lado = vertices_cuboid[initial_vertice_index_lado].GetCoords()
        initial_coords_point_3d_lado = AllplanGeo.Point3D(initial_coords_lado[0], initial_coords_lado[1], initial_coords_lado[2])

        # Final coords
        final_vertice_index_lado = final_index_lado
        final_coords_lado = vertices_cuboid[final_vertice_index_lado].GetCoords()
        final_coords_point_3d_lado = AllplanGeo.Point3D(final_coords_lado[0], final_coords_lado[1], final_coords_lado[2])

        #line_lado = AllplanGeo.Line3D(initial_coords_point_3d_lado, final_coords_point_3d_lado)
        vector_3d_lado = AllplanGeo.Vector3D(final_coords_point_3d_lado.X, final_coords_point_3d_lado.Y,  final_coords_point_3d_lado.Z)

        return vector_3d_lado

    def get_initial_position_for_xps_transporte(self, cuboid: AllplanGeo.Polyhedron3D) -> AllplanGeo.Vector3D:
        default_side_vector = self.initial_position
        if self.selector_lado_xps_transport_value == self.left_side_selector_lado_xps_transport_value:
            initial_index = 5
            final_index = 6
            left_side_vector_3d = self.get_vector_3d_lado_cuboid(cuboid, initial_index, final_index)
            return left_side_vector_3d
        return default_side_vector

    # Modelizacion XPS transporte
    def modeling_xps_transporte(self, cuboid: AllplanGeo.Polyhedron3D, cuboid_reference: AllplanGeo.Polyhedron3D):
        if self.add_xps_transporte:
            xps_transporte = cuboid
            initial_position = self.get_initial_position_for_xps_transporte(cuboid_reference)
            self.move_xps_cuboid(cuboid, initial_position)
            return xps_transporte
        return None

    # Modelizacion XPS transporte
    def create_xps_transporte(self):
        if self.add_xps_transporte:
            xps_transporte = self.create_xps_cuboid_transporte()
            return xps_transporte
        return None

    #Create cavidades
    def get_polyhedron1_test(self, length_poly1: float| None = None, width_poly1: float| None = None, height_poly1: float| None = None) -> AllplanGeo.Polyhedron3D:
        """_summary_

        Args:
            length_poly1 (float | None, optional): _description_. Defaults to None.
            width_poly1 (float | None, optional): _description_. Defaults to None.
            height_poly1 (float | None, optional): _description_. Defaults to None.

        Returns:
            AllplanGeo.Polyhedron3D: _description_
        """
        default_length_poly1 = 300.0
        default_width_poly1 = 400.0
        default_height_poly1 = 500.0

        _length_poly1 = length_poly1 if length_poly1 else default_length_poly1
        _width_poly1 = width_poly1 if width_poly1 else default_width_poly1
        _height_poly1 = height_poly1 if height_poly1 else default_height_poly1
        polyhed1 = AllplanGeo.Polyhedron3D.CreateCuboid(_length_poly1, _width_poly1, _height_poly1)
        return polyhed1

    def get_polyhedron2_test(self) -> AllplanGeo.Polyhedron3D:
        """_summary_

        Returns:
            AllplanGeo.Polyhedron3D: _description_
        """
        p1_poly2 = AllplanGeo.Point3D(2000, 1000, 2000)
        p2_poly2 = AllplanGeo.Point3D(5000, 5000, 7000)
        polyhed2 = AllplanGeo.Polyhedron3D.CreateCuboid(p1_poly2, p2_poly2)
        return polyhed2

    def calculate_boolean(self, polyhedron3d: AllplanGeo.Polyhedron3D,  cavidades_polynhedron3d_list: list[AllplanGeo.Polyhedron3D] = []):
        """Create boolean

        Args:
            polyhedron3d (AllplanGeo.Polyhedron3D): _description_
            cavidades_polynhedron3d_list (list[AllplanGeo.Polyhedron3D], optional): _description_. Defaults to [].
        """
        for cavidad in cavidades_polynhedron3d_list:

            error, intersection, union, subtraction1, subtraction2 = AllplanGeo.MakeBoolean(cavidad, polyhedron3d)

            # if the operation was successful, and the resulting elements
            # are valid polyhedrons, create the 3d elements in the drawing file
            if error == AllplanGeo.eOK:
                if intersection.IsValid():
                    self.elements_to_create.append_geometry_3d(intersection, self.set_and_get_common_properties_cavidad_xps())

                if all and subtraction2.IsValid():
                    self.elements_to_create.append_geometry_3d(subtraction2, self.set_and_get_common_properties_xps())

    def calculate_boolean_test(self, polyhedron3d: AllplanGeo.Polyhedron3D):
        """Create boolean test

        Args:
            polyhedron3d (AllplanGeo.Polyhedron3D): _description_
        """
        polyhed1 = self.get_polyhedron1_test()

        cavidades_polynhedron3d_list: list[AllplanGeo.Polyhedron3D] = []

        cavidades_polynhedron3d_list.append(polyhed1)

        for cavidad in cavidades_polynhedron3d_list:

            error, intersection, union, subtraction1, subtraction2 = AllplanGeo.MakeBoolean(cavidad, polyhedron3d)

            # if the operation was successful, and the resulting elements
            # are valid polyhedrons, create the 3d elements in the drawing file
            if error == AllplanGeo.eOK:
                if intersection.IsValid():
                    self.elements_to_create.append_geometry_3d(intersection, self.set_and_get_common_properties_cavidad_xps())

                if subtraction2.IsValid():
                    self.elements_to_create.append_geometry_3d(subtraction2, self.set_and_get_common_properties_xps())

    # Common properties
    # XPS
    def set_and_get_common_properties_xps(self):
        """Function to set and get common properties XPS

        Returns:
            _type_: _description_
        """
        common_properties_xps = AllplanBaseElements.CommonProperties()
        # Get and set color XPS
        common_properties_xps.Color = self.color_xps
        # Set layer XPS
        layer_xps_id = AllplanBaseElements.LayerService.GetIDByShortName(self.layer_name_xps, self._doc)
        common_properties_xps.Layer = layer_xps_id
        return common_properties_xps

    # Cavidad XPS
    def set_and_get_common_properties_cavidad_xps(self):
        """Function to set and get common properties cavidad XPS

        Returns:
            _type_: _description_
        """
        common_properties_cavidad_xps = AllplanBaseElements.CommonProperties()
        # Set color PLD
        common_properties_cavidad_xps.Color = self.color_cavidad_xps
        # Set layer PLD
        layer_cavidad_pld_id = AllplanBaseElements.LayerService.GetIDByShortName(self.layer_name_cavidad_xps, self._doc)
        common_properties_cavidad_xps.Layer = layer_cavidad_pld_id
        return common_properties_cavidad_xps

    # Handles
    def create_handles(self):
        """Create handles

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
    def create(self, cavidades_polynhedron3d_list: list[AllplanGeo.Polyhedron3D] = [],
               create_cavidades_manuales=False, inclinacion_rotacion_lados_xps_sorted_list: List = [], test=False):
        """Create all

        Args:
            cavidades_polynhedron3d_list (list[AllplanGeo.Polyhedron3D], optional): _description_. Defaults to [].
            create_cavidades_manuales (bool, optional): _description_. Defaults to False.
            inclinacion_rotacion_lados_xps_sorted_list (List, optional): _description_. Defaults to [].
            test (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        # Set color
        self.color_xps = self.get_color_xps()

        # Validate creation
        if not self.is_valid():
            print("No valid Create XPS or PLD")

        # Create cuboids
        # Create XPS and initial position
        xps_cuboid = self.create_xps()

        # Initial inclination rotation
        # TODO no así
        # if self.initial_inclination_rotation_list_input:
        #     _initial_inclination_rotation_lados_pld_sorted_list, _initial_inclination_rotation_lados_xps_sorted_list = self.fs_inclination_manager_class.set_update_inclination_xps_pld_from_inclination_rotation_list_input(
        #         self.initial_inclination_rotation_list_input)

        #     xps_cuboid = self.inclinate_geometry_object(xps_cuboid, _initial_inclination_rotation_lados_xps_sorted_list)

        # Move initial position
        # Set initial position
        self.set_initial_position()
        if self.initial_position:
            xps_cuboid = self.move_xps_cuboid(xps_cuboid, self.initial_position)

        xps_transporte_cuboid = self.create_xps_transporte()
        if (xps_transporte_cuboid := self.create_xps_transporte()):
            xps_transporte_cuboid = self.modeling_xps_transporte(xps_transporte_cuboid, xps_cuboid)

        # Inclination rotate XPS cuboid from user params
        xps_cuboid = self.inclinate_geometry_object(xps_cuboid, inclinacion_rotacion_lados_xps_sorted_list)

        # If rotation
        if self.z_rotation != 0:
            # Rotate cuboids
            # Set handle point pdl cuboid rotated ancho y alto
            # Handle point ancho PLD
            # Rotate XPS cuboid
            xps_cuboid = self.rotate_cuboid(xps_cuboid)

        self.handle_point_cuboid_pld_rotated_ancho = self.get_handle_point_from_cuboid_rotated(
            xps_cuboid, self.handle_point_cuboid_pld_rotated_ancho_index)
        self.handle_ref_point_cuboid_pld_rotated_ancho = self.get_handle_point_from_cuboid_rotated(
            xps_cuboid, self.handle_ref_point_cuboid_pld_rotated_ancho_index)
        # Handle point alto PLD
        self.handle_point_cuboid_pld_rotated_alto = self.get_handle_point_from_cuboid_rotated(
            xps_cuboid, self.handle_point_cuboid_pld_rotated_alto_index)
        self.handle_ref_point_cuboid_pld_rotated_alto = self.get_handle_point_from_cuboid_rotated(
            xps_cuboid, self.handle_ref_point_cuboid_pld_rotated_alto_index)

        # Add modeling XPS transporte
        if xps_transporte_cuboid:
            # Get common properties
            # XPS
            common_properties_xps = self.set_and_get_common_properties_xps()
            self.elements_to_create.append_geometry_3d(xps_transporte_cuboid, common_properties_xps)

        # Define model element and add cuboids
        if cavidades_polynhedron3d_list:
            if test and not create_cavidades_manuales:
                self.calculate_boolean_test(xps_cuboid)
            else:
                self.calculate_boolean(xps_cuboid, cavidades_polynhedron3d_list)
        else:
            # Get common properties
            # XPS
            common_properties_xps = self.set_and_get_common_properties_xps()
            self.elements_to_create.append_geometry_3d(xps_cuboid, common_properties_xps)

        # Set attributes
        # XPS attributes
        xps_attributes = self.set_and_return_attributes_xps()
        if cavidades_polynhedron3d_list and len(self.elements_to_create) > 1:
            self.elements_to_create.set_element_attributes(1, xps_attributes.get_attribute_list())
        else:
            self.elements_to_create.set_element_attributes(0, xps_attributes.get_attribute_list())

        return self.elements_to_create