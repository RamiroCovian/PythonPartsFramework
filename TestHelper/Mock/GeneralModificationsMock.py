""" implementation of the mock functions for the general modifications
"""

# pylint: disable=invalid-name

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

USE_MOCK = True

ORG_DELETE_ELEMENTS = AllplanBaseEle.DeleteElements


def set_use_delete_elements_mock(use_mock: bool):
    """ set the use mock state

    Args:
        use_mock: use mock state
    """

    global USE_MOCK

    USE_MOCK = use_mock


def DeleteElementsMock(doc     : AllplanEleAdapter.DocumentAdapter,
                       elements: AllplanEleAdapter.BaseElementAdapterList):
    """ Delete the elements

    Args:
        doc:      document of the Allplan drawing files
        elements: List with the UUIDs of the data base elements
    """

    global USE_MOCK

    if not USE_MOCK:
        ORG_DELETE_ELEMENTS(doc, elements)

        USE_MOCK = True
