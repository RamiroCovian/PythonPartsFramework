""" Implementation of the PythonPart utilities """

import os
from typing import Any
import uuid

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Utility as AllplanUtil
from BuildingElement import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from BuildingElementListService import BuildingElementListService
from PythonPart import PythonPart, View, View2D, View2D3D, View3D
from PythonPartViewData import PythonPartViewData


class PythonPartUtil():
    """ Implementation of the PythonPart utilities """

    def __init__(self,
                 common_props: (AllplanBaseEle.CommonProperties | None) = None):
        """ Initialize

        Args:
            common_props: common properties
        """

        self. common_props = common_props

        self.__views            = []
        self.__arch_ele_list    = []
        self.__reinf_ele_list   = []
        self.__fixture_ele_list = []
        self.__library_ele_list = []
        self.__assembly_elements = []
        self.__mwsgroup_elements = []
        self.__label_ele_list   = []
        self.__attribute_list   = BuildingElementAttributeList()
        self.__structured_container_attribute_list = {}


    def add_pythonpart_view_2d3d(self,
                                 elements  : (AllplanBasisEle.ModelElement2D |
                                              AllplanBasisEle.ModelElement3D |
                                              Any),
                                 view_data : PythonPartViewData = PythonPartViewData()):
        """Add the elements to a 2D3D view for the next PythonPart. Elements added to this view
        will be visible in both ground and isometric view.

        Args:
            elements:   elements
            view_data:  view data
        """


        view = View2D3D(elements, view_data.start_scale, view_data.end_scale) if isinstance(elements, list) else \
               View2D3D([elements], view_data.start_scale, view_data.end_scale)

        self.set_view_data(view, view_data)

        if not view.elements:
            AllplanUtil.ShowMessageBox("Error: PythonPart-view has no model elements !!!", AllplanUtil.MB_OK)

            return

        self.__views.append(view)


    def add_pythonpart_view_3d(self,
                               elements: (AllplanBasisEle.ModelElement2D |
                                          AllplanBasisEle.ModelElement3D |
                                          Any),
                               view_data : PythonPartViewData = PythonPartViewData()):
        """Add the elements to a 3D view for the next PythonPart. Elements added to this view
        will be visible only in an isometric view.

        Args:
            elements:   elements
            view_data:  view data
        """

        view = View3D(elements, view_data.start_scale, view_data.end_scale) if isinstance(elements, list) else \
               View3D([elements], view_data.start_scale, view_data.end_scale)

        self.set_view_data(view, view_data)

        self.__views.append(view)


    def add_pythonpart_view_2d(self,
                               elements: (AllplanBasisEle.ModelElement2D |
                                          AllplanBasisEle.ModelElement3D |
                                          Any),
                               view_data : PythonPartViewData = PythonPartViewData()):
        """Add the elements to a 2D view for the next PythonPart. Elements added to this view
        will be visible only in a ground view.

        Args:
            elements:   elements
            view_data:  view data
        """

        view = View2D(elements, view_data.start_scale, view_data.end_scale) if isinstance(elements, list) else \
               View2D([elements], view_data.start_scale, view_data.end_scale)

        self.set_view_data(view, view_data)

        self.__views.append(view)


    def add_view(self,
                 elements: (View | list[View])):
        """Add a view for the next PythonPart.

        Args:
            elements: elements
        """

        if isinstance(elements, list):
            self.__views.extend(elements)
        else:
            self.__views.append(elements)


    @staticmethod
    def set_view_data(view: View,
                      view_data : PythonPartViewData):
        """ set the view data

        Args:
            view:      view
            view_data: view data
        """

        view.visibility_layer_a = view_data.visibility_layer_a
        view.visibility_layer_b = view_data.visibility_layer_b
        view.visibility_layer_c = view_data.visibility_layer_c


    def add_architecture_elements(self, elements: Any):
        """Add the architecture elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: architecture elements
        """

        if isinstance(elements, list):
            self.__arch_ele_list += elements
        else:
            self.__arch_ele_list.append(elements)


    def add_reinforcement_elements(self, elements: Any):
        """Add the reinforcement elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: reinforcement elements
        """

        if isinstance(elements, list):
            self.__reinf_ele_list += elements
        else:
            self.__reinf_ele_list.append(elements)


    def add_fixture_elements(self, elements: Any):
        """Add the fixture elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: fixture elements
        """

        if isinstance(elements, list):
            self.__fixture_ele_list += elements
        else:
            self.__fixture_ele_list.append(elements)


    def add_library_elements(self, elements: Any):
        """Add the library elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: library elements
        """

        if isinstance(elements, list):
            self.__library_ele_list += elements
        else:
            self.__library_ele_list.append(elements)

    def add_assemblygroup_elements(self, elements: Any):
        """Add the library elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: library elements
        """

        if isinstance(elements, list):
            self.__assembly_elements += elements
        else:
            self.__assembly_elements.append(elements)

    def add_mwsgroup_elements(self, elements: Any):
        """Add the library elements to the PythonPart. The elements will be appended as CHILD-elements.

        Args:
            elements: library elements
        """

        if isinstance(elements, list):
            self.__mwsgroup_elements += elements
        else:
            self.__mwsgroup_elements.append(elements)

    def add_label_elements(self, elements: Any):
        """Add the label elements to the PythonPart.

        Args:
            elements: label elements
        """

        if isinstance(elements, list):
            self.__label_ele_list += elements
        else:
            self.__label_ele_list.append(elements)


    def add_attribute_list(self, attribute_list: BuildingElementAttributeList):
        """Add the attribute list to the PythonPart

        Args:
            attribute_list: attribute list
        """

        self.__attribute_list += attribute_list

    def add_attribute_list_to_sub_element_in_structured_container(self,                                             # pylint: disable=invalid-name
                                                                  attribute_list: BuildingElementAttributeList,
                                                                  object_id     : uuid.UUID = uuid.UUID(int = 0)):
        """ Add attribute list to sub element of StructuredContainer to the PythonPart

        Args:
            attribute_list: attribute list
            object_id:      logical object id
        """

        self.__structured_container_attribute_list[object_id] = attribute_list

    def get_pythonpart(self,
                       build_ele             : (BuildingElement | list[BuildingElement]),
                       local_placement_matrix: AllplanGeo.Matrix3D = AllplanGeo.Matrix3D(),
                       placement_matrix      : AllplanGeo.Matrix3D = AllplanGeo.Matrix3D(),
                       type_uuid             : str                 = "",
                       type_display_name     : str                 = "") -> PythonPart:
        """ get the PythonPart

        Args:
            build_ele:              building element with the parameter properties
            local_placement_matrix: local placement matrix of the PythonPart, used for the local geometry transformation
            placement_matrix:       placement matrix of the PythonPart (model placement)
            type_uuid:              define the selectable type
            type_display_name:      display name for the tooltip and object palette

        Returns:
            created PythonPart
        """

        if isinstance(build_ele, list):
            parameter_list = BuildingElementListService.get_params_list(build_ele)
            parameter_hash = BuildingElementListService.get_hash(build_ele)

            for ele in build_ele:
                self.__attribute_list.add_attributes_from_parameters(ele)

            build_ele = build_ele[0]
        else:
            self.__attribute_list.add_attributes_from_parameters(build_ele)

            parameter_list = build_ele.get_params_list()
            parameter_hash = build_ele.get_hash()

        return PythonPart(os.path.basename(build_ele.pyp_file_name).split(".")[0],
                          parameter_list        = parameter_list,
                          hash_value            = parameter_hash,
                          python_file           = build_ele.pyp_file_name,
                          views                 = self.__views,
                          matrix                = local_placement_matrix,
                          common_props          = self.common_props,
                          attribute_list        = self.__attribute_list.get_attribute_list(),
                          architecture_elements = self.__arch_ele_list,
                          reinforcement         = self.__reinf_ele_list,
                          fixture_elements      = self.__fixture_ele_list,
                          library_elements      = self.__library_ele_list,
                          label_elements        = self.__label_ele_list,
                          assembly_elements     = self.__assembly_elements,
                          mws_elements          = self.__mwsgroup_elements,
                          placement_matrix      = placement_matrix,
                          type_uuid             = type_uuid,
                          type_display_name     = type_display_name,
                          structured_container_attributes = self.__structured_container_attribute_list)


    def create_pythonpart(self,
                          build_ele             : (BuildingElement | list[BuildingElement]),
                          local_placement_matrix: AllplanGeo.Matrix3D = AllplanGeo.Matrix3D(),
                          placement_matrix      : AllplanGeo.Matrix3D = AllplanGeo.Matrix3D(),
                          type_uuid             : str                 = "",
                          type_display_name     : str                 = "") -> list[Any]:
        """ create a PythonPart with the current views

        Args:
            build_ele:              building element with the parameter properties
            local_placement_matrix: local placement matrix of the PythonPart, used for the local geometry transformation
            placement_matrix:       placement matrix of the PythonPart (model placement)
            type_uuid:              define the selectable type
            type_display_name:      display name for the tooltip and object palette

        Returns:
            list with the created PythonPart elements
        """

        pythonpart = self.get_pythonpart(build_ele, local_placement_matrix, placement_matrix, type_uuid, type_display_name)

        self.__views            = []
        self.__arch_ele_list    = []
        self.__reinf_ele_list   = []
        self.__fixture_ele_list = []
        self.__library_ele_list = []
        self.__assembly_elements = []
        self.__mwsgroup_elements = []
        self.__label_ele_list   = []

        return pythonpart.create()
