""" implementation of the PythonPart
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import uuid

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_ArchElements as AllplanArch
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Precast as AllplanPrecast
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil

from BuildingElement import BuildingElement
from DocumentManager import DocumentManager

from BuildingElementInputServices.AttributeTakeoverService import AttributeTakeoverService
from BuildingElementAttributeList import BuildingElementAttributeList

class AttrBuilder():
    """ Define specific PythonPart attributes
    """

    @staticmethod
    def pyp_file_param_list_attr(python_file   : str,
                                 parameter_list: list[str]) -> tuple[AllplanBaseEle.AttributeStringVec, list[str]]:
        """ Define attribute holding python file name and all parameter - values pairs of pyp file

        Args:
            python_file   : Filename of PYP file
            parameter_list: list of parameters of PYP file

        Returns:
            Attribute holding values as string vector, geometry parameter values
        """

        values = AllplanUtil.VecStringList()

        geom_param_values : list[str] = []

        values.append(python_file)

        for item in parameter_list:
            if "Polyhedron3D" in item or "BRep3D(" in item or "BSpline3D(" in item:     # pylint: disable=magic-value-comparison
                name, _, geo_param_value = item.partition("=")

                geo_uuid = str(uuid.uuid4())

                values.append(f"{name}=GeometryProxyElement:{geo_uuid}{chr(10)}")

                geom_param_values.append(f"{geo_uuid}={geo_param_value}")

            else:
                values.append(item)

        return AllplanBaseEle.AttributeStringVec(AllplanBaseEle.ATTRNR_PYTHONPART_PATH, values), geom_param_values


    @staticmethod
    def python_part_attr() -> AllplanBaseEle.AttributeString:
        """ Define attribute holding "PythonPart" identification string

        Returns:
            Attribute holding PythonPart identifier
        """

        return AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_PYTHONPART_CHECK, 'PythonPart')


    @staticmethod
    def placement_matrix_attr(matrix: AllplanGeo.Matrix3D) -> AllplanBaseEle.AttributeDoubleVec:
        """ Define attribute holding PythonPart matrix for update

        Args:
            matrix: placement matrix

        Returns:
            Attribute holding PythonPart matrix for update
        """

        values = AllplanUtil.VecDoubleList()

        geo_matrix_size = 16

        for i in range(0, geo_matrix_size):
            values.append(matrix[i])

        return AllplanBaseEle.AttributeDoubleVec(AllplanBaseEle.ATTRNR_PYTHONPART_MATRIX, values)


class View():
    """ Definition of a view class
    """

    def __init__(self,
                 viewtype    : AllplanBasisEle.MacroSlideType = AllplanBasisEle.MacroSlideType.eGeometry,
                 visibility2d: bool                           = True,
                 visibility3d: bool                           = True,
                 start_scale : float                          = 0.,
                 end_scale   : float                          = 9999.,
                 elements    : (list[Any] | None)             = None):
        """ initialization of view class

        Args:
            viewtype:     view type. Defaults to AllplanBasisElements.MacroSlideType.eGeometry.
            visibility2d: visible in 2D. Defaults to True.
            visibility3d: visible in 3D. Defaults to True.
            start_scale:  start scale. Defaults to 0.
            end_scale:    end scale. Defaults to 9999.
            elements:     elements. Defaults to None.
        """
        self._start_scale        = start_scale
        self._end_scale          = end_scale
        self._visibility2d       = visibility2d
        self._visibility3d       = visibility3d
        self._visibility_layer_a = True
        self._visibility_layer_b = True
        self._visibility_layer_c = True
        self._viewtype           = viewtype
        self._elements           = elements if elements is not None else []

    def __repr__(self) ->str:
        """ create the element string

        Returns:
            element string
        """

        return f"View(_start_scale={self._start_scale}, " \
               f"_end_scale={self._end_scale}, " \
               f"_visibility2d={self._visibility2d}, " \
               f"_visibility3d={self._visibility3d}," \
               f"_visibility_layer_a={self._visibility_layer_a}, " \
               f"_visibility_layer_b={self._visibility_layer_b}, " \
               f"_visibility_layer_c={self._visibility_layer_c}, " \
               f"_viewtype={self._viewtype}\n" + \
            str(self._elements)

    @property
    def viewtype(self) -> AllplanBasisEle.MacroSlideType:
        """ Get the type

        Returns:
            macros slide type
        """
        return self._viewtype


    @property
    def visibility2d(self) -> bool:
        """ Get the 2D visibility flag

        Returns:
            2D visibility flag
        """
        return self._visibility2d

    @property
    def visibility3d(self) -> bool:
        """ Get the 3D visibility flag

        Returns:
            3D visibility flag
        """
        return self._visibility3d

    @property
    def visibility_layer_a(self) -> bool:
        """ Get the Layer A visibility flag

        Returns:
            Layer A visibility flag
        """
        return self._visibility_layer_a

    @visibility_layer_a.setter
    def visibility_layer_a(self,
                           value: Any):
        """ Set the Layer A visibility

        Args:
            value: New value for Layer A flag
        """
        self._visibility_layer_a = value

    @property
    def visibility_layer_b(self) -> bool:
        """ Get the Layer B visibility flag

        Returns:
            Layer B visibility flag
        """
        return self._visibility_layer_b

    @visibility_layer_b.setter
    def visibility_layer_b(self,
                           value: Any):
        """ Set the Layer B visibility

        Args:
            value: New value for Layer B flag
        """
        self._visibility_layer_b = value

    @property
    def visibility_layer_c(self) -> bool:
        """ Get the Layer C visibility flag

        Returns:
            Layer C visibility flag
        """
        return self._visibility_layer_c

    @visibility_layer_c.setter
    def visibility_layer_c(self,
                           value: Any):
        """ Set the Layer C visibility

        Args:
            value: New value for Layer C flag
        """
        self._visibility_layer_c = value

    @property
    def start_scale(self) -> float:
        """ Get the reference start scale

        Returns:
            start scale
        """
        return self._start_scale

    @property
    def end_scale(self) -> float:
        """ Get the reference end scale

        Returns:
            end scale
        """
        return self._end_scale

    @property
    def elements(self) -> list[Any]:
        """ Get all elements

        Returns:
            elements
        """
        return self._elements

    def add(self, element: Any):
        """ add one element

        Args:
            element: element
        """
        self._elements.append(element)

    def reset(self, elements: list[Any]):
        """ Reset elements

        Args:
            elements: elements
        """
        self._elements = elements

    def create(self) -> AllplanBasisEle.MacroSlideElement:
        """ Create view

        Returns:
            macro slide element
        """

        slide_props                  = AllplanBasisEle.MacroSlideProperties()
        slide_props.VisibilityGeo2D  = self.visibility2d
        slide_props.VisibilityGeo3D  = self.visibility3d
        slide_props.VisibilityLayerA = self.visibility_layer_a
        slide_props.VisibilityLayerB = self.visibility_layer_b
        slide_props.VisibilityLayerC = self.visibility_layer_c
        slide_props.Type             = self.viewtype
        slide_props.StartScaleRange  = self.start_scale
        slide_props.EndScaleRange    = self.end_scale

        return AllplanBasisEle.MacroSlideElement(slide_props, self._elements)

class View2D(View):
    """ Definition of a 2D view class
    """

    def __init__(self,
                 elements   : (list[Any] | None) = None,
                 start_scale: float              = 0.,
                 end_scale  : float              = 9999.):
        """ Initialization of 2D view class

        Args:
            elements:    elements. Defaults to None.
            start_scale: start scale. Defaults to 0.
            end_scale:   end scale. Defaults to 9999.
        """

        super().__init__(AllplanBasisEle.MacroSlideType.eGeometry,
                         True, False, start_scale, end_scale, elements)

class View3D(View):
    """ Definition of a 3D view class
    """

    def __init__(self,
                 elements   : (list[Any] | None) = None,
                 start_scale: float              = 0.,
                 end_scale  : float              = 9999.):
        """ Initialization of 3D view class

        Args:
            elements:    elements. Defaults to None.
            start_scale: start scale. Defaults to 0.
            end_scale:   end scale. Defaults to 9999.
        """

        super().__init__(AllplanBasisEle.MacroSlideType.eGeometry,
                         False, True, start_scale, end_scale, elements)

class View2D3D(View):
    """ Definition of a 2D/3D view class
    """

    def __init__(self,
                 elements   : (list[Any] | None) = None,
                 start_scale: float              = 0.,
                 end_scale  : float              = 9999.):
        """ Initialization of 3D view class

        Args:
            elements:    elements. Defaults to None.
            start_scale: start scale. Defaults to 0.
            end_scale:   end scale. Defaults to 9999.
        """

        super().__init__(AllplanBasisEle.MacroSlideType.eGeometry,
                         True, True, start_scale, end_scale, elements)

class ViewCode(View):
    """ Definition of a code view class
    """

    def __init__(self, hash_value: str):
        """ Initialization of code view class

        Args:
            hash_value: hash value
        """

        self._hash_value = hash_value

        super().__init__(AllplanBasisEle.MacroSlideType.eCode,
                         False, False, 0, 9999, [])

    def create(self) -> AllplanBasisEle.MacroSlideElement:
        """ Create code view

        Returns:
            macro slide element
        """

        slide_props                 = AllplanBasisEle.MacroSlideProperties()
        slide_props.VisibilityGeo2D = super().visibility2d
        slide_props.VisibilityGeo3D = super().visibility3d
        slide_props.Type            = super().viewtype
        slide_props.StartScaleRange = super().start_scale
        slide_props.EndScaleRange   = super().end_scale

        attr_list     = [AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_HASH, self._hash_value)]
        attr_set_list = [AllplanBaseEle.AttributeSet(attr_list)]
        attributes    = AllplanBaseEle.Attributes(attr_set_list)
        objects       = [AllplanBasisEle.AttributeContainer(attributes)]

        return AllplanBasisEle.MacroSlideElement(slide_props, objects)


class PythonPart():
    """ Definition of class PythonPart
    """

    def __init__(self,
                 name                 : str,
                 parameter_list       : list[str],
                 hash_value           : str,
                 python_file          : str,
                 views                : (list[(View2D | View3D | View2D3D)] | None) = None,
                 matrix               : AllplanGeo.Matrix3D                         = AllplanGeo.Matrix3D(),
                 common_props         : (AllplanBaseEle.CommonProperties | None)    = None,
                 reinforcement        : (list[Any] | None)                          = None,
                 attribute_list       : (list[Any] | None)                          = None,
                 library_elements     : (list[Any] | None)                          = None,
                 architecture_elements: (list[Any] | None)                          = None,
                 label_elements       : (list[Any] | None)                          = None,
                 fixture_elements     : (list[Any] | None)                          = None,
                 assembly_elements    : (list[Any] | None)                          = None,
                 mws_elements         : (list[Any] | None)                          = None,
                 placement_matrix     : (AllplanGeo.Matrix3D | None)                = None,
                 type_uuid            : str                                         = "",
                 type_display_name    : str                                         = "",
                 structured_container_attributes : (dict[uuid.UUID, BuildingElementAttributeList]) = {}):
        """ Initialization of class PythonPart

        Args:
            name:                  name of the modified property
            parameter_list:        list with the parameter
            hash_value:            Hash value of the parameter
            python_file:           File name of the pyp file
            views:                 Views for PythonPart
            matrix:                Local matrix of PythonPart, used for the local geometry transformation
            common_props:          Common properties of PythonPart
            reinforcement:         Reinforcement elements for PythonPart
            attribute_list:        Attribute list
            library_elements:      Library elements for PythonPart
            architecture_elements: Architecture elements for PythonPart
            label_elements:        Label elements
            fixture_elements:      Fixture elements for PythonPart
            assembly_elements:     assembly element
            mws_elements:          mvs elements
            placement_matrix:      Placement matrix of the PythonPart
            type_uuid:             define the selectable type defines the selectable type
            type_display_name:     display name for the tooltip and object palette
            structured_container_attributes: attributes for StructuredContainer
        """

        self._name              = name
        self._parameter_list    = parameter_list
        self._hash_value        = hash_value
        self._python_file       = python_file
        self._catalog_name      = "STD\\Library" # set to some useful value
        self._sub_type          = AllplanBasisEle.PYTHON_PART_SUB_TYPE       # 1780
        self._domain_type       = AllplanBasisEle.PYTHON_PART_DOMAIN_TYPE # 21400
        self._matrix            = matrix
        self._distortion_state  = False #block distortion for standard PythonParts
        self._label_elements    = label_elements
        self._placement_matrix  = placement_matrix
        self._leading_macro     = False
        self._type_uuid         = type_uuid
        self._type_display_name = type_display_name
        self._structured_container_attributes = structured_container_attributes


        #----------------- use the default or current common properties

        if common_props is None:
            pyp_ele = DocumentManager.get_instance().pythonpart_element

            if pyp_ele.IsNull():
                common_props = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()
            else:
                common_props = pyp_ele.GetCommonProperties()

        self._common_props = common_props

        self._views                 = self.__test_elements(views, View)
        self._reinforcement         = self.__test_elements(reinforcement, AllplanReinf.ReinfElement)
        self._library_elements      = self.__test_elements(library_elements, AllplanBasisEle.LibraryElement)
        self._architecture_elements = self.__test_elements(architecture_elements, (AllplanArch.ArchElement, AllplanBasisEle.BasisElement))
        self._attribute_list        = self.__test_elements(attribute_list, AllplanBaseEle.Attribute)
        self._fixture_elements      = self.__test_elements(fixture_elements,
                                                           (AllplanPrecast.FixturePlacementElement, AllplanPrecast.FixtureGroupElement))
        self._assembly_elements      = self.__test_elements(assembly_elements, AllplanPrecast.AssemblyGroupElement)
        self._mws_elements           = self.__test_elements(mws_elements, AllplanPrecast.PrecastMWSElement)


    def __repr__(self) ->str:
        """ create the element string

        Returns:
            element string
        """

        return f"PythonPart(_name={self._name}, " \
               f"_hash_value={self._hash_value}, " \
               f"_python_file={self._python_file}, " \
               f"_catalog_name={self._catalog_name},"\
               f"_sub_type={self._sub_type}, " \
               f"_domain_type={self._domain_type}\n" \
               f"======================================\n{self.views}\n"

    @property
    def views(self) -> list[View]:
        """ Get the views

        Returns:
            views
        """
        return self._views

    def add(self, view: View):
        """ Add one view

        Args:
            view: view
        """

        self._views.append(view)

    def distortion_state(self, state: bool):
        """ Set distortion state

        Args:
            state: distortion state
        """
        self._distortion_state = state

    def leading_macro(self,
                      macro_leading: bool):
        """ Set leading macro

        Args:
            macro_leading: leading macro state
        """
        self._leading_macro = macro_leading

    def reset(self, views: list[View]):
        """ Reset views

        Args:
            views: views
        """
        self._views = views

    @property
    def matrix(self) -> AllplanGeo.Matrix3D:
        """ Transformation matrix used for local transformation of the PythonPart

        Returns:
            transformation matrix
        """

        return self._matrix

    @matrix.setter
    def matrix(self, matrix: AllplanGeo.Matrix3D):
        self._matrix = matrix

    @property
    def placement_matrix(self) -> (AllplanGeo.Matrix3D | None):
        """ Placement matrix

        Returns:
            placement matrix
        """

        return self._placement_matrix

    @placement_matrix.setter
    def placement_matrix(self, matrix: AllplanGeo.Matrix3D):
        self._placement_matrix = matrix

    def create(self) -> list[AllplanBasisEle.AllplanElement]:
        """ create the PythonPart

        Returns:
            created elements for the PythonPart
        """

        model_element_list = []
        slide_list         = []

        slide_list.append(ViewCode(self._hash_value).create())

        for view in self._views:
            slide_list.append (view.create())

        macro_prop             = AllplanBasisEle.MacroProperties()
        macro_prop.Name        = self._name
        macro_prop.CatalogName = self._catalog_name
        macro_prop.SubType     = self._sub_type
        macro_prop.DomainType  = self._domain_type

        macro = AllplanBasisEle.MacroElement(macro_prop, slide_list)

        for sub_element_id, attribute_list in self._structured_container_attributes.items():
            attrib_set = AllplanBaseEle.AttributeSet(attribute_list.get_attribute_list())
            macro.SetAttributesForSubElementInStrucutredContainer(attrib_set, sub_element_id)

        macro.SetHash(self._hash_value)

        mp_prop = AllplanBasisEle.MacroPlacementProperties()

        mp_prop.Matrix          = self._matrix if self._placement_matrix is None else self._placement_matrix * self._matrix
        mp_prop.SubType         = self._sub_type
        mp_prop.DomainType      = self._domain_type
        mp_prop.DistortionState = self._distortion_state
        mp_prop.LeadingMacro    = self._leading_macro

        macro_placement = AllplanBasisEle.MacroPlacementElement(self._common_props, mp_prop, macro,
                                                                self._reinforcement, self._library_elements,
                                                                self._architecture_elements, self._fixture_elements,
                                                                self._assembly_elements, self._mws_elements)

        # add all public attributes

        attr_list = self._attribute_list

        param_list_attr, geo_param_values = AttrBuilder.pyp_file_param_list_attr(self._python_file, self._parameter_list)

        attr_list.append(param_list_attr)
        attr_list.append(AttrBuilder.python_part_attr())

        if self._type_uuid:
            attr_list.append(AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_PYTHONPART_UUID, self._type_uuid))

        if self._type_display_name:
            attr_list.append(AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_PYTHONPART_DISPLAY_NAME, self._type_display_name))

        attr_list.append(AttrBuilder.placement_matrix_attr(self._matrix))

        AttributeTakeoverService.add_takeover_attributes(attr_list)

        attributes = AllplanBaseEle.Attributes([AllplanBaseEle.AttributeSet(attr_list)])

        macro_placement.SetAttributes(attributes)
        macro_placement.SetGeometryParameterValueList(geo_param_values)

        if self._label_elements:
            macro_placement.SetLabelElements(self._label_elements)

        model_element_list.append(macro)
        model_element_list.append(macro_placement)

        return model_element_list


    @staticmethod
    def __test_elements(elements        : (list[Any] | None),
                        allowed_ele_type: Any) -> list[Any]:
        """ test the elements

        Args:
            elements:         elements to test
            allowed_ele_type: allowed element type

        Returns:
            adapted elements

        Raises:
            TypeError: raised in case of wrong element type
        """

        if elements is None:
            return []

        for ele in elements:
            if not isinstance(ele, allowed_ele_type):
                parts = str(type(allowed_ele_type)).split(".")

                allowed_ele_type_str = parts[1].rstrip("'>").lower() if len(parts) < 1 else str(type(allowed_ele_type()))

                parts = str(type(ele)).split(".")

                ele_type_str = parts[1].rstrip("'>").lower() if len(parts) < 1 else str(type(ele))

                print(f"===== Wrong element for type {allowed_ele_type_str} element =====")
                print(ele)

                raise TypeError (f"PythonPart.__init__: Element{ele_type_str} is not of type {ele_type_str}")

        return elements


class PythonPartGroup():
    """ Definition of a PythonPart group
    """
    def __init__(self,
                 name             : str,
                 parameter_list   : list[str],
                 hash_value       : str,
                 python_file      : str,
                 pythonparts      : (list[PythonPart] | None) = None,
                 type_uuid        : str                       = "",
                 type_display_name: str                       = ""):
        """ Initialize

        Args:
            name:              name
            parameter_list:    parameter list
            hash_value:        hash value of the parameter
            python_file:       name of the pyp file
            pythonparts:       list with the PythonParts to put into group
            type_uuid:         define the selectable type defines the selectable type
            type_display_name: display name for the tooltip and object palette

        Raises:
