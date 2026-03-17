""" implementation of the list with the data of the modification elements
"""

from typing import cast

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

class ModificationElementList(list[(str | AllplanEleAdapter.BaseElementAdapter)]):
    """ implementation of the list with the data of the modification elements
    """

    EMPTY_GUID = "00000000-0000-0000-0000-000000000000--0"

    def __init__(self,
                 elements: (list[(str | AllplanEleAdapter.BaseElementAdapter)] | None) = None):
        """ initialize

        Args:
            elements: elements to modify
        """

        if elements is None:
            return

        for ele in elements:
            if isinstance(ele, AllplanEleAdapter.BaseElementAdapter):
                self.append(ele.GetNOIGUID())
            else:
                self.append(ele)


    def is_modification_element(self) -> bool:
        """ check for an existing modification element

        Returns:
            modification element state
        """

        return self and self[0] != self.EMPTY_GUID   #type: ignore


    def get_base_element_adapter(self,
                                 doc: AllplanEleAdapter.DocumentAdapter) -> AllplanEleAdapter.BaseElementAdapter:
        """ get the BaseElementAdapter for the index

        Args:
            doc: document of the Allplan drawing files

        Returns:
            BaseElementAdapter
        """

        return AllplanEleAdapter.BaseElementAdapter.FromNOIGUID(cast(str, self[0]), doc)
