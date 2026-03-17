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

"""Exposed classes and functions from NemAll_Python_Reinforcement"""

from __future__ import annotations

import typing

import enum
import collections.abc

import NemAll_Python_BaseElements
import NemAll_Python_BasisElements
import NemAll_Python_Geometry
import NemAll_Python_IFW_ElementAdapter
import NemAll_Python_IFW_Input
import NemAll_Python_Utility


__all__ = [
    "AllplanElement",
    "AnchorageLengthService",
    "AnchorageType",
    "Bar",
    "BarAreaPlacementProperties",
    "BarAreaPlacementService",
    "BarPlacement",
    "BarPlacementSection",
    "BarPositionData",
    "BarSpacer",
    "BarWithArc",
    "BarsOperations",
    "BendingRollerService",
    "BendingShape",
    "BendingShapeList",
    "BendingShapeType",
    "CircleStirrup",
    "CircularAreaElement",
    "Column",
    "ColumnStirrup",
    "CreateReinforcementLabeling",
    "CrossBars",
    "Diamond",
    "DivideBarsParameters",
    "ExtrudeBarPlacement",
    "Freeform",
    "FullCircle",
    "GeometryExpansionUtil",
    "HookLengthService",
    "HookType",
    "InitApplicationtest",
    "InitUnitTest",
    "LShapedBar",
    "LabelType",
    "LabelWithComb",
    "LabelWithComb2Pointer",
    "LabelWithComb3Pointer",
    "LabelWithDimensionLine",
    "LabelWithFan",
    "LabelWithFanStartCenterEnd",
    "LabelWithFanStartEnd",
    "LabelWithPointer",
    "LongitudinalBar",
    "LongitudinalBarDoubleBentOff",
    "LongitudinalBarFourTimesBentOff",
    "LongitudinalBarProperties",
    "LongitudinalBarPropertiesList",
    "LongitudinalBarSingleBentOff",
    "LongitudinalBars",
    "Mesh",
    "MeshAreaPlacementProperties",
    "MeshAreaPlacementService",
    "MeshBendingDirection",
    "MeshData",
    "MeshOperations",
    "MeshPlacement",
    "NormType",
    "Normal",
    "OpenStirrup",
    "PlaneMeshPlacement",
    "ReinfElement",
    "ReinforcementLabel",
    "ReinforcementLabelList",
    "ReinforcementLabelPointerProperties",
    "ReinforcementLabelProperties",
    "ReinforcementService",
    "ReinforcementSettings",
    "ReinforcementShapeBuilder",
    "ReinforcementType",
    "ReinforcementUtil",
    "SHook",
    "SpiralElement",
    "Stirrup",
    "StirrupType",
    "SweepBarPlacement",
    "Torsion",
    "TorsionStirrup",
    "eAnchorage",
    "eAnchorageHook",
    "eAnchorageHookOneCrossBar",
    "eAnchorageStraight",
    "eAnchorageStraightOneCrossBar",
    "eAnchorageStraightTwoCrossBars",
    "eAngle",
    "eNORM_AS",
    "eNORM_BS",
    "eNORM_DIN",
    "eNORM_DIN_1",
    "eNORM_DIN_H",
    "eNORM_EC2",
    "eNORM_EHE",
    "eNORM_NEN",
    "eNORM_NF",
    "eNORM_OE",
    "eNORM_SIA",
    "eNORM_SNIP",
    "eNORM_SNIP2003",
    "eNormNo",
    "eStirrup"
]


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

class AnchorageLengthService():
    """Service class for the anchorage length calculation
    """
    def Calculate(self, concreteGrade: int, steelGrade: int, diameter: float, asMesh: float, bDoubleBar: bool, meshBarDistCross: float,
                  bMesh: bool, barDistance: float, roundLength: float):
        """Calculation of the anchorage length

        Args:
            concreteGrade:    Concrete grade index (starting from 1)
            steelGrade:       Steel grade
            diameter:         Diameter
            asMesh:           asMesh of the mesh
            bDoubleBar:       Double bar
            meshBarDistCross: Distance of the mesh bars cross to the anchorage direction
            bMesh:            Anchorage for a mesh
            barDistance:      Bar distance
            roundLength:      Rounding length
        """
    def CalculateBar(self, concreteGrade: int, steelGrade: int, diameter: float, bDoubleBar: bool, barDistance: float, roundLength: float):
        """Calculation of the anchorage length for a bar

        Args:
            concreteGrade: Concrete grade index (starting from 1)
            steelGrade:    Steel grade
            diameter:      Diameter
            bDoubleBar:    Double bar
            barDistance:   Bar distance
            roundLength:   Rounding length
        """
    def GetAnchorageLength(self) -> float:
        """Get the anchorage length

        Returns:
             Anchorage length
        """
    def GetAnchorageType(self) -> AnchorageType:
        """Get the anchorage type

        Returns:
             Anchorage type
        """
    def GetAsFactor(self) -> float:
        """Get the as factor required / available

        Returns:
             As mesh factor
        """
    def GetCompositionZone(self) -> int:
        """Get the composition zone

        Returns:
             Composition zone
        """
    def GetHookAngle(self) -> float:
        """Get the hook angle

        Returns:
             Hook angle
        """
    def GetL1(self) -> float:
        """Get length L1

        Returns:
             Length L1
        """
    def GetL2(self) -> float:
        """Get length L2

        Returns:
             Length L2
        """
    def GetL3(self) -> float:
        """Get length L3

        Returns:
             Length L3
        """
    def GetLongitudinalOffset(self) -> float:
        """Get the longitudinal offset

        Returns:
             Longitudinal offset
        """
    def GetOverlapLength(self) -> float:
        """Get the overlap length

        Returns:
             Overlap length
        """
    def IsCompressionBar(self) -> bool:
        """Get the compression bar state

        Returns:
             Compression bar: true/false
        """
    def SetAnchorageType(self, anchorageType: AnchorageType):
        """Set the anchorage type

        Args:
            anchorageType: Anchorage type
        """
    def SetAsFactor(self, AsFactor: float):
        """Set the as factor required / available

        Args:
            AsFactor: As facto required / availabler
        """
    def SetCompositionZone(self, compositionZone: int):
        """Set the composition zone

        Args:
            compositionZone: Composition zone
        """
    def SetCompressionBar(self, bCompressionBar: bool):
        """Set the compression bar state

        Args:
            bCompressionBar: Compression bar: true/false
        """
    def SetHookAngle(self, hookAngle: float):
        """Set the hook angle

        Args:
            hookAngle: Hook angle
        """
    def SetLongitudinalOffset(self, longitudinalOffset: float):
        """Set the longitudinal offset

        Args:
            longitudinalOffset: longitudinal offset
        """
    def __init__(self):
        """Initialize
        """

