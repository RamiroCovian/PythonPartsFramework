""" implementation of the open file dialog
"""

from _collections_abc import Callable

import NemAll_Python_Palette as AllplanPalette
import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementStringTable import BuildingElementStringTable
from ControlProperties import ControlProperties
from ParameterProperty import ParameterProperty

from .FileDialog import FileDialog

class OpenFileDialogImpl(FileDialog):
    """ implementation of the open file dialog
    """

    @staticmethod
    def create_controls(wpf_palette       : AllplanPalette.PythonWpfPaletteBuilder,
                        prop              : ParameterProperty,
                        ctrl_props        : ControlProperties,
                        page_index        : int,
                        global_str_table  : BuildingElementStringTable,
                        is_control_enabled: Callable[[ControlProperties], bool]) -> bool:
        """ Add the controls

        Args:
            wpf_palette:        palette builder
            prop:               parameter property
            ctrl_props:         control properties
            page_index:         page index
            global_str_table:   global string table
            is_control_enabled: function for getting the enabled state

        Returns:
            created controls state
        """

        return FileDialog.create_controls(wpf_palette, prop, ctrl_props, page_index, global_str_table, is_control_enabled)


    @staticmethod
    def show(build_ele      : BuildingElement,
             prop           : ParameterProperty,
             value_ctrl_prop: ControlProperties,
             name           : str) -> bool:
        """ show the dialog

        Args:
            build_ele:       building element with the parameter properties
            prop:            parameter property
            value_ctrl_prop: value control property
            name:            parameter name

        Returns:
            update palette state
        """

        if (index := OpenFileDialogImpl.get_index(build_ele, value_ctrl_prop, name)) is None:
            prop.value = AllplanUtil.FileDialog.AskOpenFile(prop.value, value_ctrl_prop.text,
                                                            value_ctrl_prop.value_list, value_ctrl_prop.value_list.split("|")[0],
                                                            OpenFileDialogImpl.get_default_directories(value_ctrl_prop))

        else:
            prop.value[index] = \
                AllplanUtil.FileDialog.AskOpenFile(prop.value[index], value_ctrl_prop.text,
                                                   value_ctrl_prop.value_list, value_ctrl_prop.value_list.split("|")[0],
                                                   OpenFileDialogImpl.get_default_directories(value_ctrl_prop))

        return True
