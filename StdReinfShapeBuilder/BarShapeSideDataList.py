""" implementation of the list for the bar shape side data
"""

from typing import List, Union, Tuple

import NemAll_Python_Geometry as AllplanGeo

class BarShapeSideDataList(List[Union[float,
                                      Tuple[AllplanGeo.Point2D, AllplanGeo.Point2D, float],
                                      Tuple[AllplanGeo.Point2D, AllplanGeo.Point2D, float, float],
                                      Tuple[AllplanGeo.Point2D, AllplanGeo.Point2D, float, float, float],
                                      Tuple[AllplanGeo.Line2D, float],
                                      Tuple[AllplanGeo.Line2D, float, float],
                                      Tuple[AllplanGeo.Line2D, float, float, float],
                                      Tuple[AllplanGeo.Arc2D, float, float, float],
                                      Tuple[AllplanGeo.Point3D, AllplanGeo.Point3D, float],
                                      Tuple[AllplanGeo.Point3D, AllplanGeo.Point3D, float, float],
                                      Tuple[AllplanGeo.Line3D, float],
                                      Tuple[AllplanGeo.Line3D, float, float]]]):
    """ the rows can have the following tuple entries

        cover: float as concrete cover at the start/end of the shape\n
        or\n
        (start point: AllplanGeo.Point2D as start point of the side,
         end point: AllplanGeo.Point2D as end point of the side,
         cover: float as concrete cover of the side,
         bending_roller: float as optional bending roller at the side end,
         z_coord_bar: float as optional bar coordinate in z direction of the local shape coordinate system)\n
        or\n
        (start point: AllplanGeo.Point3D as start point of the side,
         end point: AllplanGeo.Point3D as end point of the side,
         cover: float as concrete cover of the side,
         bending_roller: float as optional bending roller at the side end)\n
        or\n
        (line: AllplanGeo.Line2D/3D as side,
         cover: float as concrete cover of the side,
         bending_roller: float as optional bending roller at the side end)\n
        or\n
        (arc: AllplanGeo.Arc2D as side,
         cover: float as concrete cover of the side,
         bending_roller: float as optional bending roller at the side end)
    """
