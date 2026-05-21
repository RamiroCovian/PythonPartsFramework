import random

import NemAll_Python_ArchElements as AllplanArchElements
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
import NemAll_Python_IFW_Input as AllplanIFW

from BuildingElementAttributeList import BuildingElementAttributeList
from DocumentManager import DocumentManager
from PythonPartTransaction import PythonPartTransaction
from TypeCollections.ModificationElementList import ModificationElementList
from Utils.Architecture.OpeningPointsUtil import OpeningPointsUtil

from .solid_opening import SolidOpening


class OpeningCreationUtil:
    """Utility class for creating openings with attributes in Allplan.

    Becase ALLPLAN does not yet support the possibility to create openings
    with attributes, this class is used to create openings and add attributes
    to them in a second transaction step.


    """

    def __init__(self):
        self.document = DocumentManager.get_instance().document
        self.created_openings: list[AllplanElementAdapter.GUID] = []
        self.transaction = PythonPartTransaction(self.document)

    def reset(self):
        """Reset the utility."""
        self.created_openings = []

    def opening_filter(self, element_adapter: AllplanElementAdapter.BaseElementAdapter) -> bool:
        """Filter function to check if the element is a niche tier and not already created.

        Arguments:
            element_adapter: The element adapter to check.

        Returns:
            bool: True if the element is a niche tier and not already created, False otherwise.
        """
        type_filter = AllplanIFW.SelectionQuery([AllplanIFW.QueryTypeID(AllplanElementAdapter.NicheTier_TypeUUID)])

        # Check if the element is of the correct type
        if not type_filter(element_adapter):
            return False

        # Check if the element is already created
        return element_adapter.GetModelElementUUID() not in self.created_openings

    def create_openings(self,
                       elem: AllplanElementAdapter.BaseElementAdapter,
                       openings: list[SolidOpening],
                       attributes: list[AllplanBaseElements.Attribute]):
        """Create openings in the given element and add attributes to them.

        Arguments:
            elem: The element adapter to create openings in.
            openings: A list of SolidOpening objects representing the openings to create.
            attributes: A list of attributes to add to the created openings.
        """

        for opening in openings:
            placement = opening.placement
            length = opening.size[0]
            width = opening.size[1]
            heigh = opening.size[2]
            opp = self._create_opening_element(
                random.random() * 3600,
                elem,
                AllplanGeo.Point3D(placement.X, placement.Y, placement.Z),
                length,
                width,
                heigh)

            created_elements = self.transaction.execute(
                AllplanGeo.Matrix3D(),
                AllplanIFW.ViewWorldProjection(), # this is OK only, as long as no reinforcenent labels or UVSs are to be created
                [opp],
                ModificationElementList())
            # created_elements = AllplanBaseElements.CreateElements(self.document, AllplanGeo.Matrix3D(), [opp], [], None)

            created_openings = list(filter(self.opening_filter, created_elements))

            if not created_openings:
                print("No openings created")
                continue

            # keep track of created openings
            for created_opening in created_openings:
                self.created_openings.append(created_opening.GetModelElementUUID())

            if not attributes:
                continue

            opening_attribute_list = BuildingElementAttributeList()
            opening_attribute_list.add_attribute_list(attributes)

            opening_elems = AllplanElementAdapter.BaseElementAdapterList(created_openings)

            if len(opening_elems) > 0:
                print("Adding attributes:\n", opening_attribute_list)
                print("to opening:\n")

                for opening_elem in opening_elems:
                    print(opening_elem.GetModelElementUUID())

                self.add_attributes(opening_elems, opening_attribute_list)


    def _create_opening_element(self,
            random: float,
            wall: AllplanElementAdapter.BaseElementAdapter,
            opening_pos: AllplanGeo.Point3D,
            llarg: float,
            gruix: float,
            alt: float
            ) -> AllplanArchElements.GeneralOpeningElement:
        # opp_build_ele = self.build_ele
        #----------------- create the properties
        if not (general_axis_ele := AllplanElementAdapter.AxisElementAdapter(wall)).IsNull():
            general_ele_axis = general_axis_ele.GetAxis()

        general_ele_geo   = wall.GetGroundViewArchitectureElementGeometry()

        start_pnt = AllplanGeo.Point3D(opening_pos.X,
                                       opening_pos.Y,
                                       opening_pos.Z)
        end_pnt = AllplanGeo.Point3D(opening_pos.X + llarg,
                                     opening_pos.Y,
                                     opening_pos.Z)
        placement_line    = AllplanGeo.Line2D(start_pnt.To2D, end_pnt.To2D)

        opening_prop = AllplanArchElements.GeneralOpeningProperties(
            AllplanArchElements.OpeningType.eRecess) #AllplanArchElements.OpeningType.eRecess

        opening_prop.VisibleInViewSection3D   = True
        opening_prop.Independent2DInteraction = False

        plane_ref = AllplanArchElements.PlaneReferences(self.document, AllplanElementAdapter.BaseElementAdapter())
        plane_ref.SetBottomOffset(opening_pos.Z)
        plane_ref.SetHeight(alt)
        opening_prop.PlaneReferences = plane_ref

        geom = opening_prop.GetGeometryProperties()
        geom.Depth = gruix


        #----------------- create the opening
        if not AllplanElementAdapter.AxisElementAdapter(wall).IsNull():
            opening_end_pnt = OpeningPointsUtil.create_opening_end_point_for_axis_element(start_pnt.To2D,
                                                                                          llarg,
                                                                                          general_ele_axis,
                                                                                          general_ele_geo,
                                                                                          placement_line)
        else:
            opening_end_pnt = OpeningPointsUtil.create_opening_end_point_for_shaped_element(start_pnt.To2D,
                                                                                            llarg,
                                                                                            placement_line)

        return AllplanArchElements.GeneralOpeningElement(
            opening_prop,
            wall,
            start_pnt.To2D,
            opening_end_pnt,
            drawPlacementPreview = False
            )


    def add_attributes(self, elems: AllplanElementAdapter.BaseElementAdapterList, attribute_list: BuildingElementAttributeList):
        for elem in elems:
            AllplanBaseElements.ElementsAttributeService.ChangeAttributes(
                attribute_list.get_attributes_list_as_tuples(),
                AllplanElementAdapter.BaseElementAdapterList(list([elem])))


