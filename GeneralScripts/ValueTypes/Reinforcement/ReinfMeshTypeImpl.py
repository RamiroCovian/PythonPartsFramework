""" implementation of the ReinfMeshType value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Reinforcement as AllplanReinf

from ControlProperties import ControlProperties

from Utilities.GeneralConstants import GeneralConstants

from ..BaseStrImpl import BaseStrImpl
from ..ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty
    from ..ValueTypeUtils.PropertyPaletteControlService import PropertyPaletteControlService

class ReinfMeshTypeImpl(BaseStrImpl):
    """ implementation of the ReinfMeshType value type
    """

    @staticmethod
    def get_value(value_str: str) -> (list[str] | str):
        """ get the mesh type from a string

        Args:
            value_str: value string

        Returns:
            value from string
        """

        if value_str == GeneralConstants.USE_CURRENT_RESOURCE_VALUE:
            return AllplanReinf.ReinforcementSettings.GetMeshType()

        return BaseStringToValueConverter.to_str(value_str)


    @staticmethod
    def add_to_palette(wpf_palette          : AllplanPalette.PythonWpfPaletteBuilder,
                       prop                 : ParameterProperty,
                       ctrl_props           : ControlProperties,
                       prop_pal_ctrl_service: PropertyPaletteControlService):
        """ Add the ReinfMeshType edit control

        Args:
            wpf_palette:           WPf palette
            prop:                  parameter property
            ctrl_props:            control properties
            prop_pal_ctrl_service: property palette control service
        """

        if not ctrl_props.constraint:
            mesh_group = -1
        else:
            if (mesh_group_prop := prop_pal_ctrl_service.build_ele.get_property(ctrl_props.constraint[0])) is None:
                print(f"Constaint {ctrl_props.constraint[0]} not found for the mesh type")

                return

            mesh_group = mesh_group_prop.value

        wpf_palette.AddMeshType(ctrl_props.text, prop.name, prop.value, prop_pal_ctrl_service.page_index,
                                ctrl_props.expander_name + ctrl_props.expander_state_key,
                                ctrl_props.row_name + ctrl_props.row_state_key,
                                prop_pal_ctrl_service.is_control_enabled(ctrl_props), mesh_group,
                                ctrl_props.height, ctrl_props.width, ctrl_props.font_face_code)
