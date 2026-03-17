""" Implementation of the building element palette service
"""

from typing import Any

import inspect

import NemAll_Python_Palette as AllplanPalette

from BaseScriptObject import BaseScriptObject
from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementControlService import BuildingElementControlService
from BuildingElementPalette import BuildingElementPalette
from BuildingElementUtil import BuildingElementUtil
from ControlPropertiesMinMaxUtil import ControlPropertiesMinMaxUtil
from ControlPropertiesValueListUtil import ControlPropertiesValueListUtil
from DocumentManager import DocumentManager
from StringEvaluate import StringEvaluate

import BuildingElementParameterPropertyUtil

import BuildingElementValueUtil

from BuildingElementInputServices.ScriptService import ScriptService
from BuildingElementInputServices.ScriptObjectService import ScriptObjectService

from Palette.PaletteBuildingElementUtil import PaletteBuildingElementUtil

class BuildingElementPaletteService:
    """ Definition of class BuildingElementPaletteService
    """

    __palette_lock = False
    __update_lock  = False

    def __init__(self,
                 build_ele_list           : list[BuildingElement],
                 build_ele_composite      : BuildingElementComposite,
                 build_ele_script         : Any,
                 build_ele_ctrl_props_list: list[BuildingElementControlProperties],
                 picture_path             : str,
                 script_object            : (BaseScriptObject | None) = None):
        """ Initialize the data

        Args:
            build_ele_list:            list with the building elements
            build_ele_composite:       building element composite with the building element constraints
            build_ele_script:          Building element script
            build_ele_ctrl_props_list: list with the building element control properties
            picture_path:              Picture path
            script_object:             script object
        """

        self.build_ele_pal : (BuildingElementPalette | None)          = None
        self.palette       : (AllplanPalette.PythonWpfPalette | None) = None

        self.build_ele_list            = build_ele_list
        self.build_ele_composite       = build_ele_composite
        self.build_ele_script          = build_ele_script
        self.build_ele_ctrl_props_list = build_ele_ctrl_props_list
        self.picture_path              = picture_path
        self.script_object             = script_object

        self.page_building_ele: list[list[int]] = []


    @staticmethod
    def set_palette_lock(palette_lock: bool):
        """ set the palette lock state

        Args:
            palette_lock: palette lock state
        """

        BuildingElementPaletteService.__palette_lock = palette_lock


    @staticmethod
    def set_update_lock(update_lock: bool):
        """ set the palette lock state

        Args:
            update_lock: palette lock state
        """

        BuildingElementPaletteService.__update_lock = update_lock


    def show_palette(self,
                     part_name        : str,
                     show_close_button: bool = True,
                     open_palette     : bool = True,
                     active_page_text : str  = "",
                     is_visual_script : bool = False):
        """ Show the palette

        Args:
            part_name:         Name of the PythonPart
            show_close_button: Show close button in palette
            open_palette:      open the palette
            active_page_text:  active page text
            is_visual_script:  execution for VisualScripting
        """

        self.build_ele_pal = BuildingElementPalette(is_visual_script)

        if not self.__palette_lock:
            self.palette = AllplanPalette.PythonWpfPalette()

            self.page_building_ele = self.build_ele_pal.show(self.build_ele_list,
                                                             self.build_ele_ctrl_props_list,
                                                             self.palette.GetPythonWpfPaletteBuilder(),
                                                             self.picture_path, self.build_ele_composite)

        if open_palette and self.palette is not None:
            self.palette.Open(self.build_ele_list[0].title, part_name, self.build_ele_list[0].data_column_width,
                              show_close_button, self.build_ele_list[0].show_favorite_buttons,
                              DocumentManager.get_instance().document, active_page_text)


    def get_control_text(self) -> str:
        """ Get the control data as text

        Returns:
            Controls data as text
        """

        control_text = str(self.palette)

        if self.palette:
            self.palette.Reset(False)

        return control_text


    def show_page_for_element(self,
                              act_page            : int,
                              build_ele_index_list: list [int]):
        """ Show the page for the element_index

        Args:
            act_page:             active page index
            build_ele_index_list: index list with the connected building elements (geometry, reinforcement, ...) of a sub element
        """

        set_new_page    = True
        page_type_index = -1

        for build_ele_index in build_ele_index_list:
            script_name = self.build_ele_list[build_ele_index].script_name

            index = 0

            page_type_dict = {}

            add_to_page_type_dict = True


            #----------------- get the index of the last "script_name" building element
            #                  don't count hidden elements to get the real index

            for i in range(0, build_ele_index + 1):
                if i == 0  or  self.build_ele_composite.is_element_visible(i - 1, self.build_ele_list):
                    ele_script_name = self.build_ele_list[i].script_name


                    #----------------- count same names before the first "script_name"

                    if add_to_page_type_dict  and  self.build_ele_ctrl_props_list[i]:
                        page_type_dict[ele_script_name] = 1


                    #----------------- first "script_name" closes the name counting

                    if script_name == ele_script_name:
                        add_to_page_type_dict = False
                        index += 1

            self.set_building_element_index(index, script_name)


            #----------------- get the index of the page type

            if page_type_index == -1:
                page_type_index = len(page_type_dict) - 1

            if len(page_type_dict) - 1 == act_page:
                set_new_page = False

        if set_new_page:
            self.update_palette(page_type_index, True)
        else:
            self.update_palette(-1, True)

        self.check_building_element_index()


    def on_control_event(self,
                         event_id: int) -> bool:
        """ On control event

        Args:
            event_id: event id of control.

        Returns:
            event was processed state
        """

        if not self.build_ele_script or self.palette is None or self.build_ele_pal is None:
            return False


        #----------------- get the on_control_event function

        if (on_control_event_fct := getattr(self.build_ele_script, "on_control_event", None)) is None:
            print("BuildingElementInput.py (on_control_event not overloaded in script ",
                  self.build_ele_list[0].script_name, ")")

            return False


        #----------------- execute the control event

        arg_spec = inspect.getfullargspec(on_control_event_fct)

        func_param_count = len(arg_spec.args)

        doc = DocumentManager.get_instance().document

        if len(self.build_ele_list) == 1:
            if func_param_count == 2:
                refresh_palette = on_control_event_fct(self.build_ele_list[0], event_id)
            else:
                refresh_palette = on_control_event_fct(self.build_ele_list[0], event_id, doc)
        else:
            if func_param_count == 3:
                refresh_palette = on_control_event_fct(self.build_ele_list, self.build_ele_composite, event_id)
            else:
                refresh_palette = on_control_event_fct(self.build_ele_list, self.build_ele_composite, event_id, doc)


        #----------------- refresh the palette if necessary

        if refresh_palette:
            self.palette.Reset(True)

            if self.palette:
                self.page_building_ele = self.build_ele_pal.show(self.build_ele_list,
                                                                 self.build_ele_ctrl_props_list,
                                                                 self.palette.GetPythonWpfPaletteBuilder(),
                                                                 self.picture_path, self.build_ele_composite)

        return True


    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any) -> bool:
        """ Modify property of element

        Args:
            page:  description
            name:  the name of the property.
            value: new value for property.

        Returns:
            update palette state
        """

        #----------------- set the global properties

        if name == "__GlobalConcreteCover__":
            for build_ele in self.build_ele_list:
                build_ele.modify_value_type("ReinfConcreteCover", value)

            return True

        if name == "__GlobalReinforcementDiameter__":
            for build_ele in self.build_ele_list:
                build_ele.modify_value_type("ReinfBarDiameter", value)

            return True


        #----------------- get the page number (input from a DOM control)

        name = name.replace("___DOM", "")

        if page >= 100:
            page = PaletteBuildingElementUtil.get_page_from_building_element_index(page, self.page_building_ele,
                                                                                   self.build_ele_ctrl_props_list, name)


        #----------------- get the old visible state

        build_ele_visible = [self.build_ele_composite.is_element_visible(i - 1, self.build_ele_list) \
                            for i in range(1, len(self.build_ele_list))]


        #----------------- Get the building element for the name and page

        parent_name = BuildingElementParameterPropertyUtil.get_property_value_name(name)

        build_ele_index = PaletteBuildingElementUtil.get_build_ele_index(self.page_building_ele,
                                                                         self.build_ele_list,
                                                                         page, parent_name)

        build_ele            = self.build_ele_list[build_ele_index]
        build_ele_ctrl_props = self.build_ele_ctrl_props_list[build_ele_index]

        build_ele_ctrl_props.reset_refresh_control()


        #----------------- Check and set the new value

        refresh_palette, prop = BuildingElementValueUtil.update_value(name, value, build_ele, build_ele_ctrl_props)

        if name == "__ElementIndex__":
            refresh_palette = True

            script_name = build_ele.script_name

            self.set_building_element_index(value, script_name)

        if self.script_object:
            refresh_palette |= ScriptObjectService.modify_element_property(self.script_object, name, value)

        elif self.build_ele_script:
            refresh_palette |= ScriptService.modify_element_property(name, value, prop, build_ele_index, self.build_ele_script,
                                                                     self.build_ele_list, self.build_ele_ctrl_props_list,
                                                                     self.build_ele_composite)

        if len(self.build_ele_list) > 1:
            if self.build_ele_composite.connect_building_element_values(self.build_ele_list):
                refresh_palette = True


        #----------------- check the corresponding min and max values

        param_dict = StringEvaluate.get_string_eval_param_dict(build_ele, self.build_ele_list[0].get_string_tables()[0])

        if ControlPropertiesMinMaxUtil.check_min_max_value(build_ele, build_ele_ctrl_props, param_dict,
                                                           self.build_ele_list[0].get_string_tables()[1]):
            refresh_palette = True

        if ControlPropertiesValueListUtil.validate_values(build_ele, build_ele_ctrl_props, param_dict):
            refresh_palette = True

        if refresh_palette:
            return True


        #----------------- Check for changed visibility, ...

        if BuildingElementControlService.check_visible_state(self.build_ele_list[0], build_ele_ctrl_props, param_dict, name, False):
            return True

        if BuildingElementControlService.check_enable_state(self.build_ele_list[0], build_ele_ctrl_props, param_dict, name, False):
            return True

        for page_data in build_ele.get_pages():
            if name in page_data.visible_condition or \
               name in page_data.enable_condition:
                return True

        if prop and prop.value_type == "reinfconcretecover"  and self.palette is not None and \
           self.palette.GetPythonWpfPaletteBuilder().IsConcreteCoverPaletteUpdate(value):
            return True

        if not refresh_palette:
            if next((True for i in range(len(self.build_ele_list) - 1)
                     if build_ele_visible[i] != self.build_ele_composite.is_element_visible(i, self.build_ele_list)), False):
                return True


        #----------------- check for control on multiple pages

        multi_page = False

        for build_ele_ctrl_props in self.build_ele_ctrl_props_list:
            if build_ele_ctrl_props.get_property(name) is not None:
                if multi_page:
                    return True

                multi_page = True

        return False


    def close_palette(self) -> str:
        """ Close the palette

        Returns:
            text of the active page
        """

        if not self.palette:
            return ""

        return self.palette.Close()


    def update_palette(self,
                       page_index             : int,
                       update_dialog_data     : bool,
                       _show_palette_close_btn= True):
        """ Update the palette

        Args:
            page_index:              page index to show, -1 = use current
            update_dialog_data:      update the dialog data: True/False
            _show_palette_close_btn: show close button in palette: True/False
        """

        if self.palette is None or self.build_ele_pal is None:
            return

        self.palette.Reset(True)

        self.page_building_ele = self.build_ele_pal.show(self.build_ele_list, self.build_ele_ctrl_props_list,
                                                         self.palette.GetPythonWpfPaletteBuilder(),
                                                         self.picture_path, self.build_ele_composite)

        if update_dialog_data and not BuildingElementPaletteService.__update_lock:
            self.palette.UpdateDialogData(page_index)


    def refresh_palette(self,
                        build_ele_list    : list[BuildingElement],
                        build_ele_ctrl_props_list: list[BuildingElementControlProperties]):
        """ refresh the palette

        Args:
            build_ele_list:     Building element list
            build_ele_ctrl_props_list: Control properties list
        """

        self.build_ele_list      = build_ele_list
        self.build_ele_ctrl_props_list  = build_ele_ctrl_props_list

        self.update_palette(0, False)


    def set_building_element_index(self,
                                   index      : int,
                                   script_name: str):
        """ Set the building element index

        Args:
            index:       Element index
            script_name: Script name
        """

        script_list = BuildingElementUtil.count_scripts(self.build_ele_list)

        if script_list[script_name] < index:
            index = script_list[script_name]

        visible_count = 0

        for i, build_ele in enumerate(self.build_ele_list):
            if i > 0 and script_name == build_ele.script_name and self.build_ele_composite.is_element_visible(i - 1, self.build_ele_list):
                visible_count += 1

        index = min(visible_count, index)

        for build_ele in self.build_ele_list:
            if script_name == build_ele.script_name:
                if (prop := build_ele.get_property("__ElementIndex__")):
                    prop.value = index


    def check_building_element_index(self):
        """ Check the building element index (e.g. set to 0 for hidden elements)
        """

        for i in range(1, len(self.build_ele_list)):
            if self.build_ele_composite.is_element_visible(i - 1, self.build_ele_list):
                prop = getattr(self.build_ele_list[i],"__ElementIndex__",None)

                if prop  and  prop.value != 0:
                    _, composite_index_list = self.build_ele_composite.get_composite_build_ele_list(i - 1, self.build_ele_list)

                    for composite_index in composite_index_list:
                        self.set_building_element_index(prop.value, self.build_ele_list[composite_index].script_name)
