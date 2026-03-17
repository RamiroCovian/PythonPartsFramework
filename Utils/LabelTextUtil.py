""" Implementation of the utility for the label text creation
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import enum
import math

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

import NemAll_Python_Utility as AllplanUtil

from Utilities.GeneralConstants import GeneralConstants

from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes
from ValueTypes.ValueTypeUtils.ValueType import ValueType

if TYPE_CHECKING:
    from BuildingElement import BuildingElement

class LabelTextFrame(enum.IntEnum):
    """ definition of the label text frame types
    """

    NO               = 0
    UNDERLINE        = 1
    RECTANGLE        = 2
    FILLET_RECTANGLE = 3
    CIRCLE           = 4
    OCTAGON          = 5


class LabelTextDimensionUnit(enum.IntEnum):
    """ definition the label text dimension unit
    """

    MM = 0
    CM = 1
    DM = 2
    M  = 3

    MM2 = 4
    CM2 = 5
    DM2 = 6
    M2  = 7

    MM3 = 8
    CM3 = 9
    DM3 = 10
    M3  = 11

    DEG = 12
    NO  = 13


class LabelTextFormat(enum.IntEnum):
    """ definition the label text format unit
    """

    CHARACTER = 0
    FLOAT     = 1
    INTEGER   = 2


class LabelTextUtil():
    """ Implementation of the utility for the label text creation
    """

    __default_value_type_unit = {ParameterPropertyValueTypes.ANGLE       : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.AREA        : LabelTextDimensionUnit.M2,
                                 ParameterPropertyValueTypes.DOUBLE      : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.INTEGER     : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.LENGTH      : LabelTextDimensionUnit.M,
                                 ParameterPropertyValueTypes.STRING      : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.VOLUME      : LabelTextDimensionUnit.M3,
                                 ParameterPropertyValueTypes.WEIGHT      : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.COLOR       : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.FACESTYLE   : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.FONT        : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.FONTEMPHASIS: LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.HATCH       : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.LAYER       : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.PATTERN     : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.PEN         : LabelTextDimensionUnit.NO,
                                 ParameterPropertyValueTypes.STROKE      : LabelTextDimensionUnit.NO,
                                 }

    __dim_factor = [1, 10, 100, 1000, 1, 100, 10000, 1000000, 1, 1000, 1000000, 1000000000, math.pi / 180, 1]

    def __init__(self):
        """ initialize
        """

        self.__label_text_frame    = LabelTextFrame.NO
        self.__pre_text            = ""
        self.__dimension_unit      = LabelTextDimensionUnit.MM
        self.__dimension_unit_text = ""
        self.__text_format         = LabelTextFormat.CHARACTER
        self.__digits              = 30
        self.__decimals            = 0
        self.__parameter_value     = []
        self.__attributes          = []


    def set_text_frame(self,
                       text_frame: LabelTextFrame):
        """ set the text frame of the label

        Args:
            text_frame: text frame
        """

        self.__label_text_frame = text_frame


    def set_pre_text(self,
                     pre_text: str):
        """ set the pre text

        Args:
            pre_text: prefix text
        """

        self.__pre_text = pre_text


    def set_dimension_unit(self,
                           dimension_unit: LabelTextDimensionUnit):
        """ set the dimension

        Args:
            dimension_unit: dimension unit
        """

        self.__dimension_unit = dimension_unit

        self.__dimension_unit_text = ["mm", "cm", "dm", "m", "mm²", "cm²", "dm²", "m²", "mm³", "cm³", "dm³", "m³", "", ""][dimension_unit]


    def set_dimension_unit_by_value_type(self,
                                         value_type: ValueType):
        """ set the dimension unit by the value type

        Args:
            value_type: Value type
        """

        self.set_dimension_unit(LabelTextUtil.__default_value_type_unit[value_type])


    def set_format(self,
                   text_format: LabelTextFormat,
                   digits     : int,
                   decimals   : int = 0):
        """ set the format of the label text

        Args:
            text_format: text format
            digits:      digits
            decimals:    decimals
        """

        self.__text_format = text_format
        self.__digits      = digits
        self.__decimals    = decimals


    def set_format_by_value_type(self,
                                 value_type: ValueType):
        """ set the format by the value type

        Args:
            value_type: Value type
        """

        match value_type:
            case ParameterPropertyValueTypes.INTEGER:
                self.set_format(LabelTextFormat.INTEGER, 8)

            case ParameterPropertyValueTypes.STRING:
                self.set_format(LabelTextFormat.CHARACTER, 100)

            case _:
                self.set_format(LabelTextFormat.FLOAT, 8, 3)


    def add_parameter(self,
                      build_ele      : (BuildingElement | list[BuildingElement]),
                      parameter_name : str,
                      parameter_value: (Any | None) = None):
        """ add a parameter to the label text

        Args:
            build_ele:       building element with the parameter properties
            parameter_name:  parameter name
            parameter_value: parameter value, use from parameter_name if None
        """

        index = 0
        prop  = None

        name = parameter_name.split(GeneralConstants.SUB_NAME_SEPARATOR, 1)[0]

        if isinstance(build_ele, list):
            for index, ele in enumerate(build_ele):
                if (prop := ele.get_property(name)) is not None:
                    break
        else:
            prop = build_ele.get_property(name)

        if prop is None:
            AllplanUtil.ShowMessageBox(f"Parameter {parameter_name}does not exist!!!",  AllplanUtil.MB_OK)
            return

        self.__parameter_value.append((index, parameter_value if parameter_value is not None else prop.value, parameter_name))


    def add_parameter_name(self,
                           parameter_name: str,
                           value         : Any):
        """ add a parameter name and value to the label text

        Args:
            parameter_name: parameter name
            value:          value
        """

        self.__parameter_value.append((0, value, parameter_name))


    def add_attribute(self,
                      doc         : AllplanEleAdapter.DocumentAdapter,
                      attribute_id: int,
                      value       : Any = ""):
        """ add an attribute to the label text

        Args:
            doc:          document of the Allplan drawing files
            attribute_id: attribute ID
            value:        value
        """

        if not attribute_id:
            return

        self.__attributes.append((attribute_id, value))

        value_type = AllplanBaseEle.AttributeService.GetAttributeType(doc, attribute_id)

        match value_type:
            case AllplanBaseEle.AttributeService.AttributeType.Integer:
                self.__text_format = LabelTextFormat.INTEGER
                self.__digits      = 20

            case AllplanBaseEle.AttributeService.AttributeType.Double:
                self.__text_format = LabelTextFormat.FLOAT                  # pylint: disable=redefined-variable-type
                self.__digits      = 10
                self.__decimals    = 2

            case _:
                self.__text_format = LabelTextFormat.CHARACTER

        self.__dimension_unit_text = AllplanBaseEle.AttributeService.GetAttributeUnit(doc, attribute_id)


    def create_label_text(self) -> str:
        """ create the label text

        Returns:
            label text
        """

        layout_key = 0
        layout_key += (self.__label_text_frame & 7) << 2
        layout_key |= 32 if self.__pre_text else 0

        match self.__text_format:
            case LabelTextFormat.CHARACTER:
                text_format = f"A{self.__digits}"

            case LabelTextFormat.INTEGER:
                text_format = f"I{self.__digits}"

            case _:
                text_format = f"F{self.__digits}.{self.__decimals}"

        fmt = "CRI"[self.__text_format]

        text = f"|T|{fmt}|0|0|{layout_key}|{self.__dimension_unit % 4}|{text_format}| {self.__dimension_unit_text}||{self.__pre_text}|"

        div_str = f"/{LabelTextUtil.__dim_factor[self.__dimension_unit]}" \
                  if LabelTextUtil.__dim_factor[self.__dimension_unit] != 1 else ""

        part_index = 0

        for index, _, name in self.__parameter_value:
            if part_index:
                text += "+"

            part_index += 1

            text += f"@611[\"{index}:{name};{fmt}\"]@{div_str}"

        for attribute, _ in self.__attributes:
            if part_index:
                text += "+"

            part_index += 1

            text += f"@{attribute}@"

        return f"{text}|"


    def create_label_default_text(self) -> str:
        """ create the text

        Returns:
            default label text
        """

        match self.__text_format:
            case LabelTextFormat.INTEGER:
                text_format = f"{{:{self.__digits}d}}"

            case LabelTextFormat.FLOAT:
                text_format = f"{{:{self.__digits}.{self.__decimals}f}}"

            case _:
                text_format = ""

        text = ""


        #----------------- add the values

        for _, value, _ in self.__parameter_value:
            text += self.__format_value(value, text_format)


        #----------------- add the attributes

        for _, value in self.__attributes:
            text += self.__format_value(value, text_format)

        return f"{text}|"


    def __format_value(self,
                       value      : Any,
                       text_format: str) -> str:
        """ convert the value to a formatted string

        Args:
            value:       value
            text_format: format

        Returns:
            value as string
        """

        dim_fac = 1 if self.__dimension_unit == LabelTextDimensionUnit.DEG else LabelTextUtil.__dim_factor[self.__dimension_unit]

        match self.__text_format:
            case LabelTextFormat.CHARACTER:
                return value

            case LabelTextFormat.INTEGER:
                return text_format.format(value).lstrip(" ")

            case _:
                res = text_format.format(value / dim_fac).lstrip(" ")

                return res
