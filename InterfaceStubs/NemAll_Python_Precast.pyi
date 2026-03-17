# pylint: disable=invalid-name
# pylint: disable=used-before-assignment
# pylint: disable=too-many-public-methods
# pylint: disable=c-extension-no-member
# pylint: disable=import-self
# pylint: disable=empty-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=redefined-builtin
# pylint: disable=anomalous-backslash-in-string
# pylint: disable=too-few-public-methods
# pylint: disable=function-redefined
# pylint: disable=eq-without-hash

"""Exposed classes and functions from NemAll_Python_Precast"""

from __future__ import annotations

import typing

import enum
import collections.abc

import NemAll_Python_BaseElements
import NemAll_Python_Geometry
import NemAll_Python_IFW_ElementAdapter
import NemAll_Python_IFW_Input


__all__ = [
    "AllowedElements",
    "AllplanElement",
    "Anchor",
    "AnchorBorderPosition",
    "AssemblyGroupElement",
    "Cell",
    "ClippingPathProperties",
    "CreateElementplan",
    "CreatePrecastElements",
    "Direction",
    "DirectionMode",
    "DirectionProperties",
    "FileEntryPath",
    "FinishProperties",
    "FixtureCombinationType",
    "FixtureElement",
    "FixtureGroupElement",
    "FixtureGroupProperties",
    "FixturePlacementElement",
    "FixturePlacementProperties",
    "FixtureProperties",
    "FixtureSlideElement",
    "FixtureSlideProperties",
    "FixtureSlideType",
    "FixtureSlideViewType",
    "FormatProperties",
    "GetPagePropertiesFromCatalog",
    "HeadingProperties",
    "HeightDefinitionType",
    "LabelStyle",
    "LabelStyleProperties",
    "LabelingProperties",
    "Legend",
    "LegendProperties",
    "LightProperties",
    "LineProperties",
    "Location",
    "LockPrecastUpdate",
    "MacroGroupType",
    "MacroSubType",
    "MacroType",
    "OutlineShape",
    "OutlineType",
    "OutlineTypeInGroup",
    "Page",
    "PageProperties",
    "PagePropertiesList",
    "Plan",
    "Position",
    "PrecastElement",
    "PrecastElementProperties",
    "PrecastLayer",
    "PrecastLayerProperties",
    "PrecastMWSElement",
    "PrecastProperties",
    "ProfilType",
    "RepresentationProperties",
    "Rotation",
    "ScaleProperties",
    "SectionProperties",
    "SubType",
    "SurfaceProperties",
    "TextAlignment",
    "TextParameters",
    "TextProperties",
    "TriggerPrecastUpdate",
    "Type",
    "UnlockPrecastUpdate",
    "View",
    "ViewProperties",
    "VisibilityProperties",
    "e2D_BACK_VIEW",
    "e2D_FRONT_VIEW",
    "e2D_LEFT_VIEW",
    "e2D_NO_VIEW",
    "e2D_RIGHT_VIEW",
    "e2D_SYMBOL",
    "e2D_TOP_VIEW",
    "e3D_VIEW",
    "e3D_VIEW_OLD",
    "e3D_VIEW_OUTLINE_AREA",
    "e3D_VIEW_OUTLINE_AREA_ACTUAL",
    "e3D_VIEW_OUTLINE_VOLUME",
    "eAccordingTheUSStandard",
    "eAll",
    "eAnchorPlate",
    "eAnchorage",
    "eAverage",
    "eBOTTOM_VIEW",
    "eBUILTIN_OUTLINE_SHAPE_NOTHING",
    "eBUILTIN_OUTLINE_SHAPE_RECTANGLE",
    "eBUILTIN_OUTLINE_SHAPE_SYMBOL",
    "eBUILTIN_OUTLINE_SHAPE_TRAPEZOID",
    "eBUILTIN_OUTLINE_TYPE_IN_GROUP_MINUS",
    "eBUILTIN_OUTLINE_TYPE_IN_GROUP_NOTHING",
    "eBUILTIN_OUTLINE_TYPE_IN_GROUP_PLUS",
    "eBUILTIN_OUTLINE_TYPE_MINUS",
    "eBUILTIN_OUTLINE_TYPE_NOTHING",
    "eBUILTIN_OUTLINE_TYPE_NO_AFFECT",
    "eBUILTIN_OUTLINE_TYPE_PLUS",
    "eBUILTIN_PROFIL_TYPE_EDGE",
    "eBUILTIN_PROFIL_TYPE_JOINT",
    "eBarAccessory",
    "eBarCoupler",
    "eBarNut",
    "eBarThread",
    "eBorderBottom",
    "eBorderHorizontal",
    "eBorderInnerBottom",
    "eBorderInnerHorizontal",
    "eBorderInnerLeft",
    "eBorderInnerRight",
    "eBorderInnerTop",
    "eBorderInnerVertical",
    "eBorderLeft",
    "eBorderRight",
    "eBorderTop",
    "eBorderVertical",
    "eBottomCenter",
    "eBottomLeft",
    "eBottomRight",
    "eBracingElement",
    "eCONNECTION_POINT",
    "eCONTOUR_CUT",
    "eCatchmentArea",
    "eCenter",
    "eChannel",
    "eCirculationLoadPoint",
    "eCirculationPipeAdapter",
    "eCirculationStartPoint",
    "eCode",
    "eComponent",
    "eConcreteArea",
    "eConcreteBeam",
    "eConcreteBlock",
    "eConnectionModeller",
    "eConnectionWallColumn",
    "eConnectorEBT",
    "eConstPrefabConnection",
    "eCorbel",
    "eCornerInnerLeftBottom",
    "eCornerInnerLeftTop",
    "eCornerInnerRightBottom",
    "eCornerInnerRightTop",
    "eCornerLeftBottom",
    "eCornerLeftTop",
    "eCornerRightBottom",
    "eCornerRightTop",
    "eCoverMountingAngle",
    "eCrossRib",
    "eDirectionI",
    "eDirectionII",
    "eDirectionIII",
    "eDirectionIV",
    "eDirectionV",
    "eDirectionVI",
    "eElectricalBIE",
    "eElectricalLamp",
    "eElectricalRoute",
    "eExtension",
    "eFacility",
    "eFalseJoint",
    "eFileEntryPathLibrary",
    "eFileEntryPathOffice",
    "eFileEntryPathPrivate",
    "eFileEntryPathProject",
    "eFileEntryPathProjectPlus",
    "eFileEntryPathStandard",
    "eFill",
    "eFrame",
    "eFull",
    "eGeometry",
    "eGroupType_CuttedGroup",
    "eGroupType_DynamicGroup",
    "eGroupType_GeneralGroup",
    "eGroupType_LeadingGroup",
    "eGroup_Fixture",
    "eHeatingLoadPoint",
    "eHeatingPipeAdapter",
    "eHeatingStartPoint",
    "eHollowBody",
    "eInsertion",
    "eInsulationArea",
    "eInsulationElement",
    "eInsulationStripe",
    "eJointLength",
    "eJointReinforcement",
    "eLOCK_FIXED",
    "eLOCK_FIXED_P1",
    "eLOCK_UML",
    "eLeftBottom",
    "eLeftCenter",
    "eLeftTop",
    "eLinePointPlacement",
    "eLine_Fixture",
    "eLoadCut",
    "eMEASURE_POINTS",
    "eMacro",
    "eMultiLine3D",
    "eNailer",
    "eNode",
    "eNone",
    "eORGA_ORIGINAL",
    "eOnlyThese",
    "eOverrule",
    "ePipe",
    "ePipePoint",
    "ePlacingLoop",
    "ePlane_Fixture",
    "ePoint_Fixture",
    "ePolyline",
    "ePrefabConnection",
    "ePrefabConnectionCorner",
    "ePrefabModeller",
    "eProfileEdge",
    "eReinforcement",
    "eReinforcement_Cage",
    "eReport",
    "eRestricted",
    "eRevealAnchor",
    "eRevealAnchorVirtual",
    "eRibBody",
    "eRightBottom",
    "eRightCenter",
    "eRightTop",
    "eRingBeam",
    "eRoofLine",
    "eRoofParapetLine",
    "eRoofParapetSupport",
    "eRope",
    "eRotation0",
    "eRotation180",
    "eRotation270",
    "eRotation90",
    "eSTD_Formwork",
    "eSanitationLoadPoint",
    "eSanitationPipeAdapter",
    "eSanitationStartPoint",
    "eSecondaryReinf",
    "eSewageLoadPoint",
    "eSewageNetElement",
    "eSewagePipeAdapter",
    "eSewageStartPoint",
    "eShaft",
    "eSlidingRestraint",
    "eSolidStrip",
    "eSpecialBuilding",
    "eSpecialLoad_Undefined",
    "eSpecialLoad_X",
    "eSpecialLoad_Y",
    "eSpecialLoad_Z",
    "eSphere",
    "eSteelProfile",
    "eStripCorbel",
    "eStructuralRecessFaceSupport",
    "eStructuralRecessLongitudinalSupport",
    "eSurface",
    "eTGA_ADAPTER",
    "eTheseNot",
    "eTieBar",
    "eTileArea",
    "eTileElement",
    "eTopCenter",
    "eTopLeft",
    "eTopRight",
    "eTrimmer",
    "eUndergroundCadaster",
    "eUnknownAlignment",
    "eUseNoSpecialSubType",
    "eUseSameSubType",
    "eUseSameType",
    "eVentilationDuctAdapter",
    "eVentilationLoadPoint",
    "eVentilationStartPoint",
    "eVx",
    "eVy",
    "eVz",
    "eZone"
]


class AllowedElements(enum.Enum):
    """allowed elements for visibility
    """
    eAll = 0
    eOnlyThese = 1
    eTheseNot = 2

    names = {eAll: eAll,
             eOnlyThese: eOnlyThese,
             eTheseNot: eTheseNot}

    values = {0: eAll,
              1: eOnlyThese,
              2: eTheseNot}

    def __getitem__(self, key: (str | int | float)) -> AllowedElements:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class AllplanElement():
    """Implementation of the Allplan element
    """
    def GetAttributes(self) -> object:
        """Get the attributes object

        Returns:
            Attributes object
        """
    def GetBaseElementAdapter(self) -> NemAll_Python_IFW_ElementAdapter.BaseElementAdapter:
        """Get the model element

        Returns:
            Model element
        """
    def GetCommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties

        Returns:
            Common properties
        """
    def GetGeometryObject(self) -> object:
        """Get the geometry object

        Returns:
            Geometry object
        """
    def GetLabelElements(self) -> list:
        """Get the label elements

        Returns:
            LabelElements
        """
    def GetSubElementID(self) -> type:
        """Get the SubElementID

        Returns:
            SubElementID
        """
    def SetAttributes(self, attributeContainer: object):
        """Set the attributes object

        Args:
            attributeContainer: Attributes object
        """
    def SetCommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties):
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    def SetDockingPointsKey(self, dockingPointsKey: str):
        """Set the docking points key

        Args:
            dockingPointsKey: Docking points key
        """
    def SetGeometryObject(self, geoObject: object):
        """Set the geometry object

        Args:
            geoObject: Geometry object
        """
    def SetLabelElements(self, labelElements: list):
        """Set the label elements

        Args:
            labelElements: Label elements
        """
    @property
    def Attributes(self) -> object:
        """Get the attributes object
        """
    @Attributes.setter
    def Attributes(self, attributeContainer: object) -> None:
        """Set the attributes object

        Args:
            attributeContainer: Attributes object
        """
    @property
    def CommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties
        """
    @CommonProperties.setter
    def CommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties) -> None:
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    @property
    def GeometryObject(self) -> object:
        """Get the geometry object
        """
    @GeometryObject.setter
    def GeometryObject(self, geoObject: object) -> None:
        """Set the geometry object

        Args:
            geoObject: Geometry object
        """
    @property
    def LabelElements(self) -> list:
        """Get the label elements
        """
    @LabelElements.setter
    def LabelElements(self, labelElements: list) -> None:
        """Set the label elements

        Args:
            labelElements: Label elements
        """

