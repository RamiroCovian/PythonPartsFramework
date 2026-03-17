""" implementation of the opening sill properties parameter utilities
"""

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_ArchElements as AllplanArchEle

from BuildingElement import BuildingElement

class OpeningSillPropertiesParameterUtil():
    """ implementation of the opening sill properties parameter utilities
    """

    @staticmethod
    def create_sill_properties(build_ele   : BuildingElement,
                               name_postfix: str,
                               sill_prop   : AllplanArchEle.VerticalOpeningSillProperties):
        """ create the sill properties from the parameter values

        Args:
            build_ele:    building element with the parameter properties
            name_postfix: postfix of the parameter names
            sill_prop:    sill properties
        """

        sill_prop.Type =  build_ele.get_existing_property(f"Sill{name_postfix}").value

        com_prop = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()

        com_prop.Color  =  build_ele.get_existing_property(f"Color{name_postfix}").value
        com_prop.Pen    =  build_ele.get_existing_property(f"Pen{name_postfix}").value
        com_prop.Stroke =  build_ele.get_existing_property(f"Stroke{name_postfix}").value

        sill_prop.CommonProperties = com_prop
