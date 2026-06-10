import NemAll_Python_Geometry as AllplanGeo


class SolidOpening():
    def __init__(self, solid: AllplanGeo.Polyhedron3D, placement: AllplanGeo.Vector3D, size: list[float]):
        self.solid = solid
        self.placement = placement
        self.size = size
