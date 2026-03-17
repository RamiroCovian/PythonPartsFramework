""" implementation of the trade dialog
"""

from _collections_abc import Callable

import NemAll_Python_ArchElements as AllplanArch
import NemAll_Python_Palette as AllplanPalette

from BuildingElement import BuildingElement
from BuildingElementStringTable import BuildingElementStringTable
from ControlProperties import ControlProperties
from DocumentManager import DocumentManager
from ParameterProperty import ParameterProperty

from Utilities.GeneralConstants import GeneralConstants

from .ValueDialogType import ValueDialogType

class TradeDialogImpl(ValueDialogType):
    """ implementation of the trade dialog
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

        row_name = ctrl_props.row_name if ctrl_props.row_name else ctrl_props.text

        wpf_palette.AddButton(AllplanArch.PropertyDialogs.GetTradeDescription(prop.value),
                              prop.name + GeneralConstants.DIALOG_BUTTON_KEY, 0, page_index,
                              ctrl_props.expander_name, row_name,
                              is_control_enabled(ctrl_props),
                              ctrl_props.height, ctrl_props.width,
                              ctrl_props.font_style, ctrl_props.font_face_code)

        return True


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

        index = TradeDialogImpl.get_index(build_ele, value_ctrl_prop, name)

        doc = DocumentManager.get_instance().document

        if index is None:
            prop.value = AllplanArch.PropertyDialogs.OpenTradeDialog(doc, prop.value)
        else:
            prop.value[index] = AllplanArch.PropertyDialogs.OpenTradeDialog(doc, prop.value[index])

        return False
