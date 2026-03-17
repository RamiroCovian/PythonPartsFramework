""" implementation of the XML data tree reader
"""

from xml.etree import ElementTree

import NemAll_Python_AllplanSettings as AllplanSettings

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementMaterialStringTable import BuildingElementMaterialStringTable
from ParameterProperty import ParameterProperty
from TraceService import TraceService, TraceLevel

from Utilities.GeneralConstants import GeneralConstants

from .XmlElementTreeUtil import XmlElementTreeUtil
from .XmlParameterSectionReader import XmlParameterSectionReader
from .XmlParameterTextReader import XmlParameterTextReader

class XmlDataTreeReader():
    """ implementation of the XML data tree reader
    """

    def __init__(self,
                 path: str):
        """ Initialization of class BuildingElementXML

        Args:
            path: path of the XML file
        """

        self.__local_str_table  = BuildingElementStringTable("", False, "")         # local table of this pyp file
        self.__global_str_table = BuildingElementStringTable("", False, "")         # global table for all pyp files

        self.persistent = ParameterProperty.Persistent.MODEL_AND_FAVORITE

        self.input_type       = ParameterProperty.InputType.OPTIONAL
        self.is_imperial_unit = AllplanSettings.ImperialUnitService.IsImperialUnit()
        self.is_visual_script = GeneralConstants.VISUAL_SCRIPTS_FOLDER_KEY in path.lower()


    def set_string_tables(self,
                          pyp_path        : str,
                          global_str_table: BuildingElementStringTable,
                          doc_ele         : ElementTree.ElementTree,
                          build_ele       : BuildingElement):
        """ Set local and global string tables

        Args:
            pyp_path:         path of the xml file
            global_str_table: the global string table.
            doc_ele:          document element
            build_ele:        building element with the parameter properties
        """

        language_file = XmlElementTreeUtil.get_tag_data(doc_ele,'LanguageFile', "Element")

        TraceService().trace(TraceLevel.LANGUAGE_FILE_NAME, "LanguageFile = ", language_file)

        language = global_str_table.get_language() if global_str_table.is_valid() else \
                   AllplanSettings.AllplanLocalisationService.AllplanLanguage()


        #----------------- create string table from numeric ids

        if language_file:
            if (ipos := language_file.lower().find("etc\\")) == 0:
                pyp_path = AllplanSettings.AllplanPaths.GetPythonPartsEtcPath() + language_file[ipos + 4:]

            else:
                ipos = pyp_path.rfind("\\")

                pyp_path = pyp_path[:ipos + 1] + (language_file[2:] if language_file.startswith(".") else language_file)

        self.__local_str_table = BuildingElementStringTable(pyp_path, True, language)

        self.__global_str_table = global_str_table

        build_ele.add_string_tables(self.__local_str_table, self.__global_str_table)


    def get_script_data(self,
                        doc_ele  : ElementTree.ElementTree,
                        build_ele: BuildingElement) -> str:
        """ get the script data

        Args:
            doc_ele:   document element
            build_ele: building element with the parameter properties

        Returns:
            sub elements file
        """

        if not (parameter := XmlElementTreeUtil.get_element(doc_ele, "Script")):
            return ""

        build_ele.script_name              = XmlElementTreeUtil.get_tag_data(parameter, 'Name')
        build_ele.script_uuid              = XmlElementTreeUtil.get_tag_data(parameter, 'Uuid')
        build_ele.title                    = XmlElementTreeUtil.get_tag_data(parameter, 'Title')
        build_ele.read_last_input          = XmlElementTreeUtil.get_bool_value(parameter, "ReadLastInput")
        build_ele.is_interactor            = XmlElementTreeUtil.get_bool_value(parameter, "Interactor")
        build_ele.geometry_expand          = XmlElementTreeUtil.get_tag_data(parameter, "GeometryExpand") in {"1", "True"}
        build_ele.vs_placement_point_input = XmlElementTreeUtil.get_bool_value(parameter, "VSPlacementPointInput")
        build_ele.vs_multi_placement       = XmlElementTreeUtil.get_bool_value(parameter, "VSMultiPlacement")
        build_ele.version                  = XmlElementTreeUtil.get_tag_data(parameter, 'Version')
        build_ele.show_favorite_buttons    = XmlElementTreeUtil.get_bool_value(parameter, "ShowFavoriteButtons", default_value = True)

        data_column_width = XmlElementTreeUtil.get_tag_data(parameter, "DataColumnWidth")

        build_ele.data_column_width = int(data_column_width) if data_column_width else 0

        sub_elements_file = XmlElementTreeUtil.get_tag_data(parameter, "SubElements")

        if (text_id := XmlElementTreeUtil.get_tag_data(parameter, 'TextId')) != "":
            if (tmp_val := XmlParameterTextReader.get_localisation(text_id, self.__local_str_table, self.__global_str_table)) != '':
                build_ele.title = tmp_val

        return sub_elements_file


    def get_pages_data(self,
                       global_material_str_table: BuildingElementMaterialStringTable,
                       doc_ele                  : ElementTree.ElementTree,
                       build_ele                : BuildingElement) -> BuildingElementControlProperties:
        """ get the data from the pages

        Args:
            global_material_str_table: global material string table
            doc_ele:                   document element
            build_ele:                 building element with the parameter properties

        Returns:
            control properties of the building element
        """

        # Extract page nodes <Page>...<\Page>

        build_ele_ctrl_props = BuildingElementControlProperties()


        #----------------- get the palette layout script

        build_ele_ctrl_props.palette_layout_script = XmlElementTreeUtil.get_tag_data(doc_ele, "PaletteLayoutScript",
                                                                                     allow_multiline_text = True)


        #----------------- get the data for the pages

        for page_index, page in enumerate(XmlElementTreeUtil.get_elements_by_tag_name(doc_ele, "Page")):
            name    = XmlElementTreeUtil.get_tag_data(page, "Name")
            visible = XmlElementTreeUtil.get_tag_data(page, "Visible", "Page", allow_multiline_text = True)
            enable  = XmlElementTreeUtil.get_tag_data(page, "Enable", "Page", allow_multiline_text = True)

            text = XmlParameterTextReader.get_prop_text(page, self.__local_str_table, self.__global_str_table,
                                                        self.is_visual_script, "Page") if name != GeneralConstants.HIDDEN_PAGE_KEY else ""


            #------------- set the global persistent state

            if name in {GeneralConstants.IN_MANDATORY_PAGE_KEY, GeneralConstants.IN_PAGE_KEY, GeneralConstants.OUT_PAGE_KEY,
                        GeneralConstants.IN_OUT_PAGE_KEY, GeneralConstants.IN_OPTIONAL_PAGE_KEY}:
                self.persistent = ParameterProperty.Persistent.NO

            elif name == GeneralConstants.HIDDEN_PAGE_KEY:
                self.persistent = ParameterProperty.Persistent.MODEL

            else:
                self.persistent = ParameterProperty.Persistent.MODEL_AND_FAVORITE


            #------------- set the input type

            if name == GeneralConstants.IN_MANDATORY_PAGE_KEY:
                self.input_type = ParameterProperty.InputType.MANDATORY
            else:
                self.input_type = ParameterProperty.InputType.OPTIONAL

            build_ele.add_page(name, text, visible, enable)

            param_section_reader = XmlParameterSectionReader(build_ele, build_ele_ctrl_props,
                                                             self.__local_str_table, self.__global_str_table,
                                                             self.persistent, self.input_type,
                                                             self.is_imperial_unit, self.is_visual_script)

            param_section_reader.execute(page, page_index, global_material_str_table)

        return build_ele_ctrl_props
