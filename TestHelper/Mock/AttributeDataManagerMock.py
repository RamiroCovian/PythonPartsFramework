""" Implementation of the attribute data manager mock.
"""

class AttributeDataManagerMock():
    """ Implementation of the attribute data manager mock
    """

    @staticmethod
    def GetAttributeName(attibute_id: int) -> str:
        """ get the attribute name

        Args:
            attibute_id: attribute id

        Returns:
            attribute name
        """

        return str(attibute_id)
