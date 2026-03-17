""" implementation of the parameter reader
"""

from typing import cast

from xml.etree import ElementTree

import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementMaterialStringTable import BuildingElementMaterialStringTable
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementXMLValue import BuildingElementXMLValue
from ControlProperties import ControlProperties
from ParameterProperty import ParameterProperty

from DialogTypes.FileDialog import FileDialog
from DialogTypes.ValueDialogTypes import ValueDialogTypes

from Utilities.AttributeIdEnums import AttributeIdEnums
from Utilities.GeneralConstants import GeneralConstants
from Utilities.SplitUtil import SplitUtil

from ValueTypes.ParameterPropertyValueType import ParameterPropertyValueType
from ValueTypes.ParameterPropertyValueTypesImpl import ParameterPropertyValueTypesImpl

from .IncludeData import IncludeData
from .XmlParameterReaderUtil import XmlParameterReaderUtil
from .XmlParameterTextReader import XmlParameterTextReader
from .XmlParameterValueReader import XmlParameterValueReader
from .XmlElementTreeUtil import XmlElementTreeUtil
from .XmlStringToValueConverter import XmlStringToValueConverter
from .XmlParentParameterData import XmlParentParameterData

class XmlParameterReader():
    """ implementation of the parameter reader
    """

    @staticmethod
    def get_parameter_property(param             : ElementTree.Element,
                               value_type        : str,
                               persistent        : ParameterProperty.Persistent,
                               input_type        : ParameterProperty.InputType,
                               is_visual_script  : bool,
                               build_ele         : BuildingElement,
                               local_str_table   : BuildingElementStringTable,
                               global_str_table  : BuildingElementStringTable,
                               material_str_table: BuildingElementMaterialStringTable,
                               is_imperial_unit  : bool,
                               name_postfix      : str) -> ParameterProperty:
        """ get the parameter property

        Args:
            param:              parameter
            value_type:         value type
            persistent:         persistent state
            input_type:         input type
            is_visual_script:   visual script state
            build_ele:          building element with the parameter properties
            local_str_table:    local string table
            global_str_table:   global string table
            material_str_table: material string table
            is_imperial_unit:   imperial unit state
            name_postfix:       name postfix

        Returns:
            parameter property
        """

        list_state = XmlElementTreeUtil.get_tag_data(param, "ListState")

        if (attribute_id := XmlElementTreeUtil.get_tag_data(param, "AttributeId")):
            attribute_id = eval(attribute_id, {"AttributeIdEnums": AttributeIdEnums})

            if isinstance(attribute_id, list):
                attribute_id = f"[{','.join([str(int(item)) for item in attribute_id])}]"

            else:
                attribute_id = str(int(attribute_id))


        #----------------- read the parameter property data

        param_prop                   = ParameterProperty()
        param_prop.value_type        = BuildingElementXMLValue.get_property_palette_value_type(
                                                               ParameterPropertyValueTypesImpl.get_value_type_impl(value_type))
        param_prop.name              = f"{XmlElementTreeUtil.get_tag_data(param, 'Name')}{name_postfix}"
        param_prop.dimensions        = XmlElementTreeUtil.get_tag_data(param, "Dimensions")
        param_prop.attribute_id_str  = attribute_id or "0"
        param_prop.list_state        = int(list_state) if list_state else 0
        param_prop.list_reverse      = XmlElementTreeUtil.get_bool_value(param, "ListReverse")
        param_prop.list_squeeze      = XmlElementTreeUtil.get_tag_data(param, "ListSqueeze").lower() in {"", "true"}
        param_prop.exclude_identical = XmlElementTreeUtil.get_bool_value(param, "ExcludeIdentical")

        param_prop.persistent = persistent if param_prop.value_type.is_persistent else ParameterProperty.Persistent.NO

        param_prop.input_type = input_type


        #----------------- get the persistence

        if is_visual_script and param_prop.name in {"CreateModelObjects", "CreateModelPreviewObjects",
                                                    "CreateHandles", "NumberPoints"}:
            param_prop.persistent = ParameterProperty.Persistent.NO

        if (persistent_data := XmlElementTreeUtil.get_tag_data(param, "Persistent")):
            param_prop.persistent = cast(ParameterProperty.Persistent, getattr(ParameterProperty.Persistent, persistent_data.upper(),
                                                                               param_prop.persistent))


        #----------------- get the data for the namedtuple

        if param_prop.value_type.is_tuple_type(True):
            param_prop.set_named_tuple_def(XmlElementTreeUtil.get_tag_data(param, "TypeName"),
                                           SplitUtil.split_string_with_bracket_parts(
                                           XmlElementTreeUtil.get_tag_data(param, "FieldNames").replace("\n", "").
                                                                                                    replace(" ", ""), ","))

        #----------------- get the value

        value_str = XmlParameterValueReader.get_value_str(param, value_type, local_str_table, global_str_table,
                                                          is_imperial_unit, build_ele)

        if param_prop.input_type == ParameterProperty.InputType.MANDATORY:
            param_prop.value = None
        else:
            param_prop.value = XmlStringToValueConverter.get_value(build_ele,
                                                                   param_prop.value_type, value_str,
                                                                   param_prop.named_tuple_def,
                                                                   param_prop.attribute_id,
                                                                   local_str_table,
                                                                   material_str_table)

        return param_prop


    @staticmethod
    def get_control_properties(param            : ElementTree.Element,
                               local_str_table  : BuildingElementStringTable,
                               global_str_table : BuildingElementStringTable,
                               is_visual_script : bool,
                               is_imperial_unit : bool,
                               build_ele        : BuildingElement,
                               page_index       : int,
                               parent_param_data: XmlParentParameterData,
                               param_prop       : ParameterProperty,
                               include_data     : IncludeData) -> ControlProperties:
        """ get the control properties

        Args:
            param:             parameter
            local_str_table:   local string table
            global_str_table:  global string table
            is_visual_script:  visual script state
            is_imperial_unit:  imperial unit state
            build_ele:         building element with the parameter properties
            page_index:        page index
            parent_param_data: data of the parent parameter
            param_prop:        parameter property
            include_data:      description

        Returns:
            control properties
        """

        value_type = param_prop.value_type

        text                 = XmlParameterTextReader.get_prop_text(param, local_str_table, global_str_table,
                                                                    is_visual_script).replace("#", include_data.text_postfix)
        value_str            = XmlParameterValueReader.get_value_str(param, value_type, local_str_table, global_str_table,
                                                                     is_imperial_unit, build_ele)
        enable_condition     = XmlElementTreeUtil.get_tag_data(param, "Enable", allow_multiline_text = True)
        visible_condition    = XmlParameterReaderUtil.get_visible(param, param_prop.name, include_data)
        event_id             = XmlElementTreeUtil.get_tag_data(param, 'EventId')
        value_index_name     = XmlElementTreeUtil.get_tag_data(param, 'ValueIndexName')
        value_list_start_row = XmlElementTreeUtil.get_tag_data(param, 'ValueListStartRow')
        value_dialog         = XmlElementTreeUtil.get_tag_data(param, 'ValueDialog')
        as_slider            = XmlElementTreeUtil.get_bool_value(param, 'ValueSlider')
        height               = XmlElementTreeUtil.get_str_value(param, "HeightInRow", "22")
        width                = XmlElementTreeUtil.get_str_value(param, "WidthInRow", str(value_type.get_default_control_width()))
        font_style           = XmlElementTreeUtil.get_int_value(param, "FontStyle", 2)
        font_face_code       = XmlElementTreeUtil.get_int_value(param, "FontFaceCode", 0)
        background_color     = XmlElementTreeUtil.get_tag_data(param, "BackgroundColor", allow_multiline_text = True)

        value_text_list = ""

        param_prop.enum_dict, value_list = XmlParameterValueReader.get_enum_dict(param)

        if not value_list:
            value_list = XmlParameterValueReader.get_value_list(param, value_type, local_str_table, global_str_table)

        if value_list:
            value_text_list, text = XmlParameterValueReader.get_value_text_list(param, text, value_type,
                                                                                value_list.count(GeneralConstants.TEXT_SEPARATOR) + 1,
                                                                                local_str_table, global_str_table)

        value_list_2       = XmlParameterValueReader.get_value_list_2(param)
        value_list_textids = XmlElementTreeUtil.get_tag_data(param, 'ValueList_TextIds')

        if include_data.is_include:
            enable_condition = XmlParameterReaderUtil.insert_name_postfix(enable_condition, include_data.name_postfix)


        #----------------- get the row state

        if not (row_name:= parent_param_data.row_name) and XmlElementTreeUtil.get_bool_value(param, 'XYZinRow'):
            row_name = param_prop.name + GeneralConstants.XYZ_IN_ROW_KEY


        #----------------- set the value dialog data

        value_dialog_impl = None

        if value_dialog:
            if (value_dialog_impl := ValueDialogTypes.get_value_dialog_type_impl(value_dialog)) is None:
                AllplanUtil.ShowMessageBox(f"No input dialog found for :{value_dialog}",  AllplanUtil.MB_OK)

            elif isinstance(value_dialog_impl, FileDialog):
                param_prop.value = value_dialog_impl.expand_value_string(param_prop.value)

                value_list   = XmlElementTreeUtil.get_tag_data(param, 'FileFilter')
                value_list_2 = f"{XmlElementTreeUtil.get_tag_data(param, 'FileExtension')}|" \
                                "{XmlElementTreeUtil.get_tag_data(param, 'DefaultDirectories').lower()}"

        ctrl_prop = ControlProperties(text, param_prop.name, enable_condition, visible_condition,
                                      page_index, parent_param_data.expander_name, row_name,
                                      value_str, value_list, value_list_2, event_id, ControlProperties.ControlType.CONTROL,
                                      value_index_name,
                                      int(value_list_start_row) if value_list_start_row else 0,
                                      value_dialog_impl, value_list_textids, as_slider,
                                      height, width, font_style, font_face_code, background_color,
                                      parent_param_data.row_state_key, parent_param_data.expander_state_key)

        ctrl_prop.value_text_list = value_text_list

        XmlParameterReaderUtil.get_sub_member_text(param_prop.value_type, ctrl_prop)


        #----------------- set the enable and visible state (only constant value check)

        if enable_condition == GeneralConstants.FALSE:
            ctrl_prop.enable = False

        if visible_condition == GeneralConstants.FALSE:
            ctrl_prop.visible = False


        #----------------- get the additional data

        XmlParameterReader.__get_min_max_value(param, ctrl_prop)

        XmlParameterReader.__get_constraint(param, include_data.is_include, include_data.name_postfix, ctrl_prop)

        XmlParameterReader.__get_named_tuple_data(param, value_type, local_str_table, global_str_table, is_visual_script, ctrl_prop)

        return ctrl_prop


    @staticmethod
    def __get_min_max_value(param    : ElementTree.Element,
                            ctrl_prop: ControlProperties):
        """ set the min and max value

        Args:
            param:     parameter
            ctrl_prop: control properties
        """

        ctrl_prop.min_value_condition = XmlElementTreeUtil.get_tag_data(param, "MinValue",
                                                                        allow_multiline_text = True).replace(" ,", "," )
        ctrl_prop.max_value_condition = XmlElementTreeUtil.get_tag_data(param, "MaxValue",
                                                                        allow_multiline_text = True).replace(" ,", "," )
        ctrl_prop.interval_value      = XmlElementTreeUtil.get_tag_data(param, "IntervalValue",
                                                                        allow_multiline_text = True)
        while ctrl_prop.min_value_condition.find(" ,") != -1:
            ctrl_prop.min_value_condition = ctrl_prop.min_value_condition.replace(" ,", "," )

        while ctrl_prop.max_value_condition.find(" ,") != -1:
            ctrl_prop.max_value_condition = ctrl_prop.max_value_condition.replace(" ,", "," )


    @staticmethod
    def __get_named_tuple_data(param           : ElementTree.Element,
                               value_type      : ParameterPropertyValueType,
                               local_str_table : BuildingElementStringTable,
                               global_str_table: BuildingElementStringTable,
                               is_visual_script: bool,
                               ctrl_prop       : ControlProperties):
        """ set the named tuple data

        Args:
            param:            parameter
            value_type:       value type
            local_str_table:  local string table
            global_str_table: global string table
            is_visual_script: visual script state
            ctrl_prop:        control properties
        """

        if not value_type.is_tuple_type(True):
            return

        named_tuple_params = XmlElementTreeUtil.get_element(param, "NamedTuple")

        if (tuple_text := XmlParameterTextReader.get_prop_text(named_tuple_params, local_str_table, global_str_table, is_visual_script)
                if named_tuple_params else ""):
            ctrl_prop.text = tuple_text

        if GeneralConstants.TEXT_SEPARATOR not in ctrl_prop.text:
            ctrl_prop.text = ctrl_prop.text.replace(",", GeneralConstants.TEXT_SEPARATOR)


    @staticmethod
    def __get_constraint(param       : ElementTree.Element,
                         is_include  : bool,
                         name_postfix: str,
                         ctrl_prop   : ControlProperties):
        """ set the constraint

        Args:
            param:        parameter
            is_include:   is include state
            name_postfix: name postfix
            ctrl_prop:    control properties
        """

        if (constraint := XmlElementTreeUtil.get_tag_data(param, "Constraint")):
            if is_include:
                constraint = XmlParameterReaderUtil.insert_name_postfix(constraint, name_postfix)

            ctrl_prop.constraint = constraint.split(";")
