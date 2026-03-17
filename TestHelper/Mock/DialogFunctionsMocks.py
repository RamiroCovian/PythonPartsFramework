""" Implementation of the dialog function mocks.
"""

# pylint: disable=invalid-name

import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

ATTRIBUTE_ID = 1398

def OpenAttributeSelectionDialog(_doc       : AllplanEleAdapter.DocumentAdapter,
                                 _dialogType: AllplanBaseEle.AttributeService.AttributeSelectionDialogType) -> int:
    """ open the attribute selection dialog

    Args:
        _doc:        document of the Allplan drawing files
        _dialogType: dialog type

    Returns:
        attribute ID
    """

    return ATTRIBUTE_ID


def OpenRGBColorDialog(_doc  : AllplanEleAdapter.DocumentAdapter,
                       _color: int) -> int:
    """ open the rgb color dialog

    Args:
        _doc:   document of the Allplan drawing files
        _color: color

    Returns:
        color
    """

    return AllplanBasisEle.ARGB(255, 0, 0, 0).GetARGB() + 0x1000000


def OpenSymbolDialog(_default_value: str) -> str:
    """ open the symbol dialog

    Args:
        _default_value: default value

    Returns:
        color
    """

    return "this is a symbol"


def set_attribute_id_for_button(attribute_id: int):
    """ set the attribute ID for the attribute button click

    Args:
        attribute_id: attribute ID
    """

    global ATTRIBUTE_ID     # pylint: disable=global-statement

    ATTRIBUTE_ID = attribute_id