class AnchorageType(enum.Enum):
    """Types of the anchorage
    """
    eAnchorageHook = 2
    eAnchorageHookOneCrossBar = 4
    eAnchorageStraight = 1
    eAnchorageStraightOneCrossBar = 3
    eAnchorageStraightTwoCrossBars = 5

    names = {eAnchorageStraight: eAnchorageStraight,
             eAnchorageHook: eAnchorageHook,
             eAnchorageStraightOneCrossBar: eAnchorageStraightOneCrossBar,
             eAnchorageHookOneCrossBar: eAnchorageHookOneCrossBar,
             eAnchorageStraightTwoCrossBars: eAnchorageStraightTwoCrossBars}

    values = {1: eAnchorageStraight,
              2: eAnchorageHook,
              3: eAnchorageStraightOneCrossBar,
              4: eAnchorageHookOneCrossBar,
              5: eAnchorageStraightTwoCrossBars}

    def __getitem__(self, key: (str | int | float)) -> AnchorageType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class BarAreaPlacementProperties():

    class Benching(enum.Enum):
        """Benching type
        """
        HorizontalBenching = 1
        NoBenching = 0
        VerticalBenching = 2

        names = {NoBenching: NoBenching,
                 HorizontalBenching: HorizontalBenching,
                 VerticalBenching: VerticalBenching}

        values = {0: NoBenching,
                  1: HorizontalBenching,
                  2: VerticalBenching}

        def __getitem__(self, key: (str | int | float)) -> BarAreaPlacementProperties.Benching:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    class PlacementStrategy(enum.Enum):
        """PlacementStrategy type
        """
        Centered = 2
        FromEnd = 3
        FromStart = 1

        names = {FromStart: FromStart,
                 Centered: Centered,
                 FromEnd: FromEnd}

        values = {1: FromStart,
                  2: Centered,
                  3: FromEnd}

        def __getitem__(self, key: (str | int | float)) -> BarAreaPlacementProperties.PlacementStrategy:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, diameter: float, distance: float, overlapping: float, isMoveOverlapping: bool, maxBarLength: float,
                 startBarLength: float, maxPlacementLength: float, firstBarEdgeDistance: float, placementStrategy: PlacementStrategy, benching: Benching, benchingLength: float, isPolygonalPlacement: bool):
        """Constructor

        Args:
            diameter:             Diameter
            distance:             Distance
            overlapping:          Overlapping
            isMoveOverlapping:    Is overlapping moved: true/false
            maxBarLength:         Maximal bar length
            startBarLength:       Start bar length
            maxPlacementLength:   Maximal placement length, 0 = will be calculated
            firstBarEdgeDistance: First bar edge distance, <0 = will be calculated
            placementStrategy:    Placement strategy
            benching:             Benching
            benchingLength:       Benching length
            isPolygonalPlacement: Place in polygon: true / place per meter: false
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class BarAreaPlacementService():

    def AddOpeningPolygon(self, arg2: NemAll_Python_Geometry.Polygon3D, openingPol: float):
        """Add an opening polygon

        Args:
            openingPol: Opening polygon
        """
    def Calculate(self, doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, barPlacementProp: BarAreaPlacementProperties,
                  placementMatrix: NemAll_Python_Geometry.Matrix3D, concreteCoverZDir: float) -> list:
        """Calculate the meshes

        Args:
            doc:                 Document
            barPlacementProp:    Placement properties
            placementMatrix:     Placement matrix
            concreteCoverZDir:   Concrete cover in the local z direction
        """
    def SetOuterPolygon(self, arg2: NemAll_Python_Geometry.Polygon3D, placementPol: float):
        """Constructor

        Args:
            placementPol: Placement polygon
        """
    def __init__(self):
        """Initialize
        """

class ReinfElement(AllplanElement):


class BarPlacementSection():
    """Implementation of the bar placement section class
    """
    def GetDistance(self) -> float:
        """Get the distance

        Returns:
            Distance
        """
    def GetLength(self) -> float:
        """Get the length

        Returns:
            Length
        """
    def IsEnabled(self) -> bool:
        """Get the enabled state

        Returns:
            Enable state
        """
    @typing.overload
    def __init__(self, isEnabled: bool, length: float, distance: float):
        """Constructor

        Args:
            isEnabled: Section enabled state
            length:    Section length
            distance:  Bar distance
        """
    @typing.overload
    def __init__(self, element: BarPlacementSection):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class BendingShape():
    """Implementation of the reinforcement shape
    """
    def GetBendingRoller(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get the bending roller

        Returns:
            Bending roller
        """
    def GetBendingShapeType(self) -> BendingShapeType:
        """Get the bending shape type

        Returns:
            Bending shape type
        """
    def GetConcreteGrade(self) -> int:
        """Get the concrete grade

        Returns:
            Concrete grade  (index of the global list starting from 0, -1 = use global value from the Allplan settings)
        """
    def GetDiameter(self) -> float:
        """Get the diameter

        Returns:
            Diameter
        """
    def GetHookAngleEnd(self) -> float:
        """Get the hook angle a the end of the shape

        Returns:
            Hook angle at the end of the shape
        """
    def GetHookAngleStart(self) -> float:
        """Get the hook angle a the start of the shape

        Returns:
            Hook angle at the start of the shape
        """
    def GetHookLengthEnd(self) -> float:
        """Get the hook length a the end of the shape

        Returns:
            Hook length at the end of the shape
        """
    def GetHookLengthStart(self) -> float:
        """Get the hook length a the start of the shape

        Returns:
            Hook length at the start of the shape
        """
    def GetHookTypeEnd(self) -> HookType:
        """Get the hook type a the end of the shape

        Returns:
            Hook type a the end of the shape
        """
    def GetHookTypeStart(self) -> HookType:
        """Get the hook type a the start of the shape

        Returns:
            Hook type a the start of the shape
        """
    def GetMeshBendingDirection(self) -> MeshBendingDirection:
        """Get the mesh bending direction

        Returns:
            Mesh bending direction
        """
    def GetMeshType(self) -> str:
        """Get the mesh type

        Returns:
            Mesh type
        """
    def GetShapePolyline(self) -> NemAll_Python_Geometry.Polyline3D:
        """Get the shape polyline

        Returns:
            Shape polyline
        """
    def GetSteelGrade(self) -> int:
        """Get the steel grade

        Returns:
            Steel grade
        """
    def IsValid(self) -> bool:
        """Get the state of the shape

        Returns:
            Shape is valid: true/false
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the shape

        Args:
            transVec: Move vector
        """
    @typing.overload
    def Rotate(self, modelAngles: object, refPnt: NemAll_Python_Geometry.Point3D):
        """Rotate the shape

        Args:
            modelAngles: Model angles
            refPnt:      Reference point of the rotation
        """
    @typing.overload
    def Rotate(self, modelAngles: object):
        """Rotate the shape

        Args:
            modelAngles: Model angles
        """
    def Rotate(self):
        """ Overloaded function. See individual overloads.
        """
    def SetBendingRoller(self, bendingRoller: NemAll_Python_Utility.VecDoubleList):
        """Set the bending roller

        Args:
            bendingRoller: Bending roller
        """
    def SetDiameter(self, diameter: float):
        """Set the diameter

        Args:
            diameter: diameter
        """
    def SetHookAngleEnd(self, hookAngleEnd: float):
        """Set the hook angle at the end of the shape

        Args:
            hookAngleEnd: Hook angle
        """
    def SetHookAngleStart(self, hookAngleStart: float):
        """Set the hook angle at the start of the shape

        Args:
            hookAngleStart: Hook angle
        """
    def SetHookLengthEnd(self, hookLengthEnd: float):
        """Set the end length of the hook

        Args:
            hookLengthEnd: End length of the hook
        """
    def SetHookLengthStart(self, hookLengthStart: float):
        """Set the start length of the hook

        Args:
            hookLengthStart: Start length of the hook
        """
    def SetHookTypeEnd(self, hookTypeEnd: HookType):
        """Set the hook type at the end of the shape

        Args:
            hookTypeEnd: Hook type
        """
    def SetHookTypeStart(self, hookTypeStart: HookType):
        """Set the hook type at the start of the shape

        Args:
            hookTypeStart: Hook type
        """
    def SetShapePolyline(self, shapePol: NemAll_Python_Geometry.Polyline3D):
        """Set the shape polyline

        Args:
            shapePol: Shape polyline
        """
    def SetSteelGrade(self, steelGrade: int):
        """Set the steel grade

        Args:
            steelGrade: steel grade
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the shape

        Args:
            transMat: Transformation matrix
        """
    def __eq__(self, shape: BendingShape) -> bool:
        """Compare operator

        Args:
            shape: Shape to compare

        Returns:
            Shapes are equal: true/false
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, shapePol: NemAll_Python_Geometry.Polyline3D, bendingRoller: NemAll_Python_Utility.VecDoubleList, diameter: float,
                 steelGrade: int, concreteGrade: int, bendingShapeType: BendingShapeType):
        """Constructor

        Args:
            shapePol:         Shape polyline
            bendingRoller:    Bending roller
            diameter:         Diameter
            steelGrade:       Steel grade
            concreteGrade:    Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType: Bending shape type
        """
    @typing.overload
    def __init__(self, shapePoint: NemAll_Python_Geometry.Point3D, diameter: float, steelGrade: int, concreteGrade: int):
        """Constructor for a point placement

        Args:
            shapePoint:    Shape placement point
            diameter:      Diameter
            steelGrade:    Steel grade
            concreteGrade: Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
        """
    @typing.overload
    def __init__(self, shapePol: NemAll_Python_Geometry.Polyline3D, bendingRoller: NemAll_Python_Utility.VecDoubleList, meshType: str,
                 meshBendingDirection: MeshBendingDirection, steelGrade: int, concreteGrade: int, bendingShapeType: BendingShapeType):
        """Constructor

        Args:
            shapePol:             Shape polyline
            bendingRoller:        Bending roller
            meshType:             Mesh type
            meshBendingDirection: Mesh bending direction
            steelGrade:           Steel grade
            concreteGrade:        Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType:     Bending shape type
        """
    @typing.overload
    def __init__(self, shapePol: NemAll_Python_Geometry.Polyline3D, bendingRoller: NemAll_Python_Utility.VecDoubleList, diameter: float,
                 steelGrade: int, concreteGrade: int, bendingShapeType: BendingShapeType, hookLengthStart: float, hookAngleStart: float, hookTypeStart: HookType, hookLengthEnd: float, hookAngleEnd: float, hookTypeEnd: HookType):
        """Constructor

        Args:
            shapePol:         Shape polyline
            bendingRoller:    Bending roller
            diameter:         Diameter
            steelGrade:       Steel grade
            concreteGrade:    Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType: Bending shape type
            hookLengthStart:  Hook length at the start of the shape
            hookAngleStart:   Hook angle at the start of the shape
            hookTypeStart:    Hook type at the start of the shape
            hookLengthEnd:    Hook length at the end of the shape
            hookAngleEnd:     Hook angle at the end of the shape
            hookTypeEnd:      Hook type at the end of the shape
        """
    @typing.overload
    def __init__(self, shapePol: NemAll_Python_Geometry.Polyline3D, bendingRoller: NemAll_Python_Utility.VecDoubleList, meshType: str,
                 meshBendingDirection: MeshBendingDirection, steelGrade: int, concreteGrade: int, bendingShapeType: BendingShapeType, hookLengthStart: float, hookAngleStart: float, hookTypeStart: HookType, hookLengthEnd: float, hookAngleEnd: float, hookTypeEnd: HookType):
        """Constructor

        Args:
            shapePol:             Shape polyline
            bendingRoller:        Bending roller
            meshType:             Mesh type
            meshBendingDirection: Mesh bending direction
            steelGrade:           Steel grade
            concreteGrade:        Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType:     Bending shape type
            hookLengthStart:      Hook length at the start of the shape
            hookAngleStart:       Hook angle at the start of the shape
            hookTypeStart:        Hook type at the start of the shape
            hookLengthEnd:        Hook length at the end of the shape
            hookAngleEnd:         Hook angle at the end of the shape
            hookTypeEnd:          Hook type at the end of the shape
        """
    @typing.overload
    def __init__(self, element: BendingShape):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def BendingRoller(self) -> list[float]:
        """Get the bending roller
        """
    @BendingRoller.setter
    def BendingRoller(self, bendingRoller: list[float]) -> None:
        """Set the bending roller

        Args:
            bendingRoller: Bending roller
        """
    @property
    def Diameter(self) -> float:
        """Get the diameter
        """
    @Diameter.setter
    def Diameter(self, diameter: float) -> None:
        """Set the diameter

        Args:
            diameter: diameter
        """
    @property
    def HookAngleEnd(self) -> float:
        """Get the hook angle a the end of the shape
        """
    @HookAngleEnd.setter
    def HookAngleEnd(self, hookAngleEnd: float) -> None:
        """Set the hook angle at the end of the shape

        Args:
            hookAngleEnd: Hook angle
        """
    @property
    def HookAngleStart(self) -> float:
        """Get the hook angle a the start of the shape
        """
    @HookAngleStart.setter
    def HookAngleStart(self, hookAngleStart: float) -> None:
        """Set the hook angle at the start of the shape

        Args:
            hookAngleStart: Hook angle
        """
    @property
    def HookLengthEnd(self) -> float:
        """Get the hook length a the end of the shape
        """
    @HookLengthEnd.setter
    def HookLengthEnd(self, hookLengthEnd: float) -> None:
        """Set the end length of the hook

        Args:
            hookLengthEnd: End length of the hook
        """
    @property
    def HookLengthStart(self) -> float:
        """Get the hook length a the start of the shape
        """
    @HookLengthStart.setter
    def HookLengthStart(self, hookLengthStart: float) -> None:
        """Set the start length of the hook

        Args:
            hookLengthStart: Start length of the hook
        """
    @property
    def HookTypeEnd(self) -> HookType:
        """Get the hook type a the end of the shape
        """
    @HookTypeEnd.setter
    def HookTypeEnd(self, hookTypeEnd: HookType) -> None:
        """Set the hook type at the end of the shape

        Args:
            hookTypeEnd: Hook type
        """
    @property
    def HookTypeStart(self) -> HookType:
        """Get the hook type a the start of the shape
        """
    @HookTypeStart.setter
    def HookTypeStart(self, hookTypeStart: HookType) -> None:
        """Set the hook type at the start of the shape

        Args:
            hookTypeStart: Hook type
        """
    @property
    def ShapePolyline(self) -> NemAll_Python_Geometry.Polyline3D:
        """Get the shape polyline
        """
    @ShapePolyline.setter
    def ShapePolyline(self, shapePol: NemAll_Python_Geometry.Polyline3D) -> None:
        """Set the shape polyline

        Args:
            shapePol: Shape polyline
        """
    @property
    def SteelGrade(self) -> int:
        """Get the steel grade
        """
    @SteelGrade.setter
    def SteelGrade(self, steelGrade: int) -> None:
        """Set the steel grade

        Args:
            steelGrade: steel grade
        """

class BarsOperations():

    @staticmethod
    def DivideBarsPlacement(placement: DivideBarsParameters, divisionPolyline: NemAll_Python_Geometry.Polyline2D) -> str:
        """Divide the bars placement

        Returns:
              Result message

        Args:
            placement:           BaseElementAdapter with the placement
            divideBarsParameter: Divide bars parameters
            divisionPolyline:    Divison polyline
        """
    @staticmethod
    def JoinBarsPlacements(placement: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList, fillEdges: bool) -> str:
        """Join the bars placements

        Returns:
              Result message

        Args:
            placements:          BaseElementAdapterList with the placements
            fillEdges:           Fill the edges: True/False
        """
    def __init__(self):
        """Initialize
        """

class BendingRollerService():
    """Service class for the bending roller calculation
    """
    @staticmethod
    def GetBendBendingRollerFactor(diameter: float, steelGrade: int, concreteGrade: int) -> float:
        """Get the bend bending roller factor

        Args:
            diameter:      Diameter
            steelGrade:    Steel grade
            concreteGrade: Concrete grade

        Returns:
             Bending roller factor
        """
    @staticmethod
    def GetBendingRoller(diameter: float, steelGrade: int, concreteGrade: int, bStirrup: bool) -> float:
        """Get the bending roller

        Args:
            diameter:      Diameter
            steelGrade:    Steel grade
            concreteGrade: Concrete grade
            bStirrup:      Shape is a stirrup: true/false

        Returns:
             Bending roller factor
        """
    @staticmethod
    def GetBendingRollerFactor(diameter: float, steelGrade: int, concreteGrade: int, bStirrup: bool) -> float:
        """Get the bending roller factor

        Args:
            diameter:      Diameter
            steelGrade:    Steel grade
            concreteGrade: Concrete grade
            bStirrup:      Shape is a stirrup: true/false

        Returns:
             Bending roller factor
        """
    @staticmethod
    def GetDefaultBendingRollers(norm: NormType) -> NemAll_Python_Utility.VecDoubleList:
        """Get the default bending rollers

        Args:
            norm: Norm

        Returns:
             Default bending rollers
        """

class BarPositionData(BendingShape):
    """Implementation of the bar position data
    """
    def GetCount(self) -> int:
        """Get the count

        Returns:
            Count
        """
    def GetLength(self) -> float:
        """Get the length

        Returns:
            length
        """
    def GetPosition(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def SetCount(self, count: int):
        """Set the count

        Args:
            count: Count
        """
    def SetLength(self, length: float):
        """Set the length

        Args:
            length: length
        """
    def SetPosition(self, position: int):
        """Set the position number

        Args:
            position: Position
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, barElement: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter):
        """Constructor

        Args:
            barElement: Bar element
        """
    @typing.overload
    def __init__(self, param: BarPositionData):
        """Copy constructor

        Args:
            param
        """
    @typing.overload
    def __init__(self, bendingShape: BendingShape):
        """Constructor

        Args:
            bendingShape: Bending shape
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Count(self) -> int:
        """Get the count
        """
    @Count.setter
    def Count(self, count: int) -> None:
        """Set the count

        Args:
            count: Count
        """
    @property
    def Length(self) -> float:
        """Get the length
        """
    @Length.setter
    def Length(self, length: float) -> None:
        """Set the length

        Args:
            length: length
        """
    @property
    def Position(self) -> int:
        """Get the position number
        """
    @Position.setter
    def Position(self, position: int) -> None:
        """Set the position number

        Args:
            position: Position
        """

class BendingShapeList():
    """List for BendingShape objects
    """
    def __contains__(self, value: BendingShape) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BendingShape):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BendingShapeList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BendingShape:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BendingShapeList:
        """Add a list

        Args:
            eleList: BendingShape list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BendingShape):
        """Constructor with a BendingShape

        Args:
            ele: BendingShape
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BendingShape

        Args:
            eleList: BendingShape list
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
    def __repr__(self) -> str:
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: BendingShape):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BendingShape):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BendingShapeList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BendingShape list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class BendingShapeType(enum.Enum):
    """Type of the bending shape
    """
    BarSpacer = 113
    BarWithArc = 115
    CircleStirrup = 67
    ColumnStirrup = 110
    Freeform = 99
    LShapedBar = 11
    LongitudinalBar = 0
    LongitudinalBarDoubleBentOff = 26
    LongitudinalBarFourTimesBentOff = 44
    LongitudinalBarSingleBentOff = 15
    OpenStirrup = 21
    SHook = 112
    Stirrup = 51
    TorsionStirrup = 111

    names = {LongitudinalBar: LongitudinalBar,
             LShapedBar: LShapedBar,
             OpenStirrup: OpenStirrup,
             LongitudinalBarSingleBentOff: LongitudinalBarSingleBentOff,
             LongitudinalBarDoubleBentOff: LongitudinalBarDoubleBentOff,
             LongitudinalBarFourTimesBentOff: LongitudinalBarFourTimesBentOff,
             ColumnStirrup: ColumnStirrup,
             Stirrup: Stirrup,
             TorsionStirrup: TorsionStirrup,
             SHook: SHook,
             BarSpacer: BarSpacer,
             CircleStirrup: CircleStirrup,
             BarWithArc: BarWithArc,
             Freeform: Freeform}

    values = {0: LongitudinalBar,
              11: LShapedBar,
              21: OpenStirrup,
              15: LongitudinalBarSingleBentOff,
              26: LongitudinalBarDoubleBentOff,
              44: LongitudinalBarFourTimesBentOff,
              110: ColumnStirrup,
              51: Stirrup,
              111: TorsionStirrup,
              112: SHook,
              113: BarSpacer,
              67: CircleStirrup,
              115: BarWithArc,
              99: Freeform}

    def __getitem__(self, key: (str | int | float)) -> BendingShapeType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class CircularAreaElement(ReinfElement, AllplanElement):
    """Implementation of the bar placement element
    """
    def GetConcreteCoverContour(self) -> float:
        """Get the concrete cover from the contour

        Returns:
            Concrete cover from the contour
        """
    def GetConcreteCoverEnd(self) -> float:
        """Get the concrete cover from the end

        Returns:
            Concrete cover from the end
        """
    def GetConcreteCoverStart(self) -> float:
        """Get the concrete cover from the start

        Returns:
            Concrete cover from the start
        """
    def GetConcreteGrade(self) -> int:
        """Get the concrete grade

        Returns:
            Concrete grade  (index of the global list starting from 0, -1 = use global value from the Allplan settings)
        """
    def GetContourPoints(self) -> NemAll_Python_Geometry.Polyline3D:
        """Get the contour points

        Returns:
            Contour points
        """
    def GetDiameter(self) -> float:
        """Get the diameter

        Returns:
            Diameter
        """
    def GetDistance(self) -> float:
        """Get the distance

        Returns:
            Distance
        """
    def GetEvenFirstLength(self) -> float:
        """Get the first length for the even ring number

        Returns:
            First length for the even ring number
        """
    def GetEvenOverlapEnd(self) -> float:
        """Get the overlap length at the end for the even ring number

        Returns:
            Overlap length at the end for the even ring number
        """
    def GetEvenOverlapStart(self) -> float:
        """Get the overlap length at the start for the even ring number

        Returns:
            Overlap length at the start for the even ring number
        """
    def GetLengthFactor(self) -> float:
        """Get the length factor

        Returns:
            Length factor
        """
    def GetMaxBarLength(self) -> float:
        """Get the maximal bar length

        Returns:
            Maximal bar length
        """
    def GetMaxBarRise(self) -> float:
        """Get the maximal bar radius

        Returns:
            Maximal bar radius
        """
    def GetMinBarLength(self) -> float:
        """Get the minimal bar length

        Returns:
            Minimal bar length
        """
    def GetMinBarRadius(self) -> float:
        """Get the minimal bar radius

        Returns:
            Minimal bar radius
        """
    def GetOddFirstLength(self) -> float:
        """Get the first length for the odd ring number

        Returns:
            First length for the odd ring number
        """
    def GetOddOverlapEnd(self) -> float:
        """Get the overlap length at the end for the odd ring number

        Returns:
            Overlap length at the end for the odd ring number
        """
    def GetOddOverlapStart(self) -> float:
        """Get the overlap length at the start for the even ring number

        Returns:
            Overlap length at the start for the odd ring number
        """
    def GetOuterAngleEnd(self) -> float:
        """Get the outer angle at the end

        Returns:
            Outer angle at the end
        """
    def GetOuterAngleStart(self) -> float:
        """Get the outer angle at the start

        Returns:
            Outer angle at the start
        """
    def GetOverlapLength(self) -> float:
        """Get the overlap length

        Returns:
            Overlap length
        """
    def GetPlacementRule(self) -> int:
        """Get the placement rule

        Returns:
            Placement rule
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def GetRotationAxis(self) -> NemAll_Python_Geometry.Line3D:
        """Get the rotation axis

        Returns:
            Rotation axis
        """
    def GetSteelGrade(self) -> int:
        """Get the steel grade

        Returns:
            Steel grade
        """
    def GetinnerAngleEnd(self) -> float:
        """Get the inner angle at the end

        Returns:
            Inner angle at the end
        """
    def GetinnerAngleStart(self) -> float:
        """Get the inner angle at the start

        Returns:
            Inner angle at the start
        """
    def IsPlacePerLinearMeter(self) -> bool:
        """Get the place per linear meter state

        Returns:
            Place per linear meter: true/false
        """
    def IsbOverlapEndAsCircle(self) -> bool:
        """Get the overlap state at the end

        Returns:
            Overlap length at the end as circle = true, as tangent = false
        """
    def IsbOverlapStartAsCircle(self) -> bool:
        """Get the overlap state at the start

        Returns:
            Overlap length at the start as circle = true, as tangent = false
        """
    def SetBarProperties(self, distance: float, maxBarLength: float, minBarLength: float, placementRule: int, oddFirstLength: float,
                         evenFirstLength: float, minBarRadius: float, maxBarRise: float):
        """Set the bar properties

        Args:
            distance:        Distance
            maxBarLength:    Maximal bar length
            minBarLength:    Minimal bar length
            placementRule:   Placement rule
            oddFirstLength:  First length for the odd ring number
            evenFirstLength: First bar length for the event ring number
            minBarRadius:    Minimal bar radius
            maxBarRise:      Maximal bar rise
        """
    def SetLengthFactor(self, lengthFactor: float):
        """Set the length factor

        Args:
            lengthFactor: Length factor
        """
    def SetOverlap(self, oddOverlapStart: float, evenOverlapStart: float, bOverlapStartAsCircle: bool, oddOverlapEnd: float,
                   evenOverlapEnd: float, bOverlapEndAsCircle: bool, overlapLength: float):
        """Set the overlap

        Args:
            oddOverlapStart:       Overlap length at the start for the odd ring number
            evenOverlapStart:      Overlap length at the start for the even ring number
            bOverlapStartAsCircle: Overlap length at the start as circle = true, as tangent = false
            oddOverlapEnd:         Overlap length at the end for the odd ring number
            evenOverlapEnd:        Overlap length at the end for the even ring number
            bOverlapEndAsCircle:   Overlap length at the end as circle = true, as tangent = false
            overlapLength:         Overlap length
        """
    def SetPlacePerLinearMeter(self, bPlacePerLinearMeter: bool):
        """Set the place per linear meter state

        Args:
            bPlacePerLinearMeter: Place per linear meter: true/false
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, positionNumber: int, diameter: float, steelGrade: int, concreteGrade: int,
                 rotationAxis: NemAll_Python_Geometry.Line3D, contourPoints: NemAll_Python_Geometry.Polyline3D, outerAngleStart: float, outerAngleEnd: float, innerAngleStart: float, innerAngleEnd: float, concreteCoverStart: float, concreteCoverEnd: float, concreteCoverContour: float):
        """Constructor

        Args:
            positionNumber:       Position number
            diameter:             Diameter
            steelGrade:           Steel grade
            concreteGrade:        Concrete grade
            rotationAxis:         Rotation axis
            contourPoints:        Contour points
            outerAngleStart:      Outer angle at the start
            outerAngleEnd:        Outer angle at the end
            innerAngleStart:      Inner angle at the start
            innerAngleEnd:        Inner angle at the end
            concreteCoverStart:   Concrete cover at the start
            concreteCoverEnd:     Concrete cover at the end
            concreteCoverContour: Concrete cover of the contour
        """
    @typing.overload
    def __init__(self, element: CircularAreaElement):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def LengthFactor(self) -> float:
        """Get the length factor
        """
    @LengthFactor.setter
    def LengthFactor(self, lengthFactor: float) -> None:
        """Set the length factor

        Args:
            lengthFactor: Length factor
        """
    @property
    def PlacePerLinearMeter(self) -> bool:
        """Get the place per linear meter state
        """
    @PlacePerLinearMeter.setter
    def PlacePerLinearMeter(self, bPlacePerLinearMeter: bool) -> None:
        """Set the place per linear meter state

        Args:
            bPlacePerLinearMeter: Place per linear meter: true/false
        """

class DivideBarsParameters():
    """Parameters for dividing engineering geometry
    """
    class eDivideMode(enum.Enum):
        """Information of Divide Mode
        """
        GAP = 2
        OVERLAP = 0
        PLANE = 1

        names = {OVERLAP: OVERLAP,
                 PLANE: PLANE,
                 GAP: GAP}

        values = {0: OVERLAP,
                  1: PLANE,
                  2: GAP}

        def __getitem__(self, key: (str | int | float)) -> DivideBarsParameters.eDivideMode:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    class eInputMode(enum.Enum):
        """Information of input mode
        """
        ELEMENT2D = 2
        OPENING = 1
        POLYGON = 0

        names = {POLYGON: POLYGON,
                 OPENING: OPENING,
                 ELEMENT2D: ELEMENT2D}

        values = {0: POLYGON,
                  1: OPENING,
                  2: ELEMENT2D}

        def __getitem__(self, key: (str | int | float)) -> DivideBarsParameters.eInputMode:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    class eLengthPosition(enum.Enum):
        """Information of position of Overlap-/Gap-Length
        """
        LEFT = 0
        MIDDLE = 1
        RIGHT = 2

        names = {LEFT: LEFT,
                 MIDDLE: MIDDLE,
                 RIGHT: RIGHT}

        values = {0: LEFT,
                  1: MIDDLE,
                  2: RIGHT}

        def __getitem__(self, key: (str | int | float)) -> DivideBarsParameters.eLengthPosition:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def GetTrimLens(self) -> tuple[float, float]:
        """Get necessary length to lengthen/shorten bar parts

        Returns:
            tuple(lengthen/shorten left bar part,
                  lengthen/shorten right bar part)
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, DivideMode: eDivideMode, OverlapPosition: eLengthPosition, OverlapLength: float, GapPosition: eLengthPosition,
                 GapLength: float):
        """Constructor

        Args:
            DivideMode:      Mode of division
            OverlapPosition: Position of Overlap
            OverlapLength:   Overlap length
            GapPosition:     Position of Gap
            GapLength:       Gap length
        """
    @typing.overload
    def __init__(self, element: DivideBarsParameters):
        """Copy constructor

        Args:
            element: Element to copy
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
    def DivideMode(self) -> DivideBarsParameters.eDivideMode:
        """Get the mode of division
        """
    @DivideMode.setter
    def DivideMode(self, DivideMode: DivideBarsParameters.eDivideMode) -> None:
        """Set the mode of division

        Args:
            DivideMode: Mode of division
        """
    @property
    def GapLength(self) -> float:
        """Get the gap length
        """
    @GapLength.setter
    def GapLength(self, GapLength: float) -> None:
        """Set the gap length

        Args:
            GapLength: Gap length
        """
    @property
    def GapPosition(self) -> DivideBarsParameters.eLengthPosition:
        """Get the position of gap
        """
    @GapPosition.setter
    def GapPosition(self, GapPosition: DivideBarsParameters.eLengthPosition) -> None:
        """Set the position of gap

        Args:
            GapPosition: Position of gap
        """
    @property
    def OverlapLength(self) -> float:
        """Get the overlap length
        """
    @OverlapLength.setter
    def OverlapLength(self, OverlapLength: float) -> None:
        """Set the overlap length

        Args:
            OverlapLength: Overlap length
        """
    @property
    def OverlapPosition(self) -> DivideBarsParameters.eLengthPosition:
        """Get the position of overlap
        """
    @OverlapPosition.setter
    def OverlapPosition(self, OverlapPosition: DivideBarsParameters.eLengthPosition) -> None:
        """Set the position of overlap

        Args:
            OverlapPosition: Position of overlap
        """
    ELEMENT2D = eInputMode.ELEMENT2D
    GAP = eDivideMode.GAP
    LEFT = eLengthPosition.LEFT
    MIDDLE = eLengthPosition.MIDDLE
    OPENING = eInputMode.OPENING
    OVERLAP = eDivideMode.OVERLAP
    PLANE = eDivideMode.PLANE
    POLYGON = eInputMode.POLYGON
    RIGHT = eLengthPosition.RIGHT

class ExtrudeBarPlacement(ReinfElement, AllplanElement):
    """Implementation of the extrude bar placement element
    """
    class eEdgeOffsetType(enum.Enum):
        """Edge offset type
        """
        eMajorValueAtEnd = 3
        eMajorValueAtStart = 1
        eStartEqualEnd = 2
        eZeroAtEnd = 4
        eZeroAtStart = 0

        names = {eZeroAtStart: eZeroAtStart,
                 eMajorValueAtStart: eMajorValueAtStart,
                 eStartEqualEnd: eStartEqualEnd,
                 eMajorValueAtEnd: eMajorValueAtEnd,
                 eZeroAtEnd: eZeroAtEnd}

        values = {0: eZeroAtStart,
                  1: eMajorValueAtStart,
                  2: eStartEqualEnd,
                  3: eMajorValueAtEnd,
                  4: eZeroAtEnd}

        def __getitem__(self, key: (str | int | float)) -> ExtrudeBarPlacement.eEdgeOffsetType:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    class eProfileRotation(enum.Enum):
        """Profile rotation
        """
        eNoRotation = 0
        eStandard = 1
        eZ_Axis = 2

        names = {eNoRotation: eNoRotation,
                 eStandard: eStandard,
                 eZ_Axis: eZ_Axis}

        values = {0: eNoRotation,
                  1: eStandard,
                  2: eZ_Axis}

        def __getitem__(self, key: (str | int | float)) -> ExtrudeBarPlacement.eProfileRotation:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def AddCrossBendingShape(self, shape: BendingShape):
        """Add a cross bending shape

        Args:
            shape: Reinforcement shape
        """
    def AddLongitudinalBarProp(self, longitudinalBarProp: LongitudinalBarProperties):
        """Add the longitudinal bar properties

        Args:
            longitudinalBarProp: longitudinal bar properties
        """
    def AddPlacementSection(self, placementSection: BarPlacementSection) -> bool:
        """Add a placement section

        Args:
            placementSection: Section

        Returns:
            Section is added: true/false
        """
    def Extrude(self):
        """Extrude the bars
        """
    def GetBarOffset(self) -> float:
        """Get the bar offset

        Returns:
            Bar offset
        """
    def GetBendingShapeViewVector(self) -> NemAll_Python_Geometry.Vector3D:
        """Get the view vector of the bending shape

        Returns:
            View vector of the bending shape
        """
    def GetCommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties

        Returns:
            Common properties
        """
    def GetConcreteCoverEnd(self) -> float:
        """Get the concrete cover at the end of the path

        Returns:
            Concrete cover at the end of the path
        """
    def GetConcreteCoverStart(self) -> float:
        """Get the concrete cover at the start of the path

        Returns:
            Concrete cover at the start of the path
        """
    def GetCrossBarDistance(self) -> float:
        """Get the cross bar distance

        Returns:
            Cross bar distance
        """
    def GetCrossBendingShapes(self) -> BendingShapeList:
        """Get the cross bending shapes

        Returns:
            Cross bending shapes
        """
    def GetEdgeOffsetEnd(self) -> float:
        """Get the edge offset at the end of the path

        Returns:
            Edge offset at the end of the path
        """
    def GetEdgeOffsetStart(self) -> float:
        """Get the edge offset at the start of the path

        Returns:
            Edge offset at the start of the path
        """
    def GetEdgeOffsetType(self) -> eEdgeOffsetType:
        """Get the edge offset type

        Returns:
            Edge offset type
        """
    def GetEdgeOffsets(self) -> tuple:
        """Get the edge offsets

        Returns:
            Edge offsets
        """
    def GetMaxBreakAngle(self) -> float:
        """Get the maximal break angle

        Returns:
            Maximal break angle
        """
    def GetPlacementPath(self) -> NemAll_Python_Geometry.Path3D:
        """Get the placement path

        Returns:
            Placement path
        """
    def GetPlacementSections(self) -> object:
        """Get the placement sections

        Returns:
            Placement sections
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def GetProfileRoation(self) -> eProfileRotation:
        """Get the profile rotation

        Returns:
            Profile rotation
        """
    def IsBreakElimination(self) -> bool:
        """Get the break eliminination state

        Returns:
            Break elimination state
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the placement

        Args:
            transVec: Move vector
        """
    def SetCommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties):
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the placement

        Args:
            transMat: Transformation matrix
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: ExtrudeBarPlacement):
        """Copy constructor

        Args:
            placement: Placement to copy
        """
    @typing.overload
    def __init__(self, positionNumber: int, path: NemAll_Python_Geometry.Path3D, profileRotation: eProfileRotation, breakElimination: bool,
                 maxBreakAngle: float, crossBarDistance: float, concreteCoverStart: float, concreteCoverEnd: float, edgeOffsetType: eEdgeOffsetType, edgeOffsetStart: float, edgeOffsetEnd: float, barOffset: float, bendingShapeViewVector: NemAll_Python_Geometry.Vector3D):
        """Constructor for cross bars

        Args:
            positionNumber:         Position number
            path:                   Path
            profileRotation:        Profile rotation
            breakElimination:       Break elemination
            maxBreakAngle:          Maximal break angle
            crossBarDistance:       Cross bar distance
            concreteCoverStart:     Concrete cover at the start of the path
            concreteCoverEnd:       Concrete cover at the end of the path
            edgeOffsetType:         Get the edge offset type of the path
            edgeOffsetStart:        Edge offset at the start of the path
            edgeOffsetEnd:          Edge offset at the end of the path
            barOffset:              Bar offset
            bendingShapeViewVector: View vector of the bending shape
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def CommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties
        """
    @CommonProperties.setter
    def CommonProperties(self, value: NemAll_Python_BaseElements.CommonProperties) -> None:
        """Set the common properties
        """
    @property
    def PositionNumber(self) -> int:
        """Get the position number
        """
    @PositionNumber.setter
    def PositionNumber(self, value: int) -> None:
        """Set the position number
        """
    eMajorValueAtEnd = eEdgeOffsetType.eMajorValueAtEnd
    eMajorValueAtStart = eEdgeOffsetType.eMajorValueAtStart
    eNoRotation = eProfileRotation.eNoRotation
    eStandard = eProfileRotation.eStandard
    eStartEqualEnd = eEdgeOffsetType.eStartEqualEnd
    eZ_Axis = eProfileRotation.eZ_Axis
    eZeroAtEnd = eEdgeOffsetType.eZeroAtEnd
    eZeroAtStart = eEdgeOffsetType.eZeroAtStart

class GeometryExpansionUtil():

    def GetLineAbove(self, arg2: NemAll_Python_Geometry.Point2D, arg3: NemAll_Python_Geometry.Line2D, arg4: bool, arg5: int) -> tuple:
        """Get the line above the base line and the placement point
        """
    def GetLineAtPoint(self, arg2: NemAll_Python_Geometry.Point2D, arg3: NemAll_Python_Geometry.Vector2D, arg4: bool, arg5: float) -> tuple:
        """Get the line at the defined point of the reference line
        """
    def GetLineFromPoint(self, arg2: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, arg3: NemAll_Python_Geometry.Point2D,
                         arg4: NemAll_Python_IFW_Input.ViewWorldProjection, arg5: bool) -> tuple:
        """Get the line near to the input point
        """
    def GetLineLeft(self, arg2: NemAll_Python_Geometry.Point2D, arg3: NemAll_Python_Geometry.Line2D, arg4: bool, arg5: int) -> tuple:
        """Get the line left from the base line and the placement point
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, pMsgInfo: NemAll_Python_IFW_Input.AddMsgInfo, use3DGeometry: bool):
        """Constructor

        Args:
            pMsgInfo:      Additional message info
            use3DGeometry: Use the 3D geometry for the expansione: true/false
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class HookLengthService():
    """Service class for the hook length calculation
    """
    def GetHookLength(self, hookAngle: float, hookType: HookType, diameter: float) -> float:
        """Calculate the hook length

        Args:
            hookAngle: Hook angle
            hookType:  Hook type
            diameter:  Diameter

        Returns:
             Hook length
        """
    def GetHookLengthPartFromBendingRoller(self, hookAngle: float, hookType: HookType, diameter: float) -> float:
        """Calculate the hook length part from the beginning of the bending roller

        Args:
            hookAngle: Hook angle
            hookType:  Hook type
            diameter:  Diameter

        Returns:
             Hook length part from the beginning of the bending roller
        """
    def GetHookLengthPartOfBendingRoller(self, hookAngle: float, hookType: HookType, diameter: float) -> float:
        """Calculate the hook length part of the bending roller

        Args:
            hookAngle: Hook angle
            hookType:  Hook type
            diameter:  Diameter

        Returns:
             Hook length part of the bending roller
        """
    def GetStandardAnchorageHookLength(self, diameter: float) -> float:
        """Calculate the standard anchorage hook length

        Args:
            diameter: Diameter

        Returns:
             Standard anchorage hook length
        """
    def __init__(self, norm: int, concreteGrade: int, steelGrade: int, bExactLength: bool):
        """Constructor

        Args:
            norm:          Norm
            concreteGrade: Concrete grade
            steelGrade:    Steel grade
            bExactLength:  Calculate the exact length
        """

class HookType(enum.Enum):
    """Types of the hooks
    """
    eAnchorage = 3
    eAngle = 2
    eStirrup = 1

    names = {eStirrup: eStirrup,
             eAngle: eAngle,
             eAnchorage: eAnchorage}

    values = {1: eStirrup,
              2: eAngle,
              3: eAnchorage}

    def __getitem__(self, key: (str | int | float)) -> HookType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class LabelType(enum.Enum):
    """Types of the label
    """
    LabelWithComb = 2
    LabelWithComb2Pointer = 3
    LabelWithComb3Pointer = 4
    LabelWithDimensionLine = 1
    LabelWithFan = 5
    LabelWithFanStartCenterEnd = 7
    LabelWithFanStartEnd = 6
    LabelWithPointer = 0

    names = {LabelWithPointer: LabelWithPointer,
             LabelWithDimensionLine: LabelWithDimensionLine,
             LabelWithComb: LabelWithComb,
             LabelWithComb2Pointer: LabelWithComb2Pointer,
             LabelWithComb3Pointer: LabelWithComb3Pointer,
             LabelWithFan: LabelWithFan,
             LabelWithFanStartEnd: LabelWithFanStartEnd,
             LabelWithFanStartCenterEnd: LabelWithFanStartCenterEnd}

    values = {0: LabelWithPointer,
              1: LabelWithDimensionLine,
              2: LabelWithComb,
              3: LabelWithComb2Pointer,
              4: LabelWithComb3Pointer,
              5: LabelWithFan,
              6: LabelWithFanStartEnd,
              7: LabelWithFanStartCenterEnd}

    def __getitem__(self, key: (str | int | float)) -> LabelType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class LongitudinalBarProperties():
    """Implementation of the longitudinal bar properties
    """
    class eDeliveryShapeType(enum.Enum):
        """Delivery shape types
        """
        eRound = 1
        eStraight = 0

        names = {eStraight: eStraight,
                 eRound: eRound}

        values = {0: eStraight,
                  1: eRound}

        def __getitem__(self, key: (str | int | float)) -> LongitudinalBarProperties.eDeliveryShapeType:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    class eInsideBarsState(enum.Enum):
        """Inside bar state
        """
        eExact = 0
        eOverlapped = 2
        eShortened = 1

        names = {eExact: eExact,
                 eShortened: eShortened,
                 eOverlapped: eOverlapped}

        values = {0: eExact,
                  1: eShortened,
                  2: eOverlapped}

        def __getitem__(self, key: (str | int | float)) -> LongitudinalBarProperties.eInsideBarsState:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def GetBendingShape(self) -> BendingShape:
        """Get the bending shape

        Returns:
            Bending shape
        """
    def GetDeliveryShapeType(self) -> eDeliveryShapeType:
        """Get the delivery shape type

        Returns:
            Delivery shape type
        """
    def GetInsideBarsState(self) -> eInsideBarsState:
        """Get the insid bars state

        Returns:
            Inside bars state
        """
    def GetMinBarDistance(self) -> float:
        """Get the minimal bar distance

        Returns:
            Minimal bar distance
        """
    def GetOverlappingAtEnd(self) -> float:
        """Get the overlapping at end

        Returns:
            Overlapping at end
        """
    def GetOverlappingAtStart(self) -> float:
        """Get the overlapping at start

        Returns:
            Overlapping at start
        """
    def GetOverlappingLength(self) -> float:
        """Get the overlapping length

        Returns:
            Overlapping length
        """
    def GetStartLength(self) -> float:
        """Get the start length

        Returns:
            Start length
        """
    def IsOverlappingAtEndTurnedOn(self) -> bool:
        """Get the overlapping at end state

        Returns:
            Overlapping at end state
        """
    def IsOverlappingAtStartTurnedOn(self) -> bool:
        """Get the overlapping at start state

        Returns:
            Overlapping at start state
        """
    def SetBendingShape(self, shape: BendingShape):
        """Set the bending shape

        Args:
            shape: Shape

        Returns:
            Bending shape
        """
    def __eq__(self, : LongitudinalBarProperties) -> bool:
        """Compare operator

        Args:

        Returns:
            Bars are equal: true/false
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, shape: BendingShape, overlappingAtStartTurnedOn: bool, overlappingAtStart: float, overlappingAtEndTurnedOn: bool,
                 overlappingAtEnd: float, overlappingLength: float, minBarDistance: float, deliveryShapeType: eDeliveryShapeType, insideBarsState: eInsideBarsState, startLength: float):
        """Constructor

        Args:
            shape:                      Bar shape
            overlappingAtStartTurnedOn: Overlapping at start start
            overlappingAtStart:         Overlapping at start
            overlappingAtEndTurnedOn:   Overlapping at end state
            overlappingAtEnd:           Overlapping at end
            overlappingLength:          Overlapping length
            minBarDistance:             Minimal bar distance
            deliveryShapeType:          Delivery shape type
            insideBarsState:            Inside bars state
            startLength:                Start length
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def BendingShape(self) -> BendingShape:
        """Get the bending shape
        """
    @BendingShape.setter
    def BendingShape(self, value: BendingShape) -> None:
        """Set the bending shape
        """
    eExact = eInsideBarsState.eExact
    eOverlapped = eInsideBarsState.eOverlapped
    eRound = eDeliveryShapeType.eRound
    eShortened = eInsideBarsState.eShortened
    eStraight = eDeliveryShapeType.eStraight

class LongitudinalBarPropertiesList():
    """List for LongitudinalBarProperties objects
    """
    def __contains__(self, value: LongitudinalBarProperties) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: LongitudinalBarProperties):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: LongitudinalBarPropertiesList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> LongitudinalBarProperties:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __init__(self):
        """Initialize
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
    def __setitem__(self, index: (int | slice), value: LongitudinalBarProperties):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: LongitudinalBarProperties):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: LongitudinalBarPropertiesList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class MeshAreaPlacementProperties():

    class MeshPlacementDirection(enum.Enum):
        """Mesh placement direction
        """
        Cross = 1
        Longitudinal = 0

        names = {Longitudinal: Longitudinal,
                 Cross: Cross}

        values = {0: Longitudinal,
                  1: Cross}

        def __getitem__(self, key: (str | int | float)) -> MeshAreaPlacementProperties.MeshPlacementDirection:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def __init__(self):
        """Initialize
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def LapJointOffset(self) -> None:
        """Get/set the lap joint offset state

        :type: None
        """
    @property
    def MeshSizeRound(self) -> None:
        """Get/set the mesh size round state

        :type: None
        """
    @property
    def OverlapCross(self) -> None:
        """Get/set the cross overlap

        :type: None
        """
    @property
    def OverlapLongitudinal(self) -> None:
        """Get/set the longitudinal overlap

        :type: None
        """
    @property
    def PlacementDirection(self) -> None:
        """Get/set the placement direction

        :type: None
        """
    @property
    def PlacementEndJustified(self) -> None:
        """Get/set the placement end justified state

        :type: None
        """
    @property
    def PlacementStartChange(self) -> None:
        """Get/set the placement start change state

        :type: None
        """
    @property
    def StartLength(self) -> None:
        """Get/set the start length

        :type: None
        """
    @property
    def StartWidth(self) -> None:
        """Get/set the start width

        :type: None
        """

class MeshAreaPlacementService():

    def AddOpeningPolygon(self, arg2: NemAll_Python_Geometry.Polygon3D, openingPol: float):
        """Add an opening polygon

        Args:
            openingPol: Opening polygon
        """
    def Calculate(self, arg2: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, doc: MeshData, mesh: MeshAreaPlacementProperties,
                  placementMatrix: NemAll_Python_Geometry.Matrix3D, startPositionNumber: int, concreteCoverZDir: float) -> list:
        """Calculate the meshes

        Args:
            doc:                 Document
            mesh:                Mesh data
            placementMatrix:     Placement matrix
            startPositionNumber: Start position number
            concreteCoverZDir:   Concrete cover in the local z direction
        """
    def SetOuterPolygon(self, arg2: NemAll_Python_Geometry.Polygon3D, placementPol: float):
        """Constructor

        Args:
            placementPol: Placement polygon
        """
    def __init__(self):
        """Initialize
        """

class MeshBendingDirection(enum.Enum):
    """Types of the mesh bending direction
    """
    CrossBars = 0
    LongitudinalBars = 1

    names = {LongitudinalBars: LongitudinalBars,
             CrossBars: CrossBars}

    values = {1: LongitudinalBars,
              0: CrossBars}

    def __getitem__(self, key: (str | int | float)) -> MeshBendingDirection:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class MeshData():
    """Implementation of the mesh data
    """
    def CreateLabel(self):
        """Create the label
        """
    @staticmethod
    def Format(type: str, length: float, width: float) -> str:
        """Get the mesh text

        Args:
            type:   Mesh type
            length: Mesh length
            width:  Mesh width

        Returns:
            Mesh text
        """
    def GetAsBendingDirection(self, bendingDirection: MeshBendingDirection) -> float:
        """Get the as in bending direction

        Args:
            bendingDirection: Bending direction

        Returns:
            As in bending direction
        """
    def GetDiameterBendingDirection(self, bendingDirection: MeshBendingDirection) -> tuple[float, bool]:
        """Get the diameter in bending direction

        Args:
            bendingDirection: Bending direction

        Returns:
            tuple(Diameter in bending direction,
                  Double bar state)
        """
    def GetDimensions(self) -> tuple[float, float]:
        """Get the mesh dimensions

        Returns:
            tuple(Mesh length,
                  Mesh width)
        """
    def GetDistanceBendingDirection(self, bendingDirection: MeshBendingDirection) -> float:
        """Get the distance in bending direction

        Args:
            bendingDirection: Bending direction

        Returns:
            Distance in bending direction
        """
    def GetOverlapBendingDirection(self, bendingDirection: MeshBendingDirection) -> float:
        """Get the overlap in bending direction

        Args:
            bendingDirection: Bending direction

        Returns:
            Overlap in bending direction
        """
    def SetType(self, type: str):
        """Set the mesh type

        Args:
            type: Mesh type
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, type: str, length: float, width: float, diameterLongitudinal: float, diameterCross: float, asLongitudinal: float,
                 asCross: float, distanceLongitudinal: float, distanceCross: float, bDoubleBarLongitudinal: bool, bDoubleBarCross: bool, overlapLongitudinal: float, overlapCross: float, weight: float):
        """Constructor

        Args:
            type:                   Mesh type
            length:                 Mesh length
            width:                  Mesh width
            diameterLongitudinal:   Diameter in longitudinal direction
            diameterCross:          Diameter in cross direction
            asLongitudinal:         As in longitudinal direction
            asCross:                As in cross direction
            distanceLongitudinal:   Distance in longitudinal direction
            distanceCross:          Distance in cross direction
            bDoubleBarLongitudinal: Double bar in longitudinal direction
            bDoubleBarCross:        Double bar in cross direction
            overlapLongitudinal:    Overlap in longitudinal direction
            overlapCross:           Overlap in cross direction
            weight:                 Mesh weight
        """
    @typing.overload
    def __init__(self, element: MeshData):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def AsBendingDirection(self) -> float:
        """Get the as in bending direction
        """
    @property
    def AsCross(self) -> float:
        """Get the as in cross direction
        """
    @property
    def AsLongitudinal(self) -> float:
        """Get the as in longitudinal direction
        """
    @property
    def DiameterCross(self) -> float:
        """Get the diameter in cross direction
        """
    @property
    def DiameterLongitudinal(self) -> float:
        """Get the diameter in longitudinal direction
        """
    @property
    def DistanceBendingDirection(self) -> float:
        """Get the distance in bending direction
        """
    @property
    def DistanceCross(self) -> float:
        """Get the distance in cross direction
        """
    @property
    def DistanceLongitudinal(self) -> float:
        """Get the distance in longitudinal direction
        """
    @property
    def IsDoubleBarCross(self) -> bool:
        """Get the double bar state in cross direction
        """
    @property
    def IsDoubleBarLongitudinal(self) -> bool:
        """Get the double bar state in longitudinal direction
        """
    @property
    def Label(self) -> str:
        """Get the mesh label
        """
    @property
    def Length(self) -> float:
        """Get the mesh length
        """
    @property
    def OverlapBendingDirection(self) -> float:
        """Get the overlap in bending direction
        """
    @property
    def OverlapCross(self) -> float:
        """Get the overlap in cross direction
        """
    @property
    def OverlapLongitudinal(self) -> float:
        """Get the overlap in longitudinal direction
        """
    @property
    def Type(self) -> str:
        """Get the mesh type
        """
    @Type.setter
    def Type(self, type: str) -> None:
        """Set the mesh type

        Args:
            type: Mesh type
        """
    @property
    def Weight(self) -> float:
        """Get the mesh weight
        """
    @property
    def Width(self) -> float:
        """Get the mesh width
        """