class Anchor():

    @typing.overload
    def __init__(self, id: int, fromId: int, fromPos: AnchorBorderPosition, toId: int, toPos: AnchorBorderPosition):
        """Constructor

        Args:
            Anchor:ID
            From:cell ID
            From:cell pos
            To:cell ID
            To:cell pos
        """
    @typing.overload
    def __init__(self, id: int, fromId: int, fromPos: AnchorBorderPosition, toId: int, toPos: AnchorBorderPosition, align: bool,
                 offsetX: float, offsetY: float):
        """Constructor

        Args:
            Anchor:ID
            From:cell ID
            From:cell pos
            To:cell ID
            To:cell pos
            Align
            Offset:x
            Offset:y
        """
    @typing.overload
    def __init__(self, id: int, fromPos: AnchorBorderPosition, toId: int, toPos: AnchorBorderPosition):
        """Constructor

        Args:
            Anchor:ID
            From:cell pos
            To:cell ID
            To:cell pos
        """
    @typing.overload
    def __init__(self, id: int, fromPos: AnchorBorderPosition, toId: int, toPos: AnchorBorderPosition, offsetX: float, offsetY: float):
        """Constructor

        Args:
            Anchor:ID
            From:cell pos
            To:cell ID
            To:cell pos
            Offset:x
            Offset:y
        """
    @typing.overload
    def __init__(self, id: int, fromCell: Cell, fromPos: AnchorBorderPosition, toCell: Cell, toPos: AnchorBorderPosition):
        """Constructor

        Args:
            Anchor:ID
            From:cell
            From:cell pos
            To:cell
            To:cell pos
        """
    @typing.overload
    def __init__(self, id: int, fromCell: Cell, fromPos: AnchorBorderPosition, toCell: Cell, toPos: AnchorBorderPosition, align: bool,
                 offsetX: float, offsetY: float):
        """Constructor

        Args:
            Anchor:ID
            From:cell
            From:cell pos
            To:cell
            To:cell pos
            Align
            Offset:x
            Offset:y
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class AnchorBorderPosition(enum.Enum):
    """anchor border positions
    """
    eBorderBottom = 2
    eBorderHorizontal = 3
    eBorderInnerBottom = 4098
    eBorderInnerHorizontal = 4099
    eBorderInnerLeft = 4100
    eBorderInnerRight = 4104
    eBorderInnerTop = 4097
    eBorderInnerVertical = 4108
    eBorderLeft = 4
    eBorderRight = 8
    eBorderTop = 1
    eBorderVertical = 12
    eCornerInnerLeftBottom = 4102
    eCornerInnerLeftTop = 4101
    eCornerInnerRightBottom = 4106
    eCornerInnerRightTop = 4105
    eCornerLeftBottom = 6
    eCornerLeftTop = 5
    eCornerRightBottom = 10
    eCornerRightTop = 9

    names = {eBorderLeft: eBorderLeft,
             eBorderTop: eBorderTop,
             eBorderRight: eBorderRight,
             eBorderBottom: eBorderBottom,
             eCornerLeftTop: eCornerLeftTop,
             eCornerLeftBottom: eCornerLeftBottom,
             eCornerRightTop: eCornerRightTop,
             eCornerRightBottom: eCornerRightBottom,
             eBorderHorizontal: eBorderHorizontal,
             eBorderVertical: eBorderVertical,
             eCornerInnerLeftTop: eCornerInnerLeftTop,
             eCornerInnerLeftBottom: eCornerInnerLeftBottom,
             eCornerInnerRightTop: eCornerInnerRightTop,
             eCornerInnerRightBottom: eCornerInnerRightBottom,
             eBorderInnerTop: eBorderInnerTop,
             eBorderInnerBottom: eBorderInnerBottom,
             eBorderInnerLeft: eBorderInnerLeft,
             eBorderInnerRight: eBorderInnerRight,
             eBorderInnerHorizontal: eBorderInnerHorizontal,
             eBorderInnerVertical: eBorderInnerVertical}

    values = {4: eBorderLeft,
              1: eBorderTop,
              8: eBorderRight,
              2: eBorderBottom,
              5: eCornerLeftTop,
              6: eCornerLeftBottom,
              9: eCornerRightTop,
              10: eCornerRightBottom,
              3: eBorderHorizontal,
              12: eBorderVertical,
              4101: eCornerInnerLeftTop,
              4102: eCornerInnerLeftBottom,
              4105: eCornerInnerRightTop,
              4106: eCornerInnerRightBottom,
              4097: eBorderInnerTop,
              4098: eBorderInnerBottom,
              4100: eBorderInnerLeft,
              4104: eBorderInnerRight,
              4099: eBorderInnerHorizontal,
              4108: eBorderInnerVertical}

    def __getitem__(self, key: (str | int | float)) -> AnchorBorderPosition:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class PrecastElement(AllplanElement):

    def __init__(self, Properties: PrecastElementProperties):
        """Constructor

        Args:
            elementProp: Element properties
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Properties(self) -> None:
        """Property for Precast Element Properties
        Value type: PrecastElementProperties


        :type: None
        """
    @property
    def deletePython(self) -> None:
        """Property to delete Python after elementation
        Value type: int


        :type: None
        """

class Cell():

    @typing.overload
    def GetCell(self) -> object:
        """
        """
    @typing.overload
    def GetCell(self):
        """
        """
    def GetCell(self):
        """ Overloaded function. See individual overloads.
        """

class ClippingPathProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def ClippingLineFull(self) -> :
        """
        """
    @property
    def ClippingLineSegmentLength(self) -> :
        """
        """
    @property
    def ClippingPathLineColor(self) -> :
        """
        """
    @property
    def ClippingPathLineEndSymbolHeight(self) -> :
        """
        """
    @property
    def ClippingPathLineEndSymbolNr(self) -> :
        """
        """
    @property
    def ClippingPathLineEndSymbolOn(self) -> :
        """
        """
    @property
    def ClippingPathLineSymbolHeight(self) -> :
        """
        """
    @property
    def ClippingPathLineSymbolNr(self) -> :
        """
        """
    @property
    def ClippingPathLineSymbolOn(self) -> :
        """
        """
    @property
    def ClippingPathLineType(self) -> :
        """
        """
    @property
    def ClippingPathPen(self) -> :
        """
        """
    @property
    def EndTextProps(self) -> :
        """
        """
    @property
    def PlaceClippingLine(self) -> :
        """
        """
    @property
    def SectionsToShow(self) -> :
        """
        """
    @property
    def StartTextProps(self) -> :
        """
        """

class Direction(enum.Enum):
    """directions for views
    """
    eDirectionI = 1
    eDirectionII = 2
    eDirectionIII = 3
    eDirectionIV = 4
    eDirectionV = 5
    eDirectionVI = 6

    names = {eDirectionI: eDirectionI,
             eDirectionII: eDirectionII,
             eDirectionIII: eDirectionIII,
             eDirectionIV: eDirectionIV,
             eDirectionV: eDirectionV,
             eDirectionVI: eDirectionVI}

    values = {1: eDirectionI,
              2: eDirectionII,
              3: eDirectionIII,
              4: eDirectionIV,
              5: eDirectionV,
              6: eDirectionVI}

    def __getitem__(self, key: (str | int | float)) -> Direction:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class DirectionMode(enum.Enum):
    """mode for directions
    """
    eFull = 1
    eRestricted = 0

    names = {eRestricted: eRestricted,
             eFull: eFull}

    values = {0: eRestricted,
              1: eFull}

    def __getitem__(self, key: (str | int | float)) -> DirectionMode:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class DirectionProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def CutPosition(self) -> :
        """
        """
    @property
    def CutWidth(self) -> :
        """
        """
    @property
    def Mode(self) -> :
        """
        """

class FileEntryPath(enum.Enum):
    """paths
    """
    eFileEntryPathLibrary = 5
    eFileEntryPathOffice = 1
    eFileEntryPathPrivate = 2
    eFileEntryPathProject = 3
    eFileEntryPathProjectPlus = 4
    eFileEntryPathStandard = 0

    names = {eFileEntryPathStandard: eFileEntryPathStandard,
             eFileEntryPathOffice: eFileEntryPathOffice,
             eFileEntryPathPrivate: eFileEntryPathPrivate,
             eFileEntryPathProject: eFileEntryPathProject,
             eFileEntryPathProjectPlus: eFileEntryPathProjectPlus,
             eFileEntryPathLibrary: eFileEntryPathLibrary}

    values = {0: eFileEntryPathStandard,
              1: eFileEntryPathOffice,
              2: eFileEntryPathPrivate,
              3: eFileEntryPathProject,
              4: eFileEntryPathProjectPlus,
              5: eFileEntryPathLibrary}

    def __getitem__(self, key: (str | int | float)) -> FileEntryPath:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class FinishProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def ApplySurfaceElemToFinishSurfaces(self) -> :
        """
        """
    @property
    def FinishLinesColor(self) -> :
        """
        """
    @property
    def FinishLinesLayer(self) -> :
        """
        """
    @property
    def FinishLinesLineType(self) -> :
        """
        """
    @property
    def FinishLinesPen(self) -> :
        """
        """
    @property
    def IsFinishLinesColorFromLayer(self) -> :
        """
        """
    @property
    def IsFinishLinesLineTypeFromLayer(self) -> :
        """
        """
    @property
    def IsFinishLinesPenFromLayer(self) -> :
        """
        """
    @property
    def ShowCeilingSurfaces(self) -> :
        """
        """
    @property
    def ShowEntireStructOnly(self) -> :
        """
        """
    @property
    def ShowFloorSurfaces(self) -> :
        """
        """
    @property
    def ShowVerticalSurfaces(self) -> :
        """
        """

