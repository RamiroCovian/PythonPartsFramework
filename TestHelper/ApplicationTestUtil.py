""" implementation of the application test utilities
"""

# pylint: disable=import-outside-toplevel

class ApplicationTestUtil():
    """ implementation of the application test utilities
    """

    @staticmethod
    def init_application_test() -> object:
        """ initialize the application test

        Args:
            load_resources: load the resources

        Returns:
            Allplan document
        """

        import NemAll_Python_Reinforcement as AllplanReinf

        doc = AllplanReinf.InitApplicationtest()

        from TypeCollections.ModificationElementList import ModificationElementList

        from DocumentManager import DocumentManager

        DocumentManager.get_instance().document = doc
        DocumentManager.get_instance().set_pythonpart_element(ModificationElementList())

        return doc
