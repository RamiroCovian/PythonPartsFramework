import NemAll_Python_Geometry as AllplanGeometry

from TypeCollections.ModelEleList import ModelEleList
from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


# ----- Params  Difusor 3D -----
COLOR_1 = 70
COLOR_2 = 10

R_CYL_BIG = 125.0
H_CYL_BIG = 250.0

HEIGHT_CYL = 110

R_CYL_SMALL = 75.0
H_CYL_SMALL = 50.0

L_CUBO = 135
W_CUBO = 130
H_CUBO = 65

L_FLANGE = 30
W_FLANGE = 215
H_FLANGE = 5

R_SIDE = 75.0
C_H = 60.0

R_TACO = 15  # radio
H_TACO = 15  # altura

CUBE_LENGTH = 10.0  # largo del cubo
CUBE_WIDTH = 25.0  # ancho (en Y)

ALT_CYL_CUB = H_CYL_BIG+H_CUBO

class DifusorObject3D:
    def __init__(self):
        self.geo_tools = CreateSmartGeo()

    def create_difusor_geometry_3D(self) -> ModelEleList:
        x_vector_small = AllplanGeometry.Vector3D(0, 0, 1)
        z_vector_small = AllplanGeometry.Vector3D(1, 0, 0)

        difusor_desc = {
            # Cilindro base
            "bases": [
                {"type": "cylinder", "radius": R_CYL_BIG, "height": H_CYL_BIG, "color": COLOR_1,
                "operations": [
                    # Cubo
                    {"action": "union", "shape": {
                        "type": "cubo", "length": L_CUBO, "width": W_CUBO, "height": H_CUBO, "base_point": (-L_CUBO / 2,  -L_CUBO / 2, H_CYL_BIG), "color": COLOR_1
                    }},

                    # Cylinder 1
                    {"action": "union", "shape":
                    {"type": "cylinder", "radius": R_CYL_SMALL, "height": H_CYL_SMALL, "base_point": (67, R_SIDE / 2, H_CYL_BIG + C_H / 2),
                    "color": COLOR_1, "x_axis": x_vector_small,  "direction": z_vector_small, "rotation": 90}},

                    # Cylinder 2
                    {"action": "union", "shape":
                    {"type": "cylinder", "radius": R_CYL_SMALL, "height": H_CYL_SMALL, "base_point": (67, -R_SIDE / 2, H_CYL_BIG + C_H / 2),
                    "color": COLOR_1, "x_axis": x_vector_small,  "direction": z_vector_small, "rotation": 90}},

                    # Plancha lisa
                    {"action": "union", "shape": {
                        "type": "cubo", "length": L_FLANGE, "width": W_FLANGE, "height": H_FLANGE,
                        "base_point": (L_FLANGE,  - W_FLANGE / 2, H_CYL_BIG+H_CUBO), "color": COLOR_1
                    }},

                    # Orifio 1
                    {"action": "subtract", "shape":
                    {"type": "cubo", "length": CUBE_LENGTH, "width": CUBE_WIDTH, "height": HEIGHT_CYL, "base_point": (41 , -HEIGHT_CYL, ALT_CYL_CUB), "color": COLOR_1}},

                    {"action": "subtract", "shape":
                    {"type": "cylinder", "radius": CUBE_LENGTH, "height": HEIGHT_CYL, "base_point": (46, -85, ALT_CYL_CUB), "color": COLOR_1}},

                    # Orifio 2
                    {"action": "subtract", "shape":
                    {"type": "cubo", "length": CUBE_LENGTH, "width": CUBE_WIDTH, "height": HEIGHT_CYL, "base_point": (41 , 85, ALT_CYL_CUB), "color": COLOR_1}},

                    {"action": "subtract", "shape":
                    {"type": "cylinder", "radius": CUBE_LENGTH, "height": HEIGHT_CYL, "base_point": (46, 85, ALT_CYL_CUB), "color": COLOR_1}},

                    {"action": "subtract", "shape":
                    {"type": "cylinder", "radius": CUBE_LENGTH, "height": HEIGHT_CYL, "base_point": (46, 85, ALT_CYL_CUB), "color": COLOR_1}},
                ]},

                # Cylinder 1
                {"type": "cylinder", "radius": R_TACO, "height": H_TACO, "base_point": (47, 90, 325), "color": COLOR_2},

                # Cylinder 2
                {"type": "cylinder", "radius": R_TACO, "height": H_TACO, "base_point": (47, -90, 325), "color": COLOR_2},
            ]
        }

        elements = self.geo_tools.build_from_description(difusor_desc)
        return elements



    #------------------------------------------------ CODIGO ALLPLAN ------------------------------------------------

        # self.model_ele_list = []
        # self.common_prop = AllplanGlobalSettings.AllplanGlobalSettings.GetCurrentCommonProperties()

        # --- Crear geometría 3D ---
    #     cylinder_big = self.geo_tools._create_cylinder(
    #         radius=R_CYL_BIG,  # Radio
    #         height=H_CYL_BIG,  # Altura
    #         base_point=AllplanGeometry.Point3D(0, 0, 0),
    #         # color_index=COLOR_1,
    #     )
    #     # elements.append(cylinder_big[1])
    #     self.common_prop.Color = COLOR_1
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, cylinder_big))

    #     base_small = AllplanGeometry.Point3D(67, R_SIDE / 2, H_CYL_BIG + C_H / 2)
    #     x_vector_small = AllplanGeometry.Vector3D(0, 0, 1)
    #     z_vector_small = AllplanGeometry.Vector3D(1, 0, 0)

    #     cylinder_small_1 = self.geo_tools._create_cylinder(
    #         radius=R_CYL_SMALL,
    #         height=H_CYL_SMALL,
    #         base_point=base_small,
    #         aux_x_axis=x_vector_small,
    #         axis_direction=z_vector_small,
    #         # color_index=COLOR_1,
    #         rotation_angle_deg=90,
    #     )
    #     # elements.append(cylinder_small_1[1])
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, cylinder_small_1))

    #     base_small_2 = AllplanGeometry.Point3D(67, -R_SIDE / 2, H_CYL_BIG + C_H / 2)
    #     cylinder_small_2 = self.geo_tools._create_cylinder(
    #         radius=R_CYL_SMALL,
    #         height=H_CYL_SMALL,
    #         base_point=base_small_2,
    #         aux_x_axis=x_vector_small,
    #         axis_direction=z_vector_small,
    #         # color_index=COLOR_1,
    #         rotation_angle_deg=90,
    #     )
    #     # elements.append(cylinder_small_2[1])
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, cylinder_small_2))

    #     base_cubo = AllplanGeometry.Point3D(-L_CUBO / 2,  -L_CUBO / 2, H_CYL_BIG)
    #     top_cubo = self.geo_tools._create_cubo(length=L_CUBO, width=W_CUBO, height=H_CUBO, base_point=base_cubo)
    #     # elements.append(top_cubo[1])

    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, top_cubo))

    #     base_flange = AllplanGeometry.Point3D(L_FLANGE,  - W_FLANGE / 2, H_CYL_BIG+H_CUBO)
    #     prop, top_flange = self._create_top_flange(
    #         length=L_FLANGE,
    #         width=W_FLANGE,
    #         height=H_FLANGE,
    #         base_point=base_flange,
    #         color_index=COLOR_1,
    #         alt_cyl_cub=H_CYL_BIG+H_CUBO
    #     )
    #     # elements.append(top_flange[1])
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(prop, top_flange))


    #     taco_1 = self.geo_tools._create_cylinder(
    #         radius=R_TACO,  # radio
    #         height=H_TACO,  # altura
    #         base_point=AllplanGeometry.Point3D(47, 90, 325),
    #         # color_index=COLOR_2,
    #     )
    #     # elements.append(taco_1[1])
    #     self.common_prop.Color = COLOR_2
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, taco_1))

    #     taco_2 = self.geo_tools._create_cylinder(
    #         radius=R_TACO,  # radio
    #         height=H_TACO,  # altura
    #         base_point=AllplanGeometry.Point3D(47, -90, 325),
    #         # color_index=COLOR_2,
    #     )
    #     # elements.append(taco_2[1])
    #     self.common_prop.Color = COLOR_2
    #     self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.common_prop, taco_2))

    #     return self.model_ele_list

    # def _create_top_flange(self, length, width, height, base_point, color_index, alt_cyl_cub):
    #     """Crea la placa fina o 'reborde' VERTICAL con una abertura semicircular en los extremos"""

    #     # --- Parámetros de dimensiones ---
    #     CUBE_LENGTH = 10.0  # largo del cubo
    #     CUBE_WIDTH = 25.0  # ancho (en Y)

    #      # --- Crear cuboide principal ---
    #     flange = self.geo_tools._create_cubo(length=length, width=width, height=height, base_point=base_point)

    #     # --- Crear cuboide derecha ---
    #     base_cubo_1 = AllplanGeometry.Point3D(41 , -110, alt_cyl_cub)
    #     cubo_1 = self.geo_tools._create_cubo(length=CUBE_LENGTH, width=CUBE_WIDTH, height=height, base_point=base_cubo_1)

    #     # --- Crear cilindro derecha ---
    #     cylinder = self.geo_tools._create_cylinder(
    #         radius=10,  # radio
    #         height=height,  # largo
    #         base_point=AllplanGeometry.Point3D(46, - 85, alt_cyl_cub),
    #     )
    #     _, cube_cylinder_1 = AllplanGeometry.MakeUnion(cubo_1, cylinder) # unir cubo + cilindro
    #     _, flange_with_hole_1 = AllplanGeometry.MakeSubtraction(flange, cube_cylinder_1) # restar en flange

    #     # --- Crear el cuboide izquirda ---
    #     base_cubo_2 = AllplanGeometry.Point3D(41 , 85, alt_cyl_cub)
    #     cubo_2 = self.geo_tools._create_cubo(length=CUBE_LENGTH, width=CUBE_WIDTH, height=height, base_point=base_cubo_2)

    #     # --- Crear cilindro izquirda ---
    #     cylinder_left = self.geo_tools._create_cylinder(
    #         radius=10,  # radio
    #         height=height,  # largo
    #         base_point=AllplanGeometry.Point3D(46, 85, alt_cyl_cub),
    #     )
    #     _, cube_cylinder_2 = AllplanGeometry.MakeUnion(cubo_2, cylinder_left) # unir cubo + cilindro
    #     _, flange_with_hole_2 = AllplanGeometry.MakeSubtraction(flange_with_hole_1, cube_cylinder_2) # restar en flange

    #     self.common_prop.Color = color_index
    #     # model_elem = AllplanBasisElements.ModelElement3D( self.common_prop, flange_with_hole_2)
    #     # self.model_ele_list.append(model_elem)

    #     return self.common_prop, flange_with_hole_2