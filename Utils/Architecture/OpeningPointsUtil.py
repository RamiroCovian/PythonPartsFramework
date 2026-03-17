""" implementation of the opening points utilities
"""

import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

class OpeningPointsUtil():
    """ implementation of the opening points utilities
    """

    @staticmethod
    def create_opening_end_point_for_axis_element(opening_start_pnt: AllplanGeo.Point2D,
                                                  opening_width    : float,
                                                  element_axis     : (AllplanGeo.Line2D | AllplanGeo.Arc2D),
                                                  element_polygon  : (AllplanGeo.Polygon2D | AllplanGeo.Polyline2D),
                                                  placement_line   : AllplanGeo.Line2D) -> AllplanGeo.Point2D:
        """ create the opening points for an axis element

        Args:
            opening_start_pnt: opening start point
            opening_width:     opening width
            element_axis:      element axis
            element_polygon:   element polygon / polyline
            placement_line:    placement line

        Returns:
            end point of the opening
        """

        #----------------- opening points for a linear axis

        if isinstance(element_axis, AllplanGeo.Line2D):
            loc_start = AllplanGeo.TransformCoord.PointLocal(placement_line, opening_start_pnt).X

            opening_end_pnt = AllplanGeo.TransformCoord.PointGlobal(placement_line, loc_start + opening_width).To2D


        #----------------- opening points for a circular, spline axis or entity based wall

        else:
            _, dir_ele = AllplanGeo.Polyline2DUtil.GetPolyline2DSegment(AllplanGeo.Polyline2D(element_polygon), opening_start_pnt)

            dir_ele.TrimEnd(-100)

            error, opening_end_pnt = \
                AllplanGeo.Polygon2DUtil.FindPointOnPolygonWithDistance(AllplanGeo.Polygon2D(element_polygon.Points),
                                                                        opening_start_pnt, dir_ele.EndPoint,
                                                                        element_axis, opening_width)

            if error:
                opening_end_pnt = opening_start_pnt

        return opening_end_pnt


    @staticmethod
    def create_opening_end_point_for_shaped_element(opening_start_pnt: AllplanGeo.Point2D,
                                                    opening_width    : float,
                                                    placement_line   : AllplanGeo.Line2D) -> AllplanGeo.Point2D:
        """ create the opening points for a shaped element

        Args:
            opening_start_pnt: opening start point
            opening_width:     opening width
            placement_line:    placement line

        Returns:
            end point of the opening
        """

        loc_start = AllplanGeo.TransformCoord.PointLocal(placement_line, opening_start_pnt).X

        opening_end_pnt = AllplanGeo.TransformCoord.PointGlobal(placement_line, loc_start + opening_width).To2D

        return opening_end_pnt


    @staticmethod
    def create_opening_points_for_axis_element(opening_start_pnt: AllplanGeo.Point2D,
                                               opening_end_pnt  : AllplanGeo.Point2D,
                                               opening_width    : float,
                                               element_thickness: float) -> list[AllplanGeo.Point2D]:
        """ create the opening points for an axis element

        Args:
            opening_start_pnt: opening start point
            opening_end_pnt:   opening end point
            opening_width:     opening width
            element_thickness: element thickness

        Returns:
            opening points
        """

        base_line = AllplanGeo.Line2D(opening_start_pnt, opening_end_pnt)

        opening_points = [opening_start_pnt, opening_end_pnt,
                          AllplanGeo.TransformCoord.PointGlobal(base_line, AllplanGeo.Point2D(opening_width, element_thickness)).To2D,
                          AllplanGeo.TransformCoord.PointGlobal(base_line, AllplanGeo.Point2D(0, element_thickness)).To2D]

        return opening_points



    @staticmethod
    def get_opening_offset_points(element          : AllplanEleAdapter.BaseElementAdapter,
                                  opening_start_pnt: AllplanGeo.Point2D,
                                  placement_line   : AllplanGeo.Line2D) -> tuple[bool, AllplanGeo.Point2D, AllplanGeo.Point2D]:
        """ get the left and right point for the opening offset

        Args:
            element:           element for the opening
            opening_start_pnt: opening start point
            placement_line:    placement line from the opening start point

        Returns:
            points created, start offset point, end offset point
        """

        if AllplanEleAdapter.AxisElementAdapter(element).HasAxis():
            return AllplanArchEle.ArchitectureElementsGeometryService.GetOpeningOffsetPoints(element, opening_start_pnt)

        return True, placement_line.StartPoint, placement_line.EndPoint


    @staticmethod
    def get_start_point_from_start_offset(element_axis    : (AllplanGeo.Line2D | AllplanGeo.Arc2D | None),
                                          offset_start_pnt: AllplanGeo.Point2D,
                                          placement_line  : AllplanGeo.Line2D,
                                          placement_arc   : (AllplanGeo.Arc2D | None),
                                          element_polygon : (AllplanGeo.Polygon2D | AllplanGeo.Polyline2D),
                                          offset          : float) -> tuple[bool, AllplanGeo.Point2D]:
        """ get the start point by an offset from an offset start point

        Args:
            element_axis:     element axis
            offset_start_pnt: offset start point
            placement_line:   placement line
            placement_arc:    placement arc
            element_polygon:  element polygon / polyline
            offset:           offset from the offset start point

        Returns:
            start point of the opening
        """


        #----------------- calculate the new start point of the opening for a linear axis

        if isinstance(element_axis, AllplanGeo.Line2D):
            loc_start_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_line, offset_start_pnt).X

            return True, AllplanGeo.TransformCoord.PointGlobal(placement_line, loc_start_pnt_dist + offset).To2D


        #----------------- calculate the new start point of the opening for a circular axis

        placement_polyline = AllplanArchEle.ArchitectureElementsGeometryService.GetOuterPolyline(
                                        AllplanGeo.Polygon2D(element_polygon.Points),
                                        placement_line, element_axis)

        if isinstance(element_axis, AllplanGeo.Arc2D):
            if placement_arc is None:
                return False, AllplanGeo.Point2D()

            loc_start_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_arc, offset_start_pnt).X

            return OpeningPointsUtil.calc_point_at_placement_arc(loc_start_pnt_dist + offset,
                                                                 placement_arc, placement_polyline)


        #----------------- calculate the new start point of the opening for a polyline axis

        loc_start_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_polyline, offset_start_pnt).X

        return True, AllplanGeo.TransformCoord.PointGlobal(placement_polyline, loc_start_pnt_dist + offset).To2D


    @staticmethod
    def get_distance_from_offset_start_point(input_pnt       : AllplanGeo.Point3D,
                                             element_axis    : (AllplanGeo.Line2D | AllplanGeo.Arc2D | None),
                                             offset_start_pnt: AllplanGeo.Point2D,
                                             placement_line  : AllplanGeo.Line2D,
                                             placement_arc   : (AllplanGeo.Arc2D | None),
                                             element_polygon : (AllplanGeo.Polygon2D | AllplanGeo.Polyline2D)) -> float:
        """ get the local distance between input and offset start point

        Args:
            input_pnt:        input point
            element_axis:     element axis
            offset_start_pnt: offset start point
            placement_line:   placement line
            placement_arc:    placement arc
            element_polygon:  element polygon / polyline

        Returns:
            distance between input and start point
        """

        if isinstance(element_axis, AllplanGeo.Line2D):
            return AllplanGeo.TransformCoord.PointLocal(placement_line, input_pnt).X - \
                   AllplanGeo.TransformCoord.PointLocal(placement_line, offset_start_pnt).X

        if isinstance(element_axis, AllplanGeo.Arc2D):
            if placement_arc is None:
                return 0

            return AllplanGeo.TransformCoord.PointLocal(placement_arc, input_pnt).X - \
                   AllplanGeo.TransformCoord.PointLocal(placement_arc, offset_start_pnt).X

        placement_polyline = AllplanArchEle.ArchitectureElementsGeometryService.GetOuterPolyline(
                             AllplanGeo.Polygon2D(element_polygon.Points),
                                                  placement_line, element_axis)

        return AllplanGeo.TransformCoord.PointLocal(placement_polyline, input_pnt).X - \
               AllplanGeo.TransformCoord.PointLocal(placement_polyline, offset_start_pnt).X


    @staticmethod
    def get_start_point_from_end_offset(element_axis   : (AllplanGeo.Line2D | AllplanGeo.Arc2D | None),
                                        offset_end_pnt : AllplanGeo.Point2D,
                                        placement_line : AllplanGeo.Line2D,
                                        placement_arc  : (AllplanGeo.Arc2D | None),
                                        opening_width  : float,
                                        element_polygon: (AllplanGeo.Polygon2D | AllplanGeo.Polyline2D),
                                        offset         : float) -> tuple[bool, AllplanGeo.Point2D]:
        """ get the start point by an offset from an offset start point

        Args:
            element_axis:    element axis
            offset_end_pnt:  offset end point
            placement_line:  placement line
            placement_arc:   placement arc
            opening_width:   opening width
            element_polygon: element polygon / polyline
            offset:          offset from the offset start point

        Returns:
            start point of the opening
        """

        #----------------- calculate the new start point of the opening for a linear axis

        if isinstance(element_axis, AllplanGeo.Line2D):
            loc_end_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_line, offset_end_pnt).X

            return True, AllplanGeo.TransformCoord.PointGlobal(placement_line,
                                                               loc_end_pnt_dist - offset - opening_width).To2D


        #----------------- calculate the new start point of the opening for a circular axis

        placement_polyline = AllplanArchEle.ArchitectureElementsGeometryService.GetOuterPolyline(
                             AllplanGeo.Polygon2D(element_polygon.Points),
                                                  placement_line, element_axis)

        if isinstance(element_axis, AllplanGeo.Arc2D):
            if placement_arc is None:
                return False, AllplanGeo.Point2D()

            loc_end_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_arc, offset_end_pnt).X

            return OpeningPointsUtil.calc_point_at_placement_arc(loc_end_pnt_dist - offset - opening_width,
                                                                 placement_arc, placement_polyline)


        #----------------- calculate the new start point of the opening for a polyline axis

        if placement_polyline is None:
            return False, AllplanGeo.Point2D()

        loc_end_pnt_dist = AllplanGeo.TransformCoord.PointLocal(placement_polyline, offset_end_pnt).X

        opening_end_pnt = AllplanGeo.TransformCoord.PointGlobal(placement_polyline, loc_end_pnt_dist - offset)


        #----------------- get the start point at the polyline

        _, dir_ele = AllplanGeo.Polyline2DUtil.GetPolyline2DSegment(placement_polyline,
                                                                    opening_end_pnt.To2D)

        dir_ele.TrimStart(-100)

        found, opening_start_pnt = AllplanGeo.Polygon2DUtil.FindPointOnPolygonWithDistance(AllplanGeo.Polygon2D(element_polygon.Points),
                                                                                                                opening_end_pnt.To2D,
                                                                                                                dir_ele.StartPoint,
                                                                                                                element_axis,
                                                                                                                opening_width)

        return (found == 0), opening_start_pnt


    @staticmethod
    def get_distance_from_offset_end_point(input_pnt      : AllplanGeo.Point3D,
                                           element_axis   : (AllplanGeo.Line2D | AllplanGeo.Arc2D | None),
                                           offset_end_pnt : AllplanGeo.Point2D,
                                           placement_line : AllplanGeo.Line2D,
                                           placement_arc  : (AllplanGeo.Arc2D | None),
                                           element_polygon: (AllplanGeo.Polygon2D | AllplanGeo.Polyline2D)) -> float:
        """ get the local distance between input and offset end point

        Args:
            input_pnt:       input point
            element_axis:    element axis
            offset_end_pnt:  offset end point
            placement_line:  placement line
            placement_arc:   placement arc
            element_polygon: element polygon / polyline

        Returns:
            distance between input and start point
        """

        if isinstance(element_axis, AllplanGeo.Line2D):
            return AllplanGeo.TransformCoord.PointLocal(placement_line, offset_end_pnt).X - \
                   AllplanGeo.TransformCoord.PointLocal(placement_line, input_pnt).X

        if isinstance(element_axis, AllplanGeo.Arc2D):
            if placement_arc is None:
                return 0

            return AllplanGeo.TransformCoord.PointLocal(placement_arc, offset_end_pnt).X - \
                   AllplanGeo.TransformCoord.PointLocal(placement_arc, input_pnt).X

        placement_polyline = AllplanArchEle.ArchitectureElementsGeometryService.GetOuterPolyline(
                             AllplanGeo.Polygon2D(element_polygon.Points),
                                                  placement_line, element_axis)

        return AllplanGeo.TransformCoord.PointLocal(placement_polyline, offset_end_pnt).X - \
               AllplanGeo.TransformCoord.PointLocal(placement_polyline, input_pnt).X


    @staticmethod
    def calc_point_at_placement_arc(local_dist        : float,
                                    placement_arc     : AllplanGeo.Arc2D,
                                    placement_polyline: AllplanGeo.Polyline2D) -> tuple[bool, AllplanGeo.Point2D]:
        """ calculate the point at the placement arc

        Args:
            local_dist:         local point distance at the placement arc
            placement_arc:      placement arc
            placement_polyline: placement polyline

        Returns:
            found state, point at the polyline
        """

        ortho_start_pnt = AllplanGeo.TransformCoord.PointGlobal(placement_arc,
                                                                AllplanGeo.Point2D(local_dist, 1000))
        ortho_end_pnt = AllplanGeo.TransformCoord.PointGlobal(placement_arc,
                                                              AllplanGeo.Point2D(local_dist, -1000))

        ortho_line = AllplanGeo.Line2D(ortho_start_pnt.To2D, ortho_end_pnt.To2D)

        found, intersect_pnts = AllplanGeo.IntersectionCalculus(ortho_line, placement_polyline)

        return (True, intersect_pnts[0].To2D) if found else (False, AllplanGeo.Point2D())