class FixtureCombinationType(enum.Enum):
    """Fixture combination types
    """
    eVx = 1
    eVy = 2
    eVz = 3

    names = {eVx: eVx,
             eVy: eVy,
             eVz: eVz}

    values = {1: eVx,
              2: eVy,
              3: eVz}

    def __getitem__(self, key: (str | int | float)) -> FixtureCombinationType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class FixtureElement(PrecastElement, AllplanElement):
    """FixtureElement class
    """
    def GetFixtureProperties(self) -> FixtureProperties:
        """Get the Fixture properties

        Returns:
             Fixture properties
        """
    def GetHash(self) -> str:
        """Get the hash value

        Returns:
             Hash value
        """
    def GetSlideList(self) -> list:
        """Get the slide object list

        Returns:
             Slide object list
        """
    def SetFixtureProperties(self, fixProp: FixtureProperties):
        """Set the Fixture properties

        Args:
            fixProp: fixture properties
        """
    def SetHash(self, hash: str):
        """Set the hash value

        Args:
            hash:Hash value
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, fixProp: FixtureProperties, slideList: list):
        """Constructor

        Args:
            fixProp:        Fixture properties
            slideList:      Slide list of fixture definition
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class FixtureGroupElement(PrecastElement, AllplanElement):
    """FixtureGroupElement class
    """
    def GetFixtureGroupProperties(self) -> FixtureGroupProperties:
        """Get the FixtureGroup properties

        Returns:
             FixtureGroup properties
        """
    def GetFixtureList(self) -> list:
        """Get the fixture object list

        Returns:
             Fixture object list
        """
    def SetFixtureGroupProperties(self, FixtureGroupProp: FixtureGroupProperties):
        """Set the FixtureGroup properties

        Args:
            FixtureGroupProp: FixtureGroup properties
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, FixtureGroupProp: FixtureGroupProperties, slideList: list):
        """Constructor

        Args:
            FixtureGroupProp: FixtureGroup properties
            placementList:  Placement list of macro group
        """
    @typing.overload
    def __init__(self, commonProp: NemAll_Python_BaseElements.CommonProperties, FixtureGroupProp: FixtureGroupProperties, slideList: list):
        """Constructor

        Args:
            commonProp:     Common properties
            FixtureGroupProp: FixtureGroup properties
            placementList:  Placement list of macro group
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class FixtureGroupProperties():
    """FixtureGroupProperties class
    """
    def __eq__(self, prop: FixtureGroupProperties) -> bool:
        """equal operator

        Args:
            prop: FixtureGroupProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def LeadingPoint(self) -> None:
        """Leading point of the fixture group

        Value type: Point3D


        :type: None
        """
    @property
    def Name(self) -> None:
        """Name of the fixture group

        Value type: str


        :type: None
        """
    @property
    def Type(self) -> None:
        """Type of the fixture group
        (General|Dynamic|Cutted|Leading)
        Value type: enum


        :type: None
        """

class FixturePlacementElement(PrecastElement, AllplanElement):
    """FixturePlacementElement class
    """
    def GetFixturePlacementProperties(self) -> FixturePlacementProperties:
        """Get the MacroPlacement properties

        Returns:
             MacroPlacement properties
        """
    def GetMacro(self) -> object:
        """Get the corresponding macro definition

        Returns:
             Macro definition element
        """
    def SetFixturePlacementProperties(self, MacroPlacementProp: FixturePlacementProperties):
        """Set the MacroPlacement properties

        Args:
            MacroPlacementProp: MacroPlacement properties
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, commonProp: NemAll_Python_BaseElements.CommonProperties, macroPlacementProp: FixturePlacementProperties,
                 macro: object):
        """Constructor

        Args:
            commonProp:               Common properties
            macroPlacementProp:       MacroPlacement properties
            macro:                    Macro definition element
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class FixturePlacementProperties():
    """FixturePlacementProperties class
    """
    def __eq__(self, prop: FixturePlacementProperties) -> bool:
        """equal operator

        Args:
            prop: FixturePlacementProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def Automation(self) -> None:
        """Value type: bool


        :type: None
        """
    @property
    def ConnectionToAIACatalog(self) -> None:
        """Enable connection to the Precast Fixture catalog of the Fixture placement element

        Value type: bool


        :type: None
        """
    @property
    def ConnectionToAllplanCatalog(self) -> None:
        """Enable connection to the Allplan Catalog of the Fixture placement element

        Value type: bool


        :type: None
        """
    @property
    def CountOfQuestions(self) -> None:
        """Number of active question attributes of the Fixture placement element

        Value type: int


        :type: None
        """
    @property
    def DistortionState(self) -> None:
        """Value type: bool


        :type: None
        """
    @property
    def DomainType(self) -> None:
        """Domaintype of the Fixture placement element

        Value type: None


        :type: None
        """
    @property
    def EnableQuestions(self) -> None:
        """Enables the question attributes of the Fixture placement element

        Value type: bool


        :type: None
        """
    @property
    def HasParentModificationBehaviour(self) -> None:
        """Property for specific behavior for modification state
        Value type: bool


        :type: None
        """
    @property
    def HeightDefinitionType(self) -> HeightDefinitionType:
        """Get the Height definition type
        """
    @HeightDefinitionType.setter
    def HeightDefinitionType(self, value: HeightDefinitionType) -> None:
        """Set the Height definition type
        """
    @property
    def HollowShaft(self) -> None:
        """Value type: bool


        :type: None
        """
    @property
    def Mass_V6(self) -> None:
        """Value type: float


        :type: None
        """
    @property
    def Mass_V7(self) -> None:
        """Value type: float


        :type: None
        """
    @property
    def Mass_V8(self) -> None:
        """Value type: float


        :type: None
        """
    @property
    def Mass_V9(self) -> None:
        """Value type: float


        :type: None
        """
    @property
    def Matrix(self) -> NemAll_Python_Geometry.Matrix3D:
        """Get the Matrix for location in world coordinate system
        """
    @Matrix.setter
    def Matrix(self, value: NemAll_Python_Geometry.Matrix3D) -> None:
        """Set the Matrix for location in world coordinate system
        """
    @property
    def MirrorState(self) -> None:
        """Property for the fixture placement mirrored state
        Value type: bool


        :type: None
        """
    @property
    def Name(self) -> None:
        """Name of the Fixture placement element

        Value type: str


        :type: None
        """
    @property
    def OutlineShape(self) -> None:
        """Value type: OutlineShape


        :type: None
        """
    @property
    def OutlineType(self) -> None:
        """Value type: OutlineType


        :type: None
        """
    @property
    def OutlineTypeInGroup(self) -> None:
        """Value type: OutlineTypeInGroup


        :type: None
        """
    @property
    def PositionNr(self) -> None:
        """Value type: int


        :type: None
        """
    @property
    def ProfilType(self) -> None:
        """Value type: ProfilType


        :type: None
        """
    @property
    def SubType(self) -> None:
        """SubType of the Fixture placement element

        Value type: MacroSubType


        :type: None
        """
    @property
    def Type(self) -> None:
        """Type of the Fixture placement element

        Value type: MacroType


        :type: None
        """
    @property
    def UnitFactor(self) -> None:
        """Value type: int


        :type: None
        """
    @property
    def UseAlways2DRepInGroundView(self) -> None:
        """Value type: bool


        :type: None
        """
    @property
    def UseDrawOrder(self) -> bool:
        """Get the Uses the draw order setting of the placement or the elements of the Fixture ?
        """
    @UseDrawOrder.setter
    def UseDrawOrder(self, value: bool) -> None:
        """Set the Uses the draw order setting of the placement or the elements of the Fixture ?
        """
    @property
    def UseFormat(self) -> bool:
        """Get the Uses the format setting (pen, stroke, color) of the placement or the elements of the Fixture ?
        """
    @UseFormat.setter
    def UseFormat(self, value: bool) -> None:
        """Set the Uses the format setting (pen, stroke, color) of the placement or the elements of the Fixture ?
        """
    @property
    def Visibility(self) -> None:
        """Value type: bool


        :type: None
        """

class FixtureProperties():
    """FixtureProperties class
    """
    def __eq__(self, prop: FixtureProperties) -> bool:
        """equal operator

        Args:
            prop: FixtureProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def CatalogName(self) -> None:
        """Value type: str


        :type: None
        """
    @property
    def DomainType(self) -> None:
        """Domaintype of the Fixture element

        Value type: None


        :type: None
        """
    @property
    def InsertionPoint(self) -> None:
        """Value type: Point3D


        :type: None
        """
    @property
    def IsScaleDependent(self) -> None:
        """Value type: bool


        :type: None
        """
    @property
    def Name(self) -> None:
        """Value type: str


        :type: None
        """
    @property
    def PositionNr(self) -> None:
        """Value type: int


        :type: None
        """
    @property
    def SubType(self) -> None:
        """SubType of the Fixture element

        Value type: MacroSubType


        :type: None
        """
    @property
    def Type(self) -> None:
        """Type of the Fixture element

        Value type: MacroType


        :type: None
        """
    @property
    def UnitFactor(self) -> None:
        """Value type: int


        :type: None
        """

class FixtureSlideElement(PrecastElement, AllplanElement):
    """FixtureSlideElement class
    """
    def GetFixtureSlideProperties(self) -> FixtureSlideProperties:
        """Get the FixtureSlide properties

        Returns:
             FixtureSlide properties
        """
    def GetObjectList(self) -> list:
        """Get the slide object list

        Returns:
             Slide object list
        """
    def SetFixtureSlideProperties(self, FixtureSlideProp: FixtureSlideProperties):
        """Set the FixtureSlide properties

        Args:
            FixtureSlideProp: FixtureSlide properties
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, FixtureSlideProp: FixtureSlideProperties, objectList: list):
        """Constructor

        Args:
            FixtureSlideProp: FixtureSlide properties
            objectList:     Object list of slide
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class FixtureSlideProperties():
    """FixtureSlideProperties class
    """
    def __eq__(self, prop: FixtureSlideProperties) -> bool:
        """equal operator

        Args:
            prop: FixtureSlideProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def EndScaleRange(self) -> None:
        """Property for end reference scale of slide
        Value type: float


        :type: None
        """
    @property
    def OffsetOfReferencePoint1(self) -> None:
        """Property for first offset value to reference point
        Value type: Vector3D


        :type: None
        """
    @property
    def OffsetOfReferencePoint2(self) -> None:
        """Property for second offset value to reference point
        Value type: Vector3D


        :type: None
        """
    @property
    def ReferencePoint(self) -> None:
        """Property for reference point
        Value type: Point3D


        :type: None
        """
    @property
    def ResizeSettingVx(self) -> None:
        """Property for resize setting for x direction
        Value type: eCombinationType


        :type: None
        """
    @property
    def ResizeSettingVy(self) -> None:
        """Property for resize setting for y direction
        Value type: eCombinationType


        :type: None
        """
    @property
    def ResizeSettingVz(self) -> None:
        """Property for resize setting for z direction
        Value type: eCombinationType


        :type: None
        """
    @property
    def StartScaleRange(self) -> None:
        """Property for start reference scale of slide
        Value type: float


        :type: None
        """
    @property
    def Type(self) -> None:
        """Property for type of slide
        Value type: eSlideType


        :type: None
        """
    @property
    def ViewType(self) -> None:
        """Property for view type of slide
        Value type: eSlideViewType


        :type: None
        """
    @property
    def VisibilityGeo2D(self) -> None:
        """Property for geometry 2D visibility of slide
        Value type: bool


        :type: None
        """
    @property
    def VisibilityGeo3D(self) -> None:
        """Property for geometry 3D visibility of slide
        Value type: bool


        :type: None
        """
    @property
    def VisibilityLayerA(self) -> None:
        """Property for layer A visibility of slide
        Value type: bool


        :type: None
        """
    @property
    def VisibilityLayerB(self) -> None:
        """Property for layer B visibility of slide
        Value type: bool


        :type: None
        """
    @property
    def VisibilityLayerC(self) -> None:
        """Property for layer C visibility of slide
        Value type: bool


        :type: None
        """

