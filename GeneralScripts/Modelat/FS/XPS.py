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
from DocumentManager import DocumentManager

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

    def __init__(self, doc: AllplanEleAdapter.DocumentAdapter, z_unique: int, ancho_pld, alto_pld, grosor_xps, z_rotation: int, layer_value_name: int):
        """Initialize values

        Args:
            doc (AllplanEleAdapter.DocumentAdapter): _description_
            z_unique (int): _description_
            ancho_pld (_type_): _description_
            alto_pld (_type_): _description_
            grosor_xps (_type_): _description_
            z_rotation (int): _description_
            layer_value_name (int): _description_
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
        # XPS
        self.default_color_xps = 1
        self.color_xps = self.default_color_xps

        # Layer name
        self.layer_name_pld = ""
        self.layer_name_xps = ""

        # Set values
        self._doc = doc
        self.z_rotation = z_rotation
        self.z_unique = z_unique
        self.ancho_pld = ancho_pld
        self.alto_pld = alto_pld
        # XPS
        self.desface_value_by_side = self.default_desfasado_pld * 2
        self.alto_xps = self.alto_pld - self.desface_value_by_side
        self.ancho_xps = self.ancho_pld - self.desface_value_by_side

        self.grosor_xps = grosor_xps
        self.layer_name_xps = f"FS_XPS-{layer_value_name}"

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
        """Create all cuboids

        Returns:
            _type_: _description_
        """
        # Set color
        self.color_xps = self.get_color_xps()

        # Validate creation
        if not self.is_valid():
            print("No valid Create XPS or PLD")

        # Create cuboids

        # Create XPS
        xps_cuboid = self.create_xps()

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

        # Define model element and add cuboids
        model_elements = ModelEleList()

        # Get common properties
        # XPS
        common_properties_xps = self.set_and_get_common_properties_xps()

        # Add XPS cuboid and its common properties
        model_elements.append_geometry_3d(xps_cuboid, common_properties_xps)

        # Set attributes
        # XPS attributes
        xps_attributes = self.set_and_return_attributes_xps()
        model_elements.set_element_attributes(0, xps_attributes.get_attribute_list())

        return model_elements