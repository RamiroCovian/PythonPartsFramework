""" Implementation of the reinforcement definition class
"""

from typing import Union, Dict, Any

from xml.etree import ElementTree

from XMLReader.XmlElementTreeUtil import XmlElementTreeUtil

class ReinforcementDefinition():
    """ Implementation of the reinforcement definition class
    """

    def __init__(self):
        """ initialize
        """
        self.__definition_dict = {}
        self.__param_dict      = None


    def read_data(self,
                  param: ElementTree.Element):
        """ Read the data nodes from the xml file

        Args:
            param: data node
        """

        for _, name, value in XmlElementTreeUtil.get_elements(param):
            self.__definition_dict[name] = value


    def set_parameter_dictionary(self,
                                 param_dict: Dict[str, str]):
        """ Set the parameter dictionary

        Args:
            param_dict: parameter dictionary
        """

        self.__param_dict = param_dict


    def get_value(self,
                  name   : str,
                  default: Union[int, float] = 0) -> Union[int, float]:
        """ Get the value from the name

        Args:
            name:    name of the value
            default: default value

        Returns:
            value
        """

        if not name in self.__definition_dict:
            return default

        return eval(self.__definition_dict[name], self.__param_dict)


    def get_attribute(self,
                      name   : str,
                      default: Any = None) -> Any:
        """ Get the attribute from the name

        Args:
            name:    name of the attribute
            default: default value

        Returns:
            attribute
        """

        if (attr := self.__definition_dict.get(name, None)) is not None:
            return attr

        return default


    def get_attribute_count(self) -> int:
        """ Get the attribute from the name

        Returns:
            attribute count
        """

        return len(self.__definition_dict)
