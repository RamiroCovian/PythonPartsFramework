""" This script generates library preview for PythonPart
"""

# pylint: disable=bare-except
# pylint: disable=not-callable

from typing import Tuple, Any

import sys
import traceback

import dataclasses

# pylint: disable=unused-import
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter              # needed for document (call from C++)
# pylint: enable=unused-import

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_AllplanSettings as AllplanSettings

from BuildingElementUtil import BuildingElementUtil
from BuildingElementService import BuildingElementService
from BuildingElementMaterialStringTable import BuildingElementMaterialStringTable
from BuildingElementStringTable import BuildingElementStringTable
from ControlPropertiesUtil import ControlPropertiesUtil
from DocumentManager import DocumentManager
from TraceService import TraceService
from DeleteObsoleteFiles import delete_obsolete_files
from ImportHook import ImportHookFinder

sys.meta_path.append(ImportHookFinder)

def create_library_preview(file_name: str,
                           document : AllplanEleAdapter.DocumentAdapter) -> Tuple[bool, Any]:
    """ Create preview objects for PythonPart

    Args:
        file_name: the name of the XML file.
        document:  the document adapter.

    Returns:
        created preview state, created script
    """

    TraceService(True)

    delete_obsolete_files()

    DocumentManager.get_instance().document = document
    DocumentManager.get_instance().clear_pythonpart_element()

    modification_ele_list = []

    path                       = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath()
    string_table_path          = path + '\\PythonPartsFramework\\GeneralScripts\\Stringtable\\BuildingElement.pyp'
    material_string_table_path = path + '\\PythonPartsFramework\\GeneralScripts\\Stringtable\\BuildingElementMaterial.pyp'

    language = AllplanSettings.AllplanLocalisationService.AllplanLanguage()

    str_table          = BuildingElementStringTable(string_table_path, False, language)
    material_str_table = BuildingElementMaterialStringTable(material_string_table_path, False, language)


    #------------------ Read the building element

    result, build_ele_script, build_ele_list, control_props_list, build_ele_composite, _, file_name = \
        BuildingElementService().read_data_from_pyp(file_name, str_table, True, material_str_table)

    if not result or not build_ele_script or not build_ele_list or not control_props_list:
        return False, build_ele_script


    #------------------ Import the script

    build_element_script = BuildingElementUtil.import_building_element_script(build_ele_list[0], False)

    if (init_ctrl__prop := getattr(build_element_script, "initialize_control_properties", None)) is not None:
        try:
            if build_ele_list and len(build_ele_list) == 1:
                init_ctrl__prop(build_ele_list[0],ControlPropertiesUtil(control_props_list, build_ele_list), document)
            else:
                init_ctrl__prop(build_ele_list, ControlPropertiesUtil(control_props_list, build_ele_list), document)

        except:
            traceback.print_exc()


    #------------------ Execute the element creation

    try:
        preview_element_list = None

        if (preview_fct := getattr(build_element_script, "create_preview", None)):
            if len(build_ele_list) > 1:
                if build_ele_list[0].script_name.lower() != "nodescript.py":
                    build_ele_composite.connect_building_element_values(build_ele_list)

                preview_element_list = preview_fct(build_ele_list, build_ele_composite, document)
            else:
                preview_element_list = preview_fct(build_ele_list[0], document)

        elif (create_element := getattr(build_ele_script, "create_element", None)):
            if len(build_ele_list) == 1 and build_element_script is not None:
                preview_element_list = create_element(build_ele_list[0], document)

            elif build_element_script is not None:
                build_ele_composite.connect_building_element_values(build_ele_list)

                preview_element_list = create_element(build_ele_list, build_ele_composite, document)

    except:
        traceback.print_exc()

        return False, build_ele_script


    #------------------ Create element in document

    if not preview_element_list:
        return False, build_element_script

    if dataclasses.is_dataclass(preview_element_list):
        AllplanBaseEle.CreateElements(document, AllplanGeo.Matrix3D(), preview_element_list.elements,
                                      modification_ele_list, None)

    elif isinstance(preview_element_list[0], list):
        AllplanBaseEle.CreateElements(document, AllplanGeo.Matrix3D(), preview_element_list[0],
                                      modification_ele_list, None)

    else:
        return False, build_element_script

    return True, build_element_script
