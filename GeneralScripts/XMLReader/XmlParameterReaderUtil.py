""" implementation of the parameter reader utilities
"""

from typing import Any

from xml.etree import ElementTree

from BuildingElement import BuildingElement
from ControlProperties import ControlProperties

from Utilities.SplitUtil import SplitUtil
from Utilities.GeneralConstants import GeneralConstants

from ValueTypes.ValueTypeUtils.BaseStringToValueConverter import BaseStringToValueConverter

from ValueTypes.ParameterPropertyValueType import ParameterPropertyValueType
from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes

from .IncludeData import IncludeData
from .XmlElementTreeUtil import XmlElementTreeUtil

ORG_LIST_KEY  = "$list_"
TEMP_LIST_KEY = "@list_"

class XmlParameterReaderUtil():
    """ implementation of the parameter reader utilities
    """

    @staticmethod
    def get_sub_member_text(value_type: ParameterPropertyValueType,
                            ctrl_prop : ControlProperties):
        """ get the sub member text (e. g. for the coordinates of a point)

        Args:
            value_type: value type
            ctrl_prop:  control properties
        """

        if GeneralConstants.SUB_TEXT_SEPARATOR not in ctrl_prop.text:
            return

        sub_texts = ctrl_prop.text.split(GeneralConstants.SUB_TEXT_SEPARATOR)

        name = f"{ctrl_prop.value_name}."

        parts = []

        if value_type in (ParameterPropertyValueTypes.POINT2D, ParameterPropertyValueTypes.VECTOR2D):
            parts = ["X", "Y"]

        elif value_type in (ParameterPropertyValueTypes.POINT3D, ParameterPropertyValueTypes.VECTOR3D):
            parts = ["X", "Y", "Z"]

        elif value_type in (ParameterPropertyValueTypes.LINE2D, ParameterPropertyValueTypes.LINE3D):
            parts = ["StartPoint", "EndPoint"]

        elif value_type == ParameterPropertyValueTypes.CIRCLE2D:
            parts = ["CenterPoint", "MajorRadius"]

        elif value_type == ParameterPropertyValueTypes.CIRCLE3D:
            parts = ["CenterPoint", "MajorRadius", "ZAxis"]

        elif value_type == ParameterPropertyValueTypes.ARC2D:
            parts = ["CenterPoint", "MinorRadius", "MajorRadius", "AxisAngle", "StartAngle", "EndAngle"]

        elif value_type == ParameterPropertyValueTypes.ARC3D:
            parts = ["CenterPoint", "MinorRadius", "MajorRadius", "StartAngle", "EndAngle", "XDirection", "ZAxis"]

        elif value_type == ParameterPropertyValueTypes.AXISPLACEMENT3D:
            parts = ["Origin", "XDirection", "ZDirection"]

        elif value_type == ParameterPropertyValueTypes.PLANE3D:
            parts = ["Point", "Vector"]

        if parts:
            ctrl_prop.member_text = {name + part: text for part,text in zip(parts, sub_texts)}


    @staticmethod
    def get_radio_button_group_selection(build_ele: BuildingElement,
                                         value_str: str) -> list[Any]:
        """ get the radio button group selection

        Args:
            build_ele: building element with the parameter properties
            value_str: value string

        Returns:
            group selection
        """

        if value_str.startswith("["):
            result = []

            for row_item in SplitUtil.split_by_comma(value_str.strip()[1:-1]):
                col_items = SplitUtil.split_by_comma(row_item.strip("[]"))

                col_result = [BaseStringToValueConverter.to_auto(col_item) if (value := build_ele.get_constant(col_item)) is None \
                              else value for col_item in col_items]

                if len(col_result) > 1:
                    result.append(col_result)
                else:
                    result.append(col_result[0])

            return result

        return BaseStringToValueConverter.to_auto(value_str) if (value := build_ele.get_constant(value_str)) is None else value


    @staticmethod
    def get_visible(param         : ElementTree.Element,
                    name          : str,
                    include_data  : IncludeData,
                    has_value_type: str = '') -> str:
        """ get the visible data

        Args:
            param:          parameter
            name:           name of the modified property
            include_data:   include data
            has_value_type: tag must assigned to the value type

        Returns:
            visible data
        """

        visible = XmlElementTreeUtil.get_tag_data(param, "Visible", has_value_type,
                                                  allow_multiline_text = True)

        if include_data.is_include:
            visible = XmlParameterReaderUtil.insert_name_postfix(visible, include_data.name_postfix)

        if not include_data.incl_visible:
            return visible

        if include_data.name_postfix:
            name = name[:-len(include_data.name_postfix)]

        visible_cond_all = include_data.incl_visible.get("__ALL__", "")

        if (visible_cond := include_data.incl_visible.get(name, None)) is None:
            return visible_cond_all or visible

        return visible_cond


    @staticmethod
    def insert_name_postfix(text        : str,
                            name_postfix: str) -> str:
        """ insert the name postfix at the position defined by a $

        Args:
            text:         text
            name_postfix: name postfix

        Returns:
            adapted text
        """

        if ORG_LIST_KEY in text:
            return text.replace(ORG_LIST_KEY, TEMP_LIST_KEY).replace("$", name_postfix).replace(TEMP_LIST_KEY, ORG_LIST_KEY)

        return text.replace("$", name_postfix)
