""" implementation of the time stamp connection value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from DocumentManager import DocumentManager

from Utilities.GeneralConstants import GeneralConstants

from ..Data.ParameterConnection import ParameterConnection

from ..ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

class ParameterConnectionImpl(ParameterPropertyValueType):
    """ implementation of the time stamp connection value type
    """

    @staticmethod
    def to_string(value: ParameterConnection) -> str:
        """ convert the value to a string

        Args:
            value: new value

        Returns:
            list as string
        """

        return f"{','.join(value.parameters)}{GeneralConstants.TEXT_SEPARATOR}{value.uuid}" \
               f"{GeneralConstants.TEXT_SEPARATOR}{value.parameter_hash}"


    @staticmethod
    def get_value(value_str: str) -> ParameterConnection:
        """ get the value from a string

        Args:
            value_str: value string

        Returns:
            value
        """

        if GeneralConstants.TEXT_SEPARATOR not in value_str:
            return ParameterConnection(AllplanEleAdapter.BaseElementAdapter(),
                                      [item.strip() for item in value_str.split(",")])

        parts = value_str.split(GeneralConstants.TEXT_SEPARATOR)

        uuid = AllplanEleAdapter.GUID.FromString(parts[1])

        return ParameterConnection(AllplanEleAdapter.BaseElementAdapter.FromGUID(uuid, DocumentManager.get_instance().document),
                                   [item.strip() for item in parts[0].split(",")])
