""" definition of the parameter property value types
"""

from __future__ import annotations

from .AttributeSelectionDialogImpl import AttributeSelectionDialogImpl
from .BitmapResourceDialogImpl import BitmapResourceDialogImpl
from .BottomPlaneReferencesDialogImpl import BottomPlaneReferencesDialogImpl
from .DateDialogImpl import DateDialogImpl
from .FixtureDialogImpl import FixtureDialogImpl
from .OpenFavoriteFileDialogImpl import OpenFavoriteFileDialogImpl
from .OpenFileDialogImpl import OpenFileDialogImpl
from .OpeningSymbolDialogImpl import OpeningSymbolDialogImpl
from .PlaneReferencesDialogImpl import PlaneReferencesDialogImpl
from .RGBColorDialogImpl import RGBColorDialogImpl
from .SaveFavoriteFileDialogImpl import SaveFavoriteFileDialogImpl
from .SaveFileDialogImpl import SaveFileDialogImpl
from .SmartSymbolDialogImpl import SmartSymbolDialogImpl
from .SymbolDialogImpl import SymbolDialogImpl
from .TopPlaneReferencesDialogImpl import TopPlaneReferencesDialogImpl
from .TradeDialogImpl import TradeDialogImpl
from .ValueDialogType import ValueDialogType      # must imported after all impl, problem with isinstance check

class ValueDialogTypes():
    """ definition of the value dialog types
    """

    value_dialog_types_impl = {"attributeselection"       : AttributeSelectionDialogImpl("attributeselection"),
                               "attributeselectioninsert" : AttributeSelectionDialogImpl("attributeselectioninsert"),
                               "attributeselectionproject": AttributeSelectionDialogImpl("attributeselectionproject"),
                               "bitmapresourcedialog"     : BitmapResourceDialogImpl("bitmapresourcedialog"),
                               "bottomplanereferences"    : BottomPlaneReferencesDialogImpl("bottomplanereferences"),
                               "datedialog"               : DateDialogImpl("datedialog"),
                               "fixturedialog"            : FixtureDialogImpl("fixturedialog"),
                               "openfavoritefiledialog"   : OpenFavoriteFileDialogImpl("openfavoritefiledialog"),
                               "openfiledialog"           : OpenFileDialogImpl("openfiledialog"),
                               "planereferences"          : PlaneReferencesDialogImpl("planereferences"),
                               "rgbcolordialog"           : RGBColorDialogImpl("rgbcolordialog"),
                               "savefavoritefiledialog"   : SaveFavoriteFileDialogImpl("savefavoritefiledialog"),
                               "savefiledialog"           : SaveFileDialogImpl("savefiledialog"),
                               "symboldialog"             : SymbolDialogImpl("symboldialog"),
                               "smartsymboldialog"        : SmartSymbolDialogImpl("smartsymboldialog"),
                               "openingsymboldialog"      : OpeningSymbolDialogImpl("openingsymboldialog"),
                               "topplanereferences"       : TopPlaneReferencesDialogImpl("topplanereferences"),
                               "trade"                    : TradeDialogImpl("trade")
                              }

    @staticmethod
    def get_value_dialog_type_impl(value_dialog_type: str) -> (ValueDialogType | None):
        """ get the value dialog type

        Args:
            value_dialog_type: dialog type name

        Returns:
            dialog type implementation
        """

        if (value_dialog_type_impl := ValueDialogTypes.value_dialog_types_impl.get(value_dialog_type.lower())) is not None:
            return value_dialog_type_impl

        return None
