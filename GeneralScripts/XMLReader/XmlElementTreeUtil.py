""" Script for XmlElementTreeUtil
"""

from typing import Any

from xml.etree import ElementTree

from _collections_abc import Generator, Iterator

from TraceService import TraceService, TraceLevel

from Utilities.GeneralConstants import GeneralConstants

from ValueTypes.ValueTypeUtils.StringToValueUtil import StringToValueUtil

class XmlElementTreeUtil():
    """ Definition of class XmlElementTreeUtil
    """

    @staticmethod
    def parse(file_name: str) -> ElementTree.ElementTree:
        """ Parse the xml file

        Args:
            file_name: Name of the xml file

        Returns:
            element tree
        """

        return ElementTree.parse(file_name)


    @staticmethod
    def get_elements_by_tag_name(node: ElementTree.ElementTree,
                                 tag : str) -> Generator[ElementTree.Element, None, None]:
        """ Get the elements for the tag

        Args:
            node: Check this parameter node for tag
            tag:  Tag

        Returns:
            element
        """

        return node.iter(tag)


    @staticmethod
    def get_elements(node: ElementTree.Element) -> Iterator[tuple[ElementTree.Element, str, (str | None)]]:
        """ Get the elements for the node

        Args:
            node: Check this parameter node for tag

        Yield:
            element
        """

        for ele in node.findall("./"):
            yield (ele, ele.tag, ele.text)


    @staticmethod
    def get_elements_with_attrib(node: ElementTree.Element) -> Iterator[tuple[ElementTree.Element, str, (str | None), dict[str, str]]]:
        """ Get the elements and the attributes for the node

        Args:
            node: Check this parameter node for tag

        Yield:
            element
        """

        for ele in node.findall("./"):
            yield (ele, ele.tag, ele.text, ele.attrib)


    @staticmethod
    def get_element(node: (ElementTree.ElementTree | ElementTree.Element),
                    tag : str) -> (ElementTree.Element | None):
        """ Get the first element for the tag

        Args:
            node: Check this parameter node for tag
            tag:  Tag

        Returns:
            element
        """

        elements = node.iter(tag)

        return next((ele for ele in elements), None)


    @staticmethod
    def get_tag_data(node                : (ElementTree.ElementTree | ElementTree.Element),
                     tag                 : str,
                     has_value_type      : str  = '',
                     allow_multiline_text: bool = False) -> str:
        """ Extract tag data

        Args:
            node:                 Check this parameter node for tag
            tag:                  tag
            has_value_type:       tag must assigned to the value type
            allow_multiline_text: allow multiline state

        Returns:
            returns
        """

        if not (tag_data := node.findall(f".{tag}") if has_value_type else list(node.iter(tag))):
            return ""

        if tag_data[0].text is None:
            return ""

        return tag_data[0].text.strip("\n ") if allow_multiline_text else \
               tag_data[0].text.replace("\n", "")


    @staticmethod
    def get_attribute(node     : ElementTree.Element,
                      attribute: str) -> (str | None):
        """ Extract tag attribute

        Args:
            node:      Check this parameter node for tag
            attribute: Attribute

        Returns:
            tag attribute
        """

        return node.attrib.get(attribute)


    @staticmethod
    def get_text_id_tag_data(node           : ElementTree.Element,
                             parent_node_tag: str = '') -> tuple[(str | None), str]:
        """ Extract tag data for Text and TextId

        Args:
            node:            Check this parameter node for tag
            parent_node_tag: Stop/search criteria for traverse of XML tree

        Returns:
            tag data as string
        """

        text_param    = node.findall(".Text") if parent_node_tag else list(node.iter("Text"))
        text_id_param = node.findall(".TextId") if parent_node_tag else list(node.iter("TextId"))

        text = text_param[0].text if text_param else ""


        #----------------- Text tag is used

        if not text_id_param:
            if text:
                if text.strip(" "):
                    TraceService().trace(TraceLevel.MISSING_TEXT_ID, "missing <TextId/> for: ", text)

                return text, ""

            return "", ""


        #----------------- TextId tag is used

        if (text_id := text_id_param[0].text):
            return text, text_id.replace(",", GeneralConstants.TEXT_SEPARATOR)

        TraceService().trace(TraceLevel.MISSING_TEXT_ID, "Empty text ID in the pyp file")

        return "Empty TextId", ""


    @staticmethod
    def get_bool_value(node           : ElementTree.Element,
                       name           : str,
                       parent_node_tag: str  = '',
                       default_value  : bool = False) -> bool:
        """ Extract boolean value of node

        Args:
            node:            Starting node.
            name:            name of the modified property
            parent_node_tag: Stop/search criteria for traverse of XML tree
            default_value:   default value

        Returns:
            bool value
        """

        if not (value_str := XmlElementTreeUtil.get_tag_data(node, name, parent_node_tag)):
            return default_value

        return StringToValueUtil.get_bool_value_from_str(value_str)


    @staticmethod
    def __get_value(node           : ElementTree.Element,
                    name           : str,
                    default_value  : Any,
                    parent_node_tag: str,
                    converter      : Any) -> Any:
        """ Extract value of node

        Args:
            node:            Starting node.
            name:            name of the modified property
            default_value:   Default value
            parent_node_tag: Stop/search criteria for traverse of XML tree
            converter:       Converter function for the string to value conversion

        Returns:
            value
        """

        if not (value_str := XmlElementTreeUtil.get_tag_data(node, name, parent_node_tag)):
            return default_value

        try:
            return converter(value_str)

        except ValueError:
            print()
            print(f"Name {name}: {value_str} isn't type of {converter}")
            print()

        return default_value


    @staticmethod
    def get_float_value(node           : ElementTree.Element,
                        name           : str,
                        default_value  : float,
                        parent_node_tag: str = '') -> float:
        """ Extract float value of node

        Args:
            node:            Starting node.
            name:            name of the modified property
            default_value:   Default value
            parent_node_tag: Stop/search criteria for traverse of XML tree

        Returns:
            float value
        """

        return XmlElementTreeUtil.__get_value(node, name, default_value, parent_node_tag, float)


    @staticmethod
    def get_int_value(node           : ElementTree.Element,
                      name           : str,
                      default_value  : int,
                      parent_node_tag: str = '') -> int:
        """ Extract int value of node

        Args:
            node:            Starting node.
            name:            name of the modified property
            default_value:   Default value
            parent_node_tag: Stop/search criteria for traverse of XML tree

        Returns:
            int value
        """

        return XmlElementTreeUtil.__get_value(node, name, default_value, parent_node_tag, int)


    @staticmethod
    def get_str_value(node           : ElementTree.Element,
                      name           : str,
                      default_value  : str,
                      parent_node_tag: str = '') -> str:
        """ Extract string value of node

        Args:
            node:            Starting node.
            name:            name of the modified property
            default_value:   Default value
            parent_node_tag: Stop/search criteria for traverse of XML tree

        Returns:
            string value
        """

        return XmlElementTreeUtil.__get_value(node, name, default_value, parent_node_tag, str)


    @staticmethod
    def get_children_by_title(node: (ElementTree.Element | ElementTree.ElementTree),
                              name: str) -> Iterator[ElementTree.Element]:
        """ Extract sub children of a node

        Args:
            node: Starting node.
            name: name of the modified property

        Yield:
            child
        """

        yield from node.findall(f".{name}")