class MeshOperations():

    @staticmethod
    def CutMesh(placements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter, divisionLine: NemAll_Python_Geometry.Polygon2D) -> str:
        """Divide the bars placement

        Returns:
              Result message

        Args:
            placement:     BaseElementAdapter with the placement
            cutPolygon:    Cut polygon
        """
    def __init__(self):
        """Initialize
        """

class MeshPlacement(ReinfElement, AllplanElement):

    def GetBendingShape(self) -> BendingShape:
        """Get the shape polyline

        Returns:
             Shape polyline
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
             Position number
        """
    def GetWidthVector(self) -> NemAll_Python_Geometry.Vector3D:
        """Get the width vector

        Returns:
             Width vector
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the placement

        Args:
            transVec: Move vector
        """
    def SetBendingShape(self, shape: BendingShape):
        """Set the reinforcement shape

        Args:
            shape: Reinforcement shape
        """
    def SetPositionNumber(self, positionNumber: int):
        """Set the position number

        Args:
            positionNumber: Position number
        """
    def SetWidthVector(self, widthVec: NemAll_Python_Geometry.Vector3D):
        """Set the width vector

        Args:
            widthVec: Width vector
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the placement

        Args:
            transMat: Transformation matrix
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, positionNumber: int, widthVec: NemAll_Python_Geometry.Vector3D, bendingShape: BendingShape):
        """Constructor

        Args:
            positionNumber: Position number
            widthVec:       Width vector of the mesh
            bendingShape:   Mesh shape
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class NormType(enum.Enum):
    """Types of the norms
    """
    eNORM_AS = 8
    eNORM_BS = 5
    eNORM_DIN = 0
    eNORM_DIN_1 = 10
    eNORM_DIN_H = 4
    eNORM_EC2 = 6
    eNORM_EHE = 7
    eNORM_NEN = 9
    eNORM_NF = 3
    eNORM_OE = 2
    eNORM_SIA = 1
    eNORM_SNIP = 11
    eNORM_SNIP2003 = 12
    eNormNo = -1

    names = {eNormNo: eNormNo,
             eNORM_DIN: eNORM_DIN,
             eNORM_SIA: eNORM_SIA,
             eNORM_OE: eNORM_OE,
             eNORM_NF: eNORM_NF,
             eNORM_DIN_H: eNORM_DIN_H,
             eNORM_BS: eNORM_BS,
             eNORM_EC2: eNORM_EC2,
             eNORM_EHE: eNORM_EHE,
             eNORM_AS: eNORM_AS,
             eNORM_NEN: eNORM_NEN,
             eNORM_DIN_1: eNORM_DIN_1,
             eNORM_SNIP: eNORM_SNIP,
             eNORM_SNIP2003: eNORM_SNIP2003}

    values = {-1: eNormNo,
              0: eNORM_DIN,
              1: eNORM_SIA,
              2: eNORM_OE,
              3: eNORM_NF,
              4: eNORM_DIN_H,
              5: eNORM_BS,
              6: eNORM_EC2,
              7: eNORM_EHE,
              8: eNORM_AS,
              9: eNORM_NEN,
              10: eNORM_DIN_1,
              11: eNORM_SNIP,
              12: eNORM_SNIP2003}

    def __getitem__(self, key: (str | int | float)) -> NormType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class PlaneMeshPlacement(ReinfElement, AllplanElement):
    """Implementation of the mesh placement element
    """
    def GetCommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties

        Returns:
            Common properties
        """
    def GetMeshData(self) -> MeshData:
        """Get the mesh data

        Returns:
            Mesh data
        """
    def GetMeshLength(self) -> float:
        """Get the mesh length

        Returns:
            Mesh length
        """
    def GetMeshPolygon(self) -> NemAll_Python_Geometry.Polygon3D:
        """Get the shape polyline

        Returns:
            Shape polyline
        """
    def GetMeshWidth(self) -> float:
        """Get the mesh width

        Returns:
            Mesh width
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def IsValid(self) -> bool:
        """Get the state of the shape

        Returns:
            Shape is valid: true/false
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the placement

        Args:
            transVec: Move vector
        """
    def SetCommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties):
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    def SetMeshPolygon(self, shape: NemAll_Python_Geometry.Polygon3D):
        """Set the reinforcement shape

        Args:
            shape: Reinforcement shape
        """
    def SetPositionNumber(self, positionNumber: int):
        """Set the position number

        Args:
            positionNumber: Position number
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the placement

        Args:
            transMat: Transformation matrix
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: PlaneMeshPlacement):
        """Copy constructor

        Args:
            placement: Placement to copy
        """
    @typing.overload
    def __init__(self, positionNumber: int, meshData: MeshData, meshLength: float, meshWidth: float,
                 meshPolygon: NemAll_Python_Geometry.Polygon3D):
        """Constructor

        Args:
            positionNumber: Position number
            meshData:       Mesh data
            meshLength:     Mesh length
            meshWidth:      Mesh width
            meshPolygon:    Mesh polygon
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
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
    def MeshPolygon(self) -> NemAll_Python_Geometry.Polygon3D:
        """Get the shape polyline
        """
    @MeshPolygon.setter
    def MeshPolygon(self, shape: NemAll_Python_Geometry.Polygon3D) -> None:
        """Set the reinforcement shape

        Args:
            shape: Reinforcement shape
        """
    @property
    def PositionNumber(self) -> int:
        """Get the position number
        """
    @PositionNumber.setter
    def PositionNumber(self, positionNumber: int) -> None:
        """Set the position number

        Args:
            positionNumber: Position number
        """

