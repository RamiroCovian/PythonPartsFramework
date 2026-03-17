"""Implementation of the bottom top plane service mock
"""

import NemAll_Python_ArchElements as AllplanArchEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Geometry

from DocumentManager import DocumentManager

TOP_REF_PLANE    = AllplanArchEle.PlaneReferences(DocumentManager.get_instance().document, AllplanEleAdapter.BaseElementAdapter())
BOTTOM_REF_PLANE = AllplanArchEle.PlaneReferences(DocumentManager.get_instance().document, AllplanEleAdapter.BaseElementAdapter())

from NemAll_Python_ArchElements import BasePlaneReferences

class BottomTopPlaneServiceMock():
    """Implementation of the bottom top plane service mock
    """
    @staticmethod
    def GetAbsoluteBottomElevation(refElement: AllplanEleAdapter.BaseElementAdapter,
                                   doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> float:
        """Get the absolute elevation of the bottom plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Absolute elevation of the bottom plane
        """

    @staticmethod
    def GetAbsoluteTopElevation(refElement: AllplanEleAdapter.BaseElementAdapter,
                                doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> float:
        """Get the absolute elevation of the top plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Absolute elevation of the top plane
        """

    @staticmethod
    def GetBottomReferencePlane(refElement: AllplanEleAdapter.BaseElementAdapter,
                                doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> (NemAll_Python_Geometry.BRep3D | NemAll_Python_Geometry.Polyhedron3D | NemAll_Python_Geometry.Plane3D):
        """Get the bottom reference plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Bottom reference plane as Plan3D, BRep3D or Polyhedron3D
        """

        return BOTTOM_REF_PLANE

    @staticmethod
    def GetDocumentBottomElevation(refElement: AllplanEleAdapter.BaseElementAdapter,
                                   doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> float:
        """Get the document elevation of the bottom plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Absolute elevation of the bottom plane
        """

    @staticmethod
    def GetDocumentDefaultPlanes(doc: AllplanEleAdapter.DocumentAdapter) -> tuple[NemAll_Python_Geometry.Plane3D,
                                 NemAll_Python_Geometry.Plane3D]:
        """Get the default bottom and top plane of the document

        Args:
            doc

        Returns:
            Default bottom and top plane of the document
        """

    @staticmethod
    def GetDocumentTopElevation(refElement: AllplanEleAdapter.BaseElementAdapter,
                                doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> float:
        """Get the document elevation of the top plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Absolute elevation of the top plane
        """

    @staticmethod
    def GetTopReferencePlane(refElement: AllplanEleAdapter.BaseElementAdapter,
                             doc: AllplanEleAdapter.DocumentAdapter, planeProp: BasePlaneReferences) -> (NemAll_Python_Geometry.BRep3D | NemAll_Python_Geometry.Polyhedron3D | NemAll_Python_Geometry.Plane3D):
        """Get the top reference plane

        Args:
            refElement: Reference element (empty element if not exist)
            doc:        Document
            planeProp:  Plane properties

        Returns:
            Bottom reference plane as Plan3D, BRep3D or Polyhedron3D
        """

        return TOP_REF_PLANE


    @staticmethod
    def set_bottom_ref_plane(bottom_ref_plane: AllplanArchEle.PlaneReferences):
        """ set the bottom reference plane

        Args:
            bottom_ref_plane: bottom reference plane
        """

        global BOTTOM_REF_PLANE

        BOTTOM_REF_PLANE = bottom_ref_plane


    @staticmethod
    def set_top_ref_plane(top_ref_plane: AllplanArchEle.PlaneReferences):
        """ set the top reference plane

        Args:
            top_ref_plane: top reference plane
        """

        global TOP_REF_PLANE

        TOP_REF_PLANE = top_ref_plane