class FixtureSlideType(enum.Enum):
    """fixture slide types
    """
    eCode = 1
    eExtension = 5
    eGeometry = 0
    eReinforcement = 2
    eReport = 3
    eUndergroundCadaster = 4

    names = {eGeometry: eGeometry,
             eCode: eCode,
             eReinforcement: eReinforcement,
             eReport: eReport,
             eUndergroundCadaster: eUndergroundCadaster,
             eExtension: eExtension}

    values = {0: eGeometry,
              1: eCode,
              2: eReinforcement,
              3: eReport,
              4: eUndergroundCadaster,
              5: eExtension}

    def __getitem__(self, key: (str | int | float)) -> FixtureSlideType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class FixtureSlideViewType(enum.Enum):
    """Fixture slide view types
    """
    e2D_BACK_VIEW = 6
    e2D_FRONT_VIEW = 5
    e2D_LEFT_VIEW = 3
    e2D_NO_VIEW = 0
    e2D_RIGHT_VIEW = 4
    e2D_SYMBOL = 11
    e2D_TOP_VIEW = 1
    e3D_VIEW = 7
    e3D_VIEW_OLD = 8
    e3D_VIEW_OUTLINE_AREA = 10
    e3D_VIEW_OUTLINE_AREA_ACTUAL = 12
    e3D_VIEW_OUTLINE_VOLUME = 9
    eBOTTOM_VIEW = 2
    eCONNECTION_POINT = 20
    eCONTOUR_CUT = 18
    eLOCK_FIXED = 14
    eLOCK_FIXED_P1 = 16
    eLOCK_UML = 15
    eMEASURE_POINTS = 19
    eORGA_ORIGINAL = 17
    eTGA_ADAPTER = 13

    names = {e2D_NO_VIEW: e2D_NO_VIEW,
             e2D_TOP_VIEW: e2D_TOP_VIEW,
             eBOTTOM_VIEW: eBOTTOM_VIEW,
             e2D_LEFT_VIEW: e2D_LEFT_VIEW,
             e2D_RIGHT_VIEW: e2D_RIGHT_VIEW,
             e2D_FRONT_VIEW: e2D_FRONT_VIEW,
             e2D_BACK_VIEW: e2D_BACK_VIEW,
             e3D_VIEW: e3D_VIEW,
             e3D_VIEW_OLD: e3D_VIEW_OLD,
             e3D_VIEW_OUTLINE_VOLUME: e3D_VIEW_OUTLINE_VOLUME,
             e3D_VIEW_OUTLINE_AREA: e3D_VIEW_OUTLINE_AREA,
             e2D_SYMBOL: e2D_SYMBOL,
             e3D_VIEW_OUTLINE_AREA_ACTUAL: e3D_VIEW_OUTLINE_AREA_ACTUAL,
             eTGA_ADAPTER: eTGA_ADAPTER,
             eLOCK_FIXED: eLOCK_FIXED,
             eLOCK_UML: eLOCK_UML,
             eLOCK_FIXED_P1: eLOCK_FIXED_P1,
             eORGA_ORIGINAL: eORGA_ORIGINAL,
             eCONTOUR_CUT: eCONTOUR_CUT,
             eMEASURE_POINTS: eMEASURE_POINTS,
             eCONNECTION_POINT: eCONNECTION_POINT}

    values = {0: e2D_NO_VIEW,
              1: e2D_TOP_VIEW,
              2: eBOTTOM_VIEW,
              3: e2D_LEFT_VIEW,
              4: e2D_RIGHT_VIEW,
              5: e2D_FRONT_VIEW,
              6: e2D_BACK_VIEW,
              7: e3D_VIEW,
              8: e3D_VIEW_OLD,
              9: e3D_VIEW_OUTLINE_VOLUME,
              10: e3D_VIEW_OUTLINE_AREA,
              11: e2D_SYMBOL,
              12: e3D_VIEW_OUTLINE_AREA_ACTUAL,
              13: eTGA_ADAPTER,
              14: eLOCK_FIXED,
              15: eLOCK_UML,
              16: eLOCK_FIXED_P1,
              17: eORGA_ORIGINAL,
              18: eCONTOUR_CUT,
              19: eMEASURE_POINTS,
              20: eCONNECTION_POINT}

    def __getitem__(self, key: (str | int | float)) -> FixtureSlideViewType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class FormatProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def EliminationAngle(self) -> :
        """
        """
    @property
    def EliminationOn(self) -> :
        """
        """
    @property
    def FinishedElementsProps(self) -> :
        """
        """
    @property
    def FixedAttributesForVisibleEdges(self) -> :
        """
        """
    @property
    def HiddenEdgesProps(self) -> :
        """
        """
    @property
    def IsBetweenDifferentSurfacesOn(self) -> :
        """
        """
    @property
    def SetIsSurfaceFromObjectOn(self) -> :
        """
        """
    @property
    def ShowHiddenEdges(self) -> :
        """
        """
    @property
    def ShowVisibleEdges(self) -> :
        """
        """
    @property
    def VisibleEdgesProps(self) -> :
        """
        """

class HeadingProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def AdditionalText(self) -> :
        """
        """
    @property
    def IsOn(self) -> :
        """
        """
    @property
    def ProjectionOn(self) -> :
        """
        """
    @property
    def TextParams(self) -> :
        """
        """

class HeightDefinitionType(enum.Enum):
    """Height definition types
    """
    eAverage = 3
    eComponent = 2
    eMacro = 1
    eNone = 0

    names = {eNone: eNone,
             eMacro: eMacro,
             eComponent: eComponent,
             eAverage: eAverage}

    values = {0: eNone,
              1: eMacro,
              2: eComponent,
              3: eAverage}

    def __getitem__(self, key: (str | int | float)) -> HeightDefinitionType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class LabelStyle(Cell):

    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, labelStyleProps: LabelStyleProperties,
                 allowOverlapping: bool):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            LabelStyleProperties
            AllowOverlapping
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, labelStyleProps: LabelStyleProperties,
                 allowOverlapping: bool, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            LabelStyleProperties
            AllowOverlapping
            ConditionTemplate
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class LabelStyleProperties():

    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, fileEntryPath: FileEntryPath, fileNr: int, entryNr: int):
        """Constructor

        Args:
            EFileEntryPath
            FileNr
            EntryNr
        """
    @typing.overload
    def __init__(self, fileEntryPath: FileEntryPath, fileNr: int, entryNr: int, location: Location):
        """Constructor

        Args:
            EFileEntryPath
            FileNr
            EntryNr
            Location
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def EntryNr(self) -> None:
        """Entry number of labelStyle props

        Value type: int


        :type: None
        """
    @property
    def FileEntrPath(self) -> None:
        """File entry path of labelStyle props

        Value type: EFileEntryPath enum


        :type: None
        """
    @property
    def FileNr(self) -> None:
        """File number of labelStyle props

        Value type: int


        :type: None
        """
    @property
    def Location(self) -> None:
        """Location of labelStyle props

        Value type: Location enum


        :type: None
        """

class LabelingProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def HeadingProps(self) -> :
        """
        """
    @property
    def LineSpacing(self) -> :
        """
        """
    @property
    def OffsetFromView(self) -> :
        """
        """
    @property
    def Position(self) -> :
        """
        """
    @property
    def PrecastProps(self) -> :
        """
        """
    @property
    def ScaleProps(self) -> :
        """
        """

class Legend(Cell):

    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, legendProps: LegendProperties):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            LegendProperties
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, legendProps: LegendProperties,
                 conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            LegendProperties
            ConditionTemplate
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class LegendProperties():

    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, fileEntryPath: FileEntryPath, fileNr: int, entryNr: int, maxHeight: float, maxWidth: float):
        """Constructor

        Args:
            EFileEntryPath
            FileNr
            EntryNr
            MaxHeight
            MaxWidth
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def EntryNr(self) -> None:
        """Entry number of legend props

        Value type: int


        :type: None
        """
    @property
    def FileEntrPath(self) -> None:
        """File entry path of legend props

        Value type: EFileEntryPath enum


        :type: None
        """
    @property
    def FileNr(self) -> None:
        """File number of legend props

        Value type: int


        :type: None
        """
    @property
    def MaxHeight(self) -> None:
        """Max height of legend props

        Value type: double


        :type: None
        """
    @property
    def MaxWidth(self) -> None:
        """Max width of legend props

        Value type: double


        :type: None
        """

class LightProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def AmbientLightIntensity(self) -> :
        """
        """
    @property
    def ConsiderLight(self) -> :
        """
        """
    @property
    def IsShadowsOn(self) -> :
        """
        """
    @property
    def LightElevationAngle(self) -> :
        """
        """
    @property
    def LightIncidenceAngle(self) -> :
        """
        """
    @property
    def LightIntensity(self) -> :
        """
        """

class LineProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def Color(self) -> :
        """
        """
    @property
    def Hatch(self) -> :
        """
        """
    @property
    def Thickness(self) -> :
        """
        """
    @property
    def Type(self) -> :
        """
        """

