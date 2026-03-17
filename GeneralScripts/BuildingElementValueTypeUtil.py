"""
Implementation of the value type utilities
"""

class BuildingElementValueTypeUtil():
    """
    Implementation of the value type utilities
    """

    @staticmethod
    def is_float_type(value_type):
        """
        Check for a float value type
        """

        return value_type in ("angle",
                              "anglecombobox",
                              "double",
                              "doublecombobox",
                              "length",
                              "lengthcombobox",
                              "area",
                              "volume",
                              "weight",
                              "reinfbendingroller",
                              "reinfconcretecover",
                              "reinfbardiameter",
                              "reinfhooklength")
