""" Implementation of the mock class for the ReinforcementUtil.
"""

# pylint: disable=invalid-name

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

class ReinforcementUtilMock():
    """ Implementation of the mock class for the ReinforcementUtil
    """

    @staticmethod
    def GetNextBarPositionNumber(_doc: AllplanEleAdapter.DocumentAdapter) -> int:
        """ Get the the next bar position number

        Args:
            _doc: document of the Allplan drawing files

        Returns:
            Next bar position number
        """

        return 1

    @staticmethod
    def GetNextMeshPositionNumber(_doc: AllplanEleAdapter.DocumentAdapter) -> int:
        """ Get the the next mesh position number

        Args:
            _doc: document of the Allplan drawing files

        Returns:
            Next mesh position number
        """

        return 1