class WindowOpeningCreationUtil(OpeningCreationUtil):
    """Utility class for creating window openings with attributes in Allplan.

    Variant of OpeningCreationUtil that produces WindowOpeningElement instead of
    GeneralOpeningElement (recess). The created elements are identified by
    WindowTier_TypeUUID instead of NicheTier_TypeUUID.
    """

    def opening_filter(self, element_adapter: AllplanElementAdapter.BaseElementAdapter) -> bool:
        """Filter function to check if the element is a window tier and not already created.

        Arguments:
            element_adapter: The element adapter to check.

        Returns:
            bool: True if the element is a window tier and not already created, False otherwise.
        """
        type_filter = AllplanIFW.SelectionQuery([AllplanIFW.QueryTypeID(AllplanElementAdapter.WindowTier_TypeUUID)])

        if not type_filter(element_adapter):
            return False

        return element_adapter.GetModelElementUUID() not in self.created_openings

    def _create_opening_element(self,
            random: float,
            wall: AllplanElementAdapter.BaseElementAdapter,
            opening_pos: AllplanGeo.Point3D,
            llarg: float,
            gruix: float,
            alt: float
            ) -> AllplanArchElements.WindowOpeningElement:
        if not (general_axis_ele := AllplanElementAdapter.AxisElementAdapter(wall)).IsNull():
            general_ele_axis = general_axis_ele.GetAxis()

        general_ele_geo = wall.GetGroundViewArchitectureElementGeometry()

        start_pnt = AllplanGeo.Point3D(opening_pos.X,
                                       opening_pos.Y,
                                       opening_pos.Z)
        end_pnt = AllplanGeo.Point3D(opening_pos.X + llarg,
                                     opening_pos.Y,
                                     opening_pos.Z)
        placement_line = AllplanGeo.Line2D(start_pnt.To2D, end_pnt.To2D)

        opening_prop = AllplanArchElements.WindowOpeningProperties()

        opening_prop.Independent2DInteraction = False

        plane_ref = AllplanArchElements.PlaneReferences(self.document, AllplanElementAdapter.BaseElementAdapter())
        plane_ref.SetBottomOffset(opening_pos.Z)
        plane_ref.SetHeight(alt)
        opening_prop.PlaneReferences = plane_ref

        geom = opening_prop.GetGeometryProperties()
        geom.Depth = gruix

        if not AllplanElementAdapter.AxisElementAdapter(wall).IsNull():
            opening_end_pnt = OpeningPointsUtil.create_opening_end_point_for_axis_element(start_pnt.To2D,
                                                                                          llarg,
                                                                                          general_ele_axis,
                                                                                          general_ele_geo,
                                                                                          placement_line)
        else:
            opening_end_pnt = OpeningPointsUtil.create_opening_end_point_for_shaped_element(start_pnt.To2D,
                                                                                            llarg,
                                                                                            placement_line)

        return AllplanArchElements.WindowOpeningElement(
            opening_prop,
            wall,
            start_pnt.To2D,
            opening_end_pnt,
            drawPlacementPreview = False
            )