class BarPlacement(ReinfElement, AllplanElement):
    """Implementation of the bar placement element
    """
    def GetBarCount(self) -> int:
        """Get the bar count

        Returns:
            Bar count
        """
    def GetBendingShape(self) -> BendingShape:
        """Get the shape polyline

        Returns:
            Shape polyline
        """
    def GetBendingShapeMatrix(self) -> NemAll_Python_Geometry.Matrix3D:
        """Get the bending shape matrix

        Returns:
            Bending shape matrix
        """
    def GetCommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties

        Returns:
            Common properties
        """
    def GetDistanceVector(self) -> NemAll_Python_Geometry.Vector3D:
        """Get the distance vector

        Returns:
            Distance vector
        """
    def GetEndBendingShape(self) -> BendingShape:
        """Get the shape polyline at the end of a polygonal placement

        Returns:
            Shape polyline
        """
    def GetEndPoint(self) -> NemAll_Python_Geometry.Point3D:
        """Get the end point of the placement at the placement line

        Returns:
            End point of the placement at the placement line
        """
    def GetLabel(self) -> ReinforcementLabel:
        """Get the label

        Returns:
            Label
        """
    def GetLengthFactor(self) -> float:
        """Get the length factor

        Returns:
            Length factor
        """
    def GetPlacementMatrix(self) -> NemAll_Python_Geometry.Matrix3D:
        """Get the placement matrix of the first bar

        Returns:
            Placement matrix
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def GetRotationAngle(self) -> NemAll_Python_Geometry.Angle:
        """Get the rotation angle

        Returns:
            Rotation angle
        """
    def GetRotationAxis(self) -> NemAll_Python_Geometry.Line3D:
        """Get the rotation axis

        Returns:
            Rotation axis
        """
    def GetStartPoint(self) -> NemAll_Python_Geometry.Point3D:
        """Get start point of the placement at the placement line

        Returns:
            Start point of the placement at the placement line
        """
    def IsPlacePerLinearMeter(self) -> bool:
        """Get the place per linear meter state

        Returns:
            Place per linear meter: true/false
        """
    def IsPolygonalPlacement(self) -> bool:
        """Get the polygonal placement state

        Returns:
            Polygonal placement: true/false
        """
    def IsRotationalPlacement(self) -> bool:
        """Get the rotational placement state

        Returns:
            Rotational placement: true/false
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the placement

        Args:
            transVec: Move vector
        """
    def SetBarCount(self, barCount: int):
        """Set the bar count

        Args:
            barCount: Bar count
        """
    def SetBendingShape(self, shape: BendingShape):
        """Set the reinforcement shape

        Args:
            shape: Reinforcement shape
        """
    def SetBendingShapeMatrix(self, bendingShapeMat: NemAll_Python_Geometry.Matrix3D):
        """Set the bending shape matrix

        Args:
            bendingShapeMat: Bending shape matrix
        """
    def SetCommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties):
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    def SetDistanceVector(self, distVec: NemAll_Python_Geometry.Vector3D):
        """Set the distance vector

        Args:
            distVec: Distance vector
        """
    def SetEndBendingShape(self, shape: BendingShape):
        """Set the reinforcement shape at the end

        Args:
            shape: Reinforcement shape
        """
    def SetLabel(self, label: ReinforcementLabel, labelAssocView: NemAll_Python_IFW_ElementAdapter.AssocViewElementAdapter):
        """Set the label

        Args:
            label:          Label
            labelAssocView: Associative view for the label
        """
    def SetLengthFactor(self, lengthFactor: float):
        """Set the length factor

        Args:
            lengthFactor: Length factor
        """
    def SetPlacePerLinearMeter(self, bPlacePerLinearMeter: bool):
        """Set the place per linear meter state

        Args:
            bPlacePerLinearMeter: Place per linear meter: true/false
        """
    def SetPositionNumber(self, positionNumber: int):
        """Set the position number

        Args:
            positionNumber: Position number
        """
    def SetRotationAngle(self, rotationAngle: float):
        """Set the rotation angle

        Args:
            rotationAngle: Rotation angle
        """
    def SetRotationAxis(self, rotationAxis: NemAll_Python_Geometry.Line3D):
        """Set the rotation axis

        Args:
            rotationAxis: Rotation axis
        """
    def SetRotationalPlacement(self, bRotationalPlacement: bool):
        """Set the rotational placement state

        Args:
            bRotationalPlacement: Rotational placement state
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the placement

        Args:
            transMat: Transformation matrix
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: BarPlacement):
        """Copy constructor

        Args:
            placement: Placement to copy
        """
    @typing.overload
    def __init__(self, positionNumber: int, barCount: int, distVec: NemAll_Python_Geometry.Vector3D,
                 startPnt: NemAll_Python_Geometry.Point3D, endPnt: NemAll_Python_Geometry.Point3D, bendingShape: BendingShape):
        """Constructor

        Args:
            positionNumber: Position number
            barCount:       Bar count
            distVec:        Distance vector
            startPnt:       Start point of the placement at the placement line
            endPnt:         End point of the placement at the placement line
            bendingShape:   Bending shape
        """
    @typing.overload
    def __init__(self, positionNumber: int, barCount: int, startBendingShape: BendingShape, endBendingShape: BendingShape):
        """Constructor

        Args:
            positionNumber:    Position number
            barCount:          Bar count
            startBendingShape: Start shape of the polygonal placement
            endBendingShape:   End shape of the polygonal placement
        """
    @typing.overload
    def __init__(self, positionNumber: int, barCount: int, rotationAxis: NemAll_Python_Geometry.Line3D,
                 rotationAngle: NemAll_Python_Geometry.Angle, bendingShape: BendingShape):
        """Constructor for the rotational placement

        Args:
            positionNumber: Position number
            barCount:       Bar count
            rotationAxis:   Rotation point
            rotationAngle:  Rotation angle
            bendingShape:   Bending shape
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def BarCount(self) -> int:
        """Get the bar count
        """
    @BarCount.setter
    def BarCount(self, barCount: int) -> None:
        """Set the bar count

        Args:
            barCount: Bar count
        """
    @property
    def BendingShape(self) -> BendingShape:
        """Get the shape polyline
        """
    @BendingShape.setter
    def BendingShape(self, shape: BendingShape) -> None:
        """Set the reinforcement shape

        Args:
            shape: Reinforcement shape
        """
    @property
    def BendingShapeMatrix(self) -> NemAll_Python_Geometry.Matrix3D:
        """Get the bending shape matrix
        """
    @BendingShapeMatrix.setter
    def BendingShapeMatrix(self, bendingShapeMat: NemAll_Python_Geometry.Matrix3D) -> None:
        """Set the bending shape matrix

        Args:
            bendingShapeMat: Bending shape matrix
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
    def DistanceVector(self) -> NemAll_Python_Geometry.Vector3D:
        """Get the distance vector
        """
    @DistanceVector.setter
    def DistanceVector(self, distVec: NemAll_Python_Geometry.Vector3D) -> None:
        """Set the distance vector

        Args:
            distVec: Distance vector
        """
    @property
    def EndBendingShape(self) -> BendingShape:
        """Get the shape polyline at the end of a polygonal placement
        """
    @EndBendingShape.setter
    def EndBendingShape(self, shape: BendingShape) -> None:
        """Set the reinforcement shape at the end

        Args:
            shape: Reinforcement shape
        """
    @property
    def LengthFactor(self) -> float:
        """Get the length factor
        """
    @LengthFactor.setter
    def LengthFactor(self, lengthFactor: float) -> None:
        """Set the length factor

        Args:
            lengthFactor: Length factor
        """
    @property
    def PlacePerLinearMeter(self) -> bool:
        """Get the place per linear meter state
        """
    @PlacePerLinearMeter.setter
    def PlacePerLinearMeter(self, bPlacePerLinearMeter: bool) -> None:
        """Set the place per linear meter state

        Args:
            bPlacePerLinearMeter: Place per linear meter: true/false
        """
    @property
    def PositionNumber(self) -> int:
        """Get the position number
        """
    @PositionNumber.setter
    def PositionNumber(self, positionNumber: int) -> None:
        """Set the position number

        Args:
            positionNumber: Position number
        """
    @property
    def RotationAngle(self) -> NemAll_Python_Geometry.Angle:
        """Get the rotation angle
        """
    @RotationAngle.setter
    def RotationAngle(self, rotationAngle: NemAll_Python_Geometry.Angle) -> None:
        """Set the rotation angle

        Args:
            rotationAngle: Rotation angle
        """
    @property
    def RotationAxis(self) -> NemAll_Python_Geometry.Line3D:
        """Get the rotation axis
        """
    @RotationAxis.setter
    def RotationAxis(self, rotationAxis: NemAll_Python_Geometry.Line3D) -> None:
        """Set the rotation axis

        Args:
            rotationAxis: Rotation axis
        """
    @property
    def RotationalPlacement(self) -> bool:
        """Get the rotational placement state
        """
    @RotationalPlacement.setter
    def RotationalPlacement(self, bRotationalPlacement: bool) -> None:
        """Set the rotational placement state

        Args:
            bRotationalPlacement: Rotational placement state
        """

class ReinforcementLabel():

    def SetAdditionalText(self, additionalText: str):
        """Set the additional text

        Args:
            additionalText: Additional text
        """
    def SetLabelOffset(self, labelOffset: NemAll_Python_Geometry.Vector2D):
        """Set the label offset

        Args:
            labelOffset: Label offset
        """
    def SetPointerStartPoint(self, pointerStartPoint: NemAll_Python_Geometry.Point2D):
        """Set the start pointer of the text pointer

        Args:
            pointerStartPoint: Start point of the text pointer
        """
    def SetShowTextPointer(self, showTextPointer: bool):
        """Set the state for showing the text pointer

        Args:
            showTextPointer: Show the text pointer: true/false
        """
    def SetShowTextPointerEndSymbol(self, showTextPointerEndSymbol: bool):
        """Set the state for showing the text pointer end symbol

        Args:
            showTextPointerEndSymbol: Show the text pointer end symbol: true/false
        """
    def SetTextProperties(self, textProperties: NemAll_Python_BasisElements.TextProperties):
        """Set the text properties

        Args:
            textProperties: Text properties
        """
    def SetVisibleBars(self, visibleBars: (list[int] | NemAll_Python_Utility.VecIntList)):
        """Set the vector with the visible bars

        Args:
            visibleBars: Vector with the visible bars: 1, 2, 3, .. index from left; -1, -2, -3, ... index from right, 0 = center
        """
    def ShowAllBars(self, bShowAllBars: bool):
        """Set the all bars inside the dimension line, ... state

        Args:
            bShowAllBars: Show all bars in the dimension lines, ...: true/false
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, reinforcementType: ReinforcementType, type: LabelType, positionNumber: int, labelProp: ReinforcementLabelProperties,
                 labelPoint: NemAll_Python_Geometry.Point2D, angle: NemAll_Python_Geometry.Angle):
        """Constructor

        Args:
            reinforcementType: Reinforcement type
            type:              Label type
            positionNumber:    Position number
            labelProp:         Label properties
            labelPoint:        Label placement point
            angle:             Angle
        """
    @typing.overload
    def __init__(self, reinforcementType: ReinforcementType, type: LabelType, positionNumber: int, labelProp: ReinforcementLabelProperties,
                 shapeSide: int, shapeSideFactor: float, labelOffset: NemAll_Python_Geometry.Vector2D, angle: NemAll_Python_Geometry.Angle):
        """Constructor

        Args:
            reinforcementType: Reinforcement type
            type:              Label type
            positionNumber:    Position number
            labelProp:         Label properties
            shapeSide:         Shape side for the text pointer
            shapeSideFactor:   Factor for the text pointer at the shape side
            labelOffset:       Label offset
            angle:             Angle
        """
    @typing.overload
    def __init__(self, reinforcementType: ReinforcementType, type: LabelType, positionNumber: int, labelProp: ReinforcementLabelProperties,
                 bDimLineAtShapeStart: bool, dimLineOffset: float):
        """Constructor

        Args:
            reinforcementType:    Reinforcement type
            type:                 Label type
            positionNumber:       Position number
            labelProp:            Label properties
            bDimLineAtShapeStart: Placement of the dimension line: at shape start = true / at shape end = false
            dimLineOffset:        Offset of the dimension line from the placement
        """
    @typing.overload
    def __init__(self, reinforcementType: ReinforcementType, type: LabelType, positionNumber: int, labelProp: ReinforcementLabelProperties,
                 pointerProp: ReinforcementLabelPointerProperties, bDimLineAtShapeStart: bool, dimLineOffset: float):
        """Constructor

        Args:
            reinforcementType:    Reinforcement type
            type:                 Label type
            positionNumber:       Position number
            labelProp:            Label properties
            pointerProp:          Pointer properties
            bDimLineAtShapeStart: Placement of the dimension line: at shape start = true / at shape end = false
            dimLineOffset:        Offset of the dimension line from the placement
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class ReinforcementLabelList():

    def __contains__(self, value: ReinforcementLabel) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ReinforcementLabel):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ReinforcementLabel:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __init__(self):
        """Initialize
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
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    def __setitem__(self, index: (int | slice), value: ReinforcementLabel):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ReinforcementLabel):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ReinforcementLabelList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ReinforcementLabelPointerProperties():

    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, combLineAngle: float, bCombLineByLength: bool, combLineValue: float):
        """Constructor

        Args:
            combLineAngle:     Comb line angle (deg)
            bCombLineByLength: Define the comb line by length = true, by distance = false
            combLineValue:     Value for the comb line length/distance
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class ReinforcementLabelProperties():

    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, prop: ReinforcementLabelProperties):
        """Copy constructor

        Args:
            prop: Properties to copy
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
    def ShowBarCount(self) -> None:
        """Set/get the show state for the bar count

        :type: None
        """
    @property
    def ShowBarDiameter(self) -> None:
        """Set/get the show state for the bar diameter

        :type: None
        """
    @property
    def ShowBarDistance(self) -> None:
        """Set/get the show state for the bar distance

        :type: None
        """
    @property
    def ShowBarLayer(self) -> None:
        """Set/get the show state for the bar layer

        :type: None
        """
    @property
    def ShowBarLength(self) -> None:
        """Set/get the show state for the bar length

        :type: None
        """
    @property
    def ShowBarPlace(self) -> None:
        """Set/get the show state for the bar place

        :type: None
        """
    @property
    def ShowBendingShape(self) -> None:
        """Set/get the show state for the bending shape

        :type: None
        """
    @property
    def ShowPositionAtEnd(self) -> None:
        """Set/get the show state for the bar diameter

        :type: None
        """
    @property
    def ShowPositionNumber(self) -> None:
        """Set/get the show state for the position number

        :type: None
        """
    @property
    def ShowSteelGrade(self) -> None:
        """Set/get the show state for the steel grade

        :type: None
        """
    @property
    def ShowTwoLineText(self) -> None:
        """Set/get the show state for the two line text

        :type: None
        """

