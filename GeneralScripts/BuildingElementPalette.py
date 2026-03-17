""" Script for BuildingElementPalette
"""

import os

import NemAll_Python_Palette as AllplanPalette

from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementCounter import BuildingElementCounter

from Palette.PalettePages import PalettePages

class BuildingElementPalette():
    """ Definition of class BuildingElementPalette
    """

    HIDDEN_PAGE = "__HiddenPage__"

    def __init__(self,
                 is_visual_script: bool = False):
        """ Initialization of class BuildingElementPalette

        Args:
            is_visual_script: palette for a visual script state
        """

        self.is_visual_script = is_visual_script
        self.page_index       = 0

        super().__init__()


    def show(self,
             build_ele_list     : list[BuildingElement],
             control_props_list : list[BuildingElementControlProperties],
             wpf_palette        : AllplanPalette.PythonWpfPaletteBuilder,
             picture_path       : str,
             build_ele_composite: BuildingElementComposite) -> list[list[int]]:
        """ show the palette

        Args:
            build_ele_list:      the building elements
            control_props_list:  control properties
            wpf_palette:         the palette to show.
            picture_path:        picture path
            build_ele_composite: building element composite

        Returns:
            list with the building element indexes assigned to a page
        """

        picture_path = os.path.dirname(picture_path)


        #------------------ loop the building elements

        page_building_ele: list[list[int]] = []

        build_ele_counter = BuildingElementCounter()

        page_index = 0

        page_index_dict: dict[str, int] = {}

        str_table = build_ele_list[0].get_string_tables()[0]

        for build_ele_index, build_ele in enumerate(build_ele_list):
            if build_ele_index > 0 and not build_ele_composite.is_element_visible(build_ele_index - 1, build_ele_list):
                continue

            if not build_ele_counter.check_index(build_ele):
                continue


            #---------------- get the pages

            hidden_page = [sub_page_index for sub_page_index, page_data in enumerate(build_ele.get_pages())
                           if page_data.name == self.HIDDEN_PAGE]


            #---------------- set the min/max and get the control properties for the "not hidden" pages

            control_props_list[build_ele_index].eval_palette_layout_script()

            page_control_props = [BuildingElementControlProperties() for _ in range(len(build_ele.get_pages()))]

            for ctrl_prop in control_props_list[build_ele_index]:
                if ctrl_prop.page not in hidden_page:
                    page_control_props[ctrl_prop.page].append(ctrl_prop)


            #------------------ Show the input controls for the pages

            palette_pages = PalettePages(build_ele, str_table, self.is_visual_script, picture_path)

            page_index = palette_pages.show_controls_for_pages(wpf_palette, page_building_ele,
                                                               page_index, page_index_dict, build_ele_index,
                                                               build_ele, page_control_props)

        return page_building_ele
