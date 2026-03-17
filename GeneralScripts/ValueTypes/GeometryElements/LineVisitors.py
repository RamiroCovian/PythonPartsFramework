""" implementation of the line visitors for the property modification
"""

# pylint: disable=invalid-name

from typing import Any

import NemAll_Python_Geometry as AllplanGeo

from .CoordinateValueUtil import CoordinateValueUtil
from ..ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil

LINE_TYPES = AllplanGeo.Line2D | AllplanGeo.Line3D | list[AllplanGeo.Line2D] | list[AllplanGeo.Line3D]

class LineVisitors():
    """ implementation of the line visitors for the property modification
    """

    @staticmethod
    def visit_StartPoint(line     : LINE_TYPES,
                         sep_count: int,
                         name     : str,
                         value    : Any):
        """ modify the start point

        Args:
            line:      description
            sep_count: separator count
            name:      name of the modified property
            value:     new value
        """

        if sep_count == 1:
            ParameterPropertyListUtil.set_sub_item_value(line, "StartPoint", value)

        else:
            CoordinateValueUtil.set_sub_item_coordinate_value(line, name, value)


    @staticmethod
    def visit_EndPoint(line     : LINE_TYPES,
                       sep_count: int,
                       name     : str,
                       value    : Any):
        """ modify the end point

        Args:
            line:      description
            sep_count: separator count
            name:      name of the modified property
            value:     new value
        """

        if sep_count == 1:
            ParameterPropertyListUtil.set_sub_item_value(line, "EndPoint", value)

        else:
            CoordinateValueUtil.set_sub_item_coordinate_value(line, name, value)
