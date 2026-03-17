""" implementation of the utilities for the element properties attributes
"""

from typing import List

import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from AttributeIdValue import AttributeIdValue

class ElementPropertiesAttributeUtil():
    """ implementation of the utilities for the element properties attributes
    """

    @staticmethod
    def set_attributes(doc       : AllplanEleAdapter.DocumentAdapter,
                       ele_prop  : AllplanArchEle.RoomProperties,
                       attributes: List[AttributeIdValue]):
        """ set the attributes to the properties

        Args:
            doc:        document of the Allplan drawing files
            ele_prop:   element properties
            attributes: attributes
        """

        attribute_type = AllplanBaseEle.AttributeService

        for attr_id_value in attributes:
            value_type = AllplanBaseEle.AttributeService.GetAttributeType(doc, attr_id_value.attribute_id)

            if value_type == attribute_type.Integer:
                ele_prop.SetAttribute(AllplanBaseEle.AttributeInteger(attr_id_value.attribute_id, attr_id_value.value))

            elif value_type == attribute_type.Double:
                ele_prop.SetAttribute(AllplanBaseEle.AttributeDouble(attr_id_value.attribute_id, attr_id_value.value))

            elif value_type == attribute_type.String:
                ele_prop.SetAttribute(AllplanBaseEle.AttributeString(attr_id_value.attribute_id, attr_id_value.value))

            elif value_type == attribute_type.Enum:
                enum_list = AllplanBaseEle.AttributeService.GetEnumValues(doc, attr_id_value.attribute_id)

                ele_prop.SetAttribute(AllplanBaseEle.AttributeEnum(attr_id_value.attribute_id, enum_list.index(attr_id_value.value)))
