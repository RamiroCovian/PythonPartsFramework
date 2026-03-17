""" implementation of the service for the handle properties
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Optional, Any, Dict, Type

import abc
import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil

import BuildingElementParameterPropertyUtil as PropertyUtil

from HandleParameterData import HandleParameterData
from HandleParameterType import HandleParameterType
from HandleProperties import HandleProperties
from ParameterProperty import ParameterProperty

from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes

if TYPE_CHECKING:
    from BuildingElement import BuildingElement

ANGLE_EPS = 0.1
ZMIN_NAME = "ZMin"
ZMAX_NAME = "ZMax"



#------------------------------------------------ implementation of the base class for the property update --------------------------------



class _BaseHandlePropUpdate(abc.ABC):
    """ base class for the handle property update
    """

    def __init__(self,
                 build_ele  : BuildingElement,
                 handle_prop: HandleProperties,
                 input_pnt  : AllplanGeo.Point3D,
                 param_data : HandleParameterData):
        """ initialize

        Args:
            build_ele:   building element with the parameter properties
            handle_prop: handle property
            input_pnt:   input point
            param_data:  parameter data
        """

        self._build_ele      = build_ele
        self._handle_prop    = handle_prop
        self._input_pnt      = input_pnt
        self._param_data     = param_data
        self._update_palette = False

        self._dist_pnt     = input_pnt - self._handle_prop.ref_point
        self._is_abs_value = self._handle_prop.abs_value


    def get_property_data(self) -> Tuple[Optional[ParameterProperty], str, str]:
        """ get the property data

        Returns:
            parameter property, item_name with index, parameter name
        """

        item_name = self._param_data.param_prop_name.replace(self._build_ele.element_id, "")
        name      = PropertyUtil.get_property_value_name(item_name)

        if (prop := self._build_ele.get_property(name)) is None:
            AllplanUtil.ShowMessageBox("Building element has no member " + name, AllplanUtil.MB_OK)
            return prop, item_name, name


        #----------------- item name with the index

        if (list_index := self._param_data.list_index) is not None:
            item_name += "[" + str(list_index) + "]" if not isinstance(list_index, list) else \
                         "[" + "][".join([str(index) for index in list_index]) + "]"

        return prop, item_name, name


    def update_property_value(self,
                              value: Any):
        """ update the property value

        Args:
            value: new value
        """

        prop, item_name, name = self.get_property_data()

        if prop is None:
            return


        #------------- check the value range

        if (distance_factor := self._param_data.distance_factor) is None:
            distance_factor = self._handle_prop.distance_factor

        value *= distance_factor

        min_value, max_value, value_list, interval_value = self._handle_prop.get_min_max_values(name)

        if prop.value_type != ParameterPropertyValueTypes.RADIO_BUTTON_GROUP:
            value = max(value, min_value)
            value = min(value, max_value)

        if value_list:
            _, value = prop.value_type.validate_for_list_value(value, prop.value_type, value_list,
                                                               self._build_ele.get_parameter_dict())

        #----------------- check the interval

        if interval_value:
            interval_value = eval(interval_value, self._build_ele.get_parameter_dict())

            count = round((value - min_value) / interval_value)

            value = min_value + count * interval_value


        #----------------- execute the update

        self._update_palette = PropertyUtil.set_property_value(prop, item_name, value)


    def get_z_min_max(self) -> Tuple[Optional[ParameterProperty], Optional[ParameterProperty]]:
        """ get the min and max parameter of the z coordinate

        Returns:
            min/max parameter of the z coordinate
        """

        if (z_min := self._build_ele.get_property("ZMin")) is None:
            AllplanUtil.ShowMessageBox("Building element has no member ZMin", AllplanUtil.MB_OK)
            return (None, None)

        if (z_max := self._build_ele.get_property("ZMax")) is None:
            AllplanUtil.ShowMessageBox("Building element has no member ZMax", AllplanUtil.MB_OK)
            return (None, None)

        return (z_min, z_max)


    @property
    def update_palette(self) -> bool:
        """ get the update palette state

        Returns:
            update palette state
        """

        return self._update_palette


    @abc.abstractmethod
    def __call__(self):
        """ execute the value update
        """


#------------------------------------------------ implementation of the update classes for the parameter types ----------------------------



class _XDistance(_BaseHandlePropUpdate):
    """ modify the x distance
    """

    def __call__(self):
        """ execute the value update
        """

        self.update_property_value(math.fabs(self._dist_pnt.X) if self._is_abs_value else self._dist_pnt.X)


class _YDistance(_BaseHandlePropUpdate):
    """ modify the y distance
    """

    def __call__(self):
        """ execute the value update
        """

        self.update_property_value(math.fabs(self._dist_pnt.Y) if self._is_abs_value else self._dist_pnt.Y)


class _ZDistance(_BaseHandlePropUpdate):
    """ modify the z distance
    """

    def __call__(self):
        """ execute the value update
        """

        self.update_property_value(math.fabs(self._dist_pnt.Z) if self._is_abs_value else self._dist_pnt.Z)


class _Point(_BaseHandlePropUpdate):
    """ modify the point
    """

    def __call__(self):
        """ execute the value update
        """

        prop, item_name, name = self.get_property_data()

        if prop is None:
            return

        _, _, _, interval_value = self._handle_prop.get_min_max_values(name)


        #----------------- adapt the point coordinate to an interval

        if interval_value:
            dist_vec = AllplanGeo.Vector3D(self._dist_pnt)

            if (dist := dist_vec.GetLength()):
                interval_value = eval(interval_value, self._build_ele.get_parameter_dict())

                count = round(dist / interval_value)

                if (dist := count * interval_value):
                    dist_vec.Normalize(dist)

                    self._input_pnt = self._handle_prop.ref_point + dist_vec

        self._update_palette = PropertyUtil.set_property_value(prop, item_name, self._input_pnt)


class _PointDistance(_BaseHandlePropUpdate):
    """ modify the point distance
    """

    def __call__(self):
        """ execute the value update
        """

        self.update_property_value(math.fabs(self._dist_pnt.GetDistance(AllplanGeo.Point3D())))


class _Angle(_BaseHandlePropUpdate):
    """ modify the angle
    """

    def __call__(self):
        """ execute the value update
        """

        dist_pnt = self._dist_pnt

        if self._handle_prop.angle_placement:
            trans_mat = self._handle_prop.angle_placement.GetTransformationMatrix()
            trans_mat.Reverse()

            self.update_property_value(AllplanGeo.CalcAngle(AllplanGeo.Point2D(AllplanGeo.Transform(self._handle_prop.ref_point, trans_mat)),
                                                            AllplanGeo.Point2D(AllplanGeo.Transform(self._input_pnt, trans_mat))).Deg)

        else:
            self.update_property_value(AllplanGeo.CalcAngle(AllplanGeo.Point2D(), AllplanGeo.Point2D(dist_pnt)).Deg)


class _ZCoord(_BaseHandlePropUpdate):
    """ modify the z coordinate
    """

    def __call__(self):
        """ execute the value update
        """

        prop, _, name = self.get_property_data()

        if prop is None:
            return


        #----------------- update the min z coordinate

        if name == ZMIN_NAME:
            z_min, z_max = self.get_z_min_max()

            if z_min is None or z_max is None:
                return

            height = z_max.value - z_min.value

            new_height = AllplanGeo.Vector3D(self._dist_pnt).GetLength()

            z_min.value += height - new_height

            return


        #----------------- update the max z coordinate

        if name == ZMAX_NAME:
            z_min, z_max = self.get_z_min_max()

            if not z_min or not z_max:
                return

            height = z_max.value - z_min.value

            new_height = AllplanGeo.Vector3D(self._dist_pnt).GetLength()

            z_max.value += new_height - height


class _VectorDistance(_BaseHandlePropUpdate):
    """ modify the value by a vector distance
    """

    def __call__(self):
        """ execute the value update
        """

        if (dir_vector := self._param_data.dir_vector) is None and \
           (dir_vector := self._handle_prop.dir_vector) is None:
            return

        vec = AllplanGeo.Vector3D(self._handle_prop.ref_point, self._input_pnt)

        value = math.fabs(self._dist_pnt.GetDistance(AllplanGeo.Point3D()))


        #----------------- check the direction

        if vec.DotProduct(dir_vector) < ANGLE_EPS:
            value *= -1

        self.update_property_value(value)


class _CheckBox(_BaseHandlePropUpdate):
    """ modify the value by checkbox toggle
    """

    def __call__(self):
        """ execute the value update
        """

        prop, item_name, _ = self.get_property_data()

        if prop is None:
            return

        self._update_palette = PropertyUtil.set_property_value(prop, item_name,
                                                               not PropertyUtil.get_property_value(prop, item_name))


class _IncrementButton(_BaseHandlePropUpdate):
    """ modify the value by increment
    """

    def __call__(self):
        """ execute the value update
        """

        prop, item_name, _ = self.get_property_data()

        if prop is None:
            return

        self._update_palette = PropertyUtil.set_property_value(prop, item_name,
                                                               PropertyUtil.get_property_value(prop, item_name) + \
                                                               self._param_data.in_decrement_value)


class _DecrementButton(_BaseHandlePropUpdate):
    """ modify the value by decrement
    """

    def __call__(self):
        """ execute the value update
        """

        prop, item_name, _ = self.get_property_data()

        if prop is None:
            return

        self._update_palette = PropertyUtil.set_property_value(prop, item_name,
                                                               PropertyUtil.get_property_value(prop, item_name) - \
                                                               self._param_data.in_decrement_value)


#------------------------- create the dict with the update classes assigned to the parameter type

HANDLE_PROPERTIES_UPDATER: Dict[HandleParameterType, Type[_BaseHandlePropUpdate]] = \
    {HandleParameterType.X_DISTANCE      : _XDistance,
     HandleParameterType.Y_DISTANCE      : _YDistance,
     HandleParameterType.Z_DISTANCE      : _ZDistance,
     HandleParameterType.POINT           : _Point,
     HandleParameterType.POINT_DISTANCE  : _PointDistance,
     HandleParameterType.ANGLE           : _Angle,
     HandleParameterType.Z_COORD         : _ZCoord,
     HandleParameterType.VECTOR_DISTANCE : _VectorDistance,
     HandleParameterType.CHECK_BOX       : _CheckBox,
     HandleParameterType.INCREMENT_BUTTON: _IncrementButton,
     HandleParameterType.DECREMENT_BUTTON: _DecrementButton
    }



#------------------------------------------------ implementation of the handle properties service -----------------------------------------



class HandlePropertiesService():
    """ implementation of the service for the handle properties
    """

    @staticmethod
    def update_property_value(build_ele  : BuildingElement,
                              handle_prop: HandleProperties,
                              input_pnt  : AllplanGeo.Point3D) -> bool:
        """ Update the property value

        Args:
            build_ele:   building element with the parameter properties
            handle_prop: handle property
            input_pnt:   input point

        Returns:
            update palette state
        """

        update_palette = False

        for param_data in handle_prop.parameter_data:
            if (updater := HANDLE_PROPERTIES_UPDATER.get(param_data.param_type)) is not None:
                update_class = updater(build_ele, handle_prop, input_pnt, param_data)

                update_class()

                update_palette |= update_class.update_palette

        return update_palette
