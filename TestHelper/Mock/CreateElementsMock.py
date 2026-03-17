""" implementation of the mock function for CreateElements.
"""

# pylint: disable="invalid-name"
# pylint: disable="global-statement"
# pylint: disable="unused-argument"

import functools

import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseEle

from TestHelper.CreateTestStringsUtil import CreateTestStringsUtil

MODEL_ELEMENTS       = []
PARAMETER_LISTS      = []
ATTRIBUTE_LISTS      = []
CLEAR_MODEL_ELEMENTS = False
USE_MOCK             = True
ELEMENTS_FROM_DB     = AllplanEleAdapter.BaseElementAdapterList()

ORG_CREATE_ELEMENTS = AllplanBaseEle.CreateElements


def set_use_create_elements_mock(use_mock: bool):
    """ set the use mock state

    Args:
        use_mock: use mock state
    """

    global USE_MOCK

    USE_MOCK = use_mock


def clear_model_elements():
    """ clear the lists with the model elements """

    global MODEL_ELEMENTS
    global PARAMETER_LISTS
    global ATTRIBUTE_LISTS
    global CLEAR_MODEL_ELEMENTS

    MODEL_ELEMENTS  = []
    PARAMETER_LISTS = []
    ATTRIBUTE_LISTS = []

    CLEAR_MODEL_ELEMENTS = False


def set_clear_model_elements():
    """ set the model elements state """

    global CLEAR_MODEL_ELEMENTS

    CLEAR_MODEL_ELEMENTS = True


def CreateElementsMock(doc             : AllplanEleAdapter.DocumentAdapter,
                       insertionMat    : AllplanGeo.Matrix3D,
                       modelElelist    : list,
                       modelUuidlist   : list,
                       assoRefObj      : object,
                       appendReinfPosNr: bool = True,
                       createUndoStep  : bool = True) -> AllplanEleAdapter.BaseElementAdapterList:
    """ Create the elements in the data base

    Args:
        doc:              document of the Allplan drawing files
        insertionMat:     Matrix with the placement point and the rotation
        modelElelist:     list with the model elements
        modelUuidlist:    list with the model UUIDS in modification mode
        assoRefObj:       Associative view reference object
        appendReinfPosNr: True:  Append the reinforcement position numbers to the existing position numbers
        createUndoStep:   Create an undo step after the creation of the PythonPart

    Returns:
        list with the created elements
    """

    global MODEL_ELEMENTS
    global PARAMETER_LISTS
    global ATTRIBUTE_LISTS
    global ELEMENTS_FROM_DB

    if not USE_MOCK:
        ELEMENTS_FROM_DB = ORG_CREATE_ELEMENTS(doc, insertionMat, modelElelist, modelUuidlist, assoRefObj, appendReinfPosNr, createUndoStep)

        modelElelist = AllplanBaseEle.GetElements(ELEMENTS_FROM_DB)

    elif createUndoStep or CLEAR_MODEL_ELEMENTS:
        clear_model_elements()

    if modelElelist:
        model_elements, parameter_list, attribute_list = CreateTestStringsUtil.get_model_elements_data(modelElelist)

        MODEL_ELEMENTS  += model_elements
        PARAMETER_LISTS += parameter_list
        ATTRIBUTE_LISTS += attribute_list

    return ELEMENTS_FROM_DB


def get_elements_text() -> str:
    """ get the element text from the model elements

    Returns:
        elements text
    """

    return str(MODEL_ELEMENTS)


def get_geometry_elements_text() -> str:
    """ get the element text from the geometry elements

    Returns:
        geometry elements text
    """

    return CreateTestStringsUtil.get_geometry_elements_text(MODEL_ELEMENTS)


def get_parameter_list_text() -> str:
    """ get the parameter list text

    Returns:
        parameter list text
    """

    return functools.reduce(lambda text, parameter_list:
                            text + str(parameter_list) + "---------------------------------------------------\n",
                            PARAMETER_LISTS, "")


def get_parameter_list_element_id(element_id: str = "DoubleTeeBeam1") -> str:
    """ get the parameter depends on element_id

    Args:
        element_id: element ID

    Returns:
        parameter list string
    """

    element_id_list = ""

    for param_list in PARAMETER_LISTS:
        param = str(param_list)

        if "__ElementID=" + element_id + "___" not in param:
            continue

        for split_param in param.split("-------------------\n"):
            if "__ElementID=" + element_id + "___" not in split_param:
                continue

            split_lines = split_param.splitlines()

            for split_line in  split_lines:
                if "GUIDParent=" not in split_line:             # pylint: disable=magic-value-comparison
                    element_id_list += split_line + "\n"

    return element_id_list


def get_attributes_text() -> str:
    """ get the attributes text from the model elements

    Returns:
        elements text
    """

    return str(ATTRIBUTE_LISTS)


def get_elements_from_db()  -> AllplanEleAdapter.BaseElementAdapterList:
    """ get the created elements from the data base

    Returns:
        created elements
    """

    return ELEMENTS_FROM_DB
