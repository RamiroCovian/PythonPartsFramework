"""FS Common manegement file
"""
import NemAll_Python_Geometry as AllplanGeo
from Utils import TextReferencePointPosition
from PreviewSymbols import PreviewSymbols

ANGLE_A_STR = "A"
ANGLE_B_STR = "B"
ANGLE_C_STR = "C"
ANGLE_D_STR = "D"
ANGLE_Z_STR = "Z"


class InclinationManager():

    def __init__(self, ancho_ref_cuboid, alto_ref_cuboid, grosor_ref_cuboid):
        # Set values
        self.ancho_ref_cuboid = ancho_ref_cuboid
        self.alto_ref_cuboid = alto_ref_cuboid
        self.grosor_ref_cuboid = grosor_ref_cuboid

        # Lado A
        self.inclinacion_rotacion_lado_a = None
        # Lado B
        self.inclinacion_rotacion_lado_b = None
        # Lado C
        self.inclinacion_rotacion_lado_c = None
        # Lado D
        self.inclinacion_rotacion_lado_d = None
        # Lado Z
        self.inclinacion_rotacion_lado_z = None

        # lines inclination
        # Lado A
        self.eje_lado_a = AllplanGeo.Line3D()
        # Lado B
        self.eje_lado_b = AllplanGeo.Line3D()
        # Lado C
        self.eje_lado_c = AllplanGeo.Line3D()
        # Lado D
        self.eje_lado_d = AllplanGeo.Line3D()
        # Lado Z
        self.eje_lado_z = AllplanGeo.Line3D()

        # Create reference cuboid
        self.ref_cuboid = self.create_reference_cuboid()

    def create_reference_cuboid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Create cuboid
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(
            placement = AllplanGeo.AxisPlacement3D(),
            length    = self.ancho_ref_cuboid,
            width     = self.alto_ref_cuboid,
            height    = self.grosor_ref_cuboid
        )

        return cuboid

    # Start get lines inclination
    def get_eje_inclinacion(self, initial_vertice_index: int, final_vertice_index: int):
        vertices_cuboid = self.ref_cuboid.GetVertices()

        # initial coords
        initial_coords = vertices_cuboid[initial_vertice_index].GetCoords()
        initial_coords_point_3d = AllplanGeo.Point3D(initial_coords[0], initial_coords[1], initial_coords[2])
        # final coords
        final_coords = vertices_cuboid[final_vertice_index].GetCoords()
        final_coords_point_3d = AllplanGeo.Point3D(final_coords[0], final_coords[1], final_coords[2])

        return AllplanGeo.Line3D(initial_coords_point_3d, final_coords_point_3d)

    def get_eje_inclinacion_lado_a(self):
        initial_vertice_index_lado_a = 4
        final_vertice_index_lado_a = 7

        self.eje_lado_a = self.get_eje_inclinacion(initial_vertice_index_lado_a, final_vertice_index_lado_a)

        return self.eje_lado_a

    def get_eje_inclinacion_lado_b(self):
        initial_vertice_index_lado_b = 5
        final_vertice_index_lado_b = 6

        self.eje_lado_b = self.get_eje_inclinacion(initial_vertice_index_lado_b, final_vertice_index_lado_b)

        return self.eje_lado_b

    def get_eje_inclinacion_lado_c(self):
        initial_vertice_index_lado_c = 4
        final_vertice_index_lado_c = 5

        self.eje_lado_c = self.get_eje_inclinacion(initial_vertice_index_lado_c, final_vertice_index_lado_c)

        return self.eje_lado_c

    def get_eje_inclinacion_lado_d(self):
        initial_vertice_index_lado_d = 7
        final_vertice_index_lado_d = 6

        self.eje_lado_d = self.get_eje_inclinacion(initial_vertice_index_lado_d, final_vertice_index_lado_d)

        return self.eje_lado_d

    def get_eje_inclinacion_lado_z(self):
        initial_vertice_index_lado_z = 0
        final_vertice_index_lado_z = 4

        self.eje_lado_z = self.get_eje_inclinacion(initial_vertice_index_lado_z, final_vertice_index_lado_z)

        return self.eje_lado_z
    # End get lines inclination

    def get_processed_inclinations(self, inclination_list: list[tuple[str, int]]):
        """_summary_

        Args:
            inclination_rotation_list_input (list[tuple[str, int]]): _description_

        Returns:
            _type_: _description_
        """
        inclination_sorted_list = []

        for item in inclination_list:
            str_angle = str(item[0])
            angle_value = item[1]

            if str_angle == ANGLE_A_STR:
                # Update inclination lines lado A
                self.get_eje_inclinacion_lado_a()
                if angle_value:

                    # Angle
                    angle = AllplanGeo.Angle()
                    angle.SetDeg(-angle_value if angle_value != 0 else angle_value)

                    # Update inclinacion rotation lado A
                    if  self.inclinacion_rotacion_lado_a is None:
                        self.inclinacion_rotacion_lado_a = (self.eje_lado_a, angle)

                    inclination_sorted_list.append(self.inclinacion_rotacion_lado_a)

                    # Rotate reference cuboid
                    self.ref_cuboid = InclinationManager.inclinar_geometry_object(self.ref_cuboid, self.inclinacion_rotacion_lado_a)

            elif str_angle == ANGLE_B_STR:
                # Update inclination lines lado B
                self.get_eje_inclinacion_lado_b()
                if angle_value:

                    # Angle
                    angle = AllplanGeo.Angle()
                    angle.SetDeg(angle_value)

                    # Update inclinacion rotation lado B
                    if  self.inclinacion_rotacion_lado_b is None:
                        self.inclinacion_rotacion_lado_b = (self.eje_lado_b, angle)

                    inclination_sorted_list.append(self.inclinacion_rotacion_lado_b)

                    # Rotate reference cuboid
                    self.ref_cuboid = InclinationManager.inclinar_geometry_object(self.ref_cuboid, self.inclinacion_rotacion_lado_b)

            elif str_angle == ANGLE_C_STR:
                # Update inclination lines lado C
                self.get_eje_inclinacion_lado_c()
                if angle_value:

                    # Angle
                    angle = AllplanGeo.Angle()
                    angle.SetDeg(angle_value)

                    # Update inclinacion rotation lado C
                    if  self.inclinacion_rotacion_lado_c is None:
                        self.inclinacion_rotacion_lado_c = (self.eje_lado_c, angle)

                    inclination_sorted_list.append(self.inclinacion_rotacion_lado_c)

                    # Rotate reference cuboid
                    self.ref_cuboid = InclinationManager.inclinar_geometry_object(self.ref_cuboid, self.inclinacion_rotacion_lado_c)

            elif str_angle == ANGLE_D_STR:
                # Update inclination lines lado D
                self.get_eje_inclinacion_lado_d()
                if angle_value:

                    # Angle
                    angle = AllplanGeo.Angle()
                    angle.SetDeg(-angle_value if angle_value != 0 else angle_value)

                    # Update inclinacion rotation lado D
                    if  self.inclinacion_rotacion_lado_d is None:
                        self.inclinacion_rotacion_lado_d = (self.eje_lado_d, angle)

                    inclination_sorted_list.append(self.inclinacion_rotacion_lado_d)

                    # Rotate reference cuboid
                    self.ref_cuboid = InclinationManager.inclinar_geometry_object(self.ref_cuboid, self.inclinacion_rotacion_lado_d)

            elif str_angle == ANGLE_Z_STR:
                # Update inclination lines PLD XPS lado D
                self.get_eje_inclinacion_lado_z()
                if angle_value:

                    # Angle
                    angle = AllplanGeo.Angle()
                    angle.SetDeg(-angle_value if angle_value != 0 else angle_value)

                    # Update inclinacion rotation lado D
                    if  self.inclinacion_rotacion_lado_z is None:
                        self.inclinacion_rotacion_lado_z = (self.eje_lado_z, angle)

                    inclination_sorted_list.append(self.inclinacion_rotacion_lado_z)

                    # Rotate reference cuboid
                    self.ref_cuboid = InclinationManager.inclinar_geometry_object(self.ref_cuboid, self.inclinacion_rotacion_lado_z)
            else:
                continue

        # Set and get handle points cuboid
        #self.handle_points_cuboid = self.set_and_get_handle_points(reference_cuboid)

        return inclination_sorted_list

    # Start handles points
    def get_handle_point_from_line_cuboid(self, line_cuboid: AllplanGeo.Line3D, initial: bool = False):
        """Get handle point from line 3D

        Args:
            line_cuboid (AllplanGeo.Line3D): _description_
            initial (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        coords = line_cuboid.GetCoords()
        if initial:
            coords_line_inclinated = AllplanGeo.Point3D(coords[0], coords[1], coords[2])
        else:
            coords_line_inclinated = AllplanGeo.Point3D(coords[3], coords[4], coords[5])
        return coords_line_inclinated

    def get_lines_lado_cuboid(self, geometry_object: AllplanGeo.Polyhedron3D, initial_index_lado: int, final_index_lado: int):
        """Get lines lado cuboid

        Args:
            geometry_object (AllplanGeo.Polyhedron3D): _description_
            initial_index_lado (int): _description_
            final_index_lado (int): _description_

        Returns:
            _type_: _description_
        """
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

        line_3d_lado = AllplanGeo.Line3D(initial_coords_point_3d_lado, final_coords_point_3d_lado)
        #vector_3d_lado = AllplanGeo.Vector3D(final_coords_point_3d_lado.X, final_coords_point_3d_lado.Y,  final_coords_point_3d_lado.Z)

        return line_3d_lado

    def set_and_get_handle_points(self):
        """Set and get handle points

        Returns:
            _type_: _description_
        """
        # Get lines cuboid PLD
        # Lado A
        initial_index = 4
        final_index = 7
        line_lado_a = self.get_lines_lado_cuboid(self.ref_cuboid, initial_index, final_index)
        # Lado C
        initial_index = 4
        final_index = 5
        line_lado_c = self.get_lines_lado_cuboid(self.ref_cuboid, initial_index, final_index)

        first_handle_point_cuboid = self.get_handle_point_from_line_cuboid(line_lado_a)
        second_handle_point_cuboid = self.get_handle_point_from_line_cuboid(line_lado_c)

        return first_handle_point_cuboid, second_handle_point_cuboid
    # End handles points

    # Start Preview symbols
    def get_preview_symbols(self):
        preview_symbols = PreviewSymbols()

        # Default values
        default_height = 12
        default_ref_pnt_pos = TextReferencePointPosition.CENTER_RIGHT
        default_color = 1
        default_rotation_angle =  AllplanGeo.Angle()
        # Lado A
        text_lado_a = "Lado A"
        #reference_point_lado_a =  AllplanGeo.Point3D(0,1000,0)
        #reference_point_lado_a =  self.get_coords_from_line(self.line_lado_a_pld, True)
        lado_a_pld = self.eje_lado_a
        reference_point_lado_a =  self.get_coords_from_line(lado_a_pld, True)
        #reference_point_lado_a =  self.get_coords_from_line(self.line_lado_a_pld, True)
        # Lado B
        text_lado_b = "Lado B"
        #reference_point_lado_b =  AllplanGeo.Point3D(1200,100,0)
        #reference_point_lado_b =  self.get_coords_from_line(self.line_lado_b_pld, True)
        lado_b_pld = self.eje_lado_b
        reference_point_lado_b =  self.get_coords_from_line(lado_b_pld)
        #reference_point_lado_b =  self.get_coords_from_line(self.line_lado_b_pld)
        # Lado C
        text_lado_c = "Lado C"
        #reference_point_lado_c =  AllplanGeo.Point3D(700,0,0)
        #reference_point_lado_c =  self.get_coords_from_line(self.line_lado_c_pld, True)
        lado_c_pld = self.eje_lado_c
        reference_point_lado_c =  self.get_coords_from_line(lado_c_pld)
        #reference_point_lado_c =  self.get_coords_from_line(self.line_lado_c_pld)
        # Lado D
        text_lado_d = "Lado D"
        #reference_point_lado_d =  AllplanGeo.Point3D(700,3000,0)
        #reference_point_lado_d =  self.get_coords_from_line(self.line_lado_d_pld, True)
        lado_d_pld = self.eje_lado_d
        reference_point_lado_d =  self.get_coords_from_line(lado_d_pld, True)
        #reference_point_lado_d =  self.get_coords_from_line(self.line_lado_d_pld, True)
        # Lado A
        preview_symbols.add_text(
            text= text_lado_a, #texto que se muestra en la vista
            reference_point= reference_point_lado_a, #posicionNumero en relacion al (0,0) de la pythonPart
            ref_pnt_pos= default_ref_pnt_pos, #como se ajusta el texto(al cento del reference_point en este caso
            height= default_height, #tamaño de la letra (en este caso depende de lo que entra el usuiario)
            color= default_color, #color del texto
            rotation_angle= default_rotation_angle) #angulo de rotación en caso de que sea necesario

        # Lado B
        preview_symbols.add_text(
            text= text_lado_b, #texto que se muestra en la vista
            reference_point= reference_point_lado_b, #posicionNumero en relacion al (0,0) de la pythonPart
            ref_pnt_pos= default_ref_pnt_pos, #como se ajusta el texto(al cento del reference_point en este caso
            height= default_height, #tamaño de la letra (en este caso depende de lo que entra el usuiario)
            color= default_color, #color del texto
            rotation_angle= default_rotation_angle) #angulo de rotación en caso de que sea necesario

        # Lado C
        preview_symbols.add_text(
            text= text_lado_c, #texto que se muestra en la vista
            reference_point= reference_point_lado_c, #posicionNumero en relacion al (0,0) de la pythonPart
            ref_pnt_pos= default_ref_pnt_pos, #como se ajusta el texto(al cento del reference_point en este caso
            height= default_height, #tamaño de la letra (en este caso depende de lo que entra el usuiario)
            color= default_color, #color del texto
            rotation_angle= default_rotation_angle) #angulo de rotación en caso de que sea necesario

        # Lado D
        preview_symbols.add_text(
            text= text_lado_d, #texto que se muestra en la vista
            reference_point= reference_point_lado_d, #posicionNumero en relacion al (0,0) de la pythonPart
            ref_pnt_pos= default_ref_pnt_pos, #como se ajusta el texto(al cento del reference_point en este caso
            height= default_height, #tamaño de la letra (en este caso depende de lo que entra el usuiario)
            color= default_color, #color del texto
            rotation_angle= default_rotation_angle) #angulo de rotación en caso de que sea necesario

        return preview_symbols

    def get_coords_from_line(self, line: AllplanGeo.Line3D, initial: bool = False):
        """_summary_

        Args:
            cuboid (_type_): _description_
            vertice_index (_type_): _description_

        Returns:
            _type_: _description_
        """
        coords = line.GetCoords()
        if initial:
            coords_line = AllplanGeo.Point3D(coords[0], coords[1], coords[2])
        else:
            coords_line = AllplanGeo.Point3D(coords[3], coords[4], coords[5])

        return coords_line
    # End Preview symbols

    def inclinar_geometry_object(geometry_object: AllplanGeo.Polyhedron3D, eje_inclinacion):
        """Function to rotate a given cuboid

        Args:
            geometry_object (_type_): _description_
            inclination_rotation_angle (_type_): _description_

        Returns:
            _type_: _description_
        """

        if eje_inclinacion:
            default_angle = AllplanGeo.Angle()
            default_angle.SetDeg(0)
            angle = eje_inclinacion[1] if eje_inclinacion[1] else default_angle

            a_axis = eje_inclinacion[0]
            geometry_object = AllplanGeo.Rotate(geometry_object, AllplanGeo.Axis3D(a_axis), angle)

        return geometry_object
