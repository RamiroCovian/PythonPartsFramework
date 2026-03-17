""" implementation of the vertical opening geometry properties parameter utilities
"""

import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_Geometry as AllplanGeo

from BuildingElement import BuildingElement

from .ProfileParameterUtil import ProfileParameterUtil

class VerticalOpeningGeometryPropertiesParameterUtil():
    """ implementation of the vertical opening geometry properties parameter utilities
    """

    def __init__(self,
                 build_ele   : BuildingElement,
                 name_postfix: str):
        """ initialize

        Args:
            build_ele:    building element with the parameter properties
            name_postfix: postfix of the parameter names
        """

        self.name_postfix = name_postfix

        profile_prop = build_ele.get_property(f"Profile{self.name_postfix}")

        self.profile_param_util = ProfileParameterUtil("" if profile_prop is None else profile_prop.value)

        self.adapt_plane_references(build_ele)


    def create_opening_geo_properties(self,
                                      build_ele       : BuildingElement,
                                      opening_geo_prop: AllplanArchEle.VerticalOpeningGeometryProperties):
        """ create the opening Geometry properties from the parameter values

        Args:
            build_ele:        building element with the parameter properties
            opening_geo_prop: opening geometry properties
        """

        name_postfix = self.name_postfix

        opening_geo_prop.Shape     = build_ele.get_existing_property(f"Shape{name_postfix}").value
        opening_geo_prop.Width     = build_ele.get_existing_property(f"Width{name_postfix}").value
        opening_geo_prop.RiseAtTop = build_ele.get_existing_property(f"RiseAtTop{name_postfix}").value

        if (depth := build_ele.get_property(f"Depth{name_postfix}")) is not None:
            opening_geo_prop.Depth = depth.value or build_ele.ElementThickness.value

        if opening_geo_prop.Shape == AllplanArchEle.VerticalOpeningShapeType.eRiseBottomTop:
            opening_geo_prop.SegmentsAtTop     = build_ele.get_existing_property(f"SegmentsAtTop{name_postfix}").value
            opening_geo_prop.SegmentsAtBottom  = build_ele.get_existing_property(f"SegmentsAtBottom{name_postfix}").value
            opening_geo_prop.RiseAtBottom      = build_ele.get_existing_property(f"RiseAtBottom{name_postfix}").value

        if opening_geo_prop.Shape == AllplanArchEle.VerticalOpeningShapeType.eArbitrary:
            opening_geo_prop.ProfilePath = build_ele.get_existing_property(f"Profile{name_postfix}").value

            if not opening_geo_prop.ProfilePath:
                opening_geo_prop.Shape = AllplanArchEle.VerticalOpeningShapeType.eRectangle
            else:
                opening_geo_prop.ShapePolygon = self.profile_param_util.get_polygon(opening_geo_prop.ProfilePath)

        self.adapt_plane_references(build_ele)


    def adapt_plane_references(self,
                               build_ele: BuildingElement):
        """ adapt the plane references

        Args:
            build_ele: building element with the parameter properties
        """

        if (profile_prop := build_ele.get_property(f"Profile{self.name_postfix}")) is None:
            return

        name_postfix = self.name_postfix

        height_settings = build_ele.HeightSettings.value

        if build_ele.get_existing_property(f"Shape{name_postfix}").value != AllplanArchEle.VerticalOpeningShapeType.eArbitrary or \
            not build_ele.get_existing_property(f"Profile{self.name_postfix}").value:
            height = height_settings.Height

            if height_settings.TopPlaneDependency == AllplanArchEle.PlaneReferences.PlaneReferenceDependency.eTopFixed:
                height_settings.TopPlaneDependency = AllplanArchEle.PlaneReferences.PlaneReferenceDependency.eTopPlane

                height_settings.Height = height

            return

        if height_settings.BottomPlaneDependency != AllplanArchEle.PlaneReferences.PlaneReferenceDependency.eComponentsBottomPlane and \
           height_settings.TopPlaneDependency    != AllplanArchEle.PlaneReferences.PlaneReferenceDependency.eComponentsTopPlane:
            height_settings.TopPlaneDependency = AllplanArchEle.PlaneReferences.PlaneReferenceDependency.eTopFixed

        profile_min_max = AllplanGeo.CalcMinMax(self.profile_param_util.get_polygon(profile_prop.value))[0]

        build_ele.get_existing_property(f"Width{name_postfix}").value = profile_min_max.SizeX

        height_settings.Height = profile_min_max.SizeY
