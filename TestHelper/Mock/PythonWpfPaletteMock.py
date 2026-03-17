""" implementation of the mock class for PythonWpfPaletteBuilder.
"""

# pylint: disable=missing-function-docstring
# pylint: disable=global-statement
# pylint: disable=invalid-name
# pylint: disable=too-many-public-methods
# pylint: disable=no-self-use
# pylint: disable=missing-return-doc

from typing import cast

import unittest

import NemAll_Python_Palette as AllplanPalette

PALETTE_CONTROL_STRINGS = []

CURRENT_EXPANDER_NAME = ""
CURRENT_ROW_NAME      = ""


class PythonWpfPaletteBuilderMock(unittest.TestCase):
    """ implementation of the mock class for PythonWpfPaletteBuilder """

    def add_expander(self, expander_name):
        global CURRENT_EXPANDER_NAME, CURRENT_ROW_NAME

        if CURRENT_EXPANDER_NAME == expander_name:
            return

        CURRENT_EXPANDER_NAME = expander_name

        if expander_name:
            PALETTE_CONTROL_STRINGS.append(expander_name)

        CURRENT_ROW_NAME = ""


    def add_control(self, row_name, text, value_name, value_str):
        global CURRENT_ROW_NAME

        if row_name  and  row_name == CURRENT_ROW_NAME:
            PALETTE_CONTROL_STRINGS[-1] += "; " + value_name + " = " + value_str

            return

        CURRENT_ROW_NAME = row_name

        if row_name:
            PALETTE_CONTROL_STRINGS.append(row_name + " : " + value_name + " = " + value_str)
        else:
            text = text.strip()

            PALETTE_CONTROL_STRINGS.append(text + " : " + value_name + " = " + value_str)


    def AddPage(self, _page_name, _page_text):
        return


    def AddSeparator(self, _page, expander_name):
        self.add_expander(expander_name)


    def AddLengthValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _min_value, _max_value, _interval_value, _as_slider,
                       _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddAngleValue(self, text, name, value,
                      _page, expander_name, row_name, _is_control_enabled,
                      _min_value, _max_value, _interval_value, _as_slider,
                      _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddDoubleValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _min_value, _max_value, _interval_value, _as_slider,
                       _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddIntValue(self, text, name, value,
                    _page, expander_name, row_name, _is_control_enabled,
                    _min_value, _max_value, _interval_value, _as_slider,
                    _height, _width, _font_face_code, _background_color):
        if not isinstance(value,int):
            self.assertTrue(isinstance(value,int))

        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddAreaValue(self, text, name, value,
                     _page, expander_name, row_name, _is_control_enabled,
                     _min_value, _max_value, _interval_value, _as_slider,
                     _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddVolumeValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _min_value, _max_value, _interval_value, _as_slider,
                       _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddWeightValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _min_value, _max_value, _interval_value, _as_slider,
                       _height, _width, _font_face_code, _background_color):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddStringValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code, _background_color):
        if not isinstance(value,str):
            self.assertTrue(isinstance(value,int))

        self.add_expander(expander_name)
        self.add_control(row_name, text, name, value)


    def AddText(self, text, value, _orientation,
                _page, expander_name, row_name, _is_control_enabled,
                _height, _width, _font_size, _face_code):
        if not isinstance(value, str):
            self.assertTrue(isinstance(value,int))

        self.add_expander(expander_name)
        self.add_control(row_name, text, "", value)


    def AddLayer(self, text, name, value,
                 _page, expander_name, row_name, _is_control_enabled,
                 _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPenValue(self, text, name, value,
                    _page, expander_name, row_name, _is_control_enabled,
                    _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddStroke(self, text, name, value,
                  _page, expander_name, row_name, _is_control_enabled,
                  _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddColorValue(self, text, name, value,
                      _page, expander_name, row_name, _is_control_enabled,
                      _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddFaceStyleValue(self, text, name, value,
                          _page, expander_name, row_name, _is_control_enabled,
                          _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddHatchValue(self, text, name, value,
                      _page, expander_name, row_name, _is_control_enabled,
                      _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPatternValue(self, text, name, value,
                        _page, expander_name, row_name, _is_control_enabled,
                        _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddComboBoxValue(self, text, name, value, _value_list, _ctrl_type, _value_type,
                         _page, expander_name, row_name, _is_control_enabled,
                         _height, _width, _font_face_code, _background_color, _isEditable):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddCheckboxValue(self, text, name, value,
                         _page, expander_name, row_name, _is_control_enabled,
                         _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, "True" if value == 1 else "False")


    def AddMaterialButton(self, text, name, value, _selected_value,
                          _page, expander_name, row_name, _is_control_enabled,
                          _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddMultiMaterialLayoutCatalogRef(self, text, name, value, _selected_value,
                                         _page, expander_name, row_name, _is_control_enabled,
                                         _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPicture(self, text, name, picture_name, _lib_path, orientation, _page, expander_name, row_name):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, f"{picture_name} - {orientation}")

    def AddResourcePicture(self, description: str, name: str, picture_resource_id: int, _page: int, expander_name: str, row_name: str,
                           _height: int, _width: int):
        self.add_expander(expander_name)
        self.add_control(row_name, description, name, str(picture_resource_id))

    def AddRadioButton(self, _group_text, group_name, text, value, _selected_value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, group_name, str(value))


    def AddButton(self, text, name, event_id,
                  _page, expander_name, row_name, _is_control_enabled,
                  _height, _width, _font_style, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(event_id))

    def AddRefPointButton(self, text, name, event_id, _ref_pnt_type,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(event_id))


    def AddPictureButtonList(self, text, name, value, _picture_path, _picture_list, _value_list, _text_list,
                             _page, expander_name, row_name, _is_control_enabled,
                             _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPictureResourceToggleButton(self, text, name, value, _picture_list, _value_list, _text_list,
                                       _page, expander_name, row_name, _is_control_enabled,
                                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddPictureResourceButtonList(self, text, name, value, _picture_list, _value_list, _text_list,
                                     _page, expander_name, row_name, _is_control_enabled,
                                     _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddPictureComboBox(self, text, name, value, _picture_path, _picture_list, _value_list, _text_list,
                           _page, expander_name, row_name, _is_control_enabled,
                           _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPictureResourceComboBox(self, text, name, value, _picture_list, _value_list, _text_list,
                                   _page, expander_name, row_name, _is_control_enabled,
                                   _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddPictureResourceButton(self, text, name, _value, event_id,
                                 _page, expander_name, row_name, _is_control_enabled,
                                 _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(event_id))


    def AddPictureButton(self, text, name, _value, event_id,
                         _page, expander_name, row_name, _is_control_enabled,
                         _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(event_id))


    def AddBarDiameter(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddMeshType(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled, _mesh_group,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddMeshGroup(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddConcreteCoverValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddBendingRollerValue(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddSteelGrade(self, text, name, value,
                       _page, expander_name, row_name, _is_control_enabled,
                       _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddConcreteGrade(self, text, name, value,
                         _page, expander_name, row_name, _is_control_enabled,
                         _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def AddFixtureValues(self, path, _file, _entry, name, value,
                         _page, expander_name, row_name, _is_control_enabled,
                         _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, path.split(" ")[0] , name, str(value))

    def AddPointFixtureCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled,
                                  _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddFactoryCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddPrecastElementTypeCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddConcreteGradeCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddInsulationCatalogRef(self, text, name, value,
                                _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddBrickTileCatalogRef(self, text, name, value,
							   _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddNormCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddSurfaceCatalogRef(self, text, name, value,
                                  _page, expander_name, row_name, _is_control_enabled):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))

    def AddPlaneReferencesButton(self, text, name, value,
                                 _page, expander_name, row_name, _is_control_enabled,
                                 _height, _width, _font_face_code):
        self.add_expander(expander_name)
        self.add_control(row_name, text, name, str(value))


    def IsConcreteCoverPaletteUpdate(self, _cover) -> bool:
        return True


class PythonWpfPaletteMock():
    """ implementation of the mock class for PythonWpfPaletteMock """

    @staticmethod
    def reset_globals():
        global CURRENT_EXPANDER_NAME
        global CURRENT_ROW_NAME

        PALETTE_CONTROL_STRINGS.clear()

        CURRENT_EXPANDER_NAME = ""
        CURRENT_ROW_NAME      = ""

    def __init__(self):
        self.reset_globals()

    def GetPythonWpfPaletteBuilder(self) -> AllplanPalette.PythonWpfPaletteBuilder:
        """  get the palette builder

        Returns:
            palette builder
        """
        self.reset_globals()

        return cast(AllplanPalette.PythonWpfPaletteBuilder, PythonWpfPaletteBuilderMock())


    def Open(self, _1, _2, _3, _4, _5, _6, _7):

        return


    def Close(self):
        return


    def Reset(self, _ = ""):
        self.reset_globals()


    def UpdateDialogData(self, _):
        return

    def EnableControl(self, _name, _i_page, _enabled):
        return

    @staticmethod
    def get_palette_controls_string() -> str:
        """ get the control strings of the palette

        Returns:
            palette control strings
        """

        ctrl_string = ""

        for ctrl in PALETTE_CONTROL_STRINGS:
            ctrl_string += ctrl + "\n"

        return ctrl_string
