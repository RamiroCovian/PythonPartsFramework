""" implementation of the opening tier offset properties parameter utilities
"""

import NemAll_Python_ArchElements as AllplanArchEle

from BuildingElement import BuildingElement

class OpeningTierOffsetPropertiesParameterUtil():
    """ implementation of the tier offset properties parameter utilities
    """

    @staticmethod
    def create_tier_offset_properties(build_ele       : BuildingElement,
                                      name_postfix    : str,
                                      tier_offset_prop: AllplanArchEle.VerticalOpeningTierOffsetProperties):
        """ create the opening tier offset properties from the parameter values

        Args:
            build_ele:        building element with the parameter properties
            name_postfix:     postfix of the parameter names
            tier_offset_prop: tier offset properties
        """

        #----------------- set the properties for the tier offset

        tier_offset_prop.Type        = build_ele.get_existing_property(f"LayerOffsetType{name_postfix}").value
        tier_offset_prop.LeftOffset  = build_ele.get_existing_property(f"LeftOffset{name_postfix}").value
        tier_offset_prop.RightOffset = build_ele.get_existing_property(f"RightOffset{name_postfix}").value
        tier_offset_prop.TopOffset   = build_ele.get_existing_property(f"TopOffset{name_postfix}").value

        match build_ele.get_existing_property(f"LayerOffsetType{name_postfix}").value:
            case AllplanArchEle.VerticalOpeningTierOffsetType.eAdvanced:
                tier_offset_prop.LeftOffsets   = build_ele.get_existing_property(f"LeftOffsets{name_postfix}").value
                tier_offset_prop.RightOffsets  = build_ele.get_existing_property(f"RightOffsets{name_postfix}").value
                tier_offset_prop.BottomOffsets = build_ele.get_existing_property(f"BottomOffsets{name_postfix}").value
                tier_offset_prop.TopOffsets    = build_ele.get_existing_property(f"TopOffsets{name_postfix}").value


        #----------------- set properties for the facing

            case AllplanArchEle.VerticalOpeningTierOffsetType.eWithOuterFacing | \
                 AllplanArchEle.VerticalOpeningTierOffsetType.eWithInnerFacing:
                facing_prop = tier_offset_prop.GetFacingProperties()

                facing_prop.LeftFacing = build_ele.get_existing_property(f"HasLeftFacing{name_postfix}").value
                facing_prop.RightFacing = build_ele.get_existing_property(f"HasRightFacing{name_postfix}").value
                facing_prop.TopFacing = build_ele.get_existing_property(f"HasTopFacing{name_postfix}").value

                if facing_prop.LeftFacing:
                    facing_prop.LeftWidth = build_ele.get_existing_property(f"LeftWidth{name_postfix}").value
                    facing_prop.LeftDepth = build_ele.get_existing_property(f"LeftDepth{name_postfix}").value

                if facing_prop.RightFacing:
                    facing_prop.RightWidth = build_ele.get_existing_property(f"RightWidth{name_postfix}").value
                    facing_prop.RightDepth = build_ele.get_existing_property(f"RightDepth{name_postfix}").value

                if facing_prop.TopFacing:
                    facing_prop.TopWidth = build_ele.get_existing_property(f"TopWidth{name_postfix}").value
                    facing_prop.TopDepth = build_ele.get_existing_property(f"TopDepth{name_postfix}").value

                facing_prop.OpeningSide = \
                    AllplanArchEle.OpeningSide.eInnerSide \
                        if build_ele.get_existing_property(f"OpeningWidthDefinedBy{name_postfix}").value == "Interior side" else \
                    AllplanArchEle.OpeningSide.eOuterSide