class Location(enum.Enum):
    """locations
    """
    eLeftBottom = 1
    eLeftTop = 3
    eRightBottom = 0
    eRightTop = 2

    names = {eRightBottom: eRightBottom,
             eLeftBottom: eLeftBottom,
             eRightTop: eRightTop,
             eLeftTop: eLeftTop}

    values = {0: eRightBottom,
              1: eLeftBottom,
              2: eRightTop,
              3: eLeftTop}

    def __getitem__(self, key: (str | int | float)) -> Location:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class MacroGroupType(enum.Enum):
    """types
    """
    eGroupType_CuttedGroup = 2
    eGroupType_DynamicGroup = 1
    eGroupType_GeneralGroup = 0
    eGroupType_LeadingGroup = 3

    names = {eGroupType_GeneralGroup: eGroupType_GeneralGroup,
             eGroupType_DynamicGroup: eGroupType_DynamicGroup,
             eGroupType_CuttedGroup: eGroupType_CuttedGroup,
             eGroupType_LeadingGroup: eGroupType_LeadingGroup}

    values = {0: eGroupType_GeneralGroup,
              1: eGroupType_DynamicGroup,
              2: eGroupType_CuttedGroup,
              3: eGroupType_LeadingGroup}

    def __getitem__(self, key: (str | int | float)) -> MacroGroupType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class MacroSubType(enum.Enum):
    """Sub types
    """
    eAnchorPlate = 13
    eAnchorage = 12
    eBarAccessory = 50
    eBarCoupler = 47
    eBarNut = 48
    eBarThread = 49
    eBracingElement = 44
    eCatchmentArea = 41
    eChannel = 54
    eCirculationLoadPoint = 80
    eCirculationPipeAdapter = 81
    eCirculationStartPoint = 79
    eConcreteArea = 83
    eConcreteBeam = 46
    eConcreteBlock = 45
    eConnectionModeller = 24
    eConnectionWallColumn = 93
    eConnectorEBT = 88
    eConstPrefabConnection = 60
    eCorbel = 10
    eCoverMountingAngle = 53
    eCrossRib = 82
    eElectricalBIE = 67
    eElectricalLamp = 68
    eElectricalRoute = 69
    eFacility = 32
    eFalseJoint = 55
    eFill = 29
    eFrame = 9
    eHeatingLoadPoint = 71
    eHeatingPipeAdapter = 72
    eHeatingStartPoint = 70
    eHollowBody = 25
    eInsertion = 35
    eInsulationArea = 85
    eInsulationElement = 90
    eInsulationStripe = 89
    eJointLength = 22
    eJointReinforcement = 28
    eLinePointPlacement = 58
    eLoadCut = 19
    eMultiLine3D = 42
    eNailer = 92
    eNode = 39
    eOverrule = 86
    ePipe = 30
    ePipePoint = 31
    ePlacingLoop = 26
    ePolyline = 1
    ePrefabConnection = 37
    ePrefabConnectionCorner = 38
    ePrefabModeller = 23
    eProfileEdge = 21
    eReinforcement_Cage = 87
    eRevealAnchor = 8
    eRevealAnchorVirtual = 20
    eRibBody = 59
    eRingBeam = 6
    eRoofLine = 3
    eRoofParapetLine = 4
    eRoofParapetSupport = 5
    eRope = 40
    eSTD_Formwork = 94
    eSanitationLoadPoint = 77
    eSanitationPipeAdapter = 78
    eSanitationStartPoint = 76
    eSecondaryReinf = 27
    eSewageLoadPoint = 65
    eSewageNetElement = 52
    eSewagePipeAdapter = 66
    eSewageStartPoint = 64
    eShaft = 33
    eSlidingRestraint = 7
    eSolidStrip = 56
    eSpecialBuilding = 34
    eSpecialLoad_Undefined = 17
    eSpecialLoad_X = 14
    eSpecialLoad_Y = 15
    eSpecialLoad_Z = 16
    eSphere = 63
    eSteelProfile = 43
    eStripCorbel = 57
    eStructuralRecessFaceSupport = 62
    eStructuralRecessLongitudinalSupport = 61
    eSurface = 51
    eTieBar = 11
    eTileArea = 91
    eTileElement = 84
    eTrimmer = 18
    eUseNoSpecialSubType = 0
    eUseSameSubType = -1
    eVentilationDuctAdapter = 75
    eVentilationLoadPoint = 74
    eVentilationStartPoint = 73
    eZone = 36

    names = {eUseSameSubType: eUseSameSubType,
             eUseNoSpecialSubType: eUseNoSpecialSubType,
             ePolyline: ePolyline,
             eRoofLine: eRoofLine,
             eRoofParapetLine: eRoofParapetLine,
             eRoofParapetSupport: eRoofParapetSupport,
             eRingBeam: eRingBeam,
             eSlidingRestraint: eSlidingRestraint,
             eRevealAnchor: eRevealAnchor,
             eFrame: eFrame,
             eCorbel: eCorbel,
             eTieBar: eTieBar,
             eAnchorage: eAnchorage,
             eAnchorPlate: eAnchorPlate,
             eSpecialLoad_X: eSpecialLoad_X,
             eSpecialLoad_Y: eSpecialLoad_Y,
             eSpecialLoad_Z: eSpecialLoad_Z,
             eSpecialLoad_Undefined: eSpecialLoad_Undefined,
             eTrimmer: eTrimmer,
             eLoadCut: eLoadCut,
             eRevealAnchorVirtual: eRevealAnchorVirtual,
             eProfileEdge: eProfileEdge,
             eJointLength: eJointLength,
             ePrefabModeller: ePrefabModeller,
             eConnectionModeller: eConnectionModeller,
             eHollowBody: eHollowBody,
             ePlacingLoop: ePlacingLoop,
             eSecondaryReinf: eSecondaryReinf,
             eJointReinforcement: eJointReinforcement,
             eFill: eFill,
             ePipe: ePipe,
             ePipePoint: ePipePoint,
             eFacility: eFacility,
             eShaft: eShaft,
             eSpecialBuilding: eSpecialBuilding,
             eInsertion: eInsertion,
             eZone: eZone,
             ePrefabConnection: ePrefabConnection,
             ePrefabConnectionCorner: ePrefabConnectionCorner,
             eNode: eNode,
             eRope: eRope,
             eCatchmentArea: eCatchmentArea,
             eMultiLine3D: eMultiLine3D,
             eSteelProfile: eSteelProfile,
             eBracingElement: eBracingElement,
             eConcreteBlock: eConcreteBlock,
             eConcreteBeam: eConcreteBeam,
             eBarCoupler: eBarCoupler,
             eBarNut: eBarNut,
             eBarThread: eBarThread,
             eBarAccessory: eBarAccessory,
             eSurface: eSurface,
             eSewageNetElement: eSewageNetElement,
             eCoverMountingAngle: eCoverMountingAngle,
             eChannel: eChannel,
             eFalseJoint: eFalseJoint,
             eSolidStrip: eSolidStrip,
             eStripCorbel: eStripCorbel,
             eLinePointPlacement: eLinePointPlacement,
             eRibBody: eRibBody,
             eConstPrefabConnection: eConstPrefabConnection,
             eStructuralRecessLongitudinalSupport: eStructuralRecessLongitudinalSupport,
             eStructuralRecessFaceSupport: eStructuralRecessFaceSupport,
             eSphere: eSphere,
             eSewageStartPoint: eSewageStartPoint,
             eSewageLoadPoint: eSewageLoadPoint,
             eSewagePipeAdapter: eSewagePipeAdapter,
             eElectricalBIE: eElectricalBIE,
             eElectricalLamp: eElectricalLamp,
             eElectricalRoute: eElectricalRoute,
             eHeatingStartPoint: eHeatingStartPoint,
             eHeatingLoadPoint: eHeatingLoadPoint,
             eHeatingPipeAdapter: eHeatingPipeAdapter,
             eVentilationStartPoint: eVentilationStartPoint,
             eVentilationLoadPoint: eVentilationLoadPoint,
             eVentilationDuctAdapter: eVentilationDuctAdapter,
             eSanitationStartPoint: eSanitationStartPoint,
             eSanitationLoadPoint: eSanitationLoadPoint,
             eSanitationPipeAdapter: eSanitationPipeAdapter,
             eCirculationStartPoint: eCirculationStartPoint,
             eCirculationLoadPoint: eCirculationLoadPoint,
             eCirculationPipeAdapter: eCirculationPipeAdapter,
             eCrossRib: eCrossRib,
             eConcreteArea: eConcreteArea,
             eTileElement: eTileElement,
             eInsulationArea: eInsulationArea,
             eOverrule: eOverrule,
             eReinforcement_Cage: eReinforcement_Cage,
             eConnectorEBT: eConnectorEBT,
             eInsulationStripe: eInsulationStripe,
             eInsulationElement: eInsulationElement,
             eTileArea: eTileArea,
             eNailer: eNailer,
             eConnectionWallColumn: eConnectionWallColumn,
             eSTD_Formwork: eSTD_Formwork}

    values = {-1: eUseSameSubType,
              0: eUseNoSpecialSubType,
              1: ePolyline,
              3: eRoofLine,
              4: eRoofParapetLine,
              5: eRoofParapetSupport,
              6: eRingBeam,
              7: eSlidingRestraint,
              8: eRevealAnchor,
              9: eFrame,
              10: eCorbel,
              11: eTieBar,
              12: eAnchorage,
              13: eAnchorPlate,
              14: eSpecialLoad_X,
              15: eSpecialLoad_Y,
              16: eSpecialLoad_Z,
              17: eSpecialLoad_Undefined,
              18: eTrimmer,
              19: eLoadCut,
              20: eRevealAnchorVirtual,
              21: eProfileEdge,
              22: eJointLength,
              23: ePrefabModeller,
              24: eConnectionModeller,
              25: eHollowBody,
              26: ePlacingLoop,
              27: eSecondaryReinf,
              28: eJointReinforcement,
              29: eFill,
              30: ePipe,
              31: ePipePoint,
              32: eFacility,
              33: eShaft,
              34: eSpecialBuilding,
              35: eInsertion,
              36: eZone,
              37: ePrefabConnection,
              38: ePrefabConnectionCorner,
              39: eNode,
              40: eRope,
              41: eCatchmentArea,
              42: eMultiLine3D,
              43: eSteelProfile,
              44: eBracingElement,
              45: eConcreteBlock,
              46: eConcreteBeam,
              47: eBarCoupler,
              48: eBarNut,
              49: eBarThread,
              50: eBarAccessory,
              51: eSurface,
              52: eSewageNetElement,
              53: eCoverMountingAngle,
              54: eChannel,
              55: eFalseJoint,
              56: eSolidStrip,
              57: eStripCorbel,
              58: eLinePointPlacement,
              59: eRibBody,
              60: eConstPrefabConnection,
              61: eStructuralRecessLongitudinalSupport,
              62: eStructuralRecessFaceSupport,
              63: eSphere,
              64: eSewageStartPoint,
              65: eSewageLoadPoint,
              66: eSewagePipeAdapter,
              67: eElectricalBIE,
              68: eElectricalLamp,
              69: eElectricalRoute,
              70: eHeatingStartPoint,
              71: eHeatingLoadPoint,
              72: eHeatingPipeAdapter,
              73: eVentilationStartPoint,
              74: eVentilationLoadPoint,
              75: eVentilationDuctAdapter,
              76: eSanitationStartPoint,
              77: eSanitationLoadPoint,
              78: eSanitationPipeAdapter,
              79: eCirculationStartPoint,
              80: eCirculationLoadPoint,
              81: eCirculationPipeAdapter,
              82: eCrossRib,
              83: eConcreteArea,
              84: eTileElement,
              85: eInsulationArea,
              86: eOverrule,
              87: eReinforcement_Cage,
              88: eConnectorEBT,
              89: eInsulationStripe,
              90: eInsulationElement,
              91: eTileArea,
              92: eNailer,
              93: eConnectionWallColumn,
              94: eSTD_Formwork}

    def __getitem__(self, key: (str | int | float)) -> MacroSubType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class MacroType(enum.Enum):
    """types
    """
    eGroup_Fixture = 3
    eLine_Fixture = 1
    ePlane_Fixture = 2
    ePoint_Fixture = 0
    eUseSameType = -1

    names = {eUseSameType: eUseSameType,
             ePoint_Fixture: ePoint_Fixture,
             eLine_Fixture: eLine_Fixture,
             ePlane_Fixture: ePlane_Fixture,
             eGroup_Fixture: eGroup_Fixture}

    values = {-1: eUseSameType,
              0: ePoint_Fixture,
              1: eLine_Fixture,
              2: ePlane_Fixture,
              3: eGroup_Fixture}

    def __getitem__(self, key: (str | int | float)) -> MacroType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class OutlineShape(enum.Enum):
    """ outline shapes
    """
    eBUILTIN_OUTLINE_SHAPE_NOTHING = 0
    eBUILTIN_OUTLINE_SHAPE_RECTANGLE = 1
    eBUILTIN_OUTLINE_SHAPE_SYMBOL = 3
    eBUILTIN_OUTLINE_SHAPE_TRAPEZOID = 2

    names = {eBUILTIN_OUTLINE_SHAPE_NOTHING: eBUILTIN_OUTLINE_SHAPE_NOTHING,
             eBUILTIN_OUTLINE_SHAPE_RECTANGLE: eBUILTIN_OUTLINE_SHAPE_RECTANGLE,
             eBUILTIN_OUTLINE_SHAPE_TRAPEZOID: eBUILTIN_OUTLINE_SHAPE_TRAPEZOID,
             eBUILTIN_OUTLINE_SHAPE_SYMBOL: eBUILTIN_OUTLINE_SHAPE_SYMBOL}

    values = {0: eBUILTIN_OUTLINE_SHAPE_NOTHING,
              1: eBUILTIN_OUTLINE_SHAPE_RECTANGLE,
              2: eBUILTIN_OUTLINE_SHAPE_TRAPEZOID,
              3: eBUILTIN_OUTLINE_SHAPE_SYMBOL}

    def __getitem__(self, key: (str | int | float)) -> OutlineShape:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class OutlineType(enum.Enum):
    """ outline types
    """
    eBUILTIN_OUTLINE_TYPE_MINUS = 2
    eBUILTIN_OUTLINE_TYPE_NOTHING = 0
    eBUILTIN_OUTLINE_TYPE_NO_AFFECT = 3
    eBUILTIN_OUTLINE_TYPE_PLUS = 1

    names = {eBUILTIN_OUTLINE_TYPE_NOTHING: eBUILTIN_OUTLINE_TYPE_NOTHING,
             eBUILTIN_OUTLINE_TYPE_PLUS: eBUILTIN_OUTLINE_TYPE_PLUS,
             eBUILTIN_OUTLINE_TYPE_MINUS: eBUILTIN_OUTLINE_TYPE_MINUS,
             eBUILTIN_OUTLINE_TYPE_NO_AFFECT: eBUILTIN_OUTLINE_TYPE_NO_AFFECT}

    values = {0: eBUILTIN_OUTLINE_TYPE_NOTHING,
              1: eBUILTIN_OUTLINE_TYPE_PLUS,
              2: eBUILTIN_OUTLINE_TYPE_MINUS,
              3: eBUILTIN_OUTLINE_TYPE_NO_AFFECT}

    def __getitem__(self, key: (str | int | float)) -> OutlineType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class OutlineTypeInGroup(enum.Enum):
    """ outline types in group
    """
    eBUILTIN_OUTLINE_TYPE_IN_GROUP_MINUS = 2
    eBUILTIN_OUTLINE_TYPE_IN_GROUP_NOTHING = 0
    eBUILTIN_OUTLINE_TYPE_IN_GROUP_PLUS = 1

    names = {eBUILTIN_OUTLINE_TYPE_IN_GROUP_NOTHING: eBUILTIN_OUTLINE_TYPE_IN_GROUP_NOTHING,
             eBUILTIN_OUTLINE_TYPE_IN_GROUP_PLUS: eBUILTIN_OUTLINE_TYPE_IN_GROUP_PLUS,
             eBUILTIN_OUTLINE_TYPE_IN_GROUP_MINUS: eBUILTIN_OUTLINE_TYPE_IN_GROUP_MINUS}

    values = {0: eBUILTIN_OUTLINE_TYPE_IN_GROUP_NOTHING,
              1: eBUILTIN_OUTLINE_TYPE_IN_GROUP_PLUS,
              2: eBUILTIN_OUTLINE_TYPE_IN_GROUP_MINUS}

    def __getitem__(self, key: (str | int | float)) -> OutlineTypeInGroup:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class Page():

    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, anchors: list):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Anchors:BaseReferenceModelElements
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, anchors: list, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Anchors:BaseReferenceModelElements
            ConditionTemplate
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
            ConditionTemplate
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, scale: float, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Scale
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, scale: float, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Scale
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
            ConditionTemplate
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, scales: list, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Scales
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, pageNr: int, scales: list, anchors: list,
                 size: NemAll_Python_Geometry.MinMax2D, centeringCells: bool, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            PageNr
            Scales
            Anchors:BaseReferenceModelElements
            Size
            CenteringCells
            ConditionTemplate
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def add_anchor(self, anchor: Anchor):
        """Adds an anchor to the page

        Args:
            Anchor:to add
        """
    def add_anchors(self, anchors: list):
        """Adds anchors to the page

        Args:
            Anchors:to add
        """
    def add_cell(self, cell: Cell):
        """Adds a cell (labelStyle/legend/view) to the page

        Args:
            Cell:to add
        """
    @property
    def DrawingFile(self) -> None:
        """Sets the drawing file where the page should be placed

        Value type: int


        :type: None
        """

