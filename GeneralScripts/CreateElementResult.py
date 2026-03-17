""" Implementation of the data class for the result of the create_element function
"""

from typing import Any

from dataclasses import dataclass, field

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from HandleProperties import HandleProperties
from PreviewSymbols import PreviewSymbols
from PythonPartTransaction import ConnectToElements, ReinforcementRearrange


@dataclass
class CreateElementResult():
    """ Implementation of the data class for the result of the create_element function

    Attributes:
        elements:               list of elements to create
        handles:                list of handles to create
        preview_element:        list of element to draw only in the preview
        placement_point:        if set, the point is used as global placement point for the elements
        multi_placement:        if True, the elements can be placed multiple times
        preview_symbols:        preview symbols to show in the preview
        reinf_rearrange:        properties for rearranging the reinforcement mark numbering
        handle_placement_geo:   elements, which should be used during the handle modification
        as_static_preview:      if True, the preview is drawn as static preview
        connect_to_ele:         data for the PythonPart connection to element(s)
        uuid_parameter_name:    if set, the model object UUID of the created PythonPart is assigned to this name
        elements_to_delete:     elements which should be delete
    """

    elements            : list[Any]                                          = field(default_factory = list)
    handles             : list[HandleProperties]                             = field(default_factory = list)
    preview_elements    : list[Any]                                          = field(default_factory = list)
    placement_point     : ((AllplanGeo.Point2D | AllplanGeo.Point3D) | None) = None
    multi_placement     : bool                                               = False
    preview_symbols     : (PreviewSymbols | None)                            = None
    reinf_rearrange     : ReinforcementRearrange                             = field(default_factory = ReinforcementRearrange)
    handle_placement_geo: list[Any]                                          = field(default_factory = list)
    as_static_preview   : bool                                               = False
    connect_to_ele      : ConnectToElements                                  = field(default_factory = ConnectToElements)
    uuid_parameter_name : str                                                = ""
    elements_to_delete  : (AllplanEleAdapter.BaseElementAdapterList | None)  = None

    def is_empty(self) -> bool:
        """ check for empty data

        Returns:
            True if no elements and handles exist, otherwise False
        """

        return not self.elements and not self.preview_elements and not self.handles
