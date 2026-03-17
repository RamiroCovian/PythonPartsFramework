# ------------------------------------------- Codo 45 grados -------------------------------------------
COLOR_1 = 40  # Amarillo

codo_45_desc1 = {
    "bases": [
        {"type": "cubo", "length": 30, "width": 30, "height": 20, "color": COLOR_1,
        "operations": [
            {"action": "subtract", "shape":
             {"type": "cubo", "length": 22, "width": 22, "height": 20, "base_point": (30, 16, 0), "color": COLOR_1, "rotation": 45}},

            {"action": "subtract", "shape":
            {"type": "cubo", "length": 11, "width": 11, "height": 20, "base_point": (0 , 0, 0), "color": COLOR_1}},

            {"action": "union", "shape":
            {"type": "cubo", "length": 6, "width": 6, "height": 20, "base_point":  (11, 8, 0), "color": COLOR_1, "rotation": 45}},
        ]},
    ]
}

# ------------------------------------------- Soporte instalacion -------------------------------------------
COLOR_1 = 5

# --- Medidas orificios interno del soporte  ---
L_CUBO_1 = 12
W_CUBO_1 = 8
H_CUBO_1 = 3
C_RADIUS = W_CUBO_1

soporte_desc = {
    # Cubo base pequeño 1
    "bases": [{"type": "cubo", "length": 22, "width": 25, "height": 3, "color": COLOR_1,
        "operations": [
            # Dos agujeros cilíndricos 1
            {"action": "subtract", "shape": {"type": "cylinder", "radius": 5, "height": 3, "base_point": (8, 5, 0)}},
            {"action": "subtract", "shape": {"type": "cylinder", "radius": 5, "height": 3, "base_point": (8, 20, 0)}},

            # Cubo alto 1
            {"action": "union", "shape": {"type": "cubo", "length": 3, "width": 25, "height": 110, "base_point": (22, 0, 0)}},

            # Cubo largo superior
            {"action": "union", "shape": {"type": "cubo", "length": 680, "width": 25, "height": 3, "base_point": (22, 0, 110)}},

            # 13 orificios rectangulares repetidos
            {"action": "loop", "count": 13, "step": (50, 0, 0), "mode": "subtract", "shape": {
                    "base": {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1, "height": H_CUBO_1, "base_point": (55, 8.5, 110),"color": COLOR_1,
                    "operations": [
                        # 2 cilíndricos
                        {"action": "union", "shape": {"type": "cylinder", "radius": C_RADIUS, "height": H_CUBO_1, "base_point": (55, 12.5, 110)}},
                        {"action": "union", "shape": {"type": "cylinder", "radius": C_RADIUS, "height": H_CUBO_1, "base_point": (67, 12.5, 110)}},
                    ]}
            }},

            # Cubo alto 2
            {"action": "union", "shape": {"type": "cubo", "length": 3, "width": 25, "height": 110, "base_point": (699, 0, 0)}},

            # Cubo pequeño 2
            {"action": "union", "shape": {"type": "cubo", "length": 22, "width": 25, "height": 3,"base_point": (700, 0, 0)}},

            # Dos agujeros cilíndricos 2
            {"action": "subtract", "shape": {"type": "cylinder", "radius": 5, "height": 3, "base_point": (716, 5, 0), "color": COLOR_1}},
            {"action": "subtract", "shape": {"type": "cylinder", "radius": 5, "height": 3, "base_point": (716, 20, 0), "color": COLOR_1}},
        ]}
    ],
}

# ------------------------------------------- Manguito -------------------------------------------

# --- Parámetros manguito ---
COLOR_1 = 70 # green
COLOR_2 = 6 # red

L_CUBO_1 = 110
W_CUBO_1 = 80
L_CUBO_2 = 22
W_CUBO_2 = 84

manguito_desc  = {
    "bases": [
        {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1,"height": W_CUBO_1, "base_point": (0, 0, 0), "color": COLOR_1, "operations": []},
        {"type": "cubo", "length": L_CUBO_2, "width": W_CUBO_2,"height": W_CUBO_2, "base_point": (6, -2, -2), "color": COLOR_2, "operations": []},
        {"type": "cubo", "length": L_CUBO_2, "width": W_CUBO_2,"height": W_CUBO_2, "base_point": (82, -2, -2), "color": COLOR_2, "operations": []},
    ]
}

# ------------------------------------------- Difusor -------------------------------------------

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

x_vector_small = None #AllplanGeometry.Vector3D(0, 0, 1)
z_vector_small = None #AllplanGeometry.Vector3D(1, 0, 0)

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
                "type": "cubo", "length": L_FLANGE, "width": W_FLANGE, "height": H_FLANGE, "base_point": (L_FLANGE,  - W_FLANGE / 2, H_CYL_BIG+H_CUBO),
                "color": COLOR_1}},

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
        ]},

        # Cylinder 1
        {"type": "cylinder", "radius": R_TACO, "height": H_TACO, "base_point": (47, 90, 325), "color": COLOR_2},

        # Cylinder 2
        {"type": "cylinder", "radius": R_TACO, "height": H_TACO, "base_point": (47, -90, 325), "color": COLOR_2},
    ]
}