""" Script for BuildingElementXML
"""

import os

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementMaterialStringTable import BuildingElementMaterialStringTable
from BuildingElementValueConstraint import BuildingElementValueConstraint
from BuildingElementXMLInclude import BuildingElementXMLInclude
from FileNameService import FileNameService
from TraceService import TraceService, TraceLevel

from Utilities.GeneralConstants import GeneralConstants

from ValueTypes.ValueTypeUtils.ValueType import ValueType

from XMLReader.XmlConstantsReader import XmlConstantsReader
from XMLReader.XmlDataTreeReader import XmlDataTreeReader
from XMLReader.XmlElementTreeUtil import XmlElementTreeUtil
from XMLReader.XmlReinforcementReader import XmlReinforcementReader

class BuildingElementXML():
    """    Definition of class BuildingElementXML
    """

    @staticmethod
    def read_element_parameter(pyp_path          : str,
                               global_str_table  : BuildingElementStringTable         = BuildingElementStringTable("", False, ""),
                               material_str_table: BuildingElementMaterialStringTable = BuildingElementMaterialStringTable("", False, "")) \
                               -> tuple[BuildingElement, BuildingElementControlProperties, str]:
        """ Read the element parameter from XML file global_str_table

        Args:
            pyp_path:           the path to XML file.
            global_str_table:   the global string table.
            material_str_table: material string table

        Returns:
            a tuple with (the building element with parsed parameters, control data, sub elements file)
        """

        path = pyp_path

        TraceService().trace(TraceLevel.PYP_FILE_NAME, "Read pyp file: ", path)


        #----------------- set and get the path data

        build_ele = BuildingElement()

        build_ele.pyp_file_name = FileNameService.get_lib_pyp_sricpt_path(path)
        build_ele.pyp_file_path = os.path.split(path)[0]

        if GeneralConstants.VISUAL_SCRIPTS_FOLDER_KEY not in path.lower():
            path = BuildingElementXMLInclude.get_final_pyp_file(path)


        #----------------- read the XML document

        doc_ele = XmlElementTreeUtil.parse(path)

        xml_data_tree_reader = XmlDataTreeReader(path)

        xml_data_tree_reader.set_string_tables(pyp_path, global_str_table, doc_ele, build_ele)


        #----------------- get the data

        sub_elements_file = xml_data_tree_reader.get_script_data(doc_ele, build_ele)

        XmlConstantsReader.exeute(doc_ele, build_ele, build_ele.get_string_tables()[0])

        build_ele_ctrl_props = xml_data_tree_reader.get_pages_data(material_str_table, doc_ele, build_ele)

        XmlReinforcementReader.execute(doc_ele, build_ele)

        build_ele.add_material_string_table(material_str_table)

        BuildingElementValueConstraint.check_property_constraint_init(build_ele, build_ele_ctrl_props)

        ValueType.reset_reload()

        return (build_ele, build_ele_ctrl_props, sub_elements_file)
