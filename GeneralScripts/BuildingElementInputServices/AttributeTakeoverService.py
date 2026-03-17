""" Implementation of the attribute takeover service
"""

from typing import Any, cast

from datetime import date

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from DocumentManager import DocumentManager
from ParameterProperty import ParameterProperty

from Utilities.AttributeIdEnums import AttributeIdEnums

from ValueTypes.DateImpl import BaseStringToValueConverter
from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes

EXTERNAL_ATTRIBUTES : dict[str, Any] = {}

class AttributeTakeoverService():
    """ Implementation of the attribute takeover service """

    @staticmethod
    def check_external_attribute_modification(build_ele_list: list[BuildingElement]):
        """ check for an external attribute modification and adapt the values

        Args:
            build_ele_list: building element list
        """

        pyp_ele = DocumentManager.get_instance().pythonpart_element

        attr_dict = {}

        attr_varied : set[int] = set()


        #----------------- get the attributes from the sub PythonParts

        if AllplanBaseEle.PythonPartService.IsPythonPartGroupElement(pyp_ele):
            AttributeTakeoverService.__get_attributes_from_sub_elements(build_ele_list, pyp_ele, attr_dict, attr_varied)


        #----------------- get the attributes from the PythonPart

        else:
            attr_dict = dict(iter(AllplanBaseEle.ElementsAttributeService.GetAttributes(pyp_ele)))


        #----------------- get the PyP attribute values from the element attributes

        AttributeTakeoverService.__get_param_values_from_attributes(build_ele_list, attr_dict, attr_varied)

        if not AllplanBaseEle.PythonPartService.IsPythonPartGroupElement(pyp_ele):
            EXTERNAL_ATTRIBUTES[str(pyp_ele.GetModelElementUUID())] = attr_dict


    @staticmethod
    def add_takeover_attributes(attributes: list[AllplanBaseEle.Attribute]):
        """ add the takeover attributes

        Args:
            attributes: attributes
        """

        pyp_ele = DocumentManager.get_instance().pythonpart_element

        if (external_attr_dict := EXTERNAL_ATTRIBUTES.get(str(pyp_ele.GetModelElementUUID()))) is None:
            return


        #----------------- add the missing external attributes

        build_ele_attr = BuildingElementAttributeList()

        exclude_geo = {AttributeIdEnums.RADIUS, AttributeIdEnums.X_COORDINATE, AttributeIdEnums.Y_COORDINATE,
                       AttributeIdEnums.LENGTH, AttributeIdEnums.THICKNESS, AttributeIdEnums.HEIGHT, AttributeIdEnums.VOLUME,
                       AttributeIdEnums.BASE_AREA, AttributeIdEnums.WIDTH}

        for key, value in external_attr_dict.items():
            if key not in exclude_geo and next((True for attribute in attributes if key == attribute.Id), False) is False:
                build_ele_attr.add_attribute(key, value)

        attributes += build_ele_attr.get_attribute_list()


    @staticmethod
    def __get_attributes_from_sub_elements(build_ele_list: list[BuildingElement],
                                           pyp_ele       : AllplanEleAdapter.BaseElementAdapter,
                                           attr_dict     : dict[int, Any],
                                           attr_varied   : set[int]):
        """ get the attributes from the sub PythonParts of the group

        Args:
            build_ele_list: list with the building elements
            pyp_ele:        group element
            attr_dict:      attribute dict
            attr_varied:    varied attribute IDs
        """

        undefined = build_ele_list[0].get_string_tables()[1].get_string("e_UNDEFINED", "Undefined")

        for child_ele in AllplanEleAdapter.BaseElementAdapterChildElementsService.GetChildElements(pyp_ele, True):
            if not AllplanBaseEle.PythonPartService.IsPythonPartElement(child_ele):
                continue

            for attr_id, attr_value in AllplanBaseEle.ElementsAttributeService.GetAttributes(child_ele):
                if not isinstance(attr_value, str) or attr_value != undefined:
                    if attr_id in attr_dict and attr_value != attr_dict[attr_id]:
                        attr_varied.add(attr_id)

                    attr_dict[attr_id] = attr_value


    @staticmethod
    def __get_param_values_from_attributes(build_ele_list: list[BuildingElement],
                                           attr_dict     : dict[int, Any],
                                           attr_varied   : set[int]):
        """ get the parameter values from the attributes

        Args:
            build_ele_list: list with the building elements
            attr_dict:      attribute dict
            attr_varied:    varied attribute IDs
        """

        for build_ele in build_ele_list:
            for prop in build_ele.get_properties():
                if prop.value_type == ParameterPropertyValueTypes.ATTRIBUTE_ID_VALUE:
                    AttributeTakeoverService.__check_attribute_id_value(prop, attr_dict, attr_varied)

                elif isinstance(prop.attribute_id, list):
                    AttributeTakeoverService.__check_attribute_list(prop, attr_dict, attr_varied)

                elif prop.attribute_id:
                    if (value := attr_dict.get(prop.attribute_id)):
                        if not AttributeTakeoverService.__check_varied_attribute(prop.attribute_id, attr_varied):
                            prop.value = AttributeTakeoverService.__convert_attribute_value(prop.value, value, prop.attribute_id)

                        del attr_dict[prop.attribute_id]


    @staticmethod
    def __check_attribute_list(prop       : ParameterProperty,
                               attr_dict  : dict[int, Any],
                               attr_varied: set[int]):
        """ check for attribute list

        Args:
            prop:        property
            attr_dict:   attribute dict
            attr_varied: varied attribute IDs
        """

        for index, attribute_id in enumerate(cast(list, prop.attribute_id)):
            if (value := attr_dict.get(attribute_id)):
                if not AttributeTakeoverService.__check_varied_attribute(attribute_id, attr_varied):
                    prop.value[index] = AttributeTakeoverService.__convert_attribute_value(prop.value[index], value, attribute_id)

                del attr_dict[attribute_id]


    @staticmethod
    def __check_attribute_id_value(prop       : ParameterProperty,
                                   attr_dict  : dict[int, Any],
                                   attr_varied: set[int]):
        """ check for attribute id and value

        Args:
            prop:        property
            attr_dict:   attribute dict
            attr_varied: varied attribute IDs
        """

        if isinstance(prop.value, list):
            for value in prop.value:
                if (attr_value := attr_dict.get(value.attribute_id, None)) is not None:
                    if not AttributeTakeoverService.__check_varied_attribute(value.attribute_id, attr_varied):
                        value.value = AttributeTakeoverService.__convert_attribute_value(value.value, attr_value, value.attribute_id)

                    del attr_dict[value.attribute_id]

                elif value.attribute_id:
                    name = AllplanBaseEle.AttributeService.GetAttributeName(DocumentManager.get_instance().document,
                                                                            value.attribute_id)

                    AllplanUtil.ShowMessageBox(f"Not possible to update value for Attribute {name}",  AllplanUtil.MB_OK)

        elif prop.value.attribute_id:
            if not AttributeTakeoverService.__check_varied_attribute(prop.value.attribute_id, attr_varied):
                prop.value.value = AttributeTakeoverService.__convert_attribute_value(prop.value.value,
                                                                                      attr_dict.get(prop.value.attribute_id),
                                                                                      prop.value.attribute_id)

            del attr_dict[prop.value.attribute_id]


    @staticmethod
    def __convert_attribute_value(value       : Any,
                                  new_value   : Any,
                                  attribute_id: int) -> Any:
        """ convert the new attribute value

        Args:
            value:        value
            new_value:    new value
            attribute_id: attribute ID

        Returns:
            new parameter value
        """

        if isinstance(value, date):
            if (date_value := BaseStringToValueConverter.string_to_date(new_value, True)) is None:
                return value

            return date_value


        #----------------- convert to mm

        match AllplanBaseEle.AttributeService.GetAttributeUnit(DocumentManager.get_instance().document, attribute_id):
            case "m":
                return new_value * 1000

            case "m²":
                return new_value * 1000000

            case "m³":
                return new_value * 1000000000

            case "cm":
                return new_value * 10

            case "cm²":
                return new_value * 100

            case "cm³":
                return new_value * 1000

        return new_value


    @staticmethod
    def __check_varied_attribute(attribute_id: int,
                                 attr_varied : set[int]) -> bool:
        """ check for varied attribute

        Args:
            attribute_id: attribute ID
            attr_varied:  varied attribute IDs

        Returns:
            varied attribute state
        """

        if attribute_id not in attr_varied:
            return False

        # doc = DocumentManager.get_instance().document

        # AllplanUtil.ShowMessageBox(f"Different values vor attribute " \
        #                             f"{AllplanBaseEle.AttributeService.GetAttributeName(doc, attribute_id)}",
        #                             AllplanUtil.MB_OK)

        return True
