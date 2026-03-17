""" implementation of the opening door swing properties parameter utilities
"""

import math

import NemAll_Python_ArchElements as AllplanArchEle

from BuildingElement import BuildingElement

class OpeningDoorSwingPropertiesParameterUtil():
    """ implementation of the opening door swing properties parameter utilities
    """

    @staticmethod
    def create_door_swing_properties(build_ele   : BuildingElement,
                                 name_postfix: str,
                                 door_swing_prop : AllplanArchEle.DoorSwingProperties):
        """ create the door swing properties from the parameter values

        Args:
            build_ele:    building element with the parameter properties
            name_postfix: postfix of the parameter names
            door_swing_prop:  door_swing properties
        """

        door_swing_prop.Type           = build_ele.get_existing_property(f"DoorSwingSymbol{name_postfix}").value
        door_swing_prop.BasePointIndex = build_ele.get_existing_property(f"DoorSwingBasePointIndex{name_postfix}").value
        door_swing_prop.Angle          = math.radians(build_ele.get_existing_property(f"OpeningSymbolAngle{name_postfix}").value)
        door_swing_prop.LeafThickness  = build_ele.get_existing_property(f"OpeningSymbolOffset{name_postfix}").value
