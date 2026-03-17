""" implementation of the ReinfMeshGroup value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Reinforcement as AllplanReinf

from ControlProperties import ControlProperties

from Utilities.GeneralConstants import GeneralConstants

from ..BaseIntImpl import BaseIntImpl
from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinfMeshGroupImpl(BaseIntImpl):
    """ implementation of the ReinfMeshGroup value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[int] | int):
        """ get the mesh group from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if value_str == GeneralConstants.USE_CURRENT_RESOURCE_VALUE:
            return AllplanReinf.ReinforcementSettings.GetMeshGroup()

        mesh_group = BaseStringToValueConverter.to_int(value_str)

        if isinstance(mesh_group, list):
            return [AllplanReinf.ReinforcementSettings.CheckMeshGroup(mesh_group[i]) for i in range(len(mesh_group))]

        return AllplanReinf.ReinforcementSettings.CheckMeshGroup(mesh_group)



    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the ReinfMeshGroup edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        prop_pal_ctrl_service.add_control(wpf_palette.AddMeshGroup, prop, ctrl_props, prop.value)
