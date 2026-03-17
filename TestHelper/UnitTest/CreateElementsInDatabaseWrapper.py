""" implementation of the element in database creation helper
"""

from typing import Any

import gc

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Utility as AllplanUtil

from TestHelper.UnitTest.StandardPythonPartUnitTestWrapper import StandardPythonPartUnitTestWrapper

class CreateElementsInDatabaseWrapper():
    """ implementation of the element in database creation helper
    """

    @staticmethod
    def create_pythonpart(doc              : AllplanEleAdapter.DocumentAdapter,
                          relative_pyp_name: str,
                          modify_parameter : (list[tuple[str, Any]] | None) = None,
                          clear_document   : bool                           = False) -> AllplanEleAdapter.BaseElementAdapterList:
        """ create the PythonPart for the test

        Args:
            doc:               document of the Allplan drawing files
            relative_pyp_name: name of the pyp file including path relative to the ...\etc folder
            modify_parameter:  list with the parameter to modify (name, value)
            clear_document:    clear the document state

        Returns:
            created PythonPart element
        """

        #----------------- forge the garbage collector
        #                  (need to call __del__ with ClearUnitTestDocument in StandardPythonPartUnitTestWrapper
        #                   before loading new data)

        gc.collect()


        #----------------- create the PythonPart

        if clear_document:
            AllplanUtil.ClearUnitTestDocument()

        unit_test_wrapper = StandardPythonPartUnitTestWrapper(relative_pyp_name, doc)

        for name, value in (modify_parameter or []):
            unit_test_wrapper.modify_element_property(0, name, value)

        unit_test_wrapper.create_elements_in_db_by_api(False)

        return unit_test_wrapper.get_elements_from_db()


    @staticmethod
    def import_symbol(name                    : str,
                      clear_document          : bool,
                      update_arch_ele_geometry: bool = False) -> AllplanEleAdapter.BaseElementAdapterList:
        """ import a symbol in the data base for the test

        Args:
            name:                     name of the modified property
            clear_document:           clear the document state
            update_arch_ele_geometry: Update the geometry elements after load (e.g. adapts slabs to the plane

        Returns:
            returns elements of the symbol
        """

        #----------------- forge the garbage collector
        #                  (need to call __del__ with ClearUnitTestDocument in StandardPythonPartUnitTestWrapper
        #                   before loading new data)

        gc.collect()

        return AllplanUtil.LoadSymbolForUnitTest(name, clear_document, update_arch_ele_geometry)
