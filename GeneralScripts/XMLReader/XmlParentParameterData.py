""" implementation of the data for a xml parent parameter
"""

from typing import Any

from dataclasses import dataclass, field

@dataclass
class XmlParentParameterData():
    """ implementation of the data for a xml parent parameter
    """

    expander_name         : str               = ""
    row_name              : str               = ""
    row_state_key         : str               = ""
    expander_state_key    : str               = ""
    radio_group_name      : str               = ""
    radio_group_text      : str               = ""
    radio_group_selection : (list[Any] | Any) = field(default_factory = list)


    def reset_expander(self):
        """ reset the expander data
        """

        self.expander_name      = ""
        self.expander_state_key = ""


    def reset_row(self):
        """ reset the row data
        """

        self.row_name      = ""
        self.row_state_key = ""


    def reset_radio_group(self):
        """ reset the radio group data
        """

        self.radio_group_text      = ""
        self.radio_group_name      = ""
        self.radio_group_selection = []
