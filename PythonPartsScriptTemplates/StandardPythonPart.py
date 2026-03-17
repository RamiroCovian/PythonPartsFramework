""" A template script for creating a standard PythonPart
"""
from typing import List, Tuple

import NemAll_Python_Geometry as AllplanGeometry
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_Input as AllplanIFWInput
import NemAll_Python_Reinforcement as AllplanReinforcement
from BuildingElement import BuildingElement
from ControlPropertiesUtil import ControlPropertiesUtil
from CreateElementResult import CreateElementResult
from HandleProperties import HandleProperties
from HandlePropertiesService import HandlePropertiesService


def check_allplan_version(build_ele: BuildingElement,
                          version: float) -> bool:
    """Called when the PythonPart is started to check, if the current
    Allplan version is supported.

    Args:
        build_ele: building element with the parameter properties
        version:   current Allplan version

    Returns:
        True if current Allplan version is supported and PythonPart script can be run, False otherwise
    """

    return True


def migrate_parameter(parameter_list: list,
                      version: float) -> None:
    """Migrate the parameter

    This function is called only during the modification of a PythonPart

    Args:
        parameter_list: parameter list
        version:        current PythonPart version
    """


def create_docking_points(build_ele: BuildingElement,
                          doc      : AllplanElementAdapter.DocumentAdapter) -> Tuple[List[Tuple[str, AllplanGeometry.Point3D]],
                                                                                     List[Tuple[str, AllplanGeometry.Point3D]],
                                                                                     List[Tuple[str, AllplanGeometry.Point3D]]]:
    """ Creation of the docking points

    Args:
        build_ele: building element with the parameter properties
        doc:       document of the Allplan drawing files

    Returns:
        list of tuples (key, docking_point) for the 2D view
        list of tuples (key, docking_point) for the 3D view
        list of tuples (key, docking_point) for the 2D and 3D view
    """

    return ...


def move_handle(build_ele: BuildingElement,
                handle_prop: HandleProperties,
                input_pnt: AllplanGeometry.Point3D,
                doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Called after modification of the element geometry using handles

    Args:
        build_ele:      building element with the parameter properties
        handle_prop:    handle properties
        input_pnt:      input point
        doc:            input document

    Returns:
        Object with the result data of the element creation

    """
    HandlePropertiesService.update_property_value(build_ele, handle_prop, input_pnt)

    return create_element(build_ele, doc)


def expand_create_element(build_ele_list: BuildingElement,
                          expand_util: AllplanReinforcement.GeometryExpansionUtil ,
                          ref_pnt: AllplanGeometry.Point2D,
                          view_proj: AllplanIFWInput.ViewWorldProjection,
                          doc: AllplanElementAdapter.DocumentAdapter,
                          last_expanded: bool
                          ) -> Tuple[bool,
                                     bool,
                                     AllplanGeometry.Point3D,
                                     AllplanElementAdapter.BaseElementAdapter,
                                     CreateElementResult]:
    """Creation of the element based on geometry expansion. This function is called
    with every mouse movement in the window, when the <GeometryExpand> tag is set to True
    in the .pyp file

    Args:
        build_ele_list: list with the building element.
        expand_util:    the utility for expansion.
        ref_pnt:        reference point.
        view_proj:      view world projection.
        doc:            input document
        last_expanded:  True if the geometry of the current element is created by an expansion
                        (in case of False it's not necessary to create the original element geometry)

    Returns:
        True, if the expansion was successful
        True, if  the handles should be displayed
        placement point
        the element on which the expansion was done
        created elements
    """

    return ... , ... , ... , ... , ...


def initialize_control_properties(build_ele: BuildingElement,
                                  ctrl_prop_util: ControlPropertiesUtil,
                                  doc: AllplanElementAdapter.DocumentAdapter) -> None:
    """Called after the properties and their values are read, but before
    the property palette is displayed.

    Args:
        build_ele:      building element
        ctrl_prop_util: control properties utility
        doc:            document
    """


def modify_control_properties(build_ele: BuildingElement,
                              ctrl_prop_util: ControlPropertiesUtil,
                              value_name: str,
                              event_id: int,
                              doc: AllplanElementAdapter.DocumentAdapter) -> bool:
    """Called after each change within the property palette

    Args:
        build_ele:      building element
        ctrl_prop_util: control properties utility
        value_name:     name(s) of the modified value (multiple names are separated by ,)
        event_id:       event ID
        doc:            document

    Returns:
        True if an update of the property palette is necessary, False otherwise
    """

    return True


def set_active_palette_page_index(active_page_index: int) -> None:
    """ Called when changing page in the property palette

    Args:
        active_page_index: index of the active page, starting from 0
    """


def on_control_event(build_ele: BuildingElement,
                     event_id: int,
                     doc: AllplanElementAdapter.DocumentAdapter) -> bool:
    """ Called, when an event is triggered with a control (e.g. a button) in a property palette

    Args:
        build_ele: building element with the parameter properties
        event_id:  event id of the triggered control
        doc:       document of the Allplan drawing files

    Returns:
        True if palette refresh is necessary, False otherwise
    """


def create_preview(build_ele: BuildingElement,
                   doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Function for the creation of the library preview elements.

    Args:
        build_ele: the building element.
        doc:       input document

    Returns:
        Preview elements. Only elements included in the property "elements" will be shown in the library preview
    """

    return CreateElementResult(elements=[...])


def create_element(build_ele: BuildingElement,
                   doc: AllplanElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Function for the element creation

    Args:
        build_ele: the building element.
        doc:       input document

    Returns:
        created element result
    """

    return CreateElementResult()