TypeError:      When list of PythonParts to group contains a non-PythonPart object
        """

        self._name              = name
        self._hash_value        = hash_value
        self._python_file       = python_file
        self._parameter_list    = parameter_list
        self._type_uuid         = type_uuid
        self._type_display_name = type_display_name

        if pythonparts is None:
            pythonparts = []

        for elem in pythonparts:
            if not isinstance(elem, PythonPart):
                raise TypeError ('Provided list of the PythonParts contains an object, which is not a PythonPart')

        self._pythonparts = pythonparts


    @classmethod
    def from_build_ele(cls,
                 build_ele        : BuildingElement,
                 name             : str = "",
                 pythonparts      : (list[PythonPart] | None) = None,
                 type_uuid        : str                       = "",
                 type_display_name: str                       = "") -> PythonPartGroup:
        """ Initialize the PythonPart group from a BuildingElement

        Args:
            build_ele:         Building element containing parameter values of the PythonPart group
            name:              Name of the group. If not provided, the name of the .pyp file will be used
            pythonparts:       List of PythonParts to put into group. You can initialize an empty group
                               and append PythonParts to it using append() or extend()
            type_uuid:         define the selectable type defines the selectable type
            type_display_name: display name for the tooltip and object palette

        Returns:
            Constructed PythonPart group

        Raises:
            TypeError:      When list of PythonParts to group contains a non-PythonPart object
        """

        if not name:
            name = Path(build_ele.pyp_file_name).stem

        if pythonparts is not None:
            for pyp in pythonparts:
                if not isinstance(pyp, PythonPart):
                    raise TypeError ('Provided list of the PythonParts contains an object, which is not a PythonPart')

        return cls(name,
                   build_ele.get_params_list(),
                   build_ele.get_hash(),
                   build_ele.pyp_file_name,
                   None,
                   type_uuid, type_display_name)


    def append(self, pythonpart: PythonPart):
        """Add a new PythonPart to the group

        Args:
            pythonpart: PythonPart to add
        """

        self._pythonparts.append(pythonpart)


    def extend(self, pythonparts: list[PythonPart]):
        """Extend the group with new PythonParts

        Args:
            pythonparts: list of PythonParts to add to the group
        """
        self._pythonparts.extend(pythonparts)


    @property
    def pythonparts(self) -> list[PythonPart]:
        """ List of the PythonParts in the group

        Returns:
            PythonParts
        """

        return self._pythonparts


    def __str__(self) ->str:
        """ create the element string

        Returns:
            element string
        """

        return f"PythonPartGroup(name={self._name})\n" \
               f"======================================\n{self._pythonparts}\n"


    def create(self) ->list[AllplanBasisEle.AllplanElement]:
        """ create the PythonPartGroup

        Returns:
            list with the created elements for the PythonPartGroup
        """

        #------------------ Define macro placements / macro definitions for group

        macro_definitions = []
        macro_placements  = []

        for pythonpart in self._pythonparts:
            macro_and_placement = pythonpart.create()

            macro_definitions.append(macro_and_placement[0])
            macro_placements.append(macro_and_placement[1])

        macrogroup_prop      = AllplanBasisEle.MacroGroupProperties()
        macrogroup_prop.Name = self._name
        macrogroup           = AllplanBasisEle.MacroGroupElement(macrogroup_prop, macro_placements)


        #----------------- add the attributes

        param_list_attr, geo_param_values = AttrBuilder.pyp_file_param_list_attr(self._python_file, self._parameter_list)

        attr_list = [param_list_attr,
                     AttrBuilder.python_part_attr()]

        if self._type_uuid:
            attr_list.append(AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_PYTHONPART_UUID, self._type_uuid))

        if self._type_display_name:
            attr_list.append(AllplanBaseEle.AttributeString(AllplanBaseEle.ATTRNR_PYTHONPART_DISPLAY_NAME, self._type_display_name))

        AttributeTakeoverService.add_takeover_attributes(attr_list)

        attributes = AllplanBaseEle.Attributes([AllplanBaseEle.AttributeSet(attr_list)])

        macrogroup.SetAttributes(attributes)
        macrogroup.SetGeometryParameterValueList(geo_param_values)

        macro_definitions.append(macrogroup)

        return macro_definitions
