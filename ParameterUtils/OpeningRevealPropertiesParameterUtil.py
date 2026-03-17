""" implementation of the opening reveal properties parameter utilities
"""

import NemAll_Python_ArchElements as AllplanArchEle

from BuildingElement import BuildingElement

class OpeningRevealPropertiesParameterUtil():
    """ implementation of the opening reveal properties parameter utilities
    """

    @staticmethod
    def create_reveal_properties(build_ele   : BuildingElement,
                                 name_postfix: str,
                                 reveal_prop : AllplanArchEle.VerticalOpeningRevealProperties):
        """ create the reveal properties from the parameter values

        Args:
            build_ele:    building element with the parameter properties
            name_postfix: postfix of the parameter names
            reveal_prop:  reveal properties
        """

        reveal_prop.Type        = build_ele.get_existing_property(f"Reveal{name_postfix}").value
        reveal_prop.Depth       = build_ele.get_existing_property(f"Depth{name_postfix}").value
        reveal_prop.OuterOffset = build_ele.get_existing_property(f"OuterOffset{name_postfix}").value
        reveal_prop.InnerOffset = build_ele.get_existing_property(f"InnerOffset{name_postfix}").value
        reveal_prop.SideOffset  = build_ele.get_existing_property(f"SideOffset{name_postfix}").value