class ReinforcementService():
    """Reinforcement service
    """
    class BarShapeCodeStandard(enum.Enum):
        """Standard for the bar shape code
        """
        eACI = 4
        eBS = 2
        eIso3766 = 1
        eIso4066 = 0
        eSANS = 3

        names = {eIso4066: eIso4066,
                 eIso3766: eIso3766,
                 eBS: eBS,
                 eSANS: eSANS,
                 eACI: eACI}

        values = {0: eIso4066,
                  1: eIso3766,
                  2: eBS,
                  3: eSANS,
                  4: eACI}

        def __getitem__(self, key: (str | int | float)) -> ReinforcementService.BarShapeCodeStandard:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    @staticmethod
    def GetACIBarMark(barsDefinitionElement: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter, showIndex: bool) -> list:
        """Get the bar mark

        Args:
            barsDefinitionElement:    Bars definition element
            showIndex:                Show the index

        Returns:
             bar mark for ACI
        """
    @staticmethod
    def GetACIPlacementBarMark(barsPlacementElement: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter, showIndex: bool) -> tuple:
        """Get the bar mark for a placement

        Args:
            barsPlacementElement:     Bars placement element
            showIndex:                Show the index

        Returns:
             tuple(bar mark for ACI, bar count)
        """
    @staticmethod
    def GetBarPositionData(elements: NemAll_Python_IFW_ElementAdapter.BaseElementAdapterList) -> list:
        """Get the bar position data

        Args:
            elements:    List with the elements

        Returns:
             List with the bar position data
        """
    @staticmethod
    def GetBarShapeCode(barsDefinitionElement: NemAll_Python_IFW_ElementAdapter.BaseElementAdapter,
                        barShapeCopdeStandard: BarShapeCodeStandard) -> tuple:
        """Get the bar shape code

        Args:
            barsDefinitionElement:    Bars definition element
            barShapeCopdeStandard:    Standard for the bar shape code

        Returns:
             shape code count, list of (shape codes, bar length), list of (segment name, segment lengths))  for ACI
             shape code count, list of shape codes, list of lengths)  for all other
        """
    eACI = BarShapeCodeStandard.eACI
    eBS = BarShapeCodeStandard.eBS
    eIso3766 = BarShapeCodeStandard.eIso3766
    eIso4066 = BarShapeCodeStandard.eIso4066
    eSANS = BarShapeCodeStandard.eSANS

