""" Script for BuildingElementStringTableManager functions
"""

# pylint: disable=unused-private-member

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from BuildingElementStringTable import BuildingElementStringTable

class BuildingElementStringTableManager():
    """ Singleton class for the string table manager """

    __instance = None


    def __init__(self):
        """ initialize

        Raises:
            PermissionError: raised in case of multiple init
        """

        if BuildingElementStringTableManager.__instance is not None:
            raise PermissionError("BuildingElementStringTableManager is a singleton")

        BuildingElementStringTableManager.__instance = self

        self.__use_global_string_table = True
        self.__global_string_table     : dict[str, BuildingElementStringTable] = {}


    @staticmethod
    def get_instance() -> BuildingElementStringTableManager:
        """ Get the one an only instance for the string table manager

        Returns:
            building element string table manager
        """

        if BuildingElementStringTableManager.__instance is None:
            BuildingElementStringTableManager()

        return cast(BuildingElementStringTableManager, BuildingElementStringTableManager.__instance)


    def get_global_string_table(self,
                                path: str) -> (BuildingElementStringTable | None):
        """ Get the global string table

        Args:
            path: path of the string table

        Returns:
            string table
        """

        if not self.__use_global_string_table:
            return None

        if path in self.__global_string_table:
            return self.__global_string_table[path]

        return None


    def add_string_table(self,
                         path     : str,
                         str_table: BuildingElementStringTable):
        """ Add a string table to the global string table

        Args:
            path:      path of the string table
            str_table: string table
        """

        if self.__use_global_string_table:
            self.__global_string_table[path] = str_table


    def clear_global_string_table(self):
        """ Clear the global string table
        """

        self.__global_string_table.clear()


    def set_use_global_string_table(self,
                                    use_global_table: bool):
        """ Set the state of the global string table usage

        Args:
            use_global_table: use the global string table True/False
        """

        self.__use_global_string_table = use_global_table
