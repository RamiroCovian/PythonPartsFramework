""" implementation of the bottom plane references dialog
"""

import NemAll_Python_ArchElements as AllplanArch

from BuildingElement import BuildingElement
from ControlProperties import ControlProperties
from DocumentManager import DocumentManager
from ParameterProperty import ParameterProperty

from .ValueDialogType import ValueDialogType

class BottomPlaneReferencesDialogImpl(ValueDialogType):
    """ implementation of the bottom plane references dialog
    """

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

        index = BottomPlaneReferencesDialogImpl.get_index(build_ele, value_ctrl_prop, name)

        doc        = DocumentManager.get_instance().document
        pythonpart = DocumentManager.get_instance().pythonpart_element

        if index is None:
            AllplanArch.PropertyDialogs.OpenBottomPlaneReferenceDialog(pythonpart, doc, prop.value)
        else:
            AllplanArch.PropertyDialogs.OpenBottomPlaneReferenceDialog(pythonpart, doc, prop.value[index])

        return True
