""" implementation of the input service
"""

from typing import Any

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_Input as AllplanIFW

from BuildingElementListService import BuildingElementListService
from DocumentManager import DocumentManager
from InputMode import InputMode
from PythonPartPreview import PythonPartPreview
from PythonPartTransaction import PythonPartTransaction

from .InputData import InputData
from .InteractorService import InteractorService
from .ScriptObjectService import ScriptObjectService
from .ScriptService import ScriptService

class InputService():
    """ implementation of the input service
    """

    ACTIVE_PAGE_KEY     = "___ActivePage___"
    PRECAST_ELEMENT_KEY = "precastelementtypecatalogreference"
    DOM_KEY             = "___DOM___SubmitChanges___"
    MULTIMATERIAL_KEY   = "multimateriallayoutcatalogreference"

    @staticmethod
    def modify_element_property(input_data: InputData,
                                page      : int,
                                name      : str,
                                value     : Any):
        """ Modify property of element

        Args:
            input_data: input data
            page      : the page of the property
            name      : the name of the property.
            value     : new value for property.
        """

        if name == InputService.ACTIVE_PAGE_KEY:
            InputService.__modify_active_page(input_data, value)
            return


        #----------------- finalize the DOM input

        if input_data.palette_service is not None and name == InputService.DOM_KEY:
            input_data.palette_service.update_palette(-1, True)

            InputService.draw_preview(input_data, False, True, True, False)

            return

        DocumentManager.get_instance().document = input_data.coord_input.GetInputViewDocument()

        name = name.replace("___DOM", "")


        #----------------- modification is done in the interactor

        if input_data.input_mode == InputMode.Interactor:
            InteractorService.modify_element_property(input_data, page, name, value)

            return


        #----------------- modify the property in a standard PythonPart
        #                  - modify the value
        #                  - execute the modification function of the script for further checks and modifications

        if input_data.palette_service is None:
            return

        input_data.is_modified_parameter = True

        update_palette = input_data.palette_service.modify_element_property(page, name, value)

        prop = input_data.build_ele_list[0].get_property(name)
        if prop is not None and prop.value_type.lower() in [InputService.PRECAST_ELEMENT_KEY, InputService.MULTIMATERIAL_KEY]:
            input_data.palette_service.update_palette(-1, False)

        if ScriptService.modify_control_properties(input_data, name, 0):
            update_palette = True


        #----------------- check for a palette update due to a control refresh

        if next((build_ele_ctrl_props.is_refresh_control() for build_ele_ctrl_props in input_data.build_ele_ctrl_props_list), False):
            update_palette = True


        #----------------- execute after modification

        if InputService.__execute_update_after_modification(input_data, update_palette):
            input_data.palette_service.update_palette(-1, False)


    @staticmethod
    def create_elements_in_db(input_data: InputData):
        """ Create the element in the data base

        Args:
            input_data: input
        """

        if not input_data.is_only_update:
            input_data.handle_modi_service.stop()

        input_data.input_mode  = InputMode.WriteToDB
        input_data.expand_util = None

        doc = input_data.coord_input.GetInputViewDocument()

        if input_data.create_ele_result.elements or input_data.create_ele_result.elements_to_delete is not None:
            if input_data.is_modify_elements:
                if input_data.is_modified_parameter:
                    AllplanBaseEle.ModifyElements(input_data.coord_input.GetInputViewDocument(),
                                                  input_data.create_ele_result.elements)
                else:
                    AllplanIFW.VisibleService.ShowAllElements()
            else:
                pyp_transaction = PythonPartTransaction(doc,
                                                        connect_to_ele = input_data.create_ele_result.connect_to_ele)

                pyp_transaction.execute(input_data.insert_matrix,
                                        input_data.coord_input.GetViewWorldProjection(),
                                        input_data.create_ele_result.elements,
                                        input_data.modification_ele_list,
                                        input_data.create_ele_result.reinf_rearrange, True,
                                        input_data.asso_ref_ele,
                                        uuid_parameter_name = input_data.create_ele_result.uuid_parameter_name,
                                        elements_to_delete  = input_data.create_ele_result.elements_to_delete)

        input_data.build_ele_service.write_data_to_default_favorite_file(input_data.build_ele_list)


    @staticmethod
    def recalculate_and_draw_preview(input_data         : InputData,
                                     to_screen          : bool,
                                     draw_input_controls: bool,
                                     use_static_preview : bool):
        """ recalculate and draw the preview

        Args:
            input_data:          input data
            to_screen:           direct draw to the screen True/False
            draw_input_controls: draw the input controls: True/False
            use_static_preview:  use the static preview state
        """

        if input_data.script_object and input_data.script_object.script_object_interactor is not None or \
           use_static_preview and input_data.create_ele_result.as_static_preview:
            return


        #----------------- check for a new element creation

        if not ScriptObjectService.execute_script_object(input_data):
            if not ScriptService.create_element(input_data):
                return

        InputService.draw_preview(input_data, to_screen, True, draw_input_controls, use_static_preview)


    @staticmethod
    def draw_preview(input_data         : InputData,
                     to_screen          : bool,
                     draw_handles       : bool,
                     draw_input_controls: bool,
                     use_static_preview : bool):
        """ Draw the preview

        Args:
            input_data:          input data
            to_screen:           direct draw to the screen True/False
            draw_handles:        draw the handles True/False
            draw_input_controls: draw the input controls: True/False
            use_static_preview:  use the static preview state
        """

        if input_data.script_object and input_data.script_object.script_object_interactor is not None or \
           use_static_preview and input_data.create_ele_result.as_static_preview:
            return

        input_doc = input_data.coord_input.GetInputViewDocument()
        view_proj = input_data.coord_input.GetViewWorldProjection()

        if input_data.input_mode == InputMode.RefPoint:
            input_data.last_input_doc = input_doc
            input_data.last_view_proj = view_proj
        else:
            if input_doc.GetDocumentID() == input_data.last_input_doc.GetDocumentID():
                input_data.last_view_proj = view_proj

            input_doc = input_data.last_input_doc
            view_proj = input_data.last_view_proj


        #----------------- Draw the handles

        if draw_handles and input_data.input_mode == InputMode.HandleSelect:
            input_data.handle_modi_service.start(input_data.create_ele_result.handles, input_data.insert_matrix,
                                                 input_doc, view_proj, draw_input_controls)

        if input_data.create_ele_result.preview_symbols is not None:
            input_data.create_ele_result.preview_symbols.draw(input_data.insert_matrix,
                                                              input_data.coord_input.GetViewWorldProjection(),
                                                              not input_data.modification_ele_list.is_modification_element())


        #----------------- Draw the element preview

        PythonPartPreview.execute(input_doc,
                                    input_data.insert_matrix,
                                    input_data.create_ele_result.preview_elements,
                                    False, input_data.asso_ref_ele,
                                    not input_data.modification_ele_list.is_modification_element(),
                                    input_data.create_ele_result.as_static_preview)

        PythonPartPreview.execute(input_doc,
                                  input_data.insert_matrix,
                                  input_data.create_ele_result.elements,
                                  to_screen, input_data.asso_ref_ele,
                                  not input_data.modification_ele_list.is_modification_element(),
                                  input_data.create_ele_result.as_static_preview)

    @staticmethod
    def __modify_active_page(input_data: InputData,
                             value     : Any):
        """ modify the active page

        Args:
            input_data: input data
            value:      new value for property.
        """

        set_page_index = getattr(input_data.interactor, "set_active_palette_page_index", None) \
                            if input_data.input_mode == InputMode.Interactor else \
                         getattr(input_data.build_ele_script, "set_active_palette_page_index", None)

        if set_page_index:
            set_page_index(value)

        input_data.active_page = value


    @staticmethod
    def __execute_update_after_modification(input_data    : InputData,
                                            update_palette: bool) -> bool:
        """ execute the update after the modification

        Args:
            input_data:     input data
            update_palette: update palette state

        Returns:
            update palette state
        """

        #------------- palette update is needed for changed parameter values as result of a
        #              new PythonPart creation in draw_preview

        param_list = ""

        if not update_palette:
            param_list = BuildingElementListService.get_params_list(input_data.build_ele_list)

        InputService.recalculate_and_draw_preview(input_data, True, True, True)

        if not update_palette:
            update_palette = param_list != BuildingElementListService.get_params_list(input_data.build_ele_list)

        return update_palette
