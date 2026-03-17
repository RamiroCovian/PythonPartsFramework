"""
Implementation of the string table service
"""

from enum import IntEnum
import ntpath

import NemAll_Python_BaseElements as AllplanBaseEle

class SectionFillType(IntEnum):
    """
    Class with the definition of the section fill types

    The fill types can be used to set the
    filling of section surfaces
    """

    EMPTY       = 0
    FILLING     = 1
    HATCHING    = 2
    PATTERN     = 3
    FACESTYLE   = 4
    BITMAP      = 5


class SectionFill():
    """
    Definition of class SectionFill
    """

    def __init__(self, section_type, number):
        self.m_type = section_type
        self.m_number = number
        self.m_bitmap = ''

    def __repr__(self):
        description = '<%s>\n'\
            'type   = %s\n'\
            'number = %s\n'\
            'bitmap = %s\n'\
            % (self.__class__.__name__,
               self.m_type,
               self.m_number,
               self.m_bitmap)
        return description

    def set_type(self, section_type):
        """
        Set the type

        Args:
            type: type of section_fill
        """
        self.m_type = section_type

    def get_type(self):
        """
        Get type

        Returns:
            type of section_fill
        """
        return self.m_type

    def set_number(self, number):
        """
        Set the number

        Args:
            number: number of section_fill
        """
        self.m_number = number

    def get_number(self):
        """
        Get number

        Returns:
            number of section_fill
        """
        return self.m_number

    def set_bitmap(self, bitmap):
        """
        Set the bitmap

        Args:
            bitmap: bitmap of section_fill
        """
        self.m_bitmap = bitmap

    def get_bitmap(self):
        """
        Get bitmap

        Returns:
            bitmap of section_fill
        """
        return self.m_bitmap

    @staticmethod
    def add_section_filling(elem,section_fill):
        """
        Add section filling to element

        Args:
            elem:         element to add section fill
            section_fill: section fill
        """
        attr_list = []

        if section_fill.type == SectionFillType.FILLING:
            attr_list.append(AllplanBaseEle.AttributeInteger(118, 3))
            attr_list.append(AllplanBaseEle.AttributeInteger(252, section_fill.number))
        elif section_fill.type == SectionFillType.HATCHING:
            attr_list.append(AllplanBaseEle.AttributeInteger(118, 2))
            attr_list.append(AllplanBaseEle.AttributeInteger(124, section_fill.number))
        elif section_fill.type == SectionFillType.PATTERN:
            attr_list.append(AllplanBaseEle.AttributeInteger(118, 1))
            attr_list.append(AllplanBaseEle.AttributeInteger(126, section_fill.number))
        elif section_fill.type == SectionFillType.FACESTYLE:
            attr_list.append(AllplanBaseEle.AttributeInteger(125, section_fill.number))
        elif section_fill.type == SectionFillType.BITMAP:
            path, file = ntpath.split(section_fill.m_bitmap)
            attr_list.append(AllplanBaseEle.AttributeString(333, path))
            attr_list.append(AllplanBaseEle.AttributeString(336, file))

        if len(attr_list)!= 0:
            attr_set_list = []
            attr_set_list.append(AllplanBaseEle.AttributeSet(attr_list))
            attributes = AllplanBaseEle.Attributes(attr_set_list)
            elem.SetAttributes(attributes)

    #----------------- property definition
    type   = property(get_type, set_type)
    number = property(get_number, set_number)
    bitmap = property(get_bitmap, set_bitmap)


    @staticmethod
    def add_section_filling_attribute(elem, section_fill, attr_list):
        """
        Add section filling and attribues to element

        Args:
            elem:         element to add section fill
            section_fill: section fill
            attr_list:    attrribue list
        """

        if section_fill:
            if section_fill.type == SectionFillType.FILLING:
                attr_list.append(AllplanBaseEle.AttributeInteger(118, 3))
                attr_list.append(AllplanBaseEle.AttributeInteger(252, section_fill.number))
            elif section_fill.type == SectionFillType.HATCHING:
                attr_list.append(AllplanBaseEle.AttributeInteger(118, 2))
                attr_list.append(AllplanBaseEle.AttributeInteger(124, section_fill.number))
            elif section_fill.type == SectionFillType.PATTERN:
                attr_list.append(AllplanBaseEle.AttributeInteger(118, 1))
                attr_list.append(AllplanBaseEle.AttributeInteger(126, section_fill.number))
            elif section_fill.type == SectionFillType.FACESTYLE:
                attr_list.append(AllplanBaseEle.AttributeInteger(125, section_fill.number))
            elif section_fill.type == SectionFillType.BITMAP:
                path, file = ntpath.split(section_fill.m_bitmap)
                attr_list.append(AllplanBaseEle.AttributeString(333, path))
                attr_list.append(AllplanBaseEle.AttributeString(336, file))

        if len(attr_list)!= 0:
            attr_set_list = []
            attr_set_list.append(AllplanBaseEle.AttributeSet(attr_list))
            attributes = AllplanBaseEle.Attributes(attr_set_list)
            elem.SetAttributes(attributes)

    #----------------- property definition
    type   = property(get_type, set_type)
    number = property(get_number, set_number)
    bitmap = property(get_bitmap, set_bitmap)

