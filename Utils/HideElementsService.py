""" implementation of the hide elements service
"""

from typing import Any

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW

class HideElementsService():
    """ implementation of the hide elements service
    """

    def __init__(self):
        """ initialize
        """

        self.__hidden_elements : list[AllplanEleAdapter.BaseElementAdapter] = []


    def hide_arch_ground_view_elements(self,
                                       arch_ele: AllplanEleAdapter.BaseElementAdapter):
        """ hide the architecture ground view elements

        Args:
            arch_ele: architecture element
        """

        for child_ele in AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(arch_ele, False):
            if not isinstance(child_ele.GetGeometry(), AllplanGeo.Polyhedron3D):
                self.__hidden_elements.append(child_ele)

                for child_ele2 in AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(child_ele, False):
                    if not isinstance(child_ele2.GetGeometry(), AllplanGeo.Polyhedron3D):
                        self.__hidden_elements.append(child_ele2)

        self.__show_elements(False)


    def hide_element(self,
                     element: AllplanEleAdapter.BaseElementAdapter):
        """ hide the element and the children

        Args:
            element: element to hide
        """

        self.__hidden_elements.append(element)

        self.__hidden_elements += AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(element, True)

        self.__show_elements(False)


    def hide_element_and_linked(self,
                                element: AllplanEleAdapter.BaseElementAdapter):
        """ hide the element, the children and the linked elements

        Args:
            element: element to hide
        """

        self.__hidden_elements.append(element)

        self.__hidden_elements += AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(element, True)

        def get_child_elements(ele: AllplanEleAdapter.BaseElementAdapter):
            self.__hidden_elements.append(ele)

            for child_ele in AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(ele, True):
                get_child_elements(child_ele)

        for linked_ele in AllplanEleAdapter.BaseElementAdapterService.GetLinkedElements(element):
            get_child_elements(linked_ele)

        self.__show_elements(False)


    def show_elements(self):
        """ show the hidden elements
        """

        if not self.hidden_elements:
            return

        self.__show_elements(True)

        self.clear()


    def __show_elements(self,
                        show: bool):
        """ show/hide the elements

        Args:
            show: show state
        """

        AllplanIFW.VisibleService.ShowElements(AllplanEleAdapter.BaseElementAdapterList(self.__hidden_elements), show)


    def clear(self):
        """ clear the elements
        """

        self.__hidden_elements.clear()


    @property
    def get_hidden_geo_elements(self) -> list[Any]:
        """ get the geometry of the hidden elements

        Returns:
            elements
        """

        geo_elements = []

        for ele in self.__hidden_elements:
            if (geo := ele.GetGeometry()) is not None:
                geo_elements.append(geo)

        return geo_elements


    @property
    def hidden_elements(self) -> list[AllplanEleAdapter.BaseElementAdapter]:
        """ get the elements

        Returns:
            elements
        """

        return self.__hidden_elements
