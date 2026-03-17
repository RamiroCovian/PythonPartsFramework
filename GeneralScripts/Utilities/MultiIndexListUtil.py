""" implementation of the utilities for the multi index list
"""

from typing import Any

from BuildingElementStringTable import BuildingElementStringTable
from ParameterProperty import ParameterProperty

from ValueTypes.MultiIndex import MultiIndex

class MultiIndexListUtil():
    """ implementation of the utilities for the multi index list
    """

    @staticmethod
    def get_value(prop            : ParameterProperty,
                  multi_index     : MultiIndex,
                  global_str_table: BuildingElementStringTable) -> tuple[Any, bool]:
        """ get the value for the indexes

        Args:
            prop:             parameter property
            multi_index:      multi indexes
            global_str_table: global string table

        Returns:
            value, varied state
        """

        #----------------- possible index problem in case of dynamic list

        values = set()

        count = len(prop.value)

        for index_from, index_to in multi_index:
            for index in range(index_from, index_to + 1):
                if index <= count:
                    values.add(prop.value[index - 1])
                elif not values:
                    values.add("")

        if len(values) > 1:
            return global_str_table.get_string("e_VARIED", "*varied*"), True

        return next(iter(values)), False


    @staticmethod
    def delete_values(prop       : ParameterProperty,
                      multi_index: MultiIndex):
        """ delete the value for the indexes

        Args:
            prop:        parameter property
            multi_index: multi indexes
        """

        del_indexes = set()

        count = len(prop.value)

        for index_from, index_to in multi_index:
            for index in range(index_from, index_to + 1):
                if index < count:
                    del_indexes.add(index)

        prop.value = [value for index, value in enumerate(prop.value) if index not in del_indexes]
