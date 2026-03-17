""" Example script for FS
"""
import random
from .PLD import PLD
from .XPS import XPS
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
from CreateElementResult import CreateElementResult
from DocumentManager import DocumentManager
from TypeCollections.ModelEleList import ModelEleList
from BuildingElement import BuildingElement

print('Load FS.py')

def check_allplan_version(build_ele, version):
    """ Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """
    del build_ele
    del version
    return True

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """Move handle function

    Args:
        build_ele (_type_): _description_
        handle_prop (_type_): _description_
        input_pnt (_type_): _description_
        doc (_type_): _description_

    Returns:
        _type_: _description_
    """
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def on_control_event(build_ele: BuildingElement, event_id: int):
    """Control event function

    Args:
        build_ele (BuildingElement): _description_
        event_id (int): _description_
    """
    # Events ID
    envent_id_create_figure = 1000

    doc = DocumentManager.get_instance().document
    if event_id == envent_id_create_figure:
        create_element(build_ele, doc)

def create_element_class(build_ele, doc, placement_mat = AllplanGeo.Matrix3D()):
    """Create element class

    Args:
        build_ele (_type_): _description_
        doc (_type_): _description_
        placement_mat (_type_, optional): _description_. Defaults to AllplanGeo.Matrix3D().

    Returns:
        _type_: _description_
    """

    # Define name parameters
    z_unique = build_ele.zUnique.value
    ancho_pld = build_ele.AnchoPLD.value
    alto_pld = build_ele.LargoPLD.value
    grosor_xps = build_ele.EspesorXPS.value
    z_rotation = build_ele.ZRotationInput.value
    type_pld = build_ele.TypePLD.value
    layer_value_name = build_ele.LayerValueName.value
    borde_afilado_selector = build_ele.SelectorBordeAfilado.value

    # Define model element and add figures
    model_elements = ModelEleList()

    pld_element = PLD(doc, z_unique, ancho_pld, alto_pld, z_rotation, type_pld, layer_value_name, borde_afilado_selector)
    xps_element = XPS(doc, z_unique, ancho_pld, alto_pld, grosor_xps, z_rotation, layer_value_name)

    # Create elements
    model_elements += pld_element.create()
    model_elements += xps_element.create()

    # Create handles after update values
    handle_list = pld_element.create_handles()

    # model_elem_list = pythonpartgroup.create()
    # model_elem_list_preview = pythonpartgroup_preview.create()

    #return (model_elem_list, handle_list)

    result = {
        "elements"              :  model_elements,
        "handles"               :  handle_list,
        "preview_elements"      :  model_elements}

    return result

def create_element(build_ele, doc):
    """Create element

    Args:
        build_ele (_type_): _description_
        doc (_type_): _description_

    Returns:
        _type_: _description_
    """
    result = create_element_class(build_ele, doc)
    #model_elem_list = result["model_elem_list"]
    model_elem_list = result["elements"]
    handle_list = result["handles"]
    model_elem_list_preview = result["preview_elements"]
    return CreateElementResult(elements=            model_elem_list,
                                handles=            handle_list,
                                preview_elements=   model_elem_list_preview)

class FS():
    """Define FS class
    """

    def __init__(self, build_ele, doc, placement_mat = AllplanGeo.Matrix3D() ):
        """Initialize values

        Args:
            build_ele (_type_): _description_
            doc (_type_): _description_
            placement_mat (_type_, optional): _description_. Defaults to AllplanGeo.Matrix3D().
        """

        self.build_fs = build_ele
        self._doc = doc

        self.placement_mat = placement_mat

    def create(self):
        """Create FS

        Returns:
            _type_: _description_
        """

        result = create_element_class(self.build_fs , self._doc, self.placement_mat)

        model_elem_list = result["elements"]
        handle_list = result["handles"]
        model_elem_list_preview = result["preview_elements"]

        result = {
            "elements"              :  model_elem_list,
            "handles"               :  handle_list,
            "preview_elements"      :  model_elem_list_preview}

        return result