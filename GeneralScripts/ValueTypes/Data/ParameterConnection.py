""" implementation of the data class for the parameter connection data
"""

from __future__ import annotations

from typing import cast

from dataclasses import dataclass, field

import hashlib

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from BuildingElementParameterListUtil import BuildingElementParameterListUtil

from Utilities.GeneralConstants import GeneralConstants

@dataclass
class ParameterConnection:
    """ implementation of the data class for the parameter connection data
    """

    __element      : AllplanEleAdapter.BaseElementAdapter = AllplanEleAdapter.BaseElementAdapter()
    uuid           : AllplanEleAdapter.GUID               = AllplanEleAdapter.GUID()
    parameters     : list[str]                            = field(default_factory = list)
    parameter_hash : str                                  = ""


    def __init__(self,
                 connection_element: AllplanEleAdapter.BaseElementAdapter,
                 parameters        : list[str]):
        """ initialize

        Args:
            connection_element: element
            parameters:         parameters
        """

        self.parameters = parameters
        self.element    = connection_element


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

        if element.IsNull():
            self.uuid           = AllplanEleAdapter.GUID()
            self.parameter_hash = ""

            return


        #----------------- set the connection data

        self.uuid = element.GetModelElementUUID()

        _, _, pyp_parameters = AllplanBaseEle.PythonPartService.GetParameter(element)

        param_str = ""

        for param in self.parameters:
            if param == GeneralConstants.PLACEMENT_MATRIX_KEY:
                param_str += str(AllplanBaseEle.PythonPartService.GetPlacementMatrix(element)).replace(" ", "").replace("\n", "")

            else:
                param_str += cast(str, BuildingElementParameterListUtil.get_value_string(pyp_parameters, param))

        self.parameter_hash = hashlib.sha224(param_str.encode('utf-8')).hexdigest()
