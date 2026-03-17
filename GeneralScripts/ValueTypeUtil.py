""" Implementation of the value type utilities
"""

class ValueTypeUtil():
    """ Implementation of the value type utilities """

    @staticmethod
    def is_combobox_with_string_input(value_type_str: str) -> bool:
        """ check for combobox with string input

        Args:
            value_type_str: value type string

        Returns:
            combo box state
        """

        return value_type_str in {"stringcombobox",
                                  "dynamicstringcombobox",
                                  "pointfixturecatalogreference",
                                  "linefixturecatalogreference",
                                  "areafixturecatalogreference",
                                  "materialcatalogreference",
                                  "factorycatalogreference",
                                  "precastelementtypecatalogreference",
                                  "precastelementtypelayer",
                                  "concretegradecatalogrefenrence",
                                  "insulationcatalogrefenrence",
                                  "bricktilecatalogreference",
                                  "normcatalogreference",
                                  "surfacecatalogreference",
                                  "multimateriallayoutcatalogreference"}


    @staticmethod
    def is_string_input(value_type_str: str) -> bool:
        """ check for the value type has string input

        Args:
            value_type_str: value type string

        Returns:
            string input state
        """

        return value_type_str in {"materialbutton", "string", "text", "reinfmeshtype", "multilinestring", "codestring"} or \
               ValueTypeUtil.is_combobox_with_string_input(value_type_str)
