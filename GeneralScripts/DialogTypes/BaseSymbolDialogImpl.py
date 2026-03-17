""" implementation of the symbol dialog
"""

from _collections_abc import Callable

import NemAll_Python_ArchElements as AllplanArch
import NemAll_Python_Palette as AllplanPalette

from BuildingElementStringTable import BuildingElementStringTable
from ControlProperties import ControlProperties
from ParameterProperty import ParameterProperty

from Utilities.GeneralConstants import GeneralConstants

from .FileDialog import FileDialog

class BaseSymbolDialogImpl(FileDialog):
    """ implementation of the symbol dialog
    """

    @staticmethod
    def create_controls(wpf_palette       : AllplanPalette.PythonWpfPaletteBuilder,
                        prop              : ParameterProperty,
                        ctrl_props        : ControlProperties,
                        page_index        : int,
                        _global_str_table : BuildingElementStringTable,
                        is_control_enabled: Callable[[ControlProperties], bool]) -> bool:
        """ Add the controls

        Args:
            wpf_palette:        palette builder
            prop:               parameter property
            ctrl_props:         control properties
            page_index:         page index
            _global_str_table:  global string table
            is_control_enabled: function for getting the enabled state

        Returns:
            True
        """

        init_path = prop.value or AllplanArch.PropertyDialogs.GetLastSymbolPath()

        row_name = ctrl_props.row_name or ctrl_props.text

        wpf_palette.AddButton(init_path, prop.name + GeneralConstants.DIALOG_BUTTON_KEY,
                              0, page_index,
                              ctrl_props.expander_name, row_name,
                              is_control_enabled(ctrl_props),
                              ctrl_props.height, ctrl_props.width,
                              ctrl_props.font_style, ctrl_props.font_face_code)

        return True
