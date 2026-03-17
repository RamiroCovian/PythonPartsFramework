import NemAll_Python_Utility as PythonUtility
import math
from typing import Any, List


from StringTableService import StringTableService
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeom
import NemAll_Python_IFW_Input as AllplanIFWInput
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter

from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService


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


# def create_interactor(coord_input: AllplanIFWInput.CoordinateInput, pyp_path: str, str_table_service):
def create_interactor(
    coord_input: AllplanIFWInput.CoordinateInput,
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

    return GetElementsClass(coord_input, pyp_path, str_table_service)


class GetElementsClass:
    def __init__(
        self, coord_input: AllplanIFWInput.CoordinateInput, pyp_path: str, str_table_service
    ):

        self.coord_input = coord_input
        self.str_table_service = str_table_service
        self.build_ele_service = BuildingElementService()

        self.is_success = self.show_palette(pyp_path)
        if not self.is_success:
            return

        # elems1 = AllplanBaseElements.ElementsByAttributeService.GetInstance().GetElements(1442)

        self.doc = self.coord_input.GetActiveViewDocument()
        inputDoc = self.coord_input.GetInputViewDocument()

        activeName = AllplanElementAdapter.DocumentNameService.GetActiveDocumentName()
        print("Active DOC: " + activeName)
        print("Active DOC ID: " + str(self.doc.GetDocumentID()))
        print("Input DOC ID: " + str(inputDoc.GetDocumentID()))
        print("Input DOC ID (2): " + str(self.coord_input.GetInputViewDocumentID()))

        print("ALL LOADED DOCS:")
        allDocs = AllplanElementAdapter.DocumentNameService.GetLoadedDocumentsNameData()
        for doc in allDocs:
            print(" " + str(doc[1]) + " - " + doc[0])
        print("\n")

        elems = AllplanElementAdapter.BaseElementAdapterList(
            AllplanBaseElements.ElementsSelectService.SelectAllElements(self.doc)
        )

        walls = filter(self.GetWalls, elems)
        for wall in walls:
            msg = self.get_msg(wall)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_blaus = filter(lambda elem: self.GetTubs(elem, "BLAU"), elems)
        for tub in tubs_blaus:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_rosa = filter(lambda elem: self.GetTubs(elem, "ROSA"), elems)
        for tub in tubs_rosa:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_verd = filter(lambda elem: self.GetTubs(elem, "VERD"), elems)
        for tub in tubs_verd:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_taronja = filter(lambda elem: self.GetTubs(elem, "TARONJA"), elems)
        for tub in tubs_taronja:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_marro = filter(lambda elem: self.GetTubs(elem, "MARRO"), elems)
        for tub in tubs_marro:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        tubs_lila = filter(lambda elem: self.GetTubs(elem, "LILA"), elems)
        for tub in tubs_lila:
            msg = self.get_msg(tub)
            res = PythonUtility.ShowMessageBox(msg, PythonUtility.MB_OKCANCEL)
            if res == PythonUtility.IDCANCEL:
                return

        return

    def GetTubs(self, elem: AllplanElementAdapter.BaseElementAdapter, tipus: str):
        attrs = elem.GetAttributes(AllplanBaseElements.eAttibuteReadState.ReadAll)
        attrsA = filter(lambda attr: "TUB " + tipus in str(attr[1]), attrs)

        for attrA in attrsA:
            return True

        return False

    def GetWalls(self, elem: AllplanElementAdapter.BaseElementAdapter):
        # a7fae808-845c-4491-9f44-3757c493e673
        if (
            AllplanElementAdapter.WallTier_TypeUUID
            == elem.GetElementAdapterType().GetGuid()
        ):
            return True

        return False

    def get_msg(self, elem: AllplanElementAdapter.BaseElementAdapter):
        msg = ""
        msg += "Name:                " + str(elem.GetDisplayName()) + "\n"
        msg += "Drawing file number: " + str(elem.GetDrawingfileNumber()) + "\n"
        msg += (
            "Element adapter type:"
            + str(elem.GetElementAdapterType().GetTypeName())
            + "\n"
        )
        msg += "Model element UUID:  " + str(elem.GetModelElementUUID()) + "\n"
        msg += "Is 3D element:       " + str(elem.Is3DElement()) + "\n\n"

        elemDoc = elem.GetDocument()
        msg += "Document:            " + AllplanElementAdapter.DocumentNameService.GetDocumentName(elem, True, True, " - ") + "\n\n"
        msg += "Document ID:         " + str(elemDoc.GetDocumentID()) + "\n\n"


        # msg += "Geometry:" + "\n"
        # modelGeom3D = elem.GetModelGeometry()
        # msg += str(modelGeom3D) + "\n"

        msg += "Attributes:" + "\n"
        for attribute in elem.GetAttributes(
            AllplanBaseElements.eAttibuteReadState.ReadAll
        ):
            if "TUB " in str(attribute[1]):
                msg += (
                    "\t"
                    + str(attribute[0])
                    + " "
                    + str(
                        AllplanBaseElements.AttributeService.GetAttributeName(
                            self.doc, attribute[0]
                        )
                    )
                    + "="
                    + str(attribute[1])
                    + "\n"
                )

        return msg

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
            pyp_path + "\\GetElements.pyp",
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
        self, mouse_msg: int, pnt: AllplanGeom.Point2D, msg_info: AllplanIFWInput.AddMsgInfo
    ) -> bool:
        return True

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
