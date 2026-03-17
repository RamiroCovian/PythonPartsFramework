""" Implementation of the model element string utils
"""

from typing import Any, cast

import functools
import subprocess

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Precast as AllplanPrecast

class CreateTestStringsUtil():
    """ Implementation of the model element string utils
    """

    @staticmethod
    def get_model_elements_data(model_ele_list: list[Any]) -> tuple[list[Any], list[Any], list[Any]]:
        """ get the exploded model elements and the parameter list

        Explodes the PythonPart/PythonPartGroup and gets the model objects from the slides

        Args:
            model_ele_list: list with the created model elements

        Returns:
            list with the model elements contained in the PythonPart, parameters of the PythonPart
        """

        model_elements : list[Any] = []
        parameter_lists: list[Any] = []
        attribute_lists: list[Any] = []


        #----------------- get the elements from a PythonPart group

        if next((True for model_ele in model_ele_list if isinstance(model_ele, AllplanBasisEle.MacroGroupElement)), False):
            for model_ele in model_ele_list:
                if isinstance(model_ele, AllplanBasisEle.MacroGroupElement):
                    for placement in model_ele.GetPlacementList():
                        CreateTestStringsUtil.__get_parameter_list(placement, parameter_lists)

                        slides = placement.GetMacro().GetSlideList()

                        model_elements += slides[1].GetObjectList()
                        model_elements += placement.GetFixtureElementsList()
                        model_elements += placement.GetArchitectureElementsList()

            return model_elements, parameter_lists, attribute_lists


        #----------------- get the elements from the PythonPart

        element = model_ele_list[0]

        if isinstance(element, AllplanBasisEle.MacroPlacementElement):
            element   = element.GetMacro()
            placement = model_ele_list[0]
        else:
            placement = None

        if isinstance(element, AllplanBasisEle.MacroElement):
            slides = element.GetSlideList()

            for index in range(1, len(slides)):
                model_elements += slides[index].GetObjectList()

            if placement is None:
                placement = model_ele_list[1]

            placement = cast(AllplanBasisEle.MacroPlacementElement, placement)

            model_elements += placement.GetFixtureElementsList()
            model_elements += placement.GetReinforcementList()
            model_elements += placement.GetArchitectureElementsList()
            model_elements += placement.GetLabelElements()

            param_list = None

            for attr_list in placement.GetAttributesList():
                param_list = next((attrib for attrib in attr_list.GetAttributes() \
                    if isinstance(attrib, AllplanBaseEle.AttributeStringVec)), None)

                for item in attr_list.Attributes:
                    if item.Id not in (539, 611, 1034):
                        attribute_lists.append(item)

            if param_list is not None:
                parameter_lists.append(CreateTestStringsUtil.__get_parameter_list_str(param_list.Value[1:]))
        else:
            model_elements += model_ele_list

        return model_elements, parameter_lists, attribute_lists


    @staticmethod
    def __get_parameter_list(placement      : AllplanBasisEle.MacroPlacementElement,
                             parameter_lists: list[str]):
        """ get the parameter list

        Args:
            placement:       macro placement
            parameter_lists: parameter list
        """

        for attribute in placement.GetAttributesList()[0].GetAttributes():
            if not isinstance(attribute, AllplanBaseEle.AttributeStringVec):
                continue

            param_list = attribute.Value

            istart = 1 if len(param_list) == 1 or not str(param_list[1]).startswith("ParameterHash=") else 2

            parameter_lists.append(CreateTestStringsUtil.__get_parameter_list_str(param_list[istart:]))

            return


    @staticmethod
    def __get_parameter_list_str(param_list: list[str]) -> str:
        """ get the parameter list string

        Args:
            param_list: parameter list

        Returns:
            parameter list string
        """

        return str(param_list)[2: -4].replace("\\n', '", "\n").replace("', '", "\n").replace("\\\\", "\\") + "\n"


    @staticmethod
    def get_geometry_elements_text(model_elements: list[Any]) -> str:
        """ get the element text from the geometry elements

        Args:
            model_elements: model elements

        Returns:
            string of the geometry from the model elements
        """

        geo_ele_text = ""

        for model_ele in model_elements:
            if isinstance(model_ele, AllplanPrecast.FixturePlacementElement):
                geo_ele_text += str(model_ele) + "\n"

                for slide in model_ele.GetMacro().GetSlideList():
                    geo_ele_text += str(slide) + "\n"
                    geo_ele_text += functools.reduce(lambda text, obj: text + str(obj.GetGeometryObject()) + "\n",
                                                    slide.GetObjectList(), "")

            elif (geo_obj := model_ele.GetGeometryObject()):
                geo_ele_text += str(geo_obj) + "\n"
            else:
                geo_ele_text += str(model_ele)

        return geo_ele_text


    @staticmethod
    def copy_element_strings_to_clipboard(model_ele_list: list[Any]):
        """ create a string from the model elements and copy it the to clipboard

        Args:
            model_ele_list: model elements
        """

        model_elements, _, _ = CreateTestStringsUtil.get_model_elements_data(model_ele_list)

        geo_ele_text = CreateTestStringsUtil.get_geometry_elements_text(model_elements)

        text = "        TestUtil.compare_element_strings(get_geometry_elements_text(),\n" + \
               "                                         \"" + \
               geo_ele_text.replace("\n","\\n\"    \\\n                                         \"") + "\")\n\n"

        subprocess.run(['clip.exe'], input = text.encode("UTF-8"), check = True)


    @staticmethod
    def copy_parameter_strings_to_clipboard(model_ele_list: list[Any]):
        """ create a string from the parameters and copy it the to clipboard

        Args:
            model_ele_list: model elements
        """

        _, parameters, _ = CreateTestStringsUtil.get_model_elements_data(model_ele_list)

        param_text = functools.reduce(lambda text, parameter_list:
                                      text + str(parameter_list) + "---------------------------------------------------\n",
                                      parameters, "")

        text = "        TestUtil.compare_element_strings(get_parameter_list_text(),\n" + \
               "                                         \"" + \
               param_text.replace("\n","\\n\"    \\\n                                         \"") + "\")\n\n"

        subprocess.run(['clip.exe'], input = text.encode("UTF-8"), check = True)


    @staticmethod
    def copy_element_and_parameter_strings_to_clipboard(model_ele_list: list[Any]):
        """ create a string from the model elements and parameters and copy it the to clipboard

        Args:
            model_ele_list: model elements
        """

        model_elements, parameters, _ = CreateTestStringsUtil.get_model_elements_data(model_ele_list)

        geo_ele_text = CreateTestStringsUtil.get_geometry_elements_text(model_elements)

        text = "        TestUtil.compare_element_strings(get_geometry_elements_text(),\n" + \
               "                                         \"" + \
               geo_ele_text.replace("\n","\\n\"    \\\n                                         \"") + "\")\n\n"

        param_text = functools.reduce(lambda text, parameter_list:
                                      text + str(parameter_list) + "---------------------------------------------------\n",
                                      parameters, "")

        text += "        TestUtil.compare_element_strings(get_parameter_list_text(),\n" + \
                "                                         \"" + \
                param_text.replace("\n","\\n\"    \\\n                                         \"") + "\")\n\n"

        subprocess.run(['clip.exe'], input = text.encode("UTF-8"), check = True)
