""" implementation of the coordinate value utilities
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import NemAll_Python_Geometry as AllplanGeo

from ValueListUtil import ValueListUtil

from ..ValueTypeUtils.ParameterPropertyListUtil import ParameterPropertyListUtil

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

CoordEle   = AllplanGeo.Point2D | AllplanGeo.Point3D | AllplanGeo.Vector2D | AllplanGeo.Vector3D
CoordEle3d = AllplanGeo.Point3D | AllplanGeo.Vector3D

class CoordinateValueUtil():
    """ implementation of the coordinate value utilities
    """

    SUB_NAME_SEPARATOR = "."
    INDEX_BRACKET      = "["

    @staticmethod
    def set_coordinate(prop : ParameterProperty,
                       name : str,
                       value: (float | list[float])):
        """ Set the coordinate of a geometry element

        Args:
            prop:  parameter property of the coordinate
            name:  name of the modified property
            value: property value
        """

        if value is None:
            return

        prop.is_modified = True


        #----------------- assign the new value in case of a full element

        if CoordinateValueUtil.SUB_NAME_SEPARATOR not in name and CoordinateValueUtil.INDEX_BRACKET not in name:
            prop.value = value

            return


        #----------------- part can't be an empty list

        if value == []:
            return


        #----------------- resize a list

        if isinstance(value, list):
            if isinstance(prop.value, list):
                ValueListUtil.resize_2_dim_list(value, prop.value)
            else:
                prop.value = ValueListUtil.create_value_list(prop, value)


        #----------------- assign the new value

        coord = ParameterPropertyListUtil.get_item_value(prop, name)

        CoordinateValueUtil.set_coordinate_value(coord, name, value)


    @staticmethod
    def set_coordinate_value(coord: (CoordEle | list[CoordEle]),
                             name : str,
                             value: Any) -> Any:
        """ Set the coordinate value (x or y or z) of a geometry element

        Args:
            coord: coordinate
            name:  name of the modified property
            value: property value

        Returns:
            modified coordinate
        """

        #----------------- assign the sub value(s) of the coordinate

        if isinstance(value, list):
            ValueListUtil.replace_sub_values(value, cast(list, coord), name[-1])

            return coord

        match name[-1]:
            case "X":
                return ParameterPropertyListUtil.set_sub_item_value(coord, "X", value)

            case "Y":
                return ParameterPropertyListUtil.set_sub_item_value(coord, "Y", value)

            case "Z":
                return ParameterPropertyListUtil.set_sub_item_value(coord, "Z", value)


        #----------------- set the complete coordinate

        if isinstance(coord, list):
            for item in coord:
                item.Set(value)
        else:
            coord.Set(value)

        return coord


    @staticmethod
    def set_sub_item_coordinate_value(items: Any,
                                      name : str,
                                      value: Any):
        """ set the sub item value

        Args:
            items: items
            name:  name of the modified property
            value: new value
        """

        sub_item_name = name.split(".", 1)[1].split(".", 1)[0]

        if isinstance(items, list):
            for item in items:
                setattr(item, sub_item_name, CoordinateValueUtil.set_coordinate_value(getattr(item, sub_item_name), name, value))
        else:
            setattr(items, sub_item_name, CoordinateValueUtil.set_coordinate_value(getattr(items, sub_item_name), name, value))
