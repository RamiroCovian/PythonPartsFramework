""" implementation of the handle creator
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW

from HandleDirection import HandleDirection
from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from HandleProperties import HandleProperties

class HandleCreator():
    """ implementation of the handle creator
    """

    @staticmethod
    def point_distance(handle_list      : list[HandleProperties],
                       name             : str,
                       handle_point     : AllplanGeo.Point3D,
                       ref_point        : AllplanGeo.Point3D,
                       has_input_field  : bool                        = True,
                       input_field_above: bool                        = True,
                       show_handles     : bool                        = True,
                       center_point     : (AllplanGeo.Point3D | None) = None):
        """ create a handle with a point distance

        Args:
            handle_list:       handle list
            name:              handle parameter name
            handle_point:      handle point
            ref_point:         reference point
            has_input_field:   has input field state
            input_field_above: input field above the dimension line state
            show_handles:      show the handles state
            center_point:      center point for arc
        """

        handle_list.append(HandleProperties(name, handle_point, ref_point,
                                            [HandleParameterData(name, HandleParameterType.POINT_DISTANCE,
                                                                 has_input_field = has_input_field,
                                                                 show_input_field_always = True,
                                                                 input_field_above = input_field_above)],
                                            HandleDirection.POINT_DIR,
                                            show_handles = show_handles,
                                            center_point = center_point))


    @staticmethod
    def point(handle_list : list[HandleProperties],
              name        : str,
              handle_point: AllplanGeo.Point3D,
              index       : (int | None) = None,
              info_text   : str          = ""):
        """ create a handle with a point to move

        Args:
            handle_list:  handle list
            name:         handle parameter name
            handle_point: handle point
            index:        point index
            info_text:    info text
        """

        handle_list.append(HandleProperties(name, handle_point, handle_point,
                                            [HandleParameterData(name, HandleParameterType.POINT, False,
                                                                 list_index = index)],
                                             HandleDirection.XYZ_DIR, info_text = info_text))


    @staticmethod
    def point_list_2d(handle_list  : list[HandleProperties],
                      name         : str,
                      handle_points: list[AllplanGeo.Point2D],
                      info_text    : str          = ""):
        """ create a handle with a point to move

        Args:
            handle_list:   handle list
            name:          handle parameter name
            handle_points: handle points
            info_text:     info text
        """

        for index, pnt in enumerate(handle_points):
            HandleCreator.point(handle_list, name, pnt.To3D, index, info_text)


    @staticmethod
    def move_in_direction(handle_list    : list[HandleProperties],
                          name           : str,
                          placement_point: AllplanGeo.Point3D,
                          angle          : AllplanGeo.Angle,
                          info_text      : str = ""):
        """ create a handle for a move in the arrow direction

        Args:
            handle_list:     handle list
            name:            handle parameter name
            placement_point: placement move handle
            angle:           handle angle
            info_text:       info text
        """

        move_handle = HandleProperties(name, placement_point, AllplanGeo.Point3D(),
                                       [HandleParameterData(name, HandleParameterType.POINT, False)],
                                        HandleDirection.XYZ_DIR)

        move_handle.handle_type  = AllplanIFW.ElementHandleType.HANDLE_ARROW
        move_handle.info_text    = info_text
        move_handle.handle_angle = angle

        handle_list.append(move_handle)


    @staticmethod
    def move(handle_list    : list[HandleProperties],
             name           : str,
             placement_point: AllplanGeo.Point3D,
             info_text      : str = ""):
        """ create a handle for a move

        Args:
            handle_list:     handle list
            name:            handle parameter name
            placement_point: placement move handle
            info_text:       info text
        """

        move_handle = HandleProperties(name, placement_point, AllplanGeo.Point3D(),
                                       [HandleParameterData(name, HandleParameterType.POINT, False)],
                                        HandleDirection.XYZ_DIR)

        move_handle.handle_type  = AllplanIFW.ElementHandleType.HANDLE_SQUARE_BLUE
        move_handle.info_text    = info_text

        handle_list.append(move_handle)


    @staticmethod
    def move_xyz(handle_list      : list[HandleProperties],
                 name             : str,
                 handle_point     : AllplanGeo.Point3D,
                 ref_point        : AllplanGeo.Point3D,
                 has_input_field  : bool = True,
                 input_field_above: bool = True,
                 show_handles     : bool = True):
        """ create a handle with a move in x/y/z direction

        Args:
            handle_list:       handle list
            name:              handle parameter name
            handle_point:      handle point
            ref_point:         reference point
            has_input_field:   has input field state
            input_field_above: input field above the dimension line state
            show_handles:      show the handles state
        """

        handle_list.append(HandleProperties(name, handle_point, ref_point,
                                            [HandleParameterData(name, HandleParameterType.POINT_DISTANCE,
                                                                 has_input_field = has_input_field,
                                                                 show_input_field_always = True,
                                                                 input_field_above = input_field_above)],
                                            HandleDirection.XYZ_DIR,
                                            show_handles = show_handles))
