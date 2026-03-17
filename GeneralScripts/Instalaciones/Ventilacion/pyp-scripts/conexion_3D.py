from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class ConexionObject3D:
    def __init__(self):
        self.geo_tools = CreateSmartGeo()

    def create_conexion_geometry_3D(self) -> ModelEleList:
        COLOR_1 = 12 # naranja
        L_CUBO_1 = 46
        W_CUBO_1 = 161

        conexion_desc  = {
            "bases": [
                {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1,"height": W_CUBO_1, "base_point": (0, 0, 0), "color": COLOR_1, "operations": []},
            ]}
        model_ele_list = self.geo_tools.build_from_description(conexion_desc)
        return model_ele_list
