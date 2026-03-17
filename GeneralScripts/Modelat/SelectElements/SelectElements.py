import NemAll_Python_Utility as PythonUtility
import math
from typing import Any, List

from StringTableService import StringTableService
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeom
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter

from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
import subprocess


def check_allplan_version(build_ele: BuildingElement, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version

    # Support all versions
    return True


def create_element(build_ele: BuildingElement, doc):
    """ "
    Used to Preview
    """
    return ([], [])


# def create_interactor(coord_input: AllplanIFW.CoordinateInput, pyp_path: str, str_table_service):
def create_interactor(
    coord_input: AllplanIFW.CoordinateInput,
    pyp_path: str,
    str_table_service: StringTableService,
    build_ele_list: List,
    build_ele_composite: BuildingElementComposite,
    control_props_list: List,
    modify_uuid_list: List,
):
    """
    Start Interactor
    """

    return SelectElementsClass(coord_input, pyp_path, str_table_service)


class SelectElementsClass:
    def __init__(
        self, coord_input: AllplanIFW.CoordinateInput, pyp_path: str, str_table_service
    ):
        self.element_list = []
        self.coord_input = coord_input
        self.str_table_service = str_table_service
        self.build_ele_service = BuildingElementService()

        self.is_success = self.show_palette(pyp_path)
        if not self.is_success:
            return

        self.initPythonPart()

    def initPythonPart(self):
        """ "
        Turn on selection area in process_mouse_msg
        """
        self.element_list = []
        self.doc = self.coord_input.GetInputViewDocument()

        element_filter = AllplanIFW.ElementSelectFilterSetting(True)

        self.area = True
        display_text = "Select column(s) by left-click or area selection"
        self.post_element_selection = AllplanIFW.PostElementSelection()
        AllplanIFW.InputFunctionStarter.StartElementSelect(
            display_text,
            element_filter,
            self.post_element_selection,
            True,
            AllplanIFW.SelectionMode.eSelectSubObject,
        )

    def show_palette(self, pyp_path) -> bool:
        (
            result,
            self.build_ele_script,
            self.build_ele_list,
            self.control_props_list,
            self.build_ele_composite,
            part_name,
            self.file_name,
        ) = self.build_ele_service.read_data_from_pyp(
            pyp_path + "\\SelectElements.pyp",
            self.str_table_service.str_table,
            False,
            self.str_table_service.material_str_table,
        )

        if not result:
            return False

        self.palette_service = BuildingElementPaletteService(
            self.build_ele_list,
            self.build_ele_composite,
            self.build_ele_script,
            self.control_props_list,
            self.file_name,
        )

        self.palette_service.show_palette(part_name)

        return True

    def process_mouse_msg(
        self, mouse_msg: int, pnt: AllplanGeom.Point2D, msg_info: AllplanIFW.AddMsgInfo
    ) -> bool:

        if not bool(self.element_list):
            self.element_list = [
                element
                for element in self.post_element_selection.GetSelectedElements(self.doc)
            ]

            list_adapters = AllplanElementAdapter.BaseElementAdapterList()

            for elem in self.element_list:
                msg = self.get_msg(elem)
                PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OK)
                list_adapters.append(elem)

                # Append attribute
                thisElem = AllplanElementAdapter.BaseElementAdapterList()
                thisElem.append(elem)
                AllplanBaseElements.ElementsAttributeService.ChangeAttribute(2447, 'TEST', thisElem)

            AllplanIFW.HighlightService.HighlightElements(list_adapters)

            return True

        self.initPythonPart()

        return True

    def get_msg(self, elem: AllplanElementAdapter.BaseElementAdapter):
        msg = ""
        msg += f"Name:                {str(elem.GetDisplayName())}\n"

        layer = elem.GetCommonProperties().Layer
        id_doc = self.coord_input.GetInputViewDocument().GetDocumentID()
        msg += f"Layer:                {str(AllplanBaseElements.LayerService.GetShortNameByID(layer, id_doc))}\n"

        msg += "Drawing file number: " + str(elem.GetDrawingfileNumber()) + "\n"
        msg += "Element adapter type:" + str(elem.GetElementAdapterType().GetTypeName()) + "\n"
        msg += "Model element UUID:  " + str(elem.GetModelElementUUID()) + "\n"
        msg += "Is 3D element:       " + str(elem.Is3DElement()) + "\n"

        msg += "TYPE: " + str(elem.GetArchElementType()) + "\n"

        msg += "SolidGeom: " + str(elem.GetGeometry()) + "\n"
        msg += "SolidGeom2: " + str(elem.GetModelGeometry()) + "\n"

        msg += "Geom: " + str(elem.GetGroundViewArchitectureElementGeometry()) + "\n"

        msg += "3DArchGeom: " + str(elem.GetPureArchitectureElementGeometry()) + "\n"

        msg += "Attributes:" + "\n"
        for attribute in elem.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAll):
            msg += "\t" + str(attribute[0]) + " " + str(AllplanBaseElements.AttributeService.GetAttributeName(self.doc, attribute[0])) + "=" + str(attribute[1]) + "\n"

        return msg

    def on_cancel_function(self) -> bool:
        """Cancel the input function

        Returns:
            True/False for success.
        """
        if self.is_success:
            self.palette_service.close_palette()

        return True

    def on_mouse_leave(self):
        """Handles the mouse leave event"""
        self.on_preview_draw()

    def on_preview_draw(self):
        """Handles the preview draw event"""
        pass

    def modify_element_property(self, page: int, name: str, value: Any):
        """
        Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """

        update_palette = self.palette_service.modify_element_property(page, name, value)

        if update_palette:
            self.palette_service.update_palette(-1, False)
