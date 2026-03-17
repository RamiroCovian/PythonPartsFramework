from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class ConductoObject3D:
    def __init__(self):
        self.geo_tools = CreateSmartGeo()

    def create_conducto_geometry_3D(self, length: float = 500, witdh: float = 75, height: float = 75, color: int = 1) -> ModelEleList:
        conexion_desc = {
            "bases": [
                {
                    "type": "cubo",
                    "length": length,
                    "width": witdh,
                    "height": height,
                    "base_point": (0, 0, 0),
                    "color": color,
                    "operations": [],
                },
            ]
        }
        model_ele_list = self.geo_tools.build_from_description(conexion_desc)
        return model_ele_list
