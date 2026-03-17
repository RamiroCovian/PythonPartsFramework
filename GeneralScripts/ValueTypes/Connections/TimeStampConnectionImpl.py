""" implementation of the time stamp connection value type
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from DocumentManager import DocumentManager

from Utilities.GeneralConstants import GeneralConstants

from ..Data.TimeStampConnection import TimeStampConnection

from ..ParameterPropertyValueType import ParameterPropertyValueType

if TYPE_CHECKING:
    from ParameterProperty import ParameterProperty

class TimeStampConnectionImpl(ParameterPropertyValueType):
    """ implementation of the time stamp connection value type
    """

    @staticmethod
    def to_string(value: (TimeStampConnection | list[TimeStampConnection])) -> str:
        """ convert the value to a string

        Args:
            value: new value

        Returns:
            list as string
        """

        if not isinstance(value, list):
            return f"{value.uuid}{GeneralConstants.TEXT_SEPARATOR}{value.time_stamp}"

        return ";".join(f"{item.uuid}|{item.time_stamp}" for item in value)


    @staticmethod
    def get_value(value_str: str) -> (TimeStampConnection | list[TimeStampConnection]):
        """ get the value from a string

        Args:
            value_str: value string

        Returns:
            value
        """

        if value_str == GeneralConstants.EMPTY_LIST:
            return []

        if not (value_str := value_str.replace("(",  "").replace(")", "")):
            return TimeStampConnection(AllplanEleAdapter.BaseElementAdapter())

        if GeneralConstants.LIST_ITEM_SEPARATOR not in value_str:
            if not (uuid_str := value_str.split(GeneralConstants.TEXT_SEPARATOR, 1)[0]):
                return TimeStampConnection(AllplanEleAdapter.BaseElementAdapter())

            uuid = AllplanEleAdapter.GUID.FromString(uuid_str)

            return TimeStampConnection(AllplanEleAdapter.BaseElementAdapter.FromGUID(uuid, DocumentManager.get_instance().document))

        return [cast(TimeStampConnection, TimeStampConnectionImpl.get_value(item)) for item in value_str.split(";")]
