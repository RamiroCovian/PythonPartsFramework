""" implementation of the MaterialCatalogReference value type
"""

# pylint: disable=magic-value-comparison

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette

from ControlProperties import ControlProperties

from ..BaseStrImpl import BaseStrImpl

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class MaterialCatalogReferenceImpl(BaseStrImpl):
    """ implementation of the MaterialCatalogReference value type
    """

    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the string combo box control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        start = prop.value.find("(")
        end   = prop.value.find(")")
        val   = prop.value[start + 1:]

        if end > -1:
            val = prop.value[start + 1: end]

        if "ConcreteCat" in prop.value or "In-situ ConcreteCat" in prop.value:
            prop_pal_ctrl_service.add_control(wpf_palette.AddConcreteGradeCatalogRef, prop, ctrl_props, val)

        if "InsulationCat" in prop.value:
            prop_pal_ctrl_service.add_control(wpf_palette.AddInsulationCatalogRef, prop, ctrl_props, val)

        if "Brick/TileCat" in prop.value:
            prop_pal_ctrl_service.add_control(wpf_palette.AddBrickTileCatalogRef, prop, ctrl_props, val)
