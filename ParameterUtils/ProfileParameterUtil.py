""" implementation of the profile parameter utility
"""

import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_Geometry as AllplanGeo

class ProfileParameterUtil():
    """ implementation of the profile parameter utility
    """

    def __init__(self,
                 profile_name   : str,
                 default_polygon: AllplanGeo.Polygon2D = AllplanGeo.Polygon2D()):
        """ initialize

        Args:
            profile_name:    name of the profile
            default_polygon: default polygon in case of empty profile name
        """

        self.__profile_polyline = default_polygon
        self.__profile_name     = ""

        self.__read_profile(profile_name)


    def get_polygon(self,
                    profile_name: str) -> AllplanGeo.Polygon2D:
        """ get the profile polygon

        Args:
            profile_name: name of the profile

        Returns:
            profile polygon
        """

        self.__read_profile(profile_name)

        return AllplanGeo.Polygon2D(self.__profile_polyline.Points)


    def __read_profile(self,
                       profile_name: str):
        """ read the profile, the coordinates are local to the center point

        Args:
            profile_name: name of the profile
        """

        if not profile_name:
            return

        if self.__profile_name != profile_name:
            self.__profile_name = profile_name

            profile_polyline = AllplanArchEle.ProfileCatalogService.GetProfileBoundaryPolyline(self.__profile_name)

            minmax, _ = AllplanGeo.CalcMinMax(profile_polyline)

            ref_pnt = minmax.GetCenter()

            self.__profile_polyline = AllplanGeo.Move(profile_polyline, AllplanGeo.Vector2D(ref_pnt) * -1)
