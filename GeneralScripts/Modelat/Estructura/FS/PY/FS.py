""" Example script for FS
"""
import math
import random
from typing import List, Tuple
from .PLD import PLD
from .XPS import XPS
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
from CreateElementResult import CreateElementResult
from DocumentManager import DocumentManager
from TypeCollections.ModelEleList import ModelEleList
from BuildingElement import BuildingElement
from PythonPartUtil import PythonPartUtil
from PythonPart import PythonPart, PythonPartGroup
import NemAll_Python_BaseElements as AllplanBaseElements

from .InclinationManager import InclinationManager
from .InclinationManager import ANGLE_A_STR, ANGLE_B_STR, ANGLE_C_STR, ANGLE_D_STR

print('Load FS.py Estructura FS cav auto')

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

def create_element_class(build_ele, doc, placement_mat = AllplanGeo.Matrix3D(),
                         cavidades_polynhedron3d_list: list[AllplanGeo.Polyhedron3D] = [],
                         create_cavidades_manuales=False, test=False, inclinaciones_rotacion = []):
    """Create element class

    Args:
        build_ele (_type_): _description_
        doc (_type_): _description_
        placement_mat (_type_, optional): _description_. Defaults to AllplanGeo.Matrix3D().
        cavidades_polynhedron3d_list (list[AllplanGeo.Polyhedron3D], optional): _description_. Defaults to [].
        create_cavidades_manuales (bool, optional): _description_. Defaults to False.
        test (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    group_elems = [] #All elements of suite
    group_elems_preview = [] #All elements of suite

    # Define name parameters
    z_unique = build_ele.zUnique.value
    fs_name = build_ele.FSName.value
    ancho_pld = build_ele.AnchoPLD.value
    alto_pld = build_ele.LargoPLD.value
    grosor_pld = build_ele.EspesorPLD.value
    ancho_xps = ancho_pld - 4
    alto_xps = alto_pld - 4
    grosor_xps = build_ele.EspesorXPS.value
    z_rotation = build_ele.ZRotationInput.value
    type_pld = build_ele.TypePLD.value
    layer_value_name = build_ele.LayerValueName.value
    borde_afilado_selector = build_ele.SelectorBordeAfilado.value
    # layer names
    layer_name_pld = f"FS_PLD-{layer_value_name}"
    layer_name_xps = f"FS_XPS-{layer_value_name}"

    # inclination and rotate
    inclination_rotation_angle_lado_a = build_ele.LadoARotationInputAngle.value
    inclination_rotation_angle_lado_b = build_ele.LadoBRotationInputAngle.value
    inclination_rotation_angle_lado_c = build_ele.LadoCRotationInputAngle.value
    inclination_rotation_angle_lado_d = build_ele.LadoDRotationInputAngle.value
    # Get values from PYP (Inclination lists)
    inclination_order_list = build_ele.OrderInclinationList.value

    inclination_list = set_and_update_order_inclination(inclination_rotation_angle_lado_a, inclination_rotation_angle_lado_b, inclination_rotation_angle_lado_c, inclination_rotation_angle_lado_d, inclination_order_list)

    # Set and update order inclination
    build_ele.OrderInclinationList.value = inclination_order_list

    ejes_inclinacion_sorted_list = []

    # Get values XPS transporte
    selector_add_xps_transporte_value = build_ele.SelectorTransporte.value
    largo_xps_transport_value = build_ele.LargoXPSTransporte.value
    selector_lado_xps_transport_value = build_ele.SelectorLadoTransporteXPS.value
    add_xps_transporte = True if selector_add_xps_transporte_value and selector_add_xps_transporte_value == 2 else False

    # Define model element and add figures
    model_elements = ModelEleList()

    # Initial position FS
    #initial_position_point_fs = placement_mat
    #initial_position_point_fs = None

    # Define cortes zona list
    cortes_zona_list: List[AllplanGeo.Polyhedron3D] = []

    fs_class = FS(build_ele=build_ele, doc=doc, placement_mat = placement_mat, ancho_pld=ancho_pld, alto_pld=alto_pld, grosor_pld=grosor_pld,
                  grosor_xps=grosor_xps, z_rotation=z_rotation, inclination_list=inclination_list,
                  name=fs_name, borde_afilado_selector=borde_afilado_selector)

    # Define initial position from placement
    initial_placement = AllplanGeo.Vector3D() #fs_class.set_and_get_initial_position_from_placement()

    initial_inclination_list = inclinaciones_rotacion

    pld_element = PLD(doc, z_unique, ancho_pld, alto_pld, grosor_pld, z_rotation, type_pld, layer_name_pld, initial_placement,
                      initial_inclination_list, borde_afilado_selector)
    xps_element = XPS(doc, z_unique, ancho_xps, alto_xps, grosor_xps, z_rotation, layer_name_xps, initial_placement,
                      initial_inclination_list, add_xps_transporte, largo_xps_transport_value, cortes_zona_list, selector_lado_xps_transport_value)

    # FS inclination manager class
    fs_inclination_manager_class = fs_class.inclination_manager
    ejes_inclinacion_sorted_list = fs_inclination_manager_class.get_processed_inclinations(inclination_list)

    # Define handle points
    handle_points_cuboid = fs_inclination_manager_class.set_and_get_handle_points()

    pld = pld_element.create(cavidades_polynhedron3d_list, create_cavidades_manuales, ejes_inclinacion_sorted_list,
                             handle_points_cuboid=handle_points_cuboid, test=test)

    xps = xps_element.create(cavidades_polynhedron3d_list, create_cavidades_manuales, ejes_inclinacion_sorted_list, test=test)

    python_part_util = PythonPartUtil()

    python_part_util.add_pythonpart_view_2d3d(pld)
    python_part_util.add_pythonpart_view_2d3d(xps)

    python_part_fs = python_part_util.create_pythonpart(
                    build_ele,
                    type_display_name = "PythonPart FS",
                    #placement_matrix = AllplanGeo.Matrix3D(),
                    placement_matrix = placement_mat,
                    local_placement_matrix = AllplanGeo.Matrix3D()
                )

    model_elements += python_part_fs

    group_elems.append(python_part_fs)
    group_elems_preview.append(python_part_fs)

    # Create handles after update values
    handle_list = pld_element.create_handles()

    result = {
        "elements"              :  model_elements,
        "handles"               :  handle_list,
        "preview_elements"      :  model_elements,
        "group_elems"           :  group_elems,
        "group_elems_preview"   :  group_elems_preview,
        "build_ele"             :  build_ele,#build_ele_TD
        }

    return result

def set_and_update_order_inclination(inclination_rotation_angle_lado_a, inclination_rotation_angle_lado_b, inclination_rotation_angle_lado_c, inclination_rotation_angle_lado_d, rotation_inclination_order: List):
    """Set and update order inclination

    Args:
        rotation_inclination_order (List): _description_
        inclination_rotation_lados_sorted_list (List): _description_
    """

    # Lado A
    if is_valid_add_angle(rotation_inclination_order, inclination_rotation_angle_lado_a, ANGLE_A_STR):
        rotation_inclination_order.append(ANGLE_A_STR)
    # Remove lado A
    index_to_remove_from_list = validate_and_get_index_remove_angle_from_list(rotation_inclination_order, inclination_rotation_angle_lado_a, ANGLE_A_STR)
    if index_to_remove_from_list is not None:
        del rotation_inclination_order[index_to_remove_from_list]

    # Lado B
    if is_valid_add_angle(rotation_inclination_order, inclination_rotation_angle_lado_b, ANGLE_B_STR):
        rotation_inclination_order.append(ANGLE_B_STR)
    # Remove lado B
    index_to_remove_from_list = validate_and_get_index_remove_angle_from_list(rotation_inclination_order, inclination_rotation_angle_lado_b, ANGLE_B_STR)
    if index_to_remove_from_list is not None:
        del rotation_inclination_order[index_to_remove_from_list]

    # Lado C
    if is_valid_add_angle(rotation_inclination_order, inclination_rotation_angle_lado_c, ANGLE_C_STR):
        rotation_inclination_order.append(ANGLE_C_STR)
    # Remove lado C
    index_to_remove_from_list = validate_and_get_index_remove_angle_from_list(rotation_inclination_order, inclination_rotation_angle_lado_c, ANGLE_C_STR)
    if index_to_remove_from_list is not None:
        del rotation_inclination_order[index_to_remove_from_list]

    # Lado D
    if is_valid_add_angle(rotation_inclination_order, inclination_rotation_angle_lado_d, ANGLE_D_STR):
        rotation_inclination_order.append(ANGLE_D_STR)
    # Remove lado D
    index_to_remove_from_list = validate_and_get_index_remove_angle_from_list(rotation_inclination_order, inclination_rotation_angle_lado_d, ANGLE_D_STR)
    if index_to_remove_from_list is not None:
        del rotation_inclination_order[index_to_remove_from_list]

    inclination_rotation_list_input = [
        (angle_str,
        inclination_rotation_angle_lado_a if angle_str == ANGLE_A_STR else
        inclination_rotation_angle_lado_b if angle_str == ANGLE_B_STR else
        inclination_rotation_angle_lado_c if angle_str == ANGLE_C_STR else
        inclination_rotation_angle_lado_d if angle_str == ANGLE_D_STR else
        None)
        for angle_str in rotation_inclination_order
    ]

    return inclination_rotation_list_input



    # [(ANGLE_A_STR, inclination_rotation_angle_lado_a), (ANGLE_B_STR, inclination_rotation_angle_lado_b),
    #                              (ANGLE_C_STR, inclination_rotation_angle_lado_c), (ANGLE_D_STR, inclination_rotation_angle_lado_d)]

    # list_to_update_to_initial = [item for item in initial_order_rotation_inclination_list if item not in rotation_inclination_order]

    # Update lados list that move to initial position
    # for item in list_to_update_to_initial:
    #     if item == ANGLE_A_STR:
    #         self.inclination_rotation_lados_update_to_initial.append(self.line_lado_a_pld)
    #     if item == ANGLE_B_STR:
    #         self.inclination_rotation_lados_update_to_initial.append(self.line_lado_b_pld)
    #     if item == ANGLE_C_STR:
    #         self.inclination_rotation_lados_update_to_initial.append(self.line_lado_c_pld)
    #     if item == ANGLE_D_STR:
    #         self.inclination_rotation_lados_update_to_initial.append(self.line_lado_d_pld)

def is_valid_add_angle(rotation_inclination_order, angle, angle_str):
    """Check if is valid angle

    Args:
        rotation_inclination_order (_type_): _description_
        angle (_type_): _description_
        angle_str (_type_): _description_

    Returns:
        _type_: _description_
    """
    if angle_str not in rotation_inclination_order:
        if angle is not None and angle > 0:
            return True
    return False

def validate_and_get_index_remove_angle_from_list(rotation_inclination_order: List, angle, angle_str):
    """Check and gei index to remove

    Args:
        rotation_inclination_order (List): _description_
        angle (_type_): _description_
        angle_str (_type_): _description_

    Returns:
        _type_: _description_
    """
    if angle_str in rotation_inclination_order:
        if angle is None or angle == 0 and rotation_inclination_order:
            return rotation_inclination_order.index(angle_str)
            #return True
    #return False
    return None

def create_element(build_ele, doc):
    """Create element

    Args:
        build_ele (_type_): _description_
        doc (_type_): _description_

    Returns:
        _type_: _description_
    """
    result = create_element_class(build_ele, doc)
    #model_elem_list = result["model_elem_list"]
    model_elem_list = result["elements"]
    handle_list = result["handles"]
    model_elem_list_preview = result["preview_elements"]
    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview)

class FS():
    """Define FS class
    """

    def __init__(self, build_ele, doc, placement_mat = AllplanGeo.Matrix3D(), ancho_pld=None, alto_pld=None,
                 grosor_pld=None, grosor_xps=None, z_rotation: float|None = None, cavidades_list: List[AllplanGeo.Polyhedron3D] = [], cortes_zona_list: List[AllplanGeo.Polyhedron3D] = [],
                 fs_type:  int|None = None, inclination_list: list[tuple[str, float]]|None = None, name: str|None = None, largo_fs= None, ancho_fs= None, grosor_fs= None,
                 borde_afilado_selector: int|None = None):
                 #initial_position_point_fs: AllplanGeo.Point3D|None = None, borde_afilado_selector: int|None = None):
        """Initialize values

        Args:
            build_ele (_type_): _description_
            doc (_type_): _description_
            placement_mat (_type_, optional): _description_. Defaults to AllplanGeo.Matrix3D().
            ancho_pld (_type_, optional): _description_. Defaults to None.
            alto_pld (_type_, optional): _description_. Defaults to None.
            grosor_pld (_type_, optional): _description_. Defaults to None.
            inclination_rotation_angle_lado_a (int | None, optional): _description_. Defaults to None.
        """

        self.build_fs = build_ele
        self._doc = doc

        self.placement_mat = placement_mat
        self.cavidades_polynhedron3d_list = []
        # Define positions
        self.position_pld = AllplanGeo.Vector3D(placement_mat[12],
                                                placement_mat[13],
                                                placement_mat[14])
        self.position_xps = AllplanGeo.Vector3D(placement_mat[12] + 2,
                                                placement_mat[13] + 2,
                                                placement_mat[14] + 15)

        # Create cavidades manuales
        # Options create figure
        self.create_cavidades_manuales = False
        self.create_rectangular_cuboid_value = 1
        self.create_cylinder_value = 2
        # Rotation inclination
        # default values
        self.default_alto_pld = 3000 # borde largo - length (interpolables)
        self.defaul_ancho_pld = 1200 # borde corto - weidth (interpolables)
        self.default_grosor_pld = 15 # grosor o espesos - height
        self.default_grosor_xps = 40
        self.default_z_rotation = 0

        # Set values
        self.ancho_pld = ancho_pld if ancho_pld else self.defaul_ancho_pld
        self.alto_pld = alto_pld if alto_pld else self.default_alto_pld
        self.grosor_pld = grosor_pld if grosor_pld else self.default_grosor_pld
        self.grosor_xps = grosor_xps if grosor_xps else self.default_grosor_xps
        self.z_rotation = z_rotation if z_rotation else self.default_z_rotation

        self.inclination_manager = InclinationManager(self.ancho_pld, self.alto_pld, self.grosor_pld)

        # FS values
        self.name = name
        self.largo_fs = largo_fs
        self.ancho_fs = ancho_fs
        self.grosor_fs = grosor_fs
        self.fs_type = fs_type
        # Borde afilado selector
        self.borde_afilado_selector = borde_afilado_selector

        # Initial inclination lados
        self.initial_inclinacion_rotacion_lado_a_pld = None
        self.initial_inclinacion_rotacion_lado_b_pld = None
        self.initial_inclinacion_rotacion_lado_c_pld = None
        self.initial_inclinacion_rotacion_lado_d_pld = None
        #self.inital_position_point_fs = initial_position_point_fs
        self.handle_points_cuboid = None

        # Inclination lados
        self.inclination_list = inclination_list
        # Lado A
        self.inclinacion_rotacion_lado_a_pld = None
        self.inclinacion_rotacion_lado_a_xps = None
        # Lado B
        self.inclinacion_rotacion_lado_b_pld = None
        self.inclinacion_rotacion_lado_b_xps = None
        # Lado C
        self.inclinacion_rotacion_lado_c_pld = None
        self.inclinacion_rotacion_lado_c_xps = None
        # Lado D
        self.inclinacion_rotacion_lado_d_pld = None
        self.inclinacion_rotacion_lado_d_xps = None


        self.default_desfasado_xps_respect_to_pld = 2
        # lines inclination
        # Lado A
        self.line_lado_a_pld = AllplanGeo.Line3D()
        self.line_lado_a_xps = AllplanGeo.Line3D()
        # Lado B
        self.line_lado_b_pld = AllplanGeo.Line3D()
        self.line_lado_b_xps = AllplanGeo.Line3D()
        # Lado C
        self.line_lado_c_pld = AllplanGeo.Line3D()
        self.line_lado_c_xps = AllplanGeo.Line3D()
        # Lado D
        self.line_lado_d_pld = AllplanGeo.Line3D()
        self.line_lado_d_xps = AllplanGeo.Line3D()

        self.initial_order_rotation_inclination_list = ["A", "B", "C", "D"]
        self.inclination_rotation_lados_update_to_initial = []

        # Initial position
        self.index_placement_x = 12
        self.index_placement_y = 13
        self.index_placement_z = 14

        # Cavidades values
        self.cavidades_list = cavidades_list

        # Cortes de zona
        self.cortes_zona_list = cortes_zona_list

    # Cavidades manuales
    # Create cuboid
    def create_cuboid(self, ancho, alto, grosor):
        """Create cuboid cavidad manual

        Args:
            ancho (_type_): _description_
            alto (_type_): _description_
            grosor (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = ancho,
            width     = alto,
            height    = grosor
        )

        return cuboid

    # Cavidades manuales
    # Create cylinder
    def create_cylinder(self, diametro):
        """Create cylinder cavidad manual

        Args:
            diametro (_type_): _description_

        Returns:
            _type_: _description_
        """
        radius_major = diametro/2
        radius_minor = diametro/2
        cylinder = AllplanGeo.Cylinder3D(
            refPlacement=   AllplanGeo.AxisPlacement3D(),
            radiusMajor=    radius_major,
            radiusMinor=    radius_minor,
            apex=           AllplanGeo.Point3D(0, 0, 1000)
        )
        return cylinder

    # Rotate cuboid
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

    def set_placement_values(self):
        # Set values placement
        #if self.inital_position_point_fs:
        #    self.placement_mat.SetValue(self.index_placement_x, self.inital_position_point_fs.X)
        #    self.placement_mat.SetValue(self.index_placement_y, self.inital_position_point_fs.Y)
        #    self.placement_mat.SetValue(self.index_placement_z, self.inital_position_point_fs.Z)
        if self.placement_mat:
            self.placement_mat.SetValue(self.index_placement_x, self.placement_mat[12])
            self.placement_mat.SetValue(self.index_placement_y, self.placement_mat[13])
            self.placement_mat.SetValue(self.index_placement_z, self.placement_mat[14])

    def get_initial_position_from_placement(self):
        # Get values placement
        #if self.inital_position_point_fs:
        if self.placement_mat:
            _x = self.placement_mat[self.index_placement_x]
            _y = self.placement_mat[self.index_placement_y]
            _z = self.placement_mat[self.index_placement_z]
            return AllplanGeo.Vector3D(_x, _y, _z)

        return None

    def set_and_get_initial_position_from_placement(self):
        self.set_placement_values()
        initial_position = self.get_initial_position_from_placement()
        return initial_position

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

    # def create_reference_cuboid_pld(self):
    #     """_summary_

    #     Returns:
    #         _type_: _description_
    #     """
    #     # Create cuboid
    #     cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
    #         placement = AllplanGeo.AxisPlacement3D(),
    #         length    = self.ancho_pld,
    #         width     = self.alto_pld,
    #         height    = self.grosor_pld
    #     )

    #     return cuboid

    # def initial_inclination_lado_a(self, reference_cuboid):
    #     """Initial inclination lado A

    #     Args:
    #         reference_cuboid (_type_): _description_
    #     """
    #     #reference_cuboid = self.create_reference_cuboid_pld()
    #     lines_inclination_lado_a = self.get_lines_inclination_pld_xps_lado_a(reference_cuboid)[0]
    #     # Angle
    #     angle = AllplanGeo.Angle()
    #     angle.SetDeg(0)

    #     # Update initial inclinacion rotation lado A
    #     self.initial_inclinacion_rotacion_lado_a_pld = (lines_inclination_lado_a, angle)

    # def initial_inclination_lado_b(self, reference_cuboid):
    #     """Initial inclination lado B

    #     Args:
    #         reference_cuboid (_type_): _description_
    #     """
    #     lines_inclination_lado_b = self.get_lines_inclination_pld_xps_lado_b(reference_cuboid)[0]
    #     # Angle
    #     angle = AllplanGeo.Angle()
    #     angle.SetDeg(0)

    #     # Update initial inclinacion rotation lado A
    #     self.initial_inclinacion_rotacion_lado_b_pld = (lines_inclination_lado_b, angle)

    # def initial_inclination_lado_c(self, reference_cuboid):
    #     """Initial inclination lado C

    #     Args:
    #         reference_cuboid (_type_): _description_
    #     """
    #     lines_inclination_lado_c = self.get_lines_inclination_pld_xps_lado_c(reference_cuboid)[0]
    #     # Angle
    #     angle = AllplanGeo.Angle()
    #     angle.SetDeg(0)

    #     # Update initial inclinacion rotation lado A
    #     self.initial_inclinacion_rotacion_lado_c_pld = (lines_inclination_lado_c, angle)

    # def initial_inclination_lado_d(self, reference_cuboid):
    #     """Initial inclination lado D

    #     Args:
    #         reference_cuboid (_type_): _description_
    #     """
    #     lines_inclination_lado_d = self.get_lines_inclination_pld_xps_lado_d(reference_cuboid)[0]
    #     # Angle
    #     angle = AllplanGeo.Angle()
    #     angle.SetDeg(0)

    #     # Update initial inclinacion rotation lado A
    #     self.initial_inclinacion_rotacion_lado_d_pld = (lines_inclination_lado_d, angle)

    # def get_lines_inclination_pld_xps_lado_a(self, geometry_object: AllplanGeo.Polyhedron3D):
    #     """Get lines inclination lado A PLD XPS

    #     Args:
    #         geometry_object (AllplanGeo.Polyhedron3D): _description_

    #     Returns:
    #         _type_: _description_
    #     """
    #     vertices_cuboid = geometry_object.GetVertices()
    #     # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

    #     # Lado A PLD
    #     # Using points 3D
    #     # initial coords PLD
    #     initial_vertice_index_lado_a_pld = 4
    #     initial_coords_lado_a_pld = vertices_cuboid[initial_vertice_index_lado_a_pld].GetCoords()
    #     initial_coords_point_3d_lado_a_pld = AllplanGeo.Point3D(initial_coords_lado_a_pld[0], initial_coords_lado_a_pld[1], initial_coords_lado_a_pld[2])
    #     # final coords PLD
    #     final_vertice_index_lado_a_pld = 7
    #     final_coords_lado_a_pld = vertices_cuboid[final_vertice_index_lado_a_pld].GetCoords()
    #     final_coords_point_3d_lado_a_pld = AllplanGeo.Point3D(final_coords_lado_a_pld[0], final_coords_lado_a_pld[1], final_coords_lado_a_pld[2])
    #     line_lado_a_pld = AllplanGeo.Line3D(initial_coords_point_3d_lado_a_pld, final_coords_point_3d_lado_a_pld)
    #     # Set line lado A XPS
    #     line_lado_a_xps = line_lado_a_pld

    #     # Update lines lado A
    #     self.line_lado_a_pld = line_lado_a_pld
    #     self.line_lado_a_xps = line_lado_a_xps

    #     return line_lado_a_pld, line_lado_a_xps

    # def get_lines_inclination_pld_xps_lado_b(self, geometry_object: AllplanGeo.Polyhedron3D):
    #     vertices_cuboid = geometry_object.GetVertices()
    #     # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

    #     # Lado B PLD
    #     # Using points 3D
    #     # initial coords PLD
    #     initial_vertice_index_lado_b_pld = 5
    #     initial_coords_lado_b_pld = vertices_cuboid[initial_vertice_index_lado_b_pld].GetCoords()
    #     initial_coords_point_3d_lado_b_pld = AllplanGeo.Point3D(initial_coords_lado_b_pld[0], initial_coords_lado_b_pld[1], initial_coords_lado_b_pld[2])
    #     # final coords PLD
    #     final_vertice_index_lado_b_pld = 6
    #     final_coords_lado_b_pld = vertices_cuboid[final_vertice_index_lado_b_pld].GetCoords()
    #     final_coords_point_3d_lado_b_pld = AllplanGeo.Point3D(final_coords_lado_b_pld[0], final_coords_lado_b_pld[1], final_coords_lado_b_pld[2])
    #     line_lado_b_pld = AllplanGeo.Line3D(initial_coords_point_3d_lado_b_pld, final_coords_point_3d_lado_b_pld)
    #     # Set line lado B XPS
    #     line_lado_b_xps = line_lado_b_pld

    #     # Update lines lado B
    #     self.line_lado_b_pld = line_lado_b_pld
    #     self.line_lado_b_xps = line_lado_b_xps

    #     return line_lado_b_pld, line_lado_b_xps

    # def get_lines_inclination_pld_xps_lado_c(self, geometry_object: AllplanGeo.Polyhedron3D):
    #     vertices_cuboid = geometry_object.GetVertices()
    #     # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

    #     # Lado C PLD
    #     # Using points 3D
    #     # initial coords PLD
    #     initial_vertice_index_lado_c_pld = 4
    #     initial_coords_lado_c_pld = vertices_cuboid[initial_vertice_index_lado_c_pld].GetCoords()
    #     initial_coords_point_3d_lado_c_pld = AllplanGeo.Point3D(initial_coords_lado_c_pld[0], initial_coords_lado_c_pld[1], initial_coords_lado_c_pld[2])
    #     # final coords PLD
    #     final_vertice_index_lado_c_pld = 5
    #     final_coords_lado_c_pld = vertices_cuboid[final_vertice_index_lado_c_pld].GetCoords()
    #     final_coords_point_3d_lado_c_pld = AllplanGeo.Point3D(final_coords_lado_c_pld[0], final_coords_lado_c_pld[1], final_coords_lado_c_pld[2])
    #     line_lado_c_pld = AllplanGeo.Line3D(initial_coords_point_3d_lado_c_pld, final_coords_point_3d_lado_c_pld)

    #     # Set line lado C XPS
    #     line_lado_c_xps = line_lado_c_pld

    #     # Update lines lado C
    #     self.line_lado_c_pld = line_lado_c_pld
    #     self.line_lado_c_xps = line_lado_c_xps

    #     return line_lado_c_pld, line_lado_c_xps

    # def get_lines_inclination_pld_xps_lado_d(self, geometry_object: AllplanGeo.Polyhedron3D):
    #     vertices_cuboid = geometry_object.GetVertices()
    #     # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

    #     # Lado D PLD
    #     # Using points 3D
    #     # initial coords PLD
    #     initial_vertice_index_lado_d_pld = 7
    #     initial_coords_lado_d_pld = vertices_cuboid[initial_vertice_index_lado_d_pld].GetCoords()
    #     initial_coords_point_3d_lado_d_pld = AllplanGeo.Point3D(initial_coords_lado_d_pld[0], initial_coords_lado_d_pld[1], initial_coords_lado_d_pld[2])
    #     # final coords PLD
    #     final_vertice_index_lado_d_pld = 6
    #     final_coords_lado_d_pld = vertices_cuboid[final_vertice_index_lado_d_pld].GetCoords()
    #     final_coords_point_3d_lado_d_pld = AllplanGeo.Point3D(final_coords_lado_d_pld[0], final_coords_lado_d_pld[1], final_coords_lado_d_pld[2])
    #     line_lado_d_pld = AllplanGeo.Line3D(initial_coords_point_3d_lado_d_pld, final_coords_point_3d_lado_d_pld)

    #     # Set line lado D XPS
    #     line_lado_d_xps = line_lado_d_pld

    #     # Update lines lado D
    #     self.line_lado_d_pld = line_lado_d_pld
    #     self.line_lado_d_xps = line_lado_d_xps

    #     return line_lado_d_pld, line_lado_d_xps


    # def get_lines_lado_cuboid(self, geometry_object: AllplanGeo.Polyhedron3D, initial_index_lado: int, final_index_lado: int):
    #     vertices_cuboid = geometry_object.GetVertices()
    #     # error_code, lines3d_list = reference_cuboid.GetEdgesLines()

    #     # Lado geometry object
    #     # Using points 3D
    #     # Initial coords
    #     initial_vertice_index_lado = initial_index_lado
    #     initial_coords_lado = vertices_cuboid[initial_vertice_index_lado].GetCoords()
    #     initial_coords_point_3d_lado = AllplanGeo.Point3D(initial_coords_lado[0], initial_coords_lado[1], initial_coords_lado[2])

    #     # Final coords
    #     final_vertice_index_lado = final_index_lado
    #     final_coords_lado = vertices_cuboid[final_vertice_index_lado].GetCoords()
    #     final_coords_point_3d_lado = AllplanGeo.Point3D(final_coords_lado[0], final_coords_lado[1], final_coords_lado[2])

    #     line_3d_lado = AllplanGeo.Line3D(initial_coords_point_3d_lado, final_coords_point_3d_lado)
    #     #vector_3d_lado = AllplanGeo.Vector3D(final_coords_point_3d_lado.X, final_coords_point_3d_lado.Y,  final_coords_point_3d_lado.Z)

    #     return line_3d_lado

    # def get_handle_point_from_line_cuboid(self, line_cuboid: AllplanGeo.Line3D, initial: bool = False):
    #     """_summary_

    #     Args:
    #         cuboid (_type_): _description_
    #         vertice_index (_type_): _description_

    #     Returns:
    #         _type_: _description_
    #     """
    #     coords = line_cuboid.GetCoords()
    #     if initial:
    #         coords_line_inclinated = AllplanGeo.Point3D(coords[0], coords[1], coords[2])
    #     else:
    #         coords_line_inclinated = AllplanGeo.Point3D(coords[3], coords[4], coords[5])
    #     return coords_line_inclinated

    # def set_and_get_handle_points(self, reference_cuboid: AllplanGeo.Polyhedron3D):
    #     # Get lines cuboid PLD
    #     # Lado A
    #     initial_index = 4
    #     final_index = 7
    #     line_lado_a = self.get_lines_lado_cuboid(reference_cuboid, initial_index, final_index)
    #     # Lado C
    #     initial_index = 4
    #     final_index = 5
    #     line_lado_c = self.get_lines_lado_cuboid(reference_cuboid, initial_index, final_index)

    #     first_handle_point_cuboid = self.get_handle_point_from_line_cuboid(line_lado_a)
    #     second_handle_point_cuboid = self.get_handle_point_from_line_cuboid(line_lado_c)

    #     return first_handle_point_cuboid, second_handle_point_cuboid

    def is_valid_add_angle(self, rotation_inclination_order, angle, angle_str):
        """Check if is valid angle

        Args:
            rotation_inclination_order (_type_): _description_
            angle (_type_): _description_
            angle_str (_type_): _description_

        Returns:
            _type_: _description_
        """
        if angle_str not in rotation_inclination_order:
            if angle is not None and angle > 0:
                return True
        return False

    def add_cavidades_manuales(self, build_ele: BuildingElement):
        """_summary_

        Args:
            build_ele (BuildingElement): _description_
        """
        # Update cavidades manuales flag
        self.create_cavidades_manuales = True
        # Get selector value
        selector_figure_value = build_ele.SelectorFigura.value

        if selector_figure_value == self.create_rectangular_cuboid_value:
            ancho_cuboid = build_ele.AnchoCavidadCuboid.value
            alto_cuboid = build_ele.LargoCavidadCuboid.value
            espesor_cuboid = build_ele.EspesorCavidadCuboid.value

            # Create cuboid cavidad
            cavidad_cuboid = self.create_cuboid(ancho_cuboid, alto_cuboid, espesor_cuboid)
            self.cavidades_polynhedron3d_list.append(cavidad_cuboid)

        if selector_figure_value == self.create_cylinder_value:
            diametro_cylinder = build_ele.DiametroCavidadCylinder.value

            # Create cylinder cavidad
            cavidad_cylinder = self.create_cylinder(diametro_cylinder)
            # Create polyhedron from cylinder
            error_code , polyhedron_cylinder = AllplanGeo.CreatePolyhedron(cavidad_cylinder, 36)
            if error_code == AllplanGeo.eGeometryErrorCode.eOK:
                self.cavidades_polynhedron3d_list.append(polyhedron_cylinder)
            else:
                print("Error convert cylinder 3d to Polyhedron")

    def update_offset_polyhedron3d(self, geo_item, offset_cavidad):
        # TODO: offset
        return geo_item


    def update_polygon3d_list(self, geo_item):
        """_summary_

        Args:
            geo_item (_type_): _description_
        """
        offset_cavidad = 2
        is_polyhedron_3d = isinstance(geo_item, AllplanGeo.Polyhedron3D)
        is_brep_3d =  isinstance(geo_item, AllplanGeo.BRep3D)
        if is_polyhedron_3d:
            # Aumentar offset
            #geo_item.le
            polyhedron_result = self.update_offset_polyhedron3d(geo_item, offset_cavidad)
            self.cavidades_polynhedron3d_list.append(polyhedron_result)
        if is_brep_3d:
            brep_settings = AllplanGeo.ApproximationSettings()
            brep_settings.SetBRepTesselation(
                density=1,
                maxAngle=AllplanGeo.Angle(),
                minLength=0,
                maxLength=0,
            )
            create_result = AllplanGeo.CreatePolyhedron(
                geo_item, brep_settings
            )
            if create_result[0] == AllplanGeo.eGeometryErrorCode.eOK:
                created_polyhedron = create_result[1]
                polyhedron_result = self.update_offset_polyhedron3d(created_polyhedron, offset_cavidad)
                self.cavidades_polynhedron3d_list.append(polyhedron_result)

    def get_and_make_cavidades_from_list(self, list_geo: AllplanEleAdapter.BaseElementAdapterList):
        """_summary_

        Args:
            list_geo (AllplanEleAdapter.BaseElementAdapterList): _description_
        """
        for i, item_list in enumerate(list_geo):
            _type = item_list.GetElementAdapterType()

            geo_model = item_list.GetModelGeometry()

            if isinstance(geo_model, List):
                if len(geo_model) == 1:
                    geo_item = geo_model[0]
                    self.update_polygon3d_list(geo_item)
                else:
                    print(geo_model)
            else:
                self.update_polygon3d_list(geo_model)

    def set_and_get_preview_symbols(self):
        """Set and get preview symbols

        Returns:
            _type_: _description_
        """

        return self.inclination_manager.get_preview_symbols()

    def create(self):
        """Create FS

        Returns:
            _type_: _description_
        """

        result = create_element_class(self.build_fs , self._doc, self.placement_mat, self.cavidades_polynhedron3d_list, self.create_cavidades_manuales, test=True, inclinaciones_rotacion = self.inclination_list)

        # model_elem_list = result["elements"]
        # handle_list = result["handles"]
        # model_elem_list_preview = result["preview_elements"]
        # group_elems = result["group_elems"]
        # group_elems_preview = result["group_elems_preview"]

        #result = {
        #    "elements"              :  model_elem_list,
        #    "handles"               :  handle_list,
        #    "preview_elements"      :  model_elem_list_preview,
        #    "group_elems"           :  group_elems,
        #    "group_elems_preview"   :  group_elems_preview}

        result = {
            "elements"              :  result["elements"],#model_elem_list,
            "handles"               :  result["handles"],#handle_list,
            "preview_elements"      :  result["preview_elements"],# model_elem_list_preview,
            "group_elems"           :  result["group_elems"],#group_elems,
            "group_elems_preview"   :  result["group_elems_preview"],#group_elems_preview,
            "build_ele"             :  result["build_ele"],#build_ele_TD
            }

        return result