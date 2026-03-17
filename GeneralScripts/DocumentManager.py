""" Script for DocumentManager functions
"""

# pylint: disable=unused-private-member

from __future__ import annotations

from typing import cast

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from TypeCollections.ModificationElementList import ModificationElementList

class DocumentManager():
    """ Singleton class for the document manager """

    if not "DocumentManager__instance" in globals():
        globals()["DocumentManager__instance"] = None

    def __init__(self):
        """ Constructor

            Raises:
                PermissionError: if no instance exist
        """

        if globals()["DocumentManager__instance"] is not None:
            raise PermissionError("DocumentManager is a singleton")

        globals()["DocumentManager__instance"] = self

        self.__document           = AllplanEleAdapter.DocumentAdapter()
        self.__pythonpart_element = AllplanEleAdapter.BaseElementAdapter()
        self.__asso_ref_element   = AllplanEleAdapter.BaseElementAdapter()


    @staticmethod
    def get_instance() -> DocumentManager:
        """ Get the one an only instance for the document manager

        Returns:
            DocumentManager object
        """

        if globals()["DocumentManager__instance"] is None:
            DocumentManager()

        return globals()["DocumentManager__instance"]


    @property
    def document(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the document

        Returns:
            get the document
        """

        return self.__document


    @document.setter
    def document(self,
                 document: AllplanEleAdapter.DocumentAdapter):
        """ set the document

        Args:
            document: document
        """

        self.__document = document


    @property
    def pythonpart_element(self) -> AllplanEleAdapter.BaseElementAdapter:
        """ get the PythonPart element

        Returns:
            get the PythonPart element
        """

        return self.__pythonpart_element


    def clear_pythonpart_element(self):
        """ clear the PythonPart element
        """

        self.__pythonpart_element = AllplanEleAdapter.BaseElementAdapter()


    def set_pythonpart_element(self,
                               modification_ele_list: ModificationElementList):
        """ set the PythonPart element from the model element UUID

        Args:
            modification_ele_list: list with the modification elements in modification mode
        """

        if self.document is None:
            return

        if not modification_ele_list.is_modification_element():
            self.__pythonpart_element = AllplanEleAdapter.BaseElementAdapter()

        elif isinstance(modification_ele_list[0], AllplanEleAdapter.BaseElementAdapter):
            self.__pythonpart_element = cast(AllplanEleAdapter.BaseElementAdapter, modification_ele_list[0])

        else:
            self.__pythonpart_element = modification_ele_list.get_base_element_adapter(self.document)

    @property
    def asso_ref_element(self) -> AllplanEleAdapter.BaseElementAdapter:
        """ get the asso_ref element

        Returns:
            get the asso_ref element
        """

        return self.__asso_ref_element

    @asso_ref_element.setter
    def asso_ref_element(self,
                         asso_ref_element: AllplanEleAdapter.BaseElementAdapter):
        """ set the asso_ref element

        Args:
            asso_ref_element: asso_ref_element
        """

        self.__asso_ref_element = asso_ref_element

    def clear_asso_ref_element(self):
        """ clear the asso_ref element
        """

        self.__asso_ref_element = AllplanEleAdapter.BaseElementAdapter()
