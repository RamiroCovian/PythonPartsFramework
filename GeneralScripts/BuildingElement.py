"""Script for BuildingElement
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=unnecessary-lambda-assignment

from __future__ import annotations

from typing import Any

import hashlib

from dataclasses import dataclass

from _collections_abc import Iterator

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil

from BuildingElementConverter import BuildingElementConverter
from BuildingElementStringTable import BuildingElementStringTable
from BuildingElementMaterialStringTable import BuildingElementMaterialStringTable
from HandlePropertiesService import HandlePropertiesService
from HandleProperties import HandleProperties
from ParameterProperty import ParameterProperty
from ReinforcementDefinition import ReinforcementDefinition
from TraceService import TraceService

from TestHelper import PythonPartPylintDecorator

PARAMETER_CONSTANT = "__Constant___"

class BuildingElement():
    """ Definition of class BuildingElement
    """

    @dataclass
    class PageData():
        """ implementation of the page data class """

        name             : str = ""
        text             : str = ""
        visible_condition: str = ""
        enable_condition : str = ""

    def __init__(self):
        """ Initialization of class BuildingElement
        """

        self.__pages                     : list[BuildingElement.PageData] = []
        self.__reinforcement_list        : list[ReinforcementDefinition]  = []

        self.__script_name               = ""
        self.__pyp_file_name             = ""
        self.__pyp_file_path             = ""
        self.__title                     = ""
        self.__insert_matrix             = AllplanGeo.Matrix3D()
        self.__geometry_expand           = False
        self.__local_str_table           = BuildingElementStringTable("", False, "")         #local table of this pyp file
        self.__global_str_table          = BuildingElementStringTable("", False, "")         # global table for all pyp files
        self.__global_material_str_table = BuildingElementMaterialStringTable("", False, "") # global material table for all pyp files
        self.__read_last_input           = False
        self.__is_interactor             = False
        self.__element_id                = ""
        self.__data_column_width         = 0
        self.__script_uuid               = ""
        self.__version                   = ""
        self.__node_index                = 0
        self.__vs_placement_point_input  = False
        self.__vs_multi_placement        = False
        self.__skip_eval                 = False
        self.__show_favorite_buttons     = True

    def __repr__(self) -> str:
        """ get the string from the object member

        Returns:
            data string
        """
        return  f"<{self.__class__.__name__}>\n" \
                f"   pages                    = {self.__pages}\n" \
                f"   reinforcement_list       = {self.__reinforcement_list}\n" \
                f"   script_name              = {self.__script_name}\n" \
                f"   pyp_file_name            = {self.__pyp_file_name}\n" \
                f"   pyp_file_path            = {self.__pyp_file_path}\n" \
                f"   title                    = {self.__title}\n" \
                f"   insert_matrix            = {self.__insert_matrix}\n" \
                f"   geometry_expand          = {self.__geometry_expand}\n" \
                f"   parameters               = {repr(self.get_parameter_dict())}\n" \
                f"   read_last_input          = {self.__read_last_input}\n" \
                f"   is_interactor            = {self.__is_interactor}\n" \
                f"   element_id               = {self.__element_id}\n" \
                f"   data_column_width        = {self.__data_column_width}\n" \
                f"   vs_placement_point_input = {self.__vs_placement_point_input}\n" \
                f"   vs_multi_placement       = {self.__vs_multi_placement}\n" \
                f"   script_uuid              = {self.__script_uuid}\n"

    def print_values(self):
        """ Print the building element values
        """

        for prop in self.get_properties():
            TraceService.trace_1(prop.name + " = " + str(prop.value))

    def add_page(self,
                 name             : str,
                 text             : str,
                 visible_condition: str,
                 enable_condition : str):
        """ Add pages for property dialog

        Args:
            name:              the name of the page.
            text:              text of the page
            visible_condition: visible condition of the page
            enable_condition:  enable condition of the page
        """
        self.__pages.append(BuildingElement.PageData(name, text, visible_condition, enable_condition))

    def reset_page(self,
                   name             : str,
                   text             : str,
                   visible_condition: str,
                   enable_condition : str):
        """ Reset pages for property dialog

        Args:
            name:              the name of the page.
            text:              text of the page
            visible_condition: visible condition
            enable_condition:  enable condition
        """
        self.__pages.clear()
        self.__pages.append(BuildingElement.PageData(name, text, visible_condition, enable_condition))

    def get_pages(self) -> list[PageData]:
        """ Get pages for property dialog

        Returns:
            list of the pages.
        """
        return self.__pages

    def add_string_tables(self,
                          local_str_table : BuildingElementStringTable,
                          global_str_table: BuildingElementStringTable):
        """ Sets the local and global string table

        Args:
            local_str_table:  local string table
            global_str_table: global string table
        """
        self.__local_str_table  = local_str_table
        self.__global_str_table = global_str_table

    def get_string_tables(self) -> tuple[BuildingElementStringTable, BuildingElementStringTable]:
        """ Get the local and global string tables

        Returns:
            tuple of local and global string table
        """
        return self.__local_str_table, self.__global_str_table

    def add_material_string_table(self,
                                  global_material_str_table: BuildingElementMaterialStringTable):
        """ Sets the global material string table

        Args:
            global_material_str_table: global material string table
        """
        self.__global_material_str_table = global_material_str_table

    def get_material_string_table(self) -> BuildingElementMaterialStringTable:
        """ Get the global material string table

        Returns:
            global material string table
        """
        return self.__global_material_str_table

    def get_insert_matrix(self) -> AllplanGeo.Matrix3D:
        """ Get matrix for macro/  macro group update

        Returns:
            tuple matrix
        """
        return  self.__insert_matrix

    def set_insert_matrix(self,
                          matrix: AllplanGeo.Matrix3D):
        """ Sets matrix for insertion

        Args:
            matrix: insertion matrix
        """
        self.__insert_matrix = matrix

    def add_property(self,
                     name : str,
                     value: ParameterProperty):
        """ Add a new property to class

        Args:
            name:  the name of the property.
            value: the value of the property.
        """

        # create local fget and fset functions with the access to the get_property and set_property methods
        fget = lambda self: self.get_property(name)
        fset = lambda self, value: self.set_property(name, value)

        # add property to self
        setattr(self.__class__, name, property(fget, fset))

        # add corresponding local variable as reference to the parameter property
        setattr(self, "__ParamProp___" + name, value)

    def set_property(self,
                     name : str,
                     value: Any):
        """ Set property value by name

        Args:
            name:  the name of the property.
            value: new value of the property.
        """
        setattr(self, "__ParamProp___" + name, value)

    def get_property(self,
                     name: str) -> (ParameterProperty | None):
        """ Get property parameter by name

        Args:
            name: the name of the property.

        Returns:
            property parameter, None if not exist
        """

        if (ip_square_bracket_open := name.find("[")) != -1:
            return getattr(self, "__ParamProp___" + name[:ip_square_bracket_open], None)

        if (ip_bracket_open := name.find("(")) != -1:
            return getattr(self, "__ParamProp___" + name[:ip_bracket_open], None)

        return getattr(self, "__ParamProp___" + name, None)

    def get_constant(self,
                     name: str) -> (Any < None):
        """ get the constant by name

        Args:
            name: name of the constant

        Returns:
            constant value, None if not exist
        """

        return getattr(self, PARAMETER_CONSTANT + name, None)

    def get_existing_property(self,
                              name: str) -> ParameterProperty:
        """ Get a mandatory property parameter by name. If the property doesn't exist,
        a message box is shown and an exception is thrown

        Args:
            name: the name of the property.

        Returns:
            property

        Raises:
            ValueError: raised in case of missing parameter
        """

        if (prop := self.get_property(name)):
            return prop

        msg = "The parameter " + name + " must exist in the BuildingElement"

        AllplanUtil.ShowMessageBox(msg, AllplanUtil.MB_OK)

        raise ValueError(msg)

    @property
    def skip_eval(self) -> bool:
        """ Get corresponding skip_eval

        Returns:
            status fo skip_eval
        """
        return self.__skip_eval

    @skip_eval.setter
    def skip_eval(self,
                  value: bool) -> None:

        """ Set skip eval property

        Args:
            value: Status of skip eval
        """
        self.__skip_eval = value

    @property
    def script_name(self) -> str:
        """ Get corresponding script name

        Returns:
            name of the script.
        """
        return self.__script_name

    @script_name.setter
    def script_name(self,
                    name: str):
        """ Set corresponding script name

        Args:
            name: the name of the script.
        """
        self.__script_name = name

    @property
    def pyp_file_name(self) -> str:
        """ Get corresponding pyp file name

        Returns:
            name of the pyp file.
        """
        return self.__pyp_file_name

    @pyp_file_name.setter
    def pyp_file_name(self,
                      name: str):
        """ Set corresponding pyp file name

        Args:
            name: the name pyp file.
        """
        self.__pyp_file_name = name

    @property
    def pyp_file_path(self) -> str:
        """ Get corresponding pyp file path

        Returns:
            name of the pyp file path.
        """
        return self.__pyp_file_path

    @pyp_file_path.setter
    def pyp_file_path(self,
                      path: str):
        """ Set corresponding pyp file path

        Args:
            path: pyp file path
        """
        self.__pyp_file_path = path

    @property
    def title(self) -> str:
        """ Get the property palette title

        Returns:
            property palette title
        """
        return self.__title

    @title.setter
    def title(self,
              title: str):
        """ Set the property palette title

        Args:
            title: title of the property palette
        """
        self.__title = title

    def get_hash(self) -> str:
        """ Calculate a hash value for script name and parameter list

        Returns:
            Calculated hash string.
        """
        script_str = self.script_name.encode('utf-8')

        if (param_dict := self.get_model_parameter_dict(True)) is not None:
            script_str += repr(param_dict).encode('utf-8')

        return hashlib.sha224(script_str).hexdigest()

    @property
    def geometry_expand(self) -> bool:
        """ Get geometry expand state

        Returns:
            true/false state of geometry expand.
        """
        return self.__geometry_expand

    @geometry_expand.setter
    def geometry_expand(self,
                        expand: bool):
        """ Set the geometry expand state

        Args:
            expand: True/False state of geometry expand.
        """
        self.__geometry_expand = expand

    @property
    def read_last_input(self) -> bool:
        """ Get read last input state

        Returns:
            true/false state of read last input
        """
        return self.__read_last_input

    @read_last_input.setter
    def read_last_input(self,
                        read_last_input: bool):
        """ Set the read last input state

        Args:
            read_last_input: true/false state of geometry expand.
        """
        self.__read_last_input = read_last_input

    @property
    def is_interactor(self) -> bool:
        """ Get the interactor state

        Returns:
            true/false interactor state
        """
        return self.__is_interactor

    @is_interactor.setter
    def is_interactor(self,
                      is_interactor: bool):
        """ Set the interactor state

        Args:
            is_interactor: interactor state

        """
        self.__is_interactor = is_interactor

    @property
    def vs_placement_point_input(self) -> bool:
        """ Get the VS placement point input state

        Returns:
            true/false VS is placed by point input
        """
        return self.__vs_placement_point_input

    @vs_placement_point_input.setter
    def vs_placement_point_input(self,
                                 vs_placement_point_input: bool):
        """ Set the VS placement point input state

        Args:
            vs_placement_point_input: true/false VS placement point input
        """
        self.__vs_placement_point_input = vs_placement_point_input

    @property
    def vs_multi_placement(self) -> bool:
        """ Get the VS multi placement state

        Returns:
            true/false VS multi placement
        """
        return self.__vs_multi_placement

    @vs_multi_placement.setter
    def vs_multi_placement(self,
                           vs_multi_placement: bool):
        """ Set the VS multi placement state

        Args:
            vs_multi_placement: true/false VS multi placement
        """
        self.__vs_multi_placement = vs_multi_placement

    @property
    def element_id(self) -> str:
        """ Get the element id

        Returns:
            element id
        """
        return self.__element_id

    @element_id.setter
    def element_id(self,
                   element_id: str):
        """ Set the element id

        Args:
            element_id: ID of the element
        """
        self.__element_id = element_id

    @property
    def data_column_width(self) -> int:
        """ Get data column width

        Returns:
            data column width
        """
        return self.__data_column_width

    @data_column_width.setter
    def data_column_width(self,
                          data_column_width: int):
        """ Set the data column width

        Args:
            data_column_width: Width of the data column
        """
        self.__data_column_width = data_column_width

    @property
    def script_uuid(self) -> str:
        """ Get the UUID of the pyp file

        Returns:
            UUID of the pyp file
        """
        return self.__script_uuid

    @script_uuid.setter
    def script_uuid(self,
                    script_uuid: str):
        """ Set the UUID of the pyp file

        Args:
            script_uuid: UUID of the pyp file
        """
        self.__script_uuid = script_uuid

    @property
    def version(self) -> str:
        """ Get the version number as string

        Returns:
            Version number
        """
        return self.__version

    @version.setter
    def version(self,
                version: str):
        """ Set the version number as string

        Args:
            version: Version number
        """
        self.__version = version

    @property
    def show_favorite_buttons(self) -> bool:
        """ Get the show_favorite_button state

        Returns:
            show_favorite_buttons state
        """
        return self.__show_favorite_buttons

    @show_favorite_buttons.setter
    def show_favorite_buttons(self,
                              show_favorite_buttons: bool):
        """ Set the show_favorite_button state

        Args:
            show_favorite_buttons: show_favorite_button state
        """
        self.__show_favorite_buttons = show_favorite_buttons

    def get_float_version(self) -> float:
        """ Get the version as float number from the string

        Returns:
            version number as float value
        """

        if not self.__version:
            return 1.0

        if self.__version.count(".") > 1:
            parts = self.__version.split(".")

            try:
                return float(parts[0] + "." + parts[1] + "0" * (4 - len(parts[1])) + \
                             "".join([("0" * (4 - len(part)) + part) for part in parts[2:]]))
            except ValueError:
                return 1.0

        try:
            return float(self.__version)

        except ValueError:
            return 1.0


    @property
    def node_index(self) -> int:
        """ Get the node_index for VS

        Returns:
            node_index
        """
        return self.__node_index

    @node_index.setter
    def node_index(self,
                   node_index: int):
        """ Set the node_index

        Args:
            node_index: node index for VS
        """
        self.__node_index = node_index

    def get_reinforcement_definition_list(self) -> list[ReinforcementDefinition]:
        """ Get reinforcement list

        Returns:
            list of reinforcement.
        """
        return self.__reinforcement_list

    def set_reinforcement_definition_list(self,
                                          reinf_list: list[ReinforcementDefinition]):
        """ Set reinforcement list

        Args:
            reinf_list: list of reinforcement.
        """
        self.__reinforcement_list = reinf_list

    @PythonPartPylintDecorator.deprecated(replace = "use HandlePropertiesService.update_property_value(...)")
    def change_property(self,
                        handle_prop: HandleProperties,
                        input_pnt  : AllplanGeo.Point3D) -> bool:
        """ Change property value

        Args:
            handle_prop: handle property
            input_pnt:   input point

        Returns:
            update palette state
        """

        return HandlePropertiesService.update_property_value(self, handle_prop, input_pnt)

    @staticmethod
    def is_parameter_property(name: str) -> bool:
        """ Check for a parameter property

        Args:
            name: name of the parameter property

        Returns:
            name has parameter property
        """

        return name.find("__ParamProp___") != -1


    def get_properties(self) -> Iterator[ParameterProperty]:
        """ Get an iterator for the properties

        Yield:
            property iterator
        """

        for name, prop in self.__dict__.items():
            if self.is_parameter_property(name):
                yield prop


    def get_parameter_dict(self) -> dict[str, Any]:
        """ Get parameters dictionary

        Returns:
            dictionary of parameters.
        """

        return {prop.name: prop.value for prop in self.get_properties()}


    def get_model_parameter_dict(self,
                                 exclude_identical: bool = False) -> dict[str, ParameterProperty]:
        """ Get parameters dictionary for the model parameter

        Args:
            exclude_identical: exclude the parameter which should not be used for the identical check

        Returns:
            dictionary of parameters.
        """

        persist_states = (ParameterProperty.Persistent.MODEL, ParameterProperty.Persistent.MODEL_AND_FAVORITE)

        return {prop.name: prop.value \
                for prop in self.get_properties() if prop.persistent in persist_states and
                                                  (not exclude_identical or not prop.exclude_identical)}


    def modify_value_type(self,
                          value_type: str,
                          value     : Any):
        """ Modify the value of a value type

        Args:
            value_type: Value type
            value:      Value
        """

        for prop in self.get_properties():
            if prop.value_type == value_type:
                prop.value = value


    def get_params_list(self) -> list[str]:
        """ Get the list with the parameter values

        Returns:
            list with the parameter values
        """

        return BuildingElementConverter.get_params_list(self)


    def get_modified_properties(self) -> Iterator[ParameterProperty]:
        """ Get an iterator for the modified properties

        Yield:
            property iterator of the modified properties
        """

        for name, prop in self.__dict__.items():
            if self.is_parameter_property(name) and prop.is_modified:
                yield prop


    def reset_property_modified(self):
        """ Reset the modified state of the properties
        """

        for prop in self.get_properties():
            prop.reset_modified()


    def deep_copy(self) -> BuildingElement:
        """ deep copy of the object member

        Returns:
            copied building element
        """

        build_ele = BuildingElement()

        for page_data in self.get_pages():
            build_ele.add_page(page_data.name, page_data.text, page_data.visible_condition, page_data.enable_condition)

        build_ele.script_name              = self.script_name
        build_ele.pyp_file_name            = self.pyp_file_name
        build_ele.pyp_file_path            = self.pyp_file_path
        build_ele.title                    = self.title
        build_ele.geometry_expand          = self.geometry_expand
        build_ele.read_last_input          = self.read_last_input
        build_ele.is_interactor            = self.is_interactor
        build_ele.element_id               = self.element_id
        build_ele.data_column_width        = self.data_column_width
        build_ele.script_uuid              = self.script_uuid
        build_ele.version                  = self.version
        build_ele.node_index               = self.node_index
        build_ele.vs_placement_point_input = self.vs_placement_point_input
        build_ele.vs_multi_placement       = self.vs_multi_placement

        build_ele.set_reinforcement_definition_list(self.get_reinforcement_definition_list())
        build_ele.add_string_tables(*self.get_string_tables())
        build_ele.add_material_string_table(self.get_material_string_table())
        build_ele.set_insert_matrix(self.get_insert_matrix())

        for prop in self.get_properties():
            build_ele.add_property(prop.name, prop.deep_copy())

        return build_ele


    def add_constant(self,
                     name : str,
                     value: Any):
        """ Add a new constant to class

        Args:
            name:  the name of the constant
            value: the value of the constant
        """

        # create local fget
        fget = lambda self: getattr(self, PARAMETER_CONSTANT + name, None)

        # add property to self
        setattr(self.__class__, name, property(fget))

        # add corresponding local variable
        setattr(self, PARAMETER_CONSTANT + name, value)


    def get_constant_dict(self) -> dict[str, Any]:
        """ Get constants dictionary

        Returns:
            dictionary of constants
        """

        return {name[13:]: prop for name, prop in self.__dict__.items() if PARAMETER_CONSTANT in name}