class ReinforcementSettings():

    @staticmethod
    def CheckBarDiameter() -> float:
        """Check, whether the diameter is included in the diameter list of the current steel grade

        Returns:
            Bar diameter (original or nearest value)
        """
    @staticmethod
    def CheckMeshGroup() -> int:
        """Check, whether the mesh group is included in the group list

        Returns:
            Mesh group (original or first)
        """
    @staticmethod
    def GetBarDiameter() -> float:
        """Get the current bar diameter

        Returns:
            Bar diameter
        """
    @staticmethod
    def GetBarWeight(steelGrade: int, barDiameter: float) -> float:
        """Get the weight for a bar diameter

        Args:
            steelGrade:     Steel grade
            barDiameter:    Bar diameter

        Returns:
            Weight for a bar diameter
        """
    @staticmethod
    def GetBendingRoller() -> float:
        """Get the current bending roller

        Returns:
            Bending roller
        """
    @staticmethod
    def GetConcreteGrade() -> int:
        """Get the current concrete grade

        Returns:
            Concrete grade
        """
    @staticmethod
    def GetMaxBarLength() -> float:
        """Get the maximal bar length

        Returns:
            Maximal bar length
        """
    @staticmethod
    def GetMeshGroup() -> int:
        """Get the current mesh group

        Returns:
            Mesh group
        """
    @staticmethod
    def GetMeshType() -> str:
        """Get the current mesh type

        Returns:
            Mesh type
        """
    @staticmethod
    def GetNorm() -> int:
        """Get the current norm

        Returns:
            Norm
        """
    @staticmethod
    def GetSteelGrade() -> int:
        """Get the current steel grade

        Returns:
            Steel grade
        """
    @staticmethod
    def Is3DReinforcement() -> bool:
        """Get the 3D-Reinforcement state

        Returns:
            Create 3D-Reinforcement: true/false
        """
    def __init__(self):
        """Initialize
        """