class PageProperties():
    """@brief Wrapper for page properties of elementplan
    """
    @typing.overload
    def __init__(self, label: str, sizeType: int, scaleType: int, fixedScale: float):
        """@brief Creates a helper to fill python palette for UVS Elementplan
        @param label Label of the page
        @param sizeType Size type of the page (Fixed | AutomaticSelection)
        @param scaleType Scale type of the page (ScaleAutomaticSelection | ScaleFixed | MaximumSize)
        @param fixedScale Fixed scale

        Args:
            label
            sizeType
            scaleType
            fixedScale
        """
    @typing.overload
    def __init__(self, element: PageProperties):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def FixedScale(self) -> float:
        """Get the Fixed scaleof the page
        """
    @FixedScale.setter
    def FixedScale(self, value: float) -> None:
        """Set the Fixed scaleof the page
        """
    @property
    def Label(self) -> str:
        """Get the Label of the page
        """
    @Label.setter
    def Label(self, value: str) -> None:
        """Set the Label of the page
        """
    @property
    def ScaleType(self) -> int:
        """Get the Scale type of the page
        """
    @ScaleType.setter
    def ScaleType(self, value: int) -> None:
        """Set the Scale type of the page
        """
    @property
    def SizeType(self) -> int:
        """Get the Size type of the page
        """
    @SizeType.setter
    def SizeType(self, value: int) -> None:
        """Set the Size type of the page
        """

class PagePropertiesList():
    """List for PageProperties objects
    """
    def __contains__(self, value: PageProperties) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: PageProperties):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: PagePropertiesList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> PageProperties:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> PagePropertiesList:
        """Add a list

        Args:
            eleList: PageProperties list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: PageProperties):
        """Constructor with a PageProperties

        Args:
            ele: PageProperties
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of PageProperties

        Args:
            eleList: PageProperties list
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __iter__(self) -> collections.abc.Iterator:
        """List iterator

        Returns:
            List iterator
        """
    def __len__(self) -> int:
        """Get the list length

        Returns:
            Length of the list
        """
    def __setitem__(self, index: (int | slice), value: PageProperties):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: PageProperties):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: PagePropertiesList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: PageProperties list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Plan():

    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter):
        """Constructor

        Args:
            DocumentAdapter
        """
    @typing.overload
    def __init__(self, arg2: NemAll_Python_IFW_ElementAdapter.DocumentAdapter,
                 doc: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList):
        """Constructor

        Args:
            DocumentAdapter
            BaseElementAdapterList
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def add_page(self, page: Page):
        """Adds a page to the plan

        Args:
            page:to add
        """
    @typing.overload
    def create(self, elemPlan: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter) -> bool:
        """Creates the elementplan

        Args:
            Allplan::IFW::ElementAdapter::BaseElementAdapter:-> created elementplan
        """
    @typing.overload
    def create(self, elemPlan: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter,
               baseElements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList) -> bool:
        """Creates the elementplan

        Args:
            Allplan::IFW::ElementAdapter::BaseElementAdapter:-> created elementplan
            Allplan::IFW::ElementAdapter::BaseElementAdapterList:-> elements to create
        """
    def create(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def DrawingFile(self) -> None:
        """Sets the drawing file where the elementplan should be placed

        Value type: int


        :type: None
        """
    @property
    def Offset(self) -> None:
        """Sets the offset of the plan

        Value type: Allplan::Geometry::Point2D


        :type: None
        """

class Position(enum.Enum):
    """position for labeling
    """
    eAccordingTheUSStandard = 7
    eBottomCenter = 5
    eBottomLeft = 4
    eBottomRight = 6
    eNone = 0
    eTopCenter = 2
    eTopLeft = 1
    eTopRight = 3

    names = {eNone: eNone,
             eTopLeft: eTopLeft,
             eTopCenter: eTopCenter,
             eTopRight: eTopRight,
             eBottomLeft: eBottomLeft,
             eBottomCenter: eBottomCenter,
             eBottomRight: eBottomRight,
             eAccordingTheUSStandard: eAccordingTheUSStandard}

    values = {0: eNone,
              1: eTopLeft,
              2: eTopCenter,
              3: eTopRight,
              4: eBottomLeft,
              5: eBottomCenter,
              6: eBottomRight,
              7: eAccordingTheUSStandard}

    def __getitem__(self, key: (str | int | float)) -> Position:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class AssemblyGroupElement(PrecastElement, AllplanElement):
    """AssemblyGroupElement class
    """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, name: str, number: int, LibraryElementsList: list, FixtureElementsList: list, ReinforcementList: list):
        """Constructor

        Args:
            name:      Name of the assembly group
            number:    Number of the assembly group
            LibraryElementsList:    List of library fixtures which should be included in the assembly group
            FixtureElementsList:    List of parametric fixtures which should be included in the assembly group
            ReinforcementList:      List of reinforcement placements which should be included in the assembly group
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def FixtureElementsList(self) -> None:
        """List of parametric fixtures which should be included in the assembly group
        Value type: list


        :type: None
        """
    @property
    def LibraryElementsList(self) -> None:
        """List of library fixtures which should be included in the assembly group
        Value type: list


        :type: None
        """
    @property
    def Name(self) -> None:
        """Name of the assembly group
        Value type: str


        :type: None
        """
    @property
    def Number(self) -> None:
        """Number of the assembly group
        Value type: int


        :type: None
        """
    @property
    def ReinforcementList(self) -> None:
        """List of reinforcement placements which should be included in the assembly group
        Value type: list


        :type: None
        """

class PrecastElementProperties():
    """PrecastElementProperties class
    """
    def GetPrecastElementTypeFromIdx(self, arg2: int) -> str:
        """Get the name of the PrecastElementType from Cat Idx

        Returns:
             PrecastElementType Cat Name
        """
    def SetElementTypeCatalogGUID_from_Name(self, arg2: str) -> NemAll_Python_Utility.GUID:
        """Set the elementTypeCatGUID

        Returns:
             elementTypeCatGUID
        """
    def SetFactoryCatalogAddressOffset(self, arg2: str) -> int:
        """Set the factoryCatAddressOffset

        Returns:
             factoryCatAddressOffset
        """
    def SetNormCatalogAddressOffset(self, arg2: str) -> int:
        """Set the normCatAddressOffset

        Returns:
             normCatAddressOffset
        """
    def __eq__(self, prop: PrecastElementProperties) -> bool:
        """equal operator

        Args:
            prop: PrecastElementProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def CreateLabeling(self) -> None:
        """Property for CreateLabeling
        Value type: bool


        :type: None
        """
    @property
    def DimensionCross(self) -> None:
        """Property for DimensionCross
        Value type: float


        :type: None
        """
    @property
    def DimensionSpan(self) -> None:
        """Property for DimensionSpan
        Value type: float


        :type: None
        """
    @property
    def DimensionViewing(self) -> None:
        """Property for DimensionViewing
        Value type: float


        :type: None
        """
    @property
    def ElemTypeAttribut(self) -> None:
        """Property for ElemTypeAttribut
        Value type: str


        :type: None
        """
    @property
    def ElementType(self) -> None:
        """Property for ElementType
        Value type: int


        :type: None
        """
    @property
    def ElementTypeCatGUID(self) -> None:
        """Property for ElementTypeCatGUID
        Value type: GUID


        :type: None
        """
    @property
    def Factory(self) -> None:
        """Property for Factory
        Value type: str


        :type: None
        """
    @property
    def FactoryCatAddressOffset(self) -> None:
        """Property for FactoryCatAddressOffset
        Value type: int


        :type: None
        """
    @property
    def LabelingTextRefPoint(self) -> None:
        """Property for LabelingTextRefPoint
        Value type: int


        :type: None
        """
    @property
    def Layers(self) -> None:
        """Property for Layers
        Value type: list


        :type: None
        """
    @property
    def ManualDimensions(self) -> None:
        """Property for ManualDimensions
        Value type: bool


        :type: None
        """
    @property
    def Norm(self) -> None:
        """Property for Norm
        Value type: str


        :type: None
        """
    @property
    def NormCatAddressOffset(self) -> None:
        """Property for NormCatAddressOffset
        Value type: int


        :type: None
        """
    @property
    def PieceFactor(self) -> None:
        """Property for PieceFactor
        Value type: int


        :type: None
        """
    @property
    def PosNr(self) -> None:
        """Property for PosNr
        Value type: int


        :type: None
        """
    @property
    def PosNrText(self) -> None:
        """Property for PosNrText
        Value type: str


        :type: None
        """
    @property
    def ReferencePoint(self) -> None:
        """Property for ReferencePoint
        Value type: Point3D


        :type: None
        """
    @property
    def SpanDirection(self) -> None:
        """Property for SpanDirection
        Value type: Point3D


        :type: None
        """
    @property
    def ViewDirection(self) -> None:
        """Property for ViewDirection
        Value type: Point3D


        :type: None
        """

class PrecastLayer(AllplanElement):
    """PrecastLayer class
    """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, Properties: PrecastLayerProperties):
        """Constructor

        Args:
            layerProp: Layer properties
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Properties(self) -> None:
        """Property for Properties
        Value type: PrecastLayerProperties


        :type: None
        """

