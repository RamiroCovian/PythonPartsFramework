""" implementation of the standard PythonPart unit test wrapper
"""

from typing import cast, Any

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil

from BuildingElementInput import BuildingElementInput
from HandleProperties import HandleProperties
from InputMode import InputMode

from TypeCollections import GeometryTyping
from TypeCollections.ModificationElementList import ModificationElementList

from TestHelper import TestUtil

from TestHelper.Mock.CoordinateInputMock import CoordinateInputMock
from TestHelper.Mock.CreateElementsMock import get_geometry_elements_text, get_elements_text, get_attributes_text, \
                                               set_use_create_elements_mock, get_elements_from_db, clear_model_elements
from TestHelper.Mock.PythonWpfPaletteMock import PythonWpfPaletteMock

from TestHelper.Mock import DialogFunctionsMocks

class StandardPythonPartUnitTestWrapper():
    """ implementation of the standard PythonPart unit test wrapper
    """

    def __init__(self,
                 relative_pyp_name    : str,
                 doc                  : AllplanEleAdapter.DocumentAdapter,
                 modification_ele_list: ModificationElementList = ModificationElementList(),
                 parameter_data       : (list[Any] | None)      = None):
        """ initialize

        Args:
            relative_pyp_name:     name of the pyp file including path relative to the ...\\etc folder
            doc:                   document of the Allplan drawing files
            modification_ele_list: list with the BaseElementAdapter of the modified elements
            parameter_data:        parameter data
        """

        self.doc            = doc
        self.clear_document = False

        self.build_ele_input = BuildingElementInput(cast(AllplanIFW.CoordinateInput, CoordinateInputMock(doc)),
                                                    AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + \
                                                    r"PythonPartsFramework\GeneralScripts")

        self.build_ele_input.start_input(AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + relative_pyp_name,
                                         [] if parameter_data is None else parameter_data, AllplanIFW.AddMsgInfo(),
                                         modification_ele_list.is_modification_element(), modification_ele_list,
                                         AllplanGeo.Matrix3D(),  AllplanGeo.Matrix3D(),
                                         AllplanEleAdapter.BaseElementAdapter(), False)

    def on_preview_draw(self):
        """ Handles the preview draw event
        """

        self.build_ele_input.on_preview_draw()


    def on_mouse_leave(self):
        """ Handles the mouse leave event
        """

        self.build_ele_input.on_mouse_leave()


    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any):
        """ Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """

        self.build_ele_input.modify_element_property(page, name, value)
        self.build_ele_input.palette_service.update_palette(-1, False)


    def on_control_event(self,
                         event_id                : int,
                         use_create_elements_mock: bool = True):
        """ create the element in Allplan

        Args:
            event_id:                 event id of the clicked button control
            use_create_elements_mock: use the mock function for the element creation state
        """

        clear_model_elements()

        set_use_create_elements_mock(use_create_elements_mock)

        self.build_ele_input.on_control_event(event_id)

        set_use_create_elements_mock(True)


    def process_mouse_click(self,
                            click_pnt: AllplanGeo.Point3D,
                            use_mock : bool = True):
        """ process a mouse button click

        Args:
            click_pnt: clicked point
            use_mock:  use the mock for the element creation state
        """

        set_use_create_elements_mock(use_mock)

        cast(CoordinateInputMock, self.build_ele_input.coord_input).SetInputPoint(click_pnt)

        self.build_ele_input.process_mouse_msg(513, AllplanGeo.Point2D(click_pnt), AllplanIFW.AddMsgInfo())

        set_use_create_elements_mock(True)


    def create_elements_in_db(self,
                              clear_document: bool = False):
        """ create the element in Allplan by using a mock

        Args:
            clear_document: clear the document if the object is deleted
        """

        if clear_document:
            self.clear_document = clear_document

        clear_model_elements()

        if self.build_ele_input.input_mode != InputMode.HandleSelect:
            self.build_ele_input.process_mouse_msg(513, AllplanGeo.Point2D(), AllplanIFW.AddMsgInfo())

        self.build_ele_input.on_cancel_function()


    def on_cancel_function(self):
        """ execute the on cancel function event
        """

        self.build_ele_input.on_cancel_function()


    def create_elements_in_db_by_api(self,
                                     clear_document: bool):
        """ create the element in Allplan by using the API

        Args:
            clear_document: clear the document if the object is deleted
        """

        if clear_document:
            self.clear_document = clear_document

        set_use_create_elements_mock(False)

        self.create_elements_in_db()

        set_use_create_elements_mock(True)


    @staticmethod
    def test_palette(compare_str: str):
        """ compare the palette controls text

        Args:
            compare_str: compare string
        """

        exclude_attrs = ["Ifc ID :", "Allright_Comp_ID", "Component ID :"]

        ctrl_strings = [ctrl_string for ctrl_string in PythonWpfPaletteMock.get_palette_controls_string().split("\n") \
                                    if next((False for exclude_attr in exclude_attrs if ctrl_string.startswith(exclude_attr)), True)]

        TestUtil.compare_element_strings("\n".join(ctrl_strings), compare_str, 39, True)


    @staticmethod
    def test_geometry(compare_str: str):
        """ compare the geometry elements text

        Args:
            compare_str: compare string
        """

        TestUtil.compare_element_strings(get_geometry_elements_text(),
                                         compare_str, 40)


    @staticmethod
    def test_elements(compare_str: str):
        """ compare the elements text

        Args:
            compare_str: compare string
        """

        TestUtil.compare_element_strings(get_elements_text(),
                                         compare_str, 40)


    def test_elements_from_db(self,
                              compare_str: str):
        """ compare the elements from database text

        Args:
            compare_str: compare string
        """

        elements = AllplanBaseEle.GetElements(AllplanBaseEle.ElementsSelectService.SelectAllElements(self.doc))

        TestUtil.compare_element_strings(str(elements),
                                         compare_str, 48)


    @staticmethod
    def test_model_geometry(elements   : list[AllplanEleAdapter.BaseElementAdapter],
                            compare_str: str):
        """ compare the elements model geometry

        Args:
            elements:    elements to compare
            compare_str: compare string
        """

        text = ""

        for element in elements:
            text += str(element.GetModelGeometry())

        TestUtil.compare_element_strings(text,
                                         compare_str, 46)


    @staticmethod
    def test_element_geometry(elements   : list[AllplanEleAdapter.BaseElementAdapter],
                              compare_str: str):
        """ compare the elements geometry

        Args:
            elements:    elements to compare
            compare_str: compare string
        """

        text = ""

        for element in elements:
            text += str(element.GetGeometry())

        TestUtil.compare_element_strings(text,
                                         compare_str, 48)


    @staticmethod
    def test_model_element_geometry(elements   : list[AllplanEleAdapter.BaseElementAdapter],
                                    compare_str: str):
        """ compare the model elements geometry

        Args:
            elements:    elements to compare
            compare_str: compare string
        """

        text = ""

        for element in elements:
            text += str(element.GetModelGeometry())

        TestUtil.compare_element_strings(text,
                                         compare_str, 54)

    @staticmethod
    def test_attributes(compare_str: str):
        """ compare the elements text

        Args:
            compare_str: compare string
        """

        TestUtil.compare_element_strings(get_attributes_text(),
                                         compare_str, 42)


    def set_selected_element(self,
                             sel_ele: AllplanEleAdapter.BaseElementAdapter):
        """ set the selected element

        Args:
            sel_ele: selected element
        """

        cast(CoordinateInputMock, self.build_ele_input.coord_input).SetSelectedElement(sel_ele)


    def set_selected_geometry_element(self,
                                      sel_geo_ele: GeometryTyping.CURVES):
        """ set the selected geometry element

        Args:
            sel_geo_ele: selected geometry element
        """

        cast(CoordinateInputMock, self.build_ele_input.coord_input).SetSelectedGeometryElement(sel_geo_ele)


    def set_selected_elements(self,
                              sel_elements: AllplanEleAdapter.BaseElementAdapterList):
        """ set the selected element

        Args:
            sel_elements: selected elements
        """

        script_object_interactor = self.build_ele_input.interactor.script_object_interactor

        script_object_interactor._MultiElementSelectInteractor__post_element_selection.SetSelectedElements(sel_elements)


    @staticmethod
    def set_attribute_id_for_button(attribute_id: int):
        """ set the attribute ID for the attribute button click

        Args:
            attribute_id: attribute ID
        """

        DialogFunctionsMocks.set_attribute_id_for_button(attribute_id)


    @staticmethod
    def get_elements_from_db()  -> AllplanEleAdapter.BaseElementAdapterList:
        """ get the created elements from the data base (in case of not used mock!)

        Returns:
            created elements
        """

        return get_elements_from_db()


    def get_handles(self) -> list[HandleProperties]:
        """ get the handles

        Returns:
            handles
        """

        return self.build_ele_input.handle_modi_service._HandleModificationService__handle_service.handles  # pylint: disable=protected-access # type: ignore


    def __del__(self):
        """ save the default favorite data """

        if self.clear_document:
            AllplanUtil.ClearUnitTestDocument()
