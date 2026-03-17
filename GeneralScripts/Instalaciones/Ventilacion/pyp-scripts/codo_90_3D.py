from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class Codo90Object3D:
    def __init__(self):
        self.geo_tools = CreateSmartGeo()

    def create_codo_90_geometry_3D(self) -> ModelEleList:
        COLOR_1 = 40  # Amarillo
        COLOR_2 = 12 # naranja
        L_CUBO_1 = 45
        W_CUBO_1 = 160

        # Cubo base con corte 45 grados
        codo_90_desc = {
            "bases": [
                {"type": "cubo", "length": 300, "width": 300, "height": 160, "color": COLOR_1,
                "operations": [
                    {"action": "subtract",
                        "shape": {
                            "type": "cubo", "length": 400, "width": 400, "height": 300, "base_point": (300, 160, 0), "color": COLOR_1, "rotation": 45,
                    }},
                    {"action": "subtract", "shape":
                    {"type": "cubo", "length": 140, "width": 140, "height": 160, "base_point": (0 , 0, 0), "color": COLOR_1}},

                    {"action": "union", "shape":
                    {"type": "cubo", "length": 100, "width": 100, "height": 160, "base_point":  (150, 100, 0), "color": COLOR_1, "rotation": 45}},
                ]},

                # {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1, "height": W_CUBO_1, "base_point":  (140, 0, 0), "color": COLOR_2, "rotation": -90},
                # {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1, "height": W_CUBO_1, "base_point":  (0, 300, 0), "color": COLOR_2, "rotation": -180},
            ]
        }

        model_ele_list = self.geo_tools.build_from_description(codo_90_desc)
        return model_ele_list
