from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class MenguitoObject3D:
    def __init__(self):
        self.geo_tools = CreateSmartGeo()

    def create_manguito_geometry_3D(self) -> ModelEleList:
        COLOR_1 = 70 # green
        COLOR_2 = 6 # red

        # --- Parámetros manguito ---
        L_CUBO_1 = 110
        W_CUBO_1 = 80
        L_CUBO_2 = 22
        W_CUBO_2 = 84

        manguito_desc  = {
            # Cilindro base
            "bases": [
                {"type": "cubo", "length": L_CUBO_1, "width": W_CUBO_1,"height": W_CUBO_1, "base_point": (0, 0, 0), "color": COLOR_1, "operations": []},
                {"type": "cubo", "length": L_CUBO_2, "width": W_CUBO_2,"height": W_CUBO_2, "base_point": (6, -2, -2), "color": COLOR_2, "operations": []},
                {"type": "cubo", "length": L_CUBO_2, "width": W_CUBO_2,"height": W_CUBO_2, "base_point": (82, -2, -2), "color": COLOR_2, "operations": []},
            ]}
        model_ele_list = self.geo_tools.build_from_description(manguito_desc)
        return model_ele_list


    #------------------------------------------------ CODIGO ALLPLAN ------------------------------------------------
    # --- Crear geometría 3D ---
    # base_point_cubo = AllplanGeometry.Point3D(0, 0, 0)
    # prop, base_cubo = self.geo_tools._create_cubo(length=L_CUBO_1, width=W_CUBO_1, height=W_CUBO_1, base_point=base_point_cubo, color_index=COLOR_1)
    # self.model_ele_list.append(AllplanBasisElements.ModelElement3D(prop, base_cubo))

    # base_point_cubo_1 = AllplanGeometry.Point3D(6,  0, 0)
    # prop1, cubo_1 = self.geo_tools._create_cubo(length=L_CUBO_2, width=W_CUBO_2, height=W_CUBO_2, base_point=base_point_cubo_1, color_index=COLOR_2)

    # self.model_ele_list.append(AllplanBasisElements.ModelElement3D(prop1, cubo_1))

    # base_point_cubo_2 = AllplanGeometry.Point3D(82,  0, 0)
    # prop2, cubo_2 = self.geo_tools._create_cubo(length=L_CUBO_2, width=W_CUBO_2, height=W_CUBO_2, base_point=base_point_cubo_2, color_index=COLOR_2)
