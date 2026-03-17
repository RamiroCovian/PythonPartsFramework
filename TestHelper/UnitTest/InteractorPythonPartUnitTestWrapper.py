""" implementation of the interactor PythonPart unit test wrapper
"""

from typing import Any

from .StandardPythonPartUnitTestWrapper import StandardPythonPartUnitTestWrapper

class InteractorPythonPartUnitTestWrapper(StandardPythonPartUnitTestWrapper):
    """ implementation of the interactor PythonPart unit test wrapper
    """

    def modify_element_property(self,
                                page : int,
                                name : str,
                                value: Any):
        """ Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """

        self.build_ele_input.modify_element_property(page, name, value)

        interactor = self.build_ele_input.interactor

        if (sub_interactor := getattr(interactor, "script_object_interactor", None)) is not None:
            if (build_ele_input := getattr(sub_interactor, "build_ele_input", None)) is not None:
                build_ele_input.palette_service.update_palette(-1, False)

                return

        if (palette_service := getattr(interactor, "palette_service", None)) is not None:
            palette_service.update_palette(-1, False)
