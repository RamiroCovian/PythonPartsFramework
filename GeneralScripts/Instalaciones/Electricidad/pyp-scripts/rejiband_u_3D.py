# -*- coding: utf-8 -*-
from TypeCollections.ModelEleList import ModelEleList

from Instalaciones.GeometryTools.create_smart_geo import CreateSmartGeo


class RejibandUObject3D:
    """
    Mock MVP2: Rejiband en forma de U orientada en eje X.

    Convención de ejes:
    - Largo: X
    - Ancho: Y (centrado)
    - Altura: Z
    """
    def __init__(self) -> None:
        self.geo_tools = CreateSmartGeo()

    def create_rejiband_u_geometry_3d(
        self,
        length: float = 1000.0,
        width: float = 100.0,
        height: float = 50.0,
        thickness: float = 4.0,
        color: int = 1,
    ) -> ModelEleList:
        L = float(max(length, 1.0))
        W = float(max(width, 10.0))
        H = float(max(height, thickness + 1.0))
        t = float(max(thickness, 1.0))

        # Clamp thickness to avoid degeneracy
        if t * 2.0 > W:
            t = max(1.0, W * 0.2)

        # Construcción: base + 2 laterales (sin hueco interior)
        # centrado en Y: base_point Y = -W/2
        desc = {
            "bases": [
                {
                    "type": "cubo",
                    "length": L,
                    "width": W,
                    "height": t,
                    "base_point": (0, -W / 2.0, 0),
                    "color": color,
                    "operations": [
                        {"action": "union", "shape": {"type": "cubo", "length": L, "width": t, "height": H, "base_point": (0, -W / 2.0, 0), "color": color}},
                        {"action": "union", "shape": {"type": "cubo", "length": L, "width": t, "height": H, "base_point": (0, (W / 2.0) - t, 0), "color": color}},
                    ],
                }
            ]
        }
        return self.geo_tools.build_from_description(desc)