class PrecastLayerProperties():
    """PrecastLayerProperties class
    """
    def SetMaterialCatalogAddressOffset(self, arg2: str, arg3: str) -> int:
        """Set the materialCatAddressOffset

        Returns:
             materialCatAddressOffset
        """
    def __eq__(self, prop: PrecastLayerProperties) -> bool:
        """equal operator

        Args:
            prop: PrecastLayerProperties to compare

        Returns:
                  true if they are equal, false otherwise
        """
    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def CalculateLayerThickness(self) -> None:
        """Property for CalculateLayerThickness
        Value type: bool


        :type: None
        """
    @property
    def LayerName(self) -> None:
        """Property for LayerName
        Value type: str


        :type: None
        """
    @property
    def LayerNumber(self) -> None:
        """Property for LayerNumber
        Value type: int


        :type: None
        """
    @property
    def LayerThickness(self) -> None:
        """Property for LayerThickness
        Value type: float


        :type: None
        """
    @property
    def Material(self) -> None:
        """Property for Material
        Value type: str


        :type: None
        """
    @property
    def MaterialCatAddressOffset(self) -> None:
        """Property for MaterialCatAddressOffset
        Value type: int


        :type: None
        """
    @property
    def MaterialType(self) -> None:
        """Property for MaterialType
        Value type: int


        :type: None
        """

