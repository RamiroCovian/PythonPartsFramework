"""
Implementation of the building element counter
"""

from collections import Counter

class BuildingElementCounter():
    """
    Definition of class BuildingElementCounter
    """

    def __init__(self):
        """
        Initialisation of class BuildingElementConunter
        """
        self.m_ele_count = Counter()

    def __repr__(self):
        return "%s(\n"     \
               "   %s\n"   \
               ")\n"       \
               % (self.__class__.__name__,
                  self.m_ele_count)

    def check_index(self, build_ele):
        """
        Checks, whether the current element has the index from the palette

        Args:
            build_ele:  building element

        Returns:
            element has the palette index
        """

        script_name = build_ele.script_name

        self.m_ele_count.update((script_name,))

        prop = getattr(build_ele, "__ElementIndex__", None)

        if prop is None:
            return True

        index = prop.value

        return index == self.m_ele_count[script_name]
