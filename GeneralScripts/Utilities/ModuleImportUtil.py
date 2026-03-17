""" implementation of the module import utility
"""
from types import ModuleType

class ModuleImportUtil():
    """ implementation of the module import utility
    """


    @staticmethod
    def import_from_abs_path(module_name: str) -> ModuleType:
        """ import the module from an absolute path

        Args:
            module_name: module name

        Returns:
            loaded module
        """

        ip_vs = module_name.lower().find("\\visualscripts\\")

        script_name = module_name[ip_vs + 15:]

        islash = script_name.rfind("\\")

        script_name = script_name.replace("\\", ".")

        return __import__(script_name, fromlist = script_name[islash + 1:])
