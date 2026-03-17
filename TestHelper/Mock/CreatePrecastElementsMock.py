""" implementation of the mock function for CreatePrecastElements. """

# pylint: disable="invalid-name"

import typing

from NemAll_Python_IFW_Input import ViewWorldProjection
from NemAll_Python_IFW_ElementAdapter import DocumentAdapter, BaseElementAdapterList
from NemAll_Python_Geometry import Matrix3D

def CreatePrecastElementsMock(_doc: DocumentAdapter,
                              _insertionMat: Matrix3D,
                              _elements: BaseElementAdapterList,
                              _modelEleList: typing.List,
                              _modelUuidList: typing.List,
                              _viewProj: ViewWorldProjection,
                              _delete_python: bool) -> None:
    """ Create the precast elements

    Parameter: _doc             Document
               _insertionMat    Insertion matrix
               _elements        List of created elements
               _modelEleList    List of model elements which have to be created
               _modelUuidList   List with the model UUIDS in modification mode
               _viewProj        View projection
               _delete_python   bool weather the python should be deleted after update
    """