class ReinforcementShapeBuilder():
    """Implementation of the reinforcement shape builder
    """
    @typing.overload
    def AddPoint(self, pnt: NemAll_Python_Geometry.Point2D, concreteCover: float, bendingRoller: float, zCoordBar: float = 0):
        """Add an end point of a geometry side

        Args:
            pnt:           End point of the side
            concreteCover: Concrete cover
            bendingRoller: Bending roller
            zCoordBar:     Bar coordinate in z direction of the local shape coordinate system
        """
    @typing.overload
    def AddPoint(self, pnt: NemAll_Python_Geometry.Point3D, concreteCover: float, bendingRoller: float):
        """Add an end point of a geometry side

        Args:
            pnt:           End point of the side
            concreteCover: Concrete cover
            bendingRoller: Bending roller
        """
    def AddPoint(self):
        """ Overloaded function. See individual overloads.
        """
    def AddPoints(self, pointList: object):
        """Add the shape geometry points

        Args:
            pointList: Point list
        """
    @typing.overload
    def AddSide(self, startPnt: NemAll_Python_Geometry.Point2D, endPnt: NemAll_Python_Geometry.Point2D, concreteCover: float,
                bendingRoller: float, zCoordBar: float = 0):
        """Add a geometry side of the shape

        Args:
            startPnt:      Start point of the geometry side
            endPnt:        End point of the geometry side
            concreteCover: Concrete cover
            bendingRoller: Bending roller between the last and current side
            zCoordBar:     Bar coordinate in z direction of the local shape coordinate system
        """
    @typing.overload
    def AddSide(self, startPnt: NemAll_Python_Geometry.Point3D, endPnt: NemAll_Python_Geometry.Point3D, concreteCover: float,
                bendingRoller: float):
        """Add a geometry side of the shape

        Args:
            startPnt:      Start point of the geometry side
            endPnt:        End point of the geometry side
            concreteCover: Concrete cover
            bendingRoller: Bending roller between the last and current side
        """
    def AddSide(self):
        """ Overloaded function. See individual overloads.
        """
    def AddSides(self, sideList: object):
        """Add the geometry sides of a shape

        Args:
            sideList: Side list
        """
    @typing.overload
    def CreateShape(self, diameter: float, bendingRoller: float, steelGrade: int, concreteGrade: int,
                    bendingShapeType: BendingShapeType) -> BendingShape:
        """Create the shape

        Args:
            diameter:         Diameter
            bendingRoller:    Default bending roller
            steelGrade:       Steel grade
            concreteGrade:    Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType: Bending shape type

        Returns:
            Creation successful: true/false
        """
    @typing.overload
    def CreateShape(self, meshType: str, meshBendingDirection: MeshBendingDirection, bendingRoller: float, steelGrade: int,
                    concreteGrade: int, bendingShapeType: BendingShapeType) -> BendingShape:
        """Create the shape

        Args:
            meshType:             Mesh type
            meshBendingDirection: Mesh bending direction
            bendingRoller:        Default bending roller
            steelGrade:           Steel grade
            concreteGrade:        Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            bendingShapeType:     Bending shape type

        Returns:
            Creation successful: true/false
        """
    @typing.overload
    def CreateShape(self, shapeProps: object) -> BendingShape:
        """Create the shape

        Args:
            shapeProps: Shape properties

        Returns:
            Creation successful: true/false
        """
    def CreateShape(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def CreateStirrup(self, diameter: float, bendingRoller: float, steelGrade: int, concreteGrade: int,
                      stirrupType: StirrupType) -> BendingShape:
        """Create the stirrup shape

        Args:
            diameter:      Diameter
            bendingRoller: Default bending roller
            steelGrade:    Steel grade
            concreteGrade: Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            stirrupType:   Type of the stirrup

        Returns:
            Creation successful: true/false
        """
    @typing.overload
    def CreateStirrup(self, meshType: str, meshBendingDirection: MeshBendingDirection, bendingRoller: float, steelGrade: int,
                      concreteGrade: int, stirrupType: StirrupType) -> BendingShape:
        """Create the stirrup shape

        Args:
            meshType:             Mesh type
            meshBendingDirection: Mesh bending direction
            bendingRoller:        Default bending roller
            steelGrade:           Steel grade
            concreteGrade:        Concrete grade (index of the global list starting from 0, -1 = use global value from the Allplan settings)
            stirrupType:          Type of the stirrup

        Returns:
            Creation successful: true/false
        """
    @typing.overload
    def CreateStirrup(self, shapeProps: object, stirrupType: StirrupType) -> BendingShape:
        """Create the stirrup shape

        Args:
            shapeProps:  Shape properties
            stirrupType: Type of the stirrup

        Returns:
            Creation successful: true/false
        """
    def CreateStirrup(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def GetMeshData(meshType: str) -> MeshData:
        """Get the mesh data

        Args:
            meshType: Mesh type

        Returns:
            Mesh data
        """
    def SetAnchorageHookEnd(self, angle: float):
        """Set an anchorage hook at the end of the shape

        Args:
            angle: Hook angle
        """
    def SetAnchorageHookEndFromSide(self):
        """Set an anchorage hook at the end of the shape, get the angle from the side
        """
    def SetAnchorageHookStart(self, angle: float):
        """Set an anchorage hook at the start of the shape

        Args:
            angle: Hook angle
        """
    def SetAnchorageHookStartFromSide(self):
        """Set an anchorage hook at the start of the shape, get the angle from the side
        """
    def SetAnchorageLengthEnd(self, anchorageLength: float):
        """Set the anchorage length at the end of the shape

        Args:
            anchorageLength: Anchorage length at the end of the shape
        """
    def SetAnchorageLengthStart(self, anchorageLength: float):
        """Set the anchorage length at the start of the shape

        Args:
            anchorageLength: Anchorage length at the start of the shape
        """
    def SetConcreteCoverEnd(self, concreteCover: float):
        """Set the concrete cover at the end of the shape

        Args:
            concreteCover: Concrete cover
        """
    @typing.overload
    def SetConcreteCoverLineEnd(self, startPnt: NemAll_Python_Geometry.Point2D, endPnt: NemAll_Python_Geometry.Point2D,
                                concreteCover: float):
        """Set the concrete cover line at the end of the shape

        Args:
            startPnt:      Start point of the concrete cover line at the end of the shape
            endPnt:        Endpoint of the concrete cover line at the end of the shape
            concreteCover: Concrete cover
        """
    @typing.overload
    def SetConcreteCoverLineEnd(self, startPnt: NemAll_Python_Geometry.Point3D, endPnt: NemAll_Python_Geometry.Point3D,
                                concreteCover: float):
        """Set the concrete cover line at the end of the shape

        Args:
            startPnt:      Start point of the concrete cover line at the end of the shape
            endPnt:        Endpoint of the concrete cover line at the end of the shape
            concreteCover: Concrete cover
        """
    def SetConcreteCoverLineEnd(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def SetConcreteCoverLineStart(self, startPnt: NemAll_Python_Geometry.Point2D, endPnt: NemAll_Python_Geometry.Point2D,
                                  concreteCover: float):
        """Set the concrete cover line at the start of the shape

        Args:
            startPnt:      Start point of the concrete cover line at the start of the shape
            endPnt:        Endpoint of the concrete cover line at the start of the shape
            concreteCover: Concrete cover
        """
    @typing.overload
    def SetConcreteCoverLineStart(self, startPnt: NemAll_Python_Geometry.Point3D, endPnt: NemAll_Python_Geometry.Point3D,
                                  concreteCover: float):
        """Set the concrete cover line at the start of the shape

        Args:
            startPnt:      Start point of the concrete cover line at the start of the shape
            endPnt:        Endpoint of the concrete cover line at the start of the shape
            concreteCover: Concrete cover
        """
    def SetConcreteCoverLineStart(self):
        """ Overloaded function. See individual overloads.
        """
    def SetConcreteCoverStart(self, concreteCover: float):
        """Set the concrete cover at the start of the shape

        Args:
            concreteCover: Concrete cover
        """
    def SetFullCircleOverlap(self, fullCircleOverlap: float):
        """Set the overlap length for the full circle stirrup

        Args:
            fullCircleOverlap: Overlap length
        """
    def SetHookEnd(self, length: float, angle: float, type: HookType):
        """Set the hook at the end of the shape

        Args:
            length: Hook length (0 = calculate)
            angle:  Hook angle
            type:   Hook type
        """
    def SetHookStart(self, length: float, angle: float, type: HookType):
        """Set the hook at the start of the shape

        Args:
            length: Hook length (0 = calculate)
            angle:  Hook angle
            type:   Hook type
        """
    def SetOverlapLengthEnd(self):
        """Set an overlap length a the end of the shape
        """
    def SetOverlapLengthStart(self):
        """Set an overlap length a the start of the shape
        """
    def SetSideLengthEnd(self, sideLength: float):
        """Set the side length at the end of the shape

        Args:
            sideLength: Side length
        """
    def SetSideLengthStart(self, sideLength: float):
        """Set the side length at the start of the shape

        Args:
            sideLength: Side length
        """
    @typing.overload
    def SetStartPoint(self, startPnt: NemAll_Python_Geometry.Point2D):
        """Set a start point of a geometry side

        Args:
            startPnt: Start point
        """
    @typing.overload
    def SetStartPoint(self, startPnt: NemAll_Python_Geometry.Point3D):
        """Set a start point of a geometry side

        Args:
            startPnt: Start point
        """
    def SetStartPoint(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, shapePlaneMatrix: NemAll_Python_Geometry.Matrix3D):
        """Constructor

        Args:
            shapePlaneMatrix: Matrix of the plane for the real shape calculation
        """
    @typing.overload
    def __init__(self, shapePlaneMatrix: NemAll_Python_Geometry.Matrix3D, create3DShape: bool, localZCoverFront: float,
                 localZCoverBack: float):
        """Constructor

        Args:
            shapePlaneMatrix: Matrix of the plane for the real shape calculation
            create3DShape:    Create a 3D shape
            localZCoverFront: Concrete cover in the front of the local z direction of the shape (needed for 3D shape)
            localZCoverBack:  Concrete cover in the back of the local z direction of the shape (needed for 3D shape)
        """
    @typing.overload
    def __init__(self, element: ReinforcementShapeBuilder):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class ReinforcementType(enum.Enum):
    """Types of the reinforcement
    """
    Bar = 0
    Mesh = 1

    names = {Bar: Bar,
             Mesh: Mesh}

    values = {0: Bar,
              1: Mesh}

    def __getitem__(self, key: (str | int | float)) -> ReinforcementType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ReinforcementUtil():

    @staticmethod
    def GetNextBarPositionNumber(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter) -> int:
        """Get the the next bar position number

        Returns:
             Next bar position number
            r: doc              Document
        """
    @staticmethod
    def GetNextMeshPositionNumber(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter) -> int:
        """Get the the next mesh position number

        Returns:
             Next mesh position number
            r: doc              Document
        """
    @staticmethod
    def Rearrange(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, fromBarPosition: int = 1, fromMeshPosition: int = 1,
                  toBarPosition: int = 99999, toMeshPosition: int = 99999, afterBarPosition: int = 1, aftgerMeshPosition: int = 1, tolerance: float = 1.0, rearrangedLock: bool = False, identicalShapes: bool = False, identicalPrefix: bool = False, createUndoStep: bool = True):
        """Rearrange the reinforcement

        Args:
            doc:              Document
            fromBarPosition:  Rearrange from bar position
            fromMeshPosition: Rearrange from mesh position
            toBarPosition:    Rearrange to bar position
            toMeshPosition:   Rearrange to mesh position
            afterBarPosition: Rearrange after bar position
            afterMeshPosition:Rearrange after mesh position
            tolerance:        Tolerance
            rearrangedLock:   Rearranged positions are locked state
            identicalShapes:  Rearrange identical shapes state
            identicalPrefix:  Rearrange identical prefix state
            createUndoStep:   Create the undo step state
        """
    def __init__(self):
        """Initialize
        """

class SpiralElement(ReinfElement, AllplanElement):

    def SetLengthFactor(self, arg2: float):
        """Get the length factor

        Returns:
             Length factor
        """
    def SetNumberLoopsEnd(self, arg2: int):
        """Set the loops at the end
        """
    def SetNumberLoopsStart(self, arg2: int):
        """Set the loops at the start
        """
    def SetPitchSections(self, pitch1: float, length1: float, pitch2: float, length2: float, pitch3: float, length3: float, pitch4: float,
                         length4: float):
        """Set the pitch section

        Args:
            pitch1:  Pitch section 1
            length1: Length section 1
            pitch2:  Pitch section 2
            length2: Length section 2
            pitch3:  Pitch section 3
            length3: Length section 3
            pitch4:  Pitch section 4
            length4: Length section 4
        """
    def SetPlacePerLinearMeter(self, bPlacePerMeter: bool):
        """Set the place per linear meter state

        Args:
            bPlacePerMeter: Place per linear meter: true/false
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, positionNumber: int, diameter: float, steelGrade: int, concreteGrade: int,
                 rotationAxis: NemAll_Python_Geometry.Line3D, contourPoints: NemAll_Python_Geometry.Polyline3D, pitch: float, hookLengthStart: float, hookAngleStart: float, hookLengthEnd: float, hookAngleEnd: float, concreteCoverStart: float, concreteCoverEnd: float, concreteCoverContour: float):
        """Constructor

        Args:
            positionNumber:     Position number
            diameter:           Diameter
            steelGrade:         Steel grade
            concreteGrade:      Concrete grade
            rotationAxis:       Rotation axis
            contourPoints:      Contour points
            pitch:              Pitch
            hookLengthStart:    Hook length at the start
            hookAngleStart:     Hook angle at the start
            hookLengthEnd:      Hook length at the end
            hookAngleEnd:       Hook angle at the end
            concreteCoverStart: Concrete cover at the start
            concreteCoverEnd:   Concrete cover at the end
            concreteCoverEnd:   Concrete cover at the contour
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class StirrupType(enum.Enum):
    """Types of the stirrups
    """
    Column = 3
    Diamond = 4
    FullCircle = 5
    Normal = 1
    Torsion = 2

    names = {Normal: Normal,
             Torsion: Torsion,
             Column: Column,
             Diamond: Diamond,
             FullCircle: FullCircle}

    values = {1: Normal,
              2: Torsion,
              3: Column,
              4: Diamond,
              5: FullCircle}

    def __getitem__(self, key: (str | int | float)) -> StirrupType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class SweepBarPlacement(ReinfElement, AllplanElement):
    """Implementation of the sweep bar placement element
    """
    class eEdgeOffsetType(enum.Enum):
        """Edge offset types
        """
        eMajorValueAtEnd = 3
        eMajorValueAtStart = 1
        eStartEqualEnd = 2
        eZeroAtEnd = 4
        eZeroAtStart = 0

        names = {eZeroAtStart: eZeroAtStart,
                 eMajorValueAtStart: eMajorValueAtStart,
                 eStartEqualEnd: eStartEqualEnd,
                 eMajorValueAtEnd: eMajorValueAtEnd,
                 eZeroAtEnd: eZeroAtEnd}

        values = {0: eZeroAtStart,
                  1: eMajorValueAtStart,
                  2: eStartEqualEnd,
                  3: eMajorValueAtEnd,
                  4: eZeroAtEnd}

        def __getitem__(self, key: (str | int | float)) -> SweepBarPlacement.eEdgeOffsetType:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def AddPlacementSection(self, placementSection: BarPlacementSection) -> bool:
        """Add a placement section

        Args:
            placementSection: Section

        Returns:
            Section is added: true/false
        """
    def AddSectionBars(self, bendingShapes: BendingShapeList, sectionsLongitudinalBarsProp: LongitudinalBarPropertiesList,
                       sectionPlane: NemAll_Python_Geometry.Plane3D):
        """Add the bars and the section plane for a section

        bendingShapeViewVector  View vector of the bending shape

        Args:
            bendingShapes:                Bending shapes of the section
            sectionsLongitudinalBarsProp: Longitudinal bars properties
            sectionPlane:                 Section plane
        """
    def GetBarOffset(self) -> float:
        """Get the bar offset

        Returns:
            Bar offset
        """
    def GetBenchingAngle(self) -> float:
        """Get the benching angle

        Returns:
            Benching angle
        """
    def GetBenchingLength(self) -> float:
        """Get the benching length

        Returns:
            Benching length
        """
    def GetCommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties

        Returns:
            Common properties
        """
    def GetConcreteCoverEnd(self) -> float:
        """Get the concrete cover at the end of the path

        Returns:
            Concrete cover at the end of the path
        """
    def GetConcreteCoverStart(self) -> float:
        """Get the concrete cover at the start of the path

        Returns:
            Concrete cover at the start of the path
        """
    def GetCrossBarDistance(self) -> float:
        """Get the cross bar distance

        Returns:
            Cross bar distance
        """
    def GetEdgeOffsetEnd(self) -> float:
        """Get the edge offset at the end of the path

        Returns:
            Edge offset at the end of the path
        """
    def GetEdgeOffsetStart(self) -> float:
        """Get the edge offset at the start of the path

        Returns:
            Edge offset at the start of the path
        """
    def GetEdgeOffsetType(self) -> eEdgeOffsetType:
        """Get the edge offset type

        Returns:
            Edge offset type
        """
    def GetEdgeOffsets(self) -> tuple:
        """Get the edge offsets

        Returns:
            Edge offsets
        """
    def GetPlacementSections(self) -> object:
        """Get the placement sections

        Returns:
            Placement sections
        """
    def GetPositionNumber(self) -> int:
        """Get the position number

        Returns:
            Position number
        """
    def IsFirstPathIsSweepPath(self) -> bool:
        """Get the first path is sweep path state

        Returns:
            First path is sweep path state
        """
    def IsInterpolation(self) -> bool:
        """Get the interpolation state

        Returns:
            Interpolation state
        """
    def IsInterpolationOfAllPoints(self) -> bool:
        """Get the interpolation of all points state

        Returns:
            Interpolation of all points state
        """
    def IsRoation(self) -> bool:
        """Get the rotation state

        Returns:
            Rotation state
        """
    def Move(self, transVec: NemAll_Python_Geometry.Vector3D):
        """Move the placement

        Args:
            transVec: Move vector
        """
    def SetCommonProperties(self, commonProp: NemAll_Python_BaseElements.CommonProperties):
        """Set the common properties

        Args:
            commonProp: Common properties
        """
    def SetPositionNumber(self, positionNumber: int):
        """Set the position number

        Args:
            positionNumber: Position number
        """
    def Sweep(self):
        """Sweep the bars
        """
    def Transform(self, transMat: NemAll_Python_Geometry.Matrix3D):
        """Transform the placement

        Args:
            transMat: Transformation matrix
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: SweepBarPlacement):
        """Copy constructor

        Args:
            placement: Placement to copy
        """
    @typing.overload
    def __init__(self, positionNumber: int, sweepPaths: NemAll_Python_Geometry.Path3DList, rotation: bool, firstPathIsSweepPath: bool,
                 interpolation: bool, interpolationOfAllPoints: bool, crossBarDistance: float, concreteCoverStart: float, concreteCoverEnd: float, edgeOffsetType: eEdgeOffsetType, edgeOffsetStart: float, edgeOffsetEnd: float, barOffset: float, benchingLength: float, benchingAngle: float):
        """Constructor for cross bars

        Args:
            positionNumber:           Position number
            sweepPaths:               Path
            rotation:                 Rotation
            firstPathIsSweepPath:     First path is also sweep path
            interpolation:            Interpolation
            interpolationOfAllPoints: Interpolation of all points
            crossBarDistance:         Cross bar distance
            concreteCoverStart:       Concrete cover at the start of the path
            concreteCoverEnd:         Concrete cover at the end of the path
            edgeOffsetType:           Get the edge offset type of the path
            edgeOffsetStart:          Edge offset at the start of the path
            edgeOffsetEnd:            Edge offset at the end of the path
            barOffset:                Bar offset
            benchingLength:           Benching length
            benchingAngle:            Benching angle
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def CommonProperties(self) -> NemAll_Python_BaseElements.CommonProperties:
        """Get the common properties
        """
    @CommonProperties.setter
    def CommonProperties(self, value: NemAll_Python_BaseElements.CommonProperties) -> None:
        """Set the common properties
        """
    @property
    def PositionNumber(self) -> int:
        """Get the position number
        """
    @PositionNumber.setter
    def PositionNumber(self, value: int) -> None:
        """Set the position number
        """
    eMajorValueAtEnd = eEdgeOffsetType.eMajorValueAtEnd
    eMajorValueAtStart = eEdgeOffsetType.eMajorValueAtStart
    eStartEqualEnd = eEdgeOffsetType.eStartEqualEnd
    eZeroAtEnd = eEdgeOffsetType.eZeroAtEnd
    eZeroAtStart = eEdgeOffsetType.eZeroAtStart

@typing.overload
def CreateReinforcementLabeling(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, insertionMat: NemAll_Python_Geometry.Matrix3D,
                                labelList: list, viewProj: NemAll_Python_IFW_Input.ViewWorldProjection, undoRedoService: (object | None) = None):
    """Create the reinforcement labels

    Args:
        doc:            Document
        insertionMat:   Insertion matrix
        modelEleList:   List with the model elements
        viewProj:       View projection
        undoRedoService:Undo redo service
    """
@typing.overload
def CreateReinforcementLabeling(doc: NemAll_Python_IFW_ElementAdapter.DocumentAdapter, insertionMat: NemAll_Python_Geometry.Matrix3D,
                                labelList: ReinforcementLabelList, viewProj: NemAll_Python_IFW_Input.ViewWorldProjection):
    """Create the reinforcement labels

    Args:
        doc:            Document
        insertionMat:   Insertion matrix
        labelList:      List with the labels
        viewProj:       View projection
    """
def CreateReinforcementLabeling(self):
    """ Overloaded function. See individual overloads.
    """
def InitApplicationtest() -> NemAll_Python_IFW_ElementAdapter.DocumentAdapter:
    """
    """
def InitUnitTest():
    """
    """
