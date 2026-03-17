""" implementation of the filter collection
"""

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from ScriptObjectInteractors.BaseFilterObject import BaseFilterObject

class FilterCollection(BaseFilterObject):
    """ implementation of the filter collection
    """

    def __init__(self):
        """ initialize
        """

        self.filters : list[(BaseFilterObject | AllplanIFW.SelectionQuery)] = []


    def append(self,
               ele_filter: (BaseFilterObject | AllplanIFW.SelectionQuery)):
        """ append a filter

        Args:
            ele_filter: filter
        """

        self.filters.append(ele_filter)


    def __call__(self, element: AllplanEleAdapter.BaseElementAdapter) -> bool:
        """ execute the filter collection

        Args:
            element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

        return any(ele_filter(element) for ele_filter in self.filters)
