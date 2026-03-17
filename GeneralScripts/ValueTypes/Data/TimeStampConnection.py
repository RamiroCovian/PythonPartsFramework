""" implementation of the data class for the time stamp connection data
"""

from __future__ import annotations

from dataclasses import dataclass

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

@dataclass
class TimeStampConnection:
    """ implementation of the data class for the time stamp connection data
    """

    __element  : AllplanEleAdapter.BaseElementAdapter = AllplanEleAdapter.BaseElementAdapter()
    uuid       : AllplanEleAdapter.GUID               = AllplanEleAdapter.GUID()
    time_stamp : int                                  = 0


    def __init__(self,
                 connection_element: AllplanEleAdapter.BaseElementAdapter):
        """ initialize

        Args:
            connection_element: element
        """

        self.element = connection_element


    @property
    def element(self) -> AllplanEleAdapter.BaseElementAdapter:
        """ get the element

        Returns:
            element
        """

        return self.__element


    @element.setter
    def element(self,
                element: AllplanEleAdapter.BaseElementAdapter):
        """ set the element

        Args:
            element: element
        """

        self.__element = element

        if element.IsValid():
            self.uuid       = element.GetModelElementUUID()
            self.time_stamp = element.GetTimeStamp()
        else:
            self.uuid       = AllplanEleAdapter.GUID()
            self.time_stamp = 0