class PrecastMWSElement(PrecastElement, AllplanElement):
    """PrecastMWSElement class
    """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, factory: str, name: str, number: int, piecefactor: int, longitBarHeight: int, SegmentNumber: int,
                 SegmentVector: NemAll_Python_Geometry.Point3D, SegementPointList: list, ReinforcementList: list):
        """Constructor

        Args:
            factory: factory
            name:    name of the MWS element
            number:    number of the MWS element
            piecefactor:    piecefactor of the MWS element
            longitBarHeight:    longitBarHeight of the MWS element
            SegmentNumber:    SegmentNumber of the MWS element
            SegmentVector:    SegmentVector of the MWS element
            SegementPointList:    SegementPointList of the MWS element
            ReinforcementList:    ReinforcementList of the MWS element
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def Factory(self) -> None:
        """Property for Factory
        Value type: str


        :type: None
        """
    @property
    def IndexLongitBar(self) -> None:
        """Index of the longitudinal bar in the Reinfrocementlist
        Value type: int


        :type: None
        """
    @property
    def LongitBarHeight(self) -> None:
        """Heightposition of the longitudinal bar (1 = Position 1, 2 = Position 2)
        Value type: int


        :type: None
        """
    @property
    def Name(self) -> None:
        """Property for Name
        Value type: str


        :type: None
        """
    @property
    def Number(self) -> None:
        """Property for Number
        Value type: int


        :type: None
        """
    @property
    def Piecefactor(self) -> None:
        """Property for Piecefactor
        Value type: int


        :type: None
        """
    @property
    def ReinforcementList(self) -> None:
        """list of reinforcement placements
        Value type: list


        :type: None
        """
    @property
    def SegmentNumber(self) -> None:
        """Number of the main segement of the transversal shape
        Value type: int


        :type: None
        """
    @property
    def SegmentPointList(self) -> None:
        """Pointlist of the transversal shape
        Value type: list


        :type: None
        """
    @property
    def SegmentVector(self) -> None:
        """Property for Norm Catalog
        Value type: int


        :type: None
        """

class PrecastProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def Location(self) -> :
        """
        """
    @property
    def OverwriteConfiguration(self) -> :
        """
        """
    @property
    def PositionNumberIsOn(self) -> :
        """
        """

class ProfilType(enum.Enum):
    """profil types
    """
    eBUILTIN_PROFIL_TYPE_EDGE = 1
    eBUILTIN_PROFIL_TYPE_JOINT = 0

    names = {eBUILTIN_PROFIL_TYPE_JOINT: eBUILTIN_PROFIL_TYPE_JOINT,
             eBUILTIN_PROFIL_TYPE_EDGE: eBUILTIN_PROFIL_TYPE_EDGE}

    values = {0: eBUILTIN_PROFIL_TYPE_JOINT,
              1: eBUILTIN_PROFIL_TYPE_EDGE}

    def __getitem__(self, key: (str | int | float)) -> ProfilType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class RepresentationProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def BasicReinforcementPrecastElementsActive(self) -> :
        """
        """
    @property
    def FixturesAsWireModel(self) -> :
        """
        """
    @property
    def ReferenceScaleFor2D3DFoils(self) -> :
        """
        """

class Rotation(enum.Enum):
    """rotations for views
    """
    eRotation0 = 0
    eRotation180 = 2
    eRotation270 = 3
    eRotation90 = 1

    names = {eRotation0: eRotation0,
             eRotation90: eRotation90,
             eRotation180: eRotation180,
             eRotation270: eRotation270}

    values = {0: eRotation0,
              1: eRotation90,
              2: eRotation180,
              3: eRotation270}

    def __getitem__(self, key: (str | int | float)) -> Rotation:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ScaleProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def AdditionalText(self) -> :
        """
        """
    @property
    def IsOn(self) -> :
        """
        """
    @property
    def TextParams(self) -> :
        """
        """

class SectionProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def LimitSectionBodyByElement(self) -> :
        """
        """
    @property
    def Name(self) -> :
        """
        """
    @property
    def Prefix(self) -> :
        """
        """
    @property
    def ShowLabel(self) -> :
        """
        """
    @property
    def XDirectionProps(self) -> :
        """
        """
    @property
    def YDirectionProps(self) -> :
        """
        """
    @property
    def ZDirectionProps(self) -> :
        """
        """

class SubType(enum.Enum):
    """Sub types
    """
    eAnchorPlate = 13
    eAnchorage = 12
    eBarAccessory = 50
    eBarCoupler = 47
    eBarNut = 48
    eBarThread = 49
    eBracingElement = 44
    eCatchmentArea = 41
    eChannel = 54
    eCirculationLoadPoint = 80
    eCirculationPipeAdapter = 81
    eCirculationStartPoint = 79
    eConcreteArea = 83
    eConcreteBeam = 46
    eConcreteBlock = 45
    eConnectionModeller = 24
    eConnectionWallColumn = 93
    eConnectorEBT = 88
    eConstPrefabConnection = 60
    eCorbel = 10
    eCoverMountingAngle = 53
    eCrossRib = 82
    eElectricalBIE = 67
    eElectricalLamp = 68
    eElectricalRoute = 69
    eFacility = 32
    eFalseJoint = 55
    eFill = 29
    eFrame = 9
    eHeatingLoadPoint = 71
    eHeatingPipeAdapter = 72
    eHeatingStartPoint = 70
    eHollowBody = 25
    eInsertion = 35
    eInsulationArea = 85
    eInsulationElement = 90
    eInsulationStripe = 89
    eJointLength = 22
    eJointReinforcement = 28
    eLinePointPlacement = 58
    eLoadCut = 19
    eMultiLine3D = 42
    eNailer = 92
    eNode = 39
    eOverrule = 86
    ePipe = 30
    ePipePoint = 31
    ePlacingLoop = 26
    ePolyline = 1
    ePrefabConnection = 37
    ePrefabConnectionCorner = 38
    ePrefabModeller = 23
    eProfileEdge = 21
    eReinforcement_Cage = 87
    eRevealAnchor = 8
    eRevealAnchorVirtual = 20
    eRibBody = 59
    eRingBeam = 6
    eRoofLine = 3
    eRoofParapetLine = 4
    eRoofParapetSupport = 5
    eRope = 40
    eSTD_Formwork = 94
    eSanitationLoadPoint = 77
    eSanitationPipeAdapter = 78
    eSanitationStartPoint = 76
    eSecondaryReinf = 27
    eSewageLoadPoint = 65
    eSewageNetElement = 52
    eSewagePipeAdapter = 66
    eSewageStartPoint = 64
    eShaft = 33
    eSlidingRestraint = 7
    eSolidStrip = 56
    eSpecialBuilding = 34
    eSpecialLoad_Undefined = 17
    eSpecialLoad_X = 14
    eSpecialLoad_Y = 15
    eSpecialLoad_Z = 16
    eSphere = 63
    eSteelProfile = 43
    eStripCorbel = 57
    eStructuralRecessFaceSupport = 62
    eStructuralRecessLongitudinalSupport = 61
    eSurface = 51
    eTieBar = 11
    eTileArea = 91
    eTileElement = 84
    eTrimmer = 18
    eUseNoSpecialSubType = 0
    eUseSameSubType = -1
    eVentilationDuctAdapter = 75
    eVentilationLoadPoint = 74
    eVentilationStartPoint = 73
    eZone = 36

    names = {eUseSameSubType: eUseSameSubType,
             eUseNoSpecialSubType: eUseNoSpecialSubType,
             ePolyline: ePolyline,
             eRoofLine: eRoofLine,
             eRoofParapetLine: eRoofParapetLine,
             eRoofParapetSupport: eRoofParapetSupport,
             eRingBeam: eRingBeam,
             eSlidingRestraint: eSlidingRestraint,
             eRevealAnchor: eRevealAnchor,
             eFrame: eFrame,
             eCorbel: eCorbel,
             eTieBar: eTieBar,
             eAnchorage: eAnchorage,
             eAnchorPlate: eAnchorPlate,
             eSpecialLoad_X: eSpecialLoad_X,
             eSpecialLoad_Y: eSpecialLoad_Y,
             eSpecialLoad_Z: eSpecialLoad_Z,
             eSpecialLoad_Undefined: eSpecialLoad_Undefined,
             eTrimmer: eTrimmer,
             eLoadCut: eLoadCut,
             eRevealAnchorVirtual: eRevealAnchorVirtual,
             eProfileEdge: eProfileEdge,
             eJointLength: eJointLength,
             ePrefabModeller: ePrefabModeller,
             eConnectionModeller: eConnectionModeller,
             eHollowBody: eHollowBody,
             ePlacingLoop: ePlacingLoop,
             eSecondaryReinf: eSecondaryReinf,
             eJointReinforcement: eJointReinforcement,
             eFill: eFill,
             ePipe: ePipe,
             ePipePoint: ePipePoint,
             eFacility: eFacility,
             eShaft: eShaft,
             eSpecialBuilding: eSpecialBuilding,
             eInsertion: eInsertion,
             eZone: eZone,
             ePrefabConnection: ePrefabConnection,
             ePrefabConnectionCorner: ePrefabConnectionCorner,
             eNode: eNode,
             eRope: eRope,
             eCatchmentArea: eCatchmentArea,
             eMultiLine3D: eMultiLine3D,
             eSteelProfile: eSteelProfile,
             eBracingElement: eBracingElement,
             eConcreteBlock: eConcreteBlock,
             eConcreteBeam: eConcreteBeam,
             eBarCoupler: eBarCoupler,
             eBarNut: eBarNut,
             eBarThread: eBarThread,
             eBarAccessory: eBarAccessory,
             eSurface: eSurface,
             eSewageNetElement: eSewageNetElement,
             eCoverMountingAngle: eCoverMountingAngle,
             eChannel: eChannel,
             eFalseJoint: eFalseJoint,
             eSolidStrip: eSolidStrip,
             eStripCorbel: eStripCorbel,
             eLinePointPlacement: eLinePointPlacement,
             eRibBody: eRibBody,
             eConstPrefabConnection: eConstPrefabConnection,
             eStructuralRecessLongitudinalSupport: eStructuralRecessLongitudinalSupport,
             eStructuralRecessFaceSupport: eStructuralRecessFaceSupport,
             eSphere: eSphere,
             eSewageStartPoint: eSewageStartPoint,
             eSewageLoadPoint: eSewageLoadPoint,
             eSewagePipeAdapter: eSewagePipeAdapter,
             eElectricalBIE: eElectricalBIE,
             eElectricalLamp: eElectricalLamp,
             eElectricalRoute: eElectricalRoute,
             eHeatingStartPoint: eHeatingStartPoint,
             eHeatingLoadPoint: eHeatingLoadPoint,
             eHeatingPipeAdapter: eHeatingPipeAdapter,
             eVentilationStartPoint: eVentilationStartPoint,
             eVentilationLoadPoint: eVentilationLoadPoint,
             eVentilationDuctAdapter: eVentilationDuctAdapter,
             eSanitationStartPoint: eSanitationStartPoint,
             eSanitationLoadPoint: eSanitationLoadPoint,
             eSanitationPipeAdapter: eSanitationPipeAdapter,
             eCirculationStartPoint: eCirculationStartPoint,
             eCirculationLoadPoint: eCirculationLoadPoint,
             eCirculationPipeAdapter: eCirculationPipeAdapter,
             eCrossRib: eCrossRib,
             eConcreteArea: eConcreteArea,
             eTileElement: eTileElement,
             eInsulationArea: eInsulationArea,
             eOverrule: eOverrule,
             eReinforcement_Cage: eReinforcement_Cage,
             eConnectorEBT: eConnectorEBT,
             eInsulationStripe: eInsulationStripe,
             eInsulationElement: eInsulationElement,
             eTileArea: eTileArea,
             eNailer: eNailer,
             eConnectionWallColumn: eConnectionWallColumn,
             eSTD_Formwork: eSTD_Formwork}

    values = {-1: eUseSameSubType,
              0: eUseNoSpecialSubType,
              1: ePolyline,
              3: eRoofLine,
              4: eRoofParapetLine,
              5: eRoofParapetSupport,
              6: eRingBeam,
              7: eSlidingRestraint,
              8: eRevealAnchor,
              9: eFrame,
              10: eCorbel,
              11: eTieBar,
              12: eAnchorage,
              13: eAnchorPlate,
              14: eSpecialLoad_X,
              15: eSpecialLoad_Y,
              16: eSpecialLoad_Z,
              17: eSpecialLoad_Undefined,
              18: eTrimmer,
              19: eLoadCut,
              20: eRevealAnchorVirtual,
              21: eProfileEdge,
              22: eJointLength,
              23: ePrefabModeller,
              24: eConnectionModeller,
              25: eHollowBody,
              26: ePlacingLoop,
              27: eSecondaryReinf,
              28: eJointReinforcement,
              29: eFill,
              30: ePipe,
              31: ePipePoint,
              32: eFacility,
              33: eShaft,
              34: eSpecialBuilding,
              35: eInsertion,
              36: eZone,
              37: ePrefabConnection,
              38: ePrefabConnectionCorner,
              39: eNode,
              40: eRope,
              41: eCatchmentArea,
              42: eMultiLine3D,
              43: eSteelProfile,
              44: eBracingElement,
              45: eConcreteBlock,
              46: eConcreteBeam,
              47: eBarCoupler,
              48: eBarNut,
              49: eBarThread,
              50: eBarAccessory,
              51: eSurface,
              52: eSewageNetElement,
              53: eCoverMountingAngle,
              54: eChannel,
              55: eFalseJoint,
              56: eSolidStrip,
              57: eStripCorbel,
              58: eLinePointPlacement,
              59: eRibBody,
              60: eConstPrefabConnection,
              61: eStructuralRecessLongitudinalSupport,
              62: eStructuralRecessFaceSupport,
              63: eSphere,
              64: eSewageStartPoint,
              65: eSewageLoadPoint,
              66: eSewagePipeAdapter,
              67: eElectricalBIE,
              68: eElectricalLamp,
              69: eElectricalRoute,
              70: eHeatingStartPoint,
              71: eHeatingLoadPoint,
              72: eHeatingPipeAdapter,
              73: eVentilationStartPoint,
              74: eVentilationLoadPoint,
              75: eVentilationDuctAdapter,
              76: eSanitationStartPoint,
              77: eSanitationLoadPoint,
              78: eSanitationPipeAdapter,
              79: eCirculationStartPoint,
              80: eCirculationLoadPoint,
              81: eCirculationPipeAdapter,
              82: eCrossRib,
              83: eConcreteArea,
              84: eTileElement,
              85: eInsulationArea,
              86: eOverrule,
              87: eReinforcement_Cage,
              88: eConnectorEBT,
              89: eInsulationStripe,
              90: eInsulationElement,
              91: eTileArea,
              92: eNailer,
              93: eConnectionWallColumn,
              94: eSTD_Formwork}

    def __getitem__(self, key: (str | int | float)) -> SubType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class SurfaceProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def SurfaceElements(self) -> :
        """
        """
    @property
    def Transparency(self) -> :
        """
        """

class TextAlignment(enum.Enum):
    """Alignments for text of labeling for view
    """
    eBottomCenter = 6
    eCenter = 5
    eLeftBottom = 1
    eLeftCenter = 9
    eLeftTop = 4
    eRightBottom = 2
    eRightCenter = 7
    eRightTop = 3
    eTopCenter = 8
    eUnknownAlignment = 0

    names = {eUnknownAlignment: eUnknownAlignment,
             eLeftTop: eLeftTop,
             eTopCenter: eTopCenter,
             eRightTop: eRightTop,
             eLeftCenter: eLeftCenter,
             eCenter: eCenter,
             eRightCenter: eRightCenter,
             eLeftBottom: eLeftBottom,
             eBottomCenter: eBottomCenter,
             eRightBottom: eRightBottom}

    values = {0: eUnknownAlignment,
              4: eLeftTop,
              8: eTopCenter,
              3: eRightTop,
              9: eLeftCenter,
              5: eCenter,
              7: eRightCenter,
              1: eLeftBottom,
              6: eBottomCenter,
              2: eRightBottom}

    def __getitem__(self, key: (str | int | float)) -> TextAlignment:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class TextParameters():

    def __init__(self):
        """Initialize
        """
    @property
    def BackgroundColorType(self) -> :
        """
        """
    @property
    def BorderColor(self) -> :
        """
        """
    @property
    def BorderLineType(self) -> :
        """
        """
    @property
    def BorderOffset(self) -> :
        """
        """
    @property
    def BorderThickness(self) -> :
        """
        """
    @property
    def ColumnAngle(self) -> :
        """
        """
    @property
    def CustomBackgroundColor(self) -> :
        """
        """
    @property
    def FontAngle(self) -> :
        """
        """
    @property
    def FontColor(self) -> :
        """
        """
    @property
    def FontEmphasis(self) -> :
        """
        """
    @property
    def FontHeight(self) -> :
        """
        """
    @property
    def FontID(self) -> :
        """
        """
    @property
    def FontLayer(self) -> :
        """
        """
    @property
    def FontWidth(self) -> :
        """
        """
    @property
    def IsFontColorFromLayer(self) -> :
        """
        """
    @property
    def IsFontLineTypeFromLayer(self) -> :
        """
        """
    @property
    def IsFontPenFromLayer(self) -> :
        """
        """
    @property
    def PositionNumberBorderLine(self) -> :
        """
        """
    @property
    def RowDistance(self) -> :
        """
        """
    @property
    def TextPlacementPointType(self) -> :
        """
        """
    @property
    def UseBorderAroundTheText(self) -> :
        """
        """
    @property
    def UseConstantSizeInLayout(self) -> :
        """
        """
    @property
    def UseCustomTextParameters(self) -> :
        """
        """

class TextProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def Color(self) -> :
        """
        """
    @property
    def FontAngle(self) -> :
        """
        """
    @property
    def FontId(self) -> :
        """
        """
    @property
    def Height(self) -> :
        """
        """
    @property
    def Width(self) -> :
        """
        """

class Type(enum.Enum):
    """types
    """
    eGroup_Fixture = 3
    eLine_Fixture = 1
    ePlane_Fixture = 2
    ePoint_Fixture = 0
    eUseSameType = -1

    names = {eUseSameType: eUseSameType,
             ePoint_Fixture: ePoint_Fixture,
             eLine_Fixture: eLine_Fixture,
             ePlane_Fixture: ePlane_Fixture,
             eGroup_Fixture: eGroup_Fixture}

    values = {-1: eUseSameType,
              0: ePoint_Fixture,
              1: eLine_Fixture,
              2: ePlane_Fixture,
              3: eGroup_Fixture}

    def __getitem__(self, key: (str | int | float)) -> Type:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class View(Cell):

    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, direction: Direction, rotation: Rotation):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            Direction
            Rotation
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, direction: Direction, rotation: Rotation,
                 viewProps: ViewProperties):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            Direction
            Rotation
            View:properties
        """
    @typing.overload
    def __init__(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, cellId: int, direction: Direction, rotation: Rotation,
                 viewProps: ViewProperties, conditionTemplate: str):
        """Constructor

        Args:
            DocumentAdapter
            CellId
            Direction
            Rotation
            View:properties
            Condition:template
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def create(self, elements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList, position: NemAll_Python_Geometry.Point2D,
               view: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter) -> bool:
        """Creates a standalon local uvs view without plan

        Args:
            Allplan::IFW::ElementAdapter::BaseElementAdapterList:-> elements of the view
            Allplan::Geometry::Point2D:-> position of the view
            Allplan::IFW::ElementAdapter::BaseElementAdapter:-> created view
        """

class ViewProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def ClippingPathProps(self) -> :
        """
        """
    @property
    def FormatProps(self) -> :
        """
        """
    @property
    def LabelingProps(self) -> :
        """
        """
    @property
    def LightProps(self) -> :
        """
        """
    @property
    def RepresentationProps(self) -> :
        """
        """
    @property
    def SectionProps(self) -> :
        """
        """
    @property
    def SurfaceProps(self) -> :
        """
        """
    @property
    def UpdateAutomatically(self) -> :
        """
        """
    @property
    def VisibilityProps(self) -> :
        """
        """
    @property
    def ZoomFactorX(self) -> :
        """
        """
    @property
    def ZoomFactorY(self) -> :
        """
        """

class VisibilityProperties():

    def __init__(self):
        """Initialize
        """
    @property
    def AllowedLayers(self) -> :
        """
        """
    @property
    def Printset(self) -> :
        """
        """
    @property
    def SelectedLayers(self) -> :
        """
        """

def CreateElementplan(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, catOffset: int, pageProps: list,
                      elements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList):
    """@brief Creates the elementplan
    @param doc DocumentAdapter for ptrArrrayData
    @param catOffset Offset of layout in catalog
    @param elements Elements for plan

    Args:
        doc
        catOffset
        pageProps
        elements
    """
def CreatePrecastElements(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, insertionMat: NemAll_Python_Geometry.Matrix3D,
                          elements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList, modelEleList: list, modelUuidList: list, viewProj: NemAll_Python_IFW_Input.ViewWorldProjection, delete_python: bool):
    """Create the precast elements

    Args:
        doc:            Document
        insertionMat:   Insertion matrix
        elements:       List of created elements
        modelEleList:   List of model elements which have to be created
        modelUuidList:  List with the model UUIDS in modification mode
        viewProj:       View projection
        delete_python:  bool weather the python should be deleted after update
    """
def GetPagePropertiesFromCatalog(catOffset: int) -> list:
    """@brief Gets the pages from selected layout
    @param catOffset Offset of layout in catalog
    @return List of pages

    Args:
        catOffset
    """
def LockPrecastUpdate():
    """Lock the precast update
    """
def TriggerPrecastUpdate(elements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList) -> bool:
    """Trigger the precast update

    Args:
        elements:   Elements to update

    Returns:
        update successful: true/false)
    """
def UnlockPrecastUpdate():
    """Lock the precast update
    """
