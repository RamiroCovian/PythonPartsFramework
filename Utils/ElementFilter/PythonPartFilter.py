""" implementation of the PythonPart filter
"""

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from ScriptObjectInteractors.BaseFilterObject import BaseFilterObject

class PythonPartFilter(BaseFilterObject):
    """ implementation of the PythonPart filter
    """

    def __call__(self, element: AllplanEleAdapter.BaseElementAdapter) -> bool:
        """ execute the filtering

        Args:
            element: element to filter

        Returns:
            element fulfills the filter: True/False
        """

        return AllplanBaseEle.PythonPartService.IsPythonPartElement(element) or \
               AllplanBaseEle.PythonPartService.IsPythonPartGroupElement(element)
